# il_mining_qa - auditoria da zona mining (regras novas da rodada 2), roda num .blend pronto:
#   blender -b <int.blend> --python il_mining_qa.py [-- MINE_]
#   1. z-fighting: face de um objeto do prefixo com outra face (de QUALQUER objeto proximo) paralela, mesmo sentido,
#      a menos de 0,1 e com material diferente, sobrepostas na projecao (amostras no centro e a meio caminho dos
#      vertices);
#   2. pecas microscopicas: componente conectado com TODAS as dimensoes < 0,35;
#   3. resumo por objeto (tris, materiais).
import sys, os, math
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREFIX = tuple(argv[0].split(",")) if argv else ("MINE_",)
GAP = 0.1
MICRO = 0.35
PIT_TOP, PIT_R = 3.2, 60.0          # il_layout.PIT / PIT_R


def world_polys(ob):
    me = ob.data
    mw = ob.matrix_world
    nm = mw.to_3x3().inverted().transposed()
    vs = [mw @ v.co for v in me.vertices]
    out = []
    for p in me.polygons:
        mi = p.material_index
        mat = me.materials[mi].name if mi < len(me.materials) and me.materials[mi] else "?"
        n = (nm @ p.normal).normalized()
        out.append(([vs[i] for i in p.vertices], n, mat, p.area))
    return out


def bbox(ob):
    mw = ob.matrix_world
    cs = [mw @ Vector(c) for c in ob.bound_box]
    return (Vector((min(c.x for c in cs), min(c.y for c in cs), min(c.z for c in cs))),
            Vector((max(c.x for c in cs), max(c.y for c in cs), max(c.z for c in cs))))


def main():
    tgt = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith(PREFIX)]
    if not tgt:
        print("MQA nenhum objeto com prefixo", PREFIX)
        return
    lo = Vector((min(bbox(o)[0].x for o in tgt), min(bbox(o)[0].y for o in tgt), min(bbox(o)[0].z for o in tgt)))
    hi = Vector((max(bbox(o)[1].x for o in tgt), max(bbox(o)[1].y for o in tgt), max(bbox(o)[1].z for o in tgt)))
    others = []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith("COL_") or o in tgt or o.hide_render:
            continue
        a, b = bbox(o)
        if a.x > hi.x or a.y > hi.y or a.z > hi.z or b.x < lo.x or b.y < lo.y or b.z < lo.z:
            continue
        others.append(o)
    verts, polys, info = [], [], []
    tgt_ranges = {}
    for o in tgt + others:
        s = len(info)
        for vs, n, mat, area in world_polys(o):
            base = len(verts)
            verts += vs
            polys.append(list(range(base, base + len(vs))))
            info.append((o.name, mat, n, area))
        if o in tgt:
            tgt_ranges[o.name] = (s, len(info))
    bvh = BVHTree.FromPolygons(verts, polys, all_triangles=False)
    hits = {}
    for name, (s, e) in tgt_ranges.items():
        for fi in range(s, e):
            oname, mat, n, area = info[fi]
            if area < 0.01:
                continue
            pv = [verts[i] for i in polys[fi]]
            c = sum(pv, Vector()) / len(pv)
            samples = [c] + [c + (v - c) * 0.5 for v in pv]
            # face virada para baixo enterrada sob o piso do fosso (terra opaca por cima): nao aparece
            if n.z < -0.9 and c.z < PIT_TOP - 0.02 and math.hypot(c.x, c.y) < PIT_R - 0.5:
                continue
            for p in samples:
                for co, nn, idx, dist in bvh.find_nearest_range(p, GAP):
                    if idx == fi or idx is None:
                        continue
                    o2, mat2, n2, area2 = info[idx]
                    if mat2 == mat or n2.dot(n) < 0.995 or area2 < 0.01:
                        continue
                    d = p - co
                    lat = d - n * d.dot(n)
                    if lat.length > 0.02:
                        continue
                    key = (oname, mat, o2, mat2)
                    rec = hits.setdefault(key, [0, p.copy(), abs(d.dot(n)), n.copy(), co.copy()])
                    rec[0] += 1
                    break
    # dedup simetrico
    seen = set()
    rows = []
    for (a, ma, b, mb_), (cnt, p, gap, n, co) in sorted(hits.items(), key=lambda kv: -kv[1][0]):
        k = tuple(sorted([(a, ma), (b, mb_)]))
        if k in seen:
            continue
        seen.add(k)
        rows.append((cnt, a, ma, b, mb_, p, gap, n))
    print("MQA zfight pares=%d" % len(rows))
    for cnt, a, ma, b, mb_, p, gap, n in rows[:40]:
        print("MQA ZF %4d  %s[%s] x %s[%s]  em (%.2f, %.2f, %.2f) n=(%.2f,%.2f,%.2f) folga %.3f" % (
            cnt, a, ma, b, mb_, p.x, p.y, p.z, n.x, n.y, n.z, gap))
    # pecas microscopicas
    tot_micro = 0
    for o in tgt:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.verts.ensure_lookup_table()
        mw = o.matrix_world
        seen_v = set()
        micro = []
        for v in bm.verts:
            if v.index in seen_v:
                continue
            stack = [v]
            comp = []
            seen_v.add(v.index)
            while stack:
                x = stack.pop()
                comp.append(x)
                for e in x.link_edges:
                    y = e.other_vert(x)
                    if y.index not in seen_v:
                        seen_v.add(y.index)
                        stack.append(y)
            cs = [mw @ x.co for x in comp]
            dims = (max(c.x for c in cs) - min(c.x for c in cs), max(c.y for c in cs) - min(c.y for c in cs),
                    max(c.z for c in cs) - min(c.z for c in cs))
            if max(dims) < MICRO:
                micro.append((cs[0], dims))
        bm.free()
        tot_micro += len(micro)
        if micro:
            print("MQA MICRO %s: %d pecas (ex.: %s)" % (o.name, len(micro),
                                                       ["(%.1f,%.1f,%.1f) %s" % (c.x, c.y, c.z,
                                                                                 tuple(round(d, 2) for d in dm))
                                                        for c, dm in micro[:4]]))
    print("MQA micro_total=%d" % tot_micro)
    for o in sorted(tgt, key=lambda o: o.name):
        me = o.data
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        print("MQA OBJ %-26s tris=%6d mats=%s" % (o.name, t, [m.name for m in me.materials if m]))


main()
