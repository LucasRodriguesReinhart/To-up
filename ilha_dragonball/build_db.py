# build_db.py - reconstroi a Ilha 2 (Dragon Ball) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_db.py -- [blockout] [sem=<zona,zona>]
#      DB_OUT=<caminho.blend> muda a saida (padrao ilha_dragonball.blend)
#   db_core (colisao andavel + marcadores + minerio + portao Shadow Garden aprovado) roda sempre. Cada zona usa o modulo
#   de detalhe quando ele existe (ZONE_MODULES) e o blockout quando nao existe (ou com o argumento 'blockout').
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import db_lib as DL                  # poe o pipeline do lobby e da Ilha 1 no sys.path
import bpy
import fm_lib
import db_layout as L
import db_scene
import db_core
import db_blockout

# zona -> modulos de detalhe (na ordem)
ZONE_MODULES = {
    "terrain": ["db_terrain"],        # massa da ilha, penhascos, mesas/pilares, terracos, chao, recortes
    "mining": ["db_mining"],          # bacia de canion, promenade, acessos, rochas da arena, pod central
    "entrance": ["db_entrance"],      # ponte de chegada, escadaria, portal Capsule, praca
    "capsule": ["db_capsule"],        # Capsule (heroi) com interior + anexos
    "village": ["db_village"],        # casas-capsula, mercado marcial, oficina, pods, dojo
    "towers": ["db_towers"],          # torres, satelites andaveis, passarelas de vidro, heliponto
    "summon": ["db_summon"],          # torre de invocacao (familia da Ilha 1) + praca DB
    "water": ["db_water"],            # 3 pocos, 2 quedas pela borda, cascata da mesa NW
    "exit": ["db_exit"],              # trilha, arco natural, ponte de saida, ilhota do portao SG, ancora, transicao
    "dressing": ["db_veg", "db_props", "db_lights"],   # veg antes: os props consultam a vegetacao ja montada
}


def zone_ready(zone):
    return all(os.path.exists(os.path.join(HERE, m + ".py")) for m in ZONE_MODULES[zone])


def build(blockout=False, skip_zones=(), studio_zone=None, res=(1600, 900), samples=24):
    """monta a cena inteira. studio_zone: so essa zona usa o modulo de detalhe (as outras ficam em blockout)"""
    t0 = time.time()
    DL.reset_scene()
    fm_lib.make_materials()
    db_scene.setup(res=res, samples=samples)
    db_core.build()
    use = {}
    for zone in ZONE_MODULES:
        if zone in skip_zones:
            continue
        use[zone] = (zone == studio_zone) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    db_blockout.build(skip=set(detailed) | set(skip_zones))
    for zone in detailed:
        for m in ZONE_MODULES[zone]:
            t = time.time()
            importlib.import_module(m).build()
            print("%s %.1fs" % (m, time.time() - t))
    fm_lib.make_materials()           # materiais registrados pelos modulos depois do primeiro make
    db_scene.tone_emissives()
    db_scene.sea()
    db_scene.islets()
    db_scene.clouds()
    db_scene.cameras()
    db_scene.scale_reference(visible=not detailed or bool(studio_zone))
    bpy.context.view_layer.update()
    return detailed, time.time() - t0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    skip = ()
    for a in argv:
        if a.startswith("sem="):
            skip = tuple(a[4:].split(","))
    OUT = os.environ.get("DB_OUT") or os.path.join(HERE, "ilha_dragonball.blend")
    detailed, dt = build(blockout="blockout" in argv, skip_zones=skip)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    tris = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith("COL_"):
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUILD OK zonas_detalhadas=%s objs=%d tris=%d col=%d t=%.1fs -> %s" % (
        ",".join(detailed) or "-", len(bpy.data.objects), tris, ncol, dt, OUT))
