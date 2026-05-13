import math


class Obliczanie:
    @staticmethod
    def odleglosc(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    @staticmethod
    def oblicz_kat(a, b, c):
        ba = (a[0] - b[0], a[1] - b[1])
        bc = (c[0] - b[0], c[1] - b[1])
        il_skalarny = ba[0] * bc[0] + ba[1] * bc[1]
        dlug_wek_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
        dlug_wek_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)
        if dlug_wek_ba * dlug_wek_bc == 0: return 0
        cos_kata = max(-1, min(1, il_skalarny / (dlug_wek_ba * dlug_wek_bc)))
        return math.degrees(math.acos(cos_kata))

    def get_data(self, landmarks, w, h):
        p = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]
        # KOŃCZYNY
        data = {}
        data['l_bark'], data['p_bark'] = p[11], p[12]
        data['l_lokiec'], data['p_lokiec'] = p[13], p[14]
        data['l_nadgarstek'], data['p_nadgarstek'] = p[15], p[16]
        data['l_biodro'], data['p_biodro'] = p[23], p[24]
        data['l_kolano'], data['p_kolano'] = p[25], p[26]
        data['l_kostka'], data['p_kostka'] = p[27], p[28]

        # OBLICZENIA
        data['kat_l_lokiec'] = self.oblicz_kat(data['l_bark'], data['l_lokiec'], data['l_nadgarstek'])
        data['kat_p_lokiec'] = self.oblicz_kat(data['p_bark'], data['p_lokiec'], data['p_nadgarstek'])
        data['kat_l_kolano'] = self.oblicz_kat(data['l_biodro'], data['l_kolano'], data['l_kostka'])
        data['kat_p_kolano'] = self.oblicz_kat(data['p_biodro'], data['p_kolano'], data['p_kostka'])

        odl_n = self.odleglosc(data['l_nadgarstek'], data['p_nadgarstek'])
        odl_b = self.odleglosc(data['l_bark'], data['p_bark'])

        data['dlonie_razem'] = odl_n < (odl_b * 0.6)
        data['nogi_ugiete'] = data['kat_l_kolano'] < 160 or data['kat_p_kolano'] < 160
        data['rece_przed'] = abs(data['l_nadgarstek'][0] - data['p_nadgarstek'][0]) < odl_b * 1.5

        return data