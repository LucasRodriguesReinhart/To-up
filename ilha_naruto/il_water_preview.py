# il_water_preview - SO REVISAO da zona water (nao entra no build, nao grava .blend).
# Abre um build integrado (IL_OUT da pasta _studio/water), abre no terreno VISUAL o que o contrato TERRENO x AGUA
# manda o terreno abrir (leito do riacho do vale = il_col.stream_bed_poly ate L.STREAM_BED, nicho da bica 3x3 no
# muro x=108) com booleanas temporarias - enquanto o terreno detalhado nao traz esses cortes - e renderiza as cameras
# de il_water.CAMS pedidas (ou vistas avulsas nome:x,y,z:tx,ty,tz[:lente]).
# uso: blender -b <_studio/water/int.blend> --python il_water_preview.py -- <pasta> [CAM_Water_A,CAM_Water_B]
#      [nome:x,y,z:tx,ty,tz[:lente] ...] [--res 1280x720] [--nocut]
import sys, os, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy
from mathutils import Vector
import il_layout as L


def cutters():
    import il_col
    mb = IL.MB("TMP_WaterPreviewCut", "00_REFERENCE", detail="far", floor=-999)
    bed = IL.clip(il_col.stream_bed_poly(), -1.0, 0.0, -L.SPOUT[0])     # o leito encosta na face do muro x=108
    mb.prism(IL.ccw(bed), L.STREAM_BED, L.G + 3.0, "BLK_Mass")
    sx, sy, sz = L.SPOUT
    mb.box((2.5, 3.0, 3.0), (sx - 1.2, sy, sz), (0, 0, 0), "BLK_Mass", 0.0)
    ob = mb.finish()
    ob.hide_render = True
    return ob


def carve(cut):
    n = 0
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.name.startswith(("TER_Ground", "TER_Retaining", "TER_Cliffs_Upper", "TER_Grass",
                                                       "TER_Valley", "TER_Paths")):
            continue
        m = o.modifiers.new("PreviewWaterCut", "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.object = cut
        try:
            m.solver = "EXACT"
            m.use_hole_tolerant = True
        except Exception:
            pass
        n += 1
    print("PREVIEW cortes em %d objetos" % n)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = argv[0]
    res = (1280, 720)
    if "--res" in argv:
        w, h = argv[argv.index("--res") + 1].split("x")
        res = (int(w), int(h))
    os.makedirs(out, exist_ok=True)
    import il_water as W
    if "--nocut" not in argv:
        carve(cutters())
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.eevee.taa_render_samples = 12
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    views = []
    for a in argv[1:]:
        if a.startswith("--") or (a.replace("x", "").isdigit()):
            continue
        if a.count(":") >= 2:
            p = a.split(":")
            views.append((p[0], Vector([float(v) for v in p[1].split(",")]), Vector([float(v) for v in p[2].split(",")]),
                          float(p[3]) if len(p) > 3 else 20.0))
        else:
            for n in a.split(","):
                if n in W.CAMS:
                    loc, tgt, lens = W.CAMS[n]
                    views.append((n, Vector(loc), Vector(tgt), lens))
    for name, loc, tgt, lens in views:
        cd = bpy.data.cameras.new("tmp_" + name)
        cd.lens = lens
        cd.clip_end = 4000
        ob = bpy.data.objects.new("tmp_" + name, cd)
        sc.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
        sc.camera = ob
        sc.render.filepath = os.path.join(out, name + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("PREVIEW RENDER", sc.render.filepath)


main()
