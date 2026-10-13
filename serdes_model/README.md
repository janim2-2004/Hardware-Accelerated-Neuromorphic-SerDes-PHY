# serdes_model

Behavioral Python model of the full SERDES pipeline (TX -> channel -> RX -> CDR -> analysis).
Purpose: golden reference for the RTL, plus the software SNN-vs-baseline comparison (Bronze gate).

## Install and test
```
pip install -r serdes_model/requirements.txt
pytest serdes_model
```
Run from the repo root. Foundation blocks are implemented and tested; everything marked
`NotImplementedError` is a stub with a docstring describing what to build.

## Modelling approach
Edge-timestamp model, not a sampled waveform. A data line is an `EdgeStream`: a sorted array of
transition times plus the initial level. The receiver asks "what was the level at time t?" using a
binary search. This keeps picosecond-scale DCO steps cheap to simulate against a 40 ns bit period.

## Build order
1. Ideal chain: prbs -> serializer -> sampler -> deserializer -> ber. Must give BER = 0.
2. Impairments one at a time with a free-running RX clock (channel/*). Plot BER vs. each.
3. dco_mmcm alone, driven by a scripted command sequence.
4. Baseline CDR: pd_alexander + loop_filter + dco_mmcm + lock_detector in cdr_loop.
5. SNN detector in the same slot (float first, then fixed-point via fixedpoint/qformat).
6. analysis + sim sweeps; export golden vectors.

## Conventions
- All parameters live in `config.py` (LinkConfig). Hardware numbers (OSR, clocks, DCO step) go there only.
- Every random source takes a seeded `numpy.random.Generator` from `common/rng.py`.
- Phase detectors all implement `cdr.pd_base.PhaseDetector` so they are swappable.
- Time is in seconds (float64) unless a name ends in `_ps`, `_ns`, `_hz`.
