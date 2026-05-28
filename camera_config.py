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
        self.holistic_przod = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.holistic_bok = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=2,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # KAMERA
        self.vid_przod = cv2.VideoCapture(0)
        cv2.namedWindow('Siatkowka AI Trainer PRZOD', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Siatkowka AI Trainer PRZOD', 1920, 1080)
        self.vid_bok = cv2.VideoCapture(1)
        cv2.namedWindow('Siatkowka AI Trainer BOK', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Siatkowka AI Trainer BOK', 1920, 1080)

        # ZAPIS WIDEO
        przod_w = int(self.vid_przod.get(cv2.CAP_PROP_FRAME_WIDTH))
        przod_h = int(self.vid_przod.get(cv2.CAP_PROP_FRAME_HEIGHT))
        timestamp = datetime.now().strftime("%H%M%S")
        self.video_przod_filename = os.path.join(self.output_dir, f"Odbicie_{tryb_treningu}_{timestamp}_PRZOD.mp4")

        bok_w = int(self.vid_bok.get(cv2.CAP_PROP_FRAME_WIDTH))
        bok_h = int(self.vid_bok.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.video_bok_filename = os.path.join(self.output_dir, f"Odbicie_{tryb_treningu}_{timestamp}_BOK.mp4")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out_przod = cv2.VideoWriter(self.video_przod_filename, fourcc, 20.0, (przod_w, przod_h))
        self.out_bok = cv2.VideoWriter(self.video_bok_filename, fourcc, 20.0, (bok_w, bok_h))

    def release(self):
        self.vid_przod.release()
        self.vid_bok.release()
        self.out_przod.release()
        self.out_bok.release()
        self.holistic_przod.close()
        self.holistic_bok.close()
        cv2.destroyAllWindows()