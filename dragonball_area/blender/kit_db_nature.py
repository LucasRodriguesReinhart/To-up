# DRAGONBALL_ROCKS / DRAGONBALL_NATURE / clouds & islets.  Asset origin = ground centre, front = -Y.
from dblib import *

ROCK_TONES = ['db_rock', 'db_rock_light', 'db_rock_dark']

# ------------------------------------------------------------------ ROCKS
def _chunk(name, loc, w, d, h, m, rz, rs, top=True):
    """Faceted rock chunk: a block plus bevelled top made of wedges (reads rounded, stays cheap)."""
    x, y, z = loc
    box(name, (x, y, z + h*.4), (w, d, h*.8), m, (0, 0, rz), True)
    if top:
        ca, sa = math.cos(rz), math.sin(rz)
        for k, (dx, dy, ang) in enumerate(((0, -1, 0), (0, 1, PI), (-1, 0, -PI/2), (1, 0, PI/2))):
            span = w if dx == 0 else d
            depth = (d if dx == 0 else w) * .5
            ox, oy = dx*(w*.5 - depth*.5)*1.0, dy*(d*.5 - depth*.5)
            px, py = x + ox*ca - oy*sa, y + ox*sa + oy*ca
            wedge(name + 'Bisel', (px, py, z + h*.8 + h*.1), (span, depth, h*.2), m, (0, 0, rz + ang), False)

def rocks():
    rs = rng(11)
    for nm, (w, d, h) in (('Rocha_S', (4, 3.4, 3)), ('Rocha_M', (8, 7, 6)), ('Rocha_L', (15, 12, 11))):
        asset('DRAGONBALL_ROCKS', nm)
        _chunk('Rocha', (0, 0, 0), w, d, h, 'db_rock', 0, rs)
        _chunk('Rocha', (w*.42, d*.25, 0), w*.55, d*.6, h*.6, 'db_rock_light', .6, rs)
        box('Estrato', (0, 0, h*.35), (w + .3, d + .3, h*.08), 'db_rock_dark', (0, 0, 0), False)
        if nm != 'Rocha_S':
            _chunk('Rocha', (-w*.45, -d*.2, 0), w*.4, d*.45, h*.45, 'db_rock_dark', -.4, rs)

    # tall battle spires (60 studs at s=1): round tiers with strata rings and a grassy top
    def spire(nm, tiers, seed, cap_tree=True, lean=0.0):
        r = rng(seed)
        asset('DRAGONBALL_ROCKS', nm)
        z = 0.0
        ox = oy = 0.0
        for i, (rad, h) in enumerate(tiers):
            m = 'db_rock' if i % 2 == 0 else 'db_rock_light'
            cyl('Coluna', (ox, oy, z + h/2), rad, h, m, 'Z', True)
            cyl('Estrato', (ox, oy, z + h - .6), rad + .45, 1.2, 'db_rock_dark', 'Z', False)
            # side bulges break the perfect cylinder
            for k in range(3):
                a = k*2.1 + r.uniform(-.5, .5)
                bw = rad*r.uniform(.7, 1.0)
                box('Saliencia', (ox + math.cos(a)*rad*.7, oy + math.sin(a)*rad*.7, z + h*r.uniform(.3, .7)),
                    (bw, bw*.8, h*r.uniform(.35, .6)), r.choice(ROCK_TONES), (0, 0, a), False)
            z += h
            ox += lean*h + r.uniform(-.8, .8); oy += lean*.4*h + r.uniform(-.8, .8)
        top_r = tiers[-1][0]
        cyl('TopoGrama', (ox, oy, z + .5), top_r + .3, 1.0, 'db_grass', 'Z', False)
        if cap_tree:
            cyl('TroncoTopo', (ox + top_r*.2, oy, z + 3), .5, 5, 'db_trunk', 'Z', False)
            ball('CopaTopo', (ox + top_r*.2, oy, z + 6.5), 6, 'tree_ball')
            ball('CopaTopo', (ox + top_r*.2 + 2, oy + 1, z + 5.5), 3.6, 'tree_ball_light')
        return z
    spire('Pilar_A', [(9, 16), (8, 14), (7.2, 16), (6.4, 14)], 3)
    spire('Pilar_B', [(7, 20), (6, 18), (5.2, 22)], 4, cap_tree=False, lean=.03)
    spire('Pilar_C', [(12, 12), (11, 10), (10, 12), (8.5, 14), (7.5, 12)], 5)

    # balanced boulder on a thin neck (iconic battlefield silhouette)
    asset('DRAGONBALL_ROCKS', 'Rocha_Equilibrio')
    cyl('Base', (0, 0, 7), 7, 14, 'db_rock', 'Z', True)
    cyl('Estrato', (0, 0, 13), 7.4, 1.2, 'db_rock_dark', 'Z', False)
    cyl('Pescoco', (0, 0, 21), 3.2, 16, 'db_rock_light', 'Z', True)
    ball('Pedra', (1.5, 0, 34), 17, 'db_rock', col=True)
    box('Faceta', (2, -5, 36), (9, 4, 7), 'db_rock_light', (.3, .2, .4), False)
    box('Faceta', (-4, 4, 31), (7, 5, 6), 'db_rock_dark', (-.2, .3, 1.1), False)

    # natural arch spanning a 26-stud trail
    asset('DRAGONBALL_ROCKS', 'Arco_Rocha')
    for s in (-1, 1):
        cyl('PernaArco', (s*19, 0, 14), 7, 28, 'db_rock', 'Z', True)
        cyl('Estrato', (s*19, 0, 9), 7.4, 1.2, 'db_rock_dark', 'Z', False)
        box('Saliencia', (s*22, -3, 6), (8, 8, 12), 'db_rock_light', (0, 0, .4*s), True)
    vring('Arco', (0, 0, 26), 19, 9, 12, 'db_rock', 14, 0, True, a0=0, a1=PI)
    vring('ArcoEstrato', (0, 0, 26), 23.2, 1.2, 12.4, 'db_rock_dark', 14, 0, False, a0=0.15, a1=PI-.15)
    box('TopoGrama', (0, 0, 49.6), (16, 11, 1), 'db_grass', (0, 0, 0), False)
    ball('Arbusto', (-4, 1, 51), 4, 'tree_ball')

    # mountain massif module (40 x 34 x 60) with strata; stacked and scaled to build the northern range
    def massif(nm, seed, h, w=40, d=34):
        r = rng(seed)
        asset('DRAGONBALL_ROCKS', nm)
        tiers = [(1.0, .38), (.86, .3), (.7, .32)]
        z = 0
        for i, (k, hh) in enumerate(tiers):
            th = h*hh
            m = ['db_rock', 'db_rock_light', 'db_rock'][i]
            box('Macico', (r.uniform(-1, 1), r.uniform(-1, 1), z + th/2), (w*k, d*k, th), m, (0, 0, r.uniform(-.06, .06)), True)
            box('Estrato', (0, -d*k/2 - .2, z + th - 1), (w*k + .6, 1.2, 2), 'db_rock_dark', (0, 0, 0), False)
            box('Estrato', (0, d*k/2 + .2, z + th - 1), (w*k + .6, 1.2, 2), 'db_rock_dark', (0, 0, 0), False)
            for s in (-1, 1):
                wedge('Ombro', (s*(w*k/2 + 2.5), 0, z + th*.35), (d*k*.9, 5, th*.7), r.choice(ROCK_TONES), (0, 0, s*PI/2), False)
            z += th
        box('TopoGrama', (0, 0, z + .5), (w*.7 - 1, d*.7 - 1, 1), 'db_grass', (0, 0, 0), False)
        ball('Copa', (w*.15, -d*.1, z + 4), 7, 'tree_ball')
        ball('Copa', (-w*.18, d*.12, z + 3.5), 5.5, 'tree_ball_dark')
    massif('Penhasco', 7, 60)
    massif('Penhasco_Baixo', 8, 34, 44, 34)

    asset('DRAGONBALL_ROCKS', 'Mesa_Natural')
    box('Mesa', (0, 0, 5), (30, 24, 10), 'db_rock', (0, 0, 0), True)
    box('Estrato', (0, 0, 7), (30.6, 24.6, 1.2), 'db_rock_dark', (0, 0, 0), False)
    box('TopoGrama', (0, 0, 10.3), (29, 23, .6), 'db_grass', (0, 0, 0), True)
    for s in (-1, 1):
        wedge('Talude', (s*17, 0, 3), (24, 4, 6), 'db_rock_light', (0, 0, s*PI/2), False)

# ------------------------------------------------------------------ NATURE
def nature():
    def ball_tree(nm, s, seed):
        r = rng(seed)
        asset('DRAGONBALL_NATURE', nm)
        h = 9*s
        rod('Tronco', (0, 0, 0), (.6*s, .3*s, h*.55), 1.1*s, 'db_trunk', True)
        rod('Tronco', (.6*s, .3*s, h*.55), (0, 0, h), .9*s, 'db_trunk', False)
        ball('Copa', (0, 0, h + 3*s), 10*s, 'tree_ball')
        ball('Copa', (3.6*s, 1*s, h + 1.4*s), 6.5*s, 'tree_ball_dark')
        ball('Copa', (-3.4*s, -1.2*s, h + 1.8*s), 7*s, 'tree_ball')
        ball('CopaLuz', (-1*s, -2*s, h + 6*s), 5.5*s, 'tree_ball_light')
    ball_tree('Arvore_Bola_G', 1.35, 1)
    ball_tree('Arvore_Bola_M', 1.0, 2)

    asset('DRAGONBALL_NATURE', 'Arvore_Ajisa')
    cyl('Tronco', (0, 0, 8), .8, 16, 'db_trunk', 'Z', False)
    ball('Bulbo', (0, 0, 19), 9, 'tree_ajisa')
    ball('BulboLuz', (-1.4, -1.6, 20), 3.6, 'tree_ball_light')
    box('ColisaoTronco', (0, 0, 4), (1, 1, 8), 'invisible', (0, 0, 0), True)

    asset('DRAGONBALL_NATURE', 'Palmeira')
    pts = [(0, 0, 0), (.8, 0, 5), (2.2, 0, 10), (4.2, 0, 14.5)]
    for a, b in zip(pts, pts[1:]):
        rod('Tronco', a, b, .9, 'db_trunk', False)
    for k in range(7):
        a = k/7*2*PI
        tip = (4.2 + math.cos(a)*7, math.sin(a)*7, 12.5)
        rod('Folha', (4.2, 0, 14.8), tip, 2.2, 'palm_leaf', False, h=.3)
    ball('Coco', (4.2, 0, 14.2), 1.6, 'db_trunk')
    box('ColisaoTronco', (1, 0, 4), (1.2, 1.2, 8), 'invisible', (0, 0, 0), True)

    asset('DRAGONBALL_NATURE', 'Arbusto_Bola')
    ball('Arbusto', (0, 0, 1.6), 4.4, 'tree_ball')
    ball('Arbusto', (2.4, .6, 1.2), 3.2, 'tree_ball_dark')
    ball('Arbusto', (-2, -.8, 1.1), 3, 'tree_ball_light')

    asset('DRAGONBALL_NATURE', 'Flores')
    r = rng(9)
    for k in range(9):
        x, y = r.uniform(-3, 3), r.uniform(-2, 2)
        box('Haste', (x, y, .5), (.12, .12, 1), 'db_grass_dark', (0, 0, 0), False)
        ball('Flor', (x, y, 1.1), .7, r.choice(['flower_pink', 'flower_yellow', 'flower_white']))
    box('Folhagem', (0, 0, .15), (7, 5, .3), 'db_grass_dark', (0, 0, 0), False)

    asset('DRAGONBALL_NATURE', 'Tufo')
    for k in range(4):
        a = k/4*2*PI
        wedge('Folha', (math.cos(a)*.5, math.sin(a)*.5, .9), (.5, .7, 1.8), 'db_grass_dark', (0, 0, a), False)

# ------------------------------------------------------------------ SKY
def sky():
    for nm, seed, n in (('Nuvem_G', 1, 7), ('Nuvem_M', 2, 5)):
        r = rng(seed)
        asset('DRAGONBALL_DECORATION', nm)
        base = 16 if nm == 'Nuvem_G' else 10
        for k in range(n):
            x = (k - (n-1)/2)*base*.6 + r.uniform(-2, 2)
            d = base*r.uniform(.8, 1.3)*(1.2 - abs(k-(n-1)/2)/n)
            ball('Nuvem', (x, r.uniform(-3, 3), d*.25), d, 'cloud')
        box('BaseNuvem', (0, 0, -base*.05), (n*base*.55, base*.7, base*.3), 'cloud_shade', (0, 0, 0), False)

    asset('DRAGONBALL_DECORATION', 'Ilhota_Flutuante')
    for i, (rad, h) in enumerate(((16, 6), (13, 8), (9, 9), (5, 8), (2.5, 6))):
        z = -sum(t[1] for t in ((16, 6), (13, 8), (9, 9), (5, 8), (2.5, 6))[:i]) - h/2
        cyl('Rocha', (0, 0, z), rad, h, ['db_rock', 'db_rock_dark', 'db_rock', 'db_rock_red', 'db_rock_deep'][i], 'Z', False)
    cyl('Grama', (0, 0, .5), 16.3, 1, 'db_grass', 'Z', False)
    cyl('PilarIlhota', (-6, 3, 14), 4.5, 28, 'db_rock', 'Z', False)
    cyl('Estrato', (-6, 3, 20), 4.9, 1.2, 'db_rock_dark', 'Z', False)
    cyl('TopoPilar', (-6, 3, 28.4), 4.7, .8, 'db_grass', 'Z', False)
    cyl('Tronco', (7, -3, 4), .6, 8, 'db_trunk', 'Z', False)
    ball('Copa', (7, -3, 9.5), 8, 'tree_ball')
    ball('Copa', (9.5, -1, 8.5), 5, 'tree_ball_light')
    box('Cachoeirinha', (15.4, 2, -8), (1, 4, 16), 'db_water', (0, 0, 0), False)

def build():
    rocks(); nature(); sky()

# ------------------------------------------------------------------ SCULPTED ROCKS (replace the primitive rocks)
def rocks_sculpt():
    import dbshapes as S
    import bmesh as _bm
    def col_cyl(loc, r, h): cyl('Colisao', loc, r, h, 'invisible', 'Z', True)
    def col_box(loc, dims, rz=0): box('Colisao', loc, dims, 'invisible', (0, 0, rz), True)
    for nm, sz, seed in (('Rocha_S', (4.5, 3.8, 3.2), 3), ('Rocha_M', (9, 7.5, 6.5), 5), ('Rocha_L', (16, 13, 11), 7)):
        c = asset('DRAGONBALL_ROCKS', nm)
        bm = S.boulder(nm, c, size=sz, seed=seed, sub=2)
        tmp = bpy.data.meshes.new('tmp')
        for (dx, dy, k, sd, tone) in ((sz[0]*.45, sz[1]*.25, .55, seed + 1, 'db_rock_light'), (-sz[0]*.4, -sz[1]*.25, .45, seed + 2, 'db_rock_dark')):
            b2 = S.boulder(nm, c, size=(sz[0]*k, sz[1]*k, sz[2]*k), seed=sd, sub=1, tone=tone, loc=(dx, dy, 0))
            b2.to_mesh(tmp); b2.free(); bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
        S.to_object(nm + '_Malha', bm, c, smooth=False)
        col_box((0, 0, sz[2]*.4), (sz[0]*.8, sz[1]*.8, sz[2]*.8))
    for nm, (h, r0, r1, tiers, seed, lean, top) in (('Pilar_A', (60, 9, 6.2, 4, 3, (0, 0), 'grass')), ('Pilar_B', (62, 7, 4.6, 3, 4, (.035, .015), 'rock')),
                                                   ('Pilar_C', (60, 12, 7.5, 5, 5, (0, 0), 'grass'))):
        c = asset('DRAGONBALL_ROCKS', nm)
        S.spire(nm + '_Malha', c, h, r0, r1, tiers, seed, lean=lean, top=top)
        for k in range(3):
            zc = h*(k + .5)/3
            col_cyl((lean[0]*zc, lean[1]*zc, zc), r0 + (r1 - r0)*(k + .5)/3 - .6, h/3)
        if top == 'grass':
            cyl('TroncoTopo', (0, 0, h + 4), .6, 6, 'db_trunk', 'Z', False)
            for (x, y, z, d, m) in ((0, 0, h + 8.5, 8, 'tree_ball'), (2.6, 1.2, h + 7.2, 5.5, 'tree_ball_light'), (-2.4, -1, h + 7.4, 5.2, 'tree_ball_dark')):
                ball('CopaTopo', (x, y, z), d, m)
    c = asset('DRAGONBALL_ROCKS', 'Rocha_Equilibrio')
    S.spire('Equilibrio_Base', c, 30, 7.5, 3.4, 2, 9, top='rock')
    bm = S.boulder('Equilibrio_Pedra', c, size=(18, 15, 13), seed=11, sub=2, flat_bottom=False, loc=(1.5, 0, 28))
    S.to_object('Equilibrio_Pedra', bm, c, smooth=False)
    col_cyl((0, 0, 7), 6.5, 14); col_cyl((0, 0, 22), 3.2, 16)
    c = asset('DRAGONBALL_ROCKS', 'Arco_Rocha')
    S.arch('Arco_Malha', c, span=38, leg_r=7, height=28, seed=4)
    for s in (-1, 1): col_cyl((s*19, 0, 14), 6.5, 28)
    for nm, (w, d, h, layers, seed) in (('Penhasco', (40, 34, 60, 3, 7)), ('Penhasco_Baixo', (44, 34, 34, 2, 8))):
        c = asset('DRAGONBALL_ROCKS', nm)
        S.massif(nm + '_Malha', c, w, d, h, layers, seed)
        col_box((0, 0, h*.25), (w*.9, d*.9, h*.5))
        col_box((0, 0, h*.72), (w*.7, d*.7, h*.44))
        for (x, y, dd, m) in ((w*.12, -d*.08, 8, 'tree_ball'), (-w*.15, d*.1, 6, 'tree_ball_dark'), (w*.02, d*.14, 5, 'tree_ball_light')):
            ball('Copa', (x, y, h + 3.2), dd, m)
    c = asset('DRAGONBALL_ROCKS', 'Mesa_Natural')
    S.massif('Mesa_Malha', c, 30, 24, 10, 1, 12)
    col_box((0, 0, 5), (29, 23, 10))

def islet_sculpt():
    import dbshapes as S
    c = asset('DRAGONBALL_DECORATION', 'Ilhota_Flutuante')
    S.islet('Ilhota_Malha', c, 16, 34, 6)
    S.spire('Ilhota_Pilar', c, 28, 4.8, 3.4, 2, 21, top='grass').location = (-6, 3, 0)
    cyl('Tronco', (7, -3, 4), .6, 8, 'db_trunk', 'Z', False)
    ball('Copa', (7, -3, 10), 9, 'tree_ball')
    ball('Copa', (9.5, -1, 8.8), 6, 'tree_ball_light')
    ball('Copa', (4.6, -4.4, 9), 5.5, 'tree_ball_dark')
    box('Cachoeirinha', (15.4, 2, -8), (1, 4, 16), 'db_water', (0, 0, 0), False)

def build():
    rocks(); nature(); sky()
    rocks_sculpt(); islet_sculpt()

# ------------------------------------------------------------------ STYLIZED TREES v2 (broad cloud crowns, no lollipops)
def _crown(center, cw, ch, tones, seed, n=11, flat=.35):
    """Cluster of overlapping blobs on a wide, flattened dome (remeshed later into one puffy crown per tone)."""
    r = rng(seed)
    main, dark, light = tones
    cx, cy, cz = center
    ball('Copa', (cx, cy, cz + ch*.08), cw*.62, main)
    for k in range(n):
        a = k/n*2*PI + r.uniform(-.25, .25)
        e = r.uniform(-.35, .85)
        rad = cw*.5*(1 - .35*max(e, 0))
        x = cx + math.cos(a)*rad*math.cos(e)
        y = cy + math.sin(a)*rad*math.cos(e)
        z = cz + ch*.42*math.sin(e)
        d = cw*r.uniform(.32, .44)*(1 - .25*max(e, 0))
        tone = light if e > .45 else (dark if e < -.05 else main)
        ball('Copa', (x, y, z), d, tone)
    # underside kept flatter (stylized canopy)
    for k in range(5):
        a = k/5*2*PI + .3
        ball('Copa', (cx + math.cos(a)*cw*.28, cy + math.sin(a)*cw*.28, cz - ch*flat), cw*.36, dark)
    ball('CopaTopo', (cx - cw*.08, cy - cw*.06, cz + ch*.46), cw*.34, light)

def trees_v2():
    import dbshapes as S
    DB = ('tree_ball', 'tree_ball_dark', 'tree_ball_light')
    KO = ('foliage', 'foliage_dark', 'foliage_light')
    specs = [
        # name, height, r0, r1, crown width, crown height, tones, bark, seed, lean
        ('Arvore_Bola_G', 14, 1.6, .9, 22, 13, DB, 'db_trunk', 21, (.08, .03)),
        ('Arvore_Bola_M', 10, 1.15, .65, 15, 9.5, DB, 'db_trunk', 22, (-.06, .05)),
        ('Arvore_Konoha_G', 16, 1.9, 1.0, 26, 15, KO, 'trunk', 31, (.05, -.04)),
        ('Arvore_Konoha_M', 11, 1.3, .7, 17, 11, KO, 'trunk', 32, (-.05, .04)),
        ('Arvore_Konoha_Gigante', 30, 3.6, 1.8, 44, 24, KO, 'trunk', 33, (.04, .02)),
    ]
    for (nm, h, r0, r1, cw, ch, tones, bark, seed, lean) in specs:
        c = asset('DRAGONBALL_NATURE', nm)
        ob, top, tips = S.trunk_mesh(nm + '_Tronco', c, h, r0, r1, lean, 3 if cw < 30 else 5, 4 if cw < 30 else 6, seed, bark, 'db_trunk' if bark == 'trunk' else 'db_rock_deep')
        cz = h + ch*.18
        _crown((top.x, top.y, cz), cw, ch, tones, seed, 11 if cw < 30 else 16)
        c['TrunkLen'] = h
        cyl('ColisaoTronco', (0, 0, h*.35), r0*.8, h*.7, 'invisible', 'Z', True)
    # Namek-style tree: two stacked crowns on a curved trunk (not a single ball on a stick)
    c = asset('DRAGONBALL_NATURE', 'Arvore_Ajisa')
    ob, top, tips = S.trunk_mesh('Ajisa_Tronco', c, 17, 1.1, .6, (.1, .02), 2, 3, 41, 'db_trunk', 'db_rock_deep')
    _crown((top.x, top.y, 18.5), 13, 9, ('tree_ajisa', 'tree_ball_dark', 'tree_ball_light'), 41, 9)
    _crown((tips[0].x, tips[0].y, tips[0].z + 1), 8, 6, ('tree_ajisa', 'tree_ball_dark', 'tree_ball_light'), 42, 7)
    cyl('ColisaoTronco', (0, 0, 5), .9, 10, 'invisible', 'Z', True)
    # Konoha cedar: tiered conical crown
    c = asset('DRAGONBALL_NATURE', 'Cedro_Konoha')
    ob, top, tips = S.trunk_mesh('Cedro_Tronco', c, 22, 1.4, .5, (0, 0), 0, 4, 51, 'trunk', 'db_trunk')
    for k in range(6):
        z = 7 + k*3.0
        w = 17 - k*2.5
        r = rng(60 + k)
        for i in range(7):
            a = i/7*2*PI + k*.4
            ball('Copa', (math.cos(a)*w*.26, math.sin(a)*w*.26, z + r.uniform(-.4, .4)), w*.5, 'foliage_dark' if k % 2 == 0 else 'foliage')
    ball('CopaTopo', (0, 0, 24.5), 5.5, 'foliage_light')
    cyl('ColisaoTronco', (0, 0, 6), 1.2, 12, 'invisible', 'Z', True)
    c['TrunkLen'] = 22

_old_build = build
def build():
    _old_build()
    trees_v2()

# ------------------------------------------------------------------ STYLIZED TREES v3 (leaf-card canopies, reference: Genshin/Ghibli stylized trees)
def _tree3(nm, h, r0, r1, branches, clump_r, palette, inner, bark, bark_dark, seed, lean=(0, 0), fill=2, density=1.0, spread=1.0):
    import dbshapes as S
    from mathutils import Vector as V3
    r = rng(seed)
    c = asset('DRAGONBALL_NATURE', nm)
    ob, top, tips = S.trunk_mesh(nm + '_Tronco', c, h, r0, r1, lean, branches, 4 if r0 < 2.5 else 6, seed, bark, bark_dark)
    clumps = []
    for tp in tips:
        dirv = V3((tp.x - top.x*.6, tp.y - top.y*.6, 0))
        off = dirv.normalized()*clump_r*.25*spread if dirv.length > .01 else V3()
        clumps.append((tp + off + V3((0, 0, clump_r*.15)), clump_r*r.uniform(.85, 1.1)))
    clumps.append((top + V3((0, 0, clump_r*.55)), clump_r*1.2))
    cen = sum((p for p, _ in clumps), V3())/len(clumps)
    for k in range(fill):
        a = r.uniform(0, 2*PI)
        clumps.append((cen + V3((math.cos(a)*clump_r*.9, math.sin(a)*clump_r*.9, -clump_r*.2)), clump_r*.85))
    cen = sum((p for p, _ in clumps), V3())/len(clumps)
    for (p, rr) in clumps:
        ball('CopaInterna', tuple(p), rr*1.35, inner)
    S.foliage(nm + '_Folhas', c, clumps, cen, seed, palette, density)
    cyl('ColisaoTronco', (0, 0, h*.35), r0*.8, h*.7, 'invisible', 'Z', True)
    return c

def trees_v3():
    import dbshapes as S
    from mathutils import Vector as V3
    _tree3('Arvore_Bola_G', 13, 1.5, .8, 5, 6.5, ('light', 'mid', 'dark'), 'tree_ball_dark', 'db_trunk', 'db_rock_deep', 71, (.05, .02))
    _tree3('Arvore_Bola_M', 9, 1.1, .6, 4, 4.8, ('light', 'mid', 'dark'), 'tree_ball_dark', 'db_trunk', 'db_rock_deep', 72, (-.04, .03))
    _tree3('Arvore_Ajisa', 15, 1.1, .55, 3, 4.6, ('teal', 'teal', 'dark'), 'tree_ajisa', 'db_trunk', 'db_rock_deep', 73, (.07, 0), fill=1)
    _tree3('Arvore_Konoha_G', 15, 1.8, .95, 5, 7.5, ('mid', 'mid', 'dark'), 'foliage_dark', 'trunk', 'db_trunk', 81, (.04, -.03))
    _tree3('Arvore_Konoha_M', 10, 1.25, .7, 4, 5.5, ('light', 'mid', 'dark'), 'foliage_dark', 'trunk', 'db_trunk', 82, (-.04, .03))
    _tree3('Arvore_Konoha_Gigante', 28, 3.4, 1.7, 7, 12, ('mid', 'mid', 'dark'), 'foliage_dark', 'trunk', 'db_trunk', 83, (.03, .02), fill=4, density=1.1)
    # conifer: stacked tiers of leaf clumps along the trunk
    c = asset('DRAGONBALL_NATURE', 'Cedro_Konoha')
    ob, top, tips = S.trunk_mesh('Cedro_Tronco', c, 24, 1.4, .45, (0, 0), 0, 4, 91, 'trunk', 'db_trunk')
    clumps = []
    for k in range(7):
        z = 6 + k*3.0
        rad = 7.5 - k*.95
        for i in range(4 if rad > 3 else 2):
            a = i/4*2*PI + k*.7
            clumps.append((V3((math.cos(a)*rad*.45, math.sin(a)*rad*.45, z)), rad*.62))
    clumps.append((V3((0, 0, 26.5)), 2.2))
    for (p, rr) in clumps:
        ball('CopaInterna', tuple(p), rr*1.3, 'foliage_dark')
    S.foliage('Cedro_Folhas', c, clumps, V3((0, 0, 15)), 91, ('mid', 'dark', 'dark'), .8)
    cyl('ColisaoTronco', (0, 0, 6), 1.2, 12, 'invisible', 'Z', True)

def build():
    _old_build()
    trees_v3()
