"""First-order RC ISI channel, checked against the closed-form solution."""
import math
import numpy as np
import pytest
from serdes_model.channel.isi_channel import ISIChannel
from serdes_model.common.signals import EdgeStream

TAU = 10.0
BW = 1.0 / (2 * math.pi * TAU)          # chosen so tau = 10 (time units are arbitrary here)


def test_tau_from_bandwidth():
    assert abs(ISIChannel(BW).tau_s - TAU) < 1e-12


def test_isolated_edges_have_no_shift():
    e = EdgeStream(np.array([0.0, 1000.0, 2000.0]), 0)                      # spacing >> tau: fully settled
    assert np.allclose(ISIChannel(BW).apply(e).edge_times, e.edge_times, atol=1e-9)


def test_fixed_delay_option():
    e = EdgeStream(np.array([0.0, 1000.0]), 0)
    out = ISIChannel(BW, include_fixed_delay=True).apply(e)
    assert np.allclose(out.edge_times - e.edge_times, TAU * math.log(2), atol=1e-9)


def test_short_pulse_trailing_edge_moves_early_by_closed_form():
    w = 15.0
    out = ISIChannel(BW).apply(EdgeStream(np.array([0.0, w]), 0))
    expected_shift = TAU * math.log(1 - math.exp(-w / TAU))                 # = -2.52 for w = 1.5 tau
    assert out.n_edges == 2
    assert abs(out.edge_times[0] - 0.0) < 1e-9                              # leading edge unaffected
    assert abs((out.edge_times[1] - w) - expected_shift) < 1e-9
    assert expected_shift < 0                                               # earlier => pulse shrinks


def test_pulse_too_short_is_swallowed():
    # width 5 < tau*ln2 = 6.93: the line never reaches 50% before the edge reverses
    assert ISIChannel(BW).apply(EdgeStream(np.array([0.0, 5.0]), 0)).n_edges == 0


def test_works_from_initial_level_one_and_keeps_alternation():
    e = EdgeStream(np.array([0.0, 15.0, 60.0, 75.0, 400.0]), 1)
    out = ISIChannel(BW).apply(e)
    assert out.initial_level == 1 and out.n_edges == 5
    assert np.all(np.diff(out.edge_times) > 0)


def test_lower_bandwidth_means_more_distortion():
    e = EdgeStream(np.array([0.0, 20.0, 45.0, 60.0, 100.0]), 0)
    shifts = []
    for bw in (BW * 4, BW * 2, BW):
        out = ISIChannel(bw).apply(e)
        assert out.n_edges == e.n_edges
        shifts.append(np.abs(out.edge_times - e.edge_times).max())
    assert shifts[0] < shifts[1] < shifts[2]


def test_rejects_bad_bandwidth():
    with pytest.raises(ValueError):
        ISIChannel(0.0)
