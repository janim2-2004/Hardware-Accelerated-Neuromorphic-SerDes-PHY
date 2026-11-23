"""Bits -> ideal transition timestamps.

In: bit array.  Out: EdgeStream (ideal edges at multiples of the UI).
Params: ui_s, tx_ppm (TX clock error), t0 (start time).
Hardware counterpart: OSERDES.

Responsibility: turn a bit sequence into the times at which the line toggles.
Bit i occupies [t0 + i*ui, t0 + (i+1)*ui). An edge sits at the start of bit i whenever
bits[i] != bits[i-1]. The initial level is bits[0], so there is no edge at t0 itself.
tx_ppm stretches the UI by (1 + tx_ppm*1e-6) to model a TX clock that is slightly off-frequency.
"""
import numpy as np
from serdes_model.common.signals import EdgeStream


def serialize(bits: np.ndarray, ui_s: float, tx_ppm: float = 0.0, t0: float = 0.0) -> EdgeStream:
    bits = np.asarray(bits)
    idx = np.flatnonzero(bits[1:] != bits[:-1]) + 1      # bit indices where the value changes
    edge_times = t0 + idx * ui_s * (1 + tx_ppm * 1e-6)
    return EdgeStream(edge_times, initial_level=int(bits[0]))
