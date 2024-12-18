import importlib.util

from ._base import SerializerMetadata, SerializerRegistry
from ._formats import (
    AnnDataSerializer,
    NumpySerializer,
    PandasSerializer,
    PickleSerializer,
)

__all__ = [
    "AnnDataSerializer",
    "NumpySerializer",
    "PandasSerializer",
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

try:
    importlib.util.find_spec("pandas")
    importlib.util.find_spec("pyarrow")
    SerializerRegistry.register(PandasSerializer)
except ImportError:
    pass

# Always register the pickle serializer last as a fallback
SerializerRegistry.register(PickleSerializer)
