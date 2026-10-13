"""Model of the MMCM dynamic-phase-shift DCO: quantized, rate-limited phase shifter.

In: step commands (+1/-1/0) with the time they are issued.  Out: accumulated phase offset (seconds).
Params: step_s (1/56 VCO period), handshake latency (PSDONE) in cycles, max step rate.
Key behaviour to capture: a new step cannot start until the previous one completes, so commands
issued during the handshake are dropped or queued (decide and document). This limits the trackable
frequency offset to about step_s / (handshake_cycles * ps_clk_period).
Hardware counterpart: MMCM PSEN/PSINCDEC/PSDONE controller (M4).
"""
from serdes_model.config import LinkConfig


class MMCMDCO:
    def __init__(self, cfg: LinkConfig, ps_clk_hz: float = 100e6):
        self.step_s = cfg.dco_step_s
        self.handshake_s = cfg.ps_handshake_cycles / ps_clk_hz
        self.phase_s = 0.0
        self._busy_until = 0.0

    def command(self, t: float, step: int) -> bool:
        """Issue a step at time t. Return True if accepted, False if the DCO was still busy."""
        raise NotImplementedError

    @property
    def max_tracking_ppm(self) -> float:
        """Upper bound on the frequency offset the loop can follow, in ppm."""
        return (self.step_s / self.handshake_s) * 1e6
