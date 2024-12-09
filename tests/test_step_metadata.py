import time

import yaflux as yf


class SomeAnalysis(yf.Base):

    @yf.step(creates="some_data")
    def step_a(self):
        time.sleep(1e-3)
        return 42

    @yf.step(creates=["some_other_data", "some_more_data"])
    def step_b(self):
        return {"some_other_data": 42, "some_more_data": 42}

    @yf.step(creates="extra_data", requires="some_data")
    def step_c(self):
        return 42

    @yf.step(creates="something_else")
    def step_d(self, some_arg: str):
        return 42

def test_metadata_single():
    analysis = SomeAnalysis(parameters=None)
    analysis.step_a()
    metadata = analysis.get_step_metadata("step_a")

    assert metadata.creates == ["some_data"]
    assert metadata.requires == []
    assert metadata.timestamp > 0
    assert metadata.elapsed > 0
    assert metadata.args == []
    assert metadata.kwargs == {}

def test_metadata_multiple():
    analysis = SomeAnalysis(parameters=None)
    analysis.step_b()
    metadata = analysis.get_step_metadata("step_b")

    assert metadata.creates == ["some_other_data", "some_more_data"]
    assert metadata.requires == []
    assert metadata.args == []
    assert metadata.kwargs == {}

def test_metadata_requires():
    analysis = SomeAnalysis(parameters=None)
    analysis.step_a()
    analysis.step_c()
    metadata = analysis.get_step_metadata("step_c")

    assert metadata.creates == ["extra_data"]
    assert metadata.requires == ["some_data"]
    assert metadata.args == []
    assert metadata.kwargs == {}

def test_metadata_args():
    analysis = SomeAnalysis(parameters=None)
    analysis.step_d("hello")
    metadata = analysis.get_step_metadata("step_d")

    assert metadata.creates == ["something_else"]
    assert metadata.requires == []
    assert metadata.args == ["hello"]
    assert metadata.kwargs == {}

def test_metadata_kwargs():
    analysis = SomeAnalysis(parameters=None)
    analysis.step_d(some_arg="hello")
    metadata = analysis.get_step_metadata("step_d")

    assert metadata.creates == ["something_else"]
    assert metadata.requires == []
    assert metadata.args == []
    assert metadata.kwargs == {
        "some_arg": "hello"
    }

def test_step_children():
    analysis = SomeAnalysis(parameters=None)
    analysis.step_b()
    children = analysis.get_step_results("step_b")

    assert children == {
    "some_other_data": 42,
    "some_more_data": 42
    }
