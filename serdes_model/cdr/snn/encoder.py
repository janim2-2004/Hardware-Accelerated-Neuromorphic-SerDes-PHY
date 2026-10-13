"""Converts oversampled edge/transition information into input spikes for the neuron array.

In: samples (length osr).  Out: spike vector (one entry per input line).
Params: encoding scheme (e.g. one input line per sample slot, spike on transition).
Hardware counterpart: spike encoder RTL.
"""
import numpy as np


class SpikeEncoder:
    def __init__(self, osr: int = 4):
        self.osr = osr

    def encode(self, samples: np.ndarray) -> np.ndarray:
        raise NotImplementedError
