# ds_veg - VEGETACAO da Ilha 4 (DEMON SLAYER), agente 3a da Onda 3 (PLANO_DS secoes 4, 5, 7, 12; prompt secoes 15, 16,
# 18, 19, 25, 26, 33, 34, 37, 39, 41). Substitui a vegetacao do ds_blockout.dressing. Prefixo DS_Veg_, colecao
# 10_VEGETATION, sem luz. Colisao SO nos troncos, nos colmos das touceiras e nos esteios da pergola (COL_DS_Veg*).
#
# INTENCAO (cada grupo tem um porque; nada de scatter):
#   - ENTRADA (densidade baixa): 1 pinheiro-marco (kuromatsu) torto na crista oeste debrucado sobre o patio do torii +
#     4 cedros (sugi) em grupo na crista da trilha. Nada roxo.
#   - BAMBUZAL (sudeste): TOUCEIRAS (5-6 colmos de um mesmo pe, nos com anel, folhas em leque nos 2 nos de cima e no
#     topo, brotos na base) ladeando o caminho calcado (BAMBOO_RAMP, livre); as touceiras da beira se inclinam sobre o
#     caminho (tunel); corredor de visada trilha -> estrela do summon aberto. No topo do bambuzal a PERGOLA de bambu
#     com a 4a glicinia (L.WISTERIA[3]) atravessando o caminho: a transicao bambuzal -> clareira.
#   - CLAREIRA: as 3 arvores largas da planta (L.CLEARING_TREES; raizes que agarram o chao, a do nordeste com as
#     raizes recortadas para fora do canal) e GRAMA EM MANCHAS so na borda: a densidade cresce do miolo VAZIO para
#     fora (nada dentro da MiningZone + 3; folha nenhuma abaixo de piso + 12,6 sobre ela).
#   - PE DA SUBIDA: pinheiro torto no canto noroeste da clareira (a berma/patamar fica no eixo clareira -> forja: la
#     ele tapava o salao e a boca nas PlayerHeight; aqui ele fica abaixo da linha do terraco da forja).
#   - VILA (media-alta): arvores largas ATRAS das casas (enquadram os telhados, nao tapam porta nem rua), cedros atras
#     do kura, arbustos podados (karikomi) junto das casas e no jardim do V6, e a 3a glicinia pendendo da fujidana do
#     V6 (topo a 8,66, do ds_village). Pinheiro no promontorio oeste.
#   - FORJA (heroi): so moldura ATRAS (3 arvores largas + cedros nas rochas do fundo, todas >= 20 abaixo da chamine).
#     Nada na frente da boca nem da torre.
#   - SAIDA (baixa): cedros esparsos ao longo do caminho.
# FAMILIA DA GLICINIA: as 2 do plato do summon sao do ds_summon (wisteria_tree). As 2 daqui usam a MESMA linguagem
# (ds_summon.raceme + ds_summon._blob + tronco em S com o mesmo cone de raiz, tons WIS_TONES), so que conduzidas numa
# trelica: tronco que sobe por um esteio, bracos sobre a trelica, tufos de folha em cima e cortina de cachos embaixo.
# MATERIAIS: so os da paleta (Bark_DS, Leaf_DS_Broad/Cedar/Shrub, Bamboo_DS/_Dry, Wisteria_DS*). 3 tons de verde:
# Cedar (escuro, coniferas e o fundo das copas), Broad (medio, arvores largas), Shrub (claro: momiji, karikomi, folha
# de bambu e tufos de grama). Lilas so nas glicinias.
# RAIZES: cada arvore da clareira tem as suas (curvas, mergulhando no chao real, fora do canal). (ONDA 4: o ds_terrain
# nao gera mais as raizes retas DS_Clr_Roots, entao o apagamento delas aqui saiu.)
# ONDA 4b (agente 4b-VEG, DENSIDADE): a ilha lia esparsa contra as refs. Acrescimos (densify, secao "ONDA 4b"):
#   - DEN_TREES: 47 arvores da MESMA familia em versao LEVE (broad_lite: keyaki/momiji com metade das massas; cedro)
#     em fileiras/grupos com intencao: crista da Trilha, fundo e rua da vila baixa, topo do arrimo vila alta -> clareira,
#     moldura da clareira (O/S/SE/L/N), barranco NE, abas da subida na berma, borda do patio do carvao, as 2 margens
#     do caminho de saida, lobo leste da forja, fundo e tras do summon. site_ok: chao natural, fora da MiningZone + 6,
#     tronco >= 7 + r da rota (faixa das lanternas/cercas do ds_props livre), fora de escada/agua/frente de casa/ancora
#     de prop; NUDGE ate 5 em volta; a copa encolhe (0,82/0,68) se fechar uma VISADA protegida (protected_views: forja
#     boca/salao/torre-chamine, estrela e torre do summon, portao OP, das PlayerHeight, Ref_* e do gate do QA).
#     Colisao do tronco so a <= 26 de rota ou na clareira (o COL_ da ilha e compartilhado).
#   - saias de mato no pe das arvores novas (do lado de fora do caminho); FRANJA das falesias: moitas e arvorezinhas
#     agarradas (cliff_tree) no topo REAL das colunas da coroa (raio de cima) + moitas na FACE das colunas (raio
#     horizontal, face_clump), em setores de ruido de baixa frequencia; moitas de PE DE MURO em setores.
#   - bambuzal 23 -> 29 touceiras (+ moitas na aba oeste, sobre o arrimo da Trilha); grama 280 -> 170 tufos.
#   Glicinias continuam so as 4. Orcamento: ~115,5k tris (teto 118k / 95 MeshParts no export_ds).
# OBJETOS: 1 por celula de 140 x 140 da planta (o export fatia > 160 em celulas e cada material vira 1 MeshPart);
# bambuzal e glicinias em objetos proprios.
import math, random, zlib
import bpy
from mathutils import Vector, noise
from mathutils.bvhtree import BVHTree
import ds_lib as DL
from ds_lib import MB, col_box
import ds_layout as L
import fm_portal_kit as PK
import ds_summon as SUM

C = "10_VEGETATION"
T0, T1, T2, T3, T4 = L.T0, L.T1, L.T2, L.T3, L.T4
BARK, BROAD, CEDAR, SHRUB = "Bark_DS", "Leaf_DS_Broad", "Leaf_DS_Cedar", "Leaf_DS_Shrub"
BAMB, BAMB_DRY = "Bamboo_DS", "Bamboo_DS_Dry"
ZZ = Vector((0.0, 0.0, 1.0))
TAU = math.tau
CLEAR_TOP = T1 + L.CLEAR_H + 0.6          # folha nenhuma abaixo disso sobre a MiningZone (+ folga)
MINE_PAD = 3.0                            # nada de vegetacao no chao dentro da MiningZone + 3
TOP_MAX = L.CHIMNEY_TOP - 22.0            # nada de vegetacao acima disso (a chamine fica >= 20 acima de tudo)
STATS = {}


def hh(*a):
    s = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    return (zlib.crc32(s.encode("utf-8")) & 0xffffffff) / 4294967296.0


def vdir(a, z=0.0):
    return Vector((math.cos(a), math.sin(a), z))


def in_mine(x, y, pad=MINE_PAD):
    x0, y0, x1, y1 = L.MINE_RECT
    return x0 - pad < x < x1 + pad and y0 - pad < y < y1 + pad


# ================================================================== a cena ja montada (chao REAL, o que ja existe)
class Probe:
    """raios contra o que as outras zonas ja montaram: o chao natural (terreno) onde a planta pode nascer e o
    construido (casas, forja, summon, agua, portao) que copa nenhuma pode atravessar"""
    NATURAL = ("DS_Ter_Ground", "DS_Ter_Grass", "DS_Clr_Floor", "DS_Ter_Rocks", "DS_Ter_Bodies", "DS_Ter_Cliff")
    WALLS = ("DS_Ter_Ishigaki", "DS_Ter_RockWalls", "DS_Ter_Cliff", "DS_Ter_Rocks", "DS_Ter_Bodies")
    BUILT = ("DS_Vil_", "DS_Frg_", "DS_Sum_", "DS_Ent_Torii", "DS_Ent_Toro", "DS_Ent_Bridge", "DS_Exit_Torii",
             "DS_Exit_Bridge", "DS_Water_", "DS_Prop_", "GATE_", "DS_Exit_AnchorGuard")

    def __init__(self):
        V, P, self.own, self.mat = [], [], [], []
        bV, bP = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or o.hide_render or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "DS_Veg_", "VFX_",
                                                                           "DS_Clr_OreProxy")):
                continue
            mw = o.matrix_world
            me = o.data
            vs = [mw @ v.co for v in me.vertices]
            mats = [m.name if m else "" for m in me.materials]
            b = len(V)
            V += vs
            for p in me.polygons:
                P.append([b + i for i in p.vertices])
                self.own.append(o.name)
                self.mat.append(mats[p.material_index] if p.material_index < len(mats) else "")
            if o.name.startswith(self.BUILT):
                b2 = len(bV)
                bV += vs
                bP += [[b2 + i for i in p.vertices] for p in me.polygons]
        self.bvh = BVHTree.FromPolygons(V, P)
        self.built = BVHTree.FromPolygons(bV, bP) if bP else None
        self.routes = [pts for pts, z in L.routes().values()]
        self.stairs = [r for nm, up, r, zf, zt in L.stair_notches()]

    def top(self, x, y, z0=320.0):
        """(z, dono, material, normal_z) do primeiro que um raio de cima encontra"""
        h = self.bvh.ray_cast(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), 500.0)
        if h[0] is None:
            return None
        return h[0].z, self.own[h[2]], self.mat[h[2]], h[1].z

    def ground(self, x, y, need_natural=True):
        t = self.top(x, y)
        if t is None or (need_natural and not t[1].startswith(self.NATURAL)):
            return None
        return t[0]

    def gz(self, x, y, fallback):
        t = self.top(x, y)
        return t[0] if t else fallback

    def clear_of_built(self, p, r):
        if self.built is None:
            return True
        return self.built.find_nearest(Vector(p), r)[0] is None

    def route_dist(self, x, y):
        return min(L.polyline_dist(x, y, pts) for pts in self.routes)

    def in_stairs(self, x, y, m=1.5):
        return any(r[0] - m < x < r[2] + m and r[1] - m < y < r[3] + m for r in self.stairs)


# ================================================================== primitivas organicas (silhueta facetada, sem bevel)
def cushion(mb, c, rx, ry, h, m, rng, n=7, rot=0.0, jit=0.12, prof=((0.0, 0.66), (0.36, 1.0), (0.76, 0.62))):
    """ALMOFADA de folhagem: fundo quase plano (le como massa apoiada nos galhos, nao bola), cintura larga a 1/3,
    ombro estreito e topo deslocado; anel com raio e angulo sorteados = facetas irregulares. c = centro do FUNDO."""
    bm = mb.bm
    rings = []
    for k, (fz, fr) in enumerate(prof):
        ring = []
        for j in range(n):
            a = rot + TAU * (j + rng.uniform(-0.2, 0.2)) / n
            s = fr * rng.uniform(1.0 - jit, 1.0 + jit)
            ring.append(bm.verts.new((c.x + math.cos(a) * rx * s, c.y + math.sin(a) * ry * s,
                                      c.z + h * (fz + (rng.uniform(-0.06, 0.06) if k else rng.uniform(-0.03, 0.03))))))
        rings.append(ring)
    bot = bm.verts.new((c.x, c.y, c.z - h * 0.05))
    top = bm.verts.new((c.x + rng.uniform(-0.18, 0.18) * rx, c.y + rng.uniform(-0.18, 0.18) * ry, c.z + h))
    for j in range(n):
        j2 = (j + 1) % n
        bm.faces.new((rings[0][j2], rings[0][j], bot))
        bm.faces.new((rings[-1][j], rings[-1][j2], top))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    mb._post([v for r in rings for v in r] + [bot, top], m, None, 0, 1)


def pad(mb, c, s, m, rng, flat=0.62, n=6, subs=2):
    """MASSA de copa: almofada principal + 1-2 almofadas menores desencontradas por cima/fora (contorno de nuvem,
    topo irregular). c = ponto onde o galho entra (o fundo fica 0,32 s abaixo)"""
    a0 = rng.uniform(0, TAU)
    base = c - ZZ * (s * 0.32)
    cushion(mb, base, s * 1.05, s * rng.uniform(0.82, 0.95), s * flat * 1.25, m, rng, n=n, rot=a0,
            prof=((0.0, 0.72), (0.42, 1.0), (0.8, 0.68)))
    for k in range(subs):
        a = a0 + 2.2 * k + rng.uniform(-0.5, 0.5)
        q = base + vdir(a) * s * rng.uniform(0.45, 0.7) + ZZ * s * rng.uniform(0.18, 0.4)
        ss = s * rng.uniform(0.55, 0.7)
        cushion(mb, q, ss * 1.05, ss * 0.9, ss * flat * 1.3, m, rng, n=6, rot=a)


def leaf(mb, a, d, Ln, W, m, rng):
    """folha lanceolada FECHADA (tetraedro achatado e torcido: 4 tris) de a na direcao d"""
    d = d.normalized()
    side = d.cross(ZZ)
    if side.length < 1e-4:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    nrm = side.cross(d).normalized()
    mid = a + d * Ln * 0.38
    bm = mb.bm
    va = bm.verts.new(a)
    vt = bm.verts.new(a + d * Ln)
    vl = bm.verts.new(mid + side * W * 0.5 + nrm * 0.06)
    vr = bm.verts.new(mid - side * W * 0.5 - nrm * 0.06)
    for f in ((va, vl, vt), (va, vt, vr), (vl, vr, vt), (va, vr, vl)):
        bm.faces.new(f)
    mb._post([va, vt, vl, vr], m, None, 0, 1)


ROOT_KO = [None]            # ONDA 6b: (pontos, linhas) dos props fixos (prop_keepout), posto no build


def _root_ground_ok(P, q, z0):
    """ONDA 6b (item 45): a raiz so mergulha em CHAO NATURAL na cota do pe (-1,2..+1,6). Na borda do plato o raio
    de cima achava o pe da falesia 17-30 abaixo e a 'raiz' descia o paredao (lia tronco escorrendo pela falesia, e uma
    atravessava a madeira do summon); tambem nada de raiz entrando em construido nem em prop fixo (cerca, lanterna)"""
    t = P.top(q.x, q.y)
    if t is None or not t[1].startswith(P.NATURAL) or not (z0 - 1.2 < t[0] < z0 + 1.6):
        return False
    if ROOT_KO[0] is not None and prop_gap(q.x, q.y, ROOT_KO[0]) < 1.0:
        return False
    return P.clear_of_built(Vector((q.x, q.y, t[0] + 0.3)), 0.7)


def roots(mb, P, base, r0, rng, n=5, reach=(2.4, 4.0), avoid=None, a0=None):
    """raizes que AGARRAM o chao: nascem no tronco a ~1,5 de altura, descem em arco e mergulham 0,45 no chao real
    (sondado). avoid(x, y) -> True = proibido (canal, rua): a raiz gira; se nao achar lugar, nao nasce.
    ONDA 6b: tambem gira (ou nao nasce) se o chao do meio/da ponta nao for natural na cota do pe (_root_ground_ok)"""
    a0 = rng.uniform(0, TAU) if a0 is None else a0
    made = 0
    for k in range(n):
        a = a0 + TAU * k / n + rng.uniform(-0.3, 0.3)
        Ln = rng.uniform(*reach)
        ok = False
        for t in range(5):
            aa = a + (0.0, 0.45, -0.45, 0.9, -0.9)[t]
            e = base + vdir(aa) * (r0 + Ln)
            m_ = base + vdir(aa) * (r0 + Ln * 0.55)
            if (not avoid or not (avoid(e.x, e.y) or avoid(m_.x, m_.y))) and \
                    _root_ground_ok(P, e, base.z) and _root_ground_ok(P, m_, base.z):
                ok = True
                a = aa
                break
        if not ok:
            continue
        d = vdir(a)
        side = vdir(a + math.pi / 2) * rng.uniform(-0.5, 0.5)
        p0 = base + d * r0 * 0.3 + ZZ * rng.uniform(1.4, 2.0)
        p1 = base + d * (r0 + 0.35) + ZZ * 0.85
        q2 = base + d * (r0 + Ln * 0.55) + side * 0.4
        p2 = Vector((q2.x, q2.y, P.gz(q2.x, q2.y, base.z) + 0.2))
        q3 = base + d * (r0 + Ln) + side
        p3 = Vector((q3.x, q3.y, P.gz(q3.x, q3.y, base.z) - 0.45))
        tube(mb, [p0, p1, p2, p3], [r0 * 0.5, r0 * 0.4, r0 * 0.24, 0.1], n=5)
        made += 1
    return made


def tube(mb, pts, radii, m=BARK, n=6):
    """galho/tronco SEM tampa: as 2 pontas ficam escondidas (enterradas, dentro do tronco ou da massa de copa)"""
    PK.taper_tube(mb, [Vector(p) for p in pts], radii, m, n=n, caps=False)


# ================================================================== ARVORE LARGA (keyaki / momiji estilizados)
def broad_tree(mb, P, x, y, rng, h=22.0, R=8.0, leaf_m=BROAD, dark=CEDAR, limbs=3, flat=0.9, lean=(0.0, 0.0),
               face=None, avoid=None, adjust=None, shift=(0.0, 0.0), r_scale=1.0):
    """arvore larga das referencias: tronco CURTO e grosso com base alargada e raizes, forquilha baixa (~0,3 h) em
    'limbs' bracos que abrem em vaso; a COPA e uma massa grande em 3 andares de massas (anel de baixo largo, anel de
    cima recolhido e girado, coroa) + 2 massas internas no tom escuro (profundidade, sem buraco no meio). Cada massa =
    almofadas facetadas desencontradas (contorno de nuvem). adjust(c, s) -> (c, s) ou None. shift: so o pe do tronco
    desloca (canal), a copa fica no ponto da planta."""
    z = P.gz(x + shift[0], y + shift[1], T1)
    base = Vector((x + shift[0], y + shift[1], z))
    axis = Vector((x, y, z))
    r0 = (0.5 + R * 0.09) * r_scale
    lv = Vector((lean[0], lean[1], 0.0))
    hf = h * rng.uniform(0.27, 0.32)
    ph = rng.uniform(0, TAU)
    tp, tr = [], []
    for i in range(6):
        f = i / 5
        off = (axis - base) * f + lv * f * f + vdir(ph) * math.sin(f * math.pi) * 0.35 * r0
        tp.append(base + off + ZZ * (hf * f - 0.6 * (1 - f)))
        tr.append(r0 * (1.34 if i == 0 else (1.14 - 0.3 * f)))
    tube(mb, tp, tr, n=8)
    F, rf = tp[-1], tr[-1]
    nr = roots(mb, P, base, r0, rng, n=5, avoid=avoid)
    pads = []
    a0 = (face if face is not None else rng.uniform(0, TAU)) + rng.uniform(-0.2, 0.2)
    C0 = axis + lv

    def place(pc, s, m, frm, rads, branch=True):
        if adjust:
            r_ = adjust(pc, s)
            if r_ is None:
                return False
            pc, s = r_
        if branch:
            mid = frm.lerp(pc, 0.5) + ZZ * 0.5
            tube(mb, [frm, mid, pc - ZZ * 0.2], rads, n=5)
        pads.append((pc, s, m))
        return True

    ends = []
    for k in range(limbs):
        a = a0 + TAU * k / limbs + rng.uniform(-0.25, 0.25)
        d = vdir(a)
        l1 = F + d * R * 0.16 + ZZ * h * 0.1
        l2 = F + d * R * 0.34 + ZZ * h * 0.2
        tube(mb, [F - ZZ * 0.8, l1, l2], [rf * 0.74, rf * 0.58, rf * 0.44], n=6)
        ends.append((a, l2))
        # anel de baixo: 2 massas largas por braco
        for s_ in (-1, 1):
            b = a + s_ * rng.uniform(0.32, 0.5)
            pc = C0 + vdir(b) * R * rng.uniform(0.56, 0.7) + ZZ * h * rng.uniform(0.5, 0.58)
            place(pc, R * rng.uniform(0.4, 0.46), leaf_m, l2, [rf * 0.36, rf * 0.26, rf * 0.16])
    # anel de cima (girado entre os bracos) e coroa
    for k, (a, l2) in enumerate(ends):
        b = a + math.pi / limbs + rng.uniform(-0.2, 0.2)
        pc = C0 + vdir(b) * R * rng.uniform(0.32, 0.42) + ZZ * h * rng.uniform(0.7, 0.77)
        place(pc, R * rng.uniform(0.42, 0.48), leaf_m, l2, [rf * 0.32, rf * 0.22, rf * 0.14])
    top = C0 + lv * 0.2 + vdir(ph + 1.0) * R * 0.08 + ZZ * h * 0.86
    place(top, R * 0.44, leaf_m, F, [rf * 0.6, rf * 0.4, rf * 0.2])
    for k in range(2):
        a = a0 + math.pi / limbs + math.pi * k + rng.uniform(-0.3, 0.3)
        place(C0 + vdir(a) * R * 0.26 + ZZ * h * 0.58, R * 0.42, dark, F, None, branch=False)
    for pc, s, m in pads:
        pad(mb, pc, s, m, rng, flat=flat, subs=1)
    col_box("DS_VegTrunk", (r0 * 2.0, r0 * 2.0, 8.0), (base.x, base.y, z + 4.0))
    top_z = max(pc.z + s * flat * 1.1 for pc, s, m in pads) if pads else z + h
    return dict(base=base, pads=len(pads), roots=nr, top=top_z)


# ================================================================== PINHEIRO japones (kuromatsu, torto, em nuvens)
def pine(mb, P, x, y, rng, h=13.0, lean_az=0.0, lean=0.45, reach=5.0, leaf_m=CEDAR, adjust=None):
    """tronco em S inclinado (o vento da montanha), galhos quase horizontais alternados e MASSAS CHATAS em camadas
    (poda em nuvem, niwaki) + massa do alto; raizes curtas"""
    z = P.gz(x, y, T1)
    base = Vector((x, y, z))
    d = vdir(lean_az)
    perp = vdir(lean_az + math.pi / 2)
    pts, rad = [], []
    for i in range(7):
        f = i / 6
        off = d * (h * lean) * (1.25 * f - 0.45 * f * f) + perp * math.sin(f * math.pi * 1.3) * 0.9
        pts.append(base + off + ZZ * (h * 0.9 * f - 0.5 * (1 - f)))
        rad.append(1.6 if i == 0 else 1.25 - 0.8 * f)
    tube(mb, pts, rad, n=7)
    roots(mb, P, base, 0.95, rng, n=3, reach=(1.6, 2.6))

    def spine(f):
        t = f * 6
        i = min(5, int(t))
        return pts[i].lerp(pts[i + 1], t - i)

    tiers = [(0.42, 1.0), (0.56, -1.0), (0.7, 0.4), (0.82, -0.7)]
    n = 0
    for f, s_ in tiers:
        p = spine(f)
        az = lean_az + s_ * rng.uniform(0.9, 1.5)
        rr = reach * (1.15 - f * 0.55) * rng.uniform(0.85, 1.05)
        e = p + vdir(az) * rr + ZZ * rng.uniform(0.4, 1.1)
        if adjust:
            r_ = adjust(e, 2.6)
            if r_ is None:
                continue
            e = r_[0]
        mid = p.lerp(e, 0.5) - ZZ * 0.35
        tube(mb, [p, mid, e - ZZ * 0.2], [0.55 - 0.15 * f, 0.38 - 0.1 * f, 0.2], n=5)
        s = rng.uniform(2.9, 3.6) * (1.1 - 0.3 * f)
        cushion(mb, e - ZZ * 0.5, s * 1.15, s * 0.82, s * 0.48, leaf_m, rng, n=8, rot=az)
        cushion(mb, e + vdir(az) * s * 0.35 - ZZ * 0.05, s * 0.66, s * 0.52, s * 0.4, leaf_m, rng, n=6, rot=az)
        n += 1
    top = pts[-1]
    cushion(mb, top - ZZ * 0.5, 3.1, 2.6, 1.6, leaf_m, rng, n=8, rot=lean_az)
    cushion(mb, top + ZZ * 0.5 + d * 0.6, 1.9, 1.6, 1.1, leaf_m, rng, n=6, rot=lean_az)
    col_box("DS_VegTrunk", (2.0, 2.0, 7.0), (x, y, z + 3.5))
    return dict(base=base, pads=n + 1, top=top.z + 1.4)


# ================================================================== CEDRO (sugi) - grupos no fundo e nas encostas
def cedar(mb, P, x, y, rng, h=22.0, r=3.4, leaf_m=CEDAR, col=True):
    """SUGI estilizado na linguagem das outras copas: tronco reto e afilado + coluna conica de MASSAS empilhadas
    (5 andares de 2 almofadas desencontradas em volta do tronco, de baixo largo para cima estreito, fundo plano de
    cada andar = camadas) e ponta romba. Le como cedro (coluna escura e alta), nao como pinheiro de natal."""
    z = P.gz(x, y, T1)
    h = min(h, TOP_MAX - z)
    PK.cone(mb, Vector((x, y, z - 0.5)), Vector((x, y, z + h * 0.84)), 0.36 + r * 0.12, 0.14, BARK, n=6)
    lean = vdir(rng.uniform(0, TAU)) * rng.uniform(0.2, 0.7)
    nt = 4
    a0 = rng.uniform(0, TAU)
    for k in range(nt):
        t = k / (nt - 1)
        zb = z + h * (0.18 + 0.58 * t)
        rad = r * (1.0 - 0.58 * t)
        c = Vector((x, y, zb)) + lean * t
        for j in range(2):
            a = a0 + 2.1 * k + math.pi * j + rng.uniform(-0.4, 0.4)
            q = c + vdir(a) * rad * 0.22 - ZZ * (h * 0.03 * j)
            cushion(mb, q, rad * rng.uniform(0.9, 1.0), rad * rng.uniform(0.74, 0.86), h * 0.27 * (1.0 - 0.3 * t),
                    leaf_m, rng, n=6, rot=a, prof=((0.0, 0.92), (0.3, 1.0), (0.72, 0.5)))
    tip = Vector((x, y, z + h * 0.93)) + lean
    cushion(mb, tip - ZZ * h * 0.06, r * 0.34, r * 0.3, h * 0.13, leaf_m, rng, n=6)
    if col and L.zone_of(x, y) is not None:
        col_box("DS_VegTrunk", (1.4, 1.4, 7.0), (x, y, z + 3.5))
    return z + h


# ================================================================== KARIKOMI (arbusto podado) e TUFO de grama
def low_ground(P, x, y, r, z_ref, drop=1.0):
    """ONDA 6b (item 46): cota MAIS BAIXA do chao sob uma almofada (centro + 4 pontos a 0,6 r), limitada a z_ref -
    drop (na quina de falesia/arrimo a almofada fica agarrada na borda, nao desce o paredao). Antes cada almofada
    satelite usava a cota do centro da moita e boiava 0,2-0,5 em chao inclinado"""
    zs = [P.gz(x + dx, y + dy, z_ref) for dx, dy in ((0.0, 0.0), (0.6 * r, 0.0), (-0.6 * r, 0.0), (0.0, 0.6 * r),
                                                       (0.0, -0.6 * r))]
    return max(min(zs), z_ref - drop)


def karikomi(mb, P, x, y, rng, r=1.7, lumps=2, m=SHRUB):
    """azaleia podada: 1-3 almofadas LISAS (poda) encostadas, mais largas que altas, enterradas 0,2"""
    z = P.gz(x, y, T1)
    a0 = rng.uniform(0, TAU)
    for k in range(lumps):
        q = Vector((x, y, z - 0.2)) + (vdir(a0 + 2.4 * k) * r * 0.75 if k else Vector())
        rr = r * (1.0 if k == 0 else rng.uniform(0.62, 0.8))
        q.z = low_ground(P, q.x, q.y, rr, z) - 0.2
        cushion(mb, q, rr * 1.08, rr * 0.95, rr * 1.0, m, rng, n=9, rot=a0 + k, jit=0.05,
                prof=((0.0, 0.86), (0.32, 1.0), (0.7, 0.82)))


def bush(mb, P, x, y, rng, r=1.6, m=BROAD, n=6, lumps=None):
    """mato baixo SELVAGEM (pe de muro, borda da clareira): 2-3 almofadas asperas e desencontradas, mais alto num
    lado, enterradas 0,25 (contraponto ao karikomi podado da vila). ONDA 4b: n/lumps para a versao de LONGE (franja
    das falesias: 2 almofadas de 5 lados)"""
    z = P.gz(x, y, T1)
    a0 = rng.uniform(0, TAU)
    for k in range(lumps or rng.randint(2, 3)):
        q = Vector((x, y, z - 0.25)) + vdir(a0 + 2.3 * k) * r * (0.0 if k == 0 else rng.uniform(0.55, 0.85))
        rr = r * (1.0 if k == 0 else rng.uniform(0.55, 0.75))
        q.z = low_ground(P, q.x, q.y, rr, z) - 0.25
        cushion(mb, q, rr, rr * 0.85, rr * rng.uniform(0.95, 1.25), m, rng, n=n, rot=a0 + k, jit=0.16)
    return z


def tuft(mb, x, y, z, rng, s=1.0, m=SHRUB, P=None):
    """tufo de capim: 6-9 laminas (tetraedros finos e inclinados para fora), a base enterrada 0,22 no chao.
    ONDA 6b (item 46): com P, cada lamina assenta no chao DELA (borda de terraco/caminho: a lamina do lado baixo
    boiava ate 0,46); lamina cujo chao cai > 0,9 (quina de muro) sai"""
    bm = mb.bm
    vs = []
    nb = rng.randint(6, 9)
    made = 0
    for k in range(nb):
        a = rng.uniform(0, TAU)
        rr = rng.uniform(0.0, 0.45) * s
        bx, by = x + math.cos(a) * rr, y + math.sin(a) * rr
        hg = s * rng.uniform(0.75, 1.55)
        la = a + rng.uniform(-0.6, 0.6)
        lx, ly = math.cos(la) * hg * rng.uniform(0.15, 0.5), math.sin(la) * hg * rng.uniform(0.15, 0.5)
        w = 0.14 * s
        r0 = rng.uniform(0, TAU)
        zb = z
        if P is not None:
            zb = min(P.gz(bx + math.cos(r0 + TAU * i / 3) * w, by + math.sin(r0 + TAU * i / 3) * w, z)
                     for i in range(3))
            if zb < z - 0.9:
                continue
            zb = min(zb, z)
        made += 1
        b = [bm.verts.new((bx + math.cos(r0 + TAU * i / 3) * w, by + math.sin(r0 + TAU * i / 3) * w, zb - 0.22))
             for i in range(3)]
        tp = bm.verts.new((bx + lx, by + ly, zb + hg))
        for f in ((b[0], b[1], tp), (b[1], b[2], tp), (b[2], b[0], tp), (b[0], b[2], b[1])):
            bm.faces.new(f)
        vs += b + [tp]
    mb._post(vs, m, None, 0, 1)
    return made * 4


# ================================================================== BAMBU em touceira
def culm(mb, p0, h, r, splay, bend, rng, collars=4):
    """colmo: entrenos que alongam para cima, leve dobra em cada no, afina para a ponta. Devolve os nos (ponto,
    tangente, raio) para as folhas.
    ONDA 6b (item 47): o no era um anel claro (Bamboo_DS_Dry, 1,3 x o raio, 0,25) no MESMO intervalo em todos os
    colmos - lia fita adesiva. Agora o proprio colmo ALARGA no no (na cor do colmo) e, nos 'collars' nos de baixo (a
    altura do olho), volta ao raio 0,12 acima (a aresta do no: 1 anel a mais, ~os 10 tris do anel antigo): 1,10 x
    nesses (1,08 lia liso demais de perto, volta 2), 1,06 x nos de cima (so a quebra de faceta). Os entrenos
    crescem da base ao topo (0,8 -> 1,2 x o passo do colmo, o 1o curto) e o passo e de cada colmo (hash da posicao:
    nao consome o rng, o resto da touceira nao muda)"""
    k0 = 2.15 + 0.5 * hh("colmo", p0.x, p0.y)
    zs = [0.0]
    for i in range(14):
        s = k0 * (0.8 + 0.4 * min(1.0, zs[-1] / h)) * (0.55 if i == 0 else 0.92 + 0.16 * hh("entreno", p0.x, p0.y, i))
        if zs[-1] + s > h:
            break
        zs.append(zs[-1] + s)
    if h - zs[-1] > 1.2:
        zs.append(h)
    else:
        zs[-1] = h
    bp, br = [p0 - ZZ * 0.4], [r * 1.05]
    kink = vdir(rng.uniform(0, TAU)) * 0.05
    for i, zz in enumerate(zs[1:], 1):
        t = zz / h
        bp.append(p0 + splay * zz + bend * (t ** 2.2) * h + kink * (i % 2) * zz * 0.2 + ZZ * zz)
        br.append(r * (1.0 - 0.45 * t))
    pts, rads, nodes = [], [], []
    for i, (p, rr) in enumerate(zip(bp, br)):
        if 0 < i < len(bp) - 1:
            d = (bp[i + 1] - bp[i - 1]).normalized()
            nodes.append((p, d, rr))
            pts.append(p)
            rads.append(rr * (1.10 if i <= collars else 1.06))
            if i <= collars:
                pts.append(p + d * 0.12)
                rads.append(rr)
        else:
            pts.append(p)
            rads.append(rr)
    PK.taper_tube(mb, pts, rads, BAMB, n=5)
    nodes.append((bp[-1], (bp[-1] - bp[-2]).normalized(), br[-1]))
    return nodes


def leaf_fan(mb, p, rng, az0, n=4, Ln=2.0, up=-0.35, m="Leaf_DS_Bamboo"):
    for j in range(n):
        az = az0 + (j - (n - 1) / 2) * 0.62 + rng.uniform(-0.15, 0.15)
        d = Vector((math.cos(az), math.sin(az), up + rng.uniform(-0.2, 0.15)))
        leaf(mb, p + vdir(az) * 0.15, d, Ln * rng.uniform(0.85, 1.12), 0.3 * Ln, m, rng)


def bamboo_clump(mb, P, x, y, rng, h=20.0, n=5, toward=None, lean=0.0):
    """TOUCEIRA: n colmos do mesmo pe (anel de 1,4), abrindo em leque; os da beira do caminho se inclinam para ele
    acima de ~8 (tunel); 2 leques de folha nos 2 nos de cima de cada colmo + leque do topo; 1-2 brotos na base"""
    z = P.gz(x, y, L.bamboo_z(x, y))
    tris = 0
    a0 = rng.uniform(0, TAU)
    for k in range(n):
        a = a0 + TAU * k / n + rng.uniform(-0.4, 0.4)
        rr = rng.uniform(0.3, 1.4)
        p0 = Vector((x + math.cos(a) * rr, y + math.sin(a) * rr, P.gz(x + math.cos(a) * rr, y + math.sin(a) * rr, z)))
        hk = h * rng.uniform(0.78, 1.05)
        splay = vdir(a) * rng.uniform(0.03, 0.08)
        bend = (toward * lean if toward is not None else Vector()) + vdir(a) * rng.uniform(0.04, 0.1)
        r = rng.uniform(0.3, 0.44)
        nodes = culm(mb, p0, hk, r, splay, bend, rng)
        az = math.atan2(nodes[-1][0].y - y, nodes[-1][0].x - x) if (nodes[-1][0].xy - Vector((x, y))).length > 0.3 \
            else rng.uniform(0, TAU)
        # folhagem na metade de cima: leques alternados nos 3 nos de cima + leque do topo (massa que le de longe)
        for j, (p, d, rd) in enumerate(nodes[-3:-1]):
            leaf_fan(mb, p, rng, az + (1.3 if j % 2 else -1.3) + rng.uniform(-0.5, 0.5), n=4,
                     Ln=rng.uniform(3.0, 3.8))
        p, d, rd = nodes[-1]
        leaf_fan(mb, p, rng, az, n=5, Ln=rng.uniform(2.8, 3.4), up=0.35)
    for k in range(rng.randint(1, 2)):
        a = rng.uniform(0, TAU)
        q = Vector((x + math.cos(a) * 1.9, y + math.sin(a) * 1.9, 0.0))
        q.z = low_ground(P, q.x, q.y, 0.38, P.gz(q.x, q.y, z), drop=0.8)       # ONDA 6b (46): o broto boiava 0,33
        PK.cone(mb, q - ZZ * 0.3, q + ZZ * rng.uniform(0.9, 1.5), 0.38, 0.05, BAMB_DRY, n=5)
    col_box("DS_VegBamboo", (2.8, 2.8, 8.0), (x, y, z + 4.0))
    return z


# ================================================================== GLICINIA em trelica (mesma familia do ds_summon)
def wisteria_on_frame(mb, P, rng, trunk_xy, z, fc, u, v, au, av, top, min_bottom, posts=()):
    """glicinia CONDUZIDA numa trelica (fujidana): o tronco em S com o cone de raiz do ds_summon sobe junto de um
    esteio, abre 3 bracos sobre a trelica, TUFOS de folha (3 massas do ds_summon._blob) cobrindo ~60% do topo, massas
    de flor no tom fundo e a CORTINA de cachos (ds_summon.raceme) pendendo entre as ripas. fc = centro da trelica,
    u/v = eixos, au/av = meias-medidas, top = cota do topo das ripas; min_bottom(x, y) = cota minima da ponta do
    cacho naquele ponto (vao livre do caminho)"""
    tones = SUM.WIS_TONES
    bx, by = trunk_xy
    base = Vector((bx, by, z))
    cu = (base - fc).dot(u)
    cv = (base - fc).dot(v)
    corner = fc + u * max(-au + 0.6, min(au - 0.6, cu)) + v * max(-av + 0.6, min(av - 0.6, cv))
    head = Vector((corner.x, corner.y, top + 0.15))
    ph = rng.uniform(0, TAU)
    tr, rr = [], []
    for i in range(8):
        f = i / 7
        off = (head - base) * f
        wob = vdir(ph + f * 5.0) * math.sin(f * math.pi) * 0.7
        p = base + Vector((off.x, off.y, 0.0)) + wob + ZZ * ((top + 0.15 - z) * f - 0.3 * (1 - f))
        tr.append(p)
        rr.append(0.72 - 0.36 * f)
    PK.taper_tube(mb, tr, rr, BARK, n=8)
    PK.cone(mb, base - ZZ * 0.3, base + ZZ * 1.0, 1.15, 0.72, BARK, 8)
    # bracos sobre a trelica (saem da cabeca e atravessam o topo)
    su = 1.0 if cu >= 0 else -1.0
    sv = 1.0 if cv >= 0 else -1.0
    for k, (tu, tv) in enumerate(((-su * 0.9, -sv * 0.8), (-su * 0.9, sv * 0.5), (su * 0.3, -sv * 0.9))):
        e = fc + u * au * 0.9 * tu + v * av * 0.9 * tv
        e.z = top + 0.42
        mid = head.lerp(e, 0.5) + ZZ * 0.35
        PK.taper_tube(mb, [head, mid, e], [0.34, 0.24, 0.13], BARK, n=6)
    # tufos de folha sobre o topo (grade 3 x 3 desencontrada, ~7 tufos)
    used = []
    for iu in (-1, 0, 1):
        for iv in (-1, 0, 1):
            if rng.random() < 0.22 and (iu, iv) != (0, 0):
                continue
            c = fc + u * (iu * au * 0.62 + rng.uniform(-0.5, 0.5)) + v * (iv * av * 0.6 + rng.uniform(-0.4, 0.4))
            c.z = top + 0.55 + rng.uniform(0.0, 0.3)
            s_ = rng.uniform(1.0, 1.25)
            for j in range(3):
                aa = rng.uniform(0, TAU)
                SUM._blob(mb, c + vdir(aa) * s_ * 0.7 + ZZ * rng.uniform(-0.1, 0.25), s_ * rng.uniform(0.95, 1.15),
                          s_ * rng.uniform(0.75, 0.9), s_ * 0.5, "Leaf_DS_Broad", nu=8, rot=aa)
            if rng.random() < 0.55:
                aa = rng.uniform(0, TAU)
                SUM._blob(mb, c + vdir(aa) * s_ * 0.9 - ZZ * s_ * 0.2, s_ * 0.8, s_ * 0.66, s_ * 0.45, tones[0], nu=8,
                          rot=aa)
    # tufos que TRANSBORDAM a borda da trelica (a copa le de baixo e de lado, como as do summon) + cachos longos
    # pendendo deles por fora do vao de passagem
    n = 0
    for k in range(6):
        t = (k + rng.uniform(-0.2, 0.2)) / 6.0
        d = (t % 1.0) * (4 * au + 4 * av)
        if d < 2 * au:
            pu, pv = -au + d, -av - 0.5
        elif d < 2 * au + 2 * av:
            pu, pv = au + 0.5, -av + (d - 2 * au)
        elif d < 4 * au + 2 * av:
            pu, pv = au - (d - 2 * au - 2 * av), av + 0.5
        else:
            pu, pv = -au - 0.5, av - (d - 4 * au - 2 * av)
        c = fc + u * pu + v * pv
        c.z = top + 0.15
        s_ = rng.uniform(0.95, 1.15)
        if P.built is not None:                 # nada de tufo enfiado no beiral da casa (a propria trelica nao conta)
            hit = P.built.find_nearest(c, s_ * 1.6)
            if hit[0] is not None:
                q = hit[0] - fc
                if not (abs(q.dot(u)) < au + 1.3 and abs(q.dot(v)) < av + 1.3 and top - 1.6 < hit[0].z < top + 0.4):
                    continue
        for j in range(2):
            aa = rng.uniform(0, TAU)
            SUM._blob(mb, c + vdir(aa) * s_ * 0.6 + ZZ * rng.uniform(-0.05, 0.2), s_ * rng.uniform(0.95, 1.1),
                      s_ * rng.uniform(0.75, 0.9), s_ * 0.5, "Leaf_DS_Broad", nu=8, rot=aa)
        for j in range(3):
            aa = rng.uniform(0, TAU)
            q = c + vdir(aa) * rng.uniform(0.3, 1.1) * s_
            vis = min(rng.uniform(2.6, 3.8), top + 0.15 - 0.35 - min_bottom(q.x, q.y))
            if vis > 1.2:
                SUM.raceme(mb, Vector((q.x, q.y, top + 0.15)), vis, rng.uniform(0.3, 0.38), rng, tones)
                n += 1
    # cortina de cachos (grade desencontrada sob o topo)
    su = 1.5
    sv = 1.35
    k_u = int(au * 2 / su) + 1
    k_v = int(av * 2 / sv) + 1
    for i in range(k_u):
        for j in range(k_v):
            if rng.random() < 0.18:
                continue
            pu = -au + 0.4 + i * (2 * au - 0.8) / max(1, k_u - 1) + rng.uniform(-0.3, 0.3)
            pv = -av + 0.4 + j * (2 * av - 0.8) / max(1, k_v - 1) + rng.uniform(-0.3, 0.3)
            p = fc + u * pu + v * pv
            if any((Vector((p.x - q.x, p.y - q.y, 0.0))).length < 0.95 for q in posts):
                continue
            top_c = top + 0.25
            vis = rng.uniform(2.2, 3.5)
            lim = top_c - 0.35 - min_bottom(p.x, p.y)
            vis = min(vis, lim)
            if vis < 1.2:
                continue
            SUM.raceme(mb, Vector((p.x, p.y, top_c)), vis, rng.uniform(0.3, 0.38), rng, tones)
            n += 1
    col_box("DS_VegTrunk", (1.6, 1.6, 6.0), (bx, by, z + 3.0))
    return n


def bamboo_pole(mb, a, b, r=0.3, m=BAMB_DRY, nodes=True):
    a, b = Vector(a), Vector(b)
    PK.taper_tube(mb, [a, b], [r, r * 0.92], m, n=6)
    if nodes:
        d = (b - a)
        Ln = d.length
        d.normalize()
        k = max(1, int(Ln / 2.4))
        for i in range(1, k + 1):
            p = a + d * (Ln * i / (k + 1))
            PK.cone(mb, p - d * 0.08, p + d * 0.1, r * 1.3, r * 1.25, BAMB, n=6)


def bamboo_pergola(mb, mbw, P, rng):
    """4a glicinia (L.WISTERIA[3]): pergola de bambu velho ATRAVESSANDO o caminho calcado no topo do bambuzal (a
    transicao para a clareira, como nas refs 01/02/05), a glicinia nasce no ponto da planta (fora do caminho), sobe
    pelo esteio oeste e cobre o topo; cachos com a ponta >= 6,9 acima do caminho no vao de passagem"""
    wx, wy = L.WISTERIA[3]
    # ponto do caminho mais proximo da glicinia
    best = None
    for a_, b_ in zip(L.BAMBOO_RAMP, L.BAMBOO_RAMP[1:]):
        d_, t = L.seg_dist(wx, wy, a_[0], a_[1], b_[0], b_[1])
        if best is None or d_ < best[0]:
            best = (d_, (a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t),
                    Vector((b_[0] - a_[0], b_[1] - a_[1], 0.0)).normalized())
    _, (cx, cy), v = best
    u = Vector((wx - cx, wy - cy, 0.0)).normalized()          # +u = lado da glicinia (oeste)
    gz = P.gz(cx, cy, L.bamboo_z(cx, cy))
    fc = Vector((cx, cy, gz))
    au, av = 5.6, 2.6
    top = gz + 10.4
    for su in (-1, 1):
        for sv in (-1, 1):
            p = fc + u * su * au + v * sv * av
            zp = P.gz(p.x, p.y, gz)
            bamboo_pole(mb, (p.x, p.y, zp - 0.4), (p.x, p.y, top - 0.3), 0.34, BAMB_DRY)
            col_box("DS_VegPergola", (0.9, 0.9, top - zp), (p.x, p.y, (zp + top) / 2))
    # 2 vigas atravessando o caminho (sobre os esteios) e 5 ripas ao longo dele
    for sv in (-1, 1):
        a = fc + u * (-au - 0.9) + v * sv * av
        b = fc + u * (au + 0.9) + v * sv * av
        bamboo_pole(mb, (a.x, a.y, top - 0.62), (b.x, b.y, top - 0.62), 0.3, BAMB_DRY)
    for i in range(5):
        pu = -au + 0.6 + i * (2 * au - 1.2) / 4
        a = fc + u * pu + v * (-av - 1.0)
        b = fc + u * pu + v * (av + 1.0)
        bamboo_pole(mb, (a.x, a.y, top - 0.08), (b.x, b.y, top - 0.08), 0.18, BAMB, nodes=False)

    def min_bottom(x, y):
        """ONDA 6b (item 49): na faixa de 2,5 de cada lado do eixo do caminho o cacho termina >= piso + 8 (la a camera
        de 3a pessoa encosta, 10-12, e os cachos enchiam o topo do quadro); ate 3,8, >= + 6,9; fora, + 5,2. Piso
        LOCAL (a rampa sobe ao longo da pergola)"""
        q = Vector((x, y, 0.0)) - Vector((fc.x, fc.y, 0.0))
        lateral = abs(q.dot(u))
        g = max(gz, P.gz(x, y, gz))
        return g + (8.0 if lateral < 2.5 else (6.9 if lateral < 3.8 else 5.2))
    posts = [fc + u * su * au + v * sv * av for su in (-1, 1) for sv in (-1, 1)]
    n = wisteria_on_frame(mbw, P, rng, (wx, wy), P.gz(wx, wy, gz), fc, u, v, au, av, top + 0.1, min_bottom, posts)
    return n, (cx, cy, gz)


def v6_wisteria(mb, P, rng):
    """3a glicinia (L.WISTERIA[2]): pende da fujidana do jardim do V6 (ds_village: esteios em +-3,6 / +-3,2, ripas no
    topo a 8,66). O tronco nasce junto do esteio sudoeste e sobe por ele; cachos ate ~5,7 acima do jardim"""
    wx, wy = L.WISTERIA[2]
    gz = P.gz(wx, wy, T2)
    fc = Vector((wx, wy, gz))
    u, v = Vector((1.0, 0.0, 0.0)), Vector((0.0, 1.0, 0.0))
    top = gz + 8.66
    posts = [fc + u * sx * 3.6 + v * sy * 3.2 for sx in (-1, 1) for sy in (-1, 1)]
    # ONDA 6b: o pe saiu de (-2,75; -2,35) para (-2,2; +1,8) (esteio NOROESTE): a 1,2 do esteio SO o tronco (r 0,72
    # + ondulacao 0,7) e o cone de raiz (1,15) atravessavam o esteio e a pedra dele, e em y 350 o tronco entrava no
    # beiral da casa; a 2,0 do esteio NO, longe do beiral, ele sobe JUNTO do esteio sem entrar.
    # Cachos: o jardim nao e caminho (a rota do V6 passa no eixo da casa, a 12 daqui): pe-direito 5,6 sob a trelica
    n = wisteria_on_frame(mb, P, rng, (wx - 2.2, wy + 1.8), P.gz(wx - 2.2, wy + 1.8, gz), fc, u, v, 4.4, 3.9,
                          top, lambda x, y: gz + 5.6, posts)
    return n


# ================================================================== plano da vegetacao (pontos da planta + intencao)
# arvores largas: (chave, x, y, tipo, altura, raio da copa, rumo de abertura (graus) ou None)
BROAD_TREES = [
    ("ClrW", L.CLEARING_TREES[0][0], L.CLEARING_TREES[0][1], "keyaki", 25.0, 13.0, None),
    ("ClrSE", L.CLEARING_TREES[1][0], L.CLEARING_TREES[1][1], "keyaki", 27.0, 13.5, None),
    ("ClrNE", L.CLEARING_TREES[2][0], L.CLEARING_TREES[2][1], "momiji", 21.0, 10.5, None),
    ("VilLow", -90.0, 121.0, "momiji", 18.0, 10.0, None),        # substitui a do blockout (-86, 120): vila baixa
    ("VilBack", -126.0, 180.0, "keyaki", 24.0, 12.0, None),       # atras do V2/V3 (enquadra os telhados)
    ("VilHigh", -148.0, 306.0, "keyaki", 25.0, 12.0, None),       # substitui a do blockout (-146, 316): atras do V5/V6
    ("VilKura", -153.0, 280.0, "momiji", 18.0, 9.0, None),        # ao lado dos cedros do kura (borda oeste)
    ("Ravina", 141.0, 198.0, "momiji", 18.0, 9.5, None),          # margem leste: entre a clareira e a ravina
    ("SummonS", 194.0, 260.0, "keyaki", 21.0, 11.0, None),        # atras do plato do summon (enquadra a torre)
    ("BackW", -56.0, 534.0, "keyaki", 24.0, 14.0, None),          # moldura da forja (rochas do fundo)
    ("BackC", 14.0, 548.0, "keyaki", 25.0, 15.0, None),
    ("BackE", 70.0, 534.0, "momiji", 21.0, 12.0, None),
]
# pinheiros: (chave, x, y, altura, rumo da inclinacao (graus), inclinacao, alcance dos galhos)
PINES = [
    ("Entry", -30.0, 31.0, 15.0, 10.0, 0.42, 6.0),        # arvore-marco da entrada, debrucada sobre o patio
    ("Mirante", -38.0, 364.0, 13.0, 307.0, 0.5, 5.6),     # pe da subida, canto NO: torto sobre a clareira
    ("Promontorio", -152.0, 342.0, 13.0, 180.0, 0.5, 5.6),  # promontorio da vila alta, debrucado sobre o vazio
]
# cedros em grupos: (grupo, [(x, y, altura, raio)])
CEDARS = [
    ("Trilha", [(-44.0, 46.0, 22.0, 3.6), (-50.0, 62.0, 26.0, 4.0), (-47.0, 80.0, 20.0, 3.4), (-56.0, 92.0, 23.0, 3.7)]),
    ("Kura", [(-140.0, 242.0, 23.0, 3.7), (-147.0, 257.0, 26.0, 4.0), (-134.0, 266.0, 20.0, 3.3)]),
    ("VilaBaixaO", [(-138.0, 206.0, 21.0, 3.5), (-130.0, 150.0, 19.0, 3.3)]),
    ("Barranco", [(146.0, 346.0, 20.0, 3.4), (141.0, 364.0, 23.0, 3.7), (166.0, 343.0, 22.0, 3.6)]),
    ("Fundo", [(-20.0, 562.0, 22.0, 3.9), (104.0, 524.0, 19.0, 3.5), (-86.0, 528.0, 20.0, 3.7)]),
    ("Saida", [(-130.0, 472.0, 24.0, 3.7), (-128.0, 494.0, 21.0, 3.5), (-84.0, 548.0, 22.0, 3.6),
               (-80.0, 568.0, 25.0, 3.8), (-124.0, 562.0, 20.0, 3.4)]),
]
# mato baixo selvagem: pe de muro, borda da clareira, pe do plato do summon, beira da saida (o validador derruba o
# que cair em rota, escada, agua ou construido)
BUSHES = [(-47.0, 262.0, 2.6), (-50.0, 318.0, 2.8), (-45.0, 232.0, 2.3), (-48.0, 340.0, 2.4), (-46.0, 248.0, 1.6), (-14.0, 366.0, 1.7), (56.0, 377.0, 1.9),
          (-38.0, 182.0, 1.6), (96.0, 152.0, 1.8), (132.0, 214.0, 1.7), (146.0, 282.0, 1.7), (146.0, 320.0, 1.8),
          (-24.0, 64.0, 1.6), (10.0, 92.0, 1.5), (-120.0, 530.0, 1.8), (-92.0, 582.0, 1.6), (-40.0, 360.0, 1.5),
          (118.0, 236.0, 1.4), (-58.0, 360.0, 1.6), (-160.0, 300.0, 1.8)]
# arbustos podados (karikomi): perto das casas, no jardim do V6, nos pes de escada; o validador derruba quem cair em
# rua, porta, casa ou rota
SHRUBS = [(-54.0, 120.0, 1.6), (-74.0, 141.0, 1.4), (-76.0, 182.0, 1.7), (-84.0, 210.0, 1.4), (-108.0, 170.0, 1.8),
          (-104.0, 144.0, 1.5), (-92.0, 240.0, 1.5), (-90.0, 268.0, 1.6), (-114.0, 270.0, 1.5), (-91.0, 300.0, 1.4),
          (-88.0, 314.0, 1.6), (-88.0, 322.0, 1.3), (-89.0, 356.0, 1.5), (-97.0, 321.0, 1.2), (-112.0, 316.0, 1.3),
          (-4.0, 372.0, 1.5), (40.0, 373.0, 1.6), (-14.0, 398.0, 1.3), (132.0, 288.0, 1.4), (132.0, 313.0, 1.5),
          (-24.0, 46.0, 1.4), (20.0, 44.0, 1.3), (-36.0, 124.0, 1.5), (-44.0, 196.0, 1.4)]


# ================================================================== ONDA 4b: DENSIDADE DIRIGIDA
# A leitura do lead: a ilha lia esparsa demais contra as refs (copa densa ladeando TODOS os caminhos, bordas dos
# terracos e topo das falesias; moitas no pe dos muros; bambuzal cheio; massa verde emoldurando a clareira e a vila).
# Cada grupo abaixo tem um porque (fileira que ladeia um caminho, borda de terraco, moldura de capitulo); nada e
# espalhado por sorteio. As arvores novas sao da MESMA familia (keyaki / momiji / sugi) em versao LEVE (broad_lite:
# a mesma linguagem de massas em nuvem, metade das massas, sem os galhos ate cada massa) - custa ~1/2 e le igual de
# longe. Regras de cada sitio (site_ok): chao natural, fora da MiningZone, tronco a >= 7 + r da linha de rota (a faixa
# de ~2 entre a borda do caminho e o tronco fica para as lanternas e cercas do ds_props), fora de escada, agua, frente
# de casa (porta), ancoras de props, portao da vila; a copa nao fecha nenhuma VISADA protegida (forja: boca, salao,
# torre-chamine; estrela e torre do summon; portao OP) das PlayerHeight, das Ref_* e das visadas do gate do QA.
# (x, y, tipo, altura, raio da copa, chave/intencao)   tipo: K = keyaki leve, M = momiji leve, C = cedro
DEN_TREES = [
    # TRILHA: a crista oeste fecha o gargalo (copa debrucada sobre a escada), entre os cedros da crista
    (-56.0, 72.0, "K", 18.0, 9.0, "TrilhaCrista"), (-42.0, 63.0, "M", 14.0, 7.0, "TrilhaCrista"),
    # VILA BAIXA: atras das casas (borda oeste) e entre a rua e a clareira (moldura da rua vista da clareira)
    (-120.0, 134.0, "C", 22.0, 3.7, "VilaFundo"), (-120.0, 215.0, "M", 15.0, 8.0, "VilaFundo"),
    (-52.0, 186.0, "K", 18.0, 9.0, "VilaRua"), (-56.0, 216.0, "M", 13.0, 6.5, "VilaRua"),
    # VILA ALTA: fileira no topo do arrimo para a clareira (as refs: copas sobre o muro entre a vila e a clareira)
    (-62.0, 248.0, "K", 18.0, 9.0, "VilaAltaBorda"), (-60.0, 268.0, "C", 21.0, 3.7, "VilaAltaBorda"),
    (-58.0, 312.0, "K", 18.0, 9.5, "VilaAltaBorda"), (-60.0, 330.0, "M", 14.0, 7.0, "VilaAltaBorda"),
    (-86.0, 366.0, "K", 17.0, 8.5, "VilaAltaN"),          # gramado ao norte do jardim do V6, ao pe da OesteForja
    # CLAREIRA: moldura da borda (oeste ao pe do arrimo, sudeste junto do bambuzal, leste entre o canal e o summon,
    # norte ao pe da berma flanqueando a SubidaA); o miolo continua vazio
    (-28.0, 174.0, "M", 15.0, 7.5, "ClareiraO"), (-34.0, 246.0, "K", 17.0, 8.5, "ClareiraO"),
    (-34.0, 316.0, "M", 15.0, 7.5, "ClareiraO"), (-30.0, 340.0, "K", 18.0, 9.0, "ClareiraO"),
    (84.0, 146.0, "K", 18.0, 9.5, "ClareiraSE"), (124.0, 194.0, "M", 15.0, 8.0, "ClareiraSE"),
    (138.0, 252.0, "C", 19.0, 3.5, "ClareiraL"), (138.0, 282.0, "K", 16.0, 8.0, "ClareiraL"),
    (136.0, 322.0, "M", 14.0, 7.0, "ClareiraL"),
    # 6c: a keyaki do antecampo era (24; 138) R 9,5 = em cima da lanterna de no Antecampo (22; 138): o NUDGE tirava o
    # tronco, mas a copa ficava a 0,5 do chapeu dela. Agora 11 a leste e copa 7,5 (folga >= 2,5 da lanterna)
    (33.0, 140.0, "K", 17.0, 7.5, "ClareiraS"), (46.0, 140.0, "M", 14.0, 7.0, "ClareiraS"),
    (38.0, 362.0, "K", 17.0, 8.5, "ClareiraN"), (62.0, 358.0, "K", 18.0, 9.0, "ClareiraN"),
    (88.0, 366.0, "M", 13.0, 6.5, "ClareiraN"),
    # BARRANCO NE (topo da falesia sobre a lagoa)
    (135.0, 392.0, "K", 16.0, 8.0, "Barranco"), (132.0, 430.0, "C", 20.0, 3.5, "Barranco"),
    (156.0, 352.0, "M", 13.0, 6.5, "Barranco"),
    # BERMA: as 2 abas da subida (fora do corredor clareira -> boca da fornalha)
    (-24.0, 392.0, "K", 16.0, 8.5, "Berma"), (64.0, 410.0, "K", 17.0, 9.0, "Berma"),
    (84.0, 414.0, "M", 13.0, 6.5, "Berma"), (58.0, 390.0, "C", 19.0, 3.5, "Berma"),
    # TERRACO DA FORJA: borda oeste do patio do carvao, as 2 margens do caminho de saida, lobo leste (roda)
    (-140.0, 392.0, "C", 22.0, 3.8, "Carvao"), (-140.0, 484.0, "K", 18.0, 9.0, "Carvao"), (-138.0, 418.0, "K", 18.0, 9.0, "Carvao"),
    (-134.0, 446.0, "C", 20.0, 3.5, "Carvao"), (-100.0, 384.0, "M", 14.0, 7.0, "Carvao"),
    (-124.0, 508.0, "M", 13.0, 6.5, "SaidaO"), (-118.0, 548.0, "M", 13.0, 6.5, "SaidaO"),
    (-88.0, 474.0, "K", 17.0, 8.5, "SaidaL"), (-84.0, 500.0, "C", 21.0, 3.6, "SaidaL"),
    (124.0, 462.0, "C", 20.0, 3.5, "ForjaL"), (114.0, 500.0, "K", 16.0, 8.0, "ForjaL"),
    # FUNDO (rochas da montanha), longe da sela atras da chamine
    (-36.0, 548.0, "C", 22.0, 3.8, "Fundo"), (88.0, 556.0, "K", 17.0, 8.5, "Fundo"),
    # SUMMON: borda de tras do plato (enquadra a torre por tras, abaixo da estrela)
    (204.0, 286.0, "K", 14.0, 7.0, "Summon"), (206.0, 314.0, "M", 13.0, 6.0, "Summon"),
]
# arcos do contorno SEM franja de vegetacao (pontes, torii, mirante do summon, sangradouro, cascata, saida)
FRINGE_SKIP = [((0.0, 0.0), 30.0), ((-95.0, 594.0), 26.0), ((210.0, 300.0), 16.0), ((154.0, 230.0), 14.0),
               ((-97.0, 586.0), 22.0)]
WATER_LINES = (L.CHANNEL, L.TAILRACE, L.FLUME)


def front_of_house(x, y, reach=22.0):
    """ponto na frente de uma casa (lado da porta/rua) a menos de reach do centro"""
    for h in L.HOUSES:
        cx, cy = h[2], h[3]
        dx, dy = x - cx, y - cy
        if dx * dx + dy * dy > reach * reach:
            continue
        rum = math.radians(_HOUSE_RUMO.get(h[0], 0.0))
        if dx * math.cos(rum) + dy * math.sin(rum) > -2.0:
            return h[0]
    return None


_HOUSE_RUMO = {"V1": 15.0, "V2": 20.0, "V3": 23.0, "V4": -90.0, "V5": -6.0, "V6": 0.0}   # = ds_village.HOUSES


def _prop_anchors():
    try:
        import ds_village
        return [(a[1], a[2], a[4]) for a in ds_village.PROP_ANCHORS]
    except Exception:
        return []


def protected_views():
    """(olho, alvo) que copa nenhuma pode fechar: as visadas do gate do QA + forja/summon das PlayerHeight e Ref_*"""
    cams = L.cams()
    star = None
    o = bpy.data.objects.get("L_DSSum_Star")
    if o:
        star = o.location.copy()
    chim = Vector((L.CHIMNEY[0], L.CHIMNEY[1], L.CHIMNEY_TOP - 0.6))
    mouth = Vector((L.FURNACE_MOUTH[0], L.FURNACE_MOUTH[1] - 2.2, T4 + 6.0))
    hall = Vector((0.0, 486.0, T4 + 22.0))
    tower = [Vector((L.CHIMNEY[0], L.CHIMNEY[1], T4 + 56.0)), Vector((L.CHIMNEY[0], L.CHIMNEY[1] - 7.6, T4 + 46.0)),
             Vector((L.CHIMNEY[0] - 7.6, L.CHIMNEY[1] - 7.6, T4 + 40.0))]
    tower_c = Vector((L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], T3 + 30.0))
    forge = [chim, mouth, hall] + tower
    summ = [p for p in (star, tower_c) if p is not None]
    out = []
    for cn in L.PLAYER_CAMS + L.REF_CAMS + ["CAM_DS_Entry", "CAM_DS_Clearing", "CAM_DS_Forge", "CAM_DS_Summon"]:
        if cn not in cams:
            continue
        eye = Vector(cams[cn][0])
        tg = Vector(cams[cn][1])
        out.append((eye, tg))
        if "OnePiece" in cn:
            continue
        for p in forge + summ:
            out.append((eye, p))
    g = L.gate_op_pos()
    for eye, tgts in (((0.0, 150.0, T1 + L.EYE), [mouth]), ((L.MINE_C[0], L.MINE_C[1], T1 + L.EYE), [mouth]),
                      ((-12.0, 58.0, T1 + L.EYE), summ), ((-12.0, 64.0, T1 + L.EYE), summ),
                      ((30.0, 200.0, T1 + L.EYE), summ),
                      ((L.EXIT_START[0], L.EXIT_START[1] - 4.0, T4 + L.EYE), [Vector((g[0], g[1], T4 + 12.0))])):
        for p in tgts:
            out.append((Vector(eye), p))
    return out


def seg_point_dist(a, b, p):
    d = b - a
    t = max(0.0, min(1.0, (p - a).dot(d) / max(1e-9, d.length_squared)))
    return (a + d * t - p).length


def blocks_view(views, spheres):
    for e, t in views:
        for c, r in spheres:
            if seg_point_dist(e, t, c) < r + 0.8:
                return True
    return False


def tree_spheres(kind, x, y, z, h, R):
    if kind == "C":
        return [(Vector((x, y, z + h * 0.35)), R * 1.05), (Vector((x, y, z + h * 0.68)), R * 0.75)]
    return [(Vector((x, y, z + h * 0.62)), R * 0.92), (Vector((x, y, z + h * 0.86)), R * 0.62)]


# ================================================================== ONDA 6b (item 44): folga dos PROPS
# O ds_props roda DEPOIS do ds_veg (build_ds: dressing = veg, props, vfx, lights), entao a vegetacao nao enxerga as
# pecas dele no raio. As de posicao FIXA (lanternas de no, cercas dos setores, das bordas de terraco e dos caminhos,
# canto dos mineiros, candidatos de banco/placa/pilha) sao lidas do proprio modulo (sem copiar numero: se o ds_props
# muda uma cerca, a folga acompanha). As lanternas de caminho (posicao dinamica) ja desviam de tronco/moita no
# ds_props (raio lateral a +1 e +3,2); o que sobra embaixo disso (raiz, lamina de capim) sai no after_props().
PROP_GAP_TRUNK = 2.5            # face do tronco -> prop/cerca (auditoria 6a, item 44)
PROP_GAP_BUSH = 0.6             # borda da moita -> prop/cerca


def prop_keepout():
    """(pontos (x, y, raio), polilinhas) dos props de posicao fixa do ds_props"""
    pts, lines = [], []
    try:
        import ds_props as PR
    except Exception as e:
        print("AVISO ds_veg: ds_props nao importou (%s): sem folga de props" % e)
        return pts, lines
    for it in getattr(PR, "NODE_LAMPS", ()):
        pts.append((it[1], it[2], 1.3))
    m = getattr(PR, "MINERS", None)
    if m:
        pts.append((m[0], m[1], 3.4))
    for it in getattr(PR, "LIFE", ()):
        for q in it[2]:
            pts.append((q[0], q[1], 1.2))
    for it in getattr(PR, "FENCE_SECTORS", ()):
        lines.append([tuple(q) for q in it[1]])
    try:
        lines += [[tuple(q) for q in ln] for nm, ln in PR._fence_lines()]
    except Exception as e:
        print("AVISO ds_veg: ds_props._fence_lines falhou (%s): so FENCE_LINES" % e)
        lines += [[tuple(q) for q in ln] for nm, ln in getattr(PR, "FENCE_LINES", ())]
    return pts, [ln for ln in lines if len(ln) >= 2]


def prop_gap(x, y, ko):
    """distancia horizontal de (x, y) a BORDA do prop fixo mais proximo"""
    pts, lines = ko
    d = 1e9
    for px, py, pr in pts:
        d = min(d, math.hypot(x - px, y - py) - pr)
    for ln in lines:
        d = min(d, L.polyline_dist(x, y, ln))
    return d


def site_ok(P, x, y, r_trunk, ctx, route_gap=7.0, need_floor=False, ring=True, prop_min=None):
    """(z, None) se o pe pode nascer em (x, y); senao (None, motivo). ONDA 6b: prop_min = folga minima do centro ate
    a borda dos props fixos (ctx['ko'])"""
    if prop_min is not None and ctx.get("ko") and prop_gap(x, y, ctx["ko"]) < prop_min:
        return None, "prop"
    t = P.top(x, y)
    if t is None or not t[1].startswith(P.NATURAL):
        return None, "chao %s" % (t[1] if t else None)
    if t[3] < 0.6:
        return None, "inclinado"
    if need_floor and L.zone_of(x, y) is None:
        return None, "fora do piso"
    if in_mine(x, y, 6.0):
        return None, "zona"
    if P.route_dist(x, y) < route_gap + r_trunk:
        return None, "rota"
    if P.in_stairs(x, y, 3.0):
        return None, "escada"
    if any(L.polyline_dist(x, y, w) < 4.5 + r_trunk for w in WATER_LINES) or \
            L.point_in_poly(x, y, DL.offset_poly(L.POND, 2.0 + r_trunk)):
        return None, "agua"
    if front_of_house(x, y):
        return None, "frente de casa"
    for ax, ay, ar in ctx["anchors"]:
        if (x - ax) ** 2 + (y - ay) ** 2 < (ar + r_trunk + 2.5) ** 2:
            return None, "ancora"
    if not P.clear_of_built(Vector((x, y, t[0] + 1.5)), r_trunk + 2.5):
        return None, "construido"
    if ring:                                # a faixa da beira do caminho (lajes, rua, patio) fica livre
        for k in range(8):
            a = TAU * k / 8
            q = P.top(x + math.cos(a) * (r_trunk + 2.2), y + math.sin(a) * (r_trunk + 2.2))
            if q is not None and abs(q[0] - t[0]) < 2.5 and not q[1].startswith(P.NATURAL):
                return None, "beira de %s" % q[1]
    return t[0], None


def broad_lite(mb, P, x, y, rng, h=15.0, R=7.0, leaf_m=BROAD, dark=CEDAR, limbs=3, flat=0.86, lean=(0.0, 0.0),
               adjust=None, nroots=2, col=True):
    """a arvore larga da familia em versao LEVE: tronco curto e grosso (base alargada, 2 raizes que agarram o chao),
    forquilha baixa em 'limbs' bracos em vaso; COPA = 1 massa larga na ponta de cada braco + anel de cima recolhido
    (limbs - 1 massas, girado) + coroa + 1 massa interna escura (profundidade). Mesmas almofadas (pad) da familia."""
    z = P.gz(x, y, T1)
    base = Vector((x, y, z))
    r0 = 0.45 + R * 0.08
    lv = Vector((lean[0], lean[1], 0.0))
    hf = h * rng.uniform(0.28, 0.33)
    ph = rng.uniform(0, TAU)
    tp, tr = [], []
    for i in range(4):
        f = i / 3
        tp.append(base + lv * f * f * 0.6 + vdir(ph) * math.sin(f * math.pi) * 0.3 * r0 + ZZ * (hf * f - 0.5 * (1 - f)))
        tr.append(r0 * (1.32 if i == 0 else (1.1 - 0.3 * f)))
    tube(mb, tp, tr, n=6)
    F, rf = tp[-1], tr[-1]
    nr = roots(mb, P, base, r0, rng, n=nroots, reach=(1.8, 3.0)) if nroots else 0
    C0 = base + lv
    a0 = rng.uniform(0, TAU)
    pads = []

    def place(pc, s, m):
        if adjust:
            r_ = adjust(pc, s)
            if r_ is None:
                return
            pc, s = r_
        pads.append((pc, s, m))

    for k in range(limbs):
        a = a0 + TAU * k / limbs + rng.uniform(-0.25, 0.25)
        pc = C0 + vdir(a) * R * rng.uniform(0.5, 0.6) + ZZ * h * rng.uniform(0.52, 0.6)
        mid = F + vdir(a) * R * 0.22 + ZZ * h * 0.12
        tube(mb, [F - ZZ * 0.6, mid, pc - ZZ * 0.3], [rf * 0.72, rf * 0.5, rf * 0.3], n=5)
        place(pc, R * rng.uniform(0.46, 0.52), leaf_m)
    for k in range(max(1, limbs - 1)):
        a = a0 + math.pi / limbs + TAU * k / max(1, limbs - 1) + rng.uniform(-0.2, 0.2)
        place(C0 + vdir(a) * R * rng.uniform(0.26, 0.34) + ZZ * h * rng.uniform(0.72, 0.78), R * rng.uniform(0.44, 0.5),
              leaf_m)
    place(C0 + vdir(ph + 1.0) * R * 0.08 + ZZ * h * 0.88, R * 0.42, leaf_m)
    inner = C0 + vdir(a0 + math.pi) * R * 0.2 + ZZ * h * 0.6
    if adjust:
        r_ = adjust(inner, R * 0.44)
        inner = r_ if r_ else None
    else:
        inner = (inner, R * 0.44)
    for pc, s, m in pads:
        pad(mb, pc, s, m, rng, flat=flat, subs=1)
    if inner:
        cushion(mb, inner[0] - ZZ * inner[1] * 0.3, inner[1] * 1.05, inner[1] * 0.9, inner[1] * 0.8, dark, rng, n=6)
    if col and L.zone_of(x, y) is not None:
        col_box("DS_VegTrunk", (r0 * 2.0, r0 * 2.0, 7.0), (x, y, z + 3.5))
    return dict(top=max((pc.z + s * flat * 1.1 for pc, s, m in pads), default=z + h), pads=len(pads) + 1, roots=nr)


def cliff_tree(mb, P, x, y, z, rng, out_az, h=8.0, R=3.8, m=BROAD):
    """arvorezinha AGARRADA no topo de uma coluna da coroa: tronco que sai inclinado para o vazio e sobe em S (o
    vento da montanha), copa de 2-3 massas pequenas; sem colisao (ninguem chega la)"""
    base = Vector((x, y, z))
    d = vdir(out_az)
    pts = [base - ZZ * 0.5, base + d * 0.9 + ZZ * h * 0.25, base + d * 2.0 + ZZ * h * 0.55, base + d * 2.4 + ZZ * h * 0.8]
    tube(mb, pts, [0.62, 0.48, 0.34, 0.2], n=5)
    top = pts[-1]
    cushion(mb, top - ZZ * R * 0.35, R * 1.05, R * 0.85, R * 0.75, m, rng, n=7, rot=out_az)
    for k in range(rng.randint(1, 2)):
        a = out_az + (1.6 if k else -1.6) + rng.uniform(-0.4, 0.4)
        q = top + vdir(a) * R * 0.75 - ZZ * R * rng.uniform(0.25, 0.45)
        cushion(mb, q - ZZ * R * 0.2, R * 0.7, R * 0.58, R * 0.55, m, rng, n=6, rot=a)
    return top.z + R * 0.5


def densify(P, cells, trunks, make_adjust):
    """ONDA 4b: a densidade dirigida (arvores, saias de mato, franja das falesias, moitas de pe de muro)"""
    ctx = dict(anchors=_prop_anchors() + [(L.VILLAGE_GATE[0], L.VILLAGE_GATE[1], 6.0), (L.WELL[0], L.WELL[1], 5.0),
                                          (L.HOKORA[0], L.HOKORA[1], 4.0)] +
               [(wx, wy, 6.0) for wx, wy in L.WISTERIA], ko=ROOT_KO[0])
    views = protected_views()
    rej = STATS.setdefault("den_rejeitado", [])
    made = []
    # ---------------- arvores (fileiras e grupos dirigidos)
    t0 = _tris(cells)
    for i, (x0, y0, kind, h0, R0, grp) in enumerate(DEN_TREES):
        r_ = random.Random(zlib.crc32(("den%s%d" % (grp, i)).encode()))
        # o ponto da planta; se o pe nao serve (chanfro da coluna, beira de caminho...), procura ate 5 em volta; se a
        # copa fecha uma visada, a arvore encolhe (0,82 / 0,68) antes de desistir
        why0 = None
        found = None
        for ox, oy in NUDGE:
            x, y = x0 + ox, y0 + oy
            rt = 0.5 if kind == "C" else 0.45 + R0 * 0.08
            z, why = site_ok(P, x, y, rt * 1.3, ctx, prop_min=rt * 1.32 + PROP_GAP_TRUNK)
            if why is None and any(math.hypot(x - tx, y - ty) < tr + rt + 2.0 for tx, ty, tr in trunks):
                why = "tronco vizinho"
            if why is None:
                for sc in (1.0, 0.82, 0.68):
                    h, R = min(h0 * sc, TOP_MAX - z - 1.0), R0 * sc
                    if not blocks_view(views, tree_spheres(kind, x, y, z, h, R)):
                        found = (x, y, z, h, R)
                        break
                if found:
                    break
                why = "visada"
            why0 = why0 or why
        if not found:
            rej.append((grp, x0, y0, why0))
            continue
        x, y, z, h, R = found
        if (x, y) != (x0, y0) or R != R0:
            STATS.setdefault("den_ajustado", []).append((grp, x0, y0, round(x - x0, 1), round(y - y0, 1), round(R / R0, 2)))
        hh_ = h
        mb = cells.at(x, y)
        # colisao do tronco so onde o jogador circula (<= 26 de uma rota ou na clareira): o orcamento de COL_ da ilha
        # e compartilhado (1300); tronco no fundo atras das casas / na beira do contorno fica sem caixa
        colide = P.route_dist(x, y) < 26.0 or L.point_in_poly(x, y, L.CLEARING)
        if kind == "C":
            top = cedar(mb, P, x, y, r_, h=hh_, r=R, col=colide)
        else:
            kw = dict(leaf_m=SHRUB, dark=BROAD, limbs=4, flat=0.74) if kind == "M" else dict(leaf_m=BROAD, dark=CEDAR)
            top = broad_lite(mb, P, x, y, r_, h=hh_, R=R, adjust=make_adjust(R), col=colide, **kw)["top"]
        STATS["den_col"] = STATS.get("den_col", 0) + (1 if colide and L.zone_of(x, y) is not None else 0)
        made.append((x, y, kind, R, z))
        trunks.append((x, y, 2.0 if kind == "C" else 2.6))
        STATS.setdefault("den_arvores", 0)
        STATS["den_arvores"] += 1
    t1 = _tris(cells)
    # ---------------- saias de mato: 2-3 moitas no pe de cada arvore nova, do lado de FORA do caminho (a arvore
    # 'planta' no chao e o gramado vazio vira massa)
    nsk = 0
    for j, (x, y, kind, R, z) in enumerate(made):
        r_ = random.Random(7000 + j)
        # rumo de fora: para longe da rota mais proxima
        best = None
        for a in range(12):
            aa = TAU * a / 12
            d = P.route_dist(x + math.cos(aa) * 6.0, y + math.sin(aa) * 6.0)
            if best is None or d > best[0]:
                best = (d, aa)
        az = best[1]
        for k in range(2 if kind == "K" else (1 if kind == "M" else 0)):
            a = az + (k - 0.5) * 1.1 + r_.uniform(-0.3, 0.3)
            rr = (R * r_.uniform(0.55, 0.85)) if kind != "C" else r_.uniform(2.6, 3.6)
            bx, by = x + math.cos(a) * rr, y + math.sin(a) * rr
            br = r_.uniform(1.5, 2.3)
            zz, why = site_ok(P, bx, by, br, ctx, route_gap=4.0, ring=False, prop_min=br + PROP_GAP_BUSH)
            if why:
                continue
            bush(cells.at(bx, by), P, bx, by, r_, r=br, m=(CEDAR if (j + k) % 3 == 0 else BROAD))
            trunks.append((bx, by, br + 0.4))
            nsk += 1
    STATS["den_saias"] = nsk
    t2 = _tris(cells)
    # ---------------- franja das falesias: moitas e arvorezinhas agarradas no TOPO REAL das colunas da coroa
    STATS["den_franja"] = cliff_fringe(P, cells, ctx, views)
    t3 = _tris(cells)
    # ---------------- moitas de pe de muro (em setores, massas, nao tufos)
    STATS["den_pe_muro"] = wall_foot(P, cells, ctx, trunks)
    t4 = _tris(cells)
    STATS["den_tris"] = dict(arvores=t1 - t0, saias=t2 - t1, franja=t3 - t2, pe_muro=t4 - t3)
    return made


NUDGE = [(0.0, 0.0)] + [(math.cos(TAU * k / 8) * d, math.sin(TAU * k / 8) * d) for d in (2.5, 5.0) for k in range(8)]


def _tris(cells):
    return sum(sum(len(f.verts) - 2 for f in mb.bm.faces) for mb in cells.mbs.values())


def cliff_fringe(P, cells, ctx, views):
    """anda pelo contorno (passo de ciclo fixo); onde o raio de cima acha o topo de uma coluna da coroa (DS_Ter_Cliff,
    face de cima) a 0,3..4 abaixo do piso vizinho, a franja nasce: setores DIRIGIDOS pelo ruido de baixa frequencia
    (trechos verdes de 3-6 moitas + 1 arvorezinha agarrada a cada ~3 trechos, e trechos de rocha nua entre eles)"""
    rim = list(L.ISLAND_RIM)
    steps = (5.2, 4.1, 6.3, 4.6, 5.6)
    pts = []
    k = 0
    need = steps[0]
    for a, b in zip(rim, rim[1:] + rim[:1]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if ln < 1e-6:
            continue
        t = 0.0
        while ln - t >= need:
            t += need
            pts.append((a[0] + (b[0] - a[0]) * t / ln, a[1] + (b[1] - a[1]) * t / ln, (b[0] - a[0]) / ln, (b[1] - a[1]) / ln))
            k += 1
            need = steps[k % len(steps)]
        need -= ln - t
    n = nt = nf = 0
    sector = 0
    for i, (x, y, tx, ty) in enumerate(pts):
        if any(math.hypot(x - c[0], y - c[1]) < r for c, r in FRINGE_SKIP):
            continue
        g = noise.noise(Vector((x * 0.035, y * 0.035, 11.3)))
        if g < 0.04:
            sector = 0
            continue
        # normal para fora: o contorno e anti-horario? testa os 2 lados
        nx_, ny_ = ty, -tx
        if L.point_in_poly(x + nx_ * 6.0, y + ny_ * 6.0, L.ISLAND_RIM):
            nx_, ny_ = -nx_, -ny_
        best = None
        for off in (1.0, -0.5, 2.6, -2.0):
            px, py = x + nx_ * off, y + ny_ * off
            t = P.top(px, py)
            if t is None or not t[1].startswith("DS_Ter_Cliff") or t[3] < 0.7:
                continue
            best = (px, py, t[0])
            break
        if best is None:
            continue
        px, py, z = best
        zf = None
        for d in (5.0, 9.0, 14.0):
            zf = L.zone_of(px - nx_ * d, py - ny_ * d)
            if zf is not None:
                break
        if zf is not None and not (zf - 4.5 < z < zf - 0.2):
            continue
        if P.route_dist(px, py) < 6.0 or P.in_stairs(px, py, 3.0):
            continue
        if not P.clear_of_built(Vector((px, py, z + 1.0)), 2.6):
            continue
        r_ = random.Random(8800 + i)
        sector += 1
        out_az = math.atan2(ny_, nx_)
        # moita PENDURADA na face da falesia (as refs: verde agarrado nas colunas a meia altura), 1 a cada 3 pontos
        # do trecho verde: raio horizontal de fora para dentro numa cota de ciclo fixo abaixo do piso
        if sector % 3 == 1 and nf < FACE_MAX and zf is not None:
            zc = zf - FACE_DROPS[i % len(FACE_DROPS)]
            o = Vector((px + nx_ * 18.0, py + ny_ * 18.0, zc))
            hit = P.bvh.ray_cast(o, Vector((-nx_, -ny_, 0.0)), 30.0)
            if hit[0] is not None and P.own[hit[2]].startswith("DS_Ter_Cliff") and abs(hit[1].z) < 0.6:
                face_clump(cells.at(px, py), hit[0], Vector((hit[1].x, hit[1].y, 0.0)).normalized(),
                           r_.uniform(2.4, 3.4), (BROAD, CEDAR, SHRUB)[nf % 3], r_)
                nf += 1
        if sector % 7 == 3 and g > 0.12:
            hh_ = r_.uniform(7.0, 10.0)
            RR = r_.uniform(3.4, 4.6)
            sph = [(Vector((px + nx_ * 2.4, py + ny_ * 2.4, z + hh_ * 0.8)), RR)]
            if not blocks_view(views, sph):
                cliff_tree(cells.at(px, py), P, px, py, z, r_, out_az, h=hh_, R=RR, m=(BROAD, SHRUB, CEDAR)[i % 3])
                nt += 1
                continue
        br = r_.uniform(1.4, 2.4) * (1.0 + 0.4 * max(0.0, g))
        bush(cells.at(px, py), P, px, py, r_, r=br, m=(CEDAR if i % 4 == 0 else (SHRUB if i % 5 == 0 else BROAD)),
             n=5, lumps=2)
        n += 1
    return (n, nt, nf)


FACE_MAX = 20
FACE_DROPS = (7.5, 12.0, 9.0, 15.5, 10.5)


def face_clump(mb, p, nrm, r, m, rng):
    """moita agarrada na FACE de uma coluna: almofada achatada contra a rocha (metade enterrada na face) + 1 menor
    pendendo ao lado e abaixo (le como mato que desce da fresta). Sem colisao"""
    az = math.atan2(nrm.y, nrm.x)
    c = p + nrm * (r * 0.25) - ZZ * (r * 0.45)
    cushion(mb, c, r * 0.8, r * 1.1, r * 1.0, m, rng, n=5, rot=az, jit=0.15)
    side = vdir(az + math.pi / 2) * (r * rng.choice((-0.8, 0.8)))
    cushion(mb, c + side - ZZ * (r * 0.55), r * 0.55, r * 0.7, r * 0.7, m, rng, n=5, rot=az, jit=0.15)


def wall_foot(P, cells, ctx, trunks, budget=40):
    """moitas no PE dos muros de arrimo e das faces de rocha (vizinho 2+ mais alto, de muro/rocha), em SETORES (ruido
    de baixa frequencia) e com espacamento minimo: trechos de massa e trechos de muro limpo, nunca uma fita uniforme"""
    rim = L.ISLAND_RIM
    xs = [p[0] for p in rim]
    ys = [p[1] for p in rim]
    cand = []
    step = 3.0
    y = min(ys) + 1.0
    while y < max(ys):
        x = min(xs) + 1.0
        while x < max(xs):
            jx = x + (hh("wfx", x, y) - 0.5) * 2.0
            jy = y + (hh("wfy", x, y) - 0.5) * 2.0
            x += step
            if not L.point_in_poly(jx, jy, rim) or in_mine(jx, jy, 6.0):
                continue
            g = noise.noise(Vector((jx * 0.045, jy * 0.045, 7.1)))
            if g < 0.0:
                continue
            t = P.top(jx, jy)
            if t is None or not t[1].startswith(P.NATURAL) or t[3] < 0.8 or L.zone_of(jx, jy) is None:
                continue
            z0 = t[0]
            wall = None
            for a in range(8):
                aa = TAU * a / 8
                q = P.top(jx + math.cos(aa) * 2.6, jy + math.sin(aa) * 2.6)
                if q is not None and q[0] - z0 > 2.0 and q[1].startswith(P.WALLS):
                    wall = aa
                    break
            if wall is None:
                continue
            cand.append((g + 0.3 * hh("wfw", jx, jy), jx, jy, wall))
        y += step
    cand.sort(reverse=True)
    n = 0
    placed = []
    for w, x, y, wall in cand:
        if n >= budget:
            break
        r_ = random.Random(zlib.crc32(("wf%.1f%.1f" % (x, y)).encode()))
        br = r_.uniform(1.6, 2.6)
        if any(math.hypot(x - px, y - py) < br + pr + 0.6 for px, py, pr in placed):
            continue
        if any(math.hypot(x - tx, y - ty) < tr + br * 0.5 for tx, ty, tr in trunks):
            continue
        zz, why = site_ok(P, x, y, br, ctx, route_gap=4.2, ring=False, prop_min=br + PROP_GAP_BUSH)
        if why:
            continue
        bush(cells.at(x, y), P, x, y, r_, r=br, m=(CEDAR if n % 3 == 0 else BROAD))
        placed.append((x, y, br))
        trunks.append((x, y, br + 0.4))
        n += 1
    return n


# ================================================================== objetos por celula
CELL = 140.0
CELL_X0, CELL_Y0 = -185.0, -20.0
CELL_NAMES = {(0, 0): "SW", (1, 0): "Entrada", (2, 0): "Leste", (0, 1): "VilaBaixa", (1, 1): "Clareira",
              (2, 1): "ClareiraL", (0, 2): "VilaAlta", (1, 2): "ClareiraN", (2, 2): "Summon", (0, 3): "Carvao",
              (1, 3): "Forja", (2, 3): "ForjaL", (0, 4): "Saida", (1, 4): "Fundo", (2, 4): "FundoL"}


class Cells:
    def __init__(self):
        self.mbs = {}

    def key(self, x, y):
        return (max(0, min(2, int((x - CELL_X0) // CELL))), max(0, min(4, int((y - CELL_Y0) // CELL))))

    def at(self, x, y):
        k = self.key(x, y)
        if k not in self.mbs:
            nm = "DS_Veg_" + CELL_NAMES.get(k, "C%d_%d" % k)
            self.mbs[k] = MB(nm, C, random.Random(zlib.crc32(nm.encode())), detail="far", floor=-999)
        return self.mbs[k]

    def finish(self):
        out = []
        for k, mb in sorted(self.mbs.items()):
            ob = mb.finish()
            if ob:
                out.append(ob)
        return out


# ================================================================== grama em manchas (so bordas)
def zone_density(P, x, y):
    """densidade por capitulo (secao 5): entrada baixa, vila media-alta, clareira = 0 no miolo crescendo para fora,
    forja so no fundo, saida baixa"""
    nm = L.floor_name(x, y)
    if nm == "T1":
        if L.point_in_poly(x, y, L.CLEARING):
            x0, y0, x1, y1 = L.MINE_RECT
            dx = max(x0 - x, 0.0, x - x1)
            dy = max(y0 - y, 0.0, y - y1)
            d = math.hypot(dx, dy)
            return max(0.0, min(1.0, (d - 4.0) / 22.0)) * 0.95
        return 0.75 if x < -30 else 0.55                  # vila baixa / trilha
    return {"Bamboo": 0.6, "VillageHigh": 0.8, "Berm": 0.6, "Summon": 0.45, "Forge": 0.25, "ExitLand": 0.4,
            "Entry": 0.0}.get(nm, 0.35)


def grass(P, cells, rng, budget=280, avoid_pts=()):
    """manchas de capim SO em bordas: pe de muro / arrimo / rocha (vizinho 2+ mais alto), transicao grama -> terra
    (beira de caminho, borda da clareira), margem da lagoa e pe das arvores. Ruido de baixa frequencia agrupa os tufos
    em MANCHAS; a densidade de cada capitulo multiplica. Nada na MiningZone + 3, em rota, escada, agua ou laje."""
    rim = L.ISLAND_RIM
    xs = [p[0] for p in rim]
    ys = [p[1] for p in rim]
    step = 2.1
    cand = []
    y = min(ys) + 1.0
    while y < max(ys):
        x = min(xs) + 1.0
        while x < max(xs):
            jx = x + (hh("gx", x, y) - 0.5) * 1.6
            jy = y + (hh("gy", x, y) - 0.5) * 1.6
            x += step
            if not L.point_in_poly(jx, jy, rim) or in_mine(jx, jy):
                continue
            dz = zone_density(P, jx, jy)
            if dz <= 0.0:
                continue
            nz = noise.noise(Vector((jx * 0.09, jy * 0.09, 3.7)))       # manchas
            patch = max(0.0, min(1.0, (nz + 0.15) * 2.2))
            if dz * patch < 0.05:
                continue
            t = P.top(jx, jy)
            if t is None or not t[1].startswith(P.NATURAL) or t[3] < 0.8 or not t[2].startswith(("Grass_DS", "Dirt_DS")):
                continue
            z0 = t[0]
            score = 0.0
            on_grass = t[2].startswith("Grass_DS")
            for a in (0.0, 1.5708, 3.1416, 4.7124, 0.785, 2.356, 3.927, 5.498):
                q = P.top(jx + math.cos(a) * 2.0, jy + math.sin(a) * 2.0)
                if q is None:
                    continue
                if q[0] - z0 > 1.6 and q[1].startswith(P.WALLS):
                    score = max(score, 1.0)                 # pe de muro / arrimo / rocha
                elif on_grass and q[2].startswith("Dirt_DS") and abs(q[0] - z0) < 0.6:
                    score = max(score, 0.7)                 # beira de caminho / transicao para a terra
                elif not q[1].startswith(P.NATURAL) and q[0] - z0 > 0.25 and q[0] - z0 < 4.0:
                    score = max(score, 0.55)                # pe de lajes, socos, pedras de borda
            if score == 0.0:
                continue
            if P.route_dist(jx, jy) < 1.8 or P.in_stairs(jx, jy, 1.2):
                continue
            if L.point_in_poly(jx, jy, DL.offset_poly(L.POND, 1.2)) or L.polyline_dist(jx, jy, L.CHANNEL) < 3.4:
                continue
            if any((jx - ax) ** 2 + (jy - ay) ** 2 < ar * ar for ax, ay, ar in avoid_pts):
                continue
            w = score * dz * patch
            if w > 0.05:
                cand.append((w * (0.6 + 0.4 * hh("gw", jx, jy)), jx, jy, z0, score))
            continue
        y += step
    cand.sort(reverse=True)
    n = tris = 0
    for w, x, y, z, score in cand[:budget]:
        s = (0.75 + 0.75 * score) * rng.uniform(0.8, 1.1)
        tris += tuft(cells.at(x, y), x, y, z, rng, s, P=P)
        n += 1
    return n, tris, len(cand)


# ================================================================== bambuzal
def sightlines():
    """visadas do QA que o bambu nao pode fechar: topo da trilha -> estrela do summon (e o centro da torre)"""
    out = []
    star = bpy.data.objects.get("L_DSSum_Star")
    tgt = [star.location.copy()] if star else []
    tgt.append(Vector((L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], T3 + 30.0)))
    for eye in (Vector((-12.0, 58.0, T1 + L.EYE)), Vector((-12.0, 64.0, T1 + L.EYE))):
        for t in tgt:
            out.append((eye, t))
    return out


def line_cap(x, y, r, lines):
    """altura maxima (cota) que uma touceira em (x, y) de raio r pode ter sem cortar as visadas"""
    cap = 1e9
    for e, t in lines:
        d = t - e
        L2 = d.x * d.x + d.y * d.y
        k = max(0.0, min(1.0, ((x - e.x) * d.x + (y - e.y) * d.y) / L2))
        px, py = e.x + d.x * k, e.y + d.y * k
        if math.hypot(x - px, y - py) < r + 3.0:
            cap = min(cap, e.z + d.z * k - 1.2)
    return cap


def _ramp_station(ramp, s):
    acc = 0.0
    for a, b in zip(ramp, ramp[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if acc + ln >= s or b == ramp[-1]:
            t = min(1.0, (s - acc) / ln)
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        acc += ln


BAMBOO_MAX = 29                 # ONDA 4b: 23 -> 29 touceiras (bambuzal cheio das refs 02/04)
BAMBOO_SEEDS_4B = [(22.0, 72.0), (24.0, 98.0), (22.0, 120.0), (100.0, 140.0)]


def bamboo_grove(P, mb, rng, wis_c):
    """o bambu cresce em MOITAS (rizoma): 3-4 touceiras juntas por moita. Moitas de beira alternam os lados do
    caminho (as touceiras da beira se debrucam sobre ele: tunel), moitas de fundo encostam na borda da ilha; entre
    elas ficam clareiras de capim (a nevoa baixa do FX_Mist_Bamboo assenta ali). As visadas trilha -> summon limitam
    a altura de quem fica no caminho delas."""
    lines = sightlines()
    ramp = L.BAMBOO_RAMP
    seeds = []
    s_tot = L.plen(ramp)
    s = 8.0
    side = 1
    while s < s_tot - 6.0:
        (px, py), (tx, ty) = _ramp_station(ramp, s)
        off = rng.uniform(10.0, 12.5)
        seeds.append((px - ty * off * side, py + tx * off * side, "edge", (ty * side, -tx * side)))
        side = -side
        s += rng.uniform(17.0, 22.0)
    # ONDA 4b: moitas na aba oeste (o bambu fecha o lado leste da Trilha, sobre o arrimo) e no fundo leste
    for sx, sy in BAMBOO_SEEDS_4B:
        seeds.append((sx, sy, "deep", None))
    for i in range(300):
        x = rng.uniform(8.0, 122.0)
        y = rng.uniform(0.0, 152.0)
        if L.point_in_poly(x, y, L.BAMBOO) and L.polyline_dist(x, y, ramp) > 17.0 \
                and all(math.hypot(x - q[0], y - q[1]) > 17.0 for q in seeds):
            seeds.append((x, y, "deep", None))
    made = []
    for sx, sy, kind, tw in seeds:
        nwant = rng.randint(3, 4)
        got = 0
        for k in range(30):
            if got >= nwant or len(made) >= BAMBOO_MAX:
                break
            if got == 0:
                x, y = sx, sy
            else:
                a = rng.uniform(0, TAU)
                d = rng.uniform(4.4, 6.0)
                x, y = sx + math.cos(a) * d, sy + math.sin(a) * d
            if not L.point_in_poly(x, y, L.BAMBOO) or L.floor_name(x, y) != "Bamboo":
                continue
            dpath = L.polyline_dist(x, y, ramp)
            if dpath < 6.6:
                continue
            if L.poly_edge_dist(x, y, L.BAMBOO) < 2.4:
                continue
            if any(math.hypot(x - m[0], y - m[1]) < 4.4 for m in made):
                continue
            if math.hypot(x - wis_c[0], y - wis_c[1]) < 9.5 or math.hypot(x - L.WISTERIA[3][0], y - L.WISTERIA[3][1]) < 4.5:
                continue
            if P.route_dist(x, y) < 5.0 or P.in_stairs(x, y, 2.0):
                continue
            if P.ground(x, y) is None:
                continue
            z = P.gz(x, y, L.bamboo_z(x, y))
            h = rng.uniform(17.0, 22.5)
            cap = line_cap(x, y, 2.5, lines)
            if cap - z < 10.0:
                continue
            h = min(h, cap - z)
            toward = None
            lean = 0.0
            if kind == "edge" and tw is not None and dpath < 11.0:
                toward = Vector((tw[0], tw[1], 0.0))
                lean = rng.uniform(0.1, 0.16)
            bamboo_clump(mb, P, x, y, rng, h=h, n=5 if h > 15.0 else 4, toward=toward, lean=lean)
            made.append((x, y, kind, h))
            got += 1
    return made


# ================================================================== BUILD
def drop_blockout_veg():
    """a vegetacao do blockout (e as colisoes dela) sai"""
    for o in [o for o in bpy.data.objects if o.name.startswith(("DS_Veg_Blockout", "COL_DS_VegTrunk", "COL_DS_VegBamboo"))]:
        bpy.data.objects.remove(o, do_unlink=True)


def build():
    drop_blockout_veg()
    bpy.context.view_layer.update()
    P = Probe()
    cells = Cells()
    rng = random.Random(30303)
    tops = []
    trunks = []
    KO = prop_keepout()
    ROOT_KO[0] = KO
    STATS["props_fixos"] = (len(KO[0]), len(KO[1]))

    def fixed_spot(key, x, y, r):
        """arvore de ponto FIXO da planta: se encosta num prop fixo, procura o ponto mais perto (NUDGE) com folga,
        chao natural e longe da rota; senao fica e avisa"""
        if prop_gap(x, y, KO) >= r + PROP_GAP_TRUNK:
            return x, y
        for ox, oy in NUDGE[1:]:
            qx, qy = x + ox, y + oy
            t = P.top(qx, qy)
            if t is None or not t[1].startswith(P.NATURAL) or t[3] < 0.6 or P.route_dist(qx, qy) < 5.0 + r:
                continue
            if prop_gap(qx, qy, KO) >= r + PROP_GAP_TRUNK:
                STATS.setdefault("fixa_deslocada", []).append((key, x, y, round(ox, 1), round(oy, 1)))
                return qx, qy
        print("AVISO ds_veg: %s em (%.1f, %.1f) a %.1f de um prop fixo" % (key, x, y, prop_gap(x, y, KO)))
        return x, y

    def avoid_canal(x, y):
        return L.polyline_dist(x, y, L.CHANNEL) < 3.4 or L.point_in_poly(x, y, DL.offset_poly(L.POND, 1.6))

    def make_adjust(R):
        def adj(c, s):
            c = c.copy()
            # sobre a MiningZone (+ massa) a folha fica acima de piso + 12,6
            if in_mine(c.x, c.y, pad=s * 1.05 + 1.0) and c.z - s * 0.4 < CLEAR_TOP:
                c.z = CLEAR_TOP + s * 0.4
            if c.z + s * 1.0 > TOP_MAX:
                c.z = TOP_MAX - s * 1.0
            # copa nao atravessa casa, forja, torre, ponte...: encolhe ate 2 vezes, senao a massa sai
            for k in range(3):
                if P.clear_of_built(c, s * 1.15):
                    return c, s
                s *= 0.8
            STATS.setdefault("massas_cortadas", 0)
            STATS["massas_cortadas"] += 1
            return None
        return adj

    # ---------------- arvores largas
    for key, x, y, kind, h, R, face in BROAD_TREES:
        x, y = fixed_spot(key, x, y, 0.5 + R * 0.09)
        r_ = random.Random(zlib.crc32(key.encode()))
        mb = cells.at(x, y)
        zg = P.gz(x, y, T1)
        h = min(h, TOP_MAX - zg - 1.0)
        kw = dict(h=h, R=R, adjust=make_adjust(R), avoid=avoid_canal if key == "ClrNE" else None)
        if kind == "momiji":
            kw.update(leaf_m=SHRUB, dark=BROAD, limbs=4, flat=0.74)
        else:
            kw.update(leaf_m=BROAD, dark=CEDAR, limbs=3, flat=0.9)
        if key == "ClrNE":
            # tronco a 0,7 a oeste do ponto da planta: a base alargada nao encosta no muro do canal (x 117,2)
            kw.update(shift=(-0.7, 0.0), lean=(-1.2, -0.4), r_scale=0.85)
        elif key == "ClrW":
            # a copa se debruca sobre a borda da clareira (leste), nao sobre a rua da vila (PlayerHeight_Village limpa)
            kw.update(lean=(3.0, 0.8))
        info = broad_tree(mb, P, x, y, r_, **kw)
        tops.append((info["top"], "DS_Veg arvore " + key))
        trunks.append((x, y, 3.0))
        STATS["tree_" + key] = (round(zg, 1), round(info["top"], 1), info["pads"], info["roots"])
    # ---------------- pinheiros
    for key, x, y, h, az, lean, reach in PINES:
        x, y = fixed_spot("pine" + key, x, y, 1.6)
        r_ = random.Random(zlib.crc32(("pine" + key).encode()))
        adj = make_adjust(reach)
        info = pine(cells.at(x, y), P, x, y, r_, h=h, lean_az=math.radians(az), lean=lean, reach=reach, adjust=adj)
        tops.append((info["top"], "DS_Veg pinheiro " + key))
        trunks.append((x, y, 2.5))
        STATS["pine_" + key] = (round(info["base"].z, 1), round(info["top"], 1), info["pads"])
    # ---------------- cedros
    for grp, lst in CEDARS:
        for i, (x, y, h, r) in enumerate(lst):
            x, y = fixed_spot("cedar%s%d" % (grp, i), x, y, 0.4 + r * 0.12)
            r_ = random.Random(zlib.crc32(("cedar%s%d" % (grp, i)).encode()))
            if P.ground(x, y) is None:
                STATS.setdefault("cedar_rejeitado", []).append((grp, x, y))
                continue
            if not P.clear_of_built(Vector((x, y, P.gz(x, y, T1) + h * 0.5)), r + 0.5):
                STATS.setdefault("cedar_rejeitado", []).append((grp, x, y, "construido"))
                continue
            top = cedar(cells.at(x, y), P, x, y, r_, h=h, r=r)
            tops.append((top, "DS_Veg cedro " + grp))
            trunks.append((x, y, 2.0))
    # ---------------- bambuzal + pergola com a 4a glicinia
    mbb = MB("DS_Veg_Bamboo", C, random.Random(7701), detail="far", floor=-999)
    mbw = MB("DS_Veg_Wisteria", C, random.Random(7702), detail="far", floor=-999)
    nw4, wis_c = bamboo_pergola(mbb, mbw, P, random.Random(4104))
    clumps = bamboo_grove(P, mbb, random.Random(7703), wis_c)
    STATS["bamboo_clumps"] = len(clumps)
    for x, y, k, h in clumps:
        trunks.append((x, y, 2.4))
    nw3 = v6_wisteria(mbw, P, random.Random(4103))
    STATS["wisteria_racemes"] = (nw3, nw4)
    # ---------------- mato baixo selvagem
    nb = 0
    for i, (x, y, r) in enumerate(BUSHES):
        r_ = random.Random(9300 + i)
        t = P.top(x, y)
        why = None
        if t is None or not t[1].startswith(P.NATURAL):
            why = "chao %s" % (t[1] if t else None)
        elif in_mine(x, y, 5.0):
            why = "zona"
        elif P.route_dist(x, y) < r + 1.6:
            why = "rota"
        elif P.in_stairs(x, y, 1.0):
            why = "escada"
        elif L.polyline_dist(x, y, L.CHANNEL) < 3.4 + r or L.point_in_poly(x, y, DL.offset_poly(L.POND, 1.6 + r)):
            why = "agua"
        elif not P.clear_of_built(Vector((x, y, t[0] + 0.8)), r + 0.4):
            why = "construido"
        elif prop_gap(x, y, KO) < r + PROP_GAP_BUSH:
            why = "prop"                        # ONDA 6b: (-38, 182) era o vagonete dos mineiros; 2 na cerca da Vila
        if why:
            STATS.setdefault("mato_rejeitado", []).append((x, y, why))
            continue
        bush(cells.at(x, y), P, x, y, r_, r=r, m=BROAD if i % 3 else CEDAR)
        trunks.append((x, y, r + 0.5))
        nb += 1
    STATS["mato"] = nb
    # ---------------- karikomi
    nk = 0
    for i, (x, y, r) in enumerate(SHRUBS):
        r_ = random.Random(9100 + i)
        t = P.top(x, y)
        why = None
        if t is None or not t[1].startswith(P.NATURAL):
            why = "chao %s" % (t[1] if t else None)
        elif in_mine(x, y, 5.0):
            why = "zona"
        elif P.route_dist(x, y) < r + 1.6:
            why = "rota"
        elif P.in_stairs(x, y, 1.0):
            why = "escada"
        elif not P.clear_of_built(Vector((x, y, t[0] + 0.8)), r + 0.6):
            why = "construido"
        elif prop_gap(x, y, KO) < r + PROP_GAP_BUSH:
            why = "prop"
        if why:
            STATS.setdefault("karikomi_rejeitado", []).append((x, y, why))
            continue
        # ONDA 6b (item 48): o karikomi era Leaf_DS_Shrub (66/104/56), a 11 da grama B (76/108/58): sumia no chao sem
        # textura. Agora no verde de copa (Broad 46/84/48) e, 1 em 3, no escuro (Cedar 34/66/46: o buxo/azaleia
        # podado classico) - nenhum material novo (as celulas ja tem os dois: 0 MeshPart)
        karikomi(cells.at(x, y), P, x, y, r_, r=r, lumps=1 + (i % 3 != 0) + (i % 4 == 0),
                 m=CEDAR if i % 3 == 0 else BROAD)
        trunks.append((x, y, r + 0.6))
        nk += 1
    STATS["karikomi"] = nk
    # ---------------- ONDA 4b: densidade dirigida (arvores leves, saias, franja das falesias, pe de muro)
    densify(P, cells, trunks, make_adjust)
    # ---------------- grama em manchas
    # ONDA 4b: 280 -> 170 tufos (o orcamento foi para as massas; as moitas novas ja fazem a transicao das bordas)
    n, tris, nc = grass(P, cells, random.Random(5150), budget=170, avoid_pts=trunks)
    STATS["grass"] = (n, tris, nc)
    objs = cells.finish()
    for mb in (mbb, mbw):
        ob = mb.finish()
        if ob:
            objs.append(ob)
    tops.sort(reverse=True)
    STATS["top"] = tops[:3]
    tt = 0
    for o in objs:
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        tt += t
        print("DS_VEG obj %-22s tris=%6d mats=%d" % (o.name, t, len(o.data.materials)))
    print("DS_VEG ok: objetos=%d tris=%d %s" % (len(objs), tt, STATS))
    return objs


# ================================================================== ONDA 6b (item 44): conferencia DEPOIS dos props
SMALL_ISLAND = 4.6              # maior lado de uma ilha "pequena" (raiz, lamina de capim, broto, almofada de moita)


def after_props():
    """chamada pelo ds_lights (o ultimo do dressing), com os props JA montados: cada ilha de malha da vegetacao e
    testada (BVH.overlap) contra as malhas DS_Prop_* e DS_Ent_Toro. Ilha PEQUENA (raiz, lamina de capim, broto,
    almofada de moita: maior lado < SMALL_ISLAND) que atravessa um prop SAI - as lanternas de caminho do ds_props
    escolhem o lugar depois da vegetacao e o raio lateral delas (a +1 do chao) nao ve raiz nem capim. Ilha grande
    (tronco, copa) ou ilha alta (massa de copa encostando num poste) que atravessa prop = FALHA de colocacao: so
    AVISO (resolver em prop_keepout/site_ok).
    Devolve (ilhas removidas, ilhas grandes em conflito)."""
    import bmesh
    objs = [o for o in bpy.data.objects if o.type == "MESH" and not o.hide_render and
            o.name.startswith(("DS_Prop_", "DS_Ent_Toro"))]
    V, Pp = [], []
    for o in objs:
        mw = o.matrix_world
        b = len(V)
        V += [mw @ v.co for v in o.data.vertices]
        Pp += [[b + i for i in p.vertices] for p in o.data.polygons]
    if not Pp:
        print("ds_veg after_props: sem props")
        return 0, []
    PB = BVHTree.FromPolygons(V, Pp)
    removed, big = 0, []
    for ob in [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("DS_Veg_")]:
        mw = ob.matrix_world
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        seen = set()
        kill = []
        for v0 in bm.verts:
            if v0.index in seen:
                continue
            isl, stack = [], [v0]
            seen.add(v0.index)
            while stack:
                v = stack.pop()
                isl.append(v)
                for e in v.link_edges:
                    w = e.other_vert(v)
                    if w.index not in seen:
                        seen.add(w.index)
                        stack.append(w)
            co = [mw @ v.co for v in isl]
            lo = Vector((min(c.x for c in co), min(c.y for c in co), min(c.z for c in co)))
            hi = Vector((max(c.x for c in co), max(c.y for c in co), max(c.z for c in co)))
            c = (lo + hi) / 2
            if PB.find_nearest(c, (hi - lo).length / 2 + 0.05)[0] is None:
                continue
            idx = {v.index: i for i, v in enumerate(isl)}
            fs = {f for v in isl for f in v.link_faces}
            tb = BVHTree.FromPolygons(co, [[idx[v.index] for v in f.verts] for f in fs])
            if not tb.overlap(PB):
                continue
            zf = L.zone_of(c.x, c.y)
            if max(hi - lo) < SMALL_ISLAND and lo.z < (lo.z if zf is None else zf) + 1.5:   # so o que nasce no chao
                kill += isl
                removed += 1
            else:
                big.append((ob.name, round(c.x, 1), round(c.y, 1), round(c.z, 1)))
        if kill:
            bmesh.ops.delete(bm, geom=kill, context="VERTS")
            bm.to_mesh(ob.data)
            ob.data.update()
        bm.free()
    print("ds_veg after_props: %d ilhas pequenas (raiz/capim/moita) que atravessavam props removidas" % removed)
    for b_ in big:
        print("AVISO ds_veg: tronco/copa atravessando prop: %s (%.1f, %.1f, %.1f)" % b_)
    return removed, big


# ================================================================== CAMERAS da zona (folhas da onda 3a)
def _cams():
    wx, wy = L.WISTERIA[3]
    vx, vy = L.WISTERIA[2]
    return {
        "CAM_DSVeg_TreeW": ((-12.0, 128.0, T1 + 5.5), (-36.0, 152.0, T1 + 9.0), 18),
        "CAM_DSVeg_TreeSE": ((80.0, 196.0, T1 + 5.5), (110.0, 168.0, T1 + 10.0), 18),
        "CAM_DSVeg_TreeNE": ((96.0, 330.0, T1 + 5.5), (116.0, 352.0, T1 + 7.0), 20),
        "CAM_DSVeg_Roots": ((107.0, 344.0, T1 + 3.2), (116.0, 352.0, T1 + 0.8), 22),
        "CAM_DSVeg_Cedar": ((-102.0, 520.0, T4 + 5.5), (-84.0, 552.0, T4 + 11.0), 18),
        "CAM_DSVeg_BambooPath": ((33.0, 46.0, L.bamboo_z(33.0, 46.0) + 5.5), (50.0, 90.0, L.bamboo_z(50.0, 90.0) + 6.0), 20),
        "CAM_DSVeg_BambooClump": ((44.0, 66.0, L.bamboo_z(44.0, 66.0) + 5.0), (30.0, 70.0, L.bamboo_z(30.0, 70.0) + 6.0), 22),
        "CAM_DSVeg_Pergola": ((64.0, 128.0, L.bamboo_z(64.0, 128.0) + 5.5), (57.0, 106.0, L.bamboo_z(57.0, 106.0) + 7.0), 18),
        "CAM_DSVeg_WisV6": ((-90.0, 340.0, T2 + 5.5), (vx, vy, T2 + 6.5), 20),
        "CAM_DSVeg_WisSumS": ((160.0, 286.0, T3 + 5.5), (176.0, 270.0, T3 + 6.5), 22),
        "CAM_DSVeg_WisSumN": ((160.0, 316.0, T3 + 5.5), (176.0, 330.0, T3 + 6.5), 22),
        "CAM_DSVeg_ClearingEdge": ((22.0, 238.0, T1 + 5.5), (-40.0, 252.0, T1 + 2.0), 22),
        "CAM_DSVeg_WallFoot": ((-34.0, 254.0, T1 + 4.0), (-52.0, 240.0, T1 + 1.5), 22),
        "CAM_DSVeg_PineMirante": ((-8.0, 336.0, T1 + 5.5), (-38.0, 366.0, T1 + 8.0), 20),
        "CAM_DSVeg_PineEntry": ((10.0, 18.0, T0 + 5.5), (-28.0, 32.0, T0 + 12.0), 20),
        "CAM_DSVeg_Village": ((-60.0, 236.0, T2 + 26.0), (-128.0, 250.0, T2 + 4.0), 22),
        "CAM_DSVeg_ForgeBack": ((10.0, 430.0, T4 + 22.0), (10.0, 540.0, 108.0), 22),
        # ONDA 4b (densidade): closes da franja das falesias e das molduras novas
        "CAM_DSVeg_CliffW": ((-235.0, 190.0, 78.0), (-160.0, 230.0, 58.0), 24),
        "CAM_DSVeg_CliffE": ((205.0, 110.0, 74.0), (140.0, 170.0, 56.0), 24),
        "CAM_DSVeg_CliffNE": ((215.0, 430.0, 92.0), (145.0, 400.0, 72.0), 24),
        "CAM_DSVeg_CliffForgeW": ((-235.0, 470.0, 104.0), (-150.0, 450.0, 80.0), 24),
        "CAM_DSVeg_ClearingFrameW": ((40.0, 250.0, T1 + 18.0), (-40.0, 290.0, T1 + 6.0), 22),
        "CAM_DSVeg_ClearingFrameS": ((45.0, 300.0, T1 + 18.0), (30.0, 150.0, T1 + 4.0), 22),
        "CAM_DSVeg_Berm": ((40.0, 300.0, T1 + 12.0), (40.0, 400.0, T3 + 8.0), 22),
        "CAM_DSVeg_ExitPath": ((-104.0, 446.0, T4 + 5.5), (-112.0, 520.0, T4 + 4.0), 22),
    }


CAMS = _cams()
