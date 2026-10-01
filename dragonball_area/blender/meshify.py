# Converts a kit asset (collection of RBX primitive objects) into smooth, bevelled meshes merged per material.
# Visual meshes become MeshParts in Roblox; the `col` primitives are exported separately as invisible collision Parts.
import bpy, bmesh, math
from mathutils import Matrix, Vector

SHAPES = {'RBX_Block': 'B', 'RBX_Cylinder': 'C', 'RBX_Ball': 'A', 'RBX_Wedge': 'W', 'RBX_Corner': 'K'}

def _bevel(bm, dims, frac=.14, cap=.9, segs=2, edges=None):
    off = min(min(dims)*frac, cap)
    if off < .03: return
    bmesh.ops.bevel(bm, geom=edges if edges is not None else list(bm.edges), offset=off, offset_type='OFFSET',
                    segments=segs, profile=.5, affect='EDGES', clamp_overlap=True)

def piece(shape, dims, quality=1.0):
    """bmesh of one primitive in its local frame, already sized (no scale left)."""
    bm = bmesh.new()
    dx, dy, dz = dims
    if shape == 'B':
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(dx, dy, dz), verts=bm.verts)
        _bevel(bm, dims, .16, 1.2, 2 if min(dims) > .6 else 1)
    elif shape == 'W':
        v = [bm.verts.new(p) for p in ((-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5), (-.5, .5, .5), (.5, .5, .5))]
        for f in ((0, 3, 2, 1), (3, 4, 5, 2), (0, 1, 5, 4), (0, 4, 3), (1, 2, 5)):
            bm.faces.new([v[i] for i in f])
        bmesh.ops.scale(bm, vec=(dx, dy, dz), verts=bm.verts)
        _bevel(bm, dims, .12, .8, 1)
    elif shape == 'K':
        v = [bm.verts.new(p) for p in ((-.5, -.5, -.5), (.5, -.5, -.5), (.5, .5, -.5), (-.5, .5, -.5), (-.5, -.5, .5))]
        for f in ((0, 3, 2, 1), (0, 1, 4), (3, 0, 4), (1, 2, 4), (2, 3, 4)):
            bm.faces.new([v[i] for i in f])
        bmesh.ops.scale(bm, vec=(dx, dy, dz), verts=bm.verts)
        _bevel(bm, dims, .1, .6, 1)
    elif shape == 'C':
        r = max(dy, dz)/2
        segs = int(max(12, min(40, 10 + r*2.2))*quality)
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r, radius2=r, depth=dx)
        # cone is along Z: rotate to local X (Roblox cylinder axis)
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi/2, 3, 'Y'))
        caps = [e for e in bm.edges if all(abs(abs(vv.co.x) - dx/2) < 1e-4 for vv in e.verts)]
        _bevel(bm, (dx, r*2, r*2), .12, .5, 2, caps)
    elif shape == 'A':
        r = dx/2
        u = int(max(12, min(32, 10 + r*2))*quality)
        bmesh.ops.create_uvsphere(bm, u_segments=u, v_segments=max(8, u//2), radius=r)
    return bm

def _walk(coll, M, out):
    for o in coll.objects:
        mw = M @ o.matrix_world
        if o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection:
            _walk(o.instance_collection, mw, out)
        elif o.type == 'MESH':
            out.append((o, mw))
    for ch in coll.children:
        _walk(ch, M, out)

def meshify(asset_name, target, offset=Vector((0, 0, 0)), quality=1.0, smooth_angle=40):
    """Builds '<asset>' empty with one mesh child per material inside `target` collection. Returns (empty, tris)."""
    src = bpy.data.collections[asset_name]
    items = []
    _walk(src, Matrix.Identity(4), items)
    per_mat = {}
    for o, mw in items:
        shape = SHAPES.get(o.data.name.split('.')[0])
        if not shape: continue
        mat = o.material_slots[0].material if o.material_slots else None
        if mat is None or 'i' in mat.get('rbx_flags', ''): continue
        loc, rot, scl = mw.decompose()
        dims = (abs(scl.x), abs(scl.y), abs(scl.z))
        bm = piece(shape, dims, quality)
        T = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()
        bm.transform(T)
        tmp = bpy.data.meshes.new('tmp')
        bm.to_mesh(tmp); bm.free()
        key = mat.name
        if key not in per_mat:
            per_mat[key] = (bmesh.new(), mat)
        per_mat[key][0].from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    root = bpy.data.objects.new(asset_name, None)
    root.location = offset
    target.objects.link(root)
    tris = 0
    for key, (bm, mat) in per_mat.items():
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=.0005)
        me = bpy.data.meshes.new(asset_name + '__' + key[2:])
        bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        try:
            me.set_sharp_from_angle(angle=math.radians(smooth_angle))
        except Exception:
            pass
        me.materials.append(mat)
        ob = bpy.data.objects.new(asset_name + '__' + key[2:], me)
        ob.parent = root
        target.objects.link(ob)
        tris += sum(len(p.vertices) - 2 for p in me.polygons)
    return root, tris
