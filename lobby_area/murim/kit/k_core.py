# k_core.py - nucleo de modelagem do KIT "Seita da Forja Celeste" (Blender 5.x, via MCP).
# Cada peca do kit e um Builder: varias partes (cada uma com sua "tinta") acumuladas em UMA malha. A forma de cada
# parte e desenhada a mao (perfis, poligonos, caminhos); o codigo so extruda/torneia/varre/chanfra e repete.
# Unidades = studs. Eixos Blender: X fachada, Y profundidade (frente = -Y), Z cima.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

PAINTS = {   # tinta -> cor de viewport (sRGB hex). Os shaders pintados ficam em k_materiais.
    'verm': 'B8321E', 'vermS': '7E2014', 'ouro': 'E0A83A', 'bronze': '8C6A2E', 'mad': '4A2E1E', 'madM': '7A4B2A',
    'pedra': 'DCCDB0', 'piso': 'B9AD95', 'junta': '8F846E', 'telha': '2E5A4C', 'telhaImp': 'D4A034', 'jade': '3E7D6E',
    'jadeE': '2E5A4C', 'creme': 'F1E3C0', 'ferro': '2B2624', 'chama': 'FFC84A', 'pinho': '3E6B3A', 'folha': '6E9A45',
    'casca': '5A3F2A', 'bordo': 'C4432B', 'tecido': 'A8261A', 'corte': '1E1A18',
    'aco': 'C9D0D8',
}

def hex_lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)

def paint_mat(key):
    name = 'P_' + key
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name); m.diffuse_color = (*hex_lin(PAINTS[key]), 1)
        m.use_nodes = True
        b = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if b: b.inputs['Base Color'].default_value = (*hex_lin(PAINTS[key]), 1); b.inputs['Roughness'].default_value = .8
    return m

def col(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name); (parent or bpy.context.scene.collection).children.link(c)
    return c

def clear_col(name):
    c = bpy.data.collections.get(name)
    if c:
        for o in list(c.objects):
            me = o.data; bpy.data.objects.remove(o, do_unlink=True)
            if me and me.users == 0: bpy.data.meshes.remove(me)
    return col(name)

def ctx():
    # em segundo plano (blender -b) nao ha janelas: o override vazio basta, os operadores usam a view layer ativa
    if not bpy.context.window_manager.windows: return {}
    win = bpy.context.window_manager.windows[0]; scr = win.screen
    area = next((a for a in scr.areas if a.type == 'VIEW_3D'), scr.areas[0]); region = next(r for r in area.regions if r.type == 'WINDOW')
    return dict(window=win, screen=scr, area=area, region=region)

# ------------------------------------------------------------------ primitivas desenhadas (retornam bmesh temporario)
def bevel_sharp(bm, w, seg=2, angle=0.55, profile=0.7):
    """chanfra so as arestas vivas (angulo entre faces > angle); nao toca em arestas coplanares nem de borda."""
    if w <= 0: return
    es = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > angle]
    if es: bmesh.ops.bevel(bm, geom=es, offset=w, segments=seg, profile=profile, affect='EDGES', clamp_overlap=True)

def t_box(x0, x1, y0, y1, z0, z1, bev=0.0, seg=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(x1 - x0, y1 - y0, z1 - z0), verts=bm.verts)
    bmesh.ops.translate(bm, vec=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), verts=bm.verts)
    bevel_sharp(bm, bev, seg); return bm

def t_prism(poly, axis, t0, t1, bev=0.0, seg=2):
    """poligono 2D (lista de (a,b), anti-horario) extrudado ao longo de axis entre t0 e t1.
    axis 'Y': (a,b)=(x,z); axis 'X': (a,b)=(y,z); axis 'Z': (a,b)=(x,y)."""
    bm = bmesh.new()
    def P(a, b, t):
        return {'Y': (a, t, b), 'X': (t, a, b), 'Z': (a, b, t)}[axis]
    v0 = [bm.verts.new(P(a, b, t0)) for a, b in poly]; v1 = [bm.verts.new(P(a, b, t1)) for a, b in poly]
    n = len(poly)
    bm.faces.new(v0[::-1]); bm.faces.new(v1)
    for i in range(n): bm.faces.new((v0[i], v0[(i + 1) % n], v1[(i + 1) % n], v1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bevel_sharp(bm, bev, seg); return bm

def t_lathe(profile, seg=24, smooth=True):
    """torneia perfil [(r,z)...] em torno de Z."""
    bm = bmesh.new(); rings = []
    for r, z in profile:
        if r < 1e-4: v = bm.verts.new((0, 0, z)); rings.append([v] * seg)
        else: rings.append([bm.verts.new((math.cos(i / seg * math.tau) * r, math.sin(i / seg * math.tau) * r, z)) for i in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg):
            q = []
            for v in (a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]):
                if v not in q: q.append(v)
            if len(q) >= 3:
                try: bm.faces.new(q)
                except ValueError: pass
    for ring, rev in ((rings[0], True), (rings[-1], False)):
        if len(set(ring)) > 2:
            try: bm.faces.new(ring[::-1] if rev else ring)
            except ValueError: pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces: f.smooth = True
    return bm

def t_sweep(profile, path, closed=False, up=Vector((0, 0, 1)), cap=True, smooth=False):
    """varre perfil [(u,v)...] (u = para fora/direita do caminho, v = para cima) ao longo de path (lista de Vector),
    com esquadria (miter) nos cantos. O perfil deve ser um poligono fechado anti-horario olhando no sentido do caminho."""
    bm = bmesh.new(); n = len(path); rings = []
    for i, p in enumerate(path):
        if closed: a, b = path[(i - 1) % n], path[(i + 1) % n]
        else: a, b = path[max(i - 1, 0)], path[min(i + 1, n - 1)]
        d0 = (p - a).normalized() if (p - a).length > 1e-6 else None
        d1 = (b - p).normalized() if (b - p).length > 1e-6 else None
        if d0 is None: d0 = d1
        if d1 is None: d1 = d0
        t = (d0 + d1); t = t.normalized() if t.length > 1e-6 else d1
        side = t.cross(up).normalized()                    # direita do caminho
        cosh = max(0.2, side.dot(d1.cross(up).normalized()))
        upv = side.cross(t).normalized()
        rings.append([bm.verts.new(p + side * (u / cosh) + upv * v) for u, v in profile])
    m = len(profile)
    segs = range(n) if closed else range(n - 1)
    for i in segs:
        a, b = rings[i], rings[(i + 1) % n]
        for j in range(m): bm.faces.new((a[j], a[(j + 1) % m], b[(j + 1) % m], b[j]))
    if cap and not closed:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces: f.smooth = True
    return bm

def t_tube(pts, radii, seg=10, cap=True, smooth=True):
    bm = bmesh.new(); rings = []; prev_n1 = None
    for i, p in enumerate(pts):
        t = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        ref = prev_n1 if prev_n1 is not None else (Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((0, 1, 0)))
        n1 = (ref - t * ref.dot(t)).normalized(); n2 = t.cross(n1).normalized(); prev_n1 = n1
        rings.append([bm.verts.new(p + (n1 * math.cos(a / seg * math.tau) + n2 * math.sin(a / seg * math.tau)) * radii[i]) for a in range(seg)])
    for a, b in zip(rings, rings[1:]):
        for i in range(seg): bm.faces.new((a[i], a[(i + 1) % seg], b[(i + 1) % seg], b[i]))
    if cap:
        bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces: f.smooth = True
    return bm

def t_blob(r, scale=(1, 1, 1), sub=2, lobes=0, lobe_amp=0.0, seed=0, flat_bottom=None):
    """massa organica: icoesfera escalada com lobos radiais (copas, arbustos, corpos de bichos)."""
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    rnd = random.Random(seed); ph = [rnd.uniform(0, math.tau) for _ in range(3)]
    for v in bm.verts:
        d = v.co.normalized(); a = math.atan2(d.y, d.x)
        k = 1.0
        if lobes: k += lobe_amp * (0.6 * math.sin(lobes * a + ph[0]) + 0.4 * math.sin((lobes + 2) * a + ph[1] + d.z * 2.0)) * (1 - abs(d.z) * 0.6)
        v.co = Vector((d.x * r * k * scale[0], d.y * r * k * scale[1], d.z * r * scale[2]))
        if flat_bottom is not None and v.co.z < flat_bottom: v.co.z = flat_bottom + (v.co.z - flat_bottom) * 0.25
    for f in bm.faces: f.smooth = True
    return bm

def xf(bm, M=None, loc=None, rot=None, scale=None):
    """transforma bmesh temporario: scale -> rot (euler XYZ em graus ou Matrix) -> loc, ou matriz M."""
    if scale is not None: bmesh.ops.scale(bm, vec=scale if hasattr(scale, '__len__') else (scale,) * 3, verts=bm.verts)
    if rot is not None:
        R = rot if isinstance(rot, Matrix) else (Matrix.Rotation(math.radians(rot[2]), 3, 'Z') @ Matrix.Rotation(math.radians(rot[1]), 3, 'Y') @ Matrix.Rotation(math.radians(rot[0]), 3, 'X'))
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=R, verts=bm.verts)
    if loc is not None: bmesh.ops.translate(bm, vec=loc, verts=bm.verts)
    if M is not None: bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return bm

def mirror_x(bm):
    bmesh.ops.scale(bm, vec=(-1, 1, 1), verts=bm.verts); bmesh.ops.reverse_faces(bm, faces=bm.faces); return bm

# ------------------------------------------------------------------ Builder: uma peca do kit
class Builder:
    def __init__(self, name, seed=0):
        self.name = name; self.bm = bmesh.new(); self.keys = []; self.rnd = random.Random(seed)
        self.lay = self.bm.loops.layers.color.new('rnd')
    def slot(self, key):
        if key not in self.keys: self.keys.append(key)
        return self.keys.index(key)
    def add(self, tbm, key, rnd=None):
        """funde um bmesh temporario na peca, com a tinta `key`. rnd = valor de variacao (0..1) desta parte."""
        s = self.slot(key); r = self.rnd.random() if rnd is None else rnd
        lay = tbm.loops.layers.color.get('rnd') or tbm.loops.layers.color.new('rnd')
        for f in tbm.faces:
            f.material_index = s
            if rnd != 'keep':
                for l in f.loops: l[lay] = (r, r, r, 1)
        me = bpy.data.meshes.new('_tmp'); tbm.to_mesh(me); tbm.free()
        self.bm.from_mesh(me); bpy.data.meshes.remove(me)
        return self
    def tris(self):
        return sum(max(1, len(f.verts) - 2) for f in self.bm.faces)
    def finish(self, colname, loc=(0, 0, 0)):
        me = bpy.data.meshes.new(self.name); self.bm.to_mesh(me); self.bm.free()
        for k in self.keys: me.materials.append(paint_mat(k))
        o = bpy.data.objects.new(self.name, me); col(colname).objects.link(o); o.location = loc
        return o

def instance(master, name, colname, loc=(0, 0, 0), rot_z=0.0, scale=(1, 1, 1)):
    """copia ligada (mesma malha) - e assim que o kit e reutilizado."""
    o = bpy.data.objects.new(name, master.data); col(colname).objects.link(o)
    o.location = loc; o.rotation_euler = (0, 0, math.radians(rot_z)); o.scale = scale
    return o

def smooth01(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)

def arc_pts(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
