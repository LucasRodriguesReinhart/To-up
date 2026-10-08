# op_veg.py - VEGETACAO da Ilha 5 (ONE PIECE / WANO), M4 (PLANO_OP secoes 0, 9, 14; PROMPT_USUARIO secoes 9, 15, 17).
# Substitui op_blockout.dressing (OP_Veg_Blockout). Prefixo OP_Veg_, colecao 10_VEGETATION, sem luz. Colisao SO nos
# troncos que o jogador alcanca (COL_OP_VegTrunk_*: pe dentro de um piso andavel e a <= 40 de uma rota).
#
# LEITURA DAS REFS: a ref_01 e MUITO mais verde que a ilha do M4 - copas verdes densas nas bordas e falesias,
# cerejeiras rosas pontuando ruas/praca/portoes, pinheiros nas pontas de rocha, moitas no pe dos muros e verde
# escorrendo pelas falesias. Prompt 17: "flores rosas como ENQUADRAMENTO e hierarquia; a arvore monumental tem a maior
# presenca; ruas e patios com respiro; nao esconder fachadas, pontes e entrada".
#
# FAMILIAS (reutilizaveis; nada de espalhar ao acaso):
#   - CEREJEIRA (sakura) XS/S/M/L: tronco ESCURO curvo (base alargada, S inclinado, forquilha baixa em 2-3 bracos que
#     abrem), copa de CONJUNTOS DE FLOR = os 3 templates da arvore monumental (op_tree.TEMPLATES + op_tree._ellipsoid +
#     op_tree.post_faces: almofada com lobos, material por orientacao da face) em LOD (BLOOM_LOD). Nenhuma petala
#     modelada. 3 tons (Light/Blossom/Deep) nas 2 cerejeiras-heroi do grande torii; 2 tons (Light/Blossom) nas demais
#     (1 material a menos por objeto = MeshParts).
#   - PINHEIRO DE WANO (kuromatsu): tronco escuro em S que se debruca, galhos quase horizontais e NUVENS achatadas
#     (verde-pinho embaixo; nas maiores, nuvem clara em cima) - a leitura do pinheiro do summon.
#   - ARVORE VERDE LARGA: copa redonda em almofadas (a "brocolis" das bordas da concept) + satelite verde-pinho escuro.
#   - MOITA: 2-3 almofadas baixas (pe de muro, borda, prateleira de falesia).
#   - VERDE DE FALESIA: moita de beira (no labio, meio para fora + 1 almofada que desce colada na face), arvorezinha
#     AGARRADA que se debruca para o vazio, tufo colado na face alta.
# INTENCAO (densidade DIRIGIDA, cresce para as BORDAS; ordem = prioridade de orcamento):
#   1. HERO_CHERRIES (lista com nota): ombros do grande torii, cantos da praca POR FORA do piso, rochas dos 2 lados do
#      castelo (moldura do rochedo vista da praca), promontorio da saida, frente leste/oeste, terraco alto, summon...
#   2. op_capital.VEG_SPOTS (recantos, patamares das pontes do canal, mirantes): o maior tamanho que cabe (M -> S -> XS).
#   3. HERO_PINES: pontas de rocha (narizes da entrada, contrafortes do castelo, rochas NE, fundo, esporao da espada).
#   4. QUINTAIS (city_yards): copas pequenas entre os telhados, longe da borda (cerejeira S 45% / verde 55%); fora do
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
# ORCAMENTO (PLANO_OP secao 9, dono vegetation; teto do export 48,6k tris / 49 MeshParts): BUDGET_TRIS proprio.
#   9 objetos por SETOR; a peca (objeto, material) de um setor que passa de 158 studs fica abaixo de CAP tris (o export
#   so fatia peca >= 1500 tris E > 160 studs), senao a planta vai para o setor vizinho com folga. 5-6 materiais por
#   setor (Wood_OP_Dark, Leaf_OP, Leaf_OP_Pine, Flower_OP_Blossom/_Light; _Deep so na entrada).
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
import fm_portal_kit as PK
import op_tree as TR

C = "10_VEGETATION"
BARK, LEAF, PINE = "Wood_OP_Dark", "Leaf_OP", "Leaf_OP_Pine"
ZZ = Vector((0.0, 0.0, 1.0))
TAU = math.tau
T0, T1, P, CF, CC, W3Z = L.T0, L.T1, L.P, L.CF, L.CC, L.W3
MINE_PAD = 10.0
BUDGET_TRIS = 47600             # teto proprio (export: 48,6k)
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


# ================================================================== primitivas organicas
def cushion(mb, c, rx, ry, h, m, rng, n=7, rot=0.0, jit=0.12, prof=((0.0, 0.7), (0.38, 1.0), (0.78, 0.64))):
    """ALMOFADA de folhagem facetada: fundo quase plano, cintura larga a 1/3, ombro estreito, topo deslocado.
    c = centro do FUNDO. Tris = 2n + 2n(len(prof)-1)"""
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
    bot = bm.verts.new((c.x, c.y, c.z - h * 0.06))
    top = bm.verts.new((c.x + rng.uniform(-0.16, 0.16) * rx, c.y + rng.uniform(-0.16, 0.16) * ry, c.z + h))
    for j in range(n):
        j2 = (j + 1) % n
        bm.faces.new((rings[0][j2], rings[0][j], bot))
        bm.faces.new((rings[-1][j], rings[-1][j2], top))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    mb._post([v for r in rings for v in r] + [bot, top], m, None, 0, 1)


def tube(mb, pts, radii, m=BARK, n=6, caps=True):
    PK.taper_tube(mb, [Vector(p) for p in pts], radii, m, n=n, caps=caps)




# LOD do conjunto de flor: (lados/aneis do corpo, lados/aneis dos lobos, quantos lobos) - mesmos TEMPLATES do op_tree
BLOOM_LOD = {2: ((10, 5), (6, 4), 5), 1: ((7, 4), (5, 3), 4), 0: ((7, 4), (5, 3), 3)}


def bloom(mb, c, r, flat, tmpl, rot, lod=1):
    """CONJUNTO DE FLOR da arvore monumental (op_tree.TEMPLATES: almofada + 5 lobos; material por orientacao da face:
    topo Flower_OP_Light, corpo _Blossom, baixo _Deep) em LOD - a mesma familia, so com menos lados"""
    groups = {"Flower_OP_Light": [], "Flower_OP_Blossom": [], "Flower_OP_Deep": []}
    cz, sz = math.cos(rot), math.sin(rot)
    big_n, lobe_n, nlobes = BLOOM_LOD[lod]
    for i, ((ox, oy, oz), pr, ft, fb) in enumerate(tmpl):
        if i > nlobes:
            break
        x, y = ox * r * cz - oy * r * sz, ox * r * sz + oy * r * cz
        pc = (c[0] + x, c[1] + y, c[2] + oz * r * flat * 1.4)
        rr = pr * r
        nu, nv = big_n if pr > 0.9 else lobe_n
        fs = TR._ellipsoid(mb, pc, rr, rr * 0.94, rr * ft * flat * 1.25, rr * fb * flat * 1.25, nu, nv, rot + ox)
        for f in fs:
            nz = f.normal.z
            if nz < -0.3:
                groups["Flower_OP_Deep"].append(f)
            elif nz > 0.62:
                groups["Flower_OP_Light"].append(f)
            else:
                groups["Flower_OP_Blossom"].append(f)
    if lod < 2:                     # 2 tons fora das cerejeiras-heroi (1 material a menos por objeto: MeshParts)
        groups["Flower_OP_Blossom"] += groups.pop("Flower_OP_Deep")
    for m, fs in groups.items():
        TR.post_faces(mb, fs, m, smooth=True)


# ================================================================== FAMILIAS
# cada familia: PLANO (esferas da copa para as regras, ANTES de gerar) + GERADOR
CHERRY_SIZES = {"XS": (8.5, 4.8, 2, 0.45), "S": (11.0, 7.0, 2, 0.55), "M": (14.0, 9.5, 3, 0.7), "L": (18.0, 12.0, 3, 0.9)}   # h, R, bracos, r0


def cherry_plan(x, y, z, size, lean_az, rng):
    h, R, nl, r0 = CHERRY_SIZES[size]
    d = vdir(lean_az)
    base = Vector((x, y, z))
    F = base + d * R * 0.2 + ZZ * h * 0.38                      # forquilha baixa (copa larga, guarda-chuva)
    a0 = lean_az + rng.uniform(-0.5, 0.5)
    tips = []
    for k in range(nl):
        a = a0 + TAU * k / nl + rng.uniform(-0.3, 0.3) + (0.6 if nl == 2 else 0.0)
        out = R * rng.uniform(0.54, 0.62)
        tips.append((a, F + vdir(a) * out + ZZ * h * rng.uniform(0.2, 0.28), R * rng.uniform(0.47, 0.53)))
    top = (F + d * R * 0.1 + vdir(a0 + 2.0) * R * 0.08 + ZZ * h * 0.48, R * 0.5)
    drop = (F + vdir(a0 + math.pi * 0.85) * R * 0.78 + ZZ * h * 0.1, R * 0.32)   # massa baixa caida (lod 2)
    sph = [(t[1] + ZZ * t[2] * 0.2, t[2] * 1.12) for t in tips] + [(top[0] + ZZ * top[1] * 0.2, top[1] * 1.12)]
    return dict(h=h, R=R, r0=r0, base=base, F=F, tips=tips, top=top, drop=drop, d=d, spheres=sph, nl=nl)


def cherry(mb, pl, rng, lod=1):
    """CEREJEIRA: tronco escuro curvo (base alargada, S inclinado), forquilha baixa em bracos que abrem quase na
    horizontal e sobem na ponta; conjuntos de flor nas pontas + 1 no alto (ceu entre eles); lod 2: + massa caida"""
    base, F, d, r0, h = pl["base"], pl["F"], pl["d"], pl["r0"], pl["h"]
    perp = Vector((-d.y, d.x, 0.0))
    s = 1.0 if rng.random() < 0.5 else -1.0
    lean = F - base
    pts = [base - ZZ * 0.5, base + lean * 0.22 + perp * 0.35 * s + ZZ * 0.4,
           base + lean * 0.55 - perp * 0.55 * s, base + lean * 0.86 + perp * 0.2 * s, F]
    n = 6 if lod == 2 else (5 if lod else 4)
    tube(mb, pts, [r0 * 1.3, r0 * 1.08, r0 * 0.94, r0 * 0.84, r0 * 0.74], n=n)
    PK.cone(mb, base - ZZ * 0.5, base + ZZ * 1.0, r0 * 2.1, r0 * 1.15, BARK, n=n)
    for a, tip, rr in pl["tips"]:
        v = tip - F
        mid = F + Vector((v.x, v.y, 0.0)) * 0.5 + ZZ * v.z * 0.32
        tube(mb, [F - vdir(a) * r0 * 0.3, mid, tip - ZZ * rr * 0.15], [r0 * 0.68, r0 * 0.5, r0 * 0.3],
             n=5 if lod == 2 else 4)
    k0 = int(rng.random() * 3)
    for i, (a, tip, rr) in enumerate(pl["tips"]):
        bloom(mb, tip, rr, 0.78, TR.TEMPLATES[(i + k0) % 3], rng.uniform(0, TAU), lod)
    c, r = pl["top"]
    bloom(mb, c, r, 0.72, TR.TEMPLATES[(k0 + 2) % 3], rng.uniform(0, TAU), lod)
    if lod == 2:
        c, r = pl["drop"]
        tube(mb, [F, F.lerp(c, 0.5) + ZZ * 0.4, c], [r0 * 0.5, r0 * 0.36, r0 * 0.22], n=4)
        bloom(mb, c, r, 0.8, TR.TEMPLATES[(k0 + 1) % 3], rng.uniform(0, TAU), 1)


def pine_plan(x, y, z, h, lean_az, rng, lod=1):
    d = vdir(lean_az)
    sv = Vector((-d.y, d.x, 0.0))
    b0 = Vector((x, y, z))
    s = h / 12.0
    pts = [b0 - ZZ * 0.5, b0 + d * 0.6 * s + ZZ * h * 0.22, b0 + d * 2.3 * s + sv * 0.8 * s + ZZ * h * 0.45,
           b0 + d * 3.2 * s - sv * 0.4 * s + ZZ * h * 0.68, b0 + d * 2.5 * s + ZZ * h * 0.88]
    pads = []
    tiers = ((0.36, 2.9, 4.8, 2.7), (0.52, 0.5, 4.4, 2.5), (0.66, 4.2, 3.9, 2.2), (0.8, 1.8, 3.2, 1.9))
    for k, (t, ang, ln, rr) in enumerate(tiers if lod else tiers[:3]):
        a = lean_az + ang + rng.uniform(-0.3, 0.3)
        seg = min(3, int(t * 4))
        bp = pts[seg].lerp(pts[seg + 1], t * 4 - seg)
        tip = bp + vdir(a) * ln * s + ZZ * 0.6 * s
        pads.append((bp, tip, rr * s, a))
    sph = [(tip + ZZ * 0.4 * s, rr * 1.45) for bp, tip, rr, a in pads] + [(pts[-1] + ZZ * 0.6 * s, 2.2 * s)]
    return dict(pts=pts, pads=pads, s=s, d=d, spheres=sph, base=b0, R=4.6 * s)


def pine(mb, pl, rng, lod=1):
    """PINHEIRO DE WANO (kuromatsu): tronco escuro em S que se debruca, galhos quase horizontais, nuvens achatadas
    (verde-pinho embaixo; nas 2 maiores uma nuvem clara em cima)"""
    pts, s = pl["pts"], pl["s"]
    tube(mb, pts, [0.85 * s, 0.66 * s, 0.5 * s, 0.36 * s, 0.24 * s], n=5 if lod else 4)
    PK.cone(mb, pts[0], pts[0] + ZZ * 1.4 * s, 1.5 * s, 0.8 * s, BARK, n=5 if lod else 4)
    for i, (bp, tip, rr, a) in enumerate(pl["pads"]):
        mid = bp.lerp(tip, 0.55) + ZZ * 0.2 * s
        tube(mb, [bp, mid, tip], [0.3 * s, 0.22 * s, 0.15 * s], n=4 if lod else 3)
        cushion(mb, tip - ZZ * 0.25 * s, rr * 1.45, rr * 1.1, rr * 0.5, PINE, rng, n=7 if lod else 6, rot=a)
        if lod and i < 2:
            cushion(mb, tip + ZZ * 0.45 * s + vdir(a) * 0.3 * s, rr * 0.95, rr * 0.75, rr * 0.36, LEAF, rng, n=6,
                    rot=a + 0.5)
    t = pts[-1]
    cushion(mb, t - ZZ * 0.2 * s, 2.3 * s, 1.9 * s, 1.15 * s, PINE, rng, n=7 if lod else 6,
            rot=math.atan2(pl["d"].y, pl["d"].x))
    if lod:
        cushion(mb, t + ZZ * 0.6 * s, 1.5 * s, 1.25 * s, 0.75 * s, LEAF, rng, n=6)


def broad_plan(x, y, z, h, R, rng, lod=0):
    b0 = Vector((x, y, z))
    lean = vdir(rng.uniform(0, TAU)) * rng.uniform(0.2, 0.8)
    C0 = b0 + lean + ZZ * h * 0.6
    sats = []
    a0 = rng.uniform(0, TAU)
    ns = 3 if lod else 2
    for k in range(ns):
        a = a0 + TAU * k / ns + rng.uniform(-0.4, 0.4)
        sats.append((C0 + vdir(a) * R * rng.uniform(0.55, 0.7) - ZZ * h * rng.uniform(0.04, 0.14),
                     R * rng.uniform(0.56, 0.66), a))
    sph = [(C0 + ZZ * R * 0.3, R * 0.95)] + [(c + ZZ * r * 0.3, r) for c, r, a in sats]
    return dict(base=b0, C0=C0, h=h, R=R, sats=sats, spheres=sph, lean=lean)


def broad(mb, pl, rng, lod=0):
    """ARVORE VERDE LARGA: tronco curto, copa redonda em almofadas (central + 2-3 satelites, 1 delas verde-pinho
    escuro = profundidade)"""
    b0, C0, h, R = pl["base"], pl["C0"], pl["h"], pl["R"]
    r0 = 0.3 + R * 0.075
    tube(mb, [b0 - ZZ * 0.5, b0 + pl["lean"] * 0.3 + ZZ * h * 0.3, C0 - ZZ * R * 0.3], [r0 * 1.3, r0, r0 * 0.6],
         n=4)
    cushion(mb, C0 - ZZ * R * 0.45, R, R * rng.uniform(0.86, 0.96), R * 1.15, LEAF, rng, n=9 if lod else 8)
    for i, (c, r, a) in enumerate(pl["sats"]):
        cushion(mb, c - ZZ * r * 0.4, r, r * 0.88, r * 1.05, PINE if i == 1 else LEAF, rng, n=7 if lod else 6, rot=a)


def bush(mb, x, y, z, r, rng, lumps=2, m=LEAF, n=6):
    a0 = rng.uniform(0, TAU)
    for k in range(lumps):
        q = Vector((x, y, z - 0.3)) + (vdir(a0 + 2.3 * k) * r * rng.uniform(0.55, 0.85) if k else Vector())
        rr = r * (1.0 if k == 0 else rng.uniform(0.55, 0.75))
        cushion(mb, q, rr * 1.1, rr * 0.95, rr * rng.uniform(0.95, 1.2), m if k != 1 else PINE, rng, n=n, rot=a0 + k,
                jit=0.15)


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
    (-106.0, 130.0, "M", 210.0, 1, "canto SO da praca, por fora do piso (moldura de quem sobe a escadaria)"),
    (-88.0, 374.0, "M", 180.0, 1, "rocha oeste do castelo: moldura do rochedo vista da praca"),
    (88.0, 370.0, "L", 0.0, 1, "rocha leste do castelo, perto da base da arvore (eco da copa monumental)"),
    (298.0, 292.0, "M", 60.0, 1, "promontorio da saida (laje, lanternas, cerejeira)"),
    (100.0, 26.0, "M", None, 1, "rocha da frente leste, sobre a enseada (concept: rosa na borda direita)"),
    (-70.0, 30.0, "M", None, 1, "borda sul do bairro do canal (concept: rosa na frente esquerda)"),
    (-104.0, 334.0, "M", 150.0, 1, "canto NO da praca, pe do terraco alto"),
    (108.0, 306.0, "S", 30.0, 1, "canto NE da praca, entrada do santuario"),
    (126.0, 178.0, "S", None, 1, "gramado sul do terraco do summon"),
    (128.0, 420.0, "M", None, 0, "bosque do fundo leste"),
    (-176.0, 420.0, "M", None, 0, "terraco alto, jardim do fundo das mansoes"),
    (-178.0, 350.0, "S", None, 1, "terraco alto, jardim entre a U1 e a U4"),
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
    (215.0, 505.0, 12.0, 60.0, "raiz do esporao"),
    (226.0, 528.0, 11.0, 40.0, "esporao"),
    (262.0, 572.0, 11.0, 40.0, "esporao, perto da espada"),
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


def city_yards(pc, budget, step=10.0):
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
                    if hh("cy", nm, x, y, "k") < 0.45:
                        ok = place_cherry(pc, xx, yy, "S", "quintal", lod=0, nudge=False, quiet=True)
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


def rim_band(pc, budget):
    """faixa da borda: 3 fileiras para dentro da crista; densidade por setor (ruido dirigido de baixa frequencia,
    massas e vazios ao longo do contorno) e maior na fileira de fora"""
    n = 0
    for row, (step, inset, base) in enumerate(((8.0, 5.5, 0.9), (10.0, 13.0, 0.65), (13.0, 21.0, 0.35))):
        for x, y, ang, d in rim_samples(step, inset):
            if pc.tris > budget:
                return n
            if rim_skip(x, y):
                continue
            sector = 0.5 + 0.5 * math.sin(d / 61.0 + 1.3) * math.cos(d / 23.0 + 0.4)
            dens = base * (0.6 + 0.6 * sector)
            key = (row, round(d, 1))
            if hh("rim", *key) > dens:
                continue
            k = hh("rimk", *key)
            s = 0.8 + 0.5 * hh("rims", *key) - 0.1 * row
            lean = math.degrees(ang) + (hh("riml", *key) - 0.5) * 50.0
            if k < 0.2:
                ok = place_pine(pc, x, y, 12.0 * s, "borda", lean=lean, lod=0, nudge=True, quiet=True)
            elif k < 0.78:
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
    out["t_hero"] = pc.tris
    out["quintais"] = city_yards(pc, BUDGET_TRIS * 0.53)
    out["t_quintais"] = pc.tris
    out["bosque"] = forest(pc, BUDGET_TRIS * 0.61)
    out["t_bosque"] = pc.tris
    out["borda"] = rim_band(pc, BUDGET_TRIS * 0.77)
    out["t_borda"] = pc.tris
    out["crista"] = cliff_greens(pc, BUDGET_TRIS * 0.91)
    out["t_crista"] = pc.tris
    out["face"] = face_clumps(pc, BUDGET_TRIS * 0.94)
    out["prateleiras"] = ledges(pc, BUDGET_TRIS * 0.97)
    out["pe_muro"] = wall_feet(pc, BUDGET_TRIS)
    objs = []
    for nm in sorted(_SEC):
        o = _SEC[nm].finish()
        if o:
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
    print("op_veg: rejeicoes %s | sem espaco no setor %d | atravessaria o construido %d" % (
        sorted(pc.rej.items(), key=lambda a: -a[1]), STATS.get("sem_espaco", 0), STATS.get("intersecao", 0)))
    print("op_veg: setores %s" % ", ".join("%s %s" % (nm, sorted(sc.cnt.items())) for nm, sc in sorted(_SEC.items())))
    print("op_veg: cerejeiras %s" % " ".join("(%.0f,%.0f,%.1f R%.1f)" % (t[0], t[1], t[2], t[4]) for t in TRUNKS
                                             if t[5] == "cherry"))
    print("op_veg: pinheiros-marco %s" % " ".join("(%.0f,%.0f,%.1f)" % (t[0], t[1], t[2]) for t in TRUNKS
                                                  if t[5] == "pine")[:600])
    print("op_veg: moitas de pe de muro %s" % STATS.get("pe_muro_xy", [])[:20])
    print("op_veg: altas (pe > 140) %s" % " ".join("%s(%.0f,%.0f,%.1f)" % (t[5], t[0], t[1], t[2]) for t in TRUNKS
                                                   if t[2] > 140.0))
    for f in STATS.get("falhou", []):
        print("op_veg: AVISO nao nasceu %s (%.0f, %.0f) %s %s" % f)


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
