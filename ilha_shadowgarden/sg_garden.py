# sg_garden - JARDINAGEM da Ilha 3 (Shadow Garden), 2026-09-29 (pedido do usuario: "a grama do roblox esta muito
# feia ... resultado semelhante ao bonemeal na grama do minecraft").
# O gramado deixa de ser tapete verde chapado: um CAMPO VIVO de grama alta em tufos e flores pequenas em manchas.
#
# KIT (reutilizavel; chamado pelo sg_veg, sg_court e sg_village):
#   clump        - TOUCEIRA do campo: coroa em estrela de 7-9 laminas largas unidas no pe (vale rente ao chao, ponta
#                  alta; as do lado de fora da borda / do vento mais altas e abertas), 2n tris, 1 material por touceira;
#   blade/tuft   - laminas finas (piramide de 3 faces, a mais alta CURVA em 2 lances) para floreiras e closes;
#   3 tons de lamina por MATERIAL (escuro / meio / luar) misturados ENTRE touceiras (o Roblox ignora cor de vertice);
#   flores       - 4 especies lidas pela SILHUETA: flor-da-lua branca de 5 petalas (estrela em taca com miolo ambar),
#                  campanula violeta (3 sinos pendentes numa haste inclinada), espiga azul (lavanda/delfinio: fuso de
#                  4 faces no alto da haste), dente-de-leao ambar (raro: bola baixa + roseta); + rosa branca;
#   hedge_round  - sebe de buxo de topo ARREDONDADO; topiary (bola de buxo); cushion (massa baixa de canteiro);
#   bed          - canteiro de cantaria baixa (terra + bordadura em pecas) encostado na fachada;
#   formal_bed   - compartimento do jardim de lua do patio (faixas lavanda / flor-da-lua / campanula);
#   vine         - roseira trepadeira (hastes de madeira, tufos de folhas de buxo e rosas brancas) em parede PLANA
#                  (flat_wall confere por raios: nunca sobre janela, postigo ou torre);
#   window_box_planting / ground_planter_planting / trail - plantio das floreiras da vila (tema por casa).
# CAMPO (build, roda no fim do sg_veg; tudo decoracao, SEM colisao):
#   1. mascara do gramado por raio (so face de grama Grass_SG*, fora de solido); ruas + terra batida, praca, escadas,
#      pontes, lotes das casas, alquimia e cachoeiras excluidos tambem pela PLANTA (no estudio de uma zona ela e
#      montada depois do vestir);
#   2. campo de distancia ate a borda do gramado: densidade CHEIA na borda (muro, rua, casa, canteiro, poste),
#      rala no meio; mais cheia ao pe das arvores; manchas dirigidas por um campo de baixa frequencia (nao confete);
#      VISIBILIDADE (rodada 2): ate 25 do eixo das rotas o gramado fica COBERTO (grade de 1,25, tufos quase se
#      tocando; touceira grande so na borda/arvore/poste/foco, no miolo o tufo LOD de 3-4 laminas largas, 6-8 tris);
#      longe das rotas, ralo; tons das laminas um passo ACIMA do chao (o "pelo" claro do bonemeal);
#      ZERO em rota (corredor de 0,9 com esmaecimento ate 2,2), piso, rua, escada ou mineracao;
#   3. flores em MANCHAS dirigidas: jardins das casas (HOUSE_GARDENS: variacao por casa), postes, pes de escada e
#      portoes, porta da alquimia, cabeceira da saida, arvores do gramado e 10 "pontos de bonemeal" no gramado aberto
#      (maximos do campo), sempre em espiral de filotaxia com a 2a especie na borda;
#   4. manchas de tom no gramado base (pocas escuras sob as arvores e onde o capim adensa, clareiras de luar), rentes;
#   5. canteiros das arvores em piso calcado (sg_veg.tree_pit), 4 canteiros em arco ao pe da fonte da praca;
#   6. no patio do castelo (sg_court): jardim de lua formal + roseiras na face interna da muralha.
# QA proprio (GARDEN_QA): nenhum item do campo cai em rua/praca/escada/casa/piso calcado/rota/salao/dungeon.
# Orcamento: grama + flores <= ~80k tris (rodada 2, autorizado; medido ~78k liquidos na ilha); MeshParts <= +50.
# Prefixo SG_Veg_Gdn_, colecao 10_VEGETATION (1 objeto por zona: P1, P2W, P2E, LawnTone, Court).
# Materiais: registrados na paleta base (sg_lib.SMATS).
import math
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sg_lib as SL
from sg_lib import MB, fm_lib
import sg_layout as L

P1, P2, P3, SUM = L.P1, L.P2, L.P3, L.SUM
COLL = "10_VEGETATION"

# ------------------------------------------------------------------ materiais (paleta base: sg_lib.SMATS)
BLADE_D = "Leaf_SGGrassDark"      # base dos tufos (sombra)
BLADE_M = "Leaf_SGGrass"          # laminas do meio, hastes
BLADE_L = "Leaf_SGGrassLight"     # pontas ao luar / folhagem cinza da lavanda
F_MOON = "Flower_SGMoon"          # flor-da-lua / rosa branca
F_BELL = "Flower_SGBell"          # campanula violeta
F_SPIKE = "Flower_SGSpike"        # espiga azul
F_AMBER = "Flower_SGAmber"        # dente-de-leao / miolo da flor-da-lua
LEAF_BOX = "Leaf_SGBox"           # buxo (sebes, bolas, arbustos, folhas das trepadeiras)
LAWN_L = "Grass_SGLight"          # clareira de luar no gramado
LAWN_D = "Grass_SG_B"             # poca escura sob as arvores (variante ja existente da grama)
GRAVEL = "Dirt_SGGravel"          # cascalho dos caminhos do jardim do patio
SOIL = "Dirt_SG"
CURB = "Stone_SG_TrimLow"         # bordadura dos canteiros (cantaria de remate do kit)
STEM_W = "Wood_SG_Dark"           # haste lenhosa das roseiras
for _k, _v in ((BLADE_D, (56, 86, 74)), (BLADE_M, (74, 110, 90)), (BLADE_L, (104, 140, 112)), (F_MOON, (198, 202, 216)),
               (F_BELL, (122, 90, 168)), (F_SPIKE, (86, 110, 178)), (F_AMBER, (204, 152, 72)), (LEAF_BOX, (40, 68, 56)),
               (LAWN_L, (50, 76, 67)), (GRAVEL, (98, 96, 106))):
    # (so por seguranca: o registro de verdade e o sg_lib.SMATS; setdefault nao muda o que ja existe)
    fm_lib.MATS.setdefault(_k, (fm_lib.S(*_v), 0.85, 0.0, 0, None, 0.04))
fm_lib.MATS.setdefault(CURB, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))

WIND = (0.62, -0.78)              # vento/luar de noroeste: as laminas pendem para sudeste (normalizado abaixo)
_wl = math.hypot(*WIND)
WIND = (WIND[0] / _wl, WIND[1] / _wl)

# ------------------------------------------------------------------ cameras (renders/overhaul/13b_jardim)
CAMS = {
    "CAM_SGGdn_PH_P2W": ((-44.0, -47.0, P2 + 5.2), (-78.0, -60.0, P2 + 1.5), 22),
    "CAM_SGGdn_PH_P2E": ((22.0, -47.0, P2 + 5.2), (44.0, -60.0, P2 + 1.5), 22),
    "CAM_SGGdn_PH_P1": ((-60.0, -124.0, P1 + 5.2), (-78.0, -140.0, P1 + 2.0), 22),
    "CAM_SGGdn_Plaza": ((14.0, -110.0, P1 + 6.5), (-10.0, -146.0, P1 + 1.0), 22),
    "CAM_SGGdn_StreetEdge": ((-24.0, -43.0, P2 + 4.0), (-60.0, -50.0, P2 + 0.3), 24),
    "CAM_SGGdn_Court_A": ((-4.0, 1.0, P3 + 5.2), (-26.0, 10.0, P3 + 0.5), 22),
    "CAM_SGGdn_Court_B": ((42.0, 22.0, P3 + 6.5), (22.0, 9.0, P3 + 0.3), 22),
    "CAM_SGGdn_CU_Tuft": ((41.0, -53.6, P2 + 2.1), (41.6, -57.0, P2 + 0.45), 30),
    "CAM_SGGdn_CU_WinBox": ((-75.0, -131.0, P1 + 5.5), (-78.0, -137.0, P1 + 3.5), 30),
    "CAM_SGGdn_Block": ((-40.0, -28.0, P2 + 34.0), (-70.0, -60.0, P2), 22),
    "CAM_SGGdn_House_A": ((-86.0, -52.0, P2 + 5.2), (-94.0, -61.0, P2 + 1.5), 24),
    "CAM_SGGdn_House_B": ((72.0, -120.7, P1 + 5.2), (80.0, -134.5, P1 + 1.5), 24),
    "CAM_SGGdn_House_C": ((-51.0, -38.8, P2 + 5.2), (-58.5, -29.6, P2 + 2.0), 24),
}

# ------------------------------------------------------------------ utilidades deterministicas
def hh(x, y, k=0.0):
    """ruido-hash [0,1) fixo por posicao (nada de sorteio por execucao)"""
    v = math.sin(x * 12.9898 + y * 78.233 + k * 37.719) * 43758.5453
    return v - math.floor(v)


def field(x, y):
    """campo de BAIXA frequencia [0,1] que dirige as manchas (cheio / ralo) do gramado"""
    v = (math.sin(x / 9.3 + 0.7) * math.cos(y / 7.1 - 0.4) + 0.7 * math.sin((x + y) / 13.7 + 1.3)
         + 0.45 * math.cos((x - 2.0 * y) / 17.9 + 2.2))
    return max(0.0, min(1.0, 0.5 + v / 4.3))


def field2(x, y):
    """segundo campo (tom das laminas: onde a lua bate mais)"""
    v = math.sin(x / 6.1 - 1.1) * math.sin(y / 8.3 + 0.5) + 0.6 * math.cos((x + 1.7 * y) / 11.3)
    return max(0.0, min(1.0, 0.5 + v / 3.2))


# ------------------------------------------------------------------ faces orientadas (sem depender do recalc)
def _face(bm, vs, inside):
    a, b, c = vs[0].co, vs[1].co, vs[2].co
    n = (b - a).cross(c - a)
    cen = Vector((0.0, 0.0, 0.0))
    for v in vs:
        cen += v.co
    cen /= len(vs)
    if n.dot(cen - inside) < 0:
        vs = list(reversed(vs))
    return bm.faces.new(vs)


STATS = {}


def _mbtris(mb):
    return sum(len(f.verts) - 2 for f in mb.bm.faces)

import os as _os
DEBUG = bool(_os.environ.get("SG_GDN_DEBUG"))


def _count(k, n=1):
    STATS[k] = STATS.get(k, 0) + n


# ------------------------------------------------------------------ KIT: laminas e tufos
def blade(mb, base, ang, h, w, lean, m, curved=False, closed=False, keel=0.4, wind=0.0):
    """lamina: piramide de 3 faces (secao em V com quilha atras) com a base 0,08 enterrada; 'ang' = para onde pende,
    'lean' (0..0,8) quanto pende; curved = 2 lances (a ponta pende mais: arco). closed = fundo fechado (objetos
    com recalc de normais). tris: 3 (reta) / 9 (curva) (+1 fechada)"""
    bm = mb.bm
    bx, by, bz = base
    bz -= 0.08
    ca, sa = math.cos(ang), math.sin(ang)
    px, py = -sa, ca
    ring = [Vector((bx + px * w / 2, by + py * w / 2, bz)), Vector((bx - px * w / 2, by - py * w / 2, bz)),
            Vector((bx - ca * w * keel, by - sa * w * keel, bz))]
    lx, ly = ca * lean + WIND[0] * wind, sa * lean + WIND[1] * wind
    ll = math.hypot(lx, ly)
    up = h * math.sqrt(max(0.25, 1.0 - min(0.9, ll) ** 2))
    tip = Vector((bx + lx * h, by + ly * h, bz + 0.08 + up))
    vs = [bm.verts.new(p) for p in ring]
    allv = list(vs)
    if curved:
        f = 0.56
        mc = Vector((bx + lx * h * 0.26, by + ly * h * 0.26, bz + 0.08 + up * 0.62))
        cen0 = Vector((bx, by, bz))
        mid = [bm.verts.new(mc + (p - cen0) * f) for p in ring]
        allv += mid
        ins = (cen0 + mc) / 2
        for i in range(3):
            j = (i + 1) % 3
            _face(bm, [vs[i], vs[j], mid[j], mid[i]], ins)
        tv = bm.verts.new(tip)
        allv.append(tv)
        ins2 = (mc * 2 + tip) / 3
        for i in range(3):
            _face(bm, [mid[i], mid[(i + 1) % 3], tv], ins2)
    else:
        tv = bm.verts.new(tip)
        allv.append(tv)
        ins = (ring[0] + ring[1] + ring[2]) / 3 * 0.75 + tip * 0.25
        for i in range(3):
            _face(bm, [vs[i], vs[(i + 1) % 3], tv], ins)
    if closed:
        _face(bm, vs, (ring[0] + ring[1] + ring[2]) / 3 + Vector((0, 0, 0.05)))
    mb._post(allv, m, 0.0, 0, 1)
    return tip


def tuft(mb, x, y, z, s, n=4, out=None, tone=0.5, closed=False, curved=1, spread=1.0):
    """tufo: n laminas em leque (fase por posicao; as do lado 'out' (para fora da borda) mais altas e pendendo mais),
    alturas s * (0,55..1,0); material por lamina: a mais alta MEIO ou LUZ (tone > 0,62), as baixas ESCURAS.
    tris ~ 3n + 6 por lamina curva"""
    ph = hh(x, y) * math.tau
    ox, oy = out if out else (WIND[0], WIND[1])
    hs = []
    for i in range(n):
        a = ph + i * math.tau / n + (hh(x, y, i + 1) - 0.5) * 0.9
        facing = math.cos(a) * ox + math.sin(a) * oy                 # -1..1
        hh_ = s * (0.62 + 0.26 * facing + 0.18 * hh(y, x, i + 3))
        hs.append((hh_, a, facing))
    order = sorted(range(n), key=lambda i: -hs[i][0])
    tall = order[0]
    for rank, i in enumerate(order):
        h_, a, facing = hs[i]
        r0 = s * 0.07 * spread * (0.6 + hh(x, y, i + 7))
        bx, by = x + math.cos(a) * r0, y + math.sin(a) * r0
        lean = 0.22 + 0.2 * max(0.0, facing) + 0.1 * hh(x, y, i + 11)
        if rank == 0:
            m = BLADE_L if tone > 0.62 else BLADE_M
        elif rank == 1 and n >= 4:
            m = BLADE_M
        else:
            m = BLADE_D
        w = max(0.07, s * (0.11 if rank == 0 else 0.13))
        blade(mb, (bx, by, z), a, h_, w, lean, m, curved=(rank < curved), closed=closed, wind=0.08)
    _count("tufos")


def clump(mb, x, y, z, s, n=6, out=None, m=BLADE_M, wide=False):
    """TOUCEIRA de grama do campo (a massa do "bonemeal"): coroa em estrela de n laminas largas unidas no pe - cada
    lamina sobe de um vale rente ao chao ate a ponta; as do lado 'out' (para fora da borda / vento) mais altas e mais
    abertas. Le tufo de capim de qualquer lado e estrela de cima. 1 material por touceira (o tom varia ENTRE touceiras).
    tris 2n"""
    bm = mb.bm
    ph = hh(x, y) * math.tau
    ox, oy = out if out else WIND
    R = (0.8 if wide else 0.56) * s
    c = Vector((x, y, z + 0.06))
    ring = []
    for k in range(2 * n):
        a = ph + k * math.pi / n + (hh(x, y, k + 1) - 0.5) * (0.5 * math.pi / n)
        ca, sa = math.cos(a), math.sin(a)
        if k % 2 == 0:
            facing = ca * ox + sa * oy
            h = s * (0.66 + 0.24 * facing + 0.26 * hh(y, x, k + 2))
            r = R * (0.85 + 0.35 * max(0.0, facing) + 0.2 * hh(x, y, k + 5))
            ring.append(bm.verts.new((x + ca * r, y + sa * r, z + h)))
        else:
            r = R * (0.55 if wide else 0.42)
            ring.append(bm.verts.new((x + ca * r, y + sa * r, z - 0.04)))
    cv = bm.verts.new(c)
    ins = Vector((x, y, z - 0.6))
    for k in range(2 * n):
        _face(bm, [cv, ring[k], ring[(k + 1) % (2 * n)]], ins)
    mb._post(ring + [cv], m, 0.0, 0, 1)
    _count("touceiras")


# ------------------------------------------------------------------ KIT: flores
def _basis(nrm):
    n = Vector(nrm).normalized()
    ref = Vector((1.0, 0.0, 0.0)) if abs(n.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    e1 = n.cross(ref).normalized()
    e2 = n.cross(e1).normalized()
    return n, e1, e2


STEM = [BLADE_M]    # material das hastes (as floreiras trocam pelo escuro: 1 material a menos no objeto da vila)


def stem(mb, a, b, r=0.035, m=None, closed=False):
    """haste: piramide fina de 3 faces do pe (a, enterrado 0,05) ate b. tris 3"""
    m = m or STEM[0]
    bm = mb.bm
    a = Vector(a) - Vector((0, 0, 0.05))
    b = Vector(b)
    d = (b - a).normalized()
    n, e1, e2 = _basis(d)
    ring = [bm.verts.new(a + (e1 * math.cos(k * math.tau / 3) + e2 * math.sin(k * math.tau / 3)) * r) for k in range(3)]
    tv = bm.verts.new(b)
    ins = a * 0.7 + b * 0.3
    for i in range(3):
        _face(bm, [ring[i], ring[(i + 1) % 3], tv], ins)
    if closed:
        _face(bm, ring, a + d * 0.05)
    mb._post(ring + [tv], m, 0.0, 0, 1)


def star_head(mb, c, r, nrm, rot, m=F_MOON, center=F_AMBER, inner=0.42, cup=0.12, bottom=False):
    """flor de 5 petalas: estrela de 10 pontas (5 petalas de raio r, entalhes a inner*r) com leque de cima ate o apice
    (petalas em taca rasa) e fundo plano; miolo = piramide ambar curta. tris 18 + 3"""
    bm = mb.bm
    n, e1, e2 = _basis(nrm)
    c = Vector(c)
    ring = []
    for k in range(10):
        a = rot + k * math.pi / 5
        rr = r if k % 2 == 0 else r * inner
        ring.append(bm.verts.new(c + (e1 * math.cos(a) + e2 * math.sin(a)) * rr + n * (cup * r if k % 2 == 0 else 0.0)))
    ap = bm.verts.new(c + n * r * 0.1)
    for i in range(10):
        _face(bm, [ring[i], ring[(i + 1) % 10], ap], c - n * r * 0.2)
    if bottom:
        _face(bm, list(ring), c + n * r * 0.3)
    mb._post(ring + [ap], m, 0.0, 0, 1)
    if center:
        cr = r * 0.3
        rb = [bm.verts.new(c + (e1 * math.cos(rot + k * math.tau / 3 + 0.5) + e2 * math.sin(rot + k * math.tau / 3 + 0.5))
                           * cr) for k in range(3)]
        tp = bm.verts.new(c + n * r * 0.34)
        for i in range(3):
            _face(bm, [rb[i], rb[(i + 1) % 3], tp], c + n * r * 0.05)
        if bottom:
            _face(bm, rb, c + n * r * 0.2)
        mb._post(rb + [tp], center, 0.0, 0, 1)


def pent_bud(mb, c, r, nrm, rot, m, up=0.55, down=0.3):
    """botao/rosa: bipiramide de 5 lados (achatada). tris 10"""
    bm = mb.bm
    n, e1, e2 = _basis(nrm)
    c = Vector(c)
    ring = [bm.verts.new(c + (e1 * math.cos(rot + k * math.tau / 5) + e2 * math.sin(rot + k * math.tau / 5)) * r)
            for k in range(5)]
    t = bm.verts.new(c + n * r * up)
    b = bm.verts.new(c - n * r * down)
    for i in range(5):
        j = (i + 1) % 5
        _face(bm, [ring[i], ring[j], t], c)
        _face(bm, [ring[j], ring[i], b], c)
    mb._post(ring + [t, b], m, 0.0, 0, 1)


def octa(mb, c, rx, rz, m, rot=0.0, lo=None):
    """octaedro (bola baixa / fuso): raio rx no plano, meia-altura rz (lo = meia-altura de baixo). tris 8"""
    bm = mb.bm
    c = Vector(c)
    lo = rz if lo is None else lo
    ring = [bm.verts.new(c + Vector((math.cos(rot + k * math.pi / 2) * rx, math.sin(rot + k * math.pi / 2) * rx, 0.0)))
            for k in range(4)]
    t = bm.verts.new(c + Vector((0, 0, rz)))
    b = bm.verts.new(c - Vector((0, 0, lo)))
    for i in range(4):
        j = (i + 1) % 4
        _face(bm, [ring[i], ring[j], t], c)
        _face(bm, [ring[j], ring[i], b], c)
    mb._post(ring + [t, b], m, 0.0, 0, 1)


def bell_cone(mb, apex, mouth, r, m=F_BELL, rot=0.0, closed=False):
    """sino de 5 lados ARREDONDADO: apice preso na haste -> ombro (0,62 r a 30% da altura, a copa redonda) -> boca
    aberta (r, com a borda um pouco virada para fora). Boca fechada so em objeto com recalc. tris 15 (+3)"""
    bm = mb.bm
    apex, mouth = Vector(apex), Vector(mouth)
    n, e1, e2 = _basis(mouth - apex)
    L_ = (mouth - apex).length

    def ring(c, rr, ph=0.0):
        return [bm.verts.new(c + (e1 * math.cos(rot + ph + k * math.tau / 5) + e2 * math.sin(rot + ph + k * math.tau / 5))
                             * rr) for k in range(5)]
    sh = ring(apex + n * L_ * 0.3, r * 0.66)
    mo = ring(mouth, r, 0.0)
    ap = bm.verts.new(apex)
    ins = apex + n * L_ * 0.5
    for i in range(5):
        j = (i + 1) % 5
        _face(bm, [sh[i], sh[j], ap], ins)
        _face(bm, [sh[i], sh[j], mo[j], mo[i]], ins)
    if closed:
        _face(bm, mo, ins)
    mb._post(sh + mo + [ap], m, 0.0, 0, 1)


def flower_moon(mb, x, y, z, s=1.0, closed=False, leaves=False):
    """flor-da-lua: haste curta, estrela branca de 5 petalas (r 0,22 s) voltada para cima e um pouco para o sul"""
    h = s * (0.5 + 0.22 * hh(x, y, 5))
    tx, ty = (hh(x, y, 6) - 0.5) * 0.12 * s, (hh(y, x, 6) - 0.5) * 0.12 * s
    c = (x + tx, y + ty, z + h)
    stem(mb, (x, y, z), (c[0], c[1], c[2] - 0.02), 0.03 * s + 0.01, closed=closed)
    tilt = 0.22
    nrm = (tx * 2.0 + WIND[0] * tilt * 0.3, ty * 2.0 - tilt, 1.0)
    star_head(mb, c, 0.27 * s, nrm, hh(x, y, 8) * 1.3, bottom=closed)
    if leaves:
        for k in range(2):
            a = hh(x, y, 9 + k) * math.tau
            blade(mb, (x, y, z), a, 0.34 * s, 0.1 * s, 0.7, BLADE_D, closed=closed)
    _count("flor_lua")


def flower_bell(mb, x, y, z, s=1.0, closed=False):
    """campanula: haste inclinada com 3 sinos violeta pendentes, alternando o lado"""
    h = s * (0.85 + 0.25 * hh(x, y, 12))
    a = hh(x, y, 13) * math.tau
    ca, sa = math.cos(a), math.sin(a)
    top = Vector((x + ca * 0.22 * s, y + sa * 0.22 * s, z + h))
    stem(mb, (x, y, z), top, 0.032 * s + 0.01, closed=closed)
    for k, t in enumerate((0.62, 0.8, 1.0)):
        p = Vector((x, y, z)) + (top - Vector((x, y, z))) * t
        side = 1 if k % 2 == 0 else -1
        ox, oy = -sa * side * 0.09 * s + ca * 0.05 * s, ca * side * 0.09 * s + sa * 0.05 * s
        apex = Vector((p.x + ox * 0.4, p.y + oy * 0.4, p.z - 0.01))
        mouth = Vector((p.x + ox * 1.6, p.y + oy * 1.6, p.z - 0.2 * s))
        bell_cone(mb, apex, mouth, 0.12 * s * (1.0 if k else 1.15), rot=a + k, closed=closed)
    _count("flor_sino")


def flower_spike(mb, x, y, z, s=1.0, closed=False, n=2):
    """espiga azul (lavanda/delfinio): n hastes em leque, cada uma com um FUSO de 4 faces no terco de cima"""
    for k in range(n):
        a = hh(x, y, 20 + k) * 0.8 + k * math.tau / n
        lean = 0.1 + 0.12 * (k % 2)
        h = s * (1.05 + 0.3 * hh(x, y, 24 + k))
        bx, by = x + math.cos(a) * 0.05 * s, y + math.sin(a) * 0.05 * s
        top = (bx + math.cos(a) * lean * h, by + math.sin(a) * lean * h, z + h)
        s0 = (bx + math.cos(a) * lean * h * 0.62, by + math.sin(a) * lean * h * 0.62, z + h * 0.6)
        stem(mb, (bx, by, z), s0, 0.028 * s + 0.008, closed=closed)
        # fuso: do meio da haste ate o topo, mais largo a 35%
        c = ((s0[0] + top[0]) / 2, (s0[1] + top[1]) / 2, s0[2] + (top[2] - s0[2]) * 0.38)
        octa(mb, c, 0.075 * s, top[2] - c[2], F_SPIKE, rot=a, lo=c[2] - s0[2] + 0.02)
    _count("flor_espiga")


def flower_amber(mb, x, y, z, s=1.0, closed=False):
    """dente-de-leao ambar: bola baixa (octaedro achatado) numa haste curta + roseta de 2 folhas rentes"""
    h = s * (0.45 + 0.2 * hh(x, y, 30))
    stem(mb, (x, y, z), (x, y, z + h - 0.04), 0.03 * s + 0.008, closed=closed)
    octa(mb, (x, y, z + h), 0.12 * s, 0.08 * s, F_AMBER, rot=hh(x, y, 31))
    for k in range(2):
        a = hh(x, y, 32 + k) * math.tau
        blade(mb, (x, y, z), a, 0.24 * s, 0.12 * s, 0.85, STEM[0], closed=closed)
    _count("flor_ambar")


SPECIES = {"moon": flower_moon, "bell": flower_bell, "spike": flower_spike, "amber": flower_amber}


def plant(mb, kind, x, y, z, s=1.0, closed=False, rich=False):
    if kind == "spike" and rich:
        return flower_spike(mb, x, y, z, s, closed=closed, n=3)
    SPECIES[kind](mb, x, y, z, s, closed=closed)


# ------------------------------------------------------------------ KIT: buxo, massas, canteiros, trepadeiras
def topiary(mb, c, r, m=LEAF_BOX, squash=0.9):
    """bola de buxo (icosfera de 80 faces, levemente achatada, assentada no chao)"""
    mb.ico(r, (c[0], c[1], c[2] + r * squash * 0.92), m, 1, scale=(1.0, 1.0, squash))
    _count("buxo")


def hedge_round(mb, a, b, w, h, z, m=LEAF_BOX):
    """sebe de buxo de TOPO ARREDONDADO (perfil de 8 pontos: paredes quase retas + meia-cana em 3 lances), com as
    pontas fechadas. tris 16 + 12"""
    bm = mb.bm
    ax, ay = a
    bx, by = b
    L_ = math.hypot(bx - ax, by - ay)
    if L_ < 0.05:
        return
    ux, uy = (bx - ax) / L_, (by - ay) / L_
    nx, ny = -uy, ux
    prof = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, h * 0.6), (w * 0.4, h * 0.86), (w * 0.17, h), (-w * 0.17, h),
            (-w * 0.4, h * 0.86), (-w / 2, h * 0.6)]
    rings = []
    for (px, py) in ((ax, ay), (bx, by)):
        rings.append([bm.verts.new((px + nx * u, py + ny * u, z + v)) for u, v in prof])
    allv = rings[0] + rings[1]
    k = len(prof)
    for j in range(k):
        j2 = (j + 1) % k
        u, v = (prof[j][0] + prof[j2][0]) / 2, (prof[j][1] + prof[j2][1]) / 2
        mx, my = (ax + bx) / 2, (ay + by) / 2
        ins = Vector((mx, my, z + h * 0.45))
        _face(bm, [rings[0][j], rings[0][j2], rings[1][j2], rings[1][j]], ins)
    _face(bm, list(rings[0]), Vector((ax + ux * 0.2, ay + uy * 0.2, z + h * 0.45)))
    _face(bm, list(rings[1]), Vector((bx - ux * 0.2, by - uy * 0.2, z + h * 0.45)))
    mb._post(allv, m, 0.0, 0, 1)
    _count("sebe_m", L_)


def cushion(mb, a, b, w, h, z, m):
    """massa baixa de canteiro (almofada comprida de topo arredondado): a folhagem que carrega as flores"""
    hedge_round(mb, a, b, w, h, z, m)


def leaf_clump(mb, c, r, nrm, m=LEAF_BOX, flat=0.55):
    """tufo de folhas achatado contra a parede (icosfera de 20 faces)"""
    ang = math.atan2(nrm[1], nrm[0])
    mb.ico(r, tuple(c), m, 0, scale=(flat, 1.0, 0.85), rot=(0.0, 0.0, ang))


def vine(mb, base, u, n, H, W=1.6, roses=6, socle=(0.0, 0.0)):
    """ROSEIRA TREPADEIRA encostada numa parede: base (x, y, z) = pe da PAREDE no chao, u = tangente, n = normal para
    fora (2D), socle = (quanto o soco sai, altura do soco). 2 hastes de madeira nascem na terra na frente do soco,
    sobem por ele e abrem em zigue-zague ate H; tufos de folhas de buxo nos nos e no meio dos lances, rosas brancas
    nos tufos de cima. Nada atravessa a parede: hastes a 0,2 dela, folhas de 0,12 a 0,55."""
    bx, by, bz = base
    ux, uy = u
    nx, ny = n
    sd, sh = socle

    def W3(s_, off, z):
        return Vector((bx + ux * s_ + nx * off, by + uy * s_ + ny * off, z))
    pts_all = []
    for k, side in enumerate((-1, 1)):
        pts = [W3(side * 0.12, sd + 0.18, bz - 0.05)]
        z0 = bz
        if sh > 0.05:
            pts.append(W3(side * 0.16, sd + 0.18, bz + sh + 0.06))
            z0 = bz + sh + 0.45
            pts.append(W3(side * 0.26, 0.22, z0))
        steps = 4
        for i in range(1, steps + 1):
            zc = z0 + (bz + H - z0) * i / steps
            sw = side * W * 0.5 * (0.4 + 0.6 * i / steps) * (1.0 if i % 2 else 0.6)
            pts.append(W3(sw, 0.2, zc))
        for a, b in zip(pts, pts[1:]):
            mb.rod(tuple(a), tuple(b), 0.055 if k == 0 else 0.045, STEM_W, n=4)
        pts_all.append(pts)
    spots = []
    for pts in pts_all:
        for i in range(1, len(pts)):
            a, b = pts[i - 1], pts[i]
            if b.z < bz + sh + 0.3:
                continue
            for t in ((0.5, 1.0) if (b - a).length > 1.0 else (1.0,)):
                spots.append(a + (b - a) * t)
    spots.sort(key=lambda p: p.z)
    for i, p in enumerate(spots):
        r = 0.42 + 0.1 * hh(p.x, p.y, 40)
        leaf_clump(mb, (p.x + nx * 0.16, p.y + ny * 0.16, p.z), r, (nx, ny))
        if i % 2 == 0:
            # folhas de lado (a trepadeira abre em leque, nao e um cordao)
            sg = 1 if i % 4 == 0 else -1
            leaf_clump(mb, (p.x + nx * 0.14 + ux * 0.5 * sg, p.y + ny * 0.14 + uy * 0.5 * sg, p.z - 0.25), r * 0.8,
                       (nx, ny))
    top = [p for p in spots if p.z > bz + H * 0.4]
    for i, p in enumerate(top[-roses:] if roses else []):
        sg = 1 if i % 2 else -1
        c = (p.x + nx * 0.36 + ux * 0.1 * sg, p.y + ny * 0.36 + uy * 0.1 * sg, p.z + 0.12)
        pent_bud(mb, c, 0.16, (nx * 0.8, ny * 0.8, 0.6), hh(p.x, p.y, 41) * 2, F_MOON)
    _count("trepadeiras")


def flat_wall(G, base, u, n, s0, H, z0=1.2, span=0.7, tol=0.2, want=None):
    """a coluna da trepadeira em s0 cai numa parede PLANA (sem janela/postigo/contraforte)? raios horizontais de fora
    para dentro em 3 colunas x 4 alturas; devolve a distancia media da parede ao pe (off) ou None"""
    bx, by, bz = base
    ds = []
    for ds_ in (-span, 0.0, span):
        for zz in (z0, z0 + (H - z0) * 0.35, z0 + (H - z0) * 0.7, H - 0.1):
            p = (bx + u[0] * (s0 + ds_) + n[0] * 3.0, by + u[1] * (s0 + ds_) + n[1] * 3.0, bz + zz)
            h = G.horiz(p, (-n[0], -n[1], 0.0), 6.0)
            if h is None or (want and not h[2].startswith(want)):
                if DEBUG:
                    print("GARDEN_DBG parede s=%.2f z=%.2f sem acerto (%s)" % (s0 + ds_, zz, h and h[2]))
                return None
            ds.append(3.0 - ((h[0].x - p[0]) * -n[0] + (h[0].y - p[1]) * -n[1]))
    if max(ds) - min(ds) > tol:
        if DEBUG:
            print("GARDEN_DBG parede s=%.2f irregular %s" % (s0, [round(d, 2) for d in ds]))
        return None
    return sum(ds) / len(ds)


def bed(mb, P, s0, s1, off0, dp, zg, h=0.4):
    """canteiro de cantaria baixa: terra ate zg + h - 0,08 e bordadura (frente + 2 lados; o fundo e a parede)
    P(s, off, z) -> ponto mundo; yaw vem da tangente. Devolve a funcao do plano de plantio (s, t 0..1)"""
    pa, pb = P(s0, off0, zg), P(s1, off0, zg)
    yaw = math.atan2(pb.y - pa.y, pb.x - pa.x)
    Ls = s1 - s0
    cs = (s0 + s1) / 2
    c = P(cs, off0 + dp / 2, zg + (h - 0.08) / 2 - 0.02)
    mb.box((Ls - 0.1, dp - 0.1, h - 0.04), tuple(c), (0, 0, yaw), SOIL, 0.0)
    # bordadura em pecas (~1,6) com junta de 0,05 e chanfro pequeno
    t = 0.28
    nb = max(1, int(round(Ls / 1.6)))
    for k in range(nb):
        a0 = s0 + Ls * k / nb + (0.025 if k else 0.0)
        a1 = s0 + Ls * (k + 1) / nb - (0.025 if k < nb - 1 else 0.0)
        cc = P((a0 + a1) / 2, off0 + dp - t / 2, zg + h / 2 - 0.03)
        mb.box((a1 - a0, t, h + 0.06), tuple(cc), (0, 0, yaw), CURB, 0.04)
    for sx in (s0, s1):
        inset = t / 2 if sx == s0 else -t / 2
        cc = P(sx + inset, off0 + (dp - t) / 2, zg + h / 2 - 0.03)
        mb.box((t, dp - t - 0.05, h + 0.06), tuple(cc), (0, 0, yaw), CURB, 0.04)
    _count("canteiros")
    zt = zg + h - 0.08

    def spot(sv, tv):
        """s ao longo, tv 0 (parede) .. 1 (bordadura)"""
        return P(sv, off0 + 0.12 + (dp - t - 0.24) * tv, zt)
    return spot


# ------------------------------------------------------------------ jardim formal (canteiros do patio do castelo)
def formal_bed(ms, mg, xa, xb, ya, yb, zg, outer=-1):
    """compartimento do jardim de lua: bordadura baixa de cantaria sobre o cascalho, terra e 3 FAIXAS de cor ao longo
    de x (almofada de folhagem + flores): lavanda azul junto da sebe de fora, massa de flores-da-lua no meio,
    campanulas junto do caminho. outer = lado (-1 = y baixo, +1 = y alto) onde fica a sebe de fora.
    ms = objeto das pedras (patio), mg = objeto das plantas."""
    t, hc = 0.2, 0.22
    for (p0, p1) in (((xa, ya), (xb, ya + t)), ((xa, yb - t), (xb, yb)), ((xa, ya + t), (xa + t, yb - t)),
                     ((xb - t, ya + t), (xb, yb - t))):
        ms.box2((p0[0], p0[1], zg - 0.02), (p1[0], p1[1], zg + hc), CURB, 0.03)
    zt = zg + 0.14
    ms.box2((xa + t, ya + t, zg - 0.02), (xb - t, yb - t, zt), SOIL, 0.0)
    D = yb - ya - 2 * t
    bands = [(0.2, "spike"), (0.52, "moon"), (0.83, "bell")]
    for tv, kind in bands:
        y = (ya + t + D * tv) if outer < 0 else (yb - t - D * tv)
        a, b = (xa + t + 0.2, y), (xb - t - 0.2, y)
        if kind == "spike":
            cushion(mg, a, b, 0.62, 0.36, zt - 0.04, BLADE_M)
            n = int((b[0] - a[0]) / 0.42)
            for k in range(n):
                x = a[0] + (b[0] - a[0]) * (k + 0.5) / n
                yy = y + (0.08 if k % 2 else -0.08)
                top = (x + 0.05 * (1 if k % 2 else -1), yy, zt + 1.1 + 0.14 * hh(x, yy, 3))
                s0 = (x, yy, zt + 0.5)
                stem(mg, (x, yy, zt + 0.2), s0, 0.03)
                c = ((s0[0] + top[0]) / 2, yy, s0[2] + (top[2] - s0[2]) * 0.38)
                octa(mg, c, 0.095, top[2] - c[2], F_SPIKE, rot=0.4 * k, lo=c[2] - s0[2] + 0.02)
        elif kind == "moon":
            cushion(mg, a, b, 0.86, 0.4, zt - 0.04, BLADE_D)
            n = int((b[0] - a[0]) / 0.48)
            for k in range(n):
                x = a[0] + (b[0] - a[0]) * (k + 0.5) / n
                yy = y + (0.2 if k % 2 else -0.2) + 0.05 * math.sin(k * 2.1)
                star_head(mg, (x, yy, zt + 0.36 + (0.05 if k % 3 == 0 else 0.0)), 0.3,
                          (0.1 * math.sin(k), -0.2 + (0.25 if k % 2 else -0.1), 1.0), 0.6 * k)
        else:
            cushion(mg, a, b, 0.66, 0.4, zt - 0.04, BLADE_M)
            n = int((b[0] - a[0]) / 0.8)
            for k in range(n):
                x = a[0] + (b[0] - a[0]) * (k + 0.5) / n
                flower_bell(mg, x, y + (0.1 if k % 2 else -0.1), zt + 0.26, 0.9)
    _count("canteiro_formal")


def hedge_roses(mg, a, b, zt, step=2.1, side=0.0):
    """rosas brancas ao longo do topo de uma sebe de buxo (roseira entremeada)"""
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(L_ / step))
    for k in range(n):
        t = (k + 0.5) / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        pent_bud(mg, (x, y + side, zt + 0.02), 0.15, (0.2 * math.sin(k * 1.3), 0.2 * math.cos(k * 1.7), 1.0),
                 0.9 * k, F_MOON)
    _count("rosas_sebe", n)


# ------------------------------------------------------------------ plantio em faixas (canteiros, floreiras)
def band_row(mb, spot, sa, sb, tv, kind, step, s=1.0, closed=False, phase=0.0):
    """fileira de uma especie ao longo do canteiro (s de sa a sb) na profundidade tv, passo 'step' (desencontrado
    pela fase: fileiras vizinhas nao alinham)"""
    n = max(1, int((sb - sa) / step))
    for k in range(n):
        sv = sa + (sb - sa) * (k + 0.5 + phase) / (n + 0.5)
        p = spot(sv, tv)
        plant(mb, kind, p.x, p.y, p.z, s, closed=closed)


# ------------------------------------------------------------------ floreiras de janela (sg_village.window_box)
# tema por casa (variacao DIRIGIDA): 1 flor-da-lua e folhas pendentes, 3 campanulas, 4 lavanda, 6 ambar + lua,
# 9 "cheia" (as 3 especies frias)
BOX_THEME = {1: ("moon", "bell"), 3: ("bell", "moon"), 4: ("spike", "spike"), 6: ("amber", "moon"),
             9: ("moon", "bell", "spike")}


def trail(mb, a, b, m=BLADE_D):
    """fio de folhagem pendente (hera): haste do rebordo ate b (abaixo) com 3 folhinhas (bipiramides achatadas)"""
    a, b = Vector(a), Vector(b)
    stem(mb, b, a + Vector((0, 0, 0.05)), 0.03, m=m, closed=True)
    for t in (0.35, 0.68, 1.0):
        p = a + (b - a) * t
        pent_bud(mb, p, 0.13 if t < 1 else 0.16, (0.3, 0.3, 1.0), t * 5.0, m, up=0.35, down=0.35)


def house_of(p):
    best, bi = 1e9, 0
    for i, (x, y, w, d, deg, z) in enumerate(L.HOUSE_LOTS):
        dd = math.hypot(p[0] - x, p[1] - y)
        if dd < best:
            best, bi = dd, i
    return bi


def window_box_planting(mb, f, s, zb, w):
    """a floreira pendurada sob o peitoril (sg_village.window_box): terra rente ao rebordo, ALMOFADA de folhagem que
    enche a caixa, as flores da CASA por cima (tema dirigido: BOX_THEME, ciclo fixo), laminas atras e folhas
    PENDENTES transbordando a frente. f = Face da casa (P(s, off, z) com z relativo), zb = centro da caixa.
    Objeto com recalc de normais: pecas fechadas."""
    theme = BOX_THEME.get(house_of(f.P(s, 0.0, zb)), ("moon", "bell"))
    nv = f.nvec()
    STEM[0] = BLADE_D
    t0 = _mbtris(mb)
    zs = zb + 0.18                                                        # nivel da terra
    f.box(mb, s, 0.72, zs - 0.02, w + 0.28, 0.46, 0.06, SOIL)
    a, b = f.P(s - w / 2 + 0.02, 0.7, zs - 0.06), f.P(s + w / 2 - 0.02, 0.7, zs - 0.06)
    hedge_round(mb, (a.x, a.y), (b.x, b.y), 0.44, 0.3, a.z, BLADE_D)
    n = max(4, int(round(w / 0.44)))
    for k in range(n):
        u = -w / 2 + 0.1 + (w - 0.2) * (k + 0.5) / n
        kind = theme[k % len(theme)]
        pf = f.P(s + u, 0.66 + (0.12 if k % 2 else -0.04), zs + 0.1)
        plant(mb, kind, pf.x, pf.y, pf.z, 0.68, closed=True)
        # folhas pendentes: um fio caindo por cima do rebordo a cada 2 posicoes (comprimento alternado)
        if k % 2 == 0:
            trail(mb, f.P(s + u, 0.95, zb + 0.3), f.P(s + u + 0.08, 1.12, zb - (0.62 if k % 4 == 0 else 0.4)))
    for k in range(2):
        u = -w / 2 + w * (k + 0.5) / 2
        pb = f.P(s + u, 0.5, zs)
        blade(mb, (pb.x, pb.y, pb.z), f.yaw + math.pi / 2 + (k - 1) * 0.3, 0.55, 0.12, 0.2, BLADE_D, closed=True)
    STEM[0] = BLADE_M
    _count("floreiras")
    _count("tris_floreiras", _mbtris(mb) - t0)


def ground_planter_planting(mb, f2, zs, span):
    """floreira de chao (sg_village.ground_planter, casa 7): o mesmo plantio, campanulas e flores-da-lua"""
    nv = f2.nvec()
    STEM[0] = BLADE_D
    t0 = _mbtris(mb)
    n = 4
    for k in range(n):
        u = -span / 2 + span * (k + 0.5) / n
        p = f2.P(u, 0.38, zs - 0.12)
        leaf_clump(mb, (p.x, p.y, p.z), 0.3, (nv.x, nv.y), m=BLADE_D, flat=0.6)
        pb = f2.P(u, -0.12, zs)
        blade(mb, (pb.x, pb.y, pb.z), f2.yaw + math.pi / 2, 0.55, 0.1, 0.2, BLADE_D, closed=True)
        pf = f2.P(u + 0.08, 0.12, zs)
        plant(mb, "bell" if k % 2 == 0 else "moon", pf.x, pf.y, pf.z, 0.7, closed=True)
    STEM[0] = BLADE_M
    _count("floreiras_chao")
    _count("tris_floreiras_chao", _mbtris(mb) - t0)


# ------------------------------------------------------------------ o chao (raios com o MATERIAL da face)
class Ground:
    SKIP = ("COL_", "SG_Sky_", "PREVIEW_", "SCALE_", "CAM_", "L_", "SG_Veg_", "VFX_", "GATE_")

    def __init__(self, box, only=None):
        x0, y0, x1, y1 = box
        vs, tris, owner, mats = [], [], [], []
        self.names, self.mnames = [], []
        self.ok = False
        base = 0
        for o in bpy.data.objects:
            if o.type != "MESH" or o.name.startswith(self.SKIP) or o.hide_render or not o.data.polygons:
                continue
            if only and not o.name.startswith(only):
                continue
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            if max(v.x for v in bb) < x0 or min(v.x for v in bb) > x1 or max(v.y for v in bb) < y0 or \
                    min(v.y for v in bb) > y1:
                continue
            me = o.data
            me.calc_loop_triangles()
            nv = len(me.vertices)
            co = np.empty(nv * 3, dtype=np.float64)
            me.vertices.foreach_get("co", co)
            co = co.reshape(nv, 3)
            M = np.array(o.matrix_world)
            co = co @ M[:3, :3].T + M[:3, 3]
            nt = len(me.loop_triangles)
            tv = np.empty(nt * 3, dtype=np.int64)
            me.loop_triangles.foreach_get("vertices", tv)
            mi = np.empty(nt, dtype=np.int64)
            me.loop_triangles.foreach_get("material_index", mi)
            names = [(m.name if m else "") for m in me.materials] or [""]
            moff = len(self.mnames)
            self.mnames.extend(names)
            tris.append(tv.reshape(nt, 3) + base)
            vs.append(co)
            owner.append(np.full(nt, len(self.names), dtype=np.int32))
            mats.append(np.minimum(mi, len(names) - 1) + moff)
            self.names.append(o.name)
            base += nv
        if not vs:
            self.bvh = None
            self.grass = np.zeros(1, dtype=bool)
            return
        self.ok = True
        V = np.concatenate(vs)
        T = np.concatenate(tris)
        self.owner = np.concatenate(owner)
        self.mat = np.concatenate(mats)
        self.bvh = BVHTree.FromPolygons(V.tolist(), T.tolist(), all_triangles=True)
        self.grass = np.array([fm_lib.family_of(n).startswith("Grass_SG") or n.startswith("Grass_SG")
                               for n in self.mnames], dtype=bool)

    def down(self, x, y, z0, dist=40.0):
        if self.bvh is None:
            return None
        loc, nrm, idx, d = self.bvh.ray_cast(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), dist)
        if loc is None:
            return None
        return loc.z, nrm, int(idx)

    def is_grass(self, idx):
        return bool(self.grass[self.mat[idx]])

    def inside_solid(self, x, y, z):
        """dentro de um solido fechado? (o raio para cima bate numa face virada para cima = por dentro)"""
        if self.bvh is None:
            return False
        loc, nrm, idx, d = self.bvh.ray_cast(Vector((x, y, z + 0.03)), Vector((0.0, 0.0, 1.0)), 30.0)
        return loc is not None and nrm.z > 0.2

    def horiz(self, p, d, dist=6.0):
        if self.bvh is None:
            return None
        loc, nrm, idx, dd = self.bvh.ray_cast(Vector(p), Vector(d), dist)
        if loc is None:
            return None
        return loc, nrm, self.names[int(self.owner[idx])]


# ------------------------------------------------------------------ planta: o que NUNCA recebe grama
def _in_rot_rect(x, y, cx, cy, deg, hl, hw):
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return abs(u) < hl and abs(v) < hw


STREET_POLYS = None
STREET_QA = None


def _streets_qa():
    global STREET_QA
    if STREET_QA is None:
        STREET_QA = [(SL.ccw(SL.ribbon_poly(pts, w / 2 + 0.95)), z) for pts, w, z in L.STREETS]
    return STREET_QA


def _streets():
    global STREET_POLYS
    if STREET_POLYS is None:
        STREET_POLYS = []
        for pts, w, z in L.STREETS:
            # rua + meio-fio + terra batida do P2 (0,95 alem da borda)
            STREET_POLYS.append((SL.ccw(SL.ribbon_poly(pts, w / 2 + 1.3)), z))
    return STREET_POLYS


def plan_blocked(x, y, z):
    """pisos/estruturas REAIS da planta para o QA (a mascara do gramado usa as mesmas regras com folga maior):
    rua + meio-fio + terra batida (0,95), praca, escada + banzos, casa + soco (0,5), alquimia, pontes, cachoeiras"""
    for poly, zs in _streets_qa():
        if abs(zs - z) < 3.0 and L.point_in_poly(x, y, poly):
            return "rua"
    if math.hypot(x - L.PLAZA_C[0], y - L.PLAZA_C[1]) < L.PLAZA_R + 0.5:
        return "praca"
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        ln = tread * n
        cx, cy = foot[0] + math.cos(a) * ln / 2, foot[1] + math.sin(a) * ln / 2
        if _in_rot_rect(x, y, cx, cy, deg, ln / 2 + 0.6, w / 2 + 1.2):
            return "escada"
    for hx, hy, w, d, deg, zz in L.HOUSE_LOTS:
        if abs(zz - z) < 3.0 and _in_rot_rect(x, y, hx, hy, deg, d / 2 + 0.5, w / 2 + 0.5):
            return "casa"
    if math.hypot(x - L.CRAFT_C[0], y - L.CRAFT_C[1]) < L.CRAFT_R + 0.3:
        return "alquimia"
    a0, a1, sw = L.SUMMON_BRIDGE
    if min(a0[0], a1[0]) - 1.0 < x < max(a0[0], a1[0]) + 1.0 and abs(y - a0[1]) < sw / 2 + 1.5:
        return "ponte"
    ex, ey = L.EXIT_START
    if x > ex - 2.0 and abs(y - ey) < L.EXIT_W / 2 + 2.0:
        return "ponte"
    for wx, wy, wz, deg in L.WATERFALLS:
        if math.hypot(x - wx, y - wy) < 8.0:
            return "agua"
    x0, y0, x1, y1 = L.MINE_RECT
    if x0 - 4 < x < x1 + 4 and y0 - 8 < y < y1 + 4:
        return "salao"
    return None


def _pip_grid(X, Y, poly):
    ins = np.zeros(X.shape, dtype=bool)
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        dy = (yj - yi) or 1e-9
        ins ^= ((yi > Y) != (yj > Y)) & (X < (xj - xi) * (Y - yi) / dy + xi)
        j = i
    return ins


def _rot_rect_grid(X, Y, cx, cy, deg, hl, hw):
    a = math.radians(deg)
    dx, dy = X - cx, Y - cy
    u = dx * math.cos(a) + dy * math.sin(a)
    v = -dx * math.sin(a) + dy * math.cos(a)
    return (np.abs(u) < hl) & (np.abs(v) < hw)


def plan_mask(X, Y, Z):
    """a mesma regra do plan_blocked, na grade inteira (numpy)"""
    out = []
    st = np.zeros(X.shape, dtype=bool)
    for poly, zs in _streets():
        st |= (np.abs(Z - zs) < 3.0) & _pip_grid(X, Y, poly)
    out.append(("rua", st))
    out.append(("praca", np.hypot(X - L.PLAZA_C[0], Y - L.PLAZA_C[1]) < L.PLAZA_R + 1.0))
    es = np.zeros(X.shape, dtype=bool)
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        ln = tread * n
        es |= _rot_rect_grid(X, Y, foot[0] + math.cos(a) * ln / 2, foot[1] + math.sin(a) * ln / 2, deg, ln / 2 + 1.2,
                             w / 2 + 1.6)
    out.append(("escada", es))
    cs = np.zeros(X.shape, dtype=bool)
    for hx, hy, w, d, deg, zz in L.HOUSE_LOTS:
        cs |= (np.abs(Z - zz) < 3.0) & _rot_rect_grid(X, Y, hx, hy, deg, d / 2 + 0.9, w / 2 + 0.9)
    out.append(("casa", cs))
    out.append(("alquimia", np.hypot(X - L.CRAFT_C[0], Y - L.CRAFT_C[1]) < L.CRAFT_R + 0.8))
    a0, a1, sw = L.SUMMON_BRIDGE
    ex, ey = L.EXIT_START
    out.append(("ponte", ((X > min(a0[0], a1[0]) - 1.0) & (X < max(a0[0], a1[0]) + 1.0) & (np.abs(Y - a0[1]) < sw / 2 + 1.5))
                | ((X > ex - 2.0) & (np.abs(Y - ey) < L.EXIT_W / 2 + 2.0))))
    ag = np.zeros(X.shape, dtype=bool)
    for wx, wy, wz, deg in L.WATERFALLS:
        ag |= np.hypot(X - wx, Y - wy) < 8.0
    out.append(("agua", ag))
    return out


# ------------------------------------------------------------------ mascara do gramado + campo de distancia
RES = 0.5
BOX_VIL = (-126.0, -176.0, 162.0, -2.0)
CAP = 8.0


class Lawn:
    def __init__(self, G, box=BOX_VIL):
        self.G = G
        x0, y0, x1, y1 = box
        self.x0, self.y0 = x0, y0
        nx, ny = int((x1 - x0) / RES), int((y1 - y0) / RES)
        self.nx, self.ny = nx, ny
        mask = np.zeros((ny, nx), dtype=bool)
        zz = np.zeros((ny, nx), dtype=np.float32)
        why = {}
        for j in range(ny):
            y = y0 + (j + 0.5) * RES
            for i in range(nx):
                x = x0 + (i + 0.5) * RES
                h = G.down(x, y, P2 + 3.2, 16.0)
                if h is None:
                    continue
                z, nrm, idx = h
                if nrm.z < 0.9 or not G.is_grass(idx):
                    continue
                mask[j, i] = True
                zz[j, i] = z
        # planta (vetorizado na grade) e solidos (raio para cima so nas celulas que sobraram)
        X = x0 + (np.arange(nx) + 0.5) * RES
        Y = y0 + (np.arange(ny) + 0.5) * RES
        XX, YY = np.meshgrid(X, Y)
        ZL = np.where(zz > 40.0, zz, P1)
        for b, blk in plan_mask(XX, YY, ZL):
            hit = blk & mask
            why[b] = why.get(b, 0) + int(hit.sum())
            mask &= ~blk
        js, is_ = np.nonzero(mask)
        for j, i in zip(js.tolist(), is_.tolist()):
            x = x0 + (i + 0.5) * RES
            y = y0 + (j + 0.5) * RES
            if G.inside_solid(x, y, float(zz[j, i])):
                mask[j, i] = False
                why["solido"] = why.get("solido", 0) + 1
        self.mask, self.z, self.why = mask, zz, why
        # distancia (studs) ate a celula de nao-grama mais proxima (dilatacao em 8 vizinhos, ate CAP)
        dist = np.full(mask.shape, CAP, dtype=np.float32)
        front = ~mask
        dist[front] = 0.0
        for k in range(1, int(CAP / RES) + 1):
            g = front.copy()
            g[1:, :] |= front[:-1, :]
            g[:-1, :] |= front[1:, :]
            g[:, 1:] |= front[:, :-1]
            g[:, :-1] |= front[:, 1:]
            if k % 2 == 0:              # diagonais a cada 2 passos: aproxima a distancia euclidiana (octogono)
                g[1:, 1:] |= front[:-1, :-1]
                g[:-1, :-1] |= front[1:, 1:]
                g[1:, :-1] |= front[:-1, 1:]
                g[:-1, 1:] |= front[1:, :-1]
            new = g & ~front
            dist[new] = k * RES
            front = g
        self.dist = dist
        gy, gx = np.gradient(dist)
        self.gx, self.gy = gx, gy
        self.route = np.full(mask.shape, 99.0, dtype=np.float32)

    def cell(self, x, y):
        i = int((x - self.x0) / RES)
        j = int((y - self.y0) / RES)
        if 0 <= i < self.nx and 0 <= j < self.ny:
            return j, i
        return None

    def at(self, x, y):
        c = self.cell(x, y)
        if c is None or not self.mask[c]:
            return None
        return float(self.z[c]), float(self.dist[c])

    def out_dir(self, x, y):
        c = self.cell(x, y)
        if c is None:
            return WIND
        gx, gy = float(self.gx[c]), float(self.gy[c])
        ln = math.hypot(gx, gy)
        if ln < 1e-4:
            return WIND
        return gx / ln, gy / ln

    def raster_routes(self, routes):
        """distancia ate as rotas do QA (mesmo nivel), rasterizada na grade"""
        X = self.x0 + (np.arange(self.nx) + 0.5) * RES
        Y = self.y0 + (np.arange(self.ny) + 0.5) * RES
        for pts, z in routes:
            for a, b in zip(pts, pts[1:]):
                lo_x, hi_x = min(a[0], b[0]) - 28.0, max(a[0], b[0]) + 28.0
                lo_y, hi_y = min(a[1], b[1]) - 28.0, max(a[1], b[1]) + 28.0
                i0, i1 = max(0, int((lo_x - self.x0) / RES)), min(self.nx, int((hi_x - self.x0) / RES) + 1)
                j0, j1 = max(0, int((lo_y - self.y0) / RES)), min(self.ny, int((hi_y - self.y0) / RES) + 1)
                if i0 >= i1 or j0 >= j1:
                    continue
                xx, yy = np.meshgrid(X[i0:i1], Y[j0:j1])
                dx, dy = b[0] - a[0], b[1] - a[1]
                L2 = dx * dx + dy * dy or 1e-9
                t = np.clip(((xx - a[0]) * dx + (yy - a[1]) * dy) / L2, 0.0, 1.0)
                d = np.hypot(xx - (a[0] + dx * t), yy - (a[1] + dy * t)).astype(np.float32)
                zc = self.z[j0:j1, i0:i1]
                d = np.where(np.abs(zc - z) < 3.0, d, 99.0).astype(np.float32)
                self.route[j0:j1, i0:i1] = np.minimum(self.route[j0:j1, i0:i1], d)

    def rdist(self, x, y):
        c = self.cell(x, y)
        return 99.0 if c is None else float(self.route[c])


# ------------------------------------------------------------------ objetos por zona (1 MeshPart por material)
class Beds:
    def __init__(self):
        self.mbs = {}

    def mb(self, key):
        m = self.mbs.get(key)
        if m is None:
            m = self.mbs[key] = MB("SG_Veg_Gdn_%s" % key, COLL, None, detail="near", floor=-999)
        return m

    def finish(self):
        out = []
        for k in sorted(self.mbs):
            ob = self.mbs[k].finish(recalc=False)
            if ob:
                out.append(ob)
        self.mbs.clear()
        return out


def zone_key(x, y, z):
    if z > P3 - 3.0:
        return "P2W" if x < 10.0 else "P2E"
    if y > -84.0 and z > P2 - 3.0:
        return "P2W" if x < 10.0 else "P2E"
    return "P1"


# ------------------------------------------------------------------ registro do que foi plantado (QA)
PLANTED = []        # (tipo, x, y, z, contexto)
OCC = {}            # discos ocupados por plantio dirigido (grade de 2 studs -> [(x, y, r)]): os tufos rareiam ali


def _occ(x, y, r):
    OCC.setdefault((int(math.floor(x / 2.0)), int(math.floor(y / 2.0))), []).append((x, y, r))


def _occupied(x, y, pad=0.0):
    cx, cy = int(math.floor(x / 2.0)), int(math.floor(y / 2.0))
    for i in (cx - 1, cx, cx + 1):
        for j in (cy - 1, cy, cy + 1):
            for ox, oy, r in OCC.get((i, j), ()):
                if (x - ox) ** 2 + (y - oy) ** 2 < (r + pad) ** 2:
                    return True
    return False


# ------------------------------------------------------------------ jardins das casas (variacao DIRIGIDA por casa)
# kind: 'bed' (canteiro de cantaria encostado na fachada; P1 calcado) | 'lawn' (plantio direto no gramado; P2)
# back: especie ALTA da fileira de tras (ritmo: 3 plantas e um respiro); front: especies das DERIVAS da frente (grupos de
# 3-5 flores com uma touceira baixa entre eles; as especies se revezam por grupo); vines: roseiras (fracao da
# meia-largura, a coluna anda ate cair em parede plana); box: bolas de buxo nas quinas; patch: mancha no gramado da
# frente; skip: trecho livre (balcao da loja); half: so a metade sem o torreao
HOUSE_GARDENS = {
    0: dict(kind="bed", dp=1.5, back="spike", front=("moon",), skip=(-3.2, 3.2)),                 # loja: lavanda + lua
    1: dict(kind="bed", dp=1.4, back="bell", front=("moon",)),                                    # floreiras cheias
    2: dict(kind="bed", dp=1.3, back=None, front=("bell", "moon"), vines=(-0.72, 0.72)),         # roseiras na fachada
    3: dict(kind="bed", dp=1.4, back="spike", front=("moon",), half=1),                          # meia fachada (torreao)
    4: dict(kind="bed", dp=1.5, back="spike", front=("spike", "moon")),                          # canteiro de lavanda
    5: dict(kind="bed", dp=1.4, back="moon", front=("amber", "moon"), skip=(-3.2, 3.2)),         # loja: toque ambar
    6: dict(kind="lawn", back="spike", front=("moon",), skip=(-3.2, 3.2), box=True),
    7: dict(kind="lawn", back=None, front=("moon", "bell"), box=True, patch=("moon", "bell")),
    8: dict(kind="lawn", back="bell", front=("moon",), vines=(-0.72, 0.72)),
    9: dict(kind="lawn", back="bell", front=("moon", "amber"), patch=("amber", "moon")),
    10: dict(kind="lawn", back="spike", front=("moon",), skip=(-3.2, 3.2), box=True),
}
DRIFT = (3, 4, 3, 5, 4)             # tamanho dos grupos da frente (ciclo fixo)


def plant_band(mb, pos, sa, sb, back, front, idx, ctx, closed=False):
    """fileira de tras (alta, em ritmo) + DERIVAS na frente. pos(s, tv) -> Vector (ou None fora do gramado)"""
    if back:
        n = max(1, int((sb - sa) / 0.66))
        for k in range(n):
            if k % 4 == 3:
                continue                                      # respiro do ritmo
            sv = sa + (sb - sa) * (k + 0.5) / n
            p = pos(sv, 0.22 + 0.06 * (k % 2))
            if p is not None:
                plant(mb, back, p.x, p.y, p.z, 1.0, closed=closed)
                PLANTED.append(("flor", p.x, p.y, p.z, ctx))
    sv = sa + 0.1
    g = 0
    while sv < sb - 0.3:
        cnt = DRIFT[(g + idx) % len(DRIFT)]
        kind = front[g % len(front)]
        step = 0.42 if kind != "bell" else 0.5
        for k in range(cnt):
            s_ = sv + k * step
            if s_ > sb - 0.2:
                break
            tv = 0.62 + (0.2 if k % 2 else -0.02) + 0.06 * math.sin(s_ * 3.1 + idx)
            p = pos(s_, tv)
            if p is not None:
                plant(mb, kind, p.x, p.y, p.z, 0.95 + 0.1 * (k == cnt // 2), closed=closed)
                PLANTED.append(("flor", p.x, p.y, p.z, ctx))
        sv += cnt * step + 0.2
        # respiro entre as derivas: touceira baixa de folhas
        p = pos(sv, 0.7)
        if p is not None and sv < sb - 0.2:
            clump(mb, p.x, p.y, p.z, 0.72, 5, m=BLADE_D)
        sv += 0.45
        g += 1


def house_face(idx):
    """P(s, off, z) da FACHADA da casa idx (s ao longo, off para fora a partir da parede, z relativo ao piso), a
    meia-largura e o rumo da frente (o mesmo referencial do sg_village.house)"""
    x, y, w, d, deg, z = L.HOUSE_LOTS[idx]
    a = math.radians(deg)
    fx, fy = math.cos(a), math.sin(a)
    tx, ty = fy, -fx                         # tangente (s positivo): direita de quem olha a fachada de frente
    cx, cy = x + fx * d / 2, y + fy * d / 2

    def P(s, off, zz):
        return Vector((cx + tx * s + fx * off, cy + ty * s + fy * off, z + zz))
    return P, w / 2, (fx, fy), (tx, ty), z


def house_gardens(B, lawn, G=None):
    try:
        import sg_village as VL
        specs = VL.SPECS
    except Exception:
        specs = [{} for _ in L.HOUSE_LOTS]
    for idx, g in sorted(HOUSE_GARDENS.items()):
        P, hw, fwd, tan, z0 = house_face(idx)
        spec = specs[idx] if idx < len(specs) else {}
        zkey = "P1" if z0 < P2 - 1 else ("P2W" if L.HOUSE_LOTS[idx][0] < 10 else "P2E")
        mb = B.mb(zkey)
        off0 = 0.56                                 # frente do soco (sai 0,5)
        sa, sb = -hw + 0.4, hw - 0.4
        if g.get("half"):
            tur = spec.get("turret")
            side = -tur[0] if tur else 1
            sa, sb = (0.4, hw - 0.4) if side > 0 else (-hw + 0.4, -0.4)
        spans = [(sa, sb)]
        if g.get("skip"):
            k0, k1 = g["skip"]
            spans = [(sa, min(sb, k0)), (max(sa, k1), sb)]
        spans = [(a, b) for a, b in spans if b - a > 1.2]
        ctx = "casa%d" % idx
        if g["kind"] == "bed":
            for a, b in spans:
                spot = bed(mb, P, a, b, off0, g["dp"], 0.0)
                plant_band(mb, lambda sv, tv: spot(sv, tv), a + 0.3, b - 0.3, g.get("back"), g["front"], idx, ctx)
                c = P((a + b) / 2, off0 + g["dp"] / 2, 0.0)
                PLANTED.append(("canteiro", c.x, c.y, c.z, ctx))
        else:
            def pos(sv, tv):
                q = P(sv, off0 + 0.3 + 1.25 * tv + 0.15 * math.sin(sv * 1.7 + idx), 0.0)
                h = lawn.at(q.x, q.y) if lawn else None
                if h is None:
                    return None
                _occ(q.x, q.y, 0.35)
                return Vector((q.x, q.y, h[0]))
            for a, b in spans:
                plant_band(mb, pos, a + 0.2, b - 0.2, g.get("back"), g["front"], idx, ctx)
                # pe da parede: touceiras escuras rentes ao soco (a casa "senta" no gramado)
                n = max(1, int((b - a) / 1.25))
                for k in range(n):
                    q = pos(a + (b - a) * (k + 0.5) / n, -0.12)
                    if q is not None:
                        clump(mb, q.x, q.y, q.z, 0.8 + 0.15 * (k % 2), 5, out=fwd, m=BLADE_D)
                        PLANTED.append(("tufo", q.x, q.y, q.z, ctx))
            if g.get("box"):
                for sv in (-hw - 0.1, hw + 0.1):
                    p = P(sv, off0 + 0.55, 0.0)
                    h = lawn.at(p.x, p.y) if lawn else None
                    if h is not None:
                        topiary(mb, (p.x, p.y, h[0] - 0.05), 0.62)
                        _occ(p.x, p.y, 0.8)
                        PLANTED.append(("buxo", p.x, p.y, h[0], "casa%d" % idx))
            if g.get("patch"):
                # mancha de flores num canto do gramado da frente (lado mais longe da rua transversal)
                p = P(hw - 1.6, off0 + 4.2, 0.0)
                patch(mb, lawn, p.x, p.y, 1.9, g["patch"], "casa%d" % idx)
        for fr in g.get("vines", ()):
            # altura: abaixo do cordao/balanco do 1o pavimento; a coluna precisa cair em parede PLANA (raios): anda
            # para o meio da fachada ate achar (nunca sobre janela, postigo, lanterna ou cunhal)
            st = spec.get("stories", [("stone", 6.0)]) if spec else [("stone", 6.0)]
            H = min(5.2, 1.0 + st[0][1] - 1.4)
            base = P(0.0, 0.0, 0.0)
            got = None
            for k in range(12):
                sv = fr * hw + math.copysign(0.35 * ((k + 1) // 2) * (1 if k % 2 else -1), fr)
                if G is None:
                    break
                off = flat_wall(G, (base.x, base.y, base.z), tan, fwd, sv, H, want="SG_Vil_", tol=0.3)
                if off is not None and abs(off) < 0.35:
                    got = (sv, off)
                    break
            if got is None and G is not None:
                # a fachada nao tem coluna plana desse lado: a roseira vai para a EMPENA/LATERAL do mesmo lado,
                # perto da quina da frente (o que se ve da rua)
                hx, hy, w_, d_, deg_, hz = L.HOUSE_LOTS[idx]
                sgn = 1.0 if fr > 0 else -1.0
                nrm = (tan[0] * sgn, tan[1] * sgn)
                bs = Vector((hx + nrm[0] * w_ / 2, hy + nrm[1] * w_ / 2, hz))
                for k in range(10):
                    sv2 = d_ / 2 - 1.1 - 0.4 * k
                    off = flat_wall(G, (bs.x, bs.y, bs.z), fwd, nrm, sv2, H, want="SG_Vil_", tol=0.3)
                    if off is not None and abs(off) < 0.35:
                        def PS(sv_, of_, zz_, bs=bs, nrm=nrm):
                            return Vector((bs.x + fwd[0] * sv_ + nrm[0] * of_, bs.y + fwd[1] * sv_ + nrm[1] * of_,
                                           bs.z + zz_))
                        q = PS(sv2, off, 0.0)
                        if g["kind"] == "bed":
                            spot = bed(mb, PS, sv2 - 0.8, sv2 + 0.8, 0.56, 1.0, 0.0)
                            for tv, sx in ((0.7, -0.45), (0.7, 0.45)):
                                pp = spot(sv2 + sx, tv)
                                plant(mb, "moon", pp.x, pp.y, pp.z, 0.95)
                        vine(mb, (q.x, q.y, q.z), fwd, nrm, H, W=1.5, roses=6, socle=(0.5 - off, 0.98))
                        _occ(q.x + nrm[0] * 0.8, q.y + nrm[1] * 0.8, 1.0)
                        PLANTED.append(("trepadeira", q.x, q.y, q.z, "casa%d_lateral" % idx))
                        _count("trepadeira_lateral")
                        got = "lateral"
                        break
            if got is None:
                _count("trepadeira_recusada")
                continue
            if got == "lateral":
                continue
            sv, off = got
            p = P(sv, off, 0.0)
            vine(mb, (p.x, p.y, p.z), tan, fwd, H, W=1.5, roses=6, socle=(0.5 - off, 0.98))
            _occ(p.x + fwd[0] * 0.8, p.y + fwd[1] * 0.8, 1.0)
            PLANTED.append(("trepadeira", p.x, p.y, p.z, "casa%d" % idx))


# ------------------------------------------------------------------ canteiros da fonte da praca
PLAZA_ARCS = (45.0, 135.0, 225.0, 315.0)      # meio de cada arco (os eixos 0/90/180/270 ficam livres: caminhos)
PLAZA_ARC_HALF = 27.0


def plaza_beds(B, G):
    """4 canteiros em ARCO ao pe da bacia da fonte (entre os 4 caminhos), bordadura de cantaria baixa, lavanda junto
    da bacia e derivas de flor-da-lua/campanula na frente. O raio vem da bacia REAL (raios horizontais); a volta da
    praca (anel de 12) fica livre (o canteiro termina antes de 10,2)."""
    if G is None or not G.ok:
        return 0
    cx, cy = L.PLAZA_C
    z = P1
    mb = B.mb("P1")
    rmax = 0.0
    for k in range(48):
        a = math.radians(k * 7.5)
        h = G.horiz((cx + 12.0 * math.cos(a), cy + 12.0 * math.sin(a), z + 0.35), (-math.cos(a), -math.sin(a), 0.0), 9.0)
        if h is None:
            continue
        rmax = max(rmax, math.hypot(h[0].x - cx, h[0].y - cy))
    if rmax < 5.0 or rmax > 8.8:
        _count("praca_sem_bacia")
        return 0
    r0 = rmax + 0.2
    dp = 1.25
    t = 0.26
    got = 0
    for am in PLAZA_ARCS:
        a0, a1 = math.radians(am - PLAZA_ARC_HALF), math.radians(am + PLAZA_ARC_HALF)
        nseg = 10

        def A(i):
            return a0 + (a1 - a0) * i / nseg
        # terra: setor de coroa (prisma)
        pts = [(cx + (r0 + dp) * math.cos(A(i)), cy + (r0 + dp) * math.sin(A(i))) for i in range(nseg + 1)]
        pts += [(cx + r0 * math.cos(A(i)), cy + r0 * math.sin(A(i))) for i in range(nseg, -1, -1)]
        mb.prism(SL.ccw(pts), z - 0.05, z + 0.3, SOIL)
        # bordadura: pecas no arco de fora + 2 cabeceiras radiais
        for i in range(0, nseg, 2):
            aa, ab = A(i) + 0.004, A(i + 2) - 0.004
            rm = r0 + dp - t / 2
            p0 = (cx + rm * math.cos(aa), cy + rm * math.sin(aa))
            p1 = (cx + rm * math.cos(ab), cy + rm * math.sin(ab))
            L_ = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            mb.box((L_, t, 0.44), ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z + 0.19),
                   (0, 0, math.atan2(p1[1] - p0[1], p1[0] - p0[0])), CURB, 0.04)
        for aa in (a0, a1):
            rm = r0 + (dp - t) / 2
            mb.box((dp - t, t, 0.44), (cx + rm * math.cos(aa), cy + rm * math.sin(aa), z + 0.19), (0, 0, aa), CURB, 0.04)
        # plantio: s = comprimento de arco no raio do meio, tv = de dentro (bacia) para fora
        rmid = r0 + dp / 2
        Ls = (a1 - a0) * rmid

        def pos(sv, tv, a0=a0):
            a = a0 + sv / rmid
            r = r0 + 0.15 + (dp - t - 0.3) * tv
            return Vector((cx + r * math.cos(a), cy + r * math.sin(a), z + 0.3))
        plant_band(mb, pos, 0.35, Ls - 0.35, "spike", ("moon", "bell") if am in (45.0, 225.0) else ("bell", "moon"),
                   int(am), "praca_canteiro")
        PLANTED.append(("canteiro", cx + rmid * math.cos(math.radians(am)), cy + rmid * math.sin(math.radians(am)), z,
                        "praca_canteiro"))
        got += 1
    _count("canteiros_praca", got)
    return got


# ------------------------------------------------------------------ manchas de flores (bonemeal dirigido)
def patch(mb, lawn, cx, cy, R, kinds, ctx, dens=1.0):
    """mancha: flores em espiral de filotaxia (angulo aureo) ate R, especies por ANEL (miolo = 1a especie, borda = a
    2a), mais densa no miolo; so onde ha gramado; tufos no meio"""
    ga = math.pi * (3.0 - math.sqrt(5.0))
    n = int(R * R * 2.4 * dens)
    got = 0
    for k in range(n):
        r = R * math.sqrt((k + 0.5) / n)
        a = k * ga + hh(cx, cy) * 6.0
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        h = lawn.at(x, y) if lawn else None
        if h is None or h[1] < 0.35 or lawn.rdist(x, y) < 1.3 or _occupied(x, y, 0.1):
            continue
        if plan_blocked(x, y, h[0] if h[0] > 40.0 else P1):
            continue
        kind = kinds[0] if r < R * 0.62 or len(kinds) == 1 else kinds[1]
        s = 1.15 + 0.2 * (1.0 - r / R)             # acima do capim cheio (a flor le por cima dos tufos)
        plant(mb, kind, x, y, h[0], s, rich=True)
        PLANTED.append(("flor", x, y, h[0], ctx))
        _occ(x, y, 0.3)
        got += 1
    _count("manchas")
    return got


# ------------------------------------------------------------------ o campo de tufos
TUFT_TARGET = 48000          # tris dos tufos do gramado (o resto do orcamento: flores, canteiros, patio, floreiras)


def scatter(B, lawn, trees, lamps):
    """o CAMPO (rodada 2, 2026-09-30: "o gramado tem de ficar COBERTO, como o bonemeal"):
      - VISIVEL (a menos de 25 do eixo de uma rota): grade de ~1,05 com tremor, quase todo ponto recebe tufo -> os
        tufos quase se tocam e o chao so aparece entre eles; longe das rotas: ralo (so bordas);
      - 2 tamanhos: TOUCEIRA grande (7-9 laminas) so nas BORDAS (muro, rua, casa, canteiro), ao pe das arvores, dos
        postes e nos focos do campo de manchas; no miolo, o tufo LOD de 3-4 laminas largas (6-8 tris);
      - tons CLAROS sobre o chao (o capim do bonemeal e mais claro que o bloco): meio / luar na maioria, escuro so na
        sombra (pe de arvore, junto do muro); ZERO em rota (corredor de 0,9, esmaecendo ate 2,2)."""
    cand = []
    SP = 1.25
    X0, Y0 = lawn.x0, lawn.y0
    nx = int(lawn.nx * RES / SP)
    ny = int(lawn.ny * RES / SP)
    for jj in range(ny):
        for ii in range(nx):
            x = X0 + (ii + 0.5) * SP + (hh(ii, jj, 1) - 0.5) * SP * 0.7
            y = Y0 + (jj + 0.5) * SP + (hh(jj, ii, 2) - 0.5) * SP * 0.7
            h = lawn.at(x, y)
            if h is None:
                continue
            z, de = h
            if de < 0.45:
                continue
            rd = lawn.rdist(x, y)
            if rd < 0.9:
                continue
            if plan_blocked(x, y, z if z > 40.0 else P1):
                continue
            wild = z < P2 - 3.0
            if wild:
                if y > -80.0:
                    continue
                near = False
                for k in range(6):
                    aa = k * math.tau / 6
                    if L.zone_of(x + math.cos(aa) * 9.0, y + math.sin(aa) * 9.0) is not None:
                        near = True
                        break
                if not near:
                    continue
            edge = max(0.0, min(1.0, 1.0 - (de - 0.7) / 2.4))
            tree = 0.0
            for tx, ty, tz, tr, th in trees:
                dd = math.hypot(x - tx, y - ty)
                if dd < tr + 2.4:
                    tree = max(tree, 1.0 - max(0.0, dd - 0.8) / (tr + 1.6))
            lamp = 0.0
            for lx, ly in lamps:
                dd = math.hypot(x - lx, y - ly)
                if dd < 3.2:
                    lamp = max(lamp, 1.0 - dd / 3.2)
            f = field(x, y)
            if rd < 25.0 and not wild:
                p = 0.9 + 0.08 * edge
            else:
                p = 0.06 + 0.5 * edge + 0.4 * tree + 0.3 * max(0.0, f - 0.55)
                if wild:
                    p *= 0.5
            if rd < 2.2:
                p *= (rd - 0.9) / 1.3
            if _occupied(x, y):
                p *= 0.3
            p = min(0.98, p)
            cand.append((x, y, z, de, p, edge, tree, f, wild, rd, lamp))

    def form(c):
        x, y, z, de, p, edge, tree, f, wild, rd, lamp = c
        big = edge > 0.75 or tree > 0.45 or lamp > 0.4 or f > 0.86
        if big:
            s = 0.9 + 0.5 * edge + 0.36 * tree + 0.2 * max(0.0, f - 0.5)
            s *= 0.9 + 0.2 * hh(x, y, 3)
            s = max(0.8, min(1.6, s))
            n = 9 if s > 1.3 else (8 if s > 1.05 else 7)
        else:
            s = (0.78 + 0.3 * f) * (0.88 + 0.26 * hh(x, y, 3))
            n = 4 if hh(x, y, 4) < 0.3 else 3
        return s, n, 2 * n, big
    forms = [form(c) for c in cand]
    exp = sum(c[4] * fm[2] for c, fm in zip(cand, forms))
    k = min(1.0, TUFT_TARGET / max(1.0, exp))
    placed = 0
    nbig = 0
    for c, fm in zip(cand, forms):
        x, y, z, de, p, edge, tree, f, wild, rd, lamp = c
        if hh(x, y, 9) >= p * k:
            continue
        s, n, tris, big = fm
        out = lawn.out_dir(x, y) if de < 3.5 else WIND
        t = field2(x, y) + 0.3 * (hh(x, y, 17) - 0.5) - 0.5 * tree - (0.15 if de < 1.0 else 0.0)
        m = BLADE_L if (t > 0.45 and not wild and y > -84.0) else (BLADE_M if t > 0.12 else BLADE_D)
        clump(B.mb(zone_key(x, y, z)), x, y, z, s, n, out=out, m=m, wide=(not big))
        PLANTED.append(("tufo", x, y, z, "gramado" if not wild else "ombro"))
        placed += 1
        nbig += 1 if big else 0
    _count("touceiras_grandes", nbig)
    return placed, k, len(cand)


# ------------------------------------------------------------------ manchas de tom no gramado base
def lawn_tones(lawn, trees):
    """pocas escuras sob as arvores do gramado e clareiras de luar no gramado aberto: poligonos irregulares rentes
    (0,05 acima do chao: sem z-fight) que so existem onde TODO o contorno cai no gramado"""
    mb = MB("SG_Veg_Gdn_LawnTone", COLL, None, detail="far", floor=-999)
    n = 0

    def blob(cx, cy, R, z, m, k):
        for tries in range(4):
            pts = []
            NV = 16
            for i in range(NV):
                a = i * math.tau / NV + hh(cx, cy, k) * 2.0
                rr = R * (0.62 + 0.25 * math.sin(3.0 * a + hh(cx, cy, k + 2) * 6.0) + 0.3 * hh(cx + i, cy - i, k + 1))
                pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
            ok = True
            for (px, py) in pts + [(cx, cy)]:
                h = lawn.at(px, py)
                if h is None or abs(h[0] - z) > 0.3 or lawn.rdist(px, py) < 0.5:
                    ok = False
                    break
            if ok:
                bm = mb.bm
                top = [bm.verts.new((px, py, z + 0.05)) for px, py in pts]
                bot = [bm.verts.new((px, py, z - 0.05)) for px, py in pts]
                ins = Vector((cx, cy, z))
                _face(bm, top, ins)
                for i in range(NV):
                    j = (i + 1) % NV
                    _face(bm, [top[i], top[j], bot[j], bot[i]], ins)
                mb._post(top + bot, m, 0.0, 0, 1)
                return True
            R *= 0.78
        return False
    for tx, ty, tz, tr, th in trees:
        h = lawn.at(tx + 0.6, ty + 0.6)
        if h and tz > P2 - 3.0 and blob(tx, ty, tr * 1.05, h[0], LAWN_D, 50):
            n += 1
    # clareiras de luar: maximos do campo nos gramados abertos do P2 (grade grossa, os 8 maiores, bem separados)
    cands = []
    for gy in np.arange(-80.0, -8.0, 4.0):
        for gx in np.arange(-116.0, 150.0, 4.0):
            h = lawn.at(gx, gy)
            if h is None or h[1] < 3.5:
                continue
            cands.append((field2(gx, gy) + 0.3 * field(gx, gy), gx, gy, h[0]))
    cands.sort(reverse=True)
    chosen = []
    for v, gx, gy, z in cands:
        if all(math.hypot(gx - a, gy - b) > 20.0 for a, b in chosen):
            if blob(gx, gy, 5.0 + 2.0 * hh(gx, gy, 61), z, LAWN_L, 60):
                chosen.append((gx, gy))
                n += 1
        if len(chosen) >= 12:
            break
    # pocas escuras onde o capim adensa (maximos do campo das manchas), fora das clareiras
    cands = sorted(((field(gx, gy), gx, gy, z) for v, gx, gy, z in cands), reverse=True)
    dark = []
    for v, gx, gy, z in cands:
        if all(math.hypot(gx - a, gy - b) > 18.0 for a, b in dark) and                 all(math.hypot(gx - a, gy - b) > 11.0 for a, b in chosen):
            if blob(gx, gy, 3.5 + 1.5 * hh(gx, gy, 71), z, LAWN_D, 80):
                dark.append((gx, gy))
                n += 1
        if len(dark) >= 10:
            break
    mb.finish(recalc=False)
    return n


# ------------------------------------------------------------------ canteiros das arvores (piso calcado)
def plant_pits(B, pits):
    """o canteiro octogonal da arvore em piso calcado (sg_veg.tree_pit): anel de tufos e 3 flores-da-lua na terra"""
    for x, y, zt in pits:
        mb = B.mb(zone_key(x, y, zt))
        for k in range(7):
            a = k * math.tau / 7 + 0.3
            r = 1.12 + 0.12 * (k % 2)
            px, py = x + r * math.cos(a), y + r * math.sin(a)
            clump(mb, px, py, zt, 0.9 + 0.15 * (k % 3 == 0), 6, out=(math.cos(a), math.sin(a)),
                  m=BLADE_M if k % 2 else BLADE_D)
            PLANTED.append(("tufo", px, py, zt, "canteiro_arvore"))
        for k in range(3):
            a = k * math.tau / 3 + 1.0
            px, py = x + 0.78 * math.cos(a), y + 0.78 * math.sin(a)
            flower_moon(mb, px, py, zt, 0.9)
            PLANTED.append(("flor", px, py, zt, "canteiro_arvore"))


# ------------------------------------------------------------------ roseiras nos muros do patio do castelo
COURT_VINES = (-34.0, -26.0, 26.0, 34.0)      # |x| 7..21 e a torre redonda do portao


def court_vines(mb):
    """roseiras trepadeiras na face interna da muralha (y ~ -3), atras dos canteiros do patio (chamado pelo
    sg_court.court): acha a face por raio (so malhas do castelo) e confere que a coluna e parede PLANA; se o castelo
    ainda nao foi montado (estudio de outra zona), nao planta"""
    G = Ground((-60.0, -14.0, 60.0, 6.0), only=("SG_Cas_",))
    if not G.ok:
        return 0
    got = 0
    for x in COURT_VINES:
        hit = G.horiz((x, 1.5, P3 + 2.0), (0.0, -1.0, 0.0), 8.0)
        if hit is None:
            continue
        yw = hit[0].y
        H = 6.5
        for dx in (0.0, 0.8, -0.8, 1.6, -1.6):
            off = flat_wall(G, (x + dx, yw, P3), (1.0, 0.0), (0.0, 1.0), 0.0, H, z0=3.0, span=0.8)
            if off is None:
                continue
            # soco/embasamento da muralha: quanto sai (raio rente ao chao) e ate onde sobe
            h0 = G.horiz((x + dx, yw + 3.0, P3 + 0.4), (0.0, -1.0, 0.0), 6.0)
            sd = max(0.0, (h0[0].y - (yw + off)) if h0 else 0.0)
            sh = 0.0
            if sd > 0.1:
                for zz in (0.8, 1.2, 1.6, 2.0, 2.4, 2.8):
                    h1 = G.horiz((x + dx, yw + 3.0, P3 + zz), (0.0, -1.0, 0.0), 6.0)
                    if h1 and h1[0].y - (yw + off) > 0.1:
                        sh = zz
            vine(mb, (x + dx, yw + off, P3), (1.0, 0.0), (0.0, 1.0), H, W=2.0, roses=8, socle=(sd, sh))
            PLANTED.append(("trepadeira", x + dx, yw, P3, "muralha"))
            got += 1
            break
    return got


# ------------------------------------------------------------------ QA: nada em rota / piso
def qa(lawn):
    bad = {"rua": 0, "praca": 0, "escada": 0, "rota": 0, "piso": 0, "salao": 0, "dungeon": 0, "casa": 0}
    ex = []
    kx0, ky0, kz0, kx1, ky1, kz1 = L.DUN_KEEP_OUT
    for kind, x, y, z, ctx in PLANTED:
        if kx0 < x < kx1 and ky0 < y < ky1 and kz0 < z < kz1:
            bad["dungeon"] += 1
        hx = L.MINE_RECT
        if hx[0] < x < hx[2] and hx[1] < y < hx[3]:
            bad["salao"] += 1
        if ctx in ("gramado", "ombro") or (kind == "flor" and ctx.startswith("mancha")):
            b = plan_blocked(x, y, z)
            if b in ("rua", "praca", "escada", "casa"):
                bad[b] += 1
                ex.append((kind, round(x, 1), round(y, 1), b))
            fl = L.floor_name(x, y)
            fz = L.zone_of(x, y)
            if fl is not None and fl != "P2" and fz is not None and abs(fz - z) < 1.0:
                bad["piso"] += 1
                ex.append((kind, round(x, 1), round(y, 1), round(z, 1), fl))
            if lawn is not None and lawn.rdist(x, y) < 0.9:
                bad["rota"] += 1
                ex.append((kind, round(x, 1), round(y, 1), "rota"))
    tot = sum(bad.values())
    seen = {}
    shown = []
    for e in ex:
        if seen.get(e[-1], 0) < 3:
            seen[e[-1]] = seen.get(e[-1], 0) + 1
            shown.append(e)
    print("GARDEN_QA itens=%d fora_do_lugar=%s %s %s" % (len(PLANTED), bad, "OK" if tot == 0 else "FAIL", shown))
    return tot


# ------------------------------------------------------------------ build (chamado no fim do sg_veg.build)
PITS = []           # (x, y, z_terra) - preenchido pelo sg_veg.tree_pit


def _tris(B):
    t = 0
    for m in B.mbs.values():
        for f in m.bm.faces:
            t += len(f.verts) - 2
    return t


def reset():
    """inicio do vestir (sg_court.build): zera o registro (o patio planta antes do campo); as contas das floreiras
    (a vila monta antes do vestir) ficam"""
    keep = {k: v for k, v in STATS.items() if "floreiras" in k}
    STATS.clear()
    STATS.update(keep)
    PLANTED.clear()
    OCC.clear()


def build(trees=None, routes=None):
    import time
    t0 = time.time()
    trees = trees or []
    B = Beds()
    G = Ground((BOX_VIL[0] - 2, BOX_VIL[1] - 2, BOX_VIL[2] + 2, 60.0))
    lawn = Lawn(G)
    if routes:
        lawn.raster_routes(routes)
    t1 = time.time()
    lawn_trees = [(x, y, z, r, h) for x, y, z, r, h in trees if lawn.at(x + 0.8, y + 0.8) is not None
                  or lawn.at(x - 0.8, y - 0.8) is not None]
    lamps = []
    try:
        import sg_props as PR
        lamps += [(x, y) for n, x, y, z, lit in PR.LAMPS]
    except Exception:
        pass
    try:
        import sg_village as VL
        lamps += [(x, y) for x, y, z, lit in VL.LAMPS]
    except Exception:
        pass
    # 1. plantio dirigido primeiro (ocupa o lugar): casas, postes, escadas/portoes, alquimia, arvores do gramado
    ph = {}
    house_gardens(B, lawn, G)
    ph["casas"] = _tris(B)
    ring_spots = [
        # (x, y, raio, especies, contexto)
        (-77.0, -48.4, 1.8, ("moon", "bell"), "mancha_poste"),     # poste da rua do P2 oeste (lado do gramado)
        (10.2, -54.2, 1.6, ("moon", "spike"), "mancha_poste"),      # poste do cruzamento do eixo
        (-12.4, -77.0, 1.8, ("spike", "moon"), "mancha_escada"),    # topo da escada P1P2 (arco)
        (12.4, -77.0, 1.8, ("spike", "moon"), "mancha_escada"),
        (-11.0, -31.0, 2.2, ("moon", "spike"), "mancha_portao"),    # pe da escada do portao do castelo
        (11.0, -31.0, 2.2, ("moon", "spike"), "mancha_portao"),
        (104.0, -30.0, 1.8, ("bell", "moon"), "mancha_portao"),     # pe da escada leste (dungeon)
        (120.0, -30.0, 1.8, ("bell", "moon"), "mancha_portao"),
        (76.5, -49.5, 1.9, ("amber", "bell"), "mancha_alquimia"),   # porta da alquimia (oeste)
        (77.0, -70.5, 1.9, ("bell", "amber"), "mancha_alquimia"),
        (147.0, -28.0, 1.8, ("moon", "amber"), "mancha_saida"),     # cabeceira da ponte da saida
        (147.0, -48.5, 1.8, ("moon", "bell"), "mancha_saida"),
    ]
    for x, y, R, kinds, ctx in ring_spots:
        patch(B.mb(zone_key(x, y, P2)), lawn, x, y, R, kinds, ctx)
    for i, (tx, ty, tz, tr, th) in enumerate(lawn_trees):
        if tz < P2 - 3.0:
            continue
        a = hh(tx, ty, 70) * math.tau
        px, py = tx + math.cos(a) * (tr + 0.9), ty + math.sin(a) * (tr + 0.9)
        kinds = (("bell", "moon"), ("moon", "spike"), ("bell",))[i % 3]
        patch(B.mb(zone_key(px, py, tz)), lawn, px, py, 1.5, kinds, "mancha_arvore", dens=0.8)
    # pontos de "bonemeal" no gramado aberto: maximos do campo, bem separados
    spots = []
    for gy in np.arange(-80.0, -8.0, 3.0):
        for gx in np.arange(-116.0, 152.0, 3.0):
            h = lawn.at(gx, gy)
            if h is None or h[1] < 2.5 or lawn.rdist(gx, gy) < 3.0:
                continue
            spots.append((field(gx, gy) - 0.4 * field2(gx, gy), gx, gy))
    spots.sort(reverse=True)
    mix = (("moon", "bell"), ("spike", "moon"), ("bell", "spike"), ("moon", "amber"), ("moon",), ("bell", "moon"))
    chosen = []
    for v, gx, gy in spots:
        if all(math.hypot(gx - a, gy - b) > 11.0 for a, b in chosen):
            chosen.append((gx, gy))
            patch(B.mb(zone_key(gx, gy, P2)), lawn, gx, gy, 1.6 + 0.6 * (len(chosen) % 2),
                  mix[len(chosen) % len(mix)], "mancha_gramado")
        if len(chosen) >= 24:
            break
    ph["manchas"] = _tris(B) - sum(ph.values())
    # 2. canteiros das arvores do piso calcado e da fonte da praca
    plant_pits(B, PITS)
    ph["canteiros_arvore"] = _tris(B) - sum(ph.values())
    plaza_beds(B, G)
    ph["praca"] = _tris(B) - sum(ph.values())
    nv = 0
    # 4. o campo de tufos
    placed, kf, ncand = scatter(B, lawn, lawn_trees, lamps)
    ph["campo"] = _tris(B) - sum(ph.values())
    # 5. manchas de tom
    ntone = lawn_tones(lawn, lawn_trees)
    obs = B.finish()
    tris = {}
    for o in obs + [bpy.data.objects.get("SG_Veg_Gdn_LawnTone")]:
        if o is None:
            continue
        per = {}
        for p in o.data.polygons:
            nm = o.data.materials[p.material_index].name
            per[nm] = per.get(nm, 0) + len(p.vertices) - 2
        tris[o.name] = (sum(per.values()), len(per))
    print("GARDEN mascara %.1fs celulas_grama=%d excluidas=%s" % (t1 - t0, int(lawn.mask.sum()), lawn.why))
    print("GARDEN tufos_campo=%d/%d (fator %.2f) stats=%s tons=%d trepadeiras_patio=%d" % (
        placed, ncand, kf, {k: (round(v, 1) if isinstance(v, float) else v) for k, v in STATS.items()}, ntone, nv))
    print("GARDEN tris por fase:", ph)
    print("GARDEN objetos (tris, materiais=MeshParts):", tris, "total_tris=%d MeshParts=%d" % (
        sum(v[0] for v in tris.values()), sum(v[1] for v in tris.values())))
    qa(lawn)
    print("GARDEN FIM %.1fs" % (time.time() - t0))
