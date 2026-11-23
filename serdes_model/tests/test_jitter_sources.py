"""Each jitter source: exact formula on hand-picked edges, identity at zero, reproducibility, statistics."""
import numpy as np
from serdes_model.channel.jitter_sources import (
    DeterministicJitter, FrequencyOffset, JitterChain, RandomJitter, SinusoidalJitter)
from serdes_model.common.signals import EdgeStream


def test_sinusoidal_jitter_formula():
    # f = 1 Hz: sin peaks (+1) at t = 0.25 + n and troughs (-1) at 0.75 + n. ui = 2 s, amp = 0.1 UI -> 0.2 s.
    e = EdgeStream(np.array([0.25, 1.25, 2.75]), 0)
    out = SinusoidalJitter(0.1, 1.0, 2.0).apply(e)
    assert np.allclose(out.edge_times, [0.45, 1.45, 2.55])


def test_sinusoidal_phase_offset():
    e = EdgeStream(np.array([0.0]), 0)
    out = SinusoidalJitter(0.1, 1.0, 2.0, phase=np.pi / 2).apply(e)        # sin(pi/2) = 1
    assert np.allclose(out.edge_times, [0.2])


def test_random_jitter_statistics_and_reproducibility():
    e = EdgeStream(np.arange(1, 50_001, dtype=float), 0)                    # edges 1 UI apart (ui_s = 1)
    out = RandomJitter(0.05, 1.0, seed=7).apply(e)
    dt = out.edge_times - e.edge_times
    assert out.n_edges == e.n_edges                                         # sigma << spacing: nothing swallowed
    assert abs(dt.std() - 0.05) < 0.05 * 0.03                               # sigma within 3%
    assert abs(dt.mean()) < 0.002                                           # zero mean
    again = RandomJitter(0.05, 1.0, seed=7).apply(e)
    assert np.array_equal(out.edge_times, again.edge_times)                 # same seed -> identical
    other = RandomJitter(0.05, 1.0, seed=8).apply(e)
    assert not np.array_equal(out.edge_times, other.edge_times)             # different seed -> different


def test_frequency_offset_is_a_linear_ramp():
    e = EdgeStream(np.array([1.0, 2.0, 4.0]), 0)
    assert np.allclose(FrequencyOffset(100.0).apply(e).edge_times, [1.0001, 2.0002, 4.0004])
    assert np.allclose(FrequencyOffset(-100.0).apply(e).edge_times, [0.9999, 1.9998, 3.9996])


def test_deterministic_jitter_depends_on_edge_polarity():
    e = EdgeStream(np.array([1.0, 2.0, 3.0, 4.0]), 0)                       # rise, fall, rise, fall
    assert np.allclose(DeterministicJitter(0.1, 1.0).apply(e).edge_times, [1.1, 1.9, 3.1, 3.9])
    e1 = EdgeStream(np.array([1.0, 2.0]), 1)                                # fall, rise
    assert np.allclose(DeterministicJitter(0.1, 1.0).apply(e1).edge_times, [0.9, 2.1])


def test_deterministic_jitter_swallows_one_bit_pulse():
    # +0.6 UI on the rising edge and -0.6 UI on the falling edge cross each other: the 1-UI pulse disappears.
    e = EdgeStream(np.array([0.0 + 1.0, 2.0]), 0)
    assert DeterministicJitter(0.6, 1.0).apply(e).n_edges == 0


def test_zero_amplitude_is_identity():
    e = EdgeStream(np.array([1.0, 2.5, 4.0]), 1)
    for src in (SinusoidalJitter(0.0, 1e5, 1.0), RandomJitter(0.0, 1.0), FrequencyOffset(0.0),
                DeterministicJitter(0.0, 1.0)):
        out = src.apply(e)
        assert np.array_equal(out.edge_times, e.edge_times) and out.initial_level == 1


def test_empty_stream_passes_through():
    e = EdgeStream(np.array([]), 0)
    for src in (SinusoidalJitter(0.1, 1.0, 1.0), RandomJitter(0.1, 1.0), FrequencyOffset(5.0),
                DeterministicJitter(0.1, 1.0)):
        assert src.apply(e).n_edges == 0


def test_jitter_chain_applies_in_order():
    e = EdgeStream(np.array([1.0]), 0)

    class Add:
        def __init__(self, x): self.x = x
        def apply(self, edges): return edges.shifted(self.x)

    class Double:
        def apply(self, edges): return EdgeStream(edges.edge_times * 2, edges.initial_level)

    assert JitterChain([Add(1.0), Double()]).apply(e).edge_times[0] == 4.0   # (1+1)*2
    assert JitterChain([Double(), Add(1.0)]).apply(e).edge_times[0] == 3.0   # 1*2+1
