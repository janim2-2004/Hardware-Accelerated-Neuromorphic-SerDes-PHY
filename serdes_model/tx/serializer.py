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

    # Rejects empty array, and rejects any value other than 0 or 1
    bits = np.asarray(bits, dtype=np.uint8)
    if bits.size == 0:
        raise ValueError("serialize() needs at least one bit")
    if np.any(bits > 1):
        raise ValueError("bits must be 0/1")

    # bits[1:] != bits[:-1] --> compares each bit with the one before it to check if the values have changed and store result in another array
    # flatnonzero()         --> returns the positions where the bits differ
    # + 1                   --> converts the poistions to indicies of which bit had just changed
    idx = np.flatnonzero(bits[1:] != bits[:-1]) + 1 

    # Convert the indicies of the changed bits into time intervals
    # ui_s   --> unit interval time in seconds (how long 1 symbol lasts)
    # tx_ppm --> Tx clk frquency error (in the millions)
    edge_times = t0 + idx * ui_s * (1 + tx_ppm * 1e-6)

    # EdgeStream is an object that holds:
    # edge_times    --> sorted array of times for when the symbol flips
    # initial_level --> the lines level (0 or 1) before the first symbol flip
    return EdgeStream(edge_times, initial_level=int(bits[0]))
