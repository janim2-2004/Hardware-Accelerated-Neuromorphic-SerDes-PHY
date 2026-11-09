"""Bits -> ideal transition timestamps.

In: bit array.  Out: EdgeStream (ideal edges at multiples of the UI).
Params: ui_s, tx_ppm (TX clock error), t0 (start time).
Hardware counterpart: OSERDES.

The serializer records the times of the edges in the bit stream.  
The first edge occurs at t0 + ui_s, and subsequent edges occur at t0 + (i+1)*ui_s for each bit where the current bit is different than the last bit (change in level).  
The initial level is bits[0], and there is no edge at t0.
"""
import numpy as np
from serdes_model.common.signals import EdgeStream


def serialize(bits: np.ndarray, ui_s: float, tx_ppm: float = 0.0, t0: float = 0.0) -> EdgeStream:
    """TODO: bit i occupies [t0 + i*ui, t0 + (i+1)*ui) with ui scaled by (1 + tx_ppm*1e-6).
    An edge exists wherever bits[i] != bits[i-1]. initial_level = bits[0] (no edge at t0)."""

    idx = np.flatnonzero(bits[1:] != bits[:-1]) + 1      # bit indices where the value changes
    edge_times = t0 + idx * ui_s * (1 + tx_ppm * 1e-6)
    return EdgeStream(edge_times, initial_level=int(bits[0]))

    #raise NotImplementedError
