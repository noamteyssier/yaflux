class CircularDependencyError(Exception):
    def __init__(self, node):
        self.node = node

    def __str__(self):
        return f"Circular dependency detected at node {self.node}."


class MutabilityConflictError(Exception):
    def __init__(self, level: int, conflicts: list[tuple[str, str, set[str]]]):
        self.level = level
        self.conflicts = conflicts

    def __str__(self):
        return (
            f"Mutability conflicts detected at level {self.level}:\n"
            + "\n".join(
                [
                    f"  {step1} + {step2}: {conflict}"
                    for step1, step2, conflict in self.conflicts
                ]
            )
            + "\n"
            "Please ensure that the mutability levels are unambiguous using flags."
        )
