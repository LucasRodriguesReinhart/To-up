import bpy,json,os
from mathutils import Vector
OUT=r'C:\Users\lucas\OneDrive\Desktop\To up\output\pickaxes_game'
with open(os.path.join(OUT,'manifest.json')) as f: manifest=json.load(f)
original=bpy.context.window.scene
qa=bpy.data.scenes.new('TEMP_EXPORT_QA'); bpy.context.window.scene=qa
results=[]
try:
    for item in manifest:
        slug=item['id']
        bpy.ops.import_scene.fbx(filepath=os.path.join(OUT,slug,slug+'.fbx'))
        meshes=[o for o in qa.objects if o.type=='MESH']
        assert len(meshes)==item['mesh_parts'],(slug,'mesh count')
        assert all(len(o.data.uv_layers)>0 for o in meshes),(slug,'missing UV')
        pts=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
        dims=[max(v[i] for v in pts)-min(v[i] for v in pts) for i in range(3)]
        assert 2.5<dims[2]<4.1,(slug,'unexpected height',dims)
        assert 2.0<dims[0]<4.5,(slug,'unexpected width',dims)
        results.append({'id':slug,'fbx_roundtrip':'pass','dimensions_blender':dims,'mesh_parts':len(meshes)})
        for o in list(qa.objects): bpy.data.objects.remove(o,do_unlink=True)
finally:
    bpy.context.window.scene=original; bpy.data.scenes.remove(qa)
with open(os.path.join(OUT,'validation.json'),'w') as f: json.dump(results,f,indent=2)
print(json.dumps(results))
