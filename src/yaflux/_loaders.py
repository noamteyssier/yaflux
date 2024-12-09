# yaflux/_loaders.py
from typing import Union, Type, TypeVar
import pickle

from ._base import Base
from ._portable import Portable

T = TypeVar("T", bound="Base")


class PortableUnpickler(pickle.Unpickler):
    """Custom unpickler that converts Analysis classes to Portable."""

    def find_class(self, module, name):
        try:
            return super().find_class(module, name)
        except (ImportError, AttributeError):
            if name.endswith("Analysis"):
                return Portable
            raise


def load_analysis(cls: Type[T], filepath: str) -> Union[T, Portable]:
    """
    Load analysis, attempting original class first, falling back to portable.
    """
    with open(filepath, "rb") as f:
        try:
            return pickle.load(f)
        except (AttributeError, ImportError):
            return PortableUnpickler(f).load()


def load_portable(filepath: str) -> Portable:
    """
    Load analysis in portable format, regardless of original class availability.
    """
    return Portable.load(filepath)


def to_portable(analysis: Base) -> Portable:
    """Convert an analysis to a portable version."""
    return Portable.from_analysis(analysis)
