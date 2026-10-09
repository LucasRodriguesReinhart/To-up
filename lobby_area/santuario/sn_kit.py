# sn_kit.py - KIT do Santuario: pedra antiga desgastada e as pecas que dao vida as ruinas.
#   worn_block   bloco com chanfro e cantos lascados (corte por plano + tampa)
#   ruin_wall    muro de cantaria com o topo arruinado em blocos de alturas diferentes
#   column       coluna de tambores (base, fuste com junta entre tambores, capitel); pode estar quebrada
#   arch         arco de aduelas sobre 2 pilares (vao w, altura h); pode faltar pedras
#   moss_patch   capa de musgo com contorno irregular sobre uma face de cima
#   ivy          cortina de hera descendo por uma face (folhas achatadas em cachos)
#   chain        corrente de elos ovais em catenaria entre 2 pontos
#   rune_glyphs  runas em relevo (Neon) numa face
#   pickaxe / pickaxe_rack, brazier, crystal_cluster, rubble, flower_bed
# Todas desenham num wb_lib.Build num Frame local Fr (wb_kit). Coordenadas do frame: x ao longo, y para fora/frente,
# z para cima. Escala: jogador 5 studs.
import math
import random
import zlib

import bmesh
from mathutils import Matrix, Vector

import sn_lib as SL
from wb_kit import Fr, bb, bx, beam, cyl, lathe, poly_prism
from wb_house import voussoirs

RAD = math.radians
V = Vector


def rng(*k):
    return random.Random(zlib.crc32(repr(k).encode()))


# ------------------------------------------------------------------ bloco desgastado
def _box_bm(dims, bevel):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.transform(bm, matrix=Matrix.Diagonal(V((*dims, 1.0))), verts=bm.verts[:])
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, offset_type="OFFSET", segments=1, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    return bm


def chip_bm(bm, dims, r, n=2, depth=(0.12, 0.3)):
    """lasca n cantos: plano perto do canto com normal na diagonal (+ ruido), corta e tampa o buraco"""
    hx, hy, hz = dims[0] / 2, dims[1] / 2, dims[2] / 2
    corners = [V((sx * hx, sy * hy, sz * hz)) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    r.shuffle(corners)
    m = min(dims)
    for c in corners[:n]:
        nrm = V((math.copysign(1, c.x) * r.uniform(0.5, 1.0), math.copysign(1, c.y) * r.uniform(0.5, 1.0),
                 math.copysign(1, c.z) * r.uniform(0.5, 1.0))).normalized()
        d = m * r.uniform(*depth)
        co = c - nrm * d * 1.6
        res = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=nrm,
                                     clear_outer=True)
        edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if edges:
            try:
                bmesh.ops.holes_fill(bm, edges=bm.edges[:], sides=0)
            except Exception:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def worn_block(b, F, cx, cy, cz, dims, mat, seed=0, chips=2, bevel=0.12, turn=0.0, tilt=(0.0, 0.0)):
    """bloco de pedra com chanfro e cantos lascados; centro (cx, cy, cz) no frame F; turn/tilt em graus"""
    r = rng("wb", seed, round(cx, 2), round(cy, 2), round(cz, 2))
    bm = _box_bm(dims, bevel)
    if chips:
        chip_bm(bm, dims, r, chips)
    R = F.R() @ Matrix.Rotation(RAD(turn), 3, "Z") @ Matrix.Rotation(RAD(tilt[0]), 3, "X") @ Matrix.Rotation(RAD(tilt[1]), 3, "Y")
    bmesh.ops.transform(bm, matrix=Matrix.Translation(F.p(cx, cy, cz)) @ R.to_4x4(), verts=bm.verts[:])
    b.mesh(bm, mat, axes=[V(R.col[i]).normalized() for i in range(3)], dims=tuple(dims))


# ------------------------------------------------------------------ muro arruinado
def ruin_wall(b, F, x0, x1, z0, h, t, mat, seed=0, ruin=0.45, course=1.6, top_mat=None, moss=True, cap=None):
    """muro de x0 a x1 (frame F, face em y = +t/2), altura base h: o miolo vai ate h*(1-ruin) e o topo e feito de
    blocos com alturas variadas (silhueta arruinada). top_mat = material dos blocos do topo (padrao = mat)."""
    r = rng("wall", seed, x0, x1)
    L = x1 - x0
    hb = h * (1.0 - ruin)
    bb(b, F, x0, x1, -t / 2, t / 2, z0, z0 + hb, mat)
    # blocos do topo em fiadas, alturas da silhueta seguindo um ruido suave
    nx = max(2, int(L / 2.2))
    prof = [hb + (h - hb) * max(0.0, math.sin(math.pi * (k + r.random()) / nx) * r.uniform(0.3, 1.1)) for k in range(nx)]
    for k in range(nx):
        xa = x0 + L * k / nx
        xb = x0 + L * (k + 1) / nx
        ztop = z0 + min(h, prof[k])
        zz = z0 + hb
        row = 0
        while zz < ztop - 0.4:
            hh = min(course, ztop - zz)
            off = (0.5 if row % 2 else 0.0) * (xb - xa)
            for (a, c) in (((xa + off * 0.0), xb),):
                worn_block(b, F, (a + c) / 2, r.uniform(-0.08, 0.08), zz + hh / 2,
                           (c - a - 0.12, t + r.uniform(-0.1, 0.15), hh - 0.08), top_mat or mat, seed=(seed, k, row),
                           chips=1 if r.random() < 0.5 else 0, bevel=0.1)
            zz += hh
            row += 1
        if moss and r.random() < 0.55 and ztop > z0 + hb + 0.3:
            moss_patch(b, F, (xa + xb) / 2, 0.0, ztop + 0.02, (xb - xa) * 0.9, t * 0.9, seed=(seed, k))
    if cap:
        bb(b, F, x0 - 0.2, x1 + 0.2, -t / 2 - 0.25, t / 2 + 0.25, z0 + hb - 0.4, z0 + hb, cap)


# ------------------------------------------------------------------ coluna em tambores
def column(b, F, x, y, z0, h, r0=1.4, mat="SN_Ashlar", base_mat="SN_Ashlar_Dark", seed=0, broken=None, capital=True,
           drums=None, moss=True):
    """coluna: base quadrada + toro, fuste em tambores (juntas 0,06 mais finas), capitel com abaco.
    broken = altura onde a coluna termina quebrada (topo inclinado e irregular)."""
    r = rng("col", seed, round(x, 1), round(y, 1))
    bb(b, F, x - r0 * 1.45, x + r0 * 1.45, y - r0 * 1.45, y + r0 * 1.45, z0, z0 + 0.9, base_mat, bevel=0.1)
    lathe(b, F, x, y, [(r0 * 1.32, 0.0), (r0 * 1.32, 0.25), (r0 * 1.12, 0.6), (r0 * 1.05, 0.7)], base_mat, 16, z0=z0 + 0.9)
    top = z0 + h if broken is None else z0 + broken
    zz = z0 + 1.6
    nd = drums or max(2, int((top - zz) / 3.2))
    dh = (top - zz) / nd
    for k in range(nd):
        za, zc = zz + k * dh, zz + (k + 1) * dh - 0.06
        ra = r0 * (1.0 - 0.06 * (za - z0) / h)
        rc = r0 * (1.0 - 0.06 * (zc - z0) / h)
        off = V((r.uniform(-0.06, 0.06), r.uniform(-0.06, 0.06), 0)) if k else V((0, 0, 0))
        if broken is not None and k == nd - 1:
            # tambor do topo quebrado: prisma com topo inclinado e serrilhado
            n = 12
            pts = []
            tilt = r.uniform(0.6, 1.8)
            a0 = r.uniform(0, 2 * math.pi)
            bm = bmesh.new()
            bot = [bm.verts.new(F.p(x + off.x + ra * math.cos(2 * math.pi * i / n), y + off.y + ra * math.sin(2 * math.pi * i / n), za)) for i in range(n)]
            tp = [bm.verts.new(F.p(x + off.x + rc * math.cos(2 * math.pi * i / n), y + off.y + rc * math.sin(2 * math.pi * i / n),
                                   zc - tilt * (1 + math.cos(2 * math.pi * i / n - a0)) * 0.5 - r.uniform(0, 0.35))) for i in range(n)]
            bm.faces.new(list(reversed(bot)))
            bm.faces.new(tp)
            for i in range(n):
                bm.faces.new((bot[i], bot[(i + 1) % n], tp[(i + 1) % n], tp[i]))
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            b.mesh(bm, mat)
            if moss:
                moss_patch(b, F, x, y, zc - tilt * 0.5, ra * 1.6, ra * 1.6, seed=(seed, "top"), round_=True)
        else:
            cyl(b, F, (x + off.x, y + off.y, za), (x + off.x, y + off.y, zc), ra, mat, seg=16, r1=rc)
    if broken is None and capital:
        lathe(b, F, x, y, [(r0 * 0.96, 0.0), (r0 * 1.15, 0.5), (r0 * 1.35, 1.0), (r0 * 1.38, 1.15)], mat, 16, z0=top)
        bb(b, F, x - r0 * 1.55, x + r0 * 1.55, y - r0 * 1.55, y + r0 * 1.55, top + 1.15, top + 1.85, base_mat, bevel=0.1)
        return top + 1.85
    return top


# ------------------------------------------------------------------ arco de aduelas
def stone_arch(b, F, cx, w, h_spring, depth=2.4, ring=1.5, mat="SN_Ashlar", pier=2.4, pier_mat=None, seed=0,
               missing=(), key_mat=None, moss=True, n=11):
    """arco de meio ponto: 2 pilares (pier x depth) ate a nascenca h_spring + anel de n aduelas; missing = indices
    das aduelas que caiu (ruina). Plano do arco = plano xz do frame, espessura ao longo de y."""
    r = rng("arch", seed, cx)
    rr = w / 2
    pm = pier_mat or mat
    for s in (-1, 1):
        px = cx + s * (rr + pier / 2)
        for k in range(int(h_spring / 1.8) + 1):
            za = k * 1.8
            zc = min(h_spring, za + 1.8)
            if zc - za < 0.2:
                continue
            worn_block(b, F, px + r.uniform(-0.05, 0.05), 0.0, (za + zc) / 2, (pier, depth, zc - za - 0.07), pm,
                       seed=(seed, s, k), chips=1 if r.random() < 0.4 else 0, bevel=0.1)
        bb(b, F, px - pier / 2 - 0.25, px + pier / 2 + 0.25, -depth / 2 - 0.25, depth / 2 + 0.25, h_spring - 0.5, h_spring,
           pier_mat or "SN_Ashlar_Dark")
    for k in range(n):
        if k in missing:
            continue
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        quad = [(cx + (rr + ring) * math.cos(a0), h_spring + (rr + ring) * math.sin(a0)),
                (cx + (rr + ring) * math.cos(a1), h_spring + (rr + ring) * math.sin(a1)),
                (cx + rr * math.cos(a1), h_spring + rr * math.sin(a1)), (cx + rr * math.cos(a0), h_spring + rr * math.sin(a0))]
        bm = bmesh.new()
        v0 = [bm.verts.new(F.p(xq, -depth / 2, zq)) for (xq, zq) in quad]
        v1 = [bm.verts.new(F.p(xq, depth / 2, zq)) for (xq, zq) in quad]
        bm.faces.new(list(reversed(v0)))
        bm.faces.new(v1)
        for i in range(4):
            bm.faces.new((v0[i], v0[(i + 1) % 4], v1[(i + 1) % 4], v1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        c = sum((v.co for v in bm.verts), V()) / len(bm.verts)
        for v in bm.verts:
            v.co = c + (v.co - c) * 0.955
        mt = key_mat if (key_mat and k == n // 2) else mat
        b.mesh(bm, mt, axes=[F.t, F.f, V((0, 0, 1))], dims=(ring, depth, ring))
    if moss:
        moss_patch(b, F, cx, 0.0, h_spring + rr + ring + 0.02, w * 0.5, depth * 0.9, seed=(seed, "am"))
    return h_spring + rr + ring


# ------------------------------------------------------------------ musgo, hera, flores
def moss_patch(b, F, cx, cy, z, sx, sy, seed=0, round_=False, thick=0.28, mat="SN_Moss"):
    """capa de musgo com contorno irregular (poligono suave) e borda caindo um pouco"""
    r = rng("moss", seed, round(cx, 2), round(cy, 2), round(z, 2))
    n = 14
    pts = []
    k1, p1 = r.uniform(2, 4), r.uniform(0, 6.28)
    for i in range(n):
        a = 2 * math.pi * i / n
        f = 0.75 + 0.2 * math.sin(k1 * a + p1) + r.uniform(-0.08, 0.08)
        pts.append((cx + sx / 2 * f * math.cos(a), cy + sy / 2 * f * math.sin(a)))
    poly_prism(b, F, pts, z - 0.05, z + thick, mat)


def ivy(b, F, x, y, z_top, length, width=2.2, seed=0, mat="SN_Ivy"):
    """cortina de hera descendo por uma face (F: face com +y para fora, plano em y): cachos de folhas achatadas"""
    r = rng("ivy", seed, round(x, 1), round(z_top, 1))
    strands = max(2, int(width / 0.9))
    for s in range(strands):
        sx = x - width / 2 + (s + 0.5) * width / strands + r.uniform(-0.2, 0.2)
        ln = length * r.uniform(0.55, 1.0)
        zz = z_top
        while zz > z_top - ln:
            b.sphere(F.p(sx + r.uniform(-0.25, 0.25), y + 0.22, zz), r.uniform(0.42, 0.62), mat, seg=6, scale=(1.0, 0.45, 0.9))
            zz -= r.uniform(0.55, 0.8)


def chain(b, F, a, c, sag, link=1.3, thick=0.32, mat="SN_Chain"):
    """corrente de elos ovais em catenaria simples de a ate c (pontos do frame), alternando 90 graus"""
    a, c = V(a), V(c)
    L = (c - a).length
    n = max(3, int(L / (link * 1.55)))
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a.lerp(c, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for i in range(n):
        p0, p1 = pts[i], pts[i + 1]
        mid = (p0 + p1) / 2
        d = (p1 - p0).normalized()
        up = V((0, 0, 1)) if abs(d.z) < 0.95 else V((1, 0, 0))
        side = d.cross(up).normalized()
        if i % 2:
            side = d.cross(side).normalized()
        bm = bmesh.new()
        segs, rs = 10, 5
        ring = []
        for k in range(segs):
            u = 2 * math.pi * k / segs
            cc = mid + d * (math.cos(u) * link * 0.62) + side * (math.sin(u) * link * 0.36)
            tang = (d * (-math.sin(u) * link * 0.62) + side * (math.cos(u) * link * 0.36)).normalized()
            nrm = tang.cross(d.cross(side).normalized()).normalized()
            bi = tang.cross(nrm).normalized()
            ring.append([bm.verts.new(cc + (nrm * math.cos(2 * math.pi * j / rs) + bi * math.sin(2 * math.pi * j / rs)) * thick)
                         for j in range(rs)])
        for k in range(segs):
            for j in range(rs):
                bm.faces.new((ring[k][j], ring[(k + 1) % segs][j], ring[(k + 1) % segs][(j + 1) % rs], ring[k][(j + 1) % rs]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, mat)


def rune_glyphs(b, Ff, x0, x1, z, h=1.6, n=8, seed=0, mat="SN_Rune", depth=0.16):
    """runas em relevo na face Ff (y = 0 = plano da face): cada uma 3-4 tracos numa grade 3x3"""
    r = rng("runes", seed)
    g3 = (0.0, 0.5, 1.0)
    w = (x1 - x0) / n
    for i in range(n):
        gx0 = x0 + i * w + w * 0.2
        gw = w * 0.6
        for t in range(r.randint(3, 4)):
            ax, az = g3[r.randrange(3)], g3[r.randrange(3)]
            bx_, bz = g3[r.randrange(3)], g3[r.randrange(3)]
            if (ax, az) == (bx_, bz):
                bz = 1.0 if az < 0.5 else 0.0
            pa = (gx0 + ax * gw, depth / 2, z + az * h)
            pc = (gx0 + bx_ * gw, depth / 2, z + bz * h)
            beam(b, Ff, pa, pc, 0.22, depth, mat)


def crystal_cluster(b, F, x, y, z, s=1.0, mat="SN_CrystalBlue", seed=0, n=5):
    """cachos de cristal de minerio saindo da pedra (prismas hexagonais pontudos)"""
    r = rng("cry", seed, round(x, 1), round(y, 1))
    for k in range(n):
        ang = r.uniform(0, 2 * math.pi)
        tilt = r.uniform(0, 35)
        hgt = s * r.uniform(1.6, 3.4)
        rad = s * r.uniform(0.25, 0.5)
        base = F.p(x + math.cos(ang) * s * 0.5, y + math.sin(ang) * s * 0.5, z)
        d = V((math.cos(ang) * math.sin(RAD(tilt)), math.sin(ang) * math.sin(RAD(tilt)), math.cos(RAD(tilt))))
        d = (F.R() @ d).normalized()
        tipb = base + d * hgt * 0.78
        b.cyl(base, tipb, rad, mat, seg=6, r1=rad * 0.95)
        b.cyl(tipb, tipb + d * hgt * 0.22, rad * 0.95, mat, seg=6, r1=0.02)


def rubble(b, F, cx, cy, z, radius, n, mat="SN_Ashlar", seed=0, size=(0.6, 1.8)):
    r = rng("rub", seed, round(cx, 1), round(cy, 1))
    for k in range(n):
        a = r.uniform(0, 2 * math.pi)
        d = radius * math.sqrt(r.random())
        s = r.uniform(*size)
        worn_block(b, F, cx + d * math.cos(a), cy + d * math.sin(a), z + s * 0.3, (s * r.uniform(0.9, 1.6), s, s * 0.8),
                   mat, seed=(seed, k), chips=2, bevel=0.08, turn=r.uniform(0, 90), tilt=(r.uniform(-12, 12), r.uniform(-12, 12)))


def flower_bed(b, F, cx, cy, z, sx, sy, n=18, seed=0, cols=("SN_FlowerBlue", "WB_FlowerWhite", "SN_Petal")):
    r = rng("fl", seed, round(cx, 1), round(cy, 1))
    for k in range(n):
        x = cx + r.uniform(-sx / 2, sx / 2)
        y = cy + r.uniform(-sy / 2, sy / 2)
        hgt = r.uniform(0.6, 1.3)
        b.cyl(F.p(x, y, z), F.p(x + r.uniform(-0.1, 0.1), y + r.uniform(-0.1, 0.1), z + hgt), 0.06, "WB_Leaf", seg=4, caps=False)
        b.sphere(F.p(x, y, z + hgt), r.uniform(0.18, 0.28), r.choice(cols), seg=6, scale=(1, 1, 0.7))
        if r.random() < 0.6:
            b.sphere(F.p(x + r.uniform(-0.3, 0.3), y + r.uniform(-0.3, 0.3), z + 0.25), r.uniform(0.3, 0.45), "WB_Leaf", seg=6,
                     scale=(1, 1, 0.6))


def pickaxe(b, F, x, y, z, turn=0.0, lean=0.0, s=1.0, head="WB_Steel", handle="WB_Timber", gem=None):
    """picareta (o produto do Ignis): cabo + cabeca curva de duas pontas + cinta de couro"""
    Fp = F.sub(x, y, z, turn)
    R = Fp.R() @ Matrix.Rotation(RAD(lean), 3, "X")
    up = R @ V((0, 0, 1))
    side = R @ V((1, 0, 0))
    o = Fp.o
    top = o + up * 4.2 * s
    b.cyl(o, top, 0.16 * s, handle, seg=6)
    b.cyl(o + up * 0.6 * s, o + up * 1.5 * s, 0.2 * s, "WB_LeatherDark", seg=6)
    # cabeca: dois bracos curvos (4 segmentos cada) saindo do olho
    b.box(top, (0.55 * s, 0.5 * s, 0.6 * s), head, rot=R)
    for sg in (-1, 1):
        prev = top
        for k in range(1, 5):
            t = k / 4
            p = top + side * (sg * 1.7 * s * t) - up * (0.55 * s * t * t)
            b.cyl(prev, p, 0.24 * s * (1.0 - 0.7 * t) + 0.04, head, seg=6, r1=0.24 * s * (1.0 - 0.7 * (t + 0.25)) + 0.03)
            prev = p
    if gem:
        b.sphere(top + R @ V((0, 0.28 * s, 0)), 0.18 * s, gem, seg=6)


def pickaxe_rack(b, F, x, y, n=4, seed=0):
    """cavalete de madeira com picaretas expostas (com tipos diferentes de cabeca)"""
    Fr_ = F.sub(x, y, 0, 0)
    w = n * 1.6 + 0.8
    for s in (-1, 1):
        bb(b, Fr_, s * w / 2 - 0.25, s * w / 2 + 0.25, -0.25, 0.25, 0.0, 4.2, "WB_Timber")
    bb(b, Fr_, -w / 2, w / 2, -0.2, 0.2, 3.6, 3.95, "WB_Timber")
    bb(b, Fr_, -w / 2, w / 2, -0.6, 0.6, 0.0, 0.35, "WB_Plank")
    heads = ["WB_Steel", "WB_Iron", "SN_Gold", "WB_Steel", "SN_Bronze"]
    gems = [None, "SN_CrystalBlue", None, "SN_CrystalAmber", None]
    for k in range(n):
        xx = -w / 2 + 0.8 + k * 1.6 + 0.4
        pickaxe(b, Fr_, xx, 0.35, 0.35, turn=0, lean=-12, s=0.85, head=heads[k % 5], gem=gems[k % 5])


def brazier(b, F, x, y, z0=0.0, h=3.4, name=None, fire_r=0.9):
    """braseiro de bronze sobre coluna curta de pedra, com chamas"""
    lathe(b, F, x, y, [(0.9, 0.0), (0.9, 0.4), (0.55, 0.6), (0.45, h - 1.0), (0.7, h - 0.9)], "SN_Ashlar_Dark", 10, z0=z0)
    lathe(b, F, x, y, [(0.6, 0.0), (1.4, 0.5), (1.6, 0.9), (1.5, 1.0), (0.0, 0.3)], "SN_Bronze", 12, z0=z0 + h - 1.0)
    for k in range(4):
        a = k * math.pi / 2 + 0.3
        fh = 1.6 + (k % 2) * 0.5
        lathe(b, F, x + 0.3 * math.cos(a), y + 0.3 * math.sin(a), [(fire_r * 0.6, 0.0), (fire_r * 0.5, fh * 0.45),
                                                                    (fire_r * 0.2, fh * 0.8), (0.0, fh)], "WB_Fire", 6,
              z0=z0 + h - 0.2)
    lathe(b, F, x, y, [(fire_r * 0.5, 0.0), (fire_r * 0.3, 0.8), (0.0, 1.3)], "WB_FireCore", 6, z0=z0 + h - 0.15)
    if name:
        import fm_lib
        fm_lib.light(name, "POINT", F.p(x, y, z0 + h + 1.0), 700.0, (1.0, 0.6, 0.28), 0.7)
        fm_lib.marker("VFX_Brazier_" + name.split("_")[-1], F.p(x, y, z0 + h + 0.4), (0, 0, 0), 1.0, "PLAIN_AXES",
                      "15_GAMEPLAY_MARKERS", {"particle": "fire", "rate": 8, "size": 1.6})
