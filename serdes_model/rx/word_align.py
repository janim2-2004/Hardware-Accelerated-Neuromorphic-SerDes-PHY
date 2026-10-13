"""Finds word boundaries using a training/comma pattern.

In: bit array.  Out: bit offset (0..word_bits-1) and aligned words.  Params: comma pattern.
Hardware counterpart: bitslip / alignment logic. For BER-only testing with PRBS this can be skipped.
"""
import numpy as np


class WordAligner:
    def __init__(self, comma_pattern: int, word_bits: int = 8):
        self.comma_pattern, self.word_bits = comma_pattern, word_bits

    def find_offset(self, bits: np.ndarray) -> int:
        raise NotImplementedError
