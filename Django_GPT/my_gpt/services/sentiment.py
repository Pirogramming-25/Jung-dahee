"""Sentiment analysis service (English text-classification).

Model: cardiffnlp/twitter-roberta-base-sentiment-latest
License: see the model card on Hugging Face (non-commercial research use
per the original TimeLMs / TweetEval terms - check before commercial use).
"""
from functools import lru_cache

from transformers import pipeline

from .common import get_pipeline_device

MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# The model's raw labels are lowercase ("negative", "neutral", "positive").
_LABEL_DISPLAY = {
    "negative": "Negative",
    "neutral": "Neutral",
    "positive": "Positive",
}


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """Lazily build (and cache) the sentiment-analysis pipeline."""
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        top_k=None,
        device=get_pipeline_device(),
    )


def run_sentiment(text):
    """Run sentiment analysis on `text` and return a structured result."""
    classifier = get_sentiment_pipeline()
    raw_scores = classifier(text)[0]

    all_scores = [
        {
            "label": _LABEL_DISPLAY.get(item["label"].lower(), item["label"]),
            "score": float(item["score"]),
        }
        for item in raw_scores
    ]
    all_scores.sort(key=lambda item: item["score"], reverse=True)
    top = all_scores[0]

    return {
        "label": top["label"],
        "score": top["score"],
        "all_scores": all_scores,
    }
