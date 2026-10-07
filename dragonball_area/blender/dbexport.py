# Vale Capsule export:
#   export/dragonball_kit.fbx  -> K_<asset> models (textured MeshParts), imported once through Studio's 3D importer
#   export/dragonball_map.fbx  -> G_<group> models (unique map meshes: terrain, quarry, paths...)
#   export/dragonball_build.lua -> pasted in the command bar: recolours meshes, adds collision/decor Parts,
#                                  clones kit instances and assembles ServerStorage.DragonBallArea
import bpy, os, math
from mathutils import Matrix, Vector
import klib, meshkit

ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up\dragonball_area"
EXP = ROOT + r"\export"
M3 = Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0)))
RSHAPES = {'RBX_Block': 'B', 'RBX_Cylinder': 'C', 'RBX_Ball': 'A', 'RBX_Wedge': 'W', 'RBX_Corner': 'K'}
EXTRA_ASSETS = ['Arvore_Konoha_G', 'Arvore_Konoha_M', 'Arvore_Konoha_Gigante', 'Cedro_Konoha']   # used by KonohaIsland
DECO = ('text', 'textcolor', 'emblem', 'emblemface', 'ink', 'light', 'fx', 'swirl', 'fa', 'fb')
TOPS = ['DRAGONBALL_TERRAIN', 'DRAGONBALL_BUILDINGS', 'DRAGONBALL_LANDMARKS', 'DRAGONBALL_MINING', 'DRAGONBALL_ROCKS',
        'DRAGONBALL_NATURE', 'DRAGONBALL_DECORATION', 'DRAGONBALL_CAPSULE_TECH', 'DRAGONBALL_PROPS']

def f(v, d=2):
    s = ('%.' + str(d) + 'f') % v
    s = s.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def clean(s):
    return str(s).replace('|', '/').replace('\n', ' ').replace(']==]', '')

def xform(mw):
    """Blender world matrix -> (roblox pos, quat, size) for a unit primitive."""
    t = M3 @ mw.to_translation()
    b3 = mw.to_3x3()
    cols = [Vector((b3[0][i], b3[1][i], b3[2][i])) for i in range(3)]
    s = [c.length for c in cols]
    R = Matrix([[cols[j][i]/s[j] for j in range(3)] for i in range(3)])
    q = (M3 @ R @ M3.transposed()).to_quaternion()
    return t, q, (s[0], s[2], s[1])

def part_lines(items):
    out = []
    for o, mw in items:
        if o.get('pal'): continue
        shape = RSHAPES.get(o.data.name.split('.')[0])
        if not shape: continue
        mat = meshkit._mat(o); key = meshkit._key(mat)
        if not key: continue
        t, q, size = xform(mw)
        deco = ';'.join('%s=%s' % (k, clean(o[k])) for k in o.keys() if k in DECO)
        col = bool(o.get('col'))
        def line(kind_key, c, name, attrs, sz):
            return '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%d|%s|%s' % (
                shape, f(t.x), f(t.y), f(t.z), f(max(sz[0], .05)), f(max(sz[1], .05)), f(max(sz[2], .05)),
                f(q.x, 4), f(q.y, 4), f(q.z, 4), f(q.w, 4), kind_key, 1 if c else 0, clean(name), attrs)
        if key in meshkit.PART_ONLY:
            if key == 'invisible' and not col: continue
            out.append(line(key, col, o.name.split('.')[0], deco, size))
            continue
        if col:
            out.append(line('invisible', True, o.name.split('.')[0], '', size))
        if deco:
            sz = list(size)
            i = sz.index(min(sz)); sz[i] += .08
            out.append(line('anchor', False, o.name.split('.')[0], deco, sz))
    return out

def _origin_marker(name, target, parent):
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=.2)
    ob = meshkit._new_obj(name + '__origem', bm, target, parent, bpy.data.materials['DB_Palette'], 40)
    meshkit.bake_uv(ob, 'cc_white')
    return ob

def _rename_splits(meshes):
    for m in meshes:
        if '~' in m.name: continue
        base, _, tail = m.name.rpartition('__')
        parts = tail.split('_')
        # split_big appends _0/_1 suffixes; move them behind '~'
        suf = []
        while parts and parts[-1] in ('0', '1'):
            suf.insert(0, parts.pop())
        if suf:
            m.name = '%s__%s~%s' % (base, '_'.join(parts), ''.join(suf))

def used_assets():
    names = set()
    def walk(c):
        for o in c.objects:
            if o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection:
                names.add(o.instance_collection.name)
        for ch in c.children: walk(ch)
    for t in TOPS: walk(bpy.data.collections[t])
    names.update(EXTRA_ASSETS)
    return sorted(names)

def build_meshes(kit=True, mapg=True, only=None):
    pal = meshkit.build_palette()
    stats = {}
    if kit:
        K = klib.coll('EXPORT_KIT'); klib.clear_collection(K)
        for a in (only or used_assets()):
            sub = bpy.data.collections.new('MK_' + a); K.children.link(sub)
            root, tris, meshes = meshkit.convert('K_' + a, meshkit.asset_items(a), sub, pal, root_name='K_' + a)
            _rename_splits(meshes)
            _origin_marker('K_' + a, sub, root)
            stats['K_' + a] = (tris, len(meshes))
    if mapg:
        Mc = klib.coll('EXPORT_MAP'); klib.clear_collection(Mc)
        for gname, path, items, inst in map_groups():
            vis = [(o, mw) for (o, mw) in items if o.get('pal') or meshkit._key(meshkit._mat(o)) not in meshkit.PART_ONLY]
            if not vis: continue
            root, tris, meshes = meshkit.convert(gname, vis, Mc, pal, root_name=gname)
            _rename_splits(meshes)
            _origin_marker(gname, Mc, root)
            stats[gname] = (tris, len(meshes))
    return stats

def map_groups():
    out = []
    def walk(c, path):
        direct = [(o, o.matrix_world.copy()) for o in c.objects if o.type == 'MESH']
        inst = [o for o in c.objects if o.type == 'EMPTY' and o.instance_type == 'COLLECTION' and o.instance_collection]
        if direct or inst:
            out.append(('G_' + '_'.join(path), '/'.join(path), direct, inst))
        for ch in c.children: walk(ch, path + [ch.name])
    for t in TOPS: walk(bpy.data.collections[t], [t])
    return out

def export_fbx(coll_name, path):
    bpy.ops.object.select_all(action='DESELECT')
    c = bpy.data.collections[coll_name]
    obs = list(c.all_objects)
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'EMPTY', 'MESH'}, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_ALL', global_scale=1.0, axis_forward='-Z', axis_up='Y',
                             mesh_smooth_type='FACE', add_leaf_bones=False, path_mode='COPY', embed_textures=True)
    return os.path.getsize(path)

def write_lua(path, name='DragonBallArea'):
    lines = []
    for k in sorted(klib.PALETTE.keys()):
        rgb, rmat, flags = klib.PALETTE[k]
        lines.append('M|%s|%d,%d,%d|%s|%s' % (k, rgb[0], rgb[1], rgb[2], rmat, flags))
    for a in used_assets():
        lines.append('T|' + a)
        lines += part_lines(meshkit.asset_items(a))
    n_inst = 0
    for gname, path_, items, inst in map_groups():
        lines.append('G|%s|%s' % (gname, path_))
        lines += part_lines(items)
        for e in inst:
            t, q, size = xform(e.matrix_world)
            s = e.matrix_world.to_scale().x
            lines.append('I|%s|%s|%s|%s|%s|%s|%s|%s|%s' % (e.instance_collection.name, f(t.x), f(t.y), f(t.z),
                                                          f(q.x, 4), f(q.y, 4), f(q.z, 4), f(q.w, 4), f(s, 3)))
            n_inst += 1
    gp = bpy.data.collections.get('DRAGONBALL_GAMEPLAY')
    marks = 0
    if gp:
        for o in gp.objects:
            if o.name.startswith('GP_'):
                t = M3 @ o.matrix_world.to_translation()
                props = ';'.join('%s=%s' % (k, clean(o[k])) for k in o.keys())
                lines.append('P|%s|%s|%s|%s|%s' % (o.name.split('.')[0], f(t.x), f(t.y), f(t.z), props))
                marks += 1
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('local D=[==[\n' + '\n'.join(lines) + '\n]==]\n')
        fh.write(BUILDER % name)
    return len(lines), n_inst, marks, os.path.getsize(path)

BUILDER = r'''
local NAME="%s"
local SS=game:GetService("ServerStorage")
local store=SS:FindFirstChild("DragonBallMeshes")
if not store then store=Instance.new("Folder") store.Name="DragonBallMeshes" store.Parent=SS end
for _,n in {"dragonball_kit","dragonball_map"} do
 local m=workspace:FindFirstChild(n)
 if m then local old=store:FindFirstChild(n) if old then old:Destroy() end m.Parent=store end
end
local kitSrc,mapSrc=store:FindFirstChild("dragonball_kit"),store:FindFirstChild("dragonball_map")
assert(kitSrc and mapSrc,"[DragonBall] importe dragonball_kit.fbx e dragonball_map.fbx antes")
local mats={}
for line in D:gmatch("[^\n]+") do
 local p=line:split("|")
 if p[1]=="M" then local c=p[3]:split(",") mats[p[2]]={Color3.fromRGB(tonumber(c[1]),tonumber(c[2]),tonumber(c[3])),Enum.Material[p[4]],p[5] or ""} end
end
-- palette texture (one image shared by every textured mesh)
local palTex=""
for _,d in store:GetDescendants() do if d:IsA("MeshPart") and d.TextureID~="" then palTex=d.TextureID break end end
local function keyOf(n) local k=n:match("__(.+)$") or "" k=k:gsub("~.*$",""):gsub("%%.%%d+$","") return k end
local origins={}
for _,d in store:GetDescendants() do
 if d:IsA("MeshPart") then
  local k=keyOf(d.Name)
  d.Anchored=true d.CanCollide=false d.CanQuery=false d.CanTouch=false
  pcall(function() d.CollisionFidelity=Enum.CollisionFidelity.Box end)
  if k=="origem" then origins[d.Parent]=d.Position d.Transparency=1
  elseif k=="pal" then d.Color=Color3.new(1,1,1) d.Material=Enum.Material.SmoothPlastic if d.TextureID=="" then d.TextureID=palTex end d.CastShadow=true
  elseif mats[k] then local m=mats[k] d.TextureID="" d.Color=m[1] d.Material=m[2] d.CastShadow=not m[3]:find("n")
   if m[3]:find("g") then d.Transparency=.35 end
  end
 end
end
local old=SS:FindFirstChild(NAME) if old then old:Destroy() end
local oldKit=SS:FindFirstChild("DragonBallKit") if oldKit then oldKit:Destroy() end
local kit=Instance.new("Folder") kit.Name="DragonBallKit"
local root=Instance.new("Model") root.Name=NAME
local nodes={}
local function node(path)
 if nodes[path] then return nodes[path] end
 local parent,name=root,path
 local cut=path:match("^.*()/")
 if cut then parent=node(path:sub(1,cut-1)) name=path:sub(cut+1) end
 local m=Instance.new(parent==root and "Folder" or "Model") m.Name=name m.Parent=parent
 nodes[path]=m return m
end
local function stripOrigin(model)
 local o
 for _,d in model:GetDescendants() do if d:IsA("MeshPart") and keyOf(d.Name)=="origem" then o=o or d.Position d:Destroy() end end
 if not o then warn("[DragonBall] sem marcador de origem em",model.Name) o=Vector3.zero end
 model.WorldPivot=CFrame.new(o)
 return o
end
local function mkPart(p,base)
 local k=p[1] local inst
 if k=="W" then inst=Instance.new("WedgePart") elseif k=="K" then inst=Instance.new("CornerWedgePart") else
  inst=Instance.new("Part") inst.Shape=k=="C" and Enum.PartType.Cylinder or k=="A" and Enum.PartType.Ball or Enum.PartType.Block end
 inst.Anchored=true inst.TopSurface=Enum.SurfaceType.Smooth inst.BottomSurface=Enum.SurfaceType.Smooth
 inst.Size=Vector3.new(tonumber(p[5]),tonumber(p[6]),tonumber(p[7]))
 inst.CFrame=base*CFrame.new(tonumber(p[2]),tonumber(p[3]),tonumber(p[4]),tonumber(p[8]),tonumber(p[9]),tonumber(p[10]),tonumber(p[11]))
 local mk=p[12] local col=p[13]=="1"
 inst.CanCollide=col inst.CanQuery=col inst.CanTouch=false inst.CastShadow=false
 if mk=="invisible" or mk=="anchor" then inst.Transparency=1
 else local m=mats[mk] if m then inst.Color=m[1] inst.Material=m[2] if m[3]:find("g") then inst.Transparency=.35 end end end
 inst.Name=p[14]
 if p[15] and p[15]~="" then for kv in p[15]:gmatch("[^;]+") do local a,b=kv:match("^(.-)=(.*)$") if a then inst:SetAttribute(a,tonumber(b) or b) end end end
 return inst
end
local templates={}
local cur,curBase,curKind
local nParts,nInst=0,0
for line in D:gmatch("[^\n]+") do
 local p=line:split("|")
 local k=p[1]
 if k=="T" then
  local src=kitSrc:FindFirstChild("K_"..p[2])
  if src then
   cur=src:Clone() cur.Name=p[2] local o=stripOrigin(cur) curBase=CFrame.new(o) cur.Parent=kit templates[p[2]]=cur
  else warn("[DragonBall] sem malha para",p[2]) cur=Instance.new("Model") cur.Name=p[2] cur.WorldPivot=CFrame.new() curBase=CFrame.new() cur.Parent=kit templates[p[2]]=cur end
  curKind="K"
 elseif k=="G" then
  local parent=node(p[3])
  local src=mapSrc:FindFirstChild(p[2])
  if src then local g=src:Clone() local o=stripOrigin(g) g:PivotTo(CFrame.new()) g.Name="Malha" g.Parent=parent end
  cur=parent curBase=CFrame.new() curKind="G"
 elseif k=="I" then
  local t=templates[p[2]]
  if t then
   local c=t:Clone() local s=tonumber(p[10])
   if math.abs(s-1)>.001 then c:ScaleTo(s) end
   c:PivotTo(CFrame.new(tonumber(p[3]),tonumber(p[4]),tonumber(p[5]),tonumber(p[6]),tonumber(p[7]),tonumber(p[8]),tonumber(p[9])))
   c.Parent=cur nInst+=1
  end
 elseif k=="P" then
  local pt=Instance.new("Part") pt.Name=p[2] pt.Anchored=true pt.Size=Vector3.one pt.Transparency=1
  pt.CanCollide=false pt.CanQuery=false pt.CanTouch=false pt.Position=Vector3.new(tonumber(p[3]),tonumber(p[4]),tonumber(p[5]))
  for kv in (p[6] or ""):gmatch("[^;]+") do local a,b=kv:match("^(.-)=(.*)$") if a then pt:SetAttribute(a,tonumber(b) or b) end end
  pt.Parent=node("Gameplay")
 elseif k=="B" or k=="C" or k=="A" or k=="W" or k=="K" then
  local part=mkPart(p,curBase) part.Parent=cur nParts+=1
 end
end
kit.Parent=SS
root.Parent=SS
print("DRAGONBALL_BUILD",NAME,"instancias",nInst,"parts",nParts)
'''
