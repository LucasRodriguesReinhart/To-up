# trecho_piso_agua.py - pequeno trecho de piso (lajotas com juntas e meio-fio em relevo, padrao claro da referencia)
# e pequena margem de agua (meio-fio arredondado, leito com pedras e profundidade variavel; a agua e Terrain no Roblox).
import bpy, bmesh, math, random
from mathutils import Vector
import trecho_torre as T
from trecho_torre import new_obj, clear, MAT, apply_bevel, hsweep
import trecho_escada as E

def build_floor(col):
    objs = []
    rnd = random.Random(5)
    # lajotas 3.6 x 3.6 entre y=-19.5 (pe da escada) e y=+5, x -15..15 (fora da escada: a escada comeca em -19.5)
    bm = bmesh.new()
    y = -19.5
    while y < 5.0:
        x = -14.4
        while x < 14.4:
            z = -.4 + rnd.uniform(-.025, .025)
            r = bmesh.ops.create_cube(bm, size=1)
            vs = r['verts']
            bmesh.ops.scale(bm, vec=(3.5, 3.5, .4), verts=vs)
            bmesh.ops.translate(bm, vec=(x + 1.8, y + 1.8, z + .2), verts=vs)
            x += 3.6
        y += 3.6
    o = new_obj('PISO_lajotas', bm, col, MAT['FLOOR']); apply_bevel(o, .06, 2, 60); objs.append(o)
    # base continua sob as juntas (junta mais escura) e sob o trecho
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(30, 25, .5), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, -7.25, -.55), verts=bm.verts); objs.append(new_obj('PISO_base', bm, col, T.M('T_JUNTA', (.5, .47, .43))))
    # meio-fio em relevo formando o painel apontado da referencia (ref_stairs_edge): contorno de .5 de largura e .2 de altura
    def curb(pts, nm):
        bm = bmesh.new()
        n = len(pts)
        for i in range(n):
            p0 = Vector((pts[i][0], pts[i][1], 0)); p1 = Vector((pts[(i + 1) % n][0], pts[(i + 1) % n][1], 0))
            d = (p1 - p0); L = d.length; d.normalize(); nrm = Vector((-d.y, d.x, 0))
            c = (p0 + p1) / 2
            r = bmesh.ops.create_cube(bm, size=1); vs = r['verts']
            bmesh.ops.scale(bm, vec=(L + .5, .5, .2), verts=vs)
            ang = math.atan2(d.y, d.x)
            bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__('mathutils').Matrix.Rotation(ang, 3, 'Z'), verts=vs)
            bmesh.ops.translate(bm, vec=(c.x, c.y, .1), verts=vs)
        o = new_obj(nm, bm, col, MAT['TRIM']); apply_bevel(o, .05, 2, 60); return o
    # painel central apontado (losango alongado) na frente do avatar + dois paineis laterais
    objs.append(curb([(0, -16.5), (2.6, -12.5), (2.6, -3.5), (0, .5), (-2.6, -3.5), (-2.6, -12.5)], 'PISO_curb_central'))
    for s in (-1, 1):
        objs.append(curb([(s * 5.5, -14), (s * 10.5, -14), (s * 12.5, -9), (s * 10.5, -4), (s * 5.5, -4), (s * 3.5, -9)], 'PISO_curb_lateral'))
    # insercao clara no painel central (painel de pedra mais clara ligeiramente saliente)
    bm = bmesh.new(); vs = [bm.verts.new((x, y, .06)) for x, y in [(0, -15.5), (1.9, -12.3), (1.9, -3.8), (0, -.5), (-1.9, -3.8), (-1.9, -12.3)]]
    f = bm.faces.new(vs); r = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, 0, -.1), verts=[g for g in r['geom'] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); objs.append(new_obj('PISO_painel_claro', bm, col, MAT['TRIM']))
    return objs

def build_water(col):
    """margem: meio-fio arredondado ao longo de x=15 (de y=-21 a -2), leito descendo de -.5 a -2.2 ate x=27,
    pedras semi-submersas, e uma pedra maior emergindo. Agua (Terrain) de x 15.6..27, topo -.35."""
    objs = []
    rnd = random.Random(9)
    # meio-fio arredondado (perfil varrido ao longo de Y)
    cop = [(0, -.6), (0, .15), (.15, .35), (.45, .45), (.75, .38), (.95, .2), (1.05, 0), (1.05, -.6)]
    for s in (1,):
        bm = bmesh.new(); rings = []
        for yv in (-21.0, -2.0):
            rings.append([bm.verts.new(Vector((15.0 + u, yv, v))) for (u, v) in cop])
        for j in range(len(cop) - 1):
            bm.faces.new([rings[0][j], rings[0][j + 1], rings[1][j + 1], rings[1][j]])
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        objs.append(new_obj('AGUA_meiofio', bm, col, MAT['TRIM']))
    # leito: grade deslocada descendo para fora (profundidade variavel) com ondulacoes
    bm = bmesh.new()
    NX, NY = 14, 22
    grid = []
    for i in range(NX + 1):
        row = []
        for j in range(NY + 1):
            x = 15.6 + i / NX * 11.4; y = -21.0 + j / NY * 19.0
            t = i / NX
            z = -.55 - 1.7 * t ** 1.3 + rnd.uniform(-.08, .08) + .12 * math.sin(x * 1.7 + y * 1.1)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for i in range(NX):
        for j in range(NY):
            bm.faces.new([grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = True
    objs.append(new_obj('AGUA_leito', bm, col, T.M('T_LEITO', (.52, .5, .44), .9)))
    # paredes do leito (fecham lateral e fundo) para nao ver o vazio
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(12.4, 19.4, 3.0), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(21.2, -11.5, -3.2), verts=bm.verts); objs.append(new_obj('AGUA_caixa', bm, col, T.M('T_LEITO', (.52, .5, .44), .9)))
    # pedras: submersas perto da margem e uma maior emergindo
    def rock(pos, r, seed):
        bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)
        rr = random.Random(seed)
        for v in bm.verts: v.co *= 1 + (rr.random() - .5) * .35
        bmesh.ops.scale(bm, vec=(1.2, 1.0, .6), verts=bm.verts); bmesh.ops.translate(bm, vec=pos, verts=bm.verts)
        for f in bm.faces: f.smooth = True
        return new_obj('AGUA_pedra', bm, col, T.M('T_PEDRA', (.6, .6, .58), .85))
    for k in range(9):
        x = rnd.uniform(16.5, 24); y = rnd.uniform(-20, -3)
        objs.append(rock((x, y, -.9 - (x - 15.6) * .12), rnd.uniform(.35, .8), 30 + k))
    objs.append(rock((17.5, -8.0, -.55), 1.25, 50)); objs.append(rock((19.0, -16.5, -.7), 1.0, 51))
    return objs

def build_all():
    col = clear('PISO'); cola = clear('AGUA')
    return build_floor(col) + build_water(cola)
