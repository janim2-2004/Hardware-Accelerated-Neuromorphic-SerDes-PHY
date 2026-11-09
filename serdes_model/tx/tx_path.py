"""Whole TX chain from a LinkConfig: PRBS -> line code -> serializer -> TX driver.

Out: (data_bits, line_bits, EdgeStream). This is the TX half of sim/link.py.
Hardware counterpart: the TX datapath block diagram (Diagrams/Tx Datapath).
"""
from serdes_model.config import LinkConfig
from serdes_model.tx.prbs import PRBS
from serdes_model.tx.line_code import LineEncoder
from serdes_model.tx.serializer import serialize
from serdes_model.tx.tx_driver import TxDriver


def run_tx(cfg: LinkConfig, n_bits: int):
    """For 8b10b, n_bits must be a multiple of 8 and len(line_bits) = 10/8 * n_bits;
    the UI is one *line* bit."""
    data = PRBS(cfg.prbs_order, cfg.prbs_seed).next_bits(n_bits)
    line = LineEncoder(cfg.line_code).encode(data)
    edges = serialize(line, cfg.ui_s, tx_ppm=cfg.tx_ppm)
    drv = TxDriver(cfg.tx_rise_time_s, cfg.tx_jitter_sigma_ui * cfg.ui_s, seed=cfg.seed)
    return data, line, drv.apply(edges)
