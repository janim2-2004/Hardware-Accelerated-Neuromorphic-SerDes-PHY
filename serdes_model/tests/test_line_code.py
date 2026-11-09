import numpy as np
import pytest
from serdes_model.tx.line_code import LineEncoder
from serdes_model.rx.line_decode import LineDecoder

rng = np.random.default_rng(0)


def rand_bits(n):
    return rng.integers(0, 2, n, dtype=np.uint8)


# Encode -> decode gives the original bits back, for every scheme.
# Chunked, so state (scrambler history, 8b/10b running disparity) must carry across calls.
@pytest.mark.parametrize("code", ["none", "scrambler", "8b10b"])
def test_roundtrip_chunked(code):
    d = rand_bits(8 * 1000)
    enc, dec = LineEncoder(code), LineDecoder(code)
    out = np.concatenate([dec.decode(enc.encode(c)) for c in np.split(d, 4)])
    assert np.array_equal(out, d)


# Every byte value and both starting running disparities round-trip, at the 10/8 rate.
@pytest.mark.parametrize("start_rd", [-1, +1])
def test_8b10b_roundtrip_all_bytes(start_rd):
    data = np.tile(np.arange(256), 2)
    bits = ((data[:, None] >> np.arange(8)) & 1).astype(np.uint8).ravel()
    enc = LineEncoder("8b10b")
    enc._rd = start_rd
    line = enc.encode(bits)
    assert len(line) == len(bits) * 10 // 8
    assert np.array_equal(LineDecoder("8b10b").decode(line), bits)
