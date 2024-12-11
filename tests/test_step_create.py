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

    @yf.step(creates="inferred_key")
    def creates_return_type_datastruct(self) -> dict[str, int]:
        return {"inferred_key": 42}

    @yf.step(creates="results_dict")
    def creates_return_singular_dict(self) -> dict[str, int]:
        """The case where a singular value is returned as a dictionary.

        In this case inference should give us a `result.results_dict` attribute
        and not a `result.a` and `result.b` attribute.
        """
        return {
            "a": 42,
            "b": 42,
        }

    @yf.step(creates=["a", "b"])
    def creates_return_superset_dict(self) -> dict[str, int]:
        """The case where the results dict is a superset of the creates list.

        This should raise an error because it's ambiguous as a potential bug.
        """
        return {
            "a": 42,
            "b": 42,
            "c": 42,
        }

    @yf.step(creates=["a", "b", "_flag", "c"])
    def creates_with_interspersed_flags(self) -> tuple[int, int, int]:
        return (42, 42, 42)


def test_create_null():
    analysis = CreateTesting(parameters=None)
    analysis.create_null()
    assert "create_null" in analysis.completed_steps
    try:
        analysis.results.create_null
        assert False
    except AttributeError:
        pass


def test_create_as_str():
    analysis = CreateTesting(parameters=None)
    analysis.creates_as_str()
    assert analysis.results.creates_as_str == 42


def test_create_as_list_singular():
    analysis = CreateTesting(parameters=None)
    analysis.creates_as_list_singular()
    assert analysis.results.creates_as_list_singular == 42


def test_create_as_list_multiple():
    analysis = CreateTesting(parameters=None)
    analysis.creates_as_list_multiple()
    assert analysis.results.creates_as_list_multiple_a == 42
    assert analysis.results.creates_as_list_multiple_b == 42


def test_create_return_type_singular():
    analysis = CreateTesting(parameters=None)
    analysis.creates_return_type_singular()
    assert analysis.results.creates_return_type_singular == 42


def test_create_return_type_unnamed_tuple():
    analysis = CreateTesting(parameters=None)
    analysis.creates_return_type_unnamed_tuple()
    assert analysis.results.tuple_a == 42
    assert analysis.results.tuple_b == 42


def test_create_return_type_expected_tuple():
    analysis = CreateTesting()
    analysis.creates_return_type_expected_tuple()
    assert analysis.results.expected_tuple == (42, 42)


def test_create_return_type_datastruct():
    analysis = CreateTesting()
    analysis.creates_return_type_datastruct()
    assert analysis.results.inferred_key == 42


def test_create_return_singular_dict():
    analysis = CreateTesting()
    analysis.creates_return_singular_dict()
    assert analysis.results.results_dict == {"a": 42, "b": 42}


def test_create_return_superset_dict():
    analysis = CreateTesting()
    try:
        analysis.creates_return_superset_dict()
        assert False
    except ValueError as exc:
        assert "superset of creates list" in str(exc)


def test_create_with_interspersed_flags():
    analysis = CreateTesting()
    analysis.creates_with_interspersed_flags()
    assert analysis.results.a == 42
    assert analysis.results.b == 42
    assert analysis.results.c == 42
