import os
import tempfile
from typing import IO, Any

from .._base import Serializer, SerializerMetadata


class PandasSerializer(Serializer):
    """Serializer for Pandas DataFrames using Apache Arrow.

    This serializer is only active if pandas and pyarrow are installed.
    Install optional dependencies with:
        pip install yaflux[pandas]
    """

    FORMAT = "arrow"

    @classmethod
    def can_serialize(cls, obj: Any) -> bool:
        """Check if object is a pandas DataFrame."""
        try:
            import pandas as pd

            return isinstance(obj, pd.DataFrame)
        except ImportError:
            return False

    @classmethod
    def serialize(cls, data: Any) -> tuple[str, SerializerMetadata]:
        """Serialize DataFrame to Arrow format."""
        try:
            import pandas as pd
            import pyarrow as pa
        except ImportError as e:
            raise ImportError(
                "pandas and pyarrow packages are required for DataFrame serialization. "
                "Install with: pip install yaflux[pandas]"
            ) from e

        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data must be a pandas DataFrame")

        # Create a temporary file that will persist until explicitly deleted
        tmp = tempfile.NamedTemporaryFile(suffix=f".{cls.FORMAT}", delete=False)  # noqa

        # Convert DataFrame to Arrow Table and write to file
        table = pa.Table.from_pandas(data)
        with pa.OSFile(tmp.name, "wb") as sink:  # noqa
            with pa.RecordBatchFileWriter(sink, table.schema) as writer:
                writer.write_table(table)

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
        """Deserialize bytes back into a DataFrame."""
        try:
            from io import BytesIO

            import pyarrow as pa
        except ImportError as e:
            raise ImportError(
                "pandas and pyarrow are required for DataFrame deserialization. "
                "Install with: pip install yaflux[pandas]"
            ) from e

        buffer = BytesIO(data.read())
        try:
            # Read Arrow Table from buffer and convert to DataFrame
            reader = pa.ipc.RecordBatchFileReader(buffer)
            table = reader.read_all()
            return table.to_pandas()
        except Exception as e:
            raise ValueError(f"Failed to deserialize DataFrame: {e!s}") from e
        finally:
            buffer.close()
