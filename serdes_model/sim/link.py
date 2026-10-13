"""Wires the full chain together from a LinkConfig.

prbs -> (line_code) -> serializer -> tx_driver -> jitter/ISI/noise -> frontend -> CDR/sampler -> deserializer -> BER.
Out: dict with rx_bits, ber, traces. This is the single entry point used by sweeps and tests.
Hardware counterpart: the whole single-board loopback test setup.
"""
from serdes_model.config import LinkConfig


def run_link(cfg: LinkConfig, detector=None, n_bits: int = 100_000) -> dict:
    """detector=None -> free-running (no CDR) receiver; otherwise a PhaseDetector for the CDR loop."""
    raise NotImplementedError
