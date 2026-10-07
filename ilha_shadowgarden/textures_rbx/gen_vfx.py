# gen_vfx.py - texturas proprias dos efeitos da Ilha 3 (RGBA, brancas: a cor vem do ParticleEmitter/ImageColor3).
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
random.seed(3); np.random.seed(3)
def save(a, nome):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").save(nome); print("ok", nome)
def grid(n):
    y, x = np.mgrid[0:n, 0:n].astype(float); c = (n - 1) / 2
    return (x - c) / c, (y - c) / c
# 1) linhas de velocidade de tela: raios finos das bordas para o centro, centro limpo
N = 1024; X, Y = grid(N); r = np.hypot(X, Y); ang = np.arctan2(Y, X)
lines = np.zeros((N, N))
for _ in range(150):
    a0 = random.uniform(-math.pi, math.pi); w = random.uniform(0.002, 0.007); r0 = random.uniform(0.42, 0.8)
    d = np.abs((ang - a0 + math.pi) % (2 * math.pi) - math.pi)
    wr = w * (r / 0.8)
    m = np.clip(1 - d / np.maximum(wr, 1e-4), 0, 1) * np.clip((r - r0) / 0.25, 0, 1)
    lines = np.maximum(lines, m * random.uniform(0.6, 1.0))
A = lines * 255; save(np.dstack([np.full_like(A, 255)] * 3 + [A]), "VFX_speedlines_tela.png")
# 2) risco de energia (particula alongada): nucleo fino brilhante, halo suave, pontas afinando
W, H = 512, 64
x = np.linspace(-1, 1, W)[None, :]; y = np.linspace(-1, 1, H)[:, None]
taper = np.clip(1 - np.abs(x) ** 2.2, 0, 1)
core = np.exp(-(y / (0.10 * taper + 1e-3)) ** 2) * taper
halo = np.exp(-(y / (0.45 * taper + 1e-3)) ** 2) * taper * 0.45
A = np.clip(core + halo, 0, 1) * 255
save(np.dstack([np.full_like(A, 255)] * 3 + [A]), "VFX_risco.png")
# 3) disco de acrecao (vista de frente): bracos em espiral finos e longos (riscos de luz), borda interna clara
N = 1024; img = Image.new("L", (N, N), 0); d = ImageDraw.Draw(img); c = N / 2
for k in range(70):
    a0 = random.uniform(0, 2 * math.pi); r0 = random.uniform(0.33, 0.62); r1 = r0 + random.uniform(0.18, 0.40)
    w = random.uniform(2, 7); val = random.randint(120, 255)
    pts = []
    for i in range(40):
        t = i / 39; rr = r0 + (r1 - r0) * t; aa = a0 + t * random.uniform(1.4, 2.2)   # espiral
        pts.append((c + math.cos(aa) * rr * c * 0.98, c + math.sin(aa) * rr * c * 0.98))
    for i in range(39):
        fade = math.sin(math.pi * i / 39)
        d.line([pts[i], pts[i + 1]], fill=int(val * fade), width=max(1, int(w * (1 - 0.6 * i / 39))))
d.ellipse((c - 0.36 * c, c - 0.36 * c, c + 0.36 * c, c + 0.36 * c), outline=255, width=14)
A = np.asarray(img.filter(ImageFilter.GaussianBlur(2.5)), dtype=float)
X, Y = grid(N); r = np.hypot(X, Y)
A = A * np.clip((r - 0.30) / 0.04, 0, 1) * np.clip((1.02 - r) / 0.2, 0, 1)
A = np.clip(A * 1.4, 0, 255)
save(np.dstack([np.full_like(A, 255)] * 3 + [A]), "VFX_disco_acrecao.png")
# 4) vinheta de tela (preta nas bordas, centro transparente)
N = 512; X, Y = grid(N); r = np.hypot(X * 0.9, Y)
A = np.clip((r - 0.45) / 0.75, 0, 1) ** 1.4 * 255
save(np.dstack([np.zeros_like(A)] * 3 + [A]), "VFX_vinheta.png")
# 5) rachaduras no chao (pretas, ramificadas, alpha)
N = 1024; img = Image.new("L", (N, N), 0); d = ImageDraw.Draw(img)
def crack(x, y, a, L, w, depth):
    pts = [(x, y)]
    for i in range(int(L / 14)):
        a += random.gauss(0, 0.13); x += math.cos(a) * 14; y += math.sin(a) * 14; pts.append((x, y))
        if depth < 3 and random.random() < 0.08: crack(x, y, a + random.choice([-1, 1]) * random.uniform(0.5, 1.1), L * 0.45, w * 0.6, depth + 1)
    for i in range(len(pts) - 1):
        ww = max(1, int(w * (1 - i / len(pts))))
        d.line([pts[i], pts[i + 1]], fill=255, width=ww)
for k in range(9):
    a = k / 9 * 2 * math.pi + random.uniform(-0.2, 0.2)
    crack(N / 2, N / 2, a, random.uniform(300, 470), random.uniform(20, 30), 0)
d.ellipse((N / 2 - 60, N / 2 - 60, N / 2 + 60, N / 2 + 60), fill=255)
A = np.asarray(img.filter(ImageFilter.GaussianBlur(1.2)), dtype=float)
save(np.dstack([np.zeros_like(A)] * 3 + [A]), "VFX_rachaduras.png")
