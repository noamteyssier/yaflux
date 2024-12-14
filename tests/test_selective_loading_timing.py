import os
import time

import yaflux as yf

OUTPUT_PATH = "large_tmp.yax"


class MyAnalysis(yf.Base):
    """"""

    @yf.step(creates="large_obj")
    def build_very_large_object(self) -> list[int]:
        return [i for i in range(10**5)]

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
    run_and_save_analysis(OUTPUT_PATH)

    try:
        elapsed_no_select = time_load(OUTPUT_PATH)
        elapsed_with_select = time_load(OUTPUT_PATH, select="sum")
        assert elapsed_with_select < elapsed_no_select

    finally:
        delete_file(OUTPUT_PATH)


def test_time_exclusive_time_diff():
    run_and_save_analysis(OUTPUT_PATH)

    try:
        elapsed_no_select = time_load(OUTPUT_PATH)
        elapsed_with_select = time_load(OUTPUT_PATH, exclude="large_obj")
        assert elapsed_with_select < elapsed_no_select

    finally:
        delete_file(OUTPUT_PATH)


def test_time_no_results_time_diff():
    run_and_save_analysis(OUTPUT_PATH)

    try:
        elapsed_no_select = time_load(OUTPUT_PATH)
        elapsed_with_select = time_load(OUTPUT_PATH, no_results=True)
        assert elapsed_with_select < elapsed_no_select

    finally:
        delete_file(OUTPUT_PATH)
