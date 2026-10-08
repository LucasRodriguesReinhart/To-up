# op_blockout - BLOCKOUT (M1) da Ilha 5 ONE PIECE / WANO, zona por zona: massa da ilha em terracos, entrada (ponte +
# GRANDE torii), rua de chegada, capital (volumes com telhado por CONJUNTO), praca de mineracao (piso, emblema rente,
# estandartes nas bordas), castelo elevado (adro, portao, subida, patio, varanda vermelha, torre de 4 andares com
# terreo ACESSIVEL), arvore monumental arqueada (tronco que afina + raizes + copa em massas), summon (torre AMS aprovada
# por alias), porto (cais, rua alta, pier, palafita) + navio (casco, convés acessivel, mastros, velas), agua (SO a pedra;
# a agua e do Roblox; previa em 00_REFERENCE), saida (ponte vermelha, promontorio, portao One Punch Man da galeria,
# guarda provisoria), marcos secundarios (caveira com chifres, espada distante, pagode) e vestir (cerejeiras, pinheiros,
# lanternas). Materiais simples da paleta OPMATS, sem textura.
# Cada zona cria: massas visuais (detail="far"), a colisao dos PROPRIOS volumes (casas, castelo, torii, mastros...) e
# as luzes basicas. Chao, escadas, pontes, guardas e TODOS os marcadores sao do op_core/op_col (sempre).
# O modulo de detalhe de uma zona SUBSTITUI a funcao dela aqui (build(skip={...})).
import math, random
import bmesh
from mathutils import Vector, Matrix
import op_lib as DL
from op_lib import MB, col_box, col_box2, yaw_to, Frame, light, ccw
import fm_lib
import op_layout as L
import op_col

ZONES = ["terrain", "entry", "capital", "plaza", "castle", "tree", "summon", "harbor", "ship", "water", "exit",
         "landmarks", "dressing"]
T0, T1, P, CF, CC = L.T0, L.T1, L.P, L.CF, L.CC
WARM = (1.0, 0.66, 0.36)
DETAILED = set()


# ------------------------------------------------------------------ primitivas
def faces_solid(mb, verts_co, faces_idx, m):
    bm = mb.bm
    vs = [bm.verts.new(c) for c in verts_co]
    for f in faces_idx:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    mb._post(vs, m, None, 0, 1)
    return vs


def uz_prism(mb, F, pts_uz, y0, y1, m):
    n = len(pts_uz)
    co = [F.p(u, y0, z) for u, z in pts_uz] + [F.p(u, y1, z) for u, z in pts_uz]
    fs = [list(range(n)), list(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        fs.append([i, j, n + j, n + i])
    faces_solid(mb, co, fs, m)


def frustum(mb, F, w0, d0, z0, w1, d1, z1, m, th=0.6):
    """saia de telhado (tronco de piramide): retangulo w0 x d0 em z0 ate w1 x d1 em z1, com espessura no beiral"""
    W0, D0, W1, D1 = w0 / 2, d0 / 2, w1 / 2, d1 / 2
    co = [F.p(-W0, -D0, z0), F.p(W0, -D0, z0), F.p(W0, D0, z0), F.p(-W0, D0, z0),
          F.p(-W1, -D1, z1), F.p(W1, -D1, z1), F.p(W1, D1, z1), F.p(-W1, D1, z1),
          F.p(-W0, -D0, z0 - th), F.p(W0, -D0, z0 - th), F.p(W0, D0, z0 - th), F.p(-W0, D0, z0 - th)]
    fs = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7],
          [8, 9, 1, 0], [9, 10, 2, 1], [10, 11, 3, 2], [11, 8, 0, 3], [11, 10, 9, 8]]
    faces_solid(mb, co, fs, m)


def irimoya(mb, F, w, d, z0, rise, over, m="Roof_OP_Blue", ridge_m="Roof_OP_Ridge", gable_m="Wood_OP_Dark", th=0.7,
            ridge_ends="Roof_OP_Ridge"):
    """telhado IRIMOYA: saia de 4 aguas + empena de 2 aguas em cima (triangulo recuado), cumeeira com onigawara"""
    W, Dd = w / 2 + over, d / 2 + over
    z1 = z0 + rise * 0.55
    zr = z0 + rise
    hd = 0.45 * Dd
    hw = max(W - (Dd - hd), W * 0.55)
    co = [F.p(-W, -Dd, z0), F.p(W, -Dd, z0), F.p(W, Dd, z0), F.p(-W, Dd, z0),
          F.p(-hw, -hd, z1), F.p(hw, -hd, z1), F.p(hw, hd, z1), F.p(-hw, hd, z1),
          F.p(-W, -Dd, z0 - th), F.p(W, -Dd, z0 - th), F.p(W, Dd, z0 - th), F.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7], [4, 5, 6, 7],
          [8, 9, 1, 0], [9, 10, 2, 1], [10, 11, 3, 2], [11, 8, 0, 3], [11, 10, 9, 8]]
    faces_solid(mb, co, fs, m)
    gw = hw + 0.9
    co = [F.p(-gw, -hd - 0.5, z1 - 0.25), F.p(gw, -hd - 0.5, z1 - 0.25), F.p(gw, 0, zr), F.p(-gw, 0, zr),
          F.p(gw, hd + 0.5, z1 - 0.25), F.p(-gw, hd + 0.5, z1 - 0.25),
          F.p(-gw, -hd - 0.5, z1 - 0.25 - th), F.p(gw, -hd - 0.5, z1 - 0.25 - th),
          F.p(gw, hd + 0.5, z1 - 0.25 - th), F.p(-gw, hd + 0.5, z1 - 0.25 - th)]
    fs = [[0, 1, 2, 3], [4, 5, 3, 2], [6, 7, 1, 0], [8, 9, 5, 4], [7, 8, 4, 2, 1], [9, 6, 0, 3, 5], [9, 8, 7, 6]]
    faces_solid(mb, co, fs, m)
    for s in (-1, 1):
        x = s * (gw - 0.6)
        co = [F.p(x, -hd, z1 - 0.1), F.p(x, hd, z1 - 0.1), F.p(x, 0, zr - 0.6),
              F.p(x - s * 0.3, -hd, z1 - 0.1), F.p(x - s * 0.3, hd, z1 - 0.1), F.p(x - s * 0.3, 0, zr - 0.6)]
        faces_solid(mb, co, [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]], gable_m)
    mb.box((2 * gw + 0.6, 1.0, 0.9), F.p(0, 0, zr + 0.2), F.r(), ridge_m, 0.0)
    for s in (-1, 1):
        mb.box((0.9, 1.3, 1.9), F.p(s * (gw + 0.2), 0, zr + 0.6), F.r(), ridge_ends, 0.0)
    return zr


def kirizuma(mb, F, w, d, z0, rise, over, m="Roof_OP_Blue", ridge_m="Roof_OP_Ridge", gable_m="Plaster_OP", th=0.6):
    W, Dd = w / 2 + over, d / 2 + over
    zr = z0 + rise
    co = [F.p(-W, -Dd, z0), F.p(W, -Dd, z0), F.p(W, 0, zr), F.p(-W, 0, zr), F.p(W, Dd, z0), F.p(-W, Dd, z0),
          F.p(-W, -Dd, z0 - th), F.p(W, -Dd, z0 - th), F.p(W, Dd, z0 - th), F.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 2, 3], [4, 5, 3, 2], [6, 7, 1, 0], [8, 9, 5, 4], [7, 8, 4, 2, 1], [9, 6, 0, 3, 5], [9, 8, 7, 6]]
    faces_solid(mb, co, fs, m)
    for s in (-1, 1):
        x = s * (w / 2)
        co = [F.p(x, -d / 2, z0 - 0.05), F.p(x, d / 2, z0 - 0.05), F.p(x, 0, zr - 0.5)]
        co += [F.p(x - s * 0.4, -d / 2, z0 - 0.05), F.p(x - s * 0.4, d / 2, z0 - 0.05), F.p(x - s * 0.4, 0, zr - 0.5)]
        faces_solid(mb, co, [[0, 1, 2], [5, 4, 3], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]], gable_m)
    mb.box((2 * W + 0.4, 0.9, 0.8), F.p(0, 0, zr + 0.15), F.r(), ridge_m, 0.0)
    return zr


def hip_roof(mb, F, w, d, z0, rise, over, ridge_len=0.0, m="Roof_OP_Blue", ridge_m="Roof_OP_Ridge", th=0.6):
    W, Dd = w / 2 + over, d / 2 + over
    zr = z0 + rise
    r = ridge_len / 2
    co = [F.p(-W, -Dd, z0), F.p(W, -Dd, z0), F.p(W, Dd, z0), F.p(-W, Dd, z0), F.p(-r - 0.01, 0, zr), F.p(r + 0.01, 0, zr),
          F.p(-W, -Dd, z0 - th), F.p(W, -Dd, z0 - th), F.p(W, Dd, z0 - th), F.p(-W, Dd, z0 - th)]
    fs = [[0, 1, 5, 4], [2, 3, 4, 5], [1, 2, 5], [3, 0, 4], [6, 7, 1, 0], [7, 8, 2, 1], [8, 9, 3, 2], [9, 6, 0, 3],
          [9, 8, 7, 6]]
    faces_solid(mb, co, fs, m)
    if ridge_len > 0.5:
        mb.box((ridge_len + 0.8, 0.9, 0.8), F.p(0, 0, zr + 0.15), F.r(), ridge_m, 0.0)
    return zr


def timber_box(mb, F, w, d, z0, h, wall_m="Plaster_OP", post_m="Wood_OP_Dark", band=True, posts=True):
    mb.box((w, d, h), F.p(0, 0, z0 + h / 2), F.r(), wall_m, 0.0)
    if posts:
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.box((0.9, 0.9, h + 0.2), F.p(sx * (w / 2 - 0.15), sy * (d / 2 - 0.15), z0 + h / 2), F.r(), post_m, 0.0)
        n = max(1, int(w / 6.0))
        for k in range(1, n):
            x = -w / 2 + w * k / n
            for sy in (-1, 1):
                mb.box((0.6, 0.5, h), F.p(x, sy * (d / 2 + 0.12), z0 + h / 2), F.r(), post_m, 0.0)
    if band:
        mb.box((w + 0.5, d + 0.5, 0.8), F.p(0, 0, z0 + h - 0.4), F.r(), post_m, 0.0)
        mb.box((w + 0.3, d + 0.3, 0.6), F.p(0, 0, z0 + 0.3), F.r(), post_m, 0.0)


def window(mb, F, u, v_face, z, ww, wh, out=1.0, frame_m="Wood_OP_Dark", glass_m="Window_OP_Warm"):
    mb.box((ww + 0.7, 0.35, wh + 0.7), F.p(u, v_face + out * 0.12, z), F.r(), frame_m, 0.0)
    mb.box((ww, 0.2, wh), F.p(u, v_face + out * 0.2, z), F.r(), glass_m, 0.0)


def loft(mb, pts, m, n=10, flat=0.86, caps=True, twist=0.0):
    """tronco/galho organico: aneis elipticos (raio r, achatamento flat) ao longo de pontos (x, y, z, r); o raio varia
    ponto a ponto (afinamento progressivo); as secoes acompanham a tangente (curva, nao tubo dobrado uniforme)"""
    P_ = [Vector(p[:3]) for p in pts]
    R = [p[3] for p in pts]
    rings = []
    up = Vector((0.0, 0.0, 1.0))
    prev_side = None
    for i, p in enumerate(P_):
        t = (P_[min(i + 1, len(P_) - 1)] - P_[max(i - 1, 0)]).normalized()
        u = up if abs(t.dot(up)) < 0.92 else Vector((1.0, 0.0, 0.0))
        side = t.cross(u).normalized()
        if prev_side is not None and side.dot(prev_side) < 0:
            side = -side
        prev_side = side
        vv = side.cross(t).normalized()
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n + twist * i
            ring.append(mb.bm.verts.new(p + side * (math.cos(a) * R[i]) + vv * (math.sin(a) * R[i] * flat)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            try:
                mb.bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
            except ValueError:
                pass
    if caps:
        for ring, rev in ((rings[0], True), (rings[-1], False)):
            try:
                mb.bm.faces.new(list(reversed(ring)) if rev else ring)
            except ValueError:
                pass
    mb._post([v for r in rings for v in r], m, None, 0, 1)


def catmull(pts, sub=3):
    """Catmull-Rom aberto em pontos (x, y, z, r)"""
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(4)))
    out.append(tuple(pts[-1]))
    return out


def tree(mb, x, y, z, h, r, m_leaf="Leaf_OP", m_bark="Bark_OP", lobes=3, rng=None, col=True):
    rng = rng or random.Random(int(x * 7 + y * 3) & 0xffff)
    mb.cyl(r * 0.12 + 0.6, h * 0.55, (x, y, z + h * 0.27), m=m_bark, n=7, r2=r * 0.08 + 0.4, bevel=0.0)
    for k in range(lobes):
        a = 2.4 * k + rng.uniform(0, 1)
        d = r * 0.35 if k else 0.0
        rr = r * (1.0 if k == 0 else 0.7)
        mb.ico(rr, (x + d * math.cos(a), y + d * math.sin(a), z + h * (0.62 + 0.12 * k)),
               m_leaf if isinstance(m_leaf, str) else m_leaf[k % len(m_leaf)], 1, scale=(1.0, 1.0, 0.62))
    if col:
        col_box("OP_VegTrunk", (r * 0.24 + 1.0, r * 0.24 + 1.0, 8.0), (x, y, z + 4.0))


def cherry(mb, x, y, z, h=11.0, r=6.5, col=True):
    """cerejeira (ACENTO): tronco inclinado + copa rosa em 3 massas achatadas (2 tons)"""
    rng = random.Random(int(x * 11 + y * 5) & 0xffff)
    lean = rng.uniform(-0.6, 0.6)
    loft(mb, [(x, y, z - 0.3, 0.9), (x + lean, y + lean * 0.5, z + h * 0.45, 0.6), (x + lean * 2.2, y + lean, z + h * 0.7, 0.45)],
         "Bark_OP", n=7)
    for k in range(3):
        a = 2.1 * k + rng.uniform(0, 1)
        d = r * 0.42 if k else 0.0
        mb.ico(r * (1.0 if k == 0 else 0.72), (x + lean * 2 + d * math.cos(a), y + lean + d * math.sin(a),
                                                z + h * (0.78 + 0.06 * k)),
               "Flower_OP_Blossom" if k != 1 else "Flower_OP_Light", 1, scale=(1.0, 1.0, 0.58))
    if col:
        col_box("OP_VegTrunk", (2.0, 2.0, 8.0), (x, y, z + 4.0))


def pine(mb, x, y, z, h, col=False):
    """pinheiro japones (proxy): tronco torto + 3 pratos de folhagem"""
    rng = random.Random(int(x * 3 + y * 13) & 0xffff)
    lx = rng.uniform(-2.0, 2.0)
    loft(mb, [(x, y, z - 0.3, 0.8), (x + lx * 0.5, y, z + h * 0.5, 0.55), (x + lx, y + 0.5, z + h * 0.85, 0.35)],
         "Bark_OP", n=6)
    for k, (fr, fz) in enumerate(((1.0, 0.55), (0.8, 0.75), (0.55, 0.92))):
        mb.ico(h * 0.28 * fr, (x + lx * fz + rng.uniform(-1, 1), y + rng.uniform(-1, 1), z + h * fz), "Leaf_OP_Pine", 1,
               scale=(1.0, 1.0, 0.36))
    if col:
        col_box("OP_VegTrunk", (1.6, 1.6, 8.0), (x, y, z + 4.0))


def lantern_post(mb, x, y, z, h=7.0, name_light=None, energy=150.0):
    """lanterna de poste (PROXY): pilar, braco, caixa com armacao escura e papel aceso DENTRO, chapeu"""
    mb.box((0.7, 0.7, h), (x, y, z + h / 2), (0, 0, 0), "Wood_OP_Dark", 0.0)
    mb.box((1.9, 1.9, 0.35), (x, y, z + h + 0.15), (0, 0, 0), "Wood_OP_Dark", 0.0)
    mb.box((1.3, 1.3, 1.6), (x, y, z + h + 1.15), (0, 0, 0), "Glass_OP_Lantern", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.22, 0.22, 1.7), (x + sx * 0.7, y + sy * 0.7, z + h + 1.15), (0, 0, 0), "Wood_OP_Dark", 0.0)
    mb.cyl(1.5, 0.7, (x, y, z + h + 2.3), m="Roof_OP_Ridge", n=4, r2=0.2, bevel=0.0, rot=(0, 0, math.pi / 4))
    col_box("OP_PropLamp", (0.8, 0.8, h), (x, y, z + h / 2))
    if name_light:
        light(name_light, "POINT", (x, y, z + h + 1.0), energy, WARM, 0.4)


def toro(mb, x, y, z, s=1.0, name_light=None):
    mb.box((2.6 * s, 2.6 * s, 0.6 * s), (x, y, z + 0.3 * s), (0, 0, 0), "Stone_OP", 0.0)
    mb.cyl(0.55 * s, 2.6 * s, (x, y, z + 1.9 * s), m="Stone_OP", n=8, bevel=0.0)
    mb.box((2.0 * s, 2.0 * s, 0.4 * s), (x, y, z + 3.4 * s), (0, 0, 0), "Stone_OP", 0.0)
    mb.box((1.7 * s, 1.7 * s, 1.5 * s), (x, y, z + 4.35 * s), (0, 0, 0), "Stone_OP", 0.0)
    mb.box((1.76 * s, 1.0 * s, 0.9 * s), (x, y, z + 4.35 * s), (0, 0, 0), "Glass_OP_Lantern", 0.0)
    mb.box((1.0 * s, 1.76 * s, 0.9 * s), (x, y, z + 4.35 * s), (0, 0, 0), "Glass_OP_Lantern", 0.0)
    mb.cyl(1.9 * s, 1.0 * s, (x, y, z + 5.6 * s), m="Stone_OP", n=6, r2=0.4 * s, bevel=0.0)
    mb.ico(0.4 * s, (x, y, z + 6.4 * s), "Stone_OP", 1)
    col_box("OP_PropToro", (2.6 * s, 2.6 * s, 6.0 * s), (x, y, z + 3.0 * s))
    if name_light:
        light(name_light, "POINT", (x, y, z + 4.35 * s), 140.0, WARM, 0.3)


def torii(mb, x, y, z, ang, w, h, area, scale=1.0):
    """torii de laca vermelha com kasagi preto de pontas levantadas; ang = rumo de quem atravessa (rad); vao w x h"""
    F = Frame(x, y, z, ang - math.pi / 2)
    s = scale
    px = w / 2 + 1.1 * s
    for sd in (-1, 1):
        mb.cyl(1.6 * s, 1.0 * s, F.p(sd * px, 0, 0.5 * s), m="Stone_OP_Dark", n=10, bevel=0.0)
        mb.cyl(1.15 * s, h + 3.0 * s, F.p(sd * px, 0, 1.0 * s + (h + 3.0 * s) / 2), m="Wood_OP_Lacquer", n=12,
               r2=1.0 * s, bevel=0.0)
        col_box(area, (2.8 * s, 2.8 * s, h + 4.0 * s), F.p(sd * px, 0, (h + 4.0 * s) / 2), F.r())
    mb.box((w + 8.0 * s, 1.2 * s, 1.4 * s), F.p(0, 0, h - 1.0 * s), F.r(), "Wood_OP_Lacquer", 0.0)          # nuki
    mb.box((1.2 * s, 1.0 * s, 3.0 * s), F.p(0, 0, h + 1.2 * s), F.r(), "Wood_OP_Lacquer", 0.0)              # gakuzuka
    mb.box((2.6 * s, 0.5 * s, 2.0 * s), F.p(0, -0.75 * s, h + 1.2 * s), F.r(), "Metal_OP_Gold", 0.0)        # placa
    mb.box((w + 9.0 * s, 2.0 * s, 1.2 * s), F.p(0, 0, h + 3.2 * s), F.r(), "Wood_OP_Lacquer", 0.0)          # shimaki
    span = w + 12.0 * s
    mb.box((span * 0.6, 2.6 * s, 1.1 * s), F.p(0, 0, h + 4.35 * s), F.r(), "Roof_OP_Ridge", 0.0)           # kasagi
    for sd in (-1, 1):
        mb.box((span * 0.24, 2.6 * s, 1.1 * s), F.p(sd * span * 0.39, 0, h + 4.6 * s), F.r(0, -sd * 0.12, 0),
               "Roof_OP_Ridge", 0.0)


def banner_pole(mb, x, y, z, h=16.0, face=0.0, col=True, m="Cloth_OP_White", crest="Cloth_OP_Indigo"):
    """mastro com estandarte vertical (nobori) branco e brasao indigo; a bandeira MARCA o lugar (praca/castelo)"""
    F = Frame(x, y, z, face)
    mb.cyl(0.35, h, F.p(0, 0, h / 2), m="Wood_OP_Dark", n=8, bevel=0.0)
    mb.box((2.8, 0.25, 0.35), F.p(1.4, 0, h - 0.6), F.r(), "Wood_OP_Dark", 0.0)
    mb.box((2.6, 0.18, h * 0.55), F.p(1.6, 0, h - 1.0 - h * 0.275), F.r(), m, 0.0)
    mb.cyl(0.9, 0.22, F.p(1.6, -0.13, h - 1.0 - h * 0.2), (math.pi / 2, 0, F.a), m=crest, n=12, bevel=0.0)
    mb.box((1.4, 1.4, 0.8), F.p(0, 0, 0.4), F.r(), "Stone_OP", 0.0)
    if col:
        col_box("OP_PropBanner", (1.4, 1.4, h), F.p(0, 0, h / 2), F.r())


# ------------------------------------------------------------------ terreno
def _edge_walls(mb, nm, poly, z, mat="Stone_OP", cap="Stone_OP_Path"):
    """muro de arrimo (ishigaki) nas bordas INTERNAS onde o vizinho e um piso mais baixo (> 1); aberto em escada/ponte"""
    pts = ccw(poly)
    n = len(pts)
    zf = lambda x, y: L._zval(z, x, y)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            continue
        nx, ny = dy / ln, -dx / ln
        k = max(1, int(ln / 1.5))
        run = []

        def flush(run):
            if len(run) < 2:
                return
            p0, p1 = run[0], run[-1]
            zt = max(zf(*p0), zf(*p1))
            zb = min(min(L.zone_of(p[0] + nx * 1.6, p[1] + ny * 1.6) or zt for p in run), zt) - 0.6
            sl = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            cx, cy = (p0[0] + p1[0]) / 2 + nx * 0.55, (p0[1] + p1[1]) / 2 + ny * 0.55
            ang = math.atan2(dy, dx)
            mb.box((sl + 1.2, 1.1, zt - zb), (cx, cy, (zb + zt) / 2), (0, 0, ang), mat, 0.0)
            mb.box((sl + 1.3, 1.5, 0.45), (cx - nx * 0.2, cy - ny * 0.2, zt + 0.2), (0, 0, ang), cap, 0.0)
        for s in range(k + 1):
            t = s / k
            x, y = a[0] + dx * t, a[1] + dy * t
            ok = L.floor_name(x - nx * 0.6, y - ny * 0.6) == nm
            zo = L.zone_of(x + nx * 1.6, y + ny * 1.6)
            ok = ok and zo is not None and zf(x, y) - zo > 1.0 and not op_col.opening(x + nx * 1.6, y + ny * 1.6)
            if ok:
                run.append((x, y))
            else:
                flush(run)
                run = []
        flush(run)


TOPS = {"Court": "Stone_OP_Path", "CastleLanding": "Stone_OP_Path", "W3": "Grass_OP", "Forecourt": "Stone_OP_Path",
        "Plaza": "Grass_OP", "W2b": "Grass_OP", "ExitLand": "Grass_OP", "T1": "Grass_OP",
        "Entry": "Stone_OP_Path", "HarborMid": "Stone_OP_Path", "Harbor": "Wood_OP_Mid"}


def terrain():
    rng = random.Random(11)
    rim = DL.rim()
    c = DL.centroid(rim)
    # quilha em ESTRATOS (Tier C): some sob o mar local na area 5; vista da Demon Slayer, ilha flutuante
    mk = MB("OP_Ter_Keel", "02_TERRAIN", rng, detail="far", floor=-999)
    mk.prism(rim, 22.0, L.SHOULDER - 0.4, "Cliff_OP")
    mk.prism(rim, L.SHOULDER - 0.4, L.SHOULDER, "Cliff_OP_Dark")
    sw = lambda k, ph, amp, base: (lambda i, a: base + amp * math.sin(k * a + ph) + 0.5 * amp * math.sin((k + 3) * a + 2 * ph))
    mk.prism(ccw(DL.offset_poly_var(rim, sw(3, 0.4, 2.4, -2.6))), 14.0, 22.0, "Cliff_OP_Dark")
    mk.prism(ccw(DL.scale_poly(DL.offset_poly_var(rim, sw(4, 1.7, 3.0, -2.0)), 0.88, c)), 6.0, 14.0, "Cliff_OP")
    mk.prism(ccw(DL.scale_poly(DL.offset_poly_var(rim[::2], sw(5, 2.9, 5.0, -4.0)), 0.66, c)), 1.0, 6.0, "Cliff_OP_Dark")
    mk.prism(ccw(DL.scale_poly(rim[::3], 0.36, c)), L.KEEL - 10.0, 1.0, "Cliff_OP")
    mk.finish()
    # patamares: massa de falesia ate o piso + tampo do material do chao (sem os entalhes das escadas)
    mt = MB("OP_Ter_Terraces", "02_TERRAIN", rng, detail="far", floor=-999)
    for nm, poly, z, pr in L.floors():
        if nm == "ShipDeck":
            continue
        for piece in L.floor_pieces(nm):
            DL.prism(mt, piece, L.BASE if nm != "Harbor" else L.BASE, z, "Cliff_OP", top_m=TOPS[nm])
    for nm, up, rect, zf, zt in L.stair_notches():
        fill = L.clip_rect(ccw(L.floor_poly(up)), rect) if up else []
        if len(fill) >= 3:
            low = L.floor_name(*L.stair_frame(nm)[0][:2])
            DL.prism(mt, fill, L.BASE, zf, "Cliff_OP", top_m=TOPS.get(low, "Stone_OP_Path"))
    mt.finish()
    mw = MB("OP_Ter_RetainingWalls", "02_TERRAIN", rng, detail="far", floor=-999)
    for nm, poly, z, pr in L.floors():
        if nm in ("ShipDeck", "Harbor"):
            continue
        _edge_walls(mw, nm, poly, z)
    mw.finish()
    # ombros e rochas que fecham a borda (nada de prateleira rente a agua), raiz NE, fundo alto
    mr = MB("OP_Ter_Rocks", "02_TERRAIN", rng, detail="far", floor=-999)
    for nm, pts, z in L.ROCKS:
        DL.prism(mr, pts, L.BASE, z, "Cliff_OP", top_m="Cliff_OP_Moss")
    # agulhas de rocha no fundo (moldura do castelo, Tier C), sem ilhotas soltas
    for x, y, r, h in ((-118.0, 462.0, 12.0, 150.0), (-60.0, 486.0, 14.0, 162.0), (110.0, 486.0, 13.0, 156.0),
                       (176.0, 452.0, 12.0, 142.0), (232.0, 352.0, 11.0, 128.0)):
        DL.prism(mr, DL.blob_poly(x, y, r, 9, rng, 0.2), 60.0, h - 6.0, "Cliff_OP")
        DL.prism(mr, DL.blob_poly(x, y, r * 0.75, 8, rng, 0.2), h - 6.0, h, "Cliff_OP_Moss")
    mr.finish()


# ------------------------------------------------------------------ entrada: ponte de 120, GRANDE torii, patio, toro
def entry():
    rng = random.Random(33)
    mb = MB("OP_Ent_Blockout", "18_ENTRY", rng, detail="far", floor=-999)
    ln = L.BRIDGE_IN_LEN
    pitch = math.atan2(L.T0 - L.DECK, ln)
    zc = (L.DECK + L.T0) / 2
    mb.box((L.DECK_W, ln + 0.5, 1.2), (0.0, L.PREV_Y + ln / 2, zc - 0.6), (pitch, 0, 0), "Wood_OP_Dark", 0.0)
    for s in (-1, 1):
        x = s * (L.DECK_W / 2 + 0.4)
        mb.box((1.0, ln + 0.5, 1.6), (x, L.PREV_Y + ln / 2, zc - 0.5), (pitch, 0, 0), "Wood_OP_Lacquer", 0.0)
        mb.box((0.6, ln + 0.5, 0.55), (x, L.PREV_Y + ln / 2, zc + 3.6), (pitch, 0, 0), "Wood_OP_Lacquer", 0.0)
        for k in range(0, int(ln) + 1, 6):
            y = L.PREV_Y + k
            zz = L.DECK + (L.T0 - L.DECK) * k / ln
            mb.box((0.7, 0.7, 3.9), (x, y, zz + 1.95), (0, 0, 0), "Wood_OP_Lacquer", 0.0)
            mb.box((0.9, 0.9, 0.5), (x, y, zz + 4.1), (0, 0, 0), "Metal_OP_Gold", 0.0)
    # pilares de pedra (afinando ate a quilha) a cada ~24 + vigas
    for k in (16, 40, 64, 88, 108):
        y = L.PREV_Y + k
        zz = L.DECK + (L.T0 - L.DECK) * k / ln
        for s in (-1, 1):
            mb.cyl(2.4, zz - 18.0, (s * 6.5, y, (zz + 18.0) / 2 - 1.2), m="Stone_OP", n=8, r2=1.6, bevel=0.0)
        mb.box((17.0, 1.6, 1.6), (0.0, y, zz - 2.0), (0, 0, 0), "Wood_OP_Dark", 0.0)
    for s in (-1, 1):
        zz = L.DECK + (L.T0 - L.DECK) * 0.5
        lantern_post(mb, s * (L.DECK_W / 2 + 0.4), L.PREV_Y + 60.0, zz, 6.0,
                     "L_OPProp_Lamp_Bridge_%s" % ("L" if s < 0 else "R"), 140.0)
    mb.box((L.DECK_W + 3.0, 10.0, 1.6), (0.0, L.PREV_Y + 5.0, L.DECK - 0.75), (pitch, 0, 0), "Stone_OP_Dark", 0.0)
    tx, ty = L.TORII_IN
    torii(mb, tx, ty, T0, math.pi / 2, L.TORII_W, L.TORII_H, "OP_EntTorii", 1.2)
    toro(mb, -15.0, 24.0, T0, 1.1, "L_OPProp_Toro_In_L")
    toro(mb, 15.0, 24.0, T0, 1.1, "L_OPProp_Toro_In_R")
    for s in (-1, 1):                                     # 2 nobori vermelhos ladeando o torii (concept)
        banner_pole(mb, s * 19.5, 4.0, T0, 11.0, 0.0 if s > 0 else math.pi, m="Cloth_OP_Red", crest="Cloth_OP_White")
    DL.plan_stair(mb, "Chegada")
    mb.finish()


# ------------------------------------------------------------------ capital: construcoes por familia
def house(mb, spec, area="OP_CapHouse"):
    nm, fam, x, y, w, d, deg, z, fl, roof, rm = spec
    F = Frame(x, y, z, math.radians(deg) - math.pi / 2)     # +y local = FRENTE; x local ao longo da fachada
    soco = 1.0
    stone = "Stone_OP_Dark" if fam in ("armazem", "santuario") else "Stone_OP"
    mb.box((w + 1.0, d + 1.0, soco), F.p(0, 0, soco / 2), F.r(), stone, 0.0)
    z0 = soco
    wall = {"loja": "Plaster_OP_Shop", "casa": "Plaster_OP_Warm", "esquina": "Plaster_OP", "mansao": "Plaster_OP",
            "santuario": "Plaster_OP", "armazem": "Plaster_OP", "moinho": "Plaster_OP_Warm", "pavilhao": None}[fam]
    if fam == "pavilhao":
        mb.box((w, d, 0.6), F.p(0, 0, z0 + 0.3), F.r(), "Wood_OP_Mid", 0.0)
        for sx in (-1, 0, 1):
            for sy in (-1, 1):
                if sx == 0 and w < 16:
                    continue
                mb.box((0.9, 0.9, 7.5), F.p(sx * (w / 2 - 0.7), sy * (d / 2 - 0.7), z0 + 3.75), F.r(), "Wood_OP_Lacquer"
                       if rm == "Roof_OP_Red" else "Wood_OP_Dark", 0.0)
                col_box(area + nm, (1.0, 1.0, 7.5), F.p(sx * (w / 2 - 0.7), sy * (d / 2 - 0.7), z0 + 3.75), F.r())
        hip_roof(mb, F, w, d, z0 + 7.5, 4.6, 2.4, ridge_len=w * 0.4, m=rm)
        return
    h1 = {"loja": 7.0, "casa": 7.0, "esquina": 7.5, "mansao": 8.0, "santuario": 8.5, "armazem": 9.0, "moinho": 7.0}[fam]
    htot = h1
    if fam == "armazem":                                   # armazem: reboco grosso, base escura, porta de madeira
        mb.box((w + 0.4, d + 0.4, 2.0), F.p(0, 0, z0 + 1.0), F.r(), "Stone_OP_Dark", 0.0)
        mb.box((w, d, h1 * fl * 0.85), F.p(0, 0, z0 + h1 * fl * 0.425), F.r(), wall, 0.0)
        mb.box((5.0, 0.4, 6.0), F.p(0, d / 2 + 0.15, z0 + 3.0), F.r(), "Wood_OP_Dark", 0.0)
        htot = h1 * fl * 0.85
        window(mb, F, 0.0, d / 2, z0 + htot - 2.4, 2.0, 1.4)
    else:
        timber_box(mb, F, w, d, z0, h1, wall)
        if fam == "loja":                                  # comercio CENOGRAFICO: frente com treliça escura + noren
            mb.box((w * 0.74, 0.3, 5.0), F.p(0, d / 2 + 0.16, z0 + 2.7), F.r(), "Wood_OP_Dark", 0.0)
            for k in range(3):
                u = -w * 0.24 + k * w * 0.24
                mb.box((w * 0.2, 0.3, 2.2), F.p(u, d / 2 + 0.35, z0 + 4.4), F.r(), "Cloth_OP_Indigo", 0.0)
            mb.box((w + 1.6, 3.2, 0.4), F.p(0, d / 2 + 1.6, z0 + h1 - 0.2), F.r(-0.28, 0, 0), "Roof_OP_Ridge", 0.0)  # alpendre
        elif fam == "santuario":
            mb.box((w - 4.0, 0.3, 6.0), F.p(0, d / 2 + 0.16, z0 + 3.0), F.r(), "Wood_OP_Lacquer", 0.0)
            mb.box((w + 2.0, 4.0, 0.6), F.p(0, d / 2 + 2.0, z0 - 0.3), F.r(), "Wood_OP_Mid", 0.0)
        else:
            for u in (-w * 0.28, w * 0.28):
                window(mb, F, u, d / 2, z0 + 3.8, 2.4, 2.0)
            mb.box((2.8, 0.35, 5.2), F.p(0, d / 2 + 0.14, z0 + 2.6), F.r(), "Wood_OP_Dark", 0.0)
        zz = z0 + h1
        for k in range(1, fl):                              # pisos de cima recuados com saia de telhado entre eles
            frustum(mb, F, w + 3.0, d + 3.0, zz + 0.2, w - 1.0, d - 1.0, zz + 1.6, rm)
            ww, dd = w - 2.0 * k, d - 1.6 * k
            timber_box(mb, F, ww, dd, zz + 0.6, 6.0, wall)
            window(mb, F, 0.0, dd / 2, zz + 3.4, min(ww * 0.5, 6.0), 1.8)
            if fam == "esquina" and k == fl - 1:            # varanda de madeira (gesto proprio da esquina)
                mb.box((ww + 1.2, 2.0, 0.4), F.p(0, dd / 2 + 1.0, zz + 0.9), F.r(), "Wood_OP_Mid", 0.0)
                mb.box((ww + 1.2, 0.3, 1.2), F.p(0, dd / 2 + 1.9, zz + 1.6), F.r(), "Wood_OP_Lacquer", 0.0)
            zz += 6.6
        htot = zz - z0
        w, d = (w - 2.0 * (fl - 1), d - 1.6 * (fl - 1))
    if fam == "esquina" or fam == "mansao" or fam == "santuario":
        top = irimoya(mb, F, w, d, z0 + htot, 6.5 if fam != "mansao" else 7.0, 2.6, m=rm)
    elif roof == "kirizuma":
        top = kirizuma(mb, F, w, d, z0 + htot, 5.0, 1.6, m=rm, gable_m="Plaster_OP" if fam != "moinho" else "Wood_OP_Mid")
    else:
        top = irimoya(mb, F, w, d, z0 + htot, 5.5, 2.2, m=rm)
    if fam == "santuario":
        for s in (-1, 1):
            mb.box((0.6, 1.0, 1.4), F.p(s * (w / 2 + 2.0), 0, top + 0.8), F.r(), "Metal_OP_Gold", 0.0)
    W0, D0 = spec[4], spec[5]
    col_box(area + nm, (W0 + 0.4, D0 + 0.4, htot + soco), F.p(0, 0, (htot + soco) / 2), F.r())
    light("L_OPCap_Win_%s" % nm, "POINT", F.p(0, D0 / 2 + 2.0, z0 + 3.0), 60.0, WARM, 0.4) if fam in ("loja", "esquina") else None


def capital():
    rng = random.Random(55)
    mb = MB("OP_Cap_Blockout", "05_CAPITAL", rng, detail="far", floor=None)
    for spec in L.BUILDINGS:
        if spec[0].startswith("H"):
            continue
        house(mb, spec)
    for nm in ("Praca", "Sudoeste", "OesteAlta"):
        DL.plan_stair(mb, nm)
    # santuario NE: torii pequeno vermelho
    torii(mb, L.SHRINE_TORII[0], L.SHRINE_TORII[1], P, 0.0, 8.0, 9.0, "OP_CapTorii", 0.6)
    # recanto de descanso da rua de chegada (banco + lanterna) e lanternas de rua
    mb.box((6.0, 1.6, 1.4), (-27.0, 91.6, T1 + 0.7), (0, 0, 0), "Wood_OP_Mid", 0.0)
    col_box("OP_CapBench", (6.0, 1.6, 1.4), (-27.0, 91.6, T1 + 0.7))
    for i, (x, y, z) in enumerate(((-14.0, 50.0, T1), (14.0, 66.0, T1), (-14.0, 96.0, T1), (14.0, 80.0, T1))):
        lantern_post(mb, x, y, z, 6.5, "L_OPProp_Lamp_Rua_%d" % i, 120.0)
    mb.finish()
    # pisos visuais das ruas (lajes claras rente: o tampo do patamar ja e Stone_OP_Path; aqui so meio-fio do canal)
    mp = MB("OP_Cap_Streets", "05_CAPITAL", rng, detail="far", floor=-999)
    for pts, w, z in L.STREETS:
        mp.prism(ccw(L.ribbon(pts, w / 2)), z - 0.2, z + 0.12, "Stone_OP_Path")
    mp.finish()


# ------------------------------------------------------------------ praca de mineracao
def plaza(ore_proxies=False):
    rng = random.Random(66)
    mb = MB("OP_Plz_Paving", "03_PLAZA", rng, detail="far", floor=-999)
    mb.prism(ccw(L.PLAZA), P - 0.3, P + 0.12, "Stone_OP_Plaza")
    # emblema RENTE (0,12 acima do piso: le como incrustacao; sem colisao, sem pedestal): anel + 8 petalas + miolo
    ex, ey = L.EMBLEM_C
    R = L.EMBLEM_R
    ring_o = L.circle_poly((ex, ey), R, 10.0)
    for k in range(36):
        a0, a1 = math.radians(k * 10), math.radians(k * 10 + 10)
        q = [(ex + (R - 1.4) * math.cos(a0), ey + (R - 1.4) * math.sin(a0)), (ex + R * math.cos(a0), ey + R * math.sin(a0)),
             (ex + R * math.cos(a1), ey + R * math.sin(a1)), (ex + (R - 1.4) * math.cos(a1), ey + (R - 1.4) * math.sin(a1))]
        mb.prism(ccw(q), P + 0.02, P + 0.24, "Stone_OP_Inlay")
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        c = (ex + 6.6 * math.cos(a), ey + 6.6 * math.sin(a))
        pet = [(c[0] + 3.2 * math.cos(a) * math.cos(t) - 1.4 * -math.sin(a) * math.sin(t),
                c[1] + 3.2 * math.sin(a) * math.cos(t) - 1.4 * math.cos(a) * math.sin(t))
               for t in [i * math.pi / 5 for i in range(10)]]
        mb.prism(ccw(pet), P + 0.02, P + 0.24, "Stone_OP_Inlay")
    mb.prism(ccw(L.circle_poly((ex, ey), 2.2, 30.0)), P + 0.02, P + 0.24, "Stone_OP_Inlay")
    mb.finish()
    del ring_o
    # meio-fio da praca (faixa de pedra na borda, rente) e estandartes nos cantos (fora da zona + 8)
    me = MB("OP_Plz_Edge", "03_PLAZA", rng, detail="far", floor=None)
    pts = ccw(L.PLAZA)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        me.box((ln + 0.6, 1.4, 0.5), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, P - 0.05), (0, 0, math.atan2(dy, dx)), "Stone_OP", 0.0)
    for i, (x, y) in enumerate(L.BANNERS):
        banner_pole(me, x, y, P, 18.0, math.atan2(L.MINE_C[1] - y, L.MINE_C[0] - x) - math.pi / 2)
    for i, x in enumerate((-17.0, 17.0)):
        lantern_post(me, x, 123.0, P, 7.0, "L_OPProp_Lamp_PracaS_%d" % i, 140.0)
        lantern_post(me, x * 1.25, 306.0, P, 7.0, "L_OPProp_Lamp_PracaN_%d" % i, 140.0)
    me.finish()
    if ore_proxies:
        mo = MB("OP_Plz_OreProxy", "03_PLAZA", rng, detail="far", floor=-999)
        for kind, i, x, y, r in L.ore_points():
            mo.cyl(r * 0.6, r * 0.9, (x, y, P + r * 0.45), m="OP_OreProxy", n=6, r2=r * 0.25, bevel=0.0)
        mo.finish()


# ------------------------------------------------------------------ castelo (heroi)
def keep(mb):
    """torre de menagem: 4 andares escalonados (reboco claro, base de pedra, saias de telha escura, chidori na frente,
    varanda vermelha no 4o, shachihoko dourados); TERREO ACESSIVEL: porta aberta -> salao real com piso, teto, luz"""
    kx, ky = L.KEEP_C
    F = Frame(kx, ky, CC, math.pi)                       # +y local = frente = -Y do mundo (praca)
    hx0, hy0 = L.KEEP_TIERS[0][:2]
    # base de pedra (tenshudai) com talude: 4 faces inclinadas encostadas na parede (a da frente aberta na porta)
    door_w, door_h = L.KEEP_DOOR[2], L.KEEP_DOOR[3]
    sec = [(0.0, 0.0), (3.0, 0.0), (0.4, 5.0), (0.0, 5.0)]          # (para fora, z): talude de 3 em 5
    for side, (cu, cv, ang, half) in enumerate(((0.0, hy0, 0.0, hx0), (0.0, -hy0, math.pi, hx0),
                                                (hx0, 0.0, -math.pi / 2, hy0), (-hx0, 0.0, math.pi / 2, hy0))):
        p0 = F.p(cu, cv, 0.0)
        Fs = Frame(p0.x, p0.y, CC, F.a + ang)
        spans = [(-half - 3.0, -door_w / 2 - 2.0), (door_w / 2 + 2.0, half + 3.0)] if side == 0 else [(-half - 3.0, half + 3.0)]
        for a0, a1 in spans:
            co = [Fs.p(a0, o, z) for o, z in sec] + [Fs.p(a1, o, z) for o, z in sec]
            faces_solid(mb, co, [[0, 1, 2, 3], [7, 6, 5, 4], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]],
                        "Stone_OP")
    for i, (hx, hy, z0, hw_, over) in enumerate(L.KEEP_TIERS):
        w, d = 2 * hx, 2 * hy
        if i == 0:
            # terreo OCO: 4 paredes de 2 (porta aberta na frente), teto, tatame, salao com luz
            t = 2.0
            wall_h = hw_
            for s in (-1, 1):
                mb.box((t, d, wall_h), F.p(s * (hx - t / 2), 0, z0 + wall_h / 2), F.r(), "Plaster_OP", 0.0)
                col_box("OP_CasKeep", (t, d, wall_h), F.p(s * (hx - t / 2), 0, z0 + wall_h / 2), F.r())
            mb.box((w, t, wall_h), F.p(0, -(hy - t / 2), z0 + wall_h / 2), F.r(), "Plaster_OP", 0.0)
            col_box("OP_CasKeep", (w, t, wall_h), F.p(0, -(hy - t / 2), z0 + wall_h / 2), F.r())
            side = (w - door_w) / 2
            for s in (-1, 1):
                mb.box((side, t, wall_h), F.p(s * (door_w / 2 + side / 2), hy - t / 2, z0 + wall_h / 2), F.r(),
                       "Plaster_OP", 0.0)
                col_box("OP_CasKeep", (side, t, wall_h), F.p(s * (door_w / 2 + side / 2), hy - t / 2, z0 + wall_h / 2), F.r())
            mb.box((door_w, t, wall_h - door_h), F.p(0, hy - t / 2, z0 + door_h + (wall_h - door_h) / 2), F.r(),
                   "Plaster_OP", 0.0)
            col_box("OP_CasKeep", (door_w, t, wall_h - door_h), F.p(0, hy - t / 2, z0 + door_h + (wall_h - door_h) / 2), F.r())
            # moldura da porta (madeira escura + verga dourada) e soco de pedra externo (6 de altura)
            for s in (-1, 1):
                mb.box((0.8, 0.9, door_h), F.p(s * (door_w / 2 + 0.4), hy + 0.1, z0 + door_h / 2), F.r(), "Wood_OP_Dark", 0.0)
            mb.box((door_w + 2.4, 0.9, 0.9), F.p(0, hy + 0.1, z0 + door_h + 0.45), F.r(), "Metal_OP_Gold", 0.0)
            for s in (-1, 1):
                mb.box((side - 0.4, 0.5, 6.0), F.p(s * (door_w / 2 + 0.8 + (side - 1.2) / 2), hy + 0.24, z0 + 3.0), F.r(),
                       "Stone_OP", 0.0)
            mb.box((w - 4.4, d - 4.4, 0.25), F.p(0, 0, z0 + 0.125), F.r(), "Wood_OP_Mid", 0.0)        # tatame
            mb.box((w - 3.8, d - 3.8, 0.6), F.p(0, 0, z0 + 12.3), F.r(), "Wood_OP_Dark", 0.0)          # teto
            col_box("OP_CasKeepCeil", (w - 3.8, d - 3.8, 0.6), F.p(0, 0, z0 + 12.3), F.r())
            mb.box((w - 4.0, d - 4.0, wall_h - 12.6), F.p(0, 0, z0 + 12.6 + (wall_h - 12.6) / 2), F.r(), "Plaster_OP", 0.0)
            for zz in (z0 + 14.6,):
                for u in (-hx * 0.55, hx * 0.55):
                    window(mb, F, u, hy, zz, 3.0, 2.2)
            light("L_OPCas_Hall_1", "POINT", F.p(-6.0, 0.0, z0 + 8.0), 260.0, WARM, 0.5)
            light("L_OPCas_Hall_2", "POINT", F.p(6.0, -4.0, z0 + 8.0), 260.0, WARM, 0.5)
            light("L_OPCas_Hall_3", "POINT", F.p(0.0, 10.0, z0 + 8.0), 160.0, WARM, 0.5)
        else:
            timber_box(mb, F, w, d, z0, hw_, "Plaster_OP", post_m="Wood_OP_Dark", band=True, posts=False)
            for u in (-hx * 0.5, 0.0, hx * 0.5):
                window(mb, F, u, hy, z0 + hw_ * 0.55, 2.0, 1.8)
                window(mb, F, u, -hy, z0 + hw_ * 0.55, 2.0, 1.8, out=-1.0)
            for v in (-hy * 0.45, hy * 0.45):
                Fs = Frame(F.p(0, v, 0).x, F.p(0, v, 0).y, CC, F.a + math.pi / 2)
                window(mb, Fs, 0.0, hx, z0 + hw_ * 0.55, 2.0, 1.8)
                window(mb, Fs, 0.0, -hx, z0 + hw_ * 0.55, 2.0, 1.8, out=-1.0)
        ztop = z0 + hw_
        if i < len(L.KEEP_TIERS) - 1:
            nx_, ny_ = L.KEEP_TIERS[i + 1][:2]
            frustum(mb, F, w + 2 * over, d + 2 * over, ztop + 0.3, 2 * nx_ + 1.0, 2 * ny_ + 1.0, ztop + 3.4, "Roof_OP_Blue", 0.8)
            # chidori-hafu (empena triangular) na frente das saias dos andares 1 e 2; a do 1 tem friso dourado
            if i < 2:
                Fg = Frame(F.p(0, hy + over * 0.4, 0).x, F.p(0, hy + over * 0.4, 0).y, CC, F.a)
                kirizuma(mb, Fg, 10.0 - 2.0 * i, 5.0, ztop + 0.9, 3.4, 0.6, m="Roof_OP_Blue", gable_m="Plaster_OP")
                mb.box((2.2, 0.4, 1.6), Fg.p(0, 3.2, ztop + 2.2), Fg.r(), "Metal_OP_Gold", 0.0)
            if i == 2:                                      # varanda vermelha (mawarien) em volta do 4o andar
                hx3, hy3 = L.KEEP_TIERS[3][:2]
                mb.box((2 * hx3 + 4.0, 2 * hy3 + 4.0, 0.5), F.p(0, 0, ztop + 3.6), F.r(), "Wood_OP_Mid", 0.0)
                for s in (-1, 1):
                    mb.box((2 * hx3 + 4.0, 0.4, 1.4), F.p(0, s * (hy3 + 2.0), ztop + 4.5), F.r(), "Wood_OP_Lacquer", 0.0)
                    mb.box((0.4, 2 * hy3 + 4.0, 1.4), F.p(s * (hx3 + 2.0), 0, ztop + 4.5), F.r(), "Wood_OP_Lacquer", 0.0)
        else:
            zr = irimoya(mb, F, w, d, ztop + 0.3, 7.5, over, m="Roof_OP_Blue", ridge_m="Roof_OP_Ridge",
                         gable_m="Plaster_OP", ridge_ends="Metal_OP_Gold")
            for s in (-1, 1):                               # shachihoko dourados nas pontas da cumeeira
                p = F.p(s * (w / 2 + over * 0.55 - 1.2), 0, zr + 1.8)
                mb.box((1.0, 1.6, 3.0), p, F.r(0, s * 0.35, 0), "Metal_OP_Gold", 0.0)
    col_box("OP_CasKeepUpper", (2 * hx0, 2 * hy0, 40.0), F.p(0, 0, 18.0 + 20.0), F.r())


def castle():
    rng = random.Random(77)
    mb = MB("OP_Cas_Blockout", "04_CASTLE", rng, detail="far", floor=None)
    # adro: portao vermelho sobre o topo da escada Adro (moldura do eixo praca -> cachoeira -> castelo)
    gx, gy, gw = L.CASTLE_GATE
    Fg = Frame(gx, gy, CF, 0.0)
    for s in (-1, 1):
        px = s * (gw / 2 + 1.2)
        mb.box((2.4, 2.4, 15.0), Fg.p(px, 0, 7.5), Fg.r(), "Wood_OP_Lacquer", 0.0)
        mb.box((3.2, 3.2, 1.0), Fg.p(px, 0, 0.5), Fg.r(), "Stone_OP_Dark", 0.0)
        mb.box((1.6, 1.6, 12.0), Fg.p(px, -3.4, 6.0), Fg.r(), "Wood_OP_Lacquer", 0.0)      # pilar de apoio
        col_box("OP_CasGate", (3.2, 6.4, 15.0), Fg.p(px, -1.6, 7.5), Fg.r())
        lantern_post(mb, px + s * 4.0, gy - 2.0, CF, 6.0, None)
    mb.box((gw + 6.0, 2.0, 1.6), Fg.p(0, 0, 14.0), Fg.r(), "Wood_OP_Lacquer", 0.0)
    mb.box((6.0, 0.6, 2.4), Fg.p(0, -1.2, 14.0), Fg.r(), "Metal_OP_Gold", 0.0)
    irimoya(mb, Frame(gx, gy - 1.6, CF, 0.0), gw + 4.0, 7.0, 15.0, 5.0, 2.2, m="Roof_OP_Blue", gable_m="Wood_OP_Lacquer")
    # escadas da subida (cortadas no flanco oeste da rocha) + patamar
    DL.plan_stair(mb, "Adro")
    DL.plan_stair(mb, "CasteloA", side_floor=CF)
    DL.plan_stair(mb, "CasteloB", side_floor=L.CL)
    # portao do patio (pequeno) no topo da CasteloB
    cx_, cy_, cw_ = L.COURT_GATE
    Fc = Frame(cx_, cy_, CC, 0.0)
    for s in (-1, 1):
        mb.box((1.6, 1.6, 10.0), Fc.p(s * (cw_ / 2 + 0.8), 0, 5.0), Fc.r(), "Wood_OP_Dark", 0.0)
        col_box("OP_CasCourtGate", (1.6, 1.6, 10.0), Fc.p(s * (cw_ / 2 + 0.8), 0, 5.0), Fc.r())
    kirizuma(mb, Fc, cw_ + 3.0, 4.0, 10.0, 2.4, 1.0, m="Roof_OP_Blue", gable_m="Wood_OP_Dark")
    # VARANDA VERMELHA do patio: guarda-corpo vermelho na borda da frente (mirante sobre a cidade)
    rail = [(-63.4, 376.0, CC), (-49.6, 358.6, CC), (-24.0, 352.6, CC), (24.0, 352.6, CC), (49.6, 358.6, CC),
            (65.4, 372.4, CC)]
    DL.vis_fence(mb, rail, h=3.4, post_step=4.0, m="Wood_OP_Lacquer", rail_m="Wood_OP_Lacquer")
    # muros brancos (dobei) com cobertura de telha no fundo e no flanco leste do patio
    for pts in ([(74.0, 380.0), (74.0, 440.0), (62.0, 467.0), (20.0, 475.0), (-40.0, 473.0), (-88.0, 459.0)],):
        DL.wall_ribbon(mb, pts, CC, CC + 5.0, 1.2, "Plaster_OP", cap_m="Roof_OP_Blue", cap_h=0.7, side=1.0)
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            nx, ny = -dy / ln, dx / ln
            col_box("OP_CasWall", (ln + 1.0, 1.4, 5.0), ((a[0] + b[0]) / 2 + nx * 0.6, (a[1] + b[1]) / 2 + ny * 0.6, CC + 2.5),
                    (0, 0, math.atan2(dy, dx)))
    # yagura (torreao de 2 andares) no canto SE do patio
    tx, ty, ts = L.TURRET
    Ft = Frame(tx, ty, CC, math.pi)
    mb.box((ts + 1.0, ts + 1.0, 1.4), Ft.p(0, 0, 0.7), Ft.r(), "Stone_OP", 0.0)
    timber_box(mb, Ft, ts, ts, 1.4, 8.0, "Plaster_OP", posts=False)
    frustum(mb, Ft, ts + 4.0, ts + 4.0, 9.6, ts - 2.0, ts - 2.0, 11.6, "Roof_OP_Blue")
    timber_box(mb, Ft, ts - 3.0, ts - 3.0, 10.8, 5.0, "Plaster_OP", posts=False)
    irimoya(mb, Ft, ts - 3.0, ts - 3.0, 15.8, 4.0, 1.8)
    window(mb, Ft, 0.0, ts / 2, 6.0, 2.4, 1.6)
    col_box("OP_CasTurret", (ts + 1.0, ts + 1.0, 16.0), Ft.p(0, 0, 8.0), Ft.r())
    # estandartes gigantes na face da rocha, um de cada lado da cachoeira (concept)
    for s in (-1, 1):
        x = s * 15.0
        mb.box((7.0, 0.5, 20.0), (x, 351.2, CC - 15.0), (0, 0, 0), "Cloth_OP_White", 0.0)
        mb.cyl(2.4, 0.4, (x, 350.8, CC - 11.0), (math.pi / 2, 0, 0), m="Cloth_OP_Indigo", n=14, bevel=0.0)
        mb.box((8.4, 0.8, 0.8), (x, 351.4, CC - 4.6), (0, 0, 0), "Wood_OP_Dark", 0.0)
    keep(mb)
    lantern_post(mb, -56.0, 386.0, CC, 6.0, "L_OPProp_Lamp_Patio_0", 120.0)
    lantern_post(mb, 46.0, 386.0, CC, 6.0, "L_OPProp_Lamp_Patio_1", 120.0)
    mb.finish()
    # falesia do castelo: colunas de rocha verticais na face da frente e nos flancos (alturas e larguras dirigidas,
    # mais altas nos lados, baixas no meio para a cachoeira e os estandartes)
    mr = MB("OP_Cas_Cliff", "04_CASTLE", rng, detail="far", floor=-999)
    cols = [(-58.0, 362.0, 7.0, CC - 4.0), (-46.0, 351.0, 6.0, CC - 10.0), (-34.0, 347.0, 5.0, CC - 18.0),
            (30.0, 346.0, 5.0, CC - 16.0), (42.0, 348.0, 6.5, CC - 8.0), (56.0, 356.0, 7.0, CC - 2.0),
            (68.0, 368.0, 6.0, CC + 2.0), (76.0, 392.0, 7.0, CC - 6.0), (78.0, 420.0, 6.0, CC + 4.0),
            (-86.0, 446.0, 6.0, CC - 6.0)]
    for x, y, r, zt in cols:
        DL.prism(mr, DL.blob_poly(x, y, r, 8, rng, 0.16), CF - 2.0, zt, "Cliff_OP", top_m="Cliff_OP_Moss")
    mr.finish()


# ------------------------------------------------------------------ arvore monumental arqueada
def tree_monument():
    rng = random.Random(91)
    mb = MB("OP_Tree_Blockout", "04_CASTLE", rng, detail="far", floor=-999)
    # base convincente: monte de rocha com raizes agarradas na borda do patio e descendo a falesia leste
    bx, by = L.TREE_TRUNK[0][:2]
    DL.prism(mb, DL.blob_poly(bx, by, 14.0, 11, rng, 0.15), CC - 4.0, CC + 1.6, "Cliff_OP", top_m="Cliff_OP_Moss")
    trunk = catmull(L.TREE_TRUNK, 4)
    # sinuosidade dirigida (nao sorteio): leve torcao lateral ao longo do tronco
    trunk = [(x + 1.2 * math.sin(i * 0.5), y + 0.8 * math.cos(i * 0.4), z, r) for i, (x, y, z, r) in enumerate(trunk)]
    loft(mb, trunk, "Bark_OP", n=12, flat=0.82)
    for idx, pts in L.TREE_BRANCHES:
        p0 = L.TREE_TRUNK[idx]
        loft(mb, catmull([(p0[0], p0[1], p0[2], p0[3] * 0.55)] + pts, 3), "Bark_OP", n=8, flat=0.85)
    for rx, ry, rz, rr in L.TREE_ROOTS:
        mid = ((bx + rx) / 2, (by + ry) / 2, CC + 2.0, rr * 1.2)
        loft(mb, [(bx, by, CC + 6.0, rr * 1.8), mid, (rx, ry, rz, rr * 0.5)], "Bark_OP", n=7, flat=0.7)
    # copa florida: massas principais e secundarias (2 tons de rosa + um pouco de verde por baixo)
    for k, (c, r, fl) in enumerate(L.TREE_CANOPY):
        mat = "Flower_OP_Blossom" if k % 3 != 2 else "Flower_OP_Light"
        mb.ico(r, c, mat, 2, scale=(1.0, 0.85, fl))
        for j in range(3):                                   # lobos secundarios (borda recortada da nuvem)
            a = 2.1 * j + k
            mb.ico(r * 0.5, (c[0] + r * 0.72 * math.cos(a), c[1] + r * 0.4 * math.sin(a), c[2] + r * fl * (0.25 - 0.2 * j)),
                   "Flower_OP_Light" if j == 1 else mat, 2, scale=(1.0, 0.9, 0.7))
        mb.ico(r * 0.72, (c[0], c[1], c[2] - r * fl * 0.5), "Leaf_OP", 1, scale=(1.0, 0.8, fl * 0.7))
    col_box("OP_TreeTrunk", (16.0, 16.0, 26.0), (bx, by, CC + 13.0))
    mb.finish()


# ------------------------------------------------------------------ summon: a TORRE AMS aprovada (Ilha 1) + terraco Wano
SUMMON_ALIAS = {
    "Summon_Stone": "Stone_OP_Dark", "Stone_SumBlock": "Stone_OP", "Summon_Stone_Dark": "Stone_OP_Dark",
    "Stone_Wall_Light": "Stone_OP", "Stone_SumFloor_Pale": "Stone_OP_Path", "Summon_Floor": "Stone_OP_Dark",
    "Stone_Paving_Warm": "Stone_OP_Path", "Cloth_Royal_Blue": "Cloth_OP_Indigo", "Wood_Dark": "Wood_OP_Dark",
}
_TOWER = None


def tower_mod():
    """importa il_summon com a planta DESTA ilha (valores do il_layout trocados so durante o import, como na DS)"""
    global _TOWER
    if _TOWER is not None:
        return _TOWER
    import sys, importlib
    import il_layout as NL
    want = {"SUMMON_TOWER": L.SUMMON_TOWER, "SUMMON_FACE_DEG": L.SUMMON_FACE_DEG, "T1": T1, "SUMMON_C": L.SUMMON_C,
            "SUMMON_R": L.SUMMON_R}
    saved = {k: getattr(NL, k) for k in want}
    for k, v in want.items():
        setattr(NL, k, v)
    try:
        if "il_summon" in sys.modules:
            T = importlib.reload(sys.modules["il_summon"])
        else:
            T = importlib.import_module("il_summon")
    finally:
        for k, v in saved.items():
            setattr(NL, k, v)
    assert abs(T.Z0 - T1) < 1e-6 and abs(T.TX - L.SUMMON_TOWER[0]) < 1e-6 and abs(T.TY - L.SUMMON_TOWER[1]) < 1e-6
    _TOWER = T
    return T


def build_tower():
    """estrela + aneis + torre + nucleo SEM redesenho (codigo da Ilha 1); so pedra/tecido/madeira trocados por apelido"""
    import bpy
    T = tower_mod()
    before = {o.name for o in bpy.data.objects}
    saved = dict(fm_lib.MAT_ALIAS)
    for k, v in SUMMON_ALIAS.items():
        fm_lib.MAT_ALIAS[k] = v
        fam = fm_lib.FAMILIES.get(k)
        if fam:
            for n, _ in fam[1]:
                fm_lib.MAT_ALIAS[n] = v
    try:
        stone = MB("SUM_Tower_Stone", "06_SUMMON", random.Random(620), detail="near")
        gold = MB("SUM_Tower_Gold", "06_SUMMON", random.Random(622), detail="near")
        glow = MB("SUM_Tower_Glow", "06_SUMMON", random.Random(623), detail="hero")
        T.tower_stone(stone, gold, glow)
        cr = T.tower_details(stone, gold, glow)
        cr.bm.free()
        T.masts_and_lanterns(stone, gold, glow)
        c = T.sphere(gold, glow)
        stone.finish()
        gold.finish()
        glow.finish()
        T.tower_collision()
    finally:
        fm_lib.MAT_ALIAS.clear()
        fm_lib.MAT_ALIAS.update(saved)
    dst = fm_lib.coll("06_SUMMON")
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_OPSUM_" + n[len("VFX_SUM_"):]
            ob["vfx_zone"] = "summon"
        elif n.startswith("SUM_"):
            ob.name = "OP_Sum_" + n[len("SUM_"):]
        elif n.startswith("COL_Summon"):
            ob.name = "COL_OPSum" + n[len("COL_Summon"):]
        if ob.type == "MESH":
            ob.data.name = ob.name
        if not n.startswith(("COL_", "VFX_")):
            for cl in list(ob.users_collection):
                if cl.name == "05_SUMMON":
                    cl.objects.unlink(ob)
                    if ob.name not in dst.objects:
                        dst.objects.link(ob)
    c05 = bpy.data.collections.get("05_SUMMON")
    if c05 is not None and not c05.objects and not c05.children:
        bpy.data.collections.remove(c05)
    return T, c


def summon():
    rng = random.Random(71)
    mb = MB("OP_Sum_Blockout", "06_SUMMON", rng, detail="far", floor=None)
    DL.plan_stair(mb, "Summon", side_floor=T1)
    # pavimento do terraco em volta da torre (laje clara) + guarda-corpo vermelho baixo nas bordas que dao para o porto
    tx, ty = L.SUMMON_TOWER
    mb.prism(ccw(L.circle_poly((tx - 4.0, ty), 30.0, 15.0)), T1 - 0.2, T1 + 0.12, "Stone_OP_Path")
    DL.vis_fence(mb, [(204.5, 172.0, T1), (204.5, 226.0, T1)], h=3.0, post_step=4.0, m="Wood_OP_Lacquer",
                 rail_m="Wood_OP_Lacquer")
    DL.vis_fence(mb, [(150.0, 150.6, T1), (203.0, 150.6, T1)], h=3.0, post_step=4.0, m="Wood_OP_Lacquer",
                 rail_m="Wood_OP_Lacquer")
    for i, (x, y) in enumerate(((132.0, 196.0), (132.0, 236.0))):
        toro(mb, x, y, T1, 0.9, "L_OPSum_Toro_%d" % i)
    mb.finish()
    T, c = build_tower()
    light("L_OPSum_Core", "POINT", (L.SUMMON_TOWER[0] - 1.5, L.SUMMON_TOWER[1], T1 + 9.0), 1600.0, (0.36, 0.52, 1.0), 1.0)
    light("L_OPSum_Star", "POINT", tuple(c), 3000.0, (1.0, 0.74, 0.34), 2.0)


# ------------------------------------------------------------------ porto: cais, rua alta, pier, palafita, armazens
def harbor():
    rng = random.Random(81)
    mb = MB("OP_Port_Blockout", "16_HARBOR", rng, detail="far", floor=None)
    # muro de cais (pedra) na borda da agua + defensas e cabecos; pier e palafita em estacas de madeira
    DL.wall_ribbon(mb, [(222.5, 76.0), (222.5, 110.0)], L.SEA - 2.0, L.HARBOR, 1.2, "Stone_OP", side=-1.0)
    DL.wall_ribbon(mb, [(222.5, 200.0), (222.5, 262.0)], L.SEA - 2.0, L.HARBOR, 1.2, "Stone_OP", side=-1.0)
    for x0, y0, x1, y1 in ((222.0, 110.0, 234.0, 200.0), (222.0, 40.0, 246.0, 76.0)):
        x = x0 + 1.5
        while x < x1:
            y = y0 + 1.5
            while y < y1:
                mb.cyl(0.55, L.HARBOR - (L.SEA - 4.0), (x, y, (L.HARBOR + L.SEA - 4.0) / 2 - 0.4), m="Wood_OP_Dark", n=6,
                       bevel=0.0)
                y += 9.0
            x += 9.0 if x1 - x0 > 14 else (x1 - x0 - 3.0)
    for y in range(116, 200, 14):
        mb.cyl(0.8, 1.6, (233.0, float(y), L.HARBOR + 0.8), m="Metal_OP_Iron", n=8, bevel=0.0)       # cabecos
        mb.box((0.6, 3.0, 2.0), (234.4, float(y) + 7.0, L.HARBOR - 1.0), (0, 0, 0), "Wood_OP_Mid", 0.0)  # defensas
    DL.vis_fence(mb, [(246.0, 40.6, L.HARBOR), (246.0, 75.4, L.HARBOR)], h=3.0, m="Wood_OP_Lacquer", rail_m="Wood_OP_Lacquer")
    for nm in ("PortoA", "PortoB"):
        DL.plan_stair(mb, nm)
    for spec in L.BUILDINGS:
        if spec[0].startswith("H"):
            house(mb, spec, area="OP_PortHouse")
    # barcos pequenos atracados (silhueta)
    for x, y, a in ((262.0, 70.0, 0.3), (270.0, 210.0, -0.2)):
        mb.box((4.0, 12.0, 1.6), (x, y, L.SEA + 0.6), (0, 0, a), "Wood_OP_Hull", 0.0)
    for i, (x, y, z) in enumerate(((214.0, 34.0, L.HARBOR), (204.0, 104.0, L.HMID), (226.0, 196.0, L.HARBOR))):
        lantern_post(mb, x, y, z, 6.5, "L_OPProp_Lamp_Porto_%d" % i, 120.0)
    mb.finish()


# ------------------------------------------------------------------ navio (marco cenografico, convés acessivel)
def ship():
    rng = random.Random(83)
    mb = MB("OP_Ship_Blockout", "16_HARBOR", rng, detail="far", floor=None)
    sx, sy = L.SHIP_C
    deck = L.SHIP
    y_bow, y_stern = sy - L.SHIP_LEN / 2, sy + L.SHIP_LEN / 2
    # casco: secoes em U ao longo do comprimento (afina na proa, popa larga e alta), costado com tosamento
    secs = []
    n = 14
    for i in range(n + 1):
        t = i / n                                     # 0 = proa, 1 = popa
        y = y_bow + (y_stern - y_bow) * t
        half = L.SHIP_BEAM / 2 * (math.sin(min(1.0, t * 1.6) * math.pi / 2) ** 0.8) * (0.92 if t > 0.9 else 1.0)
        half = max(half, 0.6)
        sheer = deck + 1.4 + 3.2 * (1 - t) ** 3 + 4.0 * max(0.0, t - 0.78) * 4.0
        keel = deck - 12.5 + 4.0 * (1 - t) ** 4
        secs.append((y, half, sheer, keel))
    prof = lambda h, top, kz: [(-h, top), (-h * 1.02, (top + kz) / 2 + 1.5), (-h * 0.7, kz + 2.0), (0.0, kz),
                               (h * 0.7, kz + 2.0), (h * 1.02, (top + kz) / 2 + 1.5), (h, top)]
    rings = []
    for y, h, top, kz in secs:
        rings.append([mb.bm.verts.new((sx + u, y, z)) for u, z in prof(h, top, kz)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(len(r0) - 1):
            mb.bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
    for r in (rings[0], rings[-1]):
        try:
            mb.bm.faces.new(r)
        except ValueError:
            pass
    mb._post([v for r in rings for v in r], "Wood_OP_Hull", None, 0, 1)
    # convés (tabuas) e faixa vermelha no costado
    mb.prism(ccw(L.SHIP_DECK), deck - 0.6, deck, "Wood_OP_Mid")
    for s in (-1, 1):
        mb.box((0.4, L.SHIP_LEN * 0.8, 0.9), (sx + s * (L.SHIP_BEAM / 2 + 0.2), sy + 4.0, deck + 1.0), (0, 0, 0),
               "Wood_OP_Lacquer", 0.0)
    # castelo de popa (cabine com janelas) e proa com gurupes
    mb.box((L.SHIP_BEAM - 2.0, 10.0, 6.0), (sx, y_stern - 6.0, deck + 3.0), (0, 0, 0), "Wood_OP_Hull", 0.0)
    mb.box((L.SHIP_BEAM - 1.0, 11.0, 0.6), (sx, y_stern - 6.0, deck + 6.3), (0, 0, 0), "Wood_OP_Mid", 0.0)
    for u in (-4.0, 0.0, 4.0):
        mb.box((2.0, 0.3, 1.6), (sx + u, y_stern - 11.1, deck + 3.4), (0, 0, 0), "Window_OP_Warm", 0.0)
    col_box("OP_ShipCabin", (L.SHIP_BEAM - 2.0, 10.0, 6.0), (sx, y_stern - 6.0, deck + 3.0))
    mb.cyl(0.7, 20.0, (sx, y_bow - 6.0, deck + 7.0), (math.radians(-62), 0, 0), m="Wood_OP_Dark", n=8, bevel=0.0)
    # mastros, vergas e velas (velas em 2 panos levemente curvos, apoiadas nas vergas)
    for my, h, sw in ((sy - 16.0, 44.0, 30.0), (sy + 10.0, 52.0, 36.0)):
        mb.cyl(0.9, h, (sx, my, deck + h / 2), m="Wood_OP_Dark", n=10, r2=0.6, bevel=0.0)
        col_box("OP_ShipMast", (2.0, 2.0, 8.0), (sx, my, deck + 4.0))
        for k, (zz, fw) in enumerate(((deck + h * 0.42, 1.0), (deck + h * 0.78, 0.8))):
            mb.cyl(0.45, sw * fw, (sx, my, zz), (0, math.pi / 2, 0), m="Wood_OP_Dark", n=6, bevel=0.0)
            sh = h * 0.34 if k == 0 else h * 0.28
            for j in range(2):
                mb.box((sw * fw * 0.92, 0.3, sh / 2), (sx, my - 0.6 - 0.5 * j, zz - sh / 4 - j * sh / 2),
                       (0.12 + 0.1 * j, 0, 0), "Cloth_OP_Sail", 0.0)
        mb.box((3.0, 0.2, 2.0), (sx + 1.6, my, deck + h + 1.0), (0, 0, 0), "Cloth_OP_Red", 0.0)        # flamula
    # prancha (gangway) do pier ao convés com corrimao
    a, b = (230.0, 152.0, L.HARBOR), (241.6, 152.0, deck)
    ln = math.dist(a, b)
    c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
    pitch = math.atan2(b[2] - a[2], b[0] - a[0])
    mb.box((ln, 5.0, 0.4), c, (0, -pitch, 0), "Wood_OP_Mid", 0.0)
    for s in (-1, 1):
        mb.box((ln, 0.3, 0.3), (c[0], c[1] + s * 2.6, c[2] + 3.2), (0, -pitch, 0), "Wood_OP_Dark", 0.0)
    mb.finish()


# ------------------------------------------------------------------ agua: SO a pedra estanque (a agua e do Roblox)
def water():
    rng = random.Random(88)
    mb = MB("OP_Water_Stone", "07_WATER", rng, detail="far", floor=-999)
    B = ccw(L.BASIN)
    DL.wall_ribbon(mb, B + [B[0]], L.BASIN_Z - 1.6, CF + 0.5, 1.0, "Stone_OP", side=-1.0)
    for pts, w in ((L.CANAL_E, 6.0), (L.CANAL_W, 8.0)):
        xy = [(p[0], p[1]) for p in pts]
        off = L.ribbon(xy, w / 2)
        n = len(xy)
        for s, side in ((1.0, off[:n]), (-1.0, list(reversed(off[n:])))):
            for (a, za), (b, zb) in zip(zip(side, [p[2] for p in pts]), zip(side[1:], [p[2] for p in pts[1:]])):
                zt = max(za, zb) + 1.1
                DL.wall_ribbon(mb, [a, b], min(za, zb) - 1.8, zt, 0.8, "Stone_OP", side=s)
    # roda d'agua (peca movel VFX_OP_Wheel): aros, raios e pas; eixo leste-oeste entrando no moinho
    wx, wy, wd, ww = L.WHEEL
    zc = L.WHEEL_AXLE_Z
    mw = MB("VFX_OP_Wheel", "12_VFX_HELPERS", rng, detail="far", floor=-999)
    R = wd / 2
    n = 14
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        for xo in (-ww / 2 + 0.3, ww / 2 - 0.3):
            ch = 2 * R * math.sin(math.pi / n) + 0.1
            mw.box((0.5, ch, 0.8), (wx + xo, wy + (R - 0.4) * math.cos(a), zc + (R - 0.4) * math.sin(a)), (a, 0, 0),
                   "Wood_OP_Dark", 0.0)
        mw.box((ww - 0.2, 0.3, 1.6), (wx, wy + (R - 0.5) * math.cos(a), zc + (R - 0.5) * math.sin(a)), (a, 0, 0),
               "Wood_OP_Mid", 0.0)
    for k in range(4):
        a = math.pi * k / 4
        for xo in (-ww / 2 + 0.3, ww / 2 - 0.3):
            mw.box((0.4, 2 * R - 1.0, 0.5), (wx + xo, wy, zc), (a, 0, 0), "Wood_OP_Dark", 0.0)
    mw.cyl(0.7, ww + 1.0, (wx, wy, zc), (0, math.pi / 2, 0), m="Metal_OP_Iron", n=8, bevel=0.0)
    ob = mw.finish()
    ob["pivot"] = (wx, wy, zc)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = 3.0
    ob["vfx_zone"] = "canal"
    mb.cyl(0.5, 10.0, (wx + 6.0, wy, zc), (0, math.pi / 2, 0), m="Metal_OP_Iron", n=8, bevel=0.0)
    mb.finish()
    # PREVIA da agua (00_REFERENCE: fora do export) para ler a composicao nos renders do blockout
    pw = MB("PREVIEW_Water", "00_REFERENCE", rng, detail="far", floor=-999)
    pw.prism(B, L.BASIN_Z - 0.8, L.BASIN_Z, "PREVIEW_Sea")
    for pts, w in ((L.CANAL_E, 5.0), (L.CANAL_W, 7.0)):
        for a, b in zip(pts, pts[1:]):
            pw.prism(ccw(L.ribbon([a[:2], b[:2]], w / 2)), min(a[2], b[2]) - 0.6, min(a[2], b[2]), "PREVIEW_Sea")
    for (x, y, zt, zb), dirv, wd in ((L.CASTLE_FALL, (0.0, -1.0), 7.0), (L.FALL_E, (0.55, 0.0), 6.0),
                                     (L.FALL_W, (0.0, -1.0), 7.0)):
        pw.box((wd if dirv[0] == 0 else 1.0, 1.0 if dirv[0] == 0 else wd, zt - zb), (x + dirv[0] * 1.2, y + dirv[1] * 1.2,
               (zt + zb) / 2), (0, 0, 0), "PREVIEW_Falls", 0.0)
    for (nm, (x, y, zt, zb)) in L.WEIRS:
        pw.box((6.0, 1.0, zt - zb), (x, y, (zt + zb) / 2), (0, 0, 0 if nm == "Weir_W" else math.pi / 2), "PREVIEW_Falls", 0.0)
    pw.finish()


# ------------------------------------------------------------------ saida: ponte vermelha, promontorio, guarda
def exit_():
    rng = random.Random(111)
    mb = MB("OP_Exit_Blockout", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    ux, uy = L.exit_dir()
    ang = math.atan2(uy, ux)
    Ln = L.EXIT_BRIDGE_LEN
    c = L.exit_point(Ln / 2)
    mb.box((Ln + 1.0, L.EXIT_W, 1.2), (c[0], c[1], T1 - 0.6), (0, 0, ang), "Wood_OP_Dark", 0.0)
    for s in (-1, 1):
        q = L.exit_point(Ln / 2, s * (L.EXIT_W / 2 + 0.4))
        mb.box((Ln + 1.0, 1.0, 1.6), (q[0], q[1], T1 - 0.5), (0, 0, ang), "Wood_OP_Lacquer", 0.0)
        mb.box((Ln + 1.0, 0.6, 0.55), (q[0], q[1], T1 + 3.6), (0, 0, ang), "Wood_OP_Lacquer", 0.0)
        for k in range(0, int(Ln) + 1, 6):
            p = L.exit_point(float(k), s * (L.EXIT_W / 2 + 0.4))
            mb.box((0.7, 0.7, 3.9), (p[0], p[1], T1 + 1.95), (0, 0, ang), "Wood_OP_Lacquer", 0.0)
            mb.box((0.9, 0.9, 0.5), (p[0], p[1], T1 + 4.1), (0, 0, ang), "Metal_OP_Gold", 0.0)
    # arco vermelho por baixo do tabuleiro (le como a ponte arqueada da concept, sem rampa no piso) + 2 pilares
    arc = []
    for i in range(13):
        t = i / 12
        d = Ln * (0.08 + 0.84 * t)
        p = L.exit_point(d)
        arc.append((p[0], p[1], T1 - 2.0 - 14.0 * (1 - math.sin(math.pi * t))))
    for s in (-1, 1):
        sh = [(x - uy * s * (L.EXIT_W / 2 - 1.0), y + ux * s * (L.EXIT_W / 2 - 1.0), z) for x, y, z in arc]
        mb.sweep(sh, [(-0.8, -0.8), (0.8, -0.8), (0.8, 0.8), (-0.8, 0.8)], m="Wood_OP_Lacquer")
    for d in (Ln * 0.08, Ln * 0.92):
        p = L.exit_point(d)
        mb.cyl(3.2, T1 - 16.0 - 10.0, (p[0], p[1], (T1 - 16.0 + 10.0) / 2), m="Stone_OP", n=8, r2=2.4, bevel=0.0)
    # promontorio: laje do caminho e lanternas
    hp = L.headland_poly()
    mb.prism(ccw(L.ribbon([L.exit_point(Ln), L.exit_point(Ln + L.ANCHOR_OPM_OFF)], 6.0)), T1 - 0.2, T1 + 0.12, "Stone_OP_Path")
    for i, v in enumerate((-12.0, 12.0)):
        p = L.exit_point(Ln + 6.0, v)
        lantern_post(mb, p[0], p[1], T1, 6.5, "L_OPProp_Lamp_Saida_%d" % i, 120.0)
    del hp
    mb.finish()
    mg = MB("OP_Exit_AnchorGuard", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    ap = L.anchor_opm_pos()
    for s in (-1, 1):
        p = (ap[0] - ux * 1.0 - uy * s * (L.EXIT_W / 2 + 0.6), ap[1] - uy * 1.0 + ux * s * (L.EXIT_W / 2 + 0.6))
        mg.box((1.2, 1.2, 3.4), (p[0], p[1], T1 + 1.7), (0, 0, ang), "Stone_OP_Dark", 0.0)
    q = (ap[0] - ux * 1.0, ap[1] - uy * 1.0)
    mg.box((0.3, L.EXIT_W + 1.2, 0.3), (q[0], q[1], T1 + 2.6), (0, 0, ang), "Wood_OP_Mid", 0.0)
    ob = mg.finish()
    ob["next_island_guard"] = True


# ------------------------------------------------------------------ marcos secundarios (silhueta, custo proporcional)
def landmarks():
    rng = random.Random(131)
    mb = MB("OP_Lmk_Blockout", "17_LANDMARKS", rng, detail="far", floor=-999)
    # CAVEIRA COM CHIFRES: formacao na ponta sul do promontorio, rosto para a enseada/praca; a rocha sobe do mar
    sx, sy = L.SKULL_C
    # pedestal de rocha em camadas que ESTREITAM para cima e abraçam o queixo e a nuca (formacao, nao mascara colada)
    DL.prism(mb, L.SKULL_ROCK, L.BASE, 80.0, "Cliff_OP_Dark")
    cpx, cpy = DL.centroid(L.SKULL_ROCK)
    DL.prism(mb, DL.scale_poly(L.SKULL_ROCK, 0.86, (cpx, cpy)), 80.0, 92.0, "Cliff_OP_Dark", top_m="Cliff_OP_Moss")
    for k, (du, dv, r, zt) in enumerate(((-20.0, -6.0, 9.0, 104.0), (20.0, -6.0, 9.0, 102.0), (0.0, -16.0, 14.0, 118.0),
                                          (-14.0, -18.0, 8.0, 110.0), (16.0, -16.0, 8.0, 108.0))):
        a_ = math.radians(L.SKULL_FACE_DEG)
        fx_, fy_ = math.cos(a_), math.sin(a_)
        x_, y_ = sx + fy_ * du + fx_ * dv, sy - fx_ * du + fy_ * dv
        DL.prism(mb, DL.blob_poly(x_, y_, r, 9, rng, 0.18), 88.0, zt, "Cliff_OP_Dark", top_m="Cliff_OP_Moss")
    a = math.radians(L.SKULL_FACE_DEG)
    F = Frame(sx, sy, 0.0, a - math.pi / 2)              # +y local = rosto
    mb.ico(25.0, F.p(0, 0, 118.0), "Cliff_OP_Dark", 2, scale=(1.0, 0.92, 0.9), rot=(0, 0, F.a), jitter=0.05)   # cranio
    mb.ico(16.0, F.p(0, 10.0, 102.0), "Cliff_OP_Dark", 2, scale=(1.15, 0.8, 0.9), rot=(0, 0, F.a))            # maxilar
    for s in (-1, 1):
        mb.ico(7.0, F.p(s * 9.5, 18.5, 116.0), "Cliff_OP_Void", 1, scale=(1.0, 0.6, 0.85), rot=(0, 0, F.a))    # orbitas
        mb.ico(6.0, F.p(s * 15.0, 15.0, 106.0), "Cliff_OP_Dark", 1, scale=(1.0, 0.8, 0.7), rot=(0, 0, F.a))   # macas
    mb.cyl(3.2, 5.0, F.p(0, 21.0, 107.0), (math.pi / 2, 0, F.a), m="Cliff_OP_Void", n=3, r2=0.4, bevel=0.0)    # nariz
    for k in range(6):
        u = -10.0 + k * 4.0
        mb.box((3.0, 2.4, 4.6), F.p(u, 22.0 - abs(u) * 0.22, 95.0), F.r(), "Plaster_OP_Warm", 0.0)            # dentes
    mb.box((24.0, 5.0, 2.4), F.p(0, 19.0, 92.4), F.r(), "Cliff_OP_Void", 0.0)                                  # boca
    for s in (-1, 1):                                                                                         # chifres
        pts = [(s * 18.0, 0.0, 126.0, 5.2), (s * 26.0, -2.0, 136.0, 4.0), (s * 30.0, -4.0, 148.0, 2.8),
               (s * 28.0, -5.0, 160.0, 1.6), (s * 23.0, -5.0, 168.0, 0.5)]
        loft(mb, [(F.p(x, y, z).x, F.p(x, y, z).y, z, r) for x, y, z, r in catmull(pts, 3)], "Cliff_OP_Horn", n=8, flat=1.0)
    # ESPADA MONUMENTAL distante, cravada no pinaculo do esporao NE (rigida: lamina, ponta enterrada, guarda, cabo, pomo)
    # esporao: cadeia de rochedos de alturas dirigidas (nao uma passarela plana) ate o pinaculo da espada
    for t, r, zt in ((0.0, 20.0, 96.0), (0.18, 15.0, 74.0), (0.34, 13.0, 58.0), (0.5, 12.0, 66.0), (0.66, 11.0, 54.0),
                     (0.82, 13.0, 70.0)):
        x_, y_ = 190.0 + (L.SWORD_POS[0] - 190.0) * t, 478.0 + (L.SWORD_POS[1] - 478.0) * t
        DL.prism(mb, DL.blob_poly(x_, y_, r, 9, rng, 0.2), 30.0, zt - 5.0, "Cliff_OP")
        DL.prism(mb, DL.blob_poly(x_, y_, r * 0.72, 8, rng, 0.2), zt - 5.0, zt, "Cliff_OP", top_m="Cliff_OP_Moss")
    wx, wy = L.SWORD_POS
    DL.prism(mb, DL.blob_poly(wx, wy, 16.0, 9, rng, 0.15), 30.0, L.SWORD_ROCK_Z - 30.0, "Cliff_OP")
    DL.prism(mb, DL.blob_poly(wx, wy, 11.0, 8, rng, 0.15), L.SWORD_ROCK_Z - 30.0, L.SWORD_ROCK_Z, "Cliff_OP_Dark")
    Fs = Frame(wx, wy, L.SWORD_ROCK_Z, math.radians(30.0))
    tilt = 0.08
    ax = lambda h: Fs.p(0.0, -math.sin(tilt) * h, -6.0 + math.cos(tilt) * h)      # ponto no eixo inclinado
    mb.box((12.0, 2.2, 86.0), ax(43.0), Fs.r(tilt, 0, 0), "Metal_OP_Steel", 0.0)                      # lamina
    mb.box((1.6, 2.6, 82.0), ax(43.0), Fs.r(tilt, 0, 0), "Metal_OP_Iron", 0.0)                        # nervura
    mb.box((34.0, 4.4, 4.6), ax(88.3), Fs.r(tilt, 0, 0), "Metal_OP_Gold", 0.0)                        # guarda
    mb.cyl(2.6, 26.0, ax(103.6), (tilt, 0, Fs.a), m="Cloth_OP_Red", n=8, bevel=0.0)                   # cabo
    mb.ico(4.2, ax(118.4), "Metal_OP_Gold", 1)                                                       # pomo
    # PAGODE de 5 andares no pinaculo oeste (cenografico)
    px, py, pr, ptop = L.WEST_SPIRE
    DL.prism(mb, DL.blob_poly(px, py, pr, 10, rng, 0.14), 30.0, ptop - 26.0, "Cliff_OP")
    DL.prism(mb, DL.blob_poly(px, py, pr * 0.8, 9, rng, 0.14), ptop - 26.0, ptop, "Cliff_OP", top_m="Cliff_OP_Moss")
    Fp = Frame(px, py, ptop, 0.0)
    z = 0.0
    for k in range(5):
        w = 12.0 - k * 1.6
        mb.box((w, w, 4.2), Fp.p(0, 0, z + 2.1), Fp.r(), "Wood_OP_Lacquer", 0.0)
        frustum(mb, Fp, w + 6.0, w + 6.0, z + 4.4, w - 1.0, w - 1.0, z + 6.0, "Roof_OP_Blue", 0.5)
        z += 6.2
    mb.cyl(0.4, 8.0, Fp.p(0, 0, z + 4.0), m="Metal_OP_Gold", n=6, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ vestir (PROXIES leves de composicao)
def dressing():
    rng = random.Random(121)
    mv = MB("OP_Veg_Blockout", "10_VEGETATION", rng, detail="far", floor=-999)
    # cerejeiras = ACENTO e enquadramento (nao enchimento): entrada, recanto da rua, terraco alto, santuario, summon,
    # porto, promontorio, bairro do canal
    for x, y, z in ((-36.0, 14.0, 90.0), (38.0, 16.0, 90.0), (-36.0, 91.0, T1), (-180.0, 380.0, L.W3),
                    (-150.0, 420.0, L.W3), (126.0, 318.0, P), (196.0, 182.0, T1), (300.0, 290.0, T1),
                    (-138.0, 50.0, T1), (60.0, 30.0, 86.0)):
        cherry(mv, x, y, z, 11.0, 6.5, col=L.zone_of(x, y) is not None)
    # pinheiros nas bordas de falesia e no fundo (verde que segura a silhueta)
    for x, y, z, h in ((-44.0, 20.0, 90.0, 12.0), (48.0, 26.0, 90.0, 11.0), (100.0, 28.0, 86.0, 12.0),
                       (-196.0, 96.0, 90.0, 12.0), (-90.0, 440.0, 134.0, 14.0), (-20.0, 486.0, 134.0, 16.0),
                       (40.0, 484.0, 134.0, 15.0), (150.0, 440.0, 120.0, 16.0), (196.0, 400.0, 120.0, 14.0),
                       (246.0, 340.0, 104.0, 13.0), (276.0, 330.0, 104.0, 12.0), (-60.0, 340.0, 101.0, 10.0),
                       (130.0, 356.0, 104.0, 11.0), (-208.0, 320.0, 100.2, 12.0), (-214.0, 181.0, P, 11.0)):
        pine(mv, x, y, z, h, col=L.zone_of(x, y) is not None)
    # arbustos baixos nos ombros e pes de muro (manchas, nada no meio de caminho)
    for x, y, z, r in ((-30.0, 30.0, 90.0, 3.0), (30.0, 30.0, 90.0, 3.0), (80.0, 30.0, 86.0, 3.6), (-60.0, 344.0, 101.0, 3.0),
                       (160.0, 356.0, 104.0, 3.4), (-192.0, 110.0, 90.0, 3.0), (110.0, 26.0, 86.0, 3.0)):
        mv.ico(r, (x, y, z + r * 0.4), "Leaf_OP", 1, scale=(1.3, 1.1, 0.7))
    mv.finish()


def build(skip=(), ore_proxies=False):
    DETAILED.clear()
    DETAILED.update(skip)
    fns = {"terrain": terrain, "entry": entry, "capital": capital, "plaza": lambda: plaza(ore_proxies),
           "castle": castle, "tree": tree_monument, "summon": summon, "harbor": harbor, "ship": ship, "water": water,
           "exit": exit_, "landmarks": landmarks, "dressing": dressing}
    for z in ZONES:
        if z not in skip:
            fns[z]()
