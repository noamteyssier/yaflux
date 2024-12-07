from yaflux import BaseAnalysis, AnalysisStep

class RequireTesting(BaseAnalysis):
    @AnalysisStep(creates="dep_a")
    def dep_a(self) -> dict[str, int]:
        return {"dep_a": 42}

    @AnalysisStep(creates="dep_b")
    def dep_b(self) -> dict[str, int]:
        return {"dep_b": 42}

    @AnalysisStep(requires="dep_a")
    def requires_as_str(self):
        pass

    @AnalysisStep(requires=["dep_a"])
    def requires_as_list_singular(self):
        pass

    @AnalysisStep(requires=["dep_a", "dep_b"])
    def requires_as_list_multiple(self):
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