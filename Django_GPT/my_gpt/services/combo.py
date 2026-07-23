from .common import get_pipeline_device
from .summarizer import run_summarizer_pipeline
from .sentiment import run_sentiment_pipeline
from .moderator import run_moderator_pipeline


def run_combo_pipeline(text, sample=False):
    """
    복합 분석 파이프라인.

    문서 요약 → (요약문 기반) 감정 분석 → (요약문 기반) 유해 표현 분석 순서로
    모델을 체이닝한다. 감정/유해 표현 분석은 원문이 아닌 요약문을 입력으로 받는다.
    """
    summary_result = run_summarizer_pipeline(text, sample=sample)
    summary_text = summary_result.get("summary_text", "")

    sentiment_result = run_sentiment_pipeline(summary_text)
    toxicity_result = run_moderator_pipeline(summary_text)

    top_toxicity = max(toxicity_result, key=lambda item: item["score"])

    return {
        "summary": summary_text,
        "sentiment": {
            "label": sentiment_result.get("label", ""),
            "score": sentiment_result.get("score", 0.0),
        },
        "toxicity": {
            "highest_label": top_toxicity["label"],
            "highest_score": top_toxicity["score"],
            "all_scores": toxicity_result,
        },
    }


def build_verdict(sentiment_label, toxicity_score):
    """감정 레이블과 유해 표현 최고 점수를 바탕으로 종합 판정 문장을 조건문으로 생성한다."""
    if sentiment_label.lower() == "negative":
        sentiment_description = "부정적인 평가를 포함합니다."
    else:
        sentiment_description = "강한 부정적 평가는 확인되지 않았습니다."

    if toxicity_score >= 0.5:
        toxicity_description = "유해 표현 가능성이 높습니다."
    else:
        toxicity_description = "심각한 유해 표현 가능성은 낮습니다."

    return f"이 피드백은 {sentiment_description} 또한, {toxicity_description}"
