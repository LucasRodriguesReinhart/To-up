# sg_dungeon - ZONA DUNGEON da Ilha 3 (Shadow Garden). build() substitui sg_blockout.dungeon (inclusive as colisoes e as
# luzes dela). Prefixo SG_Dun_, colecao 17_DUNGEON, VFX_SGDUN_* em 12_VFX_HELPERS. A dungeon e a "corrida de mineracao"
# periodica do jogo (XX:00 / XX:30): o jogador entra pelo PORTAL da portaria (superficie, P3) e o jogo o leva para as 3
# SALAS modulares escondidas dentro da rocha (piso DUN_Z 6,0; teto DUN_CEIL 28); minera nos DUN_ORE_* e sai pelo portal
# de saida da R3. O sistema e do jogo: aqui so o LUGAR. NAO modela minerio.
#   1. PORTARIA (DUNGEON_HOUSE 26x26 em (100, 72), P3 52,2): torre gotica escura (ver REFINAMENTO abaixo: coroamento de
#      agulhas negras, fendas violeta, fachada-portal na face SUL com o vao ogival 10 x 14). Interior 20 x 20 entravel (pe-direito 21,6 sob a abobada): PORTAL ESPIRAL no fundo (anel de pedra com
#      runas de prata + disco violeta; a espiral gira = VFX_SGDUN_Portal), nicho ogival, 2 GUARDIOES encapuzados com
#      espada (genericos), estrado de 2 degraus (0,4 + 0,8 - colisao casada), 2 braseiros, tochas, abobada com nervuras.
#   2. SALAS (R1 chegada 36 x 36, R2 mineracao 44 x 44, R3 camara final 44 x 44) com o MESMO kit: parede com pilastras
#      e arcos ogivais cegos, colunas de canto, cornija de arranque, tochas de parede, piso de lajes escuras com friso,
#      abobada ogival de bercos com nervuras e bossas. Vaos de ligacao 12 x 12 (verga + timpano ogival com o emblema).
#      Variacao: R1 portal de chegada (parede oeste, aceso); R2 salao largo com arcada dupla nas paredes N/S e 2 lustres;
#      R3 portal de saida (parede leste; a espiral e objeto proprio SG_Dun_R3_ExitSpiral que o jogo liga em FINISHING),
#      altar = medalhao embutido no piso sob o DUN_ORE_R3_SUPERLEGENDARY + lustre-coroa em cima.
#   3. COLISAO propria (caixas): piso, paredes com os vaos, teto (opaco) das salas; paredes com o vao da porta (+ cantos
#      da ogiva), teto interno, torrinhas, ombreiras do portal, estrado, estatuas, braseiros e monolitos. Nada colidivel a
#      menos de 5 dos DUN_ORE_* ate piso+12 (conferido em ccol()).
#   4. Luzes (7): portaria = portal violeta + braseiro quente; patio = 1 luz violeta da aproximacao; salas = portal de
#      chegada (violeta) + 2 lustres da R2 + lustre da R3 (quentes).
# REFINAMENTO 2026-09-28 (queixa: "a entrada da dungeon esta sem impacto e parece generica"). A portaria deixa de ser uma
# torre com porta e vira um LUGAR DE DESAFIO, com um sistema so (obsidiana + violeta + runas + o emblema da ordem):
#   - FACHADA-PORTAL: portal monumental projetado 5 studs para fora da face sul, 4 arquivoltas ogivais escalonadas
#     (violeta/obsidiana alternadas, ~31 de altura) com 2 costuras de energia, LAMINAS de obsidiana no extradorso (coroa
#     quebrada que fura a linha das ameias), emblema da ordem (sg_emblem.plaque) no fecho, TIMPANO com um segundo VORTICE
#     que gira (VFX_SGDUN_FacadeVortex, visivel de longe) e a LAPIDE negra da contagem sob o marcador DUNGEON_UI.
#   - COROAMENTO: ameias viram dentes de obsidiana irregulares, torrinhas e agulha central viram agulhas negras (com
#     laminas menores inclinadas), lancetas e seteiras viram FENDAS violeta (SG_VioletDeep_Glow). Sai o que era generico:
#     oculo quente, wimperg com estrela, pinaculos navy, lanternas quentes da porta.
#   - APROXIMACAO (patio P3 ao sul): ferradura de lajes negras com RACHADURAS luminosas convergindo no portal, CIRCULO de
#     6 monolitos de obsidiana inclinados com runas (os 2 do vao sao os mais altos) acorrentados entre si e ao portal,
#     2 braseiros de chama violeta e 2 SENTINELAS encapuzadas com laminas cruzadas. Corredor de 10 no eixo x=100 e as
#     linhas do andador (patio->portaria, escada leste->portaria) livres (conferido em _approach_check()).
#   - Salas: o emblema substitui a estrela das molduras dos vaos; runas no piso diante dos portais R1/R3 e no altar.
import math, random
import bpy
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light
import fm_lib
import sg_layout as L
import sg_emblem as EM

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (3 de 4)
NEW_MATS = {
    "Stone_SGDunVault": (S(34, 38, 62), 0.8, 0.0, 0, None, 0.06),      # navy escuro: panos da abobada, fundo de nichos
    "Stone_SGDunStatue": (S(58, 62, 80), 0.55, 0.0, 0, None, 0.04),    # pedra polida dos guardioes
    "SG_DunVoid_Glow": (S(46, 26, 104), 0.3, 0.0, 1.0, S(56, 30, 124), 0.0),   # fundo do vortice (violeta profundo)
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

CS, TR, BL, FL = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Block", "Stone_SG_Floor"
VA, ST, VO = "Stone_SGDunVault", "Stone_SGDunStatue", "SG_DunVoid_Glow"
NAVY, SLATE, SV, IR = "Roof_SG_Navy", "Roof_SG_Slate", "Metal_SG_Silver", "Metal_SG_Iron"
GL, WW, VG = "Lantern_Glow", "Window_Warm", "SG_Violet_Glow"
# paleta de identidade (sg_lib.SMATS, refinamento): funcao de cada material na dungeon
OB, MBK, VS, BI = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Stone_SG_Violet", "Metal_SG_BlackIron"
VD, RG = "SG_VioletDeep_Glow", "SG_Rune_Glow"

P3 = L.P3
HX, HY, HW, HD = L.DUNGEON_HOUSE                 # 100, 72, 26, 26
HT = 3.0                                         # espessura das paredes da portaria
HX0, HX1, HY0, HY1 = HX - HW / 2, HX + HW / 2, HY - HD / 2, HY + HD / 2      # 87..113 x 59..85
IX0, IX1, IY0, IY1 = HX0 + HT, HX1 - HT, HY0 + HT, HY1 - HT                 # 90..110 x 62..82 (interior 20 x 20)
DW, DH = L.DUNGEON_DOOR_W, L.DUNGEON_DOOR_H      # 10 x 14
D_RISE = 4.5
D_SPR = DH - D_RISE                              # arranque da ogiva da porta (9,5)
BODY = 34.0                                      # topo da alvenaria (acima do piso P3)
IN_SPR, IN_CROWN, IN_CEIL = 14.5, 21.6, 22.0     # abobada interna da portaria / teto colidivel
PX, PY = L.DUNGEON_PORTAL                        # (100, 80)
DAIS = ((72.6, 0.4), (74.6, 0.8))                # (y inicial, topo) dos 2 degraus do estrado
TURRET_R = 3.6

Z, ZCEIL = L.DUN_Z, L.DUN_CEIL                   # 6, 28
ROOMS = dict(L.DUN_ROOMS)
WT = 2.0                                         # espessura das paredes das salas
LINK_H = 12.0
LY = 80.0                                        # eixo dos vaos / portais das salas
R_SPR = 12.0                                     # arranque da abobada das salas (acima do piso)
R_CROWN = ZCEIL - Z - 0.4                        # fecho (21,6): a casca (0,35) fica abaixo do teto colidivel
BX0, BY0, BX1, BY1 = -64.0, 56.0, 68.0, 104.0    # envelope das salas (paredes externas incluidas)

# ------------------------------------------------------------------ FACHADA-PORTAL (face sul; s = x, d = para o sul, h)
P_SPR = 10.0                                     # arranque das arquivoltas
P_HW0, P_RISE0, P_T = 6.5, 16.0, 1.2             # arquivolta 0 (intradorso) e largura de cada ordem
P_DEP = (1.8, 2.9, 4.0, 5.1)                     # frente de cada ordem (quanto projeta para o sul)
P_MAT = (VS, OB, VS, OB)                         # violeta / obsidiana alternadas (a externa, com as laminas, e negra)
TAB_H0, TAB_H1 = 14.0, 16.9                      # lapide da contagem (sob o marcador DUNGEON_UI, h 17)
KEY_H = 28.3                                     # centro do emblema do fecho


def order_hw(k):
    return P_HW0 + P_T * k


def order_rise(k):
    return P_RISE0 + P_T * k


def o0_half(h):
    """meia-largura do intradorso da arquivolta 0 na altura h (acima do piso)"""
    v = h - P_SPR
    if v <= 0.0:
        return P_HW0
    c, zc, R = _ogive_center(P_HW0, P_RISE0)
    q = R * R - (v - zc) ** 2
    return max(0.0, c + math.sqrt(q)) if q > 0 else 0.0


# ------------------------------------------------------------------ APROXIMACAO (patio P3 ao sul da porta)
PC = (100.0, 56.0)                               # centro da ferradura de lajes / do circulo de pedras
PR = 22.0                                        # raio da ferradura
MONO_R = 20.5
# (alfa graus abaixo da horizontal, altura): o par do vao (42) e o mais alto; oeste = espelho do leste
MONO_SPEC = ((8.0, 7.4), (25.0, 8.8), (42.0, 10.6))
STATUE_XY = ((86.0, 51.0), (114.0, 51.0))
BRAZIER_XY = ((92.5, 49.5), (107.5, 49.5))
# linhas do andador do sg_qa que cruzam o patio (patio -> portaria e portaria -> escada leste) + corredor do eixo
WALK_LINES = [((80.0, 30.0), (100.0, 51.0)), ((100.0, 51.0), (110.0, 30.0)), ((100.0, 51.0), (100.0, 62.0))]

CAMS = {
    "CAM_SGDun_HouseSouth": ((100.0, 18.0, P3 + 9.0), (100.0, 72.0, P3 + 24.0), 20),
    "CAM_SGDun_HouseEast": ((150.0, 40.0, P3 + 16.0), (100.0, 72.0, P3 + 24.0), 22),
    "CAM_SGDun_HouseNorth": ((132.0, 128.0, P3 + 34.0), (100.0, 72.0, P3 + 26.0), 22),
    "CAM_SGDun_HouseWest": ((58.0, 104.0, P3 + 16.0), (100.0, 72.0, P3 + 24.0), 22),
    "CAM_SGDun_PlayerDoor": ((100.0, 42.0, P3 + 5.2), (100.0, 72.0, P3 + 9.0), 22),
    "CAM_SGDun_Guardian": ((98.5, 70.0, P3 + 5.5), (92.6, 76.8, P3 + 6.0), 24),
    "CAM_SGDun_InteriorBack": ((100.0, 77.5, P3 + 6.0), (100.0, 59.0, P3 + 7.0), 18),
    "CAM_SGDun_R1Arrival": ((-36.0, 86.0, Z + 5.2), (-62.0, 79.0, Z + 7.0), 20),
    "CAM_SGDun_R1Spawn": ((-58.0, 70.0, Z + 5.2), (0.0, 82.0, Z + 5.0), 20),
    "CAM_SGDun_R2": ((-21.0, 61.0, Z + 9.0), (16.0, 98.0, Z + 8.0), 16),
    "CAM_SGDun_R2Link": ((-38.0, 84.0, Z + 5.2), (-8.0, 78.0, Z + 7.0), 20),
    "CAM_SGDun_R3Exit": ((25.0, 76.0, Z + 5.2), (66.0, 80.0, Z + 7.0), 20),
    "CAM_SGDun_R3Back": ((62.0, 62.0, Z + 10.0), (22.0, 96.0, Z + 7.0), 16),
    # refinamento: a dungeon vista do patio do castelo, na aproximacao (altura do jogador), de longe e o sentinela
    "CAM_SGDun_FromCastleCourt": ((30.0, 4.0, P3 + 7.0), (100.0, 58.0, P3 + 15.0), 26),
    "CAM_SGDun_Approach": ((90.0, 30.0, P3 + 5.2), (100.0, 60.0, P3 + 12.0), 20),
    "CAM_SGDun_Far": ((10.0, -70.0, P3 + 62.0), (100.0, 62.0, P3 + 16.0), 34),
    "CAM_SGDun_Sentinel": ((76.0, 40.0, P3 + 4.2), (95.0, 57.0, P3 + 8.5), 22),
}

EXTRA_ROUTES = {
    "PORTARIA_ATE_O_PORTAL": ([(100.0, 50.0), (100.0, 60.0), (100.0, 70.0), (100.0, 73.6), (100.0, 76.5)], P3),
    "APROXIMACAO_EIXO": ([(100.0, 32.0), (100.0, 44.0), (100.0, 54.0), (100.0, 61.0)], P3),
    "APROXIMACAO_TRAVESSIA": ([(92.0, 40.0), (100.0, 46.5), (108.0, 40.0)], P3),
    "SALA_R1_VOLTA": ([(-57.5, 66.5), (-30.5, 66.5), (-30.5, 93.5), (-57.5, 93.5), (-57.5, 66.5)], Z),
    "SALA_R2_VOLTA": ([(-19.5, 62.5), (15.5, 62.5), (15.5, 97.5), (-19.5, 97.5), (-19.5, 62.5)], Z),
    "SALA_R3_VOLTA": ([(26.5, 62.5), (61.5, 62.5), (61.5, 97.5), (26.5, 97.5), (26.5, 62.5)], Z),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ colisao com folga dos minerios
_ORES = [(x, y) for room, kind, i, x, y, r in L.dun_ore_points()]
_SKIP = []


def _clear(p0, p1, rad=5.0):
    x0, x1 = sorted((p0[0], p1[0]))
    y0, y1 = sorted((p0[1], p1[1]))
    z0, z1 = sorted((p0[2], p1[2]))
    if z1 <= Z or z0 >= Z + 12.0:
        return True
    for x, y in _ORES:
        dx = max(x0 - x, 0.0, x - x1)
        dy = max(y0 - y, 0.0, y - y1)
        if math.hypot(dx, dy) < rad:
            return False
    return True


def ccol(area, p0, p1):
    """caixa de colisao; nas salas so se ficar a >= 5 de todo DUN_ORE (senao fica so o visual e avisa)"""
    if not _clear(p0, p1):
        _SKIP.append((area, tuple(round(v, 1) for v in p0)))
        return None
    return col_box2(area, p0, p1)


# ------------------------------------------------------------------ referencial de uma face de parede
class Face:
    """face plana de parede: s = coordenada ao longo (x se horiz, y se nao), d = distancia a partir da face no sentido
    'sign' (para dentro da sala ou para fora da torre), h = altura acima de z0"""

    def __init__(self, horiz, plane, sign, z0):
        self.hz, self.pl, self.sg, self.z0 = horiz, plane, sign, z0

    def p(self, s, d, h):
        if self.hz:
            return (s, self.pl + self.sg * d, self.z0 + h)
        return (self.pl + self.sg * d, s, self.z0 + h)

    def v(self, s, d, h):
        return Vector(self.p(s, d, h))

    def n(self):
        return Vector((0.0, self.sg, 0.0)) if self.hz else Vector((self.sg, 0.0, 0.0))

    def u(self):
        return Vector((1.0, 0.0, 0.0)) if self.hz else Vector((0.0, 1.0, 0.0))


def fbox(mb, F, s0, s1, d0, d1, h0, h1, m, bev=0.0):
    mb.box2(F.p(s0, d0, h0), F.p(s1, d1, h1), m, bev)


def fcol(area, F, s0, s1, d0, d1, h0, h1):
    return ccol(area, F.p(s0, d0, h0), F.p(s1, d1, h1))


def fcyl(mb, F, s, d, h0, h1, r, m, n=8, r2=None):
    mb.cyl(r, h1 - h0, F.p(s, d, (h0 + h1) / 2.0), m=m, n=n, r2=r2, bevel=0.0)


# ------------------------------------------------------------------ ogivas (arco quebrado) no plano da parede
def _ogive_center(hw, rise):
    xc = (hw * hw - rise * rise) / (2.0 * hw)
    c = min(xc, -0.25 * hw)
    zc = (rise * rise - hw * hw + 2.0 * hw * c) / (2.0 * rise)
    return c, zc, math.hypot(hw - c, zc)


def ogive_right(hw, rise, n):
    c, zc, R = _ogive_center(hw, rise)
    t0 = math.atan2(-zc, hw - c)
    ta = math.atan2(rise - zc, -c)
    pts = [(c + R * math.cos(t0 + (ta - t0) * k / n), zc + R * math.sin(t0 + (ta - t0) * k / n)) for k in range(n + 1)]
    pts[0] = (hw, 0.0)
    pts[-1] = (0.0, rise)
    return pts


def ogive(cs, hw, rise, spring, n=6):
    r = ogive_right(hw, rise, n)
    return [(cs - u, spring + v) for u, v in r] + [(cs + u, spring + v) for u, v in reversed(r)][1:]


def ogive_z(hw, rise, u):
    c, zc, R = _ogive_center(hw, rise)
    return max(0.0, zc + math.sqrt(max(0.0, R * R - (abs(u) - c) ** 2)))


def band(mb, F, inner, outer, d0, d1, m, closed=False):
    """faixa solida no plano da parede entre duas polilinhas (s, h) do mesmo tamanho"""
    bm = mb.bm
    n = len(inner)
    iF = [bm.verts.new(F.p(s, d1, h)) for s, h in inner]
    iB = [bm.verts.new(F.p(s, d0, h)) for s, h in inner]
    oF = [bm.verts.new(F.p(s, d1, h)) for s, h in outer]
    oB = [bm.verts.new(F.p(s, d0, h)) for s, h in outer]
    for i in (range(n) if closed else range(n - 1)):
        j = (i + 1) % n
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    if not closed:
        for k in (0, n - 1):
            bm.faces.new((iF[k], oF[k], oB[k], iB[k]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def slab(mb, F, pts, d0, d1, m):
    """placa no plano da parede (poligono CONVEXO (s, h))"""
    bm = mb.bm
    Fv = [bm.verts.new(F.p(s, d1, h)) for s, h in pts]
    Bv = [bm.verts.new(F.p(s, d0, h)) for s, h in pts]
    n = len(pts)
    bm.faces.new(Fv)
    bm.faces.new(list(reversed(Bv)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((Fv[j], Fv[i], Bv[i], Bv[j]))
    mb._post(Fv + Bv, m, None, 0, 1)


def spandrel(mb, F, corner, arc, d0, d1, m):
    """tampa entre um canto (s, h) e um trecho de arco (leque a partir do canto): o 'tímpano' ao lado da ogiva"""
    bm = mb.bm
    cF, cB = bm.verts.new(F.p(corner[0], d1, corner[1])), bm.verts.new(F.p(corner[0], d0, corner[1]))
    aF = [bm.verts.new(F.p(s, d1, h)) for s, h in arc]
    aB = [bm.verts.new(F.p(s, d0, h)) for s, h in arc]
    for i in range(len(arc) - 1):
        bm.faces.new((cF, aF[i], aF[i + 1]))
        bm.faces.new((cB, aB[i + 1], aB[i]))
        bm.faces.new((aF[i], aB[i], aB[i + 1], aF[i + 1]))
    bm.faces.new((cF, cB, aB[0], aF[0]))
    bm.faces.new((cF, aF[-1], aB[-1], cB))
    mb._post([cF, cB] + aF + aB, m, None, 0, 1)


def arch_band(mb, F, cs, hw, rise, spring, foot, t, d0, d1, m, n=6):
    inner = [(cs - hw, foot)] + ogive(cs, hw, rise, spring, n) + [(cs + hw, foot)]
    outer = [(cs - hw - t, foot)] + ogive(cs, hw + t, rise + t, spring, n) + [(cs + hw + t, foot)]
    band(mb, F, inner, outer, d0, d1, m)


def arch_panel(mb, F, cs, hw, rise, spring, foot, d0, d1, m, n=6):
    slab(mb, F, [(cs - hw, foot)] + ogive(cs, hw, rise, spring, n) + [(cs + hw, foot)], d0, d1, m)




def wall_ogive_opening(mb, F, s0, s1, cs, hw, spring, rise, top, d0, d1, m, n=6):
    """pano de parede de s0..s1 x 0..top com um vao ogival (retangulo ate 'spring' + ogiva) centrado em cs"""
    fbox(mb, F, s0, cs - hw, d0, d1, -0.5, top, m)
    fbox(mb, F, cs + hw, s1, d0, d1, -0.5, top, m)
    fbox(mb, F, cs - hw, cs + hw, d0, d1, spring + rise, top, m)
    r = ogive_right(hw, rise, n)
    spandrel(mb, F, (cs - hw, spring + rise), [(cs - u, spring + v) for u, v in r], d0, d1, m)
    spandrel(mb, F, (cs + hw, spring + rise), [(cs + u, spring + v) for u, v in r], d0, d1, m)


def tri_prism(mb, F, pts, d0, d1, m):
    slab(mb, F, pts, d0, d1, m)


# ------------------------------------------------------------------ pecas do sistema (laminas, runas, correntes)
def obox3(mb, c, ax, ay, az, sx, sy, sz, m):
    """caixa orientada: centro c, eixos (unitarios) ax, ay, az e medidas ao longo deles"""
    c = Vector(c)
    hx, hy, hz = ax * (sx / 2.0), ay * (sy / 2.0), az * (sz / 2.0)
    bm = mb.bm
    V = {}
    for i in (0, 1):
        for j in (0, 1):
            for k in (0, 1):
                V[i, j, k] = bm.verts.new(c + hx * (2 * i - 1) + hy * (2 * j - 1) + hz * (2 * k - 1))
    for f in (((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)), ((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1)),
              ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)), ((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0)),
              ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))):
        bm.faces.new([V[q] for q in f])
    mb._post(list(V.values()), m, None, 0, 1)


def blade(mb, base, dirv, side, fwd, L_, w, th, m, curl=0.0, ridge=None):
    """lamina/espinho de obsidiana: base w x th, ombro a 45% (afinando) e ponta; curl = desvio lateral (garra);
    ridge = material de um fio (energia) na lombada da face da frente (le a silhueta de noite)"""
    base, dirv, side, fwd = Vector(base), Vector(dirv).normalized(), Vector(side).normalized(), Vector(fwd).normalized()
    mid = base + dirv * (L_ * 0.45) + side * (w * curl)
    tip = base + dirv * L_ + side * (w * curl * 1.6)
    bm = mb.bm
    sq = ((-1, -1), (1, -1), (1, 1), (-1, 1))
    B = [bm.verts.new(base + side * (a * w / 2) + fwd * (b * th / 2)) for a, b in sq]
    M = [bm.verts.new(mid + side * (a * w * 0.3) + fwd * (b * th * 0.32)) for a, b in sq]
    T = bm.verts.new(tip)
    bm.faces.new(list(reversed(B)))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((B[i], B[j], M[j], M[i]))
        bm.faces.new((M[i], M[j], T))
    mb._post(B + M + [T], m, None, 0, 1)
    if ridge:
        a = base + fwd * (th / 2 + 0.02)
        b = mid + fwd * (th * 0.32 + 0.02)
        c = base.lerp(tip, 0.86) + fwd * 0.04
        for p0, p1, wd in ((a, b, 0.26), (b, c, 0.2)):
            ax = (p1 - p0).normalized()
            obox3(mb, (p0 + p1) / 2, ax, side, ax.cross(side).normalized(), (p1 - p0).length + 0.1, wd, 0.1, ridge)


# runas da ordem: UM alfabeto angular (7 glifos) usado em monolitos, portal, pedestais e pisos das salas (sistema)
GLYPHS = [
    [((0, 0), (0, 1.4)), ((0, 1.0), (0.5, 1.4)), ((0, 0.55), (0.5, 0.95))],
    [((0, 0), (0, 1.4)), ((0, 1.4), (0.5, 1.0)), ((0.5, 1.0), (0, 0.6))],
    [((-0.45, 0), (0.45, 1.4)), ((0.45, 0), (-0.45, 1.4))],
    [((0, 0), (0, 1.4)), ((-0.5, 0.9), (0, 1.4)), ((0.5, 0.9), (0, 1.4))],
    [((-0.4, 0), (-0.4, 1.4)), ((0.4, 0), (0.4, 1.4)), ((-0.4, 1.4), (0.4, 0.7))],
    [((0, 0), (0, 1.4)), ((-0.5, 0.3), (0.5, 1.1))],
    [((0, 0.15), (0.45, 0.7)), ((0.45, 0.7), (0, 1.25)), ((0, 1.25), (-0.45, 0.7)), ((-0.45, 0.7), (0, 0.15))],
]


def glyph(mb, o, ea, eb, en, k, sc, m=RG, dep=0.12, w=0.22):
    """glifo k (base-centro o) no plano (ea lateral, eb 'cima'), saltado 'dep' ao longo da normal en"""
    o, ea, eb, en = Vector(o), Vector(ea), Vector(eb), Vector(en)
    for (a0, b0), (a1, b1) in GLYPHS[k % len(GLYPHS)]:
        p0 = o + ea * (a0 * sc) + eb * (b0 * sc)
        p1 = o + ea * (a1 * sc) + eb * (b1 * sc)
        d = p1 - p0
        ax = d.normalized()
        ay = en.cross(ax).normalized()
        obox3(mb, (p0 + p1) / 2 + en * (dep / 2), ax, ay, en, d.length + w, w, dep, m)


def chain(mb, p0, p1, sag, m=BI, pitch=0.66):
    """corrente de ferro negro em catenaria (parabola): elos VAZADOS (4 barras) alternando deitado/em pe"""
    p0, p1 = Vector(p0), Vector(p1)
    n = max(3, int((p1 - p0).length / pitch))
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(p0.lerp(p1, t) + Vector((0.0, 0.0, -4.0 * sag * t * (1.0 - t))))
    hw, wr = 0.26, 0.2
    for i in range(n):
        a, b = pts[i], pts[i + 1]
        ax = (b - a).normalized()
        hl = (b - a).length * 0.5 + 0.13
        s0 = ax.cross(Vector((0.0, 0.0, 1.0))).normalized()
        s = s0 if i % 2 == 0 else ax.cross(s0).normalized()
        nn = ax.cross(s).normalized()
        c = (a + b) / 2
        for sg in (-1, 1):
            obox3(mb, c + s * (sg * hw), ax, s, nn, 2 * hl, wr, wr, m)
            obox3(mb, c + ax * (sg * (hl - wr / 2)), s, ax, nn, 2 * hw + wr, wr, wr, m)


# ------------------------------------------------------------------ KIT (portaria e salas usam as mesmas pecas)
PIL_D, PIL_HW = 1.5, 1.5


def pilaster(mb, F, s, top, area=None):
    """pilastra engastada: plinto, fuste + colunelo frontal, capitel (arranque da abobada em 'top')"""
    fbox(mb, F, s - PIL_HW - 0.3, s + PIL_HW + 0.3, 0.0, PIL_D + 0.3, 0.0, 1.0, TR, 0.08)
    fbox(mb, F, s - PIL_HW, s + PIL_HW, 0.0, PIL_D, 1.0, top - 0.9, CS, 0.06)
    fcyl(mb, F, s, PIL_D, 1.0, top - 0.9, 0.45, CS, 8)
    fbox(mb, F, s - PIL_HW - 0.25, s + PIL_HW + 0.25, 0.0, PIL_D + 0.45, top - 0.9, top, TR, 0.08)
    if area:
        fcol(area, F, s - PIL_HW - 0.3, s + PIL_HW + 0.3, 0.0, PIL_D + 0.3, -0.5, top)


def corner_col(mb, F, s, sgn, top, area=None):
    """coluna de canto (ocupa o canto das duas paredes): s = canto, sgn = para onde ela cresce ao longo da face F"""
    a, b = sorted((s, s + sgn * 2.4))
    a2, b2 = sorted((s, s + sgn * 2.7))
    fbox(mb, F, a2, b2, 0.0, 2.7, 0.0, 1.0, TR, 0.08)
    fbox(mb, F, a, b, 0.0, 2.4, 1.0, top - 0.9, CS, 0.06)
    fbox(mb, F, a2, b2, 0.0, 2.75, top - 0.9, top, TR, 0.08)
    if area:
        fcol(area, F, a2, b2, 0.0, 2.7, -0.5, top)


def blind_arch(mb, F, s0, s1, spring=7.0, twin=False):
    """arco ogival cego (fundo navy + arquivolta clara) no vao entre duas pilastras; twin = arcada dupla"""
    fbox(mb, F, s0, s1, 0.0, 0.4, 0.0, 0.9, TR, 0.05)                 # rodape
    if twin:
        mid = (s0 + s1) / 2.0
        blind_arch(mb, F, s0, mid + 0.35, spring, False)
        blind_arch(mb, F, mid - 0.35, s1, spring, False)
        fbox(mb, F, mid - 0.45, mid + 0.45, 0.0, 0.7, 0.9, spring + 0.4, CS, 0.05)   # colunelo central
        return
    cs = (s0 + s1) / 2.0
    hw = (s1 - s0) / 2.0 - 0.8
    if hw < 1.2:
        return
    rise = min(hw * 1.15, 5.2)
    arch_panel(mb, F, cs, hw, rise, spring, 0.9, 0.0, 0.15, VA)
    arch_band(mb, F, cs, hw, rise, spring, 0.9, 0.55, 0.0, 0.5, TR)


def cornice(mb, F, s0, s1, h):
    if s1 - s0 > 0.3:
        fbox(mb, F, s0, s1, 0.0, 0.6, h - 0.6, h, TR, 0.05)


def torch(mb, F, s, d, h):
    """tocha de parede: mao-francesa de ferro, copo e chama (Neon quente)"""
    mb.beam(F.p(s, d, h - 1.4), F.p(s, d + 0.95, h - 0.25), 0.22, 0.22, IR, 0.0)
    mb.cyl(0.36, 0.5, F.p(s, d + 1.0, h), m=IR, n=6, r2=0.52, bevel=0.0)
    mb.cyl(0.3, 0.9, F.p(s, d + 1.0, h + 0.7), m=GL, n=6, r2=0.04, bevel=0.0)


def link_frame(mb, F, cs, hw_open):
    """moldura do vao de ligacao 12 x 12: verga clara + timpano ogival navy com o emblema da ordem"""
    fbox(mb, F, cs - hw_open - 1.3, cs + hw_open + 1.3, 0.0, 0.8, LINK_H, LINK_H + 1.2, TR, 0.06)
    th = hw_open + 0.6
    arch_panel(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.0, 0.15, VA)
    arch_band(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.7, 0.0, 0.6, TR)
    # emblema da ordem no timpano (substitui a estrela avulsa: um simbolo so)
    n = F.n()
    EM.plaque(mb, mb, mb, mb, F.p(cs, 0.6, LINK_H + 3.5), math.atan2(n.y, n.x), 1.25)


def tile_floor(mb, rect, z, tile=4.0, margin=1.0, friso=0.8, gap=0.25, skip=None):
    """piso de lajes escuras (topo EXATO em z) com friso claro junto as paredes; juntas mostram a base mais clara"""
    x0, y0, x1, y1 = rect
    mb.box2((x0, y0, z - 0.6), (x1, y1, z - 0.15), BL, 0.0)

    def ringbox(a, b, m):
        # anel entre o retangulo recuado 'a' e o recuado 'b' (a < b)
        ax0, ay0, ax1, ay1 = x0 + a, y0 + a, x1 - a, y1 - a
        bx0, by0, bx1, by1 = x0 + b, y0 + b, x1 - b, y1 - b
        mb.box2((ax0, ay0, z - 0.4), (ax1, by0, z), m, 0.0)
        mb.box2((ax0, by1, z - 0.4), (ax1, ay1, z), m, 0.0)
        mb.box2((ax0, by0, z - 0.4), (bx0, by1, z), m, 0.0)
        mb.box2((bx1, by0, z - 0.4), (ax1, by1, z), m, 0.0)
    ringbox(0.0, margin, FL)
    ringbox(margin, margin + friso, TR)
    ix0, iy0, ix1, iy1 = x0 + margin + friso, y0 + margin + friso, x1 - margin - friso, y1 - margin - friso
    nx = max(1, int(round((ix1 - ix0) / tile)))
    ny = max(1, int(round((iy1 - iy0) / tile)))
    tx, ty = (ix1 - ix0) / nx, (iy1 - iy0) / ny
    for i in range(nx):
        for j in range(ny):
            ax, ay = ix0 + i * tx, iy0 + j * ty
            if skip and skip(ax + tx / 2, ay + ty / 2):
                continue
            mb.box2((ax + gap / 2, ay + gap / 2, z - 0.4), (ax + tx - gap / 2, ay + ty - gap / 2, z), FL, 0.0)


# ------------------------------------------------------------------ abobada ogival de bercos + nervuras
def _vault_map(rect, axis):
    x0, y0, x1, y1 = rect
    if axis == "x":
        yc, hw = (y0 + y1) / 2.0, (y1 - y0) / 2.0
        return (x0, x1), hw, (lambda a, u: (a, yc + u))
    xc, hw = (x0 + x1) / 2.0, (x1 - x0) / 2.0
    return (y0, y1), hw, (lambda a, u: (xc + u, a))


def vault_z(rect, axis, zf, spring, crown, u):
    _, hw, _ = _vault_map(rect, axis)
    return zf + spring + ogive_z(hw, crown - spring, u)


def vault(mb, rect, axis, zf, spring, crown, ribs=(), nseg=18):
    """berco ogival (arranque 'spring', fecho 'crown' acima de zf) ao longo de 'axis'; nervuras transversais nos
    valores de 'ribs' (coordenada ao longo do eixo), nervuras de testa nas duas pontas e cumeeira"""
    (a0, a1), hw, mp = _vault_map(rect, axis)
    rise = crown - spring
    bm = mb.bm
    us = [-hw + 2 * hw * (0.5 - 0.5 * math.cos(math.pi * k / nseg)) for k in range(nseg + 1)]

    def zz(u):
        return zf + spring + ogive_z(hw, rise, u)
    lo = [[bm.verts.new((*mp(a, u), zz(u))) for u in us] for a in (a0, a1)]
    hi = [[bm.verts.new((*mp(a, u), zz(u) + 0.35)) for u in us] for a in (a0, a1)]
    n = len(us)
    for i in range(n - 1):
        bm.faces.new((lo[0][i], lo[0][i + 1], lo[1][i + 1], lo[1][i]))
        bm.faces.new((hi[0][i], hi[1][i], hi[1][i + 1], hi[0][i + 1]))
        for k in (0, 1):
            bm.faces.new((lo[k][i], hi[k][i], hi[k][i + 1], lo[k][i + 1]))
    for i in (0, n - 1):
        bm.faces.new((lo[0][i], lo[1][i], hi[1][i], hi[0][i]))
    mb._post([v for r in lo + hi for v in r], VA, None, 0, 1)
    prof = [(-0.45, 0.12), (0.45, 0.12), (0.45, -0.8), (-0.45, -0.8)]
    prof_w = [(-0.35, 0.12), (0.35, 0.12), (0.35, -0.6), (-0.35, -0.6)]
    ue = [-hw + 0.3 + (2 * hw - 0.6) * (0.5 - 0.5 * math.cos(math.pi * k / 20)) for k in range(21)]

    def rib(a, pr):
        mb.sweep([(*mp(a, u), zz(u) - 0.02) for u in ue], pr, TR)
    for a in ribs:
        rib(a, prof)
    rib(a0 + 0.4, prof_w)
    rib(a1 - 0.4, prof_w)
    mb.sweep([(*mp(a0 + 0.4, 0.0), zz(0.0) - 0.02), (*mp(a1 - 0.4, 0.0), zz(0.0) - 0.02)], prof, TR)
    for a in ribs:
        x, y = mp(a, 0.0)
        mb.cyl(0.95, 0.7, (x, y, zz(0.0) - 0.95), m=TR, n=8, bevel=0.0)


# ------------------------------------------------------------------ portal (anel com runas + disco + espiral)
def _pl(c, u, v, n, a, r, d):
    return c + u * (math.cos(a) * r) + v * (math.sin(a) * r) + n * d


def ring3(mb, c, u, v, n, r0, r1, d0, d1, m, seg=28):
    bm = mb.bm
    A = [2 * math.pi * k / seg for k in range(seg)]
    iF = [bm.verts.new(_pl(c, u, v, n, a, r0, d1)) for a in A]
    iB = [bm.verts.new(_pl(c, u, v, n, a, r0, d0)) for a in A]
    oF = [bm.verts.new(_pl(c, u, v, n, a, r1, d1)) for a in A]
    oB = [bm.verts.new(_pl(c, u, v, n, a, r1, d0)) for a in A]
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def disc3(mb, c, u, v, n, r, d0, d1, m, seg=28):
    bm = mb.bm
    A = [2 * math.pi * k / seg for k in range(seg)]
    Fv = [bm.verts.new(_pl(c, u, v, n, a, r, d1)) for a in A]
    Bv = [bm.verts.new(_pl(c, u, v, n, a, r, d0)) for a in A]
    bm.faces.new(Fv)
    bm.faces.new(list(reversed(Bv)))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((Fv[j], Fv[i], Bv[i], Bv[j]))
    mb._post(Fv + Bv, m, None, 0, 1)


def spiral(mb, c, u, v, n, R, d0, d1, m, arms=5, twist=2.7, seg=14, a0=0.0):
    """bracos da espiral (fitas que afinam nas pontas) + nucleo"""
    bm = mb.bm
    for k in range(arms):
        th0 = a0 + 2 * math.pi * k / arms
        LF, RF, LB, RB = [], [], [], []
        for i in range(seg + 1):
            t = i / seg
            r = 0.7 + (R - 0.7) * t
            th = th0 + twist * t
            w = 0.28 + 1.7 * t * (1.0 - t)
            dl = (w / 2.0) / r
            LF.append(bm.verts.new(_pl(c, u, v, n, th - dl, r, d1)))
            RF.append(bm.verts.new(_pl(c, u, v, n, th + dl, r, d1)))
            LB.append(bm.verts.new(_pl(c, u, v, n, th - dl, r, d0)))
            RB.append(bm.verts.new(_pl(c, u, v, n, th + dl, r, d0)))
        for i in range(seg):
            bm.faces.new((LF[i], RF[i], RF[i + 1], LF[i + 1]))
            bm.faces.new((LB[i + 1], RB[i + 1], RB[i], LB[i]))
            bm.faces.new((LF[i + 1], LB[i + 1], LB[i], LF[i]))
            bm.faces.new((RF[i], RB[i], RB[i + 1], RF[i + 1]))
        bm.faces.new((LF[0], LB[0], RB[0], RF[0]))
        bm.faces.new((RF[-1], RB[-1], LB[-1], LF[-1]))
        mb._post(LF + RF + LB + RB, m, None, 0, 1)
    disc3(mb, c, u, v, n, 1.0, d0, d1 + 0.05, m, 12)


def obox(mb, c, u, v, n, su, sv, sn, m, bev=0.0):
    """caixa centrada em c com medidas ao longo de u, v, n (eixos alinhados ao mundo)"""
    h = u * (su / 2) + v * (sv / 2) + n * (sn / 2)
    ext = Vector((abs(h.x), abs(h.y), abs(h.z)))
    mb.box2(c - ext, c + ext, m, bev)


def portal_frame(mb, c, u, v, n, r_in, r_out, floor_z):
    """anel de pedra (cantaria clara com runas de prata + coroa escura), chave com estrela e pes"""
    v3 = Vector
    ring3(mb, c, u, v, n, r_in, r_in + 0.9, -0.6, 0.7, TR)
    ring3(mb, c, u, v, n, r_in + 0.9, r_out, -0.6, 0.35, CS)
    # runas: 16 barrinhas de prata no aro claro (radiais e tangenciais alternadas)
    rr = r_in + 0.45
    for k in range(16):
        a = 2 * math.pi * (k + 0.5) / 16
        p = _pl(c, u, v, n, a, rr, 0.72)
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        dirv = radial if k % 2 == 0 else tang
        ln = 0.55 if k % 2 == 0 else 0.4
        mb.beam(p - dirv * ln, p + dirv * ln, 0.22, 0.2, SV, 0.0)
    # chave (topo) e pes (base) do anel
    top = c + v * (r_out - 0.2)
    obox(mb, top + n * 0.1, u, v, n, 1.6, 1.8, 1.6, TR, 0.08)
    obox(mb, top + n * 0.95, u, v, n, 0.5, 0.6, 0.5, SV)
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        h = p.z + 0.4 - floor_z
        obox(mb, v3((p.x, p.y, floor_z + h / 2)), u, v, n, 2.2, h, 2.0, CS, 0.08)


# ------------------------------------------------------------------ guardiao encapuzado (generico) e braseiro
def guardian(mb, x, y, z, ang):
    """guardiao encapuzado generico (sem personagem): manto em sino, capa, capuz com a ponta caida para tras e o
    rosto em sombra, maos no pomo da espada cravada no pedestal"""
    F = SL.Frame(x, y, z, ang)
    mb.box((2.8, 2.8, 1.4), F.p(0, 0, 0.7), F.r(), CS, 0.12)
    mb.box((3.1, 3.1, 0.3), F.p(0, 0, 1.55), F.r(), TR, 0.06)
    zb = 1.7
    mb.cyl(1.45, 4.6, F.p(0, -0.1, zb + 2.3), F.r(), m=ST, n=8, r2=1.05)                       # manto
    mb.cyl(1.55, 1.5, F.p(0, -0.15, zb + 5.0), F.r(), m=ST, n=8, r2=0.85)                      # capa (ombros caidos)
    mb.cyl(0.95, 1.5, F.p(0, -0.05, zb + 6.35), F.r(-0.12, 0, 0), m=ST, n=8, r2=0.62)          # capuz
    mb.cyl(0.62, 1.3, F.p(0, -0.45, zb + 7.45), F.r(0.55, 0, 0), m=ST, n=8, r2=0.05)           # ponta do capuz
    mb.box((0.72, 0.3, 0.95), F.p(0, 0.76, zb + 6.2), F.r(-0.12, 0, 0), VA, 0.0)               # rosto em sombra
    for sx in (-1, 1):
        mb.beam(F.p(sx * 0.95, 0.15, zb + 4.75), F.p(sx * 0.3, 1.05, zb + 3.35), 0.7, 0.7, ST, 0.1)   # mangas
    mb.box((1.05, 0.75, 0.62), F.p(0, 1.15, zb + 3.3), F.r(), ST, 0.12)                        # maos
    mb.box((0.36, 0.36, 0.36), F.p(0, 1.22, zb + 3.8), F.r(0, 0, math.pi / 4), SV, 0.0)         # pomo
    mb.box((1.9, 0.3, 0.3), F.p(0, 1.25, zb + 2.8), F.r(), SV, 0.0)                             # guarda
    mb.box((0.42, 0.2, 2.65), F.p(0, 1.25, zb + 1.33), F.r(), SV, 0.0)                          # lamina


def brazier(mb, x, y, z):
    mb.box((1.9, 1.9, 0.5), (x, y, z + 0.25), (0, 0, 0), TR, 0.08)
    mb.cyl(0.62, 2.3, (x, y, z + 1.65), m=CS, n=8, bevel=0.0)
    mb.cyl(0.9, 0.3, (x, y, z + 2.95), m=TR, n=8, bevel=0.0)
    mb.cyl(0.75, 0.8, (x, y, z + 3.5), m=IR, n=8, r2=1.3, bevel=0.0)
    mb.cyl(1.12, 0.22, (x, y, z + 3.8), m=GL, n=8, bevel=0.0)
    flame(mb, x, y, z + 3.85, GL, 0.8)                                                   # chama (mesmo desenho)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        mb.beam((x + 0.5 * math.cos(a), y + 0.5 * math.sin(a), z + 2.9),
                (x + 1.25 * math.cos(a), y + 1.25 * math.sin(a), z + 3.9), 0.2, 0.2, IR, 0.0)




def chandelier(mb, x, y, h, top, r=3.0, n=8):
    """lustre de ferro (aro + raios + velas) pendurado da abobada: h = altura do aro, top = z da nervura"""
    ring_lo = [(x + r * math.cos(2 * math.pi * k / 16), y + r * math.sin(2 * math.pi * k / 16), h) for k in range(17)]
    mb.tube(ring_lo, 0.2, IR, 6)
    mb.cyl(0.45, 2.6, (x, y, h + 1.1), m=IR, n=8, r2=0.25, bevel=0.0)
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        ca, sa = math.cos(a), math.sin(a)
        mb.beam((x + 0.3 * ca, y + 0.3 * sa, h + 2.0), (x + r * ca, y + r * sa, h), 0.2, 0.2, IR, 0.0)
        mb.cyl(0.32, 0.3, (x + r * ca, y + r * sa, h + 0.25), m=IR, n=6, bevel=0.0)
        mb.cyl(0.2, 0.7, (x + r * ca, y + r * sa, h + 0.75), m=GL, n=6, bevel=0.0)
    mb.rod((x, y, h + 2.4), (x, y, top), 0.13, IR, 6)


# ==================================================================== PORTARIA (superficie)
def house_shell():
    """corpo externo: paredes (vao ogival da porta), plinto/cinta/cornija de obsidiana, coroamento de DENTES negros
    irregulares, torrinhas com AGULHAS negras + laminas, contrafortes, FENDAS violeta no andar alto, agulha central negra
    com fendas; a face sul recebe a FACHADA-PORTAL (facade_portal)"""
    mb = MB("SG_Dun_House_Body", "17_DUNGEON", random.Random(701), detail="near")
    rng = random.Random(709)
    FS, FN = Face(True, HY0, -1, P3), Face(True, HY1, 1, P3)
    FW, FE = Face(False, HX0, -1, P3), Face(False, HX1, 1, P3)
    # paredes (a de sul com o vao ogival 10 x 14)
    wall_ogive_opening(mb, FS, HX0, HX1, HX, DW / 2, D_SPR, D_RISE, BODY, -HT, 0.0, CS)
    fbox(mb, FN, HX0, HX1, -HT, 0.0, -0.5, BODY, CS)
    fbox(mb, FW, IY0, IY1, -HT, 0.0, -0.5, BODY, CS)
    fbox(mb, FE, IY0, IY1, -HT, 0.0, -0.5, BODY, CS)
    pw = order_hw(3) + P_T + 0.2                   # meia-largura do portal (a cinta e o plinto param nele)
    # soco alto de obsidiana, cinta (h 16) de obsidiana e cornija negra com misulas em todas as faces
    for F, (a, b) in ((FS, (HX0, HX1)), (FN, (HX0, HX1)), (FW, (HY0, HY1)), (FE, (HY0, HY1))):
        spans = ((a, HX - pw), (HX + pw, b)) if F is FS else ((a, b),)
        for s0, s1 in spans:
            if s1 - s0 > 0.3:
                fbox(mb, F, s0, s1, 0.0, 0.55, -0.5, 2.6, OB, 0.08)
                fbox(mb, F, s0, s1, 0.0, 0.5, 15.6, 16.4, OB, 0.05)
        fbox(mb, F, a + 3.0, b - 3.0, 0.0, 0.9, 33.0, 34.2, OB, 0.08)
        s = a + 4.0
        while s <= b - 3.9:
            fbox(mb, F, s - 0.45, s + 0.45, 0.0, 0.75, 31.4, 33.0, OB, 0.05)
            s += 2.7
        # parapeito + DENTES de obsidiana de alturas irregulares (coroa quebrada); na face sul o miolo fica livre para
        # a coroa de laminas do portal furar o ceu
        fbox(mb, F, a + 3.2, b - 3.2, -0.4, 0.9, 34.2, 35.6, CS, 0.05)
        s = a + 4.6
        while s <= b - 4.2:
            if not (F is FS and abs(s - HX) < 8.0):
                ht = rng.uniform(1.6, 3.6) + (1.3 if (s < a + 5.0 or s > b - 7.0) else 0.0)
                sk = rng.uniform(-0.35, 0.35)
                slab(mb, F, [(s - 0.75, 35.6), (s + 0.75, 35.6), (s + sk, 35.6 + ht)], -0.4, 0.9, OB)
            s += 2.8
    # contrafortes (meio das faces leste, oeste e norte), FENDAS violeta no andar alto e arcada cega baixa
    for F, c in ((FE, HY), (FW, HY), (FN, HX)):
        fbox(mb, F, c - 1.6, c + 1.6, 0.0, 1.4, -0.5, 16.4, CS, 0.08)
        fbox(mb, F, c - 1.8, c + 1.8, 0.0, 1.6, 16.0, 16.8, OB, 0.06)
        fbox(mb, F, c - 1.25, c + 1.25, 0.0, 0.9, 16.8, 31.4, CS, 0.08)
        blade(mb, F.v(c, 0.45, 31.2), Vector((0, 0, 1)) + F.n() * 0.25, F.u(), F.n(), 4.2, 1.6, 0.9, OB)
        for k in (-1, 1):
            cs = c + k * 5.0
            arch_panel(mb, F, cs, 0.6, 1.8, 28.0, 19.0, 0.0, 0.12, VD)
            arch_band(mb, F, cs, 0.6, 1.8, 28.0, 19.0, 0.55, 0.0, 0.5, OB)
            fbox(mb, F, cs - 1.6, cs + 1.6, 0.0, 0.7, 18.5, 19.0, OB, 0.05)
            # arcada cega baixa (quebra a massa ao nivel do jogador, 360 graus): moldura de pedra violeta
            arch_panel(mb, F, cs + k * 1.5, 2.8, 3.0, 8.4, 2.6, 0.0, 0.12, VA)
            arch_band(mb, F, cs + k * 1.5, 2.8, 3.0, 8.4, 2.6, 0.5, 0.0, 0.45, VS)
    # torrinhas de canto: faixas negras, FENDAS violeta e AGULHAS negras irregulares (agulha + 3 laminas inclinadas)
    tops = {(HX0, HY0): 15.5, (HX1, HY0): 13.0, (HX0, HY1): 12.0, (HX1, HY1): 16.5}
    for (cx, cy), hm in tops.items():
        mb.cyl(TURRET_R, 40.5, (cx, cy, P3 + 19.75), m=CS, n=8, bevel=0.0)
        for h0, h1, r in ((-0.5, 2.6, TURRET_R + 0.4), (15.6, 16.4, TURRET_R + 0.3), (33.0, 34.2, TURRET_R + 0.4),
                          (39.4, 40.6, TURRET_R + 0.6)):
            mb.cyl(r, h1 - h0, (cx, cy, P3 + (h0 + h1) / 2), m=OB, n=8, bevel=0.0)
        SL.spire(mb, (cx, cy), TURRET_R + 0.7, P3 + 40.6, hm, OB, n=6)
        a = math.atan2(cy - HY, cx - HX)
        for j, (da, ln) in enumerate(((-1.25, 6.0), (0.0, 7.6), (1.25, 5.0))):
            aa = a + da
            ro = Vector((math.cos(aa), math.sin(aa), 0.0))
            base = Vector((cx, cy, P3 + 40.2)) + ro * (TURRET_R + 0.1)
            blade(mb, base, ro * 0.42 + Vector((0, 0, 1)), Vector((-ro.y, ro.x, 0.0)), ro, ln, 1.3, 1.1, OB,
                  curl=0.15 * (j - 1))
        # fendas violeta voltadas para fora (diagonal)
        for h in (10.0, 24.0):
            mb.box((0.35, 0.5, 3.0), (cx + math.cos(a) * (TURRET_R - 0.1), cy + math.sin(a) * (TURRET_R - 0.1), P3 + h),
                   (0, 0, a), VD, 0.0)
        col_box2("SG_DunHouse", (cx - TURRET_R, cy - TURRET_R, P3 - 0.5), (cx + TURRET_R, cy + TURRET_R, P3 + 40.6))
    # cobertura: laje escura, agulha central NEGRA com fendas violeta nas 4 faces, lucarnas negras com fenda violeta
    mb.box2((HX0 + 0.6, HY0 + 0.6, P3 + 33.6), (HX1 - 0.6, HY1 - 0.6, P3 + 34.2), NAVY, 0.0)
    hs, zb, sh = 9.0, P3 + 34.2, 28.0
    mb.box2((HX - hs - 0.4, HY - hs - 0.4, zb), (HX + hs + 0.4, HY + hs + 0.4, zb + 0.8), OB, 0.05)
    SL.spire(mb, (HX, HY), hs * math.sqrt(2.0), zb + 0.8, sh, OB, n=4)
    apex = Vector((HX, HY, zb + 0.8 + sh))
    for F, c in ((FS, HX), (FN, HX), (FW, HY), (FE, HY)):
        n = F.n()
        b0 = Vector((HX, HY, zb + 0.8)) + n * hs
        p0, p1 = b0.lerp(apex, 0.30), b0.lerp(apex, 0.74)
        ax = (p1 - p0).normalized()
        nf = F.u().cross(ax).normalized()
        if nf.dot(n) < 0:
            nf = -nf
        obox3(mb, (p0 + p1) / 2 + nf * 0.05, ax, F.u(), nf, (p1 - p0).length, 0.55, 0.2, VD)
    mb.rod((HX, HY, zb + 0.8 + sh - 0.5), (HX, HY, zb + sh + 5.0), 0.2, SV, 6)
    mb.box((0.9, 0.9, 0.9), (HX, HY, zb + sh + 3.2), (0.6, 0.6, 0.0), SV, 0.0)
    for F, c in ((FS, HX), (FN, HX), (FW, HY), (FE, HY)):
        h0 = 4.2
        hsx = hs * (1.0 - (h0 + 0.8 - 1.0) / sh)        # meia-largura da agulha na base da lucarna
        dfront = hsx - HW / 2 + 0.6                       # d (para fora da face da torre) da frente da lucarna
        fbox(mb, F, c - 1.7, c + 1.7, dfront - 3.5, dfront, BODY + h0, BODY + h0 + 3.6, OB, 0.05)
        tri_prism(mb, F, [(c - 2.2, BODY + h0 + 3.6), (c + 2.2, BODY + h0 + 3.6), (c, BODY + h0 + 7.0)],
                  dfront - 3.5, dfront + 0.3, OB)
        fbox(mb, F, c - 0.4, c + 0.4, dfront, dfront + 0.1, BODY + h0 + 0.5, BODY + h0 + 3.1, VD, 0.0)
    mb.finish()
    facade_portal()
    # colisao das paredes da portaria (vao 10 x 14 + cantos da ogiva) e teto interno
    ccol("SG_DunHouse", (HX0, HY0, P3 - 0.5), (HX - DW / 2, IY0, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX + DW / 2, HY0, P3 - 0.5), (HX1, IY0, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX - DW / 2, HY0, P3 + DH), (HX + DW / 2, IY0, P3 + BODY + 3.2))
    zc = D_SPR + ogive_z(DW / 2, D_RISE, DW / 2 - 1.4)
    for s0, s1 in ((HX - DW / 2, HX - DW / 2 + 1.4), (HX + DW / 2 - 1.4, HX + DW / 2)):
        ccol("SG_DunHouse", (s0, HY0, P3 + zc), (s1, IY0, P3 + DH))
    ccol("SG_DunHouse", (HX0, IY1, P3 - 0.5), (HX1, HY1, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (HX0, IY0, P3 - 0.5), (IX0, IY1, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (IX1, IY0, P3 - 0.5), (HX1, IY1, P3 + BODY + 3.2))
    ccol("SG_DunHouse", (IX0, IY0, P3 + IN_CEIL), (IX1, IY1, P3 + IN_CEIL + 2.0))


def _vortex_fit():
    """maior anel (raio externo) que cabe no timpano, acima da lapide e dentro do intradorso da arquivolta 0"""
    r = 4.4
    top = P_SPR + P_RISE0
    while r > 1.5:
        hc = TAB_H1 + 0.25 + r
        while hc + r < top - 0.2:
            ok = True
            for i in range(-12, 13):
                dy = r * i / 12.0
                if math.sqrt(max(0.0, r * r - dy * dy)) > o0_half(hc + dy) - 0.08:
                    ok = False
                    break
            if ok:
                return r, hc
            hc += 0.05
        r -= 0.05
    return 2.0, TAB_H1 + 2.5


def _arc_at(pts, f):
    """ponto e tangente (unitaria) a uma fracao f do comprimento de uma polilinha 2D"""
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    t = f * cum[-1]
    for i in range(len(pts) - 1):
        if cum[i + 1] >= t:
            a, b = pts[i], pts[i + 1]
            L_ = max(1e-6, cum[i + 1] - cum[i])
            k = (t - cum[i]) / L_
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k), ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)
    a, b = pts[-2], pts[-1]
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    return b, ((b[0] - a[0]) / L_, (b[1] - a[1]) / L_)


def facade_portal():
    """FACHADA-PORTAL: 4 arquivoltas ogivais escalonadas projetadas para o sul (violeta/obsidiana), costuras de energia,
    laminas de obsidiana no extradorso + coroa de laminas no fecho, emblema da ordem no fecho, timpano negro com o
    VORTICE (espiral gira: VFX_SGDUN_FacadeVortex), lapide da contagem (DUNGEON_UI), runas nas ombreiras"""
    mb = MB("SG_Dun_Portal_Front", "17_DUNGEON", random.Random(731), detail="near")
    F = Face(True, HY0, -1, P3)
    up = Vector((0.0, 0.0, 1.0))
    # 1. arquivoltas + bases altas + impostas (alternando a cor com a ordem)
    for k in range(4):
        hw, rise, dk = order_hw(k), order_rise(k), P_DEP[k]
        arch_band(mb, F, HX, hw, rise, P_SPR, 0.0, P_T, 0.0, dk, P_MAT[k], n=12)
        for sg in (-1, 1):
            s0, s1 = sorted((HX + sg * (hw - 0.05), HX + sg * (hw + P_T + 0.15)))
            fbox(mb, F, s0, s1, 0.0, dk + 0.25, -0.3, 2.6, OB, 0.08)
            fbox(mb, F, s0, s1, 0.0, dk + 0.2, P_SPR - 0.8, P_SPR, VS if P_MAT[k] == OB else OB, 0.06)
    # costuras de energia (0|1 e 2|3): o portal "vaza" violeta entre as pedras
    for k in (1,):
        x = P_T * k - 0.3
        arch_band(mb, F, HX, P_HW0 + x, P_RISE0 + x, P_SPR, 2.6, 0.3, 0.0, P_DEP[k - 1] + 0.06, VD, n=12)
    # 2. campo negro entre a porta e a arquivolta 0 (ombreiras + timpanos da ogiva da porta)
    for sg in (-1, 1):
        s0, s1 = sorted((HX + sg * (DW / 2), HX + sg * (P_HW0 + 0.05)))
        fbox(mb, F, s0, s1, 0.0, 0.2, -0.3, TAB_H0, OB)
        r = ogive_right(DW / 2, D_RISE, 6)
        spandrel(mb, F, (HX + sg * (P_HW0 - 0.2), TAB_H0), [(HX + sg * u, D_SPR + v) for u, v in r], 0.0, 0.2, OB)
    # 3. LAPIDE da contagem (o BillboardGui do DUNGEON_UI fica na frente dela): obsidiana, moldura de energia, campo
    #    de marmore negro
    w0, w1 = o0_half(TAB_H0), o0_half(TAB_H1)
    slab(mb, F, [(HX - w0, TAB_H0), (HX + w0, TAB_H0), (HX + w1, TAB_H1), (HX - w1, TAB_H1)], 0.0, 0.7, OB)
    fw = w1 - 0.55
    for s0, s1, h0, h1 in ((HX - fw, HX + fw, TAB_H0 + 0.35, TAB_H0 + 0.57),
                           (HX - fw, HX + fw, TAB_H1 - 0.57, TAB_H1 - 0.35),
                           (HX - fw, HX - fw + 0.22, TAB_H0 + 0.35, TAB_H1 - 0.35),
                           (HX + fw - 0.22, HX + fw, TAB_H0 + 0.35, TAB_H1 - 0.35)):
        fbox(mb, F, s0, s1, 0.7, 0.8, h0, h1, VD)
    fbox(mb, F, HX - fw + 0.22, HX + fw - 0.22, 0.7, 0.74, TAB_H0 + 0.57, TAB_H1 - 0.57, MBK)
    # 4. timpano (acima da lapide) + VORTICE
    og = ogive(HX, P_HW0, P_RISE0, P_SPR, 24)
    top = [(s, h) for s, h in og if h > TAB_H1 + 0.01]
    slab(mb, F, [(HX - w1, TAB_H1)] + top + [(HX + w1, TAB_H1)], 0.0, 0.2, OB)
    rr, hc = _vortex_fit()
    rd = rr - 0.55
    c = F.v(HX, 0.0, hc)
    u3, n3 = F.u(), F.n()
    ring3(mb, c, u3, up, n3, rd, rr, 0.15, 0.95, OB, seg=32)
    ring3(mb, c, u3, up, n3, rd - 0.22, rd, 0.15, 1.05, SV, seg=32)
    disc3(mb, c, u3, up, n3, rd, 0.2, 0.4, VO, 32)
    for k in range(12):
        a = 2 * math.pi * k / 12
        rad = u3 * math.cos(a) + up * math.sin(a)
        tng = u3 * -math.sin(a) + up * math.cos(a)
        obox3(mb, c + rad * ((rd + rr) / 2) + n3 * 0.98, rad, tng, n3, rr - rd - 0.16, 0.22, 0.1, RG)
    vf = MB("VFX_SGDUN_FacadeVortex", "12_VFX_HELPERS", random.Random(733), detail="near")
    spiral(vf, c, u3, up, n3, rd - 0.1, 0.4, 0.55, VG, arms=4, twist=2.4, seg=12, a0=0.3)
    ob = vf.finish()
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, -1.0, 0.0]
    ob["rpm"] = -7.0
    ob["vfx"] = "vortice da fachada (timpano do portal): gira ao contrario do portal interno"
    # 5. runas nas ombreiras (frente da ordem 2, as duas de pedra violeta)
    sm = order_hw(2) + P_T / 2
    for sg in (-1, 1):
        for i, h in enumerate((3.3, 5.2, 7.1)):
            glyph(mb, F.v(HX + sg * sm, P_DEP[2], h), F.u(), up, F.n(), 2 * i + (0 if sg < 0 else 3), 0.72)
    # 6. fecho: bloco negro + EMBLEMA da ordem
    fbox(mb, F, HX - 1.3, HX + 1.3, 0.0, P_DEP[3] + 0.1, P_SPR + P_RISE0 + 0.3, KEY_H + 1.9, OB, 0.06)
    EM.plaque(mb, mb, mb, mb, F.p(HX, P_DEP[3] + 0.6, KEY_H), -math.pi / 2, 2.1)
    # 7. LAMINAS de obsidiana no extradorso (so onde nao entram nas torrinhas) + coroa de laminas no fecho
    hw3, rs3 = order_hw(3) + P_T, order_rise(3) + P_T
    pts = ogive_right(hw3, rs3, 80)
    dc = P_DEP[3] * 0.55
    for sg in (-1, 1):
        for f, Lb, cu in ((0.46, 4.0, 0.0), (0.60, 5.8, 0.14), (0.73, 3.8, 0.0), (0.86, 6.6, -0.12)):
            (u, v), (tu, tv) = _arc_at(pts, f)
            if u > 9.7:
                continue
            nu, nv = tv, -tu                       # normal para fora do arco (lado direito)
            base = F.v(HX + sg * (u - 0.35 * nu), dc, P_SPR + v - 0.35 * nv)
            inpl = F.u() * (sg * nu) + up * nv
            side = F.u() * (sg * tu) + up * tv
            blade(mb, base, inpl * 0.55 + up * 0.65 + F.n() * 0.45, side, F.n(), Lb, 1.5, 1.4, OB, curl=cu * sg,
                  ridge=VD)
    apex = F.v(HX, dc + 0.6, P_SPR + rs3 - 0.6)
    for ang, Lb in ((0.0, 10.5), (-0.38, 7.2), (0.38, 7.2), (-0.8, 4.6), (0.8, 4.6)):
        d = F.u() * math.sin(ang) + up * math.cos(ang) + F.n() * 0.2
        blade(mb, apex + F.u() * (math.sin(ang) * 1.0), d, F.u() * math.cos(ang) - up * math.sin(ang), F.n(), Lb,
              1.9, 1.6, OB, ridge=VD)
    mb.finish()
    # colisao das ombreiras escalonadas (ate o arranque; o vao da porta 10 x 14 continua livre)
    for sg in (-1, 1):
        prev = DW / 2
        for k in range(4):
            so = order_hw(k) + P_T
            ccol("SG_DunPortalFront", F.p(HX + sg * prev, 0.0, -0.5), F.p(HX + sg * so, P_DEP[k], P_SPR + 0.5))
            prev = so
    print("DUN portal: vortice r=%.2f centro h=%.2f | lapide %.1f..%.1f (DUNGEON_UI h %.1f)" % (
        rr, hc, TAB_H0, TAB_H1, L.DUNGEON_DOOR_H + 3.0))


# ==================================================================== APROXIMACAO (patio P3 ao sul da portaria)
def _mono_frame(x, y, lean):
    O = Vector((x, y, P3))
    nI = Vector((PC[0] - x, PC[1] - y, 0.0)).normalized()        # para o centro do circulo (face das runas)
    t = Vector((-nI.y, nI.x, 0.0))
    up = Vector((0.0, 0.0, 1.0))
    upL = up * math.cos(lean) - nI * math.sin(lean)               # inclina PARA FORA do circulo
    nL = nI * math.cos(lean) + up * math.sin(lean)

    def P(a, b, h):
        return O + t * a + nL * b + upL * h
    return P, t, nL, upL, nI


def monolith(mb, x, y, H, flip, idx):
    """monolito de obsidiana inclinado para fora, topo quebrado em bisel, colar de ferro negro e 3-4 runas na face que
    olha o portal; devolve o centro do colar (ancora das correntes) e o raio lateral dele"""
    P, t, nL, upL, nI = _mono_frame(x, y, math.radians(7.0))
    bw, bt, tw, tt = 1.45, 0.8, 1.0, 0.55
    dh = (0.0, -1.5, -0.9, -0.35)
    corners = ((-1, 1), (1, 1), (1, -1), (-1, -1))
    bm = mb.bm
    Bv = [bm.verts.new(P(a * flip * bw, b * bt, -0.4)) for a, b in corners]
    Tv = [bm.verts.new(P(a * flip * tw, b * tt, H + dh[i])) for i, (a, b) in enumerate(corners)]
    bm.faces.new(list(reversed(Bv)))
    bm.faces.new((Tv[0], Tv[1], Tv[2]))
    bm.faces.new((Tv[0], Tv[2], Tv[3]))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((Bv[i], Bv[j], Tv[j], Tv[i]))
    mb._post(Bv + Tv, OB, None, 0, 1)
    # soco de obsidiana bruta
    mb.prism(SL.ccw(SL.blob_poly(x, y, 2.05, n=7, rng=random.Random(800 + idx), amp=0.16)), P3 - 0.2, P3 + 0.45, OB)

    def half(hh):
        fr = min(1.0, max(0.0, (hh + 0.4) / (H - 0.6)))
        return bw + (tw - bw) * fr, bt + (tt - bt) * fr
    hcol = H - 2.6
    ac, bc = half(hcol)
    for sb in (-1, 1):
        obox3(mb, P(0.0, sb * (bc + 0.1), hcol), t, nL, upL, 2 * ac + 0.5, 0.26, 0.4, BI)
        obox3(mb, P(sb * (ac + 0.1), 0.0, hcol), nL, t, upL, 2 * bc + 0.5, 0.26, 0.4, BI)
    # runas na face interna (acompanha o afunilamento da face)
    h = 1.9
    j = 0
    while h + 1.4 * 0.9 < hcol - 0.5:
        b0 = half(h)[1]
        b1 = half(h + 1.0)[1]
        o = P(0.0, b0, h)
        eb = (P(0.0, b1, h + 1.0) - o).normalized()
        en = t.cross(eb).normalized()
        if en.dot(nI) < 0:
            en = -en
        glyph(mb, o, t, eb, en, idx * 3 + j, 0.9)
        h += 1.95
        j += 1
    col_box("SG_DunApproach", (2 * bw + 0.2, 2 * bt + 0.6, H), P3 * Vector((0, 0, 1)) + Vector((x, y, H / 2 - 0.3))
            - nI * 0.35, (0.0, 0.0, math.atan2(t.y, t.x)))
    return P(0.0, 0.0, hcol), ac


def sentinel(mb, x, y, fx, fy):
    """SENTINELA encapuzada (generica, sem personagem): pedestal negro com faixa de energia e runa, manto em sino,
    capa, capuz com o rosto em sombra e olhos violeta, duas LAMINAS cruzadas em X seguradas pelos punhos"""
    ang = math.atan2(-fx, fy)
    F = SL.Frame(x, y, P3, ang)
    o = F.p(0, 0, 0)
    fw, rt, up = F.p(0, 1, 0) - o, F.p(1, 0, 0) - o, Vector((0.0, 0.0, 1.0))
    mb.box((3.4, 3.4, 2.1), F.p(0, 0, 0.75), F.r(), OB, 0.1)
    mb.box((3.46, 3.46, 0.24), F.p(0, 0, 1.1), F.r(), VD, 0.0)
    mb.box((3.8, 3.8, 0.35), F.p(0, 0, 1.975), F.r(), VS, 0.06)
    glyph(mb, F.p(0, 1.7, 0.12), rt, up, fw, 5, 0.55)
    zb = 2.15
    mb.cyl(1.75, 4.3, F.p(0, -0.1, zb + 2.15), F.r(), m=ST, n=8, r2=1.2)                 # manto
    mb.cyl(1.95, 1.8, F.p(0, -0.2, zb + 5.1), F.r(), m=ST, n=8, r2=1.0)                  # capa
    mb.cyl(1.15, 1.9, F.p(0, 0.0, zb + 6.7), F.r(-0.14, 0, 0), m=ST, n=8, r2=0.7)        # capuz
    mb.cyl(0.72, 1.5, F.p(0, -0.55, zb + 7.9), F.r(0.6, 0, 0), m=ST, n=8, r2=0.05)       # ponta do capuz
    mb.box((0.9, 0.35, 1.05), F.p(0, 0.92, zb + 6.55), F.r(-0.14, 0, 0), VA, 0.0)        # rosto em sombra
    for sx in (-1, 1):
        mb.box((0.34, 0.2, 0.2), F.p(sx * 0.22, 1.08, zb + 6.72), F.r(), RG, 0.0)       # olhos
    for sgn in (-1, 1):
        hilt = F.p(sgn * 0.95, 1.55, zb + 4.9)
        tip = F.p(-sgn * 1.35, 1.85, zb + 0.35)
        ax = (tip - hilt).normalized()
        ay = fw.cross(ax).normalized()
        obox3(mb, hilt.lerp(tip, 0.5), ax, ay, fw, (tip - hilt).length, 0.4, 0.2, SV)           # lamina
        obox3(mb, hilt - ax * 0.12, ay, ax, fw, 1.7, 0.26, 0.32, OB)                             # guarda
        g1 = hilt - ax * 1.0
        obox3(mb, hilt.lerp(g1, 0.5), ax, ay, fw, 1.0, 0.3, 0.3, OB)                             # punho
        mb.box((0.38, 0.38, 0.38), g1 - ax * 0.2, (0.6, 0.6, 0.0), SV, 0.0)                     # pomo
        hand = hilt - ax * 0.5
        mb.box((0.78, 0.66, 0.66), hand, F.r(), ST, 0.1)                                         # mao
        mb.beam(F.p(sgn * 1.4, 0.2, zb + 5.5), hand, 0.72, 0.72, ST, 0.1)                       # manga
    col_box("SG_DunApproach", (3.8, 3.8, 10.4), (x, y, P3 + 4.9), (0.0, 0.0, ang))


def flame(mb, x, y, z0, m, sc0):
    """chama estilizada: corpo em "cebola" que balanca e afina (pilha de troncos de 7 lados, girados) + 2 labaredas
    menores inclinadas. Silhueta de fogo, nao de cristal. Mesmo desenho no braseiro violeta e nos quentes."""
    for (ox, oy, sc, sway) in ((0.0, 0.0, 1.0, 0.25), (0.62, 0.35, 0.58, 0.55), (-0.55, -0.4, 0.5, -0.5)):
        sc *= sc0
        zc = z0
        for i, (r0, r1, hh) in enumerate(((0.8, 1.08, 0.8), (1.08, 0.66, 1.2), (0.66, 0.24, 1.3), (0.24, 0.0, 0.9))):
            dx = ox * sc0 + sway * sc * (i * 0.35) ** 1.5
            mb.cyl(r0 * sc, hh * sc, (x + dx, y + oy * sc0, zc + hh * sc / 2), (0.0, 0.0, 0.45 * i), m=m, n=7,
                   r2=max(0.0, r1 * sc), bevel=0.0)
            zc += hh * sc - 0.02


def vbrazier(mb, x, y):
    """braseiro de CHAMA VIOLETA: base e fuste de obsidiana com faixa de energia, capitel violeta, tigela de ferro negro
    com 4 garras, brasa de runa e 3 linguas de chama (Neon)"""
    z = P3
    up = Vector((0.0, 0.0, 1.0))
    mb.box((2.3, 2.3, 0.9), (x, y, z + 0.15), (0, 0, 0), OB, 0.08)
    mb.cyl(0.7, 2.8, (x, y, z + 2.0), m=OB, n=6, bevel=0.0)
    mb.cyl(0.78, 0.24, (x, y, z + 1.6), m=VD, n=6, bevel=0.0)
    mb.cyl(1.05, 0.4, (x, y, z + 3.55), m=VS, n=6, r2=0.85, bevel=0.0)
    mb.cyl(0.85, 0.9, (x, y, z + 4.2), m=BI, n=8, r2=1.5, bevel=0.0)
    c = Vector((x, y, z))
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        ro = Vector((math.cos(a), math.sin(a), 0.0))
        blade(mb, c + ro * 1.3 + up * 4.45, ro * 0.45 + up, Vector((-ro.y, ro.x, 0.0)), ro, 1.7, 0.45, 0.3, BI)
    mb.cyl(1.05, 0.25, (x, y, z + 4.55), m=RG, n=8, bevel=0.0)
    flame(mb, x, y, z + 4.55, VG, 1.0)
    col_box2("SG_DunApproach", (x - 1.15, y - 1.15, P3 - 0.3), (x + 1.15, y + 1.15, P3 + 4.7))


def approach_floor():
    """ferradura de lajes de marmore negro (juntas de obsidiana) com RACHADURAS de energia convergindo na soleira
    violeta do portal; runas na soleira. Tudo rente ao piso (topo das lajes P3+0,13, energia +0,03 acima)"""
    mb = MB("SG_Dun_Approach_Floor", "17_DUNGEON", random.Random(781), detail="near")
    cx, cy = PC
    z0, zj, zt = P3 - 0.25, P3 + 0.07, P3 + 0.13
    arc = [(cx + PR * math.cos(math.pi + math.pi * k / 32), cy + PR * math.sin(math.pi + math.pi * k / 32))
           for k in range(33)]
    mb.prism(SL.ccw(arc), z0, zj, OB)
    mb.box2((cx - PR, cy - 0.01, z0), (cx + PR, HY0, zj), OB, 0.0)
    rings = (5.5, 9.0, 12.5, 16.0, 19.2, PR)
    for r0, r1 in zip(rings, rings[1:]):
        rm = (r0 + r1) / 2.0
        n = max(4, int(round(math.pi * rm / 3.3)))
        for i in range(n):
            ga = math.pi + math.pi * i / n + 0.13 / rm
            gb = math.pi + math.pi * (i + 1) / n - 0.13 / rm
            ra, rb = r0 + 0.13, r1 - 0.13
            gm = (ga + gb) / 2.0
            pts = [(cx + ra * math.cos(g), cy + ra * math.sin(g)) for g in (ga, gm, gb)] + \
                  [(cx + rb * math.cos(g), cy + rb * math.sin(g)) for g in (gb, gm, ga)]
            mb.prism(SL.ccw(pts), P3 - 0.1, zt, MBK)
    for x0 in (cx - PR, cx - PR + 3.0, cx - PR + 6.0, cx + PR - 9.0, cx + PR - 6.0, cx + PR - 3.0):
        mb.box2((x0 + 0.13, cy + 0.13, P3 - 0.1), (x0 + 2.87, HY0 - 0.13, zt), MBK, 0.0)
    # borda de obsidiana (le como limite do lugar do desafio sobre o calcamento claro do patio)
    rim_o = [(cx + (PR + 0.7) * math.cos(math.pi + math.pi * k / 32), cy + (PR + 0.7) * math.sin(math.pi + math.pi * k / 32))
             for k in range(33)]
    for k in range(32):
        a0, a1 = rim_o[k], rim_o[k + 1]
        i0, i1 = arc[k], arc[k + 1]
        mb.prism(SL.ccw([i0, i1, a1, a0]), z0, P3 + 0.3, OB)
    for sx in (-1, 1):
        xa = cx + sx * PR
        xb = cx + sx * (PR + 0.7)
        mb.box2((min(xa, xb), cy, z0), (max(xa, xb), HY0, P3 + 0.3), OB, 0.0)
    # soleira de pedra violeta (meia-lua r 5,4 + o recuo entre as ombreiras) com runas
    a5 = [(cx + 5.37 * math.cos(math.pi + math.pi * k / 16), cy + 5.37 * math.sin(math.pi + math.pi * k / 16))
          for k in range(17)]
    mb.prism(SL.ccw(a5), P3 - 0.1, zt, VS)
    mb.box2((HX - DW / 2 - 0.5, HY0 - P_DEP[3], P3 - 0.1), (HX + DW / 2 + 0.5, HY0, zt), VS, 0.0)
    up = Vector((0.0, 0.0, 1.0))
    for i, g in enumerate((-60.0, -30.0, 0.0, 30.0, 60.0)):
        a = math.radians(-90.0 + g)
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        o = Vector((cx, cy, zt - 0.1)) + rad * 4.2
        glyph(mb, o, Vector((-rad.y, rad.x, 0.0)), -rad, up, i + 1, 0.62, RG, dep=0.13)
    # rachaduras de energia: nascem na soleira e correm para fora (largas perto do portal, finas longe)
    rng = random.Random(787)

    def seg(p0, p1, w):
        d = Vector((p1[0] - p0[0], p1[1] - p0[1], 0.0))
        L_ = d.length
        if L_ < 0.05:
            return
        ax = d / L_
        obox3(mb, ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, zt - 0.07), ax, Vector((-ax.y, ax.x, 0.0)), up,
              L_ + w * 0.6, w, 0.2, VD)
    for k, th in enumerate((194.0, 209.0, 224.0, 241.0, 258.0, 282.0, 299.0, 316.0, 331.0, 346.0)):
        a = math.radians(th)
        r_end = rng.uniform(16.5, 21.2)
        steps = 7
        pts = []
        for i in range(steps + 1):
            rr = 5.6 + (r_end - 5.6) * i / steps
            if i:
                a += math.radians(rng.uniform(-5.0, 5.0))
            a = min(max(a, math.radians(186.0)), math.radians(354.0))
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        for i in range(steps):
            seg(pts[i], pts[i + 1], 0.5 - 0.26 * i / steps)
        if k % 2 == 0:
            b = pts[3]
            ab = math.atan2(b[1] - cy, b[0] - cx) + (0.5 if k % 4 == 0 else -0.5)
            q = b
            for i in range(2):
                q2 = (q[0] + 1.9 * math.cos(ab), q[1] + 1.9 * math.sin(ab))
                seg(q, q2, 0.3 - 0.06 * i)
                q = q2
                ab += rng.uniform(-0.3, 0.3)
    mb.finish()


def approach_guard():
    """circulo de 6 monolitos runicos acorrentados, 2 sentinelas e 2 braseiros violeta; 1 luz violeta"""
    mb = MB("SG_Dun_Approach_Guard", "17_DUNGEON", random.Random(791), detail="near")
    F = Face(True, HY0, -1, P3)
    for sg in (-1, 1):
        anc = []
        for j, (alpha, H) in enumerate(MONO_SPEC):
            a = math.radians(alpha)
            x, y = PC[0] + sg * MONO_R * math.cos(a), PC[1] - MONO_R * math.sin(a)
            anc.append(monolith(mb, x, y, H, sg, j + (0 if sg < 0 else 3)))
        sx, sy = STATUE_XY[0 if sg < 0 else 1]
        sentinel(mb, sx, sy, -sg * math.sin(math.radians(15.0)), -math.cos(math.radians(15.0)))
        bx, by = BRAZIER_XY[0 if sg < 0 else 1]
        vbrazier(mb, bx, by)
        # correntes: impostas do portal -> monolito 0 -> 1 -> 2 (o circulo esta preso ao portal)
        imp = F.v(HX + sg * (order_hw(3) + P_T * 0.5), P_DEP[3] + 0.25, P_SPR - 0.4)
        pts = [(imp, 0.0)] + anc
        for (p0, r0), (p1, r1) in zip(pts, pts[1:]):
            dh = Vector((p1.x - p0.x, p1.y - p0.y, 0.0)).normalized()
            a0 = p0 + dh * (r0 + 0.3)
            a1 = p1 - dh * (r1 + 0.3)
            chain(mb, a0, a1, 0.35 + 0.07 * (a1 - a0).length)
    mb.finish()
    light("L_SGDun_Approach", "POINT", (100.0, 47.0, P3 + 9.0), 3200.0, (0.62, 0.38, 1.0), 2.0)


def _approach_check():
    """folga das colisoes novas do patio ate as linhas do andador (corpo 1,1; exigimos >= 1,7) e o corredor x=100"""
    items = []
    for sg in (-1, 1):
        for alpha, H in MONO_SPEC:
            a = math.radians(alpha)
            x, y = PC[0] + sg * MONO_R * math.cos(a), PC[1] - MONO_R * math.sin(a)
            nI = Vector((PC[0] - x, PC[1] - y, 0.0)).normalized()
            items.append(("monolito", x - nI.x * 0.35, y - nI.y * 0.35, math.hypot(1.55, 1.1)))
    for x, y in STATUE_XY:
        items.append(("sentinela", x, y, 1.9 * math.sqrt(2.0)))
    for x, y in BRAZIER_XY:
        items.append(("braseiro", x, y, 1.15 * math.sqrt(2.0)))
    worst = 99.0
    for nm, x, y, r in items:
        dmin = min(L.seg_dist(x, y, a[0], a[1], b[0], b[1])[0] for a, b in WALK_LINES) - r
        dcor = abs(x - HX) - r - 5.0
        worst = min(worst, dmin, dcor + 1.7)
        if dmin < 1.7 or dcor < 0.0:
            print("DUN AVISO aproximacao: %s (%.1f, %.1f) folga rota %.2f corredor %.2f" % (nm, x, y, dmin, dcor))
    print("DUN aproximacao: folga minima ate o andador/corredor = %.2f (exige >= 1,7)" % worst)


def approach():
    approach_floor()
    approach_guard()
    _approach_check()


def house_interior():
    mb = MB("SG_Dun_House_Interior", "17_DUNGEON", random.Random(711), detail="near")
    FS, FN = Face(True, IY0, 1, P3), Face(True, IY1, -1, P3)
    FW, FE = Face(False, IX0, 1, P3), Face(False, IX1, -1, P3)
    # piso (+0,05 sobre o calcamento do terreno) e soleira
    tile_floor(mb, (IX0, IY0, IX1, IY1), P3 + 0.05, tile=3.4, margin=0.9, friso=0.7,
               skip=lambda x, y: y > DAIS[0][0] - 0.2)
    mb.box2((HX - DW / 2, HY0, P3 - 0.4), (HX + DW / 2, IY0, P3 + 0.05), TR, 0.0)
    # estrado de 2 degraus (so 0,4 e 0,8: colisao casada)
    (y1, z1), (y2, z2) = DAIS
    mb.box2((IX0 + 2.2, y1, P3 - 0.2), (IX1 - 2.2, y2, P3 + z1), TR, 0.06)
    mb.box2((IX0, y2, P3 - 0.2), (IX1, y2 + 0.6, P3 + z2), TR, 0.06)
    mb.box2((IX0, y2 + 0.6, P3 - 0.2), (IX1, IY1, P3 + z2), FL, 0.0)
    col_box2("SG_DunHouse", (IX0 + 2.2, y1, P3 - 0.5), (IX1 - 2.2, y2, P3 + z1))
    col_box2("SG_DunHouse", (IX0, y2, P3 - 0.5), (IX1, IY1, P3 + z2))
    # paredes laterais: colunas de canto, pilastra do meio, arcos cegos, tochas
    for F in (FW, FE):
        corner_col(mb, F, IY0, 1, IN_SPR, "SG_DunHouse")
        corner_col(mb, F, IY1, -1, IN_SPR, "SG_DunHouse")
        pilaster(mb, F, HY, IN_SPR, "SG_DunHouse")
        blind_arch(mb, F, IY0 + 2.4, HY - PIL_HW - 0.3, 7.6)
        fbox(mb, F, HY + PIL_HW + 0.3, IY1 - 2.4, 0.0, 0.4, 0.0, 0.9 + DAIS[1][1], TR, 0.05)
        blind_arch_raised(mb, F, HY + PIL_HW + 0.3, IY1 - 2.4, 7.6, DAIS[1][1])
        cornice(mb, F, IY0, IY1, IN_SPR)
        torch(mb, F, HY, PIL_D + 0.45, 8.4)
    # parede sul (porta): moldura interna, rodape, tochas
    arch_band(mb, FS, HX, DW / 2, D_RISE, D_SPR, 0.0, 0.7, 0.0, 0.5, TR, n=7)
    for s0, s1 in ((IX0 + 2.4, HX - DW / 2 - 0.7), (HX + DW / 2 + 0.7, IX1 - 2.4)):
        fbox(mb, FS, s0, s1, 0.0, 0.4, 0.0, 0.9, TR, 0.05)
        cornice(mb, FS, s0, s1, IN_SPR)
    for s in (HX - 7.6, HX + 7.6):
        torch(mb, FS, s, 0.0, 8.4)
    # parede norte: nicho ogival navy com arquivolta, atras do portal
    pr = 7.0
    arch_panel(mb, FN, HX, pr + 0.2, pr + 0.8, 7.4, DAIS[1][1], 0.0, 0.15, VA, n=8)
    arch_band(mb, FN, HX, pr + 0.2, pr + 0.8, 7.4, DAIS[1][1], 0.6, 0.0, 0.55, TR, n=8)
    # abobada (berco ao longo de y, arcos em x) com nervura no eixo das pilastras
    vault(mb, (IX0, IY0, IX1, IY1), "y", P3, IN_SPR, IN_CROWN, ribs=(HY,))
    # guardioes e braseiros internos (as lanternas quentes da porta sairam: a fachada agora e o portal violeta)
    house_props(mb)
    mb.finish()


def blind_arch_raised(mb, F, s0, s1, spring, lift):
    """arco cego sobre o estrado (pe levantado em 'lift')"""
    cs = (s0 + s1) / 2.0
    hw = (s1 - s0) / 2.0 - 0.8
    if hw < 1.2:
        return
    rise = min(hw * 1.15, 5.2)
    arch_panel(mb, F, cs, hw, rise, spring, 0.9 + lift, 0.0, 0.15, VA)
    arch_band(mb, F, cs, hw, rise, spring, 0.9 + lift, 0.55, 0.0, 0.5, TR)


def house_portal():
    """portal espiral da portaria: anel + disco (estaticos) e a espiral que gira (VFX_SGDUN_Portal)"""
    r_in, r_out = 5.4, 7.0
    zf = P3 + DAIS[1][1]
    c = Vector((PX, PY + 0.6, zf + r_out - 0.4))
    u, v, n = Vector((1, 0, 0)), Vector((0, 0, 1)), Vector((0, -1, 0))
    mb = MB("SG_Dun_House_Portal", "17_DUNGEON", random.Random(721), detail="near")
    portal_frame(mb, c, u, v, n, r_in, r_out, zf)
    disc3(mb, c, u, v, n, r_in + 0.15, -0.5, -0.3, VO, 32)
    mb.finish()
    vf = MB("VFX_SGDUN_Portal", "12_VFX_HELPERS", random.Random(723), detail="near")
    spiral(vf, c, u, v, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7)
    ob = vf.finish()
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, -1.0, 0.0]
    ob["rpm"] = 5.0
    ob["vfx"] = "espiral violeta do portal da dungeon (gira no plano do disco)"
    col_box2("SG_DunPortal", (PX - r_out, PY - 0.2, zf), (PX + r_out, IY1, zf + 2 * r_out - 0.4))
    return c


def house_props(mb):
    zf = P3 + DAIS[1][1]
    gy = 76.8
    for gx in (92.6, 107.4):
        fx, fy = (HX - gx) * 0.08, -1.0
        guardian(mb, gx, gy, zf, math.atan2(-fx, fy))
        col_box2("SG_DunHouse", (gx - 1.5, gy - 1.5, zf - 0.5), (gx + 1.5, gy + 1.5, zf + 9.0))
    for bx in (93.6, 106.4):
        brazier(mb, bx, 69.0, P3 + 0.05)
        col_box2("SG_DunHouse", (bx - 1.0, 68.0, P3), (bx + 1.0, 70.0, P3 + 4.0))
    light("L_SGDun_Portal", "POINT", (PX, 75.5, P3 + 7.0), 1800.0, (0.64, 0.42, 1.0), 1.5)
    light("L_SGDun_Brazier", "POINT", (HX, 67.5, P3 + 7.5), 2200.0, (1.0, 0.66, 0.36), 1.0)


# ==================================================================== SALAS (sob a ilha)
def room_walls():
    """paredes das 3 salas (visual + colisao identicos), piso e teto colidiveis"""
    mb = MB("SG_Dun_Rooms_Shell", "17_DUNGEON", random.Random(741), detail="far", floor=-999)
    zb, zt = Z - 0.6, ZCEIL
    y0l, y1l = LY - L.DUN_LINK_W / 2, LY + L.DUN_LINK_W / 2
    pieces = [
        ((-64.0, 60.0), (-62.0, 100.0)),            # R1 oeste
        ((-64.0, 98.0), (-26.0, 100.0)),            # R1 norte
        ((-64.0, 60.0), (-26.0, 62.0)),             # R1 sul
        ((-24.0, 102.0), (20.0, 104.0)),            # R2 norte
        ((-24.0, 56.0), (20.0, 58.0)),              # R2 sul
        ((22.0, 102.0), (68.0, 104.0)),             # R3 norte
        ((22.0, 56.0), (68.0, 58.0)),               # R3 sul
        ((66.0, 56.0), (68.0, 104.0)),              # R3 leste
    ]
    for xa, xb in ((-26.0, -24.0), (20.0, 22.0)):   # paredes compartilhadas com o vao de ligacao
        pieces += [((xa, 56.0), (xb, y0l)), ((xa, y1l), (xb, 104.0))]
        mb.box2((xa, y0l, Z + LINK_H), (xb, y1l, zt), CS, 0.0)
        ccol("SG_DunRoom", (xa, y0l, Z + LINK_H), (xb, y1l, zt))
    for (xa, ya), (xb, yb) in pieces:
        mb.box2((xa, ya, zb), (xb, yb, zt), CS, 0.0)
        ccol("SG_DunRoom", (xa, ya, zb), (xb, yb, zt))
    mb.finish()
    ccol("SG_DunRoom", (BX0, BY0, Z - 2.0), (BX1, BY1, Z))
    ccol("SG_DunRoom", (BX0, BY0, ZCEIL), (BX1, BY1, ZCEIL + 1.5))


def room_kit():
    """kit das salas: pilastras, colunas de canto, arcos cegos, cornijas, molduras dos vaos, tochas, pisos, abobadas"""
    mk = MB("SG_Dun_Rooms_Kit", "17_DUNGEON", random.Random(751), detail="near")
    mv = MB("SG_Dun_Rooms_Vault", "17_DUNGEON", random.Random(753), detail="near")
    mf = MB("SG_Dun_Rooms_Floor", "17_DUNGEON", random.Random(755), detail="near")
    mi = MB("SG_Dun_Rooms_Iron", "17_DUNGEON", random.Random(757), detail="near")
    A = "SG_DunKit"
    cx3 = sum(ROOMS["R3"][0::2]) / 2.0
    for nm in ("R1", "R2", "R3"):
        x0, y0, x1, y1 = ROOMS[nm]
        FS, FN = Face(True, y0, 1, Z), Face(True, y1, -1, Z)
        FW, FE = Face(False, x0, 1, Z), Face(False, x1, -1, Z)
        # colunas de canto
        for F, a, b in ((FS, x0, x1), (FN, x0, x1)):
            corner_col(mk, F, a, 1, R_SPR, A)
            corner_col(mk, F, b, -1, R_SPR, A)
        # paredes N/S: pilastras que carregam as nervuras
        if nm == "R1":
            ps = [x0 + 12.0, x0 + 24.0]
        elif nm == "R2":
            ps = [x0 + 11.0, x1 - 11.0]
        else:
            ps = [x0 + 11.0, x0 + 22.0, x0 + 33.0]
        for F in (FS, FN):
            bounds = [x0 + 2.4] + [q for p in ps for q in (p - PIL_HW - 0.3, p + PIL_HW + 0.3)] + [x1 - 2.4]
            for p in ps:
                pilaster(mk, F, p, R_SPR, A)
            for k in range(0, len(bounds), 2):
                sa, sb = bounds[k], bounds[k + 1]
                blind_arch(mk, F, sa, sb, 7.0, twin=(sb - sa > 16.0))
            cornice(mk, F, x0 + 2.4, x1 - 2.4, R_SPR)
            if nm == "R1":
                for p in ps:
                    torch(mi, F, p, PIL_D + 0.45, 8.4)
        # paredes L/O: vao de ligacao ou portal no eixo y 80, pilastras-ombreira, arcos cegos nos lados
        for F, side in ((FW, "W"), (FE, "E")):
            jam = (LY - L.DUN_LINK_W / 2 - PIL_HW - 0.3, LY + L.DUN_LINK_W / 2 + PIL_HW + 0.3)
            if (nm, side) in (("R1", "W"), ("R3", "E")):
                jam = (LY - 9.5, LY + 9.5)
            for p in jam:
                pilaster(mk, F, p, R_SPR, A)
                torch(mi, F, p, PIL_D + 0.45, 8.4)
            blind_arch(mk, F, y0 + 2.4, jam[0] - PIL_HW - 0.3, 7.0)
            blind_arch(mk, F, jam[1] + PIL_HW + 0.3, y1 - 2.4, 7.0)
            cornice(mk, F, y0 + 2.4, jam[0] - PIL_HW - 0.3, R_SPR)
            cornice(mk, F, jam[1] + PIL_HW + 0.3, y1 - 2.4, R_SPR)
            is_link = (nm == "R1" and side == "E") or nm == "R2" or (nm == "R3" and side == "W")
            if is_link:
                link_frame(mk, F, LY, L.DUN_LINK_W / 2)
        # piso de lajes com friso; R3: medalhao do altar no centro (sob o minerio SUPERLEGENDARY)
        cxr, cyr = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        skip = (lambda x, y, cx=cxr, cy=cyr: abs(x - cx) < 9.0 and abs(y - cy) < 9.0) if nm == "R3" else None
        tile_floor(mf, (x0, y0, x1, y1), Z, tile=4.0, margin=1.0, friso=0.8, skip=skip)
        # abobada de bercos ao longo de x com nervuras nas pilastras
        vault(mv, (x0, y0, x1, y1), "x", Z, R_SPR, R_CROWN, ribs=ps)
    # soleiras dos vaos
    for xa, xb in ((-26.0, -24.0), (20.0, 22.0)):
        mf.box2((xa, LY - L.DUN_LINK_W / 2, Z - 0.4), (xb, LY + L.DUN_LINK_W / 2, Z), TR, 0.0)
    # medalhao do altar da R3 (embutido, topo exato no piso: nada colidivel perto do minerio)
    altar_medallion(mf, *[(ROOMS["R3"][0] + ROOMS["R3"][2]) / 2.0, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0])
    # lustres: 2 na R2 (mineracao), 1 coroa na R3 (altar)
    for x, y, h, r in ((-13.0, LY, 16.5, 3.0), (9.0, LY, 16.5, 3.0), (cx3, LY, 15.8, 3.8)):
        rect = ROOMS["R2"] if x < 21.0 else ROOMS["R3"]
        top = vault_z(rect, "x", Z, R_SPR, R_CROWN, 0.0) - 0.8
        chandelier(mi, x, y, Z + h, top, r=r, n=8 if r < 3.5 else 12)
    for m in (mk, mv, mf, mi):
        m.finish()


def altar_medallion(mb, cx, cy):
    """quadrado 18 x 18 sem lajes -> anel de cantaria -> campo navy -> anel de prata -> disco (tudo com topo em Z)"""
    n = 32
    ang = [2 * math.pi * k / n for k in range(n)]
    Hs = 9.0

    def circ(r):
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in ang]
    sq = [(cx + Hs * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
           cy + Hs * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    # o quadrado de 18 fica no miolo da grade (ja sem lajes): a borda e ajustada a grade na sala
    rings = [(sq, circ(7.8), FL), (circ(7.8), circ(7.0), TR), (circ(7.0), circ(3.2), VA), (circ(3.2), circ(2.7), SV)]
    zt, zb = Z, Z - 0.4
    bm = mb.bm
    for outer, inner, m in rings:
        oT = [bm.verts.new((x, y, zt)) for x, y in outer]
        iT = [bm.verts.new((x, y, zt)) for x, y in inner]
        oB = [bm.verts.new((x, y, zb)) for x, y in outer]
        iB = [bm.verts.new((x, y, zb)) for x, y in inner]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
            bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
            bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
            bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
        mb._post(oT + iT + oB + iB, m, None, 0, 1)
    mb.prism(circ(2.7), zb, zt, FL)
    # 8 runas da ordem no campo navy (no lugar dos raios de estrela), rentes: topo Z + 0,03
    up = Vector((0.0, 0.0, 1.0))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        glyph(mb, Vector((cx, cy, zt - 0.1)) + rad * 3.9, Vector((-rad.y, rad.x, 0.0)), rad, up, k, 1.5, RG, dep=0.13)


def floor_runes(mb, c, n):
    """arco de 7 runas rentes ao piso diante de um portal das salas (c = pe do portal, n = para dentro da sala)"""
    up = Vector((0.0, 0.0, 1.0))
    base = math.atan2(n.y, n.x)
    for i in range(7):
        a = base + math.radians(-54.0 + 18.0 * i)
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        glyph(mb, Vector((c.x, c.y, Z - 0.1)) + rad * 7.0, Vector((-rad.y, rad.x, 0.0)), -rad, up, i + 2, 1.0, RG,
              dep=0.13)
    for i in range(24):
        a0 = base + math.radians(-66.0 + 5.5 * i)
        a1 = a0 + math.radians(5.5)
        p0 = Vector((c.x + 9.2 * math.cos(a0), c.y + 9.2 * math.sin(a0), Z - 0.07))
        p1 = Vector((c.x + 9.2 * math.cos(a1), c.y + 9.2 * math.sin(a1), Z - 0.07))
        ax = (p1 - p0).normalized()
        obox3(mb, (p0 + p1) / 2, ax, Vector((-ax.y, ax.x, 0.0)), up, (p1 - p0).length + 0.05, 0.3, 0.2, RG)


def room_portals():
    """portal de chegada (R1, parede oeste, aceso) e portal de saida (R3, parede leste): mesma peca da portaria"""
    mb = MB("SG_Dun_Rooms_Portals", "17_DUNGEON", random.Random(761), detail="near")
    r_in, r_out = 5.0, 6.5
    x0 = ROOMS["R1"][0]
    x1 = ROOMS["R3"][2]
    v = Vector((0, 0, 1))
    specs = [("R1", Vector((x0 + 1.0, LY, Z + r_out - 0.3)), Vector((1, 0, 0)), Face(False, x0, 1, Z)),
             ("R3", Vector((x1 - 1.0, LY, Z + r_out - 0.3)), Vector((-1, 0, 0)), Face(False, x1, -1, Z))]
    out = {}
    for nm, c, n, F in specs:
        u = n.cross(v).normalized()
        portal_frame(mb, c, u, v, n, r_in, r_out, Z)
        disc3(mb, c, u, v, n, r_in + 0.15, -0.5, -0.3, VO if nm == "R1" else VA, 32)
        # nicho ogival navy atras do anel + arquivolta
        arch_panel(mb, F, LY, r_out + 0.2, r_out + 0.8, c.z - Z, 0.0, 0.0, 0.15, VA, n=8)
        arch_band(mb, F, LY, r_out + 0.2, r_out + 0.8, c.z - Z, 0.0, 0.6, 0.0, 0.55, TR, n=8)
        ccol("SG_DunPortal", F.p(LY - r_out, 0.0, -0.5), F.p(LY + r_out, 1.75, 2 * r_out - 0.6))
        floor_runes(mb, Vector((c.x, c.y, Z)), n)
        out[nm] = (c, u, n)
    c, u, n = out["R1"]
    spiral(mb, c, u, v, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7, a0=0.4)
    mb.finish()
    # espiral da saida: objeto proprio (o jogo mostra so em FINISHING/FINISHED)
    c, u, n = out["R3"]
    ms = MB("SG_Dun_R3_ExitSpiral", "17_DUNGEON", random.Random(763), detail="near")
    spiral(ms, c, u, v, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7, a0=1.1)
    ob = ms.finish()
    ob["show"] = "FINISHING,FINISHED"
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [round(n.x, 3), round(n.y, 3), round(n.z, 3)]
    ob["note"] = "espiral do portal de saida: o jogo liga (Transparency 0) quando a corrida termina"


def room_lights():
    x0 = ROOMS["R1"][0]
    light("L_SGDun_R1_Portal", "POINT", (x0 + 6.0, LY, Z + 7.0), 2600.0, (0.64, 0.42, 1.0), 1.5)
    light("L_SGDun_R2_ChandelierW", "POINT", (-13.0, LY, Z + 15.8), 5200.0, (1.0, 0.68, 0.40), 1.0)
    light("L_SGDun_R2_ChandelierE", "POINT", (9.0, LY, Z + 15.8), 5200.0, (1.0, 0.68, 0.40), 1.0)
    cx3 = sum(ROOMS["R3"][0::2]) / 2.0
    light("L_SGDun_R3_Altar", "POINT", (cx3, LY, Z + 15.0), 5600.0, (1.0, 0.68, 0.40), 1.0)


def build():
    _SKIP.clear()
    house_shell()
    house_interior()
    house_portal()
    approach()
    room_walls()
    room_kit()
    room_portals()
    room_lights()
    bad = []
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith(("SG_Dun_", "VFX_SGDUN_")):
            nd = sum(1 for p in o.data.polygons if p.area < 1e-6)
            if nd:
                bad.append((o.name, nd, [tuple(round(c, 1) for c in o.data.polygons[i].center)
                                         for i in range(len(o.data.polygons)) if o.data.polygons[i].area < 1e-6][:3]))
    print("DUN faces degeneradas:", bad or "nenhuma")
    if _SKIP:
        print("DUN AVISO colisoes omitidas por folga de minerio (so visual):", _SKIP)
    else:
        print("DUN folga dos minerios: OK (nenhuma colisao a menos de 5 de DUN_ORE_* ate piso+12)")
