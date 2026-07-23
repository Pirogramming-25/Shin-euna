from .common import get_pipeline_device
import os
from functools import lru_cache
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()
MODEL_ID = os.getenv(
    "HF_SENTIMENT_MODEL_ID",
    "cardiffnlp/twitter-roberta-base-sentiment-latest",
)


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        device=get_pipeline_device(),
    )


def run_sentiment_pipeline(text):
    classifier = get_sentiment_pipeline()
    result = classifier(text)

    if not result:
        raise RuntimeError("모델이 빈 응답을 반환했습니다.")

    return result[0]