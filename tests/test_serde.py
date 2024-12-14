import os

import yaflux as yf

OUTPUT_PATH = "serde_tmp.yax"


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
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)

    # Save and reload
    analysis.save(filepath=OUTPUT_PATH)
    reloaded = analysis.load(filepath=OUTPUT_PATH)

    # Delete the file
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)

    assert reloaded.results.res_a == 42
    assert reloaded.results.res_b == 42
    assert "step_a" in reloaded.completed_steps
    assert "step_b" in reloaded.completed_steps


def test_save_panic_on_found():
    analysis = SerdeTesting(parameters=None)

    # Ensure that the file exists
    if not os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "w") as f:
            f.write("")

    # Try saving
    try:
        analysis.save(filepath=OUTPUT_PATH)
        assert False
    except FileExistsError:
        pass

    # Delete the file
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)


def test_save_overwrite():
    analysis = SerdeTesting(parameters=None)

    # Ensure that the file exists
    if not os.path.exists(OUTPUT_PATH):
        with open(OUTPUT_PATH, "w") as f:
            f.write("")

    # Save and reload
    analysis.save(filepath=OUTPUT_PATH, force=True)

    # Delete the file
    if os.path.exists(OUTPUT_PATH):
        os.remove(OUTPUT_PATH)
