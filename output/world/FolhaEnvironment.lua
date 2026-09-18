-- Vila da Folha: a terraced quarry using the original game's Plastic/Studs terrain and trees.
local SS=game:GetService("ServerStorage")
local M={}
local V=Vector3.new
local C=Color3.fromRGB
local grass={C(104,194,38),C(124,214,46),C(87,177,34)}
local earth={C(169,132,83),C(183,145,95),C(157,119,76),C(194,157,107)}
local sand={C(215,193,145),C(225,204,159),C(205,181,133)}
local wood=C(101,65,38)
local darkWood=C(68,47,34)
local dark=C(51,57,65)
local red=C(174,57,38)
local water=C(37,163,238)
function M.build(parent,area)
 local rnd=Random.new(7151)
 local center=area.centro
 local scene=Instance.new("Model") scene.Name="VilaDaFolha" scene.Parent=parent
 scene:SetAttribute("AreaAmbient",true)
 local function folder(name) local f=Instance.new("Folder") f.Name=name f.Parent=scene return f end
 local terrain,river,buildings,plants,props=folder("Terreno"),folder("RioECachoeira"),folder("Arquitetura"),folder("Vegetacao"),folder("Detalhes")
 local function part(name,size,pos,color,group,material,angle,collide)
  local p=Instance.new("Part") p.Name=name p.Anchored=true p.Size=size
  p.CFrame=CFrame.new(center+pos)*(angle or CFrame.identity)
  p.Color=color p.Material=material or Enum.Material.Plastic
  p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth
  p.CanCollide=collide~=false p.CanTouch=false p.CanQuery=p.CanCollide
  p.Parent=group or props return p
 end
 local function block(name,size,pos,color,group)
  local p=part(name,size,pos,color,group) p.TopSurface=Enum.SurfaceType.Studs return p
 end
 local function beam(name,a,b,width,color,group)
  return part(name,V(width,width,(b-a).Magnitude),(a+b)*.5,color,group,Enum.Material.Wood,CFrame.lookAt(a,b).Rotation,false)
 end
 local function light(pos,scale,group)
  scale=scale or 1 group=group or props
  part("BaseLanterna",V(1.1,.4,1.1)*scale,pos+V(0,.2,0)*scale,dark,group)
  part("Poste",V(.38,3.1,.38)*scale,pos+V(0,1.9,0)*scale,wood,group,Enum.Material.Wood)
  local bulb=part("LuzQuente",V(.85,1.2,.85)*scale,pos+V(0,3.65,0)*scale,C(255,195,75),group,Enum.Material.Neon,nil,false)
  part("TetoLanterna",V(1.25,.3,1.25)*scale,pos+V(0,4.4,0)*scale,dark,group)
  for _,x in ipairs({-.48,.48}) do for _,z in ipairs({-.48,.48}) do
   part("ArmacãoLanterna",V(.12,1.35,.12)*scale,pos+V(x,3.65,z)*scale,dark,group,nil,nil,false)
  end end
  local l=Instance.new("PointLight") l.Color=C(255,196,104) l.Brightness=.75 l.Range=12*scale l.Shadows=false l.Parent=bulb
 end
 local function leafSymbol(board,color,scaleY)
  local gui=Instance.new("SurfaceGui") gui.Face=Enum.NormalId.Front gui.CanvasSize=Vector2.new(256,256)
  gui.LightInfluence=.65 gui.Adornee=board gui.MaxDistance=220 gui.Parent=board
  local function line(a,b,thickness)
   local f=Instance.new("Frame") f.BorderSizePixel=0 f.BackgroundColor3=color
   f.AnchorPoint=Vector2.new(.5,.5) f.Position=UDim2.fromOffset((a.X+b.X)/2,(a.Y+b.Y)/2)
   f.Size=UDim2.fromOffset((a-b).Magnitude,thickness or 8)
   f.Rotation=math.deg(math.atan2(b.Y-a.Y,b.X-a.X)) f.Parent=gui
  end
  local prev
  for i=0,30 do
   local t=i/30*math.pi*3.35 local r=8+i*1.65
   local p=Vector2.new(130+math.cos(t)*r,128+math.sin(t)*r*(scaleY or 1))
   if prev then line(prev,p) end prev=p
  end
  line(Vector2.new(82,143),Vector2.new(52,205))
  line(Vector2.new(52,205),Vector2.new(114,192))
  line(Vector2.new(114,192),Vector2.new(99,167))
  line(Vector2.new(161,88),Vector2.new(201,49))
  return gui
 end
 local function text(board,label,color)
  local g=Instance.new("SurfaceGui") g.Face=Enum.NormalId.Front g.PixelsPerStud=26
  g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.LightInfluence=.7 g.Adornee=board g.MaxDistance=220 g.Parent=board
  local t=Instance.new("TextLabel") t.Size=UDim2.fromScale(.94,.88) t.Position=UDim2.fromScale(.03,.06)
  t.BackgroundTransparency=1 t.Text=label t.TextColor3=color or C(255,237,191)
  t.Font=Enum.Font.GothamBlack t.TextScaled=true t.Parent=g
 end
 local function banner(pos,height)
  height=height or 13
  for _,x in ipairs({-4.4,4.4}) do part("Mastro",V(.55,height+3,.55),pos+V(x,(height+3)/2,0),wood,buildings,Enum.Material.Wood) end
  part("VigaEstandarte",V(10,.65,.65),pos+V(0,height+2.3,0),darkWood,buildings,Enum.Material.Wood)
  local cloth=part("EstandarteDaFolha",V(6.4,height,.25),pos+V(0,height/2+1,0),red,buildings,nil,nil,false)
  leafSymbol(cloth,dark,.8)
  for _,x in ipairs({-3,3}) do part("BordaDourada",V(.13,height,.31),pos+V(x,height/2+1,-.04),C(205,159,69),buildings,nil,nil,false) end
 end
 local function torii(pos,width,height)
  for _,x in ipairs({-width/2,width/2}) do
   part("BaseTorii",V(3,.7,3),pos+V(x,.35,0),dark,buildings)
   part("PilarVermelho",V(1.65,height,1.65),pos+V(x,height/2,0),red,buildings)
  end
  part("TraveTorii",V(width+5,1.7,2.5),pos+V(0,height,0),dark,buildings)
  part("TraveInferior",V(width+2,.8,1.2),pos+V(0,height-3,0),red,buildings)
  local symbol=part("BrasaoTorii",V(4.2,4.2,.32),pos+V(0,height-3.1,-.8),C(227,211,165),buildings,nil,nil,false)
  leafSymbol(symbol,dark)
  light(pos+V(-width/2+2,height-6,0),.65)
  light(pos+V(width/2-2,height-6,0),.65)
 end
 local function tree(pos,scale)
  local source=workspace.LobbyRenovado.OriginalArt:FindFirstChild("Arvore")
  if not source then return end
  local t=source:Clone() t.Name="ArvoreDaFolha"
  t:ScaleTo(source:GetScale()*(scale or .75))
  local cf,size=t:GetBoundingBox()
  t:PivotTo(t:GetPivot()+center+pos+V(0,size.Y/2,0)-cf.Position)
  t:PivotTo(t:GetPivot()*CFrame.Angles(0,rnd:NextNumber(0,6.28),0))
  for _,p in ipairs(t:GetDescendants()) do if p:IsA("BasePart") then
   p.Anchored=true p.CanCollide=p.Name:find("tronco")~=nil p.CanQuery=p.CanCollide p.CanTouch=false
  end end
  t.Parent=plants
 end
 local function terrace(pos,size,height)
  block("EstratoArenito",V(size.X,height+5,size.Z),pos+V(0,(height-5)/2,0),earth[rnd:NextInteger(1,#earth)],terrain)
  block("BordaGramada",V(size.X+.5,1.2,size.Z+.5),pos+V(0,height+.2,0),grass[rnd:NextInteger(1,3)],terrain)
 end
 local function fence(a,b)
  local length=(b-a).Magnitude local sections=math.ceil(length/6)
  for i=0,sections do
   local p=a:Lerp(b,i/sections)
   part("Mourao",V(.7,3.6,.7),p+V(0,1.8,0),wood,props,Enum.Material.Wood)
   part("TopoMourao",V(.95,.25,.95),p+V(0,3.6,0),darkWood,props)
  end
  beam("Corrimao",a+V(0,3,0),b+V(0,3,0),.42,wood)
  beam("Travessa",a+V(0,1.4,0),b+V(0,1.4,0),.32,wood)
 end
 local function stairs(pos,width,count,rise,run)
  for i=1,count do
   block("Degrau",V(width,i*rise,run+.1),pos+V(0,i*rise/2,(i-.5)*run),sand[2],terrain)
  end
 end
 local function crate(pos,size)
  size=size or 2.4
  part("Caixote",V(size,size,size),pos+V(0,size/2,0),C(125,87,50),props,Enum.Material.Wood)
  for _,y in ipairs({.18,size-.18}) do part("AroCaixa",V(size+.08,.23,size+.08),pos+V(0,y,0),darkWood,props,Enum.Material.Wood,nil,false) end
  beam("DiagonalCaixa",pos+V(-size*.4,.3,-size*.51),pos+V(size*.4,size-.3,-size*.51),.22,C(160,117,68))
 end
 local function emitter(pos,texture,color,rate,size,speed)
  local p=part("VFX",V(.1,.1,.1),pos,C(255,255,255),river,nil,nil,false) p.Transparency=1
  local a=Instance.new("Attachment") a.Parent=p
  local e=Instance.new("ParticleEmitter") e.Texture=texture e.Rate=rate e.Color=ColorSequence.new(color)
  e.Lifetime=NumberRange.new(1,2) e.Speed=NumberRange.new(speed*.6,speed)
  e.SpreadAngle=Vector2.new(45,45) e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,size*.5),NumberSequenceKeypoint.new(1,size)})
  e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.65),NumberSequenceKeypoint.new(1,1)})
  e:SetAttribute("FolhaAmbient",true) e.Parent=a return e
 end
 local function riverX(z)
  return 49+8*math.sin((z+70)*.055)-math.max(0,z-35)*.3
 end

 -- Continuous sand shelves with a real recessed river bed.
 part("LeitoSeguro",V(206,2,188),V(0,-5.8,0),C(125,115,81),terrain)
 for row=0,17 do
  local z=-85+row*10 local cx=riverX(z)
  for side=1,2 do
   local lo=side==1 and -100 or cx+8
   local hi=side==1 and cx-8 or 100
   local count=math.ceil((hi-lo)/11)
   for i=1,count do
    local width=(hi-lo)/count local x=lo+(i-.5)*width
    local green=math.abs(x)>84 or (z<-65 and math.abs(x)>18)
    block(green and "GramaOriginal" or "PisoArenito",V(width+.02,4.8,10.02),V(x,-2.4,z),
     green and grass[rnd:NextInteger(1,3)] or sand[rnd:NextInteger(1,3)],terrain)
   end
  end
  local w=part("AguaRio",V(16.4,.6,10.1),V(cx,-1.3,z),water,river,Enum.Material.Plastic,nil,false)
  w.Transparency=.17
  for side=-1,1,2 do
   part("Margem",V(1.4,2,10.1),V(cx+side*8.25,-1.05,z),earth[2],river)
  end
  for i=1,2 do
   local a=V(cx+rnd:NextNumber(-5,5),-.94,z+4)
   local b=V(riverX(z-10)+rnd:NextNumber(-4,4),-.94,z-6)
   local f=part("CorrenteFolha",V(.25,.05,2),a,C(170,236,255),river,Enum.Material.Neon,nil,false)
   f:SetAttribute("FlowA",center+a) f:SetAttribute("FlowB",center+b) f:SetAttribute("FlowPhase",rnd:NextNumber())
   f.Transparency=.5
  end
 end
 -- Tiered perimeter: staggered ledges, independent silhouettes, green caps.
 for side=-1,1,2 do
  for i=0,7 do
   local z=-73+i*23 local h=rnd:NextInteger(23,42)
   terrace(V(side*105,0,z),V(27,0,27),h)
   terrace(V(side*89,0,z+5),V(14,0,15),h*.47)
   if i%2==0 then tree(V(side*89,h*.47+.8,z+5),.56) end
   if i%3==0 then tree(V(side*105,h+.8,z),.8) end
  end
 end
 for _,x in ipairs({-100,-77,-54,-31,31,55,79,103}) do
  local height=rnd:NextInteger(39,57)
  terrace(V(x,0,96),V(25,0,27),height)
  if x<-12 or x>48 then terrace(V(x,0,81),V(20,0,15),height*.55) end
  if x%2~=0 then tree(V(x,height+.8,95),.64) end
 end
 -- An overhead rock bridge conceals the distant areas while leaving the progression route open.
 block("ArcoDeArenito",V(41,31,26),V(0,41,99),earth[2],terrain)
 block("TopoDoArco",V(42,1.2,27),V(0,57,99),grass[2],terrain)
 tree(V(4,57.8,99),.68)
 -- Vines and leafy clumps break up the cliff faces without blocking movement.
 for _,v in ipairs({{-94,14,-35},{-87,15,36},{90,18,-24},{-55,23,79},{57,22,79},{88,15,59}}) do
  local x,y,z=v[1],v[2],v[3]
  for strand=1,3 do
   local length=3+strand*1.6
   local stem=part("Cipo",V(.13,length,.14),V(x+strand*.7,y-length*.5,z),C(62,113,39),plants,nil,nil,false)
   for j=0,3 do
    part("FolhaCipo",V(.8,.3,.5),V(x+strand*.7+(j%2==0 and .3 or -.3),y-j*length/4,z-.1),
     grass[(j+strand)%3+1],plants,nil,CFrame.Angles(0,0,math.rad(j%2==0 and 25 or -25)),false)
   end
  end
 end
 -- Left lodge terrace with a clear stair approach from the quarry.
 terrace(V(-67,0,1),V(35,0,44),8)
 for i=1,8 do
  block("EscadaDaVila",V(2.1,i,13),V(-43-(i-.5)*2,i/2,-10),sand[2],terrain)
 end
 fence(V(-84,8.8,-19),V(-84,8.8,20))
 fence(V(-78,8.8,-21),V(-58,8.8,-21))
 -- Lodge, timber framing, individual roof shingles, lit openings and veranda.
 local lodge=V(-67,8.8,6)
 part("FundacaoCasa",V(29,1,22),lodge+V(0,.5,0),earth[4],buildings)
 part("ParedesCasa",V(25,10,18),lodge+V(0,6,0),C(191,157,104),buildings)
 part("Varanda",V(29,.6,5),lodge+V(0,1.2,-11),wood,buildings,Enum.Material.Wood)
 for _,x in ipairs({-13,0,13}) do
  part("VigaCasa",V(.7,11,.7),lodge+V(x,6,-10),darkWood,buildings,Enum.Material.Wood)
 end
 for _,y in ipairs({1.5,10.6}) do part("TraveCasa",V(28,.6,.7),lodge+V(0,y,-10),darkWood,buildings,Enum.Material.Wood) end
 for _,x in ipairs({-7,7}) do
  local win=part("JanelaAcesa",V(4.5,4,.2),lodge+V(x,6,-9.15),C(255,199,91),buildings,Enum.Material.Neon,nil,false)
  for _,dx in ipairs({-2.25,0,2.25}) do part("MolduraJanela",V(.24,4.4,.4),lodge+V(x+dx,6,-9.4),darkWood,buildings) end
  part("JanelaTravessa",V(4.7,.25,.4),lodge+V(x,6,-9.4),darkWood,buildings)
 end
 part("PortaMadeira",V(3.4,7,.3),lodge+V(0,4.8,-9.3),darkWood,buildings,Enum.Material.Wood)
 for side=-1,1,2 do
  for row=0,5 do
   for col=-3,3 do
    part("Telha",V(4.3,.5,2.7),lodge+V(col*4.22,15.2-row*.62,side*(1+row*2.2)),
     C(99+row*3,68+row*2,66+row*2),buildings,Enum.Material.Plastic,CFrame.Angles(math.rad(side*16),0,0))
   end
  end
 end
 part("Cumeeira",V(31,.7,.9),lodge+V(0,15.6,0),darkWood,buildings)
 for _,x in ipairs({-12,12}) do light(lodge+V(x,1.5,-11),.9) end
 local sign=part("PlacaMinerais",V(10,4,.6),V(-76,14,-20),wood,buildings,Enum.Material.Wood)
 text(sign,"MINERAIS\nDA FOLHA")
 crate(V(-82,8.9,17),3) crate(V(-78,8.9,19),2.4)

 -- Right mine entrance on a raised shelf, with rails climbing into the tunnel.
 terrace(V(78,0,63),V(39,0,41),9)
 stairs(V(72,0,30),18,10,.96,2.1)
 local mine=V(77,9.8,68)
 part("TunelEscuro",V(20,19,.6),mine+V(0,9,14),C(27,26,29),buildings)
 part("TetoDoTunel",V(20,2,19),mine+V(0,19,5),C(72,75,82),buildings)
 part("PisoDoTunel",V(20,.35,20),mine+V(0,.2,4),C(129,118,99),buildings)
 for _,side in ipairs({-1,1}) do
  part("LateralDoTunel",V(1,19,19),mine+V(side*10,9,5),C(49,52,58),buildings)
 end
 for _,x in ipairs({-12,12}) do
  block("PilarDaMina",V(7,22,10),mine+V(x,10,-1),C(83,85,88),buildings)
  part("MadeiraDaMina",V(1.8,17,2),mine+V(x*.74,8,-7),wood,buildings,Enum.Material.Wood)
 end
 for i=0,4 do
  block("ArcoDaMina",V(6.1,7,9),mine+V((i-2)*5,21-math.abs(i-2)*1.2,-1),C(84+i*2,86+i*2,91+i*2),buildings)
 end
 part("VigaEntrada",V(23,2,2),mine+V(0,17,-7),wood,buildings,Enum.Material.Wood)
 local insignia=part("PedraDaFolha",V(13,8,.6),mine+V(0,23,-6),C(98,101,103),buildings)
 leafSymbol(insignia,C(208,209,198))
 local function rails(a,b)
  local count=math.ceil((b-a).Magnitude/2.6)
  for i=0,count do local q=a:Lerp(b,i/count)
   part("Dormente",V(7,.3,.65),q,wood,buildings,Enum.Material.Wood,nil,false)
  end
  for _,x in ipairs({-2.35,2.35}) do
   local bar=beam("Trilho",a+V(x,.3,0),b+V(x,.3,0),.25,C(120,124,131),buildings)
   bar.Material=Enum.Material.Metal
  end
 end
 rails(V(72,.3,22),V(72,.3,30)) rails(V(72,.3,30),V(72,10.1,51)) rails(V(72,10.1,51),V(77,10.1,70))
 local cart=V(75,10.4,60)
 part("CarrinhoMina",V(4.3,2.4,4.7),cart+V(0,1.5,0),C(93,86,81),props,Enum.Material.Metal)
 part("CargaMinerio",V(3.5,.5,3.8),cart+V(0,2.9,0),C(64,68,77),props)
 for _,x in ipairs({-2.3,2.3}) do for _,z in ipairs({-1.5,1.5}) do
  local wheel=part("RodaCarrinho",V(.5,1.1,1.1),cart+V(x,.5,z),dark,props,Enum.Material.Metal,nil,false) wheel.Shape=Enum.PartType.Cylinder
 end end
 light(V(64,9.9,53),1.05) light(V(90,9.9,53),1.05)
 crate(V(92,9.9,66),3) crate(V(91,9.9,71),2.5)
 -- Main waterfall, pool mist and stepped streams.
 local wx=riverX(83)
 part("AguaSuperior",V(12,.7,14),V(wx,43,91),water,river,nil,nil,false)
 for i=0,4 do
  local p=part("LaminaCachoeira",V(2.5,44-rnd:NextNumber(0,2),1.9),V(wx+(i-2)*2.2,21.4,81+rnd:NextNumber(-.8,.8)),
   i%2==0 and C(45,174,250) or C(96,203,255),river,nil,nil,false)
  p.Transparency=.15
  local texture=Instance.new("Texture") texture.Name="FluxoCachoeira"
  texture.Texture="rbxasset://textures/particles/water_main.dds" texture.Face=Enum.NormalId.Front
  texture.StudsPerTileU=7 texture.StudsPerTileV=11 texture.Transparency=.6 texture.Parent=p
 end
 emitter(V(wx,.2,79),"rbxasset://textures/particles/smoke_main.dds",C(211,246,255),12,6,4)
 for _,z in ipairs({68,32,-25}) do
  for _,side in ipairs({-1,1}) do
   block("PedraDaMargem",V(3.4,2.5,4),V(riverX(z)+side*10,1,z),C(107,116,100),river)
   tree(V(riverX(z)+side*17,0,z+5),.6)
  end
 end
 local function bridge(z)
  local cx=riverX(z) local width=31
  for i=0,14 do
   local x=-width/2+i*width/14
   local y=.45+math.sin(i/14*math.pi)*1.6
   part("TabuaPonte",V(width/14+.05,.55,10),V(cx+x,y,z),C(136+i%3*9,91+i%3*5,53),buildings,Enum.Material.Wood)
   if i%3==0 or i==14 then
    for _,side in ipairs({-1,1}) do part("PostePonte",V(.6,3.1,.6),V(cx+x,y+1.6,z+side*4.7),wood,buildings) end
   end
   if i>0 then
    local prevx=-width/2+(i-1)*width/14
    local prevy=.45+math.sin((i-1)/14*math.pi)*1.6
    for _,side in ipairs({-1,1}) do beam("CorrimaoPonte",V(cx+prevx,prevy+2.9,z+side*4.7),V(cx+x,y+2.9,z+side*4.7),.4,wood,buildings) end
   end
  end
 end
 bridge(-55) bridge(25)
 -- Foreground gate and signs, rear progression gate and shrine.
 torii(V(0,0,-86),25,18)
 torii(V(0,0,88),20,19)
 local nextSign=part("ProximaArea",V(12,3,.5),V(0,16,87),wood,buildings)
 text(nextSign,"DERROTE O CHEFE")
 local entrySign=part("MinaDaFolha",V(12,7,.5),V(78,5,-69),wood,buildings,Enum.Material.Wood)
 text(entrySign,"MINA\nDA FOLHA")
 for _,x in ipairs({73,83}) do part("ApoioPlaca",V(.65,7,.65),V(x,2.8,-68.7),wood,buildings) end
 terrace(V(-27,0,66),V(25,0,23),14)
 stairs(V(-27,0,35),11,14,1,1.5)
 banner(V(-27,14.8,72),12)
 light(V(-36,14.8,59),.9) light(V(-18,14.8,59),.9)
 banner(V(-90,26,15),16)
 banner(V(100,37,40),17)
 banner(V(-54,47,98),13)
 -- Stone relief: carved face, angular hair and forehead plate inset into the cliff.
 local face=V(-69,33,82)
 block("RelevoPedra",V(19,23,3),face,earth[2],buildings)
 part("RostoEsculpido",V(10,12,3),face+V(0,0,-2.1),earth[4],buildings)
 part("Queixo",V(7,3,3),face+V(0,-6,-2),earth[3],buildings)
 part("Nariz",V(1.4,4,1.5),face+V(0,-.3,-4),earth[1],buildings)
 for _,x in ipairs({-2.6,2.6}) do
  part("OlhoEsculpido",V(2.1,.65,.25),face+V(x,1.2,-3.7),C(108,83,53),buildings)
  part("Sobrancelha",V(2.5,.5,.5),face+V(x,2.2,-3.8),earth[1],buildings,nil,CFrame.Angles(0,0,math.rad(x*3)))
  for i=1,3 do part("MarcaRosto",V(1.8,.15,.2),face+V(x*1.3,-i*.8,-3.65),earth[3],buildings) end
 end
 part("Boca",V(3,.25,.2),face+V(0,-4,-3.7),earth[3],buildings)
 local band=part("BandanaEsculpida",V(10,2.6,.6),face+V(0,4,-3.9),earth[1],buildings)
 local emblem=part("EmblemaBandana",V(3,2.6,.1),face+V(0,4,-4.25),earth[2],buildings)
 leafSymbol(emblem,C(114,88,58))
 for i=0,10 do
  local theta=math.rad(-75+i*15)
  local spike=Instance.new("WedgePart") spike.Name="CabeloEsculpido" spike.Anchored=true
  spike.Size=V(2.8,6.8,3)
  spike.CFrame=CFrame.new(center+face+V(math.sin(theta)*6,6+math.cos(theta)*3,-2))*CFrame.Angles(0,0,-theta)
  spike.Color=earth[4] spike.Material=Enum.Material.Plastic spike.Parent=buildings
 end
 -- Grounded accents: clear paths remain between the ore clusters.
 local trees={{-88,-57,.7},{-76,-34,.65},{-85,40,.75},{-55,58,.55},{-15,78,.6},{15,70,.62},{88,-53,.85},{89,-13,.65},{-45,-67,.55}}
 for _,d in ipairs(trees) do tree(V(d[1],0,d[2]),d[3]) end
 for _,d in ipairs({{-38,-57},{27,-62},{-44,23},{24,40},{-50,52},{82,-35},{65,9}}) do light(V(d[1],0,d[2]),.8) end
 fence(V(-85,0,-67),V(-50,0,-67))
 fence(V(-80,0,43),V(-57,0,43))
 fence(V(72,0,-32),V(90,0,-32))
 fence(V(96,9.8,47),V(96,9.8,76))
 for i=1,45 do
  local x=rnd:NextNumber(-94,96) local z=rnd:NextNumber(-78,76)
  if math.abs(x-riverX(z))<13 then continue end
  if math.abs(x)<18 and z<50 then continue end
  if x<-44 and z>-26 and z<33 then continue end
  if x>55 and z>24 then continue end
  local s=rnd:NextNumber(.5,1.5)
  block("PedrinhaComMusgo",V(s*2,s,s*1.7),V(x,s*.35,z),C(112,132,91),props)
 end
 for i=1,40 do
  local z=rnd:NextNumber(-79,74) local x=riverX(z)+(i%2==0 and -1 or 1)*rnd:NextNumber(10,13)
  for j=1,3 do
   part("Junco",V(.15,rnd:NextNumber(1.2,2.6),.18),V(x+j*.25,.9,z),C(74,137,53),plants,nil,CFrame.Angles(0,0,math.rad(j*9-18)),false)
  end
 end
 emitter(V(-72,12,-6),"rbxasset://textures/particles/sparkles_main.dds",C(255,212,126),1,.22,.35)
 -- Fixed curated placements keep paths, stairs, buildings and water clear.
 local spots={
 {-31,-59},{-12,-55},{14,-54},{30,-39},{-53,-44},{-66,-50},
 {-28,-33},{-7,-30},{16,-28},{-36,-8},{-18,-4},{13,-9},{27,8},
 {-64,37},{-48,40},{-37,21},{-49,63},{-65,62},{-79,59},
 {-14,37},{15,34},{23,54},{9,63},{-7,65},
 {78,-53},{84,-11},{71,-17},{78,11},{-49,-61},{-34,52},
 }
 local spawns={}
 for i,p in ipairs(spots) do table.insert(spawns,{pos=center+V(p[1],0,p[2]),variant=i%11==0 and 3 or i%4==0 and 2 or 1}) end
 -- Mirror the layout so the lodge is on the viewer's left when entering from the lobby.
 local function mirror(v) return V(-v.X,v.Y,v.Z) end
 for _,p in ipairs(scene:GetDescendants()) do
  if p:IsA("BasePart") then
   local cf=p.CFrame
   p.CFrame=CFrame.fromMatrix(center+mirror(cf.Position-center),-mirror(cf.RightVector),mirror(cf.UpVector))
   for _,attribute in ipairs({"FlowA","FlowB"}) do
    local point=p:GetAttribute(attribute) if point then p:SetAttribute(attribute,center+mirror(point-center)) end
   end
  end
 end
 for _,entry in ipairs(spawns) do entry.pos=center+mirror(entry.pos-center) end
 return {spawns=spawns,boss=center+V(1,0,16),returnPad=center+V(19,.5,-77)}
end
return M
