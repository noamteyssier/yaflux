import os

import pandas as pd

import yaflux as yf
from yaflux._yax._serializer import SerializerRegistry
from yaflux._yax._serializer._formats import PandasSerializer

N = 1000
M = 100

OUTPUT = "test_yax_pandas.yax"


class Analysis(yf.Base):
    @yf.step(creates="df")
    def create_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({f"col_{i}": list(range(N)) for i in range(M)})


def test_serde_with_pandas():
    analysis = Analysis()
    analysis.execute()

    # Save the analysis
    analysis.save(OUTPUT)
    assert os.path.exists(OUTPUT)

    # Load the analysis
    loaded = Analysis.load(OUTPUT)

    # Check that the loaded analysis is the same as the original
    assert loaded.results.df.equals(analysis.results.df)

    # Clean up
    os.remove(OUTPUT)


def test_serde_without_pandas():
    original_serializers = SerializerRegistry._serializers.copy()

    try:
        SerializerRegistry._serializers = [
            s
            for s in SerializerRegistry._serializers
            if not issubclass(s, PandasSerializer)
        ]

        analysis = Analysis()
        analysis.execute()

        # Save analysis
        analysis.save(OUTPUT, force=True)
        assert os.path.exists(OUTPUT)

        # Load analysis
        loaded = Analysis.load(OUTPUT)
        assert loaded.results.df.equals(analysis.results.df)

    # Clean up
    finally:
        SerializerRegistry._serializers = original_serializers
        if os.path.exists(OUTPUT):
            os.remove(OUTPUT)
