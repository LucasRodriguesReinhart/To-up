# trecho_poste.py - poste de referencia (ref_lamp_left / user_00): base, aneis, haste com entasis, colar de 6 petalas,
# lanterna octogonal com barras e bracadeiras em X, tampa em disco, cupula e agulha. Perfis desenhados e torneados
# (spin), petala modelada como superficie curva com espessura e repetida radialmente. Altura total ~8.1.
import bpy, bmesh, math
from mathutils import Vector, Matrix
import trecho_torre as T
from trecho_torre import new_obj, clear, MAT, apply_bevel

def M(name, rgb, rough=.8, metal=0.0):
    return T.M(name, rgb, rough, metal)
CREAM = M('T_CREAM', (.90, .87, .80), .7)
MILK = M('T_MILK', (.98, .97, .93), .5)

def spin(profile, seg=24):
    """torneia um perfil [(r, z)...] em torno de Z (spin manual)."""
    bm = bmesh.new(); rings = []
    for r, z in profile:
        if r < 1e-4:
            v = bm.verts.new((0, 0, z)); rings.append([v] * seg)
        else:
            rings.append([bm.verts.new((math.cos(i / seg * math.tau) * r, math.sin(i / seg * math.tau) * r, z)) for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            q = [a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]]
            u = []
            for v in q:
                if v not in u: u.append(v)
            if len(u) >= 3:
                try: bm.faces.new(u)
                except ValueError: pass
    if profile[0][0] > 1e-4:
        try: bm.faces.new(rings[0][::-1])
        except ValueError: pass
    if profile[-1][0] > 1e-4:
        try: bm.faces.new(rings[-1])
        except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def petal():
    """petala: superficie (u ao longo, v atraves) curva para fora com concha, ponta afilada e enrolada; espessura .08."""
    bm = bmesh.new()
    NU, NV = 12, 7
    grid = []
    for i in range(NU + 1):
        u = i / NU                       # 0 base -> 1 ponta
        # petala larga e lisa (lirio): meia-largura .48 na base -> .62 no meio -> ponta arredondada (.22)
        half = .48 + .14 * math.sin(math.pi * min(u / .6, 1.0)) if u < .6 else .62 - .40 * ((u - .6) / .4) ** 1.7
        # eixo: abre para fora desde a base (~40 graus), ponta chega ao raio do disco da lanterna e vira para fora
        flare = (max(0, u - .55) / .45) ** 1.5
        r_axis = .44 + 1.0 * u ** 1.35 + .25 * flare
        z_axis = 1.95 * u - .35 * flare ** 1.3
        row = []
        for j in range(NV + 1):
            v = j / NV - .5
            w = v * 2 * half
            cup = (1 - (2 * v) ** 2) * .16                       # concha suave e constante
            row.append(Vector((w, r_axis - cup, z_axis)))
        grid.append(row)
    verts = [[bm.verts.new(p) for p in row] for row in grid]
    for i in range(NU):
        for j in range(NV):
            bm.faces.new([verts[i][j], verts[i][j + 1], verts[i + 1][j + 1], verts[i + 1][j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update()
    # espessura (solidify manual): copia deslocada pela normal + costura das bordas
    offs = {v: v.normal.copy() * .09 for v in bm.verts}
    res = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    vs = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    # verts novos herdam a posicao dos originais: desloca-os pela normal original correspondente (mais proximo)
    import mathutils
    kd = mathutils.kdtree.KDTree(len(offs)); ids = list(offs.keys())
    for i, v in enumerate(ids): kd.insert(v.co, i)
    kd.balance()
    for v in vs:
        co, idx, d = kd.find(v.co)
        v.co += offs[ids[idx]]
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def build_lamp(col, pos=(0, 0, 0), name='POSTE'):
    x, y, z0 = pos
    objs = []
    def place(bm, nm, mat, dz=0.0):
        bmesh.ops.translate(bm, vec=(x, y, z0 + dz), verts=bm.verts)
        return new_obj(f'{name}_{nm}', bm, col, mat)
    # base de pedra clara (plinto torneado) + anel de ouro no pe
    objs.append(place(spin([(.62, 0), (.62, .22), (.56, .34), (.44, .46), (.40, .62)], 20), 'base', T.MAT['TRIM']))
    objs.append(place(spin([(.36, 0), (.44, .06), (.44, .22), (.34, .30)], 20), 'anel_pe', T.MAT['GOLD'], .62))
    # haste com entasis (mais larga a 1/3) e anel de ouro no topo
    H = 4.7
    objs.append(place(spin([(.31, 0), (.335, H * .3), (.30, H * .7), (.26, H)], 20), 'haste', CREAM, .92))
    objs.append(place(spin([(.26, 0), (.33, .06), (.33, .24), (.25, .30)], 20), 'anel_topo', T.MAT['GOLD'], .92 + H))
    top = .92 + H + .30
    # taca solida sob/dentro das petalas (fecha o interior do calice)
    objs.append(place(spin([(.25, 0), (.36, .2), (.44, .5), (.46, .8), (.40, 1.0), (.0, 1.05)], 20), 'taca', CREAM, top))
    # colar: 6 petalas grandes sobrepostas (+ 6 sepalas menores e mais abertas entre elas)
    for i in range(6):
        bm = petal(); a = i / 6 * math.tau
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, 'Z'), verts=bm.verts)
        objs.append(place(bm, 'petala', CREAM, top + .12))
    for i in range(6):
        bm = petal(); a = (i + .5) / 6 * math.tau
        bmesh.ops.scale(bm, vec=(.7, .7, .6), verts=bm.verts)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(18), 3, 'X'), verts=bm.verts)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, 'Z'), verts=bm.verts)
        objs.append(place(bm, 'sepala', CREAM, top + .02))
    # lanterna octogonal: base de ouro, vidro leitoso, 8 barras nas arestas, bracadeiras em X, anel superior
    lz = top + 1.55; LH = 1.35; R8 = .52
    def octa(r, h, dz):
        bm = bmesh.new()
        pts = [(math.cos((i + .5) / 8 * math.tau) * r, math.sin((i + .5) / 8 * math.tau) * r) for i in range(8)]
        vs = [bm.verts.new((px, py, 0)) for px, py in pts]; f = bm.faces.new(vs)
        res = bmesh.ops.extrude_face_region(bm, geom=[f]); bmesh.ops.translate(bm, vec=(0, 0, h), verts=[g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bmesh.ops.translate(bm, vec=(0, 0, dz), verts=bm.verts); return bm
    objs.append(place(octa(R8 + .12, .16, lz - .16), 'lant_base', T.MAT['GOLD']))
    objs.append(place(octa(R8, LH, lz), 'lant_vidro', MILK))
    for i in range(8):
        a = (i + .5) / 8 * math.tau
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(.09, .09, LH + .1), verts=bm.verts)
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, 'Z'), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(math.cos(a) * (R8 + .02), math.sin(a) * (R8 + .02), LH / 2), verts=bm.verts)
        objs.append(place(bm, 'lant_barra', T.MAT['GOLD'], lz))
    fw = 2 * R8 * math.sin(math.pi / 8); fr = R8 * math.cos(math.pi / 8) + .03
    L = math.hypot(fw, LH) * .92
    for i in range(8):
        a = i / 8 * math.tau
        for tilt in (math.atan2(fw, LH), -math.atan2(fw, LH)):
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(.06, .06, L), verts=bm.verts)
            bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(tilt, 3, 'X'), verts=bm.verts)
            bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, 'Z'), verts=bm.verts)
            bmesh.ops.translate(bm, vec=(math.cos(a) * fr, math.sin(a) * fr, LH / 2), verts=bm.verts)
            objs.append(place(bm, 'lant_x', T.MAT['GOLD'], lz))
    # tampa: anel de ouro, disco largo claro com aro, cupula de ouro e agulha
    cz = lz + LH
    objs.append(place(octa(R8 + .14, .12, cz), 'tampa_anel', T.MAT['GOLD']))
    objs.append(place(spin([(.95, 0), (1.0, .14), (.92, .26), (.72, .34), (.55, .38)], 24), 'tampa_disco', CREAM, cz + .12))
    objs.append(place(spin([(.98, 0), (1.02, .05), (.98, .1)], 24), 'tampa_aro', T.MAT['GOLD'], cz + .18))
    objs.append(place(spin([(.5, 0), (.52, .1), (.46, .5), (.5, .58), (.28, .7), (.3, .78), (.02, 1.35)], 16), 'cupula', T.MAT['GOLD'], cz + .5))
    return objs

def build_all(positions):
    col = clear('POSTE')
    objs = []
    for i, p in enumerate(positions):
        objs += build_lamp(col, p, f'POSTE{i}')
    return objs
