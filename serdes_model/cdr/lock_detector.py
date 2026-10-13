"""Decides locked / unlocked from the recent error history.

In: error stream.  Out: lock flag per UI.  Params: window, threshold (e.g. fewer than N non-zero errors in W UIs).
Hardware counterpart: lock flag in the telemetry interface (I4).
"""


class LockDetector:
    def __init__(self, window: int = 64, max_errors: int = 8):
        self.window, self.max_errors = window, max_errors

    def update(self, error: int) -> bool:
        raise NotImplementedError

    def reset(self):
        pass
