-- Shared construction vocabulary. Original Plastic/Studs and imported foliage are preserved.
local Art={}
local V=Vector3.new
local C=Color3.fromRGB
local pi=math.pi
function Art.new(root,center,palette,seed)
 local A={root=root,center=center,pal=palette,rng=Random.new(seed)}
 function A.group(name,parent)
  local f=Instance.new('Model') f.Name=name f.Parent=parent or root return f
 end
 A.land=A.group('01_Relevo') A.buildings=A.group('02_Arquitetura') A.paths=A.group('03_Circulacao')
 A.plants=A.group('04_Vegetacao') A.props=A.group('05_Detalhes') A.water=A.group('06_AguaEVFX')
 function A.part(name,size,pos,color,parent,rotation,collide,material)
  local p=Instance.new('Part') p.Name=name p.Anchored=true p.Size=size
  p.CFrame=CFrame.new(center+pos)*(rotation or CFrame.identity) p.Color=color
  p.Material=material or Enum.Material.Plastic p.TopSurface=Enum.SurfaceType.Smooth p.BottomSurface=Enum.SurfaceType.Smooth
  p.CanCollide=collide==true p.CanQuery=p.CanCollide p.CanTouch=false p.CastShadow=size.Magnitude>2
  p.Parent=parent or A.props return p
 end
 function A.block(name,size,pos,color,parent,rotation,collide)
  local p=A.part(name,size,pos,color,parent,rotation,collide~=false) p.TopSurface=Enum.SurfaceType.Studs return p
 end
 function A.rod(name,a,b,width,color,parent,material)
  return A.part(name,V(width,width,(b-a).Magnitude),(a+b)/2,color,parent,CFrame.lookAt(a,b).Rotation,false,material)
 end
 function A.cylinder(name,r,h,pos,color,parent,collide,material)
  local p=A.part(name,V(h,r*2,r*2),pos,color,parent,CFrame.Angles(0,0,pi/2),collide,material) p.Shape=Enum.PartType.Cylinder return p
 end
 function A.ball(name,size,pos,col,parent)
  local p=A.part(name,size,pos,col,parent,nil,false) p.Shape=Enum.PartType.Ball return p
 end
 function A.sign(words,pos,w,h,parent,color)
  local p=A.part('Placa',V(w,h,.4),pos,color or palette.wood,parent or A.buildings,nil,false,Enum.Material.Wood)
  local g=game.StarterGui.InterfacesMundo.Templates.PlacaIlha:Clone()
  g.Name='SurfaceGui';g.Enabled=true;g.Adornee=p;g.Texto.Text=words;g.Parent=p
  return p,g
 end
 function A.fence(a,b,iron,parent)
  local color=iron and palette.trim or palette.wood local n=math.ceil((b-a).Magnitude/6)
  parent=parent or A.props
  for i=0,n do local q=a:Lerp(b,i/n)
   A.part('Mourao',V(.6,4,.6),q+V(0,2,0),color,parent,nil,true,iron and Enum.Material.Metal or Enum.Material.Wood)
   A.part('TampaMourao',V(.85,.25,.85),q+V(0,4,0),palette.trim,parent)
  end
  for _,h in {1.5,3.5} do A.rod('Travessa',a+V(0,h,0),b+V(0,h,0),.32,color,parent,Enum.Material.Wood) end
  -- One continuous collider avoids catching the avatar on individual rails.
  local barrier=A.part('GuardaCorpo',V(.5,4,(b-a).Magnitude),(a+b)/2+V(0,2,0),color,parent,CFrame.lookAt(a,b).Rotation,true)
  barrier.Transparency=1
 end
 function A.lamp(pos,scale,parent,color)
  scale=scale or 1 parent=parent or A.props color=color or palette.glow
  local m=A.group('Lanterna',parent)
  A.block('Base',V(1.4,.4,1.4)*scale,pos+V(0,.2,0)*scale,palette.trim,m)
  A.part('Poste',V(.35,4.4,.35)*scale,pos+V(0,2.5,0)*scale,palette.wood,m,nil,false,Enum.Material.Wood)
  local light=A.part('VidroLuminoso',V(.85,1.3,.85)*scale,pos+V(0,4.8,0)*scale,color,m,nil,false,Enum.Material.Neon)
  for _,x in {-.52,.52} do for _,z in {-.52,.52} do A.part('Armacão',V(.13,1.5,.13)*scale,pos+V(x,4.8,z)*scale,palette.trim,m) end end
  A.part('Tampa',V(1.45,.3,1.45)*scale,pos+V(0,5.55,0)*scale,palette.trim,m)
  local l=Instance.new('PointLight') l.Color=color l.Brightness=.45 l.Range=12*scale l.Shadows=false l.Parent=light
  return m
 end
 function A.emit(pos,color,rate,size,texture,velocity,parent)
  local p=A.part('EmissorAmbiente',V(1,1,1),pos,color,parent or A.water) p.Transparency=1
  local e=Instance.new('ParticleEmitter') e.Texture=texture or 'rbxasset://textures/particles/sparkles_main.dds'
  e.Color=ColorSequence.new(color) e.Rate=rate e.Lifetime=NumberRange.new(2,4)
  e.Speed=NumberRange.new(.3,1.3) e.SpreadAngle=Vector2.new(70,70) e.Acceleration=velocity or V(0,.1,0)
  e.Size=NumberSequence.new({NumberSequenceKeypoint.new(0,size*.4),NumberSequenceKeypoint.new(.4,size),NumberSequenceKeypoint.new(1,size*.2)})
  e.Transparency=NumberSequence.new({NumberSequenceKeypoint.new(0,1),NumberSequenceKeypoint.new(.2,.45),NumberSequenceKeypoint.new(.7,.65),NumberSequenceKeypoint.new(1,1)})
  e.LightEmission=.35 e:SetAttribute('FolhaAmbient',true) e.Parent=p return e
 end
 function A.tree(pos,scale,color,parent)
  local lobby=workspace:FindFirstChild('LobbyRenovado') local original=lobby and lobby:FindFirstChild('OriginalArt')
  local template=original and original:FindFirstChild('Arvore') if not template then return end
  local m=template:Clone() m.Name='ArvoreOriginal' m:ScaleTo(template:GetScale()*scale)
  local cf,size=m:GetBoundingBox() m:PivotTo(CFrame.new(center+pos+V(0,size.Y/2,0))*CFrame.Angles(0,A.rng:NextNumber(0,6.28),0)*cf:ToObjectSpace(m:GetPivot()))
  for _,p in m:GetDescendants() do if p:IsA('BasePart') then
   p.Anchored=true p.CanCollide=p.Name:lower():find('tronco')~=nil p.CanQuery=p.CanCollide p.CanTouch=false
   if color and p.Name:lower():find('folhagem') then p.Color=color:Lerp(C(190,203,159),A.rng:NextNumber(0,.08)) end
  end end
  m.Parent=parent or A.plants return m
 end
 function A.shrub(pos,size,color)
  for i=1,4 do
   local q=pos+V(math.sin(i*2.2)*size*.5,size*.4,math.cos(i*2.2)*size*.5)
   A.block('Arbusto',V(size,size*.8,size),q,color or palette.grass,A.plants,CFrame.Angles(.08,i*.7,.08),false)
  end
 end
 function A.tuft(pos,size,color)
  for i=1,3 do
   A.part('FolhaDoChao',V(.22,size,.7),pos+V((i-2)*.22,size*.38,0),color or palette.grass,A.plants,CFrame.Angles(0,i*1.8,(i-2)*.5))
  end
 end
 function A.rock(pos,size,color,parent)
  color=color or palette.rock parent=parent or A.land
  local m=A.group('RochedoFacetado',parent)
  A.block('Nucleo',size*V(.72,.77,.8),pos+V(0,size.Y*.37,0),color,m,CFrame.Angles(0,.21,0))
  for i=0,3 do
   local a=i*pi/2+.25 local p=Instance.new('WedgePart') p.Name='FaceTalhada' p.Anchored=true
   p.Size=size*V(.58,.9,.5) p.CFrame=CFrame.new(center+pos+V(math.sin(a)*size.X*.28,size.Y*.42,math.cos(a)*size.Z*.28))*CFrame.Angles(0,a,0)
   p.Color=color:Lerp(palette.soil,(i%3)*.07) p.Material=Enum.Material.Plastic p.TopSurface=Enum.SurfaceType.Studs
   p.CanTouch=false p.CanCollide=true p.CanQuery=true p.Parent=m
  end
  return m
 end
 function A.cliff(pos,w,d,h)
  local m=A.group('FalésiaEstratificada',A.land) local yaw=A.rng:NextNumber(-.3,.3)
  local col=palette.rock:Lerp(palette.soil,A.rng:NextNumber(.02,.14))
  A.block('Maciço',V(w,h,d),pos+V(0,h/2,0),col,m,CFrame.Angles(0,yaw,0))
  for i=0,3 do
   local layer=h*(.15+i*.22) local offset=(i%2==0 and -1 or 1)*w*.035
   A.block('EstratoExposto',V(w*1.025,1.2,d*1.04),pos+V(offset,layer,0),col:Lerp(palette.trim,.1+i*.025),m,CFrame.Angles(0,yaw,0))
  end
  A.block('CapaDeGrama',V(w+1,1,d+1),pos+V(0,h+.2,0),palette.grass,m,CFrame.Angles(0,yaw,0))
  for i=1,3 do
   local x=(i-2)*w*.28 local y=h*.35+i%2*h*.21
   A.rock(pos+V(x,0,-d*.43),V(w*.35,y+7,d*.3),col,m)
   A.block('BolsaDeMusgo',V(w*.27,.5,d*.23),pos+V(x,y*.7,-d*.53),palette.grass,m,CFrame.Angles(0,.17*i,0),false)
  end
  for i=1,7 do
   local x=A.rng:NextNumber(-w*.43,w*.43) local y=A.rng:NextNumber(3,h-3)
   A.part('FissuraVertical',V(.15,A.rng:NextNumber(2,6),.11),pos+V(x,y,-d*.505),col:Lerp(palette.trim,.27),m,CFrame.Angles(0,0,.07*i))
   if i%2==0 then A.block('FragmentoEstrato',V(w*.18,1.4,1.6),pos+V(x,y-2,-d*.51),col:Lerp(palette.soil,.17),m,CFrame.Angles(0,.12,0),false) end
  end
  local pivot=CFrame.new(center+pos)
  m:PivotTo(pivot*CFrame.Angles(0,math.atan2(pos.X,pos.Z),0)*pivot:Inverse()*m:GetPivot())
  if A.rng:NextNumber()<.72 then A.tree(pos+V(0,h+.7,0),.7,palette.foliage) end
  return m
 end
 function A.path(a,b,width,color,tiles)
  local delta=b-a local n=math.ceil(delta.Magnitude/(tiles and 5 or 9)) local right=V(-delta.Z,0,delta.X).Unit
  for i=1,n do
   local q=a:Lerp(b,(i-.5)/n) local c=(color or palette.path):Lerp(palette.soil,A.rng:NextNumber(0,.12))
   A.block('CaminhoNivelado',V(width,.14,delta.Magnitude/n+.04),q+V(0,.08,0),c,A.paths,CFrame.lookAt(a,b).Rotation,false)
   for _,side in {-1,1} do A.part('MeioFio',V(.28,.07,delta.Magnitude/n),q+right*side*(width/2+.18)+V(0,.11,0),(color or palette.path):Lerp(palette.rock,.15),A.paths,CFrame.lookAt(a,b).Rotation) end
  end
 end
 function A.bridge(a,b,width,stone)
  local m=A.group('Ponte',A.paths) local d=(b-a) local n=math.ceil(d.Magnitude/1.5) local right=V(-d.Z,0,d.X).Unit
  for i=0,n-1 do
   local t=(i+.5)/n local q=a:Lerp(b,t)+V(0,math.sin(t*pi)*.5,0)
   A.part('Tabua',V(width,.4,d.Magnitude/n+.03),q,stone and palette.path or palette.wood:Lerp(C(181,138,87),i%3*.1),m,CFrame.lookAt(a,b).Rotation,true,stone and Enum.Material.Plastic or Enum.Material.Wood)
  end
  for _,s in {-1,1} do A.fence(a+right*(width/2)*s,b+right*(width/2)*s,stone,m) end
  for _,s in {-1,1} do A.rod('Longarina',a+right*(width*.4)*s-V(0,.6,0),b+right*(width*.4)*s-V(0,.6,0),.9,palette.trim,m,Enum.Material.Wood) end
 end
 function A.waterfall(pos,h,w)
  local m=A.group('Cachoeira',A.water)
  for i=0,4 do
   local p=A.part('LaminaDagua',V(w/5+.12,h,1.5),pos+V((i-2)*w/5,h/2,0),palette.water:Lerp(C(166,218,230),i%2*.18),m)
   p.Transparency=.2
   local t=Instance.new('Texture') t.Name='FluxoCachoeira' t.Texture='rbxasset://textures/particles/water_main.dds' t.Face=Enum.NormalId.Front
   t.StudsPerTileU=6 t.StudsPerTileV=12 t.Transparency=.6 t.Parent=p
  end
  A.emit(pos+V(0,1,-2),palette.water:Lerp(C(235,245,252),.7),5,5,'rbxasset://textures/particles/smoke_main.dds',V(0,.3,0))
  A.rock(pos+V(-w*.75,-1,-2),V(6,4,5)) A.rock(pos+V(w*.75,-1,-1),V(7,5,5))
 end
 function A.waterSurface(pos,size)
  local p=A.part('Lago',size,pos,palette.water,A.water) p.Transparency=.23 p.Reflectance=.1
  for _,face in {Enum.NormalId.Top} do
   local t=Instance.new('Texture') t.Name='OndasDaIlha' t.Texture='rbxasset://textures/particles/water_main.dds' t.Face=face
   t.StudsPerTileU=18 t.StudsPerTileV=22 t.Transparency=.9 t.Parent=p
  end
  return p
 end
 function A.crate(pos,s)
  s=s or 1 local m=A.group('Caixote',A.props)
  A.part('Madeira',V(2.6,2.6,2.6)*s,pos+V(0,1.3,0)*s,palette.wood,m,nil,false,Enum.Material.Wood)
  for _,h in {.2,2.4} do A.part('Cinta',V(2.8,.22,2.8)*s,pos+V(0,h,0)*s,palette.trim,m) end
  for _,z in {-1.34,1.34} do A.rod('TravessaDiagonal',pos+V(-1,.3,z)*s,pos+V(1,2.3,z)*s,.2*s,C(171,130,79),m,Enum.Material.Wood) end
 end
 function A.barrel(pos,s)
  s=s or 1 A.cylinder('Barril',1.25*s,3*s,pos+V(0,1.5*s,0),palette.wood,A.props,false,Enum.Material.Wood)
  for _,y in {.35,2.65} do A.cylinder('AroBarril',1.3*s,.2*s,pos+V(0,y*s,0),palette.trim,A.props,false,Enum.Material.Metal) end
 end
 function A.bench(pos)
  for _,x in {-2.3,2.3} do A.part('PeBanco',V(.4,1.8,1.7),pos+V(x,.9,0),palette.trim) end
  for _,z in {-.6,0,.6} do A.part('Assento',V(6,.25,.52),pos+V(0,1.7,z),palette.wood,nil,nil,false,Enum.Material.Wood) end
  A.part('Encosto',V(6,1.1,.3),pos+V(0,2.7,.8),palette.wood,nil,nil,false,Enum.Material.Wood)
 end
 function A.roof(pos,w,d,h,color,parent)
  parent=parent or A.buildings
  for side=-1,1,2 do for row=0,5 do
   local z=side*(row+.5)*(d+5)/12 local y=h+3.5-row*.55
   for col=0,math.ceil(w/3)-1 do
    A.part('Telha',V(w/math.ceil(w/3)+.03,.38,(d+5)/12+.28),pos+V(-w/2+(col+.5)*w/math.ceil(w/3),y,z),color:Lerp(palette.trim,(col%3)*.035+row*.025),parent,CFrame.Angles(side*.22,0,0),false)
   end
  end end
  A.part('Cumeeira',V(w+1,.65,.7),pos+V(0,h+3.95,0),palette.trim,parent)
 end
 function A.house(pos,w,d,h,color,roof,label,style)
  local m=A.group(label or 'Casa',A.buildings)
  A.block('Fundacao',V(w+1.5,.65,d+1.5),pos+V(0,.3,0),palette.rock,m)
  A.part('Paredes',V(w,h,d),pos+V(0,h/2+.5,0),color,m,nil,true)
  for _,y in {1,h*.5,h+.3} do A.part('Friso',V(w+.3,.4,d+.3),pos+V(0,y,0),palette.wood,m) end
  for _,x in {-w/2+.1,w/2-.1} do A.part('Pilar',V(.5,h,.5),pos+V(x,h/2+.6,-d/2-.2),palette.wood,m) end
  for _,x in {-w*.31,w*.31} do
   A.part('MolduraJanela',V(w*.24,h*.42,.4),pos+V(x,h*.55,-d/2-.22),palette.trim,m)
   A.part('Vidro',V(w*.21,h*.36,.42),pos+V(x,h*.55,-d/2-.3),C(152,190,195):Lerp(palette.glow,.32),m)
   for j=-1,1 do A.part('Caixilho',V(.12,h*.37,.5),pos+V(x+j*w*.06,h*.55,-d/2-.32),palette.wood,m) end
   A.part('Peitoril',V(w*.27,.4,1),pos+V(x,h*.35,-d/2-.55),palette.wood,m)
  end
  A.part('PortalPorta',V(4.2,7,.35),pos+V(0,3.5,-d/2-.25),palette.wood,m)
  A.part('Porta',V(3.3,6.3,.4),pos+V(0,3.2,-d/2-.45),palette.trim,m)
  A.ball('Macaneta',V(.25,.25,.25),pos+V(1,3.2,-d/2-.75),C(201,166,83),m)
  A.roof(pos,w+4,d,h,color:Lerp(roof,.92),m)
  for _,x in {-w*.34,w*.34} do
   A.part('VigaSobBeiral',V(.35,1.5,d+3),pos+V(x,h-.5,0),palette.wood,m)
   for _,z in {-d*.48,d*.48} do A.rod('MaoFrancesa',pos+V(x,h-2,z),pos+V(x,h+.2,z-1.5),.3,palette.wood,m,Enum.Material.Wood) end
  end
  A.part('Calha',V(w+4,.3,.3),pos+V(0,h+.1,-d*.5-2.5),palette.trim,m)
  A.part('Chamine',V(2.5,5,2.5),pos+V(w*.25,h+4,d*.2),palette.rock,m)
  A.part('ChapeuChamine',V(3.1,.4,3.1),pos+V(w*.25,h+6.6,d*.2),palette.trim,m)
  A.emit(pos+V(w*.25,h+7,d*.2),C(192,184,168),.55,2,'rbxasset://textures/particles/smoke_main.dds',V(.2,.6,0),m)
  if label then A.sign(label,pos+V(0,h-1,-d/2-.7),math.min(w-3,20),2.5,m) end
  for _,x in {-w*.45,w*.45} do A.lamp(pos+V(x,.5,-d/2-1.4),.65,m) end
  if style=='village' then
   for i=-2,2 do A.part('ToldoListrado',V(w/5+.03,.25,4),pos+V(i*w/5,h*.48,-d/2-2),i%2==0 and roof or C(231,214,175),m,CFrame.Angles(.15,0,0)) end
   A.part('Balcao',V(w*.8,2.4,2),pos+V(0,1.2,-d/2-2),palette.wood,m,nil,false,Enum.Material.Wood)
   for i=-2,2 do A.ball('Tigela',V(1,.4,1),pos+V(i*1.8,2.55,-d/2-2),C(227,213,175),m) end
  end
  A.barrel(pos+V(w/2+2,0,-d/2+1)) A.crate(pos+V(-w/2-2,0,-d/2+1))
  return m
 end
 function A.torii(pos,w,h,color)
  local m=A.group('Torii',A.buildings) color=color or C(168,57,40)
  for _,x in {-w/2,w/2} do
   A.block('Sapata',V(3,.7,3),pos+V(x,.35,0),palette.trim,m)
   A.part('Coluna',V(1.3,h,1.3),pos+V(x,h/2,0),color,m,nil,true)
  end
  A.part('Trave',V(w+5,1.25,2),pos+V(0,h,0),palette.trim,m)
  A.part('Travessa',V(w+2,.65,1),pos+V(0,h-2.6,0),color,m)
  for _,x in {-w/2-1,w/2+1} do A.part('PontaCurva',V(4,.6,2),pos+V(x,h+.5,0),palette.trim,m,CFrame.Angles(0,0,x<0 and -.15 or .15)) end
  return m
 end
 return A
end
return Art
