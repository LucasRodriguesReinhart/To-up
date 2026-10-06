# ds_qa - testes automaticos da Ilha 4: navegacao sobre as colisoes COL_ (mesmo andador do lobby e das ilhas: degrau
# 2,3, queda 2,3, altura livre 6,5, corpo 1,1) nas rotas da secao 30 do prompt (+ extras), sondas de borda,
# CLAREIRA_LIVRE (nada colidivel na MiningZone ate piso + 12), marcadores/cameras obrigatorios, auditoria tecnica,
# BUDGET (plano secao 7) e as medidas do GATE do blockout (secao 28 do prompt / PLANO secao 12).
# uso: blender -b ilha_demonslayer.blend --python ds_qa.py -- [nav] [tech] [markers] [clear] [budget] [gate]
#      (padrao: tudo)
import sys, os, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ds_lib as DL
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import ds_layout as L
import ds_col
import fm_qa

T0, T1, T2, T3, T4 = L.T0, L.T1, L.T2, L.T3, L.T4


# ------------------------------------------------------------------ navegacao
def col_bvh(exclude=()):
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


def sg_stub():
    """ilhota da Shadow Garden (so para o teste SHADOW_GATE->ENTRY): 30 de tabuleiro antes do WORLD_FROM_PREV, no
    lugar do portao DS aprovado (28 antes da ancora)"""
    if bpy.data.objects.get("COL_QA_SGStub_001"):
        return
    DL.col_box("QA_SGStub", (DL.L.DECK_W, 30.5, 2.0), (L.PREV_X, L.PREV_Y - 14.75, L.DECK - 1.0))
    bpy.context.view_layer.update()


def _probes():
    out = []
    ux, uy = L.exit_dir()
    ap = L.anchor_op_pos()
    out.append(("ANCORA_OP_guarda", ap[0] - ux * 1.0, ap[1] - uy * 1.0, T4, ux, uy, 3.5))
    for d, nm in ((28.0, "PONTE_SAIDA"),):
        p = L.exit_point(d)
        out.append((nm + "_lado_E", p[0], p[1], T4, -uy, ux, L.EXIT_W / 2 + 3.0))
        out.append((nm + "_lado_D", p[0], p[1], T4, uy, -ux, L.EXIT_W / 2 + 3.0))
    pc = L.exit_point(L.EXIT_BRIDGE_LEN + L.PIER[1] / 2)
    out.append(("CABECEIRA_lado_E", pc[0], pc[1], T4, -uy, ux, L.PIER[0] / 2 + 3.0))
    out.append(("CABECEIRA_lado_D", pc[0], pc[1], T4, uy, -ux, L.PIER[0] / 2 + 3.0))
    for y in (-80.0, -50.0, -20.0):
        z = L.DECK + (L.T0 - L.DECK) * (y - L.PREV_Y) / L.BRIDGE_IN_LEN
        out.append(("PONTE_CHEGADA_%d_O" % y, 0.0, y, z, -1.0, 0.0, L.DECK_W / 2 + 3.0))
        out.append(("PONTE_CHEGADA_%d_L" % y, 0.0, y, z, 1.0, 0.0, L.DECK_W / 2 + 3.0))
    out += [("PATIO_T0_O", -10.0, 10.0, T0, -1.0, 0.0, 20.0), ("PATIO_T0_S_borda", 16.0, 6.0, T0, 0.0, -1.0, 12.0),
            ("TRILHA_borda_bambuzal", 0.0, 64.0, T1, 1.0, 0.0, 18.0),
            ("BAMBUZAL_borda_leste", 50.0, 60.0, L.bamboo_z(50.0, 60.0), 1.0, 0.0, 30.0),
            ("VILA_BAIXA_borda_O", -110.0, 140.0, T1, -1.0, 0.0, 40.0),
            ("VILA_ALTA_borda_O", -140.0, 300.0, T2, -1.0, 0.0, 30.0),
            ("CLAREIRA_ravina_leste", 120.0, 210.0, T1, 1.0, 0.0, 30.0),
            ("SUMMON_borda_L", 190.0, 300.0, T3, 1.0, 0.0, 24.0), ("SUMMON_borda_N", 176.0, 320.0, T3, 0.0, 1.0, 24.0),
            ("SUMMON_borda_S", 176.0, 280.0, T3, 0.0, -1.0, 24.0),
            ("BERMA_borda_clareira", 60.0, 386.0, T3, 0.0, -1.0, 12.0),
            ("FORJA_borda_berma", 70.0, 436.0, T4, 0.0, -1.0, 12.0),
            ("FORJA_borda_norte", 0.0, 515.0, T4, 0.0, 1.0, 20.0),
            ("FORJA_borda_leste", 120.0, 470.0, T4, 1.0, 0.0, 20.0),
            ("SAIDA_borda_O", -112.0, 556.0, T4, -1.0, 0.0, 20.0),
            ("LAGOA_guarda", 100.0, 372.0, T1, 0.0, 1.0, 14.0),
            ("ESCADA_Summon_guarda", 140.0, 300.0, T1 + 6.0, 0.0, 1.0, 9.0)]
    return out


def probes(bvh):
    res = []
    for name, x, y, z, dx, dy, reach in _probes():
        o = Vector((x, y, z + 2.0))
        d = Vector((dx, dy, 0.0)).normalized()
        hit = bvh.ray_cast(o, d, reach)
        ok = hit[0] is not None
        res.append((name, ok))
        print(("OK   " if ok else "FAIL ") + "SONDA " + name + ("" if ok else "  (borda aberta: nada segura o jogador)"))
    return res


def nav():
    sg_stub()
    bvh, n = col_bvh()
    print("COL faces:", n)
    res = {}
    ok = 0
    R = L.routes()
    for name, (pts, z0) in R.items():
        f, zend = fm_qa.walk(bvh, pts, z0)
        res[name] = f
        ok += not f
        print(("OK   " if not f else "FAIL ") + "ROTA " + name + ("" if not f else "  " + str(f)))
    print("ROTAS %d/%d OK" % (ok, len(res)))
    # ONDA 4: rotas INTERNAS das casas visitaveis (V1 chaya e V6 casa principal), do ds_village
    try:
        import ds_village
        bad_v = ds_village.qa_run()
        nv = len(ds_village.qa_routes())
        print("ROTAS_VILA %d/%d OK" % (nv - len(bad_v), nv))
    except Exception as e:
        print("FAIL ROTAS_VILA nao rodaram: %s" % e)
    bvh2, _ = col_bvh(exclude=("COL_GateOnePieceLock",))
    f, zend = fm_qa.walk(bvh2, L.gate_open_route(), T4)
    print(("OK   " if not f else "FAIL ") + "ROTA PORTAO_OP_ABERTO->ANCORA" + ("" if not f else "  " + str(f)))
    f2, _ = fm_qa.walk(bvh, L.gate_open_route(), T4)
    print(("OK   " if f2 else "FAIL ") + "PORTAO_OP_FECHADO bloqueia a passagem: %s" % (f2[:1] if f2 else "NAO bloqueia"))
    pr = probes(bvh)
    print("SONDAS %d/%d OK" % (sum(1 for _, k in pr if k), len(pr)))
    old = fm_qa.BODY_R
    fm_qa.BODY_R = 1.7
    try:
        estreitas = [nm for nm, (pts, z0) in R.items() if fm_qa.walk(bvh, pts, z0)[0]]
    finally:
        fm_qa.BODY_R = old
    print("LARGURA rotas com trecho < 3,4 de largura: %s" % (estreitas or "nenhuma"))
    o = bpy.data.objects.get("COL_QA_SGStub_001")
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    return res


# ------------------------------------------------------------------ clareira livre
def _box_bvh(p0, p1):
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return BVHTree.FromPolygons(v, f)


def _obj_hits_box(o, p0, p1):
    mw = o.matrix_world
    vs = [mw @ v.co for v in o.data.vertices]
    for v in vs:
        if p0[0] < v.x < p1[0] and p0[1] < v.y < p1[1] and p0[2] < v.z < p1[2]:
            return True
    if not vs:
        return False
    xs = [v.x for v in vs]
    ys = [v.y for v in vs]
    zs = [v.z for v in vs]
    if max(xs) < p0[0] or min(xs) > p1[0] or max(ys) < p0[1] or min(ys) > p1[1] or max(zs) < p0[2] or min(zs) > p1[2]:
        return False
    t = BVHTree.FromPolygons(vs, [list(p.vertices) for p in o.data.polygons])
    return bool(t.overlap(_box_bvh(p0, p1)))


def clear():
    """CLAREIRA_LIVRE: nada COLIDIVEL dentro da MiningZone entre piso + 0,3 e piso + 12 (o SpawnMinerio raycasta de +12
    e testa a caixa 7 x 8 x 7); visual de outras zonas dentro da zona so como aviso; piso plano em 60,2 (raycast)"""
    x0, y0, x1, y1 = L.MINE_RECT
    p0, p1 = (x0, y0, T1 + 0.3), (x1, y1, T1 + L.CLEAR_H)
    bad = [o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("COL_") and _obj_hits_box(o, p0, p1)]
    vis = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(("COL_", "DS_Clr_", "DS_Ter_",
           "SCALE_", "PREVIEW_")) and _obj_hits_box(o, p0, p1)]
    print(("OK   " if not bad else "FAIL ") + "CLAREIRA_LIVRE colisores na MiningZone (piso+0,3..+12): %s" % (bad[:10] or "nenhum"))
    if vis:
        print("AVISO CLAREIRA_LIVRE malhas visuais de outras zonas na MiningZone: %s" % vis[:10])
    bvh, n = col_bvh()
    worst, nbad = 0.0, 0
    x = x0 + 2.0
    while x < x1:
        y = y0 + 2.0
        while y < y1:
            hit = bvh.ray_cast(Vector((x, y, T1 + 12.0)), Vector((0, 0, -1)), 30.0)
            if hit[0] is None or abs(hit[0].z - T1) > 0.5 or hit[1].z < 0.85:
                nbad += 1
            else:
                worst = max(worst, abs(hit[0].z - T1))
            y += 7.5
        x += 7.5
    print(("OK   " if nbad == 0 else "FAIL ") + "CLAREIRA_PISO raycast de +12 na grade 7,5: %d pontos fora (|piso-60,2|<0,5, "
          "normal>0,85); desvio max %.3f" % (nbad, worst))
    return bad


# ------------------------------------------------------------------ marcadores
REQUIRED = ["WORLD_FROM_PREV", "WORLD_ENTRY_DemonSlayer", "PATH_ENTRY_CENTER", "MiningZone_DemonSlayer",
            "SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition", "ISLAND_EXIT_DemonSlayer",
            "ISLAND_NEXT_ANCHOR_OnePiece", "GATE_OnePiece", "GATE_OnePiece_INTERACT", "GATE_OnePiece_LOCKED",
            "GATE_OnePiece_EXIT", "GATE_OnePiece_OpenFX", "PURCHASE_UI_ANCHOR_OnePiece", "COL_GateOnePieceLock_001",
            "COL_DSAnchorGuard_001", "DS_Exit_AnchorGuard",
            "SAFE_Entrada", "SAFE_Ponte_Chegada", "SAFE_Trilha", "SAFE_Vila_Baixa", "SAFE_Vila_Alta", "SAFE_Clareira_S",
            "SAFE_Clareira_N", "SAFE_Summon", "SAFE_Patamar", "SAFE_Forja_Patio", "SAFE_Patio_Carvao", "SAFE_Saida",
            "SAFE_Cabeceira",
            "AUDIO_Forge", "AUDIO_Waterwheel", "AUDIO_Cascade", "AUDIO_Pond", "AUDIO_Bamboo", "AUDIO_Summon",
            "AUDIO_Clearing", "AUDIO_Village",
            "FX_Fall_1_Lip", "FX_Fall_1_Step", "FX_Fall_1_Base", "FX_Fall_2_Lip", "FX_Fall_2_Base", "FX_Forge_Smoke",
            "FX_Forge_Embers", "FX_Forge_Smoke_Vent", "FX_Mist_Bamboo", "FX_Mist_Ravine", "WATER_Pond", "WATER_Flume", "WATER_Tailrace",
            "WATER_Channel", "VFX_DS_Wheel"]
REQUIRED_CAMS = list(L.cams().keys())


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
    x0, y0, x1, y1 = L.MINE_RECT
    fora = [n for x, y, r, n in pts if not (x0 < x < x1 and y0 < y < y1)]
    overl = 0
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            a, b = pts[i], pts[j]
            if math.hypot(a[0] - b[0], a[1] - b[1]) < a[2] + b[2] + 1.0:
                overl += 1
    gp = {}
    for o in bpy.data.objects:
        if o.name.startswith("GP_Block_"):
            gp[o.get("kind")] = gp.get(o.get("kind"), 0) + 1
    g = bpy.data.objects.get("GATE_OnePiece")
    wp = bpy.data.objects.get("WORLD_FROM_PREV")
    print("MARKERS faltando=%d %s" % (len(miss), miss))
    print("MARKERS minerio=%s total=%d fora_da_zona=%d sobrepostos=%d GP_Block=%s portao_OP_area=%s" % (
        ores, len(pts), len(fora), overl, gp, g.get("area_id") if g else None))
    nmk = sum(1 for o in bpy.data.objects if o.type == "EMPTY" and o.users_collection
              and o.users_collection[0].name == "14_GAMEPLAY_MARKERS")
    print("MARKERS total na colecao 14_GAMEPLAY_MARKERS: %d" % nmk)
    if wp:
        r = L.to_roblox(wp.location.x, wp.location.y, wp.location.z)
        d = math.dist((r[0], r[1], r[2]), L.A_RBX)
        print(("OK   " if d < 1e-3 else "FAIL ") + "ENCAIXE WORLD_FROM_PREV -> Roblox (%.3f, %.3f, %.3f) vs ancora (%.3f, %.3f, "
              "%.3f): %.4f" % (r + tuple(L.A_RBX) + (d,)))
    return miss


# ------------------------------------------------------------------ tecnico
def tech():
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh|Empty|Camera|Light)(\.\d+)?$")
    dup = re.compile(r".+\.\d{3}$")
    bad, dups, nomat, scale, degen, tris, per = [], [], [], [], 0, 0, []
    for o in bpy.data.objects:
        if gen.match(o.name):
            bad.append(o.name)
        if dup.match(o.name):
            dups.append(o.name)
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_")):
            continue
        me = o.data
        t = sum(len(p.vertices) - 2 for p in me.polygons)
        tris += t
        per.append((t, o.name))
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
    for lab, lst in (("genericos", bad), ("duplicados", dups), ("sem material", nomat), ("transform", scale)):
        if lst:
            print("TECH %s: %s" % (lab, lst[:12]))
    return dict(bad=bad, dups=dups, nomat=nomat, scale=scale, degen=degen, tris=tris)


# ------------------------------------------------------------------ orcamento (PLANO secao 7)
BUDGET_ISLAND = {"static_tris": 600000, "static_meshes": 650, "vfx_tris": 15000, "vfx_meshes": 30, "materials": 110,
                 "day_lights": 36, "col": 1300}


def budget():
    import studio_ds
    st, sm, vt, vm, mats = 0, 0, 0, 0, set()
    per = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "DS_Clr_OreProxy")):
            continue
        if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
            continue
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        m = studio_ds.est_meshparts(o)
        own = studio_ds.owner_of(o.name)
        a = per.setdefault(own, [0, 0])
        a[0] += t
        a[1] += m
        for mt in o.data.materials:
            if mt:
                mats.add(mt.name)
        if o.name.startswith("VFX_"):
            vt += t
            vm += m
        else:
            st += t
            sm += m
    nl = sum(1 for o in bpy.data.objects if o.type == "LIGHT" and not o.name.startswith("SUN_")
             and not o.name.startswith(("L_DSProp_",)))
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    B = BUDGET_ISLAND
    for lab, v, lim in (("static_tris", st, B["static_tris"]), ("static_meshes~", sm, B["static_meshes"]),
                        ("vfx_tris", vt, B["vfx_tris"]), ("vfx_meshes~", vm, B["vfx_meshes"]),
                        ("materials", len(mats), B["materials"]), ("day_lights", nl, B["day_lights"]),
                        ("col", ncol, B["col"])):
        print(("OK   " if v <= lim else "FAIL ") + "BUDGET %-15s %7d / %d" % (lab, v, lim))
    for k in sorted(per):
        print("BUDGET dono %-11s tris %7d  MeshParts~ %4d" % (k, per[k][0], per[k][1]))
    return st, sm


# ------------------------------------------------------------------ gate do blockout (medidas)
VIS_OWNER = []


def vis_bvh():
    verts, polys = [], []
    VIS_OWNER.clear()
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "SCALE_", "PREVIEW_CloudSea", "PREVIEW_Moon")) or o.hide_render:
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        polys += [[base + i for i in p.vertices] for p in o.data.polygons]
        VIS_OWNER.extend([o.name] * len(o.data.polygons))
    return BVHTree.FromPolygons(verts, polys)


def _zmax(prefixes=None, exclude=()):
    best = (-1e9, None)
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "SCALE_", "PREVIEW_")) or o.name.startswith(exclude):
            continue
        if prefixes and not o.name.startswith(prefixes):
            continue
        mw = o.matrix_world
        z = max((mw @ v.co).z for v in o.data.vertices)
        if z > best[0]:
            best = (z, o.name)
    return best


def gate():
    """medidas do GATE (PLANO secao 12): landmark, summon, forma, camera do jogador, visadas"""
    print("GATE forma: topo %.0f x %.0f (razao %.2f, meta >= 1,5) | clareira razao %.2f (meta >= 1,4) | area %.0f" % (
        max(p[1] for p in L.RIM_CTRL) - min(p[1] for p in L.RIM_CTRL), max(p[0] for p in L.RIM_CTRL) - min(p[0] for p in L.RIM_CTRL),
        (max(p[1] for p in L.RIM_CTRL) - min(p[1] for p in L.RIM_CTRL)) / (max(p[0] for p in L.RIM_CTRL) - min(p[0] for p in L.RIM_CTRL)),
        (max(p[1] for p in L.CLEARING) - min(p[1] for p in L.CLEARING)) / (max(p[0] for p in L.CLEARING) - min(p[0] for p in L.CLEARING)),
        L.area(L.CLEARING)))
    zf, nf = _zmax(("DS_Frg_",))
    zo, no = _zmax(None, exclude=("DS_Frg_",))
    zs, ns = _zmax(("DS_Sum_", "VFX_DSSUM_"))
    print(("OK   " if zf - zo >= 20.0 else "FAIL ") + "GATE landmark: chamine %.1f (%s) vs mais alto de fora da forja %.1f "
          "(%s): margem %.1f (meta >= 20)" % (zf, nf, zo, no, zf - zo))
    print(("OK   " if zs < zf else "FAIL ") + "GATE summon: topo %.1f (%s) abaixo da chamine %.1f" % (zs, ns, zf))
    bvh = vis_bvh()
    chim = Vector((L.CHIMNEY[0], L.CHIMNEY[1], L.CHIMNEY_TOP - 0.6))
    mouth = Vector((L.FURNACE_MOUTH[0], L.FURNACE_MOUTH[1] - 2.2, L.T4 + 6.0))     # centro da boca acesa (10 x 9)
    tower_pts = [chim, Vector((L.CHIMNEY[0], L.CHIMNEY[1], L.T4 + 56.0)), Vector((L.CHIMNEY[0], L.CHIMNEY[1] - 7.6, L.T4 + 46.0)),
                 Vector((L.CHIMNEY[0] - 7.6, L.CHIMNEY[1] - 7.6, L.T4 + 40.0))]
    star = None
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name == "L_DSSum_Star":
            star = o.location.copy()
    tower_c = Vector((L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], T3 + 30.0))

    blocker = {}

    def visible(eye, tgt, tol=3.0):
        d = tgt - eye
        hit = bvh.ray_cast(eye, d.normalized(), d.length)
        ok = hit[0] is None or (hit[0] - eye).length >= d.length - tol
        if not ok:
            blocker["last"] = "%s a %.0f" % (VIS_OWNER[hit[2]], (hit[0] - eye).length)
        return ok
    cams = L.cams()
    for cn in L.PLAYER_CAMS:
        loc, tgt, lens = cams[cn]
        eye = Vector(loc)
        fwd = (Vector(tgt) - eye).normalized()
        near = bvh.find_nearest(eye, 2.0)
        ray = bvh.ray_cast(eye, fwd, 12.0)
        occl = near[0] is not None or ray[0] is not None
        msg = []
        for lab, p in (("chamine", chim), ("boca", mouth), ("estrela_summon", star), ("torre_summon", tower_c)):
            if p is not None:
                vis = visible(eye, p)
                ang = math.degrees(fwd.angle(p - eye))
                msg.append("%s %s(%.0fg)" % (lab, "V" if vis else "-", ang))
        print(("OK   " if not occl else "FAIL ") + "GATE camera %-34s oclusao<12: %s | %s" % (
            cn, "nenhuma" if not occl else "SIM (%s)" % (("perto %.1f" % (near[0] - eye).length) if near[0] else
                                                       ("raio %.1f" % (ray[0] - eye).length)), "  ".join(msg)))
    # pedidos do criterio: forja visivel da entrada e da clareira; boca do antecampo; summon da trilha e da clareira
    for cn in ("CAM_DS_PlayerHeight_Entry", "CAM_DS_PlayerHeight_Clearing", "CAM_DS_PlayerHeight_Village"):
        eye = Vector(cams[cn][0])
        vis = [visible(eye, p) for p in tower_pts]
        print(("OK   " if any(vis) else "FAIL ") + "GATE visada torre-chamine (silhueta) de %s: %d/%d pontos (chamine, chapeu, "
              "topo do corpo, quina)%s" % (cn, sum(vis), len(vis), "" if all(vis) else "  (bloqueio: %s)" % blocker.get("last")))
    checks = [("chamine da PlayerHeight_Clearing", cams["CAM_DS_PlayerHeight_Clearing"][0], chim),
              ("boca da fornalha do antecampo (0,150)", (0.0, 150.0, T1 + L.EYE), mouth),
              ("boca da fornalha do centro da clareira", (L.MINE_C[0], L.MINE_C[1], T1 + L.EYE), mouth),
              ("summon (estrela) do topo da Trilha (-12,58)", (-12.0, 58.0, T1 + L.EYE), star),
              ("summon (estrela) da clareira (30,200)", (30.0, 200.0, T1 + L.EYE), star),
              ("portao OP da cabeca da ponte de saida", (L.EXIT_START[0], L.EXIT_START[1] - 4.0, T4 + L.EYE),
               Vector((L.gate_op_pos()[0], L.gate_op_pos()[1], T4 + 12.0)))]
    nok = 0
    for lab, eye, p in checks:
        if p is None:
            continue
        v = visible(Vector(eye), p)
        nok += v
        print(("OK   " if v else "FAIL ") + "GATE visada %s%s" % (lab, "" if v else "  (bloqueada: %s)" % blocker.get("last")))
    return nok


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    argv = argv or ["nav", "tech", "markers", "clear", "budget", "gate"]
    if "nav" in argv:
        nav()
    if "markers" in argv:
        markers()
    if "clear" in argv:
        clear()
    if "tech" in argv:
        tech()
    if "budget" in argv:
        budget()
    if "gate" in argv:
        gate()
