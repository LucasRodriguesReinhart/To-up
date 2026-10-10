# build_op.py - reconstroi a Ilha 5 (ONE PIECE / WANO) do zero e salva o .blend
# uso: blender -b --factory-startup --python build_op.py -- [blockout] [proxies] [sem=<zona,zona>] [com=<zona,zona>]
#      com=<zonas>: V2-0 - liga o modulo de detalhe da V1 (ZONE_MODULES_V1) so nessas zonas (teste dos agentes de zona;
#      o modulo tem de ler a planta V2)
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
# V2-0 (PLANO_V2 secao 11, integracao): a planta V2 (quadras, NE, canais rebaixados, pontes em arco, sem pagode/H3/
# estandartes) so existe no BLOCKOUT por enquanto. Ficam em blockout (ZONE_MODULES_V2_0) as zonas cujo modulo V1 depende
# da planta antiga ou foi reprovado e reprova o gate 'visual'; cada onda V2 religa a sua zona aqui quando o modulo novo
# passar no gate. (ZONE_MODULES abaixo = mapa V1, mantido para referencia; o build usa ZONE_MODULES_V2_0.)
ZONE_MODULES_V1 = {
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
    "dressing": ["op_props", "op_veg", "op_vfx", "op_lights"],
                             # M4/M6 op_veg, op_props, op_vfx, op_lights. M4 op_veg (acrescimo pontual do agente da
                             # vegetacao): deve ficar por ULTIMO na lista (a vegetacao desvia do que ja foi montado,
                             # inclusive props); expoe op_veg.TRUNKS para quem precisar desviar dos troncos
                             # M4 op_vfx/op_lights (acrescimo pontual do agente de luz/VFX): op_veg e o ULTIMO que faz
                             # GEOMETRIA; depois dele so o op_vfx (marcadores FX_* + previa PREVIEW_VFX_* em 00_REFERENCE,
                             # que a vegetacao nao deve ver) e o op_lights por ultimo (so audita/hierarquiza luzes)
                             # M4 op_props (acrescimo pontual do agente de props): PRIMEIRO do dressing - assenta cada
                             # peca por raio no chao ja construido; a vegetacao desvia das pecas e colisoes dele
}
ZONE_MODULES_V2_0 = {
    "terrain": [],     # op_terrain V1: pele/borda reprovadas (U5/U8: 6.000+ studs2 sem colisao), NE antigo, canais na
                       #   cota velha -> V2-3 (bordas que fecham as frestas, socalcos NE, pinaculo sem pagode)
    "entry": [],       # op_entry V1: nobori da ponte e poste em T (U15/U16) -> V2-3
    "capital": [],     # op_capital/op_m2_trecho V1: casas soltas (U1/U2/U11), le L.BUILDINGS/STREETS da V1 -> V2-3 (kit V2)
    "plaza": [],       # op_m2_praca/op_plaza V1: estandartes, borda do trecho M2 (frestas U5) -> V2-3 (faixa do eixo)
    "castle": ["op_castle"],  # V2-2 castelo de Wano no kit V2 (5 andares/telhados em telha ondulada, chidori/karahafu,
                              #   salao com vida, muros/cerca/portoes com colisao) - gate visual verde junto com a arvore
    "tree": ["op_tree"],      # V2 arvore (pinheiro monumental de almofadas) religada com o castelo V2-2 (op_castle antes:
                              #   o check_castle do op_tree le as malhas OP_Cas_*) - gate visual verde
    "summon": ["op_summon"],  # V2-2 conves pirata (proa+carranca de leao, mastros com Jolly Roger, timao, baus; torre AMS intacta) - passou no gate visual (commit V2-2)
    "harbor": ["op_harbor"],  # V2-2 porto vivo (H3 fora; guindaste com tambor/lingada moveis, 3 grupos de barcos
                              #   balancando, lonja, redes, armazem aberto) - passou no gate visual (agente do porto V2)
    "ship": ["op_ship"],      # V2-2 navio atracado (velas ferradas, lingada) + junco fundeado VFX_OP_Junk - gate verde
    "water": [],       # op_water V1: canais na cota antiga (U6) -> V2-3 (canais rebaixados, capa fora das pontes)
    "exit": [],        # op_exit V1: frestas entre as tabuas (U5) -> V2-3
    "landmarks": [],   # op_landmarks V1: pagode (U13) -> V2-3
    "dressing": [],    # op_props/op_veg/op_vfx/op_lights V1: postes em T, estandartes, arvores-esfera -> V2-1/V2-3
}
ZONE_MODULES = ZONE_MODULES_V2_0


FORCE_DETAIL = set()      # com=<zonas> (V2-0)


def zone_mods(zone):
    return ZONE_MODULES_V1[zone] if zone in FORCE_DETAIL else ZONE_MODULES[zone]


def zone_ready(zone):
    ms = zone_mods(zone)
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
    use = {}
    for zone in ZONE_MODULES:
        if zone in skip_zones:
            continue
        use[zone] = (zone == studio_zone and zone_ready(zone)) if studio_zone else (not blockout and zone_ready(zone))
    detailed = [z for z, u in use.items() if u]
    op_core.WATER_MEASURED = "water" in detailed        # V2-0: sem op_water, os FX_/WATER_ saem da planta (canais novos)
    op_core.build()
    op_blockout.build(skip=set(detailed) | set(skip_zones), ore_proxies=ore_proxies)
    print("BUILD V2-0 zonas em blockout: %s" % (",".join(z for z in ZONE_MODULES if z not in detailed) or "-"))
    for zone in detailed:
        for m in zone_mods(zone):
            t = time.time()
            run_module(m)
            print("%s %.1fs" % (m, time.time() - t))
    import op_col
    print("BUILD guardas erguidas acima de muros/props vizinhos: %d" % op_col.raise_guards())   # V2-0 (9.4)
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
        if a.startswith("com="):
            FORCE_DETAIL.update(a[4:].split(","))
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
