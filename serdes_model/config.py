"""Single source of truth for link and hardware parameters.

Keep the numbers here identical to the RTL (OSR, clock frequencies, VCO, DCO step).
Hardware counterpart: constants shared with the Verilog/VHDL parameters.
"""
from dataclasses import dataclass, field


@dataclass
class LinkConfig:
    # --- data link ---
    bit_rate_hz: float = 25e6          # 25 Mbps working target
    prbs_order: int = 7                # 7, 15, 23 or 31
    osr: int = 4                       # oversampling ratio (samples per UI)
    word_bits: int = 8                 # deserializer word width

    # --- clocking (Au V2: 100 MHz oscillator) ---
    sys_clk_hz: float = 100e6          # sample clock = bit_rate * osr when osr=4 at 25 Mbps
    vco_hz: float = 800e6              # MMCM VCO (confirm range in DS181)
    ps_steps_per_vco_period: int = 56  # MMCM dynamic phase shift resolution
    ps_handshake_cycles: int = 12      # PSEN -> PSDONE latency in PSCLK cycles (confirm in UG472)

    # --- impairments (defaults = ideal) ---
    freq_offset_ppm: float = 0.0       # TX/RX clock mismatch (channel.FrequencyOffset)
    sj_amplitude_ui: float = 0.0       # sinusoidal jitter, peak, in UI
    sj_freq_hz: float = 1e5
    rj_sigma_ui: float = 0.0           # random jitter, RMS, in UI
    dj_peak_ui: float = 0.0            # deterministic (duty-cycle) jitter, peak, in UI

    # --- TX driver (tx.TxDriver) ---
    tx_rise_time_s: float = 0.0        # finite rise time -> fixed 50% delay of rise/2
    tx_jitter_sigma_s: float = 0.0     # TX-side random jitter, RMS, seconds

    # --- channel (channel.ISIChannel / channel.ThresholdNoise) ---
    isi_bandwidth_hz: float | None = None   # first-order RC bandwidth; None = infinite (no ISI)
    noise_sigma_v: float = 0.0         # voltage noise at the RX threshold, RMS volts
    slew_v_per_s: float = 3.5e7        # edge slew at the threshold (volts -> seconds); 350 mV / 10 ns

    # --- RX front end (rx.LVDSFrontEnd) ---
    fe_threshold_offset_s: float = 0.0  # input offset expressed as time: rising late, falling early
    fe_hysteresis_s: float = 0.0        # total hysteresis expressed as time: all edges late by half of it

    # --- test control (I5) ---
    channel_bypass: bool = False       # True = jumper straight through (cfg_loopback): skip every impairment

    # --- reproducibility ---
    seed: int = 1234

    @property
    def ui_s(self) -> float:
        """Unit interval (bit period) in seconds."""
        return 1.0 / self.bit_rate_hz

    @property
    def sample_period_s(self) -> float:
        return 1.0 / self.sys_clk_hz

    @property
    def dco_step_s(self) -> float:
        """Smallest DCO phase step: 1/56 of the VCO period."""
        return (1.0 / self.vco_hz) / self.ps_steps_per_vco_period
