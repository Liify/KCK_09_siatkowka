class Warunki:
    @staticmethod
    def detect_position(tryb_treningu, data_przod, data_bok):
        stan_klatki_przod = "neutral"
        feedback_przod = []
        punkty_przod = None

        # DETEKCJA POZYCJI
        if data_przod:
            punkty_przod = 0
            if tryb_treningu == "Dolne":
                if data_przod['l_nadgarstek'][1] > data_przod['l_bark'][1] + 20 and data_przod['p_nadgarstek'][1] > data_przod['p_bark'][1] + 20:
                    stan_klatki_przod = "dol"
                    if data_przod['kat_l_lokiec'] > 150 and data_przod['kat_p_lokiec'] > 150:
                        punkty_przod += 40
                    else:
                        feedback_przod.append("Wyprostuj lokcie")
            else:
                if data_przod['l_nadgarstek'][1] < (data_przod['l_bark'][1] - 60) and data_przod['p_nadgarstek'][1] < (data_przod['p_bark'][1] - 60):
                    stan_klatki_przod = "gora"
                    if 60 < data_przod['kat_l_lokiec'] < 140 and 60 < data_przod['kat_p_lokiec'] < 140:
                        punkty_przod += 40
                    else:
                        feedback_przod.append("Popraw koszyczek")

            # WARUNKI
            if data_przod['dlonie_razem']: punkty_przod += 20
            else: feedback_przod.append("Zlacz dlonie")

            if data_przod['nogi_ugiete']: punkty_przod += 20
            else: feedback_przod.append("Ugnij nogi")

            if data_przod['rece_przed']: punkty_przod += 20
            else: feedback_przod.append("Rece przed cialo")


        stan_klatki_bok = "neutral"
        feedback_bok = []
        punkty_bok = None

        if data_bok:
            punkty_bok = 0
            if tryb_treningu == "Dolne":
                if data_bok['l_nadgarstek'][1] > data_bok['l_bark'][1] + 20:
                    stan_klatki_bok = "dol"
                    if data_bok['kat_l_lokiec'] > 150:
                        punkty_bok += 40
                    else:
                        feedback_bok.append("Wyprostuj lokcie (Bok)")
            else:
                if data_bok['l_nadgarstek'][1] < (data_bok['l_bark'][1] - 60):
                    stan_klatki_bok = "gora"
                    if 60 < data_bok['kat_l_lokiec'] < 140:
                        punkty_bok += 40
                    else:
                        feedback_bok.append("Zly kat lokcia (Bok)")

            if data_bok['nogi_ugiete']:
                punkty_bok += 30
            else:
                feedback_bok.append("Ugnij nogi (Bok)")

            if data_bok['rece_przed']:
                punkty_bok += 30
            else:
                feedback_bok.append("Rece zbytnio przy ciele")

        if stan_klatki_przod != "neutral":
            stan_globalny = stan_klatki_przod
        elif stan_klatki_bok != "neutral":
            stan_globalny = stan_klatki_bok
        else:
            stan_globalny = "neutral"


        return stan_globalny, punkty_przod, punkty_bok, feedback_przod, feedback_bok