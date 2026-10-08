# vm_veg.py - VEGETACAO do lobby VILA MEDIEVAL (onda V3a). Meta = ref/ref_01_estilo_vila.jpg: VIDA VERDE entre e
# atras das casas (pinheiro cartoon alto + arvores de copa redonda em massas), hera subindo a pedra, grama alta e tufos
# na borda da rua, flores em manchas, sebes; arredores (sudoeste, leste da loja, norte) com bosques em vez de grama lisa.
# Substitui a vegetacao do blockout V0 (VM_Veg_Trees_*) e as arvores do patio do V2b (VM_Veg_Court): o V3 refaz tudo.
#
# Coordenadas ROBLOX (X leste, Z sul, Y cima); Blender = (X, -Z, Y). Determinismo: so hash (K.h01 / K.rng = crc32 +
# fmix32), ordem fixa, nada de random global nem hash() do Python.
#
# INTENCAO (densidade DIRIGIDA, nada de scatter uniforme)
#   - a densidade CRESCE das bordas das ruas para fora (smoothstep da distancia ao calcamento) e e maxima na borda do
#     plato (cinturao); um ruido de baixa frequencia separa BOSQUES de CLAREIRAS; rua, portas e escadas ficam livres;
#   - ARVORES HEROI com intencao (lista HERO): atras das fileiras de casas (a copa aparece por cima/entre os telhados,
#     como na ref), no vao entre E2 e E3 da rua curva (o enquadramento da ref_01), emoldurando a praca, o patio dos
#     portais (copas entre os portais, pinheiros nas pontas), a forja (so ATRAS e nos flancos, nunca no largo nem na
#     frente) e a rua de saida (pinheiros no portao);
#   - visadas protegidas (VIEWS): spawn -> chamine/forja, praca -> forja, rua -> portao, adro -> ranking, rua -> loja,
#     arco -> portais: nenhuma copa fecha o segmento;
#   - HERA em quinas e lados expostos do terreo de pedra (sondada: so cresce onde o raio acha PEDRA; madeira = porta /
#     janela -> o tufo nao nasce), na ala oeste da forja, nas torres do portao e nos fundos do salao da guilda;
#   - CHAO (after_props, depois do vm_props): tufos de grama alta na borda de grama das ruas (2 fileiras, a de fora
#     mais densa), pes de parede, pe das arvores e das muretas; flores em manchas (1 cor por celula); sebes podadas
#     nos flancos do terraco do spawn e nos quintais; prados de capim alto e flores nos arredores.
#
# FAMILIA (silhueta facetada sem bevel, 3 tons de verde, tom ESCURO por dentro/por baixo):
#   pinheiro cartoon (ref_01): tronco reto com raizes, 4-6 SAIAS conicas em camadas com pontas caidas (borda em
#        estrela), face de baixo escura (Leaf_VM_Pine), lados no verde medio, ultima saia no verde claro;
#   arvore de copa redonda: tronco curto e grosso com base alargada e 2-3 RAIZES que mergulham no chao real (sondado),
#        forquilha em 3 bracos, copa = almofadas desencontradas em 3 andares (fundo de cada almofada escuro, topo medio,
#        coroa clara) + massa interna escura; lod 1 (longe) com metade das almofadas;
#   moita / sebe: almofadas largas e baixas (fundo escuro); tufo: laminas finas inclinadas (verde claro / medio);
#   flor: cabecas de 4 tris sobre um tufo baixo; hera: placas achatadas coladas na pedra (escuro + medio).
#
# MATERIAIS: Bark_VM, Leaf_VM_Pine (escuro), Leaf_VM_Round (medio), Leaf_VM_Light (claro, NOVO: +1 material),
#   Flower_VM_* (1 cor por celula). Objetos: 1 por CELULA da planta (VM_Veg_<col><lin>, <= 150 studs de lado: o
#   export nao fatia) -> <= 5 MeshParts por celula. Colisao SO nos troncos (COL_VegTrunk_*).
# ORCAMENTO (lead, V3): vegetation <= 55k tris / 40 MeshParts (vm_layout.BUDGET_OWNER).
#
# INTERSECAO: Probe = BVH de TODAS as malhas construidas (export, menos chao natural, colinas, montanhas e o proprio
#   V3a) + volumes de QA (Ignis, chao diante do Ignis, Top100) + caixas de exclusao (largo da forja, escadaria do spawn,
#   anel dos portais). Tronco, copa (esferas), moita, tufo e hera sao testados; o relatorio isect() mede no fim as
#   sobreposicoes reais de triangulos contra o construido (piso descontado).
#
# uso: o build_vm.py chama vm_veg.build() depois do vm_town, vm_props.build() e vm_veg.after_props(); cameras no fim.
#      blender -b --factory-startup <blend> --python vm_veg.py -- report [json]
#      python -B vm_veg.py sheets <pasta_previa> <pasta_roblox> <pasta_saida>       (folhas, so PIL)
import sys, os, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
try:
    import bpy
except ImportError:            # folhas (python puro)
    bpy = None

TAU = math.tau
COLL = "09_VEGETATION"
BARK, DARK, MID, LIGHT = "Bark_VM", "Leaf_VM_Pine", "Leaf_VM_Round", "Leaf_VM_Light"
STATS = {}
TRUNKS = []          # (x, z, r) Roblox: pes de arvore (o vm_props desvia)
CLOSES = {}          # cameras de close (arvore, pinheiro, hera): nome -> (pos, alvo, lente) Roblox
CELL_FLOWER = {"WN": "yellow", "WS": "pink", "CN": "yellow", "CS": "red", "EN": "pink", "ES": "yellow"}
TRI_CAP = {"trees": 38500, "ivy": 3400, "ground": 10500}
GROUND_CAP = {"rua": 4200, "pe": 1500, "sebe": 1100}     # o resto do teto do chao vai para os prados

if bpy is not None:
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import vm_lib as VL
    import vm_layout as L
    import fm_lib
    from fm_lib import MB, S, MATS, col_box
    import fm_portal_kit as PK
    import vm_kit as K
    MATS.setdefault(LIGHT, (S(132, 186, 72), 0.85, 0.0, 0, None, 0.0))   # verde claro (coroa, capim alto)
    ZZ = Vector((0.0, 0.0, 1.0))
    PCX, PCZ = L.PLAZA_C
    CCX, CCZ = L.COURT_C


# ================================================================== utilidades
def h01(*k):
    import vm_kit as K_
    return K_.h01(*k)


def smooth(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def vnoise(x, z, sc=38.0, key="clump"):
    """ruido de valor deterministico (0..1), grade de 'sc' studs, interpolacao suave"""
    u, v = x / sc, z / sc
    i, j = math.floor(u), math.floor(v)
    fu, fv = u - i, v - j
    fu, fv = fu * fu * (3 - 2 * fu), fv * fv * (3 - 2 * fv)
    a = h01(key, i, j)
    b = h01(key, i + 1, j)
    c = h01(key, i, j + 1)
    d = h01(key, i + 1, j + 1)
    return (a * (1 - fu) + b * fu) * (1 - fv) + (c * (1 - fu) + d * fu) * fv


def seg_dist(px, pz, a, b):
    dx, dz = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dz * dz or 1e-9
    t = max(0.0, min(1.0, ((px - a[0]) * dx + (pz - a[1]) * dz) / l2))
    return math.hypot(px - a[0] - dx * t, pz - a[1] - dz * t)


def poly_dist(px, pz, pts, closed=False):
    P = list(pts) + ([pts[0]] if closed else [])
    return min(seg_dist(px, pz, a, b) for a, b in zip(P, P[1:]))


def seg3_dist(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / (ab.length_squared or 1e-9)))
    return (a + ab * t - p).length


def B(x, z, y=0.0):
    return Vector((x, -z, y))


def cell_of(x, z):
    c = "W" if x < -90.0 else ("C" if x < 45.0 else "E")
    return c + ("N" if z < 10.0 else "S")


# ================================================================== a cena construida (chao natural + obstaculos)
class Probe:
    """raios contra o que as outras ondas montaram: CHAO NATURAL (faces Grass_VM*) onde a planta nasce e o CONSTRUIDO
    (todas as malhas do export + volumes de QA + caixas de exclusao) que tronco, copa, prop e tufo nao atravessam"""
    SKIP = ("COL_", "PREVIEW_", "SCALE_", "VM_Veg_", "VM_Prop_", "CAM_", "VFX_")
    NOT_BUILT = ("VM_Ter_Ground", "VM_Ter_Hills", "VM_Bg_", "VM_Ter_Cliffs")
    KO = []          # caixas de exclusao (Roblox lo, hi) acrescentadas ao construido

    def __init__(self, extra_ko=()):
        V, P, self.own, self.mat = [], [], [], []
        bV, bP, self.bown, self.bmat = [], [], [], []
        groups = set(VL.EXPORT_GROUPS)
        for o in bpy.data.objects:
            if o.type != "MESH" or o.name.startswith(self.SKIP):
                continue
            qa = o.name.startswith("QA_")
            if not qa:
                if o.hide_render or not o.users_collection or o.users_collection[0].name not in groups:
                    continue
            mw = o.matrix_world
            me = o.data
            vs = [mw @ v.co for v in me.vertices]
            mats = [m.name if m else "" for m in me.materials]
            if not qa:
                b = len(V)
                V += vs
                for p in me.polygons:
                    P.append([b + i for i in p.vertices])
                    self.own.append(o.name)
                    self.mat.append(mats[p.material_index] if p.material_index < len(mats) else "")
            if not o.name.startswith(self.NOT_BUILT):
                b2 = len(bV)
                bV += vs
                for p in me.polygons:
                    bP.append([b2 + i for i in p.vertices])
                    self.bown.append(o.name)
                    self.bmat.append(mats[p.material_index] if p.material_index < len(mats) else "")
        for lo, hi in list(self.KO) + list(extra_ko):
            a, b = B(lo[0], lo[2], lo[1]), B(hi[0], hi[2], hi[1])
            x0, x1 = sorted((a.x, b.x))
            y0, y1 = sorted((a.y, b.y))
            z0, z1 = sorted((a.z, b.z))
            k = len(bV)
            bV += [Vector((x, y, z)) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
            for f in ((0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)):
                bP.append([k + i for i in f])
                self.bown.append("KO")
                self.bmat.append("KO")
        self.bvh = BVHTree.FromPolygons(V, P)
        self.built = BVHTree.FromPolygons(bV, bP)
        self.bV, self.bP = bV, bP
        self.routes = [pts for pts, y in L.routes().values()]
        # volumes de QA (Roblox lo, hi): nada do V3a pode entrar (Ignis, chao diante dele, Top100) + exclusoes
        self.qa = []
        for o in bpy.data.objects:
            if o.name.startswith("QA_") and o.get("qa_lo") is not None:
                self.qa.append((tuple(o["qa_lo"]), tuple(o["qa_hi"])))

    def top(self, x, z, y0=400.0):
        """(Y, dono, material, normal_y) do primeiro que um raio de cima encontra (Roblox x, z)"""
        h = self.bvh.ray_cast(Vector((x, -z, y0)), Vector((0.0, 0.0, -1.0)), 900.0)
        if h[0] is None:
            return None
        return h[0].z, self.own[h[2]], self.mat[h[2]], h[1].z

    def natural(self, x, z):
        """cota do chao de GRAMA em (x, z) ou None (rua, praca, telhado, agua, fora do plato)"""
        t = self.top(x, z)
        if t is None or not t[2].startswith("Grass_VM") or t[3] < 0.8 or not (5.0 < t[0] < 7.6):
            return None
        return t[0]

    def floor_y(self, x, z, hint=6.0):
        """piso andavel em (x, z): o mais alto abaixo de hint + 3 (props em calcamento)"""
        h = self.bvh.ray_cast(Vector((x, -z, hint + 3.0)), Vector((0.0, 0.0, -1.0)), 12.0)
        return (h[0].z, self.own[h[2]], self.mat[h[2]]) if h[0] is not None else None

    def clear(self, p, r):
        """nada construido a menos de r do ponto Blender p"""
        return self.built.find_nearest(Vector(p), r)[0] is None

    def clear_r(self, x, z, y, r):
        return self.clear(B(x, z, y), r)

    def route_dist(self, x, z):
        return min(poly_dist(x, z, pts) for pts in self.routes)

    def wall_hit(self, p, d, dist=4.0):
        """raio horizontal contra o construido: (ponto, normal, material) ou None"""
        h = self.built.ray_cast(Vector(p), Vector(d), dist)
        if h[0] is None:
            return None
        return h[0], h[1], self.bmat[h[2]], self.bown[h[2]]


# caixas de exclusao (Roblox lo/hi): largo e frente da forja, escadaria do spawn, boca da ponte, disco/anel dos
# portais ate a frente das espirais, rampa da ponte da ilha
Probe.KO = [((-27.0, 6.5, -51.0), (25.0, 40.0, -35.0)),                     # largo da forja (dono V2a)
            ((-10.5, 6.5, -66.0), (6.5, 32.0, -38.0)),                      # Ignis + chao livre diante dele
            ((-14.8, 5.0, 78.5), (14.8, 14.0, 90.5)),                       # escadaria do spawn
            ((-11.5, 5.0, -24.0), (11.5, 14.0, 4.0)),                       # ponte do eixo
            ((40.0, 5.0, 141.0), (60.0, 30.0, 156.0)),                      # vao do portao
            # V3b (VFX no export): levada + roda d'agua (36, 9,4, -66) + pilao; pluma da chamine; quedas do canal
            ((30.0, 0.0, -88.0), (42.5, 20.0, -16.0)),
            ((-13.0, 30.0, -99.0), (13.0, 300.0, -73.0)),
            ((-140.0, -40.0, -26.0), (-117.0, 20.0, 2.0)), ((149.0, -40.0, -26.0), (178.0, 20.0, 2.0))]


# ================================================================== geometria organica (bmesh direto no MB)
def _faces(mb, vs, faces, m):
    bm = mb.bm
    for f in faces:
        try:
            bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    mb._post(vs, m, None, 0, 1)


def cushion(mb, c, rx, ry, h, m_top, m_bot, rng, n=7, rot=0.0, jit=0.12,
            prof=((0.0, 0.70), (0.38, 1.0), (0.78, 0.64))):
    """ALMOFADA de folhagem facetada (fundo quase plano, cintura a 1/3, ombro estreito, topo deslocado): fundo + 1a
    faixa no material ESCURO (m_bot = o tom de dentro/de baixo), 2a faixa + topo em m_top. c = centro do FUNDO (Blender).
    42 tris (n=7)."""
    bm = mb.bm
    rings = []
    for k, (fz, fr) in enumerate(prof):
        ring = []
        for j in range(n):
            a = rot + TAU * (j + rng.uniform(-0.2, 0.2)) / n
            s = fr * rng.uniform(1.0 - jit, 1.0 + jit)
            ring.append(Vector((c.x + math.cos(a) * rx * s, c.y + math.sin(a) * ry * s,
                                c.z + h * (fz + (rng.uniform(-0.05, 0.05) if k else 0.0)))))
        rings.append(ring)
    bot = Vector((c.x, c.y, c.z - h * 0.04))
    top = Vector((c.x + rng.uniform(-0.18, 0.18) * rx, c.y + rng.uniform(-0.18, 0.18) * ry, c.z + h))
    # parte de baixo (escura)
    vs = [bm.verts.new(p) for p in rings[0]] + [bm.verts.new(p) for p in rings[1]] + [bm.verts.new(bot)]
    fs = []
    for j in range(n):
        j2 = (j + 1) % n
        fs.append((j2, j, 2 * n))
        fs.append((j, j2, n + j2, n + j))
    _faces(mb, vs, fs, m_bot)
    vs = [bm.verts.new(p) for p in rings[1]] + [bm.verts.new(p) for p in rings[2]] + [bm.verts.new(top)]
    fs = []
    for j in range(n):
        j2 = (j + 1) % n
        fs.append((j, j2, n + j2, n + j))
        fs.append((n + j, n + j2, 2 * n))
    _faces(mb, vs, fs, m_top)
    return 6 * n


def tube(mb, pts, radii, m=BARK, n=6):
    """galho / tronco / raiz sem tampa (as pontas ficam enterradas ou dentro da copa)"""
    PK.taper_tube(mb, [Vector(p) for p in pts], radii, m, n=n, caps=False)
    return 2 * n * (len(pts) - 1)


def roots(mb, P, x, z, y, r0, rng, n=3, reach=(1.8, 3.2)):
    """raizes que AGARRAM o chao: nascem no tronco a ~1,5 de altura, descem em arco e mergulham 0,45 no chao REAL
    (sondado); so onde o chao do meio e da ponta e grama na cota do pe e nada construido no caminho"""
    a0 = rng.uniform(0, TAU)
    t = 0
    for k in range(n):
        a = a0 + TAU * k / n + rng.uniform(-0.35, 0.35)
        Ln = rng.uniform(*reach)
        ok = None
        for da in (0.0, 0.5, -0.5):
            aa = a + da
            ex, ez = x + math.cos(aa) * (r0 + Ln), z + math.sin(aa) * (r0 + Ln)
            mx, mz = x + math.cos(aa) * (r0 + Ln * 0.55), z + math.sin(aa) * (r0 + Ln * 0.55)
            ye, ym = P.natural(ex, ez), P.natural(mx, mz)
            if ye is None or ym is None or abs(ye - y) > 0.9 or abs(ym - y) > 0.9:
                continue
            if not P.clear_r(mx, mz, ym + 0.4, 0.6) or not P.clear_r(ex, ez, ye + 0.2, 0.5):
                continue
            ok = (aa, ex, ez, ye, mx, mz, ym)
            break
        if ok is None:
            continue
        aa, ex, ez, ye, mx, mz, ym = ok
        sx, sz = -math.sin(aa) * rng.uniform(-0.4, 0.4), math.cos(aa) * rng.uniform(-0.4, 0.4)
        p0 = B(x + math.cos(aa) * r0 * 0.3, z + math.sin(aa) * r0 * 0.3, y + rng.uniform(1.3, 1.9))
        p1 = B(x + math.cos(aa) * (r0 + 0.3), z + math.sin(aa) * (r0 + 0.3), y + 0.8)
        p2 = B(mx + sx, mz + sz, ym + 0.18)
        p3 = B(ex + sx * 2, ez + sz * 2, ye - 0.45)
        t += tube(mb, [p0, p1, p2, p3], [r0 * 0.5, r0 * 0.4, r0 * 0.24, 0.1], n=5)
    return t


def pine_skirt(mb, c, R, th, rng, m_side, n=7, rot=0.0, droop=0.16):
    """SAIA de pinheiro cartoon: cone com borda em ESTRELA (n pontas caidas, n entalhes recolhidos), face de baixo
    concava e ESCURA. c = centro da base da saia (Blender). 4n tris."""
    bm = mb.bm
    apex = c + ZZ * th
    ring = []
    for j in range(2 * n):
        a = rot + TAU * j / (2 * n) + rng.uniform(-0.06, 0.06)
        if j % 2 == 0:      # ponta
            r, dz = R * rng.uniform(0.92, 1.08), -th * droop * rng.uniform(0.7, 1.2)
        else:               # entalhe
            r, dz = R * rng.uniform(0.62, 0.72), th * 0.16
        ring.append(c + Vector((math.cos(a) * r, math.sin(a) * r, dz)))
    k = 2 * n
    vs = [bm.verts.new(p) for p in ring] + [bm.verts.new(apex)]
    _faces(mb, vs, [(j, (j + 1) % k, k) for j in range(k)], m_side)
    cen = c + ZZ * (th * 0.22)
    vs = [bm.verts.new(p) for p in ring] + [bm.verts.new(cen)]
    _faces(mb, vs, [((j + 1) % k, j, k) for j in range(k)], DARK)
    return 4 * n


def pine(mb, P, x, z, y, h, rng, lod=0, slim=1.0):
    """PINHEIRO CARTOON da ref_01: tronco reto (base alargada + raizes), 4-6 saias conicas sobrepostas que estreitam
    para cima, pontas caidas, ultima saia clara e ponta fina. h = altura total. slim < 1 = pinheiro ESGUIO (as saias
    comecam mais alto e abrem menos: cabe entre/atras das casas, a copa sobe por cima dos telhados como na ref)"""
    t = 0
    r0 = 0.32 + h * 0.022
    t += tube(mb, [B(x, z, y - 0.6), B(x, z, y + 0.5), B(x, z, y + h * 0.45)], [r0 * 1.35, r0, r0 * 0.6], n=6)
    if lod == 0:
        t += roots(mb, P, x, z, y, r0, rng, n=3, reach=(1.2, 2.2))
    nt = 5 if h > 22 else 4
    if lod:
        nt = 4
    rot = rng.uniform(0, TAU)
    lean = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), 0.0)) * 0.25
    for k in range(nt):
        f = k / (nt - 1)
        zb = y + h * (0.20 + (1.0 - slim) * 0.45 + (0.58 - (1.0 - slim) * 0.4) * f)
        R = h * (0.25 - 0.17 * f) * slim * rng.uniform(0.92, 1.08)
        th = h * (0.30 - 0.10 * f)
        m = LIGHT if k == nt - 1 else MID
        c = B(x, z, zb) + lean * f * 2.0
        t += pine_skirt(mb, c, R, th, rng, m, n=7 if lod == 0 else 6, rot=rot + 0.45 * k)
    return t


PUFF = ((0.0, 0.6), (0.42, 1.0), (0.84, 0.56))      # almofada de copa CHEIA (le redonda, nao prato)


def round_tree(mb, P, x, z, y, h, R, rng, lod=0):
    """ARVORE DE COPA REDONDA: tronco curto e grosso (base alargada, raizes que agarram o chao), forquilha em 3 bracos
    em vaso, copa = almofadas desencontradas em 3 andares (fundo escuro, topo medio, coroa clara) + massa interna
    escura. lod 1 = copa com metade das almofadas, sem raizes nem bracos."""
    t = 0
    r0 = 0.42 + R * 0.085
    hf = h * rng.uniform(0.30, 0.36)
    ph = rng.uniform(0, TAU)
    base = B(x, z, y)
    tp = [base + Vector((0, 0, -0.6)), base + Vector((math.cos(ph) * 0.15, math.sin(ph) * 0.15, hf * 0.5)),
          base + Vector((math.cos(ph) * 0.25, math.sin(ph) * 0.25, hf))]
    t += tube(mb, tp, [r0 * 1.35, r0 * 1.0, r0 * 0.8], n=6 if lod == 0 else 5)
    if lod == 0:
        t += roots(mb, P, x, z, y, r0, rng, n=3)
    F = tp[-1]
    C0 = base
    a0 = rng.uniform(0, TAU)
    pads = []
    limbs = 3
    for k in range(limbs):
        a = a0 + TAU * k / limbs + rng.uniform(-0.25, 0.25)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        pc = C0 + d * R * rng.uniform(0.5, 0.6) + ZZ * h * rng.uniform(0.52, 0.58)
        if lod == 0:
            mid = F + d * R * 0.22 + ZZ * h * 0.1
            t += tube(mb, [F - ZZ * 0.6, mid, pc - ZZ * 0.3], [r0 * 0.62, r0 * 0.45, r0 * 0.28], n=5)
        pads.append((pc, R * rng.uniform(0.46, 0.52), MID))
    for k in range(2):
        a = a0 + math.pi / limbs + math.pi * k + rng.uniform(-0.25, 0.25)
        pc = C0 + Vector((math.cos(a), math.sin(a), 0)) * R * rng.uniform(0.24, 0.32) + ZZ * h * rng.uniform(0.70, 0.76)
        pads.append((pc, R * rng.uniform(0.44, 0.5), MID if k else LIGHT))
    pads.append((C0 + Vector((math.cos(ph + 1), math.sin(ph + 1), 0)) * R * 0.08 + ZZ * h * 0.86, R * 0.4, LIGHT))
    if lod:
        pc, s_, m_ = pads[5]
        pads = [pads[0], pads[1], pads[2], pads[3], (pc - ZZ * h * 0.08, s_ * 1.1, m_)]
    for pc, s, m in pads:
        base_c = pc - ZZ * (s * 0.32)
        t += cushion(mb, base_c, s * 1.05, s * rng.uniform(0.84, 0.96), s * 1.15, m, DARK, rng, n=7 if lod == 0 else 6,
                     rot=rng.uniform(0, TAU), prof=PUFF)
        if lod == 0:
            a = rng.uniform(0, TAU)
            q = base_c + Vector((math.cos(a), math.sin(a), 0)) * s * rng.uniform(0.45, 0.65) + ZZ * s * rng.uniform(0.25, 0.4)
            ss = s * rng.uniform(0.52, 0.66)
            t += cushion(mb, q, ss * 1.05, ss * 0.9, ss * 1.2, LIGHT if m == LIGHT or h01("sub", x, z, a) < 0.5 else MID,
                         DARK, rng, n=6, rot=a, prof=PUFF)
    # massa interna escura (profundidade: o vao entre as almofadas nao mostra o ceu)
    inner = C0 + ZZ * h * 0.56
    t += cushion(mb, inner - ZZ * R * 0.15, R * 0.5, R * 0.46, R * 0.42, DARK, DARK, rng, n=6)
    return t


def bush(mb, P, x, z, y, r, rng, lumps=None, m=MID):
    """moita: 2-3 almofadas largas e baixas desencontradas, enterradas 0,25 (fundo escuro)"""
    t = 0
    a0 = rng.uniform(0, TAU)
    for k in range(lumps or rng.randint(2, 3)):
        d = 0.0 if k == 0 else r * rng.uniform(0.55, 0.85)
        qx, qz = x + math.cos(a0 + 2.3 * k) * d, z + math.sin(a0 + 2.3 * k) * d
        rr = r * (1.0 if k == 0 else rng.uniform(0.55, 0.75))
        yy = P.natural(qx, qz) or y
        t += cushion(mb, B(qx, qz, min(yy, y) - 0.25), rr, rr * 0.88, rr * rng.uniform(0.9, 1.15),
                     m if k else (LIGHT if h01("bushc", x, z) < 0.3 else m), DARK, rng, n=6, rot=a0 + k)
    return t


def tuft(mb, x, z, y, rng, s=1.0, m=LIGHT):
    """TUFO de capim alto: 5-8 laminas (tetraedros finos inclinados para fora), base enterrada 0,2; 3 tris por lamina
    (a face de baixo fica no chao)"""
    bm = mb.bm
    vs = []
    fs = []
    nb = rng.randint(5, 7)
    for k in range(nb):
        a = rng.uniform(0, TAU)
        rr = rng.uniform(0.0, 0.4) * s
        bx, bz = x + math.cos(a) * rr, z + math.sin(a) * rr
        hg = s * rng.uniform(0.75, 1.5)
        la = a + rng.uniform(-0.6, 0.6)
        lx, lz = math.cos(la) * hg * rng.uniform(0.15, 0.5), math.sin(la) * hg * rng.uniform(0.15, 0.5)
        w = 0.15 * s
        r0 = rng.uniform(0, TAU)
        i0 = len(vs)
        for i in range(3):
            vs.append(B(bx + math.cos(r0 + TAU * i / 3) * w, bz + math.sin(r0 + TAU * i / 3) * w, y - 0.2))
        vs.append(B(bx + lx, bz + lz, y + hg))
        fs += [(i0, i0 + 1, i0 + 3), (i0 + 1, i0 + 2, i0 + 3), (i0 + 2, i0, i0 + 3)]
    bv = [bm.verts.new(p) for p in vs]
    _faces(mb, bv, fs, m)
    return 3 * nb


def flower_patch(mb, x, z, y, rng, fl, n=None, r=1.1):
    """MANCHA DE FLORES: cabecas (bipiramide achatada de 4 tris + 4 de baixo) sobre caules curtos no meio de um tufo
    baixo de folhas"""
    t = tuft(mb, x, z, y, rng, s=0.55, m=MID)
    bm = mb.bm
    n = n or rng.randint(5, 8)
    vs, fs = [], []
    for k in range(n):
        a = rng.uniform(0, TAU)
        d = r * math.sqrt(rng.random())
        cx, cz = x + math.cos(a) * d, z + math.sin(a) * d
        cy = y + rng.uniform(0.45, 0.95)
        s = rng.uniform(0.26, 0.38)
        r0 = rng.uniform(0, TAU)
        i0 = len(vs)
        for i in range(4):
            vs.append(B(cx + math.cos(r0 + TAU * i / 4) * s, cz + math.sin(r0 + TAU * i / 4) * s, cy))
        vs.append(B(cx, cz, cy + s * 0.55))
        vs.append(B(cx, cz, cy - s * 0.45))
        for i in range(4):
            fs.append((i0 + i, i0 + (i + 1) % 4, i0 + 4))
            fs.append((i0 + (i + 1) % 4, i0 + i, i0 + 5))
    bv = [bm.verts.new(p) for p in vs]
    _faces(mb, bv, fs, fl)
    return t + 8 * n


def hedge(mb, P, a, b, rng, w=1.7, hgt=2.2):
    """SEBE podada de a ate b (Roblox x, z): almofadas lisas encostadas ao longo do eixo (topo medio, fundo escuro);
    so onde o chao e grama e nada construido"""
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(2, int(L_ / (w * 0.85)))
    t = 0
    for i in range(n + 1):
        f = i / n
        x, z = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        y = P.natural(x, z)
        if y is None or not P.clear_r(x, z, y + 1.0, w * 0.6):
            continue
        t += cushion(mb, B(x, z, y - 0.2), w * 0.75, w * 0.62, hgt, MID, DARK, rng, n=6, rot=rng.uniform(0, TAU),
                     jit=0.05, prof=((0.0, 0.92), (0.35, 1.0), (0.8, 0.86)))
    return t


# ================================================================== keepouts, visadas, distancia ao calcamento
def _paths():
    """(polilinha Roblox, meia largura do calcamento + meio-fio)"""
    import vm_town as T
    return [(T.west_path().P, 7.1), (T.Path(L.EXIT_ROAD, smooth=2).P, 7.1), ([(30.0, 43.0), (61.9, 43.0)], 6.1),
            ([(0.0, -21.0), (0.0, -36.4)], 9.8), ([(0.0, 15.0), (0.0, 1.0)], 9.8), ([(0.0, 1.0), (0.0, -21.0)], 11.5),
            (L.ISLE_BRIDGE, 9.0)]


PATHS = []


def d_way(x, z):
    """distancia (>= 0) ate o calcamento mais proximo (ruas, praca, terraco do spawn, patio, largo da forja)"""
    if not PATHS:
        PATHS.extend(_paths())
    d = min(poly_dist(x, z, p) - hw for p, hw in PATHS)
    d = min(d, math.hypot(x - PCX, z - PCZ) - 36.8)
    d = min(d, math.hypot(x - CCX, z - CCZ) - 40.5)
    sx = max(abs(x) - 21.0, 0.0)
    sz = max(88.0 - z, z - 113.0, 0.0)
    d = min(d, math.hypot(sx, sz))                                          # terraco do spawn
    fx = max(-27.0 - x, x - 25.0, 0.0)
    fz = max(-51.0 - z, z + 35.0, 0.0)
    d = min(d, math.hypot(fx, fz))                                          # largo da forja
    return max(0.0, d)


def plateau_edge(x, z):
    return poly_dist(x, z, L.PLATEAU, closed=True)


HOUSES = []


def house_front(x, z, reach=7.0, side=1.0):
    """dentro da faixa diante da frente de uma casa (porta / vitrine): reach studs a partir da fachada"""
    if not HOUSES:
        import vm_town as T
        import vm_trecho as TR
        for h in T.layout():
            HOUSES.append((h["x"], h["z"], h["fx"], h["fz"], h["W"], h["D"]))
        for h in TR.HOUSES:
            kw = h["kw"]
            HOUSES.append((h["x"], h["z"], h["fx"], h["fz"], kw.get("W", 12.0), kw.get("D", 10.0)))
    for hx, hz, fx, fz, W, D in HOUSES:
        dx, dz = x - hx, z - hz
        u = dx * (-fz) + dz * fx
        v = dx * fx + dz * fz
        if abs(u) < W / 2 + side and D / 2 - 0.5 < v < D / 2 + reach:
            return True
    return False


DOORS = []


def doors():
    """portas = folhas de tabua grandes (Wood_VM_Plank das casas de fundo e Wood_VM_Timber das tabuas do kit: faces
    verticais grandes, soma > 6 studs2 por celula de 3, abaixo de 13,5 = terreo) das casas, loja, salao, forja,
    quiosque e portao; + portas de contrato (loja, forja)"""
    if DOORS:
        return DOORS
    acc = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(("VM_House_", "VM_Shop_", "VM_Rank_Hall", "VM_Frg_Hall",
                                                       "VM_Mail_", "VM_Exit_Gate", "VM_Court_Arch")):
            continue
        me = o.data
        mw = o.matrix_world
        mats = [m.name if m else "" for m in me.materials]
        for p in me.polygons:
            mn = mats[p.material_index]
            if mn not in ("Wood_VM_Plank", "Wood_VM_Timber") or abs(p.normal.z) > 0.2 or                     p.area < (2.0 if mn == "Wood_VM_Plank" else 3.5):
                continue
            c = mw @ p.center
            if c.z > 13.5:
                continue
            k = (round(c.x / 3.0), round(c.y / 3.0))
            a = acc.setdefault(k, [0.0, Vector(), Vector()])
            nw = (mw.to_3x3() @ p.normal)
            a[0] += p.area
            a[1] += c * p.area
            a[2] += nw * p.area
    for k, (ar, cs, ns) in sorted(acc.items()):
        if ar >= 6.0:
            c = cs / ar
            n = Vector((ns.x, ns.y, 0.0))
            n = n.normalized() if n.length > 1e-6 else Vector((0.0, 0.0, 0.0))
            DOORS.append((c.x, -c.y, n.x, -n.y))
    DOORS.append((L.SHOP_DOOR[0], L.SHOP_DOOR[1], -1.0, 0.0))
    DOORS.append((-1.0, -50.0, 0.0, 1.0))
    return DOORS


def near_door(x, z, r=4.5):
    return any(math.hypot(x - d[0], z - d[1]) < r for d in doors())


def VIEWS():
    """visadas protegidas (Roblox): olho -> alvo; nenhuma copa a menos de 'folga' do segmento"""
    E = L.EYE
    Y = L.Y_PAVE
    v = [((0.0, L.Y_SPAWN + E + 1.5, 104.0), (0.0, 94.0, -86.0)),         # spawn -> chamine
         ((0.0, L.Y_SPAWN + E + 1.5, 104.0), (-1.0, 20.0, -55.0)),         # spawn -> boca da forja
         ((3.0, Y + E, 58.0), (-1.0, 26.0, -62.0)),                          # praca -> forja
         ((28.0, Y + E, 76.0), (50.0, 14.0, 146.0)),                         # rua de saida -> portao
         ((53.0, Y + 7.0, 140.0), (30.0, Y + 14.0, 64.0)),                   # ref_01 (miolo do quadro)
         ((-80.0, Y + E, 66.0), (-170.0, 18.0, 74.0)),                       # arco -> portais
         ((-58.0, Y + E, 54.0), (-86.0, 18.0, 16.0)),                        # adro -> ranking
         ((35.0, Y + E, 44.0), (76.0, 15.0, 42.5)),                          # rua -> loja
         ((51.0, Y + E, 141.0), (10.0, 7.0, 214.0))]                         # portao -> ponte
    return [(B(a[0], a[2], a[1]), B(b[0], b[2], b[1])) for a, b in v]


def blocks_view(views, spheres):
    for c, r in spheres:
        for a, b in views:
            if seg3_dist(c, a, b) < r + 0.6:
                return True
    return False


def tree_spheres(kind, x, z, y, h, R, slim=1.0):
    """esferas que envolvem a copa (teste contra o construido e as visadas)"""
    if kind == "pine":
        z0 = 0.20 + (1.0 - slim) * 0.45
        out = []
        for f in (0.0, 0.33, 0.66, 1.0):
            zb = z0 + (0.58 - (1.0 - slim) * 0.4) * f
            rr = h * (0.25 - 0.17 * f) * slim * 1.15
            out.append((B(x, z, y + h * (zb + 0.06)), rr))
        out.append((B(x, z, y + h * 0.9), h * 0.07))
        return out
    out = [(B(x, z, y + h * 0.62), R * 0.9), (B(x, z, y + h * 0.86), R * 0.6)]
    for k in range(5):
        a = TAU * k / 5
        out.append((B(x + math.cos(a) * R * 0.62, z + math.sin(a) * R * 0.62, y + h * 0.56), R * 0.58))
    return out


def tree_box(kind, x, z, y, h, R, slim=1.0):
    """caixa (Roblox lo, hi) que contem a arvore inteira (teste duro contra os volumes de QA)"""
    r = R * 1.3 if kind == "round" else h * 0.27 * slim
    return (x - r, y - 1.0, z - r), (x + r, y + h * 1.06, z + r)


def box_hit(a, b, pad=0.3):
    return all(a[0][i] < b[1][i] + pad and b[0][i] < a[1][i] + pad for i in range(3))


# ================================================================== plano das arvores
class Cells:
    def __init__(self):
        self.mb = {}

    def get(self, x, z):
        k = cell_of(x, z)
        if k not in self.mb:
            self.mb[k] = MB("VM_Veg_" + k, COLL, K.rng("veg", k), detail="far", floor=-999)
        return self.mb[k]

    def finish(self):
        out = []
        for k in sorted(self.mb):
            ob = self.mb[k].finish()
            if ob is not None:
                ob["vm_v3a"] = 1
                out.append(ob)
        self.mb.clear()
        return out


CELLS = [None]
TREE_SPH = []        # esferas das copas plantadas (as cameras de QA nao nascem dentro de uma copa)
PLACED_HERO = []     # (nome, x, z, y, tipo, h, R) dos herois plantados (cameras de close)


def HERO():
    """arvores com INTENCAO (nome, Roblox x, z, tipo, altura, raio da copa | esguio). A sondagem desloca ate ~4,5
    studs. 'pine' com R < 1 = pinheiro ESGUIO (slim = R): cabe atras/entre as casas e sobe por cima dos telhados."""
    return [
        # rua curva de saida (ref_01): no vao entre E2 e E3, atras das 2 fileiras (copas por cima dos telhados)
        ("vaoE2E3", 69.0, 103.0, "pine", 36.0, 0.72), ("trasE1", 72.0, 84.0, "pine", 32.0, 0.8),
        ("trasE2", 77.0, 95.0, "round", 21.0, 8.0), ("trasE3", 80.0, 117.0, "pine", 31.0, 0.85),
        ("trasE4", 77.0, 134.0, "round", 19.0, 7.5), ("cantoE1", 62.0, 72.0, "round", 17.0, 6.5),
        ("trasW1", 25.0, 113.0, "pine", 34.0, 0.7), ("trasW2", 27.0, 129.0, "pine", 30.0, 0.75),
        ("refSE", 53.0, 66.0, "pine", 36.0, 0.75), ("fundoW", 26.0, 142.0, "round", 16.0, 6.0),
        # portao (moldura de fora para dentro)
        ("portaoO", 31.0, 150.0, "pine", 27.0, 0.8), ("portaoL", 70.0, 148.0, "pine", 29.0, 0.85),
        # atras do terraco do spawn e das casas de fundo
        ("spawnSO", -34.0, 126.0, "pine", 30.0, 1.0), ("spawnS", -4.0, 136.0, "round", 20.0, 8.0),
        ("spawnSE", 14.0, 138.0, "pine", 28.0, 1.0), ("spawnS2", -20.0, 140.0, "round", 17.0, 7.0),
        # sudoeste da praca: atras das casas SW/WS (copa entre os telhados vista da praca e da rua oeste)
        ("trasSW", -50.0, 88.0, "round", 20.0, 8.0), ("trasWS", -63.0, 86.0, "pine", 30.0, 0.85),
        ("trasSW2", -42.0, 98.0, "pine", 26.0, 1.0), ("trasWS2", -78.0, 84.0, "round", 18.0, 7.0),
        ("trasSW3", -26.0, 98.0, "round", 15.0, 6.0),
        # noroeste da praca / canal oeste (atras de NW1-NW2, CW)
        ("canalO", -52.0, 12.0, "round", 18.0, 7.0), ("canalO2", -66.0, 4.0, "pine", 36.0, 0.9),
        # leste: atras da loja e das casas NE/SE, canal leste
        ("trasLoja", 97.0, 40.0, "pine", 30.0, 1.0), ("trasLoja2", 98.0, 56.0, "round", 20.0, 8.0),
        ("trasNE", 70.0, 22.0, "round", 18.0, 7.0), ("trasNE2", 64.0, 11.0, "pine", 38.0, 0.8),
        ("trasSE", 66.0, 64.0, "pine", 26.0, 0.9), ("canalL", 58.0, 6.0, "round", 17.0, 6.5),
        # forja: so ATRAS e nos flancos (fora do largo, longe da frente); altos para subir ao lado da chamine
        ("forjaO", -48.0, -62.0, "pine", 40.0, 1.0), ("forjaO2", -46.0, -84.0, "round", 20.0, 8.0),
        ("forjaN", -12.0, -104.0, "round", 21.0, 8.5), ("forjaN2", 14.0, -106.0, "pine", 32.0, 1.0),
        ("forjaL", 50.0, -78.0, "round", 19.0, 7.5), ("forjaL2", 52.0, -56.0, "pine", 40.0, 1.0),
        ("forjaNO", -38.0, -100.0, "pine", 32.0, 1.0), ("forjaNL", 34.0, -100.0, "round", 18.0, 7.0),
        # rua norte e flancos do largo: pinheiros altos que aparecem por cima dos telhados vistos do spawn
        ("norteO", -36.0, -42.0, "pine", 42.0, 0.8), ("norteL", 46.0, -40.0, "pine", 42.0, 0.8),
        ("norteO2", -31.0, -27.0, "round", 16.0, 6.0), ("norteL2", 30.0, -32.0, "pine", 26.0, 0.8),
        ("norteO3", -58.0, -38.0, "round", 21.0, 8.0), ("norteL3", 62.0, -42.0, "pine", 30.0, 1.0),
        # ranking: atras do salao da guilda
        ("guilda", -118.0, 6.0, "round", 19.0, 7.5), ("guilda2", -110.0, -8.0, "pine", 29.0, 1.0),
    ]


def COURT_TREES():
    """patio dos portais: copas entre os portais (atras, na faixa de grama) e pinheiros nas pontas e no fundo"""
    out = []
    for k in range(7):
        b = math.radians(180.0 + (k - 3.0) * L.PORTAL_STEP_DEG)
        rr = 78.0
        out.append(("patio%d" % k, CCX + math.cos(b) * rr, CCZ + math.sin(b) * rr, "round",
                    17.0 + 2.0 * h01("ct", k), 6.5))
    out += [("patioS", -121.0, 20.0, "pine", 26.0, 1.0), ("patioN", -98.0, 122.0, "pine", 27.0, 1.0),
            ("patioO", -210.0, 72.0, "pine", 28.0, 1.0), ("patioO2", -206.0, 40.0, "pine", 26.0, 1.0),
            ("patioO3", -206.0, 104.0, "pine", 25.0, 1.0), ("patioN2", -92.0, 113.0, "round", 17.0, 6.5)]
    return out


def site_tree(P, x, z, kind, h, R, placed, views, hero=False, slim=1.0):
    """(y, motivo) se o pe pode nascer em (x, z)"""
    rt = 0.42 + R * 0.085 if kind == "round" else 0.32 + h * 0.022
    y = P.natural(x, z)
    if y is None:
        return None, "chao"
    gap = 3.0 if kind == "pine" else 3.8
    if d_way(x, z) < rt + gap:
        return None, "calcamento"
    if P.route_dist(x, z) < (4.0 if hero else 5.5):
        return None, "rota"
    if house_front(x, z, 7.5) or near_door(x, z, 6.0):
        return None, "frente/porta"
    if not P.clear_r(x, z, y + 1.4, rt + 0.9):
        return None, "construido"
    rc = R if kind == "round" else h * 0.16 * slim
    for cx, cz, cr in placed:
        if math.hypot(x - cx, z - cz) < (cr + rc) * (0.5 if hero else 0.62):
            return None, "vizinha"
    sp = tree_spheres(kind, x, z, y, h, R, slim)
    for c, r in sp:
        if not P.clear(c, r):
            return None, "copa x construido"
    tb = tree_box(kind, x, z, y, h, R, slim)
    if any(box_hit(tb, q) for q in P.qa):
        return None, "volume de QA"
    if blocks_view(views, sp):
        return None, "visada"
    return y, None


def place_tree(P, x, z, y, kind, h, R, key, lod=0, slim=1.0):
    rng = K.rng("tree", key, round(x, 1), round(z, 1))
    mb = CELLS[0].get(x, z)
    if kind == "pine":
        t = pine(mb, P, x, z, y, h, rng, lod, slim)
        rt = 0.32 + h * 0.022
        cr = h * 0.16 * slim
    else:
        t = round_tree(mb, P, x, z, y, h, R, rng, lod)
        rt = 0.42 + R * 0.085
        cr = R
    col_box("VegTrunk", (rt * 2.4, rt * 2.4, 8.0), tuple(B(x, z, y + 3.8)))
    TRUNKS.append((x, z, rt + 0.6))
    TREE_SPH.extend(tree_spheres(kind, x, z, y, h, R, slim))
    return t, cr


def trees(P):
    views = VIEWS()
    placed = []
    tris = 0
    rep = {"hero": 0, "patio": 0, "campo": 0, "falhas": {}}
    PLACED_HERO.clear()
    # 1) heroi + patio: com intencao (desloca ate ~4,5 studs em espiral se a sondagem recusar; copa encolhe)
    for grp, lst in (("hero", HERO()), ("patio", COURT_TREES())):
        for (nm, x0, z0, kind, h0, R0) in lst:
            slim = R0 if kind == "pine" else 1.0
            done = False
            why = None
            for k in range(17):
                a = k * 2.4
                d = 0.0 if k == 0 else 1.0 + 0.22 * k
                x, z = x0 + math.cos(a) * d, z0 + math.sin(a) * d
                for f in (1.0, 0.86, 0.74):
                    h = h0 if kind == "pine" else h0 * f
                    R = R0 * f
                    sl = slim * f if kind == "pine" else 1.0
                    y, why = site_tree(P, x, z, kind, h, R, placed, views, hero=True, slim=sl)
                    if y is not None or why not in ("copa x construido", "vizinha"):
                        break
                if y is not None:
                    lod = 0 if (grp == "patio" or d_way(x, z) < 14.0 or P.route_dist(x, z) < 16.0) else 1
                    t, cr = place_tree(P, x, z, y, kind, h, R, (grp, nm), lod, sl)
                    tris += t
                    placed.append((x, z, cr))
                    rep[grp] += 1
                    PLACED_HERO.append((nm, x, z, y, kind, h, R))
                    done = True
                    break
            if not done:
                rep["falhas"]["%s(%s)" % (nm, why)] = (round(x0, 1), round(z0, 1))
    # 2) campo: densidade dirigida (borda da rua -> fora, cinturao do plato, bosques x clareiras)
    cand = []
    step = 9.0
    xs = range(int(-226 / step), int(170 / step) + 1)
    zs = range(int(-128 / step), int(156 / step) + 1)
    for i in xs:
        for j in zs:
            x = i * step + (h01("jx", i, j) - 0.5) * step * 0.8
            z = j * step + (h01("jz", i, j) - 0.5) * step * 0.8
            if not VL.in_poly(x, z, L.PLATEAU):
                continue
            dw = d_way(x, z)
            de = plateau_edge(x, z)
            d = smooth(6.0, 30.0, dw) * 0.8
            if de < 24.0:
                d = max(d, 0.95 - de / 70.0)
            cl = vnoise(x, z, 42.0)
            d *= 0.15 + 1.15 * smooth(0.3, 0.75, cl)
            if h01("acc", i, j) < d * 0.85:
                cand.append((-(d + 0.2 * h01("ord", i, j)), x, z, de, dw))
    cand.sort()
    for _, x, z, de, dw in cand:
        if tris >= TRI_CAP["trees"]:
            rep["falhas"]["teto_tris"] = rep["falhas"].get("teto_tris", 0) + 1
            continue
        pine_p = 0.62 if (de < 30.0 or z < -70.0) else 0.42
        kind = "pine" if h01("kind", round(x), round(z)) < pine_p else "round"
        far = math.hypot(x - 0.0, z - 40.0) > 110.0 or de < 20.0 or dw > 40.0
        if kind == "pine":
            h = 20.0 + 12.0 * h01("ph", round(x), round(z))
            R = 0
        else:
            h = 15.0 + 7.0 * h01("rh", round(x), round(z))
            R = h * 0.4
        y, why = site_tree(P, x, z, kind, h, R, placed, views)
        if y is None:
            rep["falhas"][why] = rep["falhas"].get(why, 0) + 1
            continue
        t, cr = place_tree(P, x, z, y, kind, h, R, ("campo", round(x), round(z)), 1 if far else 0)
        tris += t
        placed.append((x, z, cr))
        rep["campo"] += 1
    rep["tris"] = tris
    STATS["arvores"] = rep
    print("VEG arvores: heroi %d, patio %d, campo %d, %d tris; recusas %s" % (
        rep["hero"], rep["patio"], rep["campo"], tris,
        {k: v for k, v in rep["falhas"].items() if not isinstance(v, tuple)}))
    hf = {k: v for k, v in rep["falhas"].items() if isinstance(v, tuple)}
    if hf:
        print("VEG herois recusados:", hf)
    return placed


# ================================================================== HERA (sondada na pedra)
def ivy_sites():
    """(x, z, fx, fz, nome) Roblox: ponto na face de fora de uma parede de pedra + normal para fora. Quinas da frente
    e lados expostos do terreo das casas (sorteio fixo), ala oeste da forja, torres do portao, fundos do salao da
    guilda, lados da loja"""
    import vm_town as T
    out = []
    for h in T.layout():
        if h["preset"] == "FILL" and h01("ivyF", h["id"]) < 0.6:
            continue
        fx, fz = h["fx"], h["fz"]
        rx, rz = -fz, fx
        W, D = h["W"], h["D"]
        k = h01("ivy", h["id"])
        if k < 0.5:
            s = 1 if k < 0.25 else -1
            cx = h["x"] + fx * (D / 2) + rx * s * (W / 2 - 1.1)
            cz = h["z"] + fz * (D / 2) + rz * s * (W / 2 - 1.1)
            out.append((cx, cz, fx, fz, "casa_" + h["id"]))
        for side, sgn in (("R", 1), ("L", -1)):
            if side not in h["party"] and h01("ivyS", h["id"], side) < 0.6:
                cx = h["x"] + rx * sgn * (W / 2) + fx * (D * 0.12)
                cz = h["z"] + rz * sgn * (W / 2) + fz * (D * 0.12)
                out.append((cx, cz, rx * sgn, rz * sgn, "lado_" + h["id"] + side))
    out += [(35.5, 148.0, -1.0, 0.0, "portao_O"), (64.5, 148.0, 1.0, 0.0, "portao_L")]
    return out


def ivy_scan(P):
    """paredes de PEDRA com pe de grama, achadas por raios: grade de 3 studs no chao natural da vila, 8 raios
    horizontais a 1,5 do chao (alcance 2,6); face vertical de pedra = sitio. So a 4..30 de uma rota (visivel, fora do
    caminho), longe de porta; 1 sitio a cada 13 studs (ordem sorteada fixa)."""
    cands = []
    for i in range(int(-130 / 3), int(112 / 3)):
        for j in range(int(-100 / 3), int(150 / 3)):
            x, z = i * 3.0 + 1.5, j * 3.0 + 1.5
            y = P.natural(x, z)
            if y is None or near_door(x, z, 5.0):
                continue
            rd = P.route_dist(x, z)
            if not (4.0 < rd < 30.0):
                continue
            best = None
            for k in range(8):
                a = TAU * k / 8
                h = P.wall_hit(B(x, z, y + 1.5), Vector((math.cos(a), math.sin(a), 0.0)), 2.6)
                if h is None or not h[2].startswith("Stone_") or abs(h[1].z) > 0.3 or h[3] == "KO":
                    continue
                if h[3].startswith(("VM_Ter_", "VM_Town_")):
                    continue                    # muros do canal / muretas: a hera e das paredes de casa
                d = (h[0] - B(x, z, y + 1.5)).length
                if best is None or d < best[0]:
                    best = (d, h)
            if best:
                hp, n = best[1][0], best[1][1]
                n = Vector((n.x, n.y, 0.0))
                if n.length < 0.5:
                    continue
                n.normalize()
                if n.dot(B(x, z, hp.z) - hp) < 0:
                    n = -n
                cands.append((h01("ivyscan", i, j), hp.x, -hp.y, n.x, -n.y, "scan_%d_%d" % (i, j)))
    cands.sort()
    out = []
    for _, x, z, fx, fz, nm in cands:
        if all(math.hypot(x - a, z - b) > 13.0 for a, b, c, d, e in out):
            out.append((x, z, fx, fz, nm))
    return out


def ivy_patch(mb, P, x, z, fx, fz, rng, key):
    """HERA colada na pedra: acha a face com um raio horizontal a 1,5 do chao; cada folha (placa achatada de 15 tris)
    so nasce onde o raio acha PEDRA a no maximo 0,55 do plano e sem madeira/janela a 0,75 em volta (porta, janela,
    veneziana = nada); a borda da placa e projetada vertice a vertice na pedra (acompanha o relevo: sem atravessar).
    Forma: base larga no chao, linguas irregulares subindo (altura 4,5-8)."""
    IVY_WHY[0] = "porta"
    if near_door(x, z, 3.6):
        return 0, None
    base_y = P.natural(x + fx * 1.0, z + fz * 1.0)
    if base_y is None:
        fl = P.floor_y(x + fx * 1.0, z + fz * 1.0)
        IVY_WHY[0] = "sem chao"
        if fl is None:
            return 0, None
        base_y = fl[0]
    p0 = B(x + fx * 2.5, z + fz * 2.5, base_y + 1.5)
    hit = P.wall_hit(p0, B(-fx, -fz, 0.0), 5.0)
    IVY_WHY[0] = "sem pedra (%s)" % (hit[2] if hit else None)
    if hit is None or not hit[2].startswith("Stone_"):
        return 0, None
    hp, nrm = hit[0], hit[1]
    nrm = Vector((nrm.x, nrm.y, 0.0))
    if nrm.length < 0.5:
        return 0, None
    nrm.normalize()
    if nrm.dot(Vector((fx, -fz, 0.0))) < 0:          # a normal do triangulo pode vir invertida
        nrm = -nrm
    u = Vector((-nrm.y, nrm.x, 0.0))
    W = rng.uniform(2.8, 4.4)
    H = rng.uniform(4.5, 8.0)
    tongues = [rng.uniform(0.4, 1.0) for _ in range(5)]
    t = 0
    made = 0
    bm = mb.bm

    def on_wall(q):
        hn = P.wall_hit(q + nrm * 1.0, -nrm, 2.0)
        if hn is None or not hn[2].startswith("Stone_"):
            return None
        return hn[0]
    for i in range(52):
        a = rng.uniform(-0.5, 0.5)
        hu = tongues[min(4, int((a + 0.5) * 5))] * H * (1.0 - 0.6 * abs(a) * 2)
        v = (rng.random() ** 1.3) * hu
        uu = a * W * (1.0 - 0.4 * v / max(hu, 0.1))
        q = hp + u * uu + ZZ * (v - 1.5 + 0.15)
        if q.z < base_y + 0.05:
            q.z = base_y + 0.05
        hh = P.wall_hit(q + nrm * 1.2, -nrm, 2.2)
        if hh is None or not hh[2].startswith("Stone_") or (hh[0] - q).dot(nrm) < -0.55:
            continue
        bad = False                       # janela / porta por perto (caixilho, veneziana, tabua): a folha nao nasce
        for du, dv in ((0.75, 0.0), (-0.75, 0.0), (0.0, 0.75), (0.0, -0.6)):
            hn = P.wall_hit(q + u * du + ZZ * dv + nrm * 1.2, -nrm, 2.2)
            if hn is not None and hn[2].startswith(("Wood_", "Window_", "Metal_")):
                bad = True
                break
        if bad or near_door(q.x, -q.y, 2.9):
            continue
        r = rng.uniform(0.32, 0.55) * (1.2 if v < 1.0 else 1.0)
        th = rng.uniform(0.16, 0.26)
        m = DARK if (rng.random() < 0.5 or v < 1.0) else MID
        rot = rng.uniform(0, TAU)
        ring0 = []
        ok = True
        for j in range(5):
            aa = rot + TAU * j / 5 + rng.uniform(-0.15, 0.15)
            ca, sa = math.cos(aa), math.sin(aa)
            w = on_wall(q + u * ca * r + ZZ * sa * r * 0.85)
            if w is None:
                ok = False
                break
            ring0.append(w)
        if not ok:
            continue
        dep = [p.dot(nrm) for p in ring0]
        if max(dep) - min(dep) > 0.45:          # quina / vao no meio: a folha ficaria solta demais
            continue
        top_d = max(dep)
        ring0 = [p + nrm * (top_d - p.dot(nrm) + 0.08) for p in ring0]
        c = sum(ring0, Vector()) / 5
        ring1 = [c + (p - c) * 0.68 + nrm * th * 0.6 for p in ring0]
        apex = c + nrm * th + u * rng.uniform(-0.08, 0.08)
        vs = [bm.verts.new(p) for p in ring0 + ring1 + [apex]]
        fs = []
        for j in range(5):
            j2 = (j + 1) % 5
            fs.append((j, j2, 5 + j2, 5 + j))
            fs.append((5 + j, 5 + j2, 10))
        _faces(mb, vs, fs, m)
        t += 15
        made += 1
    IVY_WHY[0] = "poucas folhas (%d)" % made
    if made < 10:
        return t, None
    return t, (hp + ZZ * 1.5, nrm)


IVY_DONE = []
IVY_WHY = [""]


def ivy(P):
    tris = 0
    n = 0
    IVY_DONE.clear()
    done_xz = []
    for (x, z, fx, fz, key) in ivy_sites() + ivy_scan(P):
        if tris >= TRI_CAP["ivy"]:
            break
        if any(math.hypot(x - a, z - b) < 10.0 for a, b in done_xz):
            continue
        rng = K.rng("ivy", key)
        mb = CELLS[0].get(x, z)
        t, info = ivy_patch(mb, P, x, z, fx, fz, rng, key)
        tris += t
        if info:
            n += 1
            IVY_DONE.append((key, info))
            done_xz.append((x, z))
        else:
            STATS.setdefault("hera_fora", {})[key] = IVY_WHY[0]
    STATS["hera"] = {"placas": n, "tris": tris, "onde": [k for k, i in IVY_DONE]}
    print("VEG hera: %d manchas, %d tris: %s" % (n, tris, [k for k, i in IVY_DONE]))
    print("VEG hera fora:", STATS.get("hera_fora"))


def find_cam(P, tgt, dist, up, lens, pref=None, n=24):
    """camera de close: em volta do alvo (Blender), a 'dist' e 'up' acima do alvo; aceita o primeiro angulo (a partir
    de 'pref', rad Blender, alternando para os 2 lados) com a camera fora do construido, sem teto em cima e a visada
    livre ate 1,5 do alvo. -> ((x, y, z) Roblox, alvo Roblox, lente) ou None"""
    a0 = pref if pref is not None else 0.0
    for k in range(n):
        a = a0 + ((k + 1) // 2) * (TAU / n) * (1 if k % 2 else -1)
        cp = tgt + Vector((math.cos(a) * dist, math.sin(a) * dist, up))
        if not P.clear(cp, 1.2) or in_crown(cp):
            continue
        d = tgt - cp
        h = P.built.ray_cast(cp, d.normalized(), d.length - 1.5)
        if h[0] is not None:
            continue
        top = P.top(cp.x, -cp.y)
        if top is not None and top[0] > cp.z:
            continue
        return (cp.x, cp.z, -cp.y), (tgt.x, tgt.z, -tgt.y), lens
    return None


def in_crown(p, pad=1.2):
    return any((p - c).length < r + pad for c, r in TREE_SPH)


def resolve_closes(P):
    """cameras de close nos herois plantados (copa redonda e pinheiro da rua de saida) e na hera mais visivel"""
    want = {"CAM_VM_V3_Close_Arvore": ("trasE2", "trasE4", "cantoE1", "spawnS", "trasSW"),
            "CAM_VM_V3_Close_Pinheiro": ("vaoE2E3", "trasW1", "trasE3", "spawnSO", "trasWS")}
    for cam, names in want.items():
        for nm in names:
            hit = [h for h in PLACED_HERO if h[0] == nm]
            if not hit:
                continue
            _, x, z, y, k, h, R = hit[0]
            tgt = B(x, z, y + h * 0.42)
            c = find_cam(P, tgt, h * 1.15, -h * 0.42 + 6.5, 24)
            if c:
                CLOSES[cam] = c
                break
    for key, (c, nrm) in IVY_DONE:
        r = find_cam(P, c, 8.5, 1.0, 26, pref=math.atan2(nrm.y, nrm.x), n=10)
        if r:
            CLOSES["CAM_VM_V3_Close_Hera"] = r
            break


# ================================================================== CHAO: tufos, flores, moitas, sebes (after_props)
def ground_cover(P, foot):
    """foot = [(x, z, r)] pegadas dos props e troncos (o tufo nao entra nelas)"""
    tris = 0
    rep = {"tufos": 0, "flores": 0, "moitas": 0, "sebes": 0}
    cap = [0.0]                     # teto da secao corrente (rua / pe / sebe / prado)

    def free(x, z, r=0.5):
        if any(math.hypot(x - a, z - b) < c + r for a, b, c in foot):
            return False
        return True

    def put_tuft(x, z, s, key, m=LIGHT):
        nonlocal tris
        if tris >= cap[0]:
            return False
        y = P.natural(x, z)
        if y is None or not free(x, z) or near_door(x, z, 3.0) or not P.clear_r(x, z, y + 0.6, 0.7):
            return False
        mb = CELLS[0].get(x, z)
        tris += tuft(mb, x, z, y, K.rng("tf", key), s, m)
        rep["tufos"] += 1
        return True

    def put_flower(x, z, key):
        nonlocal tris
        if tris >= cap[0]:
            return False
        y = P.natural(x, z)
        if y is None or not free(x, z, 1.2) or near_door(x, z, 3.5) or not P.clear_r(x, z, y + 0.6, 1.0):
            return False
        mb = CELLS[0].get(x, z)
        tris += flower_patch(mb, x, z, y, K.rng("fl", key), K.FLOWERS[CELL_FLOWER[cell_of(x, z)]])
        rep["flores"] += 1
        return True

    def put_bush(x, z, r, key):
        nonlocal tris
        if tris >= cap[0]:
            return False
        y = P.natural(x, z)
        if y is None or not free(x, z, r) or near_door(x, z, 4.0) or d_way(x, z) < r * 0.6 or \
                not P.clear_r(x, z, y + r * 0.6, r * 0.95) or P.route_dist(x, z) < 3.0:
            return False
        mb = CELLS[0].get(x, z)
        tris += bush(mb, P, x, z, y, r, K.rng("bu", key), lumps=2)
        foot.append((x, z, r * 0.8))
        rep["moitas"] += 1
        return True

    # 1) borda de grama das ruas: 2 fileiras (a de fora mais densa e mais alta) + manchas de flores
    import vm_town as T
    cap[0] = tris + GROUND_CAP["rua"]
    roads = [("oeste", T.west_path(), 7.1), ("saida", T.Path(L.EXIT_ROAD, smooth=2), 7.1),
             ("loja", T.Path([(30.0, 43.0), (61.9, 43.0)]), 6.1), ("norte", T.Path([(0.0, -21.0), (0.0, -36.4)]), 9.8),
             ("eixo", T.Path([(0.0, 15.0), (0.0, 1.0)]), 9.8), ("praca", T.circle_path(PCX, PCZ, 36.8), 0.0)]
    for nm, path, hw in roads:
        s = 0.0
        i = 0
        while s < path.L:
            for sg in ((-1, 1) if nm != "praca" else (1,)):
                for row, (t0, t1, pr, sc) in enumerate(((0.35, 1.3, 0.5, 0.85), (1.6, 3.6, 0.7, 1.2))):
                    k = (nm, i, sg, row)
                    if h01("re", *k) > pr * (0.55 + 0.6 * vnoise(*path.pt(s), sc=17.0, key="edge")):
                        continue
                    t = hw + t0 + (t1 - t0) * h01("rt", *k)
                    x, z = path.pt(s, sg * t)
                    if h01("rf", *k) < 0.16 and row == 1:
                        put_flower(x, z, k)
                    else:
                        put_tuft(x, z, sc * (0.8 + 0.5 * h01("rs", *k)), k, LIGHT if h01("rm", *k) < 0.7 else MID)
            s += 1.9 + 1.6 * h01("rds", nm, i)
            i += 1
    # 2) pe das paredes (frente e lados das casas, quando ha grama) e das arvores
    cap[0] = tris + GROUND_CAP["pe"]
    for idx, (hx, hz, fx, fz, W, D) in enumerate(HOUSES or []):
        rx, rz = -fz, fx
        for k in range(int(W / 1.6) + 1):
            if h01("wf", idx, k) > 0.45:
                continue
            u = -W / 2 + W * (k + 0.5) / (int(W / 1.6) + 1)
            v = D / 2 + 0.6 + 0.6 * h01("wv", idx, k)
            put_tuft(hx + fx * v + rx * u, hz + fz * v + rz * u, 0.8, ("wf", idx, k))
    for i, (x, z, r) in enumerate(list(TRUNKS)):
        n = 1 + int(3 * h01("tb", i))
        for k in range(n):
            a = h01("tba", i, k) * TAU
            d = r + 0.8 + 1.6 * h01("tbd", i, k)
            if k == 0 and h01("tbb", i) < 0.35:
                put_bush(x + math.cos(a) * (d + 0.8), z + math.sin(a) * (d + 0.8), 1.4 + 0.6 * h01("tbr", i), ("tb", i))
            else:
                put_tuft(x + math.cos(a) * d, z + math.sin(a) * d, 1.0 + 0.4 * h01("tbs", i, k), ("tt", i, k), MID)
    # 3) sebes podadas: flancos do terraco do spawn, quintais das casas de fundo, borda do canal sul
    hedges = [((-23.0, 92.0), (-23.0, 110.0)), ((23.0, 92.0), (23.0, 110.0)), ((-30.0, 116.0), (-30.0, 132.0)),
              ((-18.0, 131.0), (20.0, 131.0)), ((62.0, 2.0), (92.0, 2.0)), ((-60.0, 112.0), (-36.0, 112.0))]
    cap[0] = tris + GROUND_CAP["sebe"]
    for i, (a, b) in enumerate(hedges):
        if tris >= cap[0]:
            break
        t = hedge(CELLS[0].get(*a), P, a, b, K.rng("hedge", i))
        if t:
            rep["sebes"] += 1
            tris += t
    # 4) prados nos arredores: manchas de capim alto e flores onde o ruido de prado e alto e longe da rua
    cap[0] = TRI_CAP["ground"]
    step = 6.0
    mc = []                          # ordem sorteada (fixa): o teto nao corta sempre o mesmo lado do plato
    for i in range(int(-226 / step), int(170 / step) + 1):
        for j in range(int(-128 / step), int(156 / step) + 1):
            x = i * step + (h01("mx", i, j) - 0.5) * step
            z = j * step + (h01("mz", i, j) - 0.5) * step
            if not VL.in_poly(x, z, L.PLATEAU):
                continue
            mead = vnoise(x, z, 30.0, "mead") * smooth(5.0, 20.0, d_way(x, z))
            if mead >= 0.5:
                mc.append((h01("mord", i, j), i, j, x, z))
    mc.sort()
    for _, i, j, x, z in mc:
        if tris >= cap[0]:
            break
        u = h01("mk", i, j)
        if u < 0.16:
            put_flower(x, z, ("m", i, j))
        elif u < 0.55:
            for k in range(3):
                a = h01("ma", i, j, k) * TAU
                put_tuft(x + math.cos(a) * 1.3, z + math.sin(a) * 1.3, 1.3, ("mt", i, j, k))
        elif u < 0.6:
            put_bush(x, z, 1.6 + 0.8 * h01("mr", i, j), ("mb", i, j))
    rep["tris"] = tris
    STATS["chao"] = rep
    print("VEG chao:", rep)


# ================================================================== BUILD
def clear():
    """apaga a vegetacao do blockout V0 (VM_Veg_Trees_*) e do V2b (VM_Veg_Court) + uma execucao anterior do V3a"""
    n = 0
    for o in list(bpy.data.objects):
        if o.name.startswith(("VM_Veg_", "COL_VegTrunk_")):
            bpy.data.objects.remove(o, do_unlink=True)
            n += 1
    fm_lib._COL_COUNT.pop("VegTrunk", None)
    TRUNKS.clear()
    TREE_SPH.clear()
    CLOSES.clear()
    STATS.clear()
    DOORS.clear()
    HOUSES.clear()
    PATHS.clear()
    return n


def build():
    """arvores + hera (antes dos props). O chao (tufos, flores, moitas, sebes) vem em after_props()."""
    STATS["apagados"] = clear()
    house_front(0.0, 0.0)             # carrega HOUSES
    P = Probe()
    CELLS[0] = Cells()
    placed = trees(P)
    ivy(P)
    resolve_closes(P)
    return placed


def after_props(foot=()):
    P = Probe()
    if CELLS[0] is None:
        CELLS[0] = Cells()
    ground_cover(P, list(foot) + list(TRUNKS))
    resolve_arredor(P)
    obs = CELLS[0].finish()
    CELLS[0] = None
    STATS["objetos"] = [o.name for o in obs]
    return report(True)


def cams():
    E = L.EYE
    Y = L.Y_PAVE
    c = dict(CLOSES)
    for k, v in ARREDOR().items():
        c.setdefault(k, v)
    c["CAM_VM_V3_Air_Norte"] = ((40.0, 120.0, -230.0), (0.0, 0.0, -10.0), 24)
    return c


def ARREDOR():
    E = L.EYE
    Y = L.Y_PAVE
    return {"CAM_VM_V3_Arredor_SO": ((-19.0, L.Y_SPAWN + E, 104.0), (-80.0, 12.0, 118.0), 20),     # terraco do spawn
            "CAM_VM_V3_Arredor_Loja": ((70.0, Y + E, 66.0), (140.0, 11.0, 50.0), 18),             # sul da loja -> leste
            "CAM_VM_V3_Arredor_Norte": ((-30.0, L.Y_NORTH + E, -24.0), (-100.0, 12.0, -60.0), 18)}  # margem norte -> NO


def resolve_arredor(P):
    """as cameras dos arredores fogem de tronco e de parede (espiral de ate 7 studs na altura do olho)"""
    for nm, (pos, tgt, lens) in ARREDOR().items():
        for k in range(30):
            a = k * 2.4
            d = 0.0 if k == 0 else 0.8 + 0.22 * k
            x, z = pos[0] + math.cos(a) * d, pos[2] + math.sin(a) * d
            if any(math.hypot(x - tx, z - tz) < tr + 6.0 for tx, tz, tr in TRUNKS):
                continue
            cp = B(x, z, pos[1])
            if not P.clear(cp, 1.5) or in_crown(cp, 2.0):
                continue
            tv = B(tgt[0], tgt[2], tgt[1])
            dd = tv - cp
            h = P.built.ray_cast(cp, dd.normalized(), dd.length * 0.5)
            if h[0] is not None:
                continue
            CLOSES[nm] = ((x, pos[1], z), tgt, lens)
            break


def cameras():
    for n, (loc, tgt, lens) in cams().items():
        fm_lib.camera(n, VL.B(loc[0], loc[2], loc[1]), VL.B(tgt[0], tgt[2], tgt[1]), lens)


# ================================================================== relatorio + intersecao contra o construido
def _tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def isect(prefixes=("VM_Veg_", "VM_Prop_")):
    """sobreposicao REAL de triangulos dos objetos do V3a contra o construido (piso descontado: triangulo construido
    horizontal (n.z > 0,8) com o encontro a menos de 0,4 da cota dele = assentado no chao/calcamento)"""
    P = Probe()
    out = {}
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type != "MESH" or not o.name.startswith(prefixes):
            continue
        mw = o.matrix_world
        vs = [mw @ v.co for v in o.data.vertices]
        ps = [list(p.vertices) for p in o.data.polygons]
        if not ps:
            continue
        mats = [m.name if m else "" for m in o.data.materials]
        pmat = [mats[p.material_index] for p in o.data.polygons]
        b = BVHTree.FromPolygons(vs, ps)
        bad = 0
        where = {}
        for i, j in b.overlap(P.built):
            f = P.bP[j]
            n = (P.bV[f[1]] - P.bV[f[0]]).cross(P.bV[f[2]] - P.bV[f[0]])
            if n.length > 1e-9 and abs(n.normalized().z) > 0.8:
                continue                 # piso / calcamento / topo de mureta: assentado
            zmine = min(vs[k].z for k in ps[i])
            if max(P.bV[k].z for k in f) < zmine + 0.35:
                continue                 # quina de paralelepipedo / meio-fio logo abaixo da base: assentado
            own = P.bown[j]
            if pmat[i].startswith(("Leaf_", "Bark")) and own == "KO":
                pass
            bad += 1
            k = "%s<-%s" % (pmat[i], own)
            where[k] = where.get(k, 0) + 1
        out[o.name] = {"pares": bad, "onde": dict(sorted(where.items(), key=lambda kv: -kv[1])[:6])}
    return out


def report(print_=True, path=None, do_isect=True):
    rows = {}
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type != "MESH" or not o.name.startswith(("VM_Veg_", "VM_Prop_")):
            continue
        mats = sorted({o.data.materials[p.material_index].name for p in o.data.polygons})
        own = "vegetation" if o.name.startswith("VM_Veg_") else "props"
        xs = [(o.matrix_world @ v.co) for v in o.data.vertices]
        ext = (max(v.x for v in xs) - min(v.x for v in xs), max(v.y for v in xs) - min(v.y for v in xs)) if xs else (0, 0)
        rows[o.name] = {"dono": own, "tris": _tris(o), "materiais": len(mats), "mats": mats,
                        "extensao": [round(ext[0], 1), round(ext[1], 1)]}
    own = {}
    for v in rows.values():
        t = own.setdefault(v["dono"], [0, 0])
        t[0] += v["tris"]
        t[1] += v["materiais"]
    ncol = {"VegTrunk": sum(1 for o in bpy.data.objects if o.name.startswith("COL_VegTrunk_")),
            "Prop": sum(1 for o in bpy.data.objects if o.name.startswith("COL_Prop"))}
    out = {"objetos": rows, "por_dono": own, "stats": STATS, "col": ncol}
    if do_isect:
        out["isect"] = isect()
    if print_:
        for k, v in rows.items():
            print("   %-18s %-10s %6d tris %2d mat  ext %s  %s" % (k, v["dono"], v["tris"], v["materiais"],
                                                                   v["extensao"], ",".join(v["mats"])))
        for k, v in sorted(own.items()):
            lim = L.BUDGET_OWNER.get(k, ("-", "-"))
            print("V3A dono %-10s %7d tris (%s)  ~%3d MeshParts (%s)" % (k, v[0], lim[0], v[1], lim[1]))
        print("V3A COL", ncol)
        if do_isect:
            tot = sum(v["pares"] for v in out["isect"].values())
            print("V3A ISECT pares de triangulos contra o construido (sem piso): %d" % tot)
            for k, v in out["isect"].items():
                if v["pares"]:
                    print("   ISECT %-18s %4d  %s" % (k, v["pares"], v["onde"]))
    if path:
        json.dump(out, open(path, "w", encoding="utf-8"), indent=1, default=str)
    return out


# ================================================================== folhas (python puro + PIL)
def sheets(dp, dr, outd):
    import vm_sheet as SH
    os.makedirs(outd, exist_ok=True)
    W2 = 960

    def pair(cam, title):
        return [SH.label(SH.fit(os.path.join(dp, cam + ".jpg")), "V3a PREVIA  " + title),
                SH.label(SH.fit(os.path.join(dr, cam + ".jpg")), "V3a ROBLOX  " + title)]

    def ex(cam, d=None):
        return os.path.exists(os.path.join(d or dr, cam + ".jpg"))

    ref = SH.label(SH.fit(os.path.join(SH.REF, "ref_01_estilo_vila.jpg"), W2, 540), "REFERENCIA ref_01")
    SH.compose([[ref, SH.label(SH.fit(os.path.join(dr, "CAM_VM_V2_Ref01.jpg")), "V3a ROBLOX  rua curva de saida")],
                [SH.label(SH.fit(os.path.join(dp, "CAM_VM_V2_Ref01.jpg")), "V3a PREVIA  rua curva de saida"),
                 SH.label(SH.fit(os.path.join(dr, "CAM_VM_V2_RuaSaida.jpg")), "V3a ROBLOX  praca -> rua de saida")]],
               os.path.join(outd, "FOLHA_ref01.jpg"), "Lobby Vila Medieval V3a - ref_01 x vila (vegetacao + props)")
    groups = [("FOLHA_spawn_forja.jpg", "spawn -> praca -> forja",
               [("CAM_VM_V2_SpawnPraca", "SpawnPraca"), ("CAM_VM_V2_PracaForja", "PracaForja"),
                ("CAM_VM_V2_RuaForja", "RuaForja")]),
              ("FOLHA_praca360.jpg", "praca 360",
               [("CAM_VM_V2_Praca360_%d" % k, "Praca 360 / %d" % (k * 90)) for k in range(4)]),
              ("FOLHA_portais.jpg", "patio dos portais e ranking",
               [("CAM_VM_V2_Portais", "Portais"), ("CAM_VM_V2_PortaisDentro", "PortaisDentro"),
                ("CAM_VM_V2_Ranking", "Ranking")]),
              ("FOLHA_loja.jpg", "loja e arredores do leste",
               [("CAM_VM_V2_LojaFora", "LojaFora"), ("CAM_VM_V3_Arredor_Loja", "leste da loja")]),
              ("FOLHA_saida_ponte.jpg", "rua de saida, portao e ponte",
               [("CAM_VM_V2_RuaSaida", "RuaSaida"), ("CAM_VM_V2_Portao", "Portao"), ("CAM_VM_V2_Ponte", "Ponte")]),
              ("FOLHA_arredores.jpg", "arredores (sudoeste, norte)",
               [("CAM_VM_V3_Arredor_SO", "sudoeste"), ("CAM_VM_V3_Arredor_Norte", "norte (canal -> bosque)")]),
              ("FOLHA_aerea.jpg", "aereas",
               [("CAM_VM_V2_Air_SE", "aerea sudeste"), ("CAM_VM_V2_Air_W", "aerea oeste"),
                ("CAM_VM_V3_Air_Norte", "aerea norte")])]
    for fn, title, cams_ in groups:
        rows = [pair(c, t) for c, t in cams_ if ex(c) and ex(c, dp)]
        if rows:
            SH.compose(rows, os.path.join(outd, fn), "Lobby Vila Medieval V3a - " + title)
    closes = [c for c in ("CAM_VM_V3_Close_Arvore", "CAM_VM_V3_Close_Pinheiro", "CAM_VM_V3_Close_Hera",
                          "CAM_VM_V3_Close_Props1", "CAM_VM_V3_Close_Props2", "CAM_VM_V3_Close_Placa")
              if ex(c)]
    rows = []
    for i in range(0, len(closes), 2):
        rows.append([SH.label(SH.fit(os.path.join(dr, c + ".jpg")), "ROBLOX  " + c.replace("CAM_VM_V3_Close_", ""))
                     for c in closes[i:i + 2]])
    if rows:
        SH.compose(rows, os.path.join(outd, "FOLHA_closes_roblox.jpg"), "Lobby Vila Medieval V3a - closes (Roblox)")
    if ex("CAM_VM_Plan", dp):
        SH.compose([[SH.fit(os.path.join(dp, "CAM_VM_Plan.jpg"), 960)]], os.path.join(outd, "FOLHA_planta.jpg"),
                   "Lobby Vila Medieval V3a - vista de cima (previa)")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    if argv and argv[0] == "sheets":
        sheets(argv[1], argv[2], argv[3])
    elif argv and argv[0] == "report":
        report(True, argv[1] if len(argv) > 1 else None)
