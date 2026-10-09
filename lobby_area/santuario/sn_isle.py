# sn_isle.py - ILHA DOS PORTAIS (oeste do plato, separada pelo lago): patio circular de lajes com a PEDRA DOS MUNDOS
# no centro (estrado hexagonal em 3 degraus + obelisco com 6 runas, cada uma na cor do mundo e apontando para o seu
# portal, e cristal ambar no topo), 6 trilhas acesas na cor de cada mundo do centro ate o estrado, PORTICO DE ENTRADA
# "CAMINHO DOS MUNDOS" no lado da ponte, a PONTE ANTIGA ate o plato com cabeceiras e braseiros, o portico da cabeceira do
# plato ("PORTAIS") e o anel de ruinas da borda (colunas entre os portais, cristais). Os portais e os estrados sao do
# sn_portals (posicoes de sn_layout.portal_pos, ja na ilha).
import math

import bmesh
import fm_lib
import sn_lib as SL
import sn_layout as L
from mathutils import Vector
from sn_kit import column, worn_block, moss_patch, ivy, rng, brazier, rune_glyphs, ruin_wall, stone_arch, crystal_cluster, rubble
from wb_kit import Fr, bb, beam, cyl, lathe, poly_prism, text, banner
from wb_lib import RB

V = Vector
COLL_C = "06_PORTALS"
COLL_B = "07_EXIT"
AREA = "Isle"
WORLD_COL = {"Naruto": "SN_RuneAmber", "DragonBall": "SN_RuneOrange", "ShadowGarden": "SN_RuneViolet",
             "DemonSlayer": "SN_RuneRed", "OnePiece": "SN_RuneBlue", "OnePunchMan": "SN_RuneYellow"}
WORLD_RGB = {"SN_RuneAmber": (255, 176, 70), "SN_RuneOrange": (255, 130, 40), "SN_RuneViolet": (190, 120, 255),
             "SN_RuneRed": (255, 76, 64), "SN_RuneBlue": (90, 170, 255), "SN_RuneYellow": (255, 222, 90)}


def col(dx, dy, dz, p, yaw=0.0):
    fm_lib.col_box(AREA, (dx, dy, dz), p, (0, 0, yaw))


def court(b):
    import sn_hero as H
    cx, cz = L.PORTAL_ISLE_C
    F = Fr.rbx(cx, cz, L.Y_PLAZA, 0.0, 1.0)
    R = L.ISLE_COURT_R
    # leito escuro + lajes em 3 aneis + meio-fio de pedra escura
    poly_prism(b, F, [(R * math.cos(2 * math.pi * i / 64), R * math.sin(2 * math.pi * i / 64)) for i in range(64)],
               L.Y_GRASS - 0.7 - L.Y_PLAZA, -0.16, "SN_Ashlar_Dark")
    rr = rng("islab")
    edges = [7.2, 12.6, 18.0, R - 0.5]
    for k in range(3):
        q0, q1 = edges[k] + 0.07, edges[k + 1] - 0.07
        rm = (q0 + q1) / 2
        nseg = max(10, int(round(2 * math.pi * rm / rr.uniform(4.2, 5.0))))
        off = rr.uniform(0, 360.0 / nseg)
        for j in range(nseg):
            a0 = off + 360.0 * j / nseg
            a1 = off + 360.0 * (j + 1) / nseg
            g = math.degrees(0.07 / rm)
            H.slab(b, F, q0, q1, a0 + g, a1 - g, rr.uniform(-0.035, 0.03), 0.6, 0.11, "SN_Plaza")
    n = 64
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        beam(b, F, ((R - 0.25) * math.cos(a0), (R - 0.25) * math.sin(a0), 0.05),
             ((R - 0.25) * math.cos(a1), (R - 0.25) * math.sin(a1), 0.05), 0.7, 0.34, "SN_Carved")
    # trilhas acesas do centro ate cada portal, na cor do mundo (local x = -X Roblox, y = +Z Roblox)
    for i, (key, aid) in enumerate(L.PORTALS):
        a = math.radians(L.PORTAL_ANG[i])
        X, Zr = math.cos(a), math.sin(a)
        m = WORLD_COL[key]
        p0 = (-8.0 * X, 8.0 * Zr, 0.05)
        p1 = (-(R - 1.0) * X, (R - 1.0) * Zr, 0.05)
        beam(b, F, p0, p1, 0.55, 0.12, m)
        for s in (-1, 1):
            off = (s * 0.95 * Zr, s * 0.95 * X)
            beam(b, F, (p0[0] + off[0], p0[1] + off[1], 0.04), (p1[0] + off[0], p1[1] + off[1], 0.04), 0.22, 0.1, "SN_Bronze")
    # Pedra dos Mundos: estrado hexagonal em 3 degraus + obelisco + cristal
    for (r_, z0, z1, m) in ((7.0, -0.2, 0.55, "SN_Ashlar_Dark"), (5.6, 0.55, 1.15, "SN_Carved"), (4.2, 1.15, 1.75, "SN_Ashlar")):
        poly_prism(b, F, [(r_ * math.cos(math.pi / 6 + k * math.pi / 3), r_ * math.sin(math.pi / 6 + k * math.pi / 3))
                          for k in range(6)], z0, z1, m)
    bm = bmesh.new()
    lo, hi, H_ = 1.9, 1.15, 15.0
    vb = [bm.verts.new(F.p(lo * math.cos(k * math.pi / 3), lo * math.sin(k * math.pi / 3), 1.75)) for k in range(6)]
    vt = [bm.verts.new(F.p(hi * math.cos(k * math.pi / 3), hi * math.sin(k * math.pi / 3), 1.75 + H_)) for k in range(6)]
    ap = bm.verts.new(F.p(0.0, 0.0, 1.75 + H_ + 2.2))
    bm.faces.new(list(reversed(vb)))
    for k in range(6):
        bm.faces.new((vb[k], vb[(k + 1) % 6], vt[(k + 1) % 6], vt[k]))
        bm.faces.new((vt[k], vt[(k + 1) % 6], ap))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, "SN_Carved")
    # faixa de runa vertical em cada face, na cor do portal para onde a face aponta
    for i, (key, aid) in enumerate(L.PORTALS):
        a = math.radians(L.PORTAL_ANG[i])
        X, Zr = math.cos(a), math.sin(a)
        dirl = V((-X, Zr, 0.0))                           # direcao local (x = -X, y = +Z)
        for k in range(4):
            z0 = 3.0 + k * 3.2
            t = (z0 - 1.75) / H_
            rad = lo + (hi - lo) * t + 0.06
            c = dirl * rad
            beam(b, F, (c.x, c.y, z0), (c.x, c.y, z0 + 2.2), 0.35, 0.5, WORLD_COL[key])
            side = V((-dirl.y, dirl.x, 0.0)) * 0.55
            beam(b, F, (c.x - side.x, c.y - side.y, z0 + 0.5), (c.x + side.x, c.y + side.y, z0 + 1.4), 0.25, 0.3,
                 WORLD_COL[key])
    cyl(b, F, (0, 0, 1.75 + H_ + 2.2), (0, 0, 1.75 + H_ + 2.6), 1.4, "SN_Bronze", seg=12)
    crystal_cluster(b, F, 0.0, 0.0, 1.75 + H_ + 2.6, 1.3, "SN_CrystalAmber", seed="isle_top")
    moss_patch(b, F, 3.6, -3.0, 0.57, 2.5, 1.8, seed="ism")
    col(8.4, 8.4, 2.0, F.p(0, 0, 0.9))
    col(4.0, 4.0, H_ + 4.0, F.p(0, 0, 1.75 + (H_ + 4.0) / 2))
    # colisao do patio (faixas, topo 7,0)
    z = -R
    while z < R - 1e-6:
        z1 = min(R, z + 4.0)
        zm = max(abs(z), abs(z1)) if z * z1 > 0 else 0.0
        hw = math.sqrt(max(0.0, R * R - zm * zm))
        if hw > 0.5:
            col(2 * hw, z1 - z, 1.0, RB(cx, cz + (z + z1) / 2, L.Y_PLAZA - 0.5))
        z = z1
    fm_lib.light("L_SN_IsleStone", "POINT", F.p(0, 0, 1.75 + H_ + 4.0), 900.0, (1.0, 0.7, 0.35), 1.0)
    fm_lib.marker("LETREIRO_Ilha", F.p(0, 0, 26.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"texto": "ILHA DOS PORTAIS", "alcance": 240})
    fm_lib.marker("VFX_Rune_IsleStone", F.p(0, 0, 3.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "rune", "rate": 4})
    fm_lib.marker("VFX_Dust_Isle", F.p(0, 0, 8.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "dust", "rate": 4})


def gate_isle(b):
    """portico de entrada da ilha (lado da ponte): arco com o letreiro CAMINHO DOS MUNDOS lido por quem chega"""
    x = L.ISLE_BRIDGE["x_isle"] - 6.0
    z = L.ISLE_BRIDGE["z"]
    F = Fr.rbx(x, z, L.Y_PLAZA, 1.0, 0.0)            # +y local = leste (para a ponte, quem chega)
    h_spring, w = 11.0, 12.0
    stone_arch(b, F, 0.0, w, h_spring, depth=3.0, ring=1.6, mat="SN_Ashlar", pier=3.2, pier_mat="SN_Carved",
               seed="isgate", missing=(), key_mat="SN_Carved", n=11)
    Ft = Fr(F.p(0, 1.62, 0), (F.f.x, F.f.y))
    bb(b, Ft, -8.6, 8.6, -0.3, 0.05, h_spring + w / 2 + 1.8, h_spring + w / 2 + 3.6, "SN_Carved", bevel=0.08)
    text(b, Ft, "CAMINHO DOS MUNDOS", 0.78, "SN_Gold", 0.0, 0.08, h_spring + w / 2 + 2.7, thick=0.14, bold=True)
    for s in (-1, 1):
        px = s * (w / 2 + 1.6)
        bb(b, F, px - 2.2, px + 2.2, -2.2, 2.2, -0.8, 0.9, "SN_Ashlar_Dark", bevel=0.12)
        col(3.4, 3.4, h_spring + 1.0, F.p(px, 0, (h_spring + 1.0) / 2), F.yaw())
        banner(b, Fr(F.p(px, 1.62, 0), (F.f.x, F.f.y)), 0.0, 0.0, h_spring - 0.6, "SN_CanvasViolet", 2.2, 7.0,
               pole=False, emblem=False)
    ivy(b, Fr(F.p(0, 1.7, 0), (F.f.x, F.f.y)), w / 2 + 1.6, 0.0, h_spring - 0.4, 6.0, 2.5, seed="isgiv")


def gate_main(b):
    """cabeceira da ponte no plato: 2 pilares com braseiro, placa PORTAIS com seta e estandartes"""
    x = L.ISLE_BRIDGE["x_main"] + 6.0
    z = L.ISLE_BRIDGE["z"]
    F = Fr.rbx(x, z, L.Y_PLAZA, 1.0, 0.0)            # +y local = leste (para a praca)
    for s in (-1, 1):
        px = s * 8.6
        top = column(b, F, px, 0.0, L.Y_GRASS - 0.4 - L.Y_PLAZA, 13.0, r0=1.35, seed=("igm", s), moss=True)
        brazier(b, F, px, 0.0, top, 3.0, "L_SN_Brazier_IsleMain_%d" % s)
        col(3.2, 3.2, 14.0, F.p(px, 0, 7.0), F.yaw())
    worn_block(b, F, 0.0, 0.0, 15.6, (21.0, 2.0, 1.8), "SN_Carved", seed="igml", chips=2, bevel=0.15)
    Ft = Fr(F.p(0, 1.02, 0), (F.f.x, F.f.y))
    text(b, Ft, "PORTAIS", 0.95, "SN_Gold", 0.0, 0.0, 15.6, thick=0.16, bold=True)
    Ft2 = Fr(F.p(0, -1.02, 0), (-F.f.x, -F.f.y))
    text(b, Ft2, "SANTUARIO", 0.8, "SN_Gold", 0.0, 0.0, 15.6, thick=0.14, bold=True)


def bridge(b):
    """ponte antiga plato -> ilha (leste-oeste), tabuleiro na cota 7, arcos baixos sobre a agua, parapeitos"""
    z = L.ISLE_BRIDGE["z"]
    xa, xb, w = L.ISLE_BRIDGE["x_main"], L.ISLE_BRIDGE["x_isle"], L.ISLE_BRIDGE["w"]
    n_span = 3
    span = (xa - xb) / n_span
    for k in range(n_span):
        xm = xa - (k + 0.5) * span
        Fd = Fr.rbx(xm, z, L.Y_PLAZA, 0.0, -1.0)        # +y local = norte; x local = leste
        bb(b, Fd, -span / 2, span / 2, -w / 2, w / 2, -1.6, -0.02, "SN_Ashlar_Dark")
        r = rng("ibrd", k)
        y = -w / 2 + 0.6
        while y < w / 2 - 0.6:
            ln = r.uniform(2.6, 3.4)
            y1 = min(w / 2 - 0.6, y + ln)
            bb(b, Fd, -span / 2 + 0.05, span / 2 - 0.05, y + 0.06, y1 - 0.06, -0.12, 0.03, "SN_Plaza", bevel=0.05)
            y = y1
        for s in (-1, 1):
            Fp = Fd.sub(0.0, s * (w / 2 - 0.45), 0.0, 0.0)
            ruin_wall(b, Fp, -span / 2, span / 2, 0.0, 2.6 if (k + s) % 3 else 1.6, 0.9, "SN_Ashlar", seed=("ibp", k, s),
                      ruin=0.25 if (k + s) % 3 else 0.55, course=0.9)
            col(span, 0.9, 2.6, Fd.p(0, s * (w / 2 - 0.45), 1.3), Fd.yaw())
        # arco por baixo (plano do arco ao longo da ponte)
        Fs = Fr(RB(xm, z, 0.0), (0.0, 1.0))           # f = Blender +y (norte); t = +x (leste): arco ao longo de x
        stone_arch(b, Fs, 0.0, span - 4.0, 0.6, depth=w - 0.8, ring=1.2, mat="SN_Ashlar", pier=4.0,
                   pier_mat="SN_Ashlar_Dark", seed=("iba", k), n=9, moss=False)
        col(span, w, 1.6, RB(xm, z, L.Y_PLAZA - 0.8))
    for x in (xa, xb):
        for s in (-1, 1):
            Fb = Fr.rbx(x, z + s * (w / 2 - 1.4), L.Y_PLAZA, 0.0, -1.0)
            brazier(b, Fb, 0.0, 0.0, 0.0, 3.2, "L_SN_Brazier_IsleBr_%d_%d" % (int(-x), s))
    # cabeceiras: lajes ate dentro de cada terra (fecha o vao entre o barranco e o 1o vao)
    for (x0, x1) in ((xa - 1.0, xa + 9.0), (xb - 9.0, xb + 1.0)):
        Fe = Fr.rbx((x0 + x1) / 2, z, L.Y_PLAZA, 0.0, -1.0)
        bb(b, Fe, -(x1 - x0) / 2, (x1 - x0) / 2, -w / 2 - 0.6, w / 2 + 0.6, L.Y_WATER - 2.0 - L.Y_PLAZA, -0.02,
           "SN_Ashlar_Dark", bevel=0.1)
        bb(b, Fe, -(x1 - x0) / 2 + 0.1, (x1 - x0) / 2 - 0.1, -w / 2 + 0.6, w / 2 - 0.6, -0.12, 0.03, "SN_Plaza", bevel=0.05)
        col(x1 - x0, w + 1.2, 1.0, RB((x0 + x1) / 2, z, L.Y_PLAZA - 0.5))
    fm_lib.marker("SAFE_IlhaPonte", RB((xa + xb) / 2, z, L.Y_PLAZA + 0.2), (0, 0, 0), 1.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"kind": "safe"})


def rim(b):
    """anel de ruinas da borda da ilha: colunas entre os portais (atras), cristais e entulho"""
    cx, cz = L.PORTAL_ISLE_C
    r = rng("isrim")
    angs = L.PORTAL_ANG
    for i in range(len(angs) - 1):
        a = math.radians((angs[i] + angs[i + 1]) / 2)
        rr_ = L.PORTAL_R + 6.0
        x, z = cx + rr_ * math.cos(a), cz + rr_ * math.sin(a)
        F = Fr.rbx(x, z, L.Y_GRASS - 0.3, -math.cos(a), -math.sin(a))
        broken = None if i % 2 == 0 else r.uniform(7.0, 11.0)
        column(b, F, 0.0, 0.0, 0.0, 17.0, r0=1.3, seed=("isc", i), broken=broken)
        col(3.0, 3.0, 17.0, RB(x, z, L.Y_GRASS + 8.0))
        if i % 2 == 1:
            crystal_cluster(b, F, 2.4, -1.5, 0.0, 1.2, list(WORLD_COL.values())[i] if False else "SN_CrystalBlue",
                            seed=("iscr", i))
        rubble(b, F, 2.5, -2.0, 0.0, 2.6, 6, "SN_Ashlar", seed=("isr", i))
    # 2 cristais grandes atras do portal central (oeste), emoldurando a ilha vista da ponte
    for s, m in ((-1, "SN_CrystalAmber"), (1, "SN_CrystalBlue")):
        a = math.radians(180.0 + s * 44.0)
        rr_ = L.PORTAL_R + 16.0
        F = Fr.rbx(cx + rr_ * math.cos(a), cz + rr_ * math.sin(a), L.Y_GRASS - 0.2, 0.0, 1.0)
        rubble(b, F, 0.0, 0.0, 0.0, 4.0, 9, "SN_Ashlar_Dark", seed=("isbig", s))
        crystal_cluster(b, F, 0.0, 0.0, 0.0, 2.2, m, seed=("isbigc", s))


def build():
    SL.register()
    for k, c in WORLD_RGB.items():
        if k not in fm_lib.MATS:
            fm_lib.MATS[k] = (fm_lib.S(*c), 0.5, 0.0, 2.2, fm_lib.S(*c), 0.0)
    for k in WORLD_RGB:
        if ("SN_Rune", "Neon", 0.0, False) in fm_lib.RBX_RULES:
            pass
    fm_lib.make_materials()
    b = SL.Build("WB_Court_Isle", COLL_C)
    court(b)
    gate_isle(b)
    rim(b)
    objs = b.finish()
    b = SL.Build("WB_Exit_IsleBridge", COLL_B)
    bridge(b)
    gate_main(b)
    objs += b.finish()
    return objs
