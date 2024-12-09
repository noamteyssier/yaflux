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

## Example Usage

### Defining and running an analysis

```python
import yaflux as yf

class MyAnalysis(yf.Base):

    @yf.step(creates="processed_data", requires="raw_data")
    def process_data(self) -> typing.Any:
        # Process data here
        return {"processed_data": processed_result}

# Run and save analysis
analysis = MyAnalysis(parameters={...})
analysis.process_data()

# Access results
results = analysis.results.processed_data

# Save analysis state
analysis.save("analysis.pkl")
```

### Loading an analysis

`yaflux` provides a simple way to load and access analysis results:

```python
import yaflux as yf

# Load analysis as a Python object
analysis = MyAnalysis.load("analysis.pkl")

# Access results
results = analysis.results.processed_data

# View metadata
print(analysis.available_steps)
print(analysis.completed_steps)

# Rerun analysis from a specific step
analysis.process_data()
```

### Loading an analysis without original class definition

`yaflux` provides support for sharing analysis results with collaborators who may not have access to your original analysis code.
This is particularly useful when:

- Sharing results with colleagues who don't need the full pipeline
- Archiving analysis results for long-term storage
- Making results available in environments where the original code cannot be installed

```python
import yaflux as yf

# Load without original class definition
portable = yf.load_portable("analysis.pkl")

# Access results
results = portable.results.processed_data

# View metadata
print(portable.available_steps)
print(portable.completed_steps)
```

When loading portable results:

- All results and metadata are preserved.
- Step definitions are replaced with informative placeholders
- Original class definition is not required

## Design Philosophy

`yaflux` was designed around several core principles:

1. **Python-Native**: Built to integrate seamlessly with existing Python analysis workflows
2. **Explicit Dependencies**: Clear declaration of inputs and outputs for each analysis step
3. **State Protection**: Immutable results storage to ensure reproducibility
4. **Minimal Infrastructure**: No external dependencies or services required
5. **Portability**: Complete analyses can be serialized and shared

## Use Cases

`yaflux` is particularly well-suited for:

- Complex data analysis pipelines requiring clear provenance
- Scientific computing workflows where reproducibility is critical
- Collaborative research projects requiring shared analysis states
- Multi-step data transformations needing explicit dependency management

## Implementation

`yaflux` uses Python's type system and decorators to create a lightweight framework that enforces:

- Clear specification of dependencies between analysis steps
- Protected storage of intermediate and final results
- Reproducible execution of analysis pipelines
- Comprehensive tracking of analysis state

## Installation

```bash
pip install yaflux
```
