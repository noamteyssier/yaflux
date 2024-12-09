import yaflux as yf


class SimpleAnalysis(yf.Base):
    """Simple analysis class for testing portability."""

    @yf.step(creates="res_a")
    def step_a(self) -> int:
        return 42

    @yf.step(creates="res_b", requires="res_a")
    def step_b(self) -> int:
        return self.results.res_a * 2


def test_to_portable():
    """Test converting a live analysis to portable format."""
    analysis = SimpleAnalysis(parameters={"x": 1})
    analysis.step_a()
    analysis.step_b()

    # Convert to portable
    portable = yf.to_portable(analysis)

    # Check core attributes maintained
    assert portable.parameters == {"x": 1}
    assert portable.results.res_a == 42
    assert portable.results.res_b == 84
    assert set(portable.completed_steps) == {"step_a", "step_b"}

    # Check step metadata preserved
    assert "step_a" in portable.available_steps
    assert "step_b" in portable.available_steps

    # Verify methods raise appropriate errors
    try:
        portable.step_a()  # type: ignore (should raise NotImplementedError)
        assert False, "Should have raised NotImplementedError"
    except NotImplementedError as e:
        assert "step_a" in str(e)
        assert "creates" in str(e)


def test_portable_metadata():
    """Test metadata about steps is preserved correctly."""
    analysis = SimpleAnalysis(parameters={"x": 1})
    portable = yf.to_portable(analysis)

    # Check step_a metadata
    try:
        portable.step_a()  # type: ignore (should raise NotImplementedError)
    except NotImplementedError as e:
        error_msg = str(e)
        assert "creates: ['res_a']" in error_msg
        assert "requires: []" in error_msg

    # Check step_b metadata
    try:
        portable.step_b()  # type: ignore (should raise NotImplementedError)
    except NotImplementedError as e:
        error_msg = str(e)
        assert "creates: ['res_b']" in error_msg
        assert "requires: ['res_a']" in error_msg
