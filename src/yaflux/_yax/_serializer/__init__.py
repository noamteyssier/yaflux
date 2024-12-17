from ._base import SerializerMetadata, SerializerRegistry
from ._formats import PickleSerializer

__all__ = ["PickleSerializer", "SerializerMetadata", "SerializerRegistry"]

# Always register the PickleSerializer as a fallback
SerializerRegistry.register(PickleSerializer)
