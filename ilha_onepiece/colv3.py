# colv3.py - COLISAO V3: "o que se ve e o que colide" (motor GENERICO; a configuracao e de cada ilha: op_col.V3).
# Rodada 3 (10/10): o jogador ficava em pe no ar sobre guarda-corpos e muros, andava no telhado/muralha do castelo,
# atravessava paredes de casa e a camera batia em parede invisivel - a colisao era um enxame de caixas COL_ separadas do
# visual (guardas de 8,5 erguidas pelo raise_guards, caixas CamOccluder) e o visual tinha CanCollide=false.
#
# O MOTOR (roda no export e no QA, NUNCA salva o .blend):
#   1. purge(cfg): apaga as COL_ que nao estao na lista branca da ilha (chao/escada/ponte/leito = solido sob o piso
#      visivel; jogabilidade: trava do portao, guarda da ancora; guardas de queda DOCUMENTADAS).
#   2. split(cfg): em cada objeto visual colidivel, as faces de material solido (pedra, madeira, reboco, telha, rocha,
#      casca, metal) viram AGRUPAMENTOS convexos que o Roblox colide pela propria forma (CollisionFidelity Hull):
#        a) pecas soltas (ilhas de vertices) -> grupos que se tocam (bbox +0,1);
#        b) cada grupo e testado: o fecho convexo NAO pode roubar espaco livre - um ponto andavel (amostrado sobre
#           todo piso visivel/colisao, a +1,2 / +2,5 / +4,0) dentro do fecho, a mais de 0,9 de qualquer geometria
#           solida e que nao esteja num comodo fechado (teto em cima + paredes nas 8 direcoes) = rua entre casas,
#           convés entre amuradas, interior aberto, vao de porta. Roubou -> o grupo e partido no eixo principal (pelo
#           maior vao entre pecas) ate cada pedaco ficar justo; peca unica concava -> partida pelas faces;
#        c) tamanho maximo 150 em X/Y (o export fatiaria em celulas) e AABB de MUNDO fora das zonas 'keepout' (o
#           SpawnMinerio usa GetPartBoundsInBox: uma peca girada 145 graus tem AABB enorme);
#        d) pedacos vizinhos se juntam de novo quando o fecho da uniao continua justo (menos MeshParts);
#        e) PORTADORES: em cada agrupamento so os materiais que acrescentam forma viram MeshPart colidivel (o resto -
#           frisos, ouro, lanterna - fica no objeto original, so visual, dentro do fecho dos portadores);
#      cada portador vira um objeto '<objeto>_k<n>_<j>' (1 material: o export nao funde nada) com a propriedade
#      colv3 = 'H' (Hull). O que nao e portador continua no objeto original, CanCollide=false.
#   3. meshes(cfg): a colisao COMO O ROBLOX VAI FAZER (para o QA): caixas COL_ restantes + o fecho convexo de cada
#      peca colv3 (Hull = fecho exato; Box = AABB de mundo).
# Portar para outra ilha: copie este arquivo, monte um Config (prefixos de objeto/material, COL_ mantidas, matriz de
# mundo, keepout) e chame purge/split antes do export_roblox.main() (piece_flags acrescenta a letra colv3 e o bloco Lua
# lua_block() aplica CanCollide/CanQuery/CollisionFidelity nas MeshParts no montar).
import math, time
import numpy as np
import bpy, bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

FIDELITY = {"H": "Hull", "B": "Box", "D": "Default", "P": "PreciseConvexDecomposition"}


class Config:
    skip_obj = ()                  # prefixos de objeto que nunca colidem pelo visual (pele de chao, VFX, asset com COL)
    only_obj = ()                  # se nao vazio: so estes prefixos de objeto colidem pelo visual
    nocol_mat = ("Leaf", "Flower", "Cloth", "Rope", "Glass", "Window", "Emblem", "Energy", "Summon_", "Crystal", "P_",
                 "Roof")           # TELHADO: so colide o que esta ao ALCANCE (roof_cond): ninguem anda em telhado alto
                                   # (beiral > pulo por projeto) e a camera nao 'pula' no beiral; o corpo da casa colide
    roof_cond = ("Roof",)          # telhado ao alcance (pular nele de algo alcancado ou cair nele de um patamar) colide
    roof_reach_xy = 6.0            # ... distancia horizontal de um ponto alcancado ate a planta do pedaco de telhado
    cut_len = 24.0                 # face solida mais longa que isto e cortada (coplanar) para poder ser partida
    nocol_zones = []               # [(poligono xy, zlo, zhi)]: peca com centro dentro nao colide (praca de mineracao)
    air_r = 3.0                    # topo de fecho a <= air_r (horizontal) de algo alcancado e <= pulo acima dele ...
    air_step = 1.5                 # ... amostrado neste passo ...
    air_d = 1.0                    # ... precisa de visual a <= air_d embaixo (senao e 'em pe no ar': o fecho e partido)
    air_n = 2                      # amostras no ar que recusam o fecho (1 amostra de quina passa)
    leaf_drop = 2.5                # folha indivisivel que ainda rouba/fica no ar: < leaf_drop (diagonal) nao colide;
                                   # maior vira PreciseConvexDecomposition (o Roblox decompoe a propria malha)
    corridors = []                 # rotas de jogo [(x, y[, z]), ...]: corredor livre de fecho (contrato das rotas)
    corridor_r = 1.0               # raio do corpo no corredor (o andador do QA usa 1,1 x 0,9): fecho inflado deste raio
    corridor_h = (2.0, 2.8, 3.6, 4.3, 5.0)   # alturas do andador do QA (+ intermediarias)
    trunk = []                     # [(prefixo do objeto, prefixo do material, altura)]: arvore so colide o tronco ate
                                   # 'altura' acima do chao (0 = nao colide): ninguem escala copa/arco/galho
    nocol_sub = ("Glow",)          # substring no nome do material
    roof_mat = ("Roof",)           # telhado: nao gera ponto livre (inalcancavel por projeto; o QA confere)
    floor_col = ()                 # prefixos COL_ que sao CHAO (seguram a pele fina por cima)
    keep_col = ()                  # prefixos COL_ que ficam (chao + jogabilidade + guardas documentadas)
    world = None                   # Matrix 4x4 projeto -> mundo (AABB do Roblox); None = identidade
    keepout = []                   # [(poligono xy, zlo, zhi, nome)] proibido para a AABB de mundo de peca colidivel
    keepout_small = 12.0           # ... salvo peca pequena (diagonal da AABB de mundo < isto): a caixa e a propria peca
    min_diag = 1.5                 # agrupamento menor que isto nao colide
    prop_diag = 4.0                # prop ISOLADO (grupo aceito inteiro) com diagonal < prop_diag e altura < prop_h nao
    prop_h = 3.0                   # colide (balde, caixote, saco, pedrinha: o lead pediu 'small props do NOT collide')
    max_xy = 150.0                 # extensao maxima X/Y de um agrupamento (o export fatia > 160)
    skin_h = 0.8                   # peca fina (altura <= isto) assentada no chao (<= skin_d) = pele: nao colide
    skin_d = 0.5
    near = 1.2                     # ponto livre a menos disto da geometria solida nao conta como roubado (vitrine
                                   # rasa, nicho de porta, recuo de fachada e fresta <= ~2,4 podem ser cheios: o corpo
                                   # do jogador tem 2 de largura)
    steal_n = 4                    # o fecho e recusado com >= steal_n pontos roubados (ruido de 1-2 pontos passa)
    heights = (1.2, 2.5, 4.0)      # alturas dos pontos livres acima de cada piso
    seeds = []                     # pontos de partida do alcance (spawn, saida do portao...)
    jump = 7.2                     # pulo padrao do Roblox
    body_r = 0.75                  # raio livre do corpo no alcance ...
    body_h = (1.6, 2.8, 4.0)       # ... nestas alturas (1,6: o espelho do degrau seguinte de uma escada nao bloqueia)
    reach = 7.5                    # so gera ponto livre a <= reach acima de um chao de colisao (pulo 7,2): telhado,
                                   # topo de udatsu e andar de cima ficam de fora (o QA confere o alcance de verdade)
    foliage = ("Leaf", "Flower", "Cloth", "Rope", "Glass")   # copa, flor, pano (noren, estandarte, shimenawa), corda e
                                   # vidro de lanterna NAO fecham passagem nem comodo; janela/shoji/parede fecham
    grid = 1.0                     # passo da amostragem dos pisos
    cover = 0.75                   # material com >= 75% dos vertices a <= cover_m do fecho dos portadores nao vira
    cover_m = 1.0                  # portador (fica so visual: friso, ouro, lanterna dentro do volume)
    small = 10.0                   # agrupamento menor que isto (diagonal): 1 portador so, salvo cobertura < small_cover
    small_cover = 0.6
    max_depth = 22
    verbose = False
    debug = False


def _is_nocol_mat(cfg, m):
    return m.startswith(cfg.nocol_mat) or any(s in m for s in cfg.nocol_sub)


def _visual_objects(cfg):
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_")) or o.hide_render:
            continue
        if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
            continue
        out.append(o)
    return out


def _collidable_obj(cfg, o):
    if o.name.startswith(cfg.skip_obj):
        return False
    if cfg.only_obj and not o.name.startswith(cfg.only_obj):
        return False
    return True


# ------------------------------------------------------------------ 1) lista branca das COL_
def purge(cfg):
    """apaga as COL_ fora da lista branca; devolve {prefixo: n} das apagadas e das mantidas"""
    gone, kept = {}, {}
    import re
    for o in list(bpy.data.objects):
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        k = re.sub(r"_\d+$", "", o.name)
        if o.name.startswith(cfg.keep_col):
            kept[k] = kept.get(k, 0) + 1
            continue
        gone[k] = gone.get(k, 0) + 1
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    return gone, kept


# ------------------------------------------------------------------ fecho convexo / semi-espacos
def hull_verts(P):
    """vertices do fecho convexo de P (n x 3); planos (normais para fora, d) ou None se degenerado (plano/linha)"""
    P = np.asarray(P, dtype=np.float64)
    if len(P) < 4:
        return P, None
    bm = bmesh.new()
    for p in P:
        bm.verts.new(p)
    try:
        res = bmesh.ops.convex_hull(bm, input=bm.verts[:], use_existing_faces=False)
    except Exception:
        bm.free()
        return P, None
    faces = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
    if len(faces) < 4:
        bm.free()
        return P, None
    used = {v for f in faces for v in f.verts}
    HV = np.array([tuple(v.co) for v in used])
    c = HV.mean(axis=0)
    N, D = [], []
    for f in faces:
        f.normal_update()
        n = np.array(tuple(f.normal))
        ln = np.linalg.norm(n)
        if ln < 1e-9:
            continue
        n = n / ln
        p0 = np.array(tuple(f.verts[0].co))
        d = float(n @ p0)
        if n @ c - d > 0:                     # normal para dentro: inverte
            n, d = -n, -d
        N.append(n)
        D.append(d)
    bm.free()
    if len(N) < 4:
        return HV, None
    N = np.array(N)
    D = np.array(D)
    ext = HV.max(axis=0) - HV.min(axis=0)
    if ext.min() < 0.02:                      # placa: sem volume
        return HV, None
    pr = HV @ N.T                             # espessura minima (placa girada tambem e placa)
    if float((pr.max(axis=0) - pr.min(axis=0)).min()) < 0.06:
        return HV, None
    return HV, (N, D)


def inside(planes, Q, margin=0.15):
    """mascara dos pontos Q (m x 3) a >= margin para dentro de todos os planos"""
    if planes is None or len(Q) == 0:
        return np.zeros(len(Q), bool)
    N, D = planes
    return np.all(Q @ N.T - D[None, :] <= -margin, axis=1)


def exit_dist(planes, p, d):
    N, D = planes
    nd = N @ d
    num = D - N @ p
    m = nd > 1e-9
    if not m.any():
        return 1e9
    return float(np.min(num[m] / nd[m]))


# ------------------------------------------------------------------ geometria das cenas
class _Obj:
    """faces de um objeto em coordenadas de mundo (numpy) + pecas soltas"""

    def __init__(self, o, cfg):
        self.o = o
        me = o.data
        mw = o.matrix_world
        n = len(me.vertices)
        co = np.empty(n * 3)
        me.vertices.foreach_get("co", co)
        co = co.reshape(-1, 3)
        M = np.array(mw)
        self.V = co @ M[:3, :3].T + M[:3, 3]
        npoly = len(me.polygons)
        ls = np.empty(npoly, np.int32)
        me.polygons.foreach_get("loop_start", ls)
        lt = np.empty(npoly, np.int32)
        me.polygons.foreach_get("loop_total", lt)
        lv = np.empty(len(me.loops), np.int32)
        me.loops.foreach_get("vertex_index", lv)
        mi = np.empty(npoly, np.int32)
        me.polygons.foreach_get("material_index", mi)
        self.ls, self.lt, self.lv, self.mi = ls, lt, lv, mi
        mats = [(s.name if s else "Default") for s in me.materials] or ["Default"]
        self.mats = mats
        self.fmat = [mats[min(i, len(mats) - 1)] for i in mi]
        col = np.array([not _is_nocol_mat(cfg, mats[min(i, len(mats) - 1)]) for i in range(len(mats))])
        self.fcol = col[np.minimum(mi, len(mats) - 1)] if npoly else np.zeros(0, bool)
        self.npoly = npoly

    def fverts(self, f):
        s = self.ls[f]
        return self.lv[s:s + self.lt[f]]

    def parts(self, faces):
        """ilhas de vertices (union-find) das faces dadas -> lista de arrays de faces"""
        par = {}

        def find(a):
            r = a
            while par[r] != r:
                r = par[r]
            while par[a] != r:
                par[a], a = r, par[a]
            return r
        for f in faces:
            vs = self.fverts(f)
            r0 = None
            for v in vs:
                v = int(v)
                if v not in par:
                    par[v] = v
                r = find(v)
                if r0 is None:
                    r0 = r
                elif r != r0:
                    par[r] = r0
        out = {}
        for f in faces:
            out.setdefault(find(int(self.fverts(f)[0])), []).append(f)
        return [np.array(v, np.int32) for v in out.values()]

    def vids(self, faces):
        return np.unique(np.concatenate([self.fverts(f) for f in faces])) if len(faces) else np.zeros(0, np.int32)

    def centroids(self, faces):
        return np.array([self.V[self.fverts(f)].mean(axis=0) for f in faces])

    def area(self, faces):
        a = 0.0
        for f in faces:
            P = self.V[self.fverts(f)]
            if len(P) < 3:
                continue
            c = P[0]
            for i in range(1, len(P) - 1):
                a += 0.5 * np.linalg.norm(np.cross(P[i] - c, P[i + 1] - c))
        return a


def _bvh_from(objs_faces):
    verts, polys = [], []
    for ob, faces in objs_faces:
        base = len(verts)
        vid = ob.vids(faces)
        remap = {int(v): base + k for k, v in enumerate(vid)}
        verts.extend(map(tuple, ob.V[vid]))
        for f in faces:
            polys.append([remap[int(v)] for v in ob.fverts(f)])
    if not polys:
        return None
    return BVHTree.FromPolygons(verts, polys)


def _col_boxes(prefixes):
    """COL_ com o prefixo dado -> (verts, faces) de mundo"""
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_") or (prefixes and not o.name.startswith(prefixes)):
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [tuple(mw @ v.co) for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
    return verts, polys


# ------------------------------------------------------------------ pontos livres (onde o jogador pode estar)
def free_points(cfg, objs, floor_bvh):
    """amostra todo piso andavel (normal >= 0,7) visivel solido ou de colisao de chao, em varias camadas, e devolve os
    pontos a +heights. Telhado nao gera ponto livre (inalcancavel por projeto: o QA confere)."""
    verts, polys, roof = [], [], []
    for ob in objs:
        fs = np.nonzero(ob.fcol)[0]
        if not len(fs):
            continue
        base = len(verts)
        vid = ob.vids(fs)
        remap = np.full(len(ob.V), -1, np.int64)
        remap[vid] = np.arange(len(vid)) + base
        verts.extend(map(tuple, ob.V[vid]))
        for f in fs:
            polys.append([int(remap[v]) for v in ob.fverts(f)])
            roof.append(ob.fmat[f].startswith(cfg.roof_mat))
    cv, cp = _col_boxes(cfg.floor_col)
    base = len(verts)
    verts += cv
    polys += [[base + i for i in p] for p in cp]
    roof += [False] * len(cp)
    B = BVHTree.FromPolygons(verts, polys)
    FB = BVHTree.FromPolygons(cv, cp) if cp else None
    roof = np.array(roof)
    V = np.array(verts)
    x0, y0, z0 = V.min(axis=0)
    x1, y1, z1 = V.max(axis=0)
    g = cfg.grid
    pts = []
    DOWN = Vector((0, 0, -1))
    for x in np.arange(x0 + g * 0.37, x1, g):
        for y in np.arange(y0 + g * 0.61, y1, g):
            z = z1 + 5.0
            for _ in range(20):
                h = B.ray_cast(Vector((x, y, z)), DOWN, 2000.0)
                if h[0] is None:
                    break
                if h[1].z >= 0.7 and not roof[h[2]]:
                    zz = h[0].z
                    ok = FB is None
                    if not ok:                     # ao alcance: ate 'reach' acima do chao de colisao embaixo
                        f = FB.ray_cast(Vector((x, y, zz + 0.2)), DOWN, cfg.reach + 0.2)
                        ok = f[0] is not None
                    if ok:
                        pts.append((x, y, zz))
                z = h[0].z - 0.05
    P = np.array(pts) if pts else np.zeros((0, 3))
    Q = np.concatenate([P + np.array((0.0, 0.0, hh)) for hh in cfg.heights]) if len(P) else P
    return P, Q


def reach(cfg, P, encl):
    """ALCANCE (BFS a partir de cfg.seeds) sobre as superficies amostradas P: anda (degrau <= step), pula (sobe <= jump)
    e cai de qualquer altura; a celula precisa de corpo livre (nada do visual - menos folhagem - a < body_r de
    +1,0/+2,5/+4,0). Janela/pano contam como parede: o que fica atras deles nao e alcancavel (e o fecho pode encher).
    Devolve a mascara de P alcancado."""
    n = len(P)
    if not n or not cfg.seeds:
        return np.ones(n, bool)
    g = cfg.grid
    I = np.round(P[:, 0] / g).astype(np.int64)
    J = np.round(P[:, 1] / g).astype(np.int64)
    cells = {}
    for k in range(n):
        cells.setdefault((int(I[k]), int(J[k])), []).append(k)
    free = np.ones(n, bool)
    for k in range(n):
        x, y, z = P[k]
        for hh in cfg.body_h:
            if encl.find_nearest(Vector((x, y, z + hh)), cfg.body_r)[0] is not None:
                free[k] = False
                break
    seen = np.zeros(n, bool)
    from collections import deque
    q = deque()
    for sx, sy, sz in cfg.seeds:
        c = cells.get((int(round(sx / g)), int(round(sy / g))), [])
        best = min(c, key=lambda k: abs(P[k, 2] - sz), default=None)
        if best is not None and abs(P[best, 2] - sz) < 4.0:
            seen[best] = True
            q.append(best)
    NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    while q:
        k = q.popleft()
        z = P[k, 2]
        for di, dj in NB:
            for kk in cells.get((int(I[k]) + di, int(J[k]) + dj), ()):
                if seen[kk] or not free[kk]:
                    continue
                if P[kk, 2] - z > cfg.jump:
                    continue
                seen[kk] = True
                q.append(kk)
    return seen


# ------------------------------------------------------------------ teste de roubo de espaco livre
class _Ctx:
    def __init__(self, cfg, Q, solid_bvh, keepout_w, encl_bvh=None):
        self.cfg = cfg
        self.Q = Q
        order = np.argsort(Q[:, 0]) if len(Q) else np.zeros(0, np.int64)
        self.Qs = Q[order] if len(Q) else Q
        self.Qx = self.Qs[:, 0] if len(Q) else np.zeros(0)
        self.solid = solid_bvh
        self.encl = encl_bvh or solid_bvh
        self.keepout = keepout_w
        self.tests = 0
        self.t = 0.0
        self.why = {}
        self.debug = []
        self.H = np.zeros((0, 3))
        self.Hx = np.zeros(0)
        self.rmap = None

    def set_hard(self, H):
        if len(H):
            o = np.argsort(H[:, 0])
            self.H = H[o]
            self.Hx = self.H[:, 0]

    def cand(self, lo, hi):
        i0 = np.searchsorted(self.Qx, lo[0])
        i1 = np.searchsorted(self.Qx, hi[0], side="right")
        S = self.Qs[i0:i1]
        if not len(S):
            return S
        m = (S[:, 1] >= lo[1]) & (S[:, 1] <= hi[1]) & (S[:, 2] >= lo[2]) & (S[:, 2] <= hi[2])
        return S[m]

    def enclosed(self, p, planes):
        """ponto num comodo FECHADO (teto em cima e parede nas 8 direcoes antes de sair do fecho): pode ser cheio"""
        P = Vector(p)
        up = self.encl.ray_cast(P, Vector((0, 0, 1)), 30.0)
        if up[0] is None:
            return False
        for k in range(8):
            a = k * math.pi / 4
            d = np.array((math.cos(a), math.sin(a), 0.0))
            t = exit_dist(planes, np.asarray(p), d)
            h = self.encl.ray_cast(P, Vector(d), t + 0.3)
            if h[0] is None:
                return False
        return True

    def steals(self, HV, planes, limit=2, rec=None):
        """quantos pontos livres o fecho rouba (para cedo em 'limit'; rec = lista que recebe os pontos roubados)"""
        t0 = time.time()
        self.tests += 1
        if planes is None:
            self.t += time.time() - t0
            return 0
        lo, hi = HV.min(axis=0), HV.max(axis=0)
        if len(self.H):                             # corredor de ROTA: nenhum fecho entra (sem tolerancia de 'perto')
            i0 = np.searchsorted(self.Hx, lo[0] - self.cfg.corridor_r)
            i1 = np.searchsorted(self.Hx, hi[0] + self.cfg.corridor_r, side="right")
            S = self.H[i0:i1]
            if len(S):
                r = self.cfg.corridor_r
                S = S[(S[:, 1] >= lo[1] - r) & (S[:, 1] <= hi[1] + r) & (S[:, 2] >= lo[2] - r) & (S[:, 2] <= hi[2] + r)]
                hit = inside(planes, S, margin=-r) if len(S) else S[:0]   # fecho inflado do raio do corpo
                if len(S) and hit.any():
                    if rec is not None:
                        rec.append(("rota",) + tuple(np.round(S[hit][0], 1)))
                    self.t += time.time() - t0
                    return limit
        na = self.air_top(HV, planes, self.cfg.air_n, rec)
        if na >= self.cfg.air_n:
            self.t += time.time() - t0
            return limit
        n = 0
        C = self.cand(lo, hi)
        if not len(C):
            self.t += time.time() - t0
            return n
        C = C[inside(planes, C)]
        if len(C) > 400:
            rng = np.random.default_rng(len(C))
            C = C[rng.permutation(len(C))]
        for p in C:
            nn = self.solid.find_nearest(Vector(p), self.cfg.near)
            if nn[0] is not None:
                continue
            if self.enclosed(p, planes):
                continue
            n += 1
            if rec is not None:
                rec.append(tuple(np.round(p, 1)))
            if n >= limit:
                break
        self.t += time.time() - t0
        return n

    def set_reach(self, PR, g):
        """mapa 2D (passo g) da MAIOR cota alcancada perto (raio air_r) - para saber se um topo de fecho e pulavel"""
        self.rg = g
        if not len(PR):
            self.rmap = None
            return
        I = np.floor(PR[:, 0] / g).astype(np.int64)
        J = np.floor(PR[:, 1] / g).astype(np.int64)
        self.ri0, self.rj0 = int(I.min()) - 4, int(J.min()) - 4
        M = np.full((int(I.max()) - self.ri0 + 5, int(J.max()) - self.rj0 + 5), -1e9)
        np.maximum.at(M, (I - self.ri0, J - self.rj0), PR[:, 2])
        r = int(math.ceil(self.cfg.air_r / g))
        D = M.copy()
        for di in range(-r, r + 1):
            for dj in range(-r, r + 1):
                if di * di + dj * dj > r * r:
                    continue
                S = np.full_like(M, -1e9)
                a0, a1 = max(0, di), M.shape[0] + min(0, di)
                b0, b1 = max(0, dj), M.shape[1] + min(0, dj)
                S[a0 - di:a1 - di, b0 - dj:b1 - dj] = M[a0:a1, b0:b1]
                D = np.maximum(D, S)
        self.rmap = D

    def air_top(self, HV, planes, limit, rec=None):
        """amostras do TOPO do fecho (normal >= 0,6) que o jogador alcanca (pulo de uma superficie alcancada a <= air_r)
        e que nao tem nada visivel a <= air_d embaixo = 'em pe no ar' (a queixa da rodada 3)"""
        if self.rmap is None or planes is None:
            return 0
        N, D = planes
        up = N[:, 2] > 1e-6
        if not up.any():
            return 0
        lo, hi = HV.min(axis=0), HV.max(axis=0)
        g = self.cfg.air_step
        xs = np.arange(lo[0] + g / 2, hi[0], g)
        ys = np.arange(lo[1] + g / 2, hi[1], g)
        if not len(xs) or not len(ys):
            return 0
        X, Y = np.meshgrid(xs, ys, indexing="ij")
        X, Y = X.ravel(), Y.ravel()
        Nu, Du = N[up], D[up]
        Zc = (Du[None, :] - X[:, None] * Nu[None, :, 0] - Y[:, None] * Nu[None, :, 1]) / Nu[None, :, 2]
        k = np.argmin(Zc, axis=1)
        zt = Zc[np.arange(len(X)), k]
        nz = Nu[k, 2]
        dn = ~up
        if dn.any():
            Nd, Dd = N[dn], D[dn]
            with np.errstate(divide="ignore", invalid="ignore"):
                Zb = (Dd[None, :] - X[:, None] * Nd[None, :, 0] - Y[:, None] * Nd[None, :, 1]) / Nd[None, :, 2]
            Zb = np.where(np.abs(Nd[None, :, 2]) > 1e-6, Zb, -1e9)
            zb = Zb.max(axis=1)
        else:
            zb = np.full(len(X), -1e9)
        ok = (zt >= zb + 0.05) & (nz >= 0.6)
        side = np.all(X[:, None] * N[None, :, 0] + Y[:, None] * N[None, :, 1] + zt[:, None] * N[None, :, 2] - D[None, :]
                      <= 0.05, axis=1)
        ok &= side
        if not ok.any():
            return 0
        I = np.floor(X / self.rg).astype(np.int64) - self.ri0
        J = np.floor(Y / self.rg).astype(np.int64) - self.rj0
        inb = (I >= 0) & (J >= 0) & (I < self.rmap.shape[0]) & (J < self.rmap.shape[1])
        rz = np.full(len(X), -1e9)
        rz[inb] = self.rmap[I[inb], J[inb]]
        ok &= rz + self.cfg.jump >= zt
        n = 0
        for i in np.nonzero(ok)[0]:
            h = self.encl.ray_cast(Vector((float(X[i]), float(Y[i]), float(zt[i]) + 0.05)), Vector((0, 0, -1)),
                                   self.cfg.air_d + 0.05)
            if h[0] is None:
                n += 1
                if rec is not None:
                    rec.append(("ar",) + (round(float(X[i]), 1), round(float(Y[i]), 1), round(float(zt[i]), 2)))
                if n >= limit:
                    break
        return n

    def keepout_hit(self, HV):
        if not self.keepout:
            return None
        W = self.cfg.world
        if W is not None:
            M = np.array(W)
            P = HV @ M[:3, :3].T + M[:3, 3]
        else:
            P = HV
        lo, hi = P.min(axis=0), P.max(axis=0)
        for poly, zlo, zhi, name in self.keepout:
            if hi[2] < zlo or lo[2] > zhi:
                continue
            if _rect_poly_overlap(lo[:2], hi[:2], poly):
                if float(np.linalg.norm(hi[:2] - lo[:2])) < self.cfg.keepout_small:
                    continue                  # peca pequena (poste, banco): a caixa ja e a propria peca, partir nao ajuda
                return name
        return None


def _rect_poly_overlap(lo, hi, poly):
    """AABB 2D x poligono CONVEXO (SAT)"""
    R = np.array([(lo[0], lo[1]), (hi[0], lo[1]), (hi[0], hi[1]), (lo[0], hi[1])])
    Pp = np.asarray(poly)
    axes = [np.array((1.0, 0.0)), np.array((0.0, 1.0))]
    for i in range(len(Pp)):
        e = Pp[(i + 1) % len(Pp)] - Pp[i]
        axes.append(np.array((-e[1], e[0])))
    for a in axes:
        r = R @ a
        p = Pp @ a
        if r.max() < p.min() - 1e-6 or p.max() < r.min() - 1e-6:
            return False
    return True


# ------------------------------------------------------------------ particao de um grupo
class _Elem:
    __slots__ = ("faces", "HV", "c", "a", "lo", "hi")


def _mk_elem(ob, faces):
    e = _Elem()
    e.faces = faces
    vid = ob.vids(faces)
    P = ob.V[vid]
    e.HV, _ = hull_verts(P) if len(P) > 8 else (P, None)
    e.lo, e.hi = P.min(axis=0), P.max(axis=0)
    e.c = (e.lo + e.hi) / 2
    e.a = max(1e-3, float(np.prod(np.maximum(e.hi - e.lo, 0.1))))
    return e


def _hull_of(elems):
    P = np.concatenate([e.HV for e in elems])
    return hull_verts(P)


def _too_big(cfg, HV):
    ext = HV.max(axis=0) - HV.min(axis=0)
    return max(ext[0], ext[1]) > cfg.max_xy


def _bisect(elems):
    C = np.array([e.c for e in elems])
    W = np.array([e.a for e in elems])
    m = (C * W[:, None]).sum(axis=0) / W.sum()
    X = C - m
    cov = (X * W[:, None]).T @ X
    w, v = np.linalg.eigh(cov)
    ax = v[:, -1]
    pr = C @ ax
    order = np.argsort(pr)
    ps = pr[order]
    n = len(ps)
    lo, hi = int(n * 0.2), max(int(n * 0.8), int(n * 0.2) + 1)
    gaps = ps[1:] - ps[:-1]
    k = None
    if hi - lo >= 1:
        seg = gaps[max(0, lo - 1):min(len(gaps), hi)]
        if len(seg):
            j = int(np.argmax(seg))
            if seg[j] > 0.5:
                k = max(0, lo - 1) + j + 1
    if k is None:
        k = n // 2
    k = min(max(k, 1), n - 1)
    A = [elems[i] for i in order[:k]]
    B = [elems[i] for i in order[k:]]
    return A, B


def _split_faces(ob, e):
    """peca unica concava: parte as faces pela mediana do eixo de maior extensao"""
    if len(e.faces) < 4:
        return None
    C = ob.centroids(e.faces)
    ext = C.max(axis=0) - C.min(axis=0)
    ax = int(np.argmax(ext))
    if ext[ax] < 0.3:
        return None
    med = np.median(C[:, ax])
    m = C[:, ax] <= med
    if m.all() or not m.any():
        m = C[:, ax] < med
        if m.all() or not m.any():
            return None
    return _mk_elem(ob, e.faces[m]), _mk_elem(ob, e.faces[~m])


def _solve(ctx, ob, elems, depth, out, warn):
    HV, planes = _hull_of(elems)
    why = None
    if _too_big(ctx.cfg, HV):
        why = "grande"
    elif ctx.keepout_hit(HV) is not None:
        why = "keepout"
    else:
        rec = [] if (ctx.cfg.debug and depth <= 1) else None
        if ctx.steals(HV, planes, ctx.cfg.steal_n, rec) >= ctx.cfg.steal_n:
            why = "rouba"
            if rec is not None:
                ctx.debug.append((ob.o.name, depth, len(elems), tuple(np.round(HV.min(axis=0), 1)),
                                  tuple(np.round(HV.max(axis=0), 1)), rec))
    ctx.why[why] = ctx.why.get(why, 0) + 1
    ok = why is None
    if ok:
        out.append((elems, HV, planes, "H"))
        return
    if depth >= ctx.cfg.max_depth:
        warn.append(("profundidade", ob.o.name, tuple(np.round(HV.mean(axis=0), 1))))
        out.append((elems, HV, planes, "P"))
        return
    if len(elems) == 1:
        sp = _split_faces(ob, elems[0])
        if sp is None:
            warn.append(("peca_concava", ob.o.name, tuple(np.round(HV.mean(axis=0), 1))))
            out.append((elems, HV, planes, "P"))      # concava e indivisivel: decomposicao precisa do Roblox
            return
        _solve(ctx, ob, [sp[0]], depth + 1, out, warn)
        _solve(ctx, ob, [sp[1]], depth + 1, out, warn)
        return
    A, B = _bisect(elems)
    _solve(ctx, ob, A, depth + 1, out, warn)
    _solve(ctx, ob, B, depth + 1, out, warn)


def _touch_groups(elems, tol=0.1):
    n = len(elems)
    par = list(range(n))

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    lo = np.array([e.lo for e in elems]) - tol
    hi = np.array([e.hi for e in elems]) + tol
    order = np.argsort(lo[:, 0])
    active = []
    for i in order:
        x = lo[i, 0]
        active = [j for j in active if hi[j, 0] >= x]
        for j in active:
            if np.all(lo[i] <= hi[j]) and np.all(lo[j] <= hi[i]):
                a, b = find(i), find(j)
                if a != b:
                    par[a] = b
        active.append(i)
    g = {}
    for i in range(n):
        g.setdefault(find(i), []).append(elems[i])
    return list(g.values())


def _remerge(ctx, ob, clusters, max_tries=10):
    """junta agrupamentos vizinhos quando o fecho da uniao continua justo (so Hull com Hull)"""
    keep = [c for c in clusters if c[3] != "H"]
    cl = [list(c) for c in clusters if c[3] == "H"]
    changed = True
    while changed and len(cl) > 1:
        changed = False
        bb = [(c[1].min(axis=0), c[1].max(axis=0)) for c in cl]
        order = sorted(range(len(cl)), key=lambda i: float(np.prod(np.maximum(bb[i][1] - bb[i][0], 0.1))))
        dead = set()
        for i in order:
            if i in dead:
                continue
            ci = (bb[i][0] + bb[i][1]) / 2
            cands = []
            for j in range(len(cl)):
                if j == i or j in dead:
                    continue
                if np.all(bb[i][0] - 0.6 <= bb[j][1]) and np.all(bb[j][0] - 0.6 <= bb[i][1]):
                    cands.append((float(np.linalg.norm((bb[j][0] + bb[j][1]) / 2 - ci)), j))
            cands.sort()
            for _, j in cands[:max_tries]:
                els = cl[i][0] + cl[j][0]
                HV, planes = _hull_of(els)
                if _too_big(ctx.cfg, HV) or ctx.keepout_hit(HV) is not None or                         ctx.steals(HV, planes, ctx.cfg.steal_n) >= ctx.cfg.steal_n:
                    continue
                cl[j] = [els, HV, planes, "H", cl[j][4] + cl[i][4]]
                bb[j] = (HV.min(axis=0), HV.max(axis=0))
                dead.add(i)
                changed = True
                break
        cl = [c for k, c in enumerate(cl) if k not in dead]
    return [tuple(c) for c in cl] + keep


# ------------------------------------------------------------------ portadores e emissao
def _carriers(cfg, ob, faces, diag=1e9):
    """materiais que viram MeshPart colidivel no agrupamento (por area; pula quem ja esta dentro dos fechos)"""
    cover = cfg.small_cover if diag < cfg.small else cfg.cover
    by = {}
    for f in faces:
        by.setdefault(ob.fmat[f], []).append(f)
    items = sorted(((ob.area(fs), m, np.array(fs, np.int32)) for m, fs in by.items()), key=lambda t: -t[0])
    chosen = []
    for a, m, fs in items:
        P = ob.V[ob.vids(fs)]
        if chosen:
            ins = np.zeros(len(P), bool)
            for _, _, pl in chosen:
                if pl is not None:
                    ins |= inside(pl, P, margin=-cfg.cover_m)
            if ins.mean() >= cover:
                continue
        HV, pl = hull_verts(P)
        if pl is None:
            continue                          # material PLANO neste agrupamento: sem fecho no Roblox (cairia para Box =
                                              # AABB de mundo enorme) -> fica so visual
        chosen.append((m, fs, pl))
    return [(m, fs) for m, fs, pl in chosen]


def _emit(ob, name, faces):
    """objeto novo com as faces dadas do objeto original (coordenadas de mundo, matriz identidade)"""
    src = ob.o
    me = src.data
    vid = ob.vids(faces)
    remap = {int(v): k for k, v in enumerate(vid)}
    bm = bmesh.new()
    bv = [bm.verts.new(tuple(p)) for p in ob.V[vid]]
    uv_src = me.uv_layers.get("UVMap") or me.uv_layers.active
    uvl = bm.loops.layers.uv.new("UVMap") if uv_src else None
    uvd = None
    if uv_src:
        uvd = np.empty(len(me.loops) * 2)
        uv_src.data.foreach_get("uv", uvd)
        uvd = uvd.reshape(-1, 2)
    sm = np.zeros(len(me.polygons), bool)
    me.polygons.foreach_get("use_smooth", sm)
    mats = []
    midx = {}
    for f in faces:
        vs = [bv[remap[int(v)]] for v in ob.fverts(f)]
        try:
            nf = bm.faces.new(vs)
        except ValueError:
            continue
        m = int(ob.mi[f])
        if m not in midx:
            midx[m] = len(mats)
            mats.append(m)
        nf.material_index = midx[m]
        nf.smooth = bool(sm[f])
        if uvl is not None:
            s = ob.ls[f]
            for k, lp in enumerate(nf.loops):
                lp[uvl].uv = tuple(uvd[s + k])
    nm = bpy.data.meshes.new(name)
    bm.to_mesh(nm)
    bm.free()
    for m in mats:
        nm.materials.append(me.materials[m] if m < len(me.materials) else None)
    o = bpy.data.objects.new(name, nm)
    for c in src.users_collection:
        c.objects.link(o)
    return o


def _remove_faces(o, faces):
    if not len(faces):
        return
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    kill = [bm.faces[int(i)] for i in faces]
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(o.data)
    bm.free()


def _cut_long_faces(o, cfg):
    """corta (sem mudar o que se ve: corte coplanar, UV interpolada) as faces de material solido mais longas que
    cfg.cut_len em planos x/y = k * cut_len/2 do referencial de projeto: assim toda peca concava pode ser partida e
    nenhuma peca reta longa fica com AABB de mundo enorme. Devolve o numero de faces novas."""
    me = o.data
    mats = [(s.name if s else "") for s in me.materials]
    bm = bmesh.new()
    bm.from_mesh(me)
    mw = o.matrix_world
    bm.transform(mw)
    L2 = cfg.cut_len * cfg.cut_len
    n0 = len(bm.faces)

    def longs():
        out = []
        for f in bm.faces:
            m = mats[f.material_index] if f.material_index < len(mats) else ""
            if _is_nocol_mat(cfg, m) and not m.startswith(cfg.roof_cond):
                continue
            if any((e.verts[0].co - e.verts[1].co).length_squared > L2 for e in f.edges):
                out.append(f)
        return out
    fs = longs()
    if not fs:
        bm.free()
        return 0
    step = cfg.cut_len / 2.0

    def is_long(f):
        m = mats[f.material_index] if f.material_index < len(mats) else ""
        if _is_nocol_mat(cfg, m) and not m.startswith(cfg.roof_cond):
            return False
        return any((e.verts[0].co - e.verts[1].co).length_squared > L2 for e in f.edges)
    for ax in (0, 1):
        cand = set(longs())
        if not cand:
            break
        vs = {v for f in cand for v in f.verts}
        lo = min(v.co[ax] for v in vs)
        hi = max(v.co[ax] for v in vs)
        no = Vector((1.0, 0.0, 0.0)) if ax == 0 else Vector((0.0, 1.0, 0.0))
        for k in range(int(math.floor(lo / step)) + 1, int(math.ceil(hi / step))):
            c = k * step
            cut = [f for f in cand if f.is_valid and min(v.co[ax] for v in f.verts) < c - 1e-3 and
                   max(v.co[ax] for v in f.verts) > c + 1e-3]
            if not cut:
                continue
            geom = list({e for f in cut for e in f.edges}) + cut + list({v for f in cut for v in f.verts})
            co = Vector((0.0, 0.0, 0.0))
            co[ax] = c
            res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=co, plane_no=no)
            newf = [g for g in res["geom"] if isinstance(g, bmesh.types.BMFace)]
            cand = {f for f in cand if f.is_valid} | {f for f in newf if f.is_valid and is_long(f)}
    n1 = len(bm.faces)
    bm.transform(mw.inverted())
    bm.to_mesh(me)
    bm.free()
    return n1 - n0


def _parts_info(ob, pf):
    vid = ob.vids(pf)
    P = ob.V[vid]
    return P, P.min(axis=0), P.max(axis=0)


def _in_zone(cfg, c):
    for poly, zlo, zhi in cfg.nocol_zones:
        if zlo <= c[2] <= zhi:
            xs = [p[0] for p in poly]
            ys = [p[1] for p in poly]
            if min(xs) <= c[0] <= max(xs) and min(ys) <= c[1] <= max(ys):
                return True
    return False


def _trunk_faces(cfg, ob, pf, floor_bvh):
    """arvore/tronco: so o que fica ate trunk_h acima do chao embaixo colide (sem escalar copa/arco)"""
    rule = None
    for pre, mpre, h in cfg.trunk:
        if ob.o.name.startswith(pre) and ob.fmat[int(pf[0])].startswith(mpre):
            rule = h
            break
    if rule is None:
        return pf
    if rule <= 0:
        return pf[:0]
    C = ob.centroids(pf)
    keep = np.zeros(len(pf), bool)
    for k, c in enumerate(C):
        g = floor_bvh.ray_cast(Vector((c[0], c[1], c[2] + 0.1)), Vector((0, 0, -1)), 200.0) if floor_bvh else (None,)
        gz = g[0].z if g[0] is not None else -1e9
        keep[k] = c[2] - gz <= rule
    return pf[keep]


def split(cfg, log=print):
    """passo 2 do motor (ver cabecalho). Muda a cena (export/QA: sem salvar). Devolve o relatorio."""
    t0 = time.time()
    bpy.context.view_layer.update()
    ncut = 0
    for o in _visual_objects(cfg):
        if _collidable_obj(cfg, o) and cfg.cut_len > 0:
            ncut += _cut_long_faces(o, cfg)
    objs = [_Obj(o, cfg) for o in _visual_objects(cfg)]
    cobjs = [ob for ob in objs if _collidable_obj(cfg, ob.o)]
    floor_v, floor_p = _col_boxes(cfg.floor_col)
    floor_bvh = BVHTree.FromPolygons(floor_v, floor_p) if floor_p else None
    # a) pecas de cada objeto colidivel (so faces de material solido), sem a pele fina assentada no chao, sem o que fica
    #    na zona sem colisao (praca de mineracao) e, em arvore, so o tronco baixo
    work = []
    nskin = nzone = ntrunk = 0
    for ob in cobjs:
        fs = np.nonzero(ob.fcol)[0].astype(np.int32)
        if not len(fs):
            work.append((ob, []))
            continue
        if cfg.nocol_zones:
            inz = np.array([any(_in_zone(cfg, ob.V[v]) for v in ob.fverts(f)) for f in fs], bool)
            nzone += int(inz.sum())
            fs = fs[~inz]
            if not len(fs):
                work.append((ob, []))
                continue
        keep = []
        for pf in ob.parts(fs):
            P, lo, hi = _parts_info(ob, pf)
            c = (lo + hi) / 2
            if hi[2] - lo[2] <= cfg.skin_h and floor_bvh is not None:
                h = floor_bvh.ray_cast(Vector((c[0], c[1], hi[2] + 0.6)), Vector((0, 0, -1)), 2.0)
                if h[0] is not None and abs(h[0].z - hi[2]) <= cfg.skin_d:
                    nskin += 1
                    continue
            if cfg.trunk:
                pt = _trunk_faces(cfg, ob, pf, floor_bvh)
                if len(pt) < len(pf):
                    ntrunk += 1
                if not len(pt):
                    continue
                if len(pt) < len(pf):
                    keep += ob.parts(pt)
                    continue
            keep.append(pf)
        work.append((ob, keep))
    # b) BVH de fechamento: TODO o visual (menos folhagem e pele) dos objetos colidiveis + chao. Janela/shoji/pano
    #    fecham o comodo: casa fechada pode ser cheia pelo fecho (quem atravessaria a janela bate no fecho)
    ev, ep = [], []
    kept_of = {id(ob): (np.concatenate(k) if k else np.zeros(0, np.int32)) for ob, k in work}
    for ob in cobjs:
        if not ob.npoly:
            continue
        fm = np.array([not ob.fmat[f].startswith(cfg.foliage) for f in range(ob.npoly)], bool)
        dropped = np.setdiff1d(np.nonzero(ob.fcol)[0], kept_of.get(id(ob), np.zeros(0, np.int32)))
        if len(dropped):
            fm[dropped] = False
        if not fm.any():
            continue
        fs = np.nonzero(fm)[0]
        vid = ob.vids(fs)
        remap = np.full(len(ob.V), -1, np.int64)
        remap[vid] = np.arange(len(vid)) + len(ev)
        ev.extend(map(tuple, ob.V[vid]))
        ep.extend([int(remap[v]) for v in ob.fverts(f)] for f in fs)
    base = len(ev)
    ev += floor_v
    ep += [[base + i for i in p] for p in floor_p]
    encl = BVHTree.FromPolygons(ev, ep)
    t1 = time.time()
    # c) pontos livres + ALCANCE
    P, Q = free_points(cfg, cobjs, floor_bvh)
    R = reach(cfg, P, encl)
    PR = P[R]
    # d) telhado ao ALCANCE colide (Hull): pular nele ou cair nele de um patamar = tem de segurar. O resto do telhado
    #    nao colide (beiral alto por projeto: ninguem chega; a camera nao 'pula' no beiral)
    nroof = nroof_ok = 0
    if cfg.roof_cond and len(PR):
        order = np.argsort(PR[:, 0])
        PS = PR[order]
        PX = PS[:, 0]
        for k, (ob, keep) in enumerate(work):
            rf = np.array([f for f in range(ob.npoly) if ob.fmat[f].startswith(cfg.roof_cond)], np.int32)
            if not len(rf):
                continue
            add = []
            for pf in ob.parts(rf):
                nroof += 1
                Pp, lo, hi = _parts_info(ob, pf)
                m = cfg.roof_reach_xy
                i0 = np.searchsorted(PX, lo[0] - m)
                i1 = np.searchsorted(PX, hi[0] + m, side="right")
                S = PS[i0:i1]
                if not len(S):
                    continue
                sel = (S[:, 1] >= lo[1] - m) & (S[:, 1] <= hi[1] + m) & (S[:, 2] + cfg.jump + 0.5 >= lo[2])
                if sel.any():
                    add.append(pf)
                    nroof_ok += 1
            if add:
                work[k] = (ob, keep + add)
    # e) BVH 'solido' = face de material solido que colide + solidos de chao (perto / comodo fechado)
    sv, sp = [], []
    for ob, k in work:
        if not k:
            continue
        fs = np.concatenate(k)
        vid = ob.vids(fs)
        remap = np.full(len(ob.V), -1, np.int64)
        remap[vid] = np.arange(len(vid)) + len(sv)
        sv.extend(map(tuple, ob.V[vid]))
        sp.extend([int(remap[v]) for v in ob.fverts(f)] for f in fs)
    base = len(sv)
    sv += floor_v
    sp += [[base + i for i in p] for p in floor_p]
    solid = BVHTree.FromPolygons(sv, sp)
    Q = np.concatenate([PR + np.array((0.0, 0.0, hh)) for hh in cfg.heights]) if len(PR) else PR
    kw = []
    W = cfg.world
    for poly, zlo, zhi, name in cfg.keepout:
        if W is not None:
            pw = [tuple((W @ Vector((x, y, 0.0)))[:2]) for x, y in poly]
            zl = (W @ Vector((poly[0][0], poly[0][1], zlo))).z
            zh = (W @ Vector((poly[0][0], poly[0][1], zhi))).z
        else:
            pw, zl, zh = list(poly), zlo, zhi
        kw.append((pw, zl, zh, name))
    t2 = time.time()
    ctx = _Ctx(cfg, Q, solid, kw, encl)
    ctx.set_reach(PR, cfg.grid)
    # corredores das ROTAS (contrato de jogo): os pontos alcancados a <= corridor_r da linha de cada rota, nas alturas do
    # andador do QA, nao podem ficar dentro de fecho nenhum
    if cfg.corridors and floor_bvh is not None:
        # o andador do QA segue o CHAO de colisao (degrau <= 2,3): o corredor tambem (independe do alcance do BFS)
        H = []
        for pts, z0 in cfg.corridors:
            z = z0
            for a, b in zip(pts, pts[1:]):
                dx, dy = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dy)
                if ln < 1e-6:
                    continue
                ux, uy = dx / ln, dy / ln
                for k in range(int(ln / 0.75) + 1):
                    x, y = a[0] + ux * k * 0.75, a[1] + uy * k * 0.75
                    h = floor_bvh.ray_cast(Vector((x, y, z + 2.5)), Vector((0, 0, -1)), 60.0)
                    if h[0] is None:
                        continue
                    z = h[0].z
                    for hh in cfg.corridor_h:              # linha do andador; o raio do corpo vai no teste
                        H.append((x, y, z + hh))
        for poly, zlo, zhi in cfg.nocol_zones:          # zona sem colisao: nenhum FECHO entra (quina de curva/L)
            xs_ = [p[0] for p in poly]
            ys_ = [p[1] for p in poly]
            for x in np.arange(min(xs_) + 0.5, max(xs_), 3.0):
                for y in np.arange(min(ys_) + 0.5, max(ys_), 3.0):
                    for z in np.arange(zlo + 1.6, zhi, 3.0):
                        H.append((float(x), float(y), float(z)))
        if H:
            ctx.set_hard(np.unique(np.round(np.array(H), 2), axis=0))
    rep = dict(objetos=0, pecas_pele=nskin, pecas_zona=nzone, troncos_cortados=ntrunk, faces_cortadas=ncut,
               telhados=nroof, telhados_alcancaveis=nroof_ok, agrupamentos=0, portadores=0, faces_movidas=0, avisos=[],
               por_objeto={}, pontos_livres=int(len(P)), alcancados=int(R.sum()), pequenos=0)
    emitted = []
    for ob, parts in work:
        if not parts:
            continue
        oname = ob.o.name
        elems = [_mk_elem(ob, pf) for pf in parts]
        groups = _touch_groups(elems)
        clusters = []
        warn = []
        n_solved = 0
        for g in groups:
            out = []
            _solve(ctx, ob, g, 0, out, warn)
            n_solved += len(out)
            single = len(out) == 1                    # grupo inteiro aceito de primeira (prop isolado?)
            clusters += [tuple(c) + (1 if single else 0,) for c in out]
        if len(clusters) > 1:
            clusters = _remerge(ctx, ob, clusters)
        rep["avisos"] += warn
        n_emit = 0
        moved = []
        k = 0
        for els, HV, planes, fid, single in clusters:
            ext = HV.max(axis=0) - HV.min(axis=0)
            dg = float(np.linalg.norm(ext))
            if dg < cfg.min_diag or (single == 1 and dg < cfg.prop_diag and ext[2] < cfg.prop_h):
                rep["pequenos"] += 1                  # prop pequeno isolado (balde, caixote, saco): nao colide
                continue
            if fid == "P" and dg < cfg.leaf_drop:
                rep["folhas_soltas"] = rep.get("folhas_soltas", 0) + 1
                continue                              # pedacinho concavo que rouba/fica no ar: so visual
            faces = np.concatenate([e.faces for e in els])
            k += 1
            for j, (m, fs) in enumerate(_carriers(cfg, ob, faces, dg)):
                name = "%s_k%d_%d" % (oname, k, j)
                o = _emit(ob, name, fs)
                o["colv3"] = fid
                o["colv3_src"] = oname
                o["colv3_k"] = k
                emitted.append(o)
                moved.append(fs)
                n_emit += 1
        if moved:
            mv = np.concatenate(moved)
            _remove_faces(ob.o, mv)
            rep["faces_movidas"] += int(len(mv))
            if len(ob.o.data.polygons) == 0:
                me = ob.o.data
                bpy.data.objects.remove(ob.o, do_unlink=True)
                bpy.data.meshes.remove(me)
        rep["objetos"] += 1
        rep["agrupamentos"] += k
        rep["portadores"] += n_emit
        rep["por_objeto"][oname] = (len(parts), len(groups), n_solved, k, n_emit)
        if cfg.verbose:
            log("COLV3 %-26s pecas %5d grupos %4d particao %4d -> agrupamentos %4d, MeshParts colidiveis %4d" % (
                oname, len(parts), len(groups), n_solved, k, n_emit))
    bpy.context.view_layer.update()
    rep["tempo"] = dict(pecas=round(t1 - t0, 1), pontos=round(t2 - t1, 1), particao=round(time.time() - t2, 1),
                        testes=ctx.tests, t_testes=round(ctx.t, 1), motivos=dict((str(k), v) for k, v in ctx.why.items()))
    rep["emitidos"] = [o.name for o in emitted]
    rep["debug"] = ctx.debug
    rep["_P"], rep["_R"], rep["_encl"] = P, R, encl  # (diagnostico: superficies amostradas, alcance, fechamento)
    return rep


# ------------------------------------------------------------------ 3) a colisao como o Roblox faz (para o QA)
def meshes(cfg):
    """[(nome, verts, faces, tipo)] da colisao: caixas COL_ (tipo 'box') + fecho de cada peca colv3 ('hull'/'box')"""
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        if o.name.startswith("COL_"):
            mw = o.matrix_world
            out.append((o.name, [tuple(mw @ v.co) for v in o.data.vertices], [list(p.vertices) for p in o.data.polygons],
                        "box"))
            continue
        c = o.get("colv3")
        if not c:
            continue
        mw = o.matrix_world
        M = np.array(mw)
        n = len(o.data.vertices)
        co = np.empty(n * 3)
        o.data.vertices.foreach_get("co", co)
        P = co.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]
        if c == "B":
            out.append((o.name,) + _world_aabb_mesh(cfg, P) + ("box",))
            continue
        bm = bmesh.new()
        for p in P:
            bm.verts.new(p)
        try:
            bmesh.ops.convex_hull(bm, input=bm.verts[:], use_existing_faces=False)
        except Exception:
            pass
        faces = [f for f in bm.faces]
        if len(faces) < 4:
            bm.free()
            out.append((o.name,) + _world_aabb_mesh(cfg, P) + ("flat",))
            continue
        bm.verts.index_update()
        vs = [tuple(v.co) for v in bm.verts]
        fs = [[v.index for v in f.verts] for f in faces]
        bm.free()
        out.append((o.name, vs, fs, "hull"))
    return out


def _world_aabb_mesh(cfg, P):
    W = cfg.world
    if W is not None:
        M = np.array(W)
        Pw = P @ M[:3, :3].T + M[:3, 3]
        Mi = np.linalg.inv(M)
    else:
        Pw, Mi = P, np.eye(4)
    lo, hi = Pw.min(axis=0), Pw.max(axis=0)
    lo = np.minimum(lo, hi - 0.05)
    C = np.array([(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    C = C @ Mi[:3, :3].T + Mi[:3, 3]
    F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return [tuple(c) for c in C], F


def ref_table():
    """referencia do Blender para a auditoria no Studio: por objeto colv3 (ja no MUNDO), a cobertura da planta da AABB
    de mundo pelo fecho (grade 6 x 6, raio para baixo) e o volume do fecho. A auditoria_colisao.lua mede a mesma
    cobertura na colisao REAL do Roblox: se der muito maior, o Roblox nao fez o fecho esperado."""
    rows = []
    for o in bpy.data.objects:
        c = o.get("colv3")
        if not c:
            continue
        mw = o.matrix_world
        P = np.array([tuple(mw @ v.co) for v in o.data.vertices])
        if len(P) < 4:
            continue
        HV, planes = hull_verts(P)
        bm = bmesh.new()
        for p in HV:
            bm.verts.new(p)
        try:
            bmesh.ops.convex_hull(bm, input=bm.verts[:], use_existing_faces=False)
        except Exception:
            pass
        vol = 0.0
        try:
            vol = abs(bm.calc_volume())
        except Exception:
            pass
        bm.verts.ensure_lookup_table()
        vs = [tuple(v.co) for v in bm.verts]
        fs = [[v.index for v in f.verts] for f in bm.faces]
        bm.free()
        if len(fs) < 4:
            continue
        B = BVHTree.FromPolygons(vs, fs)
        lo, hi = P.min(axis=0), P.max(axis=0)
        n = hit = 0
        for a in range(6):
            for b in range(6):
                x = lo[0] + (a + 0.5) / 6 * (hi[0] - lo[0])
                y = lo[1] + (b + 0.5) / 6 * (hi[1] - lo[1])
                h = B.ray_cast(Vector((x, y, hi[2] + 1.0)), Vector((0, 0, -1)), hi[2] - lo[2] + 2.0)
                n += 1
                hit += h[0] is not None
        rows.append((o.name, round(hit / n, 2), round(vol, 1)))
    s = ["local COLV3_REF = {  -- objeto -> {cobertura da planta da AABB pelo fecho (0..1), volume do fecho}"]
    for nm, cov, vol in rows:
        s.append("  ['%s']={%s,%s}," % (nm, cov, vol))
    s.append("}")
    return chr(10).join(s)


# ------------------------------------------------------------------ Lua (montar): aplica a colisao nas MeshParts
LUA = r"""
-- COLISAO V3 (colv3.py): o que se ve e o que colide. MeshPart com letra de colisao nas flags (H Hull, B Box, D Default,
-- P PreciseConvexDecomposition) colide pela propria forma (CanCollide/CanQuery: o Popper da camera tambem para nela);
-- o resto do visual nao colide e nao bloqueia a camera. As COL_ que sobram (chao, jogabilidade, guardas documentadas)
-- NAO tem tag CamOccluder. A CollisionFidelity so muda no modo de edicao (Command Bar/plugin): por isso fica aqui.
do
  local FIDV3 = {H = Enum.CollisionFidelity.Hull, B = Enum.CollisionFidelity.Box, D = Enum.CollisionFidelity.Default,
    P = Enum.CollisionFidelity.PreciseConvexDecomposition}
  local nV3, nVis, nFail = {H = 0, B = 0, D = 0, P = 0}, 0, 0
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA('MeshPart') then
      local e = MESH[d.Name]
      local c = e and string.match(e[10] or '', '[HBDP]') or nil
      if c then
        d.CanCollide = true; d.CanQuery = true; d.CanTouch = false; d.CollisionGroup = 'Default'
        local ok = pcall(function() d.CollisionFidelity = FIDV3[c] end)
        if not ok then nFail += 1 end
        d:SetAttribute('colv3', c); nV3[c] += 1
        local r = COLV3_REF and COLV3_REF[string.match(d.Name, '^(.-)__') or '']
        if r then d:SetAttribute('colv3_cov', r[1]); d:SetAttribute('colv3_vh', r[2]) end
      else
        d.CanCollide = false; d.CanQuery = false; d.CanTouch = false
        d:SetAttribute('colv3', nil); nVis += 1
      end
    end
  end
  for _, p in ipairs(COLF:GetChildren()) do pcall(function() CS:RemoveTag(p, 'CamOccluder') end) end
  print(string.format('COLISAO V3: %d MeshParts colidem (Hull %d, Box %d, Default %d, Precise %d; %d fidelidade recusada), %d so visuais, %d COL_ invisiveis', nV3.H + nV3.B + nV3.D + nV3.P, nV3.H, nV3.B, nV3.D, nV3.P, nFail, nVis, #COLF:GetChildren()))
end
"""
