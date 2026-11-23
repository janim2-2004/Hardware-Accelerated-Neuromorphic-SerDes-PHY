"""Ideal-case end-to-end test: zero jitter, zero offset -> BER must be exactly 0.
Covers serializer, sampler, deserializer, ber and sim.link working together."""
import numpy as np
from serdes_model.config import LinkConfig
from serdes_model.sim.link import run_link


def test_ideal_link_has_zero_ber():
    result = run_link(LinkConfig(), detector=None, n_bits=10_000)
    assert result["ber"] == 0.0
    assert result["errors"] == 0
    assert result["direct_errors"] == 0          # recovered bits equal transmitted bits exactly
    assert result["words"].shape == (10_000 // 8, 8)


def test_ideal_link_all_prbs_orders():
    for order in (7, 15, 23):
        r = run_link(LinkConfig(prbs_order=order), n_bits=2_000)
        assert r["ber"] == 0.0 and r["direct_errors"] == 0


def test_ideal_link_other_osr():
    for osr in (2, 4, 8):
        r = run_link(LinkConfig(osr=osr), n_bits=2_000)
        assert r["direct_errors"] == 0


def test_large_frequency_offset_causes_errors():
    # Free-running RX with a big TX/RX mismatch must slip against the data (this is why a CDR is needed).
    r = run_link(LinkConfig(freq_offset_ppm=20_000.0), n_bits=2_000)
    assert r["ber"] > 0.0
