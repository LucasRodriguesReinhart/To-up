# sn_hero.py - PECA-HEROI do Santuario: plinto escalonado + BIGORNA-TITA (basalto rachado com lava viva por dentro,
# musgo, hera, correntes, runas acesas), o MARTELO quebrado do deus cravado a noroeste, a FORJA DO IGNIS (abside de
# pedra aberta para a praca: colunas, arco-costela quebrado, lareira alimentada por um canal de lava que desce da
# bigorna, foles gigantes, ferramentas, picaretas a venda) e a PRACA DAS RUNAS.
# Contrato do Ignis: Root (-0.9, 7, -60.7) olhando +Z; envoltoria X -9.9..6.1 / Y 7..31 / Z -64.7..-52.7 livre;
# chao plano na cota 7 de z -52.7 a -40.
import math
import random

import bmesh
from mathutils import Matrix, Vector

import fm_lib
import sn_lib as SL
import sn_layout as L
from sn_kit import (worn_block, chip_bm, ruin_wall, column, stone_arch, moss_patch, ivy, chain, rune_glyphs,
                    crystal_cluster, rubble, flower_bed, pickaxe_rack, brazier, rng)
from wb_kit import Fr, bb, bx, beam, cyl, lathe, poly_prism, text, barrel, crate, sack, banner
from wb_lib import RB

RAD = math.radians
V = Vector
Y0 = L.Y_PLAZA
HS = -1.0                      # chifre da bigorna para o LESTE (x local negativo no frame que olha para o sul)


def loft_x(b, F, secs, mat, n=16):
    """loft ao longo de x do frame: secoes (x, z_centro, raio_y, raio_cima, raio_baixo) -> malha fechada"""
    bm = bmesh.new()
    rings = []
    for (x, zc_, ry, rt, rb) in secs:
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n
            cz, cy = math.sin(a), math.cos(a)
            rz = rt if cz >= 0 else rb
            ring.append(bm.verts.new(F.p(x, ry * cy, zc_ + rz * cz)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, mat)


def extrude_xz(b, F, pts, y0, y1, mat, bevel=0.0):
    """poligono no plano (x, z) do frame extrudado de y0 a y1 (perfil lateral da bigorna)"""
    bm = bmesh.new()
    a = [bm.verts.new(F.p(x, y0, z)) for (x, z) in pts]
    c = [bm.verts.new(F.p(x, y1, z)) for (x, z) in pts]
    n = len(pts)
    bm.faces.new(a)
    bm.faces.new(list(reversed(c)))
    for i in range(n):
        bm.faces.new((a[i], c[i], c[(i + 1) % n], a[(i + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, offset_type="OFFSET", segments=1, affect="EDGES",
                        clamp_overlap=True)
    b.mesh(bm, mat, axes=[F.t, F.f, V((0, 0, 1))], dims=(1.0, 1.0, 1.0))


def lava_strip(b, F, pts, w=0.9, depth=0.35, core=True):
    """fio de lava ao longo de uma polilinha (pontos no frame): faixa Neon + nucleo mais claro"""
    for p0, p1 in zip(pts, pts[1:]):
        beam(b, F, p0, p1, w, depth, "SN_Lava")
        if core:
            q0 = (p0[0], p0[1] + depth * 0.45, p0[2])
            q1 = (p1[0], p1[1] + depth * 0.45, p1[2])
            beam(b, F, q0, q1, w * 0.45, depth * 0.4, "SN_LavaHot")


# ------------------------------------------------------------------ plinto + bigorna-tita
def anvil(coll="04_FORGE"):
    b = SL.Build("WB_Frg_Anvil", coll)
    ax, az = L.ANVIL_C
    F = Fr.rbx(ax, az, Y0, 0.0, 1.0)              # +y = sul (para a praca), +x = oeste
    x0, x1, z0, z1, ph = L.ANVIL_PLINTH
    ya, yb = z0 - az, z1 - az                     # -24 .. 26
    # plinto em 3 degraus: fiadas de cantaria escura + friso entalhado no do meio + capa clara
    tiers = [(0.0, 2.2, 0.0, "SN_Ashlar_Dark"), (2.2, 4.2, 3.0, "SN_Carved"), (4.2, ph, 6.0, "SN_Ashlar")]
    for (za, zc, ins, m) in tiers:
        bb(b, F, x0 + ins, x1 - ins, ya + ins, yb - ins, za, zc, m)
        bb(b, F, x0 + ins - 0.3, x1 - ins + 0.3, ya + ins - 0.3, yb - ins + 0.3, zc - 0.35, zc, "SN_Ashlar_Dark")
    # escadaria central na frente do plinto (sobe para o pe da bigorna)
    for k in range(10):
        zz = (k + 1) * ph / 10
        yy = yb + 3.0 - k * 0.3 - 0.3
        bb(b, F, -9.0, 9.0, yy - 0.3 - (9 - k) * 0.0, yb + 3.0 - k * 0.3, 0.0, zz, "SN_Ashlar") if False else None
    st_n, st_h, st_run = 10, ph / 10, 1.1
    for k in range(st_n):
        y_front = yb + st_n * st_run - k * st_run
        bb(b, F, -10.0, 10.0, yb - 1.0, y_front, k * st_h, (k + 1) * st_h, "SN_Ashlar" if k % 2 else "SN_Ashlar_Dark")
    # cantos do plinto: blocos tombados e musgo
    r = rng("plinth", 1)
    for (cx, cy) in ((x0 + 3, ya + 3), (x1 - 3, ya + 3), (x0 + 3, yb - 3), (x1 - 3, yb - 3)):
        moss_patch(b, F, cx, cy, ph + 0.01, 7.0, 5.0, seed=("pm", cx, cy))
    rubble(b, F, x1 + 3, yb + 4, 0.0, 6.0, 9, "SN_Ashlar", seed=11)
    rubble(b, F, x0 - 3, yb + 2, 0.0, 5.0, 7, "SN_Ashlar_Dark", seed=12)
    # ----- bigorna (sobre o plinto, z local a partir de ph)
    Z = ph
    # pes: dois blocos alargados nas pontas + ponte rebaixada (arco por baixo)
    for s in (-1, 1):
        extrude_xz(b, F, [(s * 22, Z), (s * 47, Z), (s * 44, Z + 7.5), (s * 24, Z + 8)] if s > 0 else
                   [(s * 47, Z), (s * 22, Z), (s * 24, Z + 8), (s * 44, Z + 7.5)], -22.0, 22.0, "SN_Iron", bevel=0.5)
    extrude_xz(b, F, [(-23, Z + 3.5), (23, Z + 3.5), (23, Z + 8.2), (-23, Z + 8.2)], -16.0, 16.0, "SN_Iron", bevel=0.4)
    # cintura com laterais concavas
    prof = []
    for k in range(9):
        t = k / 8.0
        z = Z + 7.5 + 23.0 * t
        w = 26.5 + 8.5 * (1 - t) ** 2.2 + 2.2 * t ** 3
        prof.append((w, z))
    waist = [(-prof[0][0], prof[0][1])] + [(w, z) for (w, z) in prof] + [(-w, z) for (w, z) in reversed(prof)][:-1]
    extrude_xz(b, F, waist, -14.0, 14.0, "SN_Iron", bevel=0.5)
    # corpo partido por uma racha diagonal larga com lava funda dentro (lado A e lado B)
    zc0, zc1 = Z + 30.0, Z + 47.5
    crack = [(6.5, zc1), (2.8, Z + 44.0), (6.0, Z + 40.2), (1.2, Z + 35.6), (3.8, zc0)]
    gap = 1.55
    A = [(-41, zc0)] + [(x - gap, z) for (x, z) in reversed(crack)] + [(-41, zc1)]
    Bp = [(crack[0][0] + gap, zc1)] + [(x + gap, z) for (x, z) in crack[1:]] + [(41, zc0), (41, zc1)]
    extrude_xz(b, F, A, -17.0, 17.0, "SN_Iron", bevel=0.6)
    extrude_xz(b, F, Bp, -17.0, 17.0, "SN_Iron", bevel=0.6)
    # lava no fundo da racha (recuada 1 stud) + nucleo claro + brasas presas nas bordas
    extrude_xz(b, F, [(x - gap * 0.9, z) for (x, z) in crack] + [(x + gap * 0.9, z) for (x, z) in reversed(crack)],
               -15.6, 15.6, "SN_Lava")
    extrude_xz(b, F, [(x - 0.45, z) for (x, z) in crack] + [(x + 0.45, z) for (x, z) in reversed(crack)], -15.9, 15.9,
               "SN_LavaHot")
    rr0 = rng("embers")
    for (x, z) in crack:
        for yy in (16.9, -16.9):
            b.sphere(F.p(x + rr0.uniform(-0.6, 0.6), yy, z + rr0.uniform(-0.8, 0.8)), rr0.uniform(0.25, 0.45), "SN_LavaHot", seg=6)
    # rachaduras menores ramificando pela superficie (fios de lava embutidos, quebrados em zigue-zague)
    def fissure(pts, yy, w=0.5):
        for p0, p1 in zip(pts, pts[1:]):
            beam(b, F, (p0[0], yy, p0[1]), (p1[0], yy, p1[1]), w, 0.42, "SN_Lava")
    for yy in (16.92, -16.92):
        fissure([(1.2, Z + 35.6), (-4.0, Z + 34.0), (-7.5, Z + 35.4), (-12.0, Z + 33.2)], yy)
        fissure([(6.0, Z + 40.2), (10.5, Z + 41.8), (13.0, Z + 40.6), (17.5, Z + 42.4)], yy, 0.42)
        fissure([(3.8, zc0), (5.0, Z + 27.0), (3.6, Z + 24.0)], yy * 14.25 / 16.92, 0.45)
    # mesa (face) grossa com chanfro largo e quinas lascadas; chapa de ferro gasto por cima
    face_cx = -3.0
    worn_block(b, F, face_cx, 0.0, zc1 + 4.5, (98.0, 38.0, 9.0), "SN_Iron", seed="face", chips=4, bevel=1.1)
    worn_block(b, F, -1.0, 0.0, zc1 + 9.25, (84.0, 33.0, 0.9), "WB_Iron", seed="plate", chips=3, bevel=0.3)
    for (hx, hw) in ((-45.0, 3.4), (-38.5, 1.7)):
        bb(b, F, hx - hw / 2, hx + hw / 2, -hw / 2, hw / 2, zc1 + 7.0, zc1 + 9.75, "WB_Dark")
        bb(b, F, hx - hw / 2 + 0.3, hx + hw / 2 - 0.3, -hw / 2 + 0.3, hw / 2 - 0.3, zc1 + 7.0, zc1 + 9.4, "SN_LavaHot")
    # pedaco arrancado do calcanhar (fica no plinto) e borda queimada no lugar
    worn_block(b, F, 50.0, 16.5, ph + 2.4, (7.0, 6.0, 4.6), "SN_Iron", seed="heelchunk", chips=4, bevel=0.5, turn=-20,
               tilt=(8, 16))
    # CHIFRE moldado: secoes elipticas da raiz (funda, encaixada no corpo) ate a ponta quebrada, curvando para cima
    secs = []
    for k in range(15):
        t = k / 14.0
        x = -40.0 - 40.0 * t
        zc_ = zc1 + 3.4 + 4.0 * t * t
        ry = 13.0 * (1 - t) ** 1.1 + 1.6
        rt = 5.6 * (1 - t) ** 0.9 + 1.4
        rb = 16.0 * (1 - t) ** 1.6 + 1.4
        secs.append((x, zc_, ry, rt, rb))
    loft_x(b, F, secs, "SN_Iron", n=18)
    worn_block(b, F, -66.0, 14.0, ph + 1.6, (6.5, 4.5, 3.2), "SN_Iron", seed="tip", chips=4, bevel=0.4, turn=25, tilt=(10, -14))
    # cintas de bronze rebitadas na cintura e no topo da cintura
    for zz, half in ((Z + 9.0, 34.0), (Z + 29.0, 28.5)):
        for yy in (14.2, -14.2):
            beam(b, F, (-half, yy, zz), (half, yy, zz), 1.8, 0.55, "SN_Bronze")
            for k in range(9):
                xx = -half + 2.0 + k * (2 * half - 4.0) / 8
                b.sphere(F.p(xx, yy + 0.3 * (1 if yy > 0 else -1), zz), 0.32, "SN_Gold", seg=6)
    # runas acesas numa faixa entalhada no corpo
    for yy, sgn in ((17.05, 1), (-17.05, -1)):
        bb(b, F, -38.0, -2.0, yy - 0.02 * sgn, yy + 0.18 * sgn, zc0 + 5.0, zc0 + 9.6, "SN_Ashlar_Dark") if False else None
    Ff = Fr(F.p(0, 17.0, 0), (F.f.x, F.f.y))
    rune_glyphs(b, Ff, -36.0, -6.0, zc0 + 7.2, h=3.2, n=6, seed="rA", depth=0.3)
    rune_glyphs(b, Ff, 12.5, 36.0, zc0 + 7.2, h=3.2, n=5, seed="rB", depth=0.3)
    Fb = Fr(F.p(0, -17.0, 0), (-F.f.x, -F.f.y))
    rune_glyphs(b, Fb, -36.0, -12.0, zc0 + 7.2, h=3.2, n=5, seed="rC", depth=0.3)
    rune_glyphs(b, Fb, 6.0, 36.0, zc0 + 7.2, h=3.2, n=6, seed="rD", depth=0.3)
    # PAINEIS FORJADOS nas laterais do corpo (moldura em relevo + parafusos de bronze nos cantos e no meio)
    for yy, sgn in ((17.0, 1), (-17.0, -1)):
        for (pa, pb) in ((-39.0, -3.2), (9.6, 39.0)):
            za_, zb_ = zc0 + 1.5, zc1 - 1.5
            for zz in (za_, zb_):
                beam(b, F, (pa, yy + sgn * 0.25, zz), (pb, yy + sgn * 0.25, zz), 0.7, 1.3, "SN_Iron")
            for xx in (pa, pb):
                beam(b, F, (xx, yy + sgn * 0.25, za_ - 0.65), (xx, yy + sgn * 0.25, zb_ + 0.65), 1.3, 0.7, "SN_Iron")
            for (qx, qz) in ((pa, za_), (pb, za_), (pa, zb_), (pb, zb_), ((pa + pb) / 2, za_), ((pa + pb) / 2, zb_)):
                cyl(b, F, (qx, yy, qz), (qx, yy + sgn * 0.95, qz), 0.95, "SN_Bronze", seg=8, r1=0.62)
    # SELO RUNICO na cintura (frente e tras): aro de bronze + raios + runa central acesa
    for yy, sgn in ((14.0, 1), (-14.0, -1)):
        cx_, cz_ = -14.0, Z + 18.5
        rr_, n_ = 6.2, 20
        for k in range(n_):
            a0 = 2 * math.pi * k / n_
            a1 = 2 * math.pi * (k + 1) / n_
            beam(b, F, (cx_ + rr_ * math.cos(a0), yy + sgn * 0.3, cz_ + rr_ * math.sin(a0)),
                 (cx_ + rr_ * math.cos(a1), yy + sgn * 0.3, cz_ + rr_ * math.sin(a1)), 0.7, 0.9, "SN_Bronze")
        for k in range(6):
            a0 = 2 * math.pi * k / 6 + 0.26
            beam(b, F, (cx_ + 2.2 * math.cos(a0), yy + sgn * 0.12, cz_ + 2.2 * math.sin(a0)),
                 (cx_ + (rr_ - 0.8) * math.cos(a0), yy + sgn * 0.12, cz_ + (rr_ - 0.8) * math.sin(a0)), 0.3, 0.42,
                 "SN_Rune")
        cyl(b, F, (cx_, yy, cz_), (cx_, yy + sgn * 0.5, cz_), 1.9, "SN_Rune", seg=12)
        cyl(b, F, (cx_, yy, cz_), (cx_, yy + sgn * 0.35, cz_), 2.5, "SN_Bronze", seg=12)
        # segundo selo menor do outro lado da racha
        cx2 = 18.0
        for k in range(14):
            a0 = 2 * math.pi * k / 14
            a1 = 2 * math.pi * (k + 1) / 14
            beam(b, F, (cx2 + 4.0 * math.cos(a0), yy + sgn * 0.3, cz_ + 4.0 * math.sin(a0)),
                 (cx2 + 4.0 * math.cos(a1), yy + sgn * 0.3, cz_ + 4.0 * math.sin(a1)), 0.6, 0.7, "SN_Bronze")
        cyl(b, F, (cx2, yy, cz_), (cx2, yy + sgn * 0.45, cz_), 1.3, "SN_Rune", seg=10)
    # parafusos grandes ao longo da mesa (frente e tras) e cantoneiras de bronze nas quinas da mesa
    for yy, sgn in ((19.0, 1), (-19.0, -1)):
        for k in range(11):
            xx = face_cx - 45.0 + k * 9.0
            cyl(b, F, (xx, yy, zc1 + 4.5), (xx, yy + sgn * 0.9, zc1 + 4.5), 1.05, "SN_Bronze", seg=8, r1=0.7)
    for (qx, qy) in ((face_cx - 49.0, 19.0), (face_cx - 49.0, -19.0), (face_cx + 49.0, 19.0), (face_cx + 49.0, -19.0)):
        sx_ = 1 if qx > face_cx else -1
        sy_ = 1 if qy > 0 else -1
        bb(b, F, qx - sx_ * 4.0, qx + sx_ * 0.35, qy - sy_ * 4.0, qy + sy_ * 0.35, zc1 + 0.2, zc1 + 9.0, "SN_Bronze")
    # pes: sapatas de bronze nas pontas
    for s_ in (-1, 1):
        bb(b, F, s_ * 47.4, s_ * 43.0, -22.4, 22.4, Z, Z + 2.2, "SN_Bronze")
    # musgo na mesa e nos pes, hera descendo pela frente
    moss_patch(b, F, -12.0, 2.0, zc1 + 9.72, 40.0, 26.0, seed="mesa", thick=0.5)
    moss_patch(b, F, 28.0, -6.0, zc1 + 9.72, 16.0, 14.0, seed="mesa2", thick=0.45)
    for s in (-1, 1):
        moss_patch(b, F, s * 35.0, 0.0, Z + 8.0, 18.0, 36.0, seed=("pe", s), thick=0.4)
    Fiv = Fr(F.p(0, 19.0, 0), (F.f.x, F.f.y))
    for (x, ln, wd) in ((-26.0, 13.0, 4.0), (-2.0, 8.0, 3.0), (22.0, 15.0, 5.0), (40.0, 10.0, 3.2)):
        ivy(b, Fiv, x, 0.0, zc1 + 8.8, ln, wd, seed=("iv", x))
    # correntes: do chifre e do calcanhar ate argolas no plinto (pontos convertidos para o mundo)
    for (pa, pc, sag) in (((-52.0, 8.0, zc1 + 2.0), (-62.0, 20.0, ph + 0.6), 6.0),
                          ((-46.0, 13.0, zc1 + 1.0), (-38.0, 24.0, ph + 0.6), 5.0),
                          ((44.0, 15.0, zc1 + 1.0), (54.0, 24.0, ph + 0.6), 6.5)):
        chain(b, F, F.p(*pa), F.p(*pc), sag)
    for (xx, yy) in ((-62.0, 20.0), (-38.0, 24.0), (54.0, 24.0)):
        lathe(b, F, xx, yy, [(1.4, 0.0), (1.4, 0.6), (0.9, 0.9), (0.0, 0.9)], "SN_Ashlar_Dark", 10, z0=ph)
    # lava escorrendo da racha: desce pela cintura, pelos pes e pelos degraus do plinto ate o canal
    xs = 3.8
    pts = [(xs, 14.9, zc0 + 0.3), (xs + 0.6, 14.9, Z + 22.0), (xs - 0.4, 14.9, Z + 14.0), (xs + 0.2, 14.9, Z + 8.0),
           (xs + 0.2, 22.4, Z + 7.6), (xs, 22.4, Z + 0.4), (xs, 26.4, ph - 0.2), (xs, 26.4, 0.3)]
    lava_strip(b, F, pts, w=1.6, depth=0.55)
    # cristais de minerio brotando do plinto
    for (cx, cy, m) in ((x0 + 8, yb - 1.0, "SN_CrystalBlue"), (x1 - 10, yb - 1.0, "SN_CrystalAmber"), (x0 + 24, ya + 1, "SN_CrystalBlue")):
        crystal_cluster(b, F, cx, cy, ph, 1.6, m, seed=(cx, cy))
    # braseiros nos cantos da frente do plinto
    brazier(b, F, x0 + 4.0, yb - 3.0, ph, 3.6, "L_SN_Brazier_AnvilW")
    brazier(b, F, x1 - 4.0, yb - 3.0, ph, 3.6, "L_SN_Brazier_AnvilE")
    objs = b.finish()
    # colisao
    c = F.p(0, 0, 0)
    for (za, zc, ins) in ((0.0, 2.2, 0.0), (2.2, 4.2, 3.0), (4.2, ph, 6.0)):
        fm_lib.col_box("Anvil", (x1 - x0 - 2 * ins, yb - ya - 2 * ins, zc - za), F.p((x0 + x1) / 2, (ya + yb) / 2, (za + zc) / 2),
                       (0, 0, F.yaw()))
    fm_lib.col_box("Anvil", (94, 44, 8), F.p(0, 0, Z + 4), (0, 0, F.yaw()))
    fm_lib.col_box("Anvil", (60, 28, 23), F.p(0, 0, Z + 19), (0, 0, F.yaw()))
    fm_lib.col_box("Anvil", (98, 38, 26.5), F.p(face_cx, 0, zc0 + 13.25), (0, 0, F.yaw()))
    fm_lib.light("L_SN_AnvilCrack", "POINT", F.p(3.5, 19.0, zc0 + 8.0), 1800.0, (1.0, 0.45, 0.15), 2.0)
    fm_lib.marker("VFX_Anvil_Embers", F.p(3.5, 18.0, zc0 + 10.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "ember", "rate": 10})
    fm_lib.marker("VFX_Anvil_Smoke", F.p(3.5, 0.0, zc1 + 10.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "smoke_thin", "rate": 2})
    return objs


# ------------------------------------------------------------------ martelo do deus, cravado
def hammer(coll="04_FORGE"):
    b = SL.Build("WB_Frg_Hammer", coll)
    hx, hz = L.HAMMER["head"]
    F = Fr.rbx(hx, hz, Y0, 0.0, 1.0)
    sx, sy, sz = L.HAMMER["head_size"]
    yaw = L.HAMMER["yaw"]
    tilt = L.HAMMER["tilt"]
    # cabeca meio enterrada: inclinada, com faces chanfradas e cintas de bronze
    Fh = F.sub(0, 0, 0, yaw)
    Rh = Fh.R() @ Matrix.Rotation(RAD(-18), 3, "Y")
    cz = sz * 0.22
    import sn_kit
    bmh = sn_kit._box_bm((sx, sy, sz), 1.2)
    sn_kit.chip_bm(bmh, (sx, sy, sz), rng("hh"), 3)
    bmesh.ops.transform(bmh, matrix=Matrix.Translation(Fh.p(0, 0, cz)) @ Rh.to_4x4(), verts=bmh.verts[:])
    b.mesh(bmh, "SN_Iron", axes=[V(Rh.col[i]).normalized() for i in range(3)], dims=(sx, sy, sz))
    for k, xx in enumerate((-sx * 0.36, sx * 0.36)):
        c = Fh.o + Rh @ V((xx, 0, 0)) + V((0, 0, cz))
        b.box(c, (2.2, sy + 0.8, sz + 0.8), "SN_Bronze", rot=Rh, bevel=0.3)
    for sgn in (-1, 1):                                       # faces de batida (blocos ressaltados nas pontas)
        c = Fh.o + Rh @ V((sgn * (sx / 2 + 0.6), 0, 0)) + V((0, 0, cz))
        b.box(c, (1.4, sy * 0.86, sz * 0.86), "WB_Iron", rot=Rh, bevel=0.5)
    # runas acesas na lateral da cabeca voltada para a praca
    Fr_h = Fr(Fh.o + Rh @ V((0, -sy / 2 - 0.05, 0)) + V((0, 0, cz)), tuple((Rh @ V((0, -1, 0)))[:2]))
    rune_glyphs(b, Fr_h, -sx * 0.25, sx * 0.25, -2.2, h=4.0, n=4, seed="hr", depth=0.3)
    # cabo: sai do olho da cabeca para cima e para o lado, inclinado
    eye = Fh.o + Rh @ V((0, 0, sz * 0.5)) + V((0, 0, cz))
    d = (Fh.R() @ V((0.0, -math.cos(RAD(tilt)), math.sin(RAD(tilt))))).normalized()
    Lh = L.HAMMER["handle_len"]
    rr = L.HAMMER["handle_r"]
    end = eye + d * Lh
    b.cyl(eye - d * 2.0, eye + d * Lh * 0.5, rr * 1.06, "SN_WoodAged", seg=16, r1=rr * 0.96)
    b.cyl(eye + d * Lh * 0.5, end, rr * 0.96, "SN_WoodAged", seg=16, r1=rr * 0.88)
    # colar de bronze na saida do olho + segundo colar com runas
    b.cyl(eye - d * 0.5, eye + d * 2.6, rr * 1.42, "SN_Bronze", seg=16, r1=rr * 1.3)
    b.cyl(eye + d * 2.6, eye + d * 3.4, rr * 1.2, "SN_Gold", seg=16)
    for t in (0.30, 0.42):
        p = eye + d * Lh * t
        b.cyl(p, p + d * 1.2, rr * 1.16, "SN_Bronze", seg=16)
    # punho: enrolamento de couro em espiral (faixas inclinadas)
    side = d.cross(V((0, 0, 1))).normalized()
    up2 = side.cross(d).normalized()
    t0, t1 = 0.56, 0.86
    nw = 16
    for k in range(nw):
        tA = t0 + (t1 - t0) * k / nw
        tB = t0 + (t1 - t0) * (k + 0.85) / nw
        for j in range(10):
            a0 = 2 * math.pi * j / 10
            a1 = 2 * math.pi * (j + 1) / 10
            pa = eye + d * Lh * (tA + (tB - tA) * j / 10) + (side * math.cos(a0) + up2 * math.sin(a0)) * rr * 0.98
            pb = eye + d * Lh * (tA + (tB - tA) * (j + 1) / 10) + (side * math.cos(a1) + up2 * math.sin(a1)) * rr * 0.98
            b.beam(pa, pb, 0.55, 1.5, "WB_LeatherDark")
    # pomo: anel + esfera achatada de bronze com gema ambar
    b.cyl(end - d * 0.8, end + d * 1.4, rr * 1.3, "SN_Bronze", seg=16, r1=rr * 1.1)
    b.cyl(end + d * 1.4, end + d * 2.6, rr * 1.1, "SN_Gold", seg=16, r1=rr * 0.6)
    b.sphere(end + d * 3.0, rr * 0.55, "SN_CrystalAmber", seg=10)
    # cratera de impacto: anel de lajes partidas e terra em volta da cabeca
    for k in range(16):
        a = 2 * math.pi * k / 16
        rad = sx * 0.62 + (k % 3) * 1.5
        worn_block(b, F, rad * math.cos(a), rad * math.sin(a), 0.4, (4.0, 3.0, 1.4), "SN_Plaza", seed=("cr", k), chips=2,
                   turn=math.degrees(a) + 20, tilt=(math.cos(a) * 18, math.sin(a) * 18))
    rubble(b, F, 0, 0, 0.0, sx * 0.7, 18, "SN_Ashlar", seed="hamrub")
    # rachaduras de lava irradiando do impacto pelo chao (fios Neon rente ao gramado, em zigue-zague)
    rc = rng("hamcrack")
    for k in range(7):
        a = 2 * math.pi * k / 7 + rc.uniform(-0.2, 0.2)
        rad = sx * 0.55
        pts_ = []
        for j in range(5):
            rad += rc.uniform(3.0, 5.5)
            aa = a + rc.uniform(-0.18, 0.18)
            pts_.append((rad * math.cos(aa), rad * math.sin(aa), 0.06))
        for p0, p1 in zip(pts_, pts_[1:]):
            w_ = 0.7 * (1 - pts_.index(p0) / 5.0) + 0.2
            beam(b, F, p0, p1, w_, 0.16, "SN_Lava")
    moss_patch(b, F, 2.0, 0.0, sz * 0.62 + cz, sx * 0.5, sy * 0.6, seed="hm", thick=0.4)
    ivy(b, Fr(eye + d * Lh * 0.35 + V((0, 0, 0)), (F.f.x, F.f.y)), 0, 0, 0, 10, 3.0, seed="hiv")
    flower_bed(b, F, sx * 0.4, sy * 0.9, 0.1, 10, 6, 22, seed="hfl")
    objs = b.finish()
    fm_lib.col_box("Hammer", (sx * 0.9, sy * 0.9, sz * 0.7), F.p(0, 0, sz * 0.35), (0, 0, F.yaw() + RAD(yaw)))
    mid = eye + d * Lh * 0.5
    fm_lib.col_box("Hammer", (rr * 2, rr * 2, Lh), mid, (0, -0.0, 0)) if False else None
    return objs


# ------------------------------------------------------------------ forja do Ignis (abside)
def forge(coll="04_FORGE"):
    b = SL.Build("WB_Frg_Hall", coll)
    fx, fz = L.FORGE_C
    F = Fr.rbx(fx, fz, Y0, 0.0, 1.0)
    r_in, r_out = L.FORGE_R
    t = r_out - r_in
    rm = (r_in + r_out) / 2
    a_open0, a_open1 = L.FORGE_OPEN

    def polar(rad, ang):
        """angulo Roblox (atan2(dz,dx)) -> ponto local do frame (x = oeste, y = sul)"""
        a = math.radians(ang)
        X, Zr = rad * math.cos(a), rad * math.sin(a)
        return -X, Zr                                        # x local = -X Roblox, y local = +Z Roblox

    # piso: disco de lajes escuras + soleira ate a praca
    pts = [polar(r_out + 1.0, a) for a in range(0, 360, 10)]
    poly_prism(b, F, pts, -0.6, 0.02, "SN_Ashlar_Dark")
    bb(b, F, -14.0, 14.0, 14.0, 22.4, -0.6, 0.02, "SN_Ashlar_Dark")
    # muro da abside em segmentos retos ao longo do arco fechado (155 -> 385 graus), topo arruinado
    a = a_open1
    seg = 0
    while a < a_open0 + 360 - 1e-6:
        a2 = min(a + 13.0, a_open0 + 360)
        p0, p1 = polar(rm, a), polar(rm, a2)
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) + 0.35
        ang = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
        Fw = Fr(F.p(mx, my, 0), (math.cos(math.radians(ang + 90)) * F.t.x + math.sin(math.radians(ang + 90)) * F.f.x,
                                   math.cos(math.radians(ang + 90)) * F.t.y + math.sin(math.radians(ang + 90)) * F.f.y))
        hgt = 11.0 if 240 < (a % 360) < 300 else 8.5
        ruin_wall(b, Fw, -ln / 2, ln / 2, 0.0, hgt, t, "SN_Ashlar", seed=("apse", seg), ruin=0.4, course=1.5)
        a = a2
        seg += 1
    # colunas: duas na boca (155/25) e duas no fundo (210/330), altas, com capitel
    col_top = 26.0
    for ang in (a_open1, a_open0, 212.0, 328.0):
        px, py = polar(rm, ang)
        column(b, F, px, py, 0.0, col_top, r0=1.7, seed=("fc", ang))
    # arco-costela quebrado ligando as colunas do fundo (atras do Ignis, fora da envoltoria)
    p210, p330 = polar(rm, 212.0), polar(rm, 328.0)
    span = abs(p210[0] - p330[0])
    Fa = Fr(F.p(0.0, p210[1], 0), (F.f.x, F.f.y))
    stone_arch(b, Fa.sub(0, 0, col_top + 1.85, 0), 0.0, span - 4.2, 0.0, depth=2.6, ring=1.8, mat="SN_Ashlar",
               pier=0.01, seed="rib", missing=(7, 8), moss=True) if False else None
    _rib(b, Fa, span, col_top + 1.85)
    # lintel com a placa na boca da abside (acima da envoltoria: Y >= 33)
    pa, pb = polar(rm, a_open1), polar(rm, a_open0)
    Fl = Fr(F.p(0.0, pa[1], 0), (F.f.x, F.f.y))
    bb(b, Fl, pa[0] - 1.8, pb[0] + 1.8, -1.3, 1.3, col_top + 1.85, col_top + 4.0, "SN_Ashlar_Dark") if pa[0] > pb[0] else \
        bb(b, Fl, pb[0] - 1.8, pa[0] + 1.8, -1.3, 1.3, col_top + 1.85, col_top + 4.0, "SN_Ashlar_Dark")
    bb(b, Fl, -9.0, 9.0, 1.3, 1.7, col_top + 4.2, col_top + 7.4, "SN_WoodAged")
    for zz in (col_top + 4.2, col_top + 7.1):
        bb(b, Fl, -9.3, 9.3, 1.2, 1.85, zz - 0.15, zz + 0.3, "SN_Bronze")
    text(b, Fl, "FORJA DO IGNIS", 1.25, "SN_Gold", 0.0, 1.72, col_top + 5.8, 0.15, bold=True)
    for s in (-1, 1):
        beam(b, Fl, (s * 6.0, 1.5, col_top + 4.0), (s * 6.0, 1.5, col_top + 4.25), 0.2, 0.2, "SN_Chain")
    # estandartes nas colunas da boca
    for ang, col in ((a_open1, "WB_Cloth_Red"), (a_open0, "WB_Cloth_Red")):
        px, py = polar(rm, ang)
        Fb = Fr(F.p(px, py + 1.95, 0), (F.f.x, F.f.y))
        banner(b, Fb, 0.0, 0.0, 22.0, col, 3.0, 9.0)
    # LAREIRA no fundo: bacia de pedra com brasa e fogo, alimentada pelo canal de lava que vem da bigorna
    hy = -12.0                                               # y local da lareira (norte = -y)
    lathe(b, F, 0.0, hy, [(4.2, 0.0), (4.4, 1.0), (4.0, 1.6), (3.3, 1.6), (3.3, 0.9), (0.0, 0.9)], "SN_Ashlar_Dark", 18)
    cyl(b, F, (0, hy, 0.9), (0, hy, 1.25), 3.3, "SN_Lava", seg=18)
    cyl(b, F, (0, hy, 1.25), (0, hy, 1.45), 2.2, "SN_LavaHot", seg=14)
    import wb_forge2 as WF
    WF.flames(b, F.sub(0, 0, 0, 0), 0.0, hy, 1.3, 4.2, "hearth")
    fm_lib.light("L_SN_Hearth", "POINT", F.p(0, hy + 2.0, 5.0), 2600.0, (1.0, 0.48, 0.16), 1.4)
    fm_lib.marker("VFX_Hearth_Fire_C", F.p(0, hy, 1.6), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "fire", "rate": 16, "size": 3.4})
    fm_lib.marker("VFX_Hearth_Ember_C", F.p(0, hy, 3.2), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "ember", "rate": 8})
    # canal de lava: do pe do plinto (z -92) ate a lareira, passando por uma boca em arco no muro do fundo
    ch = [(-6.0 * -1, -30.0), (-6.0 * -1 + 0.0, -24.0), (3.0, -20.0), (1.5, -16.0), (0.0, hy - 3.6)]
    ch = [(x * -1.0, y) for (x, y) in [(6.0, -30.0), (5.0, -24.0), (3.0, -19.5), (1.5, -16.5), (0.6, hy - 3.8)]]
    for (p0, p1) in zip(ch, ch[1:]):
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) + 0.4
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        Fc = Fr(F.p(mx, my, 0), (math.cos(ang + math.pi / 2) * F.t.x + math.sin(ang + math.pi / 2) * F.f.x,
                                   math.cos(ang + math.pi / 2) * F.t.y + math.sin(ang + math.pi / 2) * F.f.y))
        bb(Fc and b, Fc, -ln / 2, ln / 2, -1.2, 1.2, -0.5, -0.12, "SN_Lava")
        bb(b, Fc, -ln / 2, ln / 2, -0.5, 0.5, -0.14, -0.05, "SN_LavaHot")
        for s in (-1, 1):
            bb(b, Fc, -ln / 2, ln / 2, s * 1.7 - 0.5, s * 1.7 + 0.5, -0.3, 0.35, "SN_Ashlar_Dark")
    # boca em arco no muro do fundo (por onde a lava entra)
    Fm = Fr(F.p(0.0, -rm, 0), (F.f.x, F.f.y))
    stone_arch(b, Fm, 0.0, 3.4, 1.2, depth=t + 0.6, ring=0.9, mat="SN_Ashlar_Dark", pier=0.9, seed="culv", moss=False, n=7)
    # FOLES gigantes dos dois lados da lareira (tabuas + couro em pregas + bico ate a lareira)
    for s in (-1, 1):
        bx0 = s * 7.5
        Fbw = F.sub(bx0, hy + 1.0, 0, -s * 30)
        bb(b, Fbw, -1.6, 1.6, -3.2, 3.2, 0.0, 1.2, "SN_Ashlar_Dark")
        extrude_xz(b, Fbw, [(-1.8, 1.2), (1.8, 1.2), (0.6, 4.4), (-0.6, 4.4)], -3.6, 3.6, "WB_Plank")
        for k in range(4):
            zz = 1.6 + k * 0.75
            bb(b, Fbw, -1.9 + k * 0.28, 1.9 - k * 0.28, -3.9, 3.9, zz, zz + 0.45, "WB_LeatherDark")
        b.cyl(Fbw.p(0, -3.6, 2.4), F.p(s * 3.6, hy + 0.6, 1.4), 0.45, "SN_Bronze", seg=8)
        beam(b, Fbw, (0, 3.6, 4.6), (0, 7.5, 7.5), 0.5, 0.5, "WB_Timber")            # alavanca
    # bancada, cavalete de ferramentas, tonel de tempera, pilhas de carvao e lingotes (encostados no muro)
    WF.workbench(b, F.sub(-13.0, -2.0, 0, 90), 0, 0, 0.0, 4.6)
    WF.tool_rack(b, F.sub(13.4, -4.0, 0, -90), 0, 0, 0.0, 4.0)
    WF.quench(b, F, 12.6, 3.6)
    for (cx, cy) in ((-12.0, -9.0), (11.0, -10.0)):
        for k in range(7):
            rr_ = rng("coal", cx, k)
            b.sphere(F.p(cx + rr_.uniform(-1.4, 1.4), cy + rr_.uniform(-1.0, 1.0), 0.4 + rr_.uniform(0, 0.6)), rr_.uniform(0.6, 0.9),
                     "WB_Coal", seg=6, scale=(1, 1, 0.7))
    for k in range(3):
        for j in range(3 - k):
            bb(b, F, -14.6 + j * 1.3 + k * 0.65, -13.6 + j * 1.3 + k * 0.65, 4.0, 5.4, 0.02 + k * 0.5, 0.48 + k * 0.5,
               "WB_Ingot" if (j + k) % 3 == 0 else "WB_Iron")
    barrel(b, F, -14.6, 7.8, 1.1, 2.6)
    crate(b, F, 14.8, 8.2, 2.2, turn=14)
    # picaretas a venda na entrada (fora da envoltoria do Ignis) e braseiros
    for s in (-1, 1):
        pickaxe_rack(b, F.sub(s * 12.5, 17.5, 0, 0), 0, 0, n=4, seed=s)
        brazier(b, F, s * 17.5, 21.0, 0.0, 3.4, "L_SN_Brazier_Forge%s" % ("W" if s > 0 else "E"))
    # hera e musgo nas colunas/muros
    objs = b.finish()
    # colisao: muro (segmentos), colunas, lareira, foles, bancadas
    a = a_open1
    while a < a_open0 + 360 - 1e-6:
        a2 = min(a + 13.0, a_open0 + 360)
        p0, p1 = polar(rm, a), polar(rm, a2)
        mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1]) + 0.35
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        c = F.p(mx, my, 4.0)
        fm_lib.col_box("Forge", (ln, t, 8.0), c, (0, 0, F.yaw() + ang))
        a = a2
    for ang in (a_open1, a_open0, 212.0, 328.0):
        px, py = polar(rm, ang)
        fm_lib.col_box("Forge", (4.2, 4.2, col_top), F.p(px, py, col_top / 2), (0, 0, F.yaw()))
    fm_lib.col_box("Forge", (9.0, 9.0, 1.8), F.p(0, hy, 0.9), (0, 0, F.yaw()))
    for s in (-1, 1):
        fm_lib.col_box("Forge", (4.0, 7.6, 4.6), F.p(s * 7.5, hy + 1.0, 2.3), (0, 0, F.yaw() - s * RAD(30)))
        fm_lib.col_box("Forge", (3.4, 5.0, 4.2), F.p(s * 12.5, 17.5, 2.1), (0, 0, F.yaw()))
    contract_markers()
    return objs


def _rib(b, F, span, z_spring):
    """arco-costela de aduelas grandes entre as colunas do fundo, com 2 aduelas faltando (ruina)"""
    n = 13
    rr = span / 2 - 1.9
    ring = 2.0
    depth = 2.6
    for k in range(n):
        if k in (8, 9):
            continue
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        quad = [((rr + ring) * math.cos(a0), z_spring + (rr + ring) * math.sin(a0)),
                ((rr + ring) * math.cos(a1), z_spring + (rr + ring) * math.sin(a1)),
                (rr * math.cos(a1), z_spring + rr * math.sin(a1)), (rr * math.cos(a0), z_spring + rr * math.sin(a0))]
        bm = bmesh.new()
        v0 = [bm.verts.new(F.p(x, -depth / 2, z)) for (x, z) in quad]
        v1 = [bm.verts.new(F.p(x, depth / 2, z)) for (x, z) in quad]
        bm.faces.new(list(reversed(v0)))
        bm.faces.new(v1)
        for i in range(4):
            bm.faces.new((v0[i], v0[(i + 1) % 4], v1[(i + 1) % 4], v1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        c = sum((v.co for v in bm.verts), V()) / len(bm.verts)
        for v in bm.verts:
            v.co = c + (v.co - c) * 0.96
        b.mesh(bm, "SN_Ashlar_Moss" if k in (3, 4, 10) else "SN_Ashlar", axes=[F.t, F.f, V((0, 0, 1))], dims=(ring, depth, ring))
    # aduela caida no chao
    worn_block(b, F, -rr * 0.4, 3.0, 1.0, (3.4, 2.6, 2.0), "SN_Ashlar", seed="fallen", chips=3, turn=30, tilt=(12, 8))


def contract_markers():
    rx, ry, rz = L.IGNIS_ROOT
    fm_lib.marker("NPC_Ignis", RB(rx, rz, ry), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"npc": "Ignis", "alvo": "workspace.NPCs.Ignis (Root)", "face_x": 0.0, "face_z": 1.0, "yaw_deg": 180.0})
    fm_lib.marker("INTERACT_Ignis", RB(rx, rz + 0.5, L.IGNIS_BELLY_Y), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"prompt_range": 18, "server_range": 22, "alvo": "belly (prompt do Main)"})
    fm_lib.marker("PLAYER_INTERACT_Ignis", RB(L.PLAYER_IGNIS[0], L.PLAYER_IGNIS[1], Y0), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"face_x": 0.0, "face_z": -1.0, "yaw_deg": 0.0})
    fm_lib.marker("IGNIS_Anvil", RB(L.IGNIS_ANVIL[0], L.IGNIS_ANVIL[2], L.IGNIS_ANVIL[1]), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"nota": "bigorna do golem"})
    fm_lib.marker("LETREIRO_Ignis", RB(rx, rz, L.LETREIRO_Y), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"alvo": "LetreiroIgnis"})
    fm_lib.marker("ForgeChimney", RB(0.0, -74.0, 12.0), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"nota": "AudioWorld: ambiente da forja"})


# ------------------------------------------------------------------ praca das runas
def slab(b, F, r0, r1, a0, a1, dz, depth, ch, mat, nseg=None):
    """laje em setor anelar com chanfro no topo: 3 aneis de vertices (base, inicio do chanfro, topo recuado)"""
    if nseg is None:
        nseg = max(2, int(math.ceil((a1 - a0) / 6.0)))
    bm = bmesh.new()

    def loop(rr0, rr1, aa0, aa1, z):
        pts = []
        for i in range(nseg + 1):
            a = math.radians(aa0 + (aa1 - aa0) * i / nseg)
            pts.append((rr1 * math.cos(a), rr1 * math.sin(a)))
        for i in range(nseg, -1, -1):
            a = math.radians(aa0 + (aa1 - aa0) * i / nseg)
            pts.append((rr0 * math.cos(a), rr0 * math.sin(a)))
        return [bm.verts.new(F.p(x, y, z)) for (x, y) in pts]
    rm = (r0 + r1) / 2
    ga = math.degrees(ch / rm)
    bot = loop(r0, r1, a0, a1, dz - depth)
    mid = loop(r0, r1, a0, a1, dz - ch)
    top = loop(r0 + ch, r1 - ch, a0 + ga, a1 - ga, dz)
    n = len(bot)
    for A_, B_ in ((bot, mid), (mid, top)):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((A_[i], A_[j], B_[j], B_[i]))
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, mat)


def plaza(coll="03_TOWN"):
    b = SL.Build("WB_Town_Plaza", coll)
    F = Fr.rbx(L.C[0], L.C[1], Y0, 0.0, 1.0)

    def ring(r0, r1, z0, z1, mat, n=72, a0=0.0, a1=360.0):
        bm = bmesh.new()
        outer, inner, outer2, inner2 = [], [], [], []
        closed = abs(a1 - a0) >= 359.9
        m = n if closed else n + 1
        for i in range(m):
            a = math.radians(a0 + (a1 - a0) * i / n)
            for lst, rr, zz in ((outer, r1, z0), (inner, r0, z0), (outer2, r1, z1), (inner2, r0, z1)):
                lst.append(bm.verts.new(F.p(rr * math.cos(a), rr * math.sin(a), zz)))
        rng_ = range(n) if closed else range(n)
        for i in rng_:
            j = (i + 1) % m if closed else i + 1
            bm.faces.new((outer2[i], outer2[j], inner2[j], inner2[i]))
            bm.faces.new((outer[i], inner[i], inner[j], outer[j]))
            bm.faces.new((outer[i], outer[j], outer2[j], outer2[i]))
            bm.faces.new((inner[j], inner[i], inner2[i], inner2[j]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, mat)
    # leito escuro das juntas + lajes chanfradas em aneis concentricos (cada laje um tom, juntas com AO no bake)
    poly_prism(b, F, [(L.PLAZA_R * math.cos(2 * math.pi * i / 72), L.PLAZA_R * math.sin(2 * math.pi * i / 72)) for i in range(72)],
               -0.8, -0.16, "SN_Ashlar_Dark")
    r0_, r1_ = L.RUNE_R
    rr_s = rng("slabs")
    zones = [(L.MEDAL_R + 0.1, r0_ - 0.75, 4), (r1_ + 0.75, L.PLAZA_R - 0.25, 3)]
    for (ra, rb, nring) in zones:
        edges = [ra + (rb - ra) * k / nring for k in range(nring + 1)]
        for k in range(nring):
            q0, q1 = edges[k] + 0.07, edges[k + 1] - 0.07
            rm_ = (q0 + q1) / 2
            nseg = max(10, int(round(2 * math.pi * rm_ / rr_s.uniform(4.2, 5.2))))
            off = rr_s.uniform(0, 360.0 / nseg)
            for j in range(nseg):
                a0 = off + 360.0 * j / nseg
                a1 = off + 360.0 * (j + 1) / nseg
                g = math.degrees(0.07 / rm_)
                slab(b, F, q0, q1, a0 + g, a1 - g, rr_s.uniform(-0.035, 0.03), 0.6, 0.11, "SN_Plaza")
    ring(L.PLAZA_R - 0.2, L.PLAZA_R + 1.4, -0.8, 0.22, "SN_Ashlar_Dark", 96)
    r0, r1 = L.RUNE_R
    ring(r0, r1, -0.2, 0.06, "SN_Carved", 96)
    ring(r0 - 0.7, r0, -0.2, 0.12, "SN_Bronze", 96)
    ring(r1, r1 + 0.7, -0.2, 0.12, "SN_Bronze", 96)
    # runas acesas no anel (traços radiais/tangenciais em grade 3x3, por celula angular)
    rr_ = rng("plaza_runes")
    n = 40
    for i in range(n):
        a_c = 2 * math.pi * (i + 0.5) / n
        da = 2 * math.pi / n * 0.32
        g = [(-1, 0), (0, 0), (1, 0)]
        pts = []
        for t in range(rr_.randint(3, 4)):
            u0, w0 = rr_.choice((-1, 0, 1)), rr_.choice((0, 1, 2))
            u1, w1 = rr_.choice((-1, 0, 1)), rr_.choice((0, 1, 2))
            if (u0, w0) == (u1, w1):
                w1 = 2 if w0 < 1 else 0
            pa = (r0 + 0.8 + w0 * (r1 - r0 - 1.6) / 2, a_c + u0 * da)
            pc = (r0 + 0.8 + w1 * (r1 - r0 - 1.6) / 2, a_c + u1 * da)
            beam(b, F, (pa[0] * math.cos(pa[1]), pa[0] * math.sin(pa[1]), 0.1),
                 (pc[0] * math.cos(pc[1]), pc[0] * math.sin(pc[1]), 0.1), 0.32, 0.14, "SN_Rune")
    # raios de bronze do medalhao ate o anel
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4
        beam(b, F, ((L.MEDAL_R + 0.4) * math.cos(a), (L.MEDAL_R + 0.4) * math.sin(a), 0.04),
             ((r0 - 0.7) * math.cos(a), (r0 - 0.7) * math.sin(a), 0.04), 0.5, 0.12, "SN_Bronze")
    # medalhao: disco escuro, aro de bronze e o emblema bigorna + martelo em ouro velho
    cyl(b, F, (0, 0, -0.2), (0, 0, 0.08), L.MEDAL_R, "SN_Ashlar_Dark", seg=40)
    ring(L.MEDAL_R - 0.6, L.MEDAL_R, -0.2, 0.16, "SN_Bronze", 48)
    k_ = 1.15
    anv = [(-6.6, 1.5), (-3.2, 2.3), (5.0, 2.3), (5.7, 1.5), (4.5, 1.0), (2.3, 0.1), (2.0, -1.6), (3.8, -2.7), (-3.8, -2.7),
           (-2.0, -1.6), (-2.3, 0.1), (-3.5, 1.0)]
    poly_prism(b, F, [(x * k_, (y - 0.4) * k_) for (x, y) in anv], 0.08, 0.3, "SN_Gold")
    # martelo cruzando por tras (cabo e cabeca), em bronze
    beam(b, F, (-5.2, -6.2, 0.2), (3.4, 5.6, 0.2), 0.75, 0.14, "SN_Bronze")
    hc = (3.9, 6.3)
    import math as _m
    ang = _m.atan2(5.6 + 6.2, 3.4 + 5.2)
    tx, ty = _m.cos(ang + _m.pi / 2), _m.sin(ang + _m.pi / 2)
    beam(b, F, (hc[0] - tx * 2.4, hc[1] - ty * 2.4, 0.22), (hc[0] + tx * 2.4, hc[1] + ty * 2.4, 0.22), 1.6, 0.2, "SN_Bronze")
    # trilhas acesas no piso ate cada estacao (estilo das setas que guiam do Anime Defenders)
    import sn_layout as LL
    for ang in (90.0, 270.0, 14.0, 166.0, 214.0, 326.0):
        a = math.radians(ang)
        X, Zr = math.cos(a), math.sin(a)
        p0 = (-(r1 + 1.2) * X, (r1 + 1.2) * Zr, 0.05)
        p1 = (-(L.PLAZA_R - 1.2) * X, (L.PLAZA_R - 1.2) * Zr, 0.05)
        beam(b, F, p0, p1, 0.5, 0.12, "SN_Rune")
        for s in (-1, 1):
            off = (s * 0.9 * Zr, s * 0.9 * X)
            beam(b, F, (p0[0] + off[0], p0[1] + off[1], 0.04), (p1[0] + off[0], p1[1] + off[1], 0.04), 0.22, 0.1, "SN_Bronze")
    objs = b.finish()
    return objs
