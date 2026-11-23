"""Torch version of the SNN phase detector. Same equations as the numpy model in cdr/snn/.

Pipeline for one window [prev, s0, s1, s2, s3]:
    encoder   x = |neighbor differences|              (4 lines: gaps A, B, C, D)
    layer     v = W x ;  s = spike(v - threshold)     (neurons 0..n_early-1 are early, the rest are late)
    decoder   y = (late spikes) - (early spikes)      (soft value used for the loss; round and clip to -1/0/+1 to score)

Sign convention matches cdr/pd_base.py: negative = sampling early, positive = late, 0 = hold.

Start state: weights = hand-derived truth table (early neurons listen to gap B, late neurons to gap D) plus a
little noise, so training starts from a known-good network. Threshold 0.5 against weights of 1.0 leaves margin
for that noise.

IMPORTANT: this must stay numerically identical to the numpy model. tests/test_torch_numpy_parity.py enforces it.
"""
import torch
import torch.nn as nn

from serdes_model.fixedpoint.qformat import QFormat
# from serdes_model.training.quant import fake_quantize
# from serdes_model.training.surrogate import spike_fn

N_IN = 4
GAP_A, GAP_B, GAP_C, GAP_D = range(4)      # column order of the encoder output


def encode(windows: torch.Tensor) -> torch.Tensor:
    "[B, 5] bits -> [B, 4] spikes: 1 where neighboring samples differ (rising/falling is ignored)."
    w = windows.float()
    return (w[:, 1:] - w[:, :-1]).abs()


def handset_weights(n_early: int, n_late: int) -> torch.Tensor:
    "Hand-derived starting weights: early neurons fire on a transition in gap B, late neurons on gap D."
    W = torch.zeros(n_early + n_late, N_IN)
    W[:n_early, GAP_B] = 1.0
    W[n_early:, GAP_D] = 1.0

    """
    W = [0, 1, 0, 0
         0, 1, 0, 0
         0, 0, 0, 1
         0, 0, 0, 1]
    """
    return W

class SNNPhaseDetector(nn.Module):
    def __init__(self, n_early: int = 2, n_late: int = 2, threshold: float = 0.5, leak: float = 0.0,
                 k: float = 25.0, qformat: QFormat | None = None, init_noise: float = 0.05):
        super().__init__()
        self.n_early, self.n_late = n_early, n_late
        self.threshold, self.leak, self.k, self.qformat = threshold, leak, k, qformat
        W0 = handset_weights(n_early, n_late)
        self.weight = nn.Parameter(W0 + init_noise * torch.randn_like(W0))   # the only learned parameters

    def effective_weight(self) -> torch.Tensor:
        "Weights the forward pass actually uses: quantized if a QFormat is set, else full precision."
        return fake_quantize(self.weight, self.qformat) if self.qformat is not None else self.weight

    def forward(self, windows: torch.Tensor) -> torch.Tensor:
        "One timestep per window, membrane reset every window (so the leak has no effect). Returns soft y [B]."
        x = encode(windows)                                       # [B, 4]
        v = x @ self.effective_weight().T                         # [B, n_neurons]
        s = spike_fn(v - self.threshold, self.k)                  # [B, n_neurons]
        return s[:, self.n_early:].sum(dim=1) - s[:, :self.n_early].sum(dim=1)

    def forward_sequence(self, windows_seq: torch.Tensor) -> torch.Tensor:
        """
        Temporal variant: [T, B, 5] consecutive windows, membrane carried across windows (leak matters).

        v[t] = leak * v[t-1] * (1 - s[t-1]) + W x[t]. Returns y for every step, [T, B].
        TODO: not used by train.py yet; needs sequence data from the dataset builder.
        """
        W = self.effective_weight()
        T, B, _ = windows_seq.shape
        v = torch.zeros(B, W.shape[0], device=windows_seq.device)
        s = torch.zeros_like(v)
        out = []
        for t in range(T):
            v = self.leak * v * (1.0 - s) + encode(windows_seq[t]) @ W.T
            s = spike_fn(v - self.threshold, self.k)
            out.append(s[:, self.n_early:].sum(dim=1) - s[:, :self.n_early].sum(dim=1))
        return torch.stack(out)