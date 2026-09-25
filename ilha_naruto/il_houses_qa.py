# il_houses_qa - auditoria rapida da zona houses (so as pecas do il_houses, sem o resto da ilha)
# uso: blender -b --factory-startup --python il_houses_qa.py [-- zfight]
#   * por objeto: materiais, MeshParts estimadas (mesma regra do studio.est_meshparts), area por material
#     (< 60 studs2 = o fold do export funde no vizinho ou, se protegido, sobra uma MeshPart minuscula), altura do
#     objeto acima do chao da casa
#   * z-fighting: faces alinhadas aos eixos, mesmo sentido, materiais diferentes, a menos de 0,1 uma da outra e com
#     sobreposicao > 0,02 studs2 (dentro de cada objeto e entre objetos da zona)
import sys, os, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy
import fm_lib
import il_layout as L

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
IL.reset_scene()
fm_lib.make_materials()
before = {o.name for o in bpy.data.objects}
import il_houses as H
t = time.time()
H.build()
print("HQA build %.1fs" % (time.time() - t))
made = [o for o in bpy.data.objects if o.name not in before]
meshes = [o for o in made if o.type == "MESH" and not o.name.startswith("COL_")]
PROTECT = ("Flower_", "Emblem_", "Water", "Foam", "Crystal_", "Lantern_", "Window_Warm")


def est_mp(ob):
    per = {}
    for p in ob.data.polygons:
        per[p.material_index] = per.get(p.material_index, 0) + len(p.vertices) - 2
    return sum(max(1, math.ceil(t / 18000.0)) for t in per.values())


def ground(ob):
    n = ob.name
    if "_Upper_" in n:
        return H.UPPER_Z
    if n.startswith("VIL_House_T2"):
        return L.T2
    if n.startswith("VIL_House_T1"):
        return L.T1
    return L.G


tot_mp = 0
tot_tri = 0
small = []
for ob in sorted(meshes, key=lambda o: o.name):
    me = ob.data
    area = {}
    for p in me.polygons:
        m = me.materials[p.material_index].name if me.materials[p.material_index] else "?"
        area[m] = area.get(m, 0.0) + p.area
    mp = est_mp(ob)
    tot_mp += mp
    tri = sum(len(p.vertices) - 2 for p in me.polygons)
    tot_tri += tri
    zs = [v.co.z for v in me.vertices]
    h = max(zs) - ground(ob)
    print("HQA %-24s mp=%2d tris=%5d alt=%5.1f  %s" % (ob.name, mp, tri, h,
                                                       " ".join("%s:%.0f" % (k, v) for k, v in sorted(area.items()))))
    for k, v in area.items():
        if v < 60.0:
            small.append((ob.name, k, round(v, 1), "protegido" if k.startswith(PROTECT) else "FUNDE"))
print("HQA TOTAL MeshParts~%d tris=%d objetos=%d" % (tot_mp, tot_tri, len(meshes)))
print("HQA materiais < 60 studs2 por objeto:", small or "nenhum")
print("HQA pecas microscopicas descartadas:", {k: v for k, v in H.MICRO_LOG.items() if v} if hasattr(H, "MICRO_LOG") else "?")

if "zfight" in argv:
    # faces axiais: (eixo, sinal) -> lista (coord, rect2d, material, objeto, z_chao)
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    verts, polys, normals = [], [], []
    buckets = {}
    for ob in meshes:
        me = ob.data
        mw = ob.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in me.vertices]
        gz = ground(ob)
        for p in me.polygons:
            polys.append([base + i for i in p.vertices])
            n = p.normal
            normals.append(Vector(n))
            ax = max(range(3), key=lambda i: abs(n[i]))
            if abs(n[ax]) < 0.999:
                continue
            sg = 1 if n[ax] > 0 else -1
            vs = [mw @ me.vertices[i].co for i in p.vertices]
            if ax == 2 and sg < 0 and vs[0].z <= gz + 0.15:
                continue                      # fundo apoiado no chao
            u, v = [i for i in range(3) if i != ax]
            r = (min(q[u] for q in vs), min(q[v] for q in vs), max(q[u] for q in vs), max(q[v] for q in vs))
            if (r[2] - r[0]) * (r[3] - r[1]) < 1e-4:
                continue
            m = me.materials[p.material_index].name
            buckets.setdefault((ax, sg), []).append((vs[0][ax], r, m, ob.name))
    bvh = BVHTree.FromPolygons(verts, polys)

    def visible(ax, sg, c_front, uc, vc):
        """a face da frente (na cota c_front) e vista de fora no ponto (uc, vc)? (nao esta coberta por outra peca
        nem dentro de um solido)"""
        u, v = [i for i in range(3) if i != ax]
        p0 = [0.0, 0.0, 0.0]
        p0[ax], p0[u], p0[v] = c_front + sg * 0.3, uc, vc
        p0 = Vector(p0)
        n = Vector([0.0, 0.0, 0.0])
        n[ax] = sg
        h = bvh.ray_cast(p0, -n, 0.6)
        if h[0] is None or abs(h[3] - 0.3) > 0.03:
            return False
        # o ponto de partida esta dentro de um solido? (algum raio sai por uma face vista por dentro)
        dirs = [n]
        for k in (u, v):
            for sgn in (-1.0, 1.0):
                d = Vector([0.0, 0.0, 0.0])
                d[k] = sgn
                dirs.append(d)
        for d in dirs:
            h2 = bvh.ray_cast(p0, d, 60.0)
            if h2[0] is not None and normals[h2[2]].dot(d) > 0.5:
                return False
        return True

    hits = []
    for key, lst in buckets.items():
        lst.sort(key=lambda e: e[0])
        j0 = 0
        for i in range(len(lst)):
            ci, ri, mi, oi = lst[i]
            while lst[j0][0] < ci - 0.1:
                j0 += 1
            for j in range(j0, i):
                cj, rj, mj, oj = lst[j]
                if mi == mj or abs(ci - cj) >= 0.0995:
                    continue
                ox0, ox1 = max(ri[0], rj[0]), min(ri[2], rj[2])
                oy0, oy1 = max(ri[1], rj[1]), min(ri[3], rj[3])
                if ox1 - ox0 > 0.05 and oy1 - oy0 > 0.05 and (ox1 - ox0) * (oy1 - oy0) > 0.02:
                    front = max(ci, cj) if key[1] > 0 else min(ci, cj)
                    if not visible(key[0], key[1], front, (ox0 + ox1) / 2, (oy0 + oy1) / 2):
                        continue
                    hits.append((round(abs(ci - cj), 3), "XYZ"[key[0]] + ("+" if key[1] > 0 else "-"), oi, mi, oj, mj,
                                 [round(x, 2) for x in (ox0, oy0, ox1, oy1)], round(front, 2)))
    print("HQA ZFIGHT visiveis=%d" % len(hits))
    for h in sorted(hits)[:60]:
        print("HQA ZF d=%.3f %s %s:%s x %s:%s em %s plano %.2f" % h)
