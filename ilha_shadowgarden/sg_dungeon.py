# sg_dungeon - ZONA DUNGEON da Ilha 3 (Shadow Garden), PLANTA v4 (onda 1, agente 1d, 2026-09-30). build() substitui
# sg_blockout.dungeon (colisoes e luzes incluidas). Prefixo SG_Dun_, colecao 17_DUNGEON. A dungeon e a "corrida de
# mineracao" periodica do jogo (XX:00 / XX:30): o jogador desce pelo trono -> escada caracol -> Salao Sombrio (sg_cave)
# e o portal DUNGEON_Hall o leva a R1; minera nas arenas R2/R3 (DUN_ORE_*) e passa de sala pelo portal DUN_NEXT_* (parede
# de energia 27 x 21 x 1 que o JOGO cria no CFrame do marcador). O sistema e do jogo: aqui so o LUGAR. NAO modela minerio.
# v4 (renders/plano_mestre/PLANO.md):
#   - a PORTARIA-caverna ao lado do castelo SAIU (boca, tunel, rocha em estratos, aproximacao, vortice da superficie):
#     a entrada agora e o portal do Salao Sombrio (sg_cave, agente 1c).
#   - SALAS 3x sob o Salao Sombrio, fila em +Y no eixo x = 0: R1 84 x 84 (chegada), R2 e R3 104 x 104 (arenas), piso
#     -72, teto -28 (pe-direito 44), paredes de 2. O MESMO kit aprovado do overhaul 09 (pilastras com colunelo, arcadas
#     cegas de 2 ordens, cornija, nervuras em pera, lajes em 2 tamanhos, tochas de ferro, runas do alfabeto unico,
#     lustres com o kit de vela) no ritmo da escala nova: tramos de 14 / 14,9 com os MESMOS arcos de antes (so mais
#     tramos, nada esticado); a altura extra vai para a ABOBADA (arranque 18, fecho 43,6) com nervuras e liernes.
#     Variacao dirigida: R1 lancetas altas + portal de chegada aceso; R2 escoras de mina e grelhas alternadas; R3
#     colunelos duplos + retabulo no eixo do muro leste + medalhao no centro.
#   - VAOS de ligacao 28 x 22 (DUN_LINK_*): ombreiras em cunhais, VERGA DE ADUELAS (arco adintelado) com runas no
#     fecho, timpano ogival de aduelas com chave; soleira no plano do vao.
#   - PORTAL DA PROXIMA SALA: DUN_NEXT_R2 no plano medio do vao R2R3, DUN_NEXT_R3 num NICHO do muro norte da R3. A
#     parede de energia (27 x 21 x 1, base no piso) cabe INTEIRA no vao livre 28 x 22 (0,5 nos lados, 1 em cima) e toda
#     a moldura fica FORA do vao: era o bug "a barreira que teleporta esta para fora". Soleira com canal runico sob a
#     parede e medalhao runico no timpano. A espiral SG_Dun_R3_ExitSpiral* fica no fundo do nicho (visual do
#     DUN_NEXT_R3; o DungeonService acende).
#   - SAIDAS por PROMPT (DUN_EXIT_R1 no muro sul da R1, DUN_EXIT_R3 no muro oeste da R3): arco de saida menor com o
#     vortice APAGADO (disco navy + espiral de pedra negra, sem brilho). Nenhuma barreira de toque.
#   - SPAWNS (DUNGEON_Spawn, DUN_SPAWN_R2/R3): circulo runico baixo (placa de 0,15) onde o grupo chega.
#   Z-fight (familia F11 do relatorio 19): nada coplanar ou a < 0,12 de face paralela de outro material (runas do piso
#   a +0,13, campos navy a 0,15 da parede, placas +0,15 sobre as lajes, fundo das lajes 0,15 abaixo).
#   Colisao: paredes com os vaos, piso, teto, pilastras, colunas de canto, portais, retabulo e nicho; nada colidivel a
#   menos de 5 dos DUN_ORE_* ate piso+12 (ccol()). Luzes (5): portal de chegada, lustres R1, R2 (2) e R3.
# FINESSE 3 (AUDITORIA3 10.01-10.10, agente D, 2026-10-05):
#   - 10.01 vault(): abobada de PEDRA por tramo: arcos-diafragma de aduelas (1,6 x 1,1, chave) nascendo dos capiteis,
#     formeretes; R1 lajes de cantaria em fiada corrida sobre o leito navy (2 valores), R2 rocha em estratos salientes
#     com cerchas e tercas de madeira, R3 nervuras em pera (cumeeira, liernes, tercelotes) com chaves e coroa clara.
#   - 10.02 ROOM_ID: R1 cripta (nichos fundos com arca tumular / lapide, luz ambar), R2 galeria de mina (celas com
#     grelha ancorada / escoras, rocha, luz fria), R3 santuario (pilastras 2,3 x 2,2 com colunelos duplos, retabulo,
#     coroa de velas, luz violeta suave).
#   - 10.03 grille()/shoring(): grelha em quadro de ferro dentro de montantes de pedra (dobradicas, fechadura);
#     escora com sapatas, forro e grampos. 10.04 niche(): moldura ogival de aduelas com runas em relevo e vortice em
#     camadas. 10.05 rk()/rune_relief(): sem runas-seta (3, 4), medalhao e spawn sem seta. 10.06 retable_bay(): runa
#     em relevo de pedra com Neon so no miolo, frontal moldurado. 10.07 chandelier(): 2 lustres R1/R2 e coroa de 2
#     niveis na R3, pendurados nas chaves. 10.08 tile_floor(): bordadura + fiada corrida, sem faixa central, pedra
#     fosca (Stone_SG_Block sobre junta escura). 10.09 headwall(): tribuna cega de lancetas + rosacea escura.
#     10.10 exit_arch(clad=): edicula com nicho recuado 1,5, capa de 2 ordens, soleira, 2 tochas e coroamento.
import math, random, bisect
import bpy
import bmesh
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box2, light
import fm_lib
import sg_layout as L
import sg_emblem as EM

S = fm_lib.S
# ------------------------------------------------------------------ materiais da zona (os do overhaul 09 continuam
# registrados: so contam os que alguma malha usa)
NEW_MATS = {
    "Stone_SGDunVault": (S(34, 38, 62), 0.8, 0.0, 0, None, 0.06),      # navy escuro: leito da abobada, campos das arcadas
    "Stone_SGDunSlab": (S(52, 56, 84), 0.8, 0.0, 0, None, 0.06),       # FINESSE 3 10.01: pano da abobada (um valor acima)
    "SG_DunVoid_Glow": (S(46, 26, 104), 0.3, 0.0, 1.0, S(56, 30, 124), 0.0),   # fundo do vortice (violeta profundo)
    "Stone_SGDunCaveDeep": (S(40, 24, 74), 0.8, 0.0, 0, None, 0.06),
    "Stone_SGDunRuin": (S(80, 74, 102), 0.85, 0.0, 0, None, 0.08),
    "Crystal_SGDun": (S(62, 42, 108), 0.3, 0.0, 0, None, 0.04),
    "SG_DunCrystal_Glow": (S(140, 100, 228), 0.3, 0.0, 2.2, S(140, 100, 228), 0.0),
    # cera da vela do kit (mesma do salao: sg_hall.NEW_MATS; registrada aqui para a zona nao depender do sg_hall)
    "Wax_SGHallCandle": (S(212, 170, 116), 0.7, 0.0, 0, None, 0.0),
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)
fm_lib.RBX_CAL.setdefault("SG_DunCrystal_Glow", (None, [int(c) for c in fm_lib.to_srgb(NEW_MATS["SG_DunCrystal_Glow"][0])]))
# a abobada das salas nao usa a textura de ruido da pedra (14.02): a leitura vem das nervuras
if ("Stone_SGDunVault", None) not in fm_lib.TEX_RULES:
    fm_lib.TEX_RULES = (("Stone_SGDunVault", None), ("Stone_SGDunSlab", None)) + tuple(fm_lib.TEX_RULES)
CSH, CGL = "Crystal_SGDun", "SG_DunCrystal_Glow"
TRL = "Stone_SG_TrimLow"                         # remate perto do jogador (14.01; = sg_castle.CAPL)
WD = "Wood_SG_Dark"
CS, BL, FL = "Stone_SG_Castle", "Stone_SG_Block", "Stone_SG_Floor"
VA, VO = "Stone_SGDunVault", "SG_DunVoid_Glow"
SV, IR = "Metal_SG_Silver", "Metal_SG_Iron"
GL, VG = "Lantern_Glow", "SG_Violet_Glow"
OB, MBK, BI = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Metal_SG_BlackIron"
VD = "SG_VioletDeep_Glow"
WAX = "Wax_SGHallCandle"

# ------------------------------------------------------------------ planta v4 das salas (sg_layout)
Z, ZCEIL = L.DUN_Z, L.DUN_CEIL                   # -72 / -28 (pe-direito 44)
ROOMS = dict(L.DUN_ROOMS)
ORDER = [n for n, _ in L.DUN_ROOMS]
WT = L.DUN_WALL                                  # 2
LX = L.DUN_LX                                    # eixo dos vaos e portais (x = 0)
LINK_W, LINK_H = L.DUN_LINK_W, L.DUN_LINK_H      # vao LIVRE 28 x 22
LINK_HW = LINK_W / 2.0
NEXT_W, NEXT_H, NEXT_T = L.DUN_NEXT_W, L.DUN_NEXT_H, L.DUN_NEXT_T   # parede de energia do jogo 27 x 21 x 1
R_SPR = 18.0                                     # cornija / arranque da abobada (acima do piso)
R_CROWN = ZCEIL - Z - 0.4                        # fecho 43,6: a casca (0,35) fica abaixo do teto colidivel
BX0 = min(r[0] for r in ROOMS.values()) - WT     # envelope (paredes externas incluidas)
BY0 = min(r[1] for r in ROOMS.values()) - WT
BX1 = max(r[2] for r in ROOMS.values()) + WT
BY1 = max(r[3] for r in ROOMS.values()) + WT + 2.5   # + fundo do nicho da R3
NICHE_BACK = ROOMS["R3"][3] + WT + 1.0           # face do fundo do nicho (305): a parede de energia fica 1,5 a frente
UPZ = Vector((0.0, 0.0, 1.0))


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


def candle(mb, x, y, z, hc=0.6, s=1.0, dish=True):
    """vela do kit (= sg_hall.candle, 12.09): prato de ferro, vela creme nao emissiva, pavio e chama em gota (so ela
    e Neon). z = apoio."""
    if dish:
        EM._lathe(mb, (x, y, z), [(0.12 * s, 0.0), (0.34 * s, 0.07 * s), (0.3 * s, 0.1 * s), (0.0, 0.07 * s)], IR, 6,
                  caps=(True, False))
        z += 0.07 * s
    r = 0.1 * s
    EM._lathe(mb, (x, y, z), [(r, 0.0), (r, hc - 0.04 * s), (0.0, hc - 0.01 * s)], WAX, 5, caps=(False, False))
    zt = z + hc - 0.02 * s
    mb.rod((x, y, zt - 0.02 * s), (x, y, zt + 0.12 * s), 0.018 * s + 0.01, IR, 3, caps=False)
    zf = zt + 0.05 * s
    EM._lathe(mb, (x, y, zf), [(0.0, 0.0), (0.11 * s, 0.14 * s), (0.06 * s, 0.3 * s), (0.0, 0.44 * s)], GL, 6)
    return zf + 0.44 * s


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


# OVERHAUL 09 (09.04/09.13/16.07): UM alfabeto de runas na ilha inteira = sg_court.RUNE_SEGS (runas ANGULARES da
# ordem: haste + ramos diagonais, nada de curva de letra latina). Os obeliscos do patio usam o MESMO desenho.
import sg_court as CT


def rune(mb, o, ea, eb, en, k, sc, m=OB, dep=0.05, w=0.09):
    """runa k do alfabeto da ilha com CENTRO em o, no plano (ea lateral, eb 'cima'), tracos saltando 'dep' ao longo
    de en (entalhe: o traco e o FUNDO escuro/aceso do sulco). sc = 1 -> glifo de 0,76 de altura (o do obelisco)."""
    o, ea, eb, en = Vector(o), Vector(ea).normalized(), Vector(eb).normalized(), Vector(en).normalized()
    ww = w * sc
    for (a0, b0), (a1, b1) in CT.RUNE_SEGS[k % len(CT.RUNE_SEGS)]:
        p0 = o + ea * (a0 * sc) + eb * (b0 * sc)
        p1 = o + ea * (a1 * sc) + eb * (b1 * sc)
        d = p1 - p0
        ax = d.normalized()
        ay = en.cross(ax).normalized()
        obox3(mb, (p0 + p1) / 2 + en * (dep / 2), ax, ay, en, d.length + ww, ww, dep, m)


# ------------------------------------------------------------------ OVERHAUL 09: solidos convexos (casco) e cortes
def _dedupe3(pts, tol=2e-3):
    out = []
    for p in pts:
        p = Vector(p)
        if all((p - q).length > tol for q in out):
            out.append(p)
    return out


def hull(mb, pts, m, face_m=None):
    """solido convexo dos pontos (sem pontos internos). face_m(normal, centro) -> material ou None (troca por face)"""
    bm = mb.bm
    vs = [bm.verts.new(p) for p in _dedupe3(pts)]
    if len(vs) < 4:
        for v in vs:
            bm.verts.remove(v)
        return []
    res = bmesh.ops.convex_hull(bm, input=vs, use_existing_faces=False)
    junk = list({v for v in res["geom_interior"] + res["geom_unused"] if isinstance(v, bmesh.types.BMVert)})
    if junk:
        bmesh.ops.delete(bm, geom=junk, context="VERTS")
    for _ in range(4):                                # pontos colineares -> triangulo de area nula: colapsa a aresta
        fs = {f for v in vs if v.is_valid for f in v.link_faces}
        bad = [f for f in fs if f.calc_area() < 2e-5]
        if not bad:
            break
        es = list({min(f.edges, key=lambda e: e.calc_length()) for f in bad})
        bmesh.ops.collapse(bm, edges=es, uvs=False)
    keep = [v for v in vs if v.is_valid]
    faces = mb._post(keep, m, None, 0, 1)
    if face_m:
        cache = {}
        for f in faces:
            mm = face_m(f.normal, f.calc_center_median())
            if mm:
                if mm not in cache:
                    cache[mm] = mb._mi_for(mm)
                f.material_index = cache[mm]
    return faces


def clip(pts, n, c):
    """recorta o poliedro convexo dos pontos pelo semiespaco n.p <= c: vertices do casco que ficam + intersecoes das
    ARESTAS do casco com o plano (exato, sem pontos internos)"""
    n = Vector(n)
    tmp = bmesh.new()
    tv = [tmp.verts.new(p) for p in _dedupe3(pts)]
    res = bmesh.ops.convex_hull(tmp, input=tv, use_existing_faces=False)
    edges = [e for e in res["geom"] if isinstance(e, bmesh.types.BMEdge)]
    out = [v.co.copy() for v in tmp.verts if v.link_edges and n.dot(v.co) <= c + 1e-6]
    for e in edges:
        a, b = e.verts[0].co, e.verts[1].co
        da, db = n.dot(a) - c, n.dot(b) - c
        if (da < -1e-6 < 1e-6 < db) or (db < -1e-6 < 1e-6 < da):
            out.append(a.lerp(b, da / (da - db)))
    tmp.free()
    return _dedupe3(out, 0.01)


def cbox_pts(c, ax, ay, az, sx, sy, sz, ch):
    """pontos de uma caixa orientada com TODAS as arestas chanfradas 'ch' (24 pontos: cada canto vira 3)"""
    c, ax, ay, az = Vector(c), Vector(ax), Vector(ay), Vector(az)
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    ch = max(0.0, min(ch, hx * 0.45, hy * 0.45, hz * 0.45))
    out = []
    for i in (-1, 1):
        for j in (-1, 1):
            for k in (-1, 1):
                if ch < 1e-4:
                    out.append(c + ax * (i * hx) + ay * (j * hy) + az * (k * hz))
                    continue
                for a, b, d in ((ch, 0, 0), (0, ch, 0), (0, 0, ch)):
                    out.append(c + ax * (i * (hx - a)) + ay * (j * (hy - b)) + az * (k * (hz - d)))
    return out


def cbox(mb, c, ax, ay, az, sx, sy, sz, m, ch=0.1, cuts=(), face_m=None):
    """bloco orientado chanfrado; cuts = [(normal LOCAL (x, y, z), recuo a partir do canto mais externo nessa
    direcao)] = faces de FRATURA / quinas quebradas (ruina dirigida, nada sorteado)"""
    c, ax, ay, az = Vector(c), Vector(ax).normalized(), Vector(ay).normalized(), Vector(az).normalized()
    pts = cbox_pts(c, ax, ay, az, sx, sy, sz, ch)
    for nl, dep in cuts:
        nw = (ax * nl[0] + ay * nl[1] + az * nl[2]).normalized()
        top = max(nw.dot(p) for p in pts)
        pts = clip(pts, nw, top - dep)
    return hull(mb, pts, m, face_m)


def fblock(mb, F, s0, s1, d0, d1, h0, h1, m, ch=0.1, cuts=(), face_m=None):
    """bloco de cantaria no referencial da face F (s ao longo, d para fora, h para cima); cuts em (s, d, h) locais"""
    up = Vector((0.0, 0.0, 1.0))
    c = F.v((s0 + s1) / 2.0, (d0 + d1) / 2.0, (h0 + h1) / 2.0)
    return cbox(mb, c, F.u(), F.n(), up, abs(s1 - s0), abs(d1 - d0), abs(h1 - h0), m, ch, cuts, face_m)


def fledge(mb, F, s0, s1, prof, m):
    """perfil [(d, h)] (poligono CONVEXO no plano d-h da face F) extrudado de s0 a s1: cornija, imposta, cordao"""
    pts = [F.v(s, d, h) for s in (s0, s1) for d, h in prof]
    return hull(mb, pts, m)


def lathe_ax(mb, o, ax, prof, m, n=6, ph=0.0):
    """revolucao em torno de um eixo qualquer (o = origem, ax = direcao); prof = [(raio, distancia)] de baixo para
    cima, raio 0 = polo (tampas nas pontas com raio > 0): fustes, remates, colunas de cristal"""
    o, ax = Vector(o), Vector(ax).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    bm = mb.bm
    rows = []
    for r, d in prof:
        if r < 1e-5:
            rows.append([bm.verts.new(o + ax * d)])
        else:
            rows.append([bm.verts.new(o + ax * d + (e1 * math.cos(ph + 2 * math.pi * i / n) +
                                                    e2 * math.sin(ph + 2 * math.pi * i / n)) * r) for i in range(n)])
    faces = []
    for A, B in zip(rows, rows[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new((A[0], B[i], B[j])))
            elif len(B) == 1:
                faces.append(bm.faces.new((A[i], A[j], B[0])))
            else:
                faces.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    for R in (rows[0], rows[-1]):
        if len(R) > 2:
            faces.append(bm.faces.new(R))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return mb._post([v for r in rows for v in r], m, None, 0, 1)


# ------------------------------------------------------------------ KIT DAS SALAS (OVERHAUL 09.10: Tier A)
# linguagem unica de chanfro 0,1 na cantaria; remates em Stone_SG_TrimLow (14.01); pecas redondas em torno (n 10)
# v4: pilastra um pouco mais cheia para o pe-direito de 44 (arranque 18): mesma secao em proporcao ao fuste de antes
PIL_D, PIL_HW = 1.8, 1.8
COL_R = 0.5                                      # colunelo engastado da pilastra


def fplinth(mb, F, s0, s1, d1, h0, h1, e, m, d0=-0.2):
    """soco em TALUDE: retangulo s0..s1 x d0..d1 em h0 que recua 'e' (frente e lados) ate h1"""
    pts = [F.v(s, d, h0) for s in (s0, s1) for d in (d0, d1)]
    pts += [F.v(s, d, h1) for s in (s0 + e, s1 - e) for d in (d0, d1 - e)]
    return hull(mb, pts, m)


def colonette(mb, F, s, d, h0, h1, r, cap=True, n=8, rot=None):
    """colunelo redondo em pe na face F (centro s, d): base com PLINTO e TORO, fuste, capitel em SINO com astragalo.
    h0 = pe, h1 = topo do capitel (o abaco e o bloco de cima)"""
    o = F.v(s, d, 0.0)
    x, y, z0 = o.x, o.y, o.z
    ph = math.pi / n if rot is None else rot
    EM._lathe(mb, (x, y, z0 + h0), [(r + 0.24, 0.0), (r + 0.22, 0.2), (r + 0.02, 0.5)], TRL, n, ph,
              caps=(False, True))
    # F11: o fuste entra so 0,13 no colar do capitel (o colar fica 0,16 fora do fuste; antes o fuste subia 0,5 dentro
    # do capitel a 0,1 da face)
    EM._lathe(mb, (x, y, z0 + h0 + 0.5), [(r, 0.0), (r, h1 - h0 - (1.42 if cap else 0.5))], CS, n, ph,
              caps=(False, False))
    if cap:
        EM._lathe(mb, (x, y, z0 + h1 - 1.05), [(r + 0.16, 0.0), (r + 0.04, 0.4), (r + 0.3, 0.85)], TRL, n, ph,
                  caps=(False, True))
        a = r + 0.38                                                                    # abaco sobre o sino
        fblock(mb, F, s - a, s + a, d - a, d + a, h1 - 0.2, h1, TRL, 0.0)


def altar_retable(mb, F, s, top, mi):
    """RETABULO da R3 (09.10: 'altar'): mesa de altar de obsidiana com tampo moldurado e frontal com runa acesa baixa,
    2 velas do kit, painel ogival navy em moldura de remate e MISULA no alto (a nervura continua nascendo dela)"""
    fblock(mb, F, s - 2.6, s + 2.6, -0.2, 1.2, -0.1, 0.45, OB, 0.1)                       # degrau
    fblock(mb, F, s - 2.2, s + 2.2, -0.2, 1.05, 0.45, 2.75, OB, 0.1)                      # corpo da mesa
    fledge(mb, F, s - 2.5, s + 2.5, [(-0.2, 2.75), (1.2, 2.75), (1.38, 2.9), (1.38, 3.1), (-0.2, 3.1)], TRL)  # tampo
    fblock(mb, F, s - 1.45, s + 1.45, 1.0, 1.1, 0.95, 2.35, VA, 0.04)                     # frontal rebaixado
    rune(mb, F.v(s, 1.1, 1.65), F.u(), UPZ, F.n(), 4, 1.25, VD, 0.04)
    for sc in (s - 1.7, s + 1.7):
        p = F.v(sc, 0.55, 3.1)
        candle(mi, p.x, p.y, p.z, 0.62, 1.1, dish=True)
    # painel ogival (retabulo) + moldura
    arch_panel(mb, F, s, 2.0, 2.4, 7.6, 3.1, 0.0, 0.18, VA, n=6)
    ogee_band(mb, F, s, 2.0, 2.4, 7.6, 0.42, 0.0, 0.5, TRL)
    for sc in (s - 2.21, s + 2.21):
        fblock(mb, F, sc - 0.21, sc + 0.21, 0.0, 0.5, 3.1, 7.6, TRL, 0.06)
    # misula que carrega a nervura (no lugar do capitel da pilastra)
    hull(mb, [F.v(ss, d, h) for ss in (s - 1.2, s + 1.2) for d, h in
              ((-0.2, top - 2.6), (0.3, top - 2.6), (PIL_D + 0.66, top - 0.4), (PIL_D + 0.66, top), (-0.2, top))], TRL)


def corner_col(mb, F, s, sgn, top, area=None):
    """coluna de canto: soco em talude, massa chanfrada e colunelo de 3/4 no canto interno, capitel moldurado"""
    a, b = sorted((s, s + sgn * 2.4))
    a2, b2 = sorted((s, s + sgn * 2.75))
    fblock(mb, F, a2, b2, -0.2, 2.75, -0.1, 0.7, OB, 0.0)
    fblock(mb, F, a, b, -0.2, 2.4, 0.7, top - 1.3, CS, 0.1)
    colonette(mb, F, s + sgn * 2.4, 2.4, 0.7, top - 1.3, 0.5, n=6)
    ca, cb = sorted((s, s + sgn * 3.0))
    fledge(mb, F, ca, cb, [(-0.2, top - 1.3), (2.4, top - 1.3), (3.0, top - 0.5), (3.0, top), (-0.2, top)], TRL)
    if area:
        fcol(area, F, a2, b2, 0.0, 2.7, -0.5, top)


def ogee_band(mb, F, cs, hw, rise, spring, t, d0, d1, m, n=6):
    """arquivolta (so o arco, do arranque ao fecho) de espessura radial t"""
    band(mb, F, ogive(cs, hw, rise, spring, n), ogive(cs, hw + t, rise + t, spring, n), d0, d1, m)


def skirting(mb, F, s0, s1):
    """soco corrido da parede (obsidiana em talude): a parede nasce do piso, nao de um rodape-caixa"""
    if s1 - s0 > 0.3:
        fledge(mb, F, s0, s1, [(-0.1, -0.1), (0.42, -0.1), (0.42, 0.5), (0.2, 0.78), (-0.1, 0.78)], OB)


def _arch_geo(s0, s1, spring, lancet=False):
    """(meia-largura, flecha, arranque) da arcada cega: a ogiva mantem a proporcao e o ARRANQUE desce se preciso para
    a chave ficar 0,1 abaixo da cornija (nada atravessa a cornija). lancet (R1): ogiva mais aguda"""
    hw = (s1 - s0) / 2.0 - 0.8
    rise = min(hw * (1.7 if lancet else 1.15), 6.0)
    return hw, rise, min(spring, R_SPR - 0.88 - 1.02 - rise)


def cornice(mb, F, s0, s1, h):
    """cornija de remate com perfil (face, gola e aba), no arranque da abobada"""
    if s1 - s0 > 0.3:
        fledge(mb, F, s0, s1, [(-0.1, h - 0.78), (0.22, h - 0.78), (0.62, h - 0.3), (0.72, h - 0.3), (0.72, h),
                               (-0.1, h)], TRL)


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


PORTAL_NV = 18                                   # aduelas do anel do portal das salas


def portal_frame(mb, c, u, v, n, r_in, r_out, floor_z, nv=PORTAL_NV, seg=28):
    """moldura do portal das salas (09.12): ANEL DE ADUELAS de remate (juntas abertas sobre o aro escuro) com runas
    ENTALHADAS do alfabeto da ilha em aduelas alternadas (Neon escuro), coroa de cantaria, CHAVE esculpida saliente
    (degraus + voluta) e PES em consola sobre socos de obsidiana"""
    ring3(mb, c, u, v, n, r_in + 0.18, r_in + 0.9, -0.6, 0.3, OB, seg)                   # aro escuro (juntas; F11)
    ring3(mb, c, u, v, n, r_in + 0.9, r_out, -0.6, 0.35, CS, seg)
    ch = 0.1
    for k in range(nv):
        a0 = math.pi / 2 + 2 * math.pi * (k - 0.5) / nv + 0.018
        a1 = math.pi / 2 + 2 * math.pi * (k + 0.5) / nv - 0.018
        if k == 0:
            continue                                                                    # a chave
        pts = []
        for a in (a0, (a0 + a1) / 2, a1):
            for r in (r_in, r_in + 0.95):
                pts.append(_pl(c, u, v, n, a, r, -0.55))
                pts.append(_pl(c, u, v, n, a, r, 0.72 - ch))
                rr = r + (ch if r < r_in + 0.5 else -ch)
                aa = a + (ch / r if a == a0 else (-ch / r if a == a1 else 0.0))
                pts.append(_pl(c, u, v, n, aa, rr, 0.72))
        hull(mb, pts, TRL)
        if k % 2 == 0 and k not in (nv // 2 - 1, nv // 2, nv // 2 + 1):
            am = (a0 + a1) / 2
            radial = u * math.cos(am) + v * math.sin(am)
            tang = u * -math.sin(am) + v * math.cos(am)
            rune(mb, c + radial * (r_in + 0.47) + n * 0.72, tang, radial, n, rk(k // 2), 0.78, VD, 0.14, 0.12)
    # chave: pedra maior que sai do anel (frente em degraus) + voluta de remate em cima
    top = c + v * (r_in + 0.35)
    for w, hh, d1 in ((1.3, 2.2, 1.0), (0.9, 1.6, 1.3)):
        cbox(mb, top + v * (hh / 2) + n * ((d1 - 0.6) / 2), u, n, v, w, d1 + 0.6, hh, TRL, 0.0)
    lathe_ax(mb, top + v * 1.35 + n * 1.3, n, [(0.0, 0.0), (0.3, 0.02), (0.34, 0.14), (0.0, 0.24)], TRL, 8)
    # pes em consola: soco de obsidiana + consola de remate com o perfil que recebe o anel
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        hz = p.z + 0.4 - floor_z
        base = Vector((p.x, p.y, floor_z))
        cbox(mb, base + UPZ * 0.35, u, n, UPZ, 2.5, 2.3, 0.8, OB, 0.0)
        hull(mb, [base + u * (s_ * 1.0) + n * d + UPZ * z for s_ in (-1, 1) for d, z in
                  ((-0.9, 0.7), (0.9, 0.7), (1.05, hz * 0.55), (0.75, hz), (-0.9, hz))], TRL)


# ------------------------------------------------------------------ OVERHAUL 09.08: CRISTAIS com facetas de verdade
def _frame3(d):
    d = Vector(d).normalized()
    ref = Vector((0.0, 0.0, 1.0)) if abs(d.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = d.cross(ref).normalized()
    return d, e1, d.cross(e1).normalized()


def crystal_hex(mb, base, dirv, h, r, ph=0.0, body=CSH, tip=CGL):
    """COLUNA de cristal: prisma hexagonal levemente conico (casca escura, sem brilho) que nasce 0,6 dentro do calo
    e TERMINACAO de 6 facetas com o apice deslocado (so a ponta e Neon: 09.08)"""
    d, e1, e2 = _frame3(dirv)
    b = Vector(base) - d * 0.6
    hb = h * 0.7 + 0.6

    def ring(o, rr):
        return [o + (e1 * math.cos(ph + k * math.pi / 3) + e2 * math.sin(ph + k * math.pi / 3)) * rr for k in range(6)]
    r1 = ring(b + d * hb, r * 0.86)
    hull(mb, ring(b, r) + r1, body)
    hull(mb, r1 + [b + d * (hb + h * 0.3) + (e1 * math.cos(ph) + e2 * math.sin(ph)) * (r * 0.22)], tip)


def crystal_boss(mb, base, dirv, R, m):
    """CALO de rocha de onde o aglomerado brota (casco dirigido, afunda na parede): nada solto"""
    d, e1, e2 = _frame3(dirv)
    b = Vector(base)
    pts = []
    for k in range(7):
        a = 2 * math.pi * k / 7
        rr = R * (1.0 + 0.22 * math.sin(k * 2.1 + 0.4))
        pts.append(b - d * 0.25 + (e1 * math.cos(a) + e2 * math.sin(a)) * rr)
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.5
        rr = R * 0.55 * (1.0 + 0.2 * math.cos(k * 1.7))
        pts.append(b + d * (0.32 * R) + (e1 * math.cos(a) + e2 * math.sin(a)) * rr)
    pts.append(b - d * (0.9 * R))
    hull(mb, pts, m)


# aglomerado: (escala, abertura, azimute) das colunas menores em volta da maior (leque dirigido, assimetrico)
SPREAD = ((0.62, 0.5, 0.6), (0.46, 0.62, 2.6), (0.34, 0.55, 4.3), (0.28, 0.7, 5.4))


def cluster(mb, base, dirv, h, r, k, boss_m):
    d, e1, e2 = _frame3(dirv)
    crystal_boss(mb, base, d, r * 2.2, boss_m)
    crystal_hex(mb, base, d, h, r, 0.3)
    for i, (sc, a, az) in enumerate(SPREAD[:max(0, k - 1)]):
        off = e1 * math.cos(az) + e2 * math.sin(az)
        dd = (d + off * a).normalized()
        crystal_hex(mb, Vector(base) + off * (r * 1.2), dd, h * sc, r * sc * 1.1, 0.9 * i)


def crystal_pendant(mb, c, m=CGL):
    """o cristal da boca (VFX: gira no eixo z do pivot): biterminado hexagonal, facetas de verdade, ponta de cima
    entra no capuz de prata"""
    EM._lathe(mb, (c.x, c.y, c.z), [(0.0, -1.75), (0.6, -0.9), (0.7, 0.55), (0.6, 1.15), (0.0, 2.08)], m, 6)


def portal_ring_dark(mb, c, u, v, n, r_in, r_out, floor_z):
    """anel ESCURO do vortice: aro de obsidiana com runas acesas, coroa de ferro negro com laminas de obsidiana em raio
    (ameaca) e fio de energia no labio interno; pes de obsidiana"""
    ring3(mb, c, u, v, n, r_in, r_in + 1.05, -0.6, 0.7, OB)
    ring3(mb, c, u, v, n, r_in + 1.05, r_out, -0.6, 0.42, BI)
    ring3(mb, c, u, v, n, r_in - 0.08, r_in + 0.1, -0.35, 0.78, VD)
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        rune(mb, c + radial * (r_in + 0.53) + n * 0.7, tang, radial, n, k, 0.8, m=VD, dep=0.06, w=0.12)
    for k in range(12):
        a = 2 * math.pi * k / 12 + math.pi / 2
        if abs(math.sin(a) + 1.0) < 0.3:
            continue                                                          # nada de lamina para baixo
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        ln = 2.4 if k == 0 else (1.6 if k % 2 == 0 else 1.1)
        blade(mb, c + radial * (r_out - 0.3) + n * 0.05, radial, tang, n, ln, 0.9, 0.55, OB)
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        h = p.z + 0.4 - floor_z
        obox(mb, Vector((p.x, p.y, floor_z + h / 2)), u, v, n, 2.4, h, 2.2, OB, 0.08)


def altar_medallion(mb, cx, cy):
    """MEDALHAO do centro da R3 (v4: placa baixa +0,15 sobre as lajes, F11): anel de remate -> fio aceso -> campo navy
    com 8 runas (Neon escuro, +0,13) -> fio aceso -> disco de pedra"""
    n = 24
    ang = [2 * math.pi * k / n for k in range(n)]
    k_ = MED_HS / 9.0

    def circ(r):
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in ang]
    rings = [(circ(7.8 * k_), circ(7.0 * k_), TRL), (circ(7.0 * k_), circ(6.8 * k_), VD),
             (circ(6.8 * k_), circ(3.2 * k_), VA), (circ(3.2 * k_), circ(2.7 * k_), VD)]
    zt, zb = Z + 0.15, Z - 0.1
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
    mb.prism(circ(2.7 * k_), zb, zt, FL)
    up = Vector((0.0, 0.0, 1.0))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        rune(mb, Vector((cx, cy, zt - 0.05)) + rad * (5.1 * k_), Vector((-rad.y, rad.x, 0.0)), rad, up, rk(k), 2.6 * k_,
             VD, dep=0.18)   # F11: runa +0,13 sobre o campo


def _floor_arc(mb, c, r, a0, a1, w, m, k=12):
    """filete runico no piso (arco continuo, topo em Z + 0,13: F11, nada a menos de 0,12 da laje)"""
    pts = [Vector((c.x + r * math.cos(a0 + (a1 - a0) * i / k), c.y + r * math.sin(a0 + (a1 - a0) * i / k),
                   Z - 0.05)) for i in range(k + 1)]
    mb.sweep(pts, [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, 0.18), (-w / 2, 0.18)], m, True, None, up=(0.0, 0.0, 1.0))


def floor_runes(mb, c, n, sc=1.0):
    """INSCRICAO no piso diante de um portal das salas (09.13): 7 runas do alfabeto da ilha ENTALHADAS (Neon escuro,
    rentes) entre 2 filetes continuos de obsidiana - faixa de inscricao, nao letreiro aceso (sc: portal maior)"""
    up = Vector((0.0, 0.0, 1.0))
    base = math.atan2(n.y, n.x)
    for i in range(7):
        a = base + math.radians(-54.0 + 18.0 * i)
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        rune(mb, Vector((c.x, c.y, Z - 0.05)) + rad * (6.4 * sc), Vector((-rad.y, rad.x, 0.0)), -rad, up, i + 2,
             1.6 * sc, VD, dep=0.18)
    for r in (5.3 * sc, 7.5 * sc):
        _floor_arc(mb, c, r, base - math.radians(64.0), base + math.radians(64.0), 0.16, VD)


def room_faces(nm):
    x0, y0, x1, y1 = ROOMS[nm]
    return {"S": Face(True, y0, 1, Z), "N": Face(True, y1, -1, Z), "W": Face(False, x0, 1, Z),
            "E": Face(False, x1, -1, Z)}


PITCH_N = {"R1": 6, "R2": 7, "R3": 7}            # tramos dos muros longos: 14 (R1) / 14,86 (arenas)


def rib_ys(nm):
    x0, y0, x1, y1 = ROOMS[nm]
    p = (y1 - y0) / PITCH_N[nm]
    return [y0 + p * k for k in range(1, PITCH_N[nm])]


JAMB_W = 1.8                                     # cunhais da ombreira: de |x| 14 a 15,8 (FORA do vao livre)
FRAME_HW = LINK_HW + JAMB_W                      # 15,8
CORNER = 2.75                                    # coluna de canto (avanco nos 2 muros)
ARCH_SPRING = {"R1": 13.5, "R2": 10.0, "R3": 10.5}   # R1 lancetas altas; R2 mina; R3 altar
TORCH_H = 11.4
PORTAL_R = (7.4, 9.2)                            # portal de chegada da R1 (aceso)
EXIT_R = (2.9, 4.1)                              # arco de saida (vortice apagado): coroa de cantaria de 0,3
EXIT_S = {"R1": -30.0, "R3": 205.8}              # centro do arco de saida no muro (marcador: x -30 / y 204); na R3 o
#                                                  arco ocupa o 1o tramo inteiro (200,85..210,76) sem tocar coluna/pilastra
# muros de ponta (s = x): tipo do centro e pilastras
END = {("R1", "S"): "arrival", ("R1", "N"): "link", ("R2", "S"): "link", ("R2", "N"): "next",
       ("R3", "S"): "next", ("R3", "N"): "niche"}


# ------------------------------------------------------------------ vaos, portais da proxima sala e nicho
def vouss_piece(mb, F, quad, d0, d1, m, g=0.04):
    """aduela: quadrilatero (s, h) no plano da parede encolhido 'g' nas juntas, de d0 a d1"""
    cs = sum(q[0] for q in quad) / 4.0
    ch = sum(q[1] for q in quad) / 4.0
    pts = []
    for s, h in quad:
        ds, dh = cs - s, ch - h
        ln = math.hypot(ds, dh) or 1.0
        s2, h2 = s + ds / ln * g, h + dh / ln * g
        for d in (d0, d1):
            pts.append(F.v(s2, d, h2))
    hull(mb, pts, m)


def flat_arch(mb, F, cs, ext, zb, zt, nv=9, dep=0.75, key_rune=None):
    """VERGA DE ADUELAS (arco adintelado): cunhas com juntas radiais que convergem abaixo do vao; as pontas sao
    verticais (nao invadem as pilastras); o FECHO sobe e avanca, com runa entalhada acesa (Neon escuro)"""
    ah = zb - 22.0                                   # ponto de convergencia das juntas

    def top_s(s):
        return max(cs - ext, min(cs + ext, cs + (s - cs) * (zt - ah) / (zb - ah)))
    for i in range(nv):
        s0 = cs - ext + 2.0 * ext * i / nv
        s1 = cs - ext + 2.0 * ext * (i + 1) / nv
        key = i == nv // 2
        zz = zt + (0.9 if key else 0.0)
        if key:
            quad = [(s0, zb), (s1, zb), (top_s(s1) + 0.25, zz), (top_s(s0) - 0.25, zz)]
        else:
            quad = [(s0, zb), (s1, zb), (top_s(s1), zt), (top_s(s0), zt)]
        vouss_piece(mb, F, quad, -0.1, dep + (0.3 if key else 0.0), TRL)
    if key_rune is not None:
        rune(mb, F.v(cs, dep + 0.28, (zb + zt + 0.9) / 2.0), F.u(), UPZ, F.n(), key_rune, 1.9, VD, 0.16, 0.14)


def ogive_vouss(mb, F, cs, hw, rise, spring, t, d0, d1, m, n=12, per=2):
    """arco ogival de ADUELAS (pecas de 'per' segmentos) - a chave e posta a parte"""
    inner = ogive(cs, hw, rise, spring, n)
    outer = ogive(cs, hw + t, rise + t, spring, n)
    k = 0
    while k < len(inner) - 1:
        j = min(len(inner) - 1, k + per)
        quad = [inner[k], outer[k], outer[j], inner[j]]
        vouss_piece(mb, F, quad, d0, d1, m)
        k = j


def link_frame(mk, F, kind):
    """moldura de um lado do vao 28 x 22 (kind 'link' | 'next' | 'niche'): cunhais das ombreiras, verga de aduelas com
    runas no fecho, timpano ogival navy com arco de aduelas e chave; 'next'/'niche' ganham o MEDALHAO runico no timpano.
    Tudo em |s| >= 14 ou h >= 22: o vao livre (e a parede de energia 27 x 21 do jogo) fica limpo."""
    cs, hw = LX, LINK_HW
    rows = 6
    hh = LINK_H / rows
    for sg in (-1, 1):
        for k in range(rows):
            lg = k % 2 == 0
            a, b = sorted((cs + sg * hw, cs + sg * (hw + (JAMB_W if lg else 1.25))))
            h0, h1 = k * hh + (0.0 if k == 0 else 0.05), (k + 1) * hh - 0.05
            fblock(mk, F, a, b, 0.0, 0.62 if lg else 0.46, h0 if k else -0.1, h1, OB if k == 0 else TRL,
                   0.1 if k == 0 else 0.0)
    zb, zt = LINK_H, LINK_H + 3.0
    flat_arch(mk, F, cs, FRAME_HW, zb, zt, key_rune=5 if kind != "link" else 1)
    spr, rise, t = zt, 9.0, 1.1
    arch_panel(mk, F, cs, FRAME_HW - 0.15, rise - 0.1, spr, spr - 0.3, 0.0, 0.15, VA, n=10)
    ogive_vouss(mk, F, cs, FRAME_HW, rise, spr, t, -0.1, 0.62, TRL, n=12, per=2)
    for sg in (-1, 1):                                                   # impostas sobre os cunhais
        a, b = sorted((cs + sg * (FRAME_HW - 0.2), cs + sg * (FRAME_HW + t + 0.25)))
        fledge(mk, F, a, b, [(-0.1, spr - 0.02), (0.72, spr - 0.02), (0.72, spr + 0.3), (-0.1, spr + 0.3)], TRL)
    kz = spr + rise + t
    fblock(mk, F, cs - 0.75, cs + 0.75, -0.1, 0.95, kz - 1.9, kz + 0.9, TRL, 0.1)          # chave do timpano
    if kind != "link":
        c = F.v(cs, 0.15, spr + 4.3)
        u, v, n = F.u(), UPZ, F.n()
        ring3(mk, c, u, v, n, 2.3, 3.1, 0.0, 0.42, OB, 16)
        disc3(mk, c, u, v, n, 2.35, 0.0, 0.2, OB, 16)
        rune_relief(mk, c + n * 0.2, u, v, n, 8, 2.9, TRL, VD, 0.18, 0.22)      # 10.05: runa em relevo, sem seta
        for i in range(8):
            a = 2 * math.pi * i / 8 + math.pi / 8
            rad = u * math.cos(a) + v * math.sin(a)
            obox3(mk, c + rad * 2.7 + n * 0.49, rad, u * -math.sin(a) + v * math.cos(a), n, 0.42, 0.14, 0.16, TRL)


def link_sill(mb, ya, yb, next_=False, ym=None, back=1.2):
    """soleira no plano do vao (y de ya a yb = espessura da parede): 3 pedras de remate +0,15 sobre o piso; no portal da
    proxima sala a soleira e de obsidiana com um CANAL runico aceso sob a parede de energia (1,1 de largura)"""
    zt = Z + 0.15
    w3 = LINK_W / 3.0
    ym = (ya + yb) / 2.0 if ym is None else ym
    for k in range(3):
        xa = LX - LINK_HW + k * w3 + 0.04
        xb = xa + w3 - 0.08
        if next_:
            mb.box2((xa, ya - 1.2, Z - 0.4), (xb, ym - 0.55, zt), OB, 0.06)
            mb.box2((xa, ym + 0.55, Z - 0.4), (xb, yb + back, zt), OB, 0.06)
        else:
            mb.box2((xa, ya - 1.2, Z - 0.4), (xb, yb + 1.2, zt), TRL, 0.06)
    if next_:
        mb.box2((LX - LINK_HW, ym - 0.55, Z - 0.4), (LX + LINK_HW, ym + 0.55, Z - 0.05), VD, 0.0)


def next_portals(mk):
    """os 2 portais da proxima sala: moldura dos 2 lados do vao R2R3 (DUN_NEXT_R2) e do nicho da R3 (DUN_NEXT_R3)"""
    ms = MB("SG_Dun_R3_ExitSpiral", "17_DUNGEON", random.Random(763), detail="near")
    c, n = niche(mk, ms, room_faces("R3")["N"])
    ob = ms.finish()
    ob["show"] = "TRANSITION,FINISHING,FINISHED"
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, -1.0, 0.0]
    ob["note"] = ("espiral do NICHO do muro norte da R3 = visual do DUN_NEXT_R3 (portal da proxima sala): fica 1,5 atras "
                  "da parede de energia; o DungeonService liga (Transparency 0) quando a sala limpa / em transicao")


# ------------------------------------------------------------------ portal de chegada (R1), saidas e spawns
def arrival_portal(mb, F):
    """portal de CHEGADA no muro sul da R1 (aceso: o grupo sai dele): anel de aduelas (09.12) em nicho de 2 ORDENS"""
    r_in, r_out = PORTAL_R
    n = F.n()
    c = F.v(LX, 1.0, r_out - 0.3)
    u = n.cross(UPZ).normalized()
    portal_frame(mb, c, u, UPZ, n, r_in, r_out, Z)
    disc3(mb, c, u, UPZ, n, r_in + 0.15, -0.5, -0.3, VO, 32)
    spiral(mb, c, u, UPZ, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7, seg=10, a0=0.4)
    rise = r_out + 2.2
    spr = c.z - Z
    arch_panel(mb, F, LX, r_out + 0.2, rise, spr, 0.0, 0.0, 0.15, VA, n=8)
    arch_band(mb, F, LX, r_out + 0.2, rise, spr, 0.0, 0.6, -0.1, 0.55, TRL, n=8)
    ogee_band(mb, F, LX, r_out + 0.8, rise + 0.6, spr, 0.5, -0.1, 0.8, CS, n=8)
    ccol("SG_DunPortal", F.p(LX - r_out, 0.0, -0.5), F.p(LX + r_out, 1.75, 2 * r_out - 0.6))
    return c                                     # (a inscricao do piso e o circulo runico do spawn, 11 a frente)


def spawn_circle(mb, cx, cy, r=4.2, k0=0):
    """CIRCULO RUNICO do spawn: placa baixa (+0,15) com aro de remate, faixa de obsidiana com 6 runas acesas (Neon
    escuro, +0,13) e miolo de marmore negro"""
    n = 16
    ang = [2 * math.pi * k / n for k in range(n)]
    zt, zb = Z + 0.15, Z - 0.1

    def circ(rr):
        return [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for a in ang]
    bm = mb.bm
    for outer, inner, m in ((circ(r), circ(r - 0.45), TRL), (circ(r - 0.45), circ(r - 1.85), OB)):
        oT = [bm.verts.new((x, y, zt)) for x, y in outer]
        iT = [bm.verts.new((x, y, zt)) for x, y in inner]
        oB = [bm.verts.new((x, y, zb)) for x, y in outer]
        iB = [bm.verts.new((x, y, zb)) for x, y in inner]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
            bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
            bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
        mb._post(oT + iT + oB + iB, m, None, 0, 1)
    mb.prism(circ(r - 1.85), zb, zt, MBK)
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        rad = Vector((math.cos(a), math.sin(a), 0.0))
        rune(mb, Vector((cx, cy, zt - 0.05)) + rad * (r - 1.15), Vector((-rad.y, rad.x, 0.0)), rad, UPZ, rk(k + k0), 1.1,
             VD, dep=0.18)
    # 10.05: sem seta no miolo (a direcao vem da luz e da moldura do portal)


def retable_bay(mk, mi, F, s0, s1):
    """RETABULO da R3 (variacao da sala: 'altar') no tramo do eixo do muro leste: a arcada cega do tramo, mesa de altar
    de obsidiana com frontal navy moldurado, 4 velas do kit, painel ogival interno com a runa grande em RELEVO de
    pedra (10.06: Neon medio so no miolo do traco)"""
    s = (s0 + s1) / 2.0
    blind_arch(mk, F, s0, s1, ARCH_SPRING["R3"], room="R3_altar", mi=mi)
    fblock(mk, F, s - 3.4, s + 3.4, -0.2, 1.9, -0.1, 0.45, OB, 0.1)                       # degrau
    fblock(mk, F, s - 2.9, s + 2.9, -0.2, 1.5, 0.45, 3.0, OB, 0.1)                        # corpo da mesa
    fledge(mk, F, s - 3.2, s + 3.2, [(-0.2, 3.0), (1.65, 3.0), (1.85, 3.16), (1.85, 3.38), (-0.2, 3.38)], TRL)
    fblock(mk, F, s - 2.1, s + 2.1, 1.5, 1.64, 1.0, 2.55, VA, 0.04)                       # frontal rebaixado
    for a, b, h0, h1 in ((s - 2.3, s - 2.1, 0.8, 2.75), (s + 2.1, s + 2.3, 0.8, 2.75), (s - 2.3, s + 2.3, 0.8, 1.0),
                         (s - 2.3, s + 2.3, 2.55, 2.75)):                                   # 10.06: frontal MOLDURADO
        fblock(mk, F, a, b, 1.5, 1.78, h0, h1, TRL, 0.0)
    rune_relief(mk, F.v(s, 1.64, 1.78), F.u(), UPZ, F.n(), 7, 1.2, TRL, VD, 0.12, 0.16)
    for sc in (s - 2.5, s - 1.6, s + 1.6, s + 2.5):
        p = F.v(sc, 0.7, 3.38)
        candle(mi, p.x, p.y, p.z, 0.62 if abs(sc - s) > 2.0 else 0.9, 1.1, dish=True)
    arch_panel(mk, F, s, 2.2, 2.6, 8.2, 3.38, 0.15, 0.32, VA, n=6)
    ogee_band(mk, F, s, 2.2, 2.6, 8.2, 0.42, 0.15, 0.62, TRL)
    for sc in (s - 2.41, s + 2.41):
        fblock(mk, F, sc - 0.21, sc + 0.21, 0.15, 0.62, 3.38, 8.2, TRL, 0.06)
    rune_relief(mk, F.v(s, 0.32, 6.6), F.u(), UPZ, F.n(), 6, 2.4, TRL, VD, 0.2, 0.3)       # 10.06: relevo de pedra
    fcol("SG_DunKit", F, s - 3.4, s + 3.4, 0.0, 1.9, -0.5, 3.4)


# ==================================================================== FINESSE 3 (AUDITORIA3 10.01-10.10): identidade das
# salas, abobada de pedra por tramo, grades ancoradas, portal em camadas, runas em relevo, lustres na escala, piso em
# lajes com ritmo, cabeceiras articuladas e saida em edicula
SLB = "Stone_SGDunSlab"                           # pano da abobada um valor acima do leito navy (10.01)
RK, RKD = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark"   # rocha exposta da galeria de mina (R2)
RUNES_OK = (0, 2, 6, 7, 8, 1, 5)                  # 10.05: sem as runas 3 e 4 (garfo = seta de UI)


def rk(i):
    return RUNES_OK[i % len(RUNES_OK)]


def rune_relief(mb, o, ea, eb, en, k, sc, stone=TRL, core=VD, dep=0.16, w=0.2):
    """runa em RELEVO de pedra (10.06): tracos de cantaria salientes 'dep' e o Neon medio so no MIOLO do traco (filete
    de 40% da largura, 0,05 sobre a pedra)"""
    rune(mb, o, ea, eb, en, k, sc, stone, dep, w)
    rune(mb, Vector(o) + Vector(en).normalized() * dep, ea, eb, en, k, sc, core, 0.05, w * 0.3)


# identidade por sala (10.02): pilastra (meia-largura, profundidade), luz (cor, energia), tipo de abobada
ROOM_ID = {
    "R1": dict(pil=(1.8, 1.8), light=((1.0, 0.68, 0.40), 12000.0), vault="crypt"),     # cripta de cantaria, ambar
    "R2": dict(pil=(1.8, 1.8), light=((0.76, 0.82, 1.0), 14000.0), vault="mine"),      # galeria de mina, luz fria
    "R3": dict(pil=(2.3, 2.2), light=((0.84, 0.66, 1.0), 20000.0), vault="rib"),       # santuario, violeta suave
}


def pil_hw(nm):
    return ROOM_ID[nm]["pil"][0]


def pil_d(nm):
    return ROOM_ID[nm]["pil"][1]


def pj(nm):
    """pilastra ao lado do vao (a moldura do vao fica entre as duas)"""
    return FRAME_HW + 0.3 + pil_hw(nm)


# ------------------------------------------------------------------ pilastra / tocha (largura por sala)
def pilaster(mb, F, s, top, area=None, twin=False, hw=PIL_HW, dep=PIL_D):
    """pilastra (09.10): soco de obsidiana em talude, fuste de cantaria, COLUNELO engastado (twin = colunelos DUPLOS,
    R3), capitel moldurado onde a nervura / o arco-diafragma nasce. R3 (10.02): pilastra maior (hw 2,3 x 2,2)"""
    W = hw
    fblock(mb, F, s - W - 0.35, s + W + 0.35, -0.2, dep + 0.45, -0.1, 0.7, OB, 0.0)
    fplinth(mb, F, s - W - 0.35, s + W + 0.35, dep + 0.45, 0.7, 1.0, 0.25, OB)
    fblock(mb, F, s - W, s + W, -0.2, dep, 1.0, top - 1.3, CS, 0.0)
    off = 0.3 * W
    for sc in ((s - off, s + off) if twin else (s,)):
        colonette(mb, F, sc, dep + 0.08, 1.0, top - 1.3, COL_R * (0.84 if twin else 1.0), n=6)
    fledge(mb, F, s - W - 0.3, s + W + 0.3, [(-0.2, top - 1.3), (dep + 0.3, top - 1.3), (dep + 0.62, top - 0.62),
                                             (dep + 0.66, top - 0.36), (dep + 0.66, top), (-0.2, top)], TRL)
    if area:
        fcol(area, F, s - W - 0.3, s + W + 0.3, 0.0, dep + 0.3, -0.5, top)


def torch(mb, F, s, d, h, twin=False, dmount=None, dep=PIL_D):
    """tocha de FERRO (09.11/12.09): BRACADEIRA em volta do colunelo (ou chapa na pedra: twin / dmount), braco com
    argola, cabo de madeira inclinado, cesto de 4 hastes curvas com trapo escuro e chama PEQUENA em gota (so ela
    emite). h = altura da chama; dmount = chapa numa face qualquer (edicula da saida)"""
    n, u = F.n(), F.u()
    cc = F.v(s, dep + 0.08, 0.0)
    zc = F.p(s, 0, h - 1.75)[2]
    if twin or dmount is not None:
        p = F.v(s, dep if dmount is None else dmount, h - 1.75)
        obox3(mb, p + n * 0.08, u, n, UPZ, 0.34, 0.16, 0.9, BI)
        root = p + n * 0.16
    else:
        EM._lathe(mb, (cc.x, cc.y, zc - 0.14), [(COL_R + 0.14, 0.0), (COL_R + 0.14, 0.28)], BI, 8, math.pi / 8)
        root = Vector((cc.x, cc.y, zc)) + n * (COL_R + 0.14)
    tip = root + n * 0.55 + UPZ * 0.28
    obox3(mb, (root + tip) / 2, (tip - root).normalized(), u, (tip - root).normalized().cross(u).normalized(),
          (tip - root).length + 0.06, 0.13, 0.13, BI)
    ax = (UPZ * 0.94 + n * 0.34).normalized()
    ring_c = tip + n * 0.14
    EM._lathe(mb, (ring_c.x, ring_c.y, ring_c.z - 0.09), [(0.19, 0.0), (0.19, 0.18)], BI, 6, 0.0, caps=(False, False))
    bot = ring_c - ax * 0.75
    lathe_ax(mb, bot, ax, [(0.07, 0.0), (0.12, 0.95), (0.14, 1.3)], WD, 6)
    top = bot + ax * 1.3
    lathe_ax(mb, top - ax * 0.05, ax, [(0.13, 0.0), (0.23, 0.26), (0.16, 0.42)], "Cloth_SG_Navy", 6)
    e1 = ax.cross(u).normalized()
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        rv = (u * math.cos(a) + e1 * math.sin(a))
        pts = [top + ax * 0.02 + rv * 0.12, top + ax * 0.24 + rv * 0.31, top + ax * 0.54 + rv * 0.24]
        mb.tube(pts, 0.035, BI, 3)
    EM._lathe(mb, (top.x + ax.x * 0.36, top.y + ax.y * 0.36, top.z + ax.z * 0.36),
              [(0.0, 0.0), (0.13, 0.14), (0.0, 0.47)], GL, 6)


# ------------------------------------------------------------------ grelha ancorada e escora com forro (10.03)
def grille(mb, mi, F, cs, h0, h1, hw):
    """GRELHA de ferro da cela (10.03): montantes de pedra chumbados (d -0,1..1,0), soleira e verga de remate, fundo
    escuro da cela, QUADRO de ferro chato (2 montantes + 2 travessas) dentro do vao com as barras presas nele, 2
    dobradicas de um lado e chapa de fechadura do outro: nada flutua na frente do campo"""
    # fundo da cela (obsidiana, mais escuro que o campo navy; 0,15 a frente dele: F11)
    slab(mb, F, [(cs - hw - 0.1, h0 - 0.1), (cs + hw + 0.1, h0 - 0.1), (cs + hw + 0.1, h1 + 0.1),
                 (cs - hw - 0.1, h1 + 0.1)], 0.15, 0.3, OB)
    for sg in (-1, 1):                                                                  # montantes de pedra
        a, b = sorted((cs + sg * hw, cs + sg * (hw + 0.55)))
        fblock(mb, F, a, b, -0.1, 1.0, h0 - 0.4, h1 + 0.4, TRL, 0.0)
    fblock(mb, F, cs - hw - 0.55, cs + hw + 0.55, -0.1, 1.0, h0 - 0.75, h0 - 0.4, TRL, 0.0)    # soleira
    fblock(mb, F, cs - hw - 0.55, cs + hw + 0.55, -0.1, 1.0, h1 + 0.4, h1 + 0.75, TRL, 0.0)    # verga
    d0, d1 = 0.42, 0.56                                                                 # quadro de ferro chato
    for sg in (-1, 1):
        a, b = sorted((cs + sg * (hw - 0.22), cs + sg * hw))
        fblock(mi, F, a, b, d0, d1, h0, h1, BI, 0.0)
    for hh in (h0, h1 - 0.2):
        fblock(mi, F, cs - hw, cs + hw, d0, d1, hh, hh + 0.2, BI, 0.0)
    for i in range(5):
        p = F.v(cs - hw + 0.22 + (2 * hw - 0.44) * (i + 0.5) / 5, (d0 + d1) / 2, 0.0)
        mi.rod((p.x, p.y, p.z + h0 + 0.1), (p.x, p.y, p.z + h1 - 0.1), 0.08, BI, 4)
    hh = h0 + (h1 - h0) * 0.5
    fblock(mi, F, cs - hw + 0.1, cs + hw - 0.1, d0 + 0.02, d1 - 0.02, hh - 0.09, hh + 0.09, BI, 0.0)
    for hh in (h0 + 0.6, h1 - 0.8):                                                     # dobradicas (lado esquerdo)
        p = F.v(cs - hw - 0.08, 0.49, hh)
        lathe_ax(mi, p, UPZ, [(0.13, 0.0), (0.13, 0.5)], BI, 6)
    fblock(mi, F, cs + hw - 0.5, cs + hw + 0.02, d1, d1 + 0.06, hh - 0.6, hh + 0.2, BI, 0.0)   # fechadura


def shoring(mb, F, cs, hw, spring):
    """ESCORA de madeira de mina (R2, 10.03): esteios sobre SAPATAS de pedra, chapeu com cunhas, maos-francesas,
    grampos de ferro e FORRO de pranchas entre os esteios (a madeira segura a rocha: nao e um portico solto)"""
    hp = 0.28
    zt = spring + 0.35
    for sg in (-1, 1):
        sp = cs + sg * (hw + 0.2)
        fblock(mb, F, sp - hp - 0.2, sp + hp + 0.2, 0.55, 1.3, -0.02, 0.3, OB, 0.0)               # sapata
        fblock(mb, F, sp - hp, sp + hp, 0.6, 1.16, 0.3, zt, WD, 0.0)
        fblock(mb, F, sp - hp - 0.14, sp + hp + 0.14, 0.46, 1.3, zt - 1.05, zt - 0.85, BI, 0.0)   # grampo
        a = F.v(sp - sg * 0.2, 0.88, zt - 1.7)
        b = F.v(sp - sg * 1.5, 0.88, zt - 0.15)
        mb.beam(a, b, 0.34, 0.34, WD, 0.05)
    fblock(mb, F, cs - hw - 0.75, cs + hw + 0.75, 0.55, 1.21, zt, zt + 0.62, WD, 0.0)             # chapeu
    for sg in (-1, 1):
        fblock(mb, F, cs + sg * (hw * 0.5) - 0.35, cs + sg * (hw * 0.5) + 0.35, 0.6, 1.15, zt + 0.62, zt + 0.84,
               WD, 0.0)
    for k in range(2):                                                                            # forro
        h = 2.6 + k * (zt - 5.0)
        fblock(mb, F, cs - hw - 0.2, cs + hw + 0.2, 0.3, 0.58, h - 0.3, h + 0.3, WD, 0.0)


def blind_arch(mb, F, s0, s1, spring=7.0, twin=False, room="R1", mi=None, skirt=True, deep=False):
    """arcada CEGA (09.10): campo navy rebaixado, ombreiras de cantaria, impostas de remate, arquivolta de 2 ORDENS
    (a interna em cantaria, a externa em remate) com chave; twin = arcada dupla sobre colunelo central.
    R2: grelha ancorada nos arcos da arcada dupla e escoras de mina nos simples. deep = ombreiras e arquivoltas
    profundas (nicho de cripta da R1)"""
    mi = mi or mb
    if skirt:
        skirting(mb, F, s0, s1)
    if twin:
        mid = (s0 + s1) / 2.0
        blind_arch(mb, F, s0, mid + 0.35, spring, False, room + "_twin", mi, False)
        blind_arch(mb, F, mid - 0.35, s1, spring, False, room + "_twin", mi, False)
        colonette(mb, F, mid, 0.45, 0.78, _arch_geo(s0, mid + 0.35, spring, room.startswith("R1"))[2], 0.34, n=6,
                  rot=0.0 if F.hz else math.pi / 2)
        return
    cs = (s0 + s1) / 2.0
    hw, rise, spring = _arch_geo(s0, s1, spring, room.startswith("R1"))
    if hw < 1.2:
        return
    dj, d1, d2 = (0.9, 0.9, 1.1) if deep else (0.34, 0.34, 0.52)
    arch_panel(mb, F, cs, hw + 0.15, rise + 0.15, spring, 0.78, 0.0, 0.15, VA, 3)
    for sg in (-1, 1):
        a, b = sorted((cs + sg * hw, cs + sg * (hw + 0.42)))
        fblock(mb, F, a, b, -0.1, dj, 0.78, spring - 0.34, CS, 0.0)
        a, b = sorted((cs + sg * (hw - 0.06), cs + sg * (hw + 0.62)))
        fledge(mb, F, a, b, [(-0.1, spring - 0.34), (dj + 0.22, spring - 0.34), (dj + 0.22, spring), (-0.1, spring)], TRL)
    ogee_band(mb, F, cs, hw, rise, spring, 0.4, -0.1, d1, CS, 3)
    if room != "R1_twin":
        ogee_band(mb, F, cs, hw + 0.3, rise + 0.3, spring, 0.52, -0.1, d2, TRL, 3)
    kz = spring + rise + 0.4
    fblock(mb, F, cs - 0.34, cs + 0.34, -0.1, d2 + 0.1, kz - 0.25, kz + 0.62, TRL, 0.0)
    if room == "R2_twin":
        grille(mb, mi, F, cs, 1.7, spring - 1.4, min(2.0, hw - 0.6))
    elif room == "R2":
        shoring(mi, F, cs, hw, spring)


def plaque(mb, F, s, k):
    """LAPIDE do nicho da cripta (R1): placa de obsidiana moldurada no fundo do nicho com uma runa em relevo de pedra
    (sem Neon: memoria, nao magia)"""
    fblock(mb, F, s - 1.3, s + 1.3, 0.15, 0.42, 2.2, 6.2, OB, 0.0)
    fblock(mb, F, s - 1.5, s + 1.5, 0.15, 0.3, 1.95, 2.2, TRL, 0.0)
    fblock(mb, F, s - 1.5, s + 1.5, 0.15, 0.3, 6.2, 6.45, TRL, 0.0)
    rune(mb, F.v(s, 0.42, 4.2), F.u(), UPZ, F.n(), rk(k), 2.2, TRL, 0.14, 0.2)


def tomb(mb, F, s, area=None):
    """arca tumular do nicho da cripta (R1, 10.02): caixa de obsidiana chanfrada sobre soco, tampa de remate em
    talude com cordao; dentro da profundidade da pilastra (nada na rota)"""
    fblock(mb, F, s - 1.6, s + 1.6, 0.2, 1.7, -0.05, 0.3, OB, 0.0)
    fblock(mb, F, s - 1.4, s + 1.4, 0.3, 1.55, 0.3, 1.5, OB, 0.12)
    pts = [F.v(ss, d, 1.5) for ss in (s - 1.5, s + 1.5) for d in (0.25, 1.62)]
    pts += [F.v(ss, d, 1.98) for ss in (s - 1.0, s + 1.0) for d in (0.6, 1.25)]
    hull(mb, pts, TRL)
    if area:
        fcol(area, F, s - 1.6, s + 1.6, 0.0, 1.7, -0.5, 2.0)


# ------------------------------------------------------------------ ABOBADA de pedra por tramo (10.01)
def _arc_table(hw, rise, nsmp=200):
    us = [-hw + 2.0 * hw * k / nsmp for k in range(nsmp + 1)]
    zs = [ogive_z(hw, rise, u) for u in us]
    cum = [0.0]
    for k in range(nsmp):
        cum.append(cum[-1] + math.hypot(us[k + 1] - us[k], zs[k + 1] - zs[k]))
    return us, zs, cum


def _u_at(tab, s):
    us, zs, cum = tab
    s = max(0.0, min(cum[-1], s))
    k = bisect.bisect_left(cum, s)
    if k <= 0:
        return us[0]
    if k >= len(cum):
        return us[-1]
    t = (s - cum[k - 1]) / max(1e-9, cum[k] - cum[k - 1])
    return us[k - 1] + (us[k] - us[k - 1]) * t


VAULT_NSEG = {"R1": 20, "R2": 18, "R3": 20}
VAULT_ROWS = {"R1": 2, "R2": 1, "R3": 1}
ARCH_W, ARCH_DEP, ARCH_NV = 1.6, 1.1, 15         # arco-diafragma: secao real (1,6 x 1,1), 15 aduelas + chave


def vault(mb, nm, rect, zf, spring, crown, ribs):
    """ABOBADA de berco ogival por tramo (10.01), com identidade por sala (10.02):
    - casca fechada (leito) em grelha de bandas x tramos, material por celula;
    - ARCOS-DIAFRAGMA de aduelas (secao 1,6 x 1,1, chave maior) nascendo dos capiteis das pilastras, formeretes nas
      cabeceiras;
    - R1 cripta: panos em LAJES de cantaria aparelhadas em fiada corrida (2 valores: laje x leito) sobre o leito;
    - R2 mina: ROCHA em estratos (bandas escuras salientes 0,3) com CERCHAS de madeira e tercas sob a rocha;
    - R3 santuario: NERVURAS em pera (transversais, cumeeira, liernes e tercelotes por tramo) com chaves em roseta e
      o pano da coroa um valor acima."""
    x0, y0, x1, y1 = rect
    xc, hw = (x0 + x1) / 2.0, (x1 - x0) / 2.0
    rise = crown - spring
    tab = _arc_table(hw, rise)
    total = tab[2][-1]
    kind = ROOM_ID[nm]["vault"]
    bm = mb.bm

    def zz(u):
        return zf + spring + ogive_z(hw, rise, u)

    def nrm(u):
        e = 0.05
        dz = (ogive_z(hw, rise, min(hw, u + e)) - ogive_z(hw, rise, max(-hw, u - e))) / (min(hw, u + e) - max(-hw, u - e))
        ln = math.hypot(dz, 1.0)
        return Vector((-dz / ln, 0.0, 1.0 / ln))                       # normal para FORA (cima)

    def P(u, y, d=0.0):
        """ponto da casca em (u, y) deslocado d para DENTRO da sala (ao longo da normal)"""
        p = Vector((xc + u, y, zz(u)))
        return p - nrm(u) * d if d else p

    def cell_faces(V, mats):
        """grelha V[j][i] (j ao longo de y) -> faces de baixo (visiveis) com material por celula + topo + bordas"""
        rows, cols = len(V), len(V[0])
        T = [[bm.verts.new(v.co + nrm(us[i]) * 0.35) for i, v in enumerate(row)] for row in V]
        allv = [v for r in V + T for v in r]
        faces = []
        byfm = {}
        for j in range(rows - 1):
            for i in range(cols - 1):
                f = bm.faces.new((V[j][i], V[j + 1][i], V[j + 1][i + 1], V[j][i + 1]))
                byfm.setdefault(mats(i, j), []).append(f)
                faces.append(bm.faces.new((T[j][i], T[j][i + 1], T[j + 1][i + 1], T[j + 1][i])))
        for j in range(rows - 1):
            faces.append(bm.faces.new((V[j][0], T[j][0], T[j + 1][0], V[j + 1][0])))
            faces.append(bm.faces.new((V[j][-1], V[j + 1][-1], T[j + 1][-1], T[j][-1])))
        for i in range(cols - 1):
            faces.append(bm.faces.new((V[0][i], V[0][i + 1], T[0][i + 1], T[0][i])))
            faces.append(bm.faces.new((V[-1][i], T[-1][i], T[-1][i + 1], V[-1][i + 1])))
        mb._post(allv, VA, None, 0, 1)
        for m, fs in byfm.items():
            if m != VA:
                mi_ = mb._mi_for(m)
                for f in fs:
                    f.material_index = mi_
                mb._uv(fs, m)

    nseg = VAULT_NSEG[nm]
    us = [_u_at(tab, total * k / nseg) for k in range(nseg + 1)]
    us[0], us[-1] = -hw, hw
    ys = [y0] + list(ribs) + [y1]
    if kind == "mine":
        # rocha em estratos: cada banda e uma faixa fechada propria; as impares (escuras) avancam 0,3
        STEP = (0.24, 0.4, 0.3, 0.44, 0.26, 0.38, 0.32, 0.42)       # saliencia do estrato por tramo (dirigida)
        for i in range(nseg):
            m = RKD if i % 2 else RK
            u0, u1 = us[i], us[i + 1]
            dd = [(STEP[(j + i) % len(STEP)] if i % 2 else 0.0) for j in range(len(ys))]
            lo = [[bm.verts.new(P(u, y, dd[j])) for u in (u0, u1)] for j, y in enumerate(ys)]
            hi = [[bm.verts.new(P(u, y, dd[j] - 0.35)) for u in (u0, u1)] for j, y in enumerate(ys)]
            for j in range(len(ys) - 1):
                bm.faces.new((lo[j][0], lo[j + 1][0], lo[j + 1][1], lo[j][1]))
                bm.faces.new((hi[j][0], hi[j][1], hi[j + 1][1], hi[j + 1][0]))
                bm.faces.new((lo[j][0], hi[j][0], hi[j + 1][0], lo[j + 1][0]))
                bm.faces.new((lo[j][1], lo[j + 1][1], hi[j + 1][1], hi[j][1]))
            for j in (0, len(ys) - 1):
                bm.faces.new((lo[j][0], lo[j][1], hi[j][1], hi[j][0]))
            mb._post([v for r in lo + hi for v in r], m, None, 0, 1)
    else:
        V = [[bm.verts.new(P(u, y)) for u in us] for y in ys]
        if kind == "rib":
            lim = 0.5 * hw
            cell_faces(V, lambda i, j: SLB if abs((us[i] + us[i + 1]) / 2.0) < lim else VA)
        else:
            cell_faces(V, lambda i, j: VA)
    # ---- arcos-diafragma de aduelas (todas as salas) e formeretes
    def vouss_arch(y, w, dep, nv, key, m=TRL):
        g = 0.07
        for k in range(nv):
            s0, s1 = total * k / nv + g, total * (k + 1) / nv - g
            u0, u1 = _u_at(tab, s0), _u_at(tab, s1)
            if k == 0:
                u0 = -hw
            if k == nv - 1:
                u1 = hw
            iskey = key and k == nv // 2
            ww, dd = (w + 0.7, dep + 0.55) if iskey else (w, dep)
            pts = [P(u, yy, d) for u in (u0, u1) for yy in (y - ww / 2.0, y + ww / 2.0) for d in (-0.1, dd)]
            hull(mb, pts, m)
    if kind == "mine":
        # cerchas de madeira (vigas de 1,2 em 8 lancos) 1,0 abaixo da rocha, sobre os capiteis; tercas e grampos
        def beam_arc(y, w, n, dtop):
            prof = [(-w / 2.0, -dtop - w), (w / 2.0, -dtop - w), (w / 2.0, -dtop), (-w / 2.0, -dtop)]
            pts = [_u_at(tab, total * k / n) for k in range(n + 1)]
            pts[0], pts[-1] = -hw + 0.35, hw - 0.35
            rings = []
            for k, u in enumerate(pts):
                p = P(u, y)
                N = nrm(u)
                t = (P(pts[min(n, k + 1)], y) - P(pts[max(0, k - 1)], y)).normalized()
                side = t.cross(N).normalized()
                rings.append([bm.verts.new(p + side * a + N * b) for a, b in prof])
            for r0, r1 in zip(rings, rings[1:]):
                for j in range(4):
                    bm.faces.new((r0[j], r0[(j + 1) % 4], r1[(j + 1) % 4], r1[j]))
            bm.faces.new(list(reversed(rings[0])))
            bm.faces.new(rings[-1])
            mb._post([v for r in rings for v in r], WD, None, 0, 1)
        for y in ribs:
            beam_arc(y, 1.25, 8, 1.15)
        for f in (0.0, -0.45, 0.45):
            u = f * hw
            a, b = P(u, y0 + 0.3, 0.75), P(u, y1 - 0.3, 0.75)
            mb.beam(a, b, 0.8, 0.8, WD, 0.04)
            for y in ribs:                                              # grampo de ferro na cruz terca x cercha
                c = P(u, y, 1.15)
                obox3(mb, c, Vector((1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0)), UPZ, 1.0, 1.55, 0.95, BI)
        for y in (y0 + 0.5, y1 - 0.5):
            vouss_arch(y, 1.0, 0.7, 11, False)
    else:
        for y in ribs:
            vouss_arch(y, ARCH_W, ARCH_DEP, ARCH_NV, True)
        for y in (y0 + 0.5, y1 - 0.5):
            vouss_arch(y, 1.0, 0.7, 11, False)
    if kind == "crypt":
        # lajes aparelhadas em fiada corrida (3 fiadas por tramo, meia laje de desencontro), 0,17 abaixo do leito
        band = total / nseg
        rows = VAULT_ROWS[nm]
        gap = 0.2
        for j in range(len(ys) - 1):
            ya, yb = ys[j], ys[j + 1]
            for r in range(rows):
                ra, rb = ya + (yb - ya) * r / rows, ya + (yb - ya) * (r + 1) / rows
                ra, rb = ra + (gap if r else ARCH_W / 2.0 + 0.15), rb - (gap if r < rows - 1 else ARCH_W / 2.0 + 0.15)
                if j == 0 and r == 0:
                    ra = ya + 1.2
                if j == len(ys) - 2 and r == rows - 1:
                    rb = yb - 1.2
                shift = 0.5 * band if (j * rows + r) % 2 else 0.0
                cuts = [0.0] + [min(total, band * (k + 1) - shift) for k in range(nseg) if 0.0 < band * (k + 1) - shift < total - 0.5] + [total]
                for sa, sb in zip(cuts, cuts[1:]):
                    sa2, sb2 = sa + (gap if sa > 0 else 0.3), sb - (gap if sb < total else 0.3)
                    if sb2 - sa2 < 0.8:
                        continue
                    ua, ub = _u_at(tab, sa2), _u_at(tab, sb2)
                    Fr = [bm.verts.new(P(u, y, 0.17)) for u, y in ((ua, ra), (ub, ra), (ub, rb), (ua, rb))]
                    Bk = [bm.verts.new(P(u, y, 0.02)) for u, y in ((ua, ra), (ub, ra), (ub, rb), (ua, rb))]
                    bm.faces.new(list(reversed(Fr)))
                    bm.faces.new(Bk)
                    for q in range(4):
                        q2 = (q + 1) % 4
                        bm.faces.new((Fr[q], Fr[q2], Bk[q2], Bk[q]))
                    mb._post(Fr + Bk, SLB, None, 0, 1)
    if kind == "rib":
        # nervuras em pera: cumeeira, liernes e TERCELOTES por tramo (do capitel ao meio do tramo na cumeeira)
        def pear5(w, dep):
            h = w / 2.0
            return [(-h, 0.1), (h, 0.1), (h * 0.82, -dep * 0.52), (0.0, -dep), (-h * 0.82, -dep * 0.52)]

        def rib(uys, prof):
            rings = []
            n = len(uys)
            for k, (u, y) in enumerate(uys):
                p = P(u, y)
                N = nrm(u)
                p0 = P(*uys[max(0, k - 1)])
                p1 = P(*uys[min(n - 1, k + 1)])
                t = (p1 - p0).normalized()
                side = t.cross(N).normalized()
                rings.append([bm.verts.new(p + side * a + N * b) for a, b in prof])
            kk = len(prof)
            for r0, r1 in zip(rings, rings[1:]):
                for j in range(kk):
                    bm.faces.new((r0[j], r0[(j + 1) % kk], r1[(j + 1) % kk], r1[j]))
            bm.faces.new(list(reversed(rings[0])))
            bm.faces.new(rings[-1])
            mb._post([v for r in rings for v in r], TRL, None, 0, 1)
        prof_w = pear5(0.7, 0.62)
        rib([(0.0, y0 + 0.5), (0.0, y1 - 0.5)], pear5(0.9, 0.85))                       # cumeeira
        for sg in (-1, 1):
            u = sg * 0.5 * hw
            rib([(u, y0 + 0.5), (u, y1 - 0.5)], prof_w)                                  # liernes
        for ya, yb in zip(ys, ys[1:]):
            ym = (ya + yb) / 2.0
            for sg in (-1, 1):
                for yy in (ya, yb):
                    n_ = 5
                    pts = [(sg * abs(_u_at(tab, total / 2.0 * (1.0 - k / n_))), yy + (ym - yy) * k / n_)
                           for k in range(n_ + 1)]
                    pts[0] = (sg * (hw - 0.3), pts[0][1])
                    rib(pts, prof_w)
            x, y = xc, ym                                                                # chave do meio do tramo
            EM._lathe(mb, (x, y, zz(0.0) - 0.95), [(0.0, -0.05), (0.4, 0.0), (0.85, 0.3), (1.0, 0.62), (0.86, 0.95)],
                      TRL, 6, math.pi / 6, caps=(False, True))
        for y in ribs:                                                                   # chaves nos cruzamentos
            EM._lathe(mb, (xc, y, zz(0.0) - ARCH_DEP - 0.55 - 0.7), [(0.0, -0.05), (0.42, 0.0), (0.9, 0.32), (1.05, 0.66),
                                                                     (0.9, 0.98)], TRL, 6, math.pi / 6, caps=(False, True))


def vault_hang(nm, rect, y):
    """cota onde um lustre pode pendurar em (eixo, y): fundo da chave do arco (R1/R3), da cercha (R2) ou da roseta"""
    crown = vault_z(rect, "y", Z, R_SPR, R_CROWN, 0.0)
    kind = ROOM_ID[nm]["vault"]
    if kind == "mine":
        return crown - 1.15 - 1.25 - 0.1
    if kind == "rib":
        return crown - 0.95 - 1.0
    return crown - ARCH_DEP - 0.55 - 0.1


# ------------------------------------------------------------------ cabeceiras articuladas (10.09)
def headwall(mk, F, nm, kind):
    """timpano dos muros de ponta (entre a cornija e a abobada): TRIBUNA CEGA de lancetas sobre peitoril (3 por lado
    na R1, 5 nas arenas), e ROSACEA escura (roda de pedra com campo navy) no eixo, acima da moldura central"""
    x0, y0, x1, y1 = ROOMS[nm]
    rect = (x0, y0, x1, y1)
    xc = (x0 + x1) / 2.0
    hwr = (x1 - x0) / 2.0
    inner = (PORTAL_R[1] + 0.2 + 0.6 + 0.5 + 0.4) if kind == "arrival" else (FRAME_HW + 1.1 + 0.5)
    h0 = R_SPR + 1.4
    for sg in (-1, 1):
        s_in = xc + sg * (inner + 0.5)
        umax = hwr - CORNER - 0.5
        while umax > inner + 6.0 and vault_z(rect, "y", 0.0, R_SPR, R_CROWN, umax) - 1.0 < h0 + 7.4:
            umax -= 0.5
        s_out = xc + sg * umax
        span = abs(s_out - s_in)
        n = 3 if nm == "R1" else 4
        pier = 0.7
        aw = (span - (n - 1) * pier) / n
        fledge(mk, F, min(s_in, s_out), max(s_in, s_out), [(-0.1, h0 - 0.55), (0.55, h0 - 0.55), (0.66, h0 - 0.25),
                                                            (0.66, h0), (-0.1, h0)], TRL)
        for k in range(n):
            cs = s_in + sg * (aw / 2.0 + k * (aw + pier))
            hw = aw / 2.0 - 0.72
            uo = abs(cs - xc) + hw + 0.9
            zv = vault_z(rect, "y", 0.0, R_SPR, R_CROWN, min(hwr - 0.01, uo)) - 1.0
            rise = hw * 1.5
            spr = h0 + max(2.6, hw * 1.3)
            if spr + rise + 0.5 > zv:
                spr = zv - rise - 0.5
            if spr < h0 + 1.6:
                continue
            arch_panel(mk, F, cs, hw, rise, spr, h0, 0.0, 0.15, VA, 3)
            for q in (-1, 1):
                a, b = sorted((cs + q * hw, cs + q * (hw + 0.42)))
                fblock(mk, F, a, b, -0.1, 0.45, h0, spr, TRL, 0.0)
            ogee_band(mk, F, cs, hw, rise, spr, 0.45, -0.1, 0.5, TRL, 3)
    # rosacea escura no eixo
    zr = 30.0 if kind == "arrival" else 39.0
    r = 2.6
    c = F.v(xc, 0.0, zr)
    u, v, n = F.u(), UPZ, F.n()
    ring3(mk, c, u, v, n, r - 0.5, r, 0.0, 0.5, TRL, 12)
    disc3(mk, c, u, v, n, r - 0.5, 0.0, 0.15, VA, 12)
    for i in range(6):
        a = 2 * math.pi * i / 6 + math.pi / 6
        rad = u * math.cos(a) + v * math.sin(a)
        obox3(mk, c + rad * ((r - 0.5 + 0.55) / 2.0) + n * 0.3, rad, u * -math.sin(a) + v * math.cos(a), n,
              r - 0.5 - 0.55 + 0.1, 0.3, 0.3, TRL)
    lathe_ax(mk, c + n * 0.15, n, [(0.0, 0.0), (0.5, 0.05), (0.6, 0.35), (0.0, 0.55)], TRL, 8)


# ------------------------------------------------------------------ piso em lajes com ritmo (10.08)
def tile_floor(mb, rect, z, skip=None, mod=7.0, border=3.5, gap=0.25):
    """piso (10.08): leito de junta escuro, friso de remate junto as paredes, BORDADURA de lajes mais escuras e
    campo de lajes medias em FIADA CORRIDA (meia laje de desencontro a cada fiada): sem faixa central, pedra fosca.
    skip(a, b, ya, yb) -> True = laje nao entra (medalhao)."""
    x0, y0, x1, y1 = rect
    mb.box2((x0, y0, z - 0.6), (x1, y1, z - 0.15), FL, 0.0)

    def ringbox(a, b, m):
        ax0, ay0, ax1, ay1 = x0 + a, y0 + a, x1 - a, y1 - a
        bx0, by0, bx1, by1 = x0 + b, y0 + b, x1 - b, y1 - b
        mb.box2((ax0, ay0, z - 0.4), (ax1, by0, z), m, 0.0)
        mb.box2((ax0, by1, z - 0.4), (ax1, ay1, z), m, 0.0)
        mb.box2((ax0, by0, z - 0.4), (bx0, by1, z), m, 0.0)
        mb.box2((bx1, by0, z - 0.4), (ax1, by1, z), m, 0.0)
    ringbox(0.0, 1.0, FL)
    ringbox(1.0, 1.8, TRL)
    b0, b1 = 1.8, 1.8 + border
    # bordadura: lajes compridas (2 x mod) em volta, sentido do muro
    for (xa, ya, xb, yb, horiz) in ((x0 + b0, y0 + b0, x1 - b0, y0 + b1, True), (x0 + b0, y1 - b1, x1 - b0, y1 - b0, True),
                                    (x0 + b0, y0 + b1, x0 + b1, y1 - b1, False), (x1 - b1, y0 + b1, x1 - b0, y1 - b1, False)):
        ln = (xb - xa) if horiz else (yb - ya)
        nn = max(1, int(round(ln / (mod * 1.4))))
        t = ln / nn
        for k in range(nn):
            if horiz:
                mb.box2((xa + t * k + gap / 2, ya + gap / 2, z - 0.4), (xa + t * (k + 1) - gap / 2, yb - gap / 2, z), CS, 0.0)
            else:
                mb.box2((xa + gap / 2, ya + t * k + gap / 2, z - 0.4), (xb - gap / 2, ya + t * (k + 1) - gap / 2, z), CS, 0.0)
    ix0, iy0, ix1, iy1 = x0 + b1, y0 + b1, x1 - b1, y1 - b1
    nx = max(1, int(round((ix1 - ix0) / mod)))
    ny = max(1, int(round((iy1 - iy0) / mod)))
    tx, ty = (ix1 - ix0) / nx, (iy1 - iy0) / ny
    for j in range(ny):
        ya, yb = iy0 + ty * j, iy0 + ty * (j + 1)
        if j % 2:
            cuts = [ix0] + [ix0 + tx * (i + 0.5) for i in range(nx)] + [ix1]
        else:
            cuts = [ix0 + tx * i for i in range(nx + 1)]
        for a, b in zip(cuts, cuts[1:]):
            if skip and skip(a, b, ya, yb):
                continue
            mb.box2((a + gap / 2, ya + gap / 2, z - 0.4), (b - gap / 2, yb - gap / 2, z), BL, 0.0)


# ------------------------------------------------------------------ lustres na escala das salas (10.07)
def candle_lite(mb, x, y, z, hc=0.8, s=1.3):
    """vela do kit em versao de lustre (vista de 20 abaixo): prato, vela creme e chama em gota"""
    EM._lathe(mb, (x, y, z), [(0.34 * s, 0.0), (0.34 * s, 0.08 * s), (0.0, 0.08 * s)], IR, 6, caps=(True, False))
    z += 0.08 * s
    r = 0.1 * s
    EM._lathe(mb, (x, y, z), [(r, 0.0), (r, hc - 0.04 * s), (0.0, hc - 0.01 * s)], WAX, 5, caps=(False, False))
    zf = z + hc + 0.03 * s
    EM._lathe(mb, (x, y, zf), [(0.0, 0.0), (0.12 * s, 0.15 * s), (0.0, 0.46 * s)], GL, 6)


def chandelier(mb, x, y, h, top, r=5.0, n=8, m=BI, inner=0, mi=BI):
    """lustre de ferro (10.07, escala das salas de 104): aro em tubo, bracos em S, balaustre de torno, velas do kit e
    haste presa na chave do arco por uma roseta; inner > 0 = COROA de 2 niveis (aro interno mais alto)"""
    def ring(rr, hh, nn):
        mb.tube([(x + rr * math.cos(2 * math.pi * k / 16), y + rr * math.sin(2 * math.pi * k / 16), hh)
                 for k in range(17)], 0.2, m, 5)
        for k in range(nn):
            a = 2 * math.pi * k / nn + math.pi / nn
            ca, sa = math.cos(a), math.sin(a)
            pts = [(x + q * ca, y + q * sa, hh + zz) for q, zz in ((0.35, 1.0), (rr * 0.35, 0.25), (rr * 0.7, 0.6),
                                                                      (rr, 0.15))]
            mb.tube(pts, 0.1, m, 3)
            candle_lite(mb, x + rr * ca, y + rr * sa, hh + 0.12)
    ring(r, h, n)
    EM._lathe(mb, (x, y, h - 0.4), [(0.0, 0.0), (0.38, 0.25), (0.52, 0.55), (0.25, 1.1), (0.38, 1.4), (0.15, 1.75),
                                    (0.15, 2.2)], mi, 6, caps=(False, True))
    if inner:
        ring(r * 0.5, h + 1.8, inner)
        mb.rod((x, y, h + 1.4), (x, y, h + 2.8), 0.15, mi, 6)
    mb.rod((x, y, h + (2.8 if inner else 2.0)), (x, y, top - 0.2), 0.13, mi, 6)
    EM._lathe(mb, (x, y, top - 0.6), [(0.14, 0.0), (0.7, 0.4), (0.74, 0.55), (0.0, 0.62)], mi, 6, caps=(True, False))


# ------------------------------------------------------------------ saida em edicula (10.10) e portal em camadas (10.04)
def exit_arch(mb, F, s, orders=2, clad=None, mi=None):
    """SAIDA por prompt ('Sair'): EDICULA (10.10): o tramo e revestido com cantaria de 1,5 (clad = (s0, s1)) que deixa
    o aro num NICHO recuado, capa ogival de 2 ordens saliente, SOLEIRA de remate e 2 tochas na cantaria. O vortice
    fica apagado (disco navy + espiral de pedra negra). Colisao: aro e revestimento."""
    r_in, r_out = EXIT_R
    n = F.n()
    c = F.v(s, 1.0, r_out - 0.3)
    u = n.cross(UPZ).normalized()
    portal_frame(mb, c, u, UPZ, n, r_in, r_out, Z, nv=12, seg=16)
    disc3(mb, c, u, UPZ, n, r_in + 0.15, -0.5, -0.3, VA, 24)
    spiral(mb, c, u, UPZ, n, r_in - 0.2, -0.28, -0.12, OB, arms=5, twist=2.7, seg=5, a0=0.8)
    rise = r_out + 0.9
    spr = c.z - Z
    hwo = r_out + 0.2
    arch_panel(mb, F, s, hwo, rise, spr, 0.0, 0.0, 0.15, VA, n=8)
    if clad:
        s0, s1 = clad
        dc = 1.5
        t1, t2 = 0.6, 0.45
        ho = hwo + t1 + t2                                     # borda externa da capa
        apex = spr + rise + t1 + t2
        top = apex + 2.4                                       # a edicula para abaixo da cornija: le como porche
        fblock(mb, F, s0, s - ho, -0.1, dc, -0.1, top, CS, 0.0)
        fblock(mb, F, s + ho, s1, -0.1, dc, -0.1, top, CS, 0.0)
        fblock(mb, F, s - ho, s + ho, -0.1, dc, apex, top, CS, 0.0)
        fledge(mb, F, s0, s1, [(-0.1, top), (dc + 0.35, top), (dc + 0.35, top + 0.3), (dc + 0.1, top + 0.55),
                               (-0.1, top + 0.55)], TRL)       # coroamento de remate
        for q in (-1, 1):                                      # ombreiras da 2a ordem (ate o arranque)
            a, b = sorted((s + q * (hwo + t1), s + q * ho))
            fblock(mb, F, a, b, -0.1, dc, -0.1, spr, CS, 0.0)
        outer = ogive(s, ho, rise + t1 + t2, spr, 8)
        half = len(outer) // 2
        spandrel(mb, F, (s - ho, apex), outer[:half + 1], -0.1, dc, CS)
        spandrel(mb, F, (s + ho, apex), outer[half:], -0.1, dc, CS)
        arch_band(mb, F, s, hwo, rise, spr, 0.0, t1, dc - 0.1, dc + 0.55, TRL, n=8)
        ogee_band(mb, F, s, hwo + t1, rise + t1, spr, t2, dc - 0.1, dc + 0.8, CS, n=8)
        # soleira de remate (placa +0,15) e tochas na cantaria
        mb.box2(F.p(s - ho - 0.2, -0.1, -0.4), F.p(s + ho + 0.2, dc + 1.3, 0.15), TRL, 0.06)
        for q in (-1, 1):
            torch(mi or mb, F, s + q * (ho + 1.3), 0.0, 9.0, dmount=dc)
        ccol("SG_DunExit", F.p(s0, 0.0, -0.5), F.p(s - ho, dc, top))
        ccol("SG_DunExit", F.p(s + ho, 0.0, -0.5), F.p(s1, dc, top))
    else:
        t = 0.6 if orders == 2 else 0.5
        arch_band(mb, F, s, hwo, rise, spr, 0.0, t, -0.1, 0.55, TRL, n=8)
        if orders == 2:
            ogee_band(mb, F, s, r_out + 0.8, rise + 0.6, spr, 0.4, -0.1, 0.8, CS, n=8)
        mb.box2(F.p(s - r_out - 0.25, -0.1, -0.4), F.p(s + r_out + 0.25, 2.2, 0.15), TRL, 0.06)
    ccol("SG_DunExit", F.p(s - r_out, 0.0, -0.5), F.p(s + r_out, 1.75, 2 * r_out - 0.6))


def niche(mk, ms, F):
    """NICHO do muro norte da R3 (DUN_NEXT_R3): fundo 1,5 atras do plano medio do muro, bochechas e teto de cantaria.
    10.04: no fundo uma MOLDURA OGIVAL de aduelas com runas em relevo abraca o VORTICE EM CAMADAS (vazio profundo ->
    anel navy -> fios acesos -> espiral do jogo), nada de disco solto dentro da caixa."""
    y1 = ROOMS["R3"][3]
    yw = y1 + WT
    yb = NICHE_BACK
    hw = LINK_HW
    zb = Z - 0.6
    mk.box2((LX - hw - 1.2, yb, zb), (LX + hw + 1.2, yb + 1.4, Z + LINK_H + 1.2), CS, 0.0)
    for sg in (-1, 1):
        a, b = sorted((LX + sg * hw, LX + sg * (hw + 1.2)))
        mk.box2((a, yw - 0.05, zb), (b, yb, Z + LINK_H + 1.2), CS, 0.0)
    mk.box2((LX - hw, yw - 0.05, Z + LINK_H), (LX + hw, yb, Z + LINK_H + 1.2), CS, 0.0)
    ccol("SG_DunRoom", (LX - hw - 1.2, yb, Z - 0.5), (LX + hw + 1.2, yb + 1.4, Z + LINK_H + 1.2))
    Fb = Face(True, yb, -1, Z)                    # face do fundo do nicho (olha para -y)
    cz = 11.0
    R = 9.7
    # moldura ogival de aduelas: ombreiras do piso ao arranque (11), ogiva de 11,6 de meia-largura, chave e impostas
    hwf, t = R + 1.0, 1.9
    risef = 9.2
    for sg in (-1, 1):
        a, b = sorted((LX + sg * hwf, LX + sg * (hwf + t)))
        for k in range(4):
            h0, h1 = k * cz / 4.0 + (0.06 if k else -0.1), (k + 1) * cz / 4.0 - 0.06
            fblock(mk, Fb, a, b, 0.0, 0.62 if k % 2 == 0 else 0.5, h0, h1, TRL if k else OB, 0.0)
        fledge(mk, Fb, min(a, b) - 0.2, max(a, b) + 0.2, [(0.0, cz - 0.04), (0.78, cz - 0.04), (0.78, cz + 0.3),
                                                          (0.0, cz + 0.3)], TRL)
    ogive_vouss(mk, Fb, LX, hwf, risef, cz, t, 0.0, 0.62, TRL, n=12, per=2)
    arch_panel(mk, Fb, LX, hwf, risef, cz, 0.0, 0.0, 0.15, VA, n=10)
    kz = cz + risef + t
    fblock(mk, Fb, LX - 0.8, LX + 0.8, 0.0, 0.95, kz - 1.7, kz + 0.9, TRL, 0.1)
    rune_relief(mk, Fb.v(LX, 0.95, kz - 0.4), Fb.u(), UPZ, Fb.n(), 8, 1.3, TRL, VD, 0.12, 0.16)
    mid = ogive(LX, hwf + t / 2.0, risef + t / 2.0, cz, 12)              # runas em relevo nas aduelas
    for i, k in enumerate((3, 8, 16, 21)):
        rune_relief(mk, Fb.v(mid[k][0], 0.62, mid[k][1]), Fb.u(), UPZ, Fb.n(), rk(i), 0.9, TRL, VD, 0.1, 0.14)
    # vortice em camadas no campo da moldura
    c = Vector((LX, yb, Z + cz))
    u, v, n = Vector((1, 0, 0)), UPZ, Vector((0, -1, 0))
    disc3(mk, c, u, v, n, 6.4, 0.15, 0.22, VO, 24)                     # vazio profundo
    ring3(mk, c, u, v, n, 6.4, R, 0.15, 0.3, VA, 32)                    # anel navy
    ring3(mk, c, u, v, n, 6.3, 6.5, 0.15, 0.48, VD, 24)                 # fio interno
    ring3(mk, c, u, v, n, R, R + 0.8, 0.15, 0.55, OB, 32)               # aro de obsidiana
    ring3(mk, c, u, v, n, R - 0.12, R + 0.05, 0.15, 0.7, VD, 32)        # fio externo
    spiral(ms, c, u, v, n, 9.0, 0.32, 0.5, VG, arms=5, twist=2.7, a0=1.1)
    return c, n


# ------------------------------------------------------------------ tramos, pilastras das pontas e KIT das salas
def fill_bay(mk, mi, F, nm, sa, sb, idx, long=False):
    """tramo entre pilastras: a arcada cega do kit com a identidade da sala (10.02): R1 cripta = nicho fundo com arca
    tumular alternando com lancetas geminadas (muros longos); R2 mina = cela com grelha ancorada alternando com escora
    de madeira; R3 santuario = arcos altos simples"""
    w = sb - sa
    if w < 2.8:
        skirting(mk, F, sa, sb)
        return
    spr = ARCH_SPRING[nm]
    if nm == "R1":
        if long:
            blind_arch(mk, F, sa, sb, spr, room="R1", mi=mi, deep=True)
            if idx % 2 == 0:
                tomb(mk, F, (sa + sb) / 2.0, "SG_DunKit")
            else:
                plaque(mk, F, (sa + sb) / 2.0, idx)
        else:
            blind_arch(mk, F, sa, sb, spr, twin=w > 9.0, room="R1", mi=mi)
    elif nm == "R2":
        blind_arch(mk, F, sa, sb, spr, room="R2_twin" if idx % 2 else "R2", mi=mi)
    else:
        blind_arch(mk, F, sa, sb, spr, twin=w > 16.0, room="R3", mi=mi)


def bays_between(a, b, ps, hw=PIL_HW):
    """tramos livres entre a e b cortados pelas pilastras ps (meia-largura hw)"""
    cuts = [a] + [q for p in sorted(ps) if a < p < b for q in (p - hw - 0.3, p + hw + 0.3)] + [b]
    return [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts), 2)]


def end_pils(nm, side):
    x0, y0, x1, y1 = ROOMS[nm]
    hw = (x1 - x0) / 2.0
    p = pj(nm)
    m = (p + hw - 0.75) / 2.0                    # pilastra do meio: 2 tramos iguais ate a coluna de canto
    ps = [-m, -p, p, m]
    if (nm, side) == ("R1", "S"):
        ps = [-p, p, m]                          # o tramo oeste inteiro e o da saida (DUN_EXIT_R1 em x -30)
    return [LX + q for q in ps]


def torch_pils(nm, side, ps):
    if side in ("W", "E"):
        return [ps[k] for k in (0, len(ps) - 1)]
    if END[(nm, side)] == "link" and nm != "R1":
        return []
    if (nm, side) == ("R1", "N"):
        return []
    return [p for p in ps if abs(abs(p - LX) - pj(nm)) < 0.1]


_R2 = ROOMS["R2"]
_P1, _P2 = (ROOMS["R1"][3] - ROOMS["R1"][1]) / PITCH_N["R1"], (_R2[3] - _R2[1]) / PITCH_N["R2"]
# lustres (10.07): (sala, x, y, altura do aro, raio, velas, velas do aro interno, material do aro) - R1: 2 nos arcos 2 e
# 4; R2: 2 rodas de madeira nas cerchas 2 e 5; R3: COROA de 2 niveis no meio do tramo central (sobre o medalhao)
CHANDELIERS = (("R1", LX, ROOMS["R1"][1] + 2.0 * _P1, 21.0, 5.0, 8, 0, BI),
               ("R1", LX, ROOMS["R1"][1] + 4.0 * _P1, 21.0, 5.0, 8, 0, BI),
               ("R2", LX, _R2[1] + 2.0 * _P2, 21.5, 5.6, 8, 0, WD),
               ("R2", LX, _R2[1] + 5.0 * _P2, 21.5, 5.6, 8, 0, WD),
               ("R3", LX, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0, 20.0, 8.0, 12, 6, BI))


def room_kit():
    """kit das salas (FINESSE 3): pilastras com colunelo e capitel de onde nasce o arco-diafragma, colunas de canto,
    arcadas cegas com a identidade DIRIGIDA de cada sala, cornija, tochas, piso em lajes com ritmo, abobada de pedra
    por tramo, vaos/portais em camadas, portal de chegada, saidas em edicula, spawns, retabulo, cabeceiras e lustres"""
    mk = MB("SG_Dun_Rooms_Kit", "17_DUNGEON", random.Random(751), detail="near")
    mv = MB("SG_Dun_Rooms_Vault", "17_DUNGEON", random.Random(753), detail="near")
    mf = MB("SG_Dun_Rooms_Floor", "17_DUNGEON", random.Random(755), detail="far", floor=Z - 0.4)
    mfd = MB("SG_Dun_Rooms_FloorInlay", "17_DUNGEON", random.Random(756), detail="near")
    mi = MB("SG_Dun_Rooms_Iron", "17_DUNGEON", random.Random(757), detail="near")
    mp = MB("SG_Dun_Rooms_Portals", "17_DUNGEON", random.Random(761), detail="near")
    A = "SG_DunKit"
    for nm in ORDER:
        x0, y0, x1, y1 = ROOMS[nm]
        Fs = room_faces(nm)
        twin = nm == "R3"
        hw, dep = pil_hw(nm), pil_d(nm)
        ribs = rib_ys(nm)
        # ---- muros longos (oeste / leste): pilastras nos pontos dos arcos-diafragma
        for side in ("W", "E"):
            F = Fs[side]
            for p in ribs:
                pilaster(mk, F, p, R_SPR, A, twin=twin, hw=hw, dep=dep)
            for p in torch_pils(nm, side, ribs):
                torch(mi, F, p, 0.0, TORCH_H, twin=twin, dep=dep)
            bays = bays_between(y0 + CORNER + 0.1, y1 - CORNER - 0.1, ribs, hw)
            for i, (sa, sb) in enumerate(bays):
                if nm == "R3" and side == "W" and i == 0:
                    skirting(mk, F, sa, sb)
                    exit_arch(mp, F, EXIT_S["R3"], orders=1)
                elif nm == "R3" and side == "E" and i == len(bays) // 2:
                    skirting(mk, F, sa, sb)
                    retable_bay(mk, mi, F, sa, sb)
                else:
                    fill_bay(mk, mi, F, nm, sa, sb, i, long=True)
            cornice(mk, F, y0 + 2.4, y1 - 2.4, R_SPR)
        # ---- muros de ponta (sul / norte): colunas de canto, pilastras, vao/portal/nicho no eixo, cabeceira
        for side in ("S", "N"):
            F = Fs[side]
            kind = END[(nm, side)]
            corner_col(mk, F, x0, 1, R_SPR, A)
            corner_col(mk, F, x1, -1, R_SPR, A)
            ps = end_pils(nm, side)
            for p in ps:
                pilaster(mk, F, p, R_SPR, A, twin=twin, hw=hw, dep=dep)
            for p in torch_pils(nm, side, ps):
                torch(mi, F, p, 0.0, TORCH_H, twin=twin, dep=dep)
            headwall(mk, F, nm, kind)
            if kind == "arrival":
                arrival_portal(mp, F)
                hwp = PORTAL_R[1] + 0.2 + 0.6 + 0.5 + 0.4
                spans = [(x0 + CORNER + 0.1, LX - hwp), (LX + hwp, x1 - CORNER - 0.1)]
            else:
                link_frame(mk, F, kind)
                spans = [(x0 + CORNER + 0.1, LX - FRAME_HW - 0.1), (LX + FRAME_HW + 0.1, x1 - CORNER - 0.1)]
            k = 0
            for a, b in spans:
                for sa, sb in bays_between(a, b, ps, hw):
                    if kind == "arrival" and sa < EXIT_S["R1"] < sb:
                        exit_arch(mp, F, EXIT_S["R1"], clad=(sa, sb), mi=mi)
                    else:
                        fill_bay(mk, mi, F, nm, sa, sb, k)
                    cornice(mk, F, sa - 0.1, sb + 0.1, R_SPR)
                    k += 1
        # ---- piso, spawn, abobada
        tile_floor(mf, (x0, y0, x1, y1), Z, mod=7.5)
        sx, sy = L.dun_spawn(nm)
        spawn_circle(mfd, sx, sy, 4.2, k0={"R1": 0, "R2": 2, "R3": 4}[nm])
        vault(mv, nm, (x0, y0, x1, y1), Z, R_SPR, R_CROWN, ribs)
    # soleiras dos vaos (no plano da parede)
    for ra, rb in zip(ORDER, ORDER[1:]):
        link_sill(mfd, ROOMS[ra][3], ROOMS[rb][1], next_=(ra == "R2"))
    link_sill(mfd, ROOMS["R3"][3], NICHE_BACK, next_=True, ym=L.dun_next("R3")[1], back=0.0)
    next_portals(mk)
    altar_medallion(mfd, (ROOMS["R3"][0] + ROOMS["R3"][2]) / 2.0, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0)
    for nm, x, y, h, r, nc, inner, m in CHANDELIERS:
        chandelier(mi, x, y, Z + h, vault_hang(nm, ROOMS[nm], y), r=r, n=nc, m=m, inner=inner)
    for m in (mk, mv, mf, mfd, mi, mp):
        m.finish()


def room_lights():
    """5 luzes (10.02: uma cor por sala): portal de chegada (violeta), R1 ambar (entre os 2 lustres), R2 fria (nas 2
    rodas), R3 violeta suave (na coroa). No jogo o export_sg da Range 60 / Brightness 3 (10.11)."""
    y0 = ROOMS["R1"][1]
    light("L_SGDun_R1_Portal", "POINT", (LX, y0 + 7.0, Z + 8.5), 5000.0, (0.64, 0.42, 1.0), 1.5)
    col, e = ROOM_ID["R1"]["light"]
    light("L_SGDun_R1_Chandelier", "POINT", (LX, (ROOMS["R1"][1] + ROOMS["R1"][3]) / 2.0, Z + 20.0), e, col, 1.0)
    col, e = ROOM_ID["R2"]["light"]
    for tag, y in (("S", _R2[1] + 2.0 * _P2), ("N", _R2[1] + 5.0 * _P2)):
        light("L_SGDun_R2_Chandelier%s" % tag, "POINT", (LX, y, Z + 20.8), e, col, 1.0)
    col, e = ROOM_ID["R3"]["light"]
    light("L_SGDun_R3_Chandelier", "POINT", (LX, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0, Z + 19.3), e, col, 1.0)


# ------------------------------------------------------------------ paredes (casca colidivel)
def room_walls():
    """paredes (visual + colisao identicos) com os vaos 28 x 22 e o nicho; piso e teto colidiveis"""
    mb = MB("SG_Dun_Rooms_Shell", "17_DUNGEON", random.Random(741), detail="far", floor=-999)
    zb, zt = Z - 0.6, ZCEIL
    pieces = []
    r1 = ROOMS["R1"]
    pieces.append(((r1[0] - WT, r1[1] - WT), (r1[2] + WT, r1[1])))                       # muro sul da R1
    for nm in ORDER:
        x0, y0, x1, y1 = ROOMS[nm]
        ya = y0 - (WT if nm == "R1" else 0.0)
        pieces += [((x0 - WT, ya), (x0, y1 + WT)), ((x1, ya), (x1 + WT, y1 + WT))]      # muros oeste / leste
    walls_ns = []
    for ra, rb in zip(ORDER, ORDER[1:]):
        a, b = ROOMS[ra], ROOMS[rb]
        walls_ns.append((a[3], b[1], min(a[0], b[0]) - WT, max(a[2], b[2]) + WT))
    r3 = ROOMS["R3"]
    walls_ns.append((r3[3], r3[3] + WT, r3[0] - WT, r3[2] + WT))                         # muro norte (nicho)
    for ya, yb, xa, xb in walls_ns:
        pieces += [((xa, ya), (LX - LINK_HW, yb)), ((LX + LINK_HW, ya), (xb, yb))]
        # ONDA 3 (z-fight): o intradorso da casca sobe 0,08 (a verga de aduelas do kit entra 0,1 no muro com o fundo a
        # 0,02-0,03 dele); a colisao continua na cota do vao
        mb.box2((LX - LINK_HW, ya, Z + LINK_H + 0.08), (LX + LINK_HW, yb, zt), CS, 0.0)
        ccol("SG_DunRoom", (LX - LINK_HW, ya, Z + LINK_H), (LX + LINK_HW, yb, zt))
    for (xa, ya), (xb, yb) in pieces:
        mb.box2((xa, ya, zb), (xb, yb, zt), CS, 0.0)
        ccol("SG_DunRoom", (xa, ya, zb), (xb, yb, zt))
    mb.finish()
    ccol("SG_DunRoom", (BX0, BY0, Z - 2.0), (BX1, BY1, Z))
    ccol("SG_DunRoom", (BX0, BY0, ZCEIL), (BX1, BY1, ZCEIL + 1.5))


MED_HS = 10.5                                    # medalhao do centro da R3 (raio 9,1: placa baixa)


# ------------------------------------------------------------------ cameras e rotas extras do QA
_R1, _R3 = ROOMS["R1"], ROOMS["R3"]
CAMS = {
    # chegada na R1 (o que o grupo ve ao sair do portal) e o fundo com o portal de chegada e a saida
    "CAM_SGDun_R1_Arrival": ((LX + 3.0, _R1[1] + 10.0, Z + 5.4), (LX, _R1[3], Z + 11.0), 18),
    "CAM_SGDun_R1_Back": ((_R1[2] - 12.0, _R1[3] - 10.0, Z + 5.4), (LX - 14.0, _R1[1], Z + 9.0), 18),
    "CAM_SGDun_R2_A": ((LX + 4.0, _R2[1] + 8.0, Z + 5.4), (LX, _R2[3], Z + 11.0), 16),
    "CAM_SGDun_R2_B": ((_R2[2] - 8.0, _R2[3] - 8.0, Z + 5.4), (_R2[0] + 20.0, _R2[1] + 12.0, Z + 11.0), 16),
    "CAM_SGDun_R3_A": ((LX + 4.0, _R3[1] + 8.0, Z + 5.4), (LX, _R3[3], Z + 11.0), 16),
    "CAM_SGDun_R3_B": ((_R3[2] - 10.0, _R3[3] - 8.0, Z + 5.4), (_R3[0], _R3[1] + 14.0, Z + 9.0), 16),
    # portais da proxima sala DE FRENTE (com a parede 27 x 21 x 1 simulada no estudio) e as saidas
    "CAM_SGDun_NextR2_Front": ((LX, _R2[3] - 42.0, Z + 12.0), (LX, _R2[3], Z + 16.5), 20),
    "CAM_SGDun_NextR3_Front": ((LX, _R3[3] - 42.0, Z + 12.0), (LX, _R3[3], Z + 16.5), 20),
    "CAM_SGDun_ExitR1": ((EXIT_S["R1"] + 3.0, _R1[1] + 20.0, Z + 5.4), (EXIT_S["R1"], _R1[1], Z + 5.0), 22),
    "CAM_SGDun_ExitR3": ((_R3[0] + 20.0, EXIT_S["R3"] + 5.0, Z + 5.4), (_R3[0], EXIT_S["R3"], Z + 5.0), 22),
    # closes de acabamento
    "CAM_SGDun_Torch": ((_R2[0] + 8.0, _R2[1] + 22.0, Z + 9.0), (_R2[0], _R2[1] + 14.86, Z + 10.5), 26),
    "CAM_SGDun_Retable": ((_R3[2] - 16.0, 250.0, Z + 5.4), (_R3[2], 250.0, Z + 6.0), 22),
    "CAM_SGDun_SpawnR1": ((LX + 9.0, _R1[1] + 27.0, Z + 7.0), (LX, _R1[1] + 9.0, Z + 2.0), 22),
    # FINESSE 3: as cameras da AUDITORIA3 (secao 10; o studio nao as cria) + abobadas de cada sala (olho a 5,5)
    "CAM_A3_10_R1_Chegada": ((3.0, 16.0, Z + 5.5), (0.0, 90.0, Z + 11.0), 18),
    "CAM_A3_10_R1_Fundo": ((30.0, 80.0, Z + 5.5), (-14.0, 6.0, Z + 9.0), 18),
    "CAM_A3_10_R1_Saida": ((-26.0, 26.0, Z + 5.5), (-30.0, 6.0, Z + 5.0), 20),
    "CAM_A3_10_Vao_R1R2": ((2.0, 78.0, Z + 5.5), (0.0, 104.0, Z + 10.0), 18),
    "CAM_A3_10_R2_Entrada": ((4.0, 100.0, Z + 5.5), (0.0, 196.0, Z + 11.0), 18),
    "CAM_A3_10_R2_Diagonal": ((44.0, 188.0, Z + 5.5), (-32.0, 104.0, Z + 11.0), 18),
    "CAM_A3_10_R2_Portal": ((0.0, 160.0, Z + 5.5), (0.0, 196.0, Z + 12.0), 18),
    "CAM_A3_10_R2_Parede": ((-38.0, 140.0, Z + 5.5), (-52.0, 150.0, Z + 10.0), 20),
    "CAM_A3_10_R3_Entrada": ((4.0, 206.0, Z + 5.5), (0.0, 302.0, Z + 11.0), 18),
    "CAM_A3_10_R3_Diagonal": ((42.0, 294.0, Z + 5.5), (-52.0, 212.0, Z + 9.0), 18),
    "CAM_A3_10_R3_Portal": ((0.0, 266.0, Z + 5.5), (0.0, 303.0, Z + 12.0), 18),
    "CAM_A3_10_R3_Retabulo": ((36.0, 250.0, Z + 5.5), (52.0, 250.0, Z + 6.0), 20),
    "CAM_A3_10_R3_Teto": ((0.0, 250.0, Z + 5.5), (0.0, 262.0, Z + 44.0), 14),
    "CAM_A3_10_R1_Teto": ((-10.0, 30.0, Z + 5.5), (6.0, 62.0, Z + 40.0), 16),
    "CAM_A3_10_R2_Teto": ((-20.0, 120.0, Z + 5.5), (10.0, 160.0, Z + 40.0), 16),
}


def _loop(r, d=5.0):
    x0, y0, x1, y1 = r
    return [(x0 + d, y0 + d), (x1 - d, y0 + d), (x1 - d, y1 - d), (x0 + d, y1 - d), (x0 + d, y0 + d)]


EXTRA_ROUTES = {
    "SALA_R1_VOLTA": (_loop(ROOMS["R1"]), Z),
    "SALA_R2_VOLTA": (_loop(ROOMS["R2"]), Z),
    "SALA_R3_VOLTA": (_loop(ROOMS["R3"]), Z),
    # grupo: 2 linhas a +-10 do eixo nos vaos de 28
    "GRUPO_VAO_R1R2": ([(LX - 10.0, _R1[3] - 6.0), (LX - 10.0, _R2[1] + 6.0), (LX + 10.0, _R2[1] + 6.0),
                        (LX + 10.0, _R1[3] - 6.0)], Z),
    "GRUPO_VAO_R2R3": ([(LX - 10.0, _R2[3] - 6.0), (LX - 10.0, _R3[1] + 6.0), (LX + 10.0, _R3[1] + 6.0),
                        (LX + 10.0, _R2[3] - 6.0)], Z),
    "SPAWN_R1_ATE_SAIDA": ([L.dun_spawn("R1"), (EXIT_S["R1"], _R1[1] + 6.0)], Z),
    "SPAWN_R3_ATE_SAIDA": ([L.dun_spawn("R3"), (_R3[0] + 8.0, L.dun_exit("R3")[1])], Z),
    "SALA_R3_ATE_O_NICHO": ([(LX, _R3[3] - 20.0), (LX, _R3[3] + 0.5)], Z),
}
EXTRA_PROBES = []


def build():
    _SKIP.clear()
    room_walls()
    room_kit()
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
    fit_check()


def fit_check():
    """prova numerica: a parede de energia do jogo (w x h x t no CFrame do marcador DUN_NEXT_*) cabe no vao livre e nao
    encosta em nenhuma peca da dungeon (malhas SG_Dun_* e colisoes COL_SG_Dun*)"""
    from mathutils.bvhtree import BVHTree
    for nm in ("R2", "R3"):
        nx, ny = L.dun_next(nm)
        p0 = (nx - NEXT_W / 2, ny - NEXT_T / 2, Z + 0.01)
        p1 = (nx + NEXT_W / 2, ny + NEXT_T / 2, Z + NEXT_H)
        hits = []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith(("SG_Dun_", "COL_SG_Dun", "COL_SGDun")):
                continue
            if o.name.startswith("SG_Dun_R3_ExitSpiral"):
                continue
            mw = o.matrix_world
            vs = [mw @ v.co for v in o.data.vertices]
            if not vs:
                continue
            if (max(v.x for v in vs) < p0[0] or min(v.x for v in vs) > p1[0] or max(v.y for v in vs) < p0[1] or
                    min(v.y for v in vs) > p1[1] or max(v.z for v in vs) < p0[2] or min(v.z for v in vs) > p1[2]):
                continue
            inside = any(p0[0] < v.x < p1[0] and p0[1] < v.y < p1[1] and p0[2] < v.z < p1[2] for v in vs)
            t = BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons])
            bx = [(p0[0], p0[1], p0[2]), (p1[0], p0[1], p0[2]), (p1[0], p1[1], p0[2]), (p0[0], p1[1], p0[2]),
                  (p0[0], p0[1], p1[2]), (p1[0], p0[1], p1[2]), (p1[0], p1[1], p1[2]), (p0[0], p1[1], p1[2])]
            bf = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
            if inside or t.overlap(BVHTree.FromPolygons(bx, bf)):
                hits.append(o.name)
        print(("OK   " if not hits else "FAIL ") + "DUN_NEXT_%s parede %gx%gx%g no vao (%.1f, %.1f): %s" % (
            nm, NEXT_W, NEXT_H, NEXT_T, nx, ny, "livre (folga 0,5 nos lados, %.1f em cima)" % (LINK_H - NEXT_H)
            if not hits else "ENCOSTA em %s" % hits[:6]))
