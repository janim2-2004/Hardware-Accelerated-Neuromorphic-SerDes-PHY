"""Fixed-point quantization. Use as a switch on SNN/loop-filter blocks, not as a separate code path.

Hardware counterpart: the bit widths chosen for the RTL (Q format = total_bits, frac_bits).
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class QFormat:
    total_bits: int
    frac_bits: int
    signed: bool = True

    @property
    def lsb(self) -> float:
        return 2.0 ** -self.frac_bits

    @property
    def max_value(self) -> float:
        int_max = (2 ** (self.total_bits - 1) - 1) if self.signed else (2 ** self.total_bits - 1)
        return int_max * self.lsb

    @property
    def min_value(self) -> float:
        return -(2 ** (self.total_bits - 1)) * self.lsb if self.signed else 0.0

    def to_int(self, x, mode: str = "round", saturate: bool = True):
        """Quantize to the integer code the RTL would hold."""
        scaled = np.asarray(x, dtype=float) / self.lsb
        codes = np.round(scaled) if mode == "round" else np.floor(scaled)
        if saturate:
            lo = self.min_value / self.lsb
            hi = self.max_value / self.lsb
            codes = np.clip(codes, lo, hi)
        return codes.astype(np.int64)

    def quantize(self, x, mode: str = "round", saturate: bool = True):
        """Return x snapped to the representable grid (as float)."""
        return self.to_int(x, mode, saturate) * self.lsb
