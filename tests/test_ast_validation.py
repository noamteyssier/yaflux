import pytest

import yaflux as yf


def test_ast_validation():
    """Test that AST validation catches undeclared results access."""

    with pytest.raises(yf.AstUndeclaredUsageError) as exc:

        class BadAnalysis(yf.Base):
            @yf.step(creates="output")
            def bad_step(self) -> int:
                # Accessing result without declaring it
                return self.results.undeclared * 2

    assert exc.value.func_name == "bad_step"
    assert exc.value.undeclared == ["undeclared"]

    # Should work with proper declaration
    class GoodAnalysis(yf.Base):
        @yf.step(creates="output", requires="input")
        def good_step(self) -> int:
            return self.results.input * 2


def test_ast_validation_multiple_accesses():
    """Test validation with multiple results accesses."""

    with pytest.raises(yf.AstUndeclaredUsageError) as exc:

        class BadAnalysis(yf.Base):
            @yf.step(creates="output", requires="a")
            def bad_step(self) -> int:
                # Only 'a' is declared but accessing multiple
                x = self.results.a
                y = self.results.b
                z = self.results.c
                return x + y + z

    assert exc.value.func_name == "bad_step"
    assert "b" in exc.value.undeclared
    assert "c" in exc.value.undeclared
    assert "a" not in exc.value.undeclared


def test_ast_validation_nested_access():
    """Test validation catches nested access patterns."""

    with pytest.raises(yf.AstUndeclaredUsageError) as exc:

        class BadAnalysis(yf.Base):
            @yf.step(creates="output")
            def bad_step(self) -> int:
                def inner():
                    return self.results.nested

                return inner() * 2

    assert exc.value.func_name == "bad_step"
    assert exc.value.undeclared == ["nested"]


def test_self_assignment():
    with pytest.raises(yf.AstSelfMutationError) as exc:

        class Analysis(yf.Base):
            @yf.step(creates="some")
            def some_step(self):
                self.some = 1
                return 42

    assert exc.value.func_name == "some_step"
    assert exc.value.mutated == ["some"]
