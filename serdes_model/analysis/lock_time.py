"""Time to first stable lock. In: lock flag trace, stable window. Out: UI count (or None if never locked).
Hardware counterpart: lock-time metric from telemetry timestamps."""
import numpy as np


def lock_time_ui(lock_flags: np.ndarray, stable_window: int = 64):
    raise NotImplementedError
