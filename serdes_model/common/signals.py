"""Data containers passed between blocks.

EdgeStream   - a binary line as sorted transition times (seconds) plus the level before the first edge.
SampleStream - sampled bits with the time each sample was taken.
Hardware counterpart: wires and registers.
"""
from dataclasses import dataclass
import numpy as np


@dataclass
class EdgeStream:
    edge_times: np.ndarray      # sorted, seconds
    initial_level: int = 0      # level before the first edge (0 or 1)

    def level_at(self, t):
        """Line level at time(s) t (scalar or array). Binary search, O(log n) per query."""
        t = np.asarray(t, dtype=float)
        n_edges = np.searchsorted(self.edge_times, t, side="right")
        return (self.initial_level ^ (n_edges & 1)).astype(np.uint8)

    @property
    def n_edges(self) -> int:
        return len(self.edge_times)

    def levels_after_edges(self) -> np.ndarray:
        """Line level just AFTER each edge (1 = rising edge, 0 = falling edge). Edges strictly alternate,
        so edge k leaves the line at initial_level ^ ((k + 1) mod 2). Used by polarity-dependent blocks."""
        k = np.arange(self.n_edges)
        return (self.initial_level ^ ((k + 1) & 1)).astype(np.uint8)

    def shifted(self, dt, swallow_crossed: bool = True) -> "EdgeStream":
        """Return a copy with each edge moved by dt (scalar or per-edge array).

        Edges are shifted in their original order. If jitter pushes an edge onto or past its neighbour, the
        pulse between them has zero or negative width and physically does not exist: with
        swallow_crossed=True both edges are removed (cascading, so a swallowed pulse can expose a new
        crossing). With swallow_crossed=False the times are just re-sorted (legacy behaviour).
        """
        times = np.asarray(self.edge_times + dt, dtype=float)
        # Fast path (almost always taken): order intact, nothing crossed.
        if len(times) < 2 or np.all(times[1:] > times[:-1]):
            return EdgeStream(times, self.initial_level)
        if not swallow_crossed:
            return EdgeStream(np.sort(times), self.initial_level)
        # Slow path: stack walk. A new edge at or before the previous kept edge cancels it (pair removed).
        # Removing a pair keeps edge parity, so the polarity of every surviving edge stays correct.
        kept = []
        for t in times.tolist():
            if kept and t <= kept[-1]:
                kept.pop()
            else:
                kept.append(t)
        return EdgeStream(np.array(kept, dtype=float), self.initial_level)


@dataclass
class SampleStream:
    times: np.ndarray           # seconds
    bits: np.ndarray            # uint8 0/1, same length as times
