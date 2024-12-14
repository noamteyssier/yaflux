# _executor.py
from collections import deque
from typing import Any, Optional, TypeVar

from ._base import Base

T = TypeVar("T", bound="Base")


class Executor:
    """Handles execution order and dependency management for analysis pipelines."""

    def __init__(self, analysis: "T"):
        self._analysis = analysis

    def _get_dependency_graph(self) -> dict[str, set[str]]:
        """Build adjacency list of step dependencies."""
        graph = {}
        for step_name in self._analysis.available_steps:
            method = getattr(self._analysis.__class__, step_name)
            graph[step_name] = set()

            # Add edges for result dependencies
            for req in zip(method.requires, method.requires_flags):
                for potential_step in self._analysis.available_steps:
                    potential_method = getattr(self._analysis.__class__, potential_step)
                    create_set = set([
                        req for req in zip(potential_method.creates, potential_method.creates_flags)
                    ])
                    if req in create_set:
                        graph[step_name].add(potential_step)

        return graph

    def _get_execution_order(self) -> list[str]:
        """Determine the order of step execution using topological sort."""
        graph = self._get_dependency_graph()
        indegrees = {step: 0 for step in graph}

        # Calculate initial indegrees
        for step in graph:
            for dependent in graph[step]:
                indegrees[dependent] = indegrees.get(dependent, 0) + 1

        # Start with steps that have no dependencies
        queue = deque([step for step, count in indegrees.items() if count == 0])
        execution_order = []

        while queue:
            step = queue.popleft()
            execution_order.append(step)

            # Update dependencies
            for dependent_step in self._analysis.available_steps:
                if step in graph.get(dependent_step, set()):
                    indegrees[dependent_step] -= 1
                    if indegrees[dependent_step] == 0:
                        queue.append(dependent_step)

        if len(execution_order) != len(self._analysis.available_steps):
            raise ValueError("Circular dependency detected in analysis steps")

        return execution_order

    def execute(
        self,
        target_step: Optional[str] = None,
        force: bool = False,
        panic_on_existing: bool = False,
    ) -> Any:
        """Execute analysis steps in dependency order up to target_step."""
        execution_order = self._get_execution_order()

        print(execution_order)

        # If target specified, trim execution order to that step
        if target_step:
            if target_step not in execution_order:
                raise ValueError(f"Step {target_step} not found in analysis")
            target_idx = execution_order.index(target_step)
            execution_order = execution_order[: target_idx + 1]

        # Execute steps in order
        result = None
        for step_name in execution_order:
            method = getattr(self._analysis, step_name)
            if step_name not in self._analysis.completed_steps or force:
                result = method(force=force, panic_on_existing=panic_on_existing)

        return result if target_step else None

    def execute_all(self, force: bool = False, panic_on_existing: bool = False) -> None:
        """Execute all available steps in the analysis."""
        self.execute(force=force, panic_on_existing=panic_on_existing)
