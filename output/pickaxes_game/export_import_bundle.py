import bpy,os,json
out=r'C:\Users\lucas\OneDrive\Desktop\To up\output\pickaxes_game'
ids=['enferrujada','ferro','aco','rubi','obsidiana','runica','estelar','ignis']
saved=[]
bpy.ops.object.select_all(action='DESELECT')
for i,slug in enumerate(ids):
    root=bpy.data.objects[slug]; saved.append((root,root.matrix_world.copy()))
    root.location=(i*5,0,0); root.rotation_euler=(0,0,0); root.select_set(True)
    for o in root.children:
        if o.type=='MESH': o.select_set(True)
bpy.ops.export_scene.fbx(filepath=os.path.join(out,'IMPORTAR_8_PICARETAS.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False,use_mesh_modifiers=True)
for root,matrix in saved: root.matrix_world=matrix
print('BUNDLE_READY')
