"""PRBS generator (Fibonacci LFSR).

In: seed.  Out: bit array.  Params: order 7/15/23/31.
Hardware counterpart: M3 PRBS generator (RTL). Same polynomial and seed must be used for the BER checker.
"""
import numpy as np

# order -> feedback taps (x^a + x^b + 1)
TAPS = {7: (7, 6), 15: (15, 14), 23: (23, 18), 31: (31, 28)}


class PRBS:
    def __init__(self, order: int = 7, seed: int | None = None):
        if order not in TAPS:
            raise ValueError(f"order must be one of {sorted(TAPS)}")
        self.order = order
        self.mask = (1 << order) - 1
        self._init_state = (seed if seed else self.mask) & self.mask
        if self._init_state == 0:
            raise ValueError("LFSR seed must be non-zero")
        self.state = self._init_state

    def reset(self):
        self.state = self._init_state

    def next_bits(self, n: int) -> np.ndarray:
        a, b = TAPS[self.order]
        out = np.empty(n, dtype=np.uint8)
        s = self.state
        for i in range(n):
            bit = ((s >> (a - 1)) ^ (s >> (b - 1))) & 1
            s = ((s << 1) | bit) & self.mask
            out[i] = bit
        self.state = s
        return out
