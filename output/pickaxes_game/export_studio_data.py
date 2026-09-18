import bpy,json,os
from mathutils import Vector
out=r'C:\Users\lucas\OneDrive\Desktop\To up\output\pickaxes_game\studio_data'
os.makedirs(out,exist_ok=True)
ids=['enferrujada','ferro','aco','rubi','obsidiana','runica','estelar','ignis']
manifest=[]
for slug in ids:
    root=bpy.data.objects[slug]
    for o in root.children:
        if o.type!='MESH': continue
        mesh=o.data; mesh.calc_loop_triangles(); local=root.matrix_world.inverted()@o.matrix_world
        def convert(v): return [round(v.x,6),round(v.z,6),round(-v.y,6)]
        vertices=[convert(local@v.co) for v in mesh.vertices]
        normals=[convert(local.to_3x3()@n.vector) for n in mesh.corner_normals]
        uv=[[round(u.uv.x,6),round(1-u.uv.y,6)] for u in mesh.uv_layers.active.data]
        triangles=[[list(t.vertices),list(t.loops)] for t in mesh.loop_triangles]
        m=mesh.materials[0]; name=m.name.split('.')[0]
        p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        linear=list(p.inputs['Base Color'].default_value)[:3]
        color=[round(12.92*c if c<=.0031308 else 1.055*c**(1/2.4)-.055,5) for c in linear]
        material='Neon' if name in ['Arcane violet','Starlight','Molten orange','White hot core'] else ('Slate' if name=='Rust' else ('SmoothPlastic' if name in ['Leather','Leather wrap','Ruby crystal','Obsidian glass'] else ('Wood' if name=='Walnut' else 'Metal')))
        data={'slug':slug,'name':o.name,'material':material,'color':color,'vertices':vertices,'normals':normals,'uvs':uv,'triangles':triangles}
        file=o.name+'.json'
        with open(os.path.join(out,file),'w') as f: json.dump(data,f,separators=(',',':'))
        manifest.append({'file':file,'slug':slug,'name':o.name,'triangles':len(triangles)})
with open(os.path.join(out,'index.json'),'w') as f: json.dump(manifest,f)
print('EXPORTED',len(manifest),'meshes')
