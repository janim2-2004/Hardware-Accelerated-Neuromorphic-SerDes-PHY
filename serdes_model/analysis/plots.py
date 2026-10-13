"""Plot helpers: BER vs. impairment, lock transient, jitter-tolerance mask, SNN-vs-baseline overlays."""


def plot_lock_transient(traces: dict, ax=None):
    raise NotImplementedError


def plot_tolerance_mask(freqs_hz, max_amp_ui, label: str, ax=None):
    raise NotImplementedError
