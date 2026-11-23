import numpy as np
from serdes_model.analysis.ber import measure_ber
from serdes_model.tx.prbs import PRBS


def test_clean_prbs_has_zero_ber():
    for order in (7, 15, 23, 31):
        bits = PRBS(order).next_bits(1_000)
        assert measure_ber(bits, order) == (0, 1_000 - order, 0.0)


def test_sync_works_from_any_point_in_the_stream():
    # Checker must lock regardless of where in the sequence it starts (no knowledge of TX seed/delay).
    bits = PRBS(7).next_bits(1_000)[137:]
    assert measure_ber(bits, 7)[0] == 0


def test_counts_injected_errors():
    bits = PRBS(15).next_bits(2_000)
    bits[500] ^= 1
    bits[1500] ^= 1
    errors, compared, ber = measure_ber(bits, 15)
    assert errors == 2 and compared == 2_000 - 15 and ber == errors / compared


def test_all_zero_stream_reports_total_failure():
    assert measure_ber(np.zeros(100, dtype=np.uint8), 7)[2] == 1.0
