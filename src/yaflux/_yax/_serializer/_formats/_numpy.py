import os
import tempfile
from typing import IO, Any

from .._base import Serializer, SerializerMetadata


class NumpySerializer(Serializer):
    """Serializer for numpy arrays.

    This serializer is only active if numpy is installed.
    install optional dependency with:
        pip install yaflux[numpy]
    """

    FORMAT = "npy"

    @classmethod
    def can_serialize(cls, obj: Any) -> bool:
        """Check if object is an ndarray instance."""
        try:
            import numpy as np

            return isinstance(obj, np.ndarray)
        except ImportError:
            return False

    @classmethod
    def serialize(cls, data: Any) -> tuple[str, SerializerMetadata]:
        """Serialize numpy object to bytes."""
        try:
            import numpy as np
        except ImportError as e:
            raise ImportError(
                "numpy package is required for numpy serialization. "
                "Install with: pip install yaflux[numpy]"
            ) from e

        if not isinstance(data, np.ndarray):
            raise TypeError("Data must be a numpy object")

        # Create a temporary file that will persist until explicitly deleted
        # (should be done in the tar serializer)
        tmp = tempfile.NamedTemporaryFile(suffix=f".{cls.FORMAT}", delete=False)  # noqa

        # Write to a temporary file
        np.save(tmp.name, data)
        tmp.flush()

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
    def deserialize(cls, data: IO[bytes], metadata: SerializerMetadata) -> Any:
        """Deserialize bytes back into a numpy object."""
        try:
            from io import BytesIO

            import numpy as np
        except ImportError as e:
            raise ImportError(
                "numpy package is required for numpy deserialization. "
                "Install with: pip install yaflux[numpy]"
            ) from e

        buffer = BytesIO(data.read())
        try:
            return np.load(buffer)
        except Exception as e:
            raise ValueError(f"Failed to deserialize numpy: {e!s}") from e
        finally:
            buffer.close()
