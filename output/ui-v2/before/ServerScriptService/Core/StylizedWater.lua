-- Agua e cachoeiras estilizadas (Vila da Folha e Vale Capsule).
-- Agua: cor em gradiente + duas camadas animadas (rede de linhas brancas e sombra deslocada), no estilo cartoon.
-- Cachoeiras: Beams curvos com textura correndo (mesma tecnica do plugin Waterfall Generator, automatizada),
-- espuma na borda, anel de espuma e ondas expandindo na base, nevoa e respingos.
local M={}
local V=Vector3.new local C=Color3.fromRGB

local TEX={
 linhas='rbxassetid://123614169905314',
 sombra='rbxassetid://78258374642866',
 cachoeira='rbxassetid://108982815970120',
 espuma='rbxassetid://115696152960275',
 nevoa='rbxasset://textures/particles/smoke_main.dds',
 gota='rbxasset://textures/particles/sparkles_main.dds',
}
M.TEX=TEX

local function part(props,parent)
 local p=Instance.new(props.Shape and 'Part' or 'Part')
 p.Anchored=true p.CanCollide=false p.CanQuery=false p.CanTouch=false p.CastShadow=false
 p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth
 for k,v in props do p[k]=v end
 p.Parent=parent
 return p
end

local function texture(p,name,id,tile,transp,face,color)
 local t=Instance.new('Texture') t.Name=name t.Texture=id t.Face=face or Enum.NormalId.Top
 t.StudsPerTileU=tile t.StudsPerTileV=tile t.Transparency=transp or 0 if color then t.Color3=color end
 t.Parent=p return t
end

local function emitter(parent,cfg)
 local e=Instance.new('ParticleEmitter')
 for k,v in cfg do e[k]=v end
 e:SetAttribute('FolhaAmbient',true)
 e.Parent=parent return e
end

-- ---------------------------------------------------------------- superficies de agua
local DEEP,MID,LIGHT=C(34,128,204),C(58,170,226),C(128,216,244)

function M.surface(p,depth01)
 for _,c in p:GetChildren() do if c:IsA('Texture') or c:IsA('Decal') then c:Destroy() end end
 p.Material=Enum.Material.SmoothPlastic p.Reflectance=0
 p.Transparency=.06
 local d=math.clamp(depth01 or .5,0,1)
 p.Color=d<.5 and LIGHT:Lerp(MID,d*2) or MID:Lerp(DEEP,(d-.5)*2)
 local sombra=texture(p,'AguaSombra',TEX.sombra,34,.15)
 local linhas=texture(p,'AguaLinhas',TEX.linhas,28,.05)
 local seed=(p.Position.X*.37+p.Position.Z*.21)%7
 linhas:SetAttribute('WaterSeed',seed) sombra:SetAttribute('WaterSeed',seed)
end

local function surfaces(model)
 -- agrupa as faixas de agua por pai para calcular o gradiente (borda clara, centro fundo)
 local groups={}
 for _,p in model:GetDescendants() do
  if p:IsA('BasePart') and (p.Name=='Agua' or p.Name=='AguaLago') then
   local g=groups[p.Parent] or {} groups[p.Parent]=g table.insert(g,p)
  end
 end
 for _,list in groups do
  local mn,mx=V(math.huge,0,math.huge),V(-math.huge,0,-math.huge)
  for _,p in list do mn=V(math.min(mn.X,p.Position.X),0,math.min(mn.Z,p.Position.Z)) mx=V(math.max(mx.X,p.Position.X),0,math.max(mx.Z,p.Position.Z)) end
  local center=(mn+mx)/2 local half=math.max((mx-mn).Magnitude/2,1)
  local long=(mx-mn).Magnitude>120 -- rio comprido: cor media uniforme
  for _,p in list do
   local d=long and .55 or 1-(V(p.Position.X,0,p.Position.Z)-center).Magnitude/half
   M.surface(p,d)
  end
 end
 for _,p in model:GetDescendants() do
  if p:IsA('BasePart') and p.Name=='PocoCachoeira' then
   for _,c in p:GetChildren() do if c:IsA('Texture') then c:Destroy() end end
   p.Color=C(214,242,252) p.Transparency=.35 p.Material=Enum.Material.SmoothPlastic
   local t=texture(p,'EspumaPoco',TEX.espuma,10,.2) t:SetAttribute('WaterSeed',1)
  end
 end
end

-- ---------------------------------------------------------------- cachoeiras
local function cluster(parts)
 local out={}
 for _,p in parts do
  local placed=false
  for _,c in out do
   local q=c[1]
   if (V(p.Position.X,0,p.Position.Z)-V(q.Position.X,0,q.Position.Z)).Magnitude<16 then table.insert(c,p) placed=true break end
  end
  if not placed then table.insert(out,{p}) end
 end
 return out
end

local function beam(a0,a1,cfg,parent)
 local b=Instance.new('Beam')
 b.Attachment0=a0 b.Attachment1=a1 b.FaceCamera=false b.Segments=24
 for k,v in cfg do b[k]=v end
 b.Parent=parent return b
end

function M.waterfall(parts,island,center)
 local ref=parts[1]
 local lateral=ref.CFrame.RightVector lateral=V(lateral.X,0,lateral.Z).Unit
 local normal=V(-lateral.Z,0,lateral.X)
 local top,bottom=-math.huge,math.huge
 local lo,hi=math.huge,-math.huge
 local sum=V()
 for _,p in parts do
  local h=math.abs(p.CFrame.UpVector.Y)>.5 and p.Size.Y or p.Size.Z
  top=math.max(top,p.Position.Y+h/2) bottom=math.min(bottom,p.Position.Y-h/2)
  local s=(p.Position-ref.Position):Dot(lateral) local w=p.Size.X/2
  lo=math.min(lo,s-w) hi=math.max(hi,s+w)
  sum+=p.Position
 end
 local mid=sum/#parts
 local width=math.max(hi-lo,4)
 local base=ref.Position+lateral*((lo+hi)/2)
 base=V(base.X,mid.Y,base.Z)
 -- lado de fora: o lado onde nao ha rocha (raycast); na borda da ilha, para longe do centro
 local params=RaycastParams.new() params.FilterType=Enum.RaycastFilterType.Exclude params.FilterDescendantsInstances=parts
 local probe=V(base.X,top-6,base.Z)
 local hitF=workspace:Raycast(probe,normal*14,params)
 local hitB=workspace:Raycast(probe,-normal*14,params)
 local out
 if hitF and not hitB then out=-normal elseif hitB and not hitF then out=normal
 else local away=V(base.X-center.X,0,base.Z-center.Z) out=(away:Dot(normal)>=0) and normal or -normal end

 local folder=Instance.new('Model') folder.Name='CachoeiraEstilizada' folder.Parent=parts[1].Parent
 local lipPos=V(base.X,top,base.Z)+out*.6
 local fall=top-bottom
 local drop=math.clamp(fall*.08,2.5,7)
 local plungePos=V(base.X,bottom,base.Z)+out*drop
 -- existe poco embaixo?
 local down=workspace:Raycast(plungePos+V(0,4,0),V(0,-14,0),params)
 local pool=down~=nil
 if pool then plungePos=V(plungePos.X,down.Position.Y+.2,plungePos.Z) end

 local src=part({Name='Fonte',Size=V(1,1,1),Transparency=1,CFrame=CFrame.new(lipPos)},folder)
 local plg=part({Name='Queda',Size=V(1,1,1),Transparency=1,CFrame=CFrame.new(plungePos)},folder)
 local a0=Instance.new('Attachment') a0.Parent=src a0.WorldCFrame=CFrame.fromMatrix(lipPos,out,lateral)
 local a1=Instance.new('Attachment') a1.Parent=plg a1.WorldCFrame=CFrame.fromMatrix(plungePos,V(0,1,0),lateral)
 local curve0=math.clamp(fall*.14,3,10)
 local curve1=-math.clamp(fall*.45,8,40)
 local body=beam(a0,a1,{Name='Agua',Texture=TEX.cachoeira,TextureMode=Enum.TextureMode.Static,TextureLength=26,TextureSpeed=1.6,
  Width0=width,Width1=width*1.18,CurveSize0=curve0,CurveSize1=curve1,LightEmission=.15,LightInfluence=.6,
  Color=ColorSequence.new(C(200,240,255),C(150,215,245)),
  Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,0),NumberSequenceKeypoint.new(.85,.05),NumberSequenceKeypoint.new(1,.35)}),ZOffset=0},folder)
 body.TextureMode=Enum.TextureMode.Wrap
 beam(a0,a1,{Name='AguaFundo',Texture=TEX.cachoeira,TextureMode=Enum.TextureMode.Wrap,TextureLength=40,TextureSpeed=1.1,
  Width0=width+3,Width1=width*1.3+4,CurveSize0=curve0*.8,CurveSize1=curve1*1.05,LightEmission=0,LightInfluence=1,
  Color=ColorSequence.new(C(90,180,230)),Transparency=NumberSequence.new(.35),ZOffset=-1},folder)
 beam(a0,a1,{Name='AguaBrilho',Texture=TEX.cachoeira,TextureMode=Enum.TextureMode.Wrap,TextureLength=18,TextureSpeed=2.3,
  Width0=width*.75,Width1=width*.9,CurveSize0=curve0*1.1,CurveSize1=curve1*.95,LightEmission=.45,LightInfluence=.4,
  Color=ColorSequence.new(C(255,255,255)),Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.25),NumberSequenceKeypoint.new(1,.55)}),ZOffset=1},folder)

 -- espuma na borda de cima
 local n=math.max(3,math.floor(width/2.2))
 for i=0,n do
  local s=-width/2+width*i/n
  local d=2.2+((i*37)%10)/10*1.4
  part({Name='EspumaBorda',Shape=Enum.PartType.Ball,Size=V(d,d,d),Color=C(245,252,255),Material=Enum.Material.SmoothPlastic,
   Transparency=.05,CFrame=CFrame.new(lipPos+lateral*s+out*.4+V(0,.2,0))},folder)
 end
 emitter(src,{Texture=TEX.gota,Color=ColorSequence.new(C(230,248,255)),Rate=width*.8,Lifetime=NumberRange.new(.6,1),
  Speed=NumberRange.new(2,5),SpreadAngle=Vector2.new(25,25),Acceleration=V(0,-30,0),Size=NumberSequence.new(.4,.1),
  Transparency=NumberSequence.new(.2,1),EmissionDirection=Enum.NormalId.Front,Shape=Enum.ParticleEmitterShape.Box,LightEmission=.3})

 local plume=part({Name='Nevoa',Size=V(width+4,1,4),Transparency=1,CFrame=CFrame.fromMatrix(plungePos+V(0,1,0),lateral,V(0,1,0))},folder)
 emitter(plume,{Texture=TEX.nevoa,Color=ColorSequence.new(C(236,248,255)),Rate=math.clamp(width*.7,4,24),Lifetime=NumberRange.new(2,3.4),
  Speed=NumberRange.new(2,5),SpreadAngle=Vector2.new(60,60),Acceleration=V(0,2.5,0),
  Size=NumberSequence.new({NumberSequenceKeypoint.new(0,3),NumberSequenceKeypoint.new(1,10)}),
  Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.55),NumberSequenceKeypoint.new(1,1)}),Shape=Enum.ParticleEmitterShape.Box,
  EmissionDirection=Enum.NormalId.Top,LightEmission=.2,RotSpeed=NumberRange.new(-30,30),Rotation=NumberRange.new(0,360)})
 if pool then
  emitter(plume,{Texture=TEX.gota,Color=ColorSequence.new(C(245,252,255)),Rate=width*1.2,Lifetime=NumberRange.new(.5,.9),
   Speed=NumberRange.new(8,15),SpreadAngle=Vector2.new(50,50),Acceleration=V(0,-40,0),Size=NumberSequence.new(.7,.2),
   Transparency=NumberSequence.new(.1,1),EmissionDirection=Enum.NormalId.Top,Shape=Enum.ParticleEmitterShape.Box,LightEmission=.3})
  -- anel de espuma e ondas expandindo (animadas no cliente)
  local rx,rz=width*.65+3,width*.35+3
  for i=0,13 do
   local a=i/14*math.pi*2
   local d=2.6+((i*53)%10)/10*1.8
   local q=plungePos+lateral*math.cos(a)*rx+out*math.sin(a)*rz
   part({Name='EspumaBase',Shape=Enum.PartType.Ball,Size=V(d,d*.7,d),Color=C(245,252,255),Material=Enum.Material.SmoothPlastic,
    Transparency=.08,CFrame=CFrame.new(q+V(0,.1,0))},folder)
  end
  for k=1,3 do
   local ring=part({Name='OndaAnel',Shape=Enum.PartType.Cylinder,Size=V(.12,width*.8,width*.8),Color=C(240,250,255),
    Material=Enum.Material.SmoothPlastic,Transparency=.4,CFrame=CFrame.new(plungePos+V(0,.15+k*.02,0))*CFrame.Angles(0,0,math.pi/2)},folder)
   local deco=Instance.new('Texture') deco.Name='AnelEspuma' deco.Texture=TEX.espuma deco.Face=Enum.NormalId.Right deco.StudsPerTileU=6 deco.StudsPerTileV=6 deco.Parent=ring
   ring:SetAttribute('RingPhase',k/3) ring:SetAttribute('RingMax',width*2.2+8) ring:SetAttribute('RingMin',width*.6)
  end
 end
 for _,p in parts do p:Destroy() end
 return folder
end

function M.apply(model,center)
 surfaces(model)
 local groups={}
 for _,p in model:GetDescendants() do
  if p:IsA('BasePart') and (p.Name=='Cachoeira' or p.Name=='CachoeiraBorda' or p.Name=='Cachoeirinha') then
   local key=p.Name..'@'..p.Parent:GetFullName()
   groups[key]=groups[key] or {} table.insert(groups[key],p)
  end
 end
 local n=0
 for _,list in groups do
  for _,c in cluster(list) do
   local ok,err=pcall(M.waterfall,c,model,center)
   if ok then n+=1 else warn('[StylizedWater]',err) end
  end
 end
 return n
end

return M

