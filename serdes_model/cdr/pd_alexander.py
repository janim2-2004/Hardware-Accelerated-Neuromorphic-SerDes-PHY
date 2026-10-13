"""Alexander (bang-bang) phase detector: the conventional baseline.

In: oversampled bits for the current and previous UI.  Out: early/late/hold as -1/+1/0.
Params: which of the osr samples are data vs. edge samples.
Hardware counterpart: M2 baseline detector RTL.
"""
import numpy as np
from serdes_model.cdr.pd_base import PhaseDetector


class AlexanderPD(PhaseDetector):
    def __init__(self, osr: int = 4):
        self.osr = osr

    def update(self, samples: np.ndarray) -> int:
        # TODO: compare previous data sample, edge sample, current data sample.
        # data differs from edge AND edge == next data -> sampling late; edge == previous data -> early.
        raise NotImplementedError
