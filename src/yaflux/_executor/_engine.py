from collections import deque
from typing import Any

from .._base import Base
from .._graph import build_read_graph
from ._error import (
    ExecutorCircularDependencyError,
    ExecutorMissingStartError,
    ExecutorMissingTargetStepError,
)


class Executor:
    """Handles execution order and dependency management for analysis pipelines."""

    def __init__(self, analysis: "Base"):
        self._analysis = analysis

    def _calculate_indegrees(self, graph: dict[str, set[str]]) -> dict[str, int]:
        """Calculate the indegree of each step in the dependency graph."""
        return {step: len(graph[step]) for step in graph}

    def _get_execution_order(self) -> list[str]:
        """Determine the order of step execution using topological sort."""
        graph = build_read_graph(self._analysis)
        indegrees = self._calculate_indegrees(graph)

        # Start with steps that have no dependencies
        queue = deque([step for step, count in indegrees.items() if count == 0])
        processed_steps = set(queue)
        execution_order = []

        if len(queue) == 0:
            raise ExecutorMissingStartError(
                "No possible starting step found in analysis."
            )

        while queue:
            step = queue.popleft()
            execution_order.append(step)
            processed_steps.add(step)

            # Update dependencies
            for dependent_step in self._analysis.available_steps:
                if step in graph.get(dependent_step, set()):
                    indegrees[dependent_step] -= 1
                    if indegrees[dependent_step] == 0:
                        if dependent_step in processed_steps:
                            raise ExecutorCircularDependencyError(
                                "Circular dependency detected in analysis steps: "
                                + f"{step}"
                            )
                        queue.append(dependent_step)

        if len(execution_order) != len(self._analysis.available_steps):
            raise ExecutorCircularDependencyError(
                "Circular dependency detected in analysis steps"
            )

        return execution_order

    def execute(
        self,
        target_step: str | None = None,
        force: bool = False,
        panic_on_existing: bool = False,
    ) -> Any:
        """Execute analysis steps in dependency order up to target_step."""
        execution_order = self._get_execution_order()

        # If target specified, trim execution order to that step
        if target_step:
            if target_step not in execution_order:
                raise ExecutorMissingTargetStepError(
                    f"Step {target_step} not found in analysis"
                )
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
