import sys,os,math,bpy
sys.path.insert(0,os.path.dirname(__file__))
from sggeo import *
init();terrain_geo().finish('Ilha_anel','BLOCKOUT')
g=Geo();g.box((0,-5,-8),(130,130,4),'floor')
for x,y,w,d,h in [(-105,-40,25,35,22),(-114,22,30,34,29),(-78,-107,29,23,24),(9,113,65,35,45),(-28,110,17,17,65),(39,118,16,16,79)]:
 g.box((x,y,h/2),(w,d,h),'stone');g.roof((x,y,h),w+3,d+3,12)
for x,y,z,r,h in [(-135,103,0,27,62),(-85,140,0,29,82),(93,138,0,32,77),(144,100,0,20,61),(70,158,0,28,95)]:g.cyl((x,y,z),r,h,'rock',7,r*.55)
g.arch((101,70,0),32,52,8,18,'rocklight')
g.box((0,-127,.2),(22,65,.4),'path');g.box((0,90,10),(80,34,20),'darkstone')
for x,y,w,d in [(-76,-4,16,146),(76,-4,16,146),(0,-83,145,14),(0,73,150,14)]:g.box((x,y,.2),(w,d,.4),'path')
for y,sy in [(-60,-1),(50,1)]:
 g.add([(-12,y,-6),(12,y,-6),(12,y+sy*26,0),(-12,y+sy*26,0)],[(0,1,2,3)],'path')
g.cyl((116,-43,-2),26,.2,'water',40);g.finish('Massas','BLOCKOUT')
shot('blockout_entry',(0,-178,8),(0,48,30));shot('blockout_overview',(320,-390,325),(0,8,14),430)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'shadowgarden_blockout.blend'))
