"""TX output non-idealities (finite rise time, TX-side jitter).

In: EdgeStream.  Out: EdgeStream.  Params: rise_time_s, tx_jitter_sigma_s.
Hardware counterpart: FPGA LVDS output buffer.
"""
from serdes_model.common.signals import EdgeStream


class TxDriver:
    def __init__(self, rise_time_s: float = 0.0, jitter_sigma_s: float = 0.0, seed: int = 0):
        self.rise_time_s = rise_time_s
        self.jitter_sigma_s = jitter_sigma_s
        self.seed = seed

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError
