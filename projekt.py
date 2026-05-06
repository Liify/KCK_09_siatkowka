import cv2
import mediapipe as mp
import math

#KONFIGURACJA
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(
    static_image_mode=False,
    model_complexity=2,
    smooth_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

#FUNKCJE
def odleglosc(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

def oblicz_kat(a, b, c):
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])
    il_skalarny = ba[0] * bc[0] + ba[1] * bc[1]
    dlug_wek_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
    dlug_wek_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
    if dlug_wek_ba * dlug_wek_bc == 0:
        return 0
    cos_kata = max(-1, min(1, il_skalarny / (dlug_wek_ba * dlug_wek_bc)))
    return math.degrees(math.acos(cos_kata))

#ZMIENNE
licznik_dol = 0
licznik_gora = 0
poprzedni_stan_ruchu = "neutral"
buffer_stan = []
BUFFER_SIZE = 4 #JAKOŚĆ
cooldown = 0

#KAMERA
vid = cv2.VideoCapture(0)
cv2.namedWindow('Siatkowka AI Trainer', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Siatkowka AI Trainer', 1920, 1080)
#PROGRAM
while vid.isOpened():
    ret, frame = vid.read()
    if not ret:
        break
    obraz = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    wynik = holistic.process(obraz)
    obraz = cv2.cvtColor(obraz, cv2.COLOR_RGB2BGR)
    h, w, _ = obraz.shape

    stan_klatki = "neutral"
    feedback = []
    punkty = 0
    if cooldown > 0:
        cooldown -= 1

    if wynik.pose_landmarks:
        mp_drawing.draw_landmarks(
            obraz,
            wynik.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS
        )
        p = [(int(lm.x * w), int(lm.y * h)) for lm in wynik.pose_landmarks.landmark]

        #KOŃCZYNY
        l_bark, p_bark = p[11], p[12]
        l_lokiec, p_lokiec = p[13], p[14]
        l_nadgarstek, p_nadgarstek = p[15], p[16]
        l_biodro, p_biodro = p[23], p[24]
        l_kolano, p_kolano = p[25], p[26]
        l_kostka, p_kostka = p[27], p[28]

        #OBLICZENIA
        kat_l_lokiec = oblicz_kat(l_bark, l_lokiec, l_nadgarstek)
        kat_p_lokiec = oblicz_kat(p_bark, p_lokiec, p_nadgarstek)
        kat_l_kolano = oblicz_kat(l_biodro, l_kolano, l_kostka)
        kat_p_kolano = oblicz_kat(p_biodro, p_kolano, p_kostka)
        odl_nadgarstki = odleglosc(l_nadgarstek, p_nadgarstek)
        odl_barki = odleglosc(l_bark, p_bark)
        dlonie_razem = odl_nadgarstki < (odl_barki * 0.6)
        nogi_ugiete = kat_l_kolano < 160 or kat_p_kolano < 160
        rece_przed = abs(l_nadgarstek[0] - p_nadgarstek[0]) < odl_barki * 1.5

        #DETEKCJA POZYCJI !!!
        #TRZEBA COŚ ZROBIĆ W KWESTII DETEKCJI NEUTRAL BO JEST RACZEJ ZA MAŁA
        #DÓŁ
        if l_nadgarstek[1] > l_bark[1] + 20 and p_nadgarstek[1] > p_bark[1] + 20:
            stan_klatki = "dol"
            if kat_l_lokiec > 150 and kat_p_lokiec > 150:
                punkty += 40
            else:
                feedback.append("Wyprostuj lokcie")

        #GÓRA
        elif l_nadgarstek[1] < (l_bark[1] - 60) and p_nadgarstek[1] < (p_bark[1] - 60):
            stan_klatki = "gora"
            if 60 < kat_l_lokiec < 140 and 60 < kat_p_lokiec < 140:
                punkty += 40
            else:
                feedback.append("Popraw koszyczek")

        #NEUTRAL
        else:
            stan_klatki = "neutral"

        #WARUNKI
        if dlonie_razem:
            punkty += 20
        else:
            feedback.append("Zlacz dlonie")

        if nogi_ugiete:
            punkty += 20
        else:
            feedback.append("Ugnij nogi")

        if rece_przed:
            punkty += 20
        else:
            feedback.append("Rece przed cialo")

        #STABILIZACJA
        buffer_stan.append(stan_klatki)
        if len(buffer_stan) > BUFFER_SIZE:
            buffer_stan.pop(0)
        stan_stabilny = max(set(buffer_stan), key=buffer_stan.count)

        #LICZENIE ODBIĆ
        #DOLNE
        if (poprzedni_stan_ruchu == "dol"
                and stan_stabilny == "neutral"
                and punkty >= 70
                and cooldown == 0):
            licznik_dol += 1
            cooldown = 8

        #GÓRNE
        if (poprzedni_stan_ruchu == "gora"
                and stan_stabilny == "neutral"
                and punkty >= 70
                and cooldown == 0):
            licznik_gora += 1
            cooldown = 8

        if stan_stabilny in ["dol", "gora"]:
            poprzedni_stan_ruchu = stan_stabilny

        #UI
        cv2.rectangle(obraz, (0, 0), (w, 120), (30, 30, 30), -1)
        if punkty >= 70:
            kolor_punktow = (0, 255, 0)
        else:
            kolor_punktow = (0, 0, 255)
        cv2.putText(obraz, f"SCORE: {punkty}%", (20, 40),
                    cv2.FONT_HERSHEY_DUPLEX, 1, kolor_punktow, 2)
        cv2.putText(obraz, f"DOLNE: {licznik_dol}", (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(obraz, f"GORNE: {licznik_gora}", (180, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(obraz, f"TRYB: {stan_stabilny.upper()}",
                    (w // 2 - 60, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (150, 150, 150), 1)

        #FEEDBACK
        for i, text in enumerate(feedback[:2]):
            cv2.putText(obraz, f"! {text}",
                        (w - 260, 30 + i * 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 165, 255), 2)

    cv2.imshow('Siatkowka AI Trainer', obraz)
    if cv2.waitKey(1) & 0xFF == 27:
        break
vid.release()
cv2.destroyAllWindows()
holistic.close()