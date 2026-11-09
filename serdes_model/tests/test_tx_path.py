import numpy as np
import pytest
from serdes_model.config import LinkConfig
from serdes_model.tx.tx_path import run_tx
from serdes_model.rx.sampler import Sampler
from serdes_model.rx.line_decode import LineDecoder


def recover(cfg, n):
    data, line, edges = run_tx(cfg, n)
    t = (np.arange(len(line)) + 0.5) * cfg.ui_s + cfg.tx_rise_time_s / 2   # ideal mid-UI clock
    rx = Sampler().sample(edges, t).bits          # aperture 0: Sampler(aperture>0) has an RNG bug
    return data, LineDecoder(cfg.line_code).decode(rx)


@pytest.mark.parametrize("code", ["none", "scrambler", "8b10b"])
def test_ideal_tx_ber_zero(code):
    data, out = recover(LinkConfig(line_code=code), 8000)
    assert np.array_equal(out, data)


def test_ber_zero_with_rise_time_and_small_jitter():
    data, out = recover(LinkConfig(tx_rise_time_s=2e-9, tx_jitter_sigma_ui=0.02), 8000)
    assert np.array_equal(out, data)
