"""Batch experiments over config grids (jitter amp/freq, frequency offset, OSR, bit width).
Out: tidy tables (dict of arrays or a pandas DataFrame) ready for analysis.plots.
Hardware counterpart: M3 host-side sweep scripts; keep the sweep definitions identical so results are comparable.

Responsibility: run run_link over the Cartesian product of LinkConfig field grids and return one flat
row per run (the swept values plus the result numbers), so plots and tables are one list comprehension away.
"""
import itertools
from dataclasses import replace

from serdes_model.config import LinkConfig
from serdes_model.sim.link import run_link


def sweep(base: LinkConfig, n_bits: int = 20_000, detector=None, **grids) -> list:
    """Example: sweep(LinkConfig(), rj_sigma_ui=[0.1, 0.2], sj_freq_hz=[1e5, 1e6]) -> 4 rows.

    Each keyword is a LinkConfig field name mapped to the values to try. With no grids, one run of `base`.
    Row keys: the swept fields, plus errors, bits_compared, ber, direct_errors, ber_direct.
    """
    names = list(grids)
    for name in names:
        if not hasattr(base, name):
            raise ValueError(f"LinkConfig has no field {name!r}")
    rows = []
    for combo in itertools.product(*(grids[name] for name in names)):
        params = dict(zip(names, combo))
        r = run_link(replace(base, **params), detector=detector, n_bits=n_bits)
        rows.append({**params,
                     "errors": r["errors"], "bits_compared": r["bits_compared"], "ber": r["ber"],
                     "direct_errors": r["direct_errors"], "ber_direct": r["ber_direct"]})
    return rows
