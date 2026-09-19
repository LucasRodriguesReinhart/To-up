# lvlib.py - nucleo do kit do Lobby V9 (recriacao do lobby de Anime Expeditions).
# Unidades: 1 unidade Blender = 1 stud. Z para cima. -Y = sul (saida p/ Area 1), +Y = norte (Forja).
# Cada objeto exportado leva prefixo de material (TILE__, MARB__, GOLD__, ...) que o script
# do Studio converte em Color/Material/Reflectance do Roblox.
import bpy, bmesh, math, os, random
from mathutils import Matrix, Vector, Euler

ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area"
EXPORT = os.path.join(ROOT, "export")

# ---------------------------------------------------------------- materiais
# nome -> (rgb 0-255, uso). O FBX leva a cor base; o Studio aplica o material Roblox.
MATS = {
    'TILE':  (234, 228, 214),   # piso claro (textura de ladrilho)
    'TILE2': (214, 206, 190),   # piso secundario um tom abaixo
    'STONE': (206, 202, 192),   # blocos de parede (textura de cantaria)
    'MARB':  (238, 233, 222),   # marmore claro liso (balaustres, molduras)
    'MARB2': (198, 196, 190),   # marmore medio (corpo de fachada)
    'TRIM':  (150, 152, 158),   # pedra escura (plintos, contornos)
    'GOLD':  (240, 195, 92),    # dourado (Foil no Studio)
    'BLUE':  (36, 84, 190),     # embutido azul lapis do piso
    'NEON':  (120, 225, 255),   # ciano luminoso (cristais, lanternas)
    'EMBER': (255, 140, 48),    # brasa da forja (Neon laranja)
    'GLASS': (150, 215, 235),   # vidro das cupulas
    'WATER': (66, 190, 220),    # agua dos canais
    'FOAM':  (225, 248, 252),   # espuma / quedas d'agua
    'WOOD':  (98, 68, 42),      # madeira escura (portas)
    'TRUNK': (139, 104, 72),    # troncos
    'LEAF':  (110, 180, 92),    # folhagem (UV aponta pra paleta de copas)
    'GRASS': (118, 196, 96),    # canteiros de grama
    'ROCK':  (132, 136, 142),   # pedras de canal
    'FLOR':  (240, 170, 200),   # flores
    'DARK':  (30, 32, 40),      # interior escuro atras de portas/janelas
    # folhagem: um material por cor (o Studio pinta MeshPart pela cor do material)
    'LEAFAZ':  (86, 170, 225),
    'LEAFAZ2': (64, 146, 208),
    'LEAFCY':  (96, 205, 195),
    'LEAFGD':  (235, 190, 88),
    'LEAFGD2': (222, 168, 66),
    'LEAFLV':  (188, 148, 228),
    'LEAFRS':  (232, 158, 200),
    'LEAFVD':  (108, 182, 90),
    'LEAFVD2': (88, 162, 76),
    'GRAMA':   (118, 196, 96),
    'FLORBR':  (245, 240, 235),
    'FLORRS':  (240, 170, 200),
    'FLORAM':  (245, 210, 110),
}
# swatch antigo -> material
SW2MAT = {'azul': 'LEAFAZ', 'azul2': 'LEAFAZ2', 'ciano': 'LEAFCY', 'dourada': 'LEAFGD',
          'dourada2': 'LEAFGD2', 'lavanda': 'LEAFLV', 'rosa': 'LEAFRS', 'verde': 'LEAFVD',
          'verde2': 'LEAFVD2', 'grama': 'GRAMA', 'flor_br': 'FLORBR', 'flor_rs': 'FLORRS',
          'flor_am': 'FLORAM'}

# paleta de copas: cada arvore usa um swatch (UV constante) na textura LEAF
LEAF_SWATCHES = [
    ('azul',     (86, 170, 225)),
    ('azul2',    (64, 146, 208)),
    ('ciano',    (96, 205, 195)),
    ('dourada',  (235, 190, 88)),
    ('dourada2', (222, 168, 66)),
    ('lavanda',  (188, 148, 228)),
    ('rosa',     (232, 158, 200)),
    ('verde',    (108, 182, 90)),
    ('verde2',   (88, 162, 76)),
    ('grama',    (118, 196, 96)),
    ('flor_br',  (245, 240, 235)),
    ('flor_rs',  (240, 170, 200)),
    ('flor_am',  (245, 210, 110)),
]

def _mat(name):
    m = bpy.data.materials.get('LV_' + name)
    if m is None:
        m = bpy.data.materials.new('LV_' + name)
        m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    rgb = MATS[name]
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (rgb[0]/255, rgb[1]/255, rgb[2]/255, 1)
        bsdf.inputs['Roughness'].default_value = 0.75
    return m

def mat_all():
    return {k: _mat(k) for k in MATS}

# textura de paleta pras copas (16x16 por swatch)
def build_leaf_palette():
    n = len(LEAF_SWATCHES)
    cols = 4
    rows = (n + cols - 1) // cols
    px_sw = 16
    W, H = cols * px_sw, rows * px_sw
    img = bpy.data.images.get('lv_leaf_palette') or bpy.data.images.new('lv_leaf_palette', W, H, alpha=False)
    if img.size[0] != W or img.size[1] != H:
        img.scale(W, H)
    buf = [0.0] * (W * H * 4)
    for i, (_, rgb) in enumerate(LEAF_SWATCHES):
        cx, cy = i % cols, i // cols
        for yy in range(px_sw):
            for xx in range(px_sw):
                X = cx * px_sw + xx
                Y = H - 1 - (cy * px_sw + yy)
                o = (Y * W + X) * 4
                buf[o:o+4] = [rgb[0]/255, rgb[1]/255, rgb[2]/255, 1.0]
    img.pixels = buf
    os.makedirs(EXPORT, exist_ok=True)
    img.filepath_raw = os.path.join(EXPORT, 'lv_leaf_palette.png')
    img.file_format = 'PNG'
    img.save()
    m = bpy.data.materials.get('LV_LEAF')
    if m is None:
        m = _mat('LEAF')
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.get('LeafTex') or nt.nodes.new('ShaderNodeTexImage')
    tex.name = 'LeafTex'
    tex.image = img
    tex.interpolation = 'Closest'
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return img

def leaf_uv(name):
    i = [j for j, (n, _) in enumerate(LEAF_SWATCHES) if n == name][0]
    cols = 4
    rows = (len(LEAF_SWATCHES) + cols - 1) // cols
    cx, cy = i % cols, i // cols
    return ((cx + .5) / cols, 1 - (cy + .5) / rows)

# ---------------------------------------------------------------- texturas procedurais
def _tile_noise(x, y, seed):
    # hash barato e deterministico
    h = math.sin(x * 127.1 + y * 311.7 + seed * 74.7) * 43758.5453
    return h - math.floor(h)

def build_tile_texture():
    """Ladrilho claro estilizado: pedras grandes com variacao suave e juntas finas."""
    S = 256
    img = bpy.data.images.get('lv_tiles') or bpy.data.images.new('lv_tiles', S, S, alpha=False)
    if img.size[0] != S:
        img.scale(S, S)
    base = (233/255, 227/255, 213/255)
    joint = (184/255, 177/255, 162/255)
    buf = [0.0] * (S * S * 4)
    ntile = 4  # 4x4 ladrilhos por textura; UV escala 1 tile = ~8 studs
    tsz = S // ntile
    for ty in range(ntile):
        for tx in range(ntile):
            v = (_tile_noise(tx, ty, 3) - .5) * 0.055
            warm = (_tile_noise(tx, ty, 9) - .5) * 0.03
            col = (min(1, base[0] + v + warm), min(1, base[1] + v + warm * .5), min(1, base[2] + v))
            for yy in range(tsz):
                for xx in range(tsz):
                    X, Y = tx * tsz + xx, ty * tsz + yy
                    edge = min(xx, yy, tsz - 1 - xx, tsz - 1 - yy)
                    grain = (_tile_noise(X // 3, Y // 3, 17) - .5) * 0.028
                    if edge < 2:
                        c = joint
                    elif edge < 4:
                        f = (edge - 2) / 2
                        c = tuple(joint[i] * (1 - f) + col[i] * f for i in range(3))
                    else:
                        c = col
                    o = (Y * S + X) * 4
                    buf[o] = max(0, min(1, c[0] + grain))
                    buf[o+1] = max(0, min(1, c[1] + grain))
                    buf[o+2] = max(0, min(1, c[2] + grain))
                    buf[o+3] = 1.0
    img.pixels = buf
    os.makedirs(EXPORT, exist_ok=True)
    img.filepath_raw = os.path.join(EXPORT, 'lv_tiles.png')
    img.file_format = 'PNG'
    img.save()
    for matname in ('TILE', 'TILE2'):
        m = _mat(matname)
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
        tex = nt.nodes.get('TileTex') or nt.nodes.new('ShaderNodeTexImage')
        tex.name = 'TileTex'
        tex.image = img
        nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return img

def build_stone_texture():
    """Cantaria: fiadas de blocos com juntas horizontais fortes (paredes/fachadas)."""
    S = 256
    img = bpy.data.images.get('lv_stone') or bpy.data.images.new('lv_stone', S, S, alpha=False)
    if img.size[0] != S:
        img.scale(S, S)
    base = (206/255, 202/255, 192/255)
    joint = (168/255, 164/255, 154/255)
    buf = [0.0] * (S * S * 4)
    rows = 6
    rh = S // rows
    for ry in range(rows):
        off = (rh * 2) if ry % 2 else 0
        bw = S // 3
        for yy in range(rh):
            for X in range(S):
                Y = ry * rh + yy
                bx = ((X + off) % S) // bw
                v = (_tile_noise(bx, ry, 5) - .5) * 0.05
                col = tuple(max(0, min(1, c + v)) for c in base)
                exx = (X + off) % bw
                edge = min(yy, rh - 1 - yy, exx, bw - 1 - exx)
                grain = (_tile_noise(X // 2, Y // 2, 23) - .5) * 0.03
                if edge < 2:
                    c = joint
                else:
                    c = col
                o = (Y * S + X) * 4
                buf[o] = max(0, min(1, c[0] + grain))
                buf[o+1] = max(0, min(1, c[1] + grain))
                buf[o+2] = max(0, min(1, c[2] + grain))
                buf[o+3] = 1.0
    img.pixels = buf
    img.filepath_raw = os.path.join(EXPORT, 'lv_stone.png')
    img.file_format = 'PNG'
    img.save()
    m = _mat('STONE')
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nt.nodes.get('StoneTex') or nt.nodes.new('ShaderNodeTexImage')
    tex.name = 'StoneTex'
    tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return img

# ---------------------------------------------------------------- colecoes
def coll(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    elif parent and c.name not in [ch.name for ch in parent.children]:
        try:
            parent.children.link(c)
        except Exception:
            pass
    return c

def clear_collection(c):
    for o in list(c.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for ch in list(c.children):
        clear_collection(ch)
        bpy.data.collections.remove(ch)

# ---------------------------------------------------------------- construcao de malha
class B:
    """Acumulador de bmesh por material. Um objeto final por material."""
    def __init__(self, name, target_coll, mats):
        self.name = name
        self.target = target_coll
        self.mats = mats
        self.groups = {}

    def bm(self, mat):
        if mat not in self.groups:
            self.groups[mat] = bmesh.new()
        return self.groups[mat]

    def add(self, mat, bm_piece, uv=None):
        tmp = bpy.data.meshes.new('tmp')
        bm_piece.to_mesh(tmp)
        bm_piece.free()
        if uv is not None:
            lay = tmp.uv_layers.new(name='UVMap')
            for d in lay.data:
                d.uv = uv
        self.bm(mat).from_mesh(tmp)
        bpy.data.meshes.remove(tmp)

    def finish(self, uv_world=('TILE', 'TILE2', 'STONE'), uv_scale=None):
        """Cria um objeto por material. uv_world: materiais que ganham box-UV em espaco de mundo."""
        uv_scale = uv_scale or {}
        out = []
        for mat, bm in self.groups.items():
            if not bm.faces:
                bm.free()
                continue
            me = bpy.data.meshes.new('%s__%s' % (mat, self.name))
            bm.to_mesh(me)
            bm.free()
            for p in me.polygons:
                p.use_smooth = True
            try:
                me.set_sharp_from_angle(angle=math.radians(42))
            except Exception:
                pass
            me.materials.append(self.mats[mat])
            if mat in uv_world:
                scale = uv_scale.get(mat, 1/32.0)  # 1 repeticao a cada 32 studs (4 ladrilhos de 8)
                lay = me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
                for poly in me.polygons:
                    n = poly.normal
                    ax = 2 if abs(n.z) >= max(abs(n.x), abs(n.y)) else (0 if abs(n.x) > abs(n.y) else 1)
                    for li in poly.loop_indices:
                        co = me.vertices[me.loops[li].vertex_index].co
                        if ax == 2:
                            lay.data[li].uv = (co.x * scale, co.y * scale)
                        elif ax == 0:
                            lay.data[li].uv = (co.y * scale, co.z * scale)
                        else:
                            lay.data[li].uv = (co.x * scale, co.z * scale)
            ob = bpy.data.objects.new('%s__%s' % (mat, self.name), me)
            self.target.objects.link(ob)
            out.append(ob)
        self.groups = {}
        return out

# --------- pecas geometricas (todas devolvem bmesh transformado no lugar) ---------
def _xform(bm, pos=(0, 0, 0), rot=(0, 0, 0), scl=None):
    M = Matrix.Translation(Vector(pos)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()
    if scl:
        M = M @ Matrix.Diagonal((scl[0], scl[1], scl[2], 1))
    bm.transform(M)
    return bm

def box(size, pos=(0, 0, 0), rot=(0, 0, 0), bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    bmesh.ops.scale(bm, vec=(size[0], size[1], size[2]), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=min(bevel, min(size) * .45),
                        segments=1, profile=.7, affect='EDGES')
    return _xform(bm, pos, rot)

def cyl(r, h, pos=(0, 0, 0), rot=(0, 0, 0), seg=16, r2=None, bevel=0.0, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, segments=seg,
                          radius1=r, radius2=r if r2 is None else r2, depth=h)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, profile=.7, affect='EDGES')
    return _xform(bm, (pos[0], pos[1], pos[2] + h / 2), rot)

def ball(r, pos=(0, 0, 0), seg=12, scl=None):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
    if scl:
        bmesh.ops.scale(bm, vec=scl, verts=bm.verts)
    return _xform(bm, pos)

def lathe(profile, pos=(0, 0, 0), seg=20, rot=(0, 0, 0)):
    """Solido de revolucao. profile: [(raio, z), ...] de baixo pra cima."""
    bm = bmesh.new()
    ring_prev = None
    for (r, z) in profile:
        if r <= 0.0005:
            v = bm.verts.new((0, 0, z))
            ring = [v] * seg
        else:
            ring = []
            for i in range(seg):
                a = i / seg * math.tau
                ring.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
        if ring_prev is not None:
            for i in range(seg):
                a, b2 = ring_prev[i], ring_prev[(i + 1) % seg]
                c, d = ring[(i + 1) % seg], ring[i]
                quad = [v for v in (a, b2, c, d)]
                uniq = []
                for v in quad:
                    if v not in uniq:
                        uniq.append(v)
                if len(uniq) >= 3:
                    try:
                        bm.faces.new(uniq)
                    except ValueError:
                        pass
        ring_prev = ring
    # tampas
    bm.verts.ensure_lookup_table()
    if profile[0][0] > 0.0005:
        try:
            bm.faces.new([v for v in bm.verts if abs(v.co.z - profile[0][1]) < 1e-6][:seg][::-1])
        except Exception:
            pass
    if profile[-1][0] > 0.0005:
        try:
            bm.faces.new([v for v in bm.verts if abs(v.co.z - profile[-1][1]) < 1e-6][-seg:])
        except Exception:
            pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    return _xform(bm, pos, rot)

def ngon_prism(points, h, pos=(0, 0, 0), rot=(0, 0, 0)):
    """Prisma extrudado de um poligono 2D (lista de (x,y)), altura h a partir de z=0."""
    bm = bmesh.new()
    bottom = [bm.verts.new((x, y, 0)) for (x, y) in points]
    top = [bm.verts.new((x, y, h)) for (x, y) in points]
    try:
        bm.faces.new(bottom[::-1])
        bm.faces.new(top)
    except ValueError:
        pass
    n = len(points)
    for i in range(n):
        bm.faces.new([bottom[i], bottom[(i + 1) % n], top[(i + 1) % n], top[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _xform(bm, pos, rot)

def ring_prism(pts_out, pts_in, h, pos=(0, 0, 0), rot=(0, 0, 0)):
    """Anel extrudado: poligono externo com furo interno (mesma contagem de pontos)."""
    assert len(pts_out) == len(pts_in)
    n = len(pts_out)
    bm = bmesh.new()
    ob = [bm.verts.new((x, y, 0)) for (x, y) in pts_out]
    ib = [bm.verts.new((x, y, 0)) for (x, y) in pts_in]
    ot = [bm.verts.new((x, y, h)) for (x, y) in pts_out]
    it = [bm.verts.new((x, y, h)) for (x, y) in pts_in]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([ob[i], ob[j], ib[j], ib[i]])          # fundo
        bm.faces.new([ot[j], ot[i], it[i], it[j]][::-1])    # topo
        bm.faces.new([ob[j], ob[i], ot[i], ot[j]])          # lateral externa
        bm.faces.new([ib[i], ib[j], it[j], it[i]])          # lateral interna
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _xform(bm, pos, rot)

def reg_poly(r, sides, rot0=0.0):
    return [(math.cos(i / sides * math.tau + rot0) * r, math.sin(i / sides * math.tau + rot0) * r) for i in range(sides)]

def arch_wall(w, h, arch_r, arch_h, depth, pos=(0, 0, 0), rot=(0, 0, 0), seg=12):
    """Parede com abertura em arco (romana ou ogival conforme arch_h > arch_r).
    Plano XZ (largura X, altura Z), extrudada em Y por depth, centrada em Y."""
    pts = []
    # contorno externo (sentido anti-horario a partir de baixo-esq)
    pts += [(-w/2, 0), (w/2, 0), (w/2, h), (-w/2, h)]
    bm = bmesh.new()
    outer = [bm.verts.new((x, -depth/2, z)) for (x, z) in pts]
    # abertura: costela de arco - construimos a parede como poligono com furo via faces manuais
    # abordagem: dividir a parede em 3 colunas (esq, dir) + verga superior com arco recortado
    bm.free()
    bm = bmesh.new()
    spring = arch_h - arch_r if arch_h > arch_r else arch_h * 0  # altura do pe do arco
    spring = max(0.0, arch_h - arch_r)
    # perfil do furo (meio arco de cada lado)
    hole = [(-arch_r, 0.0)]
    hole += [(-arch_r, spring)]
    for i in range(1, seg):
        a = math.pi * i / seg
        hole.append((-math.cos(a) * arch_r, spring + math.sin(a) * arch_r))
    hole += [(arch_r, spring), (arch_r, 0.0)]
    # face frontal como fan entre contorno externo e furo
    front = []
    outer_pts = [(-w/2, 0), (-w/2, h), (w/2, h), (w/2, 0)]
    loop = outer_pts + hole[::-1]
    vs_f = [bm.verts.new((x, -depth/2, z)) for (x, z) in loop]
    vs_b = [bm.verts.new((x, depth/2, z)) for (x, z) in loop]
    try:
        bm.faces.new(vs_f)
        bm.faces.new(vs_b[::-1])
    except ValueError:
        pass
    n = len(loop)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([vs_f[i], vs_f[j], vs_b[j], vs_b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _xform(bm, pos, rot)

def torus(R, r, pos=(0, 0, 0), rot=(0, 0, 0), seg=20, sides=8, arc=math.tau):
    bm = bmesh.new()
    rings = []
    steps = seg if arc >= math.tau - 1e-4 else seg + 1
    for i in range(steps):
        a = arc * i / seg
        cx, cy = math.cos(a) * R, math.sin(a) * R
        ring = []
        for j in range(sides):
            b2 = j / sides * math.tau
            rr = R + math.cos(b2) * r
            ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, math.sin(b2) * r)))
        rings.append(ring)
    closed = arc >= math.tau - 1e-4
    n = seg if closed else steps - 1
    for i in range(n):
        r1 = rings[i]
        r2 = rings[(i + 1) % steps]
        for j in range(sides):
            bm.faces.new([r1[j], r1[(j + 1) % sides], r2[(j + 1) % sides], r2[j]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _xform(bm, pos, rot)

def puff_cloud(centers, base_r, seed=1, seg=10):
    """Copa organica: esferas achatadas fundidas (sem remesh: barato e estiloso)."""
    rng = random.Random(seed)
    bm = bmesh.new()
    for (cx, cy, cz, rr) in centers:
        b2 = bmesh.new()
        bmesh.ops.create_uvsphere(b2, u_segments=seg, v_segments=max(5, seg // 2), radius=rr)
        bmesh.ops.scale(b2, vec=(1.0, 1.0, rng.uniform(.72, .85)), verts=b2.verts)
        for v in b2.verts:
            v.co.x += (rng.random() - .5) * rr * .16
            v.co.y += (rng.random() - .5) * rr * .16
            v.co.z += (rng.random() - .5) * rr * .1
        _xform(b2, (cx, cy, cz))
        tmp = bpy.data.meshes.new('tmp')
        b2.to_mesh(tmp)
        b2.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    return bm

def stairs(width, run, rise, steps, pos=(0, 0, 0), rot=(0, 0, 0), nosing=.12):
    """Escada solida subindo em +Y a partir de z=0. Cada degrau com beiral fino."""
    bm = bmesh.new()
    for i in range(steps):
        b2 = bmesh.new()
        d = run + (nosing if i < steps else 0)
        bmesh.ops.create_cube(b2, size=1)
        bmesh.ops.scale(b2, vec=(width, d, rise), verts=b2.verts)
        _xform(b2, (0, i * run + run/2, i * rise + rise/2))
        tmp = bpy.data.meshes.new('tmp')
        b2.to_mesh(tmp)
        b2.free()
        bm.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    return _xform(bm, pos, rot)

def merge(*bms):
    out = bmesh.new()
    for bm in bms:
        tmp = bpy.data.meshes.new('tmp')
        bm.to_mesh(tmp)
        bm.free()
        out.from_mesh(tmp)
        bpy.data.meshes.remove(tmp)
    return out
