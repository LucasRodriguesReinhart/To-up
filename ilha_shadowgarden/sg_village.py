# sg_village - VILA da Ilha 3 (Shadow Garden): praca central + fonte, ruas com meio-fio, escada P1->P2 (so visual),
# 11 casas gothicas de meia-enxaimel (NAO entraveis: sem porta nenhuma), poucos postes de ferro no eixo e na rua da
# praca. So ambientacao (o ultimo na hierarquia): poucas pecas, cada uma com funcao de leitura.
# Substitui sg_blockout.village. Colisao propria: corpo de cada casa (caixa), torreao, postes. O piso, a escada, a
# bacia da fonte e as guardas sao do sg_col (congelado).
import math, random
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, Frame, light, octo_col, fm_lib
import sg_layout as L

P1, P2, P3 = L.P1, L.P2, L.P3
COLL = "05_VILLAGE"
WIN = "Window_Warm"
WOOD = "Wood_SG_Dark"
STONE = "Stone_SG_Block"
TRIM = "Stone_SG_Trim"
ROOF = "Roof_SG_Slate"
IRON = "Metal_SG_Iron"
# materiais novos da vila (3 de 5)
M_PL = "Plaster_SGVil"          # reboco apagado (frio-quente, escuro): o Plaster_SG claro demais vira "casa de conto clara"
M_COB = "Stone_SGVilCobble"     # calcamento escuro (desenho radial da praca, faixas das ruas)
M_SHUT = "Wood_SGVilNavy"       # persianas / postigos pintados de navy
fm_lib.MATS.setdefault(M_PL, (fm_lib.S(96, 88, 88), 0.8, 0.0, 0, None, 0.06))
fm_lib.MATS.setdefault(M_COB, (fm_lib.S(72, 76, 92), 0.9, 0.0, 0, None, 0.10))
fm_lib.MATS.setdefault(M_SHUT, (fm_lib.S(36, 42, 72), 0.75, 0.0, 0, None, 0.05))

CAMS = {
    # 360 da vila (frente, tras, lados) + altura do jogador nas ruas do P1 e do P2
    "CAM_SGVil_Front": ((0.0, -196.0, P1 + 34.0), (0.0, -108.0, P1 + 2.0), 22),
    "CAM_SGVil_Back": ((0.0, -4.0, P3 + 30.0), (0.0, -96.0, P1 + 2.0), 22),
    "CAM_SGVil_SideW": ((-150.0, -96.0, P2 + 26.0), (-40.0, -100.0, P1 + 4.0), 22),
    "CAM_SGVil_SideE": ((160.0, -110.0, P2 + 26.0), (40.0, -100.0, P1 + 4.0), 22),
    "CAM_SGVil_P1W_Back": ((-66.0, -186.0, P1 + 16.0), (-62.0, -128.0, P1 + 6.0), 22),
    "CAM_SGVil_P1E_Back": ((70.0, -186.0, P1 + 16.0), (66.0, -128.0, P1 + 6.0), 22),
    "CAM_SGVil_P2_Back": ((-24.0, -14.0, P2 + 20.0), (-62.0, -52.0, P2 + 5.0), 20),
    "CAM_SGVil_P2E_Back": ((24.0, -14.0, P2 + 20.0), (44.0, -56.0, P2 + 5.0), 20),
    "CAM_SGVil_Turret": ((28.0, -124.0, P1 + 7.0), (50.0, -140.0, P1 + 11.0), 22),
    "CAM_SGVil_Shop": ((-38.0, -126.0, P1 + 5.2), (-52.0, -141.0, P1 + 6.0), 22),
    "CAM_SGVil_Fountain": ((12.0, -146.0, P1 + 7.0), (0.0, -128.0, P1 + 4.0), 24),
    "CAM_SGVil_PH_P1W": ((-22.0, -119.0, P1 + 5.2), (-100.0, -121.0, P1 + 7.0), 22),
    "CAM_SGVil_PH_P1E": ((22.0, -119.0, P1 + 5.2), (100.0, -118.0, P1 + 7.0), 22),
    "CAM_SGVil_PH_Stair": ((0.0, -114.0, P1 + 5.2), (0.0, -40.0, P2 + 9.0), 22),
    "CAM_SGVil_PH_P2E": ((-104.0, -45.0, P2 + 5.2), (40.0, -46.0, P2 + 6.0), 22),
    "CAM_SGVil_PH_P2Craft": ((6.0, -46.0, P2 + 5.2), (76.0, -56.0, P2 + 6.0), 22),
}

# rotas extras: as ruas da vila tem que continuar livres (nada da vila no caminho)
EXTRA_ROUTES = {
    "VIL_RUA_P1_OESTE": ([(-20.0, -118.0), (-60.0, -120.0), (-98.0, -118.0)], P1),
    "VIL_RUA_P1_LESTE": ([(20.0, -118.0), (64.0, -120.0), (108.0, -116.0)], P1),
    "VIL_RUA_P2": ([(-108.0, -45.0), (-40.0, -44.0), (0.0, -45.0), (60.0, -45.0), (70.0, -56.0), (75.0, -60.0)], P2),
    "VIL_EIXO_P2": ([(0.0, -81.0), (0.0, -60.0), (0.0, -30.0)], P2),
    "VIL_PRACA_ANEL": ([(L.PLAZA_C[0] + 12.0 * math.cos(math.radians(a)), L.PLAZA_C[1] + 12.0 * math.sin(math.radians(a)))
                        for a in range(-90, 271, 45)], P1),
}
# a ponta oeste da rua do P2 (mirante sobre a cachoeira) tem guarda
EXTRA_PROBES = [("VIL_P2_mirante_oeste", -112.0, -45.0, P2, -1.0, 0.0, 10.0)]


# ------------------------------------------------------------------ utilidades
def ring_prism(mb, c, r0, r1, n, z0, z1, m, rot0=0.0):
    """anel poligonal (n lados, vertices em rot0 + k*360/n) de r0 a r1, de z0 a z1"""
    bm = mb.bm
    cx, cy = c
    ang = [math.radians(rot0) + 2 * math.pi * k / n for k in range(n)]
    ob = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z0)) for a in ang]
    ot = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)) for a in ang]
    ib = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)) for a in ang]
    it = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z1)) for a in ang]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((it[i], it[j], ib[j], ib[i]))
        bm.faces.new((ot[i], ot[j], it[j], it[i]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    mb._post(ob + ot + ib + it, m, None, 0, 1)


def ngon(c, r, n, rot0=0.0):
    return [(c[0] + r * math.cos(math.radians(rot0) + 2 * math.pi * k / n),
             c[1] + r * math.sin(math.radians(rot0) + 2 * math.pi * k / n)) for k in range(n)]


def tri_slab(mb, pts, nvec, th, m):
    """triangulo (3 pontos mundo no plano de fora) extrudado para dentro (-nvec) com espessura th"""
    bm = mb.bm
    a = [bm.verts.new(Vector(p)) for p in pts]
    b = [bm.verts.new(Vector(p) - nvec * th) for p in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


def poly_slab(mb, pts2, plane, th, m):
    """poligono 2D (u, v) num plano vertical: plane = (origem, eixo_u, eixo_v, normal) mundo; extruda -normal"""
    o, eu, ev, nv = plane
    bm = mb.bm
    a = [bm.verts.new(o + eu * u + ev * v) for u, v in pts2]
    b = [bm.verts.new(o + eu * u + ev * v - nv * th) for u, v in pts2]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    n = len(pts2)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


class Face:
    """face de parede no referencial G da casa: centro c (2D local), tangente u, normal n = rot90(u) para fora"""

    def __init__(self, G, c, u, length):
        self.G, self.c, self.u, self.L = G, c, u, length
        self.n = (-u[1], u[0])
        self.yaw = G.a + math.atan2(u[1], u[0])

    def P(self, s, off, z):
        c, u, n = self.c, self.u, self.n
        return self.G.p(c[0] + u[0] * s + n[0] * off, c[1] + u[1] * s + n[1] * off, z)

    def box(self, mb, s, off, z, sx, sy, sz, m, rx=0.0, ry=0.0):
        mb.box((sx, sy, sz), self.P(s, off, z), (rx, ry, self.yaw), m, 0.0)

    def beam(self, mb, s0, z0, s1, z1, off, w, h, m=WOOD):
        mb.beam(self.P(s0, off, z0), self.P(s1, off, z1), w, h, m, 0.0)

    def nvec(self):
        a = self.G.a
        nx, ny = self.n
        return Vector((nx * math.cos(a) - ny * math.sin(a), nx * math.sin(a) + ny * math.cos(a), 0.0))


def window(mb, f, s, zlo, w, h, head="arch", shutters=False, planter=False):
    """janela quente com caixilho escuro em cruz, peitoril de pedra, cabeca (arco ogival de madeira / verga de pedra)"""
    zc = zlo + h / 2
    f.box(mb, s, 0.02, zc, w, 0.3, h, WIN)                                   # vidro quente
    f.box(mb, s, 0.2, zlo + h + 0.12, w + 0.6, 0.2, 0.3, WOOD)                # caixilho: topo
    f.box(mb, s, 0.2, zlo - 0.05, w + 0.6, 0.2, 0.3, WOOD)                    # base
    for k in (-1, 1):
        f.box(mb, s + k * (w / 2 + 0.15), 0.2, zc, 0.3, 0.2, h + 0.3, WOOD)    # ombreiras
    f.box(mb, s, 0.22, zc, 0.22, 0.2, h, WOOD)                                # montante
    f.box(mb, s, 0.22, zlo + h * 0.62, w, 0.2, 0.22, WOOD)                    # travessa
    f.box(mb, s, 0.3, zlo - 0.3, w + 0.9, 0.55, 0.26, TRIM)                   # peitoril
    if head == "arch":
        f.beam(mb, s - w / 2 - 0.35, zlo + h + 0.2, s, zlo + h + 1.0, 0.2, 0.3, 0.36)
        f.beam(mb, s + w / 2 + 0.35, zlo + h + 0.2, s, zlo + h + 1.0, 0.2, 0.3, 0.36)
    elif head == "lintel":
        f.box(mb, s, 0.18, zlo + h + 0.5, w + 1.0, 0.45, 0.6, TRIM)
    if shutters:
        for k in (-1, 1):
            f.box(mb, s + k * (w * 0.75 + 0.45), 0.14, zc, w * 0.5, 0.22, h, M_SHUT)
    if planter:
        f.box(mb, s, 0.5, zlo - 0.72, w + 0.4, 0.75, 0.5, WOOD)
        f.box(mb, s, 0.52, zlo - 0.32, w + 0.2, 0.6, 0.4, "Leaf_SG_Pine")


def shopfront(mb, f, s, w=4.4):
    """vitrine de loja com persiana FECHADA: mais larga que alta, peitoril de balcao a 2,1 do chao (nunca le como porta),
    bandeira quente em cima e toldo de ardosia"""
    z0, z1 = 2.1, 4.3
    f.box(mb, s, 0.05, (z0 + z1) / 2, w, 0.3, z1 - z0, M_SHUT)                 # persiana fechada
    for i in range(4):
        f.box(mb, s, 0.22, z0 + 0.35 + i * 0.5, w, 0.14, 0.2, WOOD)            # ripas
    f.box(mb, s, 0.45, z0 - 0.15, w + 0.8, 0.9, 0.3, TRIM)                     # balcao de pedra
    f.box(mb, s, 0.25, z0 - 0.9, w + 0.4, 0.3, 1.2, TRIM)                      # almofada sob o balcao
    for k in (-1, 1):
        f.box(mb, s + k * (w / 2 + 0.25), 0.2, (z0 - 0.3 + z1 + 0.5) / 2, 0.5, 0.35, z1 - z0 + 0.8, WOOD)
    f.box(mb, s, 0.2, z1 + 0.25, w + 1.0, 0.4, 0.5, WOOD)                      # verga
    f.box(mb, s, 0.04, z1 + 0.95, w, 0.3, 0.8, WIN)                            # bandeira quente
    for k in (-1, 0, 1):
        f.box(mb, s + k * w / 3, 0.2, z1 + 0.95, 0.22, 0.2, 0.8, WOOD)
    f.box(mb, s, 0.2, z1 + 1.45, w + 1.0, 0.35, 0.3, WOOD)
    # toldo de ardosia inclinado
    t = math.radians(28.0)
    f.box(mb, s, 1.0, z1 + 1.75, w + 1.4, 2.1, 0.28, ROOF, rx=-t)
    for k in (-1, 1):
        f.beam(mb, s + k * (w / 2 + 0.3), z1 + 0.9, s + k * (w / 2 + 0.3), z1 + 1.6, 1.7, 0.22, 0.22, IRON)
        f.beam(mb, s + k * (w / 2 + 0.3), z1 + 0.9, s + k * (w / 2 + 0.3), z1 + 1.9, 0.3, 0.22, 0.22, IRON)


def timber_face(mb, f, z0, z1, wins, rng):
    """estrutura aparente (so do lado de fora): soleira, frechal, montantes e escoras em chevron nos vaos cheios"""
    Lf = f.L
    f.box(mb, 0.0, 0.15, z0 + 0.22, Lf + 0.3, 0.3, 0.44, WOOD)
    f.box(mb, 0.0, 0.15, z1 - 0.22, Lf + 0.3, 0.3, 0.44, WOOD)
    xs = [-Lf / 2 + 0.22, Lf / 2 - 0.22]
    blocked = []
    for s, w in wins:
        xs += [s - w / 2 - 0.55, s + w / 2 + 0.55]
        blocked.append((s - w / 2 - 0.6, s + w / 2 + 0.6))
    xs = sorted(xs)
    full = list(xs)
    for a, b in zip(xs, xs[1:]):
        mid = (a + b) / 2
        if b - a > 3.4 and not any(b0 < mid < b1 for b0, b1 in blocked):
            full.append(mid)
    full = sorted(full)
    for x in full:
        f.box(mb, x, 0.15, (z0 + z1) / 2, 0.42, 0.3, z1 - z0 - 0.3, WOOD)
    for a, b in zip(full, full[1:]):
        mid = (a + b) / 2
        if b - a < 1.0 or any(b0 < mid < b1 for b0, b1 in blocked):
            continue
        if mid < 0:
            f.beam(mb, a + 0.2, z0 + 0.45, b - 0.2, z1 - 0.45, 0.15, 0.3, 0.38)
        else:
            f.beam(mb, a + 0.2, z1 - 0.45, b - 0.2, z0 + 0.45, 0.15, 0.3, 0.38)


def win_slots(Lf, w, n=None, margin=1.6):
    n = n if n is not None else max(1, int((Lf - 2 * margin + 1.2) / (w + 2.4)))
    step = (Lf - 2 * margin) / n
    return [-Lf / 2 + margin + step * (k + 0.5) for k in range(n)]


# ------------------------------------------------------------------ casa
def house(mb, idx, lot, spec, rng):
    x, y, w_lot, d_lot, deg, z = lot
    ya = math.radians(deg) - math.pi / 2
    gable_front = spec.get("gable_front", False)
    if gable_front:
        G = Frame(x, y, z, ya + math.pi / 2)
        W, D = d_lot, w_lot
        front = "+x"
    else:
        G = Frame(x, y, z, ya)
        W, D = w_lot, d_lot
        front = "+y"
    stories = spec["stories"]           # [("stone"|"timber", altura)]
    jet = spec.get("jetty", 0.0)
    R = spec["rise"]
    wx0, wx1, wy0, wy1 = -W / 2, W / 2, -D / 2, D / 2

    def faces(b):
        x0, x1, y0, y1 = b
        return {"+y": Face(G, (0.0, y1), (1.0, 0.0), x1 - x0), "-y": Face(G, (0.0, y0), (-1.0, 0.0), x1 - x0),
                "+x": Face(G, (x1, (y0 + y1) / 2), (0.0, -1.0), y1 - y0),
                "-x": Face(G, (x0, (y0 + y1) / 2), (0.0, 1.0), y1 - y0)}

    # base de pedra (sobe 1,0; afunda 0,4)
    mb.box((W + 0.7, D + 0.7, 1.4), G.p(0, 0, 0.3), G.r(), STONE, 0.12)
    zc = 1.0
    body = (wx0, wx1, wy0, wy1)
    top_b = body
    for si, (kind, h) in enumerate(stories):
        b = body
        if si > 0 and jet > 0:
            x0, x1, y0, y1 = body
            if gable_front:
                b = (x0, x1 + jet, y0, y1)
            else:
                b = (x0, x1, y0 - jet * 0.6, y1 + jet)
            # banda do piso em balanco + misulas sob o balanco da frente
            bx0, bx1, by0, by1 = b
            mb.box((bx1 - bx0 + 0.3, by1 - by0 + 0.3, 0.5), G.p((bx0 + bx1) / 2, (by0 + by1) / 2, zc + 0.05), G.r(),
                   WOOD, 0.0)
            ff = faces(body)[front]
            for s in win_slots(ff.L, 0.4, n=int(ff.L / 2.4), margin=0.8):
                ff.box(mb, s, jet / 2, zc - 0.45, 0.4, jet, 0.8, WOOD)
        x0, x1, y0, y1 = b
        mat = STONE if kind == "stone" else M_PL
        mb.box((x1 - x0, y1 - y0, h), G.p((x0 + x1) / 2, (y0 + y1) / 2, zc + h / 2), G.r(), mat, 0.0)
        fs = faces(b)
        for key, f in fs.items():
            is_front = key == front
            ww = 1.7 if kind == "timber" else 1.6
            wh = 2.4 if kind == "timber" else 2.5
            shop = spec.get("shop") and si == 0 and is_front
            if shop:
                slots = [(0.0, "shop")] + ([(-f.L / 2 + 2.4, "w"), (f.L / 2 - 2.4, "w")] if f.L >= 12.5 else [])
            elif is_front:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=spec.get("nwin", None))]
            else:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=(1 if f.L < 11.0 else 2))]
            zl = zc + (1.9 if kind == "stone" else 1.5)
            if si == 0 and len(stories) == 1:
                zl = zc + 2.0
            wins = []
            for s, kd in slots:
                if kd == "shop":
                    shopfront(mb, f, s)
                    continue
                window(mb, f, s, zl, 1.4 if shop else ww, wh, head=("lintel" if kind == "stone" else "arch"),
                       shutters=(is_front and kind == "stone" and not shop),
                       planter=bool(is_front and spec.get("planter") and kind == "timber"))
                wins.append((s, ww))
            if kind == "timber":
                timber_face(mb, f, zc, zc + h, wins, rng)
        if kind == "stone" and si < len(stories) - 1:
            mb.box((x1 - x0 + 0.5, y1 - y0 + 0.5, 0.45), G.p((x0 + x1) / 2, (y0 + y1) / 2, zc + h - 0.2), G.r(),
                   TRIM, 0.0)                                                 # cordao de pedra
        if kind == "stone":
            # cunhais (pedra clara alternada nas quinas)
            pq, la, lb = 0.22, 1.5, 0.9
            for cx_, cy_ in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                sgx, sgy = math.copysign(1, cx_), math.copysign(1, cy_)
                for k in range(int(h / 1.6)):
                    zz = zc + 0.8 + k * 1.6
                    ax, ay = (la, lb) if k % 2 == 0 else (lb, la)
                    mb.box((ax, ay, 0.8), G.p(cx_ - sgx * (ax / 2 - pq), cy_ - sgy * (ay / 2 - pq), zz), G.r(), TRIM,
                           0.0)
        zc += h
        body = b
        top_b = b
    ze = zc
    # ---- telhado ingreme (cumeeira ao longo de x de G) sobre o ultimo pavimento
    x0, x1, y0, y1 = top_b
    cy = (y0 + y1) / 2
    hd = (y1 - y0) / 2
    oe, og, th = 1.0, 0.8, 0.6
    t = math.atan2(R, hd)
    Ls = (hd + oe) / math.cos(t)
    rows = max(4, int(Ls / 1.6))
    dl = math.radians(3.0)
    tr = t - dl
    for s in (-1, 1):
        # fiadas de ardosia: cada fiada um pouco menos inclinada -> a borda de baixo sobra sobre a seguinte (sombra)
        for k in range(rows):
            f0 = k / rows
            f1 = min(1.0, (k + 1.35) / rows)
            ay = cy + s * f0 * (hd + oe)
            az = ze + R - f0 * (R + oe * math.tan(t))
            lr = (f1 - f0) * Ls
            dy, dz = s * math.cos(tr), -math.sin(tr)
            ny, nz = s * math.sin(tr), math.cos(tr)
            thr = 0.5 if k else th
            mb.box((x1 - x0 + 2 * og, lr, thr), G.p((x0 + x1) / 2, ay + dy * lr / 2 + ny * thr / 2,
                                                    az + dz * lr / 2 + nz * thr / 2), G.r(-s * tr, 0, 0), ROOF, 0.0)
        # guarda-po (tabua escura na borda da empena)
        for xe in (x0 - og - 0.1, x1 + og + 0.1):
            mb.beam(G.p(xe, cy, ze + R + th), G.p(xe, cy + s * (hd + oe), ze - oe * math.tan(t) + th * 0.6), 0.28,
                    0.7, WOOD, 0.0)
    rt = ze + R + th / math.cos(t)
    mb.box((x1 - x0 + 2 * og + 0.2, 0.75, 0.75), G.p((x0 + x1) / 2, cy, rt - 0.2), G.r(math.pi / 4, 0, 0), IRON, 0.0)
    for xe in (x0 - og + 0.2, x1 + og - 0.2):
        mb.cyl(0.3, 2.2, G.p(xe, cy, rt + 1.0), G.r(), IRON, n=4, r2=0.02, bevel=0.0)   # pinaculo de ferro
    # empenas (reboco + estrutura), janela de sotao
    for sx, key in ((1, "+x"), (-1, "-x")):
        f = Face(G, (x1 if sx > 0 else x0, cy), (0.0, -1.0) if sx > 0 else (0.0, 1.0), y1 - y0)
        nv = f.nvec()
        pts = [f.P(-hd, 0.0, ze), f.P(hd, 0.0, ze), f.P(0.0, 0.0, ze + R)]
        tri_slab(mb, pts, nv, 0.6, M_PL)
        f.box(mb, 0.0, 0.15, ze + 0.22, y1 - y0 + 0.3, 0.3, 0.44, WOOD)
        attic = (key == front) or spec.get("attic_all", False)
        zc_win = ze + 1.0
        if attic:
            window(mb, f, 0.0, zc_win, 1.3, 2.0, head="arch" if key == front else None)
            f.box(mb, 0.0, 0.15, (zc_win + 3.3 + ze + R - 0.6) / 2, 0.42, 0.3, ze + R - 0.6 - zc_win - 3.3, WOOD)
        else:
            f.box(mb, 0.0, 0.15, ze + R * 0.46, 0.42, 0.3, R * 0.9, WOOD)
        zcol = (ze + 4.4) if attic else (ze + R * 0.42)
        half = hd * (1 - (zcol - ze) / R) - 0.3
        f.box(mb, 0.0, 0.15, zcol, 2 * half, 0.3, 0.42, WOOD)                 # linha alta
        for k in (-1, 1):
            f.beam(mb, k * (hd - 0.5), ze + 0.4, k * max(0.5 * half, 1.7), zcol - 0.1, 0.15, 0.3, 0.36)
    # ---- aguas-furtadas
    for side, xd in spec.get("dormers", []):
        s = 1 if side == "+y" else -1
        wd = 2.8
        yf = cy + s * (hd - 0.6)
        zr = ze + R * (1 - (hd - 0.6) / hd)
        zb = zr + th / math.cos(t) + 0.1
        zt = zb + 2.9
        yb = cy + s * hd * (1 - (zt - ze) / R)
        ya0, ya1 = sorted((yb - s * 0.4, yf))
        mb.box((wd, ya1 - ya0, zt - zr + 0.6), G.p(xd, (ya0 + ya1) / 2, (zr - 0.6 + zt) / 2), G.r(), M_PL, 0.0)
        rr = 1.7
        hw = wd / 2 + 0.35
        t2 = math.atan2(rr, hw)
        L2 = hw / math.cos(t2)
        ln = abs(yf - yb) + 1.0
        for s2 in (-1, 1):
            mb.box((L2 + 0.2, ln, 0.32), G.p(xd + s2 * hw / 2, (yf + yb) / 2 + s * 0.3, zt + rr / 2 + 0.16),
                   G.r(0, s2 * t2, 0), ROOF, 0.0)
        fd = Face(G, (xd, yf), (s * 1.0, 0.0), wd)
        tri_slab(mb, [fd.P(-wd / 2, 0.0, zt), fd.P(wd / 2, 0.0, zt), fd.P(0.0, 0.0, zt + rr)], fd.nvec(), 0.4, WOOD)
        window(mb, fd, 0.0, zb + 0.5, 1.3, 1.8, head=None)
        mb.cyl(0.18, 1.2, G.p(xd, (yf + yb) / 2 + s * 0.8, zt + rr + 0.7), G.r(), IRON, n=4, r2=0.02, bevel=0.0)
    # ---- chamine
    if spec.get("chimney"):
        cx_, cy_ = spec["chimney"]
        cx_ *= (x1 - x0) / 2
        cy_ = cy + cy_ * hd
        zz0 = ze - 0.5
        zz1 = ze + R + 2.6
        mb.box((1.5, 1.5, zz1 - zz0), G.p(cx_, cy_, (zz0 + zz1) / 2), G.r(), STONE, 0.0)
        mb.box((2.0, 2.0, 0.4), G.p(cx_, cy_, zz1 + 0.2), G.r(), TRIM, 0.0)
        mb.box((0.7, 0.7, 0.8), G.p(cx_ - 0.3, cy_, zz1 + 0.8), G.r(), "Cliff_Rock_SG_Dark", 0.0)
    # ---- torreao (canto da frente)
    tur = spec.get("turret")
    if tur:
        sx, sy = tur
        tx, ty = (x0 if sx < 0 else x1) + sx * 0.6, (y1 + 0.6) if sy > 0 else (y0 - 0.6)
        wp = G.p(tx, ty, 0.0)
        r = 2.5
        zt0 = z - 0.4
        zt1 = z + ze + 3.2
        c2 = (wp.x, wp.y)
        mb.prism(SL.ccw(ngon(c2, r + 0.35, 8, 22.5)), z - 0.4, z + 1.0, STONE)
        mb.prism(SL.ccw(ngon(c2, r, 8, 22.5)), z + 1.0, zt1, STONE)
        mb.prism(SL.ccw(ngon(c2, r + 0.45, 8, 22.5)), zt1, zt1 + 0.6, TRIM)
        SL.spire(mb, c2, r + 0.9, zt1 + 0.6, 10.5, ROOF, n=8)
        mb.cyl(0.26, 2.6, (wp.x, wp.y, zt1 + 0.6 + 10.5 + 0.9), (0, 0, 0), IRON, n=4, r2=0.02, bevel=0.0)
        # frestas quentes estreitas nas faces que dao para a rua (faces do octogono centradas em k*45 graus)
        out = math.degrees(math.atan2(wp.y - G.o.y, wp.x - G.o.x))
        out = 45.0 * round(out / 45.0)
        ap = r * math.cos(math.pi / 8)
        for zz in (z + ze - 5.2, z + ze + 0.4):
            for da in (-45.0, 0.0, 45.0):
                a_ = math.radians(out + da)
                ux_, uy_ = -math.sin(a_), math.cos(a_)
                p = Vector((wp.x + ap * math.cos(a_), wp.y + ap * math.sin(a_), zz))
                mb.box((0.25, 0.6, 1.8), p, (0, 0, a_), WIN, 0.0)
                mb.box((0.4, 1.1, 0.3), p + Vector((0, 0, -1.05)), (0, 0, a_), TRIM, 0.0)
                mb.beam(p + Vector((ux_ * 0.55, uy_ * 0.55, 0.9)), p + Vector((0, 0, 1.45)), 0.3, 0.3, TRIM, 0.0)
                mb.beam(p - Vector((ux_ * 0.55, uy_ * 0.55, -0.9)), p + Vector((0, 0, 1.45)), 0.3, 0.3, TRIM, 0.0)
        octo_col("SG_VilHouse", wp.x, wp.y, r + 0.3, z - 0.4, z + ze + 3.2)
    # ---- colisao do corpo (caixa)
    bx0, bx1, by0, by1 = body
    cxb, cyb = (min(bx0, wx0) + max(bx1, wx1)) / 2, (min(by0, wy0) + max(by1, wy1)) / 2
    sxb = max(bx1, wx1) - min(bx0, wx0) + 0.7
    syb = max(by1, wy1) - min(by0, wy0) + 0.7
    hb = ze + R * 0.55
    col_box("SG_VilHouse", (sxb, syb, hb + 0.4), G.p(cxb, cyb, hb / 2 - 0.2), G.r())


# especificacao das 11 casas (indice = sg_layout.HOUSE_LOTS): 1 ou 2 pavimentos, empena de frente ou de lado,
# balanco, aguas-furtadas, chamine (x relativo a meia-largura, y relativo a meia-profundidade), um torreao, lojas
SPECS = [
    # P1 oeste
    dict(stories=[("stone", 6.4), ("timber", 5.6)], jetty=0.8, rise=8.4, shop=True, dormers=[("+y", 3.6)],
         chimney=(-0.62, -0.35), planter=True),
    dict(stories=[("timber", 6.8)], rise=9.2, dormers=[("+y", -2.6), ("+y", 2.6)], chimney=(0.6, -0.3), nwin=2),
    dict(stories=[("stone", 6.0), ("timber", 5.4)], jetty=0.8, rise=9.8, gable_front=True, chimney=(-0.55, 0.5)),
    # P1 leste
    dict(stories=[("stone", 6.6), ("timber", 6.0)], jetty=0.8, rise=8.6, turret=(-1, 1), dormers=[("+y", 3.2)],
         chimney=(0.66, -0.4), planter=True),
    dict(stories=[("timber", 7.0)], rise=10.2, gable_front=True, chimney=(0.5, -0.5), attic_all=True),
    dict(stories=[("stone", 6.2), ("timber", 5.4)], jetty=0.8, rise=8.0, shop=True, dormers=[("+y", -2.8)],
         chimney=(0.6, -0.3)),
    # P2 oeste
    dict(stories=[("stone", 6.4), ("timber", 5.8)], jetty=0.8, rise=8.8, shop=True, dormers=[("+y", -3.6), ("+y", 3.6)],
         chimney=(0.62, -0.35), planter=True),
    dict(stories=[("timber", 6.8)], rise=10.0, gable_front=True, chimney=(-0.5, 0.45)),
    dict(stories=[("stone", 6.0), ("timber", 5.6)], jetty=0.8, rise=9.6, gable_front=True, chimney=(0.5, -0.5),
         planter=True),
    # P2 leste
    dict(stories=[("timber", 6.8)], rise=9.0, dormers=[("+y", -2.6), ("+y", 2.6)], chimney=(-0.6, -0.3), nwin=2),
    dict(stories=[("stone", 6.2), ("timber", 5.6)], jetty=0.8, rise=8.4, shop=True, dormers=[("+y", 2.8)],
         chimney=(-0.62, -0.35)),
]
GROUPS = [("P1W", (0, 1, 2)), ("P1E", (3, 4, 5)), ("P2W", (6, 7, 8)), ("P2E", (9, 10))]


# ------------------------------------------------------------------ praca + fonte
def plaza():
    rng = random.Random(4101)
    mb = MB("SG_Vil_Plaza", COLL, rng, detail="near")
    c = L.PLAZA_C
    R = L.PLAZA_R
    z = P1
    mb.prism(SL.ccw(ngon(c, R, 64)), z - 0.25, z + 0.07, "Stone_Paving_SG")
    ring_prism(mb, c, R - 1.4, R, 64, z - 0.1, z + 0.13, TRIM)                 # borda de cantaria
    ring_prism(mb, c, 7.4, 9.2, 24, z - 0.1, z + 0.1, M_COB)                    # colar escuro da fonte
    for r0, r1 in ((9.2, 9.8), (16.4, 17.0)):
        ring_prism(mb, c, r0, r1, 48, z - 0.1, z + 0.11, TRIM)
    # rosacea do chao: 16 setores alternados (escuro/claro) entre os aneis + 16 raios de cantaria
    n = 16
    for k in range(n):
        a0 = 360.0 / n * k
        a1 = a0 + 360.0 / n
        if k % 2 == 0:
            outer = SL.arc_pts(16.4, a0, a1, 5.0, c[0], c[1])
            inner = SL.arc_pts(9.8, a1, a0, 5.0, c[0], c[1])
            mb.prism(SL.ccw(outer + inner), z - 0.1, z + 0.095, M_COB)
        a = math.radians(a0)
        for r0, r1 in ((9.8, 16.4), (17.0, R - 1.4)):
            if r0 > 16 and k % 2 == 1:
                continue
            rm = (r0 + r1) / 2
            mb.box((r1 - r0, 0.55, 0.22), (c[0] + rm * math.cos(a), c[1] + rm * math.sin(a), z + 0.0),
                   (0, 0, a), TRIM, 0.0)
    mb.finish()

    # fonte: bacia dodecagonal (casa com a colisao do sg_col: 12 lados, R 7, topo P1+2,6), taca em 2 niveis, lua de prata
    mf = MB("SG_Vil_Fountain", COLL, rng, detail="near")
    rot = 0.0
    mf.prism(SL.ccw(ngon(c, 7.55, 12, rot)), z - 0.1, z + 0.32, TRIM)                 # degrau
    ring_prism(mf, c, 6.05, 7.0, 12, z + 0.32, z + 2.3, "Stone_SG_Castle", rot)       # parede da bacia
    ring_prism(mf, c, 5.85, 7.25, 12, z + 2.3, z + 2.6, TRIM, rot)                    # capeamento
    for k in range(12):
        a = math.radians(rot + 30.0 * k)
        mf.box((0.75, 0.75, 1.98), (c[0] + 7.02 * math.cos(a), c[1] + 7.02 * math.sin(a), z + 1.31), (0, 0, a), TRIM,
               0.0)
    mf.prism(SL.ccw(ngon(c, 6.1, 12, rot)), z + 0.32, z + 1.95, "Stone_SG_Castle")     # fundo da bacia
    mf.prism(SL.ccw(ngon(c, 6.08, 12, rot)), z + 1.95, z + 2.05, "Water_SG")           # lamina d'agua
    cx, cy = c
    mf.cyl(1.45, 0.6, (cx, cy, z + 2.3), (0, 0, math.pi / 8), TRIM, n=8, bevel=0.0)
    mf.cyl(1.05, 2.4, (cx, cy, z + 3.8), (0, 0, math.pi / 8), TRIM, n=8, r2=0.8, bevel=0.0)
    mf.cyl(0.8, 1.1, (cx, cy, z + 5.55), (0, 0, 0), "Stone_SG_Castle", n=12, r2=3.0, bevel=0.0)   # taca de baixo
    ring_prism(mf, c, 2.7, 3.15, 12, z + 6.0, z + 6.35, TRIM)
    mf.cyl(2.72, 0.12, (cx, cy, z + 6.18), (0, 0, 0), "Water_SG", n=12, bevel=0.0)
    mf.cyl(0.55, 2.0, (cx, cy, z + 7.3), (0, 0, math.pi / 8), TRIM, n=8, r2=0.45, bevel=0.0)
    mf.cyl(0.5, 0.8, (cx, cy, z + 8.6), (0, 0, 0), "Stone_SG_Castle", n=12, r2=1.7, bevel=0.0)    # taca de cima
    ring_prism(mf, c, 1.45, 1.8, 12, z + 8.95, z + 9.2, TRIM)
    mf.cyl(1.47, 0.1, (cx, cy, z + 9.05), (0, 0, 0), "Water_SG", n=12, bevel=0.0)
    # remate de prata: haste + lua crescente (encara a entrada, -Y)
    mf.cyl(0.28, 1.6, (cx, cy, z + 10.0), (0, 0, 0), "Metal_SG_Silver", n=8, r2=0.18, bevel=0.0)
    # crescente: circulo externo R 1,5 menos o interno R 1,22 deslocado 0,55 (pontas nas intersecoes)
    Ro, Ri, dx = 1.5, 1.22, 0.55
    xi = (Ro * Ro - Ri * Ri + dx * dx) / (2 * dx)
    yi = math.sqrt(Ro * Ro - xi * xi)
    ao = math.degrees(math.atan2(yi, xi)) + 1.5
    ai = math.degrees(math.atan2(yi, xi - dx)) + 1.5
    cres = [(Ro * math.cos(math.radians(ao + (360 - 2 * ao) * i / 18)), Ro * math.sin(math.radians(ao + (360 - 2 * ao) * i / 18)))
            for i in range(19)]
    cres += [(dx + Ri * math.cos(math.radians(360 - ai - (360 - 2 * ai) * i / 14)),
              Ri * math.sin(math.radians(360 - ai - (360 - 2 * ai) * i / 14))) for i in range(15)]
    # plano vertical XZ (encara -Y, a entrada): parte grossa embaixo, sobre a haste; pontas para cima, leve giro
    o = Vector((cx, cy + 0.2, z + 10.75 + Ro))
    ang = math.radians(68.0)
    eu = Vector((math.cos(ang), 0.0, math.sin(ang)))
    ev = Vector((-math.sin(ang), 0.0, math.cos(ang)))
    poly_slab(mf, cres, (o, eu, ev, Vector((0, 1.0, 0))), 0.4, "Metal_SG_Silver")
    mf.finish()


# ------------------------------------------------------------------ ruas com meio-fio, escada P1->P2, muretas
def _street_list():
    out = []
    for i, (pts, w, z) in enumerate(L.STREETS):
        pts = list(pts)
        if z == P1 and abs(pts[0][0]) > 20 and abs(pts[0][1] - L.PLAZA_C[1]) < 20:
            # a rua da praca nasce DENTRO da praca (a borda de cantaria cobre a junta)
            sx = math.copysign(21.0, pts[0][0])
            pts = [(sx, pts[0][1])] + pts
        out.append((i, pts, w, z))
    return out


def _in_other_street(x, y, me, streets, pad=0.4):
    for i, pts, w, z in streets:
        if i == me:
            continue
        if L.polyline_dist(x, y, pts) < w / 2 + pad:
            return True
    return False


def _blocked_curb(x, y, z):
    if math.hypot(x - L.PLAZA_C[0], y - L.PLAZA_C[1]) < L.PLAZA_R + 0.3:
        return True
    if math.hypot(x - L.CRAFT_C[0], y - L.CRAFT_C[1]) < L.CRAFT_R + 0.5:
        return True
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        t = (x - foot[0]) * ux + (y - foot[1]) * uy
        d = abs(-(x - foot[0]) * uy + (y - foot[1]) * ux)
        if -tread - 1.5 <= t <= tread * n + 1.5 and d <= w / 2 + 1.4:
            return True
    zz = L.zone_of(x, y)
    return zz is None or abs(zz - z) > 0.1


def _offset_line(pts, off):
    out = []
    n = len(pts)
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            ax, ay = x - pts[i - 1][0], y - pts[i - 1][1]
            bx, by = pts[i + 1][0] - x, pts[i + 1][1] - y
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            dx, dy = ax / la + bx / lb, ay / la + by / lb
        ln = math.hypot(dx, dy) or 1.0
        out.append((x - dy / ln * off, y + dx / ln * off))
    return out


def _resample(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(ln / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def streets():
    rng = random.Random(4102)
    sl = _street_list()
    objs = {P1: MB("SG_Vil_Streets_P1", COLL, rng, detail="near"), P2: MB("SG_Vil_Streets_P2", COLL, rng, detail="near"),
            P3: MB("SG_Vil_Streets_P3", COLL, rng, detail="near")}
    for i, pts, w, z in sl:
        mb = objs[z]
        mb.prism(SL.ccw(SL.ribbon_poly(pts, w / 2)), z - 0.25, z + 0.05, "Stone_Paving_SG")
        if z == P3:
            continue            # patio do castelo / dungeon: so o calcamento (o detalhe e das zonas do P3)
        # faixa central de calcamento escuro (margens claras + centro escuro: le como rua sobre grama OU lajes)
        core = L.STREETS[i][0]
        mb.prism(SL.ccw(SL.ribbon_poly(core, w / 2 - 1.5)), z - 0.1, z + 0.075, M_COB)
        # meio-fio dos dois lados (interrompido em cruzamentos, praca, escadas, porta do craft e fora do piso)
        for side in (-1, 1):
            line = _resample(_offset_line(pts, side * (w / 2 - 0.3)), 1.0)
            runs, run = [], []
            for p in line:
                if _blocked_curb(p[0], p[1], z) or _in_other_street(p[0], p[1], i, sl, pad=0.2):
                    if len(run) > 1:
                        runs.append(run)
                    run = []
                else:
                    run.append(p)
            if len(run) > 1:
                runs.append(run)
            for run in runs:
                k = 0
                while k < len(run) - 1:
                    j = min(len(run) - 1, k + 6)
                    a, b = run[k], run[j]
                    ln = math.hypot(b[0] - a[0], b[1] - a[1])
                    if ln > 0.3:
                        mb.box((ln + 0.1, 0.6, 0.34), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z + 0.05),
                               (0, 0, math.atan2(b[1] - a[1], b[0] - a[0])), TRIM, 0.0)
                    k = j
    for o in objs.values():
        o.finish()
    # escada P1 -> P2 (so visual; a colisao e do sg_col) + muretas baixas onde a rua do P2 tem queda
    ms = MB("SG_Vil_StairP1P2", COLL, rng, detail="near")
    SL.plan_stair(ms, "P1P2", m="Stone_Paving_SG", side_m=STONE)
    for s in (-1, 1):
        SL.vis_parapet(ms, [(s * 9.9, -83.45, P2), (s * 26.0, -83.45, P2)], h=1.5, w=1.0, m=STONE)
    SL.vis_parapet(ms, [(-118.0, -55.0, P2), (-119.2, -40.4, P2), (-117.6, -35.0, P2)], h=1.5, w=1.0, m=STONE)
    ms.finish()


# ------------------------------------------------------------------ postes de ferro (eixo principal + rua da praca)
LAMPS = [
    # (x, y, z, com_luz)  topo da escada P1P2 / cruzamento do eixo com a rua do P2 / rua da praca (O e L).
    # O pe da escada fica com as lanternas da praca (vestir): par proprio aqui virava cacho de postes.
    (-10.6, -80.6, P2, True), (10.6, -80.6, P2, True),
    (7.8, -51.6, P2, True),
    (-46.0, -125.3, P1, True), (48.0, -112.9, P1, True),
]


def lamps():
    rng = random.Random(4103)
    mb = MB("SG_Vil_Lamps", COLL, rng, detail="near")
    for i, (x, y, z, lit) in enumerate(LAMPS):
        mb.cyl(0.75, 0.9, (x, y, z + 0.35), (0, 0, math.pi / 8), STONE, n=8, bevel=0.0)
        mb.cyl(0.5, 0.5, (x, y, z + 1.05), (0, 0, math.pi / 8), IRON, n=8, r2=0.3, bevel=0.0)
        mb.cyl(0.26, 6.2, (x, y, z + 4.3), (0, 0, 0), IRON, n=8, r2=0.2, bevel=0.0)
        mb.cyl(0.42, 0.3, (x, y, z + 4.0), (0, 0, 0), IRON, n=8, bevel=0.0)
        zc = z + 8.3
        mb.box((1.3, 1.3, 0.25), (x, y, zc - 0.95), (0, 0, 0), IRON, 0.0)
        mb.cyl(0.35, 0.6, (x, y, zc - 1.3), (0, 0, 0), IRON, n=8, r2=0.2, bevel=0.0)
        mb.box((0.85, 0.85, 1.5), (x, y, zc), (0, 0, 0), "Lantern_Glow", 0.0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                mb.box((0.22, 0.22, 1.7), (x + sx * 0.5, y + sy * 0.5, zc), (0, 0, 0), IRON, 0.0)
        SL.spire(mb, (x, y), 1.05, zc + 0.85, 1.6, IRON, n=4)
        mb.cyl(0.12, 0.8, (x, y, zc + 2.7), (0, 0, 0), IRON, n=4, r2=0.02, bevel=0.0)
        col_box("SG_VilLamp", (1.0, 1.0, 9.0), (x, y, z + 4.5))
        if lit:
            light("L_SGVil_Lamp_%02d" % i, "POINT", (x, y, zc), 260.0, (1.0, 0.7, 0.4), 0.4)
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    rng = random.Random(4100)
    plaza()
    streets()
    for gname, idxs in GROUPS:
        mb = MB("SG_Vil_Houses_%s" % gname, COLL, rng, detail="near")
        for i in idxs:
            house(mb, i, L.HOUSE_LOTS[i], SPECS[i], rng)
        mb.finish()
    lamps()
