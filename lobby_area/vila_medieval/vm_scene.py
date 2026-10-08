# vm_scene - DIA ENSOLARADO da previa (SPEC 'Luz': sol quente, sombra suave; o Roblox faz a luz pelo perfil do lobby
# no AreaAtmosphere = Lighting do Edit) + cameras de QA (Roblox -> Blender) + camera ortografica da planta + bonecos
# de escala + nuvens (so previa). Reaproveita fm_scene (render, ceu em degrade, sol, compositor de nevoa).
import math, random
import bpy
from mathutils import Vector
import vm_lib as VL
import vm_layout as L
import fm_lib
import fm_scene

# vetor que APONTA PARA O SOL (Blender). Roblox: sol a sudoeste e alto (~52 graus) -> a fachada da forja (+Z) e a rua
# curva recebem luz de frente-esquerda para quem chega das ilhas; sombras curtas e suaves.
SUN_DIR = Vector((-0.42, -0.50, 0.76)).normalized()


def setup(res=(960, 540), samples=24):
    fm_scene.setup_render(res, samples)
    fm_scene.AMB_COLOR = (0.56, 0.66, 0.86)
    fm_scene.AMB_POWER = 0.75
    fm_scene.setup_world()
    w = bpy.context.scene.world
    for nd in w.node_tree.nodes:
        if nd.bl_idname == "ShaderNodeValToRGB":
            els = sorted(nd.color_ramp.elements, key=lambda e: e.position)
            els[0].color = (0.62, 0.78, 0.98, 1)          # horizonte claro
            if len(els) > 2:
                els[1].color = (0.30, 0.55, 0.95, 1)
            els[-1].color = (0.08, 0.30, 0.86, 1)         # zenite azul
    fm_scene.SUN_DIR = SUN_DIR
    fm_scene.SUN_COLOR = (1.0, 0.93, 0.80)
    fm_scene.SUN_POWER = 4.2
    fm_scene.FOG.update(start=320.0, depth=1600.0, factor=0.40, color=(0.72, 0.83, 0.97), curve=1.4)
    fm_scene.setup_sun()
    vs = bpy.context.scene.view_settings
    vs.view_transform = "AgX"
    try:
        vs.look = "AgX - Base Contrast"
    except Exception:
        pass
    vs.exposure = 0.55


def clouds():
    rng = random.Random(1212)
    for nm in ("Cloud",):
        fm_lib.mat(nm)
    mb = fm_lib.MB("PREVIEW_Clouds", "00_REFERENCE", rng, detail="far", floor=-999)
    for i in range(14):
        a = math.radians(rng.uniform(140, 400))
        r = rng.uniform(520, 820)
        cx, cz = math.cos(a) * r, math.sin(a) * r
        cy = rng.uniform(170, 260)
        n = rng.randint(5, 9)
        L_ = rng.uniform(60, 120)
        for k in range(n):
            f = k / (n - 1) - 0.5
            rr = rng.uniform(16, 30) * (1.25 - abs(f))
            p = VL.B(cx + f * L_ * math.cos(a + 1.57), cz + f * L_ * math.sin(a + 1.57), cy + rr * 0.3)
            mb.ico(rr, tuple(p), "Cloud", 2, (1.0, 1.0, 0.62), jitter=0.12)
    mb.finish()


def cameras():
    for n, (loc, tgt, lens) in L.cams().items():
        fm_lib.camera(n, VL.B(loc[0], loc[2], loc[1]), VL.B(tgt[0], tgt[2], tgt[1]), lens)
    # planta: ortografica de cima no recorte EXATO da planta aprovada (1200 x 1140 px; norte = cima)
    cd = bpy.data.cameras.new("CAM_VM_Plan")
    cd.type = "ORTHO"
    cd.ortho_scale = L.PLAN_W
    cd.clip_start, cd.clip_end = 1.0, 2000.0
    ob = bpy.data.objects.new("CAM_VM_Plan", cd)
    cx, cz = L.PLAN_CENTER
    ob.location = VL.B(cx, cz, 600.0)
    ob.rotation_euler = (0.0, 0.0, 0.0)
    fm_lib.coll("00_REFERENCE").objects.link(ob)
    bpy.context.scene.camera = bpy.data.objects["CAM_VM_Ref_01"]


def scale_reference(visible=True):
    sx, sz = L.SPAWN
    spots = [("SCALE_Dummy_Spawn", 3.0, 96.0, L.Y_SPAWN, 0, -1), ("SCALE_Dummy_Praca", -6.0, 40.0, L.Y_PAVE, 0, -1),
             ("SCALE_Dummy_Rua", 4.0, 4.0, L.Y_PAVE, 0, -1), ("SCALE_Dummy_Ignis", 2.0, -44.0, L.Y_NORTH, 0, -1),
             ("SCALE_Dummy_Loja", 66.0, 45.0, L.Y_SHOP, 1, 0), ("SCALE_Dummy_Ranking", -78.0, 36.0, L.Y_RANK, -0.4, -0.9),
             ("SCALE_Dummy_Portais", -112.0, 74.0, L.Y_PAVE, -1, 0), ("SCALE_Dummy_Portao", 47.0, 141.0, L.Y_PAVE, 0, 1),
             ("SCALE_Dummy_RuaCurva", 44.0, 118.0, L.Y_PAVE, -0.3, -1)]
    for n, x, z, y, fx, fz in spots:
        VL.dummy(n, x, z, y, fx, fz, visible=visible)
