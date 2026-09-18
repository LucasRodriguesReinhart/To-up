-- Additive lobby dressing. Keeps the existing buildings, paths and original studded materials.
local M={}
function M.build()
 local root=workspace:WaitForChild("LobbyRenovado")
 local old=root:FindFirstChild("AcabamentoDaVila") if old then old:Destroy() end
 local model=Instance.new("Model") model.Name="AcabamentoDaVila" model.Parent=root
 local V=Vector3.new local C=Color3.fromRGB
 local wood=C(114,73,39) local dark=C(62,46,32) local stone=C(110,108,93) local green=C(88,163,43)
 local function part(name,size,pos,color,material,rot)
  local p=Instance.new("Part") p.Name=name p.Size=size p.CFrame=CFrame.new(pos)*(rot or CFrame.identity)
  p.Anchored=true p.Color=color p.Material=material or Enum.Material.Plastic
  p.CanCollide=false p.CanTouch=false p.CanQuery=false
  p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth p.Parent=model return p
 end
 local function beam(a,b,width,color)
  return part("Viga",V(width,width,(b-a).Magnitude),(a+b)/2,color,Enum.Material.Wood,CFrame.lookAt(a,b).Rotation)
 end
 local function lantern(p,size)
  part("Armação",V(1.1,.2,1.1)*size,p+V(0,.65*size,0),dark)
  part("Armação",V(1,.2,1)*size,p-V(0,.65*size,0),dark)
  local bulb=part("LuzDaVila",V(.65,1.05,.65)*size,p,C(255,176,65),Enum.Material.Neon)
  for _,x in ipairs({-.43,.43}) do for _,z in ipairs({-.43,.43}) do
   part("Grade",V(.1,1.35,.1)*size,p+V(x*size,0,z*size),dark)
  end end
  local light=Instance.new("PointLight") light.Color=C(255,174,87) light.Brightness=1.15 light.Range=13*size light.Parent=bulb
 end
 local function bush(p)
  for i=0,4 do
   local q=p+V(math.cos(i*1.8)*1.35,.65+i%2*.3,math.sin(i*1.8)*1.2)
   local leaf=part("ArbustoOriginal",V(2.1,1.6,2),q,green:Lerp(C(126,203,62),i*.12))
   leaf.TopSurface=Enum.SurfaceType.Studs
   if i%2==0 then part("FloresDouradas",V(.45,.3,.45),q+V(0,1,0),C(249,205,87)) end
  end
 end
 local function planter(p)
  part("Jardineira",V(7,1.3,4),p+V(0,.65,0),stone)
  local soil=part("TerraJardineira",V(6.4,.15,3.4),p+V(0,1.4,0),C(88,68,43))
  for _,x in ipairs({-1.9,1.9}) do bush(p+V(x,1.3,0)) end
 end
 local function bench(p,angle)
  local cf=CFrame.new(p)*CFrame.Angles(0,angle,0)
  local function b(name,s,q,col) return part(name,s,cf:PointToWorldSpace(q),col,Enum.Material.Wood,cf.Rotation) end
  for i=0,2 do b("AssentoBanco",V(7,.25,.6),V(0,1.9,i*.67-.67),wood) end
  for i=0,1 do b("EncostoBanco",V(7,.65,.25),V(0,2.7+i*.75,1),wood) end
  for _,x in ipairs({-2.7,2.7}) do b("ApoioBanco",V(.5,2,.5),V(x,1,0),dark) b("ApoioEncosto",V(.4,3.3,.4),V(x,1.65,1),dark) end
 end
 -- Timber workshops frame the furnace without occupying the middle of the plaza.
 for _,side in ipairs({-1,1}) do
  local center=V(side*34,2.8,-19)
  for _,x in ipairs({-6.5,6.5}) do for _,z in ipairs({-4,4}) do
   part("ColunaPergola",V(.85,10,.85),center+V(x,5,z),wood,Enum.Material.Wood)
   beam(center+V(x,7,z),center+V(x+(x>0 and -2.5 or 2.5),10,z),.65,wood)
  end end
  for i=-4,4 do
   part("RipadoCobertura",V(15,.4,.85),center+V(0,10.5,i*1.2),wood,Enum.Material.Wood)
  end
  part("TampoBancada",V(9,.5,3.3),center+V(0,3,-1),wood,Enum.Material.Wood)
  for _,x in ipairs({-3.6,3.6}) do part("PeBancada",V(.7,3,.7),center+V(x,1.5,-1),dark) end
  for i=-2,2 do
   part("LingoteEstoque",V(1.35,.6,.7),center+V(i*1.7,3.65,-1),side==1 and C(165,182,186) or C(205,139,52),Enum.Material.Metal)
  end
  lantern(center+V(-5,8.5,3),1) lantern(center+V(5,8.5,3),1)
  part("TecidoOficina",V(9,2,.2),center+V(0,8.9,4.4),side==1 and C(74,119,160) or C(162,60,42))
 end
 -- Hanging lights and planted seating niches along the side routes.
 for _,side in ipairs({-1,1}) do
  bench(V(side*40,3,28),side*math.pi/2)
  planter(V(side*39,3,17))
  planter(V(side*34,3,42))
  for _,z in ipairs({8,36}) do
   part("PosteGuirlanda",V(.6,12,.6),V(side*48,8.7,z),wood,Enum.Material.Wood)
  end
  local prev
  for i=0,14 do
   local t=i/14 local q=V(side*48,14.7-math.sin(t*math.pi)*2.4,8+28*t)
   if prev then beam(prev,q,.1,dark) end prev=q
   if i%2==1 then lantern(q-V(0,.7,0),.65) end
  end
 end
 for _,p in ipairs({{-29,3,-4},{29,3,-4},{-65,1,48},{66,1,46},{-82,1,22},{82,1,-12},{-57,1,69},{57,1,68}}) do bush(V(p[1],p[2],p[3])) end
 -- Hearth fire and rising embers are handled by the existing VFX quality toggle.
 for _,x in ipairs({-4,0,4}) do
  local anchor=part("BrasaDaFornalha",V(.2,.2,.2),V(x,5.5,-32),C(255,151,52))
  anchor.Transparency=1
  local a=Instance.new("Attachment") a.Parent=anchor
  local e=Instance.new("ParticleEmitter")
  e.Texture="rbxasset://textures/particles/fire_main.dds"
  e.Color=ColorSequence.new(C(255,219,94),C(235,66,20))
  e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,5),NumberSequenceKeypoint.new(.4,7),NumberSequenceKeypoint.new(1,0)})
  e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.1),NumberSequenceKeypoint.new(.65,.25),NumberSequenceKeypoint.new(1,1)})
  e.Lifetime=NumberRange.new(.8,1.2) e.Rate=12 e.Speed=NumberRange.new(5,8) e.SpreadAngle=Vector2.new(14,14)
  e.LightEmission=.7 e:SetAttribute("LobbyAmbient",true) e.Parent=a
  local l=Instance.new("PointLight") l.Color=C(255,143,51) l.Brightness=.4 l.Range=14 l.Parent=anchor
 end
 local forge=root.Arquitetura:FindFirstChild("ForjaIgnis")
 if forge then for _,light in ipairs(forge:GetDescendants()) do
  if light:IsA("PointLight") and light.Parent.Name=="Fogo" then
   if light:GetAttribute("BeforePolishBrightness")==nil then light:SetAttribute("BeforePolishBrightness",light.Brightness) light:SetAttribute("BeforePolishRange",light.Range) end
   light.Brightness=1.1 light.Range=22
  end
 end end
 return model
end
return M
