"""LVDS receiver: input offset, hysteresis, finite bandwidth.

In: EdgeStream.  Out: EdgeStream.  Params: threshold_offset_v, hysteresis_v.
Hardware counterpart: IBUFDS.
"""
from serdes_model.common.signals import EdgeStream


class LVDSFrontEnd:
    def __init__(self, threshold_offset_s: float = 0.0, hysteresis_s: float = 0.0):
        self.threshold_offset_s = threshold_offset_s   # modelled as a fixed edge delay for now
        self.hysteresis_s = hysteresis_s

    def apply(self, edges: EdgeStream) -> EdgeStream:
        raise NotImplementedError
