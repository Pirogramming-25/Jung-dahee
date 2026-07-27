import math
import time

import cv2 as cv
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions

from visualization import draw_manual, print_RSP_result

# ------------------------------------------------------------------
# 설정
# ------------------------------------------------------------------
MODEL_PATH = "hand_landmarker.task"

# HandLandmark index 상수 (엄지는 판별 로직에서 사용하지 않음)
WRIST = 0
INDEX_TIP, INDEX_PIP = 8, 6
MIDDLE_TIP, MIDDLE_PIP = 12, 10
RING_TIP, RING_PIP = 16, 14
PINKY_TIP, PINKY_PIP = 20, 18

FINGERS = [
    (INDEX_TIP, INDEX_PIP),
    (MIDDLE_TIP, MIDDLE_PIP),
    (RING_TIP, RING_PIP),
    (PINKY_TIP, PINKY_PIP),
]

ROCK, PAPER, SCISSORS = 0, 1, 2


def distance(a, b):
    """두 랜드마크 사이의 유클리드 거리 (정규화 좌표 기준)"""
    return math.hypot(a.x - b.x, a.y - b.y)


def is_finger_extended(landmarks, tip_idx, pip_idx, wrist_idx=WRIST):
    """
    (TIP - WRIST) 거리와 (PIP - WRIST) 거리를 비교해
    손가락이 펴져 있는지 판단
    """
    dist_tip = distance(landmarks[tip_idx], landmarks[wrist_idx])
    dist_pip = distance(landmarks[pip_idx], landmarks[wrist_idx])
    return dist_tip > dist_pip


def count_extended_fingers(landmarks):
    """검지~소지 중 펴진 손가락 개수를 반환"""
    count = 0
    for tip_idx, pip_idx in FINGERS:
        if is_finger_extended(landmarks, tip_idx, pip_idx):
            count += 1
    return count


def classify_rps(extended_count):
    """
    펴진 손가락 개수 -> 가위/바위/보 매핑
    0개 펴짐 -> 바위 (Rock)
    2개 펴짐 -> 가위 (Scissors)
    4개 펴짐 -> 보   (Paper)
    그 외(1, 3개 등 애매한 경우) -> 판별 불가(None)
    """
    if extended_count == 0:
        return ROCK
    elif extended_count == 2:
        return SCISSORS
    elif extended_count == 4:
        return PAPER
    else:
        return None


def open_camera(max_index=3, warmup_tries=30, warmup_delay=0.1):
    """
    인덱스 0부터 max_index까지 순서대로 시도해서
    실제로 프레임을 읽을 수 있는 카메라를 찾아 반환.
    (아이폰 연속성 카메라 등으로 인덱스가 밀리는 경우 대응)
    """
    for index in range(max_index + 1):
        cap = cv.VideoCapture(index)
        if not cap.isOpened():
            cap.release()
            continue

        # 카메라가 워밍업되는 동안 첫 프레임 읽기가 실패할 수 있어 잠시 재시도
        for _ in range(warmup_tries):
            ret, frame = cap.read()
            if ret:
                print(f"Camera index {index} opened successfully.")
                return cap
            time.sleep(warmup_delay)

        # 이 인덱스에서는 프레임을 못 읽었으니 다음 인덱스로
        cap.release()

    return None


def run():
    base_options = BaseOptions(model_asset_path=MODEL_PATH)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
    )
    landmarker = vision.HandLandmarker.create_from_options(options)

    cap = open_camera()
    if cap is None:
        print("Cannot open any camera. Check camera connection / permissions.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            frame = cv.flip(frame, 1)
            rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            timestamp_ms = int(time.time() * 1000)
            detection_result = landmarker.detect_for_video(mp_image, timestamp_ms)

            rps_result = None
            if detection_result.hand_landmarks:
                landmarks = detection_result.hand_landmarks[0]
                extended_count = count_extended_fingers(landmarks)
                rps_result = classify_rps(extended_count)

            frame = draw_manual(frame, detection_result)
            frame = print_RSP_result(frame, rps_result)

            cv.imshow("RPS Game", frame)
            if cv.waitKey(1) == ord("q"):
                break
    finally:
        cap.release()
        cv.destroyAllWindows()
        landmarker.close()


if __name__ == "__main__":
    run()