"""Converts output spikes into a signed phase error.

In: spike counts from the early/late neuron groups over a window.  Out: signed error.
Params: window length, gain.
Hardware counterpart: decoder RTL.
"""
import numpy as np


class PhaseDecoder:
    def __init__(self, window: int = 1, gain: float = 1.0):
        self.window, self.gain = window, gain

    def decode(self, early_spikes: int, late_spikes: int) -> int:
        raise NotImplementedError
