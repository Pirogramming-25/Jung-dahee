"""Toxic / harmful language detection service (English, multi-label).

Model: unitary/toxic-bert
License: Apache-2.0.
"""
from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device

MODEL_ID = "unitary/toxic-bert"


@lru_cache(maxsize=1)
def get_moderator_pipeline():
    """Lazily build (and cache) the toxicity classification pipeline."""
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        top_k=None,
        device=get_pipeline_device(),
    )


def run_moderation(text):
    """Run multi-label toxicity classification on `text`."""
    classifier = get_moderator_pipeline()
    raw_scores = classifier(text)[0]

    all_scores = [
        {"label": item["label"], "score": float(item["score"])}
        for item in raw_scores
    ]
    all_scores.sort(key=lambda item: item["score"], reverse=True)
    top = all_scores[0]

    return {
        "highest_label": top["label"],
        "highest_score": top["score"],
        "all_scores": all_scores,
    }