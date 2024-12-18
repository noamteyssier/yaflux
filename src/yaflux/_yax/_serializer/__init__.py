import importlib.util

from ._base import SerializerMetadata, SerializerRegistry
from ._formats import AnnDataSerializer, NumpySerializer, PickleSerializer

__all__ = [
    "AnnDataSerializer",
    "NumpySerializer",
    "PickleSerializer",
    "SerializerMetadata",
    "SerializerRegistry",
]

# Register the serializers
try:
    importlib.util.find_spec("anndata")
    SerializerRegistry.register(AnnDataSerializer)
except ImportError:
    pass  # Anndata is not installed

try:
    importlib.util.find_spec("numpy")
    SerializerRegistry.register(NumpySerializer)
except ImportError:
    pass  # Numpy is not installed

# Always register the pickle serializer last as a fallback
SerializerRegistry.register(PickleSerializer)
