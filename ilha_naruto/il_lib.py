# il_lib - base da Ilha 1 (Naruto) sobre o pipeline do lobby (lobby_area/forja_mineradora/fm_lib.py).
# Reaproveita: MB (construtor de malha com variantes/UV/chanfro), materiais + traducao Roblox (MATS/RBX_CAL/rbx_rule),
# colisao COL_ (col_box/col_ramp), marcadores, luzes, cameras, fm_parts (escada/cerca/mureta/lanterna/calcamento),
# kits de arquitetura/vegetacao/agua/props e o export_roblox. Aqui ficam so o que e da ilha: colecoes, paleta Konoha,
# geometria das zonas (poligonos de terraco) e colisao por poligono/anel.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
LOBBY = os.path.normpath(os.path.join(HERE, "..", "lobby_area", "forja_mineradora"))
for p in (HERE, LOBBY):
    if p not in sys.path:
        sys.path.insert(0, p)

import bpy
from mathutils import Vector
import fm_lib
from fm_lib import MB, D, S, col_box, col_box2, col_ramp, light, camera, add_variants, MATS, RBX_CAL
import il_layout as L

COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_MINING", "04_VILLAGE", "05_SUMMON", "06_WATER",
        "07_NEXT_ISLAND", "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "11_LIGHTING", "12_VFX_HELPERS",
        "13_COLLISION", "14_GAMEPLAY_MARKERS", "15_EXPORT", "_SCALE_REFERENCE"]
fm_lib.COLS = COLS
# detail="far" (sem fundo apoiado): pisos da ilha
fm_lib._FLOOR_LEVELS = tuple(sorted({L.PIT, L.G, L.RING, L.T1, L.T2}))

# ------------------------------------------------------------------ paleta Konoha (lida nas referencias)
# nomes com os PREFIXOS do lobby -> herdam textura de detalhe (TEX_RULES) e Enum.Material (RBX_RULES)
KMATS = {
    "Grass_Konoha":      (S(112, 170, 62), 0.9, 0.0, 0, None, 0.20),
    "Dirt_Pit":          (S(166, 112, 70), 0.95, 0.0, 0, None, 0.16),
    "Stone_Paving_Warm": (S(206, 188, 158), 0.85, 0.0, 0, None, 0.18),
    "Stone_Wall_Light":  (S(178, 170, 156), 0.85, 0.0, 0, None, 0.16),
    "Stone_Wall_Dark":   (S(128, 120, 110), 0.85, 0.0, 0, None, 0.16),
    "Cliff_Rock_Tan":    (S(164, 134, 104), 0.9, 0.0, 0, None, 0.14),
    "Cliff_Rock_Tan_Dark": (S(112, 90, 72), 0.9, 0.0, 0, None, 0.12),
    "Cliff_Rock_Tan_Top": (S(184, 158, 124), 0.9, 0.0, 0, None, 0.10),
    "Roof_Terracotta":   (S(176, 72, 50), 0.7, 0.0, 0, None, 0.12),
    "Roof_Blue":         (S(62, 84, 138), 0.7, 0.0, 0, None, 0.12),
    "Roof_Green":        (S(72, 118, 80), 0.7, 0.0, 0, None, 0.12),
    "Plaster_Cream":     (S(232, 212, 172), 0.9, 0.0, 0, None, 0.08),
    "Wood_Lacquer_Red":  (S(168, 42, 32), 0.55, 0.0, 0, None, 0.08),
    "Metal_Gold":        (S(222, 170, 70), 0.3, 0.9, 0, None, 0.05),
    "Summon_Stone":      (S(92, 94, 122), 0.8, 0.0, 0, None, 0.12),
    "Summon_Stone_Dark": (S(64, 64, 88), 0.8, 0.0, 0, None, 0.10),
    "Summon_Floor":      (S(150, 112, 188), 0.7, 0.0, 0, None, 0.06),
    "Cloth_Royal_Blue":  (S(44, 62, 170), 0.9, 0.0, 0, None, 0.06),
    "Summon_Star_Glow":  (S(255, 186, 60), 0.3, 0.0, 3.0, S(255, 176, 50), 0.0),
    "Summon_Blue_Glow":  (S(80, 150, 255), 0.3, 0.0, 3.0, S(80, 150, 255), 0.0),
    "DB_Energy_Glow":    (S(255, 132, 30), 0.3, 0.0, 3.0, S(255, 132, 30), 0.0),
    "Sea_Water":         (S(38, 128, 196), 0.1, 0.0, 0.15, S(38, 128, 196), 0.0),
    "BLK_Mass":          (S(190, 186, 180), 0.9, 0.0, 0, None, 0.0),
}
for k, v in KMATS.items():
    MATS.setdefault(k, v)
# cor que o Roblox recebe (sem calibracao medida ainda: a propria cor)
for k in ("Summon_Star_Glow", "Summon_Blue_Glow", "DB_Energy_Glow"):
    RBX_CAL.setdefault(k, (None, [int(c) for c in fm_lib.to_srgb(KMATS[k][0])]))
add_variants("Stone_Paving_Warm", [("Stone_Paving_Warm", 5), ("Stone_Paving_Warm_B", 3, (218, 202, 172)),
                                   ("Stone_Paving_Warm_C", 2, (188, 170, 142))], cap=2)
add_variants("Stone_Wall_Light", [("Stone_Wall_Light", 5), ("Stone_Wall_Light_B", 3, (192, 184, 170)),
                                  ("Stone_Wall_Light_C", 2, (158, 150, 138))], cap=2)
add_variants("Cliff_Rock_Tan", [("Cliff_Rock_Tan", 5), ("Cliff_Rock_Tan_B", 3, (178, 148, 116)),
                                ("Cliff_Rock_Tan_C", 2, (142, 116, 92))], cap=2)
add_variants("Roof_Terracotta", [("Roof_Terracotta", 5), ("Roof_Terracotta_B", 3, (190, 84, 58))], cap=2)
add_variants("Roof_Blue", [("Roof_Blue", 5), ("Roof_Blue_B", 3, (74, 98, 152))], cap=2)
add_variants("Grass_Konoha", [("Grass_Konoha", 6), ("Grass_Konoha_B", 4, (98, 156, 56))], cap=2)
add_variants("Dirt_Pit", [("Dirt_Pit", 6), ("Dirt_Pit_B", 4, (150, 100, 62))], cap=2)


# ------------------------------------------------------------------ cena
def reset_scene():
    fm_lib.COLS = COLS
    fm_lib.reset_scene()
    fm_lib._COL_COUNT.clear()


def mk(name, loc, rot=(0, 0, 0), size=2.0, kind="PLAIN_AXES", props=None, c="14_GAMEPLAY_MARKERS"):
    return fm_lib.marker(name, loc, rot, size, kind, c, props)


def yaw_to(dx, dy):
    """rotacao Z (rad) para que o eixo +Y local aponte na direcao (dx, dy)"""
    return math.atan2(dy, dx) - math.pi / 2


# ------------------------------------------------------------------ geometria 2D
def ccw(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return list(poly) if a > 0 else list(reversed(poly))


def area(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return a / 2


def clip(poly, nx, ny, c):
    """Sutherland-Hodgman: mantem a parte com nx*x + ny*y <= c"""
    out = []
    n = len(poly)
    for i in range(n):
        p = poly[i]
        q = poly[(i + 1) % n]
        dp = nx * p[0] + ny * p[1] - c
        dq = nx * q[0] + ny * q[1] - c
        if dp <= 0:
            out.append(p)
        if (dp < 0 < dq) or (dq < 0 < dp):
            t = dp / (dp - dq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def arc_pts(r, a0, a1, step_deg=4.0, cx=0.0, cy=0.0):
    n = max(2, int(abs(a1 - a0) / step_deg) + 1)
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n)]


def wedge_clip(poly, a0, a1):
    """mantem o setor angular a0..a1 (graus, a1-a0 < 180) com apice na origem"""
    # lado esquerdo do raio a0 e lado direito do raio a1
    t0, t1 = math.radians(a0), math.radians(a1)
    p = clip(poly, math.sin(t0), -math.cos(t0), 0.0)          # manter  cross(dir0, p) >= 0
    p = clip(p, -math.sin(t1), math.cos(t1), 0.0)             # manter  cross(dir1, p) <= 0
    return p


def replace_apex_with_arc(poly, r, a_from, a_to, step_deg=3.0):
    """troca o vertice da origem (apice do setor) por um arco de raio r (de a_from a a_to, graus)"""
    out = []
    for p in poly:
        if abs(p[0]) < 1e-6 and abs(p[1]) < 1e-6:
            out.extend(arc_pts(r, a_from, a_to, step_deg))
        else:
            out.append(p)
    return out


def rim():
    return ccw(L.ISLAND_RIM)


def t1_poly():
    """terraco T1: setor 26..200 graus, fora do raio T1_WALL_R, oeste de x=108 (vale do riacho), dentro do contorno"""
    a0, a1 = L.T1_WALL_A
    p = wedge_clip(rim(), a0, a1)
    p = clip(p, 1.0, 0.0, 108.0)
    return ccw(replace_apex_with_arc(p, L.T1_WALL_R, a1, a0))


def t2_poly():
    p = clip(rim(), 0.0, -1.0, -L.T2_WALL_Y)       # y >= T2_WALL_Y
    p = clip(p, 1.0, 0.0, 118.0)
    p = clip(p, 1.0, -1.0, L.T2_EXIT_CUT)          # fora da faixa da ponte de saida
    return ccw(p)


def cliff_poly():
    return ccw(clip(rim(), 0.0, -1.0, -L.BACK_CLIFF_Y))


def base_halves(hole_r):
    """contorno da ilha menos o disco central (raio hole_r), em 2 poligonos simples (norte e sul)"""
    out = []
    for s in (1, -1):
        p = clip(rim(), 0.0, -s, 0.0)                 # s=1: y >= 0 ; s=-1: y <= 0
        # troca o trecho sobre o eixo x (entre -hole_r e +hole_r) pelo semicirculo
        q = []
        for i, pt in enumerate(p):
            q.append(pt)
        # remove pontos do eixo dentro do furo e insere o arco
        q = [pt for pt in q if not (abs(pt[1]) < 1e-6 and abs(pt[0]) < hole_r)]
        # achar a posicao: entre os dois pontos do eixo y=0 (x<0 e x>0)
        idx = [i for i, pt in enumerate(q) if abs(pt[1]) < 1e-6]
        if len(idx) >= 2:
            # o contorno cruza y=0 em x = xa (oeste) e xb (leste); o miolo e ligado pelo semicirculo
            arcp = arc_pts(hole_r, 180.0, 0.0, 3.0) if s == 1 else arc_pts(hole_r, 0.0, -180.0, 3.0)
            ia, ib = idx[0], idx[-1]
            qa, qb = q[ia], q[ib]
            # ordem: o poligono CCW do lado norte vai de leste para oeste pelo contorno e volta por baixo
            seq = q[:]
            # monta: ... qW -> arco -> qE ... (sempre ligando o ponto do eixo mais a oeste ao mais a leste)
            iw = ia if qa[0] < qb[0] else ib
            ie = ib if iw == ia else ia
            if s == 1:
                # CCW norte: percorre contorno de leste (y=0) ate oeste (y=0) pelo norte; volta de oeste p/ leste
                path = []
                i = ie
                while True:
                    path.append(seq[i])
                    if i == iw:
                        break
                    i = (i + 1) % len(seq)
                path += [(xw, 0.0) for xw in (-hole_r,)]
                path += arcp[1:-1]
                path += [(hole_r, 0.0)]
            else:
                path = []
                i = iw
                while True:
                    path.append(seq[i])
                    if i == ie:
                        break
                    i = (i + 1) % len(seq)
                path += [(hole_r, 0.0)] + arcp[1:-1] + [(-hole_r, 0.0)]
            out.append(ccw(path))
        else:
            out.append(ccw(q))
    return out


def x_intervals(poly, y):
    xs = []
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        if (y0 > y) != (y1 > y):
            xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def _inter(a, b):
    out = []
    for x0, x1 in a:
        for u0, u1 in b:
            lo, hi = max(x0, u0), min(x1, u1)
            if hi - lo > 0.2:
                out.append((lo, hi))
    return out


def _union(a, b):
    ivs = sorted(a + b)
    out = []
    for iv in ivs:
        if out and iv[0] <= out[-1][1] + 0.01:
            out[-1] = (out[-1][0], max(out[-1][1], iv[1]))
        else:
            out.append(iv)
    return out


def col_poly(area_name, poly, z0, z1, step=2.0, mode="union", minus_r=None):
    """colisao de um poligono (piso/volume) em faixas de 'step' studs ao longo de y.
    mode='union' cobre a borda por fora (ate ~0,5 stud alem), 'inter' fica por dentro.
    minus_r: tira um disco central (raio) das faixas."""
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        ya, yb = y, min(y + step, max(ys))
        samples = [ya + 0.05, (ya + yb) / 2, yb - 0.05]
        ivs = None
        for s in samples:
            iv = x_intervals(poly, s)
            if minus_r:
                cut = []
                if abs(s) < minus_r:
                    h = math.sqrt(minus_r * minus_r - s * s)
                    for x0, x1 in iv:
                        if x0 < -h:
                            cut.append((x0, min(x1, -h)))
                        if x1 > h:
                            cut.append((max(x0, h), x1))
                    iv = cut
            ivs = iv if ivs is None else (_union(ivs, iv) if mode == "union" else _inter(ivs, iv))
        for x0, x1 in ivs or []:
            if x1 - x0 > 0.3:
                col_box2(area_name, (x0, ya, z0), (x1, yb, z1))
                n += 1
        y = yb
    return n


def col_annulus(area_name, r0, r1, a0, a1, z0, z1, n=None):
    """anel/setor de colisao em caixas radiais (corda na borda externa)"""
    span = a1 - a0
    n = n or max(4, int(span / 5.0))
    da = math.radians(span / n)
    for i in range(n):
        a = math.radians(a0) + da * (i + 0.5)
        rm = (r0 + r1) / 2
        w = 2 * r1 * math.tan(da / 2) + 0.4
        col_box(area_name, (r1 - r0, w, z1 - z0), (rm * math.cos(a), rm * math.sin(a), (z0 + z1) / 2),
                (0, 0, a))
    return n


def prism(mb, poly, z0, z1, m, top_m=None, bevel=0.0):
    """prisma vertical; top_m != m -> tampo separado fino (material do piso) sobre o corpo"""
    poly = ccw(poly)
    if top_m and top_m != m:
        mb.prism(poly, z0, z1 - 0.3, m, bevel)
        mb.prism(poly, z1 - 0.3, z1, top_m, 0.0)
    else:
        mb.prism(poly, z0, z1, m, bevel)


def annulus(mb, r0, r1, a0, a1, z0, z1, m, step=3.0, top_m=None):
    """setor de anel como prisma (poligono: arco externo + arco interno)"""
    outer = arc_pts(r1, a0, a1, step)
    inner = arc_pts(r0, a1, a0, step)
    prism(mb, outer + inner, z0, z1, m, top_m)
