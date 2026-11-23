import numpy as np
from serdes_model.common.signals import EdgeStream
from serdes_model.rx.sampler import Sampler
from serdes_model.tx.serializer import serialize


def test_serialize_edge_positions():
    e = serialize(np.array([0, 0, 1, 1, 0]), ui_s=1.0)
    assert e.initial_level == 0
    assert list(e.edge_times) == [2.0, 4.0]


def test_serialize_tx_ppm_stretches_ui():
    e = serialize(np.array([0, 1]), ui_s=1.0, tx_ppm=1e6)      # +100% -> UI doubles
    assert list(e.edge_times) == [2.0]


def test_serialize_round_trips_through_sampler():
    bits = np.array([1, 0, 0, 1, 1, 1, 0, 1, 0, 0], dtype=np.uint8)
    e = serialize(bits, ui_s=1.0)
    s = Sampler().sample(e, np.arange(len(bits)) + 0.5)
    assert np.array_equal(s.bits, bits)


def test_sampler_aperture_is_reproducible_and_local():
    e = EdgeStream(np.array([10.0]), initial_level=0)
    t = np.array([5.0, 10.0, 15.0])                 # only the middle sample sits on the edge
    a = Sampler(aperture_s=1.0, seed=3).sample(e, t).bits
    b = Sampler(aperture_s=1.0, seed=3).sample(e, t).bits
    assert np.array_equal(a, b)                     # same seed -> same metastable outcome
    assert a[0] == 0 and a[2] == 1                  # samples away from the edge stay deterministic
