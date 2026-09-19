# trecho_arvores.py - arvores douradas (plumas altas) e tufos dos plantios, pela silhueta da referencia:
# pluma alta e estreita, mais cheia no terco inferior/medio, afinando para a ponta, com fios/barbas legiveis.
# Construcao: caule torneado + cards cruzados com textura de pluma (alpha) em 3 tiers de tamanho decrescente,
# mais plumas laterais menores inclinadas (variacao interna). Tufos: esfera deslocada + cards de tufo.
import bpy, bmesh, math, random, os
from mathutils import Vector, Matrix
import trecho_torre as T
from trecho_torre import new_obj, clear

TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tex_trecho')

def mat_alpha(name, fn):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.get('Tex') or nt.nodes.new('ShaderNodeTexImage'); tex.name = 'Tex'
    img = bpy.data.images.get(fn) or bpy.data.images.load(os.path.join(TEX, fn)); img.name = fn
    tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color']); nt.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])
    bsdf.inputs['Roughness'].default_value = .85
    m.blend_method = 'HASHED'
    try: m.shadow_method = 'HASHED'
    except Exception: pass
    m.diffuse_color = (.9, .72, .32, 1)
    return m

def card(bm, w, h, mat_index=0):
    """plano vertical (x largura, z altura) com UV completo, base em z=0."""
    v = [bm.verts.new((-w / 2, 0, 0)), bm.verts.new((w / 2, 0, 0)), bm.verts.new((w / 2, 0, h)), bm.verts.new((-w / 2, 0, h))]
    f = bm.faces.new(v); f.material_index = mat_index
    uv = bm.loops.layers.uv.verify()
    for l, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        l[uv].uv = co
    return f

def plume_tree(col, pos, h=22.0, w=5.6, seed=1, name='PLUMA'):
    rnd = random.Random(seed)
    x, y, z0 = pos
    mA = mat_alpha('T_PLUMA', 'pluma_ouro.png'); mB = mat_alpha('T_PLUMA2', 'pluma_ouro2.png')
    # caule: torneado fino, ligeiramente inclinado
    import trecho_poste as P
    bm = P.spin([(.22, 0), (.17, h * .25), (.10, h * .55), (.03, h * .8)], 10)
    bmesh.ops.translate(bm, vec=(x, y, z0), verts=bm.verts)
    objs = [new_obj(f'{name}_caule', bm, col, T.M('T_CAULE', (.45, .36, .24)))]
    # cards: 3 tiers x 3 planos cruzados (60 graus), tamanhos decrescentes, leve rotacao/inclinacao aleatoria
    bm = bmesh.new()
    tiers = ((0.0, 1.0, .58), (h * .28, .86, .50), (h * .52, .68, .40))    # (z inicio, escala altura, escala largura)
    for tz, sh_, sw_ in tiers:
        for k in range(3):
            a = k * math.pi / 3 + rnd.uniform(-.15, .15)
            f = card(bm, w * sw_ * 2, h * sh_ * (1 - tz / h) if tz else h, 0 if rnd.random() < .5 else 1)
            vs = list(f.verts)
            tilt = rnd.uniform(-.05, .05)
            M_ = Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(tilt, 4, 'X')
            for v in vs: v.co = M_ @ v.co + Vector((x, y, z0 + tz))
    # plumas laterais menores (variacao interna da silhueta)
    for k in range(4):
        a = rnd.uniform(0, math.tau); r = w * .22
        f = card(bm, w * .9, h * .38, rnd.randint(0, 1))
        M_ = Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(rnd.uniform(.12, .3), 4, 'Y')
        for v in f.verts: v.co = M_ @ v.co + Vector((x + math.cos(a) * r, y + math.sin(a) * r, z0 + h * rnd.uniform(.18, .42)))
    # faces dupla: duplica com normal invertida (Roblox DoubleSided tambem sera ligado)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = new_obj(f'{name}_folhas', bm, col, mA); o.data.materials.append(mB)
    objs.append(o)
    return objs

def tuft_bush(col, pos, r=1.5, seed=1, name='TUFO'):
    rnd = random.Random(seed)
    x, y, z0 = pos
    mT = mat_alpha('T_TUFO', 'tufo_ouro.png')
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    for v in bm.verts:
        v.co *= 1 + (rnd.random() - .5) * .3
        v.co.z *= .8
    bmesh.ops.translate(bm, vec=(x, y, z0 + r * .75), verts=bm.verts)
    core = new_obj(f'{name}_miolo', bm, col, T.M('T_TUFO_MIOLO', (.86, .66, .25), .9))
    # cards de tufo ao redor (alpha) para bordas fofas
    bm = bmesh.new()
    for k in range(8):
        a = k / 8 * math.tau + rnd.uniform(-.2, .2)
        f = card(bm, r * 2.2, r * 2.0)
        M_ = Matrix.Rotation(a, 4, 'Z') @ Matrix.Rotation(rnd.uniform(-.2, .2), 4, 'X')
        for v in f.verts: v.co = M_ @ v.co + Vector((x, y, z0 - r * .2))
    for k in range(3):
        f = card(bm, r * 2.2, r * 2.0)
        M_ = Matrix.Rotation(rnd.uniform(0, math.tau), 4, 'Z') @ Matrix.Rotation(math.pi / 2, 4, 'X')
        for v in f.verts: v.co = M_ @ v.co + Vector((x, y, z0 + r * .8 + k * .2))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return [core, new_obj(f'{name}_cards', bm, col, mT)]

def build_all(plumes, tufts):
    col = clear('ARVORES')
    objs = []
    for i, (pos, h, w) in enumerate(plumes):
        objs += plume_tree(col, pos, h, w, seed=3 + i, name=f'PLUMA{i}')
    for i, (pos, r) in enumerate(tufts):
        objs += tuft_bush(col, pos, r, seed=11 + i, name=f'TUFO{i}')
    return objs
