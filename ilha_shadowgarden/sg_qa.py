# sg_qa - testes automaticos da Ilha 3: navegacao sobre as colisoes COL_ (mesmo andador do lobby e das Ilhas 1/2:
# degrau 2,3, queda 2,3, altura livre 6,5, corpo 1,1) nas rotas da missao, sondas de borda, salao de mineracao livre,
# caixa da dungeon limpa, auditoria tecnica e conferencia dos marcadores/cameras obrigatorios.
# uso: blender -b ilha_shadowgarden.blend --python sg_qa.py -- [nav] [tech] [markers] [clear]   (padrao: tudo)
import sys, os, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_lib as SL
import bpy, bmesh
from mathutils import Vector
import sg_layout as L
import sg_col
import fm_qa

P1, P2, P3, SUM = L.P1, L.P2, L.P3, L.SUM


# ------------------------------------------------------------------ trechos de rota (pontos xy; o andador acha o z)
def arrival():
    sx, sy = L.ENTRY_SPAWN
    return [(0.0, L.PREV_Y - 24.0), (0.0, L.PREV_Y + 1.0), (0.0, L.BRIDGE_Y1 + 2.0), (0.0, L.ENTRY_STAIR[1] - 1.5),
            (0.0, L.ENTRY_STAIR_Y1 + 1.5), (0.0, L.PORTICO_B_Y), (sx, sy)]


def spawn_to_plaza_north():
    sx, sy = L.ENTRY_SPAWN
    return [(sx, sy), (0.0, -152.0), (-14.0, -140.0), (-14.0, -116.0), (0.0, -103.0)]


def up_to_p2():
    return [(0.0, -103.0), (0.0, -100.5), (0.0, -82.0), (0.0, -60.0), (0.0, -45.0)]


def p2_to_forecourt():
    return [(0.0, -45.0), (0.0, -29.0), (0.0, -26.5), (0.0, -8.0), (0.0, -2.0), (0.0, 20.0)]


def forecourt_to_hall():
    return [(0.0, 20.0), (0.0, 36.0), (0.0, 42.0), (0.0, 50.0), (0.0, 70.0), (-20.0, 100.0), (20.0, 120.0)]


def p2_east_to_craft():
    cx, cy = L.CRAFT_C
    return [(0.0, -45.0), (40.0, -45.0), (60.0, -46.0), (68.0, -56.0), (cx - L.CRAFT_R - 3.0, cy),
            (cx - L.CRAFT_R + 1.0, cy), (cx - 5.0, cy)]


def forecourt_to_dungeon():
    cx, cy, w, d = L.DUNGEON_HOUSE
    return [(0.0, 20.0), (46.0, 20.0), (80.0, 30.0), (cx, cy - d / 2 - 8.0), (cx, cy - d / 2 + 1.0), (cx, cy - 2.0)]


def plaza_to_summon():
    a0, a1, w = L.SUMMON_BRIDGE
    top = L.stair_top("Summon")
    return [(-14.0, -140.0), (-26.0, -120.0), (-60.0, -120.0), (-96.0, -118.0), (a0[0] - 1.0, a0[1]),
            (a1[0] + 0.5, a1[1]), (top[0] - 1.5, top[1]), (L.SUMMON_TOWER[0] + 14.0, L.SUMMON_TOWER[1])]


def p2_to_exit_gate():
    g = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    return [(0.0, -45.0), (60.0, -45.0), (100.0, -38.0), (130.0, -38.0), (L.EXIT_START[0] - 2.0, L.EXIT_START[1]),
            L.exit_point(20.0), L.exit_point(44.0), L.exit_point(L.EXIT_BRIDGE_LEN + 2.0), (g[0] - ux * 7.0, g[1] - uy * 7.0)]


def dungeon_to_p2_east():
    cx, cy, w, d = L.DUNGEON_HOUSE
    ft = L.stair_frame("EastP3")[0]
    return [(cx, cy - 2.0), (cx, cy - d / 2 + 1.0), (cx, cy - d / 2 - 8.0), (110.0, 30.0), (ft[0], -6.0), (ft[0], -10.0),
            (ft[0], ft[1] - 1.0), (ft[0] - 2.0, -36.0)]


def rev(p):
    return list(reversed(p))


def routes():
    r = {}
    r["DB_ANCORA->SG_ENTRADA"] = (arrival(), L.DECK)
    ent_hall = spawn_to_plaza_north() + up_to_p2()[1:] + p2_to_forecourt()[1:] + forecourt_to_hall()[1:]
    r["ENTRADA->CASTELO_MINING_HALL"] = (ent_hall, P1)
    r["ENTRADA->SUMMON"] = ([L.ENTRY_SPAWN, (0.0, -152.0)] + plaza_to_summon(), P1)
    r["ENTRADA->CRAFT"] = (spawn_to_plaza_north() + up_to_p2()[1:] + p2_east_to_craft()[1:], P1)
    r["ENTRADA->DUNGEON"] = (spawn_to_plaza_north() + up_to_p2()[1:] + p2_to_forecourt()[1:] + forecourt_to_dungeon()[1:], P1)
    r["VILA->CASTELO"] = ([(-100.0, -45.0), (-40.0, -44.0)] + p2_to_forecourt() + forecourt_to_hall()[1:4], P2)
    hall_out = rev(forecourt_to_hall()[:5])
    r["CASTELO->CRAFT"] = (hall_out + rev(p2_to_forecourt())[1:] + p2_east_to_craft()[1:], P3)
    r["CASTELO->DUNGEON"] = (hall_out + forecourt_to_dungeon()[1:], P3)
    r["CASTELO->PORTAO_DS"] = (hall_out + rev(p2_to_forecourt())[1:] + p2_to_exit_gate()[1:], P3)
    cx, cy = L.CRAFT_C
    r["DUNGEON->CRAFT"] = (dungeon_to_p2_east() + [(70.0, -46.0), (66.0, -58.0), (cx - L.CRAFT_R - 3.0, cy),
                                                   (cx - 5.0, cy)], P3)
    r["CRAFT->CASTELO"] = (rev(p2_east_to_craft()) + p2_to_forecourt()[1:] + forecourt_to_hall()[1:4], P2)
    r["VILA_BAIXA_LESTE->PRACA"] = ([(100.0, -118.0), (64.0, -120.0), (26.0, -120.0), (14.0, -130.0)], P1)
    r["PRACA_VOLTA"] = ([(0.0, -150.0), (-18.0, -140.0), (-18.0, -116.0), (0.0, -105.0), (18.0, -116.0),
                         (18.0, -140.0), (0.0, -150.0)], P1)
    # salas da dungeon (ov09b: tirado da planta): R1 -> vao -> R2 -> vao -> R3 pelo eixo dos vaos
    yc = L.DUN_LY
    pts = []
    for nm, (x0, y0, x1, y1) in L.DUN_ROOMS:
        pts += [(x0 + 8.0, yc), (x1 - 3.0, yc)]
    pts.insert(2, (L.dun_links()[0][1], yc))
    pts.insert(5, (L.dun_links()[1][1], yc))
    r["DUNGEON_SALAS_R1->R3"] = (pts, L.DUN_Z)
    return r


def open_routes():
    g = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    return {"PORTAO_DS_ABERTO->ANCORA": ([(g[0] - ux * 7.0, g[1] - uy * 7.0), g, (g[0] + ux * 12.0, g[1] + uy * 12.0),
                                          L.exit_point(L.EXIT_BRIDGE_LEN + L.ANCHOR_OFF - 1.0)], L.EXIT_Z)}


def module_routes():
    import importlib, build_sg
    rr, pp = {}, []
    for mods in build_sg.ZONE_MODULES.values():
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
    out.append(("ANCORA_DS_borda", ap[0] - ux * 1.0, ap[1] - uy * 1.0, L.EXIT_Z, ux, uy, 3.5))
    p = L.exit_point(32.0)
    out.append(("PONTE_SAIDA_lado_N", p[0], p[1], L.EXIT_Z, -uy, ux, L.EXIT_W / 2 + 3.0))
    out.append(("PONTE_SAIDA_lado_S", p[0], p[1], L.EXIT_Z, uy, -ux, L.EXIT_W / 2 + 3.0))
    out.append(("PONTE_CHEGADA_lado_O", 0.0, -245.0, L.DECK, -1.0, 0.0, L.DECK_W / 2 + 3.0))
    out.append(("PONTE_CHEGADA_lado_L", 0.0, -245.0, L.DECK, 1.0, 0.0, L.DECK_W / 2 + 3.0))
    out.append(("CALCADA_ALTA_O", 0.0, -170.0, P1, -1.0, 0.0, 16.0))
    out.append(("CALCADA_ALTA_L", 0.0, -170.0, P1, 1.0, 0.0, 16.0))
    out.append(("PATIO_BAIXO_O", 0.0, -214.0, L.DECK, -1.0, 0.0, 16.0))
    sx, sy = L.SUMMON_C
    out.append(("SUMMON_borda_O", sx, sy, SUM, -1.0, 0.0, L.SUMMON_R + 3.0))
    out.append(("SUMMON_borda_N", sx, sy, SUM, 0.0, 1.0, L.SUMMON_R + 3.0))
    a0, a1, w = L.SUMMON_BRIDGE
    out.append(("PONTE_SUMMON_N", (a0[0] + a1[0]) / 2, a0[1], P1, 0.0, 1.0, w / 2 + 3.0))
    out.append(("P2_borda_sul_O", -60.0, -76.0, P2, 0.0, -1.0, 12.0))
    out.append(("P3_borda_sul_O", -50.0, -1.0, P3, 0.0, -1.0, 12.0))
    out.append(("P2_borda_leste", 150.0, -60.0, P2, 1.0, 0.0, 14.0))
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


def db_stub():
    """cabeceira da Ilha 2 (so para o teste DB_ANCORA->SG_ENTRADA): 30 studs de tabuleiro antes de WORLD_FROM_PREV"""
    if bpy.data.objects.get("COL_QA_DBStub_001"):
        return
    ob = SL.col_box2("QA_DBStub", (-L.DECK_W / 2, L.PREV_Y - 30.0, L.DECK - 2.0), (L.DECK_W / 2, L.PREV_Y + 0.5, L.DECK))
    bpy.context.view_layer.update()
    return ob


def nav():
    db_stub()
    bvh, n = col_bvh()
    print("COL faces:", n)
    res = {}
    ok = 0
    for name, (pts, z0) in routes().items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        res[name] = f
        ok += not f
        print(("OK   " if not f else "FAIL ") + "ROTA " + name + ("" if not f else "  " + str(f)))
    print("ROTAS %d/%d OK" % (ok, len(res)))
    bvh2, _ = col_bvh(exclude=("COL_GateDemonSlayerLock",))
    ok2 = 0
    rr = open_routes()
    for name, (pts, z0) in rr.items():
        f, zend = fm_qa.walk(bvh2, pts, z0)
        ok2 += not f
        print(("OK   " if not f else "FAIL ") + "ROTA " + name + ("" if not f else "  " + str(f)))
    print("ROTAS_ABERTAS %d/%d OK" % (ok2, len(rr)))
    mr, mp = module_routes()
    ok3 = 0
    for name, (pts, z0) in mr.items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        ok3 += not f
        print(("OK   " if not f else "FAIL ") + "ROTA " + name + ("" if not f else "  " + str(f)))
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
    o = bpy.data.objects.get("COL_QA_DBStub_001")
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    return res


# ------------------------------------------------------------------ salao livre + caixa da dungeon limpa
def _box_bvh(p0, p1):
    from mathutils.bvhtree import BVHTree
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return BVHTree.FromPolygons(v, f)


def _obj_hits_box(o, p0, p1):
    """a malha do objeto encosta na caixa? (vertice dentro ou face cruzando uma face da caixa)"""
    from mathutils.bvhtree import BVHTree
    mw = o.matrix_world
    vs = [mw @ v.co for v in o.data.vertices]
    for v in vs:
        if p0[0] < v.x < p1[0] and p0[1] < v.y < p1[1] and p0[2] < v.z < p1[2]:
            return True
    xs = [v.x for v in vs]
    ys = [v.y for v in vs]
    zs = [v.z for v in vs]
    if not vs or max(xs) < p0[0] or min(xs) > p1[0] or max(ys) < p0[1] or min(ys) > p1[1] or max(zs) < p0[2] or min(zs) > p1[2]:
        return False
    t = BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons])
    return bool(t.overlap(_box_bvh(p0, p1)))


def clear():
    """(1) nada COLIDIVEL dentro da zona de minerio do salao entre piso+0,3 e piso+12 (o SpawnMinerio raycasta de +12);
    (2) nenhuma malha de fora da dungeon dentro da caixa das salas (senao aparece rocha dentro da sala)."""
    x0, y0, x1, y1 = L.MINE_RECT
    p0, p1 = (x0, y0, L.HALL + 0.3), (x1, y1, L.HALL + 12.0)
    bad = [o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("COL_") and _obj_hits_box(o, p0, p1)]
    vis = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(("COL_", "SG_Hall_", "SCALE_"))
           and not o.name.startswith("SG_Cas_") and _obj_hits_box(o, p0, p1)]
    print(("OK   " if not bad else "FAIL ") + "SALAO_LIVRE colisores na zona de minerio (piso+0,3..+12): %s" % (bad[:10] or "nenhum"))
    if vis:
        print("AVISO SALAO_LIVRE malhas visuais de outras zonas na zona de minerio: %s" % vis[:10])
    kx0, ky0, kz0, kx1, ky1, kz1 = L.DUN_KEEP_OUT
    q0, q1 = (kx0, ky0, kz0), (kx1, ky1, kz1)
    bad2 = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(("SG_Dun_", "COL_SGDun", "SCALE_"))
            and not o.name.startswith("COL_") and _obj_hits_box(o, q0, q1)]
    print(("OK   " if not bad2 else "FAIL ") + "DUNGEON_LIMPA malhas de fora dentro da caixa das salas: %s" % (bad2[:10] or "nenhuma"))
    return bad, bad2


REQUIRED = ["WORLD_FROM_PREV", "WORLD_ENTRY_ShadowGarden", "PATH_ENTRY_CENTER", "MiningZone_ShadowGarden", "SUMMON_Main",
            "SUMMON_Interact", "SUMMON_PlayerPosition", "CRAFT_Station", "PLAYER_INTERACT_Craft", "NPC_Craft",
            "DUNGEON_Entrance", "DUNGEON_Portal", "DUNGEON_UI", "DUNGEON_Return", "DUNGEON_Spawn", "DUNGEON_ExitPortal",
            "DUN_ROOM_R1", "DUN_ROOM_R2", "DUN_ROOM_R3", "DUN_SPAWN_R2", "DUN_SPAWN_R3", "DUN_LINK_R1R2",
            "DUN_LINK_R2R3", "DUN_EXIT_R1", "ISLAND_EXIT_ShadowGarden", "ISLAND_NEXT_ANCHOR_DemonSlayer",
            "GATE_DemonSlayer", "GATE_DemonSlayer_INTERACT", "GATE_DemonSlayer_LOCKED", "GATE_DemonSlayer_EXIT",
            "PURCHASE_UI_ANCHOR_DemonSlayer", "GATE_DemonSlayer_OpenFX", "AUDIO_Fountain", "AUDIO_HallAmbience"]
REQUIRED_CAMS = ["CAM_SG_Entry", "CAM_SG_Front", "CAM_SG_Left", "CAM_SG_Right", "CAM_SG_Back", "CAM_SG_BirdEye",
                 "CAM_SG_Castle", "CAM_SG_MiningHall", "CAM_SG_Summon", "CAM_SG_Craft", "CAM_SG_Dungeon",
                 "CAM_SG_ExitGate", "CAM_SG_PlayerHeight_Entry", "CAM_SG_PlayerHeight_MiningHall",
                 "CAM_SG_PlayerHeight_Summon", "CAM_SG_PlayerHeight_Craft", "CAM_SG_PlayerHeight_Dungeon",
                 "CAM_SG_PlayerHeight_ExitGate"]


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
            if math.hypot(a[0] - b[0], a[1] - b[1]) < a[2] + b[2] + 1.0:
                overl += 1
    dun = sum(1 for o in bpy.data.objects if o.name.startswith("DUN_ORE_"))
    g = bpy.data.objects.get("GATE_DemonSlayer")
    print("MARKERS faltando=%d %s" % (len(miss), miss))
    print("MARKERS minerio=%s sobrepostos=%d dungeon=%d portao_DS_area=%s" % (ores, overl, dun, g.get("area_id") if g else None))
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
    per.sort(reverse=True)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    nl = sum(1 for o in bpy.data.objects if o.type == "LIGHT" and not o.name.startswith("SUN_"))
    print("TECH nomes_genericos=%d duplicados=%d sem_material=%d transform_nao_aplicado=%d degeneradas=%d" % (
        len(bad), len(dups), len(nomat), len(scale), degen))
    print("TECH tris=%d objetos=%d malhas=%d materiais=%d colisoes=%d luzes=%d" % (
        tris, len(bpy.data.objects), sum(1 for o in bpy.data.objects if o.type == "MESH"),
        len([m for m in bpy.data.materials if m.users]), ncol, nl))
    print("TECH maiores:", per[:8])
    for lab, lst in (("genericos", bad), ("duplicados", dups), ("sem material", nomat), ("transform", scale),
                     ("pesados", heavy)):
        if lst:
            print("TECH %s: %s" % (lab, lst[:12]))
    return dict(bad=bad, dups=dups, nomat=nomat, scale=scale, degen=degen, tris=tris)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    argv = argv or ["nav", "tech", "markers", "clear"]
    if "nav" in argv:
        nav()
    if "markers" in argv:
        markers()
    if "clear" in argv:
        clear()
    if "tech" in argv:
        tech()
