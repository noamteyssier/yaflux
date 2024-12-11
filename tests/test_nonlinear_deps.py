from _utils import _assert_in_order, _assert_out_of_order

import yaflux as yf


class DirectedAnalysis(yf.Base):
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

    @yf.step(creates="res_a1")
    def dag_a1(self) -> int:
        return 42

    @yf.step(creates="res_b1", requires="res_a1")
    def dag_b1(self) -> int:
        _ = self.results.res_a1
        return 42

    @yf.step(creates="res_c1", requires="res_b1")
    def dag_c1(self) -> int:
        _ = self.results.res_b1
        return 42

    @yf.step(creates="res_b2", requires="res_a1")
    def dag_b2(self) -> int:
        _ = self.results.res_a1
        return 42

    @yf.step(creates="res_c2", requires="res_b2")
    def dag_c2(self) -> int:
        _ = self.results.res_b2
        return 42

    @yf.step(creates="res_c3", requires="res_b2")
    def dag_c3(self) -> int:
        _ = self.results.res_b2
        return 42

    @yf.step(creates="res_d1", requires=["res_c2", "res_c3"])
    def dag_d1(self) -> int:
        _ = self.results.res_c2
        _ = self.results.res_c3
        return 42


def test_directed_analysis():
    analysis = DirectedAnalysis(parameters=None)

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
    analysis = DirectedAnalysis(parameters=None)

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
    analysis = DirectedAnalysis(parameters=None)

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
    analysis = DirectedAnalysis(parameters=None)

    # Set up prerequisites
    _assert_in_order(analysis, analysis.dag_a1)
    _assert_in_order(analysis, analysis.dag_b2)

    # Try running d1 with only one dependency met
    _assert_in_order(analysis, analysis.dag_c2)
    _assert_out_of_order(analysis, analysis.dag_d1)

    # Complete all dependencies and verify d1 can run
    _assert_in_order(analysis, analysis.dag_c3)
    _assert_in_order(analysis, analysis.dag_d1)
