# fm_props - props de ambientacao com proposito: iluminacao das rotas, estandartes de entrada, bancos da praca,
# pilhas de carga junto aos pontos logisticos, placas de direcao (sem texto), fumaca da chamine (helper VFX)
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, marker, light, resample, point_in_poly
from fm_parts import (Frame, lantern, banner, crate, barrel, crystal_cluster, mine_cart, emblem_pickaxe,
                      emblem_hammers, fence)
import fm_layout as L

F0 = L.FLOOR


def building_boxes(margin=1.5):
    """pegadas xy das construcoes (lanternas e cargas nunca nascem dentro de alas, torre ou casas)"""
    import bpy
    out = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(("FORGE_", "BLD_", "WATER_Waterwheel", "MINE_Entrance")):
            continue
        if o.name.startswith("BLD_Bridges"):
            continue
        cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
        out.append((min(c.x for c in cs) - margin, min(c.y for c in cs) - margin,
                    max(c.x for c in cs) + margin, max(c.y for c in cs) + margin))
    return out


def inside_any(x, y, boxes):
    return any(x0 < x < x1 and y0 < y < y1 for (x0, y0, x1, y1) in boxes)


def build():
    rng = random.Random(1111)
    import fm_buildings
    BOXES = building_boxes()
    mb = MB("PROP_Path_Lanterns", "08_PROPS", rng)
    # lanternas ao longo dos caminhos (alternando lados, a cada ~16), braco para o caminho
    k = 0
    for name, (pts, w) in fm_buildings.PATHS.items():
        if name in ("Shop_Apron",):
            continue
        fine = resample([Vector((p[0], p[1], 0)) for p in pts], 16.0)
        for i, p in enumerate(fine[:-1] if len(fine) > 2 else fine[:1]):
            q = fine[min(i + 1, len(fine) - 1)]
            t = (q - p).normalized() if (q - p).length > 0 else Vector((1, 0, 0))
            s = Vector((-t.y, t.x, 0))
            side = 1 if i % 2 == 0 else -1
            pos = p + t * 5.0 + s * side * (w / 2 + 1.6)
            # nunca na frente do pe de uma escada de portal
            if pos.y > 33 and min(abs(pos.x - px) for px in L.PORTAL_X) < 11.0:
                pos = p + t * 5.0 - s * side * (w / 2 + 1.6)
                side = -side
                if pos.y > 33 and min(abs(pos.x - px) for px in L.PORTAL_X) < 11.0:
                    continue
            if any(point_in_poly(pos.x, pos.y, fm_buildings.ribbon(pp, ww + 2.0))
                   for (pp, ww) in fm_buildings.PATHS.values()):
                continue
            if inside_any(pos.x, pos.y, BOXES):
                continue
            ang = math.atan2(-s.y * side, -s.x * side)
            lantern(mb, (pos.x, pos.y, F0), ang, name="L_Path_%s_%02d" % (name, i), h=7.0)
            col_box("Props", (1.5, 1.5, 8.0), (pos.x, pos.y, F0 + 4.0))
            k += 1
    # lanternas nos pes das escadas dos portais (pares, como na referencia)
    for j, px in enumerate(L.PORTAL_X):
        for sgn in (-1, 1):
            x = px + sgn * 9.2
            lantern(mb, (x, L.FLIGHT1_Y0 - 0.5, F0), math.pi if sgn > 0 else 0.0, name="L_StairFoot_%d_%d" % (j, sgn + 1),
                    h=6.5, arm=False)
            col_box("Props", (1.5, 1.5, 8.5), (x, L.FLIGHT1_Y0 - 0.5, F0 + 4.2))
    # escadaria do spawn: par de lanternas + estandartes (moldura da chegada)
    for sgn in (-1, 1):
        lantern(mb, (sgn * 12.0, -73.0, 0.0), 0.0, name="L_SpawnStair_%d" % (sgn + 1), h=6.5, arm=False)
        col_box("Props", (1.5, 1.5, 8.5), (sgn * 12.0, -73.0, 4.2))
    mb.finish()

    bn = MB("PROP_Entrance_Banners", "08_PROPS", rng)
    for sgn in (-1, 1):
        x = sgn * 13.0
        y = -58.0
        for dx in (-1.7, 1.7):
            bn.box((0.9, 0.9, 13.0), (x + dx, y, F0 + 6.5), (0, 0, 0), "Wood_Dark", 0.1)
        bn.box((5.2, 1.0, 0.9), (x, y, F0 + 12.6), (0, 0, 0), "Wood_Dark", 0.08)
        banner(bn, (x, y - 0.2, F0 + 12.0), 0.0, w=2.8, h=7.0, cloth="Cloth_Navy", trim="Metal_Brass", emblem="pickaxe")
        col_box("Props", (4.4, 1.2, 13.0), (x, y, F0 + 6.5))
    bn.finish()

    # bancos de madeira na borda da praca (voltados para a forja)
    bc = MB("PROP_Plaza_Benches", "08_PROPS", rng)
    # bancos na margem leste do rio, de frente para a roda d'agua (lugar de parada, fora das rotas)
    for (bx, by) in ((L.RIVER_X[1] + 7.0, L.WHEEL_C[1] - 16.0), (L.RIVER_X[1] + 7.0, L.WHEEL_C[1] - 25.0)):
        c = Vector((bx, by, F0 + 0.35))
        ang = D(90)
        F = Frame(c.x, c.y, c.z, ang)
        bc.box((5.0, 1.4, 0.35), F.p(0, 0, 1.6), F.r(), "Wood_Plank", 0.06)
        bc.box((5.0, 0.3, 1.2), F.p(0, 0.65, 2.6), F.r(), "Wood_Plank", 0.05)
        for sx in (-2.0, 2.0):
            bc.box((0.4, 1.4, 1.6), F.p(sx, 0, 0.8), F.r(), "Stone_Dark", 0.08)
        col_box("Props", (5.0, 1.6, 2.2), (c.x, c.y, c.z + 1.1), F.r())
    bc.finish()

    # pilhas de carga: saida da mina, deposito na forja, cais do rio, patio dos fundos
    cg = MB("PROP_Cargo", "08_PROPS", rng)
    clusters = [(-60, -54, 0.6), (-30, 2, 1.2), (50, -30, 2.0), (70, -30, 0.5), (-12, 34, 0.2),
                (12, 34, 0.8), (106, 28, 1.5), (-100, 32, 0.4), (122, -20, 1.0), (-66, 8, 0.3)]
    for (x, y, a) in clusters:
        if inside_any(x, y, BOXES):
            continue
        if any(point_in_poly(x, y, fm_buildings.ribbon(pp, ww + 8.0)) for (pp, ww) in fm_buildings.PATHS.values()):
            continue
        F = Frame(x, y, F0 + 0.3, a)
        crate(cg, tuple(F.p(0, 0, 0)), 2.2, a, rng)
        crate(cg, tuple(F.p(2.4, 0.3, 0)), 2.0, a + 0.2, rng)
        crate(cg, tuple(F.p(1.2, 0.1, 2.2)), 1.8, a - 0.1, rng)
        barrel(cg, tuple(F.p(-2.2, 1.0, 0)))
        if rng.random() < 0.6:
            crystal_cluster(cg, tuple(F.p(0.0, 0.0, 2.2)), 0.5, "Crystal_Blue", rng, 4)
        c = F.p(0.4, 0.2, 0)
        col_box("Props", (6.4, 3.6, 4.2), (c.x, c.y, F0 + 2.4), F.r())
    cg.finish()

    # placas de direcao sem texto (icones): mina / portais / forja - no centro-oeste e no pos-ponte
    sg = MB("PROP_Signposts", "08_PROPS", rng)
    for (x, y, arrows) in ((-30, -50, ((-150, "pick"), (60, "portal"))), (74, -24, ((90, "portal"), (180, "forge")))):
        sg.box((0.9, 0.9, 8.5), (x, y, F0 + 4.25), (0, 0, 0), "Wood_Dark", 0.1)
        for j, (deg, icon) in enumerate(arrows):
            a = D(deg)
            z = F0 + 7.0 - j * 1.8
            c = Vector((x + math.cos(a) * 2.0, y + math.sin(a) * 2.0, z))
            sg.box((4.0, 0.3, 1.3), c, (0, 0, a), "Wood_Plank", 0.08)
            tip = Vector((x + math.cos(a) * 4.3, y + math.sin(a) * 4.3, z))
            sg.cyl(0.9, 0.3, tip, (D(90), 0, a + math.pi / 2), "Wood_Plank", 3, bevel=0.0)
            ic = Vector((x + math.cos(a) * 2.4, y + math.sin(a) * 2.4, z))
            m = {"pick": "Crystal_Blue", "portal": "P_Shadow_Glow", "forge": "Forge_Emissive"}[icon]
            sg.ico(0.45, ic + Vector((math.sin(a) * 0.3, -math.cos(a) * 0.3, 0)), m, 1)
        col_box("Props", (1.2, 1.2, 8.5), (x, y, F0 + 4.25))
    sg.finish()

    # helper VFX: fumaca da chamine (bolhas cinza subindo e derivando; no Roblox vira ParticleEmitter)
    sm = MB("VFX_Chimney_Smoke", "12_VFX_HELPERS", rng)
    cx, cy = L.CHIMNEY
    z = L.CHIMNEY_TOP + 1.0
    for i in range(16):
        f = i / 15
        r = 3.5 + f * 9.0
        p = Vector((cx + f * f * 26.0 + rng.uniform(-2, 2), cy + f * 12.0 + rng.uniform(-2, 2), z + f * 70.0))
        sm.ico(r, p, "Smoke", 2, (1, 1, 0.8), jitter=0.2)
    sm.finish()
    marker("VFX_Chimney_Smoke_Emitter", (cx, cy, L.CHIMNEY_TOP), (0, 0, 0), 4, props={"particle": "smoke", "rate": 6})
    marker("VFX_Forge_Sparks", (L.ANVIL[0], L.ANVIL[1], L.FL + 6), (0, 0, 0), 2, props={"particle": "sparks"})
    marker("VFX_Hearth_Fire", (0, 0.5, L.FL + 3), (0, 0, 0), 2, props={"particle": "fire"})
    for key, px in zip(L.PORTAL_KEYS, L.PORTAL_X):
        marker("VFX_Portal_Swirl_%s" % key, (px, L.PORTAL_Y, L.TERR + 11.2), (0, 0, 0), 3,
               props={"anim": "girar espiral em Y, 30 graus/s"})
