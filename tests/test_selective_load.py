import os

import yaflux as yf

TMP_PATH = "test_tmp.yax"


class MyAnalysis(yf.Base):
    @yf.step(creates="base_data")
    def load_base_data(self) -> list[int]:
        return [1, 2, 3, 4, 5]

    @yf.step(creates="mixin_data")
    def load_mixin_data(self) -> list[int]:
        return [10, 20, 30, 40, 50]

    @yf.step(creates="final_data", requires=["base_data", "mixin_data"])
    def final_process(self) -> list[int]:
        return [x + y for x, y in zip(self.results.base_data, self.results.mixin_data)]


def run_and_save(path: str):
    analysis = MyAnalysis()
    analysis.load_base_data()
    analysis.load_mixin_data()
    analysis.final_process()
    analysis.save(path, force=True)


def delete_tmp(path):
    if os.path.exists(path):
        os.remove(path)


def test_full_loading():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH)
    assert analysis.results.base_data == [1, 2, 3, 4, 5]
    assert analysis.results.mixin_data == [10, 20, 30, 40, 50]
    assert analysis.results.final_data == [11, 22, 33, 44, 55]
    delete_tmp(TMP_PATH)


def test_select_loading_no_results():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, select=[])
    assert not hasattr(analysis.results, "base_data")
    assert not hasattr(analysis.results, "mixin_data")
    assert not hasattr(analysis.results, "final_data")
    delete_tmp(TMP_PATH)


def test_selective_loading_select_as_str():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, select="mixin_data")
    assert not hasattr(analysis.results, "base_data")
    assert analysis.results.mixin_data == [10, 20, 30, 40, 50]
    assert not hasattr(analysis.results, "final_data")
    delete_tmp(TMP_PATH)


def test_selective_loading_select_as_list():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, select=["mixin_data"])
    assert not hasattr(analysis.results, "base_data")
    assert analysis.results.mixin_data == [10, 20, 30, 40, 50]
    assert not hasattr(analysis.results, "final_data")
    delete_tmp(TMP_PATH)


def test_selective_loading_select_multiple():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, select=["mixin_data", "base_data"])
    assert analysis.results.base_data == [1, 2, 3, 4, 5]
    assert analysis.results.mixin_data == [10, 20, 30, 40, 50]
    assert not hasattr(analysis.results, "final_data")
    delete_tmp(TMP_PATH)


def test_selective_loading_select_non_existent():
    run_and_save(TMP_PATH)
    try:
        MyAnalysis.load(TMP_PATH, select="non_existent")
        assert False
    except yf.YaxMissingResultError:
        assert True
    delete_tmp(TMP_PATH)


def test_selective_loading_select_non_existent_list():
    run_and_save(TMP_PATH)
    try:
        MyAnalysis.load(TMP_PATH, select=["non_existent"])
        assert False
    except yf.YaxMissingResultError:
        assert True
    delete_tmp(TMP_PATH)


def test_selective_loading_exclude_as_str():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, exclude="mixin_data")
    assert analysis.results.base_data == [1, 2, 3, 4, 5]
    assert not hasattr(analysis.results, "mixin_data")
    assert analysis.results.final_data == [11, 22, 33, 44, 55]
    delete_tmp(TMP_PATH)


def test_selective_loading_exclude_as_list():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, exclude=["mixin_data"])
    assert analysis.results.base_data == [1, 2, 3, 4, 5]
    assert not hasattr(analysis.results, "mixin_data")
    assert analysis.results.final_data == [11, 22, 33, 44, 55]
    delete_tmp(TMP_PATH)


def test_selective_loading_exclude_multiple():
    run_and_save(TMP_PATH)
    analysis = MyAnalysis.load(TMP_PATH, exclude=["mixin_data", "base_data"])
    assert not hasattr(analysis.results, "base_data")
    assert not hasattr(analysis.results, "mixin_data")
    assert analysis.results.final_data == [11, 22, 33, 44, 55]
    delete_tmp(TMP_PATH)


def test_selective_loading_exclude_non_existent():
    run_and_save(TMP_PATH)
    MyAnalysis.load(TMP_PATH, exclude="non_existent")  # Should not raise
    delete_tmp(TMP_PATH)


def test_selective_loading_exclude_non_existent_list():
    run_and_save(TMP_PATH)
    MyAnalysis.load(TMP_PATH, exclude=["non_existent"])  # Should not raise
    delete_tmp(TMP_PATH)


# path = "tmp/tmp.yax"
# run_and_save(path)
# analysis = MyAnalysis.load(path, select="mixin_data")
# dot = analysis.visualize_dependencies().render("simple", cleanup=True)
