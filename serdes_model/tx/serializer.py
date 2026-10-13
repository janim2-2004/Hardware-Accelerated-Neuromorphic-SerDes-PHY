"""Bits -> ideal transition timestamps.

In: bit array.  Out: EdgeStream (ideal edges at multiples of the UI).
Params: ui_s, tx_ppm (TX clock error), t0 (start time).
Hardware counterpart: OSERDES.
"""
import numpy as np
from serdes_model.common.signals import EdgeStream


def serialize(bits: np.ndarray, ui_s: float, tx_ppm: float = 0.0, t0: float = 0.0) -> EdgeStream:
    """TODO: bit i occupies [t0 + i*ui, t0 + (i+1)*ui) with ui scaled by (1 + tx_ppm*1e-6).
    An edge exists wherever bits[i] != bits[i-1]. initial_level = bits[0] (no edge at t0)."""
    raise NotImplementedError
