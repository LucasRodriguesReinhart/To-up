# ETAPA 5: blockout of the whole island with proxy volumes (replaced later by the kit).
from db_layout import *

def blockout():
    B = G('DB_BLOCKOUT'); into(B); clear_collection(B)
    rs = rng(5)
    # quarry pit
    box('BO_PisoPedreira', (QC[0], QC[1], QFLOOR-2), (QRX*2, QRY*2, 4), 'db_dirt')
    for i in range(48):
        t = i/48*2*PI
        x, y = quarry_point(t, 1)
        x2, y2 = quarry_point(t + 2*PI/48, 1)
        ang = math.atan2(y2-y, x2-x)
        box('BO_Parede', ((x+x2)/2, (y+y2)/2, QFLOOR/2), (math.hypot(x2-x, y2-y)+1, 6, -QFLOOR), 'db_rock', (0, 0, ang))
    # plateau + complex
    x0, x1, y0, y1 = PLATEAU
    box('BO_Plato', ((x0+x1)/2, (y0+y1)/2, PLAT_Z/2), (x1-x0, y1-y0, PLAT_Z), 'cc_grey')
    dome('BO_Cupula', (70, 112, PLAT_Z), 32, 'cc_white', sink=.35)
    disc('BO_Torre', (112, 136, PLAT_Z+40), 7, 80, 'cc_white')
    ball('BO_Bulbo', (112, 136, PLAT_Z+84), 22, 'cc_blue')
    for (x, y) in ((40, 80), (40, 140), (124, 84)):
        disc('BO_Tanque', (x, y, PLAT_Z+9), 7, 18, 'cc_cream')
    # mountain + canyon spires
    for x in range(-200, 201, 16):
        h = 70 + 30*abs(math.sin(x*.02)) + (40 if x < -110 else 0)
        box('BO_Montanha', (x, mountain_front(x)+24, h/2), (18, 48, h), 'db_rock')
    for (x, y, r, h) in ((-176, 118, 11, 96), (-126, 142, 9, 80), (-150, 104, 6, 60), (-104, 176, 10, 70), (-188, 150, 8, 110)):
        disc('BO_Pilar', (x, y, h/2), r, h, 'db_rock_light')
    # lake
    cx, cy, rx, ry = LAKE
    box('BO_Lago', (cx, cy, -2.5), (rx*2, ry*2, .5), 'db_water')
    # town, sanctuary, arena, crater, portal, pad
    for (x, y) in ((-150, -90), (-120, -60), (-160, -30), (-110, -10), (-150, 20), (-100, 30), (-140, 50), (-176, -60)):
        dome('BO_CasaDomo', (x, y, 0), rs.uniform(7, 11), rs.choice(['cc_cream', 'cc_yellow', 'cc_white']), sink=.2)
    disc('BO_TorreVila', (-96, -80, 25), 3, 50, 'cc_white')
    ball('BO_TorreVilaBulbo', (-96, -80, 52), 12, 'cc_yellow')
    disc('BO_Santuario', (SANCT[0], SANCT[1], .75), 17, 1.5, 'temple_stone')
    disc('BO_Dragao', (SANCT[0]-20, SANCT[1], 16), 4, 32, 'dragon')
    box('BO_Arena', (ARENA[0], ARENA[1], 1.5), (40, 40, 3), 'temple_tile')
    disc('BO_Cratera', (CRATER[0], CRATER[1], -3), CR_R, 6, 'db_crater')
    vring('BO_Portal', (PORTAL[0], PORTAL[1], 14), 11, 2.5, 2.5, 'cc_blue', 20, -PI/4)
    disc('BO_Pista', (PAD[0], PAD[1], .1), PAD[2], .2, 'db_paving')
    # trees
    for i in range(60):
        x, y = rs.uniform(-190, 190), rs.uniform(-190, 150)
        if not in_poly(x, y) or quarry_f(x, y, 14) <= 1 or lake_f(x, y, 6) <= 1: continue
        if PLATEAU[0]-6 < x < PLATEAU[1]+6 and PLATEAU[2]-6 < y < PLATEAU[3]+6: continue
        if abs(x) < 14 and y < -90: continue
        s = rs.uniform(6, 10)
        disc('BO_Tronco', (x, y, s*.6), .8, s*1.2, 'db_trunk')
        ball('BO_Copa', (x, y, s*1.5), s*1.4, 'tree_ball')

def shot(name, eye, target, lens=24, res=(1280, 720)):
    scn = bpy.context.scene
    cam = bpy.data.objects.get('DBCam')
    if not cam:
        cam = bpy.data.objects.new('DBCam', bpy.data.cameras.new('DBCam'))
        scn.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.clip_end = 3000
    cam.location = eye
    d = Vector(target) - Vector(eye)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    scn.camera = cam
    scn.render.engine = 'BLENDER_WORKBENCH'
    sh = scn.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'TEXTURE'
    sh.show_shadows = True; sh.show_cavity = True; sh.cavity_type = 'WORLD'
    sh.background_type = 'VIEWPORT' if hasattr(sh, 'background_type') else sh.background_type
    scn.world.color = (0.45, 0.72, 1.0) if scn.world else None
    scn.render.resolution_x, scn.render.resolution_y = res
    scn.render.film_transparent = False
    path = SHOTS + '\\' + name + '.png'
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path

SHOTS = r"C:\Users\lucas\AppData\Local\Temp\claude\C--Users-lucas-OneDrive-Desktop-To-up\dac70137-60fb-4411-a2ab-aa40fdb92195\scratchpad\db"
