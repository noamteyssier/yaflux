import yaflux as yf


class CreateTesting(yf.Base):
    """This class tests step API."""

    @yf.step()
    def create_null(self):
        pass

    @yf.step(creates="creates_as_str")
    def creates_as_str(self) -> int:
        return 42

    @yf.step(creates=["creates_as_list_singular"])
    def creates_as_list_singular(self) -> int:
        return 42

    @yf.step(creates=["creates_as_list_multiple_a", "creates_as_list_multiple_b"])
    def creates_as_list_multiple(self) -> dict[str, int]:
        return {"creates_as_list_multiple_a": 42, "creates_as_list_multiple_b": 42}

    @yf.step(creates="creates_return_type_singular")
    def creates_return_type_singular(self) -> int:
        return 42

    @yf.step(creates=["tuple_a", "tuple_b"])
    def creates_return_type_unnamed_tuple(self) -> tuple[int, int]:
        return (42, 42)

    @yf.step(creates="expected_tuple")
    def creates_return_type_expected_tuple(self) -> tuple[int, int]:
        """The case where the result is actually a tuple.

        We should not try to split the tuple into separate results.
        """
        return (42, 42)

    @yf.step(creates="creates_return_type_dict")
    def creates_return_type_datastruct(self) -> dict[str, int]:
        return {"creates_return_type_dict": 42}


def test_create_null():
    analysis = CreateTesting(parameters=None)
    analysis.create_null()
    assert "create_null" in analysis.completed_steps


def test_create_as_str():
    analysis = CreateTesting(parameters=None)
    analysis.creates_as_str()
    assert "creates_as_str" in analysis.completed_steps
    assert analysis.results.creates_as_str == 42


def test_create_as_list_singular():
    analysis = CreateTesting(parameters=None)
    analysis.creates_as_list_singular()
    assert "creates_as_list_singular" in analysis.completed_steps


def test_create_as_list_multiple():
    analysis = CreateTesting(parameters=None)
    analysis.creates_as_list_multiple()
    assert "creates_as_list_multiple" in analysis.completed_steps
    assert analysis.results.creates_as_list_multiple_a == 42
    assert analysis.results.creates_as_list_multiple_b == 42


def test_create_return_type_singular():
    analysis = CreateTesting(parameters=None)
    analysis.creates_return_type_singular()
    assert "creates_return_type_singular" in analysis.completed_steps
    assert analysis.results.creates_return_type_singular == 42


def test_create_return_type_unnamed_tuple():
    analysis = CreateTesting(parameters=None)
    analysis.creates_return_type_unnamed_tuple()
    assert "creates_return_type_unnamed_tuple" in analysis.completed_steps
    assert analysis.results.tuple_a == 42
    assert analysis.results.tuple_b == 42


def test_create_return_type_expected_tuple():
    analysis = CreateTesting()
    analysis.creates_return_type_expected_tuple()
    assert "creates_return_type_expected_tuple" in analysis.completed_steps
    assert analysis.results.expected_tuple == (42, 42)
