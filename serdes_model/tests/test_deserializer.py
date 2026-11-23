import numpy as np
from serdes_model.rx.deserializer import Deserializer


def test_msb_first_words():
    bits = np.array([1, 0, 0, 0, 0, 0, 0, 1,   0, 1, 0, 1, 0, 1, 0, 1], dtype=np.uint8)
    d = Deserializer(8, msb_first=True)
    words = d.deserialize(bits)
    assert words.shape == (2, 8)
    assert list(d.to_ints(words)) == [0b10000001, 0b01010101]


def test_lsb_first_reverses_bit_order():
    bits = np.array([1, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8)      # first-arrived bit is the LSB
    d = Deserializer(8, msb_first=False)
    assert list(d.to_ints(d.deserialize(bits))) == [0b00000011]


def test_partial_trailing_word_dropped():
    assert Deserializer(8).deserialize(np.ones(19, dtype=np.uint8)).shape == (2, 8)
    assert Deserializer(8).deserialize(np.ones(3, dtype=np.uint8)).shape == (0, 8)
