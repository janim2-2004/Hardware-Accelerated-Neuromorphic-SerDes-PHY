"""Plot helpers: BER vs. impairment, lock transient, jitter-tolerance mask, SNN-vs-baseline overlays.

Responsibility: small matplotlib wrappers that draw onto a caller-supplied Axes (or make one), so
several curves (e.g. baseline vs SNN) can be overlaid on the same plot.
"""
import numpy as np


def plot_ber_vs_impairment(x, ber, xlabel: str, label: str = "", ax=None, floor: float | None = None,
                           logx: bool = False):
    """BER on a log axis against one swept impairment.

    A BER of exactly 0 cannot be drawn on a log axis, so zeros are drawn at `floor` (use about
    0.5 / bits_compared, the smallest rate the run could resolve) with open markers, meaning "no errors seen".
    Returns the Axes.
    """
    import matplotlib.pyplot as plt
    if ax is None:
        _, ax = plt.subplots()
    x, ber = np.asarray(x, dtype=float), np.asarray(ber, dtype=float)
    floor = floor if floor else 1e-6
    nonzero = ber > 0
    ax.semilogy(x[nonzero], ber[nonzero], "o-", label=label or None)
    if (~nonzero).any():
        ax.semilogy(x[~nonzero], np.full((~nonzero).sum(), floor), "o", mfc="none", color="gray",
                    label="no errors seen" if label else None)
    if logx:
        ax.set_xscale("log")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("BER")
    ax.grid(True, which="both", alpha=0.3)
    return ax


def plot_lock_transient(traces: dict, ax=None):
    raise NotImplementedError


def plot_tolerance_mask(freqs_hz, max_amp_ui, label: str, ax=None):
    raise NotImplementedError
