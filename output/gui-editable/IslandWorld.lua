-- Six authored teleport destinations. All mandatory interaction routes share one ground level.
local Art=require(script.Parent.IslandArt)
local M={}
local V=Vector3.new local C=Color3.fromRGB local pi=math.pi
local palettes={
 {rock=C(156,117,75),soil=C(206,179,128),grass=C(99,161,52),foliage=C(66,128,54),path=C(229,208,159),wood=C(108,67,37),trim=C(54,47,41),water=C(43,158,199),glow=C(255,193,96),accent=C(196,66,40)},
 {rock=C(156,128,101),soil=C(190,188,129),grass=C(106,171,123),foliage=C(67,145,164),path=C(218,214,169),wood=C(121,99,65),trim=C(49,74,83),water=C(66,155,126),glow=C(238,212,139),accent=C(52,143,218)},
 {rock=C(82,99,106),soil=C(123,135,113),grass=C(60,102,63),foliage=C(39,80,68),path=C(172,174,148),wood=C(80,62,47),trim=C(39,47,49),water=C(48,106,132),glow=C(249,185,100),accent=C(117,144,212)},
 {rock=C(68,60,91),soil=C(104,94,125),grass=C(75,59,116),foliage=C(94,55,139),path=C(150,140,168),wood=C(64,43,66),trim=C(34,29,48),water=C(108,57,174),glow=C(192,133,255),accent=C(148,67,222)},
 {rock=C(171,132,91),soil=C(219,190,134),grass=C(95,154,67),foliage=C(49,123,71),path=C(234,217,172),wood=C(129,82,47),trim=C(61,66,73),water=C(40,154,188),glow=C(255,206,123),accent=C(59,127,165)},
 {rock=C(103,115,120),soil=C(145,151,148),grass=C(95,130,92),foliage=C(66,103,76),path=C(191,193,178),wood=C(102,92,75),trim=C(47,57,64),water=C(55,114,139),glow=C(239,223,165),accent=C(200,152,57)},
}
local function emblem(A,pos,size,kind,col,face,parent)
 local board=A.part('Brasao',V(size,size,.15),pos,col,parent or A.buildings)
 local templates=game.StarterGui.InterfacesMundo.Templates
 local g=templates['Brasao_'..kind]:Clone()
 g.Name='SurfaceGui';g.Enabled=true;g.Adornee=board;g.Face=face or Enum.NormalId.Front
 for _,o in g:GetDescendants() do
  if o:IsA('Frame') and o:GetAttribute('Recorte') then o.BackgroundColor3=col end
 end
 g.Parent=board
 return board
end
local function dome(A,pos,r,h,roof,label)
 local p=A.pal local m=A.group(label or 'HabitaçãoNamek',A.buildings)
 A.cylinder('Fundacao',r+1.3,.8,pos+V(0,.4,0),p.trim,m,true)
 A.cylinder('Corpo',r,h,pos+V(0,h/2+.8,0),C(218,218,196),m,true)
 for i=0,10 do local t=(i+.5)/11 A.cylinder('PainelCupula',r*math.sqrt(1-t*t),r*.72/11+.05,pos+V(0,h+.8+t*r*.72,0),roof:Lerp(C(175,199,217),i*.013),m,true) end
 A.cylinder('FrisoBase',r+.1,.4,pos+V(0,2,0),p.accent,m,false)
 A.part('Entrada',V(4,6.5,.4),pos+V(0,3.9,-r-.1),p.trim,m)
 A.part('Porta',V(3,5.8,.4),pos+V(0,3.6,-r-.4),p.glow,m,nil,false)
 for i=1,9 do
  local a=i/10*pi*2 local q=pos+V(math.sin(a)*(r+.2),4.8,-math.cos(a)*(r+.2))
  A.part('MolduraJanela',V(2.6,3.2,.5),q,p.trim,m,CFrame.Angles(0,-a,0))
  A.part('VidroAzul',V(2.1,2.6,.55),q,C(85,160,191),m,CFrame.Angles(0,-a,0))
 end
 if label then A.sign(label,pos+V(0,h-1,-r-.4),r*1.45,3.2,m,C(71,90,108)) end
 return m
end
local function ajisa(A,pos,h)
 local m=A.group('Ajisa',A.plants)
 for i=0,5 do A.cylinder('TroncoAnelado',.65-i*.055,h/6+.2,pos+V(math.sin(i*.25)*.6,(i+.5)*h/6,0),C(128+i*7,140+i*4,126),m,true) end
 A.ball('CopaAzul',V(14,9,14),pos+V(.5,h+2,0),C(66,141,165),m)
 A.ball('CopaLateral',V(9,6,10),pos+V(-3,h+.5,-1),C(58,130,151),m)
 A.ball('CopaIluminada',V(8,6,9),pos+V(2,h+4,1),C(76,154,173),m)
end
local function cedar(A,pos,h)
 local m=A.group('CedroDaMontanha',A.plants)
 A.cylinder('Tronco',1.1,h,pos+V(0,h/2,0),A.pal.wood,m,true,Enum.Material.Wood)
 local tree=A.tree(pos,h/21.6,A.pal.foliage,m)
 if tree then for _,part in tree:GetDescendants() do if part:IsA('BasePart') then part.CanCollide=false part.CanQuery=false end end end
 for _,a in {0,2.1,4.2} do A.rod('Raiz',pos+V(0,.6,0),pos+V(math.cos(a)*3,.15,math.sin(a)*3),.6,A.pal.wood,m) end
end
local function cityBuilding(A,pos,w,d,h,color,label)
 local p=A.pal local m=A.group(label or 'Edificio',A.buildings)
 A.part('Concreto',V(w,h,d),pos+V(0,h/2,0),color,m,nil,true)
 for y=0,h,5 do A.part('LajeEntrePisos',V(w+.6,.5,d+.6),pos+V(0,y,0),color:Lerp(p.trim,.22),m) end
 for y=3.2,h-2,5 do for x=-w/2+3,w/2-2,5 do
  A.part('Moldura',V(3.1,3.2,.35),pos+V(x,y,-d/2-.18),p.trim,m)
  A.part('Vidro',V(2.6,2.65,.4),pos+V(x,y,-d/2-.23),C(99,146,158):Lerp(p.glow,A.rng:NextNumber()<.14 and .45 or 0),m)
  A.part('Caixilho',V(.14,2.7,.5),pos+V(x,y,-d/2-.28),color,m)
 end end
 for _,x in {-w/2+.3,w/2-.3} do A.part('Pilastra',V(.8,h,.5),pos+V(x,h/2,-d/2-.35),color:Lerp(p.trim,.14),m) end
 A.part('Cobertura',V(w+1,1,d+1),pos+V(0,h+.2,0),p.trim,m)
 A.part('CaixaDagua',V(w*.3,4,d*.4),pos+V(w*.22,h+2.5,0),C(104,119,124),m)
 for i=1,3 do A.part('Ventilação',V(2,.8,2),pos+V(-w*.25,h+1,i*3-d*.25),C(170,177,177),m) end
 A.part('Entrada',V(6,6,.5),pos+V(0,3,-d/2-.25),C(65,87,98),m)
 if label then A.sign(label,pos+V(0,8.4,-d/2-.7),math.min(25,w-1),2.8,m,C(45,67,83)) end
 return m
end
function M.build(parent,area)
 local p=palettes[area.id] local c=area.centro local A=Art.new(parent,c,p,7000+area.id) local rng=A.rng local id=area.id
 parent.ModelStreamingMode=Enum.ModelStreamingMode.PersistentPerPlayer
 parent:SetAttribute('WorldRevision',5) parent:SetAttribute('BoundsHalfSize',V(146,120,146))
 parent:SetAttribute('EntryPosition',c+V(0,9.5,-85)) parent:SetAttribute('SafePosition',c+V(0,9.5,-73))
 parent:SetAttribute('GachaPosition',c+V(-43,6.35,-79))
 -- A continuous core eliminates repeated jumping/stair climbing between mining targets.
 A.block('SoloCentral',V(152,12,228),V(0,0,0),id==6 and p.soil or p.grass:Lerp(p.soil,.24),A.land)
 -- Irregular mining clearings contrast with planted verges and the stone circulation routes.
 for _,x in {-40,40} do for _,z in {-34,35} do
  for _,q in {{0,0,47,44},{-5,0,42,49},{3,2,49,37}} do
   A.block('ClareiraMineral',V(q[3],.06,q[4]),V(x+q[1],6.05,z+q[2]),p.soil:Lerp(p.path,.1),A.land,CFrame.Angles(0,q[1]*.012,0),false)
  end
 end end
 for _,s in {-1,1} do A.block('MargemExterior',V(48,12,288),V(s*120,0,0),p.grass,A.land) end
 for _,z in {-129,129} do A.block('FundoBacia',V(192,12,30),V(0,0,z),p.grass,A.land) end
 A.block('LeitoRaso',V(288,3,288),V(0,-2,0),p.rock,A.land)
 for _,s in {-1,1} do
  A.waterSurface(V(s*86,2.3,0),V(20,.35,228))
  for _,z in {-61,25,87} do A.bridge(V(s*69,6.05,z),V(s*107,6.05,z),16,id==4 or id==5 or id==6) end
  for _,zs in {{-111,-71},{-51,15},{35,77},{97,111}} do
   A.fence(V(s*75.4,6,zs[1]),V(s*75.4,6,zs[2]),id==4 or id==6)
   A.fence(V(s*97,6,zs[1]),V(s*97,6,zs[2]),id==4 or id==6)
  end
  A.path(V(s*109,6,-100),V(s*109,6,103),18,p.path,true)
  for z=-102,100,14 do
   local flow=A.part('CorrenteFolha',V(.18,.04,2.6),V(s*86,2.6,z),p.water:Lerp(C(222,239,245),.55),A.water)
   flow.Transparency=.65 flow:SetAttribute('FlowA',c+V(s*86,2.6,z+6)) flow:SetAttribute('FlowB',c+V(s*86,2.6,z-7)) flow:SetAttribute('FlowPhase',rng:NextNumber())
  end
 end
 -- Broad entry concourse, a 22-stud spine and three 18-stud cross routes.
 A.path(V(0,6,-106),V(0,6,94),22,p.path,true)
 for _,z in {-62,1,65} do A.path(V(-70,6,z),V(70,6,z),18,p.path,true) end
 A.path(V(-60,6,-88),V(60,6,-88),22,p.path,true)
 for _,x in {-71,71} do A.path(V(x,6,-64),V(x,6,67),6,p.path) end
 -- Landscape enclosure: varied silhouettes, strata and outcrops instead of a flat block wall.
 for s=-1,1,2 do
  for i=0,6 do local z=-112+i*36 local h=(id==6 and 32 or 31)+rng:NextInteger(0,24)
   if id~=6 then A.cliff(V(s*(140+i%2*3),-6,z),39,27,h) else cityBuilding(A,V(s*139,6,z),24,31,h+15,C(117+i%3*10,132+i%2*8,138)) end
  end
 end
 for i=-4,4 do
  local x=i*33 local h=(id==3 and 65 or 48)+rng:NextInteger(0,26)
  if id~=6 then A.cliff(V(x,-6,139+i%2*4),35,29,h) else cityBuilding(A,V(x,6,139),29,27,h,C(123+i%3*8,135+i%2*6,141)) end
  A.cliff(V(x,-6,-137),35,28,25+rng:NextInteger(0,12))
 end
 for _,s in {-1,1} do
  A.waterfall(V(s*87,2.5,112),id==3 and 41 or id==4 and 48 or 35,13)
  for _,z in {-93,-20,57,105} do A.rock(V(s*122,6,z),V(7,4+z%4,8),p.rock) end
 end
 -- Invisible closure lies inside the scenery, with a server-owned recovery layer as well.
 local limits=A.group('LimitesDaArea')
 for _,s in {-1,1} do
  local x=A.part('LimiteLateral',V(6,220,304),V(s*149,82,0),p.rock,limits,nil,true) x.Transparency=1
  local z=A.part('LimiteFrontal',V(304,220,6),V(0,82,s*149),p.rock,limits,nil,true) z.Transparency=1
 end
 local ceiling=A.part('LimiteSuperior',V(304,4,304),V(0,190,0),p.rock,limits,nil,true) ceiling.Transparency=1
 -- Localised gardens occupy the edges; no debris is collidable in a mining approach lane.
 for _,s in {-1,1} do for _,z in {-101,-32,37,107} do
  A.shrub(V(s*70,6,z),2.4,p.grass) A.tuft(V(s*68,6,z+4),1.5)
  A.lamp(V(s*71,6,z+6),.9)
 end end
 for i=1,52 do
  local s=i%2==0 and 1 or -1 local z=rng:NextNumber(-109,107) local x=s*rng:NextNumber(118,128)
  A.tuft(V(x,6,z),rng:NextNumber(.7,1.9),p.grass:Lerp(p.foliage,.25))
  if i%6==0 then A.shrub(V(x,6,z),2,p.foliage) end
 end
 for _,q in {{-18,-73},{18,-73},{-16,64},{16,64}} do A.lamp(V(q[1],6,q[2]),1) end
 for _,q in {{-58,-99},{58,-99}} do A.bench(V(q[1],6,q[2])) A.shrub(V(q[1]-5,6,q[2]),2) end
 -- Planted islands frame the entry and break up the long view, without occupying the travel spine.
 for _,q in {{-20,-90},{20,-90},{-18,83},{18,83},{-63,7},{63,-7}} do
  local x,z=q[1],q[2]
  A.block('Canteiro',V(9,.4,12),V(x,6.2,z),p.grass,A.plants,nil,false)
  for _,s in {-1,1} do A.part('PedraDoCanteiro',V(.7,.5,12),V(x+s*4.5,6.4,z),p.rock,A.plants) end
  A.shrub(V(x,6.4,z-3),1.9,p.foliage)
  if math.abs(z)>70 then
   if id==2 then ajisa(A,V(x,6.5,z+2),14) elseif id==3 then cedar(A,V(x,6.5,z+2),22) else A.tree(V(x,6.5,z+2),.7,p.foliage) end
  end
  for j=1,5 do A.tuft(V(x+math.sin(j*2)*2.8,6.5,z+math.cos(j*2)*3.5),1,p.grass) end
 end
 for _,x in {-15,15} do for _,z in {-43,-27,24,42} do
  A.shrub(V(x,6,z),1.15,p.grass)
  for j=1,3 do
   local pos=V(x+(j-2)*.8,6.4,z+.8)
   A.part('HasteFlor',V(.08,.7,.08),pos,p.foliage,A.plants)
   A.ball('Flor',V(.45,.25,.45),pos+V(0,.45,0),id==4 and C(171,118,230) or id==3 and C(171,148,209) or C(226,198,124),A.plants)
  end
 end end
 -- Small inset stones give the open ground wear, rather than a perfectly smooth sheet.
 for i=1,72 do
  local x=rng:NextNumber(-65,65) local z=rng:NextNumber(-102,94)
  if math.abs(x)>13 and math.abs(z)>13 and math.abs(z+62)>12 and math.abs(z-65)>12 then
   A.part('SeixoRenteAoSolo',V(rng:NextNumber(.5,1.6),.08,rng:NextNumber(.5,1.2)),V(x,6.16,z),p.soil:Lerp(p.rock,.25),A.props,CFrame.Angles(0,rng:NextNumber(0,6.28),0))
  end
 end
 -- Distinct compositions and landmarks for every anime environment.
 if id==1 then
  A.torii(V(0,6,-106),28,18)
  for _,q in {{-117,72,24,19,14,0},{115,70,23,20,20,1},{-116,-5,23,19,19,2},{116,-8,22,20,14,0}} do
   A.house(V(q[1],6,q[2]),q[3],q[4],q[5],({C(204,187,139),C(175,197,173),C(196,175,158)})[q[6]+1],C(129,62,50),q[6]==2 and 'ICHIRAKU' or 'VILA DA FOLHA',q[6]==2 and 'village' or nil)
  end
  dome(A,V(0,6,113),19,19,C(155,61,46),'GABINETE DO HOKAGE')
  emblem(A,V(0,35,93),12,'leaf',C(218,198,151))
  -- Three sculpted stone portraits read as a carved memorial at the rear cliff.
  for i=-1,1 do
   local q=V(i*28,55,128) local skin=C(188+i*4,155+i*3,111)
   A.part('FaceNaPedra',V(13,17,4),q,skin,A.buildings)
   A.part('Queixo',V(9,4,4),q+V(0,-9,-.2),skin,A.buildings)
   for _,s in {-1,1} do
    A.part('Sobrancelha',V(4,.9,.8),q+V(s*3,2,-2.3),p.rock,A.buildings,CFrame.Angles(0,0,s*.09))
    A.part('Olho',V(2.8,.45,.8),q+V(s*3,.8,-2.35),p.trim:Lerp(skin,.6),A.buildings)
   end
   A.part('Nariz',V(1.5,4,2),q+V(0,-1,-3),skin:Lerp(p.rock,.1),A.buildings)
   A.part('Boca',V(4,.4,.6),q+V(0,-5.5,-2.5),p.rock,A.buildings)
   A.part('Bandana',V(13,3,1),q+V(0,5.3,-2.7),skin:Lerp(p.rock,.18),A.buildings)
   emblem(A,q+V(0,5.3,-3.3),2.5,'leaf',skin)
   for j=-3,3 do A.rock(q+V(j*2,7,-.4),V(3,4+math.abs(j)%2*2,4),skin,A.buildings) end
  end
  for _,q in {{-65,80},{66,83},{-116,-82},{113,-78},{-47,112},{48,115}} do A.tree(V(q[1],6,q[2]),1,p.foliage) end
  for _,z in {-61,26} do
   for _,s in {-1,1} do A.rod('FioLanternas',V(s*58,18,z),V(s*118,18,z),.12,p.wood) end
   for _,x in {-107,-95,-83,-71,71,83,95,107} do A.lamp(V(x,12.5,z),.6) end
  end
  for _,q in {{-57,6,79},{57,6,80},{-115,6,37}} do
   A.emit(V(q[1],q[2]+7,q[3]),C(231,185,133),.8,.16,nil,V(.6,-.25,0))
  end
 elseif id==2 then
  -- The lakes and blue Ajisa crowns distinguish Namek from the Earth's Capsule architecture.
  dome(A,V(-24,6,111),20,17,C(59,122,179),'CAPSULE CORP.') emblem(A,V(-24,33,91),10,'capsule',C(224,219,196))
  dome(A,V(114,6,68),11,8,C(196,213,180),'VILA NAMEK') dome(A,V(-116,6,62),10,8,C(181,203,164),nil)
  for _,q in {{-114,-88},{115,-88},{-114,-29},{118,4},{-62,91},{53,106},{-103,103},{108,110}} do ajisa(A,V(q[1],6,q[2]),18+rng:NextInteger(0,6)) end
  A.cylinder('PlataformaEsferas',12,.35,V(44,6.2,108),p.trim,A.buildings,false)
  for i=1,7 do local a=i/7*pi*2 local q=V(44+math.sin(a)*7,8.1,108+math.cos(a)*7)
   A.ball('EsferaDoDragao',V(2.7,2.7,2.7),q,C(240,160,47),A.buildings)
   A.part('Estrela',V(.45,.45,.15),q+V(0,0,-1.3),C(158,47,27),A.buildings,CFrame.Angles(0,0,pi/4))
  end
  for _,s in {-1,1} do for i=1,3 do A.rock(V(s*115,6,-46+i*12),V(5,3,6),p.rock) end end
  for _,q in {{-60,9,77},{53,9,78},{-102,4,-20},{102,4,40}} do A.emit(V(q[1],q[2],q[3]),C(146,228,190),1,.15,nil,V(0,.4,0)) end
 elseif id==3 then
  A.torii(V(0,6,-104),27,18,C(109,54,45))
  A.house(V(0,6,110),34,23,13,C(171,165,138),C(67,73,87),'CASA DA MONTANHA')
  A.house(V(-116,6,67),22,19,10,C(155,153,128),C(55,67,78),'REFUGIO NICHIRIN')
  for _,s in {-1,1} do for _,z in {-105,-80,-39,-11,46,92,113} do cedar(A,V(s*(117+z%7),6,z),27+rng:NextInteger(0,14)) end end
  for _,q in {{-55,103},{48,102},{-60,-98},{61,-99}} do A.tree(V(q[1],6,q[2]),1.1,C(111,87,146)) end
  for _,x in {-15,15} do for _,z in {-39,35} do cedar(A,V(x,6,z),29) end end
  for _,q in {{-49,82},{53,85},{-119,22},{121,-63}} do for j=1,6 do
   local x,z=q[1]+math.sin(j*2)*2,q[2]+math.cos(j*2)*2 local h=11+j%3*2
   A.cylinder('Bambu',.22,h,V(x,6+h/2,z),C(76,113,68),A.plants,false)
   for y=8,6+h,2 do A.cylinder('NoDoBambu',.26,.16,V(x,y,z),C(112,139,81),A.plants,false) end
  end end
  for _,q in {{-126,26,35},{122,30,87},{-52,37,126}} do
   local pos=V(q[1],q[2],q[3]) local points={} for i=0,7 do local a=i*pi/4 points[i+1]=V(math.sin(a)*10,math.cos(a)*10,0) A.rod('FioTeia',pos,pos+points[i+1],.06,C(194,209,212),A.plants) end
   for _,r in {.3,.55,.8} do for i=1,8 do A.rod('FioTeia',pos+points[i]*r,pos+points[i%8+1]*r,.055,C(172,197,200),A.plants) end end
  end
  for _,x in {-56,54} do for _,z in {-34,34,85} do
   A.emit(V(x,8,z),C(111,146,156),1,8,'rbxasset://textures/particles/smoke_main.dds',V(.25,0,0))
   A.emit(V(x,9,z),C(183,216,179),1,.14,nil,V(.05,.15,0))
  end end
 elseif id==4 then
  -- Cathedral, buttresses and arcaded gardens replace the single featureless castle block.
  local m=A.group('CatedralDasSombras',A.buildings)
  A.part('Nave',V(42,32,26),V(0,22,113),p.rock,m,nil,true)
  for _,x in {-20,-10,10,20} do
   A.block('Contraforte',V(3,37,7),V(x,24,97),p.trim,m)
   A.part('VeioArcano',V(.18,27,.2),V(x,24,93.4),p.accent,m,nil,false,Enum.Material.Neon)
  end
  A.part('EntradaSombria',V(15,21,.4),V(0,16.5,99.5),C(21,18,32),m)
  for _,s in {-1,1} do A.part('ArcoOgival',V(10,2,2),V(s*3.3,29,99),p.trim,m,CFrame.Angles(0,0,s*.62)) end
  emblem(A,V(0,39,98),12,'moon',p.trim,nil,m)
  for _,x in {-30,30} do
   A.block('Torre',V(12,48,14),V(x,30,112),p.rock,m)
   for y=15,51,12 do A.block('Cornija',V(13,.9,15),V(x,y,112),p.trim,m) end
   for i=0,8 do local w=14*(1-i/9) A.block('Pinaculo',V(w,2.3,w),V(x,56+i*2,112),p.trim,m) end
   A.part('JanelaVertical',V(2,24,.3),V(x,34,104.7),p.accent,m,nil,false,Enum.Material.Neon)
  end
  for _,s in {-1,1} do for _,z in {-15,35,84} do
   local q=V(s*116,6,z)
   for _,dx in {-6,6} do A.block('ColunaArcada',V(2,16,3),q+V(dx,8,0),p.rock,m) A.block('Capitel',V(3,1,4),q+V(dx,16,0),p.trim,m) end
   for _,k in {-1,1} do A.part('ArcoArcada',V(8,1.5,3),q+V(k*2.8,18.6,0),p.rock,m,CFrame.Angles(0,0,k*.54)) end
   A.fence(q+V(-6,0,3),q+V(6,0,3),true,m)
   A.tree(q+V(2,0,9),1,p.foliage)
  end end
  A.torii(V(0,6,-106),29,18,p.trim)
  for _,q in {{-54,95},{53,99},{-120,-88},{119,-86}} do A.tree(V(q[1],6,q[2]),1.1,p.foliage) end
  for _,q in {{-58,6,-34},{58,6,32},{-45,6,87}} do
   A.cylinder('ColunaArruinada',2.3,7,V(q[1],q[2]+3.5,q[3]),p.rock,A.props,false)
   A.rock(V(q[1]+4,6,q[3]+2),V(4,2,3),p.rock,A.props)
   A.emit(V(q[1],10,q[3]),C(160,103,216),1,.2,nil,V(0,.4,0))
  end
  A.cylinder('Eclipse',16,1,V(-63,91,137),p.accent,A.buildings,false,Enum.Material.Neon).CFrame=CFrame.new(c+V(-63,91,137))*CFrame.Angles(0,pi/2,0)
  A.cylinder('DiscoEclipse',15.2,1.2,V(-61.5,92,136),p.trim,A.buildings,false).CFrame=CFrame.new(c+V(-61.5,92,136))*CFrame.Angles(0,pi/2,0)
 elseif id==5 then
  -- White stone, tiled roofs, quays and moorings draw on Water Seven's canal streets.
  A.house(V(0,6,112),36,23,20,C(218,212,175),C(171,77,49),'PORTO GRAND LINE')
  for _,q in {{-116,70,23,20,24},{115,69,24,19,18},{-116,-4,23,20,15},{114,-8,22,18,22}} do
   A.house(V(q[1],6,q[2]),q[3],q[4],q[5],q[1]<0 and C(197,207,190) or C(231,207,159),q[2]>0 and C(162,66,42) or C(69,119,145),q[2]>0 and 'ESTALEIRO' or 'MERCADO DO CAIS',q[2]<0 and 'village' or nil)
  end
  for _,s in {-1,1} do for _,z in {-91,-35,54,106} do
   A.part('AmarraDoCais',V(.75,4,.75),V(s*98,8,z),p.wood,A.props,nil,false,Enum.Material.Wood)
   for y=7,9,1 do A.cylinder('CordaEnrolada',.6,.2,V(s*98,y,z),C(177,149,99),A.props,false) end
   A.barrel(V(s*104,6,z+3))
  end end
  -- A compact sailing vessel sits in the eastern canal without consuming a movement route.
  local ship=V(86,1.8,-28) local sm=A.group('Caravela',A.buildings)
  for i=0,3 do A.part('Casco',V(12-i*1.4,.9,31-i*2),ship+V(0,i*.75,0),p.wood:Lerp(p.trim,.3-i*.05),sm) end
  for z=-12,12,2 do A.part('Conves',V(10,.3,1.95),ship+V(0,3,z),C(171,132,81),sm,nil,false,Enum.Material.Wood) end
  A.part('Mastro',V(.65,25,.65),ship+V(0,15,0),p.wood,sm)
  A.part('Verga',V(16,.6,.6),ship+V(0,23,0),p.wood,sm)
  A.part('Vela',V(14,13,.3),ship+V(0,17,-.25),C(231,224,194),sm)
  emblem(A,ship+V(0,18,-.48),6,'compass',C(231,224,194),nil,sm)
  for _,s in {-1,1} do A.rod('Cordame',ship+V(0,27,0),ship+V(s*5,3,-10),.1,p.trim,sm) end
  for _,q in {{-116,-94},{117,-95},{-61,102},{63,100}} do A.tree(V(q[1],6,q[2]),.95,p.foliage) end
  -- Beacon and dock cargo create a readable port silhouette.
  A.cylinder('Farol',5,31,V(113,21.5,111),C(224,214,177),A.buildings,true)
  for _,y in {15,24,34} do A.cylinder('FaixaFarol',5.1,2,V(113,y,111),C(156,65,42),A.buildings,false) end
  A.cylinder('VarandaFarol',6.5,.8,V(113,37,111),p.trim,A.buildings,false)
  A.part('LanternaFarol',V(6,5,6),V(113,40,111),p.glow,A.buildings,nil,false,Enum.Material.Neon)
  A.cylinder('ChapeuFarol',6.5,1,V(113,43,111),C(156,65,42),A.buildings,false)
  for i=1,5 do A.crate(V(-119+i%2*3,6+(i>3 and 2.6 or 0),34+math.floor(i/2)*3)) end
 elseif id==6 then
  -- City blocks replace the mountain-estate layout: usable streets at one level.
  A.path(V(0,6.2,-106),V(0,6.2,102),22,C(63,72,79))
  A.path(V(-70,6.2,1),V(70,6.2,1),18,C(63,72,79))
  for z=-100,92,13 do if math.abs(z)>14 then A.part('FaixaDaAvenida',V(.4,.04,5),V(0,6.4,z),C(221,204,140)) end end
  for _,z in {-14,15} do for x=-8,8,3 do A.part('FaixaPedestre',V(1.8,.04,5),V(x,6.4,z),C(211,214,198)) end end
  cityBuilding(A,V(0,6,115),36,23,43,C(160,173,176),'ASSOCIACAO DOS HEROIS')
  emblem(A,V(0,43,103),8,'hero',C(213,181,89))
  for _,q in {{-116,66,24,22,28},{116,64,23,22,37},{-116,-12,23,25,22},{115,-10,23,23,29}} do
   cityBuilding(A,V(q[1],6,q[2]),q[3],q[4],q[5],q[1]<0 and C(165,167,153) or C(144,160,162),q[2]<0 and 'CIDADE Z' or 'RESIDENCIAL')
  end
  -- Saitama's modest apartment, utility pipes, awnings and signs provide street-scale details.
  cityBuilding(A,V(-49,6,114),22,18,14,C(184,175,148),'APARTAMENTOS')
  for _,x in {-55,-46} do A.part('Varanda',V(7,.4,2),V(x,14,103.5),p.trim,A.buildings) A.fence(V(x-3,14,102.5),V(x+3,14,102.5),true,A.buildings) end
  for _,s in {-1,1} do for _,z in {-74,-30,31,83} do
   local q=V(s*69,6,z) A.part('PosteUrbano',V(.4,10,.4),q+V(0,5,0),p.trim)
   A.rod('BracoLuminaria',q+V(0,10,0),q+V(-s*3,10.5,0),.3,p.trim)
   local b=A.part('Luminaria',V(2,.3,1),q+V(-s*3,10.3,0),p.glow,nil,nil,false,Enum.Material.Neon)
   local l=Instance.new('PointLight') l.Brightness=.3 l.Range=13 l.Color=p.glow l.Parent=b
  end end
  for _,q in {{-61,-33},{58,37},{49,96}} do
   A.part('BarreiraObra',V(6,2.3,.4),V(q[1],7.2,q[2]),C(206,161,51),A.props)
   for i=-2,2 do A.part('ListraObra',V(.65,2.4,.43),V(q[1]+i,7.2,q[2]),p.trim,A.props,CFrame.Angles(0,0,.4)) end
   A.emit(V(q[1]+2,6.7,q[2]+3),C(155,164,166),.8,3,'rbxasset://textures/particles/smoke_main.dds',V(0,.6,0))
  end
  for _,q in {{-121,-90},{119,-91},{53,110}} do A.tree(V(q[1],6,q[2]),.9,p.foliage) end
 end
 -- An illuminated excavation entrance, rail sleepers and a mine cart finish the rear edge.
 local mine=V(id==2 and 66 or -65,6,110) local tunnel=A.group('EntradaDaMina',A.buildings)
 for _,s in {-1,1} do
  A.rock(mine+V(s*10,0,1),V(7,16,10),p.rock,tunnel)
  A.part('EscoraDaMina',V(1.1,12,1.1),mine+V(s*7,6,-4),p.wood,tunnel,nil,true,Enum.Material.Wood)
  A.lamp(mine+V(s*9,0,-5),.85,tunnel)
 end
 A.rock(mine+V(0,12,1),V(22,7,10),p.rock,tunnel)
 A.part('TravessaDaMina',V(17,1,1.3),mine+V(0,12,-4),p.wood,tunnel,nil,false,Enum.Material.Wood)
 A.part('EscuridaoDoTunel',V(15,12,.4),mine+V(0,6,7),C(23,25,29),tunnel,nil,true)
 A.path(mine+V(0,0,-17),mine+V(0,0,6),15,p.soil)
 for z=-13,5,2.6 do A.part('Dormente',V(5.5,.13,.65),mine+V(0,.19,z),p.wood,tunnel,nil,false,Enum.Material.Wood) end
 for _,x in {-1.9,1.9} do A.rod('Trilho',mine+V(x,.33,-13),mine+V(x,.33,5),.16,C(115,120,125),tunnel,Enum.Material.Metal) end
 A.part('Vagoneta',V(4,2.7,4),mine+V(0,1.7,3),p.trim,tunnel)
 for _,x in {-2,2} do for _,z in {1.8,4.2} do A.ball('Roda',V(.4,1.1,1.1),mine+V(x,.6,z),p.rock,tunnel) end end
 A.sign(id==6 and 'TUNEL DE ESCAVACAO' or 'MINERAIS',mine+V(0,17,-4.5),19,3.2,tunnel)
 A.crate(mine+V(-11,0,-5),1) A.barrel(mine+V(11,0,-4),1)
 -- Banners and pennants add movement; local ambience animates only nearby parts.
 for _,s in {-1,1} do
  local q=V(s*68,6,-97)
  A.part('MastroDoEstandarte',V(.4,12,.4),q+V(0,6,0),p.wood)
  A.rod('TravessaDoEstandarte',q+V(-3,11.4,0),q+V(3,11.4,0),.3,p.wood)
  local cloth=emblem(A,q+V(0,8.5,-.15),5,id==1 and 'leaf' or id==2 and 'capsule' or id==3 and 'katana' or id==4 and 'moon' or id==5 and 'compass' or 'hero',id==4 and p.trim or p.path)
  cloth:SetAttribute('IslandSway',true) cloth:SetAttribute('SwayPhase',s+2)
 end
 -- Tiny distant bird silhouettes add motion without obstructing the mining field.
 if id==1 or id==2 or id==5 then for i=1,3 do
  local bird=A.group('PassaroDaIlha',A.water)
  local origin=V(-35+i*30,43+i*4,61)
  A.part('Corpo',V(.45,.3,1.3),origin,p.trim,bird)
  for _,s in {-1,1} do A.part('Asa',V(1.4,.12,.6),origin+V(s*.8,.2,0),p.trim,bird,CFrame.Angles(0,0,s*.2)) end
  bird:SetAttribute('IslandBird',true) bird:SetAttribute('OrbitCenter',c+origin) bird:SetAttribute('OrbitRadius',17+i*4) bird:SetAttribute('OrbitPhase',i*2)
 end end
 -- A finished summoning alcove sits beside the arrival point in every destination.
 A.path(V(-43,6,-88),V(-43,6,-76),18,p.path,true)
 local kiosk=A.group('AlcovaDeInvocacao',A.buildings)
 for _,x in {-51,-35} do A.part('PilarAlcova',V(.65,12,.65),V(x,12,-75),p.wood,kiosk) end
 A.roof(V(-43,6,-76),22,16,12,id==4 and p.trim or p.accent,kiosk)
 A.sign('INVOCACAO',V(-43,17,-85),15,2.2,kiosk)
 local machine=workspace.Gachas:FindFirstChild('Gacha_'..area.tema)
 if machine and machine:FindFirstChild('PadGacha') then
  local pad=machine.PadGacha
  machine:PivotTo(machine:GetPivot()+c+V(-43,6.35,-78)-pad.Position)
  pad.Size=V(10,.25,10) pad.Transparency=.75
  for _,d in machine:GetDescendants() do
   if d:IsA('BillboardGui') then d.MaxDistance=38 elseif d:IsA('BasePart') then d.CanTouch=false end
  end
 end
 -- Progression is by a readable portal, never a corridor through the next island.
 local exit=V(45,6,80) local portal=A.group('PortalDeProgressao',A.buildings)
 for _,x in {-7,7} do A.block('PilarPortal',V(2.3,15,3),exit+V(x,7.5,0),p.trim,portal) end
 A.block('ArcoPortal',V(18,2.3,3),exit+V(0,15,0),p.rock,portal)
 local pane=A.part('Limiar',V(11,12,.3),exit+V(0,7,0),p.accent,portal,nil,false,Enum.Material.Neon) pane.Transparency=.65
 pane.Transparency=.86
 for i=0,23 do local a=i/24*pi*2
  A.part('AroDoPortal',V(1.6,.6,.8),exit+V(math.sin(a)*6,7+math.cos(a)*6,-.7),p.accent,portal,CFrame.Angles(0,0,-a),false,Enum.Material.Neon)
 end
 local pad=A.part('ViagemProximaArea',V(11,.2,8),exit+V(0,.3,-3),p.accent,portal) pad.Transparency=.9
 if id<6 then pad:SetAttribute('NextAreaId',id+1) else pad:SetAttribute('Destino','lobby') pad.CanTouch=true end
 A.sign(id==6 and 'VOLTA AO LOBBY' or 'PROXIMA ILHA',exit+V(0,18,0),22,3,portal)
 A.emit(exit+V(0,4,-.5),p.accent,2,.25,nil,V(0,1,0),portal)
 for _,x in {-9,9} do A.lamp(exit+V(x,0,-3),.8) end
 local rp=V(43,6.2,-87)
 A.cylinder('MolduraRetorno',6,.15,rp,p.trim,A.paths,false)
 A.sign('LOBBY',V(43,10,-95),10,2.4)
 -- Hand-spaced ore pockets: the central/cross lanes and approach arcs stay clear.
 local spots={}
 for _,sx in {-1,1} do for _,sz in {-1,1} do
  for _,x in {24,44,64} do for _,z in {24,46} do table.insert(spots,{sx*x,sz*z}) end end
 end end
 -- Area-specific variation never narrows the 14+ stud circulation corridors.
 local spawns={} local count=(id==1 and 30 or (id==2 or id==4) and 22 or 24)
 if count==30 then for _,q in {{-113,-104},{113,-104},{-110,43},{110,40},{-116,95},{116,95}} do table.insert(spots,q) end end
 for i=1,count do
  local q=spots[i] local x,z=q[1],q[2]
  if id==2 then z+=x<0 and -1 or 1 elseif id==3 then x+=z<0 and -1 or 1 elseif id==5 then z+=x<0 and 1.3 or -.7 end
  local foot=V(x,6.02,z)
  A.block('AfloramentoMineral',V(7.5,.04,7.5),foot,p.soil:Lerp(p.rock,.12),A.paths,CFrame.Angles(0,rng:NextNumber(-.35,.35),0),false)
  table.insert(spawns,{pos=c+V(x,6.1,z),variant=i%8==0 and 3 or i%4==0 and 2 or 1})
 end
 -- The boss has a spacious bay beside, rather than across, the main route.
 A.cylinder('AnelDoChefe',8,.08,V(-37,6.2,76),p.trim,A.paths,false)
 A.cylinder('PisoDoChefe',7.6,.08,V(-37,6.25,76),p.soil,A.paths,false)
 for _,x in {-48,-26} do A.lamp(V(x,6,81),.85) end
 return {spawns=spawns,boss=c+V(-37,6.32,76),returnPad=c+rp}
end
return M
