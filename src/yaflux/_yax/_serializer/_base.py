from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import IO, Any, ClassVar, TypeVar

T = TypeVar("T")


@dataclass
class SerializerMetadata:
    """Metadata about how an object was serialized."""

    format: str  # e.g. "pkl", "h5ad", "parquet"
    type_name: str  # e.g. "AnnData", "DataFrame"
    module_name: str  # e.g. "anndata", "pandas"
    size_bytes: int


class Serializer(ABC):
    """Base class for all serializers."""

    FORMAT: ClassVar[str]  # Class-level constant for format identifier

    @classmethod
    @abstractmethod
    def can_serialize(cls, obj: Any) -> bool:
        """Whether this serializer can handle this object type."""
        pass

    @classmethod
    @abstractmethod
    def serialize(cls, data: Any) -> tuple[bytes | str, SerializerMetadata]:
        """Serialize object to bytes with metadata."""
        pass

    @classmethod
    @abstractmethod
    def deserialize(cls, data: IO[bytes], metadata: SerializerMetadata) -> Any:
        """Deserialize object from bytes using metadata."""
        pass


class SerializerRegistry:
    """Registry of available serializers."""

    _serializers: ClassVar[list[type[Serializer]]] = []

    @classmethod
    def register(cls, serializer: type[Serializer]) -> None:
        cls._serializers.append(serializer)

    @classmethod
    def get_serializer(cls, obj: Any) -> type[Serializer]:
        """Get appropriate serializer for an object."""
        for serializer in cls._serializers:
            if serializer.can_serialize(obj):
                return serializer
        raise ValueError(f"No serializer found for object type: {type(obj)}")
