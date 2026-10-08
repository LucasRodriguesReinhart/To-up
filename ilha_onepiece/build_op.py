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
    "terrain": ["op_terrain"],  # M4 op_terrain (agente do terreno: falesias em massas, rochedo do castelo, arrimos, pele)
    "entry": ["op_entry"],      # M2 op_entry (agente entrada+summon: ponte 120 em arcos, grande torii, patio, escada)
    "capital": ["op_capital"],  # M4 op_capital (agente da capital): chama o trecho M2 (op_m2_trecho, intacto) + capital inteira
    "plaza": ["op_m2_praca", "op_plaza"],  # M2 faixa sul + emblema (op_m2_praca, intacto) + M4 op_plaza (agente da praca: resto do piso em aneis/eixo/campos + borda; remove o piso provisorio)
    "castle": ["op_castle"],  # M3 op_castle (agente do castelo: torre 4 andares 360, salao acessivel, patio, adro, portoes, estandartes)
    "tree": ["op_tree"],  # M3 op_tree (arvore monumental arqueada; acrescimo do agente da arvore)
    "summon": ["op_summon"],    # M2 op_summon (torre AMS por alias como o ds_summon + base Wano no terraco leste)
    "harbor": ["op_harbor"],  # M3 op_harbor (agente porto+navio: pier/palafita/armazens/escadas PortoA-B/barcos)
    "ship": ["op_ship"],      # M3 op_ship (agente porto+navio: casco, mastros, velas, prancha, castelo de popa)
    "water": ["op_water"],  # M4 op_water (agente da agua: cantaria dos canais/bacia, degraus, bicas, roda d'agua VFX_OP_Wheel, pedras de base; mede e corrige FX_*/WATER_* via op_core._water_measured)
    "exit": ["op_exit"],  # M4 op_exit (agente saida+marcos: ponte vermelha em arco, promontorio, cabeca de ponte da ancora + guarda provisoria)
    "landmarks": ["op_landmarks"],  # M4 op_landmarks (agente saida+marcos: caveira esculpida na rocha, espada, pagode)
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
