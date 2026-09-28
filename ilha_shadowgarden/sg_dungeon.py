# sg_dungeon - ZONA DUNGEON da Ilha 3 (Shadow Garden). build() substitui sg_blockout.dungeon (inclusive as colisoes e as
# luzes dela). Prefixo SG_Dun_, colecao 17_DUNGEON, VFX_SGDUN_* em 12_VFX_HELPERS. A dungeon e a "corrida de mineracao"
# periodica do jogo (XX:00 / XX:30): o jogador entra pelo PORTAL da portaria (superficie, P3) e o jogo o leva para as 3
# SALAS modulares escondidas dentro da rocha (piso DUN_Z 6,0; teto DUN_CEIL 28); minera nos DUN_ORE_* e sai pelo portal
# de saida da R3. O sistema e do jogo: aqui so o LUGAR. NAO modela minerio.
#   1. PORTARIA (DUNGEON_HOUSE 26x26 em (100, 72), P3 52,2): torre gotica escura com 4 torrinhas de canto de agulha navy,
#      cornija com misulas + ameias, agulha central navy com 4 lucarnas quentes, contrafortes e lancetas quentes no andar
#      alto; fachada SUL com o portal: vao ogival 10 x 14, 3 arquivoltas escalonadas, wimperg com a estrela de prata e 2
#      pinaculos. Interior 20 x 20 entravel (pe-direito 21,6 sob a abobada): PORTAL ESPIRAL no fundo (anel de pedra com
#      runas de prata + disco violeta; a espiral gira = VFX_SGDUN_Portal), nicho ogival, 2 GUARDIOES encapuzados com
#      espada (genericos), estrado de 2 degraus (0,4 + 0,8 - colisao casada), 2 braseiros, tochas, abobada com nervuras.
#   2. SALAS (R1 chegada 36 x 36, R2 mineracao 44 x 44, R3 camara final 44 x 44) com o MESMO kit: parede com pilastras
#      e arcos ogivais cegos, colunas de canto, cornija de arranque, tochas de parede, piso de lajes escuras com friso,
#      abobada ogival de bercos com nervuras e bossas. Vaos de ligacao 12 x 12 (verga + timpano ogival com a estrela).
#      Variacao: R1 portal de chegada (parede oeste, aceso); R2 salao largo com arcada dupla nas paredes N/S e 2 lustres;
#      R3 portal de saida (parede leste; a espiral e objeto proprio SG_Dun_R3_ExitSpiral que o jogo liga em FINISHING),
#      altar = medalhao embutido no piso sob o DUN_ORE_R3_SUPERLEGENDARY + lustre-coroa em cima.
#   3. COLISAO propria (caixas): piso, paredes com os vaos, teto (opaco) das salas; paredes com o vao da porta (+ cantos
#      da ogiva), teto interno, torrinhas, pinaculos, portal, estrado, estatuas e braseiros da portaria. Nada colidivel a
#      menos de 5 dos DUN_ORE_* ate piso+12 (conferido em ccol()).
#   4. Luzes (6): portaria = portal violeta + braseiro quente; salas = portal de chegada (violeta) + 2 lustres da R2 + lustre
#      da R3 (quentes).
import math, random
import bpy
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box2, light
import fm_lib
import sg_layout as L

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
}

EXTRA_ROUTES = {
    "PORTARIA_ATE_O_PORTAL": ([(100.0, 50.0), (100.0, 60.0), (100.0, 70.0), (100.0, 73.6), (100.0, 76.5)], P3),
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


def star(mb, F, cs, ch, r, d0, d1, m, pts=8):
    """estrela de prata do Shadow Garden (8 pontas) no plano da parede"""
    ring = []
    for k in range(pts * 2):
        rr = r if k % 2 == 0 else r * 0.42
        a = math.pi / 2 + k * math.pi / pts
        ring.append((cs + rr * math.cos(a), ch + rr * math.sin(a)))
    for k in range(pts * 2):
        slab(mb, F, [(cs, ch), ring[k], ring[(k + 1) % (pts * 2)]], d0, d1, m)


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
    """moldura do vao de ligacao 12 x 12: verga clara + timpano ogival navy com a estrela de prata"""
    fbox(mb, F, cs - hw_open - 1.3, cs + hw_open + 1.3, 0.0, 0.8, LINK_H, LINK_H + 1.2, TR, 0.06)
    th = hw_open + 0.6
    arch_panel(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.0, 0.15, VA)
    arch_band(mb, F, cs, th, 5.0, LINK_H + 1.2, LINK_H + 1.2, 0.7, 0.0, 0.6, TR)
    star(mb, F, cs, LINK_H + 3.4, 1.3, 0.15, 0.3, SV)


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
    mb.cyl(0.85, 1.05, (x, y, z + 3.85 + 0.52), m=GL, n=8, r2=0.18, bevel=0.0)          # chama baixa (brasa viva)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        mb.beam((x + 0.5 * math.cos(a), y + 0.5 * math.sin(a), z + 2.9),
                (x + 1.25 * math.cos(a), y + 1.25 * math.sin(a), z + 3.9), 0.2, 0.2, IR, 0.0)


def wall_lantern(mb, F, s, d, h):
    """lanterna de ferro pendurada numa mao-francesa (marca a porta)"""
    mb.beam(F.p(s, d, h + 0.2), F.p(s, d + 1.6, h + 1.2), 0.2, 0.2, IR, 0.0)
    mb.beam(F.p(s, d, h - 0.6), F.p(s, d + 1.0, h + 0.9), 0.2, 0.2, IR, 0.0)
    c = F.p(s, d + 1.6, h)
    mb.box((0.62, 0.62, 1.0), (c[0], c[1], c[2]), (0, 0, 0), GL, 0.0)
    for a in (0.25, 1.82, 3.39, 4.96):
        mb.box((0.2, 0.2, 1.2), (c[0] + 0.4 * math.cos(a + 0.54), c[1] + 0.4 * math.sin(a + 0.54), c[2]), (0, 0, 0), IR, 0.0)
    mb.box((0.95, 0.95, 0.22), (c[0], c[1], c[2] - 0.6), (0, 0, 0), IR, 0.0)
    SL.spire(mb, (c[0], c[1]), 0.72, c[2] + 0.55, 0.65, IR, n=4)


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
    """corpo externo: paredes (vao ogival da porta), plinto, cintas, misulas, cornija, ameias, torrinhas de canto,
    contrafortes, lancetas quentes, portal com arquivoltas + wimperg, agulha central com lucarnas"""
    mb = MB("SG_Dun_House_Body", "17_DUNGEON", random.Random(701), detail="near")
    FS, FN = Face(True, HY0, -1, P3), Face(True, HY1, 1, P3)
    FW, FE = Face(False, HX0, -1, P3), Face(False, HX1, 1, P3)
    # paredes (a de sul com o vao ogival 10 x 14)
    wall_ogive_opening(mb, FS, HX0, HX1, HX, DW / 2, D_SPR, D_RISE, BODY, -HT, 0.0, CS)
    fbox(mb, FN, HX0, HX1, -HT, 0.0, -0.5, BODY, CS)
    fbox(mb, FW, IY0, IY1, -HT, 0.0, -0.5, BODY, CS)
    fbox(mb, FE, IY0, IY1, -HT, 0.0, -0.5, BODY, CS)
    # plinto, cinta (h 16) e cornija com misulas em todas as faces
    for F, (a, b) in ((FS, (HX0, HX1)), (FN, (HX0, HX1)), (FW, (HY0, HY1)), (FE, (HY0, HY1))):
        if F is FS:
            for s0, s1 in ((a, HX - DW / 2 - 2.2), (HX + DW / 2 + 2.2, b)):
                fbox(mb, F, s0, s1, 0.0, 0.5, -0.5, 1.3, BL, 0.08)
            for s0, s1 in ((a, 90.4), (109.6, b)):
                fbox(mb, F, s0, s1, 0.0, 0.5, 15.6, 16.4, TR, 0.05)
        else:
            fbox(mb, F, a, b, 0.0, 0.5, -0.5, 1.3, BL, 0.08)
            fbox(mb, F, a, b, 0.0, 0.5, 15.6, 16.4, TR, 0.05)
        fbox(mb, F, a + 3.0, b - 3.0, 0.0, 0.9, 33.0, 34.2, TR, 0.08)
        s = a + 4.0
        while s <= b - 3.9:
            fbox(mb, F, s - 0.45, s + 0.45, 0.0, 0.75, 31.4, 33.0, TR, 0.05)
            s += 2.7
        # parapeito + ameias
        fbox(mb, F, a + 3.2, b - 3.2, -0.4, 0.9, 34.2, 35.6, CS, 0.05)
        s = a + 4.6
        while s <= b - 4.2:
            fbox(mb, F, s - 0.7, s + 0.7, -0.4, 0.9, 35.6, 37.4, CS, 0.08)
            s += 2.8
    # contrafortes (meio das faces leste, oeste e norte) e lancetas quentes do andar alto
    for F, c in ((FE, HY), (FW, HY), (FN, HX)):
        fbox(mb, F, c - 1.6, c + 1.6, 0.0, 1.4, -0.5, 16.4, CS, 0.08)
        fbox(mb, F, c - 1.8, c + 1.8, 0.0, 1.6, 16.0, 16.8, TR, 0.06)
        fbox(mb, F, c - 1.25, c + 1.25, 0.0, 0.9, 16.8, 31.4, CS, 0.08)
        for k in (-1, 1):
            cs = c + k * 5.0
            arch_panel(mb, F, cs, 1.3, 2.6, 26.6, 20.0, 0.0, 0.12, WW)
            arch_band(mb, F, cs, 1.3, 2.6, 26.6, 20.0, 0.45, 0.0, 0.45, TR)
            fbox(mb, F, cs - 2.0, cs + 2.0, 0.0, 0.7, 19.5, 20.0, TR, 0.05)
            # arcada cega baixa (quebra a massa ao nivel do jogador, 360 graus)
            arch_panel(mb, F, cs + k * 1.5, 2.8, 3.0, 8.4, 1.3, 0.0, 0.12, VA)
            arch_band(mb, F, cs + k * 1.5, 2.8, 3.0, 8.4, 1.3, 0.5, 0.0, 0.45, TR)
    # fachada sul: oculo quente no alto
    slab(mb, FS, [(HX + 1.7 * math.cos(2 * math.pi * k / 14), 29.4 + 1.7 * math.sin(2 * math.pi * k / 14))
                  for k in range(14)], 0.0, 0.12, WW)
    band(mb, FS, [(HX + 1.7 * math.cos(2 * math.pi * k / 14), 29.4 + 1.7 * math.sin(2 * math.pi * k / 14))
                  for k in range(14)],
         [(HX + 2.4 * math.cos(2 * math.pi * k / 14), 29.4 + 2.4 * math.sin(2 * math.pi * k / 14)) for k in range(14)],
         0.0, 0.5, TR, closed=True)
    # portal: 3 arquivoltas escalonadas ate o chao (ombreiras), wimperg com a estrela, 2 pinaculos
    for i, (t, dep) in enumerate(((0.6, 0.5), (0.6, 0.95), (0.7, 1.4))):
        hw = DW / 2 + sum(x[0] for x in ((0.6, 0), (0.6, 0), (0.7, 0))[:i])
        arch_band(mb, FS, HX, hw, D_RISE + (hw - DW / 2), D_SPR, 0.0, t, 0.0, dep, TR if i != 1 else CS, n=7)
    g0, g1, gh0, gh1 = HX - 7.4, HX + 7.4, 15.9, 25.6
    tri_prism(mb, FS, [(g0, gh0), (g1, gh0), (HX, gh1)], 0.0, 0.9, TR)
    tri_prism(mb, FS, [(g0 + 1.6, gh0 + 0.8), (g1 - 1.6, gh0 + 0.8), (HX, gh1 - 1.9)], 0.9, 1.05, CS)
    star(mb, FS, HX, 19.4, 1.7, 1.05, 1.25, SV)
    for s in (HX - 8.7, HX + 8.7):
        fbox(mb, FS, s - 0.8, s + 0.8, 0.0, 1.6, -0.5, 22.0, CS, 0.08)
        fbox(mb, FS, s - 1.0, s + 1.0, 0.0, 1.8, 22.0, 22.7, TR, 0.06)
        c = FS.p(s, 0.8, 22.7)
        SL.spire(mb, (c[0], c[1]), 1.3, c[2], 4.6, NAVY, n=4)
        ccol("SG_DunHouse", FS.p(s - 0.8, 0.0, -0.5), FS.p(s + 0.8, 1.6, 22.0))
    # torrinhas de canto
    for cx, cy in ((HX0, HY0), (HX1, HY0), (HX0, HY1), (HX1, HY1)):
        mb.cyl(TURRET_R, 40.5, (cx, cy, P3 + 19.75), m=CS, n=8, bevel=0.0)
        for h0, h1, r in ((-0.5, 1.3, TURRET_R + 0.4), (15.6, 16.4, TURRET_R + 0.3), (33.0, 34.2, TURRET_R + 0.4),
                          (39.4, 40.6, TURRET_R + 0.6)):
            mb.cyl(r, h1 - h0, (cx, cy, P3 + (h0 + h1) / 2), m=TR if h0 > 0 else BL, n=8, bevel=0.0)
        SL.spire(mb, (cx, cy), TURRET_R + 0.9, P3 + 40.6, 14.0, NAVY, n=8)
        mb.rod((cx, cy, P3 + 54.2), (cx, cy, P3 + 56.8), 0.14, SV, 6)
        # seteira escura voltada para fora (diagonal)
        a = math.atan2(cy - HY, cx - HX)
        for h in (10.0, 24.0):
            mb.box((0.35, 0.6, 2.4), (cx + math.cos(a) * (TURRET_R - 0.1), cy + math.sin(a) * (TURRET_R - 0.1), P3 + h),
                   (0, 0, a), NAVY, 0.0)
        col_box2("SG_DunHouse", (cx - TURRET_R, cy - TURRET_R, P3 - 0.5), (cx + TURRET_R, cy + TURRET_R, P3 + 40.6))
    # cobertura: laje de ardosia, agulha central navy e lucarnas quentes
    mb.box2((HX0 + 0.6, HY0 + 0.6, P3 + 33.6), (HX1 - 0.6, HY1 - 0.6, P3 + 34.2), NAVY, 0.0)
    hs, zb, sh = 9.0, P3 + 34.2, 30.0
    mb.box2((HX - hs - 0.4, HY - hs - 0.4, zb), (HX + hs + 0.4, HY + hs + 0.4, zb + 0.8), CS, 0.05)
    SL.spire(mb, (HX, HY), hs * math.sqrt(2.0), zb + 0.8, sh, NAVY, n=4)
    mb.rod((HX, HY, zb + 0.8 + sh - 0.5), (HX, HY, zb + sh + 5.0), 0.2, SV, 6)
    mb.box((0.9, 0.9, 0.9), (HX, HY, zb + sh + 3.2), (0.6, 0.6, 0.0), SV, 0.0)
    for F, c in ((FS, HX), (FN, HX), (FW, HY), (FE, HY)):
        h0 = 6.2
        hsx = hs * (1.0 - (h0 + 0.8 - 1.0) / sh)        # meia-largura da agulha na base da lucarna
        dfront = hsx - HW / 2 + 0.6                       # d (para fora da face da torre) da frente da lucarna
        fbox(mb, F, c - 1.7, c + 1.7, dfront - 3.5, dfront, BODY + h0, BODY + h0 + 3.6, CS, 0.05)
        tri_prism(mb, F, [(c - 2.2, BODY + h0 + 3.6), (c + 2.2, BODY + h0 + 3.6), (c, BODY + h0 + 6.0)],
                  dfront - 3.5, dfront + 0.3, NAVY)
        fbox(mb, F, c - 0.75, c + 0.75, dfront, dfront + 0.1, BODY + h0 + 0.6, BODY + h0 + 2.9, WW, 0.0)
    mb.finish()
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
    # guardioes, braseiros e as lanternas da porta (lado de fora) no mesmo objeto: mesmos materiais
    house_props(mb)
    FSo = Face(True, HY0, -1, P3)
    for s in (HX - 6.9, HX + 6.9):
        wall_lantern(mb, FSo, s, 1.4, 7.6)
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
    # raios da estrela (8) no campo navy: tiras de cantaria embutidas (mesmo topo)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        p0 = (cx + 3.4 * math.cos(a), cy + 3.4 * math.sin(a))
        p1 = (cx + 6.8 * math.cos(a), cy + 6.8 * math.sin(a))
        mb.beam((p0[0], p0[1], zt - 0.19), (p1[0], p1[1], zt - 0.19), 0.45, 0.4, TR, 0.0)


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
    room_walls()
    room_kit()
    room_portals()
    room_lights()
    if _SKIP:
        print("DUN AVISO colisoes omitidas por folga de minerio (so visual):", _SKIP)
    else:
        print("DUN folga dos minerios: OK (nenhuma colisao a menos de 5 de DUN_ORE_* ate piso+12)")
