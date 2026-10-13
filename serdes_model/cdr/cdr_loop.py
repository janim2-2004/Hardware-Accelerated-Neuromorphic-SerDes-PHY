"""Closes the loop: samples -> detector -> loop filter -> DCO -> new sampling phase.

In: EdgeStream (received line), LinkConfig, a PhaseDetector instance.
Out: per-UI traces (phase error, DCO phase, lock flag) and recovered bits.
Hardware counterpart: the full CDR (M2 datapath + M1/M2 detector + M4 loop/DCO).
"""
from serdes_model.config import LinkConfig
from serdes_model.cdr.pd_base import PhaseDetector


class CDRLoop:
    def __init__(self, cfg: LinkConfig, detector: PhaseDetector):
        self.cfg, self.detector = cfg, detector

    def run(self, edges, n_ui: int) -> dict:
        """TODO: for each UI: sample osr times at (nominal grid + dco.phase_s), run the detector,
        loop filter, issue a DCO command, record traces. Return dict of numpy arrays."""
        raise NotImplementedError
