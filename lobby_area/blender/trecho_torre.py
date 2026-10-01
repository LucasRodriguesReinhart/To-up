# trecho_torre.py - modelagem da BASE da Tower (referencia user_00) para o trecho de amostra.
# Metodo: operacoes de edicao aplicadas peca a peca sobre malhas nomeadas (loop cuts por bisect, extrude/recesso
# de faces selecionadas, cortes booleanos dos vaos, molduras por varredura de perfil desenhado, bevel), com as
# medidas tiradas da correspondencia de camera (refs/match/proxy_04). Nao e um gerador parametrico: cada
# elemento corresponde a um elemento apontavel na referencia.
import bpy, bmesh, math
from mathutils import Vector, Matrix

TERR = 4.5            # topo do terraco (base da fachada)
YF = -32.5            # plano da fachada (normal +Y, camera em +Y)
BW, BD = 28.5, 20.0   # corpo: largura x profundidade
Z_TOP = TERR + 22.0   # topo da amostra (corpo escuro comeca acima do letreiro)
# niveis (absolutos)
Z_PLINTH = TERR + 0.9
Z_CORN1 = TERR + 10.7     # cornija do nivel terreo
Z_CORN1T = Z_CORN1 + 0.9
Z_SIGN_T = TERR + 16.0    # topo da faixa do letreiro
Z_CORN2T = Z_SIGN_T + 0.8
# bays em x (metade direita; espelhado)
X_CENT = 6.5              # meia-largura do bay central
X_PIL1 = 8.1              # pilastra intermediaria 6.5..8.1
X_SIDE = 12.9             # bay lateral 8.1..12.9
X_CORNER = BW / 2         # pilastra de canto 12.9..14.25
# portal (vao interno) e arcos laterais
PORTAL_W, PORTAL_SPRING, PORTAL_APEX = 8.6, TERR + 5.9, TERR + 10.2     # vao interno (apice abaixo da cornija)
SIDE_W, SIDE_SPRING, SIDE_APEX, SIDE_X = 3.0, TERR + 5.5, TERR + 7.0, 10.5

def coll(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c)
    return c

def clear(name):
    c = coll(name)
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    return c

def new_obj(name, bm, col, mat=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    if mat: me.materials.append(mat)
    return o

def M(name, rgb, rough=.8, metal=0.0):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    m.diffuse_color = (*rgb, 1)
    return m

MAT = {
    'STONE': M('T_STONE', (.78, .74, .68)),        # pedra clara do nivel terreo
    'TRIM': M('T_TRIM', (.86, .84, .79)),          # pedra de molduras/pilastras (mais clara)
    'DARK': M('T_DARK', (.36, .30, .25)),          # pedra escura quente do corpo
    'GOLD': M('T_GOLD', (.93, .72, .30), .35, 1.0),
    'GLOW': M('T_GLOW', (1.0, .86, .45), .6),
    'FLOOR': M('T_FLOOR', (.80, .77, .71)),
}

# ---------------------------------------------------------------- utilitarios de modelagem
def bisect(bm, co, no):
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=co, plane_no=no)

def front_faces(bm, y_plane, x0, x1, z0, z1, tol=.05):
    out = []
    for f in bm.faces:
        c = f.calc_center_median()
        if abs(c.y - y_plane) < tol and f.normal.y > .9 and x0 - tol < c.x < x1 + tol and z0 - tol < c.z < z1 + tol:
            out.append(f)
    return out

def extrude_faces(bm, faces, dist):
    """extrude um grupo de faces coplanares ao longo da normal (dist>0 = para fora)."""
    if not faces: return []
    n = faces[0].normal.copy()
    res = bmesh.ops.extrude_face_region(bm, geom=faces)
    vs = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=n * dist, verts=vs)
    bmesh.ops.delete(bm, geom=faces, context='FACES')
    return [g for g in res['geom'] if isinstance(g, bmesh.types.BMFace)]

def arch_outline(w, spring, apex, z0, n=18):
    """contorno (x,z) de um vao em arco: base em z0, arranque em 'spring', apice em 'apex' (arco pleno se apex-spring == w/2)."""
    r = w / 2; k = (apex - spring) / r
    pts = [(-r, z0), (r, z0), (r, spring)]
    for i in range(1, n):
        a = math.pi * i / n
        pts.append((math.cos(a) * r, spring + math.sin(a) * r * k))
    pts.append((-r, spring))
    return pts

def prism_xz(pts, y_front, depth, col, name, mat=None):
    """extrude um poligono (x,z) de y_front para y_front-depth (para dentro)."""
    bm = bmesh.new()
    vs = [bm.verts.new((x, y_front, z)) for x, z in pts]
    f = bm.faces.new(vs)
    res = bmesh.ops.extrude_face_region(bm, geom=[f])
    vs2 = [g for g in res['geom'] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=(0, -depth, 0), verts=vs2)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, col, mat)

def sweep(path, profile, col, name, mat, closed=False):
    """varre um perfil 2D (u,v) ao longo de um caminho 3D. u = para fora (normal do caminho no plano), v = para frente (+Y).
    path: lista de Vector 3D no plano XZ (y constante). O 'para fora' e a normal 2D do caminho no plano XZ."""
    bm = bmesh.new()
    rings = []
    npt = len(path)
    for i, p in enumerate(path):
        p0 = path[max(i - 1, 0)] if not closed else path[i - 1]
        p1 = path[min(i + 1, npt - 1)] if not closed else path[(i + 1) % npt]
        t = (p1 - p0); t.y = 0
        if t.length < 1e-6: t = Vector((0, 0, 1))
        t.normalize()
        nrm = Vector((-t.z, 0, t.x))          # normal no plano XZ (para fora do vao quando o caminho e anti-horario visto de +Y)
        ring = [bm.verts.new(p + nrm * u + Vector((0, v, 0))) for (u, v) in profile]
        rings.append(ring)
    m = len(profile)
    segs = npt if closed else npt - 1
    for i in range(segs):
        r1, r2 = rings[i], rings[(i + 1) % npt]
        for j in range(m - 1):
            bm.faces.new([r1[j], r1[j + 1], r2[j + 1], r2[j]])
    if not closed:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, col, mat)

def arch_path(w, spring, apex, z0, y, n=24, inset=0.0):
    """caminho 3D (Vectors) subindo pela ombreira esquerda, contornando o arco e descendo pela direita (anti-horario visto de +Y)."""
    r = w / 2 + inset; k = (apex - spring) / (w / 2)
    pts = [Vector((-r, y, z0)), Vector((-r, y, spring))]
    for i in range(1, n):
        a = math.pi - math.pi * i / n
        pts.append(Vector((math.cos(a) * r, y, spring + math.sin(a) * r * k)))
    pts += [Vector((r, y, spring)), Vector((r, y, z0))]
    return pts

def apply_boolean(target, cutter):
    mod = target.modifiers.new('cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.object = cutter; mod.solver = 'EXACT'
    with bpy.context.temp_override(object=target, active_object=target, selected_objects=[target]):
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def apply_bevel(obj, width=.08, segments=2, angle=35):
    mod = obj.modifiers.new('bev', 'BEVEL'); mod.width = width; mod.segments = segments; mod.limit_method = 'ANGLE'; mod.angle_limit = math.radians(angle)
    with bpy.context.temp_override(object=obj, active_object=obj, selected_objects=[obj]):
        bpy.ops.object.modifier_apply(modifier=mod.name)

# ---------------------------------------------------------------- TORRE: corpo com relevo
def build_body(col):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(BW, BD, Z_TOP - TERR), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, YF - BD / 2, (TERR + Z_TOP) / 2), verts=bm.verts)
    # loop cuts verticais (bays) e horizontais (niveis) na frente
    for x in (-X_SIDE, -X_PIL1, -X_CENT, X_CENT, X_PIL1, X_SIDE):
        bisect(bm, (x, 0, 0), (1, 0, 0))
    for z in (Z_PLINTH, Z_CORN1 - .8, Z_CORN1, Z_CORN1 + .35, Z_CORN1T, Z_SIGN_T, Z_SIGN_T + .3, Z_CORN2T):
        bisect(bm, (0, 0, z), (0, 0, 1))
    # 1) plinto: faixa inferior para fora
    extrude_faces(bm, front_faces(bm, YF, -BW, BW, TERR, Z_PLINTH), .45)
    # 2) pilastras (canto e intermediarias) para fora, com capitel (faixa Z_CORN1-.8..Z_CORN1) um pouco mais
    for x0, x1 in ((-X_CORNER, -X_SIDE), (-X_PIL1, -X_CENT), (X_CENT, X_PIL1), (X_SIDE, X_CORNER)):
        extrude_faces(bm, front_faces(bm, YF, x0, x1, Z_PLINTH, Z_CORN1 - .8), .55)
        extrude_faces(bm, front_faces(bm, YF, x0, x1, Z_CORN1 - .8, Z_CORN1), .75)
    # 3) bays laterais e central recuados (profundidade do vao)
    extrude_faces(bm, front_faces(bm, YF, -X_SIDE, -X_PIL1, Z_PLINTH, Z_CORN1), -.7)
    extrude_faces(bm, front_faces(bm, YF, X_PIL1, X_SIDE, Z_PLINTH, Z_CORN1), -.7)
    extrude_faces(bm, front_faces(bm, YF, -X_CENT, X_CENT, Z_PLINTH, Z_CORN1), -.9)
    # 4) faixa da cornija 1: sai .35 (a moldura com perfil e varrida a parte, em build_moldings)
    extrude_faces(bm, front_faces(bm, YF, -BW, BW, Z_CORN1, Z_CORN1T), .35)
    # 5) faixa do letreiro levemente recuada; faixa da cornija 2 sai .3 (perfil varrido a parte)
    extrude_faces(bm, front_faces(bm, YF, -BW, BW, Z_CORN1T, Z_SIGN_T), -.3)
    extrude_faces(bm, front_faces(bm, YF, -BW, BW, Z_SIGN_T, Z_CORN2T), .3)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = new_obj('TORRE_corpo', bm, col, MAT['STONE'])
    # materiais por zona: escuro acima da cornija 2, molduras claras nas pilastras/cornijas
    me = body.data
    me.materials.append(MAT['TRIM']); me.materials.append(MAT['DARK'])
    for p in me.polygons:
        c = p.center
        if c.z > Z_CORN2T - .01: p.material_index = 2
        elif (Z_CORN1 - .01 < c.z < Z_CORN1T + .01) or (Z_SIGN_T - .01 < c.z < Z_CORN2T + .01) or c.z < Z_PLINTH + .01: p.material_index = 1
        elif c.y > YF + .3 and c.z < Z_CORN1: p.material_index = 1        # pilastras salientes
    # cortes dos vaos (booleanos) - portal profundo e nichos laterais
    cut = prism_xz(arch_outline(PORTAL_W, PORTAL_SPRING, PORTAL_APEX, TERR - .5), YF + 2, 8.0, col, 'cut_portal')
    apply_boolean(body, cut)
    for s in (-1, 1):
        pts = [(x + s * SIDE_X, z) for x, z in arch_outline(SIDE_W, SIDE_SPRING, SIDE_APEX, TERR + 1.2)]
        cut = prism_xz(pts, YF + 2, 2.0 + 2.2, col, 'cut_side')
        apply_boolean(body, cut)
    apply_bevel(body, .07, 2, 40)
    return body

def hsweep(x0, x1, y, z, profile, col, name, mat, wrap=0.0):
    """molding horizontal ao longo da frente (de x0 a x1 no plano y), com retornos de comprimento 'wrap' nas
    laterais. profile: (u = para fora em +Y, v = para cima)."""
    pts = []
    if wrap > 0:
        pts.append(Vector((x0, y - wrap, z)))
    pts += [Vector((x0, y, z)), Vector((x1, y, z))]
    if wrap > 0:
        pts.append(Vector((x1, y - wrap, z)))
    # sweep() usa u = normal 2D no plano XZ do caminho: para um caminho horizontal em X a normal aponta em Z.
    # aqui queremos u->+Y e v->+Z: construimos direto.
    bm = bmesh.new(); rings = []
    for i, p in enumerate(pts):
        p0 = pts[max(i - 1, 0)]; p1 = pts[min(i + 1, len(pts) - 1)]
        t = (p1 - p0); t.normalize()
        out = Vector((t.y, -t.x, 0))       # normal horizontal a direita do caminho... escolhida para apontar para +Y na frente
        if out.y < 0: out = -out
        if abs(t.y) > .9: out = Vector((1 if p.x > 0 else -1, 0, 0))   # retornos laterais: para fora em X
        rings.append([bm.verts.new(p + out * u + Vector((0, 0, v))) for (u, v) in profile])
    m = len(profile)
    for i in range(len(pts) - 1):
        for j in range(m - 1):
            bm.faces.new([rings[i][j], rings[i][j + 1], rings[i + 1][j + 1], rings[i + 1][j]])
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return new_obj(name, bm, col, mat)

def build_moldings(col):
    """cornijas com perfil (cima reversa + filete + dentado simplificado), capiteis e bases das pilastras,
    filetes dourados nas arestas das pilastras. Tudo varrido a partir de perfis desenhados."""
    objs = []
    # perfil de cornija (u para fora, v para cima) - cyma recta sobre filete sobre gola
    cyma = [(0, 0), (.15, 0), (.15, .12), (.45, .2), (.55, .32), (.72, .5), (.95, .62), (1.15, .72), (1.15, .85), (0, .85)]
    yfront = YF + .35
    objs.append(hsweep(-BW / 2 - .1, BW / 2 + .1, yfront, Z_CORN1T - .85, cyma, col, 'CORNIJA1', MAT['TRIM'], wrap=BD))
    objs.append(hsweep(-BW / 2 - .1, BW / 2 + .1, YF + .3, Z_CORN2T - .85, [(u * .8, v * .9) for u, v in cyma], col, 'CORNIJA2', MAT['TRIM'], wrap=BD))
    # friso dourado sob a cornija 1 e sobre a faixa do letreiro
    band = [(0, 0), (.12, 0), (.12, .22), (0, .22)]
    objs.append(hsweep(-BW / 2, BW / 2, yfront + .01, Z_CORN1 + .05, band, col, 'FRISO_OURO1', MAT['GOLD'], wrap=BD))
    objs.append(hsweep(-BW / 2, BW / 2, YF + .3 + .01, Z_SIGN_T + .08, band, col, 'FRISO_OURO2', MAT['GOLD'], wrap=BD))
    # cordao/cimalha do plinto
    plinth_prof = [(0, 0), (.3, 0), (.3, .18), (.18, .3), (.06, .42), (0, .5)]
    objs.append(hsweep(-BW / 2 - .45, BW / 2 + .45, YF + .45, Z_PLINTH, plinth_prof, col, 'PLINTO_cimalha', MAT['TRIM'], wrap=BD))
    # capiteis das pilastras: abaco + equino (perfil) envolvendo as 3 faces expostas
    cap_prof = [(0, 0), (.1, 0), (.22, .18), (.36, .4), (.42, .62), (.42, .8), (0, .8)]
    base_prof = [(0, 0), (.32, 0), (.32, .16), (.2, .3), (.1, .5), (0, .6)]
    for x0, x1, yfp in ((-X_CORNER, -X_SIDE, YF + .55), (-X_PIL1, -X_CENT, YF + .55), (X_CENT, X_PIL1, YF + .55), (X_SIDE, X_CORNER, YF + .55)):
        cx = (x0 + x1) / 2; hw = (x1 - x0) / 2
        # caminho retangular em torno da pilastra (frente + 2 lados), aberto atras
        for prof, z, nm in ((cap_prof, Z_CORN1 - .8 - .8, 'CAPITEL'), (base_prof, Z_PLINTH, 'BASE_PIL')):
            pts = [Vector((cx - hw - .02, YF - .2, z)), Vector((cx - hw - .02, yfp, z)), Vector((cx + hw + .02, yfp, z)), Vector((cx + hw + .02, YF - .2, z))]
            bm = bmesh.new(); rings = []
            for i, p in enumerate(pts):
                # normal para fora do retangulo: lados -> +-X, frente -> +Y
                if i == 0: n = Vector((-1, 0, 0)); n2 = Vector((0, 0, 0))
                if i in (1, 2):
                    nx = -1 if i == 1 else 1
                    ring = [bm.verts.new(p + Vector((nx * u, u, v))) for (u, v) in prof]
                else:
                    nx = -1 if i == 0 else 1
                    ring = [bm.verts.new(p + Vector((nx * u, 0, v))) for (u, v) in prof]
                rings.append(ring)
            m = len(prof)
            for i in range(3):
                for j in range(m - 1):
                    bm.faces.new([rings[i][j], rings[i][j + 1], rings[i + 1][j + 1], rings[i + 1][j]])
            bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            objs.append(new_obj(nm, bm, col, MAT['TRIM']))
        # filete dourado vertical nas duas arestas frontais da pilastra (ref: pilastras com bordas douradas)
        for xe in (x0 + .12, x1 - .12):
            bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(.16, .12, Z_CORN1 - 1.6 - Z_PLINTH - .6), verts=bm.verts)
            bmesh.ops.translate(bm, vec=(xe, yfp + .04, (Z_CORN1 - 1.6 + Z_PLINTH + .6) / 2), verts=bm.verts)
            objs.append(new_obj('FILETE_OURO_PIL', bm, col, MAT['GOLD']))
    return objs

# ---------------------------------------------------------------- PORTAL: molduras douradas, tracaria, fundo luminoso
def build_portal(col):
    objs = []
    yf = YF - .9 + .02          # plano do bay central recuado
    # perfil de moldura (u para fora do vao, v para frente): ogiva/cima com filetes (desenhado)
    prof_gold = [(0.0, 0.0), (0.0, .28), (.12, .40), (.30, .46), (.55, .46), (.70, .34), (.80, .18), (.95, .12), (1.10, .12), (1.10, 0.0)]
    prof_fillet = [(0.0, 0.0), (0.0, .16), (.28, .22), (.42, .16), (.42, 0.0)]
    # portal: filete de pedra clara junto ao vao + moldura dourada larga por fora + segundo anel dourado fino
    p = arch_path(PORTAL_W, PORTAL_SPRING, PORTAL_APEX, TERR, yf)
    objs.append(sweep(p, prof_fillet, col, 'PORTAL_filete', MAT['TRIM']))
    p2 = arch_path(PORTAL_W, PORTAL_SPRING, PORTAL_APEX, TERR, yf, inset=.42)
    objs.append(sweep(p2, prof_gold, col, 'PORTAL_moldura_ouro', MAT['GOLD']))
    p3 = arch_path(PORTAL_W, PORTAL_SPRING, PORTAL_APEX, TERR, yf, inset=1.75)
    objs.append(sweep(p3, [(0, 0), (0, .2), (.2, .3), (.4, .2), (.4, 0)], col, 'PORTAL_anel_ext', MAT['GOLD']))
    # base das ombreiras (plintos das molduras)
    for s in (-1, 1):
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(2.6, 1.2, 1.1), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(s * (PORTAL_W / 2 + 1.05), yf + .35, TERR + .55), verts=bm.verts)
        o = new_obj('PORTAL_plinto', bm, col, MAT['TRIM']); apply_bevel(o, .06, 2); objs.append(o)
    # tracaria dourada dentro do vao: maineis, travessa, arquinhos e roseta (barras varridas)
    yt = yf - 1.4
    bar = [(-.09, -.09), (-.09, .09), (.09, .09), (.09, -.09)]
    def bar_path(pts):
        return [Vector((x, yt, z)) for x, z in pts]
    # 5 maineis (4 luzes) + 3 travessas + arquinhos ogivais em cada luz + tracaria fina (losangos) na faixa superior
    xs = [-3.2, -1.6, 0.0, 1.6, 3.2]
    for x in xs:
        objs.append(sweep(bar_path([(x, TERR), (x, PORTAL_SPRING + .9)]), bar, col, 'TRAC_mainel', MAT['GOLD']))
    for zz in (TERR + 2.2, TERR + 4.4, PORTAL_SPRING + .9):
        objs.append(sweep(bar_path([(-PORTAL_W / 2, zz), (PORTAL_W / 2, zz)]), bar, col, 'TRAC_travessa', MAT['GOLD']))
    thin = [(-.06, -.06), (-.06, .06), (.06, .06), (.06, -.06)]
    for cx in (-2.4, -0.8, 0.8, 2.4):
        w = 1.6; sp = PORTAL_SPRING + .9
        pts = [(cx - w / 2, sp)]
        for i in range(1, 10):
            a = math.pi - math.pi * i / 10
            pts.append((cx + math.cos(a) * w / 2, sp + math.sin(a) * w / 2 * 1.3))
        pts.append((cx + w / 2, sp))
        objs.append(sweep(bar_path(pts), thin, col, 'TRAC_arquinho', MAT['GOLD']))
        # losangos entre as travessas (padrao fino da referencia)
        for zz in (TERR + 3.3, TERR + 5.5):
            d = [(cx, zz + .7), (cx + .6, zz), (cx, zz - .7), (cx - .6, zz), (cx, zz + .7)]
            objs.append(sweep(bar_path(d), [(-.045, -.045), (-.045, .045), (.045, .045), (.045, -.045)], col, 'TRAC_losango', MAT['GOLD']))
    # roseta: anel + 4 folhas (anel varrido)
    rc = (0.0, PORTAL_SPRING + 2.6); rr = 1.0
    ring = [(rc[0] + math.cos(a) * rr, rc[1] + math.sin(a) * rr) for a in [i / 20 * math.tau for i in range(21)]]
    objs.append(sweep(bar_path(ring), bar, col, 'TRAC_roseta', MAT['GOLD']))
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        small = [(rc[0] + math.cos(a) * .6 + math.cos(b) * .38, rc[1] + math.sin(a) * .6 + math.sin(b) * .38) for b in [i / 12 * math.tau for i in range(13)]]
        objs.append(sweep(bar_path(small), [(-.06, -.06), (-.06, .06), (.06, .06), (.06, -.06)], col, 'TRAC_folha', MAT['GOLD']))
    # fundo luminoso do portal (painel ao fundo do vao) e piso do vao
    pts = arch_outline(PORTAL_W + .4, PORTAL_SPRING, PORTAL_APEX + .2, TERR - .2)
    objs.append(prism_xz(pts, yf - 5.4, .3, col, 'PORTAL_fundo_luz', MAT['GLOW']))   # dentro da profundidade do corte (8 a partir de YF+2)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(PORTAL_W + .6, 7.2, .4), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, yf - 3.4, TERR - .2), verts=bm.verts); objs.append(new_obj('PORTAL_piso', bm, col, MAT['FLOOR']))
    # arcos laterais: filete + moldura dourada (mesmos perfis, escala menor) e fundo luminoso
    for s in (-1, 1):
        ys = YF - .7 + .02
        pth = [Vector((v.x + s * SIDE_X, v.y, v.z)) for v in arch_path(SIDE_W, SIDE_SPRING, SIDE_APEX, TERR + 1.2, ys)]
        objs.append(sweep(pth, [(u * .7, v * .8) for u, v in prof_fillet], col, 'LAT_filete', MAT['TRIM']))
        pth2 = [Vector((v.x + s * SIDE_X, v.y, v.z)) for v in arch_path(SIDE_W, SIDE_SPRING, SIDE_APEX, TERR + 1.2, ys, inset=.3)]
        objs.append(sweep(pth2, [(u * .62, v * .85) for u, v in prof_gold], col, 'LAT_moldura_ouro', MAT['GOLD']))
        # peitoril
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(SIDE_W + 1.6, .9, .4), verts=bm.verts)
        bmesh.ops.translate(bm, vec=(s * SIDE_X, ys + .3, TERR + 1.0), verts=bm.verts); o = new_obj('LAT_peitoril', bm, col, MAT['TRIM']); apply_bevel(o, .05, 2); objs.append(o)
        # tracaria simples (mainel + arquinho) e fundo luminoso
        yt2 = ys - 1.0
        objs.append(sweep([Vector((s * SIDE_X, yt2, TERR + 1.2)), Vector((s * SIDE_X, yt2, SIDE_SPRING + .6))], [(-.07, -.07), (-.07, .07), (.07, .07), (.07, -.07)], col, 'LAT_mainel', MAT['GOLD']))
        pts = [(x + s * SIDE_X, z) for x, z in arch_outline(SIDE_W + .3, SIDE_SPRING, SIDE_APEX + .1, TERR + 1.0)]
        objs.append(prism_xz(pts, ys - 4.0, .3, col, 'LAT_fundo_luz', MAT['GLOW']))
    return objs

# ---------------------------------------------------------------- LETREIRO: suportes em voluta + placa (sem texto por enquanto)
def build_sign(col):
    objs = []
    yb = YF - .3 + .02                     # plano da faixa do letreiro
    zc = (Z_CORN1T + Z_SIGN_T) / 2 + .2    # centro vertical da placa
    # placa dourada com moldura (placeholder da identificacao)
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(13.5, .35, 3.6), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, yb + .25, zc), verts=bm.verts); o = new_obj('SIGN_placa', bm, col, MAT['GOLD']); apply_bevel(o, .1, 3); objs.append(o)
    # volutas de suporte (S) varridas, uma de cada lado, apoiadas na cornija 1
    prof = [(-.22, -.18), (-.22, .18), (.22, .18), (.22, -.18)]
    for s in (-1, 1):
        pts = []
        for i in range(25):
            t = i / 24
            a = -math.pi / 2 + t * math.pi * 1.6
            r = 1.6 - t * .9
            pts.append(Vector((s * (7.4 + math.cos(a) * r), yb + .5, Z_CORN1T + .9 + math.sin(a) * r + t * .5)))
        objs.append(sweep(pts, prof, col, 'SIGN_voluta', MAT['GOLD']))
    return objs

def split_by_material(obj, col):
    """o importador do Roblox funde materiais: separa o objeto em um por material (mantendo nomes por zona)."""
    me = obj.data
    names = {0: 'TORRE_corpo_pedra', 1: 'TORRE_corpo_moldura', 2: 'TORRE_corpo_escuro'}
    out = []
    for mi, mat in enumerate(me.materials):
        bm = bmesh.new(); bm.from_mesh(me)
        kill = [f for f in bm.faces if f.material_index != mi]
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        if not bm.faces:
            bm.free(); continue
        for f in bm.faces: f.material_index = 0
        m2 = bpy.data.meshes.new(names.get(mi, obj.name + str(mi))); bm.to_mesh(m2); bm.free()
        m2.materials.append(mat)
        for p in m2.polygons: p.use_smooth = False
        o2 = bpy.data.objects.new(names.get(mi, obj.name + str(mi)), m2); col.objects.link(o2); out.append(o2)
    bpy.data.objects.remove(obj, do_unlink=True)
    return out

def build_all():
    col = clear('TORRE'); colp = clear('PORTAL')
    body = build_body(col)
    parts = split_by_material(body, col)
    build_moldings(col)
    build_portal(colp)
    build_sign(colp)
    return parts
