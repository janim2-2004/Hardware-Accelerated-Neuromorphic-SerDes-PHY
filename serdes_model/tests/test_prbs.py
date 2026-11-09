import numpy as np
import pytest
from serdes_model.tx.prbs import PRBS

#Generates two periods of a PRBS sequence and checks that the first period is equal to the second period, and that the number of 1s is one more than the number of 0s
#Orders 23 and 31 are not tested because the full period takes too long to run
@pytest.mark.parametrize("order", [7, 15])
def test_period_is_maximal(order):
    n = 2 ** order - 1
    bits = PRBS(order).next_bits(2 * n)
    assert np.array_equal(bits[:n], bits[n:])          # repeats after 2^n - 1
    assert bits[:n].sum() == 2 ** (order - 1)           # one more 1 than 0s

#Generate a PRBS sequence, reset the generator, and check that the same sequence is generated again
def test_reset_reproduces():
    p = PRBS(7)
    a = p.next_bits(50)
    p.reset()
    assert np.array_equal(a, p.next_bits(50))
