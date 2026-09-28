# build_sg.py - reconstroi a Ilha 3 (Shadow Garden) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_sg.py -- [blockout] [sem=<zona,zona>]
#      SG_OUT=<caminho.blend> muda a saida (padrao ilha_shadowgarden.blend)
#   sg_core (colisao andavel + TODOS os marcadores + portao Demon Slayer aprovado) roda sempre. Cada zona usa o modulo
#   de detalhe quando ele existe (ZONE_MODULES) e o blockout quando nao existe (ou com o argumento 'blockout').
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sg_lib as SL                  # poe o pipeline do lobby e das Ilhas 1 e 2 no sys.path
import bpy
import fm_lib
import sg_layout as L
import sg_scene
import sg_core
import sg_blockout

# zona -> modulos de detalhe (na ordem)
ZONE_MODULES = {
    "terrain": ["sg_terrain"],        # massa da ilha, patamares, arrimos, ombro, penhascos em coluna, montes
    "entry": ["sg_entry"],            # ponte de chegada, patio baixo, escadaria, 2 porticos, calcada alta
    "village": ["sg_village"],        # praca + fonte, ruas, 12 casas de meia-enxaimel (so ambientacao)
    "castle": ["sg_castle"],          # muralha + portao, nave (casca do Mining Hall), torres, torre-coroa
    "hall": ["sg_hall"],              # interior do Mining Hall (piso livre, pilastras, janelas, lustres, luz)
    "summon": ["sg_summon"],          # ponte + plataforma + torre de invocacao (familia das Ilhas 1 e 2)
    "craft": ["sg_craft"],            # pavilhao redondo do alquimista (interior + frasco gigante)
    "dungeon": ["sg_dungeon"],        # portaria com portal espiral + 3 salas modulares sob a ilha
    "water": ["sg_water"],            # 4 cachoeiras frias + fonte
    "exit": ["sg_exit"],              # ponte leste, ilhota do portao Demon Slayer, ancora
    "dressing": ["sg_veg", "sg_props", "sg_lights"],   # veg antes: os props consultam a vegetacao ja montada
}


def zone_ready(zone):
    return all(os.path.exists(os.path.join(HERE, m + ".py")) for m in ZONE_MODULES[zone])


def build(blockout=False, skip_zones=(), studio_zone=None, res=(1600, 900), samples=24):
    """monta a cena inteira. studio_zone: so essa zona usa o modulo de detalhe (as outras ficam em blockout)"""
    t0 = time.time()
    SL.reset_scene()
    fm_lib.make_materials()
    sg_scene.setup(res=res, samples=samples)
    sg_core.build()
    use = {}
    for zone in ZONE_MODULES:
        if zone in skip_zones:
            continue
        use[zone] = (zone == studio_zone) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    sg_blockout.build(skip=set(detailed) | set(skip_zones))
    for zone in detailed:
        for m in ZONE_MODULES[zone]:
            t = time.time()
            importlib.import_module(m).build()
            print("%s %.1fs" % (m, time.time() - t))
    fm_lib.make_materials()           # materiais registrados pelos modulos depois do primeiro make
    sg_scene.tone_emissives()
    sg_scene.sea()
    sg_scene.islets()
    sg_scene.clouds()
    sg_scene.moon()
    sg_scene.cameras()
    sg_scene.scale_reference(visible=not detailed or bool(studio_zone))
    bpy.context.view_layer.update()
    return detailed, time.time() - t0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    skip = ()
    for a in argv:
        if a.startswith("sem="):
            skip = tuple(a[4:].split(","))
    OUT = os.environ.get("SG_OUT") or os.path.join(HERE, "ilha_shadowgarden.blend")
    detailed, dt = build(blockout="blockout" in argv, skip_zones=skip)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    tris = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith("COL_"):
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUILD OK zonas_detalhadas=%s objs=%d tris=%d col=%d t=%.1fs -> %s" % (
        ",".join(detailed) or "-", len(bpy.data.objects), tris, ncol, dt, OUT))
