# wb_exit.py - SAIDA da vila Wolfberg: PORTAO (2 torres redondas de pedra com telhado conico, arco de aduelas, portas
# de madeira abertas, tabua "WOLFBERG" / "BOA SORTE NAS MINAS", lanternas, estandartes, muralhas baixas com canteiro)
# e a PONTE DE PEDRA reta ate a Ilha 1 (tabuleiro de paralelepipedo descendo de Y 7 a Y 6, 3 arcos de meio ponto com
# os pes no leito do lago, parapeitos com pilaretes e postes de lanterna, alargamento no desembarque x -12..12).
# Contrato: passagem do portao livre (x -8..8, pe-direito 16 no interior / 15 no arco), ponte termina em ISLE_LINK
# (0, 6, 222). Coordenadas ROBLOX na planta (wb_layout); frames do kit (Fr.rbx) para construir.
import math
import random

import bmesh
import fm_lib
import wb_lib as W
import wb_layout as L
from wb_kit import (Fr, bb, bx, beam, cyl, poly_wall, poly_prism, lathe, text, lantern, lantern_wall, lantern_post,
                    banner, bush, ST, STD, TB, PK, IR, TXT, RAD)
from wb_lib import RB, V

PREFIX = "WB_Exit_"
COLL = "07_EXIT"
SEED = 1707
# cameras (nome, olho Roblox, alvo Roblox, lente)
CAMS = [
    ("CAM_WB_Exit_Ponte", (0.0, 13.0, 180.0), (0.0, 16.0, 120.0), 24),      # da ponte olhando a vila
    ("CAM_WB_Exit_Rua", (0.0, 14.0, 110.0), (0.0, 14.0, 160.0), 24),        # da rua sul olhando o portao
    ("CAM_WB_Exit_Lado", (44.0, 9.0, 185.0), (0.0, 7.0, 185.0), 28),        # de lado, ponte baixa (arcos)
    ("CAM_WB_Exit_Aerea", (60.0, 120.0, 240.0), (0.0, 5.0, 170.0), 24),     # aerea
]

# ------------------------------------------------------------------ medidas (locais; piso do portao = 0 = Y 7)
GX, GZ = L.GATE                     # (0, 142)
Y0 = L.Y_PAVE                       # 7
HW = L.GATE_HW                      # 8  (meio vao)
TR = L.GATE_TOWER_W / 2.0           # 4.5 (raio da torre)
TXC = HW + TR                       # 12.5 (centro das torres)
TH = L.GATE_TOWER_H                 # 26 (corpo da torre)
GD = 5.0                            # meia profundidade do bloco do portao (z 137..147)
FACE = 0.7                          # camada da face com o arco (atras dela o corredor tem teto plano em 16)
SPRING, CROWN = 7.0, 15.0           # nascenca e fecho do arco (raio 8)
CEIL = 16.0                         # teto do corredor (as folhas abertas de 14,8 passam por baixo)
WTOP = 20.0                         # topo da muralha do portao (Y 27)
BZ0, BZ1, BWID = L.BRIDGE["z0"], L.BRIDGE["z1"], L.BRIDGE["w"]      # 148, 222, 16
BL = BZ1 - BZ0                      # 74
DROP = L.Y_PAVE - L.Y_ISLE          # 1.0
BH = BWID / 2.0                     # 8
LH = (L.ISLE_LANDING[1] - L.ISLE_LANDING[0]) / 2.0                  # 12 (meio desembarque)
FLARE0, FLARE1 = 60.0, 64.0         # y local onde o tabuleiro alarga de +-8 para +-12 (z 208..212)
PAR_W, PAR_H = 0.8, 2.4             # parapeito
COB_T, SLAB_T = 0.6, 0.7            # paralelepipedo + laje/cornija
ARCH_R, PIER_W = 7.0, 4.0           # arcos de meio ponto (vao 14) e pilares
SPRING_B = L.Y_BED - Y0             # -9: nascenca dos arcos no leito do lago (Y -2)
ARCHES = [(10.0, 24.0), (28.0, 42.0), (46.0, 60.0)]                 # y local (pe a pe) dos 3 arcos (z 158..208)
WATER_Z = L.Y_WATER - Y0            # -4.8


def zdeck(y):
    """cota local do topo do tabuleiro em y local (0 = z 148, Y 7) -> desce 1,0 ate y = 74"""
    return -DROP * y / BL


def deck_half(y):
    """meia largura do tabuleiro em y local (alarga de 8 a 12 entre FLARE0 e FLARE1)"""
    if y <= FLARE0:
        return BH
    if y >= FLARE1:
        return LH
    return BH + (LH - BH) * (y - FLARE0) / (FLARE1 - FLARE0)


# ------------------------------------------------------------------ helpers de malha (so deste modulo)
def wall_xz(b, F, pts, y0, y1, m):
    """poligono no plano (x, z) local extrudado de y0 a y1 (faces do arco, oitoes)"""
    bm = bmesh.new()
    a = [bm.verts.new(F.p(x, y0, z)) for (x, z) in pts]
    c = [bm.verts.new(F.p(x, y1, z)) for (x, z) in pts]
    n = len(pts)
    bm.faces.new(a)
    bm.faces.new(list(reversed(c)))
    for i in range(n):
        bm.faces.new((a[i], c[i], c[(i + 1) % n], a[(i + 1) % n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def prism_fn(b, F, pts_xy, ztop, thick, m):
    """prisma de um poligono local (x, y) cujo topo segue ztop(y) (plano inclinado) e a base fica thick abaixo"""
    bm = bmesh.new()
    top = [bm.verts.new(F.p(x, y, ztop(y))) for (x, y) in pts_xy]
    bot = [bm.verts.new(F.p(x, y, ztop(y) - thick)) for (x, y) in pts_xy]
    n = len(pts_xy)
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for i in range(n):
        bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def arch_ring(b, F, plane, cu, cv, ri, ro, w0, w1, n, m, a0=0.0, a1=180.0):
    """anel de aduelas (faixa fechada) de raio ri..ro em torno de (cu, cv) no plano 'xz' (u = x, v = z, espessura em y)
    ou 'yz' (u = y, v = z, espessura em x), de w0 a w1, angulos a0..a1 (graus, 0 = +u)"""
    def P(u, v, w):
        return F.p(u, w, v) if plane == "xz" else F.p(w, u, v)
    bm = bmesh.new()
    inn0, out0, inn1, out1 = [], [], [], []
    for k in range(n + 1):
        a = RAD(a0 + (a1 - a0) * k / n)
        cu_, sv_ = math.cos(a), math.sin(a)
        inn0.append(bm.verts.new(P(cu + ri * cu_, cv + ri * sv_, w0)))
        out0.append(bm.verts.new(P(cu + ro * cu_, cv + ro * sv_, w0)))
        inn1.append(bm.verts.new(P(cu + ri * cu_, cv + ri * sv_, w1)))
        out1.append(bm.verts.new(P(cu + ro * cu_, cv + ro * sv_, w1)))
    for k in range(n):
        bm.faces.new((inn0[k], out0[k], out0[k + 1], inn0[k + 1]))          # face w0
        bm.faces.new((inn1[k], inn1[k + 1], out1[k + 1], out1[k]))          # face w1
        bm.faces.new((out0[k], out1[k], out1[k + 1], out0[k + 1]))          # extradorso
        bm.faces.new((inn0[k], inn0[k + 1], inn1[k + 1], inn1[k]))          # intradorso
    bm.faces.new((inn0[0], inn1[0], out1[0], out0[0]))
    bm.faces.new((inn0[n], out0[n], out1[n], inn1[n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def pyramid(b, F, x, y, z0, z1, half, m):
    bm = bmesh.new()
    base = [bm.verts.new(F.p(x + sx * half, y + sy * half, z0)) for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    apex = bm.verts.new(F.p(x, y, z1))
    bm.faces.new(list(reversed(base)))
    for i in range(4):
        bm.faces.new((base[i], base[(i + 1) % 4], apex))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def arch_pts(cx, cz, r, n, a0=0.0, a1=180.0):
    return [(cx + r * math.cos(RAD(a0 + (a1 - a0) * k / n)), cz + r * math.sin(RAD(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


# ------------------------------------------------------------------ TORRE REDONDA
def tower(b, F, s):
    """torre de pedra no frame F (origem no centro da torre, piso 0): base escura, corpo, cordao, misulas, telhado
    conico de telha escura com beiral, seteiras, janelinha para a vila, estandarte para a ponte, flamula"""
    n = 16
    lathe(b, F, 0, 0, [(TR + 0.5, -1.4), (TR + 0.5, 1.9), (TR, 2.6)], STD, n)                   # cantaria escura
    lathe(b, F, 0, 0, [(TR, 2.4), (TR, TH + 0.2)], ST, n)                                        # corpo
    lathe(b, F, 0, 0, [(TR - 0.02, 12.8), (TR + 0.36, 13.0), (TR + 0.36, 13.5), (TR - 0.02, 13.7)], STD, n)  # cordao
    lathe(b, F, 0, 0, [(TR - 0.02, TH - 1.9), (TR + 0.6, TH - 1.2), (TR + 0.6, TH - 0.1), (TR - 0.02, TH - 0.1)],
          STD, n)                                                                                 # misulas
    # telhado conico (beiral de 1,4 alem das misulas) + ponta de ferro + flamula
    lathe(b, F, 0, 0, [(TR + 0.3, TH - 0.2), (TR + 1.5, TH - 0.2), (TR + 1.5, TH + 0.3), (TR + 1.15, TH + 0.75),
                       (0.42, TH + 9.6), (0.0, TH + 10.1)], "WB_Roof_Dark", n)
    cyl(b, F, (0, 0, TH + 9.4), (0, 0, TH + 12.2), 0.14, IR, seg=6)
    b.sphere(F.p(0, 0, TH + 12.2), 0.34, IR, seg=6)
    Ff = F.sub(0, 0, 0, 0)
    poly_wall(b, Ff, [(0.1, TH + 12.0), (2.4, TH + 11.5), (0.1, TH + 10.9)], -0.04, 0.04, "WB_Cloth_Gold")
    # seteiras (2) viradas para a ponte / fora e janelinha para a vila. A torre com s > 0 fica em x local +TXC, logo
    # o lado de FORA dela e o angulo 0 (eixo t); a ponte e o angulo 90 (eixo f)
    for (ang, zc) in ((90.0 - s * 33.75, 10.5), (90.0 - s * 78.75, 18.5)):
        r_face = TR * math.cos(RAD(11.25))
        Fs = Fr(F.p(r_face * math.cos(RAD(ang)), r_face * math.sin(RAD(ang)), 0), (F.t * math.cos(RAD(ang)) + F.f * math.sin(RAD(ang))).xy)
        bb(b, Fs, -0.28, 0.28, -0.6, 0.14, zc - 1.5, zc + 1.5, "WB_Dark")
        for sx in (-1, 1):
            bb(b, Fs, sx * 0.5 - 0.22, sx * 0.5 + 0.22, -0.4, 0.24, zc - 1.85, zc + 1.85, STD)
        bb(b, Fs, -0.72, 0.72, -0.4, 0.24, zc + 1.5, zc + 1.85, STD)
        bb(b, Fs, -0.72, 0.72, -0.4, 0.24, zc - 1.85, zc - 1.5, STD)
    ang = 270.0 + s * 11.25
    r_face = TR * math.cos(RAD(11.25))
    Fw = Fr(F.p(r_face * math.cos(RAD(ang)), r_face * math.sin(RAD(ang)), 0), (F.t * math.cos(RAD(ang)) + F.f * math.sin(RAD(ang))).xy)
    bb(b, Fw, -1.0, 1.0, -0.6, 0.12, 13.0, 15.4, "WB_Dark")
    bb(b, Fw, -0.12, 0.12, -0.3, 0.2, 13.0, 15.4, TB)
    bb(b, Fw, -1.0, 1.0, -0.3, 0.2, 14.1, 14.3, TB)
    bb(b, Fw, -1.4, 1.4, -0.4, 0.3, 15.4, 15.9, STD)
    bb(b, Fw, -1.4, 1.4, -0.4, 0.42, 12.5, 13.0, STD)
    # estandarte virado para a ponte (angulo 90 = +y local = +Z Roblox), com 2 bracos de ferro
    Fb = Fr(F.p(0, TR + 0.5, 0), F.f.xy)
    banner(b, Fb, 0.0, 0.0, 21.5, "WB_Cloth_Red" if s > 0 else "WB_Cloth_Blue", 2.6, 7.4)
    for sx in (-1, 1):
        bb(b, Fb, sx * 1.5 - 0.12, sx * 1.5 + 0.12, -0.6, 0.0, 21.36, 21.64, IR)


# ------------------------------------------------------------------ MURALHA DO PORTAO (arco, portas, tabua, lanternas)
def gate_wall(b, F):
    """bloco entre as torres: x -10..10 (entra nas torres), y -GD..GD. Vao x -8..8 com arco de meio ponto nas duas
    faces (camada FACE) e corredor de teto plano em CEIL atras; muralha ate WTOP com cornija e ameias"""
    for s in (-1, 1):
        bb(b, F, s * HW, s * (HW + 2.0), -GD, GD, 0.0, WTOP, ST)                       # pilares/ombreiras
        bb(b, F, s * HW, s * (HW + 2.0), -GD - 0.3, GD + 0.3, -0.6, 1.3, STD)           # soco escuro
    bb(b, F, -HW, HW, -GD + FACE - 0.05, GD - FACE + 0.05, CEIL, WTOP, ST)              # verga/teto do corredor
    arc = arch_pts(0.0, SPRING, HW, 14)                                                  # de (+8, 7) a (-8, 7)
    face_poly = [(-HW, WTOP), (HW, WTOP), (HW, SPRING)] + arc[1:-1] + [(-HW, SPRING)]
    wall_xz(b, F, face_poly, GD - FACE, GD, ST)
    wall_xz(b, F, face_poly, -GD, -GD + FACE, ST)
    # vigas do teto do corredor (vistas pelo arco)
    for y in (-2.6, 0.0, 2.6):
        bb(b, F, -HW - 0.3, HW + 0.3, y - 0.4, y + 0.4, CEIL - 0.8, CEIL + 0.1, TB)
    # aduelas + fecho + ombreiras salientes nas 2 faces; cornija e parapeito com ameias
    for s in (-1, 1):
        y_face = s * GD
        ya, yb = sorted((y_face - s * 0.05, y_face + s * 0.35))
        arch_ring(b, F, "xz", 0.0, SPRING, HW, HW + 1.4, ya, yb, 13, STD)
        ka, kb = sorted((y_face - s * 0.05, y_face + s * 0.55))
        bb(b, F, -1.1, 1.1, ka, kb, SPRING + HW - 1.0, SPRING + HW + 1.5, STD, bevel=0.06)   # fecho (keystone)
        for sx in (-1, 1):
            bb(b, F, min(sx * HW, sx * (HW + 1.4)), max(sx * HW, sx * (HW + 1.4)), ya, yb, -0.3, SPRING + 0.3, STD)
        ca, cb = sorted((y_face, y_face + s * 0.3))
        bb(b, F, -HW - 2.1, HW + 2.1, ca, cb, WTOP - 0.5, WTOP, STD)                        # cornija
        ma, mb = sorted((y_face - s * 0.05, y_face + s * 0.3))
        for k in range(-5, 6):                                                              # misulas sob a cornija
            bb(b, F, k * 1.8 - 0.35, k * 1.8 + 0.35, ma, mb, WTOP - 1.2, WTOP - 0.5, STD)
        # parapeito do adarve + ameias
        pa, pb = sorted((y_face, y_face - s * 0.8))
        bb(b, F, -HW - 2.0, HW + 2.0, pa, pb, WTOP, WTOP + 1.2, ST)
        for k in range(-2, 3):
            x = k * 3.6
            bb(b, F, x - 0.9, x + 0.9, pa, pb, WTOP + 1.2, WTOP + 2.3, ST)
            ma, mb = sorted((y_face + s * 0.1, y_face - s * 0.9))
            bb(b, F, x - 1.0, x + 1.0, ma, mb, WTOP + 2.3, WTOP + 2.6, STD)
    # tabua de madeira acima do arco, nas 2 faces: "WOLFBERG" para quem chega da ponte (+Z), aviso para a vila (-Z)
    for s, label, size in ((1, "WOLFBERG", 1.5), (-1, "BOA SORTE NAS MINAS", 0.84)):
        Ff = F.sub(0, s * GD, 0, 0 if s > 0 else 180)          # origem na face, +y para fora
        bb(b, Ff, -7.2, 7.2, 0.12, 0.62, 16.75, 19.2, PK, bevel=0.06)
        bb(b, Ff, -7.5, 7.5, 0.05, 0.72, 16.5, 16.85, TB, bevel=0.05)
        bb(b, Ff, -7.5, 7.5, 0.05, 0.72, 19.1, 19.45, TB, bevel=0.05)
        for sx in (-1, 1):
            bb(b, Ff, sx * 7.35 - 0.2, sx * 7.35 + 0.2, 0.05, 0.72, 16.5, 19.45, TB)
            bb(b, Ff, sx * 5.0 - 0.14, sx * 5.0 + 0.14, 0.62, 0.9, 16.6, 19.35, IR)       # cintas de ferro
        text(b, Ff, label, size, TXT, 0.0, 0.66, 17.95, 0.14, bold=True)
        # lanternas de parede dos dois lados do arco
        for sx in (-1, 1):
            idx = (0 if s > 0 else 2) + (0 if sx < 0 else 1)
            lantern_wall(b, Ff, sx * 9.6, 10.6, "L_WB_Lamp_Gate_%d" % idx)


def doors(b, F):
    """portas duplas de tabuas ABERTAS (90 graus para dentro do corredor), encostadas nas paredes internas: folha
    8 x ~14,8 x 0,5 com topo em arco (as duas juntas fecham o arco), travessas, ferragens, dobradicas e argola"""
    y_h = -GD + FACE                                           # dobradica na face da vila (dentro do corredor)
    for sx in (-1, 1):
        x_in = sx * (HW - 0.62)                                # face da folha virada para o corredor
        x_wall = sx * (HW - 0.12)                              # 0,12 de folga da parede
        pts = [(y_h, 0.25), (y_h + 8.0, 0.25), (y_h + 8.0, CROWN - 0.25)]
        for k in range(1, 13):
            u = 8.0 * (1.0 - k / 12.0)
            pts.append((y_h + u, SPRING + math.sqrt(max(0.0, HW * HW - (8.0 - u) ** 2)) - 0.25))
        poly_wall(b, F, pts, min(x_in, x_wall), max(x_in, x_wall), PK)
        for (zc, y_span) in ((2.6, (y_h + 0.3, y_h + 7.7)), (7.2, (y_h + 0.3, y_h + 7.7)), (11.6, (y_h + 1.9, y_h + 7.7))):
            a, c = y_span
            bb(b, F, min(x_in, x_in - sx * 0.18), max(x_in, x_in - sx * 0.18), a, c, zc - 0.28, zc + 0.28, TB)
            bb(b, F, min(x_in - sx * 0.18, x_in - sx * 0.26), max(x_in - sx * 0.18, x_in - sx * 0.26), a + 0.6, c - 2.2,
               zc - 0.14, zc + 0.14, IR)
        for zc in (2.6, 11.6):
            cyl(b, F, (sx * (HW - 0.37), y_h + 0.05, zc - 0.7), (sx * (HW - 0.37), y_h + 0.05, zc + 0.7), 0.3, IR, seg=8)
        b.sphere(F.p(x_in - sx * 0.2, y_h + 7.0, 6.2), 0.3, IR, seg=6)
        fm_lib.col_box("Exit", (0.6, 8.0, 14.8), F.p(sx * (HW - 0.37), y_h + 4.0, 7.4), (0, 0, F.yaw()))


def low_walls(b, F):
    """muralhas baixas (3 x 1,5) saindo das torres ate x = +-30, pilar escuro na ponta, canteiro de arbustos na frente
    (lado da ponte) sobre a grama (Y 6,8 = local -0,2)"""
    r = random.Random(SEED)
    for sx in (-1, 1):
        x0, x1 = sx * TXC, sx * 30.0
        lo, hi = min(x0, x1), max(x0, x1)
        bb(b, F, lo, hi, -0.75, 0.75, -0.9, 3.0, ST)
        bb(b, F, lo, hi, -0.92, 0.92, 3.0, 3.4, STD)
        bb(b, F, x1 - 1.05, x1 + 1.05, -1.05, 1.05, -0.9, 3.9, STD)
        pyramid(b, F, x1, 0.0, 3.9, 4.7, 1.2, STD)
        fm_lib.col_box("Exit", (abs(hi - lo) + 1.0, 2.1, 4.6), F.p((lo + hi) / 2, 0, 1.4), (0, 0, F.yaw()))
        # canteiro: terra com meio-fio escuro, arbustos com flores
        bx0, bx1 = sorted((sx * (TXC + 5.0), sx * 29.4))
        bb(b, F, bx0, bx1, 0.95, 4.1, -0.5, -0.05, "WB_Dirt")
        bb(b, F, bx0 - 0.4, bx1 + 0.4, 4.1, 4.5, -0.5, 0.3, STD, bevel=0.06)
        bb(b, F, bx0 - 0.4, bx0, 0.95, 4.5, -0.5, 0.3, STD, bevel=0.06)
        bb(b, F, bx1, bx1 + 0.4, 0.95, 4.5, -0.5, 0.3, STD, bevel=0.06)
        Fb = F.sub(0, 0, -0.05, 0)
        n = 4
        for k in range(n):
            x = bx0 + 1.6 + (bx1 - bx0 - 3.2) * k / (n - 1) + r.uniform(-0.3, 0.3)
            bush(b, Fb, x, 2.5 + r.uniform(-0.3, 0.3), r.uniform(1.6, 2.1), seed=(sx, k),
                 flowers=["WB_FlowerRed", None, "WB_FlowerYellow", "WB_FlowerPink"][k % 4])
        fm_lib.col_box("Exit", (bx1 - bx0 + 0.8, 3.6, 1.0), F.p((bx0 + bx1) / 2, 2.7, 0.0), (0, 0, F.yaw()))


def gate(coll=COLL):
    b = W.Build("WB_Exit_Gate", coll, seed=SEED)
    F = Fr.rbx(GX, GZ, Y0, 0.0, 1.0)              # +y local = +Z Roblox (para a ponte); +x local = -X Roblox
    for s in (-1, 1):
        Ft = Fr(F.p(s * TXC, 0, 0), F.f.xy)
        tower(b, Ft, s)
        fm_lib.col_box("Exit", (2 * TR + 0.4, 2 * TR + 0.4, TH + 2.0), F.p(s * TXC, 0, TH / 2 - 0.5), (0, 0, F.yaw()))
    gate_wall(b, F)
    doors(b, F)
    low_walls(b, F)
    # laje de ligacao portao -> ponte (x -8..8, z 142..148, cota 7)
    bb(b, F, -HW, HW, 0.0, BZ0 - GZ, -0.7, 0.0, "WB_Cobble")
    fm_lib.col_box("Exit", (2 * HW, BZ0 - GZ, 1.0), F.p(0, (BZ0 - GZ) / 2, -0.5), (0, 0, F.yaw()))
    # colisao: verga sobre o vao (acima de CEIL) + haunches do arco nas faces
    fm_lib.col_box("Exit", (2 * HW + 0.4, 2 * GD + 0.8, WTOP + 2.6 - CEIL), F.p(0, 0, (CEIL + WTOP + 2.6) / 2), (0, 0, F.yaw()))
    for s in (-1, 1):
        for sx in (-1, 1):
            fm_lib.col_box("Exit", (1.6, FACE + 0.4, CROWN - SPRING), F.p(sx * (HW - 0.8), s * (GD - FACE / 2 - 0.1), (SPRING + CROWN) / 2),
                           (0, 0, F.yaw()))
    objs = b.finish()
    fm_lib.marker("LOBBY_GATE_Ilha1", RB(GX, GZ, Y0), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"nota": "portao da ponte da Ilha 1 (Vila da Folha)", "face_x": 0.0, "face_z": 1.0, "yaw_deg": 180.0})
    return objs


# ------------------------------------------------------------------ PONTE DE PEDRA
def pilaret(b, F, x, y, big=False):
    """pilarete do parapeito centrado em (x, y) local; devolve z local do topo (onde o poste pode sentar)"""
    z = zdeck(y)
    h, c = (0.9, 1.1) if big else (0.65, 0.8)
    top = z + (3.4 if big else 2.9)
    bb(b, F, x - h, x + h, y - h, y + h, z - 0.7, top, ST)
    bb(b, F, x - c, x + c, y - c, y + c, top, top + (0.4 if big else 0.3), STD, bevel=0.05)
    return top + (0.4 if big else 0.3)


def bridge(coll=COLL):
    b = W.Build("WB_Exit_Bridge", coll, seed=SEED)
    F = Fr.rbx(0.0, BZ0, Y0, 0.0, 1.0)            # origem (0, 7, 148); +y local = +Z Roblox (ao longo da ponte)
    LEND = BL - 0.1                               # cornija/parapeitos param 0,1 antes da borda da praca da ilha
    deck = [(-BH, 0.0), (BH, 0.0), (BH, FLARE0), (LH, FLARE1), (LH, BL), (-LH, BL), (-LH, FLARE1), (-BH, FLARE0)]
    o = PAR_W + 0.3
    slab = [(-BH - o, 0.0), (BH + o, 0.0), (BH + o, FLARE0), (LH + o, FLARE1), (LH + o, LEND), (-LH - o, LEND),
            (-LH - o, FLARE1), (-BH - o, FLARE0)]
    prism_fn(b, F, deck, zdeck, COB_T, "WB_Cobble")                                            # paralelepipedo
    prism_fn(b, F, slab, lambda y: zdeck(y) - COB_T + 0.1, SLAB_T + 0.1, STD)                    # laje / cornija
    z_mid = lambda y: zdeck(y) - COB_T - SLAB_T / 2.0                                            # meio da laje
    # ---------------------------------------------------------------- parapeitos (3 trechos por lado) + capeamento
    for sx in (-1, 1):
        segs = [[(BH, 0.0), (BH + PAR_W, 0.0), (BH + PAR_W, FLARE0), (BH, FLARE0)],
                [(BH, FLARE0), (BH + PAR_W, FLARE0), (LH + PAR_W, FLARE1), (LH, FLARE1)],
                [(LH, FLARE1), (LH + PAR_W, FLARE1), (LH + PAR_W, LEND), (LH, LEND)]]
        for seg in segs:
            poly = [(sx * x, y) for (x, y) in seg]
            prism_fn(b, F, poly, lambda y: zdeck(y) + PAR_H - 0.25, PAR_H - 0.25 + 0.7, ST)
            cop = [(sx * (x + (-0.1 if abs(x) in (BH, LH) else 0.1)), y) for (x, y) in seg]
            prism_fn(b, F, cop, lambda y: zdeck(y) + PAR_H, 0.3, STD)
        xc = sx * (BH + PAR_W / 2.0)
        xl = sx * (LH + PAR_W / 2.0)
        for y in (0.65, 12.0, 24.0, 36.0, 48.0, FLARE0):
            top = pilaret(b, F, xc, y)
            if not ((y == 12.0 and sx > 0) or (y == 36.0 and sx < 0) or (y == FLARE0 and sx > 0)):
                pyramid(b, F, xc, y, top, top + 0.55, 0.75, STD)
        top = pilaret(b, F, xl, FLARE1)
        pyramid(b, F, xl, FLARE1, top, top + 0.55, 0.75, STD)
        # colisao dos parapeitos (rampas finas sobre os 3 trechos)
        for (x0, y0, x1, y1) in ((xc, 0.0, xc, FLARE0), (xc, FLARE0, xl, FLARE1), (xl, FLARE1, xl, LEND)):
            fm_lib.col_ramp("Exit", F.p(x0, y0, zdeck(y0) + PAR_H), F.p(x1, y1, zdeck(y1) + PAR_H), PAR_W + 0.2, 3.1)
    # postes de lanterna sobre pilaretes a cada 24, alternando lados; pilaretes grandes com lanterna no fim
    k = 0
    for (y, sx, big) in ((12.0, 1, False), (36.0, -1, False), (FLARE0, 1, False), (BL - 1.1, -1, True), (BL - 1.1, 1, True)):
        x = sx * ((LH if big else BH) + PAR_W / 2.0)
        top = pilaret(b, F, x, y, big=big) if big else zdeck(y) + 3.2
        Fp = Fr(F.p(x, y, top), (F.p(0, y, top) - F.p(x, y, top)).xy)      # braco virado para o eixo da ponte
        lantern_post(b, Fp, 0.0, 0.0, "L_WB_Lamp_Bridge_%d" % k, h=7.6 if big else 7.0)
        fm_lib.col_box("Exit", (1.4, 1.4, 8.0), F.p(x, y, top + 4.0), (0, 0, F.yaw()))
        k += 1
    # ---------------------------------------------------------------- infraestrutura: encontros, pilares, arcos
    WX = BH + PAR_W                                                       # 8,8: faces laterais da estrutura
    bb(b, F, -WX, WX, 0.0, ARCHES[0][0], SPRING_B - 0.5, z_mid(ARCHES[0][0]), ST)              # encontro da vila
    ab = [(-WX, ARCHES[-1][1]), (WX, ARCHES[-1][1]), (LH + PAR_W, FLARE1), (LH + PAR_W, LEND), (-LH - PAR_W, LEND),
          (-LH - PAR_W, FLARE1)]
    poly_prism(b, F, ab, SPRING_B - 0.5, z_mid(LEND) - 0.05, ST)                               # encontro da ilha (cais)
    for i in range(len(ARCHES) - 1):
        ya, yb = ARCHES[i][1], ARCHES[i + 1][0]
        bb(b, F, -WX, WX, ya, yb, SPRING_B - 0.5, z_mid(yb), ST)                               # pilar
        yc = (ya + yb) / 2.0
        for sx in (-1, 1):                                                                     # talha-mar
            poly_prism(b, F, [(sx * WX, ya), (sx * WX, yb), (sx * (WX + 2.2), yc)], SPRING_B - 0.5, -3.6, ST)
            poly_prism(b, F, [(sx * (WX - 0.2), ya - 0.25), (sx * (WX - 0.2), yb + 0.25), (sx * (WX + 2.5), yc)],
                       -3.62, -3.2, STD)
    for (ya, yb) in ARCHES:
        yc = (ya + yb) / 2.0
        pts = [(ya, z_mid(ya)), (yb, z_mid(yb)), (yb, SPRING_B)]
        pts += [(yc + ARCH_R * math.cos(RAD(a)), SPRING_B + ARCH_R * math.sin(RAD(a))) for a in
                [180.0 * k / 16 for k in range(1, 16)]]
        pts.append((ya, SPRING_B))
        poly_wall(b, F, pts, -WX, WX, ST)                                                      # tímpano + abobada
        for sx in (-1, 1):
            w0, w1 = sorted((sx * (WX - 0.05), sx * (WX + 0.25)))
            arch_ring(b, F, "yz", yc, SPRING_B, ARCH_R, ARCH_R + 0.6, w0, w1, 13, STD, 30.0, 150.0)
            k0, k1 = sorted((sx * (WX - 0.05), sx * (WX + 0.38)))
            bb(b, F, k0, k1, yc - 0.75, yc + 0.75, SPRING_B + ARCH_R - 1.0, SPRING_B + ARCH_R + 0.25, STD, bevel=0.05)
    # ---------------------------------------------------------------- colisao do tabuleiro (rampas) e marcador
    fm_lib.col_ramp("Exit", F.p(0, 0, 0.0), F.p(0, BL, zdeck(BL)), BWID, 1.5)
    fm_lib.col_ramp("Exit", F.p(0, FLARE0, zdeck(FLARE0)), F.p(0, BL, zdeck(BL)), 2 * LH, 1.5)
    objs = b.finish()
    ix, iy, iz = L.ISLE_LINK
    fm_lib.marker("ISLE_LINK_Area1", RB(ix, iz, iy), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"nota": "fim da ponte = borda da praca de chegada da Area 1 (z 222, piso 6)", "face_x": 0.0,
                   "face_z": 1.0, "yaw_deg": 180.0})
    return objs


def build(coll=COLL):
    """portao + ponte; devolve a lista de objetos criados"""
    return gate(coll) + bridge(coll)
