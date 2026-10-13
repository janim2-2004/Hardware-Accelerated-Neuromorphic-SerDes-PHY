import numpy as np
import pytest
from serdes_model.tx.prbs import PRBS


@pytest.mark.parametrize("order", [7, 15])
def test_period_is_maximal(order):
    n = 2 ** order - 1
    bits = PRBS(order).next_bits(2 * n)
    assert np.array_equal(bits[:n], bits[n:])          # repeats after 2^n - 1
    assert bits[:n].sum() == 2 ** (order - 1)           # one more 1 than 0s


def test_reset_reproduces():
    p = PRBS(7)
    a = p.next_bits(50)
    p.reset()
    assert np.array_equal(a, p.next_bits(50))
