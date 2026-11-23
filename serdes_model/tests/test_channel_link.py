"""Channel wired into run_link: chain building, per-impairment behaviour, BER against theory, sweeps."""
import math
from dataclasses import replace
import numpy as np
import pytest
from serdes_model.channel.chain import build_channel
from serdes_model.channel.isi_channel import ISIChannel
from serdes_model.channel.jitter_sources import (
    DeterministicJitter, FrequencyOffset, RandomJitter, SinusoidalJitter)
from serdes_model.channel.noise import ThresholdNoise
from serdes_model.config import LinkConfig
from serdes_model.rx.frontend import LVDSFrontEnd
from serdes_model.sim.link import run_link
from serdes_model.sim.sweeps import sweep
from serdes_model.tx.tx_driver import TxDriver

BASE = LinkConfig()


def Q(x):
    return 0.5 * math.erfc(x / math.sqrt(2))


# ---------------- chain building ----------------
def test_default_config_builds_an_empty_chain():
    assert build_channel(BASE).sources == []


def test_full_chain_order_matches_the_diagram():
    cfg = replace(BASE, tx_rise_time_s=1e-9, sj_amplitude_ui=0.1, rj_sigma_ui=0.01, dj_peak_ui=0.05,
                  freq_offset_ppm=10, isi_bandwidth_hz=50e6, noise_sigma_v=0.01, fe_hysteresis_s=1e-9)
    kinds = [type(s) for s in build_channel(cfg).sources]
    assert kinds == [TxDriver, SinusoidalJitter, RandomJitter, DeterministicJitter, FrequencyOffset,
                     ISIChannel, ThresholdNoise, LVDSFrontEnd]


def test_bypass_skips_every_impairment():
    cfg = replace(BASE, rj_sigma_ui=0.5, sj_amplitude_ui=1.0, channel_bypass=True)
    assert build_channel(cfg).sources == []
    assert run_link(cfg, n_bits=5_000)["direct_errors"] == 0


def test_ideal_config_leaves_edges_untouched():
    r = run_link(BASE, n_bits=2_000)
    assert r["rx_edges"].n_edges > 0 and r["ber"] == 0.0 and r["direct_errors"] == 0


def test_cdr_is_still_not_implemented():
    with pytest.raises(NotImplementedError):
        run_link(BASE, detector=object(), n_bits=100)


# ---------------- each impairment closes the eye where theory says ----------------
def test_random_jitter_ber_matches_gaussian_tail():
    # A sample is wrong when its left edge slips late (or its right edge early) by more than 0.5 UI.
    # With PRBS transition density 1/2 that gives BER ~ Q(0.5 / sigma_ui).
    for sigma in (0.2, 0.25):
        ber = run_link(replace(BASE, rj_sigma_ui=sigma), n_bits=200_000)["ber_direct"]
        assert abs(ber - Q(0.5 / sigma)) < 0.15 * Q(0.5 / sigma), (sigma, ber, Q(0.5 / sigma))


def test_ber_rises_monotonically_with_random_jitter():
    bers = [run_link(replace(BASE, rj_sigma_ui=s), n_bits=100_000)["ber_direct"] for s in (0.15, 0.2, 0.25, 0.3)]
    assert bers == sorted(bers) and bers[0] < bers[-1]


def test_sinusoidal_jitter_errors_start_beyond_half_a_ui():
    kw = dict(sj_freq_hz=1e6)
    assert run_link(replace(BASE, sj_amplitude_ui=0.3, **kw), n_bits=20_000)["direct_errors"] == 0
    assert run_link(replace(BASE, sj_amplitude_ui=0.7, **kw), n_bits=20_000)["direct_errors"] > 0


def test_deterministic_jitter_errors_start_beyond_half_a_ui():
    assert run_link(replace(BASE, dj_peak_ui=0.3), n_bits=20_000)["direct_errors"] == 0
    assert run_link(replace(BASE, dj_peak_ui=0.6), n_bits=20_000)["direct_errors"] > 0


def test_frequency_offset_slips_a_free_running_receiver():
    # drift = ppm * 1e-6 * n_bits UI. 10 ppm over 20k bits = 0.2 UI (fine); 1000 ppm = 20 UI (slips).
    assert run_link(replace(BASE, freq_offset_ppm=10.0), n_bits=20_000)["direct_errors"] == 0
    assert run_link(replace(BASE, freq_offset_ppm=1000.0), n_bits=20_000)["direct_errors"] > 0


def test_threshold_noise_hurts_more_with_larger_sigma():
    assert run_link(replace(BASE, noise_sigma_v=0.01), n_bits=20_000)["direct_errors"] == 0
    assert run_link(replace(BASE, noise_sigma_v=0.3), n_bits=100_000)["ber_direct"] > 0


def test_isi_bandwidth_sweep():
    assert run_link(replace(BASE, isi_bandwidth_hz=10e6), n_bits=20_000)["direct_errors"] == 0
    narrow = run_link(replace(BASE, isi_bandwidth_hz=3e6), n_bits=20_000)
    assert narrow["direct_errors"] > 0
    very_narrow = run_link(replace(BASE, isi_bandwidth_hz=2e6), n_bits=20_000)
    assert very_narrow["rx_edges"].n_edges < run_link(BASE, n_bits=20_000)["rx_edges"].n_edges   # pulses swallowed


def test_tx_driver_and_frontend_fixed_delays_are_harmless_when_small():
    cfg = replace(BASE, tx_rise_time_s=4e-9, fe_hysteresis_s=2e-9, fe_threshold_offset_s=1e-9)
    assert run_link(cfg, n_bits=20_000)["direct_errors"] == 0


# ---------------- reproducibility ----------------
def test_same_seed_same_result_different_seed_differs():
    cfg = replace(BASE, rj_sigma_ui=0.3, noise_sigma_v=0.1)
    a, b = run_link(cfg, n_bits=20_000), run_link(cfg, n_bits=20_000)
    assert np.array_equal(a["rx_bits"], b["rx_bits"])
    c = run_link(replace(cfg, seed=99), n_bits=20_000)
    assert not np.array_equal(a["rx_bits"], c["rx_bits"])


# ---------------- sweeps ----------------
def test_sweep_returns_one_row_per_grid_point():
    rows = sweep(BASE, n_bits=5_000, rj_sigma_ui=[0.0, 0.3], sj_freq_hz=[1e5, 1e6])
    assert len(rows) == 4
    assert {"rj_sigma_ui", "sj_freq_hz", "errors", "ber", "ber_direct"} <= set(rows[0])
    assert rows[0]["rj_sigma_ui"] == 0.0 and rows[0]["ber_direct"] == 0.0
    assert [r["rj_sigma_ui"] for r in rows if r["sj_freq_hz"] == 1e6][-1] == 0.3


def test_sweep_rejects_unknown_field():
    with pytest.raises(ValueError):
        sweep(BASE, not_a_field=[1])
