# Quick Start

`yaflux` helps you manage complex analytical workflows in Python.
It provides a structured approach to tracking transformations, ensuring reproducibility, and maintaining clear provenance.
This quick start guide will show you how to define and run an analysis using `yaflux`.

## Defining an Analysis

Analyses in `yaflux` are defined as classes that inherit from `Base`.

The key components of an analysis are the individual steps that make up the workflow.
These steps are defined as methods within the analysis class and are decorated with `step`.

The `step` decorator allows you to specify the inputs and outputs of each step, as well as any dependencies between steps.

### Example Analysis

Here's an example of an analysis class with three steps:

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
```

### Step Decorator

The `step` decorator is used to define the individual steps of the analysis workflow.

It will automatically handle adding the results of the decorated method to the analysis object so you can focus on functional implementations.

#### Dependencies

It takes the following arguments:

1. `creates`: The name of the result(s) created by the step (if any)
2. `requires`: The name(s) of the result(s) required by the step (if any)

The `creates` and `requires` arguments allow you to specify the inputs and outputs of each step.

The decorated method should return the result(s) of the step.

#### Mutability

Note that in the above example **no step mutates the analysis object**.

The `step` decorator ensures that the results of each step are properly stored and tracked by the analysis object.
This is an attempt to limit the potential for side effects and to make the analysis more reproducible.

## Executing an Analysis

The benefit of using `yaflux` is that it automatically:

1. Tracks dependencies between steps
2. Ensures that each step is only run once
3. Provides a clear record of which steps have been completed

This keeps your analysis organized and reproducible.
It also keeps you from inadvertently running the same step multiple times or running steps out of order.

### Redundant Execution

`yaflux` will by default skip redundant execution of steps.

The `step` method includes a `force` parameter that allows you to force the step to run again.

```python
analysis = MyAnalysis()

# Run the first step
analysis.workflow_step_a()

# Try to run the first step again (skips execution)
analysis.workflow_step_a()

# Force the first step to run again
analysis.workflow_step_a(force=True)

# Panic on redundant execution (raises an error)
analysis.workflow_step_a(panic_on_existing=True)
```

### Dependency Tracking

`yaflux` automatically tracks dependencies between steps.

This means that you can define the order of your analysis steps however you'd like.
`yaflux` will ensure that each step is only runnable once its dependencies have been met.

```python
# Run the first step
analysis = MyAnalysis()
analysis.workflow_step_a()

# Try an invalid step (raises an error)
analysis.workflow_step_c()

# Run the second step
analysis.workflow_step_b()

# Run the third step (works because the second step has been run)
analysis.workflow_step_c()
```

## Saving and Loading Analysis States

One of the advantages of `yaflux` is the ability to save and load analysis states.
This allows you to easily share and reproduce analyses without having to rerun the entire workflow.

### Saving

We can easily save the analysis state to a file:

```python
# We can save the analysis state to a file
analysis.save("analysis.pkl")
```

### Loading

#### Loading with Original Class Definition

If you have access to the original class definition, you can load the analysis state as follows:

```python
import yaflux as yf

# We can load the analysis state from a file
analysis = MyAnalysis.load("analysis.pkl")

# Access results
results = analysis.results.final_data

# View metadata
print(analysis.available_steps)
print(analysis.completed_steps)

# Rerun analysis from a specific step
analysis.workflow_step_b()
```

#### Loading without Original Class Definition

A challenge with custom analysis classes is that some end users may not have access to the original class definition.

`yaflux` provides a solution for this by allowing you to save and load analysis states without the original class definition.

Here's how you can load an analysis without the original class definition:

```python
# Load the analysis state without the original class definition
loaded_analysis = yf.load_portable("analysis.pkl")
```

## Visualizing Analysis Steps

A useful feature of `yaflux` is the ability to visualize the analysis steps.

You can generate a graph of the analysis workflow using the `visualize_dependencies` method:

```python
analysis = MyAnalysis()
analysis.visualize_dependencies()
```

This will create a graph of the analysis steps and their dependencies, which can help you understand the workflow structure.
![Alt text](./assets/example_workflow.svg)

As we run analysis steps this workflow will update to reflect the current state of the analysis.

```python
analysis.workflow_step_a()
analysis.workflow_step_b()
analysis.visualize_dependencies()
```

![Alt text](./assets/example_workflow_filled.svg)