"""Seeded random number generation. Use make_rng everywhere so runs are reproducible."""
import numpy as np


def make_rng(seed: int, stream: int = 0) -> np.random.Generator:
    """Independent reproducible stream per (seed, stream) pair."""
    return np.random.default_rng(np.random.SeedSequence([seed, stream]))
