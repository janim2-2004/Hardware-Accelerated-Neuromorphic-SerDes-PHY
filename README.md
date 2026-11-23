# Hardware-Accelerated Neuromorphic SerDes PHY

**An FPGA-based Clock and Data Recovery (CDR) loop that uses a spiking neural network (SNN) as its phase detector.**

Serial links use a CDR to pull a sampling clock out of the incoming data. On modern FPGAs the CDR is
hardened inside the multi-Gbps transceivers and can't be changed. This project builds a complete
SerDes link and CDR loop in programmable fabric on an Artix-7. It replaces the conventional phase
detector with a small network of leaky integrate-and-fire (LIF) neurons, then benchmarks it against a
conventional Alexander bang-bang detector running in the same loop on the same hardware.

The result is a working hardware proof of concept and a measured comparison against a known baseline.

---

## Motivation

- Hardened transceiver CDRs leave no room to experiment with other timing-recovery designs on standard hardware.
- Event-driven (neuromorphic) computing has shown efficiency gains on custom silicon (Intel Loihi, IBM TrueNorth), but it hasn't been evaluated for timing recovery.
- The literature we reviewed shows **no spiking-neuron CDR and none on synchronous FPGA fabric**. MediaTek has patented a CDR that uses a conventional (non-spiking) neural network.

## Target specifications

Targets are provisional and will be finalized at the Bronze gate (week 10).

| Metric | Target | Measured by |
|---|---|---|
| Data rate | 25–50 Mbps sustained lock (100 Mbps stretch) | PRBS over LVDS loopback |
| Bit error rate | ≤ 1e-9 while locked | BER checker, ≥ 3e9 bits |
| Jitter tolerance | ≥ 0.2 UI peak-to-peak, equal to or better than baseline | Swept injected jitter, both loops |
| Lock time | ≤ 1000 bit periods after reset | Telemetry timestamps |
| Resource use | LUT / FF / BRAM / DSP, SNN vs. baseline | Vivado utilization report |
| Power | Dynamic power, SNN vs. baseline | Vivado estimate + measured current |
| Fixed-point accuracy | Lock time within 5% of the floating-point model | Golden-vector comparison |

The data-rate ceiling is set by the SNN pipeline clock and the oversampling ratio.

## System architecture

```
 TX (FPGA fabric)                                          RX (FPGA fabric)
 ┌──────────────┐  ┌──────────────┐  ┌────────────┐  ┌────────┐     ┌──────────┐  ┌──────────────┐
 │ PRBS gen     │→ │ Line encoder │→ │ Serializer │→ │ OBUFDS │──┐  │ IBUFDS   │→ │ Loopback mux │
 │ (7/15/23/31) │  │ (optional)   │  │            │  │ LVDS   │  │  └──────────┘  └──────┬───────┘
 └──────────────┘  └──────────────┘  └────────────┘  └────────┘  │                       ↓
                                                                 │  ┌───────────────────────────┐
     Option A: external LVDS loopback (jumper wires, real ISI) ──┘  │ Oversampling capture OSR 4│
     Option B: internal RTL loopback (tx_serial → RX mux)           └────────────┬──────────────┘
                                                                                 ↓
                                     ┌───────────────────────────────────────────────────────┐
                                     │ CDR loop: phase detector slot (Alexander | SNN)        │
                                     │ → loop filter → DCO (MMCM dynamic phase shift) ─┐      │
                                     │   lock detector               sample_clk ←───────┘     │
                                     └────────────────────────┬──────────────────────────────┘
                                                              ↓
                                   Deserializer 1:8 → word aligner / line decoder (optional) → rx_data
                                                 └→ BER checker → UART telemetry → host
```

- Both sides run from the board's single 100 MHz oscillator through MMCMs (TX bit clock 25 MHz, RX sample clock 100 MHz = 4× oversampling).
- Frequency offset and jitter are injected deliberately by a jitter injector (second detuned MMCM or TX MMCM phase modulation).
- The phase detector is a **swappable slot**, so both detectors drop into the same loop and are compared under identical conditions.

Detailed block diagrams and per-module flowcharts are in [`Diagrams/`](Diagrams):
[TX datapath](Diagrams/Tx%20Datapath), [RX datapath](Diagrams/Rx%20Datapath), [CDR](Diagrams/CDR),
[Channel model](Diagrams/Channel%20Model), and the
[TX–RX loopback overview](Diagrams/serdes_datapath_2-6%20TX-RX%20loopback%20(side%20by%20side).png).

## Workstreams

| Module | Scope |
|---|---|
| **M1 – SNN phase detector** | Python SNN model and fixed-point sweep; RTL for spike encoder, LIF neurons and decoder. Done when the model converges, RTL matches golden vectors, and timing closes. |
| **M2 – CDR datapath and baseline** | ISERDES front end, Alexander detector, lock detector, loop filter and DCO controller RTL. Done when the baseline locks on hardware and the detector slot swaps cleanly. |
| **M3 – Test, verification and analysis** | Python channel and baseline models, PRBS transmitter, BER checker, UART telemetry, sweep scripts, regression for both detectors, results analysis. |
| **M4 – Physical layer and loop dynamics** | MMCM clocking, dynamic-phase-shift DCO, loop filter design, LVDS signal integrity, jitter injection, scope and power measurements. |

**Datapath ownership:** the main TX and RX datapaths (PRBS → line code → serializer → LVDS out, and
LVDS in → capture → deserializer → word align / line decode) are one workstream. The CDR loop and the SNN
are owned by other team members.

Modules talk through five interfaces frozen in Period 1: **sample stream, phase error, DCO command,
telemetry, test configuration**.

## Hardware and tools

- **Board:** Alchitry Au V2 (Xilinx Artix-7 XC7A35T), 100 MHz on-board oscillator
- **I/O:** LVDS_25 differential pairs on header pins, external jumper-wire loopback
- **Clocking:** MMCME2 (VCO 800 MHz), dynamic phase shift as the DCO (~22 ps steps)
- **Tools:** Vivado WebPACK, Python 3 (NumPy, SciPy, Matplotlib, pytest), lab oscilloscope
- **Budget:** ~$250 CAD

## Repository layout

```
Diagrams/                 Block diagrams and module flowcharts (draw.io source + PNG exports)
docs/                     Implementation guides
serdes_model/             Python behavioral model: golden reference for the RTL
  config.py               LinkConfig: single source of truth for link/hardware parameters
  common/                 EdgeStream / SampleStream containers, seeded RNG
  tx/                     PRBS, line encoder, serializer, TX driver
  channel/                Jitter sources, ISI channel, noise
  rx/                     Front end, sampler, deserializer, word aligner, line decoder
  cdr/                    Phase detectors (Alexander, SNN), loop filter, DCO, lock detector
  fixedpoint/             Q-format quantization for RTL bit widths
  analysis/               BER, jitter tolerance, lock time, plots
  sim/                    Full-link runner and parameter sweeps
  export/                 Golden-vector export for RTL testbenches
  tests/                  pytest suite
```

See [`serdes_model/README.md`](serdes_model/README.md) for the modelling approach (edge-timestamp
model), build order and coding conventions.

## Quick start

From the repository root:

```bash
pip install -r serdes_model/requirements.txt
```

```bash
pytest serdes_model -v
```

## Milestones

Thirteen two-week periods, October to March, each ending with an instructor meeting.

| Gate | Week | Deliverable |
|---|---|---|
| Period 1 | 1–2 | Interfaces frozen, toolchain confirmed on board, clocking plan |
| Period 3 | 5–6 | SNN converges in software (go/no-go) |
| **Bronze** | 10 | Software models, SNN-vs-baseline curves, fixed-point spec |
| Period 6 | 11–12 | Baseline CDR locked on hardware |
| **Silver** | 18 | Both loops simulated and verified; SNN RTL passes golden vectors |
| Period 11 | 21–22 | Both loops at 25 Mbps; first comparative dataset |
| **Gold** | 24 | Final comparative metrics: lock time, jitter tolerance, resources, power |
| Period 13 | 25–26 | Final report, poster, demo, code handover |

**Contingency:** if the SNN doesn't converge in Period 3, the team documents the failure analysis and
continues the baseline hardware path. Gold then becomes a baseline characterization plus a documented negative result.

## Deliverables

1. Python SNN model with jitter-tolerance validation
2. RTL for the SNN detector (M1) and baseline CDR (M2)
3. Test infrastructure (M3, M4) and simulation results for both loops
4. FPGA bitstream demonstrating a locked SNN CDR over LVDS loopback
5. Comparative report: lock time, jitter tolerance, resources, power
6. Final report and demo
