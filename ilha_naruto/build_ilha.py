# build_ilha.py - reconstroi a Ilha 1 (Naruto) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_ilha.py -- [blockout] [sem=<zona,zona>]
#      IL_OUT=<caminho.blend> muda a saida (padrao ilha_naruto.blend)
#   il_core (colisao do chao + marcadores de mundo/minerio) roda sempre. Cada zona usa o modulo de detalhe quando
#   ele existe (ZONE_MODULES) e o blockout quando nao existe (ou com o argumento 'blockout').
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import il_lib as IL                  # poe o pipeline do lobby no sys.path
import bpy
import fm_lib
import il_layout as L
import il_scene
import il_core
import il_blockout

# zona -> modulos de detalhe (na ordem)
ZONE_MODULES = {
    "terrain": ["il_terrain"],
    "mining": ["il_mining"],
    "entrance": ["il_entrance"],
    "village": ["il_village"],
    "houses": ["il_houses"],
    "summon": ["il_summon"],
    "water": ["il_water"],
    "exit": ["il_exit"],              # ponte de saida, ilhota, interface (ancora)
    "gate_db": ["il_gate_db"],        # portao de compra Dragon Ball (na ilhota da saida)
    "gates": ["il_gates"],            # galeria dos 4 outros portoes de compra (fora da ilha)
    "dressing": ["il_props", "il_veg", "il_lights"],
}


def zone_ready(zone):
    return all(os.path.exists(os.path.join(HERE, m + ".py")) for m in ZONE_MODULES[zone])


def build(blockout=False, skip_zones=(), studio_zone=None):
    """monta a cena inteira. studio_zone: so essa zona usa o modulo de detalhe (as outras ficam em blockout)"""
    t0 = time.time()
    IL.reset_scene()
    fm_lib.make_materials()
    il_scene.setup(res=(1600, 900), samples=24)
    il_core.build()
    use = {}
    for zone in ZONE_MODULES:
        if zone in skip_zones:
            continue
        use[zone] = (zone == studio_zone) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    # blockout das zonas sem detalhe ANTES dos modulos (o dressing testa contra a geometria de todas as zonas)
    il_blockout.build(skip=set(detailed) | set(skip_zones))
    for zone in detailed:
        for m in ZONE_MODULES[zone]:
            t = time.time()
            importlib.import_module(m).build()
            print("%s %.1fs" % (m, time.time() - t))
    il_scene.sea()
    il_scene.islets()
    il_scene.clouds()
    il_scene.cameras()
    il_scene.scale_reference(visible=not detailed or bool(studio_zone))
    bpy.context.view_layer.update()
    return detailed, time.time() - t0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    skip = ()
    for a in argv:
        if a.startswith("sem="):
            skip = tuple(a[4:].split(","))
    OUT = os.environ.get("IL_OUT") or os.path.join(HERE, "ilha_naruto.blend")
    detailed, dt = build(blockout="blockout" in argv, skip_zones=skip)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    tris = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith("COL_"):
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUILD OK zonas_detalhadas=%s objs=%d tris=%d col=%d t=%.1fs -> %s" % (
        ",".join(detailed) or "-", len(bpy.data.objects), tris, ncol, dt, OUT))
