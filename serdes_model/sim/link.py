"""Wires the full chain together from a LinkConfig.

prbs -> (line_code) -> serializer -> tx_driver -> jitter/ISI/noise -> frontend -> CDR/sampler -> deserializer -> BER.
Out: dict with rx_bits, ber, traces. This is the single entry point used by sweeps and tests.
Hardware counterpart: the whole single-board loopback test setup.

Currently implemented:
  PRBS -> serializer -> channel (TX driver, SJ, RJ, DJ, ppm offset, ISI, noise, RX front end)
       -> free-running sampler -> deserializer -> BER checker.
Optional line coding and the CDR loop are added in later steps.
"""
import numpy as np

from serdes_model.analysis.ber import measure_ber
from serdes_model.channel.chain import build_channel
from serdes_model.config import LinkConfig
from serdes_model.rx.deserializer import Deserializer
from serdes_model.rx.sampler import Sampler
from serdes_model.tx.prbs import PRBS
from serdes_model.tx.serializer import serialize


def run_link(cfg: LinkConfig, detector=None, n_bits: int = 100_000) -> dict:
    """detector=None -> free-running (no CDR) receiver; otherwise a PhaseDetector for the CDR loop.

    Returns a dict with:
      tx_bits, rx_bits      transmitted / recovered bits (uint8)
      words                 rx_bits grouped into cfg.word_bits-wide words, shape (n_words, word_bits)
      errors, bits_compared, ber   from the self-synchronizing PRBS checker (what the RTL checker would report)
      direct_errors, ber_direct    bit-for-bit mismatches against tx_bits (exact; no seed fragility, so use it
                                   for sweeps while the receiver is free-running and bits stay aligned)
      rx_edges              the EdgeStream the receiver saw (after every impairment)
      traces                dict of per-sample arrays (currently the sample times)
    """
    # --- The CDR is a later build step: fail loudly instead of silently ignoring the detector. ---
    if detector is not None:
        raise NotImplementedError("CDR loop is a later build step; use detector=None for the free-running RX")

    ui = cfg.ui_s

    # 1. TX: PRBS bits -> ideal edge timestamps (no clock error here: ppm offset is a channel block).
    tx_bits = PRBS(cfg.prbs_order).next_bits(n_bits)
    tx_edges = serialize(tx_bits, ui)

    # 2. Channel: every enabled impairment shifts / removes edges. Empty chain = ideal wire.
    rx_edges = build_channel(cfg).apply(tx_edges)

    # 3. RX sampling grid: cfg.osr samples per UI on the nominal clock. With no CDR there is no phase
    #    correction, so we keep the sample in the middle of each UI (slot osr//2), the farthest from edges.
    sample_period = ui / cfg.osr
    sample_times = (np.arange(n_bits) * cfg.osr + cfg.osr // 2) * sample_period

    # 4. Capture the line at those times (aperture 0 here: no metastability in the free-running chain).
    rx_bits = Sampler(aperture_s=0.0, seed=cfg.seed).sample(rx_edges, sample_times).bits

    # 5. Deserialize to words and run the PRBS checker on the recovered bit stream.
    words = Deserializer(cfg.word_bits).deserialize(rx_bits)
    errors, compared, ber = measure_ber(rx_bits, cfg.prbs_order)
    direct_errors = int(np.count_nonzero(tx_bits != rx_bits))

    return {
        "tx_bits": tx_bits,
        "rx_bits": rx_bits,
        "words": words,
        "errors": errors,
        "bits_compared": compared,
        "ber": ber,
        "direct_errors": direct_errors,
        "ber_direct": direct_errors / n_bits,
        "rx_edges": rx_edges,
        "traces": {"sample_times": sample_times},
    }
