# Design Philosophy

`yaflux` was built around several core design principles that guide its implementation and usage. These principles aim to create a framework that is both powerful and maintainable while remaining true to Python's philosophy of explicit over implicit.

## Core Principles

### 1. Explicit Dependencies

One of the fundamental principles of `yaflux` is that dependencies between analysis steps should be explicitly declared.
This is achieved through the `@step` decorator's `creates` and `requires` parameters:

```python
@yf.step(creates="processed_data", requires="raw_data")
def process_data(self) -> int:
    return self.results.raw_data * 2
```

This explicit declaration serves multiple purposes:

- Makes the code self-documenting
- Enables automatic dependency validation
- Facilitates workflow visualization
- Prevents accidental order-of-execution errors

### 2. Immutable Results

Results in `yaflux` are designed to be effectively immutable once created.
While Python doesn't enforce true immutability, the framework's architecture strongly discourages direct mutation of results:

- Results are accessed through a protected `results` property
- Each step must declare what it creates upfront
- Modifications require explicit force flags
- Results are tracked in a centralized store

This approach helps ensure reproducibility and makes it easier to reason about the state of an analysis at any point in time.

### 3. Minimal Infrastructure

`yaflux` is designed to be lightweight and to work with standard Python tools and practices:

- Zero external dependencies for core functionality
- Uses Python's built-in pickling for serialization
- Works with standard type hints and decorators
- Integrates naturally with existing Python codebases

This minimalist approach makes the library easy to install, maintain, and integrate into existing workflows.

### 4. Fail Fast, Fail Explicitly

The framework is designed to catch errors early and provide clear feedback:

- Dependency requirements are checked before step execution
- Clear error messages when steps are run out of order
- Type hints encourage catching errors at development time
- Explicit validation of step inputs and outputs

### 5. Portable Results

Analysis results should be shareable and accessible even without access to the original analysis code:

- Results can be loaded without the original class definitions
- Metadata about steps and their relationships is preserved
- Clear separation between analysis logic and results storage

## Implementation Decisions

### Analysis as Classes

Analyses in `yaflux` are implemented as classes rather than functions or pipelines for several reasons:

1. Natural encapsulation of related steps
2. Ability to inherit and extend existing analyses
3. Clean interface for accessing results and metadata
4. Consistent state management across steps

### Decorator-Based Step Definition

The choice to use decorators for step definitions provides:

1. Clean syntax that doesn't interfere with method implementation
2. Automatic handling of boilerplate operations
3. Separation of concerns between step logic and framework features
4. Familiar Python pattern that integrates well with IDEs and tools

### Results Management

The `Results` class implementation provides:

1. Attribute-style access to results
2. Protection against accidental mutations
3. Clear separation between results and computation
4. Built-in metadata tracking

## Design Tradeoffs

### Explicit vs. Implicit

`yaflux` chooses explicit dependency declaration over automatic inference. While this requires more upfront code, it provides:

- Better documentation
- Clearer error messages
- Easier debugging
- More maintainable code

### Class-Based vs. Functional

The choice of a class-based approach over a purely functional one adds some complexity but enables:

- Better state management
- More natural result access
- Easier extension and inheritance
- Cleaner implementation of complex workflows

### Serialization Approach

Using Python's pickle for serialization provides simplicity but has some limitations:

- Not language-agnostic
- Potential security concerns with untrusted data
- Version compatibility challenges

These tradeoffs are accepted for the benefits of:

- Zero-dependency serialization
- Full Python object support
- Native handling of complex data types

## Future Considerations

The design of `yaflux` allows for future extensions while maintaining backward compatibility:

1. Alternative serialization formats
2. Parallel execution support
3. Enhanced visualization capabilities
4. Additional metadata tracking
5. Integration with other analysis frameworks

These extensions can be added without compromising the core design principles that make `yaflux` effective for managing complex analytical workflows.
