# k_render.py - renders de revisao: clay (Workbench + cavidade), cor de tinta (Workbench MATERIAL), wireframe (EEVEE com no Wireframe).
import bpy, os, math
from mathutils import Vector
from k_core import col

OUT = r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\murim\kit\renders"
os.makedirs(OUT, exist_ok=True)

def camera(loc, tgt, lens=35, name='CamKit'):
    sc = bpy.context.scene
    cam = bpy.data.objects.get(name)
    if cam is None:
        cam = bpy.data.objects.new(name, bpy.data.cameras.new(name)); col('CENA').objects.link(cam)
    cam.location = loc; d = Vector(tgt) - Vector(loc); cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = lens; cam.data.clip_end = 2000; sc.camera = cam; return cam

def sun(elev=48, azim=-35, energy=3.2):
    o = bpy.data.objects.get('SolKit')
    if o is None:
        o = bpy.data.objects.new('SolKit', bpy.data.lights.new('SolKit', 'SUN')); col('CENA').objects.link(o)
    o.data.energy = energy; o.data.angle = math.radians(3); o.data.color = (1.0, .94, .82)
    o.rotation_euler = (math.radians(90 - elev), 0, math.radians(azim)); return o

def only(cols):
    """deixa renderizaveis so as colecoes em `cols` (+ CENA)."""
    for c in bpy.context.scene.collection.children:
        vis = c.name in cols or c.name == 'CENA'
        c.hide_render = not vis
        lc = bpy.context.view_layer.layer_collection.children.get(c.name)
        if lc: lc.exclude = not vis

def workbench(path, mode='MATERIAL', res=(1400, 900), clay=(.78, .74, .68)):
    sc = bpy.context.scene; sc.render.engine = 'BLENDER_WORKBENCH'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.film_transparent = False
    sh = sc.display.shading; sh.light = 'STUDIO'; sh.color_type = mode; sh.single_color = clay
    sh.show_cavity = True; sh.cavity_type = 'BOTH'; sh.cavity_ridge_factor = 1.0; sh.cavity_valley_factor = 1.4
    sh.curvature_ridge_factor = 1.0; sh.curvature_valley_factor = 1.2; sh.show_shadows = True; sh.shadow_intensity = .35
    sh.show_object_outline = False; sh.show_specular_highlight = False
    sh.background_type = 'VIEWPORT'; sh.background_color = (.16, .17, .19)
    try: sc.display.render_aa = '8'
    except Exception: pass
    sc.render.filepath = os.path.join(OUT, path); bpy.ops.render.render(write_still=True); return sc.render.filepath

def eevee(path, res=(1400, 900), sky=(.50, .68, .92), sky_strength=1.0, samples=48):
    """render de apresentacao com os materiais FINAIS (atlas assados). View transform Standard = cores fieis ao que vai pro Roblox."""
    sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0; sc.view_settings.gamma = 1
    w = sc.world or bpy.data.worlds.new('World'); sc.world = w; w.use_nodes = True
    bg = next((n for n in w.node_tree.nodes if n.type == 'BACKGROUND'), None) or w.node_tree.nodes.new('ShaderNodeBackground')
    bg.inputs[0].default_value = (*sky, 1); bg.inputs[1].default_value = sky_strength
    outn = next((n for n in w.node_tree.nodes if n.type == 'OUTPUT_WORLD'), None) or w.node_tree.nodes.new('ShaderNodeOutputWorld')
    w.node_tree.links.new(bg.outputs[0], outn.inputs[0])
    try: sc.eevee.taa_render_samples = samples
    except Exception: pass
    for attr, val in (('use_shadows', True), ('use_raytracing', False)):
        try: setattr(sc.eevee, attr, val)
        except Exception: pass
    sc.render.filepath = os.path.join(OUT, path); bpy.ops.render.render(write_still=True); return sc.render.filepath
