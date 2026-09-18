import bpy, math, os, json
from mathutils import Vector

OUT=r'C:\Users\lucas\OneDrive\Desktop\To up\output\pickaxes_game'
os.makedirs(OUT,exist_ok=True)
scene=bpy.context.scene
for o in scene.objects: o.hide_render=True; o.hide_set(True)
parts=[]
def mat(name,c,metal=0,rough=.4,emit=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*c,1); m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emit
    return m
iron=mat('Iron',(.16,.20,.23),.75,.4)
silver=mat('Steel edge',(.51,.64,.71),.83,.25)
rust=mat('Rust',(.29,.105,.038),.35,.85)
wood=mat('Walnut',(.14,.061,.026),0,.82)
leather=mat('Leather',(.072,.027,.021),0,.76)
binding=mat('Leather wrap',(.22,.09,.04),0,.73)
brass=mat('Old brass',(.44,.26,.08),.8,.38)
gold=mat('Royal gold',(.68,.40,.095),.8,.27)
black=mat('Blackened metal',(.027,.035,.046),.7,.36)
obsidian=mat('Obsidian glass',(.032,.014,.06),.68,.19)
purplemetal=mat('Amethyst metal',(.13,.055,.23),.75,.32)
ruby=mat('Ruby crystal',(.65,.015,.047),.36,.24,.55)
violet=mat('Arcane violet',(.40,.055,1),.3,.23,1.3)
cyan=mat('Starlight',(.13,.68,1),.3,.23,1.6)
navy=mat('Celestial blue',(.025,.075,.19),.76,.26)
fire=mat('Molten orange',(1,.14,.007),.25,.29,1.5)
hot=mat('White hot core',(1,.64,.075),.3,.23,2)
darkred=mat('Volcanic armor',(.12,.023,.017),.74,.37)
def add(o,name,m):
    o.name=name
    for c in list(o.users_collection): c.objects.unlink(o)
    col.objects.link(o); o.data.materials.append(m); parts.append(o); return o
def bevel(o,w=.018):
    if w:
        mod=o.modifiers.new('Edge bevel','BEVEL'); mod.width=w; mod.segments=1
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def cylinder(name,r,h,z,m,n=10):
    bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=h,location=(0,0,z)); return bevel(add(bpy.context.object,name,m))
def box(name,loc,size,m,w=.018):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); return bevel(add(o,name,m),w)
def poly(name,points,depth,m,y=0,w=0):
    n=len(points); mesh=bpy.data.meshes.new(name)
    mesh.from_pydata([(x,yy+y,z) for yy in [-depth/2,depth/2] for x,z in points],[],[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)])
    mesh.update(); o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(m); parts.append(o); return bevel(o,w)
def crystal(name,loc,scale,m):
    # Hexagonal prism with pointed terminations, deliberately crisp facets.
    verts=[(0,0,-1)]+[(math.cos(a*math.tau/6),math.sin(a*math.tau/6),z) for z in [-.42,.38] for a in range(6)]+[(0,0,1)]
    faces=[(0,1+(i+1)%6,1+i) for i in range(6)]+[(1+i,1+(i+1)%6,7+(i+1)%6,7+i) for i in range(6)]+[(7+i,7+(i+1)%6,13) for i in range(6)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update(); o=bpy.data.objects.new(name,mesh); col.objects.link(o); o.data.materials.append(m); parts.append(o); o.location=loc; o.scale=scale; return o
def line(name,points,width,m,y=-.18):
    for (x,z),(xx,zz) in zip(points,points[1:]):
        mid=((x+xx)/2,y,(z+zz)/2); length=math.hypot(xx-x,zz-z)
        o=box(name,mid,(width,.018,length),m,.003); o.rotation_euler.y=math.atan2(xx-x,zz-z)
def grip(tier,accent):
    cylinder('Tang',.10,2.75,1.44,black)
    cylinder('Wood handle' if tier<3 else 'Leather handle',.135,2.33,1.35,wood if tier<3 else leather,10)
    for i in range(6 if tier<3 else 10):
        z=.43+i*(.23 if tier<3 else .15)
        verts=[]
        for j in range(13):
            a=j*math.tau/12
            for dz in [-.031,.031]: verts.append((.145*math.cos(a),.145*math.sin(a),z+.14*j/12+dz))
        mesh=bpy.data.meshes.new('Wrap'); mesh.from_pydata(verts,[],[(j*2,j*2+1,j*2+3,j*2+2) for j in range(12)]); mesh.update()
        o=bpy.data.objects.new('Grip wrap',mesh); col.objects.link(o); o.data.materials.append(binding if tier<5 else black); parts.append(o)
    for z in [.28,2.16,2.49]: cylinder('Handle collar',.175,.11,z,accent)
    if tier>=3:
        cylinder('Pommel',.2,.20,.12,accent)
        cylinder('Guard',.21,.10,2.32,accent)
    if tier>=4: crystal('Pommel gem',(0,-.15,.12),(.095,.07,.12),[ruby,violet,violet,cyan,fire][tier-4])
def socket(tier,metal,gem=None):
    box('Head socket',(0,0,2.9),(.44,.40,.56),metal,.04)
    for z in [2.64,3.16]: box('Socket cap',(0,0,z),(.52,.44,.075),metal)
    for face in [-1,1]:
        if gem:
            o=box('Gem bezel',(0,face*.225,2.92),(.27,.08,.31),gold if tier in [4,7,8] else silver); o.rotation_euler.y=math.pi/4
            crystal('Core crystal',(0,face*.29,2.92),(.16,.09,.25),gem)
        else:
            for x in [-.14,.14]:
                crystal('Rivet',(x,face*.21,2.92),(.035,.025,.04),silver if tier>1 else iron)
def blades(tier,body,trim):
    if tier==1:
        right=[(.18,3.02),(.65,3.07),(1.11,2.92),(1.45,2.62),(1.65,2.27),(1.20,2.65),(.66,2.82),(.18,2.80)]
        left=[(.18,3.02),(.75,3.04),(1.0,2.97),(1.06,2.70),(.74,2.75),(.18,2.80)]
    elif tier==2:
        right=[(.18,3.06),(.77,3.10),(1.2,2.96),(1.65,2.55),(1.27,2.72),(.74,2.87),(.18,2.82)]
        left=[(.18,3.06),(.85,3.10),(1.1,3.00),(1.13,2.75),(.77,2.84),(.18,2.82)]
    elif tier==5:
        right=[(.18,3.05),(.62,3.27),(.95,3.16),(1.12,3.36),(1.32,3.11),(1.57,3.04),(1.5,2.9),(1.96,2.43),(1.43,2.62),(1.19,2.81),(.92,2.70),(.57,2.86),(.18,2.70)]; left=right
    elif tier==8:
        right=[(.18,3.07),(.53,3.24),(.67,3.60),(.85,3.28),(1.12,3.24),(1.20,3.49),(1.42,3.11),(1.72,2.96),(2.05,2.32),(1.48,2.69),(1.12,2.76),(.79,2.90),(.40,2.73),(.18,2.7)]; left=right
    else:
        span={3:1.60,4:1.73,6:1.83,7:1.9}[tier]
        right=[(.18,3.05),(.59,3.21),(1.04,3.23),(1.40,3.02),(span,2.49),(1.28,2.80),(.93,2.95),(.56,2.91),(.18,2.72)]; left=right
    for sign,pts in [(1,right),(-1,left)]:
        poly('Blade',[(sign*x,z) for x,z in pts],.25 if tier>=5 else .21,body,w=.012)
        if tier in [3,4,6,7]:
            p=[(.55,2.91),(.93,2.95),(1.28,2.80),(pts[4][0],2.49),(1.31,2.89),(.94,3.03),(.55,2.99)]
            poly('Cutting edge',[(sign*x,z) for x,z in p],.267,trim,w=.005)
        if tier in [1,2]:
            for face in [-1,1]:
                line('Forge seam',[(sign*.34,2.94),(sign*.73,2.98),(sign*1.0,2.88)],.024,iron if tier==1 else silver,face*.116)
        if tier>=4:
            energy={4:ruby,5:violet,6:violet,7:cyan,8:fire}[tier]
            for face in [-1,1]:
                line('Energy inlay',[(sign*.33,2.88),(sign*.67,3.06),(sign*1.02,3.10),(sign*1.38,2.94)],.035 if tier!=8 else .065,energy,face*.14)
        if tier==1:
            for face in [-1,1]:
                for x,z in [(.44,2.91),(.7,2.96),(1.04,2.84)]:
                    poly('Rust patch',[(sign*(x-.11),z-.05),(sign*(x+.10),z-.015),(sign*(x+.04),z+.075),(sign*(x-.07),z+.035)],.007,rust,face*.118)

definitions=[('enferrujada','ENFERRUJADA',2),('ferro','FERRO',8),('aco','ACO',34),('rubi','RUBI',150),('obsidiana','OBSIDIANA',700),('runica','RUNICA',3400),('estelar','ESTELAR',17000),('ignis','IGNIS',90000)]
report=[]; roots=[]
for tier,(slug,title,damage) in enumerate(definitions,1):
    parts=[]; col=bpy.data.collections.new('PICKAXE | '+slug); scene.collection.children.link(col)
    accent=[iron,iron,silver,gold,purplemetal,silver,gold,gold][tier-1]
    body=[rust,iron,iron,black,obsidian,purplemetal,navy,darkred][tier-1]
    energy=[None,None,None,ruby,violet,violet,cyan,fire][tier-1]
    grip(tier,accent); blades(tier,body,silver if tier!=7 else gold); socket(tier,accent,energy)
    if tier==3:
        for face in [-1,1]:
            for sign in [-1,1]: line('Steel reinforcement',[(sign*.35,3.06),(sign*.64,3.14),(sign*.98,3.14)],.035,silver,face*.13)
    if tier==4:
        for sign in [-1,1]:
            o=crystal('Ruby shoulder',(sign*.58,0,3.27),(.145,.15,.33),ruby); o.rotation_euler.y=sign*.35
        crystal('Ruby crown',(0,0,3.32),(.105,.11,.22),ruby)
    if tier==5:
        for sign in [-1,1]:
            for x,z,s in [(.46,3.23,.28),(.97,3.31,.24),(1.41,3.02,.17)]:
                o=crystal('Obsidian shard',(sign*x,.03,z),(.12,.15,s),obsidian); o.rotation_euler.y=sign*.55
        crystal('Void shard',(0,0,3.34),(.14,.14,.31),violet)
    if tier==6:
        for face in [-1,1]:
            for sign in [-1,1]:
                for x,z in [(.68,3.12),(1.10,3.10)]:
                    line('Runic glyph',[(sign*(x-.06),z+.035),(sign*x,z-.035),(sign*(x+.06),z+.035)],.023,violet,face*.16)
                    line('Runic glyph stem',[(sign*x,z-.065),(sign*x,z+.075)],.021,violet,face*.16)
        for z in [.72,1.1,1.48]:
            cylinder('Runic grip band',.155,.065,z,silver)
            crystal('Grip rune',(0,-.159,z),(.033,.018,.08),violet)
        for sign in [-1,1]: poly('Crown prong',[(sign*.17,3.17),(sign*.27,3.52),(sign*.35,3.36),(sign*.29,3.12)],.23,silver,w=.01)
        crystal('Arcane focus',(0,0,3.42),(.105,.1,.25),violet)
    if tier==7:
        for sign in [-1,1]:
            poly('Celestial wing',[(sign*.45,3.16),(sign*.68,3.48),(sign*1.17,3.56),(sign*.88,3.32),(sign*.72,3.19)],.15,gold,w=.008)
            crystal('Wing starlight',(sign*.78,-.09,3.37),(.12,.055,.15),cyan)
        star=[(math.sin(i*math.pi/4)*(.34 if i%2==0 else .115),3.43+math.cos(i*math.pi/4)*(.34 if i%2==0 else .115)) for i in range(8)]
        poly('Four point star',star,.11,gold,w=.009)
        crystal('Star core',(0,-.075,3.43),(.105,.07,.14),cyan)
        for face in [-1,1]:
            for sign in [-1,1]:
                for x,z in [(.68,3.11),(1.01,3.14),(1.30,3.0)]: crystal('Constellation stud',(sign*x,face*.15,z),(.027,.022,.035),cyan)
    if tier==8:
        for sign in [-1,1]:
            poly('Molten cutting channel',[(sign*.40,2.80),(sign*.80,2.98),(sign*1.14,2.85),(sign*1.51,2.80),(sign*2.05,2.32),(sign*1.65,2.79),(sign*1.21,2.98),(sign*.77,3.09)],.273,fire,w=.004)
            poly('Golden fire horn',[(sign*.17,3.13),(sign*.24,3.50),(sign*.49,3.74),(sign*.39,3.37),(sign*.32,3.13)],.25,gold,w=.01)
            for face in [-1,1]: line('Hot fissure',[(sign*.61,3.19),(sign*.69,3.35),(sign*.73,3.22)],.035,hot,face*.144)
        crystal('Furnace heart',(0,-.30,2.92),(.11,.065,.18),hot)
        crystal('Eternal flame',(0,0,3.43),(.13,.13,.29),fire)
        for z in [.6,.98,1.36,1.74]:
            cylinder('Lava grip cage',.16,.07,z,gold)
            crystal('Grip ember',(0,-.151,z+.1),(.035,.03,.08),fire)
    # Bake transforms, normals and UVs. Combine by material to reduce draw calls.
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:
        o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for mod in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=mod.name)
        o.select_set(False)
    grouped=[]; material_groups={}
    for o in parts: material_groups.setdefault(o.data.materials[0],[]).append(o)
    for material,subset in material_groups.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in subset: o.select_set(True)
        bpy.context.view_layer.objects.active=subset[0]; bpy.ops.object.join()
        o=bpy.context.object; o.name=slug+'__'+material.name.replace(' ','_'); grouped.append(o)
    parts=grouped
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts: o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.uv.smart_project(angle_limit=math.radians(65),island_margin=.012); bpy.ops.object.mode_set(mode='OBJECT')
    # Pivot at the grip center. Blender Z up converts to Roblox Y up in FBX.
    for o in parts: o.location.z-=1.15
    scene.cursor.location=(0,0,0); bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    root=bpy.data.objects.new(slug,None); col.objects.link(root); roots.append(root)
    root['PicaretaId']=slug; root['BaseDamage']=damage
    for o in parts: o.parent=root
    root.select_set(True)
    target=os.path.join(OUT,slug); os.makedirs(target,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(target,slug+'.glb'),use_selection=True,export_format='GLB')
    bpy.ops.export_scene.fbx(filepath=os.path.join(target,slug+'.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,bake_anim=False,add_leaf_bones=False,use_mesh_modifiers=True)
    tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in parts)
    report.append({'id':slug,'name':title,'base_damage':damage,'triangles':tris,'mesh_parts':len(parts),'uv':all(len(o.data.uv_layers)>0 for o in parts),'materials':[o.data.materials[0].name for o in parts]})
    root.location=((tier-1)%4*4.8-7.2,0,4.9 if tier<=4 else 0)
    root.rotation_euler.z=math.radians(-5 if tier%2 else 5)

presentation=bpy.data.collections.new('PRESENTATION'); scene.collection.children.link(presentation)
def present(o):
    for c in list(o.users_collection): c.objects.unlink(o)
    presentation.objects.link(o)
labelmat=mat('Label white',(.68,.78,.86),0,.6,.25)
muted=mat('Label muted',(.25,.37,.46),0,.8,.2)
def text_obj(body,x,z,size,m):
    curve=bpy.data.curves.new('Label','FONT'); curve.body=body; curve.align_x='CENTER'; curve.size=size; curve.extrude=0
    o=bpy.data.objects.new(body,curve); presentation.objects.link(o); o.location=(x,-.25,z); o.rotation_euler=(math.pi/2,0,0); o.data.materials.append(m)
for tier,(slug,title,damage) in enumerate(definitions,1):
    x=(tier-1)%4*4.8-7.2; z=4.9 if tier<=4 else 0
    text_obj('%02d  /  %s'%(tier,title),x,z-1.68,.25,labelmat)
    text_obj('DANO  '+format(damage,','),x,z-2.02,.16,muted)
text_obj('IGNIS  /  ARSENAL DE MINERACAO',0,8.50,.43,labelmat)
text_obj('OITO NIVEIS  -  COLECAO DE PICARETAS',0,8.04,.18,muted)
world=bpy.data.worlds.new('Arsenal studio'); scene.world=world; world.use_nodes=True
bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND'); bg.inputs[0].default_value=(.013,.022,.035,1); bg.inputs[1].default_value=.5
def aim(o,point): o.rotation_euler=(Vector(point)-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(0,-30,5.5)); camera=bpy.context.object; present(camera); camera.name='Arsenal Camera'; aim(camera,(0,0,3.2)); camera.data.type='ORTHO'; camera.data.ortho_scale=20.5; scene.camera=camera
for name,loc,power,size,color in [('Key',(-7,-8,12),2400,8,(.8,.9,1)),('Fill',(8,-6,6),2000,7,(1,.82,.62)),('Rim',(0,3,9),3000,8,(.5,.7,1)),('Lower',(-5,-4,1),500,5,(.65,.80,1))]:
    bpy.ops.object.light_add(type='AREA',location=loc); o=bpy.context.object; present(o); o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.data.color=color; aim(o,(0,0,3))
scene.render.engine='CYCLES'; scene.cycles.samples=32
scene.render.resolution_x=2400; scene.render.resolution_y=1450; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.filepath=os.path.join(OUT,'arsenal_preview.png')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA'; area.spaces.active.shading.type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
with open(os.path.join(OUT,'manifest.json'),'w',encoding='utf-8') as f: json.dump(report,f,indent=2)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'picaretas_arsenal.blend'))
print('COMPLETE',json.dumps(report))
