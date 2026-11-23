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

## Status
| Step | State |
|---|---|
| 1. Ideal chain (prbs, serializer, sampler, deserializer, ber, run_link) | done |
| 2. Channel impairments (RJ, SJ, DJ, ppm, ISI, noise, TX driver, RX front end) | done (Phase 1) |
| 3. DCO model | stub |
| 4. Baseline CDR (Alexander, loop filter, lock detector, cdr_loop) | stub |
| 5. SNN detector | stub |
| 6. Analysis sweeps / golden vectors | `sim.sweeps.sweep` and `plot_ber_vs_impairment` done; rest stub |

## Channel model (Phase 1)
Every impairment is an `EdgeStream -> EdgeStream` block that shifts edge times. `channel.chain.build_channel(cfg)`
assembles the enabled blocks in this order (an all-default config gives an empty chain = ideal wire):

`TxDriver -> SinusoidalJitter -> RandomJitter -> DeterministicJitter -> FrequencyOffset -> ISIChannel -> ThresholdNoise -> LVDSFrontEnd`

- Parameters are `LinkConfig` fields (`sj_*`, `rj_sigma_ui`, `dj_peak_ui`, `freq_offset_ppm`, `tx_*`,
  `isi_bandwidth_hz`, `noise_sigma_v`, `slew_v_per_s`, `fe_*`). `channel_bypass=True` skips all of them.
- Frequency offset lives only in the channel (`FrequencyOffset`); `run_link` no longer passes ppm to the serializer.
- A pulse that jitter squeezes to zero or negative width is removed (`EdgeStream.shifted`, `swallow_crossed=True`).
- ISI is a first-order RC with a 50% comparator: short pulses shrink (the trailing edge moves early) and very
  short pulses vanish. By default the constant tau*ln2 latency is subtracted so only the pattern-dependent shift remains.
- Each random source uses its own RNG stream (`common/rng.py`), so enabling one never changes another's draws.
- Reproduce the gate figure: `python -m serdes_model.sim.ber_vs_impairments out.png`.
- Without a CDR the receiver is free-running: a ppm offset starts slipping bits once `ppm * 1e-6 * n_bits`
  reaches about 0.5 UI, so the BER cliff for that sweep moves with `n_bits`.
