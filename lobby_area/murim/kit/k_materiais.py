# k_materiais.py - materiais PINTADOS do kit e bake para atlas (Roblox: SurfaceAppearance ignora cor de vertice, entao a
# pintura - sombra de AO colorida, gradiente, variacao por peca, luz de cima, realce de aresta, brilho pintado - vai no ColorMap).
# Fluxo: build_paints() -> unwrap(atlas) -> bake(atlas, passe) -> finalize(atlas) (material unico por atlas para exportar).
import bpy, bmesh, os, time
from k_core import hex_lin, ctx, PAINTS

TEX = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\murim\kit\tex"
os.makedirs(TEX, exist_ok=True)

#        base      sombra    realce    rough var  edge  ao   face spec emis
PD = {
    'verm':     ('B8321E', '5A1208', 'F07A55', .40, .07, .42, .80, .10, .10, 0),
    'vermS':    ('8E2718', '430C06', 'C8492E', .52, .07, .35, .80, .10, .0, 0),
    'ouro':     ('C28A2C', '6E3A0C', 'F2C866', .45, .06, .40, .70, .06, .28, 0),
    'bronze':   ('80602A', '36230C', 'C9A45C', .50, .07, .40, .75, .06, .22, 0),
    'mad':      ('4A2E1E', '1E1009', '8A6040', .66, .10, .40, .80, .10, .0, 0),
    'madM':     ('7A4B2A', '3A1E0E', 'B98452', .66, .10, .40, .80, .10, .0, 0),
    'pedra':    ('B09971', '6E5C40', 'D9CBAE', .86, .09, .40, .85, .04, .0, 0),
    'piso':     ('978362', '574B39', 'C2B69C', .88, .12, .35, .85, .03, .0, 0),
    'junta':    ('7E745F', '403829', '9A8F78', .92, .06, .15, .85, .05, .0, 0),
    'telha':    ('2E5A4C', '0F2A24', '6FB49C', .36, .12, .45, .80, .12, .30, 0),
    'telhaImp': ('D4A034', '86500E', 'FFE596', .38, .10, .45, .80, .12, .35, 0),
    'jade':     ('3E7D6E', '15382F', '9ADBC6', .50, .06, .55, .80, .10, .08, 0),
    'jadeE':    ('2E5A4C', '0F2722', '72B7A2', .50, .06, .50, .80, .10, .08, 0),
    'creme':    ('CDB98A', '8C7040', 'E2D2A8', .78, .04, .15, .70, .0, .0, 0),
    'ferro':    ('2B2624', '0C0A09', '6A605C', .55, .05, .40, .80, .10, .15, 0),
    'chama':    ('FFC84A', 'E08A22', 'FFF4C8', .60, .03, .15, .35, .04, .0, 1),
    'pinho':    ('3E6B3A', '15331F', '9CC85E', .85, .10, .30, .85, .34, .0, 0),
    'folha':    ('6E9A45', '2A5226', 'D2E887', .85, .10, .30, .85, .34, .0, 0),
    'casca':    ('7A5638', '3E2614', 'A98058', .88, .10, .40, .60, .10, .0, 0),
    'bordo':    ('C4432B', '5E140C', 'F59A5A', .85, .10, .30, .85, .30, .0, 0),
    'tecido':   ('A8261A', '4E0B06', 'E9603F', .82, .06, .30, .80, .10, .0, 0),
    'aco':      ('B9C2CC', '4A5664', 'F2F6FA', .34, .04, .55, .70, .08, .35, 0),
    'agua':     ('3FA0A0', '14545C', '9FE8E0', .20, .05, .30, .60, .08, .45, 0),
    'brasa':    ('FF7A1A', 'C23A06', 'FFD79A', .70, .06, .10, .30, .04, .0, 1),
    'bambu':     ('7FA85A', '2F4A22', 'C6E28A', 0.85, 0.10, 0.30, 0.85, 0.30, 0.00, 0),
    'palha':    ('C9A86A', '7A5A2E', 'EFD9A4', .90, .12, .35, .85, .10, .0, 0),
    'corte':    ('1E1A18', '0A0908', '2A2522', .9, .0, .0, .5, .0, .0, 0),
}

def _n(nt, typ, **kw):
    n = nt.nodes.new(typ)
    for k, v in kw.items(): setattr(n, k, v)
    return n

def build_paint(key):
    base, shad, high, rough, var, edge, ao, face, spec, emis = PD[key]
    m = bpy.data.materials.get('P_' + key) or bpy.data.materials.new('P_' + key)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    out = _n(nt, 'ShaderNodeOutputMaterial'); em = _n(nt, 'ShaderNodeEmission'); em.name = 'EMIT'
    bs = _n(nt, 'ShaderNodeBsdfPrincipled'); bs.name = 'BSDF'; bs.inputs['Roughness'].default_value = rough
    bs.inputs['Base Color'].default_value = (*hex_lin(base), 1)
    geo = _n(nt, 'ShaderNodeNewGeometry'); tc = _n(nt, 'ShaderNodeTexCoord')
    def math(op, a, b=None, clamp=False):
        n = _n(nt, 'ShaderNodeMath', operation=op, use_clamp=clamp)
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: L(v, n.inputs[i])
        return n.outputs[0]
    def mixc(mode, fac, c1, c2):
        n = _n(nt, 'ShaderNodeMixRGB', blend_type=mode)
        if isinstance(fac, (int, float)): n.inputs[0].default_value = fac
        else: L(fac, n.inputs[0])
        for i, c in ((1, c1), (2, c2)):
            if isinstance(c, tuple): n.inputs[i].default_value = c
            else: L(c, n.inputs[i])
        return n.outputs[0]
    def ramp(v, p0, p1):
        n = _n(nt, 'ShaderNodeValToRGB'); n.color_ramp.elements[0].position = p0; n.color_ramp.elements[1].position = p1; L(v, n.inputs[0]); return n.outputs[0]
    # --- fatores escalares
    sep = _n(nt, 'ShaderNodeSeparateXYZ'); L(tc.outputs['Generated'], sep.inputs[0])
    grad = math('ADD', math('MULTIPLY', sep.outputs['Z'], .17), .83)                                    # escuro embaixo, claro em cima (por peca)
    att = _n(nt, 'ShaderNodeAttribute'); att.attribute_name = 'rnd'
    sepc = _n(nt, 'ShaderNodeSeparateColor'); L(att.outputs['Color'], sepc.inputs[0])
    vr = math('ADD', math('MULTIPLY', math('SUBTRACT', sepc.outputs[0], .5), var * 2), 1.0)             # variacao por peca
    nz = _n(nt, 'ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = .22; nz.inputs['Detail'].default_value = 1.5; L(tc.outputs['Object'], nz.inputs['Vector'])
    nv = math('ADD', math('MULTIPLY', math('SUBTRACT', nz.outputs[0], .5), .12), 1.0)                   # mancha larga de pincel
    nsep = _n(nt, 'ShaderNodeSeparateXYZ'); L(geo.outputs['Normal'], nsep.inputs[0])
    fc = math('ADD', math('MULTIPLY', nsep.outputs['Z'], face), 1.0)                                    # luz pintada vinda de cima
    mval = math('MULTIPLY', math('MULTIPLY', grad, vr), math('MULTIPLY', nv, fc))
    col = mixc('MULTIPLY', 1.0, (*hex_lin(base), 1), mval)
    # --- sombra de AO colorida
    aon = _n(nt, 'ShaderNodeAmbientOcclusion'); aon.samples = 16; aon.inputs['Distance'].default_value = 1.8
    aof = ramp(aon.outputs['AO'], .22, .88)
    sh = mixc('MULTIPLY', 1.0, (*hex_lin(shad), 1), mval)
    col = mixc('MIX', math('ADD', math('MULTIPLY', aof, ao * .82), 1 - ao * .82), sh, col)
    # --- realce de aresta convexa: desvio entre a normal "chanfrada" (Bevel node, so a propria malha) e a normal real,
    #     multiplicado pelo AO para nao acender os cantos concavos. (Testados e descartados: AO "por dentro" - as pecas do
    #     kit se interpenetram e tudo virava aresta; Pointiness - em malha hard-surface todo vertice e de aresta.)
    bvn = _n(nt, 'ShaderNodeBevel'); bvn.samples = 6; bvn.inputs['Radius'].default_value = .075
    dte = _n(nt, 'ShaderNodeVectorMath', operation='DOT_PRODUCT'); L(bvn.outputs['Normal'], dte.inputs[0]); L(geo.outputs['Normal'], dte.inputs[1])
    edg = math('MULTIPLY', ramp(math('SUBTRACT', 1.0, dte.outputs['Value']), .015, .16), aof)
    col = mixc('MIX', math('MULTIPLY', edg, edge), col, (*hex_lin(high), 1))
    # --- brilho pintado (ouro, bronze, telha vidrada): mancha de luz fixa, independente da camera
    if spec > 0:
        dot = _n(nt, 'ShaderNodeVectorMath', operation='DOT_PRODUCT'); L(geo.outputs['Normal'], dot.inputs[0]); dot.inputs[1].default_value = (-.35, -.55, .76)
        sp = math('MULTIPLY', math('POWER', math('MAXIMUM', dot.outputs['Value'], 0.0), 9.0), spec, clamp=True)
        col = mixc('SCREEN', sp, col, (*hex_lin(high), 1))
    L(col, em.inputs['Color'])
    cR = _n(nt, 'ShaderNodeRGB'); cR.name = 'C_ROUGH'; cR.outputs[0].default_value = (rough, rough, rough, 1)
    cE = _n(nt, 'ShaderNodeRGB'); cE.name = 'C_EMIS'; cE.outputs[0].default_value = (emis, emis, emis, 1)
    rr = _n(nt, 'NodeReroute'); rr.name = 'C_COLOR'; L(col, rr.inputs[0])
    bev = _n(nt, 'ShaderNodeBevel'); bev.samples = 8; bev.inputs['Radius'].default_value = .09; L(bev.outputs['Normal'], bs.inputs['Normal'])
    img = _n(nt, 'ShaderNodeTexImage'); img.name = 'BAKE'
    L(em.outputs[0], out.inputs['Surface'])
    m.diffuse_color = (*hex_lin(base), 1)
    return m

def build_paints():
    for k in PD: build_paint(k)

def set_pass(which):
    """liga a saida de todos os P_* conforme o passe: color | rough | emis | normal."""
    for k in PD:
        m = bpy.data.materials.get('P_' + k)
        if not m: continue
        nt = m.node_tree; L = nt.links.new; out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'); em = nt.nodes['EMIT']
        if which == 'normal': L(nt.nodes['BSDF'].outputs[0], out.inputs['Surface'])
        else:
            L(em.outputs[0], out.inputs['Surface'])
            src = {'color': nt.nodes['C_COLOR'].outputs[0], 'rough': nt.nodes['C_ROUGH'].outputs[0], 'emis': nt.nodes['C_EMIS'].outputs[0]}[which]
            L(src, em.inputs['Color'])

def unwrap(atlas, meshes, margin=.004):
    """junta as malhas unicas do atlas numa malha temporaria, faz smart project + pack e copia as UVs de volta."""
    t0 = time.time(); bm = bmesh.new(); spans = []
    for me in meshes:
        a = sum(len(f.verts) for f in bm.faces); bm.from_mesh(me); b = sum(len(f.verts) for f in bm.faces); spans.append((me, a, b))
    tmp = bpy.data.meshes.new('_uv_' + atlas); bm.to_mesh(tmp); bm.free()
    o = bpy.data.objects.new('_uv_' + atlas, tmp); bpy.context.scene.collection.objects.link(o)
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    try:
        with bpy.context.temp_override(**ctx(), active_object=o, object=o, selected_objects=[o], selected_editable_objects=[o]): bpy.ops.object.mode_set(mode='EDIT')
        be = bmesh.from_edit_mesh(tmp)
        for f in be.faces: f.select = True
        bmesh.update_edit_mesh(tmp)
        with bpy.context.temp_override(**ctx(), active_object=o, object=o, edit_object=o, selected_objects=[o], selected_editable_objects=[o]):
            bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=margin, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    finally:
        with bpy.context.temp_override(**ctx(), active_object=o, object=o, selected_objects=[o]): bpy.ops.object.mode_set(mode='OBJECT')
    src = tmp.uv_layers.active.data
    for me, a, b in spans:
        uv = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap'); me.uv_layers.active = uv
        assert len(me.loops) == b - a, (me.name, len(me.loops), b - a)
        buf = [0.0] * (2 * (b - a)); full = [0.0] * (2 * len(src)); src.foreach_get('uv', full); buf = full[2 * a:2 * b]; uv.data.foreach_set('uv', buf)
    bpy.data.objects.remove(o, do_unlink=True); bpy.data.meshes.remove(tmp)
    return '%s: %d malhas, %d loops, %.1fs' % (atlas, len(meshes), spans[-1][2], time.time() - t0)

def bake(atlas, objs, which, size=2048, samples=32, device='GPU'):
    """assa um passe para o atlas. objs = UM objeto por malha unica (na posicao de montagem, para o AO pegar o contexto)."""
    t0 = time.time(); sc = bpy.context.scene; eng0 = sc.render.engine
    name = '%s_%s' % (atlas, which); img = bpy.data.images.get(name)
    if img is None or img.size[0] != size:
        if img: bpy.data.images.remove(img)
        img = bpy.data.images.new(name, size, size, alpha=False)
    img.colorspace_settings.name = 'sRGB' if which == 'color' else 'Non-Color'
    for k in PD:
        m = bpy.data.materials.get('P_' + k)
        if m: n = m.node_tree.nodes['BAKE']; n.image = img; m.node_tree.nodes.active = n; n.select = True
    set_pass(which)
    sc.render.engine = 'CYCLES'; sc.cycles.device = device; sc.cycles.samples = samples; sc.cycles.use_denoising = False
    try: bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'HIP'; bpy.context.preferences.addons['cycles'].preferences.get_devices()
    except Exception: pass
    for ob in bpy.context.view_layer.objects: ob.select_set(False)
    for ob in objs: ob.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    try:
        with bpy.context.temp_override(**ctx(), active_object=objs[0], object=objs[0], selected_objects=objs, selected_editable_objects=objs):
            bpy.ops.object.bake(type='NORMAL' if which == 'normal' else 'EMIT', margin=6, use_clear=True, normal_space='TANGENT')
    finally:
        sc.render.engine = eng0; set_pass('color')
    # protecao: o operador de bake pode devolver FINISHED e nao assar NADA (imagem preta, sem excecao). Medir sempre.
    #   cor: fracao de pixels nao pretos; normal: fracao com azul alto; rough/emis: aceita preto (emissivo e quase todo preto).
    n = size * size; px = [0.0] * (n * 4); img.pixels.foreach_get(px)
    if which == 'color': cheio = sum(1 for i in range(0, n * 4, 4 * 97) if px[i] + px[i + 1] + px[i + 2] > .02) / (n / 97)
    elif which == 'normal': cheio = sum(1 for i in range(0, n * 4, 4 * 97) if px[i + 2] > .4) / (n / 97)
    else: cheio = 1.0
    if cheio < .15: raise RuntimeError('BAKE VAZIO em %s: so %.1f%% da imagem tem conteudo (o operador nao assou)' % (name, cheio * 100))
    path = os.path.join(TEX, name + '.png'); img.filepath_raw = path; img.file_format = 'PNG'; img.save()
    return '%s %.1fs cobertura %.0f%% -> %s' % (name, time.time() - t0, cheio * 100, path)

def final_material(atlas, maps=('color', 'normal', 'rough'), emis=False):
    m = bpy.data.materials.get('F_' + atlas) or bpy.data.materials.new('F_' + atlas)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear(); L = nt.links.new
    out = _n(nt, 'ShaderNodeOutputMaterial'); bs = _n(nt, 'ShaderNodeBsdfPrincipled'); L(bs.outputs[0], out.inputs['Surface'])
    def tex(which, cs):
        p = os.path.join(TEX, '%s_%s.png' % (atlas, which))
        if not os.path.exists(p): return None
        im = bpy.data.images.load(p, check_existing=True); im.reload(); im.colorspace_settings.name = cs
        n = _n(nt, 'ShaderNodeTexImage'); n.image = im; return n
    c = tex('color', 'sRGB')
    if c: L(c.outputs[0], bs.inputs['Base Color'])
    r = tex('rough', 'Non-Color')
    if r: L(r.outputs[0], bs.inputs['Roughness'])
    nm = tex('normal', 'Non-Color')
    if nm:
        nn = _n(nt, 'ShaderNodeNormalMap'); L(nm.outputs[0], nn.inputs['Color']); L(nn.outputs[0], bs.inputs['Normal'])
    if emis:
        e = tex('emis', 'Non-Color')
        if e and c:
            L(c.outputs[0], bs.inputs['Emission Color']); L(e.outputs[0], bs.inputs['Emission Strength'])
    return m

def finalize(atlas, objs, emis=False):
    """troca as tintas (varios slots) pelo material final do atlas (um slot) nas malhas unicas; e o que sera exportado."""
    m = final_material(atlas, emis=emis); n = 0
    for o in objs:
        me = o.data
        me.materials.clear(); me.materials.append(m)
        idx = [0] * len(me.polygons); me.polygons.foreach_set('material_index', idx); me.update(); n += 1
    return '%s -> F_%s em %d malhas' % (atlas, atlas, n)
