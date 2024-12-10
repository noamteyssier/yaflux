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
