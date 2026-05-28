import cv2


class UI:
    @staticmethod
    def draw(obraz, user_name, licznik, punkty, tryb_treningu, feedback, nazwa_kamery):
        h, w, _ = obraz.shape

        # PROSTOKĄT TŁA
        cv2.rectangle(obraz, (0, 0), (w, 120), (30, 30, 30), -1)

        # KOLOR JAKOŚCI
        kolor_punktow = (0, 255, 0) if punkty >= 70 else (0, 0, 255)

        # NAPISY GŁÓWNE
        cv2.putText(obraz, f"PROFIL: {user_name} | {nazwa_kamery}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(obraz, f"POWOTORZENIA: {licznik}", (20, 100), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        cv2.putText(obraz, f"JAKOSC: {punkty}%", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 1, kolor_punktow, 2)
        cv2.putText(obraz, f"TRENING: {tryb_treningu}", (w // 2 - 60, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (150, 150, 150), 1)

        # FEEDBACK (max 2 linie)
        for i, text in enumerate(feedback[:2]):
            cv2.putText(obraz, f"! {text}", (w - 260, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)