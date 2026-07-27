import math
import os
import time

import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python import vision

from visualization import draw_manual, print_RSP_result

# hand_landmarker.task 모델은 RPSGame 루트 폴더에 있음
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "hand_landmarker.task")

ROCK, PAPER, SCISSORS = 0, 1, 2

# 손 랜드마크 인덱스 (README_image/hand-landmarks.png 참고)
WRIST = 0
THUMB_MCP, THUMB_TIP = 2, 4
INDEX_PIP, INDEX_TIP = 6, 8
MIDDLE_PIP, MIDDLE_TIP = 10, 12
RING_PIP, RING_TIP = 14, 16
PINKY_MCP, PINKY_PIP, PINKY_TIP = 17, 18, 20


def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def _is_finger_open(landmarks, tip_idx, pip_idx):
    """손가락 끝(tip)이 중간 관절(pip)보다 손목에서 더 멀리 있으면 펴진 것으로 판단.
    (손이 기울어져도 y좌표 비교보다 안정적)"""
    wrist = landmarks[WRIST]
    return _dist(landmarks[tip_idx], wrist) > _dist(landmarks[pip_idx], wrist)


def _is_thumb_open(landmarks):
    """엄지는 손바닥 옆으로 벌어지는 움직임이라 새끼손가락 뿌리(pinky mcp) 기준 거리로 판단"""
    pinky_mcp = landmarks[PINKY_MCP]
    return _dist(landmarks[THUMB_TIP], pinky_mcp) > _dist(landmarks[THUMB_MCP], pinky_mcp)


def classify_rps(landmarks):
    """21개 손 랜드마크로 가위/바위/보 판별. 0=Rock, 1=Paper, 2=Scissors, None=판별 불가"""
    index_open = _is_finger_open(landmarks, INDEX_TIP, INDEX_PIP)
    middle_open = _is_finger_open(landmarks, MIDDLE_TIP, MIDDLE_PIP)
    ring_open = _is_finger_open(landmarks, RING_TIP, RING_PIP)
    pinky_open = _is_finger_open(landmarks, PINKY_TIP, PINKY_PIP)
    thumb_open = _is_thumb_open(landmarks)

    open_count = sum([index_open, middle_open, ring_open, pinky_open])

    if index_open and middle_open and not ring_open and not pinky_open:
        return SCISSORS
    if open_count == 0 and not thumb_open:
        return ROCK
    if open_count >= 3:
        return PAPER
    if open_count <= 1:
        return ROCK
    return None


class HandLandmarkerRunner:
    """LIVE_STREAM 모드는 비동기 콜백으로 결과가 오므로, 최신 결과를 보관해두는 래퍼"""

    def __init__(self, model_path):
        self.latest_result = None
        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=model_path),
            running_mode=vision.RunningMode.LIVE_STREAM,
            num_hands=1,
            result_callback=self._on_result,
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def _on_result(self, result, output_image, timestamp_ms):
        self.latest_result = result

    def detect_async(self, mp_image, timestamp_ms):
        self.landmarker.detect_async(mp_image, timestamp_ms)

    def close(self):
        self.landmarker.close()


def main():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return

    runner = HandLandmarkerRunner(MODEL_PATH)
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            frame = cv.flip(frame, 1)  # 거울 모드
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            timestamp_ms = int((time.time() - start_time) * 1000)
            runner.detect_async(mp_image, timestamp_ms)

            result = runner.latest_result
            rps_result = None
            if result is not None and result.hand_landmarks:
                rps_result = classify_rps(result.hand_landmarks[0])

            frame = draw_manual(frame, result)
            frame = print_RSP_result(frame, rps_result)

            cv.imshow("RPS Game", frame)
            if cv.waitKey(1) == ord("q"):
                break
    finally:
        runner.close()
        cap.release()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()
