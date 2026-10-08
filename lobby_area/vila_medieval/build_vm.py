# build_vm.py - reconstroi o lobby VILA MEDIEVAL do zero e salva lobby_vila_medieval.blend
# uso: blender -b --factory-startup --python build_vm.py            (VM_OUT=<caminho.blend> muda a saida)
#   ordem fixa + semente do mathutils.noise fixa -> build deterministico (licao da Ilha 4)
#   vm_col (piso andavel + barreiras) -> vm_core (marcadores de contrato, volumes de QA, proxies de previa) ->
#   vm_blockout (zonas; o patio chama vm_portals = os 6 portais APROVADOS) -> cena (dia, cameras, escala)
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import vm_lib as VL                 # poe o pipeline do lobby (forja_mineradora) no sys.path, sem __pycache__
import bpy
import fm_pv3
fm_pv3.load()                       # portais aprovados: registram materiais/texturas das espirais ANTES do make
import fm_portals                   # (One Piece) registra os materiais dele no import
import fm_lib
import vm_layout as L
import vm_scene, vm_col, vm_core, vm_blockout


def build():
    t0 = time.time()
    from mathutils import noise as _noise
    _noise.seed_set(4402)
    VL.reset_scene()
    fm_lib.make_materials()
    vm_scene.setup()
    vm_col.build()
    vm_core.build()
    rep = vm_blockout.build()
    # V1 (acrescimo pontual): TRECHO DE QUALIDADE FINAL praca -> ponte com o kit (vm_kit). O vm_trecho recorta do
    # blockout o que cai na regiao (casas S1W/S1E/PNW/PNE, medalhao, ponte, rua sul, muros do canal x -30..30, props e
    # arvores) e constroi as pecas finais no lugar; cameras CAM_VM_T_* depois das do V0.
    import vm_trecho
    vm_trecho.build()
    # V2a (acrescimo pontual): FORJA DO IGNIS (vm_forge). Apaga o volume de blockout da forja do V0 (VM_Frg_*,
    # COL_Forge_*) e a laje lisa do largo, constroi a forja final + o largo (envoltoria do Ignis livre, chao plano em 7),
    # MOVE os marcadores da forja do vm_core e cria os VFX_* do lobby atual; cameras CAM_VM_F_* no fim.
    import vm_forge
    vm_forge.build()
    # V2b (acrescimo pontual): A VILA (vm_town) em volta do trecho: praca em aneis, terraco do spawn, casas do kit por
    # quadra, ruas, loja, ranking, patio dos portais, portao + ponte da Ilha 1, canal. Apaga os volumes do blockout que
    # substitui (casas, praca, spawn, loja, palco/salao, patio, portao, ponte, ruas fora do largo, COL_Canal refeitos);
    # junta as cores de flor dos enfeites do trecho; cameras CAM_VM_V2_* no fim.
    import vm_town
    vm_town.build()
    fm_lib.make_materials()          # materiais registrados depois do primeiro make (portais)
    vm_scene.clouds()
    vm_scene.cameras()
    vm_trecho.cameras()
    vm_forge.cameras()               # V2a
    vm_town.cameras()                # V2b
    vm_scene.scale_reference(visible=True)
    bpy.context.view_layer.update()
    return rep, time.time() - t0


if __name__ == "__main__":
    OUT = os.environ.get("VM_OUT") or os.path.join(HERE, "lobby_vila_medieval.blend")
    rep, dt = build()
    bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
    tris = 0
    for o in bpy.data.objects:
        if o.type == "MESH" and not o.name.startswith(("COL_", "PREVIEW_", "SCALE_", "QA_")):
            tris += sum(len(p.vertices) - 2 for p in o.data.polygons)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_"))
    print("BUILD OK objs=%d tris=%d col=%d t=%.1fs -> %s" % (len(bpy.data.objects), tris, ncol, dt, OUT))
