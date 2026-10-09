# sn_veg.py - KIT DE VEGETACAO estilo anime (Ghibli/Genshin): copas de "nuvens" de folhagem com luz pintada forte
# (claro-amarelado em cima, verde-azulado embaixo, AO entre os tufos), troncos afunilados com raizes, pinheiros em
# saias estreladas, arbustos e a ARVORE ANCIA (raizes abracando ruinas). Cada variante e modelada UMA vez fora do mapa,
# assada no proprio atlas (512) e depois COPIADA para os pontos (copias juntadas por variante = mesmo atlas).
import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import fm_lib
import sn_lib as SL
from wb_lib import RB

V = Vector
KIT_O = (2600.0, 0.0)          # canteiro do kit (Blender x, y), longe do mapa
GZ = 7.0                       # chao do kit = chao da praca


def _rng(*k):
    return random.Random(str(k))


def _hash3(x, y, z):
    v = math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453
    return v - math.floor(v)


def _vnoise(p, s):
    """value noise 3D suave (para deformar os tufos)"""
    x, y, z = p.x * s, p.y * s, p.z * s
    xi, yi, zi = math.floor(x), math.floor(y), math.floor(z)
    fx, fy, fz = x - xi, y - yi, z - zi
    fx, fy, fz = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy), fz * fz * (3 - 2 * fz)
    acc = 0.0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (fx if dx else 1 - fx) * (fy if dy else 1 - fy) * (fz if dz else 1 - fz)
                acc += w * _hash3(xi + dx, yi + dy, zi + dz)
    return acc


def puff(b, c, r, mat, seed, squash=0.82, lumps=0.16, seg=14):
    """tufo de folhagem: esfera deformada por ruido (bolhas), achatada embaixo"""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg * 2 // 3), radius=1.0)
    off = V((_hash3(seed, 1, 2) * 50, _hash3(seed, 3, 4) * 50, _hash3(seed, 5, 6) * 50))
    for v in bm.verts:
        d = v.co.normalized()
        n1 = _vnoise(d * 1.0 + off, 2.2)
        n2 = _vnoise(d * 1.0 + off * 1.7, 5.0)
        k = 1.0 + lumps * (n1 - 0.5) * 2.0 + lumps * 0.5 * (n2 - 0.5) * 2.0
        z = d.z
        if z < 0:
            z *= 0.62                                     # base achatada (tufo pousa na copa)
        v.co = V((d.x * k * r, d.y * k * r, z * k * r * squash))
    bmesh.ops.translate(bm, vec=V(c), verts=bm.verts[:])
    b.mesh(bm, mat)


def trunk(b, pts, radii, mat="SN_Bark", seg=9):
    """tronco/galho em segmentos afunilados por uma polilinha"""
    for (p0, p1), (r0, r1) in zip(zip(pts, pts[1:]), zip(radii, radii[1:])):
        b.cyl(p0, p1 + (p1 - p0).normalized() * 0.15, r0, mat, r1=r1, seg=seg)


def roots(b, base, r, n, h, seed, mat="SN_Bark"):
    rr = _rng("roots", seed)
    for k in range(n):
        a = 2 * math.pi * k / n + rr.uniform(-0.3, 0.3)
        d = V((math.cos(a), math.sin(a), 0))
        p0 = base + V((0, 0, h))
        p1 = base + d * r * rr.uniform(1.6, 2.2) + V((0, 0, -0.3))
        b.cyl(p0, p1, r * 0.42, mat, r1=r * 0.12, seg=6)


def oak(b, o, h, seed, leaf="SN_Leaf"):
    """carvalho de copa em nuvem: tronco curvo + 2-3 galhos + 7-10 tufos"""
    rr = _rng("oak", seed)
    base = V(o)
    lean = V((rr.uniform(-1, 1), rr.uniform(-1, 1), 0)) * h * 0.03
    p = [base + V((0, 0, -0.6)), base + V((0, 0, h * 0.25)) + lean * 0.4, base + V((0, 0, h * 0.5)) + lean]
    rt = h * 0.065
    trunk(b, p, [rt * 1.25, rt, rt * 0.78])
    roots(b, base, rt, 5, h * 0.06, seed)
    top = p[-1]
    cz = base.z + h * 0.66
    R = h * 0.36
    tips = []
    for k in range(3):
        a = 2 * math.pi * k / 3 + rr.uniform(-0.4, 0.4)
        d = V((math.cos(a), math.sin(a), 0))
        q = top + d * R * 0.55 + V((0, 0, h * 0.12))
        trunk(b, [top, q], [rt * 0.6, rt * 0.3], seg=6)
        tips.append(q)
    # tufos: coroa central alta + anel + tufos nas pontas dos galhos
    puff(b, V((top.x, top.y, cz + R * 0.42)), R * 0.78, leaf, seed * 7 + 1)
    n = rr.randint(5, 6)
    for k in range(n):
        a = 2 * math.pi * k / n + rr.uniform(-0.25, 0.25)
        d = R * rr.uniform(0.55, 0.7)
        c = V((top.x + d * math.cos(a), top.y + d * math.sin(a), cz + rr.uniform(-R * 0.12, R * 0.15)))
        puff(b, c, R * rr.uniform(0.5, 0.62), leaf, seed * 7 + 2 + k)
    for k, q in enumerate(tips):
        puff(b, q + V((0, 0, R * 0.1)), R * 0.42, leaf, seed * 7 + 20 + k)
    return R


def pine(b, o, h, seed, leaf="SN_PineLeaf"):
    """pinheiro estilizado: saias em estrela (pontas caidas), mais estreitas para cima"""
    rr = _rng("pine", seed)
    base = V(o)
    rt = h * 0.04
    trunk(b, [base + V((0, 0, -0.6)), base + V((0, 0, h * 0.45))], [rt * 1.2, rt * 0.7], seg=7)
    roots(b, base, rt, 4, h * 0.04, seed)
    nt = 5
    for k in range(nt):
        t = k / (nt - 1)
        z0 = base.z + h * (0.2 + 0.62 * t)
        rad = h * (0.30 - 0.21 * t) * rr.uniform(0.92, 1.06)
        hh = h * (0.30 - 0.1 * t)
        npt = 9
        bm = bmesh.new()
        ring = []
        ring2 = []
        rot = rr.uniform(0, 2 * math.pi)
        for j in range(npt * 2):
            a = rot + math.pi * j / npt
            rj = rad * (1.0 if j % 2 == 0 else 0.7)
            dz = -hh * (0.18 if j % 2 == 0 else 0.02)     # pontas caidas
            ring.append(bm.verts.new((base.x + rj * math.cos(a), base.y + rj * math.sin(a), z0 + dz)))
            ring2.append(bm.verts.new((base.x + rj * 0.55 * math.cos(a), base.y + rj * 0.55 * math.sin(a),
                                       z0 + hh * 0.18 + dz * 0.4)))
        apex = bm.verts.new((base.x, base.y, z0 + hh))
        under = bm.verts.new((base.x, base.y, z0 + hh * 0.08))
        n2 = len(ring)
        for j in range(n2):
            j2 = (j + 1) % n2
            bm.faces.new((ring[j], ring[j2], ring2[j2], ring2[j]))
            bm.faces.new((ring2[j], ring2[j2], apex))
            bm.faces.new((ring[j2], ring[j], under))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, leaf)
    return h * 0.3


def bush(b, o, s, seed, leaf="SN_Leaf", flower=None):
    rr = _rng("bush", seed)
    base = V(o)
    for k in range(4):
        a = 2 * math.pi * k / 4 + rr.uniform(-0.4, 0.4)
        d = s * rr.uniform(0.2, 0.45)
        puff(b, base + V((d * math.cos(a), d * math.sin(a), s * 0.35)), s * rr.uniform(0.45, 0.62), leaf, seed * 5 + k,
             squash=0.75, seg=10)
    if flower:
        for k in range(7):
            a = rr.uniform(0, 2 * math.pi)
            d = s * rr.uniform(0.2, 0.7)
            b.sphere(base + V((d * math.cos(a), d * math.sin(a), s * rr.uniform(0.6, 0.95))), s * 0.11, flower, seg=6)
    return s


def ancient(b, o, h, seed, leaf="SN_Leaf"):
    """ARVORE ANCIA: tronco largo e torcido, raizes enormes, 4 galhos grossos, copa larga em camadas"""
    rr = _rng("anc", seed)
    base = V(o)
    rt = h * 0.085
    p = [base + V((0, 0, -0.8)), base + V((0.6, 0.3, h * 0.2)), base + V((-0.4, 0.8, h * 0.4)), base + V((0.3, 0.2, h * 0.55))]
    trunk(b, p, [rt * 1.5, rt * 1.15, rt * 0.95, rt * 0.8], seg=12)
    roots(b, base, rt * 1.2, 7, h * 0.09, seed)
    top = p[-1]
    R = h * 0.42
    cz = base.z + h * 0.68
    for k in range(4):
        a = 2 * math.pi * k / 4 + rr.uniform(-0.3, 0.3)
        d = V((math.cos(a), math.sin(a), 0))
        q1 = top + d * R * 0.35 + V((0, 0, h * 0.06))
        q2 = top + d * R * 0.75 + V((0, 0, h * 0.1))
        trunk(b, [top, q1, q2], [rt * 0.55, rt * 0.4, rt * 0.22], seg=8)
        puff(b, q2 + V((0, 0, R * 0.12)), R * 0.5, leaf, seed * 11 + k)
    puff(b, V((top.x, top.y, cz + R * 0.35)), R * 0.72, leaf, seed * 11 + 9)
    for k in range(7):
        a = 2 * math.pi * k / 7 + rr.uniform(-0.2, 0.2)
        d = R * rr.uniform(0.45, 0.62)
        puff(b, V((top.x + d * math.cos(a), top.y + d * math.sin(a), cz + rr.uniform(-R * 0.05, R * 0.25))),
             R * rr.uniform(0.42, 0.52), leaf, seed * 11 + 20 + k)
    return R


# variante -> (construtor, altura/escala, folha, extra)
VARIANTS = {
    "oak1": (oak, 22.0, "SN_Leaf", 1),
    "oak2": (oak, 18.0, "SN_Leaf", 2),
    "oak3": (oak, 24.0, "SN_LeafLight", 3),
    "oakG": (oak, 20.0, "SN_LeafGold", 4),
    "pine1": (pine, 30.0, "SN_PineLeaf", 1),
    "pine2": (pine, 24.0, "SN_PineLeaf", 2),
    "bush1": (bush, 3.4, "SN_Leaf", 1),
    "bushF": (bush, 3.0, "SN_Leaf", 2),
    "ancient": (ancient, 46.0, "SN_Leaf", 1),
}
_KIT = {}


def build_kit(names=None, size=512, reuse=False):
    """modela cada variante no canteiro e assa (um atlas 512 por variante). Devolve {nome: (objeto, origem)}"""
    import sn_paint as P
    names = names or list(VARIANTS)
    ground = None
    me = bpy.data.meshes.new("TMP_KitGround")
    bm = bmesh.new()
    x0, y0 = KIT_O
    for (x, y) in ((-60, -60), (60 * len(names) + 60, -60), (60 * len(names) + 60, 60), (-60, 60)):
        bm.verts.new((x0 + x, y0 + y, GZ))
    bm.faces.new(bm.verts[:])
    bm.to_mesh(me)
    bm.free()
    ground = bpy.data.objects.new("TMP_KitGround", me)
    bpy.context.scene.collection.objects.link(ground)
    ground.data.materials.append(bpy.data.materials.get("WB_Grass"))
    for i, nm in enumerate(names):
        fn, sc, leaf, sd = VARIANTS[nm]
        o = V((x0 + 60.0 * i, y0, GZ))
        b = SL.Build("WB_VegK_%s" % nm, "09_VEGETATION")
        flower = "SN_FlowerBlue" if nm == "bushF" else None
        if fn is bush:
            fn(b, o, sc, sd, leaf, flower)
        else:
            fn(b, o, sc, sd, leaf)
        b.finish(smooth_angle=179.0)
        big = fn is ancient
        P.bake_group("WB_VegK_%s" % nm, "Veg_%s" % nm, pps=6.0, samples=16, reuse=reuse, size=1024 if big else size)
        parts = sorted([x for x in bpy.data.objects if x.name.startswith("WB_VegK_%s__" % nm)], key=lambda x: x.name)
        _KIT[nm] = (parts[0], o, parts[1:])
    bpy.data.objects.remove(ground, do_unlink=True)
    bpy.data.meshes.remove(me)
    return _KIT


def place(nm, spots, coll="09_VEGETATION", col=True):
    """copia a variante para os pontos [(x_rbx, z_rbx, y_rbx, yaw_graus, escala)] e junta numa malha por variante"""
    ob, o, extra = _KIT[nm]
    srcs = [ob] + extra
    out = []
    for src in srcs:
        bm_all = bmesh.new()
        for (x, z, y, yaw, s) in spots:
            T = (Matrix.Translation(RB(x, z, y)) @ Matrix.Rotation(math.radians(yaw), 4, "Z") @
                 Matrix.Diagonal(V((s, s, s, 1.0))) @ Matrix.Translation(-V(o)))
            tmp = src.data.copy()
            tmp.transform(src.matrix_world)
            tmp.transform(T)
            bm_all.from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
        suffix = src.name.split("__", 1)[1]
        me = bpy.data.meshes.new("WB_Veg_%s__%s" % (nm, suffix))
        bm_all.to_mesh(me)
        bm_all.free()
        for m in src.data.materials:
            me.materials.append(m)
        for p in me.polygons:
            p.use_smooth = True
        nob = bpy.data.objects.new(me.name, me)
        SL.collection(coll).objects.link(nob)
        out.append(nob)
    if col:
        fn, sc, leaf, sd = VARIANTS[nm]
        for (x, z, y, yaw, s) in spots:
            if fn is bush:
                continue
            h = sc * s
            rt = h * (0.085 if fn is ancient else 0.065 if fn is oak else 0.04) * 2.4
            fm_lib.col_box("Veg", (rt, rt, h * 0.5), RB(x, z, y + h * 0.25), (0, 0, 0))
    return out


def hide_kit():
    """tira as matrizes do kit da cena (ficam so as copias)"""
    for nm, (ob, o, extra) in _KIT.items():
        for x in [ob] + extra:
            for c in list(x.users_collection):
                c.objects.unlink(x)
