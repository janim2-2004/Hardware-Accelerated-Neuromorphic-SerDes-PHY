"""Reverses tx.line_code. In: bits/words. Out: data. Hardware counterpart: optional decoder."""
import numpy as np


class LineDecoder:
    def __init__(self, scheme: str = "none"):
        self.scheme = scheme

    def decode(self, bits: np.ndarray) -> np.ndarray:
        raise NotImplementedError
