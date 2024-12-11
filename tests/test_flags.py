import yaflux as yf


class Analysis(yf.Base):
    @yf.step(creates="a")
    def setup(self):
        return [1, 2, 3]

    @yf.step(creates="_mut_a", requires="a")
    def inplace_mut(self):
        self.results.a[0] = 42

    @yf.step(creates="b", requires=["a", "_mut_a"])
    def use_mut(self):
        return self.results.a

    @yf.step(creates="_mut_a")
    def redundant_flag_setup(self):
        return [1, 2, 3]


def test_flag_usage():
    analysis = Analysis()
    analysis.setup()
    analysis.inplace_mut()
    analysis.use_mut()

    assert analysis.results.a == [42, 2, 3]


def test_flag_usage_out_of_order():
    analysis = Analysis()
    analysis.setup()
    try:
        analysis.use_mut()
        assert False
    except ValueError as e:
        assert "_mut_a" in str(e)


def test_flag_redundant_set():
    analysis = Analysis()
    analysis.setup()
    analysis.inplace_mut()
    try:
        analysis.redundant_flag_setup()
    except yf.FlagError as e:
        assert "_mut_a" in str(e)
