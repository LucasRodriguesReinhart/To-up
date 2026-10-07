# ds_terrain - ZONA TERRAIN da Ilha 4 (DEMON SLAYER), onda 1a. build() substitui ds_blockout.terrain.
# Prefixos DS_Ter_ (terreno) e DS_Clr_ (chao da clareira; o dono no export tambem e o terreno). Colecoes 02_TERRAIN e
# 03_CLEARING. Sem luzes. Le a planta TRAVADA (ds_layout); nao cria marcador; a colisao andavel continua toda no ds_col
# (aqui so: rochas da borda da clareira e as faces das falesias/arrimos de rocha que avancam sobre o piso de baixo).
#
# LEITURA (lead): a ilha lia CHATA. Aqui o terreno e feito de COLUNAS de rocha facetadas (a lingua das referencias):
#   1. COROA: anel de colunas no contorno, topo SEMPRE abaixo do piso vizinho (0,4..2,4: nunca furam o chao andavel),
#      pes pendentes em alturas DIRIGIDAS (ciclos fixos, nada de sorteio solto), 1 estrato continuo em z 45 (abaixo dele
#      a coluna recua e escurece); atras da forja a coroa vira o paredao da montanha (ate ~108).
#   2. QUILHA: mais 2 aneis de colunas para dentro e para baixo (topos escondidos atras do anel de fora), pontas
#      pendentes ate -34, com nucleos ocultos que fecham as frestas.
#   3. ARRIMOS: entre patamares. Altos naturais (berma do mirante, plato do summon, cascata) = colunas de rocha que
#      avancam sobre o piso de baixo (com colisao propria); construidos (vila alta, frente da forja = o "muro alto")
#      = ISHIGAKI em talude: fiadas de pedra com junta rebaixada (o fundo escuro aparece na junta) e capa de pedra.
#   4. ENCHIMENTO: tudo que esta dentro do contorno e nao e piso (crista oeste, barranco nordeste, rochas da montanha,
#      ombro leste, bloco da escada Trilha) vira colunas com o topo DIRIGIDO por regiao; a primeira fila junto a um piso
#      fica um pouco acima dele (borda natural de rocha), nunca invadindo o piso.
#   5. CHAO: corpo oculto ate piso - 0,5 (o "leito", escuro) + PELE do piso exatamente NA COTA DA COLISAO (campo de
#      distancia + marching squares: borda exata, sem frestas); grama em MANCHAS 0,18 acima com bordadura em chanfro
#      (verde escuro); lajes (patio do torii com o sando no eixo, trilha, pisantes do bambuzal) 0,14 acima com junta.
#      Onde OUTRO modulo poe piso (patio da forja, patamar da subida, ruas da vila, caminho de saida) e onde ha AGUA
#      (lagoa, canal, calha) a pele NAO existe: fica o leito 0,5 abaixo (regra do z-fight: piso sobre piso >= 0,3).
#   6. CLAREIRA: terra batida com ondulacao suave SEM colisao (<= 0,3, mesmo material: sem z-fight), grama so na
#      transicao da borda, fragmentos de pedra e raizes so nas bordas, 7 rochas de borda (com colisao, fora da zona+8).
#      O miolo fica LIVRE (CLAREIRA_LIVRE: nada colidivel na MiningZone).
#   7. RAVINA leste: corte entre colunas com o leito em degraus ate o labio (FX_Fall_2_Lip, 53,4) e a calha recuada na
#      coroa para a queda; a pedra da cascata interna fica para o ds_water (aqui so o recuo das colunas atras dela).
# ONDA 4b (DENSIDADE, critica do lead: falesia em colunas cinza limpas e clareira = retangulo marrom chapado):
#   - FALESIA: tom POR COLUNA (Cliff_DS_B quente explicito / familia fria), estrato de baixo escuro em metade das
#     colunas (sem linha continua), capa verde que CAI pela face de fora (drip_dir: os vertices de fora descem 1..5,
#     borda irregular; musgo ou Grass_DS_Deep) e DS_Ter_Moss = linguas de musgo/verde escorrendo (streaks: 0,22 a
#     frente da face, nunca coplanar). Forma, posicao e topo plano das colunas NAO mudam (ancoras do ds_veg).
#   - CLAREIRA: pele em manchas terra / terra escura (material por regiao NA MESMA cota, sem saia na borda interna:
#     field_mesh(inner=)), terra escura mais perto da grama + trilhas de passagem (CLR_TRACKS, so fora da MiningZone),
#     faixa de grama da borda larga e rasgada, grama rala em manchas ate ~46 da borda; relevo (<= 0,26) so FORA da
#     MiningZone + 2. Colisao intocada (CLAREIRA_PISO plano).
#   - CAMPOS DE GRAMA: cada camada em pedacos de TOM (Grass_DS_Deep / Grass_DS / Grass_DS_B / Grass_DS_Dry; vies da
#     borda das falesias e da borda da clareira) + trilhas de passagem no patamar, vila alta e saida (FIELD_TRACKS).
# CONTRATO COM OS OUTROS MODULOS: ver BED_REGIONS (onde a pele nao existe). O patio do torii (lajes) e o chao do plato
# do summon sao DESTE modulo (eram do terreno no blockout). A clareira do blockout (DS_Clr_Ground + as pedras de
# DS_Clr_Edges) e removida aqui: o chao da clareira e do terreno (build_ds.ZONE_MODULES).
import math, zlib
import numpy as np
import bmesh
import bpy
from mathutils import Vector
import ds_lib as DL
from ds_lib import MB, col_box, ccw
import fm_lib
import ds_layout as L
import ds_col

T0, T1, T2, T3, T4 = L.T0, L.T1, L.T2, L.T3, L.T4
BASE = 44.0                 # fundo dos corpos dos patamares (a quilha cobre o resto)
BEDD = 0.5                  # leito: topo do corpo = piso - 0,5
GRASS_H = 0.18              # manchas de grama acima do piso
SLAB_H = 0.14               # lajes acima do piso
STRATA = 45.0               # o estrato continuo da coroa
ROCK, ROCKD, MOSS = "Cliff_DS", "Cliff_DS_Dark", "Cliff_DS_Moss"
STONE, PATH, SDARK = "Stone_DS", "Stone_DS_Path", "Stone_DS_Dark"
LAJE = "Stone_DS_Laje"      # lajes dos caminhos: cinza quente MEDIO (Path claro demais ao lado da madeira escura)
DIRT, DIRTD, GRASS, GRASSB = "Dirt_DS", "Dirt_DS_Dark", "Grass_DS", "Grass_DS_B"
# ONDA 4b (densidade): rocha quente explicita (o resto da familia Cliff_DS segue sorteando), grama funda (borda verde
# que cai, musgo escorrendo, manchas junto das falesias) e grama rala/seca (manchas da clareira)
ROCKB, GDEEP, GDRY = "Cliff_DS_B", "Grass_DS_Deep", "Grass_DS_Dry"
MOSS_REC = []               # colunas registradas para o musgo escorrendo (ver streaks)

# ------------------------------------------------------------------ cameras de revisao da zona
CAMS = {
    "CAM_DSTer_KeelSE": ((420.0, -60.0, 10.0), (40.0, 250.0, 30.0), 24),
    "CAM_DSTer_KeelW": ((-420.0, 260.0, 0.0), (0.0, 300.0, 30.0), 24),
    "CAM_DSTer_Ref01Low": ((25.0, -170.0, 110.0), (25.0, 120.0, 40.0), 22),
    "CAM_DSTer_PH_Court": ((2.0, 4.0, T0 + 5.5), (-6.0, 60.0, T1 + 3.0), 22),
    "CAM_DSTer_PH_Trail": ((-14.0, 60.0, T1 + 5.5), (10.0, 150.0, T1 + 2.0), 22),
    "CAM_DSTer_PH_VilWall": ((-30.0, 250.0, T1 + 5.5), (-62.0, 300.0, T1 + 4.0), 22),
    "CAM_DSTer_PH_ForgeWall": ((-20.0, 340.0, T1 + 5.5), (10.0, 430.0, T3 + 4.0), 22),
    "CAM_DSTer_PH_ClrEdge": ((92.0, 190.0, T1 + 5.5), (140.0, 236.0, T1), 22),
    "CAM_DSTer_PH_SummonWall": ((100.0, 262.0, T1 + 5.5), (150.0, 300.0, T1 + 5.0), 22),
    "CAM_DSTer_Ravine": ((200.0, 190.0, 72.0), (150.0, 230.0, 50.0), 24),
    "CAM_DSTer_BackCliff": ((60.0, 760.0, 120.0), (20.0, 540.0, 80.0), 24),
    "CAM_DSTer_PH_Berm": ((10.0, 404.0, T3 + 5.5), (60.0, 300.0, T1), 22),
    "CAM_DSTer_PH_Bamboo": ((22.0, 32.0, T0 + 5.5), (60.0, 120.0, T1 + 2.0), 22),
}


# ------------------------------------------------------------------ variacao DIRIGIDA (hash estavel, sem estado)
def hh(*a):
    s = "|".join("%.2f" % v if isinstance(v, float) else str(v) for v in a)
    return (zlib.crc32(s.encode("utf-8")) & 0xffffffff) / 4294967296.0


def cyc(seq, i):
    return seq[i % len(seq)]


# ------------------------------------------------------------------ campos de distancia (numpy)
def sdf_poly(X, Y, P):
    """distancia com sinal ao poligono (positivo dentro)"""
    P = np.asarray(P, float)
    n = len(P)
    inside = np.zeros(X.shape, bool)
    d2 = np.full(X.shape, 1e18)
    for i in range(n):
        ax, ay = P[i]
        bx, by = P[(i + 1) % n]
        if (ay > by) or (ay < by):
            cond = (ay > Y) != (by > Y)
            xint = (bx - ax) * (Y - ay) / (by - ay) + ax
            inside ^= cond & (X < xint)
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0)
        d2 = np.minimum(d2, (X - ax - dx * t) ** 2 + (Y - ay - dy * t) ** 2)
    d = np.sqrt(d2)
    return np.where(inside, d, -d)


def sdf_line(X, Y, pts, hw):
    """faixa de meia-largura hw em volta da polilinha (positivo dentro)"""
    d2 = np.full(X.shape, 1e18)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0)
        d2 = np.minimum(d2, (X - ax - dx * t) ** 2 + (Y - ay - dy * t) ** 2)
    return hw - np.sqrt(d2)


def sdf_rect(X, Y, r):
    x0, y0, x1, y1 = r
    return sdf_poly(X, Y, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)])


def waves(X, Y, seed, scale=1.0):
    """'ruido' suave e DIRIGIDO (soma de 4 ondas fixas), amplitude ~1"""
    out = np.zeros(X.shape)
    for k, (fx, fy, ph) in enumerate(((0.031, 0.018, 0.0), (-0.017, 0.043, 1.3), (0.052, -0.029, 2.1),
                                      (0.011, 0.067, 4.0))):
        out += math.cos(k * 0.7 + seed) * 0.42 * np.sin((X * fx + Y * fy) * scale * 6.0 + ph + seed * (k + 1))
    return out


class Grid:
    def __init__(self, x0, y0, x1, y1, h):
        self.h = h
        self.x0, self.y0 = math.floor(x0 / h) * h - h, math.floor(y0 / h) * h - h
        nx = int(math.ceil((x1 - self.x0) / h)) + 2
        ny = int(math.ceil((y1 - self.y0) / h)) + 2
        xs = self.x0 + np.arange(nx) * h
        ys = self.y0 + np.arange(ny) * h
        self.X, self.Y = np.meshgrid(xs, ys)


DISSOLVE_ANG = float(__import__("os").environ.get("DS_DISSOLVE_ANG", "0.02"))   # rad (ONDA 4: era 0,15)


def sample(G, A, x, y):
    """valor bilinear do campo A (na grade G) em (x, y)"""
    fi, fj = (x - G.x0) / G.h, (y - G.y0) / G.h
    i, j = int(math.floor(fi)), int(math.floor(fj))
    ny, nx = A.shape
    if not (0 <= i < nx - 1 and 0 <= j < ny - 1):
        return -1.0
    tx, ty = fi - i, fj - j
    return float((A[j, i] * (1 - tx) + A[j, i + 1] * tx) * (1 - ty) + (A[j + 1, i] * (1 - tx) + A[j + 1, i + 1] * tx) * ty)


def field_mesh(mb, G, F, zfun, m, top_off=0.0, skirt=0.5, flare=0.0, m_skirt=None, dissolve=True, inner=None,
               inner_thr=0.3):
    """superficie da regiao F > 0 (marching squares sobre a grade G) no z = zfun(x, y) + top_off, com saia de
    'skirt' para baixo na borda (alargando 'flare' para fora: chanfro). Faces em ordem anti-horaria (normal +Z).
    ONDA 4b: inner = campo da regiao INTEIRA quando F e um pedaco dela (tom/material por mancha): a borda interna
    (entre 2 pedacos da mesma camada, inner > inner_thr no meio da aresta) fica sem saia (nada a esconder, e tris)."""
    F = np.where(np.abs(F) < 1e-3, -1e-3, F)
    Fl = F.tolist()
    ny, nx = F.shape
    h, x0, y0 = G.h, G.x0, G.y0
    bm = mb.bm
    cache = {}
    verts = []

    def V(key, x, y):
        v = cache.get(key)
        if v is None:
            v = bm.verts.new((x, y, zfun(x, y) + top_off))
            cache[key] = v
            verts.append(v)
        return v

    def node(i, j):
        return V(("n", i, j), x0 + i * h, y0 + j * h)

    def edge(i0, j0, i1, j1):
        if (i1, j1) < (i0, j0):
            i0, j0, i1, j1 = i1, j1, i0, j0
        f0, f1 = Fl[j0][i0], Fl[j1][i1]
        t = min(0.97, max(0.03, f0 / (f0 - f1)))
        return V(("e", i0, j0, i1, j1), x0 + (i0 + (i1 - i0) * t) * h, y0 + (j0 + (j1 - j0) * t) * h)

    faces = []
    for j in range(ny - 1):
        row0, row1 = Fl[j], Fl[j + 1]
        for i in range(nx - 1):
            c = ((i, j, row0[i]), (i + 1, j, row0[i + 1]), (i + 1, j + 1, row1[i + 1]), (i, j + 1, row1[i]))
            pos = [cc[2] > 0 for cc in c]
            if not any(pos):
                continue
            if pos[0] == pos[2] and pos[1] == pos[3] and pos[0] != pos[1] and sum(cc[2] for cc in c) <= 0.0:
                # 6b: celula em SELA com o centro negativo = 2 cantos separados. Antes a sela virava sempre um hexagono
                # ligando os cantos positivos, e o campo complementar (-F, material vizinho na mesma cota) fazia o mesmo:
                # os 2 cobriam o meio da celula (coplanar de material diferente). Agora o centro decide (F e -F
                # escolhem lados opostos)
                for k in range(4):
                    if pos[k]:
                        a, pv, nx2 = c[k], c[(k - 1) % 4], c[(k + 1) % 4]
                        try:
                            faces.append(bm.faces.new((node(a[0], a[1]), edge(a[0], a[1], nx2[0], nx2[1]),
                                                       edge(pv[0], pv[1], a[0], a[1]))))
                        except ValueError:
                            pass
                continue
            vs = []
            for k in range(4):
                a, b = c[k], c[(k + 1) % 4]
                if pos[k]:
                    vs.append(node(a[0], a[1]))
                if pos[k] != pos[(k + 1) % 4]:
                    vs.append(edge(a[0], a[1], b[0], b[1]))
            if len(vs) >= 3:
                try:
                    faces.append(bm.faces.new(vs))
                except ValueError:
                    pass
    if not faces:
        return []
    if dissolve:
        for f in faces:
            f.normal_update()
        # ONDA 4: ordem DETERMINISTICA (o set de BMEdge saia em ordem de memoria: o dissolve mudava de build para
        # build) e limite de angulo ate DISSOLVE_ANG. Com 0,15 rad (8,6 graus) o dissolve juntava encostas suaves em
        # ngons NAO planares de ate ~8000 studs2 (53 vertices) e cada camada (pele de terra x manchas de grama 0,15
        # acima) triangulava a sua de um jeito: a grama afundava sob a terra em trechos inteiros (bambuzal, entrada).
        bm.edges.index_update()
        bm.verts.index_update()
        edges = sorted({e for f in faces for e in f.edges}, key=lambda e: e.index)
        verts.sort(key=lambda v: v.index if v.is_valid else -1)
        # funde as faces coplanares e tira os vertices quase colineares do contorno
        bmesh.ops.dissolve_limit(bm, angle_limit=DISSOLVE_ANG, use_dissolve_boundaries=False, verts=verts, edges=edges,
                                 delimit=set())
    verts = [v for v in verts if v.is_valid]
    vset = set(verts)
    faces = list({f for v in verts for f in v.link_faces})
    # saia (borda): arestas de contorno na ordem do laco (anti-horario visto de cima -> fora = direita)
    bnd = []
    for f in faces:
        for lp in f.loops:
            if len(lp.edge.link_faces) == 1:
                a_, b_ = lp.vert, lp.link_loop_next.vert
                if inner is not None and sample(G, inner, (a_.co.x + b_.co.x) / 2, (a_.co.y + b_.co.y) / 2) > inner_thr:
                    continue
                bnd.append((a_, b_))
    bnd.sort(key=lambda e: (e[0].index, e[1].index))
    nrm = {}
    for a, b in bnd:
        dx, dy = b.co.x - a.co.x, b.co.y - a.co.y
        ln = math.hypot(dx, dy) or 1.0
        o = (dy / ln, -dx / ln)
        for v in (a, b):
            s = nrm.get(v, (0.0, 0.0))
            nrm[v] = (s[0] + o[0], s[1] + o[1])
    low = {}
    for v, (ox, oy) in nrm.items():
        ln = math.hypot(ox, oy) or 1.0
        low[v] = bm.verts.new((v.co.x + ox / ln * flare, v.co.y + oy / ln * flare, v.co.z - skirt))
    for a, b in bnd:
        try:
            bm.faces.new((a, low[a], low[b], b))
        except ValueError:
            pass
    mb._post(verts, m, None, 0, 1)
    if low:
        mb._post(list(low.values()), m_skirt or m, None, 0, 1)
    return verts


# ------------------------------------------------------------------ pecas de rocha
def column(mb, cx, cy, a, b, ang, ztop, zbot, key, m=ROCK, cap=MOSS, strata=(), taper=0.55, tip=3.0, ch=0.7,
           n=6, mlow=ROCKD, ledge=None, bottom=True, flare=1.0, cap_top_only=False, block=False, top_s=0.80,
           step_s=0.88, tilt=None, drip=0.0, drip_dir=None, rec=None):
    """COLUNA de rocha facetada: pegada de n lados (meia-largura a no rumo ang, meia-profundidade b), raios DIRIGIDOS
    pela chave; topo com chanfro (material cap); estratos: abaixo de cada cota a coluna recua 12% (ressalto 'ledge')
    e escurece (mlow); pe pendente: o ultimo trecho afina (taper) numa ponta 'tip' abaixo de zbot (tip <= 0 = pe reto;
    bottom=False = sem tampa de baixo, para pe enterrado). Cada parte tem os PROPRIOS vertices (o material nao vaza)."""
    if ztop - zbot < 0.8:
        return 0
    ca, sa = math.cos(ang), math.sin(ang)
    bm = mb.bm
    if block:
        # bloco talhado: retangulo com 2 quinas opostas cortadas (quais e quanto: DIRIGIDO pela chave)
        c1 = 0.25 + 0.35 * hh(key, "c1")
        c2 = 0.20 + 0.40 * hh(key, "c2")
        sk = (hh(key, "sk") - 0.5) * 0.3
        flip = hh(key, "f") > 0.5
        m_ = min(a, b)
        if flip:
            base = [(a, -b), (a, b - c1 * m_), (a - c1 * m_, b), (-a, b), (-a, -b + c2 * m_), (-a + c2 * m_, -b)]
        else:
            base = [(a - c1 * m_, -b), (a, -b + c1 * m_), (a, b), (-a + c2 * m_, b), (-a, b - c2 * m_), (-a, -b)]
        base = [(u + v * sk, v) for u, v in base]
        n = len(base)
    else:
        if n is None:                   # 5, 6 ou 7 faces (dirigido pela chave)
            n = (5, 6, 7, 6)[int(hh(key, "n") * 4) % 4]
        rr = [0.78 + 0.40 * hh(key, k) for k in range(n)]
        rot0 = (hh(key, "r") - 0.5) * 0.5
        base = [(a * rr[k] * math.cos(rot0 + 2 * math.pi * k / n), b * rr[k] * math.sin(rot0 + 2 * math.pi * k / n))
                for k in range(n)]

    def ring(s, z):
        out = []
        for k, (u, v) in enumerate(base):
            u, v = u * s, v * s
            out.append(bm.verts.new((cx + u * ca - v * sa, cy + u * sa + v * ca, z[k] if isinstance(z, list) else z)))
        return out

    # topo inclinado (plano: cai 'slope' por stud no rumo (dx, dy)) - o ponto mais alto fica em ztop
    if tilt:
        tdx, tdy, slope = tilt
        pr = [(u * ca - v * sa) * tdx + (u * sa + v * ca) * tdy for u, v in base]
        pmin = min(pr)
        ztops = [ztop - slope * (p - pmin) * top_s for p in pr]
    else:
        ztops = [ztop] * n
    chs = [ch + drip * hh(key, k, "d") for k in range(n)]
    if drip_dir:
        # ONDA 4b: a capa verde CAI pela face de fora (vertices virados para drip_dir descem mais: borda irregular)
        ddx, ddy, amt = drip_dir
        for k, (u, v) in enumerate(base):
            px, py = u * ca - v * sa, u * sa + v * ca
            d = (px * ddx + py * ddy) / (math.hypot(px, py) or 1.0)
            if d > 0.0:
                chs[k] += amt * d ** 1.5 * (0.35 + 0.65 * hh(key, k, "dd"))
    chs = [min(c_, (ztop - zbot) * 0.35) for c_ in chs]
    zmid = [zt_ - c_ for zt_, c_ in zip(ztops, chs)]

    def band(lo, up):
        for k in range(n):
            j = (k + 1) % n
            bm.faces.new((lo[k], lo[j], up[j], up[k]))

    cuts = [z for z in sorted(strata, reverse=True) if zbot + 2.0 < z < min(zmid) - 1.5]
    top, mid = ring(top_s, ztops), ring(1.0, zmid)
    bm.faces.new(top)
    if cap_top_only and not drip:       # musgo SO no plano do topo; o chanfro e rocha (nada de "tampinha")
        mb._post(top, cap, None, 0, 1)
        top2 = ring(top_s, ztops)
        band(mid, top2)
        mb._post(top2 + mid, m, None, 0, 1)
    else:                               # musgo no topo e escorrendo pela face (profundidade propria por face)
        band(mid, top)
        mb._post(top + mid, cap, None, 0, 1)
    zs = [zmid] + cuts + [zbot]
    if rec is not None:                 # faces da 1a faixa (vertical, escala 1) para o musgo escorrendo
        pts = [(cx + u * ca - v * sa, cy + u * sa + v * ca) for u, v in base]
        rec[0].append((rec[1], key, pts, list(zmid), zs[1], rec[2]))
    s = 1.0
    for k in range(len(zs) - 1):
        mm = m if k == 0 else mlow
        up, lo = ring(s, zs[k]), ring(s * (flare if k == len(zs) - 2 else 1.0), zs[k + 1])
        band(lo, up)
        vs = up + lo
        if k == len(zs) - 2:
            if tip > 0.05 and taper <= 0.0:
                # 6b (orcamento): ponta em BICO (apice unico, sem tampa): n triangulos em vez de 2n + tampa
                ap = bm.verts.new((cx, cy, zs[k + 1] - tip))
                for kk in range(n):
                    bm.faces.new((ap, lo[(kk + 1) % n], lo[kk]))
                vs.append(ap)
            elif tip > 0.05:
                pt = ring(s * taper, zs[k + 1] - tip)
                band(pt, lo)
                if bottom:
                    bm.faces.new(list(reversed(pt)))
                vs += pt
            elif bottom:
                bm.faces.new(list(reversed(lo)))
            mb._post(vs, mm, None, 0, 1)
        else:
            mb._post(vs, mm, None, 0, 1)
            o, i_ = ring(max(s, s * step_s), zs[k + 1]), ring(min(s, s * step_s), zs[k + 1])
            for kk in range(n):
                j = (kk + 1) % n
                bm.faces.new((o[kk], o[j], i_[j], i_[kk]))
            mb._post(o + i_, ledge or mlow, None, 0, 1)
            s *= step_s
    return 1


def streaks(mb, recs):
    """ONDA 4b: MUSGO E VERDE ESCORRENDO pelas faces de fora das colunas (a lingua das refs: faixas verdes que descem
    da capa do topo). Cada faixa e uma lingua de 5 lados 0,22 A FRENTE da face (nunca coplanar), com espessura que
    entra na rocha; comeca 0,25 acima do pe da capa (emenda com o chanfro verde) e desce L DIRIGIDO pela chave.
    recs: (fora (dx, dy) ou None, chave, pegada, zmid por vertice, pe da 1a faixa, (quantas, Lmin, Lmax))"""
    n = 0
    for out, key, pts, zmid, zlow, (cnt, lmin, lmax) in recs:
        nv = len(pts)
        cands = []
        for k in range(nv):
            a, b = pts[k], pts[(k + 1) % nv]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 1.4:
                continue
            nx_, ny_ = dy / ln, -dx / ln
            if out is None or nx_ * out[0] + ny_ * out[1] > 0.3:
                cands.append((hh(key, k, "sk"), k, a, b, ln, nx_, ny_))
        cands.sort()
        for _, k, a, b, ln, nx_, ny_ in cands[:cnt]:
            j = (k + 1) % nv
            hb = min(zmid[k], zmid[j]) - zlow
            L = min(lmin + (lmax - lmin) * hh(key, k, "sl"), hb * 0.7)
            if L < 1.2:
                continue
            ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            w = min(ln * (0.45 + 0.3 * hh(key, k, "sw")), 4.6)
            u0 = 0.12 * ln + (ln * 0.76 - w) * hh(key, k, "st")
            u1 = u0 + w

            def P(u, d, off):
                zt = zmid[k] + (zmid[j] - zmid[k]) * u / ln
                return (a[0] + ux * u + nx_ * off, a[1] + uy * u + ny_ * off, zt - d)
            lip = 0.25
            shape = [(u0, -lip), (u1, -lip), (u1 - 0.18 * w, (0.45 + 0.25 * hh(key, k, "s1")) * L),
                     (u0 + (0.25 + 0.3 * hh(key, k, "s2")) * w, L)]
            bm = mb.bm
            fr = [bm.verts.new(P(u, d, 0.22)) for u, d in shape]
            bk = [bm.verts.new(P(u, d, -0.12)) for u, d in shape]
            ff = bm.faces.new(fr)
            ff.normal_update()
            if ff.normal.x * nx_ + ff.normal.y * ny_ < 0:
                ff.normal_flip()
            ns_ = len(shape)
            cxs = sum(p[0] for p in shape) / ns_
            cds = sum(p[1] for p in shape) / ns_
            for q in range(ns_):
                r = (q + 1) % ns_
                sf = bm.faces.new((fr[q], fr[r], bk[r], bk[q]))
                sf.normal_update()
                # fora da lingua = do centro da forma para o meio da aresta (no plano da face)
                mu = (shape[q][0] + shape[r][0]) / 2 - cxs
                md = (shape[q][1] + shape[r][1]) / 2 - cds
                want = (ux * mu, uy * mu, -md)
                if sf.normal.x * want[0] + sf.normal.y * want[1] + sf.normal.z * want[2] < 0:
                    sf.normal_flip()
            m = GDEEP if hh(key, k, "sm") < 0.45 else MOSS
            mb._post(fr + bk, m, None, 0, 1)
            n += 1
    return n


def boulder(mb, cx, cy, z0, r, hgt, key, m=STONE, cap=None, ang=0.0, n=7):
    """pedra de borda: coluna baixa larga de 7 lados com topo chanfrado (a mesma lingua das falesias), meio enterrada"""
    column(mb, cx, cy, r, r * (0.72 + 0.2 * hh(key, "b")), ang, z0 + hgt, z0 - 0.6, key, m=m, cap=cap or m,
           taper=0.95, tip=0.0, ch=min(0.6, hgt * 0.35), n=n, mlow=m, bottom=False)


def slab(mb, quad, zf, top, th=0.36, ch=0.09, m=LAJE):
    """laje: quad 2D (anti-horario), topo em zf(x, y) + top com chanfro, espessura th (sem fundo)"""
    bm = mb.bm
    if ch <= 0.0:
        vt = [bm.verts.new((x, y, zf(x, y) + top)) for x, y in quad]
        vb = [bm.verts.new((x, y, zf(x, y) + top - th)) for x, y in quad]
        bm.faces.new(vt)
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new((vb[k], vb[j], vt[j], vt[k]))
        mb._post(vt + vb, m, None, 0, 1)
        return
    c = (sum(p[0] for p in quad) / 4, sum(p[1] for p in quad) / 4)
    inner = [(p[0] + (c[0] - p[0]) * ch / max(0.4, math.dist(p, c)) * 1.4,
              p[1] + (c[1] - p[1]) * ch / max(0.4, math.dist(p, c)) * 1.4) for p in quad]
    bm = mb.bm
    vt = [bm.verts.new((x, y, zf(x, y) + top)) for x, y in inner]
    vm = [bm.verts.new((x, y, zf(x, y) + top - ch)) for x, y in quad]
    vb = [bm.verts.new((x, y, zf(x, y) + top - th)) for x, y in quad]
    bm.faces.new(vt)
    for k in range(4):
        j = (k + 1) % 4
        bm.faces.new((vm[k], vm[j], vt[j], vt[k]))
        bm.faces.new((vb[k], vb[j], vm[j], vm[k]))
    mb._post(vt + vm + vb, m, None, 0, 1)


# ------------------------------------------------------------------ geometria da planta
FLOORS = L.floors()
FLOOR_BY = {nm: (poly, z, pr) for nm, poly, z, pr in FLOORS}


def floor_z(nm, x, y):
    return L._zval(FLOOR_BY[nm][1], x, y)


def zfloor(x, y):
    return L.zone_of(x, y)


def resample(pts, step, closed=True):
    P = list(pts) + ([pts[0]] if closed else [])
    out = []
    acc = 0.0
    for a, b in zip(P, P[1:]):
        ln = math.dist(a, b)
        while acc <= ln:
            t = acc / ln if ln else 0.0
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, math.atan2(b[1] - a[1], b[0] - a[0])))
            acc += step
        acc -= ln
    return out


def tangent_frames(pts, steps, closed=True):
    """pontos ao longo da polilinha com passo DIRIGIDO (ciclo 'steps'): (x, y, rumo, passo)"""
    P = list(pts) + ([pts[0]] if closed else [])
    segs = list(zip(P, P[1:]))
    total = sum(math.dist(a, b) for a, b in segs)
    out, s, i = [], 0.0, 0
    while s < total - 0.5:
        st = cyc(steps, i)
        d = s + st / 2
        acc = 0.0
        for a, b in segs:
            ln = math.dist(a, b)
            if acc + ln >= d:
                t = (d - acc) / ln if ln else 0
                out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
                            math.atan2(b[1] - a[1], b[0] - a[0]), st))
                break
            acc += ln
        s += st
        i += 1
    return out


# regioes que nao sao piso (so visual), com a cota do topo das colunas
def region_top(x, y):
    """cota DIRIGIDA do topo do enchimento de rocha em (x, y), ou None (ombro generico: decide pela vizinhanca)"""
    if L.point_in_poly(x, y, L.BACK_ROCKS):
        # montanha atras da forja: PICOS dirigidos (a moldura da silhueta), sela no meio, nascente no pico leste
        base = 84.0 + min(8.0, max(0.0, (y - 516.0) * 0.2))
        for px, py, ph in BACK_PEAKS:
            base = max(base, ph - 0.62 * math.dist((x, y), (px, py)))
        if L.polyline_dist(x, y, L.FLUME) < 5.5:
            base = min(base, 95.0)
        return base
    if L.point_in_poly(x, y, L.NE_BANK):
        return 70.0 + 4.0 * hh(round(x / 6), round(y / 6), "ne")
    if L.point_in_poly(x, y, L.WEST_RIDGE):
        return 64.0 + 8.0 * min(1.0, max(0.0, (-x - 30.0) / 30.0)) + 2.0 * hh(round(x / 6), round(y / 6), "wr")
    return None


# picos ENQUADRANDO a chamine (x 37): ombros altos a oeste (-24) e a leste (68), sela baixa bem atras dela
# (a chamine, 152,2, segue >= 20 acima de tudo), nascente no pico leste (106)
BACK_PEAKS = [(-62.0, 552.0, 108.0), (-24.0, 566.0, 126.0), (6.0, 580.0, 114.0), (40.0, 584.0, 104.0),
              (68.0, 560.0, 121.0), (106.0, 552.0, 116.0), (-98.0, 552.0, 96.0), (86.0, 538.0, 104.0)]
RAVINE = [(128.0, 236.0), (140.0, 231.5), (150.0, 227.5), (157.0, 231.0), (170.0, 234.0)]
RAVINE_HW = 4.6


def in_ravine(x, y, pad=0.0):
    return L.polyline_dist(x, y, RAVINE) < RAVINE_HW + pad and x > 134.0


def near_floor(x, y, r=10.0):
    """(MENOR cota de piso num raio r, distancia ao piso mais proximo) por amostragem em 16 rumos x 3 raios"""
    best, dmin = None, 99.0
    for k in range(16):
        t = 2 * math.pi * k / 16
        for d in (r * 0.3, r * 0.65, r):
            z = zfloor(x + math.cos(t) * d, y + math.sin(t) * d)
            if z is not None:
                best = z if best is None else min(best, z)
                dmin = min(dmin, d)
                break
    return best, dmin


def fill_top(x, y):
    """topo DIRIGIDO do enchimento de rocha num ponto que nao e piso: regiao nomeada (crista, barranco, montanha) com a
    primeira fila mais baixa junto do piso; ombro generico = piso mais baixo vizinho + borda de rocha (+1,4 na beira,
    descendo para fora). Devolve (topo, piso vizinho, distancia)"""
    rt = region_top(x, y)
    zf, dmin = near_floor(x, y, 12.0)
    if rt is None:
        if zf is None:
            zf, dmin = near_floor(x, y, 30.0)
        zb = zf if zf is not None else L.SHOULDER + 4.0
        rt = zb + max(-1.2, min(1.4, 1.9 - 0.32 * dmin)) + 0.5 * hh(round(x, 1), round(y, 1), "v")
    elif zf is not None:
        rt = min(rt, zf + 3.0 + 1.6 * dmin)
    return rt, zf, dmin


def opening_any(x, y):
    return ds_col.opening(x, y)


def fit_top(verts2d, ztop, lower_only=False):
    """topo de coluna que NUNCA fura um piso andavel: vertice dentro de piso de cota zf -> topo <= zf - 0,4.
    lower_only=False: devolve None se o rebaixamento passa de 1,2 (o enchimento encolhe em vez de afundar)"""
    zt = ztop
    for x, y in verts2d:
        zf = zfloor(x, y)
        if zf is not None and zt > zf - 0.4:
            if not lower_only and ztop - (zf - 0.4) > 1.2:
                return None
            zt = zf - 0.4
        if opening_any(x, y):
            if not lower_only:
                return None
            zt = min(zt, (zf if zf is not None else zt) - 2.5)
    return zt


def foot(cx, cy, a, b, ang, s=1.08):
    ca, sa = math.cos(ang), math.sin(ang)
    out = []
    for k in range(8):
        t = 2 * math.pi * k / 8
        u, v = a * math.cos(t) * s, b * math.sin(t) * s
        out.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return out


# ------------------------------------------------------------------ 1. coroa + 2. quilha
def crown(mb):
    rim = DL.rim()
    rp = L.ISLAND_RIM
    steps = (9.0, 5.0, 7.2, 4.4, 11.0, 6.0, 8.2, 5.4, 6.6, 10.0, 4.8)
    outs = (0.4, 1.4, -0.2, 0.9, 2.2, 0.2, 1.1, -0.4, 1.6, 2.8, 0.0)
    drops = (0.4, 0.4, 1.1, 0.5, 2.4, 0.4, 0.9, 1.8, 0.4, 0.6, 3.2, 0.4)
    bots = (30.0, 38.0, 26.0, 41.0, 33.0, 24.0, 36.0, 29.0, 42.0, 31.0, 22.0, 35.0, 39.0)
    n = 0
    for i, (x, y, ang, st) in enumerate(tangent_frames(ccw(rp), steps)):
        nx_, ny_ = math.sin(ang), -math.cos(ang)            # para fora (contorno anti-horario)
        o = cyc(outs, i)
        cx, cy = x + nx_ * o, y + ny_ * o
        a = st * 0.6
        b = 3.2 + 1.8 * hh(i, "b")
        if in_ravine(cx, cy, 2.0):
            continue
        # cota de referencia: o piso/regiao logo para dentro
        zref = None
        for d in (4.0, 8.0, 13.0, 19.0):
            px, py = cx - nx_ * d, cy - ny_ * d
            zref = zfloor(px, py)
            if zref is None:
                zref = region_top(px, py)
            if zref is not None:
                break
        if zref is None:
            zref = near_floor(cx, cy, 24.0)[0] or L.SHOULDER
        zt = zref - cyc(drops, i)
        zt = fit_top(foot(cx, cy, a, b, ang), zt, lower_only=True)
        # pontes: a coroa passa POR BAIXO dos tabuleiros (encontro de pedra e do ds_entry / ds_exit)
        for nm, p0, p1, w in L.bridge_list():
            if ds_col._in_rect_along(cx, cy, p0, p1, w / 2 + 3.0, pad=6.0):
                zt = min(zt, p1[2] - 3.0)
        zb = cyc(bots, i) + (8.0 if zref > 76.0 else 0.0)
        # ONDA 4b: tom POR COLUNA (quente explicita / familia fria), capa verde que cai pela face de fora (musgo ou
        # grama funda), estrato de baixo escuro e faixas de musgo escorrendo (0..3 por coluna, ciclo dirigido)
        mcol = ROCKB if hh(i, "wm") < 0.38 else ROCK
        capm = GDEEP if hh(i, "cg") < 0.6 else MOSS
        # 6b (item 11): estratos da coroa 0,18 abaixo dos do enchimento (66/86 coplanares: musgo x rocha escura)
        column(mb, cx, cy, a * 0.92, b, ang, zt, zb, ("cr", i), m=mcol, cap=capm, strata=(STRATA, 65.82, 85.82),
               tip=2.0 + 4.0 * hh(i, "t"), mlow=ROCKD if hh(i, "ml") < 0.5 else ROCK, ledge=ROCKD, n=None, top_s=0.88, ch=0.4,
               tilt=(nx_, ny_, 0.2), drip=0.3 + 1.1 * hh(i, "dr"), drip_dir=(nx_, ny_, 2.0 + 3.0 * hh(i, "dd")),
               rec=(MOSS_REC, (nx_, ny_), (cyc((1, 0, 1, 2, 1, 0, 1), i), 4.0, 14.0)))
        n += 1
    return n


def keel(mb):
    ctrl = L.RIM_CTRL
    n = 0
    # 6b (orcamento): o anel de DENTRO (pontas a -12..-36, so visto de baixo das nuvens) em colunas ~1,7x mais largas
    # (passo 15 -> 25: a largura acompanha o passo, sem fresta) - paga parte do ishigaki/T4 da onda 6b
    for ring_i, (off, steps, ztop, bots, strata) in enumerate((
            (-5.5, (11.6, 9.4, 13.6, 10.0, 11.2), 41.0, (14.0, 4.0, 20.0, 8.0, 17.0, 0.0, 11.0), ()),
            (-16.0, (25.0, 21.0, 28.0, 23.0), 18.0, (-20.0, -32.0, -12.0, -26.0, -36.0, -16.0), ()))):
        poly = L.smooth_closed(DL.offset_poly(ctrl, off), 2)
        for i, (x, y, ang, st) in enumerate(tangent_frames(ccw(poly), steps)):
            nx_, ny_ = math.sin(ang), -math.cos(ang)
            a = st * 0.66
            b = 4.5 + 1.5 * hh(ring_i, i, "b")
            zt = ztop - 3.0 * hh(ring_i, i, "zt")
            column(mb, x + nx_ * 1.0, y + ny_ * 1.0, a, b, ang, zt, cyc(bots, i), ("kl", ring_i, i), m=ROCKD,
                   cap=ROCKD, strata=strata, tip=3.0 + 6.0 * hh(ring_i, i, "tip"), taper=0.0, ch=0.4, n=5)
            n += 1
    # nucleos ocultos (fecham as frestas entre os aneis)
    for off, z0, z1 in ((-3.0, 34.0, BASE), (-11.0, 8.0, 36.0), (-23.0, -18.0, 12.0)):
        poly = ccw(L.smooth_closed(DL.offset_poly(ctrl[::2], off), 1))
        mb.prism(poly, z0, z1, ROCKD)
    return n


# ------------------------------------------------------------------ 3. corpos dos patamares (ocultos) + leito
def bodies(mb):
    for nm, poly, z, pr in FLOORS:
        if callable(z):
            # 6b (item 05): o bambuzal so sobe entre y 28 e 132 (cota constante fora): o tampo inteiro era um n-gono
            # concavo NAO planar e a triangulacao subia ate 0,07 da grama na entrada do bambuzal. Agora 3 faixas planas
            for y0, y1 in ((-1e4, L.BAMBOO_Y0), (L.BAMBOO_Y0, L.BAMBOO_Y1), (L.BAMBOO_Y1, 1e4)):
                piece = L.clip_rect(ccw(poly), (-1e4, y0, 1e4, y1))
                if len(piece) >= 3 and L.area(piece) > 0.5:
                    DL.sloped_prism(mb, piece, BASE, lambda x, y, z=z: z(x, y) - BEDD, ROCKD, top_m=DIRTD)
            continue
        for piece in L.floor_pieces(nm):
            DL.prism(mb, piece, BASE, z - BEDD, ROCKD, top_m=DIRTD)
    for nm, up, rect, zf, zt in L.stair_notches():
        fill = L.clip_rect(ccw(L.floor_poly(up)), rect) if up else []
        if len(fill) >= 3:
            DL.prism(mb, fill, BASE, zf - 0.3, ROCKD)


# ------------------------------------------------------------------ 4. arrimos
WALL_KIND = {("Berm", "T1"): "rock", ("Summon", "T1"): "rock", ("Forge", "T1"): "rock",
             ("VillageHigh", "T1"): "ishi", ("Forge", "Berm"): "ishi", ("Forge", "VillageHigh"): "ishi",
             ("Berm", "VillageHigh"): "ishi", ("T1", "Bamboo"): "ishi", ("ExitLand", "VillageHigh"): "ishi",
             ("T1", "Entry"): "ishi", ("Bamboo", "Entry"): "ishi"}


def wall_runs():
    """trechos de borda de piso com desnivel para o vizinho (piso ou enchimento de rocha dentro do contorno):
    (cima, baixo, p0, p1, fora(nx, ny), z_cima, z_baixo, sentido). 'down' = o piso e o lado alto (arrimo do proprio
    piso); 'up' = o enchimento e mais alto (face de rocha/arrimo virada PARA o piso)"""
    out = []
    rim = L.ISLAND_RIM
    for nm, poly, z, pr in FLOORS:
        pts = ccw(poly)
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 0.5:
                continue
            nx_, ny_ = dy / ln, -dx / ln
            k = max(1, int(ln / 1.0))
            run, cur = [], None

            def flush(run, cur):
                if len(run) < 2:
                    return
                zo = [r[1] for r in run]
                p0, p1 = run[0][0], run[-1][0]
                if cur[1] == "down":
                    zt = max(floor_z(nm, *p0), floor_z(nm, *p1))
                    out.append((nm, cur[0], p0, p1, (nx_, ny_), zt, min(zo), "down"))
                else:
                    zb = min(floor_z(nm, *p0), floor_z(nm, *p1))
                    out.append((None, nm, p0, p1, (nx_, ny_), max(zo), zb, "up"))
            for s in range(k + 1):
                t = s / k
                x, y = a[0] + dx * t, a[1] + dy * t
                qx, qy = x + nx_ * 1.6, y + ny_ * 1.6
                key, zo = None, None
                if L.floor_name(x - nx_ * 0.6, y - ny_ * 0.6) == nm and not ds_col.opening(qx, qy):
                    zh = floor_z(nm, x, y)
                    lo = L.floor_name(qx, qy)
                    if lo is not None:
                        zo = L.zone_of(qx, qy)
                        if zh - zo > 1.0:
                            key = (lo, "down")
                    elif L.point_in_poly(qx, qy, rim) and L.poly_edge_dist(qx, qy, rim) > 3.0 \
                            and not in_ravine(qx, qy, 1.0):
                        zo = fill_top(qx, qy)[0]
                        if zh - zo > 1.0:
                            key = (None, "down")
                        elif zo - zh > 1.5:
                            key = (None, "up")
                if key != cur:
                    flush(run, cur)
                    run = []
                if key is not None:
                    run.append(((x, y), zo))
                cur = key
            flush(run, cur)
    return out


# 6b (item 03): o ishigaki lia TIJOLO (fiadas da mesma altura, junta vertical reta, face plana, sem quina nem talude).
#   Agora: fiadas de altura nominal DIRIGIDA pela cota do pe (muros vizinhos com o mesmo pe casam as fiadas e as quinas),
#   pedra a pedra: comprimento 1,8..3,4, ~30% ocupando 2 fiadas (quebra a junta continua), ~12% partidas em 2 pedras
#   de calco, giro de +-4 graus no plano da face, cantos da face soltos (+-0,07) e saliencia propria (+-0,08 de
#   recuo); talude CURVO (pe aberto, topo a prumo: media 9 graus nos muros > 6, 7 nos baixos); quinas em SANGI-ZUMI
#   (3:1, longa/curta alternando a cada fiada, o inicio e o fim do trecho ao contrario: na quina de 2 trechos as longas
#   se cruzam); 3 tons (Stone_DS_Ishi / IshiD / Stone_DS_B) abaixo da pedra clara das quinas; capa em pecas de ~2,5
#   com junta, altura e giro proprios e pingadeira de 0,1.
ISHI, ISHID, STONEB = "Stone_DS_Ishi", "Stone_DS_IshiD", "Stone_DS_B"
COURSES = (1.35, 1.1, 1.55, 1.2, 1.45, 1.0, 1.6)
LENS = (3.1, 2.2, 3.7, 2.6, 3.4, 2.0, 4.0, 2.8, 2.4)
CAPS = (2.6, 2.2, 2.9, 2.4, 2.7)
CAP_LOW = (-60.5, 424.0, 84.5, 439.0)     # borda sul do patio da forja: meio-fio do ds_forge (6b-C) a T4 + 0,32


def ishi_batter(H):
    """talude medio (tangente) do ishigaki: ~9 graus nos muros com mais de 6 de altura, 7 nos baixos"""
    return 0.16 if H > 6.0 else 0.12


def ishigaki(mb, p0, p1, nrm, zt, zb, key, batter=None, base=0.2, prs=(0.2, 0.12, 0.12), cap_out=None, backing=True,
             g=0.11, chf=0.16, avoid=None):
    """muro de ISHIGAKI (ver o comentario acima). p0 -> p1 com a face para nrm; base = afastamento da face no topo
    (0 = a face nasce na linha: bochecha de escada); prs = (saliencia minima, faixa, recuo +-); cap_out = quanto a capa
    sai da linha (None: face + pingadeira)"""
    nx_, ny_ = nrm
    ux, uy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(ux, uy)
    if ln < 0.6:
        return
    ux, uy = ux / ln, uy / ln
    H = zt - zb
    if H < 0.3:
        return
    B = ishi_batter(H) if batter is None else batter
    bm = mb.bm

    def off(v):
        t = max(0.0, min(1.0, 1.0 - v / H))
        return base + B * H * t ** 1.35

    def P(u, v, w):
        o = off(v) + w
        return (p0[0] + ux * u + nx_ * o, p0[1] + uy * u + ny_ * o, zb + v)

    def stone(u0, u1, v0, v1, pr, ch, m, rot=0.0, jk=None):
        cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
        cr, sr = math.cos(rot), math.sin(rot)

        def R(u, v):
            du, dv = u - cu, v - cv
            return cu + du * cr - dv * sr, cv + du * sr + dv * cr
        bk = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
        fr = ((u0 + ch, v0 + ch), (u1 - ch, v0 + ch), (u1 - ch, v1 - ch), (u0 + ch, v1 - ch))
        if avoid is not None and any(avoid(*P(*R(u, v), w)[:2]) for u, v in bk for w in (-0.04, pr + 0.06)):
            return
        back = [bm.verts.new(P(*R(u, v), -0.04)) for u, v in bk]
        front = []
        for k, (u, v) in enumerate(fr):
            ju, jv, jw = jk[k] if jk else (0.0, 0.0, 0.0)
            uu, vv = R(u + ju, v + jv)
            front.append(bm.verts.new(P(uu, vv, pr + jw)))
        bm.faces.new(front)
        for k in range(4):
            j = (k + 1) % 4
            bm.faces.new((back[k], back[j], front[j], front[k]))
        mb._post(back + front, m, None, 0, 1)
    e0, e1 = -0.6, ln + 0.6
    # fiadas: sequencia DIRIGIDA pela cota do pe, escalada para fechar a altura exata
    nc = max(1, int(round(H / 1.32)))
    c0 = int(round(zb * 2.0)) % len(COURSES)
    hs = [COURSES[(c0 + i) % len(COURSES)] for i in range(nc)]
    sc = H / sum(hs)
    courses, v = [], 0.0
    for h_ in hs:
        courses.append((v, h_ * sc))
        v += h_ * sc
    # junta: fundo escuro seguindo o talude curvo (1 faixa por fiada)
    if backing:
        spans = [(e0, e1)]
        if avoid is not None:                # trechos do fundo fora das escadas (passo 0,25)
            spans, cur, k = [], None, 0
            nk = max(1, int((e1 - e0) / 0.25))
            for k in range(nk + 1):
                uu = e0 + (e1 - e0) * k / nk
                ok = not any(avoid(*P(uu, vv, -0.05)[:2]) for vv in (0.0, H))
                if ok and cur is None:
                    cur = uu
                if not ok and cur is not None:
                    spans.append((cur, e0 + (e1 - e0) * (k - 1) / nk))
                    cur = None
            if cur is not None:
                spans.append((cur, e1))
        for sa, sb in spans:
            if sb - sa < 0.2:
                continue
            lo = [bm.verts.new(P(sa, 0.0, -0.05)), bm.verts.new(P(sb, 0.0, -0.05))]
            allv = list(lo)
            for c in courses:
                vv = c[0] + c[1]
                up = [bm.verts.new(P(sa, vv, -0.05)), bm.verts.new(P(sb, vv, -0.05))]
                bm.faces.new((lo[0], lo[1], up[1], up[0]))
                allv += up
                lo = up
            mb._post(allv, SDARK, None, 0, 1)
    quoin = ln > 6.0
    QL, QS = 3.0, 1.0

    def q_ends(ci):
        if not quoin:
            return e0, e1
        return e0 + (QL if ci % 2 == 0 else QS), e1 - (QS if ci % 2 == 0 else QL)
    occ = {}
    k0 = int(hh(key, "l") * 9)
    for ci, (v, hcr) in enumerate(courses):
        top_c = ci == len(courses) - 1
        qa, qb = q_ends(ci)
        if quoin:                       # sangi-zumi: pedra clara de quina, longa/curta alternando
            for ua, ub in ((e0, qa), (qb, e1)):
                jk = [((hh(key, ci, ua, k, "qu") - 0.5) * 0.08, 0.0, (hh(key, ci, ua, k, "qw") - 0.5) * 0.06)
                      for k in range(4)]
                stone(ua + 0.09, ub - 0.09, v + 0.09, v + hcr - 0.09, 0.34, 0.14, STONE, jk=jk)
        qa2, qb2 = q_ends(ci + 1) if ci + 1 < len(courses) else (qa, qb)
        ta, tb = max(qa, qa2), min(qb, qb2)          # faixa onde cabe pedra de 2 fiadas
        blocks = sorted(occ.get(ci, []))
        u, bi = qa, 0
        while u < qb - 0.3:
            blk = next((bb for bb in blocks if bb[0] - 0.05 <= u < bb[1]), None)
            if blk:
                u = blk[1]
                continue
            nxt = min([bb[0] for bb in blocks if bb[0] > u] + [qb])
            L_ = cyc(LENS, ci * 7 + bi + k0)
            if nxt - u - L_ < 1.2:
                L_ = nxt - u
            if L_ < 0.35:
                u = nxt
                continue
            tall = (not top_c and L_ > 1.5 and ta <= u and u + L_ <= tb and hh(key, ci, bi, "tall") < 0.35)
            v1 = v + hcr + (courses[ci + 1][1] if tall else 0.0)
            if tall:
                occ.setdefault(ci + 1, []).append((u, u + L_))
            last = v1 >= H - 0.05
            dt = 0.0 if last else 0.26 * hh(key, ci, bi, "dt")
            db = 0.0 if v <= 0.05 else 0.18 * hh(key, ci, bi, "db")
            hm = hh(key, ci, bi, "m")
            m = ISHID if hm < 0.16 else (STONEB if hm < 0.28 else ISHI)
            rot = (hh(key, ci, bi, "rot") - 0.5) * 0.16
            pr = prs[0] + prs[1] * hh(key, ci, bi) + (hh(key, ci, bi, "rc") - 0.5) * prs[2]
            jk = [((hh(key, ci, bi, k, "ju") - 0.5) * 0.18, (hh(key, ci, bi, k, "jv") - 0.5) * 0.2,
                   (hh(key, ci, bi, k, "jw") - 0.5) * 0.06) for k in range(4)]
            va, vb = v + g + db, v1 - g - dt
            if not tall and vb - va > 1.0 and L_ < 2.8 and hh(key, ci, bi, "sp") < 0.08:
                # pedra de calco: 2 pedras empilhadas (a de baixo maior)
                vm = va + (vb - va) * (0.55 + 0.1 * hh(key, ci, bi, "sv"))
                stone(u + g, u + L_ - g, va, vm - 0.08, pr, chf * 0.9, m, rot * 0.5, jk)
                stone(u + g + 0.2, u + L_ - g - 0.15, vm + 0.08, vb, pr * 0.8, chf * 0.75, ISHID if m == ISHI else ISHI,
                      -rot * 0.5)
            else:
                stone(u + g, u + L_ - g, va, vb, pr, chf, m, rot, jk)
            u += L_
            bi += 1
    # capa (kasa-ishi): pecas de ~2,5 com junta de 0,2, altura/giro proprios e pingadeira sobre a face (a face de fora
    # da capa fica >= 0,15 a frente da pedra mais saliente: nada paralelo a < 0,12); espessura 0,5 (nao desce pela
    # fiada de cima). Sobre a borda sul do patio da forja (onde o ds_forge pos o meio-fio dele a T4 + 0,32) a capa
    # desce 0,15 (o meio-fio fica 0,17 acima: sem coplanar)
    co = (base + prs[0] + prs[1] + prs[2] * 0.5 + 0.2) if cap_out is None else cap_out
    mid = (co - 0.9) / 2
    u, ci = -0.4, 0
    k0 = int(hh(key, "cp") * 5)
    while u < ln + 0.4:
        L_ = min(cyc(CAPS, ci + k0), ln + 0.4 - u)
        if L_ > 0.6:
            yaw = (hh(key, ci, "cy") - 0.5) * 0.035
            dz = (hh(key, ci, "cz") - 0.5) * 0.08
            cu = u + L_ / 2
            ca, sa = math.cos(yaw), math.sin(yaw)
            pts = []
            for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                du = su * (L_ / 2 - 0.1)
                dv = (-0.9 if sv < 0 else co) - mid
                ru, rv = du * ca - dv * sa, du * sa + dv * ca + mid
                pts.append((p0[0] + ux * (cu + ru) + nx_ * rv, p0[1] + uy * (cu + ru) + ny_ * rv))
            if avoid is not None and any(avoid(x_, y_) for x_, y_ in pts):
                u += L_
                ci += 1
                continue
            cx_ = sum(p_[0] for p_ in pts) / 4
            cy_ = sum(p_[1] for p_ in pts) / 4
            if CAP_LOW[0] <= cx_ <= CAP_LOW[2] and CAP_LOW[1] <= cy_ <= CAP_LOW[3] and abs(zt - T4) < 0.05:
                dz = -0.14                  # topo T4 + 0,16: 0,16 acima do chao do patio e 0,16 abaixo do meio-fio
            slab(mb, ccw(pts), lambda x, y: zt, 0.3 + dz, th=0.5, ch=0.0, m=PATH)
        u += L_
        ci += 1


def rock_wall(mb, mcol, p0, p1, nrm, zt, zb, key, recess=(), inward=False, collide=True):
    """falesia natural entre patamares: colunas que avancam 0,6..2,6 sobre o piso de baixo (colisao propria)"""
    nx_, ny_ = nrm
    ln = math.dist(p0, p1)
    if ln < 1.0:
        return
    ux, uy = (p1[0] - p0[0]) / ln, (p1[1] - p0[1]) / ln
    ang = math.atan2(uy, ux)
    steps = (5.2, 4.2, 6.0, 4.6, 5.6)
    outs = (1.2, 2.2, 0.8, 1.8, 2.6, 1.0)
    u, i = -1.0, 0
    maxo = 0.0
    while u < ln + 1.0:
        st = cyc(steps, i + int(hh(key, "s") * 5))
        uc = u + st / 2
        o = cyc(outs, i)
        x, y = p0[0] + ux * uc, p0[1] + uy * uc
        for (rx, ry, rr, rd) in recess:
            if math.dist((x, y), (rx, ry)) < rr:
                o -= rd
        if inward:                      # face para o piso, corpo para tras (dentro do enchimento)
            b = 2.6 + 0.8 * hh(key, i, "b")
            cx, cy = x - nx_ * (b + 0.1 - 0.4 * o), y - ny_ * (b + 0.1 - 0.4 * o)
        else:
            b = 2.4 + o / 2
            cx, cy = x + nx_ * (o - b), y + ny_ * (o - b)
        top = zt - cyc((0.15, 0.15, 0.6, 0.15, 1.1, 0.15, 0.3), i + int(hh(key, "t") * 7))
        aa = st * 0.54
        for sc in (1.0, 0.75, 0.5, 0.0):            # escada cortada no arrimo: o bloco nunca entra no lance
            if sc and not any(ds_col.opening(px, py) for px, py in foot(cx, cy, aa * sc, b * sc, ang, 1.0)):
                break
        if sc:
            hgt = zt - zb
            fx, fy = (-nx_, -ny_) if inward else (nx_, ny_)
            column(mb, cx, cy, aa * sc, b * sc, ang, top, zb - 1.0, (key, i), tip=0.0, ch=0.35, bottom=False,
                   flare=1.05, n=None, top_s=0.9, mlow=ROCK, ledge=MOSS, step_s=1.08, tilt=(fx, fy, 0.16),
                   drip=0.5 + 0.9 * hh(key, i, "dr"), m=ROCKB if hh(key, i, "wm") < 0.4 else ROCK,
                   cap=GDEEP if hh(key, i, "cg") < 0.4 else MOSS, drip_dir=(fx, fy, 0.8 + 1.4 * hh(key, i, "dd")),
                   rec=(MOSS_REC, (fx, fy), (cyc((0, 0, 1, 0, 1), i), 1.6, min(5.0, hgt * 0.5))),
                   strata=(zb + hgt * (0.3 + 0.12 * hh(key, i, "st")),) if hgt > 5.0 else ())
            # blocos caidos ao pe (dentro da faixa da colisao quando ha piso embaixo)
            if hh(key, i, "tal") > 0.4:
                r = 0.7 + 0.6 * hh(key, i, "tr")
                dd = (o + 0.2 + r * 0.4) if not collide else min(o + 0.2, 1.9 - r * 0.3)
                if inward:
                    dd = 0.2 + r * 0.5
                px, py = x + fx * dd + ux * (hh(key, i, "tu") - 0.5) * st * 0.6, y + fy * dd + uy * (hh(key, i, "tu") - 0.5) * st * 0.6
                if not ds_col.opening(px, py):
                    boulder(mb, px, py, zb, r, 0.6 + 1.0 * hh(key, i, "th"), (key, i, "tal"), m=ROCK, ang=ang, n=5)
        maxo = max(maxo, o)
        u += st
        i += 1
    # colisao: a face de rocha que avanca sobre o piso de baixo (o piso de cima ja e macico no ds_col)
    if not collide or inward:
        return
    k = max(1, int(ln / 10.0))
    for j in range(k):
        a, b = j / k * ln, (j + 1) / k * ln
        m_ = ((a + b) / 2)
        cx, cy = p0[0] + ux * m_ + nx_ * maxo * 0.45, p0[1] + uy * m_ + ny_ * maxo * 0.45
        col_box("DS_TerWall", (b - a + 0.6, maxo * 0.9, zt - zb), (cx, cy, (zt + zb) / 2), (0, 0, ang))


def wall_kind(up, low, zt, zb, p0):
    """construido (ishigaki) junto da entrada, da trilha, da vila e na frente da forja; natural (rocha) no resto"""
    if (up, low) in WALL_KIND:
        return WALL_KIND[(up, low)]
    if low is None and up in ("T1", "Entry", "VillageHigh") and zt - zb <= 7.5 and region_top(*p0) is None:
        return "ishi"
    if up is None and low in ("Entry", "T1") and p0[1] < 140.0 and region_top(*p0) is None:
        return "ishi"
    return "ishi" if (low is not None and up is not None and zt - zb <= 7.0) else "rock"


def notch_cheeks(mb):
    """escada cortada no arrimo: as 2 faces laterais do entalhe (o corpo do patamar de cima) viram ISHIGAKI a prumo,
    so no trecho DENTRO do patamar de cima (fora dele nao ha face a fechar); os banzos da escada ficam na frente"""
    n = 0
    for nm, up, rect, zf, zt in L.stair_notches():
        if up is None:
            continue
        foot, deg, w, ns, tread, g = L.stair_frame(nm)
        a = math.radians(deg)
        ux, uy = round(math.cos(a)), round(math.sin(a))
        top = L.stair_top(nm)
        hw = w / 2 + 1.25
        for s in (-1, 1):
            vx, vy = -uy * s, ux * s                         # lado (para fora do lance)
            pts = []
            t, tmax = -tread, tread * ns + 0.5
            while t <= tmax:
                x = foot[0] + ux * t + vx * (hw + 0.3)
                y = foot[1] + uy * t + vy * (hw + 0.3)
                # 6b: tambem onde o lado do lance e ENCHIMENTO (ex.: crista oeste ao lado da escada Trilha): o arrimo
                # diagonal da crista agora fica fora da largura da escada e a face do entalhe precisa da bochecha
                fl = L.floor_name(x, y)
                if fl == up or (fl is None and L.point_in_poly(x, y, L.ISLAND_RIM) and t > tread):
                    pts.append((foot[0] + ux * t + vx * hw, foot[1] + uy * t + vy * hw))
                t += 0.5
            if len(pts) < 3:
                continue
            p0, p1 = pts[0], pts[-1]
            # a face olha para o lance (-v). 6b (item 01): a linha era recuada 0,6 para dentro do patamar e as pedras
            # (saliencia <= 0,4) ficavam DENTRO do corpo do patamar: so a capa aparecia sobre a face lisa do
            # DS_Ter_Bodies. Agora a face nasce NA face do corpo (base 0, sem fundo de junta: a junta mostra o corpo
            # escuro) e as pedras ocupam os 0,25 entre o corpo e os banzos da escada (saliencia 0,06..0,2)
            q0, q1 = p0, p1
            ux2, uy2 = q1[0] - q0[0], q1[1] - q0[1]
            if (uy2 * -vx - ux2 * -vy) < 0:                 # sentido tal que a direita do trecho = -v
                q0, q1 = q1, q0
            # 6c: capa RECUADA 0,15 atras da linha (era 0,0: a face da capa ficava NO plano da borda da pele do patamar,
            # Dirt_DS x Stone_DS_Path a 0,0-0,02 no topo das bochechas, ex. SubidaA (6,75; 388; 70,1)). Para a frente
            # nao da: a fiada de cima sai 0,19-0,24 (a capa ficaria a < 0,12 dela) e o banzo esta a 0,18-0,32
            ishigaki(mb, q0, q1, (-vx, -vy), zt, zf - 0.5, ("ch", nm, s), batter=0.0, base=0.0, prs=(0.19, 0.04, 0.02),
                     cap_out=-0.15, backing=False, g=0.06, chf=0.08)
            n += 1
    return n


STAIR_CLEAR = []


def stair_clear(x, y):
    """6b (pedido do 6b-B, item 32): o ishigaki dos arrimos fica >= 0,3 FORA da largura das escadas e dos banzos
    (pe - meio piso .. topo + 0,3; meia-largura + banzo 1,0 + 0,3). Ex.: OesteForja, face em x -70,6 contra a borda
    da escada em -71 perto de (-71,3; 371,7; 73)"""
    if not STAIR_CLEAR:
        for nm, foot, deg, w, n, tread, g in L.STAIRS:
            a = math.radians(deg)
            ux, uy = round(math.cos(a)), round(math.sin(a))
            # meia-largura + 0,75: >= 0,75 fora da largura da escada; a faixa externa do banzo (0,25) fica livre porque
            # a face do entalhe esta a 0,25 do banzo (sem ela as faces do entalhe/crista ficam lisas)
            STAIR_CLEAR.append((foot, ux, uy, -tread / 2 - 0.3, tread * n + 0.3, w / 2 + 0.75))
    for foot, ux, uy, t0, t1, hw in STAIR_CLEAR:
        dx, dy = x - foot[0], y - foot[1]
        t, v = dx * ux + dy * uy, -dx * uy + dy * ux
        if t0 <= t <= t1 and abs(v) <= hw:
            return True
    return False


def walls(mb_i, mb_r):
    n_i = n_r = 0
    cascade = (L.CASCADE[0], L.CASCADE[1], 7.0, 1.6)
    for k, (up, low, p0, p1, nrm, zt, zb, sense) in enumerate(wall_runs()):
        if math.dist(p0, p1) < 1.5:
            continue
        kind = wall_kind(up, low, zt, zb, p0)
        if sense == "up":
            # face virada para o piso (lado baixo): a linha recua para dentro do enchimento (nada invade o piso)
            nx_, ny_ = nrm
            H = zt - zb
            sh = (0.2 + ishi_batter(H + 0.5) * (H + 0.5) + 0.3) if kind == "ishi" else 0.3
            q0 = (p1[0] + nx_ * sh, p1[1] + ny_ * sh)
            q1 = (p0[0] + nx_ * sh, p0[1] + ny_ * sh)
            if kind == "ishi":
                ishigaki(mb_i, q0, q1, (-nx_, -ny_), zt, zb - 0.5, ("iu", k), avoid=stair_clear)
                n_i += 1
            else:
                rock_wall(mb_r, None, q0, q1, (-nx_, -ny_), zt + 0.4, zb, ("ru", k), inward=True, collide=False)
                n_r += 1
            continue
        if kind == "rock":
            rock_wall(mb_r, None, p0, p1, nrm, zt, zb, ("rw", k), recess=(cascade,), collide=low is not None)
            n_r += 1
        else:
            ishigaki(mb_i, p0, p1, nrm, zt, zb - 0.5, ("iw", k), avoid=stair_clear)
            n_i += 1
    return n_i, n_r


# ------------------------------------------------------------------ 5. enchimento (o que nao e piso dentro do contorno)
def fill(mb):
    n = 0
    for sp in (7.6, 9.0):
        n += _fill_pass(mb, sp)
    _fill_cores(mb)
    return n


def _fill_pass(mb, sp):
    rim = L.ISLAND_RIM
    xs = [p[0] for p in rim]
    ys = [p[1] for p in rim]
    n = 0
    j = 0
    y = min(ys) + 2.0
    while y < max(ys):
        x = min(xs) + (sp / 2 if j % 2 else 0.0)
        while x < max(xs):
            jx = (hh(x, y, "jx") - 0.5) * 2.4
            jy = (hh(x, y, "jy") - 0.5) * 2.4
            cx, cy = x + jx, y + jy
            x += sp
            if not L.point_in_poly(cx, cy, rim) or L.poly_edge_dist(cx, cy, rim) < 2.5:
                continue
            if L.point_in_poly(cx, cy, L.BACK_ROCKS) != (sp < 8.0):
                continue
            if zfloor(cx, cy) is not None or opening_any(cx, cy) or in_ravine(cx, cy, 0.5):
                continue
            if L.point_in_poly(cx, cy, VALA):           # 6b (item 02): o talude plantado da vala ocupa o lugar
                continue
            rt, zf, dmin = fill_top(cx, cy)
            ang = hh(cx, cy, "a") * math.pi
            a = sp * (0.6 + 0.12 * hh(cx, cy, "ra"))
            b = sp * (0.52 + 0.1 * hh(cx, cy, "rb"))
            ok = None
            for s in (1.0, 0.8, 0.62):
                ok = fit_top(foot(cx, cy, a * s, b * s, ang), rt)
                if ok is not None:
                    a, b = a * s, b * s
                    break
            if ok is None:                      # nao coube acima do piso vizinho: afunda (borda rente), nunca buraco
                ok = fit_top(foot(cx, cy, a, b, ang), rt, lower_only=True)
            zlow = min((zf if zf is not None else L.SHOULDER) - 2.0, ok - 6.0)
            kk = ("fl", round(cx, 1), round(cy, 1))
            back = L.point_in_poly(cx, cy, L.BACK_ROCKS)
            if back:                    # montanha: colunas mais esguias, topo quebrado em degraus dirigidos
                a, b = a * 0.8, b * 0.8
                ok += cyc((0.0, 3.5, -2.0, 6.0, 1.0, -3.5, 4.5), int(hh(*kk) * 7))
            # ONDA 4b: tom por coluna; perto da borda (ou na montanha) a face de FORA ganha capa caindo e musgo
            edge_d = L.poly_edge_dist(cx, cy, rim)
            ox, oy = cx - 20.0, cy - 300.0
            ol = math.hypot(ox, oy) or 1.0
            outd = (ox / ol, oy / ol) if (back or edge_d < 16.0) else None
            column(mb, cx, cy, a, b, ang, ok, zlow if ok < 76.0 else 74.0, kk, m=ROCKB if hh(*kk, "wm") < 0.36 else ROCK,
                   cap=GDEEP if (outd and hh(*kk, "cg") < 0.45) else MOSS,
                   strata=(86.0, 98.0, 110.0) if ok > 90.0 else ((66.0,) if ok > 70.0 else ()), tip=0.0, bottom=False,
                   n=None, top_s=0.86, ch=0.45, drip=0.4 + 1.0 * hh(*kk, "dr"),
                   tilt=(math.cos(ang * 3.1), math.sin(ang * 3.1), 0.22 if back else 0.12), ledge=MOSS, mlow=ROCK,
                   drip_dir=(outd[0], outd[1], 1.2 + 2.0 * hh(*kk, "dd")) if outd else None,
                   rec=(MOSS_REC, outd, (cyc((1, 0, 0, 1, 0), int(hh(*kk, "ns") * 5)), 3.0, 11.0)) if outd else None)
            n += 1
        y += sp * 0.866
        j += 1
    return n


def _fill_cores(mb):
    # nucleos ocultos das regioes altas (a fresta entre colunas mostra rocha escura, nao o vazio)
    for poly, zt in ((L.WEST_RIDGE, 62.5), (L.NE_BANK, 68.0), (L.BACK_ROCKS, 84.0)):
        DL.prism(mb, DL.offset_poly(poly, -1.2), BASE, zt, ROCKD, top_m=MOSS)
    # ombro oculto: onde nenhuma coluna coube, aparece rocha com musgo 1,6 abaixo do patio mais baixo (nunca o vazio)
    DL.prism(mb, DL.offset_poly(L.RIM_CTRL, -2.0), BASE, L.SHOULDER - 1.0, ROCKD)


# ------------------------------------------------------------------ 5b. vala da escada Trilha (6b, item 02)
# A VALA ao lado da escada Trilha (entre o banzo direito, o patio T0, o bambuzal e o arrimo do T1) era um fosso de ~1,5
# com fundo de rocha escura: o 1o quadro depois do torii lia emenda nao terminada. Vira um TALUDE PLANTADO: leito de
# terra subindo do patio (+0,28) ao pe do arrimo (+2,2), meio-fio de pedras na borda do patio, 8 pedras de 1..2 meio
# enterradas no talude e pedras de borda no labio do bambuzal (as samambaias sao do ds_entry). Sem colisao: a guarda
# invisivel da borda do patio (COL_DS_Guard) ja fecha a vala.
VALA = [(-4.6, 42.2), (8.0, 42.2), (8.0, 53.6), (-4.6, 53.6)]


def vala_z(x, y):
    return T0 + 0.28 + max(0.0, min(1.0, (y - 42.2) / 11.4)) * 1.9


def vala_bed(mb_g):
    bm = mb_g.bm
    P = ccw(VALA)
    top = [bm.verts.new((x, y, vala_z(x, y))) for x, y in P]
    bot = [bm.verts.new((x, y, T0 - 1.6)) for x, y in P]
    bm.faces.new(top)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((bot[i], bot[j], top[j], top[i]))
    mb_g._post(top + bot, GDEEP, None, 0, 1)            # leito de musgo/grama funda sob as samambaias


def vala_stones(mb_s):
    mats = (STONEB, ISHI, ISHID, ISHI, STONEB)
    n = 0
    # meio-fio na borda do patio
    for i, x in enumerate((-3.2, -0.9, 1.5, 3.9, 6.4)):
        r = 0.98 + 0.2 * hh(i, "vm")
        boulder(mb_s, x, 42.95, T0 + 0.1, r, 0.68 + 0.2 * hh(i, "vh"), ("vm", i), m=cyc(mats, i), ang=0.3 * i)
        n += 1
    # pedras do talude (meio enterradas)
    for i, (x, y, r, hgt) in enumerate(((-2.4, 46.4, 1.5, 1.0), (5.0, 46.8, 1.8, 1.2), (0.4, 50.0, 2.0, 1.4),
                                        (4.6, 51.6, 1.4, 1.1), (6.9, 49.0, 1.2, 0.9), (-3.0, 51.8, 1.6, 1.5),
                                        (2.2, 45.0, 0.9, 0.6))):
        boulder(mb_s, x, y, vala_z(x, y) - 0.15, r, hgt, ("vt", i), m=cyc(mats, i + 2), ang=hh(i, "va") * 3.0)
        n += 1
    # labio do bambuzal: pedras de borda (a laje fina de terra some atras delas)
    for i, y in enumerate((43.3, 45.6, 47.9, 50.2, 52.5)):
        boulder(mb_s, 7.9, y, L.bamboo_z(8.0, y) - 0.1, 0.8 + 0.15 * hh(i, "vb"), 0.6, ("vb", i), m=cyc(mats, i + 1),
                ang=1.2 + 0.4 * i)
        n += 1
    return n


# ------------------------------------------------------------------ 6. ravina leste (sangradouro)
def ravine(mb):
    # leito em degraus: do fim do canal (T1) ao labio (53,6) - pedra escura molhada; colunas dos lados ja vem do fill
    steps = [((132.0, 235.0), (142.0, 231.0), T1 - 0.6), ((142.0, 231.0), (149.5, 228.0), T1 - 3.2),
             ((149.5, 228.0), (158.5, 231.5), L.SHOULDER)]
    for k, (a, b, z) in enumerate(steps):
        ln = math.dist(a, b)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        column(mb, c[0], c[1], ln / 2 + 1.4, RAVINE_HW + 0.6, ang, z, 30.0 - k * 4, ("rv", k), m=ROCKD, cap=SDARK,
               taper=0.6, tip=4.0, ch=0.35, n=6)
    # paredes do corte (2 fileiras de colunas altas nas margens) - a agua cai no vao entre elas
    for s in (-1, 1):
        for i, (x, y, ang, st) in enumerate(tangent_frames(RAVINE, (4.6, 3.8, 5.2), closed=False)):
            nx_, ny_ = -math.sin(ang) * s, math.cos(ang) * s
            cx, cy = x + nx_ * (RAVINE_HW + 2.0), y + ny_ * (RAVINE_HW + 2.0)
            if zfloor(cx, cy) is not None:
                continue
            zt = fit_top(foot(cx, cy, st * 0.62, 2.6, ang), T1 + 1.2 + 1.6 * hh(i, s, "rv"), lower_only=True)
            column(mb, cx, cy, st * 0.62, 2.6, ang, zt, 20.0 + 6.0 * hh(i, s, "rb"), ("rvw", s, i),
                   strata=(STRATA,), tip=3.0)


# ------------------------------------------------------------------ 7. chao: pele, grama, lajes, clareira
TRAIL_PATH = [(-12.0, 54.0), (-11.0, 70.0), (-8.5, 88.0), (-4.0, 106.0), (1.5, 122.0), (7.0, 136.0), (12.0, 148.0)]
TRAIL_HW = 3.4


def exit_bed_poly():
    """pegada EXATA do berco do caminho de saida do ds_exit (onda 1c: polilinha e largura proprias, berco escuro em
    T4 + 0,04..0,12): a pele some so ali (sem z-fight e sem sobra de leito a mostra). Sem o ds_exit: a faixa da planta"""
    try:
        import ds_exit as E
        fr = E._path_frames(E.PATH)
        total = fr[-1][0]
        left, right = [], []
        for s, x, y, dx, dy in fr[::8] + [fr[-1]]:
            hw = E._width(s, total) + 0.35
            left.append((x - dy * hw, y + dx * hw))
            right.append((x + dy * hw, y - dx * hw))
        return ccw(left + list(reversed(right)))
    except Exception:
        return ccw(L.ribbon(L.EXIT_PATH, 3.2))


def exit_deck_poly():
    """6b (item 15): pegada do inicio do tabuleiro da ponte de saida (u -0,7..6, v +-10,6): a pele some ali (leito 0,5
    abaixo) - era Dirt 0,1 sob a madeira do tabuleiro"""
    return ccw([L.exit_point(-0.7, -10.6), L.exit_point(6.0, -10.6), L.exit_point(6.0, 10.6), L.exit_point(-0.7, 10.6)])


def exit_band(X, Y):
    """6b (item 15): o CAMINHO DE SAIDA e terra batida clara NA PELE (material por regiao na mesma cota), nao mais um
    leito aberto que o ds_exit enchia (o enchimento ficava coplanar com a pele vizinha de outro material). A faixa sai
    0,45 alem do berco das lajes do ds_exit, com borda irregular"""
    return sdf_poly(X, Y, exit_bed_poly()) + 0.45 + 0.35 * waves(X, Y, 23.9, 2.3)


def bed_regions(X, Y):
    """onde a pele NAO existe (piso de outro modulo ou agua): leito 0,5 abaixo. Campo positivo dentro."""
    fs = [sdf_rect(X, Y, L.FORGE_YARD) + 0.2, sdf_rect(X, Y, L.CLIMB_LAND) + 0.2,
          sdf_line(X, Y, L.VILLAGE_STREET, 3.7), sdf_line(X, Y, L.VILLAGE_STREET_HIGH, 3.7),
          sdf_poly(X, Y, exit_deck_poly()),
          sdf_poly(X, Y, L.POND) + 0.6, sdf_line(X, Y, L.CHANNEL, 2.5), sdf_line(X, Y, L.TAILRACE, 2.5)]
    out = fs[0]
    for f in fs[1:]:
        out = np.maximum(out, f)
    return out


def floor_fields(G):
    """campo efetivo de cada piso (sem os de maior prioridade e sem os entalhes das escadas)"""
    X, Y = G.X, G.Y
    raw = {}
    for nm, poly, z, pr in FLOORS:
        f = None
        for piece in L.floor_pieces(nm):
            s = sdf_poly(X, Y, ccw(piece))
            f = s if f is None else np.maximum(f, s)
        raw[nm] = f
    eff = {}
    for nm, poly, z, pr in FLOORS:
        f = raw[nm]
        for nm2, poly2, z2, pr2 in FLOORS:
            if pr2 > pr:
                f = np.minimum(f, -raw[nm2])
        eff[nm] = f
    return eff


SKIN = {"Entry": DIRTD, "T1": DIRT, "Bamboo": DIRT, "VillageHigh": DIRT, "Berm": DIRT, "Summon": DIRT,
        "Forge": DIRTD, "ExitLand": DIRT}


# ONDA 4b: trilhas de PASSAGEM na borda da clareira (onde as rotas cruzam a faixa de grama): a grama abre e a pele
# fica em terra ESCURA (calcada). So FORA da MiningZone (no miolo a terra batida e uma so).
CLR_TRACKS = [([(12.0, 148.0), (20.0, 166.0), (30.0, 186.0)], 2.6),             # trilha -> antecampo
              ([(66.0, 132.0), (63.0, 150.0), (58.0, 172.0)], 2.2),             # bambuzal -> antecampo
              ([(16.0, 336.0), (16.0, 356.0), (17.0, 378.0)], 2.4),             # pe da SubidaA
              ([(101.0, 296.0), (112.0, 299.0), (124.0, 300.0)], 2.2),          # pontezinha do summon
              ([(-11.0, 284.0), (-28.0, 284.0), (-42.0, 284.0)], 2.2),          # VilaClareira
              ([(-11.0, 230.0), (-24.0, 222.0), (-34.0, 208.0)], 1.8),          # poco/hokora
              ([(101.0, 200.0), (112.0, 190.0)], 1.8)]                          # arvore sudeste
# tom da grama por piso (semente das manchas de verde)
TONE_SEED = {"T1": 9.4, "Bamboo": 2.7, "VillageHigh": 5.9, "Berm": 7.3, "Summon": 1.9, "Forge": 8.8, "ExitLand": 3.3,
             "Entry": 4.6}
# trilhas de passagem nos campos de grama fora da clareira (rotas do plano 4.4 que cruzam a grama)
FIELD_TRACKS = {"Berm": [([(-14.0, 405.0), (-30.0, 398.0), (-46.0, 383.0)], 1.9),              # patamar -> oeste
                         ([(46.0, 408.0), (66.0, 401.0), (88.0, 408.0), (98.0, 420.0)], 1.9)],  # -> mirante leste
                "VillageHigh": [([(-50.0, 284.0), (-62.0, 286.0), (-76.0, 290.0)], 1.9)],
                "ExitLand": [([(-100.0, 524.0), (-92.0, 548.0), (-86.0, 574.0)], 1.6)]}


# 6b (item 04): o T4 OESTE (chegada da OesteForja, patio do carvao, inicio do caminho de saida) era UM poligono de terra
# escura de 278 x 167 com as lanternas espetadas no vazio. Agora: 3 TRILHAS (as mesmas linhas das lanternas do ds_props
# 'Carvao' e 'FrgPatio' - quem alinhar lanterna use estas polilinhas), terra batida CLARA em manchas de pisoteio e ao
# longo das trilhas (material por regiao NA MESMA cota), grama seca em manchas e uma faixa de grama na borda oeste e no
# pe do muro sul, lajes irregulares com meio-fio na trilha do patio (rota principal para a saida), pisantes nas outras
# duas e pedras de borda. NADA dentro do FORGE_YARD (o patio da forja e do ds_forge).
T4_TRAILS = {
    "Carvao": ([(-66.0, 375.6), (-62.0, 396.0), (-55.0, 416.0), (-46.0, 428.0), (-40.0, 435.2)], 1.7, "pisantes"),
    "Patio": ([(-60.5, 448.2), (-70.0, 449.0), (-86.0, 450.6), (-101.5, 452.0)], 1.5, "lajes"),
    "Forno": ([(-66.0, 375.6), (-78.0, 381.0), (-92.0, 386.2), (-106.5, 390.0)], 1.6, "pisantes"),
}
T4_WEST_X = -18.0                   # o tratamento do T4 vale a oeste disso (a leste e o patio do ds_forge / a berma)
KILN = (-112.0, 400.0, 8.5)         # carvoeira do ds_forge (x, y, raio livre)


def t4_trails_f(X, Y, pad=0.0):
    out = None
    for nm, (pts, hw, kind) in T4_TRAILS.items():
        f = sdf_line(X, Y, pts, hw + pad + 0.35 * waves(X, Y, 19.3, 2.2))
        out = f if out is None else np.maximum(out, f)
    return out


def t4_trampled(X, Y):
    """terra batida CLARA no T4 oeste (> 0): faixa das trilhas, manchas de pisoteio nos nos (topo da OesteForja, frente
    da carvoeira, borda do patio) e manchas largas dirigidas"""
    f = t4_trails_f(X, Y, 0.9)
    for px, py, r in ((-66.0, 379.0, 6.5), (-106.0, 391.0, 5.5), (-62.0, 447.0, 5.0), (-48.0, 425.0, 4.0)):
        f = np.maximum(f, r + 1.2 * waves(X, Y, 3.3, 2.0) - np.hypot(X - px, Y - py))
    f = np.maximum(f, (waves(X, Y, 41.3, 1.25) + 0.3 * waves(X, Y, 8.1, 2.6) - 0.45) * 7.0)
    # nunca encostando no chao do ds_forge (patio + frente das oficinas: DS_Frg_Ground passa do FORGE_YARD para o norte)
    f = np.minimum(f, -(sdf_rect(X, Y, (L.FORGE_YARD[0] - 1.5, L.FORGE_YARD[1] - 1.5, L.FORGE_YARD[2], 600.0)) + 0.5))
    return np.where(X < T4_WEST_X, f, -1.0)


def clr_tracks(X, Y):
    out = None
    for pts, hw in CLR_TRACKS:
        f = sdf_line(X, Y, pts, hw + 0.5 * waves(X, Y, 12.1, 2.0))
        out = f if out is None else np.maximum(out, f)
    return np.minimum(out, -(sdf_rect(X, Y, L.MINE_RECT) + 0.5))


MIOLO_SPOTS = [(6.0, 204.0, 7.0), (48.0, 196.0, 6.0), (84.0, 226.0, 8.0), (22.0, 262.0, 6.5), (66.0, 276.0, 7.5),
               (4.0, 312.0, 6.0), (86.0, 314.0, 6.5)]


def clr_dark(X, Y):
    """terra ESCURA na pele da clareira (> 0): manchas de terra calcada/umida (so material, sem relevo) + trilhas.
    Mais perto da grama (transicao terra -> grama), rara no miolo"""
    clr = sdf_poly(X, Y, ccw(L.CLEARING))
    mt = waves(X, Y, 21.3, 1.05) + 0.25 * waves(X, Y, 5.1, 2.4) - 0.95 + 0.75 * np.clip(1.0 - (clr - 14.0) / 22.0, 0.0, 1.0)
    out = np.maximum(mt * 8.0, clr_tracks(X, Y))
    # 6b (item 06): o MIOLO (MiningZone) era uma cor so: 7 manchas largas de terra escura (calcada/umida), mesma cota
    for px, py, r in MIOLO_SPOTS:
        out = np.maximum(out, r + 2.2 * waves(X, Y, 31.7 + px * 0.01, 1.7) - np.hypot(X - px, (Y - py) * 0.8))
    return out


def tone_parts(nm, X, Y, bias):
    """pedacos de TOM de uma camada de grama (campos que eram um verde so): funda > B > base > seca, manchas largas
    dirigidas (ondas fixas) + vies (borda da clareira e beira das falesias puxam para o funda)"""
    t = 0.85 * waves(X, Y, TONE_SEED.get(nm, 0.0), 0.85) + bias
    return [(t - 0.5, GDEEP), (np.minimum(t + 0.45, 0.5 - t), GRASS), (np.minimum(t + 0.95, -0.45 - t), GRASSB),
            (-0.95 - t, GDRY)]


def grass_cover(nm, X, Y):
    """cobertura de grama DIRIGIDA por piso (> 0 = grama). As trilhas de terra ficam onde ela abre."""
    w = waves(X, Y, {"T1": 0.3, "Bamboo": 1.1, "VillageHigh": 2.2, "Berm": 3.1, "Summon": 4.0, "Forge": 5.2,
                     "ExitLand": 6.1}.get(nm, 0.0))
    if nm == "T1":
        # clareira: terra no miolo, grama so na transicao da borda (anel irregular) e em poucas manchas
        clr = sdf_poly(X, Y, ccw(L.CLEARING))
        ring = 9.0 + 4.0 * w - clr                          # ~9..13 a partir da borda da clareira para dentro
        vil = 1.3 + 2.6 * w                                 # fora da clareira (trilha, vila baixa): grama em manchas
        # ONDA 4b: a faixa de grama da borda fica larga e RASGADA (2a onda mais fina: ilhas de grama soltas) e a
        # grama rala se espalha em manchas pequenas ate ~44 da borda, rareando para dentro
        w2 = waves(X, Y, 15.7, 2.6)
        ring = 21.0 + 6.0 * w + 4.0 * w2 - clr
        rala = np.minimum((waves(X, Y, 33.0, 2.5) + 0.3 * w2 - 0.58 - 0.012 * np.maximum(0.0, clr - 16.0)) * 6.0,
                          np.minimum(clr - 8.0, 46.0 - clr))
        ring = np.maximum(ring, rala)
        g = np.where(clr > 0, ring, vil)
        mine = sdf_rect(X, Y, L.MINE_RECT)
        g = np.where(mine > 6.0, -1.0, g)                   # miolo da zona: terra limpa
        for (px, py, r) in ((-6.0, 196.0, 5.5), (96.0, 214.0, 4.5), (-4.0, 318.0, 5.0), (94.0, 322.0, 4.0),
                            (40.0, 186.0, 3.5)):
            g = np.maximum(g, r + 0.8 * w - np.hypot(X - px, Y - py))
        # caminhos de terra batida: trilha -> antecampo, margem oeste (vila -> VilaClareira), pe da subida, summon
        for pts, hw in (([(12.0, 148.0), (20.0, 166.0), (30.0, 186.0)], 3.0),
                        ([(-30.0, 104.0), (-28.0, 150.0), (-30.0, 214.0), (-34.0, 284.0), (-24.0, 330.0),
                          (2.0, 362.0), (16.0, 376.0)], 2.6),
                        ([(60.0, 150.0), (90.0, 180.0), (110.0, 240.0), (112.0, 290.0), (116.0, 300.0)], 2.6),
                        ([(-40.0, 112.0), (-30.0, 104.0)], 2.4)):
            g = np.minimum(g, -sdf_line(X, Y, pts, hw + 0.6 * w))
        g = np.minimum(g, -(clr_tracks(X, Y) + 0.3))        # ONDA 4b: trilhas de passagem na borda da clareira
        return g
    if nm == "Bamboo":
        g = 2.0 + 2.2 * w
        return np.minimum(g, -sdf_line(X, Y, L.BAMBOO_RAMP, 3.0 + 0.5 * w))
    if nm == "VillageHigh":
        return _tracks(nm, X, Y, 1.0 + 2.6 * w)
    if nm == "Berm":
        # ONDA 4b: o patamar era um campo liso: clareiras de terra em manchas + trilhas de passagem
        return _tracks(nm, X, Y, np.minimum(2.6 + 1.6 * w, 2.2 + 2.4 * waves(X, Y, 17.2, 2.2)))
    if nm == "Summon":
        r = np.hypot(X - L.SUMMON_C[0], Y - L.SUMMON_C[1])
        g = r - 17.0 + 3.0 * w
        return np.minimum(g, -sdf_line(X, Y, [(150.0, 300.0), (168.0, 300.0)], 2.8))
    if nm == "Forge":
        # terra escura de trabalho na frente; grama so no fundo e nas pontas
        g = -1.0 + 3.0 * w + (Y - 500.0) * 0.12 + np.maximum(0.0, -X - 80.0) * 0.08
        # 6b (item 04): T4 oeste - grama seca em manchas, faixa na borda oeste e no pe do muro sul (transicao ao muro),
        # nunca nas trilhas, na terra batida nem em volta da carvoeira
        dF = sdf_poly(X, Y, ccw(L.FORGE_TERR))
        west = np.maximum((waves(X, Y, 27.7, 1.1) + 0.3 * waves(X, Y, 6.6, 2.4) - 0.12) * 6.0,
                          (-131.0 - X) + 3.0 * w)
        west = np.maximum(west, np.where(Y < 394.0, 4.2 + 1.6 * w - dF, -1.0))
        west = np.minimum(west, -(t4_trampled(X, Y) + 0.6))
        west = np.minimum(west, np.hypot(X - KILN[0], Y - KILN[1]) - KILN[2])
        g = np.maximum(g, np.where(X < T4_WEST_X, west, -1.0))
        return np.minimum(g, -sdf_line(X, Y, [(-104.0, 452.0), (-60.0, 446.0), (-20.0, 450.0)], 3.0))
    if nm == "ExitLand":
        return _tracks(nm, X, Y, 2.0 + 2.0 * w)
    return np.full(X.shape, -1.0)


def _tracks(nm, X, Y, g):
    for pts, hw in FIELD_TRACKS.get(nm, ()):
        g = np.minimum(g, -sdf_line(X, Y, pts, hw + 0.4 * waves(X, Y, 12.1, 2.0)))
    return g


def slab_regions(X, Y):
    """onde ha LAJES (a grama nao cobre)"""
    return np.maximum(sdf_poly(X, Y, ccw(L.ENTRY_COURT)), sdf_line(X, Y, TRAIL_PATH, TRAIL_HW + 0.6))


def ground(mb_skin, mb_grass, mb_clr):
    rim = L.ISLAND_RIM
    G = Grid(min(p[0] for p in rim), min(p[1] for p in rim), max(p[0] for p in rim), max(p[1] for p in rim), 2.0)
    X, Y = G.X, G.Y
    eff = floor_fields(G)
    bed = bed_regions(X, Y)
    slabs_f = slab_regions(X, Y)
    clr = sdf_poly(X, Y, ccw(L.CLEARING))
    dark = clr_dark(X, Y)
    # vies do tom: beira das falesias (ate 14 do contorno) puxa para o verde fundo
    rim_b = 0.55 * np.clip(1.0 - sdf_poly(X, Y, ccw(rim)) / 14.0, 0.0, 1.0)
    clr_b = np.clip(0.7 - 0.075 * clr, -0.95, 0.7)          # clareira: funda na borda, seca/rala para dentro
    eb = exit_band(X, Y)
    stats = {}
    for nm, poly, z, pr in FLOORS:
        zf = (lambda x, y, z=z: L._zval(z, x, y))
        f = np.minimum(eff[nm], -bed)
        if nm == "T1":
            # a clareira tem pele propria (DS_Clr_): aqui so o resto do T1
            fo = np.minimum(f, -clr)
            fi = np.minimum(f, clr)
            tr = sdf_line(X, Y, TRAIL_PATH, TRAIL_HW + 0.5)       # junta das lajes da trilha: terra ESCURA
            field_mesh(mb_skin, G, np.minimum(fo, -tr), zf, SKIN[nm], skirt=BEDD)
            field_mesh(mb_skin, G, np.minimum(fo, tr), zf, DIRTD, skirt=BEDD)
            # ONDA 4b: pele da clareira em manchas terra / terra escura (calcada, trilhas): MATERIAL por regiao na
            # mesma cota (bordas coincidentes, sem saia entre elas)
            dk = np.maximum(tr, dark)
            field_mesh(mb_clr, G, np.minimum(fi, -dk), zf, DIRT, skirt=BEDD, inner=fi)
            field_mesh(mb_clr, G, np.minimum(fi, dk), zf, DIRTD, skirt=BEDD, inner=fi)
        elif nm in ("Forge", "ExitLand"):
            # 6b (item 04): T4 oeste em terra escura de trabalho + terra batida CLARA (trilhas e pisoteio), mesma cota;
            # (item 15) o caminho de saida tambem e terra batida clara da pele
            tp = np.maximum(t4_trampled(X, Y), eb) if nm == "Forge" else eb
            mbase = SKIN[nm] if nm == "Forge" else DIRTD
            field_mesh(mb_skin, G, np.minimum(f, -tp), zf, mbase, skirt=BEDD, inner=f)
            field_mesh(mb_skin, G, np.minimum(f, tp), zf, DIRT, skirt=BEDD, inner=f)
        else:
            field_mesh(mb_skin, G, f, zf, SKIN[nm], skirt=BEDD)
        g = np.minimum(np.minimum(f - 0.9, grass_cover(nm, X, Y)), -(slabs_f + 0.4))
        g = np.minimum(g, -(eb + 0.5))                      # 6b: grama nunca no caminho de saida
        tgt = mb_clr if nm == "T1" else mb_grass
        # ONDA 4b: cada camada de grama em pedacos de TOM (funda / B / base / seca), bordas internas sem saia
        bias = rim_b + (np.where(clr > 0, clr_b, 0.0) if nm == "T1" else 0.0)
        if nm == "Forge":                                   # 6b (item 04): o T4 oeste puxa para a grama SECA
            bias = bias + np.where(X < T4_WEST_X, -0.55, 0.0)
        for mask, mat in tone_parts(nm, X, Y, bias):
            gp = np.minimum(g, mask)
            if nm == "T1":
                field_mesh(mb_grass, G, np.minimum(gp, -clr), zf, mat, top_off=GRASS_H, skirt=0.3, flare=0.35,
                           m_skirt=GRASSB, inner=g)
                field_mesh(mb_clr, G, np.minimum(gp, clr), zf, mat, top_off=GRASS_H, skirt=0.3, flare=0.35,
                           m_skirt=GRASSB, inner=g)
            else:
                field_mesh(tgt, G, gp, zf, mat, top_off=GRASS_H, skirt=0.3, flare=0.35, m_skirt=GRASSB, inner=g)
        stats[nm] = True
    return G


def clearing_relief(mb):
    """ondulacao SUAVE do chao da clareira, sem colisao: lombas largas do mesmo material (terra), <= 0,26 de altura,
    so fora do miolo (o miolo fica plano e legivel). Mesmo material da pele -> sem z-fight."""
    G = Grid(-50.0, 120.0, 134.0, 410.0, 3.0)
    X, Y = G.X, G.Y
    clr = sdf_poly(X, Y, ccw(L.CLEARING))
    w = waves(X, Y, 7.7, 1.3)
    f = np.minimum(clr - 3.0, 0.55 * w - 0.18)
    f = np.minimum(f, -sdf_poly(X, Y, L.POND) - 3.0)
    f = np.minimum(f, -sdf_line(X, Y, L.CHANNEL, 4.0))
    f = np.minimum(f, -(grass_cover("T1", X, Y) + 2.5))     # nunca sob/sobre a grama (0,08 de folga = z-fight)
    # ONDA 4b: relevo so FORA da MiningZone (+2) e nunca sobre a terra escura (a lomba e de terra clara)
    f = np.minimum(f, -sdf_rect(X, Y, L.MINE_RECT) - 2.0)
    f = np.minimum(f, -(clr_dark(X, Y) + 1.5))
    # 6b (item 07): a borda das lombas (chanfro de 1,6) lia triangulo escuro/buraco na sombra: chanfro de 3,0 (~5 graus)
    field_mesh(mb, G, f, lambda x, y: T1, DIRT, top_off=0.26, skirt=0.4, flare=3.0, m_skirt=DIRT)


def lay_slabs_rows(mb, origin, u, v, length, width, zf, key, depth_cyc, width_cyc, keep, gap=0.26, m=LAJE, ch=0.09):
    """lajes em fiadas: fiadas de profundidade DIRIGIDA ao longo de u, cada uma partida em pecas ao longo de v
    (larguras DIRIGIDAS, juntas desencontradas); keep(quad) decide se a peca entra"""
    s, r = 0.0, 0
    n = 0
    while s < length - 0.4:
        d = min(cyc(depth_cyc, r), length - s)
        t = -width / 2 - (cyc(width_cyc, r * 3) * 0.5 if r % 2 else 0.0)
        c = 0
        while t < width / 2 - 0.3:
            wdt = cyc(width_cyc, r * 5 + c + int(hh(key, "w") * 6))
            t0, t1 = max(t, -width / 2), min(t + wdt, width / 2)
            if t1 - t0 > 0.6:
                jit = [(hh(key, r, c, k) - 0.5) * 0.3 for k in range(8)]
                pts = []
                for k, (ss, tt) in enumerate(((s + gap / 2, t0 + gap / 2), (s + d - gap / 2, t0 + gap / 2),
                                              (s + d - gap / 2, t1 - gap / 2), (s + gap / 2, t1 - gap / 2))):
                    ss += jit[2 * k] * (0.0 if (k in (0, 3) and r == 0) else 1.0)
                    tt += jit[2 * k + 1]
                    pts.append((origin[0] + u[0] * ss + v[0] * tt, origin[1] + u[1] * ss + v[1] * tt))
                quad = ccw(pts)
                if keep(quad):
                    slab(mb, quad, zf, SLAB_H, m=m, ch=ch)
                    n += 1
            t += wdt
            c += 1
        s += d
        r += 1
    return n


def paving(mb):
    n = 0
    court = ccw(DL.offset_poly(L.ENTRY_COURT, -0.4))
    inside = lambda q: all(L.point_in_poly(x, y, court) and not opening_any(x, y) for x, y in q)
    zc = lambda x, y: T0
    # SANDO no eixo (lajes grandes retangulares, 3 por fiada): do torii ao pe da escada Trilha
    n += lay_slabs_rows(mb, (-0.0, -0.2), (0.0, 1.0), (1.0, 0.0), 44.0, 13.4, zc, "sando",
                        (3.4, 3.0, 3.6, 3.2), (4.5, 4.4, 4.5), inside)
    # lados do patio: pecas menores e irregulares, fiadas no outro rumo. 6b (item 10): na borda oeste as pecas
    # passavam da pele do patio (vao de 0,28 sob a laje, sobre a saia) e se cruzavam junto da guarda: agora ficam 0,9
    # para dentro da borda e nenhuma laje cruza outra (SAT)
    court2 = ccw(DL.offset_poly(L.ENTRY_COURT, -0.9))
    placed = []

    def side_ok(q):
        if not (all(L.point_in_poly(x, y, court2) and not opening_any(x, y) for x, y in q)
                and all(abs(x) > 7.25 for x, y in q)):
            return False
        r = list(q) + [(sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4)]
        if _sat_hit(r, placed):
            return False
        placed.append(r)
        return True
    for sx in (-1, 1):
        n += lay_slabs_rows(mb, (sx * 7.3, -1.0), (0.0, 1.0), (sx * 1.0, 0.0), 46.0, 44.0, zc, ("pt", sx),
                            (2.6, 2.2, 3.0, 2.4, 2.8), (3.2, 2.6, 3.8, 2.9, 3.4), side_ok, ch=0.0)
    # trilha: lajes irregulares que se desfazem na chegada a clareira
    pts = TRAIL_PATH
    acc = 0.0
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        ln = math.dist(a, b)
        u = ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)
        v = (-u[1], u[0])
        fade = (i >= len(pts) - 3)

        def keep(q, i=i, fade=fade):
            if not all(L.floor_name(x, y) == "T1" for x, y in q):
                return False
            if any(L.point_in_poly(x, y, L.ribbon(L.VILLAGE_STREET, 3.8)) for x, y in q):
                return False
            if fade:
                c = (sum(p[0] for p in q) / 4, sum(p[1] for p in q) / 4)
                return hh(round(c[0], 1), round(c[1], 1), "fd") > (0.25 if i == len(pts) - 3 else 0.6)
            return True
        n += lay_slabs_rows(mb, (a[0] - u[0] * 0.3, a[1] - u[1] * 0.3), u, v, ln + 0.3, TRAIL_HW * 2, lambda x, y: T1,
                            ("tr", i), (1.9, 2.3, 1.7, 2.1, 2.5), (2.4, 1.8, 2.8, 2.1, 2.6), keep, ch=0.0)
        acc += ln
    # bambuzal: PISANTES de pedra no caminho de terra (sobem com o chao inclinado)
    bz = L.bamboo_z
    for i, (x, y, ang, st) in enumerate(tangent_frames(L.BAMBOO_RAMP, (2.7, 2.4, 2.9, 2.5), closed=False)):
        u = (math.cos(ang), math.sin(ang))
        v = (-u[1], u[0])
        off = (0.9 if i % 2 else -0.9) + (hh(i, "bo") - 0.5) * 0.6
        w_, d_ = 2.0 + 0.6 * hh(i, "bw"), 1.4 + 0.4 * hh(i, "bd")
        cx, cy = x + v[0] * off, y + v[1] * off
        q = [(cx + u[0] * sx * d_ / 2 + v[0] * sy * w_ / 2, cy + u[1] * sx * d_ / 2 + v[1] * sy * w_ / 2)
             for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        if L.floor_name(cx, cy) != "Bamboo":
            continue
        slab(mb, ccw(q), bz, SLAB_H, th=0.4, m=LAJE)
        n += 1
    return n


def _frames(pts, step=0.25):
    """amostra a polilinha: (s, x, y, dx, dy)"""
    out, s = [], 0.0
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        k = max(1, int(ln / step))
        for i in range(k):
            out.append((s + ln * i / k, a[0] + dx * i / k, a[1] + dy * i / k, dx / ln, dy / ln))
        s += ln
    out.append((s, pts[-1][0], pts[-1][1], out[-1][3], out[-1][4]))
    return out


def _at(fr, s):
    lo, hi = 0, len(fr) - 1
    while lo < hi:
        m = (lo + hi + 1) // 2
        if fr[m][0] <= s:
            lo = m
        else:
            hi = m - 1
    return fr[lo]


def _sat_hit(q, placed):
    for p in placed:
        if abs(p[4][0] - q[4][0]) > 5 or abs(p[4][1] - q[4][1]) > 5:
            continue
        sep = False
        for poly in (q[:4], p[:4]):
            for i in range(4):
                a, b = poly[i], poly[(i + 1) % 4]
                nx, ny = b[1] - a[1], a[0] - b[0]
                pa = [nx * c[0] + ny * c[1] for c in q[:4]]
                pb = [nx * c[0] + ny * c[1] for c in p[:4]]
                if max(pa) <= min(pb) + 0.02 or max(pb) <= min(pa) + 0.02:
                    sep = True
                    break
            if sep:
                break
        if not sep:
            return True
    return False


def t4_ok(q):
    """a peca cabe no T4 oeste: piso 'Forge', fora do patio da forja (+0,5), da faixa do caminho de saida e das escadas"""
    x0, y0, x1, y1 = L.FORGE_YARD
    for x, y in q:
        if L.floor_name(x, y) != "Forge" or opening_any(x, y):
            return False
        if x0 - 0.5 < x < x1 + 0.5 and y0 - 0.5 < y < y1 + 0.5:
            return False
        if L.point_in_poly(x, y, T4_EXIT_POLY):
            return False
    return True


T4_EXIT_POLY = []


def t4_paving(mb):
    """6b (item 04): trilha do PATIO em lajes irregulares (2 por fiada, juntas desencontradas) e as trilhas da carvoeira
    e da OesteForja em PISANTES (pedras de passo alternadas sobre a terra batida clara)"""
    T4_EXIT_POLY[:] = DL.offset_poly(exit_bed_poly(), 0.3)
    n = 0
    placed = []
    zf = lambda x, y: T4
    for nm, (pts, hw, kind) in T4_TRAILS.items():
        fr = _frames(pts)
        total = fr[-1][0]
        s, r = 0.4, 0
        while s < total - 0.5:
            _, x, y, dx, dy = _at(fr, s)
            if kind == "lajes":
                d = cyc((1.3, 1.1, 1.5, 1.2, 1.4), r + int(hh(nm, "d") * 5))
                cut = -hw + 2 * hw * (0.36 + 0.28 * hh(nm, r, "c"))
                for va, vb in ((-hw, cut), (cut, hw)):
                    pts4 = []
                    for k, (a, b) in enumerate(((0.0, va), (d, va), (d, vb), (0.0, vb))):
                        a += (0.08 if k in (0, 3) else -0.08) + (hh(nm, r, va, k, "a") - 0.5) * 0.16
                        b += (0.08 if b == va else -0.08) + (hh(nm, r, va, k, "b") - 0.5) * 0.14
                        pts4.append((x + dx * a - dy * b, y + dy * a + dx * b))
                    q = pts4 + [(x + dx * d / 2 - dy * (va + vb) / 2, y + dy * d / 2 + dx * (va + vb) / 2)]
                    if t4_ok(pts4) and not _sat_hit(q, placed):
                        placed.append(q)
                        slab(mb, ccw(pts4), zf, SLAB_H, th=0.4, ch=0.0, m=LAJE)
                        n += 1
                s += d
            else:
                # pisante: pedra de passo de 1,7..2,1 x 1,2..1,5, alternando +-0,45 do eixo, giro proprio
                off = (0.45 if r % 2 else -0.45) + (hh(nm, r, "o") - 0.5) * 0.4
                w_, d_ = 1.7 + 0.4 * hh(nm, r, "w"), 1.2 + 0.3 * hh(nm, r, "dd")
                a0 = math.atan2(dy, dx) + (hh(nm, r, "rt") - 0.5) * 0.5
                cx, cy = x - dy * off, y + dx * off
                ca, sa = math.cos(a0), math.sin(a0)
                pts4 = [(cx + ca * su * d_ / 2 - sa * sv * w_ / 2, cy + sa * su * d_ / 2 + ca * sv * w_ / 2)
                        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                q = pts4 + [(cx, cy)]
                if t4_ok(pts4) and not _sat_hit(q, placed):
                    placed.append(q)
                    slab(mb, ccw(pts4), zf, SLAB_H + 0.04, th=0.45, ch=0.09, m=LAJE)
                    n += 1
                s += 2.0 + 0.4 * hh(nm, r, "st")
            r += 1
    return n


def t4_stones(mb):
    """6b (item 04): meio-fio de pedra (Stone_DS_B) nos 2 lados da trilha do patio e nas pontas das trilhas de pisantes;
    pedras de borda no labio oeste do T4 e no pe do muro norte da OesteForja (transicao ao muro/falesia)"""
    n = 0
    zf = lambda x, y: T4
    for nm, (pts, hw, kind) in T4_TRAILS.items():
        fr = _frames(pts)
        total = fr[-1][0]
        spans = [(0.0, total)] if kind == "lajes" else [(0.0, 5.0), (total - 5.0, total)]
        for s0, s1 in spans:
            for side in (-1, 1):
                s, k = s0 + 0.2, 0
                while s < s1 - 0.6:
                    ln = min(cyc((1.7, 1.4, 1.9, 1.5), k + (side > 0)), s1 - s)
                    if ln < 0.7:
                        break
                    _, x, y, dx, dy = _at(fr, s + ln / 2)
                    o = side * (hw + 0.42 + (hh(nm, s0, side, k, "co") - 0.5) * 0.12)
                    cx, cy = x - dy * o, y + dx * o
                    a0 = math.atan2(dy, dx) + (hh(nm, side, k, "cr") - 0.5) * 0.06
                    ca, sa = math.cos(a0), math.sin(a0)
                    hl, hwid = ln / 2 - 0.08, 0.2 + 0.04 * hh(nm, side, k, "cw")
                    pts4 = [(cx + ca * su * hl - sa * sv * hwid, cy + sa * su * hl + ca * sv * hwid)
                            for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
                    if t4_ok(pts4):
                        slab(mb, ccw(pts4), zf, 0.28 + 0.06 * hh(nm, side, k, "ch"), th=0.7, ch=0.06, m=STONEB)
                        n += 1
                    s += ln
                    k += 1
    # pedras de borda: labio oeste do T4 (sobre a grama da faixa) e quinas do pe do muro sul
    for i, (x, y, r, hgt) in enumerate(((-139.0, 452.0, 1.3, 0.9), (-141.5, 432.0, 1.0, 0.7), (-140.0, 410.0, 1.5, 1.1),
                                        (-138.5, 396.0, 1.1, 0.8), (-133.0, 470.0, 1.2, 0.8), (-120.0, 384.0, 1.2, 0.9),
                                        (-84.0, 378.6, 1.0, 0.7), (-74.5, 377.6, 0.8, 0.6), (-57.0, 377.6, 0.9, 0.6),
                                        (-44.0, 398.0, 1.2, 0.8))):
        if L.floor_name(x, y) != "Forge":
            continue
        boulder(mb, x, y, T4, r, hgt, ("t4b", i), m=cyc((ISHI, STONEB, ISHID), i), ang=hh(i, "t4a") * 3.0)
        a = hh(i, "t4s") * 6.28
        boulder(mb, x + math.cos(a) * r * 1.4, y + math.sin(a) * r * 1.4, T4, r * 0.5, hgt * 0.55, ("t4s", i),
                m=cyc((STONEB, ISHI), i), ang=a)
        n += 2
    return n


def clearing_edges(mb):
    """borda da clareira: poucas pedras (com colisao, fora da zona + 8) e fragmentos de pedra rentes ao chao.
    (ONDA 4: as raizes retas das 3 arvores largas - DS_Clr_Roots - sairam daqui; cada arvore do ds_veg tem as suas)"""
    x0, y0, x1, y1 = L.MINE_RECT
    rocks = [(-38.0, 168.0, 2.4, 1.6), (-41.0, 262.0, 1.8, 1.2), (-42.0, 308.0, 2.8, 1.9), (113.0, 192.0, 2.2, 1.5),
             (114.0, 258.0, 1.7, 1.1), (-18.0, 364.0, 2.0, 1.3), (74.0, 374.0, 2.3, 1.4)]
    for i, (x, y, r, hgt) in enumerate(rocks):
        assert not (x0 - 8 < x < x1 + 8 and y0 - 8 < y < y1 + 8), (x, y)
        boulder(mb, x, y, T1, r, hgt, ("cb", i), ang=hh(i, "ang") * 3.0)
        # pedra-satelite menor ao lado (as pedras se agrupam, nao ficam soltas)
        a = hh(i, "sat") * 6.28
        boulder(mb, x + math.cos(a) * r * 1.5, y + math.sin(a) * r * 1.5, T1, r * 0.45, hgt * 0.5, ("cbs", i),
                ang=a)
        col_box("DS_ClrRock", (r * 1.7, r * 1.4, hgt + 0.6), (x, y, T1 + (hgt + 0.6) / 2 - 0.3), (0, 0, 0))
    # fragmentos de pedra rentes ao chao (0,16 acima), so na faixa da borda
    frags = 0
    for i in range(60):
        t = hh(i, "ft") * 2 * math.pi
        k = i % 4
        cx, cy = 42.0 + math.cos(t) * (96.0 + 10.0 * hh(i, "fr")), 262.0 + math.sin(t) * (150.0 + 12.0 * hh(i, "fr"))
        if L.floor_name(cx, cy) != "T1" or not L.point_in_poly(cx, cy, L.CLEARING):
            continue
        if x0 - 3 < cx < x1 + 3 and y0 - 3 < cy < y1 + 3:
            continue
        if L.polyline_dist(cx, cy, L.CHANNEL) < 4.0 or L.point_in_poly(cx, cy, DL.offset_poly(L.POND, 3.0)):
            continue
        r = 0.6 + 0.6 * hh(i, "fs")
        boulder(mb, cx, cy, T1 - 0.3, r, 0.46, ("fg", i), ang=t)
        frags += 1
    return frags


# ------------------------------------------------------------------ limpeza do blockout da clareira
def drop_blockout_clearing():
    """o chao da clareira passa a ser do terreno: some o DS_Clr_Ground do blockout, as pedras do DS_Clr_Edges
    (fica a cerca em setores, que e do ds_props na onda 3) e as colisoes dessas pedras"""
    ob = bpy.data.objects.get("DS_Clr_Ground")
    if ob:
        bpy.data.objects.remove(ob, do_unlink=True)
    ob = bpy.data.objects.get("DS_Clr_Edges")
    if ob:
        me = ob.data
        idx = [i for i, m in enumerate(me.materials) if m and m.name.startswith("Stone_DS")]
        if idx:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.material_index in idx], context="FACES")
            bm.to_mesh(me)
            bm.free()
    for o in [o for o in bpy.data.objects if o.name.startswith("COL_DS_ClrRock_")]:
        bpy.data.objects.remove(o, do_unlink=True)


# ------------------------------------------------------------------ build
def build():
    drop_blockout_clearing()
    stats = {}
    MOSS_REC.clear()
    # quilha e coroa: Tier C (sem chanfro de bevel; o chanfro de musgo e geometria propria)
    mk = MB("DS_Ter_Cliff", "02_TERRAIN", None, detail="far", floor=-999)
    stats["coroa"] = crown(mk)
    mk.finish(recalc=False)
    mq = MB("DS_Ter_Keel", "02_TERRAIN", None, detail="far", floor=-999)
    stats["quilha"] = keel(mq)
    mq.finish(recalc=False)
    mb = MB("DS_Ter_Bodies", "02_TERRAIN", None, detail="far", floor=-999)
    bodies(mb)
    mb.finish()
    mi = MB("DS_Ter_Ishigaki", "02_TERRAIN", None, detail="far", floor=-999)
    mr = MB("DS_Ter_RockWalls", "02_TERRAIN", None, detail="far", floor=-999)
    stats["arrimos"] = walls(mi, mr)
    stats["bochechas"] = notch_cheeks(mi)
    stats["vala"] = vala_stones(mi)
    stats["t4_pedras"] = t4_stones(mi)
    mi.finish(recalc=False)
    mr.finish(recalc=False)
    mf = MB("DS_Ter_Rocks", "02_TERRAIN", None, detail="far", floor=-999)
    stats["enchimento"] = fill(mf)
    ravine(mf)
    mf.finish(recalc=False)
    # ONDA 4b: musgo e verde escorrendo (1 objeto, 2 materiais) sobre as colunas registradas acima
    mm = MB("DS_Ter_Moss", "02_TERRAIN", None, detail="far", floor=-999)
    stats["musgo"] = streaks(mm, MOSS_REC)
    mm.finish(recalc=False)
    ms = MB("DS_Ter_Ground", "02_TERRAIN", None, detail="far", floor=-999)
    mg = MB("DS_Ter_Grass", "02_TERRAIN", None, detail="far", floor=-999)
    mc = MB("DS_Clr_Floor", "03_CLEARING", None, detail="far", floor=-999)
    ground(ms, mg, mc)
    vala_bed(mg)
    clearing_relief(mc)
    ms.finish(recalc=False)
    mg.finish(recalc=False)
    mc.finish(recalc=False)
    mp = MB("DS_Ter_Paving", "02_TERRAIN", None, detail="far", floor=-999)
    stats["lajes"] = paving(mp)
    stats["t4_lajes"] = t4_paving(mp)
    mp.finish(recalc=False)
    me = MB("DS_Clr_EdgeRocks", "03_CLEARING", None, detail="far", floor=-999)
    stats["fragmentos"] = clearing_edges(me)
    me.finish(recalc=False)
    print("ds_terrain", stats)
