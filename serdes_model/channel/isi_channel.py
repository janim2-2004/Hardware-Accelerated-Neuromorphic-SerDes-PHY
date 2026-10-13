"""Bandwidth-limited channel producing pattern-dependent edge shifts (ISI).

In: EdgeStream.  Out: EdgeStream.  Params: bandwidth_hz (or time constant), edge spacing dependence.
Hardware counterpart: jumper wires / board traces. Expect little ISI at 25 Mbps; keep it for sweeps.
"""
from serdes_model.common.signals import EdgeStream


class ISIChannel:
    def __init__(self, bandwidth_hz: float):
        self.bandwidth_hz = bandwidth_hz

    def apply(self, edges: EdgeStream) -> EdgeStream:
        # TODO: first-order RC: closely spaced edges shift later (partial swing). Start simple.
        raise NotImplementedError
