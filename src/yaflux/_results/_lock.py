import threading
from contextlib import contextmanager


class ResultsLock:
    """Context manager for controlling results mutation."""

    _thread_local = threading.local()

    @classmethod
    def can_mutate(cls) -> bool:
        """Check if the current thread is allowed to mutate results."""
        return getattr(cls._thread_local, "can_mutate", False)

    @classmethod
    @contextmanager
    def allow_mutation(cls):
        """Context manager for allowing results mutation."""
        previous = cls.can_mutate()
        cls._thread_local.can_mutate = True
        try:
            yield
        finally:
            cls._thread_local.can_mutate = previous
