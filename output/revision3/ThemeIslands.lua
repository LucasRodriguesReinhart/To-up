-- Authored Dragon Ball and Shadow Garden islands. Built only for Ki and Sombra.
local M={}
local V=Vector3.new
local C=Color3.fromRGB
local pi=math.pi
function M.build(parent,area)
 local shadow=area.id==4
 local center=area.centro
 local random=Random.new(9700+area.id)
 local model=Instance.new("Model") model.Name=shadow and "ShadowGarden" or "DragonBallIsland" model.Parent=parent
 local function group(name) local f=Instance.new("Model") f.Name=name f.Parent=model return f end
 local land=group("IlhaETerracos")
 local architecture=group("Arquitetura")
 local decor=group("VegetacaoEDetalhes")
 local waters=group("RiosECachoeiras")
 local rock=shadow and C(64,57,84) or C(182,132,86)
 local soil=shadow and C(115,104,134) or C(224,184,118)
 local grass=shadow and C(111,61,173) or C(105,204,47)
 local wood=shadow and C(55,40,61) or C(118,78,42)
 local trim=shadow and C(35,29,50) or C(66,78,99)
 local accent=shadow and C(180,55,255) or C(48,139,235)
 local water=shadow and C(124,31,234) or C(38,168,244)
 local glow=shadow and C(193,126,244) or C(255,189,65)
 local function part(name,size,pos,color,folder,rotation,material,collide)
  local p=Instance.new("Part") p.Name=name p.Anchored=true p.Size=size
  p.CFrame=CFrame.new(center+pos)*(rotation or CFrame.identity)
  p.Color=color p.Material=material or Enum.Material.Plastic
  p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth
  p.CanCollide=collide~=false p.CanTouch=false p.CanQuery=p.CanCollide
  p.Parent=folder or decor return p
 end
 local function block(name,size,pos,color,folder,rot)
  local p=part(name,size,pos,color,folder,rot) p.TopSurface=Enum.SurfaceType.Studs return p
 end
 local function cylinder(name,radius,height,pos,color,folder,material)
  local p=part(name,V(height,radius*2,radius*2),pos,color,folder,CFrame.Angles(0,0,pi/2),material)
  p.Shape=Enum.PartType.Cylinder return p
 end
 local function ball(name,size,pos,color,folder,material)
  local p=part(name,size,pos,color,folder,nil,material,false) p.Shape=Enum.PartType.Ball return p
 end
 local function line(name,a,b,width,color,folder,material)
  return part(name,V(width,width,(b-a).Magnitude),(a+b)/2,color,folder,CFrame.lookAt(a,b).Rotation,material,false)
 end
 local function text(board,words,color,font)
  local g=Instance.new("SurfaceGui") g.Adornee=board g.Face=Enum.NormalId.Front
  g.SizingMode=Enum.SurfaceGuiSizingMode.PixelsPerStud g.PixelsPerStud=30
  g.LightInfluence=.35 g.MaxDistance=200 g.Parent=board
  local label=Instance.new("TextLabel") label.Size=UDim2.fromScale(.92,.88) label.Position=UDim2.fromScale(.04,.06)
  label.BackgroundTransparency=1 label.Text=words label.TextScaled=true
  label.TextColor3=color or C(248,237,217) label.Font=font or Enum.Font.GothamBlack label.Parent=g
  return g
 end
 local function emblem(board,color,kind,face)
  local g=Instance.new("SurfaceGui") g.Face=face or Enum.NormalId.Front g.Adornee=board
  g.CanvasSize=Vector2.new(256,256) g.LightInfluence=.35 g.MaxDistance=230 g.Parent=board
  local function shape(x,y,w,h,col,round)
   local f=Instance.new("Frame") f.BorderSizePixel=0 f.Position=UDim2.fromOffset(x,y)
   f.Size=UDim2.fromOffset(w,h) f.BackgroundColor3=col f.Parent=g
   if round then local c=Instance.new("UICorner") c.CornerRadius=UDim.new(1,0) c.Parent=f end
   return f
  end
  if kind=="moon" then
   shape(37,26,182,198,color,true)
   shape(85,12,152,177,board.Color,true)
   local star=shape(54,31,18,18,color,false) star.Rotation=45
  else
   -- Brush-like strokes of the martial-arts emblem, independent of font availability.
   local strokes={{37,75,9,69},{54,55,11,158},{70,70,10,59},{92,54,131,11},{104,101,109,10},
    {107,147,116,10},{125,60,11,89},{174,103,11,47},{109,170,108,11},{109,170,11,54},{206,170,11,54},{109,217,108,10}}
   for _,p in ipairs(strokes) do shape(p[1],p[2],p[3],p[4],color,false) end
  end
  return g
 end
 local function plaque(words,pos,size,color)
  local board=part("Placa",V(size.X,size.Y,.55),pos,color or wood,architecture,nil,Enum.Material.Wood)
  text(board,words)
  return board
 end
 local function lamp(pos,scale)
  scale=scale or 1
  block("BaseLampiao",V(1.8,.7,1.8)*scale,pos+V(0,.35,0)*scale,trim,decor)
  block("ColunaLampiao",V(.9,3.3,.9)*scale,pos+V(0,2.1,0)*scale,shadow and rock or wood,decor)
  local light=part("CristalDeLuz",V(1.15,1.6,1.15)*scale,pos+V(0,4.3,0)*scale,glow,decor,
   shadow and CFrame.Angles(0,0,pi/4) or nil,Enum.Material.Neon,false)
  if not shadow then
   for _,x in ipairs({-.67,.67}) do for _,z in ipairs({-.67,.67}) do
    part("Armacão",V(.13,1.9,.13)*scale,pos+V(x,4.3,z)*scale,wood,decor,nil,nil,false)
   end end
  end
  part("CapitelLampiao",V(1.7,.45,1.7)*scale,pos+V(0,5.4,0)*scale,trim,decor)
  local l=Instance.new("PointLight") l.Color=glow l.Range=11*scale l.Brightness=shadow and .55 or .65 l.Shadows=false l.Parent=light
 end
 local function fence(a,b)
  for i=0,math.ceil((b-a).Magnitude/5) do
   local q=a:Lerp(b,i/math.ceil((b-a).Magnitude/5))
   part("Mourao",V(.7,3.5,.7),q+V(0,1.75,0),wood,decor,nil,Enum.Material.Wood)
  end
  line("Corrimao",a+V(0,3,0),b+V(0,3,0),.45,wood,decor,Enum.Material.Wood)
  line("Travessa",a+V(0,1.4,0),b+V(0,1.4,0),.32,wood,decor,Enum.Material.Wood)
 end
 local function tree(pos,size)
  local template=workspace.LobbyRenovado.OriginalArt:FindFirstChild("Arvore")
  if not template then return end
  local t=template:Clone() t.Name=shadow and "ArvoreSombria" or "ArvoreNamekusei"
  t:ScaleTo(template:GetScale()*size)
  local cf,box=t:GetBoundingBox()
  t:PivotTo(t:GetPivot()+center+pos+V(0,box.Y/2,0)-cf.Position)
  t.Parent=decor
  for _,p in ipairs(t:GetDescendants()) do if p:IsA("BasePart") then
   p.CanCollide=p.Name:find("tronco")~=nil p.CanQuery=p.CanCollide p.CanTouch=false
   if shadow then p.Color=p.Name:find("folhagem") and C(76+random:NextInteger(0,25),37,135+random:NextInteger(0,35)) or C(53,43,65) end
  end end
 end
 local function palm(pos,height)
  for i=0,4 do
   part("TroncoPalmeira",V(.9,height/5+.3,.9),pos+V(math.sin(i*.3)*1.2,(i+.5)*height/5,0),C(140-i*5,100-i*4,61),decor,CFrame.Angles(0,0,-.04*i))
  end
  local crown=pos+V(1.2,height,0)
  for i=0,7 do
   local angle=i*pi/4 local dir=V(math.cos(angle),0,math.sin(angle))
   for j=1,3 do
    local q=crown+dir*(j*1.6)+V(0,1.2-(j-1)^2*.5,0)
    local leaf=part("FolhaPalmeira",V(2.5,.5,2.4),q,C(40+j*7,158-j*7,62),decor,CFrame.Angles(0,-angle,math.rad(12)),nil,false)
   end
  end
  for _,x in ipairs({-.6,.6}) do ball("Coco",V(.8,.9,.8),crown+V(x,-.8,0),C(99,69,37),decor) end
 end
 local function ledge(x,z,w,d,h)
  block("Estrato",V(w,h+5,d),V(x,(h-5)/2,z),rock:Lerp(C(210,186,159),random:NextNumber(0,.13)),land)
  block("TopoGrama",V(w+.4,1,d+.4),V(x,h+.15,z),grass,land)
 end
 local function stairs(pos,width,steps,rise,run)
  for i=1,steps do block("Degrau",V(width,i*rise,run+.05),pos+V(0,i*rise/2,(i-.5)*run),soil:Lerp(C(228,222,217),.16),land) end
 end
 local function flow(a,b)
  local p=part("CorrenteFolha",V(.3,.08,2.3),a,shadow and C(221,135,255) or C(172,234,255),waters,nil,Enum.Material.Neon,false)
  p:SetAttribute("FlowA",center+a) p:SetAttribute("FlowB",center+b) p:SetAttribute("FlowPhase",random:NextNumber())
  p.Transparency=.45
 end
 local function waterfall(x,z,top,width)
  for i=0,4 do
   local p=part("Queda",V(width/5+.15,top,1.3),V(x+(i-2)*width/5,top/2+.2,z),water:Lerp(C(192,204,255),i%2*.25),waters,nil,nil,false)
   p.Transparency=.13
   local tex=Instance.new("Texture") tex.Name="FluxoCachoeira" tex.Texture="rbxasset://textures/particles/water_main.dds"
   tex.Face=Enum.NormalId.Front tex.StudsPerTileU=6 tex.StudsPerTileV=10 tex.Transparency=.65 tex.Parent=p
  end
  local mist=part("NeblinaDaQueda",V(.1,.1,.1),V(x,.7,z-2),water,waters,nil,nil,false) mist.Transparency=1
  local a=Instance.new("Attachment") a.Parent=mist
  local e=Instance.new("ParticleEmitter") e.Texture="rbxasset://textures/particles/smoke_main.dds"
  e.Color=ColorSequence.new(water:Lerp(C(255,255,255),.65)) e.Size=NumberSequence.new(5)
  e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,.7),NumberSequenceKeypoint.new(1,1)})
  e.Lifetime=NumberRange.new(1.2,2.1) e.Rate=10 e.Speed=NumberRange.new(1,3) e.SpreadAngle=Vector2.new(50,50)
  e:SetAttribute("FolhaAmbient",true) e.Parent=a
 end
 local function bridge(a,b,width,height)
  local delta=b-a local count=math.ceil(delta.Magnitude/2.2)
  local direction=delta.Unit local side=V(-direction.Z,0,direction.X)
  for i=0,count do
   local t=i/count local q=a:Lerp(b,t)+V(0,math.sin(t*pi)*height,0)
   part("TabuaPonte",V(width,.45,delta.Magnitude/count+.06),q,wood:Lerp(C(182,132,75),i%3*.07),architecture,CFrame.lookAt(q,q+direction).Rotation,Enum.Material.Wood)
   if i%3==0 or i==count then
    for _,k in ipairs({-1,1}) do part("PostePonte",V(.6,3,.6),q+side*k*(width/2-.3)+V(0,1.5,0),wood,architecture) end
   end
   if i>0 then
    local t0=(i-1)/count local q0=a:Lerp(b,t0)+V(0,math.sin(t0*pi)*height+2.7,0)
    for _,k in ipairs({-1,1}) do line("GuardaCorpo",q0+side*k*(width/2-.3),q+V(0,2.7,0)+side*k*(width/2-.3),.4,wood,architecture) end
   end
  end
 end
 local function banner(pos,height)
  for _,x in ipairs({-4.8,4.8}) do part("PilarEstandarte",V(.8,height+2,.8),pos+V(x,(height+2)/2,0),wood,architecture) end
  part("TravessaEstandarte",V(11,.8,1),pos+V(0,height+1,0),trim,architecture)
  local board=part("Estandarte",V(7,height,.28),pos+V(0,height/2,0),shadow and C(31,18,58) or C(231,217,168),architecture,nil,nil,false)
  emblem(board,shadow and C(181,107,255) or C(33,33,40),shadow and "moon" or "martial")
 end
 local function dome(pos,radius,height,roofColor,label)
  cylinder("CorpoCupula",radius,height,pos+V(0,height/2,0),C(198,207,210),architecture)
  for i=0,7 do
   local t=(i+.5)/8
   local r=radius*math.sqrt(1-t*t)
   cylinder("AnelCupula",r,radius*.62/8+.05,pos+V(0,height+t*radius*.62,0),roofColor:Lerp(C(125,171,255),i*.025),architecture)
  end
  local facade=part("Identidade",V(radius*.95,7,.15),pos+V(0,height*.69,-radius-.06),C(233,227,215),architecture,nil,nil,false)
  text(facade,label,C(25,39,61))
  local door=part("PortaIluminada",V(4.2,6.6,.3),pos+V(0,3.3,-radius-.2),C(255,200,101),architecture,nil,Enum.Material.Neon,false)
  for i=0,9 do
   local angle=i/10*2*pi
   local q=pos+V(math.sin(angle)*(radius+.15),3.8,-math.cos(angle)*(radius+.15))
   if math.abs(math.sin(angle))>.2 then
    local win=part("JanelaCapsula",V(2,2.9,.3),q,C(80,147,205),architecture,CFrame.Angles(0,-angle,0),Enum.Material.Glass,false)
    win.Transparency=.08
   end
  end
 end
 local function tower(pos,height,width)
  block("BaseTorre",V(width+3,3,width+3),pos+V(0,1.5,0),trim,architecture)
  block("Torre",V(width,height,width),pos+V(0,height/2,0),rock,architecture)
  for _,side in ipairs({-1,1}) do
   part("VeioArcano",V(.4,height-4,.3),pos+V(side*width*.34,height/2,-width*.51),accent,architecture,nil,Enum.Material.Neon,false)
  end
  for i=0,12 do
   local w=(width+3)*(1-i/13)
   block("AgulhaTorre",V(w,1.4,w),pos+V(0,height+i*1.35,0),trim,architecture)
  end
  for _,x in ipairs({-1,1}) do for _,z in ipairs({-1,1}) do
   block("MerlaoTorre",V(2,3,2),pos+V(x*width*.5,height-.2,z*width*.5),trim,architecture)
  end end
 end

 -- Open water encircles the raised central quarry.
 local sea=part("AguaDaIlha",V(226,.4,204),V(0,.25,0),water,waters,nil,nil,false) sea.Transparency=shadow and .1 or .18
 cylinder("BaseDaIlha",76,8,V(0,.8,0),rock,land)
 cylinder("GramaDaBorda",77,1,V(0,4.9,0),grass,land)
 cylinder("PracaMineracao",69,.6,V(0,5.5,0),soil,land)
 for x=-60,60,10 do for z=-60,60,10 do
  if x*x+z*z<65*65 then
   block("Lajota",V(9.95,.15,9.95),V(x,5.86,z),soil:Lerp(C(255,242,217),random:NextNumber(0,.065)),land)
  end
 end end
 -- Front approach and terraces produce the reference's stepped island silhouette.
 block("CaminhoEntrada",V(20,5,30),V(0,2.5,-84),soil,land)
 stairs(V(0,5,-71),20,1,.95,4)
 stairs(V(0,0,-111),20,5,1,2.5)
 for side=-1,1,2 do
  for i=0,5 do
   local z=-74+i*31 local h=20+random:NextInteger(0,22)
   ledge(side*103,z,27,31,h)
   ledge(side*86,z+6,15,18,h*.5)
   tree(V(side*87,h*.5+.7,z+5),shadow and .68 or .58)
   if i%2==0 then tree(V(side*103,h+.8,z),.72) end
  end
 end
 for _,x in ipairs({-96,-71,-45,45,71,96}) do
  local h=35+random:NextInteger(0,20) ledge(x,94,28,28,h)
  tree(V(x,h+.8,94),.67)
 end
 -- Tall distant sandstone closes the horizon while the smaller ledges keep a layered silhouette.
 for _,x in ipairs({-128,-96,-64,-32,0,32,64,96,128}) do
  local h=50+random:NextInteger(0,18)
  ledge(x,129,33,20,h)
  if x%64==0 then tree(V(x,h+.8,128),.75) end
 end
 for _,side in ipairs({-1,1}) do
  for _,z in ipairs({-46,-10,26,62,98}) do
   local h=42+random:NextInteger(0,24) ledge(side*130,z,22,37,h)
  end
 end
 -- Back cliffs close the horizon behind the landmark.
 for _,x in ipairs({-24,0,24}) do ledge(x,108,26,13,shadow and 42 or 34) end
 -- Angular shelves break up the circular rim and give the bank a natural outline.
 for _,p in ipairs({{-49,-56},{49,-55},{-70,-25},{70,-22},{-67,37},{66,42},{-36,64},{38,62}}) do
  local b=block("RochedoDaMargem",V(13,7,12),V(p[1],1.5,p[2]),rock,land,CFrame.Angles(0,.35,0))
  block("IlhotaGramada",V(13.3,.7,12.3),V(p[1],5.3,p[2]),grass,land,CFrame.Angles(0,.35,0))
 end
 block("TerraçoInvocacao",V(29,6,27),V(-66,2.8,-62),rock,land)
 block("PisoInvocacao",V(29.3,.4,27.3),V(-66,6,-62),soil,land)
 fence(V(-79,6,-74),V(-79,6,-51))
 lamp(V(-77,6,-74),.85) lamp(V(-53,6,-74),.85)
 -- Water routes and usable side bridges.
 for _,side in ipairs({-1,1}) do
  for z=-78,68,10 do flow(V(side*(77+random:NextNumber(1,9)),.55,z+4),V(side*(77+random:NextNumber(1,9)),.55,z-7)) end
 end
 bridge(V(-62,6,8),V(-94,11,17),9,1.3)
 bridge(V(61,6,10),V(94,11,21),9,1.3)
 bridge(V(-41,6,-52),V(-83,6,-70),10,1.1)
 for _,p in ipairs({{-15,-59},{15,-59},{-53,-23},{53,-23},{-55,27},{55,27},{-18,30},{18,30}}) do lamp(V(p[1],6,p[2]),.85) end
 for _,side in ipairs({-1,1}) do
  fence(V(side*65,6,-22),V(side*65,6,12))
  fence(V(side*41,6,-56),V(side*58,6,-39))
 end
 -- Ground medallion between the ore clusters.
 local med=cylinder("Medalhao",14,.08,V(0,6.01,-9),trim,decor)
 cylinder("CentroMedalhao",12.7,.09,V(0,6.1,-9),soil,decor)
 local badge=part("SimboloNoPiso",V(24,.07,24),V(0,6.18,-9),soil,decor,nil,nil,false)
 badge.Transparency=1
 emblem(badge,trim,shadow and "moon" or "martial",Enum.NormalId.Top)
 -- The upper terrace is approached by the central staircase.
 ledge(0,68,65,46,15)
 stairs(V(0,6,28),20,12,.8,2)
 for _,x in ipairs({-13,13}) do
  for _,z in ipairs({32,42,53}) do lamp(V(x,6+(z-28)*.4,z),.8) end
 end
 if shadow then
  -- A gothic keep and glowing sigils, with a hooded statue on its forecourt.
  block("CasteloCentral",V(37,32,15),V(0,31,78),rock,architecture)
  for _,x in ipairs({-29,29}) do tower(V(x,15.8,72),34,9) end
  for _,x in ipairs({-19,19}) do tower(V(x,15.8,89),47,8) end
  for _,x in ipairs({-13,13}) do part("ColunaArcana",V(1.2,33,1.2),V(x,32,69),accent,architecture,nil,Enum.Material.Neon,false) end
  local rune=part("SeloCastelo",V(22,22,.25),V(0,43,69.9),trim,architecture)
  emblem(rune,C(184,56,255),"moon")
  local entry=part("PortaCastelo",V(12,17,.35),V(0,24,69.8),C(22,16,35),architecture)
  for i=0,6 do
   local w=37-i*4.7
   block("EmpenaCastelo",V(w,2.2,17),V(0,48+i*2,78),trim,architecture)
  end
  for _,x in ipairs({-7,7}) do
   part("MolduraPorta",V(1.1,18,1.2),V(x,24,69.1),trim,architecture)
   lamp(V(x,16,66),.7)
  end
  cylinder("Pedestal",5,2,V(0,17,57),trim,architecture)
  block("EstatuaCorpo",V(3,5,2),V(0,20.5,57),C(32,27,43),architecture)
  ball("Capuz",V(3,3.3,3),V(0,24,57),C(34,27,47),architecture)
  part("RostoOculto",V(1.5,1.4,.2),V(0,23.9,55.55),C(9,8,16),architecture)
  for _,side in ipairs({-1,1}) do
   part("BraçoEstatua",V(1.1,4,1.2),V(side*2,21,57),C(33,27,44),architecture,CFrame.Angles(0,0,side*.28))
   lamp(V(side*7,16,55),1)
  end
  waterfall(72,65,36,11) waterfall(-77,31,30,10)
  for _,p in ipairs({{96,50,70},{-85,56,89},{-114,65,-5}}) do
   for j=0,3 do
    block("IlhaFlutuante",V(4+j*3,2.4,4+j*2.8),V(p[1],p[2]-4.5+j*2.4,p[3]),rock,land,CFrame.Angles(0,.2,0))
   end
   block("GramaFlutuante",V(13,1,12),V(p[1],p[2]+4.1,p[3]),grass,land)
  end
  local moon=part("Eclipse",V(1.5,39,39),V(-62,85,96),C(135,38,255),architecture,CFrame.Angles(0,pi/2,0),Enum.Material.Neon,false)
  moon.Shape=Enum.PartType.Cylinder
  local mask=part("SombraDoEclipse",V(1.6,36,36),V(-59,87,94),C(24,15,47),architecture,CFrame.Angles(0,pi/2,0),Enum.Material.Plastic,false)
  mask.Shape=Enum.PartType.Cylinder
  banner(V(91,24,43),17) banner(V(-99,33,-22),18) banner(V(37,16,70),17)
  local lore=plaque("NAS SOMBRAS\nNASCEM\nOS MAIS FORTES.",V(94,29,-5),Vector2.new(17,14),rock)
 else
  -- Capsule HQ, training house, Karin tower and floating lookout.
  dome(V(0,16,68),22,14,C(41,98,207),"CAPSULE\nCORP.")
  dome(V(67,12,-1),12,8,C(228,137,43),"KAME")
  ledge(70,1,32,33,11)
  stairs(V(64,6,-30),15,7,.8,2)
  for _,p in ipairs({{-28,16,50},{28,16,50},{-34,6,23},{37,6,13},{53,12,14},{-61,6,23}}) do palm(V(p[1],p[2],p[3]),12) end
  cylinder("TorreKarin",3,53,V(-43,43,92),C(228,234,230),architecture)
  for _,y in ipairs({24,43,63}) do cylinder("AnelTorreKarin",3.3,.65,V(-43,y,92),accent,architecture) end
  dome(V(-43,69,92),8,4,C(40,109,217),"")
  cylinder("MiranteFlutuante",19,2.4,V(-104,62,91),C(216,229,219),architecture)
  cylinder("MiranteBase",13,9,V(-104,57,91),C(226,231,219),architecture)
  dome(V(-104,63.5,91),9,5,C(58,119,219),"KAMI")
  for _,x in ipairs({-117,-92}) do tree(V(x,64.5,91),.4) end
  local dragon=ball("EsferaDoDragao",V(43,43,43),V(93,49,90),C(255,174,31),architecture,Enum.Material.Plastic)
  local stars=part("EstrelasDaEsfera",V(27,20,.1),V(93,50,68.4),C(255,174,31),architecture,nil,nil,false)
  stars.Transparency=1 text(stars,"★\n★  ★",C(190,48,34))
  waterfall(48,76,39,12) waterfall(-75,43,40,11)
  banner(V(-91,18,-26),15)
  plaque("TORRE\nKARIN  ↑",V(-43,28,71),Vector2.new(13,8),wood)
  plaque("MINERAIS\nDRAGON BALL",V(81,12,-45),Vector2.new(15,8),wood)
 end
 -- Left mine and right travel portal are navigable parts of both islands.
 local mine=V(shadow and 83 or -83,12,24)
 ledge(mine.X,26,30,35,11)
 for _,x in ipairs({-10,10}) do
  block("ColunaMina",V(5,16,8),mine+V(x,8,0),rock,architecture)
  part("SuporteMina",V(1.3,13,1.2),mine+V(x*.8,6.5,-5),wood,architecture)
 end
 block("TetoMina",V(25,5,12),mine+V(0,17,1),rock,architecture)
 part("FundoMina",V(16,14,.4),mine+V(0,7,9),C(18,16,24),architecture)
 part("PisoMina",V(18,.3,18),mine+V(0,.2,1),soil,architecture)
 local sign=plaque(shadow and "MINAS\nSHADOW GARDEN" or "PLANETA\nNAMEKUSEI",mine+V(0,17,-5.5),Vector2.new(21,5),wood)
 for _,x in ipairs({-8,8}) do lamp(mine+V(x,0,-7),.8) end
 for z=-10,7,2 do part("DormenteMina",V(6,.2,.55),mine+V(0,.4,z),wood,architecture) end
 for _,x in ipairs({-2,2}) do line("TrilhoMina",mine+V(x,.7,-10),mine+V(x,.7,7),.24,C(130,133,141),architecture,Enum.Material.Metal) end
 block("Carrinho",V(4,2.7,4.3),mine+V(0,1.8,4),trim,architecture)
 local exit=V(shadow and -84 or -69,12,76)
 ledge(exit.X,77,29,28,11)
 bridge(V(-58,6,49),V(exit.X,12,66),10,1.3)
 for _,x in ipairs({-9,9}) do block("PilarPortal",V(3,17,4),exit+V(x,8.5,0),trim,architecture) end
 block("LintelPortal",V(22,3,4),exit+V(0,18,0),rock,architecture)
 local portal=part("PortalProximaArea",V(14,14,.8),exit+V(0,8.5,0),accent,architecture,nil,Enum.Material.Neon,false)
 portal.Transparency=.23
 if shadow then emblem(portal,C(72,21,139),"moon") else text(portal,"✦",C(226,241,255)) end
 local pad=part("ViagemProximaArea",V(14,1,10),exit+V(0,.6,-4),accent,architecture,nil,Enum.Material.Neon,false)
 pad.CanTouch=true pad.Transparency=.65 pad:SetAttribute("NextAreaId",area.id+1)
 plaque("PRÓXIMA ÁREA\nDERROTE O CHEFE",exit+V(0,23,0),Vector2.new(23,7),trim)
 for _,x in ipairs({-10,10}) do lamp(exit+V(x,0,-7),.9) end
 -- Foreground details and stones around the grassy rim.
 for i=1,32 do
  local angle=random:NextNumber(0,2*pi) local radius=random:NextNumber(69,75)
  local x,z=math.sin(angle)*radius,math.cos(angle)*radius
  block("PedraDecorativa",V(random:NextNumber(1.5,3),1.1,2),V(x,6.1,z),rock:Lerp(grass,.2),decor)
  if i%4==0 then tree(V(x,5.8,z),.6) end
 end
 for _,p in ipairs({{50,6,41},{-49,6,35},{58,6,-37},{-62,6,-28},{29,6,-61}}) do
  if shadow then tree(V(p[1],p[2],p[3]),.66) else palm(V(p[1],p[2],p[3]),11) end
 end
 if shadow then
  for _,p in ipairs({{-42,-43},{44,-43},{-54,12},{54,23},{33,61}}) do
   local crystal=part("CristalSombrio",V(1.5,4,1.5),V(p[1],7.5,p[2]),accent,decor,CFrame.Angles(0,.3,.15),Enum.Material.Neon,false)
  end
 end
 local spots={{-40,-36},{38,-36},{-22,-48},{21,-48},{-49,-8},{48,-3},{-32,12},{33,13},
 {-49,27},{48,31},{-27,-24},{29,-20},{-11,14},{12,16},{-34,38},{32,40},
 {-50,-40},{50,-42},{-17,39},{17,40},{-56,9},{54,13}}
 local spawns={}
 for i,p in ipairs(spots) do table.insert(spawns,{pos=center+V(p[1],6,p[2]),variant=i%7==0 and 3 or i%3==0 and 2 or 1}) end
 parent:SetAttribute("EntryPosition",center+V(0,9,-82))
 return {spawns=spawns,boss=center+V(-21,6,29),returnPad=center+V(13,5.6,-83)}
end
return M

