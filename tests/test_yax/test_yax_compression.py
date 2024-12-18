import os
import time

import yaflux as yf

OUTPATH = "comp_test.yax"
OUTPATH_COMPRESSED = "comp_test.yax.gz"


class Analysis(yf.Base):
    @yf.step(creates="some")
    def build_large(self):
        return [i for i in range(5**6)]


def test_compression_write():
    analysis = Analysis()
    analysis.execute()

    start = time.time()
    analysis.save(OUTPATH, force=True)
    elapsed_uncomp = time.time() - start

    start = time.time()
    analysis.save(OUTPATH_COMPRESSED, force=True)
    elapsed_comp = time.time() - start

    # Both paths should exist
    assert os.path.exists(OUTPATH)
    assert os.path.exists(OUTPATH_COMPRESSED)

    # Uncompressed file should take less time to write since theres no overhead
    assert elapsed_uncomp < elapsed_comp

    # Validate file sizes
    assert os.path.getsize(OUTPATH_COMPRESSED) < os.path.getsize(OUTPATH)

    # Validate file contents
    loaded_uncomp = yf.load(OUTPATH)
    loaded_comp = yf.load(OUTPATH_COMPRESSED)

    # Should have same results
    assert loaded_uncomp.results.some == loaded_comp.results.some

    # Clean up
    os.remove(OUTPATH)
    os.remove(OUTPATH_COMPRESSED)


def test_extension_naming():
    analysis = Analysis()
    analysis.execute()

    analysis.save(OUTPATH, force=True, compress=True)
    assert os.path.exists(OUTPATH_COMPRESSED)
    os.remove(OUTPATH_COMPRESSED)

    analysis.save(OUTPATH_COMPRESSED, force=True, compress=True)
    assert os.path.exists(OUTPATH_COMPRESSED)
    os.remove(OUTPATH_COMPRESSED)

    analysis.save(OUTPATH, force=True, compress=False)
    assert os.path.exists(OUTPATH)
    os.remove(OUTPATH)

    analysis.save(OUTPATH_COMPRESSED, force=True, compress=False)
    assert os.path.exists(OUTPATH_COMPRESSED)
    os.remove(OUTPATH_COMPRESSED)
