"""Document summarization service (English summarization).

Model: sshleifer/distilbart-cnn-6-6
License: Apache-2.0 (distilled from facebook/bart-large-cnn).
"""
from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device

MODEL_ID = "sshleifer/distilbart-cnn-6-6"


@lru_cache(maxsize=1)
def get_summarizer_pipeline():
    """Lazily build (and cache) the summarization pipeline."""
    return pipeline(
        task="summarization",
        model=MODEL_ID,
        device=get_pipeline_device(),
    )


def run_summary(original_text, do_sample=False):
    """Summarize `original_text` and return original/summary length + ratio.

    When `do_sample=True`, sampling parameters are used so that repeated
    calls (e.g. the combo "regenerate" feature) can produce different
    summaries for the same input.
    """
    summarizer = get_summarizer_pipeline()

    generate_kwargs = {"max_length": 180, "min_length": 30, "truncation": True}
    if do_sample:
        generate_kwargs.update(do_sample=True, top_p=0.9, temperature=0.8)

    summary = summarizer(original_text, **generate_kwargs)[0]["summary_text"].strip()

    summary_ratio = (
        (len(summary) / len(original_text)) * 100 if original_text else 0.0
    )

    return {
        "summary": summary,
        "original_length": len(original_text),
        "summary_length": len(summary),
        "ratio": summary_ratio,
    }