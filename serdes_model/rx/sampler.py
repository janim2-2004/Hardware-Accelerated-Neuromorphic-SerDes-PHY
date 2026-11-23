"""Samples the line at given clock-edge times.

In: EdgeStream + array of sample times.  Out: SampleStream.
Params: aperture_s (setup/hold window), metastability handling (return random bit inside window).
Hardware counterpart: input flip-flops / ISERDES capture.

Responsibility: answer "what did the receiver's flip-flop capture at each sample instant?".
Normally that is just the line level at that time. If a sample lands within +/- aperture/2 of an
edge, a real flip-flop could go metastable, so the captured bit is replaced with a random 0/1.
"""
import numpy as np
from serdes_model.common.rng import make_rng
from serdes_model.common.signals import EdgeStream, SampleStream


class Sampler:
    def __init__(self, aperture_s: float = 0.0, seed: int = 0):
        self.aperture_s = aperture_s
        self.seed = seed
        # Seeded generator so metastable outcomes are reproducible run to run.
        # (Previously missing: sample() crashed with AttributeError whenever aperture_s > 0.)
        self._rng = make_rng(seed)

    def sample(self, edges: EdgeStream, sample_times: np.ndarray) -> SampleStream:
        # Force sample_times into a 1-D float array (accepts scalars, lists, arrays).
        t = np.atleast_1d(np.asarray(sample_times, dtype=float))

        # Ideal capture: the line level at each sample time (binary search in EdgeStream).
        bits = edges.level_at(t)

        # Metastability model: only needed if there is an aperture and at least one edge.
        if self.aperture_s > 0 and edges.n_edges > 0:
            e = edges.edge_times
            last = len(e) - 1
            i = np.searchsorted(e, t)                              # first edge at/after each sample
            dist_prev = np.abs(t - e[np.clip(i - 1, 0, last)])     # distance to nearest edge before
            dist_next = np.abs(e[np.clip(i, 0, last)] - t)         # distance to nearest edge after

            # Samples whose nearest edge is inside the +/- aperture/2 window are "near an edge".
            near = np.minimum(dist_prev, dist_next) < self.aperture_s / 2
            # Skip the random draw entirely if no sample is near an edge.
            if near.any():
                bits = bits.copy()
                bits[near] = self._rng.integers(0, 2, size=int(near.sum()), dtype=np.uint8)

        return SampleStream(t, bits)
