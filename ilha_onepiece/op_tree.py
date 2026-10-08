# op_tree.py - ARVORE MONUMENTAL ARQUEADA (marco heroi da Ilha 5 ONE PIECE / WANO, M3; dono "tree", prefixo OP_Tree_)
# PROMPT_USUARIO secao 9 + PLANO_OP secoes 0.6 e 9. Substitui tree_monument() do op_blockout.
#   SILHUETA: tronco nasce de uma base com raizes no fundo-leste do patio do castelo (136,2), sobe a DIREITA da torre
#     quase reto (leve inclinacao para fora), dobra num OMBRO mais fechado no alto da direita, passa por cima da torre
#     num topo LONGO e baixo (~274) e desce a ESQUERDA com a ponta caida (nao e aro perfeito: curvatura assimetrica).
#   ESPESSURA: progressiva, base monumental com alargamento e lobos que viram raizes (~1/3 da largura da torre no meio
#     do tronco, como na ref_02), afinando ate a ponta; secao achatada (mais funda no plano do arco); caneluras largas
#     com TORCAO DIRIGIDA (meia volta no comprimento todo) = fibra do tronco, nao torcao sem direcao.
#   RAIZES: seguem o chao REAL (raio para baixo na geometria que ja existe: piso do patio, muro, rocha do fundo) -
#     passam POR CIMA do muro e escorrem pela face da rocha (agarram a rocha do castelo); achatadas e meio enterradas.
#   CASCA: Tier A (ate CC+26, onde a camera do jogador alcanca) com 36 lados, nervuras finas, nos; Tier B (resto) 18 lados.
#   COPA: massas principais e secundarias feitas de 3 CONJUNTOS de flor reutilizaveis (almofada com lobos; topo claro,
#     corpo rosa, baixo rosa fundo), SO por cima/fora do arco: o miolo do arco fica aberto (castelo e ceu aparecem).
#   COLISAO: so o tronco e as raizes dentro do patio (alcance do jogador). Copa e arco: sem colisao.
# Contrato com o castelo (op_castle): tree_envelope() / TREE_KEEPOUT (abaixo) e castle_envelope() (lido do op_layout).
import math, random
import bmesh, bpy
from mathutils import Vector, Matrix, Euler, noise
from mathutils.bvhtree import BVHTree
import op_lib as DL
from op_lib import MB, col_box
import op_layout as L

CC = L.CC
TIER_A_TOP = CC + 26.0          # casca detalhada so ate aqui (patio 136,2 + ~20 de alcance da camera do jogador)

# ------------------------------------------------------------------ CONTRATO / ENVOLTORIA (ler antes de mexer)
BASE_C = (54.0, 449.0)          # eixo do tronco no chao do patio (canto fundo-leste, colado ao muro)
# tronco (x, y, z, raio): sobe a direita da torre, ombro alto a direita, topo longo e baixo, desce a esquerda
TRUNK = [(54.0, 449.0, CC - 5.0, 14.6), (55.0, 448.0, CC + 4.0, 13.8), (58.0, 447.0, CC + 16.0, 12.9),
         (64.0, 445.0, CC + 32.0, 12.2), (71.0, 442.0, CC + 50.0, 11.6), (76.0, 439.0, CC + 70.0, 11.0),
         (77.0, 435.0, CC + 90.0, 10.4), (73.0, 430.0, CC + 110.0, 9.8), (62.0, 424.0, CC + 126.0, 9.2),
         (44.0, 417.0, CC + 138.0, 9.2), (22.0, 412.0, CC + 145.0, 8.8), (-2.0, 409.0, CC + 147.0, 8.2),
         (-24.0, 409.0, CC + 143.0, 7.4), (-42.0, 411.0, CC + 134.0, 6.5), (-54.0, 414.0, CC + 121.0, 5.6),
         (-60.0, 416.0, CC + 106.0, 4.6), (-61.0, 417.0, CC + 92.0, 3.7), (-58.0, 416.0, CC + 82.0, 2.6),
         (-52.0, 414.0, CC + 76.0, 1.8)]
FLAT = 0.84                     # secao: raio no plano do arco = r; de lado = r * FLAT
# raizes-contraforte: (angulo no chao em graus, comprimento, raio na saida, achatamento, garfo, peso do lobo na base)
#   direcoes LONGE da torre; as do patio sao rentes (pisaveis), as de fora agarram o muro e a rocha
ROOTS = [(-10.0, 30.0, 6.4, 0.52, True, 1.0),     # leste: por cima do muro, escorre pela face da rocha (BackE 120)
         (34.0, 24.0, 6.0, 0.52, False, 1.0),     # nordeste: canto do muro -> rocha do fundo
         (64.0, 20.0, 5.6, 0.52, True, 0.9),      # norte-nordeste: canto do muro -> escorre na rocha do fundo-leste
         (132.0, 9.0, 5.6, 0.5, False, 0.85),     # noroeste: patio, atras da torre (curta: para antes do muro)
         (172.0, 17.0, 6.0, 0.5, True, 0.9),      # oeste: patio, atras da torre (y > 446), rente no fim
         (250.0, 12.0, 5.6, 0.5, False, 0.8),     # sul-sudoeste: patio (curta; longe do canto da torre)
         (284.0, 20.0, 5.6, 0.52, False, 0.9)]    # sul: ao longo do muro leste, para o yagura
# copa: massas (centro, raio, achatamento, n_conjuntos, papel) - so por cima/fora do arco (miolo aberto)
MASSES = [((-6.0, 412.0, CC + 160.0), 34.0, 0.74, 6, "principal: topo"),
          ((54.0, 424.0, CC + 150.0), 28.0, 0.76, 5, "principal: ombro da direita"),
          ((-46.0, 413.0, CC + 154.0), 25.0, 0.78, 5, "principal: esquerda (emissor de petalas)"),
          ((-58.0, 414.0, CC + 78.0), 21.0, 0.86, 4, "principal: ponta caida da esquerda (gancho)"),
          ((92.0, 438.0, CC + 102.0), 19.0, 0.82, 3, "secundaria: galho da direita"),
          ((86.0, 432.0, CC + 132.0), 16.0, 0.8, 2, "secundaria: fora do ombro"),
          ((84.0, 460.0, CC + 64.0), 13.0, 0.8, 2, "secundaria: atras, vista do patio"),
          ((16.0, 440.0, CC + 166.0), 21.0, 0.74, 3, "secundaria: topo atras (profundidade)"),
          ((-28.0, 437.0, CC + 156.0), 17.0, 0.74, 2, "secundaria: esquerda atras"),
          ((24.0, 392.0, CC + 156.0), 14.0, 0.76, 2, "secundaria: topo na frente")]
# galhos: (ponto aproximado de saida no tronco, pontos (x, y, z, r)) - curtos e grossos; terminam DENTRO de uma massa
BRANCHES = [((76.0, 438.0, CC + 80.0), [(86.0, 438.0, CC + 92.0, 4.8), (92.0, 438.0, CC + 100.0, 3.0)]),
            ((64.0, 445.0, CC + 38.0), [(76.0, 456.0, CC + 52.0, 3.4), (84.0, 460.0, CC + 62.0, 2.0)]),
            ((66.0, 426.0, CC + 122.0), [(61.0, 424.0, CC + 138.0, 4.4), (54.0, 424.0, CC + 148.0, 2.8)]),
            ((75.0, 431.0, CC + 106.0), [(82.0, 432.0, CC + 122.0, 3.2), (86.0, 432.0, CC + 130.0, 1.8)]),
            ((30.0, 413.0, CC + 143.0), [(23.0, 428.0, CC + 156.0, 3.6), (16.0, 439.0, CC + 163.0, 2.2)]),
            ((36.0, 414.0, CC + 141.0), [(30.0, 400.0, CC + 150.0, 2.8), (24.0, 393.0, CC + 155.0, 1.6)]),
            ((4.0, 409.0, CC + 147.0), [(-1.0, 411.0, CC + 154.0, 4.4), (-6.0, 412.0, CC + 159.0, 3.0)]),
            ((-30.0, 410.0, CC + 141.0), [(-38.0, 412.0, CC + 149.0, 3.6), (-46.0, 413.0, CC + 153.0, 2.2)]),
            ((-20.0, 409.0, CC + 144.0), [(-24.0, 425.0, CC + 151.0, 3.0), (-28.0, 436.0, CC + 155.0, 1.8)]),
            ((-60.0, 416.0, CC + 100.0), [(-64.0, 418.0, CC + 90.0, 2.2), (-64.0, 416.0, CC + 84.0, 1.4)])]
# o castelo NAO pode entrar aqui (poligono no nivel do patio, z de CC a CC+30): o muro do fundo-leste deve TERMINAR
# encostado na base/raizes (as raizes passam por cima do muro do blockout ate o op_castle refazer o encontro)
TREE_KEEPOUT = [(30.0, 452.0), (34.0, 436.0), (48.0, 426.0), (58.0, 410.0), (78.0, 410.0), (84.0, 432.0),
                (94.0, 452.0), (86.0, 478.0), (60.0, 482.0), (36.0, 472.0)]
CLEAR_CASTLE = 4.0              # folga minima tronco/galho/copa <-> volumes do castelo (torre, telhados, yagura)


def castle_envelope():
    """volumes do castelo que a arvore respeita (lidos do op_layout): caixas (x0, y0, z0, x1, y1, z1)"""
    kx, ky = L.KEEP_C
    out = []
    for i, (hx, hy, z0, hw, over) in enumerate(L.KEEP_TIERS):
        top = (CC + z0 + hw + (10.0 if i == len(L.KEEP_TIERS) - 1 else 3.6))
        out.append(("torre_andar_%d" % i, (kx - hx - over, ky - hy - over, CC, kx + hx + over, ky + hy + over, top)))
    out.append(("torre_base_talude", (kx - L.KEEP_TIERS[0][0] - 3.0, ky - L.KEEP_TIERS[0][1] - 3.0, CC,
                                      kx + L.KEEP_TIERS[0][0] + 3.0, ky + L.KEEP_TIERS[0][1] + 3.0, CC + 5.0)))
    tx, ty, ts = L.TURRET
    out.append(("yagura", (tx - ts / 2 - 2.0, ty - ts / 2 - 2.0, CC, tx + ts / 2 + 2.0, ty + ts / 2 + 2.0, CC + 22.0)))
    return out


MASSES = [(c, r * 1.12, f, n, papel) for c, r, f, n, papel in MASSES]       # +12% (volta 6: presenca na Ref_01)
TRUNK = [(x, y, z, r * (1.0 if i < 3 else 1.08)) for i, (x, y, z, r) in enumerate(TRUNK)]   # meio do tronco +8%


def tree_envelope():
    """o que o castelo (e qualquer outro dono) deve deixar livre: capsulas do tronco/galhos, elipsoides da copa e o
    poligono da base. {"capsules": [((x,y,z), (x,y,z), r)], "blobs": [((x,y,z), (rx, ry, rz))], "keepout": [...],
    "keepout_z": (z0, z1)}"""
    caps = []
    for a, b in zip(TRUNK, TRUNK[1:]):
        caps.append((a[:3], b[:3], max(a[3], b[3]) * 1.15))
    for att, pts in BRANCHES:
        c = trunk_nearest(att)
        prev = (c[0].x, c[0].y, c[0].z, c[1])
        for p in pts:
            caps.append((prev[:3], p[:3], max(prev[3] * 0.55, p[3])))
            prev = p
    blobs = [(c, (r * 1.25, r * 1.15, r * f * 1.3)) for c, r, f, n, _ in MASSES]
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


def skin(mb, rings, m, cap0=True, cap1=True, smooth=True, mat_of=None, s_of=None):
    """aneis (listas de Vector com o mesmo n) -> tubo fechado; mat_of(face, i_anel) escolhe material por face.
    UV CILINDRICA: u = comprimento de arco (s_of[i] ou acumulado; o veio da madeira segue u), v = volta x circunf.
    -> o veio da textura (Wood no Roblox) corre ao longo do tronco/raiz, sem costura entre Tier A e B"""
    bm = mb.bm
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
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
    for f, i in faces:
        cc = (circ[i] + circ[min(i + 1, len(circ) - 1)]) / 2.0
        ks = []
        for lp in f.loops:
            v = lp.vert
            j = i if v in vr[i] else i + 1
            ks.append((lp, j, vr[j].index(v)))
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
            groups.setdefault(mat_of(f, i), []).append(f)
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
def _trunk_rings(s0, s1, ds, n, fine):
    c = trunk_curve()
    root_ang = [math.radians(a) for a, *_ in ROOTS]
    root_w = [lw for *_, lw in ROOTS]
    knots = [(0.4, CC + 9.0, 1.0), (2.6, CC + 15.0, 0.8), (4.4, CC + 5.0, 0.7)]     # (angulo, z, forca) - nos
    rings = []
    svals = []
    steps = max(2, int(math.ceil((s1 - s0) / ds)))
    for i in range(steps + 1):
        s = s0 + (s1 - s0) * i / steps
        svals.append(s)
        p, r, tg = c.at(s)
        nv, bv = frame_y(tg)
        h = max(0.0, p.z - CC)
        flare = 1.0 + 0.22 * math.exp(-h / 6.0)
        lob_f = 0.40 * math.exp(-h / 7.0)
        tw = math.pi * s / c.len                                          # meia volta no comprimento (fibra)
        ring = []
        for k in range(n):
            th = 2 * math.pi * k / n
            d = nv * math.cos(th) + bv * math.sin(th) * FLAT
            wa = math.atan2(d.y, d.x)
            m = flare
            for a, w in zip(root_ang, root_w):
                cs = math.cos(wa - a)
                if cs > 0:
                    m += lob_f * w * cs ** 10
            m += 0.08 * math.sin(5 * th + tw * 2.0)                      # caneluras largas, torcao dirigida
            if fine:
                fade = max(0.0, min(1.0, (TIER_A_TOP - 2.0 - p.z) / 6.0))
                # casca em PLACAS: 9 sulcos em V estreitos e fundos (4 amostras por placa nos 36 lados: le sem
                # textura, no sol e na sombra) que giram devagar com a fibra, + ondulacao fina
                grv = 1.0 - abs(math.sin(4.5 * th + 0.05 * p.z + tw * 0.5))
                m += fade * (-0.12 * grv ** 1.5 + 0.015 * math.sin(23 * th - 0.07 * p.z))
                for ka, kz, kf in knots:
                    da = math.atan2(math.sin(th - ka), math.cos(th - ka))
                    m += fade * kf * 0.09 * math.exp(-(da / 0.32) ** 2 - ((p.z - kz) / 2.2) ** 2)
            ring.append(p + d * (r * m))
        rings.append(ring)
    return rings, svals


def trunk(mb_a, mb_b):
    c = trunk_curve()
    # s em que o centro passa de TIER_A_TOP
    sA = 0.0
    while sA < c.len and c.at(sA)[0].z < TIER_A_TOP:
        sA += 0.25
    ra, sa = _trunk_rings(0.0, sA, 1.1, 36, True)
    # UMA malha so (sem emenda visivel): Tier A = aneis a cada 1,1 com nervuras finas e nos; Tier B = aneis a cada
    # 3,2 e so as caneluras largas (o detalhe acaba onde a camera do jogador deixa de alcancar)
    rb, sb = _trunk_rings(sA, c.len, 3.2, 36, False)
    skin(mb_a, ra + rb[1:], "Bark_OP", cap0=True, cap1=True, s_of=sa + sb[1:])
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
    r_g = 18.0                                                           # raio do tronco no chao (com alargamento)
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
        # raiz NAO escala parede: corta onde o chao SOBE e fica alto (rocha do fundo; muro fino ela atravessa por cima)
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
    """secao eliptica: largura rad (lado horizontal), altura hh (contraforte alto perto do tronco, achatada longe)"""
    rings = []
    prev = None
    for i, p in enumerate(cpts):
        tg = (cpts[min(i + 1, len(cpts) - 1)] - cpts[max(i - 1, 0)]).normalized()
        side, up = frame_flat(tg, prev)
        prev = side
        ring = []
        for k in range(n):
            th = 2 * math.pi * k / n
            w = 1.0 + 0.06 * math.sin(3 * th + i * 0.4)
            # lamina: o lado de cima afina (secao em gota) quando a raiz e contraforte
            sq = 1.0 - 0.35 * max(0.0, math.sin(th)) * min(1.0, hh[i] / max(rad[i], 0.1) - 0.6)
            ring.append(p + side * (math.cos(th) * rad[i] * w * max(0.45, sq)) + up * (math.sin(th) * hh[i] * w))
        rings.append(ring)
    skin(mb, rings, "Bark_OP", cap0=True, cap1=True)


# ------------------------------------------------------------------ galhos
def branches(mb):
    out = []
    for bi, (att, pts) in enumerate(BRANCHES):
        p, r, tg = trunk_nearest(att)
        chain = [(p.x, p.y, p.z, r * 0.52)] + list(pts)
        d = Curve(chain, 8)
        n = 10
        rings = []
        steps = max(3, int(d.len / 2.2))
        for i in range(steps + 1):
            q, rr, t2 = d.at(d.len * i / steps)
            nv, bv = frame_y(t2)
            rings.append([q + (nv * math.cos(2 * math.pi * k / n) + bv * math.sin(2 * math.pi * k / n) * 0.9) * rr
                          for k in range(n)])
        skin(mb, rings, "Bark_OP", cap0=True, cap1=True)
        out.append(Vector(pts[-1][:3]))
    return out


# ------------------------------------------------------------------ copa (conjuntos reutilizaveis)
def _blob_template(seed):
    """CONJUNTO de flor: almofada (topo redondo, baixo achatado) + 5 lobos na borda/topo. Retorna lista de partes
    [(centro, raio, achat_topo, achat_baixo)] em unidades do raio 1."""
    rng = random.Random(seed)
    parts = [((0.0, 0.0, 0.0), 1.0, 0.78, 0.46)]
    a0 = rng.uniform(0, 6.28)
    for k in range(5):
        a = a0 + 2 * math.pi * k / 5 + rng.uniform(-0.35, 0.35)
        d = rng.uniform(0.62, 0.84) if k < 4 else rng.uniform(0.15, 0.35)
        z = rng.uniform(0.05, 0.32) if k < 4 else rng.uniform(0.42, 0.58)
        parts.append(((math.cos(a) * d, math.sin(a) * d, z), rng.uniform(0.42, 0.56), 0.82, 0.5))
    return parts


TEMPLATES = [_blob_template(s) for s in (11, 23, 37)]


def _ellipsoid(mb, c, rx, ry, rz_top, rz_bot, nu, nv, rot):
    bm = mb.bm
    cz, sz = math.cos(rot), math.sin(rot)
    top = bm.verts.new((c[0], c[1], c[2] + rz_top))
    bot = bm.verts.new((c[0], c[1], c[2] - rz_bot))
    rows = []
    for j in range(1, nv):
        ph = math.pi * j / nv
        z = math.cos(ph)
        s = math.sin(ph)
        row = []
        for i in range(nu):
            a = 2 * math.pi * i / nu
            x, y = math.cos(a) * s * rx, math.sin(a) * s * ry
            row.append(bm.verts.new((c[0] + x * cz - y * sz, c[1] + x * sz + y * cz,
                                     c[2] + z * (rz_top if z > 0 else rz_bot))))
        rows.append(row)
    fs = []
    for i in range(nu):
        i2 = (i + 1) % nu
        fs.append(bm.faces.new((top, rows[0][i], rows[0][i2])))
        fs.append(bm.faces.new((bot, rows[-1][i2], rows[-1][i])))
    for r0, r1 in zip(rows, rows[1:]):
        for i in range(nu):
            i2 = (i + 1) % nu
            fs.append(bm.faces.new((r0[i], r1[i], r1[i2], r0[i2])))
    cv = Vector(c)
    for f in fs:
        f.normal_update()
        if f.normal.dot(f.calc_center_median() - cv) < 0:      # normal para FORA (o material sai da normal)
            f.normal_flip()
    return fs


def blossom_set(mb, c, r, flat, tmpl, rot):
    """carimba um CONJUNTO (template) em c, raio r, achatamento flat; material por orientacao da face:
    topo claro, corpo rosa, baixo rosa fundo (leitura de volume sem textura)"""
    groups = {"Flower_OP_Light": [], "Flower_OP_Blossom": [], "Flower_OP_Deep": []}
    cz, sz = math.cos(rot), math.sin(rot)
    for (ox, oy, oz), pr, ft, fb in tmpl:
        x, y = ox * r * cz - oy * r * sz, ox * r * sz + oy * r * cz
        pc = (c[0] + x, c[1] + y, c[2] + oz * r * flat * 1.4)
        rr = pr * r
        big = pr > 0.9
        fs = _ellipsoid(mb, pc, rr, rr * 0.94, rr * ft * flat * 1.25, rr * fb * flat * 1.25,
                        16 if big else 9, 8 if big else 5, rot + ox)
        for f in fs:
            nz = f.normal.z
            if nz < -0.3:
                groups["Flower_OP_Deep"].append(f)
            elif nz > 0.62:
                groups["Flower_OP_Light"].append(f)
            else:
                groups["Flower_OP_Blossom"].append(f)
    for m, fs in groups.items():
        post_faces(mb, fs, m, smooth=True)


def canopy(mb, rng):
    k = 0
    for mi, (c, r, flat, nsets, _) in enumerate(MASSES):
        # conjunto central grande + satelites (silhueta recortada, sem nuvem uniforme)
        blossom_set(mb, c, r * 0.8, flat, TEMPLATES[k % 3], rng.uniform(0, 6.28))
        k += 1
        for j in range(1, nsets):
            a = rng.uniform(0, 6.28) + j * 2.1
            d = r * rng.uniform(0.5, 0.7)
            cc = (c[0] + math.cos(a) * d, c[1] + math.sin(a) * d * 0.7, c[2] + rng.uniform(-0.25, 0.2) * r * flat)
            blossom_set(mb, cc, r * rng.uniform(0.48, 0.6), flat, TEMPLATES[k % 3], rng.uniform(0, 6.28))
            k += 1
    return k


def twigs(mb, ends, rng):
    """raminhos do fim de cada galho ate a borda de baixo da massa (a copa de baixo mostra a estrutura)"""
    for e in ends:
        best = min(MASSES, key=lambda m: (Vector(m[0]) - e).length)
        c, r, flat = Vector(best[0]), best[1], best[2]
        for j in range(3):
            a = rng.uniform(0, 6.28)
            tgt = c + Vector((math.cos(a) * r * 0.62, math.sin(a) * r * 0.45, -r * flat * 0.25))
            mid = e.lerp(tgt, 0.5) + Vector((0, 0, -1.2))
            d = Curve([(e.x, e.y, e.z, 0.95), (mid.x, mid.y, mid.z, 0.65), (tgt.x, tgt.y, tgt.z, 0.35)], 4)
            rings = []
            steps = 4
            for i in range(steps + 1):
                q, rr, t2 = d.at(d.len * i / steps)
                nv, bv = frame_y(t2)
                rings.append([q + (nv * math.cos(2 * math.pi * k / 6) + bv * math.sin(2 * math.pi * k / 6)) * rr
                              for k in range(6)])
            skin(mb, rings, "Bark_OP", cap0=True, cap1=True)


# ------------------------------------------------------------------ rocha da base
def base_rocks(mb, ground, rng):
    """rocha do castelo onde a base pega: blocos facetados (pedra, nao inflavel) fora do muro, no degrau entre o
    patio (136,2) e a rocha do fundo (120 / 150), e 2 lajes baixas dentro do patio sob as raizes"""
    bx, by = BASE_C
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
            n = noise.noise_vector(v.co * 0.18 + Vector((i * 3.1, i * 1.7, 0.0)))
            v.co += n * r * 0.16
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
    p, r, tg = trunk_point(0.0)
    for k, ang in enumerate((0.0, math.pi / 4)):
        col_box("OP_TreeTrunk", (22.0, 22.0, 28.0), (bx, by, CC + 14.0), (0, 0, ang))
    col_box("OP_TreeTrunk", (19.0, 19.0, 16.0), (bx + 3.0, by - 1.5, CC + 34.0), (0, 0, math.pi / 8))
    # raizes dentro do patio: caixas rentes por trecho (so onde a raiz sobe > 0,9 do piso); fora do patio nada
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
    hard, wall = 0, 0
    where = []
    if tb and cb:
        for i, j in tb.overlap(cb):
            c = sum((tv[k] for k in tf[i]), Vector()) / len(tf[i])          # onde a ARVORE encosta
            if L.point_in_poly(c.x, c.y, TREE_KEEPOUT) and c.z < CC + 30.0:
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
            dz = (c[2] - rz) - z1
            if dz < worst[0] and abs(c[0]) - rx < x1 and abs(c[1] - L.KEEP_C[1]) - ry < (y1 - y0) / 2:
                worst = (dz, nm + " (copa)")
    ok = hard == 0 and worst[0] >= CLEAR_CASTLE
    if verbose:
        print(("OK   " if ok else "FAIL ") + "OP_TREE castelo: %d interseccoes fora da base %s | %d encontros base x muro "
              "(no TREE_KEEPOUT: o op_castle termina o muro ali) | folga minima tronco/galho/copa -> castelo %.1f (%s)" % (
                  hard, " ".join(where), wall, worst[0], worst[1]))
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
    noise.seed_set(5505)
    rng = random.Random(4105)
    ground = Ground(10.0, 405.0, 110.0, 500.0)
    # Tier A: base (tronco ate CC+26, raizes, rocha) - perto do jogador
    mb_a = MB("OP_Tree_Trunk", "04_CASTLE", rng, detail="hero", floor=-999)
    mb_b = MB("OP_Tree_Branches", "04_CASTLE", rng, detail="far", floor=-999)
    trunk(mb_a, mb_b)
    segs = roots(mb_a, ground, rng)
    base_rocks(mb_a, ground, rng)
    mb_a.finish()
    ends = branches(mb_b)
    twigs(mb_b, ends, rng)
    mb_b.finish()
    mc = MB("OP_Tree_Bloom", "04_CASTLE", rng, detail="far", floor=-999)
    canopy(mc, rng)
    mc.finish()
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
