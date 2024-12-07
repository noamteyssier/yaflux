from yaflux import BaseAnalysis, AnalysisStep

class MyAnalysis(BaseAnalysis):
    """This is a testing analysis class to model analysis steps.

    This class is used to test the functionality of the analysis steps and the
    analysis pipeline.

    Structure
    =========

    LinearAnalysis:
        lin_a -> lin_b -> lin_c

    DirectedAnalysis:
        dag_a1 -> dag_b1 -> dag_c1
               -> dag_b2 -> dag_c2 \
                         -> dag_c3 \
                                   -> dag_d1

    """

    @AnalysisStep(
        creates=["res_a"],
        requires=[],
    )
    def lin_a(self) -> dict[str, int]:
        return {"res_a": 42}

    @AnalysisStep(
        creates=["res_b"],
        requires=["res_a"],
    )
    def lin_b(self) -> dict[str, int]:
        return {"res_b": 42}

    @AnalysisStep(
        creates=["res_c"],
        requires=["res_b"],
    )
    def lin_c(self) -> dict[str, int]:
        return {"res_c": 42}

    @AnalysisStep(
        creates=["res_a1"],
        requires=[],
    )
    def dag_a1(self) -> dict[str, int]:
        return {"res_a1": 42}

    @AnalysisStep(
        creates=["res_b1"],
        requires=["res_a1"],
    )
    def dag_b1(self) -> dict[str, int]:
        return {"res_b1": 42}

    @AnalysisStep(
        creates=["res_c1"],
        requires=["res_b1"],
    )
    def dag_c1(self) -> dict[str, int]:
        return {"res_c1": 42}

    @AnalysisStep(
        creates=["res_b2"],
        requires=["res_a1"],
    )
    def dag_b2(self) -> dict[str, int]:
        return {"res_b2": 42}

    @AnalysisStep(
        creates=["res_c2"],
        requires=["res_b2"],
    )
    def dag_c2(self) -> dict[str, int]:
        return {"res_c2": 42}

    @AnalysisStep(
        creates=["res_c3"],
        requires=["res_b2"],
    )
    def dag_c3(self) -> dict[str, int]:
        return {"res_c3": 42}

    @AnalysisStep(
        creates=["res_d1"],
        requires=["res_c2", "res_c3"],
    )
    def dag_d1(self) -> dict[str, int]:
        return {"res_d1": 42}

    @AnalysisStep(
        creates=["var_out"],
        requires=[],
    )
    def var_out(self, val: int) -> dict[str, int]:
        return {"var_out": val}

def _assert_out_of_order(analysis, step):
    """Tests for out of order execution of analysis steps."""
    try:
        step()
        assert False
    except ValueError:
        assert True
    assert step.__name__ not in analysis.completed_steps

def _assert_in_order(analysis, step):
    """Tests for in order execution of analysis steps."""
    step()
    assert step.__name__ in analysis.completed_steps

def test_linear_analysis():
    analysis = MyAnalysis(parameters=None)

    _assert_in_order(analysis, analysis.lin_a)
    _assert_in_order(analysis, analysis.lin_b)
    _assert_in_order(analysis, analysis.lin_c)

def test_linear_analysis_out_of_order():
    analysis = MyAnalysis(parameters=None)

    # Run lin_b before lin_a
    _assert_out_of_order(analysis, analysis.lin_b)

    # Run lin_c before lin_a and lin_b
    _assert_out_of_order(analysis, analysis.lin_c)

    # Now run in order
    _assert_in_order(analysis, analysis.lin_a)
    _assert_in_order(analysis, analysis.lin_b)
    _assert_in_order(analysis, analysis.lin_c)

def test_directed_analysis():
    analysis = MyAnalysis(parameters=None)

    # Initial step
    _assert_in_order(analysis, analysis.dag_a1)

    # Branch 1
    _assert_in_order(analysis, analysis.dag_b1)
    _assert_in_order(analysis, analysis.dag_c1)

    # Branch 2
    _assert_in_order(analysis, analysis.dag_b2)
    _assert_in_order(analysis, analysis.dag_c2)

    # Branch 2 -> Branch 3
    _assert_in_order(analysis, analysis.dag_c3)

    # Depends on Branch 2 and Branch 3
    _assert_in_order(analysis, analysis.dag_d1)

def test_directed_analysis_out_of_order():
    analysis = MyAnalysis(parameters=None)

    # Try running b1 before a1
    _assert_out_of_order(analysis, analysis.dag_b1)

    # Try running c2 before b2 and a1
    _assert_out_of_order(analysis, analysis.dag_c2)

    # Try running d1 before its dependencies
    _assert_out_of_order(analysis, analysis.dag_d1)

    # Now run in correct order
    _assert_in_order(analysis, analysis.dag_a1)
    _assert_in_order(analysis, analysis.dag_b2)
    _assert_in_order(analysis, analysis.dag_c2)
    _assert_in_order(analysis, analysis.dag_c3)
    _assert_in_order(analysis, analysis.dag_d1)

def test_partial_branch_execution():
    """Test that we can execute only one branch of the DAG."""
    analysis = MyAnalysis(parameters=None)

    # Execute only branch 1
    _assert_in_order(analysis, analysis.dag_a1)
    _assert_in_order(analysis, analysis.dag_b1)
    _assert_in_order(analysis, analysis.dag_c1)

    # Verify other branches weren't affected
    assert "res_b2" not in analysis.completed_steps
    assert "res_c2" not in analysis.completed_steps
    assert "res_c3" not in analysis.completed_steps
    assert "res_d1" not in analysis.completed_steps


def test_multiple_dependent_steps():
    """Test step with multiple dependencies (dag_d1)."""
    analysis = MyAnalysis(parameters=None)

    # Set up prerequisites
    _assert_in_order(analysis, analysis.dag_a1)
    _assert_in_order(analysis, analysis.dag_b2)

    # Try running d1 with only one dependency met
    _assert_in_order(analysis, analysis.dag_c2)
    _assert_out_of_order(analysis, analysis.dag_d1)

    # Complete all dependencies and verify d1 can run
    _assert_in_order(analysis, analysis.dag_c3)
    _assert_in_order(analysis, analysis.dag_d1)


def test_result_values():
    """Test that the actual values returned by steps are correct."""
    analysis = MyAnalysis(parameters=None)

    # Test linear pipeline results
    analysis.lin_a()
    assert analysis.results["res_a"] == 42

    analysis.lin_b()
    assert analysis.results["res_b"] == 42

    analysis.lin_c()
    assert analysis.results["res_c"] == 42

def test_step_idempotency():
    """Test that running steps multiple times doesn't change results."""
    analysis = MyAnalysis(parameters=None)

    # Run linear pipeline
    analysis.lin_a()
    analysis.lin_b()
    first_result = analysis.results["res_b"]

    # Run middle step again
    analysis.lin_b()
    assert analysis.results["res_b"] == first_result

def test_step_skip():
    """Test that running steps multiple times doesn't change results."""
    analysis = MyAnalysis(parameters=None)

    # Check that we can assign the result
    analysis.var_out(42)
    assert analysis.results.var_out == 42

    # Running the step again should skip regardless of the different value
    analysis.var_out(43)
    assert analysis.results.var_out == 42

    # Running the step again with the force flag should update the value
    analysis.var_out(43, force=True)
    assert analysis.results.var_out == 43

    # Running the step again with the panic_on_existing flag should raise an error
    try:
        analysis.var_out(44, panic_on_existing=True)
        assert False
    except ValueError:
        assert True

def test_completed_steps_tracking():
    """Test that completed_steps is properly tracked."""
    analysis = MyAnalysis(parameters=None)

    assert len(analysis.completed_steps) == 0

    analysis.lin_a()
    assert len(analysis.completed_steps) == 1
    assert "lin_a" in analysis.completed_steps

    analysis.lin_b()
    assert len(analysis.completed_steps) == 2
    assert "lin_b" in analysis.completed_steps
