local D=[==[
G|KONOHA_TEST
G|KONOHA_TEST/TestAsset
M|190,78,50|SmoothPlastic|
M|84,138,104|SmoothPlastic|
M|80,108,140|SmoothPlastic|
M|222,176,72|Metal|
M|176,184,188|SmoothPlastic|
M|140,96,60|Wood|
M|255,196,110|Neon|n
M|128,136,144|Metal|
M|255,110,50|Neon|n
M|90,220,255|Neon|n
M|236,224,192|SmoothPlastic|
B|0|0|0|2|0|6|4|2|0|0.2588|0|0.9659|1|BoxRot|
W|0|1|-10|2|0|4|4|4|0|0|0|1|1|WedgeN|
W|0|2|-20|2|0|4|4|6|0|0.7071|0|0.7071|1|WedgeRot|
K|0|3|-30|2|0|4|4|4|0|0|0|1|1|Corner|
C|0|4|0|3|12|6|4|4|0|0|0.7071|0.7071|1|CylZ|
C|0|5|-10|2|12|8|2|2|0|0|0|1|1|CylX|
A|0|6|-20|2|12|3|3|3|0|0|0|1|0|Ball|
B|0|7|-32|3|13|0.6|0.6|9.38|-0.3255|-0.2725|-0.0985|0.9|0|Rod|
B|0|8|0|1|30|2|2|2|0|0|0|1|1|NorthMarker|
B|0|9|-40|1|0|2|2|2|0|0|0|1|1|EastMarker|
B|1|10|0|1.5|-15|12|3|6|0|0.3827|0|0.9239|1|Base|
W|1|0|1.06|4.5|-13.94|12|3|3|0|0.3827|0|0.9239|1|Roof|
]==]

local NAME="KonohaTest"
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
