# build_sg.py - reconstroi a Ilha 3 (Shadow Garden) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_sg.py -- [blockout] [sem=<zona,zona>]
#      SG_OUT=<caminho.blend> muda a saida (padrao ilha_shadowgarden.blend)
#   sg_core (colisao andavel + TODOS os marcadores + portao Demon Slayer aprovado) roda sempre. Cada zona usa o modulo
#   de detalhe quando ele existe (ZONE_MODULES) e o blockout quando nao existe (ou com o argumento 'blockout').
# PLANTA v4 (ONDA 0, plano mestre renders/plano_mestre/PLANO.md):
#   - zonas que MUDAM DE ESCALA ou de forma ficam em BLOCKOUT v4 ate a onda 1 refazer o modulo: terreno (ilha nova),
#     vila (7 casas visitaveis; a praca/fonte da v3 entra realocada), castelo 2x, salao 2x + trono movel, SALAO
#     SOMBRIO (zona nova 'cave'), masmorra 3x, agua (so a pedra das bicas) e vestir (patio-jardim/mirante simples);
#   - zonas que SO MUDAM DE LUGAR rodam o modulo da v3 pelo sg_relocate (referencial v3 + transformacao rigida):
#     entrada (a ponte curva ate ela e do blockout), invocacao, alquimia e saida (giro de 120 para o noroeste).
#   Onda 1: quando um modulo for refeito na v4, ponha-o em ZONE_MODULES e tire de LEGACY. Nao apague codigo de detalhe.
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

# zona -> modulos de detalhe (na ordem); lista vazia = BLOCKOUT v4
ZONE_MODULES = {
    "terrain": [],                    # v4: ilha nova (onda 1 refaz sg_terrain)
    "entry": ["sg_entry"],            # v3 realocada (so o fim da ponte, patio, escadaria e porticos)
    "village": [],                    # v4: 7 casas visitaveis (onda 1 refaz sg_village); praca da v3 realocada
    "castle": [],                     # v4: castelo 2x (onda 1 refaz sg_castle)
    "hall": [],                       # v4: salao 2x + trono movel (onda 1 refaz sg_hall)
    "cave": [],                       # v4 NOVO: salao sombrio + escada caracol (onda 1 cria sg_cave)
    "summon": ["sg_summon"],          # v3 realocada
    "craft": ["sg_craft"],            # v3 realocada
    "dungeon": [],                    # v4: salas 3x (onda 1 refaz sg_dungeon)
    "water": [],                      # v4: agua no Roblox; o blockout faz so a pedra das bicas
    "exit": ["sg_exit"],              # v3 realocada (giro 120, +8 de cota) para a ponta noroeste
    "dressing": [],                   # v4: patio-jardim/mirante simples (onda 2 refaz sg_court/sg_veg/sg_garden)
}
# modulos da v3 que rodam pelo sg_relocate (referencial v3 -> planta v4)
LEGACY = ("sg_entry", "sg_summon", "sg_craft", "sg_exit")


def zone_ready(zone):
    ms = ZONE_MODULES[zone]
    return bool(ms) and all(os.path.exists(os.path.join(HERE, m + ".py")) for m in ms)


def load_module(m):
    if m in LEGACY:
        import sg_relocate
        return sg_relocate.load(m)
    return importlib.import_module(m)


def run_module(m):
    """roda o modulo de detalhe (os da v3 pelo sg_relocate) e o que a zona precisa em volta dele"""
    if m in LEGACY:
        import sg_relocate
        mod, made = sg_relocate.run(m)
    else:
        mod = importlib.import_module(m)
        mod.build()
    if m == "sg_entry":
        sg_blockout.entry_bridge(y_end=L.Y_ENTRY - 34.0)      # a ponte curva da ancora ate o trecho do sg_entry
    return mod


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
        use[zone] = (zone == studio_zone and zone_ready(zone)) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    sg_blockout.build(skip=set(detailed) | set(skip_zones))
    for zone in detailed:
        for m in ZONE_MODULES[zone]:
            t = time.time()
            run_module(m)
            print("%s %.1fs" % (m, time.time() - t))
    fm_lib.make_materials()           # materiais registrados pelos modulos depois do primeiro make
    sg_scene.tone_emissives()
    sg_scene.sea()
    sg_scene.islets()
    sg_scene.clouds()
    sg_scene.moon()
    sg_scene.neighbors()
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
