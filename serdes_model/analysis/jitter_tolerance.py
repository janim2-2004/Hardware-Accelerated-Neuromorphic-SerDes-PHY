"""Jitter tolerance: for each SJ frequency, the largest amplitude at which BER stays below target.

In: a function that runs the link for (sj_amp_ui, sj_freq_hz) and returns BER; sweep grids.
Out: array of (freq, max_amp_ui) = the tolerance mask. Use bisection per frequency.
Hardware counterpart: M4/M3 jitter-tolerance sweep.
"""


def jitter_tolerance(run_link, freqs_hz, amp_lo_ui=0.0, amp_hi_ui=2.0, ber_target=1e-9):
    raise NotImplementedError
