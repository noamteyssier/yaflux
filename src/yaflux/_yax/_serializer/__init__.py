import importlib.util

from ._base import SerializerMetadata, SerializerRegistry
from ._formats import AnnDataSerializer, PickleSerializer

__all__ = [
    "PickleSerializer",
    "SerializerMetadata",
    "SerializerRegistry",
    "AnnDataSerializer",
]

# Register the serializers
try:
    importlib.util.find_spec("anndata")
    SerializerRegistry.register(AnnDataSerializer)
except ImportError:
    pass  # Anndata is not installed

# Always register the pickle serializer last as a fallback
SerializerRegistry.register(PickleSerializer)
