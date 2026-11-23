"""LVDS receiver: input offset, hysteresis, finite bandwidth.

In: EdgeStream.  Out: EdgeStream.  Params: threshold_offset_s, hysteresis_s.
Hardware counterpart: IBUFDS.

Responsibility: model the receiver comparator's decision point, with both effects expressed as time
(voltage divided by the edge slew), consistent with the rest of the edge-timestamp model:
  threshold_offset_s  the threshold sits off-centre: rising edges trip late and falling edges early
                      by that amount (a duty-cycle distortion; negative values swap the directions).
  hysteresis_s        total hysteresis band as time: the input must travel half the band further
                      before the output flips, so EVERY edge is late by hysteresis_s / 2.
Finite bandwidth is not modelled here; use channel.ISIChannel for that.
"""
import numpy as np

from serdes_model.common.signals import EdgeStream


class LVDSFrontEnd:
    def __init__(self, threshold_offset_s: float = 0.0, hysteresis_s: float = 0.0):
        self.threshold_offset_s = threshold_offset_s
        self.hysteresis_s = hysteresis_s

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        sign = 2.0 * edges.levels_after_edges() - 1.0                # +1 rising, -1 falling
        dt = sign * self.threshold_offset_s + self.hysteresis_s / 2.0
        return edges.shifted(dt)
