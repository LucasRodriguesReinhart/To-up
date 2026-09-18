# Smooth island ground: one textured mesh (grass top with holes, rounded rim, rocky cliff skirt).
import bpy, bmesh, math
from mathutils import Vector, geometry
from dbshapes import paint, to_object, n3
import db_layout as L

def _signed_area(poly):
    return sum(poly[i][0]*poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0]*poly[i][1] for i in range(len(poly)))/2

def _normals(poly):
    """outward normals (for a CCW polygon) per vertex."""
    ccw = _signed_area(poly) > 0
    out = []
    n = len(poly)
    for i in range(n):
        a, b = Vector(poly[i-1]), Vector(poly[(i+1) % n])
        t = (b - a).normalized()
        nv = Vector((t.y, -t.x)) if ccw else Vector((-t.y, t.x))
        out.append(nv)
    return out

def quarry_loop(n=72, grow=1.0):
    return [L.quarry_point(i/n*2*math.pi, grow) for i in range(n)]

def ellipse_loop(cx, cy, rx, ry, n=56):
    return [(cx + math.cos(i/n*2*math.pi)*rx, cy + math.sin(i/n*2*math.pi)*ry) for i in range(n)]

def island_mesh(target):
    outer = L.OUTLINE
    holes = [quarry_loop(72, 1.0), ellipse_loop(L.LAKE[0], L.LAKE[1], L.LAKE[2] + 1, L.LAKE[3] + 1, 56),
             ellipse_loop(L.CRATER[0], L.CRATER[1], L.CR_R - 1, L.CR_R - 1, 44)]
    bm = bmesh.new()
    loops = [outer] + holes
    tris = geometry.tessellate_polygon([[Vector((x, y, 0)) for (x, y) in lp] for lp in loops])
    flat = [Vector((x, y, 0)) for lp in loops for (x, y) in lp]
    verts = [bm.verts.new(p) for p in flat]
    for (a, b, c) in tris:
        try:
            f = bm.faces.new((verts[a], verts[b], verts[c]))
            if f.normal.z < 0: f.normal_flip()
        except ValueError:
            pass
    # rounded rim + cliff skirt on the outer edge
    nrm = _normals(outer)
    prof = [(0, 0), (.9, -.35), (1.5, -1.3), (1.7, -3.0), (1.2, -6.5), (.6, -10.5)]
    rings = [verts[:len(outer)]]
    for k, (o, z) in enumerate(prof[1:]):
        ring = []
        for i, (x, y) in enumerate(outer):
            jit = n3(x*.08, y*.08, z*.2, 1.0, 3)*1.6 if z < -2 else 0
            p = Vector((x, y, z)) + Vector((nrm[i].x, nrm[i].y, 0))*(o + jit)
            ring.append(bm.verts.new(p))
        rings.append(ring)
    n = len(outer)
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            try:
                f = bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError:
                continue
            f.normal_update()
            if f.normal.dot(Vector((nrm[i].x, nrm[i].y, 0))) < 0 and f.normal.z < .5: f.normal_flip()
    # short skirts inside the holes so their edges never show a gap
    off = len(outer)
    for hole in holes:
        hv = verts[off:off + len(hole)]
        off += len(hole)
        low = [bm.verts.new(Vector((v.co.x, v.co.y, -3))) for v in hv]
        hc = sum((Vector((x, y, -1.5)) for (x, y) in hole), Vector()) / len(hole)
        for i in range(len(hole)):
            j = (i + 1) % len(hole)
            try: f = bm.faces.new((hv[i], hv[j], low[j], low[i]))
            except ValueError: continue
            f.normal_update()
            if f.normal.dot(hc - f.calc_center_median()) < 0: f.normal_flip()
    for f in bm.faces:
        c = f.calc_center_median()
        if c.z > -.05 and f.normal.z < 0: f.normal_flip()
    def col(f):
        c = f.calc_center_median()
        if f.normal.z > .8 and c.z > -.2: return 'db_grass'
        if c.z > -1.5: return 'db_grass_dark'
        if c.z > -4: return 'db_rock_light'
        if c.z > -6: return 'db_rock_dark'
        return 'db_rock'
    paint(bm, col)
    return to_object('Terreno_Malha', bm, target, smooth=True, sharp=50)
