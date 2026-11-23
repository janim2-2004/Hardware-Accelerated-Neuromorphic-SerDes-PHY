"""Recovered bits -> parallel words.

In: bit array.  Out: 2-D array (n_words, word_bits).  Params: word_bits, msb_first.
Hardware counterpart: ISERDES shift register.

Responsibility: group the recovered serial bit stream into fixed-width words.
Output layout: each row is one word, written MSB at column 0 down to LSB at the last column.
  msb_first=True  -> the first bit received in a word is its MSB (row = bits in arrival order).
  msb_first=False -> the first bit received is the LSB (row = arrival order reversed).
A trailing partial word (fewer than word_bits leftover bits) is dropped, as a real shift register
would never present it as a complete word.
"""
import numpy as np


class Deserializer:
    def __init__(self, word_bits: int = 8, msb_first: bool = True):
        if word_bits < 1:
            raise ValueError("word_bits must be >= 1")
        self.word_bits, self.msb_first = word_bits, msb_first

    def deserialize(self, bits: np.ndarray) -> np.ndarray:
        """Return an (n_words, word_bits) uint8 array of bits, MSB in column 0."""
        bits = np.asarray(bits, dtype=np.uint8).ravel()
        n_words = len(bits) // self.word_bits                    # whole words only
        words = bits[: n_words * self.word_bits].reshape(n_words, self.word_bits)
        if not self.msb_first:
            words = words[:, ::-1]                               # first-arrived bit becomes the LSB
        return words.copy()

    def to_ints(self, words: np.ndarray) -> np.ndarray:
        """Convert the bit matrix from deserialize() into integer word values (MSB weighted highest)."""
        words = np.asarray(words, dtype=np.int64)
        weights = 1 << np.arange(self.word_bits - 1, -1, -1, dtype=np.int64)
        return words @ weights
