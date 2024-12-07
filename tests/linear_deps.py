import yaflux as yf
from _utils import _assert_in_order, _assert_out_of_order

class LinearAnalysis(yf.BaseAnalysis):
    """This is a testing analysis class to model analysis steps.

    This class is used to test the functionality of the analysis steps and the
    analysis pipeline.

    Structure
    =========

    LinearAnalysis:
        lin_a -> lin_b -> lin_c
    """

    @yf.step(creates="res_a")
    def lin_a(self) -> dict[str, int]:
        return {"res_a": 42}

    @yf.step(creates="res_b", requires="res_a")
    def lin_b(self) -> dict[str, int]:
        return {"res_b": 42}

    @yf.step(creates="res_c", requires="res_b")
    def lin_c(self) -> dict[str, int]:
        return {"res_c": 42}

def test_linear_analysis():
    analysis = LinearAnalysis(parameters=None)

    _assert_in_order(analysis, analysis.lin_a)
    _assert_in_order(analysis, analysis.lin_b)
    _assert_in_order(analysis, analysis.lin_c)

def test_linear_analysis_out_of_order():
    analysis = LinearAnalysis(parameters=None)

    # Run lin_b before lin_a
    _assert_out_of_order(analysis, analysis.lin_b)

    # Run lin_c before lin_a and lin_b
    _assert_out_of_order(analysis, analysis.lin_c)

    # Now run in order
    _assert_in_order(analysis, analysis.lin_a)
    _assert_in_order(analysis, analysis.lin_b)
    _assert_in_order(analysis, analysis.lin_c)
