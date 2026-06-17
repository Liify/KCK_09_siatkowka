class Warunki:
    @staticmethod
    def detect_position(tryb_treningu, data_przod, data_bok):

        stan_klatki_przod = "neutral"
        feedback_przod    = []
        punkty_przod      = None

        if data_przod:
            punkty_przod = 0

            if tryb_treningu == "Dolne":
                # Trigger: OBA nadgarstki wyraźnie poniżej barków (>= 40 px)
                # – zapobiega fałszywemu wykrywaniu przy rękach wzdłuż ciała
                l_low = data_przod['l_nadgarstek'][1] > data_przod['l_bark'][1] + 40
                p_low = data_przod['p_nadgarstek'][1] > data_przod['p_bark'][1] + 40

                if l_low and p_low:
                    stan_klatki_przod = "dol"

                    # Łokcie wyprostowane (>150°)
                    if data_przod['kat_l_lokiec'] > 150 and data_przod['kat_p_lokiec'] > 150:
                        punkty_przod += 40
                    else:
                        feedback_przod.append("Wyprostuj lokcie")

            else:  # Gorne
                # Trigger: OBA nadgarstki wyraźnie powyżej barków
                l_high = data_przod['l_nadgarstek'][1] < data_przod['l_bark'][1] - 60
                p_high = data_przod['p_nadgarstek'][1] < data_przod['p_bark'][1] - 60

                if l_high and p_high:
                    stan_klatki_przod = "gora"

                    # Kąt łokci w zakresie koszyczka (60°–140°)
                    if 60 < data_przod['kat_l_lokiec'] < 140 and 60 < data_przod['kat_p_lokiec'] < 140:
                        punkty_przod += 40
                    else:
                        feedback_przod.append("Popraw koszyczek")

            # Złączone dłonie – tylko przy odbiciach dolnych
            if tryb_treningu == "Dolne":
                if data_przod['dlonie_razem']:
                    punkty_przod += 20
                else:
                    feedback_przod.append("Zlacz dlonie")

            # Ugięte kolana
            if data_przod['nogi_ugiete']:
                punkty_przod += 20
            else:
                feedback_przod.append("Ugnij nogi")

            # Ręce przed ciałem
            if data_przod['rece_przed']:
                punkty_przod += 20
            else:
                feedback_przod.append("Rece przed cialem")

            # Przy odbiciach górnych: maks. = 40+20+20 = 80 → skaluj do 100
            if tryb_treningu == "Gorne" and punkty_przod is not None:
                punkty_przod = min(100, int(punkty_przod * 1.25))

        stan_klatki_bok = "neutral"
        feedback_bok    = []
        punkty_bok      = None

        if data_bok:
            punkty_bok = 0

            if tryb_treningu == "Dolne":
                if data_bok['l_nadgarstek'][1] > data_bok['l_bark'][1] + 40:
                    stan_klatki_bok = "dol"

                    if data_bok['kat_l_lokiec'] > 150:
                        punkty_bok += 40
                    else:
                        feedback_bok.append("Wyprostuj lokcie")

            else:  # Gorne
                if data_bok['l_nadgarstek'][1] < data_bok['l_bark'][1] - 60:
                    stan_klatki_bok = "gora"

                    if 60 < data_bok['kat_l_lokiec'] < 140:
                        punkty_bok += 40
                    else:
                        feedback_bok.append("Zly kat lokcia")

            if data_bok['nogi_ugiete']:
                punkty_bok += 30
            else:
                feedback_bok.append("Ugnij nogi")

            if data_bok['rece_przed']:
                punkty_bok += 30
            else:
                feedback_bok.append("Rece przed cialem")

        if stan_klatki_przod != "neutral":
            stan_globalny = stan_klatki_przod
        elif stan_klatki_bok != "neutral":
            stan_globalny = stan_klatki_bok
        else:
            stan_globalny = "neutral"

        return stan_globalny, punkty_przod, punkty_bok, feedback_przod, feedback_bok