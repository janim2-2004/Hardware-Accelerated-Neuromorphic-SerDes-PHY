"""Optional line coding to guarantee transition density (scrambler or 8b/10b).

In: bits.  Out: bits.  Params: scheme ("none", "scrambler", "8b10b").
Hardware counterpart: optional; not in the RTL baseline since PRBS already has good edge density.
"""
import numpy as np
from serdes_model.tx.prbs import TAPS

# 3 types of line encoders: none, scrambler, 8b/10b
SCHEMES = ("none", "scrambler", "8b10b")


# ---------------------------------------------------------------------------
# 8b/10b tables and helpers (module level so the RX decoder and tests can reuse them)
# Only the RD- column is stored; the RD+ code is the complement (see encode_byte).
# ---------------------------------------------------------------------------

# 5b/6b, RD- column, index = x (low 5 bits EDCBA), bits "abcdei"
T6 = ["100111", "011101", "101101", "110001", "110101", "101001", "011001", "111000",
      "111001", "100101", "010101", "110100", "001101", "101100", "011100", "010111",
      "011011", "100011", "010011", "110010", "001011", "101010", "011010", "111010",
      "110011", "100110", "010110", "110110", "001110", "101110", "011110", "101011"]

# 3b/4b, RD- column, index = y (high 3 bits HGF), bits "fghj"; index 7 = primary P7
T4 = ["1011", "1001", "0101", "1100", "1101", "1010", "0110", "1110"]
A7 = "0111"   # alternate D.x.7, avoids a run of 5 across the 6b/4b boundary

# Comma symbol used by the RX word aligner
K28_5 = {-1: "0011111010", +1: "1100000101"}


def disparity(code: str) -> int:
    return code.count("1") - (len(code) - code.count("1"))   # number of 1's - number of 0's


def comp(code: str) -> str:
    return code.translate(str.maketrans("01", "10"))          # flip every bit


def encode_byte(byte: int, rd: int) -> tuple[str, int]:
    """Encode one byte (D.x.y) at running disparity rd (-1 or +1). Returns (10-bit code, new rd)."""
    # x --> lower 5-bits
    # y --> upper 3-bits
    x, y = byte & 0x1F, byte >> 5

    # 5b/6b: complement at RD+ if unbalanced
    six = T6[x]

    # rd == +1 means there are more 1s, therefore we to use the complement 
    # If the line is unbalanced, flip the disparity
    # For case where y == 7 (code = 111000), it is balanced by if the disparity was prev. +1, 
    # then we want to use the complement to avoid a long run of 1's
    if rd == +1 and (disparity(six) != 0 or x == 7): 
        six = comp(six)
    if disparity(six) != 0:
        rd = -rd

    # 3b/4b: uses the RD left by the 6b sub-block; D.x.3 is balanced but has two forms
    use_a7 = y == 7 and ((rd == -1 and x in (17, 18, 20)) or (rd == +1 and x in (11, 13, 14)))
    four = A7 if use_a7 else T4[y]
    if rd == +1 and (disparity(four) != 0 or y == 3):
        four = comp(four)
    if disparity(four) != 0:
        rd = -rd

    return six + four, rd

def bits_to_bytes(bits: np.ndarray) -> np.ndarray:
    """Pack bits into bytes, 8 at a time, first bit = LSB (bit A)."""
    weights = 1 << np.arange(8)
    return (bits.reshape(-1, 8).astype(np.int64) * weights).sum(axis=1)


def bytes_to_bits(data: np.ndarray) -> np.ndarray:
    """Inverse of bits_to_bytes."""
    return ((np.asarray(data)[:, None] >> np.arange(8)) & 1).astype(np.uint8).ravel()


class LineEncoder:
    def __init__(self, scheme: str = "none", taps=TAPS[7]):
        if scheme not in SCHEMES:
            raise ValueError(f"scheme must be one of {SCHEMES}")
        self.scheme = scheme
        self.taps = taps

        self._hist = np.ones(max(taps), dtype=np.uint8) # history of past outputs (last element = most recent)
        self._rd = -1 # running disparity for 8b/10b encoding

    def encode(self, bits: np.ndarray) -> np.ndarray:
        bits = np.asarray(bits, dtype=np.uint8)
        if self.scheme == "none":
            return bits.copy()
        if self.scheme == "scrambler":
            return self._scramble(bits)
        return self._encode_8b10b(bits)

    # Implement multiplicative scrambler encoder
    # The previous data affects how the data is scrambled
    def _scramble(self, d):
        a, b = self.taps

        m = len(self._hist) # how many pasts outputs we need
        buf = np.concatenate([self._hist, np.zeros(len(d), np.uint8)]) # array that holds past and future data

        for i in range(len(d)):
            k = m + i # position of output[i] in the buffer
            buf[k] = d[i] ^ buf[k - a] ^ buf[k - b] # XOR input with older outputted data

        self._hist = buf[-m:].copy() # keep the last `m` outputs for the next call
        return buf[m:]               # drop the history bits, return only the new outputs

    # 8b/10b: each 8 input bits -> one 10-bit symbol, running disparity carried across calls
    def _encode_8b10b(self, bits):
        if len(bits) % 8:
            raise ValueError("8b10b input length must be a multiple of 8")
        out = []
        for byte in bits_to_bytes(bits):
            code, self._rd = encode_byte(int(byte), self._rd)
            out.append(code)
        return np.frombuffer("".join(out).encode(), dtype=np.uint8) - ord("0")
