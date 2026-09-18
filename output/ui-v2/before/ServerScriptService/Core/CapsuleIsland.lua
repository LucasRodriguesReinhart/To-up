-- Vale Capsule (Area 2, tema ki). Modelada no Blender (pasta dragonball_area/): malhas importadas pelo 3D Importer
-- (ServerStorage.DragonBallMeshes) e montadas pelo script dragonball_build.lua em ServerStorage.DragonBallArea.
-- Aqui a ilha e clonada, os atributos decorativos viram SurfaceGui/luz/particulas e os marcadores GP_* viram
-- entrada, chefe, portal, invocacao e zonas de mineracao.
local SS=game:GetService('ServerStorage')
local M={}
local V=Vector3.new local C=Color3.fromRGB local pi=math.pi

local function rgb(s,default)
 local t=typeof(s)=='string' and s:split(',') or {}
 if #t<3 then return default end
 return C(tonumber(t[1]),tonumber(t[2]),tonumber(t[3]))
end

local function surface(part,face)
 local g=Instance.new('SurfaceGui') g.Face=face or Enum.NormalId.Front g.Adornee=part
 g.LightInfluence=.35 g.MaxDistance=380 g.Parent=part
 return g
end

-- logo da Capsule: aneis concentricos com a capsula atravessando
local function capsuleLogo(part,ink,faces)
 for _,face in faces do
  local g=surface(part,face) g.CanvasSize=Vector2.new(256,256)
  local function circle(x,y,w,h,color)
   local f=Instance.new('Frame') f.BorderSizePixel=0 f.Position=UDim2.fromOffset(x,y) f.Size=UDim2.fromOffset(w,h) f.BackgroundColor3=color f.BackgroundTransparency=0 f.Parent=g
   local u=Instance.new('UICorner') u.CornerRadius=UDim.new(1,0) u.Parent=f
   return f
  end
  local bg=part.Transparency>=1 and C(248,248,244) or part.Color
  circle(20,20,216,216,ink) circle(38,38,180,180,bg) circle(56,56,144,144,ink) circle(76,76,104,104,bg)
  local bar=Instance.new('Frame') bar.BorderSizePixel=0 bar.BackgroundColor3=bg bar.Position=UDim2.fromOffset(128,108) bar.Size=UDim2.fromOffset(120,40) bar.Parent=g
  local pill=circle(150,114,92,28,ink)
  local t=Instance.new('TextLabel') t.BackgroundTransparency=1 t.Size=UDim2.fromOffset(60,60) t.Position=UDim2.fromOffset(98,98)
  t.Text='CC' t.TextScaled=true t.Font=Enum.Font.GothamBlack t.TextColor3=ink t.Parent=g
 end
end

local function label(part,words,color)
 local g=surface(part) g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.PixelsPerStud=30
 local t=Instance.new('TextLabel') t.Size=UDim2.fromScale(.92,.84) t.Position=UDim2.fromScale(.04,.08)
 t.BackgroundTransparency=1 t.Text=words t.TextScaled=true t.Font=Enum.Font.GothamBlack
 t.TextColor3=color or C(255,255,255) t.TextStrokeTransparency=.8 t.Parent=g
 if part.Size.Y>part.Size.X*1.6 and not words:find(' ') then t.Text=table.concat(words:split(''),'\n') end
end

local FX={
 waterfall={tex='rbxasset://textures/particles/smoke_main.dds',color=C(225,244,252),rate=6,size=6,speed=2,acc=V(0,.6,0),life=2.5},
 mist={tex='rbxasset://textures/particles/smoke_main.dds',color=C(220,240,250),rate=4,size=7,speed=1,acc=V(0,.4,0),life=3},
 fire={tex='rbxasset://textures/particles/fire_main.dds',color=C(255,150,60),rate=14,size=1.6,speed=3,acc=V(0,3,0),life=.9},
 portal={tex='rbxasset://textures/particles/sparkles_main.dds',color=C(130,230,255),rate=10,size=.5,speed=1.5,acc=V(0,1.2,0),life=2.5},
 summon={tex='rbxasset://textures/particles/sparkles_main.dds',color=C(255,210,110),rate=10,size=.6,speed=2,acc=V(0,1.6,0),life=3},
 ki={tex='rbxasset://textures/particles/sparkles_main.dds',color=C(120,235,255),rate=6,size=.7,speed=1.2,acc=V(0,2,0),life=2.2},
 smoke={tex='rbxasset://textures/particles/smoke_main.dds',color=C(200,196,188),rate=2,size=1.4,speed=1,acc=V(.2,1.2,0),life=4},
}

local function emitter(part,kind)
 local s=FX[kind] if not s then return end
 local e=Instance.new('ParticleEmitter') e.Texture=s.tex e.Color=ColorSequence.new(s.color) e.Rate=s.rate
 e.Lifetime=NumberRange.new(s.life*.7,s.life) e.Speed=NumberRange.new(s.speed*.4,s.speed) e.SpreadAngle=Vector2.new(35,35)
 e.Acceleration=s.acc e.LightEmission=(kind=='fire' or kind=='ki') and .8 or .3
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,s.size*.5),NumberSequenceKeypoint.new(.5,s.size),NumberSequenceKeypoint.new(1,s.size*.3)})
 e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(.2,.4),NumberSequenceKeypoint.new(.8,.7),NumberSequenceKeypoint.new(1,1)})
 e:SetAttribute('FolhaAmbient',true) e.Parent=part
end

local function decorate(model,base)
 require(script.Parent.StylizedWater).apply(model,base)
 local lights=0
 for _,p in model:GetDescendants() do
  if not p:IsA('BasePart') then continue end
  local a=p:GetAttributes()
  if not next(a) then continue end
  if a.text then label(p,tostring(a.text),rgb(a.textcolor)) end
  if a.emblem=='capsule' then
   local faces=a.emblemface=='Top' and {Enum.NormalId.Top} or {Enum.NormalId.Front,Enum.NormalId.Back}
   capsuleLogo(p,rgb(a.ink,C(38,82,158)),faces)
  end
  if typeof(a.light)=='string' and lights<90 then
   local t=a.light:split(',')
   local l=Instance.new('PointLight') l.Color=C(tonumber(t[1]),tonumber(t[2]),tonumber(t[3]))
   l.Range=tonumber(t[4]) or 12 l.Brightness=tonumber(t[5]) or .8 l.Shadows=false l.Parent=p lights+=1
  end
  if typeof(a.fx)=='string' and a.fx~='' then emitter(p,a.fx) end
  if a.fx=='waterfall' or p.Name=='Cachoeira' then
   local tx=Instance.new('Texture') tx.Name='FluxoCachoeira' tx.Texture='rbxasset://textures/particles/water_main.dds'
   tx.Face=Enum.NormalId.Front tx.StudsPerTileU=6 tx.StudsPerTileV=12 tx.Transparency=.55 tx.Parent=p
  end
  if p.Name=='Agua' then
   local tx=Instance.new('Texture') tx.Name='OndasDaIlha' tx.Texture='rbxasset://textures/particles/water_main.dds'
   tx.Face=Enum.NormalId.Top tx.StudsPerTileU=18 tx.StudsPerTileV=22 tx.Transparency=.85 tx.Parent=p
  end
  if a.swirl then
   for _,face in {Enum.NormalId.Left,Enum.NormalId.Right} do
    local tx=Instance.new('Texture') tx.Name='FluxoCachoeira' tx.Texture='rbxasset://textures/particles/water_main.dds'
    tx.Face=face tx.StudsPerTileU=5 tx.StudsPerTileV=5 tx.Transparency=.35 tx.Color3=C(200,245,255) tx.Parent=p
   end
  end
  if typeof(a.fa)=='string' and typeof(a.fb)=='string' then
   local function conv(s) local t=s:split(',') return base+V(-tonumber(t[1]),tonumber(t[3]),tonumber(t[2])) end
   p:SetAttribute('FlowA',conv(a.fa)) p:SetAttribute('FlowB',conv(a.fb)) p:SetAttribute('FlowPhase',(p.Position.Z%17)/17)
  end
  for _,k in {'text','textcolor','emblem','emblemface','ink','light','fx','swirl','fa','fb'} do p:SetAttribute(k,nil) end
 end
end

function M.build(parent,area)
 local source=SS:FindFirstChild('DragonBallArea')
 assert(source,'[CapsuleIsland] ServerStorage.DragonBallArea nao encontrado')
 local c=area.centro local base=c+V(0,6,0)
 parent.ModelStreamingMode=Enum.ModelStreamingMode.PersistentPerPlayer
 parent:SetAttribute('WorldRevision',7) parent:SetAttribute('BoundsHalfSize',V(204,140,210))
 local model=source:Clone() model.Name='ValeCapsule'
 local gameplay=model:FindFirstChild('Gameplay') gameplay.Parent=nil
 model:PivotTo(model:GetPivot()+base)
 model.Parent=parent
 decorate(model,base)

 local entry,safe,gacha,returnPad,boss,nextArea
 local spawns,zones,blocks={}, {}, {}
 local i=0
 for _,m in gameplay:GetChildren() do
  local pos=base+m.Position
  local n=m.Name
  if n=='GP_Entry' then entry=pos elseif n=='GP_Safe' then safe=pos elseif n=='GP_Gacha' then gacha=pos
  elseif n=='GP_ReturnPad' then returnPad=pos elseif n=='GP_Boss' then boss=pos elseif n=='GP_NextArea' then nextArea=pos
  elseif n=='GP_Zone' then table.insert(zones,{nome=m:GetAttribute('zone'),centro=pos,tamanho=V(m:GetAttribute('sizeX'),0,m:GetAttribute('sizeZ'))})
  elseif n=='GP_Block' then table.insert(blocks,{pos=pos,raio=m:GetAttribute('radius') or 6})
  elseif n=='GP_Ore' then i+=1 table.insert(spawns,{pos=pos,variant=i%8==0 and 3 or i%4==0 and 2 or 1,zona=m:GetAttribute('zone')}) end
 end
 gameplay:Destroy()
 parent:SetAttribute('EntryPosition',entry) parent:SetAttribute('SafePosition',safe) parent:SetAttribute('GachaPosition',gacha)

 -- invocacao: a maquina fica no centro do selo das esferas
 local machine=workspace.Gachas:FindFirstChild('Gacha_'..area.tema)
 if machine and machine:FindFirstChild('PadGacha') and gacha then
  local pad=machine.PadGacha
  machine:PivotTo(machine:GetPivot()+gacha-pad.Position)
  pad.Size=V(10,.25,10) pad.Transparency=.75
  for _,d in machine:GetDescendants() do
   if d:IsA('BillboardGui') then d.MaxDistance=45 elseif d:IsA('BasePart') then d.CanTouch=false end
  end
 end

 -- portal de progressao (o Main liga o ProximityPrompt em partes com NextAreaId)
 if nextArea then
  local pad=Instance.new('Part') pad.Name='ViagemProximaArea' pad.Anchored=true pad.CanCollide=false pad.CanQuery=true pad.CanTouch=false
  pad.Size=V(12,.2,9) pad.CFrame=CFrame.new(nextArea)*CFrame.Angles(0,-pi/4,0) pad.Transparency=.9 pad.Material=Enum.Material.Neon
  pad.Color=C(120,230,255) pad:SetAttribute('NextAreaId',area.id+1) pad.Parent=model
 end

 -- limites invisiveis nas bordas da ilha
 local limits=Instance.new('Model') limits.Name='LimitesDaArea' limits.Parent=parent
 local function wall(size,offset)
  local p=Instance.new('Part') p.Name='Limite' p.Anchored=true p.Transparency=1 p.CanCollide=true p.CanQuery=false p.CanTouch=false
  p.Size=size p.Position=base+offset p.Parent=limits
 end
 wall(V(6,300,430),V(200,100,0)) wall(V(6,300,430),V(-200,100,0))
 wall(V(410,300,6),V(0,100,-208)) wall(V(410,300,6),V(0,100,204))
 wall(V(410,4,420),V(0,190,0))

 return {spawns=spawns,boss=boss,returnPad=returnPad,zonas={lista=zones,bloqueios=blocks}}
end

return M

