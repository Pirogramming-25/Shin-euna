import json
import logging

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import model_login_required
from .models import InferenceHistory
from .services.sentiment import run_sentiment_pipeline
from .services.summarizer import run_summarizer_pipeline
from .services.moderator import run_moderator_pipeline
from .services.combo import run_combo_pipeline, build_verdict

logger = logging.getLogger(__name__)


def main(request):
    return redirect("my_gpt:sentiment")


def _extract_text(request):
    """
    요청 본문에서 분석 대상 텍스트를 꺼내는 공용 함수.

    JSON body(fetch) 또는 application/x-www-form-urlencoded(form) 둘 다 지원한다.
    반환값은 항상 앞뒤 공백이 제거된 문자열이며, 값이 없으면 빈 문자열("")을 반환한다.
    """
    if request.content_type == "application/json":
        try:
            payload = json.loads(request.body or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return ""
        text = payload.get("text", "")
    else:
        text = request.POST.get("text", "")

    return text.strip()


def _validate_length(text, min_len, max_len):
    """길이가 [min_len, max_len] 범위를 벗어나면 사용자용 에러 메시지를, 아니면 None을 반환한다."""
    length = len(text)
    if length < min_len or length > max_len:
        return f"텍스트는 {min_len}~{max_len}자 사이로 입력해주세요. (현재 {length}자)"
    return None


def _save_history(request, task, input_text, output_text, result_data):
    InferenceHistory.objects.create(
        user=request.user,
        task=task,
        input_text=input_text,
        output_text=output_text,
        result_data=result_data,
    )


def _recent_history(request, task):
    if not request.user.is_authenticated:
        return []
    return InferenceHistory.objects.filter(
        user=request.user, task=task
    ).order_by("-created_at")[:5]


# ---------------------------------------------------------------------------
# 페이지 렌더링 뷰 (GET)
# ---------------------------------------------------------------------------

def sentiment_page(request):
    history = _recent_history(request, InferenceHistory.Task.SENTIMENT)
    return render(request, "my_gpt/sentiment.html", {"history": history})


@model_login_required
def summarize_page(request):
    history = _recent_history(request, InferenceHistory.Task.SUMMARIZE)
    return render(request, "my_gpt/summarize.html", {"history": history})


@model_login_required
def moderate_page(request):
    history = _recent_history(request, InferenceHistory.Task.MODERATE)
    return render(request, "my_gpt/moderate.html", {"history": history})


@model_login_required
def combo_page(request):
    history = _recent_history(request, InferenceHistory.Task.COMBO)
    return render(request, "my_gpt/combo.html", {"history": history})


# ---------------------------------------------------------------------------
# 실행 뷰 (POST, Fetch API 대상)
# ---------------------------------------------------------------------------

@require_POST
def sentiment_view(request):
    """감정 분석 API. 비로그인 사용자도 접근 가능(DB에는 저장하지 않음)."""
    text = _extract_text(request)
    if not text:
        return JsonResponse({"error": "분석할 텍스트를 입력해주세요."}, status=400)

    error = _validate_length(text, 1, 1000)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        result = run_sentiment_pipeline(text)
    except Exception:
        logger.exception("감정 분석 파이프라인 실행 중 오류")
        return JsonResponse(
            {"error": "감정 분석 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    label = result.get("label", "")
    score = result.get("score", 0.0)

    if request.user.is_authenticated:
        _save_history(
            request,
            InferenceHistory.Task.SENTIMENT,
            text,
            f"{label} ({score:.1%})",
            result,
        )

    return JsonResponse({"label": label, "score": score, "result": result})


@model_login_required
@require_POST
def summarize_view(request):
    """텍스트 요약 API. 로그인 필요."""
    text = _extract_text(request)
    if not text:
        return JsonResponse({"error": "요약할 텍스트를 입력해주세요."}, status=400)

    error = _validate_length(text, 100, 5000)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        result = run_summarizer_pipeline(text)
    except Exception:
        logger.exception("요약 파이프라인 실행 중 오류")
        return JsonResponse(
            {"error": "요약 처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    summary = result.get("summary_text", "")

    _save_history(
        request,
        InferenceHistory.Task.SUMMARIZE,
        text,
        summary,
        result,
    )

    return JsonResponse(
        {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "result": result,
        }
    )


@model_login_required
@require_POST
def moderate_view(request):
    """유해 표현 분석 API. 로그인 필요."""
    text = _extract_text(request)
    if not text:
        return JsonResponse({"error": "검사할 텍스트를 입력해주세요."}, status=400)

    error = _validate_length(text, 1, 1000)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        result = run_moderator_pipeline(text)
    except Exception:
        logger.exception("유해 표현 분석 파이프라인 실행 중 오류")
        return JsonResponse(
            {"error": "유해 표현 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    top_label = max(result, key=lambda item: item["score"])

    _save_history(
        request,
        InferenceHistory.Task.MODERATE,
        text,
        f"{top_label['label']} ({top_label['score']:.1%})",
        result,
    )

    return JsonResponse({"top_label": top_label, "result": result})


@model_login_required
@require_POST
def combo_view(request):
    """
    복합 분석 API. 로그인 필요.

    문서 요약 → (요약문 기반) 감정 분석 → (요약문 기반) 유해 표현 분석 순으로
    모델을 체이닝하여 실행한다. 재생성 버튼도 이 엔드포인트를 그대로 재호출하며,
    매 호출마다 요약 모델을 do_sample 옵션으로 다시 추론하므로 결과가 새로 생성된다.
    """
    text = _extract_text(request)
    if not text:
        return JsonResponse({"error": "분석할 텍스트를 입력해주세요."}, status=400)

    error = _validate_length(text, 200, 5000)
    if error:
        return JsonResponse({"error": error}, status=400)

    try:
        combined_result = run_combo_pipeline(text, sample=True)
    except Exception:
        logger.exception("복합 분석 파이프라인 실행 중 오류")
        return JsonResponse(
            {"error": "복합 분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."},
            status=502,
        )

    sentiment = combined_result["sentiment"]
    toxicity = combined_result["toxicity"]
    verdict = build_verdict(sentiment["label"], toxicity["highest_score"])

    output_text = (
        f"요약: {combined_result['summary']} / "
        f"감정: {sentiment['label']} ({sentiment['score']:.1%}) / "
        f"유해성: {toxicity['highest_label']} ({toxicity['highest_score']:.1%})"
    )

    _save_history(
        request,
        InferenceHistory.Task.COMBO,
        text,
        output_text,
        combined_result,
    )

    return JsonResponse({**combined_result, "verdict": verdict})
