# Advanced Usage

## Analysis Inheritance

One of `yaflux`'s powerful features is its natural support for Python class inheritance. This allows you to:

- Build complex analyses by extending simpler ones
- Override and customize base analysis steps
- Create reusable analysis templates
- Share common functionality across multiple analyses

### Basic Inheritance

Let's look at a simple example of analysis inheritance:

```python
import yaflux as yf

class SimpleAnalysis(yf.Base):
    """A basic analysis pipeline."""

    @yf.step(creates="data")
    def load_data(self):
        return [i for i in range(100)]

    @yf.step(creates="proc_a", requires="data")
    def process_a(self):
        return [i * 2 for i in self.results.data]

    @yf.step(creates="proc_b", requires="proc_a")
    def process_b(self):
        return [i + 1 for i in self.results.proc_a]

class ExtendedAnalysis(SimpleAnalysis):
    """An extended analysis that builds on SimpleAnalysis."""

    def __init__(self):
        super().__init__()

    @yf.step(creates="proc_c", requires=["proc_a", "proc_b"])
    def process_c(self):
        return [a + b for a, b in zip(self.results.proc_a, self.results.proc_b)]

# Create and use the extended analysis
analysis = ExtendedAnalysis()
analysis.load_data()       # Inherited from SimpleAnalysis
analysis.process_a()       # Inherited from SimpleAnalysis
analysis.process_b()       # Inherited from SimpleAnalysis
analysis.process_c()       # Defined in ExtendedAnalysis
```

### Inheritance Features

#### Access to Parent Steps

When you inherit from an analysis class, you get access to all of its steps. These steps:

- Maintain their original dependencies
- Can be called directly from the child class
- Are tracked in the child's completed_steps
- Appear in the child's available_steps

#### Step Dependencies

Dependencies work seamlessly across inheritance boundaries:

```python
class AdvancedAnalysis(SimpleAnalysis):
    @yf.step(creates="advanced_result", requires=["proc_a", "proc_b"])
    def advanced_step(self):
        # Can use results from parent class steps
        return [a * b for a, b in zip(
            self.results.proc_a,
            self.results.proc_b
        )]
```

#### Method Overriding

You can override parent steps to customize their behavior:

```python
class CustomAnalysis(SimpleAnalysis):
    @yf.step(creates="data")  # Same creates/requires as parent
    def load_data(self):
        # Custom implementation
        return [i * 10 for i in range(100)]
```

#### Multi-level Inheritance

`yaflux` supports Python's standard multiple inheritance:

```python
class BaseAnalysis(yf.Base):
    @yf.step(creates="base_data")
    def load_base(self): ...

class MixinAnalysis(yf.Base):
    @yf.step(creates="mixin_data")
    def load_mixin(self): ...

class ComplexAnalysis(BaseAnalysis, MixinAnalysis):
    @yf.step(creates="final", requires=["base_data", "mixin_data"])
    def process_all(self): ...
```

#### Visualization Support

The `visualize_dependencies()` method shows the complete dependency graph, including:

- Steps from all parent classes
- Dependencies between inherited steps
- Custom steps in the child class
- Cross-inheritance dependencies

### Best Practices

When using inheritance with `yaflux`:

1. **Clear Dependencies**: Always explicitly declare dependencies using `requires`, even if they come from parent classes

2. **Consistent Naming**: Use clear, consistent names for results to avoid conflicts between parent and child classes

3. **Documentation**: Document dependencies on parent class steps in your docstrings:

   ```python
   @yf.step(creates="final", requires=["base_data"])
   def final_step(self):
       """Process the final result.

       Requires parent class's load_base_data() to be run first.
       """
       ...
   ```

4. **Modular Design**: Design base classes to be independently useful while allowing for extension
