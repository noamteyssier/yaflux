# yaflux

A declarative framework for managing complex analytical workflows in Python.

## Overview

`yaflux` provides a structured approach to managing complex data analysis pipelines where tracking transformations, ensuring reproducibility, and maintaining clear provenance are essential. It offers a pure Python solution for declaring dependencies between analysis steps and managing results immutably.

## Key Features

- **Declarative Workflow Definition**: Analysis steps are defined through decorators that explicitly state their inputs and outputs
- **Immutable Results Management**: Results are tracked and protected from inadvertent mutation
- **Dependency Tracking**: Automatic tracking of dependencies between analysis steps
- **Progress Monitoring**: Built-in tracking of completed analysis steps
- **Serialization**: Simple persistence of complete analysis states
- **Portable Results**: Analysis results can be shared and loaded without original class definitions

## Example

With `yaflux`, you can define complex analytical workflows in a structured and reproducible way.

All methods are functional and the step decorator handles mutations to the analysis object.
You can specify dependencies between steps and `yaflux` will automatically track them.
This allows you to focus on the functional implementation of each step and limit side effects.

```python
import yaflux as yf

class MyAnalysis(yf.Base):
    """An example analysis class."""

    # Define analysis steps
    @yf.step(creates="raw_data")
    def workflow_step_a(self) -> list[int]:
        return [i for i in range(10)]

    # Specify dependencies between steps
    @yf.step(creates="processed_data", requires="raw_data")
    def workflow_step_b(self) -> list[int]:
        return [i * 2 for i in self.results.raw_data]

    # Combine results from previous steps
    @yf.step(creates="final_data", requires=["raw_data", "processed_data"])
    def workflow_step_c(self) -> list[int]:
        return [i + j for i in self.results.raw_data for j in self.results.processed_data]

    # Define a complete workflow however you'd like
    def run(self):
        self.workflow_step_a()
        self.workflow_step_b()
        self.workflow_step_c()

# Define and run an analysis
analysis = MyAnalysis()
analysis.run()

# Access results
final = analysis.results.final_data

# Save and load analysis state
analysis.save("analysis.pkl")

# Load analysis state
loaded = MyAnalysis.load("analysis.pkl")

# Load analysis without original class definition
loaded = yf.load_portable("analysis.pkl")

# Skip redudant steps
analysis.workflow_step_a() # skipped

# Force re-run of a step
analysis.workflow_step_a(force=True) # re-run

# Visualize the analysis (using graphviz)
analysis.visualize_dependencies()

# See how an analysis step was run and its metadata
metadata = analysis.get_step_metadata("workflow_step_b")
```

## Visualizing Complex Workflows

`yaflux` provides a built-in method for visualizing the dependencies between analysis steps.
This can be useful for understanding complex workflows and ensuring that all dependencies are correctly specified.

Let's first define a complex analysis with multiple steps and dependencies:

```python
import yaflux as yf


class MyAnalysis(yf.Base):

    @yf.step(creates=["x", "y", "z"])
    def load_data(self) -> tuple[int, int, int]:
        return 1, 2, 3

    @yf.step(creates="proc_x", requires="x")
    def process_x(self) -> int:
        return self.results.x + 1

    @yf.step(creates=["proc_y1", "proc_y2"], requires="y")
    def process_y(self) -> tuple[int, int]:
        return (
            self.results.y + 1,
            self.results.y + 2,
        )

    @yf.step(creates="proc_z", requires=["proc_y1", "proc_y2", "z"])
    def process_z(self) -> int:
        return self.results.proc_y1 + self.results.proc_y2 + self.results.z

    @yf.step(creates="final", requires=["proc_x", "proc_z"])
    def final(self) -> int:
        return self.results.proc_x + self.results.proc_z

    def run(self):
        self.load_data()
        self.process_x()
        self.process_y()
        self.process_z()
        self.final()
```

Now we can visualize the dependencies between the analysis steps:

```python
analysis = MyAnalysis()
analysis.visualize_dependencies()
```

![Dependency Graph](docs/source/assets/complex_workflow_init.svg)

As we run the analysis, we can fill in the dependency graph and see where we are in the workflow.

```python
analysis.load_data()
analysis.process_x()
analysis.process_y()

# Visualize the updated dependencies
analysis.visualize_dependencies()
```

![Dependency Graph](docs/source/assets/complex_workflow_progress.svg)

## Installation

For a base python installation with zero external dependencies use:

```bash
pip install yaflux
```

For a more feature-rich installation with additional dependencies use:

```bash
pip install yaflux[full]
```

Or if you want a specific subset of features, you can install individual extras:

```bash
pip install yaflux[viz]
```
