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

## Contents

```{toctree}
:maxdepth: 2

installation
quick_start
design
advanced_usage
```

## API

```{toctree}
:maxdepth: 2

api/index
```
