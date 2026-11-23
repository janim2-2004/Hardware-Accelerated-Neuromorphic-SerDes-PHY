"""Phase 1 gate figure: free-running-receiver BER against each channel impairment, one panel each.

Run from the repo root:   python -m serdes_model.sim.ber_vs_impairments [output.png]

Responsibility: reproduce the plots that show every impairment closes the eye the way theory predicts
(RJ follows the Gaussian tail Q(0.5/sigma); SJ and DJ switch on at 0.5 UI; a ppm offset slips the
receiver; ISI collapses below about 3 MHz). BER here is the direct bit-for-bit comparison, so once a
bit slips every following bit counts as an error (there is no CDR yet to follow the drift).
"""
import math
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from serdes_model.analysis.plots import plot_ber_vs_impairment
from serdes_model.config import LinkConfig
from serdes_model.sim.sweeps import sweep


def _q(x):
    return 0.5 * math.erfc(x / math.sqrt(2))


def make_figure(path: str = "ber_vs_impairments.png"):
    base = LinkConfig()
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    axes = axes.ravel()

    def panel(ax, field, values, n_bits, xlabel, title, scale=1.0, logx=False):
        rows = sweep(base, n_bits=n_bits, **{field: values})
        plot_ber_vs_impairment([v * scale for v in values], [r["ber_direct"] for r in rows], xlabel,
                               ax=ax, floor=0.5 / n_bits, logx=logx)
        ax.set_title(f"{title}  ({n_bits:,} bits/point)")
        return rows

    # 1. Random jitter, with the analytic Gaussian-tail curve for comparison
    sig = [0.10, 0.12, 0.15, 0.18, 0.20, 0.25, 0.30, 0.35, 0.40]
    panel(axes[0], "rj_sigma_ui", sig, 200_000, "RJ sigma (UI rms)", "Random jitter")
    xs = np.linspace(0.10, 0.40, 100)
    axes[0].semilogy(xs, [_q(0.5 / s) for s in xs], "k--", lw=1, label="theory Q(0.5/sigma)")
    axes[0].legend()
    # 2. Sinusoidal jitter (1 MHz)
    panel(axes[1], "sj_amplitude_ui", [0, 0.2, 0.4, 0.5, 0.55, 0.6, 0.8, 1.0, 1.5], 20_000,
          "SJ amplitude (UI peak) @ 1 MHz", "Sinusoidal jitter")
    # 3. Deterministic jitter
    panel(axes[2], "dj_peak_ui", [0, 0.2, 0.4, 0.45, 0.5, 0.55, 0.6, 0.8], 20_000,
          "DJ peak (UI)", "Deterministic (duty-cycle) jitter")
    # 4. Frequency offset
    panel(axes[3], "freq_offset_ppm", [0.5, 1, 2, 5, 10, 100, 1_000, 10_000], 100_000,
          "frequency offset (ppm)", "TX/RX frequency offset (no CDR)", logx=True)
    # 5. Threshold noise (x axis in volts; the slew converts it to time)
    sv = [0, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    panel(axes[4], "noise_sigma_v", sv, 100_000,
          f"threshold noise (V rms), slew {base.slew_v_per_s / 1e6:.0f} V/us", "Threshold noise")
    # 6. ISI bandwidth
    bw = [1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10]
    panel(axes[5], "isi_bandwidth_hz", [b * 1e6 for b in bw], 20_000,
          "channel bandwidth (MHz)", "ISI (first-order RC)", scale=1e-6, logx=True)

    fig.suptitle("Phase 1: free-running receiver BER vs each channel impairment "
                 f"(25 Mbps, PRBS{base.prbs_order}, sampling at mid-UI)", fontsize=13)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    return path


if __name__ == "__main__":
    print(make_figure(sys.argv[1] if len(sys.argv) > 1 else "ber_vs_impairments.png"))
