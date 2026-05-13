import cv2
from camera_config import Config
from obliczanie import Obliczanie
from warunki import Warunki
from UI import UI


def main():
    # INTERFEJS KONSOLOWY
    user_name = input("Podaj nazwę profilu (imię): ").strip()
    print("\nWybierz tryb treningu:\n1. Odbicia DOLNE\n2. Odbicia GÓRNE")
    wybor = input("Wybór (1 lub 2): ")
    tryb_treningu = "Dolne" if wybor == "1" else "Gorne"
    aktualny_cel = "dol" if tryb_treningu == "Dolne" else "gora"

    # INICJALIZACJA MODUŁÓW
    cfg = Config(user_name, tryb_treningu)
    calc = Obliczanie()
    logic = Warunki()
    ui = UI()

    # ZMIENNE STANU
    licznik = 0
    poprzedni_stan_ruchu = "neutral"
    buffer_stan = []
    BUFFER_SIZE = 4
    cooldown = 0

    while cfg.vid.isOpened():
        ret, frame = cfg.vid.read()
        if not ret: break

        # KONWERSJA I PROCESOWANIE
        obraz_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        wynik = cfg.holistic.process(obraz_rgb)
        frame = cv2.cvtColor(obraz_rgb, cv2.COLOR_RGB2BGR)
        h, w, _ = frame.shape

        stan_klatki = "neutral"
        feedback = []
        punkty = 0
        if cooldown > 0: cooldown -= 1

        if wynik.pose_landmarks:
            # RYSOWANIE SIATKI MP
            cfg.mp_drawing.draw_landmarks(frame, wynik.pose_landmarks, cfg.mp_holistic.POSE_CONNECTIONS)

            # OBLICZENIA I LOGIKA
            data = calc.get_data(wynik.pose_landmarks, w, h)
            stan_klatki, punkty, feedback = logic.detect_position(tryb_treningu, data)

            # STABILIZACJA STANU
            buffer_stan.append(stan_klatki)
            if len(buffer_stan) > BUFFER_SIZE: buffer_stan.pop(0)
            stan_stabilny = max(set(buffer_stan), key=buffer_stan.count)

            # LICZENIE ODBIĆ
            if poprzedni_stan_ruchu == aktualny_cel and stan_stabilny == "neutral" and punkty >= 70 and cooldown == 0:
                licznik += 1
                cooldown = 10

            if stan_stabilny != "neutral":
                poprzedni_stan_ruchu = stan_stabilny

            # RENDEROWANIE UI
            ui.draw(frame, user_name, licznik, punkty, tryb_treningu, feedback)

        # ZAPIS I WYŚWIETLANIE
        cfg.out.write(frame)
        cv2.imshow('Siatkowka AI Trainer', frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break

    cfg.release()


if __name__ == "__main__":
    main()