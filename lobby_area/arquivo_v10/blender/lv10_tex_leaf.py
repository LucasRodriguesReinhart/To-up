# lv10_tex_leaf.py - texturas de folhagem estilizada (manchas de 3 tons, sem ruido fotografico)
# Aplicadas com box-UV de mundo nas copas (alamos dourados / arvores verdes) para dar leitura de massa foliar.
import os
import numpy as np
from PIL import Image

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\export\tex"
rng = np.random.default_rng(3)

def save(name, arr):
    Image.fromarray((np.clip(arr, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, name)); print('tex', name)

def smooth_noise(S, cells, seed, octaves=3):
    r = np.random.default_rng(seed)
    acc = np.zeros((S, S)); amp = 1; tot = 0
    for o in range(octaves):
        c = cells * (2 ** o)
        g = r.random((c + 1, c + 1)); g[-1, :] = g[0, :]; g[:, -1] = g[:, 0]
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((S, S), Image.BICUBIC)
        acc += np.asarray(img, dtype=np.float32) / 255 * amp; tot += amp; amp *= .5
    return acc / tot

def leaves(name, dark, mid, light, seed, S=256):
    n1 = smooth_noise(S, 5, seed); n2 = smooth_noise(S, 14, seed + 1, 2)
    t = np.clip((n1 - .5) * 2.2 + .5 + (n2 - .5) * .9, 0, 1)
    # tres patamares (cel-shading suave)
    band = np.where(t < .38, 0.0, np.where(t < .7, .5, 1.0))
    band = band * .8 + t * .2
    d, m, l = np.array(dark) / 255, np.array(mid) / 255, np.array(light) / 255
    img = np.where(band[..., None] < .5, d + (m - d) * (band[..., None] / .5), m + (l - m) * ((band[..., None] - .5) / .5))
    # "folhinhas": pontos claros pequenos
    for _ in range(140):
        cx, cy = rng.integers(1, S - 2, 2)
        img[cy:cy + 2, cx:cx + 2] = l * 1.04
    save(name + '.png', img)

leaves('t_leaf_gold', (196, 138, 40), (232, 184, 70), (250, 220, 120), 11)
leaves('t_leaf_gold2', (170, 116, 30), (214, 160, 52), (240, 200, 96), 13)
leaves('t_leaf_green', (52, 118, 56), (92, 168, 80), (140, 208, 110), 17)
print('done')
