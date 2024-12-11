if __name__ == "__main__":
    import yaflux as yf

    class MyAnalysis(yf.Base):
        @yf.step(creates="a")
        def step_a(self):
            return 42

        @yf.step(creates=["b", "_b"], requires="a")
        def step_b(self):
            _ = self.results.a
            return 42

        @yf.step(creates="c", requires=["a", "b"])
        def step_c(self):
            _ = self.results.a
            _ = self.results.b
            return 42

        @yf.step(creates="d", requires=["c", "_b"])
        def step_d(self):
            _ = self.results.c
            return 42

    analysis = MyAnalysis()
    analysis.step_a()
    analysis.step_b()

    # Save the visualization to a file
    dot = analysis.visualize_dependencies()
    dot.render("dependencies", cleanup=True)
