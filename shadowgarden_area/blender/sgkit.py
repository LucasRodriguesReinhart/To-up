from sggeo import *
KIT={};CATS={}
def register(name,g,category):KIT[name]=g;CATS[name]='SHADOWGARDEN_'+category;return g
def cornice(g,w,d,z):
 g.box((0,0,z),(w+1.8,d+1.8,.7),'light');g.box((0,0,z+.65),(w+1,d+1,.65),'darkstone');g.box((0,0,z+.98),(w+1.2,d+1.2,.18),'gold')
def noble(w=22,d=19,h=18,style=0):
 g=Geo();g.box((0,0,h/2),(w,d,h),'stone');g.box((0,0,1),(w+1,d+1,2),'darkstone')
 for z in [2,h*.51,h]:cornice(g,w,d,z)
 for xx in [-w/2+.7,w/2-.7]:
  g.box((xx,-d/2-.2,h/2),(1.1,.85,h),'light')
  for zz in range(3,int(h),4):g.box((xx,-d/2-.45,zz),(1.8,1.1,.6),'light')
 for zz in [3,h*.55+1]:
  for xx in [-w*.30,w*.30]:g.window((xx,-d/2-.35,zz),3.8,h*.28)
 # door centered, recessed in porch
 g.box((0,-d/2-.2,3.4),(4.8,.6,6.8),'wood');g.arch((0,-d/2-.55,0),5,7,1,1,'light')
 g.cyl((1.4,-d/2-1,3),.17,.3,'gold',6)
 if style==1:
  g.box((0,-d/2-2,8.1),(10,4,1),'light')
  for x in [-4.6,4.6]:g.box((x,-d/2-3,10),(0.5,.5,3),'iron')
  g.box((0,-d/2-3,11.5),(10,.5,.5),'gold')
  for x in range(-4,5):g.box((x,-d/2-3,9.8),(.16,.18,3),'iron')
 if style==2:
  g.box((0,-d/2-1,7.8),(w*.72,1.2,2),'iron');g.box((0,-d/2-1.65,7.8),(w*.65,.14,.16),'gold')
  g.roof((0,-d/2-2.1,6.1),w*.78,4.2,1.3,'rooflight')
 g.roof((0,0,h+1.3),w+3,d+3,9 if style!=2 else 7)
 g.tube([(-w*.1,-d/2-1.5,h+10.3),(-w*.1,d/2+1.5,h+10.3)],[.25,.25],'gold',5)
 for xx in [-w*.28,w*.28]:
  g.box((xx,-d*.05,h+5),(3.2,3.8,3),'stone');g.roof((xx,-d*.05,h+6.5),4.4,5,2.6,'rooflight')
 g.box((w*.31,d*.26,h+6),(2.4,2.6,9),'darkstone');g.box((w*.31,d*.26,h+10.5),(3.1,3.2,.6),'light')
 return g
def tower(radius=6,h=32,point=18,square=False):
 g=Geo();n=4 if square else 8;phase=math.pi/4 if square else math.pi/8
 g.cyl((0,0,0),radius+1.2,2,'darkstone',n,phase=phase);g.cyl((0,0,2),radius,h-2,'stone',n,phase=phase)
 for z in [4,h*.45,h-3,h]:g.cyl((0,0,z),radius+.7,.7,'light',n,phase=phase)
 for a in range(4):
  q=Geo()
  for z in [h*.28,h*.64]:q.window((0,-radius*.92,z),2.4,6)
  g.merge(q,rz=a*math.pi/2)
 for i in range(8):
  a=i*math.pi/4;g.box(((radius+.3)*math.cos(a),(radius+.3)*math.sin(a),h-1.5),(1.1,1.1,3.7),'light',a)
 g.cyl((0,0,h+.5),radius+1.7,point,'roof',8,.4,phase)
 for t in [.05,.36,.68]:g.cyl((0,0,h+.5+point*t),(radius+1.7)*(1-t)+.4*t,.26,'rooflight',8,phase=phase)
 g.cyl((0,0,h+point+.5),.35,4,'gold',8,.05)
 return g
def ruin_arch():
 g=Geo();g.arch((0,0,0),12,17,2.2,3,'stone')
 for x in [-8,8]:
  g.box((x,0,.7),(4,4,1.4),'darkstone');g.box((x,0,15),(3.2,3.8,1),'light')
 g.box((-7,0,20),(4,3,4),'stone',.12)
 return g
def lantern():
 g=Geo();g.cyl((0,0,0),.85,.5,'darkstone',8);g.cyl((0,0,.5),.25,6.9,'iron',8)
 g.cyl((0,0,6.5),.55,.3,'gold',8);g.cyl((0,0,7),1.1,.6,'iron',4)
 g.box((0,0,8.1),(1.35,1.35,1.9),'amber')
 for x in [-.8,.8]:
  for y in [-.8,.8]:g.box((x,y,8.1),(.16,.16,2.3),'iron')
 g.cyl((0,0,9.3),1.4,1,'roof',4,.1);g.cyl((0,0,10.3),.12,.8,'gold',6)
 return g
def spire(seed=1,h=48,r=15):
 rng=random.Random(seed);g=Geo();n=11;rings=[];variation=[rng.uniform(.79,1.21)for i in range(n)]
 for j,t in enumerate([0,.07,.23,.29,.47,.54,.72,.78,1]):
  rr=r*(1-t*.42)*(1.1 if j in [1,3,5,7] else 1);dx=h*.16*t;dy=h*.07*t
  rings.append([(dx+math.cos(i*2*math.pi/n)*rr*variation[i],dy+math.sin(i*2*math.pi/n)*rr*variation[i],h*t+(rng.uniform(-1.5,1.5)if j else 0))for i in range(n)])
 g.loft(rings,'rock');g.k=[['rock','rocklight','rockdark'][((i//n)%3)]for i in range(len(g.f))]
 return g
def rock(seed=1,r=5,h=5):
 g=spire(seed,h,r);return g
def tree(seed=1,h=22,spread=12):
 rng=random.Random(seed);g=Geo();bend=rng.uniform(-2,2)
 g.tube([(0,0,0),(-.8,.2,h*.24),(bend,1,h*.55),(bend-1,1.4,h*.83)], [1.5,1.12,.7,.12],'wood',9)
 for j in range(6):
  a=j*math.pi/3+.24;g.tube([(0,0,1.7),(math.cos(a)*2,math.sin(a)*2,.4),(math.cos(a)*4,math.sin(a)*4,.02)],[.75,.55,.08],'wood',6)
 # overlapping asymmetrical, pointed leaf sprays, not spheres
 for j in range(10):
  a=j*2.399;rr=spread*(.48 if j<6 else .28);z=h*(.52+j*.037);cx=bend+rr*math.cos(a);cy=1+rr*math.sin(a)
  g.tube([(bend*.4,.4,h*.35),(cx*.5,cy*.5,z-3),(cx,cy,z)], [.56,.32,.04],'wood',6)
  rad=spread*.32*rng.uniform(.9,1.2);n=13;variation=[rng.uniform(.8,1.17)for _ in range(n)];rings=[]
  for layer,(rr,zz)in enumerate([(.35,-1.5),(.88,-.7),(1,0),(.84,1.4),(.46,2.5),(.12,2.9)]):
   rings.append([(cx+math.cos(i*2*math.pi/n)*rad*rr*variation[i],cy+math.sin(i*2*math.pi/n)*rad*rr*variation[i],z+zz+rng.uniform(-.28,.28))for i in range(n)])
  q=Geo();q.loft(rings,'leaf');q.k=[('leaflight'if i//n>=3 else 'leafdark'if i//n==0 else 'leaf')for i in range(len(q.f))];g.merge(q)
  # a few small leaf tips break the contour instead of a stack of cones
  for jj in range(4):
   a=jj*1.57+j;xx=cx+math.cos(a)*rad;yy=cy+math.sin(a)*rad
   g.add([(xx-.65,yy,z),(xx+.65,yy,z+.1),(xx+math.cos(a)*1.4,yy+math.sin(a)*1.4,z+.55)],[(0,1,2)],'leaflight')
 return g
def shrub(seed=63):
 rng=random.Random(seed);g=Geo();n=9
 for j,(cx,cy,z,r) in enumerate([(-1.7,0,1.5,2.7),(1.5,.4,1.65,2.4),(0,-1.1,2,2.5)]):
  variation=[rng.uniform(.82,1.18) for _ in range(n)];rings=[]
  for rr,zz in [(.5,-1.4),(1,-.35),(.83,.8),(.2,1.45)]:
   rings.append([(cx+math.cos(i*2*math.pi/n)*r*rr*variation[i],cy+math.sin(i*2*math.pi/n)*r*rr*variation[i],z+zz+rng.uniform(-.18,.18))for i in range(n)])
  q=Geo();q.loft(rings,'leaf');q.k=[('leaflight'if i//n>=2 else 'leafdark'if i//n==0 else 'leaf')for i in range(len(q.f))];g.merge(q)
 return g

def crystal(seed=1,h=7,r=2):
 rng=random.Random(seed);g=Geo()
 for j in range(5):
  a=j*2.4;rr=0 if j==0 else r*1.6;hh=h if j==0 else h*rng.uniform(.35,.7);p=(rr*math.cos(a),rr*math.sin(a),.1)
  q=Geo();q.cyl(p,r*(.65 if j else 1),hh*.7,'crystal',5,r*(.58 if j else .85));q.cyl((p[0],p[1],hh*.7),r*(.58 if j else .85),hh*.3,'crystallight',5,.03);g.merge(q)
 return g
def kit():
 for n,w,d,h,s in [('Casa_Nobre',22,20,19,0),('Casa_Sacada',24,22,25,1),('Comercio_Discreto',27,19,18,2),('Mansao',32,25,28,1),('Arquivo',27,26,32,0)]:register(n,noble(w,d,h,s),'BUILDINGS')
 for n,r,h,p,s in [('Torre_Octogonal',6,31,17,False),('Torre_Comando',8,65,23,True),('Torre_Alta',6.2,75,23,False),('Pinaculo',3.1,22,14,False)]:register(n,tower(r,h,p,s),'LANDMARKS')
 g=Geo();g.box((0,0,20),(55,29,40),'stone')
 for z in [1.5,6,24,40]:cornice(g,55,29,z)
 for x in [-23,-15,-7,1,9,17,25]:g.window((x,-15,12),4.3,17)
 g.arch((0,-17,0),12,11,1.4,4,'light');g.box((0,-15.2,5),(10,.5,10),'wood')
 g.roof((0,0,41.5),59,33,19);g.tube([(0,-17,61),(0,17,61)],[.35,.35],'gold',6)
 for x in [-28,28]:
  for y in [-12,12]:g.box((x,y,18),(2.5,4,36),'light')
 register('Salao_Sete_Sombras',g,'LANDMARKS')
 # Cloak-shaped black-and-gold crest: understated identity over the seven lancets.
 g=Geo();g.add([(-4,0,0),(4,0,0),(2.6,0,7),(0,0,9),(-2.6,0,7)],[(0,1,2,3,4)],'roof')
 for a,b in [((-4,-.1,0),(0,-.1,9)),((0,-.1,9),(4,-.1,0)),((-2,-.12,3),(2,-.12,3))]:g.tube([a,b],[.17,.17],'gold',5)
 g.cyl((0,0,9),.35,.7,'glow',6,.05);register('Brasao_Veu',g,'DECORATION')
 g=Geo()
 for r,k,w in [(5.8,'gold',.32),(5.25,'roof',.38),(4.8,'glow',.12)]:
  pts=[(r*math.cos(i*math.pi/24),0,r*math.sin(i*math.pi/24))for i in range(49)];g.tube(pts,[w]*49,k,5)
 for i in range(12):
  a=i*math.pi/6;g.tube([(4.1*math.cos(a),-.1,4.1*math.sin(a)),(4.55*math.cos(a),-.1,4.55*math.sin(a))],[.15,.15],'light',5)
 g.tube([(0,-.2,0),(-2.4,-.2,2.6)],[.22,.09],'gold',5);g.tube([(0,-.2,0),(3.2,-.2,1.5)],[.16,.08],'light',5)
 register('Relogio_Arcano',g,'DECORATION')
 g=Geo()
 for x in [-28,-14,0,14,28]:g.arch((x,0,0),11,13,2.1,14,'darkstone')
 g.box((0,0,15),(76,17,2),'light');g.box((0,-8.8,15.7),(77,.6,.35),'gold')
 register('Galeria_Mina',g,'MINING')
 register('Ruina_Arco',ruin_arch(),'RUINS')
 g=Geo();g.arch((0,0,0),14,23,2,3,'stone');g.roof((0,0,25),22,5,12)
 for x in [-10,10]:g.merge(tower(2.2,24,8),p=(x,0,0))
 register('Capela_Ruina',g,'RUINS')
 g=Geo()
 for x in [-5,5]:g.box((x,0,2),(1,2,4),'darkstone')
 g.box((0,0,4),(12,1,.65),'light')
 for x in range(-4,5,2):g.box((x,0,2.6),(.26,.35,2.6),'iron')
 register('Parapeito',g,'PROPS')
 register('Lanterna',lantern(),'PROPS')
 g=Geo();g.box((0,0,1.8),(7,2.5,.45),'woodlight');g.box((0,1.2,3),(7,.45,2.5),'wood')
 for x in [-2.5,2.5]:g.box((x,0,.8),(.6,2,1.6),'iron')
 register('Banco',g,'PROPS')
 g=Geo();g.box((0,0,1.5),(3,3,3),'woodlight')
 for z in [.3,2.7]:g.box((0,0,z),(3.1,3.1,.25),'iron')
 register('Caixa',g,'PROPS')
 g=Geo();g.cyl((0,0,0),1.6,3.7,'wood',12)
 for z in [.3,1.8,3.4]:g.cyl((0,0,z),1.67,.23,'iron',12)
 register('Barril',g,'PROPS')
 g=Geo();g.box((0,0,3),(5,1.3,6),'wood')
 for z in [0,1.5,3,4.5,6]:g.box((0,-.7,z),(5,1.7,.22),'gold' if z==6 else 'woodlight')
 for i in range(22):g.box((-2+(i%6)*.75,-.78,.72+(i//6)*1.5),(.5,.5,1.15),['roof','lilac','darkstone'][i%3])
 register('Estante',g,'PROPS')
 g=Geo();g.cyl((0,0,0),.25,12,'iron',8);g.box((2,0,9.1),(4,.2,5),'roof')
 for x in [.2,3.8]:g.box((x,-.15,9.1),(.13,.1,5),'gold')
 g.cyl((0,0,12),.5,1.4,'gold',8,.02);register('Estandarte',g,'DECORATION')
 for i,h,r in [(1,44,15),(2,66,18),(3,30,12)]:register('Falesia_'+str(i),spire(i*8,h,r),'ROCKS')
 for i,h,r in [(1,4,4),(2,7,6),(3,10,9)]:register('Rocha_'+str(i),rock(i*15,r,h),'ROCKS')
 g=Geo()
 for i in range(15):
  a=math.pi*i/14;x=23*math.cos(a);z=25+24*math.sin(a);q=rock(i+54,5.4,7);g.merge(q,p=(x,0,z-3),rz=a*.23)
 g.merge(spire(5,32,8),p=(-23,0,0));g.merge(spire(6,30,8),p=(23,0,0));register('Arco_Basalto',g,'ROCKS')
 for i,h,sp in [(1,22,12),(2,27,14),(3,18,10)]:register('Arvore_'+str(i),tree(i*7,h,sp),'NATURE')
 g=tree(37,34,7);register('Cipreste',g,'NATURE')
 g=Geo();rng=random.Random(54)
 for i in range(15):
  a=i*2.4;r=rng.uniform(0,3);x=r*math.cos(a);y=r*math.sin(a)
  g.add([(x-1,y,0),(x+1,y,.1),(x+.5,y,2.1),(x,y-.8,0),(x,y+.9,0),(x,y+.2,1.8)],[(0,1,2),(3,4,5)],'grasslight')
 register('Grama',g,'NATURE')
 register('Arbusto',shrub(),'NATURE')
 for i in range(1,6):
  g=rock(i+50,3.5+i*.35,2.2+i*.3);g.merge(crystal(i,3+i*1.2,.7+i*.13),p=(0,0,1))
  if i>=4:
   for j in range(i):g.merge(crystal(j+20,1.6,.35),p=(math.cos(j*2.4)*5,math.sin(j*2.4)*5,3+j*.6))
  register('Minerio_'+str(i),g,'MINING')
 register('Veio_Arcano',crystal(3,8,1.6),'MINING')
 g=Geo();g.arch((0,0,0),15,17,2,6,'darkstone')
 for x in [-9,9]:g.box((x,-2,6),(1,.5,10),'glow');g.box((x,-2.4,3),(1.8,.5,.4),'gold')
 register('Entrada_Mina',g,'MINING')
 g=Geo();g.box((0,0,2),(5,7,3),'wood');g.box((0,0,3.6),(5.5,7.5,.5),'iron')
 for x in [-2.7,2.7]:
  for y in [-2,2]:g.tube([(x-.3,y,1),(x+.3,y,1)],[1,1],'iron',10)
 register('Vagoneta',g,'MINING')
 g=Geo()
 for x in [-4,4]:g.box((x,0,6),(1.2,1.5,12),'wood')
 g.box((0,0,12),(11,1.5,1.5),'woodlight');g.tube([(0,-.8,12),(0,-.8,3)],[.12,.12],'iron',6)
 register('Guincho',g,'MINING')
 g=Geo();g.cyl((0,0,0),11,1.2,'darkstone',24);g.cyl((0,0,1.2),9.5,.35,'gold',24)
 g.cyl((0,0,1.55),9,.25,'roof',24)
 for x in [-10,10]:g.merge(tower(1.8,16,7),p=(x,0,0))
 g.arch((0,0,1.8),13,17,1.2,2,'light');g.arch((0,-1.1,1.8),12.5,16.5,.3,.2,'glow')
 register('Portal_Sombrio',g,'LANDMARKS')
 # editable architectural submodules
 g=Geo();g.window((0,0,0),4,9);register('Janela_Lanceta',g,'BUILDINGS')
 g=Geo();g.arch((0,0,0),8,12,1.4,3,'light');register('Arco_Modular',g,'BUILDINGS')
 g=Geo();g.cyl((0,0,0),1.8,.8,'darkstone',8);g.cyl((0,0,.8),1,11,'stone',10);g.cyl((0,0,11.8),1.7,.7,'light',8);register('Coluna',g,'BUILDINGS')
 return KIT
