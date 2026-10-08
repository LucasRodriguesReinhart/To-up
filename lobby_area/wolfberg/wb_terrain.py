# wb_terrain.py - chao do lobby Wolfberg: plato de grama com margem de rocha, lago, praca e ruas de paralelepipedo com
# meio-fio, quintais, largo do poco; PAISAGEM DE FUNDO (colinas com campos e bosques, 2 planos de montanhas com
# cristas e neve). Colisao do chao andavel por faixas (COL_).
import math
import random

import bmesh
import fm_lib
import wb_lib as W
import wb_layout as L
from mathutils import Vector
from wb_kit import Fr, oak, pine, grass_tufts, bush, STD, ST
from wb_lib import RB, V


def bpoly(poly_r):
    """poligono Roblox [(X, Z)] -> Blender [(x, y)] anti-horario"""
    pts = [(x, -z) for x, z in poly_r]
    a = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    return pts if a > 0 else list(reversed(pts))


def ribbon_r(pts, w):
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        c = pts[min(n - 1, i + 1)]
        dx, dz = c[0] - a[0], c[1] - a[1]
        ln = math.hypot(dx, dz) or 1.0
        nx, nz = -dz / ln, dx / ln
        left.append((p[0] + nx * w / 2, p[1] + nz * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - nz * w / 2))
    return left + list(reversed(right))


def circle_r(cx, cz, r, n=32, a0=0.0, a1=360.0):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n)]


def colr(area, lo, hi):
    a, c = RB(lo[0], lo[2], lo[1]), RB(hi[0], hi[2], hi[1])
    return fm_lib.col_box2(area, a, c)


def col_poly_strips(area, poly_r, y_top, thick=3.0, step=8.0):
    """piso de colisao de um poligono Roblox por faixas em X (caixas alinhadas)"""
    xs0 = [p[0] for p in poly_r]
    lo, hi = min(xs0), max(xs0)
    br = sorted({round(lo + k * step, 4) for k in range(int((hi - lo) / step) + 1)} | {round(hi, 4)})
    n = 0
    for xa, xb in zip(br, br[1:]):
        if xb - xa < 0.05:
            continue
        xm = (xa + xb) / 2
        zs = []
        m = len(poly_r)
        for i in range(m):
            (ax, az), (bx_, bz) = poly_r[i], poly_r[(i + 1) % m]
            if (ax <= xm < bx_) or (bx_ <= xm < ax):
                zs.append(az + (bz - az) * (xm - ax) / (bx_ - ax))
        zs.sort()
        for k in range(0, len(zs) - 1, 2):
            if zs[k + 1] - zs[k] > 0.05:
                colr(area, (xa, y_top - thick, zs[k]), (xb, y_top, zs[k + 1]))
                n += 1
    return n


# ilhas de grama da praca: (cx, cz, rx, rz, semente) Roblox - cantos da praca, fora do eixo x -10..10 e das rotas
PLAZA_GRASS = [(-30.0, 30.0, 9.0, 6.5, 1), (36.0, 36.0, 8.0, 4.5, 2), (-34.0, -22.0, 6.0, 9.0, 3), (46.0, -10.0, 5.0, 8.0, 4),
               (14.0, 36.0, 5.0, 3.5, 5), (-20.0, -36.0, 7.0, 3.5, 6)]


def blob(cx, cz, rx, rz, seed, n=14):
    r = random.Random(seed)
    k1, k2, p1 = r.uniform(2, 3), r.uniform(4, 6), r.uniform(0, 6.3)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n
        f = 1.0 + 0.16 * math.sin(k1 * a + p1) + 0.08 * math.sin(k2 * a)
        out.append((cx + rx * f * math.cos(a), cz + rz * f * math.sin(a)))
    return out


# tapetes circulares de bronze onde o jogador para em cada estacao (Roblox x, z)
STATION_PADS = [(-0.9, -45.0), (48.0, -9.0), (-36.0, -24.0), (-11.5, 35.5), (-104.0, 62.0)]


def ring(b, cx, cz, r0, r1, y, h, mat, n=32):
    import bmesh
    bm = bmesh.new()
    outer = [bm.verts.new(RB(cx + r1 * math.cos(2 * math.pi * k / n), cz + r1 * math.sin(2 * math.pi * k / n), y)) for k in range(n)]
    inner = [bm.verts.new(RB(cx + r0 * math.cos(2 * math.pi * k / n), cz + r0 * math.sin(2 * math.pi * k / n), y)) for k in range(n)]
    outer2 = [bm.verts.new(RB(cx + r1 * math.cos(2 * math.pi * k / n), cz + r1 * math.sin(2 * math.pi * k / n), y + h)) for k in range(n)]
    inner2 = [bm.verts.new(RB(cx + r0 * math.cos(2 * math.pi * k / n), cz + r0 * math.sin(2 * math.pi * k / n), y + h)) for k in range(n)]
    for k in range(n):
        j = (k + 1) % n
        bm.faces.new((outer2[k], outer2[j], inner2[j], inner2[k]))
        bm.faces.new((outer[k], inner[k], inner[j], outer[j]))
        bm.faces.new((outer[k], outer[j], outer2[j], outer2[k]))
        bm.faces.new((inner[j], inner[k], inner2[k], inner2[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, mat)


def medallion(b, cx, cz, r):
    """medalhao da praca: anel externo de bronze, disco de pedra escura, anel interno, 4 raios e bigorna de bronze"""
    y = L.Y_PAVE + 0.08
    ring(b, cx, cz, r - 0.7, r, y, 0.1, "WB_Brass", 40)
    b.cyl(RB(cx, cz, y - 0.3), RB(cx, cz, y + 0.06), r - 0.7, "WB_Stone_Dark", seg=40)
    ring(b, cx, cz, r * 0.42, r * 0.42 + 0.5, y, 0.1, "WB_Brass", 32)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        b.beam(RB(cx + (r * 0.42 + 0.5) * math.cos(a), cz + (r * 0.42 + 0.5) * math.sin(a), y + 0.05),
               RB(cx + (r - 0.7) * math.cos(a), cz + (r - 0.7) * math.sin(a), y + 0.05), 0.5, 0.1, "WB_Brass")
    # bigorna estilizada (silhueta chata) no centro
    b.box(RB(cx, cz, y + 0.08), (4.2, 1.6, 0.12), "WB_Brass")
    b.box(RB(cx, cz, y + 0.08), (1.8, 2.6, 0.12), "WB_Brass")
    b.cyl(RB(cx + 2.6, cz, y + 0.02), RB(cx + 2.6, cz, y + 0.14), 0.8, "WB_Brass", seg=10)


def pad(b, cx, cz, r):
    y = L.Y_PAVE + 0.08
    ring(b, cx, cz, r - 0.5, r, y, 0.08, "WB_Brass", 28)
    ring(b, cx, cz, r - 0.9, r - 0.6, y, 0.06, "WB_LampGlow", 28)


def paved(b, poly_r, y_top, mat="WB_Cobble", curb=True, thick=0.7):
    """laje de paralelepipedo (poligono Roblox) com meio-fio de pedra escura"""
    pts = bpoly(poly_r)
    b.prism(pts, y_top - thick, y_top, mat)
    if curb:
        n = len(pts)
        for i in range(n):
            a, c = pts[i], pts[(i + 1) % n]
            b.beam((a[0], a[1], y_top + 0.12), (c[0], c[1], y_top + 0.12), 0.9, 0.5, STD)


def plateau(b):
    pts = bpoly(L.PLATEAU)
    # rocha da margem (abaixo da grama) + capa de grama
    b.prism(pts, L.PLATEAU_BOTTOM, L.Y_GRASS - 0.6, "WB_Rock")
    grow = [(x * 1.012, y * 1.012) for (x, y) in pts]
    b.prism(grow, L.Y_GRASS - 0.6, L.Y_GRASS, "WB_Grass")
    # lago
    b.cyl((0, 0, L.Y_WATER - 1.0), (0, 0, L.Y_WATER), L.LAKE_R, "WB_Water", seg=48)
    # penhascos de rocha na borda norte/noroeste do plato (atras da forja): escala e enquadramento
    rc = random.Random(9)
    n = len(L.PLATEAU)
    for i in range(n):
        (x0, z0), (x1, z1) = L.PLATEAU[i], L.PLATEAU[(i + 1) % n]
        if (z0 + z1) / 2 > -60:
            continue
        seg = math.hypot(x1 - x0, z1 - z0)
        for k in range(int(seg / 12)):
            t = (k + rc.random()) / max(1, int(seg / 12))
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            cx, cz = x * 0.97 + rc.uniform(-4, 4), z * 0.97 + rc.uniform(-4, 4)
            h = rc.uniform(14, 30)
            b.sphere(RB(cx, cz, L.Y_GRASS + h * 0.25), 1.0, "WB_Rock", seg=8,
                     scale=(rc.uniform(7, 12), rc.uniform(6, 10), h))
    # pedras na margem
    r = random.Random(5)
    n = len(L.PLATEAU)
    for i in range(n):
        (x0, z0), (x1, z1) = L.PLATEAU[i], L.PLATEAU[(i + 1) % n]
        seg = math.hypot(x1 - x0, z1 - z0)
        for k in range(int(seg / 14)):
            t = (k + r.random()) / max(1, int(seg / 14))
            x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
            cx, cz = x * 1.02 + r.uniform(-3, 3), z * 1.02 + r.uniform(-3, 3)
            b.sphere(RB(cx, cz, L.Y_WATER + r.uniform(-1.0, 2.5)), r.uniform(2.5, 5.5), "WB_Rock", seg=7,
                     scale=(1.0, r.uniform(0.7, 1.3), 0.7))


def ground(coll="02_TERRAIN"):
    """chao andavel + plato + lago. Devolve a lista de objetos"""
    b = W.Build("WB_Ter_Plateau", coll)
    plateau(b)
    objs = b.finish()
    b = W.Build("WB_Ter_Paving", coll)
    paved(b, L.PLAZA, L.Y_PAVE)
    paved(b, ribbon_r(L.WEST_ROAD, L.ROAD_W), L.Y_PAVE, curb=False)
    sw = L.SOUTH_ROAD_W / 2
    paved(b, [(-sw, L.SOUTH_ROAD[0][1]), (sw, L.SOUTH_ROAD[0][1]), (sw, L.SOUTH_ROAD[1][1]), (-sw, L.SOUTH_ROAD[1][1])],
          L.Y_PAVE, curb=False)
    # EIXO principal (linguagem de piso): faixa de lajeado grande e claro, 0,08 acima, com borda de pedra escura,
    # do portao ate a soleira da forja; medalhao de bronze no centro da praca; tapetes de bronze nas estacoes
    AX = 9.0
    axis = [(-AX, L.GATE[1] - 2.0), (AX, L.GATE[1] - 2.0), (AX, -38.0), (-AX, -38.0)]
    b.prism(bpoly(axis), L.Y_PAVE - 0.3, L.Y_PAVE + 0.08, "WB_Flag")
    for x in (-AX, AX):
        b.beam(RB(x, L.GATE[1] - 2.0, L.Y_PAVE + 0.14), RB(x, -38.0, L.Y_PAVE + 0.14), 0.8, 0.5, STD)
    medallion(b, 0.0, 0.0, 9.0)
    for (px, pz) in STATION_PADS:
        pad(b, px, pz, 3.4)
    paved(b, [(-14, 88), (14, 88), (14, 104), (-14, 104)], L.Y_PAVE, curb=True)
    # ilhas de grama dentro da praca (como na referencia: cantos e bordas, nunca no eixo nem nas rotas)
    for (cx, cz, rx, rz, seed) in PLAZA_GRASS:
        poly = blob(cx, cz, rx, rz, seed)
        b.prism(bpoly(poly), L.Y_PAVE - 0.2, L.Y_PAVE + 0.12, "WB_Grass")
        n = len(poly)
        for i in range(n):
            a_, c_ = poly[i], poly[(i + 1) % n]
            b.beam(RB(a_[0], a_[1], L.Y_PAVE + 0.2), RB(c_[0], c_[1], L.Y_PAVE + 0.2), 0.7, 0.4, STD)
    paved(b, L.FORGE_YARD, L.Y_PAVE - 0.1, mat="WB_Dirt", curb=False)
    paved(b, L.FORGE_YARD_E, L.Y_PAVE - 0.1, mat="WB_Dirt", curb=False)
    # patio dos portais: disco + terraco
    paved(b, circle_r(L.COURT_C[0], L.COURT_C[1], L.COURT_R, 36), L.Y_PAVE, curb=True)
    r0, r1, a0, a1 = L.COURT_RING
    ring = circle_r(L.COURT_C[0], L.COURT_C[1], r1, 24, a0, a1) + list(reversed(circle_r(L.COURT_C[0], L.COURT_C[1], r0 + 0.5, 24, a0, a1)))
    b.prism(bpoly(ring), L.Y_PAVE - 0.5, L.Y_PORTAL, "WB_Stone")
    # 2 degraus do terraco (anel interno)
    for k, (rr, yy) in enumerate(((r0 - 1.6, L.Y_PAVE + 0.6), (r0 - 3.2, L.Y_PAVE + 0.3))):
        step = circle_r(L.COURT_C[0], L.COURT_C[1], r0 + 0.5, 24, a0, a1) + list(reversed(circle_r(L.COURT_C[0], L.COURT_C[1], rr, 24, a0, a1)))
        b.prism(bpoly(step), L.Y_PAVE - 0.3, yy, "WB_Stone_Dark")
    objs += b.finish()
    # colisao do chao
    for name, poly in (("Plaza", L.PLAZA), ("RoadW", ribbon_r(L.WEST_ROAD, L.ROAD_W)),
                       ("RoadS", [(-sw, L.SOUTH_ROAD[0][1]), (sw, L.SOUTH_ROAD[0][1]), (sw, L.SOUTH_ROAD[1][1]), (-sw, L.SOUTH_ROAD[1][1])]),
                       ("Well", [(-14, 88), (14, 88), (14, 104), (-14, 104)]), ("YardW", L.FORGE_YARD), ("YardE", L.FORGE_YARD_E),
                       ("Court", circle_r(L.COURT_C[0], L.COURT_C[1], L.COURT_R, 24)), ("Forge", L.FORGE_FLOOR)):
        col_poly_strips(name, poly, L.Y_PAVE, 3.0, 10.0)
    col_poly_strips("Grass", L.PLATEAU, L.Y_GRASS, 4.0, 16.0)
    col_ring_sectors("CourtRing", L.COURT_C[0], L.COURT_C[1], r0 - 0.5, r1, a0, a1, L.Y_PORTAL, 3.0, 5.0)
    return objs


def col_ring_sectors(area, cx, cz, r0, r1, a0, a1, y_top, thick=3.0, step_deg=5.0):
    """colisao de um setor de anel por caixas giradas (segue o circulo; faixas em X deixam buracos no anel interno)"""
    n = max(1, int(round((a1 - a0) / step_deg)))
    rm = (r0 + r1) / 2
    for k in range(n):
        am = a0 + (a1 - a0) * (k + 0.5) / n
        half = (a1 - a0) / n / 2
        w = 2 * r1 * math.sin(math.radians(half)) + 0.6          # largura tangencial com sobreposicao
        x, z = cx + rm * math.cos(math.radians(am)), cz + rm * math.sin(math.radians(am))
        # eixo X local da caixa = radial (Roblox: (cos, sin) -> Blender (cos, -sin))
        yaw = math.atan2(-math.sin(math.radians(am)), math.cos(math.radians(am)))
        fm_lib.col_box(area, (r1 - r0, w, thick), RB(x, z, y_top - thick / 2), (0, 0, yaw))
    return n


def bpoly_r(poly_r):
    return list(poly_r)


# ------------------------------------------------------------------ paisagem de fundo
def ridge(b, cx, cz, length, bearing, h, w, mat, snow=None, seed=0, n=14, y0=None):
    """cordilheira: perfil poligonal irregular (cristas) extrudado na largura; neve = capa acima de h*snow"""
    r = random.Random(seed)
    y0 = L.Y_WATER - 2.0 if y0 is None else y0
    ca, sa = math.cos(math.radians(bearing)), math.sin(math.radians(bearing))
    bm = bmesh.new()
    prof = []
    f1, f2, p1, p2 = r.uniform(2.0, 3.5), r.uniform(5.0, 8.0), r.uniform(0, 6.3), r.uniform(0, 6.3)
    for k in range(n + 1):
        t = k / n
        env = math.sin(math.pi * t) ** 0.6
        peaks = 0.62 + 0.25 * math.sin(f1 * math.pi * t + p1) + 0.13 * math.sin(f2 * math.pi * t + p2)
        hk = h * env * peaks * (0.9 + 0.2 * r.random()) if 0 < k < n else 0.0
        prof.append((t, hk))
    sm = list(prof)
    sm[0] = (0.0, 0.0)
    sm[-1] = (1.0, 0.0)
    rows = []
    for (t, hk) in sm:
        x = cx + (t - 0.5) * length * ca
        z = cz + (t - 0.5) * length * sa
        wk = w * (0.5 + 0.5 * math.sin(math.pi * t) ** 0.5)
        rows.append((x, z, hk, wk))
    front = [bm.verts.new(RB(x - sa * wk / 2, z + ca * wk / 2, y0)) for (x, z, hk, wk) in rows]
    back = [bm.verts.new(RB(x + sa * wk / 2, z - ca * wk / 2, y0)) for (x, z, hk, wk) in rows]
    top = [bm.verts.new(RB(x + r.uniform(-0.08, 0.08) * wk, z + r.uniform(-0.08, 0.08) * wk, y0 + hk)) for (x, z, hk, wk) in rows]
    for i in range(len(rows) - 1):
        bm.faces.new((front[i], front[i + 1], top[i + 1], top[i]))
        bm.faces.new((top[i], top[i + 1], back[i + 1], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, mat)
    if snow:
        bm = bmesh.new()
        zc = y0 + h * snow
        rows2 = [(x, z, hk, wk) for (x, z, hk, wk) in rows]
        tops, fr, bk = [], [], []
        for (x, z, hk, wk) in rows2:
            if hk > zc - y0:
                f = 1 - (zc - y0) / hk          # meia largura relativa na linha da neve
                tops.append(bm.verts.new(RB(x, z, y0 + hk + 0.4)))
                fr.append(bm.verts.new(RB(x - sa * wk / 2 * f, z + ca * wk / 2 * f, zc + 0.4)))
                bk.append(bm.verts.new(RB(x + sa * wk / 2 * f, z - ca * wk / 2 * f, zc + 0.4)))
            else:                                # abaixo da linha da neve: os 3 pontos colapsam no cume
                v = bm.verts.new(RB(x, z, y0 + hk + 0.3))
                tops.append(v)
                fr.append(v)
                bk.append(v)
        for i in range(len(rows2) - 1):
            for quad in ((fr[i], fr[i + 1], tops[i + 1], tops[i]), (tops[i], tops[i + 1], bk[i + 1], bk[i])):
                uniq = []
                for v in quad:
                    if v not in uniq:
                        uniq.append(v)
                if len(uniq) >= 3:
                    try:
                        bm.faces.new(uniq)
                    except ValueError:
                        pass
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, "WB_Snow")


def hill(b, cx, cz, rx, rz, h, mat="WB_Grass_Hill", y0=None):
    y0 = L.Y_WATER - 1.0 if y0 is None else y0
    b.sphere(RB(cx, cz, y0), 1.0, mat, seg=14, scale=(rx, rz, h))


def backdrop(coll="02_TERRAIN"):
    """margem distante: colinas com campos lavrados e bosques; 2 planos de montanhas com neve"""
    r = random.Random(11)
    b = W.Build("WB_Bg_Hills", coll)
    # colinas em volta (fora do lago, r 430..620), mais altas ao norte (atras da forja)
    hills = []
    for i in range(22):
        a = math.radians(i * 360 / 22 + r.uniform(-6, 6))
        d = r.uniform(470, 600)
        cx, cz = d * math.cos(a), d * math.sin(a)
        north = max(0.0, -math.sin(a))
        h = r.uniform(30, 55) + 30 * north
        rx, rz = r.uniform(90, 150), r.uniform(80, 130)
        hill(b, cx, cz, rx, rz, h)
        hills.append((cx, cz, rx, rz, h))
    # campos lavrados (faixas) sobre algumas colinas: lajes finas inclinadas lidas de longe
    for (cx, cz, rx, rz, h) in hills[::3]:
        for k in range(3):
            fx, fz = cx + r.uniform(-rx * 0.5, rx * 0.5), cz + r.uniform(-rz * 0.5, rz * 0.5)
            b.box(RB(fx, fz, L.Y_WATER - 1.0 + h * 0.55), (r.uniform(40, 70), r.uniform(25, 40), 1.5),
                  "WB_Crop" if k % 2 == 0 else "WB_Dirt", rot=None)
    objs = b.finish()
    # bosques nas colinas (pinheiros grandes, poucos tris)
    b = W.Build("WB_Bg_Forest", coll)
    F0 = Fr(V((0, 0, 0)), (0, 1))
    for (cx, cz, rx, rz, h) in hills:
        for k in range(10):
            a = r.uniform(0, 2 * math.pi)
            dd = r.uniform(0.2, 0.75)
            px, pz = cx + rx * dd * math.cos(a), cz + rz * dd * math.sin(a)
            hy = L.Y_WATER - 1.0 + h * math.sqrt(max(0.0, 1 - dd * dd)) - 2.0
            Fp = Fr(RB(px, pz, hy), (0, 1))
            if r.random() < 0.65:
                pine_far(b, Fp, r.uniform(22, 34), seed=k)
            else:
                oak_far(b, Fp, r.uniform(16, 24), seed=k)
    objs += b.finish()
    # montanhas: plano medio (rocha + neve) e plano distante (azulado)
    b = W.Build("WB_Bg_Mountains", coll)
    for i in range(9):
        a = i * 360 / 9 + r.uniform(-8, 8)
        north = max(0.0, -math.sin(math.radians(a)))
        d = r.uniform(700, 820) - 90 * north
        cx, cz = d * math.cos(math.radians(a)), d * math.sin(math.radians(a))
        ridge(b, cx, cz, r.uniform(380, 560), a + 90 + r.uniform(-15, 15), r.uniform(190, 260) + 150 * north,
              r.uniform(180, 240), "WB_Rock", snow=0.66, seed=100 + i, n=22)
    for i in range(7):
        a = i * 360 / 7 + 20 + r.uniform(-8, 8)
        d = r.uniform(1150, 1300)
        cx, cz = d * math.cos(math.radians(a)), d * math.sin(math.radians(a))
        north = max(0.0, -math.sin(math.radians(a)))
        ridge(b, cx, cz, r.uniform(700, 900), a + 90 + r.uniform(-10, 10), r.uniform(300, 380) + 160 * north,
              r.uniform(260, 340), "WB_FarMountain", snow=0.78, seed=200 + i, n=26)
    objs += b.finish()
    return objs


def pine_far(b, F, h, seed=0):
    r = random.Random(seed)
    b.cyl(F.p(0, 0, 0), F.p(0, 0, h * 0.3), 0.9, "WB_Bark", seg=5, r1=0.5)
    for k in range(3):
        z0 = h * (0.2 + 0.8 * k / 3)
        z1 = h * (0.2 + 0.8 * (k + 1.3) / 3)
        b.cyl(F.p(0, 0, z0), F.p(0, 0, z1), h * 0.2 * (1 - 0.2 * k), "WB_Pine", seg=6, r1=0.05)


def oak_far(b, F, h, seed=0):
    b.cyl(F.p(0, 0, 0), F.p(0, 0, h * 0.5), 1.2, "WB_Bark", seg=5, r1=0.6)
    b.sphere(F.p(0, 0, h * 0.72), h * 0.4, "WB_Leaf", seg=7, scale=(1, 1, 0.8))


def vegetation(coll="09_VEGETATION", oaks=True, pines=True, tufts=True):
    """carvalhos da planta, pinheiros na borda do plato, tufos/flores nas bordas da praca"""
    r = random.Random(21)
    b = W.Build("WB_Veg_Trees", coll)
    F0 = Fr(RB(0, 0, L.Y_GRASS), (0, 1))
    if oaks:
        for i, (x, z) in enumerate(L.OAKS):
            oak(b, Fr(RB(x, z, L.Y_GRASS), (0, 1)), 0, 0, r.uniform(15, 19), seed=i)
    if pines:
        n = len(L.PLATEAU)
        for i in range(n):
            (x0, z0), (x1, z1) = L.PLATEAU[i], L.PLATEAU[(i + 1) % n]
            seg = math.hypot(x1 - x0, z1 - z0)
            for k in range(int(seg / 11)):
                t = (k + r.random()) / max(1, int(seg / 11))
                x, z = x0 + (x1 - x0) * t, z0 + (z1 - z0) * t
                # para dentro do plato (10..26 studs), evitando o eixo da ponte e o patio
                cx, cz = x * r.uniform(0.86, 0.94), z * r.uniform(0.86, 0.94)
                if abs(cx) < 16 and cz > 120:
                    continue
                if math.hypot(cx - L.COURT_C[0], cz - L.COURT_C[1]) < L.COURT_RING[1] + 6:
                    continue
                big = 1.45 if cz < -60 else 1.0          # pinheiros gigantes atras da forja
                if r.random() < 0.7:
                    pine(b, Fr(RB(cx, cz, L.Y_GRASS), (0, 1)), 0, 0, r.uniform(20, 30) * big, seed=i * 10 + k)
                else:
                    oak(b, Fr(RB(cx, cz, L.Y_GRASS), (0, 1)), 0, 0, r.uniform(14, 18), seed=i * 10 + k)
    objs = b.finish()
    if tufts:
        b = W.Build("WB_Veg_Tufts", coll)
        F0 = Fr(RB(0, 0, L.Y_GRASS), (0, 1))
        # faixa de grama em volta da praca (fora do meio-fio) e ao longo da rua sul
        bands = [[(-72, 24), (-42, 24), (-42, 44), (-72, 44)], [(-72, -62), (-42, -62), (-42, -46), (-72, -46)],
                 [(56, 6), (76, 6), (76, 44), (56, 44)], [(56, -40), (76, -40), (76, -24), (56, -24)],
                 [(-50, 42), (-10, 42), (-10, 60), (-50, 60)], [(10, 42), (52, 42), (52, 60), (10, 60)],
                 [(-16, 60), (-9, 60), (-9, 140), (-16, 140)], [(9, 60), (16, 60), (16, 140), (9, 140)]]
        for i, band in enumerate(bands):
            poly = [(x, -z) for (x, z) in band]
            grass_tufts(b, F0, poly, 28, seed=i, flowers=0.35)
        F1 = Fr(RB(0, 0, L.Y_PAVE + 0.1), (0, 1))
        for (cx, cz, rx, rz, seed) in PLAZA_GRASS:
            poly = [(x, -z) for (x, z) in blob(cx, cz, rx * 0.85, rz * 0.85, seed)]
            grass_tufts(b, F1, poly, int(rx * rz * 0.35), seed=100 + seed, flowers=0.5)
            bush(b, F1, cx + rx * 0.3, -(cz - rz * 0.2), 1.6, seed=seed, flowers="WB_FlowerPink" if seed % 2 else None)
        for i in range(10):
            bush(b, F0, r.uniform(-60, 60), -r.uniform(-38, 46) if False else -(r.uniform(42, 58)), r.uniform(1.6, 2.6), seed=i,
                 flowers=r.choice([None, "WB_FlowerRed", "WB_FlowerPink"]))
        objs += b.finish()
    return objs
