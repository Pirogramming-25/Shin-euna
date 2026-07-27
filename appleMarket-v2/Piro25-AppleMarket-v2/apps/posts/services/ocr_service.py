# PaddleOCR 기반 영양성분표 OCR 기능
import re
import unicodedata

import cv2
import numpy as np
from paddleocr import PaddleOCR

_ocr_engine = None

_NUMBER = r'(\d+(?:[.,]\d+)?)'
_GAP = r'[^\d]{0,6}'


def _get_ocr_engine():
    """PaddleOCR 엔진은 초기화 비용이 크므로 최초 1회만 생성해 재사용한다."""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = PaddleOCR(
            lang='korean',
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            # 이진화 전처리 이미지에서 방향 분류기가 줄을 오분류해 인식률을
            # 크게 떨어뜨리는 문제가 있어 비활성화한다.
            use_textline_orientation=False,
            # Windows CPU 환경에서 mkldnn 백엔드가 detection 모델 추론 시
            # PIR 실행기와 충돌하여 예외를 던지는 문제가 있어 비활성화한다.
            enable_mkldnn=False,
        )
    return _ocr_engine


def _decode_image(image_bytes):
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError('이미지를 읽을 수 없습니다.')
    return image


def _preprocess(image):
    """OCR 인식률 향상을 위한 전처리: 업스케일, 노이즈 제거, 대비 강화, 이진화"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    min_side = 900
    h, w = gray.shape[:2]
    if min(h, w) < min_side:
        scale = min_side / min(h, w)
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.fastNlMeansDenoising(gray, h=10)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    binary = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
    )
    return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)


def _to_float(raw_value):
    # 나트륨처럼 큰 숫자에 쓰이는 천단위 콤마(예: 1,040)를 제거한다.
    # 소수점은 한국어 영양성분표 표기 관례대로 마침표만 사용한다.
    return float(raw_value.replace(',', ''))


def _to_grams(raw_value, unit):
    value = _to_float(raw_value)
    if unit and unit.lower() == 'mg':
        value = value / 1000
    return round(value, 2)


def _find_number(text, keyword_pattern, unit_pattern=r'(m?g)'):
    match = re.search(keyword_pattern + _GAP + _NUMBER + r'\s*' + unit_pattern, text, re.IGNORECASE)
    return match


def _parse_nutrition(rec_texts):
    # 박스 사이는 개행으로 구분해 서로 다른 박스의 숫자가 이어 붙어
    # (예: "총내용량 36g" + "130kcal" -> "36130kcal") 잘못 인식되지 않게 한다.
    joined = '\n'.join(unicodedata.normalize('NFKC', text) for text in rec_texts)

    result = {'calorie': None, 'carbohydrate': None, 'protein': None, 'fat': None}

    match = _find_number(joined, r'(?:열량|칼로리)', unit_pattern=r'k?cal')
    if not match:
        # 최신 영양성분표는 "열량/칼로리" 표기 없이 "130kcal"처럼 총 내용량
        # 옆에 숫자만 단독으로 적혀있는 경우가 많다.
        match = re.search(_NUMBER + r'\s*kcal', joined, re.IGNORECASE)
    if match:
        result['calorie'] = round(_to_float(match.group(1)), 2)

    match = _find_number(joined, r'탄수화물')
    if match:
        result['carbohydrate'] = _to_grams(match.group(1), match.group(2))

    match = _find_number(joined, r'(?<!포화)(?<!트랜스)단백질')
    if match:
        result['protein'] = _to_grams(match.group(1), match.group(2))

    match = _find_number(joined, r'(?<!포화)(?<!트랜스)지방')
    if match:
        result['fat'] = _to_grams(match.group(1), match.group(2))

    return result


def extract_nutrition_info(uploaded_file):
    """업로드된 영양성분표 이미지에서 칼로리/탄수화물/단백질/지방 정보를 추출한다."""
    uploaded_file.seek(0)
    image_bytes = uploaded_file.read()
    uploaded_file.seek(0)

    image = _decode_image(image_bytes)
    processed = _preprocess(image)

    engine = _get_ocr_engine()
    results = engine.predict(processed)

    rec_texts = []
    for page in results:
        payload = page.json if hasattr(page, 'json') else page
        if isinstance(payload, dict):
            payload = payload.get('res', payload)
            rec_texts.extend(payload.get('rec_texts', []))

    return _parse_nutrition(rec_texts)
