"""Self-synchronizing BER check against the PRBS.

In: received bit array, PRBS order.  Out: (errors, bits_compared, ber).
Approach: run a local LFSR seeded from the first `order` received bits, then compare. Matches the RTL BER checker.
Hardware counterpart: M3 BER checker.
"""
import numpy as np


def measure_ber(rx_bits: np.ndarray, prbs_order: int = 7):
    raise NotImplementedError
