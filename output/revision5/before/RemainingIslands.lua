-- Remaining themed islands: Natagumo, Grand Line and Cidade Z.
-- Uses the same original Plastic/Studs surfaces, trees and playable terraces.
local M={}
local V=Vector3.new
local C=Color3.fromRGB
local pi=math.pi
local THEMES={
 [3]={name="MonteNatagumo",rock=C(92,109,112),soil=C(158,171,166),grass=C(79,151,75),wood=C(90,62,51),trim=C(43,49,62),accent=C(89,215,194),water=C(53,153,191),light=C(255,192,116)},
 [5]={name="GrandLine",rock=C(183,141,94),soil=C(228,204,149),grass=C(109,198,49),wood=C(124,81,44),trim=C(63,58,54),accent=C(42,181,224),water=C(29,159,219),light=C(255,204,111)},
 [6]={name="CidadeZ",rock=C(119,128,134),soil=C(178,185,181),grass=C(108,175,65),wood=C(108,91,66),trim=C(56,67,80),accent=C(245,132,63),water=C(45,150,176),light=C(230,239,218)},
}
function M.build(parent,area)
 local theme=assert(THEMES[area.id],"Unsupported island")
 local c=area.centro local rng=Random.new(4400+area.id)
 local root=Instance.new("Model") root.Name=theme.name root.Parent=parent
 local function folder(name) local f=Instance.new("Model") f.Name=name f.Parent=root return f end
 local land=folder("IlhaETerracos") local art=folder("Arquitetura")
 local plants=folder("Vegetacao") local props=folder("Detalhes") local waters=folder("RiosECachoeiras")
 local function p(name,size,pos,col,group,rot,collide,mat)
  local part=Instance.new("Part") part.Name=name part.Anchored=true part.Size=size
  part.CFrame=CFrame.new(c+pos)*(rot or CFrame.identity) part.Color=col
  part.Material=mat or Enum.Material.Plastic
  part.TopSurface=Enum.SurfaceType.Smooth part.BottomSurface=Enum.SurfaceType.Smooth
  part.CanCollide=collide~=false part.CanTouch=false part.CanQuery=part.CanCollide
  part.Parent=group or props return part
 end
 local function b(name,size,pos,col,group,rot)
  local part=p(name,size,pos,col,group,rot) part.TopSurface=Enum.SurfaceType.Studs return part
 end
 local function rod(name,a,z,width,col,group,mat)
  return p(name,V(width,width,(z-a).Magnitude),(a+z)/2,col,group,CFrame.lookAt(a,z).Rotation,false,mat)
 end
 local function cylinder(name,radius,height,pos,col,group)
  local part=p(name,V(height,radius*2,radius*2),pos,col,group,CFrame.Angles(0,0,pi/2)) part.Shape=Enum.PartType.Cylinder return part
 end
 local function sphere(name,size,pos,col,group)
  local part=p(name,size,pos,col,group,nil,false) part.Shape=Enum.PartType.Ball return part
 end
 local function text(board,words,color)
  local g=Instance.new("SurfaceGui") g.Adornee=board g.Face=Enum.NormalId.Front
  g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.PixelsPerStud=32 g.MaxDistance=220 g.LightInfluence=.35 g.Parent=board
  if #words>0 and #words<=3 then g.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize g.CanvasSize=Vector2.new(128,128) end
  local l=Instance.new("TextLabel") l.Size=UDim2.fromScale(.92,.88) l.Position=UDim2.fromScale(.04,.06)
  l.BackgroundTransparency=1 l.Font=Enum.Font.GothamBlack l.Text=words l.TextScaled=true l.TextColor3=color or C(248,239,211) l.Parent=g
  return g
 end
 local function sign(words,pos,w,h,color)
  local board=p("Placa",V(w,h,.45),pos,color or theme.trim,art,nil,false,Enum.Material.Wood)
  text(board,words)
  for _,x in ipairs({-w/2,w/2}) do p("MolduraPlaca",V(.3,h+.5,.65),pos+V(x,0,0),theme.wood,art,nil,false) end
  return board
 end
 local function lamp(pos,scale)
  scale=scale or 1
  p("BaseLanterna",V(1.3,.5,1.3)*scale,pos+V(0,.25,0)*scale,theme.trim,props)
  p("PosteLanterna",V(.5,3,.5)*scale,pos+V(0,1.9,0)*scale,theme.wood,props)
  local bulb=p("LuzLanterna",V(.85,1.25,.85)*scale,pos+V(0,3.9,0)*scale,theme.light,props,nil,false,Enum.Material.Neon)
  p("CoberturaLanterna",V(1.5,.35,1.5)*scale,pos+V(0,4.7,0)*scale,theme.trim,props)
  for _,x in ipairs({-.53,.53}) do for _,z in ipairs({-.53,.53}) do p("ArmaçaoLanterna",V(.12,1.45,.12)*scale,pos+V(x,3.9,z)*scale,theme.trim,props,nil,false) end end
  local l=Instance.new("PointLight") l.Color=theme.light l.Brightness=.65 l.Range=12*scale l.Shadows=false l.Parent=bulb
 end
 local function fence(a,z)
  local n=math.max(1,math.ceil((z-a).Magnitude/5))
  for i=0,n do p("Mourao",V(.65,3.3,.65),a:Lerp(z,i/n)+V(0,1.65,0),theme.wood,props,nil,true,Enum.Material.Wood) end
  for _,h in ipairs({1.3,2.8}) do rod("GuardaCorpo",a+V(0,h,0),z+V(0,h,0),.35,theme.wood,props,Enum.Material.Wood) end
 end
 local function ledge(x,z,w,d,h)
  b("Estrato",V(w,h+5,d),V(x,(h-5)/2,z),theme.rock:Lerp(C(213,196,169),rng:NextNumber(0,.12)),land)
  b("TopoGrama",V(w+.3,.8,d+.3),V(x,h+.05,z),theme.grass,land)
 end
 local function stairs(pos,width,n,rise,run)
  for i=1,n do b("Degrau",V(width,i*rise,run+.1),pos+V(0,i*rise/2,(i-.5)*run),theme.soil,land) end
 end
 local function bridge(a,z,width,arch)
  local delta=z-a local n=math.ceil(delta.Magnitude/2.1) local side=V(-delta.Unit.Z,0,delta.Unit.X)
  local prev
  for i=0,n do
   local t=i/n local q=a:Lerp(z,t)+V(0,math.sin(t*pi)*arch,0)
   p("TabuaPonte",V(width,.45,delta.Magnitude/n+.07),q,theme.wood:Lerp(C(194,145,91),i%3*.08),art,CFrame.lookAt(q,q+delta).Rotation,true,Enum.Material.Wood)
   for _,s in ipairs({-1,1}) do
    if i%3==0 or i==n then p("PostePonte",V(.6,3,.6),q+side*s*(width/2-.2)+V(0,1.5,0),theme.wood,art) end
    if prev then rod("CorrimaoPonte",prev+side*s*(width/2-.2)+V(0,2.7,0),q+side*s*(width/2-.2)+V(0,2.7,0),.33,theme.wood,art,Enum.Material.Wood) end
   end
   prev=q
  end
 end
 local function tree(pos,scale,wisteria)
  local original=workspace.LobbyRenovado.OriginalArt:FindFirstChild("Arvore") if not original then return end
  local model=original:Clone() model.Name=wisteria and "Glicinia" or "ArvoreOriginal"
  model:ScaleTo(original:GetScale()*scale) local cf,sz=model:GetBoundingBox()
  model:PivotTo(model:GetPivot()+c+pos+V(0,sz.Y/2,0)-cf.Position)
  for _,d in ipairs(model:GetDescendants()) do if d:IsA("BasePart") then
   d.CanCollide=d.Name:lower():find("tronco")~=nil d.CanTouch=false d.CanQuery=d.CanCollide
   if wisteria and d.Name:lower():find("folhagem") then d.Color=C(147+rng:NextInteger(0,28),101,194+rng:NextInteger(0,24)) end
  end end
  model.Parent=plants
  if wisteria then
   for i=1,9 do
    local a=i/9*2*pi local q=pos+V(math.cos(a)*3,sz.Y*.64,math.sin(a)*3)
    p("FloresPendentes",V(.5,2+i%3,.55),q,C(199,153,234),plants,nil,false)
   end
  end
 end
 local function palm(pos,height)
  for i=0,4 do p("TroncoPalmeira",V(.9,height/5+.2,.9),pos+V(i*.18,(i+.5)*height/5,0),C(139-i*6,103-i*4,65),plants,CFrame.Angles(0,0,-.07),false) end
  for i=0,7 do
   local a=i*pi/4 local dir=V(math.cos(a),0,math.sin(a))
   for j=1,3 do p("FolhaPalmeira",V(2.2,.5,2.4),pos+V(.8,height+.9-(j-1)^2*.6,0)+dir*j*1.5,C(58,153-j*8,66),plants,CFrame.Angles(0,-a,.08),false) end
  end
 end
 local function bamboo(pos,height)
  for i=1,3 do
   local off=V((i-2)*1.1,0,i%2)
   p("Bambu",V(.4,height,.4),pos+off+V(0,height/2,0),C(71,123+i*8,60),plants,nil,false)
   for y=2,height,2 do p("NoBambu",V(.51,.16,.51),pos+off+V(0,y,0),C(136,173,78),plants,nil,false) end
   for j=1,4 do p("FolhaBambu",V(2.5,.15,.55),pos+off+V(j%2==0 and 1 or -1,height-1-j*.7,0),C(62,137,72),plants,CFrame.Angles(0,j,.2),false) end
  end
 end
 local function emit(pos,color,rate,texture,size)
  local anchor=p("AmbienteVFX",V(.1,.1,.1),pos,color,waters,nil,false) anchor.Transparency=1
  local a=Instance.new("Attachment") a.Parent=anchor
  local e=Instance.new("ParticleEmitter") e.Texture=texture e.Color=ColorSequence.new(color)
  e.Rate=rate e.Lifetime=NumberRange.new(1.4,2.8) e.Speed=NumberRange.new(.3,1.5) e.SpreadAngle=Vector2.new(55,55)
  e.Size=NumberSequence.new(size) e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.65),NumberSequenceKeypoint.new(.6,.7),NumberSequenceKeypoint.new(1,1)})
  e:SetAttribute("FolhaAmbient",true) e.Parent=a
 end
 local function waterfall(x,z,height,width)
  for i=0,4 do
   local part=p("QuedaDagua",V(width/5+.12,height,1.4),V(x+(i-2)*width/5,height/2+.3,z),theme.water:Lerp(C(172,219,238),i%2*.22),waters,nil,false)
   part.Transparency=.17
   local tx=Instance.new("Texture") tx.Name="FluxoCachoeira" tx.Texture="rbxasset://textures/particles/water_main.dds" tx.Face=Enum.NormalId.Front tx.StudsPerTileU=5 tx.StudsPerTileV=9 tx.Transparency=.6 tx.Parent=part
  end
  emit(V(x,1,z-2),C(190,224,227),7,"rbxasset://textures/particles/smoke_main.dds",5)
 end
 local function crate(pos)
  p("Caixote",V(2.6,2.6,2.6),pos+V(0,1.3,0),theme.wood,props,nil,true,Enum.Material.Wood)
  for _,y in ipairs({.3,2.3}) do p("CintaCaixote",V(2.75,.23,2.75),pos+V(0,y,0),theme.trim,props,nil,false) end
  rod("ReforcoCaixa",pos+V(-1, .3,-1.32),pos+V(1,2.3,-1.32),.18,C(175,132,82),props)
 end
 local function house(pos,w,d,h,roofColor,label,japanese)
  b("Fundacao",V(w+3,1,d+3),pos+V(0,.5,0),theme.rock,art)
  p("Paredes",V(w,h,d),pos+V(0,h/2+1,0),japanese and C(197,190,161) or C(224,198,145),art)
  for _,x in ipairs({-w/2,0,w/2}) do p("PilarCasa",V(.7,h+.8,.7),pos+V(x,h/2+1,-d/2-.15),theme.wood,art) end
  for _,x in ipairs({-w*.29,w*.29}) do
   p("Janela",V(w*.21,h*.42,.22),pos+V(x,h*.6,-d/2-.2),C(237,205,126),art,nil,false,Enum.Material.Plastic)
   for j=-1,1 do p("GradeJanela",V(.18,h*.43,.25),pos+V(x+j*w*.065,h*.6,-d/2-.4),theme.wood,art,nil,false) end
  end
  p("Porta",V(w*.14,h*.66,.3),pos+V(0,h*.33+1,-d/2-.25),theme.trim,art,nil,false)
  for side=-1,1,2 do for row=0,5 do
   local q=pos+V(0,h+4.2-row*.64,side*(row+.5)*(d+6)/12)
   p("TelhadoEmCamadas",V(w+5,.65,(d+6)/12+.15),q,roofColor:Lerp(theme.trim,row*.035),art,CFrame.Angles(side*.24,0,0))
  end end
  p("Cumeeira",V(w+6,.8,.8),pos+V(0,h+4.6,0),theme.trim,art)
  if label then sign(label,pos+V(0,h*.83,-d/2-.7),w*.7,2.8) end
  for _,x in ipairs({-w/2-1,w/2+1}) do lamp(pos+V(x,1,-d/2-1),.8) end
 end

 -- The shared island scale matches the established quarry areas.
 local water=p("AguaDaIlha",V(232,.4,215),V(0,.2,0),theme.water,waters,nil,false) water.Transparency=.18
 cylinder("BaseRochosa",75,9,V(0,.8,0),theme.rock,land)
 cylinder("BordaGramada",76,1,V(0,5,0),theme.grass,land)
 cylinder("PracaCentral",68,.6,V(0,5.65,0),theme.soil,land)
 for x=-60,60,10 do for z=-60,60,10 do if x*x+z*z<65^2 then
  b("PisoOriginal",V(9.96,.15,9.96),V(x,5.97,z),theme.soil:Lerp(C(239,229,207),rng:NextNumber(0,.07)),land)
 end end end
 b("AcessoEntrada",V(20,5.2,30),V(0,2.6,-85),theme.soil,land)
 stairs(V(0,0,-111),20,6,.88,2.2) stairs(V(0,5.2,-71),20,1,.85,4)
 for side=-1,1,2 do for i=0,5 do
  local z=-72+i*31 local h=25+rng:NextInteger(0,17)
  if not(area.id==5 and side==1 and i>=1 and i<=3) then
   ledge(side*104,z,26,32,h)
   if not(side==-1 and i==3) then
    ledge(side*87,z+3,14,16,h*.48)
    tree(V(side*87,h*.48+.6,z+3),.58,area.id==3 and i%2==0)
   end
   if i%2==0 then tree(V(side*104,h+.7,z),.65,area.id==3 and i%3==0) end
  end
 end end
 for _,x in ipairs({-100,-74,-48,48,74,100}) do
  local h=35+rng:NextInteger(0,18) ledge(x,97,28,27,h) tree(V(x,h+.7,96),.65,area.id==3)
 end
 for _,x in ipairs({-126,-94,-62,-30,2,34,66,98,130}) do ledge(x,129,33,20,52+rng:NextInteger(0,13)) end
 for _,side in ipairs({-1,1}) do for _,z in ipairs({-38,3,44,85}) do ledge(side*131,z,22,42,45+rng:NextInteger(0,15)) end end
 for _,x in ipairs({-24,0,24}) do ledge(x,108,26,16,36) end
 -- A central stair and a separate side mine/portal leave the ore field open.
 ledge(0,69,65,46,15)
 stairs(V(0,6,28),20,12,.8,2)
 for _,x in ipairs({-13,13}) do for _,z in ipairs({32,43,53}) do lamp(V(x,6+(z-28)*.4,z),.85) end end
 for _,q in ipairs({{-15,-60},{15,-60},{-54,-27},{54,-27},{-54,21},{54,25}}) do lamp(V(q[1],6,q[2]),.95) end
 for _,side in ipairs({-1,1}) do
  fence(V(side*65,6,-35),V(side*65,6,-9))
  for z=-80,60,10 do
   local a=V(side*81,.5,z+4) local z2=V(side*80,.5,z-6)
   local current=p("CorrenteFolha",V(.25,.06,2.2),a,C(157,224,244),waters,nil,false,Enum.Material.Neon)
   current:SetAttribute("FlowA",c+a) current:SetAttribute("FlowB",c+z2) current:SetAttribute("FlowPhase",rng:NextNumber()) current.Transparency=.55
  end
 end
 b("TerraçoGacha",V(28,6,26),V(-66,2.8,-63),theme.rock,land)
 b("PisoGacha",V(28.3,.4,26.3),V(-66,6,-63),theme.soil,land)
 fence(V(-79,6,-75),V(-79,6,-52))
 lamp(V(-77,6,-74),.9)
 bridge(V(-40,6,-53),V(-66,6,-65),10,.8)
 bridge(V(-58,6,16),V(-73,12,23),10,.55)
 if area.id~=5 then
  ledge(82,27,29,32,11)
  bridge(V(58,6,16),V(73,12,23),10,.55)
 end
 -- Small rock faces, shrubs and props echo the original world art.
 for _,q in ipairs({{-51,-55},{50,-54},{-68,-21},{68,39},{-48,56},{47,58}}) do
  b("RochedoMargem",V(12,7,10),V(q[1],2,q[2]),theme.rock,land,CFrame.Angles(0,.28,0))
  b("GramaDaMargem",V(12.2,.6,10.2),V(q[1],5.8,q[2]),theme.grass,land,CFrame.Angles(0,.28,0))
 end
 for i=1,30 do
  local a=i/30*pi*2 local rad=70+rng:NextNumber(0,3)
  local q=V(math.sin(a)*rad,6,math.cos(a)*rad)
  b("SeixoComMusgo",V(1.4+i%3,.7,1.6),q,theme.rock:Lerp(theme.grass,.25),props)
 end

 if area.id==3 then
  -- Mountain estate with layered roofs, wisteria and bamboo.
  house(V(0,16,73),43,23,12,C(62,70,90),"MONTE NATAGUMO",true)
  house(V(0,32,75),26,15,8,C(57,66,89),nil,true)
  house(V(65,12,0),22,19,9,C(74,72,84),"DOJO NICHIRIN",true)
  ledge(67,0,30,32,11)
  stairs(V(61,6,-29),14,7,.8,2)
  local function torii(pos,w,h)
   for _,x in ipairs({-w/2,w/2}) do p("PilarTorii",V(1.25,h,1.25),pos+V(x,h/2,0),C(146,62,53),art) end
   p("TraveTorii",V(w+4,1.4,2),pos+V(0,h,0),theme.trim,art)
   p("TraveInferiorTorii",V(w+2,.7,1),pos+V(0,h-2.6,0),C(146,62,53),art)
  end
  torii(V(0,5.3,-83),24,16) torii(V(0,16,48),24,16)
  for _,q in ipairs({{-38,6,36},{38,6,40},{-63,6,-30},{62,6,-36},{-39,6,-55},{30,6,-62},{-29,16,59},{29,16,60}}) do tree(V(q[1],q[2],q[3]),.8,true) end
  for _,q in ipairs({{-66,6,30},{61,6,30},{77,12,-15},{-79,12,30},{22,16,83},{-23,16,83}}) do bamboo(V(q[1],q[2],q[3]),14) end
  local function web(pos,r)
   local points={}
   for i=0,7 do
    local a=i*pi/4 local v=V(math.cos(a)*r,math.sin(a)*r,0)
    points[i+1]=v rod("FioTeia",pos,pos+v,.075,C(205,215,222),art)
   end
   for _,fraction in ipairs({.3,.55,.8}) do for i=1,8 do
    local nextI=i%8+1 rod("FioTeia",pos+points[i]*fraction,pos+points[nextI]*fraction,.06,C(200,213,224),art)
   end end
  end
  web(V(89,25,35),10) web(V(-90,30,72),12)
  local blade=p("LaminaNichirin",V(.65,13,1.2),V(28,24,61),C(176,226,225),art,nil,false,Enum.Material.Metal)
  p("GuardaKatana",V(4,.55,2),V(28,30.7,61),C(184,151,82),art,nil,false)
  p("CaboKatana",V(.9,4,1),V(28,33,61),C(93,45,48),art,nil,false)
  waterfall(76,66,38,11) waterfall(-77,39,29,9)
  for _,q in ipairs({{-45,8,47},{43,8,47},{25,8,-48}}) do emit(V(q[1],q[2],q[3]),C(175,229,199),1.3,"rbxasset://textures/particles/sparkles_main.dds",.2) end
  sign("MINAS\nNICHIRIN",V(64,13,-43),16,7)
 elseif area.id==5 then
  -- The pirate port opens on the east side to a full ship and timber quays.
  house(V(0,16,74),40,24,13,C(158,65,43),"GRAND LINE",false)
  house(V(-65,12,0),20,19,9,C(70,112,139),"ARMAZEM",false)
  ledge(-68,0,29,32,11)
  stairs(V(-63,6,-29),14,7,.8,2)
  for _,q in ipairs({{-30,16,54},{30,16,54},{-48,6,33},{47,6,-30},{-45,6,-46},{35,6,-60},{65,6,-37}}) do palm(V(q[1],q[2],q[3]),13) end
  local ship=V(89,0,9)
  b("CascoNavio",V(18,5,39),ship+V(0,2.6,0),C(89,52,32),art)
  for i=1,4 do b("ProaNavio",V(18-i*3,4,3),ship+V(0,3,-19-i*2),C(108,66,37),art) end
  for z=-17,18,2 do p("Conves",V(17,.5,1.95),ship+V(0,5.4,z),C(157+z%3*5,111,66),art,nil,true,Enum.Material.Wood) end
  for _,x in ipairs({-8.3,8.3}) do fence(ship+V(x,5.6,-16),ship+V(x,5.6,18)) end
  house(ship+V(0,5.8,12),13,10,5,C(119,51,37),nil,false)
  for _,q in ipairs({{0,29,0},{0,24,-15}}) do
   local h=q[2]
   p("MastroNavio",V(.9,h,.9),ship+V(q[1],5+h/2,q[3]),theme.wood,art,nil,false,Enum.Material.Wood)
   p("Verga",V(q[3]==0 and 22 or 15,.55,.55),ship+V(0,5+h-2,q[3]),theme.wood,art,nil,false)
   local sail=p("VelaPirata",V(q[3]==0 and 20 or 13,h*.61,.25),ship+V(0,5+h*.62,q[3]-.4),C(237,226,193),art,nil,false)
   if q[3]==0 then
    local g=text(sail,"",theme.trim) g:ClearAllChildren() g.SizingMode=Enum.SurfaceGuiSizingMode.FixedSize g.CanvasSize=Vector2.new(256,256)
    local function shape(x,y,w,h,col,round,rot)
     local f=Instance.new("Frame") f.BorderSizePixel=0 f.Position=UDim2.fromOffset(x,y) f.Size=UDim2.fromOffset(w,h) f.BackgroundColor3=col f.Rotation=rot or 0 f.Parent=g
     if round then local u=Instance.new("UICorner") u.CornerRadius=UDim.new(1,0) u.Parent=f end
    end
    shape(50,179,158,10,theme.trim,true,28) shape(50,179,158,10,theme.trim,true,-28)
    shape(78,79,102,103,theme.trim,true) shape(90,111,22,26,C(237,226,193),true) shape(147,111,22,26,C(237,226,193),true)
    shape(104,162,53,22,theme.trim,false) for x=112,148,12 do shape(x,162,4,19,C(237,226,193),false) end
    shape(75,59,108,41,C(220,169,72),true) shape(63,85,134,11,C(220,169,72),true) shape(79,78,100,9,C(171,59,44),false)
   end
   for _,side in ipairs({-1,1}) do rod("CordaNavio",ship+V(0,5+h,q[3]),ship+V(side*8,6,q[3]-9),.1,theme.trim,art) end
  end
  bridge(V(60,6,4),ship+V(-8,6,0),10,.4)
  ledge(95,78,24,24,14)
  cylinder("Farol",5.5,28,V(95,28,78),C(229,222,197),art)
  for _,y in ipairs({19,29,38}) do cylinder("FaixaFarol",5.65,1.8,V(95,y,78),C(155,63,45),art) end
  cylinder("VarandaFarol",7,1,V(95,42,78),theme.trim,art)
  local beacon=p("LuzFarol",V(6,5,6),V(95,45,78),C(248,224,146),art,nil,false,Enum.Material.Neon)
  cylinder("CoberturaFarol",7,1.3,V(95,48,78),C(158,65,43),art)
  for _,x in ipairs({-3.4,3.4}) do for _,z in ipairs({-3.4,3.4}) do p("GradeFarol",V(.3,5,.3),V(95+x,45,78+z),theme.trim,art) end end
  local chest=V(21,16,55)
  b("BauTesouro",V(7,4,4),chest+V(0,2,0),C(118,64,33),art)
  for _,x in ipairs({-2.5,2.5}) do p("AroDourado",V(.4,4.2,4.2),chest+V(x,2,0),C(226,178,68),art,nil,false,Enum.Material.Metal) end
  p("FechoTesouro",V(1,1.4,.2),chest+V(0,2.7,-2.15),C(226,178,68),art,nil,false)
  waterfall(-76,47,35,11) waterfall(45,87,39,12)
  for _,q in ipairs({{-77,12,-8},{-74,12,-10},{64,6,18},{67,6,21}}) do crate(V(q[1],q[2],q[3])) end
  sign("PORTO\nGRAND LINE",V(64,13,-42),17,7)
 elseif area.id==6 then
  -- A civic mining plaza framed by canals, ruined towers and the hero association.
  local asphalt=C(65,75,82)
  for _,x in ipairs({-59,59}) do
   p("Avenida",V(12,.15,92),V(x,6.14,-7),asphalt,land)
   for z=-47,33,12 do p("FaixaViaria",V(.4,.03,4),V(x,6.24,z),C(219,201,143),props,nil,false) end
  end
  p("AvenidaEntrada",V(118,.15,10),V(0,6.14,-53),asphalt,land)
  for x=-8,8,4 do p("FaixaPedestre",V(2,.03,8),V(x,6.24,-53),C(214,220,212),props,nil,false) end
  local function building(pos,w,d,h,col,name)
   b("Edificio",V(w,h,d),pos+V(0,h/2,0),col,art)
   p("CoberturaEdificio",V(w+1,.8,d+1),pos+V(0,h,0),theme.trim,art)
   for y=4,h-2,5 do for x=-w/2+3,w/2-2,5 do
    p("JanelaEdificio",V(2.4,2.8,.2),pos+V(x,y,-d/2-.11),C(128,185,195),art,nil,false,Enum.Material.Glass)
   end end
   if name then sign(name,pos+V(0,h*.67,-d/2-.4),w*.9,5,C(65,75,85)) end
  end
  building(V(0,16,76),43,24,17,C(171,180,179),"ASSOCIACAO\nDOS HEROIS")
  building(V(0,33,81),24,18,35,C(180,187,180),nil)
  p("FaixaHeroica",V(25,3,19),V(0,63,81),C(185,67,54),art)
  sign("H",V(0,57,71.7),12,13,C(225,180,71))
  for _,side in ipairs({-1,1}) do
   building(V(side*73,12,-2),18,22,25+side*3,C(127+side*12,144,150),nil)
   ledge(side*76,-1,28,30,11)
   stairs(V(side*72,6,-30),14,7,.8,2)
   for _,z in ipairs({-20,10}) do
    p("PosteUrbano",V(.4,9,.4),V(side*50,10.5,z),theme.trim,props)
    p("BracoPoste",V(3,.3,.3),V(side*49,15,z),theme.trim,props,nil,false)
    local bulb=p("Luminaria",V(2,.25,1),V(side*49,14.8,z),C(233,237,217),props,nil,false,Enum.Material.Neon)
   end
  end
  -- A simple stone superhero statue with an elevated glove and red cape.
  cylinder("PedestalHeroi",4.5,1.5,V(0,16.7,55),theme.trim,art)
  b("CorpoHeroi",V(3.2,5,2),V(0,20,55),C(192,155,65),art)
  sphere("CabecaHeroi",V(2.5,2.6,2.5),V(0,24,55),C(204,173,132),art)
  p("CapaHeroi",V(5,7,.5),V(0,20,56.6),C(170,56,50),art,CFrame.Angles(.15,0,0),false)
  for _,x in ipairs({-1,1}) do p("PernasHeroi",V(1,3,1.2),V(x,17.8,55),C(156,124,66),art) end
  rod("BracoHeroi",V(1.7,21,55),V(3,25,55),1,C(192,155,65),art)
  sphere("LuvaHeroi",V(2,2,2),V(3,26,55),C(166,61,51),art)
  p("BracoEsquerdo",V(1,4,1),V(-2,20,55),C(192,155,65),art,CFrame.Angles(0,0,.2))
  -- Construction crane and fractured concrete tie the city to mining.
  local crane=V(95,13,74)
  for _,x in ipairs({-2,2}) do for _,z in ipairs({-2,2}) do p("PilarGrua",V(.55,38,.55),crane+V(x,19,z),C(219,165,49),art,nil,false) end end
  for y=0,34,4 do
   rod("TrelicaGrua",crane+V(-2,y,-2),crane+V(2,y+4,-2),.35,C(194,136,43),art)
   rod("TrelicaGrua",crane+V(2,y,-2),crane+V(-2,y+4,-2),.35,C(194,136,43),art)
  end
  p("LancaGrua",V(40,1.2,3),crane+V(-10,39,0),C(213,160,47),art,nil,false)
  rod("CaboGrua",crane+V(-26,39,0),crane+V(-26,18,0),.12,theme.trim,art)
  p("GanchoGrua",V(1.3,1.5,.6),crane+V(-26,17.5,0),theme.trim,art,nil,false)
  for _,q in ipairs({{-44,6,40},{44,6,41},{-45,6,-37},{42,6,-38}}) do
   b("ConcretoFraturado",V(3,2,4),V(q[1],q[2],q[3]),C(134,145,147),props,CFrame.Angles(.12,.3,.2))
   crate(V(q[1]+4,q[2],q[3]))
  end
  waterfall(77,61,34,10) waterfall(-76,39,28,9)
  sign("CIDADE Z\nZONA DE MINERACAO",V(64,13,-43),19,7)
 end
 -- A floor insignia marks the plaza without introducing another obstacle.
 cylinder("AnelDaPraca",12,.09,V(0,6.2,-5),theme.trim,props)
 cylinder("CentroDaPraca",11.2,.1,V(0,6.27,-5),theme.soil,props)
 if area.id==3 then
  for _,angle in ipairs({pi/4,-pi/4}) do
   p("KatanaNoPiso",V(.6,.07,16),V(0,6.37,-5),theme.trim,props,CFrame.Angles(0,angle,0),false)
   local cf=CFrame.new(0,6.38,-5)*CFrame.Angles(0,angle,0)
   p("GuardaNoPiso",V(3.4,.06,.5),cf:PointToWorldSpace(V(0,0,4)),theme.trim,props,cf.Rotation,false)
  end
 elseif area.id==5 then
  for i=0,7 do
   local a=i*pi/4 local r=i%2==0 and 6 or 4.6
   p("RosaDosVentos",V(.7,.06,r*1.1),V(math.sin(a)*r*.6,6.38,-5+math.cos(a)*r*.6),theme.trim,props,CFrame.Angles(0,a,0),false)
   p("PontaBussola",V(1.1,.06,1.1),V(math.sin(a)*r*1.15,6.38,-5+math.cos(a)*r*1.15),theme.trim,props,CFrame.Angles(0,a+pi/4,0),false)
  end
 else
  for _,x in ipairs({-3.4,3.4}) do p("HNoPiso",V(1.6,.06,12),V(x,6.38,-5),theme.trim,props,nil,false) end
  p("HNoPiso",V(7,.06,1.8),V(0,6.38,-5),theme.trim,props,nil,false)
 end
 for _,x in ipairs({59,69}) do p("ApoioPlaca",V(.6,8,.6),V(x,9,-42.7),theme.wood,props,nil,false) end
 -- Low planted banks and seating complete the shared world style.
 for _,q in ipairs({{43,6,48},{-42,6,50},{34,16,63},{-34,16,64}}) do
  for j=0,3 do
   p("ArbustoDaIlha",V(2,1.4,2),V(q[1]+math.cos(j*1.8)*1.5,q[2]+.6,q[3]+math.sin(j*1.8)*1.5),theme.grass,plants,nil,false)
  end
 end
 for _,x in ipairs({-29,29}) do
  p("BancoDoTerraço",V(6,.45,1.5),V(x,17.8,52),theme.wood,props,nil,false,Enum.Material.Wood)
  for _,dx in ipairs({-2,2}) do p("ApoioBanco",V(.4,1.8,1.1),V(x+dx,16.8,52),theme.trim,props,nil,false) end
 end
 -- Ore mine and the progression gate share the same validated interaction hooks.
 local mine=V(-84,12,27)
 ledge(-84,27,29,35,11)
 for _,x in ipairs({-10,10}) do
  b("ColunaMina",V(4.5,16,8),mine+V(x,8,0),theme.rock,art)
  p("VigaMina",V(1.2,13,1.2),mine+V(x*.8,6.5,-5),theme.wood,art)
 end
 b("ArcoMina",V(25,5,12),mine+V(0,17,1),theme.rock,art)
 p("FundoTunel",V(17,14,.4),mine+V(0,7,9),C(24,29,34),art)
 p("PisoTunel",V(17,.4,19),mine+V(0,.2,1),theme.soil,art)
 sign(area.id==3 and "MINAS NICHIRIN" or area.id==5 and "MINAS DA MARE" or "MINAS DA CIDADE Z",mine+V(0,17,-5.2),22,4.3)
 for _,x in ipairs({-8,8}) do lamp(mine+V(x,0,-7),.9) end
 for z=-10,7,2.3 do p("DormenteMina",V(6,.25,.5),mine+V(0,.45,z),theme.wood,art) end
 for _,x in ipairs({-2,2}) do rod("Trilho",mine+V(x,.7,-10),mine+V(x,.7,7),.23,C(121,132,142),art,Enum.Material.Metal) end
 b("Vagoneta",V(4,2.7,4),mine+V(0,1.9,4),theme.trim,art)
 crate(mine+V(10,0,-5))
 local exit=V(-79,12,75)
 ledge(-79,77,28,27,11)
 bridge(V(-55,6,46),V(-79,12,65),10,1.2)
 for _,x in ipairs({-9,9}) do b("PilarPortal",V(3,17,4),exit+V(x,8.5,0),theme.trim,art) end
 b("TopoPortal",V(22,3,4),exit+V(0,18,0),theme.rock,art)
 local portal=p("PortalDeViagem",V(14,14,.6),exit+V(0,8.5,0),theme.accent,art,nil,false,Enum.Material.Neon) portal.Transparency=.35
 text(portal,area.id==6 and "H" or "✦",C(223,238,224))
 local pad=p("ViagemProximaArea",V(13,.4,10),exit+V(0,.6,-4),theme.accent,art,nil,false,Enum.Material.Neon) pad.Transparency=.65
 if area.id<6 then pad:SetAttribute("NextAreaId",area.id+1) else pad:SetAttribute("Destino","lobby") pad.CanTouch=true end
 sign(area.id==6 and "VOLTA AO LOBBY" or "PROXIMA AREA\nDERROTE O CHEFE",exit+V(0,23,0),24,6)
 for _,x in ipairs({-10,10}) do lamp(exit+V(x,0,-7),.9) end
 -- Curated slots keep the central routes, bridges, machine and stairs unobstructed.
 local spots={{-36,-38},{34,-35},{-18,-45},{18,-43},{-45,-12},{43,-9},{-29,10},{29,11},
 {-46,25},{44,26},{-22,-21},{23,-18},{-12,15},{11,17},{-36,38},{34,39},
 {-49,-39},{48,-42},{-22,42},{17,42},{-52,8},{51,11},{-33,-56},{31,-57}}
 local spawns={}
 for i,q in ipairs(spots) do table.insert(spawns,{pos=c+V(q[1],6.1,q[2]),variant=i%8==0 and 3 or i%4==0 and 2 or 1}) end
 parent:SetAttribute("EntryPosition",c+V(0,9,-82))
 parent:SetAttribute("GachaPosition",c+V(-66,6.5,-63))
 local gachas=workspace:FindFirstChild("Gachas")
 local machine=gachas and gachas:FindFirstChild("Gacha_"..area.tema)
 if machine and machine:FindFirstChild("PadGacha") then
  if not machine:GetAttribute("RemainingIslandPlacement") then
   machine:SetAttribute("BeforeIslandScale",machine:GetScale())
   machine:ScaleTo(machine:GetScale()*.68)
   machine:PivotTo(machine:GetPivot()*CFrame.Angles(0,pi,0))
   machine:SetAttribute("RemainingIslandPlacement",true)
  end
  local pad=machine.PadGacha
  machine:PivotTo(machine:GetPivot()+c+V(-66,6.5,-63)-pad.Position)
  pad.Size=V(11,.25,11) pad.Transparency=.65
  for _,g in ipairs(machine:GetDescendants()) do if g:IsA("BillboardGui") then g.MaxDistance=45 end end
 end
 return {spawns=spawns,boss=c+V(-22,6.1,28),returnPad=c+V(13,5.5,-83)}
end
return M

