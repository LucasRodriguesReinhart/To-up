# op_scene - mundo DIURNO da previa (Wano: ceu azul, sol quente alto vindo de tras-esquerda de quem chega, sombras
# frias), MAR LOCAL turquesa (so previa; no jogo o cliente faz o mar so na area 5), vizinhos de previa (Demon Slayer:
# contorno + cabeceira da saida + portao One Piece em silhueta), cameras de QA do plano (inclusive as 2 que reproduzem
# as referencias) e referencia de escala. Tudo de previa vai em 00_REFERENCE (PREVIEW_*) e fica fora do export.
import math, random, os, importlib.util
import bpy
from mathutils import Vector
import op_lib as DL
from op_lib import MB, camera, ccw
import op_layout as L
import fm_lib
import fm_scene
import il_scene

SUN_DIR = Vector((-0.42, -0.58, 0.70)).normalized()     # aponta PARA o sol (sudoeste local, alto): fachadas sul claras


def setup(res=(1600, 900), samples=32):
    fm_scene.setup_render(res, samples)
    fm_scene.AMB_COLOR = (0.46, 0.58, 0.82)
    fm_scene.AMB_POWER = 0.62
    fm_scene.setup_world()
    w = bpy.context.scene.world
    for nd in w.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeValToRGB":
            els = sorted(nd.color_ramp.elements, key=lambda e: e.position)
            els[0].color = (0.62, 0.80, 0.98, 1)          # horizonte claro
            els[-1].color = (0.05, 0.24, 0.86, 1)         # zenite azul saturado (concept)
            if len(els) > 2:
                els[1].color = (0.26, 0.52, 0.95, 1)
    fm_scene.SUN_DIR = SUN_DIR
    fm_scene.SUN_COLOR = (1.0, 0.92, 0.80)
    fm_scene.SUN_POWER = 4.2
    fm_scene.FOG.update(start=700.0, depth=2600.0, factor=0.22, color=(0.70, 0.83, 0.97))
    fm_scene.setup_sun()
    vs = bpy.context.scene.view_settings
    vs.view_transform = "Standard"
    try:
        vs.look = "None"
    except Exception:
        pass
    vs.exposure = 0.0
    ng = bpy.data.node_groups.get("CMP_Lobby")
    if ng:
        for nd in ng.nodes:
            if nd.bl_idname == "CompositorNodeGlare":
                for nm, val in (("Threshold", 1.0), ("Strength", 0.25), ("Size", 0.5)):
                    if nm in nd.inputs:
                        nd.inputs[nm].default_value = val


def tone_emissives():
    il_scene.tone_emissives()


def sea():
    """mar local (so previa): plano turquesa grande no nivel L.SEA + faixa de espuma rente as falesias"""
    for nm in ("PREVIEW_Sea", "PREVIEW_SeaDeep"):
        if nm not in bpy.data.materials:
            fm_lib.mat(nm)
    mb = MB("PREVIEW_Sea", "00_REFERENCE", random.Random(1313), detail="far", floor=-999)
    cx, cy = L.SEA_C
    mb.box((L.SEA_SIZE * 2.0, L.SEA_SIZE * 2.0, 1.0), (cx, cy, L.SEA - 0.5), (0, 0, 0), "PREVIEW_Sea", 0.0)
    mb.finish()


def _load_ro(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def neighbors():
    """SO previa (00_REFERENCE, fora do export): a Demon Slayer (contorno + cabeceira da saida + portao One Piece
    aprovado em silhueta) levada para o referencial local desta ilha - mostra o encaixe e a folga"""
    if "PREVIEW_Neighbor" not in bpy.data.materials:
        fm_lib.mat("PREVIEW_Neighbor")
    mb = MB("PREVIEW_Neighbors", "00_REFERENCE", random.Random(9), detail="far", floor=-999)
    try:
        DS = _load_ro("ds_layout_ro", os.path.join(DL.ROOT, "ilha_demonslayer", "ds_layout.py"))
        loc = lambda p: L.local_of_world(*DS.to_world_xy(*p))
        rim = [loc(p) for p in DS.ISLAND_RIM]
        mb.prism(ccw(rim), 20.0, DS.T1, "PREVIEW_Neighbor")
        mb.prism(ccw([loc(p) for p in DS.FORGE_TERR]), DS.T1, DS.T4, "PREVIEW_Neighbor")
        mb.prism(ccw([loc(p) for p in DS.EXIT_LAND]), DS.T1, DS.T4, "PREVIEW_Neighbor")
        ex = [loc(DS.exit_point(d)) for d in (0.0, DS.EXIT_BRIDGE_LEN)]
        mb.prism(ccw(L.ribbon(ex, 9.0)), DS.T4 - 2.0, DS.T4, "PREVIEW_Neighbor")
        mb.prism(ccw([loc(p) for p in DS.pier_poly()]), DS.T4 - 30.0, DS.T4, "PREVIEW_Neighbor")
        g = loc(DS.gate_op_pos())
        a = loc(DS.anchor_op_pos())
        ang = math.atan2(a[1] - g[1], a[0] - g[0])
        F = DL.Frame(g[0], g[1], DS.T4, ang - math.pi / 2)
        for s in (-1, 1):
            mb.box((3.0, 3.0, 12.0), F.p(s * 10.3, 0, 6.0), F.r(), "PREVIEW_Neighbor", 0.0)
        mb.cyl(12.3, 2.0, F.p(0, 0, 10.0), (math.pi / 2, 0, F.a), m="PREVIEW_Neighbor", n=24, bevel=0.0)
        tw = loc(DS.CHIMNEY[:2])
        mb.box((6.0, 6.0, DS.CHIMNEY_TOP - DS.T4), (tw[0], tw[1], (DS.CHIMNEY_TOP + DS.T4) / 2), (0, 0, 0),
               "PREVIEW_Neighbor", 0.0)
        print("SCENE encaixe: ancora DS em local OP (%.3f, %.3f) | WORLD_FROM_PREV (%.1f, %.1f)" % (
            a[0], a[1], L.PREV_X, L.PREV_Y))
    except Exception as ex:
        print("AVISO neighbors: Demon Slayer fora da previa (%s)" % ex)
    mb.finish()


ORBIT_C, ORBIT_R, ORBIT_Z = (60.0, 250.0, 100.0), 820.0, 340.0


def extra_cams():
    out = {}
    for k in range(8):
        a = math.radians(-90.0 + 45.0 * k)
        out["CAM_OP_Orbit_%d" % k] = ((ORBIT_C[0] + math.cos(a) * ORBIT_R, ORBIT_C[1] + math.sin(a) * ORBIT_R, ORBIT_Z),
                                      ORBIT_C, 30)
    z = L.DECK + 8.0
    out["CAM_OP_Conexao_OlhaDS"] = ((4.0, L.PREV_Y + 70.0, z), (-6.0, L.PREV_Y - 360.0, L.DECK - 4.0), 22)
    out["CAM_OP_Conexao_OlhaIlha"] = ((-3.0, L.PREV_Y + 4.0, z), (0.0, 160.0, L.T1 + 16.0), 22)
    # M3 op_tree (acrescimo pontual, so cameras novas): arvore vista da ponte/torii/praca/patio na altura do jogador,
    # closes de raizes e casca, copa de baixo, lado e tras (CAM_OP_Tree_*)
    try:
        import op_tree
        out.update(op_tree.cams())
    except ImportError:
        pass
    return out


def cameras():
    for n, (loc, tgt, lens) in L.cams().items():
        camera(n, loc, tgt, lens)
    for n, (loc, tgt, lens) in extra_cams().items():
        camera(n, loc, tgt, lens)
    bpy.context.scene.camera = bpy.data.objects["CAM_OP_Ref_01"]


def scale_reference(visible=True):
    g = L.gate_opm_pos()
    ux, uy = L.exit_dir()
    spots = [("SCALE_Dummy_Entry", 3.0, 22.0, L.T0), ("SCALE_Dummy_Street", -4.0, 70.0, L.T1),
             ("SCALE_Dummy_Plaza", 12.0, 150.0, L.P), ("SCALE_Dummy_Summon", 150.0, 220.0, L.T1),
             ("SCALE_Dummy_Castle", -6.0, 372.0, L.CC), ("SCALE_Dummy_Harbor", 196.0, 66.0, L.HARBOR),
             ("SCALE_Dummy_Ship", 248.0, 160.0, L.SHIP), ("SCALE_Dummy_Forecourt", 10.0, 330.0, L.CF),
             ("SCALE_Dummy_OPMGate", g[0] - ux * 9.0 - uy * 4.0, g[1] - uy * 9.0 + ux * 4.0, L.T1)]
    for n, x, y, z in spots:
        DL.dummy(n, x, y, z, visible=visible)
