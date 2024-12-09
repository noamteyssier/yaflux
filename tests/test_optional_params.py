from types import NoneType

import yaflux as yf


class OptionalParams(yf.Base):
    """"""


def test_params_null_input():
    analysis = OptionalParams(parameters=None)
    assert isinstance(analysis.parameters, NoneType)


def test_params_no_input():
    analysis = OptionalParams()
    assert isinstance(analysis.parameters, NoneType)


def test_params_some_input():
    analysis = OptionalParams(parameters={"some": "input"})
    assert isinstance(analysis.parameters, dict)
