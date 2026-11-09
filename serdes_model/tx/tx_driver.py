"""TX output non-idealities (finite rise time, TX-side jitter).

In: EdgeStream.  Out: EdgeStream.  Params: rise_time_s, tx_jitter_sigma_s.
Hardware counterpart: FPGA LVDS output buffer.

Rise time: with a linear ramp the 50% threshold is crossed half a rise time after the edge starts,
so in the edge-timestamp model it is a constant delay of rise_time_s / 2.
TX jitter: independent Gaussian shift per edge, sigma = jitter_sigma_s.
"""
import numpy as np
from serdes_model.common.rng import make_rng
from serdes_model.common.signals import EdgeStream

TX_JITTER_STREAM = 10      # distinct stream id: TX jitter independent of other random sources


class TxDriver:
    def __init__(self, rise_time_s: float = 0.0, jitter_sigma_s: float = 0.0, seed: int = 0):
        self.rise_time_s = rise_time_s
        self.jitter_sigma_s = jitter_sigma_s
        self.seed = seed
        self._rng = make_rng(seed, TX_JITTER_STREAM)   # created once: chunks get fresh noise, runs repeat

    # The serializer records only the times when the level changes
    # Its edges are `ideal` in the sense that they have no jitter

    # Each of the edge times are shifted by rise_time_s / 2 which adds latency to the model
    # Random jitter is also added to each of the edge switches
    def apply(self, edges: EdgeStream) -> EdgeStream:
        n = edges.n_edges
        if n == 0 or (self.rise_time_s == 0 and self.jitter_sigma_s == 0):
            return edges
        dt = np.full(n, self.rise_time_s / 2)
        if self.jitter_sigma_s > 0:
            dt += self._rng.normal(0.0, self.jitter_sigma_s, n)
        return edges.shifted(dt)    # re-sorts if large jitter makes edges cross; initial_level kept
