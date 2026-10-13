"""Saves detector inputs and expected outputs as files the RTL testbench can replay.

In: a detector + stimulus.  Out: .csv/.hex files (one value per line) for inputs and expected phase errors.
Hardware counterpart: golden-vector testbench for M1 RTL verification.
"""


def export_vectors(detector, samples_per_ui, out_dir: str, fmt: str = "hex"):
    raise NotImplementedError
