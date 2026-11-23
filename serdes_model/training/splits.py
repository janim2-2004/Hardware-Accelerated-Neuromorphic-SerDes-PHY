"""
Train / validation / test splits, defined at the stream level

Purpose: guarantee the three sets never share a simulated stream (same PRBS seed, same jitter draw), so
validation and test scores are not inflated by leakage. Also defines the named conditions (clean, mild,
heavy, near_lock, out_of_range) used to slice test results.

Contract with sim/dataset.py (to be written):
    generate_windows(rng, n_windows, condition) -> (windows uint8 [N, 5], labels int8 [N])
    windows columns = [previous sample, slot0, slot1, slot2, slot3]
    labels: -1 = sampling early, 0 = hold, +1 = sampling late
Until that file exists, a clean placeholder generator is used so the rest of the pipeline can run.

Numpy only (no torch).
"""
from dataclasses import dataclass

import numpy as np

from serdes_model.common.rng import make_rng

# Disjoint blocks of seeds. A stream's seed = block start + stream index, so no two splits can share a stream.
SEED_BLOCKS = {
    "train": (0, 1_000_000),
    "val": (1_000_000, 1_000_100),
    "test": (2_000_000, 2_000_100),
}


@dataclass(frozen=True)
class Condition:
    """One set of simulation conditions. Ranges are (low, high); a value is drawn per stream.

    PLACEHOLDER numbers: replace with ranges taken from the jitter spec of the link you are modelling.
    """
    name: str
    rj_sigma_ui: tuple = (0.0, 0.0)     # random jitter, sigma in UI
    sj_amp_ui: tuple = (0.0, 0.0)       # sinusoidal jitter amplitude in UI
    phase_range_ui: float = 0.375       # sampling phase error drawn from +/- this (UI)
    prbs_order: int = 7
    flip_prob: float = 0.0              # placeholder generator only: per-sample flip probability


CONDITIONS = {
    "train_mix":    Condition("train_mix", rj_sigma_ui=(0.0, 0.08), sj_amp_ui=(0.0, 0.20), flip_prob=0.02),
    "clean":        Condition("clean"),
    "mild":         Condition("mild", rj_sigma_ui=(0.01, 0.03), flip_prob=0.01),
    "heavy":        Condition("heavy", rj_sigma_ui=(0.05, 0.08), sj_amp_ui=(0.10, 0.20), flip_prob=0.05),
    "near_lock":    Condition("near_lock", rj_sigma_ui=(0.01, 0.03), phase_range_ui=0.125, flip_prob=0.01),
    "out_of_range": Condition("out_of_range", rj_sigma_ui=(0.10, 0.15), prbs_order=15, flip_prob=0.10),
}
TEST_CONDITIONS = ["clean", "mild", "heavy", "near_lock", "out_of_range"]


def seed_for(split: str, index: int) -> int:
    "Seed of the index-th stream of a split. Raises if the index would spill into another split's block."
    start, end = SEED_BLOCKS[split]
    if not 0 <= index < end - start:
        raise ValueError(f"stream index {index} outside the {split} block of size {end - start}")
    return start + index


def _placeholder_windows(rng, n_windows: int, flip_prob: float):
    """
    Stand-in generator that follows the early / aligned / late table, with optional random bit flips.
    Replace by sim.dataset.generate_windows once the serializer -> impairments -> sampler chain exists.
    Gap letters: A = previous|slot0, B = slot0|slot1, C = slot1|slot2, D = slot2|slot3.
    """
    labels = rng.choice([-1, 0, 1], size=n_windows, p=[0.25, 0.5, 0.25]).astype(np.int8)
    a = rng.integers(0, 2, size=n_windows).astype(np.uint8)
    na = 1 - a
    w = np.repeat(a[:, None], 5, axis=1)                    # default: no transition at all
    early, late = labels == -1, labels == 1
    aligned = (labels == 0) & (rng.random(n_windows) < 0.5)
    w[early, 2:] = na[early, None]                           # a a ~a ~a ~a : edge in gap B  -> early
    w[late, 4] = na[late]                                    # a a a a ~a   : edge in gap D  -> late
    w[aligned, 1:] = na[aligned, None]                       # a ~a ~a ~a ~a: edge in gap A  -> aligned (hold)
    w ^= (rng.random((n_windows, 5)) < flip_prob).astype(np.uint8)
    return w, labels


def make_split(split: str, n_windows: int, index: int = 0, condition: Condition | None = None):
    "Windows and labels from one stream of the given split. Same (split, index) always gives the same data."
    condition = condition or CONDITIONS["train_mix"]
    rng = make_rng(seed_for(split, index))
    try:
        from serdes_model.sim.dataset import generate_windows
    except ImportError:                                      # sim/dataset.py not written yet
        return _placeholder_windows(rng, n_windows, condition.flip_prob)
    return generate_windows(rng, n_windows, condition)


def test_slices(n_windows: int = 10_000) -> dict:
    "The frozen test set: one slice per named condition, each from its own stream. Touch it once, at the end."
    return {name: make_split("test", n_windows, index=i, condition=CONDITIONS[name])
            for i, name in enumerate(TEST_CONDITIONS)}


if __name__ == "__main__":
    w, y = make_split("train", 5, index=0)
    print(w, y)