"""EdgeStream.shifted / levels_after_edges: crossed edges must annihilate, not produce phantom pulses."""
import numpy as np
from serdes_model.common.signals import EdgeStream


def test_levels_after_edges_alternate():
    assert list(EdgeStream(np.array([1.0, 2.0, 3.0]), 0).levels_after_edges()) == [1, 0, 1]
    assert list(EdgeStream(np.array([1.0, 2.0, 3.0]), 1).levels_after_edges()) == [0, 1, 0]


def test_uncrossed_shift_is_plain_addition():
    e = EdgeStream(np.array([1.0, 2.0, 3.0, 4.0]), 0).shifted(0.1)
    assert np.allclose(e.edge_times, [1.1, 2.1, 3.1, 4.1])


def test_crossed_pair_is_swallowed_and_parity_kept():
    e = EdgeStream(np.array([1.0, 1.2, 3.0]), 0).shifted(np.array([0.3, 0.0, 0.0]))   # -> 1.3, 1.2, 3.0
    assert list(e.edge_times) == [3.0]                       # the zero-width pulse is gone
    assert list(e.level_at([1.25, 2.0, 3.5])) == [0, 0, 1]   # line stays low, final level still correct


def test_edges_landing_on_the_same_time_cancel():
    assert EdgeStream(np.array([1.0, 2.0]), 0).shifted(np.array([1.0, 0.0])).n_edges == 0


def test_swallowing_cascades():
    # shifted times [1, 5, 3, 0.5]: 3 cancels 5, then 0.5 cancels 1 -> nothing left
    e = EdgeStream(np.array([1.0, 2.0, 3.0, 4.0]), 0).shifted(np.array([0.0, 3.0, 0.0, -3.5]))
    assert e.n_edges == 0
    # shifted times [1, 2, 1.5, 4]: 1.5 cancels 2 -> rise at 1, fall at 4 (polarities preserved)
    e = EdgeStream(np.array([1.0, 2.0, 3.0, 4.0]), 0).shifted(np.array([0.0, 0.0, -1.5, 0.0]))
    assert list(e.edge_times) == [1.0, 4.0]


def test_legacy_sort_mode():
    e = EdgeStream(np.array([1.0, 1.2, 3.0]), 0).shifted(np.array([0.3, 0.0, 0.0]), swallow_crossed=False)
    assert list(e.edge_times) == [1.2, 1.3, 3.0]
