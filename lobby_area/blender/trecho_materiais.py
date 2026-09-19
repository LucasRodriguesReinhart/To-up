# trecho_materiais.py - liga as texturas (tex_trecho/) aos materiais do trecho (Principled: Base Color, Normal,
# Roughness, Metallic) com UV por projecao de caixa em espaco de mundo, e exporta o FBX com marcador _ORIGEM.
import bpy, bmesh, math, os
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX = os.path.join(ROOT, 'tex_trecho')
EXPORT = os.path.join(ROOT, 'export')

# material -> (albedo, normal, rough, metal, escala uv (1/studs))
LIB = {
    'T_STONE': ('pedra_principal', True, True, False, 1 / 12.0),
    'T_TRIM': ('pedra_moldura', True, True, False, 1 / 8.0),
    'T_CREAM': ('pedra_moldura', True, True, False, 1 / 6.0),
    'T_DARK': ('pedra_escura', True, True, False, 1 / 14.0),
    'T_FLOOR': ('piso', True, True, False, 1 / 14.0),
    'T_GOLD': ('ouro', True, True, True, 1 / 3.0),
    'T_MILK': ('vidro_leitoso', False, True, False, 1 / 2.0),
    'T_LEITO': ('pedra_principal', True, True, False, 1 / 6.0),
    'T_PEDRA': ('pedra_escura', True, True, False, 1 / 4.0),
    'T_JUNTA': ('pedra_escura', False, False, False, 1 / 8.0),
}

def img(fn):
    p = os.path.join(TEX, fn)
    if not os.path.exists(p): return None
    im = bpy.data.images.get(fn)
    if im is None:
        im = bpy.data.images.load(p); im.name = fn
    else:
        im.reload()
    return im

def wire(m, base, has_n, has_r, has_m):
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type in ('TEX_IMAGE', 'NORMAL_MAP'): nt.nodes.remove(n)
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    a = img(base + '_albedo.png')
    if a:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = a; t.name = 'Albedo'; nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    if has_r:
        r = img(base + '_rough.png')
        if r:
            r.colorspace_settings.name = 'Non-Color'
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = r; t.name = 'Rough'; nt.links.new(t.outputs['Color'], bsdf.inputs['Roughness'])
    if has_n:
        nimg = img(base + '_normal.png')
        if nimg:
            nimg.colorspace_settings.name = 'Non-Color'
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = nimg; t.name = 'Normal'
            nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(t.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    if has_m:
        bsdf.inputs['Metallic'].default_value = 1.0
        mi = img(base + '_metal.png')
        if mi:
            mi.colorspace_settings.name = 'Non-Color'
            t = nt.nodes.new('ShaderNodeTexImage'); t.image = mi; t.name = 'Metal'; nt.links.new(t.outputs['Color'], bsdf.inputs['Metallic'])

def box_uv(obj, scale):
    me = obj.data
    lay = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
    mw = obj.matrix_world
    for poly in me.polygons:
        n = (mw.to_3x3() @ poly.normal)
        ax = 2 if abs(n.z) >= max(abs(n.x), abs(n.y)) else (0 if abs(n.x) > abs(n.y) else 1)
        for li in poly.loop_indices:
            co = mw @ me.vertices[me.loops[li].vertex_index].co
            if ax == 2: lay.data[li].uv = (co.x * scale, co.y * scale)
            elif ax == 0: lay.data[li].uv = (co.y * scale, co.z * scale)
            else: lay.data[li].uv = (co.x * scale, co.z * scale)

def apply_all(collections=('TORRE', 'PORTAL', 'ESCADA', 'POSTE', 'PISO', 'AGUA', 'ARVORES')):
    for name, (base, hn, hr, hm, sc) in LIB.items():
        m = bpy.data.materials.get(name)
        if m: wire(m, base, hn, hr, hm)
    n = 0
    for cn in collections:
        c = bpy.data.collections.get(cn)
        if not c: continue
        for o in c.objects:
            if o.type != 'MESH' or not o.data.materials: continue
            mname = o.data.materials[0].name
            if mname in LIB:
                box_uv(o, LIB[mname][4]); n += 1
    return n

def export_fbx(name='TRECHO_AMOSTRA', collections=('TORRE', 'PORTAL', 'ESCADA', 'POSTE', 'PISO', 'AGUA', 'ARVORES')):
    os.makedirs(EXPORT, exist_ok=True)
    # marcador de origem
    org = bpy.data.objects.get('_ORIGEM')
    if org is None:
        me = bpy.data.meshes.new('_ORIGEM'); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.translate(bm, vec=(0, 0, 120), verts=bm.verts); bm.to_mesh(me); bm.free()
        org = bpy.data.objects.new('_ORIGEM', me); bpy.context.scene.collection.objects.link(org)
    sel = [org]
    for cn in collections:
        c = bpy.data.collections.get(cn)
        if c: sel += [o for o in c.objects if o.type == 'MESH']
    for o in bpy.data.objects: o.select_set(False)
    for o in sel: o.select_set(True)
    bpy.context.view_layer.objects.active = sel[0]
    path = os.path.join(EXPORT, name + '.fbx')
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward='-Z', axis_up='Y',
                             apply_scale_options='FBX_SCALE_ALL', mesh_smooth_type='FACE', path_mode='COPY',
                             embed_textures=True, use_mesh_modifiers=True, add_leaf_bones=False, bake_anim=False)
    return path, len(sel)
