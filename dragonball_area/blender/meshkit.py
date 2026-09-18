# Mesh pipeline for the Vale Capsule kit/map.
#  * opaque pieces of an asset -> ONE mesh textured with a shared colour palette (UVs point at swatches)
#  * neon / glass pieces       -> one mesh per material (Roblox needs the material per MeshPart)
#  * rock / foliage / cloud / dragon materials are voxel-remeshed + noise + decimated -> organic, not boxy
import bpy, bmesh, math, os
from mathutils import Matrix, Vector
import klib
from meshify import piece, SHAPES

ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up\dragonball_area"
PAL_PATH = ROOT + r"\export\db_palette.png"
PAL_N = 16            # swatches per row
PAL_PX = 16           # pixels per swatch
MAX_TRIS = 18000

ORGANIC = {'db_rock': 'rock', 'db_rock_light': 'rock', 'db_rock_dark': 'rock', 'db_rock_red': 'rock', 'db_rock_deep': 'rock',
           'db_crater': 'rock', 'tree_ball': 'puff', 'tree_ball_light': 'puff', 'tree_ball_dark': 'puff', 'tree_ajisa': 'puff',
           'cloud': 'puff', 'cloud_shade': 'puff', 'dragon': 'puff', 'dragon_dark': 'puff', 'dragon_belly': 'puff', 'db_sand': 'soft',
           'foliage': 'puff', 'foliage_dark': 'puff', 'foliage_light': 'puff'}
PART_ONLY = {'db_water', 'db_foam', 'ki_field', 'invisible'}      # stay Roblox Parts (animated textures / collision)

# ------------------------------------------------------------------ palette
def palette_keys():
    return sorted(klib.PALETTE.keys())

def palette_uv(key):
    i = palette_keys().index(key)
    cx, cy = i % PAL_N, i // PAL_N
    return ((cx + .5)/PAL_N, 1 - (cy + .5)/PAL_N)

def build_palette():
    keys = palette_keys()
    size = PAL_N*PAL_PX
    img = bpy.data.images.get('db_palette') or bpy.data.images.new('db_palette', size, size, alpha=False)
    if img.size[0] != size: img.scale(size, size)
    px = [0.0]*(size*size*4)
    for i, k in enumerate(keys):
        rgb = klib.PALETTE[k][0]
        cx, cy = i % PAL_N, i // PAL_N
        for yy in range(PAL_PX):
            for xx in range(PAL_PX):
                X = cx*PAL_PX + xx
                Y = size - 1 - (cy*PAL_PX + yy)
                o = (Y*size + X)*4
                px[o:o+4] = [rgb[0]/255, rgb[1]/255, rgb[2]/255, 1.0]
    img.pixels = px
    img.filepath_raw = PAL_PATH
    img.file_format = 'PNG'
    os.makedirs(os.path.dirname(PAL_PATH), exist_ok=True)
    img.save()
    mat = bpy.data.materials.get('DB_Palette') or bpy.data.materials.new('DB_Palette')
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None) or nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    tex = nt.nodes.get('PalTex') or nt.nodes.new('ShaderNodeTexImage')
    tex.name = 'PalTex'; tex.image = img; tex.interpolation = 'Closest'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = .8
    return mat

# ------------------------------------------------------------------ geometry helpers
def _walk(coll, M, out):
    for o in coll.objects:
        mw = M @ o.matrix_world
        if o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection:
            _walk(o.instance_collection, mw, out)
        elif o.type == 'MESH':
            out.append((o, mw))
    for ch in coll.children:
        _walk(ch, M, out)

def _mat(o):
    return o.material_slots[0].material if o.material_slots else None

def _key(mat):
    return mat.name[2:] if mat and mat.name.startswith('K_') else None

def _piece_mesh(o, mw, quality):
    shape = SHAPES.get(o.data.name.split('.')[0])
    if not shape: return None
    loc, rot, scl = mw.decompose()
    bm = piece(shape, (abs(scl.x), abs(scl.y), abs(scl.z)), quality)
    bm.transform(Matrix.Translation(loc) @ rot.to_matrix().to_4x4())
    return bm

def _append(dst, bm, uv=None):
    tmp = bpy.data.meshes.new('tmp')
    bm.to_mesh(tmp); bm.free()
    if uv is not None:
        lay = tmp.uv_layers.new(name='UVMap')
        for d in lay.data: d.uv = uv
    dst.from_mesh(tmp)
    bpy.data.meshes.remove(tmp)

def _new_obj(name, bm, target, parent, mat, smooth_angle):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    try: me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    except Exception: pass
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    ob.parent = parent
    target.objects.link(ob)
    return ob

_noise = None
def _noise_tex(size):
    global _noise
    t = bpy.data.textures.get('db_noise_%d' % int(size*10)) or bpy.data.textures.new('db_noise_%d' % int(size*10), 'CLOUDS')
    t.noise_scale = size; t.noise_depth = 1
    return t

def organic(ob, kind, extent):
    """Voxel remesh + smooth + noise + decimate, applied in place."""
    if kind == 'rock':
        voxel = max(.22, min(1.6, extent/40)); noise = max(.15, min(2.2, extent*.035)); nsize = max(1.5, extent*.18); smooth = 4; cap = 900 + int(extent*140)
    elif kind == 'puff':
        voxel = max(.2, min(1.4, extent/40)); noise = max(.05, extent*.012); nsize = max(1.2, extent*.2); smooth = 10; cap = 500 + int(extent*45)
    else:
        voxel = max(.25, min(1.2, extent/50)); noise = .1; nsize = 4; smooth = 6; cap = 2500
    cap = min(cap, MAX_TRIS)
    r = ob.modifiers.new('rm', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = voxel; r.adaptivity = 0
    s = ob.modifiers.new('sm', 'SMOOTH'); s.factor = .6; s.iterations = smooth
    d = ob.modifiers.new('dp', 'DISPLACE'); d.texture = _noise_tex(nsize); d.strength = noise; d.mid_level = .5; d.texture_coords = 'GLOBAL'
    me = None
    for attempt in range(3):
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        if len(me.polygons) > len(ob.data.polygons)*.3: break
        bpy.data.meshes.remove(me); me = None
    if me is None:
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    ob.modifiers.clear()
    old = ob.data; ob.data = me; bpy.data.meshes.remove(old)
    tris = sum(len(p.vertices) - 2 for p in me.polygons)
    if tris > cap:
        dec = ob.modifiers.new('dc', 'DECIMATE'); dec.ratio = cap/tris
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        dg.update()
        me2 = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        ob.modifiers.clear()
        old = ob.data; ob.data = me2; bpy.data.meshes.remove(old)
    return ob

def _extent(bm):
    if not bm.verts: return 1.0
    mn = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
    mx = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
    return max((mx - mn).length*.5, 1.0)

def tris_of(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)

def bake_uv(ob, key):
    uv = palette_uv(key)
    me = ob.data
    lay = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    for d in lay.data: d.uv = uv

def split_big(ob, target, parent, limit=MAX_TRIS):
    """Recursively bisect a mesh object by its longest axis until every piece has < limit tris."""
    if tris_of(ob) <= limit: return [ob]
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    cs = [f.calc_center_median() for f in bm.faces]
    xs = [c.x for c in cs]; ys = [c.y for c in cs]; zs = [c.z for c in cs]
    spans = [(max(xs)-min(xs), 0), (max(ys)-min(ys), 1), (max(zs)-min(zs), 2)]
    ax = max(spans)[1]
    vals = sorted(c[ax] for c in cs)
    mid = vals[len(vals)//2]
    out = []
    for side in (0, 1):
        b2 = bm.copy()
        kill = [f for f in b2.faces if (f.calc_center_median()[ax] < mid) == (side == 1)]
        bmesh.ops.delete(b2, geom=kill, context='FACES')
        m2 = bpy.data.meshes.new(ob.name + '~%d' % side)
        b2.to_mesh(m2); b2.free()
        for m in me.materials: m2.materials.append(m)
        o2 = bpy.data.objects.new(ob.name + '~%d' % side, m2)
        o2.parent = parent
        target.objects.link(o2)
        out += split_big(o2, target, parent, limit)
    bm.free()
    bpy.data.objects.remove(ob, do_unlink=True)
    return out

# ------------------------------------------------------------------ main conversion
def convert(name, items, target, pal_mat, quality=1.0, root_name=None, organic_on=True):
    """items: [(object, world_matrix)] RBX primitives. Builds root empty + meshes. Returns (root, tris, meshes)."""
    root = bpy.data.objects.new(root_name or name, None)
    target.objects.link(root)
    groups = {}          # ('pal'|key) -> bmesh ; organic keys get their own bmesh first
    leaf_objs = []
    for o, mw in items:
        if o.get('leaf'):
            me = o.data.copy()
            me.transform(mw)
            lo = bpy.data.objects.new('%s__folhas' % name, me)
            lo.parent = root
            target.objects.link(lo)
            leaf_objs.append(lo)
            continue
        if o.get('pal'):
            if 'pal' not in groups: groups['pal'] = bmesh.new()
            tmp = o.data.copy()
            tmp.transform(mw)
            groups['pal'].from_mesh(tmp)
            bpy.data.meshes.remove(tmp)
            continue
        mat = _mat(o); key = _key(mat)
        if not key or key in PART_ONLY: continue
        flags = klib.PALETTE[key][2]
        bm = _piece_mesh(o, mw, quality)
        if bm is None: continue
        if 'n' in flags or 'g' in flags:
            g = key
        elif organic_on and key in ORGANIC:
            g = 'org:' + key
        else:
            g = 'pal'
        if g not in groups: groups[g] = bmesh.new()
        _append(groups[g], bm, palette_uv(key) if g == 'pal' else None)
    meshes = []
    pal_bm = groups.pop('pal', None)
    # organic groups -> remesh, then UV to their swatch and join into the palette mesh
    for g in [k for k in groups if k.startswith('org:')]:
        key = g[4:]
        bm = groups.pop(g)
        ext = _extent(bm)
        ob = _new_obj('%s__tmp_%s' % (name, key), bm, target, root, pal_mat, 40)
        organic(ob, ORGANIC[key], ext)
        for p in ob.data.polygons: p.use_smooth = True
        try: ob.data.set_sharp_from_angle(angle=math.radians(70 if ORGANIC[key] == 'puff' else 48))
        except Exception: pass
        bake_uv(ob, key)
        if pal_bm is None: pal_bm = bmesh.new()
        pal_bm.from_mesh(ob.data)
        bpy.data.meshes.remove(ob.data)
    if pal_bm is not None and pal_bm.faces:
        ob = _new_obj('%s__pal' % name, pal_bm, target, root, pal_mat, 40)
        meshes += split_big(ob, target, root)
    for key, bm in groups.items():
        m = klib.mat(key)
        ob = _new_obj('%s__%s' % (name, key), bm, target, root, m, 40)
        meshes += split_big(ob, target, root)
    meshes += leaf_objs
    return root, sum(tris_of(m) for m in meshes), meshes

def asset_items(asset):
    items = []
    _walk(bpy.data.collections[asset], Matrix.Identity(4), items)
    return items
