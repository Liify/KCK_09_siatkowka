import cv2
import numpy as np

PANEL_H = 95                          # wysokość paska na DOLE ekranu
_FT     = cv2.FONT_HERSHEY_TRIPLEX    # ładniejszy font niż SIMPLEX/DUPLEX
_FS     = cv2.FONT_HERSHEY_SIMPLEX    # mniejszy font do etykiet



def _cień(img, text, x, y, scale, color, thick=1):
    """Tekst z cieniem – znacznie lepsza czytelność na każdym tle."""
    cv2.putText(img, text, (x + 2, y + 2), _FT, scale, (0, 0, 0),  thick + 1, cv2.LINE_AA)
    cv2.putText(img, text, (x,     y    ), _FT, scale, color,       thick,     cv2.LINE_AA)


def _etykieta(img, text, x, y, scale=0.42, color=(120, 120, 130)):
    """Mała etykieta podpisowa."""
    cv2.putText(img, text, (x, y), _FS, scale, (0, 0, 0),  2, cv2.LINE_AA)
    cv2.putText(img, text, (x, y), _FS, scale, color,       1, cv2.LINE_AA)



class UI:
    @staticmethod
    def draw(obraz, user_name, licznik, punkty, tryb_treningu, feedback, nazwa_kamery):
        h, w = obraz.shape[:2]

        overlay = obraz.copy()
        cv2.rectangle(overlay, (0, h - PANEL_H), (w, h), (12, 12, 18), -1)
        cv2.addWeighted(overlay, 0.82, obraz, 0.18, 0, obraz)
        cv2.line(obraz, (0, h - PANEL_H), (w, h - PANEL_H), (60, 60, 80), 1)

        py = h - PANEL_H   # górna krawędź panelu

        WHITE  = (230, 230, 235)
        GRAY   = (120, 120, 130)
        GREEN  = (70,  210,  90)
        RED    = (60,   70, 220)
        ORANGE = (30,  150, 255)

        kolor_q = GREEN if punkty >= 70 else RED

        _cień(obraz, user_name.upper(), 14, py + 36, 0.70, WHITE, 1)
        _etykieta(obraz, f"Kamera: {nazwa_kamery}", 14, py + 58)
        _etykieta(obraz, f"Trening: {tryb_treningu}", 14, py + 80)

        rep_str = str(licznik)
        (tw, _), _ = cv2.getTextSize(rep_str, _FT, 2.2, 2)
        cx = w // 2 - tw // 2
        _etykieta(obraz, "POWTORZENIA", w // 2 - 54, py + 22)
        _cień(obraz, rep_str, cx, py + 80, 2.2, GREEN, 2)

        q_str = f"{punkty}%"
        (tw2, _), _ = cv2.getTextSize(q_str, _FT, 1.4, 2)
        rx = w - tw2 - 16
        _etykieta(obraz, "JAKOSC", w - 95, py + 22)
        _cień(obraz, q_str, rx, py + 80, 1.4, kolor_q, 2)

        for i, msg in enumerate(feedback[:3]):
            fy = (h - PANEL_H - 12) - i * 36
            disp = f" ! {msg} "
            (fw, fh), bl = cv2.getTextSize(disp, _FS, 0.55, 1)
            x0 = 10
            y0 = fy - fh - 4
            x1 = x0 + fw
            y1 = fy + bl + 2
            # tło dymku
            cv2.rectangle(obraz, (x0 - 2, y0 - 2), (x1 + 2, y1 + 2), (0, 70, 150), -1)
            cv2.rectangle(obraz, (x0 - 2, y0 - 2), (x1 + 2, y1 + 2), ORANGE, 1)
            cv2.putText(obraz, disp, (x0, fy), _FS, 0.55, (255, 255, 255), 1, cv2.LINE_AA)