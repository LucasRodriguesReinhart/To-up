# Konoha kit library: Roblox-compatible primitives authored in Blender.
# Blender axes: X east, Y north, Z up.  Roblox: X=-bx, Y=bz, Z=by  (see export.py)
import bpy, math, random
from mathutils import Vector, Matrix, Euler

ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up\konoha_area"

# name: (rgb 0-255, roblox material, flags)  flags: n=neon, s=studs top, g=glass-ish transparency
PALETTE = {
 'wall_cream':((236,224,192),'SmoothPlastic',''), 'wall_tan':((214,190,150),'SmoothPlastic',''),
 'wall_white':((244,240,226),'SmoothPlastic',''), 'wall_peach':((232,196,160),'SmoothPlastic',''),
 'roof_red':((190,78,50),'SmoothPlastic',''), 'roof_orange':((222,122,56),'SmoothPlastic',''),
 'roof_green':((84,138,104),'SmoothPlastic',''), 'roof_blue':((80,108,140),'SmoothPlastic',''),
 'wood':((140,96,60),'Wood',''), 'wood_dark':((84,58,42),'Wood',''), 'wood_light':((190,150,100),'Wood',''),
 'trim_dark':((58,52,50),'SmoothPlastic',''), 'metal':((128,136,144),'Metal',''),
 'tank':((176,184,188),'SmoothPlastic',''), 'glass':((120,170,190),'Glass','g'), 'window_lit':((255,214,140),'Neon','n'),
 'noren':((40,58,104),'Fabric',''), 'cloth_red':((196,52,44),'Fabric',''), 'cloth_white':((240,236,222),'Fabric',''),
 'lantern':((226,70,50),'SmoothPlastic',''), 'glow':((255,196,110),'Neon','n'),
 'cliff':((196,166,120),'Plastic','s'), 'cliff_dark':((160,130,94),'Plastic','s'), 'cliff_light':((218,194,152),'Plastic','s'),
 'face_stone':((208,182,140),'SmoothPlastic',''), 'face_shadow':((150,122,90),'SmoothPlastic',''),
 'grass':((112,178,72),'Plastic','s'), 'grass_dark':((86,150,60),'Plastic','s'),
 'foliage':((76,150,64),'SmoothPlastic',''), 'foliage_dark':((52,116,56),'SmoothPlastic',''), 'foliage_light':((126,184,78),'SmoothPlastic',''),
 'trunk':((110,78,52),'Wood',''),
 'path':((226,210,170),'SmoothPlastic',''), 'paving':((196,188,166),'Plastic','s'), 'curb':((160,150,130),'SmoothPlastic',''),
 'dirt':((150,118,84),'Plastic','s'), 'dirt_dark':((116,92,70),'Plastic','s'), 'stone':((138,134,128),'Plastic','s'), 'stone_dark':((96,94,96),'Plastic','s'),
 'water':((64,170,222),'Glass','g'), 'water_foam':((200,236,250),'SmoothPlastic','g'),
 'ore_rock':((82,80,92),'Plastic',''),
 'cr_chakra':((90,220,255),'Neon','n'), 'cr_fire':((255,110,50),'Neon','n'), 'cr_wind':((140,255,170),'Neon','n'),
 'cr_lightning':((255,232,90),'Neon','n'), 'cr_earth':((230,160,70),'Neon','n'), 'cr_water':((70,140,255),'Neon','n'),
 'cr_rare':((200,120,255),'Neon','n'), 'crystal_base':((60,140,190),'SmoothPlastic',''),
 'dark_void':((24,22,28),'SmoothPlastic',''), 'gold':((222,176,72),'Metal',''), 'rope':((196,170,120),'Fabric',''),
 'leaf_green':((70,160,70),'SmoothPlastic',''), 'invisible':((255,255,255),'SmoothPlastic','i'),
 'hokage_red':((208,96,60),'SmoothPlastic',''), 'hokage_roof':((140,58,44),'SmoothPlastic',''),
 'gate_green':((58,140,84),'SmoothPlastic',''), 'portal_glow':((120,230,255),'Neon','g'),
 'namek_glow':((110,255,170),'Neon','g'),
 'sand':((230,212,168),'Plastic','s'), 'mine_floor':((120,104,90),'Plastic','s'),
}

def _srgb_to_lin(c):
    c = c/255.0
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def mat(name):
    m = bpy.data.materials.get('K_'+name)
    if m: return m
    rgb, rmat, flags = PALETTE[name]
    m = bpy.data.materials.new('K_'+name)
    lin = [_srgb_to_lin(v) for v in rgb]
    m.diffuse_color = (lin[0], lin[1], lin[2], 1.0)
    m['rbx_material'] = rmat
    m['rbx_rgb'] = list(rgb)
    m['rbx_flags'] = flags
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (lin[0], lin[1], lin[2], 1)
        bsdf.inputs['Roughness'].default_value = 0.8
        if 'n' in flags:
            bsdf.inputs['Emission Color'].default_value = (lin[0], lin[1], lin[2], 1)
            bsdf.inputs['Emission Strength'].default_value = 3.0
    return m

# ---------- shared primitive meshes (unit size) ----------
def _mesh(name, verts, faces):
    me = bpy.data.meshes.get(name)
    if me: return me
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    me.materials.append(None)
    for p in me.polygons: p.use_smooth = False
    return me

def prim(shape):
    if shape == 'B':
        v = [(x,y,z) for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)]
        f = [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]
        return _mesh('RBX_Block', v, f)
    if shape == 'W':  # high side at +y (Roblox +Z), slope faces -y
        v = [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,.5,.5),(.5,.5,.5)]
        f = [(0,3,2,1),(3,4,5,2),(0,1,5,4),(0,4,3),(1,2,5)]
        return _mesh('RBX_Wedge', v, f)
    if shape == 'K':  # corner wedge: apex above Roblox(+X,-Z) = Blender(-x,-y)
        v = [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5)]
        f = [(0,3,2,1),(0,1,4),(3,0,4),(1,2,4),(2,3,4)]
        return _mesh('RBX_Corner', v, f)
    if shape == 'C':  # axis along local x
        n = 16
        v = []
        for x in (-.5,.5):
            for i in range(n):
                a = i/n*2*math.pi
                v.append((x, .5*math.cos(a), .5*math.sin(a)))
        f = [tuple(range(n))[::-1], tuple(range(n,2*n))]
        for i in range(n):
            j = (i+1) % n
            f.append((i, j, n+j, n+i))
        return _mesh('RBX_Cylinder', v, f)
    if shape == 'A':
        me = bpy.data.meshes.get('RBX_Ball')
        if me: return me
        import bmesh
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=.5)
        me = bpy.data.meshes.new('RBX_Ball'); bm.to_mesh(me); bm.free()
        me.materials.append(None)
        return me

# ---------- collections ----------
def coll(path, parent=None):
    parent = parent or bpy.context.scene.collection
    for name in path.split('/'):
        c = bpy.data.collections.get(name)
        if not c:
            c = bpy.data.collections.new(name)
        if c.name not in [x.name for x in parent.children]:
            parent.children.link(c)
        parent = c
    return parent

class Ctx:
    target = None   # collection receiving new parts
    offset = Vector((0,0,0))
    count = 0

def into(c):
    Ctx.target = c

def clear_collection(c):
    for o in list(c.all_objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for ch in list(c.children):
        clear_collection(ch)
        bpy.data.collections.remove(ch)

# ---------- part creation ----------
def part(shape, name, loc, dims, m, rot=(0,0,0), col=None, **props):
    """dims in Blender axes (dx east, dy north, dz up). rot = Euler XYZ radians."""
    o = bpy.data.objects.new(name, prim(shape))
    o.location = Vector(loc) + Ctx.offset
    o.rotation_euler = Euler(rot, 'XYZ')
    o.scale = dims
    o.material_slots[0].link = 'OBJECT'
    mm = mat(m); o.material_slots[0].material = mm
    o.color = mm.diffuse_color
    if col is None:
        col = min(dims) >= 0.9 and (dims[0]*dims[1]*dims[2]) >= 6
    o['col'] = bool(col)
    for k, v in props.items(): o[k] = v
    Ctx.target.objects.link(o)
    Ctx.count += 1
    return o

def box(name, loc, dims, m, rot=(0,0,0), col=None, **kw):
    return part('B', name, loc, dims, m, rot, col, **kw)

def wedge(name, loc, dims, m, rot=(0,0,0), col=None, **kw):
    return part('W', name, loc, dims, m, rot, col, **kw)

def corner(name, loc, dims, m, rot=(0,0,0), col=None, **kw):
    return part('K', name, loc, dims, m, rot, col, **kw)

def ball(name, loc, dims, m, col=False, **kw):
    if isinstance(dims, (int, float)): dims = (dims, dims, dims)
    return part('A', name, loc, dims, m, (0,0,0), col, **kw)

def cyl(name, loc, r, h, m, axis='Z', col=None, rot=None, **kw):
    """Roblox cylinders are round only when the two radial sizes match."""
    if axis == 'Z': e = (0, math.pi/2, 0)
    elif axis == 'Y': e = (0, 0, math.pi/2)
    else: e = (0, 0, 0)
    if rot is not None:
        mtx = Euler(rot, 'XYZ').to_matrix() @ Euler(e, 'XYZ').to_matrix()
        e = tuple(mtx.to_euler('XYZ'))
    return part('C', name, loc, (h, r*2, r*2), m, e, col, **kw)

def rod(name, a, b, w, m, col=False, h=None, **kw):
    a, b = Vector(a), Vector(b)
    d = b - a
    L = d.length
    q = d.to_track_quat('Y', 'Z')
    return part('B', name, (a+b)/2, (w, L, h or w), m, tuple(q.to_euler('XYZ')), col, **kw)

def marker(name, loc, **props):
    o = bpy.data.objects.new(name, None)
    o.empty_display_type = 'SPHERE'; o.empty_display_size = 2
    o.location = Vector(loc) + Ctx.offset
    for k, v in props.items(): o[k] = v
    Ctx.target.objects.link(o)
    return o

# ---------- asset instancing ----------
KIT = {}
def asset(category, name):
    lib = coll('KIT_LIBRARY/KIT_'+category.split('_',1)[1])
    c = bpy.data.collections.get(name)
    if c:
        clear_collection(c)
    else:
        c = bpy.data.collections.new(name)
        lib.children.link(c)
    KIT[name] = c
    into(c)
    return c

def place(name, loc, rz=0.0, s=1.0, target=None, label=None):
    src = bpy.data.collections[name]
    e = bpy.data.objects.new(label or name, None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = src
    e.location = Vector(loc) + Ctx.offset
    e.rotation_euler = (0, 0, rz)
    e.scale = (s, s, s)
    (target or Ctx.target).objects.link(e)
    return e

def rng(seed):
    return random.Random(seed)
