"""SNN phase detector wrapper: encoder -> LIF neurons -> decoder behind the PhaseDetector interface.

In: oversampled bits.  Out: signed phase error.
Params: neuron count, weights, QFormat or None (None = floating point).
Hardware counterpart: M1 SNN RTL.
"""
import numpy as np
from serdes_model.cdr.pd_base import PhaseDetector
from serdes_model.fixedpoint.qformat import QFormat


class SNNPD(PhaseDetector):
    def __init__(self, osr: int = 4, n_neurons: int = 4, qformat: QFormat | None = None, seed: int = 0):
        self.osr, self.n_neurons, self.qformat, self.seed = osr, n_neurons, qformat, seed

    def update(self, samples: np.ndarray) -> int:
        raise NotImplementedError
