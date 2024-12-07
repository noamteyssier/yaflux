from yaflux import BaseAnalysis, step

class MyAnalysis(BaseAnalysis):

    @step(creates="res_a")
    def step_a(self) -> dict[str, int]:
        return {"res_a": 42}

    @step(creates="res_b")
    def step_b(self) -> dict[str, int]:
        return {"res_b": 42}

def test_completed_steps_tracking():
    """Test that completed_steps is properly tracked."""
    analysis = MyAnalysis(parameters=None)

    assert len(analysis.completed_steps) == 0

    analysis.step_a()
    assert len(analysis.completed_steps) == 1
    assert "step_a" in analysis.completed_steps

    analysis.step_b()
    assert len(analysis.completed_steps) == 2
    assert "step_b" in analysis.completed_steps
