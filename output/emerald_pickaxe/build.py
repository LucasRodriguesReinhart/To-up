import bpy, math, os
from mathutils import Vector

OUT = r'C:\Users\lucas\OneDrive\Desktop\To up\output\emerald_pickaxe'
os.makedirs(OUT, exist_ok=True)
scene=bpy.context.scene
collection=bpy.data.collections.new('Emerald Warden | Game Asset')
scene.collection.children.link(collection)
parts=[]
def mat(name,color,metal=0,rough=.4,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    if emission: p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    return m
steel=mat('01 | Obsidian steel',(.065,.10,.115),.85,.29)
edge=mat('02 | Honed silver',(.43,.56,.58),.9,.23)
gold=mat('03 | Antique brass',(.52,.29,.065),.78,.3)
dark=mat('04 | Recessed iron',(.023,.035,.03),.65,.43)
leather=mat('05 | Oxblood leather',(.16,.047,.025),0,.78)
wrap=mat('06 | Leather binding',(.30,.095,.042),0,.7)
green=mat('07 | Emerald crystal',(.09,.8,.018),.35,.22,2)
def register(o,name,m):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    collection.objects.link(o); o.data.materials.append(m); parts.append(o); return o
def bevel(o,w=.025):
    mod=o.modifiers.new('Forged edge bevel','BEVEL'); mod.width=w; mod.segments=2
    mod=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def cyl(name,r,depth,z,m,vertices=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=(0,0,z))
    return bevel(register(bpy.context.object,name,m),.018)
def box(name,loc,scale,m,w=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return bevel(register(o,name,m),w)
def poly(name,points,depth,m):
    n=len(points); verts=[(x,y,z) for y in [-depth/2,depth/2] for x,z in points]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); collection.objects.link(o); o.data.materials.append(m); parts.append(o); return o
def gem(name,loc,scale,m=green):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
    o=register(bpy.context.object,name,m); o.scale=scale; return o

cyl('Full length forged tang',.115,2.65,1.45,dark)
cyl('Leather grip',.15,1.65,1.13,leather,12)
for i in range(9):
    # Separate diagonal leather straps, closed around the handle.
    verts=[]; faces=[]; steps=12
    for j in range(steps+1):
        a=j/steps*math.tau; z=.40+i*.175+.13*j/steps
        for dz in [-.029,.029]: verts.append((.157*math.cos(a),.157*math.sin(a),z+dz))
    for j in range(steps): faces.append((j*2,j*2+1,j*2+3,j*2+2))
    mesh=bpy.data.meshes.new('strap'); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new('Diagonal leather wrap %02d'%i,mesh); collection.objects.link(o); o.data.materials.append(wrap); parts.append(o)
for z,r,h in [(.25,.205,.15),(.38,.175,.08),(2.02,.19,.16),(2.13,.215,.08),(2.47,.22,.17)]:
    cyl('Engraved brass ferrule',r,h,z,gold)
    cyl('Ferrule inset',r+.004,.032,z,dark)
cyl('Pommel collar',.2,.08,.12,gold)
gem('Faceted iron pommel',(0,0,.04),(.24,.20,.25),steel)
gem('Pommel emerald',(0,-.17,.02),(.10,.07,.13))

# Down-curving tips and a thick central shoulder, inspired by a fantasy mining pick.
outline=[(.18,2.98),(.55,3.16),(1.02,3.24),(1.42,3.14),(1.76,2.90),(1.99,2.49),(1.65,2.72),(1.28,2.88),(.90,2.91),(.48,2.78),(.20,2.68)]
for side in [-1,1]:
    bevel(poly('Forged blade '+str(side),[(x*side,z) for x,z in outline],.22,steel),.018)
    strip=[(1.99,2.49),(1.65,2.72),(1.28,2.88),(.90,2.91),(.48,2.78),(.48,2.86),(.92,2.99),(1.3,2.96),(1.69,2.79)]
    bevel(poly('Honed cutting edge '+str(side),[(x*side,z) for x,z in strip],.235,edge),.008)
    for face in [-1,1]:
        for x,z in [(.68,3.02),(1.12,3.06),(1.49,2.95)]:
            o=box('Blade brass rune',(side*x,face*.123,z),(.09,.015,.12),gold,.004); o.rotation_euler.y=side*math.radians(40)
        o=poly('Emerald vein '+str(side),[(side*.34,2.82),(side*.64,2.96),(side*1.02,3.04),(side*.65,3.005),(side*.34,2.87)],.014,green); o.location.y=face*.125

box('Central reinforced socket',(0,0,2.89),(.51,.43,.66),dark,.06)
for x in [-.25,.25]: box('Brass socket rail',(x,0,2.91),(.075,.49,.65),gold)
for z in [2.59,3.21]: box('Socket crown',(0,0,z),(.60,.50,.10),gold)
for face in [-1,1]:
    o=box('Diamond bezel',(0,face*.25,2.94),(.31,.085,.31),gold); o.rotation_euler.y=math.pi/4
    gem('Heart emerald',(0,face*.32,2.94),(.19,.105,.24))
    for x in [-.185,.185]:
        for z in [2.7,3.1]: gem('Socket rivet',(x,face*.238,z),(.037,.025,.037),gold)
gem('Crown crystal',(0,0,3.34),(.105,.12,.17))

# Apply modifiers and generate nonoverlapping UV islands on the game meshes.
bpy.ops.object.select_all(action='DESELECT')
for o in parts:
    o.select_set(True); bpy.context.view_layer.objects.active=o
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for mod in list(o.modifiers):
        try: bpy.ops.object.modifier_apply(modifier=mod.name)
        except: pass
    o.select_set(False)
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.015)
bpy.ops.object.mode_set(mode='OBJECT')
root=bpy.data.objects.new('Emerald Warden Pickaxe',None); collection.objects.link(root)
for o in parts: o.parent=root
root['asset_notes']='Original stylized fantasy pickaxe inspired by provided reference. Z up; handle centered on origin. Material colors; UVs generated, no texture atlas.'
root.select_set(True)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'emerald_warden_pickaxe.glb'),use_selection=True,export_format='GLB')

# Keep existing user objects, hide them for presentation.
for o in scene.objects:
    if o not in parts and o!=root: o.hide_render=True; o.hide_set(True)
world=bpy.data.worlds.new('Studio charcoal'); scene.world=world; world.use_nodes=True
next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[0].default_value=(.022,.032,.042,1)
next(n for n in world.node_tree.nodes if n.type=='BACKGROUND').inputs[1].default_value=.4
def aim(o,p): o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(4,-9,4.3)); cam=bpy.context.object; cam.name='Presentation Camera'; aim(cam,(0,0,1.7)); cam.data.type='ORTHO'; cam.data.ortho_scale=5.1; scene.camera=cam
for name,loc,power,size,color in [('Key',(-3,-4,6),950,4,(.79,.9,1)),('Gold rim',(3,2,4),1200,3,(1,.73,.38)),('Front',(1,-4,1),250,3,(.65,1,.77))]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=color; aim(o,(0,0,1.6))
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=1100; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,'emerald_warden_preview.png')
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active=parts[0]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'
            area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'emerald_warden_pickaxe.blend'))
print('ASSET_READY',len(parts),'mesh parts',sum(len(o.data.polygons) for o in parts),'polygons')

