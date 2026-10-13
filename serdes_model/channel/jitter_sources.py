"""Injected timing error. Each source maps EdgeStream -> EdgeStream by shifting edge times.

Hardware counterpart: M4 jitter injector (second, detuned MMCM or phase modulation of the TX MMCM).
Units: amplitudes in UI unless stated; convert with cfg.ui_s.
"""
from serdes_model.common.signals import EdgeStream


class SinusoidalJitter:
    """Edge shift = amp_ui * ui * sin(2*pi*freq_hz*t + phase)."""
    def __init__(self, amp_ui: float, freq_hz: float, ui_s: float, phase: float = 0.0):
        self.amp_ui, self.freq_hz, self.ui_s, self.phase = amp_ui, freq_hz, ui_s, phase

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError


class RandomJitter:
    """Gaussian edge shift, sigma in UI. Needs a seeded Generator."""
    def __init__(self, sigma_ui: float, ui_s: float, seed: int = 0):
        self.sigma_ui, self.ui_s, self.seed = sigma_ui, ui_s, seed

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError


class FrequencyOffset:
    """Linear phase ramp: edge shift = ppm*1e-6 * t (models TX/RX clock mismatch)."""
    def __init__(self, ppm: float):
        self.ppm = ppm

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError


class DeterministicJitter:
    """Bounded pattern-dependent shift (e.g. duty-cycle distortion), peak in UI."""
    def __init__(self, peak_ui: float, ui_s: float):
        self.peak_ui, self.ui_s = peak_ui, ui_s

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError


class JitterChain:
    """Apply a list of jitter sources in order."""
    def __init__(self, sources):
        self.sources = list(sources)

    def apply(self, edges: EdgeStream) -> EdgeStream:
        for s in self.sources:
            edges = s.apply(edges)
        return edges
