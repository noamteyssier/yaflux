import yaflux as yf


class SimpleAnalysis(yf.Base):
    @yf.step(creates="base_data")
    def load_base_data(self) -> list[int]:
        return [1, 2, 3, 4, 5]


class MixinAnalysis(yf.Base):
    @yf.step(creates="mixin_data")
    def load_mixin_data(self) -> list[int]:
        return [10, 20, 30, 40, 50]


class CompositeAnalysis(SimpleAnalysis, MixinAnalysis):
    @yf.step(creates="final_data", requires=["base_data", "mixin_data"])
    def final_process(self) -> list[int]:
        return [x + y for x, y in zip(self.results.base_data, self.results.mixin_data)]


def test_mixin_composition():
    analysis = CompositeAnalysis()
    analysis.load_base_data()
    analysis.load_mixin_data()
    analysis.final_process()
    assert analysis.results.final_data == [11, 22, 33, 44, 55]
