# wb_qa.py - QA do lobby Wolfberg sobre o .blend montado (build_wb):
#   nav      rotas do andador (fm_qa.walk sobre as COL_): degrau/queda <= 2,3, teto >= 6,5; tempo a pe (WalkSpeed 16)
#   env      envoltoria do Ignis livre (nenhuma malha exportavel nem COL dentro), chao plano na cota 7 diante dele
#   link     fim da ponte em (0, 6, 222) com chao de colisao
#   markers  marcadores de contrato presentes
#   budget   tris / malhas por dono
# uso: blender -b --factory-startup lobby_wolfberg.blend --python wb_qa.py -- [nav] [env] [link] [markers] [budget]
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wb_lib as W
import bpy
from mathutils import Vector
import wb_layout as L
import fm_qa

OUT = {}
FAIL = []


def walk(bvh, pts, z0):
    """andador do fm_qa com o raio do teto saindo de z + 0,7 (degraus de 0,4 encostados nao contam como teto)"""
    fails = []
    z = z0
    samples = []
    for a, b in zip(pts, pts[1:]):
        a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        n = max(1, int((b - a).length / 0.5))
        for i in range(n + 1):
            samples.append(a + (b - a) * (i / n))
    for p in samples:
        g = fm_qa.ground(bvh, p.x, p.y, z)
        if g is None:
            fails.append(("VAZIO", tuple(round(c, 1) for c in p.xy), round(z, 1)))
            break
        if g - z > fm_qa.STEP_UP:
            fails.append(("DEGRAU_ALTO", tuple(round(c, 1) for c in p.xy), round(g - z, 2)))
            break
        if z - g > fm_qa.DROP:
            fails.append(("QUEDA", tuple(round(c, 1) for c in p.xy), round(z - g, 2)))
            break
        z = g
        h = bvh.ray_cast(Vector((p.x, p.y, z + 0.7)), Vector((0, 0, 1)), fm_qa.HEAD - 0.7)
        if h[0] is not None:
            fails.append(("TETO_BAIXO", tuple(round(c, 1) for c in p.xy), round(h[0].z - z, 2)))
            break
        for hz in (2.0, 3.6, 5.0):
            nn = bvh.find_nearest(Vector((p.x, p.y, z + hz)), fm_qa.BODY_R * 0.9)
            if nn[0] is not None:
                fails.append(("OBSTACULO", tuple(round(c, 1) for c in p.xy), round(hz, 1), fm_qa.OWNER[nn[2]]))
                break
        if fails:
            break
    return fails, z


def nav():
    bvh, n = fm_qa.col_bvh()
    res = {}
    print("COL faces:", n)
    for name, (pts, y0) in L.routes().items():
        bp = [(x, -z) for x, z in pts]
        f, zend = walk(bvh, bp, y0)
        ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))
        t = ln / L.WALK
        ok = not f
        res[name] = {"ok": ok, "len": round(ln, 1), "s": round(t, 1), "fail": [list(map(str, x)) for x in f],
                     "y_end": round(zend, 2)}
        print("ROTA %-30s %s  %6.1f studs  %5.1f s%s%s" % (name, "OK  " if ok else "FAIL", ln, t,
                                                          "" if t <= 15.0 else "  <-- > 15 s", "" if ok else "  " + str(f)[:300]))
        if not ok:
            FAIL.append("rota " + name)
    OUT["nav"] = res


def _export_meshes():
    obs = []
    for g in ("02_TERRAIN", "03_TOWN", "04_FORGE", "05_SERVICES", "06_PORTALS", "07_EXIT", "09_VEGETATION"):
        c = bpy.data.collections.get(g)
        if c:
            obs += [o for o in c.all_objects if o.type == "MESH" and not o.name.startswith(("COL_", "QA_", "PREVIEW_"))]
    return obs


def _inside_box(lo, hi, shrink=0.05):
    """objetos (malhas exportaveis + COL) com algum vertice dentro da caixa Roblox lo..hi"""
    a = W.RB(lo[0] + shrink, lo[2] + shrink, lo[1] + shrink)
    b = W.RB(hi[0] - shrink, hi[2] - shrink, hi[1] - shrink)
    x0, x1 = min(a.x, b.x), max(a.x, b.x)
    y0, y1 = min(a.y, b.y), max(a.y, b.y)
    z0, z1 = min(a.z, b.z), max(a.z, b.z)
    bad = []
    objs = _export_meshes() + [o for o in bpy.data.objects if o.name.startswith("COL_")]
    for o in objs:
        mw = o.matrix_world
        bb = [mw @ Vector(c) for c in o.bound_box]
        if max(v.x for v in bb) < x0 or min(v.x for v in bb) > x1 or max(v.y for v in bb) < y0 or min(v.y for v in bb) > y1 \
                or max(v.z for v in bb) < z0 or min(v.z for v in bb) > z1:
            continue
        if o.name.startswith("COL_"):
            # caixa: testa os 8 cantos e o centro
            pts = bb + [mw.translation]
        else:
            pts = [mw @ v.co for v in o.data.vertices]
        for p in pts:
            if x0 <= p.x <= x1 and y0 <= p.y <= y1 and z0 <= p.z <= z1:
                bad.append(o.name)
                break
    return bad


def env():
    lo, hi = L.IGNIS_ENV
    bad = _inside_box(lo, hi)
    print("ENV Ignis (%s..%s): %s" % (lo, hi, "livre" if not bad else "INVADIDA por " + ", ".join(bad)))
    if bad:
        FAIL.append("envoltoria do Ignis: " + ", ".join(bad))
    lo, hi = L.IGNIS_FRONT
    bad = [n for n in _inside_box((lo[0], lo[1] + 0.3, lo[2]), hi) if not n.startswith("COL_")]
    print("FRENTE Ignis: %s" % ("livre" if not bad else "INVADIDA por " + ", ".join(bad)))
    if bad:
        FAIL.append("frente do Ignis: " + ", ".join(bad))
    # chao plano a 7 diante do golem
    bvh, n = fm_qa.col_bvh()
    ys = []
    for z in (-52.0, -48.0, -44.0, -41.0):
        for x in (-8.0, -0.9, 5.0):
            g = fm_qa.ground(bvh, x, -z, L.Y_PAVE + 1.0)
            ys.append(None if g is None else round(g, 2))
    print("CHAO diante do Ignis (cota 7 esperada):", ys)
    if any(y is None or abs(y - L.Y_PAVE) > 0.15 for y in ys):
        FAIL.append("chao diante do Ignis fora da cota 7: %s" % ys)
    OUT["env"] = {"ignis_env": not bad, "floor": ys}


def link():
    bvh, n = fm_qa.col_bvh()
    res = []
    for x in (-10.0, 0.0, 10.0):
        for z in (214.0, 218.0, 221.5):
            g = fm_qa.ground(bvh, x, -z, L.Y_ISLE + 1.5)
            res.append((x, z, None if g is None else round(g, 2)))
    print("LINK Ilha 1 (chao esperado 6.0 +-0.3 em x +-12, z 213..222):", res)
    if any(g is None or abs(g - L.Y_ISLE) > 0.3 for (_, _, g) in res):
        FAIL.append("fim da ponte: %s" % res)
    OUT["link"] = res


REQUIRED = ["SPAWN_Lobby", "SPAWNLOBBY_Part", "LAYOUT_Spawn", "LAYOUT_Shop", "LAYOUT_ShopFacing", "LAYOUT_Ignis",
            "LAYOUT_PortalIsland", "MAILBOX_Correio", "NPC_Ignis", "INTERACT_Ignis", "PLAYER_INTERACT_Ignis", "IGNIS_Anvil",
            "LETREIRO_Ignis", "ForgeChimney", "NPC_Shop", "INTERACT_Shop", "PLAYER_INTERACT_Shop", "PADLOJA_Shop", "DOOR_Shop",
            "TOP100_Origin", "LOBBY_GATE_Ilha1", "ISLE_LINK_Area1"] + ["PORTAL_" + k for k, _ in L.PORTALS]


def markers():
    have = {o.name for o in bpy.data.objects if o.type == "EMPTY"}
    miss = [m for m in REQUIRED if m not in have and not any(h.startswith(m) for h in have)]
    print("MARCADORES: %d presentes, faltam: %s" % (len(have), miss or "nenhum"))
    if miss:
        FAIL.append("marcadores faltando: " + ", ".join(miss))
    OUT["markers"] = {"missing": miss}


def budget():
    owners = [("WB_Ter_", "terrain"), ("WB_Bg_", "backdrop"), ("WB_Town_", "town"), ("WB_House_", "houses"),
              ("WB_Frg_", "forge"), ("WB_Shop_", "services"), ("WB_Rank_", "services"), ("PORTAL_", "portals"),
              ("WB_Court_", "portals"), ("WB_Exit_", "exit"), ("WB_Veg_", "vegetation"), ("WB_Prop_", "props")]
    tris = {}
    n = {}
    big = []
    for o in _export_meshes():
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        own = next((w for p, w in owners if o.name.startswith(p)), "outros")
        tris[own] = tris.get(own, 0) + t
        n[own] = n.get(own, 0) + 1
        if t > 9000:
            big.append((o.name, t))
    tot = 0
    for k in sorted(tris):
        cap = L.BUDGET_OWNER.get(k, (0, 0))
        flag = "" if tris[k] <= cap[0] else "  <-- ACIMA de %d" % cap[0]
        print("  %-11s %8d tris %4d malhas (teto %d / %d)%s" % (k, tris[k], n[k], cap[0], cap[1], flag))
        tot += tris[k]
    print("  TOTAL       %8d tris %4d malhas (teto %d / %d)" % (tot, sum(n.values()), L.BUDGET["static_tris"], L.BUDGET["static_meshes"]))
    if big:
        print("  malhas > 9000 tris (o export fatia):", big[:12])
    OUT["budget"] = {"tris": tris, "meshes": n, "total": tot}


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    todo = [a for a in argv if not a.startswith("--")] or ["nav", "env", "link", "markers", "budget"]
    for t in todo:
        print("==== " + t)
        globals()[t]()
    print("QA: %s" % ("OK" if not FAIL else "FALHAS: " + " | ".join(FAIL)))
    if "--json" in argv:
        json.dump(OUT, open(argv[argv.index("--json") + 1], "w"), indent=1)
