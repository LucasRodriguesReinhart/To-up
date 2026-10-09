# sn_hills_tex.py - ruido do relevo (compartilhado) + TEXTURA PINTADA DAS COLINAS (projecao plana sobre o anel inteiro,
# 2600 x 2600 studs em 1024 px): verdes em manchas largas, campos dourados suaves e as manchas escuras dos BOSQUES no
# MESMO lugar onde o sn_relief planta os pinheiros (mesmo ruido, mesma semente). Sem bpy (roda no python comum).
import numpy as np

HILL_SPAN = 2600.0


class Noise:
    def __init__(self, seed):
        r = np.random.default_rng(seed)
        self.g = r.random((257, 257))
        self.g[256, :] = self.g[0, :]            # periodico: sem costura no salto 255 -> 0
        self.g[:, 256] = self.g[:, 0]

    def v(self, x, y):
        """value noise 2D (x, y em unidades de celula)"""
        xi = np.floor(x).astype(int) % 256
        yi = np.floor(y).astype(int) % 256
        fx = x - np.floor(x)
        fy = y - np.floor(y)
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        a, b = self.g[yi, xi], self.g[yi, xi + 1]
        c, d = self.g[yi + 1, xi], self.g[yi + 1, xi + 1]
        return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

    def fbm(self, x, y, oct=4):
        s, amp, tot = 0.0, 1.0, 0.0
        for k in range(oct):
            s = s + amp * self.v(x * (2 ** k) + 17 * k, y * (2 ** k) + 31 * k)
            tot += amp
            amp *= 0.5
        return s / tot

    def ridged(self, x, y, oct=5):
        s, amp, tot = 0.0, 1.0, 0.0
        for k in range(oct):
            n = self.v(x * (2 ** k) + 7 * k, y * (2 ** k) + 13 * k)
            s = s + amp * (1.0 - np.abs(2 * n - 1)) ** 2
            tot += amp
            amp *= 0.5
        return s / tot


def fields(N, X, Z):
    return N.v(X / 70.0 + 300, Z / 70.0 + 300), N.fbm(X / 90.0 + 500, Z / 90.0 + 500, 3)


def tex_hills(n=1024, seed=4242):
    N = Noise(seed)
    s = (np.arange(n) + 0.5) / n
    U, Vv = np.meshgrid(s, s)
    X = (U - 0.5) * HILL_SPAN
    Z = (0.5 - Vv) * HILL_SPAN                     # linha 0 do PNG = v 1 = Z +SPAN/2 (uv v = 0.5 + Z/SPAN)
    f1, f2 = fields(N, X, Z)

    def sm(a, b, x):
        t = np.clip((x - a) / (b - a), 0, 1)
        return t * t * (3 - 2 * t)
    base = np.array([112, 164, 72]) / 255.0
    light = np.array([150, 186, 88]) / 255.0
    gold = np.array([190, 186, 100]) / 255.0
    dark = np.array([62, 104, 58]) / 255.0
    img = base[None, None, :] * np.ones((n, n, 1))
    img = img * (1 - sm(0.45, 0.7, f1)[..., None] * 0.7) + light * sm(0.45, 0.7, f1)[..., None] * 0.7
    g = N.v(X / 140.0 + 900, Z / 140.0 + 900)
    img = img * (1 - sm(0.68, 0.82, g)[..., None] * 0.55) + gold * sm(0.68, 0.82, g)[..., None] * 0.55
    fm = sm(0.55, 0.64, f2)[..., None]
    img = img * (1 - fm) + dark * fm
    fine = N.fbm(X / 18.0 + 77, Z / 18.0 + 77, 2)
    img = img * (0.94 + 0.12 * fine)[..., None]
    a = np.ones((n, n, 1))
    return np.concatenate([np.clip(img, 0, 1), a], axis=2)
