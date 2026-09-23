# export_roblox.py - prepara o lobby para o Roblox Studio
# uso: blender -b lobby_forja_mineradora.blend --python export_roblox.py [-- <pasta_saida>]
#      (ou FM_EXPORT_DIR=<pasta>; padrao ./export)
# saida:
#   LOBBY_<colecao>.fbx      malhas visuais: 1 material (VARIANTE) por malha, <= 18k tris, origem no CENTRO DO BBOX,
#                            UVMap em studs/TILE e texturas de detalhe EMBUTIDAS (o 3D Importer faz o upload)
#   lobby_data.json          malhas (centro/tamanho esperados), materiais, colisoes (COL_), marcadores, luzes
#   montar_lobby_forja.lua   Command Bar: alinha as malhas importadas, aplica cor/Material/textura por variante,
#                            cria colisoes invisiveis, marcadores, luzes, chao distante e (opcional) o Lighting do lobby
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector, Matrix
import fm_lib
import fm_mat_textures as TX

_argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = (_argv[0] if _argv else None) or os.environ.get("FM_EXPORT_DIR") or os.path.join(HERE, "export")
os.makedirs(OUT, exist_ok=True)
MAX_TRIS = 18000
GROUPS = ["02_TERRAIN", "03_FORGE", "04_MINE", "05_WATER_SYSTEM", "06_PORTALS", "07_BUILDINGS", "08_PROPS",
          "09_VEGETATION", "10_RAILS"]
SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "SKY_", "VFX_")
# vale distante: exporta so as silhuetas de rocha; o plano de 2400 studs vira uma Part de chao no Lua
FAR_VALLEY = "TER_Far_Valley"
FAR_GROUND = {"size": [2048, 2, 2048], "top_z": -69.0, "material": "Grass_Dark"}

# Blender (x, y, z) -> FBX(-Z fwd, Y up) -> Roblox (x, z, -y). Mesmo mapeamento para colisoes/marcadores/luzes.
# O montar_lobby_forja.lua CONFERE isso na importacao (ALINHAR) e corrige rotacao/deslocamento/escala do importador.
T = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))


def to_rbx(v):
    v = T @ Vector(v)
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


# ------------------------------------------------------------------ materiais Roblox
# (prefixo da familia, Enum.Material do modo padrao "hibrido" testado no Studio, transparencia, CastShadow)
# Hibrido (achado do Studio): material rico so onde a superficie e grande e lisa (Grass, Slate, Wood, Ground);
# SmoothPlastic onde a GEOMETRIA ja desenha o padrao (calcamento, alvenaria, telhas, folhas).
RBX_RULES = [
    ("Stone_Grout", "SmoothPlastic", 0.0, False),
    ("Stone_Paving", "SmoothPlastic", 0.0, False),
    ("Stone_", "SmoothPlastic", 0.0, True),
    ("Cliff_Rock", "Slate", 0.0, True),
    ("Grass", "Grass", 0.0, False),
    ("Dirt", "Ground", 0.0, False),
    ("Wood_", "Wood", 0.0, True),
    ("Bark", "Wood", 0.0, True),
    ("Rope", "Fabric", 0.0, True),
    ("Roof", "SmoothPlastic", 0.0, True),
    ("Plaster", "SmoothPlastic", 0.0, True),
    ("Leaf_", "SmoothPlastic", 0.0, False),
    ("Metal_Rust", "CorrodedMetal", 0.0, True),
    ("Metal_Heated", "Neon", 0.0, False),
    ("Metal_", "Metal", 0.0, True),
    ("P_DB_Gold", "Metal", 0.0, True),
    ("Water_Fall", "SmoothPlastic", 0.10, False),
    ("Water", "SmoothPlastic", 0.10, False),
    ("Foam", "SmoothPlastic", 0.05, False),
    ("P_OPM_Glass", "Glass", 0.2, True),
    ("P_OPM_Neon", "Neon", 0.0, False),
    ("Cloth_", "Fabric", 0.0, True),
    ("Leather", "Fabric", 0.0, True),
    ("Crystal_", "Neon", 0.0, False),
    ("Forge_Emissive", "Neon", 0.0, False),
    ("Lantern_Glow", "Neon", 0.0, False),
    ("Smoke", "SmoothPlastic", 0.3, False),
]
# materiais desconhecidos (registrados por outros modulos): palavra-chave -> (Material, transp, sombra)
RBX_KEYWORDS = [
    (("swirl", "glow", "emissive", "neon", "lantern", "crystal", "heated", "fire", "flame", "ember", "lava", "spark"),
     ("Neon", 0.0, False)),
    (("waterfall", "water", "foam", "spray"), ("SmoothPlastic", 0.10, False)),
    (("glass", "window"), ("Glass", 0.2, True)),
    (("rust", "corrod"), ("CorrodedMetal", 0.0, True)),
    (("metal", "iron", "steel", "gold", "brass", "bronze", "copper", "chain"), ("Metal", 0.0, True)),
    (("grass", "moss", "lawn"), ("Grass", 0.0, False)),
    (("leaf", "foliage", "petal", "bush", "ivy", "vine"), ("SmoothPlastic", 0.0, False)),
    (("cliff", "rock", "boulder", "slate"), ("Slate", 0.0, True)),
    (("wood", "plank", "bark", "beam", "timber", "log"), ("Wood", 0.0, True)),
    (("dirt", "mud", "soil", "ground"), ("Ground", 0.0, False)),
    (("sand",), ("Sand", 0.0, False)),
    (("snow",), ("Snow", 0.0, False)),
    (("ice",), ("Ice", 0.0, True)),
    (("cloth", "banner", "fabric", "rope", "canvas", "leather", "flag"), ("Fabric", 0.0, True)),
]

# Correcao de cor TESTADA no Studio (A/B em LOBBY_FORJA_PREVIEW.VARIANTE_CORRIGIDA): (cor exportada antes, cor certa).
# Aplica-se por RAZAO por canal a toda a familia (variantes B/C e mudancas futuras de paleta seguem junto).
# None no 1o campo = cor absoluta (familia sem variantes e com cor base inalterada).
RBX_CAL = {
    "Cliff_Rock": ((139, 139, 147), (136, 130, 122)),
    "Cliff_Rock_Dark": ((108, 108, 118), (102, 96, 90)),
    # familias cuja paleta do Blender mudou neste passe (pedra/madeira mais quentes, telhado mais escuro):
    # (cor A atual no Blender, alvo no Roblox) derivado do achado do Studio (tirar o azul, conter saturacao
    # porque a luz do Roblox ja esquenta e satura). As variantes B/C seguem pela razao B/A do Blender.
    "Stone_Light": ((150, 141, 129), (156, 148, 136)),
    "Stone_Dark": ((100, 92, 86), (102, 95, 88)),
    "Stone_Grout": ((88, 82, 76), (88, 82, 76)),
    "Stone_Paving": ((158, 145, 131), (158, 146, 132)),
    "Grass": ((96, 152, 58), (90, 134, 62)),
    "Grass_Dark": ((63, 108, 63), (60, 98, 60)),
    "Dirt": ((134, 108, 80), (124, 100, 76)),
    "Wood_Light": ((160, 114, 74), (148, 110, 80)),
    "Wood_Dark": ((100, 66, 43), (92, 64, 47)),
    "Wood_Plank": ((136, 95, 61), (126, 92, 66)),
    "Bark": ((144, 118, 89), (120, 98, 76)),
    "Rope": (None, (190, 172, 140)),
    "Roof": ((110, 108, 114), (106, 104, 106)),
    "Roof_Red": ((179, 89, 75), (168, 86, 74)),
    "Plaster": ((200, 184, 162), (196, 184, 166)),
    "Leaf_Pine": ((69, 134, 89), (64, 120, 70)),
    "Leaf_Pine_Light": ((129, 177, 111), (116, 158, 96)),
    "Leaf_Palm": ((124, 188, 108), (110, 166, 94)),
    "Leaf_Sakura": (None, (242, 188, 212)),
    "Metal_Dark": ((85, 85, 89), (78, 76, 76)),
    "Metal_Iron": ((124, 124, 129), (116, 114, 112)),
    "Metal_Brass": ((203, 170, 105), (186, 148, 90)),
    "Metal_Burnt": (None, (66, 56, 56)),
    "Metal_Rust": (None, (142, 88, 58)),
    "P_DB_Gold": ((249, 212, 108), (226, 178, 78)),
    "Forge_Emissive": (None, (250, 170, 110)),
    "Lantern_Glow": (None, (250, 214, 170)),
    "Metal_Heated": (None, (190, 86, 40)),
    "Crystal_Blue": (None, (70, 130, 210)),
    "Crystal_Purple": (None, (135, 95, 200)),
    "P_Naruto_Swirl": (None, (236, 130, 168)),
    "P_DB_Swirl": (None, (236, 200, 110)),
    "P_Shadow_Swirl": (None, (176, 120, 226)),
    "P_DS_Swirl": (None, (230, 112, 112)),
    "P_OP_Swirl": (None, (104, 160, 236)),
    "P_OPM_Swirl": (None, (124, 200, 236)),
    "P_Gold_Glow": (None, (220, 180, 90)),
    "P_Red_Glow": (None, (210, 80, 70)),
    "P_Shadow_Glow": (None, (176, 120, 226)),
    "P_OPM_Neon": (None, (80, 180, 220)),
    "Water": (None, (84, 156, 204)),
    "Water_Fall": (None, (176, 216, 240)),
    "Foam": (None, (236, 244, 250)),
}
# Lighting recomendado para o lobby (Studio). So e aplicado com APLICAR_LIGHTING=true no Lua; o ideal e levar
# estes valores para o perfil do lobby em StarterPlayerScripts.AreaAtmosphere (CurrentAreaId 0).
LIGHTING_LOBBY = {
    "Lighting": {"GeographicLatitude": 64, "ClockTime": 14.2, "EnvironmentDiffuseScale": 0.4,
                 "EnvironmentSpecularScale": 0.5, "Brightness": 2.5, "ExposureCompensation": 0.0,
                 "ShadowSoftness": 0.2, "OutdoorAmbient": [140, 138, 134], "Ambient": [100, 98, 96],
                 "ColorShift_Top": [255, 236, 210]},
    "ColorCorrectionEffect": {"Saturation": 0.02, "Contrast": 0.08, "TintColor": [255, 250, 244]},
    "BloomEffect": {"Threshold": 1.9, "Intensity": 0.35, "Size": 24},
    "Atmosphere": {"Density": 0.2, "Offset": 0.1, "Haze": 1.0, "Glare": 0.1, "Color": [205, 215, 228],
                   "Decay": [140, 160, 185]},
}
SHADOW_LIGHTS = ("L_Hearth_Fire", "L_Furnace")


def srgb(c):
    return fm_lib.to_srgb(c)


def family(name):
    return fm_lib.family_of(name)


def rbx_rule(name):
    """(Material, transparencia, CastShadow) pelo maior prefixo conhecido; senao por palavra-chave"""
    fam = family(name)
    best = None
    for key in (name, fam):
        for p, m, t, s in RBX_RULES:
            if key.startswith(p) and (best is None or len(p) > len(best[0])):
                best = (p, m, t, s)
    if best:
        return best[1], best[2], best[3]
    if name in fm_lib.SWIRLS or "swirl" in name.lower():
        return "Neon", 0.0, False
    n = name.lower()
    for kws, res in RBX_KEYWORDS:
        if any(k in n for k in kws):
            return res
    return "SmoothPlastic", 0.0, True


def rbx_color(name, mat=None):
    """cor do Roblox: cor da variante (MATS) x correcao testada da familia (razao por canal)"""
    if name in fm_lib.MATS:
        c = srgb(fm_lib.MATS[name][0])
    elif mat is not None:
        c = srgb(tuple(mat.diffuse_color)[:3])
    else:
        c = [163, 162, 165]
    fam = family(name)
    cal = RBX_CAL.get(name) or RBX_CAL.get(fam)
    if not cal:
        # familia de outro modulo: tenta pelo maior prefixo calibrado (ex.: Stone_Light_Musgo -> Stone_Light)
        keys = [k for k in RBX_CAL if name.startswith(k)]
        if keys:
            cal = RBX_CAL[max(keys, key=len)]
    if not cal:
        return c
    old, new = cal
    if old is None:
        if name == fam or name in RBX_CAL:
            return list(new)
        base = srgb(fm_lib.MATS[fam][0]) if fam in fm_lib.MATS else c
        old = base
    return [max(0, min(255, int(round(n * (x / max(o, 1)))))) for x, o, n in zip(c, old, new)]


def tex_of(name):
    return fm_lib.tex_key(name)


# ------------------------------------------------------------------ geometria
def _uv_fallback(bm, uvl, name):
    """malha sem UVMap (objeto feito fora do MB): projecao CUBICA em coordenadas de mundo, em studs/TILE"""
    tk = tex_of(name)
    inv = 1.0 / (fm_lib.tex_tile(tk) if tk else 4.0)
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for lp in f.loops:
            co = lp.vert.co
            lp[uvl].uv = (co[a] * inv, co[b] * inv)


def _uv_disc(bm, uvl):
    """espiral do portal: UV planar do disco (0..1), 'cima' do mundo = v"""
    nrm = Vector()
    for f in bm.faces:
        nrm += f.normal * f.calc_area()
    if nrm.length < 1e-6:
        return
    nrm.normalize()
    lo = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
    hi = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
    c = (lo + hi) / 2
    up = Vector((0, 0, 1)) - nrm * nrm.z
    if up.length < 1e-3:
        up = Vector((0, 1, 0)) - nrm * nrm.y
    up.normalize()
    side = up.cross(nrm).normalized()
    R = max(((v.co - c) - nrm * (v.co - c).dot(nrm)).length for v in bm.verts) or 1.0
    for f in bm.faces:
        for lp in f.loops:
            d = lp.vert.co - c
            lp[uvl].uv = (0.5 + d.dot(side) / (2 * R), 0.5 + d.dot(up) / (2 * R))


def split_object(ob):
    """retorna lista de (nome, mesh, material) - um por material (variante), fatiado se passar de MAX_TRIS.
    Copia a UVMap do MB; sem UV -> projecao cubica de mundo; espirais -> UV do disco."""
    res = []
    me = ob.data
    mw = ob.matrix_world
    bm_all = bmesh.new()
    bm_all.from_mesh(me)
    bm_all.transform(mw)
    bmesh.ops.triangulate(bm_all, faces=bm_all.faces[:])
    bm_all.verts.index_update()
    uv_src = bm_all.loops.layers.uv.get("UVMap") or bm_all.loops.layers.uv.active
    by_mat = {}
    for f in bm_all.faces:
        by_mat.setdefault(f.material_index, []).append(f)
    for mi, faces in sorted(by_mat.items()):
        mname = me.materials[mi].name if mi < len(me.materials) and me.materials[mi] else "Default"
        if ob.name.startswith(FAR_VALLEY) and family(mname) in ("Grass_Dark", "Grass"):
            continue   # plano gigante do vale -> Part FAR_GROUND no Lua
        chunks = [faces]
        # fatia espacialmente ate cada pedaco caber no limite
        while any(len(c) > MAX_TRIS for c in chunks):
            new = []
            for c in chunks:
                if len(c) <= MAX_TRIS:
                    new.append(c)
                    continue
                cs = [f.calc_center_median() for f in c]
                xs = [p.x for p in cs]
                ys = [p.y for p in cs]
                axis = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
                order = sorted(range(len(c)), key=lambda i: cs[i][axis])
                h = len(order) // 2
                new.append([c[i] for i in order[:h]])
                new.append([c[i] for i in order[h:]])
            chunks = new
        for k, c in enumerate(chunks):
            bm = bmesh.new()
            uvl = bm.loops.layers.uv.new("UVMap")
            vmap = {}
            for f in c:
                vs = []
                for v in f.verts:
                    if v.index not in vmap:
                        vmap[v.index] = bm.verts.new(v.co)
                    vs.append(vmap[v.index])
                try:
                    nf = bm.faces.new(vs)
                except ValueError:
                    continue
                if uv_src is not None:
                    for ln, lo in zip(nf.loops, f.loops):
                        ln[uvl].uv = lo[uv_src].uv
            bm.verts.index_update()
            bm.normal_update()
            if mname in fm_lib.SWIRLS or mname in TX.SWIRL_TEX:
                _uv_disc(bm, uvl)
            elif uv_src is None:
                _uv_fallback(bm, uvl, mname)
            name = "%s__%s" % (ob.name, mname) + ("_%d" % k if len(chunks) > 1 else "")
            nm = bpy.data.meshes.new(name)
            bm.to_mesh(nm)
            bm.free()
            res.append((name, nm, mname))
    bm_all.free()
    return res


# ------------------------------------------------------------------ materiais do FBX (texturas embutidas)
_EXP_MATS = {}


def export_material(mname):
    """material do FBX: familias texturizadas recebem a PNG de detalhe ligada DIRETO no Base Color (o exportador
    FBX so enxerga textura ligada direto); espirais recebem a PNG da espiral. Demais: o proprio material."""
    tk = tex_of(mname)
    swirl = mname if mname in TX.SWIRL_TEX else None
    if not tk and not swirl:
        return bpy.data.materials.get(mname)
    key = swirl or tk
    if key in _EXP_MATS:
        return _EXP_MATS[key]
    p = TX.swirl_path(swirl) if swirl else TX.path(tk)
    img = bpy.data.images.load(p, check_existing=False)
    img.name = "RBX_" + os.path.basename(p)
    m = bpy.data.materials.new("RBX_" + (("SWIRL_" + swirl) if swirl else ("TEX_" + tk)))
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    im = nt.nodes.new("ShaderNodeTexImage")
    im.image = img
    nt.links.new(im.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(bs.outputs[0], out.inputs[0])
    _EXP_MATS[key] = m
    return m


def main():
    TX.ensure()
    data = {"mapping": "Roblox = (x_blender, z_blender, -y_blender); 1 BU = 1 stud; malha: origem = centro do bbox",
            "meshes": [], "materials": {}, "textures": {}, "collisions": [], "markers": [], "lights": [],
            "far_ground": None, "lighting_lobby": LIGHTING_LOBBY}
    tmp = bpy.data.collections.new("_EXPORT_TMP")
    bpy.context.scene.collection.children.link(tmp)
    total = 0
    used = {}
    for g in GROUPS:
        col = bpy.data.collections.get(g)
        if not col:
            continue
        objs = [o for o in col.all_objects if o.type == "MESH" and not o.name.startswith(SKIP_PREFIX)]
        made = []
        for o in objs:
            for name, nm, mname in split_object(o):
                if not nm.vertices:
                    bpy.data.meshes.remove(nm)
                    continue
                xs = [v.co.x for v in nm.vertices]
                ys = [v.co.y for v in nm.vertices]
                zs = [v.co.z for v in nm.vertices]
                lo = Vector((min(xs), min(ys), min(zs)))
                hi = Vector((max(xs), max(ys), max(zs)))
                c = (lo + hi) / 2          # origem no CENTRO DO BBOX = MeshPart.Position no Roblox
                sz = hi - lo
                nm.transform(Matrix.Translation(-c))
                em = export_material(mname)
                if em is not None:
                    nm.materials.append(em)
                ob = bpy.data.objects.new(name, nm)
                ob.location = c
                tmp.objects.link(ob)
                made.append(ob)
                tris = len(nm.polygons)
                total += tris
                used[mname] = used.get(mname, 0) + 1
                data["meshes"].append({"name": name, "group": g, "material": mname, "tris": tris,
                                       "center_rbx": to_rbx(c),
                                       "size_rbx": [round(sz.x, 3), round(sz.z, 3), round(sz.y, 3)]})
        bpy.ops.object.select_all(action="DESELECT")
        for ob in made:
            ob.select_set(True)
        if made:
            bpy.context.view_layer.objects.active = made[0]
            path = os.path.join(OUT, "LOBBY_%s.fbx" % g)
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward="-Z", axis_up="Y",
                                     apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE", path_mode="COPY",
                                     embed_textures=True, add_leaf_bones=False, bake_anim=False,
                                     use_mesh_modifiers=True, object_types={"MESH"})
            print("FBX", g, len(made), "malhas", os.path.getsize(path) // 1024, "KB")
        for ob in made:
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.meshes.remove(me)
    bpy.data.collections.remove(tmp)
    # materiais: todos os que foram exportados (inclusive variantes e materiais novos de outros modulos)
    for mname in sorted(used):
        m = bpy.data.materials.get(mname)
        rm, tr, sh = rbx_rule(mname)
        swirl = mname if mname in TX.SWIRL_TEX else None
        data["materials"][mname] = {"color": rbx_color(mname, m), "material": rm, "transparency": tr,
                                    "shadow": sh, "family": family(mname), "tex": tex_of(mname),
                                    "swirl": swirl, "meshes": used[mname]}
    for k, (fn, tile) in sorted(TX.TEXTURES.items()):
        data["textures"][k] = {"file": "textures/" + fn, "studs_per_tile": tile}
    for k, (fn, arm, core) in sorted(TX.SWIRL_TEX.items()):
        data["textures"][k] = {"file": "textures/" + fn, "uv": "disco 0..1"}
    fg = dict(FAR_GROUND)
    fg["color"] = rbx_color(FAR_GROUND["material"])
    fg["pos"] = to_rbx((0, 0, FAR_GROUND["top_z"] - FAR_GROUND["size"][1] / 2))
    data["far_ground"] = fg
    # colisoes
    for o in bpy.data.objects:
        if o.name.startswith("COL_") and o.type == "MESH":
            R = o.matrix_world.to_3x3().normalized()
            data["collisions"].append({"name": o.name, "kind": o.get("col_kind", "Block"), "pos": to_rbx(o.location),
                                       "x": to_rbx(R.col[0]), "y": to_rbx(R.col[1]),
                                       "size": [round(s, 3) for s in o.scale]})
    # marcadores
    names = set()
    for o in bpy.data.objects:
        if o.type == "EMPTY" and any(o.users_collection) and o.users_collection[0].name == "15_GAMEPLAY_MARKERS":
            R = o.matrix_world.to_3x3().normalized()
            props = {}
            for k, v in o.items():
                if isinstance(v, (bool, int, float, str)):
                    props[k] = v
                else:
                    try:
                        props[k] = list(v)
                    except TypeError:
                        props[k] = str(v)
            names.add(o.name)
            data["markers"].append({"name": o.name, "pos": to_rbx(o.location), "x": to_rbx(R.col[0]),
                                    "y": to_rbx(R.col[1]), "props": props})
    if not any(n.startswith("SPAWN") for n in names):
        # o spawn so existia em fm_layout: marcador de referencia (nao e SpawnLocation para nao mexer no jogo)
        try:
            import fm_layout
            sp = fm_layout.SPAWN
        except Exception:
            sp = (0.0, -104.0, 0.0)
        data["markers"].append({"name": "SPAWN_Lobby", "pos": to_rbx((sp[0], sp[1], sp[2] + 3.0)),
                                "x": to_rbx((1, 0, 0)), "y": to_rbx((0, 1, 0)),
                                "props": {"kind": "spawn", "note": "chegada do lobby, de frente para a avenida (+Y Blender)"}})
    # luzes pontuais (Roblox PointLight/SpotLight): alcance/brilho calibrados no Studio (luz do dia Future)
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type in ("POINT", "SPOT"):
            e = o.data.energy
            rng0 = min(60, 8 + math.sqrt(e) * 1.1)
            br0 = min(4.0, 0.6 + e / 800.0)
            rng_, br = min(20.0, rng0 * 0.35), min(1.5, br0 * 0.5)
            if o.name.startswith("L_Portal_"):
                rng_, br = 14.0, 1.0
            L = {"name": o.name, "type": o.data.type, "pos": to_rbx(o.location), "color": srgb(o.data.color),
                 "range": round(rng_, 1), "brightness": round(br, 2),
                 "shadows": any(o.name.startswith(s) for s in SHADOW_LIGHTS)}
            if o.data.type == "SPOT":
                d = o.matrix_world.to_3x3() @ Vector((0, 0, -1))
                L["dir"] = to_rbx(d.normalized())
                L["angle"] = round(min(180.0, math.degrees(o.data.spot_size)), 1)
            data["lights"].append(L)
    json.dump(data, open(os.path.join(OUT, "lobby_data.json"), "w"), indent=1)
    write_lua(data)
    print("EXPORT OK malhas=%d tris=%d materiais=%d col=%d marcadores=%d luzes=%d -> %s" % (
        len(data["meshes"]), total, len(data["materials"]), len(data["collisions"]), len(data["markers"]),
        len(data["lights"]), OUT))


# ------------------------------------------------------------------ Lua
def lua_val(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(lua_val(x) for x in v) + "}"
    s = str(v).replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")
    return "'" + s + "'"


def lua_str(s):
    return lua_val(str(s))


def write_lua(data):
    L = []
    A = L.append
    A("-- montar_lobby_forja.lua  (gerado por export_roblox.py - nao editar a mao)")
    A("-- 1) Importe os FBX LOBBY_*.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA. Deixe o importador subir")
    A("--    as TEXTURAS embutidas (ele cria as imagens e poe em TextureID/SurfaceAppearance das MeshParts).")
    A("-- 2) Rode este script na Command Bar. Ele:")
    A("--    - ALINHA cada MeshPart na posicao certa (centro do bbox exportado), corrigindo deslocamento, giro de 180")
    A("--      graus e escala m->stud do importador (avisa se estiver ESPELHADO: ai tem que trocar no Blender);")
    A("--    - aplica cor/Material por VARIANTE (sufixo __Stone_Light_B etc.), CastShadow por familia e tamanho;")
    A("--    - RICO=true: textura de detalhe em SurfaceAppearance (AlphaMode Overlay) sobre a cor da variante;")
    A("--    - cria COLISOES invisiveis, MARCADORES (atributos), LUZES e o chao distante; APLICAR_LIGHTING opcional.")
    A("-- Rodar de novo e seguro (idempotente). Ids de textura encontrados sao impressos: cole em TEX para fixar.")
    A("local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloca o lobby INTEIRO (malhas alinhadas + colisoes + marcadores + luzes)")
    A("local ALINHAR = true      -- reposiciona as MeshParts pelos centros exportados (corrige o importador)")
    A("local RICO = false        -- true = texturas de detalhe (SurfaceAppearance Overlay) nas familias pedra/madeira/telha/rocha/grama/reboco/terra")
    A("local LISO = false        -- true = tudo SmoothPlastic (menos Neon/Metal/Glass), sem os materiais ricos do modo hibrido")
    A("local APLICAR_LIGHTING = false  -- true = aplica o Lighting recomendado do lobby (GLOBAL: prefira o perfil em AreaAtmosphere)")
    A("local root = workspace:FindFirstChild('LOBBY_FORJA') or Instance.new('Model', workspace)")
    A("root.Name = 'LOBBY_FORJA'")
    A("local function folder(n) local f = root:FindFirstChild(n) or Instance.new('Folder'); f.Name = n; f.Parent = root; return f end")
    A("local COLF, MKF, LTF = folder('COLLISION'), folder('GAMEPLAY_MARKERS'), folder('LIGHTS')")
    A("local function cf(p, x, y) local px = Vector3.new(p[1],p[2],p[3]) + ROOT_OFFSET")
    A("  local vx = Vector3.new(x[1],x[2],x[3]); local vy = Vector3.new(y[1],y[2],y[3])")
    A("  return CFrame.fromMatrix(px, vx, vy) end")
    # texturas
    A("-- ids das texturas (rbxassetid://...). Vazio = usa o que o 3D Importer subiu (lido das MeshParts).")
    A("-- Alternativa: suba as PNG de textures/ pelo Asset Manager e cole os ids aqui.")
    A("local TEX = {")
    for k, v in sorted(data["textures"].items()):
        A("  [%s] = '',  -- %s%s" % (lua_str(k), v["file"], (" (%s studs por repeticao)" % v["studs_per_tile"])
                                     if "studs_per_tile" in v else " (espiral, UV do disco)"))
    A("}")
    # materiais
    A("-- material/variante -> c = cor calibrada no Studio, m = Enum.Material (hibrido), t = transparencia,")
    A("--   s = CastShadow, x = textura de detalhe, w = espiral")
    A("local MAT = {")
    for k, v in sorted(data["materials"].items()):
        A("  [%s] = {c = Color3.fromRGB(%d,%d,%d), m = Enum.Material.%s, t = %s, s = %s, x = %s, w = %s}," % (
            lua_str(k), v["color"][0], v["color"][1], v["color"][2], v["material"], v["transparency"],
            lua_val(v["shadow"]), lua_str(v["tex"]) if v["tex"] else "nil",
            lua_str(v["swirl"]) if v["swirl"] else "nil"))
    A("}")
    A("local KEEP = {[Enum.Material.Neon]=true, [Enum.Material.Metal]=true, [Enum.Material.Glass]=true, [Enum.Material.CorrodedMetal]=true}")
    A("local function matOf(name)")
    A("  local s = string.match(name, '__(.+)$'); if not s then return nil end")
    A("  if MAT[s] then return MAT[s], s end")
    A("  local s2 = string.match(s, '^(.-)_%d+$')  -- fatia _0/_1")
    A("  if s2 and MAT[s2] then return MAT[s2], s2 end")
    A("  local best, bl = nil, 0   -- tolerante: maior prefixo conhecido (variantes/materiais novos)")
    A("  for k, v in pairs(MAT) do if #k > bl and string.sub(s, 1, #k) == k then best, bl = v, #k end end")
    A("  return best, s")
    A("end")
    # malhas esperadas (alinhamento)
    gidx = {g: i + 1 for i, g in enumerate(GROUPS)}
    A("-- malhas exportadas: nome = {centro X,Y,Z, tamanho X,Y,Z, FBX} (espaco Roblox, centro do bbox)")
    A("-- FBX: " + ", ".join("%d=LOBBY_%s" % (i, g) for g, i in gidx.items()))
    A("local MESH = {")
    for m in data["meshes"]:
        A("  [%s]={%s,%s,%s,%s,%s,%s,%d}," % (lua_str(m["name"]), *m["center_rbx"], *m["size_rbx"],
                                             gidx[m["group"]]))
    A("}")
    A(LUA_ALIGN)
    A(LUA_APPLY)
    # colisoes
    A("local COL = {")
    for c in data["collisions"]:
        A("  {%s,%s,{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},{%s,%s,%s}}," % (
            lua_str(c["name"]), lua_str(c["kind"]), *c["pos"], *c["x"], *c["y"], *c["size"]))
    A("}")
    A("COLF:ClearAllChildren()")
    A("for _, c in ipairs(COL) do")
    A("  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true")
    A("  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic")
    A("  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])")
    A("  p:SetAttribute('kind', c[2]); p.Parent = COLF")
    A("end")
    # marcadores
    A("local MK = {")
    for m in data["markers"]:
        props = ",".join("[%s]=%s" % (lua_str(k), lua_val(v)) for k, v in m["props"].items()
                         if not isinstance(v, (list, tuple)))
        A("  {%s,{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},{%s}}," % (lua_str(m["name"]), *m["pos"], *m["x"], *m["y"], props))
    A("}")
    A("MKF:ClearAllChildren()")
    A("for _, m in ipairs(MK) do")
    A("  local p = Instance.new('Part'); p.Name = m[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false")
    A("  p.CanTouch = false; p.Transparency = 1; p.Size = Vector3.new(1,1,1); p.CFrame = cf(m[2], m[3], m[4])")
    A("  for k, v in pairs(m[5]) do p:SetAttribute(k, v) end")
    A("  p.Parent = MKF")
    A("end")
    # luzes
    A("-- luzes: {nome, tipo, pos, cor, alcance, brilho, sombra, direcao(spot), angulo(spot)}")
    A("local LT = {")
    for l in data["lights"]:
        extra = ""
        if l["type"] == "SPOT":
            extra = ",{%s,%s,%s},%s" % (*l["dir"], l["angle"])
        A("  {%s,%s,{%s,%s,%s},{%d,%d,%d},%s,%s,%s%s}," % (
            lua_str(l["name"]), lua_str(l["type"]), *l["pos"], *l["color"], l["range"], l["brightness"],
            lua_val(l["shadows"]), extra))
    A("}")
    A("LTF:ClearAllChildren()")
    A("for _, l in ipairs(LT) do")
    A("  local a = Instance.new('Part'); a.Name = l[1]; a.Anchored = true; a.CanCollide = false; a.CanQuery = false")
    A("  a.CanTouch = false; a.Transparency = 1; a.Size = Vector3.new(0.5,0.5,0.5)")
    A("  local pos = Vector3.new(l[3][1], l[3][2], l[3][3]) + ROOT_OFFSET")
    A("  if l[2] == 'SPOT' and l[8] then a.CFrame = CFrame.lookAt(pos, pos + Vector3.new(l[8][1], l[8][2], l[8][3])) else a.CFrame = CFrame.new(pos) end")
    A("  local pl = Instance.new(l[2] == 'SPOT' and 'SpotLight' or 'PointLight')")
    A("  pl.Color = Color3.fromRGB(l[4][1], l[4][2], l[4][3]); pl.Range = l[5]; pl.Brightness = l[6]; pl.Shadows = l[7]")
    A("  if l[2] == 'SPOT' then pl.Face = Enum.NormalId.Front; if l[9] then pl.Angle = l[9] end end")
    A("  pl.Parent = a; a.Parent = LTF")
    A("end")
    # chao distante
    fg = data["far_ground"]
    A("-- chao do vale distante (o plano de 2400 studs do Blender): sem ele o lobby flutua sobre o skybox")
    A("do local g = root:FindFirstChild('FAR_GROUND') or Instance.new('Part'); g.Name = 'FAR_GROUND'")
    A("  g.Anchored = true; g.CanCollide = false; g.CanTouch = false; g.CanQuery = false; g.CastShadow = false")
    A("  g.Size = Vector3.new(%s,%s,%s); g.Position = Vector3.new(%s,%s,%s) + ROOT_OFFSET" % (
        *fg["size"], *fg["pos"]))
    A("  g.Color = Color3.fromRGB(%d,%d,%d); g.Material = LISO and Enum.Material.SmoothPlastic or Enum.Material.Grass; g.Parent = root end" % tuple(fg["color"]))
    # lighting
    A(lua_lighting(data["lighting_lobby"]))
    A("print('LOBBY_FORJA montado:', #COL, 'colisoes', #MK, 'marcadores', #LT, 'luzes')")
    src = "\n".join(L) + "\n"
    open(os.path.join(OUT, "montar_lobby_forja.lua"), "w", encoding="utf-8").write(src)


LUA_ALIGN = r"""
-- ALINHAMENTO: compara as MeshParts importadas com MESH (Procrustes discreto no plano XZ) e corrige
local function coletar()
  local parts = {}
  for _, d in ipairs(root:GetDescendants()) do
    if d:IsA('MeshPart') and MESH[d.Name] then table.insert(parts, d) end
  end
  return parts
end
local function alinhar()
  local parts = coletar()
  local nExp = 0; for _ in pairs(MESH) do nExp += 1 end
  print(string.format('ALINHAR: %d de %d malhas encontradas pelo nome', #parts, nExp))
  if #parts < 3 then warn('ALINHAR: poucas MeshParts com nome conhecido - confira se o importador manteve os nomes'); return end
  -- centroides POR FBX (grupo): tolera o importador recentralizar cada arquivo separadamente
  local G = {}
  for _, p in ipairs(parts) do local e = MESH[p.Name]
    local g = G[e[7]]; if not g then g = {ca = Vector3.zero, ce = Vector3.zero, n = 0}; G[e[7]] = g end
    g.ca += p.Position; g.ce += Vector3.new(e[1], e[2], e[3]); g.n += 1 end
  for _, g in pairs(G) do g.ca /= g.n; g.ce /= g.n end
  local function rel(p) local e = MESH[p.Name]; local g = G[e[7]]
    return p.Position - g.ca, Vector3.new(e[1], e[2], e[3]) - g.ce end
  local sa, se = 0, 0
  for _, p in ipairs(parts) do local a, b = rel(p); sa += a.Magnitude; se += b.Magnitude end
  local escala = (se > 0) and (sa / se) or 1
  local best, bestErr, bestMirror = 0, math.huge, false
  for _, mir in ipairs({false, true}) do
    for k = 0, 3 do
      local R = CFrame.Angles(0, k * math.pi / 2, 0); local err = 0
      for _, p in ipairs(parts) do
        local a, b = rel(p)
        if mir then b = Vector3.new(-b.X, b.Y, b.Z) end
        err += (a - R:VectorToWorldSpace(b) * escala).Magnitude
      end
      if err < bestErr then best, bestErr, bestMirror = k, err, mir end
    end
  end
  if bestMirror then warn('ALINHAR: o importador ESPELHOU o lobby. Nao da para corrigir aqui: troque a matriz T no export_roblox.py / eixos do FBX.') end
  if best ~= 0 then warn(string.format('ALINHAR: importador girou %d graus em Y - corrigindo', best * 90)) end
  if math.abs(escala - 1) > 0.05 then warn(string.format('ALINHAR: escala do importador %.3f (m->stud?) - corrigindo Size', escala)) end
  local Rinv = CFrame.Angles(0, -best * math.pi / 2, 0)
  for _, p in ipairs(parts) do local e = MESH[p.Name]
    if math.abs(escala - 1) > 0.05 then p.Size = p.Size / escala end
    local rot = p.CFrame - p.CFrame.Position
    p.CFrame = CFrame.new(Vector3.new(e[1], e[2], e[3]) + ROOT_OFFSET) * Rinv * rot
  end
  print(string.format('ALINHAR: ok (giro %d, escala %.3f, espelho %s)', best * 90, escala, tostring(bestMirror)))
end
if ALINHAR then alinhar() end
"""

LUA_APPLY = r"""
-- texturas: le os ids que o 3D Importer subiu (TextureID ou SurfaceAppearance) por familia
local function lerMapa(d)
  local ok, v = pcall(function() return d.TextureID end)
  if ok and v and v ~= '' then return v end
  local sa = d:FindFirstChildOfClass('SurfaceAppearance')
  if sa then
    local ok2, v2 = pcall(function() return sa.ColorMap end)
    if ok2 and v2 and v2 ~= '' then return v2 end
    local ok3, v3 = pcall(function() return sa.ColorMapContent.Uri end)
    if ok3 and v3 and v3 ~= '' then return v3 end
  end
  return nil
end
local function porMapa(sa, id)
  local ok = pcall(function() sa.ColorMap = id end)
  if not ok then ok = pcall(function() sa.ColorMapContent = Content.fromUri(id) end) end
  return ok
end
local achados = {}
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local e = matOf(d.Name)
    local key = e and (e.w or e.x)
    if key and (TEX[key] == nil or TEX[key] == '') then
      local id = lerMapa(d)
      if id then TEX[key] = id; achados[key] = id end
    end
  end
end
for k, v in pairs(achados) do print('TEX encontrada', k, v) end
-- aplica cor/material/sombra/textura por variante
local nOk, nSem, nTex = 0, 0, 0
for _, d in ipairs(root:GetDescendants()) do
  if d:IsA('MeshPart') then
    local e = matOf(d.Name)
    d.Anchored = true; d.CanCollide = false; d.CanTouch = false; d.CanQuery = false
    if e then
      nOk += 1
      d.Color = e.c; d.Transparency = e.t
      d.Material = (LISO and not KEEP[e.m]) and Enum.Material.SmoothPlastic or e.m
      d.CastShadow = e.s and (d.Size.Magnitude > 4)
      local sa = d:FindFirstChildOfClass('SurfaceAppearance')
      local sw = e.w and TEX[e.w] or ''
      local tx = e.x and TEX[e.x] or ''
      if e.w and sw ~= '' then
        -- espiral do portal: textura sempre (sem ela o disco vira um circulo chapado)
        if sa then sa:Destroy() end
        d.TextureID = sw; d.Material = Enum.Material.SmoothPlastic; nTex += 1
      elseif RICO and tx ~= '' then
        d.TextureID = ''
        if not sa then sa = Instance.new('SurfaceAppearance') end
        sa.AlphaMode = Enum.AlphaMode.Overlay
        if porMapa(sa, tx) then sa.Parent = d; nTex += 1
        else sa:Destroy(); d.TextureID = tx; nTex += 1 end
      else
        d.TextureID = ''
        if sa then sa:Destroy() end
      end
    else
      nSem += 1
    end
  end
end
print(string.format('MATERIAIS: %d MeshParts com variante reconhecida, %d sem (ficaram como vieram), %d texturizadas', nOk, nSem, nTex))
"""


def lua_lighting(cfg):
    L = ["if APLICAR_LIGHTING then", "  local Lg = game:GetService('Lighting')"]
    for k, v in cfg["Lighting"].items():
        if isinstance(v, list):
            L.append("  Lg.%s = Color3.fromRGB(%d,%d,%d)" % (k, *v))
        else:
            L.append("  Lg.%s = %s" % (k, v))
    for cls, props in cfg.items():
        if cls == "Lighting":
            continue
        L.append("  do local e = Lg:FindFirstChildOfClass('%s') or Instance.new('%s', Lg)" % (cls, cls))
        for k, v in props.items():
            if isinstance(v, list):
                L.append("    e.%s = Color3.fromRGB(%d,%d,%d)" % (k, *v))
            else:
                L.append("    e.%s = %s" % (k, v))
        L.append("  end")
    L.append("  print('Lighting do lobby aplicado (lembre de devolver GeographicLatitude=22 nos perfis das ilhas)')")
    L.append("end")
    return "\n".join(L)


if __name__ == "__main__":
    main()
