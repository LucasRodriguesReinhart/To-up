# sg_summon - ZONA SUMMON da Ilha 3 (Shadow Garden). Substitui sg_blockout.summon. Prefixo SG_Sum_, colecao 06_SUMMON,
# pecas moveis VFX_SGSUM_* em 12_VFX_HELPERS, luzes L_SGSum_*.
# REGRA DA MISSAO: a maquina e a MESMA torre de invocacao das Ilhas 1 e 2 (familia aprovada). O codigo da torre e o da
# Ilha 1 (ilha_naruto/il_summon.py), carregado com a planta DESTA ilha (il_layout.SUMMON_TOWER/FACE/T1/SUMMON_C/R
# trocados so durante o import e restaurados logo depois, como fez a Ilha 2 em db_summon.tower_mod). Reaproveitado sem
# redesenho: corpo L1 com o NICHO do portal + frontispicio + frontao, cornijas, corpo L2 com a janela-estrela, coroa
# L3 com pinaculos, contrafortes, mastros com estandartes e lanternas penduradas, pedestais internos, patamar do portal
# e a esfera armilar (gaiola + 3 aneis moveis + estrela de cristal). As funcoes que misturam base e torre
# (tower_stone, masts_and_lanterns, tower_collision) foram PORTADAS aqui so com a parte da torre; tower_details,
# in_pedestal e sphere sao chamadas direto.
# O QUE MUDOU (so base, materiais, luz e VFX):
#   - materiais: troca por apelido SO durante a torre (fm_lib.MAT_ALIAS): pedra lilas -> pedra fria SG (castelo /
#     bloco / escura: o xadrez claro/escuro da Ilha 1 vira alternancia sutil), ouro -> prata, azul royal -> navy, portal azul -> indigo (SG_SumPortal_Glow), estrela
#     ambar/amarela -> violeta + lilas (SG_Violet_Glow / SG_SumStar_Glow), bordas azuis -> violeta;
#   - base: o soco de 40 x 20 com 4 pedestais de lanterna japonesa NAO cabe na plataforma de raio 22 -> podio proprio
#     (laterais retas + fundo em arco concentrico a plataforma, que vira bastiao na borda oeste), soco claro, arcada cega
#     ogival com estrelas de prata na frente; escada da torre (mesma medida: 5 x 0,8, 7,6 de largura) sem as bordas de
#     brilho, com banzos lisos; pedestais internos com lanterna gotica de ferro (as 2 luzes quentes baixas);
#   - praca: o piso e do terreno (topo 40,2); aqui so o desenho radial discreto (+0,05) centrado no ponto do jogador
#     (SUMMON_PlayerPosition) + faixa de borda; balaustrada gotica baixa na borda (aberta na escada, x -120,5, largura
#     12), ponte curta com arco ogival e parapeitos iguais, escada da planta (sg_lib.plan_stair) com banzos lisos;
#   - fora: constelacao das asas, cristais (liam como minerio), lanternas japonesas, postes do pe da escada.
# Colisao propria: podio/soco, corpo da torre, patamar + escada da torre, pedestais. Piso, escada da planta, ponte e
# guardas: sg_col (congelado). Marcadores SUMMON_*: sg_core (congelado; o jogador fica em v 16 no piso, o gabinete
# invisivel do gacha em v 7).
# ACABAMENTO 2026-09-29: brilho MODERADO (portal indigo mais fundo 1,3 -> 0,7, estrela lilas 2,6 -> 1,5, bordas azuis da
# Ilha 1 -> SG_VioletSoft_Glow, luz do nucleo 9000 -> 6000); sairam os 2 estandartes em mastro do portao da escada (na
# frente do portal, repetiam os da torre). Torre e plataforma sem redesenho.
# OVERHAUL 10 "zero tolerancia" (2026-09-29): estrelas so no portal e na esfera (filtro no tower_details, podio, piso
# e asas sem estrela; rosacea de cantaria no ponto do jogador); vitrais com rendilhado de pedra; lanternas da ORDEM do
# kit (pedestais, mastros e pilares-portao) no lugar da lanterna gotica local e da caixa de Neon da Ilha 1; pedestal
# interno com painel rebaixado; pilastras do podio com base e capitel; balaustrada de balaustres torneados; ponte com
# arco entre as faces de rocha, impostas e aduelas radiais; estrela da esfera em violeta medio 0,9 (sem estouro).
# ONDA 2 / o2b (2026-10-01, planta v4): roda DIRETO na v4 (saiu do build_sg.LEGACY / sg_relocate): tudo sai de
# SUMMON_C / SUMMON_TOWER / SUMMON_BRIDGE (cameras relativas ao centro); as faces de rocha do arco da ponte sao
# MEDIDAS no terreno v4; rotas do QA so com o modulo construido (o FAIL PAD->PATAMAR era a colisao do blockout).
import math, random, sys, importlib
from contextlib import contextmanager
from mathutils import Vector
import bpy
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, Frame
import sg_layout as L
import fm_lib
import fm_parts as FP
import fm_portal_kit as PK
import sg_emblem as EM

COL = "06_SUMMON"
CX, CY = L.SUMMON_C
R = L.SUMMON_R
Z = L.SUM
P1 = L.P1

# ------------------------------------------------------------------ materiais novos (2 de 4)
_S = fm_lib.S
# ACABAMENTO 2026-09-29 (brilho MODERADO): o portal e a estrela estouravam e achatavam o nicho/a esfera (o neon so
# escondia a forma). Portal: indigo mais fundo e emissao 1,3 -> 0,7 (o arco e as aduelas voltam a ler); estrela:
# lilas menos branco, 2,6 -> 1,5. As bordas azuis da Ilha 1 viram o violeta BAIXO (SG_VioletSoft_Glow).
fm_lib.MATS.setdefault("SG_SumPortal_Glow", (_S(70, 54, 166), 0.3, 0.0, 0.7, _S(82, 62, 190), 0.0))   # nicho/janelas
# OVERHAUL 10 (2026-09-29, 10.06/15.06): a estrela lilas (206,180,250) em 1,5 estourava em BRANCO no Roblox (bloom) e
# apagava a gaiola de prata. Agora violeta MEDIO saturado em 0,9 + um 2o tom FUNDO para as facetas alternadas da estrela
# de cristal (antes SG_Violet_Glow 2,6, o mais forte da paleta): brilho moderado, a gaiola le na frente.
fm_lib.MATS.setdefault("SG_SumStar_Glow", (_S(146, 104, 232), 0.2, 0.0, 0.9, _S(146, 104, 232), 0.0))
fm_lib.MATS.setdefault("SG_SumStarDeep_Glow", (_S(96, 58, 188), 0.2, 0.0, 0.9, _S(96, 58, 188), 0.0))
for _k in ("SG_SumPortal_Glow", "SG_SumStar_Glow", "SG_SumStarDeep_Glow"):
    fm_lib.RBX_CAL.setdefault(_k, (None, [int(c) for c in fm_lib.to_srgb(fm_lib.MATS[_k][0])]))
# remate de cantaria perto do jogador (o mesmo do setor 01/03: um valor abaixo do Stone_SG_Trim, auditoria 14.01)
CAPL = "Stone_SG_TrimLow"
fm_lib.MATS.setdefault(CAPL, (_S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
PAR_M = "Stone_SG_Castle_B"      # corpo de balaustrada / pilaretes (a linguagem da entrada)
REL_M = "Stone_SG_Block_B"       # relevo: plinto, balaustres, bases

# materiais da Ilha 1 -> paleta SMATS (apelido so durante a torre; os nomes da Ilha 1 nunca chegam ao export)
TOWER_ALIAS = {
    "Summon_Stone": "Stone_SG_Castle", "Stone_SumBlock": "Stone_SG_Block", "Summon_Stone_Dark": "Stone_SG_Floor",
    "Metal_Gold": "Metal_SG_Silver", "Cloth_Royal_Blue": "Cloth_SG_Navy", "Wood_Dark": "Wood_SG_Dark",
    "Crystal_SumPortal_Glow": "SG_SumPortal_Glow", "Crystal_SumStar_Glow": "SG_SumStar_Glow",
    "Summon_Blue_Glow": "SG_VioletSoft_Glow", "Summon_Star_Glow": "SG_SumStar_Glow",
    "Crystal_SumAmber_Glow": "SG_SumStarDeep_Glow", "Crystal_SumYellow_Glow": "SG_SumStar_Glow",
    "Crystal_Blue": "SG_VioletSoft_Glow",
}

# ------------------------------------------------------------------ referencial da torre (o mesmo do il_summon)
TX, TY = L.SUMMON_TOWER
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2
F = Frame(TX, TY, Z, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))
ZZ = Vector((0.0, 0.0, 1.0))
# medidas da torre da Ilha 1 (il_summon) usadas antes do import (rotas/cameras); build() confere que batem
ST_FOOT, LAND_Z, PV, CORR, POD_TOP, AX, ZS = 13.6, 4.0, -1.4, 5.0, 3.3, -3.0, 46.0
LAND_V1 = 5.6
C_V = math.hypot(CX - TX, CY - TY)          # centro da plataforma no referencial da torre: (0, 7,5)
PAD_V = 16.0                                # SUMMON_PlayerPosition (sg_core)
INTER_V = 7.0                               # SUMMON_Interact (sg_core)

# ------------------------------------------------------------------ base (podio proprio)
POD_HW = 12.2          # meia largura do podio (inclui os mastros, u 10,4 +- 1)
POD_VF = 7.2           # frente do podio (a da Ilha 1)
POD_RB = 20.0          # fundo do podio: arco concentrico a plataforma
SOC_OFF = 0.9          # soco claro (0 .. 0,8) sai 0,9 do podio
SOC_RB = 20.8
PLZ = 0.8
IN_PED = (9.6, 5.6)    # pedestais internos (Ilha 1) com a lanterna gotica
RAIL_R = 21.2          # linha da balaustrada (a guarda invisivel do sg_col fica de 22 a 23)
GATE_A = 20.0          # abertura da escada: +-20 graus a partir de +X (meia largura 7,25 no raio da balaustrada)
BR_Y = 6.6             # parapeitos da ponte e banzos da escada (linha da guarda do sg_col)
WARM = (1.0, 0.64, 0.34)
VIOLET = (0.62, 0.44, 1.0)


def P(u, v, z=0.0):
    return F.p(u, v, z)


def to_local(x, y):
    d = Vector((x - TX, y - TY, 0.0))
    return d.dot(XU), d.dot(YV)


def _side_v(hw, rb):
    """v onde a lateral reta (|u| = hw) encontra o arco do fundo (raio rb em volta do centro da plataforma)"""
    return C_V - math.sqrt(rb * rb - hw * hw)


def in_base(x, y, pad=0.0):
    """ponto sobre a base da torre (soco/podio) ou sobre a escada da torre"""
    u, v = to_local(x, y)
    hw = POD_HW + SOC_OFF
    if abs(u) < hw + pad and v < POD_VF + SOC_OFF + pad and math.hypot(u, v - C_V) < SOC_RB + pad:
        return True
    return abs(u) < CORR + pad and v < ST_FOOT + pad


def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    # frente: da ponta da ponte, acima (a torre inteira, base ao remate da esfera ~62)
    "CAM_SGSum_Front": ((CX + 64.5, CY + 4.0, Z + 18.0), (TX, TY, Z + 28.0), 20),
    # tras (oeste, fora da ilha): bastiao do podio na borda + costas da torre
    "CAM_SGSum_Back": ((CX - 93.5, CY + 22.0, Z + 26.0), (TX, TY, Z + 24.0), 22),
    # lados
    "CAM_SGSum_North": ((CX + 4.5, CY + 80.0, Z + 22.0), (CX - 3.5, CY + 0.0, Z + 24.0), 22),
    "CAM_SGSum_South": ((CX - 7.5, CY - 80.0, Z + 22.0), (CX - 3.5, CY + 0.0, Z + 24.0), 22),
    # altura do jogador: na ponte olhando a subida e a torre; no pad (SUMMON_PlayerPosition) olhando o portal
    "CAM_SGSum_PlayerBridge": ((CX + 40.5, CY + 0.0, P1 + 5.2), (TX, TY, Z + 14.0), 22),
    "CAM_SGSum_PlayerPad": ((CX + 11.0, CY - 3.0, Z + 5.2), (TX, TY, Z + 10.0), 20),
    # altura do jogador na passagem lateral (norte) entre o podio e a balaustrada
    "CAM_SGSum_PlayerWalk": ((CX + 15.5, CY + 17.5, Z + 5.2), (CX - 15.5, CY + 10.0, Z + 3.0), 20),
    # ponte vista de lado (arco ogival) a partir do vao ao norte, entre a ilha e a ilhota, baixa
    # (o2b, v4: o olho fica no AR, no alinhamento do vao entre o penhasco e a lingua da ilhota)
    "CAM_SGSum_BridgeSide": ((CX + 34.5, CY + 36.0, P1 - 5.0), (CX + 34.5, CY + 0.0, P1 - 4.5), 22),
    # esfera armilar + estrela de perto
    "CAM_SGSum_Sphere": ((CX + 30.5, CY - 10.0, Z + 44.0), (TX - 3.0, TY, Z + 46.0), 30),
    # overhaul 10 (2026-09-29): closes na altura do jogador - lanterna do pedestal interno, balaustrada, podio,
    # parapeito da ponte e a ponte vista do P1 (o arco e os pes na rocha)
    "CAM_SGSum_OV_Lantern": ((CX + 9.5, CY - 14.0, Z + 5.4), (CX - 1.9, CY - 9.6, Z + 7.8), 32),
    "CAM_SGSum_OV_Rail": ((CX + 9.0, CY + 9.5, Z + 5.2), (CX + 11.0, CY + 19.0, Z + 1.4), 24),
    "CAM_SGSum_OV_Podium": ((CX + 9.5, CY - 13.0, Z + 5.2), (CX - 0.3, CY - 7.0, Z + 1.8), 26),
    "CAM_SGSum_OV_BridgeRail": ((CX + 40.0, CY + 3.5, P1 + 5.2), (CX + 32.5, CY - 6.8, P1 + 1.2), 24),
    "CAM_SGSum_OV_BridgeArch": ((CX + 35.5, CY + 14.0, P1 - 3.5), (CX + 35.2, CY + 0.0, P1 - 4.8), 30),
    # inspecao: pilar-portao do topo da escada (lanterna + banzo) e o fim da balaustrada no soco
    "CAM_SGSum_OV_GatePost": ((CX + 26.5, CY + 12.0, Z + 4.4), (CX + 19.9, CY + 7.2, Z + 2.2), 30),
    "CAM_SGSum_OV_RailEnd": ((CX - 7.5, CY + 19.0, Z + 4.8), (CX - 16.3, CY + 13.2, Z + 1.4), 28),
}

# ------------------------------------------------------------------ rotas e sondas proprias (sg_qa)
class _OnlyBuilt(dict):
    """ONDA 2 (o2b): as rotas desta zona so valem com o MODULO construido. Com a invocacao em BLOCKOUT (estudio de outra
    zona sem --all-detail) a colisao do blockout (COL_SG_SumTower, 4 x 16 x 22 no pe da torre) fecha o nicho do
    portal e o QA acusava 'sg_summon:PAD->PATAMAR' OBSTACULO (-214,4; -222) - nao era defeito da invocacao."""

    def items(self):
        return dict.items(self) if bpy.data.objects.get("SG_Sum_Base") else []

    def __iter__(self):
        return iter(dict.__iter__(self) if bpy.data.objects.get("SG_Sum_Base") else [])


_TOP = L.stair_top("Summon")
_PAD = tuple(P(0.0, PAD_V).xy)
EXTRA_ROUTES = _OnlyBuilt({
    # pad do jogador -> sobe a escada da torre -> patamar diante do portal
    "PAD->PATAMAR": ([_PAD, tuple(P(0.0, ST_FOOT + 0.4).xy), tuple(P(0.0, ST_FOOT - 1.0).xy),
                      tuple(P(0.0, LAND_V1 + 0.6).xy), tuple(P(0.0, LAND_V1 - 1.0).xy), tuple(P(0.0, PV + 2.0).xy)], Z),
    # topo da escada -> volta pelo norte e pelo sul, entre o podio e a balaustrada, ate o canto do soco
    "ESCADA->LADO_NORTE": ([(_TOP[0] - 1.5, _TOP[1])] + [(CX + 18.0 * math.cos(math.radians(a)),
                                                          CY + 18.0 * math.sin(math.radians(a)))
                                                         for a in (20.0, 50.0, 80.0, 105.0, 128.0)], Z),
    "ESCADA->LADO_SUL": ([(_TOP[0] - 1.5, _TOP[1])] + [(CX + 18.0 * math.cos(math.radians(a)),
                                                        CY + 18.0 * math.sin(math.radians(a)))
                                                       for a in (-20.0, -50.0, -80.0, -105.0, -128.0)], Z),
})
EXTRA_PROBES = []


# ------------------------------------------------------------------ utilidades de geometria
def top_prism(mb, pts, z0, z1, m):
    """prisma sem a face de baixo (inlay/aro assentado no piso: o fundo nunca aparece)"""
    pts = SL.ccw(pts)
    vb = [mb.bm.verts.new((p[0], p[1], z0)) for p in pts]
    vt = [mb.bm.verts.new((p[0], p[1], z1)) for p in pts]
    n = len(pts)
    mb.bm.faces.new(vt)
    for i in range(n):
        j = (i + 1) % n
        mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m, None, 0, 1)


def side_prism(mb, Fr, prof, y0, y1, m):
    """poligono CONVEXO (x, z) no plano vertical do referencial Fr, extrudado na lateral de y0 a y1"""
    bm = mb.bm
    a = [bm.verts.new(Fr.p(x, y0, z)) for x, z in prof]
    b = [bm.verts.new(Fr.p(x, y1, z)) for x, z in prof]
    n = len(prof)
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


def arc_piece(cx, cy, r0, r1, a0, a1, step=4.0):
    n = max(1, int(math.ceil(abs(a1 - a0) / step)))
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
              cy + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
              cy + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return outer + inner


def local_poly(pts_uv):
    return [tuple(P(u, v).xy) for u, v in pts_uv]


def base_outline(hw, vf, rb, step=6.0):
    """contorno (u, v) do podio/soco: frente reta em vf, laterais retas em +-hw, fundo em arco de raio rb em volta
    do centro da plataforma (0, C_V). Devolve (lateral_direita, arco, lateral_esquerda) para montar pecas convexas"""
    vs = _side_v(hw, rb)
    a0 = math.degrees(math.atan2(vs - C_V, hw))
    a1 = -180.0 - a0
    n = max(2, int(math.ceil(abs(a1 - a0) / step)))
    arc = [(rb * math.cos(math.radians(a0 + (a1 - a0) * i / n)), C_V + rb * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
           for i in range(n + 1)]
    return vs, arc


# ------------------------------------------------------------------ torre (codigo da Ilha 1)
_TOWER = None


def tower_mod():
    """importa il_summon com a planta desta ilha (valores do il_layout trocados so durante o import)"""
    global _TOWER
    if _TOWER is not None:
        return _TOWER
    import il_layout as NL
    want = {"SUMMON_TOWER": (TX, TY), "SUMMON_FACE_DEG": L.SUMMON_FACE_DEG, "T1": Z, "SUMMON_C": (CX, CY),
            "SUMMON_R": R}
    saved = {k: getattr(NL, k) for k in want}
    for k, v in want.items():
        setattr(NL, k, v)
    try:
        if "il_summon" in sys.modules:
            T = importlib.reload(sys.modules["il_summon"])
        else:
            T = importlib.import_module("il_summon")
    finally:
        for k, v in saved.items():
            setattr(NL, k, v)
    assert abs(T.Z0 - Z) < 1e-6 and abs(T.TX - TX) < 1e-6 and abs(T.TY - TY) < 1e-6 and abs(T.YAW - YAW) < 1e-9
    for a, b in ((T.ST_FOOT, ST_FOOT), (T.LAND_Z, LAND_Z), (T.PV, PV), (T.CORR, CORR), (T.POD_TOP, POD_TOP),
                 (T.AX, AX), (T.ZS, ZS), (T.LAND_V[1], LAND_V1), (T.IN_PED[0], IN_PED[0]), (T.IN_PED[1], IN_PED[1])):
        assert abs(a - b) < 1e-6, (a, b)
    _TOWER = T
    return T


@contextmanager
def tower_palette():
    """materiais da Ilha 1 -> SMATS so enquanto a torre e montada (o MB.finish aplica fm_lib.alias)"""
    saved = dict(fm_lib.MAT_ALIAS)
    for k, v in TOWER_ALIAS.items():
        fm_lib.MAT_ALIAS[k] = v
        fam = fm_lib.FAMILIES.get(k)
        if fam:
            for n, _ in fam[1]:
                fm_lib.MAT_ALIAS[n] = v
    try:
        yield
    finally:
        fm_lib.MAT_ALIAS.clear()
        fm_lib.MAT_ALIAS.update(saved)


def tower_body(T, stone, gold, glow):
    """PORTADO de il_summon.tower_stone (so a torre: corpo L1 com o nicho, frontispicio, frontao, cornijas, L2 com a
    janela-estrela, coroa L3). O soco, o podio de 32 de largura e a escada com bordas de brilho da Ilha 1 ficam de fora
    (a base desta ilha e a de base())."""
    rng = random.Random(621)
    lbox, lbox2, face_skin, larch, _buttress = T.lbox, T.lbox2, T.face_skin, T.larch, T._buttress
    PORT_HW, PORT_SPRING, NICHE_TOP, MAST_V = T.PORT_HW, T.PORT_SPRING, T.NICHE_TOP, T.MAST_V
    L1_SWIN, L1_BWIN, BUT_V = T.L1_SWIN, T.L1_BWIN, T.BUT_V
    # --- corpo L1: nucleo com o NICHO do portal (fundo em PV) + contrafortes de canto + pele de alvenaria
    hw, v0, v1, z0, z1 = T.L1
    nw = PORT_HW + 0.8
    lbox2(stone, -hw, v0, z0, hw, PV, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        lbox2(stone, s * nw, PV, z0, s * hw, v1, z1, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -nw, PV, NICHE_TOP, nw, v1, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Summon_Stone" if k % 2 == 0 else "Stone_SumBlock"
            lbox(stone, (0.8, v1 - PV - 0.1, zz1 - zz0 - 0.08), s * (PORT_HW + 0.4), (PV + v1) / 2, (zz0 + zz1) / 2,
                 m, 0.0)
    larch(stone, 0.0, (PV + v1) / 2, 2 * PORT_HW, PORT_SPRING, PORT_HW, v1 - PV - 0.1, m="Summon_Stone",
          key_m="Stone_SumBlock", n=9, band=2.4, keystone=False, seed=1)
    s_side = (v1 - 0.6) - MAST_V
    side_op = (s_side - 1.75, s_side + 1.75, L1_SWIN[0] - 0.2, L1_SWIN[1] + L1_SWIN[2] + 0.5, L1_SWIN[2] + 0.45)
    for s in (-1, 1):
        face_skin(stone, (s * (hw + 0.25), v1 - 0.6), (s * (hw + 0.25), v0 + 0.6), z0, z1, rng, course=2.1,
                  blk=(2.6, 4.2), thick=0.8, openings=[side_op])
        for dv in (-1, 1):
            lbox(stone, (0.9, 0.7, L1_SWIN[1] - L1_SWIN[0]), s * (hw + 0.5), MAST_V + dv * (L1_SWIN[2] + 0.35),
                 (L1_SWIN[0] + L1_SWIN[1]) / 2, "Summon_Stone", 0.0)
    back_op = (hw - 0.6 - 2.1, hw - 0.6 + 2.1, L1_BWIN[0] - 0.2, L1_BWIN[1] + L1_BWIN[2] + 0.6, L1_BWIN[2] + 0.5)
    face_skin(stone, (hw - 0.6, v0 - 0.25), (-hw + 0.6, v0 - 0.25), z0, z1, rng, course=2.1, blk=(2.6, 4.2),
              thick=0.8, openings=[back_op])
    for s in (-1, 1):
        lbox(stone, (0.75, 0.9, L1_BWIN[1] - L1_BWIN[0]), s * (L1_BWIN[2] + 0.38), v0 - 0.5,
             (L1_BWIN[0] + L1_BWIN[1]) / 2, "Summon_Stone", 0.0)
    for su in (-1, 1):
        for vv in (v0, BUT_V):
            _buttress(stone, gold, su * hw, vv, z0, 22.2, 2.5, rng, spire=2.8,
                      edges=((-1, 1), (1, 1)) if vv > 0 else ((-1, -1), (1, -1)))
    face_skin(stone, (-hw + 0.9, v1 + 0.35), (hw - 0.9, v1 + 0.35), 16.8, z1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, quoins=(False, False), base_dark=False)
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Stone_SumBlock" if k % 2 == 0 else "Summon_Stone"
            w = 2.3 if k % 2 == 0 else 2.0
            lbox(stone, (w, 2.9, zz1 - zz0 - 0.08), s * (PORT_HW + 1.1), 2.55, (zz0 + zz1) / 2, m, 0.14)
        lbox2(stone, s * (PORT_HW + 0.35), v1, PORT_SPRING, s * 6.3, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -PORT_HW - 0.4, v1, PORT_SPRING + PORT_HW + 0.2, PORT_HW + 0.4, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    larch(stone, 0.0, 2.6, 2 * PORT_HW, PORT_SPRING, PORT_HW, 2.9, n=9, band=1.5, keystone=True, seed=2)
    apex = (0.0, 22.6)
    for s in (-1, 1):
        a = P(s * 6.9, 3.45, 17.6)
        b = P(apex[0], 3.45, apex[1])
        stone.beam(a, b, 1.9, 1.2, "Stone_SumBlock", 0.0)
        ga = P(s * 7.2, 3.55, 18.45)
        gb = P(0.0, 3.55, apex[1] + 0.85)
        gold.beam(ga, gb, 2.2, 0.6, "Metal_Gold", 0.0)
    tri = [(-6.3, 17.6), (6.3, 17.6), (0.0, apex[1] - 0.2)]
    PK.plate(stone, tri, P(0.0, 3.0, 0.0), XU, ZZ, 1.0, "Summon_Stone_Dark")
    # --- cornija 1
    lbox2(stone, -hw - 1.0, v0 - 1.0, z1, hw + 1.0, 2.4, z1 + 0.6, "Summon_Stone_Dark", 0.0)
    lbox2(gold, -hw - 1.3, v0 - 1.3, z1 + 0.6, hw + 1.3, 2.6, z1 + 1.3, "Metal_Gold", 0.0)
    # --- corpo L2
    hw2, w0, w1, y0, y1 = T.L2
    lbox2(stone, -hw2, w0, y0, hw2, w1, y1, "Summon_Stone_Dark", 0.0)
    wcs = hw2 - 0.2
    win_front = (wcs - 3.5, wcs + 3.5, y0 + 1.0, y0 + 6.8 + 3.5, 3.5)
    face_skin(stone, (-hw2 + 0.2, w1 + 0.35), (hw2 - 0.2, w1 + 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    face_skin(stone, (hw2 - 0.2, w0 - 0.35), (-hw2 + 0.2, w0 - 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    ln_side = (w1 - 0.6) - (w0 + 0.6)
    for s in (-1, 1):
        a_uv = (s * (hw2 + 0.35), w1 - 0.6) if s > 0 else (s * (hw2 + 0.35), w0 + 0.6)
        b_uv = (s * (hw2 + 0.35), w0 + 0.6) if s > 0 else (s * (hw2 + 0.35), w1 - 0.6)
        side_win = (ln_side / 2 - 2.3, ln_side / 2 + 2.3, y0 + 2.4, y0 + 8.6, 2.3)
        face_skin(stone, a_uv, b_uv, y0, y1, rng, course=1.8, blk=(2.2, 3.6), thick=0.8, openings=[side_win])
    for su in (-1, 1):
        for vv in (w0, w1):
            _buttress(stone, gold, su * hw2, vv, y0, y1 + 1.4, 1.9, rng, spire=3.3, course=1.6)
    larch(stone, 0.0, w1 + 0.4, 5.2, y0 + 6.8, 2.6, 1.3, n=7, band=0.9, keystone=True, seed=3)
    for s in (-1, 1):
        lbox2(stone, s * 2.6, w1 - 0.1, y0 + 1.4, s * 3.5, w1 + 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lbox2(gold, -3.8, w1 - 0.1, y0 + 0.85, 3.8, w1 + 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    # overhaul 10: a janela de TRAS do L2 tinha so o arco de prata solto 0,2 fora da parede (flutuante): ganha o mesmo
    # emolduramento da frente (arco de aduelas, ombreiras e peitoril), espelhado
    larch(stone, 0.0, w0 - 0.4, 5.2, y0 + 6.8, 2.6, 1.3, n=7, band=0.9, keystone=True, seed=4)
    for s in (-1, 1):
        lbox2(stone, s * 2.6, w0 + 0.1, y0 + 1.4, s * 3.5, w0 - 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lbox2(gold, -3.8, w0 + 0.1, y0 + 0.85, 3.8, w0 - 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    # --- cornija 2
    lbox2(stone, -hw2 - 0.9, w0 - 0.9, y1, hw2 + 0.9, w1 + 0.9, y1 + 0.5, "Summon_Stone_Dark", 0.0)
    lbox2(gold, -hw2 - 1.2, w0 - 1.2, y1 + 0.5, hw2 + 1.2, w1 + 1.2, y1 + 1.15, "Metal_Gold", 0.0)
    # --- coroa L3 + pinaculos
    h3, c0, c1, q0, q1 = T.L3
    lbox2(stone, -h3, c0, q0, h3, c1, q1, "Summon_Stone_Dark", 0.0)
    for (a_uv, b_uv) in (((-h3 - 0.3, c1 + 0.3), (h3 + 0.3, c1 + 0.3)), ((h3 + 0.3, c0 - 0.3), (-h3 - 0.3, c0 - 0.3)),
                         ((h3 + 0.3, c1 + 0.3), (h3 + 0.3, c0 - 0.3)), ((-h3 - 0.3, c0 - 0.3), (-h3 - 0.3, c1 + 0.3))):
        face_skin(stone, a_uv, b_uv, q0, q1 - 0.25, rng, course=1.9, blk=(2.0, 3.2), thick=0.7, quoins=(False, False))
    lbox2(gold, -h3 - 0.8, c0 - 0.8, q1 - 0.25, h3 + 0.8, c1 + 0.8, q1 + 0.35, "Metal_Gold", 0.0)
    for su in (-1, 1):
        for vv in (c0, c1):
            _buttress(stone, gold, su * h3, vv, q0, q1 + 0.9, 1.3, rng, spire=1.8, course=1.4)


def masts(T, stone, gold, glow):
    """PORTADO de il_summon.masts_and_lanterns (so os mastros com estandartes e as lanternas penduradas; os 4
    pedestais de lanterna japonesa e os postes do pe da escada da Ilha 1 nao entram)"""
    K = T.K
    rng = random.Random(651)
    bn = MB("SG_Sum_Tower_Banners", COL, rng, detail="near")
    hw, v0, v1, z0, z1 = T.L1
    hw2, w0, w1, y0, y1 = T.L2
    MAST_U, MAST_V, BAN_TH = T.MAST_U, T.MAST_V, T.BAN_TH
    z_pole = 29.8
    for s in (-1, 1):
        u = s * MAST_U
        T._buttress(stone, gold, u, MAST_V, POD_TOP, 31.0, 2.0, rng, spire=3.0, course=2.0, edges=((s, 1), (s, -1)))
        for zc in (13.0, 22.5):
            T.lbox(gold, (2.4, 2.4, 0.5), u, MAST_V, zc, "Metal_Gold", 0.0)
        T.lbox2(stone, s * (hw - 0.1), MAST_V - 0.95, POD_TOP, s * (MAST_U - 0.9), MAST_V + 0.95, 12.0,
                "Summon_Stone", 0.0)
        T.lbox2(gold, s * (hw - 0.1), MAST_V - 1.15, 12.0, s * (MAST_U - 0.7), MAST_V + 1.15, 12.5, "Metal_Gold", 0.0)
        # (overhaul 10: as 2 estrelas de 4 pontas da asa sairam - 10.02, um sistema de simbolos so)
        T.lbox2(stone, s * (hw + 0.8), MAST_V - 0.8, z1, s * (MAST_U - 0.9), MAST_V + 0.8, z1 + 0.9,
                "Summon_Stone_Dark", 0.0)
        mw = P(u, MAST_V, 0.0)
        Fb = Frame(mw.x, mw.y, Z, YAW + s * BAN_TH)
        ub = Vector(Fb.p(1, 0, 0)) - Vector(Fb.p(0, 0, 0))
        stub = (MAST_U - (hw2 + 0.35)) / math.cos(BAN_TH)
        a = Fb.p(-s * stub, 0.0, z_pole)
        b = Fb.p(s * 7.0, 0.0, z_pole)
        bn.rod(a, b, 0.3, "Wood_Dark", 8)
        K.spike(gold, b, b + ub * (s * 1.5), 0.45, "Metal_Gold", 4)
        gold.ico(0.5, Fb.p(s * 6.8, 0.0, z_pole), "Metal_Gold", 1)
        for uu in (-s * (stub - 0.25), s * 1.3, s * 5.9):
            gold.box((0.4, 0.8, 0.8), Fb.p(uu, 0.0, z_pole), Fb.r(), "Metal_Gold", 0.0)
        # refino v2b: o estandarte do kit da Ilha 1 trazia outro simbolo (rosa-dos-ventos) -> estandarte da ORDEM
        # (sg_emblem, debrum dourado) no mesmo vao do mastro, olhando para a frente da torre
        EM.banner(bn, gold, bn, bn, tuple(Fb.p(s * 3.6, 0.0, z_pole - 0.5)), YAW + s * BAN_TH + math.pi / 2,
                  4.2, 12.6, trim="Metal_Gold")
        # overhaul 10 (12.01): a lanterna pendurada da Ilha 1 (caixa de Neon + piramide) virou a lanterna da ORDEM do
        # kit (sg_emblem.lantern_head) pendurada da haste por um tirante
        hang_lantern(gold, glow, Fb.p(-s * 2.4, 0.0, z_pole - 0.3), 1.0)
    # 15.05: o crescente dos estandartes e pedra violeta SEM emissao (o Neon fica no emblema monumental)
    return finish_quiet(bn)


def finish_quiet(mb):
    """finish com o crescente do emblema em Stone_SG_Violet (sem Neon): estandartes e placas (auditoria 15.05)"""
    saved = fm_lib.MAT_ALIAS.get(EM.MOON)
    fm_lib.MAT_ALIAS[EM.MOON] = "Stone_SG_Violet"
    try:
        return mb.finish()
    finally:
        if saved is None:
            fm_lib.MAT_ALIAS.pop(EM.MOON, None)
        else:
            fm_lib.MAT_ALIAS[EM.MOON] = saved


def hang_lantern(metal, glow, top, s=1.0):
    """lanterna da ordem (kit) PENDURADA: tirante de ferro de 'top' (mundo, embaixo da haste) ate o colar do remate.
    Devolve o centro do vidro."""
    top = Vector(top)
    tip = top.z - 0.55                                   # ponta do remate da lanterna
    metal.rod(top + ZZ * 0.1, Vector((top.x, top.y, tip - 0.2 * s)), 0.07, EM.L_IRON, 6)
    metal.cyl(0.13, 0.12, (top.x, top.y, top.z - 0.02), (0, 0, 0), EM.L_IRON, 6, bevel=0.0)    # argola na haste
    base = tip - 2.30 * s
    return EM.lantern_head(metal, glow, (top.x, top.y, base + EM.LH_BASE * s), YAW + math.pi / 2, s)


LAMP_PED_S = 1.45        # lanterna da ordem sobre os pedestais internos (ladeando o portal)


def in_pedestal(T, stone, silver, u, v):
    """PORTADO de il_summon.in_pedestal (overhaul 10): o dado 3 x 3 x 3 sem a estrela de 4 pontas e sem a bacia de
    cristal; plinto escuro chanfrado, base moldurada, dado com PAINEL REBAIXADO entre 4 pilastras de quina e capitel em
    2 degraus (pedra + prata). Devolve a cota (local) do topo."""
    side, hgt = T.IN_PED[2], T.IN_PED[3]
    z = POD_TOP
    lb = T.lbox
    lb(stone, (side + 0.5, side + 0.5, 0.42), u, v, z + 0.21, "Summon_Stone_Dark", 0.08)
    lb(stone, (side + 0.22, side + 0.22, 0.22), u, v, z + 0.53, "Summon_Stone", 0.06)
    z0, z1 = z + 0.64, z + hgt - 0.5
    lb(stone, (side - 0.36, side - 0.36, z1 - z0), u, v, (z0 + z1) / 2, "Stone_SumBlock", 0.0)
    for du in (-1, 1):
        for dv in (-1, 1):
            lb(stone, (0.62, 0.62, z1 - z0), u + du * (side / 2 - 0.31), v + dv * (side / 2 - 0.31), (z0 + z1) / 2,
               "Summon_Stone", 0.06)
    lb(stone, (side + 0.12, side + 0.12, 0.2), u, v, z1 + 0.1, "Summon_Stone", 0.05)
    lb(silver, (side + 0.42, side + 0.42, 0.28), u, v, z1 + 0.2 + 0.14, "Metal_Gold", 0.03)
    return z1 + 0.48


def pedestal_lantern(metal, glow, base):
    """lanterna da ordem (kit hexagonal: vidro recuado, montantes, beiral, remate) no lugar da antiga lanterna gotica
    local (caixa de Neon + agulha de 4 aguas). base = (x, y, z) do topo do pedestal. Devolve o centro do vidro."""
    b = Vector(base)
    return EM.lantern_head(metal, glow, (b.x, b.y, b.z + EM.LH_BASE * LAMP_PED_S), YAW + math.pi / 2, LAMP_PED_S)


@contextmanager
def portal_stars_only(T):
    """OVERHAUL 10 (10.02/16.07): a torre da Ilha 1 espalha ~20 estrelas (frontao, cornija, coroa, contrafortes,
    janelas do L1 e do L2, janela de tras) - um SEGUNDO sistema de simbolos contra o emblema da ordem. Durante o
    tower_details NENHUMA estrela passa: a estrela do portal (a funcao gacha) e redesenhada em portal_veil, integrada
    ao veu; a da esfera continua (sphere). Revisao do coordenador: o painel chapado de Neon do portal e os das janelas
    altas do L2 (frente e tras) tambem sao interceptados - viram camadas recuadas (portal_veil / window_veil); o
    circulo de invocacao do patamar anda 0,8 para a frente para caber a soleira (o marcador e a interacao nao mudam)."""
    K, PKm = T.K, T.PK
    orig_star, orig_plate, orig_ring = K.star, PKm.plate, PKm.ring
    hw2, w0, w1, y0, y1 = T.L2

    def star(*a, **kw):
        return None

    def plate(mb, pts2d, origin, u, v, thick, m, *a, **kw):
        if m == "Crystal_SumPortal_Glow":
            lu, lv = to_local(origin[0], origin[1])
            if abs(lu) < 0.5 and (abs(lv - (PV + 0.08)) < 0.05 or abs(lv - (w1 + 0.12)) < 0.05
                                  or abs(lv - (w0 - 0.12)) < 0.05):
                return None
        return orig_plate(mb, pts2d, origin, u, v, thick, m, *a, **kw)

    def ring(mb, c, R, u, v, *a, **kw):
        lu, lv = to_local(c[0], c[1])
        if abs(lu) < 0.3 and abs(lv - ((PV + LAND_V1) / 2 - 0.6)) < 0.05 and abs(c[2] - (Z + LAND_Z)) < 0.05:
            c = P(0.0, lv + 0.8, LAND_Z)
        return orig_ring(mb, c, R, u, v, *a, **kw)
    K.star, PKm.plate, PKm.ring = star, plate, ring
    try:
        yield
    finally:
        K.star, PKm.plate, PKm.ring = orig_star, orig_plate, orig_ring


fm_lib.MATS.setdefault("SG_SumPortalDeep_Glow", (_S(34, 24, 98), 0.3, 0.0, 0.45, _S(40, 28, 116), 0.0))
fm_lib.RBX_CAL.setdefault("SG_SumPortalDeep_Glow",
                          (None, [int(c) for c in fm_lib.to_srgb(fm_lib.MATS["SG_SumPortalDeep_Glow"][0])]))


def _qprism(mb, Q, pts, d0, d1, m):
    """poligono CONVEXO [(a, z)] no plano do vao, extrudado de d0 a d1 (Q(a, d, z) -> mundo)"""
    import bmesh
    bm = mb.bm
    va = [bm.verts.new(Q(a_, d0, z_)) for a_, z_ in pts]
    vb = [bm.verts.new(Q(a_, d1, z_)) for a_, z_ in pts]
    fs = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(va + vb, m, None, 0, 1)


def _arch_full(mb, Q, hw, z0, zs, d0, d1, m, n=12):
    pts = [(-hw, z0), (hw, z0), (hw, zs)] + [(hw * math.cos(math.pi * i / n), zs + hw * math.sin(math.pi * i / n))
                                               for i in range(1, n)] + [(-hw, zs)]
    _qprism(mb, Q, pts, d0, d1, m)


def _arch_band(mb, Q, hw_o, hw_i, z0, zs, d0, d1, m, n=12):
    """faixa em arco pleno (ombreiras + meia coroa) entre hw_i e hw_o: pecas convexas"""
    for sg in (-1, 1):
        a0, a1 = sorted((sg * hw_i, sg * hw_o))
        _qprism(mb, Q, [(a0, z0), (a1, z0), (a1, zs), (a0, zs)], d0, d1, m)
    for i in range(n):
        t0, t1 = math.pi * i / n, math.pi * (i + 1) / n
        _qprism(mb, Q, [(hw_i * math.cos(t0), zs + hw_i * math.sin(t0)), (hw_o * math.cos(t0), zs + hw_o * math.sin(t0)),
                        (hw_o * math.cos(t1), zs + hw_o * math.sin(t1)), (hw_i * math.cos(t1), zs + hw_i * math.sin(t1))],
                d0, d1, m)


def portal_veil(T, stone, silver, glow):
    """REVISAO (coordenador): o portal deixa de ser um painel chapado de Neon com a estrela colada. Dentro do nicho, VEU
    em 3 camadas RECUADAS que se fecham para o fundo (funil de arquivoltas, a linguagem do portal de aduelas da
    dungeon): faixa da frente em violeta medio, moldura interna de pedra, faixa do meio indigo e o fundo quase
    preto-violeta; a estrela (menor, em baixo relevo) fica NO fundo, cercada por um aro de prata - le como o nucleo do
    portal, nao como adesivo. Soleira de pedra na base (o veu assenta nela). As 9 faiscas sairam."""
    hw, zs = T.PORT_HW, T.PORT_SPRING
    zb = LAND_Z + 0.34                                   # topo da soleira

    def Q(a_, d, z_):
        return P(a_, PV + d, z_)
    # soleira: 3 pedras chanfradas (a do meio mais larga) do fundo do nicho ate 1,15 dele
    for u0, u1 in ((-hw - 0.3, -1.6), (-1.56, 1.56), (1.6, hw + 0.3)):
        T.lbox(stone, (u1 - u0, 1.15, 0.36), (u0 + u1) / 2, PV + 0.575, LAND_Z + 0.16, "Summon_Stone", 0.06)
    # fundo (mais escuro), faixa do meio (indigo), moldura interna (pedra), faixa da frente (violeta medio)
    _arch_full(glow, Q, 2.35, zb, zs, 0.02, 0.16, "SG_SumPortalDeep_Glow")
    _arch_band(glow, Q, 3.2, 2.25, zb, zs, 0.45, 0.6, "Crystal_SumPortal_Glow")
    _arch_band(stone, Q, 3.42, 3.12, zb, zs, 0.3, 0.98, "Stone_SumBlock")
    _arch_band(glow, Q, hw - 0.05, 3.36, zb, zs, 0.82, 0.95, "Crystal_SumStar_Glow")
    # nucleo: estrela de 5 pontas em baixo relevo no fundo + aro de prata
    zc = zb + (zs - zb) * 0.62
    _STAR[0](glow, Q(0.0, 0.22, zc), XU, ZZ, 5, 1.25, 0.52, 0.12, "Crystal_SumStar_Glow", edge=0.1)
    T.PK.ring(silver, Q(0.0, 0.2, zc), 1.62, XU, ZZ, 0.16, 0.2, "Metal_Gold", 0, 360, 24)


def window_veil(T, glow):
    """o mesmo veu recuado nas 2 janelas altas do L2 (frente e tras): fundo escuro + faixa indigo; o rendilhado de
    pedra (window_tracery) fica na frente"""
    hw2, w0, w1, y0, y1 = T.L2
    for vb, sg in ((w1, 1.0), (w0, -1.0)):
        def Q(a_, d, z_, vb=vb, sg=sg):
            return P(a_, vb + sg * d, z_)
        _arch_full(glow, Q, 2.6, y0 + 1.4, y0 + 6.8, -0.05, 0.05, "SG_SumPortalDeep_Glow")
        _arch_band(glow, Q, 2.6, 1.9, y0 + 1.4, y0 + 6.8, 0.12, 0.22, "Crystal_SumPortal_Glow", n=8)


_STAR = [None]


def window_tracery(T, stone):
    """OVERHAUL 10: sem a estrela, os vitrais de energia do L2 (frente, tras e lados) e do L1 (lados) ganham RENDILHADO
    de pedra na frente do vidro: mainel do peitoril a nascenca e, nos largos, os 2 ramos em Y ate o arco pleno - a
    janela le como janela (moldura + recuo + vidro + caixilho), nao como placa de brilho."""
    hw, v0, v1, z0, z1 = T.L1
    hw2, w0, w1, y0, y1 = T.L2
    m = "Stone_SumBlock"

    def front(v, sgn, whw, zsill, zsp, y_branch):
        vv = v + sgn * 0.3
        T.lbox(stone, (0.3, 0.32, zsp - zsill + 0.1), 0.0, vv, (zsill + zsp) / 2, m, 0.0)
        if y_branch:
            r = whw * 0.72
            for su in (-1, 1):
                stone.beam(P(0.0, vv, zsp - 0.05), P(su * r, vv, zsp + r), 0.32, 0.28, m, 0.0)

    def side(u, sgn, v, whw, zsill, zsp, y_branch):
        uu = u + sgn * 0.3
        T.lbox(stone, (0.32, 0.3, zsp - zsill + 0.1), uu, v, (zsill + zsp) / 2, m, 0.0)
        if y_branch:
            r = whw * 0.72
            for sv in (-1, 1):
                stone.beam(P(uu, v, zsp - 0.05), P(uu, v + sv * r, zsp + r), 0.32, 0.28, m, 0.0)
    front(w1 + 0.12, 1.0, 2.6, y0 + 1.4, y0 + 6.8, True)          # L2 frente (a janela-estrela antiga)
    front(w0 - 0.12, -1.0, 2.6, y0 + 1.4, y0 + 6.8, True)         # L2 tras
    vs = (w0 + w1) / 2
    for su in (-1, 1):
        side(su * (hw2 + 0.12), su, vs, 2.1, y0 + 2.4, y0 + 6.5, True)
        zs0, zsp, shw = T.L1_SWIN
        side(su * (hw + 0.1), su, T.MAST_V, shw, zs0, zsp, False)


def tower_collision(T):
    """PORTADO de il_summon.tower_collision (so a torre; a base e de base_collision)"""
    A = "SG_SumTower"

    def lc2(u0, v0, z0, u1, v1, z1):
        c = P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
        col_box(A, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), c, (0, 0, YAW))
    hw, v0, v1, z0, z1 = T.L1
    lc2(-hw - 1.3, v0 - 1.3, POD_TOP, hw + 1.3, PV, T.L3[4])                          # corpo atras do plano do portal
    lc2(-hw - 1.3, PV, T.PORT_SPRING + T.PORT_HW, hw + 1.3, v1 + 0.1, T.L3[4])        # sobre o nicho
    lc2(-T.PORT_HW, v1 + 0.1, T.PORT_SPRING + T.PORT_HW, T.PORT_HW, 4.3, 18.2)        # timpano
    for s in (-1, 1):
        lc2(s * T.PORT_HW, PV, POD_TOP, s * (hw + 1.3), 4.3, 18.2)                    # paredes do nicho + ombreiras
        lc2(s * (hw - 0.1), T.MAST_V - 1.1, POD_TOP, s * (T.MAST_U + 1.0), T.MAST_V + 1.1, 31.0)   # asa + mastro
        ih = T.IN_PED[3] + 0.5 + 5.0
        lc2(s * IN_PED[0] - 1.7, IN_PED[1] - 1.7, POD_TOP, s * IN_PED[0] + 1.7, IN_PED[1] + 1.7, POD_TOP + ih)
    lc2(-CORR, PV, -0.2, CORR, LAND_V1, LAND_Z)                                       # patamar do portal


def build_tower():
    T = tower_mod()
    before = {o.name for o in bpy.data.objects}
    stone = MB("SG_Sum_Tower_Stone", COL, random.Random(620), detail="near")
    gold = MB("SG_Sum_Tower_Silver", COL, random.Random(622), detail="near")
    glow = MB("SG_Sum_Tower_Glow", COL, random.Random(623), detail="hero")
    with tower_palette():
        tower_body(T, stone, gold, glow)
        _STAR[0] = T.K.star
        with portal_stars_only(T):
            cr = T.tower_details(stone, gold, glow)
        portal_veil(T, stone, gold, glow)
        window_veil(T, glow)
        window_tracery(T, stone)
        cr.bm.free()                              # cristais da boca do nicho: fora (liam como minerio)
        masts(T, stone, gold, glow)
        lamp_c = []
        for s in (-1, 1):
            zb = in_pedestal(T, stone, gold, s * IN_PED[0], IN_PED[1])
            lamp_c.append(pedestal_lantern(gold, glow, P(s * IN_PED[0], IN_PED[1], zb)))
        c = T.sphere(gold, glow)
        stone.finish()
        gold.finish()
        glow.finish()
    tower_collision(T)
    # renomeia o que o codigo da Ilha 1 criou: SUM_* -> SG_Sum_*, VFX_SUM_* -> VFX_SGSUM_*; colecao 05 -> 06
    dst = fm_lib.coll(COL)
    for ob in [o for o in bpy.data.objects if o.name not in before]:
        n = ob.name
        if n.startswith("VFX_SUM_"):
            ob.name = "VFX_SGSUM_" + n[len("VFX_SUM_"):]
        elif n.startswith("SUM_"):
            ob.name = "SG_Sum_" + n[len("SUM_"):]
        if ob.type == "MESH":
            ob.data.name = ob.name
        for cl in list(ob.users_collection):
            if cl.name == "05_SUMMON":
                cl.objects.unlink(ob)
                if ob.name not in dst.objects:
                    dst.objects.link(ob)
    c05 = bpy.data.collections.get("05_SUMMON")
    if c05 is not None and not c05.objects and not c05.children:
        bpy.data.collections.remove(c05)
    for ob in bpy.data.objects:
        if ob.name.startswith("VFX_SGSUM_"):
            ob["vfx_zone"] = "summon"
    return T, c, lamp_c


# ------------------------------------------------------------------ base: soco + podio (bastiao no fundo)
def base(bm_stone, bm_trim, T):
    K = T.K
    rng = random.Random(7303)
    # --- soco claro (0 .. 0,8): laterais + faixa da frente dos 2 lados da escada + arco do fundo
    hw_s, vf_s = POD_HW + SOC_OFF, POD_VF + SOC_OFF
    vs_s, arc_s = base_outline(hw_s, vf_s, SOC_RB)
    for s in (-1, 1):
        bm_stone.prism(SL.ccw(local_poly([(s * CORR, vs_s), (s * hw_s, vs_s), (s * hw_s, vf_s), (s * CORR, vf_s)])),
                       -0.6 + Z, PLZ + Z, "Stone_SG_Block")
    bm_stone.prism(SL.ccw(local_poly([(-CORR, vs_s), (CORR, vs_s), (CORR, PV), (-CORR, PV)])), -0.6 + Z, PLZ + Z,
                   "Stone_SG_Block")
    bm_stone.prism(SL.ccw(local_poly(arc_s)), -0.6 + Z, PLZ + Z, "Stone_SG_Block")
    # --- podio (0,8 .. 3,3): laterais, meio (atras do patamar) e fundo em arco
    hw, vf = POD_HW, POD_VF
    vs, arc = base_outline(hw, vf, POD_RB)
    zc0, zc1 = Z + PLZ, Z + POD_TOP
    pieces = [[(s * CORR, vs), (s * hw, vs), (s * hw, vf), (s * CORR, vf)] for s in (-1, 1)]
    pieces.append([(-CORR, vs), (CORR, vs), (CORR, PV), (-CORR, PV)])
    pieces.append(arc)
    for pc in pieces:
        bm_stone.prism(SL.ccw(local_poly(pc)), zc0 - 0.1, zc1 - 0.4, "Stone_SG_Castle")
    # rodape (fiada de base mais escura, 0,25 para fora) e capa de cantaria clara (0,35 para fora) no contorno externo
    outer = [(CORR, vf), (hw, vf), (hw, vs)] + arc[1:-1] + [(-hw, vs), (-hw, vf), (-CORR, vf)]
    for i in range(len(outer) - 1):
        (ua, va), (ub, vb) = outer[i], outer[i + 1]
        a, b = P(ua, va), P(ub, vb)
        d = (b - a)
        ln = d.length
        if ln < 0.3:
            continue
        nrm = Vector((d.y, -d.x, 0.0)).normalized()      # para fora (contorno horario no referencial -> conferir)
        mid = (a + b) / 2
        # o lado de fora e o que se afasta do eixo da torre
        cen = P(0.0, 0.0)
        if (mid - cen).dot(nrm) < 0:
            nrm = -nrm
        ang = math.atan2(d.y, d.x)
        for (z0, z1, off, m) in ((zc0 - 0.1, zc0 + 0.55, 0.22, "Stone_SG_Floor"),
                                 (zc1 - 0.45, zc1, 0.5, CAPL)):
            w = 0.9 + off
            c = mid + nrm * (off - w / 2 + 0.0)
            (bm_trim if m == CAPL else bm_stone).box((ln + (0.7 if m == CAPL else 0.45), w,
                                                                 z1 - z0), (c.x, c.y, (z0 + z1) / 2),
                                                                (0, 0, ang), m, 0.0)
    # tampo do podio (dentro da capa): ardosia escura
    for pc in pieces:
        top_prism(bm_stone, local_poly(pc), zc1 - 0.45, zc1 - 0.02, "Stone_SG_Floor")
    # pilastras (contrafortes baixos) no contorno: frente e laterais a cada ~4, fundo a cada 16 graus.
    # OVERHAUL 10 (10.05): a caixa lisa de 1 x 1 virou pilastra de verdade - base moldurada, fuste de quinas
    # chanfradas e capitel em 2 degraus (cantaria de remate) logo abaixo da capa; entre as pilastras da frente e dos
    # lados, o PAINEL da arcada cega ogival (as estrelas de prata sairam: 10.02)
    pil = []
    for s in (-1, 1):
        for u in (CORR + 0.75, 8.0, hw - 0.5):
            pil.append((s * u, vf, "v+"))
        v = vf - 3.6
        while v > vs + 1.0:
            pil.append((s * hw, v, "u+" if s > 0 else "u-"))
            v -= 4.0
    a0 = math.degrees(math.atan2(vs - C_V, hw))
    a1 = -180.0 - a0
    nk = max(2, int(abs(a1 - a0) / 16.0))
    for k in range(nk + 1):
        a = math.radians(a0 + (a1 - a0) * k / nk)
        pil.append((POD_RB * math.cos(a), C_V + POD_RB * math.sin(a), ("arc", a)))
    zb0, zb1 = PLZ + 0.55, PLZ + 0.8            # base (sobre o rodape)
    zc1 = POD_TOP - 0.45                        # capitel encosta na capa
    zs1 = zc1 - 0.3
    for u, v, face in pil:
        if isinstance(face, tuple):
            a = face[1]
            nu, nv = math.cos(a), math.sin(a)
        else:
            nu, nv = {"v+": (0.0, 1.0), "u+": (1.0, 0.0), "u-": (-1.0, 0.0)}[face]
        tu, tv = -nv, nu

        def Q(dn, dt, z):
            return P(u + nu * dn + tu * dt, v + nv * dn + tv * dt, z)
        rz = YAW + math.atan2(nv, nu)
        # base moldurada (plinto + chanfro de assento)
        bm_stone.box((0.81, 1.3, zb1 - zb0), Q(0.055, 0.0, (zb0 + zb1) / 2), (0, 0, rz), "Stone_SG_Block", 0.06)
        # fuste de quinas chanfradas (sai 0,4 da face)
        dn0, dn1, ht, c = -0.35, 0.3, 0.5, 0.1
        poly = [(dn0, -ht), (dn1 - c, -ht), (dn1, -ht + c), (dn1, ht - c), (dn1 - c, ht), (dn0, ht)]
        bm_stone.prism(SL.ccw([tuple(Q(dn, dt, 0.0).xy) for dn, dt in poly]), Z + zb1, Z + zs1, "Stone_SG_Castle")
        # capitel em 2 degraus
        bm_trim.box((0.71, 1.14, 0.14), Q(0.005, 0.0, zs1 + 0.07), (0, 0, rz), CAPL, 0.03)
        bm_trim.box((0.79, 1.3, 0.16), Q(0.045, 0.0, zs1 + 0.22), (0, 0, rz), CAPL, 0.04)
    # arcada cega ogival: um painel por vao da frente e das laterais (o fundo, virado para o mar, fica liso)
    bays = []
    for s in (-1, 1):
        for uc in ((CORR + 0.75 + 8.0) / 2, (8.0 + hw - 0.5) / 2):
            bays.append((s * uc, vf, "v+"))
        edges = [vf] + [vf - 3.6 - 4.0 * k for k in range(3)] + [vs + 0.6]
        for e0, e1 in zip(edges, edges[1:]):
            bays.append((s * hw, (e0 + e1) / 2, "u+" if s > 0 else "u-"))
    w = 1.0
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.45)]
    for i in range(1, 5):
        aa = math.radians(60.0 * i / 5.0)
        pts.append((w / 2 - w * (1 - math.cos(aa)), 0.45 + w * math.sin(aa)))
    pts.append((0.0, 0.45 + w * math.sin(math.radians(60.0))))
    for i in range(4, 0, -1):
        aa = math.radians(60.0 * i / 5.0)
        pts.append((-(w / 2 - w * (1 - math.cos(aa))), 0.45 + w * math.sin(aa)))
    pts.append((-w / 2, 0.45))
    for u, v, face in bays:
        if face == "v+":
            PK.plate(bm_stone, pts, P(u, v + 0.06, PLZ + 0.62), XU, ZZ, 0.16, "Stone_SG_Floor")
        else:
            sg = 1.0 if face == "u+" else -1.0
            PK.plate(bm_stone, pts, P(u + sg * 0.06, v, PLZ + 0.62), -YV * sg, ZZ, 0.16, "Stone_SG_Floor")


def base_collision():
    A = "SG_SumPodium"

    def lc2(u0, v0, z0, u1, v1, z1):
        c = P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2)
        col_box(A, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), c, (0, 0, YAW))
    hw, vf = POD_HW, POD_VF
    vs = _side_v(hw, POD_RB)
    for s in (-1, 1):
        lc2(s * CORR, vs, -0.6, s * (hw + 0.35), vf + 0.35, POD_TOP)             # podio (lados)
    lc2(-CORR, vs, -0.6, CORR, PV, POD_TOP)                                      # podio (meio, atras do patamar)
    # fundo em arco: 2 caixas dentro do arco
    for uu in (9.0, 5.0):
        vb = C_V - math.sqrt(POD_RB ** 2 - uu ** 2)
        lc2(-uu, vb + 0.1, -0.6, uu, vs if uu == 9.0 else C_V - math.sqrt(POD_RB ** 2 - 81.0) + 0.1, POD_TOP)
    # soco (degrau de 0,8 em volta do podio: frente e lados)
    hs, vfs = hw + SOC_OFF, vf + SOC_OFF
    vss = _side_v(hs, SOC_RB)
    for s in (-1, 1):
        lc2(s * (hw + 0.35), vss, -0.6, s * hs, vfs, PLZ)
        lc2(s * CORR, vf + 0.35, -0.6, s * (hw + 0.35), vfs, PLZ)


# ------------------------------------------------------------------ escada da torre (medidas da Ilha 1, sem brilho)
def tower_stair(stair):
    base = P(0.0, ST_FOOT, 0.0)
    ang = FACE + math.pi
    rise, tread, n, width = 0.8, 1.6, 5, 7.6
    FP.stairs(stair, "SG_SumStair", (base.x, base.y, base.z), ang, width, n, rise=rise, tread=tread,
              m="Stone_Paving_SG", side_m="Stone_SG_Block", stringers=False, col=True)
    Fs = Frame(base.x, base.y, base.z, ang)
    k = rise / tread
    # guardas invisiveis dos banzos (as mesmas do fm_parts.stairs com banzo)
    H = 4.0
    Tt = H + 1.5
    off = k * (tread * k / 2 + H) / (1 + k * k)
    for s in (-1, 1):
        y = s * (width / 2 + 0.6)
        xa, xb = -off, tread * n - off
        SL.col_ramp("SG_SumStair", Fs.p(xa, y, (xa + tread / 2) * k + H), Fs.p(xb, y, (xb + tread / 2) * k + H),
                    1.2, thick=Tt)
    # banzos lisos (sobem ate o patamar e encostam no podio) + capa de cantaria
    x_end = tread * n                                # ate a borda do patamar (v 5,6)
    zt = rise * n
    for s in (-1, 1):
        y0, y1 = s * (width / 2 + 0.05), s * (width / 2 + 1.25)
        prof = [(-0.1, -0.6), (x_end, -0.6), (x_end, zt + 0.9), (tread * n - tread / 2, zt + 0.9),
                (-0.1, 1.05)]
        side_prism(stair, Fs, prof, min(y0, y1), max(y0, y1), "Stone_SG_Block")
        yc = s * (width / 2 + 0.65)
        a = Fs.p(-0.25, yc, 1.05 + 0.18)
        b = Fs.p(tread * n - tread / 2, yc, zt + 0.9 + 0.18)
        stair.beam(a, b, 1.45, 0.36, CAPL, 0.04)
        stair.beam(b, Fs.p(x_end, yc, zt + 0.9 + 0.18), 1.45, 0.36, CAPL, 0.04)
    # patamar do portal (o da Ilha 1: 7 de fundo, do fundo do nicho ate o topo da escada)
    for pc, z0, z1, m in (((-CORR + 0.05, PV, CORR - 0.05, LAND_V1), -0.4, LAND_Z - 0.3, "Stone_SG_Block"),
                          ((-CORR + 0.05, PV, CORR - 0.05, LAND_V1 + 0.1), LAND_Z - 0.3, LAND_Z, "Stone_Paving_SG")):
        u0, v0, u1, v1 = pc
        stair.box(((u1 - u0), (v1 - v0), z1 - z0), P((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2), (0, 0, YAW), m, 0.0)


# ------------------------------------------------------------------ piso: desenho radial discreto + faixa de borda
def floor_inlay(inl):
    zt, zb = Z + 0.05, Z - 0.1
    px, py = P(0.0, PAD_V).xy
    ok = lambda x, y: (not in_base(x, y, 0.5)) and math.hypot(x - CX, y - CY) < R - 1.6
    # aneis em volta do ponto do jogador (cortados pela base da torre e pela borda)
    for r0, r1, m in ((2.35, 2.7, "Stone_SG_Floor"), (6.3, 6.7, "Stone_SG_Floor"), (11.0, 11.45, "Stone_SG_Floor")):
        n = max(12, int(2 * math.pi * r1 / 1.6))
        for i in range(n):
            a0, a1 = 360.0 * i / n, 360.0 * (i + 1) / n
            am = math.radians((a0 + a1) / 2)
            rm = (r0 + r1) / 2
            if not ok(px + rm * math.cos(am), py + rm * math.sin(am)):
                continue
            top_prism(inl, arc_piece(px, py, r0, r1, a0, a1, 6.0), zb, zt, m)
    # raios (12) entre os aneis
    for k in range(12):
        a = math.radians(15.0 + 30.0 * k)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        for ra, rb in ((2.7, 6.3), (6.7, 11.0)):
            pa = Vector((px, py, 0.0)) + d * ra
            pb = Vector((px, py, 0.0)) + d * rb
            q = [pa + (pb - pa) * (t / 6.0) for t in range(7)]
            good = [p for p in q if ok(p.x, p.y)]
            if len(good) < 7:
                continue
            w = 0.3 if ra < 3 else 0.34
            nrm = Vector((-d.y, d.x, 0.0)) * (w / 2)
            top_prism(inl, [tuple((pa + nrm).xy), tuple((pa - nrm).xy), tuple((pb - nrm).xy), tuple((pb + nrm).xy)],
                      zb, zt, m)
    # OVERHAUL 10 (10.02): a estrela de 8 pontas saiu (a estrela fica so no portal e na esfera). No ponto do jogador,
    # uma ROSACEA de cantaria rente ao piso: miolo, aro e 8 raios (desenho de roda/rosacea, nao de estrela), nos
    # mesmos 12 cm do resto do desenho radial
    ring_pts = lambda r0, r1, a0, a1: arc_piece(px, py, r0, r1, a0, a1, 7.5)
    for k in range(8):
        top_prism(inl, ring_pts(1.75, 2.05, 45.0 * k + 22.5, 45.0 * (k + 1) + 22.5), zb, zt + 0.01, CAPL)
    top_prism(inl, [(px + 0.62 * math.cos(2 * math.pi * i / 16), py + 0.62 * math.sin(2 * math.pi * i / 16))
                    for i in range(16)], zb, zt + 0.01, CAPL)
    for k in range(8):
        a = math.radians(22.5 + 45.0 * k)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        nr = Vector((-d.y, d.x, 0.0)) * 0.09
        pa = Vector((px, py, 0.0)) + d * 0.6
        pb = Vector((px, py, 0.0)) + d * 1.77
        top_prism(inl, [tuple((pa + nr).xy), tuple((pa - nr).xy), tuple((pb - nr).xy), tuple((pb + nr).xy)],
                  zb, zt + 0.01, CAPL)
    # faixa de borda (lajes escuras) por dentro da balaustrada, cortada na escada e na base da torre
    for a0 in range(-180, 180, 6):
        a1 = a0 + 6
        am = math.radians(a0 + 3.0)
        rm = (RAIL_R - 1.3)
        x, y = CX + rm * math.cos(am), CY + rm * math.sin(am)
        if in_base(x, y, 0.6) or abs(a0 + 3.0) < GATE_A + 1.0:
            continue
        top_prism(inl, arc_piece(CX, CY, RAIL_R - 1.9, RAIL_R - 0.55, a0, a1, 3.0), zb, zt, "Stone_SG_Block_B")


# ------------------------------------------------------------------ balaustrada gotica baixa (borda, ponte)
# OVERHAUL 10 (10.04/12.12/16.03): colunelo-caixa de 0,32 a cada 1,15 + pilar-caixa com piramide de 4 aguas saiu. A
# balaustrada fala a linguagem de cantaria da entrada: plinto chanfrado, BALAUSTRES TORNEADOS (torno de 6: pe, bojo,
# gargalo, colar), corrimao moldurado (pingadeira + dorso boleado), pilarete com plinto, fuste de quinas chanfradas,
# capitel em 2 degraus e o remate do kit (bola com colar, sg_entry.finial). Os pilares-portao da escada (os NOS) levam a
# lanterna da ordem (order_dressing).
RAIL_BASE, RAIL_COL, RAIL_TOP = 0.5, 1.05, 0.42
BAL_PROF = [(0.19, 0.0), (0.11, 0.17), (0.2, 0.47), (0.1, 0.82), (0.155, 1.0)]
POST_W, POST_H = 1.2, 2.3              # pilarete comum (fuste ate POST_H; capitel ate POST_H + 0,32)
GATE_W, GATE_H = 1.5, 3.0              # pilar-portao (topo da escada)


def _sq_ch(x, y, hw, c, rot):
    pts = [(-hw + c, -hw), (hw - c, -hw), (hw, -hw + c), (hw, hw - c), (hw - c, hw), (-hw + c, hw), (-hw, hw - c),
           (-hw, -hw + c)]
    ca, sa = math.cos(rot), math.sin(rot)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def rail_post(rl, p, rz, wp, hp, finial=True):
    """pilarete (p = pe no nivel do piso). Devolve o topo do capitel."""
    import sg_entry as EN
    x, y, z = p.x, p.y, p.z
    rl.box((wp + 0.32, wp + 0.32, 0.55), (x, y, z + 0.175), (0, 0, rz), REL_M, 0.06)
    rl.prism(SL.ccw(_sq_ch(x, y, wp / 2, 0.15, rz)), z + 0.45, z + hp, PAR_M)
    rl.box((wp + 0.14, wp + 0.14, 0.14), (x, y, z + hp + 0.07), (0, 0, rz), CAPL, 0.03)
    rl.box((wp + 0.36, wp + 0.36, 0.18), (x, y, z + hp + 0.23), (0, 0, rz), CAPL, 0.05)
    top = z + hp + 0.32
    if finial:
        EN.finial(rl, x, y, top, 0.36, m=CAPL, n=6)
    return top


def gothic_rail(rl, pts, z, post_every=7.5, end_posts=(True, True), post_big=()):
    """balaustrada baixa sobre a polilinha 'pts' (2D) na cota z (topo do corrimao em z + 1,97). post_big: indices
    dos pilares-portao (sem remate: recebem a lanterna). Devolve [(topo, pe, rumo)] dos pilares-portao."""
    pts = [Vector((p[0], p[1], z)) for p in pts]
    rl.sweep(pts, [(-0.5, -0.1), (0.5, -0.1), (0.5, 0.36), (0.4, RAIL_BASE), (-0.4, RAIL_BASE), (-0.5, 0.36)],
             PAR_M, True)
    h0 = RAIL_BASE + RAIL_COL
    rl.sweep(pts, [(-0.4, h0), (0.4, h0), (0.47, h0 + 0.14), (0.36, RAIL_TOP + h0), (-0.36, RAIL_TOP + h0),
                   (-0.47, h0 + 0.14)], CAPL, True)
    acc = [0.0]
    for a, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + (b - a).length)
    total = acc[-1]

    def at(s):
        for i in range(len(pts) - 1):
            if acc[i + 1] >= s - 1e-9:
                t = (s - acc[i]) / max(1e-9, acc[i + 1] - acc[i])
                d = (pts[i + 1] - pts[i]).normalized()
                return pts[i] + (pts[i + 1] - pts[i]) * t, d
        d = (pts[-1] - pts[-2]).normalized()
        return pts[-1], d
    npost = max(1, int(round(total / post_every)))
    posts = [(total * k / npost, k) for k in range(npost + 1)]
    if not end_posts[0]:
        posts = posts[1:]
    if not end_posts[1]:
        posts = posts[:-1]
    big = {k for _, k in posts if k in post_big or (k - npost - 1) in post_big}
    # balaustres entre os pilares (passo ~1,1, fora do plinto dos pilares)
    step = 1.2
    for (s0, k0), (s1, k1) in zip([(0.0, -1)] + posts, posts + [(total, -2)]):
        w0 = ((GATE_W if k0 in big else POST_W) + 0.32) / 2 + 0.3 if k0 >= 0 else 0.35
        w1 = ((GATE_W if k1 in big else POST_W) + 0.32) / 2 + 0.3 if k1 >= 0 else 0.35
        a_, b_ = s0 + w0, s1 - w1
        if b_ - a_ < 0.3:
            continue
        nb = max(1, int(round((b_ - a_) / step)) + 1)
        for j in range(nb):
            sc = a_ + (b_ - a_) * (j / (nb - 1) if nb > 1 else 0.5)
            p, d = at(sc)
            EM._lathe(rl, (p.x, p.y, p.z + RAIL_BASE), [(r, hh * RAIL_COL) for r, hh in BAL_PROF], REL_M, 6,
                      math.atan2(d.y, d.x), caps=(False, False))
    tops = []
    for sp, k in posts:
        p, d = at(sp)
        rz = math.atan2(d.y, d.x)
        if k in big:
            tops.append((rail_post(rl, p, rz, GATE_W, GATE_H, finial=False), p, rz))
        else:
            rail_post(rl, p, rz, POST_W, POST_H)
    return tops


def balustrade(rl):
    """borda da plataforma: dois arcos (norte e sul) do portao da escada ate o canto do soco (bastiao). Devolve os
    topos dos 2 pilares-portao."""
    hs = POD_HW + SOC_OFF
    # angulo (em volta do centro da plataforma) onde o arco da balaustrada encontra a lateral do soco
    a_end = 180.0 - math.degrees(math.asin(min(1.0, (hs + 0.2) / RAIL_R)))
    gates = []
    for s in (1, -1):
        pts = [(CX + RAIL_R * math.cos(math.radians(s * a)), CY + RAIL_R * math.sin(math.radians(s * a)))
               for a in [GATE_A + (a_end - GATE_A) * i / 20 for i in range(21)]]
        gates += gothic_rail(rl, pts, Z, post_every=9.0, post_big=(0,))
    return gates


# ------------------------------------------------------------------ ponte curta (arco ogival) e escada da planta
# OVERHAUL 10 (10.03): o arco antigo nascia DENTRO do penhasco e da lingua de rocha (pes em caixa atravessando as
# colunas de basalto) e tinha aduelas em caixa reta (escadinha no intradorso). Agora o arco vence o vao LIVRE entre as
# 2 faces de rocha (penhasco da ilha em x -103,0; lingua da plataforma em x -111,6, cuja base fica em z 30,0), nasce
# de IMPOSTAS de cantaria encostadas nessas faces (acima da base da lingua) e tem aduelas RADIAIS (normal do intradorso)
# com fecho; timpano liso recuado, friso e cornija; encontro leste assentado no patamar do penhasco; lajes no tabuleiro.
# ONDA 2 (o2b, planta v4): as 2 faces sao MEDIDAS na rocha do terreno v4 (sg_terrain, onda 1f) quando ele ja esta na
# cena: a do penhasco varia com y (-169,9 a -170,7 na v4) e vale a mais a OESTE na largura do timpano (o arco nunca
# fica descolado da rocha); sem terreno de detalhe, a relacao da v3 (3,0 alem do inicio da ponte / 0,4 alem do pe da
# escada da planta).
BR_FACE_E, BR_FACE_W = L.SUMMON_BRIDGE[0][0] - 3.0, L.SUMMON_BRIDGE[1][0] + 0.4


def measure_bridge_faces():
    """(face leste = penhasco da ilha, face oeste = lingua de rocha da plataforma) na linha da ponte, por raios nas
    malhas SG_Ter_*; None onde nao achou"""
    from mathutils.bvhtree import BVHTree
    a0, a1, w = L.SUMMON_BRIDGE
    y = a0[1]
    xm = (a0[0] + a1[0]) / 2.0
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("SG_Ter_"):
            continue
        M = o.matrix_world
        base = len(verts)
        verts.extend(M @ v.co for v in o.data.vertices)
        polys.extend([base + i for i in p.vertices] for p in o.data.polygons)
    if not polys:
        return None, None
    T = BVHTree.FromPolygons(verts, polys)
    east, west = [], []
    for dy in (-BR_TYMP - BR_RING, -BR_TYMP / 2, 0.0, BR_TYMP / 2, BR_TYMP + BR_RING):
        for z in (BR_SPRING - 0.4, BR_SPRING + 1.0, P1 - 3.0):
            h = T.ray_cast(Vector((xm, y + dy, z)), Vector((1.0, 0.0, 0.0)), 12.0)
            if h[0] is not None:
                east.append(h[0].x)
            h = T.ray_cast(Vector((xm, y + dy, z)), Vector((-1.0, 0.0, 0.0)), 12.0)
            if h[0] is not None:
                west.append(h[0].x)
    fe = min(east) if east else None
    fw = max(west) if west else None
    return fe, fw
BR_SPRING = 30.8                 # nascenca (impostas de 30,2 a 30,8: acima da base da lingua, sem face coplanar)
BR_CROWN = P1 - 2.2              # fecho do intradorso (34,0)
BR_TYMP = 6.4                    # meia largura do timpano
BR_RING = 0.5                    # saliencia das aduelas sobre o timpano


def _yz_faces(mb, q, y0, y1, m, bevel=0.0):
    """poligono CONVEXO [(x, z)] extrudado em y de y0 a y1"""
    import bmesh
    bm = mb.bm
    va = [bm.verts.new((x, y0, z)) for x, z in q]
    vb = [bm.verts.new((x, y1, z)) for x, z in q]
    fs = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
    n = len(q)
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(va + vb, m, None, bevel, 1)


def bridge(br, rl):
    import sg_entry as EN
    global BR_FACE_E, BR_FACE_W
    fe, fw = measure_bridge_faces()
    a0_, a1_ = L.SUMMON_BRIDGE[0][0], L.SUMMON_BRIDGE[1][0]
    if fe is not None and a1_ + 4.0 < fe < a0_ - 0.5:
        BR_FACE_E = fe
    if fw is not None and a1_ - 1.0 < fw < BR_FACE_E - 4.0:
        BR_FACE_W = fw
    print("SUM ponte: faces da rocha medidas leste %s oeste %s -> arco de %.2f a %.2f" % (
        None if fe is None else round(fe, 2), None if fw is None else round(fw, 2), BR_FACE_W, BR_FACE_E))
    a0, a1, w = L.SUMMON_BRIDGE
    x0, x1 = a0[0], a1[0] + 0.4                     # -100 .. -111,6 (a lingua de rocha do terreno comeca em -111,6)
    y = a0[1]
    hw = w / 2 + 1.2                                # tabuleiro ate a face de fora dos parapeitos
    ztop = P1 - 0.75                                # base da cornija
    # encontro leste: macico sobre o patamar do penhasco (topo 34,2), do tabuleiro ate a face da rocha
    br.box2((BR_FACE_E - 0.05, y - BR_TYMP, 33.7), (x0, y + BR_TYMP, ztop), "Stone_SG_Block", 0.0)
    # intradorso ogival abatido entre as 2 faces de rocha
    arc = EN.pointed_arc(BR_FACE_W, BR_FACE_E, BR_SPRING, BR_CROWN - BR_SPRING, 4)
    # timpano (faixas convexas do intradorso ate a base da cornija)
    for (xa, za), (xb, zb) in zip(arc, arc[1:]):
        _yz_faces(br, [(xa, za), (xb, zb), (xb, ztop), (xa, ztop)], y - BR_TYMP, y + BR_TYMP, "Stone_SG_Block")
    # impostas de cantaria nas 2 faces de rocha (0,4 dentro da rocha, 0,3 para o vao) - o arco nasce em cima delas
    for xf, sg in ((BR_FACE_E, 1.0), (BR_FACE_W, -1.0)):
        q = [(xf + sg * 0.4, BR_SPRING - 0.6), (xf - sg * 0.3, BR_SPRING - 0.6), (xf - sg * 0.3, BR_SPRING - 0.18),
             (xf - sg * 0.18, BR_SPRING), (xf + sg * 0.4, BR_SPRING)]
        _yz_faces(br, q, y - BR_TYMP - BR_RING - 0.1, y + BR_TYMP + BR_RING + 0.1, CAPL)
    # aduelas RADIAIS nas 2 faces: juntas na normal do intradorso (media das 2 faixas vizinhas), fecho mais alto
    band = 0.78
    nrm = []
    for i in range(len(arc)):
        segs = []
        for j in (i - 1, i):
            if 0 <= j < len(arc) - 1:
                (xa, za), (xb, zb) = arc[j], arc[j + 1]
                L_ = math.hypot(xb - xa, zb - za)
                segs.append(((za - zb) / L_, (xb - xa) / L_))
        nx, nz = sum(q[0] for q in segs), sum(q[1] for q in segs)
        ln = math.hypot(nx, nz)
        nrm.append((nx / ln, nz / ln))
    # a normal tem de apontar para FORA do vao (para cima no fecho)
    ic = len(arc) // 2                                               # vertice do fecho
    if nrm[ic][1] < 0:
        nrm = [(-a, -b) for a, b in nrm]
    for sy in (-1, 1):
        ya, yb = sorted((y + sy * (BR_TYMP - 0.1), y + sy * (BR_TYMP + BR_RING)))
        for i in range(len(arc) - 1):
            (xa, za), (xb, zb) = arc[i], arc[i + 1]
            tx, tz = xb - xa, zb - za
            tl = math.hypot(tx, tz)
            ex, ez = tx / tl * 0.035, tz / tl * 0.035
            q = [(xa + ex, za + ez), (xb - ex, zb - ez), (xb - ex + nrm[i + 1][0] * band, zb - ez + nrm[i + 1][1] * band),
                 (xa + ex + nrm[i][0] * band, za + ez + nrm[i][1] * band)]
            _yz_faces(br, q, ya, yb, CAPL)
        # fecho: cunha no vertice (mais larga em cima, chega a cornija)
        xc, zc = arc[ic]
        _yz_faces(br, [(xc - 0.3, zc - 0.1), (xc + 0.3, zc - 0.1), (xc + 0.46, ztop - 0.02), (xc - 0.46, ztop - 0.02)],
                  ya - 0.05, yb + 0.08, CAPL)
    # cornija de cantaria (arremata o timpano e as aduelas); tabuleiro de lajes (topo = P1)
    br.box2((x1 - 0.05, y - hw - 0.15, ztop), (x0, y + hw + 0.15, P1 - 0.35), CAPL, 0.04)
    br.box2((x1, y - hw + 0.2, P1 - 0.4), (x0, y + hw - 0.2, P1 - 0.1), "Stone_SG_Floor", 0.0)   # leito (juntas)
    rows = 2.4
    xr = x0
    k = 0
    cyc = (3.0, 3.6, 2.4, 3.3)
    lim = BR_Y - 0.5
    while xr > x1 + 0.05:
        xe = max(xr - rows, x1)
        yy = -lim - (1.2 if k % 2 else 0.0)
        j = k
        while yy < lim - 0.05:
            wv = cyc[j % len(cyc)]
            j += 1
            ya_, yb_ = max(yy, -lim), min(yy + wv, lim)
            if yb_ - ya_ > 0.6:
                br.box2((xe + 0.05, y + ya_ + 0.05, P1 - 0.35), (xr - 0.05, y + yb_ - 0.05, P1), "Stone_Paving_SG",
                        0.06)
            yy += wv
        xr = xe
        k += 1
    # parapeitos (a guarda invisivel do sg_col fica na mesma linha)
    for sy in (-1, 1):
        gothic_rail(rl, [(x0 + 0.2, y + sy * BR_Y), (a1[0] - 0.3, y + sy * BR_Y)], P1, post_every=12.0)


def plan_stair(st):
    """escada 'Summon' da planta (sg_lib.plan_stair: casa com a colisao do sg_col) + banzos lisos inclinados"""
    SL.plan_stair(st, "Summon", m="Stone_Paving_SG", side_m="Stone_SG_Block", stringers=False)
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    rise = (L.STAIR_TOP_Z["Summon"] - foot[2]) / n
    Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg))
    k = rise / tread
    x_top = tread * n - tread / 2
    zt = rise * n
    x_end = (foot[0] - (CX + RAIL_R * math.cos(math.radians(GATE_A)))) - 0.8     # ate o pilar do portao
    for s in (-1, 1):
        y0, y1 = s * (BR_Y - 0.5), s * (BR_Y + 0.5)
        prof = [(0.4, -1.8), (x_end, -1.8 + zt), (x_end, zt + 1.35), (x_top, zt + 1.35), (0.4, 1.35 + 0.4 * k)]
        side_prism(st, Fs, prof, min(y0, y1), max(y0, y1), "Stone_SG_Block")
        a = Fs.p(0.4, s * BR_Y, 1.35 + 0.4 * k + 0.18)
        b = Fs.p(x_top, s * BR_Y, zt + 1.35 + 0.18)
        st.beam(a, b, 1.3, 0.36, CAPL, 0.04)
        st.beam(b, Fs.p(x_end, s * BR_Y, zt + 1.35 + 0.18), 1.3, 0.36, CAPL, 0.04)


# ------------------------------------------------------------------ ritmo da ordem (refinamento v2, polimento leve)
def order_dressing(gates):
    """lanternas da ordem SO NOS NOS (overhaul 10, 12.04): as 4 lanternas de pedestal espalhadas pela balaustrada
    sairam; os 2 pilares-portao do topo da escada (a entrada da plataforma) levam a lanterna do kit sobre um prato de
    obsidiana. So Neon: nenhuma luz nova (teto 3 ja usado); sem colisao (pecas na borda, fora das rotas).
    Acabamento 2026-09-29: os 2 estandartes em mastro nos pilares-portao da escada SAIRAM - vistos da chegada ficavam
    NA FRENTE do portal (tapavam o nicho) e repetiam os 2 estandartes dos mastros da propria torre."""
    mb = MB("SG_Sum_OrderDressing", COL, random.Random(7701), detail="near")
    s = 0.95
    for top, p, rz in gates:
        mb.box((1.3, 1.3, 0.14), (p.x, p.y, top + 0.07), (0, 0, rz), "Stone_SG_Obsidian", 0.04)
        EM.lantern_head(mb, mb, (p.x, p.y, top + 0.14 + EM.LH_BASE * s), 0.0, s)
    mb.finish()


# ------------------------------------------------------------------ build
def join_into(target, others):
    """ONDA 2 (o2b): base, remates, incrustacao do piso, balaustrada e ponte sao a MESMA paleta de pedra (Floor,
    Castle(_B), Block(_B), Paving(_B), TrimLow): num objeto so viram 8 MeshParts em vez de 18 (o desenho nao muda)"""
    objs = [target] + [o for o in others if o is not None and o.type == "MESH"]
    if target is None or len(objs) < 2:
        return target
    with bpy.context.temp_override(active_object=target, object=target, selected_objects=objs,
                                   selected_editable_objects=objs):
        bpy.ops.object.join()
    return target


def build():
    T, c, lamp_c = build_tower()
    stone = MB("SG_Sum_Base", COL, random.Random(7301), detail="near")
    trim = MB("SG_Sum_BaseTrim", COL, random.Random(7302), detail="near")
    base(stone, trim, T)
    tower_stair(stone)
    base_collision()
    inl = MB("SG_Sum_FloorInlay", COL, random.Random(7401), detail="near")
    floor_inlay(inl)
    rl = MB("SG_Sum_Balustrade", COL, random.Random(7501), detail="near")
    gates = balustrade(rl)
    br = MB("SG_Sum_Bridge", COL, random.Random(7601), detail="near")
    bridge(br, rl)
    plan_stair(br)
    obs = [mb.finish() for mb in (stone, trim, inl, rl, br)]
    join_into(obs[0], obs[1:])
    order_dressing(gates)
    import sg_water
    sg_water.zone_relief(("SG_Sum_", "VFX_SGSUM"))
    # luzes (3): nucleo violeta (esfera-estrela) + 2 quentes baixas (lanternas da ordem dos pedestais)
    light("L_SGSum_Core", "POINT", c, 6000.0, VIOLET, 3.0)       # acabamento: 9000 -> 6000 (brilho moderado)
    for n, p in zip(("L_SGSum_Lantern_S", "L_SGSum_Lantern_N"), lamp_c):
        light(n, "POINT", p, 380.0, WARM, 0.4)
