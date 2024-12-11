import yaflux as yf


class RequireTesting(yf.Base):
    @yf.step(creates="dep_a")
    def dep_a(self) -> int:
        return 42

    @yf.step(creates="dep_b")
    def dep_b(self) -> int:
        return 42

    @yf.step(requires="dep_a")
    def requires_as_str(self):
        _ = self.results.dep_a
        pass

    @yf.step(requires=["dep_a"])
    def requires_as_list_singular(self):
        _ = self.results.dep_a
        pass

    @yf.step(requires=["dep_a", "dep_b"])
    def requires_as_list_multiple(self):
        _ = self.results.dep_a
        _ = self.results.dep_b
        pass


def test_requires_as_str():
    analysis = RequireTesting(parameters=None)
    analysis.dep_a()
    analysis.requires_as_str()
    assert "requires_as_str" in analysis.completed_steps


def test_requires_as_list_singular():
    analysis = RequireTesting(parameters=None)
    analysis.dep_a()
    analysis.requires_as_list_singular()
    assert "requires_as_list_singular" in analysis.completed_steps


def test_requires_as_list_multiple():
    analysis = RequireTesting(parameters=None)
    analysis.dep_a()
    analysis.dep_b()
    analysis.requires_as_list_multiple()
    assert "requires_as_list_multiple" in analysis.completed_steps
