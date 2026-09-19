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
    'SDK': ((128, 118, 106), 't_stone_dark.png', 't_stone_dark_n.png', None, 1/24),   # corpo escuro da torre
    'SLT': ((188, 190, 196), 't_stone_light.png', 't_stone_light_n.png', None, 1/20), # molduras, pilastras, cornijas
    'ASH': ((204, 200, 190), 't_ashlar.png', 't_ashlar_n.png', None, 1/16),           # muretas, faces de plataforma
    'FLR': ((212, 205, 190), 't_floor.png', 't_floor_n.png', None, 1/32),             # piso da praca
    'FLL': ((222, 216, 202), 't_floor_light.png', 't_floor_light_n.png', None, 1/32), # piso do patamar/terraco
    'GLD': ((222, 176, 78), 't_gold.png', None, 't_gold_r.png', 1/8),                 # dourado
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
    'DRK': ((28, 26, 30), None, None, None, None),                                    # fundo escuro dos vaos
    'LFG': ((236, 192, 86), 't_leaf_gold.png', None, None, 1/5),                     # folhagem dourada (textura de massa foliar)
    'LFG2': ((222, 168, 60), 't_leaf_gold2.png', None, None, 1/5),
    'LFV': ((104, 178, 90), 't_leaf_green.png', None, None, 1/6),                    # folhagem verde
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
    """base dourada + plinto claro, fuste liso branco com aneis de ouro, colar de petalas grandes,
    lanterna octogonal com barras douradas e vidro leitoso, tampa em disco + coroa + agulha."""
    s = scale
    x, y, z = pos
    # plinto de pedra clara + anel de ouro
    out.add('SLT', lathe([(1.0*s, 0), (1.0*s, .35*s), (.78*s, .5*s), (.62*s, .75*s), (.5*s, .9*s)], (x, y, z), seg=14))
    out.add('GLD', lathe([(.56*s, 0), (.62*s, .1*s), (.62*s, .28*s), (.5*s, .36*s), (.42*s, .38*s)], (x, y, z + .9*s), seg=14))
    # fuste liso (leve afunilamento)
    H = 6.4 * s
    out.add('WHT', lathe([(.40*s, 0), (.38*s, H*.5), (.34*s, H)], (x, y, z + 1.25*s), seg=14))
    out.add('GLD', torus(.36*s, .09*s, (x, y, z + 1.25*s + H - .1*s), seg=14, sides=6))
    # taca sob as petalas
    top = z + 1.25*s + H
    out.add('WHT', lathe([(.3*s, 0), (.62*s, .45*s), (.78*s, .8*s), (.7*s, 1.0*s)], (x, y, top), seg=14))
    # petalas grandes (8), inclinadas para fora, com uma fileira menor por dentro
    for i in range(8):
        a = i / 8 * TAU
        bm = ball(.62*s, (0, 0, 0), seg=10, scl=(.55, 1.0, 1.7))
        _xform(bm, (0, 0, 0), (math.radians(28), 0, 0))
        _xform(bm, (0, 0, 0), (0, 0, a + math.pi/2))
        _xform(bm, (x + math.cos(a)*.62*s, y + math.sin(a)*.62*s, top + 1.2*s))
        out.add('WHT', bm)
    for i in range(8):
        a = (i + .5) / 8 * TAU
        bm = ball(.42*s, (0, 0, 0), seg=8, scl=(.5, 1.0, 1.5))
        _xform(bm, (0, 0, 0), (math.radians(12), 0, 0))
        _xform(bm, (0, 0, 0), (0, 0, a + math.pi/2))
        _xform(bm, (x + math.cos(a)*.34*s, y + math.sin(a)*.34*s, top + 1.75*s))
        out.add('WHT', bm)
    # lanterna octogonal
    lz = top + 1.9*s
    LH = 1.55 * s
    out.add('MLK', ngon_prism(reg_poly(.56*s, 8, TAU/16), LH, (x, y, lz)))
    for i in range(8):
        a = i / 8 * TAU + TAU/16
        out.add('GLD', box((.1*s, .1*s, LH), (x + math.cos(a)*.58*s, y + math.sin(a)*.58*s, lz + LH/2), (0, 0, a)))
    out.add('GLD', ngon_prism(reg_poly(.66*s, 8, TAU/16), .12*s, (x, y, lz - .06*s)))
    out.add('GLD', ngon_prism(reg_poly(.66*s, 8, TAU/16), .12*s, (x, y, lz + LH*.5)))
    # tampa: disco branco largo com borda de ouro, coroa dourada e agulha
    cz = lz + LH
    out.add('GLD', ngon_prism(reg_poly(.74*s, 8, TAU/16), .14*s, (x, y, cz)))
    out.add('WHT', lathe([(.98*s, 0), (1.0*s, .22*s), (.9*s, .34*s), (.7*s, .42*s)], (x, y, cz + .14*s), seg=16))
    out.add('GLD', lathe([(.6*s, 0), (.62*s, .18*s), (.48*s, .5*s), (.5*s, .62*s), (.26*s, .7*s), (.03*s, 1.6*s)], (x, y, cz + .56*s), seg=12))

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

def arch_molding(out, pos, w, spring, apex, r=.45, mat='SLT', rot_z=0.0, pointed=True, gold=True, seg=12):
    """moldura em torno do vao (tubo de pedra clara + filete de ouro por dentro + ombreiras).
    pos.y = plano onde o EIXO do tubo fica (use frente + ~0.6*r para ficar saliente). Frente em +Y."""
    x0, y0, z0 = pos
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
    if base:
        out.add(mat, P(box((w + .6, d + .5, .9), (0, 0, .45), bevel=.08)))
        out.add(mat, P(box((w + .3, d + .25, .5), (0, 0, 1.15))))
    out.add(mat, P(box((w, d, h - 2.6), (0, 0, 1.4 + (h - 2.6) / 2))))
    if cap:
        out.add(mat, P(box((w + .3, d + .25, .5), (0, 0, h - 1.2 + .25))))
        out.add('GLD', P(box((w + .45, d + .35, .3), (0, 0, h - .7 + .15))))
        out.add(mat, P(box((w + .7, d + .5, .5), (0, 0, h - .4 + .25), bevel=.08)))

def cornice(out, pos, L, D, mat='SLT', gold=True, dentils=True, rot_z=0.0, h=2.2):
    """cornija em 3 degraus com dentículos e friso de ouro. pos = centro da base, comprimento em X, profundidade D em -Y."""
    x, y, z = pos
    def P(bm):
        _xform(bm, (0, 0, 0), (0, 0, rot_z)); _xform(bm, (x, y, z)); return bm
    # faixas empilhadas, cada uma mais saliente (+Y = frente). pos.y = plano da frente da parede.
    p1, p2, p3 = .25, .85, 1.25
    out.add(mat, P(box((L, D, h * .30), (0, p1 - D / 2, h * .15))))
    if dentils:
        n = int(L / 1.6)
        for i in range(n):
            xx = -L / 2 + .8 + i * (L / n)
            out.add(mat, P(box((.7, .6, h * .26), (xx, p1 + .3, h * .30 + h * .13))))
    out.add(mat, P(box((L + .6, D + .5, h * .22), (0, p2 - D / 2, h * .56 + h * .11), bevel=.06)))
    if gold:
        out.add('GLD', P(box((L + .7, D + .6, h * .10), (0, p2 + .08 - D / 2, h * .78 + h * .05))))
    out.add(mat, P(box((L + 1.0, D + .8, h * .22), (0, p3 - D / 2, h * .83 + h * .11), bevel=.08)))

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
def poplar(out, pos, h=24.0, r=2.4, seed=1, mat='LFG', mat2='LFG2'):
    """alamo dourado alto e estreito (ref: arvores douradas colunares)"""
    x, y, z = pos
    rnd = random.Random(seed)
    out.add('TRK', lathe([(.5, 0), (.36, h * .35), (.18, h * .8), (.04, h * .97)], (x, y, z), seg=8))
    # copa colunar: muitas plumas pequenas e alongadas em torno do eixo (silhueta estreita e "penada")
    n = 16
    for i in range(n):
        t = i / (n - 1)
        zz = z + h * (.14 + .82 * t)
        env = (0.35 + .95 * math.sin(math.pi * (t * .78 + .12))) * (1 - .45 * t)   # envelope: mais largo no terco inferior
        rr = r * env * (.55 + rnd.random() * .25)
        a = rnd.random() * TAU
        d = r * env * .55 * rnd.random()
        ox, oy = math.cos(a) * d, math.sin(a) * d
        bm = ball(rr, (0, 0, 0), seg=8, scl=(.8, .8, 1.9))
        _xform(bm, (0, 0, 0), ((rnd.random() - .5) * .5, (rnd.random() - .5) * .5, 0))
        _xform(bm, (x + ox, y + oy, zz))
        out.add(mat if i % 3 else mat2, bm)
    out.add(mat, ball(r * .28, (x, y, z + h * .99), seg=7, scl=(.8, .8, 2.6)))

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
