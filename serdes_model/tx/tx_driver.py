"""TX output non-idealities (finite rise time, TX-side jitter).

In: EdgeStream.  Out: EdgeStream.  Params: rise_time_s, tx_jitter_sigma_s.
Hardware counterpart: FPGA LVDS output buffer.

Responsibility: model the output buffer. A linear ramp of duration rise_time_s crosses 50% after
rise_time_s/2, so every edge gets that fixed delay (the same for all edges, so no pattern dependence).
The buffer also adds its own Gaussian jitter, drawn from the TX stream (independent of channel RJ).
"""
from serdes_model.common.rng import STREAM_TX, make_rng
from serdes_model.common.signals import EdgeStream


class TxDriver:
    def __init__(self, rise_time_s: float = 0.0, jitter_sigma_s: float = 0.0, seed: int = 0):
        self.rise_time_s = rise_time_s
        self.jitter_sigma_s = jitter_sigma_s
        self.seed = seed

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        dt = self.rise_time_s / 2.0                                  # fixed 50%-point delay
        if self.jitter_sigma_s > 0:
            rng = make_rng(self.seed, STREAM_TX)
            dt = dt + rng.normal(0.0, self.jitter_sigma_s, size=edges.n_edges)
        return edges.shifted(dt)
