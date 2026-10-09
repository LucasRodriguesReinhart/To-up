# sn_fixz.py - CORRIGE Z-FIGHTING (textura "tremendo" no Roblox, feedback 09/10) antes da pintura assada.
# Acha faces de PECAS DIFERENTES (pedacos soltos ou objetos diferentes) no mesmo plano (mesma normal, distancia < 0.02)
# com area sobreposta e empurra a regiao coplanar da peca MENOR para fora ao longo da normal (OFF por camada). A peca
# grande fica onde esta; a pequena (friso, tampa, chapa, degrau) passa a ficar um fio na frente.
# uso: import sn_fixz; sn_fixz.fix()   (sn_build chama depois de montar e antes de assar)
import math
from collections import defaultdict

import bmesh
import bpy
from mathutils import Vector

OFF = 0.06              # studs por camada (0.04 ainda treme de longe no Roblox)
MIN_AREA = 0.04
EPS_D = 0.02


def _objs():
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.users_collection or o.data.users != 1:
            continue
        if o.name.startswith("WB_Veg") or o.name.startswith(("PREVIEW", "COL_", "CAM_")):
            continue
        if o.name.startswith(("WB_", "PORTAL_")):
            out.append(o)
    return out


def _clip(p, q):
    """area da intersecao de dois poligonos convexos 2D (Sutherland-Hodgman)"""
    def area(poly):
        return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                         for i in range(len(poly)))
    if area(q) < 0:
        q = list(reversed(q))
    out = list(p)
    for i in range(len(q)):
        a, c = q[i], q[(i + 1) % len(q)]
        ex, ey = c[0] - a[0], c[1] - a[1]
        inp, out = out, []
        if not inp:
            break
        for j in range(len(inp)):
            s, e = inp[j - 1], inp[j]
            si = ex * (s[1] - a[1]) - ey * (s[0] - a[0]) >= 0
            ei = ex * (e[1] - a[1]) - ey * (e[0] - a[0]) >= 0
            if ei:
                if not si:
                    out.append(_inter(s, e, a, c))
                out.append(e)
            elif si:
                out.append(_inter(s, e, a, c))
    return abs(area(out)) if len(out) >= 3 else 0.0


def _inter(s, e, a, c):
    x1, y1, x2, y2 = s[0], s[1], e[0], e[1]
    x3, y3, x4, y4 = a[0], a[1], c[0], c[1]
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(den) < 1e-12:
        return e
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den
    return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))


def fix(verbose=True):
    objs = _objs()
    data = {}          # obj -> (bm, mw, mwi)
    faces = []         # (oi, part, fidx, n(world), d, poly2d-ready verts, area)
    part_area = defaultdict(float)
    for oi, o in enumerate(objs):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        mw = o.matrix_world.copy()
        data[oi] = (bm, mw, mw.inverted())
        part = {}
        k = 0
        for f in bm.faces:
            if f.index in part:
                continue
            st = [f]
            part[f.index] = k
            while st:
                g = st.pop()
                for e in g.edges:
                    for h in e.link_faces:
                        if h.index not in part:
                            part[h.index] = k
                            st.append(h)
            k += 1
        nm = mw.to_3x3().inverted().transposed()
        for f in bm.faces:
            vs = [mw @ v.co for v in f.verts]
            n = (nm @ f.normal)
            if n.length < 1e-6:
                continue
            n.normalize()
            cr = Vector()
            for q in range(len(vs)):
                cr += vs[q].cross(vs[(q + 1) % len(vs)])
            a = 0.5 * abs(cr.dot(n))
            part_area[(oi, part[f.index])] += a
            if a < MIN_AREA:
                continue
            c = sum(vs, Vector()) / len(vs)
            faces.append((oi, part[f.index], f.index, n, n.dot(c), vs, a))
    # balde por normal arredondada; dentro dele, cadeia por distancia do plano e grade 2D
    nb = defaultdict(list)
    for i, fc in enumerate(faces):
        n = fc[3]
        nb[(round(n.x, 2), round(n.y, 2), round(n.z, 2))].append(i)
    pairs = []
    for key, ids in nb.items():
        if len(ids) < 2:
            continue
        ids.sort(key=lambda i: faces[i][4])
        clusters, cur = [], [ids[0]]
        for i in ids[1:]:
            if faces[i][4] - faces[cur[-1]][4] < EPS_D:
                cur.append(i)
            else:
                clusters.append(cur)
                cur = [i]
        clusters.append(cur)
        n0 = Vector(key).normalized()
        t = n0.orthogonal().normalized()
        bv = n0.cross(t)
        for cl in clusters:
            if len(cl) < 2 or len({(faces[i][0], faces[i][1]) for i in cl}) < 2:
                continue
            p2 = {i: [(v.dot(t), v.dot(bv)) for v in faces[i][5]] for i in cl}
            grid = defaultdict(list)
            CS = 4.0
            for i in cl:
                xs = [p[0] for p in p2[i]]
                ys = [p[1] for p in p2[i]]
                for gx in range(int(math.floor(min(xs) / CS)), int(math.floor(max(xs) / CS)) + 1):
                    for gy in range(int(math.floor(min(ys) / CS)), int(math.floor(max(ys) / CS)) + 1):
                        grid[(gx, gy)].append(i)
            seen = set()
            for cell in grid.values():
                for ii in range(len(cell)):
                    i = cell[ii]
                    for jj in range(ii + 1, len(cell)):
                        j = cell[jj]
                        if (faces[i][0], faces[i][1]) == (faces[j][0], faces[j][1]):
                            continue
                        pk = (i, j) if i < j else (j, i)
                        if pk in seen:
                            continue
                        seen.add(pk)
                        if abs(faces[i][4] - faces[j][4]) > EPS_D or faces[i][3].dot(faces[j][3]) < 0.999:
                            continue
                        pi, pj = p2[i], p2[j]
                        if (min(p[0] for p in pi) >= max(p[0] for p in pj) - 0.05
                                or min(p[0] for p in pj) >= max(p[0] for p in pi) - 0.05
                                or min(p[1] for p in pi) >= max(p[1] for p in pj) - 0.05
                                or min(p[1] for p in pj) >= max(p[1] for p in pi) - 0.05):
                            continue
                        ov = _clip(pi, pj)
                        if ov > 0.05:
                            pairs.append((i, j, ov))
    # quem sobe: em cada par a peca de MENOR area total fica na frente da maior. Nivel de cada peca no plano =
    # 1 + maior nivel das pecas que ela cobre (grafo aciclico: aresta sempre da menor para a maior) -> pecas que nao se
    # tocam podem ficar no mesmo nivel e nenhuma camada sobreposta empata (o teto antigo de 4 camadas empatava).
    front = defaultdict(lambda: defaultdict(set))       # plano -> peca -> pecas que ela cobre
    for i, j, ov in pairs:
        fi, fj = faces[i], faces[j]
        nkey = (round(fi[3].x, 2), round(fi[3].y, 2), round(fi[3].z, 2))
        dkey = round(fi[4] / 0.05)
        mi, mj = (fi[0], fi[1]), (fj[0], fj[1])
        small, big = (mi, mj) if (part_area[mi], mi) < (part_area[mj], mj) else (mj, mi)
        front[(nkey, dkey)][small].add(big)
    push = {}
    for (nkey, dkey), g in front.items():
        memo = {}

        def level(m, depth=0):
            if m in memo:
                return memo[m]
            if m not in g or depth > 50:
                memo[m] = 0
                return 0
            memo[m] = 1 + max(level(k, depth + 1) for k in g[m])
            return memo[m]
        for m in g:
            lv = level(m)
            if lv:
                push[(m[0], m[1], nkey, dkey)] = lv
    # aplica: move os vertices de TODAS as faces da regiao coplanar da peca (nao so as que sobrepoem)
    moved = defaultdict(lambda: defaultdict(float))     # (oi, vidx) -> {nkey: dist}
    for (oi, pt, f_i, n, d, vs, a) in faces:
        nkey = (round(n.x, 2), round(n.y, 2), round(n.z, 2))
        for dk in (round(d / 0.05), round(d / 0.05) - 1, round(d / 0.05) + 1):
            r = push.get((oi, pt, nkey, dk))
            if r:
                bm = data[oi][0]
                for v in bm.faces[f_i].verts:
                    moved[(oi, v.index)][nkey] = max(moved[(oi, v.index)][nkey], OFF * min(r, 6))
                break
    per_obj = defaultdict(int)
    for (oi, vi), dirs in moved.items():
        bm, mw, mwi = data[oi]
        v = bm.verts[vi]
        w = mw @ v.co
        for nkey, dist in dirs.items():
            w = w + Vector(nkey).normalized() * dist
        v.co = mwi @ w
        per_obj[oi] += 1
    for oi, (bm, mw, mwi) in data.items():
        if per_obj.get(oi):
            bm.to_mesh(objs[oi].data)
            objs[oi].data.update()
        bm.free()
    if verbose:
        grp = defaultdict(int)
        for oi, c in per_obj.items():
            grp[objs[oi].name.split("__")[0]] += c
        print("FIXZ pares %d, regioes empurradas %d, vertices %d" % (len(pairs), len(push), sum(per_obj.values())))
        print("FIXZ por grupo", sorted(grp.items(), key=lambda kv: -kv[1])[:30])
    return len(pairs)
