"""Samples the line at given clock-edge times.

In: EdgeStream + array of sample times.  Out: SampleStream.
Params: aperture_s (setup/hold window), metastability handling (return random bit inside window).
Hardware counterpart: input flip-flops / ISERDES capture.
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
        raise NotImplementedError
