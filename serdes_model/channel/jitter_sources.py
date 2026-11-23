"""Injected timing error. Each source maps EdgeStream -> EdgeStream by shifting edge times.

Hardware counterpart: M4 jitter injector (second, detuned MMCM or phase modulation of the TX MMCM).
Units: amplitudes in UI unless stated; convert with cfg.ui_s.

Responsibility: model the four classic jitter families. Every source computes a per-edge shift dt from
the ideal edge time (and polarity, for DJ) and applies it with EdgeStream.shifted(), which also deletes
pulses that jitter squeezed to zero width.
  SinusoidalJitter     periodic wobble (SJ)                  - what a CDR can track, up to a limit
  RandomJitter         Gaussian, unbounded (RJ)              - sets the BER floor
  DeterministicJitter  bounded, polarity-dependent (DCD)     - fixed eye closure
  FrequencyOffset      linear phase ramp (ppm)               - TX/RX clock mismatch
JitterChain applies a list of blocks in order.
"""
import numpy as np

from serdes_model.common.rng import STREAM_RJ, make_rng
from serdes_model.common.signals import EdgeStream


class SinusoidalJitter:
    """Edge shift = amp_ui * ui * sin(2*pi*freq_hz*t + phase), evaluated at each ideal edge time t."""
    def __init__(self, amp_ui: float, freq_hz: float, ui_s: float, phase: float = 0.0):
        self.amp_ui, self.freq_hz, self.ui_s, self.phase = amp_ui, freq_hz, ui_s, phase

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        dt = self.amp_ui * self.ui_s * np.sin(2 * np.pi * self.freq_hz * edges.edge_times + self.phase)
        return edges.shifted(dt)


class RandomJitter:
    """Gaussian edge shift, sigma in UI. Needs a seeded Generator."""
    def __init__(self, sigma_ui: float, ui_s: float, seed: int = 0):
        self.sigma_ui, self.ui_s, self.seed = sigma_ui, ui_s, seed

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        # Fresh generator per call: the same input always gives the same output (reproducible sweeps).
        rng = make_rng(self.seed, STREAM_RJ)
        dt = rng.normal(0.0, self.sigma_ui * self.ui_s, size=edges.n_edges)
        return edges.shifted(dt)


class FrequencyOffset:
    """Linear phase ramp: edge shift = ppm*1e-6 * t (models TX/RX clock mismatch).
    Positive ppm = TX slower than nominal, so edges arrive progressively later."""
    def __init__(self, ppm: float):
        self.ppm = ppm

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        return edges.shifted(self.ppm * 1e-6 * edges.edge_times)


class DeterministicJitter:
    """Bounded pattern-dependent shift (duty-cycle distortion), peak in UI.

    Rising edges move late by peak_ui and falling edges early by peak_ui, so every high pulse is
    2*peak_ui narrower (or wider, for negative peak). Bounded, and tied to the data (edge polarity).
    """
    def __init__(self, peak_ui: float, ui_s: float):
        self.peak_ui, self.ui_s = peak_ui, ui_s

    def apply(self, edges: EdgeStream) -> EdgeStream:
        if edges.n_edges == 0:
            return edges
        sign = 2.0 * edges.levels_after_edges() - 1.0           # +1 rising, -1 falling
        return edges.shifted(sign * self.peak_ui * self.ui_s)


class JitterChain:
    """Apply a list of jitter sources in order."""
    def __init__(self, sources):
        self.sources = list(sources)

    def apply(self, edges: EdgeStream) -> EdgeStream:
        for s in self.sources:
            edges = s.apply(edges)
        return edges
