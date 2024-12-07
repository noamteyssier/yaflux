import os
import yaflux as yf


class SerdeTesting(yf.Base):
    """This class tests serialization and deserialization."""

    @yf.step(creates="res_a")
    def step_a(self) -> int:
        return 42

    @yf.step(creates="res_b")
    def step_b(self) -> int:
        return 42


def test_serde():
    analysis = SerdeTesting(parameters=None)
    analysis.step_a()
    analysis.step_b()

    # Delete the file just in case it exists
    # We will test the overwrite condition later
    if os.path.exists("tmp.pkl"):
        os.remove("tmp.pkl")

    # Save and reload
    analysis.save(filepath="tmp.pkl")
    reloaded = analysis.load(filepath="tmp.pkl")

    # Delete the file
    if os.path.exists("tmp.pkl"):
        os.remove("tmp.pkl")

    assert reloaded.results.res_a == 42
    assert reloaded.results.res_b == 42
    assert "step_a" in reloaded.completed_steps
    assert "step_b" in reloaded.completed_steps


def test_save_panic_on_found():
    analysis = SerdeTesting(parameters=None)

    # Ensure that the file exists
    if not os.path.exists("tmp.pkl"):
        with open("tmp.pkl", "w") as f:
            f.write("")

    # Try saving
    try:
        analysis.save(filepath="tmp.pkl")
        assert False
    except FileExistsError:
        pass

    # Delete the file
    if os.path.exists("tmp.pkl"):
        os.remove("tmp.pkl")


def test_save_overwrite():
    analysis = SerdeTesting(parameters=None)

    # Ensure that the file exists
    if not os.path.exists("tmp.pkl"):
        with open("tmp.pkl", "w") as f:
            f.write("")

    # Save and reload
    analysis.save(filepath="tmp.pkl", force=True)

    # Delete the file
    if os.path.exists("tmp.pkl"):
        os.remove("tmp.pkl")
