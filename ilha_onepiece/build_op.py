# build_op.py - reconstroi a Ilha 5 (ONE PIECE / WANO) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_op.py -- [blockout] [proxies] [sem=<zona,zona>]
#      OP_OUT=<caminho.blend> muda a saida (padrao ilha_onepiece.blend)
#   op_core (colisao andavel + TODOS os marcadores + portao One Punch Man da galeria) roda sempre. Cada zona usa o
#   modulo de detalhe quando ele existe (ZONE_MODULES) e o blockout quando nao existe (ou com o argumento 'blockout').
#   'proxies' poe proxies MUITO simples de minerio (OP_Plz_OreProxy) so para a revisao visual do blockout; o export
#   apaga (NUNCA entram no jogo).
# M1 (plano/PLANO_OP.md): todas as zonas em BLOCKOUT. M2+: ponha o modulo em ZONE_MODULES quando existir.
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import op_lib as DL                  # poe o pipeline do lobby e das Ilhas 1 e 2 no sys.path
import bpy
import fm_lib
import op_layout as L
import op_scene
import op_core
import op_blockout

# zona -> modulos de detalhe (na ordem); lista vazia = BLOCKOUT
ZONE_MODULES = {
    "terrain": [],        # M4 op_terrain
    "entry": [],          # M2/M4 op_entry
    "capital": [],        # M2 (trecho de qualidade) -> M4 op_capital (precisa do op_kit)
    "plaza": [],          # M2 (transicao rua -> praca) op_plaza
    "castle": [],         # M3 op_castle
    "tree": [],           # M3 op_tree
    "summon": [],         # M3 op_summon (torre AMS por alias, como o ds_summon)
    "harbor": [],         # M3 op_harbor
    "ship": [],           # M3 op_ship
    "water": [],          # M4 op_water
    "exit": [],           # M4 op_exit
    "landmarks": [],      # M4 op_landmarks
    "dressing": [],       # M4/M6 op_veg, op_props, op_vfx, op_lights
}


def zone_ready(zone):
    ms = ZONE_MODULES[zone]
    return bool(ms) and all(os.path.exists(os.path.join(HERE, m + ".py")) for m in ms)


def run_module(m):
    mod = importlib.import_module(m)
    mod.build()
    return mod


def build(blockout=False, skip_zones=(), studio_zone=None, res=(1600, 900), samples=24, ore_proxies=False):
    t0 = time.time()
    from mathutils import noise as _noise
    _noise.seed_set(5505)
    DL.reset_scene()
    fm_lib.make_materials()
    op_scene.setup(res=res, samples=samples)
    op_core.build()
    use = {}
    for zone in ZONE_MODULES:
        if zone in skip_zones:
            continue
        use[zone] = (zone == studio_zone and zone_ready(zone)) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    op_blockout.build(skip=set(detailed) | set(skip_zones), ore_proxies=ore_proxies)
    for zone in detailed:
        for m in ZONE_MODULES[zone]:
            t = time.time()
            run_module(m)
            print("%s %.1fs" % (m, time.time() - t))
    fm_lib.make_materials()
    op_scene.tone_emissives()
    op_scene.sea()
    op_scene.neighbors()
    op_scene.cameras()
    op_scene.scale_reference(visible=not detailed or bool(studio_zone))
    bpy.context.view_layer.update()
    return detailed, time.time() - t0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    skip = ()
    for a in argv:
        if a.startswith("sem="):
            skip = tuple(a[4:].split(","))
    OUT = os.environ.get("OP_OUT") or os.path.join(HERE, "ilha_onepiece.blend")
    detailed, dt = build(blockout="blockout" in argv, skip_zones=skip, ore_proxies="proxies" in argv)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    tris = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith(("COL_", "PREVIEW_", "SCALE_")):
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUILD OK zonas_detalhadas=%s objs=%d tris=%d col=%d t=%.1fs -> %s" % (
        ",".join(detailed) or "-", len(bpy.data.objects), tris, ncol, dt, OUT))
