# op_tree.py - ARVORE MONUMENTAL ARQUEADA (marco heroi da Ilha 5 ONE PIECE / WANO; dono "tree", prefixo OP_Tree_)
# V2 (feedback do usuario 10/10, item U4: "tubo marrom liso com nuvenzinhas rosas" REPROVADO). Refs: ref_02 (arvore do
#   castelo do anime) e ref_03 (atmosfera de Wano). A arvore do anime e um PINHEIRO monumental: tronco grosso e
#   retorcido, casca em fibras, galhos laterais que terminam em COPAS DE PINHEIRO EM NUVEM (almofadas achatadas em
#   camadas, borda lobada, verde profundo com o topo claro). Nada de rosa no arco (o rosa e das cerejeiras da cidade).
#   SILHUETA (mantida do M6b: contrato com o castelo): nasce no fundo-leste do patio (136,2), sobe a DIREITA da torre,
#     ombro baixo e largo, topo longo por cima da torre e desce a ESQUERDA terminando num gancho.
#   TRONCO V2: raios ~15% maiores (base 16, meio 12,6, apice 10); secao IRREGULAR com 3 cordoes largos + 8 SULCOS
#     longitudinais fundos (ate 18% do raio) e NOS/burls. Os vertices do anel GIRAM com a fibra (TWIST voltas no
#     comprimento): cordoes e sulcos viram ESPIRAIS continuas (tronco torcido de zimbro/bonsai), sem serrilhado.
#     Fundo dos sulcos com material proprio escuro (Bark_OP_Groove): a fibra le sem textura, no sol e na sombra.
#   GALHOS: 10 galhos grossos que NASCEM do tronco (dentro dele) e saem para fora/cima, cada um terminando num
#     CONJUNTO DE ALMOFADAS (MASSES): almofada principal + almofada de cima + 1-2 laterais mais baixas, com raminhos.
#   COPA: cloud_pad() = disco achatado com borda em lobos (vincos), fundo quase plano, topo em domo com calombos;
#     material pela normal: topo Leaf_OP_Sun (claro), lado Leaf_OP, baixo Leaf_OP_Pine (profundo). Sombreado suave.
#   RAIZES: seguem o chao REAL (raio para baixo): passam por cima do muro e escorrem pela rocha (intactas do M6b).
#   COLISAO: so o tronco e as raizes dentro do patio (alcance do jogador). Copa e arco: sem colisao.
# PRIMITIVAS COMPARTILHADAS com o op_veg (familias V2): cloud_pad (pinheiro/karikomi), puff (cacho de cerejeira e copa
#   larga: casca unica com calombos = cachos e sub-cachos, vinco escuro entre eles), limb (galho/tronco suave),
#   cull_inside (apaga as faces de um cacho escondidas dentro de outro: tris so onde se ve).
# Contrato com o castelo (op_castle): tree_envelope() / TREE_KEEPOUT (abaixo) e castle_envelope() (lido do op_layout).
# V3 (rodada 2 do usuario 10/10: 'a arvore grande melhorou bastante, porem suas folhas precisam melhorar'): tronco,
#   galhos, raizes e MASSES intactos; a COPA virou pine_cloud() (camada de base com FRANJA DE AGULHAS e fundo
#   escuro, sub-almofadas claras e capuz amarelado, 4 tons Leaf_OP_Sun/Leaf_OP/Leaf_OP_Pine/Leaf_OP_PineUnder) e os
#   satelites tambem sao nuvens em camadas. Primitivas V3 compartilhadas com o op_veg: blob (cor em faixas),
#   bark_limb (cordoes torcidos), root_claws (raizes que agarram o chao), pine_pad / pine_cloud.
import math, random
import bmesh, bpy
from mathutils import Vector, Matrix, Euler, noise
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, col_box
import op_layout as L

CC = L.CC
TAU = math.tau
ZZ = Vector((0.0, 0.0, 1.0))
TIER_A_TOP = CC + 26.0          # casca detalhada so ate aqui (patio 136,2 + ~20 de alcance da camera do jogador)
BARK, GROOVE = "Bark_OP", "Bark_OP_Groove"
PAD_MATS = ("Leaf_OP_Sun", "Leaf_OP", "Leaf_OP_Pine")      # topo / lado / baixo das almofadas da arvore monumental

# ------------------------------------------------------------------ CONTRATO / ENVOLTORIA (ler antes de mexer)
BASE_C = (54.0, 449.0)          # eixo do tronco no chao do patio (canto fundo-leste, colado ao muro)
# tronco (x, y, z, raio) - caminho do M6b (o castelo conta com ele); V2: raios FINAIS mais grossos (monumental)
TRUNK = [(54.0, 449.0, CC - 5.0, 16.0), (55.0, 448.0, CC + 4.0, 15.4), (58.0, 447.0, CC + 16.0, 14.8),
         (63.0, 445.0, CC + 30.0, 14.4), (71.0, 442.0, CC + 46.0, 14.0), (80.0, 439.0, CC + 62.0, 13.6),
         (89.0, 435.0, CC + 78.0, 13.2), (96.0, 430.0, CC + 93.0, 12.8), (94.0, 424.0, CC + 104.0, 12.4),
         (81.0, 418.0, CC + 110.5, 12.0), (58.0, 413.0, CC + 113.0, 11.6), (32.0, 410.0, CC + 113.5, 11.2),
         (7.0, 409.0, CC + 112.0, 10.6), (-17.0, 409.0, CC + 108.0, 9.8), (-39.0, 410.0, CC + 101.0, 8.8),
         (-57.0, 413.0, CC + 91.0, 7.8), (-69.0, 415.0, CC + 79.0, 6.6), (-75.0, 416.0, CC + 66.0, 5.4),
         (-75.0, 417.0, CC + 55.0, 4.3), (-71.0, 416.0, CC + 47.0, 3.2), (-65.0, 414.0, CC + 42.0, 2.0)]
FLAT = 0.88                     # secao: raio no plano do arco = r; de lado = r * FLAT
NSIDE = 44                      # lados do tronco (cordoes e sulcos amarrados aos indices: giram com a fibra)
TWIST = 1.15                    # voltas da fibra no comprimento todo (espiral visivel, nao parafuso)
# sulcos: (indice do lado, profundidade relativa ao raio) - espacamento irregular (casca, nao engrenagem)
FURROWS = [(0, 0.21), (6, 0.12), (11, 0.19), (17, 0.11), (22, 0.22), (28, 0.13), (33, 0.18), (39, 0.11)]
GROOVE_T = 0.065                # fundo de sulco mais fundo que isso = Bark_OP_Groove (escuro)
# nos / burls: (fracao do comprimento, fracao da volta, forca, comprimento)
KNOTS = [(0.035, 0.12, 0.10, 4.5), (0.07, 0.58, 0.12, 5.0), (0.16, 0.86, 0.10, 7.0), (0.30, 0.30, 0.09, 8.0),
         (0.47, 0.70, 0.08, 9.0), (0.63, 0.20, 0.08, 8.0), (0.78, 0.50, 0.07, 6.0)]
# raizes-contraforte: (angulo no chao em graus, comprimento, raio na saida, achatamento, garfo, peso do lobo na base)
ROOTS = [(-10.0, 30.0, 6.4, 0.52, True, 1.0),     # leste: por cima do muro, escorre pela face da rocha (BackE 120)
         (34.0, 24.0, 6.0, 0.52, False, 1.0),     # nordeste: canto do muro -> rocha do fundo
         (64.0, 20.0, 5.6, 0.52, True, 0.9),      # norte-nordeste: canto do muro -> escorre na rocha do fundo-leste
         (132.0, 9.0, 5.6, 0.5, False, 0.85),     # noroeste: patio, atras da torre (curta: para antes do muro)
         (172.0, 17.0, 6.0, 0.5, True, 0.9),      # oeste: patio, atras da torre (y > 446), rente no fim
         (250.0, 12.0, 5.6, 0.5, False, 0.8),     # sul-sudoeste: patio (curta; longe do canto da torre)
         (284.0, 20.0, 5.6, 0.52, False, 0.9)]    # sul: ao longo do muro leste, para o yagura
# COPA V2 = CONJUNTOS DE ALMOFADAS DE PINHEIRO na ponta de cada galho (ref_02: coroa grande sobre o arco, galho longo
#   para a esquerda, almofadas em alturas diferentes na direita, gancho com almofada pequena). Vaos de ceu entre eles.
#   (centro da base da almofada principal, raio, H/R, almofadas no conjunto, alongamento, papel)
MASSES = [((22.0, 412.0, CC + 129.0), 33.0, 0.46, 6, 1.4, "coroa: sobre o topo do arco"),
          ((-34.0, 404.0, CC + 121.0), 19.0, 0.5, 3, 1.3, "topo esquerda"),
          ((-106.0, 406.0, CC + 104.0), 20.0, 0.48, 4, 1.4, "galho longo da esquerda (ref_02)"),
          ((-60.0, 409.0, CC + 47.0), 12.0, 0.5, 2, 1.2, "ponta do gancho"),
          ((128.0, 428.0, CC + 106.0), 19.0, 0.48, 3, 1.35, "ombro direito"),
          ((118.0, 446.0, CC + 77.0), 16.0, 0.5, 3, 1.25, "direita, meio"),
          ((96.0, 465.0, CC + 48.0), 13.0, 0.5, 2, 1.2, "direita baixa, atras (vista do patio)"),
          ((58.0, 447.0, CC + 125.0), 17.0, 0.5, 3, 1.3, "atras do topo (profundidade de lado)"),
          ((-2.0, 385.0, CC + 123.0), 14.0, 0.5, 2, 1.25, "frente do topo"),
          ((-94.0, 431.0, CC + 79.0), 13.0, 0.5, 2, 1.2, "esquerda baixa, atras")]
# galhos: (ponto de saida no tronco, pontos (x, y, z, r)) - grossos; o ultimo fica DENTRO da almofada principal
BRANCHES = [((32.0, 410.0, CC + 113.5), [(28.0, 411.0, CC + 120.0, 5.6), (24.0, 412.0, CC + 127.0, 2.8)]),
            ((-17.0, 409.0, CC + 108.0), [(-24.0, 406.0, CC + 114.0, 3.8), (-29.0, 404.0, CC + 119.0, 2.4)]),
            ((-52.0, 412.0, CC + 94.0), [(-70.0, 409.0, CC + 97.0, 5.6), (-88.0, 407.0, CC + 100.5, 4.0),
                                         (-104.0, 406.0, CC + 104.0, 2.4)]),
            ((-69.0, 415.0, CC + 47.0), [(-65.0, 412.0, CC + 45.5, 1.8), (-62.0, 410.0, CC + 46.0, 1.3)]),
            ((95.0, 428.0, CC + 98.0), [(108.0, 428.0, CC + 101.0, 5.6), (118.0, 428.0, CC + 104.0, 3.8),
                                        (127.0, 428.0, CC + 106.0, 2.2)]),
            ((86.0, 436.0, CC + 72.0), [(100.0, 441.0, CC + 74.0, 4.8), (110.0, 444.0, CC + 76.0, 2.6),
                                        (116.0, 446.0, CC + 76.5, 1.6)]),
            ((66.0, 444.0, CC + 36.0), [(78.0, 454.0, CC + 41.0, 3.4), (88.0, 461.0, CC + 46.0, 2.4),
                                        (94.0, 464.0, CC + 47.5, 1.5)]),
            ((60.0, 413.0, CC + 113.0), [(59.0, 426.0, CC + 117.0, 3.6), (58.0, 438.0, CC + 122.0, 2.4),
                                         (58.0, 445.0, CC + 124.0, 1.5)]),
            ((4.0, 409.0, CC + 112.0), [(2.0, 398.0, CC + 117.0, 3.4), (-1.0, 389.0, CC + 122.0, 2.2)]),
            ((-69.0, 415.0, CC + 79.0), [(-80.0, 423.0, CC + 79.5, 3.2), (-91.0, 430.0, CC + 79.0, 2.0)])]
# o castelo NAO pode entrar aqui (poligono no nivel do patio, z de CC a CC+30): o muro do fundo-leste deve TERMINAR
# encostado na base/raizes (as raizes passam por cima do muro do blockout ate o op_castle refazer o encontro)
TREE_KEEPOUT = [(30.0, 452.0), (34.0, 436.0), (48.0, 426.0), (58.0, 410.0), (78.0, 410.0), (84.0, 432.0),
                (94.0, 452.0), (86.0, 478.0), (60.0, 482.0), (36.0, 472.0)]
CLEAR_CASTLE = 4.0              # folga minima tronco/galho/copa <-> volumes do castelo (torre, telhados, yagura)


def castle_envelope():
    """volumes do castelo que a arvore respeita (lidos do op_layout): caixas (x0, y0, z0, x1, y1, z1)"""
    kx, ky = L.KEEP_C
    out = []
    try:
        from op_castle import kz                     # M6b: andares de cima da torre esticados (op_castle.KEEP_STRETCH)
    except Exception:
        kz = lambda z: z
    for i, (hx, hy, z0, hw, over) in enumerate(L.KEEP_TIERS):
        top = CC + kz(z0 + hw + (10.0 if i == len(L.KEEP_TIERS) - 1 else 3.6))
        out.append(("torre_andar_%d" % i, (kx - hx - over, ky - hy - over, CC, kx + hx + over, ky + hy + over, top)))
    out.append(("torre_base_talude", (kx - L.KEEP_TIERS[0][0] - 3.0, ky - L.KEEP_TIERS[0][1] - 3.0, CC,
                                      kx + L.KEEP_TIERS[0][0] + 3.0, ky + L.KEEP_TIERS[0][1] + 3.0, CC + 5.0)))
    tx, ty, ts = L.TURRET
    out.append(("yagura", (tx - ts / 2 - 2.0, ty - ts / 2 - 2.0, CC, tx + ts / 2 + 2.0, ty + ts / 2 + 2.0, CC + 22.0)))
    return out


def tree_envelope():
    """o que o castelo (e qualquer outro dono) deve deixar livre: capsulas do tronco/galhos, elipsoides da copa e o
    poligono da base. {"capsules": [((x,y,z), (x,y,z), r)], "blobs": [((x,y,z), (rx, ry, rz))], "keepout": [...],
    "keepout_z": (z0, z1)}"""
    caps = []
    for a, b in zip(TRUNK, TRUNK[1:]):
        caps.append((a[:3], b[:3], max(a[3], b[3]) * 1.22))       # V2: sulcos/cordoes/nos ate +22% do raio
    for att, pts in BRANCHES:
        c = trunk_nearest(att)
        prev = (c[0].x, c[0].y, c[0].z, c[1])
        for p in pts:
            caps.append((prev[:3], p[:3], max(prev[3] * 0.55, p[3])))
            prev = p
    blobs = [((c[0], c[1], c[2] + r * f * 0.35), (r * 1.25 * ax, r * 1.15, r * f * 1.3)) for c, r, f, n, ax, _ in MASSES]
    return {"capsules": caps, "blobs": blobs, "keepout": list(TREE_KEEPOUT), "keepout_z": (CC - 20.0, CC + 30.0)}


# ------------------------------------------------------------------ curva
def _catmull_dense(pts, sub=16):
    out = []
    n = len(pts)
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        for k in range(sub):
            t = k / sub
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(len(p1))))
    out.append(tuple(pts[-1]))
    return out


class Curve:
    """polilinha densa com parametro de comprimento de arco; amostra (centro, raio) em s"""

    def __init__(self, pts, sub=16):
        d = _catmull_dense(pts, sub)
        self.P = [Vector(p[:3]) for p in d]
        self.R = [p[3] for p in d]
        self.S = [0.0]
        for a, b in zip(self.P, self.P[1:]):
            self.S.append(self.S[-1] + (b - a).length)
        self.len = self.S[-1]

    def at(self, s):
        s = max(0.0, min(self.len, s))
        lo, hi = 0, len(self.S) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.S[m] <= s:
                lo = m
            else:
                hi = m
        t = (s - self.S[lo]) / max(1e-6, self.S[hi] - self.S[lo])
        p = self.P[lo].lerp(self.P[hi], t)
        r = self.R[lo] + (self.R[hi] - self.R[lo]) * t
        tg = (self.P[hi] - self.P[lo]).normalized()
        return p, r, tg


_TRUNK_C = None


def trunk_curve():
    global _TRUNK_C
    if _TRUNK_C is None:
        _TRUNK_C = Curve(TRUNK)
    return _TRUNK_C


def trunk_point(u):
    c = trunk_curve()
    return c.at(u * c.len)


def trunk_nearest(xyz):
    """ponto do eixo do tronco mais perto de xyz -> (centro, raio, tangente)"""
    c = trunk_curve()
    q = Vector(xyz)
    i = min(range(len(c.P)), key=lambda k: (c.P[k] - q).length)
    return c.at(c.S[i])


# ------------------------------------------------------------------ malha
def post_faces(mb, faces, m, smooth=True, uv=True):
    faces = [f for f in faces if f is not None and f.is_valid]
    if not faces:
        return faces
    mi = mb._mi_for(m) if m.startswith("Cliff_OP") else mb._mi(m)
    t = 0.0                      # sem tint sorteado: tronco/raiz/galho continuos (sem faixa de cor na emenda)
    for f in faces:
        f.material_index = mi
        f[mb.tint] = t
        f.smooth = smooth
        f.normal_update()
    if uv:
        mb._uv(set(faces), m)
    return faces


def skin(mb, rings, m, cap0=True, cap1=True, smooth=True, mat_of=None, s_of=None, vval=None):
    """aneis (listas de Vector com o mesmo n) -> tubo fechado; mat_of(face, i_anel[, valores dos vertices]) escolhe o
    material por face (vval = valor por vertice, paralelo a rings). UV CILINDRICA: u = comprimento de arco, v = volta"""
    bm = mb.bm
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    vmap = {}
    if vval is not None:
        for ring, vals in zip(vr, vval):
            for v, x in zip(ring, vals):
                vmap[v] = x
    faces = []
    n = len(rings[0])
    for i, (r0, r1) in enumerate(zip(vr, vr[1:])):
        for k in range(n):
            k2 = (k + 1) % n
            try:
                f = bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
                f.normal_update()
                faces.append((f, i))
            except ValueError:
                pass
    caps = []
    for ring, ok, rev in ((vr[0], cap0, True), (vr[-1], cap1, False)):
        if ok:
            c = sum((v.co for v in ring), Vector()) / len(ring)
            cv = bm.verts.new(c)
            for k in range(n):
                a, b = ring[k], ring[(k + 1) % n]
                try:
                    caps.append(bm.faces.new((b, a, cv) if rev else (a, b, cv)))
                except ValueError:
                    pass
    if s_of is None:
        s_of = [0.0]
        for a, b in zip(rings, rings[1:]):
            ca = sum(a, Vector()) / len(a)
            cb = sum(b, Vector()) / len(b)
            s_of.append(s_of[-1] + (cb - ca).length)
    circ = []
    for ring in rings:
        c = sum(ring, Vector()) / len(ring)
        circ.append(2 * math.pi * sum((v - c).length for v in ring) / len(ring))
    import fm_lib
    tk = fm_lib.tex_key(m)
    inv = 1.0 / fm_lib.tex_tile(tk) if tk else 1.0 / 8.0
    uvl = mb.uvl
    idx = [{v: k for k, v in enumerate(ring)} for ring in vr]
    for f, i in faces:
        cc = (circ[i] + circ[min(i + 1, len(circ) - 1)]) / 2.0
        ks = []
        for lp in f.loops:
            v = lp.vert
            j = i if v in idx[i] else i + 1
            ks.append((lp, j, idx[j][v]))
        wrap = max(k for _, _, k in ks) == n - 1 and min(k for _, _, k in ks) == 0
        for lp, j, k in ks:
            if wrap and k == 0:
                k = n
            lp[uvl].uv = (s_of[j] * inv, (k / n) * cc * inv)
    if mat_of is None:
        post_faces(mb, [f for f, _ in faces], m, smooth, uv=False)
        post_faces(mb, caps, m, smooth)
    else:
        groups = {}
        for f, i in faces:
            mm = mat_of(f, i, [vmap.get(v, 0.0) for v in f.verts]) if vval is not None else mat_of(f, i)
            groups.setdefault(mm, []).append(f)
        for mm, fs in groups.items():
            post_faces(mb, fs, mm, smooth, uv=False)
        post_faces(mb, caps, m, smooth)
    return vr


def frame_y(tg, prev_n=None):
    """referencia: binormal ~ +Y (o arco vive num plano ~XZ) -> N (no plano do arco), B (de lado)"""
    Y = Vector((0.0, 1.0, 0.0))
    b = Y - tg * Y.dot(tg)
    if b.length < 1e-3:
        b = Vector((1.0, 0.0, 0.0)) - tg * tg.x
    b.normalize()
    n = b.cross(tg).normalized()
    return n, b


def frame_flat(tg, prev_side=None):
    """referencia para raizes/galhos rentes: lado horizontal (largura), N para cima (achatamento)"""
    Z = Vector((0.0, 0.0, 1.0))
    side = tg.cross(Z)
    if side.length < 0.25 and prev_side is not None:
        side = prev_side - tg * prev_side.dot(tg)
    if side.length < 1e-4:
        side = Vector((1.0, 0.0, 0.0))
    side.normalize()
    up = side.cross(tg).normalized()
    return side, up


def _hash01(*k):
    h = 0x811C9DC5
    for v in k:
        h ^= (int(v) & 0xffffffff)
        h = (h * 0x01000193) & 0xffffffff
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xffffffff
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xffffffff
    h ^= h >> 16
    return h / 4294967296.0


def _orient_out(fs, c):
    cv = Vector(c)
    for f in fs:
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - cv) < 0:      # normal para FORA (o material sai da normal)
            f.normal_flip()


# ================================================================== PRIMITIVAS DE FOLHAGEM V2 (tambem do op_veg)
def limb(mb, pts, radii, m=BARK, n=8, sub=3, caps=True, flat=1.0):
    """galho/tronco SUAVE: catmull pelos pontos, anel com referencial transportado (sem torcer), sombreado suave"""
    chain = [tuple(p)[:3] + (r,) for p, r in zip(pts, radii)]
    cv = Curve(chain, sub)
    rings = []
    side = None
    P = cv.P
    for i, (p, r) in enumerate(zip(P, cv.R)):
        tg = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)])
        if tg.length < 1e-6:
            tg = ZZ.copy()
        tg.normalize()
        if side is None:
            side = tg.cross(ZZ)
            if side.length < 0.2:
                side = tg.cross(Vector((1.0, 0.0, 0.0)))
        side = side - tg * side.dot(tg)
        if side.length < 1e-6:
            side = tg.orthogonal()
        side.normalize()
        up = tg.cross(side).normalized()
        rings.append([p + (side * math.cos(TAU * k / n) + up * math.sin(TAU * k / n) * flat) * max(r, 0.05)
                      for k in range(n)])
    skin(mb, rings, m, cap0=caps, cap1=caps)


PAD_HI = ((0.0, -0.20), (0.5, -0.18), (0.82, -0.10), (1.0, 0.10), (0.94, 0.40), (0.76, 0.68), (0.46, 0.88), (0.0, 1.0))
PAD_MID = ((0.0, -0.18), (0.66, -0.14), (1.0, 0.10), (0.9, 0.45), (0.62, 0.78), (0.0, 1.0))
PAD_LO = ((0.0, -0.16), (0.72, -0.12), (1.0, 0.12), (0.72, 0.66), (0.0, 1.0))


def cloud_pad(mb, c, R, H, rot=0.0, ax=1.0, lobes=9, seed=0, nt=36, prof=PAD_HI, mats=PAD_MATS, depth=0.16,
              lumps=3, ntop=0.42, nbot=-0.3, ry=None):
    """ALMOFADA DE PINHEIRO EM NUVEM: disco achatado (c = centro da base), borda em LOBOS com vinco entre eles, fundo
    quase plano, topo em domo com calombos. mats = (topo, lado, baixo) pela normal. Tris = 2*nt*(aneis-1) + 2*nt"""
    rng = random.Random(seed)
    ph, ph2 = rng.uniform(0, TAU), rng.uniform(0, TAU)
    cr, sr = math.cos(rot), math.sin(rot)
    ry = R if ry is None else ry
    lump = [(rng.uniform(-0.45, 0.45) * R * ax, rng.uniform(-0.4, 0.4) * ry, rng.uniform(0.12, 0.26) * H,
             rng.uniform(0.28, 0.42) * R) for _ in range(lumps)]
    c = Vector(c)
    bm = mb.bm

    def W(x, y, z):
        return bm.verts.new((c.x + x * cr - y * sr, c.y + x * sr + y * cr, c.z + z))

    def lz(x, y, zf):
        if zf <= 0.3:
            return 0.0
        return zf * sum(a * math.exp(-((x - lx) ** 2 + (y - ly) ** 2) / (w * w)) for lx, ly, a, w in lump)
    poles, rings = [], []
    for t, zf in prof:
        if t <= 0.0:
            poles.append(W(0.0, 0.0, zf * H + lz(0.0, 0.0, zf)))
            continue
        ring = []
        for j in range(nt):
            th = TAU * j / nt
            sc = abs(math.cos(lobes * th / 2 + ph)) ** 0.5
            rho = (1.0 - depth + depth * sc) * (1.0 + 0.07 * math.sin(2 * th + ph2))
            x, y = math.cos(th) * R * ax * t * rho, math.sin(th) * ry * t * rho
            z = zf * H + lz(x, y, zf) + (0.10 * H * sc * t if zf > 0.2 else 0.0)
            ring.append(W(x, y, z))
        rings.append(ring)
    fs = []
    bot, top = poles[0], poles[-1]
    for j in range(nt):
        j2 = (j + 1) % nt
        fs.append(bm.faces.new((rings[0][j2], rings[0][j], bot)))
        fs.append(bm.faces.new((rings[-1][j], rings[-1][j2], top)))
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(nt):
            j2 = (j + 1) % nt
            fs.append(bm.faces.new((r0[j], r0[j2], r1[j2], r1[j])))
    _orient_out(fs, c + ZZ * H * 0.35)
    g = {}
    for f in fs:
        nz = f.normal.z
        m = mats[0] if nz > ntop else (mats[2] if nz < nbot else mats[1])
        g.setdefault(m, []).append(f)
    for m, ff in g.items():
        post_faces(mb, ff, m, smooth=True)
    return fs


class PuffRec:
    __slots__ = ("c", "rx", "ry", "rz", "bumps", "amp", "fb", "faces", "rot")

    def __init__(self):
        self.rot = 0.0


def _puff_r(d, bumps, amp, fb):
    m = 0.0
    for b, cw in bumps:
        f = (d.dot(b) - cw) / (1.0 - cw)
        if f > m:
            m = f
    r = 1.0 + amp * (m ** 0.6 if m > 0.0 else 0.0)
    if d.z < 0.0:
        r *= 1.0 - fb * (-d.z) ** 1.5
    return r, m


def puff(mb, c, rx, ry, rz, seed=0, nu=16, nv=8, nb=8, amp=0.30, wdeg=40.0, mats=None, fb=0.35, crease=0.14,
         top_bias=0.0):
    """CACHO: casca unica (esfera parametrica nu x nv) com nb CALOMBOS arredondados (sub-cachos) e VINCO entre eles
    (o maximo dos calombos, nao a soma); fundo achatado. mats = (luz, corpo, fundo/vinco): topo de calombo claro,
    vinco e baixo no tom fundo. Devolve PuffRec (para cull_inside). Tris = 2*nu*(nv-1)"""
    rng = random.Random(seed)
    k = 1.0 / (1.0 + amp * 0.55)
    bumps = [(Vector((0.0, 0.0, 1.0)), math.cos(math.radians(wdeg * 1.1)))]
    a0 = rng.uniform(0, TAU)
    for i in range(nb):
        z = rng.uniform(-0.3 + top_bias, 0.92)
        a = a0 + i * 2.39996 + rng.uniform(-0.3, 0.3)
        s = math.sqrt(max(0.0, 1.0 - z * z))
        bumps.append((Vector((s * math.cos(a), s * math.sin(a), z)),
                      math.cos(math.radians(wdeg * rng.uniform(0.8, 1.25)))))
    c = Vector(c)
    bm = mb.bm
    rot0 = rng.uniform(0, TAU)
    mval = {}

    def V(d):
        r, m = _puff_r(d, bumps, amp, fb)
        v = bm.verts.new(c + Vector((d.x * rx, d.y * ry, d.z * rz)) * (r * k))
        mval[v] = m
        return v
    top = V(Vector((0.0, 0.0, 1.0)))
    bot = V(Vector((0.0, 0.0, -1.0)))
    rows = []
    for j in range(1, nv):
        phi = math.pi * j / nv
        s, z = math.sin(phi), math.cos(phi)
        off = (j % 2) * math.pi / nu
        rows.append([V(Vector((s * math.cos(rot0 + off + TAU * i / nu), s * math.sin(rot0 + off + TAU * i / nu), z)))
                     for i in range(nu)])
    fs = []
    for i in range(nu):
        i2 = (i + 1) % nu
        fs.append(bm.faces.new((top, rows[0][i], rows[0][i2])))
        fs.append(bm.faces.new((bot, rows[-1][i2], rows[-1][i])))
    for r0, r1 in zip(rows, rows[1:]):
        for i in range(nu):
            i2 = (i + 1) % nu
            fs.append(bm.faces.new((r0[i], r1[i], r1[i2])))
            fs.append(bm.faces.new((r0[i], r1[i2], r0[i2])))
    _orient_out(fs, c)
    mats = mats or ("Flower_OP_Light", "Flower_OP_Blossom", "Flower_OP_Deep")
    g = {}
    for f in fs:
        nz = f.normal.z
        am = sum(mval[v] for v in f.verts) / len(f.verts)
        if nz < -0.42 or (am < crease and nz < 0.8):
            m = mats[2]
        elif nz > 0.45 and am > 0.3:
            m = mats[0]
        else:
            m = mats[1]
        g.setdefault(m, []).append(f)
    for m, ff in g.items():
        post_faces(mb, ff, m, smooth=True)
    rec = PuffRec()
    rec.c, rec.rx, rec.ry, rec.rz, rec.bumps, rec.amp, rec.fb, rec.faces = c, rx * k, ry * k, rz * k, bumps, amp, fb, fs
    return rec


def _inside(rec, q, shrink=0.95):
    d = q - rec.c
    if rec.rot:
        cr, sr = math.cos(rec.rot), math.sin(rec.rot)
        d = Vector((d.x * cr + d.y * sr, -d.x * sr + d.y * cr, d.z))
    d = Vector((d.x / rec.rx, d.y / rec.ry, d.z / rec.rz))
    ln = d.length
    if ln < 1e-6:
        return True
    if ln > 1.0 + rec.amp + 0.05:
        return False
    r, _ = _puff_r(d / ln, rec.bumps, rec.amp, rec.fb)
    return ln < r * shrink


def cull_inside(mb, recs):
    """apaga as faces de um cacho que ficam INTEIRAS dentro de outro cacho da mesma planta (nunca vistas)"""
    dead = []
    for i, rec in enumerate(recs):
        others = [o for j, o in enumerate(recs) if j != i]
        if not others:
            continue
        for f in rec.faces:
            if f.is_valid and all(any(_inside(o, v.co) for o in others) for v in f.verts):
                dead.append(f)
    if dead:
        vs = {v for f in dead for v in f.verts}
        bmesh.ops.delete(mb.bm, geom=dead, context="FACES_ONLY")
        loose = [v for v in vs if v.is_valid and not v.link_faces]
        if loose:
            bmesh.ops.delete(mb.bm, geom=loose, context="VERTS")
    return len(dead)


# resolucao (nu, nv) por LOD: corpo / cacho (nivel B) / sub-cacho (nivel C)
FLUFFY_RES = {2: ((11, 5), (9, 5), (7, 4)), 1: ((9, 4), (8, 4), (6, 3)), 0: ((7, 3), (6, 3), (5, 3))}


def ico(mb, c, rx, ry, rz, sub, m, rot=0.0):
    """esfera-cacho: icosfera (sub 0 = 20 tris, sub 1 = 80) achatada embaixo, 1 material, SOMBREADO SUAVE"""
    c = Vector(c)
    M = Matrix.LocRotScale(c, Euler((0.0, 0.0, rot)), Vector((rx, ry, rz)))
    res = bmesh.ops.create_icosphere(mb.bm, subdivisions=sub, radius=1.0, matrix=M)
    vs = res["verts"]
    for v in vs:
        if v.co.z < c.z:
            v.co.z = c.z - (c.z - v.co.z) * 0.8
    fs = list({f for v in vs for f in v.link_faces})
    _orient_out(fs, c)
    post_faces(mb, fs, m, smooth=True)
    rec = PuffRec()
    rec.c, rec.rx, rec.ry, rec.rz, rec.bumps, rec.amp, rec.fb, rec.faces = c, rx, ry, rz, [], 0.0, 0.2, fs
    return rec


def fluffy_crown(mb, parts, seed, lod, mats, hang=0.35):
    """COPA FOFA (cerejeira V2b, moita): massa CHEIA + borda de cachos, tudo esfera de baixa resolucao com SOMBREADO
    SUAVE (f.smooth; o export_roblox fatia por material num bmesh que mantem o smooth da face e o FBX sai com as
    normais de vertice, que o Roblox usa; Leaf_/Flower_ saem com CastShadow=false). 3 NIVEIS por parte
    (centro, (rx, ry, rz), nB, nC):
      A CORPO (0,86 da parte, tom fundo): a massa densa sem buraco; e o miolo escuro entre os cachos e o baixo;
      B nB CACHOS (0,32..0,45 da parte) na metade de cima/fora da casca: o volume fofo e a silhueta lobada;
      C nC SUB-CACHOS (0,16..0,24) na borda de baixo, parte deles PENDENDO: a borda recortada / 'chorao'.
    TOM POR ESFERA (1 material por esfera: sem remendo triangular nem quebra de normal dentro dela), pela altura
    relativa na copa + jitter: cachos do alto claros (mats[0]), do meio (mats[1]); corpo e sub-cachos baixos no
    fundo (mats[2]) -> de cima a copa e clara com o miolo mais escuro. Faces escondidas cortadas (cull_inside)."""
    rng = random.Random(seed)
    rA, rB, rC = FLUFFY_RES[lod]
    zb = min(c[2] - r[2] for c, r, nb, nc in parts)
    zt = max(c[2] + r[2] for c, r, nb, nc in parts)
    hz = max(1e-3, zt - zb)
    recs, bodies = [], []

    def tone(z, bias=0.0):
        zr = (z - zb) / hz + rng.uniform(-0.1, 0.1) + bias
        return mats[0] if zr > 0.58 else (mats[2] if zr < 0.3 else mats[1])

    for c, (rx, ry, rz), nb, nc in parts:
        r = puff(mb, c, rx * 0.86, ry * 0.86, rz * 0.84, rng.randrange(1 << 30), rA[0], rA[1], nb=0, amp=0.0,
                 mats=(mats[2], mats[2], mats[2]), fb=0.35)
        recs.append(r)
        bodies.append(r)
    for pi, (c, (rx, ry, rz), nb, nc) in enumerate(parts):
        c = Vector(c)
        rm = (rx + ry + rz) / 3.0
        a0 = rng.uniform(0, TAU)
        if lod == 2:
            nb, nc = int(round(nb * 1.3)), int(round(nc * 1.3))
        for lvl, n, (z0, z1), shell, (k0, k1), res, bias in (("B", nb, (-0.15, 0.95), 0.8, (0.32, 0.45), rB, 0.08),
                                                               ("C", nc, (-0.7, 0.05), 0.9, (0.16, 0.24), rC, -0.05)):
            for i in range(n):
                z = z1 - (z1 - z0) * (i + 0.5) / max(1, n) + rng.uniform(-0.08, 0.08)
                a = a0 + i * 2.39996 + rng.uniform(-0.3, 0.3) + (0.7 if lvl == "C" else 0.0)
                sz = math.sqrt(max(0.0, 1.0 - z * z))
                d = Vector((sz * math.cos(a), sz * math.sin(a), z))
                q = c + Vector((d.x * rx, d.y * ry, d.z * rz)) * shell
                if lvl == "C" and rng.random() < hang:
                    q.z -= rz * rng.uniform(0.08, 0.18)                    # sub-cacho PENDENTE
                if any(j != pi and _inside(bodies[j], q, 0.8) for j in range(len(bodies))):
                    continue
                br = rm * rng.uniform(k0, k1)
                recs.append(puff(mb, q, br, br * rng.uniform(0.9, 1.06), br * rng.uniform(0.84, 0.96),
                                 rng.randrange(1 << 30), res[0], res[1], nb=0, amp=0.0,
                                 mats=(tone(q.z, bias),) * 3, fb=0.2))
    cull_inside(mb, recs)
    return recs


def blob_crown(mb, parts, seed, res, mats, core_res=(8, 4), core_k=0.8, blob_k=(0.42, 0.55)):
    """COPA DE CACHOS (cerejeira / arvore verde): cada PARTE (centro, (rx, ry, rz), n_cachos) vira um NUCLEO suave
    (core_k do tamanho, tom fundo: o miolo e a sombra de baixo) coberto por n CACHOS suaves (elipsoides lisas de
    1 material cada) na metade de cima/fora: contorno em calombos de tamanhos variados, vinco natural entre eles.
    TOM POR CACHO (nao por face: nada de remendo triangular) pela altura relativa na copa: alto = luz, meio = corpo,
    baixo = fundo. mats = (luz, corpo, fundo). Faces escondidas entre cachos/nucleos sao cortadas (cull_inside)"""
    rng = random.Random(seed)
    zb = min(c[2] - r[2] for c, r, n in parts)
    zt = max(c[2] + r[2] for c, r, n in parts)
    hz = max(1e-3, zt - zb)
    recs = []
    for c, (rx, ry, rz), nb in parts:
        if nb <= 0:                    # parte pequena = 1 cacho so, do tamanho da parte (tom pela altura)
            zr = (c[2] - zb) / hz
            m = mats[0] if zr > 0.66 else (mats[2] if zr < 0.3 else mats[1])
            recs.append(puff(mb, c, rx, ry, rz, rng.randrange(1 << 30), res[0], res[1], nb=0, amp=0.0,
                             mats=(m, m, m), fb=0.25))
            continue
        recs.append(puff(mb, c, rx * core_k, ry * core_k, rz * core_k, rng.randrange(1 << 30), core_res[0],
                         core_res[1], nb=0, amp=0.0, mats=(mats[2], mats[2], mats[2]), fb=0.3))
    for pi, (c, (rx, ry, rz), nb) in enumerate(parts):
        c = Vector(c)
        a0 = rng.uniform(0, TAU)
        rm = (rx + ry + rz) / 3.0
        for i in range(nb):
            z = 0.92 - 1.15 * (i + 0.5) / nb + rng.uniform(-0.12, 0.12)
            a = a0 + i * 2.39996 + rng.uniform(-0.35, 0.35)
            sz = math.sqrt(max(0.0, 1.0 - z * z))
            d = Vector((sz * math.cos(a), sz * math.sin(a), z))
            q = c + Vector((d.x * rx, d.y * ry, d.z * rz)) * 0.68
            if any(j != pi and _inside(recs[j], q, 0.85) for j in range(len(parts))):
                continue
            br = rm * rng.uniform(*blob_k)
            zr = (q.z - zb) / hz + rng.uniform(-0.1, 0.1)
            m = mats[0] if zr > 0.66 else (mats[2] if zr < 0.3 else mats[1])
            recs.append(puff(mb, q, br, br * rng.uniform(0.9, 1.05), br * rng.uniform(0.8, 0.92),
                             rng.randrange(1 << 30), res[0], res[1], nb=0, amp=0.0, mats=(m, m, m), fb=0.2))
    cull_inside(mb, recs)
    return recs


# ================================================================== PRIMITIVAS V3 (rodada 2 do usuario: "falta amor")
# Leitura de ARVORE ESTILIZADA DE ANIME (ref_02/ref_03), nao de gerador:
#   blob()        elipsoide suave com a cor em FAIXAS horizontais (topo claro / corpo / barriga escura): fronteira de cor
#                 = linha limpa entre aneis (cel-shading), nunca remendo triangular. Cacho da cerejeira, massa da larga.
#   bark_limb()   tronco/galho com CORDOES torcidos (casca marcada pela sombra, sem textura) e pe alargado.
#   root_claws()  raizes que AGARRAM o chao: saem do pe, deitam e entram na terra.
#   pine_pad()    camada de pinheiro em nuvem: fundo chato escuro, borda lobada, topo convexo, e a FRANJA de agulhas
#                 (tufos pontudos virados para fora/baixo na borda) - a assinatura do kuromatsu do anime.
#   pine_cloud()  conjunto de almofadas na ponta de um galho: camada de base larga + sub-almofadas no topo + capuz
#                 claro; gradiente topo amarelado -> base escura. Usado pelos kuromatsu do op_veg E pela arvore monumental.
def _rz(x, y, rot):
    c, s = math.cos(rot), math.sin(rot)
    return x * c - y * s, x * s + y * c


def blob(mb, c, rx, ry, rz, nu=8, nv=5, mats=("Flower_OP_Light", "Flower_OP_Blossom", "Flower_OP_Deep"),
         bands=(0.45, -0.25), fb=0.3, rot=0.0, wob=0.0, seed=0, top_tilt=None, sq=0.0):
    """ELIPSOIDE SUAVE EM FAIXAS (c = centro). Aneis ALINHADOS (sem defasagem): a face entre os aneis j e j+1 recebe a
    cor da faixa da latitude media -> topo mats[0] (z > bands[0]), corpo mats[1], barriga mats[2] (z < bands[1]).
    fb achata a barriga; wob = calombo de baixa frequencia (silhueta menos 'bola'); top_tilt = Vector: o 'topo' da
    faixa clara inclina para o lado de fora da copa (luz da borda). Tris = 2 * nu * (nv - 1). Devolve PuffRec"""
    c = Vector(c)
    bm = mb.bm
    rng = random.Random(seed)
    ph = rng.uniform(0, TAU)
    off = Vector((rng.uniform(-50, 50), rng.uniform(-50, 50), rng.uniform(-50, 50)))
    up = ZZ if top_tilt is None else (ZZ + top_tilt).normalized()

    def rad(d):
        r = 1.0
        if sq:                                             # superelipsoide: cupula 'podada' (karikomi)
            r /= (abs(d.x) ** sq + abs(d.y) ** sq + abs(d.z) ** sq) ** (1.0 / sq)
        if wob:
            r += wob * noise.noise(d * 1.3 + off)
        if d.z < 0.0:
            r *= 1.0 - fb * (-d.z) ** 1.5
        return r

    def P(d):
        r = rad(d)
        x, y = _rz(d.x * rx * r, d.y * ry * r, rot)
        return bm.verts.new(c + Vector((x, y, d.z * rz * r)))
    top = P(Vector((0.0, 0.0, 1.0)))
    bot = P(Vector((0.0, 0.0, -1.0)))
    rows, dirs = [], []
    for j in range(1, nv):
        phi = math.pi * j / nv
        s, z = math.sin(phi), math.cos(phi)
        ds = [Vector((s * math.cos(ph + TAU * i / nu), s * math.sin(ph + TAU * i / nu), z)) for i in range(nu)]
        dirs.append(ds)
        rows.append([P(d) for d in ds])
    g = {}

    def band(dv):
        z = sum(dv, Vector()).normalized().dot(up)
        return mats[0] if z > bands[0] else (mats[2] if z < bands[1] else mats[1])
    for i in range(nu):
        i2 = (i + 1) % nu
        f = bm.faces.new((top, rows[0][i], rows[0][i2]))
        g.setdefault(band([ZZ, dirs[0][i], dirs[0][i2]]), []).append(f)
        f = bm.faces.new((bot, rows[-1][i2], rows[-1][i]))
        g.setdefault(band([-ZZ, dirs[-1][i], dirs[-1][i2]]), []).append(f)
    for j in range(len(rows) - 1):
        r0, r1 = rows[j], rows[j + 1]
        for i in range(nu):
            i2 = (i + 1) % nu
            f = bm.faces.new((r0[i], r1[i], r1[i2], r0[i2]))
            g.setdefault(band([dirs[j][i], dirs[j + 1][i], dirs[j + 1][i2], dirs[j][i2]]), []).append(f)
    fs = [f for ff in g.values() for f in ff]
    _orient_out(fs, c)
    for m, ff in g.items():
        post_faces(mb, ff, m, smooth=True)
    rec = PuffRec()
    rec.c, rec.rx, rec.ry, rec.rz, rec.bumps, rec.amp, rec.fb, rec.faces = c, rx, ry, rz, [], 0.0, fb, fs
    rec.rot = rot
    return rec


def bark_limb(mb, pts, radii, m=BARK, n=7, sub=3, caps=True, ridges=3, ridge_amp=0.10, twist=0.6, flat=1.0,
              m2=None):
    """tronco/galho com CORDOES TORCIDOS: o anel e r * (1 + ridge_amp * cos(ridges * th + giro)); o giro cresce com o
    comprimento (twist voltas no total) -> espirais de luz e sombra (casca marcada sem textura). Sombreado suave.
    m2 = material do fundo dos sulcos (opcional; so em pecas-heroi)"""
    chain = [tuple(p)[:3] + (r,) for p, r in zip(pts, radii)]
    cv = Curve(chain, sub)
    rings, vals = [], []
    side = None
    P = cv.P
    for i, (p, r) in enumerate(zip(P, cv.R)):
        tg = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)])
        if tg.length < 1e-6:
            tg = ZZ.copy()
        tg.normalize()
        if side is None:
            side = tg.cross(ZZ)
            if side.length < 0.2:
                side = tg.cross(Vector((1.0, 0.0, 0.0)))
        side = side - tg * side.dot(tg)
        if side.length < 1e-6:
            side = tg.orthogonal()
        side.normalize()
        upv = tg.cross(side).normalized()
        u = cv.S[i] / max(cv.len, 1e-6)
        gw = TAU * twist * u
        ring, rv = [], []
        for k in range(n):
            th = TAU * k / n
            cs = math.cos(ridges * th + gw)
            rr = max(r, 0.05) * (1.0 + ridge_amp * cs)
            ring.append(p + (side * math.cos(th) + upv * math.sin(th) * flat) * rr)
            rv.append(-cs)
        rings.append(ring)
        vals.append(rv)
    if m2:
        skin(mb, rings, m, cap0=caps, cap1=caps,
             mat_of=lambda f, i, vv: m2 if min(vv) > 0.55 else m, vval=vals)
    else:
        skin(mb, rings, m, cap0=caps, cap1=caps)


def root_claws(mb, base, r0, n, gz, rng, m=BARK, reach=3.4, a0=None, ns=4, sub=1, gfun=None):
    """RAIZES que agarram o chao: n raizes saem do pe (meia altura do alargamento), deitam por cima do chao (gz) e a
    ponta entra 0,8 na terra. Angulos espalhados com jitter; a mais longa do lado da inclinacao do tronco"""
    base = Vector(base)
    a0 = rng.uniform(0, TAU) if a0 is None else a0
    for k in range(n):
        a = a0 + TAU * k / n + rng.uniform(-0.35, 0.35)
        d = Vector((math.cos(a), math.sin(a), 0.0))
        L_ = r0 * reach * rng.uniform(0.75, 1.2) * (1.25 if k == 0 else 1.0)
        rr = r0 * rng.uniform(0.42, 0.55)
        if gfun is not None:                       # a raiz so deita onde o chao continua (nada pendurado na borda)
            tip = base + d * (r0 * 0.9 + L_)
            g = gfun(tip.x, tip.y)
            if g is None or abs(g - gz) > 0.5:
                continue
        pts = [base + d * r0 * 0.25 + ZZ * r0 * 1.1, base + d * (r0 * 0.9) + ZZ * r0 * 0.35,
               Vector((base.x, base.y, gz)) + d * (r0 * 0.9 + L_ * 0.5) + ZZ * rr * 0.25,
               Vector((base.x, base.y, gz)) + d * (r0 * 0.9 + L_) - ZZ * 0.8]
        limb(mb, pts, [rr * 1.25, rr, rr * 0.6, rr * 0.25], m, n=ns, sub=sub, caps=False, flat=0.7)


PAD_DEPTH_K = 1.45               # V4 (G6 'folhas da arvore grande'): festao 45% mais fundo em toda almofada de pinheiro
PAD3 = ((0.0, -0.10), (0.55, -0.14), (0.86, -0.08), (1.0, 0.08), (0.94, 0.36), (0.74, 0.64), (0.44, 0.86), (0.0, 0.96))
PAD3_LO = ((0.0, -0.10), (0.7, -0.10), (1.0, 0.08), (0.8, 0.52), (0.0, 0.9))


def pine_pad(mb, c, R, H, rot=0.0, ax=1.0, ry=None, lobes=7, depth=0.18, seed=0, nt=24, prof=PAD3,
             mats=("Leaf_OP", "Leaf_OP_Pine", "Leaf_OP_PineUnder"), teeth=1.0, tooth_m=None, tooth_len=None,
             lumps=2, tilt=None):
    """CAMADA DE PINHEIRO EM NUVEM (c = centro da base). Corpo: disco com borda em LOBOS e vinco entre eles, fundo
    quase chato, topo convexo com calombos; cor por ANEL (faixas limpas): topo mats[0], borda mats[1], fundo mats[2].
    FRANJA: tufos de agulha (piramides de 3 faces, sombreado duro) saindo da borda para fora e para BAIXO, longos nos
    lobos e curtos nos vincos (teeth = densidade; 0 = sem franja). tilt = Vector (o disco inclina: almofada de ponta de
    galho que cai). Tris = 2*nt*(aneis-1) + 2*nt + 3*tufos"""
    rng = random.Random(seed)
    ph, ph2 = rng.uniform(0, TAU), rng.uniform(0, TAU)
    ry = R if ry is None else ry
    c = Vector(c)
    bm = mb.bm
    lump = [(rng.uniform(-0.4, 0.4) * R * ax, rng.uniform(-0.35, 0.35) * ry, rng.uniform(0.14, 0.28) * H,
             rng.uniform(0.3, 0.45) * R) for _ in range(lumps)]
    tilt = tilt or Vector((0.0, 0.0, 0.0))

    depth = depth * PAD_DEPTH_K                    # V4: festao mais fundo (borda de NUVEM, nao disco)

    def lobe(th):
        return abs(math.cos(lobes * th / 2 + ph)) ** 0.45      # V4: lobo mais redondo (era ** 0,6)

    def rho(th):
        return (1.0 - depth + depth * lobe(th)) * (1.0 + 0.06 * math.sin(2 * th + ph2))

    def W(x, y, z):
        xr, yr = _rz(x, y, rot)
        return c + Vector((xr, yr, z + xr * tilt.x + yr * tilt.y))

    def lz(x, y, zf):
        if zf <= 0.3:
            return 0.0
        return zf * sum(a * math.exp(-((x - lx) ** 2 + (y - ly) ** 2) / (w * w)) for lx, ly, a, w in lump)
    poles, rings, rz_ = [], [], []
    for t, zf in prof:
        if t <= 0.0:
            poles.append(bm.verts.new(W(0.0, 0.0, zf * H + lz(0.0, 0.0, zf))))
            continue
        ring = []
        for j in range(nt):
            th = TAU * j / nt
            r_ = rho(th)
            x, y = math.cos(th) * R * ax * t * r_, math.sin(th) * ry * t * r_
            z = zf * H + lz(x, y, zf) + (0.16 * H * lobe(th) * t if zf > 0.2 else 0.0)   # V4: cada lobo e um calombo
            ring.append(bm.verts.new(W(x, y, z)))
        rings.append(ring)
        rz_.append(zf)
    bot, top = poles[0], poles[-1]
    nr = len(rings)
    # faixas por anel: fundo (ate o anel da borda, exclusive), borda (anel da borda -> 1o de cima), topo (resto)
    rim_i = max(range(nr), key=lambda i: [t for t, zf in prof if t > 0][i])
    g = {}

    def put(m, f):
        g.setdefault(m, []).append(f)
    for j in range(nt):
        j2 = (j + 1) % nt
        put(mats[2], bm.faces.new((rings[0][j2], rings[0][j], bot)))
        put(mats[0], bm.faces.new((rings[-1][j], rings[-1][j2], top)))
    for i in range(nr - 1):
        m = mats[2] if i < rim_i else (mats[1] if i == rim_i else mats[0])
        for j in range(nt):
            j2 = (j + 1) % nt
            put(m, bm.faces.new((rings[i][j], rings[i][j2], rings[i + 1][j2], rings[i + 1][j])))
    fs = [f for ff in g.values() for f in ff]
    _orient_out(fs, W(0.0, 0.0, H * 0.35))
    for m, ff in g.items():
        post_faces(mb, ff, m, smooth=True)
    # FRANJA de agulhas: na borda (anel rim_i), 1 tufo por vertice da borda (teeth=1) - longo no lobo, curto no vinco
    nteeth = 0
    if teeth > 0:
        tl = tooth_len if tooth_len is not None else max(0.4, 0.3 * H)
        tm = tooth_m or mats[1]
        zf_rim = [zf for t, zf in prof if t > 0][rim_i]
        ntt = max(5, int(round(nt * 1.5 * teeth)))
        tf = []
        for j in range(ntt):
            # V4: FRANJA EM 2 FIADAS desencontradas de tufos FINOS (0,42 do passo: o ceu passa entre eles) que abrem
            # para fora (agulha que espalha) - fiada de baixo longa, de cima curta e mais para dentro (camadas)
            row = j % 2
            th = TAU * (j + rng.uniform(-0.25, 0.25)) / ntt
            lb = lobe(th)
            ln = tl * (0.55 + 0.6 * lb) * (1.12 if row == 0 else 0.7) * rng.uniform(0.85, 1.12)
            dth = TAU / ntt * 0.42
            zb_ = zf_rim * H - 0.05 * H + (0.14 * H if row else 0.0)
            kk = 0.97 if row == 0 else 0.9
            pts = []
            for a, zz, k in ((th - dth, zb_, kk), (th + dth, zb_, kk), (th, zb_ + 0.24 * H, kk - 0.07)):
                r_ = rho(a) * k
                pts.append(W(math.cos(a) * R * ax * r_, math.sin(a) * ry * r_, zz))
            r_ = rho(th) * kk
            ox, oy = math.cos(th) * R * ax * r_, math.sin(th) * ry * r_
            o = Vector((ox, oy, 0.0)).normalized()
            sw = rng.uniform(-0.3, 0.3) * dth                       # a ponta torce de lado (tufo vivo)
            o = Vector((o.x * math.cos(sw) - o.y * math.sin(sw), o.x * math.sin(sw) + o.y * math.cos(sw), 0.0))
            tip = W(ox + o.x * ln * 0.68, oy + o.y * ln * 0.68, zb_ - ln * 0.78)
            vs = [bm.verts.new(p) for p in pts] + [bm.verts.new(tip)]
            for a_, b_ in ((0, 1), (1, 2), (2, 0)):
                tf.append(bm.faces.new((vs[a_], vs[b_], vs[3])))
            nteeth += 1
        for f in tf:
            f.normal_update()
            ctr = (f.verts[0].co + f.verts[1].co + f.verts[2].co) / 3.0
            if f.normal.dot(ctr - W(0.0, 0.0, zf_rim * H)) < 0:
                f.normal_flip()
        post_faces(mb, tf, tm, smooth=False)
        fs += tf
    return fs


def pine_cloud(mb, c, R, flat=0.42, rot=0.0, ax=1.25, seed=0, lod=1,
               mats=("Leaf_OP_Sun", "Leaf_OP", "Leaf_OP_Pine", "Leaf_OP_PineUnder"), nsub=None, droop=0.0,
               teeth=None):
    """NUVEM DE PINHEIRO na ponta de um galho (c = centro da base da camada de baixo): CAMADA DE BASE larga (fundo
    escuro mats[3], borda mats[2], topo mats[1], franja de agulhas mats[2]) + nsub SUB-ALMOFADAS sobre ela, recuadas
    para dentro e para cima (topo mats[0] amarelado, borda mats[1], fundo mats[2], franja curta) + CAPUZ claro no
    alto. Contorno composto (lobos grandes e pequenos), luz em cima, sombra embaixo - nunca disco liso.
    droop inclina a base para fora/baixo (ponta de galho que pesa). lod 0/1/2 = resolucao e franja"""
    rng = random.Random(seed)
    c = Vector(c)
    H = R * flat
    nt = {0: 10, 1: 12, 2: 20, 3: 30}[lod]
    if nsub is None:
        nsub = {0: 1, 1: 2, 2: 2, 3: 3}[lod] + (1 if R > 8.0 else 0)
    if teeth is None:
        teeth = {0: 0.5, 1: 0.85, 2: 1.0, 3: 1.0}[lod]
    prof = PAD3_LO                                   # V4: base BAIXA (fundo chato + borda); o volume vem dos pufes
    ex = Vector((math.cos(rot), math.sin(rot), 0.0))
    tilt = Vector((ex.x, ex.y, 0.0)) * (-droop)
    fs = pine_pad(mb, c, R, H * 0.9, rot, ax, None, lobes=7 if R > 6 else 6, depth=0.2, seed=rng.randrange(1 << 30), nt=nt,
                  prof=prof, mats=(mats[1], mats[1], mats[3]), teeth=teeth, tooth_m=mats[2],
                  lumps=3 if lod >= 2 else 1, tilt=tilt)
    # V4 (G6 'as folhas da arvore grande precisam melhorar'): o topo da nuvem deixa de ser sub-almofadas LISAS (lia
    # como bolo/pires empilhado, 'lump') e vira um BROCOLIS de pufes achatados (ref_02: cada nuvem do pinheiro e um
    # monte de calombos redondos claros em cima, fundo chato escuro com a franja de agulhas): anel de pufes sobre a
    # borda (contorno festonado de verdade) + pufes de dentro mais altos (cupula). Faixas: topo Sun, corpo Leaf, pe
    # Pine; luz inclinada para fora. Faces escondidas entre pufes saem (cull_inside).
    n_rim = {0: 3, 1: 4, 2: 7, 3: 9}[lod] + (2 if R > 15.0 else 0) + (1 if nsub and nsub >= 4 else 0)
    n_in = max(1, {0: 1, 1: 1, 2: 3, 3: 4}[lod] + (1 if R > 25.0 else 0))
    pres = {0: (5, 3), 1: (6, 4), 2: (9, 4), 3: (10, 5)}[lod]
    recs = []
    a0 = rng.uniform(0, TAU)

    def put(q, rr, rz, mt, bands, out):
        q.z += (q.x - c.x) * tilt.x + (q.y - c.y) * tilt.y           # acompanha a base inclinada
        tl = Vector((out.x, out.y, 0.0)) * 0.3 if out.length > 1e-6 else None
        recs.append(blob(mb, q, rr, rr * rng.uniform(0.88, 1.0), rz, pres[0], pres[1], mt, bands, fb=0.5,
                         rot=rng.uniform(0, TAU), wob=0.06, seed=rng.randrange(1 << 30), top_tilt=tl))
    k_r = 1.0 if n_rim >= 6 else (1.18 if n_rim >= 4 else 1.3)
    for k in range(n_rim):
        a = a0 + TAU * k / n_rim + rng.uniform(-0.18, 0.18)
        d = Vector((math.cos(a) * ax, math.sin(a), 0.0))
        rad = R * rng.uniform(0.64, 0.74)                        # sobre a BORDA (cobre a testa lisa da base)
        q = c + Vector(_rz(d.x * rad, d.y * rad, rot) + (0.0,)) + ZZ * H * rng.uniform(0.2, 0.32)
        rr = R * rng.uniform(0.27, 0.34) * k_r
        put(q, rr, rr * 0.62, (mats[0], mats[1], mats[2]), (0.62, -0.3), Vector(_rz(d.x, d.y, rot) + (0.0,)))
    for k in range(n_in):
        a = a0 + 0.6 + TAU * k / n_in + rng.uniform(-0.3, 0.3)
        d = Vector((math.cos(a) * ax, math.sin(a), 0.0))
        rad = R * (0.2 if n_in > 1 else 0.05) * rng.uniform(0.8, 1.2)
        q = c + Vector(_rz(d.x * rad, d.y * rad, rot) + (0.0,)) + ZZ * H * rng.uniform(0.68, 0.84)
        rr = R * rng.uniform(0.3, 0.38)
        put(q, rr, rr * 0.58, (mats[0], mats[1], mats[2]), (0.42, -0.35), Vector(_rz(d.x, d.y, rot) + (0.0,)))
    if R > 25.0:                                      # nuvem grande (coroa): anel do meio (sem miolo liso entre os aneis)
        for k in range(6):
            a = a0 + 0.3 + TAU * k / 6 + rng.uniform(-0.2, 0.2)
            d = Vector((math.cos(a) * ax, math.sin(a), 0.0))
            rad = R * rng.uniform(0.36, 0.44)
            q = c + Vector(_rz(d.x * rad, d.y * rad, rot) + (0.0,)) + ZZ * H * rng.uniform(0.5, 0.62)
            rr = R * rng.uniform(0.22, 0.27)
            put(q, rr, rr * 0.6, (mats[0], mats[1], mats[2]), (0.5, -0.3), Vector(_rz(d.x, d.y, rot) + (0.0,)))
    cull_inside(mb, recs)
    fs += [f for rc in recs for f in rc.faces if f.is_valid]
    return fs


# ------------------------------------------------------------------ chao real (raio para baixo)
class Ground:
    def __init__(self, x0, y0, x1, y1):
        vs, fs = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or o.name.startswith(("OP_Tree_", "COL_", "PREVIEW_", "SCALE_", "OP_Plz_OreProxy")):
                continue
            if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
                continue
            mw = o.matrix_world
            bb = [mw @ Vector(c) for c in o.bound_box]
            if max(b.x for b in bb) < x0 or min(b.x for b in bb) > x1 or max(b.y for b in bb) < y0 or min(b.y for b in bb) > y1:
                continue
            me = o.data
            co = [mw @ v.co for v in me.vertices]
            for p in me.polygons:
                pv = [co[i] for i in p.vertices]
                if max(v.x for v in pv) < x0 or min(v.x for v in pv) > x1 or max(v.y for v in pv) < y0 or min(v.y for v in pv) > y1:
                    continue
                base = len(vs)
                vs.extend(pv)
                fs.append(list(range(base, base + len(pv))))
        self.bvh = BVHTree.FromPolygons(vs, fs) if fs else None

    def z(self, x, y, top=CC + 16.0, floor=CC - 40.0):
        if self.bvh is None:
            return CC
        hit = self.bvh.ray_cast(Vector((x, y, top)), Vector((0.0, 0.0, -1.0)), top - floor)
        return hit[0].z if hit[0] is not None else floor


# ------------------------------------------------------------------ tronco
def _cdist(a, b, n):
    d = abs(a - b) % n
    return min(d, n - d)


def _trunk_rings(s0, s1, ds, fine):
    c = trunk_curve()
    n = NSIDE
    root_ang = [math.radians(a) for a, *_ in ROOTS]
    root_w = [lw for *_, lw in ROOTS]
    base_knots = [(0.4, CC + 9.0, 1.0), (2.6, CC + 15.0, 0.8), (4.4, CC + 5.0, 0.7)]     # (angulo, z, forca)
    rings, vals, svals = [], [], []
    steps = max(2, int(math.ceil((s1 - s0) / ds)))
    for i in range(steps + 1):
        s = s0 + (s1 - s0) * i / steps
        svals.append(s)
        p, r, tg = c.at(s)
        nv, bv = frame_y(tg)
        u = s / c.len
        h = max(0.0, p.z - CC)
        flare = 1.0 + 0.22 * math.exp(-h / 6.0)
        flare *= 1.0 + 0.07 * noise.noise(Vector((s / 26.0, 3.3, 1.1)))       # inchacos ao longo do tronco
        lob_f = 0.40 * math.exp(-h / 7.0)
        tw = TAU * TWIST * u                                             # a FIBRA: o anel inteiro gira com ela
        fade = 1.0 - 0.5 * u                                             # sulcos mais rasos para a ponta
        fz = [dep * (0.75 + 0.4 * max(-0.55, min(0.55, noise.noise(Vector((u * 7.0, fi * 3.7, 0.5))))))
              for fi, (kf, dep) in enumerate(FURROWS)]
        ring, rv = [], []
        for k in range(n):
            th = TAU * k / n + tw
            d = nv * math.cos(th) + bv * math.sin(th) * FLAT
            wa = math.atan2(d.y, d.x)
            m = flare
            for a, w in zip(root_ang, root_w):
                cs = math.cos(wa - a)
                if cs > 0:
                    m += lob_f * w * cs ** 10
            m += 0.11 * (1.0 - 0.4 * u) * math.cos(3 * TAU * k / n + 0.7)           # 3 cordoes torcidos
            g, core = 0.0, 0.0
            for (kf, dep), dz in zip(FURROWS, fz):
                dk = min(_cdist(k, kf, n), _cdist(k, kf + 1, n))           # sulco de FUNDO CHATO: 2 lados (kf, kf+1)
                if dk == 0:
                    g = max(g, dz)
                    core = max(core, dz)
                elif dk == 1:
                    g = max(g, dz * 0.35)
            m -= g * fade
            m += 0.03 * fade * (1.0 if any(_cdist(k, kf, n) == 3 for kf, _ in FURROWS) else 0.0)  # crista entre sulcos
            for ku, kk, ks, kl in KNOTS:
                dk = _cdist(k, kk * n, n) / (n * 0.07)
                dsn = (s - ku * c.len) / kl
                if abs(dsn) < 3.0:
                    m += ks * math.exp(-dk * dk - dsn * dsn)
            if fine:
                fa = max(0.0, min(1.0, (TIER_A_TOP - 2.0 - p.z) / 6.0))
                m += fa * 0.014 * math.sin(29 * TAU * k / n - 0.07 * p.z)
                # CASCA EM PLACAS (kuromatsu): cada faixa entre 2 sulcos e cortada por fendas horizontais a cada
                # 4-6 aneis (deslocadas por faixa) -> placas que leem sem textura onde o jogador chega perto
                if fa > 0.3:
                    j = k // 3                                      # placa = 3 lados; fendas DESENCONTRADAS
                    per = 4 + int(_hash01(j, 11) * 3)
                    ph = i + int(_hash01(j, 12) * per)
                    if ph % per in (0, 1) and _hash01(j, ph // per, 13) < 0.7:
                        m -= 0.045 * fa
                        core = max(core, GROOVE_T + 0.01)
                for ka, kz, kf in base_knots:
                    da = math.atan2(math.sin(th - ka), math.cos(th - ka))
                    m += fa * kf * 0.09 * math.exp(-(da / 0.32) ** 2 - ((p.z - kz) / 2.2) ** 2)
            ring.append(p + d * (r * m))
            rv.append(core * fade)
        rings.append(ring)
        vals.append(rv)
    return rings, vals, svals


def _groove_mat(f, i, vals):
    """so a face ENTRE os 2 lados do fundo do sulco (4 vertices no fundo) e escura: listra de 1 face, nitida"""
    return GROOVE if len(vals) == 4 and min(vals) > GROOVE_T else BARK


def trunk(mb_a, mb_b):
    c = trunk_curve()
    sA = 0.0
    while sA < c.len and c.at(sA)[0].z < TIER_A_TOP:
        sA += 0.25
    ra, va, sa = _trunk_rings(0.0, sA, 1.1, True)
    rb, vb, sb = _trunk_rings(sA, c.len, 2.9, False)
    skin(mb_a, ra + rb[1:], BARK, cap0=True, cap1=True, s_of=sa + sb[1:], mat_of=_groove_mat, vval=va + vb[1:])
    return sA


# ------------------------------------------------------------------ raizes
def _root_profile(ground, xy_r, flat, d_list=None, r_g=15.0, length=20.0, top0=CC + 16.0):
    """perfil de uma raiz: para cada (x, y, meia_largura) -> (centro z, meia_altura). Perto do tronco e CONTRAFORTE
    (lamina alta e estreita que sobe ate top0 e cai em curva); longe, deita no chao meio enterrada; obstaculo (muro,
    degrau) -> passa por CIMA (fundo 0,15 acima) e escorre pela face"""
    zc, hh = [], []
    for i, (x, y, rw) in enumerate(xy_r):
        g = ground.z(x, y)
        gmax = g
        rr = max(rw * 1.25, 1.6)
        for k in range(8):
            aa = 2 * math.pi * k / 8
            gmax = max(gmax, ground.z(x + math.cos(aa) * rr, y + math.sin(aa) * rr))
        top = g + rw * flat * 1.15
        if d_list is not None:
            u = max(0.0, min(1.0, (d_list[i] - 4.0) / (r_g - 4.0 + 0.75 * length)))
            top = max(top, g + (top0 - g) * (1.0 - u) ** 1.6)
        bot = g - rw * flat * 0.85
        if gmax > g + 0.8:
            bot = max(bot, gmax + 0.15)
            top = max(top, bot + 2.0 * rw * flat)
        zc.append((top + bot) / 2.0)
        hh.append((top - bot) / 2.0)
    for _ in range(2):
        n = len(zc)
        zc = [zc[0]] + [max(zc[i], (zc[i - 1] + 2 * zc[i] + zc[i + 1]) / 4.0) for i in range(1, n - 1)] + [zc[-1]]
        hh = [hh[0]] + [(hh[i - 1] + 2 * hh[i] + hh[i + 1]) / 4.0 for i in range(1, n - 1)] + [hh[-1]]
    return zc, hh


def roots(mb, ground, rng):
    bx, by = BASE_C
    col_segs = []
    r_g = 19.0                                                           # raio do tronco no chao (com alargamento)
    for ri, (ang, length, r0, flat, fork, lw) in enumerate(ROOTS):
        a = math.radians(ang)
        dx, dy = math.cos(a), math.sin(a)
        px, py = -dy, dx
        bend = (_hash01(ri, 7) - 0.5) * 0.5                              # curva lateral suave (raiz nao e reta)
        pts, ds = [], []
        nseg = int((r_g + length) / 1.3) + 1
        for i in range(nseg + 1):
            t = i / nseg
            d = 4.0 + (r_g + length - 4.0) * t
            lat = bend * length * math.sin(math.pi * t) * 0.6
            x, y = bx + dx * d + px * lat, by + dy * d + py * lat
            rw = r0 * (1.0 - 0.95 * t ** 0.9) + 0.18          # ponta fina (nao toco cortado)
            pts.append((x, y, rw))
            ds.append(d)
        g0 = ground.z(bx, by)
        for i, (x, y, rw) in enumerate(pts):
            if i > 3 and i + 2 < len(pts) and ground.z(x, y) > g0 + 3.0 and ground.z(*pts[i + 2][:2]) > g0 + 3.0:
                pts, ds = pts[:max(4, i - 1)], ds[:max(4, i - 1)]
                m = len(pts)
                pts = [(x2, y2, rw2 if j < m - 3 else rw2 * (0.75 - 0.2 * (j - m + 3))) for j, (x2, y2, rw2) in enumerate(pts)]
                break
        zc, hh = _root_profile(ground, pts, flat, ds, r_g, length)
        cpts = [Vector((x, y, z)) for (x, y, rw), z in zip(pts, zc)]
        rad = [rw for x, y, rw in pts]
        _root_skin(mb, cpts, rad, hh, 12)
        if fork:
            i0 = int(len(cpts) * 0.55)
            fa = a + (0.6 if _hash01(ri, 3) > 0.5 else -0.6)
            fl = length * 0.45
            nf = int(fl / 1.3) + 1
            fpts = []
            for i in range(nf + 1):
                t = i / nf
                fpts.append((cpts[i0].x + math.cos(fa) * fl * t, cpts[i0].y + math.sin(fa) * fl * t,
                             rad[i0] * 0.62 * (1.0 - 0.8 * t) + 0.3))
            fz, fh = _root_profile(ground, fpts, flat)
            fz[0], fh[0] = cpts[i0].z, min(fh[0], hh[i0] * 0.8)
            _root_skin(mb, [Vector((x, y, z)) for (x, y, r), z in zip(fpts, fz)], [r for x, y, r in fpts], fh, 9)
        for p, r, h in zip(cpts, rad, hh):
            col_segs.append((p, r, h))
    return col_segs


def _root_skin(mb, cpts, rad, hh, n):
    """secao eliptica: largura rad (lado horizontal), altura hh (contraforte alto perto do tronco, achatada longe);
    2 sulcos rasos no dorso (a fibra do tronco continua na raiz)"""
    rings = []
    prev = None
    for i, p in enumerate(cpts):
        tg = (cpts[min(i + 1, len(cpts) - 1)] - cpts[max(i - 1, 0)]).normalized()
        side, up = frame_flat(tg, prev)
        prev = side
        ring = []
        for k in range(n):
            th = 2 * math.pi * k / n
            w = 1.0 + 0.06 * math.sin(3 * th + i * 0.4) - 0.08 * max(0.0, math.cos(4 * th - 0.4)) ** 6
            sq = 1.0 - 0.35 * max(0.0, math.sin(th)) * min(1.0, hh[i] / max(rad[i], 0.1) - 0.6)
            ring.append(p + side * (math.cos(th) * rad[i] * w * max(0.45, sq)) + up * (math.sin(th) * hh[i] * w))
        rings.append(ring)
    skin(mb, rings, BARK, cap0=True, cap1=True)


# ------------------------------------------------------------------ galhos + almofadas
def branches(mb):
    """galhos GROSSOS que nascem DENTRO do tronco, com leve sulco escuro no dorso; devolve as pontas"""
    out = []
    for bi, (att, pts) in enumerate(BRANCHES):
        p, r, tg = trunk_nearest(att)
        r0 = min(r * 0.5, pts[0][3] * 1.3)
        chain = [(p.x, p.y, p.z, r0)] + list(pts)
        limb(mb, [q[:3] for q in chain], [q[3] for q in chain], BARK, n=10, sub=4)
        out.append(Vector(pts[-1][:3]))
    return out


def _cluster_rot(ci):
    c = Vector(MASSES[ci][0])
    best = min(BRANCHES, key=lambda b: (Vector(b[1][-1][:3]) - c).length)
    a = Vector(best[0])
    d = Vector((c.x - a.x, c.y - a.y, 0.0))
    return math.atan2(d.y, d.x) if d.length > 3.0 else 0.0


PAD_MATS4 = ("Leaf_OP_Sun", "Leaf_OP", "Leaf_OP_Pine", "Leaf_OP_PineUnder")   # V3: topo amarelado -> fundo escuro


def canopy(mb_pads, mb_twig, rng):
    """V3 (rodada 2: 'a arvore grande melhorou bastante, porem suas folhas precisam melhorar'): cada MASSA = NUVEM DE
    PINHEIRO EM CAMADAS (pine_cloud): camada de base larga com FRANJA DE AGULHAS e fundo escuro, sub-almofadas claras
    por cima e capuz amarelado; + satelites (nuvens menores, alternando os 2 lados ao longo do galho, mais baixos e
    caindo para fora) -> contorno lobado composto, luz em cima (Leaf_OP_Sun), sombra embaixo (Leaf_OP_PineUnder).
    Raminhos curtos por baixo ligam cada satelite ao galho (a estrutura aparece de baixo, como no anime)"""
    k = 0
    for ci, (c, R, flat, n, ax, note) in enumerate(MASSES):
        c = Vector(c)
        H = R * flat
        rot = _cluster_rot(ci)
        ex = Vector((math.cos(rot), math.sin(rot), 0.0))
        ey = Vector((-ex.y, ex.x, 0.0))
        big = R >= 15.0
        pine_cloud(mb_pads, c, R, 0.44, rot, ax, seed=ci * 31, lod=2 if big else 1, mats=PAD_MATS4,
                   nsub=5 if R >= 25 else (3 if big else 2))
        k += 1
        s0 = 1.0 if _hash01(ci, 5) > 0.5 else -1.0
        for j in range(n):
            side = s0 if j % 2 == 0 else -s0
            rank = j // 2
            a = (0.0 if side > 0 else math.pi) + (_hash01(ci, j, 1) - 0.5) * 1.2 + (0.9 * rank * side)
            d = Vector((math.cos(a), math.sin(a), 0.0))
            off = ex * d.x * R * ax * (0.74 + 0.1 * rank) + ey * d.y * R * (0.76 + 0.1 * rank)
            rr = R * (0.6 - 0.08 * rank) * (0.9 + 0.2 * _hash01(ci, j, 2))
            dz = -H * (0.22 + 0.24 * rank) + H * 0.25 * (_hash01(ci, j, 3) - 0.5)
            pc = c + off + ZZ * dz
            ra = math.atan2(off.y, off.x)
            pine_cloud(mb_pads, pc, rr, 0.46, ra, 1.2, seed=ci * 31 + j + 1, lod=1, mats=PAD_MATS4,
                       nsub=2, droop=0.08 + 0.04 * rank)
            k += 1
            a_ = c + (pc - c) * 0.2 - ZZ * H * 0.1
            b_ = pc + ZZ * rr * 0.46 * 0.1
            mid = a_.lerp(b_, 0.5) - ZZ * 1.2
            limb(mb_twig, [a_, mid, b_], [max(0.9, R * 0.07), max(0.7, R * 0.05), max(0.45, R * 0.035)], BARK,
                 n=6, sub=2, caps=False)
    return k


# ------------------------------------------------------------------ rocha da base
def base_rocks(mb, ground, rng):
    """rocha do castelo onde a base pega: blocos facetados (pedra, nao inflavel) fora do muro, no degrau entre o
    patio (136,2) e a rocha do fundo (120 / 150), e 2 lajes baixas dentro do patio sob as raizes"""
    spots = [(76.0, 438.0, 9.5, 1.2), (80.0, 456.0, 10.5, 1.3), (70.0, 472.0, 8.0, 1.0)]
    for i, (x, y, r, hz) in enumerate(spots):
        g = ground.z(x, y)
        zc = min(g, CC) + r * hz * 0.25
        res = bmesh.ops.create_icosphere(mb.bm, subdivisions=1, radius=r,
                                         matrix=Matrix.LocRotScale(Vector((x, y, zc)),
                                                                   Euler((0.0, 0.0, rng.uniform(0, 6.28))),
                                                                   Vector((1.0, 0.82, hz * 0.62))))
        vs = res["verts"]
        for v in vs:
            nn = noise.noise_vector(v.co * 0.18 + Vector((i * 3.1, i * 1.7, 0.0)))
            v.co += nn * r * 0.16
        fs = list({f for v in vs for f in v.link_faces})
        for f in fs:
            f.normal_update()
        post_faces(mb, [f for f in fs if f.normal.z > 0.62], "Cliff_OP_Moss", smooth=False)
        post_faces(mb, [f for f in fs if f.normal.z <= 0.62], "Cliff_OP", smooth=False)


# ------------------------------------------------------------------ colisao (so o alcance do jogador)
def _in_court(x, y):
    return L.point_in_poly(x, y, L.COURT)


def collision(col_segs):
    bx, by = BASE_C
    for k, ang in enumerate((0.0, math.pi / 4)):
        col_box("OP_TreeTrunk", (23.0, 23.0, 28.0), (bx, by, CC + 14.0), (0, 0, ang))
    col_box("OP_TreeTrunk", (20.0, 20.0, 16.0), (bx + 3.0, by - 1.5, CC + 34.0), (0, 0, math.pi / 8))
    n = 0
    run = []

    def flush():
        nonlocal n
        if len(run) < 2:
            run.clear()
            return
        a, b = run[0], run[-1]
        d = b[0] - a[0]
        ln = max(1.0, Vector((d.x, d.y)).length)
        w = max(q[1] for q in run) * 1.7
        top = max(q[0].z + q[2] for q in run)
        h = top - CC
        if h > 0.9:
            c = (a[0] + b[0]) / 2
            col_box("OP_TreeRoot", (ln + w * 0.5, w, h), (c.x, c.y, CC + h / 2), (0, 0, math.atan2(d.y, d.x)))
            n += 1
        run.clear()
    prev = None
    for p, r, fl in col_segs:
        dist = math.hypot(p.x - bx, p.y - by)
        ok = _in_court(p.x, p.y) and dist > 10.0 and p.z < CC + 8.0
        if prev is not None and (p - prev).length > 3.0:
            flush()
        if ok:
            run.append((p, r, fl))
            if len(run) >= 5:
                flush()
        else:
            flush()
        prev = p
    flush()
    return n


# ------------------------------------------------------------------ conferencia contra o castelo
def check_castle(verbose=True):
    """BVH: interseccao das malhas OP_Tree_* com as malhas OP_Cas_* (blockout ou op_castle) + folga das capsulas do
    tronco/galhos e da copa contra castle_envelope(). Encontros dentro do TREE_KEEPOUT (muro engolido pela base)
    sao listados a parte: o op_castle deve terminar o muro ali."""
    def bvh_of(prefix):
        vs, fs = [], []
        for o in bpy.data.objects:
            if o.type == "MESH" and o.name.startswith(prefix):
                mw = o.matrix_world
                base = len(vs)
                vs.extend(mw @ v.co for v in o.data.vertices)
                fs.extend([base + i for i in p.vertices] for p in o.data.polygons)
        return (BVHTree.FromPolygons(vs, fs), vs, fs) if fs else (None, vs, fs)
    tb, tv, tf = bvh_of("OP_Tree_")
    cb, cv, cf = bvh_of("OP_Cas_")
    hard, wall, floor = 0, 0, 0
    where = []
    if tb and cb:
        for i, j in tb.overlap(cb):
            c = sum((tv[k] for k in tf[i]), Vector()) / len(tf[i])          # onde a ARVORE encosta
            if max(cv[k].z for k in cf[j]) <= CC + 0.45:
                floor += 1          # M6b: raiz meio enterrada no PISO do patio (lajes/cascalho do op_castle) = esperado
            elif L.point_in_poly(c.x, c.y, TREE_KEEPOUT) and c.z < CC + 30.0:
                wall += 1
            else:
                hard += 1
                if len(where) < 6:
                    where.append("(%.0f,%.0f,%.0f)" % tuple(c))
    env = castle_envelope()
    worst = (1e9, "")
    for (a, b, r) in tree_envelope()["capsules"]:
        for t in (0.0, 0.25, 0.5, 0.75, 1.0):
            p = Vector(a).lerp(Vector(b), t)
            for nm, (x0, y0, z0, x1, y1, z1) in env:
                dx = max(x0 - p.x, 0.0, p.x - x1)
                dy = max(y0 - p.y, 0.0, p.y - y1)
                dz = max(z0 - p.z, 0.0, p.z - z1)
                d = math.sqrt(dx * dx + dy * dy + dz * dz) - r
                if d < worst[0]:
                    worst = (d, nm)
    for c, (rx, ry, rz) in tree_envelope()["blobs"]:
        for nm, (x0, y0, z0, x1, y1, z1) in env:
            # elipsoide da copa x caixa: distancia da caixa ao centro, descontado o raio da elipsoide nessa direcao
            dx = max(x0 - c[0], 0.0, c[0] - x1)
            dy = max(y0 - c[1], 0.0, c[1] - y1)
            dz = max(z0 - c[2], 0.0, c[2] - z1)
            dd = math.sqrt(dx * dx + dy * dy + dz * dz)
            if dd < 1e-6:
                worst = min(worst, (-1.0, nm + " (copa)"))
                continue
            re = 1.0 / math.sqrt((dx / dd / rx) ** 2 + (dy / dd / ry) ** 2 + (dz / dd / rz) ** 2)
            if dd - re < worst[0]:
                worst = (dd - re, nm + " (copa)")
    ok = hard == 0 and worst[0] >= CLEAR_CASTLE
    if verbose:
        print(("OK   " if ok else "FAIL ") + "OP_TREE castelo: %d interseccoes fora da base %s | %d encontros base x muro "
              "(no TREE_KEEPOUT: o op_castle termina o muro ali) | %d raizes assentadas no piso do patio | folga minima "
              "tronco/galho/copa -> castelo %.1f (%s)" % (hard, " ".join(where), wall, floor, worst[0], worst[1]))
    return ok, hard, wall, worst


def stats(verbose=True):
    tris, mps, objs = 0, 0, 0
    import studio_op
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("OP_Tree_"):
            objs += 1
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
            mps += studio_op.est_meshparts(o)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith(("COL_OP_TreeTrunk", "COL_OP_TreeRoot")))
    top = max(((o.matrix_world @ v.co).z for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("OP_Tree_")
               for v in o.data.vertices), default=0.0)
    if verbose:
        print("OP_TREE orcamento: tris %d / 40000 | MeshParts~ %d / 30 | objetos %d | colisoes %d | topo %.1f" % (
            tris, mps, objs, ncol, top))
    return tris, mps, ncol, top


# ------------------------------------------------------------------ build
def build():
    global _TRUNK_C
    _TRUNK_C = None
    noise.seed_set(5505)
    rng = random.Random(4105)
    ground = Ground(10.0, 405.0, 110.0, 500.0)
    mb_a = MB("OP_Tree_Trunk", "04_CASTLE", rng, detail="hero", floor=-999)
    mb_b = MB("OP_Tree_Branches", "04_CASTLE", rng, detail="far", floor=-999)
    trunk(mb_a, mb_b)
    segs = roots(mb_a, ground, rng)
    base_rocks(mb_a, ground, rng)
    mb_a.finish()
    branches(mb_b)
    mc = MB("OP_Tree_Pads", "04_CASTLE", rng, detail="far", floor=-999)
    canopy(mc, mb_b, rng)
    mb_b.finish()
    op = mc.finish()
    if op is not None:
        op.visible_shadow = False      # previa = Roblox (Leaf_ CastShadow=false no fm_lib.RBX_RULES)
    collision(segs)
    stats()
    check_castle()


# ------------------------------------------------------------------ cameras da arvore (folhas M3)
def cams():
    e = L.EYE
    tgt = (8.0, 425.0, CC + 70.0)
    return {
        "CAM_OP_Tree_Ponte": ((0.0, -100.0, L.DECK + 0.6 + e), tgt, 22),
        "CAM_OP_Tree_PonteZoom": ((0.0, -100.0, L.DECK + 0.6 + e), tgt, 60),
        "CAM_OP_Tree_Torii": ((0.0, 24.0, L.T0 + e), tgt, 22),
        "CAM_OP_Tree_Praca": ((0.0, 216.0, L.P + e), tgt, 22),
        "CAM_OP_Tree_Patio": ((40.0, 377.0, CC + e), (56.0, 449.0, CC + 30.0), 22),
        "CAM_OP_Tree_PatioFundo": ((-10.0, 458.0, CC + e), (60.0, 448.0, CC + 10.0), 22),
        "CAM_OP_Tree_Raizes": ((68.0, 418.0, CC + 8.0), (50.0, 450.0, CC + 2.0), 24),
        "CAM_OP_Tree_Casca": ((68.0, 428.0, CC + 6.0), (57.0, 445.0, CC + 10.0), 30),
        "CAM_OP_Tree_CopaBaixo": ((20.0, 440.0, CC + e), (0.0, 425.0, CC + 140.0), 16),
        "CAM_OP_Tree_Lado": ((330.0, 470.0, CC + 40.0), (0.0, 425.0, CC + 80.0), 26),
        "CAM_OP_Tree_BaseTopo": ((40.0, 430.0, CC + 64.0), (56.0, 450.0, CC), 24),
        "CAM_OP_Tree_Tras": ((60.0, 900.0, CC + 80.0), (0.0, 425.0, CC + 80.0), 30),
    }
