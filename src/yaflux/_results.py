class Results:
    """Dynamic container for analysis results."""

    def __init__(self):
        self._data = {}

    def __getitem__(self, name):
        return self._data[name]

    def __getattr__(self, name):
        try:
            # Only try to get from _data if the attribute doesn't exist normally
            if name == "_data":
                raise AttributeError(f"No attribute named '{name}' exists")
            return self._data[name]
        except KeyError as exc:
            raise AttributeError(f"No result named '{name}' exists") from exc

    def __delattr__(self, name: str) -> None:
        if name == "_data":
            raise AttributeError(f"Cannot delete attribute '{name}'")
        try:
            del self._data[name]
        except KeyError as exc:
            raise AttributeError(f"No result named '{name}' exists") from exc

    def __setattr__(self, name, value):
        if name == "_data":
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value

    def __dir__(self):
        return list(self._data.keys())

    def __repr__(self):
        return f"{self.__class__.__name__}({list(self._data.keys())})"

    def __getstate__(self):
        return self._data

    def __setstate__(self, state):
        self._data = state
