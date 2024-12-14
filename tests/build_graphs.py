if __name__ == "__main__":
    import yaflux as yf

    class MyAnalysis(yf.Base):
        @yf.step(creates=["x", "y", "z"])
        def load_data(self) -> tuple[int, int, int]:
            return 1, 2, 3

        @yf.step(creates="proc_x", requires="x")
        def process_x(self) -> int:
            return self.results.x + 1

        @yf.step(creates=["proc_y1", "proc_y2", "_marked"], requires="y")
        def process_y(self) -> tuple[int, int]:
            return (
                self.results.y + 1,
                self.results.y + 2,
            )

        @yf.step(creates="proc_z", requires=["proc_y1", "proc_y2", "z"])
        def process_z(self) -> int:
            return self.results.proc_y1 + self.results.proc_y2 + self.results.z

        @yf.step(creates="final", requires=["proc_x", "proc_z", "_marked"])
        def final(self) -> int:
            return self.results.proc_x + self.results.proc_z

    analysis = MyAnalysis()
    analysis.visualize_dependencies().render(
        "./docs/source/assets/complex_workflow_init", format="svg", cleanup=True
    )

    analysis.load_data()  # type: ignore
    analysis.process_x()
    analysis.process_y()

    analysis.visualize_dependencies().render(
        "./docs/source/assets/complex_workflow_progress", format="svg", cleanup=True
    )
