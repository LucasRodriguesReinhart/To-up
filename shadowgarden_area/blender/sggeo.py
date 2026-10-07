import bpy, math, random, os, json
from mathutils import Vector, Matrix
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P={
'stone':(155,167,186),'light':(199,209,218),'darkstone':(79,91,115),'rock':(58,69,91),'rocklight':(81,95,120),'rockdark':(38,49,69),
'roof':(30,40,69),'rooflight':(49,60,93),'iron':(29,32,48),'gold':(188,153,91),'wood':(66,48,61),'woodlight':(105,78,84),
'grass':(59,95,93),'grasslight':(85,123,113),'leaf':(41,89,83),'leaflight':(71,123,108),'leafdark':(27,64,65),'lilac':(120,100,155),
'floor':(118,126,148),'path':(173,180,194),'water':(29,116,149),'shallow':(51,152,174),'foam':(177,231,238),
'glow':(174,96,255),'core':(229,205,255),'amber':(246,192,116),'window':(61,99,135),'crystal':(99,57,157),'crystallight':(153,94,221),'black':(20,24,35)}
KEYS=list(P)
MAT={}
def init():
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
 for c in list(bpy.data.collections): bpy.data.collections.remove(c)
 for k,rgb in P.items():
  m=bpy.data.materials.new('SG_'+k);m.diffuse_color=tuple(v/255 for v in rgb)+(1,);m.use_nodes=True
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.8
  if k in ('glow','core','amber'):bs.inputs['Emission Color'].default_value=m.diffuse_color;bs.inputs['Emission Strength'].default_value=.6
  MAT[k]=m
def collection(name):
 c=bpy.data.collections.get(name)
 if not c:c=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(c)
 return c
class Geo:
 def __init__(self):self.v=[];self.f=[];self.k=[]
 def add(self,v,f,k):
  n=len(self.v);self.v.extend([tuple(p) for p in v]);self.f.extend([tuple(n+i for i in face) for face in f]);self.k.extend(k if isinstance(k,list) else [k]*len(f))
 def box(self,p,s,k,rz=0):
  c=math.cos(rz);a=math.sin(rz);v=[]
  for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]:
   x=x*s[0]/2;y=y*s[1]/2;v.append((p[0]+c*x-a*y,p[1]+a*x+c*y,p[2]+z*s[2]/2))
  self.add(v,[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],k)
 def loft(self,rings,k,caps=True):
  v=[p for r in rings for p in r];n=len(rings[0]);f=[]
  for j in range(len(rings)-1):
   for i in range(n):q=(i+1)%n;f.append((j*n+i,j*n+q,(j+1)*n+q,(j+1)*n+i))
  if caps:f.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))])
  self.add(v,f,k)
 def cyl(self,p,r,h,k,n=12,r2=None,phase=0):
  r2=r if r2 is None else r2
  self.loft([[(p[0]+rr*math.cos(2*math.pi*i/n+phase),p[1]+rr*math.sin(2*math.pi*i/n+phase),p[2]+z)for i in range(n)]for rr,z in [(r,0),(r2,h)]],k)
 def tube(self,points,radii,k,n=7):
  rings=[]
  for j,pp in enumerate(points):
   p=Vector(pp);dr=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
   dr.normalize();u=dr.cross(Vector((0,1,0)))
   if u.length<.01:u=dr.cross(Vector((1,0,0)))
   u.normalize();v=dr.cross(u).normalized();rings.append([p+radii[j]*(u*math.cos(i*2*math.pi/n)+v*math.sin(i*2*math.pi/n))for i in range(n)])
  self.loft(rings,k)
 def prism(self,poly,z0,z1,k):self.loft([[(x,y,z0)for x,y in poly],[(x,y,z1)for x,y in poly]],k)
 def roof(self,p,w,d,h,k='roof'):
  x,y,z=p
  self.add([(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z),(x,y-d/2,z+h),(x,y+d/2,z+h)],[(0,1,4),(3,5,2),(0,4,5,3),(1,2,5,4),(0,3,2,1)],k)
 def arch(self,p,w,h,t,depth,k='stone',n=12):
  x,y,z=p;r=w/2;spring=h-r
  self.box((x-r-t/2,y,z+spring/2),(t,depth,spring),k);self.box((x+r+t/2,y,z+spring/2),(t,depth,spring),k)
  v=[]
  for yy in [-depth/2,depth/2]:
   for rr in [r,r+t]:
    for i in range(n+1):a=i*math.pi/n;v.append((x+rr*math.cos(a),y+yy,z+spring+rr*math.sin(a)))
  f=[];N=n+1
  for i in range(n):
   f.extend([(i,i+1,N+i+1,N+i),(2*N+i,3*N+i,3*N+i+1,2*N+i+1),(i,2*N+i,2*N+i+1,i+1),(N+i,N+i+1,3*N+i+1,3*N+i)])
  f.extend([(0,N,3*N,2*N),(n,2*N+n,3*N+n,N+n)])
  self.add(v,f,k)
 def window(self,p,w,h):
  x,y,z=p;self.box((x,y+.15,z+h*.42),(w,.3,h*.84),'window')
  self.arch(p,w,h,.45,.7,'light',8);self.box((x,y-.24,z+h*.43),(.2,.25,h*.83),'gold')
  self.box((x,y-.25,z+h*.43),(w,.25,.16),'light');self.box((x,y,z-.1),(w+1.4,1.1,.5),'light')
 def merge(self,other,p=(0,0,0),rz=0,scale=1):
  c=math.cos(rz);s=math.sin(rz)
  self.add([(p[0]+scale*(c*x-s*y),p[1]+scale*(s*x+c*y),p[2]+scale*z)for x,y,z in other.v],other.f,other.k)
 def finish(self,name,col):
  me=bpy.data.meshes.new(name);me.from_pydata(self.v,[],self.f);me.update()
  for key in KEYS:me.materials.append(MAT[key])
  for face,k in zip(me.polygons,self.k):face.material_index=KEYS.index(k)
  ob=bpy.data.objects.new(name,me);collection(col).objects.link(ob);return ob

def outer(a):return 168+13*math.sin(3*a+.2)+9*math.cos(5*a)+5*math.sin(9*a)
def inner(a):return min(65/max(abs(math.cos(a)),.001),65/max(abs(math.sin(a)),.001))
def terrain_geo():
 g=Geo();N=64;S=9;rings=[]
 for j in range(S+1):
  t=j/S;ring=[]
  for i in range(N):
   a=2*math.pi*i/N;r=inner(a)+(outer(a)-inner(a))*t;x=r*math.cos(a);y=-5+(inner(a)*(1-t)+outer(a)*t*1.05)*math.sin(a)
   dd=((x-117)/30)**2+((y+40)/63)**2
   z=-4*max(0,min(1,(1.25-dd)*2))
   ring.append((x,y,z))
  rings.append(ring)
 for j in range(S):
  for i in range(N):n=(i+1)%N;g.add([rings[j][i],rings[j+1][i],rings[j+1][n],rings[j][n]],[(0,1,2),(0,2,3)],'grass' if j>0 else 'path')
 for i in range(N):n=(i+1)%N;p=rings[-1][i];q=rings[-1][n];g.add([p,(p[0]*.95,p[1]*.95,-17),(q[0]*.95,q[1]*.95,-17),q],[(0,1,2,3)],'rocklight');g.add([(p[0]*.95,p[1]*.95,-17),(p[0]*.76,p[1]*.76,-46),(q[0]*.76,q[1]*.76,-46),(q[0]*.95,q[1]*.95,-17)],[(0,1,2,3)],'rock')
 return g
def shot(name,eye,target,ortho=None):
 sc=bpy.context.scene
 cam=bpy.data.objects.get('ReviewCamera')
 if not cam:cam=bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'));sc.collection.objects.link(cam)
 cam.location=eye;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=26
 if ortho:cam.data.type='ORTHO';cam.data.ortho_scale=ortho
 else:cam.data.type='PERSP'
 cam.data.clip_start=1;cam.data.clip_end=1500
 sc.camera=cam;sc.render.engine='BLENDER_WORKBENCH';sc.display.shading.light='STUDIO';sc.display.shading.studiolight_rotate_z=.55;sc.display.shading.color_type='MATERIAL';sc.display.shading.show_shadows=False;sc.display.shading.show_cavity=True;sc.display.shading.cavity_type='BOTH';sc.display.shading.background_type='WORLD';sc.world.color=(.08,.11,.17)
 sc.render.resolution_x=1440;sc.render.resolution_y=1000;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.join(ROOT,'renders',name+'.png');bpy.ops.render.render(write_still=True)
