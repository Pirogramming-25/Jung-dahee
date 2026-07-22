"""Shared helpers for the Hugging Face pipeline service layer."""
import torch


def get_pipeline_device():
    """Return the best available compute device id for `pipeline(device=...)`.

    - 0        -> first CUDA GPU
    - "mps"    -> Apple Silicon GPU (Metal)
    - -1       -> CPU fallback
    """
    if torch.cuda.is_available():
        return 0
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return -1


def clean_text(text):
    """Normalize incoming text (strip surrounding whitespace only)."""
    if not isinstance(text, str):
        return ""
    return text.strip()
