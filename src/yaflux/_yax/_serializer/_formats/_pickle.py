import pickle
from typing import IO, Any

from .._base import Serializer, SerializerMetadata


class PickleSerializer(Serializer):
    """Default serializer using pickle."""

    FORMAT = "pkl"

    @classmethod
    def can_serialize(cls, obj: Any) -> bool:
        return True

    @classmethod
    def serialize(cls, data: Any) -> tuple[bytes, SerializerMetadata]:
        bytes = pickle.dumps(data)
        metadata = SerializerMetadata(
            format=cls.FORMAT,
            type_name=type(data).__name__,
            module_name=type(data).__module__,
            size_bytes=len(bytes),
        )
        return bytes, metadata

    @classmethod
    def deserialize(cls, data: IO[bytes], metadata: SerializerMetadata) -> Any:
        return pickle.loads(data.read())
