"""Bandwidth-limited channel producing pattern-dependent edge shifts (ISI).

In: EdgeStream.  Out: EdgeStream.  Params: bandwidth_hz (or time constant), edge spacing dependence.
Hardware counterpart: jumper wires / board traces. Expect little ISI at 25 Mbps; keep it for sweeps.

Responsibility: model the line as a first-order RC low-pass (tau = 1/(2*pi*BW)) driven by the ideal
0/1 edges, with a comparator at 50% of the swing.

  * A lone edge needs tau*ln(2) to reach 50% (a fixed latency; removed by default).
  * If the previous edge was recent, the line has not settled, so the next edge STARTS CLOSER TO THE
    THRESHOLD and crosses EARLIER than a lone edge: short pulses shrink (the diagram's "short pulses
    cross early"). For a pulse of width w the trailing edge moves by tau*ln(1 - exp(-w/tau)) (< 0).
  * If a pulse is so short that the line never reaches 50%, it vanishes: both edges are removed.

The state is propagated edge to edge, so the shift depends on the whole recent edge history (ISI).
"""
import math

import numpy as np

from serdes_model.common.signals import EdgeStream


class ISIChannel:
    def __init__(self, bandwidth_hz: float, include_fixed_delay: bool = False):
        """include_fixed_delay=False reports only the pattern-dependent shift (the constant tau*ln2 latency of
        an RC at a 50% threshold is subtracted). True keeps the absolute delay."""
        if bandwidth_hz <= 0:
            raise ValueError("bandwidth_hz must be positive")
        self.bandwidth_hz = bandwidth_hz
        self.include_fixed_delay = include_fixed_delay

    @property
    def tau_s(self) -> float:
        return 1.0 / (2.0 * math.pi * self.bandwidth_hz)

    def apply(self, edges: EdgeStream) -> EdgeStream:
        n = edges.n_edges
        if n == 0:
            return edges
        tau = self.tau_s
        times = edges.edge_times.tolist()
        targets = edges.levels_after_edges().tolist()       # level the input heads to after each edge

        v = float(edges.initial_level)                      # normalized line voltage (0..1), starts settled
        out = []                                            # times where the line crosses 50%
        for k in range(n):
            t_k, goal = times[k], float(targets[k])
            t_next = times[k + 1] if k + 1 < n else math.inf

            # The comparator can only flip if the line is on the far side of 50% from where it is heading.
            gap = abs(goal - v)
            if gap > 0.5:
                t_cross = t_k + tau * math.log(2.0 * gap)   # solve goal + (v-goal)*exp(-dt/tau) = 0.5
                if t_cross < t_next:                        # before the input changes again?
                    out.append(t_cross)
                # else: the pulse ended first -> the transition never happens (swallowed)

            if k + 1 < n:                                   # let the RC settle toward `goal` until the next edge
                v = goal + (v - goal) * math.exp(-(t_next - t_k) / tau)

        crossings = np.array(out, dtype=float)
        if not self.include_fixed_delay:
            crossings = crossings - tau * math.log(2.0)     # remove the constant 50%-point latency
        return EdgeStream(crossings, edges.initial_level)
