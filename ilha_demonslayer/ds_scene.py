# ds_scene - mundo NOTURNO LEGIVEL da previa (lua fria + janelas e lanternas quentes), mar de nuvens, lua, vizinhos de
# previa (Shadow Garden, portao DS aprovado na ilhota dela), cameras de QA do plano (inclusive as 5 que reproduzem as
# referencias) e referencia de escala da Ilha 4. O Roblox faz a noite pelo AreaAtmosphere (tema nichirin); aqui a
# previa do Blender imita: lua fria vinda de tras-esquerda de quem chega (SUDOESTE local), ceu azul-noite (nao roxo),
# ambiente frio moderado (o piso, os caminhos e as casas leem sem luz dramatica). Tudo de previa vai em 00_REFERENCE
# (PREVIEW_*) e fica fora do export.
import math, random, os, importlib.util
import bpy
from mathutils import Vector
import ds_lib as DL
from ds_lib import MB, camera, ccw
import ds_layout as L
import fm_lib
import fm_scene
import il_scene

MOON_DIR = Vector((-0.50, -0.62, 0.60)).normalized()     # aponta PARA a lua (sudoeste local, alta)


def setup(res=(1600, 900), samples=32):
    fm_scene.setup_render(res, samples)
    fm_scene.AMB_COLOR = (0.34, 0.42, 0.66)
    fm_scene.AMB_POWER = 0.62
    fm_scene.setup_world()
    w = bpy.context.scene.world
    for nd in w.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeValToRGB":
            els = sorted(nd.color_ramp.elements, key=lambda e: e.position)
            els[0].color = (0.10, 0.14, 0.30, 1)          # horizonte azul-noite com nevoa
            els[-1].color = (0.010, 0.016, 0.060, 1)      # zenite
            if len(els) > 2:
                els[1].color = (0.040, 0.060, 0.160, 1)
        if nd.bl_idname == "ShaderNodeBackground" and nd.inputs["Color"].is_linked:
            nd.inputs["Strength"].default_value = 0.6
    fm_scene.SUN_DIR = MOON_DIR
    fm_scene.SUN_COLOR = (0.66, 0.76, 1.0)
    fm_scene.SUN_POWER = 2.0
    fm_scene.FOG.update(start=420.0, depth=1700.0, factor=0.32, color=(0.11, 0.14, 0.28))
    fm_scene.setup_sun()
    vs = bpy.context.scene.view_settings
    vs.view_transform = "Standard"
    try:
        vs.look = "None"
    except Exception:
        pass
    vs.exposure = 0.75
    ng = bpy.data.node_groups.get("CMP_Lobby")
    if ng:
        for nd in ng.nodes:
            if nd.bl_idname == "CompositorNodeGlare":
                for nm, val in (("Threshold", 0.8), ("Strength", 0.4), ("Size", 0.6)):
                    if nm in nd.inputs:
                        nd.inputs[nm].default_value = val


def tone_emissives():
    il_scene.ENERGY = tuple(il_scene.ENERGY) + ("Fire_DS_Glow", "Ember_DS_Glow")
    il_scene.tone_emissives()


def clouds():
    """mar de nuvens (so previa; o cliente faz o dele em -60 so na area 4): plano escuro + poucos bancos largos e
    achatados, de tom proximo (nada que leia como ilhota)"""
    for nm in ("Cloud_DS", "Cloud_DS_Shade"):
        if nm not in bpy.data.materials:
            fm_lib.mat(nm)
    mb = MB("PREVIEW_CloudSea", "00_REFERENCE", random.Random(1313), detail="far", floor=-999)
    mb.box((4400.0, 4400.0, 1.0), (0.0, 300.0, L.SEA_CLOUD - 0.5), (0, 0, 0), "Cloud_DS_Shade", 0.0)
    mb.finish()


def moon():
    """SO previa: lua fria no sudoeste local + estrelas"""
    rng = random.Random(5)
    for nm in ("DS_MoonDisc_Glow", "DS_Star_Glow"):
        if nm not in bpy.data.materials:
            fm_lib.mat(nm)
    mb = MB("PREVIEW_Moon", "00_REFERENCE", rng, detail="far", floor=-999)
    d = MOON_DIR
    c = Vector((d.x, d.y, 0.0)).normalized() * 1700.0
    mb.ico(120.0, (c.x, c.y + 300.0, 900.0), "DS_MoonDisc_Glow", 3)
    for i in range(80):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(900.0, 1900.0)
        z = rng.uniform(260.0, 1100.0)
        mb.ico(rng.uniform(2.0, 4.5), (math.cos(a) * r, 300.0 + math.sin(a) * r, z), "DS_Star_Glow", 1)
    mb.finish()


def _load_ro(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def neighbors():
    """SO previa (00_REFERENCE, fora do export): a Shadow Garden (contorno + ponte de saida + ilhota com o portao DS
    aprovado em silhueta) levada para o referencial local desta ilha - para as vistas mostrarem o encaixe e a folga"""
    if "PREVIEW_Neighbor" not in bpy.data.materials:
        fm_lib.mat("PREVIEW_Neighbor")
    mb = MB("PREVIEW_Neighbors", "00_REFERENCE", random.Random(9), detail="far", floor=-999)
    try:
        SG = _load_ro("sg_layout_ro", os.path.join(DL.ROOT, "ilha_shadowgarden", "sg_layout.py"))
        loc = lambda p: L.local_of_world(*SG.to_world_xy(*p))
        rim = [loc(p) for p in SG.ISLAND_RIM]
        mb.prism(ccw(rim), 0.0, SG.P3, "PREVIEW_Neighbor")
        ex = [loc(SG.exit_point(d)) for d in (0.0, SG.EXIT_BRIDGE_LEN)]
        mb.prism(ccw(L.ribbon(ex, 9.0)), SG.EXIT_Z - 2.0, SG.EXIT_Z, "PREVIEW_Neighbor")
        ic = loc(SG.islet_center())
        mb.cyl(SG.GATE_ISLET_R, 30.0, (ic[0], ic[1], SG.EXIT_Z - 15.0), m="PREVIEW_Neighbor", n=24, bevel=0.0)
        g = loc(SG.gate_ds_pos())
        a = loc(SG.anchor_pos())
        ang = math.atan2(a[1] - g[1], a[0] - g[0])
        F = DL.Frame(g[0], g[1], SG.EXIT_Z, ang - math.pi / 2)
        for s in (-1, 1):
            mb.box((2.4, 2.4, 22.0), F.p(s * 10.0, 0, 11.0), F.r(), "PREVIEW_Neighbor", 0.0)
        mb.box((24.0, 2.4, 2.4), F.p(0, 0, 21.0), F.r(), "PREVIEW_Neighbor", 0.0)
        # trecho entre a ancora e o portao DS (ilhota): tabuleiro de previa
        mb.prism(ccw(L.ribbon([g, a], 9.0)), SG.EXIT_Z - 2.0, SG.EXIT_Z, "PREVIEW_Neighbor")
        # conferencia do encaixe na previa: ancora da SG (no referencial dela) = WORLD_FROM_PREV desta ilha
        print("SCENE encaixe: ancora SG em local DS (%.3f, %.3f) | WORLD_FROM_PREV (%.1f, %.1f)" % (
            a[0], a[1], L.PREV_X, L.PREV_Y))
    except Exception as ex:
        print("AVISO neighbors: Shadow Garden fora da previa (%s)" % ex)
    mb.finish()


# ONDA 4 (integracao): cameras novas das folhas finais - 360 (8 vistas em volta do meio da ilha, a partir do SUL local =
# lado da chegada, no sentido anti-horario) e as 2 vistas da CONEXAO na cabeca da ponte de chegada (a SG aparece pelos
# vizinhos de previa). Nao entram no QA (L.cams) nem no export (SKIP_PREFIX CAM_).
ORBIT_C, ORBIT_R, ORBIT_Z = (15.0, 290.0, 66.0), 720.0, 300.0


def extra_cams():
    out = {}
    for k in range(8):
        a = math.radians(-90.0 + 45.0 * k)
        out["CAM_DS_Orbit_%d" % k] = ((ORBIT_C[0] + math.cos(a) * ORBIT_R, ORBIT_C[1] + math.sin(a) * ORBIT_R, ORBIT_Z),
                                      ORBIT_C, 30)
    z = L.DECK + 8.0                     # camera de 3a pessoa do Roblox: ~2,5 acima do olho
    out["CAM_DS_Conexao_OlhaSG"] = ((4.0, L.PREV_Y + 14.0, z), (-6.0, L.PREV_Y - 330.0, L.DECK - 4.0), 22)
    out["CAM_DS_Conexao_OlhaIlha"] = ((-3.0, L.PREV_Y + 4.0, z), (0.0, 120.0, L.T1 + 6.0), 22)
    return out


def cameras():
    for n, (loc, tgt, lens) in L.cams().items():
        camera(n, loc, tgt, lens)
    for n, (loc, tgt, lens) in extra_cams().items():
        camera(n, loc, tgt, lens)
    bpy.context.scene.camera = bpy.data.objects["CAM_DS_Ref_01"]


def scale_reference(visible=True):
    g = L.gate_op_pos()
    ux, uy = L.exit_dir()
    spots = [("SCALE_Dummy_Entry", 3.0, 22.0, L.T0), ("SCALE_Dummy_Trail", -6.0, 70.0, L.T1),
             ("SCALE_Dummy_Clearing", 30.0, 200.0, L.T1), ("SCALE_Dummy_Village", -60.0, 150.0, L.T1),
             ("SCALE_Dummy_Forge", 6.0, 460.0, L.T4), ("SCALE_Dummy_Summon", 164.0, 296.0, L.T3),
             ("SCALE_Dummy_Patamar", 20.0, 404.0, L.T3),
             ("SCALE_Dummy_OPGate", g[0] - ux * 9.0 - uy * 4.0, g[1] - uy * 9.0 + ux * 4.0, L.T4)]
    for n, x, y, z in spots:
        DL.dummy(n, x, y, z, visible=visible)
