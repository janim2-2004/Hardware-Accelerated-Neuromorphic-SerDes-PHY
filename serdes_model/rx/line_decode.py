"""Reverses tx.line_code. In: bits/words. Out: data. Hardware counterpart: optional decoder."""
import numpy as np
from serdes_model.tx.prbs import TAPS
from serdes_model.tx.line_code import SCHEMES, encode_byte, bytes_to_bits

# 10-bit code -> byte, built from every data symbol at both running disparities
_DECODE_8B10B = {encode_byte(b, rd)[0]: b for b in range(256) for rd in (-1, +1)}


class LineDecoder:
    def __init__(self, scheme: str = "none", taps=TAPS[7]):
        if scheme not in SCHEMES:
            raise ValueError(f"scheme must be one of {SCHEMES}")
        self.scheme, self.taps = scheme, taps
        self._hist = np.ones(max(taps), dtype=np.uint8)    # match the encoder; any value self-syncs

    def decode(self, bits):
        bits = np.asarray(bits, dtype=np.uint8)
        if self.scheme == "none":
            return bits.copy()
        if self.scheme == "scrambler":
            return self._descramble(bits)
        return self._decode_8b10b(bits)

    def _descramble(self, r):
        a, b = self.taps
        m = len(self._hist)
        buf = np.concatenate([self._hist, r])
        k = np.arange(m, len(buf))
        d = buf[k] ^ buf[k - a] ^ buf[k - b]   # vectorized: depends only on received bits
        self._hist = buf[-m:].copy()
        return d

    def _decode_8b10b(self, bits):
        if len(bits) % 10:
            raise ValueError("8b10b input length must be a multiple of 10 (is the stream word-aligned?)")
        data = []
        for sym in bits.reshape(-1, 10):
            code = "".join(map(str, sym))
            if code not in _DECODE_8B10B:
                raise ValueError(f"invalid 8b10b code {code}")   # later: count as a code violation
            data.append(_DECODE_8B10B[code])
        return bytes_to_bits(np.array(data, dtype=np.int64))
