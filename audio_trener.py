import pyttsx3
import threading


class AudioTrener:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self._lock = threading.Lock()

    def mow(self, tekst):
        def _run_speech():
            with self._lock:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.say(tekst)
                engine.runAndWait()

        threading.Thread(target=_run_speech, daemon=True).start()