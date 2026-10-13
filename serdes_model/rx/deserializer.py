"""Recovered bits -> parallel words.

In: bit array.  Out: 2-D array (n_words, word_bits).  Params: word_bits, msb_first.
Hardware counterpart: ISERDES shift register.
"""
import numpy as np


class Deserializer:
    def __init__(self, word_bits: int = 8, msb_first: bool = True):
        self.word_bits, self.msb_first = word_bits, msb_first

    def deserialize(self, bits: np.ndarray) -> np.ndarray:
        raise NotImplementedError
