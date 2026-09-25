# il_qa - testes automaticos da Ilha 1: navegacao sobre as colisoes COL_ (mesmo andador do lobby: degrau 2,3,
# queda 2,3, altura livre 6,5, corpo 1,1) + auditoria tecnica + conferencia dos marcadores obrigatorios.
# uso: blender -b ilha_naruto.blend --python il_qa.py -- [nav] [tech] [markers]   (padrao: tudo)
import sys, os, math, re, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy, bmesh
from mathutils import Vector
import il_layout as L
import fm_qa

RING_W = 71.0       # raio de caminhada no anel (entre a cerca r 60,9 e as lanternas r 79,5)


def ring_arc(a0, a1, r=RING_W, step=12.0):
    n = max(1, int(abs(a1 - a0) / step))
    return [(r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def radial(ang, r0, r1):
    a = math.radians(ang)
    return [(r0 * math.cos(a), r0 * math.sin(a)), (r1 * math.cos(a), r1 * math.sin(a))]


def ramp_path(side):
    import il_blockout as B
    top, bot, a_top = B.ramp_ends(side)
    rim = (L.PIT_R * math.cos(math.radians(a_top)), L.PIT_R * math.sin(math.radians(a_top)))
    ring = (RING_W * math.cos(math.radians(a_top)), RING_W * math.sin(math.radians(a_top)))
    dx, dy = bot[0] - top[0], bot[1] - top[1]
    ln = math.hypot(dx, dy)
    ahead = (bot[0] + dx / ln * 3.0, bot[1] + dy / ln * 3.0)     # alem do pe, no eixo da rampa
    inward = (ahead[0] * 0.78, ahead[1] * 0.78)
    return [inward, ahead, bot, top, rim, ring], a_top % 360.0


def routes():
    r = {}
    gp = L.gate_db_pos()
    ux, uy = L.exit_dir()
    gate_front = (gp[0] - ux * 7.0, gp[1] - uy * 7.0)
    ex = L.EXIT_START
    t1_to_exit = [(0.0, 112.0), (24.0, 118.0), (60.0, 120.0), (68.0, 96.0), ex]
    ne_stairs = radial(52.0, RING_W, 101.0)
    entry = [(0.0, -170.0), (0.0, -118.0), (0.0, -100.0), (0.0, -93.0), (0.0, -82.0), (0.0, -72.0)]
    r["ENTRY->MINING"] = (entry + [(0.0, -61.0), (0.0, -52.0), (0.0, -44.0), (0.0, -30.0), (0.0, -16.0)], L.G)
    r["ENTRY->SUMMON"] = (entry + ring_arc(270.0, 170.0)[1:] + radial(170.0, RING_W, 100.0)[1:] +
                          [(-112.0, 20.0), (-118.0, 26.0)], L.G)
    r["ENTRY->VILLAGE"] = (entry + ring_arc(-90.0, 90.0)[1:] + [(0.0, 83.0), (0.0, 97.0), (0.0, 110.0),
                                                                 (0.0, 116.0), (0.0, 129.0), (0.0, 135.0)], L.G)
    wr, a_top = ramp_path(-1)
    r["MINING->SUMMON"] = ([(-10.0, 4.0)] + wr + ring_arc(a_top, 170.0)[1:] + radial(170.0, RING_W, 100.0)[1:] +
                           [(-112.0, 20.0)], L.PIT)
    r["MINING->EXIT"] = ([(0.0, 16.0), (0.0, 44.0), (0.0, 52.0), (0.0, 61.0), (0.0, RING_W)] +
                         ring_arc(90.0, 52.0)[1:] + ne_stairs[1:] + [(80.0, 90.0), ex], L.PIT)
    r["VILLAGE->EXIT"] = ([(0.0, 135.0), (0.0, 129.0), (0.0, 116.0), (0.0, 110.0), (12.0, 110.0)] + t1_to_exit[1:],
                          L.T2)
    r["EXIT->GATE_DB"] = ([ex, L.exit_point(40.0), L.exit_point(80.0), L.exit_point(L.EXIT_BRIDGE_LEN + 2.0),
                           gate_front], L.EXIT_Z)
    sx, sy, sr = L.BLUE_W
    r["SHOP->MINING"] = ([(sx, sy - sr - 3.0), (sx, 134.0), (-12.0, 134.0), (0.0, 130.0), (0.0, 116.0),
                          (0.0, 108.0), (0.0, 97.0), (0.0, 83.0), (0.0, RING_W), (0.0, 61.0), (0.0, 52.0),
                          (0.0, 44.0), (0.0, 30.0)], L.T2)
    r["SUMMON->EXIT"] = ([(-112.0, 20.0)] + radial(170.0, 100.0, RING_W)[1:] + ring_arc(170.0, 52.0)[1:] +
                         ne_stairs[1:] + [(80.0, 90.0), ex, L.exit_point(30.0)], L.T1)
    # extras: ramen, moinho, rampa leste, volta do anel inteiro, ponte do lobby inteira
    rx, ry, rw, rd, _ = L.RAMEN
    r["RING->RAMEN"] = ([(0.0, RING_W)] + ring_arc(90.0, 128.0)[1:] + radial(128.0, RING_W, 100.0)[1:] +
                        [(rx, ry - rd / 2 - 3.0)], L.RING)
    mx, my, mw, md = L.MILL
    ma = math.degrees(math.atan2(my, 80.0))
    r["RING->MILL"] = (ring_arc(-40.0, ma)[0:] + [(RING_W + 8.0, my), (84.0, my), (90.0, my),
                                                  (mx - mw / 2 - 3.0, my)], L.RING)
    er, _ = ramp_path(1)
    r["PIT->EAST_RAMP->RING"] = ([(10.0, 4.0)] + er, L.PIT)
    r["RING_LOOP"] = (ring_arc(0.0, 360.0, step=6.0), L.RING)
    r["LOBBY_BRIDGE"] = ([(0.0, L.LOBBY_Y + 1.0), (0.0, -150.0), (0.0, L.ISLAND_S_Y + 2.0), (0.0, -104.0)], L.G)
    return r


def _mk_xy(name, default):
    o = bpy.data.objects.get(name)
    return (o.location.x, o.location.y) if o else default


def interior_routes():
    """porta -> ponto de interacao dos 4 predios entraveis, ponte em arco e travessia do portao DESBLOQUEADO"""
    r = {}
    r["HALL:porta->mesa"] = ([(0.0, 134.0), (0.0, 146.0), (0.0, 156.5),
                              _mk_xy("PLAYER_INTERACT_MainHall", (0.0, 162.6))], L.T2)
    sx, sy, sr = L.BLUE_W
    r["LOJA:porta->balcao"] = ([(sx, sy - sr - 3.0), (sx, sy - sr + 5.0),
                                _mk_xy("PLAYER_INTERACT_WeaponShop", (sx, sy - 0.6))], L.T2)
    rx, ry, rw, rd, _ = L.RAMEN
    r["RAMEN:frente->balcao"] = ([(rx, ry - rd / 2 - 5.0), (rx, ry - rd / 2 - 1.5),
                                  _mk_xy("PLAYER_INTERACT_Ramen", (rx, ry - 2.9))], L.T1)
    mx, my, mw, md = L.MILL
    r["MOINHO:porta->balcao"] = ([(mx - mw / 2 - 3.0, my), (mx - mw / 2 + 1.5, my),
                                  _mk_xy("PLAYER_INTERACT_Mill", (mx - 2.0, my))], L.G)
    fx, fy = L.FOOTBRIDGE
    r["PONTE_EM_ARCO"] = ([(fx - 15.0, fy + 2.5), (fx - 6.0, fy + 1.0), (fx + 6.0, fy - 1.0), (fx + 11.0, fy - 2.0)],
                          L.G)
    gp = L.gate_db_pos()
    ux, uy = L.exit_dir()
    r["PORTAO_DB_ABERTO->ANCORA"] = ([(gp[0] - ux * 7.0, gp[1] - uy * 7.0), gp, (gp[0] + ux * 12.0, gp[1] + uy * 12.0),
                                      L.exit_point(L.EXIT_BRIDGE_LEN + L.ANCHOR_OFF - 1.0)], L.EXIT_Z)
    return r


def module_routes():
    """rotas e sondas que os proprios modulos registram (EXTRA_ROUTES = {nome: (pts, z0)},
    EXTRA_PROBES = [(nome, x, y, z_piso, dx, dy)]) para as pecas novas deles (escadas, passagens)"""
    import importlib, build_ilha
    rr, pp = {}, []
    for mods in build_ilha.ZONE_MODULES.values():
        for m in mods:
            if not os.path.exists(os.path.join(HERE, m + ".py")):
                continue
            try:
                mod = importlib.import_module(m)
            except Exception as e:
                print("QA aviso: nao importou %s (%s)" % (m, e))
                continue
            for k, v in getattr(mod, "EXTRA_ROUTES", {}).items():
                rr["%s:%s" % (m, k)] = v
            pp += list(getattr(mod, "EXTRA_PROBES", []))
    return rr, pp


# sondas de borda: 1 stud alem de cada borda aberta que NAO pode ser saida (queda livre); cada uma tem que bater numa
# colisao ate 3 studs na direcao (dx, dy) a 2 studs acima do piso
PROBES = [
    ("T2_NE_fenda", 112.0, 126.5, L.T2, 1.0, -1.0),
    ("ANCORA_borda", None, None, L.EXIT_Z, None, None),      # calculada: ponta da plataforma na ancora
    ("PONTE_SAIDA_lado_N", None, None, L.EXIT_Z, None, None),
    ("PONTE_SAIDA_lado_S", None, None, L.EXIT_Z, None, None),
]


def probes(bvh, extra=()):
    from mathutils import Vector
    out = []
    ux, uy = L.exit_dir()
    for name, x, y, z, dx, dy in list(PROBES) + list(extra):
        if name == "ANCORA_borda":
            (x, y), dx, dy = L.exit_point(L.EXIT_BRIDGE_LEN + L.ANCHOR_OFF - 1.0), ux, uy
        elif name == "PONTE_SAIDA_lado_N":
            (x, y) = L.exit_point(60.0)
            dx, dy = -uy, ux
        elif name == "PONTE_SAIDA_lado_S":
            (x, y) = L.exit_point(60.0)
            dx, dy = uy, -ux
        o = Vector((x, y, z + 2.0))
        d = Vector((dx, dy, 0.0)).normalized()
        hit = bvh.ray_cast(o, d, L.EXIT_W / 2 + 3.0 if name.startswith("PONTE") else 3.5)
        ok = hit[0] is not None
        out.append((name, ok))
        print(("OK   " if ok else "FAIL ") + "SONDA " + name + ("" if ok else "  (borda aberta: nada segura o jogador)"))
    return out


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


def nav():
    bvh, n = fm_qa.col_bvh()
    print("COL faces:", n)
    res = {}
    ok = 0
    for name, (pts, z0) in routes().items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        res[name] = f
        ok += not f
        print(("OK   " if not f else "FAIL ") + name + ("" if not f else "  " + str(f)))
    print("ROTAS %d/%d OK" % (ok, len(res)))
    # rotas internas / travessias (o portao aberto: sem a colisao de bloqueio COL_Gate*Lock)
    bvh2, _ = col_bvh(exclude=("COL_GateDBLock",))
    ok2 = 0
    rr = interior_routes()
    for name, (pts, z0) in rr.items():
        use = bvh2 if "ABERTO" in name else bvh
        f, zend = fm_qa.walk(use, pts, z0)
        ok2 += not f
        print(("OK   " if not f else "FAIL ") + name + ("" if not f else "  " + str(f)))
    print("ROTAS_EXTRA %d/%d OK" % (ok2, len(rr)))
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
    # passe de LARGURA (informativo): as rotas principais com corpo de raio 1,7 (corredor >= ~3,4)
    old = fm_qa.BODY_R
    fm_qa.BODY_R = 1.7
    try:
        estreitas = [n for n, (pts, z0) in routes().items() if fm_qa.walk(bvh, pts, z0)[0]]
    finally:
        fm_qa.BODY_R = old
    print("LARGURA rotas com trecho < 3,4 de largura: %s" % (estreitas or "nenhuma"))
    return res


REQUIRED = ["WORLD_ENTRY_Naruto", "WORLD_FROM_LOBBY", "PATH_ENTRY_CENTER", "SUMMON_Main", "SUMMON_Interact",
            "SUMMON_PlayerPosition", "ISLAND_EXIT_Naruto", "ISLAND_NEXT_ANCHOR", "GATE_DB", "GATE_DB_INTERACT",
            "GATE_DB_LOCKED", "GATE_DB_EXIT", "PURCHASE_UI_ANCHOR_DB"]
REQUIRED_CAMS = ["CAM_Entry", "CAM_Center", "CAM_Front", "CAM_Left", "CAM_Right", "CAM_Back", "CAM_BirdEye",
                 "CAM_Mining", "CAM_Summon", "CAM_Village", "CAM_NextBridge", "CAM_DB_Gate"]


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
    gates = sorted(n for n in names if re.match(r"PURCHASE_UI_ANCHOR_\w+$", n))
    print("MARKERS faltando=%d %s" % (len(miss), miss))
    print("MARKERS minerio=%s sobrepostos=%d  ancoras_de_compra=%s" % (ores, overl, gates))
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
        if o.type != "MESH":
            continue
        if o.name.startswith("COL_"):
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
    print("TECH maiores:", per[:6])
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
