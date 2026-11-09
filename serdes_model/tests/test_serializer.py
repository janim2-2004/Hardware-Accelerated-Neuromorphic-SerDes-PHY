import numpy as np
from serdes_model.tx.prbs import PRBS
from serdes_model.tx.serializer import serialize

UI = 40e-9


# The key test: this is exactly how an ideal receiver reads the line.
# Sample the 
def test_mid_bit_sampling_recovers_bits():
    bits = PRBS(7).next_bits(1000)
    e = serialize(bits, UI)
    assert np.array_equal(e.level_at((np.arange(1000) + 0.5) * UI), bits)


def test_edges_on_grid_and_count():
    bits = PRBS(7).next_bits(1000)
    e = serialize(bits, UI, t0=1e-6)
    assert e.n_edges == np.count_nonzero(bits[1:] != bits[:-1])
    k = (e.edge_times - 1e-6) / UI
    assert np.allclose(k, np.round(k))             # every edge on a UI boundary
