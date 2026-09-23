# fm_mat_preview - troca o modo de preview dos materiais num .blend ja montado (nao salva o arquivo)
# uso: FM_MAT_PREVIEW=roblox blender -b lobby.blend --python fm_mat_preview.py --python render.py -- <pasta> CAM_...
#      modos: rico (padrao do build), liso, legado, roblox (cor calibrada que o Roblox recebe, sem ruido/textura)
import sys, os, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fm_lib

# os modulos registram os materiais proprios (MATS.setdefault) na importacao, como no build.py
for m in ["fm_parts", "fm_layout", "fm_terrain", "fm_scene", "fm_forge", "fm_mine", "fm_water", "fm_buildings",
          "fm_portals", "fm_konoha", "fm_props", "fm_veg", "fm_lights"]:
    if os.path.exists(os.path.join(HERE, m + ".py")):
        try:
            importlib.import_module(m)
        except Exception as e:
            print("fm_mat_preview: nao importou", m, e)

mode = os.environ.get("FM_MAT_PREVIEW", "roblox")
n = fm_lib.apply_preview(mode)
print("FM_MAT_PREVIEW=%s aplicado em %d materiais" % (mode, n))
