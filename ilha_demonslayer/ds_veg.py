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


def roots(mb, P, base, r0, rng, n=5, reach=(2.4, 4.0), avoid=None, a0=None):
    """raizes que AGARRAM o chao: nascem no tronco a ~1,5 de altura, descem em arco e mergulham 0,45 no chao real
    (sondado). avoid(x, y) -> True = proibido (canal, rua): a raiz gira; se nao achar lugar, nao nasce"""
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
            if not avoid or not (avoid(e.x, e.y) or avoid(m_.x, m_.y)):
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
def karikomi(mb, P, x, y, rng, r=1.7, lumps=2, m=SHRUB):
    """azaleia podada: 1-3 almofadas LISAS (poda) encostadas, mais largas que altas, enterradas 0,2"""
    z = P.gz(x, y, T1)
    a0 = rng.uniform(0, TAU)
    for k in range(lumps):
        q = Vector((x, y, z - 0.2)) + (vdir(a0 + 2.4 * k) * r * 0.75 if k else Vector())
        rr = r * (1.0 if k == 0 else rng.uniform(0.62, 0.8))
        cushion(mb, q, rr * 1.08, rr * 0.95, rr * 1.0, m, rng, n=9, rot=a0 + k, jit=0.05,
                prof=((0.0, 0.86), (0.32, 1.0), (0.7, 0.82)))


def bush(mb, P, x, y, rng, r=1.6, m=BROAD):
    """mato baixo SELVAGEM (pe de muro, borda da clareira): 2-3 almofadas asperas e desencontradas, mais alto num
    lado, enterradas 0,25 (contraponto ao karikomi podado da vila)"""
    z = P.gz(x, y, T1)
    a0 = rng.uniform(0, TAU)
    for k in range(rng.randint(2, 3)):
        q = Vector((x, y, z - 0.25)) + vdir(a0 + 2.3 * k) * r * (0.0 if k == 0 else rng.uniform(0.55, 0.85))
        rr = r * (1.0 if k == 0 else rng.uniform(0.55, 0.75))
        cushion(mb, q, rr, rr * 0.85, rr * rng.uniform(0.95, 1.25), m, rng, n=6, rot=a0 + k, jit=0.16)
    return z


def tuft(mb, x, y, z, rng, s=1.0, m=SHRUB):
    """tufo de capim: 6-9 laminas (tetraedros finos e inclinados para fora), a base enterrada 0,22 no chao"""
    bm = mb.bm
    vs = []
    nb = rng.randint(6, 9)
    for k in range(nb):
        a = rng.uniform(0, TAU)
        rr = rng.uniform(0.0, 0.45) * s
        bx, by = x + math.cos(a) * rr, y + math.sin(a) * rr
        hg = s * rng.uniform(0.75, 1.55)
        la = a + rng.uniform(-0.6, 0.6)
        lx, ly = math.cos(la) * hg * rng.uniform(0.15, 0.5), math.sin(la) * hg * rng.uniform(0.15, 0.5)
        w = 0.14 * s
        r0 = rng.uniform(0, TAU)
        b = [bm.verts.new((bx + math.cos(r0 + TAU * i / 3) * w, by + math.sin(r0 + TAU * i / 3) * w, z - 0.22))
             for i in range(3)]
        tp = bm.verts.new((bx + lx, by + ly, z + hg))
        for f in ((b[0], b[1], tp), (b[1], b[2], tp), (b[2], b[0], tp), (b[0], b[2], b[1])):
            bm.faces.new(f)
        vs += b + [tp]
    mb._post(vs, m, None, 0, 1)
    return nb * 4


# ================================================================== BAMBU em touceira
def culm(mb, p0, h, r, splay, bend, rng, collars=3):
    """colmo: segmentos que alongam para cima (no proximo do chao = curto), leve dobra em cada no, afina para a
    ponta; anel do no (Bamboo_DS_Dry, 1,3 x o raio: le de longe como as listras do bambu) nos de baixo. Devolve os
    nos (ponto, tangente, raio) para as folhas"""
    segs = [1.2, 1.7, 2.1, 2.4, 2.6, 2.8, 2.9, 3.0, 3.0, 3.0]
    zs = [0.0]
    for s in segs:
        if zs[-1] + s > h:
            break
        zs.append(zs[-1] + s)
    if h - zs[-1] > 1.2:
        zs.append(h)
    else:
        zs[-1] = h
    pts, rads = [p0 - ZZ * 0.4], [r * 1.05]
    kink = vdir(rng.uniform(0, TAU)) * 0.05
    for i, zz in enumerate(zs[1:], 1):
        t = zz / h
        pts.append(p0 + splay * zz + bend * (t ** 2.2) * h + kink * (i % 2) * zz * 0.2 + ZZ * zz)
        rads.append(r * (1.0 - 0.45 * t))
    PK.taper_tube(mb, pts, rads, BAMB, n=5)
    nodes = []
    for i in range(1, len(pts) - 1):
        d = (pts[i + 1] - pts[i - 1]).normalized()
        nodes.append((pts[i], d, rads[i]))
        if i <= collars:
            collar(mb, pts[i], d, rads[i])
    nodes.append((pts[-1], (pts[-1] - pts[-2]).normalized(), rads[-1]))
    return nodes


def collar(mb, p, d, r):
    """anel do no: tubo curto ABERTO (sem tampa: 10 tris), le como a listra do bambu.
    ONDA 4 (z-fight): o pentagono do anel era PARALELO ao do colmo a 0,035-0,05 (16 touceiras, ~200 studs2 de pisca);
    agora gira meio passo (36 graus): as faces do anel cruzam as do colmo em angulo e nenhuma fica paralela. Raio no
    vertice 1,30 / 1,24 (no meio da face 1,05 / 1,00 x o raio: as quinas do colmo continuam cobertas)"""
    PK.loft(mb, [p - d * 0.1, p + d * 0.14], [PK.circ(r * 1.30, 5, math.pi / 5), PK.circ(r * 1.24, 5, math.pi / 5)],
            BAMB_DRY, caps=False)


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
        q.z = P.gz(q.x, q.y, z)
        PK.cone(mb, q - ZZ * 0.2, q + ZZ * rng.uniform(0.9, 1.5), 0.38, 0.05, BAMB_DRY, n=5)
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
        q = Vector((x, y, 0.0)) - Vector((fc.x, fc.y, 0.0))
        lateral = abs(q.dot(u))
        return gz + (6.9 if lateral < 3.8 else 5.2)
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
    n = wisteria_on_frame(mb, P, rng, (wx - 2.75, wy - 2.35), P.gz(wx - 2.75, wy - 2.35, gz), fc, u, v, 4.4, 3.9,
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
        tris += tuft(cells.at(x, y), x, y, z, rng, s)
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
            if got >= nwant or len(made) >= 23:
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
        r_ = random.Random(zlib.crc32(("pine" + key).encode()))
        adj = make_adjust(reach)
        info = pine(cells.at(x, y), P, x, y, r_, h=h, lean_az=math.radians(az), lean=lean, reach=reach, adjust=adj)
        tops.append((info["top"], "DS_Veg pinheiro " + key))
        trunks.append((x, y, 2.5))
        STATS["pine_" + key] = (round(info["base"].z, 1), round(info["top"], 1), info["pads"])
    # ---------------- cedros
    for grp, lst in CEDARS:
        for i, (x, y, h, r) in enumerate(lst):
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
        if why:
            STATS.setdefault("karikomi_rejeitado", []).append((x, y, why))
            continue
        karikomi(cells.at(x, y), P, x, y, r_, r=r, lumps=1 + (i % 3 != 0) + (i % 4 == 0))
        trunks.append((x, y, r + 0.6))
        nk += 1
    STATS["karikomi"] = nk
    # ---------------- grama em manchas
    n, tris, nc = grass(P, cells, random.Random(5150), avoid_pts=trunks)
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
    }


CAMS = _cams()
