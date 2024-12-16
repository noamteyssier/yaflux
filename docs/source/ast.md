# Abstract Syntax Tree (AST)

One of the key components of `yaflux` is the ability to perform static analysis on the declared workflow at initialization time.
Wrapped methods of the `@yf.step` decorator can have their source code directly inspected and validated for correctness.
Because decorators are evaluated at class definition time, we can perform these checks before any analysis steps are run, and provide immediate feedback if the workflow is incorrect.

This feature is similar to compile-time errors in statically typed languages, but in this case, we are checking the structure of the workflow rather than the types of the variables.

This stops you from running a workflow that is guaranteed to fail, and helps catch errors early in the development process.

## Validations

### Dependency Usage

One of the primary validations performed on the AST is to ensure that all results used by a step are declared as requirements.

For example, consider the following step:

```python
import yaflux as yf

class Analysis(yf.Base):

    @yf.step(creates="processed_data", requires="raw_data")
    def process_data(self) -> int:
        return self.results.raw_data * 2
```

We can inspect the source code of the `process_data` method and verify that the `raw_data` result is declared as a requirement.

Lets instead create a step that uses an undeclared result:

```python
import yaflux as yf

class Analysis(yf.Base):

    @yf.step(creates="processed_data")
    def process_data(self) -> int:
        # does not declare 'raw_data' as a requirement
        return self.results.raw_data * 2
```

A nice benefit of the `@yf.step` decorator is that when this class definition is loaded, `yaflux` will raise an error indicating that the `raw_data` result is used without being declared as a requirement.

```python
import yaflux as yf

try:
    class Analysis(yf.Base):

        @yf.step(creates="processed_data")
        def process_data(self) -> int:
            # does not declare 'raw_data' as a requirement
            return self.results.raw_data * 2

except yf.AstUndeclaredUsageError as e:
    print(e)
```

This validation is crucial for ensuring that the declared workflow is correct and that all dependencies are explicitly stated.

### Direct Assignments

One of the important characteristics of `yaflux` is that results must be tracked by the framework to ensure immutability and stop side effects.
This means that direct assignments to `self` is not allowed, as it would bypass the tracking mechanism.

For example, consider the following step:

```python
import yaflux as yf

class Analysis(yf.Base):

    @yf.step(creates="processed_data", requires="raw_data")
    def process_data(self) -> int:
        self.alias_data = self.results.raw_data * 2
        return self.alias_data
```

In this case, the `processed_data` result is assigned directly to `self`, which bypasses the tracking mechanism.
It also makes it harder to reason about the state of the analysis and can lead to unexpected behavior.

When this class definition is loaded, `yaflux` will raise an error indicating that direct assignments are not allowed.

```python
import yaflux as yf

try:
    class Analysis(yf.Base):

        @yf.step(creates="processed_data", requires="raw_data")
        def process_data(self) -> int:
            self.alias_data = self.results.raw_data * 2
            return self.alias_data

except yf.AstSelfMutationError as e:
    print(e)
```
