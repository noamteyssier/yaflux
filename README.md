# yaflux

A declarative framework for managing complex analytical workflows in Python.

## Overview

yaflux provides a structured approach to managing complex data analysis pipelines where tracking transformations, ensuring reproducibility, and maintaining clear provenance are essential. It offers a pure Python solution for declaring dependencies between analysis steps and managing results immutably.

## Key Features

- **Declarative Workflow Definition**: Analysis steps are defined through decorators that explicitly state their inputs and outputs
- **Immutable Results Management**: Results are tracked and protected from inadvertent mutation
- **Dependency Tracking**: Automatic tracking of dependencies between analysis steps
- **Progress Monitoring**: Built-in tracking of completed analysis steps
- **Serialization**: Simple persistence of complete analysis states

## Example Usage

```python
from yaflux import BaseAnalysis, step

class MyAnalysis(BaseAnalysis):

    @step(creates="processed_data", requires="raw_data")
    def process_data(self):
        # Process data here
        return {"processed_data": processed_result}
```

## Design Philosophy

yaflux was designed around several core principles:

1. **Python-Native**: Built to integrate seamlessly with existing Python analysis workflows
2. **Explicit Dependencies**: Clear declaration of inputs and outputs for each analysis step
3. **State Protection**: Immutable results storage to ensure reproducibility
4. **Minimal Infrastructure**: No external dependencies or services required
5. **Portability**: Complete analyses can be serialized and shared

## Use Cases

yaflux is particularly well-suited for:

- Complex data analysis pipelines requiring clear provenance
- Scientific computing workflows where reproducibility is critical
- Collaborative research projects requiring shared analysis states
- Multi-step data transformations needing explicit dependency management

## Implementation

yaflux uses Python's type system and decorators to create a lightweight framework that enforces:

- Clear specification of dependencies between analysis steps
- Protected storage of intermediate and final results
- Reproducible execution of analysis pipelines
- Comprehensive tracking of analysis state

## Current Status

Originally developed for single-cell sequencing analysis workflows at the Arc Institute, yaflux has been designed as a general-purpose framework suitable for any complex Python analysis requiring structured workflow management.

## Installation

```bash
pip install yaflux
```
