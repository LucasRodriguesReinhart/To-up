# wb_rank.py - MURAL DOS CAMPEOES (casa do ranking GlobalTop100) do lobby Wolfberg: uma LOGGIA de pedra aberta para
# a praca, a oeste. Muro de fundo de pedra (cantaria escura nas quinas, soco, friso) com os 2 QUADROS do jogo
# emoldurados em madeira entalhada, viga-letreiro "CAMPEOES" e cartelas "FORCA" / "MOEDAS"; palco de pedra com piso
# de paralelepipedo e degrau para a praca; 4 colunas de pedra + 2 pilastras no muro, vigas, caibros e telhado de
# telha escura com oitoes de reboco ocre; estandartes vermelhos/azuis/dourado, escudos de madeira, trofeus de latao,
# lanternas (NightOnly), 2 braseiros de ferro (luz de dia + VFX), canteiros com arbustos.
# CONTRATO (wb_layout): origem RANK_O (-58, -11) na cota Y_RANK = 7,6 olhando +X; quadros 26 x 25 x 1,6 em
# z local 0..1,6 centrados em x local +-13,4 (Roblox z -24,4 / 2,4); podios em z local 9,5. Nada nosso no chao na
# faixa x -56..-42 (o jogador anda diante dos quadros). Esses volumes sao do jogo: aqui so o PREVIEW_Top100 (render).
# Referencial local F: origem no pe do muro (face leste), +x local = Roblox +Z (sul), +y local = Roblox +X (leste,
# praca), z = altura sobre o palco.
import math
import random

import bmesh
import fm_lib
import wb_lib as W
import wb_layout as L
from mathutils import Matrix
from wb_kit import (Fr, bx, bb, beam, cyl, poly_wall, poly_prism, lathe, text, timber_face, roof, lantern, banner, bush,
                    ST, STD, TB, PK, PKL, RF, RFD, PL, PLO, IR, TXT, RAD)
from wb_lib import RB

PREFIX = "WB_Rank_"
COLL = "05_SERVICES"
AREA = "Rank"
SEED = 1958
CAMS = [("CAM_WB_Rank_Praca", (-16.0, 13.0, 2.0), (-58.0, 20.0, -11.0), 24),
        ("CAM_WB_Rank_Frente", (-30.0, 11.0, -11.0), (-58.0, 16.0, -11.0), 22),
        ("CAM_WB_Rank_Frente2", (-28.0, 11.0, -25.0), (-58.0, 17.0, -24.4), 22),
        ("CAM_WB_Rank_Lado", (-44.0, 12.0, 30.0), (-58.0, 18.0, -14.0), 22),
        ("CAM_WB_Rank_Geral", (8.0, 17.0, 16.0), (-56.0, 20.0, -11.0), 24),
        ("CAM_WB_Rank_Coluna", (-34.0, 10.0, -34.0), (-44.0, 14.0, -20.0), 30),
        ("CAM_WB_Rank_Fundo", (-150.0, 46.0, -62.0), (-62.0, 20.0, -11.0), 28)]

Y = L.Y_RANK
OX, OZ = L.RANK_O                      # -58, -11
BR = "WB_Brass"
CR, CB, CG = "WB_Cloth_Red", "WB_Cloth_Blue", "WB_Cloth_Gold"

# ------------------------------------------------------------------ medidas (locais; z = 0 no palco)
HX = 31.0                              # meio comprimento do muro/palco (z -42..20)
WD = 6.0                               # espessura do muro (x -64..-58)
STAGE_Y1 = 17.0                        # borda leste do palco (x -41)
COL_Y = 16.0                           # eixo das colunas (x -42)
COL_X = (-29.0, 0.0, 29.0)             # colunas em z -40, -11, 18: uma por ponta + uma no montante central
COL_HW = 1.4                           # meia largura do fuste (vaos de 29: fuste 2,8 + maos-francesas)
WALL_TOP = 30.5                        # topo da cantaria; friso 30,5..31,3; faixa de reboco ate o telhado
CAP_Z = 29.4                           # base do capitel
PLATE_Z0, PLATE_Z1 = 31.05, 32.5       # frechal sobre as colunas
EAVE = L.RANK_ROOF["eave"] - Y         # 32
RIDGE = L.RANK_ROOF["ridge"] - Y       # 40
ROOF_HALF = 13.0                       # meia largura total do telhado (x -66..-40, centro -53)
ROOF_CY = 5.0                          # centro do telhado em y local (x -53)
SLOPE = (RIDGE - EAVE) / ROOF_HALF     # 8/13
PITCH = math.degrees(math.atan(SLOPE))
ROOF_LX = 62.4                         # oitoes em x local +-31,2 (0,2 alem das pontas do muro)
QX = (-13.4, 13.4)                     # centros dos quadros (x local)
QW, QH = 26.0, 25.0                    # quadro do jogo
FO, FI, FD = 1.1, 0.5, 2.4             # moldura: fora do quadro, sobre o quadro, saliencia do muro
FRAME_TOP = QH + FO                    # 26,1


def u_front(y):
    """cota (local) da face inferior da agua da FRENTE do telhado em y local (y de ROOF_CY ate 18)"""
    return EAVE + (ROOF_CY + ROOF_HALF - y) * SLOPE


def u_back(y):
    """cota da face inferior da agua de TRAS (y de -8 ate ROOF_CY)"""
    return EAVE + (y - (ROOF_CY - ROOF_HALF)) * SLOPE


# ------------------------------------------------------------------ helpers locais
def poly_xz(b, F, pts, y0, y1, m):
    """poligono no plano (x, z) local extrudado de y0 a y1 (frontoes, cartelas)"""
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


def lathe_y(b, F, x, y, z, prof, m, n=16):
    """solido de revolucao em torno do eixo HORIZONTAL +y local (apontando para quem olha) que passa por (x, z):
    prof = [(r, d)] de tras (d = 0) para a frente (escudos, bossas)"""
    bm = bmesh.new()
    rings = []
    for (r, d) in prof:
        rr = max(r, 0.001)
        rings.append([bm.verts.new(F.p(x + rr * math.cos(2 * math.pi * k / n), y + d, z + rr * math.sin(2 * math.pi * k / n)))
                      for k in range(n)])
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def diamond(b, F, x, y, z, s, depth, m):
    """losango entalhado (caixa girada 45 graus no plano da face), centro (x, y, z); y = centro da espessura"""
    R = F.R() @ Matrix.Rotation(RAD(45.0), 3, "Y")
    b.box(F.p(x, y, z), (s, depth, s), m, rot=R)


def rosette(b, F, x, y, z, r=0.5, m=BR):
    """bossa de latao (calota revolvida ao longo da normal da face; y = plano da face). Nunca esfera escalada:
    o scale do Build e em eixos de mundo"""
    lathe_y(b, F, x, y - 0.02, z, [(r, 0.0), (r, 0.14), (r * 0.62, 0.32), (0.0, 0.38)], m, 10)


def col(F, x0, x1, y0, y1, z0, z1):
    """caixa de colisao alinhada ao referencial local (sem giro: x local = -Y Blender, y local = X Blender)"""
    fm_lib.col_box(AREA, (abs(y1 - y0), abs(x1 - x0), abs(z1 - z0)), F.p((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                   (0, 0, 0))


# ------------------------------------------------------------------ PREVIEW dos volumes do jogo (nunca exportado)
def preview(F):
    pb = W.Build("PREVIEW_Top100", "00_REFERENCE")
    for xc in QX:
        bb(pb, F, xc - QW / 2, xc + QW / 2, 0.0, 1.6, 0.0, QH, STD)                       # moldura do jogo
        bb(pb, F, xc - 11.8, xc + 11.8, 1.6, 1.95, 0.6, 24.4, "WB_Dark")                  # painel escuro
        for (dx, h) in ((0.0, 2.4), (-8.0, 1.6), (8.0, 1.0)):                             # podios 6,6 x 5,8
            bb(pb, F, xc + dx - 3.3, xc + dx + 3.3, 9.5 - 2.9, 9.5 + 2.9, 0.0, h, ST)
    return pb.finish()


# ------------------------------------------------------------------ palco
def stage(b, F):
    # plataforma de pedra (cota 6,3..7,5) com tapete de paralelepipedo 0,1 saliente, recuado 0,7 (borda de pedra)
    poly_prism(b, F, [(-HX, -2.0), (HX, -2.0), (HX, STAGE_Y1), (-HX, STAGE_Y1)], -1.3, -0.1, STD)
    bb(b, F, -HX + 0.7, HX - 0.7, -1.3, STAGE_Y1 - 0.7, -0.25, 0.0, "WB_Cobble")
    # degrau para a praca (x -41..-39,5, topo 7,4): esconde o meio-fio da praca (topo 7,37)
    bb(b, F, -HX, HX, STAGE_Y1, STAGE_Y1 + 1.5, -1.2, -0.2, STD)
    col(F, -HX, HX, -2.0, STAGE_Y1, -1.2, 0.0)
    col(F, -HX, HX, STAGE_Y1, STAGE_Y1 + 1.5, -1.2, -0.2)


# ------------------------------------------------------------------ muro de fundo
def wall(b, F):
    # cantaria principal + soco + friso
    bb(b, F, -HX, HX, -WD, 0.0, -1.0, WALL_TOP + 0.1, ST)
    bb(b, F, -HX - 0.4, HX + 0.4, -WD - 0.4, 0.4, -1.0, 1.0, STD)
    bb(b, F, -HX - 0.5, HX + 0.5, -WD - 0.5, 0.5, WALL_TOP, WALL_TOP + 0.8, STD)
    # quinas de cantaria escura (blocos alternados) nos 2 cantos de tras e nas faces de topo dos cantos da frente
    for sx in (-1, 1):
        for i in range(14):
            z0 = 1.3 + i * 2.1
            a, c = (2.4, 1.6) if i % 2 == 0 else (1.6, 2.4)
            # canto de tras (y = -WD)
            x0, x1 = sorted((sx * HX + 0.25 * sx, sx * HX - a * sx))
            bb(b, F, x0, x1, -WD - 0.25, -WD + c, z0, z0 + 2.0, STD)
        # pilastra (meia-coluna) encostada no muro nas pontas da face leste: recebe a viga da coluna da ponta
        x0, x1 = sorted((sx * HX, sx * (HX - 2.8)))
        bb(b, F, x0, x1, 0.0, 1.2, 0.0, CAP_Z, ST)
        bb(b, F, x0 - 0.3, x1 + 0.3, 0.0, 1.5, -0.3, 1.3, STD, bevel=0.08)
        bb(b, F, x0 - 0.3, x1 + 0.3, 0.0, 1.5, CAP_Z, PLATE_Z0 - 0.05, STD, bevel=0.08)
    # contrafortes na face oeste
    for x in (-20.0, 0.0, 20.0):
        bb(b, F, x - 1.0, x + 1.0, -WD - 1.6, -WD, -1.0, 21.0, STD)
        bb(b, F, x - 1.2, x + 1.2, -WD - 1.9, -WD, 21.0, 21.7, STD)
        poly_wall(b, F, [(-WD - 1.9, 21.7), (-WD, 21.7), (-WD, 24.2)], x - 1.2, x + 1.2, STD)
    # faixa de reboco ocre do friso ate a face inferior do telhado (topo inclinado = agua de tras)
    poly_wall(b, F, [(-WD, WALL_TOP + 0.8), (0.0, WALL_TOP + 0.8), (0.0, u_back(0.0) - 0.15), (-WD, u_back(-WD) - 0.15)],
              -HX, HX, PLO)
    # enxaimel da faixa: face leste (sob o telhado da loggia) e face oeste
    bays = [-HX + 0.2 + (2 * HX - 0.4) * k / 10 for k in range(11)]
    timber_face(b, F, -HX + 0.2, HX - 0.2, WALL_TOP + 0.85, u_back(0.0) - 0.55, bays=bays, braces=True, mid=True)
    Fw = F.sub(0.0, -WD, 0.0, 180.0)
    bays_w = [-HX + 0.2 + (2 * HX - 0.4) * k / 6 for k in range(7)]
    timber_face(b, Fw, -HX + 0.2, HX - 0.2, WALL_TOP + 0.85, u_back(-WD) - 0.55, bays=bays_w, braces=True, mid=True)
    col(F, -HX, HX, -WD - 0.5, 1.2, -1.0, u_back(0.0))
    for x in (-20.0, 0.0, 20.0):
        col(F, x - 1.2, x + 1.2, -WD - 1.9, -WD, -1.0, 24.0)


# ------------------------------------------------------------------ molduras, letreiro, cartelas
def frames(b, F):
    yb = FD                                                   # face da moldura
    for xc in QX:
        xl, xr = xc - QW / 2, xc + QW / 2
        # travessas superior e inferior
        bb(b, F, xl - FO, xr + FO, 0.0, FD, QH - FI, FRAME_TOP, TB, bevel=0.08)
        bb(b, F, xl - FO, xr + FO, 0.0, FD, -0.1, 0.55, TB, bevel=0.08)
        # montante externo (o central e um so, abaixo)
        if xc < 0:
            bb(b, F, xl - FO, xl + FI, 0.0, FD, -0.1, FRAME_TOP, TB, bevel=0.08)
            xo = xl - FO + 0.8
        else:
            bb(b, F, xr - FI, xr + FO, 0.0, FD, -0.1, FRAME_TOP, TB, bevel=0.08)
            xo = xr + FO - 0.8
        # friso claro entalhado (madeira clara) no eixo das travessas e dos montantes
        bb(b, F, xl - FO + 0.55, xr + FO - 0.55, yb, yb + 0.2, QH + 0.05, QH + 0.55, PKL)
        bb(b, F, xo - 0.25, xo + 0.25, yb, yb + 0.2, 0.9, QH - 0.2, PKL)
        # bossas de latao nos cantos e losangos no meio das travessas
        for (x, z) in ((xo, QH + 0.3), (xo, 0.25), (xc, QH + 0.3)):
            rosette(b, F, x, yb + 0.2, z, 0.5)
        for x in (xc - 7.0, xc + 7.0):
            diamond(b, F, x, yb + 0.1, QH + 0.3, 0.9, 0.3, PKL)
    # montante central (os dois quadros tem so 0,8 entre si): uma peca so
    bb(b, F, -0.9, 0.9, 0.0, FD, -0.1, FRAME_TOP, TB, bevel=0.08)
    bb(b, F, -0.25, 0.25, yb, yb + 0.2, 0.9, QH - 0.2, PKL)
    rosette(b, F, 0.0, yb + 0.2, QH + 0.3, 0.5)
    rosette(b, F, 0.0, yb + 0.2, 0.25, 0.5)
    # cartelas "FORCA" / "MOEDAS" sobre cada quadro (tabua clara com cantos de madeira escura)
    for xc, label in zip(QX, ("FORCA", "MOEDAS")):
        bb(b, F, xc - 4.6, xc + 4.6, 0.0, 0.7, FRAME_TOP - 0.1, FRAME_TOP + 1.8, PK, bevel=0.06)
        for (z0, z1) in ((FRAME_TOP - 0.15, FRAME_TOP + 0.15), (FRAME_TOP + 1.5, FRAME_TOP + 1.85)):
            bb(b, F, xc - 4.8, xc + 4.8, 0.0, 0.82, z0, z1, TB)
        for sx in (-1, 1):
            bb(b, F, xc + sx * 4.8 - 0.25, xc + sx * 4.8 + 0.25, 0.0, 0.82, FRAME_TOP - 0.15, FRAME_TOP + 1.85, TB)
            rosette(b, F, xc + sx * 4.8, 0.82, FRAME_TOP + 0.85, 0.32)
        text(b, F, label, 0.95, TXT, xc, 0.72, FRAME_TOP + 0.85, 0.12, bold=True)
    # viga-letreiro: de pilastra a pilastra, losangos entalhados e "CAMPEOES" no centro
    bb(b, F, -HX + 2.4, HX - 2.4, 0.0, 1.0, 28.3, 30.1, TB, bevel=0.08)
    for x in (-25.0, -20.0, -15.0, 15.0, 20.0, 25.0):
        diamond(b, F, x, 1.0, 29.2, 1.0, 0.3, PKL)
    for x in (-9.5, 9.5):
        rosette(b, F, x, 1.0, 29.2, 0.45)
    rosette(b, F, 0.0, 1.0, 29.2, 0.6)                       # o titulo vai no letreiro da frente (coluna central)
    for xc in QX:                                             # colisao das molduras (o jogo cuida dos quadros)
        col(F, xc - QW / 2 - FO, xc + QW / 2 + FO, 0.0, FD, 0.0, FRAME_TOP)


# ------------------------------------------------------------------ loggia: colunas, vigas, caibros, telhado
def shield(b, F, x, y, z, band=CR):
    """escudo redondo de madeira (face para +y), aro de ferro, faixa de tecido e bossa de latao"""
    lathe_y(b, F, x, y, z, [(2.3, 0.0), (2.3, 0.3), (1.5, 0.55), (0.6, 0.66), (0.0, 0.68)], PK, 16)
    lathe_y(b, F, x, y, z, [(2.45, 0.05), (2.45, 0.42), (2.05, 0.42), (2.05, 0.05)], IR, 16)
    lathe_y(b, F, x, y, z, [(1.9, 0.45), (1.9, 0.66), (1.3, 0.66), (1.3, 0.45)], band, 16)
    lathe_y(b, F, x, y + 0.55, z, [(0.5, 0.0), (0.5, 0.12), (0.3, 0.42), (0.0, 0.5)], BR, 10)     # bossa central


def trophy(b, F, x, y, z0):
    """taca de latao com 2 asas sobre uma misula de pedra"""
    bb(b, F, x - 0.9, x + 0.9, y - 0.1, y + 2.4, z0 - 0.55, z0, STD, bevel=0.05)
    yc = y + 1.4
    lathe(b, F, x, yc, [(0.85, 0.0), (0.85, 0.2), (0.4, 0.3), (0.28, 1.1), (0.55, 1.45), (1.05, 2.1), (1.15, 2.9),
                        (1.05, 2.95), (0.9, 2.2), (0.55, 1.6), (0.0, 1.55)], BR, 12, z0=z0)
    for sx in (-1, 1):
        pts = [(x + sx * 1.05, yc, z0 + 2.1), (x + sx * 1.65, yc, z0 + 2.45), (x + sx * 1.7, yc, z0 + 1.7),
               (x + sx * 1.0, yc, z0 + 1.35)]
        for a, c in zip(pts[:-1], pts[1:]):
            b.cyl(F.p(*a), F.p(*c), 0.1, BR, seg=6)
        for p in pts[1:-1]:
            b.sphere(F.p(*p), 0.1, BR, seg=5)


def loggia(b, F):
    i_l = 0
    for k, x in enumerate(COL_X):
        y = COL_Y
        bb(b, F, x - 1.7, x + 1.7, y - 1.7, y + 1.7, -0.3, 1.3, STD, bevel=0.1)                    # base
        bb(b, F, x - COL_HW, x + COL_HW, y - COL_HW, y + COL_HW, 1.2, CAP_Z + 0.1, ST)              # fuste
        bb(b, F, x - 1.65, x + 1.65, y - 1.65, y + 1.65, CAP_Z, PLATE_Z0 - 0.05, STD, bevel=0.1)    # capitel
        bb(b, F, x - 0.7, x + 0.7, -1.0, y + 0.6, PLATE_Z0, PLATE_Z1 - 0.1, TB)                     # tirante ate o muro
        beam(b, F, (x, y - COL_HW - 0.2, CAP_Z - 3.4), (x, y - 4.2, PLATE_Z0 + 0.2), 0.6, 0.6, TB)  # mao-francesa (muro)
        sides = (-1, 1) if k == 1 else ((1,) if k == 0 else (-1,))
        for s in sides:                                                                           # maos-francesas no frechal
            beam(b, F, (x + s * (COL_HW + 0.1), y, CAP_Z - 3.0), (x + s * 4.8, y, PLATE_Z0 + 0.3), 0.6, 0.6, TB)
        col(F, x - 1.7, x + 1.7, y - 1.7, y + 1.7, -0.3, PLATE_Z1)
        # face da praca: estandarte, escudo, trofeu (pontas); lanternas nas faces laterais, para dentro dos vaos
        ye = y + COL_HW
        color = CG if k == 1 else CB
        banner(b, F, x, ye + 0.3, 27.6, color, 2.4, 7.0, pole=False, emblem=True)
        for sx in (-1, 1):
            bb(b, F, x + sx * 1.4 - 0.15, x + sx * 1.4 + 0.15, ye - 0.2, ye + 0.5, 27.3, 27.9, IR)
        shield(b, F, x, ye - 0.2, 15.0, CR if k == 1 else CR)
        for s in sides:
            xa, xb = sorted((x + s * (COL_HW - 0.1), x + s * (COL_HW + 1.7)))
            bb(b, F, xa, xb, y - 0.15, y + 0.15, 10.3, 10.6, IR)
            beam(b, F, (x + s * COL_HW, y, 9.0), (x + s * (COL_HW + 1.35), y, 10.3), 0.14, 0.14, IR)
            lantern(b, F, x + s * (COL_HW + 1.3), y, 10.3, "L_WB_Lamp_Rank_%d" % i_l)
            i_l += 1
        if k != 1:
            trophy(b, F, x, ye, 5.1)
        else:
            # letreiro "CAMPEOES" na frente da loggia: tabua clara com bordas escuras presa a coluna e ao frechal
            bb(b, F, -7.2, 7.2, ye, ye + 0.6, 28.9, 31.2, PK, bevel=0.06)
            for (z0, z1) in ((28.85, 29.15), (30.95, 31.25)):
                bb(b, F, -7.4, 7.4, ye, ye + 0.72, z0, z1, TB)
            for sx in (-1, 1):
                bb(b, F, sx * 7.4 - 0.25, sx * 7.4 + 0.25, ye, ye + 0.72, 28.85, 31.25, TB)
                bb(b, F, sx * 6.4 - 0.35, sx * 6.4 + 0.35, y + 0.8, ye + 0.2, 30.4, 31.4, TB)       # fixacao ao frechal
                rosette(b, F, sx * 7.4, ye + 0.72, 30.05, 0.34)
            text(b, F, "CAMPEOES", 1.45, TXT, 0.0, ye + 0.62, 30.05, 0.16, bold=True)
    # frechal sobre as colunas e vigas de ponta sob os oitoes
    bb(b, F, -HX + 1.4, HX - 1.4, COL_Y - 0.9, COL_Y + 0.9, PLATE_Z0, PLATE_Z1, TB)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (ROOF_LX / 2 - 0.9), sx * (ROOF_LX / 2 + 0.3)))
        bb(b, F, x0, x1, -WD - 0.5, COL_Y + 1.4, 30.6, EAVE, TB)
    # caibros da frente (frechal -> cumeeira) e de tras (faixa do muro -> cumeeira); viga de cumeeira
    n = 17
    for k in range(n):
        x = -29.0 + 58.0 * k / (n - 1)
        beam(b, F, (x, 17.7, u_front(17.7) - 0.45), (x, ROOF_CY, RIDGE - 0.45), 0.45, 0.6, TB)
        beam(b, F, (x, 0.3, u_back(0.3) - 0.45), (x, ROOF_CY, RIDGE - 0.45), 0.45, 0.6, TB)
    bb(b, F, -HX, HX, ROOF_CY - 0.5, ROOF_CY + 0.5, RIDGE - 1.4, RIDGE - 0.4, TB)
    # telhado: cumeeira ao longo de x local (Roblox Z); oitoes de reboco ocre com vigas nas pontas N/S
    Fr_ = F.sub(0.0, ROOF_CY, 0.0, 0.0)
    roof(b, Fr_, ROOF_LX, 2 * ROOF_HALF - 4.0, EAVE, PITCH, over=2.0, thick=0.7, m=RFD, mr=RFD, gable=True, pl=PLO,
         gable_timber=True, fascia=True, dormers=0, seed=3)
    for sx in (-1, 1):                                        # remates de latao nas pontas da cumeeira
        lathe(b, F, sx * (ROOF_LX / 2 + 1.4), ROOF_CY, [(0.5, 0.0), (0.5, 0.3), (0.2, 0.5), (0.2, 1.8), (0.55, 2.1),
                                                        (0.0, 3.0)], BR, 8, z0=RIDGE + 0.5)
    # pendoes nos vaos, pendurados no frechal (acima do topo dos quadros: nao tapam o ranking)
    for x, color in ((-20.0, CR), (-9.0, CB), (9.0, CB), (20.0, CR)):
        banner(b, F, x, COL_Y, 31.1, color, 3.0, 6.5, pole=False, emblem=True)
    # estandartes grandes nas faces de topo do muro (norte / sul)
    for sx, turn in ((-1, 90.0), (1, -90.0)):
        Fe = F.sub(sx * HX, -WD / 2, 0.0, turn)
        banner(b, Fe, 0.0, 0.6, 28.0, CR, 3.2, 9.0, pole=False, emblem=True)
        for s2 in (-1, 1):
            bb(b, Fe, s2 * 1.9 - 0.15, s2 * 1.9 + 0.15, -0.3, 0.8, 27.7, 28.3, IR)
        shield(b, Fe, 0.0, -0.2, 17.5, CB)


# ------------------------------------------------------------------ braseiros, canteiros
def brazier(b, F, x, y, tag):
    """plinto de pedra rente ao palco, tripe de ferro, bacia na altura da cintura, brasa e chamas; luz de dia + VFX"""
    bb(b, F, x - 1.6, x + 1.6, y - 1.6, y + 1.6, -1.1, 0.0, STD, bevel=0.1)
    bb(b, F, x - 1.15, x + 1.15, y - 1.15, y + 1.15, 0.0, 0.3, STD)
    for k in range(3):
        a = math.pi / 2 + 2 * math.pi * k / 3
        b.cyl(F.p(x + 1.15 * math.cos(a), y + 1.15 * math.sin(a), 0.3), F.p(x + 0.75 * math.cos(a), y + 0.75 * math.sin(a), 1.7),
              0.17, IR, seg=6)
    cyl(b, F, (x, y, 1.45), (x, y, 1.65), 0.95, IR, seg=10)
    lathe(b, F, x, y, [(0.7, 0.0), (1.7, 0.5), (2.1, 1.1), (2.2, 1.5), (1.95, 1.5), (1.8, 1.15), (1.4, 0.65), (0.0, 0.45)],
          IR, 14, z0=1.5)
    cyl(b, F, (x, y, 1.9), (x, y, 2.3), 1.3, "WB_Ember", seg=10)
    lathe(b, F, x, y, [(1.25, 0.0), (1.05, 0.8), (0.55, 1.7), (0.0, 2.6)], "WB_Fire", 8, z0=2.2)
    lathe(b, F, x + 0.6, y - 0.4, [(0.6, 0.0), (0.45, 0.6), (0.0, 1.3)], "WB_Fire", 6, z0=2.3)
    lathe(b, F, x - 0.55, y + 0.5, [(0.55, 0.0), (0.4, 0.55), (0.0, 1.15)], "WB_Fire", 6, z0=2.3)
    fm_lib.light("L_WB_Brazier_" + tag, "POINT", F.p(x, y, 3.3), 900.0, (1.0, 0.5, 0.2), 0.8)
    fm_lib.marker("VFX_Brazier_Fire_" + tag, F.p(x, y, 2.3), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "fire", "rate": 8, "size": 2.0})
    col(F, x - 1.6, x + 1.6, y - 1.6, y + 1.6, -1.1, 0.0)
    col(F, x - 2.2, x + 2.2, y - 2.2, y + 2.2, 0.0, 3.2)


def planters(b, F, r):
    Fg = F.sub(0.0, 0.0, L.Y_GRASS - Y, 0.0)                 # referencial na cota da grama (6,8)
    for sx in (-1, 1):
        x0, x1 = sorted((sx * (HX + 0.4), sx * (HX + 3.2)))
        bb(b, Fg, x0, x1, -WD - 0.3, 0.3, -0.3, 1.2, STD, bevel=0.08)
        bb(b, Fg, x0 + 0.4, x1 - 0.4, -WD + 0.1, -0.1, 0.9, 1.0, "WB_Dirt")
        for i, (dx, dy) in enumerate(((0.9, -4.3), (2.0, -1.6), (1.0, -0.6))):
            bush(b, Fg, x0 + dx if sx < 0 else x1 - dx, dy, 1.6, seed=(sx, i),
                 flowers=("WB_FlowerRed", "WB_FlowerYellow", "WB_FlowerPink")[i])
        col(Fg, x0, x1, -WD - 0.3, 0.3, -0.3, 1.2)
    # arbustos no pe da face oeste (fora do palco, sob o beiral de tras)
    for k in range(8):
        x = -27.0 + 54.0 * k / 7 + r.uniform(-0.8, 0.8)
        bush(b, Fg, x, -WD - 2.3 - r.uniform(0.0, 0.6), r.uniform(1.8, 2.4), seed=k,
             flowers=r.choice([None, "WB_FlowerRed", "WB_FlowerPink", "WB_FlowerWhite"]))


# ------------------------------------------------------------------ montagem
def build():
    r = random.Random(SEED)
    F = Fr.rbx(OX, OZ, Y, 1.0, 0.0)              # pe do muro, olhando a praca (+X); x local = Roblox +Z
    objs = preview(F)
    b = W.Build(PREFIX + "Hall", COLL, seed=SEED)
    stage(b, F)
    wall(b, F)
    frames(b, F)
    loggia(b, F)
    brazier(b, F, -(HX + 2.0), COL_Y - 0.4, "N")
    brazier(b, F, HX + 2.0, COL_Y - 0.4, "S")
    planters(b, F, r)
    objs += b.finish()
    fm_lib.marker("TOP100_Origin", RB(OX, OZ, Y), (0, 0, 0), 2.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"alvo": "LOBBY_FORJA.GlobalTop100 (OriginCF)",
                   "nota": "quadros em z 0 e podios em z 9,5 do referencial local", "face_x": 1.0, "face_z": 0.0,
                   "yaw_deg": -90.0})
    tris = sum(len(p.vertices) - 2 for o in objs if o.name.startswith(PREFIX) for p in o.data.polygons)
    print("MURAL DOS CAMPEOES: %d objetos, %d tris (%s)" % (len(objs), tris,
          ", ".join("%s %d" % (o.name.split("__")[-1], sum(len(p.vertices) - 2 for p in o.data.polygons))
                    for o in objs if o.name.startswith(PREFIX))))
    return objs
