"""Leaky integrate-and-fire neuron.

Dynamics per step: v <- leak*v + sum(w_i * x_i); if v >= threshold: spike, v <- reset.
Params: leak (0..1), threshold, reset, optional QFormat applied to v and weights.
Hardware counterpart: LIF neuron RTL unit. The step function must match the RTL cycle by cycle.
"""
import numpy as np
from serdes_model.fixedpoint.qformat import QFormat


class LIFNeuron:
    def __init__(self, leak: float, threshold: float, reset: float = 0.0, qformat: QFormat | None = None):
        self.leak, self.threshold, self.reset_value, self.qformat = leak, threshold, reset, qformat
        self.v = 0.0

    def step(self, weighted_input: float) -> int:
        """Advance one time step; return 1 if the neuron fires else 0."""
        raise NotImplementedError

    def reset_state(self):
        self.v = 0.0
