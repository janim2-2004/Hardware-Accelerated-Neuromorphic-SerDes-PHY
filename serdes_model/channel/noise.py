"""Voltage noise on the line, converted to timing error at the receiver threshold.

In: EdgeStream.  Out: EdgeStream.  Params: noise_sigma_v, slew_v_per_s (dt = noise / slew).
Hardware counterpart: board and supply noise.

Responsibility: a noisy threshold crossing happens early or late by (voltage error / slew rate).
Voltage noise therefore becomes Gaussian timing jitter with sigma_t = noise_sigma_v / slew_v_per_s,
so slow edges (small slew) turn the same noise into more jitter.
"""
from serdes_model.common.rng import STREAM_NOISE, make_rng
from serdes_model.common.signals import EdgeStream


class ThresholdNoise:
    def __init__(self, noise_sigma_v: float, slew_v_per_s: float, seed: int = 0):
        if slew_v_per_s <= 0:
            raise ValueError("slew_v_per_s must be positive")
        self.noise_sigma_v, self.slew_v_per_s, self.seed = noise_sigma_v, slew_v_per_s, seed

    @property
    def sigma_t_s(self) -> float:
        """Equivalent timing jitter (RMS seconds)."""
        return self.noise_sigma_v / self.slew_v_per_s

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        rng = make_rng(self.seed, STREAM_NOISE)
        return edges.shifted(rng.normal(0.0, self.sigma_t_s, size=edges.n_edges))
