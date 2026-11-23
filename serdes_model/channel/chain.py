"""Builds the impairment chain for a LinkConfig.

Hardware counterpart: the test-config (I5) registers that select which impairments are active.

Responsibility: turn LinkConfig numbers into the ordered list of blocks from the channel diagram:
  TX driver -> SJ -> RJ -> DJ -> frequency offset -> ISI -> threshold noise -> RX front end
Only blocks whose parameters are non-zero are included, so an all-default config yields an empty
chain (the identity) and channel_bypass=True forces that regardless of the other fields.
"""
from serdes_model.channel.isi_channel import ISIChannel
from serdes_model.channel.jitter_sources import (
    DeterministicJitter, FrequencyOffset, JitterChain, RandomJitter, SinusoidalJitter)
from serdes_model.channel.noise import ThresholdNoise
from serdes_model.config import LinkConfig
from serdes_model.rx.frontend import LVDSFrontEnd
from serdes_model.tx.tx_driver import TxDriver


def build_channel(cfg: LinkConfig) -> JitterChain:
    if cfg.channel_bypass:                       # cfg_loopback: wire straight from serializer to front end
        return JitterChain([])

    ui, seed = cfg.ui_s, cfg.seed
    blocks = []
    if cfg.tx_rise_time_s or cfg.tx_jitter_sigma_s:
        blocks.append(TxDriver(cfg.tx_rise_time_s, cfg.tx_jitter_sigma_s, seed))
    if cfg.sj_amplitude_ui:
        blocks.append(SinusoidalJitter(cfg.sj_amplitude_ui, cfg.sj_freq_hz, ui))
    if cfg.rj_sigma_ui:
        blocks.append(RandomJitter(cfg.rj_sigma_ui, ui, seed))
    if cfg.dj_peak_ui:
        blocks.append(DeterministicJitter(cfg.dj_peak_ui, ui))
    if cfg.freq_offset_ppm:
        blocks.append(FrequencyOffset(cfg.freq_offset_ppm))
    if cfg.isi_bandwidth_hz:
        blocks.append(ISIChannel(cfg.isi_bandwidth_hz))
    if cfg.noise_sigma_v:
        blocks.append(ThresholdNoise(cfg.noise_sigma_v, cfg.slew_v_per_s, seed))
    if cfg.fe_threshold_offset_s or cfg.fe_hysteresis_s:
        blocks.append(LVDSFrontEnd(cfg.fe_threshold_offset_s, cfg.fe_hysteresis_s))
    return JitterChain(blocks)
