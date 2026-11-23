"""Seeded random number generation. Use make_rng everywhere so runs are reproducible."""
import numpy as np

# Stream ids: each random source draws from its own independent stream of the same seed, so
# enabling/disabling one impairment never changes the random numbers another one sees.
STREAM_SAMPLER = 0      # sampler metastability (make_rng default)
STREAM_TX = 1           # TX driver jitter
STREAM_RJ = 2           # random jitter source
STREAM_NOISE = 3        # threshold (voltage) noise


def make_rng(seed: int, stream: int = 0) -> np.random.Generator:
    """Independent reproducible stream per (seed, stream) pair."""
    return np.random.default_rng(np.random.SeedSequence([seed, stream]))
