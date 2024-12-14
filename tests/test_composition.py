import pytest

import yaflux as yf


class BaseAnalysis(yf.Base):
    """Base analysis class with fundamental steps."""

    @yf.step(creates="base_data")
    def load_base_data(self) -> list[int]:
        return [1, 2, 3, 4, 5]

    @yf.step(creates="base_processed", requires="base_data")
    def process_base(self) -> list[int]:
        return [x * 2 for x in self.results.base_data]


class ExtendedAnalysis(BaseAnalysis):
    """First level of inheritance."""

    @yf.step(creates="extended_data", requires="base_processed")
    def process_extended(self) -> list[int]:
        return [x + 1 for x in self.results.base_processed]

    # Override a base method
    @yf.step(creates="base_data")
    def load_base_data(self) -> list[int]:
        return [10, 20, 30, 40, 50]


class FurtherExtendedAnalysis(ExtendedAnalysis):
    """Second level of inheritance."""

    @yf.step(creates="final_data", requires=["base_processed", "extended_data"])
    def final_process(self) -> list[int]:
        return [
            x + y
            for x, y in zip(self.results.base_processed, self.results.extended_data)
        ]


def test_basic_inheritance():
    """Test that basic inheritance works as expected."""
    analysis = ExtendedAnalysis()

    # Should have access to base methods
    assert hasattr(analysis, "load_base_data")
    assert hasattr(analysis, "process_base")

    # Should have its own methods
    assert hasattr(analysis, "process_extended")


def test_method_override():
    """Test that method overriding works correctly."""
    base = BaseAnalysis()
    extended = ExtendedAnalysis()

    # Run both analyses
    base.load_base_data()
    extended.load_base_data()

    # Check that results differ due to override
    assert base.results.base_data == [1, 2, 3, 4, 5]
    assert extended.results.base_data == [10, 20, 30, 40, 50]


def test_inheritance_chain_execution():
    """Test that multi-level inheritance executes correctly."""
    analysis = FurtherExtendedAnalysis()

    # Should be able to run full chain
    analysis.load_base_data()
    analysis.process_base()
    analysis.process_extended()
    analysis.final_process()

    # Verify results flow through inheritance chain
    assert hasattr(analysis.results, "base_data")
    assert hasattr(analysis.results, "base_processed")
    assert hasattr(analysis.results, "extended_data")
    assert hasattr(analysis.results, "final_data")


def test_dependency_tracking():
    """Test that dependencies work across inheritance levels."""
    analysis = FurtherExtendedAnalysis()

    # Attempting to run steps out of order should fail
    with pytest.raises(ValueError):
        analysis.process_base()  # Should fail without base_data

    with pytest.raises(ValueError):
        analysis.process_extended()  # Should fail without base_processed

    with pytest.raises(ValueError):
        analysis.final_process()  # Should fail without prerequisites

    # Running in correct order should work
    analysis.load_base_data()
    analysis.process_base()
    analysis.process_extended()
    analysis.final_process()


def test_available_steps():
    """Test that available_steps includes inherited steps."""
    analysis = FurtherExtendedAnalysis()

    available = analysis.available_steps
    assert "load_base_data" in available
    assert "process_base" in available
    assert "process_extended" in available
    assert "final_process" in available


def test_completed_steps_inheritance():
    """Test that completed_steps tracks through inheritance."""
    analysis = FurtherExtendedAnalysis()

    analysis.load_base_data()
    assert "load_base_data" in analysis.completed_steps

    analysis.process_base()
    assert "process_base" in analysis.completed_steps

    # Completed steps should work the same regardless of inheritance level
    analysis.process_extended()
    analysis.final_process()
    assert "process_extended" in analysis.completed_steps
    assert "final_process" in analysis.completed_steps


def test_metadata_inheritance():
    """Test that metadata handling works with inheritance."""
    analysis = FurtherExtendedAnalysis()

    # Run all steps
    analysis.load_base_data()
    analysis.process_base()
    analysis.process_extended()
    analysis.final_process()

    # Check metadata for all steps
    for step in analysis.completed_steps:
        metadata = analysis.get_step_metadata(step)
        assert metadata.timestamp > 0
        assert metadata.elapsed >= 0
        assert isinstance(metadata.creates, list)
        assert isinstance(metadata.requires, list)


def test_force_rerun_inheritance():
    """Test that force rerun works with inherited steps."""
    analysis = FurtherExtendedAnalysis()

    # Initial run
    analysis.load_base_data()
    initial_data = analysis.results.base_data.copy()

    # Force rerun should work
    analysis.load_base_data(force=True)  # type: ignore
    assert analysis.results.base_data == initial_data  # Data should be the same

    # Check that downstream steps still work
    analysis.process_base()
    analysis.process_extended()
    analysis.final_process()
