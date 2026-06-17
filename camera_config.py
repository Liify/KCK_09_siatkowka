import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import os
from datetime import datetime


POSE_CONNECTIONS = frozenset([
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21),
    (17, 19), (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    (11, 23), (12, 24), (23, 24), (23, 25), (24, 26), (25, 27), (26, 28),
    (27, 29), (28, 30), (29, 31), (30, 32), (27, 31), (28, 32)
])


class _FakeLandmarks:
    def __init__(self, landmarks):
        self.landmark = landmarks


class _FakeResult:
    def __init__(self, landmarks_obj):
        self.pose_landmarks = landmarks_obj



class DrawingUtils:
    @staticmethod
    def draw_landmarks(frame, landmarks, connections):
        if landmarks is None:
            return
        h, w, _ = frame.shape
        pts = {}
        for i, lm in enumerate(landmarks.landmark):
            x, y = int(lm.x * w), int(lm.y * h)
            pts[i] = (x, y)
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
        for a, b in connections:
            if a in pts and b in pts:
                cv2.line(frame, pts[a], pts[b], (200, 200, 200), 2)



class _PoseDetector:
    MODEL_PATH = "pose_landmarker_heavy.task"

    def __init__(self):
        if not os.path.exists(self.MODEL_PATH):
            raise FileNotFoundError(
                f"Brak pliku modelu '{self.MODEL_PATH}'.\n"
                "Pobierz go poleceniem:\n"
                "  curl -o pose_landmarker_heavy.task https://storage.googleapis.com/"
                "mediapipe-models/pose_landmarker/pose_landmarker_heavy/float16/latest/"
                "pose_landmarker_heavy.task\n"
                "i wrzuć do folderu projektu."
            )
        base_opts = mp_python.BaseOptions(model_asset_path=self.MODEL_PATH)
        opts = vision.PoseLandmarkerOptions(
            base_options=base_opts,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.5,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._detector = vision.PoseLandmarker.create_from_options(opts)
        self._ts_ms = 0

    def process(self, rgb_frame):
        self._ts_ms += 50   # ~20 fps; musi być rosnąco
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        result = self._detector.detect_for_video(mp_img, self._ts_ms)
        if result.pose_landmarks:
            return _FakeResult(_FakeLandmarks(result.pose_landmarks[0]))
        return _FakeResult(None)

    def close(self):
        self._detector.close()



class Config:
    def __init__(self, user_name, tryb_treningu):
        self.output_dir = os.path.join("Video", user_name)
        os.makedirs(self.output_dir, exist_ok=True)

        self.mp_drawing = DrawingUtils()
        self.mp_holistic = type('obj', (object,), {'POSE_CONNECTIONS': POSE_CONNECTIONS})()

        # Detektory
        self.holistic_przod = _PoseDetector()
        self.holistic_bok   = _PoseDetector()

        # KAMERA
        self.vid_przod = cv2.VideoCapture(0)
        cv2.namedWindow('Siatkowka AI - PRZOD', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Siatkowka AI - PRZOD', 1280, 720)

        self.vid_bok = cv2.VideoCapture(1)
        cv2.namedWindow('Siatkowka AI - BOK', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Siatkowka AI - BOK', 1280, 720)

        # ZAPIS WIDEO
        timestamp = datetime.now().strftime("%H%M%S")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        przod_w = int(self.vid_przod.get(cv2.CAP_PROP_FRAME_WIDTH))
        przod_h = int(self.vid_przod.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_przod_filename = os.path.join(
            self.output_dir, f"Odbicie_{tryb_treningu}_{timestamp}_PRZOD.mp4")
        self.out_przod = cv2.VideoWriter(
            self.video_przod_filename, fourcc, 20.0, (przod_w, przod_h))

        bok_w = int(self.vid_bok.get(cv2.CAP_PROP_FRAME_WIDTH))
        bok_h = int(self.vid_bok.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_bok_filename = os.path.join(
            self.output_dir, f"Odbicie_{tryb_treningu}_{timestamp}_BOK.mp4")
        self.out_bok = cv2.VideoWriter(
            self.video_bok_filename, fourcc, 20.0, (bok_w, bok_h))

    def release(self):
        self.vid_przod.release()
        self.vid_bok.release()
        self.out_przod.release()
        self.out_bok.release()
        cv2.destroyAllWindows()