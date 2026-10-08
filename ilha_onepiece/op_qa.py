# op_qa - testes automaticos da Ilha 5 (ONE PIECE / WANO): navegacao sobre as colisoes COL_ (mesmo andador do lobby e
# das ilhas: degrau 2,3, queda 2,3, altura livre 6,5, corpo 1,1) nas rotas da planta (+ portao aberto/fechado), sondas
# de borda, PRACA_LIVRE (nada colidivel na MiningZone ate piso + 12) + PRACA_PISO (raycast plano a 92,2), marcadores e
# cameras obrigatorios, encaixe 0,000, auditoria tecnica, BUDGET (PLANO_OP secao 9) e as medidas do GATE do blockout.
# uso: blender -b ilha_onepiece.blend --python op_qa.py -- [nav] [tech] [markers] [clear] [budget] [gate]
#      (padrao: tudo)
import sys, os, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import op_lib as DL
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import op_layout as L
import op_col
import fm_qa

T0, T1, P, CF, CC = L.T0, L.T1, L.P, L.CF, L.CC


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


def ds_stub():
    """cabeceira da Demon Slayer (so para o teste DS_GATE->ENTRY): 30 de tabuleiro antes do WORLD_FROM_PREV, no lugar
    do trecho portao One Piece -> ancora da DS"""
    if bpy.data.objects.get("COL_QA_DSStub_001"):
        return
    DL.col_box("QA_DSStub", (L.DECK_W, 30.5, 2.0), (L.PREV_X, L.PREV_Y - 14.75, L.DECK - 1.0))
    bpy.context.view_layer.update()


def _probes():
    out = []
    ux, uy = L.exit_dir()
    ap = L.anchor_opm_pos()
    out.append(("ANCORA_OPM_guarda", ap[0] - ux * 2.0, ap[1] - uy * 2.0, T1, ux, uy, 4.0))
    for d, nm in ((44.0, "PONTE_SAIDA"),):
        p = L.exit_point(d)
        out.append((nm + "_lado_E", p[0], p[1], T1, -uy, ux, L.EXIT_W / 2 + 3.0))
        out.append((nm + "_lado_D", p[0], p[1], T1, uy, -ux, L.EXIT_W / 2 + 3.0))
    for y in (-90.0, -60.0, -30.0):
        z = L.DECK + (L.T0 - L.DECK) * (y - L.PREV_Y) / L.BRIDGE_IN_LEN
        out.append(("PONTE_CHEGADA_%d_O" % y, 0.0, y, z, -1.0, 0.0, L.DECK_W / 2 + 3.0))
        out.append(("PONTE_CHEGADA_%d_L" % y, 0.0, y, z, 1.0, 0.0, L.DECK_W / 2 + 3.0))
    out += [("PATIO_TORII_O", -10.0, 12.0, T0, -1.0, 0.0, 22.0), ("PATIO_TORII_L", 10.0, 12.0, T0, 1.0, 0.0, 22.0),
            ("RUA_CHEGADA_frente_SO", -100.0, 60.0, T1, 0.0, -1.0, 40.0),
            ("PRACA_S_sobre_rua", 40.0, 124.0, P, 0.0, -1.0, 10.0),
            ("PRACA_L_sobre_summon", 110.0, 190.0, P, 1.0, 0.0, 12.0),
            ("CANAL_O_margem_praca", -160.0, 220.0, P, -1.0, 0.0, 16.0),
            ("CANAL_O_margem_alem", -186.0, 220.0, P, 1.0, 0.0, 16.0),
            ("ADRO_bacia", 0.0, 330.0, CF, 0.0, 1.0, 10.0), ("ADRO_canal_L", 60.0, 334.0, CF, 0.0, 1.0, 10.0),
            ("PATIO_CASTELO_varanda", 0.0, 362.0, CC, 0.0, -1.0, 16.0),
            ("PATIO_CASTELO_oeste", -84.0, 450.0, CC, -1.0, 0.0, 12.0),
            ("TERRACO_ALTO_oeste", -200.0, 360.0, L.W3, -1.0, 0.0, 30.0),
            ("SUMMON_borda_porto", 190.0, 200.0, T1, 1.0, 0.0, 22.0),
            ("SUMMON_borda_sul", 180.0, 156.0, T1, 0.0, -1.0, 12.0),
            ("CAIS_borda_agua", 214.0, 230.0, L.HARBOR, 1.0, 0.0, 16.0),
            ("PIER_borda", 228.0, 180.0, L.HARBOR, 1.0, 0.0, 12.0),
            ("NAVIO_amurada", 248.0, 170.0, L.SHIP, 1.0, 0.0, 14.0),
            ("PROMONTORIO_borda_S", L.exit_point(110.0, -20.0)[0], L.exit_point(110.0, -20.0)[1], T1, uy, -ux, 16.0),
            ("ESCADA_PortoA_guarda", 180.0, 140.0, L.HMID + 8.0, 0.0, -1.0, 10.0)]
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
    ds_stub()
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
    bvh2, _ = col_bvh(exclude=("COL_GateOnePunchManLock",))
    f, zend = fm_qa.walk(bvh2, L.gate_open_route(), T1)
    print(("OK   " if not f else "FAIL ") + "ROTA PORTAO_OPM_ABERTO->ANCORA" + ("" if not f else "  " + str(f)))
    f2, _ = fm_qa.walk(bvh, L.gate_open_route(), T1)
    print(("OK   " if f2 else "FAIL ") + "PORTAO_OPM_FECHADO bloqueia a passagem: %s" % (f2[:1] if f2 else "NAO bloqueia"))
    ap = L.anchor_opm_pos()
    ux, uy = L.exit_dir()
    f3, _ = fm_qa.walk(bvh2, [(ap[0] - ux * 6.0, ap[1] - uy * 6.0), (ap[0] + ux * 6.0, ap[1] + uy * 6.0)], T1)
    print(("OK   " if f3 else "FAIL ") + "TERMINO_SEGURO ancora OPM fechada pela guarda provisoria: %s" % (
        f3[:1] if f3 else "NAO fecha (passagem para a queda!)"))
    pr = probes(bvh)
    print("SONDAS %d/%d OK" % (sum(1 for _, k in pr if k), len(pr)))
    old = fm_qa.BODY_R
    fm_qa.BODY_R = 1.7
    try:
        estreitas = [nm for nm, (pts, z0) in R.items() if fm_qa.walk(bvh, pts, z0)[0]]
    finally:
        fm_qa.BODY_R = old
    print("LARGURA rotas com trecho < 3,4 de largura: %s" % (estreitas or "nenhuma"))
    o = bpy.data.objects.get("COL_QA_DSStub_001")
    if o:
        bpy.data.objects.remove(o, do_unlink=True)
    return res


# ------------------------------------------------------------------ praca livre
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
    """PRACA_LIVRE: nada COLIDIVEL dentro da MiningZone entre piso + 0,3 e piso + 12; malha visual de outra zona dentro
    da zona acima de piso + 0,3 = aviso (o emblema fica a +0,24: rente); piso plano em 92,2 (raycast de +12)"""
    x0, y0, x1, y1 = L.MINE_RECT
    p0, p1 = (x0, y0, P + 0.3), (x1, y1, P + L.CLEAR_H)
    bad = [o.name for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("COL_") and _obj_hits_box(o, p0, p1)]
    vis = [o.name for o in bpy.data.objects if o.type == "MESH" and not o.name.startswith(("COL_", "OP_Ter_",
           "SCALE_", "PREVIEW_", "OP_Plz_OreProxy")) and _obj_hits_box(o, p0, p1)]
    print(("OK   " if not bad else "FAIL ") + "PRACA_LIVRE colisores na MiningZone (piso+0,3..+12): %s" % (bad[:10] or "nenhum"))
    print(("OK   " if not vis else "AVISO ") + "PRACA_LIVRE malhas visuais na MiningZone acima de +0,3: %s" % (vis[:10] or "nenhuma"))
    bvh, n = col_bvh()
    worst, nbad = 0.0, 0
    x = x0 + 2.0
    while x < x1:
        y = y0 + 2.0
        while y < y1:
            hit = bvh.ray_cast(Vector((x, y, P + 12.0)), Vector((0, 0, -1)), 30.0)
            if hit[0] is None or abs(hit[0].z - P) > 0.5 or hit[1].z < 0.85:
                nbad += 1
            else:
                worst = max(worst, abs(hit[0].z - P))
            y += 7.5
        x += 7.5
    print(("OK   " if nbad == 0 else "FAIL ") + "PRACA_PISO raycast de +12 na grade 7,5: %d pontos fora (|piso-92,2|<0,5, "
          "normal>0,85); desvio max %.3f" % (nbad, worst))
    return bad


# ------------------------------------------------------------------ marcadores
REQUIRED = ["WORLD_FROM_PREV", "WORLD_ENTRY_OnePiece", "PATH_ENTRY_CENTER", "MiningZone_OnePiece",
            "SUMMON_Main", "SUMMON_Interact", "SUMMON_PlayerPosition", "ISLAND_EXIT_OnePiece",
            "ISLAND_NEXT_ANCHOR_OnePunchMan", "GATE_OnePunchMan", "GATE_OnePunchMan_INTERACT", "GATE_OnePunchMan_LOCKED",
            "GATE_OnePunchMan_EXIT", "GATE_OnePunchMan_OpenFX", "PURCHASE_UI_ANCHOR_OnePunchMan",
            "COL_GateOnePunchManLock_001", "COL_OPAnchorGuard_001", "OP_Exit_AnchorGuard",
            "SAFE_Entrada", "SAFE_Ponte_Chegada", "SAFE_Rua_Chegada", "SAFE_Praca_S", "SAFE_Praca_N", "SAFE_Praca_O",
            "SAFE_Praca_L", "SAFE_Summon", "SAFE_Bairro_Canal", "SAFE_Oeste_Alem", "SAFE_Terraco_Alto", "SAFE_Adro",
            "SAFE_Castelo", "SAFE_Porto_Alto", "SAFE_Cais", "SAFE_NE", "SAFE_Promontorio",
            "AUDIO_Plaza", "AUDIO_Street", "AUDIO_CastleFall", "AUDIO_FallE", "AUDIO_FallW", "AUDIO_Wheel",
            "AUDIO_Harbor", "AUDIO_Summon", "AUDIO_Castle",
            "FX_Fall_Castle_Lip", "FX_Fall_Castle_Base", "FX_Fall_E_Lip", "FX_Fall_E_Base", "FX_Fall_W_Lip",
            "FX_Fall_W_Base", "FX_Weir_E", "FX_Weir_W", "FX_Petals_Tree", "FX_Mist_CastleFall", "FX_Spring_W",
            "WATER_Sea", "WATER_Basin", "WATER_CanalE", "WATER_CanalW", "VFX_OP_Wheel"]
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
    g = bpy.data.objects.get("GATE_OnePunchMan")
    wp = bpy.data.objects.get("WORLD_FROM_PREV")
    print("MARKERS faltando=%d %s" % (len(miss), miss))
    print("MARKERS minerio=%s total=%d fora_da_zona=%d sobrepostos=%d GP_Block=%s portao_OPM_area=%s" % (
        ores, len(pts), len(fora), overl, gp, g.get("area_id") if g else None))
    nmk = sum(1 for o in bpy.data.objects if o.type == "EMPTY" and o.users_collection
              and o.users_collection[0].name == "14_GAMEPLAY_MARKERS")
    print("MARKERS total na colecao 14_GAMEPLAY_MARKERS: %d" % nmk)
    if wp:
        r = L.to_roblox(wp.location.x, wp.location.y, wp.location.z)
        d = math.dist((r[0], r[1], r[2]), L.A_RBX)
        f = (wp.matrix_world.to_3x3() @ Vector((0.0, 1.0, 0.0))).normalized()
        fr = L.dir_to_roblox(f.x, f.y)
        print(("OK   " if d < 1e-3 else "FAIL ") + "ENCAIXE WORLD_FROM_PREV -> Roblox (%.3f, %.3f, %.3f) vs ancora DS (%.3f, %.3f, "
              "%.3f): %.4f | frente (%.4f, %.4f) vs (%.4f, %.4f)" % (r + tuple(L.A_RBX) + (d, fr[0], fr[2], L.A_FWD[0], L.A_FWD[2])))
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
    cnt = {}
    for o in bpy.data.objects:
        if o.name.startswith("COL_"):
            k = re.sub(r"_\d{3}$", "", o.name)
            k = re.sub(r"(HouseX?)[A-Z]\d$", r"\1*", k)
            cnt[k] = cnt.get(k, 0) + 1
    print("TECH colisoes por area: %s" % sorted(cnt.items(), key=lambda t: -t[1])[:12])
    return dict(bad=bad, dups=dups, nomat=nomat, scale=scale, degen=degen, tris=tris)


# ------------------------------------------------------------------ orcamento (PLANO_OP secao 9)
BUDGET_ISLAND = {"static_tris": 640000, "static_meshes": 650, "vfx_tris": 15000, "vfx_meshes": 30, "materials": 110,
                 "day_lights": 36, "col": 1300}


def budget():
    import studio_op
    st, sm, vt, vm, mats = 0, 0, 0, 0, set()
    per = {}
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "OP_Plz_OreProxy")):
            continue
        if o.users_collection and o.users_collection[0].name in ("00_REFERENCE", "_SCALE_REFERENCE"):
            continue
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        m = studio_op.est_meshparts(o)
        own = studio_op.owner_of(o.name)
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
             and not o.name.startswith(("L_OPProp_", "L_OPCap_Win_")))
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
        if o.type != "MESH" or o.name.startswith(("COL_", "SCALE_", "PREVIEW_", "OP_Plz_OreProxy")) or o.hide_render:
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
    """medidas do GATE do blockout (PLANO_OP secao 13)"""
    lx = [q[0] for q in L.RIM_CTRL]
    ly = [q[1] for q in L.RIM_CTRL]
    print("GATE forma: topo %.0f x %.0f, area %.0f (DS 153k) | praca %.0f studs2 | MiningZone %.0f x %.0f" % (
        max(lx) - min(lx), max(ly) - min(ly), L.area(L.ISLAND_RIM), L.area(L.PLAZA), L.MINE_RECT[2] - L.MINE_RECT[0],
        L.MINE_RECT[3] - L.MINE_RECT[1]))
    zt, nt = _zmax(("OP_Tree_",))
    zk, nk = _zmax(("OP_Cas_Blockout", "OP_Cas_Keep"))   # M3 op_castle (acrescimo pontual): torre do modulo de detalhe
    zo, no = _zmax(None, exclude=("OP_Tree_", "OP_Cas_", "OP_Lmk_"))
    zs, ns = _zmax(("OP_Sum_", "VFX_OPSUM_"))
    zw, nw = _zmax(("OP_Lmk_",))
    print(("OK   " if zt > zk > zo else "FAIL ") + "GATE marco: arvore %.1f > castelo %.1f > resto da cidade %.1f (%s)" % (
        zt, zk, zo, no))
    print(("OK   " if zs < zk else "FAIL ") + "GATE summon: topo %.1f (%s) abaixo do castelo %.1f" % (zs, ns, zk))
    print(("OK   " if zw < zt else "FAIL ") + "GATE secundarios: caveira/espada/pagode ate %.1f (%s), abaixo da arvore" % (zw, nw))
    bvh = vis_bvh()
    keep_top = Vector((L.KEEP_C[0], L.KEEP_C[1], L.KEEP_TOP_Z + 2.0))        # acima da cumeeira (silhueta)
    tree_top = Vector((L.TREE_TRUNK[8][0], L.TREE_TRUNK[8][1], L.TREE_TRUNK[8][2] + L.TREE_TRUNK[8][3] + 3.0))
    star = None
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.name == "L_OPSum_Star":
            star = o.location.copy()
    fall = Vector((L.CASTLE_FALL[0], L.CASTLE_FALL[1] - 1.0, L.CASTLE_FALL[2] - 4.0))   # terco de cima da queda
    ship = Vector((L.SHIP_C[0], L.SHIP_C[1] + 10.0, L.SHIP + 40.0))
    gopm = Vector((L.gate_opm_pos()[0], L.gate_opm_pos()[1], T1 + 12.0))
    blocker = {}

    def visible(eye, tgt, tol=3.0):
        if tgt is star:
            tol = 10.5                                   # a estrela fica DENTRO da esfera armilar (gaiola r 9,2)
        d = tgt - eye
        hit = bvh.ray_cast(eye, d.normalized(), d.length)
        ok = hit[0] is None or (hit[0] - eye).length >= d.length - tol
        if not ok and tgt is tree_top and VIS_OWNER[hit[2]].startswith("OP_Tree_"):
            ok = True          # M3 op_tree (acrescimo pontual): o raio bate na PROPRIA arvore = arvore visivel
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
        for lab, p in (("torre", keep_top), ("arvore", tree_top), ("estrela", star)):
            if p is not None:
                msg.append("%s %s(%.0fg)" % (lab, "V" if visible(eye, p) else "-", math.degrees(fwd.angle(p - eye))))
        print(("OK   " if not occl else "FAIL ") + "GATE camera %-30s oclusao<12: %s | %s" % (
            cn, "nenhuma" if not occl else "SIM (%s)" % (("perto %.1f" % (near[0] - eye).length) if near[0] else
                                                       ("raio %.1f" % (ray[0] - eye).length)), "  ".join(msg)))
    checks = [("castelo (torre) do inicio da ponte de chegada (0,-100)", (0.0, -100.0, L.DECK + 0.6 + L.EYE), keep_top),
              ("arvore arqueada do inicio da ponte de chegada (0,-100)", (0.0, -100.0, L.DECK + 0.6 + L.EYE), tree_top),
              ("castelo do patio do torii (0,24)", (0.0, 24.0, T0 + L.EYE), keep_top),
              ("arvore arqueada do patio do torii (0,24)", (0.0, 24.0, T0 + L.EYE), tree_top),
              ("castelo do topo da escada Praca (0,124)", (0.0, 124.0, P + L.EYE), keep_top),
              ("cachoeira do castelo do centro da praca", (L.MINE_C[0], L.MINE_C[1], P + L.EYE), fall),
              ("estrela do summon do centro da praca", (L.MINE_C[0], L.MINE_C[1], P + L.EYE), star),
              ("estrela do summon da rua de chegada (0,100)", (0.0, 100.0, T1 + L.EYE), star),
              ("mastros do navio do terraco do summon", (160.0, 180.0, T1 + L.EYE), ship),
              ("portao OPM da cabeca da ponte de saida", (L.EXIT_START[0] - 4.0, L.EXIT_START[1], T1 + L.EYE), gopm)]
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
