# op_veg.py - VEGETACAO da Ilha 5 (ONE PIECE / WANO), M4 (PLANO_OP secoes 0, 9, 14; PROMPT_USUARIO secoes 9, 15, 17).
# Substitui op_blockout.dressing (OP_Veg_Blockout). Prefixo OP_Veg_, colecao 10_VEGETATION, sem luz. Colisao SO nos
# troncos que o jogador alcanca (COL_OP_VegTrunk_*: pe dentro de um piso andavel e a <= 40 de uma rota).
#
# V2 (feedback do usuario 10/10, item U4: "arvores menores como esferas/poliedros facetados verdes; cerejeiras em
#   blocos rosas" REPROVADO; pedido: atmosfera da ref_03 = cerejeiras rosas densas pela cidade + petalas no ar).
#   Regras de posicionamento, setores, testes malha x malha e API (place_*, Placer, add_item, TRUNKS) MANTIDOS;
#   trocadas as FAMILIAS (primitivas suaves do op_tree: puff/blob_crown, cloud_pad, limb) e a distribuicao (mais rosa).
#
# FAMILIAS V2 (reutilizaveis; nada de espalhar ao acaso):
#   - CEREJEIRA (sakura) XS/S/M/L: tronco ESCURO em S com pe alargado, bracos que abrem; copa FOFA (V2b,
#     op_tree.fluffy_crown): por parte da copa um nucleo escuro + cachos medios + sub-cachos na borda/pendentes, todos
#     esferas PEQUENAS de baixa resolucao com sombreado suave, 1 tom por esfera pela altura (topo Flower_OP_Light,
#     meio _Blossom, baixo/miolo _Deep). Light so nos setores da cidade/entrada/castelo (MeshParts).
#   - KUROMATSU: tronco escuro em S que se debruca, galhos quase horizontais e ALMOFADAS EM NUVEM (cloud_pad: disco
#     de borda lobada, topo Leaf_OP, lado/baixo Leaf_OP_Pine) - a linguagem da arvore monumental em pequeno.
#   - ARVORE VERDE LARGA: copa de cachos verdes (blob_crown verde: cachos Leaf_OP, nucleo/baixo verde-pinho).
#   - MOITA PODADA (karikomi): 1-3 montes arredondados achatados embaixo (copa fofa verde, V2b).
#   - VERDE DE FALESIA: as almofadas (cushion) agora sao cloud_pad suaves de borda lobada (nao poliedros).
#   - Bambu: nao entrou (sem lugar na planta que pedisse; seria familia sem funcao).
# PETALAS: cherry_groups() agrupa as cerejeiras plantadas (<= 40 entre si, grupo compacto) e o op_vfx grava 1
#   FX_Petals_* por grupo (os 13 mais pesados + a deriva da praca = 14 emissores).
# DISTRIBUICAO V2: quintais da cidade 85% cerejeira (M -> S -> XS, o maior que cabe), faixa da borda com 28%
#   cerejeira; heroi/capital como antes. Orcamento 54k (lead: <= 55k) e 9 setores x materiais <= 50 MeshParts.
#
# INTENCAO (densidade DIRIGIDA, cresce para as BORDAS; ordem = prioridade de orcamento):
#   1. HERO_CHERRIES (lista com nota): ombros do grande torii, cantos da praca POR FORA do piso, rochas dos 2 lados do
#      castelo (moldura do rochedo vista da praca), promontorio da saida, frente leste/oeste, terraco alto, summon...
#   2. op_capital.VEG_SPOTS (recantos, patamares das pontes do canal, mirantes): o maior tamanho que cabe (M -> S -> XS).
#   3. HERO_PINES: pontas de rocha (narizes da entrada, contrafortes do castelo, rochas NE, fundo, esporao da espada).
#   4. QUINTAIS (city_yards): copas entre os telhados, longe da borda (V2: cerejeira 85% / verde 15%); fora do
#      terraco do summon (jardim do op_summon).
#   5. BOSQUE das rochas do fundo/NE/promontorio e jardins do terraco alto e de alem do canal (FOREST).
#   6. FAIXA DA BORDA: 3 fileiras para dentro da crista, densidade por setor (ruido dirigido de baixa frequencia).
#   7. VERDE DE FALESIA na crista (cliff_greens), 8. tufos na face (face_clumps), 9. PRATELEIRAS de musgo do
#      OP_Ter_Cliff (moita ou pinheirinho), 10. moitas de PE DE MURO (afastadas do muro pelo raio).
#   Setores sem verde novo na borda (RIM_SKIP): nariz da entrada, gargantas das quedas, cabeca da ponte de saida,
#   ancora OPM, cais.
# REGRAS (Placer.try_site / crown_ok / add_item): chao NATURAL (OP_Ter_/OP_Lmk_ com grama, musgo ou terra; quintal de
#   terra do OP_Cap_; rocha nua so para pinheiro), plano em volta do tronco; fora da MiningZone + 10 e do piso da PRACA
#   + 3 (praca: so na borda); tronco longe de ROTAS, RUAS (L.STREETS + LANES), ESCADAS, AGUA, PONTES e do vao do torii;
#   COPA: nao cobre rua nem ponte, fora das VISADAS (gate do QA, PlayerHeight e Ref_01/02, silhueta castelo + arvore, e
#   as cameras _PH_ dos outros modulos que ja estao na cena: eixo proximo livre e nada a menos de 6 do olho), nunca
#   sobre a MiningZone abaixo de piso + 12; e depois de GERADA a planta passa por um teste EXATO malha x malha contra
#   todo o construido (casas, castelo, props...): se atravessa, e desfeita (o pe enraizado no chao horizontal vale).
#   Espacamento entre copas por familia; NUDGE ate 7; senao a planta nao nasce (o log lista as que faltaram e por que).
# ORCAMENTO (V2: teto do lead 55k tris / 50 MeshParts): BUDGET_TRIS proprio.
#   9 objetos por SETOR; a peca (objeto, material) de um setor que passa de 158 studs fica abaixo de CAP tris (o export
#   so fatia peca >= 1500 tris E > 160 studs), senao a planta vai para o setor vizinho com folga. 5-6 materiais por
#   setor (Wood_OP_Dark, Leaf_OP, Leaf_OP_Pine, Flower_OP_Blossom/_Deep; _Light so em LIGHT_SECTORS).
# ORDEM no build_op: props -> VEG -> vfx -> lights (a vegetacao enxerga os props e desvia deles). after_props() e o
#   gancho que o op_lights chama: auditoria final tronco x props. TRUNKS (x, y, z, r_tronco, R_copa, familia) exposto.
# Deterministico: hash com finalizador murmur (hh), rng por planta (rng_at), objetos da cena percorridos por nome.
import math, random, zlib
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, col_box
import op_layout as L
import op_tree as TR

C = "10_VEGETATION"
BARK, LEAF, PINE = "Wood_OP_Dark", "Leaf_OP", "Leaf_OP_Pine"
ZZ = Vector((0.0, 0.0, 1.0))
TAU = math.tau
T0, T1, P, CF, CC, W3Z = L.T0, L.T1, L.P, L.CF, L.CC, L.W3
MINE_PAD = 10.0
BUDGET_TRIS = 54000             # V2: teto do lead 55k (familias suaves custam mais por planta: menos plantas, melhores)
TRUNKS = []                      # (x, y, z, r_tronco, R_copa, familia) - exposto
STATS = {}


# ================================================================== hash dirigido (finalizador murmur)
def hh(*a):
    s = "|".join(("%.2f" % v) if isinstance(v, float) else str(v) for v in a)
    h = zlib.crc32(s.encode("utf-8")) ^ 0x9E3779B9
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967296.0


def rng_at(*k):
    return random.Random(int(hh(*k) * 2147483647))


def vdir(a, z=0.0):
    return Vector((math.cos(a), math.sin(a), z))


# ================================================================== a cena ja montada
class Probe:
    """raios contra o que as outras zonas montaram: o chao natural onde a planta nasce e o construido que copa nenhuma
    atravessa"""
    NAT_OWNER = ("OP_Ter_", "OP_Lmk_", "OP_Cap_")      # terreno, rocha dos marcos, quintais de terra da capital
    NAT_MAT = ("Grass_OP", "Cliff_OP_Moss", "Dirt_OP")
    ROCK_MAT = ("Cliff_OP",)                             # topo de rocha nua: so pinheiro/moita/tufo (rock=True)

    def __init__(self):
        V, F, self.own, self.mat = [], [], [], []
        bV, bF = [], []
        self.bnz = []
        for o in sorted(bpy.data.objects, key=lambda o: o.name):
            if o.type != "MESH" or o.hide_render or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "OP_Veg_",
                                                                           "OP_Plz_OreProxy")):
                continue
            mw = o.matrix_world
            me = o.data
            vs = [mw @ v.co for v in me.vertices]
            mats = [m.name if m else "" for m in me.materials]
            b = len(V)
            V += vs
            for p in me.polygons:
                F.append([b + i for i in p.vertices])
                self.own.append(o.name)
                self.mat.append(mats[p.material_index] if p.material_index < len(mats) else "")
            if not o.name.startswith("OP_Ter_"):
                b2 = len(bV)
                bV += vs
                bF += [[b2 + i for i in p.vertices] for p in me.polygons]
                R3 = mw.to_3x3()
                self.bnz += [abs((R3 @ p.normal).normalized().z) for p in me.polygons]
        self.bvh = BVHTree.FromPolygons(V, F)
        self.built = BVHTree.FromPolygons(bV, bF) if bF else None
        self.routes = [pts for pts, z in L.routes().values()]
        self.stairs = [r for nm, up, r, zf, zt in L.stair_notches()]

    def top(self, x, y, z0=420.0):
        h = self.bvh.ray_cast(Vector((x, y, z0)), Vector((0.0, 0.0, -1.0)), 600.0)
        if h[0] is None:
            return None
        return h[0].z, self.own[h[2]], self.mat[h[2]], abs(h[1].z)

    def natural(self, t, rock=False):
        """chao onde a planta nasce. A normal vem do enrolamento da face (parte da pele do terreno tem a face
        invertida): vale |nz|"""
        if t is None or not t[1].startswith(self.NAT_OWNER):
            return False
        if t[1].startswith("OP_Cap_") and not t[2].startswith(("Dirt_OP", "Grass_OP")):
            return False
        return t[2].startswith(self.NAT_MAT) or (rock and t[1].startswith(("OP_Ter_", "OP_Lmk_")) and
                                                 t[2].startswith(self.ROCK_MAT))

    def gz(self, x, y, fallback):
        t = self.top(x, y)
        return t[0] if t else fallback

    def clear_of_built(self, p, r):
        if self.built is None:
            return True
        return self.built.find_nearest(Vector(p), r)[0] is None

    def route_dist(self, x, y):
        return min(L.polyline_dist(x, y, pts) for pts in self.routes)


# ================================================================== zonas proibidas (planta)
def _bridge_lines():
    """pontes (eixo, meia largura): chegada, saida, 2 pontes vermelhas do canal"""
    out = [([(0.0, -125.0), (0.0, 2.0)], 11.0), ([L.exit_point(-2.0), L.exit_point(L.EXIT_BRIDGE_LEN + 2.0)], 12.0)]
    for y in (182.0, 252.0):
        out.append(([(-190.0, y), (-158.0, y)], 7.0))
    return out


BRIDGES = _bridge_lines()
WATER = [[(p[0], p[1]) for p in L.CANAL_E], [(p[0], p[1]) for p in L.CANAL_W]]
TORII_KO = ([(-16.0, 10.0), (16.0, 10.0)], 7.0)        # vao do grande torii (copa nenhuma na moldura da entrada)
# vielas da capital que nao estao no L.STREETS (op_capital: travessa L-O do bloco leste ate o mirante do porto)
LANES = [([(48.0, 75.0), (100.0, 73.0)], 5.5)]      # ate o pe do mirante (o mirante tem cerejeira: VEG_SPOTS)


def in_mine(x, y, pad=MINE_PAD):
    x0, y0, x1, y1 = L.MINE_RECT
    return x0 - pad < x < x1 + pad and y0 - pad < y < y1 + pad


def plan_reject(x, y, r, R):
    """motivo (str) se a planta da ilha proibe um tronco de raio r e copa R em (x, y); None se pode"""
    if in_mine(x, y):
        return "zona"
    if L.point_in_poly(x, y, DL.offset_poly(L.PLAZA, 3.0 + r)):
        return "praca"
    for pts, w, z in L.STREETS:
        if L.polyline_dist(x, y, pts) < w / 2 + 1.5 + r:
            return "rua"
    for pts, hw in BRIDGES:
        if L.polyline_dist(x, y, pts) < hw + max(r + 1.0, R * 0.7):
            return "ponte"
    for pts, hw in LANES:
        if L.polyline_dist(x, y, pts) < hw + r + 1.0:
            return "rua"
    if L.polyline_dist(x, y, TORII_KO[0]) < TORII_KO[1] + R * 0.6:
        return "torii"
    for w in WATER:
        if L.polyline_dist(x, y, w) < 5.0 + r:
            return "agua"
    if L.point_in_poly(x, y, DL.offset_poly(L.BASIN, 3.0 + r)):
        return "agua"
    for rr in STAIRS_R:
        if rr[0] - 3.0 - r < x < rr[2] + 3.0 + r and rr[1] - 3.0 - r < y < rr[3] + 3.0 + r:
            return "escada"
    if L.point_in_poly(x, y, DL.offset_poly(TR.TREE_KEEPOUT, 2.0 + r)):
        return "arvore"
    return None


STAIRS_R = [r for nm, up, r, zf, zt in L.stair_notches()]


# ================================================================== visadas protegidas
def protected_views():
    """(olho, alvo): gate do QA, PlayerHeight/Ref e silhueta castelo + arvore"""
    cams = L.cams()
    keep_top = Vector((L.KEEP_C[0], L.KEEP_C[1], L.KEEP_TOP_Z + 2.0))
    keep_mid = Vector((L.KEEP_C[0], L.KEEP_C[1] - 20.0, CC + 30.0))
    tt = L.TREE_TRUNK[8]
    tree_top = Vector((tt[0], tt[1], tt[2] + tt[3] + 3.0))
    tree_mid = Vector((TR.TRUNK[5][0], TR.TRUNK[5][1], TR.TRUNK[5][2]))
    star = None
    o = bpy.data.objects.get("L_OPSum_Star")
    if o:
        star = o.location.copy()
    fall = Vector((L.CASTLE_FALL[0], L.CASTLE_FALL[1] - 1.0, L.CASTLE_FALL[2] - 4.0))
    ship = Vector((L.SHIP_C[0], L.SHIP_C[1] + 10.0, L.SHIP + 40.0))
    g = L.gate_opm_pos()
    gopm = Vector((g[0], g[1], T1 + 12.0))
    torii = Vector((L.TORII_IN[0], L.TORII_IN[1], T0 + 14.0))
    gate = Vector((L.CASTLE_GATE[0], L.CASTLE_GATE[1], CF + 10.0))
    out = []
    for cn in L.PLAYER_CAMS + L.REF_CAMS + ["CAM_OP_Entry", "CAM_OP_Plaza", "CAM_OP_Castle", "CAM_OP_Harbor",
                                             "CAM_OP_Summon", "CAM_OP_Exit", "CAM_OP_Tree", "CAM_OP_Skull"]:
        if cn not in cams:
            continue
        eye, tg = Vector(cams[cn][0]), Vector(cams[cn][1])
        out.append((eye, tg))
        if cn in L.PLAYER_CAMS or cn in L.REF_CAMS:
            for p in (keep_top, keep_mid, tree_top, tree_mid, star, gate):
                if p is not None:
                    out.append((eye, p))
    for eye, p in (((0.0, -100.0, L.DECK + 0.6 + L.EYE), keep_top), ((0.0, -100.0, L.DECK + 0.6 + L.EYE), tree_top),
                   ((0.0, -100.0, L.DECK + 0.6 + L.EYE), torii), ((0.0, 24.0, T0 + L.EYE), keep_top),
                   ((0.0, 24.0, T0 + L.EYE), tree_top), ((0.0, 124.0, P + L.EYE), keep_top),
                   ((L.MINE_C[0], L.MINE_C[1], P + L.EYE), fall), ((L.MINE_C[0], L.MINE_C[1], P + L.EYE), star),
                   ((0.0, 100.0, T1 + L.EYE), star), ((160.0, 180.0, T1 + L.EYE), ship),
                   ((L.EXIT_START[0] - 4.0, L.EXIT_START[1], T1 + L.EYE), gopm),
                   ((14.0, -170.0, 214.0), torii), ((14.0, -170.0, 214.0), gate), ((14.0, -170.0, 214.0), ship)):
        if p is not None:
            out.append((Vector(eye), p))
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        if o.type == "CAMERA" and ("_PH_" in o.name or "PlayerHeight" in o.name) and not o.name.startswith("CAM_OPVeg"):
            eye = o.matrix_world.translation.copy()
            fwd = -(o.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()
            out.append((eye, eye + fwd * 42.0))      # campo PROXIMO: arvore no fim da viela e ponto focal, nao bloqueio
            PH_EYES.append(eye)
    return out


PH_EYES = []                     # olhos das cameras de altura do jogador (copa nenhuma a menos de 6 deles)


def seg_point_dist(a, b, p):
    d = b - a
    t = max(0.0, min(1.0, (p - a).dot(d) / max(1e-9, d.length_squared)))
    return (a + d * t - p).length


def blocks_view(views, spheres):
    for e, t in views:
        for c, r in spheres:
            if seg_point_dist(e, t, c) < r + 1.0:
                return True
    return False


# ================================================================== primitivas organicas (V2: SUAVES, das do op_tree)
def cushion(mb, c, rx, ry, h, m, rng, n=7, rot=0.0, jit=0.12, prof=None):
    """V2: almofada SUAVE de borda lobada (op_tree.cloud_pad, perfil baixo), 1 material; c = centro do FUNDO.
    (V1 era um poliedro facetado de n lados: reprovado como 'esferas facetadas'). Tris = 12 n"""
    c = Vector(c)
    TR.cloud_pad(mb, c + ZZ * h * 0.14, rx, h * 0.86, rot, 1.0, lobes=max(5, n - 1), seed=int(rng.random() * 1e6),
                 nt=2 * n, prof=TR.PAD_LO, mats=(m, m, m), depth=0.14, lumps=1, ry=ry)


def tube(mb, pts, radii, m=BARK, n=6, caps=True):
    """galho/tronco SUAVE (op_tree.limb, sem subdividir): sombreado continuo, sem faceta de prisma"""
    TR.limb(mb, [Vector(p) for p in pts], radii, m, n=n, sub=1, caps=caps)


# cerejeiras: 3 tons (Light no topo dos cachos, Blossom no corpo, Deep no vinco/baixo); o Light so nos setores da
# cidade/entrada/castelo (1 material a menos por setor nos outros = MeshParts)
LIGHT_SECTORS = ("Entrada", "Sudoeste", "Oeste", "Leste", "Castelo")
GREEN = (LEAF, LEAF, PINE)                       # copa verde: cachos Leaf_OP, nucleo/baixo verde-pinho
PINE_PAD = (LEAF, PINE, PINE)                    # almofada de kuromatsu: topo Leaf_OP, lado/baixo verde-pinho
# resolucao de cada CACHO por LOD (nu, nv) e cachos por parte da copa (principal, anel) por tamanho
PUFF_LOD = {2: (12, 6), 1: (9, 5), 0: (7, 4)}
CHERRY_BLOBS = {"XS": (3, 1), "S": (4, 1), "M": (5, 2), "L": (6, 2)}       # (V2, antigo blob_crown: arvore larga)
# V2b (2a volta do lead: a copa V2 lia como 5-6 bolhas grandes de face dura): COPA FOFA = op_tree.fluffy_crown, cachos
# medios (B) e sub-cachos (C) por parte: (principal B, principal C), (anel B, anel C) por tamanho
CHERRY_FLUFF = {"XS": ((4, 3), (2, 1)), "S": ((5, 4), (2, 2)), "M": ((6, 5), (3, 2)), "L": ((7, 6), (3, 2))}


def _pink(mb):
    nm = mb.name[len("OP_Veg_"):]
    return ("Flower_OP_Light" if nm in LIGHT_SECTORS else "Flower_OP_Blossom", "Flower_OP_Blossom", "Flower_OP_Deep")


def _seed(rng):
    return int(rng.random() * 1e7)


# ================================================================== FAMILIAS V2
# cada familia: PLANO (esferas da copa para as regras, ANTES de gerar) + GERADOR
CHERRY_SIZES = {"XS": (8.5, 4.8, 2, 0.45), "S": (11.0, 7.0, 3, 0.55), "M": (14.0, 9.5, 3, 0.7), "L": (18.0, 12.0, 4, 0.9)}   # h, R, cachos do anel, r0


def cherry_plan(x, y, z, size, lean_az, rng):
    """SAKURA de Wano (ref_03): tronco escuro baixo que abre em bracos; copa LARGA e FOFA = cacho principal no alto +
    anel de cachos nas pontas dos bracos + 1-2 cachos pequenos caidos na borda (o 'chorao' da cerejeira)"""
    h, R, nl, r0 = CHERRY_SIZES[size]
    d = vdir(lean_az)
    base = Vector((x, y, z))
    F = base + d * R * 0.15 + ZZ * h * 0.4
    a0 = lean_az + rng.uniform(-0.6, 0.6)
    main = (F + d * R * 0.06 + ZZ * h * 0.34, (R * 0.66, R * 0.62, R * 0.5))
    ring = []
    for k in range(nl):
        a = a0 + TAU * k / nl + rng.uniform(-0.3, 0.3)
        f = rng.uniform(0.86, 1.08)
        ring.append((a, F + vdir(a) * R * rng.uniform(0.5, 0.6) + ZZ * h * rng.uniform(0.17, 0.28),
                     (R * 0.5 * f, R * 0.47 * f, R * 0.4 * f)))
    small = []
    ns = 2 if size in ("M", "L") else 1
    for k in range(ns):
        a = a0 + TAU * (k + 0.5) / nl + rng.uniform(-0.25, 0.25)
        small.append((a, F + vdir(a) * R * 0.8 + ZZ * h * rng.uniform(-0.02, 0.08), (R * 0.32, R * 0.3, R * 0.27)))
    sph = [(main[0], max(main[1]))] + [(c, max(rr)) for a, c, rr in ring + small]
    return dict(h=h, R=R, r0=r0, base=base, F=F, main=main, ring=ring, small=small, d=d, spheres=sph, nl=nl, size=size,
                tips=[(a, c, max(rr)) for a, c, rr in ring])


def cherry(mb, pl, rng, lod=1):
    """CEREJEIRA V2: tronco escuro em S com pe alargado, bracos que abrem; copa de CACHOS (op_tree.puff: casca com
    calombos = sub-cachos, vinco escuro entre eles) de tamanhos variados; faces escondidas entre cachos cortadas"""
    base, F, d, r0, h = pl["base"], pl["F"], pl["d"], pl["r0"], pl["h"]
    perp = Vector((-d.y, d.x, 0.0))
    s = 1.0 if rng.random() < 0.5 else -1.0
    lean = F - base
    n = 7 if lod == 2 else (6 if lod else 5)
    tube(mb, [base - ZZ * 0.5, base + lean * 0.3 + perp * 0.35 * s + ZZ * 0.3, base + lean * 0.68 - perp * 0.4 * s, F],
         [r0 * 1.3, r0 * 1.04, r0 * 0.9, r0 * 0.76], n=n)
    tube(mb, [base - ZZ * 0.6, base + ZZ * 0.25, base + ZZ * 1.1], [r0 * 2.0, r0 * 1.55, r0 * 1.18], n=n, caps=False)
    for a, c, rr in pl["ring"]:
        v = c - F
        mid = F + Vector((v.x, v.y, 0.0)) * 0.5 + ZZ * v.z * 0.35
        tube(mb, [F - vdir(a) * r0 * 0.3, mid, c - ZZ * rr[2] * 0.2], [r0 * 0.62, r0 * 0.44, r0 * 0.28],
             n=5 if lod == 2 else 4)
    (mb_, mc_), (rb_, rc_) = CHERRY_FLUFF[pl["size"]]
    c, rr = pl["main"]
    parts = [(c, rr, mb_, mc_)]
    parts += [(c2, rr2, rb_, rc_) for a, c2, rr2 in pl["ring"]]
    TR.fluffy_crown(mb, parts, _seed(rng), lod, _pink(mb))


def pine_plan(x, y, z, h, lean_az, rng, lod=1):
    d = vdir(lean_az)
    sv = Vector((-d.y, d.x, 0.0))
    b0 = Vector((x, y, z))
    s = h / 12.0
    pts = [b0 - ZZ * 0.5, b0 + d * 0.6 * s + ZZ * h * 0.22, b0 + d * 2.3 * s + sv * 0.8 * s + ZZ * h * 0.45,
           b0 + d * 3.2 * s - sv * 0.4 * s + ZZ * h * 0.68, b0 + d * 2.5 * s + ZZ * h * 0.88]
    pads = []
    tiers = ((0.36, 2.9, 5.0, 2.9), (0.52, 0.5, 4.6, 2.7), (0.66, 4.2, 4.1, 2.4), (0.8, 1.8, 3.3, 2.0))
    for k, (t, ang, ln, rr) in enumerate(tiers if lod else tiers[:3]):
        a = lean_az + ang + rng.uniform(-0.3, 0.3)
        seg = min(3, int(t * 4))
        bp = pts[seg].lerp(pts[seg + 1], t * 4 - seg)
        tip = bp + vdir(a) * ln * s + ZZ * 0.5 * s
        pads.append((bp, tip, rr * s, a))
    sph = [(tip + ZZ * 0.5 * s, rr * 1.55) for bp, tip, rr, a in pads] + [(pts[-1] + ZZ * 0.7 * s, 2.5 * s)]
    return dict(pts=pts, pads=pads, s=s, d=d, spheres=sph, base=b0, R=4.8 * s)


def pine(mb, pl, rng, lod=1):
    """KUROMATSU V2: tronco escuro em S que se debruca, galhos quase horizontais e ALMOFADAS EM NUVEM (disco lobado
    suave, topo verde claro, lado/baixo verde-pinho) - a mesma linguagem da arvore monumental, em pequeno"""
    pts, s = pl["pts"], pl["s"]
    n = 6 if lod else 5
    tube(mb, pts, [0.85 * s, 0.68 * s, 0.52 * s, 0.38 * s, 0.26 * s], n=n)
    tube(mb, [pts[0], pts[0] + ZZ * 0.5 * s, pts[0] + ZZ * 1.3 * s], [1.5 * s, 1.15 * s, 0.86 * s], n=n, caps=False)
    nt, prof = (22, TR.PAD_MID) if lod else (16, TR.PAD_LO)
    for i, (bp, tip, rr, a) in enumerate(pl["pads"]):
        mid = bp.lerp(tip, 0.55) + ZZ * 0.25 * s
        tube(mb, [bp, mid, tip], [0.32 * s, 0.24 * s, 0.16 * s], n=4)
        TR.cloud_pad(mb, tip - ZZ * 0.15 * s, rr * 1.5, rr * 0.62, a, 1.2, lobes=7, seed=_seed(rng), nt=nt, prof=prof,
                     mats=PINE_PAD, depth=0.16, lumps=2)
    t = pts[-1]
    TR.cloud_pad(mb, t - ZZ * 0.1 * s, 2.5 * s, 1.5 * s, math.atan2(pl["d"].y, pl["d"].x), 1.15, lobes=7,
                 seed=_seed(rng), nt=nt, prof=prof, mats=PINE_PAD, depth=0.16, lumps=2)


def broad_plan(x, y, z, h, R, rng, lod=0):
    b0 = Vector((x, y, z))
    lean = vdir(rng.uniform(0, TAU)) * rng.uniform(0.2, 0.8)
    C0 = b0 + lean + ZZ * h * 0.62
    sats = []
    a0 = rng.uniform(0, TAU)
    ns = 3 if lod else 2
    for k in range(ns):
        a = a0 + TAU * k / ns + rng.uniform(-0.4, 0.4)
        sats.append((C0 + vdir(a) * R * rng.uniform(0.55, 0.68) - ZZ * h * rng.uniform(0.06, 0.16),
                     R * rng.uniform(0.5, 0.6), a))
    sph = [(C0, R * 0.95)] + [(c, r) for c, r, a in sats]
    return dict(base=b0, C0=C0, h=h, R=R, sats=sats, spheres=sph, lean=lean)


def broad(mb, pl, rng, lod=0):
    """ARVORE VERDE LARGA V2: tronco curto; copa = cacho principal + 2-3 cachos menores (sub-volumes com vinco
    verde-pinho entre eles), nao esfera"""
    b0, C0, h, R = pl["base"], pl["C0"], pl["h"], pl["R"]
    r0 = 0.3 + R * 0.075
    tube(mb, [b0 - ZZ * 0.5, b0 + pl["lean"] * 0.3 + ZZ * h * 0.3, C0 - ZZ * R * 0.3], [r0 * 1.3, r0, r0 * 0.6], n=5)
    parts = [(C0, (R * 0.92, R * 0.86, R * 0.74), 6 if lod else 5)]
    parts += [(c, (r * 0.9, r * 0.84, r * 0.72), 2) for c, r, a in pl["sats"]]
    TR.blob_crown(mb, parts, _seed(rng), PUFF_LOD[1 if lod else 0], GREEN)


def bush(mb, x, y, z, r, rng, lumps=2, m=LEAF, n=6):
    """MOITA PODADA (karikomi) V2b: 1-3 montes arredondados achatados embaixo, cada um uma COPA FOFA pequena
    (op_tree.fluffy_crown: nucleo verde-pinho + cachos lisos de baixa resolucao, sombreado suave)"""
    a0 = rng.uniform(0, TAU)
    parts = []
    for k in range(lumps):
        q = Vector((x, y, z)) + (vdir(a0 + 2.3 * k) * r * rng.uniform(0.6, 0.85) if k else Vector())
        rr = r * (1.0 if k == 0 else rng.uniform(0.6, 0.78))
        parts.append((q + ZZ * rr * 0.42, (rr * 1.1, rr, rr * 0.62), 5 if k == 0 else 3, 0))
    TR.fluffy_crown(mb, parts, _seed(rng), 0, (m, m, PINE) if m != PINE else (PINE, PINE, PINE))


def tris_of(mb):
    return sum(len(f.verts) - 2 for f in mb.bm.faces)


# ================================================================== objetos por SETOR (MeshParts sem fatiar)
# O export faz 1 MeshPart por (objeto, material) e FATIA em celulas de 128 a peca que tem >= 1500 tris E mais de 160
# studs. Aqui: 9 setores; a peca de um setor que passa de 158 studs fica abaixo de CAP tris por material (nunca fatia);
# se a planta estoura o CAP do setor dela, vai para o setor vizinho com folga (mais perto primeiro).
# Teto: 9 setores x 5 materiais (Flower_OP_Deep so nas cerejeiras-heroi da entrada) = 46 <= 49.
SECTORS = [  # (nome, x0, y0, x1, y1) - o primeiro que contem o pe manda
    ("Entrada", -60.0, -40.0, 100.0, 72.0),
    ("Sudoeste", -270.0, -40.0, -60.0, 140.0),
    ("Oeste", -270.0, 140.0, -96.0, 300.0),
    ("TerracoAlto", -270.0, 300.0, -96.0, 520.0),
    ("Castelo", -96.0, 300.0, 70.0, 520.0),
    ("Fundo", 70.0, 330.0, 240.0, 455.0),
    ("FundoNorte", 70.0, 455.0, 340.0, 640.0),
    ("Leste", 60.0, -40.0, 252.0, 330.0),
    ("Promontorio", 252.0, 130.0, 380.0, 400.0),
]
CAP = 1450
COMPACT = 158.0
_SEC = {}


class Sec:
    def __init__(self, nm, rect):
        self.nm = nm
        self.rect = rect
        self.c = ((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2)
        self.mb = MB("OP_Veg_" + nm, C, random.Random(int(hh("sec", nm) * 1e6)), detail="far", floor=-999)
        # marca de elemento ja aceito (o bmesh reaproveita a memoria do que foi desfeito: a ordem nao separa o novo)
        self.lv = self.mb.bm.verts.layers.int.new("veg_ok")
        self.lf = self.mb.bm.faces.layers.int.new("veg_ok")
        self.cnt = {}
        self.bb = None

    def finish(self):
        bm = self.mb.bm
        bm.verts.layers.int.remove(self.lv)
        bm.faces.layers.int.remove(self.lf)
        return self.mb.finish()


def _sec(nm):
    if nm not in _SEC:
        rect = [r[1:] for r in SECTORS if r[0] == nm][0]
        _SEC[nm] = Sec(nm, rect)
    return _SEC[nm]


def home_sector(x, y):
    for nm, x0, y0, x1, y1 in SECTORS:
        if x0 <= x < x1 and y0 <= y < y1:
            return nm
    return min(SECTORS, key=lambda r: math.hypot(x - (r[1] + r[3]) / 2, y - (r[2] + r[4]) / 2))[0]


_PROBE = [None]


def _hits_built(nv, nf, zroot):
    """a geometria nova atravessa o construido? (BVH malha contra malha) O enraizamento - face nova abaixo de
    zroot + 1,2 contra face de CHAO horizontal - nao conta"""
    P_ = _PROBE[0]
    if P_ is None or P_.built is None or not nf:
        return False
    idx = {v: i for i, v in enumerate(nv)}
    vs = [v.co.copy() for v in nv]
    fs = [[idx[v] for v in f.verts] for f in nf]
    t = BVHTree.FromPolygons(vs, fs)
    for i, j in t.overlap(P_.built):
        if zroot is not None and P_.bnz[j] > 0.9 and min(vs[k].z for k in fs[i]) < zroot + 1.2:
            continue
        return True
    return False


def add_item(x, y, ext, gen, zroot=None):
    """gera a planta (gen(mb), com rng proprio: repetivel) no setor dela; se ATRAVESSA o construido (teste exato,
    malha contra malha; o pe enraizado no chao vale), desfaz e nao nasce; se estoura o CAP de um material num setor
    largo, desfaz e tenta o vizinho. Devolve os tris ou None"""
    home = home_sector(x, y)
    order = [home] + sorted((r[0] for r in SECTORS if r[0] != home),
                            key=lambda n: math.hypot(x - (_sec(n).c[0]), y - (_sec(n).c[1])))[:3]
    for nm in order:
        sc = _sec(nm)
        bm = sc.mb.bm
        gen(sc.mb)
        nv = [v for v in bm.verts if not v[sc.lv]]
        nf = [f for f in bm.faces if not f[sc.lf]]
        if _hits_built(nv, nf, zroot):
            bmesh.ops.delete(bm, geom=nv, context="VERTS")
            STATS["intersecao"] = STATS.get("intersecao", 0) + 1
            return None
        add = {}
        for f in nf:
            k = sc.mb.mats[f.material_index]
            k = k[1] if isinstance(k, tuple) else k
            add[k] = add.get(k, 0) + len(f.verts) - 2
        bb = (x - ext, y - ext, x + ext, y + ext)
        nb = bb if sc.bb is None else (min(sc.bb[0], bb[0]), min(sc.bb[1], bb[1]), max(sc.bb[2], bb[2]),
                                       max(sc.bb[3], bb[3]))
        compact = nb[2] - nb[0] <= COMPACT and nb[3] - nb[1] <= COMPACT
        if compact or all(sc.cnt.get(m, 0) + t < CAP for m, t in add.items()):
            for m, t in add.items():
                sc.cnt[m] = sc.cnt.get(m, 0) + t
            sc.bb = nb
            for v in nv:
                v[sc.lv] = 1
            for f in nf:
                f[sc.lf] = 1
            return sum(add.values())
        bmesh.ops.delete(bm, geom=nv, context="VERTS")
    STATS["sem_espaco"] = STATS.get("sem_espaco", 0) + 1
    return None


# ================================================================== colocacao com regras
NUDGE = [(0.0, 0.0)] + [(math.cos(TAU * k / 8) * d, math.sin(TAU * k / 8) * d) for d in (2.5, 4.5, 7.0) for k in range(8)]
SPACING = {"cherry": 0.8, "pine": 0.6, "broad": 0.56, "bush": 0.5}


class Placer:
    def __init__(self, probe, views):
        self.P = probe
        self.V = views
        self.placed = []          # (x, y, R, familia)
        self.tris = 0
        self.ncol = 0
        self.rej = {}
        self.last = {}

    def _rej(self, why):
        self.rej[why] = self.rej.get(why, 0) + 1
        self.last[why] = self.last.get(why, 0) + 1
        return None

    def ground(self, x, y, r, flat_r, rock=False):
        t = self.P.top(x, y)
        if not self.P.natural(t, rock):
            return self._rej("chao")
        if t[3] < 0.6:
            return self._rej("inclinado")
        for k in range(6):
            a = TAU * k / 6
            q = self.P.top(x + math.cos(a) * flat_r, y + math.sin(a) * flat_r)
            if q is None or abs(q[0] - t[0]) > 1.6:
                return self._rej("beira")
        return t[0]

    def spacing_ok(self, x, y, R, fam):
        k = SPACING[fam]
        for px, py, pR, pf in self.placed:
            kk = max(k, SPACING[pf])
            if (x - px) ** 2 + (y - py) ** 2 < ((R + pR) * kk) ** 2:
                return False
        return True

    def crown_ok(self, sph, strict_built=True):
        if strict_built and any(not self.P.clear_of_built(c, rr * 0.9) for c, rr in sph):
            return self._rej("copa x construido")
        if any(in_mine(c.x, c.y, rr + 2.0) and c.z - rr < P + L.CLEAR_H + 0.5 for c, rr in sph):
            return self._rej("copa x zona")
        for pts, w, z in L.STREETS:                         # copa nao cobre a rua (fachadas e respiro)
            for c, rr in sph:
                if abs(c.z - z) < 30.0 and L.polyline_dist(c.x, c.y, pts) < w / 2 + rr * 0.55:
                    return self._rej("copa x rua")
        for pts, hw in BRIDGES:
            for c, rr in sph:
                if L.polyline_dist(c.x, c.y, pts) < hw + rr * 0.8:
                    return self._rej("copa x ponte")
        if blocks_view(self.V, sph):
            return self._rej("visada")
        for e in PH_EYES:
            for c, rr in sph:
                if (c - e).length < rr + 6.0:
                    return self._rej("olho de camera")
        return True

    def try_site(self, fam, x, y, r, R, plan_fn, nudge=True, flat_r=None, check_route=True, route_gap=3.0,
                 strict_built=True, rock=False):
        """procura um pe valido perto de (x, y): devolve (plano, x, y, z) ou None"""
        self.last = {}
        for dx, dy in (NUDGE if nudge else NUDGE[:1]):
            xx, yy = x + dx, y + dy
            why = plan_reject(xx, yy, r, R)
            if why:
                self._rej(why)
                continue
            if check_route and self.P.route_dist(xx, yy) < route_gap + r:
                self._rej("rota")
                continue
            if not self.spacing_ok(xx, yy, R, fam):
                self._rej("vizinha")
                continue
            z = self.ground(xx, yy, r, flat_r if flat_r is not None else r + 1.2, rock)
            if z is None:
                continue
            if not self.P.clear_of_built((xx, yy, z + r + 2.0), r + 1.5):
                self._rej("construido")
                continue
            pl = plan_fn(xx, yy, z)
            if self.crown_ok(pl["spheres"], strict_built) is None:
                continue
            return pl, xx, yy, z
        return None

    def commit(self, fam, x, y, z, r, R, collide=True):
        self.placed.append((x, y, R, fam))
        TRUNKS.append((x, y, z, r, R, fam))
        zf = L.zone_of(x, y)
        if collide and zf is not None and abs(zf - z) < 1.5 and self.P.route_dist(x, y) < 40.0:
            col_box("OP_VegTrunk", (2.0 * r + 0.4, 2.0 * r + 0.4, 7.0), (x, y, z + 3.5))
            self.ncol += 1


def _fail(pc, fam, x, y, note):
    STATS.setdefault("falhou", []).append((fam, x, y, note, dict(sorted(pc.last.items(), key=lambda a: -a[1])[:3])))


def place_cherry(pc, x, y, size, note, lean=None, lod=1, nudge=True, rock=False, quiet=False):
    h, R, nl, r0 = CHERRY_SIZES[size]
    rng = rng_at("cherry", x, y)
    la = math.radians(lean) if lean is not None else rng.uniform(0, TAU)

    def fn(xx, yy, z):
        return cherry_plan(xx, yy, z, size, la, rng_at("cplan", x, y))
    r = pc.try_site("cherry", x, y, r0 * 1.6, R, fn, nudge=nudge, rock=rock)
    if r is None:
        if not quiet:
            _fail(pc, "cerejeira", x, y, note)
        return False
    pl, xx, yy, z = r
    t = add_item(xx, yy, R + 2.0, lambda mb: cherry(mb, pl, rng_at("cgen", x, y), lod), zroot=z)
    if t is None:
        if not quiet:
            pc.last = {"atravessaria o construido / setor cheio": 1}
            _fail(pc, "cerejeira", x, y, note)
        return False
    pc.tris += t
    pc.commit("cherry", xx, yy, z, r0 * 1.3, R)
    STATS["cherry"] = STATS.get("cherry", 0) + 1
    return True


def place_pine(pc, x, y, h, note, lean=None, lod=1, nudge=True, rock=True, quiet=False):
    rng = rng_at("pine", x, y)
    la = math.radians(lean) if lean is not None else rng.uniform(0, TAU)

    def fn(xx, yy, z):
        return pine_plan(xx, yy, z, h, la, rng_at("pplan", x, y), lod)
    s = h / 12.0
    r = pc.try_site("pine", x, y, 0.85 * s, 4.6 * s, fn, nudge=nudge, rock=rock)
    if r is None:
        if not quiet:
            _fail(pc, "pinheiro", x, y, note)
        return False
    pl, xx, yy, z = r
    t = add_item(xx, yy, 7.0 * s, lambda mb: pine(mb, pl, rng_at("pgen", x, y), lod), zroot=z)
    if t is None:
        if not quiet:
            pc.last = {"atravessaria o construido / setor cheio": 1}
            _fail(pc, "pinheiro", x, y, note)
        return False
    pc.tris += t
    pc.commit("pine", xx, yy, z, 0.85 * s, 4.6 * s)
    STATS["pine"] = STATS.get("pine", 0) + 1
    return True


def place_broad(pc, x, y, h, R, lod=0, nudge=True):
    def fn(xx, yy, z):
        return broad_plan(xx, yy, z, h, R, rng_at("bplan", x, y), lod)
    r = pc.try_site("broad", x, y, 0.3 + R * 0.1, R, fn, nudge=nudge)
    if r is None:
        return False
    pl, xx, yy, z = r
    t = add_item(xx, yy, R * 1.5, lambda mb: broad(mb, pl, rng_at("bgen", x, y), lod), zroot=z)
    if t is None:
        return False
    pc.tris += t
    pc.commit("broad", xx, yy, z, 0.3 + R * 0.075, R)
    STATS["broad"] = STATS.get("broad", 0) + 1
    return True


def place_bush(pc, x, y, r, nudge=False, lumps=2, route_gap=2.5, rock=False):
    rng = rng_at("bush", x, y)
    for dx, dy in (NUDGE[:9] if nudge else NUDGE[:1]):
        xx, yy = x + dx, y + dy
        if plan_reject(xx, yy, 0.5, r):
            continue
        if pc.P.route_dist(xx, yy) < route_gap + r:
            continue
        if not pc.spacing_ok(xx, yy, r, "bush"):
            continue
        t = pc.P.top(xx, yy)
        if not pc.P.natural(t, rock) or t[3] < 0.6:
            continue
        z = t[0]
        if not pc.P.clear_of_built((xx, yy, z + r * 0.7 + 0.4), r * 0.8):
            continue
        sph = [(Vector((xx, yy, z + r * 0.5)), r * 1.1)]
        if blocks_view(pc.V, sph):
            continue
        t = add_item(xx, yy, r * 2.0, lambda mb: bush(mb, xx, yy, z, r, rng_at("bush", x, y), lumps=lumps), zroot=z)
        if t is None:
            return False
        pc.tris += t
        pc.placed.append((xx, yy, r, "bush"))
        STATS["bush"] = STATS.get("bush", 0) + 1
        return True
    return False


# ================================================================== LISTAS DIRIGIDAS
# cerejeiras de ENQUADRAMENTO (x, y, tamanho, lean graus ou None, lod, nota)
HERO_CHERRIES = [
    (-38.0, 16.0, "L", 200.0, 2, "ombro oeste do grande torii (moldura da chegada)"),
    (40.0, 18.0, "L", -20.0, 2, "ombro leste do grande torii"),
    (-106.0, 130.0, "M", 210.0, 2, "canto SO da praca, por fora do piso (moldura de quem sobe a escadaria)"),
    (-88.0, 374.0, "M", 180.0, 1, "rocha oeste do castelo: moldura do rochedo vista da praca"),
    (88.0, 370.0, "L", 0.0, 1, "rocha leste do castelo, perto da base da arvore (eco da copa monumental)"),
    (298.0, 292.0, "M", 60.0, 1, "promontorio da saida (laje, lanternas, cerejeira)"),
    (100.0, 26.0, "M", None, 0, "rocha da frente leste, sobre a enseada (concept: rosa na borda direita)"),
    (-70.0, 30.0, "M", None, 0, "borda sul do bairro do canal (concept: rosa na frente esquerda)"),
    (-104.0, 334.0, "M", 150.0, 2, "canto NO da praca, pe do terraco alto"),
    (108.0, 306.0, "S", 30.0, 1, "canto NE da praca, entrada do santuario"),
    (126.0, 178.0, "S", None, 0, "gramado sul do terraco do summon"),
    (128.0, 420.0, "M", None, 0, "bosque do fundo leste"),
    (-176.0, 420.0, "M", None, 0, "terraco alto, jardim do fundo das mansoes"),
    (-178.0, 350.0, "S", None, 0, "terraco alto, jardim entre a U1 e a U4"),
    (-212.0, 120.0, "S", None, 0, "canto SO alem do canal"),
    (170.0, 22.0, "S", None, 0, "borda sul do porto alto"),
    (-226.0, 392.0, "S", None, 0, "pe do pinaculo do pagode"),
    (172.0, 470.0, "S", None, 0, "fundo leste, borda (rosa no fundo da concept)"),
]
# pinheiros-marco (x, y, h, lean graus ou None, nota): pontas de rocha, debrucados para fora (rocha nua vale);
# lod 1 (nuvem clara em cima, mais lados) so onde a camera do jogador chega perto
HERO_PINES = [
    (-46.0, 26.0, 12.0, 160.0, "nariz oeste da entrada"),
    (52.0, 30.0, 11.0, 20.0, "nariz leste da entrada"),
    (-58.0, 356.0, 11.0, 200.0, "contraforte oeste do castelo"),
    (60.0, 352.0, 10.0, -20.0, "contraforte leste do castelo"),
    (-208.0, 320.0, 12.0, 180.0, "borda oeste do terraco alto"),
    (-214.0, 181.0, 11.0, 180.0, "alem do canal, borda oeste"),
    (-196.0, 96.0, 12.0, 200.0, "lobo SO"),
    (262.0, 350.0, 13.0, 30.0, "rochas NE sobre a queda leste"),
    (282.0, 330.0, 12.0, 60.0, "rochas NE, ponta"),
    (-90.0, 440.0, 14.0, 160.0, "fundo oeste do castelo"),
    (-20.0, 486.0, 16.0, 100.0, "fundo norte"),
    (40.0, 484.0, 15.0, 80.0, "fundo norte"),
    (325.0, 236.0, 11.0, -40.0, "promontorio, borda sul (sobre a caveira)"),
    (210.0, 19.0, 12.0, -60.0, "ponta SE do cais (M6b item 48: o canto do cais respira, so 1 pinheiro na ponta)"),
    (215.0, 505.0, 12.0, 60.0, "raiz do esporao"),
    (280.0, 588.0, 10.0, 30.0, "esporao, pe da espada"),
]
# bosque: (nome, poligono, passo, chance, h, R, chance de pinheiro)
_SKULL_N = [(288.0, 238.0), (352.0, 210.0), (358.0, 300.0), (306.0, 330.0), (286.0, 300.0)]
FOREST = [
    ("BackE", None, 14.0, 0.7, 16.0, 9.0, 0.25),
    ("BackN", None, 13.0, 0.65, 14.0, 8.0, 0.3),
    ("NERocksE", None, 12.0, 0.6, 13.0, 7.5, 0.3),
    ("NERocksW", None, 12.0, 0.45, 12.0, 7.0, 0.25),
    ("BackW", None, 12.0, 0.55, 13.0, 7.5, 0.3),
    ("CastleFootE", None, 11.0, 0.45, 11.0, 6.0, 0.35),
    ("PromontorioN", _SKULL_N, 12.0, 0.5, 13.0, 7.5, 0.3),
    ("TerracoAlto", L.W3_POLY, 14.0, 0.3, 12.0, 7.0, 0.2),
    ("AlemCanal", L.W2B, 13.0, 0.3, 11.0, 6.5, 0.25),
]


SUMMON_KO = (110.0, 144.0, 212.0, 270.0)      # terraco do summon: o jardim e do op_summon (pinheiros, canteiros)


# M6b (pedido do grupo B / item 25 da auditoria): 2 KUROMATSU no CASCALHO do patio do castelo (cota 136,2), em par
# dos 2 lados do eixo porta -> mirante, entre o mirante e a faixa de lajes da torre (fora das lajes, do eixo, da rota
# do salao e do TREE_KEEPOUT); debrucados para fora do eixo (moldura da porta vista do mirante)
COURT_PINES = [(-25.0, 362.5, 13.0, 180.0, "patio do castelo, cascalho oeste do eixo"),
               (25.0, 362.5, 13.0, 0.0, "patio do castelo, cascalho leste do eixo")]


def court_pines(pc):
    """pinheiros no cascalho (Stone_OP_Court do op_castle): o chao 'natural' da regra geral nao vale aqui"""
    kx, ky = L.KEEP_C
    tb = math.tan(math.radians(20.0))                      # pe da base da torre em talude (= op_castle.court_floor)
    hx, hy = L.KEEP_TIERS[0][0] + 0.8 + 4.7 * tb, L.KEEP_TIERS[0][1] + 0.8 + 4.7 * tb
    band = (kx - hx - 9.0, ky - hy - 9.0, kx + hx + 9.0, ky + hy + 9.0)        # faixa de lajes + borda + 0,5
    n = 0
    for x, y, h, lean, note in COURT_PINES:
        rng = rng_at("cpine", x, y)
        s_ = h / 12.0
        r = 0.85 * s_
        done = False
        for dx, dy in NUDGE[:17]:
            xx, yy = x + dx, y + dy
            if band[0] < xx < band[2] and band[1] < yy < band[3]:
                continue
            if abs(xx) < 4.5 + 2.0 + r or plan_reject(xx, yy, r, 4.6 * s_):
                continue
            if pc.P.route_dist(xx, yy) < 3.0 + r:
                continue
            t = pc.P.top(xx, yy)
            if t is None or not t[1].startswith("OP_Cas_") or not t[2].startswith("Stone_OP_Court") or t[3] < 0.9:
                continue
            if abs(t[0] - (L.CC + 0.14)) > 0.6:
                continue
            z = t[0]
            pl = pine_plan(xx, yy, z, h, math.radians(lean), rng_at("cpplan", x, y), 1)
            if pc.crown_ok(pl["spheres"]) is None:
                continue
            tt = add_item(xx, yy, 7.0 * s_, lambda mb: pine(mb, pl, rng_at("cpgen", x, y), 1), zroot=z)
            if tt is None:
                continue
            pc.tris += tt
            pc.commit("pine", xx, yy, z, r, 4.6 * s_)
            STATS["pine"] = STATS.get("pine", 0) + 1
            STATS.setdefault("patio_xy", []).append((round(xx, 1), round(yy, 1), round(z, 2)))
            n += 1
            done = True
            break
        if not done:
            print("op_veg: AVISO pinheiro do patio nao nasceu (%.0f, %.0f) %s" % (x, y, note))
    return n


def city_yards(pc, budget, step=8.5):
    """QUINTAIS e gramados DENTRO da cidade (longe da borda): a concept pontua a capital com copas entre os telhados -
    cerejeira pequena (rosa, 45%) ou arvore verde pequena; so onde a copa cabe sem tocar beiral/fachada nem cobrir rua
    (as mesmas regras de tudo) - quintal apertado fica sem arvore"""
    n = 0
    rim = ccw_rim()
    for nm in ("T1", "Plaza", "W2b", "W3"):
        poly = L.floor_poly(nm)
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        y = min(ys) + step * 0.5
        while y < max(ys):
            x = min(xs) + step * 0.5
            while x < max(xs):
                jx = (hh("cy", nm, x, y, "x") - 0.5) * step * 0.7
                jy = (hh("cy", nm, x, y, "y") - 0.5) * step * 0.7
                xx, yy = x + jx, y + jy
                if pc.tris > budget:
                    return n
                sx0, sy0, sx1, sy1 = SUMMON_KO
                if L.point_in_poly(xx, yy, poly) and L.poly_edge_dist(xx, yy, rim) > 24.0 \
                        and not (sx0 < xx < sx1 and sy0 < yy < sy1) and hh("cy", nm, x, y, "p") < 0.6:
                    if hh("cy", nm, x, y, "k") < 0.85:          # V2: a cidade da ref_03 e ROSA entre os telhados
                        ok = place_cherry(pc, xx, yy, "M", "quintal", lod=0, nudge=False, quiet=True) or                             place_cherry(pc, xx, yy, "S", "quintal", lod=0, nudge=False, quiet=True) or                             place_cherry(pc, xx, yy, "XS", "quintal", lod=0, nudge=False, quiet=True)
                    else:
                        s_ = 0.8 + 0.35 * hh("cy", nm, x, y, "s")
                        ok = place_broad(pc, xx, yy, 10.0 * s_, 5.2 * s_, lod=0, nudge=False)
                    n += ok
                x += step
            y += step
    return n


def _rock_poly(nm):
    for n, pts, z in L.ROCKS:
        if n == nm:
            return pts
    return None


_RIM = []


def ccw_rim():
    if not _RIM:
        _RIM.append(DL.ccw(L.ISLAND_RIM))
    return _RIM[0]


def forest(pc, budget):
    n = 0
    rim = ccw_rim()
    for nm, poly, step, ch, h, R, pch in FOREST:
        poly = poly or _rock_poly(nm)
        if not poly:
            continue
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        y = min(ys) + step * 0.5
        row = 0
        while y < max(ys):
            x = min(xs) + step * (0.25 if row % 2 else 0.75)
            while x < max(xs):
                jx = (hh(nm, x, y, "jx") - 0.5) * step * 0.6
                jy = (hh(nm, x, y, "jy") - 0.5) * step * 0.6
                xx, yy = x + jx, y + jy
                if L.point_in_poly(xx, yy, poly):
                    edge = L.poly_edge_dist(xx, yy, rim)
                    dens = ch * (1.3 if edge < 18.0 else (1.0 if edge < 40.0 else 0.75))   # cresce para a borda
                    if hh(nm, x, y, "p") < dens:
                        if pc.tris > budget:
                            return n
                        s = 0.8 + 0.45 * hh(nm, x, y, "s") + (0.15 if edge < 18.0 else 0.0)
                        if hh(nm, x, y, "k") < pch:
                            ok = place_pine(pc, xx, yy, h * s, "bosque " + nm, lod=0, nudge=False, quiet=True)
                        else:
                            ok = place_broad(pc, xx, yy, h * s, R * s, lod=0, nudge=False)
                        n += ok
                x += step
            y += step
            row += 1
    return n


def rim_samples(step, inset):
    """pontos ao longo do contorno, 'inset' para DENTRO (poligono anti-horario: normal para fora = (dy, -dx))"""
    rim = ccw_rim()
    out = []
    n = len(rim)
    acc = 0.0
    nxt = 0.0
    for i in range(n):
        a, b = rim[i], rim[(i + 1) % n]
        ln = math.dist(a, b)
        if ln < 1e-6:
            continue
        dx, dy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
        nx, ny = dy, -dx
        t = nxt - acc
        while t < ln:
            x, y = a[0] + dx * t, a[1] + dy * t
            out.append((x - nx * inset, y - ny * inset, math.atan2(ny, nx), acc + t))
            t += step
        acc += ln
        nxt = acc + (t - ln)
    return out


# setores da borda SEM verde novo: nariz da entrada (torii livre), gargantas das quedas, cabeca da ponte de saida,
# ancora OPM; o cais (pedra aparelhada reta) tambem
RIM_SKIP = [((0.0, 0.0), 30.0), ((L.FALL_W[0], L.FALL_W[1]), 14.0), ((L.FALL_E[0], L.FALL_E[1]), 14.0),
            ((L.EXIT_START[0], L.EXIT_START[1]), 22.0), (L.exit_point(L.EXIT_BRIDGE_LEN), 22.0),
            (L.anchor_opm_pos(), 20.0)]


def rim_skip(x, y):
    if any(math.hypot(x - c[0], y - c[1]) < r for c, r in RIM_SKIP):
        return True
    return 118.0 <= x and y <= 268.0 and (y < 12.0 or x > 214.0)


def harbor_corner(x, y):
    """M6b (item 48): canto sul do cais (x 124..214, y < 34) sem a faixa de arvores largas da borda (eram 5 'brocolis'
    em fila fechando a vista do cais para o mar): fica a cerejeira-heroi (170, 22) + 1 pinheiro na ponta (HERO_PINES)"""
    return 124.0 <= x <= 214.0 and y < 34.0


def rim_band(pc, budget):
    """faixa da borda: 3 fileiras para dentro da crista; densidade por setor (ruido dirigido de baixa frequencia,
    massas e vazios ao longo do contorno) e maior na fileira de fora"""
    n = 0
    for row, (step, inset, base) in enumerate(((8.0, 5.5, 0.9), (10.0, 13.0, 0.65), (13.0, 21.0, 0.35))):
        for x, y, ang, d in rim_samples(step, inset):
            if pc.tris > budget:
                return n
            if rim_skip(x, y) or harbor_corner(x, y):
                continue
            sector = 0.5 + 0.5 * math.sin(d / 61.0 + 1.3) * math.cos(d / 23.0 + 0.4)
            dens = base * (0.6 + 0.6 * sector)
            key = (row, round(d, 1))
            if hh("rim", *key) > dens:
                continue
            k = hh("rimk", *key)
            s = 0.8 + 0.5 * hh("rims", *key) - 0.1 * row
            lean = math.degrees(ang) + (hh("riml", *key) - 0.5) * 50.0
            if k < 0.18:
                ok = place_pine(pc, x, y, 12.0 * s, "borda", lean=lean, lod=0, nudge=True, quiet=True)
            elif k < 0.46:                                   # V2: rosa tambem na borda (ref_03; concept: frente)
                ok = place_cherry(pc, x, y, "S" if s > 0.95 else "XS", "borda", lean=lean, lod=0, nudge=True,
                                  quiet=True)
            elif k < 0.82:
                ok = place_broad(pc, x, y, 13.0 * s, 8.5 * s, lod=0, nudge=True)
            else:
                ok = place_bush(pc, x, y, 2.4 * s, nudge=True, lumps=3)
            n += ok
    return n


def wall_feet(pc, budget, step=9.0):
    """moitas no PE dos muros/arrimos: 2,2 para fora de cada piso que tem desnivel >= 2,5 para o vizinho de baixo"""
    n = 0
    polys = [(nm, poly, L._zval(z, 0, 0)) for nm, poly, z, pr in L.floors() if nm not in ("ShipDeck", "Harbor")]
    polys += [(nm, pts, z) for nm, pts, z in L.ROCKS]
    for nm, poly, zt in polys:
        pp = DL.offset_poly(poly, 2.4)
        for i in range(len(pp)):
            a, b = pp[i], pp[(i + 1) % len(pp)]
            ln = math.dist(a, b)
            k = max(1, int(ln / step))
            for j in range(k):
                if pc.tris > budget:
                    return n
                t = (j + 0.5) / k
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                if hh("wf", nm, i, j) > 0.45:
                    continue
                g = pc.P.top(x, y)
                if g is None or zt - g[0] < 2.5 or zt - g[0] > 20.0:
                    continue
                r = 1.7 + 0.9 * hh("wfr", nm, i, j)
                ex, ey = b[0] - a[0], b[1] - a[1]
                el = math.hypot(ex, ey) or 1.0
                ox, oy = ey / el, -ex / el                 # para fora do piso (poligono anti-horario)
                if L.point_in_poly(x + ox * 0.5, y + oy * 0.5, poly):
                    ox, oy = -ox, -oy
                xx, yy = x + ox * (r * 0.9 - 1.4), y + oy * (r * 0.9 - 1.4)
                ok = place_bush(pc, xx, yy, r, nudge=False, lumps=2, route_gap=3.0)
                if ok:
                    STATS.setdefault("pe_muro_xy", []).append((round(xx), round(yy), round(g[0], 1)))
                n += ok
    return n


def _crest(pc, x, y, ang):
    """(z do topo, ponto da face 3 abaixo do labio, normal da face) na crista do contorno em (x, y); None se nao ha
    crista natural (cais, ponte, construido)"""
    o = vdir(ang)
    t = pc.P.top(x - o.x * 1.5, y - o.y * 1.5)
    if not pc.P.natural(t) or t[0] < L.SEA + 14.0:
        return None
    zt = t[0]
    h = pc.P.bvh.ray_cast(Vector((x + o.x * 14.0, y + o.y * 14.0, zt - 3.0)), -o, 30.0)
    if h[0] is None or not pc.P.own[h[2]].startswith("OP_Ter_") or abs(h[1].z) > 0.6:
        return None
    return zt, h[0], h[1]


def _anchor(pc, c, rn, half_n, hgt, waist=0.45, max_drop=3.0):
    """M6b (item 46): ANCORA uma almofada de face/crista. c = centro do FUNDO, rn = normal horizontal para FORA da
    face, half_n = meia largura da almofada na direcao rn, hgt = altura. (1) prateleira/ombro de rocha ate max_drop
    abaixo do fundo: desce ate enterrar 0,1 (nada de tufo pairando 1..3 acima do apoio); (2) a face na altura da cintura:
    encosta ate a almofada entrar >= 0,35 nela (tufo colado, nao pendurado no ar). Devolve o novo c"""
    c = Vector(c)
    rn = Vector((rn.x, rn.y, 0.0))
    if rn.length < 1e-6:
        return c
    rn.normalize()
    q = c - rn * min(half_n * 0.4, 1.2) + ZZ * 0.05
    h = pc.P.bvh.ray_cast(q, -ZZ, max_drop + 0.05)
    if h[0] is not None and pc.P.own[h[2]].startswith(("OP_Ter_", "OP_Lmk_")) and c.z - h[0].z > 0.1:
        c.z = h[0].z - 0.1
        STATS["ancora_desceu"] = STATS.get("ancora_desceu", 0) + 1
    zc = c.z + hgt * waist
    m = Vector((c.x, c.y, zc))
    h = pc.P.bvh.ray_cast(m + rn * (half_n + 3.0), -rn, half_n + 9.0)
    if h[0] is not None and pc.P.own[h[2]].startswith(("OP_Ter_", "OP_Lmk_")):
        d = (m - h[0]).dot(rn)
        want = half_n - 0.35
        if d > want:
            c -= rn * (d - want)
            STATS["ancora_encostou"] = STATS.get("ancora_encostou", 0) + 1
    return c


def cliff_greens(pc, budget, step=8.5):
    """o VERDE QUE ESCORRE da concept: na crista do contorno, (a) moita de beira (almofada no labio, meio para fora,
    + 1 almofada que desce colada na face) e (b) arvorezinha AGARRADA que se debruca para o vazio (tronco que sai
    inclinado, copa fora da face). Setores com ruido dirigido; nada nos setores protegidos"""
    n = 0
    for x, y, ang, d in rim_samples(step, 0.4):
        if pc.tris > budget:
            break
        key = round(d, 1)
        if rim_skip(x, y):
            continue
        sector = 0.5 + 0.5 * math.sin(d / 47.0 + 0.7) * math.cos(d / 19.0 + 2.1)
        if hh("cg", key) > 0.42 + 0.45 * sector:
            continue
        if plan_reject(x, y, 0.5, 3.0) in ("ponte", "torii", "escada", "agua", "zona", "praca"):
            continue
        cr = _crest(pc, x, y, ang)
        if cr is None:
            continue
        zt, fp, fn_ = cr
        o = vdir(ang)
        lip = Vector((x, y, zt))
        if not pc.P.clear_of_built(lip + ZZ * 2.0, 3.5):
            continue
        tree = hh("cgt", key) < 0.3 and zt - L.SEA > 24.0
        if tree:
            R = 4.6 + 2.4 * hh("cgr", key)
            base = lip - o * 1.2
            top = base + o * (2.8 + R * 0.5) + ZZ * (4.2 + R * 0.6)
            sph = [(top + ZZ * R * 0.25, R * 1.05)]
            if not pc.crown_ok(sph):
                continue
            rng_k = ("cgtree", key)

            def gen(mb):
                rng = rng_at(*rng_k)
                tube(mb, [base - ZZ * 0.6, base + o * 1.0 + ZZ * 1.8, base + o * 2.2 + ZZ * 3.4, top - ZZ * R * 0.3],
                     [0.55, 0.45, 0.34, 0.22], n=4)
                cushion(mb, top - ZZ * R * 0.4, R * 1.1, R * 0.9, R * 0.85, LEAF, rng, n=7, rot=ang)
                a2 = ang + (1.4 if rng.random() < 0.5 else -1.4)
                cushion(mb, top + vdir(a2) * R * 0.7 - ZZ * R * 0.55, R * 0.7, R * 0.6, R * 0.6, PINE, rng, n=6, rot=a2)
            t = add_item(x, y, R + 4.0, gen, zroot=zt)
        else:
            r = 3.4 + 2.6 * hh("cgb", key)
            c1 = lip + o * r * 0.25 - ZZ * r * 0.55
            drop = 2.0 + 3.0 * hh("cgd", key)
            c2 = Vector((fp.x, fp.y, zt - drop - r * 0.8)) + o * r * 0.3
            c2 = _anchor(pc, c2, o, r * 0.6 * 1.15, r * 1.1, 0.5)          # M6b (item 46)
            m1 = LEAF if hh("cgm", key) > 0.3 else PINE
            rng_k = ("cgbush", key)

            def gen(mb):
                rng = rng_at(*rng_k)
                cushion(mb, c1, r * 1.35, r * 0.95, r * 1.0, m1, rng, n=6, rot=ang + math.pi / 2,
                        prof=((0.0, 0.8), (0.45, 1.0), (0.85, 0.62)))
                cushion(mb, c2, r * 1.05, r * 0.6, r * 1.1, LEAF if m1 == PINE else PINE, rng, n=6,
                        rot=ang + math.pi / 2, prof=((0.0, 0.75), (0.5, 1.0), (0.88, 0.74)))
            t = add_item(x, y, r * 2.0, gen, zroot=zt)
        if t is None:
            continue
        pc.tris += t
        n += 1
    return n


def face_clumps(pc, budget, step=11.0):
    """tufos COLADOS na face das falesias altas (quebram os paineis lisos: o verde agarrado da concept), 1-2 por
    ponto em alturas dirigidas, so na face do terreno"""
    n = 0
    for x, y, ang, d in rim_samples(step, 0.4):
        if pc.tris > budget:
            break
        key = round(d, 1)
        if rim_skip(x, y) or hh("fc", key) > 0.42:
            continue
        o = vdir(ang)
        t = pc.P.top(x - o.x * 1.5, y - o.y * 1.5)
        if t is None or t[0] - L.SEA < 26.0:
            continue
        for j in range(1 + (hh("fcn", key) < 0.35)):
            f = 0.3 + 0.4 * hh("fcz", key, j)
            z = L.SEA + 4.0 + (t[0] - L.SEA - 8.0) * f
            h = pc.P.bvh.ray_cast(Vector((x + o.x * 16.0, y + o.y * 16.0, z)), -o, 34.0)
            if h[0] is None or not pc.P.own[h[2]].startswith("OP_Ter_") or abs(h[1].z) > 0.5:
                continue
            nr = Vector((h[1].x, h[1].y, 0.0))
            if nr.length < 0.1:
                continue
            nr.normalize()
            if nr.dot(o) < 0.0:
                nr = -nr
            r = 2.6 + 2.0 * hh("fcr", key, j)
            c = h[0] + nr * r * 0.2 - ZZ * r * 0.7
            c = _anchor(pc, c, nr, r * 0.75 * 1.12, r * 1.15)               # M6b (item 46)
            a = math.atan2(nr.y, nr.x) + math.pi / 2
            m = LEAF if hh("fcm", key, j) > 0.4 else PINE
            rng_k = ("fc", key, j)
            tt = add_item(c.x, c.y, r * 2.0, lambda mb: cushion(mb, c, r * 1.5, r * 0.75, r * 1.15, m, rng_at(*rng_k),
                                                                 n=6, rot=a,
                                                                 prof=((0.0, 0.65), (0.45, 1.0), (0.85, 0.72))))
            if tt is None:
                continue
            pc.tris += tt
            n += 1
    return n


def ledges(pc, budget, cell=10.0):
    """PRATELEIRAS das falesias (faces de musgo do OP_Ter_Cliff viradas para cima, no meio da face): moita grande ou
    pinheirinho debrucado para fora"""
    ob = bpy.data.objects.get("OP_Ter_Cliff")
    if ob is None:
        return 0
    mw = ob.matrix_world
    me = ob.data
    mats = [m.name if m else "" for m in me.materials]
    cand = {}
    R3 = mw.to_3x3()
    for p in me.polygons:
        if not mats[p.material_index].startswith("Cliff_OP_Moss"):
            continue
        nrm = (R3 @ p.normal).normalized()
        if abs(nrm.z) < 0.6:
            continue
        c = mw @ p.center
        if not (L.SEA + 6.0 < c.z < 80.0):
            continue
        k = (int(c.x // cell), int(c.y // cell))
        if k not in cand or p.area > cand[k][1]:
            cand[k] = (c, p.area)
    n = 0
    cx, cy = DL.centroid(ccw_rim())
    for k in sorted(cand):
        if pc.tris > budget:
            break
        c, a = cand[k]
        if a < 3.0 or hh("ledge", k[0], k[1]) > 0.8 or rim_skip(c.x, c.y):
            continue
        t = pc.P.top(c.x, c.y)
        if t is None or abs(t[0] - c.z) > 0.8:
            continue
        r = 2.0 + 1.6 * hh("lr", k[0], k[1])
        if a > 8.0 and hh("lp", k[0], k[1]) < 0.3:
            out = math.atan2(c.y - cy, c.x - cx)
            pl = pine_plan(c.x, c.y, c.z, 7.0 + 3.0 * hh("lph", k[0], k[1]), out, rng_at("lpp", k[0], k[1]), 0)
            if not pc.crown_ok(pl["spheres"]):
                continue
            t = add_item(c.x, c.y, 7.0, lambda mb: pine(mb, pl, rng_at("lpg", k[0], k[1]), 0), zroot=c.z)
        else:
            t = add_item(c.x, c.y, r * 2.0, lambda mb: bush(mb, c.x, c.y, c.z, r, rng_at("ledge", k[0], k[1]),
                                                             lumps=3), zroot=c.z)
        if t is None:
            continue
        pc.tris += t
        n += 1
    return n


def capital_spots(pc):
    try:
        import op_capital
        spots = list(op_capital.VEG_SPOTS)
    except Exception as e:
        print("AVISO op_veg: op_capital.VEG_SPOTS indisponivel (%s)" % e)
        return 0
    n = 0
    for x, y, z, kind, note in spots:
        if kind == "cerejeira":
            # o maior tamanho que cabe no recanto (copa sem tocar beiral/fachada): M -> S -> XS
            chain = ("M", "S", "XS") if any(w in note for w in ("jardim", "santuario", "mirante do porto")) else ("S", "XS")
            for i, sz in enumerate(chain):
                if place_cherry(pc, x, y, sz, "capital: " + note, lod=1, quiet=i < len(chain) - 1):
                    n += 1
                    break
        elif kind == "pinheiro":
            n += place_pine(pc, x, y, 11.0, "capital: " + note, lod=1)
        else:
            n += place_bush(pc, x, y, 2.0, nudge=True, lumps=3)
    return n


# ================================================================== cameras de revisao (fora do export)
CAMS = {
    "CAM_OPVeg_Aerea": ((60.0, -300.0, 420.0), (40.0, 250.0, 60.0), 24),
    "CAM_OPVeg_AereaOeste": ((-460.0, 120.0, 300.0), (-60.0, 260.0, 80.0), 26),
    "CAM_OPVeg_AereaLeste": ((560.0, 120.0, 300.0), (160.0, 300.0, 80.0), 26),
    "CAM_OPVeg_Close_CerejeiraTorii": ((-6.0, 30.0, T0 + L.EYE), (-38.0, 14.0, T0 + 15.0), 30),
    "CAM_OPVeg_Close_CerejeiraPraca": ((-84.0, 116.0, T1 + 3.0 + L.EYE), (-104.0, 130.0, P + 7.0), 30),
    "CAM_OPVeg_Close_CerejeiraCastelo": ((40.0, 378.0, CC + L.EYE), (90.0, 372.0, CC - 4.0), 26),
    "CAM_OPVeg_Close_Pinheiro": ((-14.0, 26.0, T0 + L.EYE), (-44.0, 28.0, T0 + 12.0), 30),
    "CAM_OPVeg_Close_Bosque": ((214.0, 334.0, 146.0), (140.0, 420.0, 126.0), 26),
    "CAM_OPVeg_Close_Borda": ((-170.0, -60.0, 70.0), (-110.0, 30.0, 84.0), 26),
    "CAM_OPVeg_Close_Promontorio": ((240.0, 230.0, 96.0), (320.0, 290.0, 92.0), 26),
    "CAM_OPVeg_PH_Rua": ((0.0, 70.0, T1 + L.EYE), (0.0, 140.0, P + 10.0), 22),
    "CAM_OPVeg_PH_PracaS": ((-20.0, 124.0, P + L.EYE), (-104.0, 132.0, P + 7.0), 24),
    "CAM_OPVeg_PH_Adro": ((0.0, 300.0, P + L.EYE), (0.0, 360.0, CF + 20.0), 22),
    "CAM_OPVeg_PH_Promontorio": (tuple(L.exit_point(70.0)) + (T1 + L.EYE,), (298.0, 292.0, T1 + 8.0), 24),
    "CAM_OPVeg_PH_TerracoAlto": ((-120.0, 330.0, W3Z + L.EYE), (-180.0, 410.0, W3Z + 6.0), 22),
    "CAM_OPVeg_PH_Canal": ((-162.0, 150.0, P + L.EYE), (-200.0, 254.0, P + 6.0), 24),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        DL.camera(n, loc, tgt, lens)


# ================================================================== build
def drop_blockout_veg():
    ob = bpy.data.objects.get("OP_Veg_Blockout")
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)


def build():
    TRUNKS.clear()
    STATS.clear()
    CHERRY_GROUPS.clear()
    _SEC.clear()
    drop_blockout_veg()
    PH_EYES.clear()
    probe = Probe()
    _PROBE[0] = probe
    pc = Placer(probe, protected_views())
    out = {}
    for x, y, s, lean, lod, note in HERO_CHERRIES:
        place_cherry(pc, x, y, s, note, lean=lean, lod=lod)
    out["capital"] = capital_spots(pc)
    out["t_cerejeiras"] = pc.tris
    for x, y, h, lean, note in HERO_PINES:
        place_pine(pc, x, y, h, note, lean=lean, lod=1 if any(w in note for w in ("entrada", "contraforte")) else 0)
    out["patio"] = court_pines(pc)                                   # M6b: 2 kuromatsu no cascalho do patio
    out["t_hero"] = pc.tris
    out["quintais"] = city_yards(pc, BUDGET_TRIS * 0.80)
    out["t_quintais"] = pc.tris
    out["bosque"] = forest(pc, BUDGET_TRIS * 0.845)
    out["t_bosque"] = pc.tris
    out["borda"] = rim_band(pc, BUDGET_TRIS * 0.90)
    out["t_borda"] = pc.tris
    out["crista"] = cliff_greens(pc, BUDGET_TRIS * 0.95)
    out["t_crista"] = pc.tris
    out["face"] = face_clumps(pc, BUDGET_TRIS * 0.96)
    out["prateleiras"] = ledges(pc, BUDGET_TRIS * 0.98)
    out["pe_muro"] = wall_feet(pc, BUDGET_TRIS)
    objs = []
    for nm in sorted(_SEC):
        o = _SEC[nm].finish()
        if o:
            # previa = Roblox: Leaf_/Flower_ saem com CastShadow=false (fm_lib.RBX_RULES) -> no Blender a folhagem
            # tambem nao projeta sombra (senao a sombra dura da malha baixa desenha facetas que o jogo nao mostra)
            o.visible_shadow = False
            objs.append(o)
    cams()
    try:
        import studio_op
        mp = sum(studio_op.est_meshparts(o) for o in objs)
    except Exception:
        mp = -1
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
    STATS["tris"], STATS["meshparts"], STATS["col"] = tris, mp, pc.ncol
    print("op_veg: %d tris, MeshParts~ %d, %d objetos, colisao %d | cerejeiras %d pinheiros %d largas %d moitas %d | %s"
          % (tris, mp, len(objs), pc.ncol, STATS.get("cherry", 0), STATS.get("pine", 0), STATS.get("broad", 0),
             STATS.get("bush", 0), out))
    print("op_veg: rejeicoes %s | sem espaco no setor %d | atravessaria o construido %d | ancora: desceu %d encostou %d" % (
        sorted(pc.rej.items(), key=lambda a: -a[1]), STATS.get("sem_espaco", 0), STATS.get("intersecao", 0),
        STATS.get("ancora_desceu", 0), STATS.get("ancora_encostou", 0)))
    print("op_veg: setores %s" % ", ".join("%s %s" % (nm, sorted(sc.cnt.items())) for nm, sc in sorted(_SEC.items())))
    print("op_veg: cerejeiras %s" % " ".join("(%.0f,%.0f,%.1f R%.1f)" % (t[0], t[1], t[2], t[4]) for t in TRUNKS
                                             if t[5] == "cherry"))
    print("op_veg: pinheiros-marco %s" % " ".join("(%.0f,%.0f,%.1f)" % (t[0], t[1], t[2]) for t in TRUNKS
                                                  if t[5] == "pine")[:600])
    print("op_veg: moitas de pe de muro %s" % STATS.get("pe_muro_xy", [])[:20])
    print("op_veg: largas %s" % " ".join("(%.0f,%.0f,%.1f R%.1f)" % (t[0], t[1], t[2], t[4]) for t in TRUNKS
                                         if t[5] == "broad")[:400])
    print("op_veg: pinheiros do patio do castelo %s" % STATS.get("patio_xy", []))
    print("op_veg: altas (pe > 140) %s" % " ".join("%s(%.0f,%.0f,%.1f)" % (t[5], t[0], t[1], t[2]) for t in TRUNKS
                                                   if t[2] > 140.0))
    for f in STATS.get("falhou", []):
        print("op_veg: AVISO nao nasceu %s (%.0f, %.0f) %s %s" % f)
    gs = cherry_groups()
    print("op_veg: grupos de cerejeiras (petalas) %d: %s" % (len(gs), " ".join(
        "%s[%d](%.0f,%.0f)" % (g["name"], g["n"], (g["box"][0] + g["box"][1]) / 2, (g["box"][2] + g["box"][3]) / 2)
        for g in gs)))


# ================================================================== GRUPOS DE CEREJEIRAS (petalas: 1 emissor por GRUPO)
CHERRY_GROUPS = []
LINK = 40.0                      # cerejeiras a menos disso (pe a pe) sao o mesmo grupo


def cherry_groups(link=LINK):
    """agrupa as cerejeiras plantadas (ligacao simples <= link) -> [{name, n, box (x0, x1, y0, y1, z_pe, z_topo),
    peso}], do mais pesado (soma das copas) para o mais leve. O op_vfx grava 1 FX_Petals_* por grupo (<= 13)"""
    if CHERRY_GROUPS:
        return CHERRY_GROUPS
    pts = sorted([(x, y, z, R) for x, y, z, r, R, f in TRUNKS if f == "cherry"], key=lambda p: (-p[3], p[0], p[1]))
    left = list(pts)
    while left:
        # semente = a maior copa que sobrou; o grupo pega as que estao a <= link dela OU de um membro, sem passar de
        # 1,6 x link da semente (grupo compacto: 1 caixa de petalas densa, nao uma faixa de 150 studs)
        sd = left[0]
        g = [sd]
        left = left[1:]
        grow = True
        while grow:
            grow = False
            for p in list(left):
                if math.hypot(p[0] - sd[0], p[1] - sd[1]) <= link * 1.6 and                         any(math.hypot(p[0] - q[0], p[1] - q[1]) <= link for q in g):
                    g.append(p)
                    left.remove(p)
                    grow = True
        box = (min(p[0] - p[3] for p in g), max(p[0] + p[3] for p in g), min(p[1] - p[3] for p in g),
               max(p[1] + p[3] for p in g), min(p[2] for p in g), max(p[2] + 1.55 * p[3] for p in g))
        cx, cy = (box[0] + box[1]) / 2, (box[2] + box[3]) / 2
        CHERRY_GROUPS.append(dict(n=len(g), box=box, peso=sum(p[3] ** 2 for p in g), sec=home_sector(cx, cy),
                                  zmin=min(p[2] for p in g)))
    CHERRY_GROUPS.sort(key=lambda g: -g["peso"])
    cnt = {}
    for g in CHERRY_GROUPS:
        cnt[g["sec"]] = cnt.get(g["sec"], 0) + 1
        g["name"] = "%s%d" % (g["sec"], cnt[g["sec"]])
    return CHERRY_GROUPS


def after_props():
    """gancho chamado pelo op_lights (ultimo do dressing). Os props nascem ANTES da vegetacao e ela ja desvia deles
    (estao no construido do Probe); aqui so a AUDITORIA final tronco x props (folga >= 1,0 da face do tronco a 1,5 do
    chao), sem mexer na geometria"""
    V, F = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("OP_Prop_"):
            continue
        mw = o.matrix_world
        b = len(V)
        V += [mw @ v.co for v in o.data.vertices]
        F += [[b + i for i in p.vertices] for p in o.data.polygons]
    if not F:
        print("op_veg.after_props: sem props")
        return 0
    t = BVHTree.FromPolygons(V, F)
    bad = [(x, y, fam) for x, y, z, r, R, fam in TRUNKS if t.find_nearest(Vector((x, y, z + 1.5)), r + 1.0)[0] is not None]
    print("op_veg.after_props: troncos encostados em props: %d %s" % (len(bad), bad[:6]))
    return len(bad)
