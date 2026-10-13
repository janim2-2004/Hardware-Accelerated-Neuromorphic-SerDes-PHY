"""Batch experiments over config grids (jitter amp/freq, frequency offset, OSR, bit width).
Out: tidy tables (dict of arrays or a pandas DataFrame) ready for analysis.plots.
Hardware counterpart: M3 host-side sweep scripts; keep the sweep definitions identical so results are comparable."""
from serdes_model.config import LinkConfig


def sweep(base: LinkConfig, **grids) -> list:
    raise NotImplementedError
