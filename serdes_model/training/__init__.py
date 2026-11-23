"""Training code for the SNN phase detector. PyTorch lives in this package and nowhere else.

Rule: nothing outside serdes_model/training/ may import torch. The numpy model in serdes_model/cdr/snn/
is the golden reference that mirrors the RTL; this package trains weights and exports them into that model.

Files (in the order they are used):
    splits.py          train/val/test splits at the stream level, named test conditions
    model.py           torch SNN (same equations as the numpy model)
    surrogate.py       surrogate-gradient spike function
    quant.py           quantization-aware training helpers
    losses.py          class-weighted loss
    train.py           training loop
    evaluate.py        metrics, per-condition slices, baselines (numpy only)
    export_weights.py  checkpoint -> JSON for the numpy model / RTL
"""