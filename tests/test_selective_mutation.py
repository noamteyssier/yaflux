import yaflux as yf


class Analysis(yf.Base):
    @yf.step(creates="some")
    def some_step(self):
        return 42

    @yf.step(mutates="some", creates="_mutated")
    def mut_step(self):
        self.results.some = 1

    @yf.step(creates="final", requires=["_mutated", "some"])
    def final_step(self):
        return self.results.some + 10


def test_mutability():
    analysis = Analysis()
    analysis.execute()
