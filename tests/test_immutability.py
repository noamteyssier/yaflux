import yaflux as yf
from yaflux._results import Results, UnauthorizedMutationError


class Analysis(yf.Base):
    @yf.step(creates="res_a")
    def step_a(self) -> int:
        return 42

    @yf.step(creates="res_b", requires="res_a")
    def step_b(self) -> int:
        return self.results.res_a * 2


def test_immutable_append():
    analysis = Analysis()
    try:
        analysis._results["res_a"] = 42  # type: ignore
        assert False
    except TypeError:
        pass


def test_immutable_setter():
    analysis = Analysis()
    try:
        analysis.results["res_a"] = 42  # type: ignore
        assert False
    except TypeError:
        pass


def test_immutable_modify():
    analysis = Analysis()
    analysis.step_a()
    try:
        analysis.results["res_a"] = 43  # type: ignore
        assert False
    except TypeError:
        pass


def test_immutable_del():
    analysis = Analysis()
    analysis.step_a()
    try:
        del analysis.results["res_a"]  # type: ignore
        assert False
    except TypeError:
        pass


def test_immutable_overwrite():
    analysis = Analysis()
    try:
        analysis._results = Results()
        assert False
    except UnauthorizedMutationError:
        pass
