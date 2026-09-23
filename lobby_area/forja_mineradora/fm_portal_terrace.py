# fm_portal_terrace - dressing do terraco dos portais:
#   * cada escada anuncia o seu mundo (so dressing na borda do poco: a geometria de TER_PortalStairs, a largura util
#     dos lances e as rotas nao mudam). As pecas vao para o MB do proprio portal (dentro do lote px +-14):
#       Naruto: toro de pedra, nobori e sakura      DB: pedestais com as 7 esferas subindo ao lado
#       Shadow: grade gotica de ferro e velas roxas  DS: pergola de glicinia e lanternas de papel vermelhas
#       OP: corrimao de corda, tabuas de cais, barris  OPM: guarda-corpo de concreto com faixa neon, outdoor
#   * PORTAL_<key>_Difficulty: placa de dificuldade (1..6 pontos, moldura na cor do portal) + caixote de cristais
#     na cor do portal (minerio vindo daquele mundo) ao pe de cada escada
#   * PORTAL_Terrace_Dressing: so o centro do terraco (x -26..26), entre Shadow e Demon Slayer: ruina gotica,
#     arvore morta e cristais (lado sombrio) | glicinia, toro escuro e mureta (lado DS). Os vaos de 4 studs entre
#     portais vizinhos ficam limpos (cada portal e uma peca independente).
import math
from mathutils import Vector
from fm_lib import MB, D, col_box
from fm_parts import crystal_cluster, crate, barrel
import fm_portal_kit as K
from fm_portal_kit import V, GLOW
import fm_layout as L

T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
A = "Portal"
SY0, SY1 = 86.0, 99.4      # faixa ao lado do lance 2 (terraco, fora do poco px +-7.4)


def wisteria_tree(mb, loc, h, rng, xmax=None):
    """glicinia em guarda-chuva; xmax limita a copa e os cachos (folga de 4 studs ate o lote do portal vizinho)"""
    x, y, z = loc
    pts = [V(x, y, z), V(x + 0.7, y - 0.3, z + h * 0.3), V(x - 0.4, y + 0.3, z + h * 0.55), V(x + 0.3, y, z + h * 0.7)]
    K.taper_tube(mb, pts, [h * 0.075, h * 0.058, h * 0.046, h * 0.03], "Bark", 6)
    for i in range(3):
        a = rng.uniform(0, math.tau)
        p = pts[2] + V(math.cos(a) * h * 0.25, math.sin(a) * h * 0.25, h * 0.14)
        K.taper_tube(mb, [pts[2], p], [h * 0.035, h * 0.018], "Bark", 5)
    # copa larga e baixa (guarda-chuva) de folhagem, com os cachos lilas pendendo da borda
    for i in range(5):
        a = i * math.tau / 5 + rng.uniform(-0.3, 0.3)
        r = h * rng.uniform(0.14, 0.26)
        rad = h * rng.uniform(0.19, 0.24)
        c = V(x + math.cos(a) * r, y + math.sin(a) * r, z + h * rng.uniform(0.78, 0.86))
        if xmax is not None:
            c.x = min(c.x, xmax - rad * 1.45)
        mb.ico(rad, c, "Leaf_Pine_Light", 1, (1.15, 1.15, 0.45), jitter=0.25)
    for i in range(14):
        a = i * math.tau / 14 + rng.uniform(-0.15, 0.15)
        r = h * rng.uniform(0.26, 0.38)
        top = V(x + math.cos(a) * r, y + math.sin(a) * r, z + h * rng.uniform(0.76, 0.8))
        if xmax is not None:
            top.x = min(top.x, xmax - 0.8)
        K.raceme(mb, top, rng.uniform(2.0, 3.4), "P_DS_Wisteria", 0.5, rng)


def dead_tree(mb, loc, h, rng, m="P_Shadow_Stone"):
    x, y, z = loc
    pts = [V(x, y, z - 0.3), V(x + 0.5, y + 0.2, z + h * 0.3), V(x - 0.6, y - 0.1, z + h * 0.6), V(x - 0.2, y, z + h * 0.85)]
    K.taper_tube(mb, pts, [h * 0.08, h * 0.055, h * 0.035, h * 0.012], m, 6)
    for i, (f, a, l) in enumerate(((0.45, 0.4, 0.42), (0.58, 2.6, 0.36), (0.7, 4.3, 0.3), (0.35, 5.4, 0.28))):
        b = pts[1] + (pts[2] - pts[1]) * ((f - 0.3) / 0.3) if f < 0.6 else pts[2] + (pts[3] - pts[2]) * ((f - 0.6) / 0.25)
        e1 = b + V(math.cos(a) * h * l * 0.55, math.sin(a) * h * l * 0.55, h * l * 0.35)
        e2 = e1 + V(math.cos(a + 0.6) * h * l * 0.45, math.sin(a + 0.6) * h * l * 0.45, h * l * 0.5)
        K.taper_tube(mb, [b, e1, e2], [h * 0.03, h * 0.016, h * 0.004], m, 5)
    K.mossy_rock(mb, (x + 0.8, y - 0.6, z), (2.0, 1.6, 1.0), rng, "Cliff_Rock_Dark", moss=None)


def capsule(mb, loc, yaw, s=1.0):
    """capsula gigante (brinquedo) deitada e meio enterrada"""
    x, y, z = loc
    d = V(math.cos(yaw), math.sin(yaw), 0.12).normalized()
    c = V(x, y, z)
    mb.rod(c - d * 1.9 * s, c, 1.35 * s, "P_DB_White", 14)
    mb.rod(c, c + d * 1.9 * s, 1.35 * s, "P_DB_Orange", 14)
    mb.rod(c - d * 0.25 * s, c + d * 0.25 * s, 1.42 * s, "P_DB_Blue", 14)
    mb.ico(1.35 * s, c - d * 1.9 * s, "P_DB_White", 2)
    mb.ico(1.35 * s, c + d * 1.9 * s, "P_DB_Orange", 2)
    mb.cyl(0.45 * s, 0.4 * s, c - d * 1.0 * s + V(0, 0, 1.35 * s), (0, 0, 0), "P_DB_Blue", 10, bevel=0.0)


def bollard(mb, x, y, z):
    mb.cyl(0.6, 1.6, (x, y, z + 0.8), (0, 0, 0), "P_OPM_Concrete", 10, bevel=0.1)
    mb.cyl(0.64, 0.35, (x, y, z + 1.1), (0, 0, 0), "P_OPM_Yellow", 10, bevel=0.0)
    mb.cyl(0.64, 0.25, (x, y, z + 0.65), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    col_box(A, (1.2, 1.2, 1.8), (x, y, z + 0.9))


# ------------------------------------------------------------------ dressing das escadas (vai no MB do portal)
def _nobori(mb, x, y, s, h=9.0):
    blk = "Wood_Dark"
    mb.box((0.4, 0.4, h), (x, y, T + h / 2), (0, 0, 0), blk, 0.0)
    mb.box((2.2, 0.3, 0.3), (x + s * 1.0, y, T + h - 0.5), (0, 0, 0), blk, 0.0)
    mb.box((1.7, 0.18, 6.0), (x + s * 1.05, y, T + h - 3.6), (0, 0, 0), "P_Naruto_Orange", 0.0)
    mb.box((0.28, 0.2, 6.0), (x + s * 1.95, y, T + h - 3.6), (0, 0, 0), "P_Naruto_Tile", 0.0)
    mb.cyl(0.5, 0.24, (x + s * 1.05, y - 0.12, T + h - 2.5), (D(90), 0, 0), "P_Naruto_Tile", 8, bevel=0.0)
    col_box(A, (0.6, 0.6, h), (x, y, T + h / 2))


def stairs_naruto(mb, px, rng):
    for s in (-1, 1):
        x = px + s * 8.7
        # toro baixinho (so a camara e o chapeu sobre um soco) no alto da escada
        mb.box((1.3, 1.3, 1.6), (x, 97.8, T + 0.8), (0, 0, 0), "Stone_Dark", 0.08)
        mb.cyl(0.55, 0.9, (x, 97.8, T + 2.05), (0, 0, D(30)), "P_Naruto_Glow", 6, bevel=0.0)
        mb.cyl(1.25, 0.6, (x, 97.8, T + 2.8), (0, 0, 0), "Stone_Dark", 6, r2=0.35, bevel=0.0)
        col_box(A, (1.6, 1.6, 3.2), (x, 97.8, T + 1.6))
        for y in (88.6, 92.8):
            _nobori(mb, px + s * 8.5, y, s)
    for (dx, y, h) in ((-10.6, 91.0, 7.5), (10.2, 95.2, 5.8)):
        K.sakura_small(mb, (px + dx, y, T), h, rng, reach=0.18)
        col_box(A, (1.2, 1.2, 4.0), (px + dx, y, T + 2.0))


def stairs_db(mb, px, rng):
    """as 7 esferas sobem ao lado da escada em pedestais cada vez mais altos (1 estrela -> 7 estrelas)"""
    for k in range(7):
        s = -1 if k % 2 == 0 else 1
        y = 86.6 + k * 2.1
        x = px + s * 8.9
        h = 1.2 + k * 0.5
        mb.cyl(0.9, h, (x, y, T + h / 2), (0, 0, 0), "P_DB_White", 8, bevel=0.0)
        mb.cyl(1.0, 0.3, (x, y, T + h - 0.1), (0, 0, 0), "P_DB_Orange", 8, bevel=0.0)
        mb.cyl(1.0, 0.25, (x, y, T + 0.35), (0, 0, 0), "P_DB_Blue", 8, bevel=0.0)
        b = V(x, y, T + h + 0.85)
        mb.ico(0.8, b, "P_DB_Ball", 2)
        for j in range(k + 1):
            if k == 0:
                p = b + V(0, -0.76, 0)
            else:
                a = D(90 + 360 * j / (k + 1))
                p = b + V(math.cos(a) * 0.36, -0.7, math.sin(a) * 0.36)
            K.octa(mb, p, 0.15, 0.15, "P_DB_Star")
        col_box(A, (1.8, 1.8, h + 1.6), (x, y, T + (h + 1.6) / 2))


def stairs_shadow(mb, px, rng):
    ir, gl = "Metal_Dark", "P_Shadow_Glow"
    for s in (-1, 1):
        x = px + s * 8.3
        ys = [SY0 + k * 1.1 for k in range(13)]
        for y in ys:
            mb.box((0.2, 0.2, 2.8), (x, y, T + 1.4), (0, 0, 0), ir, 0.0)
            K.cone(mb, V(x, y, T + 2.8), V(x, y, T + 3.5), 0.2, 0.0, ir, 4)
        for z in (T + 0.6, T + 2.3):
            mb.box((0.18, ys[-1] - ys[0] + 0.2, 0.26), (x, (ys[0] + ys[-1]) / 2, z), (0, 0, 0), ir, 0.0)
        for k in range(0, 12, 3):     # arcos ogivais entre montantes (le como grade gotica, nao cerca)
            y0, y1 = ys[k], ys[k + 3]
            arc = [V(x, y0 + (y1 - y0) * t, T + 1.5 + 0.7 * math.sin(math.pi * t) ** 0.6) for t in (0, 0.25, 0.5, 0.75, 1)]
            mb.tube(arc, 0.07, ir, 4)
        col_box(A, (0.6, ys[-1] - ys[0], 3.6), (x, (ys[0] + ys[-1]) / 2, T + 1.8))
        # velas roxas em castical de ferro
        for y in (88.6, 95.8):
            cx = px + s * 10.0
            mb.cyl(0.55, 0.3, (cx, y, T + 0.15), (0, 0, 0), ir, 6, bevel=0.0)
            mb.cyl(0.14, 2.6, (cx, y, T + 1.45), (0, 0, 0), ir, 5, bevel=0.0)
            mb.cyl(0.6, 0.22, (cx, y, T + 2.75), (0, 0, 0), ir, 6, bevel=0.0)
            for ox, hh in ((-0.28, 0.9), (0.28, 0.6), (0.0, 1.2)):
                mb.cyl(0.14, hh, (cx + ox, y, T + 2.86 + hh / 2), (0, 0, 0), "P_Shadow_Cloth", 6, bevel=0.0)
                K.octa(mb, (cx + ox, y, T + 2.86 + hh + 0.2), 0.12, 0.22, gl)
            col_box(A, (1.2, 1.2, 4.0), (cx, y, T + 2.0))


def stairs_demonslayer(mb, px, rng):
    ch, gl, wis = "P_DS_Char", "P_DS_Glow", "P_DS_Wisteria"
    zb = T + 8.0
    ys = (86.6, 98.8)
    # pergola leve: esteios finos, 2 longarinas e ripas finas; os cachos pendem entre as ripas
    for s in (-1, 1):
        xi, xo = px + s * 8.6, px + s * 12.2
        for x in (xi, xo):
            for y in ys:
                mb.box((0.42, 0.42, zb - T), (x, y, (T + zb) / 2), (0, 0, 0), ch, 0.0)
                col_box(A, (0.8, 0.8, zb - T), (x, y, (T + zb) / 2))
            mb.box((0.36, ys[1] - ys[0] + 1.0, 0.42), (x, (ys[0] + ys[1]) / 2, zb + 0.2), (0, 0, 0), ch, 0.0)
        for k in range(7):
            y = ys[0] + (ys[1] - ys[0]) * k / 6
            mb.box((abs(xo - xi) + 1.0, 0.24, 0.26), ((xi + xo) / 2, y, zb + 0.54), (0, 0, 0), ch, 0.0)
        for k in range(4):     # folhagem sobre as ripas (a pergola le como planta, nao como grade)
            y = ys[0] + 1.4 + (ys[1] - ys[0] - 2.8) * k / 3
            mb.ico(1.0, ((xi + xo) / 2 + rng.uniform(-0.3, 0.3), y, zb + 0.95), "Leaf_Pine_Light", 1, (1.8, 1.6, 0.55),
                   rot=(0, 0, rng.uniform(0, 3)))
        for k in range(8):
            x = xi + (xo - xi) * rng.uniform(0.12, 0.88)
            y = ys[0] + 0.4 + (ys[1] - ys[0] - 0.8) * (k + rng.uniform(0.15, 0.85)) / 8
            K.raceme(mb, V(x, y, zb + 0.45), rng.uniform(1.8, 2.8), wis, rng.uniform(0.36, 0.42), rng)
        K.chochin(mb, ((xi + xo) / 2, 92.7, zb + 0.6), r=0.7, h=1.3, paper=gl, cap=ch, hang=0.8, n=8, rod_m=ch)


def stairs_onepiece(mb, px, rng):
    for s in (-1, 1):
        x = px + s * 8.4
        ys = [SY0 + k * 4.45 for k in range(4)]
        tops = []
        for y in ys:
            mb.cyl(0.32, 3.0, (x, y, T + 1.5), (0, 0, rng.uniform(0, 1)), "Wood_Dark", 6, bevel=0.0)
            mb.cyl(0.36, 0.25, (x, y, T + 2.6), (0, 0, 0), "Rope", 6, bevel=0.0)
            tops.append(V(x, y, T + 2.6))
        for a_, b_ in zip(tops, tops[1:]):
            mb.tube([a_ + (b_ - a_) * t - V(0, 0, 0.6 * 4 * t * (1 - t)) for t in (0, 0.25, 0.5, 0.75, 1.0)], 0.12,
                    "Rope", 5)
        col_box(A, (0.7, ys[-1] - ys[0], 3.2), (x, (ys[0] + ys[-1]) / 2, T + 1.6))
    # tabuas de cais sobre o terraco (lado esquerdo) com barris
    K.deck(mb, px - 12.6, px - 9.4, 87.4, 97.4, T + 0.3, rng, "Wood_Plank", pw=1.0)
    for (x, y, z) in ((px - 11.0, 89.6, T + 0.3), (px - 11.2, 92.4, T + 0.3), (px + 10.6, 96.6, T)):
        K.barrel_small(mb, (x, y, z), 1.0, 2.3)
        col_box(A, (2.2, 2.2, 2.6), (x, y, z + 1.3))


def stairs_opm(mb, px, rng):
    con, gl, yel, dk = "P_OPM_Concrete", "P_OPM_Glow", "P_OPM_Yellow", "Metal_Dark"
    for s in (-1, 1):
        x = px + s * 8.3
        mb.box((0.7, SY1 - SY0, 1.3), (x, (SY0 + SY1) / 2, T + 0.65), (0, 0, 0), con, 0.08)
        mb.box((0.2, SY1 - SY0, 0.18), (x - s * 0.36, (SY0 + SY1) / 2, T + 1.15), (0, 0, 0), gl, 0.0)
        for y in (SY0 + 0.4, (SY0 + SY1) / 2, SY1 - 0.4):
            mb.box((0.95, 0.95, 1.6), (x, y, T + 0.8), (0, 0, 0), con, 0.06)
        col_box(A, (0.8, SY1 - SY0, 2.0), (x, (SY0 + SY1) / 2, T + 1.0))
    # outdoor vertical sobre coluna e frade zebrado (antes no vao OP|OPM; agora dentro do lote)
    bx, by = px - 12.1, 94.6
    mb.box((1.0, 1.0, 9.0), (bx, by, T + 4.5), (0, 0, 0), con, 0.1)
    mb.box((3.2, 0.8, 6.4), (bx, by - 0.2, T + 11.4), (0, 0, 0), dk, 0.08)
    mb.box((2.6, 0.2, 5.6), (bx, by - 0.65, T + 11.4), (0, 0, 0), "P_OPM_DarkGlass", 0.0)
    for z in (T + 14.3, T + 8.5):
        mb.box((2.8, 0.25, 0.2), (bx, by - 0.7, z), (0, 0, 0), gl, 0.0)
    mb.cyl(1.1, 0.25, (bx, by - 0.8, T + 12.2), (D(90), 0, 0), yel, 14, bevel=0.0)
    mb.box((0.9, 0.2, 0.8), (bx, by - 0.95, T + 12.3), (0, 0, 0), "P_OPM_Red", 0.0)
    col_box(A, (1.4, 1.4, 9.0), (bx, by, T + 4.5))
    bollard(mb, px - 12.4, 97.6, T)


# ------------------------------------------------------------------ placa de dificuldade + caixote de cristais
def difficulty(key, px, i, rng):
    mb = K.LeanMB("PORTAL_%s_Difficulty" % key, "06_PORTALS", rng, vcap=1)
    g = GLOW[key]
    F = L.FLOOR
    x, y = px + 7.8, L.FLIGHT1_Y0 - 1.5
    mb.box((1.0, 1.0, 6.0), (x, y, F + 3.0), (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((3.6, 0.6, 2.2), (x, y - 0.3, F + 5.4), (0, 0, 0), "Wood_Plank", 0.08)
    # moldura luminosa na cor do portal (e o que o vfx pulsa) + pontos de dificuldade
    for dz in (-1.12, 1.12):
        mb.box((3.8, 0.18, 0.16), (x, y - 0.66, F + 5.4 + dz), (0, 0, 0), g, 0.0)
    for dx in (-1.83, 1.83):
        mb.box((0.16, 0.18, 2.4), (x + dx, y - 0.66, F + 5.4), (0, 0, 0), g, 0.0)
    for k in range(i + 1):
        mb.ico(0.28, (x - 1.25 + k * 0.5, y - 0.7, F + 5.4), g, 1)
    col_box(A, (1.2, 1.2, 6.0), (x, y, F + 3.0))
    # caixote aberto de cristais do mundo do portal (storytelling: minerio que chega pela escada)
    cx, cy = px - 7.2, L.FLIGHT1_Y0 - 3.0
    ca = 0.25
    dx, dy = math.cos(ca), math.sin(ca)
    mb.box((2.2, 2.2, 1.9), (cx, cy, F + 0.95), (0, 0, ca), "Wood_Plank", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.3, 0.3, 2.0), (cx + dx * sx * 1.1 - dy * sy * 1.1, cy + dy * sx * 1.1 + dx * sy * 1.1, F + 1.0),
                   (0, 0, ca), "Wood_Dark", 0.0)
    mb.box((2.34, 2.34, 0.26), (cx, cy, F + 1.72), (0, 0, ca), "Wood_Dark", 0.0)
    crystal_cluster(mb, (cx, cy, F + 1.7), 0.6, g, rng, 4)
    col_box(A, (2.5, 2.5, 2.6), (cx, cy, F + 1.3), (0, 0, 0.25))
    mb.finish()


# ------------------------------------------------------------------ centro do terraco
def build(rng):
    mb = K.LeanMB("PORTAL_Terrace_Dressing", "06_PORTALS", rng, vcap=1)
    # ---- centro-oeste (x -26 .. -17): ruina gotica (coluna quebrada), arvore morta, rochas escuras, cristais
    cx, cy = -22.4, 103.6
    mb.box((2.6, 2.6, 0.8), (cx, cy, T + 0.4), (0, 0, 0.2), "P_Shadow_Trim", 0.1)
    mb.cyl(0.95, 4.6, (cx, cy, T + 3.0), (0, 0, 0.2), "P_Shadow_Stone", 8, r2=0.85, bevel=0.0)
    K.plate(mb, [(-0.9, 0), (0.9, 0), (0.9, 0.6), (0.3, 1.4), (-0.2, 0.7), (-0.9, 1.1)], V(cx, cy, T + 5.2),
            (1, 0, 0), (0, 0, 1), 1.7, "P_Shadow_Stone")
    mb.box((1.8, 1.0, 1.0), (cx + 2.0, cy - 0.8, T + 0.5), (0.3, 0.2, 0.9), "P_Shadow_Stone", 0.08)
    col_box(A, (2.6, 2.6, 6.0), (cx, cy, T + 3.0))
    crystal_cluster(mb, (cx - 1.8, cy + 1.6, T + 0.2), 0.9, "P_Shadow_Glow", rng, 4)
    dead_tree(mb, (-20.2, 112.0, T), 11.0, rng)
    col_box(A, (1.8, 1.8, 5.0), (-20.2, 112.0, T + 2.5))
    for (x, y, s) in ((-18.4, 106.8, 1.8), (-24.6, 110.2, 1.4)):
        mb.rock((x, y, T + s * 0.25), (s * 1.3, s * 1.1, s * 0.8), "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 6)))
    # mureta gotica arruinada (topo em degraus quebrados)
    a, b = V(-25.6, 106.2, T), V(-22.2, 109.2, T)
    d = (b - a)
    ang = math.atan2(d.y, d.x)
    for i, h in enumerate((2.6, 2.0, 1.2, 1.7, 0.8)):
        c = a + d * ((i + 0.5) / 5)
        mb.box((d.length / 5 - 0.08, 1.2, h), (c.x, c.y, T + h / 2), (0, 0, ang), "P_Shadow_Stone", 0.1)
    mb.box((d.length + 0.4, 1.5, 0.5), ((a + b) / 2 + V(0, 0, 0.25)), (0, 0, ang), "P_Shadow_Trim", 0.08)
    col_box(A, (d.length, 1.4, 2.6), ((a + b) / 2 + V(0, 0, 1.3)), (0, 0, ang))
    for (x, y, s) in ((-21.6, 94.4, 2.2), (-18.6, 96.4, 1.5)):
        mb.rock((x, y, T + s * 0.25), (s * 1.3, s * 1.1, s * 0.9), "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 6)))
    crystal_cluster(mb, (-20.2, 95.2, T + 0.7), 1.2, "P_Shadow_Glow", rng, 6)
    col_box(A, (4.4, 3.6, 3.4), (-20.2, 95.2, T + 1.7))

    # ---- centro-leste (x 16 .. 26): glicinia grande + toro escuro + pedras + mureta
    XMAX = L.PORTAL_X[3] - 14.0 - 4.0 - 0.1      # lote do DS (px-14) menos a folga de 4
    wisteria_tree(mb, (19.8, 111.6, T), 12.0, rng, xmax=XMAX)
    col_box(A, (1.8, 1.8, 7.0), (19.8, 111.6, T + 3.5))
    K.toro(mb, (22.8, 104.2, T), 0.78, "Stone_Dark", "P_DS_Char", glow="P_DS_Glow", lit=False)
    col_box(A, (2.0, 2.0, 5.0), (22.8, 104.2, T + 2.5))
    for (x, y, s) in ((18.2, 107.0, 1.6), (24.4, 110.0, 1.2)):
        K.mossy_rock(mb, (x, y, T), (s * 1.3, s * 1.1, s * 0.9), rng, "Cliff_Rock_Dark", moss=None)
    a, b = (16.4, 101.6), (20.4, 104.4)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    c = V((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, T)
    mb.box((ln, 1.1, 1.5), c + V(0, 0, 0.75), (0, 0, ang), "Stone_Dark", 0.12)
    mb.box((ln + 0.3, 1.4, 0.35), c + V(0, 0, 1.65), (0, 0, ang), "P_DS_Char", 0.05)
    mb.box((ln + 0.02, 1.14, 0.2), c + V(0, 0, 1.2), (0, 0, ang), "P_DS_Blood", 0.0)
    col_box(A, (ln, 1.2, 2.0), c + V(0, 0, 1.0), (0, 0, ang))
    wisteria_tree(mb, (20.8, 94.2, T), 8.5, rng, xmax=XMAX)
    col_box(A, (1.6, 1.6, 5.0), (20.8, 94.2, T + 2.5))
    mb.finish()
