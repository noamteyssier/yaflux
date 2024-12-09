from dataclasses import dataclass


@dataclass
class Metadata:
    """Fixed data container for step metadata."""

    # What this step creates
    creates: list[str]

    # What this step requires
    requires: list[str]

    # When this step was executed
    timestamp: float

    # How long this step took to execute
    elapsed: float

    # The unnamed arguments for this step
    args: list[str]

    # The named arguments for this step
    kwargs: dict[str, str]

    def to_dict(self):
        return self.__dict__
