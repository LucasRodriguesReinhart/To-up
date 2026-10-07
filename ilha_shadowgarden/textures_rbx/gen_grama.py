# gen_grama.py - textura de grama PINTADA (vista de cima, estilo fundo de anime, tileavel) da Ilha 3 para o ColorMap
# de um MaterialVariant. Quase neutra e clara: o tom final vem da Color calibrada de cada peca (o Roblox multiplica).
# Camadas: manchas grandes de tom (pintura em 3 valores) -> pinceladas curtas em leque/direcoes variadas com
# transparencia -> respingos de luar. Todo filtro e periodico (pad wrap) para nao marcar emenda.
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
random.seed(5); np.random.seed(5)
S = 2048; OUT = 1024
def wrap_blur(im, r):
    w, h = im.size; pad = int(r * 3) + 2
    big = Image.new(im.mode, (w + 2 * pad, h + 2 * pad))
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            big.paste(im, (pad + ox * w, pad + oy * h))
    return big.filter(ImageFilter.GaussianBlur(r)).crop((pad, pad, pad + w, pad + h))
def tile_noise(freq):
    g = np.random.rand(freq, freq)
    acc = np.zeros((S, S)); xs = np.arange(S) / S * freq
    x0 = np.floor(xs).astype(int); fx = xs - x0; fx = fx * fx * (3 - 2 * fx)
    a = g[np.ix_(x0 % freq, x0 % freq)]; b = g[np.ix_(x0 % freq, (x0 + 1) % freq)]
    c = g[np.ix_((x0 + 1) % freq, x0 % freq)]; e = g[np.ix_((x0 + 1) % freq, (x0 + 1) % freq)]
    FX = fx[None, :]; FY = fx[:, None]
    return (a * (1 - FX) + b * FX) * (1 - FY) + (c * (1 - FX) + e * FX) * FY
patch = 0.55 * tile_noise(3) + 0.3 * tile_noise(6) + 0.15 * tile_noise(12)
patch = (patch - patch.min()) / (patch.max() - patch.min())
lv = np.where(patch < 0.4, 0.72, np.where(patch < 0.68, 0.79, 0.86))
bg = np.asarray(wrap_blur(Image.fromarray((lv * 255).astype(np.uint8)), 22), dtype=float) / 255.0
rgb = np.stack([bg * 0.88, bg * 1.0, bg * 0.96], -1) * 215
canvas = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).convert("RGBA")
layer = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
def poly_wrap(pts, fill):
    for ox in (-S, 0, S):
        for oy in (-S, 0, S):
            d.polygon([(x + ox, y + oy) for x, y in pts], fill=fill)
def stroke(x, y, L, w, ang, curv, col):
    n = 6; l, r = [], []
    for i in range(n + 1):
        t = i / n; a = ang + curv * t
        cx = x + math.sin(a) * L * t; cy = y - math.cos(a) * L * t
        ww = w * math.sin(math.pi * (0.15 + 0.85 * t) / 1.0) * (1 - 0.6 * t) + 0.5
        nx, ny = math.cos(a), math.sin(a)
        l.append((cx - nx * ww, cy - ny * ww)); r.append((cx + nx * ww, cy + ny * ww))
    poly_wrap(l + r[::-1], col)
# pinceladas: escuras nos vales, medias em toda parte, claras (luar) nos altos; leques de 3-5 com direcao comum
for _ in range(2300):
    x = random.uniform(0, S); y = random.uniform(0, S); c = patch[int(y) % S, int(x) % S]
    base_ang = random.uniform(-math.pi, math.pi)
    k = random.random()
    if k < 0.42 - 0.2 * c:   v, al = 0.48, 190
    elif k < 0.82:           v, al = 0.70, 170
    else:                    v, al = 1.05, 175 if c > 0.45 else 110
    for b in range(random.randint(3, 5)):
        stroke(x + random.gauss(0, 7), y + random.gauss(0, 7), random.uniform(46, 90), random.uniform(6.5, 10.5),
               base_ang + random.gauss(0, 0.45), random.gauss(0, 0.5),
               (int(200 * v * 0.88), int(200 * v), int(200 * v * 0.96), al))
canvas = Image.alpha_composite(canvas, wrap_blur(layer, 1.6)).convert("RGB")
img = wrap_blur(canvas, 1.0).resize((OUT, OUT), Image.LANCZOS)
# o Roblox MULTIPLICA o ColorMap pela Color da peca: media ~205 mantem o tom calibrado do montar (sem escurecer)
arr = np.asarray(img, dtype=float); arr = np.clip(arr * (205.0 / arr.mean()), 0, 255)
img = Image.fromarray(arr.astype(np.uint8))
img.save("SG_GramaNoturna_color.png")
t = Image.open("SG_GramaNoturna_color.png"); p = Image.new("RGB", (OUT * 3, OUT * 3))
for i in range(3):
    for j in range(3): p.paste(t, (i * OUT, j * OUT))
tint = np.asarray(p, dtype=float) * np.array([40, 62, 54]) / 255.0 * 1.0
Image.fromarray(np.clip(tint, 0, 255).astype(np.uint8)).resize((1024, 1024)).save("_previa_tile_tingida.jpg")
print("ok", np.asarray(img).mean())
