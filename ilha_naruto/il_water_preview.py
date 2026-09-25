# il_water_preview - SO REVISAO da zona water (nao salva nada, nao entra no build).
# Monta a cena como o studio (water em detalhe, resto em blockout), abre o leito do riacho do vale no terreno com uma
# booleana (o terreno detalhado recebe o mesmo corte: L.STREAM ate L.STREAM_BED), testa a travessia da ponte em arco
# com o andador do QA e renderiza as cameras pedidas.
#   --terrain : usa o modulo de detalhe do terreno (il_terrain, do agente de terreno; so leitura) no lugar do
#               blockout do terreno, para conferir as quedas contra as sangrias e os sulcos reais do penhasco
# uso: blender -b --factory-startup --python il_water_preview.py -- <pasta_saida> [--cams A,B] [--res 960x540]
#      [--terrain]
import sys, os, math, importlib, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL
import bpy
import fm_lib
from mathutils import Vector
import il_layout as L
import il_scene
import il_core
import il_blockout
import build_ilha as B


def build_scene(with_terrain):
    if not with_terrain:
        B.build(studio_zone="water")
        return "blockout"
    IL.reset_scene()
    fm_lib.make_materials()
    il_scene.setup(res=(1600, 900), samples=24)
    il_core.build()
    used = False
    try:
        importlib.import_module("il_terrain").build()
        used = True
    except Exception:
        traceback.print_exc()
        print("PREVIEW il_terrain falhou: terreno em blockout")
    import il_water
    il_water.build()
    il_blockout.build(skip={"water"} | ({"terrain"} if used else set()))
    il_scene.sea()
    il_scene.islets()
    il_scene.clouds()
    il_scene.cameras()
    il_scene.scale_reference(visible=True)
    bpy.context.view_layer.update()
    return "il_terrain" if used else "blockout"


def carve():
    import il_water as W
    mb = IL.MB("TMP_WaterBedCutter", "00_REFERENCE", detail="far", floor=-999)
    # o mesmo tracado do terreno detalhado: L.STREAM no vale, passando 8 studs alem da borda SE
    pts = W.chaikin(W.STREAM_G, 2)
    (x0, y0), (x1, y1) = W.STREAM_G[-2], W.STREAM_G[-1]
    d = Vector((x1 - x0, y1 - y0, 0)).normalized()
    pts = pts + [(x1 + d.x * 8.0, y1 + d.y * 8.0)]
    W.water_strip(mb, pts, L.G + 2.0, L.STREAM_W + 0.6, L.G + 2.0 - L.STREAM_BED, "BLK_Mass")
    cut = mb.finish()
    cut.hide_render = True
    for name in ("TER_Ground", "TER_Island_Base"):
        t = bpy.data.objects.get(name)
        if not t:
            continue
        m = t.modifiers.new("PreviewStreamBed", "BOOLEAN")
        m.operation = "DIFFERENCE"
        for k, v in (("use_self", True), ("use_hole_tolerant", True)):
            try:
                setattr(m, k, v)
            except Exception:
                pass
        m.object = cut
        try:
            m.solver = "EXACT"
        except Exception:
            pass
    return cut


def walk_bridge():
    import fm_qa
    import il_water as W
    c, u = W.footbridge_frame()
    a = c - u * (W.FB_LEN / 2 + 4.0)
    b = c + u * (W.FB_LEN / 2 + 4.0)
    bvh, n = fm_qa.col_bvh()
    f, z = fm_qa.walk(bvh, [(a.x, a.y), (c.x, c.y), (b.x, b.y)], L.G)
    print("PREVIEW PONTE SE->LESTE", "OK" if not f else "FAIL %s" % f, "z_fim=%.2f" % z)
    f, z = fm_qa.walk(bvh, [(b.x, b.y), (c.x, c.y), (a.x, a.y)], L.G)
    print("PREVIEW PONTE LESTE->SE", "OK" if not f else "FAIL %s" % f, "z_fim=%.2f" % z)
    # ponto mais alto do tabuleiro
    g = fm_qa.ground(bvh, c.x, c.y, L.G + W.FB_RISE)
    print("PREVIEW PONTE topo do tabuleiro (colisao) z=%.2f" % (g or -1))


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = argv[0]
    res = (960, 540)
    cams = None
    for i, a in enumerate(argv):
        if a == "--res":
            w, h = argv[i + 1].split("x")
            res = (int(w), int(h))
        if a == "--cams":
            cams = [c for c in argv[i + 1].split(",") if c]
    os.makedirs(out, exist_ok=True)
    print("PREVIEW terreno:", build_scene("--terrain" in argv))
    import il_water as W
    for n, v in W.CAMS.items():
        IL.camera(n, v[0], v[1], v[2] if len(v) > 2 else 20)
    carve()
    walk_bridge()
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.eevee.taa_render_samples = 16
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 88
    for cn in (cams or list(W.CAMS)):
        ob = bpy.data.objects.get(cn)
        if not ob:
            print("PREVIEW camera inexistente:", cn)
            continue
        sc.camera = ob
        sc.render.filepath = os.path.join(out, cn + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("PREVIEW RENDER", sc.render.filepath)


main()
