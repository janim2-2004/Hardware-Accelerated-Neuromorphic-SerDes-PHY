"""The swappable phase-detector slot (interface I1 -> I2).

Every detector (Alexander baseline, SNN) subclasses this, so cdr_loop never needs to know which is in use.
Hardware counterpart: the M1/M2 detector module boundary.
"""
from abc import ABC, abstractmethod
import numpy as np


class PhaseDetector(ABC):
    @abstractmethod
    def update(self, samples: np.ndarray) -> int:
        """samples: one UI of oversampled bits (length = osr, uint8 0/1) plus any history the
        detector keeps internally. Return a signed phase error: negative = sampling early,
        positive = sampling late, 0 = no information (no transition) or aligned."""

    def reset(self) -> None:
        """Clear internal state (neuron membranes, previous-sample registers)."""
