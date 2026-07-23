import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from .decorators import model_login_required
from .models import InferenceHistory
from .services.moderator import run_moderation
from .services.sentiment import run_sentiment
from .services.summarizer import run_summary

logger = logging.getLogger(__name__)

GENERIC_ERROR_MESSAGE = "모델 실행에 실패했습니다.\n잠시 후 다시 시도해주세요."

LIMITS = {
    "sentiment": (1, 1000, "분석할 문장을 입력해주세요."),
    "summarize": (100, 5000, None),
    "moderate": (1, 1000, "분석할 문장을 입력해주세요."),
}


def validate_text(raw_value, task):
    """Validate incoming text for a given task.

    Returns (clean_text, error_message). `clean_text` is None when invalid.
    """
    min_len, max_len, empty_message = LIMITS[task]

    if raw_value is None or not isinstance(raw_value, str):
        return None, "잘못된 입력 형식입니다."

    text = raw_value.strip()

    if not text:
        return None, empty_message or "입력값을 확인해주세요."

    if len(text) < min_len:
        if task == "summarize":
            return None, "요약할 문서는 100자 이상 입력해주세요."
        return None, empty_message or f"최소 {min_len}자 이상 입력해주세요."

    if len(text) > max_len:
        if task == "summarize":
            return None, "문서는 5,000자 이하로 입력해주세요."
        return None, f"입력은 {max_len}자 이하로 입력해주세요."

    return text, None


def get_recent_history(request, task):
    if not request.user.is_authenticated:
        return []
    return list(
        InferenceHistory.objects.filter(user=request.user, task=task).order_by(
            "-created_at"
        )[:5]
    )


def parse_json_body(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def index(request):
    return redirect("sentiment_page")


# ---------------------------------------------------------------------------
# Sentiment (public)
# ---------------------------------------------------------------------------
@require_GET
def sentiment_page(request):
    return render(
        request,
        "my_gpt/sentiment.html",
        {
            "model_id": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "histories": get_recent_history(request, InferenceHistory.Task.SENTIMENT),
            "active_tab": "sentiment",
        },
    )


@require_POST
def sentiment_run(request):
    payload = parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

    text, error = validate_text(payload.get("text"), "sentiment")
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        result = run_sentiment(text)
    except Exception:
        logger.exception("Sentiment inference failed.")
        return JsonResponse({"error": GENERIC_ERROR_MESSAGE}, status=502)

    if request.user.is_authenticated:
        InferenceHistory.objects.create(
            user=request.user,
            task=InferenceHistory.Task.SENTIMENT,
            input_text=text,
            output_text=result["label"],
            result_data={"label": result["label"], "score": result["score"]},
        )

    return JsonResponse({"result": result})


# ---------------------------------------------------------------------------
# Summarize (login required)
# ---------------------------------------------------------------------------
@model_login_required
@require_GET
def summarize_page(request):
    return render(
        request,
        "my_gpt/summarize.html",
        {
            "model_id": "sshleifer/distilbart-cnn-6-6",
            "histories": get_recent_history(request, InferenceHistory.Task.SUMMARIZE),
            "active_tab": "summarize",
        },
    )


@login_required
@require_POST
def summarize_run(request):
    payload = parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

    text, error = validate_text(payload.get("text"), "summarize")
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        result = run_summary(text)
    except Exception:
        logger.exception("Summarization inference failed.")
        return JsonResponse({"error": GENERIC_ERROR_MESSAGE}, status=502)

    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.SUMMARIZE,
        input_text=text,
        output_text=result["summary"],
        result_data=result,
    )

    return JsonResponse({"result": result})


# ---------------------------------------------------------------------------
# Moderate (login required)
# ---------------------------------------------------------------------------
@model_login_required
@require_GET
def moderate_page(request):
    return render(
        request,
        "my_gpt/moderate.html",
        {
            "model_id": "unitary/toxic-bert",
            "histories": get_recent_history(request, InferenceHistory.Task.MODERATE),
            "active_tab": "moderate",
        },
    )


@login_required
@require_POST
def moderate_run(request):
    payload = parse_json_body(request)
    if payload is None:
        return JsonResponse({"error": "잘못된 요청입니다."}, status=400)

    text, error = validate_text(payload.get("text"), "moderate")
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        result = run_moderation(text)
    except Exception:
        logger.exception("Moderation inference failed.")
        return JsonResponse({"error": GENERIC_ERROR_MESSAGE}, status=502)

    InferenceHistory.objects.create(
        user=request.user,
        task=InferenceHistory.Task.MODERATE,
        input_text=text,
        output_text=result["highest_label"],
        result_data=result,
    )

    return JsonResponse({"result": result})
