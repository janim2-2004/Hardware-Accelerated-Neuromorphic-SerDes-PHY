import numpy as np
from serdes_model.common.signals import EdgeStream
from serdes_model.config import LinkConfig


def test_level_at():
    e = EdgeStream(np.array([1.0, 2.0, 4.0]), initial_level=0)
    assert list(e.level_at([0.5, 1.5, 2.5, 4.5])) == [0, 1, 0, 1]


def test_config_derived():
    c = LinkConfig()
    assert abs(c.ui_s - 40e-9) < 1e-15
    assert 20e-12 < c.dco_step_s < 25e-12      # ~22 ps with 800 MHz VCO
