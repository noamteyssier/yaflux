import os

import numpy as np

import yaflux as yf
from yaflux._yax._serializer import SerializerRegistry
from yaflux._yax._serializer._formats import NumpySerializer

N = 1000
M = 100

OUTPUT = "test_yax_numpy.yax"


class Analysis(yf.Base):
    @yf.step(creates="matrix")
    def create_matrix(self) -> np.ndarray:
        return np.random.rand(N, M)


def test_serde_with_numpy():
    analysis = Analysis()
    analysis.execute()

    # Save the analysis
    analysis.save(OUTPUT, force=True)
    assert os.path.exists(OUTPUT)

    # Load the analysis
    loaded = Analysis.load(OUTPUT)

    # Check that the results are the same
    assert np.all(loaded.results.matrix == analysis.results.matrix)

    # Clean up
    os.remove(OUTPUT)


def test_serde_without_numpy():
    """Test serialization fallback.

    This simulates a situation where yaflux[anndata] is not installed.
    """
    original_serializers = SerializerRegistry._serializers.copy()

    try:
        SerializerRegistry._serializers = [
            s
            for s in SerializerRegistry._serializers
            if not issubclass(s, NumpySerializer)
        ]

        analysis = Analysis()
        analysis.execute()

        # Save analysis
        analysis.save(OUTPUT, force=True)
        assert os.path.exists(OUTPUT)

        # Load analysis
        loaded = Analysis.load(OUTPUT)
        assert np.all(loaded.results.matrix == analysis.results.matrix)

    # Clean up
    finally:
        SerializerRegistry._serializers = original_serializers
        if os.path.exists(OUTPUT):
            os.remove(OUTPUT)
