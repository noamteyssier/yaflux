import threading
from contextlib import contextmanager


class ResultsLock:
    """Context manager for controlling results mutation with granular key control."""

    _thread_local = threading.local()

    @classmethod
    def can_mutate(cls) -> bool:
        """Check if the current thread is allowed to mutate any results."""
        return getattr(cls._thread_local, "can_mutate", False)

    @classmethod
    def get_mutable_keys(cls) -> set[str]:
        """Get the set of keys that can currently be mutated."""
        return getattr(cls._thread_local, "mutable_keys", set())

    @classmethod
    def can_mutate_key(cls, key: str) -> bool:
        """Check if a specific key can be mutated."""
        if not cls.can_mutate():
            return False
        mutable_keys = cls.get_mutable_keys()
        # If no specific keys are set, allow all mutations when can_mutate is True
        return len(mutable_keys) == 0 or key in mutable_keys

    @classmethod
    @contextmanager
    def allow_mutation(cls, keys: set[str] | None = None):
        """Context manager for allowing results mutation.

        Parameters
        ----------
        keys : Optional[set[str]]
            Set of specific keys that can be mutated. If None, all keys can be mutated.
        """
        previous_state = (
            cls.can_mutate(),
            getattr(cls._thread_local, "mutable_keys", set()),
        )

        cls._thread_local.can_mutate = True
        cls._thread_local.mutable_keys = keys or set()

        try:
            yield
        finally:
            cls._thread_local.can_mutate = previous_state[0]
            cls._thread_local.mutable_keys = previous_state[1]


class FlagLock:
    """Context manager for controlling flag mutation."""

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
