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
import math, random
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
    "Stone_SGDunVault": (S(34, 38, 62), 0.8, 0.0, 0, None, 0.06),      # navy escuro: abobadas, campos das arcadas
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
    fm_lib.TEX_RULES = (("Stone_SGDunVault", None),) + tuple(fm_lib.TEX_RULES)
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
    EM._lathe(mb, (x, y, z0 + h0), [(r + 0.24, 0.0), (r + 0.24, 0.16), (r + 0.1, 0.32), (r + 0.02, 0.5)],
              TRL, n, ph, caps=(False, True))
    # F11: o fuste entra so 0,13 no colar do capitel (o colar fica 0,16 fora do fuste; antes o fuste subia 0,5 dentro
    # do capitel a 0,1 da face)
    EM._lathe(mb, (x, y, z0 + h0 + 0.5), [(r, 0.0), (r, h1 - h0 - (1.42 if cap else 0.5))], CS, n, ph,
              caps=(False, False))
    if cap:
        EM._lathe(mb, (x, y, z0 + h1 - 1.05), [(r + 0.16, 0.0), (r + 0.16, 0.14), (r + 0.04, 0.45),
                                                (r + 0.3, 0.85)], TRL, n, ph, caps=(False, True))
        a = r + 0.38                                                                    # abaco sobre o sino
        fblock(mb, F, s - a, s + a, d - a, d + a, h1 - 0.2, h1, TRL, 0.0)


def pilaster(mb, F, s, top, area=None, twin=False, altar=False, mi=None):
    """pilastra (09.10): soco de obsidiana chanfrado em talude, fuste de cantaria chanfrado, COLUNELO engastado
    (twin = colunelos DUPLOS: R3), capitel moldurado onde a nervura nasce; altar = a pilastra do eixo da R3 vira
    RETABULO (mesa de altar + painel ogival + misula que continua carregando a nervura)"""
    W = PIL_HW
    if altar:
        altar_retable(mb, F, s, top, mi or mb)
        if area:
            fcol(area, F, s - W - 0.3, s + W + 0.3, 0.0, PIL_D + 0.3, -0.5, top)
        return
    fblock(mb, F, s - W - 0.35, s + W + 0.35, -0.2, PIL_D + 0.45, -0.1, 0.7, OB, 0.0)     # v4: soco reto (o talude chanfra)
    fplinth(mb, F, s - W - 0.35, s + W + 0.35, PIL_D + 0.45, 0.7, 1.0, 0.25, OB)
    fblock(mb, F, s - W, s + W, -0.2, PIL_D, 1.0, top - 1.3, CS, 0.1)
    for sc in ((s - 0.54, s + 0.54) if twin else (s,)):
        colonette(mb, F, sc, PIL_D + 0.08, 1.0, top - 1.3, COL_R * (0.78 if twin else 1.0), n=6 if twin else 8)
    fledge(mb, F, s - W - 0.3, s + W + 0.3, [(-0.2, top - 1.3), (PIL_D + 0.3, top - 1.3), (PIL_D + 0.62, top - 0.62),
                                             (PIL_D + 0.66, top - 0.36), (PIL_D + 0.66, top), (-0.2, top)], TRL)
    if area:
        fcol(area, F, s - W - 0.3, s + W + 0.3, 0.0, PIL_D + 0.3, -0.5, top)


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
    fblock(mb, F, a2, b2, -0.2, 2.75, -0.1, 0.7, OB, 0.1)
    fblock(mb, F, a, b, -0.2, 2.4, 0.7, top - 1.3, CS, 0.1)
    colonette(mb, F, s + sgn * 2.4, 2.4, 0.7, top - 1.3, 0.5)
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


def grille(mb, mi, F, cs, h0, h1, hw):
    """GRELHA de ferro (R2): soleira e verga de remate, 5 barras redondas e 2 travessas chatas, chumbadas na pedra"""
    fblock(mb, F, cs - hw - 0.35, cs + hw + 0.35, 0.0, 0.5, h0 - 0.35, h0, TRL, 0.06)
    fblock(mb, F, cs - hw - 0.35, cs + hw + 0.35, 0.0, 0.5, h1, h1 + 0.35, TRL, 0.06)
    for i in range(5):
        p = F.v(cs - hw + 2 * hw * (i + 0.5) / 5, 0.28, 0.0)
        mi.rod((p.x, p.y, p.z + h0 - 0.1), (p.x, p.y, p.z + h1 + 0.1), 0.075, BI, 6)
    for hh in (h0 + (h1 - h0) * 0.3, h0 + (h1 - h0) * 0.72):
        fblock(mi, F, cs - hw - 0.05, cs + hw + 0.05, 0.18, 0.4, hh - 0.09, hh + 0.09, BI, 0.0)


def shoring(mb, F, cs, hw, spring):
    """ESCORA de madeira de mina (R2): 2 esteios, chapeu com cunhas, 2 maos-francesas e grampos de ferro, encostada
    na arcada cega (so visual, a menos de 1,3 da parede)"""
    hp = 0.28
    zt = spring + 0.35
    for sg in (-1, 1):
        sp = cs + sg * (hw + 0.2)
        fblock(mb, F, sp - hp, sp + hp, 0.6, 1.16, -0.02, zt, WD, 0.0)
        fblock(mb, F, sp - hp - 0.14, sp + hp + 0.14, 0.46, 1.3, zt - 1.05, zt - 0.85, BI, 0.0)        # grampo (F11)
        a = F.v(sp - sg * 0.2, 0.88, zt - 1.7)
        b = F.v(sp - sg * 1.5, 0.88, zt - 0.15)
        mb.beam(a, b, 0.34, 0.34, WD, 0.05)
    fblock(mb, F, cs - hw - 0.75, cs + hw + 0.75, 0.55, 1.21, zt, zt + 0.62, WD, 0.0)                 # chapeu
    for sg in (-1, 1):                                                                              # cunhas
        fblock(mb, F, cs + sg * (hw * 0.5) - 0.35, cs + sg * (hw * 0.5) + 0.35, 0.6, 1.15, zt + 0.62, zt + 0.84,
               WD, 0.0)


def _arch_geo(s0, s1, spring, lancet=False):
    """(meia-largura, flecha, arranque) da arcada cega: a ogiva mantem a proporcao e o ARRANQUE desce se preciso para
    a chave ficar 0,1 abaixo da cornija (nada atravessa a cornija). lancet (R1): ogiva mais aguda"""
    hw = (s1 - s0) / 2.0 - 0.8
    rise = min(hw * (1.7 if lancet else 1.15), 6.0)
    return hw, rise, min(spring, R_SPR - 0.88 - 1.02 - rise)


def blind_arch(mb, F, s0, s1, spring=7.0, twin=False, room="R1", mi=None, skirt=True):
    """arcada CEGA (09.10): campo navy rebaixado, ombreiras de cantaria, impostas de remate, arquivolta de 2 ORDENS
    (a interna em cantaria, a externa em remate) com chave; twin = arcada dupla sobre colunelo central.
    R2: grelha de ferro nos arcos da arcada dupla e escoras de mina nos arcos simples."""
    mi = mi or mb
    if skirt:
        skirting(mb, F, s0, s1)
    if twin:
        mid = (s0 + s1) / 2.0
        blind_arch(mb, F, s0, mid + 0.35, spring, False, room + "_twin", mi, False)
        blind_arch(mb, F, mid - 0.35, s1, spring, False, room + "_twin", mi, False)
        colonette(mb, F, mid, 0.45, 0.78, _arch_geo(s0, mid + 0.35, spring, room.startswith("R1"))[2], 0.34, n=6,
                  rot=0.0 if F.hz else math.pi / 2)   # F11: vertice (nao face) virado para as ombreiras
        return
    cs = (s0 + s1) / 2.0
    hw, rise, spring = _arch_geo(s0, s1, spring, room.startswith("R1"))
    if hw < 1.2:
        return
    arch_panel(mb, F, cs, hw, rise, spring, 0.78, 0.0, 0.15, VA, 4)
    for sg in (-1, 1):
        a, b = sorted((cs + sg * hw, cs + sg * (hw + 0.42)))
        fblock(mb, F, a, b, -0.1, 0.34, 0.78, spring - 0.34, CS, 0.0)                     # ombreira (recuada)
        a, b = sorted((cs + sg * (hw - 0.06), cs + sg * (hw + 0.62)))
        fledge(mb, F, a, b, [(-0.1, spring - 0.34), (0.42, spring - 0.34), (0.56, spring - 0.12), (0.56, spring),
                             (-0.1, spring)], TRL)                                          # imposta
    ogee_band(mb, F, cs, hw, rise, spring, 0.4, -0.1, 0.34, CS, 4)
    if room != "R1_twin":                         # v4: as lancetas geminadas da R1 ficam com 1 ordem (orcamento)
        ogee_band(mb, F, cs, hw + 0.4, rise + 0.4, spring, 0.42, -0.1, 0.52, TRL, 4)
    kz = spring + rise + 0.4
    fblock(mb, F, cs - 0.34, cs + 0.34, -0.1, 0.62, kz - 0.25, kz + 0.62, TRL, 0.0)        # chave
    if room == "R2_twin":
        grille(mb, mi, F, cs, 1.7, spring - 0.9, min(2.0, hw - 0.6))
    elif room == "R2":
        shoring(mi, F, cs, hw, spring)


def cornice(mb, F, s0, s1, h):
    """cornija de remate com perfil (face, gola e aba), no arranque da abobada"""
    if s1 - s0 > 0.3:
        fledge(mb, F, s0, s1, [(-0.1, h - 0.78), (0.22, h - 0.78), (0.62, h - 0.3), (0.72, h - 0.3), (0.72, h),
                               (-0.1, h)], TRL)


def torch(mb, F, s, d, h, twin=False):
    """tocha de FERRO (09.11/12.09): BRACADEIRA em volta do colunelo (ou chapa entre os colunelos duplos), braco com
    argola, cabo de madeira inclinado, cesto de 4 hastes curvas com trapo escuro e chama PEQUENA em gota (so ela
    emite). d = face da frente do colunelo; h = altura da chama"""
    n, u = F.n(), F.u()
    cc = F.v(s, PIL_D + 0.08, 0.0)
    zc = F.p(s, 0, h - 1.75)[2]
    if twin:
        p = F.v(s, PIL_D, h - 1.75)
        obox3(mb, p + n * 0.08, u, n, UPZ, 0.34, 0.16, 0.9, BI)                         # chapa (F11: 0,16)
        root = p + n * 0.16
    else:
        EM._lathe(mb, (cc.x, cc.y, zc - 0.14), [(COL_R + 0.14, 0.0), (COL_R + 0.14, 0.28)], BI, 8, math.pi / 8)
        root = Vector((cc.x, cc.y, zc)) + n * (COL_R + 0.14)      # F11: bracadeira 0,14 fora do fuste
    tip = root + n * 0.55 + UPZ * 0.28
    obox3(mb, (root + tip) / 2, (tip - root).normalized(), u, (tip - root).normalized().cross(u).normalized(),
          (tip - root).length + 0.06, 0.13, 0.13, BI)
    ax = (UPZ * 0.94 + n * 0.34).normalized()                                            # tocha inclinada para fora
    ring_c = tip + n * 0.14
    EM._lathe(mb, (ring_c.x, ring_c.y, ring_c.z - 0.09), [(0.19, 0.0), (0.19, 0.18)], BI, 8, 0.0, caps=(False, False))
    bot = ring_c - ax * 0.75
    lathe_ax(mb, bot, ax, [(0.07, 0.0), (0.12, 0.95), (0.14, 1.3)], WD, 6)
    top = bot + ax * 1.3
    lathe_ax(mb, top - ax * 0.05, ax, [(0.13, 0.0), (0.2, 0.12), (0.23, 0.3), (0.16, 0.42)], "Cloth_SG_Navy", 6)
    e1 = ax.cross(u).normalized()
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        rv = (u * math.cos(a) + e1 * math.sin(a))
        pts = [top + ax * 0.02 + rv * 0.12, top + ax * 0.24 + rv * 0.31, top + ax * 0.54 + rv * 0.24]
        mb.tube(pts, 0.035, BI, 3)
    EM._lathe(mb, (top.x + ax.x * 0.36, top.y + ax.y * 0.36, top.z + ax.z * 0.36),
              [(0.0, 0.0), (0.13, 0.11), (0.085, 0.28), (0.0, 0.47)], GL, 6)



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


def vault(mb, rect, axis, zf, spring, crown, ribs=(), nseg=18, liernes=()):
    """berco ogival (arranque 'spring', fecho 'crown' acima de zf) ao longo de 'axis'; NERVURAS em perfil de PERA
    (redondo por baixo: 09.10) nas pilastras, nervuras de testa e cumeeira; chaves em ROSETA de torno"""
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
    def pear5(w, dep):                            # perfil em PERA de 5 pontos (redondo por baixo, leve)
        h = w / 2.0
        return [(-h, 0.12), (h, 0.12), (h * 0.82, -dep * 0.52), (0.0, -dep), (-h * 0.82, -dep * 0.52)]
    prof = pear5(0.9, 0.85)
    prof_w = pear5(0.7, 0.62)
    ue = [-hw + 0.3 + (2 * hw - 0.6) * (0.5 - 0.5 * math.cos(math.pi * k / 14)) for k in range(15)]

    def rib(a, pr):
        mb.sweep([(*mp(a, u), zz(u) - 0.02) for u in ue], pr, TRL)
    for a in ribs:
        rib(a, prof)
    rib(a0 + 0.4, prof_w)
    rib(a1 - 0.4, prof_w)
    mb.sweep([(*mp(a0 + 0.4, 0.0), zz(0.0) - 0.02), (*mp(a1 - 0.4, 0.0), zz(0.0) - 0.02)], prof, TRL)
    for f in liernes:                              # v4: LIERNES longitudinais (a abobada de 104 ganha trama)
        for sg in (-1, 1):
            u = sg * hw * f
            mb.sweep([(*mp(a0 + 0.4, u), zz(u) - 0.02), (*mp(a1 - 0.4, u), zz(u) - 0.02)], prof_w, TRL)
    for a in ribs:
        x, y = mp(a, 0.0)
        EM._lathe(mb, (x, y, zz(0.0) - 0.9), [(0.0, -0.05), (0.36, 0.0), (0.78, 0.28), (1.02, 0.6), (0.9, 0.88)],
                  TRL, 8, math.pi / 8, caps=(False, True))


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
            rune(mb, c + radial * (r_in + 0.47) + n * 0.72, tang, radial, n, k // 2, 0.78, VD, 0.14, 0.12)
    # chave: pedra maior que sai do anel (frente em degraus) + voluta de remate em cima
    top = c + v * (r_in + 0.35)
    for w, hh, d1 in ((1.3, 2.2, 1.0), (0.9, 1.6, 1.3)):
        cbox(mb, top + v * (hh / 2) + n * ((d1 - 0.6) / 2), u, n, v, w, d1 + 0.6, hh, TRL, 0.1)
    lathe_ax(mb, top + v * 1.35 + n * 1.3, n, [(0.0, 0.0), (0.3, 0.02), (0.34, 0.14), (0.0, 0.24)], TRL, 8)
    # pes em consola: soco de obsidiana + consola de remate com o perfil que recebe o anel
    for sgn in (-1, 1):
        a = math.radians(-90.0 + sgn * 38.0)
        p = _pl(c, u, v, n, a, r_out - 0.4, -0.1)
        hz = p.z + 0.4 - floor_z
        base = Vector((p.x, p.y, floor_z))
        cbox(mb, base + UPZ * 0.35, u, n, UPZ, 2.5, 2.3, 0.8, OB, 0.1)
        hull(mb, [base + u * (s_ * 1.0) + n * d + UPZ * z for s_ in (-1, 1) for d, z in
                  ((-0.9, 0.7), (0.9, 0.7), (1.05, hz * 0.55), (0.75, hz), (-0.9, hz))], TRL)


def chandelier(mb, x, y, h, top, r=3.0, n=8):
    """lustre de ferro (12.09): aro em tubo, bracos em S, balaustre de torno no centro, VELAS DO KIT (prato, vela
    creme, chama em gota) e haste presa na nervura por uma roseta de ferro"""
    mb.tube([(x + r * math.cos(2 * math.pi * k / 16), y + r * math.sin(2 * math.pi * k / 16), h) for k in range(17)],
            0.16, BI, 5)
    # balaustre ACIMA da luz da sala (a luz fica ~0,7 abaixo do aro: nada de ferro envolvendo o ponto de luz)
    EM._lathe(mb, (x, y, h - 0.3), [(0.0, 0.0), (0.3, 0.2), (0.42, 0.45), (0.2, 0.95), (0.3, 1.2), (0.12, 1.5),
                                    (0.12, 1.95)], BI, 6, caps=(False, True))
    for k in range(n):
        a = 2 * math.pi * k / n + math.pi / n
        ca, sa = math.cos(a), math.sin(a)
        pts = [(x + rr * ca, y + rr * sa, h + zz) for rr, zz in ((0.3, 0.9), (1.2, 0.2), (2.2, 0.55), (r, 0.12))]
        mb.tube(pts, 0.08, BI, 4)
        candle(mb, x + r * ca, y + r * sa, h + 0.1, 0.8, 1.3, dish=True)
    mb.rod((x, y, h + 1.6), (x, y, top - 0.2), 0.11, BI, 6)
    EM._lathe(mb, (x, y, top - 0.55), [(0.12, 0.0), (0.62, 0.35), (0.66, 0.5), (0.0, 0.58)], BI, 6, caps=(True, False))



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
    n = 32
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
        rune(mb, Vector((cx, cy, zt - 0.05)) + rad * (5.1 * k_), Vector((-rad.y, rad.x, 0.0)), rad, up, k, 2.6 * k_, VD,
             dep=0.18)   # F11: runa +0,13 sobre o campo


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



# ==================================================================== SALAS v4
def tile_floor(mb, rect, z, margin=1.0, friso=0.8, gap=0.25, skip=None, mod=6.0):
    """piso (09.10 na v4): fiadas de lajes grandes e, a cada 2, uma FAIXA estreita de marmore negro (2 tons: a faixa
    marca o ritmo da sala e poupa lajes); a junta rebaixada mostra a base clara 0,15 abaixo;
    friso de remate junto as paredes. skip(a, b, ya, yb) -> True = laje nao entra (medalhao)."""
    x0, y0, x1, y1 = rect
    mb.box2((x0, y0, z - 0.6), (x1, y1, z - 0.15), BL, 0.0)

    def ringbox(a, b, m):
        ax0, ay0, ax1, ay1 = x0 + a, y0 + a, x1 - a, y1 - a
        bx0, by0, bx1, by1 = x0 + b, y0 + b, x1 - b, y1 - b
        mb.box2((ax0, ay0, z - 0.4), (ax1, by0, z), m, 0.0)
        mb.box2((ax0, by1, z - 0.4), (ax1, ay1, z), m, 0.0)
        mb.box2((ax0, by0, z - 0.4), (bx0, by1, z), m, 0.0)
        mb.box2((bx1, by0, z - 0.4), (ax1, by1, z), m, 0.0)
    ringbox(0.0, margin, FL)
    ringbox(margin, margin + friso, TRL)
    ix0, iy0, ix1, iy1 = x0 + margin + friso, y0 + margin + friso, x1 - margin - friso, y1 - margin - friso
    pat = (mod, mod, mod / 2.0)
    rows, acc, k = [], 0.0, 0
    while acc < (iy1 - iy0) - 0.5:
        rows.append(pat[k % 3])
        acc += pat[k % 3]
        k += 1
    sc = (iy1 - iy0) / sum(rows)
    nx = max(1, int(round((ix1 - ix0) / mod)))
    tx = (ix1 - ix0) / nx
    yy = iy0
    for j, rh in enumerate(rows):
        ty = rh * sc
        if rh < mod * 0.75:                        # fiada estreita = FAIXA continua de marmore negro (2 tons)
            mb.box2((ix0 + gap / 2, yy + gap / 2, z - 0.4), (ix1 - gap / 2, yy + ty - gap / 2, z), MBK, 0.0)
            yy += ty
            continue
        cuts = [ix0 + tx * i for i in range(nx + 1)]
        for a, b in zip(cuts, cuts[1:]):
            if skip and skip(a, b, yy, yy + ty):
                continue
            mb.box2((a + gap / 2, yy + gap / 2, z - 0.4), (b - gap / 2, yy + ty - gap / 2, z), FL, 0.0)
        yy += ty


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
PJ = FRAME_HW + 0.3 + PIL_HW                     # pilastra ao lado do vao (17,9)
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


def end_pils(nm, side):
    x0, y0, x1, y1 = ROOMS[nm]
    hw = (x1 - x0) / 2.0
    m = (PJ + hw - 0.75) / 2.0                   # pilastra do meio: 2 tramos iguais ate a coluna de canto
    ps = [-m, -PJ, PJ, m]
    if (nm, side) == ("R1", "S"):
        ps = [-PJ, PJ, m]                        # o tramo oeste inteiro e o da saida (DUN_EXIT_R1 em x -30)
    return [LX + p for p in ps]


def torch_pils(nm, side, ps):
    if side in ("W", "E"):
        return [ps[k] for k in (0, len(ps) - 1)]
    if END[(nm, side)] == "link" and nm != "R1":
        return []                                # o lado R2 do vao R1R2 fica sem tocha (luz nos portais e na chegada)
    if (nm, side) == ("R1", "N"):
        return []
    return [p for p in ps if abs(abs(p - LX) - PJ) < 0.1]


def fill_bay(mk, mi, F, nm, sa, sb, idx):
    """tramo entre pilastras: a arcada cega do kit com a variacao da sala"""
    w = sb - sa
    if w < 2.8:
        skirting(mk, F, sa, sb)
        return
    spr = ARCH_SPRING[nm]
    if nm == "R1":
        blind_arch(mk, F, sa, sb, spr, twin=w > 7.0, room="R1", mi=mi)
    elif nm == "R2":
        blind_arch(mk, F, sa, sb, spr, room="R2_twin" if idx % 2 else "R2", mi=mi)
    else:
        blind_arch(mk, F, sa, sb, spr, twin=w > 16.0, room="R3", mi=mi)


def bays_between(a, b, ps):
    """tramos livres entre a e b cortados pelas pilastras ps"""
    cuts = [a] + [q for p in sorted(ps) if a < p < b for q in (p - PIL_HW - 0.3, p + PIL_HW + 0.3)] + [b]
    return [(cuts[i], cuts[i + 1]) for i in range(0, len(cuts), 2)]


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
        ring3(mk, c, u, v, n, 2.3, 3.1, 0.0, 0.42, OB, 24)
        disc3(mk, c, u, v, n, 2.35, 0.0, 0.2, OB, 16)
        rune(mk, c + n * 0.2, u, v, n, 3, 2.9, VD, 0.16, 0.16)
        for i in range(8):
            a = 2 * math.pi * i / 8 + math.pi / 8
            rad = u * math.cos(a) + v * math.sin(a)
            obox3(mk, c + rad * 2.7 + n * 0.49, rad, u * -math.sin(a) + v * math.cos(a), n, 0.42, 0.14, 0.16, VD)


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


def niche(mk, ms, F):
    """NICHO do muro norte da R3 (DUN_NEXT_R3): fundo 1,5 atras do plano medio do muro, bochechas e teto de cantaria;
    no fundo o disco navy com aro runico e a ESPIRAL (objeto proprio SG_Dun_R3_ExitSpiral, o jogo acende)"""
    y1 = ROOMS["R3"][3]
    yw = y1 + WT                                  # face de tras do muro (304)
    yb = NICHE_BACK                               # face do fundo (305)
    hw = LINK_HW
    zb = Z - 0.6
    mk.box2((LX - hw - 1.2, yb, zb), (LX + hw + 1.2, yb + 1.4, Z + LINK_H + 1.2), CS, 0.0)
    for sg in (-1, 1):
        a, b = sorted((LX + sg * hw, LX + sg * (hw + 1.2)))
        mk.box2((a, yw - 0.05, zb), (b, yb, Z + LINK_H + 1.2), CS, 0.0)
    mk.box2((LX - hw, yw - 0.05, Z + LINK_H), (LX + hw, yb, Z + LINK_H + 1.2), CS, 0.0)
    ccol("SG_DunRoom", (LX - hw - 1.2, yb, Z - 0.5), (LX + hw + 1.2, yb + 1.4, Z + LINK_H + 1.2))
    # fundo: disco navy + aro de obsidiana com runas e fio aceso no labio
    c = Vector((LX, yb, Z + 11.0))
    u, v, n = Vector((1, 0, 0)), UPZ, Vector((0, -1, 0))
    disc3(mk, c, u, v, n, 9.7, 0.0, 0.15, VA, 32)
    ring3(mk, c, u, v, n, 9.7, 10.5, 0.0, 0.55, OB, 32)
    ring3(mk, c, u, v, n, 9.55, 9.72, 0.0, 0.68, VD, 32)
    for k in range(6):
        a = 2 * math.pi * (k + 0.5) / 6
        radial = u * math.cos(a) + v * math.sin(a)
        tang = u * -math.sin(a) + v * math.cos(a)
        rune(mk, c + radial * 10.1 + n * 0.55, tang, radial, n, k + 1, 0.62, VD, 0.14, 0.12)
    spiral(ms, c, u, v, n, 9.0, 0.18, 0.36, VG, arms=5, twist=2.7, a0=1.1)
    return c, n


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
    spiral(mb, c, u, UPZ, n, r_in - 0.1, -0.3, -0.1, VG, arms=5, twist=2.7, a0=0.4)
    rise = r_out + 2.2
    spr = c.z - Z
    arch_panel(mb, F, LX, r_out + 0.2, rise, spr, 0.0, 0.0, 0.15, VA, n=8)
    arch_band(mb, F, LX, r_out + 0.2, rise, spr, 0.0, 0.6, -0.1, 0.55, TRL, n=8)
    ogee_band(mb, F, LX, r_out + 0.8, rise + 0.6, spr, 0.5, -0.1, 0.8, CS, n=8)
    ccol("SG_DunPortal", F.p(LX - r_out, 0.0, -0.5), F.p(LX + r_out, 1.75, 2 * r_out - 0.6))
    return c                                     # (a inscricao do piso e o circulo runico do spawn, 11 a frente)


def exit_arch(mb, F, s, orders=2):
    """SAIDA por prompt ('Sair'): arco menor com o vortice APAGADO - anel de aduelas com runas, disco navy e espiral
    de pedra negra (sem brilho), campo e arquivolta do kit. Colisao so do anel (nada de barreira de toque)."""
    r_in, r_out = EXIT_R
    n = F.n()
    c = F.v(s, 1.0, r_out - 0.3)
    u = n.cross(UPZ).normalized()
    portal_frame(mb, c, u, UPZ, n, r_in, r_out, Z, nv=12, seg=20)
    disc3(mb, c, u, UPZ, n, r_in + 0.15, -0.5, -0.3, VA, 24)
    spiral(mb, c, u, UPZ, n, r_in - 0.2, -0.28, -0.12, OB, arms=5, twist=2.7, seg=7, a0=0.8)
    rise = r_out + 0.9
    spr = c.z - Z
    arch_panel(mb, F, s, r_out + 0.2, rise, spr, 0.0, 0.0, 0.15, VA, n=8)
    t = 0.6 if orders == 2 else 0.5
    arch_band(mb, F, s, r_out + 0.2, rise, spr, 0.0, t, -0.1, 0.55, TRL, n=8)
    if orders == 2:                                                             # 2a ordem: le como PORTA
        ogee_band(mb, F, s, r_out + 0.8, rise + 0.6, spr, 0.4, -0.1, 0.8, CS, n=8)
    ccol("SG_DunExit", F.p(s - r_out, 0.0, -0.5), F.p(s + r_out, 1.75, 2 * r_out - 0.6))


def spawn_circle(mb, cx, cy, r=4.2, k0=0):
    """CIRCULO RUNICO do spawn: placa baixa (+0,15) com aro de remate, faixa de obsidiana com 6 runas acesas (Neon
    escuro, +0,13) e miolo de marmore negro com a seta do rumo (+Y, para a proxima sala)"""
    n = 20
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
        rune(mb, Vector((cx, cy, zt - 0.05)) + rad * (r - 1.15), Vector((-rad.y, rad.x, 0.0)), rad, UPZ, k + k0, 1.1,
             VD, dep=0.18)
    # seta rasa (chevron) no miolo: aponta a proxima sala
    for sg in (-1, 1):
        a = Vector((cx, cy + 1.0, zt - 0.05))
        b = Vector((cx + sg * 1.0, cy - 0.2, zt - 0.05))
        ax = (b - a).normalized()
        obox3(mb, (a + b) / 2 + UPZ * 0.09, ax, UPZ.cross(ax), UPZ, (b - a).length + 0.2, 0.22, 0.18, VD)


def retable_bay(mk, mi, F, s0, s1):
    """RETABULO da R3 (variacao da sala: 'altar') no tramo do eixo do muro leste: a arcada cega do tramo, mesa de altar
    de obsidiana com frontal navy e runa acesa baixa, 4 velas do kit, painel ogival interno com a runa grande"""
    s = (s0 + s1) / 2.0
    blind_arch(mk, F, s0, s1, ARCH_SPRING["R3"], room="R3_altar", mi=mi)
    fblock(mk, F, s - 3.4, s + 3.4, -0.2, 1.9, -0.1, 0.45, OB, 0.1)                       # degrau
    fblock(mk, F, s - 2.9, s + 2.9, -0.2, 1.5, 0.45, 3.0, OB, 0.1)                        # corpo da mesa
    fledge(mk, F, s - 3.2, s + 3.2, [(-0.2, 3.0), (1.65, 3.0), (1.85, 3.16), (1.85, 3.38), (-0.2, 3.38)], TRL)
    fblock(mk, F, s - 2.1, s + 2.1, 1.5, 1.64, 1.0, 2.55, VA, 0.04)                       # frontal rebaixado
    rune(mk, F.v(s, 1.64, 1.78), F.u(), UPZ, F.n(), 4, 1.35, VD, 0.16, 0.12)
    for sc in (s - 2.5, s - 1.6, s + 1.6, s + 2.5):
        p = F.v(sc, 0.7, 3.38)
        candle(mi, p.x, p.y, p.z, 0.62 if abs(sc - s) > 2.0 else 0.9, 1.1, dish=True)
    arch_panel(mk, F, s, 2.2, 2.6, 8.2, 3.38, 0.15, 0.32, VA, n=6)
    ogee_band(mk, F, s, 2.2, 2.6, 8.2, 0.42, 0.15, 0.62, TRL)
    for sc in (s - 2.41, s + 2.41):
        fblock(mk, F, sc - 0.21, sc + 0.21, 0.15, 0.62, 3.38, 8.2, TRL, 0.06)
    rune(mk, F.v(s, 0.32, 6.9), F.u(), UPZ, F.n(), 6, 2.4, VD, 0.16, 0.14)
    fcol("SG_DunKit", F, s - 3.4, s + 3.4, 0.0, 1.9, -0.5, 3.4)


def lunette_lancets(mk, F, nm):
    """CLERESTORIO CEGO no timpano dos muros de ponta (o pano entre a cornija e a abobada nao fica chapado): 2 lancetas
    com campo navy, ombreiras e arquivolta de remate sobre um peitoril moldurado, ate 1,6 abaixo da abobada"""
    x0, y0, x1, y1 = ROOMS[nm]
    xc = (x0 + x1) / 2.0
    for sg in (-1, 1):
        u = sg * (24.0 if nm == "R1" else 27.0)
        s = xc + u
        top = vault_z((x0, y0, x1, y1), "y", 0.0, R_SPR, R_CROWN, abs(u) + 2.6) - 1.6
        hw, h0 = 2.1, R_SPR + 2.4
        rise = hw * 1.6
        spr = top - rise - 0.45
        fledge(mk, F, s - hw - 0.9, s + hw + 0.9, [(-0.1, h0 - 0.5), (0.5, h0 - 0.5), (0.62, h0 - 0.2), (0.62, h0),
                                                 (-0.1, h0)], TRL)
        arch_panel(mk, F, s, hw, rise, spr, h0, 0.0, 0.15, VA, 4)
        for q in (-1, 1):
            a, b = sorted((s + q * hw, s + q * (hw + 0.45)))
            fblock(mk, F, a, b, -0.1, 0.42, h0, spr, TRL, 0.0)
        ogee_band(mk, F, s, hw, rise, spr, 0.45, -0.1, 0.5, TRL, 4)


# ------------------------------------------------------------------ paredes, kit e abobadas
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


def room_kit():
    """kit das salas (overhaul 09.10 na escala v4): pilastras com colunelo e capitel onde a nervura nasce, colunas de
    canto, arcadas cegas de 2 ordens com a variacao DIRIGIDA de cada sala, cornija, tochas, pisos de lajes, abobada de
    bercos com nervuras em pera e liernes, vaos/portais, portal de chegada, saidas, spawns, retabulo e lustres"""
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
        ribs = rib_ys(nm)
        # ---- muros longos (oeste / leste): pilastras nos pontos das nervuras
        for side in ("W", "E"):
            F = Fs[side]
            for p in ribs:
                pilaster(mk, F, p, R_SPR, A, twin=twin)
            for p in torch_pils(nm, side, ribs):
                torch(mi, F, p, 0.0, TORCH_H, twin=twin)
            bays = bays_between(y0 + CORNER + 0.1, y1 - CORNER - 0.1, ribs)
            for i, (sa, sb) in enumerate(bays):
                if nm == "R3" and side == "W" and i == 0:
                    skirting(mk, F, sa, sb)
                    exit_arch(mp, F, EXIT_S["R3"], orders=1)
                elif nm == "R3" and side == "E" and i == len(bays) // 2:
                    skirting(mk, F, sa, sb)
                    retable_bay(mk, mi, F, sa, sb)
                else:
                    fill_bay(mk, mi, F, nm, sa, sb, i)
            cornice(mk, F, y0 + 2.4, y1 - 2.4, R_SPR)
        # ---- muros de ponta (sul / norte): colunas de canto, pilastras, vao/portal/nicho no eixo
        for side in ("S", "N"):
            F = Fs[side]
            kind = END[(nm, side)]
            corner_col(mk, F, x0, 1, R_SPR, A)
            corner_col(mk, F, x1, -1, R_SPR, A)
            ps = end_pils(nm, side)
            for p in ps:
                pilaster(mk, F, p, R_SPR, A, twin=twin)
            for p in torch_pils(nm, side, ps):
                torch(mi, F, p, 0.0, TORCH_H, twin=twin)
            lunette_lancets(mk, F, nm)
            if kind == "arrival":
                c = arrival_portal(mp, F)
                hwp = PORTAL_R[1] + 0.2 + 0.6 + 0.5 + 0.4
                spans = [(x0 + CORNER + 0.1, LX - hwp), (LX + hwp, x1 - CORNER - 0.1)]
            else:
                link_frame(mk, F, kind)
                spans = [(x0 + CORNER + 0.1, LX - FRAME_HW - 0.1), (LX + FRAME_HW + 0.1, x1 - CORNER - 0.1)]
            k = 0
            for a, b in spans:
                for sa, sb in bays_between(a, b, ps):
                    if kind == "arrival" and sa < EXIT_S["R1"] < sb:
                        skirting(mk, F, sa, sb)
                        exit_arch(mp, F, EXIT_S["R1"])
                    else:
                        fill_bay(mk, mi, F, nm, sa, sb, k)
                    cornice(mk, F, sa - 0.1, sb + 0.1, R_SPR)
                    k += 1
        # ---- piso, spawn, abobada
        cxr, cyr = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        tile_floor(mf, (x0, y0, x1, y1), Z, margin=1.0, friso=0.8, mod=7.0)
        sx, sy = L.dun_spawn(nm)
        spawn_circle(mfd, sx, sy, 4.2, k0={"R1": 0, "R2": 2, "R3": 4}[nm])
        vault(mv, (x0, y0, x1, y1), "y", Z, R_SPR, R_CROWN, ribs=ribs, liernes=(0.5,))
    # soleiras dos vaos (no plano da parede)
    for ra, rb in zip(ORDER, ORDER[1:]):
        link_sill(mfd, ROOMS[ra][3], ROOMS[rb][1], next_=(ra == "R2"))
    link_sill(mfd, ROOMS["R3"][3], NICHE_BACK, next_=True, ym=L.dun_next("R3")[1], back=0.0)
    next_portals(mk)
    altar_medallion(mfd, (ROOMS["R3"][0] + ROOMS["R3"][2]) / 2.0, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0)
    for nm, x, y, h, r, nc in CHANDELIERS:
        rect = ROOMS[nm]
        top = vault_z(rect, "y", Z, R_SPR, R_CROWN, 0.0) - 0.8
        chandelier(mi, x, y, Z + h, top, r=r, n=nc)
    for m in (mk, mv, mf, mfd, mi, mp):
        m.finish()


MED_HS = 10.5                                    # medalhao do centro da R3 (raio 9,1: placa baixa)
_R2 = ROOMS["R2"]
# lustres: (sala, x, y, altura do aro, raio, velas) - R1 na nervura do meio, R2 nos cruzamentos das nervuras 2 e 5,
# R3 coroa maior no centro (sobre o medalhao)
CHANDELIERS = (("R1", LX, (ROOMS["R1"][1] + ROOMS["R1"][3]) / 2.0, 21.0, 4.2, 6),
               ("R2", LX, _R2[1] + (_R2[3] - _R2[1]) * 2.0 / 7.0, 21.5, 4.6, 6),
               ("R2", LX, _R2[1] + (_R2[3] - _R2[1]) * 5.0 / 7.0, 21.5, 4.6, 6),
               ("R3", LX, (ROOMS["R3"][1] + ROOMS["R3"][3]) / 2.0, 20.8, 5.8, 10))


def room_lights():
    """5 luzes: portal de chegada (violeta) e os 4 lustres (quentes)"""
    y0 = ROOMS["R1"][1]
    light("L_SGDun_R1_Portal", "POINT", (LX, y0 + 7.0, Z + 8.5), 5000.0, (0.64, 0.42, 1.0), 1.5)
    for i, (nm, x, y, h, r, nc) in enumerate(CHANDELIERS):
        e = {"R1": 11000.0, "R2": 15000.0, "R3": 21000.0}[nm]
        light("L_SGDun_%s_Chandelier%s" % (nm, "" if nm != "R2" else ("S" if i == 1 else "N")), "POINT",
              (x, y, Z + h - 0.7), e, (1.0, 0.68, 0.40), 1.0)


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
