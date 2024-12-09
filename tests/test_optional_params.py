import yaflux as yf


class OptionalParams(yf.Base):
    """"""


def test_params_null_input():
    analysis = OptionalParams(parameters=None)
    assert analysis.parameters is None


def test_params_no_input():
    analysis = OptionalParams()
    assert analysis.parameters is None


def test_params_some_input():
    analysis = OptionalParams(parameters={"some": "input"})
    assert analysis.parameters is not None
