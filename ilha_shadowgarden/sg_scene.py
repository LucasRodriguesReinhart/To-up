# sg_scene - mundo NOTURNO (luar), mar, ilhotas flutuantes, nuvens, cameras de QA e referencia de escala da Ilha 3.
# O Roblox faz a noite pelo AreaAtmosphere (perfil da area sombra); aqui a previa do Blender imita: lua fria de noroeste,
# ceu navy/roxo, ambiente frio fraco, interiores e janelas quentes.
import math, random
import bpy
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, camera, dome
import sg_layout as L
import fm_scene
import il_scene

MOON_DIR = Vector((-0.45, 0.55, 0.70)).normalized()     # aponta PARA a lua (noroeste, alta: contraluz na fachada)


def setup(res=(1600, 900), samples=32):
    fm_scene.setup_render(res, samples)
    fm_scene.AMB_COLOR = (0.30, 0.36, 0.62)
    fm_scene.AMB_POWER = 0.42
    fm_scene.setup_world()
    w = bpy.context.scene.world
    for nd in w.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeValToRGB":
            cr = nd.color_ramp
            cols = {0: (0.080, 0.085, 0.20, 1), 1: (0.010, 0.012, 0.045, 1)}
            els = sorted(cr.elements, key=lambda e: e.position)
            els[0].color = (0.090, 0.085, 0.21, 1)       # horizonte roxo-navy
            els[-1].color = (0.008, 0.010, 0.040, 1)     # zenite quase preto azulado
            if len(els) > 2:
                els[1].color = (0.030, 0.034, 0.110, 1)
        if nd.bl_idname == "ShaderNodeBackground" and nd.inputs["Color"].is_linked:
            nd.inputs["Strength"].default_value = 0.55       # ceu visto pela camera: noite (a luz ambiente e a outra)
    fm_scene.SUN_DIR = MOON_DIR
    fm_scene.SUN_COLOR = (0.62, 0.72, 1.0)
    fm_scene.SUN_POWER = 1.6
    fm_scene.FOG.update(start=380.0, depth=1600.0, factor=0.30, color=(0.10, 0.11, 0.24))
    fm_scene.setup_sun()
    vs = bpy.context.scene.view_settings
    vs.view_transform = "Standard"
    try:
        vs.look = "None"
    except Exception:
        pass
    vs.exposure = 0.55
    ng = bpy.data.node_groups.get("CMP_Lobby")
    if ng:
        for nd in ng.nodes:
            if nd.bl_idname == "CompositorNodeGlare":
                for nm, val in (("Threshold", 0.7), ("Strength", 0.5), ("Size", 0.7)):
                    if nm in nd.inputs:
                        nd.inputs[nm].default_value = val


def tone_emissives():
    il_scene.ENERGY = tuple(il_scene.ENERGY) + ("SG_Violet_Glow", "SG_Moon_Glow")
    il_scene.tone_emissives()


def sea():
    import fm_lib
    fm_lib.MATS.setdefault("Water_SG_Sea", (fm_lib.S(16, 20, 44), 0.2, 0.0, 0, None, 0.0))
    fm_lib.make_materials()
    mb = MB("SG_Sky_Sea", "02_TERRAIN", random.Random(3), detail="far", floor=-999)
    mb.box((4200.0, 4200.0, 1.0), (0, 0, L.SEA - 0.5), (0, 0, 0), "Water_SG_Sea", 0.0)
    mb.finish()


# a Ilha 2 fica ao SUL/SUDESTE no referencial desta ilha: nada de ilhota no setor 240..300 graus (a ponte de chegada)
ISLET_SPOTS = [(-300.0, 60.0, 52.0, 20.0), (-260.0, 260.0, 80.0, 16.0), (40.0, 360.0, 64.0, 22.0),
               (300.0, 200.0, 90.0, 14.0), (340.0, 40.0, 30.0, 18.0), (-340.0, -140.0, 40.0, 14.0),
               (200.0, 380.0, 110.0, 12.0), (-150.0, 400.0, 34.0, 18.0), (380.0, -170.0, 60.0, 12.0)]


def islets():
    """ilhotas flutuantes de basalto escuro com pinheiros (fora do alcance)"""
    rng = random.Random(3909)
    mb = MB("SG_Sky_Islets", "02_TERRAIN", rng, detail="far", floor=-999)
    for x, y, z, r in ISLET_SPOTS:
        for k, (f, dz) in enumerate(((1.0, -0.35), (0.8, -0.95), (0.55, -1.55), (0.3, -2.1))):
            ox, oy = rng.uniform(-0.12, 0.12) * r, rng.uniform(-0.12, 0.12) * r
            mb.rock((x + ox, y + oy, z + dz * r), (2 * r * f, 2 * r * f * rng.uniform(0.8, 1.0), r * 0.9),
                    "Cliff_Rock_SG" if k % 2 == 0 else "Cliff_Rock_SG_Dark", 1, jitter=0.3, flat_bottom=False)
        pts = [(x + r * rng.uniform(0.85, 1.05) * math.cos(a), y + r * rng.uniform(0.85, 1.05) * math.sin(a))
               for a in [2 * math.pi * i / 9 for i in range(9)]]
        mb.prism(pts, z - 0.6, z + 0.4, "Grass_SG")
        for k in range(rng.randint(2, 4)):
            a = rng.uniform(0, 6.28)
            rr = rng.uniform(0, r * 0.55)
            px, py, h = x + rr * math.cos(a), y + rr * math.sin(a), rng.uniform(10, 16)
            mb.cyl(0.5, h * 0.35, (px, py, z + 0.4 + h * 0.17), m="Wood_SG_Dark", n=6, bevel=0.0)
            for j, (fr, fz) in enumerate(((1.0, 0.3), (0.72, 0.55), (0.45, 0.78))):
                mb.cyl(h * 0.2 * fr, h * 0.32, (px, py, z + 0.4 + h * fz), m="Leaf_SG_Pine", n=7, r2=0.2, bevel=0.0)
    mb.finish()


def clouds():
    """mar de nuvens embaixo da ilha (a concept: neblina fria sob os penhascos)"""
    rng = random.Random(1313)
    mb = MB("SG_Sky_Clouds", "02_TERRAIN", rng, detail="far", floor=-999)
    for i in range(20):
        a = math.radians(i * 18.0 + rng.uniform(-7, 7))
        R = SL.ray_poly(L.ISLAND_RIM, math.degrees(a), 0.0, -20.0) + rng.uniform(8.0, 36.0)
        cx, cy = math.cos(a) * R, -20.0 + math.sin(a) * R
        for k in range(rng.randint(4, 6)):
            rr = rng.uniform(14.0, 26.0)
            mb.ico(rr, (cx + rng.uniform(-22, 22), cy + rng.uniform(-22, 22), rng.uniform(-70.0, -38.0)), "Cloud", 2,
                   (1.25, 1.0, 0.5), jitter=0.12)
    mb.finish()


def moon():
    """SO previa (o Roblox usa a lua do Sky): disco frio grande no noroeste, fora do export"""
    mb = MB("PREVIEW_Moon", "00_REFERENCE", random.Random(5), detail="far", floor=-999)
    d = MOON_DIR
    c = Vector((d.x, d.y, 0.0)).normalized() * 1500.0
    mb.ico(90.0, (c.x, c.y, 620.0), "SG_Moon_Glow", 2)
    mb.finish()


P1, P2, P3, SUM, H = L.P1, L.P2, L.P3, L.SUM, L.HALL
CAMS = {
    # visoes pedidas (secao de QA da missao)
    "CAM_SG_Entry": ((0.0, -250.0, L.DECK + 12.0), (0.0, -120.0, P1 + 16.0), 20),
    "CAM_SG_Front": ((20.0, -470.0, 190.0), (0.0, 20.0, 60.0), 24),
    "CAM_SG_Left": ((-440.0, -20.0, 170.0), (0.0, 10.0, 60.0), 24),
    "CAM_SG_Right": ((460.0, -40.0, 170.0), (0.0, 10.0, 60.0), 24),
    "CAM_SG_Back": ((0.0, 480.0, 210.0), (0.0, 0.0, 60.0), 24),
    "CAM_SG_BirdEye": ((0.0, -40.0, 720.0), (0.0, -20.0, 0.0), 24),
    "CAM_SG_Castle": ((0.0, -60.0, P2 + 14.0), (0.0, 90.0, P3 + 50.0), 18),
    "CAM_SG_MiningHall": ((0.0, 48.0, H + 9.0), (0.0, 110.0, H + 8.0), 16),
    "CAM_SG_Summon": ((-96.0, -104.0, P1 + 12.0), (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], SUM + 14.0), 18),
    "CAM_SG_Craft": ((56.0, -44.0, P2 + 12.0), (L.CRAFT_C[0], L.CRAFT_C[1], P2 + 10.0), 18),
    "CAM_SG_CraftInterior": ((L.CRAFT_C[0] - 8.5, L.CRAFT_C[1], P2 + 5.2), (L.CRAFT_C[0] + 8.0, L.CRAFT_C[1], P2 + 4.0), 14),
    "CAM_SG_Dungeon": ((70.0, 20.0, P3 + 14.0), (L.DUNGEON_HOUSE[0], L.DUNGEON_HOUSE[1], P3 + 20.0), 18),
    "CAM_SG_DungeonInterior": ((100.0, 64.0, P3 + 5.2), (100.0, 82.0, P3 + 6.0), 14),
    "CAM_SG_DungeonRooms": ((-58.0, 80.0, L.DUN_Z + 9.0), (40.0, 80.0, L.DUN_Z + 4.0), 16),
    "CAM_SG_Village": ((-30.0, -150.0, P1 + 16.0), (-70.0, -60.0, P2 + 6.0), 20),
    "CAM_SG_ExitGate": None,          # calculada (frente do portao DS, na ponte de saida)
    # altura do jogador (olho ~5,2 acima do piso)
    "CAM_SG_PlayerHeight_Entry": ((0.0, -222.0, L.DECK + 5.2), (0.0, -150.0, P1 + 6.0), 22),
    "CAM_SG_PlayerHeight_Plaza": ((0.0, -160.0, P1 + 5.2), (0.0, -60.0, P2 + 14.0), 22),
    "CAM_SG_PlayerHeight_Village": ((-30.0, -45.0, P2 + 5.2), (-100.0, -45.0, P2 + 6.0), 22),
    "CAM_SG_PlayerHeight_Castle": ((0.0, 4.0, P3 + 5.2), (0.0, 60.0, P3 + 22.0), 20),
    "CAM_SG_PlayerHeight_MiningHall": ((0.0, 47.0, H + 5.2), (0.0, 120.0, H + 3.0), 20),
    "CAM_SG_PlayerHeight_Summon": ((-124.0, -118.0, SUM + 5.2), (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], SUM + 10.0), 22),
    "CAM_SG_PlayerHeight_Craft": ((64.0, -50.0, P2 + 5.2), (L.CRAFT_C[0], L.CRAFT_C[1], P2 + 5.0), 22),
    "CAM_SG_PlayerHeight_Dungeon": ((100.0, 40.0, P3 + 5.2), (L.DUNGEON_HOUSE[0], L.DUNGEON_HOUSE[1], P3 + 9.0), 22),
    "CAM_SG_PlayerHeight_DungeonRoom": ((-2.0, 62.0, L.DUN_Z + 5.2), (0.0, 100.0, L.DUN_Z + 3.0), 20),
    "CAM_SG_PlayerHeight_ExitGate": None,
    # cameras que imitam a concept aprovada (comparacao lado a lado)
    "CAM_SG_Ref_Main": ((70.0, -430.0, 250.0), (0.0, 10.0, 40.0), 26),
    "CAM_SG_Ref_Top": ((0.0, -10.0, 780.0), (0.0, -9.0, 0.0), 26),
    "CAM_SG_Ref_Front": ((0.0, -380.0, 110.0), (0.0, 20.0, 70.0), 24),
    "CAM_SG_Ref_Side": ((-400.0, -160.0, 160.0), (0.0, 20.0, 50.0), 24),
    "CAM_SG_Ref_Castle": ((0.0, -40.0, P2 + 20.0), (0.0, 100.0, P3 + 60.0), 20),
    "CAM_SG_Ref_Village": ((40.0, -166.0, P1 + 10.0), (-40.0, -90.0, P2 + 8.0), 20),
}


def cameras():
    for n, v in CAMS.items():
        if v is None:
            continue
        loc, tgt, lens = v
        camera(n, loc, tgt, lens)
    gp = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    z = L.EXIT_Z
    camera("CAM_SG_ExitGate", (gp[0] - ux * 38.0 - uy * 9.0, gp[1] - uy * 38.0 + ux * 9.0, z + 11.0),
           (gp[0], gp[1], z + 16.0), 18)
    camera("CAM_SG_PlayerHeight_ExitGate", (gp[0] - ux * 40.0 - uy * 5.0, gp[1] - uy * 40.0 + ux * 5.0, z + 5.2),
           (gp[0], gp[1], z + 9.0), 24)
    bpy.context.scene.camera = bpy.data.objects["CAM_SG_Ref_Main"]


def scale_reference(visible=True):
    gp = L.gate_ds_pos()
    ux, uy = L.exit_dir()
    spots = [("SCALE_Dummy_Entry", 3.0, -168.0, P1), ("SCALE_Dummy_Plaza", 10.0, -110.0, P1),
             ("SCALE_Dummy_Village", -40.0, -45.0, P2), ("SCALE_Dummy_Castle", 4.0, 30.0, P3),
             ("SCALE_Dummy_Hall", 6.0, 70.0, H), ("SCALE_Dummy_Summon", -128.0, -118.0, SUM + 0.05),
             ("SCALE_Dummy_Craft", 72.0, -60.0, P2), ("SCALE_Dummy_Dungeon", 100.0, 52.0, P3),
             ("SCALE_Dummy_DunRoom", 0.0, 72.0, L.DUN_Z),
             ("SCALE_Dummy_DSGate", gp[0] - ux * 9.0 - uy * 4.0, gp[1] - uy * 9.0 + ux * 4.0, L.EXIT_Z)]
    for n, x, y, z in spots:
        SL.dummy(n, x, y, z, visible=visible)
