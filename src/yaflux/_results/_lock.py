import threading
from contextlib import contextmanager


class ThreadSafeLock:
    """Context manager for controlling thread-safe mutation."""

    _thread_local = threading.local()

    @classmethod
    def can_mutate(cls) -> bool:
        """Check if the current thread is allowed to mutate."""
        return getattr(cls._thread_local, "can_mutate", False)

    @classmethod
    @contextmanager
    def allow_mutation(cls):
        """Context manager for allowing mutation."""
        previous = cls.can_mutate()
        cls._thread_local.can_mutate = True
        try:
            yield
        finally:
            cls._thread_local.can_mutate = previous


class ResultsLock(ThreadSafeLock):
    """Context manager for controlling results mutation."""


class FlagLock(ThreadSafeLock):
    """Context manager for controlling flag mutation."""
