-- Blender-authored Shadow Garden island. Static imported meshes are shared by every instance.
local SS=game:GetService('ServerStorage')
local Layout=require(script.Parent.ShadowGardenLayout)
local M={}
local V,C=Vector3.new,Color3.fromRGB
local function cv(p)return V(-p[1],p[3],p[2])end
local function part(parent,name,p,size,color,material)
 local o=Instance.new('Part');o.Name=name;o.Anchored=true;o.CanCollide=false;o.CanTouch=false;o.CanQuery=false;o.CastShadow=false
 o.Size=size;o.Position=p;o.Color=color or C(255,255,255);o.Material=material or Enum.Material.SmoothPlastic;o.Parent=parent;return o
end
local function point(parent,pos,color,range,brightness)
 local p=part(parent,'Luz',pos,V(.2,.2,.2));p.Transparency=1
 local l=Instance.new('PointLight');l.Color=color;l.Range=range;l.Brightness=brightness;l.Shadows=false;l.Parent=p;return p
end
local function particles(parent,pos,kind)
 local p=part(parent,kind,pos,V(3,.5,3));p.Transparency=1
 local e=Instance.new('ParticleEmitter');e.Texture=kind=='Bruma' and 'rbxasset://textures/particles/smoke_main.dds' or 'rbxasset://textures/particles/sparkles_main.dds'
 e.Color=ColorSequence.new(kind=='Bruma'and C(149,177,200)or C(193,133,255));e.Rate=kind=='Bruma'and 3 or 4;e.Lifetime=NumberRange.new(2,3.5);e.Speed=NumberRange.new(.3,1.1);e.SpreadAngle=Vector2.new(60,60)
 e.Size=kind=='Bruma'and NumberSequence.new(3,7)or NumberSequence.new(.18,.05)
 e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(.25,.65),NumberSequenceKeypoint.new(1,1)})
 e.LightEmission=kind=='Bruma'and .1 or .6;e:SetAttribute('FolhaAmbient',true);e.Parent=p
end
local function label(parent,pos,text,w,h)
 local p=part(parent,'Placa',pos,V(w,.8,h),C(29,32,48));p.Size=V(w,h,.35)
 local g=Instance.new('SurfaceGui');g.Adornee=p;g.Face=Enum.NormalId.Front;g.CanvasSize=Vector2.new(w*40,h*40);g.LightInfluence=.1;g.MaxDistance=130;g.Parent=p
 local t=Instance.new('TextLabel');t.Size=UDim2.fromScale(.93,.8);t.Position=UDim2.fromScale(.035,.1);t.BackgroundTransparency=1;t.Text=text;t.Font=Enum.Font.Garamond;t.TextScaled=true;t.TextColor3=C(215,192,141);t.Parent=g
end
local function waterfall(parent,base)
 -- Narrow curved ribbons with native scrolling texture, no external texture permissions.
 for i=0,6 do
  local x=122+i*1.9
  local p=part(parent,'QuedaDagua',base+cv({x,14,7.2}),V(.2,.2,.2));p.Transparency=1
  local a=Instance.new('Attachment');a.CFrame=CFrame.fromMatrix(V(),V(0,0,-1),V(1,0,0));a.Parent=p
  local b=Instance.new('Attachment');b.CFrame=CFrame.fromMatrix(V(0,-9,-13),V(0,-1,0),V(1,0,0));b.Parent=p
  local beam=Instance.new('Beam');beam.Name='Fluxo';beam.Attachment0=a;beam.Attachment1=b;beam.Width0=1.9;beam.Width1=2.1
  beam.CurveSize0=5;beam.CurveSize1=-4;beam.Segments=18;beam.FaceCamera=false
  beam.Color=ColorSequence.new(C(188,228,238),C(99,181,205));beam.Transparency=NumberSequence.new(.1,.45)
  beam.Texture='rbxasset://textures/particles/water_main.dds';beam.TextureMode=Enum.TextureMode.Wrap;beam.TextureLength=9;beam.TextureSpeed=1.2+i*.07;beam.LightEmission=.15;beam.Parent=p
 end
 particles(parent,base+cv({128,1,-1.1}),'Bruma')
 -- Small foam crests at the plunge, shared built-in texture.
 local p=part(parent,'Espuma',base+cv({128,1,-1.7}),V(13,.1,7),C(162,220,230));p.Transparency=.85
 local t=Instance.new('Texture');t.Texture='rbxasset://textures/particles/water_main.dds';t.Face=Enum.NormalId.Top;t.StudsPerTileU=6;t.StudsPerTileV=5;t.Transparency=.3;t.Name='OndasDaIlha';t.Parent=p
end
local footprints={Casa_Nobre={22,20,19},Casa_Sacada={24,22,25},Comercio_Discreto={27,19,18},Mansao={32,25,28},Arquivo={27,26,32},Salao_Sete_Sombras={55,29,40}}
function M.scene(parent,base,kit)
 local model=Instance.new('Model');model.Name='DominioDaVeiaArcana';model.Parent=parent
 local groups={}
 local function group(n)local g=groups[n];if not g then g=Instance.new('Folder');g.Name=n;g.Parent=model;groups[n]=g end;return g end
 local collision=group('Colisoes');local fx=group('Efeitos')
 for _,d in Layout.instances do
  local template=kit:FindFirstChild(d.asset);assert(template,'Missing Blender mesh '..d.asset)
  local o=template:Clone();o.Name=d.asset
  if d.s~=1 then o:ScaleTo(d.s)end
  o:PivotTo(CFrame.new(base+cv(d.p))*CFrame.Angles(0,d.rz,0));o.Parent=group(d.category)
  for _,p in o:GetDescendants()do if p:IsA('BasePart')then p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false end end
  local f=footprints[d.asset]
  if f then local p=part(collision,'EdificioFechado',base+cv(d.p)+V(0,f[3]*d.s/2,0),V(f[1],f[3],f[2])*d.s);p.CFrame=CFrame.new(p.Position)*CFrame.Angles(0,d.rz,0);p.Transparency=1;p.CanCollide=true;p.CanQuery=true end
  if d.asset=='Lanterna'then point(fx,base+cv(d.p)+V(0,8.1*d.s,0),C(249,199,128),15,.65)end
  if d.asset=='Veio_Arcano'then
   point(fx,base+cv(d.p)+V(0,4,0),C(169,106,252),18,.85);particles(fx,base+cv(d.p)+V(0,5,0),'Aura')
  end
  if d.asset=='Ondas_Lago'then
   for _,p in o:GetDescendants()do if p:IsA('BasePart')then p:SetAttribute('ShadowWaterRipple',true);p.CastShadow=false end end
  end
  if d.asset=='Cachoeira_Lamina'then for _,p in o:GetDescendants()do if p:IsA('BasePart')then p.Transparency=.45;p.CastShadow=false end end end
 end
 for _,d in Layout.colliders do
  local p=Instance.new(d.shape=='Wedge'and 'WedgePart'or 'Part');p.Name=d.name;p.Anchored=true;p.Transparency=1;p.CanCollide=true;p.CanQuery=true;p.CanTouch=false
  p.Size=V(d.s[1],d.s[3],d.s[2]);p.CFrame=CFrame.new(base+cv(d.p))*CFrame.Angles(0,d.rz,0);p.Parent=collision
 end
 label(fx,base+cv({0,78,14.3}),'VEIA ARCANA',22,2.1)
 label(fx,base+cv({-20,-147,5.5}),'SHADOW GARDEN',12,1.8)
 -- Entry sign is a suspended thin plaque; plenty of clearance and no blocking wall.
 label(fx,base+cv({137,57,22}),'GRAND LINE',17,1.8)
 waterfall(fx,base)
 for _,p in {{-130,105,4},{91,145,4},{-93,124,2}}do particles(fx,base+cv(p),'Bruma')end
 for _,p in {{-18,85,7},{18,85,7},{0,128,8},{-91,125,8}}do point(fx,base+cv(p),C(167,114,246),24,1.4)end
 local portal=part(fx,'NucleoPortal',base+cv({137,60,10}),V(10,13,.18),C(154,98,238),Enum.Material.Neon);portal.Transparency=.5;portal.CFrame=CFrame.new(portal.Position)*CFrame.Angles(0,-.5,0)
 particles(fx,portal.Position,'Aura');point(fx,portal.Position,C(164,118,255),25,1)
 model.WorldPivot=CFrame.new(base)
 return model
end
function M.build(parent,area)
 local kit=SS:FindFirstChild('ShadowGardenKit');assert(kit and not kit:GetAttribute('PreviewOnly'),'Import the static Blender kit first')
 local base=area.centro+V(0,6,0);local model=M.scene(parent,base,kit)
 parent.ModelStreamingMode=Enum.ModelStreamingMode.PersistentPerPlayer;parent:SetAttribute('WorldRevision',10);parent:SetAttribute('BoundsHalfSize',V(203,160,208))
 local spawns,boss,returnPad={}
 for _,m in Layout.markers do
  local pos=base+cv(m.p)
  if m.kind=='entry'then parent:SetAttribute('EntryPosition',pos)
  elseif m.kind=='safe'then parent:SetAttribute('SafePosition',pos)
  elseif m.kind=='return'then returnPad=pos
  elseif m.kind=='boss'then boss=pos
  elseif m.kind=='ore'then table.insert(spawns,{pos=pos})
  elseif m.kind=='next'then
   local p=part(model,'ViagemProximaArea',pos,V(12,.2,10),C(155,99,243),Enum.Material.Neon);p.Transparency=.9;p.CanQuery=true;p:SetAttribute('NextAreaId',5)
  end
 end
 local zones={
  {nome='PedreiraSombria',centro=base+cv({0,-5,-6}),tamanho=V(110,0,108)},
  {nome='MinaArcana',centro=base+cv({0,128,0}),tamanho=V(13,0,42)},
  {nome='Cripta',centro=base+cv({-91,124,0}),tamanho=V(16,0,26)},
 }
 return{spawns=spawns,boss=boss,returnPad=returnPad,zonas={lista=zones,bloqueios={}}}
end
return M
