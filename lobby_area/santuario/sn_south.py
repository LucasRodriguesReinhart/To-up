# sn_south.py - SETOR SUL: terraco da chegada (spawn), escadarias, os 2 GOLENS-GUARDIOES de pedra (conceito H),
# avenida das colunas, portao arruinado e a PONTE ANTIGA ate a Ilha 1 (link (0, 6, 222)).
# Coordenadas Roblox nos parametros; frames locais com +y apontando para o NORTE (para a praca) salvo indicacao.
import math

import bmesh
import fm_lib
import sn_lib as SL
import sn_layout as L
from mathutils import Matrix, Vector
from sn_kit import (column, worn_block, moss_patch, ivy, rng, brazier, rune_glyphs, ruin_wall, stone_arch,
                    crystal_cluster, rubble, flower_bed, chip_bm, _box_bm)
from wb_kit import Fr, bb, beam, cyl, lathe, poly_prism, text, banner
from wb_lib import RB

V = Vector
RAD = math.radians
COLL = "07_EXIT"
AREA = "Exit"
X0, X1, Z0, Z1 = L.SPAWN_TERRACE            # -22, 22, 52, 80
YS = L.Y_SPAWN                               # 10
ST = L.STAIR                                 # x0 -14, x1 14, z_top 52, n 5, rise .6, run 1.7
AV = L.AVENUE                                # -11, 11, 80, 146
Z_AV0 = Z1 + ST["n"] * ST["run"]             # pe da escada sul (88.5)


def F_n(x, z, y):
    """frame olhando o NORTE (para a praca): +y local = -Z Roblox"""
    return Fr.rbx(x, z, y, 0.0, -1.0)


def col(dx, dy, dz, p, yaw=0.0):
    fm_lib.col_box(AREA, (dx, dy, dz), p, (0, 0, yaw))


# ------------------------------------------------------------------ terraco + escadas
def terrace(b):
    F = F_n(0.0, (Z0 + Z1) / 2, L.Y_PLAZA)
    hz = (Z1 - Z0) / 2
    y_top = YS - L.Y_PLAZA                   # 3.0 acima da praca
    # embasamento de cantaria (bloco a bloco nas faces) + capa de lajes
    from sn_shop import ashlar_wall
    bb(b, F, X0 + 0.6, X1 - 0.6, -hz + 0.6, hz - 0.6, L.Y_GRASS - 0.6 - L.Y_PLAZA, y_top - 0.3, "SN_Ashlar_Dark")
    for (fx_, side) in ((0, "E"), (0, "W")):
        pass
    for s in (-1, 1):                        # laterais leste/oeste
        Fs = F.sub(s * (X1 - 0.6), 0.0, 0.0, -90 * s)
        ashlar_wall(b, Fs, -hz, hz, L.Y_GRASS - 0.4 - L.Y_PLAZA, y_top - 0.3, -0.6, 0.6, seed=("tw", s), course=1.1)
    Fb = F.sub(0.0, -hz + 0.6, 0.0, 180)      # face sul (para a avenida), com o vao da escada sul
    ashlar_wall(b, Fb, X0, X1, L.Y_GRASS - 0.4 - L.Y_PLAZA, y_top - 0.3, -0.6, 0.6,
                holes=[(ST["x0"], ST["x1"], -2, 20)], seed="tws", course=1.1)
    Ff = F.sub(0.0, hz - 0.6, 0.0, 0)         # face norte (para a praca), com o vao da escadaria
    ashlar_wall(b, Ff, X0, X1, L.Y_GRASS - 0.4 - L.Y_PLAZA, y_top - 0.3, -0.6, 0.6,
                holes=[(ST["x0"], ST["x1"], -2, 20)], seed="twn", course=1.1)
    # cornija + lajes do topo
    bb(b, F, X0 - 0.3, X1 + 0.3, -hz - 0.3, hz + 0.3, y_top - 0.3, y_top - 0.02, "SN_Carved", bevel=0.1)
    r = rng("terr")
    yy = -hz + 0.6
    while yy < hz - 0.6:
        d = r.uniform(2.4, 3.2)
        x = X0 + 0.6 - r.uniform(0, 1.6)
        while x < X1 - 0.6:
            ln = r.uniform(2.6, 4.0)
            xa, xb = max(X0 + 0.6, x), min(X1 - 0.6, x + ln)
            if xb - xa > 0.6:
                bb(b, F, xa + 0.06, xb - 0.06, yy + 0.06, min(hz - 0.6, yy + d) - 0.06, y_top - 0.02,
                   y_top + 0.06 + r.uniform(-0.02, 0.0), "SN_Plaza", bevel=0.05)
            x += ln
        yy += d
    # circulo de chegada (runas) no ponto de spawn
    sy = (Z0 + Z1) / 2 - L.SPAWN[1]          # local y do spawn (+y = norte)
    n = 24
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        for rr_, w_, m_ in ((5.2, 0.5, "SN_Bronze"), (4.3, 0.28, "SN_Rune")):
            beam(b, F, (rr_ * math.cos(a0), sy + rr_ * math.sin(a0), y_top + 0.1),
                 (rr_ * math.cos(a1), sy + rr_ * math.sin(a1), y_top + 0.1), w_, 0.1, m_)
    for k in range(6):
        a = 2 * math.pi * k / 6 + 0.26
        beam(b, F, (1.2 * math.cos(a), sy + 1.2 * math.sin(a), y_top + 0.1),
             (3.6 * math.cos(a), sy + 3.6 * math.sin(a), y_top + 0.1), 0.25, 0.1, "SN_Rune")
    # pedestal do correio (o MailBox do jogo pousa aqui) e bancos de pedra laterais virados para a praca
    mx, mz = L.MAILBOX
    Fm = F_n(mx, mz, YS)
    bb(b, Fm, -1.6, 1.6, -1.2, 1.2, 0.0, 0.35, "SN_Carved", bevel=0.08)
    # parapeito baixo arruinado nas bordas leste/oeste (deixa as escadas livres)
    for s in (-1, 1):
        Fs = F.sub(s * (X1 - 0.9), 0.0, y_top, -90 * s)
        ruin_wall(b, Fs, -hz + 1.0, hz - 1.0, 0.0, 2.4, 0.9, "SN_Ashlar", seed=("par", s), ruin=0.5, course=0.8)
    # escadarias: norte (para a praca) e sul (para a avenida), 5 degraus de 0,6
    for (sgn, z_top) in ((1, Z0), (-1, Z1)):
        for k in range(ST["n"]):
            top = y_top - ST["rise"] * (k + 1) + 0.06
            za = z_top - sgn * ST["run"] * k
            zb = za - sgn * ST["run"]
            Fz = F_n(0.0, (za + zb) / 2, L.Y_PLAZA)
            bb(b, Fz, ST["x0"], ST["x1"], -ST["run"] / 2 - 0.02, ST["run"] / 2 + 0.02, L.Y_GRASS - 0.6 - L.Y_PLAZA,
               top + ST["rise"] - 0.06 if k == 0 else top + ST["rise"], "SN_Ashlar" if k % 2 else "SN_Carved", bevel=0.08)
            col(ST["x1"] - ST["x0"], ST["run"], top + ST["rise"] - (L.Y_GRASS - 0.6 - L.Y_PLAZA),
                RB(0.0, (za + zb) / 2, L.Y_PLAZA + (top + ST["rise"] + L.Y_GRASS - 0.6 - L.Y_PLAZA) / 2))
        # muretas laterais das escadas com braseiros
        for s in (-1, 1):
            zz0, zz1 = sorted((z_top, z_top - sgn * ST["run"] * ST["n"]))
            Fw = F_n(s * (ST["x1"] + 0.9), (zz0 + zz1) / 2, L.Y_PLAZA)
            bb(b, Fw, -0.9, 0.9, -(zz1 - zz0) / 2, (zz1 - zz0) / 2, L.Y_GRASS - 0.6 - L.Y_PLAZA, y_top + 0.9, "SN_Carved",
               bevel=0.1)
            brazier(b, F_n(s * (ST["x1"] + 0.9), z_top, YS + 0.9), 0.0, 0.0, 0.0, 3.0,
                    "L_SN_Brazier_Stair_%d_%d" % (sgn, s))
    col(X1 - X0, Z1 - Z0, YS - (L.Y_GRASS - 0.6), RB(0.0, (Z0 + Z1) / 2, (YS + L.Y_GRASS - 0.6) / 2))


# ------------------------------------------------------------------ golens-guardioes (estatuas de pedra)
def golem(b, F, s=1.0, seed=0, hammer_side=1):
    """golem de pedra ajoelhado (estatua antiga): blocos lascados, olhos de runa apagados-ambar, martelo apoiado"""
    r = rng("golem", seed)
    def blk(cx, cy, cz, dims, mat="SN_Ashlar", tilt=(0, 0), turn=0.0, chips=2):
        worn_block(b, F, cx * s, cy * s, cz * s, tuple(d * s for d in dims), mat, seed=("gb", seed, cx, cz), chips=chips,
                   bevel=0.18 * s, turn=turn, tilt=tilt)
    # pedestal
    bb(b, F, -4.4 * s, 4.4 * s, -4.0 * s, 4.0 * s, 0.0, 1.6 * s, "SN_Carved", bevel=0.15)
    bb(b, F, -4.8 * s, 4.8 * s, -4.4 * s, 4.4 * s, 0.0, 0.5 * s, "SN_Ashlar_Dark", bevel=0.12)
    z0 = 1.6
    # pernas ajoelhadas: coxa + canela (joelho no chao)
    for sx in (-1, 1):
        blk(sx * 1.6, 0.6, z0 + 1.1, (1.8, 3.4, 2.0), tilt=(-10, 0))
        blk(sx * 1.6, -1.6, z0 + 0.7, (1.9, 2.2, 1.4), "SN_Ashlar_Dark")
    # tronco largo + peito + ombros
    blk(0.0, 0.2, z0 + 4.6, (5.6, 3.6, 4.6), tilt=(6, 0))
    blk(0.0, 0.9, z0 + 6.4, (6.4, 3.0, 2.4), "SN_Carved", tilt=(8, 0))
    for sx in (-1, 1):
        blk(sx * 4.0, 0.4, z0 + 7.0, (2.6, 2.8, 2.4), tilt=(0, sx * 10))
        # bracos: um apoiado no cabo do martelo, outro no joelho
        blk(sx * 4.4, 0.8, z0 + 4.6, (1.7, 1.8, 3.0))
        blk(sx * 4.2, 1.8, z0 + 2.6, (2.0, 2.1, 1.6), "SN_Ashlar_Dark")
    # cabeca pequena com olhos de runa (ambar fraco)
    blk(0.0, 1.3, z0 + 8.9, (2.6, 2.4, 2.2), "SN_Carved", turn=r.uniform(-8, 8))
    for sx in (-1, 1):
        bb(b, F, sx * 0.55 * s - 0.25 * s, sx * 0.55 * s + 0.25 * s, 2.45 * s, 2.6 * s, (z0 + 9.0) * s, (z0 + 9.3) * s,
           "SN_Rune")
    # runas no peito
    Fp = Fr(F.p(0, 2.42 * s, 0), (F.f.x, F.f.y))
    rune_glyphs(b, Fp, -1.4 * s, 1.4 * s, (z0 + 6.0) * s, h=1.1 * s, n=2, seed=("gr", seed), depth=0.18)
    # martelo de pedra apoiado de pe, cabeca no chao
    hx = hammer_side * 3.4 * s
    bb(b, F, hx - 1.4 * s, hx + 1.4 * s, 2.0 * s, 4.4 * s, z0 * s, (z0 + 2.2) * s, "SN_Iron", bevel=0.25)
    cyl(b, F, (hx, 3.2 * s, (z0 + 2.2) * s), (hx, 3.2 * s, (z0 + 7.4) * s), 0.35 * s, "SN_WoodAged", seg=8)
    moss_patch(b, F, 0.0, 0.4 * s, (z0 + 7.65) * s, 5.0 * s, 2.4 * s, seed=("gm", seed))
    moss_patch(b, F, hammer_side * 4.0 * s, 0.4 * s, (z0 + 8.25) * s, 2.0 * s, 2.0 * s, seed=("gm2", seed), round_=True)
    col(9.0 * s, 8.4 * s, 11.0 * s, F.p(0, 0, 5.5 * s), F.yaw())


# ------------------------------------------------------------------ avenida das colunas
def avenue(b):
    x0, x1, z0, z1 = AV
    z0 = Z_AV0
    F = F_n(0.0, (z0 + z1) / 2, L.Y_PLAZA)
    hz = (z1 - z0) / 2
    r = rng("ave")
    # lajeado (fiadas atravessadas), meio-fio e faixa central de runas
    yy = -hz
    while yy < hz:
        d = r.uniform(2.2, 3.0)
        x = x0 - r.uniform(0, 1.6)
        while x < x1:
            ln = r.uniform(2.6, 4.2)
            xa, xb = max(x0, x), min(x1, x + ln)
            if xb - xa > 0.6:
                bb(b, F, xa + 0.06, xb - 0.06, yy + 0.06, min(hz, yy + d) - 0.06, -0.5, 0.02 + r.uniform(-0.03, 0.0),
                   "SN_Plaza", bevel=0.05)
            x += ln
        yy += d
    bb(b, F, x0 - 0.2, x1 + 0.2, -hz, hz, -0.8, -0.3, "SN_Ashlar_Dark")
    col(x1 - x0 + 0.4, 2 * hz, 1.0, RB(0.0, (z0 + z1) / 2, L.Y_PLAZA - 0.5))
    for s in (-1, 1):
        bb(b, F, s * x1 - 0.5 * (1 if s > 0 else -1) * 0 - 0.5, s * x1 + 0.5, -hz, hz, -0.5, 0.18, "SN_Carved", bevel=0.08) \
            if s > 0 else bb(b, F, s * x1 - 0.5, s * x1 + 0.5, -hz, hz, -0.5, 0.18, "SN_Carved", bevel=0.08)
    for k in range(int(2 * hz / 6.0)):
        y = -hz + 3.0 + k * 6.0
        # chevrons acesos apontando para o portao (sul = -y local)
        beam(b, F, (-1.3, y + 0.9, 0.04), (0.0, y - 0.4, 0.04), 0.28, 0.1, "SN_Rune")
        beam(b, F, (1.3, y + 0.9, 0.04), (0.0, y - 0.4, 0.04), 0.28, 0.1, "SN_Rune")
    # colunatas dos dois lados (x +-14): colunas a cada 9, algumas partidas, lintel em alguns vaos, uma caida
    cols_y = [-hz + 4.0 + 9.0 * k for k in range(int((2 * hz - 6.0) / 9.0) + 1)]
    for s in (-1, 1):
        for k, y in enumerate(cols_y):
            broken = None
            if (k + (s > 0)) % 4 == 2:
                broken = r.uniform(4.0, 8.0)
            top = column(b, F, s * 14.0, y, -0.6 + L.Y_GRASS - L.Y_PLAZA + 0.6, 15.0, r0=1.15, seed=("avc", s, k),
                         broken=broken)
            col(3.0, 3.0, 15.0, F.p(s * 14.0, y, 7.0), F.yaw())
            if broken is None and k + 1 < len(cols_y) and (k + (s > 0)) % 4 not in (1, 2):
                worn_block(b, F, s * 14.0, y + 4.5, top + 0.75, (2.6, 11.6, 1.5), "SN_Ashlar", seed=("avl", s, k),
                           chips=3, bevel=0.12)
            if broken is not None:
                # tambores caidos ao lado da coluna partida
                for j in range(2):
                    cyl(b, F, (s * (17.0 + j * 2.6), y + r.uniform(-2, 2), 1.15 - 0.2),
                        (s * (17.0 + j * 2.6) + r.uniform(-0.5, 0.5), y + r.uniform(-2, 2) + 2.6, 1.15 - 0.2), 1.1,
                        "SN_Ashlar", seg=14)
        # canteiros de flores azuis entre as colunas e braseiros alternados
        for k, y in enumerate(cols_y[:-1]):
            ym = y + 4.5
            if k % 2 == 0:
                flower_bed(b, F, s * 13.0, ym, -0.2 + 0.0, 2.2, 5.0, 14, seed=("avf", s, k))
            else:
                brazier(b, F, s * 12.2, ym, 0.0, 3.4, "L_SN_Brazier_Av_%d_%d" % (s, k))
        moss_patch(b, F, s * 15.0, -10.0, 0.05, 3.0, 8.0, seed=("avm", s))


# ------------------------------------------------------------------ portao arruinado
def gate(b):
    gx, gz = L.GATE
    F = F_n(gx, gz, L.Y_PLAZA)
    # 2 pilones macicos de cantaria + arco grande com aduelas faltando (ruina) + estandartes
    h_spring = 16.0
    w = 20.0
    top = stone_arch(b, F, 0.0, w, h_spring, depth=5.0, ring=2.2, mat="SN_Ashlar", pier=5.0, pier_mat="SN_Carved",
                     seed="gate", missing=(8, 9), key_mat="SN_Carved", n=13)
    for s in (-1, 1):
        px = s * (w / 2 + 2.5)
        bb(b, F, px - 3.2, px + 3.2, -3.2, 3.2, -0.8, 1.2, "SN_Ashlar_Dark", bevel=0.12)
        col(5.4, 5.4, h_spring, F.p(px, 0, h_spring / 2), F.yaw())
        banner(b, Fr(F.p(px, 2.7, 0), (F.f.x, F.f.y)), 0.0, 0.0, h_spring - 1.0, "SN_CanvasRed", 3.0, 9.0, pole=False,
               emblem=False)
        brazier(b, F, px, 6.2, 0.0, 3.8, "L_SN_Brazier_Gate_%d" % s)
    # aduelas caidas no chao
    r = rng("gaterub")
    for k in range(4):
        worn_block(b, F, r.uniform(4.0, 9.0), r.uniform(-6, -2), 0.8, (2.4, 4.6, 1.6), "SN_Ashlar", seed=("gr", k),
                   chips=3, turn=r.uniform(0, 180), tilt=(r.uniform(-20, 20), r.uniform(-20, 20)))
    rubble(b, F, 7.0, -4.0, 0.0, 4.0, 10, "SN_Ashlar", seed="gaterub2")
    ivy(b, Fr(F.p(0, 2.6, 0), (F.f.x, F.f.y)), -w / 2 - 2.5, 0.0, h_spring - 0.5, 9.0, 3.5, seed="giv")
    # letreiro (na face SUL, lido por quem chega pela ponte) e na face norte (quem sai)
    for (fy, txt) in ((-1, "SANTUARIO DO DEUS-FERREIRO"), (1, "ILHA 1 - NARUTO")):
        Ft = Fr(F.p(0, fy * 2.62, 0), (fy * F.f.x, fy * F.f.y))
        bb(b, Ft, -8.6, 8.6, -0.4, 0.05, h_spring + 3.6, h_spring + 5.4, "SN_WoodAged", bevel=0.08)
        text(b, Ft, txt, 0.62 if fy < 0 else 0.7, "SN_Gold", 0.0, 0.08, h_spring + 4.5, thick=0.12, bold=True)
        for sx in (-6.5, 6.5):
            beam(b, Ft, (sx, -0.18, h_spring + 5.4), (sx * 0.8, -0.18, h_spring + 9.6), 0.08, 0.08, "SN_Chain")


# ------------------------------------------------------------------ ponte antiga
def bridge(b):
    bx = L.BRIDGE["x"]
    z0, z1, w = L.BRIDGE["z0"], L.BRIDGE["z1"], L.BRIDGE["w"]
    n_span = 6
    span = (z1 - z0) / n_span
    y_a, y_b = L.Y_PLAZA, L.Y_ISLE
    for k in range(n_span):
        za, zb = z0 + k * span, z0 + (k + 1) * span
        ya = y_a + (y_b - y_a) * k / n_span
        yb_ = y_a + (y_b - y_a) * (k + 1) / n_span
        zm = (za + zb) / 2
        ym = (ya + yb_) / 2
        F = Fr.rbx(bx, zm, 0.0, 1.0, 0.0)      # +y local = leste; x local = -Z ... usa plano x-z do arco ao longo da ponte
        Fa = Fr.rbx(bx, zm, 0.0, -1.0, 0.0)
        # tabuleiro (lajes) inclinado levemente
        Fd = F_n(bx, zm, ym)
        bb(b, Fd, -w / 2, w / 2, -span / 2, span / 2, -1.6, -0.02, "SN_Ashlar_Dark")
        r = rng("brd", k)
        x = -w / 2 + 0.6
        while x < w / 2 - 0.6:
            ln = r.uniform(2.6, 3.6)
            xb_ = min(w / 2 - 0.6, x + ln)
            bb(b, Fd, x + 0.06, xb_ - 0.06, -span / 2 + 0.05, span / 2 - 0.05, -0.12, 0.03, "SN_Plaza", bevel=0.05)
            x = xb_
        # parapeitos (alguns trechos quebrados)
        for s in (-1, 1):
            ruin_wall(b, Fd.sub(s * (w / 2 - 0.45), 0.0, 0.0, 90), -span / 2, span / 2, 0.0, 2.6 if (k + s) % 3 else 1.4,
                      0.9, "SN_Ashlar", seed=("bp", k, s), ruin=0.25 if (k + s) % 3 else 0.6, course=0.9)
        # arco por baixo (pilares na agua) - plano do arco = plano x-z do frame Fa (ao longo da ponte)
        Fs = Fr(RB(bx, zm, 0.0), (1.0, 0.0))   # f = +X Blender (leste); t = (0,-1) -> Blender -y = Roblox +Z
        stone_arch(b, Fs, 0.0, span - 4.4, max(0.6, ym - 1.6 - 2.2 - (span - 4.4) / 2), depth=w - 0.8, ring=1.4,
                   mat="SN_Ashlar", pier=4.4, pier_mat="SN_Ashlar_Dark", seed=("ba", k), n=9, moss=False)
        col(w, span, 1.6, RB(bx, zm, ym - 0.8))
        for s in (-1, 1):
            col(0.9, span, 2.6, RB(bx + s * (w / 2 - 0.45), zm, ym + 1.3))
        if k % 2 == 1:
            for s in (-1, 1):
                brazier(b, Fd, s * (w / 2 - 1.6), span / 2, 0.0, 3.2, "L_SN_Brazier_Br_%d_%d" % (k, s))
    # ENCONTRO (cabeceira) da ponte: laje de pedra da borda do plato ate o 1o vao + muros de arrimo ate a agua
    Fe = F_n(bx, (z0 - 6.0 + z0 + 1.5) / 2, L.Y_PLAZA)
    he = (7.5) / 2
    bb(b, Fe, -w / 2 - 0.6, w / 2 + 0.6, -he, he, L.Y_WATER - 2.0 - L.Y_PLAZA, -0.02, "SN_Ashlar_Dark", bevel=0.1)
    r = rng("enc")
    x = -w / 2 + 0.6
    while x < w / 2 - 0.6:
        ln = r.uniform(2.6, 3.6)
        xb_ = min(w / 2 - 0.6, x + ln)
        bb(b, Fe, x + 0.06, xb_ - 0.06, -he + 0.05, he - 0.05, -0.12, 0.03, "SN_Plaza", bevel=0.05)
        x = xb_
    for s_ in (-1, 1):
        bb(b, Fe, s_ * (w / 2 + 0.6) - 0.6, s_ * (w / 2 + 0.6) + 0.6, -he, he, -0.02, 1.2, "SN_Carved", bevel=0.1)
    col(w + 1.2, 7.5, 1.0, RB(bx, (z0 - 6.0 + z0 + 1.5) / 2, L.Y_PLAZA - 0.5))
    # pilares de base na agua (fundacoes visiveis)
    for k in range(n_span + 1):
        zz = z0 + k * span
        Fp = F_n(bx, zz, L.Y_WATER - 3.0)
        bb(b, Fp, -w / 2 - 0.6, w / 2 + 0.6, -2.6, 2.6, 0.0, 3.4, "SN_Ashlar_Dark", bevel=0.12)


def build():
    SL.register()
    fm_lib.make_materials()
    b = SL.Build("WB_Exit_Spawn", COLL)
    terrace(b)
    for s in (-1, 1):
        Fg = F_n(s * 18.4, Z0 + 3.6, YS)
        golem(b, Fg, 0.85, seed=("gol", s), hammer_side=-s)
    objs = b.finish()
    b = SL.Build("WB_Exit_Avenue", COLL)
    avenue(b)
    objs += b.finish()
    b = SL.Build("WB_Exit_Gate", COLL)
    gate(b)
    objs += b.finish()
    b = SL.Build("WB_Exit_Bridge", COLL)
    bridge(b)
    objs += b.finish()
    fm_lib.marker("SPAWN_Lobby", RB(L.SPAWN[0], L.SPAWN[1], YS + 0.1), (0, 0, math.pi), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"kind": "spawn", "olha": "norte (forja)"})
    fm_lib.marker("ISLE_Link", RB(*([L.ISLE_LINK[0], L.ISLE_LINK[2], L.ISLE_LINK[1]])), (0, 0, 0), 2.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"kind": "ilha1"})
    return objs
