# vm_qa - QA do lobby Vila Medieval sobre o .blend montado:
#   nav     rotas do andador (fm_qa.walk: degrau <= 2,3, queda <= 2,3, teto >= 6,5, corpo livre r 1,1) sobre as COL_,
#           com comprimento e TEMPO A PE (WalkSpeed 16) - meta <= ~15 s do spawn ate cada funcao
#   env     envoltoria do Ignis (nada da forja dentro: malha exportada nem COL), chao livre e plano em 7 diante dele,
#           envoltoria do GlobalTop100 livre
#   link    encaixe da ponte na praca de chegada da Ilha 1 (Roblox z 222, piso 6, x +-12)
#   markers marcadores de contrato presentes
#   budget  estimativa de tris / MeshParts por dono (a medida EXATA e a do export: run.sh export)
#   tech    nomes genericos, malhas sem material, faces degeneradas
# uso: blender -b --factory-startup lobby_vila_medieval.blend --python vm_qa.py -- [nav] [env] [link] [markers]
#      [budget] [tech] [--json <arquivo>]
import sys, os, math, json, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vm_lib as VL
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import vm_layout as L
import fm_qa

OUT = {}


def _bvh_obj(o):
    mw = o.matrix_world
    vs = [mw @ v.co for v in o.data.vertices]
    ps = [list(p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(vs, ps) if ps else None, vs


def nav():
    bvh, n = fm_qa.col_bvh()
    res = {}
    print("COL faces:", n)
    for name, (pts, y0) in L.routes().items():
        bp = [(x, -z) for x, z in pts]
        f, zend = fm_qa.walk(bvh, bp, y0)
        ln = VL.path_len(pts)
        t = ln / L.WALK
        ok = not f
        res[name] = {"ok": ok, "len": round(ln, 1), "s": round(t, 1), "fail": [list(map(str, x)) for x in f],
                     "y_end": round(zend, 2)}
        print("ROTA %-30s %s  %6.1f studs  %5.1f s%s%s" % (name, "OK  " if ok else "FAIL", ln, t,
                                                          "" if t <= 15.0 else "  <-- > 15 s",
                                                          "" if ok else "  " + str(f)))
    OUT["nav"] = res
    return res


def _export_meshes():
    obs = []
    for g in VL.EXPORT_GROUPS:
        c = bpy.data.collections.get(g)
        if c:
            obs += [o for o in c.all_objects if o.type == "MESH" and not o.name.startswith(("COL_", "SCALE_", "QA_",
                                                                                              "PREVIEW_"))]
    return obs


def _intrusions(vol, shrink=0.06, include_col=True, skip=()):
    """objetos (malhas exportadas e COL_) que invadem o volume 'vol' (encolhido 'shrink' de cada lado)"""
    mw = vol.matrix_world
    inv = mw.inverted()
    lo = Vector([min(v.co[i] for v in vol.data.vertices) for i in range(3)]) + Vector((shrink,) * 3)
    hi = Vector([max(v.co[i] for v in vol.data.vertices) for i in range(3)]) - Vector((shrink,) * 3)
    # volume encolhido como malha (8 cantos) para o teste de triangulos
    import itertools
    corners = [mw @ Vector((x, y, z)) for x, y, z in itertools.product((lo.x, hi.x), (lo.y, hi.y), (lo.z, hi.z))]
    faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    vb = BVHTree.FromPolygons(corners, faces)
    cand = _export_meshes() + ([o for o in bpy.data.objects if o.name.startswith("COL_")] if include_col else [])
    hits = []
    for o in cand:
        if o.name.startswith(skip):
            continue
        b, vs = _bvh_obj(o)
        if b is None:
            continue
        inside = 0
        for v in vs:
            q = inv @ v
            if lo.x < q.x < hi.x and lo.y < q.y < hi.y and lo.z < q.z < hi.z:
                inside += 1
        cross = len(b.overlap(vb))
        # caixa (COL) que ENVOLVE o volume inteiro: centro do volume dentro da caixa
        if o.name.startswith("COL_"):
            c = mw @ ((lo + hi) / 2)
            ql = o.matrix_world.inverted() @ c
            if all(abs(ql[i]) < 0.5 for i in range(3)):
                inside += 1
        if inside or cross:
            hits.append((o.name, inside, cross))
    return hits


def env():
    res = {}
    for vn, skip in (("QA_Env_Ignis", ()), ("QA_Env_Top100", ())):
        vol = bpy.data.objects.get(vn)
        if vol is None:
            print("ENV %s: volume ausente" % vn)
            continue
        h = _intrusions(vol, skip=skip)
        res[vn] = {"ok": not h, "hits": h[:20]}
        print("ENV %-20s %s %s" % (vn, "LIVRE" if not h else "INVADIDO por %d objetos" % len(h), h[:8]))
    # chao livre e plano em Y 7 diante do golem (z -52,7 .. -40, x -9,9 .. 6,1)
    vol = bpy.data.objects.get("QA_Free_IgnisFront")
    bvh, _ = fm_qa.col_bvh()
    (x0, y0, z0), (x1, y1, z1) = L.IGNIS_FRONT
    bad = []
    nsamp = 0
    x = x0 + 0.5
    while x <= x1 - 0.5:
        z = z0 + 0.5
        while z <= z1 - 0.5:
            g = fm_qa.ground(bvh, x, -z, 7.0, up=3.0)
            nsamp += 1
            if g is None or abs(g - L.Y_NORTH) > 0.02:
                bad.append((round(x, 1), round(z, 1), None if g is None else round(g, 2)))
            z += 1.0
        x += 1.0
    h = _intrusions(vol, include_col=True, skip=("COL_GroundN", "COL_Ground_")) if vol else []
    ok = not bad and not h
    res["QA_Free_IgnisFront"] = {"ok": ok, "piso_fora_de_7": bad[:10], "amostras": nsamp, "hits": h[:10]}
    print("ENV %-20s %s (%d amostras do piso em 7,0: %d fora; obstaculos: %s)" % (
        "QA_Free_IgnisFront", "LIVRE E PLANO" if ok else "PROBLEMA", nsamp, len(bad), h[:6]))
    OUT["env"] = res
    return res


def link():
    """encaixe da ponte: borda do patamar (COL e malha) x borda da praca da Ilha 1 (0, 6, 222)"""
    tgt = Vector(L.ISLE_LINK)
    cols = [o for o in bpy.data.objects if o.name.startswith("COL_IsleLanding_")]
    best = None
    for o in cols:
        if o.name.startswith("COL_IsleLandingBar"):
            continue
        mw = o.matrix_world
        vs = [VL.R(mw @ v.co) for v in o.data.vertices]
        top = max(v[1] for v in vs)
        zmax = max(v[2] for v in vs)
        xs = [v[0] for v in vs]
        best = {"col": o.name, "top_y": round(top, 3), "borda_z": round(zmax, 3), "x": [round(min(xs), 2),
                                                                                         round(max(xs), 2)]}
    deck = bpy.data.objects.get("VM_Exit_Bridge")
    dz = None
    if deck:
        mw = deck.matrix_world
        pts = [VL.R(mw @ v.co) for v in deck.data.vertices]
        top_pts = [p for p in pts if abs(p[1] - L.Y_ISLE) < 0.01 and abs(p[0]) <= 12.01]
        if top_pts:
            dz = max(p[2] for p in top_pts)
    d = None
    if best:
        d = math.dist((0.0, best["top_y"], best["borda_z"]), tuple(tgt))
    res = {"alvo": list(tgt), "patamar_col": best, "malha_borda_z": dz, "distancia_col": None if d is None else
           round(d, 3)}
    print("LINK ponte -> Ilha 1: alvo %s | COL %s | borda da malha z %s | distancia %s %s" % (
        list(tgt), best, dz, None if d is None else round(d, 3), "OK" if d is not None and d <= 0.6 else "CONFERIR"))
    OUT["link"] = res
    return res


REQ = ["SPAWN_Lobby", "SPAWNLOBBY_Part", "LAYOUT_Spawn", "LAYOUT_Shop", "LAYOUT_ShopFacing", "LAYOUT_Ignis",
       "LAYOUT_PortalIsland", "MAILBOX_Correio", "NPC_Ignis", "INTERACT_Ignis", "PLAYER_INTERACT_Ignis", "IGNIS_Anvil",
       "LETREIRO_Ignis", "NPC_Shop", "INTERACT_Shop", "PLAYER_INTERACT_Shop", "PADLOJA_Shop", "DOOR_Shop",
       "TOP100_Origin", "LOBBY_GATE_Ilha1", "ISLE_LINK_Area1", "ForgeChimney"] + ["PORTAL_" + k for k, _ in L.PORTALS]


def markers():
    mc = bpy.data.collections.get("15_GAMEPLAY_MARKERS")
    names = {o.name for o in mc.all_objects} if mc else set()
    miss = [n for n in REQ if n not in names]
    pos = {}
    for n in REQ:
        o = bpy.data.objects.get(n)
        if o:
            pos[n] = [round(c, 2) for c in VL.R(o.matrix_world.translation)]
    print("MARKERS %d/%d presentes%s" % (len(REQ) - len(miss), len(REQ), ("  FALTAM " + str(miss)) if miss else ""))
    for n in ("NPC_Ignis", "PLAYER_INTERACT_Ignis", "NPC_Shop", "PLAYER_INTERACT_Shop", "TOP100_Origin", "SPAWN_Lobby",
              "MAILBOX_Correio") + tuple("PORTAL_" + k for k, _ in L.PORTALS):
        if n in pos:
            print("   %-24s Roblox %s" % (n, pos[n]))
    OUT["markers"] = {"faltam": miss, "pos": pos}


def budget():
    owners = {}
    for o in _export_meshes():
        own = "outros"
        for p, ow in VL.OWNER_PREFIX:
            if o.name.startswith(p):
                own = ow
                break
        mats = {o.data.materials[p.material_index].name for p in o.data.polygons if o.data.materials}
        tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
        xs = [(o.matrix_world @ v.co) for v in o.data.vertices]
        if not xs:
            continue
        ext = max(max(v.x for v in xs) - min(v.x for v in xs), max(v.y for v in xs) - min(v.y for v in xs))
        cells = 1
        if ext > 160 and tris > 1500:
            cells = int(math.ceil(ext / 128.0))
        t = owners.setdefault(own, [0, 0])
        t[0] += tris
        t[1] += len(mats) * cells
    tot_t = sum(v[0] for v in owners.values())
    tot_m = sum(v[1] for v in owners.values())
    print("BUDGET (estimativa; o export fatia/funde e da a medida exata)")
    for k in sorted(owners):
        lim = L.BUDGET_OWNER.get(k, ("-", "-"))
        print("   %-12s %7d tris (%s)  ~%4d MeshParts (%s)" % (k, owners[k][0], lim[0], owners[k][1], lim[1]))
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUDGET total ~%d tris / ~%d MeshParts / %d COL (alvo <= %d / %d / %d)" % (
        tot_t, tot_m, ncol, L.BUDGET["static_tris"], L.BUDGET["static_meshes"], L.BUDGET["col"]))
    OUT["budget"] = {"por_dono": owners, "tris": tot_t, "meshparts_est": tot_m, "col": ncol}


def tech():
    gen = re.compile(r"^(Cube|Cylinder|Sphere|Plane|Icosphere|Cone|Torus|Object|Mesh)(\.\d+)?$")
    bad = [o.name for o in bpy.data.objects if gen.match(o.name)]
    nomat = [o.name for o in _export_meshes() if not o.data.materials]
    degen = sum(1 for o in _export_meshes() for p in o.data.polygons if p.area < 1e-6)
    print("TECH nomes_genericos=%d sem_material=%d faces_degeneradas=%d objetos=%d" % (len(bad), len(nomat), degen,
                                                                                      len(bpy.data.objects)))
    OUT["tech"] = {"genericos": bad, "sem_material": nomat, "degeneradas": degen}


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    want = [a for a in argv if not a.startswith("--") and not a.endswith(".json")] or \
        ["nav", "env", "link", "markers", "budget", "tech"]
    for k in want:
        globals()[k]()
    if "--json" in argv:
        p = argv[argv.index("--json") + 1]
        json.dump(OUT, open(p, "w", encoding="utf-8"), indent=1, default=str)
        print("QA json ->", p)
