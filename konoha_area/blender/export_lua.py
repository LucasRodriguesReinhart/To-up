# Exports KONOHA_* collections (collection instances realised) as a self-contained Luau build script.
# The script is pasted into the Studio command bar; it rebuilds the model under ServerStorage.
import bpy, os
from mathutils import Matrix, Vector

M3 = Matrix(((-1,0,0),(0,0,1),(0,1,0)))   # Roblox = M3 @ Blender   (det +1)
SHAPES = {'RBX_Block':'B','RBX_Cylinder':'C','RBX_Ball':'A','RBX_Wedge':'W','RBX_Corner':'K'}

def f(v, d=2):
    s = ('%.' + str(d) + 'f') % v
    s = s.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def clean(s):
    return str(s).replace('|', '/').replace('\n', ' ').replace(']==]', '')

def collect(tops):
    dg = bpy.context.evaluated_depsgraph_get()
    owner = {}
    def walk(c, route):
        for o in c.objects: owner[o.name] = route
        for ch in c.children: walk(ch, route + [ch.name])
    for tn in tops:
        walk(bpy.data.collections[tn], [tn])
    groups, gidx, mats, midx, rows, marks = [], {}, [], {}, [], []
    for inst in dg.object_instances:
        ob = inst.object
        orig = ob.original
        if inst.is_instance:
            par = inst.parent.original if inst.parent else None
            if not par or par.name not in owner: continue
            route = owner[par.name] + [par.name]
        else:
            if orig.name not in owner: continue
            route = owner[orig.name]
        mw = inst.matrix_world
        if ob.type == 'EMPTY':
            if orig.name.startswith('GP_'):
                t = M3 @ mw.to_translation()
                props = ';'.join('%s=%s' % (k, clean(orig[k])) for k in orig.keys())
                marks.append('P|%s|%s|%s|%s|%s' % (orig.name.split('.')[0], f(t.x), f(t.y), f(t.z), props))
            continue
        if ob.type != 'MESH': continue
        shape = SHAPES.get(ob.data.name.split('.')[0])
        if not shape: continue
        g = '/'.join(route)
        if g not in gidx:
            gidx[g] = len(groups); groups.append(g)
        mat = orig.material_slots[0].material if orig.material_slots else None
        mkey = mat.name if mat else 'none'
        if mkey not in midx:
            midx[mkey] = len(mats)
            rgb = list(mat['rbx_rgb']) if mat and 'rbx_rgb' in mat else [200,200,200]
            mats.append('M|%d,%d,%d|%s|%s' % (rgb[0], rgb[1], rgb[2], mat.get('rbx_material','SmoothPlastic') if mat else 'SmoothPlastic', mat.get('rbx_flags','') if mat else ''))
        t = M3 @ mw.to_translation()
        b3 = mw.to_3x3()
        cols = [Vector((b3[0][i], b3[1][i], b3[2][i])) for i in range(3)]
        s = [c.length for c in cols]
        R = Matrix([[cols[j][i]/s[j] for j in range(3)] for i in range(3)])
        q = (M3 @ R @ M3.transposed()).to_quaternion()
        size = (s[0], s[2], s[1])
        deco = ';'.join('%s=%s' % (k, clean(orig[k])) for k in orig.keys() if k not in ('col',))
        rows.append('%s|%d|%d|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%d|%s|%s' % (
            shape, gidx[g], midx[mkey], f(t.x), f(t.y), f(t.z),
            f(max(size[0], .05)), f(max(size[1], .05)), f(max(size[2], .05)),
            f(q.x, 4), f(q.y, 4), f(q.z, 4), f(q.w, 4), 1 if orig.get('col') else 0,
            clean(orig.name.split('.')[0]), deco))
    return groups, mats, rows, marks

BUILDER = r'''
local NAME="%s"
local SS=game:GetService("ServerStorage")
local old=SS:FindFirstChild(NAME) if old then old:Destroy() end
local root=Instance.new("Model") root.Name=NAME
local groups,mats,nodes={}, {}, {}
local function node(path)
 if nodes[path] then return nodes[path] end
 local parent,name=root,path
 local cut=path:match("^.*()/")
 if cut then parent=node(path:sub(1,cut-1)) name=path:sub(cut+1) end
 local m=Instance.new(parent==root and "Folder" or "Model") m.Name=name m.Parent=parent
 nodes[path]=m return m
end
local n=0
for line in D:gmatch("[^\n]+") do
 local f=line:split("|")
 local k=f[1]
 if k=="G" then table.insert(groups,f[2])
 elseif k=="M" then local c=f[2]:split(",")
  table.insert(mats,{Color3.fromRGB(tonumber(c[1]),tonumber(c[2]),tonumber(c[3])),Enum.Material[f[3]],f[4] or ""})
 elseif k=="P" then
  local p=Instance.new("Part") p.Name=f[2] p.Anchored=true p.Size=Vector3.one p.Transparency=1
  p.CanCollide=false p.CanQuery=false p.CanTouch=false p.Position=Vector3.new(tonumber(f[3]),tonumber(f[4]),tonumber(f[5]))
  for kv in (f[6] or ""):gmatch("[^;]+") do local a,b=kv:match("^(.-)=(.*)$") if a then p:SetAttribute(a,tonumber(b) or b) end end
  p.Parent=node("Gameplay")
 else
  local p
  if k=="W" then p=Instance.new("WedgePart") elseif k=="K" then p=Instance.new("CornerWedgePart") else
   p=Instance.new("Part") p.Shape=k=="C" and Enum.PartType.Cylinder or k=="A" and Enum.PartType.Ball or Enum.PartType.Block end
  local g,mi=tonumber(f[2])+1,tonumber(f[3])+1
  local mat=mats[mi]
  local size=Vector3.new(tonumber(f[7]),tonumber(f[8]),tonumber(f[9]))
  p.Anchored=true p.Size=size
  p.CFrame=CFrame.new(tonumber(f[4]),tonumber(f[5]),tonumber(f[6]),tonumber(f[10]),tonumber(f[11]),tonumber(f[12]),tonumber(f[13]))
  p.Color=mat[1] p.Material=mat[2]
  p.TopSurface=(mat[3]:find("s") and size.Y>=1) and Enum.SurfaceType.Studs or Enum.SurfaceType.Smooth
  p.BottomSurface=Enum.SurfaceType.Smooth
  local col=f[14]=="1" p.CanCollide=col p.CanQuery=col p.CanTouch=false
  p.CastShadow=size.Magnitude>6 and not mat[3]:find("n")
  if mat[3]:find("g") then p.Transparency=.35 end
  if mat[3]:find("i") then p.Transparency=1 end
  p.Name=f[15]
  if f[16] and f[16]~="" then for kv in f[16]:gmatch("[^;]+") do local a,b=kv:match("^(.-)=(.*)$") if a then p:SetAttribute(a,tonumber(b) or b) end end end
  p.Parent=node(groups[g])
  n+=1
 end
end
root.Parent=SS
print("KONOHA_BUILD",NAME,n,"parts")
'''

def export(path, tops, name='KonohaArea'):
    groups, mats, rows, marks = collect(tops)
    data = '\n'.join(['G|' + g for g in groups] + mats + marks + rows)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('local D=[==[\n' + data + '\n]==]\n')
        fh.write(BUILDER % name)
    return len(rows), len(marks), os.path.getsize(path)
