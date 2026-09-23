# fm_scene_sightline - teste de VISADA a partir do spawn (o que o jogador ve ao chegar)
# uso: blender -b lobby_forja_mineradora.blend --python fm_scene_sightline.py [-- --eye x,y,z]
#      (ou: import fm_scene_sightline; fm_scene_sightline.sightlines() de dentro do fm_qa)
# Olho do jogador no spawn; alvos: centro de cada um dos 6 discos dos portais, boca da lareira da forja e coroa da
# torre-chamine. Passa se o PRIMEIRO objeto atingido pelo raio olho->alvo for o proprio alvo. Ignora colisoes (COL_),
# referencia de escala (SCALE_), helpers de VFX (VFX_), objetos fora do render, marcadores e luzes (nao sao malha).
# O log lista, em ordem, tudo o que bloqueia a visada antes do alvo; nos discos tambem mede a borda (4 pontos a 60%
# do raio): "disco k/5" = quantos dos 5 pontos o jogador enxerga.
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import fm_layout as L

EYE = (0.0, -104.0, 5.5)
SKIP = ("COL_", "SCALE_", "VFX_", "SKY_", "BLK_")


def targets():
    """nome -> (pontos alvo [centro primeiro], prefixos que contam como 'o proprio alvo')"""
    t = {}
    for k in L.PORTAL_KEYS:
        sw = bpy.data.objects.get("PORTAL_%s_Swirl" % k)
        if sw is not None and sw.type == "MESH":
            cs = [sw.matrix_world @ Vector(c) for c in sw.bound_box]
            c = sum(cs, Vector()) / 8.0
            r = 0.5 * max(max(p.x for p in cs) - min(p.x for p in cs), max(p.z for p in cs) - min(p.z for p in cs))
        else:
            px = L.PORTAL_X[L.PORTAL_KEYS.index(k)]
            c = Vector((px, L.PORTAL_Y, L.TERR + 11.2))
            r = 7.5
        ring = [c + Vector(v) * (0.6 * r) for v in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1))]
        t["PORTAL_" + k] = ([c] + ring, ("PORTAL_%s_" % k,))
    # o Ignis fica de proposito entre o fogo e a bigorna: o NPC conta como parte do alvo da lareira
    t["FORGE_Hearth(boca)"] = ([Vector((0.0, -1.0, L.FL + 6.0))], ("FORGE_Hearth", "NPC_Ignis"))
    tw = bpy.data.objects.get("FORGE_Chimney_Tower")
    top = L.CHIMNEY_TOP
    if tw is not None and tw.type == "MESH":
        top = max((tw.matrix_world @ Vector(c)).z for c in tw.bound_box)
    t["FORGE_Chimney_Tower(coroa)"] = ([Vector((L.CHIMNEY[0], L.CHIMNEY[1], top - 2.5))], ("FORGE_Chimney_Tower",))
    return t


def scene_bvh():
    verts, polys, owner = [], [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(SKIP) or o.hide_render:
            continue
        mw = o.matrix_world
        base = len(verts)
        verts += [mw @ v.co for v in o.data.vertices]
        for p in o.data.polygons:
            polys.append([base + i for i in p.vertices])
            owner.append(o.name)
    return BVHTree.FromPolygons(verts, polys, epsilon=0.0), owner


def cast(bvh, owner, eye, tgt, own):
    """segue o raio olho->alvo; devolve (atingiu o alvo?, bloqueadores em ordem, objeto do alvo atingido)"""
    d = tgt - eye
    dist = d.length
    d.normalize()
    o = eye.copy()
    travelled = 0.0
    blockers = []
    for _ in range(64):
        h = bvh.ray_cast(o, d, dist + 3.0 - travelled)
        if h[0] is None:
            break
        ob = owner[h[2]]
        if ob.startswith(own):
            return True, blockers, ob
        if ob not in blockers:
            blockers.append(ob)
        travelled += (h[0] - o).length + 0.02
        o = h[0] + d * 0.02
        if travelled > dist + 3.0:
            break
    return False, blockers, None


def sightlines(eye=EYE, verbose=True):
    bvh, owner = scene_bvh()
    eye = Vector(eye)
    res = {}
    for name, (pts, own) in targets().items():
        hit, blockers, ob = cast(bvh, owner, eye, pts[0], own)
        ok = hit and not blockers
        seen = int(ok)
        edge_block = []
        for p in pts[1:]:
            h2, b2, _ = cast(bvh, owner, eye, p, own)
            if h2 and not b2:
                seen += 1
            for b in b2:
                if b not in blockers and b not in edge_block:
                    edge_block.append(b)
        via = ob if (ok and ob and not ob.startswith(own[0])) else None
        res[name] = dict(ok=ok, blockers=blockers, edge_blockers=edge_block, seen=seen, samples=len(pts), via=via)
        if verbose:
            tag = "OK   " if ok else "FAIL "
            extra = "" if ok else ("  bloqueado por: " + ", ".join(blockers) if blockers else "  alvo nao atingido")
            if ok and via:
                extra = "  (via %s)" % via
            if len(pts) > 1:
                extra += "  | disco %d/%d%s" % (seen, len(pts), (" borda: " + ", ".join(edge_block)) if edge_block else "")
            c = pts[0]
            print("VISADA %s%-28s alvo=(%.0f, %.0f, %.0f)%s" % (tag, name, c.x, c.y, c.z, extra))
    if verbose:
        n = sum(1 for r in res.values() if r["ok"])
        print("VISADA %d/%d livres (olho %s)" % (n, len(res), tuple(round(c, 1) for c in eye)))
    return res


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    eye = EYE
    if "--eye" in argv:
        eye = tuple(float(v) for v in argv[argv.index("--eye") + 1].split(","))
    sightlines(eye)
