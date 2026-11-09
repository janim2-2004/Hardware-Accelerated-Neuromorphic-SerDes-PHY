import numpy as np
from serdes_model.tx.prbs import PRBS
from serdes_model.tx.serializer import serialize
from serdes_model.tx.tx_driver import TxDriver

UI = 40e-9
bits = PRBS(15).next_bits(200_000)            # ~100k edges
e = serialize(bits, UI)


def test_rise_time_delay():
    out = TxDriver(rise_time_s=2e-9).apply(e)
    assert np.allclose(out.edge_times - e.edge_times, 1e-9)
    assert out.initial_level == e.initial_level


def test_jitter_stats():
    sigma = 0.02 * UI
    out = TxDriver(jitter_sigma_s=sigma, seed=1).apply(e)
    d = out.edge_times - e.edge_times          # fine: sigma << UI, so edges never reorder
    assert abs(d.mean()) < 0.05 * sigma
    assert abs(d.std() / sigma - 1) < 0.02
