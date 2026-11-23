"""TX driver, threshold noise and RX front end."""
import numpy as np
import pytest
from serdes_model.channel.noise import ThresholdNoise
from serdes_model.common.signals import EdgeStream
from serdes_model.rx.frontend import LVDSFrontEnd
from serdes_model.tx.tx_driver import TxDriver


def test_tx_driver_rise_time_is_a_fixed_half_rise_delay():
    e = EdgeStream(np.array([10e-9, 20e-9, 50e-9]), 0)
    out = TxDriver(rise_time_s=2e-9).apply(e)
    assert np.allclose(out.edge_times - e.edge_times, 1e-9)                 # rise/2 on every edge


def test_tx_driver_jitter_statistics_and_reproducibility():
    e = EdgeStream(np.arange(1, 20_001, dtype=float) * 1e-6, 0)
    out = TxDriver(0.0, 1e-9, seed=3).apply(e)
    dt = out.edge_times - e.edge_times
    assert abs(dt.std() - 1e-9) < 0.03e-9
    assert np.array_equal(out.edge_times, TxDriver(0.0, 1e-9, seed=3).apply(e).edge_times)


def test_tx_driver_ideal_is_identity():
    e = EdgeStream(np.array([1.0, 2.0]), 0)
    assert np.array_equal(TxDriver().apply(e).edge_times, e.edge_times)


def test_threshold_noise_converts_volts_to_seconds():
    n = ThresholdNoise(noise_sigma_v=0.01, slew_v_per_s=1e7, seed=1)
    assert abs(n.sigma_t_s - 1e-9) < 1e-18                                  # 10 mV / (10 V/us) = 1 ns
    e = EdgeStream(np.arange(1, 20_001, dtype=float) * 1e-6, 0)
    dt = n.apply(e).edge_times - e.edge_times
    assert abs(dt.std() - 1e-9) < 0.03e-9


def test_threshold_noise_slower_edges_mean_more_jitter():
    assert ThresholdNoise(0.01, 1e7).sigma_t_s > ThresholdNoise(0.01, 1e8).sigma_t_s


def test_threshold_noise_stream_is_independent_of_random_jitter():
    from serdes_model.channel.jitter_sources import RandomJitter
    e = EdgeStream(np.arange(1, 2001, dtype=float), 0)
    a = (RandomJitter(0.1, 1.0, seed=5).apply(e).edge_times - e.edge_times)
    b = (ThresholdNoise(0.1, 1.0, seed=5).apply(e).edge_times - e.edge_times)   # same sigma, same seed
    assert abs(np.corrcoef(a, b)[0, 1]) < 0.1                                    # different streams


def test_threshold_noise_rejects_bad_slew():
    with pytest.raises(ValueError):
        ThresholdNoise(0.01, 0.0)


def test_frontend_offset_skews_rising_vs_falling():
    e = EdgeStream(np.array([10e-9, 20e-9]), 0)                             # rise, fall
    out = LVDSFrontEnd(threshold_offset_s=1e-9).apply(e)
    assert np.allclose(out.edge_times, [11e-9, 19e-9])


def test_frontend_hysteresis_delays_every_edge_by_half_the_band():
    e = EdgeStream(np.array([10e-9, 20e-9]), 0)
    out = LVDSFrontEnd(hysteresis_s=2e-9).apply(e)
    assert np.allclose(out.edge_times, [11e-9, 21e-9])


def test_frontend_ideal_is_identity():
    e = EdgeStream(np.array([1.0, 2.0]), 1)
    assert np.array_equal(LVDSFrontEnd().apply(e).edge_times, e.edge_times)
