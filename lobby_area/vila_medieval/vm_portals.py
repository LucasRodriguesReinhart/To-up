# vm_portals - os 6 PORTAIS APROVADOS (fm_pv3_<key>.build + fm_portals.onepiece, lobby_area/forja_mineradora: SO
# LEITURA, chamados com a MESMA semente do portal_studio -> saem identicos ao que o usuario aprovou) levados para o
# terraco em semicirculo do patio dos portais (oeste) por transformacao rigida.
# Cada portal e montado no lugar original (x = PORTAL_X, espiral em y = 113, pad na cota T = 30 do lobby antigo, olhando
# -Y Blender = +Z Roblox) e depois: (1) corta o que era da ESCADA antiga (faces com centro em y < 99 ou abaixo de T-2:
# dressing do lance 2 do One Piece, fundacoes do terraco) e as COL da escada (centro em y < 99,5, a mesma regra do
# portal_studio); (2) aplica M = T(novo) . Rz(phi) . T(-velho) nas raizes (malhas, COL_, marcadores PORTAL_*, luzes).
# O piso do pad (cota T) cai na cota Y_PORTAL do terraco novo; a espiral passa a olhar para o centro do patio.
import math, random
import bpy, bmesh
from mathutils import Matrix, Vector
import vm_lib as VL
import vm_layout as L

YCUT, ZCUT = 99.0, 28.0          # corte da escada antiga (y Blender) e das fundacoes (abaixo de T - 2)


def _crop(ob):
    """apaga as faces da escada antiga / fundacoes (no referencial ORIGINAL do portal)"""
    if ob.type != "MESH":
        return 0
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    mw = ob.matrix_world
    dead = []
    for f in bm.faces:
        c = mw @ f.calc_center_median()
        if c.y < YCUT or c.z < ZCUT:
            dead.append(f)
    n = len(dead)
    if dead:
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        bm.to_mesh(ob.data)
    bm.free()
    return n


def build():
    import fm_pv3, fm_portals
    import fm_layout as FL                       # planta ANTIGA (so para saber onde o portal nasce)
    mods = fm_pv3.load()
    report = []
    for i, (key, aid) in enumerate(L.PORTALS):
        before = set(bpy.data.objects)
        if key in mods:
            mods[key].build(random.Random(fm_pv3.SEED[key]))
        else:
            fm_portals.onepiece(random.Random(707))          # One Piece: padrao de qualidade, fica no fm_portals
        new = [o for o in bpy.data.objects if o not in before]
        bpy.context.view_layer.update()              # matrix_world das pecas recem-criadas (location sem depsgraph)
        px = FL.PORTAL_X[FL.PORTAL_KEYS.index(key)]
        cut_f, cut_col = 0, 0
        for o in list(new):
            if o.name.startswith("TMP_"):
                bpy.data.objects.remove(o, do_unlink=True)
                new.remove(o)
                continue
            if o.name.startswith("COL_"):
                if o.matrix_world.translation.y < 99.5 or o.matrix_world.translation.z < ZCUT - 1.0:
                    bpy.data.objects.remove(o, do_unlink=True)
                    new.remove(o)
                    cut_col += 1
                continue
            if o.type == "MESH":
                cut_f += _crop(o)
        (nx, nz), (fx, fz) = L.portal_pos(i)
        old = Vector((px, FL.PORTAL_Y, FL.TERR))
        neu = VL.B(nx, nz, L.Y_PORTAL)
        phi = VL.yaw_b(fx, fz) + math.pi / 2           # original olha -Y (angulo -90 graus)
        M = Matrix.Translation(neu) @ Matrix.Rotation(phi, 4, "Z") @ Matrix.Translation(-old)
        for o in new:
            if o.parent is None:
                o.matrix_world = M @ o.matrix_world
            o["vm_portal"] = key
        bpy.context.view_layer.update()
        tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in new
                   if o.type == "MESH" and not o.name.startswith("COL_"))
        report.append((key, aid, len(new), tris, cut_f, cut_col))
        print("PORTAL %-12s area %d: %3d objetos, %6d tris, cortadas %d faces + %d COL da escada antiga -> (%.1f, %.1f)"
              % (key, aid, len(new), tris, cut_f, cut_col, nx, nz))
    bpy.context.view_layer.update()
    return report
