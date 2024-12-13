# yaflux/tests/_utils.py
import subprocess


def write_hidden_analysis(filepath: str):
    """Write an analysis yax using a separate Python process.

    The code is written to a temporary file and executed in a separate process.
    """

    code = f"""
import yaflux as yf

class HiddenAnalysis(yf.Base):
    @yf.step(creates="res_a")
    def step_a(self) -> int:
        return 42

    @yf.step(creates="res_b", requires="res_a")
    def step_b(self) -> int:
        return self.results.res_a * 2

analysis = HiddenAnalysis(parameters=None)
analysis.step_a()
analysis.step_b()
analysis.save("{filepath}", force=True)
"""

    # Write to temporary file
    with open("_temp_save.py", "w") as f:
        f.write(code)

    # Run in separate process
    subprocess.run(["python", "_temp_save.py"], check=True)

    # Cleanup
    import os

    os.remove("_temp_save.py")
