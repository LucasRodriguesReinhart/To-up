# il_review_cam.py - monta uma camera de video (dolly/orbit) passeando pela ilha, a partir das CAM_* existentes,
# para gerar um video de revisao rapido (nao entra no export do jogo).
# uso: blender -b ilha_naruto.blend --python il_review_cam.py -- <modo> <saida>
#   modo = "frames" <pasta>  -> renderiza so o ULTIMO frame de cada plano (PNG), para conferir o enquadramento
#   modo = "seq"    <pasta>  -> renderiza a sequencia PNG inteira (este Blender nao tem o codec FFMPEG embutido;
#                               o video final e montado depois com ffmpeg, ex.: pacote python imageio-ffmpeg)
#
# depois do "seq", monta o mp4 (ffmpeg do imageio-ffmpeg: python -c "import imageio_ffmpeg;
# print(imageio_ffmpeg.get_ffmpeg_exe())"):
#   ffmpeg -y -framerate 24 -i "<pasta>/f_%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 20 -preset medium \
#       -movflags +faststart saida.mp4
#
# SHOTS embaixo e a lista de planos (camera existente, dolly ou orbit, duracao, recuo/varredura); ajuste ali
# para um tour diferente. Nao salva o .blend (so le e renderiza).
import sys, os, math, bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
MODE = argv[0]
OUT = argv[1]
FPS = 24
sc = bpy.context.scene
sc.render.fps = FPS
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.eevee.taa_render_samples = 32 if MODE == "frames" else 12

# (nome_da_camera_existente, tipo, duracao_s, pullback_studs_OU_sweep_graus)
SHOTS = [
    ("CAM_Front",      "dolly", 3.0,  70.0),   # chegada: ilha inteira ao longe
    ("CAM_Entry",      "dolly", 2.8,  30.0),   # atravessa o portao da entrada
    ("CAM_Center",     "dolly", 2.4,  20.0),   # entra no anel / fosso
    ("CAM_Mining",     "dolly", 3.0,  22.0),   # area de mineracao
    ("CAM_Village",    "dolly", 3.0,  24.0),   # vila / salao principal
    ("CAM_Summon",     "dolly", 3.0,  20.0),   # torre do summon
    ("CAM_NextBridge", "dolly", 3.0,  26.0),   # ponte de saida
    ("CAM_DB_Gate",    "dolly", 3.0,  16.0),   # portao de compra Dragon Ball
    ("CAM_Gates_Row",  "dolly", 3.0,  32.0),   # galeria dos 4 portoes
    ("CAM_Ref15",      "orbit", 4.0,  35.0),   # giro aereo 3/4
    ("CAM_BirdEye",    "orbit", 4.5,  40.0),   # giro final de cima
]
PIVOT = Vector((0.0, 0.0, 18.0))


def ease(t):
    return 1.0 - (1.0 - t) * (1.0 - t)


# interpolacao linear em TODO keyframe novo (sem overshoot de bezier nos cortes entre planos); evita depender de
# action.fcurves, que mudou no sistema de Actions em camadas do Blender 4.4+/5.x
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'

cam_data = bpy.data.cameras.new("ReviewCamData")
cam_obj = bpy.data.objects.new("CAM_ReviewVideo", cam_data)
sc.collection.objects.link(cam_obj)
cam_obj.rotation_mode = 'QUATERNION'
sc.camera = cam_obj

frame = 1
mark_frames = []   # (frame, nome_do_plano) para o modo "frames"
for name, kind, dur, param in SHOTS:
    src = bpy.data.objects.get(name)
    if src is None:
        print("AVISO camera ausente:", name)
        continue
    n = max(2, round(dur * FPS))
    f0, f1 = frame, frame + n - 1
    cam_data.lens = src.data.lens
    if kind == "dolly":
        end_loc = src.location.copy()
        quat = src.matrix_world.to_quaternion()
        back = quat @ Vector((0.0, 0.0, 1.0))          # +Z local = "para tras" da camera
        start_loc = end_loc + back * param
        cam_obj.rotation_quaternion = quat
        cam_obj.keyframe_insert('rotation_quaternion', frame=f0)
        cam_obj.keyframe_insert('rotation_quaternion', frame=f1)
        cam_obj.location = start_loc
        cam_obj.keyframe_insert('location', frame=f0)
        fm = f0 + round((f1 - f0) * 0.6)
        cam_obj.location = start_loc.lerp(end_loc, ease(0.6))
        cam_obj.keyframe_insert('location', frame=fm)
        cam_obj.location = end_loc
        cam_obj.keyframe_insert('location', frame=f1)
    else:  # orbit
        p = src.location
        radius = math.hypot(p.x - PIVOT.x, p.y - PIVOT.y)
        a0 = math.atan2(p.y - PIVOT.y, p.x - PIVOT.x)
        sweep = math.radians(param)
        nsub = 5
        for i in range(nsub):
            t = i / (nsub - 1)
            fk = round(f0 + (f1 - f0) * t)
            ang = a0 + sweep * t
            loc = Vector((PIVOT.x + radius * math.cos(ang), PIVOT.y + radius * math.sin(ang), p.z))
            direction = (PIVOT - loc).normalized()
            quat = direction.to_track_quat('-Z', 'Y')
            cam_obj.location = loc
            cam_obj.keyframe_insert('location', frame=fk)
            cam_obj.rotation_quaternion = quat
            cam_obj.keyframe_insert('rotation_quaternion', frame=fk)
    mark_frames.append((f1, name))
    frame = f1 + 1

total = frame - 1
sc.frame_start, sc.frame_end = 1, total
print("REVIEW total_frames=%d duracao_s=%.1f" % (total, total / FPS))

if MODE == "frames":
    os.makedirs(OUT, exist_ok=True)
    for i, (f, name) in enumerate(mark_frames):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(OUT, "%02d_%s.png" % (i, name))
        bpy.ops.render.render(write_still=True)
        print("FRAME", name, f)
elif MODE == "seq":
    # este build do Blender nao tem o codec FFMPEG embutido (so formatos de imagem): renderiza PNG e o
    # ffmpeg (pacote imageio-ffmpeg) encoda depois.
    os.makedirs(OUT, exist_ok=True)
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, "f_")
    bpy.ops.render.render(animation=True)
    print("SEQ_OK", OUT, total)
