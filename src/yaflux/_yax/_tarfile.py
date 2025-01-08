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

    VERSION = "0.3.0"
    METADATA_NAME = "metadata.pkl"
    MANIFEST_NAME = "manifest.json"
    RESULTS_DIR = "results"
    EXTENSION = ".yax"  # yaflux archive extension
    COMPRESSED_EXTENSION = ".yax.gz"  # compressed yaflux archive extension

    @classmethod
    def save(
        cls, filepath: str, analysis: Any, force: bool = False, compress: bool = False
    ) -> None:
        """Save analysis to yaflux archive format."""
        filepath = cls._resolve_filepath(filepath, compress, force)

        metadata = cls._create_metadata(analysis)
        results_metadata = {}

        with tarfile.open(filepath, "w:gz" if compress else "w") as tar:
            cls._write_metadata(tar, metadata)
            cls._write_parameters(tar, analysis.parameters)
            cls._write_results(tar, analysis._results._data, results_metadata)
            cls._write_manifest(tar, metadata, results_metadata)

    @classmethod
    def load(
        cls,
        filepath: str,
        *,
        no_results: bool = False,
        select: list[str] | str | None = None,
        exclude: list[str] | str | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Load analysis from yaflux archive format."""
        select = cls._normalize_input(select)
        exclude = cls._normalize_input(exclude)

        with tarfile.open(filepath, "r:gz" if filepath.endswith(".gz") else "r") as tar:
            metadata = cls._read_metadata(tar)
            manifest = cls._read_manifest(tar)
            metadata["parameters"] = cls._read_parameters(tar)

            if no_results:
                return metadata, {}

            to_load = cls._determine_results_to_load(
                metadata["result_keys"], select, exclude
            )
            results = cls._load_results(tar, to_load, manifest)

            return metadata, results

    @classmethod
    def _resolve_filepath(cls, filepath: str, compress: bool, force: bool) -> str:
        """Resolve and validate the output filepath."""
        if filepath.endswith(cls.EXTENSION) and compress:
            filepath = filepath.replace(cls.EXTENSION, cls.COMPRESSED_EXTENSION)
        elif filepath.endswith(cls.COMPRESSED_EXTENSION):
            compress = True
        elif not filepath.endswith(cls.EXTENSION):
            filepath += cls.COMPRESSED_EXTENSION if compress else cls.EXTENSION

        if not force and os.path.exists(filepath):
            raise FileExistsError(f"File already exists: '{filepath}'")

        return filepath

    @classmethod
    def _create_metadata(cls, analysis: Any) -> dict:
        """Create metadata dictionary for the analysis."""
        return {
            "version": cls.VERSION,
            "parameters": analysis.parameters,
            "completed_steps": list(analysis._completed_steps),
            "step_metadata": analysis._results._metadata,
            "result_keys": list(analysis._results._data.keys()),
            "step_ordering": analysis._step_ordering,
            "timestamp": datetime.now().timestamp(),
        }

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
    def _write_metadata(cls, tar: tarfile.TarFile, metadata: dict) -> None:
        """Write metadata to the archive."""
        cls._add_bytes_to_tar(tar, cls.METADATA_NAME, pickle.dumps(metadata))

    @classmethod
    def _write_parameters(cls, tar: tarfile.TarFile, parameters: Any) -> None:
        """Write parameters to the archive."""
        cls._add_bytes_to_tar(tar, "parameters.pkl", pickle.dumps(parameters))

    @classmethod
    def _write_manifest(
        cls, tar: tarfile.TarFile, metadata: dict, results_metadata: dict
    ) -> None:
        """Write manifest to the archive."""
        manifest = cls._create_manifest(metadata, results_metadata)
        cls._add_bytes_to_tar(tar, cls.MANIFEST_NAME, manifest.encode("utf-8"))

    @classmethod
    def _write_results(
        cls, tar: tarfile.TarFile, results: dict, results_metadata: dict
    ) -> None:
        """Write results to the archive."""
        for key, value in results.items():
            serializer = SerializerRegistry.get_serializer(value)
            result, metadata = serializer.serialize(value)
            results_metadata[key] = metadata

            result_path = os.path.join(cls.RESULTS_DIR, f"{key}.{metadata.format}")

            if isinstance(result, str):
                tmp_name = result if not hasattr(result, "name") else result.name  # type: ignore
                tar.add(tmp_name, arcname=result_path)

                # clean up temp file
                if hasattr(result, "name"):
                    result.close()  # type: ignore

                os.unlink(tmp_name)

            else:
                cls._add_bytes_to_tar(tar, result_path, result)

    @classmethod
    def _read_metadata(cls, tar: tarfile.TarFile) -> dict:
        """Read metadata from the archive."""
        metadata_file = tar.extractfile(cls.METADATA_NAME)
        if metadata_file is None:
            raise ValueError(f"Invalid yaflux archive: missing {cls.METADATA_NAME}")

        metadata = pickle.loads(metadata_file.read())
        if "version" not in metadata:
            raise YaxMissingVersionFileError(
                "Invalid yaflux archive: missing version in metadata"
            )

        return metadata

    @classmethod
    def _read_manifest(cls, tar: tarfile.TarFile) -> dict:
        """Read manifest from the archive."""
        manifest_file = tar.extractfile(cls.MANIFEST_NAME)
        if manifest_file is None:
            raise ValueError(f"Invalid yaflux archive: missing {cls.MANIFEST_NAME}")
        return json.loads(manifest_file.read().decode("utf-8"))

    @classmethod
    def _read_parameters(cls, tar: tarfile.TarFile) -> Any:
        """Read parameters from the archive."""
        try:
            parameters_file = tar.extractfile("parameters.pkl")
            if parameters_file is None:
                return None
            return pickle.loads(parameters_file.read())
        except KeyError:
            return None

    @classmethod
    def _determine_results_to_load(
        cls,
        available_results: list[str],
        select: list[str] | None,
        exclude: list[str] | None,
    ) -> set[str]:
        """Determine which results should be loaded."""
        if select is not None and exclude is not None:
            raise ValueError("Cannot specify both select and exclude")

        to_load = set(available_results)
        if select is not None:
            invalid = set(select) - set(available_results)
            if invalid:
                raise YaxMissingResultError(f"Requested results not found: {invalid}")
            to_load = set(select)
        elif exclude is not None:
            to_load -= set(exclude)

        return to_load

    @classmethod
    def _load_results(
        cls, tar: tarfile.TarFile, to_load: set[str], manifest: dict
    ) -> dict:
        """Load selected results from the archive."""
        results = {}
        for key in to_load:
            result_meta = manifest["results"][key]
            result_metadata = SerializerMetadata(
                format=result_meta["format"],
                type_name=result_meta["type"],
                module_name=result_meta["module"],
                size_bytes=result_meta["size_bytes"],
            )

            result_path = os.path.join(
                cls.RESULTS_DIR, f"{key}.{result_metadata.format}"
            )

            # Extract the BufferedIOReader from the tarfile
            result_file = tar.extractfile(result_path)

            if result_file is None:
                raise YaxMissingResultError(f"Missing result file: {result_path}")

            for serializer in SerializerRegistry._serializers:
                if result_metadata.format == serializer.FORMAT:
                    # Deserialize from the BufferedIOReader
                    results[key] = serializer.deserialize(result_file, result_metadata)

                    break
            else:
                raise ValueError(
                    f"Unknown serialization format: {result_metadata.format}"
                )

        return results

    @classmethod
    def _add_bytes_to_tar(cls, tar: tarfile.TarFile, path: str, data: bytes) -> None:
        """Add bytes to a tarfile."""
        bytes_io = BytesIO(data)
        info = tarfile.TarInfo(path)
        info.size = len(data)
        tar.addfile(info, bytes_io)

    @staticmethod
    def _normalize_input(options: list[str] | str | None) -> list[str] | None:
        """Normalize input to a list."""
        if isinstance(options, str):
            return [options]
        return options

    @classmethod
    def is_yaflux_archive(cls, filepath: str) -> bool:
        """Check if file is a yaflux archive."""
        return (
            filepath.endswith(cls.EXTENSION)
            or filepath.endswith(cls.COMPRESSED_EXTENSION)
        ) and tarfile.is_tarfile(filepath)
