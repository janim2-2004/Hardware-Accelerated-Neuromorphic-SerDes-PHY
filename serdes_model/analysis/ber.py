"""Self-synchronizing BER check against the PRBS.

In: received bit array, PRBS order.  Out: (errors, bits_compared, ber).
Approach: run a local LFSR seeded from the first `order` received bits, then compare. Matches the RTL BER checker.
Hardware counterpart: M3 BER checker.

Responsibility: measure how many received bits differ from the PRBS that should have been sent,
without needing to know the transmitter's seed or the delay through the link.

Why seeding from received bits works: the LFSR state is exactly its last `order` output bits
(newest in bit 0). So the first `order` received bits ARE a valid LFSR state; load them, free-run
the same LFSR, and every later bit should match.

Caveats (same as a hardware checker): the first `order` bits are consumed for sync and not counted,
and a bit error inside those first `order` bits corrupts the local seed, giving ~50% BER.
"""
import numpy as np
from serdes_model.tx.prbs import PRBS


def measure_ber(rx_bits: np.ndarray, prbs_order: int = 7):
    """Return (errors, bits_compared, ber)."""
    rx = np.asarray(rx_bits, dtype=np.uint8).ravel()
    n = len(rx)
    if n <= prbs_order:
        raise ValueError(f"need more than {prbs_order} bits to sync a PRBS-{prbs_order} checker")

    # Build the LFSR state from the first `order` bits: the most recent bit (index order-1) is bit 0.
    state = 0
    for i, b in enumerate(rx[:prbs_order][::-1]):
        state |= int(b) << i

    compared = n - prbs_order
    if state == 0:
        # An all-zero seed is the LFSR's lock-up state: the stream is not a PRBS (dead link / stuck line).
        # Report total failure rather than raising, so sweeps keep running.
        return compared, compared, 1.0

    # Free-run a local reference from the seeded state and compare against everything after the seed.
    reference = PRBS(prbs_order, seed=state).next_bits(compared)
    errors = int(np.count_nonzero(reference != rx[prbs_order:]))
    return errors, compared, errors / compared
