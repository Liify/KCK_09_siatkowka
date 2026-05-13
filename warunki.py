class Warunki:
    @staticmethod
    def detect_position(tryb_treningu, data):
        stan_klatki = "neutral"
        feedback = []
        punkty = 0

        # DETEKCJA POZYCJI
        if tryb_treningu == "Dolne":
            if data['l_nadgarstek'][1] > data['l_bark'][1] + 20 and data['p_nadgarstek'][1] > data['p_bark'][1] + 20:
                stan_klatki = "dol"
                if data['kat_l_lokiec'] > 150 and data['kat_p_lokiec'] > 150:
                    punkty += 40
                else:
                    feedback.append("Wyprostuj lokcie")
        else:
            if data['l_nadgarstek'][1] < (data['l_bark'][1] - 60) and data['p_nadgarstek'][1] < (data['p_bark'][1] - 60):
                stan_klatki = "gora"
                if 60 < data['kat_l_lokiec'] < 140 and 60 < data['kat_p_lokiec'] < 140:
                    punkty += 40
                else:
                    feedback.append("Popraw koszyczek")

        # WARUNKI
        if data['dlonie_razem']: punkty += 20
        else: feedback.append("Zlacz dlonie")

        if data['nogi_ugiete']: punkty += 20
        else: feedback.append("Ugnij nogi")

        if data['rece_przed']: punkty += 20
        else: feedback.append("Rece przed cialo")

        return stan_klatki, punkty, feedback