import os

from _hidden import write_hidden_analysis

import yaflux as yf


class SimpleAnalysis(yf.Base):
    """Simple analysis class for testing portability."""

    @yf.step(creates="res_a")
    def step_a(self) -> int:
        return 42

    @yf.step(creates="res_b", requires="res_a")
    def step_b(self) -> int:
        return self.results.res_a * 2


def test_load_portable():
    """Test saving and loading in explicit portable format."""
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Load as portable
        portable = yf.load_analysis(yf.Portable, filepath)

        # Verify results maintained
        assert portable.results.res_a == 42
        assert portable.results.res_b == 84
        assert set(portable.completed_steps) == {"step_a", "step_b"}

        # Check type
        assert isinstance(portable, yf.Portable)

    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_portable_shortform():
    """Test saving and loading in explicit portable format."""
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Load as portable
        portable = yf.load_portable(filepath)

        # Verify results maintained
        assert portable.results.res_a == 42
        assert portable.results.res_b == 84
        assert set(portable.completed_steps) == {"step_a", "step_b"}

        # Check type
        assert isinstance(portable, yf.Portable)

    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_portable_explit():
    """Test saving and loading in explicit portable format."""
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Load as portable
        portable = yf.Portable.load(filepath)

        # Verify results maintained
        assert portable.results.res_a == 42
        assert portable.results.res_b == 84
        assert set(portable.completed_steps) == {"step_a", "step_b"}

        # Check type
        assert isinstance(portable, yf.Portable)

    finally:
        # Cleanup
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_with_class():
    """Test loading with original class available."""
    analysis = SimpleAnalysis(parameters={"x": 1})
    analysis.step_a()

    filepath = "test_analysis.yax"
    analysis.save(filepath)

    try:
        # Load with original class
        loaded = yf.load_analysis(SimpleAnalysis, filepath)

        # Should be original type
        assert isinstance(loaded, SimpleAnalysis)

        # Should be able to continue analysis
        loaded.step_b()
        assert loaded.results.res_b == 84

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_without_class():
    """Test loading falls back to portable when class not available."""
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    class SomeClass:
        pass

    try:
        # Mock loading without class by passing Base
        loaded = yf.load_analysis(SomeClass, filepath)

        # Should fall back to portable
        assert loaded.results.res_a == 42

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_without_class_no_results():
    """Test loading falls back to portable when class not available.

    Also validate that selection options work
    """
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Mock loading without class by passing Base
        loaded = yf.load_portable(filepath, no_results=True)

        # Should fall back to portable
        assert isinstance(loaded, yf.Portable)
        assert not hasattr(loaded.results, "res_a")  # missing results
        assert not hasattr(loaded.results, "res_b")  # missing results
        assert set(loaded.completed_steps) == {"step_a", "step_b"}

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_without_class_select_results_str():
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Mock loading without class by passing Base
        loaded = yf.load_portable(filepath, select="res_a")

        # Should fall back to portable
        assert isinstance(loaded, yf.Portable)
        assert hasattr(loaded.results, "res_a")
        assert not hasattr(loaded.results, "res_b")  # missing results
        assert set(loaded.completed_steps) == {"step_a", "step_b"}

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_without_class_select_results_list():
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Mock loading without class by passing Base
        loaded = yf.load_portable(filepath, select=["res_a"])

        # Should fall back to portable
        assert isinstance(loaded, yf.Portable)
        assert hasattr(loaded.results, "res_a")
        assert not hasattr(loaded.results, "res_b")  # missing results
        assert set(loaded.completed_steps) == {"step_a", "step_b"}

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_without_class_exclude_results_str():
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Mock loading without class by passing Base
        loaded = yf.load_portable(filepath, exclude="res_a")

        # Should fall back to portable
        assert isinstance(loaded, yf.Portable)
        assert not hasattr(loaded.results, "res_a")
        assert hasattr(loaded.results, "res_b")
        assert set(loaded.completed_steps) == {"step_a", "step_b"}

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


def test_load_analysis_without_class_exclude_results_list():
    filepath = "test_analysis.yax"
    write_hidden_analysis(filepath)

    try:
        # Mock loading without class by passing Base
        loaded = yf.load_portable(filepath, exclude=["res_a"])

        # Should fall back to portable
        assert isinstance(loaded, yf.Portable)
        assert not hasattr(loaded.results, "res_a")
        assert hasattr(loaded.results, "res_b")
        assert set(loaded.completed_steps) == {"step_a", "step_b"}

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
