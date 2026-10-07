# db_terrain_field - campos de distancia (numpy) e malha de superficie por "marching squares" para o terreno da
# Ilha 2 (dono: zona terrain). O chao e montado numa grade retilinea NAO uniforme: as linhas passam pelos cantos
# duros da planta (praca, recorte da escadaria, vertices dos terracos, lotes) e o contorno de cada regiao sai da
# interpolacao linear da distancia assinada (curvas lisas, cantos exatos, sem serrilhado de grade).
# Regioes que dividem uma borda (areia x terra x calcada) usam o MESMO campo com sinal trocado: as bordas saem
# identicas e soldadas (Surf com cache compartilhado).
import math
import numpy as np
import bmesh


# ------------------------------------------------------------------ grade
def grid_lines(lo, hi, step, req=(), merge=0.45, clear=0.4):
    """linhas da grade: passo regular + linhas obrigatorias (cantos duros). Linhas regulares a menos de clear*step
    de uma obrigatoria saem; obrigatorias a menos de 'merge' entre si viram uma so."""
    rq = []
    for v in sorted(set(round(float(v), 4) for v in req if lo <= v <= hi)):
        if rq and v - rq[-1] < merge:
            continue
        rq.append(v)
    base = []
    n = int(math.floor((hi - lo) / step)) + 1
    for k in range(n + 1):
        v = lo + k * step
        if v > hi + 1e-9:
            break
        if all(abs(v - r) > clear * step for r in rq):
            base.append(v)
    return np.array(sorted(base + rq), dtype=float)


# ------------------------------------------------------------------ distancias assinadas (negativo = dentro)
def _segs(pts, closed):
    n = len(pts)
    m = n if closed else n - 1
    return [(pts[i][0], pts[i][1], pts[(i + 1) % n][0], pts[(i + 1) % n][1]) for i in range(m)]


def dist_segments(X, Y, segs):
    d2 = np.full(np.shape(X), np.inf)
    for ax, ay, bx, by in segs:
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy
        if l2 < 1e-12:
            ex, ey = X - ax, Y - ay
        else:
            t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0)
            ex, ey = X - (ax + dx * t), Y - (ay + dy * t)
        d2 = np.minimum(d2, ex * ex + ey * ey)
    return np.sqrt(d2)


def inside_poly(X, Y, poly):
    ins = np.zeros(np.shape(X), dtype=bool)
    n = len(poly)
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[i - 1]
        if yi == yj:
            continue
        cond = (yi > Y) != (yj > Y)
        xc = (xj - xi) * (Y - yi) / (yj - yi) + xi
        ins ^= cond & (X < xc)
    return ins


def sd_poly(X, Y, poly):
    d = dist_segments(X, Y, _segs(poly, True))
    return np.where(inside_poly(X, Y, poly), -d, d)


def sd_disc(X, Y, cx, cy, r):
    return np.hypot(X - cx, Y - cy) - r


def sd_ribbon(X, Y, pts, hw):
    return dist_segments(X, Y, _segs(pts, False)) - hw


def sd_rect(X, Y, x0, y0, x1, y1):
    cx, cy = (x0 + x1) * 0.5, (y0 + y1) * 0.5
    hx, hy = abs(x1 - x0) * 0.5, abs(y1 - y0) * 0.5
    qx = np.abs(X - cx) - hx
    qy = np.abs(Y - cy) - hy
    return np.hypot(np.maximum(qx, 0.0), np.maximum(qy, 0.0)) + np.minimum(np.maximum(qx, qy), 0.0)


def sd_polar(X, Y, rfn, off=0.0, step=0.5):
    """r - (rfn(ang) + off): contorno polar em volta da origem (bacia/promenade)"""
    angs = np.arange(0.0, 360.0 + step, step)
    vals = np.array([rfn(a) for a in angs]) + off
    A = np.degrees(np.arctan2(Y, X)) % 360.0
    return np.hypot(X, Y) - np.interp(A, angs, vals)


def band(f, lo, hi):
    """faixa lo < f < hi de um campo (negativo dentro da faixa)"""
    return np.maximum(lo - f, f - hi)


# ------------------------------------------------------------------ malha
class Surf:
    """superficie por marching squares sobre a grade (xs, ys) com cota por no Z (nx, ny). cache: soldagem entre
    superficies que dividem borda (mesmo Surf). Faces anti-horarias (normal para cima); saias com normal para fora."""

    def __init__(self, mb, xs, ys, Z):
        self.mb = mb
        self.bm = mb.bm
        self.xs = xs
        self.ys = ys
        self.Z = Z
        self.cache = {}
        self.faces = {}          # material -> [faces]
        self.skirts = {}         # material -> [faces]
        self.stats = {"cells": 0, "degen": 0, "dup": 0, "fan": 0, "dropped": 0}

    def _face(self, vs):
        """face da celula; nunca larga a celula: repete com os vertices unicos e cai para leque de triangulos.
        None = a face ja existe (outra regiao do mesmo Surf cobre exatamente a celula)"""
        bm = self.bm
        try:
            return [bm.faces.new(vs)]
        except ValueError:
            pass
        u = []
        for v in vs:
            if v not in u:
                u.append(v)
        if len(u) < 3:
            self.stats["degen"] += 1
            return None
        if bm.faces.get(u) is not None:
            self.stats["dup"] += 1
            return None
        try:
            return [bm.faces.new(u)]
        except ValueError:
            pass
        out = []
        for k in range(1, len(u) - 1):
            tri = (u[0], u[k], u[k + 1])
            if bm.faces.get(tri) is not None:
                continue
            try:
                out.append(bm.faces.new(tri))
            except ValueError:
                pass
        if out:
            self.stats["fan"] += 1
            return out
        self.stats["dropped"] += 1
        return None

    def _node(self, i, j):
        k = ("n", i, j)
        v = self.cache.get(k)
        if v is None:
            v = self.bm.verts.new((float(self.xs[i]), float(self.ys[j]), float(self.Z[i, j])))
            self.cache[k] = v
        return k, v

    def _cross(self, p, q, fp, fq):
        t = fp / (fp - fq)
        if t < 1e-3:
            return self._node(*p)
        if t > 1.0 - 1e-3:
            return self._node(*q)
        if p > q:
            p, q, t = q, p, 1.0 - t
        k = ("e", p, q, round(t, 6))
        v = self.cache.get(k)
        if v is None:
            x = self.xs[p[0]] + (self.xs[q[0]] - self.xs[p[0]]) * t
            y = self.ys[p[1]] + (self.ys[q[1]] - self.ys[p[1]]) * t
            z = self.Z[p] + (self.Z[q] - self.Z[p]) * t
            v = self.bm.verts.new((float(x), float(y), float(z)))
            self.cache[k] = v
        return k, v

    # ---- divisao de material dentro da regiao (uma camada so, bordas soldadas)
    def _info(self, key, c, splits):
        """(arestas da celula que contem o vertice, valores dos campos de material nele)"""
        if key[0] == "n":
            p = (key[1], key[2])
            k = c.index(p)
            e1 = (min(c[k], c[(k + 1) % 4]), max(c[k], c[(k + 1) % 4]))
            e2 = (min(c[k - 1], c[k]), max(c[k - 1], c[k]))
            return frozenset((e1, e2)), tuple(float(g[p]) for g, _ in splits)
        _, p, q, t = key
        return frozenset(((p, q),)), tuple(float(g[p] + (g[q] - g[p]) * t) for g, _ in splits)

    def _split_vert(self, A, B, idx, s, splits, c):
        """ponto do nivel zero do campo idx no lado A-B do poligono. Num lado sobre aresta da grade, o ponto sai da
        interpolacao dos NOS da aresta (a celula vizinha acha o mesmo vertice); num lado interno, da de A e B"""
        common = A[4] & B[4]
        if common:
            p, q = next(iter(common))
            g = splits[idx][0]
            fp, fq = float(g[p]), float(g[q])
            t = fp / (fp - fq) if abs(fp - fq) > 1e-12 else 0.5
            t = min(1.0, max(0.0, t))
            if t < 1e-3 or t > 1.0 - 1e-3:
                key, v = self._node(*(p if t < 1e-3 else q))
                ed, vals = self._info(key, c, splits)
                return [key, v, 0, None, ed, vals]
            key = ("e", p, q, round(t, 6))
            v = self.cache.get(key)
            if v is None:
                x = self.xs[p[0]] + (self.xs[q[0]] - self.xs[p[0]]) * t
                y = self.ys[p[1]] + (self.ys[q[1]] - self.ys[p[1]]) * t
                z = self.Z[p] + (self.Z[q] - self.Z[p]) * t
                v = self.bm.verts.new((float(x), float(y), float(z)))
                self.cache[key] = v
            vals = tuple(float(gg[p] + (gg[q] - gg[p]) * t) for gg, _ in splits)
            return [key, v, 0, None, frozenset(((p, q),)), vals]
        if s < 1e-3:
            return A
        if s > 1.0 - 1e-3:
            return B
        ka, kb = A[0], B[0]
        if repr(ka) > repr(kb):
            A, B, s = B, A, 1.0 - s
            ka, kb = kb, ka
        key = ("c", ka, kb, round(s, 6))
        v = self.cache.get(key)
        if v is None:
            v = self.bm.verts.new(A[1].co.lerp(B[1].co, s))
            self.cache[key] = v
        vals = tuple(a + (b - a) * s for a, b in zip(A[5], B[5]))
        return [key, v, 0, None, frozenset(), vals]

    @staticmethod
    def _dedupe(poly):
        out = []
        for e in poly:
            if out and out[-1][0] == e[0]:
                continue
            out.append(e)
        while len(out) > 1 and out[0][0] == out[-1][0]:
            out.pop()
        return out

    def _clip(self, poly, idx, splits, c):
        """corta o poligono pelo nivel zero do campo idx: (pecas de dentro, resto de fora). Cada trecho contiguo de
        vertices de dentro vira uma peca PROPRIA (orelha cortada pela corda entre os 2 cruzamentos) e o resto fica
        conectado. Antes o 'dentro' juntava todos os trechos num poligono so: na celula em sela (4 cruzamentos) as
        duas metades se cobriam (faces sobrepostas = z-fight de areia x terra)."""
        n = len(poly)
        ins = [e[5][idx] < 0.0 for e in poly]
        cross = {}
        for k in range(n):
            k2 = (k + 1) % n
            if ins[k] != ins[k2]:
                A, B = poly[k], poly[k2]
                va, vb = A[5][idx], B[5][idx]
                cross[k] = self._split_vert(A, B, idx, va / (va - vb), splits, c)
        out = []
        for k in range(n):
            if not ins[k]:
                out.append(poly[k])
            if k in cross:
                out.append(cross[k])
        pieces = []
        for k0 in range(n):
            if not ins[k0] or ins[k0 - 1]:
                continue
            pc = [cross[(k0 - 1) % n]]
            k = k0
            for _ in range(n):
                pc.append(poly[k])
                if k in cross:
                    pc.append(cross[k])
                    break
                k = (k + 1) % n
            pieces.append(self._dedupe(pc))
        return pieces, self._dedupe(out)

    def build(self, f, mat, cell_mat=None, skirt=None, splits=None):
        """f: campo (nx, ny) - dentro onde f < 0. cell_mat(i, j) -> material da celula (xadrez de lajes).
        skirt(pa, pb, mat) -> (profundidade, material) da saia num trecho de contorno cujos nos de FORA sao pa e pb
        (None = sem saia): distingue a borda da regiao inteira (queda) da divisa entre materiais.
        splits: [(campo, material)] em ordem de prioridade - cada poligono de celula da regiao e cortado pelo nivel
        zero de cada campo (dentro < 0 = aquele material; o resto fica com mat). A regiao sai numa camada so, sem
        fresta entre materiais (antes cada material era uma regiao com campo proprio e os contornos nao batiam)."""
        f = np.where(np.abs(f) < 1e-6, 1e-6, f)
        splits = [(np.where(np.abs(g) < 1e-6, 1e-6, g), m) for g, m in (splits or [])]
        ins = f < 0.0
        cell_any = ins[:-1, :-1] | ins[1:, :-1] | ins[1:, 1:] | ins[:-1, 1:]
        bm = self.bm
        for i, j in np.argwhere(cell_any):
            i = int(i)
            j = int(j)
            c = ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1))
            fv = [float(f[p]) for p in c]
            iv = [v < 0.0 for v in fv]
            poly = []
            for k in range(4):
                if iv[k]:
                    key, v = self._node(*c[k])
                    poly.append([key, v, 0, None])
                k2 = (k + 1) % 4
                if iv[k] != iv[k2]:
                    key, v = self._cross(c[k], c[k2], fv[k], fv[k2])
                    poly.append([key, v, 1 if iv[k] else 2, c[k2] if iv[k] else c[k]])
            out = []
            for e in poly:
                if out and out[-1][0] == e[0]:
                    out[-1][2] |= e[2]
                    out[-1][3] = out[-1][3] or e[3]
                    continue
                out.append(e)
            while len(out) > 1 and out[0][0] == out[-1][0]:
                out[0][2] |= out[-1][2]
                out[0][3] = out[0][3] or out[-1][3]
                out.pop()
            self.stats["cells"] += 1
            if len(out) < 3:
                self.stats["degen"] += 1          # < 3 vertices distintos: lasca de area zero
                continue
            m = cell_mat(i, j) if cell_mat else mat
            if splits:
                rest = []
                for e in out:
                    ed, vals = self._info(e[0], c, splits)
                    rest.append([e[0], e[1], e[2], e[3], ed, vals])
                pieces = []
                for idx in range(len(splits)):
                    if len(rest) < 3:
                        break
                    if all(e[5][idx] >= 0.0 for e in rest):
                        continue
                    if all(e[5][idx] < 0.0 for e in rest):
                        pieces.append((rest, splits[idx][1]))
                        rest = []
                        break
                    inns, rest = self._clip(rest, idx, splits, c)
                    for inn in inns:
                        if len(inn) >= 3:
                            pieces.append((inn, splits[idx][1]))
                if len(rest) >= 3:
                    pieces.append((rest, m))
                for pc, pm in pieces:
                    got = self._face([e[1] for e in pc])
                    if got:
                        self.faces.setdefault(pm, []).extend(got)
            else:
                got = self._face([e[1] for e in out])
                if got is None:
                    continue
                self.faces.setdefault(m, []).extend(got)
            if skirt is None:
                continue
            n = len(out)
            for k in range(n):
                a, b = out[k], out[(k + 1) % n]
                if not ((a[2] & 1) and (b[2] & 2)) or a[3] is None or b[3] is None:
                    continue
                res = skirt(a[3], b[3], m)
                if not res:
                    continue
                d, sm = res
                if d <= 0.0:
                    continue
                d = round(d, 3)
                ka, kb = ("s", a[0], d), ("s", b[0], d)
                va = self.cache.get(ka)
                if va is None:
                    va = bm.verts.new((a[1].co.x, a[1].co.y, a[1].co.z - d))
                    self.cache[ka] = va
                vb = self.cache.get(kb)
                if vb is None:
                    vb = bm.verts.new((b[1].co.x, b[1].co.y, b[1].co.z - d))
                    self.cache[kb] = vb
                try:
                    sf = bm.faces.new((a[1], va, vb, b[1]))
                except ValueError:
                    continue
                self.skirts.setdefault(sm, []).append(sf)
        return self


def assign(mb, faces, mat, rng=None, variant=False):
    """material/tinta/UV de um grupo de faces (sem pegar faces vizinhas como o MB._post faria)"""
    if not faces:
        return
    faces = [f for f in faces if f.is_valid]
    mi = mb._mi_for(mat) if variant else mb._mi(mat)
    t = (rng or mb.rng).uniform(-1.0, 1.0)
    for f in faces:
        f.material_index = mi
        f[mb.tint] = t
        f.smooth = False
        f.normal_update()
    mb._uv(faces, mat)


def flush(mb, surf, rng=None, tag=""):
    st = surf.stats
    print("TERRAIN Surf %s%s celulas=%d largadas=%d (leque=%d, repetidas=%d, lascas=%d)" % (
        mb.name if hasattr(mb, "name") else "?", tag, st["cells"], st["dropped"], st["fan"], st["dup"], st["degen"]))
    for m, fs in surf.faces.items():
        assign(mb, fs, m, rng)
    for m, fs in surf.skirts.items():
        assign(mb, fs, m, rng)


def flat_bed(mb, xs, ys, z, f, mat):
    """leito plano (cota z) da regiao f < 0, fundido em n-gonos: chamar ANTES de qualquer outra geometria do mb
    (o dissolve pega o bmesh inteiro)"""
    bm = mb.bm
    n0 = len(bm.faces)
    s = Surf(mb, xs, ys, np.full((len(xs), len(ys)), float(z))).build(f, mat)
    if n0 == 0:
        bm.normal_update()           # faces.new nao calcula a normal: sem isso o dissolve nao junta nada
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(0.5), verts=list(bm.verts), edges=list(bm.edges))
        # n-gonos concavos grandes: triangula ja aqui (mesma contagem de tris) - o export e a varredura veem o mesmo
        bmesh.ops.triangulate(bm, faces=list(bm.faces), quad_method="BEAUTY", ngon_method="BEAUTY")
        faces = list(bm.faces)
    else:
        faces = [x for fs in s.faces.values() for x in fs]
    print("TERRAIN leito %s z=%.2f celulas=%d largadas=%d faces=%d" % (mb.name, z, s.stats["cells"],
                                                                        s.stats["dropped"], len(faces)))
    assign(mb, faces, mat)
    return faces
