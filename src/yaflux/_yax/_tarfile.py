import os
import pickle
import tarfile
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List

from ._error import (
    YaxMissingParametersFileError,
    YaxMissingResultError,
    YaxMissingResultFileError,
    YaxMissingVersionFileError,
)
from ._toml import _format_toml_section


class TarfileSerializer:
    """Handles serialization of analysis objects to/from yaflux archive format."""

    VERSION = "0.2.0"
    METADATA_NAME = "metadata.pkl"
    MANIFEST_NAME = "manifest.toml"
    RESULTS_DIR = "results"
    EXTENSION = ".yax"  # yaflux archive extension

    @classmethod
    def _create_manifest(cls, metadata: dict, results: dict) -> str:
        """Create a TOML manifest of the archive contents.

        Parameters
        ----------
        metadata : dict
            Analysis metadata
        results : dict
            Analysis results

        Returns
        -------
        str
            TOML formatted manifest
        """
        manifest = {
            "archive_info": {
                "version": metadata["version"],
                "created": datetime.fromtimestamp(metadata["timestamp"]).isoformat(),
                "yaflux_format": cls.VERSION,
            },
            "analysis": {
                "completed_steps": sorted(metadata["completed_steps"]),
                "step_ordering": metadata["step_ordering"],
                "parameters": str(metadata["parameters"]),
            },
            "results": {
                name: {
                    "type": type(value).__name__,
                    "module": type(value).__module__,
                    "size_bytes": len(pickle.dumps(value)),
                }
                for name, value in results.items()
            },
            "steps": {
                step: {
                    "creates": sorted(info.creates),
                    "requires": sorted(info.requires),
                    "elapsed": info.elapsed,
                    "timestamp": (datetime.fromtimestamp(info.timestamp).isoformat()),
                }
                for step, info in metadata["step_metadata"].items()
            },
        }

        return "\n".join(_format_toml_section(manifest))

    @classmethod
    def save(cls, filepath: str, analysis: Any, force: bool = False) -> None:
        """Save analysis to yaflux archive format.

        Parameters
        ----------
        filepath : str
            Path to save the analysis. If it doesn't end in .yax, the extension will be added
        analysis : Any
            Analysis object to save
        force : bool, optional
            Whether to overwrite existing file, by default False
        """
        # Ensure correct extension
        if not filepath.endswith(cls.EXTENSION):
            filepath = filepath + cls.EXTENSION

        if not force and os.path.exists(filepath):
            raise FileExistsError(f"File already exists: '{filepath}'")

        # Prepare metadata
        yax_metadata = {
            "version": cls.VERSION,
            "parameters": analysis.parameters,
            "completed_steps": list(analysis._completed_steps),
            "step_metadata": analysis._results._metadata,
            "result_keys": list(analysis._results._data.keys()),
            "step_ordering": analysis._step_ordering,
            "timestamp": datetime.now().timestamp(),
        }

        # Create tarfile
        with tarfile.open(filepath, "w:gz") as tar:
            # Add metadata
            metadata_bytes = BytesIO(pickle.dumps(yax_metadata))
            metadata_info = tarfile.TarInfo(cls.METADATA_NAME)
            metadata_info.size = len(metadata_bytes.getvalue())
            tar.addfile(metadata_info, metadata_bytes)

            # Create and add manifest
            manifest = cls._create_manifest(yax_metadata, analysis._results._data)
            manifest_bytes = BytesIO(manifest.encode("utf-8"))
            manifest_info = tarfile.TarInfo(cls.MANIFEST_NAME)
            manifest_info.size = len(manifest_bytes.getvalue())
            tar.addfile(manifest_info, manifest_bytes)

            # Add parameters
            parameters_bytes = BytesIO(pickle.dumps(analysis.parameters))
            parameters_info = tarfile.TarInfo("parameters.pkl")
            parameters_info.size = len(parameters_bytes.getvalue())
            tar.addfile(parameters_info, parameters_bytes)

            # Add results
            for key, value in analysis._results._data.items():
                result_bytes = BytesIO(pickle.dumps(value))
                result_path = os.path.join(cls.RESULTS_DIR, f"{key}.pkl")
                result_info = tarfile.TarInfo(result_path)
                result_info.size = len(result_bytes.getvalue())
                tar.addfile(result_info, result_bytes)

    @classmethod
    def load(
        cls,
        filepath: str,
        *,
        no_results: bool = False,
        select: List[str] | str | None = None,
        exclude: List[str] | str | None = None,
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Load analysis from yaflux archive format.

        Parameters
        ----------
        filepath : str
            Path to load the analysis from
        no_results : bool, optional
            Only load metadata, by default False
        select : Optional[List[str], str], optional
            Only load specific results, by default None
        exclude : Optional[List[str], str], optional
            Skip specific results, by default None

        Returns
        -------
        tuple[Dict[str, Any], Dict[str, Any]]
            Metadata and results dictionaries
        """
        select = cls._normalize_input(select)
        exclude = cls._normalize_input(exclude)

        with tarfile.open(filepath, "r:gz") as tar:
            # Load metadata
            metadata_file = tar.extractfile(cls.METADATA_NAME)
            if metadata_file is None:
                raise ValueError(f"Invalid yaflux archive: missing {cls.METADATA_NAME}")
            metadata = pickle.loads(metadata_file.read())

            # Validate version
            if "version" not in metadata:
                raise YaxMissingVersionFileError(
                    "Invalid yaflux archive: missing version in metadata"
                )

            # Load parameters
            parameters_file = tar.extractfile("parameters.pkl")
            if parameters_file is None:
                raise YaxMissingParametersFileError(
                    "Invalid yaflux archive: missing parameters.pkl"
                )
            metadata["parameters"] = pickle.loads(parameters_file.read())

            # Handle selective loading
            if no_results:
                return metadata, {}

            available_results = metadata["result_keys"]
            if select is not None and exclude is not None:
                raise ValueError("Cannot specify both select and exclude")

            # Determine which results to load
            to_load = set(available_results)
            if select is not None:
                invalid = set(select) - set(available_results)
                if invalid:
                    raise YaxMissingResultError(
                        f"Requested results not found: {invalid}"
                    )
                to_load = set(select)
            if exclude is not None:
                to_load -= set(exclude)

            # Load selected results
            results = {}
            for key in to_load:
                result_path = os.path.join(cls.RESULTS_DIR, f"{key}.pkl")
                result_file = tar.extractfile(result_path)
                if result_file is None:
                    raise YaxMissingResultFileError(
                        f"Missing result file: {result_path}"
                    )
                results[key] = pickle.loads(result_file.read())

            return metadata, results

    @classmethod
    def is_yaflux_archive(cls, filepath: str) -> bool:
        """Check if file is a yaflux archive."""
        return filepath.endswith(cls.EXTENSION) and tarfile.is_tarfile(filepath)

    @staticmethod
    def _normalize_input(options: list[str] | str | None) -> list[str] | None:
        """Normalize input to a list."""
        if isinstance(options, str):
            return [options]
        return options
