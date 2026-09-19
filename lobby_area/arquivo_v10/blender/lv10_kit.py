# lv10_kit.py - kit V10: pecas com relevo real (molduras, arcos recuados, cornijas com dentículos,
# poste da referencia, urnas, balaustres) e materiais com TEXTURA autoral (export/tex/*.png).
# Prefixo do material == nome do objeto exportado (PREFIXO__nome) -> script do Studio aplica
# Material/Color/SurfaceAppearance. Unidades: studs. Z para cima.
import bpy, bmesh, math, os, random, importlib, sys
from mathutils import Vector, Matrix, Euler
sys.path.insert(0, r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\blender")
import lvlib
importlib.reload(lvlib)
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, ring_prism, reg_poly, puff_cloud, merge, _xform

TAU = math.tau
TEX = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\export\tex"

# nome -> (cor base rgb, textura cor, textura normal, textura roughness, escala UV mundo (1/studs))
MATS10 = {
    'SDK': ((128, 118, 106), 't_stone_dark.png', 't_stone_dark_n.png', None, 1/24),   # (legado) pedra escura
    'SMD': ((190, 182, 168), 't_stone_mid.png', 't_stone_mid_n.png', None, 1/22),     # corpo da torre: pedra clara-media quente
    'SLT': ((228, 223, 212), 't_stone_light.png', 't_stone_light_n.png', None, 1/20), # marfim: molduras, pilastras, cornijas
    'ASH': ((212, 206, 194), 't_ashlar.png', 't_ashlar_n.png', None, 1/16),           # muretas, faces de plataforma
    'FLR': ((214, 207, 192), 't_floor.png', 't_floor_n.png', None, 1/28),             # piso da praca (lajotas irregulares)
    'FLL': ((222, 216, 202), 't_floor_light.png', 't_floor_light_n.png', None, 1/28), # piso do patamar/terraco
    'FLF': ((222, 216, 202), 't_floor_leaf.png', 't_floor_leaf_n.png', None, 1/28),   # piso com folhas caidas (bordas/canteiros)
    'GLD': ((226, 180, 82), 't_gold.png', None, 't_gold_r.png', 1/8),                 # dourado quente
    'LPS': ((34, 78, 190), 't_lapis.png', None, None, 1/16),                          # azul embutido
    'GRS': ((110, 186, 88), 't_grass.png', None, None, 1/10),                         # grama de canteiro
    'RCK': ((132, 136, 142), 't_rock.png', 't_rock_n.png', None, 1/24),               # rocha
    'SLA': ((96, 112, 132), 't_slate.png', None, None, 1/12),                         # ardosia
    'MLK': ((240, 242, 236), 't_milk.png', None, None, 1/2),                          # vidro leitoso da lanterna
    'EMB': ((255, 128, 40), None, None, None, None),                                  # brasa (Neon)
    'FRG': ((255, 208, 110), None, None, None, None),                                 # vitral dourado luminoso (Neon)
    'CYN': ((120, 225, 255), None, None, None, None),                                 # ciano luminoso (cristal)
    'GLS': ((120, 190, 215), None, None, None, None),                                 # vidro das cupulas
    'WTR': ((52, 170, 210), None, None, None, None),                                  # agua (fallback; no Studio vira Terrain)
    'FOAM': ((236, 248, 250), None, None, None, None),                                # espuma (pe de queda d'agua)
    'DRK': ((28, 26, 30), None, None, None, None),                                    # fundo escuro dos vaos
    'LFG': ((236, 192, 86), 't_leaf_gold.png', None, None, 1/5),                     # folhagem dourada (textura de massa foliar)
    'LFG2': ((222, 168, 60), 't_leaf_gold2.png', None, None, 1/5),
    'LFV': ((104, 178, 90), 't_leaf_green.png', None, None, 1/6),                    # folhagem verde
    'LFP': ((242, 216, 150), None, None, None, None),                                 # plumas palidas (capim-dos-pampas)
    'TRK': ((92, 70, 52), None, None, None, None),                                    # tronco
    'FLW': ((246, 176, 206), None, None, None, None),                                 # flores rosas
    'WHT': ((236, 236, 232), None, None, None, None),                                 # branco liso (petalas, fuste)
}
for k, v in MATS10.items():
    lvlib.MATS[k] = v[0]

def _img(fn):
    if fn is None:
        return None
    p = os.path.join(TEX, fn)
    im = bpy.data.images.get(fn)
    if im is None or not os.path.exists(im.filepath_raw or ''):
        im = bpy.data.images.load(p, check_existing=True)
        im.name = fn
    else:
        im.reload()
    return im

def mat(name):
    """material Principled com texturas ligadas (Base Color / Normal / Roughness) para o FBX."""
    rgb, tc, tn, tr, _ = MATS10[name]
    m = bpy.data.materials.get('LV10_' + name)
    if m is None:
        m = bpy.data.materials.new('LV10_' + name)
        m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    bsdf.inputs['Base Color'].default_value = (rgb[0]/255, rgb[1]/255, rgb[2]/255, 1)
    bsdf.inputs['Roughness'].default_value = 0.35 if name == 'GLD' else 0.8
    if name == 'GLD':
        bsdf.inputs['Metallic'].default_value = 1.0
    if name in ('EMB', 'FRG', 'CYN'):
        bsdf.inputs['Emission Color'].default_value = (rgb[0]/255, rgb[1]/255, rgb[2]/255, 1)
        bsdf.inputs['Emission Strength'].default_value = 3.0
    def texnode(nm, fn, cs='sRGB'):
        n = nt.nodes.get(nm)
        if fn is None:
            if n: nt.nodes.remove(n)
            return None
        if n is None:
            n = nt.nodes.new('ShaderNodeTexImage'); n.name = nm
        n.image = _img(fn)
        n.image.colorspace_settings.name = cs
        return n
    c = texnode('ColorTex', tc)
    if c:
        nt.links.new(c.outputs['Color'], bsdf.inputs['Base Color'])
    r = texnode('RoughTex', tr, 'Non-Color')
    if r:
        nt.links.new(r.outputs['Color'], bsdf.inputs['Roughness'])
    n = texnode('NormalTex', tn, 'Non-Color')
    nm = nt.nodes.get('NormalMap')
    if n:
        if nm is None:
            nm = nt.nodes.new('ShaderNodeNormalMap'); nm.name = 'NormalMap'
        nt.links.new(n.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    elif nm:
        nt.nodes.remove(nm)
    return m

def mats():
    return {k: mat(k) for k in MATS10}

UV_WORLD = tuple(k for k, v in MATS10.items() if v[4])
UV_SCALE = {k: v[4] for k, v in MATS10.items() if v[4]}

def _rz(pos, rot_z, about=(0, 0, 0)):
    x, y = pos[0] - about[0], pos[1] - about[1]
    c, s = math.cos(rot_z), math.sin(rot_z)
    return (about[0] + x * c - y * s, about[1] + x * s + y * c, pos[2])

def noisy_ball(r, pos, seed=1, seg=10, amp=.25, scl=(1, 1, 1)):
    """pedra: esfera com vertices deslocados (facetas suaves)"""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
    rnd = random.Random(seed)
    for v in bm.verts:
        v.co *= 1 + (rnd.random() - .5) * 2 * amp
    bmesh.ops.scale(bm, vec=scl, verts=bm.verts)
    return _xform(bm, pos)

# ---------------------------------------------------------------- POSTE (ref. imagem do poste)
def lamp_post(out, pos, scale=1.0):
    """Poste v2 (ref. imagem do poste): plinto redondo + anel de ouro no pe; fuste branco liso com entasis;
    punho de ouro; taca; 8 petalas grandes viradas para fora + 8 sepalas baixas; lanterna octogonal com
    base de ouro, barras verticais e bracadeiras em X douradas, vidro leitoso; tampa: anel de ouro,
    disco branco largo com aro de ouro, tambor de ouro e agulha. Altura total ~13*s (~2,5 avatares)."""
    s = scale
    x, y, z = pos
    # plinto + anel do pe
    out.add('SLT', lathe([(.95*s, 0), (.95*s, .3*s), (.8*s, .42*s), (.6*s, .5*s)], (x, y, z), seg=16))
    out.add('GLD', lathe([(.58*s, 0), (.6*s, .12*s), (.56*s, .3*s), (.46*s, .36*s)], (x, y, z + .5*s), seg=16))
    # fuste com entasis leve
    H = 6.3 * s
    z0 = z + .86 * s
    out.add('WHT', lathe([(.42*s, 0), (.45*s, H*.25), (.41*s, H*.6), (.35*s, H)], (x, y, z0), seg=18))
    # punho de ouro + taca branca
    top = z0 + H
    out.add('GLD', lathe([(.36*s, 0), (.5*s, .12*s), (.5*s, .38*s), (.4*s, .46*s)], (x, y, top - .1*s), seg=16))
    out.add('WHT', lathe([(.34*s, 0), (.55*s, .35*s), (.72*s, .75*s), (.66*s, .95*s)], (x, y, top + .36*s), seg=16))
    # petalas grandes: 8, base na taca, ponta virada para fora e um pouco enrolada
    for i in range(8):
        a = i / 8 * TAU
        bm = ball(.7*s, (0, 0, 0), seg=10, scl=(.5, .95, 1.9))
        _xform(bm, (0, 0, 0), (math.radians(34), 0, 0))            # tomba para fora (eixo Y local)
        _xform(bm, (0, 0, .0), (0, 0, a + math.pi/2))
        _xform(bm, (x + math.cos(a)*.72*s, y + math.sin(a)*.72*s, top + 1.65*s))
        out.add('WHT', bm)
        # ponta da petala levemente enrolada para fora (discreta)
        out.add('WHT', ball(.16*s, (x + math.cos(a)*1.28*s, y + math.sin(a)*1.28*s, top + 2.55*s), seg=7, scl=(1.1, 1.1, .7)))
    # sepalas baixas e mais abertas
    for i in range(8):
        a = (i + .5) / 8 * TAU
        bm = ball(.42*s, (0, 0, 0), seg=8, scl=(.45, .9, 1.5))
        _xform(bm, (0, 0, 0), (math.radians(58), 0, 0))
        _xform(bm, (0, 0, 0), (0, 0, a + math.pi/2))
        _xform(bm, (x + math.cos(a)*.8*s, y + math.sin(a)*.8*s, top + 1.0*s))
        out.add('WHT', bm)
    # lanterna octogonal
    lz = top + 2.15 * s
    LH = 1.55 * s
    R8 = .6 * s
    out.add('GLD', ngon_prism(reg_poly(R8 + .12*s, 8, TAU/16), .16*s, (x, y, lz - .16*s)))      # base
    out.add('MLK', ngon_prism(reg_poly(R8, 8, TAU/16), LH, (x, y, lz)))                          # vidro
    for i in range(8):
        a = i / 8 * TAU + TAU/16
        out.add('GLD', box((.09*s, .09*s, LH), (x + math.cos(a)*(R8 + .02*s), y + math.sin(a)*(R8 + .02*s), lz + LH/2), (0, 0, a)))
    # bracadeiras em X em cada face
    fr = R8 * math.cos(TAU/16) + .03*s
    fw = 2 * R8 * math.sin(TAU/16)
    L = math.hypot(fw, LH) * .92
    for i in range(8):
        a = i / 8 * TAU
        for tilt in (math.atan2(fw, LH), -math.atan2(fw, LH)):
            bm = box((.06*s, .06*s, L), (0, 0, 0))
            _xform(bm, (0, 0, 0), (tilt, 0, 0))              # inclina no plano da face (normal = X local)
            _xform(bm, (0, 0, 0), (0, 0, a))
            _xform(bm, (x + math.cos(a)*fr, y + math.sin(a)*fr, lz + LH/2))
            out.add('GLD', bm)
    # tampa
    cz = lz + LH
    out.add('GLD', ngon_prism(reg_poly(R8 + .14*s, 8, TAU/16), .14*s, (x, y, cz)))
    out.add('WHT', lathe([(1.05*s, 0), (1.08*s, .2*s), (.98*s, .34*s), (.8*s, .44*s)], (x, y, cz + .14*s), seg=18))
    out.add('GLD', torus(1.07*s, .06*s, (x, y, cz + .2*s), seg=18, sides=6))
    out.add('GLD', lathe([(.55*s, 0), (.58*s, .1*s), (.5*s, .55*s), (.56*s, .66*s), (.3*s, .78*s), (.32*s, .9*s), (.03*s, 2.0*s)], (x, y, cz + .56*s), seg=14))

# ---------------------------------------------------------------- ARCOS COM PROFUNDIDADE
def _arc_pts(w, spring, apex, n=14, pointed=True):
    """pontos do intradorso (x,z) de -w/2 a +w/2, do arranque ate o apice e de volta."""
    pts = []
    if pointed:
        R = w  # arco ogival equilatero: centros nos arranques opostos
        cx = w / 2  # centro do arco esquerdo em (+w/2, spring)
        ang_top = math.acos((w/2) / R)
        for i in range(n + 1):
            a = math.pi - (math.pi - ang_top) * (i / n)     # de 180 -> ang_top (lado esquerdo)
            pts.append((cx + math.cos(a) * R, spring + math.sin(a) * R))
        for i in range(n, -1, -1):
            a = math.pi - (math.pi - ang_top) * (i / n)
            pts.append((-cx - math.cos(a) * R, spring + math.sin(a) * R))
        # reescala para o apice pedido
        h0 = max(p[1] for p in pts) - spring
        k = (apex - spring) / h0 if h0 > 0 else 1
        pts = [(px, spring + (pz - spring) * k) for px, pz in pts]
    else:
        R = w / 2
        for i in range(2 * n + 1):
            a = math.pi - math.pi * (i / (2 * n))
            pts.append((math.cos(a) * R, spring + math.sin(a) * R * ((apex - spring) / R)))
    return pts

def _half_arc(w, spring, apex, pointed=True, n=12):
    """metade ESQUERDA do intradorso: do arranque (-w/2, spring) ate o apice (0, apex), em (x,z)."""
    pts = []
    if pointed:
        R = w; cx = w / 2                       # centro no arranque oposto
        a0, a1 = math.pi, 2 * math.pi / 3       # 180 -> 120 graus
        nat = R * math.sin(a1)                  # altura natural do apice acima do arranque
        k = (apex - spring) / nat
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            pts.append((cx + math.cos(a) * R, spring + math.sin(a) * R * k))
    else:
        R = w / 2
        k = (apex - spring) / R
        for i in range(n + 1):
            a = math.pi - (math.pi / 2) * i / n
            pts.append((math.cos(a) * R, spring + math.sin(a) * R * k))
    pts[0] = (-w / 2, spring); pts[-1] = (0, apex)
    return pts

def arch_opening(out, pos, W, Htop, w, spring, apex, depth, mat='SDK', rot_z=0.0, pointed=True, back=None, back_depth=None):
    """parede W x Htop com vao em arco (w, spring, apex), FRENTE em +Y (plano y=pos.y),
    extrudada 'depth' para -Y (dentro do edificio). back: painel de fundo recuado back_depth."""
    x0, y0, z0 = pos
    la = _half_arc(w, spring, apex, pointed)
    left = [(-W / 2, 0), (-w / 2, 0)] + la + [(0, Htop), (-W / 2, Htop)]
    right = [(-x_, z_) for x_, z_ in left][::-1]
    for poly in (left, right):
        bm = ngon_prism(poly, depth, (0, 0, 0))
        _xform(bm, (0, 0, 0), (math.pi / 2, 0, 0))       # (x, alt, prof) -> (x, -prof, alt): frente em y=0, corpo em -Y
        _xform(bm, (x0, y0, z0), (0, 0, rot_z))
        out.add(mat, bm)
    if back:
        bd = back_depth if back_depth is not None else depth - .3
        bm = box((w + .6, .3, apex + .3), (0, -bd - .15, (apex + .3) / 2))
        _xform(bm, (x0, y0, z0), (0, 0, rot_z))
        out.add(back, bm)

def _arc_tube(R, r, a0, a1, kz=1.0, seg=12, sides=8):
    """tubo em arco no plano XZ (de pe), de a0 a a1 (radianos, medidos no plano XZ a partir de +X), escala vertical kz."""
    bm = torus(R, r, (0, 0, 0), (0, 0, a0), seg=seg, sides=sides, arc=(a1 - a0))
    _xform(bm, (0, 0, 0), (math.pi / 2, 0, 0))            # XY -> XZ
    if abs(kz - 1) > 1e-6:
        bmesh.ops.scale(bm, vec=(1, 1, kz), verts=bm.verts)
    return bm

def arch_molding(out, pos, w, spring, apex, r=.45, mat='SLT', rot_z=0.0, pointed=True, gold=True, seg=12, double=False):
    """moldura em torno do vao (tubo de pedra clara + filete de ouro por dentro + ombreiras).
    pos.y = plano onde o EIXO do tubo fica (use frente + ~0.6*r para ficar saliente). Frente em +Y.
    double=True acrescenta um segundo anel mais fino, recuado, dentro do vao (revelo em dois degraus)."""
    x0, y0, z0 = pos
    if double:
        arch_molding(out, (x0, y0 - r * 1.5, z0), w - r * 1.6, spring - r * .2, apex - r * 1.2, r=r * .6, mat=mat, rot_z=rot_z, pointed=pointed, gold=False, seg=seg, double=False)
    def place(bm, dy=0.0):
        _xform(bm, (x0, y0 + dy, z0), (0, 0, rot_z)); return bm
    def mirror_x(bm):
        bmesh.ops.scale(bm, vec=(-1, 1, 1), verts=bm.verts)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm
    if pointed:
        R = w
        a0, a1 = 2 * math.pi / 3, math.pi
        kz = (apex - spring) / (R * math.sin(a0))
        for sx in (-1, 1):
            bm = _arc_tube(R, r, a0, a1, kz, seg=seg)          # arco esquerdo, centrado em (+w/2, spring)
            _xform(bm, (w / 2, 0, spring))
            if sx == 1: mirror_x(bm)
            out.add(mat, place(bm))
            if gold:
                bg = _arc_tube(R - r * .95, r * .3, a0, a1, kz, seg=seg, sides=6)
                _xform(bg, (w / 2, 0, spring))
                if sx == 1: mirror_x(bg)
                out.add('GLD', place(bg, dy=r * .35))
    else:
        R = w / 2
        kz = (apex - spring) / R
        bm = _arc_tube(R, r, 0, math.pi, kz, seg=seg * 2)
        _xform(bm, (0, 0, spring))
        out.add(mat, place(bm))
        if gold:
            bg = _arc_tube(R - r * .95, r * .3, 0, math.pi, kz, seg=seg * 2, sides=6)
            _xform(bg, (0, 0, spring))
            out.add('GLD', place(bg, dy=r * .35))
    # ombreiras (tubo vertical) + filete de ouro
    for sx in (-1, 1):
        out.add(mat, place(cyl(r, spring, (sx * w / 2, 0, 0), seg=10)))
        if gold:
            out.add('GLD', place(box((r * .55, r * .55, spring), (sx * (w / 2 - r * .95), 0, spring / 2)), dy=r * .35))
    # base das ombreiras (pequeno plinto)
    for sx in (-1, 1):
        out.add(mat, place(box((r * 2.6, r * 2.2, .7), (sx * w / 2, 0, .35), bevel=.06)))

def pilaster(out, pos, w, d, h, mat='SLT', cap=True, base=True, rot_z=0.0):
    """pilastra com base, fuste e capitel (relevo real)"""
    x, y, z = pos
    def P(bm):
        _xform(bm, (0, 0, 0), (0, 0, rot_z)); _xform(bm, (x, y, z)); return bm
    # base: plinto + toro + escocia (3 degraus reais)
    if base:
        out.add(mat, P(box((w + .8, d + .6, .7), (0, 0, .35), bevel=.08)))
        out.add(mat, P(box((w + .5, d + .4, .35), (0, 0, .7 + .17))))
        out.add(mat, P(torus(min(w, d) * .5 + .12, .16, (0, 0, 1.15), seg=12, sides=6)))
    out.add(mat, P(box((w, d, h - 3.2), (0, 0, 1.3 + (h - 3.2) / 2))))
    # capitel: anel de pescoco + equino (abre) + abaco + friso de ouro fino
    if cap:
        out.add('GLD', P(torus(min(w, d) * .5 + .06, .07, (0, 0, h - 1.9), seg=12, sides=5)))
        out.add(mat, P(lathe([(min(w, d) * .5, 0), (min(w, d) * .5 + .32, .5), (min(w, d) * .5 + .42, .7)], (0, 0, h - 1.85), seg=12)))
        out.add(mat, P(box((w + .7, d + .5, .42), (0, 0, h - 1.1 + .21))))
        out.add('GLD', P(box((w + .78, d + .56, .12), (0, 0, h - .68 + .06))))
        out.add(mat, P(box((w + .95, d + .7, .6), (0, 0, h - .6 + .3), bevel=.1)))

def cornice(out, pos, L, D, mat='SLT', gold=True, dentils=True, rot_z=0.0, h=2.2):
    """cornija em 3 degraus com dentículos e friso de ouro. pos = centro da base, comprimento em X, profundidade D em -Y."""
    x, y, z = pos
    def P(bm):
        _xform(bm, (0, 0, 0), (0, 0, rot_z)); _xform(bm, (x, y, z)); return bm
    # faixas empilhadas, cada uma mais saliente (+Y = frente). pos.y = plano da frente da parede.
    # arquitrave -> denticulos -> friso -> modilhoes (misulas) -> cimalha
    p1, p2, p3 = .25, .8, 1.35
    out.add(mat, P(box((L, D, h * .26), (0, p1 - D / 2, h * .13))))
    if dentils:
        n = int(L / 1.5)
        for i in range(n):
            xx = -L / 2 + .75 + i * (L / n)
            out.add(mat, P(box((.6, .55, h * .2), (xx, p1 + .27, h * .26 + h * .1))))
    out.add(mat, P(box((L + .5, D + .45, h * .18), (0, p2 - D / 2, h * .46 + h * .09), bevel=.05)))
    if gold:
        out.add('GLD', P(box((L + .56, D + .5, h * .07), (0, p2 + .05 - D / 2, h * .64 + h * .035))))
    # modilhoes (misulas) sob a cimalha
    nm = int(L / 2.6)
    for i in range(nm + 1):
        xx = -L / 2 + .6 + i * ((L - 1.2) / max(nm, 1))
        out.add(mat, P(box((.7, .9, h * .18), (xx, p3 - .45, h * .68 + h * .09), bevel=.04)))
    out.add(mat, P(box((L + 1.1, D + .9, h * .22), (0, p3 - D / 2, h * .86 + h * .11), bevel=.08)))

def quoins(out, pos, h, size=(1.4, 1.4), step=1.6, mat='SLT', proud=.25, rot_z=0.0):
    """cunhais alternados no canto (relevo). pos = base do canto."""
    x, y, z = pos
    n = int(h / step)
    for i in range(n):
        w = size[0] if i % 2 == 0 else size[0] * .65
        d = size[1] * .65 if i % 2 == 0 else size[1]
        bm = box((w + proud, d + proud, step * .92), (0, 0, i * step + step * .46))
        _xform(bm, (0, 0, 0), (0, 0, rot_z)); _xform(bm, (x, y, z))
        out.add(mat, bm)

# ---------------------------------------------------------------- BALAUSTRADA / MURETA
def balustrade(out, p1, p2, z, h=2.8, spacing=1.7, mat='SLT'):
    x1, y1 = p1; x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < .5: return
    a = math.atan2(dy, dx)
    mid = ((x1 + x2) / 2, (y1 + y2) / 2)
    rot = (0, 0, a)
    out.add(mat, box((L, .9, .45), (mid[0], mid[1], z + .22), rot, bevel=.08))
    out.add(mat, box((L, 1.0, .5), (mid[0], mid[1], z + h - .4), rot, bevel=.12))
    out.add('GLD', box((L, .4, .1), (mid[0], mid[1], z + h - .1), rot))
    n = max(1, int(L / spacing))
    for i in range(n + 1):
        t = i / n
        px, py = x1 + dx * t, y1 + dy * t
        out.add(mat, lathe([(.28, 0), (.36, .16), (.17, .45), (.38, 1.0), (.42, 1.35), (.18, 1.75), (.3, 1.95)], (px, py, z + .45), seg=8))

def coping_arc(out, cx, cy, R, z, a0, a1, w=1.6, h=.9, mat='SLT', seg=28, gold=True):
    """borda arredondada (meio-fio grosso) ao longo de um arco - ref. bordas do patamar"""
    bm = torus(R, h/2, (cx, cy, z + h/2), (0, 0, a0), seg=seg, sides=8, arc=(a1 - a0))
    bmesh.ops.scale(bm, vec=(1, 1, 1), verts=bm.verts)
    out.add(mat, bm)
    # laje sob o torus para fechar
    pts_o = [(cx + math.cos(a0 + (a1 - a0) * i / seg) * (R + w/2), cy + math.sin(a0 + (a1 - a0) * i / seg) * (R + w/2)) for i in range(seg + 1)]
    pts_i = [(cx + math.cos(a0 + (a1 - a0) * i / seg) * (R - w/2), cy + math.sin(a0 + (a1 - a0) * i / seg) * (R - w/2)) for i in range(seg + 1)]
    out.add(mat, ring_prism(pts_o, pts_i, h * .55, (0, 0, z)))
    if gold:
        pts_o = [(cx + math.cos(a0 + (a1 - a0) * i / seg) * (R - w/2 - .05), cy + math.sin(a0 + (a1 - a0) * i / seg) * (R - w/2 - .05)) for i in range(seg + 1)]
        pts_i = [(cx + math.cos(a0 + (a1 - a0) * i / seg) * (R - w/2 - .45), cy + math.sin(a0 + (a1 - a0) * i / seg) * (R - w/2 - .45)) for i in range(seg + 1)]
        out.add('GLD', ring_prism(pts_o, pts_i, .08, (0, 0, z + h * .55)))

# ---------------------------------------------------------------- URNA + ARBUSTO DOURADO
def urn(out, pos, r=1.5, mat='SLT', foliage='LFG', seed=1):
    x, y, z = pos
    out.add(mat, box((r * 2.2, r * 2.2, .5), (x, y, z + .25), bevel=.06))
    out.add(mat, lathe([(r * .55, 0), (r * .5, .3), (r * .75, .9), (r * 1.0, 1.9), (r * 1.1, 2.3), (r * .95, 2.5)], (x, y, z + .5), seg=14))
    out.add('GLD', torus(r * 1.02, .08, (x, y, z + 2.9), seg=14, sides=5))
    rnd = random.Random(seed)
    cs = [(0, 0, 0)] + [((rnd.random() - .5) * r * 1.4, (rnd.random() - .5) * r * 1.4, rnd.random() * r * .8) for _ in range(7)]
    out.add(foliage, puff_cloud([(x + a, y + b, z + 3.4 + c, r * (.95 if i == 0 else .7)) for i, (a, b, c) in enumerate(cs)], r * .95, seed=seed, seg=9))

def pedestal(out, pos, w=3.6, h=3.2, mat='SLT'):
    x, y, z = pos
    out.add(mat, box((w, w, .6), (x, y, z + .3), bevel=.06))
    out.add(mat, box((w * .8, w * .8, h - 1.2), (x, y, z + .6 + (h - 1.2) / 2)))
    out.add('GLD', box((w * .84, w * .84, .16), (x, y, z + h - .6 + .08)))
    out.add(mat, box((w * .95, w * .95, .52), (x, y, z + h - .26), bevel=.06))

# ---------------------------------------------------------------- VEGETACAO ESTILIZADA
def poplar(out, pos, h=26.0, r=2.0, seed=1, mat='LFG', mat2='LFG2'):
    """alamo dourado v2: alto, estreito e delicado - tronco com ramos visiveis e MUITAS plumas pequenas
    alongadas (leitura de ramos + folhas), envelope estreito que afina para uma ponta."""
    x, y, z = pos
    rnd = random.Random(seed)
    out.add('TRK', lathe([(.42, 0), (.3, h * .3), (.16, h * .7), (.05, h * .96)], (x, y, z), seg=8))
    # ramos curtos (ficam quase escondidos na copa; dao leitura de estrutura nos vaos)
    nb = 6
    for i in range(nb):
        t = .24 + .55 * i / (nb - 1)
        a = rnd.random() * TAU
        L = h * (.09 + .05 * rnd.random()) * (1 - .3 * t)
        bm = cyl(.06, L, (0, 0, 0), seg=5)
        _xform(bm, (0, 0, 0), (math.radians(30 + rnd.random() * 14), 0, 0))
        _xform(bm, (0, 0, 0), (0, 0, a))
        _xform(bm, (x, y, z + h * t))
        out.add('TRK', bm)
    # plumas: DENSAS, pequenas e alongadas; coluna estreita que afina para a ponta (leitura penada)
    n = 64
    for i in range(n):
        t = .14 + .86 * (i / (n - 1)) ** .95
        env = math.sin(math.pi * (.06 + .92 * t)) ** .7 * (1 - .5 * t) + .1
        R = r * env
        a = rnd.random() * TAU
        d = R * (.15 + .85 * rnd.random())
        rr = (.5 + .35 * rnd.random()) * (1 - .3 * t) * (r / 2.0)
        bm = noisy_ball(rr, (0, 0, 0), seed=seed * 31 + i, seg=7, amp=.16, scl=(.5, .5, 1.8))
        _xform(bm, (0, 0, 0), (math.radians(8 + 26 * (d / max(R, .01))), 0, 0))    # quanto mais externa, mais deitada
        _xform(bm, (0, 0, 0), (0, 0, a + math.pi / 2))
        _xform(bm, (x + math.cos(a) * d, y + math.sin(a) * d, z + h * t))
        out.add(mat if (i % 3) else mat2, bm)
    for k in range(3):
        out.add(mat, noisy_ball(.32 * (r / 2.0), (x + (rnd.random() - .5) * .4, y + (rnd.random() - .5) * .4, z + h * (.97 + .03 * k)), seed=seed + k, seg=7, amp=.1, scl=(.5, .5, 2.6)))

def pampas(out, pos, h=2.8, n=9, seed=1, mat='LFP'):
    """capim-dos-pampas: plumas finas e palidas em leque (vegetacao baixa da referencia)"""
    x, y, z = pos
    rnd = random.Random(seed)
    for i in range(n):
        a = rnd.random() * TAU
        tilt = math.radians(8 + rnd.random() * 26)
        hh = h * (.7 + rnd.random() * .5)
        bm = ball(.22, (0, 0, 0), seg=6, scl=(.6, .6, hh / .44))
        _xform(bm, (0, 0, 0), (tilt, 0, 0)); _xform(bm, (0, 0, 0), (0, 0, a))
        _xform(bm, (x + math.cos(a) * .25, y + math.sin(a) * .25, z + hh * .55))
        out.add(mat, bm)
    out.add('LFV', puff_cloud([(x, y, z + .35, .75), (x + .4, y - .2, z + .3, .55), (x - .35, y + .3, z + .3, .5)], .7, seed=seed, seg=7))

def ground_cover(out, pos, r=2.0, seed=1, mat='LFV'):
    """tapete baixo de folhagem (montinhos) para pes de canteiro e margens"""
    x, y, z = pos
    rnd = random.Random(seed)
    cs = [(x + (rnd.random() - .5) * r * 2, y + (rnd.random() - .5) * r * 2, z + .25, .45 + rnd.random() * .35) for _ in range(6)]
    out.add(mat, puff_cloud(cs, .5, seed=seed, seg=7))

def bush(out, pos, r=2.0, seed=1, mat='LFV', flowers='FLW', n_fl=6):
    x, y, z = pos
    rnd = random.Random(seed)
    cs = [(0, 0, 0)] + [((rnd.random() - .5) * r * 1.6, (rnd.random() - .5) * r * 1.6, rnd.random() * r * .7) for _ in range(6)]
    out.add(mat, puff_cloud([(x + a, y + b, z + r * .7 + c, r * (.95 if i == 0 else .65)) for i, (a, b, c) in enumerate(cs)], r * .85, seed=seed, seg=9))
    if flowers:
        for i in range(n_fl):
            a = rnd.random() * TAU
            out.add(flowers, ball(.22, (x + math.cos(a) * r * .9, y + math.sin(a) * r * .9, z + r * .9 + rnd.random() * r * .6), seg=5))

def rock(out, pos, r=1.6, seed=1, mat='RCK'):
    rnd = random.Random(seed)
    out.add(mat, noisy_ball(r, pos, seed=seed, amp=.22, scl=(1 + rnd.random() * .5, 1 + rnd.random() * .3, .55 + rnd.random() * .35)))

def gold_text(out, text, pos, rot=(0, 0, 0), size=6.0, depth=1.0, mat='GLD'):
    cu = bpy.data.curves.new('lv10_txt', 'FONT')
    cu.body = text
    cu.size = size
    cu.extrude = depth / 2
    cu.bevel_depth = size * .012
    cu.align_x = 'CENTER'
    try:
        cu.font = bpy.data.fonts.load(r"C:\Windows\Fonts\georgiab.ttf", check_existing=True)
    except Exception:
        pass
    ob = bpy.data.objects.new('lv10_txt', cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=.001)
    _xform(bm, (0, 0, 0), (math.pi/2, 0, 0))    # texto de pe no plano XZ
    _xform(bm, (0, 0, 0), (0, 0, math.pi))       # legivel de quem olha de +Y para -Y (frente do edificio em +Y)
    _xform(bm, pos, rot)
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(me)
    bpy.data.curves.remove(cu)
    out.add(mat, bm)
