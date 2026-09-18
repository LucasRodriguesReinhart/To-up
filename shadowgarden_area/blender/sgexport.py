import bpy,sys,os,math
sys.path.insert(0,os.path.dirname(__file__))
from sggeo import ROOT,P,KEYS
def linear(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
exp=bpy.data.collections.new('SHADOWGARDEN_EXPORT');bpy.context.scene.collection.children.link(exp)
img=bpy.data.images.new('SG_Palette',128,64,alpha=False)
pixels=[0.0]*(128*64*4)
for i,k in enumerate(KEYS):
 rgb=P[k];col=[linear(v/255)for v in rgb]+[1]
 for yy in range(16):
  for xx in range(16):
   p=((63-(i//8*16+yy))*128+i%8*16+xx)*4;pixels[p:p+4]=col
img.pixels=pixels;img.filepath_raw=os.path.join(ROOT,'export','SG_Palette.png');img.file_format='PNG';img.save()
mat=bpy.data.materials.new('SG_Palette');mat.use_nodes=True;nt=mat.node_tree;tex=nt.nodes.new('ShaderNodeTexImage');tex.image=img;tex.interpolation='Closest';bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)or nt.nodes.new('ShaderNodeBsdfPrincipled');out=next((n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'),None)or nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);bs.inputs['Roughness'].default_value=.82
for src in list(bpy.data.collections['SHADOWGARDEN_KIT'].objects):
 if src.type!='MESH':continue
 root=bpy.data.objects.new('K_'+src.name,None);exp.objects.link(root)
 o=src.copy();o.data=src.data.copy();o.name=src.name+'__pal';o.parent=root;exp.objects.link(o)
 uv=o.data.uv_layers.new(name='UVMap')
 for face in o.data.polygons:
  idx=face.material_index;coord=((idx%8+.5)/8,1-(idx//8+.5)/4)
  for li in face.loop_indices:uv.data[li].uv=coord
  face.material_index=0
 o.data.materials.clear();o.data.materials.append(mat)
 # authored origin for both assets and unique map geometry
 bpy.ops.mesh.primitive_cube_add(size=.1);origin=bpy.context.object;origin.name=src.name+'__origem';origin.parent=root
 for c in list(origin.users_collection):c.objects.unlink(origin)
 exp.objects.link(origin);origin.data.materials.append(mat)
bpy.ops.object.select_all(action='DESELECT')
for o in exp.all_objects:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(ROOT,'export','shadowgarden_kit.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,path_mode='COPY',embed_textures=True,mesh_smooth_type='FACE')
print('EXPORT_OBJECTS',len(exp.all_objects))
