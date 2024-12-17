import pickle
from typing import Any

from .._base import Serializer, SerializerMetadata


class PickleSerializer(Serializer):
    """Default serializer using pickle."""

    FORMAT = "pkl"

    @classmethod
    def can_serialize(cls, obj: Any) -> bool:
        return True

    @classmethod
    def serialize(cls, obj: Any) -> tuple[bytes, SerializerMetadata]:
        data = pickle.dumps(obj)
        metadata = SerializerMetadata(
            format=cls.FORMAT,
            type_name=type(obj).__name__,
            module_name=type(obj).__module__,
            size_bytes=len(data),
        )
        return data, metadata

    @classmethod
    def deserialize(cls, data: bytes, metadata: SerializerMetadata) -> Any:
        return pickle.loads(data)
