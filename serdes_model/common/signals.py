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

    def shifted(self, dt: np.ndarray) -> "EdgeStream":
        """Return a copy with each edge moved by dt (scalar or per-edge array). Re-sorts if edges cross."""
        times = self.edge_times + dt
        return EdgeStream(np.sort(times), self.initial_level)


@dataclass
class SampleStream:
    times: np.ndarray           # seconds
    bits: np.ndarray            # uint8 0/1, same length as times
