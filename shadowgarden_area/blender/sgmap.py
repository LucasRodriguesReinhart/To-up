from sggeo import *
from sgkit import *
INST=[];COLL=[];MARK=[]
def put(n,p=(0,0,0),rz=0,s=1,category=None):
 INST.append(dict(asset=n,p=list(p),rz=rz,s=s,category=category or CATS.get(n,'SHADOWGARDEN_TERRAIN')))
def collider(p,s,rz=0,shape='Block',name='Piso'):
 COLL.append(dict(p=list(p),s=list(s),rz=rz,shape=shape,name=name))
def unique(n,g,cat='TERRAIN'):register(n,g,cat);put(n)
def ramp(a,b,w):
 a=Vector(a);b=Vector(b);d=b-a;side=Vector((d.y,-d.x,0)).normalized()*w/2
 g=Geo();g.add([a-side,a+side,b+side,b-side],[(0,1,2,3)],'path');return g
def road(points,w=10,key='path'):
 g=Geo()
 for a,b in zip(points,points[1:]):
  aa=Vector(a);bb=Vector(b);side=Vector((bb.y-aa.y,aa.x-bb.x,0)).normalized()*w/2
  g.add([aa-side,aa+side,bb+side,bb-side],[(0,1,2,3)],key)
 return g
def layout():
 unique('Ilha_Base',terrain_geo())
 # four clipped corners give the quarry a cut-rock outline while retaining a large level floor
 poly=[(-57,-70),(57,-70),(65,-62),(65,51),(57,60),(-57,60),(-65,51),(-65,-62)]
 g=Geo();g.prism(poly,-12,-6,'floor');unique('Pedreira_Piso',g)
 collider((0,-5,-9),(114,130,6));collider((0,-5,-9),(130,112,6))
 # Ground collision rows: only the terrain actually present, hole preserved.
 for yi in range(-180,183,5):
  run=None
  for xi in range(-190,196,5):
   a=math.atan2((yi+5)/1.05,xi);r=math.hypot(xi,(yi+5)/1.05)
   dd=((xi-117)/30)**2+((yi+40)/63)**2
   valid=r<outer(a)-2 and (abs(xi)>67 or yi<-72 or yi>62)
   z=-4*max(0,min(1,(1.25-dd)*2))
   # central ramp approach reserves clearance
   if valid and run is None:run=(xi,z)
   if run is not None and (not valid or abs(z-run[1])>.8 or xi==195):
    length=xi-run[0]
    if length>0:collider((run[0]+length/2-2.5,yi,run[1]-2),(length,5.02,4))
    run=(xi,z)if valid else None
 g=Geo()
 # walls stop at cardinal ramps; wall stripes are in one mesh
 for y in [-70,60]:
  for xa,xb in [(-63,-13),(13,63)]:
   for z,h,k in [(-4.7,2.6,'rockdark'),(-2.5,1.8,'rocklight'),(-.8,1.6,'rock')]:g.box(((xa+xb)/2,y,z),(xb-xa,2,h),k)
 for x in [-65,65]:
  for ya,yb in [(-68,-17),(7,59)]:
   for z,h,k in [(-4.7,2.6,'rockdark'),(-2.5,1.8,'rocklight'),(-.8,1.6,'rock')]:g.box((x,(ya+yb)/2,z),(2,yb-ya,h),k)
 unique('Cortes_Pedreira',g,'MINING')
 g=Geo()
 for a,b,w in [((0,-50,-5.98),(0,-76,0),24),((0,40,-5.98),(0,67,0),24),((-48,-5,-5.98),(-72,-5,0),22),((48,-5,-5.98),(72,-5,0),22)]:
  g.merge(ramp(a,b,w));d=Vector(b)-Vector(a);L=math.hypot(d.x,d.y);rz=math.atan2(-d.x,d.y)
  collider(((a[0]+b[0])/2,(a[1]+b[1])/2,-3),(w,L,6),rz,'Wedge','Rampa')
 unique('Rampas_Pedreira',g)
 paths=[[(0,-177,.12),(0,-137,.12),(0,-84,.12)], [(-75,-84,.12),(-76,-5,.12),(-74,71,.12),(0,73,.12),(76,72,.12),(76,-84,.12),(-75,-84,.12)], [(-76,-88,.12),(-104,-91,.12),(-115,-60,.12),(-112,-10,.12),(-104,42,.12),(-77,64,.12)],[(76,29,.12),(103,28,.12),(132,51,.12),(134,74,.12)],[(0,68,.12),(0,91,.12),(0,139,.12)]]
 g=Geo()
 for pts in paths:g.merge(road(pts,12))
 unique('Caminhos',g)
 # Castle deck. The five-arch gallery supports it; mine passes through the middle.
 put('Galeria_Mina',(0,87,0));put('Salao_Sete_Sombras',(3,124,16));put('Torre_Comando',(-32,122,16));put('Torre_Alta',(37,125,16))
 put('Brasao_Veu',(3,108.6,46))
 put('Relogio_Arcano',(-32,116,67))
 for x,y in [(-42,99),(44,103),(-16,139),(20,143)]:put('Pinaculo',(x,y,16))
 g=Geo();g.box((0,119,15),(95,72,2),'darkstone');g.box((0,119,16.12),(93,70,.22),'path')
 unique('Patio_Cidadela',g);collider((0,119,15),(95,72,2),name='PatioSuperior')
 # Main gallery passage remains clear; solid retaining sides below terrace.
 for x in [-35,35]:collider((x,120,6),(23,57,12),name='FundacaoCastelo')
 g=Geo()
 for x in [-57,57]:
  g.merge(ramp((x,65,.14),(x,103,16.14),15));collider((x,84,8),(15,38,16),0,'Wedge','RampaCastelo')
 g.merge(road([(-57,106.5,16.14),(57,106.5,16.14)],7));unique('Acessos_Cidadela',g);collider((0,106.5,15),(129,7,2),name='PatamarCastelo')
 # Noble quarter; turn facades toward circulation.
 for n,p,rz in [('Casa_Nobre',(-95,-111,0),-.18),('Comercio_Discreto',(-118,-74,0),math.pi/2),('Casa_Sacada',(-131,-27,0),math.pi/2),('Mansao',(-113,27,0),math.pi/2),('Arquivo',(-75,110,0),0)]:put(n,p,rz)
 put('Capela_Ruina',(112,-108,0),-.4);put('Ruina_Arco',(145,-87,0),-.5);put('Ruina_Arco',(-118,73,0),.5)
 put('Entrada_Mina',(0,100,0));put('Entrada_Mina',(-91,100,0),.25);put('Arco_Basalto',(103,89,0),-.18)
 # Tunnel / crypt walls on either side; ceiling sufficient headroom, floor flat.
 g=Geo();g.box((0,128,-1),(23,60,2),'floor');g.box((-12,127,6),(2,56,12),'rock');g.box((12,127,6),(2,56,12),'rock');g.box((0,128,13),(26,57,2),'rockdark')
 for y in [108,126,145]:g.arch((0,y,0),20,11,1.2,2,'darkstone')
 g.box((-90,123,-1),(25,32,2),'floor');g.box((-104,123,6),(2,32,12),'rock');g.box((-77,124,6),(2,32,12),'rock');g.box((-90,141,6),(28,2,12),'rock');g.box((-90,124,13),(30,36,2),'rockdark')
 unique('Mina_e_Cripta',g,'MINING');collider((0,127,-1),(24,60,2));collider((-90,124,-1),(28,38,2))
 for x in [-12,12]:collider((x,129,6),(2,54,12),name='ParedeMina')
 for y in [104,121,144]:put('Veio_Arcano',(-10,y,1),.2,.55);put('Veio_Arcano',(10,y+6,1),-.3,.5)
 for x,y in [(-102,118),(-78,132),(-100,136)]:put('Veio_Arcano',(x,y,0),s=.6)
 # Outcrops form a crescent background, leaving both access ramps open.
 for n,x,y,s,rz in [(2,-137,111,1.08,-.2),(1,-119,143,1.2,.5),(2,-70,158,1.1,-.4),(1,-30,164,1.1,1),(2,63,152,1.3,-.7),(1,101,147,1.3,0),(2,146,116,.85,.6),(3,162,82,.75,.2)]:put('Falesia_'+str(n),(x,y,-4),rz,s)
 for i in range(22):
  a=i*2*math.pi/22;r=outer(a)-1;x=r*math.cos(a);y=-5+r*math.sin(a)*1.05
  if abs(x)<23 and y<-135:continue
  put('Rocha_'+str(i%3+1),(x,y,-9),a,.85+(i%4)*.19)
 # elongated lake, blended shallow-to-deep colored rings
 g=Geo();N=56;center=(117,-40);rings=[]
 for t in [0,.66,.88,1]:
  rings.append([(center[0]+26*t*math.cos(i*2*math.pi/N),center[1]+56*t*math.sin(i*2*math.pi/N),-1.9+.015*t)for i in range(N)])
 for j in range(3):
  for i in range(N):nn=(i+1)%N;g.add([rings[j][i],rings[j+1][i],rings[j+1][nn],rings[j][nn]],[(0,1,2,3)],'water' if j<1 else 'shallow')
 unique('Lago',g)
 # Stylized broken ripples modeled in geometry, one mesh, no unavailable texture IDs.
 g=Geo();rng=random.Random(203)
 for i in range(53):
  x=rng.uniform(95,139);y=rng.uniform(-90,10)
  if ((x-117)/23)**2+((y+40)/51)**2>.95:continue
  pts=[(x+j*.9,y+math.sin(j*.8+i)*.5,-1.81)for j in range(rng.randint(3,7))]
  g.merge(road(pts,.14,'foam'))
 unique('Ondas_Lago',g)
 # Stone bridge crosses the water east-west, arched ribs below deck.
 g=Geo();g.box((117,-52,.1),(70,12,1.1),'path')
 for y in [-58, -46]:
  for x in range(86,151,5):g.box((x,y,1.9),(.7,.7,3.2),'darkstone')
  g.box((117,y,3.5),(71,.8,.6),'light')
 unique('Ponte_Lago',g,'BUILDINGS');collider((117,-52,.1),(70,12,1.1),name='Ponte')
 # waterfall: curved ribbons from elevated basin, not vertical blocks
 g=Geo();g.prism([(119,11),(140,11),(141,25),(119,27)],-1,7,'rock');g.prism([(122,14),(137,14),(137,24),(122,24)],7,7.12,'water')
 unique('Nascente',g);put('Rocha_2',(141,18,0));put('Rocha_2',(117,20,0))
 g=Geo()
 for j in range(7):
  for i in range(20):
   t=i/19;y=14-13*t;z=7.1-9*t*t;x=122+j*1.9+math.sin(t*3+j)*.18;w=.82+.16*t
   if i:g.add([(px-pw,py,pz),(px+pw,py,pz),(x+w,y,z),(x-w,y,z)],[(0,1,2,3)],'shallow'if j%3 else 'foam')
   px,py,pz,pw=x,y,z,w
 unique('Cachoeira_Lamina',g)
 # Trees in intentional foreground, streets and backdrop groups.
 sites=[(-24,-151,1), (33,-146,.9),(-57,-142,.95),(64,-123,1.15),(-142,-101,1.1),(-147,-55,1.1),(-145,1,.9),(-134,56,1.1),(-58,67,.8),(79,-116,.75),(152,-110,.95),(158,-43,1.1),(154,12,1),(89,29,.8),(161,56,.8),(-141,86,.8),(-94,148,.8)]
 for i,(x,y,s) in enumerate(sites):put('Arvore_'+str(i%3+1),(x,y,0),i*1.73,s)
 for x,y in [(-42,-142),(46,-140),(-122,98),(-53,125),(75,120),(135,51)]:put('Cipreste',(x,y,0),.3,.8)
 for i,(x,y,s) in enumerate(sites):
  put('Arbusto',(x+4,y+2,0),i,s*.7);put('Grama',(x-4,y-2,0),i,1.2)
 # Patio parterre, trimmed beds away from quarry.
 for x,y in [(-88,-83),(-82,31),(-139,34),(37,-113),(46,-107),(-36,-112),(81,85),(80,112)]:put('Arbusto',(x,y,0),.4,.8)
 for i,(x,y) in enumerate([(-15,-153),(15,-139),(-14,-112),(15,-86),(-76,-61),(-76,24),(-74,60),(74,53),(76,-35),(74,-81),(-111,-96),(-112,2),(-75,104),(0,94),(0,135),(134,46),(143,-48),(-90,115)]):put('Lanterna',(x,y,0))
 for x,y in [(-82,-103),(-112,-10),(31,-117),(84,7)]:put('Banco',(x,y,0),.3)
 for x,y in [(-15,80),(16,80),(-21,-142),(22,-142)]:put('Estandarte',(x,y,0))
 for x,y in [(-53,61),(51,55)]:put('Guincho',(x,y,0));put('Vagoneta',(x-5,y+10,0),.3)
 for x,y in [(-123,-62),(-121,-60),(-81,111)]:put('Caixa',(x,y,0))
 put('Barril',(-123,-55,0));put('Estante',(-90,138,0));put('Portal_Sombrio',(137,60,0),-.5)
 # fewer perimeter rails, all one mesh per repeated segment
 for y in [-74,64]:
  for x in [-55,-41,-27,27,41,55]:put('Parapeito',(x,y,0))
 for x in [-69,69]:
  for y in [-57,-43,-29,21,35,49]:put('Parapeito',(x,y,0),math.pi/2)
 for x in [-10,10]:put('Torre_Octogonal',(x*3,-158,0),s=.52)
 # authored ore points with clearance around ramps
 for y in range(-51,49,13):
  for x in range(-51,53,13):
   if abs(x)<15 and (y<-40 or y>32):continue
   if abs(y+5)<16 and abs(x)>39:continue
   MARK.append(dict(kind='ore',p=[x,y,-6],zone='Pedreira'))
 for x,y in [(0,111),(0,126),(0,141),(-91,114),(-91,129),(112,96),(125,95)]:MARK.append(dict(kind='ore',p=[x,y,0],zone='Mina'))
 MARK.extend([dict(kind='entry',p=[0,-167,3.7]),dict(kind='safe',p=[0,-153,3.7]),dict(kind='return',p=[15,-160,.3]),dict(kind='next',p=[137,60,1.8]),dict(kind='boss',p=[0,-7,-6])])
 return INST,COLL,MARK
