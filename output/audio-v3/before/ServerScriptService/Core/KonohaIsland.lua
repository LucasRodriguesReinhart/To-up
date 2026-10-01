-- Vila da Folha (Konoha). Modelada no Blender (pasta konoha_area/) e reconstruida em Parts em ServerStorage.KonohaArea.
-- Aqui a ilha e clonada para a Area 1, os atributos decorativos viram SurfaceGui/luz/particulas e os
-- marcadores GP_* viram entrada, chefe, portal, invocacao e zonas de mineracao.
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
 g.LightInfluence=.35 g.MaxDistance=320 g.Parent=part
 return g
end

local function leaf(part,ink)
 for _,face in {Enum.NormalId.Front,Enum.NormalId.Back} do
  local g=surface(part,face) g.CanvasSize=Vector2.new(256,256)
  local function line(x1,y1,x2,y2,w)
   local a,b=Vector2.new(x1,y1),Vector2.new(x2,y2) local f=Instance.new('Frame') f.BorderSizePixel=0 f.BackgroundColor3=ink
   f.AnchorPoint=Vector2.new(.5,.5) f.Position=UDim2.fromOffset((x1+x2)/2,(y1+y2)/2) f.Size=UDim2.fromOffset((a-b).Magnitude,w or 9)
   f.Rotation=math.deg(math.atan2(y2-y1,x2-x1)) f.Parent=g
  end
  local prev for i=0,36 do local a=i/36*pi*3.4 local r=8+i*1.4 local x,y=133+math.cos(a)*r,122+math.sin(a)*r if prev then line(prev[1],prev[2],x,y,9) end prev={x,y} end
  line(80,141,50,208) line(50,208,111,189) line(111,189,99,165) line(161,84,203,42)
 end
end

local function label(part,words,color)
 local g=surface(part) g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.PixelsPerStud=30
 local t=Instance.new('TextLabel') t.Size=UDim2.fromScale(.92,.84) t.Position=UDim2.fromScale(.04,.08)
 t.BackgroundTransparency=1 t.Text=words t.TextScaled=true t.Font=Enum.Font.GothamBlack
 t.TextColor3=color or C(250,238,206) t.TextStrokeTransparency=.75 t.Parent=g
 -- placas verticais (mais altas que largas) empilham as letras
 if part.Size.Y>part.Size.X*1.6 and not words:find(' ') then t.Text=table.concat(words:split(''),'\n') end
end

local FX={
 waterfall={tex='rbxasset://textures/particles/smoke_main.dds',color=C(225,244,252),rate=6,size=6,speed=2,acc=V(0,.6,0),life=2.5},
 mist={tex='rbxasset://textures/particles/smoke_main.dds',color=C(220,240,250),rate=4,size=7,speed=1,acc=V(0,.4,0),life=3},
 fountain={tex='rbxasset://textures/particles/sparkles_main.dds',color=C(170,230,255),rate=3,size=.4,speed=2,acc=V(0,-1,0),life=2},
 fire={tex='rbxasset://textures/particles/fire_main.dds',color=C(255,150,60),rate=14,size=1.6,speed=3,acc=V(0,3,0),life=.9},
 portal={tex='rbxasset://textures/particles/sparkles_main.dds',color=C(130,230,255),rate=8,size=.5,speed=1.5,acc=V(0,1.2,0),life=2.5},
 summon={tex='rbxasset://textures/particles/sparkles_main.dds',color=C(205,140,255),rate=10,size=.6,speed=2,acc=V(0,1.6,0),life=3},
 smoke={tex='rbxasset://textures/particles/smoke_main.dds',color=C(200,196,188),rate=2,size=1.4,speed=1,acc=V(.2,1.2,0),life=4},
}

local function emitter(part,kind)
 local s=FX[kind] if not s then return end
 local e=Instance.new('ParticleEmitter') e.Texture=s.tex e.Color=ColorSequence.new(s.color) e.Rate=s.rate
 e.Lifetime=NumberRange.new(s.life*.7,s.life) e.Speed=NumberRange.new(s.speed*.4,s.speed) e.SpreadAngle=Vector2.new(35,35)
 e.Acceleration=s.acc e.LightEmission=kind=='fire' and .8 or .3
 e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,s.size*.5),NumberSequenceKeypoint.new(.5,s.size),NumberSequenceKeypoint.new(1,s.size*.3)})
 e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(.2,.4),NumberSequenceKeypoint.new(.8,.7),NumberSequenceKeypoint.new(1,1)})
 e:SetAttribute('FolhaAmbient',true) e.Parent=part
end

local function decorate(model,base)
 swapTrees(model)
 require(script.Parent.StylizedWater).apply(model,base)
 local lights=0
 for _,p in model:GetDescendants() do
  if not p:IsA('BasePart') then continue end
  local a=p:GetAttributes()
  if not next(a) then continue end
  if a.text then label(p,tostring(a.text),rgb(a.textcolor)) end
  if a.emblem=='leaf' then leaf(p,p.Color.R+p.Color.G+p.Color.B>1.6 and C(60,52,46) or C(250,236,200)) end
  if typeof(a.light)=='string' and lights<60 then
   local t=a.light:split(',')
   local l=Instance.new('PointLight') l.Color=C(tonumber(t[1]),tonumber(t[2]),tonumber(t[3]))
   l.Range=tonumber(t[4]) or 12 l.Brightness=tonumber(t[5]) or .8 l.Shadows=false l.Parent=p lights+=1
  end
  if typeof(a.fx)=='string' and a.fx~='' then emitter(p,a.fx) end
  if a.fx=='waterfall' or p.Name=='Cachoeira' or p.Name=='CachoeiraBorda' then
   local tx=Instance.new('Texture') tx.Name='FluxoCachoeira' tx.Texture='rbxasset://textures/particles/water_main.dds'
   tx.Face=Enum.NormalId.Front tx.StudsPerTileU=6 tx.StudsPerTileV=12 tx.Transparency=.55 tx.Parent=p
  end
  if p.Name=='Agua' then
   local tx=Instance.new('Texture') tx.Name='OndasDaIlha' tx.Texture='rbxasset://textures/particles/water_main.dds'
   tx.Face=Enum.NormalId.Top tx.StudsPerTileU=18 tx.StudsPerTileV=22 tx.Transparency=.85 tx.Parent=p
  end
  if a.swirl then
   -- energia do portal: a textura corre (o AmbienteFolha anima FluxoCachoeira)
   for _,face in {Enum.NormalId.Left,Enum.NormalId.Right} do
    local tx=Instance.new('Texture') tx.Name='FluxoCachoeira' tx.Texture='rbxasset://textures/particles/water_main.dds'
    tx.Face=face tx.StudsPerTileU=5 tx.StudsPerTileV=5 tx.Transparency=.35 tx.Color3=C(200,255,220) tx.Parent=p
   end
  end
  if a.sway then p:SetAttribute('IslandSway',true) p:SetAttribute('SwayPhase',p.Position.X*.07) end
  if typeof(a.fa)=='string' and typeof(a.fb)=='string' then
   local function conv(s) local t=s:split(',') return base+V(-tonumber(t[1]),tonumber(t[3]),tonumber(t[2])) end
   p:SetAttribute('FlowA',conv(a.fa)) p:SetAttribute('FlowB',conv(a.fb)) p:SetAttribute('FlowPhase',(p.Position.Z%17)/17)
  end
  for _,k in {'text','textcolor','emblem','light','fx','sway','swirl','fa','fb'} do p:SetAttribute(k,nil) end
 end
end

-- arvores de Parts (bolas num palito) -> arvores de malha com copa de folhas (ServerStorage.DragonBallKit)
local TREE_SWAP={Arvore_Folha_G='Arvore_Konoha_G',Arvore_Folha_M='Arvore_Konoha_M',Arvore_Gigante='Arvore_Konoha_Gigante',Cedro='Cedro_Konoha'}
function swapTrees(model)
 local kit=SS:FindFirstChild('DragonBallKit') if not kit then return 0 end
 local rng=Random.new(77) local n=0
 for _,m in model:GetDescendants() do
  if not m:IsA('Model') then continue end
  local key=m.Name:gsub('%.%d+$','')
  local tpl=TREE_SWAP[key] and kit:FindFirstChild(TREE_SWAP[key])
  if not tpl then continue end
  local cf,size=m:GetBoundingBox()
  local trunk=m:FindFirstChild('Tronco')
  local basePos=trunk and trunk.Position or cf.Position
  basePos=Vector3.new(basePos.X,cf.Position.Y-size.Y/2,basePos.Z)
  local tcf,tsize=tpl:GetBoundingBox()
  local s=math.clamp(size.Y/math.max(tsize.Y,1),.6,2.2)
  local c=tpl:Clone()
  if math.abs(s-1)>.01 then c:ScaleTo(s) end
  c:PivotTo(CFrame.new(basePos)*CFrame.Angles(0,rng:NextNumber(0,math.pi*2),0))
  c.Name=m.Name c.Parent=m.Parent
  m:Destroy() n+=1
 end
 return n
end

function M.build(parent,area)
 local source=SS:FindFirstChild('KonohaArea')
 assert(source,'[KonohaIsland] ServerStorage.KonohaArea nao encontrado')
 local c=area.centro local base=c+V(0,6,0)
 parent.ModelStreamingMode=Enum.ModelStreamingMode.PersistentPerPlayer
 parent:SetAttribute('WorldRevision',6) parent:SetAttribute('BoundsHalfSize',V(196,130,200))
 local model=source:Clone() model.Name='VilaDaFolha'
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

 -- invocacao: a maquina fica no centro do selo do santuario
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
 wall(V(6,300,420),V(192,100,0)) wall(V(6,300,420),V(-192,100,0))
 wall(V(390,300,6),V(0,100,-204)) wall(V(390,300,6),V(0,100,200))
 wall(V(390,4,410),V(0,178,0))

 return {spawns=spawns,boss=boss,returnPad=returnPad,zonas={lista=zones,bloqueios=blocks}}
end

return M

