from .common import get_pipeline_device
import os
from functools import lru_cache
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()
MODEL_ID = os.getenv(
    "HF_MODERATOR_MODEL_ID",
    "unitary/toxic-bert",
)


@lru_cache(maxsize=1)
def get_moderator_pipeline():
    return pipeline(
        task="text-classification",
        model=MODEL_ID,
        device=get_pipeline_device(),
    )


def run_moderator_pipeline(text):
    classifier = get_moderator_pipeline()
    result = classifier(text, top_k=None) #전체 레이블 점수 리스트 반환

    if not result:
        raise RuntimeError("모델이 빈 응답을 반환했습니다.")

    return result