from .common import get_pipeline_device
import os
from functools import lru_cache
from transformers import pipeline
from dotenv import load_dotenv

load_dotenv()
MODEL_ID = os.getenv(
    "HF_SUMMARIZER_MODEL_ID",
    "sshleifer/distilbart-cnn-6-6",
)


@lru_cache(maxsize=1)
def get_summarizer_pipeline():
    return pipeline(
        task="summarization",
        model=MODEL_ID,
        device=get_pipeline_device(),
    )


def run_summarizer_pipeline(text, sample=False):
    classifier = get_summarizer_pipeline()

    kwargs = {"max_length": 180, "min_length": 40}
    if sample:
        kwargs.update(do_sample=True, top_p=0.9, temperature=0.8)

    result = classifier(text, **kwargs)

    if not result:
        raise RuntimeError("모델이 빈 응답을 반환했습니다.")

    return result[0]