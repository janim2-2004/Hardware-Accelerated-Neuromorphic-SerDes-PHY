"""Voltage noise on the line, converted to timing error at the receiver threshold.

In: EdgeStream.  Out: EdgeStream.  Params: noise_sigma_v, slew_v_per_s (dt = noise / slew).
Hardware counterpart: board and supply noise.
"""
from serdes_model.common.signals import EdgeStream


class ThresholdNoise:
    def __init__(self, noise_sigma_v: float, slew_v_per_s: float, seed: int = 0):
        self.noise_sigma_v, self.slew_v_per_s, self.seed = noise_sigma_v, slew_v_per_s, seed

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError
