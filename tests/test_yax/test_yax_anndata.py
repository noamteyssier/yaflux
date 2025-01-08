import os

import anndata as ad
import numpy as np

import yaflux as yf
from yaflux._yax._serializer import SerializerRegistry
from yaflux._yax._serializer._formats import AnnDataSerializer

N_CELLS = 100
N_GENES = 500

OUTPUT = "test_yax_anndata.yax"


class Analysis(yf.Base):
    @yf.step(creates="adata")
    def create_anndata(self) -> ad.AnnData:
        return ad.AnnData(X=np.random.rand(N_CELLS, N_GENES))


def test_serde_with_anndata():
    analysis = Analysis()
    analysis.execute()

    # Save analysis
    analysis.save(OUTPUT, force=True)
    assert os.path.exists(OUTPUT)

    # Load analysis
    loaded = Analysis.load(OUTPUT)

    # Check loaded analysis
    assert isinstance(loaded, Analysis)
    assert isinstance(loaded.results.adata, ad.AnnData)
    assert loaded.results.adata.shape == (N_CELLS, N_GENES)

    # Clean up
    os.remove(OUTPUT)


def test_serde_without_anndata():
    """Test serialization fallback.

    This simulates a situation where yaflux[anndata] is not installed.
    """
    original_serializers = SerializerRegistry._serializers.copy()

    try:
        SerializerRegistry._serializers = [
            s
            for s in SerializerRegistry._serializers
            if not issubclass(s, AnnDataSerializer)
        ]

        analysis = Analysis()
        analysis.execute()

        # Save analysis
        analysis.save(OUTPUT, force=True)
        assert os.path.exists(OUTPUT)

        # Load analysis
        loaded = Analysis.load(OUTPUT)
        assert isinstance(loaded, Analysis)
        assert isinstance(loaded.results.adata, ad.AnnData)
        assert loaded.results.adata.shape == (N_CELLS, N_GENES)

    # Clean up
    finally:
        SerializerRegistry._serializers = original_serializers
        if os.path.exists(OUTPUT):
            os.remove(OUTPUT)
