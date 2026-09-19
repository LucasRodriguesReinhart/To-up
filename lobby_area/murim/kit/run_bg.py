# run_bg.py - roda etapas do pipeline do kit com o Blender em SEGUNDO PLANO (sem janela, sem MCP, sem limite de 60 s).
# uso: blender -b kit_forja_celeste.blend --python run_bg.py -- <etapa> [args]
import bpy, sys, os, json, time, traceback
KIT = os.path.dirname(os.path.abspath(__file__))
if KIT not in sys.path: sys.path.insert(0, KIT)
import k_core, k_pavilhao, k_materiais, k_render, k_export
args = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
etapa = args[0] if args else ''
def P(*a): print('BG>', *a); sys.stdout.flush()
t0 = time.time()
try:
    P('arquivo', os.path.basename(bpy.data.filepath), '| objetos', len(bpy.data.objects), '| etapa', etapa, args[1:])
    if etapa == 'bake':                       # bake <atlas> <passe> [size] [samples] [CPU|GPU]
        atlas, passe = args[1], args[2]
        size = int(args[3]) if len(args) > 3 else 2048; samples = int(args[4]) if len(args) > 4 else 24; dev = args[5] if len(args) > 5 else 'CPU'
        k_materiais.build_paints()
        for lc in bpy.context.view_layer.layer_collection.children:      # um k_render.only() anterior desliga as DUAS coisas
            if lc.name.startswith('PAV_'): lc.exclude = False; lc.collection.hide_render = False; lc.collection.hide_viewport = False
        for o in bpy.data.objects:
            if o.name.startswith('KIT_'): o.hide_render = False
        bpy.context.view_layer.update()
        objs = [bpy.data.objects[n] for n in k_pavilhao.ATLAS[atlas]]
        P(k_materiais.bake(atlas, objs, passe, size=size, samples=samples, device=dev))
    if etapa == 'rebuild':                    # reconstroi o pavilhao + refaz UVs de todos os atlas e salva (tintas nos slots)
        k_materiais.build_paints()
        K, R, rep = k_pavilhao.build(); P(rep[-1])
        for atlas, names in k_pavilhao.ATLAS.items(): P(k_materiais.unwrap(atlas, [bpy.data.objects[n].data for n in names]))
        P('espelhos:', k_pavilhao.remirror())
        json.dump(k_pavilhao.PLACE, open(os.path.join(KIT, 'placements.json'), 'w')); P('placements', len(k_pavilhao.PLACE))
        bpy.ops.wm.save_mainfile(); P('blend salvo')
    if etapa == 'kit2_final':                 # assa o atlas novo em qualidade final, finaliza TUDO, renderiza e exporta
        k_materiais.build_paints()
        for lc in bpy.context.view_layer.layer_collection.children:
            if lc.name.startswith('PAV_'): lc.exclude = False; lc.collection.hide_render = False; lc.collection.hide_viewport = False
        for o in bpy.data.objects:
            if o.name.startswith('KIT_'): o.hide_render = False
        bpy.context.view_layer.update()
        objs = [bpy.data.objects[n] for n in k_pavilhao.ATLAS['A_KIT2']]
        for passe, size, spp in (('color', 2048, 24), ('rough', 1024, 1), ('normal', 2048, 8)):
            P(k_materiais.bake('A_KIT2', objs, passe, size=size, samples=spp, device='CPU'))
        for atlas, names in k_pavilhao.ATLAS.items():
            P(k_materiais.finalize(atlas, [bpy.data.objects[n] for n in names], emis=(atlas == 'A_PROPS')))
        P('espelhos:', k_pavilhao.remirror())
        for nm, hexc in (('PAV_chao', '978362'), ('PAV_terraco_nucleo', '7E745F')):
            o = bpy.data.objects.get(nm)
            if o:
                m = bpy.data.materials.get('F_' + nm) or bpy.data.materials.new('F_' + nm); m.use_nodes = True
                bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'); bs.inputs['Base Color'].default_value = (*k_materiais.hex_lin(hexc), 1); bs.inputs['Roughness'].default_value = .9
                o.data.materials.clear(); o.data.materials.append(m)
        bpy.ops.wm.save_mainfile(); P('blend salvo')
        place = json.load(open(os.path.join(KIT, 'placements.json')))
        path, info = k_export.export_kit(k_pavilhao.ATLAS, place, name='KIT_FORJA_CELESTE_v3')
        P('FBX %s %.1f MB | %d malhas | %d tris | maior %d' % (os.path.basename(path), os.path.getsize(path) / 1e6, len(info), sum(v['tris'] for v in info.values()), max(v['tris'] for v in info.values())))
        try:
            cols = ['PAV_PEDRA', 'PAV_MADEIRA', 'PAV_DOUGONG', 'PAV_TELHADO', 'PAV_PROPS', 'PAV_VEG', 'PAV_CHAO', 'PAV_KIT2']
            k_render.only(cols); k_render.sun(46, -32, 3.4)
            k_render.camera((58, -66, 22), (12, -4, 14), 28); P(k_render.eevee('g1c_tex_conjunto.png', res=(1500, 900)))
            k_render.camera((24, -40, 9), (30, -6, 9), 30); P(k_render.eevee('g1c_tex_muro_portao.png', res=(1400, 800)))
            k_render.camera((-2, -44, 7), (-12, -28, 8), 30); P(k_render.eevee('g1c_tex_estandarte_espada.png', res=(1300, 800)))
        except Exception:
            P('RENDER FALHOU (o resto ja esta salvo/exportado)'); print(traceback.format_exc())
    P('fim %.1fs' % (time.time() - t0))
except Exception:
    P('ERRO'); print(traceback.format_exc()); sys.exit(1)
