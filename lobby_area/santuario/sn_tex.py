# sn_tex.py - texturas do lobby SANTUARIO DO DEUS-FERREIRO (pedra antiga de templo, frisos de runas, basalto da
# bigorna-tita, bronze com patina, musgo). Mesmo padrao do wb_tex (V2): tileaveis 1024 px, albedo completo,
# convencao U ao longo da peca / V para cima. Geradas fora do Blender (numpy + scipy).
# uso: python sn_tex.py [--force] [chaves...]
import math
import os
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "wolfberg"))
import wb_tex as T
from wb_tex import N, fbm, smoothstep, grid, rgb, solid, rgba, mix, cells, lloyd, bevel_shade, write_png

TEX_DIR = os.path.join(HERE, "textures")
VERSION = 1
_T = {"sn_ashlar": 8.0, "sn_ashlar_dark": 8.0, "sn_ashlar_moss": 8.0, "sn_carved": 8.0, "sn_basalt": 14.0,
      "sn_bronze": 5.0, "sn_moss": 8.0, "sn_wood_aged": 6.0, "sn_plaza": 10.0, "sn_rubble": 6.0,
      "sn_rock_far": 90.0, "sn_snow_far": 120.0, "sn_mountain": 1.0, "sn_hills": 1.0}
TEXTURES = {k: ("SN_%s_v%d.png" % (k[3:], VERSION), t) for k, t in _T.items()}


# ------------------------------------------------------------------ cantaria (blocos retangulares em fiadas)
def ashlar_cells(rng, rows=4, wmin=0.16, wmax=0.38):
    """blocos retangulares tileaveis: devolve (id, e = distancia a junta, dtop = distancia ao topo do bloco,
    corner = distancia ao canto mais proximo) em unidades de textura"""
    u, v = grid()
    row = np.floor(v * rows).astype(int) % rows
    fv = (v * rows) % 1.0
    ids = np.zeros((N, N), dtype=int)
    dx = np.zeros((N, N))
    du_c = np.zeros((N, N))
    nid = 0
    for r in range(rows):
        ws = []
        tot = 0.0
        while tot < 1.0:
            w = rng.uniform(wmin, wmax)
            ws.append(w)
            tot += w
        ws = np.array(ws) / tot
        cuts = np.concatenate([[0.0], np.cumsum(ws)])
        off = rng.uniform(0, 1)
        m = row == r
        uu = (u[m] + off) % 1.0
        k = np.clip(np.searchsorted(cuts, uu, side="right") - 1, 0, len(ws) - 1)
        ids[m] = nid + k
        a = uu - cuts[k]
        b = cuts[k + 1] - uu
        dx[m] = np.minimum(a, b)
        nid += len(ws)
    dy = np.minimum(fv, 1 - fv) / rows
    e = np.minimum(dx, dy)
    dtop = fv / rows                          # fv = 0 no topo da fiada (y da imagem cresce para baixo)
    corner = np.hypot(dx, dy)
    return ids, e, dtop, corner, nid


def ashlar(rng, pal, mortar, rows=4, moss=0.0, dark=False, chip=0.35):
    ids, e, dtop, corner, n = ashlar_cells(rng, rows)
    pal = np.array([rgb(c) for c in pal])
    base = (pal[rng.integers(0, len(pal), n)] * rng.uniform(0.9, 1.08, (n, 1)))[ids]
    gap, bev = 0.004, 0.022
    # cantos lascados: alguns blocos perdem o canto (arredonda forte)
    chipk = rng.random(n)[ids] < chip
    e2 = np.where(chipk & (corner < 0.05), e - (0.05 - corner) * 0.6, e)
    h = smoothstep(gap, gap + bev, e2)
    from scipy.ndimage import gaussian_filter
    hs = gaussian_filter(h, sigma=4, mode="wrap")
    sh = 1.0 + (bevel_shade(hs) - 1.0) * 0.7
    weather = fbm(rng, 5, 4)
    fine = fbm(rng, 48, 3)
    pits = smoothstep(0.7, 0.76, fbm(rng, 28, 2)) * 0.05
    img = base * (sh * (0.93 + 0.09 * (weather - 0.5) + 0.06 * fine - pits))[:, :, None]
    # escorrido escuro descendo das juntas (chuva)
    streak = fbm(rng, 3, 3, ax=6.0, ay=0.35)
    img = img * (1 - 0.1 * smoothstep(0.55, 0.8, streak))[:, :, None]
    cr = smoothstep(0.01, 0.0, np.abs(fbm(rng, 9, 3) - 0.5)) * (h > 0.9) * (rng.random(n)[ids] < 0.4)
    img = mix(img, img * 0.62, cr * 0.8)
    mort = solid(mortar) * (0.85 + 0.25 * fbm(rng, 30, 2))[:, :, None]
    img = mix(mort, img, smoothstep(gap * 0.3, gap, e2))
    if moss > 0:
        mm = smoothstep(0.42, 0.7, fbm(rng, 4, 4)) * (smoothstep(0.03, 0.0, dtop) * 0.9 + smoothstep(0.012, 0.0, e) * 0.8)
        mm = np.clip(mm + smoothstep(0.66, 0.8, fbm(rng, 6, 3)) * 0.6, 0, 1) * moss
        mcol = mix(solid((74, 112, 46)), solid((112, 150, 62)), fbm(rng, 40, 2))
        img = mix(img, mcol, mm)
    return rgba(img)


def tex_ashlar(rng):
    return ashlar(rng, [(196, 184, 160), (182, 172, 152), (204, 192, 168), (176, 166, 150), (190, 176, 150)],
                  (96, 86, 72))


def tex_ashlar_dark(rng):
    return ashlar(rng, [(132, 124, 116), (120, 114, 108), (142, 132, 120), (112, 106, 100)], (60, 54, 50), rows=3)


def tex_ashlar_moss(rng):
    return ashlar(rng, [(190, 180, 158), (176, 168, 150), (198, 188, 166), (170, 162, 148)], (90, 82, 68), moss=1.0)


# ------------------------------------------------------------------ friso de runas (faixas gravadas)
def glyph_mask(rng, cols, rows_y, y0, y1):
    """gravacoes: em cada celula um glifo de 3-5 tracos (retas e arcos curtos). Devolve mascara 0..1"""
    u, v = grid()
    m = np.zeros((N, N))
    cw = 1.0 / cols
    for c in range(cols):
        x0 = c * cw
        for t in range(int(rng.integers(3, 6))):
            g3 = (0.2, 0.5, 0.8)                     # glifo em grade 3x3 (aspecto de runa)
            ax, ay = g3[int(rng.integers(0, 3))], g3[int(rng.integers(0, 3))]
            if rng.random() < 0.85:
                bx_, by_ = g3[int(rng.integers(0, 3))], g3[int(rng.integers(0, 3))]
                if (bx_, by_) == (ax, ay):
                    by_ = 0.8 if ay < 0.5 else 0.2
            else:
                bx_, by_ = ax, ay
            # segmento em coordenadas de textura
            p0 = np.array([x0 + ax * cw, y0 + ay * (y1 - y0)])
            p1 = np.array([x0 + bx_ * cw, y0 + by_ * (y1 - y0)])
            xs0, xs1 = int(max(0, (min(p0[0], p1[0]) - 0.01) * N)), int(min(N, (max(p0[0], p1[0]) + 0.01) * N))
            ys0, ys1 = int(max(0, (min(p0[1], p1[1]) - 0.01) * N)), int(min(N, (max(p0[1], p1[1]) + 0.01) * N))
            if xs1 <= xs0 or ys1 <= ys0:
                continue
            uu, vv = u[ys0:ys1, xs0:xs1], v[ys0:ys1, xs0:xs1]
            d = p1 - p0
            L2 = max(1e-9, d.dot(d))
            tt = np.clip(((uu - p0[0]) * d[0] + (vv - p0[1]) * d[1]) / L2, 0, 1)
            dist = np.hypot(uu - (p0[0] + tt * d[0]), vv - (p0[1] + tt * d[1]))
            if L2 < 1e-6:
                dist = np.abs(dist - 0.012)                 # anel pequeno
            m[ys0:ys1, xs0:xs1] = np.maximum(m[ys0:ys1, xs0:xs1], smoothstep(0.0075, 0.0045, dist))
    return m


def tex_carved(rng):
    img = ashlar(rng, [(196, 186, 164), (186, 176, 156), (202, 192, 170)], (98, 88, 74), rows=2, chip=0.2)[:, :, :3]
    u, v = grid()
    # faixa de friso no meio de cada fiada (2 fiadas por tile -> 2 faixas)
    band = np.zeros((N, N))
    gm = np.zeros((N, N))
    for (y0, y1) in ((0.12, 0.38), (0.62, 0.88)):
        band = np.maximum(band, ((v > y0) & (v < y1)).astype(float))
        gm = np.maximum(gm, glyph_mask(rng, 7, 1, y0 + 0.03, y1 - 0.03))
        for yl in (y0, y1):
            gm = np.maximum(gm, smoothstep(0.004, 0.0015, np.abs(v - yl)))
    img = mix(img, img * 0.93, band * 0.5)
    img = mix(img, img * 0.45, gm)                              # sulco escuro
    # realce claro logo abaixo do sulco (luz de cima)
    gm_shift = np.roll(gm, 3, axis=0)
    img = mix(img, np.clip(img * 1.18, 0, 1), np.clip(gm_shift - gm, 0, 1) * 0.8)
    return rgba(img)


# ------------------------------------------------------------------ basalto da bigorna, bronze, musgo, madeira
def tex_basalt(rng):
    pts = lloyd(rng, 22, 1)
    cid, e, f1, cu, cv = cells(pts, 1.0, 1.25)
    m = len(pts)
    ang = rng.uniform(0, 2 * np.pi, m)
    shade = 0.95 + 0.18 * (np.cos(ang)[cid] * cu + np.sin(ang)[cid] * cv) * 7
    shade = np.clip(shade, 0.7, 1.25) - 0.28 * smoothstep(0.01, 0.0, e)
    pal = np.array([rgb(c) for c in [(92, 86, 84), (80, 76, 76), (100, 92, 88), (86, 80, 80)]])
    base = pal[rng.integers(0, 4, m)][cid]
    u, v = grid()
    strata = 0.5 + 0.5 * np.sin((v * 7 + fbm(rng, 3, 3) * 2.0) * 2 * np.pi)
    img = base * (shade * (0.92 + 0.1 * strata) * (0.9 + 0.14 * fbm(rng, 36, 3)))[:, :, None]
    # leve calor avermelhado nas fendas (o brilho de verdade e geometria Neon)
    hot = smoothstep(0.006, 0.0, e) * smoothstep(0.55, 0.75, fbm(rng, 5, 3))
    img = mix(img, solid((150, 70, 40)), hot * 0.5)
    return rgba(img)


def tex_bronze(rng):
    low = fbm(rng, 4, 4)
    fine = fbm(rng, 40, 3)
    img = solid((128, 92, 52)) * (0.85 + 0.25 * low + 0.1 * fine)[:, :, None]
    pat = smoothstep(0.55, 0.75, fbm(rng, 10, 4))
    img = mix(img, solid((84, 138, 118)) * (0.85 + 0.25 * fine)[:, :, None], pat * 0.7)
    img = mix(img, solid((70, 46, 26)), smoothstep(0.7, 0.85, fbm(rng, 12, 3)) * 0.4)
    return rgba(img)


def tex_moss(rng):
    img = T.dabs(rng, [(76, 116, 46), (90, 132, 54), (64, 102, 40), (104, 142, 60)], (44, 70, 30), 900, 0.02, 0.05)
    flowers = rng.random((N, N)) > 0.9994
    img[flowers] = rgb((210, 220, 250))
    return rgba(img * (0.95 + 0.1 * fbm(rng, 30, 2))[:, :, None])


def tex_wood_aged(rng):
    img = T.wood_grain(rng, (122, 104, 86), (82, 68, 56), knots=4)[:, :, :3]
    cr = smoothstep(0.012, 0.0, np.abs(fbm(rng, 6, 3, ax=0.2, ay=6.0) - 0.5))
    img = mix(img, img * 0.6, cr * 0.7)
    return rgba(img)


def tex_plaza(rng):
    """lajes grandes da praca das runas: pedra clara quase sem junta de grama, mais nobre que wb_flag"""
    pts = lloyd(rng, 18, 2)
    pal = [(206, 196, 176), (196, 186, 166), (214, 202, 180), (190, 180, 162)]
    return rgba(T.stone_field(rng, pts, pal, (120, 108, 90), 0.006, 0.03, var=0.04, crack=0.4, dome=0.05, light_k=0.4))


def tex_rubble(rng):
    pts = lloyd(rng, 70, 1)
    pal = [(170, 160, 142), (150, 142, 128), (184, 172, 152), (132, 126, 118)]
    return rgba(T.stone_field(rng, pts, pal, (92, 104, 60), 0.014, 0.05, var=0.08, grass=(96, 128, 58), dome=0.6))


def tex_rock_far(rng):
    return T.tex_rock(rng)


def tex_snow_far(rng):
    return T.tex_snow(rng)


def tex_mountain(rng):
    """RAMPA PINTADA da cordilheira (UV explicito: u = volta em torno do lago x5, periodico; v = altura/650).
    Rocha azulada com veios verticais (ravinas), mais clara no alto (perspectiva aerea), neve com borda ondulada que
    desce pelas ravinas, sombra azul na neve. Sem celulas/pedras: de longe uma serra e cor e forma, nao detalhe."""
    u, v = grid()
    h = 1.0 - v                                                    # linha 0 do PNG = topo = alto da serra
    rav = fbm(rng, 6, 4, ax=1.0, ay=0.17)                          # ravinas: compridas na vertical
    rav2 = fbm(rng, 14, 3, ax=1.0, ay=0.15)
    blot = fbm(rng, 3, 3)
    low = rgb((96, 112, 128))
    mid = rgb((126, 138, 158))
    top = rgb((168, 178, 198))
    t = np.clip(h / 0.75, 0, 1)[:, :, None]
    base = low * (1 - t) + mid * t
    base = mix(base, top, smoothstep(0.35, 0.8, h) * 0.6)
    ridge = smoothstep(0.42, 0.62, rav)
    shade = 0.78 + 0.34 * ridge + 0.14 * (rav2 - 0.5) + 0.08 * (blot - 0.5)
    img = base * shade[:, :, None]
    # neve: linha ondulada (varia em u) que desce pelas ravinas
    gul = fbm(rng, 22, 3, ax=1.0, ay=0.12)
    line = (0.60 + 0.30 * (fbm(rng, 4, 3, ax=1.0, ay=0.05) - 0.5) - 0.22 * smoothstep(0.45, 0.75, rav)
            - 0.16 * smoothstep(0.55, 0.8, gul))
    snow = smoothstep(line - 0.012, line + 0.012, h)
    snow = np.maximum(snow, smoothstep(0.80, 0.84, h))
    snow_c = rgb((236, 241, 248))
    snow_s = rgb((186, 200, 224))
    sc = mix(snow_s, snow_c, smoothstep(0.30, 0.55, rav) * 0.85 + 0.15)
    img = mix(img, sc, snow)
    # pe da serra puxando para o verde-azulado do bosque distante
    img = mix(img, rgb((84, 112, 100)), smoothstep(0.24, 0.10, h) * 0.7)
    return rgba(img)


def tex_hills(rng):
    import sn_hills_tex
    return sn_hills_tex.tex_hills()


GEN = {k: globals()["tex_" + k[3:]] for k in _T}


def path(key):
    return os.path.join(TEX_DIR, TEXTURES[key][0])


def ensure(force=False, only=None):
    os.makedirs(TEX_DIR, exist_ok=True)
    done = {}
    for key, (fn, tile) in sorted(TEXTURES.items()):
        if only and key not in only:
            continue
        p = os.path.join(TEX_DIR, fn)
        if force or not os.path.exists(p):
            try:
                import scipy  # noqa: F401
            except ImportError:
                raise RuntimeError("textura %s faltando: gere fora do Blender com 'python sn_tex.py'" % fn)
            rng = np.random.default_rng(5000 + zlib.crc32(key.encode()) % 10000)
            write_png(p, GEN[key](rng))
            print("TEX", key, fn)
        done[key] = p
    return done


if __name__ == "__main__":
    only = [a for a in sys.argv[1:] if a in TEXTURES] or None
    ensure(force="--force" in sys.argv, only=only)
    from PIL import Image, ImageDraw
    keys = sorted(TEXTURES)
    cell = 300
    sh = Image.new("RGB", (5 * cell, 2 * cell))
    d = ImageDraw.Draw(sh)
    for i, k in enumerate(keys):
        im = Image.open(path(k)).convert("RGB").resize((cell, cell))
        x, y = (i % 5) * cell, (i // 5) * cell
        sh.paste(im, (x, y))
        d.rectangle([x, y, x + 120, y + 14], fill=(0, 0, 0))
        d.text((x + 3, y + 1), k, fill=(255, 255, 0))
    sh.save(os.path.join(TEX_DIR, "_sheet.png"))
    print("SHEET ok")
