"""Ideal-case end-to-end test: zero jitter, zero offset -> BER must be exactly 0.
Enable once serializer, sampler, deserializer, ber and sim.link are implemented."""
import pytest


@pytest.mark.skip(reason="enable after the ideal chain is implemented (build order step 1)")
def test_ideal_link_has_zero_ber():
    from serdes_model.config import LinkConfig
    from serdes_model.sim.link import run_link
    result = run_link(LinkConfig(), detector=None, n_bits=10_000)
    assert result["ber"] == 0.0
