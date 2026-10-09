# sn_ground.py - CHAO do plato do Santuario: gramado (triangulacao do poligono do plato, ondulacao suave longe das
# estacoes), TRILHAS de terra batida da praca ate cada estacao (bordas irregulares), BARRANCO de terra e pedra ate o
# lago com pedras semi-submersas e juncos, o LAGO e tufos de grama/flores espalhados. Pintura assada (sn_paint):
# grama com manchas largas e sombra de contato (AO) de tudo que esta em cima.
import math
import random

import bmesh
import bpy
import fm_lib
import sn_lib as SL
import sn_layout as L
import sn_vegplan as VP
from mathutils import Vector, geometry
from sn_kit import worn_block, rng
from wb_lib import RB

V = Vector
COLL = "02_TERRAIN"
CELL = 4.0


def _noise(x, z, s, seed=0):
    from sn_veg import _vnoise
    return _vnoise(V((x, z, seed * 17.0)), s)


def _resample(poly, step):
    out = []
    n = len(poly)
    for i in range(n):
        x1, z1 = poly[i]
        x2, z2 = poly[(i + 1) % n]
        d = math.hypot(x2 - x1, z2 - z1)
        k = max(1, int(d / step))
        for j in range(k):
            t = j / k
            out.append((x1 + (x2 - x1) * t, z1 + (z2 - z1) * t))
    return out


def _zone_dist(x, z):
    """distancia aproximada ate a zona construida mais proxima (0 dentro)"""
    circ, rect = VP.keepout()
    d = 1e9
    for (cx, cz, r) in circ:
        d = min(d, math.hypot(x - cx, z - cz) - r)
    for (x0, x1, z0, z1) in rect:
        dx = max(x0 - x, 0.0, x - x1)
        dz = max(z0 - z, 0.0, z - z1)
        d = min(d, math.hypot(dx, dz) if (dx or dz) else -1.0)
    return d


def height(x, z):
    d = _zone_dist(x, z)
    e = VP.edge_dist(x, z)
    a = 0.55 * max(0.0, min(1.0, (d - 2.0) / 14.0)) * max(0.0, min(1.0, (e - 3.0) / 10.0))
    return L.Y_GRASS + a * (_noise(x, z, 0.035, 1) - 0.35) * 2.0


def lawn(poly):
    """malha do gramado: CDT com o contorno da terra como restricao e uma grade interna"""
    bnd = _resample(poly, CELL)
    pts = [V((x, z)) for (x, z) in bnd]
    nb = len(pts)
    xs = [p[0] for p in poly]
    zs = [p[1] for p in poly]
    z = min(zs) + CELL / 2
    k = 0
    while z < max(zs):
        x = min(xs) + CELL / 2 + (CELL / 2 if k % 2 else 0.0)
        while x < max(xs):
            if VP._in_poly(x, z, poly) and VP._edge_dist(x, z, poly) > CELL * 0.6:
                pts.append(V((x, z)))
            x += CELL
        z += CELL * 0.87
        k += 1
    edges = [(i, (i + 1) % nb) for i in range(nb)]
    res = geometry.delaunay_2d_cdt(pts, edges, [list(range(nb))], 1, 1e-4)
    vco, ed, faces = res[0], res[1], res[2]
    bm = bmesh.new()
    vs = [bm.verts.new(RB(p[0], p[1], height(p[0], p[1]))) for p in vco]
    for f in faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    return bm, bnd


def bank(b, bnd, center=(0.0, -7.0), seed="bank"):
    """barranco do contorno ate abaixo da agua, com ruido, + pedras na beira e juncos"""
    n = len(bnd)
    r = rng(seed)
    bm = bmesh.new()
    rings = []
    for (x, z) in bnd:
        # normal para fora (centro aproximado da terra)
        cx, cz = center
        dx, dz = x - cx, z - cz
        dl = math.hypot(dx, dz) or 1.0
        dx, dz = dx / dl, dz / dl
        w = 5.0 + 3.0 * _noise(x, z, 0.06, 3)
        n1, n2 = _noise(x, z, 0.1, 4), _noise(x, z, 0.07, 5)
        ring = [(x, z, L.Y_GRASS), (x + dx * w * 0.25, z + dz * w * 0.25, L.Y_GRASS - 1.4 - 0.8 * n1),
                (x + dx * w * (0.45 + 0.2 * n2), z + dz * w * (0.45 + 0.2 * n2), L.Y_GRASS - 9.0 - 2.0 * n1),
                (x + dx * w * (0.75 + 0.2 * n1), z + dz * w * (0.75 + 0.2 * n1), L.Y_WATER + 1.5),
                (x + dx * w * 1.15, z + dz * w * 1.15, L.Y_WATER - 3.0)]
        rings.append([bm.verts.new(RB(*p)) for p in ring])
    for i in range(n):
        a, c = rings[i], rings[(i + 1) % n]
        for j in range(len(a) - 1):
            bm.faces.new((a[j], c[j], c[j + 1], a[j + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    b.mesh(bm, "SN_Bank")
    # pedras na beira (meio submersas) e juncos
    for i in range(0, n, 2):
        x, z = bnd[i]
        if r.random() < 0.45:
            continue
        cx, cz = center
        dx, dz = x - cx, z - cz
        dl = math.hypot(dx, dz) or 1.0
        dx, dz = dx / dl, dz / dl
        t = r.uniform(2.5, 5.5)
        s = r.uniform(1.2, 3.2)
        from wb_kit import Fr
        F = Fr(RB(x + dx * t, z + dz * t, L.Y_WATER - 0.6), (dx, -dz))
        worn_block(b, F, 0.0, 0.0, s * 0.35, (s * 1.6, s * 1.2, s * 1.1), "SN_ShoreRock", seed=("sr", seed, i), chips=3,
                   bevel=0.35 * s, turn=r.uniform(0, 90), tilt=(r.uniform(-12, 12), r.uniform(-12, 12)))
        if r.random() < 0.5:
            for k in range(r.randint(4, 8)):
                px = x + dx * (t - 1.5) + r.uniform(-2, 2)
                pz = z + dz * (t - 1.5) + r.uniform(-2, 2)
                h = r.uniform(2.0, 3.6)
                b0 = RB(px, pz, L.Y_WATER - 0.4)
                b.cyl(b0, b0 + V((r.uniform(-0.4, 0.4), r.uniform(-0.4, 0.4), h)), 0.09, "SN_Reed", seg=4, r1=0.03)


def path_strip(b, pts, w, seed):
    """trilha de terra batida: faixa ao longo da polilinha com bordas irregulares, rente ao gramado"""
    r = rng("path", seed)
    dense = []
    for (a, c) in zip(pts, pts[1:]):
        d = math.hypot(c[0] - a[0], c[1] - a[1])
        k = max(1, int(d / 2.0))
        for j in range(k):
            t = j / k
            dense.append((a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t))
    dense.append(pts[-1])
    bm = bmesh.new()
    L_, R_ = [], []
    for i, (x, z) in enumerate(dense):
        p0 = dense[max(0, i - 1)]
        p1 = dense[min(len(dense) - 1, i + 1)]
        tx, tz = p1[0] - p0[0], p1[1] - p0[1]
        tl = math.hypot(tx, tz) or 1.0
        nx, nz = -tz / tl, tx / tl
        hw = w / 2 * (0.8 + 0.45 * _noise(x, z, 0.25, seed if isinstance(seed, int) else 7))
        for side, lst in ((1, L_), (-1, R_)):
            px, pz = x + nx * hw * side, z + nz * hw * side
            lst.append(bm.verts.new(RB(px, pz, height(px, pz) + 0.06)))
    for i in range(len(dense) - 1):
        bm.faces.new((L_[i], R_[i], R_[i + 1], L_[i + 1]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    for f in bm.faces:
        if f.normal.z < 0:
            f.normal_flip()
    b.mesh(bm, "SN_Path")


def paths(b):
    def ring(rr, deg):
        a = math.radians(deg)
        return (rr * math.cos(a), rr * math.sin(a))
    k = 0
    # trilha oeste: praca -> cabeceira da ponte da ilha dos portais (larga, a principal)
    bz = L.ISLE_BRIDGE["z"]
    path_strip(b, [ring(L.PLAZA_R - 1.0, L.WEST_ANG), ring(L.PLAZA_R + 14.0, L.WEST_ANG - 1.0),
                   (L.ISLE_BRIDGE["x_main"] + 6.0, bz)], 8.0, k)
    k += 1
    # ilha: da ponte ao patio e anel de terra em volta do patio (diante dos estrados)
    ix, iz = L.PORTAL_ISLE_C
    path_strip(b, [(L.ISLE_BRIDGE["x_isle"] - 3.0, bz), (ix + L.ISLE_COURT_R - 1.0, iz)], 8.0, k)
    k += 1
    pts = [(ix + (L.ISLE_COURT_R + 1.6) * math.cos(math.radians(a)), iz + (L.ISLE_COURT_R + 1.6) * math.sin(math.radians(a)))
           for a in range(0, 366, 8)]
    path_strip(b, pts, 4.0, k)
    k += 1
    for (tx, tz), dist in ((L.SHOP_C, 15.0), (L.RANK_O, 18.0)):
        a = math.degrees(math.atan2(tz, tx))
        d = math.hypot(tx, tz)
        path_strip(b, [ring(L.PLAZA_R - 1.0, a), ring(d - dist, a)], 7.0, k)
        k += 1
    hx, hz = L.HAMMER["head"]
    hd = math.hypot(hx, hz)
    path_strip(b, [ring(L.PLAZA_R - 1.0, 310.0), ring(L.PLAZA_R + 10.0, 314.0), (hx - hx / hd * 26.0, hz - hz / hd * 26.0)], 4.5, 91)


def tufts(b, n=640, seed=5):
    r = random.Random(seed)
    placed = 0
    tries = 0
    while placed < n and tries < n * 12:
        tries += 1
        x, z = r.uniform(-306, 148), r.uniform(-162, 148)
        if VP.land_of(x, z) is None or VP.edge_dist(x, z) < 2.0:
            continue
        d = _zone_dist(x, z)
        if d < 0.5 or (d > 12 and r.random() < 0.55):
            continue                                       # mais tufos perto das construcoes e trilhas
        y = height(x, z)
        base = RB(x, z, y - 0.05)
        s = r.uniform(0.7, 1.3)
        mat = "SN_Tuft" if r.random() < 0.8 else "SN_TuftLight"
        for k in range(5):
            a = r.uniform(0, 2 * math.pi)
            lean = r.uniform(0.25, 0.6)
            h = s * r.uniform(1.0, 1.8)
            tip = base + V((math.cos(a) * lean * h, math.sin(a) * lean * h, h))
            w = 0.22 * s
            side = V((-math.sin(a), math.cos(a), 0)) * w
            bm = bmesh.new()
            v0 = bm.verts.new(base - side)
            v1 = bm.verts.new(base + side)
            v2 = bm.verts.new(base + (tip - base) * 0.55 + side * 0.6 + V((0, 0, 0.05)))
            v3 = bm.verts.new(base + (tip - base) * 0.55 - side * 0.6)
            v4 = bm.verts.new(tip)
            bm.faces.new((v0, v1, v2, v3))
            bm.faces.new((v3, v2, v4))
            b.mesh(bm, mat)
        if r.random() < 0.18:
            for k in range(3):
                c = base + V((r.uniform(-0.6, 0.6), r.uniform(-0.6, 0.6), s * r.uniform(1.0, 1.5)))
                b.sphere(c, 0.22, r.choice(("SN_FlowerBlue", "WB_FlowerWhite", "SN_FlowerYellow")), seg=5)
        placed += 1
    return placed


def build():
    SL.register()
    mats = {"SN_Grass": (118, 170, 72), "SN_Path": (160, 130, 94), "SN_Bank": (128, 104, 80), "SN_ShoreRock": (130, 124, 116),
            "SN_Reed": (120, 150, 70), "SN_Tuft": (100, 156, 64), "SN_TuftLight": (140, 186, 80),
            "SN_FlowerYellow": (240, 210, 90)}
    for k, c in mats.items():
        fm_lib.MATS.setdefault(k, (fm_lib.S(*c), 0.9, 0.0, 0, None, 0.0))
    fm_lib.make_materials()
    b = SL.Build("WB_Ter_Ground", COLL)
    bnds = []
    for (nm, poly, c) in L.LANDS:
        bm, bnd = lawn(poly)
        b.mesh(bm, "SN_Grass")
        bnds.append((bnd, c, nm))
    paths(b)
    objs = b.finish(smooth_angle=60.0)
    b = SL.Build("WB_Ter_Shore", COLL)
    for (bnd, c, nm) in bnds:
        bank(b, bnd, c, seed="bank_" + nm)
    objs += b.finish(smooth_angle=40.0)
    # mar SO DE PREVIA (o jogo ja tem Terrain Water na cota -13; PREVIEW_ nao vai para o export)
    w = SL.Build("PREVIEW_Sea", "00_REFERENCE")
    w.cyl((0, 0, L.Y_WATER - 1.0), (0, 0, L.Y_WATER), 1400.0, "WB_Water", seg=64)
    w.finish()
    t = SL.Build("WB_Veg_Tufts", "09_VEGETATION")
    n = tufts(t)
    objs += t.finish(smooth_angle=179.0)
    # colisao do gramado: faixas horizontais cobrindo cada terra (topo na cota da grama)
    for (nm, poly, c) in L.LANDS:
        zs = [p[1] for p in poly]
        xs_all = [p[0] for p in poly]
        z = min(zs)
        while z < max(zs):
            z1 = min(max(zs), z + 8.0)
            xs = []
            for zz in (z + 0.5, (z + z1) / 2, z1 - 0.5):
                xx = [x for x in range(int(min(xs_all)) - 2, int(max(xs_all)) + 3, 2) if VP._in_poly(x, zz, poly)]
                if xx:
                    xs.append((min(xx), max(xx)))
            if xs:
                x0 = min(a for a, _ in xs)
                x1 = max(c_ for _, c_ in xs)
                fm_lib.col_box("Terrain", (x1 - x0 + 2.0, z1 - z, 4.0), RB((x0 + x1) / 2, (z + z1) / 2, L.Y_GRASS - 2.0),
                               (0, 0, 0))
            z = z1
    print("CHAO: gramado + trilhas + barranco + lago + %d tufos" % n)
    return objs
