# sn_qa.py - QA do lobby Santuario sobre as COLISOES (as COL_ viram Parts invisiveis no Roblox; e nelas que o jogador
# anda): rotas a pe do spawn ate cada estacao (chao continuo, degrau <= 2,1, cabeca livre 5, sem parede na frente),
# tempo de caminhada (16 studs/s), envoltoria do Ignis livre, ligacao da ponte com a Ilha 1 (z 222 na cota 6).
# uso: blender -b renders/build/build.blend --python sn_qa.py
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import sn_layout as L

WALK = 16.0
STEP = 2.1
HEAD = 5.0


def col_bvh():
    verts, polys = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_"):
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
    return BVHTree.FromPolygons(verts, polys)


def B(x, z, y):
    return Vector((x, -z, y))


def walk(bvh, name, pts, y0):
    """segue a polilinha (x, z) a partir da cota y0; devolve (ok, comprimento, problemas)"""
    dense = []
    for (a, c) in zip(pts, pts[1:]):
        d = math.hypot(c[0] - a[0], c[1] - a[1])
        k = max(1, int(d / 0.75))
        for j in range(k):
            t = j / k
            dense.append((a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t))
    dense.append(pts[-1])
    y = y0
    probs = []
    length = 0.0
    for i, (x, z) in enumerate(dense):
        hit = bvh.ray_cast(B(x, z, y + STEP + 0.4), Vector((0, 0, -1)), STEP + 6.0)
        if hit[0] is None:
            probs.append("sem chao em (%.1f, %.1f) cota %.2f" % (x, z, y))
            break
        g = hit[0].z
        if g - y > STEP:
            probs.append("degrau de %.2f em (%.1f, %.1f)" % (g - y, x, z))
            break
        up = bvh.ray_cast(Vector((B(x, z, g).x, B(x, z, g).y, g + 0.3)), Vector((0, 0, 1)), HEAD)
        if up[0] is not None:
            probs.append("teto baixo (%.1f) em (%.1f, %.1f)" % (up[0].z - g, x, z))
            break
        if i + 1 < len(dense):
            nx, nz = dense[i + 1]
            d = Vector((nx - x, -(nz - z), 0))
            dl = d.length
            if dl > 1e-6:
                for hh in (2.4, 3.6):
                    w = bvh.ray_cast(Vector((x, -z, g + hh)), d.normalized(), dl + 0.6)
                    if w[0] is not None:
                        probs.append("parede a %.1f stud (altura %.1f) em (%.1f, %.1f)" % (w[3], hh, x, z))
                        break
                if probs:
                    break
                length += dl
        y = g
    return (not probs), length, probs, y


def main():
    bvh = col_bvh()
    sp = L.SPAWN
    routes = []
    stair_n = (0.0, L.STAIR["z_top"] - L.STAIR["n"] * L.STAIR["run"] - 1.0)
    plaza_s = (0.0, 30.0)
    routes.append(("SPAWN->IGNIS", [sp, (0, 52.5), stair_n, plaza_s, (0, -30), L.PLAYER_IGNIS], L.Y_SPAWN))
    bz = L.ISLE_BRIDGE["z"]
    ix, iz = L.PORTAL_ISLE_C
    wa = math.radians(L.WEST_ANG)
    west = [(L.PLAZA_R * 0.9 * math.cos(wa), L.PLAZA_R * 0.9 * math.sin(wa)), (L.ISLE_BRIDGE["x_main"] + 10.0, bz),
            (L.ISLE_BRIDGE["x_isle"] - 8.0, bz), (ix + L.ISLE_COURT_R - 4.0, iz)]
    for i, (key, aid) in enumerate(L.PORTALS):
        (x, z), (fx, fz) = L.portal_pos(i)
        a = math.radians(L.PORTAL_ANG[i])
        # contorna a Pedra dos Mundos pelo anel r 13 (do lado do portal)
        ad = L.PORTAL_ANG[i]
        sgn = 1 if ad < 180 else -1
        ring = []
        t = 0.0
        while True:
            ring.append((ix + 13.0 * math.cos(math.radians(t)), iz + 13.0 * math.sin(math.radians(t))))
            if abs(t - (ad if sgn > 0 else ad - 360.0)) < 1e-6:
                break
            nxt = t + sgn * 20.0
            tgt = ad if sgn > 0 else ad - 360.0
            t = min(nxt, tgt) if sgn > 0 else max(nxt, tgt)
        routes.append(("SPAWN->PORTAL%d %s" % (i + 1, key), [sp, (0, 52.5), stair_n, plaza_s] + west[:-1] + ring +
                       [(x + fx * 12.0, z + fz * 12.0)], L.Y_SPAWN))
    sx, sz = L.SHOP_C
    fx, fz = L.SHOP_FACE
    a = math.atan2(sz, sx)
    routes.append(("SPAWN->LOJA", [sp, (0, 52.5), stair_n, plaza_s, (L.PLAZA_R * 0.9 * math.cos(a), L.PLAZA_R * 0.9 * math.sin(a)),
                                   (sx + fx * 20.0, sz + fz * 20.0), (sx + fx * 8.0, sz + fz * 8.0), L.SHOP_PLAYER], L.Y_SPAWN))
    rx, rz = L.RANK_O
    fx, fz = L.RANK_FACE
    a = math.atan2(rz, rx)
    routes.append(("SPAWN->TABUAS", [sp, (0, 52.5), stair_n, plaza_s, (L.PLAZA_R * 0.9 * math.cos(a), L.PLAZA_R * 0.9 * math.sin(a)),
                                     (rx + fx * 16.0, rz + fz * 16.0)], L.Y_SPAWN))
    routes.append(("SPAWN->ILHA1", [sp, (0, 79.0), (0, 92.0), (0, 120.0), (0, 148.0), (0, 180.0), (0, 221.5)], L.Y_SPAWN))
    ok_all = True
    print("=" * 80)
    for name, pts, y0 in routes:
        ok, ln, probs, yend = walk(bvh, name, pts, y0)
        t = ln / WALK
        flag = "OK " if ok else "FALHA"
        if not ok:
            ok_all = False
        print("ROTA %-28s %s  %6.1f studs  %4.1f s  cota final %.2f  %s" % (name, flag, ln, t, yend, "; ".join(probs)))
    # envoltoria do Ignis: nenhuma malha de cena dentro (alem do piso)
    (x0, y0, z0), (x1, y1, z1) = L.IGNIS_ENV
    inside = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("WB_") or not o.users_collection:
            continue
        mw = o.matrix_world
        n = 0
        for v in o.data.vertices:
            w = mw @ v.co
            X, Y, Z = w.x, w.z, -w.y
            if x0 < X < x1 and y0 + 0.1 < Y < y1 and z0 < Z < z1:
                n += 1
        if n:
            inside[o.name] = n
    print("IGNIS envoltoria: %s" % ("LIVRE" if not inside else "INVADIDA %s" % inside))
    hit = bvh.ray_cast(B(L.ISLE_LINK[0], L.ISLE_LINK[2] - 0.5, 20.0), Vector((0, 0, -1)), 40.0)
    print("LINK ponte -> Ilha 1 (z %.1f): chao na cota %s (esperado %.1f)" % (
        L.ISLE_LINK[2] - 0.5, "%.2f" % hit[0].z if hit[0] else "NENHUM", L.ISLE_LINK[1]))
    print("QA %s" % ("OK" if ok_all and not inside else "COM FALHAS"))


main()
