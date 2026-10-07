# build_ds.py - reconstroi a Ilha 4 (DEMON SLAYER) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_ds.py -- [blockout] [proxies] [sem=<zona,zona>]
#      DS_OUT=<caminho.blend> muda a saida (padrao ilha_demonslayer.blend)
#   ds_core (colisao andavel + TODOS os marcadores + portao One Piece aprovado) roda sempre. Cada zona usa o modulo de
#   detalhe quando ele existe (ZONE_MODULES) e o blockout quando nao existe (ou com o argumento 'blockout').
#   'proxies' poe proxies MUITO simples de minerio (DS_Clr_OreProxy) so para a revisao visual do blockout; o export
#   apaga (NUNCA entram no jogo).
# ONDA 0 (plano/PLANO_DS.md): todas as zonas em BLOCKOUT. Onda 1+: ponha o modulo em ZONE_MODULES quando existir.
import sys, os, time, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ds_lib as DL                  # poe o pipeline do lobby e das Ilhas 1 e 2 no sys.path
import bpy
import fm_lib
import ds_layout as L
import ds_scene
import ds_core
import ds_blockout

# zona -> modulos de detalhe (na ordem); lista vazia = BLOCKOUT
ZONE_MODULES = {
    "terrain": ["ds_terrain"],        # onda 1a
    "entry": ["ds_entry"],            # onda 1c
    "village": ["ds_village"],        # onda 2a (precisa do ds_kit, onda 1b)
    "clearing": [],                   # chao da clareira: do ds_terrain (onda 1a); bordas: ds_props/ds_veg (onda 3)
    "forge": ["ds_forge"],            # onda 2b
    "summon": ["ds_summon"],          # onda 1d
    "water": ["ds_water"],            # onda 2c
    "exit": ["ds_exit"],              # onda 1c
    "dressing": ["ds_veg", "ds_props", "ds_vfx", "ds_lights"],   # onda 3 (ds_vfx: acrescimo 3c; ds_lights por ultimo:
                                                                 # passe GLOBAL sobre as luzes de todas as zonas)
}


def zone_ready(zone):
    ms = ZONE_MODULES[zone]
    return bool(ms) and all(os.path.exists(os.path.join(HERE, m + ".py")) for m in ms)


def run_module(m):
    mod = importlib.import_module(m)
    mod.build()
    return mod


def build(blockout=False, skip_zones=(), studio_zone=None, res=(1600, 900), samples=24, ore_proxies=False):
    """monta a cena inteira. studio_zone: so essa zona usa o modulo de detalhe (as outras ficam em blockout)"""
    t0 = time.time()
    # 6c: o mathutils.noise do Blender 5.2 sorteia a tabela a cada processo (noise_vector muda entre 2 execucoes): o
    # MB.rock (montes de carvao da fornalha) saia diferente a cada build. Semente fixa -> build reprodutivel
    from mathutils import noise as _noise
    _noise.seed_set(4402)
    DL.reset_scene()
    fm_lib.make_materials()
    ds_scene.setup(res=res, samples=samples)
    ds_core.build()
    use = {}
    for zone in ZONE_MODULES:
        if zone in skip_zones:
            continue
        use[zone] = (zone == studio_zone and zone_ready(zone)) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    ds_blockout.build(skip=set(detailed) | set(skip_zones), ore_proxies=ore_proxies)
    for zone in detailed:
        for m in ZONE_MODULES[zone]:
            t = time.time()
            run_module(m)
            print("%s %.1fs" % (m, time.time() - t))
    fm_lib.make_materials()           # materiais registrados pelos modulos depois do primeiro make
    ds_scene.tone_emissives()
    ds_scene.clouds()
    ds_scene.moon()
    ds_scene.neighbors()
    ds_scene.cameras()
    ds_scene.scale_reference(visible=not detailed or bool(studio_zone))
    bpy.context.view_layer.update()
    return detailed, time.time() - t0


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    skip = ()
    for a in argv:
        if a.startswith("sem="):
            skip = tuple(a[4:].split(","))
    OUT = os.environ.get("DS_OUT") or os.path.join(HERE, "ilha_demonslayer.blend")
    detailed, dt = build(blockout="blockout" in argv, skip_zones=skip, ore_proxies="proxies" in argv)
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    tris = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith(("COL_", "PREVIEW_", "SCALE_")):
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUILD OK zonas_detalhadas=%s objs=%d tris=%d col=%d t=%.1fs -> %s" % (
        ",".join(detailed) or "-", len(bpy.data.objects), tris, ncol, dt, OUT))
