"""Samples the line at given clock-edge times.

In: EdgeStream + array of sample times.  Out: SampleStream.
Params: aperture_s (setup/hold window), metastability handling (return random bit inside window).
Hardware counterpart: input flip-flops / ISERDES capture.

The sampler records the value of the line at the given sample times.
"""
import numpy as np
from serdes_model.common.signals import EdgeStream, SampleStream


class Sampler:
    def __init__(self, aperture_s: float = 0.0, seed: int = 0):
        self.aperture_s = aperture_s
        self.seed = seed

    def sample(self, edges: EdgeStream, sample_times: np.ndarray) -> SampleStream:
        # TODO: bits = edges.level_at(sample_times); if an edge lies within +/- aperture/2 of a sample,
        # replace that bit with a random 0/1 (metastability).

        #convert sample_times to a 1D numpy array of floats
        t = np.atleast_1d(np.asarray(sample_times, dtype=float))
        bits = edges.level_at(t)
 
        if self.aperture_s > 0 and edges.n_edges > 0:
            e = edges.edge_times
            last = len(e) - 1
            i = np.searchsorted(e, t)                                  # first edge at/after each sample
            dist_prev = np.abs(t - e[np.clip(i - 1, 0, last)])          # nearest edge before (or e[0])
            dist_next = np.abs(e[np.clip(i, 0, last)] - t)              # nearest edge after (or e[-1])
            
            #Skip the random number generation if there are no samples near edges
            near = np.minimum(dist_prev, dist_next) < self.aperture_s / 2
            if near.any():
                bits = bits.copy()
                bits[near] = self._rng.integers(0, 2, size=int(near.sum()), dtype=np.uint8)
 
        return SampleStream(t, bits)

        #raise NotImplementedError
