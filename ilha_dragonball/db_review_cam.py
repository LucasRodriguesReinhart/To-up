# db_review_cam.py - video/quadros de revisao da Ilha 2 (nao entra no export do jogo). Tres tipos de plano:
#   dolly  : parte de uma CAM_* existente e recua/avanca (param = recuo em studs)
#   orbit  : gira em volta do centro da ilha a partir de uma CAM_* (param = varredura em graus)
#   walk   : CAMERA DE JOGADOR em 3a pessoa seguindo uma rota do db_qa (andador sobre as colisoes COL_: o boneco
#            anda no piso real, a camera fica atras/acima como a camera padrao do Roblox e encosta na parede quando
#            algo fica entre ela e o boneco). param = velocidade em studs/s (WalkSpeed 16 do Roblox; >16 acelera)
# uso: blender -b ilha_dragonball.blend --python db_review_cam.py -- <modo> <pasta> [--res 1280x720] [--only A,B]
#   frames : so o ULTIMO quadro de cada plano (PNG) para conferir enquadramento
#   walks  : quadros a cada ~18 studs de cada caminhada (revisao na altura do jogador, sem video)
#   seq    : a sequencia PNG inteira; o mp4 sai depois com o ffmpeg do imageio-ffmpeg:
#            ffmpeg -y -framerate 24 -i "<pasta>/f_%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 20 out.mp4
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
from mathutils import Vector, Quaternion
import db_lib as DL
import db_layout as L
import fm_qa
import db_qa

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE, OUT = argv[0], argv[1]
RES = (1280, 720)
ONLY = None
for i, a in enumerate(argv):
    if a == "--res":
        w, h = argv[i + 1].split("x")
        RES = (int(w), int(h))
    if a == "--only":
        ONLY = set(argv[i + 1].split(","))
FPS = 24
sc = bpy.context.scene
sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = RES
sc.eevee.taa_render_samples = 24 if MODE != "seq" else 12

# (nome, tipo, duracao_s (walk: ignorado), param, extra)
SHOTS = [
    ("CAM_DB_Front", "dolly", 3.0, 80.0, None),                      # a ilha inteira ao longe
    ("NARUTO_GATE->DB_ENTRY", "walk", 0, 26.0, None),                # a ponte de chegada, a escadaria e o portao
    ("CAM_DB_Mining", "dolly", 3.0, 20.0, None),
    ("DB_ENTRY->MINING", "walk", 0, 26.0, None),                     # descer para a arena
    ("MINING->SUMMON", "walk", 0, 26.0, None),
    ("CAM_DB_Summon", "dolly", 2.6, 16.0, None),
    ("MINING->CAPSULE", "walk", 0, 26.0, None),                      # vila -> Capsule -> salao por dentro
    ("CAM_DB_CapsuleInterior", "dolly", 2.6, 8.0, None),
    ("CAPSULE->SHADOW_GATE", "walk", 0, 30.0, None),                 # vila leste, trilha, arco, ponte, portao
    ("CAM_DB_ShadowGate", "dolly", 2.8, 18.0, None),
    ("CAM_DB_Ref_Main", "orbit", 6.0, 70.0, None),
    ("CAM_DB_BirdEye", "orbit", 4.0, 40.0, None),
]
PIVOT = Vector((0.0, 20.0, 24.0))
CAM_BACK, CAM_UP, HEAD = 12.5, 3.2, 4.6      # camera padrao do Roblox: ~12,5 atras da cabeca, olhando um pouco p/ baixo


def ease(t):
    return 1.0 - (1.0 - t) * (1.0 - t)


bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
cam_data = bpy.data.cameras.new("ReviewCamData")
cam_data.lens = 22.0
cam_data.clip_end = 4000.0
cam_obj = bpy.data.objects.new("CAM_ReviewVideo", cam_data)
sc.collection.objects.link(cam_obj)
cam_obj.rotation_mode = 'QUATERNION'
sc.camera = cam_obj

# boneco que anda nas caminhadas (o mesmo R15 cinza de 5,2 das referencias)
walker = DL.dummy("REVIEW_Walker", 0.0, 0.0, 0.0, 0.0, visible=True)   # malha em volta da origem (o MB grava coordenadas no vertice)
walker.rotation_mode = 'XYZ'
for c in list(walker.users_collection):          # a colecao _SCALE_REFERENCE nao renderiza: o boneco vai para a cena
    c.objects.unlink(walker)
sc.collection.objects.link(walker)
walker.hide_render = False
for o in list(bpy.data.objects):
    if o.name.startswith("SCALE_Dummy") or o.name.startswith("_SCALE"):
        o.hide_render = True

bvh, _ = fm_qa.col_bvh()
ROUTES = db_qa.routes()
ROUTES.update(db_qa.open_routes())


def route_path(name):
    """amostras (x, y, z_piso) a cada 0,5 ao longo da rota, andando sobre as COL_ como o andador do QA"""
    pts, z = ROUTES[name]
    out = []
    for a, b in zip(pts, pts[1:]):
        a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        n = max(1, int((b - a).length / 0.5))
        for i in range(n):
            p = a + (b - a) * (i / n)
            g = fm_qa.ground(bvh, p.x, p.y, z)
            if g is not None and abs(g - z) <= 2.4:
                z = g
            out.append(Vector((p.x, p.y, z)))
    out.append(Vector((pts[-1][0], pts[-1][1], z)))
    return out


def smooth_dir(path, i, span=10):
    a = path[max(0, i - span)]
    b = path[min(len(path) - 1, i + span)]
    d = Vector((b.x - a.x, b.y - a.y, 0.0))
    return d.normalized() if d.length > 1e-3 else Vector((0, 1, 0))


def third_person(p, fwd):
    head = p + Vector((0, 0, HEAD))
    want = head - fwd * CAM_BACK + Vector((0, 0, CAM_UP))
    ray = want - head
    hit = bvh.ray_cast(head, ray.normalized(), ray.length)
    if hit[0] is not None:                    # parede entre a camera e o boneco: encosta (como o Roblox)
        want = head + ray.normalized() * max(2.0, (hit[0] - head).length - 0.6)
    tgt = head + fwd * 6.0 - Vector((0, 0, 0.6))
    return want, (tgt - want).normalized().to_track_quat('-Z', 'Y')


frame = 1
marks = []          # (frame, nome) - ultimo quadro de cada plano
walk_marks = []     # (frame, nome) - quadros de revisao das caminhadas
walker.location = (0, 0, -500)
walker.keyframe_insert('location', frame=1)
for name, kind, dur, param, extra in SHOTS:
    if ONLY and name not in ONLY:
        continue
    if kind == "walk":
        if name not in ROUTES:
            print("REVIEW aviso: rota %s nao existe" % name)
            continue
        path = route_path(name)
        step = param / FPS / 0.5                     # amostras por quadro
        nfr = max(2, int(len(path) / step))
        f0 = frame
        cam_data.lens = 22.0                         # campo de visao ~70 graus, como a camera do Roblox
        cam_data.keyframe_insert('lens', frame=f0)
        cam_data.keyframe_insert('lens', frame=f0 + nfr)
        walker.location = (0, 0, -500)
        walker.keyframe_insert('location', frame=f0 - 1 if f0 > 1 else 1)
        cyaw = None
        cpos = None
        for k in range(nfr + 1):
            i = min(len(path) - 1, int(k * step))
            p = path[i]
            fwd = smooth_dir(path, i, 14)
            yaw = math.atan2(fwd.y, fwd.x)
            if cyaw is None:
                cyaw = yaw
            d = (yaw - cyaw + math.pi) % (2 * math.pi) - math.pi
            cyaw += d * 0.18                          # a camera gira atrasada (suave), como a do jogo
            cf = Vector((math.cos(cyaw), math.sin(cyaw), 0.0))
            loc, quat = third_person(p, cf)
            cpos = loc if cpos is None else cpos.lerp(loc, 0.35)
            fk = f0 + k
            walker.location = p
            walker.rotation_euler = (0.0, 0.0, yaw - math.pi / 2)
            walker.keyframe_insert('location', frame=fk)
            walker.keyframe_insert('rotation_euler', frame=fk)
            cam_obj.location = cpos
            cam_obj.rotation_quaternion = quat
            cam_obj.keyframe_insert('location', frame=fk)
            cam_obj.keyframe_insert('rotation_quaternion', frame=fk)
            if k % max(1, int(18.0 / (param / FPS))) == 0:
                walk_marks.append((fk, "%s_%03d" % (name.replace(">", "").replace("-", "_"), k)))
        f1 = f0 + nfr
        walker.location = (0, 0, -500)
        walker.keyframe_insert('location', frame=f1 + 1)
        print("REVIEW walk %s: %d amostras, %.1f s" % (name, len(path), nfr / FPS))
    else:
        src = bpy.data.objects.get(name)
        if src is None:
            print("REVIEW aviso: camera %s nao existe" % name)
            continue
        f0 = frame
        f1 = frame + int(dur * FPS) - 1
        cam_data.lens = src.data.lens
        cam_data.keyframe_insert('lens', frame=f0)
        cam_data.keyframe_insert('lens', frame=f1)
        if kind == "dolly":
            fwd = src.matrix_world.to_quaternion() @ Vector((0, 0, -1))
            end = src.location.copy()
            start = end - fwd * param
            q = src.matrix_world.to_quaternion()
            for fk, t in ((f0, 0.0), (f0 + round((f1 - f0) * 0.6), 0.6), (f1, 1.0)):
                cam_obj.location = start.lerp(end, ease(t))
                cam_obj.rotation_quaternion = q
                cam_obj.keyframe_insert('location', frame=fk)
                cam_obj.keyframe_insert('rotation_quaternion', frame=fk)
        else:
            p = src.location
            radius = math.hypot(p.x - PIVOT.x, p.y - PIVOT.y)
            a0 = math.atan2(p.y - PIVOT.y, p.x - PIVOT.x)
            for i in range(7):
                t = i / 6
                fk = round(f0 + (f1 - f0) * t)
                ang = a0 + math.radians(param) * t
                loc = Vector((PIVOT.x + radius * math.cos(ang), PIVOT.y + radius * math.sin(ang), p.z))
                cam_obj.location = loc
                cam_obj.rotation_quaternion = (PIVOT - loc).normalized().to_track_quat('-Z', 'Y')
                cam_obj.keyframe_insert('location', frame=fk)
                cam_obj.keyframe_insert('rotation_quaternion', frame=fk)
    marks.append((f1, name))
    frame = f1 + 1

total = frame - 1
sc.frame_start, sc.frame_end = 1, total
print("REVIEW total_frames=%d duracao_s=%.1f" % (total, total / FPS))
os.makedirs(OUT, exist_ok=True)
if MODE == "frames":
    for i, (f, name) in enumerate(marks):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "%02d_%s.png" % (i, name.replace(">", "").replace("-", "_")))
        bpy.ops.render.render(write_still=True)
elif MODE == "walks":
    for i, (f, name) in enumerate(walk_marks):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "%03d_%s.jpg" % (i, name))
        sc.render.image_settings.file_format = 'JPEG'
        bpy.ops.render.render(write_still=True)
    print("WALKS_OK", len(walk_marks))
elif MODE == "seq":
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, "f_")
    bpy.ops.render.render(animation=True)
    print("SEQ_OK", OUT, total)
