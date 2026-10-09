# sn_zfight.py - acha Z-FIGHTING (textura "tremendo" no Roblox): pares de faces de PECAS DIFERENTES (pedacos soltos ou
# objetos diferentes) no mesmo plano (normais iguais, distancia < 0.02) com area sobreposta. Lista por grupo e local.
# uso: blender -b renders/build/build.blend --python sn_zfight.py [-- min_area]
import math
import sys
from collections import defaultdict

import bmesh
import bpy
from mathutils import Vector
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sn_fixz import _clip

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MIN_AREA = float(argv[0]) if argv else 0.25
faces = []                                  # (obj, part, normal, d, center, verts2d basis, area, poly)
for o in bpy.data.objects:
    if o.type != "MESH" or not o.name.startswith(("WB_", "PORTAL_")) or not o.users_collection:
        continue
    me = o.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(o.matrix_world)
    bm.normal_update()
    bm.faces.ensure_lookup_table()
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
    for f in bm.faces:
        a = f.calc_area()
        if a < MIN_AREA:
            continue
        n = f.normal.copy()
        if n.length < 0.5:
            continue
        c = f.calc_center_median()
        faces.append((o.name, part[f.index], n, n.dot(c), c, [v.co.copy() for v in f.verts], a))
    bm.free()
print("faces:", len(faces))
# balde por (normal arredondada, distancia do plano arredondada)
bucket = defaultdict(list)
for i, (on, pt, n, d, c, vs, a) in enumerate(faces):
    key = (round(n.x, 2), round(n.y, 2), round(n.z, 2), round(d / 0.04))
    bucket[key].append(i)


def proj(vs, n):
    t = n.orthogonal().normalized()
    b = n.cross(t)
    return [(v.dot(t), v.dot(b)) for v in vs]


def overlap(p, q):
    """area da sobreposicao REAL (recorte de poligonos convexos) de duas faces no mesmo plano; a caixa 2D so filtra
    (a caixa sozinha dava falso positivo em tiras compridas: a base do orthogonal() do mathutils e girada 45 graus)"""
    ax0, ax1 = min(x for x, _ in p), max(x for x, _ in p)
    ay0, ay1 = min(y for _, y in p), max(y for _, y in p)
    bx0, bx1 = min(x for x, _ in q), max(x for x, _ in q)
    by0, by1 = min(y for _, y in q), max(y for _, y in q)
    w = min(ax1, bx1) - max(ax0, bx0)
    h = min(ay1, by1) - max(ay0, by0)
    if w <= 0.05 or h <= 0.05:
        return 0.0
    return _clip(p, q)


hits = defaultdict(float)
where = {}
for key, ids in bucket.items():
    if len(ids) < 2:
        continue
    for ii in range(len(ids)):
        i = ids[ii]
        on_i, pt_i, n_i, d_i, c_i, vs_i, a_i = faces[i]
        pi = proj(vs_i, n_i)
        for jj in range(ii + 1, len(ids)):
            j = ids[jj]
            on_j, pt_j, n_j, d_j, c_j, vs_j, a_j = faces[j]
            if on_i == on_j and pt_i == pt_j:
                continue
            if abs(d_i - d_j) > 0.02 or n_i.dot(n_j) < 0.999:
                continue
            ov = overlap(pi, proj(vs_j, n_i))
            if ov <= 0.1:
                continue
            g = tuple(sorted((on_i.split("__")[0], on_j.split("__")[0])))
            hits[g] += ov
            if g not in where or ov > where[g][1]:
                rb = (round(c_i.x, 1), round(c_i.z, 1), round(-c_i.y, 1))
                where[g] = (rb, ov, on_i, on_j)
print("PARES (grupo A / grupo B: area sobreposta; exemplo em coord Roblox X,Y,Z)")
for g, a in sorted(hits.items(), key=lambda kv: -kv[1])[:60]:
    w = where[g]
    print("ZF %-34s %-34s %8.1f  em %s  (%s | %s)" % (g[0], g[1], a, w[0], w[2], w[3]))
