# run_bg.py - roda etapas do pipeline do kit com o Blender em SEGUNDO PLANO (sem janela, sem MCP, sem limite de 60 s).
# uso: blender -b kit_forja_celeste.blend --python run_bg.py -- <etapa> [args]
import bpy, sys, os, json, time, traceback
KIT = os.path.dirname(os.path.abspath(__file__))
if KIT not in sys.path: sys.path.insert(0, KIT)
import bmesh
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
    if etapa.startswith('lobby_uv') or etapa.startswith('lobby_bake') or etapa == 'lobby_final':
        import k_montagem, importlib; importlib.reload(k_montagem)
        k_materiais.build_paints()
        ATL = json.load(open(os.path.join(KIT, 'lobby_atlas.json')))
        for lc in bpy.context.view_layer.layer_collection.children:
            if lc.name.startswith('LOB_'): lc.exclude = False; lc.collection.hide_render = False; lc.collection.hide_viewport = False
        for o in bpy.data.objects: o.hide_render = False
        bpy.context.view_layer.update()
        def objs_de(atlas):
            out = []
            for n in ATL[atlas]:
                me = bpy.data.meshes.get(n)
                if not me: continue
                o = next((x for x in bpy.data.objects if x.data == me), None)
                if o: out.append(o)
            return out
        if etapa.startswith('lobby_uv'):
            for atlas, nomes in ATL.items():
                P(k_materiais.unwrap(atlas, [bpy.data.meshes[n] for n in nomes if n in bpy.data.meshes], margin=.003))
            bpy.ops.wm.save_mainfile(); P('UVs salvos')
        if etapa.startswith('lobby_bake'):
            quais = args[1].split(',') if len(args) > 1 else sorted(ATL)
            passe = args[2] if len(args) > 2 else 'color'
            size = int(args[3]) if len(args) > 3 else 2048
            spp = int(args[4]) if len(args) > 4 else 20
            for atlas in quais:
                P(k_materiais.bake(atlas, objs_de(atlas), passe, size=size, samples=spp, device='CPU'))
        if etapa == 'lobby_final':
            for atlas in sorted(ATL):
                P(k_materiais.finalize(atlas, objs_de(atlas), emis=True))
            for o in bpy.data.objects:
                if o.get('espelho_de'):
                    src = bpy.data.objects.get(o['espelho_de'])
                    if not src: continue
                    bm2 = bmesh.new(); bm2.from_mesh(src.data); bmesh.ops.scale(bm2, vec=(1, -1, 1), verts=bm2.verts)
                    bmesh.ops.reverse_faces(bm2, faces=bm2.faces); bm2.to_mesh(o.data); bm2.free()
                    o.data.materials.clear()
                    for m in src.data.materials: o.data.materials.append(m)
            bpy.ops.wm.save_mainfile(); P('materiais finais aplicados')
            place = json.load(open(os.path.join(KIT, 'lobby_placements.json')))
            path, info = k_export.export_kit(ATL, place, name='LOBBY_FORJA_CELESTE')
            P('FBX %s %.1f MB | %d malhas | %d tris' % (os.path.basename(path), os.path.getsize(path) / 1e6, len(info), sum(v['tris'] for v in info.values())))
            cols = [c.name for c in bpy.context.scene.collection.children if c.name.startswith('LOB_')]
            k_render.only(cols); k_render.sun(46, -32, 3.4)
            k_render.camera((150, 230, 120), (0, -20, 20), 30); P(k_render.eevee('M3_lobby_tex.png', res=(1600, 900)))
            k_render.camera((0, 40, 26), (0, -110, 30), 34); P(k_render.eevee('M4_eixo_tex.png', res=(1500, 850)))

    if etapa == 'jardim_bancada':             # constroi as pecas de jardim/vila numa bancada e renderiza para revisao
        import k_jardim, importlib; importlib.reload(k_jardim)
        from k_core import clear_col
        k_materiais.build_paints()
        clear_col('BANCADA4')
        x = 0; info = []
        pecas = [('peonia', lambda: k_jardim.peonia(1), 7), ('crisantemo', lambda: k_jardim.crisantemo(1), 7),
                 ('lotus', lambda: k_jardim.lotus(1), 8), ('ameixeira', lambda: k_jardim.ameixeira(1), 12),
                 ('canteiro', lambda: k_jardim.canteiro_flores(1), 11), ('grama', lambda: k_jardim.moita_grama(1), 6),
                 ('lant_pedra', lambda: k_jardim.lanterna_pedra(), 7), ('poco', lambda: k_jardim.poco(), 11),
                 ('barril', lambda: k_jardim.barril(), 5), ('cesto', lambda: k_jardim.cesto(), 5),
                 ('banco', lambda: k_jardim.banco(), 8), ('caixas', lambda: k_jardim.caixas(), 7),
                 ('telhas', lambda: k_jardim.telhas_pilha(), 5), ('varal', lambda: k_jardim.varal(), 13),
                 ('placa', lambda: k_jardim.placa_loja(), 8), ('carroca', lambda: k_jardim.carroca(), 0)]
        for key, fn, dx in pecas:
            B = fn(); tr = B.tris(); o = B.finish('BANCADA4', loc=(400 + x, 0, 0)); info.append('%s %d tris' % (o.name, tr)); x += dx
        P(chr(10).join(info))
        bpy.ops.wm.save_mainfile()
        k_render.only(['BANCADA4']); k_render.sun(46, -32, 3.4)
        k_render.camera((432, -44, 16), (432, 2, 4), 30); P(k_render.workbench('J1_flores.png', 'MATERIAL', res=(1500, 700)))
        k_render.camera((492, -46, 16), (492, 2, 5), 30); P(k_render.workbench('J2_vila.png', 'MATERIAL', res=(1500, 700)))

    if etapa == 'portal_bancada':
        import k_portal, importlib; importlib.reload(k_portal)
        from k_core import clear_col
        k_materiais.build_paints(); clear_col('BANCADA5')
        TEMAS = ['chakra', 'ki', 'nichirin', 'sombra', 'mare', 'serio']
        info = []
        for i, t in enumerate(TEMAS):                                          # um portal por area, lado a lado
            x = 600 + i * 26
            for fn in (lambda t=t: k_portal.portal_moldura(t), lambda t=t: k_portal.portal_camada(0, t),
                       lambda t=t: k_portal.portal_camada(1, t), lambda t=t: k_portal.portal_camada(2, t),
                       lambda t=t: k_portal.portal_base(t), lambda t=t: k_portal.portal_fragmento(1, t)):
                B = fn(); tr = B.tris(); o = B.finish('BANCADA5', loc=(x, 0, 0)); info.append('%s %d tris' % (o.name, tr))
        P(chr(10).join(info)); bpy.ops.wm.save_mainfile()
        k_render.only(['BANCADA5']); k_render.sun(46, -32, 3.4)
        k_render.camera((665, -120, 24), (665, 0, 11), 32); P(k_render.workbench('P2_portais_6.png', 'MATERIAL', res=(1900, 780)))
        k_render.camera((602, -40, 14), (601, 0, 11), 34); P(k_render.workbench('P1_portal.png', 'MATERIAL', res=(1100, 950)))

    if etapa == 'lobby':                      # monta o LOBBY inteiro, faz UV dos atlas, salva e renderiza a visao geral
        import k_montagem, importlib; importlib.reload(k_montagem)
        k_materiais.build_paints()
        K, rep = k_montagem.build_lobby()
        P(rep[-1])
        open(os.path.join(KIT, 'lobby_relatorio.txt'), 'w').write(chr(10).join(rep))
        json.dump(k_montagem.PLACE, open(os.path.join(KIT, 'lobby_placements.json'), 'w'))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(KIT, 'lobby_forja_celeste.blend'))
        P('blend do lobby salvo')
        cols = [c.name for c in bpy.context.scene.collection.children if c.name.startswith('LOB_')]
        k_render.only(cols); k_render.sun(46, -32, 3.4)
        gordas = []
        for c in cols:
            for o in bpy.data.collections[c].objects:
                if o.type != 'MESH': continue
                t = sum(len(pl.vertices) - 2 for pl in o.data.polygons)
                if t > 19000: gordas.append((o.data.name, t))
        P('malhas acima de 19 mil tris (teto do Roblox e 20 mil): %s' % (sorted(set(gordas)) or 'nenhuma'))
        place = k_montagem.PLACE
        ATL = {'A_LOBBY_%d' % i: [] for i in range(1, 7)}
        alvo = {}
        nomes = sorted({p['mesh'] for p in place})
        # distribui as malhas em 6 atlas por area de UV aproximada (numero de loops), para nenhum atlas ficar denso demais
        pesos = []
        for n in nomes:
            me = bpy.data.meshes.get(n)
            pesos.append((len(me.loops) if me else 0, n))
        pesos.sort(reverse=True)
        carga = {k: 0 for k in ATL}
        for w, n in pesos:
            k = min(carga, key=lambda a: carga[a]); ATL[k].append(n); carga[k] += w
        json.dump(ATL, open(os.path.join(KIT, 'lobby_atlas.json'), 'w'), indent=1)
        P('atlas do lobby: ' + ', '.join('%s=%d malhas/%d loops' % (k, len(v), carga[k]) for k, v in ATL.items()))
        k_render.camera((150, 230, 120), (0, -20, 20), 30); P(k_render.workbench('M1_lobby_geral.png', 'MATERIAL', res=(1600, 900)))
        k_render.camera((0, 40, 26), (0, -110, 30), 34); P(k_render.workbench('M2_eixo.png', 'MATERIAL', res=(1500, 850)))

    if etapa == 'lobby_bancada':              # constroi as pecas novas do lobby numa bancada e renderiza para revisao
        import k_lobby, importlib; importlib.reload(k_lobby)
        from k_core import clear_col, col
        k_materiais.build_paints()
        clear_col('BANCADA3')
        x = 0; info = []
        pecas = [('torre', lambda: k_lobby.torre_fogo(), 16), ('espada', lambda: k_lobby.espada_ancestral(), 12),
                 ('pedestal', lambda: k_lobby.pedestal_espada(), 26), ('fornalha', lambda: k_lobby.fornalha(), 22),
                 ('bigorna', lambda: k_lobby.bigorna(), 9), ('fole', lambda: k_lobby.fole(), 16),
                 ('calha', lambda: k_lobby.calha_tempera(), 12), ('altar', lambda: k_lobby.altar_laminas(), 16),
                 ('braseiro', lambda: k_lobby.braseiro(), 10), ('leao', lambda: k_lobby.leao(1), 10),
                 ('leao2', lambda: k_lobby.leao(-1), 14), ('ponte', lambda: k_lobby.ponte_lua(), 36),
                 ('rocha', lambda: k_lobby.rocha(1), 10), ('bambu', lambda: k_lobby.bambu(1), 10),
                 ('bordo', lambda: k_lobby.bordo(1), 14), ('poste_t', lambda: k_lobby.poste_treino(), 6),
                 ('boneco', lambda: k_lobby.boneco_treino(), 8), ('estante', lambda: k_lobby.estante_armas(), 0)]
        for key, fn, dx in pecas:
            B = fn(); tr = B.tris(); o = B.finish('BANCADA3', loc=(200 + x, 0, 0)); info.append('%s %d tris' % (o.name, tr)); x += dx
        P('\n'.join(info))
        bpy.ops.wm.save_mainfile()
        k_render.only(['BANCADA3']); k_render.sun(46, -32, 3.4)
        k_render.camera((232, -62, 26), (232, 2, 10), 30); P(k_render.workbench('L1_forja.png', 'MATERIAL', res=(1500, 760)))
        k_render.camera((336, -70, 24), (336, 2, 9), 30); P(k_render.workbench('L1_natureza.png', 'MATERIAL', res=(1500, 760)))
        tot = sum(sum(len(pl.vertices) - 2 for pl in o.data.polygons) for o in bpy.data.collections['BANCADA3'].objects)
        gordas = [(o.name, sum(len(pl.vertices) - 2 for pl in o.data.polygons)) for o in bpy.data.collections['BANCADA3'].objects]
        gordas = [g for g in gordas if g[1] > 15000]
        P('total bancada %d tris | acima de 15 mil: %s' % (tot, gordas or 'nenhuma'))
    P('fim %.1fs' % (time.time() - t0))
except Exception:
    P('ERRO'); print(traceback.format_exc()); sys.exit(1)
