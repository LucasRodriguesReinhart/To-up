# db_qa - testes automaticos da Ilha 2: navegacao sobre as colisoes COL_ (mesmo andador do lobby/Ilha 1: degrau 2,3,
# queda 2,3, altura livre 6,5, corpo 1,1) nas rotas da missao (secao 38) + extras, sondas de borda, auditoria tecnica
# e conferencia dos marcadores/cameras obrigatorios.
# uso: blender -b ilha_dragonball.blend --python db_qa.py -- [nav] [tech] [markers]   (padrao: tudo)
import sys, os, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db_lib as DL
import bpy, bmesh
from mathutils import Vector
import db_layout as L
import db_col
import fm_qa


def prom_mid(a):
    return L.arena_r(a) + L.prom_w(a) * 0.5


def prom_arc(a0, a1, step=10.0):
    n = max(1, int(abs(a1 - a0) / step))
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        r = prom_mid(a)
        out.append((r * math.cos(math.radians(a)), r * math.sin(math.radians(a))))
    return out


def access_path(ang, inward_extra=6.0):
    """do meio do promenade ate dentro da arena passando pelo acesso (angulo)"""
    foot, top, d = L.access_frame(ang)
    r = prom_mid(ang)
    a = math.radians(ang)
    mid = (r * math.cos(a), r * math.sin(a))
    beyond = (foot[0] + d[0] * inward_extra, foot[1] + d[1] * inward_extra)
    return [mid, (top[0] - d[0] * 0.0 + math.cos(a) * 1.5, top[1] + math.sin(a) * 1.5), top, foot, beyond]


def gate_pts():
    gp = L.gate_sg_pos()
    ux, uy = L.exit_dir()
    return gp, (gp[0] - ux * 7.0, gp[1] - uy * 7.0), (gp[0] + ux * 12.0, gp[1] + uy * 12.0)


def bridge_to_gate():
    gp, front, after = gate_pts()
    return [L.EXIT_START, L.exit_point(20.0), L.exit_point(44.0), L.exit_point(L.EXIT_BRIDGE_LEN + 2.0), front]


def capsule_in():
    """da frente do terraco do Capsule ate o ponto de interacao do salao"""
    cx, cy = L.CAPSULE_C
    return [(0.0, L.CAP_STAIR[1] + 2.0), (0.0, L.CAPSULE_DOOR_Y - 2.0), (0.0, L.CAPSULE_DOOR_Y + 3.0),
            (0.0, L.CAPSULE_CORRIDOR[1] + 2.0), (0.0, L.CAPSULE_CORRIDOR[3] + 3.0), (cx, cy + 6.0)]


def hub_up_center():
    """do promenade norte ate a frente do terraco do Capsule (escada central da vila + escadaria do Capsule)"""
    yh = db_col.hub_front_y(0.0)
    y0 = L.CAP_STAIR[1] - L.CAP_STAIR_N * L.TREAD
    return [(0.0, prom_mid(90.0)), (0.0, yh - 5 * L.TREAD - 1.0), (0.0, yh + 1.5), (0.0, (yh + y0) / 2),
            (0.0, y0 - 1.0), (0.0, L.CAP_STAIR[1] + 1.5)]


def summon_in():
    x, y, w = L.SUMMON_STAIR
    return [(x + 2.0, y), (x - L.SUMMON_STAIR_N * L.TREAD - 1.5, y), (L.SUMMON_C[0] + 10.0, L.SUMMON_C[1])]


def exit_up():
    fx, fy, fdeg, fw = L.EXIT_STAIR
    a = math.radians(fdeg)
    r = prom_mid(28.0)
    return [(r * math.cos(math.radians(28.0)), r * math.sin(math.radians(28.0))), (fx - math.cos(a) * 2.0, fy - math.sin(a) * 2.0),
            (fx + math.cos(a) * 9.5, fy + math.sin(a) * 9.5)] + L.EXIT_PATH[1:]


def routes():
    r = {}
    sx, sy = L.ENTRY_SPAWN
    arrival = [(0.0, L.PREV_Y - 24.0), (0.0, L.PREV_Y + 1.0), (0.0, -150.0), (0.0, L.BRIDGE_Y1 - 1.5),
               (0.0, L.ENTRY_STAIR_Y1 + 1.5), (0.0, L.GATE_Y), (sx, sy)]
    r["NARUTO_GATE->DB_ENTRY"] = (arrival, L.DECK)
    south = [(sx, sy), (0.0, -76.0)] + access_path(270.0)[1:] + [(0.0, -20.0)]
    r["DB_ENTRY->MINING"] = (south, L.GROUND)
    r["DB_ENTRY->CAPSULE"] = ([(sx, sy), (0.0, -prom_mid(270.0))] + prom_arc(270.0, 450.0)[1:] + hub_up_center()[1:]
                              + capsule_in()[1:], L.GROUND)
    w = list(reversed(access_path(180.0)))
    r["MINING->SUMMON"] = ([(-10.0, 0.0)] + w + summon_in(), L.ARENA)
    n = list(reversed(access_path(90.0)))
    r["MINING->CAPSULE"] = ([(0.0, 10.0)] + n + hub_up_center()[1:] + capsule_in()[1:], L.ARENA)
    e = list(reversed(access_path(14.0, inward_extra=4.0)))
    r["MINING->SHADOW_GATE"] = ([(12.0, 2.0)] + e + prom_arc(14.0, 28.0)[1:] + exit_up()[1:] + bridge_to_gate()[1:],
                                L.ARENA)
    cap_out = list(reversed(capsule_in()))
    hub_east = [(0.0, 96.0), (20.0, 84.0), (50.0, 83.0), (86.0, 84.0)] + L.HUB_EXIT_LINK + [L.EXIT_PATH[-1]]
    r["CAPSULE->SHADOW_GATE"] = (cap_out + [(0.0, L.CAP_STAIR[1] - L.CAP_STAIR_N * L.TREAD - 1.5)] + hub_east +
                                 bridge_to_gate()[1:], L.CAP)
    sum_out = list(reversed(summon_in()))
    r["SUMMON->SHADOW_GATE"] = (sum_out + [(-prom_mid(180.0), -2.0)] + prom_arc(180.0, 388.0)[1:] + exit_up()[1:] +
                                bridge_to_gate()[1:], L.SUM)
    # extras
    r["PROMENADE_LOOP"] = (prom_arc(0.0, 360.0, step=6.0), L.GROUND)
    for i, (x, y, ww) in enumerate(L.HUB_SIDE_STAIRS):
        yh = db_col.hub_front_y(x)
        a = math.degrees(math.atan2(y, x))
        r["PROM->HUB_%s" % ("W" if x < 0 else "E")] = ([(x, yh - 5 * L.TREAD - 3.0), (x, yh - 5 * L.TREAD - 1.0),
                                                         (x, yh + 1.5), (x, yh + 6.0)], L.GROUND)
    for x, y, rr, kind, walk in L.TOWER_SITES:
        if walk:
            a0, a1 = L.SAT_BRIDGES[kind]
            r["SAT_%s" % kind] = ([(a0[0] * 0.9, a0[1] * 0.9), a0, a1, (x, y)], L.GROUND)
    return r


def open_routes():
    gp, front, after = gate_pts()
    return {"PORTAO_SG_ABERTO->ANCORA": ([front, gp, after, L.exit_point(L.EXIT_BRIDGE_LEN + L.ANCHOR_OFF - 1.0)],
                                         L.EXIT_Z)}


def module_routes():
    import importlib, build_db
    rr, pp = {}, []
    for mods in build_db.ZONE_MODULES.values():
        for m in mods:
            if not os.path.exists(os.path.join(HERE, m + ".py")):
                continue
            try:
                mod = importlib.import_module(m)
            except Exception as ex:
                print("QA aviso: nao importou %s (%s)" % (m, ex))
                continue
            for k, v in getattr(mod, "EXTRA_ROUTES", {}).items():
                rr["%s:%s" % (m, k)] = v
            pp += list(getattr(mod, "EXTRA_PROBES", []))
    return rr, pp


def _probes():
    ux, uy = L.exit_dir()
    out = []
    ap = L.anchor_pos()
    out.append(("ANCORA_SG_borda", ap[0] - ux * 1.0, ap[1] - uy * 1.0, L.EXIT_Z, ux, uy, 3.5))
    p = L.exit_point(32.0)
    out.append(("PONTE_SAIDA_lado_N", p[0], p[1], L.EXIT_Z, -uy, ux, L.EXIT_W / 2 + 3.0))
    out.append(("PONTE_SAIDA_lado_S", p[0], p[1], L.EXIT_Z, uy, -ux, L.EXIT_W / 2 + 3.0))
    out.append(("PONTE_CHEGADA_lado_O", 0.0, -160.0, L.DECK, -1.0, 0.0, L.DECK_W / 2 + 3.0))
    out.append(("PONTE_CHEGADA_lado_L", 0.0, -160.0, L.DECK, 1.0, 0.0, L.DECK_W / 2 + 3.0))
    for x, y, r, kind, walk in L.TOWER_SITES:
        if walk:
            a0, a1 = L.SAT_BRIDGES[kind]
            dx, dy = x - a1[0], y - a1[1]
            ln = math.hypot(dx, dy) or 1.0
            out.append(("SAT_%s_ponta" % kind, x + dx / ln * (r - 1.5), y + dy / ln * (r - 1.5), L.GROUND, dx / ln,
                        dy / ln, 3.5))
    return out


def probes(bvh, extra=()):
    res = []
    for pr in list(_probes()) + [tuple(e) + ((3.5,) if len(e) == 6 else ()) for e in extra]:
        name, x, y, z, dx, dy, reach = pr
        o = Vector((x, y, z + 2.0))
        d = Vector((dx, dy, 0.0)).normalized()
        hit = bvh.ray_cast(o, d, reach)
        ok = hit[0] is not None
        res.append((name, ok))
        print(("OK   " if ok else "FAIL ") + "SONDA " + name + ("" if ok else "  (borda aberta: nada segura o jogador)"))
    return res


def col_bvh(exclude=()):
    from mathutils.bvhtree import BVHTree
    verts, polys = [], []
    fm_qa.OWNER.clear()
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith("COL_") or o.name.startswith(exclude):
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
        fm_qa.OWNER.extend([o.name] * len(o.data.polygons))
    return BVHTree.FromPolygons(verts, polys), len(polys)


def naruto_stub():
    """cabeceira da Ilha 1 (so para o teste NARUTO_GATE->DB_ENTRY): 30 studs de tabuleiro antes de WORLD_FROM_PREV"""
    if bpy.data.objects.get("COL_QA_NarutoStub_001"):
        return
    ob = DL.col_box2("QA_NarutoStub", (-L.DECK_W / 2, L.PREV_Y - 30.0, L.DECK - 2.0), (L.DECK_W / 2, L.PREV_Y + 0.5, L.DECK))
    bpy.context.view_layer.update()
    return ob


def nav():
    naruto_stub()
    bvh, n = col_bvh()
    print("COL faces:", n)
    res = {}
    ok = 0
    for name, (pts, z0) in routes().items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        res[name] = f
        ok += not f
        print(("OK   " if not f else "FAIL ") + name + ("" if not f else "  " + str(f)))
    print("ROTAS %d/%d OK" % (ok, len(res)))
    bvh2, _ = col_bvh(exclude=("COL_GateShadowGardenLock",))
    ok2 = 0
    rr = open_routes()
    for name, (pts, z0) in rr.items():
        f, zend = fm_qa.walk(bvh2, pts, z0)
        ok2 += not f
        print(("OK   " if not f else "FAIL ") + name + ("" if not f else "  " + str(f)))
    print("ROTAS_ABERTAS %d/%d OK" % (ok2, len(rr)))
    mr, mp = module_routes()
    ok3 = 0
    for name, (pts, z0) in mr.items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        ok3 += not f
        print(("OK   " if not f else "FAIL ") + name + ("" if not f else "  " + str(f)))
    if mr:
        print("ROTAS_MODULOS %d/%d OK" % (ok3, len(mr)))
    pr = probes(bvh, mp)
    print("SONDAS %d/%d OK" % (sum(1 for _, k in pr if k), len(pr)))
    old = fm_qa.BODY_R
    fm_qa.BODY_R = 1.7
    try:
        estreitas = [nm for nm, (pts, z0) in routes().items() if fm_qa.walk(bvh, pts, z0)[0]]
    finally:
        fm_qa.BODY_R = old
    print("LARGURA rotas com trecho < 3,4 de largura: %s" % (estreitas or "nenhuma"))
    o = bpy.data.objects.get("COL_QA_NarutoStub_001")
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    return res


REQUIRED = ["WORLD_FROM_PREV", "WORLD_ENTRY_DragonBall", "PATH_ENTRY_CENTER", "MiningZone_DragonBall", "SUMMON_Main",
            "SUMMON_Interact", "SUMMON_PlayerPosition", "ISLAND_EXIT_DragonBall", "ISLAND_NEXT_ANCHOR_ShadowGarden",
            "GATE_ShadowGarden", "GATE_ShadowGarden_INTERACT", "GATE_ShadowGarden_LOCKED", "GATE_ShadowGarden_EXIT",
            "PURCHASE_UI_ANCHOR_ShadowGarden", "GATE_ShadowGarden_OpenFX", "NPC_Capsule", "PLAYER_INTERACT_Capsule"]
REQUIRED_CAMS = ["CAM_DB_Entry", "CAM_DB_Front", "CAM_DB_Left", "CAM_DB_Right", "CAM_DB_Back", "CAM_DB_BirdEye",
                 "CAM_DB_Mining", "CAM_DB_Capsule", "CAM_DB_Summon", "CAM_DB_ShadowGate", "CAM_DB_PlayerHeight_Entry",
                 "CAM_DB_PlayerHeight_Mining", "CAM_DB_PlayerHeight_Summon", "CAM_DB_PlayerHeight_ShadowGate"]


def markers():
    names = {o.name for o in bpy.data.objects}
    miss = [n for n in REQUIRED + REQUIRED_CAMS if n not in names]
    ores = {}
    pts = []
    for o in bpy.data.objects:
        m = re.match(r"ORE_(COMMON|UNCOMMON|EPIC|SUPERLEGENDARY)_\d+$", o.name)
        if m:
            ores[m.group(1)] = ores.get(m.group(1), 0) + 1
            pts.append((o.location.x, o.location.y, o.get("radius", 2.5), o.name))
    overl = 0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i], pts[j]
            if math.hypot(a[0] - b[0], a[1] - b[1]) < a[2] + b[2] + 2.0:
                overl += 1
    print("MARKERS faltando=%d %s" % (len(miss), miss))
    print("MARKERS minerio=%s sobrepostos=%d" % (ores, overl))
    return miss


def tech():
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh|Empty|Camera|Light)(\.\d+)?$")
    dup = re.compile(r".+\.\d{3}$")
    bad, dups, nomat, scale, degen, nonman, tris, heavy = [], [], [], [], 0, 0, 0, []
    per = []
    for o in bpy.data.objects:
        if gen.match(o.name):
            bad.append(o.name)
        if dup.match(o.name):
            dups.append(o.name)
        if o.type != "MESH" or o.name.startswith("COL_"):
            continue
        me = o.data
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        tris += t
        per.append((t, o.name))
        if t > 18000 * 6:
            heavy.append((o.name, t))
        if not me.materials or any(m is None for m in me.materials):
            nomat.append(o.name)
        if any(abs(s - 1.0) > 1e-4 for s in o.scale) or any(abs(r) > 1e-6 for r in o.rotation_euler):
            scale.append(o.name)
        for p in me.polygons:
            if p.area < 1e-6:
                degen += 1
        bm = bmesh.new()
        bm.from_mesh(me)
        nonman += sum(1 for e in bm.edges if not e.is_manifold)
        bm.free()
    per.sort(reverse=True)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("TECH nomes_genericos=%d duplicados=%d sem_material=%d transform_nao_aplicado=%d degeneradas=%d "
          "arestas_nao_manifold=%d" % (len(bad), len(dups), len(nomat), len(scale), degen, nonman))
    print("TECH tris=%d objetos=%d malhas=%d materiais=%d colisoes=%d" % (
        tris, len(bpy.data.objects), sum(1 for o in bpy.data.objects if o.type == "MESH"),
        len([m for m in bpy.data.materials if m.users]), ncol))
    print("TECH maiores:", per[:8])
    for lab, lst in (("genericos", bad), ("duplicados", dups), ("sem material", nomat), ("transform", scale),
                     ("pesados", heavy)):
        if lst:
            print("TECH %s: %s" % (lab, lst[:12]))
    return dict(bad=bad, dups=dups, nomat=nomat, scale=scale, degen=degen, nonman=nonman, tris=tris)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    argv = argv or ["nav", "tech", "markers"]
    if "nav" in argv:
        nav()
    if "markers" in argv:
        markers()
    if "tech" in argv:
        tech()
