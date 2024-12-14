import os
import time

import yaflux as yf


class MyAnalysis(yf.Base):
    """"""

    @yf.step(creates="large_obj")
    def build_very_large_object(self) -> list[int]:
        return [i for i in range(10**4)]

    @yf.step(creates="sum", requires="large_obj")
    def sum_large_object(self) -> int:
        return sum(self.results.large_obj)


def run_and_save_analysis(filepath: str):
    analysis = MyAnalysis()
    analysis.build_very_large_object()
    analysis.sum_large_object()
    analysis.save(filepath)


def delete_file(filepath: str):
    if os.path.exists(filepath):
        os.remove(filepath)


def time_load(filepath: str, **kwargs):
    start = time.time()
    _ = yf.load(filepath, **kwargs)
    elapsed = time.time() - start
    return elapsed


def test_time_selective_time_diff():
    filepath = "test_analysis.yax"
    run_and_save_analysis(filepath)

    try:
        elapsed_no_select = time_load(filepath)
        elapsed_with_select = time_load(filepath, select="sum")
        assert elapsed_with_select < elapsed_no_select

    finally:
        delete_file(filepath)
