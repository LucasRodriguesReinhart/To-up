# op_terrain - ZONA TERRAIN da Ilha 5 (ONE PIECE / WANO), M4. build() substitui op_blockout.terrain. Prefixo OP_Ter_,
# colecao 02_TERRAIN. Sem luzes. Le a planta TRAVADA (op_layout); nao cria marcador; a colisao andavel e toda do op_col
# (congelado): aqui NADA colide (as faces e muros ficam na linha da borda do piso ou abaixo da cabeca do jogador).
#
# CRITICA DO LEAD (blockout): borda e terracos liam como BOLO DE CAMADAS cinza; faltava o ROCHEDO ALTO do castelo com a
# cachoeira; laterais/traseira lisas. Aqui o terreno e um modelo de PLACAS (pisos da planta, rochas da planta, agua,
# escadas, berma) com 4 geradores:
#   1. FALESIA DO CONTORNO (OP_Ter_Cliff): o contorno inteiro em MASSAS de 22..64 de comprimento (nao colunas iguais):
#      cada massa tem bojo proprio (facetas planas de 5..12), ressalto de ESTRATO em altura/inclinacao/largura proprias
#      (prateleira verde = ancora de vegetacao), capa verde no topo que ESCORRE pela face (linguas de comprimento
#      dirigido), estrato de baixo mais frio em metade das massas, pe molhado escuro na linha do mar e QUILHA em cone
#      facetado ate 0 (ilha flutuante vista da DS). Cais do porto = pedra aparelhada reta (o resto da borda e organico).
#      Gargantas nas 2 quedas da borda (oeste e leste) com o labio na cota do canal.
#   2. FACES INTERNAS: toda borda de placa com desnivel. Pisos com desnivel <= 12 -> ARRIMO Wano (pedra aparelhada
#      kirikomi: fiadas de altura variada, juntas escuras rebaixadas, capa clara, soco escuro no pe); porto (65,2/42,2)
#      -> muralha de cais de blocos grandes; resto -> FACE DE ROCHA facetada (capa verde, relevo <= 0,7 ate a altura da
#      cabeca de quem anda embaixo, mais solta acima).
#   3. PELE DO CHAO (OP_Ter_Ground): campo de distancia + marching squares NA COTA EXATA da colisao: grama em 2 tons,
#      terra no contato com muros/faces/ruas (faixa irregular), lajes claras nos pisos de pedra, cais de pedra, berma
#      verde entre os pisos e a falesia (desce para o piso mais baixo vizinho), topo das rochas em verde fundo/musgo,
#      leito escuro dos canais. Onde OUTRO modulo poe piso rente (+0,12: praca, ruas, caminho da saida) a pele NAO existe:
#      fica o corpo 0,5 abaixo (BED: regra do z-fight).
#   4. ROCHEDO DO CASTELO (OP_Ter_CastleRock): face frontal da proa (98 -> 136,2) em lajes verticais largas, 2 paineis
#      planos para os estandartes (face >= 351,6 atras deles), CANAL CENTRAL da cachoeira (fundo molhado escuro, boca da
#      nascente sob a varanda, labio de pedra em (0, 351, 132,2) = FX_Fall_Castle_Lip), estrato a 117, contrafortes
#      (ButtressL/R) e pes; muralha de pedra do castelo ao longo da subida (escadas CasteloA/B); agulhas de rocha
#      presas a ilha atras do castelo (moldura da concept, abaixo da torre); esporao da espada (crista ate o pinaculo
#      z 100 onde a espada crava) e o assento da caveira no promontorio.
# CONTRATOS:
#   - BED (pele ausente, corpo a piso - 0,5): PLAZA (inset 0,5; a pavimentacao, o emblema rebaixado e a borda da
#     praca sao do dono plaza / op_plaza), L.STREETS, caminho do promontorio, patio do torii (op_entry pavimenta a
#     +0,14). Terraco do summon (op_summon a +0,3), adro e patio do castelo TEM pele (quem assentar em cima: >= +0,3).
#   - Faixa sul da praca (TRECHO, y 109..170, |x| <= 120) e do M2 (op_kit + trecho): aqui sem arrimo nem meio-fio nela.
#   - Arvore (op_tree): ancoras do rochedo em CASTLE_ROCK_ANCHORS / castle_rock_z() (abaixo); a arvore faz raycast no
#     que ja existe, e o terreno roda antes dela.
#   - Remove OP_Cas_Cliff (colunas do blockout do castelo): o rochedo do castelo agora e do terreno.
import math, zlib, os
import numpy as np
import bmesh
import bpy
from mathutils import Vector, noise
import op_lib as DL
from op_lib import MB, ccw, camera
import op_layout as L

C = "02_TERRAIN"
T0, T1, P, CF, CC, W3Z, CL = L.T0, L.T1, L.P, L.CF, L.CC, L.W3, L.CL
SEA, BASE = L.SEA, L.BASE
H = 2.5                         # passo da grade da pele
BBOX = (-255.0, -20.0, 370.0, 520.0)
ROCK, ROCKC, DARK, MOSS, VOID = "Cliff_OP_Warm", "Cliff_OP_Cool", "Cliff_OP_Dark", "Cliff_OP_Moss", "Cliff_OP_Void"
GDEEP, GRASS, GRASSB = "Grass_OP_Deep", "Grass_OP", "Grass_OP_B"
DIRT, DIRTD, PATH, STONE = "Dirt_OP", "Dirt_OP_Dark", "Stone_OP_Path", "Stone_OP"
WALL, JOINT, WOOD, WOODD = "Stone_OP_Wall", "Stone_OP_Dark", "Wood_OP_Mid", "Wood_OP_Dark"
TRECHO = (-120.0, 109.0, 120.0, 170.0)
CASTLE_CUT = (-25.5, 340.0, 25.5, 358.5)       # recorte do corpo do patio atras da face da proa (build_castle_rock)

# ------------------------------------------------------------------ CONTRATO com a arvore (op_tree)
# rochedo do castelo: patio 136,2; degrau leste para a rocha do fundo BackE (120) entre x 66..74 / y 372..468; rocha do
# fundo norte BackN (150) atras do muro. Ancoras (x, y, z, nx, ny): pontos NA superficie da rocha onde raizes agarram.
CASTLE_ROCK_TOP = CC
CASTLE_ROCK_ANCHORS = [(73.5, 432.0, CC - 1.0, 1.0, -0.05), (74.2, 440.0, CC - 6.0, 0.98, 0.15),
                       (70.0, 455.0, CC - 3.0, 0.88, 0.47), (66.0, 463.0, CC - 8.0, 0.8, 0.6),
                       (78.0, 446.0, 120.0, 0.0, 0.0), (84.0, 458.0, 120.0, 0.0, 0.0), (60.0, 470.0, CC + 2.0, 0.2, -1.0)]


def castle_rock_z(x, y):
    """cota do topo da rocha/piso no rochedo do castelo (patio, BackE, BackN) - pura planta, sem bpy"""
    p = plate_at(x, y)
    return p[2](x, y) if p else None


# ------------------------------------------------------------------ variacao DIRIGIDA (hash com finalizador murmur)
def _fmix(h):
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def hh(*a):
    s = "|".join(("%.2f" % v) if isinstance(v, float) else str(v) for v in a)
    return _fmix(zlib.crc32(s.encode("utf-8")) ^ 0x9E3779B9) / 4294967296.0


# ------------------------------------------------------------------ campos de distancia (numpy)
def sdf_poly(X, Y, Pl):
    Pl = np.asarray(Pl, float)
    n = len(Pl)
    inside = np.zeros(X.shape, bool)
    d2 = np.full(X.shape, 1e18)
    for i in range(n):
        ax, ay = Pl[i]
        bx, by = Pl[(i + 1) % n]
        if ay != by:
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
    d2 = np.full(X.shape, 1e18)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0)
        d2 = np.minimum(d2, (X - ax - dx * t) ** 2 + (Y - ay - dy * t) ** 2)
    return hw - np.sqrt(d2)


def waves(X, Y, seed, scale=1.0):
    out = np.zeros(X.shape)
    for k, (fx, fy, ph) in enumerate(((0.031, 0.018, 0.0), (-0.017, 0.043, 1.3), (0.052, -0.029, 2.1),
                                      (0.011, 0.067, 4.0))):
        out += math.cos(k * 0.7 + seed) * 0.42 * np.sin((X * fx + Y * fy) * scale * 6.0 + ph + seed * (k + 1))
    return out


class Grid:
    def __init__(self, x0, y0, x1, y1, h):
        self.h = h
        self.x0, self.y0 = x0, y0
        nx = int(math.ceil((x1 - x0) / h)) + 1
        ny = int(math.ceil((y1 - y0) / h)) + 1
        self.X, self.Y = np.meshgrid(x0 + np.arange(nx) * h, y0 + np.arange(ny) * h)


def sample(G, A, x, y):
    fi, fj = (x - G.x0) / G.h, (y - G.y0) / G.h
    i, j = int(math.floor(fi)), int(math.floor(fj))
    ny, nx = A.shape
    i = min(max(i, 0), nx - 2)
    j = min(max(j, 0), ny - 2)
    tx, ty = min(max(fi - i, 0.0), 1.0), min(max(fj - j, 0.0), 1.0)
    return float((A[j, i] * (1 - tx) + A[j, i + 1] * tx) * (1 - ty) + (A[j + 1, i] * (1 - tx) + A[j + 1, i + 1] * tx) * ty)


def assign(mb, faces, m):
    """material EXPLICITO (sem sorteio de variante: o tom e escolhido aqui, por massa/regiao)"""
    mi = mb._mi(m)
    fl = [f for f in faces if f.is_valid]
    for f in fl:
        f.material_index = mi
        f[mb.tint] = 0.0
        f.smooth = False
    mb._uv(fl, m)
    return fl


def field_mesh(mb, G, F, zfun, m, skirt=0.0, m_skirt=None, inner=None, inner_thr=0.3, flat=True):
    """superficie da regiao F > 0 (marching squares na grade G) em z = zfun(x, y); saia de 'skirt' para baixo SO nas
    bordas de fora (inner = campo da regiao inteira: borda entre pedacos da mesma placa nao ganha saia). Dissolve em
    ORDEM FIXA (determinismo, licao da DS) so com flat=True (pele plana)."""
    F = np.where(np.abs(F) < 1e-3, -1e-3, F)
    pos = F > 0
    if not pos.any():
        return []
    js, is_ = np.nonzero(pos)
    j0, j1 = max(int(js.min()) - 1, 0), min(int(js.max()) + 1, F.shape[0] - 1)
    i0, i1 = max(int(is_.min()) - 1, 0), min(int(is_.max()) + 1, F.shape[1] - 1)
    Fl = F.tolist()
    h, x0, y0 = G.h, G.x0, G.y0
    bm = mb.bm
    cache = {}
    verts = []

    def V(key, x, y):
        v = cache.get(key)
        if v is None:
            v = bm.verts.new((x, y, zfun(x, y)))
            cache[key] = v
            verts.append(v)
        return v

    def node(i, j):
        return V(("n", i, j), x0 + i * h, y0 + j * h)

    def edge(ia, ja, ib, jb):
        if (ib, jb) < (ia, ja):
            ia, ja, ib, jb = ib, jb, ia, ja
        f0, f1 = Fl[ja][ia], Fl[jb][ib]
        t = min(0.97, max(0.03, f0 / (f0 - f1)))
        return V(("e", ia, ja, ib, jb), x0 + (ia + (ib - ia) * t) * h, y0 + (ja + (jb - ja) * t) * h)

    faces = []
    for j in range(j0, j1):
        r0, r1 = Fl[j], Fl[j + 1]
        for i in range(i0, i1):
            c = ((i, j, r0[i]), (i + 1, j, r0[i + 1]), (i + 1, j + 1, r1[i + 1]), (i, j + 1, r1[i]))
            ps = [cc[2] > 0 for cc in c]
            if not any(ps):
                continue
            if ps[0] == ps[2] and ps[1] == ps[3] and ps[0] != ps[1] and sum(cc[2] for cc in c) <= 0.0:
                for k in range(4):
                    if ps[k]:
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
                if ps[k]:
                    vs.append(node(a[0], a[1]))
                if ps[k] != ps[(k + 1) % 4]:
                    vs.append(edge(a[0], a[1], b[0], b[1]))
            if len(vs) >= 3:
                try:
                    faces.append(bm.faces.new(vs))
                except ValueError:
                    pass
    if not faces:
        return []
    if flat:
        for f in faces:
            f.normal_update()
        bm.edges.index_update()
        bm.verts.index_update()
        edges = sorted({e for f in faces for e in f.edges}, key=lambda e: e.index)
        verts.sort(key=lambda v: v.index)
        bmesh.ops.dissolve_limit(bm, angle_limit=0.02, use_dissolve_boundaries=False, verts=verts, edges=edges,
                                 delimit=set())
    verts = [v for v in verts if v.is_valid]
    bm.verts.index_update()
    faces = sorted({f for v in verts for f in v.link_faces}, key=lambda f: min(v.index for v in f.verts))
    out = assign(mb, faces, m)
    if skirt > 0.0:
        bnd = []
        for f in faces:
            for lp in f.loops:
                if len(lp.edge.link_faces) == 1:
                    a_, b_ = lp.vert, lp.link_loop_next.vert
                    if inner is not None and sample(G, inner, (a_.co.x + b_.co.x) / 2, (a_.co.y + b_.co.y) / 2) > inner_thr:
                        continue
                    bnd.append((a_, b_))
        bnd.sort(key=lambda e: (e[0].index, e[1].index))
        low = {}
        sk = []
        for a, b in bnd:
            for v in (a, b):
                if v not in low:
                    low[v] = bm.verts.new((v.co.x, v.co.y, v.co.z - skirt))
            try:
                sk.append(bm.faces.new((a, low[a], low[b], b)))
            except ValueError:
                pass
        assign(mb, sk, m_skirt or m)
    return out


# ------------------------------------------------------------------ PLACAS (planta)
def _stair_z(nm):
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    rise = L.stair_rise(nm)
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)

    def z(x, y):
        t = ((x - foot[0]) * ux + (y - foot[1]) * uy + tread / 2) / tread
        return foot[2] + max(0.0, min(float(n), t)) * rise
    return z


def _const(v):
    return lambda x, y: v


def _canal_segments():
    out = []
    for nm, pts, hw in (("CanalE", L.CANAL_E, 3.0), ("CanalW", L.CANAL_W, 4.0)):
        pts = list(pts)
        if nm == "CanalW":            # garganta da queda oeste: o canal chega ate o labio (y 54 -> 46 no contorno)
            pts = pts + [(pts[-1][0], 47.0, pts[-1][2])]
        if nm == "CanalE":
            pts = pts + [(248.5, 298.0, pts[-1][2])]
        for k, (a, b) in enumerate(zip(pts, pts[1:])):
            z = min(a[2], b[2])
            out.append(("%s_%d" % (nm, k), ccw(L.ribbon([a[:2], b[:2]], hw)), z))
    return out


def plates():
    """(nome, poligono, zfun, tipo, prioridade) em ordem de prioridade (a primeira que contem o ponto manda)"""
    out = []
    for nm, up, rect, zf, zt in L.stair_notches():
        x0, y0, x1, y1 = rect
        out.append(("Stair_" + nm, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], _stair_z(nm), "stair"))
    for nm, poly, z, pr in sorted(L.floors(), key=lambda f: -f[3]):
        if nm == "ShipDeck":
            continue
        pl = ccw(poly)
        if nm == "Harbor":
            pl = ccw(DL.clip_half(pl, -1.0, 0.0, 222.4))
        out.append((nm, pl, _const(L._zval(z, 0, 0)), "floor"))
    out.append(("Basin", ccw(L.BASIN), _const(L.BASIN_Z), "water"))
    for nm, pl, z in _canal_segments():
        out.append((nm, pl, _const(z), "water"))
    # rochas: a mais ALTA manda onde se sobrepoem (contraforte sobre o pe: a face do contraforte desce ate o pe)
    for nm, pts, z in sorted(L.ROCKS, key=lambda r: -r[2]):
        out.append(("Rock_" + nm, ccw(pts), _const(z), "rock"))
    return out


PLATES = plates()
_PL_BB = [(min(p[0] for p in pl), min(p[1] for p in pl), max(p[0] for p in pl), max(p[1] for p in pl))
          for nm, pl, zf, k in PLATES]


def plate_at(x, y):
    for (nm, pl, zf, k), bb in zip(PLATES, _PL_BB):
        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3] and L.point_in_poly(x, y, pl):
            return (nm, k, zf)
    return None


RIM = ccw(L.ISLAND_RIM)
BEDS = []          # (pontos, meia largura) ou ('poly', poligono): pele ausente


# ------------------------------------------------------------------ estado do build (grades)
class S_:
    G = None
    own = {}
    union = None
    rim = None
    bandz = None


def _prepare():
    G = Grid(BBOX[0], BBOX[1], BBOX[2], BBOX[3], H)
    S_.G = G
    X, Y = G.X, G.Y
    cum = np.full(X.shape, -1e9)
    S_.own = {}
    S_.sdf = {}
    for nm, pl, zf, k in PLATES:
        s = sdf_poly(X, Y, pl)
        S_.sdf[nm] = s
        S_.own[nm] = np.minimum(s, -cum)
        cum = np.maximum(cum, s)
    S_.union = cum
    S_.rim = sdf_poly(X, Y, RIM)
    # berma: placa mais BAIXA a ate 6 (ou a mais proxima), - 0,35
    samp = []
    for nm, pl, zf, k in PLATES:
        n = len(pl)
        for i in range(n):
            a, b = pl[i], pl[(i + 1) % n]
            ln = math.dist(a, b)
            m = max(1, int(ln / 2.0))
            for s in range(m):
                t = s / m
                x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                samp.append((x, y, zf(x, y)))
    sa = np.array(samp)
    bz = np.full(X.shape, P - 0.35)
    mask = (S_.union <= 0.0) & (S_.rim > -6.0)
    idx = np.nonzero(mask)
    px, py = X[idx], Y[idx]
    res = np.empty(len(px))
    for c0 in range(0, len(px), 1500):
        dx = px[c0:c0 + 1500, None] - sa[None, :, 0]
        dy = py[c0:c0 + 1500, None] - sa[None, :, 1]
        d = np.sqrt(dx * dx + dy * dy)
        zz = np.where(d < 6.0, sa[None, :, 2], 1e9)
        mn = zz.min(1)
        near = sa[d.argmin(1), 2]
        res[c0:c0 + 1500] = np.where(mn < 1e8, mn, near)
    bz[idx] = res - 0.35
    S_.bandz = bz


def ground(x, y):
    p = plate_at(x, y)
    if p:
        if p[1] == "water":
            return p[2](x, y) - 2.2
        return p[2](x, y)
    return sample(S_.G, S_.bandz, x, y)


def bed_field():
    X, Y = S_.G.X, S_.G.Y
    f = sdf_poly(X, Y, ccw(L.PLAZA)) - 0.5
    for pts, w, z in L.STREETS:
        f = np.maximum(f, sdf_line(X, Y, pts, w / 2 - 0.4))
    Ln = L.EXIT_BRIDGE_LEN
    f = np.maximum(f, sdf_line(X, Y, [L.exit_point(Ln), L.exit_point(Ln + L.ANCHOR_OPM_OFF)], 6.0 - 0.4))
    # patio do torii: o op_entry pavimenta o patio inteiro a +0,14 (piso sobre piso < 0,3: aqui fica so o leito)
    f = np.maximum(f, sdf_poly(X, Y, ccw(L.ENTRY_COURT)) - 0.4)
    return f


# ------------------------------------------------------------------ 3. PELE DO CHAO + corpos
FLOOR_TOP = {"Court": "path", "CastleLanding": "path", "Forecourt": "path", "Entry": "path", "HarborMid": "path",
             "Harbor": "quay", "W3": "grass", "Plaza": "grass", "W2b": "grass", "ExitLand": "grass", "T1": "grass"}


def build_ground():
    G = S_.G
    X, Y = G.X, G.Y
    mg = MB("OP_Ter_Ground", C, None, detail="far", floor=BASE)
    bed = bed_field()
    wv1, wv2, wv3 = waves(X, Y, 1.7), waves(X, Y, 3.1, 1.6), waves(X, Y, 5.3, 0.7)
    for nm, pl, zf, k in PLATES:
        if k == "stair":
            continue
        own = S_.own[nm]
        z0 = zf(0.0, 0.0)
        if k == "water":
            field_mesh(mg, G, own, _const(z0 - 2.2), DIRTD)
            continue
        if k == "rock":
            # topo das rochas: verde fundo no meio, musgo na borda (faixa 1..3)
            band = 1.4 + 1.2 * (0.5 + 0.5 * wv2)
            field_mesh(mg, G, np.minimum(own, band - own), _const(z0), MOSS, skirt=0.6, inner=own)
            field_mesh(mg, G, own - band, _const(z0), GDEEP, skirt=0.6, inner=own)
            continue
        kind = FLOOR_TOP[nm]
        skin = np.minimum(own, -bed)
        if kind == "path":
            field_mesh(mg, G, skin, _const(z0), PATH, skirt=0.6, inner=own)
        elif kind == "quay":
            field_mesh(mg, G, skin, _const(z0), STONE, skirt=0.6, inner=own)
        else:
            # terra no CONTATO (borda da placa e das ruas), faixa irregular 0,3..2,4; grama em 2 tons
            band = np.maximum(0.3, 0.9 + 1.5 * wv1)
            dirt = np.minimum(skin, band - skin)
            grass = skin - band
            gb = np.minimum(grass, wv3 - 0.25)
            ga = np.minimum(grass, 0.25 - wv3)
            field_mesh(mg, G, dirt, _const(z0), DIRT, skirt=0.6, inner=own)
            field_mesh(mg, G, ga, _const(z0), GRASS, skirt=0.6, inner=own)
            field_mesh(mg, G, gb, _const(z0), GRASSB, skirt=0.6, inner=own)
    # berma (entre pisos e a falesia, frestas entre pisos): verde fundo, superficie que desce para o piso mais baixo
    band = np.minimum(S_.rim - 0.9, -S_.union)
    zb = lambda x, y: sample(G, S_.bandz, x, y)
    field_mesh(mg, G, np.minimum(band, wv2 + 0.35), zb, GDEEP, flat=False)
    field_mesh(mg, G, np.minimum(band, -wv2 - 0.35), zb, MOSS, flat=False)
    # corpos: prisma de cada placa ate piso - 0,5 (leito escuro; nas faixas BED aparece so pela fresta da peca de cima)
    # (no MESMO objeto da pele: menos MeshParts estimadas, nada muda no visual)
    mbd = mg
    for nm, pl, zf, k in PLATES:
        if k == "stair":
            continue
        z0 = zf(0.0, 0.0)
        top = z0 - 2.2 - 0.3 if k == "water" else z0 - 0.5
        if nm in ("Plaza",):
            pass
        pieces = L.floor_pieces(nm) if k == "floor" and nm != "Harbor" else [pl]
        if nm == "Court":
            # proa do castelo: o corpo recua para y >= 358,5 em |x| <= 25,5 (a face da proa e as lajes ficam na frente)
            pieces = [q for pc in pieces for q in L.subtract_rect(ccw(pc), CASTLE_CUT)]
        for pc in pieces:
            pc = ccw(pc)
            if len(pc) < 3:
                continue
            vb = [mbd.bm.verts.new((x, y, BASE)) for x, y in pc]
            vt = [mbd.bm.verts.new((x, y, top)) for x, y in pc]
            n = len(pc)
            fs = [mbd.bm.faces.new(vt)]
            for i in range(n):
                j = (i + 1) % n
                fs.append(mbd.bm.faces.new((vb[i], vb[j], vt[j], vt[i])))
            assign(mbd, fs[:1], DIRTD)
            assign(mbd, fs[1:], ROCKC)
    mg.finish()


# ------------------------------------------------------------------ geometria de faixa (loft de linhas)
def loft_rows(mb, rows, mats, closed, flip=False):
    """rows[r][i] = ponto 3D (linha r de cima para baixo, no i ao longo da borda anti-horaria); mats[r][i] = material
    do quad entre a linha r e r+1 no trecho i..i+1. Normal para FORA (direita do sentido de percurso)."""
    bm = mb.bm
    V = [[bm.verts.new(p) for p in row] for row in rows]
    n = len(rows[0])
    by = {}
    for r in range(len(rows) - 1):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            q = (V[r][i], V[r + 1][i], V[r + 1][j], V[r][j])
            if flip:
                q = q[::-1]
            pts = [v.co for v in q]
            if (pts[0] - pts[1]).length < 1e-4 and (pts[3] - pts[2]).length < 1e-4:
                continue
            try:
                f = bm.faces.new(q)
            except ValueError:
                continue
            by.setdefault(mats[r][i], []).append(f)
    for m in sorted(by):
        assign(mb, by[m], m)
    return V


def resample_closed(pts, step):
    P_ = list(pts) + [pts[0]]
    tot = sum(math.dist(a, b) for a, b in zip(P_, P_[1:]))
    n = max(8, int(round(tot / step)))
    st = tot / n
    out = []
    acc = 0.0
    k = 0
    a, b = P_[0], P_[1]
    seg = math.dist(a, b)
    for i in range(n):
        d = i * st
        while acc + seg < d and k < len(P_) - 2:
            acc += seg
            k += 1
            a, b = P_[k], P_[k + 1]
            seg = math.dist(a, b)
        t = (d - acc) / seg if seg else 0.0
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, d))
    return out, tot


def normals(pts, closed=True, smooth=2):
    n = len(pts)
    out = []
    for i in range(n):
        if closed:
            a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        else:
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        out.append((dy / ln, -dx / ln))
    for _ in range(smooth):
        nn = []
        for i in range(n):
            if closed:
                a, b = out[(i - 1) % n], out[(i + 1) % n]
            else:
                a, b = out[max(i - 1, 0)], out[min(i + 1, n - 1)]
            x, y = out[i][0] * 2 + a[0] + b[0], out[i][1] * 2 + a[1] + b[1]
            ln = math.hypot(x, y) or 1.0
            nn.append((x / ln, y / ln))
        out = nn
    return out


# ------------------------------------------------------------------ 1. FALESIA DO CONTORNO + quilha
FALL_NOTCH = [((-174.0, 46.0), 5.5, 7.5, T1 - 0.6), ((248.5, 297.5), 4.5, 3.8, P - 0.6)]  # (centro na borda, meia larg., fundo, labio)


def _kind(x, y):
    if 118.0 <= x and y <= 268.0 and x >= 120.0 and (y < 34.0 or x > 214.0) and ground(x - 3.0, y) < 50.0:
        return "quay"
    p = plate_at(x, y)
    return "cliff"


def massas(tot, key, lo=22.0, hi=64.0):
    """quebra o comprimento em massas de tamanho DIRIGIDO (sem repeticao de periodo)"""
    out = []
    t, k = 0.0, 0
    while t < tot - lo * 0.6:
        ln = lo + (hi - lo) * hh(key, k, "len") ** 1.3
        out.append((t, min(t + ln, tot)))
        t += ln
        k += 1
    if out:
        out[-1] = (out[-1][0], tot)
    return out


def ring_nodes(poly, key, step=2.0, kind_fn=None, lo=22.0, hi=64.0, amp=(1.0, 7.0)):
    """nos da falesia: facetas planas por massa (no a cada 5..12 dentro da massa) + bojo dirigido"""
    dense, tot = resample_closed(poly, step)
    # comeca a contar as massas no ponto mais ao sul (o nariz da entrada)
    i0 = min(range(len(dense)), key=lambda i: dense[i][1] + abs(dense[i][0]) * 0.2)
    dense = dense[i0:] + dense[:i0]
    d0 = dense[0][2]
    dense = [(x, y, (d - d0) % tot) for x, y, d in dense]
    nrm = normals([(x, y) for x, y, d in dense], True, 3)
    ms = massas(tot, key, lo, hi)
    nodes = []
    for k, (a, b) in enumerate(ms):
        ln = b - a
        A = amp[0] + (amp[1] - amp[0]) * hh(key, k, "A")
        if hh(key, k, "buttress") > 0.82:
            A *= 1.6
        sharp = 0.45 + 0.6 * hh(key, k, "sh")
        u = 0.0
        q = 0
        while u < ln - 0.5:
            dd = a + u
            i = int(round(dd / tot * len(dense))) % len(dense)
            x, y, _ = dense[i]
            uu = u / ln
            bump = math.sin(math.pi * uu) ** sharp
            off = 0.4 + A * bump + (hh(key, k, q, "j") - 0.5) * 2.8 * bump
            if q == 0:
                off = -0.4 - 1.2 * hh(key, k, "cr")      # vinco entre massas: recua (sombra vertical funda)
            nodes.append(dict(x=x, y=y, nx=nrm[i][0], ny=nrm[i][1], o=off, m=k, u=uu, d=dd, crease=(q == 0)))
            u += 5.0 + 7.0 * hh(key, k, q, "fs")
            q += 1
    return nodes, ms


def build_ring():
    mb = MB("OP_Ter_Cliff", C, None, detail="far", floor=-999)
    key = "rim"
    nodes, ms = ring_nodes(RIM, key)
    cx, cy = DL.centroid(RIM)
    rows = [[] for _ in range(13)]
    mats = [[] for _ in range(12)]
    for nd in nodes:
        x, y, nx, ny, o, k, u = nd["x"], nd["y"], nd["nx"], nd["ny"], nd["o"], nd["m"], nd["u"]
        kind = _kind(x, y)
        # garganta das quedas da borda
        notch = None
        for (fx, fy), hw, dep, lip in FALL_NOTCH:
            dd = math.hypot(x - fx, y - fy)
            if dd < hw + 3.0:
                notch = (max(0.0, min(1.0, (hw + 3.0 - dd) / 3.0)), dep, lip)
        zt = ground(x - nx * 1.6, y - ny * 1.6) - 0.3
        zin = ground(x - nx * 2.6, y - ny * 2.6) - 0.3
        if notch:
            f_, dep, lip = notch
            o = o * (1 - f_) - dep * f_
            zt = zt * (1 - f_) + (lip - 0.25) * f_
            zin = zin * (1 - f_) + (lip - 0.25) * f_
        P_ = lambda off, z: (x + nx * off, y + ny * off, z)
        bump = math.sin(math.pi * u)
        if kind == "quay":
            o = 0.5
            r = [P_(-2.6, zin), P_(0.0, zt + 0.3), P_(0.55, zt + 0.55), P_(0.55, zt - 0.05), P_(0.5, zt - 0.6),
                 P_(0.5, zt - 1.6), P_(0.45, zt - 2.6), P_(0.45, SEA - 0.5), P_(0.6, SEA - 3.0), P_(0.0, 24.0),
                 P_(-10.0, 14.0), P_(-26.0, 5.0)]
            mm = [STONE, PATH, PATH, WALL, WALL, WALL, WALL, DARK, DARK, DARK, DARK, DARK]
        else:
            h = max(zt - SEA, 2.0)
            drape = min(h * 0.35, 1.4 + 6.0 * hh(key, k, round(u, 2), "dr") ** 2.2 * (0.4 + bump))
            # estrato: altura, inclinacao e largura proprias por massa (prateleira verde quando larga)
            f = 0.30 + 0.45 * hh(key, k, "lf")
            dip = (hh(key, k, "dip") - 0.5) * 11.0
            zl = SEA + h * f + dip * (u - 0.5)
            zl = min(zl, zt - drape - 2.0)
            wl = (0.4 + 3.4 * hh(key, k, "lw")) * (bump ** 0.6)
            if hh(key, k, "noledge") < 0.36:        # massa lisa: sem prateleira (o estrato nao e uma linha continua)
                wl = 0.05
                zl = min(zl, SEA + 2.5 + h * 0.12)
            if notch:
                wl *= 1.0 - notch[0]
            batter = 0.03 * h * hh(key, k, "bt")
            cool = hh(key, k, "cool") > 0.45
            foot = 1.0 + 2.5 * hh(key, k, "ft")
            ot = o - batter
            r = [P_(-2.6, zin), P_(ot * 0.35 - 0.2, zt - 0.2), P_(ot * 0.8 + 0.15, zt - 0.85), P_(ot, zt - drape),
                 P_(ot + batter * 0.5, zl + 0.7), P_(o + wl, zl), P_(o + wl + 0.15, zl - 0.6 - 1.6 * hh(key, k, u, "l2")),
                 P_(o + wl + foot * 0.4, SEA + 4.0), P_(o + wl + foot, SEA - 1.0), P_(o + wl + foot * 0.6, 26.0),
                 P_(o - 6.0 - 8.0 * hh(key, k, "k1"), 16.0), P_(o - 22.0 - 10.0 * hh(key, k, "k2"), 6.0)]
            mid = MOSS if wl > 1.2 else (ROCK if not cool else ROCKC)
            low = ROCKC if cool else ROCK
            mm = [GDEEP, GDEEP, MOSS, ROCK, mid, MOSS if wl > 1.2 else low, low, low, DARK, DARK, DARK, DARK]
            if math.hypot(x - L.SKULL_C[0], y - L.SKULL_C[1]) < 44.0:
                mm = [GDEEP, MOSS, MOSS, ROCKC, ROCKC if wl <= 1.2 else MOSS, DARK, DARK, DARK, DARK, DARK, DARK, DARK]
            if notch and notch[0] > 0.3:
                mm = [DIRTD, DARK, DARK, DARK, DARK, DARK, DARK, DARK, DARK, DARK, DARK, DARK]
        # ultima linha: para dentro da ilha (a quilha afina ate a ponta)
        r.append((cx + (x - cx) * 0.35, cy + (y - cy) * 0.35, -4.0))
        for i_ in range(13):
            rows[i_].append(r[i_])
        for i_ in range(12):
            mats[i_].append(mm[i_])
    loft_rows(mb, rows, mats, True)
    # tampa de baixo: leque para o apice
    bm = mb.bm
    ap = bm.verts.new((cx, cy, L.KEEL - 10.0))
    last = [bm.verts.new(p) for p in rows[-1]]
    fs = []
    n = len(last)
    for i in range(n):
        try:
            fs.append(bm.faces.new((last[(i + 1) % n], last[i], ap)))
        except ValueError:
            pass
    assign(mb, fs, DARK)
    mb.finish()
    return nodes


# ------------------------------------------------------------------ 2. FACES INTERNAS (arrimos e faces de rocha)
def _in_rect(x, y, r):
    return r[0] <= x <= r[2] and r[1] <= y <= r[3]


def edge_runs():
    """bordas das placas (pisos e rochas) com desnivel para fora: [(tipo, [amostras]), ...]; amostra = (x, y, nx, ny,
    z de cima, z de baixo, vizinho anda?)"""
    runs = []
    rim_in = lambda x, y: L.point_in_poly(x, y, RIM) and L.poly_edge_dist(x, y, RIM) > 1.2
    for nm, pl, zf, k in PLATES:
        if k not in ("floor", "rock"):
            continue
        n = len(pl)
        for i in range(n):
            a, b = pl[i], pl[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 0.8:
                continue
            nx, ny = dy / ln, -dx / ln
            m = max(1, int(round(ln / 2.0)))
            cur, kind_c = [], None
            for s in range(m + 1):
                t = s / m
                x, y = a[0] + dx * t, a[1] + dy * t
                kind = None
                me = plate_at(x - nx * 0.6, y - ny * 0.6)
                qx, qy = x + nx * 1.6, y + ny * 1.6
                if me and me[0] == nm and rim_in(qx, qy) and not _in_rect(x, y, TRECHO) and \
                        not (nm == "Court" and y < 357.0 and abs(x) < 25.0):
                    zt = zf(x, y)
                    nb = plate_at(qx, qy)
                    if nb is None:
                        zn, walk = sample(S_.G, S_.bandz, qx, qy), False
                    elif nb[1] == "water":
                        zn, walk = nb[2](qx, qy) - (0.0 if zt - nb[2](qx, qy) < 2.6 else 1.0), False
                    else:
                        zn, walk = nb[2](qx, qy), nb[1] in ("floor", "stair")
                    drop = zt - zn
                    if nb is not None and nb[0] in ("Stair_CasteloA", "Stair_CasteloB") and                             nm in ("Court", "CastleLanding", "Rock_ButtressL", "Rock_CastleFootW"):
                        drop = 0.0                  # lado leste da subida: e a MURALHA do castelo (build_castle_rock)
                    if nb is not None and nb[1] == "stair":
                        walk = "stair"
                    if nb is not None and nb[1] == "water" and drop < 2.6:
                        drop = 0.0
                    if drop >= 0.9:
                        if k == "floor" and nm in ("HarborMid",) or (nm == "T1" and nb and nb[0] == "HarborMid"):
                            kind = "bigwall"
                        elif k == "floor" and drop <= 12.5:
                            kind = "wall"
                        else:
                            kind = "rock"
                        smp = (x, y, nx, ny, zt, zn, walk)
                if kind != kind_c and cur:
                    runs.append((kind_c, nm, cur))
                    cur = []
                kind_c = kind
                if kind:
                    cur.append(smp)
            if cur and kind_c:
                runs.append((kind_c, nm, cur))
    return [r for r in runs if len(r[2]) >= 2]


def wall_run(mb, smp, big=False, key="w"):
    """ARRIMO Wano: pedra aparelhada (kirikomi) em fiadas de altura variada, junta escura rebaixada, capa clara, soco"""
    a, b = smp[0], smp[-1]
    nx, ny = a[2], a[3]
    ux, uy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ux, uy)
    if ln < 0.6:
        return
    ux, uy = ux / ln, uy / ln
    zt = a[4]
    bm = mb.bm
    jf, bf, cf, sf = [], [], [], []

    def Pt(s, o, z):
        return Vector((a[0] + ux * s + nx * o, a[1] + uy * s + ny * o, z))

    def quad(lst, p0, p1, p2, p3):
        try:
            lst.append(bm.faces.new([bm.verts.new(p) for p in (p0, p1, p2, p3)]))
        except ValueError:
            pass

    def zb_at(s):
        t = s / ln * (len(smp) - 1)
        i = min(int(t), len(smp) - 2)
        f = t - i
        return min(smp[i][5], smp[i + 1][5]) if f > 0.01 else smp[i][5]

    # pedacos de ate 6 com o pe proprio (pe inclinado junto das escadas)
    seg = max(1, int(math.ceil(ln / 6.0)))
    cap_h = 0.55
    ch_seq = (1.5, 2.1, 1.8, 2.4) if big else (1.05, 1.35, 0.9, 1.2, 1.5)
    bl_lo, bl_hi = (3.0, 5.4) if big else (1.6, 3.6)
    for g in range(seg):
        s0, s1 = ln * g / seg, ln * (g + 1) / seg
        zb = min(zb_at(s0), zb_at(s1)) - 0.4
        # fundo escuro (a junta) a 0,12 da borda
        quad(jf, Pt(s0, 0.12, zb), Pt(s1, 0.12, zb), Pt(s1, 0.12, zt - cap_h + 0.05), Pt(s0, 0.12, zt - cap_h + 0.05))
        z = zb + 0.4 - 0.05
        row = 0
        while z < zt - cap_h - 0.35:
            chh = ch_seq[int(hh(key, g, row, "c") * len(ch_seq)) % len(ch_seq)] * (0.85 + 0.3 * hh(key, g, row, "c2"))
            z1 = min(z + chh, zt - cap_h)
            if zt - cap_h - z1 < 0.5:
                z1 = zt - cap_h
            s = s0 + (0.0 if row % 2 == 0 else -0.6 * hh(key, g, row))
            q = 0
            while s < s1 - 0.05:
                w = bl_lo + (bl_hi - bl_lo) * hh(key, g, row, q, "w")
                e = min(s + w, s1)
                if s1 - e < bl_lo * 0.5:
                    e = s1
                sa, sb = max(s, s0) + 0.07, e - 0.07
                if sb - sa > 0.3:
                    za, zz = (z if z > zb + 0.4 else zb) + 0.07, z1 - 0.07
                    o = 0.26 + 0.12 * hh(key, g, row, q, "o")
                    # frente, topo, laterais (o fundo e a junta): 4 quads
                    quad(bf, Pt(sa, o, za), Pt(sb, o, za), Pt(sb, o, zz), Pt(sa, o, zz))
                    quad(bf, Pt(sa, o, zz), Pt(sb, o, zz), Pt(sb, 0.12, zz), Pt(sa, 0.12, zz))
                    quad(bf, Pt(sb, o, za), Pt(sb, 0.12, za), Pt(sb, 0.12, zz), Pt(sb, o, zz))
                    quad(bf, Pt(sa, 0.12, za), Pt(sa, o, za), Pt(sa, o, zz), Pt(sa, 0.12, zz))
                s = e
                q += 1
            z = z1
            row += 1
        # soco escuro no pe (so onde o vizinho de baixo anda)
        if smp[0][6] or smp[-1][6]:
            zf_ = min(zb_at(s0), zb_at(s1))
            quad(sf, Pt(s0, 0.62, zf_ - 0.3), Pt(s1, 0.62, zf_ - 0.3), Pt(s1, 0.62, zf_ + 0.32), Pt(s0, 0.62, zf_ + 0.32))
            quad(sf, Pt(s0, 0.62, zf_ + 0.32), Pt(s1, 0.62, zf_ + 0.32), Pt(s1, 0.3, zf_ + 0.32), Pt(s0, 0.3, zf_ + 0.32))
    # capa clara continua: topo 0,22 acima do piso, balanco 0,4, entra 0,9 no piso
    z0, z1 = zt - cap_h + 0.22, zt + 0.22
    e0, e1 = -0.08 if True else 0.0, ln + 0.08
    quad(cf, Pt(e0, 0.5, z0), Pt(e1, 0.5, z0), Pt(e1, 0.5, z1), Pt(e0, 0.5, z1))
    quad(cf, Pt(e0, 0.5, z1), Pt(e1, 0.5, z1), Pt(e1, -0.9, z1), Pt(e0, -0.9, z1))
    quad(cf, Pt(e0, 0.12, z0), Pt(e1, 0.12, z0), Pt(e1, 0.5, z0), Pt(e0, 0.5, z0))
    for s_, sg in ((e0, -1), (e1, 1)):
        p = [Pt(s_, 0.5, z0), Pt(s_, 0.5, z1), Pt(s_, -0.9, z1), Pt(s_, -0.9, z0)]
        quad(cf, *(p if sg > 0 else p[::-1]))
    for lst in (jf, bf, cf, sf):
        for f in lst:
            f.normal_update()
    # orienta: tudo para fora (+n) / para cima
    for f in jf + bf + cf + sf:
        c = f.calc_center_median()
        if abs(f.normal.z) > 0.7:
            if f.normal.z < 0 and f in cf[1:2]:
                f.normal_flip()
            elif f.normal.z < 0 and f not in cf[2:3]:
                f.normal_flip()
    assign(mb, jf, JOINT)
    assign(mb, bf, WALL)
    assign(mb, cf, PATH)
    assign(mb, sf, JOINT)


def _fix_normals(faces, ref):
    """vira para fora: ref = funcao(face) -> vetor esperado"""
    for f in faces:
        f.normal_update()
        if f.normal.dot(ref(f)) < 0:
            f.normal_flip()


def rock_run(mb, smp, key):
    """FACE DE ROCHA facetada ao longo da borda: capa verde que cai, facetas de 5..12, relevo limitado embaixo quando o
    vizinho anda (cabeca do jogador), mais solto acima; estrato quando alta"""
    pts = [(s[0], s[1]) for s in smp]
    # nos a cada ~6 (facetas), reamostrando a polilinha
    dense = []
    acc = 0.0
    for i in range(len(smp)):
        if i:
            acc += math.dist(pts[i - 1], pts[i])
        dense.append((acc, smp[i]))
    tot = acc
    if tot < 1.5:
        return
    nodes = []
    d = 0.0
    q = 0
    while True:
        j = 0
        while j < len(dense) - 2 and dense[j + 1][0] < d:
            j += 1
        s0, s1 = dense[j][1], dense[min(j + 1, len(dense) - 1)][1]
        span = (dense[min(j + 1, len(dense) - 1)][0] - dense[j][0]) or 1.0
        t = max(0.0, min(1.0, (d - dense[j][0]) / span))
        lerp = lambda k: s0[k] + (s1[k] - s0[k]) * t
        nodes.append((lerp(0), lerp(1), s0[2], s0[3], lerp(4), min(s0[5], s1[5]), s0[6] or s1[6], q))
        if d >= tot - 0.01:
            break
        d = min(tot, d + 5.0 + 6.0 * hh(key, q, "fs"))
        q += 1
    n = len(nodes)
    nrm = normals([(nd[0], nd[1]) for nd in nodes], False, 1) if n > 2 else [(nodes[0][2], nodes[0][3])] * n
    tall = max(nd[4] - nd[5] for nd in nodes) > 14.0
    R = 9 if tall else 7
    rows = [[] for _ in range(R)]
    mats = [[] for _ in range(R - 1)]
    zl0 = 0.45 + 0.25 * hh(key, "zl")
    cool = hh(key, "cool") > 0.62
    for i, (x, y, _nx, _ny, zt, zb, walk, q) in enumerate(nodes):
        nx, ny = nrm[i]
        h = max(zt - zb, 1.2)
        endf = 0.0 if i in (0, n - 1) else 1.0
        o_up = (0.3 + 2.4 * hh(key, q, "o")) * endf * (1.0 + min(2.2, h / 18.0))   # face alta = relevo maior
        if walk == "stair":
            o_up = min(o_up, 1.2)               # ao lado de escada: a face nao avanca sobre quem sobe
        o_lo = min(o_up, 0.7) if walk else o_up * 1.15
        drape = min(h * 0.4, 0.8 + 3.2 * hh(key, q, "dr") ** 1.8)
        P_ = lambda off, z: (x + nx * off, y + ny * off, z)
        zlo = zb + min(6.5, h * 0.6) if walk else zb + h * 0.3
        low = ROCKC if cool else ROCK
        if tall:
            # prateleira de estrato no meio da face alta (musgo em cima, lingua que cai), altura com mergulho
            zl = zb + h * zl0 + (hh(key, q, "zj") - 0.5) * 3.0
            zl = max(zlo + 2.0, min(zl, zt - drape - 2.5))
            wl = (0.8 + 2.6 * hh(key, q, "wl")) * endf
            o_mid = o_up * 0.6 + (0.4 if not walk else 0.0)
            r = [P_(-1.4, zt - 0.3), P_(0.18 + o_up * 0.3, zt - 0.12), P_(o_up * 0.85 + 0.12, zt - drape),
                 P_(o_up, zl + 0.7), P_(o_up + wl, zl), P_(o_up + wl * 0.85, zl - 0.8 - 1.6 * hh(key, q, "ld")),
                 P_(max(o_lo, min(o_mid, o_up)), zlo), P_(o_lo * 0.9 + 0.1, zb + 0.2), P_(o_lo * 0.6 + 0.1, zb - 0.7)]
            up = ROCK if hh(key, q, "tone") > 0.3 else ROCKC     # tom POR FACETA na metade de cima (contraste na sombra)
            mm = [GDEEP, MOSS, up, MOSS if wl > 1.0 else up, MOSS if wl > 1.0 else up, low, low,
                  DIRTD if walk else ROCKC]
        else:
            zl = zb + h * (0.45 + 0.2 * hh(key, "zl"))
            r = [P_(-1.4, zt - 0.3), P_(0.18 + o_up * 0.3, zt - 0.12), P_(o_up * 0.85 + 0.12, zt - drape),
                 P_(o_up, max(zl, zlo + 0.5)), P_(o_lo, zlo), P_(o_lo * 0.9 + 0.1, zb + 0.2), P_(o_lo * 0.6 + 0.1, zb - 0.7)]
            mm = [GDEEP, MOSS, ROCK, low, low, DIRTD if walk else ROCKC]
        for k_ in range(1, R):
            if r[k_][2] > r[k_ - 1][2] - 0.05:
                r[k_] = (r[k_][0], r[k_][1], r[k_ - 1][2] - 0.05)
        for k_ in range(R):
            rows[k_].append(r[k_])
        for k_ in range(R - 1):
            mats[k_].append(mm[k_])
    loft_rows(mb, rows, mats, False)


def build_edges():
    mw = MB("OP_Ter_Walls", C, None, detail="far", floor=-999)
    mr = mw                     # faces de rocha no mesmo objeto dos arrimos (orcamento de MeshParts)
    for i, (kind, nm, smp) in enumerate(edge_runs()):
        key = "%s_%d" % (nm, i)
        if kind == "wall":
            wall_run(mw, smp, False, key)
        elif kind == "bigwall":
            wall_run(mw, smp, True, key)
        else:
            rock_run(mr, smp, key)
    mw.finish()


# ------------------------------------------------------------------ massas soltas: rochedos, agulhas, crista
def crag(mb, cx, cy, r, z0, z1, key, n=None, steps=2, lean=(0.0, 0.0), cap=GDEEP, m=ROCK, mlow=ROCKC, sx=1.0,
         ang=0.0, top_tilt=0.0, drape=1.0, taper=None):
    """MASSA de rocha facetada (5..8 faces de raio dirigido), em 'steps' estratos que recuam para cima, topo inclinado
    com capa verde que escorre pela face; inclinacao 'lean' (dx, dy por stud de altura)"""
    bm = mb.bm
    if n is None:
        n = (5, 6, 7, 6, 8)[int(hh(key, "n") * 5) % 5]
    rr = [0.78 + 0.4 * hh(key, k, "r") for k in range(n)]
    rot = ang + hh(key, "rot") * 6.28
    base = [(r * sx * rr[k] * math.cos(rot + 2 * math.pi * k / n), r * rr[k] * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)]
    H_ = z1 - z0
    tdx, tdy = math.cos(rot * 1.7), math.sin(rot * 1.7)
    levels = []
    for s in range(steps + 1):
        f = s / steps
        levels.append(z0 + H_ * f)
    rings = []
    mats = []

    def ring(scale, z, tilt=0.0, dz=None):
        out = []
        for k, (u, v) in enumerate(base):
            zz = z + (tilt * (u * tdx + v * tdy) if tilt else 0.0) + (dz[k] if dz else 0.0)
            out.append(Vector((cx + u * scale + lean[0] * (zz - z0), cy + v * scale + lean[1] * (zz - z0), zz)))
        return out
    sc = 1.0
    # pe (abaixo de z0 2) -> estratos -> topo
    rings.append(ring(1.05, z0 - 2.0))
    mats.append(mlow)
    for s in range(steps):
        za, zb_ = levels[s], levels[s + 1]
        rings.append(ring(sc, za + 0.01))
        mats.append(mlow if s == 0 and steps > 1 else m)
        sc2 = sc * ((0.8 + 0.1 * hh(key, s, "st")) if taper is None else taper * (0.94 + 0.12 * hh(key, s, "st")))
        if s < steps - 1:
            rings.append(ring(sc, zb_ - 0.5))
            mats.append(MOSS if hh(key, s, "ledge") > 0.5 else m)       # prateleira verde no recuo
            rings.append(ring(sc2, zb_))
            mats.append(m)
        sc = sc2
    dz = [-(0.6 + 2.6 * drape * hh(key, k, "d") ** 1.5) for k in range(n)]
    rings.append(ring(sc, z1, top_tilt, dz))
    mats.append(cap)
    rings.append(ring(sc * 0.86, z1 + 0.6, top_tilt))
    mats.append(cap)
    rings.append(ring(sc * 0.55, z1 + 1.0, top_tilt))
    vs = [[bm.verts.new(p) for p in rg] for rg in rings]
    fs_by = {}
    for r_ in range(len(vs) - 1):
        for k in range(n):
            j = (k + 1) % n
            try:
                f = bm.faces.new((vs[r_][k], vs[r_][j], vs[r_ + 1][j], vs[r_ + 1][k]))
            except ValueError:
                continue
            fs_by.setdefault(mats[r_], []).append(f)
    try:
        top = bm.faces.new(vs[-1])
        fs_by.setdefault(cap, []).append(top)
    except ValueError:
        pass
    for mm, fl in sorted(fs_by.items()):
        for f in fl:
            f.normal_update()
            c = f.calc_center_median()
            if f.normal.dot(Vector((c.x - cx, c.y - cy, 0.0))) < -1e-4 and abs(f.normal.z) < 0.99:
                f.normal_flip()
            if abs(f.normal.z) >= 0.99 and f.normal.z < 0:
                f.normal_flip()
        assign(mb, fl, mm)


def build_masses():
    mb = MB("OP_Ter_Rocks", C, None, detail="far", floor=-999)
    # AGULHAS presas a ilha atras do castelo (moldura da concept; topo < torre 216; com ombro verde para o op_veg)
    # pinaculos: base larga, 3..4 estratos que AFINAM (0,68..0,78), inclinacao propria, topo inclinado com verde
    for i, (x, y, r, zt, lean, st, tp) in enumerate((
            (-122.0, 458.0, 17.0, 162.0, (0.03, 0.04), 3, 0.74), (-66.0, 488.0, 20.0, 178.0, (-0.01, 0.03), 4, 0.76),
            (112.0, 486.0, 18.0, 170.0, (-0.04, 0.03), 4, 0.72), (178.0, 452.0, 15.0, 150.0, (0.05, 0.01), 3, 0.7),
            (230.0, 358.0, 11.0, 132.0, (0.03, -0.01), 2, 0.72))):
        crag(mb, x, y, r, 60.0, zt, "needle%d" % i, steps=st, lean=lean, top_tilt=0.16, drape=1.8, taper=tp)
    # ombros/rochedos sobre as rochas da planta (quebram o topo chato): (x, y, r, z0, z1)
    for i, (x, y, r, z0, z1) in enumerate((
            (-38.0, 14.0, 6.0, 89.0, 96.0), (44.0, 18.0, 7.0, 85.0, 93.0), (92.0, 26.0, 8.0, 85.0, 92.0),
            (-196.0, 92.0, 7.0, 89.0, 95.0), (-50.0, 480.0, 12.0, 149.0, 158.0), (10.0, 486.0, 10.0, 149.0, 155.0),
            (52.0, 482.0, 9.0, 149.0, 156.0), (-100.0, 446.0, 9.0, 117.0, 128.0), (-116.0, 424.0, 7.0, 117.0, 124.0),
            (120.0, 470.0, 12.0, 119.0, 132.0), (160.0, 412.0, 11.0, 119.0, 128.0), (194.0, 380.0, 8.0, 119.0, 126.0),
            (276.0, 336.0, 9.0, 103.0, 112.0), (230.0, 322.0, 7.0, 99.0, 106.0), (130.0, 372.0, 8.0, 103.0, 109.0),
            (-48.0, 354.0, 7.0, 123.0, 130.0), (46.0, 351.0, 7.0, 127.0, 133.0))):
        crag(mb, x, y, r, z0, z1, "crag%d" % i, steps=1 if z1 - z0 < 9 else 2, top_tilt=0.1)
    # CONTRAFORTES do fundo: massas largas que saem do mar contra o paredao de tras (profundidade e sombra)
    for i, (x, y, r, zt) in enumerate(((142.0, 503.0, 22.0, 106.0), (56.0, 511.0, 26.0, 124.0), (-14.0, 509.0, 19.0, 104.0),
                                        (-92.0, 494.0, 24.0, 118.0), (-168.0, 455.0, 20.0, 90.0), (-229.0, 404.0, 17.0, 86.0),
                                        (-240.0, 300.0, 15.0, 78.0), (-224.0, 150.0, 16.0, 80.0))):
        crag(mb, x, y, r, 26.0, zt, "backbut%d" % i, steps=3, top_tilt=0.18, drape=1.7, sx=1.3, taper=0.8,
             lean=(0.0, -0.02 if y > 300 else 0.0))
    # ASSENTO DA CAVEIRA: a nuca se funde numa massa escura atras (leste) do cranio; queixo apoiado num ressalto
    sx_, sy_ = L.SKULL_C
    a = math.radians(L.SKULL_FACE_DEG)
    fx, fy = math.cos(a), math.sin(a)
    crag(mb, sx_ - fx * 14.0, sy_ - fy * 14.0, 17.0, 84.0, 104.0, "skullnape", steps=2, cap=MOSS, m=DARK, mlow=DARK,
         top_tilt=0.15)
    crag(mb, sx_ + fx * 8.0, sy_ + fy * 8.0, 13.0, 82.0, 88.5, "skullchin", steps=1, cap=MOSS, m=DARK, mlow=DARK)
    # ESPORAO DA ESPADA: crista de massas que sobe do canto NE ate o pinaculo (z 100) onde a espada crava
    wx, wy = L.SWORD_POS
    for i, (t, r, z1, st) in enumerate(((0.02, 22.0, 104.0, 2), (0.11, 17.0, 88.0, 2), (0.19, 19.0, 78.0, 2),
                                         (0.28, 15.0, 64.0, 1), (0.36, 18.0, 70.0, 2), (0.45, 16.0, 74.0, 2),
                                         (0.53, 14.0, 60.0, 1), (0.61, 17.0, 64.0, 2), (0.70, 16.0, 76.0, 2),
                                         (0.79, 15.0, 70.0, 1), (0.87, 18.0, 86.0, 2))):
        x_, y_ = 190.0 + (wx - 190.0) * t, 478.0 + (wy - 478.0) * t
        side = (hh("spurside", i) - 0.5) * 8.0              # cumeada sinuosa (nao uma fila reta)
        ax_, ay_ = (wy - 478.0), -(wx - 190.0)
        al = math.hypot(ax_, ay_)
        crag(mb, x_ + ax_ / al * side, y_ + ay_ / al * side, r, 26.0, z1, "spur%d" % i, steps=st, top_tilt=0.14,
             drape=1.5, sx=1.25, ang=math.atan2(wy - 478.0, wx - 190.0), taper=0.78)
    crag(mb, wx, wy, 15.0, 26.0, L.SWORD_ROCK_Z - 18.0, "spurpin0", steps=2, top_tilt=0.0)
    crag(mb, wx, wy, 10.0, L.SWORD_ROCK_Z - 19.0, L.SWORD_ROCK_Z, "spurpin1", steps=1, top_tilt=0.0, n=7, drape=0.6)
    mb.finish()


# ------------------------------------------------------------------ 4. ROCHEDO DO CASTELO (proa + canal da cachoeira)
def build_castle_rock():
    mb = MB("OP_Ter_CastleRock", C, None, detail="far", floor=-999)
    bm = mb.bm
    zt = CC
    zb = L.BASIN_Z - 2.6
    YF = 352.0
    by = {}

    def poly(pts, m):
        try:
            f = bm.faces.new([bm.verts.new(p) for p in pts])
        except ValueError:
            return None
        by.setdefault(m, []).append(f)
        return f

    def box(x0, x1, y0, y1, z0, z1, m, top=None):
        p = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        poly([(x, y, z1) for x, y in p], top or m)
        for k in range(4):
            a, b = p[k], p[(k + 1) % 4]
            poly([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m)
    # face da proa: lajes verticais largas (x -25..-6 e 6..25), paineis dos estandartes planos; estrato a 117
    ZL = 117.0
    slabs = [(-25.0, -19.5, 0.75, 0.3), (-19.5, -12.8, 0.25, 0.0), (-12.8, -7.2, 0.3, 0.15), (-7.2, -5.6, 0.6, 0.2),
             (5.6, 7.2, 0.65, 0.2), (7.2, 13.4, 0.3, 0.1), (13.4, 19.5, 0.25, 0.0), (19.5, 25.0, 0.85, 0.4)]
    for i, (xa, xb, oa, ob) in enumerate(slabs):
        # (y da face em cima, y em baixo do estrato): painel a 352,0 / 351,7 (estandartes a 351,2 na frente)
        ya_up, ya_lo = YF - oa, YF - 0.3 - ob - 0.3
        top = [(xa, YF + 1.2, zt - 0.3), (xb, YF + 1.2, zt - 0.3), (xb, ya_up - 0.15, zt - 0.15), (xa, ya_up - 0.15, zt - 0.15)]
        poly(top, GDEEP)
        dr = 1.4 + 4.2 * hh("cf", i, "dr") ** 1.5
        poly([(xa, ya_up - 0.15, zt - 0.15), (xb, ya_up - 0.15, zt - 0.15), (xb, ya_up, zt - dr), (xa, ya_up, zt - dr)], MOSS)
        poly([(xa, ya_up, zt - dr), (xb, ya_up, zt - dr), (xb, ya_up, ZL + 0.6), (xa, ya_up, ZL + 0.6)], ROCK)
        poly([(xa, ya_up, ZL + 0.6), (xb, ya_up, ZL + 0.6), (xb, ya_lo, ZL), (xa, ya_lo, ZL)], MOSS if oa == 0 else ROCK)
        poly([(xa, ya_lo, ZL), (xb, ya_lo, ZL), (xb, ya_lo, zb), (xa, ya_lo, zb)], ROCK if i % 3 else ROCKC)
        # laterais das lajes (entre a laje e a vizinha recuada)
        for x_, sg in ((xa, -1), (xb, 1)):
            poly([(x_, ya_up, zt - dr), (x_, YF + 1.0, zt - dr), (x_, YF + 1.0, zb), (x_, ya_lo, zb)], ROCKC)
    # CANAL CENTRAL: fundo molhado escuro recuado (y 355), boca da nascente (vazio) sob a varanda, labio de pedra
    poly([(-5.6, 355.0, zb), (5.6, 355.0, zb), (5.6, 355.0, 128.4), (-5.6, 355.0, 128.4)], DARK)
    for x_ in (-5.6, 5.6):
        poly([(x_, 352.0, zb), (x_, 355.0, zb), (x_, 355.0, zt - 0.3), (x_, 352.0, zt - 0.3)], DARK)
    poly([(-3.4, 357.6, 128.4), (3.4, 357.6, 128.4), (3.4, 357.6, 134.0), (-3.4, 357.6, 134.0)], VOID)
    for x_ in (-3.4, 3.4):
        poly([(x_, 355.0, 128.4), (x_, 357.6, 128.4), (x_, 357.6, 134.0), (x_, 355.0, 134.0)], DARK)
    poly([(-3.4, 355.0, 134.0), (3.4, 355.0, 134.0), (3.4, 357.6, 134.0), (-3.4, 357.6, 134.0)], DARK)
    poly([(-5.6, 355.0, 128.4), (-3.4, 355.0, 128.4), (-3.4, 355.0, 134.0), (-5.6, 355.0, 134.0)], DARK)
    poly([(3.4, 355.0, 128.4), (5.6, 355.0, 128.4), (5.6, 355.0, 134.0), (3.4, 355.0, 134.0)], DARK)
    poly([(-5.6, 355.0, 134.0), (5.6, 355.0, 134.0), (5.6, 355.0, zt - 0.3), (-5.6, 355.0, zt - 0.3)], DARK)
    poly([(-5.6, 352.0, zt - 0.3), (5.6, 352.0, zt - 0.3), (5.6, 355.0, zt - 0.3), (-5.6, 355.0, zt - 0.3)], MOSS)
    poly([(-5.6, 355.0, zt - 0.36), (5.6, 355.0, zt - 0.36), (5.6, 352.0, zt - 0.36), (-5.6, 352.0, zt - 0.36)], STONE)
    # labio (bica) de pedra: a agua sai em (0, 351, 132,2)
    box(-4.2, 4.2, 350.6, 357.6, 131.0, L.CASTLE_FALL[2] - 0.15, STONE, top=DARK)
    # 2 degraus de pedra molhada no pe do canal (a queda bate e espalha na bacia)
    box(-5.4, 5.4, 351.0, 355.0, zb, 99.2, DARK)
    for mm, fl in sorted(by.items()):
        for f in fl:
            f.normal_update()
            c = f.calc_center_median()
            # fora = para -y (frente) e para fora do canal; topos para cima
            if abs(f.normal.z) > 0.7:
                if f.normal.z < 0 and not (mm == STONE):
                    f.normal_flip()
            elif abs(f.normal.y) > 0.5:
                if f.normal.y > 0 and not (abs(c.x) < 5.7 and c.y > 351.5 and mm in (DARK, VOID) and abs(f.normal.y) > 0.9
                                           and c.y >= 355.0 - 0.01) and mm not in (STONE,):
                    f.normal_flip()
            else:
                # laterais: dentro do canal apontam para o eixo; nas lajes apontam para longe do vizinho recuado
                if abs(c.x) < 6.0 and c.y > 351.5:
                    if f.normal.x * c.x > 0:
                        f.normal_flip()
        assign(mb, fl, mm)
    mb.finish()
    # MURALHA DO CASTELO ao longo da subida (escadas CasteloA/B, x = -64): pedra aparelhada de blocos grandes, do degrau
    # da escada ate o topo do que esta atras (CastleFootW 101 / ButtressL 124 / patio 136,2)
    mw = MB("OP_Ter_CastleWall", C, None, detail="far", floor=-999)
    za = _stair_z("CasteloA")
    zb2 = _stair_z("CasteloB")
    for (y0, y1) in ((337.0, 350.0), (350.0, 366.0), (366.0, 380.0), (396.0, 437.0)):
        smp = []
        for k in range(int((y1 - y0) / 2.0) + 1):
            y = y0 + (y1 - y0) * k / int((y1 - y0) / 2.0)
            top = ground(-62.5, y)
            low = za(-71.0, y) if y < 382.0 else (CL if y < 396.0 else zb2(-71.0, y))
            smp.append((-64.0, y, -1.0, 0.0, top, low, True))
        smp = smp[::-1]                      # percurso com o lado de fora a direita (-x)
        smp = [(x, y, nx, ny, smp[0][4], zl, w) for x, y, nx, ny, zt_, zl, w in smp] if False else smp
        # topo por trecho (o mais alto), pe por amostra
        tz = max(s[4] for s in smp)
        smp = [(s[0], s[1], s[2], s[3], tz, s[5], s[6]) for s in smp]
        wall_run(mw, smp, True, "castlewall%d" % int(y0))
    mw.finish()


def remove_blockout_castle_cliff():
    ob = bpy.data.objects.get("OP_Cas_Cliff")
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)


# ------------------------------------------------------------------ cais de madeira (pier e palafita sobre estacas)
def build_piers():
    mb = MB("OP_Ter_Piers", C, None, detail="far", floor=-999)
    for (x0, y0, x1, y1) in ((222.2, 110.0, 234.0, 200.0), (222.2, 40.0, 246.0, 76.0)):
        mb.box((x1 - x0, y1 - y0, 0.9), ((x0 + x1) / 2, (y0 + y1) / 2, L.HARBOR - 0.45), (0, 0, 0), WOOD, 0.0)
        # testeira escura
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1))):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            mb.box((ln + 0.5, 0.4, 1.3), ((a[0] + b[0]) / 2 + dy / ln * 0.18, (a[1] + b[1]) / 2 - dx / ln * 0.18,
                                          L.HARBOR - 0.75), (0, 0, math.atan2(dy, dx)), WOODD, 0.0)
        # juntas das tabuas (frisos escuros rebaixados 0,03 nao: faixas finas 0,02 acima seriam z-fight) -> vigas por baixo
        y = y0 + 3.0
        while y < y1 - 1.0:
            mb.box((x1 - x0 - 0.4, 0.6, 0.8), ((x0 + x1) / 2, y, L.HARBOR - 1.3), (0, 0, 0), WOODD, 0.0)
            y += 6.0
    mb.finish()


# ------------------------------------------------------------------ cameras de revisao da zona
CAMS = {
    "CAM_OPTer_CastleRock": ((-14.0, 262.0, 118.0), (0.0, 352.0, 117.0), 30),
    "CAM_OPTer_PH_Forecourt": ((-10.0, 330.0, CF + 5.5), (0.0, 352.0, 124.0), 20),
    "CAM_OPTer_PH_CastleStair": ((-71.0, 344.0, CF + 7.0), (-64.0, 400.0, 126.0), 22),
    "CAM_OPTer_PH_WallW3": ((-80.0, 262.0, P + 5.5), (-118.0, 306.0, P + 3.0), 22),
    "CAM_OPTer_PH_WallAdro": ((60.0, 292.0, P + 5.5), (40.0, 318.0, P + 2.0), 22),
    "CAM_OPTer_PH_WallSW": ((-132.0, 104.0, T1 + 5.5), (-162.0, 120.0, T1 + 2.0), 22),
    "CAM_OPTer_PH_Harbor": ((176.0, 66.0, L.HARBOR + 5.5), (160.0, 104.0, L.HMID), 22),
    "CAM_OPTer_PH_Quay": ((231.0, 150.0, L.HARBOR + 5.5), (204.0, 205.0, 68.0), 24),
    "CAM_OPTer_CliffSW": ((-330.0, -40.0, 60.0), (-160.0, 70.0, 64.0), 24),
    "CAM_OPTer_CliffFront": ((-80.0, -110.0, 52.0), (-20.0, 20.0, 70.0), 24),
    "CAM_OPTer_CliffBack": ((-40.0, 720.0, 110.0), (-20.0, 470.0, 100.0), 24),
    "CAM_OPTer_Spur": ((380.0, 470.0, 110.0), (240.0, 540.0, 70.0), 26),
    "CAM_OPTer_Enseada": ((300.0, 40.0, 70.0), (250.0, 240.0, 70.0), 24),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        camera(n, loc, tgt, lens)


# ------------------------------------------------------------------ build
def build():
    noise.seed_set(5521)
    remove_blockout_castle_cliff()
    _prepare()
    build_ground()
    build_ring()
    build_edges()
    build_castle_rock()
    build_masses()
    build_piers()
    cams()
