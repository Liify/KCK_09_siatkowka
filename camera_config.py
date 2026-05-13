import cv2
import mediapipe as mp
import os
from datetime import datetime


class Config:
    def __init__(self, user_name, tryb_treningu):
        self.output_dir = os.path.join("Video", user_name)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # KONFIGURACJA MEDIAPIPE
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # KAMERA
        self.vid = cv2.VideoCapture(0)
        cv2.namedWindow('Siatkowka AI Trainer', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Siatkowka AI Trainer', 1920, 1080)

        # ZAPIS WIDEO
        frame_w = int(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        timestamp = datetime.now().strftime("%H%M%S")
        self.video_filename = os.path.join(self.output_dir, f"Odbicie_{tryb_treningu}_{timestamp}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (frame_w, frame_h))

    def release(self):
        self.vid.release()
        self.out.release()
        self.holistic.close()
        cv2.destroyAllWindows()