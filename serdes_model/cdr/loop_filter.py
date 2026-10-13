"""Loop filter: smooths the phase-error stream into DCO commands.

In: signed error per UI.  Out: dco command in {-1, 0, +1} steps (or small int).
Params: kp, ki (proportional + integral), integrator width via QFormat.
Hardware counterpart: loop filter RTL (designed by M4, written by M2).
"""
from serdes_model.fixedpoint.qformat import QFormat


class LoopFilter:
    def __init__(self, kp: float = 1.0, ki: float = 0.0, qformat: QFormat | None = None):
        self.kp, self.ki, self.qformat = kp, ki, qformat
        self.integrator = 0.0

    def update(self, error: int) -> int:
        raise NotImplementedError

    def reset(self):
        self.integrator = 0.0
