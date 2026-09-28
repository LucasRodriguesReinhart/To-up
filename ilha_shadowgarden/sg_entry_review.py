# sg_entry_review - SO PREVIA DE REVISAO da zona entry (nao entra no build nem no export).
# Por que existe: no BLOCKOUT do terreno o "ombro" da ilha e um prisma unico no contorno inteiro com topo em P1 - 2
# (34,2), que ENTERRA o patio baixo (DECK 28,2), o pe da escadaria e o portico A. Enquanto o sg_terrain nao existe,
# a revisao na altura do jogador fica impossivel. Este script roda o studio_sg.py identico, so trocando, na previa, o
# ombro do blockout ao sul de y -186 por um ombro rebaixado (DECK + 2, a cota do labio da cachoeira sul da planta) com
# o canal do patio (|x| < 13) e da escadaria (|x| < 10,4) aberto. Mesmos argumentos do studio_sg.py.
#   blender -b --factory-startup --python sg_entry_review.py -- entry <pasta> [--cams ...] [--res 960x540]
import sys, os, runpy
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_lib as SL
import bpy, bmesh
import sg_layout as L
import sg_blockout
from il_lib import clip, ccw

_orig_terrain = sg_blockout.terrain


def _preview_terrain():
    _orig_terrain()
    ob = bpy.data.objects.get("SG_Ter_Blockout_Shoulder")
    if ob is None:
        return
    # apaga so o prisma do contorno (faces com todos os vertices em z 32,5 ou 34,2); os montes ficam
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    lv = (32.5, L.P1 - 2.3, L.P1 - 2.0)
    dead = [f for f in bm.faces if all(min(abs(v.co.z - z) for z in lv) < 1e-3 for v in f.verts)]
    bmesh.ops.delete(bm, geom=dead, context="FACES")
    bm.to_mesh(ob.data)
    bm.free()
    # massa inferior: a 1a banda (-14 .. 32,5) tambem cobre o patio; sai inteira e volta abaixo de 18 + pecas acima
    ob2 = bpy.data.objects.get("SG_Ter_Blockout_Under")
    if ob2 is not None:
        bm = bmesh.new()
        bm.from_mesh(ob2.data)
        lv2 = (-14.0, 32.5)
        dead = [f for f in bm.faces if all(min(abs(v.co.z - z) for z in lv2) < 1e-3 for v in f.verts)]
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        bm.to_mesh(ob2.data)
        bm.free()
    rim = SL.rim()
    mb = SL.MB("SG_Ter_PreviewShoulder", "02_TERRAIN", None, detail="far", floor=-999)
    north = clip(rim, 0.0, -1.0, 186.0)                         # y >= -186: igual ao blockout
    SL.prism(mb, ccw(north), -14.0, L.P1 - 2.0, "Cliff_Rock_SG", top_m="Grass_SG")
    low = clip(rim, 0.0, 1.0, -186.0)                           # y <= -186: rebaixado
    SL.prism(mb, ccw(low), -14.0, 18.0, "Cliff_Rock_SG")
    for sx in (-1.0, 1.0):
        a = clip(clip(low, 0.0, 1.0, L.ENTRY_STAIR[1]), -sx, 0.0, -L.ENTRY_LOW[2])      # ao lado do patio
        b = clip(clip(clip(low, 0.0, -1.0, -L.ENTRY_STAIR[1]), -sx, 0.0, -10.4), 0, 1, -186.0)   # ao lado da escada
        for poly in (a, b):
            if len(poly) >= 3 and abs(SL.area(poly)) > 1.0:
                SL.prism(mb, ccw(poly), 18.0, L.DECK + 2.0, "Cliff_Rock_SG", top_m="Grass_SG")
    mb.finish()
    print("REVIEW ombro do blockout rebaixado na entrada (so previa)")


sg_blockout.terrain = _preview_terrain
runpy.run_path(os.path.join(HERE, "studio_sg.py"), run_name="__main__")
