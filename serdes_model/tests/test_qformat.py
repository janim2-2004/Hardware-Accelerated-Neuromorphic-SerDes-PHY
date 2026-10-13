import numpy as np
from serdes_model.fixedpoint.qformat import QFormat


def test_round_and_saturate():
    q = QFormat(total_bits=8, frac_bits=4)               # lsb 1/16, range about [-8, 7.9375]
    assert q.quantize(0.03) == 0.0
    assert q.quantize(0.04) == 0.0625
    assert q.quantize(100.0) == q.max_value
    assert q.quantize(-100.0) == q.min_value


def test_to_int_codes():
    q = QFormat(8, 4)
    assert list(q.to_int(np.array([1.0, -1.0]))) == [16, -16]
