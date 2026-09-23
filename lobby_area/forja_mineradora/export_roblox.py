# export_roblox.py - prepara o lobby para o Roblox Studio
# uso: blender -b lobby_forja_mineradora.blend --python export_roblox.py
# saida em ./export/:
#   LOBBY_<colecao>.fbx      malhas visuais, 1 material por malha, <= 18k tris por malha, origem no centro
#   lobby_data.json          colisoes (COL_), marcadores, luzes, tabela de materiais
#   montar_lobby_forja.lua   script (Command Bar / plugin) que monta colisoes, marcadores, luzes e aplica materiais
import sys, os, json, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector, Matrix

OUT = os.path.join(HERE, "export")
os.makedirs(OUT, exist_ok=True)
MAX_TRIS = 18000
GROUPS = ["02_TERRAIN", "03_FORGE", "04_MINE", "05_WATER_SYSTEM", "06_PORTALS", "07_BUILDINGS", "08_PROPS",
          "09_VEGETATION", "10_RAILS"]
SKIP_PREFIX = ("COL_", "SCALE_", "BLK_", "SKY_", "VFX_", "TER_Far_Valley")

# Blender (x, y, z) -> FBX(-Z fwd, Y up) -> Roblox (x, z, -y). Mesmo mapeamento para colisoes/marcadores.
T = Matrix(((1, 0, 0), (0, 0, 1), (0, -1, 0)))


def to_rbx(v):
    v = T @ Vector(v)
    return [round(v.x, 3), round(v.y, 3), round(v.z, 3)]


# material -> (Enum.Material estilizado, material "rico" alternativo, transparencia)
def rbx_material(name):
    n = name.lower()
    if any(k in n for k in ("swirl", "glow", "emissive", "lantern", "crystal", "neon", "heated")):
        return "Neon", "Neon", 0.0
    if n.startswith("water_fall") or n == "foam":
        return "Neon", "Neon", 0.15
    if n == "water":
        return "Glass", "Glass", 0.35
    if "glass" in n:
        return "Glass", "Glass", 0.2
    if n.startswith("grass"):
        return "SmoothPlastic", "Grass", 0.0
    if n.startswith(("leaf", "bark")):
        return "SmoothPlastic", "Grass" if n.startswith("leaf") else "Wood", 0.0
    if n.startswith("wood") or n == "rope":
        return "SmoothPlastic", "WoodPlanks" if "plank" in n else "Wood", 0.0
    if n.startswith("metal") or "gold" in n:
        return "Metal", "Metal", 0.0
    if n.startswith(("stone_paving",)):
        return "SmoothPlastic", "Cobblestone", 0.0
    if n.startswith(("stone", "cliff")):
        return "SmoothPlastic", "Slate", 0.0
    if n.startswith("roof"):
        return "SmoothPlastic", "RoofShingles", 0.0
    if n.startswith("plaster"):
        return "SmoothPlastic", "Plaster", 0.0
    if n.startswith("cloth") or n.startswith("p_") and "red" in n:
        return "SmoothPlastic", "Fabric", 0.0
    return "SmoothPlastic", "SmoothPlastic", 0.0


def srgb(c):
    out = []
    for x in c[:3]:
        x = max(0.0, min(1.0, x))
        out.append(int(round(255 * (x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055))))
    return out


def base_color(mat):
    import fm_lib
    if mat.name in fm_lib.MATS:
        return fm_lib.MATS[mat.name][0]
    return tuple(mat.diffuse_color)[:3]


def split_object(ob):
    """retorna lista de (nome, mesh) - um por material, fatiado se passar de MAX_TRIS"""
    res = []
    me = ob.data
    mw = ob.matrix_world
    bm_all = bmesh.new()
    bm_all.from_mesh(me)
    bm_all.transform(mw)
    bmesh.ops.triangulate(bm_all, faces=bm_all.faces[:])
    bm_all.verts.index_update()
    by_mat = {}
    for f in bm_all.faces:
        by_mat.setdefault(f.material_index, []).append(f)
    for mi, faces in by_mat.items():
        mname = me.materials[mi].name if mi < len(me.materials) else "Default"
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
            vmap = {}
            for f in c:
                vs = []
                for v in f.verts:
                    if v.index not in vmap:
                        vmap[v.index] = bm.verts.new(v.co)
                    vs.append(vmap[v.index])
                try:
                    bm.faces.new(vs)
                except ValueError:
                    pass
            bm.verts.index_update()
            name = "%s__%s" % (ob.name, mname) + ("_%d" % k if len(chunks) > 1 else "")
            nm = bpy.data.meshes.new(name)
            bm.to_mesh(nm)
            bm.free()
            nm.materials.append(me.materials[mi] if mi < len(me.materials) else None)
            res.append((name, nm, mname))
    bm_all.free()
    return res


def main():
    data = {"mapping": "Roblox = (x_blender, z_blender, -y_blender); 1 BU = 1 stud", "meshes": [], "materials": {},
            "collisions": [], "markers": [], "lights": []}
    tmp = bpy.data.collections.new("_EXPORT_TMP")
    bpy.context.scene.collection.children.link(tmp)
    total = 0
    for g in GROUPS:
        col = bpy.data.collections.get(g)
        if not col:
            continue
        objs = [o for o in col.all_objects if o.type == "MESH" and not o.name.startswith(SKIP_PREFIX)]
        made = []
        for o in objs:
            for name, nm, mname in split_object(o):
                # origem no centro do bbox
                cs = [v.co for v in nm.vertices]
                if not cs:
                    continue
                c = sum(cs, Vector()) / len(cs)
                nm.transform(Matrix.Translation(-c))
                ob = bpy.data.objects.new(name, nm)
                ob.location = c
                tmp.objects.link(ob)
                made.append(ob)
                tris = len(nm.polygons)
                total += tris
                data["meshes"].append({"name": name, "group": g, "material": mname, "tris": tris,
                                       "center_rbx": to_rbx(c)})
        bpy.ops.object.select_all(action="DESELECT")
        for ob in made:
            ob.select_set(True)
        if made:
            bpy.context.view_layer.objects.active = made[0]
            path = os.path.join(OUT, "LOBBY_%s.fbx" % g)
            bpy.ops.export_scene.fbx(filepath=path, use_selection=True, axis_forward="-Z", axis_up="Y",
                                     apply_scale_options="FBX_SCALE_ALL", mesh_smooth_type="FACE", path_mode="COPY",
                                     embed_textures=False, add_leaf_bones=False, bake_anim=False,
                                     use_mesh_modifiers=True, object_types={"MESH"})
            print("FBX", g, len(made), "malhas", os.path.getsize(path) // 1024, "KB")
        for ob in made:
            me = ob.data
            bpy.data.objects.remove(ob, do_unlink=True)
            bpy.data.meshes.remove(me)
    bpy.data.collections.remove(tmp)
    # materiais
    for m in bpy.data.materials:
        if not m.users:
            continue
        styl, rich, tr = rbx_material(m.name)
        data["materials"][m.name] = {"color": srgb(base_color(m)), "material": styl, "material_rico": rich,
                                     "transparency": tr}
    # colisoes
    for o in bpy.data.objects:
        if o.name.startswith("COL_") and o.type == "MESH":
            R = o.matrix_world.to_3x3().normalized()
            data["collisions"].append({"name": o.name, "kind": o.get("col_kind", "Block"), "pos": to_rbx(o.location),
                                       "x": to_rbx(R.col[0]), "y": to_rbx(R.col[1]),
                                       "size": [round(s, 3) for s in o.scale]})
    # marcadores
    for o in bpy.data.objects:
        if o.type == "EMPTY" and any(o.users_collection) and o.users_collection[0].name == "15_GAMEPLAY_MARKERS":
            R = o.matrix_world.to_3x3().normalized()
            props = {k: (v if isinstance(v, (int, float, str)) else str(v)) for k, v in o.items()}
            data["markers"].append({"name": o.name, "pos": to_rbx(o.location), "x": to_rbx(R.col[0]),
                                    "y": to_rbx(R.col[1]), "props": props})
    # luzes pontuais (Roblox PointLight/SpotLight): alcance aproximado pela energia
    for o in bpy.data.objects:
        if o.type == "LIGHT" and o.data.type in ("POINT", "SPOT"):
            e = o.data.energy
            data["lights"].append({"name": o.name, "type": o.data.type, "pos": to_rbx(o.location),
                                   "color": srgb(o.data.color), "range": round(min(60, 8 + math.sqrt(e) * 1.1), 1),
                                   "brightness": round(min(4.0, 0.6 + e / 800.0), 2)})
    json.dump(data, open(os.path.join(OUT, "lobby_data.json"), "w"), indent=1)
    write_lua(data)
    print("EXPORT OK malhas=%d tris=%d col=%d marcadores=%d luzes=%d" % (
        len(data["meshes"]), total, len(data["collisions"]), len(data["markers"]), len(data["lights"])))


def lua_vec(v):
    return "Vector3.new(%s,%s,%s)" % tuple(v)


def write_lua(data):
    L = []
    L.append("-- montar_lobby_forja.lua  (gerado por export_roblox.py - nao editar a mao)")
    L.append("-- 1) Importe os FBX LOBBY_*.fbx (3D Importer) para dentro de workspace.LOBBY_FORJA (mantenha as posicoes).")
    L.append("-- 2) Rode este script na Command Bar. Ele cria COLISOES invisiveis, MARCADORES, LUZES e aplica os materiais.")
    L.append("local ROOT_OFFSET = Vector3.new(0, 0, 0)  -- desloque o lobby inteiro aqui (em studs)")
    L.append("local RICO = false  -- true = materiais texturizados (Slate, WoodPlanks...), false = estilizado (SmoothPlastic)")
    L.append("local root = workspace:FindFirstChild('LOBBY_FORJA') or Instance.new('Model', workspace)")
    L.append("root.Name = 'LOBBY_FORJA'")
    L.append("local function folder(n) local f = root:FindFirstChild(n) or Instance.new('Folder'); f.Name = n; f.Parent = root; return f end")
    L.append("local COLF, MKF, LTF = folder('COLLISION'), folder('GAMEPLAY_MARKERS'), folder('LIGHTS')")
    L.append("local function cf(p, x, y) local px = Vector3.new(p[1],p[2],p[3]) + ROOT_OFFSET")
    L.append("  local vx = Vector3.new(x[1],x[2],x[3]); local vy = Vector3.new(y[1],y[2],y[3])")
    L.append("  return CFrame.fromMatrix(px, vx, vy) end")
    # materiais
    L.append("local MAT = {")
    for k, v in sorted(data["materials"].items()):
        L.append("  [%r] = {c = Color3.fromRGB(%d,%d,%d), m = Enum.Material.%s, r = Enum.Material.%s, t = %s}," % (
            k, v["color"][0], v["color"][1], v["color"][2], v["material"], v["material_rico"], v["transparency"]))
    L.append("}")
    L.append("for _, d in ipairs(root:GetDescendants()) do")
    L.append("  if d:IsA('MeshPart') then")
    L.append("    local mat = string.match(d.Name, '__(.-)_%d+$') or string.match(d.Name, '__(.+)$')")
    L.append("    local e = mat and MAT[mat]")
    L.append("    d.Anchored = true; d.CanCollide = false; d.CanTouch = false; d.CanQuery = false; d.CastShadow = true")
    L.append("    if e then d.Color = e.c; d.Material = RICO and e.r or e.m; d.Transparency = e.t; d.TextureID = '' end")
    L.append("  end")
    L.append("end")
    # colisoes
    L.append("local COL = {")
    for c in data["collisions"]:
        L.append("  {%r,%r,{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},{%s,%s,%s}}," % (
            c["name"], c["kind"], *c["pos"], *c["x"], *c["y"], *c["size"]))
    L.append("}")
    L.append("COLF:ClearAllChildren()")
    L.append("for _, c in ipairs(COL) do")
    L.append("  local p = Instance.new('Part'); p.Name = c[1]; p.Anchored = true; p.CanCollide = true")
    L.append("  p.Transparency = 1; p.CastShadow = false; p.CanTouch = false; p.Material = Enum.Material.SmoothPlastic")
    L.append("  p.Size = Vector3.new(c[6][1], c[6][2], c[6][3]); p.CFrame = cf(c[3], c[4], c[5])")
    L.append("  p:SetAttribute('kind', c[2]); p.Parent = COLF")
    L.append("end")
    # marcadores
    L.append("local MK = {")
    for m in data["markers"]:
        props = ",".join("[%r]=%s" % (k, (repr(v) if isinstance(v, str) else v)) for k, v in m["props"].items())
        L.append("  {%r,{%s,%s,%s},{%s,%s,%s},{%s,%s,%s},{%s}}," % (m["name"], *m["pos"], *m["x"], *m["y"], props))
    L.append("}")
    L.append("MKF:ClearAllChildren()")
    L.append("for _, m in ipairs(MK) do")
    L.append("  local p = Instance.new('Part'); p.Name = m[1]; p.Anchored = true; p.CanCollide = false; p.CanQuery = false")
    L.append("  p.Transparency = 1; p.Size = Vector3.new(1,1,1); p.CFrame = cf(m[2], m[3], m[4])")
    L.append("  for k, v in pairs(m[5]) do p:SetAttribute(k, v) end")
    L.append("  p.Parent = MKF")
    L.append("end")
    # luzes
    L.append("local LT = {")
    for l in data["lights"]:
        L.append("  {%r,%r,{%s,%s,%s},{%d,%d,%d},%s,%s}," % (l["name"], l["type"], *l["pos"], *l["color"], l["range"],
                                                           l["brightness"]))
    L.append("}")
    L.append("LTF:ClearAllChildren()")
    L.append("for _, l in ipairs(LT) do")
    L.append("  local a = Instance.new('Part'); a.Name = l[1]; a.Anchored = true; a.CanCollide = false; a.CanQuery = false")
    L.append("  a.CanTouch = false; a.Transparency = 1; a.Size = Vector3.new(0.5,0.5,0.5)")
    L.append("  a.Position = Vector3.new(l[3][1], l[3][2], l[3][3]) + ROOT_OFFSET")
    L.append("  local pl = Instance.new(l[2] == 'SPOT' and 'SpotLight' or 'PointLight')")
    L.append("  pl.Color = Color3.fromRGB(l[4][1], l[4][2], l[4][3]); pl.Range = l[5]; pl.Brightness = l[6]; pl.Shadows = false")
    L.append("  pl.Parent = a; a.Parent = LTF")
    L.append("end")
    L.append("print('LOBBY_FORJA montado:', #COL, 'colisoes', #MK, 'marcadores', #LT, 'luzes')")
    src = "\n".join(L) + "\n"
    open(os.path.join(OUT, "montar_lobby_forja.lua"), "w", encoding="utf-8").write(src)


if __name__ == "__main__":
    main()
