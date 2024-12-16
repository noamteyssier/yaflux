import yaflux as yf


class ComplexAnalysis(yf.Base):
    @yf.step(creates="res_a")
    def step_a(self) -> int:
        return 42

    @yf.step(creates="rootless_res")
    def rootless_step(self) -> int:
        return 42

    @yf.step(creates="res_b", requires="res_a")
    def step_b(self) -> int:
        return self.results.res_a * 2

    @yf.step(creates="res_c", requires="res_b")
    def step_c(self) -> int:
        return self.results.res_b * 2

    @yf.step(creates="res_d", requires="res_c")
    def step_d(self) -> list[int]:
        return [self.results.res_c * 2 for _ in range(10)]

    @yf.step(creates="_mut_d", requires=["res_d", "rootless_res"])
    def step_mut_d(self):
        self.results.res_d[0] = self.results.rootless_res

    @yf.step(creates="res_e", requires=["_mut_d", "res_d", "res_c", "res_b"])
    def step_e(self) -> int:
        return sum(self.results.res_d) * self.results.res_b + self.results.res_c


def test_complex_analysis():
    analysis = ComplexAnalysis()
    # analysis.visualize_dependencies().render("complex", cleanup=True)
    analysis.execute_all()
    assert isinstance(analysis.results.res_e, int)


def test_invalid_target_step():
    analysis = ComplexAnalysis()
    try:
        analysis.execute("res_b")
        assert False
    except yf.ExecutorMissingTargetStepError:
        assert True


def test_partial_execution():
    analysis = ComplexAnalysis()
    analysis.execute(target_step="step_b")

    # Check that only required steps were executied
    assert "step_a" in analysis.completed_steps
    assert "step_b" in analysis.completed_steps
    assert "step_c" not in analysis.completed_steps
    assert "step_d" not in analysis.completed_steps


def test_diamond_dependencies():
    """Test handling of diamond-shaped dependency patterns"""

    class DiamondAnalysis(yf.Base):
        @yf.step(creates="root")
        def root(self) -> int:
            return 1

        @yf.step(creates="left", requires="root")
        def left_path(self) -> int:
            return self.results.root * 2

        @yf.step(creates="right", requires="root")
        def right_path(self) -> int:
            return self.results.root * 3

        @yf.step(creates="merged", requires=["left", "right"])
        def merge(self) -> int:
            return self.results.left + self.results.right

    analysis = DiamondAnalysis()
    analysis.execute_all()
    assert analysis.results.merged == 5


def test_flag_only_dependencies():
    """Test execution with only flag dependencies"""

    class FlagAnalysis(yf.Base):
        @yf.step(creates="_flag_a")
        def set_flag(self) -> None:
            pass

        @yf.step(requires="_flag_a")
        def use_flag(self) -> None:
            pass

    analysis = FlagAnalysis()
    analysis.execute_all()
    assert "_flag_a" in dir(analysis.results)


def test_orphaned_steps():
    """Test handling of steps with no connections to main graph"""

    class OrphanedAnalysis(yf.Base):
        @yf.step(creates="main")
        def main_flow(self) -> int:
            return 1

        @yf.step(creates="orphaned")
        def orphaned_step(self) -> int:
            return 2

    analysis = OrphanedAnalysis()
    analysis.execute_all()

    # Both steps should execute despite no dependencies
    assert "main_flow" in analysis.completed_steps
    assert "orphaned_step" in analysis.completed_steps


def test_empty_analysis():
    """Test handling of analysis with no steps"""

    class EmptyAnalysis(yf.Base):
        pass

    analysis = EmptyAnalysis()
    try:
        analysis.execute_all()
        assert False
    except yf.ExecutorMissingStartError:
        assert True


def test_non_dag_analysis_missing_start():
    class MissingStart(yf.Base):
        @yf.step(creates="res_a", requires="res_b")
        def step_a(self) -> int:
            return self.results.res_b

        @yf.step(creates="res_b", requires="res_a")
        def step_b(self) -> int:
            return self.results.res_a

        @yf.step(creates="res_c", requires="res_a")
        def step_c(self) -> int:
            return self.results.res_a

    analysis = MissingStart()
    # analysis.visualize_dependencies().render("missing_start", cleanup=True)
    try:
        analysis.execute_all()
        assert False
    except yf.ExecutorMissingStartError:
        assert True


def test_non_dag_analysis_circular_downstream():
    class CircularDownstream(yf.Base):
        @yf.step(creates="res_a")
        def step_a(self) -> int:
            return 42

        @yf.step(creates="res_b", requires="res_a")
        def step_b(self) -> int:
            _ = self.results.res_a
            return 42

        @yf.step(creates="res_c", requires=["res_d", "res_b"])
        def step_c(self) -> int:
            _ = self.results.res_d
            _ = self.results.res_b
            return 42

        @yf.step(creates="res_d", requires="res_c")
        def step_d(self) -> int:
            _ = self.results.res_c
            return 42

    analysis = CircularDownstream()
    # analysis.visualize_dependencies().render("circular", cleanup=True)
    try:
        analysis.execute_all()
        assert False
    except yf.ExecutorCircularDependencyError:
        assert True
