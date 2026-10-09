# sn_rank.py - TABUAS DOS CAMPEOES (ranking GlobalTop100), sudeste da praca, olhando para ela.
# Os campeoes sao gravados aos pes do deus-ferreiro: duas TABUAS de pedra monumentais (molduras entalhadas com cantos
# de bronze e coroa em arco com o emblema - martelo para FORCA, moeda para MOEDAS) emolduram os 2 quadros do jogo;
# entre elas um OBELISCO de runas acesas com braseiro; nas pontas, pilares com braseiros; atras, o muro antigo
# arruinado com o titulo "TABUAS DOS CAMPEOES" em letras de ouro na verga; palco de lajes com degrau.
# CONTRATO (como o Mural do Wolfberg): origem RANK_O na cota Y_RANK olhando a praca; quadros 26 x 25 x 1,6 em y local
# 0..1,6 centrados em x local +-13,4; podios do jogo em y local 9,5 -> faixa x +-27 / y 0..13,2 LIVRE (so o piso).
import math

import bmesh
import fm_lib
import sn_lib as SL
import sn_layout as L
from mathutils import Vector
from sn_kit import column, worn_block, moss_patch, ivy, rng, brazier, rune_glyphs, ruin_wall, crystal_cluster, rubble
from wb_kit import Fr, bb, beam, cyl, lathe, poly_prism, text
from wb_lib import RB

V = Vector
COLL = "05_SERVICES"
AREA = "Rank"
QX = (-13.4, 13.4)
QW, QH = 26.0, 25.0
HX = 34.0                  # meia largura do palco/muro


def preview(F):
    pb = SL.Build("PREVIEW_Top100", "00_REFERENCE")
    for xc in QX:
        bb(pb, F, xc - QW / 2, xc + QW / 2, 0.0, 1.6, 0.0, QH, "WB_Dark")
        bb(pb, F, xc - 11.8, xc + 11.8, 1.6, 1.95, 0.6, 24.4, "SN_Slate")
        for k in range(10):
            bb(pb, F, xc - 10.5, xc + 10.5, 1.95, 2.0, 21.5 - k * 2.0, 22.5 - k * 2.0, "SN_Paper")
        for (dx, h) in ((0.0, 2.4), (-8.0, 1.6), (8.0, 1.0)):
            bb(pb, F, xc + dx - 3.3, xc + dx + 3.3, 9.5 - 2.9, 9.5 + 2.9, 0.0, h, "SN_Ashlar")
    return pb.finish()


def stage(b, F):
    y0 = L.Y_GRASS - 0.6 - L.Y_RANK
    poly_prism(b, F, [(-HX, -9.0), (HX, -9.0), (HX, 17.0), (-HX, 17.0)], y0, -0.62, "SN_Ashlar_Dark")
    bb(b, F, -HX - 0.3, HX + 0.3, 17.0, 18.6, y0, -0.62, "SN_Ashlar")          # degrau para a praca
    # lajes do palco (fiadas ao longo de x)
    r = rng("rkst")
    yy = -8.6
    while yy < 16.8:
        d = r.uniform(2.2, 3.2)
        x = -HX + 0.4 - r.uniform(0, 1.5)
        while x < HX - 0.4:
            ln = r.uniform(2.6, 4.2)
            xa, xb = max(-HX + 0.4, x), min(HX - 0.4, x + ln)
            if xb - xa > 0.6:
                bb(b, F, xa + 0.06, xb - 0.06, yy + 0.06, min(16.8, yy + d) - 0.06, -0.62, -0.02 + r.uniform(-0.02, 0.0),
                   "SN_Plaza", bevel=0.05)
            x += ln
        yy += d
    fm_lib.col_box(AREA, (2 * HX, 26.0, 1.2), F.p(0, 4.0, -0.6), (0, 0, F.yaw()))
    fm_lib.col_box(AREA, (2 * HX + 0.6, 1.6, 0.6), F.p(0, 17.8, -0.6 - 0.3 + 0.0), (0, 0, F.yaw()))


def back_wall(b, F):
    Fw = F.sub(0, -6.2, 0, 0)
    ruin_wall(b, Fw, -HX, HX, 0.0, 40.0, 3.2, "SN_Ashlar", seed="rkw", ruin=0.16, course=1.6, top_mat="SN_Ashlar_Moss")
    # verga com o titulo (acima das coroas das tabuas), cornija e o emblema do deus no centro
    bb(b, F, -HX + 1.0, HX - 1.0, -5.0, -2.4, 33.4, 37.2, "SN_Carved", bevel=0.15)
    bb(b, F, -HX + 0.6, HX - 0.6, -5.2, -2.0, 37.2, 37.8, "SN_Ashlar_Dark", bevel=0.1)
    bb(b, F, -HX + 0.6, HX - 0.6, -5.2, -2.0, 32.8, 33.4, "SN_Ashlar_Dark", bevel=0.1)
    Ft = Fr(F.p(0, -2.38, 0), (F.f.x, F.f.y))
    text(b, Ft, "TABUAS DOS CAMPEOES", 1.9, "SN_Gold", 0.0, 0.0, 35.3, thick=0.3, bold=True)
    anv = [(-4.4, 1.0), (-2.2, 1.6), (3.4, 1.6), (3.9, 1.0), (3.0, 0.7), (1.5, 0.05), (1.3, -1.1), (2.6, -1.9),
           (-2.6, -1.9), (-1.3, -1.1), (-1.5, 0.05), (-2.4, 0.7)]
    bm = bmesh.new()
    a = [bm.verts.new(F.p(x, -2.0, 40.6 + z)) for (x, z) in anv]
    c = [bm.verts.new(F.p(x, -1.4, 40.6 + z)) for (x, z) in anv]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(len(anv)):
        bm.faces.new((a[i], a[(i + 1) % len(anv)], c[(i + 1) % len(anv)], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, "SN_Gold")
    bb(b, F, -6.0, 6.0, -5.2, -1.8, 37.8, 38.6, "SN_Carved", bevel=0.1)
    # verso: contrafortes escalonados, cornija e hera (o verso e visto da avenida e do ar)
    Fb = F.sub(0, -7.8, 0, 180)
    for k, xx in enumerate((-28.0, -14.0, 0.0, 14.0, 28.0)):
        bb(b, Fb, xx - 1.8, xx + 1.8, 0.0, 3.0, -0.6, 16.0, "SN_Ashlar_Dark", bevel=0.12)
        bb(b, Fb, xx - 1.5, xx + 1.5, 0.0, 2.0, 16.0, 26.0, "SN_Ashlar", bevel=0.12)
        bb(b, Fb, xx - 1.3, xx + 1.3, 0.0, 1.0, 26.0, 33.0, "SN_Ashlar", bevel=0.12)
        if k % 2 == 0:
            ivy(b, Fr(Fb.p(xx + 3.0, 0.05, 0), (Fb.f.x, Fb.f.y)), 0.0, 0.0, 30.0, 14.0, 4.0, seed=("rkb", k))
    for xx in (-21.0, 7.0):
        bb(b, Fb, xx - 5.0, xx + 5.0, -0.2, 0.3, 10.0, 22.0, "SN_Carved", bevel=0.1)
        Fr_ = Fr(Fb.p(0, 0.32, 0), (Fb.f.x, Fb.f.y))
        rune_glyphs(b, Fr_, xx - 3.6, xx + 3.6, 15.0, h=3.0, n=3, seed=("rkbr", xx), depth=0.25)
    ivy(b, Fr(F.p(0, -2.3, 0), (F.f.x, F.f.y)), -27.0, 0.0, 37.6, 9.0, 3.0, seed="rkv1")
    ivy(b, Fr(F.p(0, -2.3, 0), (F.f.x, F.f.y)), 25.0, 0.0, 37.6, 12.0, 3.5, seed="rkv2")


def tablet(b, F, xc, label, emblem):
    """moldura de pedra entalhada em volta do quadro do jogo + coroa em arco com emblema e cartela com o nome"""
    o, d = 1.6, 2.6                                  # largura da moldura / profundidade (de y -2.2 a 0.4)
    x0, x1 = xc - QW / 2 - o, xc + QW / 2 + o
    # muro-tabua atras do quadro
    bb(b, F, x0, x1, -2.4, -0.2, 0.0, QH + 1.0, "SN_Ashlar_Dark")
    # moldura saliente (laterais e topo; embaixo o quadro do jogo pousa direto no palco)
    for (a, c, z0, z1) in ((x0, x1, QH + 0.1, QH + 1.6), (x0, x0 + o, -0.6, QH + 1.6), (x1 - o, x1, -0.6, QH + 1.6)):
        bb(b, F, a, c, -2.4, 1.9, z0, z1, "SN_Carved", bevel=0.14)
    # cantos de bronze
    for (cx, cz) in ((x0 + o / 2, 0.35), (x1 - o / 2, 0.35), (x0 + o / 2, QH + 0.85), (x1 - o / 2, QH + 0.85)):
        bb(b, F, cx - 1.1, cx + 1.1, 1.8, 2.25, cz - 1.1, cz + 1.1, "SN_Bronze", bevel=0.1)
        cyl(b, F, (cx, 2.25, cz), (cx, 2.55, cz), 0.45, "SN_Gold", seg=8)
    # runas pequenas acesas ao longo dos montantes
    for xx in (x0 + o / 2, x1 - o / 2):
        for k in range(5):
            zz = 4.0 + k * 4.0
            beam(b, F, (xx - 0.3, 1.92, zz), (xx + 0.3, 1.92, zz + 0.9), 0.08, 0.16, "SN_Rune")
            beam(b, F, (xx + 0.3, 1.92, zz), (xx - 0.1, 1.92, zz + 0.5), 0.08, 0.14, "SN_Rune")
    # coroa em arco (semi-disco) sobre a tabua, com o emblema
    R = 7.2
    zb = QH + 1.6
    n = 16
    bm = bmesh.new()
    pts = [(xc + R * math.cos(math.pi * k / n), zb + R * 0.82 * math.sin(math.pi * k / n)) for k in range(n + 1)]
    a = [bm.verts.new(F.p(x, -2.4, z)) for (x, z) in pts]
    c = [bm.verts.new(F.p(x, 0.2, z)) for (x, z) in pts]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(len(pts)):
        bm.faces.new((a[i], a[(i + 1) % len(pts)], c[(i + 1) % len(pts)], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, "SN_Carved")
    # aro de bronze da coroa
    for k in range(n):
        p0, p1 = pts[k], pts[k + 1]
        beam(b, F, (p0[0], 0.35, p0[1]), (p1[0], 0.35, p1[1]), 0.5, 0.6, "SN_Bronze")
    ez = zb + 2.9
    cyl(b, F, (xc, 0.2, ez), (xc, 0.55, ez), 2.4, "SN_Bronze", seg=20)
    if emblem == "hammer":
        beam(b, F, (xc - 1.2, 0.6, ez - 1.6), (xc + 1.0, 0.6, ez + 1.4), 0.4, 0.5, "SN_WoodAged")
        b_ = 0.0
        beam(b, F, (xc + 0.2, 0.62, ez + 1.9), (xc + 1.9, 0.62, ez + 0.65), 0.6, 1.1, "SN_Gold")
    else:
        cyl(b, F, (xc, 0.55, ez), (xc, 0.9, ez), 1.5, "SN_Gold", seg=20)
        cyl(b, F, (xc, 0.9, ez), (xc, 1.0, ez), 1.1, "SN_Gold", seg=20)
        bb(b, F, xc - 0.25, xc + 0.25, 0.95, 1.05, ez - 0.8, ez + 0.8, "SN_Bronze")
    # nome na trave de cima da moldura
    Fl = Fr(F.p(0, 1.92, 0), (F.f.x, F.f.y))
    text(b, Fl, label, 0.75, "SN_Gold", xc, 0.0, QH + 0.85, thick=0.12, bold=True)


def obelisk(b, F):
    """obelisco de runas entre as tabuas (x 0, atras da linha dos quadros)"""
    x, y = 0.0, -1.6
    bb(b, F, x - 1.8, x + 1.8, y - 1.8, y + 1.8, 0.0, 1.4, "SN_Ashlar_Dark", bevel=0.12)
    bm = bmesh.new()
    lo, hi, H = 1.25, 0.8, 24.0
    vb = [bm.verts.new(F.p(x + sx * lo, y + sy * lo, 1.4)) for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    vt = [bm.verts.new(F.p(x + sx * hi, y + sy * hi, 1.4 + H)) for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    ap = bm.verts.new(F.p(x, y, 1.4 + H + 1.8))
    bm.faces.new(list(reversed(vb)))
    for i in range(4):
        bm.faces.new((vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i]))
        bm.faces.new((vt[i], vt[(i + 1) % 4], ap))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, "SN_Carved")
    Fo = Fr(F.p(x, y + 1.08, 0), (F.f.x, F.f.y))
    rune_glyphs(b, Fo, -0.6, 0.6, 4.0, h=1.6, n=1, seed="ob1", depth=0.2)
    for k in range(5):
        rune_glyphs(b, Fo, -0.5, 0.5, 6.5 + k * 3.4, h=1.4, n=1, seed=("ob", k), depth=0.2)
    cyl(b, F, (x, y, 1.4 + H + 1.85), (x, y, 1.4 + H + 2.2), 1.1, "SN_Bronze", seg=10)
    crystal_cluster(b, F, x, y, 1.4 + H + 2.2, 0.8, "SN_CrystalAmber", seed="obc")
    fm_lib.col_box(AREA, (3.6, 3.6, H + 3.0), F.p(x, y, (H + 3.0) / 2), (0, 0, F.yaw()))


def build():
    SL.register()
    for k, c in (("SN_Slate", (40, 46, 56)), ("SN_Paper", (238, 228, 200))):
        fm_lib.MATS.setdefault(k, (fm_lib.S(*c), 0.85, 0.0, 0, None, 0.0))
    fm_lib.make_materials()
    ox, oz = L.RANK_O
    fx, fz = L.RANK_FACE
    F = Fr.rbx(ox, oz, L.Y_RANK, fx, fz)
    objs = preview(F)
    b = SL.Build("WB_Rank_Tablets", COLL)
    stage(b, F)
    back_wall(b, F)
    tablet(b, F, QX[0], "FORCA", "hammer")
    tablet(b, F, QX[1], "MOEDAS", "coin")
    for s in (-1, 1):
        x = s * (HX - 3.0)
        column(b, F, x, -3.6, 0.0, 22.0, r0=1.6, seed=("rkc", s), moss=True)
        brazier(b, F, x, 2.2, 0.0, 4.2, "L_SN_Brazier_Rank_%d" % s, fire_r=1.2)
        fm_lib.col_box(AREA, (3.4, 3.4, 22.0), F.p(x, -3.6, 11.0), (0, 0, F.yaw()))
        crystal_cluster(b, F, s * (HX - 1.0), 12.0, -0.02, 1.2, "SN_CrystalBlue", seed=("rkcr", s))
        rubble(b, F, s * (HX + 2.5), 6.0, L.Y_GRASS - L.Y_RANK, 3.0, 7, "SN_Ashlar", seed=("rkr", s))
    moss_patch(b, F, -30.0, -8.0, -0.6, 6.0, 3.0, seed="rkm1")
    moss_patch(b, F, 29.0, 14.0, -0.6, 5.0, 3.0, seed="rkm2")
    objs += b.finish()
    fm_lib.col_box(AREA, (2 * HX, 3.2, 40.0), F.p(0, -6.2, 20.0), (0, 0, F.yaw()))
    for xc in QX:
        fm_lib.col_box(AREA, (QW + 3.2, 2.6, QH + 1.6), F.p(xc, -1.1, (QH + 1.6) / 2), (0, 0, F.yaw()))
    fm_lib.marker("TOP100_Origin", F.p(0, 0, 0), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"alvo": "LOBBY_FORJA.GlobalTop100 (OriginCF)", "nota": "quadros em z 0 e podios em z 9,5 do local",
                   "face_x": fx, "face_z": fz})
    fm_lib.marker("LETREIRO_Ranking", F.p(0, 6.0, 38.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"texto": "TABUAS DOS CAMPEOES", "alcance": 190})
    return objs
