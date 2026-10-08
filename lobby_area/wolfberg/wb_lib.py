# wb_lib.py - base do lobby WOLFBERG (vila medieval de forja, estilo da imagem do usuario) sobre o pipeline
# compartilhado (lobby_area/forja_mineradora: fm_lib/export_roblox SO LEITURA) e a planta/contratos da Vila Medieval
# (lobby_area/vila_medieval/vm_layout.py SO LEITURA).
# - registra os materiais WB_* no fm_lib.MATS com texturas COLORIDAS tileaveis (wb_tex, SurfaceAppearance no Roblox);
# - construtor de geometria (bmesh) com UV por projecao cubica em studs/tile (igual ao _uv_fallback do export);
# - conversao Roblox <-> Blender (Blender = (X, -Z, Y) do Roblox) e colecoes.
# Coordenadas nos construtores: BLENDER (x leste, y = -z_roblox, z = altura). Use RB(x, z, y) para converter.
import math
import os
import random
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
FORJA = os.path.join(ROOT, "lobby_area", "forja_mineradora")
VILA = os.path.join(ROOT, "lobby_area", "vila_medieval")
for p in (FORJA, VILA, HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)       # ordem final: HERE, VILA, FORJA

import bmesh
import bpy
from mathutils import Matrix, Vector

import fm_lib
import fm_mat_textures as TX
import wb_tex
from fm_lib import MATS, S

V = Vector
RAD = math.radians

# ------------------------------------------------------------------ materiais WB (cor base; a textura cobre com alpha 1)
# nome: (cor sRGB 0-255, rough, metal, emissao, cor_emissao, variacao), textura pela familia do prefixo (TEX_RULES)
WBMATS = {
    "WB_Cobble":        ((160, 146, 128), 0.9, 0.0, 0, None, 0.0),
    "WB_Cobble_Dark":   ((124, 112, 98), 0.9, 0.0, 0, None, 0.0),
    "WB_Stone":         ((152, 144, 132), 0.9, 0.0, 0, None, 0.0),
    "WB_Stone_Dark":    ((108, 102, 98), 0.9, 0.0, 0, None, 0.0),
    "WB_Plaster":       ((222, 204, 170), 0.9, 0.0, 0, None, 0.0),
    "WB_Plaster_Ochre": ((214, 188, 146), 0.9, 0.0, 0, None, 0.0),
    "WB_Timber":        ((88, 60, 40), 0.8, 0.0, 0, None, 0.0),
    "WB_Plank":         ((150, 104, 64), 0.8, 0.0, 0, None, 0.0),
    "WB_Plank_Light":   ((184, 140, 92), 0.8, 0.0, 0, None, 0.0),
    "WB_Roof":          ((170, 80, 48), 0.8, 0.0, 0, None, 0.0),
    "WB_Roof_Dark":     ((136, 62, 40), 0.8, 0.0, 0, None, 0.0),
    "WB_CanvasRed":     ((200, 70, 56), 0.9, 0.0, 0, None, 0.0),
    "WB_CanvasBlue":    ((70, 100, 160), 0.9, 0.0, 0, None, 0.0),
    "WB_CanvasGreen":   ((86, 136, 80), 0.9, 0.0, 0, None, 0.0),
    "WB_Iron":          ((74, 72, 76), 0.6, 0.4, 0, None, 0.0),
    "WB_Grass":         ((104, 160, 58), 0.9, 0.0, 0, None, 0.0),
    "WB_Dirt":          ((150, 118, 82), 0.95, 0.0, 0, None, 0.0),
    "WB_Bark":          ((96, 66, 44), 0.9, 0.0, 0, None, 0.0),
    "WB_Leaf":          ((84, 150, 62), 0.85, 0.0, 0, None, 0.0),
    "WB_Rock":          ((132, 122, 112), 0.9, 0.0, 0, None, 0.0),
    "WB_Pine":          ((46, 104, 66), 0.85, 0.0, 0, None, 0.0),
    "WB_Crop":          ((150, 170, 70), 0.9, 0.0, 0, None, 0.0),
    "WB_Grass_Hill":    ((112, 160, 72), 0.9, 0.0, 0, None, 0.0),
    "WB_FlowerRed":     ((214, 50, 50), 0.8, 0.0, 0, None, 0.0),
    "WB_FlowerPink":    ((230, 110, 160), 0.8, 0.0, 0, None, 0.0),
    "WB_FlowerYellow":  ((240, 200, 60), 0.8, 0.0, 0, None, 0.0),
    "WB_FlowerWhite":   ((236, 232, 220), 0.8, 0.0, 0, None, 0.0),
    "WB_Bread":         ((214, 160, 90), 0.9, 0.0, 0, None, 0.0),
    "WB_Apple":         ((200, 48, 40), 0.5, 0.0, 0, None, 0.0),
    "WB_Leather":       ((120, 72, 44), 0.8, 0.0, 0, None, 0.0),
    "WB_LeatherDark":   ((70, 42, 28), 0.8, 0.0, 0, None, 0.0),
    "WB_Cloth_Red":     ((176, 54, 44), 0.9, 0.0, 0, None, 0.0),
    "WB_Cloth_Blue":    ((56, 86, 150), 0.9, 0.0, 0, None, 0.0),
    "WB_Cloth_Green":   ((60, 120, 70), 0.9, 0.0, 0, None, 0.0),
    "WB_Cloth_Gold":    ((214, 170, 70), 0.9, 0.0, 0, None, 0.0),
    "WB_Cloth_Purple":  ((110, 60, 150), 0.9, 0.0, 0, None, 0.0),
    "WB_Cloth_Cream":   ((228, 214, 180), 0.9, 0.0, 0, None, 0.0),
    "WB_Coal":          ((40, 38, 36), 0.9, 0.0, 0, None, 0.0),
    "WB_Ingot":         ((255, 120, 40), 0.5, 0.0, 1.4, (255, 110, 30), 0.0),
    "WB_Dark":          ((30, 26, 24), 0.9, 0.0, 0, None, 0.0),
    "WB_Paper":         ((236, 226, 196), 0.9, 0.0, 0, None, 0.0),
    # sem textura (cor solida / neon)
    "WB_Glass":         ((60, 70, 90), 0.3, 0.0, 0, None, 0.0),
    "WB_Fire":          ((255, 150, 40), 0.5, 0.0, 2.5, (255, 140, 30), 0.0),
    "WB_Ember":         ((255, 90, 20), 0.5, 0.0, 1.6, (255, 80, 20), 0.0),
    "WB_LampGlow":      ((255, 214, 130), 0.5, 0.0, 1.8, (255, 210, 120), 0.0),
    "WB_Water":         ((70, 150, 190), 0.1, 0.0, 0, None, 0.0),
    "WB_Rope":          ((190, 160, 110), 0.9, 0.0, 0, None, 0.0),
    "WB_Brass":         ((196, 150, 70), 0.4, 0.8, 0, None, 0.0),
    "WB_Smoke":         ((120, 120, 120), 0.9, 0.0, 0, None, 0.0),
    "WB_SignText":      ((240, 220, 170), 0.8, 0.0, 0, None, 0.0),
    "WB_Snow":          ((230, 234, 240), 0.9, 0.0, 0, None, 0.0),
    "WB_FarMountain":   ((108, 128, 168), 0.95, 0.0, 0, None, 0.0),
}
# prefixo do material -> familia de textura (wb_tex.TEXTURES)
WB_TEX_RULES = [("WB_Cobble", "wb_cobble"), ("WB_Stone_Dark", "wb_stone_dark"), ("WB_Stone", "wb_stone"),
                ("WB_Plaster", "wb_plaster"), ("WB_Timber", "wb_timber"), ("WB_Plank", "wb_plank"),
                ("WB_Roof_Dark", "wb_roof_dark"), ("WB_Roof", "wb_roof"), ("WB_Plaster_Ochre", "wb_plaster_ochre"), ("WB_CanvasRed", "wb_canvas_red"), ("WB_CanvasBlue", "wb_canvas_blue"),
                ("WB_CanvasGreen", "wb_canvas_green"), ("WB_Iron", "wb_iron"), ("WB_Grass", "wb_grass"),
                ("WB_Dirt", "wb_dirt"), ("WB_Bark", "wb_bark"), ("WB_Leaf", "wb_leaf"), ("WB_Rock", "wb_rock"),
                ("WB_Pine", "wb_pine"), ("WB_Crop", "wb_crop"), ("WB_Grass_Hill", "wb_grass")]
# prefixo -> (Material do Roblox, transparencia, sombra)
WB_RBX_RULES = [("WB_Fire", "Neon", 0.0, False), ("WB_Ember", "Neon", 0.0, False), ("WB_LampGlow", "Neon", 0.0, False),
                ("WB_Ingot", "Neon", 0.0, False), ("WB_Cloth_", "Fabric", 0.0, True), ("WB_Pine", "Grass", 0.0, True),
                ("WB_Flower", "SmoothPlastic", 0.0, False),
                ("WB_Glass", "Glass", 0.3, True), ("WB_Water", "SmoothPlastic", 0.2, False),
                ("WB_Snow", "Snow", 0.0, False), ("WB_FarMountain", "SmoothPlastic", 0.0, False),
                ("WB_Brass", "Metal", 0.0, True), ("WB_Iron", "Metal", 0.0, True), ("WB_Grass", "Grass", 0.0, True),
                ("WB_Leaf", "Grass", 0.0, True), ("WB_Rock", "Slate", 0.0, True), ("WB_", "SmoothPlastic", 0.0, True)]

_registered = [False]


def register():
    """registra materiais, regras e texturas WB no pipeline compartilhado (sem editar os arquivos dele)"""
    if _registered[0]:
        return
    _registered[0] = True
    for k, (c, rough, metal, emit, ecol, var) in WBMATS.items():
        MATS.setdefault(k, (S(*c), rough, metal, emit, S(*ecol) if ecol else None, var))
    for r in reversed(WB_RBX_RULES):
        if r not in fm_lib.RBX_RULES:
            fm_lib.RBX_RULES.insert(0, r)
    for p, k in reversed(WB_TEX_RULES):
        if (p, k) not in fm_lib.TEX_RULES:
            fm_lib.TEX_RULES = ((p, k),) + tuple(fm_lib.TEX_RULES)
    # texturas: o fm_lib/export leem TX.TEXTURES (tile), TX.ensure() (caminhos) e TX.path(key)
    TX.TEXTURES.update(wb_tex.TEXTURES)
    if not getattr(TX, "_wb_patched", False):
        _orig_ensure, _orig_path = TX.ensure, TX.path

        def ensure(force=False, out_dir=None):
            # o ensure compartilhado itera TX.TEXTURES com o GEN dele: tira as chaves WB durante a chamada
            wb = {k: TX.TEXTURES.pop(k) for k in list(TX.TEXTURES) if k in wb_tex.TEXTURES}
            try:
                paths = _orig_ensure(force, out_dir)
            finally:
                TX.TEXTURES.update(wb)
            paths.update(wb_tex.ensure())
            return paths

        def path(key):
            return wb_tex.path(key) if key in wb_tex.TEXTURES else _orig_path(key)
        TX.ensure, TX.path = ensure, path
        TX._wb_patched = True
    wb_tex.ensure()


def tile_of(mat):
    for p, k in fm_lib.TEX_RULES:
        if k and mat.startswith(p):
            return TX.TEXTURES[k][1]
    return None


# ------------------------------------------------------------------ coordenadas e colecoes
def RB(x, z, y=0.0):
    """Roblox (x, y, z) -> Blender Vector (x, -z, y)"""
    return V((x, -z, y))


def to_rbx(v):
    return (v.x, v.z, -v.y)


def collection(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def euler(rx=0.0, ry=0.0, rz=0.0):
    return (Matrix.Rotation(RAD(rz), 3, "Z") @ Matrix.Rotation(RAD(ry), 3, "Y") @ Matrix.Rotation(RAD(rx), 3, "X"))


def rot_z(deg):
    return Matrix.Rotation(RAD(deg), 3, "Z")


# ------------------------------------------------------------------ construtor
class Build:
    """acumula geometria por material e cria 1 objeto por material ao finalizar: <name>__<mat>.
    Todas as primitivas em coordenadas BLENDER (studs). Objetos ficam com transform identidade (malha no mundo),
    UV por projecao cubica em studs/tile (igual ao export) e sombreamento por angulo."""

    def __init__(self, name, coll="03_TOWN", seed=0):
        self.name = name
        self.coll = coll
        self.rng = random.Random(seed)
        self.bms = {}
        self.objects = []

    def bm(self, mat):
        if mat not in MATS:
            raise KeyError("material desconhecido: " + mat)
        b = self.bms.get(mat)
        if b is None:
            b = self.bms[mat] = bmesh.new()
        return b

    def add(self, bm_src, mat):
        dst = self.bm(mat)
        me = bpy.data.meshes.new("_tmp")
        bm_src.to_mesh(me)
        dst.from_mesh(me)
        bpy.data.meshes.remove(me)
        bm_src.free()
        return self

    # --- primitivas
    def box(self, center, dims, mat, rot=None, bevel=0.0, segs=1):
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.transform(bm, matrix=Matrix.Diagonal(V((*dims, 1.0))), verts=bm.verts[:])
        if bevel > 0:
            bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, offset_type="OFFSET", segments=segs, profile=0.5,
                            affect="EDGES", clamp_overlap=True)
        R = (rot if rot is not None else Matrix.Identity(3)).to_4x4()
        bmesh.ops.transform(bm, matrix=Matrix.Translation(V(center)) @ R, verts=bm.verts[:])
        return self.add(bm, mat)

    def box2(self, p0, p1, mat, bevel=0.0):
        p0, p1 = V(p0), V(p1)
        c = (p0 + p1) * 0.5
        d = p1 - p0
        return self.box(c, (abs(d.x), abs(d.y), abs(d.z)), mat, bevel=bevel)

    def cyl(self, p0, p1, r0, mat, r1=None, seg=12, caps=True, bevel=0.0):
        r1 = r0 if r1 is None else r1
        p0, p1 = V(p0), V(p1)
        L = (p1 - p0).length
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=r0, radius2=r1, depth=L)
        z = (p1 - p0).normalized()
        x = V((0, 0, 1)).cross(z)
        if x.length < 1e-5:
            x = V((1, 0, 0)).cross(z)
        x.normalize()
        y = z.cross(x)
        R = Matrix((x, y, z)).transposed().to_4x4()
        bmesh.ops.transform(bm, matrix=Matrix.Translation((p0 + p1) * 0.5) @ R, verts=bm.verts[:])
        if bevel > 0:
            es = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0.0) > RAD(40)]
            bmesh.ops.bevel(bm, geom=es, offset=bevel, offset_type="OFFSET", segments=1, affect="EDGES",
                            clamp_overlap=True)
        return self.add(bm, mat)

    def sphere(self, center, r, mat, seg=16, scale=(1, 1, 1)):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(6, seg // 2), radius=r)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(V(center)) @ Matrix.Diagonal(V((*scale, 1.0))),
                            verts=bm.verts[:])
        return self.add(bm, mat)

    def prism(self, poly, z0, z1, mat, bevel=0.0):
        """extrusao vertical de um poligono (lista de (x, y)) de z0 a z1"""
        bm = bmesh.new()
        bot = [bm.verts.new((x, y, z0)) for (x, y) in poly]
        top = [bm.verts.new((x, y, z1)) for (x, y) in poly]
        n = len(poly)
        try:
            bm.faces.new(list(reversed(bot)))
            bm.faces.new(top)
        except ValueError:
            pass
        for i in range(n):
            bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if bevel > 0:
            bmesh.ops.bevel(bm, geom=bm.edges[:], offset=bevel, offset_type="OFFSET", segments=1, affect="EDGES",
                            clamp_overlap=True)
        return self.add(bm, mat)

    def slab(self, poly, z_top, thick, mat, bevel=0.0):
        return self.prism(poly, z_top - thick, z_top, mat, bevel)

    def quad(self, a, b, c, d, mat, thick=0.0):
        """quadrilatero (a,b,c,d anti-horario visto de frente); thick > 0 extruda ao longo da normal"""
        bm = bmesh.new()
        vs = [bm.verts.new(V(p)) for p in (a, b, c, d)]
        f = bm.faces.new(vs)
        if thick > 0:
            r = bmesh.ops.extrude_face_region(bm, geom=[f])
            nv = [g for g in r["geom"] if isinstance(g, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, vec=-f.normal * thick, verts=nv)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        return self.add(bm, mat)

    def tri(self, a, b, c, mat):
        bm = bmesh.new()
        bm.faces.new([bm.verts.new(V(p)) for p in (a, b, c)])
        return self.add(bm, mat)

    def beam(self, a, b, w, h, mat, roll=0.0):
        """viga de secao w x h de a ate b"""
        a, b = V(a), V(b)
        L = (b - a).length
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.transform(bm, matrix=Matrix.Diagonal(V((w, h, L, 1.0))), verts=bm.verts[:])
        z = (b - a).normalized()
        up = V((0, 0, 1)) if abs(z.z) < 0.99 else V((0, 1, 0))
        x = up.cross(z).normalized()
        y = z.cross(x)
        R = Matrix((x, y, z)).transposed()
        if roll:
            R = R @ Matrix.Rotation(RAD(roll), 3, "Z")
        bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) * 0.5) @ R.to_4x4(), verts=bm.verts[:])
        return self.add(bm, mat)

    def mesh(self, bm, mat):
        return self.add(bm, mat)

    # --- fechamento
    def finish(self, smooth_angle=35.0, uv=True):
        coll = collection(self.coll)
        out = []
        for mat, bm in self.bms.items():
            if not bm.faces:
                bm.free()
                continue
            bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.0005)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            if uv:
                box_uv(bm, tile_of(mat) or 4.0)
            me = bpy.data.meshes.new("%s__%s" % (self.name, mat))
            bm.to_mesh(me)
            bm.free()
            ob = bpy.data.objects.new(me.name, me)
            coll.objects.link(ob)
            m = bpy.data.materials.get(mat)
            if m is None:
                fm_lib.make_materials()
                m = bpy.data.materials.get(mat)
            me.materials.append(m)
            for p in me.polygons:
                p.use_smooth = True
            try:
                me.set_sharp_from_angle(angle=RAD(smooth_angle))
            except Exception:
                pass
            out.append(ob)
        self.bms = {}
        self.objects += out
        return out


def box_uv(bm, tile):
    """UV por projecao cubica em coordenadas de mundo, studs/tile (mesma regra do export_roblox._uv_fallback)"""
    uvl = bm.loops.layers.uv.get("UVMap") or bm.loops.layers.uv.new("UVMap")
    inv = 1.0 / tile
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (co[a] * inv, co[b] * inv)


# ------------------------------------------------------------------ cena de teste e render
def reset_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    for im in list(bpy.data.images):
        if im.users == 0 and not im.name.startswith("TEX_"):
            bpy.data.images.remove(im)


def setup_render(res=(1280, 720), samples=32, sun_rot=(52, 0, -35), sun_energy=4.0, sky=(0.55, 0.72, 0.95)):
    sc = bpy.context.scene
    try:
        sc.render.engine = "BLENDER_EEVEE"
    except Exception:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    try:
        sc.eevee.taa_render_samples = samples
        sc.eevee.use_shadows = True
    except Exception:
        pass
    w = sc.world or bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (*sky, 1)
    bg.inputs[1].default_value = 1.0
    for n in ("SUN", "FILL"):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    ld = bpy.data.lights.new("SUN", "SUN")
    ld.energy = sun_energy
    ld.color = (1.0, 0.95, 0.85)
    ld.angle = RAD(2.5)
    o = bpy.data.objects.new("SUN", ld)
    bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = [RAD(a) for a in sun_rot]
    ld2 = bpy.data.lights.new("FILL", "SUN")
    ld2.energy = 0.8
    ld2.color = (0.75, 0.85, 1.0)
    o2 = bpy.data.objects.new("FILL", ld2)
    bpy.context.scene.collection.objects.link(o2)
    o2.rotation_euler = [RAD(a) for a in (60, 0, 150)]


def camera(name, eye, target, lens=35):
    """eye/target em coordenadas ROBLOX (x, y, z)"""
    cd = bpy.data.cameras.get(name) or bpy.data.cameras.new(name)
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, cd)
        bpy.context.scene.collection.objects.link(cam)
    e = RB(eye[0], eye[2], eye[1])
    t = RB(target[0], target[2], target[1])
    cam.location = e
    cam.rotation_euler = (t - e).to_track_quat("-Z", "Y").to_euler()
    cd.lens = lens
    cd.clip_end = 3000
    return cam


def render(cam, path):
    sc = bpy.context.scene
    sc.camera = cam
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDER", os.path.basename(path))
