# sg_terrain - ZONA TERRAIN da Ilha 3 (Shadow Garden), PLANTA v4 (plano mestre 2026-09-30, onda 1f).
# build() substitui sg_blockout.terrain. Prefixo SG_Ter_, colecao 02_TERRAIN. Sem luzes.
# A ilha nova tem 2,4x a area da v3 (rim x -190..190, y -336..390). O acabamento APROVADO do overhaul 13 (commit
# 06d2527) volta inteiro, so que amarrado a planta v4:
#   1. TOPO dos patamares na cota (P1/entrada/invocacao em calcamento; P2, becos e terraco norte do P3 e o ombro em
#      GRAMA de 2 tons em manchas grandes e suaves; o patio do castelo em calcamento). O topo e montado por VARREDURA
#      (trapezios exatos) sobre a planta: sob as AREAS DE PISO DO LAYOUT (ruas, praca, casas, alquimia, terraco do mirante,
#      salao e presbiterio do castelo) o topo desce 0,3 com espelho vertical na borda (z-fight F5: o piso do outro
#      modulo nunca fica coplanar com o meu); o poco da escada caracol fica VAZADO.
#   2. ARRIMO P1->P2 (y -150, altura do jogador): alvenaria em fiadas alternadas, mesa de misulas com arquinhos por
#      vao, contrafortes em talude, arremate e parapeito; na face sob a MURALHA (P2->P3, y -23) NADA de alvenaria nem
#      contraforte (F3: a muralha do castelo, 1a, faz a base) e o corpo do patamar recua 0,4 atras da face dela.
#   3. BORDAS para o terreno bravo: faixa de alvenaria de fundo + base de basalto em MACICOS + arremate + PARAPEITO em
#      cantaria (plinto, lajes em relevo, capa em pecas, pedra de canto nas emendas, pilarete so nas pontas livres).
#   4. PENHASCO: coroa em blocos canelados com 7 PROMONTORIOS e 2 ESTRATOS continuos (cota fixa na ilha inteira).
#   5. QUILHA (subsolo): casca escalonada e canelada que desce do contorno ate uma secao de 136 x 336 em z -80 (a fila das
#      salas da masmorra e o Salao Sombrio ficam DENTRO dela, sem furo para fora) e fecha em ponta em -108; 7 quilhas
#      de promontorio com as colunas pendentes so nelas. E uma CASCA (sem miolo): o que se ve por dentro e do 1c/1d.
#   6. Tier C no fundo (casca, coroa, quilhas), Tier B so onde o jogador anda (arrimo, bordas, parapeitos, mirante).
#   7. AGUA: a agua e do Roblox; aqui a rocha das quedas (bancada do labio na cota -0,1 que o sg_water procura, bloco da
#      coroa recuado atras da cortina, parapeito aberto) e os DEGRAUS de basalto (fall_steps) na cota do estrato de cima
#      (20 = FX_Fall_<n>_Step). A bica/calha e os marcadores FX_Fall_* sao do sg_water.
#   8. JARDIM-MIRANTE (P3 leste): a rocha fica reduzida a falesia da borda, como moldura (plano 2.2): o promontorio do
#      mirante fica baixo no eixo da vista e 2 macicos de basalto em degrau sobem a norte e a sul ATE logo abaixo do
#      parapeito (nao tapam a vista).
#   9. cristais em 2 aglomerados na borda + as pontas pendentes da ilhota da invocacao.
# REGRAS DO SUBSOLO: nenhuma face em sg_layout.CAVE_KEEP_OUT nem em DUN_KEEP_OUT (verify_subsoil confere a casca).
# Kit de cantaria: copia local de sg_castle.ledge/block/strip e do pilarete do sg_entry (os dois modulos estao sendo
# refeitos na onda 1; o terreno nao depende deles).
import math, random, zlib
import bmesh
import bpy
from mathutils import Vector, Matrix, Euler
import sg_lib as SL
from sg_lib import MB, col_box, octo_col, ccw
import fm_lib
import fm_parts as FP
import sg_layout as L
import sg_col

P1, P2, P3, SUM, DECK = L.P1, L.P2, L.P3, L.SUM, L.DECK
SH = P1 - 2.0                       # 34,2 ombro (terreno bravo)
NECK_LOW = DECK - 2.0               # 26,2 espinha de rocha ao lado do patio baixo
CUT_Y = L.ENTRY_HIGH[1]             # -294: sul disso e o pescoco da entrada
STAIR_Y0 = L.ENTRY_STAIR[1]         # -312: pe da escadaria da entrada
NECK_STAIR_X = 10.55                # canal da escadaria LIVRE em |x| <= 10,4 (muretas do sg_entry): o terreno nasce
#                                    0,15 fora da face externa delas (nada coplanar)
PATIO_LOW = (-14.6, -336.0, 14.6, L.ENTRY_LOW[3])   # patio baixo ABERTO no DECK (pedido do 1g): topo na cota, nada acima
UNDER_BRIDGE = (-10.0, -340.0, 10.0, L.ENTRY_LOW[1])  # sob o fim do tabuleiro da ponte (sg_entry, corpo +-10,2): sem topo
BODY_BOT = SH - 1.2                 # base dos corpos dos patamares (a casca e oca)
RECESS = 0.45                       # F5: topo sob os pisos dos outros modulos (>= 0,3; fora das cotas 0,3/0,25
#                                    que os modulos usam nos proprios leitos)
KX0, KY0, KZ0, KX1, KY1, KZ1 = L.DUN_KEEP_OUT
CX0, CY0, CZ0, CX1, CY1, CZ1 = L.CAVE_KEEP_OUT

ROCK, DARK, TOP, GRASS = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top", "Grass_SG"
GRASS2 = "Grass_SGLight"            # 2o tom do chao do gramado (manchas grandes)
BLOCK, TRIM, PAVE = "Stone_SG_Block", "Stone_SG_Trim", "Stone_Paving_SG"
CAPL = "Stone_SG_TrimLow"           # remate perto do jogador (14.01)
fm_lib.MATS.setdefault(CAPL, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
PAR_M = "Stone_SG_Castle_B"         # corpo do parapeito (a mesma dupla da entrada)
REL_M = "Stone_SG_Block_B"          # relevo (lajes, plinto)
COURSES13 = (2.2, 1.4)              # fiadas alternadas do arrimo
LEN_TALL = (4.4, 3.6, 5.0, 3.9)     # comprimentos DIRIGIDOS dos blocos (fiada alta / baixa), ciclo fixo
LEN_LOW = (2.9, 3.4, 2.5, 3.1)
BED = "Stone_SG_Floor"              # leito escuro das juntas (sob as lajes do terreno)
GRAVEL = "Dirt_SGGravel"            # faixa de cascalho (bordadura) ao pe de parapeitos e muros
PAVE_B = "Stone_Paving_SG_B"        # 2o tom DIRIGIDO das lajes (fiadas alternadas)
BED_D = 0.32                        # leito das lajes: 0,32 abaixo da cota (laje de 0,30 + 0,02 sem face de contato)
GRV_D = 0.12                        # cascalho 0,12 abaixo da cota (o meio-fio mostra 0,12 de face)
GW_E, CW = 1.3, 0.5                 # bordadura ao pe do parapeito (largura) e largura do meio-fio
GW_F = 3.6                          # bordadura ao pe dos muros de arrimo (cobre o soco dos contrafortes, 2,8)
APRON = 2.0                         # rodape de chao: calcada de lajes em volta dos predios (16.08) + meio-fio
ZS_A, ZS_B = 20.0, 6.0              # os 2 estratos continuos da coroa (cota fixa na ilha inteira)
# promontorios da coroa (x, y, meia-largura): O, NO, N, NE, L (jardim-mirante), SE, SO
PROMS = [(-178.0, 40.0, 22.0), (-160.0, 296.0, 18.0), (16.0, 392.0, 22.0), (132.0, 334.0, 18.0),
         (160.0, 172.0, 26.0), (120.0, -287.0, 18.0), (-184.0, -140.0, 18.0)]
MIRANTE_PROM = 4                    # indice do promontorio do jardim-mirante

# ------------------------------------------------------------------ cameras de revisao da zona
_BR = L.BRIDGE_PATH[9]
_GX, _GY = L.exit_point(L.EXIT_BRIDGE_LEN - 20.0)
_GV = (-L.exit_dir()[1], L.exit_dir()[0])
CAMS = {
    "CAM_SGTer_Overview": ((430.0, -430.0, 250.0), (0.0, 40.0, 10.0), 24),
    "CAM_SGTer_FromBridge": ((_BR[0], _BR[1], DECK + 5.2), (0.0, -230.0, 52.0), 22),
    "CAM_SGTer_FromGate": ((_GX + _GV[0] * 16.0, _GY + _GV[1] * 16.0, P3 + 9.0), (-60.0, 270.0, 18.0), 22),
    "CAM_SGTer_Keel": ((-380.0, 40.0, -98.0), (0.0, 140.0, -40.0), 24),
    "CAM_SGTer_KeelSouth": ((170.0, -480.0, -98.0), (0.0, 60.0, -30.0), 24),
    "CAM_SGTer_PH_Arrimo": ((-70.0, -170.0, P1 + 5.2), (-24.0, -150.0, P1 + 6.0), 22),
    "CAM_SGTer_PH_Parapet": ((-140.0, 262.0, P3 + 5.2), (-156.0, 318.0, P3 + 1.4), 22),
    "CAM_SGTer_PH_Mirante": ((110.0, 150.0, P3 + 5.2), (172.0, 180.0, P3 + 1.0), 22),
    "CAM_SGTer_Mirante": ((262.0, 136.0, 74.0), (150.0, 172.0, 36.0), 24),
    "CAM_SGTer_Fall": ((-252.0, -8.0, 46.0), (-186.0, -60.0, 20.0), 24),
    "CAM_SGTer_PH_P1Edge": ((62.0, -275.0, P1 + 5.2), (140.0, -276.0, P1 + 0.5), 22),
    "CAM_SGTer_PH_FallW": ((-150.0, -44.0, P2 + 5.2), (-186.0, -62.0, P2 - 1.0), 22),
    "CAM_SGTer_PH_North": ((-10.0, 352.0, P3 + 5.2), (-66.0, 382.0, P3 + 0.5), 22),
    "CAM_SGTer_GrassP2": ((-30.0, -215.0, 150.0), (-20.0, -80.0, 44.0), 24),
    "CAM_SGTer_GrassP3": ((-270.0, 150.0, 150.0), (-128.0, 200.0, 52.0), 24),
    # FINESSE 3: cameras da AUDITORIA 3 citadas nos itens do terreno (copia de sg_scene.a3_cams: o studio nao as cria)
    "CAM_A3_01_Spawn_Volta": ((0.0, -270.0, P1 + 5.5), (0.0, -340.0, DECK + 2.0), 20),
    "CAM_A3_01_PatioBaixo": ((8.0, -331.0, DECK + 5.5), (0.0, -296.0, P1 + 10.0), 20),
    "CAM_A3_02_Praca_Chegada": ((0.0, -262.0, P1 + 5.5), (0.0, -222.0, P1 + 6.0), 20),
    "CAM_A3_02_Praca_Alta": ((44.0, -284.0, P1 + 42.0), (0.0, -222.0, P1), 22),
    "CAM_A3_03_EscP1P2_Topo": ((-4.0, -145.0, P2 + 5.5), (0.0, -200.0, P1 + 4.0), 20),
    "CAM_A3_03_Arrimo_Frente": ((-30.0, -200.0, P1 + 5.5), (-40.0, -148.0, P1 + 6.0), 20),
    "CAM_A3_03_Arrimo_E": ((62.0, -162.0, P1 + 5.5), (20.0, -149.0, P1 + 5.0), 20),
    "CAM_A3_06_Fachada_Base": ((40.0, 50.0, P3 + 5.5), (62.0, 62.0, P3 + 9.0), 20),
    "CAM_A3_06_Flanco_E": ((140.0, 116.0, P3 + 5.5), (104.0, 200.0, P3 + 30.0), 18),
    "CAM_A3_13_Mirante": ((133.0, 142.0, P3 + 5.5), (136.0, 176.0, P3 + 3.5), 20),
    "CAM_A3_14_Leste": ((820.0, 20.0, 220.0), (0.0, 20.0, 80.0), 24),
    "CAM_A3_14_Oeste": ((-820.0, 20.0, 220.0), (0.0, 20.0, 80.0), 24),
    "CAM_A3_14_Alto_34": ((560.0, -540.0, 520.0), (0.0, 0.0, 40.0), 24),
    "CAM_A3_01_Ponte_Reta": (None, None, 20),          # preenchida abaixo (referencial da ponte)
    "CAM_A3_01_Ponte_Encontro": (None, None, 20),
    "CAM_A3_14_Ilha2_Perto": (None, None, 22),
}
# as 2 cameras da ponte: mesma conta do sg_scene (_bridge_at / _bcam) sem importar o sg_scene no build


def _bridge_at(s, v=0.0):
    pts = L.BRIDGE_PATH
    acc = 0.0
    n = len(pts)
    for i in range(n - 1):
        a, b = pts[i], pts[i + 1]
        ln = math.hypot(b[0] - a[0], b[1] - a[1]) or 1e-9
        if acc + ln >= s or i == n - 2:
            t = max(0.0, min(1.0, (s - acc) / ln))
            tx, ty = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            return (a[0] + (b[0] - a[0]) * t - ty * v, a[1] + (b[1] - a[1]) * t + tx * v)
        acc += ln
    return pts[-1]


_b0, _b1 = L.BRIDGE_PATH[0], L.BRIDGE_PATH[1]
_bl = math.hypot(_b1[0] - _b0[0], _b1[1] - _b0[1]) or 1.0
_bu = ((_b1[0] - _b0[0]) / _bl, (_b1[1] - _b0[1]) / _bl)
CAMS["CAM_A3_14_Ilha2_Perto"] = ((_b0[0] - _bu[0] * 20.0, _b0[1] - _bu[1] * 20.0, DECK + 5.5), (0.0, -60.0, 110.0), 22)
_pa, _pb = _bridge_at(140.0, 0.0), _bridge_at(L.BRIDGE_LEN, 0.0)
CAMS["CAM_A3_01_Ponte_Reta"] = ((_pa[0], _pa[1], DECK + 5.5), (_pb[0], _pb[1], DECK + 22.0), 20)
_pa, _pb = _bridge_at(196.0, -42.0), _bridge_at(L.BRIDGE_LEN - 4.0, 0.0)
CAMS["CAM_A3_01_Ponte_Encontro"] = ((_pa[0], _pa[1], DECK - 2.0), (_pb[0], _pb[1], DECK - 10.0), 20)

# rotas extras: o pe do arrimo P1->P2 continua andavel com os contrafortes (colisao propria)
EXTRA_ROUTES = {
    "P1_pe_do_arrimo_O": ([(-150.0, -156.0), (-14.0, -156.0)], P1),
    "P1_pe_do_arrimo_L": ([(14.0, -156.0), (160.0, -156.0)], P1),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ cotas do terreno bravo (para o vestir)
def neck_z(y):
    if y <= STAIR_Y0:
        return NECK_LOW
    if y >= CUT_Y:
        return SH
    return NECK_LOW + (SH - NECK_LOW) * (y - STAIR_Y0) / (CUT_Y - STAIR_Y0)


def wild_z(x, y):
    """cota do chao do terreno bravo (fora dos patamares): 34,2; no pescoco da entrada, a espinha baixa"""
    return neck_z(y) if y < CUT_Y else SH


def ground_z(x, y):
    z = L.zone_of(x, y)
    return z if z is not None else wild_z(x, y)


# ------------------------------------------------------------------ kit de cantaria (copia do sg_castle / sg_entry)
def _P(W, u, t, z):
    (ox, oy), (ux, uy), (nx, ny) = W
    return (ox + ux * u + nx * t, oy + uy * u + ny * t, z)


def _dedupe(poly, eps=1e-4):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > eps or abs(p[1] - out[-1][1]) > eps:
            out.append(p)
    while len(out) > 2 and abs(out[0][0] - out[-1][0]) < eps and abs(out[0][1] - out[-1][1]) < eps:
        out.pop()
    return out


def _faces_ok(mb, fs):
    bmesh.ops.recalc_face_normals(mb.bm, faces=[f for f in fs if f is not None])


def ledge(mb, W, u0, u1, prof, m):
    """perfil [(t, z)] extrudado ao longo de u de u0 a u1 (referencial de parede W = (origem, u, normal para fora))"""
    bm = mb.bm
    prof = _dedupe(prof)
    a = [bm.verts.new(_P(W, u0, t, z)) for t, z in prof]
    b = [bm.verts.new(_P(W, u1, t, z)) for t, z in prof]
    n = len(prof)
    fs = [bm.faces.new(a), bm.faces.new(list(reversed(b)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    _faces_ok(mb, fs)
    mb._post(a + b, m, None, 0, 1)


def block(mb, W, u0, u1, z0, z1, t0, t1, ch, m):
    """bloco de cantaria: face de tras em t0, face da frente recuada 'ch' nas 4 arestas em t1"""
    bm = mb.bm
    ch = min(ch, (u1 - u0) * 0.3, (z1 - z0) * 0.3)
    back = [bm.verts.new(_P(W, u, t0, z)) for u, z in ((u0, z0), (u1, z0), (u1, z1), (u0, z1))]
    fr = [bm.verts.new(_P(W, u, t1, z)) for u, z in ((u0 + ch, z0 + ch), (u1 - ch, z0 + ch), (u1 - ch, z1 - ch),
                                                     (u0 + ch, z1 - ch))]
    fs = [bm.faces.new(back), bm.faces.new(list(reversed(fr)))]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((back[i], fr[i], fr[j], back[j])))
    _faces_ok(mb, fs)
    mb._post(back + fr, m, None, 0, 1)


def strip(mb, W, lo, hi, t0, t1, m):
    """casca fechada entre a curva de baixo 'lo' e a de cima 'hi' ([(u, z)] par a par), de t0 a t1 (arquinhos)"""
    bm = mb.bm
    L0 = [(bm.verts.new(_P(W, u, t0, z)), bm.verts.new(_P(W, u, t1, z))) for u, z in lo]
    H0 = [(bm.verts.new(_P(W, u, t0, z)), bm.verts.new(_P(W, u, t1, z))) for u, z in hi]
    fs = []
    for i in range(len(lo) - 1):
        fs.append(bm.faces.new((L0[i][0], L0[i + 1][0], H0[i + 1][0], H0[i][0])))
        fs.append(bm.faces.new((L0[i][1], H0[i][1], H0[i + 1][1], L0[i + 1][1])))
        fs.append(bm.faces.new((L0[i][0], L0[i][1], L0[i + 1][1], L0[i + 1][0])))
        fs.append(bm.faces.new((H0[i][0], H0[i + 1][0], H0[i + 1][1], H0[i][1])))
    for k in (0, -1):
        fs.append(bm.faces.new((L0[k][0], H0[k][0], H0[k][1], L0[k][1])))
    _faces_ok(mb, fs)
    mb._post([v for p in L0 + H0 for v in p], m, None, 0, 1)


def chamfer_sq(x, y, hs, c):
    return [(x - hs + c, y - hs), (x + hs - c, y - hs), (x + hs, y - hs + c), (x + hs, y + hs - c),
            (x + hs - c, y + hs), (x - hs + c, y + hs), (x - hs, y + hs - c), (x - hs, y - hs + c)]


def post(mb, x, y, z, size=1.5, h=2.3):
    """pilarete do kit da entrada: plinto + toro, fuste de quinas chanfradas, capitel em 2 degraus e remate (bola com
    colar, torno de 6)"""
    sp = size + 0.34
    mb.box((sp, sp, 0.55), (x, y, z + 0.275), (0, 0, 0), REL_M, 0.08)
    FP.frustum(mb, (x, y, z + 0.55), sp, sp, size + 0.04, size + 0.04, 0.16, REL_M)
    mb.prism(chamfer_sq(x, y, size / 2, 0.16), z + 0.71, z + h - 0.02, PAR_M)
    mb.box((size + 0.12, size + 0.12, 0.16), (x, y, z + h + 0.06), (0, 0, 0), CAPL, 0.04)
    mb.box((size + 0.38, size + 0.38, 0.21), (x, y, z + h + 0.245), (0, 0, 0), CAPL, 0.06)
    zt = z + h + 0.35
    mb.cyl(0.36, 0.12, (x, y, zt + 0.06), m=CAPL, n=6, bevel=0.0)
    mb.cyl(0.40, 0.42, (x, y, zt + 0.33), m=CAPL, n=6, r2=0.18, bevel=0.0)


# ------------------------------------------------------------------ geometria 2D
def clean(poly, eps=0.03):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append((float(p[0]), float(p[1])))
    while len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def circle(c, r, n=32, rot=0.0):
    return [(c[0] + r * math.cos(rot + 2 * math.pi * k / n), c[1] + r * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def rect_rot(cx, cy, w, d, deg):
    """retangulo w (lateral) x d (ao longo da frente 'deg') centrado em (cx, cy)"""
    a = math.radians(deg)
    fx, fy = math.cos(a), math.sin(a)
    sx, sy = -fy, fx
    return ccw([(cx + sx * s * w / 2 + fx * t * d / 2, cy + sy * s * w / 2 + fy * t * d / 2)
                for s, t in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def ribbon(pts, hw, ext=0.0):
    """faixa de meia-largura hw ao longo da polilinha (juntas em esquadro), pontas alongadas ext"""
    pts = [tuple(p) for p in pts]
    if ext and len(pts) >= 2:
        (x0, y0), (x1, y1) = pts[0], pts[1]
        ln = math.hypot(x1 - x0, y1 - y0) or 1.0
        pts[0] = (x0 - (x1 - x0) / ln * ext, y0 - (y1 - y0) / ln * ext)
        (x0, y0), (x1, y1) = pts[-2], pts[-1]
        ln = math.hypot(x1 - x0, y1 - y0) or 1.0
        pts[-1] = (x1 + (x1 - x0) / ln * ext, y1 + (y1 - y0) / ln * ext)
    left, right = [], []
    n = len(pts)
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
            ln = math.hypot(dx, dy) or 1.0
            nx, ny, k = -dy / ln, dx / ln, 1.0
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
            ln = math.hypot(dx, dy) or 1.0
            nx, ny, k = -dy / ln, dx / ln, 1.0
        else:
            ax, ay = x - pts[i - 1][0], y - pts[i - 1][1]
            bx, by = pts[i + 1][0] - x, pts[i + 1][1] - y
            la, lb = math.hypot(ax, ay) or 1.0, math.hypot(bx, by) or 1.0
            n1 = (-ay / la, ax / la)
            n2 = (-by / lb, bx / lb)
            nx, ny = n1[0] + n2[0], n1[1] + n2[1]
            ln = math.hypot(nx, ny) or 1.0
            nx, ny = nx / ln, ny / ln
            k = 1.0 / max(0.5, nx * n1[0] + ny * n1[1])          # esquadro (miter)
        left.append((x + nx * hw * k, y + ny * hw * k))
        right.append((x - nx * hw * k, y - ny * hw * k))
    return ccw(left + list(reversed(right)))


def blob(cx, cy, rx, ry, rot, seed, n=28, amp=0.13):
    """mancha SUAVE (elipse com 3 ondulacoes lentas, sem serrilha): contorno de gramado organico, nunca um circulo"""
    rng = random.Random(seed)
    p1, p2, p3 = rng.uniform(0, 6.28), rng.uniform(0, 6.28), rng.uniform(0, 6.28)
    out = []
    ca, sa = math.cos(rot), math.sin(rot)
    for k in range(n):
        t = 2 * math.pi * k / n
        f = (1.0 + amp * math.sin(2 * t + p1) + amp * 0.8 * math.sin(3 * t + p2) + amp * 0.45 * math.sin(5 * t + p3)
             + 0.12 * math.cos(t + p1))
        x, y = rx * f * math.cos(t), ry * f * math.sin(t)
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return out


def resample_closed(pts, step):
    """pontos igualmente espacados num contorno fechado: (x, y, nx, ny) com a normal para FORA (anti-horario)"""
    pts = ccw(pts)
    n = len(pts)
    segs = []
    tot = 0.0
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, ln, tot))
        tot += ln
    m = max(3, int(round(tot / step)))
    out = []
    si = 0
    for k in range(m):
        t = tot * k / m
        while si < n - 1 and segs[si][3] + segs[si][2] < t:
            si += 1
        a, b, ln, t0 = segs[si]
        f = (t - t0) / ln if ln > 1e-9 else 0.0
        x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        pa, pb = pts[(si - 1) % n], pts[(si + 2) % n]
        tx, ty = pb[0] - pa[0], pb[1] - pa[1]
        tl = math.hypot(tx, ty) or 1.0
        out.append((x, y, ty / tl, -tx / tl))
    return out


# ------------------------------------------------------------------ VARREDURA: regioes exatas em trapezios
def scan_regions(domain, layers):
    """domain: poligonos (uniao) = onde ha topo; layers: [[poligonos], ...]. Devolve [(flags, contorno)] com flags =
    tupla (dentro da camada k?) - trapezios EXATOS (as arestas sao retas dentro de cada faixa entre cotas de vertice),
    fundidos na vertical quando as arestas da esquerda/direita e a classe se repetem."""
    polys = [(ccw(clean(p)), -1) for p in domain] + [(ccw(clean(p)), k) for k, lay in enumerate(layers) for p in lay]
    polys = [(p, g) for p, g in polys if len(p) >= 3]
    edges = []                                  # (ylo, yhi, x@ylo, x@yhi, pid)
    ys = set()
    for pid, (p, g) in enumerate(polys):
        n = len(p)
        for i in range(n):
            (x0, y0), (x1, y1) = p[i], p[(i + 1) % n]
            ys.add(round(y0, 5))
            if abs(y1 - y0) < 1e-7:
                continue
            if y0 < y1:
                edges.append((y0, y1, x0, x1, pid))
            else:
                edges.append((y1, y0, x1, x0, pid))
    group = [g for p, g in polys]
    nl = len(layers)
    # arestas de poligonos diferentes que se CRUZAM dentro de uma faixa: a cota do cruzamento vira divisa de faixa
    # (sem isso o trapezio sai torcido e sobrepoe o vizinho)
    import numpy as np
    if edges:
        E = np.array([e[:4] for e in edges])
        y0, y1, xa, xb = E[:, 0], E[:, 1], E[:, 2], E[:, 3]
        sl = (xb - xa) / (y1 - y0)
        for i in range(len(edges)):
            lo = np.maximum(y0[i], y0)
            hi = np.minimum(y1[i], y1)
            m = hi - lo > 1e-6
            m[i] = False
            if not m.any():
                continue
            fi_lo = xa[i] + sl[i] * (lo - y0[i])
            fi_hi = xa[i] + sl[i] * (hi - y0[i])
            fj_lo = xa + sl * (lo - y0)
            fj_hi = xa + sl * (hi - y0)
            d0, d1 = fi_lo - fj_lo, fi_hi - fj_hi
            c = m & (d0 * d1 < 0)
            if c.any():
                yc = lo[c] + (hi[c] - lo[c]) * d0[c] / (d0[c] - d1[c])
                ys.update(round(float(v), 5) for v in yc)
    ys = sorted(ys)
    edges.sort(key=lambda e: e[0])

    def xat(e, y):
        y0, y1, x0, x1, _ = e
        return x0 + (x1 - x0) * (y - y0) / (y1 - y0)
    out = []
    openp = {}                                  # (eL, eR, cls) -> [ya, eL, eR, cls]
    ei = 0
    active = []
    for ya, yb in zip(ys, ys[1:]):
        if yb - ya < 1e-5:
            continue
        ym = (ya + yb) / 2
        while ei < len(edges) and edges[ei][0] <= ym:
            active.append(edges[ei])
            ei += 1
        active = [e for e in active if e[1] > ym]
        cr = sorted(((xat(e, ym), idx, e) for idx, e in enumerate(active)), key=lambda t: t[0])
        inside = set()
        cur = []                                # trapezios desta faixa [(eL, eR, cls)]
        for j, (xm, _, e) in enumerate(cr):
            pid = e[4]
            if pid in inside:
                inside.discard(pid)
            else:
                inside.add(pid)
            if j + 1 >= len(cr):
                break
            if any(group[q] == -1 for q in inside):
                fl = tuple(any(group[q] == k for q in inside) for k in range(nl))
            else:
                fl = None
            e2 = cr[j + 1][2]
            if fl is None:
                continue
            if cur and cur[-1][2] == fl and cur[-1][1] is e:
                cur[-1] = (cur[-1][0], e2, fl)
            else:
                cur.append((e, e2, fl))
        nxt = {}
        for eL, eR, fl in cur:
            key = (id(eL), id(eR), fl)
            if key in openp:
                nxt[key] = openp.pop(key)
            else:
                nxt[key] = [ya, eL, eR, fl]
        for key, (y0, eL, eR, fl) in openp.items():
            out.append((fl, (y0, ya, eL, eR)))
        openp = nxt
        last = yb
    for key, (y0, eL, eR, fl) in openp.items():
        out.append((fl, (y0, last, eL, eR)))
    res = []
    for fl, (y0, y1, eL, eR) in out:
        pts = _dedupe([(xat(eL, y0), y0), (xat(eR, y0), y0), (xat(eR, y1), y1), (xat(eL, y1), y1)], 1e-4)
        if len(pts) >= 3 and abs(SL.area(pts)) > 1e-4:
            res.append((fl, pts))
    return res


def flat_face(mb, pts, z, m):
    """face horizontal (para cima) com material EXATO (sem sorteio de variante)"""
    bm = mb.bm
    vs = [bm.verts.new((x, y, z)) for x, y in ccw(pts)]
    f = bm.faces.new(vs)
    f.material_index = mb._mi(m)
    f[mb.tint] = 0.0
    f.smooth = False
    f.normal_update()
    mb._uv([f], m)
    return f


# ------------------------------------------------------------------ restricoes (pontes, escadas, agua, castelo, subsolo)
BRIDGES = sg_col.bridge_list()
FALLS = []
for _wx, _wy, _wz, _deg in L.WATERFALLS:
    FALLS.append((_wx, _wy, _wz, math.cos(math.radians(_deg)), math.sin(math.radians(_deg))))


def hex_pts(cx, cy, r, n=6, rot=0.0):
    return [(cx + r * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)] + [(cx, cy)]


def water_fix(cx, cy, r, zt):
    """a cortina da cachoeira cai alem do labio: coluna na frente dela recua e baixa sob o labio"""
    for wx, wy, wz, ux, uy in FALLS:
        lat = abs(-(cx - wx) * uy + (cy - wy) * ux)
        along = (cx - wx) * ux + (cy - wy) * uy
        if lat < r + 4.6 and along > -r - 3.0:
            if along + r > 0.6:
                sh = along + r - 0.6
                cx -= ux * sh
                cy -= uy * sh
            zt = min(zt, wz - 0.4)
    return cx, cy, zt


def cap_top(cx, cy, r, zt):
    """nao furar piso: vertice dentro de patamar -> topo abaixo da cota; pontes/escadas por cima -> topo abaixo"""
    for px, py in hex_pts(cx, cy, r * 1.02):
        z = L.zone_of(px, py)
        if z is not None:
            zt = min(zt, z - 0.4)
    for nm, a, b, z, w in BRIDGES:
        if sg_col._in_rect_along(cx, cy, a, b, w / 2 + r + 1.0, pad=r + 2.5):
            zt = min(zt, z - 2.6)
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        fp = sg_col.stair_footprint(nm, pad=1.5)
        if any(L.point_in_poly(px, py, fp) for px, py in hex_pts(cx, cy, r + 1.4)):
            zt = min(zt, foot[2] - 0.1)
    return zt


def _box_hit(cx, cy, r, z0, z1, box, pad=0.3):
    x0, y0, zb0, x1, y1, zb1 = box
    if cx + r <= x0 - pad or cx - r >= x1 + pad or cy + r <= y0 - pad or cy - r >= y1 + pad:
        return False
    return not (z1 <= zb0 - pad or z0 >= zb1 + pad)


CAVE_BOX = (CX0, CY0, CZ0, CX1, max(CY1, L.SPIRAL_C[1] + L.SPIRAL_R_OUT + 1.0), CZ1)
DUN_BOX = (KX0, KY0, KZ0, KX1, KY1, KZ1)


def dun_ok(cx, cy, r, z0, z1):
    """a peca (disco de raio r, z0..z1) fica fora do subsolo (salas da masmorra e salao sombrio)?"""
    return not (_box_hit(cx, cy, r, z0, z1, DUN_BOX) or _box_hit(cx, cy, r, z0, z1, CAVE_BOX))


def stair_hit(x, y, pad=1.0):
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        if L.point_in_poly(x, y, sg_col.stair_footprint(nm, pad=pad)):
            return True
    return False


# volumes do CASTELO (1a) que tocam as bordas: a muralha inteira (x -172..172, y -23..-13) e as torres do portao.
# Ali o terreno nao poe alvenaria/contraforte/parapeito (F3).
CAS_CIRCLES = [(x, y, r + 1.5) for x, y, r in L.GATEHOUSE_TOWERS] + [(x, y, r + 1.5) for x, y, r, t in L.FRONT_TOWERS]
CAS_RECTS = [(L.WALL_X[0] - 2.0, L.WALL_Y0 - 1.0, L.WALL_X[1] + 2.0, L.WALL_Y1 + 1.5)]


def castle_hit(x, y, r=0.0):
    for cx, cy, cr in CAS_CIRCLES:
        if math.hypot(x - cx, y - cy) < cr + r:
            return True
    for x0, y0, x1, y1 in CAS_RECTS:
        if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
            return True
    return False


def water_gap(x, y):
    """trecho de borda por onde a agua de uma cachoeira sai (parapeito aberto)"""
    for wx, wy, wz, ux, uy in FALLS:
        lat = abs(-(x - wx) * uy + (y - wy) * ux)
        back = (wx - x) * ux + (wy - y) * uy
        if lat < 3.6 and -1.0 < back < 18.0:
            return True
    return False


# ------------------------------------------------------------------ setores (massa grande dividida em objetos)
RIM = clean(ccw(L.ISLAND_RIM))


def _centroid(poly):
    a = cx = cy = 0.0
    n = len(poly)
    for i in range(n):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % n]
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    return (cx / (3 * a), cy / (3 * a))


C = _centroid(RIM)
SECT = ["S", "E", "NE", "N", "NW", "W"]


def sector_of(x, y):
    a = math.degrees(math.atan2(y - C[1], x - C[0]))
    return SECT[int(((a + 120.0) % 360.0) // 60.0)]


def check_star():
    angs = [math.atan2(y - C[1], x - C[0]) for x, y in RIM]
    bad = 0
    for a0, a1 in zip(angs, angs[1:] + angs[:1]):
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        if d <= 0:
            bad += 1
    if bad:
        print("TER AVISO contorno nao estrelado em relacao ao centro: %d passos" % bad)


_MB = {}


def smb(name, detail="far"):
    if name not in _MB:
        _MB[name] = MB(name, "02_TERRAIN", random.Random(zlib.crc32(name.encode("utf-8")) & 0xffff), detail=detail,
                       floor=-999)
    return _MB[name]


def cliff_mb(x, y):
    return smb("SG_Ter_Cliff_" + sector_of(x, y))


# ------------------------------------------------------------------ areas de piso do layout (F5) e manchas de grama
def floor_areas():
    """areas onde OUTRO modulo poe piso por cima do patamar: o topo desce RECESS ali (nunca coplanar)"""
    out = [circle(L.PLAZA_C, L.PLAZA_R + 0.6, 40)]
    for pts, w, z in L.STREETS:
        out.append(ribbon(pts, w / 2 + 0.6, ext=0.6))
    for nm, t, x, y, w, d, deg, z in L.HOUSES:
        out.append(rect_rot(x, y, w + 1.2, d + 1.2, deg))
    out.append(circle(L.CRAFT_C, L.CRAFT_R + 0.9, 32))
    hx0, hy0, hx1, hy1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
    t = L.HALL_WALL
    out.append(rect(hx0 - t, hy0 - t, hx1 + t, hy1 + t))                  # salao (piso do sg_hall)
    out.append(rect(*L.CROWN_BASE))                                        # presbiterio / poco (castelo)
    mx, my, mr = L.MIRANTE_E
    out.append(circle((mx, my), mr + 0.6, 32))                             # terraco do jardim-mirante
    for nm, a, b, z, w in BRIDGES:                                         # boca da ponte da invocacao
        if nm == "SummonBridge":                                           # (a da SAIDA: o topo vai ate a borda real,
            out.append(ribbon([a, b], w / 2 + 0.6, ext=0.6))              # u ~1,9; o sg_exit comeca depois dela)
    return out


def cut_areas():
    """sem topo nenhum: o poco da escada caracol"""
    return [circle(L.SPIRAL_C, L.SPIRAL_R_OUT + 0.8, 32)]


# chao do gramado (pedido do usuario: grama "spammada" = poluicao; o capim e da onda 2): 2 tons em manchas GRANDES e
# SUAVES, dirigidas (clareiras de luar ao longo dos becos, do terraco norte e da vila alta), longe das bordas
# (cx, cy, rx, ry, giro)
PATCHES = [
    # P2 (vila alta)
    (-146.0, -120.0, 26.0, 18.0, 0.4), (-150.0, -40.0, 20.0, 14.0, -0.3), (38.0, -122.0, 30.0, 16.0, 0.15),
    (150.0, -128.0, 20.0, 14.0, 0.6), (-24.0, -44.0, 22.0, 12.0, 0.05), (160.0, -52.0, 14.0, 22.0, 0.2),
    # P3 (becos, cantos do patio, terraco norte)
    (-128.0, 22.0, 20.0, 15.0, 0.5), (132.0, 24.0, 18.0, 15.0, -0.4), (-132.0, 130.0, 14.0, 36.0, 0.05),
    (-128.0, 242.0, 13.0, 30.0, -0.08), (126.0, 96.0, 15.0, 30.0, -0.06), (122.0, 246.0, 14.0, 34.0, 0.1),
    (-62.0, 362.0, 30.0, 11.0, 0.12), (66.0, 356.0, 28.0, 12.0, -0.25), (-96.0, 330.0, 16.0, 12.0, 0.6),
    # ombro
    (-110.0, -284.0, 24.0, 5.0, 0.0), (92.0, -283.0, 22.0, 5.0, -0.05),
]


def patch_polys():
    return [blob(x, y, rx, ry, a, 5101 + 37 * i) for i, (x, y, rx, ry, a) in enumerate(PATCHES)]


# ------------------------------------------------------------------ 1) topos dos patamares e do ombro
# FINESSE 3 (02.01 / 01.01 / 01.11 / 16.08 / 14.03): o topo deixa de ser um plano liso. Camadas, por prioridade:
#   cut (sem topo) > recess (z-0,45: piso de OUTRO modulo) > hold (fica na cota: torres do castelo) > slab (LEITO escuro
#   z-0,32: por cima vao as lajes do paving()) > gravel (cascalho z-0,12 ao pe de parapeitos e muros, com meio-fio) >
#   pave_zone (calcamento) > patch (2o tom da grama) > base (grama / calcamento).
def emit_top(mb, domain, z, cuts, recess, pave_zone, patches, base, slab=(), gravel=(), hold=()):
    """topo em trapezios exatos; onde o topo desce sai o ESPELHO vertical (risers): nada de fresta para o oco"""
    layers = [cuts, recess, hold, gravel, slab, pave_zone, patches]
    n = 0
    for fl, pts in scan_regions(domain, layers):
        cut, rec, hld, grv, slb, pav, pat = fl
        if cut:
            continue
        if rec:
            zz, m = z - RECESS, (BED if slb else (PAVE if (pav or base == PAVE) else GRASS))
        elif hld:
            zz, m = z, (PAVE if (pav or base == PAVE) else GRASS)
        elif grv:
            zz, m = z - GRV_D, GRAVEL
        elif slb:
            zz, m = z - BED_D, BED
        else:
            zz, m = z, (PAVE if (pav or base == PAVE) else (GRASS2 if pat else GRASS))
        flat_face(mb, pts, zz, m)
        n += 1
    if recess or slab or gravel:
        risers(mb, domain, cuts, recess, pave_zone, z, base, slab=slab, gravel=gravel, hold=hold)
    return n


def risers(mb, domain, cuts, recess, pave_zone, z, base, step=0.5, slab=(), gravel=(), hold=()):
    """espelhos verticais em toda divisa onde o topo muda de cota (recess / leito das lajes / cascalho), virados para
    o lado mais BAIXO; material: leito escuro junto das lajes, cascalho junto do cascalho, senao o do piso de cima"""
    pip = L.point_in_poly

    def lvl(x, y):
        if not any(pip(x, y, p) for p in domain) or any(pip(x, y, p) for p in cuts):
            return None
        if any(pip(x, y, p) for p in recess):
            return RECESS
        if any(pip(x, y, p) for p in hold):
            return 0.0
        if any(pip(x, y, p) for p in gravel):
            return GRV_D
        if any(pip(x, y, p) for p in slab):
            return BED_D
        return 0.0
    bm = mb.bm
    for polys in (recess, slab, gravel):
        for poly in polys:
            pts = clean(ccw(poly))
            n = len(pts)
            for i in range(n):
                a, b = pts[i], pts[(i + 1) % n]
                dx, dy = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dy)
                if ln < 0.05:
                    continue
                ux, uy = dx / ln, dy / ln
                nx, ny = uy, -ux
                ns = max(1, int(math.ceil(ln / step)))
                keys = []
                for k in range(ns):
                    t = (k + 0.5) * ln / ns
                    x, y = a[0] + ux * t, a[1] + uy * t
                    lo, li = lvl(x + nx * 0.06, y + ny * 0.06), lvl(x - nx * 0.06, y - ny * 0.06)
                    keys.append((lo, li) if (lo is not None and li is not None and abs(lo - li) > 1e-6) else None)
                k = 0
                while k < ns:
                    key = keys[k]
                    if key is None:
                        k += 1
                        continue
                    j = k
                    while j + 1 < ns and keys[j + 1] == key:
                        j += 1
                    lo, li = key
                    t0, t1 = k * ln / ns, (j + 1) * ln / ns
                    p0 = (a[0] + ux * t0, a[1] + uy * t0)
                    p1 = (a[0] + ux * t1, a[1] + uy * t1)
                    xm, ym = (p0[0] + p1[0]) / 2 + nx * 0.06, (p0[1] + p1[1]) / 2 + ny * 0.06
                    if BED_D in (lo, li):
                        m = BED
                    elif GRV_D in (lo, li):
                        m = GRAVEL
                    else:
                        m = PAVE if base == PAVE or any(pip(xm, ym, p) for p in pave_zone) else GRASS
                    zl, zh = z - max(lo, li), z - min(lo, li)
                    vs = [bm.verts.new((p1[0], p1[1], zl)), bm.verts.new((p0[0], p0[1], zl)),
                          bm.verts.new((p0[0], p0[1], zh)), bm.verts.new((p1[0], p1[1], zh))]
                    if lo > li:                      # o lado de FORA e o mais baixo: face virada para fora
                        vs.reverse()
                    f = bm.faces.new(vs)
                    f.material_index = mb._mi(m)
                    f[mb.tint] = 0.0
                    f.normal_update()
                    mb._uv([f], m)
                    k = j + 1


# ------------------------------------------------------------------ ONDA 2 (agente do jardim, 2026-09-30): recorte do
# PATIO-JARDIM. Funcao isolada pedida pela coordenacao (o resto do sg_terrain e do agente 1f):
#   - o patio inteiro (CASTLE_FORECOURT) desce RECESS: o piso de la (eixo nobre, cascalho, lajes, canteiros) e todo do
#     sg_court, nunca coplanar com o topo do terreno (F5);
#   - os 2 GRAMADOS REBAIXADOS 1,2 (COURT_LAWNS = contorno EXTERNO do murete de cantaria do sg_court) ficam SEM topo e o
#     terreno fecha o buraco sozinho: chao de grama em P3-1,2 + espelhos verticais ate o topo rebaixado (o murete do
#     sg_court encosta neles de costas: face oposta, inerte). Sem o sg_court (estudio de outra zona) o buraco le como um
#     gramado rebaixado simples, sem fresta.
#   - a COLISAO do piso do P3 (sg_col.floors) e da onda 0: o furo dos gramados precisa entrar nos 'holes' do P3 la
#     (pendencia no relatorio da onda 2; o sg_court poe a colisao do fundo do gramado e dos degraus).
COURT_LAWN_DEPTH = 1.2
COURT_LAWNS = [(33.0, -3.0, 83.0, 15.0), (-83.0, -3.0, -33.0, 15.0)]


def court_garden_areas():
    """(rebaixo, recorte) do patio-jardim para o topo do P3"""
    return [rect(*L.CASTLE_FORECOURT)], [rect(*r) for r in COURT_LAWNS]


def court_lawn_pits(mb):
    """fundo dos gramados rebaixados (grama em P3-1,2) + espelhos do recorte (de P3-1,2 ate o topo rebaixado)"""
    bm = mb.bm
    zb, zt = P3 - COURT_LAWN_DEPTH, P3 - RECESS
    for x0, y0, x1, y1 in COURT_LAWNS:
        flat_face(mb, rect(x0, y0, x1, y1), zb, GRASS)
        pts = ccw(rect(x0, y0, x1, y1))
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            vs = [bm.verts.new((a[0], a[1], zb)), bm.verts.new((a[0], a[1], zt)), bm.verts.new((b[0], b[1], zt)),
                  bm.verts.new((b[0], b[1], zb))]
            f = bm.faces.new(vs)                      # contorno anti-horario: normal para DENTRO do buraco
            f.material_index = mb._mi(ROCK)
            f[mb.tint] = 0.0
            f.normal_update()
            mb._uv([f], ROCK)


def tops():
    fl = L.floors()
    rec = floor_areas()
    cut = cut_areas()
    court_rec, court_cut = court_garden_areas()          # onda 2: patio-jardim (ver court_lawn_pits)
    pats = patch_polys()
    court = [rect(*L.CASTLE_FORECOURT)]
    # FINESSE 3 (02.01 / 14.03): o P1 deixa de ser o plano claro de calcamento: grama escura com clareiras (as ruas e a
    # praca do sg_village ficam 0,3 acima, como calcadas elevadas), lajes so na calcada alta e nos rodapes dos predios
    base = {"P1": GRASS, "P2": GRASS, "P3": GRASS, "EntryHigh": PAVE, "EntryLow": PAVE}
    slabs, gravels, holds = dress_polys()
    nf = 0
    for nm, poly, z, pr in fl:
        if nm == "Summon":
            continue
        higher = [p for n2, p, z2, pr2 in fl if pr2 > pr]
        mb = smb("SG_Ter_Terrace_" + ("Entry" if nm.startswith("Entry") else nm))
        if nm == "EntryLow":                             # patio baixo aberto no DECK, x +-14,6, ate o contorno sul
            nf += emit_top(mb, [rect(*PATIO_LOW)], z, higher + cut + [rect(*UNDER_BRIDGE)], [], [], [], PAVE)
            continue
        nf += emit_top(mb, [poly], z, higher + cut + (court_cut if nm == "P3" else []),
                       (rec + (court_rec if nm == "P3" else [])) if nm != "EntryHigh" else [],
                       court if nm == "P3" else [], pats if base[nm] == GRASS else [], base[nm],
                       slab=slabs.get(nm, []), gravel=gravels.get(nm, []), hold=holds.get(nm, []))
        if nm == "P3":
            court_lawn_pits(mb)                          # onda 2: fundo dos gramados rebaixados
    # ombro (terreno bravo) ao norte do pescoco: contorno menos os patamares, em grama
    top = SL.clip(RIM, 0.0, -1.0, -CUT_Y)                # y >= -294
    ms = smb("SG_Ter_Shoulder")
    nf += emit_top(ms, [top], SH, [p for n2, p, z2, pr2 in fl] + [L.summon_poly()], [], [], pats, GRASS,
                   gravel=gravels.get("Shoulder", []))
    print("TER TOPO trapezios=%d" % nf)


# ------------------------------------------------------------------ 1b) VESTIR O CHAO (FINESSE 3): bordaduras, rodapes
# de predio, lajes da calcada alta e meio-fios. Tudo com o TOPO na cota do patamar (a colisao do sg_col nao muda):
#   - bordadura (01.11 / 03.05): cascalho de 1,3 rebaixado 0,12 ao pe de todo parapeito, meio-fio chanfrado de 0,5 do
#     lado da grama; ao pe dos muros de arrimo a faixa tem 3,6 (cobre o soco dos contrafortes) no patamar de baixo;
#   - rodape de chao (16.08): calcada de 2,0 de lajes em volta de cada casa, dos flancos e fundo do castelo e da
#     alquimia, com meio-fio para a grama; o leito escuro fica 0,32 abaixo e so aparece nas juntas (0,12);
#   - calcada alta (01.01): lajes em fiadas transversais de 3 (e 4) com junta desencontrada, soleira de cantaria sob o
#     portico B, meio-fio no contorno e disco de pedra (sem emblema) no spawn.
_RUNS = {}
CURBS = []          # (objeto, R, d_cascalho, d_grama, z) -> meio-fio em perfil (curbs())
LVL_Z = {"P1": P1, "P2": P2, "P3": P3}


def runs_of(nm):
    if nm not in _RUNS:
        _RUNS[nm] = [R for R in edge_runs(nm, SL.floor_poly(nm), LVL_Z[nm]) if not R["cas"]]
    return _RUNS[nm]


def strip_poly(R, t0, t1, d0, d1):
    return ccw([_xy(R, t0, d0), _xy(R, t1, d0), _xy(R, t1, d1), _xy(R, t0, d1)])


def house_frame(hrec):
    """(centro, eixo da frente f, eixo lateral s): pegada = |s| <= w/2 (lateral), |t| <= d/2 (ao longo da frente)"""
    nm, tp, x, y, w, d, deg, z = hrec
    a = math.radians(deg)
    return (x, y), (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a)), w, d, z


def dress_polys():
    """por patamar: zonas de LAJES (leito), faixas de CASCALHO e zonas 'hold'; preenche CURBS"""
    slabs, gravel, hold = {}, {}, {}
    CURBS.clear()
    for nm in ("P1", "P2", "P3"):
        z = LVL_Z[nm]
        for R in runs_of(nm):
            if R["open"] or R["br"] or R["t1"] - R["t0"] < 2.0:
                continue
            if R["cls"] == "wild":                                   # bordadura ao pe do parapeito (deste patamar)
                gravel.setdefault(nm, []).append(strip_poly(R, R["t0"], R["t1"], -(GW_E + CW), 0.6))
                CURBS.append(("SG_Ter_Wall_" + nm, R, -GW_E, -(GW_E + CW), z))
            else:                                                    # pe do muro de arrimo: no patamar de BAIXO
                x, y = _xy(R, (R["t0"] + R["t1"]) / 2, 2.0)
                low = L.floor_name(x, y)
                if low not in LVL_Z:
                    continue
                gravel.setdefault(low, []).append(strip_poly(R, R["t0"], R["t1"], -0.2, GW_F))
                CURBS.append(("SG_Ter_Wall_" + nm, R, GW_F - CW, GW_F, R["zo"]))
    # pe da calcada alta no ombro (01.11): dos 2 lados, de y -294 ate a entrada no P1
    hx0, hy0, hx1, hy1 = L.ENTRY_HIGH
    yend = max(hy0 + 1.0, -272.0)
    for s_ in (-1, 1):
        xe = hx1 if s_ > 0 else hx0
        a = (xe, hy0) if s_ > 0 else (xe, yend)
        u = (0.0, 1.0) if s_ > 0 else (0.0, -1.0)
        R = dict(a=a, u=u, n=(u[1], -u[0]), t0=0.0, t1=yend - hy0, zo=SH, ln=yend - hy0, i=-1, cls="terrace",
                 open=False, cas=False, br=False)
        gravel.setdefault("Shoulder", []).append(strip_poly(R, 0.0, yend - hy0, -0.2, GW_F))
        CURBS.append(("SG_Ter_Wall_P1", R, GW_F - CW, GW_F, SH))
    # rodapes de chao (16.08)
    A = APRON + CW
    for hrec in L.HOUSES:
        c, f, sv, w, d, z = house_frame(hrec)
        lvl = "P1" if abs(z - P1) < 0.1 else "P2"
        slabs.setdefault(lvl, []).append(rect_rot(c[0], c[1], w + 1.2 + 2 * A, d + 1.2 + 2 * A, hrec[6]))
    hx0, hy0, hx1, hy1 = L.HALL_X0 - L.HALL_WALL, L.HALL_Y0 - L.HALL_WALL, L.HALL_X1 + L.HALL_WALL, L.HALL_Y1 + L.HALL_WALL
    slabs.setdefault("P3", []).append(rect(hx0 - 0.3 - A, L.CASTLE_FORECOURT[3], hx1 + 0.3 + A, hy1 + 0.3 + A))
    hold["P3"] = [circle((cx, cy), cr, 24) for cx, cy, cr in CAS_CIRCLES]
    slabs.setdefault("P2", []).append(circle(L.CRAFT_C, L.CRAFT_R + 0.9 + A, 40))
    slabs["EntryHigh"] = [rect(*L.ENTRY_HIGH)]
    return slabs, gravel, hold


_FLOOR_AREAS = []


def in_recess(x, y):
    if not _FLOOR_AREAS:
        _FLOOR_AREAS.extend(floor_areas())
    return any(L.point_in_poly(x, y, p) for p in _FLOOR_AREAS) or castle_hit(x, y, 0.3)


def near_edge(x, y, d=GW_E + CW + 0.5):
    """perto (< d) da borda do patamar onde (x, y) esta: ali manda a bordadura do parapeito, nao o rodape"""
    nm = L.floor_name(x, y)
    if nm not in LVL_Z:
        return True
    pts = SL.floor_poly(nm)
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        if L.seg_dist(x, y, a[0], a[1], b[0], b[1])[0] < d:
            return True
    return False


def blocked_apron(x, y):
    return in_recess(x, y) or near_edge(x, y)


def pred_spans(R, t0, t1, d, pred, step=0.5):
    """trechos de t0..t1 onde pred(x, y) e falso (meio-fios que saltam recortes / bordas)"""
    out, cur = [], None
    t = t0
    while t <= t1 + 1e-6:
        x, y = _xy(R, t, d)
        ok = not pred(x, y)
        if ok and cur is None:
            cur = t
        if not ok and cur is not None:
            if t - step - cur > 0.6:
                out.append((cur, t - step))
            cur = None
        t += step
    if cur is not None and t1 - cur > 0.6:
        out.append((cur, t1))
    return out


def slab(mb, cx, cy, sx, sy, ang, z, m, bevel=0.04, th=0.30):
    """laje: caixa de 0,30 com o topo EXATO na cota, material exato (sem sorteio) e chanfro so nas arestas de cima"""
    M = Matrix.LocRotScale(Vector((cx, cy, z - th / 2)), Euler((0.0, 0.0, ang)), Vector((sx, sy, th)))
    r = bmesh.ops.create_cube(mb.bm, size=1.0, matrix=M)
    fs = mb._post(r["verts"], m, 0.0, min(bevel, min(sx, sy) * 0.3), 1)
    mi = mb._mi(m)
    for f in fs:
        f.material_index = mi


def slab_poly(mb, pts, z, m, bevel=0.04, th=0.30):
    """laje poligonal (topo na cota), material exato, chanfro nas arestas de cima"""
    pts = clean(ccw(pts))
    if len(pts) < 3:
        return
    bm = mb.bm
    vb = [bm.verts.new((x, y, z - th)) for x, y in pts]
    vt = [bm.verts.new((x, y, z)) for x, y in pts]
    bm.faces.new(list(reversed(vb)))
    bm.faces.new(vt)
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    fs = mb._post(vb + vt, m, 0.0, bevel, 1, angle=0.6)
    mi = mb._mi(m)
    for f in fs:
        f.material_index = mi


APRON_LEN = (4.4, 5.4, 4.8, 6.0, 4.0)     # modulos DIRIGIDOS das lajes dos rodapes (ciclo fixo)


def apron_band(mb, org, u, n, t0, t1, d0, d1, z, tone, k0=0):
    """faixa de lajes ao longo de u (de t0 a t1), entre d0 e d1 (uma laje de largura), junta 0,12; tom por faixa"""
    ux, uy = u
    nx, ny = n
    ang = math.atan2(uy, ux)
    pos, k = t0, k0
    dm = (d0 + d1) / 2
    while pos < t1 - 0.3:
        bl = APRON_LEN[k % 5]
        k += 1
        if t1 - (pos + bl) < 1.4:
            bl = t1 - pos
        pa, pb = pos + 0.06, pos + bl - 0.06
        tm = (pa + pb) / 2
        cx, cy = org[0] + ux * tm + nx * dm, org[1] + uy * tm + ny * dm
        if not blocked_apron(cx, cy):
            slab(mb, cx, cy, pb - pa, d1 - d0 - 0.12, ang, z, PAVE if (tone + k) % 2 else PAVE_B)
        pos += bl
    return k


def curb_prof(dg, dgr, z):
    """perfil do meio-fio no referencial do run: dg = lado do cascalho (chanfro, 0,12 de face), dgr = lado da grama"""
    s = 1.0 if dgr > dg else -1.0
    return [(dgr, z - 0.14), (dg, z - 0.14), (dg, z - 0.06), (dg + s * 0.06, z), (dgr, z)]


def curbs():
    """meio-fios das bordaduras (CURBS) nos objetos dos muros (detail near)"""
    n = 0
    for obj, R, dg, dgr, z in CURBS:
        mb = smb(obj, detail="near")
        for s0, s1 in free_spans(R, R["t0"], R["t1"], d=(dg + dgr) / 2, pad=0.3):
            ledge(mb, _W(R), s0, s1, curb_prof(dg, dgr, z), CAPL)
            n += 1
    print("TER MEIO-FIOS trechos=%d" % n)


def paving():
    """lajes com o topo na cota: calcada alta (01.01), rodapes de chao (16.08) e anel da alquimia"""
    mv = smb("SG_Ter_Paving_Vila", detail="near")
    m3 = smb("SG_Ter_Paving_P3", detail="near")
    A = APRON
    # --- rodapes das casas: 4 faixas (as laterais levam os cantos) + meio-fio em volta
    for hrec in L.HOUSES:
        c, f, sv, w, d, z = house_frame(hrec)
        mb = mv
        hw, hd = w / 2 + 0.6, d / 2 + 0.6                     # borda do recorte (floor_areas: +0,6)
        k = int(abs(c[0] * 3.0 + c[1] * 7.0)) % 5
        for sgn in (-1, 1):
            # faixa lateral (ao longo de f), com os cantos
            org = (c[0] + sv[0] * sgn * hw, c[1] + sv[1] * sgn * hw)
            nvec = (sv[0] * sgn, sv[1] * sgn)
            k = apron_band(mb, org, f, nvec, -(hd + A), hd + A, 0.06, A, z, 0, k)
            # faixa da frente / fundo (ao longo de sv), entre as laterais
            org = (c[0] + f[0] * sgn * hd, c[1] + f[1] * sgn * hd)
            nvec = (f[0] * sgn, f[1] * sgn)
            k = apron_band(mb, org, sv, nvec, -hw, hw, 0.06, A, z, 1, k)
        # meio-fio: 4 lados no contorno externo (de hw+A a hw+A+CW)
        for sgn in (-1, 1):
            for axis, lat, half in ((f, sv, hw), (sv, f, hd)):
                # lado perpendicular a 'lat' deslocado sgn*(half + A) ao longo de lat; corre ao longo de 'axis'
                org = (c[0] + lat[0] * sgn * (half + A), c[1] + lat[1] * sgn * (half + A))
                nvec = (lat[0] * sgn, lat[1] * sgn)
                other = (hd + A + CW) if axis is f else hw + A
                R = dict(a=org, u=axis, n=nvec)
                for s0, s1 in pred_spans(R, -other, other, CW / 2, blocked_apron):
                    ledge(mb, _W(R), s0, s1, curb_prof(0.0, CW, z), CAPL)
    # --- castelo: flancos e fundo do salao (as torres da fachada ficam de fora: castle_hit)
    hx0, hy0, hx1, hy1 = L.HALL_X0 - L.HALL_WALL, L.HALL_Y0 - L.HALL_WALL, L.HALL_X1 + L.HALL_WALL, L.HALL_Y1 + L.HALL_WALL
    y0 = L.CASTLE_FORECOURT[3]
    k = 2
    for sgn in (-1, 1):
        xe = hx1 if sgn > 0 else hx0
        k = apron_band(m3, (xe, y0), (0.0, 1.0), (sgn, 0.0), 0.0, hy1 - y0 + 0.3 + A, 0.36, 0.3 + A, P3, 0, k)
        R = dict(a=(xe + sgn * (0.3 + A), y0), u=(0.0, 1.0), n=(sgn, 0.0))
        for s0, s1 in pred_spans(R, 0.0, hy1 - y0 + 0.3 + A + CW, CW / 2, in_recess):
            ledge(m3, _W(R), s0, s1, curb_prof(0.0, CW, P3), CAPL)
    k = apron_band(m3, (hx0 - 0.3, hy1), (1.0, 0.0), (0.0, 1.0), 0.0, hx1 - hx0 + 0.6, 0.36, 0.3 + A, P3, 1, k)
    R = dict(a=(hx0 - 0.3 - A, hy1 + 0.3 + A), u=(1.0, 0.0), n=(0.0, 1.0))
    for s0, s1 in pred_spans(R, 0.0, hx1 - hx0 + 0.6 + 2 * A, CW / 2, in_recess):
        ledge(m3, _W(R), s0, s1, curb_prof(0.0, CW, P3), CAPL)
    # --- alquimia: anel de lajes em setores + meio-fio em 24 trechos
    cx, cy = L.CRAFT_C
    r0, r1 = L.CRAFT_R + 0.9 + 0.06, L.CRAFT_R + 0.9 + A
    ns = 28
    for q in range(ns):
        a0, a1 = 2 * math.pi * q / ns, 2 * math.pi * (q + 1) / ns
        g0, g1 = 0.06 / r0, 0.06 / r1
        pts = [(cx + r0 * math.cos(a0 + g0), cy + r0 * math.sin(a0 + g0)),
               (cx + r1 * math.cos(a0 + g1), cy + r1 * math.sin(a0 + g1)),
               (cx + r1 * math.cos(a1 - g1), cy + r1 * math.sin(a1 - g1)),
               (cx + r0 * math.cos(a1 - g0), cy + r0 * math.sin(a1 - g0))]
        mx, my = cx + (r0 + r1) / 2 * math.cos((a0 + a1) / 2), cy + (r0 + r1) / 2 * math.sin((a0 + a1) / 2)
        if not in_recess(mx, my):
            slab_poly(mv, pts, P2, PAVE if q % 2 else PAVE_B)
    rc = L.CRAFT_R + 0.9 + A
    for q in range(24):
        a0, a1 = 2 * math.pi * q / 24, 2 * math.pi * (q + 1) / 24
        p0 = (cx + rc * math.cos(a0), cy + rc * math.sin(a0))
        p1 = (cx + rc * math.cos(a1), cy + rc * math.sin(a1))
        ux, uy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        R = dict(a=p0, u=(ux, uy), n=(uy, -ux))
        if not in_recess(*_xy(R, ln / 2, 0.25)):
            ledge(mv, _W(R), 0.0, ln, curb_prof(0.0, CW, P2), CAPL)
    # --- calcada alta
    entry_walk(mv)


def entry_walk(mb):
    """calcada alta (01.01): fiadas transversais de 3 lajes (e de 4, com a junta desencontrada), soleira de cantaria
    de 1,4 sob o portico B, meio-fio de 0,7 no contorno, disco de pedra em moldura quadrada no spawn (sem emblema)"""
    hx0, hy0, hx1, hy1 = L.ENTRY_HIGH
    z = P1
    xw = hx1 - 0.7                                              # lajes ate 11,3; meio-fio 11,3..12
    sx, sy = L.ENTRY_SPAWN
    SQ = 3.75                                                   # meia-moldura do disco do spawn
    ysol0, ysol1 = L.PORTICO_B_Y - 0.7, L.PORTICO_B_Y + 0.7      # soleira
    plinth = (L.PORTICO_B_Y - 5.4, L.PORTICO_B_Y + 3.2)          # plintos dos pilares (|x| > 9,4)
    rows = []
    for k in range(4):
        rows.append((hy0 + 0.1 + 2.8 * k, hy0 + 0.1 + 2.8 * (k + 1)))
    rows += [(ysol1, ysol1 + (sy - SQ - ysol1) / 2), (ysol1 + (sy - SQ - ysol1) / 2, sy - SQ)]
    rows += [(sy - SQ, sy), (sy, sy + SQ), (sy + SQ, hy1)]
    for i, (ya, yb) in enumerate(rows):
        lim = 9.3 if (ya < plinth[1] and yb > plinth[0]) else xw
        if yb <= sy + SQ and ya >= sy - SQ:                     # fiadas ao lado da moldura do disco
            for s_ in (-1, 1):
                xa, xb = SQ + 0.06, lim
                slab(mb, s_ * (xa + xb) / 2, (ya + yb) / 2, xb - xa - 0.06, yb - ya - 0.12, 0.0, z,
                     PAVE if i % 2 else PAVE_B)
            continue
        cuts = ([-lim, -lim / 3.0, lim / 3.0, lim] if i % 2 == 0 else [-lim, -lim * 0.66, 0.0, lim * 0.66, lim])
        for xa, xb in zip(cuts, cuts[1:]):
            xa2 = xa + (0.06 if xa > -lim + 1e-6 else 0.0)
            xb2 = xb - (0.06 if xb < lim - 1e-6 else 0.0)
            slab(mb, (xa2 + xb2) / 2, (ya + yb) / 2, xb2 - xa2, yb - ya - 0.12, 0.0, z, PAVE if i % 2 else PAVE_B)
    # soleira (3 pecas de cantaria clara) entre os plintos
    for xa, xb in ((-9.3, -3.1), (-3.1, 3.1), (3.1, 9.3)):
        slab(mb, (xa + xb) / 2, L.PORTICO_B_Y, xb - xa - 0.1, ysol1 - ysol0 - 0.08, 0.0, z, CAPL, bevel=0.06)
    # meio-fio dos 2 lados (fora da zona dos plintos), chanfro para dentro
    for s_ in (-1, 1):
        for ya, yb in ((hy0, plinth[0] - 0.1), (plinth[1] + 0.1, hy1)):
            R = dict(a=(s_ * xw, ya), u=(0.0, 1.0), n=(s_, 0.0))
            ledge(mb, _W(R), 0.0, yb - ya, curb_prof(0.0, 0.7, z), CAPL)
    # disco do spawn: miolo octogonal claro, 8 cunhas, 4 cantos que fecham a moldura quadrada
    oct_r = 3.55
    g = 0.06
    for q in range(8):
        a0, a1 = math.pi / 4 * q + math.pi / 8, math.pi / 4 * (q + 1) + math.pi / 8
        pts = [(sx + 1.62 * math.cos(a0) - g * math.sin(a0), sy + 1.62 * math.sin(a0) + g * math.cos(a0)),
               (sx + oct_r * math.cos(a0) - g * math.sin(a0), sy + oct_r * math.sin(a0) + g * math.cos(a0)),
               (sx + oct_r * math.cos(a1) + g * math.sin(a1), sy + oct_r * math.sin(a1) - g * math.cos(a1)),
               (sx + 1.62 * math.cos(a1) + g * math.sin(a1), sy + 1.62 * math.sin(a1) - g * math.cos(a1))]
        slab_poly(mb, pts, z, PAVE_B if q % 2 else PAVE)
    slab_poly(mb, circle((sx, sy), 1.5, 8, math.pi / 8), z, CAPL, bevel=0.06)
    ro = oct_r + 0.12                                           # octogono com a junta de 0,12
    c8, s8 = ro * math.cos(math.pi / 8), ro * math.sin(math.pi / 8)
    for q in range(4):
        a = math.pi / 2 * q
        ca, sa = math.cos(a), math.sin(a)
        # canto (quadrante +x+y, girado q*90): do lado vertical do octogono ao canto do quadrado e de volta pelo lado
        # de cima; as arestas em x = 0 / y = 0 ficam com a junta para a peca vizinha
        loc = [(c8, g), (SQ, g), (SQ, SQ), (g, SQ), (g, c8), (s8, c8), (c8, s8)]
        pts = [(sx + x * ca - y * sa, sy + x * sa + y * ca) for x, y in loc]
        slab_poly(mb, pts, z, PAVE)


# ------------------------------------------------------------------ 2) corpos (so as faces laterais: a ilha e oca)
def sides(mb, poly, z0, z1, m, inset=None):
    """faces laterais do contorno (normais para fora), sem tampo nem fundo; inset(a, b) -> recuo da aresta"""
    pts = clean(ccw(poly))
    n = len(pts)
    bm = mb.bm
    allv = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.05:
            continue
        nx, ny = dy / ln, -dx / ln
        s = inset(a, b) if inset else 0.0
        a2 = (a[0] - nx * s, a[1] - ny * s)
        b2 = (b[0] - nx * s, b[1] - ny * s)
        vs = [bm.verts.new((a2[0], a2[1], z0)), bm.verts.new((b2[0], b2[1], z0)), bm.verts.new((b2[0], b2[1], z1)),
              bm.verts.new((a2[0], a2[1], z1))]
        bm.faces.new(vs)
        allv += vs
    if allv:
        mb._post(allv, m, None, 0, 1)


def _edge_inset(a, b):
    """o corpo do patamar recua atras de tudo que veste a borda (alvenaria, arremate, pisos/muros dos outros
    modulos que terminam na borda): 0,3; nas arestas que tocam a MURALHA (F3: y -23 e as quinas x +-172), 0,4"""
    for p in (a, b):
        if abs(p[1] - L.WALL_Y0) < 0.05 and (abs(a[1] - b[1]) < 0.05 or abs(abs(p[0]) - L.WALL_X[1]) < 0.5):
            return 0.4
    return 0.3


def bodies():
    for nm, poly, z, pr in L.floors():
        if nm == "Summon":
            continue
        z0 = {"EntryLow": 20.0, "EntryHigh": 26.0}.get(nm, BODY_BOT)
        mb = smb("SG_Ter_Terrace_" + ("Entry" if nm.startswith("Entry") else nm))
        ins = _edge_inset if nm in ("P1", "P2", "P3") else (lambda a, b: 0.3)
        if nm == "EntryLow":
            poly = rect(*PATIO_LOW)
        sides(mb, poly, z0, z, DARK, ins)      # entrada: recua 0,3 atras dos parapeitos do sg_entry
    # (o canal da escadaria da entrada fica LIVRE: a escada e as muretas sao do sg_entry)


# ------------------------------------------------------------------ 3) bordas dos patamares
def edge_runs(nm, poly, z, step=1.0):
    """trechos de borda do patamar (mesma leitura do sg_col.edge_guards): cls 'terrace' (patamar mais baixo do lado de
    fora) ou 'wild'; aberto (escada/ponte/agua); cas (muralha/torres do castelo: o terreno nao veste)"""
    pts = clean(ccw(poly))
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.3:
            continue
        ux, uy = dx / ln, dy / ln
        nx, ny = uy, -ux
        ns = max(1, int(round(ln / step)))
        keys = []
        for k in range(ns):
            t = (k + 0.5) * ln / ns
            x, y = a[0] + ux * t, a[1] + uy * t
            key = None
            if L.floor_name(x - nx * 0.6, y - ny * 0.6) == nm:
                ox, oy = x + nx * 1.6, y + ny * 1.6
                zo = L.zone_of(ox, oy)
                cls = None
                if zo is None:
                    cls, zo = "wild", wild_z(ox, oy)
                elif zo < z - 2.3:
                    cls = "terrace"
                if cls:
                    br = bool(sg_col.opening(ox, oy))            # escada / ponte: borda aberta, sem arremate
                    opn = bool(br or water_gap(x, y) or village_parapet(nm, x, y))
                    cas = castle_hit(x + nx * 1.2, y + ny * 1.2) or castle_hit(x - nx * 1.0, y - ny * 1.0)
                    key = (cls, round(zo, 2), opn, cas, br)
            keys.append(key)
        k = 0
        while k < ns:
            key = keys[k]
            j = k
            while j + 1 < ns and keys[j + 1] == key:
                j += 1
            if key is not None:
                out.append(dict(i=i, a=a, u=(ux, uy), n=(nx, ny), t0=k * ln / ns, t1=(j + 1) * ln / ns, ln=ln,
                                cls=key[0], zo=key[1], open=key[2], cas=key[3], br=key[4]))
            k = j + 1
    return out


def _W(R):
    return (R["a"], R["u"], R["n"])


def _xy(R, t, d):
    a, u, n = R["a"], R["u"], R["n"]
    return a[0] + u[0] * t + n[0] * d, a[1] + u[1] * t + n[1] * d


def course_heights(H, hs=COURSES13):
    if H < hs[0] + 0.4:
        return [H]
    n = max(1, int(round(H / (hs[0] + hs[1]) * 2.0)))
    seq = [hs[k % 2] for k in range(n)]
    sc = H / sum(seq)
    return [h * sc for h in seq]


NICHE_POLYS = []    # pegadas dos nichos do arrimo (a alvenaria e o soco saltam; arremate e misulas continuam)


def niche_hit(x, y):
    return any(L.point_in_poly(x, y, p) for p in NICHE_POLYS)


def free_spans(R, t0, t1, d=0.3, pad=0.6, step=0.5, niches=False):
    """trechos de t0..t1 sem escada (e sem nicho, se niches)"""
    out, cur = [], None
    t = t0
    while t <= t1 + 1e-6:
        x, y = _xy(R, t, d)
        ok = not stair_hit(x, y, pad=pad) and not (niches and niche_hit(x, y))
        if ok and cur is None:
            cur = t
        if not ok and cur is not None:
            if t - step - cur > 0.8:
                out.append((cur, t - step))
            cur = None
        t += step
    if cur is not None and t1 - cur > 0.8:
        out.append((cur, t1))
    return out


def masonry(mb, R, z0, z1, depth=0.45, m=BLOCK, t0=None, t1=None):
    """alvenaria de arrimo (Tier B, 13.05): fiadas de 2 alturas alternadas, blocos chanfrados de comprimento de CICLO
    FIXO (juntas desencontradas), fiada baixa 0,07 mais recuada; junta de 0,1 mostra o nucleo escuro"""
    W = _W(R)
    t0 = R["t0"] if t0 is None else t0
    t1 = R["t1"] if t1 is None else t1
    H = z1 - z0
    if H < 0.5 or t1 - t0 < 0.8:
        return
    zc = z0
    for c, hc in enumerate(course_heights(H)):
        tall = c % 2 == 0
        lens = LEN_TALL if tall else LEN_LOW
        dep = depth if tall else depth - 0.07
        for s0, s1 in free_spans(R, t0, t1, niches=True):
            k = (c * 3 + int(s0)) % 4
            pos = s0 - (0.0 if tall else lens[k] * 0.45)
            while pos < s1 - 0.05:
                bl = lens[k % 4]
                k += 1
                if s1 - (pos + bl) < 0.9:
                    bl = s1 - pos
                p0, p1 = max(pos, s0), min(pos + bl, s1)
                pos += bl
                if p1 - p0 < 0.5:
                    continue
                block(mb, W, p0 + 0.05, p1 - 0.05, zc + 0.05, zc + hc - 0.05, -0.06, dep, 0.09, m)
        zc += hc


def band_face(mb, R, z0, z1, depth=0.45, m=BLOCK):
    """faixa de alvenaria de FUNDO (Tier C): um perfil so, com as juntas de fiada em sulco"""
    if z1 - z0 < 0.5:
        return
    hs = course_heights(z1 - z0)
    prof = [(-0.06, z0), (depth, z0)]
    zc = z0
    for h in hs[:-1]:
        zc += h
        prof += [(depth, zc - 0.1), (depth - 0.17, zc), (depth, zc + 0.1)]
    prof += [(depth, z1), (-0.06, z1)]
    for s0, s1 in free_spans(R, R["t0"], R["t1"]):
        ledge(mb, _W(R), s0, s1, prof, m)


def coping(mb, R, z, w=1.3, h=0.7, ext=(0.1, 0.1)):
    """arremate da crista em perfil (TrimLow): aresta de fora chanfrada e pingadeira; topo 0,05 abaixo da cota"""
    prof = [(0.0, z - h), (w - 0.14, z - h), (w - 0.14, z - h + 0.12), (w, z - h + 0.2), (w, z - 0.22),
            (w - 0.17, z - 0.05), (0.0, z - 0.05)]
    for s0, s1 in free_spans(R, R["t0"] - ext[0], R["t1"] + ext[1], d=0.5, pad=0.2):
        ledge(mb, _W(R), s0, s1, prof, CAPL)


PAR_TOP = 1.72                      # topo do corpo do parapeito (acima da cota); capa ate +2,02
CAP_LEN = (3.8, 3.2)
SLAB_LEN = (3.8, 4.4)


def parapet(mb, R, z, ext=(0.0, 0.0)):
    """parapeito das bordas (Tier B, 13.06) sobre a guarda invisivel do sg_col: corpo com PLINTO na face interna,
    LAJES em relevo, capa em PECAS com junta e aresta interna chanfrada"""
    a, t0, t1 = R["a"], R["t0"], R["t1"]
    if t1 - t0 < 1.0:
        return
    W = _W(R)
    body = [(-0.36, z - 0.2), (0.95, z - 0.2), (0.95, z + PAR_TOP), (0.05, z + PAR_TOP), (0.05, z + 0.6),
            (-0.36, z + 0.44)]
    ledge(mb, W, t0 - ext[0], t1 + ext[1], body, PAR_M)
    k = int(abs(a[0] * 7.0 + a[1] * 3.0)) % 2
    pos = t0 + 0.12
    while pos < t1 - 0.4:
        bl = SLAB_LEN[k % 2]
        k += 1
        if t1 - 0.12 - (pos + bl) < 1.2:
            bl = t1 - 0.12 - pos
        block(mb, W, pos + 0.04, pos + bl - 0.04, z + 0.66, z + PAR_TOP - 0.1, 0.06, -0.02, 0.07, REL_M)
        pos += bl
    zc = z + PAR_TOP
    cap = [(-0.22, zc), (1.17, zc), (1.17, zc + 0.3), (-0.07, zc + 0.3)]
    k = int(abs(a[0] * 3.0 + a[1] * 7.0)) % 2
    pos = t0
    while pos < t1 - 0.05:
        bl = CAP_LEN[k % 2]
        k += 1
        if t1 - (pos + bl) < 1.2:
            bl = t1 - pos
        ledge(mb, W, pos + (0.03 if pos > t0 else 0.0), pos + bl - (0.03 if pos + bl < t1 - 1e-6 else 0.0), cap, CAPL)
        pos += bl


def post_blocked(x, y):
    """pilarete de ponta livre nao nasce colado na calcada da entrada nem na boca de uma ponte (ali o parapeito e do
    sg_entry / do modulo da ponte)"""
    hx0, hy0, hx1, hy1 = L.ENTRY_HIGH
    if hx0 - 3.0 < x < hx1 + 3.0 and hy0 - 3.0 < y < max(hy1, -270.0) + 3.0:
        return True
    for nm, a, b, z, w in BRIDGES:
        if sg_col._in_rect_along(x, y, a, b, w / 2 + 3.0, pad=3.0):
            return True
    return False


def village_parapet(nm, x, y):
    """trechos de borda onde a VILA poe o parapeito dela (sg_village.stairs_p1p2: muretas de |x| 10 a 21 na borda do
    P2 sobre a escada P1P2): o terreno faz so a alvenaria, o arremate e as misulas"""
    foot, deg, w, n, tread, g = L.stair_frame("P1P2")
    return nm == "P2" and abs(y - (foot[1] + tread * n)) < 1.0 and abs(x) < w / 2 + 12.6


def corner_stone(mb, x, y, ang, z):
    """pedra de canto sobre a emenda de dois trechos de parapeito (0,04 acima das capas: nada coplanar)"""
    mb.box((1.62, 1.62, 0.36), (x, y, z + PAR_TOP + 0.17 + 0.04), (0, 0, ang), CAPL, 0.06)


# FINESSE 3 (03.05 / 02.06): ritmo A-B do arrimo P1->P2 em posicoes DIRIGIDAS (x): contraforte LARGO nos nos (flancos
# da escada e meio dos tramos), ESTREITO nos tramos; 2 acontecimentos de cada lado da escada: nicho com banco (perto da
# praca) e nicho-fonte (bebedouro de parede) no meio do tramo. Nos outros muros de arrimo (curtos) vale o passo generico.
ARR_WIDE = (25.0, 124.0)
ARR_NARROW = (50.0, 74.0, 98.0, 146.0, 166.0)
ARR_NICHES = ((37.0, "bench"), (86.0, "trough"))


def _is_arrimo(R):
    return abs(R["u"][1]) < 0.05 and abs(R["a"][1] - L.P2_POLY[0][1]) < 0.3


def buttress_ts(R, spacing=17.0):
    """[(t, largo?)] dos contrafortes do run"""
    t0, t1 = R["t0"], R["t1"]
    out = []

    def ok(t, half):
        for dt in (-half - 1.0, 0.0, half + 1.0):
            for dd in (0.5, 2.6, 4.0):
                x, y = _xy(R, t + dt, dd)
                if stair_hit(x, y, pad=2.5) or water_gap(x, y) or castle_hit(x, y):
                    return False
        return True
    if _is_arrimo(R):
        ux = R["u"][0]
        for xs, wide in ((ARR_WIDE, True), (ARR_NARROW, False)):
            for x in xs:
                for sgn in (-1, 1):
                    t = (sgn * x - R["a"][0]) / ux
                    half = 2.3 if wide else 1.2
                    if t0 + half + 0.8 < t < t1 - half - 0.8 and ok(t, half):
                        out.append((t, wide))
        return sorted(out)
    L_ = t1 - t0
    nb = int(L_ / spacing)
    if nb < 1:
        return out
    sp = L_ / nb
    for k in range(nb):
        t = t0 + sp * (k + 0.5)
        if ok(t, 1.55):
            out.append((t, k % 2 == 0))
    return out


def buttresses(mb, R, z0, z1, ts=None):
    """contrafortes com TALUDE (13.05): soco em perfil, corpo com o degrau inclinado e capa no talude; colisao propria.
    Largo (half 2,3; sai 2,45) nos nos, estreito (half 1,2; sai 1,9) nos tramos"""
    ts = buttress_ts(R) if ts is None else ts
    W = _W(R)
    for t, wide in ts:
        half = 2.3 if wide else 1.2
        dep = 2.45 if wide else 1.9
        h1 = (z1 - z0) - 1.9
        zA = z0 + h1 - (1.2 if wide else 0.8)
        body = [(-0.05, z0 + 0.5), (dep, z0 + 0.5), (dep, zA), (dep - 1.0, zA + 1.25), (dep - 1.0, z1), (-0.05, z1)]
        ledge(mb, W, t - half, t + half, body, BLOCK)
        cap = [(dep - 1.0, zA + 1.18), (dep + 0.17, zA - 0.2), (dep + 0.17, zA + 0.06), (dep - 1.0, zA + 1.5)]
        ledge(mb, W, t - half - 0.11, t + half + 0.11, cap, CAPL)
        soc = [(-0.05, z0 - 0.2), (dep + 0.35, z0 - 0.2), (dep + 0.35, z0 + 0.3), (dep + 0.1, z0 + 0.55),
               (-0.05, z0 + 0.55)]
        ledge(mb, W, t - half - 0.2, t + half + 0.2, soc, CAPL)
        cx, cy = _xy(R, t, dep / 2)
        col_box("SG_TerButtress", (2 * half + 0.6, dep, z1 - z0 + 0.05), (cx, cy, (z0 + z1) / 2),
                (0, 0, math.atan2(R["u"][1], R["u"][0])))
    return ts


def niche(mb, R, t, kind, z0, z1):
    """nicho no arrimo (02.06 / 03.05): vao de 4,4 (banco) ou 3,6 (bebedouro) recuado 1,6 na parede, com ombreiras de
    cantaria, arco de 2 centros (flecha 0,62 do vao, abaixo da mesa de misulas) com chave e piso de laje; dentro: banco
    de pedra ou bacia de parede com bica em misula. O vao fica dentro da colisao do patamar (o jogador ve, nao entra)."""
    W = _W(R)
    wd = 4.4 if kind == "bench" else 3.6
    dep = 1.6
    ya, yb = t - wd / 2, t + wd / 2
    zf = z0 + 0.1                                  # piso do nicho
    zs = z0 + (1.5 if kind == "bench" else 2.0)    # nascenca do arco
    rise = 0.62 * wd
    zt = zs + rise
    NICHE_POLYS.append(ccw([_xy(R, ya - 0.6, -dep - 0.3), _xy(R, yb + 0.6, -dep - 0.3), _xy(R, yb + 0.6, 0.9),
                            _xy(R, ya - 0.6, 0.9)]))
    bm = mb.bm
    ang = math.atan2(W[1][1], W[1][0])

    def V(u, d, z):
        return bm.verts.new(_P(W, u, d, z))
    # caixa do vao (fundo e 2 lados), faces viradas para DENTRO do nicho (para quem olha de fora)
    fback = bm.faces.new([V(ya, -dep, zf), V(yb, -dep, zf), V(yb, -dep, zt + 0.7), V(ya, -dep, zt + 0.7)])
    fa = bm.faces.new([V(ya, -dep, zf), V(ya, -dep, zt + 0.7), V(ya, 0.5, zt + 0.7), V(ya, 0.5, zf)])
    fb = bm.faces.new([V(yb, -dep, zf), V(yb, 0.5, zf), V(yb, 0.5, zt + 0.7), V(yb, -dep, zt + 0.7)])
    mb._post([v for f in (fback, fa, fb) for v in f.verts], REL_M, None, 0, 1)      # interior CLARO (le de longe)
    for f, want in ((fback, (W[2][0], W[2][1])), (fa, (W[1][0], W[1][1])), (fb, (-W[1][0], -W[1][1]))):
        f.normal_update()
        if f.normal.x * want[0] + f.normal.y * want[1] < 0:
            f.normal_flip()
    # piso de laje clara, ombreiras e arco de 2 centros com espessura real (0,6) + chave
    mb.box((wd + 0.3, dep + 0.9, 0.3), _P(W, t, -dep / 2 + 0.25, zf - 0.15), (0, 0, ang), CAPL, 0.05)
    for u0, u1 in ((ya - 0.6, ya + 0.02), (yb - 0.02, yb + 0.6)):
        block(mb, W, u0, u1, zf + 0.02, zs + 0.08, -0.1, 0.6, 0.08, CAPL)
    c = (rise * rise - wd * wd / 4.0) / wd                     # centro de cada meio-arco: c alem do pe oposto
    Rr = wd / 2 + c
    nseg = 5
    arc = []
    aL = math.atan2(rise, -c)                                  # angulo do fecho visto do centro esquerdo (t + c)
    for i in range(nseg + 1):                                  # meio-arco ESQUERDO: do pe esquerdo (pi) ao fecho
        a = math.pi - (math.pi - aL) * i / nseg
        arc.append((t + c + Rr * math.cos(a), zs + Rr * math.sin(a)))
    aR = math.atan2(rise, c)                                   # fecho visto do centro direito (t - c)
    for i in range(1, nseg + 1):                               # meio-arco DIREITO: do fecho ao pe direito (0)
        a = aR * (1.0 - i / nseg)
        arc.append((t - c + Rr * math.cos(a), zs + Rr * math.sin(a)))
    arc = _dedupe(arc)
    hi = [(u, zz + 0.6) for u, zz in arc]
    hi[0] = (arc[0][0] - 0.6, hi[0][1])
    hi[-1] = (arc[-1][0] + 0.6, hi[-1][1])
    strip(mb, W, arc, hi, -0.1, 0.6, CAPL)
    block(mb, W, t - 0.42, t + 0.42, zt + 0.45, zt + 1.3, -0.05, 0.7, 0.08, CAPL)
    if kind == "bench":
        # banco de pedra: assento chanfrado sobre 2 pes, encosto baixo no fundo
        mb.box((wd - 0.6, 1.1, 0.3), _P(W, t, -dep + 0.7, zf + 1.5), (0, 0, ang), CAPL, 0.05)
        for u in (t - wd / 2 + 0.7, t + wd / 2 - 0.7):
            mb.box((0.5, 0.95, 1.34), _P(W, u, -dep + 0.7, zf + 0.67), (0, 0, ang), REL_M, 0.04)
        mb.box((wd - 0.6, 0.3, 1.1), _P(W, t, -dep + 0.17, zf + 2.05), (0, 0, ang), CAPL, 0.05)
    else:
        # bebedouro de parede: bacia saindo do fundo com rebordo claro e lamina escura; bica de ferro numa misula
        mb.box((wd - 0.8, 1.2, 1.45), _P(W, t, -dep + 0.65, zf + 0.725), (0, 0, ang), REL_M, 0.06)
        mb.box((wd - 0.6, 1.4, 0.22), _P(W, t, -dep + 0.68, zf + 1.56), (0, 0, ang), CAPL, 0.05)
        mb.box((wd - 1.2, 0.9, 0.1), _P(W, t, -dep + 0.68, zf + 1.52), (0, 0, ang), "Water_SG", 0.0)
        mb.box((0.8, 0.6, 0.7), _P(W, t, -dep + 0.32, zf + 3.1), (0, 0, ang), CAPL, 0.06)
        mb.cyl(0.11, 0.7, _P(W, t, -dep + 0.7, zf + 3.0), (math.pi / 2, 0, ang), "Metal_SG_Iron", 6, bevel=0.0)


def corbels(mb, R, z, ts=(), half=1.75):
    """mesa de MISULAS com ARQUINHOS sob o arremate, por vao entre contrafortes (o ritmo quebra a cada contraforte)"""
    W = _W(R)
    zc = z - 0.7
    zb = zc - 1.3
    prof = [(0.0, zb), (0.6, zb), (0.6, zb + 0.28), (1.12, zb + 0.82), (1.12, zc), (0.0, zc)]
    edges = [R["t0"] + 0.4] + [e for t, wide in sorted(ts) for e in (t - (2.3 if wide else 1.2) - 0.3,
                                                                     t + (2.3 if wide else 1.2) + 0.3)] + [R["t1"] - 0.4]
    for b0, b1 in zip(edges[0::2], edges[1::2]):
        L_ = b1 - b0
        if L_ < 1.2:
            continue
        n = max(1, int(round(L_ / 3.8)))
        tsc = [b0 + L_ * k / n for k in range(n + 1)]
        tsc = [t for t in tsc if not stair_hit(*_xy(R, t, 0.5), pad=0.4)]
        for t in tsc:
            ledge(mb, W, t - 0.34, t + 0.34, prof, CAPL)
        for ta, tb in zip(tsc, tsc[1:]):
            u0, u1 = ta + 0.34, tb - 0.34
            if u1 - u0 < 0.8 or tb - ta > 5.0:
                continue
            zs = zc - 0.95
            rise = min(0.62, (u1 - u0) * 0.4)
            lo = [(u0 + (u1 - u0) * i / 3.0, zs + rise * math.sin(math.pi * i / 3.0)) for i in range(4)]
            hi = [(uu, zc) for uu, _ in lo]
            strip(mb, W, lo, hi, 0.84, 1.1, CAPL)


def column(mb, cx, cy, r, zt, zb, rot=0.0, m=ROCK, cap=TOP, band=None, strata=None, low=None, tip=0.0,
           taper=1.0, n=6):
    """prisma de basalto (hexagonal): topo em zt (cap), faixa de topo band=(esp, mat), estrato strata=(z, fator, (dx,
    dy)) com 'low' abaixo, ponta pendente tip. Malha fechada."""
    bm = mb.bm

    def ring(rr, z, ox=0.0, oy=0.0):
        return [bm.verts.new((cx + ox + rr * math.cos(rot + 2 * math.pi * k / n),
                              cy + oy + rr * math.sin(rot + 2 * math.pi * k / n), z)) for k in range(n)]
    seq = [ring(r, zt)]
    mats = []
    zcur = zt
    if band and zt - band[0] > zb + 0.8:
        zcur = zt - band[0]
        seq.append(ring(r, zcur))
        mats.append(band[1])
    if strata and zb + 0.8 < strata[0] < zcur - 0.8:
        zs, fs, (dx, dy) = strata
        seq.append(ring(r, zs))
        mats.append(m)
        seq.append(ring(r * fs, zs, dx, dy))
        mats.append(low or m)
        seq.append(ring(r * fs * taper, zb, dx, dy))
        mats.append(low or m)
    else:
        seq.append(ring(r * taper, zb))
        mats.append(m)
    allv = [v for rg in seq for v in rg]
    top = bm.faces.new(seq[0])
    groups = {}
    for (a, b), mm in zip(zip(seq, seq[1:]), mats):
        for k in range(n):
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last = seq[-1]
    lm = mats[-1]
    if tip > 0:
        lx = sum(v.co.x for v in last) / n
        ly = sum(v.co.y for v in last) / n
        apex = bm.verts.new((lx, ly, zb - tip))
        allv.append(apex)
        for k in range(n):
            groups.setdefault(lm, []).append(bm.faces.new((last[(k + 1) % n], last[k], apex)))
    else:
        groups.setdefault(lm, []).append(bm.faces.new(list(reversed(last))))
    _faces_ok(mb, [top] + [f for fs_ in groups.values() for f in fs_])      # malha fechada: normais para fora
    mb._post(allv, m, None, 0, 1)
    top.material_index = mb._mi_for(cap)
    for mm, fs_ in groups.items():
        if mm != m:
            mi = mb._mi_for(mm)
            for f in fs_:
                f.material_index = mi


def rock_base(mb, R, zb, ztop):
    """base de basalto (13.07) em MACICOS de 3-5 colunas com vao entre eles; topo alterna POR MACICO"""
    a, t0, t1 = R["a"], R["t0"], R["t1"]
    NS = (3, 4, 3, 4)
    GAPS = (10.0, 12.0, 8.5)
    g = int(abs(a[0] * 5.0 + a[1] * 11.0)) % 4
    t = t0 + 2.4
    while t < t1 - 2.0:
        n = NS[g % 4]
        span = 3.3 * (n - 1)
        if t + span > t1 - 1.2:
            n = max(1, int((t1 - 1.2 - t) / 3.3) + 1)
            span = 3.3 * (n - 1)
        grass = g % 2 == 0
        for j in range(n):
            c = (j - (n - 1) / 2.0) / max(1.0, (n - 1) / 2.0)
            r = 3.0 - 0.6 * abs(c)
            d = r * (0.9 - 0.25 * abs(c)) + (0.5 if j % 2 else 0.0)
            tt = t + 3.3 * j
            cx, cy = _xy(R, tt, d)
            zt = ztop + 1.4 - 2.6 * abs(c) - (0.5 if j % 2 else 0.0)
            cx, cy, zt = water_fix(cx, cy, r, zt)
            zt = cap_top(cx, cy, r, zt)
            if zt < zb + 1.0 or not dun_ok(cx, cy, r, zb - 1.4, zt) or castle_hit(cx, cy, r):
                continue
            column(mb, cx, cy, r, zt, zb - 1.4 - 0.19 * ((j + g) % 3), 0.35 * j + 0.2 * g, m=ROCK,
                   cap=GRASS if grass else TOP)
        t += span + GAPS[g % 3] + 3.0
        g += 1


def quoins(mb, poly, runs, z):
    """cunhais nas quinas CONVEXAS: entre patamares pedras alternadas longa/curta; no terreno bravo um pilar so"""
    pts = clean(ccw(poly))
    n = len(pts)
    ends = {}
    for R in runs:
        if R["t0"] < 0.6:
            ends.setdefault(R["i"], []).append(("start", R))
        if R["t1"] > R["ln"] - 0.6:
            ends.setdefault((R["i"] + 1) % n, []).append(("end", R))
    for vi, lst in ends.items():
        starts = [R for k, R in lst if k == "start"]
        endsr = [R for k, R in lst if k == "end"]
        if not starts or not endsr:
            continue
        Rs, Re = starts[0], endsr[0]
        cross = Re["u"][0] * Rs["u"][1] - Re["u"][1] * Rs["u"][0]
        if cross <= 0.05:
            continue
        v = pts[vi]
        nx, ny = Re["n"][0] + Rs["n"][0], Re["n"][1] + Rs["n"][1]
        ln = math.hypot(nx, ny) or 1.0
        cx, cy = v[0] + nx / ln * 0.75, v[1] + ny / ln * 0.75
        if castle_hit(cx, cy, 1.5):
            continue
        z0 = min(Rs["zo"], Re["zo"]) - (0.3 if min(Rs["zo"], Re["zo"]) >= SH - 0.1 else 0.0)
        ang = math.atan2(Rs["u"][1], Rs["u"][0])
        if Rs["cls"] == "terrace" and Re["cls"] == "terrace":
            zc = z0
            for c, hc in enumerate(course_heights(z - 0.75 - z0)):
                sx, sy = (2.3, 1.5) if c % 2 == 0 else (1.5, 2.3)
                mb.box((sx, sy, hc - 0.1), (cx, cy, zc + hc / 2), (0, 0, ang), CAPL, 0.07)
                zc += hc
        else:
            mb.box((1.9, 1.9, z - 0.75 - z0), (cx, cy, (z0 + z - 0.75) / 2), (0, 0, ang), CAPL, 0)


def terrace_edges():
    npost = nstone = 0
    for nm, poly, z, pr in L.floors():
        if nm not in ("P1", "P2", "P3"):
            continue
        mb = smb("SG_Ter_Wall_" + nm, detail="near")
        mr = smb("SG_Ter_Terrace_" + nm)
        runs = edge_runs(nm, poly, z)
        runs = [R for R in runs if not R["cas"]]        # F3: a muralha / torres do castelo vestem esses trechos
        pars = []
        for R in runs:
            zo = R["zo"]
            if R["cls"] == "terrace":
                top = z - 0.7
                ts = buttress_ts(R)
                if _is_arrimo(R):
                    for x, kind in ARR_NICHES:
                        for sgn in (-1, 1):
                            t = (sgn * x - R["a"][0]) / R["u"][0]
                            if R["t0"] + 4.0 < t < R["t1"] - 4.0 and not any(abs(t - tb) < 4.5 for tb, w_ in ts):
                                niche(mb, R, t, kind, zo, top)
                masonry(mb, R, zo + 0.55, top)
                if not R["br"]:
                    coping(mb, R, z)
                corbels(mb, R, z, ts)
                if not R["open"]:
                    pars.append(R)
                buttresses(mb, R, zo, top, ts=ts)
                soc = [(-0.02, zo - 0.2), (0.75, zo - 0.2), (0.75, zo + 0.3), (0.55, zo + 0.55), (-0.02, zo + 0.55)]
                for s0, s1 in free_spans(R, R["t0"], R["t1"], d=0.4, pad=0.3, niches=True):
                    ledge(mb, _W(R), s0, s1, soc, CAPL)
            else:
                drop = z - zo
                ztb = z - 0.05 if R["br"] else z - 0.7  # boca de ponte/escada: sem arremate, a faixa sobe ate o topo
                if drop <= 3.0:                      # P1: meio-fio sobre o ombro
                    band_face(mb, R, zo - 0.4, ztb)
                else:                                # P2/P3: base de rocha + faixa de alvenaria
                    band = 7.6 if drop > 12.0 else 4.4
                    band_face(mb, R, z - band, ztb)
                    # FINESSE 3 (14.01): onde a coroa do penhasco sobe ate perto do patamar, os macicos de basalto
                    # ficariam enterrados nela: nao nascem (a rocha da coroa e a base)
                    mx, my = _xy(R, (R["t0"] + R["t1"]) / 2, 3.0)
                    if crown_design(mx, my) < z - band - 0.5:
                        rock_base(mr, R, zo, z - band + 1.2)
                if not R["br"]:
                    coping(mb, R, z)
                if not R["open"]:
                    pars.append(R)
        P = [(R, _xy(R, R["t0"], 0.0), _xy(R, R["t1"], 0.0)) for R in pars]

        def joined(p, me):
            for R2, s, e in P:
                if R2 is me:
                    continue
                for q in (s, e):
                    if math.hypot(p[0] - q[0], p[1] - q[1]) < 0.35:
                        return R2
            return None
        for R, s, e in P:
            js, je = joined(s, R), joined(e, R)
            parapet(mb, R, z, ext=(0.7 if js else 0.0, 0.7 if je else 0.0))
            for p, other, t_end, sgn in ((s, js, R["t0"], 1.0), (e, je, R["t1"], -1.0)):
                if other is not None:
                    if sgn < 0:
                        bis = math.atan2(R["u"][1] + other["u"][1], R["u"][0] + other["u"][0])
                        cx, cy = _xy(R, t_end, 0.47)
                        ox, oy = _xy(other, other["t0"], 0.47)
                        corner_stone(mb, (cx + ox) / 2, (cy + oy) / 2, bis, z)
                        nstone += 1
                elif R["t1"] - R["t0"] > 2.4:
                    ex, ey = _xy(R, t_end - sgn * 1.5, 0.5)
                    px, py = _xy(R, t_end + sgn * 0.98, 0.47)
                    if castle_hit(ex, ey, r=1.5) or post_blocked(px, py):
                        continue
                    post(mb, px, py, z + 0.07)
                    npost += 1
        quoins(mb, poly, runs, z)
    print("TER BORDAS pilaretes=%d pedras_de_canto=%d" % (npost, nstone))


# ------------------------------------------------------------------ entrada: espinha baixa + meio-fios
def neck():
    """terreno bravo do pescoco da entrada: duas faixas de grama/rocha MAIS BAIXAS que a calcada (26,2 ao lado do
    patio baixo, subindo com a escadaria ate 34,2) e os meio-fios do patio e da calcada. A face de fora e o fundo sao
    da casca (keel), aqui so o topo e a face de dentro."""
    me = smb("SG_Ter_Terrace_Entry")
    ys = [p[1] for p in RIM]
    ymin = min(ys)
    rows = []
    y = ymin + 0.4
    while y < CUT_Y - 0.01:
        rows.append(y)
        y += 2.0
    rows += [STAIR_Y0 - 0.05, STAIR_Y0 + 0.05, CUT_Y]
    rows = sorted(set(round(v, 3) for v in rows if ymin + 0.3 <= v <= CUT_Y))
    for s in (-1, 1):
        ring_rows = []
        for y in rows:
            iv = SL.x_intervals(RIM, y)
            if not iv:
                continue
            xs = [x for pr in iv for x in pr]
            xo = min(xs) if s < 0 else max(xs)
            xi = s * (PATIO_LOW[2] if y <= STAIR_Y0 else NECK_STAIR_X)
            if abs(xo) - abs(xi) < 0.6:
                continue
            ring_rows.append((y, xi, xo, neck_z(y)))
        bm = me.bm
        rings = []
        for y, xi, xo, zt in ring_rows:
            rings.append([bm.verts.new((xi, y, zt)), bm.verts.new((xo, y, zt)), bm.verts.new((xo, y, 23.0)),
                          bm.verts.new((xi, y, 23.0))])
        if len(rings) < 2:
            continue
        tops_, inner = [], []
        for r0, r1 in zip(rings, rings[1:]):
            tops_.append(bm.faces.new((r0[0], r0[1], r1[1], r1[0])))
            inner.append(bm.faces.new((r0[3], r0[0], r1[0], r1[3])))     # face de dentro (para o canal)
        for f in tops_ + inner:
            f.normal_update()
        for f in tops_:
            if f.normal.z < 0:
                f.normal_flip()
        for f in inner:
            if f.normal.x * s > 0:
                f.normal_flip()
        me._post([v for rg in rings for v in rg], DARK, None, 0, 1)
        mi = me._mi(GRASS)
        for f in tops_:
            f.material_index = mi
    x0, y0, x1, y1 = PATIO_LOW
    for s in (-1, 1):
        xe = x1 if s > 0 else x0
        a = (xe, y0) if s > 0 else (xe, y1)
        u = (0.0, 1.0) if s > 0 else (0.0, -1.0)
        R = dict(a=a, u=u, n=(u[1], -u[0]), t0=0.0, t1=y1 - y0)
        masonry(me, R, NECK_LOW - 0.4, DECK - 0.35)
    # face sul do patio: so fora do tabuleiro da ponte (sob ele a face e do sg_entry)
    R = dict(a=(x0, y0), u=(1.0, 0.0), n=(0.0, -1.0), t0=0.0, t1=x1 - x0)
    masonry(me, R, 25.6, DECK - 0.35, t0=0.0, t1=UNDER_BRIDGE[0] - x0 - 0.2)
    masonry(me, R, 25.6, DECK - 0.35, t0=UNDER_BRIDGE[2] - x0 + 0.2, t1=x1 - x0)
    hx0, hy0, hx1, hy1 = L.ENTRY_HIGH
    yend = max(hy0 + 1.0, -272.0)                        # a calcada entra no P1 em y -272
    for s in (-1, 1):
        xe = hx1 if s > 0 else hx0
        a = (xe, hy0) if s > 0 else (xe, yend)
        u = (0.0, 1.0) if s > 0 else (0.0, -1.0)
        R = dict(a=a, u=u, n=(u[1], -u[0]), t0=0.0, t1=yend - hy0)
        masonry(me, R, SH - 0.4, P1 - 0.35)


# ------------------------------------------------------------------ 4) coroa do penhasco (Tier C)
def prom_w(x, y):
    w = 0.0
    for px, py, hw in PROMS:
        w = max(w, 1.0 - math.hypot(x - px, y - py) / hw)
    return min(1.0, max(0.0, w) * 1.6)


def mirante_w(x, y):
    px, py, hw = PROMS[MIRANTE_PROM]
    return max(0.0, 1.0 - math.hypot(x - px, y - py) / hw)


RIM_FACE = {}


def crown_design(x, y):
    """FINESSE 3 (14.01): cota DESENHADA do topo da coroa num ponto do contorno: baixa sob a vila (P1), subindo nos
    flancos (P2) e alta sob o castelo (ate P3 - 2,7): a ilha deixa de ler como prato com a falesia da mesma altura"""
    base = wild_z(x, y)
    if y < CUT_Y:
        return base + 0.6
    if y < -150.0:
        h = 0.8
    elif y < -18.0:
        h = 0.8 + (y + 150.0) / 132.0 * 5.2                  # 0,8 -> 6,0 (T <= 41 < P2 - 2,8)
    else:
        h = 6.0 + min(1.0, (y + 18.0) / 110.0) * 9.3         # 6 -> 15,3 (T = 49,5 = P3 - 2,7)
    return base + h


COL_W = (6.2, 4.2, 8.0, 5.0, 8.8, 3.8, 6.8)              # larguras DIRIGIDAS das colunas da coroa (ciclo 7)
COL_D = (0.0, -1.2, 0.7, -0.5, 1.4, -0.9)                # recuo (-) / saliencia (+) por coluna (ciclo 6): >= 0,9 entre vizinhas
COL_T = (0.0, -1.5, 0.9, -2.4, 0.4, -1.0, -0.6, 1.2)     # degrau do topo por coluna (ciclo 8)
_KC = [0, 0, 0]


def split_cols(W):
    """larguras das colunas de um bloco de W studs (ciclo COL_W, escalado para fechar em W)"""
    ws = []
    while sum(ws) < W - 0.5:
        ws.append(COL_W[_KC[0] % 7])
        _KC[0] += 1
    sc = W / sum(ws)
    return [w * sc for w in ws]


def block_cols(mb, cols, inner, T_in, z0, apex, cap, end_mat=ROCK):
    """bloco da coroa (14.02) em GRUPO DE COLUNAS: cada coluna tem o seu recuo (retorno real na divisa) e o seu topo;
    o topo e uma PRATELEIRA de 2,0 (cota da coluna) que desce/sobe em rampa ate a linha interna (T_in); face externa
    com a faixa clara de topo (1,2), o ESTRATO de 20 (rebordo recuado 1,1 com a mesa clara) e o ESTRATO de 6 em
    SALIENCIA (bojo de 1,3 com a mesa clara em cima e a barriga escura embaixo); fecha em ponta (apex). As costas
    (lado da ilha) nao tem face. cols = [((xa, ya), (xb, yb), (nx, ny), T)], inner = [(x, y)] (len(cols) + 1)."""
    bm = mb.bm
    nc = len(cols)
    if nc < 1:
        return
    # orientacao: o contorno O + [I_fim, I_inicio] tem de ser anti-horario (normais para fora)
    O = [(c[0], c[1]) for c in cols]
    poly = [p for pr in O for p in pr] + [inner[-1], inner[0]]
    if SL.area(poly) < 0:
        cols = [((c[1], c[0]), c[2], c[3]) for c in reversed(cols)]
        cols = [(c[0][0], c[0][1], c[1], c[2]) for c in cols]
        inner = list(reversed(inner))
    Tmin = min(c[3] for c in cols)
    # aneis de baixo: (inset, z (None = por coluna, T - 1,2), material da faixa ACIMA deste anel)
    seq = [(0.0, None, TOP)]
    ins = 0.0
    if z0 + 1.0 < ZS_A < Tmin - 2.5:
        seq += [(0.0, ZS_A, ROCK), (1.1, ZS_A, TOP)]
        ins = 1.1
    zlim = (ZS_A - 1.0) if ins > 0 else (Tmin - 2.5)
    if z0 + 1.0 < ZS_B - 3.2 and ZS_B + 1.6 < zlim:
        seq += [(ins, ZS_B + 1.6, ROCK), (ins - 1.3, ZS_B + 1.1, TOP), (ins + 0.2, ZS_B - 3.0, ROCK)]
        ins += 0.2
        seq.append((ins, z0, DARK))
    else:
        seq.append((ins, z0, ROCK))
    groups = {}
    allv = []

    def V(x, y, z):
        v = bm.verts.new((x, y, z))
        allv.append(v)
        return v

    def q(f, m):
        groups.setdefault(m, []).append(f)
    # topo: anel externo e prateleira por coluna; linha interna
    OT, ST = [], []
    for (pa, pb, (nx, ny), T) in cols:
        OT.append((V(pa[0], pa[1], T), V(pb[0], pb[1], T)))
        ST.append((V(pa[0] - nx * 2.0, pa[1] - ny * 2.0, T), V(pb[0] - nx * 2.0, pb[1] - ny * 2.0, T)))
    IT = [V(x, y, T_in) for x, y in inner]
    for k in range(nc):
        q(bm.faces.new((OT[k][0], OT[k][1], ST[k][1], ST[k][0])), cap)
        q(bm.faces.new((ST[k][0], ST[k][1], IT[k + 1], IT[k])), cap)
        if k + 1 < nc:
            if abs(cols[k][3] - cols[k + 1][3]) > 0.05:                    # retorno no degrau do topo
                q(bm.faces.new((OT[k][1], OT[k + 1][0], ST[k + 1][0], ST[k][1])), cap)
            if (ST[k][1].co - ST[k + 1][0].co).length > 0.02:
                q(bm.faces.new((ST[k][1], ST[k + 1][0], IT[k + 1])), cap)
    # faces externas: faixas entre aneis (por segmento de coluna e retornos nas divisas)
    rings = [[OT[k][j] for k in range(nc) for j in (0, 1)]]
    zs_rings = [None]
    for ins_j, zj, mj in seq:
        rg = []
        for (pa, pb, (nx, ny), T) in cols:
            zz = (T - 1.2) if zj is None else zj
            rg.append(V(pa[0] - nx * ins_j, pa[1] - ny * ins_j, zz))
            rg.append(V(pb[0] - nx * ins_j, pb[1] - ny * ins_j, zz))
        rings.append(rg)
        zs_rings.append(zj)
    mats = [m for _, _, m in seq]
    n = 2 * nc
    for (ra, rb), mm in zip(zip(rings, rings[1:]), mats):
        for k in range(n - 1):
            if (ra[k + 1].co - ra[k].co).length < 0.02 and (rb[k + 1].co - rb[k].co).length < 0.02:
                continue                                                   # retorno nulo (bloco plano)
            q(bm.faces.new((ra[k + 1], ra[k], rb[k], rb[k + 1])), mm)
    # faces de TOPO (fim) do bloco: poligonos verticais no plano da normal, da prateleira ate o ultimo anel
    for end, oi, ii, sgn in ((0, 0, 0, -1.0), (1, n - 1, nc, 1.0)):
        c = cols[0] if end == 0 else cols[-1]
        nx, ny = c[2]
        T = c[3]
        ix, iy = inner[ii]
        pts = [rings[0][oi], ST[0][0] if end == 0 else ST[-1][1], IT[ii]]
        zprev = T_in
        inner_vs = []
        for (ins_j, zj, mj), rg in zip(seq, rings[1:]):
            zz = (T - 1.2) if zj is None else zj
            zz = min(zz, zprev - 0.01)
            inner_vs.append(V(ix, iy, zz))
            zprev = zz
        pts += inner_vs + [rings[j][oi] for j in range(len(rings) - 1, 0, -1)]
        f = bm.faces.new(pts)
        f.normal_update()
        ux, uy = -ny * sgn, nx * sgn        # direcao do contorno (anti-horario) * sinal da ponta
        if f.normal.x * ux + f.normal.y * uy < 0:
            f.normal_flip()
        q(f, end_mat)
        if end == 0:
            I0 = inner_vs[-1]
        else:
            I1 = inner_vs[-1]
    # ponta: leque do ultimo anel (+ as 2 arestas das pontas) ate o apex; a aresta das costas fica aberta
    last = rings[-1]
    av = V(apex[0], apex[1], apex[2])
    for k in range(n - 1):
        if (last[k + 1].co - last[k].co).length < 0.02:
            continue
        q(bm.faces.new((last[k + 1], last[k], av)), DARK)
    q(bm.faces.new((I1, last[n - 1], av)), DARK)
    q(bm.faces.new((last[0], I0, av)), DARK)
    mb._post(allv, ROCK, None, 0, 1)
    for mm, fs in groups.items():
        if mm != ROCK:
            mi = mb._mi_for(mm)
            for f in fs:
                f.material_index = mi


def zone_dist(x, y, nx, ny, lim=16.0):
    """distancia, para dentro (-normal), ate entrar num patamar (None se nao entra em lim)"""
    d = 0.5
    while d <= lim:
        if L.zone_of(x - nx * d, y - ny * d) is not None:
            return d
        d += 0.5
    return None


def rim_tags(smp):
    tags = []
    for x, y, nx, ny in smp:
        tag = None
        for nm, a, b, z, w in BRIDGES:
            if sg_col._in_rect_along(x, y, a, b, w / 2 + 3.5, pad=6.0):
                tag = ("B", round(z - 2.6, 2))
        for wi, (wx, wy, wz, ux, uy) in enumerate(FALLS):
            lat = abs(-(x - wx) * uy + (y - wy) * ux)
            along = (x - wx) * ux + (y - wy) * uy
            if lat < 6.5 and -9.0 < along < 9.0:
                tag = ("W", wi)
        # FINESSE 3 (pedido do E, 01.07): janela do ENCONTRO da ponte (alas do sg_entry, +-11,8 em y -341,5 abrindo
        # para +-19,5 em y -330, z -13,4..25,7): a coroa nao poe dentes ali (apareciam pelo ultimo arco)
        if y < -328.5 and abs(x) < 21.5:
            tag = ("E", 0)
        tags.append(tag)
    return tags


PAT_T = (0.8, -1.4, 1.6, -0.6, -2.0)
PAT_D = (0.4, -0.5, 0.9, -0.2, -0.9)
PAT_W = (24, 18, 26, 20, 16)


def rim_cliff():
    """coroa do penhasco (14.01 / 14.02, Tier C/B): blocos em GRUPOS DE COLUNAS (larguras, recuos e topos dirigidos),
    2 estratos (rebordo em 20, bojo em 6), cota do topo DESENHADA por setor (crown_design) + PROMONTORIOS (blocos largos
    que avancam, sobem, descem em DEGRAU para o mar e pendem em quilha funda) com pilar destacado so no miolo.
    No JARDIM-MIRANTE o promontorio fica BAIXO no eixo da vista (a moldura sao os macicos de mirante_rock)."""
    RIM_FACE.clear()
    _KC[0] = _KC[1] = _KC[2] = 0
    smp = resample_closed(RIM, 1.0)
    N = len(smp)
    tags = rim_tags(smp)
    i = 0
    nblk = npil = nstep = 0
    prev_t = None
    while i < N - 3:
        pw0 = prom_w(smp[i][0], smp[i][1])
        W = 26 if pw0 > 0.3 else PAT_W[nblk % 5]
        tag = tags[i]
        j = i
        while j < min(N - 1, i + W) and tags[j + 1] == tag:
            j += 1
        W = j - i
        if W < 3 or (tag and tag[0] == "E"):
            i = j + 1
            continue
        mid = smp[i + W // 2]
        base = wild_z(mid[0], mid[1])
        pw = prom_w(mid[0], mid[1])
        mw = mirante_w(mid[0], mid[1])
        pat = nblk % 5
        T = crown_design(mid[0], mid[1])
        if pw > 0.25:
            T += 1.0 + 3.5 * pw
            dout = 1.0 + 2.6 * pw
        else:
            T += PAT_T[pat]
            dout = PAT_D[pat]
        if mw > 0.35:                                   # eixo da vista do mirante: coroa baixa, avancando (balcao)
            T = min(T, base - 2.0)
        if prev_t is not None and abs(T - prev_t) < 1.0:
            T += 1.2 if T >= prev_t else -1.2
        flat = False
        if tag and tag[0] == "B":
            T = min(T, tag[1])
            flat = True
        if tag and tag[0] == "W":
            # face 1,8 ATRAS do labio (a cortina do Roblox desce rente a rocha e bate no degrau), onde quer que o labio
            # esteja em relacao ao contorno
            wx, wy, wz, ux, uy = FALLS[tag[1]]
            T = min(T, wz - 0.5)
            dout = (wx - mid[0]) * mid[2] + (wy - mid[1]) * mid[3] - 1.8
            flat = True
        zd = zone_dist(mid[0], mid[1], mid[2], mid[3])
        depth = 6.5 + 1.0 * pw
        if zd is not None and T > base + 3.0:            # coroa alta: o bloco entra no corpo do patamar (sem fresta)
            depth = max(depth, min(14.0, zd + 1.5))
        # colunas do bloco
        cols = []
        inner = []
        pos = 0.0
        for cw in split_cols(float(W)):
            qa, qb = min(N - 1, i + int(round(pos))), min(N - 1, i + int(round(pos + cw)))
            if qb <= qa:
                pos += cw
                continue
            dk = dout + (0.0 if flat else COL_D[_KC[1] % 6])
            tk = T + (0.0 if flat else COL_T[_KC[2] % 8])
            _KC[1] += 1
            _KC[2] += 1
            xa, ya, nxa, nya = smp[qa]
            xb, yb, nxb, nyb = smp[qb]
            nx, ny = (nxa + nxb), (nya + nyb)
            nl = math.hypot(nx, ny) or 1.0
            nx, ny = nx / nl, ny / nl
            pa = (xa + nxa * dk, ya + nya * dk)
            pb = (xb + nxb * dk, yb + nyb * dk)
            for px, py in (pa, pb):
                z = L.zone_of(px, py)
                if z is not None:
                    tk = min(tk, z - 0.3)
            if not inner:
                inner.append((xa - nxa * (depth - dout), ya - nya * (depth - dout)))
            inner.append((xb - nxb * (depth - dout), yb - nyb * (depth - dout)))
            cols.append((pa, pb, (nx, ny), tk))
            pos += cw
        if len(cols) < 1:
            i = j + 1
            continue
        Ts = [c[3] for c in cols]
        imx = sum(p[0] for p in inner) / len(inner)
        imy = sum(p[1] for p in inner) / len(inner)
        zin = L.zone_of(imx, imy)
        if zin is not None and max(Ts) > base + 3.0:
            T_in = min(zin - 0.5, max(Ts) + 3.0)             # rampa de rocha subindo ate sob o muro do patamar
        else:
            T_in = min(wild_z(imx, imy) - 0.4, min(Ts) - 1.0)
        prev_t = T
        z0 = ZS_B - 5.0 - 9.0 * pw
        x, y, nx, ny = mid
        zap = -26.0 - 4.0 * (nblk % 3) - 44.0 * pw
        apex = (x - nx * (depth * 0.3 - dout), y - ny * (depth * 0.3 - dout), zap)
        grass = T_in >= base - 1.6 and T < base + 3.0
        gx = sum(c[0][0] + c[1][0] for c in cols) / (2 * len(cols))
        gy = sum(c[0][1] + c[1][1] for c in cols) / (2 * len(cols))
        cmb = cliff_mb(gx, gy)
        block_cols(cmb, cols, inner, T_in, z0, apex, GRASS if grass else TOP)
        for qq in range(i, i + W + 1):
            RIM_FACE[qq] = (dout, T)
        nblk += 1
        # PROMONTORIO: degrau para o mar (bloco mais baixo, a frente, com 2-3 colunas) + pilar destacado
        if not tag and pw > 0.6 and mw < 0.2:
            cols2, inner2 = [], []
            pos = 2.0
            dout2 = dout + 4.6
            for cw in split_cols(float(W - 4)):
                qa, qb = min(N - 1, i + int(round(pos))), min(N - 1, i + int(round(pos + cw)))
                if qb <= qa:
                    pos += cw
                    continue
                dk = dout2 + COL_D[_KC[1] % 6] * 0.8
                tk = T - 6.0 + COL_T[_KC[2] % 8] * 0.7
                _KC[1] += 1
                _KC[2] += 1
                xa, ya, nxa, nya = smp[qa]
                xb, yb, nxb, nyb = smp[qb]
                nx2, ny2 = (nxa + nxb), (nya + nyb)
                nl = math.hypot(nx2, ny2) or 1.0
                pa = (xa + nxa * dk, ya + nya * dk)
                pb = (xb + nxb * dk, yb + nyb * dk)
                if not inner2:
                    inner2.append((xa + nxa * (dout - 1.6), ya + nya * (dout - 1.6)))
                inner2.append((xb + nxb * (dout - 1.6), yb + nyb * (dout - 1.6)))
                cols2.append((pa, pb, (nx2 / nl, ny2 / nl), tk))
                pos += cw
            if cols2:
                block_cols(cmb, cols2, inner2, T - 7.0, z0 + 7.0, (apex[0] + nx * 3.0, apex[1] + ny * 3.0, zap + 12.0),
                           TOP)
                nstep += 1
        if not tag and pw > 0.7 and mw < 0.2:
            x, y, nx, ny = smp[i + W // 2]
            r2 = 3.2
            d2 = dout + 5.6 + r2 * 1.1
            px, py = x + nx * d2, y + ny * d2
            zt2 = T - 11.0
            zb2 = zt2 - 40.0
            px, py, zt2 = water_fix(px, py, r2, zt2)
            zt2 = cap_top(px, py, r2, zt2)
            if zt2 - zb2 > 8.0 and dun_ok(px, py, r2, zb2 - r2 * 1.5, zt2):
                column(cliff_mb(px, py), px, py, r2, zt2, zb2, 0.3, m=ROCK, cap=TOP, band=(0.9, TOP),
                       strata=(ZS_A if ZS_A < zt2 - 2.0 else zt2 - 8.0, 0.86, (nx * 0.3, ny * 0.3)), low=DARK,
                       tip=r2 * 1.5)
                npil += 1
        gap = (1 if pw > 0.25 else 2) if (j + 1 < N and tags[min(N - 1, j + 1)] == tag) else 1
        i += W + gap
    print("TER COROA blocos=%d degraus=%d pilares=%d" % (nblk, nstep, npil))
    return nblk


# ------------------------------------------------------------------ 5) QUILHA (casca do subsolo) + quilhas dos promontorios
# FINESSE 3 (14.01): a secao sul recua para y -60 (nada de subsolo ao sul de y 2): a proa da vila fecha mais depressa
K_RECT = (-78.0, -60.0, 78.0, 344.0)       # secao da quilha em z -80 (>= 120 x 320 pedido; salas x +-56, y 2..306)
K_CORNER = 30.0
# (t para a secao K, cota, amplitude da flauta): cada nivel = faixa quase a prumo ate a cota seguinte + degrau
# FINESSE 3 (14.01): CONE invertido desde o pe da coroa (antes os 2 primeiros niveis eram quase a prumo e o fundo lia
# como prato): t 0,17 ja em -14 e 0,42 em -32; a casca continua a envolver o Salao Sombrio (z >= -17) e as salas
KEEL = [(0.00, ZS_B - 2.0, 1.0), (0.17, -14.0, 1.3), (0.42, -32.0, 1.4), (0.66, -50.0, 1.3), (0.84, -66.0, 1.0),
        (0.96, -80.0, 0.7)]
KEEL_BOT = [(0.62, -94.0), (0.30, -102.0)]   # (escala em volta do centro de K, cota) e a ponta em -108
KEEL_NU = 128


def k_poly():
    x0, y0, x1, y1 = K_RECT
    r = K_CORNER
    out = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90.0), (x1 - r, y1 - r, 0.0), (x0 + r, y1 - r, 90.0), (x0 + r, y0 + r, 180.0)):
        for k in range(7):
            a = math.radians(a0 + 15.0 * k)
            out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


KEEL_RINGS = []                              # (z, contorno 2D) para o verify_subsoil


def keel():
    mb = smb("SG_Ter_Cliff_Under")
    per = sum(math.hypot(RIM[(k + 1) % len(RIM)][0] - RIM[k][0], RIM[(k + 1) % len(RIM)][1] - RIM[k][1])
              for k in range(len(RIM)))
    pts = resample_closed(RIM, per / KEEL_NU)
    n = len(pts)
    K = k_poly()
    kc = ((K_RECT[0] + K_RECT[2]) / 2, (K_RECT[1] + K_RECT[3]) / 2)
    targ = []
    for x, y, nx, ny in pts:
        ang = math.degrees(math.atan2(y - C[1], x - C[0]))
        d = SL.ray_poly(K, ang, C[0], C[1])
        targ.append((C[0] + d * math.cos(math.radians(ang)), C[1] + d * math.sin(math.radians(ang))))
    bm = mb.bm
    FL = (1.0, 0.55, -1.0)                    # feixes de 3 colunas (fora, fora, dentro)
    KEEL_RINGS.clear()

    def ring(t, z, amp, zfun=None):
        rg, p2 = [], []
        for k, ((x, y, nx, ny), (qx, qy)) in enumerate(zip(pts, targ)):
            fl = amp * FL[k % 3]
            px, py = x + (qx - x) * t + nx * fl, y + (qy - y) * t + ny * fl
            zz = zfun(x, y) if zfun else z
            rg.append(bm.verts.new((px, py, zz)))
            p2.append((px, py))
        KEEL_RINGS.append((z if not zfun else SH, p2))
        return rg
    rings, mats = [], []
    rings.append(ring(0.0, SH, 0.0, zfun=lambda x, y: wild_z(x, y)))          # junta com o ombro / pescoco
    for i, (t, z, amp) in enumerate(KEEL):
        a_ = amp if i else 0.0                                              # o 1o nivel e a faixa atras da coroa
        rings.append(ring(t, z, a_))
        mats.append(DARK)                                                   # i=0: faixa do contorno; depois: degrau
        z_next = KEEL[i + 1][1] if i + 1 < len(KEEL) else -90.0
        rings.append(ring(t + (0.05 if i else 0.02), z_next, a_))
        mats.append(ROCK if 0 < i < 3 else DARK)                            # faixa canelada (quase a prumo)
    for sc, zz in KEEL_BOT:
        rg = []
        for (qx, qy) in targ:
            rg.append(bm.verts.new((kc[0] + (qx - kc[0]) * sc, kc[1] + (qy - kc[1]) * sc, zz)))
        rings.append(rg)
        mats.append(DARK)
    apex = bm.verts.new((kc[0], kc[1], -108.0))
    groups = {}
    for (r0, r1), mm in zip(zip(rings, rings[1:]), mats):
        for k in range(n):
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((r0[k2], r0[k], r1[k], r1[k2])))
    for k in range(n):
        groups.setdefault(DARK, []).append(bm.faces.new((rings[-1][(k + 1) % n], rings[-1][k], apex)))
    mb._post([v for rg in rings for v in rg] + [apex], DARK, None, 0, 1)
    mi = mb._mi_for(ROCK)
    for f in groups.get(ROCK, []):
        f.material_index = mi
    keels()


def keels():
    """7 QUILHAS sob os promontorios (fuso de 14 lados descendo ate -88/-96) com as colunas pendentes so nelas"""
    smp = resample_closed(RIM, 1.0)
    for idx, (px, py, hw) in enumerate(PROMS):
        x, y, nx, ny = min(smp, key=lambda s: math.hypot(s[0] - px, s[1] - py))
        tx, ty = -ny, nx
        cx, cy = x - nx * 7.0, y - ny * 7.0
        big = idx in (0, 2, 5)                      # 14.01: 3 LOBULOS maiores (O, N, SE) na quilha
        A, B = hw * (1.15 if big else 0.78), (15.0 if big else 9.5)
        kmb = cliff_mb(x, y)
        m = 14
        bm = kmb.bm
        krings = []
        for sc, z in ((1.0, ZS_B - 2.0), (0.8, -26.0), (0.5, -52.0 - (10.0 if big else 0.0))):
            rg = []
            for k in range(m):
                a = 2 * math.pi * k / m
                rr = sc * (1.0 + (0.12 if k % 2 == 0 else -0.1))
                rg.append(bm.verts.new((cx + tx * A * rr * math.cos(a) + nx * B * rr * math.sin(a),
                                        cy + ty * A * rr * math.cos(a) + ny * B * rr * math.sin(a), z)))
            krings.append(rg)
        if tx * ny - ty * nx < 0:
            krings = [rg[::-1] for rg in krings]
        zk = -88.0 - 8.0 * (idx % 2) - (10.0 if big else 0.0)
        kap = bm.verts.new((cx + nx * 1.5, cy + ny * 1.5, zk))
        kf = [bm.faces.new(krings[0])]
        for r0, r1 in zip(krings, krings[1:]):
            for k in range(m):
                k2 = (k + 1) % m
                kf.append(bm.faces.new((r0[k2], r0[k], r1[k], r1[k2])))
        for k in range(m):
            kf.append(bm.faces.new((krings[-1][(k + 1) % m], krings[-1][k], kap)))
        bmesh.ops.recalc_face_normals(bm, faces=kf)
        kmb._post([v for rg in krings for v in rg] + [kap], DARK, None, 0, 1)
        mi = kmb._mi_for(ROCK)
        for f in kf[1:1 + m]:
            f.material_index = mi
        for j in range(4):
            c = (j - 1.5) / 1.5
            a = math.pi * (0.5 + 0.34 * c)
            qx = cx + tx * A * 0.8 * math.cos(a) + nx * B * 0.85 * math.sin(a)
            qy = cy + ty * A * 0.8 * math.cos(a) + ny * B * 0.85 * math.sin(a)
            r = 4.2 - 0.9 * abs(c)
            zb = -48.0 - 20.0 * (1.0 - abs(c)) - 4.0 * (idx % 2)
            if not dun_ok(qx, qy, r, zb - r * 1.3, 0.0):
                continue
            column(kmb, qx, qy, r, 0.0, zb, 0.4 * j, m=ROCK, cap=DARK, strata=((0.0 + zb) / 2, 0.82,
                   (nx * 0.5, ny * 0.5)), low=DARK, tip=r * 1.3)


def verify_subsoil():
    """a casca envolve o subsolo: em toda cota de anel dentro da faixa de z de uma caixa, o contorno do anel contem a
    pegada da caixa com folga >= 2 (sem furo para fora); nada da ilha dentro das caixas (o QA CAVE_LIVRE/DUNGEON_LIMPA
    confere as malhas)"""
    bad = []
    for nm, (x0, y0, z0, x1, y1, z1) in (("salao", CAVE_BOX), ("salas", DUN_BOX)):
        foot = []
        for k in range(21):
            f = k / 20.0
            foot += [(x0 - 2 + (x1 - x0 + 4) * f, y0 - 2), (x0 - 2 + (x1 - x0 + 4) * f, y1 + 2),
                     (x0 - 2, y0 - 2 + (y1 - y0 + 4) * f), (x1 + 2, y0 - 2 + (y1 - y0 + 4) * f)]
        zs = [z for z, p in KEEL_RINGS]
        for i, (z, poly) in enumerate(KEEL_RINGS):
            zn = KEEL_RINGS[i + 1][0] if i + 1 < len(KEEL_RINGS) else z
            if max(z, zn) < z0 or min(z, zn) > z1:
                continue
            out = [p for p in foot if not L.point_in_poly(p[0], p[1], poly)]
            if out:
                bad.append((nm, round(z, 1), len(out)))
    # secao em z -80 (pedido: >= 120 x 320)
    sec = [p for z, p in KEEL_RINGS if abs(z + 80.0) < 0.01]
    dims = None
    if sec:
        xs = [p[0] for p in sec[-1]]
        ys = [p[1] for p in sec[-1]]
        dims = (round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1))
    print("TER SUBSOLO casca=%s secao_z-80=%s" % ("OK (envolve salao e salas)" if not bad else "FURO %s" % bad[:6],
                                                 dims))


# ------------------------------------------------------------------ raiz de rocha sob a ponte de chegada (14.01)
def bridge_root():
    """feixe de colunas de basalto pendentes sob o encontro da ponte com o patio baixo (abaixo do fundo do tabuleiro,
    25,4): a ilha 'agarra' a ponte; sem colisao (fora de rota)"""
    mb = cliff_mb(0.0, -340.0)
    # so pendentes cujo topo fica DENTRO do encontro do sg_entry (planta +-11,8 em y -341,5; z ate 25,7): saem por baixo
    for q, (cx, cy, r, zt, zb) in enumerate(((-8.0, -338.6, 3.2, 24.6, -24.0), (0.6, -339.8, 3.8, 24.2, -34.0),
                                               (7.8, -338.2, 3.0, 23.6, -18.0))):
        column(mb, cx, cy, r, zt, zb, 0.3 + 0.45 * q, m=ROCK, cap=DARK, strata=(ZS_B - 1.0 * q, 0.86, (0.0, -0.4)),
               low=DARK, tip=r * 1.5)


# ------------------------------------------------------------------ colunas altas da borda (silhueta)
def spires():
    """06.09: as colunas de rocha da planta (CLIFF_SPIRES) deixam de ser torres soltas junto das rotas: cada uma NASCE
    DA FACE do penhasco (centro fora do contorno) como feixe de 3 colunas em degrau; as 2 atras do castelo (norte, longe
    de toda rota) guardam a silhueta de longe (topo P3 + 28); as outras ficam na altura da coroa (topo = patamar + 6:
    pinaculos da falesia, abaixo do olhar de quem anda junto ao parapeito)"""
    smp = resample_closed(RIM, 1.0)
    ncol = 0
    for x, y, r, top_z, kind in L.CLIFF_SPIRES:
        rx, ry, nx, ny = min(smp, key=lambda s_: math.hypot(s_[0] - x, s_[1] - y))
        zd = zone_dist(rx, ry, nx, ny, lim=30.0)
        zp = L.zone_of(rx - nx * zd, ry - ny * zd) if zd is not None else SH
        tall = y > 350.0
        top = zp + (28.0 if tall else 6.0)
        top = max(top, crown_design(rx, ry) + 3.0)
        tx, ty = -ny, nx
        mb = cliff_mb(rx, ry)
        cx, cy = rx + nx * r * 0.7, ry + ny * r * 0.7
        for q_, (lat, out, fr, dz) in enumerate(((0.0, 0.0, 0.5, 0.0), (0.58, 0.1, 0.38, 6.0), (-0.52, 0.35, 0.32, 11.0))):
            rc = r * fr
            px, py = cx + tx * lat * r + nx * out * r, cy + ty * lat * r + ny * out * r
            zt = top - dz
            zb = -30.0 - 3.0 * q_
            px, py, zt = water_fix(px, py, rc, zt)
            zt = cap_top(px, py, rc, zt)
            if not dun_ok(px, py, rc, zb - rc * 1.5, zt):
                continue
            zs = min(ZS_A, zt - 9.0 - 1.5 * q_)
            column(mb, px, py, rc, zt, zb, 0.25 * q_ + 0.2, m=ROCK, cap=TOP, band=(1.2, TOP),
                   strata=(zs, 0.86, (nx * 0.3, ny * 0.3)), low=DARK, tip=rc * 1.6)
            ncol += 1
            if q_ == 0 and L.point_in_poly(px, py, L.ISLAND_RIM):
                octo_col("SG_TerSpire", px, py, rc * 0.8, zp - 3.7, zp + 20.0)
    print("TER AGULHAS colunas=%d" % ncol)


# ------------------------------------------------------------------ 8) jardim-mirante: moldura de rocha
def mirante_rock():
    """rocha do JARDIM-MIRANTE (P3 leste, no lugar da portaria): a vista para leste fica LIVRE no eixo (a coroa desce,
    rim_cliff) e 2 MACICOS de basalto em degrau emolduram o terraco a norte e a sul, fora do parapeito, com o topo mais
    alto logo ABAIXO da cota do P3 (a moldura e a falesia; vista de fora o terraco fica 'num pulpito' de rocha)."""
    mx, my, mr = L.MIRANTE_E
    smp = resample_closed(RIM, 1.0)
    q0 = min(range(len(smp)), key=lambda q: math.hypot(smp[q][0] - (mx + 40.0), smp[q][1] - my))
    x, y, nx, ny = smp[q0]
    tx, ty = -ny, nx
    mb = cliff_mb(x, y)
    for s, h0 in ((-1, -1.2), (1, -2.4)):
        for j, (lat, d, r, dz) in enumerate(((mr + 3.0, 2.2, 3.3, 0.0), (mr + 7.4, 3.0, 3.0, 2.2),
                                              (mr + 4.6, 6.2, 2.8, 3.6), (mr + 9.6, 6.8, 2.5, 5.8),
                                              (mr + 1.6, 5.4, 2.4, 5.0))):
            cx = x + tx * s * lat + nx * d
            cy = y + ty * s * lat + ny * d
            zt = P3 + h0 - dz
            if any(L.zone_of(px, py) is not None for px, py in hex_pts(cx, cy, r + 0.3)):
                continue
            if not dun_ok(cx, cy, r, ZS_B - 10.0, zt):
                continue
            column(mb, cx, cy, r, zt, ZS_B - 4.0 - 3.0 * j, 0.3 + 0.5 * j, m=ROCK, cap=GRASS if j % 2 == 0 else TOP,
                   band=(1.0, TOP), strata=(ZS_A, 0.86, (nx * 0.4, ny * 0.4)), low=DARK, tip=r * 1.4)


# ------------------------------------------------------------------ 7) rocha das quedas d'agua
def water_lips():
    """bancada de pedra das cachoeiras que saem de um patamar (a agua e do Roblox, a bica/calha do sg_water): bancada na
    cota do labio -0,1 ligada a borda do patamar, com margens de colunas. A do SUL sai de uma fenda (water_fix)."""
    rng = random.Random(3701)
    for wx, wy, wz, ux, uy in FALLS:
        src = None
        for k in range(1, 40):
            bx, by = wx - ux * k * 0.5, wy - uy * k * 0.5
            z = L.zone_of(bx, by)
            if z is not None:
                src = (bx, by, z, k * 0.5)
                break
        if src is None or src[2] - wz > 1.6:
            continue
        mb = cliff_mb(wx, wy)
        L_ = src[3] + 0.8
        vx, vy = -uy, ux
        a = (wx - ux * (L_ - 0.8), wy - uy * (L_ - 0.8))
        poly = [(a[0] - vx * 4.6, a[1] - vy * 4.6), (wx + ux * 0.8 - vx * 4.6, wy + uy * 0.8 - vy * 4.6),
                (wx + ux * 0.8 + vx * 4.6, wy + uy * 0.8 + vy * 4.6), (a[0] + vx * 4.6, a[1] + vy * 4.6)]
        prism2(mb, poly, SH - 1.0, wz - 0.1, ROCK, m_top=TOP, m_bot=DARK)
        for s in (-1, 1):
            nk = max(2, int(L_ / 4.0) + 1)
            for k in range(nk):
                t = (L_ - 0.8) * (1.0 - k / max(1, nk - 1)) + 0.4
                rc = rng.uniform(1.9, 2.5)
                cx = wx - ux * (t - 0.8) + vx * s * (4.6 + rc * 0.9)
                cy = wy - uy * (t - 0.8) + vy * s * (4.6 + rc * 0.9)
                zt = wz + rng.uniform(0.7, 1.6)
                zt = cap_top(cx, cy, rc, zt)
                column(mb, cx, cy, rc, zt, SH - 1.2, rng.uniform(0, 1.05), m=ROCK,
                       cap=GRASS if rng.random() < 0.5 else TOP, band=(0.7, TOP))


def fall_steps():
    """degrau de basalto sob cada cachoeira na cota do estrato de cima (20 = FX_Fall_<n>_Step): 2 fileiras de colunas
    saindo da face; a agua do Roblox bate nele, quebra em espuma e abre"""
    for wx, wy, wz, ux, uy in FALLS:
        if wz - ZS_A < 8.0:
            continue
        mb = cliff_mb(wx, wy)
        vx, vy = -uy, ux
        for along, lats, dz, r in ((-0.6, (-3.4, 0.0, 3.4), (-1.6, -1.1, -1.9), 2.7),
                                   (3.0, (-3.0, 0.2, 3.3), (-0.6, 0.0, -0.9), 2.5)):
            for q, (lat, d) in enumerate(zip(lats, dz)):
                cx, cy = wx + ux * along + vx * lat, wy + uy * along + vy * lat
                zt = ZS_A + d
                if not dun_ok(cx, cy, r, zt - 14.0, zt):
                    continue
                column(mb, cx, cy, r, zt, zt - 3.5 - 0.8 * q, 0.3 + 0.4 * q, m=ROCK, cap=TOP, band=(0.6, TOP),
                       low=DARK, tip=r * 1.3)


# ------------------------------------------------------------------ 9) cristais (2 aglomerados na borda)
def crystal(mb, base, ax, ln, r, m="SG_Crystal_Glow"):
    ax = Vector(ax).normalized()
    yaw = math.atan2(ax.y, ax.x)
    pitch = math.acos(max(-1.0, min(1.0, ax.z)))
    rot = (0.0, pitch, yaw)
    b = Vector(base)
    mb.cyl(r, ln * 0.7, b + ax * (ln * 0.35), rot, m=m, n=6, r2=r * 0.8, bevel=0.0)
    mb.cyl(r * 0.8, ln * 0.3, b + ax * (ln * 0.85), rot, m=m, n=6, r2=0.03, bevel=0.0)


def crystal_ok(x, y, r, z0, z1):
    if not dun_ok(x, y, r, z0, z1):
        return False
    for nm, a, b, z, w in BRIDGES:
        if sg_col._in_rect_along(x, y, a, b, w / 2 + 3.0, pad=4.0):
            return False
    for wx, wy, wz, ux, uy in FALLS:
        lat = abs(-(x - wx) * uy + (y - wy) * ux)
        along = (x - wx) * ux + (y - wy) * uy
        if lat < 5.5 and along > -6.0:
            return False
    return True


def rim_crystals():
    """cristais da borda (13.09): 2 aglomerados (sob o terraco norte a nordeste e sob o beco oeste) com 1 cristal-heroi
    + 3 menores em leque encravados na face REAL do bloco, + 2 pontas pendentes; e a ilhota da invocacao"""
    mb = smb("SG_Ter_Crystals")
    smp = resample_closed(RIM, 1.0)
    N = len(smp)
    fan = [(0.0, 1.0, 0.0), (-1.4, 0.62, -0.32), (1.3, 0.55, 0.3), (0.55, 0.4, 0.12)]
    ncl = 0
    for name, (hx, hy), hero in (("Nordeste", (146.0, 262.0), 6.8), ("Oeste", (-172.0, 116.0), 6.0)):
        order = sorted(range(N), key=lambda q: math.hypot(smp[q][0] - hx, smp[q][1] - hy))
        got = None
        for q in order[:60]:
            if q not in RIM_FACE:
                continue
            x, y, nx, ny = smp[q]
            dout, T = RIM_FACE[q]
            zt = T - 6.5
            fx, fy = x + nx * (dout - 0.8), y + ny * (dout - 0.8)
            if crystal_ok(fx, fy, 3.5, zt - 10.0, zt + 7.0) and zt > ZS_A + 1.0:
                got = (fx, fy, nx, ny, zt)
                break
        if got is None:
            print("TER AVISO aglomerado de cristal sem lugar:", name)
            continue
        fx, fy, nx, ny, zt = got
        sx, sy = -ny, nx
        for lat, f, lean in fan:
            ln = hero * f
            rr = (0.32 + hero * 0.10) * f
            ax = (nx * 0.45 + sx * lean, ny * 0.45 + sy * lean, 1.0)
            crystal(mb, (fx + sx * lat, fy + sy * lat, zt - ln * 0.4 - (0.0 if f == 1.0 else 0.6)), ax, ln, rr)
        for lat, dz, ln, rr in ((-1.8, 18.0, 4.4, 0.62), (2.2, 24.0, 3.2, 0.5)):
            if crystal_ok(fx, fy, 2.0, zt - dz - ln, zt - dz):
                crystal(mb, (fx - nx * 1.5 + sx * lat, fy - ny * 1.5 + sy * lat, ZS_B - 1.5 - (dz - 18.0)),
                        (nx * 0.5, ny * 0.5, -1.0), ln, rr)
        ncl += 1
    ssx, ssy = L.SUMMON_C
    for k, (deg, z, ln, rr) in enumerate(((-58.0, -9.0, 3.2, 0.42), (-44.0, -14.0, 4.4, 0.55),
                                          (-30.0, -11.0, 3.0, 0.4), (-40.0, -16.5, 2.6, 0.36))):
        a = math.radians(deg)
        crystal(mb, (ssx + 12.2 * math.cos(a), ssy + 12.2 * math.sin(a), z),
                (math.cos(a) * 0.6, math.sin(a) * 0.6, -1.0), ln, rr)
    ncl += 1
    print("TER CRISTAIS aglomerados=%d" % ncl)


# ------------------------------------------------------------------ ilhota da invocacao (a da v3, na posicao nova)
def ebox(mb, a, u, nrm, t0, t1, d0, d1, z0, z1, m):
    tm, dm = (t0 + t1) / 2, (d0 + d1) / 2
    cx = a[0] + u[0] * tm + nrm[0] * dm
    cy = a[1] + u[1] * tm + nrm[1] * dm
    mb.box((abs(t1 - t0), abs(d1 - d0), abs(z1 - z0)), (cx, cy, (z0 + z1) / 2), (0, 0, math.atan2(u[1], u[0])), m, 0)


def block_mesh(mb, outer, inner, T, zs, z0, apex, cap):
    poly = clean(ccw(outer + inner[::-1]))
    n = len(poly)
    if n < 3:
        return
    bm = mb.bm
    gx = sum(p[0] for p in poly) / n
    gy = sum(p[1] for p in poly) / n
    ox, oy = apex[0] - gx, apex[1] - gy
    ol = math.hypot(ox, oy) or 1.0

    def ring(pts, z):
        return [bm.verts.new((x, y, z)) for x, y in pts]
    lower = [(gx + (x - gx) * 0.9 + ox / ol * 0.5, gy + (y - gy) * 0.9 + oy / ol * 0.5) for x, y in poly]
    seq = [(ring(poly, T), None), (ring(poly, T - 1.0), TOP)]
    if z0 + 1.0 < zs < T - 2.5:
        seq.append((ring(poly, zs), ROCK))
        seq.append((ring(lower, zs), DARK))
        seq.append((ring(lower, z0), DARK))
    else:
        seq.append((ring(poly, z0), ROCK))
    top = bm.faces.new(seq[0][0])
    groups = {}
    for (a, _), (b, mm) in zip(seq, seq[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last = seq[-1][0]
    av = bm.verts.new(apex)
    for k in range(n):
        groups.setdefault(DARK, []).append(bm.faces.new((last[(k + 1) % n], last[k], av)))
    allv = [v for rg, _ in seq for v in rg] + [av]
    _faces_ok(mb, [top] + [f for fs in groups.values() for f in fs])
    mb._post(allv, ROCK, None, 0, 1)
    top.material_index = mb._mi_for(cap)
    for mm, fs in groups.items():
        if mm != ROCK:
            mi = mb._mi_for(mm)
            for f in fs:
                f.material_index = mi


def prism2(mb, poly, z0, z1, m_side, m_top=None, m_bot=None):
    poly = clean(ccw(poly))
    if len(poly) < 3 or abs(SL.area(poly)) < 0.5:
        return
    bm = mb.bm
    vb = [bm.verts.new((x, y, z0)) for x, y in poly]
    vt = [bm.verts.new((x, y, z1)) for x, y in poly]
    fb = bm.faces.new(list(reversed(vb)))
    ft = bm.faces.new(vt)
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m_side, None, 0, 1)
    if m_top:
        ft.material_index = mb._mi_for(m_top)
    if m_bot:
        fb.material_index = mb._mi_for(m_bot)


def summon_isle():
    """plataforma redonda propria (topo 40,2, 24-gono igual a colisao do sg_col) sobre tambor de alvenaria e rocha em
    colunas pendentes; lingua de rocha sob a escada curta"""
    rng = random.Random(3801)
    mb = smb("SG_Ter_SummonIsle")
    sx, sy = L.SUMMON_C
    R = L.SUMMON_R
    top = [(sx + R * math.cos(math.radians(15.0 * k)), sy + R * math.sin(math.radians(15.0 * k))) for k in range(24)]
    prism2(mb, top, SUM - 1.6, SUM, TRIM, m_top=PAVE)
    drum = [(sx + (R - 0.5) * math.cos(math.radians(15.0 * k)), sy + (R - 0.5) * math.sin(math.radians(15.0 * k)))
            for k in range(24)]
    prism2(mb, drum, 29.0, SUM - 1.6, DARK)
    zc0, zc1 = 33.0, SUM - 1.6
    nc = 3
    hc = (zc1 - zc0) / nc
    for c in range(nc):
        for k in range(24):
            a0 = math.radians(15.0 * k + (7.5 if c % 2 else 0.0))
            a1 = a0 + math.radians(15.0)
            p0 = (sx + (R - 0.5) * math.cos(a0), sy + (R - 0.5) * math.sin(a0))
            p1 = (sx + (R - 0.5) * math.cos(a1), sy + (R - 0.5) * math.sin(a1))
            ux, uy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(ux, uy)
            ux, uy = ux / ln, uy / ln
            am = math.degrees((a0 + a1) / 2) % 360.0
            if am < 22.0 or am > 338.0:
                continue
            ebox(mb, p0, (ux, uy), (uy, -ux), 0.1, ln - 0.1, -0.05, 0.5 + rng.uniform(-0.08, 0.08),
                 zc0 + c * hc + 0.08, zc0 + (c + 1) * hc - 0.08, BLOCK)
    for rr, z0, z1 in ((R - 3.0, 4.0, 29.5), (13.0, -18.0, 4.0), (7.0, -36.0, -18.0)):
        prism2(mb, [(sx + rr * math.cos(math.radians(22.5 * k)), sy + rr * math.sin(math.radians(22.5 * k)))
                    for k in range(16)], z0, z1, DARK)
    a0 = rng.uniform(0.0, 20.0)
    for k in range(5):
        aa = math.radians(a0 + 72.0 * k + 6.0)
        ab = math.radians(a0 + 72.0 * (k + 1) - 6.0)
        dout = rng.uniform(-0.6, 1.2)
        outer, inner = [], []
        m = 12
        for q in range(m + 1):
            t = aa + (ab - aa) * q / m
            rr = R - 0.3 + dout + ((0.45 + rng.uniform(-0.2, 0.2)) if q % 2 == 0 else -0.75)
            outer.append((sx + rr * math.cos(t), sy + rr * math.sin(t)))
        for q in range(5):
            t = aa + (ab - aa) * q / 4
            inner.append((sx + (R - 8.0) * math.cos(t), sy + (R - 8.0) * math.sin(t)))
        T = rng.uniform(30.5, 33.4)
        am = (aa + ab) / 2
        apex = (sx + (R - 3.0) * math.cos(am), sy + (R - 3.0) * math.sin(am), rng.uniform(-36.0, -14.0))
        block_mesh(mb, outer, inner, T, T - rng.uniform(10.0, 17.0), rng.uniform(-2.0, 6.0), apex, TOP)
    for n, rad, rr0, rr1, zt0, zt1, zb0, zb1 in ((6, 11.0, 4.4, 5.2, 2.0, 3.5, -44.0, -26.0),
                                                  (2, 3.5, 4.2, 4.8, -17.0, -16.0, -58.0, -48.0)):
        for k in range(n):
            a = 2 * math.pi * (k + rng.uniform(-0.15, 0.15)) / n + 0.2
            cx, cy = sx + rad * math.cos(a), sy + rad * math.sin(a)
            r = rng.uniform(rr0, rr1)
            zt = rng.uniform(zt0, zt1)
            zb = rng.uniform(zb0, zb1)
            zs = (zt + zb) / 2 + rng.uniform(-3.0, 3.0)
            column(mb, cx, cy, r, zt, zb, rng.uniform(0, 1.05), m=ROCK, cap=TOP, band=(0.8, TOP),
                   strata=(zs, 0.84, (math.cos(a) * 0.4, math.sin(a) * 0.4)), low=DARK, tip=r * 1.4)
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    xa, xb = foot[0] + 0.4, sx + R - 1.0
    ya, yb = foot[1] - w / 2 - 1.3, foot[1] + w / 2 + 1.3
    prism2(mb, [(xb, ya), (xa, ya), (xa, yb), (xb, yb)], 30.0, P1 - 0.3, DARK)
    for k, (dx, dy) in enumerate(((-2.5, -4.5), (-2.8, 4.4), (-6.2, 0.2))):
        cx, cy = foot[0] + dx, foot[1] + dy
        column(mb, cx, cy, rng.uniform(2.4, 3.0), 30.4, rng.uniform(8.0, 18.0), rng.uniform(0, 1.05), m=ROCK,
               cap=DARK, low=DARK, tip=3.6)


# ------------------------------------------------------------------ build
def build():
    _MB.clear()
    check_star()
    tops()
    bodies()
    neck()
    terrace_edges()
    curbs()
    paving()
    rim_cliff()
    keel()
    # (bridge_root() desligado a pedido do E, 01.07: os pendentes apareciam pelo ultimo arco; o encontro do sg_entry
    #  ja faz a rocha sob a ponte)
    verify_subsoil()
    spires()
    mirante_rock()
    water_lips()
    fall_steps()
    summon_isle()
    rim_crystals()
    # as cascas ABERTAS (topos, faces laterais, casca da quilha, blocos da coroa) ja nascem com a normal certa; o
    # recalc global do MB viraria algumas para dentro. So os muros (so pecas fechadas) passam pelo recalc.
    for nm in sorted(_MB):
        _MB[nm].finish(recalc=nm.startswith(("SG_Ter_Wall_", "SG_Ter_Paving_")) or nm == "SG_Ter_Crystals")
    _MB.clear()
