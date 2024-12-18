import os
import tempfile
from typing import Any, BinaryIO

from .._base import Serializer, SerializerMetadata


class AnnDataSerializer(Serializer):
    """Serializer for AnnData objects using the native h5ad format.

    This serializer is only active if anndata is installed.
    Install optional dependency with:
        pip install yaflux[anndata]
    """

    FORMAT = "h5ad"

    @classmethod
    def can_serialize(cls, obj: Any) -> bool:
        """Check if object is an AnnData instance."""
        try:
            import anndata as ad

            return isinstance(obj, ad.AnnData)
        except ImportError:
            return False

    @classmethod
    def serialize(cls, data: Any) -> tuple[str | BinaryIO, SerializerMetadata]:
        """Serialize AnnData object to bytes."""
        try:
            import anndata as ad
        except ImportError as e:
            raise ImportError(
                "anndata package is required for AnnData serialization. "
                "Install with: pip install yaflux[anndata]"
            ) from e

        if not isinstance(data, ad.AnnData):
            raise TypeError("Data must be an AnnData object")

        # Create a temporary file that will persist until explicitly deleted
        # (should be done in the tar serializer)
        tmp = tempfile.NamedTemporaryFile(suffix=".h5ad", delete=False)  # noqa

        # Write to a temporary file
        data.write_h5ad(tmp.name)

        # Get file size for metadata
        size = os.path.getsize(tmp.name)

        # Create metadata
        metadata = SerializerMetadata(
            format=cls.FORMAT,
            type_name=type(data).__name__,
            module_name=type(data).__module__,
            size_bytes=size,
        )

        return tmp.name, metadata

    @classmethod
    def deserialize(cls, data: bytes, metadata: SerializerMetadata) -> Any:
        """Deserialize bytes back into an AnnData object."""
        try:
            from io import BytesIO

            import anndata as ad
        except ImportError as e:
            raise ImportError(
                "anndata package is required for AnnData deserialization. "
                "Install with: pip install yaflux[anndata]"
            ) from e

        buffer = BytesIO(data)
        try:
            return ad.read_h5ad(buffer)
        except Exception as e:
            raise ValueError(f"Failed to deserialize AnnData: {e!s}") from e
        finally:
            buffer.close()
