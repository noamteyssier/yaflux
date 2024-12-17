import json
import os
import pickle
import tarfile
from datetime import datetime
from io import BytesIO
from typing import Any

from ._error import (
    YaxMissingResultError,
    YaxMissingVersionFileError,
)
from ._serializer import SerializerMetadata, SerializerRegistry


class TarfileSerializer:
    """Handles serialization of analysis objects to/from yaflux archive format."""

    VERSION = "0.2.1"
    METADATA_NAME = "metadata.pkl"
    MANIFEST_NAME = "manifest.json"
    RESULTS_DIR = "results"
    EXTENSION = ".yax"  # yaflux archive extension
    COMPRESSED_EXTENSION = ".yax.gz"  # compressed yaflux archive extension

    @classmethod
    def _create_manifest(cls, metadata: dict, results_metadata: dict) -> str:
        """Create a JSON manifest of the archive contents."""
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
                    "type": meta.type_name,
                    "module": meta.module_name,
                    "format": meta.format,
                    "size_bytes": meta.size_bytes,
                }
                for name, meta in results_metadata.items()
            },
            "steps": {
                step: {
                    "creates": sorted(info.creates),
                    "requires": sorted(info.requires),
                    "elapsed": info.elapsed,
                    "timestamp": datetime.fromtimestamp(info.timestamp).isoformat(),
                }
                for step, info in metadata["step_metadata"].items()
            },
        }
        return json.dumps(manifest, indent=2)

    @classmethod
    def save(
        cls, filepath: str, analysis: Any, force: bool = False, compress: bool = False
    ) -> None:
        """Save analysis to yaflux archive format.

        Parameters
        ----------
        filepath : str
            Path to save the analysis. If it doesn't end in .yax, the extension will
            be added
        analysis : Any
            Analysis object to save
        force : bool, optional
            Whether to overwrite existing file, by default False
        compress : bool, optional
            Whether to compress the archive (gzip), by default False
        """
        # Ensure correct file extension
        if filepath.endswith(cls.EXTENSION) and compress:
            filepath = filepath.replace(cls.EXTENSION, cls.COMPRESSED_EXTENSION)
        elif filepath.endswith(cls.COMPRESSED_EXTENSION):
            compress = True
        elif not filepath.endswith(cls.EXTENSION):
            if compress:
                filepath = filepath + cls.COMPRESSED_EXTENSION
            else:
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

        # Track serialization metadata for results
        results_metadata = {}

        # Create tarfile
        w_mode = "w:gz" if compress else "w"
        with tarfile.open(filepath, w_mode) as tar:
            # Add metadata
            cls._add_bytes_to_tar(
                tar,
                cls.METADATA_NAME,
                pickle.dumps(yax_metadata),
            )

            # Add parameters
            cls._add_bytes_to_tar(
                tar,
                cls.MANIFEST_NAME,
                pickle.dumps(analysis.parameters),
            )

            # Add results
            for key, value in analysis._results._data.items():
                # Get appropriate serializer for data type
                serializer = SerializerRegistry.get_serializer(value)

                # Serialize the data
                data, metadata = serializer.serialize(value)
                results_metadata[key] = metadata

                # Add to tar with format-specific extension
                result_path = os.path.join(cls.RESULTS_DIR, f"{key}.{metadata.format}")
                cls._add_bytes_to_tar(tar, result_path, data)

            # Create and add manifest (after we have all metadata)
            manifest = cls._create_manifest(yax_metadata, results_metadata)
            cls._add_bytes_to_tar(tar, cls.MANIFEST_NAME, manifest.encode("utf-8"))

    @classmethod
    def load(  # noqa: C901
        cls,
        filepath: str,
        *,
        no_results: bool = False,
        select: list[str] | str | None = None,
        exclude: list[str] | str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
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

        r_mode = "r:gz" if filepath.endswith(".gz") else "r"
        with tarfile.open(filepath, r_mode) as tar:
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

            # Load manifest
            manifest_file = tar.extractfile(cls.MANIFEST_NAME)
            if manifest_file is None:
                raise ValueError(f"Invalid yaflux archive: missing {cls.MANIFEST_NAME}")
            manifest = json.loads(manifest_file.read().decode("utf-8"))

            # Load parameters
            try:
                parameters_file = tar.extractfile("parameters.pkl")
                metadata["parameters"] = pickle.loads(parameters_file.read())
            except KeyError:
                metadata["parameters"] = None

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
                # Get serialziation info from manifest
                result_meta = manifest["results"][key]
                result_metadata = SerializerMetadata(
                    format=result_meta["format"],
                    type_name=result_meta["type"],
                    module_name=result_meta["module"],
                    size_bytes=result_meta["size_bytes"],
                )

                # Load data using appropriate serializer
                result_path = os.path.join(
                    cls.RESULTS_DIR, f"{key}.{result_metadata.format}"
                )
                result_file = tar.extractfile(result_path)
                if result_file is None:
                    raise YaxMissingResultError(f"Missing result file: {result_path}")

                # Find appropriate serializer by format
                for serializer in SerializerRegistry._serializers:
                    if result_metadata.format == serializer.FORMAT:
                        results[key] = serializer.deserialize(
                            result_file.read(), result_metadata
                        )
                        break
                else:
                    raise ValueError(
                        f"Unknown serialization format: {result_metadata.format}"
                    )

            return metadata, results

    @classmethod
    def is_yaflux_archive(cls, filepath: str) -> bool:
        """Check if file is a yaflux archive."""
        return (
            filepath.endswith(cls.EXTENSION)
            or filepath.endswith(cls.COMPRESSED_EXTENSION)
        ) and tarfile.is_tarfile(filepath)

    @staticmethod
    def _normalize_input(options: list[str] | str | None) -> list[str] | None:
        """Normalize input to a list."""
        if isinstance(options, str):
            return [options]
        return options

    @classmethod
    def _add_bytes_to_tar(
        cls,
        tar: tarfile.TarFile,
        path: str,
        data: bytes,
    ):
        """Add bytes to a tarfile."""
        bytes_io = BytesIO(data)
        info = tarfile.TarInfo(path)
        info.size = len(data)
        tar.addfile(info, bytes_io)
