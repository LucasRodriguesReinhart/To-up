# k_export.py - exporta o KIT (cada malha unica UMA vez, na origem) + dados para montar no Roblox por script.
import bpy, os, json, math
from mathutils import Vector
from k_core import col, clear_col, ctx

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\murim\kit\export"
os.makedirs(OUT, exist_ok=True)

def export_kit(atlas_map, place, name='KIT_FORJA_CELESTE'):
    c = clear_col('EXPORT'); info = {}; objs = []
    # lobby_atlas.json guarda NOME DE MALHA (run_bg.py grava com bpy.data.meshes.get(n) em objs_de).
    # Aqui isso era lido como NOME DE OBJETO: bpy.data.objects[n].data.name. Onde objeto e malha
    # divergem - as pecas KIT_* que existem em duas geracoes, com sufixo .001/.002 - o nome resolvido
    # nao batia com o da colocacao, a malha caia no 'continue' logo abaixo e SUMIA do FBX sem erro.
    # Eram 26 malhas assadas nos atlas que nunca chegavam ao Roblox.
    mesh_atlas = {}
    for atlas, names in atlas_map.items():
        for n in names: mesh_atlas[n] = atlas
    for o in bpy.data.objects:
        if o.get('espelho_de'):
            fonte = bpy.data.objects.get(o['espelho_de'])
            if fonte is not None and fonte.data.name in mesh_atlas:
                mesh_atlas[o.data.name] = mesh_atlas[fonte.data.name]
    used = sorted({p['mesh'] for p in place} | set(mesh_atlas.keys()))
    for mn in used:
        me = bpy.data.meshes.get(mn)
        if me is None or mn not in mesh_atlas: continue
        e = bpy.data.objects.new(mn, me); c.objects.link(e); objs.append(e)
        xs = [v.co for v in me.vertices]
        mn_ = Vector((min(v.x for v in xs), min(v.y for v in xs), min(v.z for v in xs))); mx_ = Vector((max(v.x for v in xs), max(v.y for v in xs), max(v.z for v in xs)))
        ce = (mn_ + mx_) / 2; sz = mx_ - mn_
        info[mn] = dict(centro=[round(v, 4) for v in ce], tamanho=[round(v, 4) for v in sz], tris=sum(len(p.vertices) - 2 for p in me.polygons), atlas=mesh_atlas[mn])
    faltando = [mn for mn in used if bpy.data.meshes.get(mn) is not None and mn not in mesh_atlas]
    sem_malha = [mn for mn in used if bpy.data.meshes.get(mn) is None]
    if faltando or sem_malha:
        raise SystemExit('EXPORT ABORTADO: %d malhas sem atlas (%s) e %d nomes sem malha (%s). '
                         'Uma montagem que perde peca em silencio e pior que um erro.'
                         % (len(faltando), ', '.join(faltando[:6]), len(sem_malha), ', '.join(sem_malha[:6])))
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    lc = bpy.context.view_layer.layer_collection.children.get('EXPORT')
    if lc: lc.exclude = False
    for e in objs: e.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    path = os.path.join(OUT, name + '.fbx')
    with bpy.context.temp_override(**ctx(), active_object=objs[0], object=objs[0], selected_objects=objs, selected_editable_objects=objs):
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward='-Z', axis_up='Y', apply_scale_options='FBX_SCALE_ALL',
                                 mesh_smooth_type='FACE', path_mode='COPY', embed_textures=True, add_leaf_bones=False, bake_anim=False,
                                 use_mesh_modifiers=True, object_types={'MESH'})
    json.dump(info, open(os.path.join(OUT, 'kit_meshes.json'), 'w'), indent=1)
    json.dump(place, open(os.path.join(OUT, 'placements.json'), 'w'))
    for e in objs: bpy.data.objects.remove(e, do_unlink=True)
    return path, info
