import cv2
from camera_config import Config
from obliczanie import Obliczanie
from warunki import Warunki
from UI import UI
from database_manager import init_db, log_error


def main():
    user_name = input("Podaj nazwę profilu (imię): ").strip()
    print("\nWybierz tryb treningu:\n1. Odbicia DOLNE\n2. Odbicia GÓRNE")
    wybor = input("Wybór (1 lub 2): ")
    tryb_treningu = "Dolne" if wybor == "1" else "Gorne"
    aktualny_cel  = "dol"   if tryb_treningu == "Dolne" else "gora"

    init_db()

    cfg   = Config(user_name, tryb_treningu)
    calc  = Obliczanie()
    logic = Warunki()
    ui    = UI()

    licznik              = 0
    poprzedni_stan_ruchu = "neutral"
    buffer_stan          = []
    BUFFER_SIZE          = 4
    cooldown             = 0

    max_punkty_przod = 0
    max_punkty_bok   = 0

    while cfg.vid_przod.isOpened() and cfg.vid_bok.isOpened():
        ret_przod, frame_przod = cfg.vid_przod.read()
        ret_bok,   frame_bok   = cfg.vid_bok.read()

        if not ret_przod or not ret_bok:
            print("Błąd pobierania obrazu z jednej z kamer.")
            break

        rgb_przod   = cv2.cvtColor(frame_przod, cv2.COLOR_BGR2RGB)
        wynik_przod = cfg.holistic_przod.process(rgb_przod)
        frame_przod = cv2.cvtColor(rgb_przod, cv2.COLOR_RGB2BGR)
        h_p, w_p, _ = frame_przod.shape

        rgb_bok     = cv2.cvtColor(frame_bok, cv2.COLOR_BGR2RGB)
        wynik_bok   = cfg.holistic_bok.process(rgb_bok)
        frame_bok   = cv2.cvtColor(rgb_bok, cv2.COLOR_RGB2BGR)
        h_b, w_b, _ = frame_bok.shape

        if cooldown       > 0: cooldown       -= 1

        data_przod = calc.get_data(wynik_przod.pose_landmarks, w_p, h_p) \
                     if wynik_przod.pose_landmarks else None
        data_bok   = calc.get_data(wynik_bok.pose_landmarks, w_b, h_b)   \
                     if wynik_bok.pose_landmarks   else None

        if wynik_przod.pose_landmarks:
            cfg.mp_drawing.draw_landmarks(
                frame_przod, wynik_przod.pose_landmarks, cfg.mp_holistic.POSE_CONNECTIONS)
        if wynik_bok.pose_landmarks:
            cfg.mp_drawing.draw_landmarks(
                frame_bok, wynik_bok.pose_landmarks, cfg.mp_holistic.POSE_CONNECTIONS)

        stan_klatki, punkty_przod, punkty_bok, feedback_przod, feedback_bok = \
            logic.detect_position(tryb_treningu, data_przod, data_bok)

        buffer_stan.append(stan_klatki)
        if len(buffer_stan) > BUFFER_SIZE:
            buffer_stan.pop(0)
        stan_stabilny = max(set(buffer_stan), key=buffer_stan.count)

        if stan_stabilny == aktualny_cel:
            if punkty_przod is not None and punkty_przod > max_punkty_przod:
                max_punkty_przod = punkty_przod
            if punkty_bok is not None and punkty_bok > max_punkty_bok:
                max_punkty_bok = punkty_bok

        if poprzedni_stan_ruchu == aktualny_cel and \
           stan_stabilny == "neutral" and cooldown == 0:


            q_ok = (max_punkty_przod >= 70) or (max_punkty_bok >= 70)

            if q_ok:
                licznik += 1
                cooldown = 10
                print(f"✅ Odbicie #{licznik} | Jakość przód={max_punkty_przod}% bok={max_punkty_bok}%")

                all_fb = feedback_przod + feedback_bok
                for fb in all_fb[:2]:
                    log_error(user_name, fb)

            max_punkty_przod = 0
            max_punkty_bok   = 0

        if stan_stabilny != "neutral":
            poprzedni_stan_ruchu = stan_stabilny

        p_ui = punkty_przod if punkty_przod is not None else 0
        b_ui = punkty_bok   if punkty_bok   is not None else 0

        ui.draw(frame_przod, user_name, licznik, p_ui, tryb_treningu, feedback_przod, "PRZOD")
        ui.draw(frame_bok,   user_name, licznik, b_ui, tryb_treningu, feedback_bok,   "BOK")

        cfg.out_przod.write(frame_przod)
        cfg.out_bok.write(frame_bok)
        cv2.imshow('Siatkowka AI - PRZOD', frame_przod)
        cv2.imshow('Siatkowka AI - BOK',   frame_bok)

        if cv2.waitKey(1) & 0xFF == 27:   # ESC = wyjście
            break

    cfg.release()
    print(f"\n🏁 Trening zakończony. Łącznie odbić: {licznik}")


if __name__ == "__main__":
    main()