# fm_portal_terrace - quebra a "galeria reta" do terraco dos portais: nos vaos entre plataformas entram rochas,
# muretas e vegetacao tematica que faz a transicao de um mundo para o outro (sem tocar nos eixos de acesso).
#   Naruto|DB: bambuzal + pedras com musgo      DB|Shadow: capsula gigante / arvore morta com cristais
#   centro-oeste: ruina gotica e rochas escuras  centro-leste: glicinia e toro escuro
#   DS|OP: glicinia baixa + pedras               OP|OPM: frades zebrados de concreto + rochas
import math
from fm_lib import MB, D, col_box
from fm_parts import crystal_cluster, crate, sakura, palm
import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L

T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
A = "Portal"


def wisteria_tree(mb, loc, h, rng):
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
        r = h * rng.uniform(0.14, 0.3)
        c = V(x + math.cos(a) * r, y + math.sin(a) * r, z + h * rng.uniform(0.78, 0.9))
        mb.ico(h * rng.uniform(0.18, 0.23), c, "Leaf_Pine_Light", 1, (1.15, 1.15, 0.45), jitter=0.25)
    for i in range(14):
        a = i * math.tau / 14 + rng.uniform(-0.15, 0.15)
        r = h * rng.uniform(0.3, 0.44)
        top = V(x + math.cos(a) * r, y + math.sin(a) * r, z + h * rng.uniform(0.74, 0.8))
        K.raceme(mb, top, rng.uniform(2.0, 3.6), "P_DS_Wisteria", 0.55, rng)


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


def build(rng):
    mb = MB("PORTAL_Terrace_Dressing", "06_PORTALS", rng)

    # ---- Naruto | DB  (x -96 .. -84): bambuzal e pedras com musgo
    K.bamboo(mb, (-92.6, 103.2, T), rng, n=6, h=(9.0, 13.0))
    col_box(A, (3.0, 3.0, 8.0), (-92.6, 103.2, T + 4.0))
    K.mossy_rock(mb, (-87.6, 101.4, T), (2.3, 1.9, 1.5), rng)
    K.mossy_rock(mb, (-94.6, 100.9, T), (1.5, 1.3, 1.0), rng)
    col_box(A, (2.2, 1.8, 1.6), (-87.6, 101.4, T + 0.8))

    # ---- DB | Shadow (x -66 .. -54): capsula gigante do lado DB, pedras escuras com cristal do lado sombrio
    capsule(mb, (-62.2, 104.6, T + 0.7), D(55), 1.0)
    col_box(A, (4.4, 3.0, 2.4), (-62.2, 104.6, T + 1.2), (0, 0, D(55)))
    mb.rock((-63.4, 109.6, T + 0.4), (2.0, 1.7, 1.3), "Cliff_Rock", 1, (0, 0, 0.7))
    mb.rock((-58.4, 111.4, T + 0.4), (2.2, 1.8, 1.4), "Cliff_Rock_Dark", 1, (0, 0, 2.1))
    crystal_cluster(mb, (-57.6, 112.6, T + 0.6), 0.8, "Crystal_Purple", rng, 3)

    # ---- centro-oeste (x -32 .. -18): ruina gotica (coluna quebrada), rochas escuras, arvore morta, cristais
    cx, cy = -27.2, 103.6
    mb.box((2.6, 2.6, 0.8), (cx, cy, T + 0.4), (0, 0, 0.2), "Stone_Dark", 0.1)
    mb.cyl(0.95, 4.6, (cx, cy, T + 3.0), (0, 0, 0.2), "P_Shadow_Stone", 8, r2=0.85, bevel=0.0)
    K.plate(mb, [(-0.9, 0), (0.9, 0), (0.9, 0.6), (0.3, 1.4), (-0.2, 0.7), (-0.9, 1.1)], V(cx, cy, T + 5.2),
            (1, 0, 0), (0, 0, 1), 1.7, "P_Shadow_Stone")
    mb.box((1.8, 1.0, 1.0), (cx + 2.0, cy - 0.8, T + 0.5), (0.3, 0.2, 0.9), "P_Shadow_Stone", 0.08)
    col_box(A, (2.6, 2.6, 6.0), (cx, cy, T + 3.0))
    crystal_cluster(mb, (cx - 1.8, cy + 1.6, T + 0.2), 0.9, "Crystal_Purple", rng, 4)
    dead_tree(mb, (-24.4, 111.8, T), 11.0, rng)
    col_box(A, (1.8, 1.8, 5.0), (-24.4, 111.8, T + 2.5))
    for (x, y, s) in ((-21.8, 106.8, 1.8), (-30.2, 110.6, 1.4)):
        mb.rock((x, y, T + s * 0.25), (s * 1.3, s * 1.1, s * 0.8), "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 6)))
    # mureta gotica arruinada (topo em degraus quebrados)
    a, b = V(-33.2, 106.4, T), V(-29.4, 109.4, T)
    d = (b - a)
    ang = math.atan2(d.y, d.x)
    for i, h in enumerate((2.6, 2.0, 1.2, 1.7, 0.8)):
        c = a + d * ((i + 0.5) / 5)
        mb.box((d.length / 5 - 0.08, 1.2, h), (c.x, c.y, T + h / 2), (0, 0, ang), "P_Shadow_Stone", 0.1)
    mb.box((d.length + 0.4, 1.5, 0.5), ((a + b) / 2 + V(0, 0, 0.25)), (0, 0, ang), "Stone_Dark", 0.08)
    col_box(A, (d.length, 1.4, 2.6), ((a + b) / 2 + V(0, 0, 1.3)), (0, 0, ang))

    # ---- centro-leste (x 18 .. 32): glicinia grande + toro escuro + pedras
    wisteria_tree(mb, (26.6, 111.6, T), 12.5, rng)
    col_box(A, (1.8, 1.8, 7.0), (26.6, 111.6, T + 3.5))
    K.toro(mb, (27.4, 104.0, T), 0.78, "Stone_Dark", "P_DS_Char", glow="P_Red_Glow", lit=False)
    col_box(A, (2.0, 2.0, 5.0), (27.4, 104.0, T + 2.5))
    for (x, y, s) in ((22.4, 107.6, 1.6), (30.2, 111.4, 1.2)):
        K.mossy_rock(mb, (x, y, T), (s * 1.3, s * 1.1, s * 0.9), rng, "Cliff_Rock_Dark", moss=None)
    # mureta baixa de pedra escura com capa de madeira carbonizada e friso vermelho-sangue
    a, b = (19.4, 101.6), (23.4, 104.4)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    ln = math.hypot(b[0] - a[0], b[1] - a[1])
    c = V((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, T)
    mb.box((ln, 1.1, 1.5), c + V(0, 0, 0.75), (0, 0, ang), "Stone_Dark", 0.12)
    mb.box((ln + 0.3, 1.4, 0.35), c + V(0, 0, 1.65), (0, 0, ang), "P_DS_Char", 0.05)
    mb.box((ln + 0.02, 1.14, 0.2), c + V(0, 0, 1.2), (0, 0, ang), "P_DS_Blood", 0.0)
    col_box(A, (ln, 1.2, 2.0), c + V(0, 0, 1.0), (0, 0, ang))

    # ---- DS | OP (x 56 .. 64): pedras de praia e um resto de casco/caixotes (a ancora do OP fica livre)
    K.mossy_rock(mb, (58.4, 101.8, T), (2.6, 2.1, 1.6), rng, "Cliff_Rock", moss=None)
    K.mossy_rock(mb, (61.6, 103.6, T), (1.6, 1.4, 1.0), rng, "Cliff_Rock", moss=None)
    col_box(A, (2.4, 2.0, 1.6), (58.4, 101.8, T + 0.8))
    crate(mb, (60.2, 106.2, T), 1.8, 0.4, rng)
    col_box(A, (2.2, 2.2, 1.8), (60.2, 106.2, T + 0.9))

    # ---- OP | OPM (x 88 .. 96): frades zebrados, barreira de concreto, rochas
    for (x, y) in ((89.6, 107.4), (92.0, 108.2), (94.4, 107.6)):
        bollard(mb, x, y, T)
    K.plate(mb, [(-2.2, 0), (2.2, 0), (1.6, 0.5), (0.8, 1.6), (-0.8, 1.6), (-1.6, 0.5)], V(92.2, 111.2, T),
            (1, 0, 0), (0, 0, 1), 1.6, "P_OPM_Concrete")
    for k in range(4):
        mb.box((0.7, 1.7, 0.35), (90.8 + k * 0.95, 111.2, T + 0.9), (0, D(35), 0), "P_OPM_Yellow" if k % 2 == 0 else "Metal_Dark", 0.0)
    col_box(A, (4.4, 1.8, 1.8), (92.2, 111.2, T + 0.9))
    mb.rock((90.2, 100.8, T + 0.3), (1.6, 1.4, 1.0), "Cliff_Rock", 1, (0, 0, 0.4))

    # ---- borda frontal do terraco (entre os pocos das escadas): acentos em profundidades e alturas diferentes,
    # para a fileira de portais nao ler como galeria reta vista do vale
    sakura(mb, (-119.6, 95.4, T), 11.5, rng)
    col_box(A, (1.6, 1.6, 6.0), (-119.6, 95.4, T + 3.0))
    K.bamboo(mb, (-91.6, 94.2, T), rng, n=4, h=(7.0, 10.0))
    col_box(A, (2.6, 2.6, 6.0), (-91.6, 94.2, T + 3.0))
    K.mossy_rock(mb, (-88.6, 96.4, T), (2.0, 1.7, 1.3), rng)
    for (x, y, s) in ((-61.6, 93.4, 2.6), (-57.8, 95.8, 1.8)):
        mb.rock((x, y, T + s * 0.25), (s * 1.3, s * 1.1, s * 0.9), "Cliff_Rock_Dark", 1, (0, 0, rng.uniform(0, 6)))
    crystal_cluster(mb, (-60.0, 94.4, T + 0.8), 1.4, "Crystal_Purple", rng, 6)
    col_box(A, (4.4, 3.6, 3.4), (-60.0, 94.4, T + 1.7))
    wisteria_tree(mb, (29.0, 93.4, T), 9.0, rng)
    col_box(A, (1.6, 1.6, 5.0), (29.0, 93.4, T + 2.5))
    palm(mb, (60.4, 94.0, T), 12.5, rng, lean=0.32)
    col_box(A, (1.6, 1.6, 7.0), (60.4, 94.0, T + 3.5))
    K.mossy_rock(mb, (57.6, 96.6, T), (1.8, 1.5, 1.1), rng, "Cliff_Rock", moss=None)
    # painel neon (outdoor vertical) sobre coluna, do lado OPM
    bx, by = 92.4, 94.6
    mb.box((1.0, 1.0, 9.0), (bx, by, T + 4.5), (0, 0, 0), "P_OPM_Concrete", 0.1)
    mb.box((3.2, 0.8, 6.4), (bx, by - 0.2, T + 11.4), (0, 0, 0), "Metal_Dark", 0.08)
    mb.box((2.6, 0.2, 5.6), (bx, by - 0.65, T + 11.4), (0, 0, 0), "P_OPM_Glass", 0.0)
    mb.box((2.8, 0.25, 0.25), (bx, by - 0.7, T + 14.3), (0, 0, 0), "P_OPM_Neon", 0.0)
    mb.box((2.8, 0.25, 0.25), (bx, by - 0.7, T + 8.5), (0, 0, 0), "P_OPM_Neon", 0.0)
    mb.cyl(1.1, 0.25, (bx, by - 0.8, T + 12.2), (D(90), 0, 0), "P_OPM_Yellow", 14, bevel=0.0)
    mb.box((0.9, 0.2, 0.8), (bx, by - 0.95, T + 12.3), (0, 0, 0), "P_OPM_Red", 0.0)
    col_box(A, (1.4, 1.4, 9.0), (bx, by, T + 4.5))
    bollard(mb, 95.0, 96.2, T)

    # ---- pontas do terraco: oeste (junto ao muro de Konoha) e leste (depois das torres)
    for (x, y, s) in ((-127.2, 103.0, 2.6), (-124.8, 99.6, 1.6), (123.6, 102.4, 2.2), (126.6, 106.8, 2.8)):
        K.mossy_rock(mb, (x, y, T), (s * 1.3, s * 1.1, s * 0.9), rng)
    mb.finish()
