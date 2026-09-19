# trecho_escada.py - escadaria, terraco, bochechas com coping, pedestais (referencia user_00 / ref_tower_base).
# Escada por perfil lateral extrudado (12 degraus), beirais por bevel; bochecha por perfil + coping varrido.
import bpy, bmesh, math
from mathutils import Vector
import trecho_torre as T
from trecho_torre import new_obj, clear, MAT, apply_bevel, hsweep

TERR, YF = T.TERR, T.YF
Y_SB, Y_ST = -19.5, -27.5      # pe e topo da escada
SW = 18.0                       # largura
N = 12

def build_stairs(col):
    objs = []
    rise = TERR / N; run = (Y_ST - Y_SB) / N   # run negativo (sobe para -Y)
    # perfil lateral (y,z) da escada, extrudado em X
    prof = [(Y_SB, 0.0)]
    for i in range(N):
        y0 = Y_SB + i * run; y1 = Y_SB + (i + 1) * run
        prof.append((y0, (i + 1) * rise)); prof.append((y1, (i + 1) * rise))
    prof += [(Y_ST - 1.0, TERR), (Y_ST - 1.0, -0.6), (Y_SB, -0.6)]
    bm = bmesh.new()
    vs = [bm.verts.new((-SW / 2, y, z)) for y, z in prof]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(SW, 0, 0), verts=[g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    st = new_obj('ESCADA_degraus', bm, col, MAT['FLOOR']); apply_bevel(st, .06, 2, 60); objs.append(st)
    # beiral (nosing) de cada degrau: barra fina saliente
    for i in range(N):
        y = Y_SB + (i + 1) * run; z = (i + 1) * rise
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(SW, .22, .14), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(0, y + .1, z - .07), verts=bm.verts)
        objs.append(new_obj('ESCADA_beiral', bm, col, MAT['TRIM']))
    # bochechas: bloco inclinado (perfil y,z) + coping varrido no topo, com bloco de arranque no pe e no topo
    for s in (-1, 1):
        xc = s * (SW / 2 + .9)
        pr = [(Y_SB + .2, -0.6), (Y_ST - 1.0, -0.6), (Y_ST - 1.0, TERR + 1.1), (Y_SB + .2, 1.1)]
        bm = bmesh.new(); vs = [bm.verts.new((xc - .9, y, z)) for y, z in pr]; f = bm.faces.new(vs)
        res = bmesh.ops.extrude_face_region(bm, geom=[f])
        bmesh.ops.translate(bm, vec=(1.8, 0, 0), verts=[g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        o = new_obj('ESCADA_bochecha', bm, col, MAT['STONE']); apply_bevel(o, .05, 2, 60); objs.append(o)
        # coping inclinado (perfil arredondado) varrido ao longo do topo
        p0 = Vector((xc, Y_SB + .2, 1.1)); p1 = Vector((xc, Y_ST - 1.0, TERR + 1.1))
        d = (p1 - p0).normalized(); up = Vector((0, 0, 1)); side = Vector((1, 0, 0))
        cop = [(-1.1, 0), (-1.1, .25), (-.95, .45), (-.6, .58), (0, .62), (.6, .58), (.95, .45), (1.1, .25), (1.1, 0)]
        bm = bmesh.new(); rings = []
        for p in (p0 - d * .3, p1 + d * .3):
            rings.append([bm.verts.new(p + side * u + up * v) for (u, v) in cop])
        for j in range(len(cop) - 1):
            bm.faces.new([rings[0][j], rings[0][j + 1], rings[1][j + 1], rings[1][j]])
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        objs.append(new_obj('ESCADA_coping', bm, col, MAT['TRIM']))
        # pedestal do pe (planter) e pedestal do topo (poste)
        for (yp, zb, w, h, nm) in ((Y_SB + 1.4, 0.0, 2.6, 1.9, 'PEDESTAL_pe'), (Y_ST - 1.0, TERR, 2.2, 1.3, 'PEDESTAL_topo')):
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(w, w, h), verts=bm.verts)
            bmesh.ops.translate(bm, vec=(s * (SW / 2 + 1.6), yp, zb + h / 2), verts=bm.verts)
            o = new_obj(nm, bm, col, MAT['STONE']); apply_bevel(o, .06, 2); objs.append(o)
            # cimalha do pedestal (perfil em volta das 4 faces)
            capp = [(0, 0), (.22, 0), (.22, .1), (.12, .22), (.04, .34), (0, .4)]
            cx, cy = s * (SW / 2 + 1.6), yp
            pts = [Vector((cx - w / 2, cy - w / 2, zb + h - .4)), Vector((cx + w / 2, cy - w / 2, zb + h - .4)), Vector((cx + w / 2, cy + w / 2, zb + h - .4)), Vector((cx - w / 2, cy + w / 2, zb + h - .4))]
            bm = bmesh.new(); rings = []
            nrm = [Vector((-1, -1, 0)).normalized(), Vector((1, -1, 0)).normalized(), Vector((1, 1, 0)).normalized(), Vector((-1, 1, 0)).normalized()]
            for p, n in zip(pts, nrm):
                rings.append([bm.verts.new(p + n * (u * 1.414) + Vector((0, 0, v))) for (u, v) in capp])
            for i in range(4):
                r1, r2 = rings[i], rings[(i + 1) % 4]
                for j in range(len(capp) - 1):
                    bm.faces.new([r1[j], r1[j + 1], r2[j + 1], r2[j]])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            objs.append(new_obj(nm + '_cimalha', bm, col, MAT['TRIM']))
    # terraco: laje entre a escada e a fachada (largura 56), com borda moldada na frente fora da escada
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(56, YF - Y_ST + 1.0 if False else (Y_ST - YF) + 1.0, TERR + .6), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, (YF + Y_ST) / 2 - .5, (TERR - .6) / 2), verts=bm.verts)
    objs.append(new_obj('TERRACO', bm, col, MAT['FLOOR']))
    for s in (-1, 1):
        x0, x1 = s * (SW / 2 + 1.8), s * 28.0
        objs.append(hsweep(min(x0, x1), max(x0, x1), Y_ST - 1.0, TERR - .5, [(0, 0), (.35, 0), (.35, .2), (.2, .35), (.08, .5), (0, .55)], col, 'TERRACO_cimalha', MAT['TRIM']))
    return objs

def build_all():
    col = clear('ESCADA')
    return build_stairs(col)
