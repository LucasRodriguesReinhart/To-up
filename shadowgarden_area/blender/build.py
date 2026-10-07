import os,sys,json,math,bpy
sys.path.insert(0,os.path.dirname(__file__))
from sggeo import *
from sgkit import *
from sgmap import *
init();kit();layout()
export=collection('SHADOWGARDEN_KIT');export.hide_render=True
obs={};data={}
for n,g in KIT.items():
 ob=g.finish(n,'SHADOWGARDEN_KIT');obs[n]=ob
 # Triangulate in Blender, export actual authored triangles/colors to the Studio bridge.
 me=ob.data;me.calc_loop_triangles()
 verts=[[-round(v.co.x,4),round(v.co.z,4),round(v.co.y,4)]for v in me.vertices]
 faces=[[t.vertices[0]+1,t.vertices[1]+1,t.vertices[2]+1,t.material_index+1]for t in me.loop_triangles]
 data[n]={'v':verts,'f':faces}
 with open(os.path.join(ROOT,'export',n+'.json'),'w')as f:json.dump(data[n],f,separators=(',',':'))
for i,d in enumerate(INST):
 src=obs[d['asset']];o=src.copy();o.data=src.data;o.name=d['asset']+'_'+str(i);collection(d['category']).objects.link(o)
 o.location=d['p'];o.rotation_euler.z=d['rz'];o.scale=(d['s'],)*3
with open(os.path.join(ROOT,'export','manifest.json'),'w')as f:json.dump({'instances':INST,'colliders':COLL,'markers':MARK,'palette':list(P.values()),'assets':list(data)},f,separators=(',',':'))
with open(os.path.join(ROOT,'export','stats.json'),'w')as f:json.dump({'asset_count':len(data),'instances':len(INST),'colliders':len(COLL),'triangles_unique':sum(len(d['f'])for d in data.values()),'triangles_placed':sum(len(data[d['asset']]['f'])for d in INST),'largest':sorted([(n,len(d['f']))for n,d in data.items()],key=lambda p:-p[1])[:8]},f,indent=2)
# Kit FBX supplied as independent reusable source as well.
bpy.ops.object.select_all(action='DESELECT')
for o in obs.values():o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'export','shadowgarden_kit.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False)
shot('final_entry',(0,-178,8),(0,67,32));shot('final_overview',(335,-420,340),(0,9,13),455)
shot('final_quarry',(31,-66,3),(0,111,37));shot('final_water',(173,-113,20),(119,-26,5));shot('final_village',(-67,-120,9),(-117,6,20))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'shadowgarden_area.blend'))
print('SHADOW_BUILD',len(INST),len(COLL),len(MARK))
