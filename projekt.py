import cv2
import time
from camera_config import Config
from obliczanie import Obliczanie
from warunki import Warunki
from UI import UI
from database_manager import init_db, log_error
from audio_trener import AudioTrener

def main():
    init_db()
    audio = AudioTrener()

    user_name = input("Podaj nazwę profilu (imię): ").strip()
    print("\nWybierz tryb treningu:\n1. Odbicia DOLNE\n2. Odbicia GÓRNE")
    wybor = input("Wybór (1 lub 2): ")
    tryb_treningu = "Dolne" if wybor == "1" else "Gorne"
    aktualny_cel = "dol" if tryb_treningu == "Dolne" else "gora"

    cfg = Config(user_name, tryb_treningu)
    calc = Obliczanie()
    logic = Warunki()
    ui = UI()

    licznik = 0
    poprzedni_stan_ruchu = "neutral"
    buffer_stan = []
    BUFFER_SIZE = 4
    cooldown = 0

    db_cooldowns = {}
    COOLDOWN_TIME = 3.0

    while cfg.vid.isOpened():
        ret, frame = cfg.vid.read()
        if not ret: break

        obraz_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        wynik = cfg.holistic.process(obraz_rgb)
        frame = cv2.cvtColor(obraz_rgb, cv2.COLOR_RGB2BGR)
        h, w, _ = frame.shape

        stan_klatki = "neutral"
        feedback = []
        punkty = 0
        if cooldown > 0: cooldown -= 1

        if wynik.pose_landmarks:
            cfg.mp_drawing.draw_landmarks(frame, wynik.pose_landmarks, cfg.mp_holistic.POSE_CONNECTIONS)

            data = calc.get_data(wynik.pose_landmarks, w, h)
            stan_klatki, punkty, feedback = logic.detect_position(tryb_treningu, data)

            current_time = time.time()
            for blad in feedback:
                if blad not in db_cooldowns or (current_time - db_cooldowns[blad]) > COOLDOWN_TIME:
                    log_error(user_name, blad)
                    audio.mow(blad)
                    db_cooldowns[blad] = current_time

            buffer_stan.append(stan_klatki)
            if len(buffer_stan) > BUFFER_SIZE: buffer_stan.pop(0)
            stan_stabilny = max(set(buffer_stan), key=buffer_stan.count)

            if poprzedni_stan_ruchu == aktualny_cel and stan_stabilny == "neutral" and punkty >= 70 and cooldown == 0:
                licznik += 1
                cooldown = 10

            if stan_stabilny != "neutral":
                poprzedni_stan_ruchu = stan_stabilny

            ui.draw(frame, user_name, licznik, punkty, tryb_treningu, feedback)

        cfg.out.write(frame)
        cv2.imshow('Siatkowka AI Trainer', frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cfg.release()

if __name__ == "__main__":
    main()