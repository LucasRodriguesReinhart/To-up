# lv_kit.py - pecas do lobby (linguagem do Anime Expeditions):
# postes ornamentados, balaustradas, gazebos de cupula azul, pontes, canteiros,
# arvores de copa esferica por cor, palmeiras, fontes, cristais.
# Cada funcao carimba geometria direto num acumulador B (lvlib), com pos/rot.
import math, random
import importlib
import lvlib
importlib.reload(lvlib)
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, arch_wall, puff_cloud, stairs, merge, _xform
from mathutils import Vector, Matrix, Euler
import bmesh

TAU = math.tau

def _rz(pos, rot_z, about=(0, 0, 0)):
    """gira um ponto em torno de about no plano XY"""
    x, y = pos[0] - about[0], pos[1] - about[1]
    c, s = math.cos(rot_z), math.sin(rot_z)
    return (about[0] + x * c - y * s, about[1] + x * s + y * c, pos[2])

# ---------------------------------------------------------------- POSTE (ref. imagem 7)
def lamp_post(out, pos, rot=0.0, scale=1.0, glow='NEON'):
    s = scale
    x, y, z = pos
    # base: plinto quadrado + molde
    out.add('TRIM', box((2.2*s, 2.2*s, .5*s), (x, y, z + .25*s), bevel=.08))
    out.add('MARB', lathe([(1.05*s, 0), (1.1*s, .3*s), (.78*s, .55*s), (.62*s, .9*s)], (x, y, z + .5*s), seg=12))
    out.add('GOLD', torus(.6*s, .15*s, (x, y, z + 1.15*s), seg=14, sides=7))
    # fuste canelado (8 cilindros finos ao redor de um nucleo)
    h = 8.2 * s
    out.add('MARB', cyl(.42*s, h, (x, y, z + 1.05*s), seg=10))
    for i in range(8):
        a = i / 8 * TAU
        out.add('MARB', cyl(.1*s, h, (x + math.cos(a)*.44*s, y + math.sin(a)*.44*s, z + 1.05*s), seg=6))
    out.add('GOLD', torus(.54*s, .16*s, (x, y, z + 1.0*s + h), seg=14, sides=7))
    # colar de petalas sob a lanterna
    top = z + 1.05*s + h + .2*s
    for i in range(6):
        a = i / 6 * TAU
        px, py = x + math.cos(a)*.75*s, y + math.sin(a)*.75*s
        out.add('MARB', ball(.5*s, (px, py, top + .35*s), seg=8, scl=(1, .5, 1.3)))
    out.add('MARB', lathe([(.4*s, 0), (.68*s, .5*s), (.5*s, .9*s)], (x, y, top), seg=12))
    # lanterna: copo de vidro + tampa dourada + coroa
    lz = top + .9*s
    out.add(glow, lathe([(.38*s, 0), (.6*s, .4*s), (.62*s, 1.3*s), (.4*s, 1.8*s)], (x, y, lz), seg=10))
    out.add('GOLD', lathe([(.66*s, 0), (.7*s, .14*s), (.24*s, .55*s), (.14*s, .8*s), (.3*s, .98*s), (.02*s, 1.7*s)], (x, y, lz + 1.75*s), seg=10))
    out.add('GOLD', torus(.56*s, .08*s, (x, y, lz + .12*s), seg=12, sides=5))

# ---------------------------------------------------------------- BALAUSTRADA
def balustrade(out, p1, p2, z, h=3.0, spacing=2.1, posts=True):
    """corrimao entre p1 e p2 no plano (x,y), base em z."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    if L < .5:
        return
    a = math.atan2(dy, dx)
    mid = ((x1+x2)/2, (y1+y2)/2)
    rot = (0, 0, a)
    # trilho inferior e superior
    out.add('MARB', box((L, .8, .5), (mid[0], mid[1], z + .25), rot, bevel=.08))
    out.add('MARB', box((L, .9, .55), (mid[0], mid[1], z + h - .45), rot, bevel=.12))
    out.add('GOLD', box((L, .34, .12), (mid[0], mid[1], z + h + .02), rot))
    # balaustres torneados
    n = max(1, int(L / spacing))
    for i in range(n + 1):
        t = i / n if n else .5
        px, py = x1 + dx * t, y1 + dy * t
        out.add('MARB', lathe([(.3, 0), (.38, .18), (.18, .5), (.4, 1.1), (.44, 1.5), (.19, 1.9), (.33, 2.1)],
                              (px, py, z + .5), seg=8))

def rail_post(out, pos, z, h=3.6):
    x, y = pos
    out.add('MARB', box((1.1, 1.1, h), (x, y, z + h/2), bevel=.1))
    out.add('GOLD', box((1.3, 1.3, .18), (x, y, z + h + .09)))
    out.add('MARB', ball(.42, (x, y, z + h + .5), seg=8))

# ---------------------------------------------------------------- GAZEBO de cupula azul
def gazebo(out, pos, rot=0.0, r=7.0, glow_lantern=True):
    x, y, z = pos
    seg = 6
    # base em 2 degraus circulares
    out.add('TRIM', cyl(r + 2.4, .7, (x, y, z), seg=24, bevel=.1))
    out.add('MARB', cyl(r + 1.4, .7, (x, y, z + .7), seg=24, bevel=.1))
    out.add('TILE2', cyl(r + .6, .5, (x, y, z + 1.4), seg=24))
    floor_z = z + 1.9
    out.add('BLUE', cyl(r * .45, .12, (x, y, floor_z), seg=18))
    out.add('GOLD', torus(r * .45 + .18, .09, (x, y, floor_z + .08), seg=20, sides=5))
    # colunas com capitel dourado
    col_h = 8.4
    for i in range(seg):
        a = i / seg * TAU + rot
        px, py = x + math.cos(a) * r * .82, y + math.sin(a) * r * .82
        out.add('TRIM', box((1.5, 1.5, .4), (px, py, floor_z + .2), (0, 0, a)))
        out.add('MARB', lathe([(.62, 0), (.5, .35), (.48, col_h - 1.1), (.58, col_h - .7), (.66, col_h - .3), (.6, col_h)],
                              (px, py, floor_z + .4), seg=10))
        out.add('GOLD', box((1.35, 1.35, .3), (px, py, floor_z + .4 + col_h + .1), (0, 0, a)))
    # arcos entre colunas (semicirculo abrindo pra CIMA)
    ent_z = floor_z + .4 + col_h + .3
    for i in range(seg):
        a1 = i / seg * TAU + rot
        a2 = (i + 1) / seg * TAU + rot
        p1 = (x + math.cos(a1) * r * .82, y + math.sin(a1) * r * .82)
        p2 = (x + math.cos(a2) * r * .82, y + math.sin(a2) * r * .82)
        mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
        L = math.hypot(p2[0]-p1[0], p2[1]-p1[1])
        aa = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
        out.add('MARB', torus(L * .46, .32, (mid[0], mid[1], ent_z - .2), (-math.pi/2, 0, aa), seg=10, sides=6, arc=math.pi))
    # entablamento + friso dourado
    out.add('MARB', cyl(r + .4, 1.1, (x, y, ent_z), seg=24, bevel=.15))
    out.add('GOLD', cyl(r + .52, .3, (x, y, ent_z + .35), seg=24))
    out.add('TRIM', cyl(r + .7, .45, (x, y, ent_z + 1.1), seg=24, bevel=.1))
    # cupula de vidro azul com gomos dourados (meridianos)
    dome_z = ent_z + 1.55
    prof = []
    for i in range(7):
        t = i / 6
        prof.append((math.cos(t * math.pi/2) * r * .92, math.sin(t * math.pi/2) * r * .66))
    out.add('GLASS', lathe(prof, (x, y, dome_z), seg=20))
    for i in range(seg):
        a = i / seg * TAU + rot + TAU/(seg*2)
        bmrib = bmesh.new()
        prev = None
        for k in range(7):
            t = k / 6
            rr = math.cos(t * math.pi/2) * r * .95
            zz = math.sin(t * math.pi/2) * r * .66
            px, py = math.cos(a) * rr, math.sin(a) * rr
            v1 = bmrib.verts.new((px - math.sin(a)*.22, py + math.cos(a)*.22, zz))
            v2 = bmrib.verts.new((px + math.sin(a)*.22, py - math.cos(a)*.22, zz))
            v3 = bmrib.verts.new((px * 1.035, py * 1.035, zz + .18))
            if prev:
                bmrib.faces.new([prev[0], v1, v3, prev[2]])
                bmrib.faces.new([prev[2], v3, v2, prev[1]])
            prev = (v1, v2, v3)
        bmesh.ops.recalc_face_normals(bmrib, faces=bmrib.faces)
        _xform(bmrib, (x, y, dome_z))
        out.add('GOLD', bmrib)
    # coroa + agulha
    tip = dome_z + r * .62
    out.add('GOLD', lathe([(.7, 0), (.78, .2), (.3, .5), (.34, .8), (.02, 2.4)], (x, y, tip - .1), seg=10))
    if glow_lantern:
        out.add('NEON', ball(.9, (x, y, floor_z + 4.6), seg=8))
        out.add('GOLD', cyl(.06, 2.4, (x, y, floor_z + 5.4), seg=5))

# ---------------------------------------------------------------- PONTE em arco
def bridge(out, pos, rot=0.0, L=16.0, W=7.0, rise=1.6):
    """ponte cruzando o eixo local X (comprimento L), tabuleiro em arco suave."""
    x, y, z = pos
    n = 8
    for i in range(n):
        t0 = i / n - .5
        t1 = (i + 1) / n - .5
        z0 = math.cos(t0 * math.pi) * rise
        z1 = math.cos(t1 * math.pi) * rise
        mx = (t0 + t1) / 2 * L
        seg_l = L / n + .12
        ang = math.atan2(z1 - z0, L / n)
        px, py, pz = _rz((x + mx, y, z + (z0 + z1)/2), rot, (x, y, 0))
        out.add('TILE2', box((seg_l, W, .55), (px, py, pz), (0, -ang, rot)))
    # bordas + balaustrada
    for sy in (-1, 1):
        for i in range(n):
            t0 = i / n - .5
            t1 = (i + 1) / n - .5
            z0 = math.cos(t0 * math.pi) * rise
            z1 = math.cos(t1 * math.pi) * rise
            mx = (t0 + t1) / 2 * L
            ang = math.atan2(z1 - z0, L / n)
            px, py, pz = _rz((x + mx, y + sy * (W/2 + .3), z + (z0+z1)/2 + .15), rot, (x, y, 0))
            out.add('MARB', box((L/n + .12, .7, .9), (px, py, pz), (0, -ang, rot), bevel=.1))
            px, py, pz = _rz((x + mx, y + sy * (W/2 + .3), z + (z0+z1)/2 + 2.2), rot, (x, y, 0))
            out.add('MARB', box((L/n + .12, .62, .5), (px, py, pz), (0, -ang, rot), bevel=.1))
            out.add('GOLD', box((L/n + .12, .3, .1), (px, py, pz + .3), (0, -ang, rot)))
            if i % 2 == 0:
                bx, by, bz = _rz((x + (t0 + .5/n) * L, y + sy * (W/2 + .3), z + (z0+z1)/2 + .6), rot, (x, y, 0))
                out.add('MARB', lathe([(.2, 0), (.26, .2), (.12, .5), (.24, 1.0), (.28, 1.3), (.1, 1.55)], (bx, by, bz), seg=7))
    # arco inferior (barriga da ponte)
    for sy in (-1, 1):
        px, py, pz = _rz((x, y + sy * (W/2 - .8), z - .4), rot, (x, y, 0))
        out.add('TRIM', torus(L * .42, .55, (px, py, pz), (math.pi/2, 0, rot), seg=12, sides=6, arc=math.pi))
    # postes das pontas
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py, pz = _rz((x + sx * (L/2 - .5), y + sy * (W/2 + .3), z + .2), rot, (x, y, 0))
            rail_post(out, (px, py), pz, 3.2)

# ---------------------------------------------------------------- CANTEIRO octogonal (ref. imagem 6)
def planter(out, pos, r=5.0, sides=8, rim_h=1.6, soil='GRASS'):
    x, y, z = pos
    pts_o = [(math.cos((i + .5)/sides*TAU)*r, math.sin((i + .5)/sides*TAU)*r) for i in range(sides)]
    pts_i = [(px*.82, py*.82) for (px, py) in pts_o]
    out.add('TRIM', ngon_prism(pts_o, rim_h * .45, (x, y, z)))
    out.add('MARB', ngon_prism([(px*1.04, py*1.04) for px, py in pts_o], rim_h * .35, (x, y, z + rim_h*.45)))
    out.add('MARB', ngon_prism(pts_o, rim_h * .35, (x, y, z + rim_h*.7)))
    out.add('GOLD', ngon_prism([(px*1.01, py*1.01) for px, py in pts_o], .1, (x, y, z + rim_h*.78)))
    out.add(soil, ngon_prism(pts_i, rim_h + .1, (x, y, z)))

# ---------------------------------------------------------------- ARVORES
def puff_tree(out, pos, swatch, h=10.0, r=5.2, seed=1, lean=0.0):
    """arvore de copa esferica (bolhas fundidas), tronco com galhos."""
    x, y, z = pos
    rng = random.Random(seed)
    leafmat = lvlib.SW2MAT[swatch]
    # tronco: 3 segmentos levemente tortos
    ang = rng.uniform(0, TAU)
    cx, cy = x, y
    seg_h = h / 3
    for i in range(3):
        tilt = lean + rng.uniform(-.06, .1)
        out.add('TRUNK', cyl(.9 - i * .22, seg_h + .4, (cx, cy, z + i * seg_h), rot=(tilt, 0, ang), seg=8))
        cx += math.cos(ang) * math.sin(tilt) * seg_h
        cy += math.sin(ang) * math.sin(tilt) * seg_h
    # galhos
    for i in range(3):
        a = ang + i * TAU/3 + rng.uniform(-.4, .4)
        gl = rng.uniform(2.2, 3.4)
        gx, gy, gz = cx + math.cos(a)*gl*.5, cy + math.sin(a)*gl*.5, z + h - seg_h*.4
        out.add('TRUNK', cyl(.3, gl, (gx, gy, gz), rot=(math.pi/2.6, 0, a + math.pi/2), seg=6))
    # copa
    centers = [(cx, cy, z + h + r * .35, r)]
    for i in range(5):
        a = rng.uniform(0, TAU)
        rr = r * rng.uniform(.42, .62)
        centers.append((cx + math.cos(a) * r * .62, cy + math.sin(a) * r * .62,
                        z + h + r * .3 + rng.uniform(-.18, .55) * r, rr))
    centers.append((cx, cy, z + h + r * .95, r * .55))
    out.add(leafmat, puff_cloud(centers, r, seed))

def palm_tree(out, pos, h=13.0, seed=1, swatch='verde'):
    x, y, z = pos
    rng = random.Random(seed)
    leafmat = lvlib.SW2MAT[swatch]
    ang = rng.uniform(0, TAU)
    lean = rng.uniform(.05, .16)
    # tronco em aneis
    n = 7
    cx, cy = x, y
    for i in range(n):
        t = i / n
        sh = h / n
        out.add('TRUNK', lathe([(.62 - t*.3, 0), (.5 - t*.24, sh*.6), (.66 - t*.3, sh + .1)],
                               (cx, cy, z + i * sh), seg=8))
        cx += math.cos(ang) * lean * sh
        cy += math.sin(ang) * lean * sh
    top = (cx, cy, z + h + .3)
    # folhas: laminas arqueadas
    nf = 9
    for i in range(nf):
        a = i / nf * TAU + rng.uniform(-.2, .2)
        droop = rng.uniform(.5, .8)
        bm = bmesh.new()
        L, W = rng.uniform(5.8, 7.4), 2.0
        segs = 5
        prev = None
        for sgi in range(segs + 1):
            t = sgi / segs
            zz = math.sin(t * math.pi * .55) * L * .32 - t * t * L * droop * .45
            xx = t * L
            wid = W * (1 - t * .75) * (math.sin(min(t * 3, 1) * math.pi / 2))
            v1 = bm.verts.new((xx, -wid/2, zz))
            v2 = bm.verts.new((xx, wid/2, zz))
            vc = bm.verts.new((xx, 0, zz + .28))
            if prev:
                bm.faces.new([prev[0], v1, vc, prev[2]])
                bm.faces.new([prev[2], vc, v2, prev[1]])
            prev = (v1, v2, vc)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        _xform(bm, top, (0, 0, a))
        out.add(leafmat, bm)
    # cocos
    for i in range(3):
        a = rng.uniform(0, TAU)
        out.add('TRUNK', ball(.42, (top[0] + math.cos(a)*.6, top[1] + math.sin(a)*.6, top[2] - .3), seg=6))

def bush(out, pos, r=2.2, swatch='verde', seed=1, flowers=None, n_fl=5):
    x, y, z = pos
    rng = random.Random(seed)
    leafmat = lvlib.SW2MAT[swatch]
    centers = [(x, y, z + r * .55, r)]
    for i in range(3):
        a = rng.uniform(0, TAU)
        centers.append((x + math.cos(a) * r * .55, y + math.sin(a) * r * .55, z + r * .4, r * rng.uniform(.5, .7)))
    out.add(leafmat, puff_cloud(centers, r, seed))
    if flowers:
        flmat = lvlib.SW2MAT[flowers]
        for i in range(n_fl):
            a = rng.uniform(0, TAU)
            rr = r * rng.uniform(.4, .95)
            out.add(flmat, ball(.28, (x + math.cos(a)*rr, y + math.sin(a)*rr, z + r*.55 + rng.uniform(.2, .6)*r), seg=6))

def grass_tuft(out, pos, seed=1, swatch='grama'):
    x, y, z = pos
    rng = random.Random(seed)
    leafmat = lvlib.SW2MAT[swatch]
    bm = bmesh.new()
    for i in range(5):
        a = rng.uniform(0, TAU)
        h = rng.uniform(.7, 1.4)
        w = .22
        bx = math.cos(a) * .3
        by = math.sin(a) * .3
        v1 = bm.verts.new((bx - w, by, 0))
        v2 = bm.verts.new((bx + w, by, 0))
        v3 = bm.verts.new((bx + math.cos(a) * .35, by + math.sin(a) * .35, h))
        bm.faces.new([v1, v2, v3])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _xform(bm, (x, y, z), (0, 0, rng.uniform(0, TAU)))
    out.add(leafmat, bm)

# ---------------------------------------------------------------- FONTE ornamental
def fountain(out, pos, r=6.5):
    x, y, z = pos
    out.add('TRIM', cyl(r + .9, .6, (x, y, z), seg=20, bevel=.1))
    out.add('MARB', lathe([(r + .7, 0), (r + .8, .6), (r + .55, .9), (r + .45, 1.5), (r + .75, 1.8), (r + .6, 2.0)], (x, y, z), seg=20))
    out.add('MARB', lathe([(r - .5, 1.9), (r - .7, .4)], (x, y, z), seg=20))
    out.add('WATER', cyl(r - .55, .25, (x, y, z + 1.25), seg=20))
    # taca central em dois niveis
    out.add('MARB', lathe([(1.5, 0), (1.05, .7), (.8, 3.4), (1.3, 4.0), (3.4, 4.7), (3.8, 5.3), (3.3, 5.5), (3.0, 5.0)], (x, y, z + .4), seg=16))
    out.add('WATER', cyl(3.1, .2, (x, y, z + 5.4), seg=16))
    out.add('MARB', lathe([(.9, 0), (.6, .5), (.5, 1.7), (1.5, 2.2), (1.8, 2.6), (1.5, 2.75), (1.3, 2.3)], (x, y, z + 5.5), seg=12))
    out.add('WATER', cyl(1.35, .16, (x, y, z + 7.9), seg=12))
    out.add('GOLD', lathe([(.55, 0), (.65, .2), (.18, .55), (.02, 1.9)], (x, y, z + 8.1), seg=10))
    # veus d'agua da taca pro tanque
    for i in range(6):
        a = i / 6 * TAU
        out.add('FOAM', cyl(.2, 3.6, (x + math.cos(a)*3.4, y + math.sin(a)*3.4, z + 1.6), rot=(.12, 0, a), seg=5))

# ---------------------------------------------------------------- CRISTAIS (identidade mineracao)
def crystal_cluster(out, pos, r=2.6, h=6.5, seed=1, mat='NEON'):
    x, y, z = pos
    rng = random.Random(seed)
    n = rng.randint(4, 6)
    for i in range(n):
        a = i / n * TAU + rng.uniform(-.3, .3)
        rr = r * rng.uniform(.3, 1.0)
        hh = h * rng.uniform(.4, 1.0)
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=hh * .2, radius2=hh * .04, depth=hh)
        _xform(bm, (px, py, z + hh/2 - .4), (rng.uniform(-.35, .35), rng.uniform(-.35, .35), a))
        out.add(mat, bm)

# ---------------------------------------------------------------- NENUFAR / detalhes de agua
def lily_pad(out, pos, r=1.0, seed=1):
    x, y, z = pos
    rng = random.Random(seed)
    out.add(lvlib.SW2MAT['verde'] if isinstance('verde', str) else 'verde', cyl(r, .07, (x, y, z), seg=9))
    if rng.random() < .4:
        out.add(lvlib.SW2MAT['flor_rs'] if isinstance('flor_rs', str) else 'flor_rs', ball(.3, (x + r*.3, y, z + .2), seg=6))

def canal_rock(out, pos, r=1.4, seed=1):
    x, y, z = pos
    rng = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=r)
    for v in bm.verts:
        v.co.x *= rng.uniform(.75, 1.25)
        v.co.y *= rng.uniform(.75, 1.25)
        v.co.z *= rng.uniform(.5, .8)
    _xform(bm, (x, y, z), (0, 0, rng.uniform(0, TAU)))
    out.add('ROCK', bm)

# ---------------------------------------------------------------- BANDEIRA / estandarte
def banner(out, pos, rot=0.0, h=9.0, cloth='BLUE'):
    x, y, z = pos
    out.add('TRIM', box((1.4, 1.4, .5), (x, y, z + .25)))
    out.add('MARB', cyl(.28, h, (x, y, z + .5), seg=8))
    out.add('GOLD', ball(.42, (x, y, z + h + .6), seg=8))
    arm = 2.6
    dx, dy = math.cos(rot), math.sin(rot)
    out.add('GOLD', cyl(.12, arm, (x + dx*arm/2, y + dy*arm/2, z + h + .1), rot=(0, math.pi/2, rot), seg=6))
    bm = bmesh.new()
    W, H = arm * .8, 4.4
    seg = 5
    prev = None
    for i in range(seg + 1):
        t = i / seg
        sway = math.sin(t * math.pi) * .3
        v1 = bm.verts.new((t * W + .3, sway, 0))
        v2 = bm.verts.new((t * W + .3, sway, -H * (1 - t * .18)))
        if prev:
            bm.faces.new([prev[0], v1, v2, prev[1]])
        prev = (v1, v2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _xform(bm, (x, y, z + h), (0, 0, rot))
    out.add(cloth, bm)
