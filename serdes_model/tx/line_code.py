"""Optional line coding to guarantee transition density (scrambler or 8b/10b).

In: bits.  Out: bits.  Params: scheme ("none", "scrambler", "8b10b").
Hardware counterpart: optional; not in the RTL baseline since PRBS already has good edge density.
"""
import numpy as np


class LineEncoder:
    def __init__(self, scheme: str = "none"):
        self.scheme = scheme

    def encode(self, bits: np.ndarray) -> np.ndarray:
        # TODO: scheme == "none" -> passthrough; implement scrambler / 8b10b only if you need them.
        raise NotImplementedError
