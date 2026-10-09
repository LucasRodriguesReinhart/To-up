# sn_ruins.py - RUINAS do santuario (o que sobrou do templo do deus-ferreiro, contando a historia do lugar):
#   - CIRCULO DOS PILARES em volta da praca (r 47): colunas antigas, algumas partidas, nunca na frente de uma trilha;
#   - muros de cerca arruinados perto da borda do plato (com vaos), arcos-fragmento isolados;
#   - a CABECA TOMBADA de um golem-guardiao gigante semi-enterrada no gramado leste (olhos de runa apagando);
#   - cristais de minerio brotando de montes de entulho; pedras soltas.
import math
import random

import fm_lib
import sn_lib as SL
import sn_layout as L
import sn_vegplan as VP
from sn_kit import (column, worn_block, moss_patch, ivy, rng, ruin_wall, stone_arch, crystal_cluster, rubble,
                    rune_glyphs, flower_bed)
from wb_kit import Fr, bb, beam, cyl
from wb_lib import RB

COLL = "03_TOWN"
AREA = "Ruins"
PILLAR_R = 47.0


def _station_angles():
    a = [90.0, 270.0, (math.degrees(math.atan2(L.SHOP_C[1], L.SHOP_C[0])) + 360) % 360,
         (math.degrees(math.atan2(L.RANK_O[1], L.RANK_O[0])) + 360) % 360] + [L.WEST_ANG, 310.0]
    return a


def _ang_dist(a, b):
    d = abs((a - b + 180) % 360 - 180)
    return d


def pillar_ring(b):
    sa = _station_angles()
    r = rng("pring")
    k = 0
    for i in range(36):
        a = i * 10.0 + 5.0
        if min(_ang_dist(a, s) for s in sa) < 9.0:
            continue
        if 255.0 < a < 287.0:                       # frente da forja: livre
            continue
        if a < 120.0:                               # sul livre (vista do spawn para loja/tabuas)
            continue
        if i % 2:
            continue
        x, z = PILLAR_R * math.cos(math.radians(a)), PILLAR_R * math.sin(math.radians(a))
        F = Fr.rbx(x, z, L.Y_GRASS - 0.3, -x, -z)
        broken = None if k % 3 != 1 else r.uniform(5.0, 9.0)
        column(b, F, 0.0, 0.0, 0.0, 15.5, r0=1.2, seed=("pr", i), broken=broken)
        fm_lib.col_box(AREA, (2.8, 2.8, 15.0), RB(x, z, L.Y_GRASS + 7.0), (0, 0, 0))
        if broken is not None:
            worn_block(b, F, r.uniform(2.5, 4.0), r.uniform(-2.0, 2.0), 0.8, (2.4, 2.4, 1.6), "SN_Ashlar",
                       seed=("prd", i), chips=3, turn=r.uniform(0, 90), tilt=(r.uniform(-20, 20), r.uniform(-20, 20)))
        flower_bed(b, F, 0.0, 0.0, 0.3, 2.6, 2.6, 6, seed=("prf", i))
        k += 1
    return k


def head(b, x, z, s=1.0, yaw=30.0):
    """cabeca tombada de um golem gigante (de lado, meio enterrada): blocos lascados, testa, sobrancelha, olho de runa"""
    F = Fr.rbx(x, z, L.Y_GRASS - 2.2 * s, math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
    worn_block(b, F, 0.0, 0.0, 4.2 * s, (13.0 * s, 10.0 * s, 9.0 * s), "SN_Ashlar", seed="hd1", chips=4, bevel=0.6 * s,
               tilt=(0.0, 18.0))
    worn_block(b, F, 0.0, 5.4 * s, 6.0 * s, (11.0 * s, 2.4 * s, 2.2 * s), "SN_Carved", seed="hd2", chips=3, bevel=0.3 * s,
               tilt=(0.0, 18.0))
    worn_block(b, F, -1.2 * s, 6.2 * s, 2.6 * s, (4.0 * s, 2.4 * s, 4.2 * s), "SN_Ashlar_Dark", seed="hd3", chips=2,
               bevel=0.4 * s, tilt=(0.0, 18.0))
    worn_block(b, F, 5.6 * s, 3.5 * s, 9.0 * s, (3.6 * s, 4.0 * s, 3.0 * s), "SN_Ashlar", seed="hd4", chips=3,
               bevel=0.3 * s, tilt=(10.0, 25.0))
    for sx in (-1, 1):
        bb(b, F, sx * 2.6 * s - 1.0 * s, sx * 2.6 * s + 1.0 * s, 5.0 * s, 5.35 * s, 4.6 * s, 5.4 * s, "SN_Rune")
    Fp = Fr(F.p(0, 5.05 * s, 0), (F.f.x, F.f.y))
    rune_glyphs(b, Fp, -3.0 * s, 3.0 * s, 1.6 * s, h=1.2 * s, n=3, seed="hdr", depth=0.2)
    moss_patch(b, F, -1.0 * s, -1.0 * s, 8.9 * s, 10.0 * s, 7.0 * s, seed="hdm", thick=0.5)
    ivy(b, Fr(F.p(0, 5.2 * s, 0), (F.f.x, F.f.y)), 3.0 * s, 0.0, 8.0 * s, 5.0, 3.0, seed="hdi")
    rubble(b, F, 0.0, 0.0, 2.2 * s, 9.0 * s, 14, "SN_Ashlar", seed="hdrub")
    crystal_cluster(b, F, -6.5 * s, 2.0 * s, 2.2 * s, 1.6, "SN_CrystalAmber", seed="hdc")
    fm_lib.col_box(AREA, (13.0 * s, 10.0 * s, 9.0 * s), F.p(0, 0, 4.2 * s), (0, 0, F.yaw()))


def walls(b):
    r = random.Random(77)
    out = 0
    segs = L.RUIN_WALLS
    for k, (xa, za, xc, zc) in enumerate(segs):
        ln = math.hypot(xc - xa, zc - za)
        mx, mz = (xa + xc) / 2, (za + zc) / 2
        if not VP._in_poly(mx, mz, L.PLATEAU):
            continue
        F = Fr.rbx(xa, za, L.Y_GRASS - 0.4, -(zc - za), (xc - xa))
        Fw = Fr(F.o, (F.f.x, F.f.y))
        # frame com x ao longo do muro: t = direcao do muro
        dx, dz = (xc - xa) / ln, (zc - za) / ln
        Fm = Fr.rbx(xa, za, L.Y_GRASS - 0.4, dz, -dx)
        ruin_wall(b, Fm, 0.0, ln, 0.0, r.uniform(5.0, 8.0), 1.8, "SN_Ashlar", seed=("rw", k), ruin=0.6, course=1.4,
                  top_mat="SN_Ashlar_Moss")
        rubble(b, Fm, ln * 0.5, 2.5, 0.4, 3.5, 8, "SN_Ashlar", seed=("rwr", k))
        if k % 2 == 0:
            crystal_cluster(b, Fm, ln * 0.3, 1.8, 0.4, 1.3, "SN_CrystalBlue" if k % 4 == 0 else "SN_CrystalAmber",
                            seed=("rwc", k))
        for t in range(int(ln / 6) + 1):
            p = Fm.p(min(ln, t * 6.0 + 3.0), 0, 0)
            fm_lib.col_box(AREA, (6.0, 1.8, 6.0), p + Fm.f * 0.0 + __import__("mathutils").Vector((0, 0, 3.0)),
                           (0, 0, Fm.yaw()))
        out += 1
    return out


def arches(b):
    pts = L.RUIN_ARCHES
    n = 0
    for k, (x, z, yaw) in enumerate(pts):
        if not VP._in_poly(x, z, L.PLATEAU):
            continue
        F = Fr.rbx(x, z, L.Y_GRASS - 0.3, math.cos(math.radians(yaw)), math.sin(math.radians(yaw)))
        stone_arch(b, F, 0.0, 9.0, 9.0, depth=2.4, ring=1.4, mat="SN_Ashlar", pier=2.4, pier_mat="SN_Ashlar_Dark",
                   seed=("arch", k), missing=(k % 3, 6 + k % 2), key_mat="SN_Carved", n=11)
        rubble(b, F, 2.0, 2.0, 0.3, 4.0, 9, "SN_Ashlar", seed=("ar", k))
        for s in (-1, 1):
            fm_lib.col_box(AREA, (2.6, 2.6, 10.0), F.p(s * 5.7, 0, 5.0), (0, 0, F.yaw()))
        n += 1
    return n


def crystals(b):
    spots = L.RUIN_CRYSTALS
    n = 0
    for k, (x, z, m, s) in enumerate(spots):
        if not VP._in_poly(x, z, L.PLATEAU):
            continue
        F = Fr.rbx(x, z, L.Y_GRASS - 0.2, 0.0, 1.0)
        rubble(b, F, 0.0, 0.0, 0.0, 3.6 * s, 10, "SN_Ashlar_Dark", seed=("cr", k))
        crystal_cluster(b, F, 0.0, 0.0, 0.0, s, m, seed=("crc", k))
        crystal_cluster(b, F, 1.8 * s, 1.0 * s, 0.0, s * 0.6, m, seed=("crc2", k))
        fm_lib.light("L_SN_Crystal_%d" % k, "POINT", F.p(0, 0, 3.0 * s), 160.0,
                     (1.0, 0.65, 0.3) if m == "SN_CrystalAmber" else (0.45, 0.75, 1.0), 1.0)
        n += 1
    return n


def build():
    SL.register()
    fm_lib.make_materials()
    b = SL.Build("WB_Prop_Ruins", COLL)
    np_ = pillar_ring(b)
    head(b, L.RUIN_HEAD[0], L.RUIN_HEAD[1], 1.0, yaw=L.RUIN_HEAD[2])
    nw = walls(b)
    na = arches(b)
    nc = crystals(b)
    objs = b.finish()
    print("RUINAS: %d pilares, %d muros, %d arcos, %d cristais + cabeca tombada" % (np_, nw, na, nc))
    return objs
