# fm_scene - mundo, sol, render, cameras de QA, referencia de escala
import bpy, math
from mathutils import Vector
from fm_lib import MB, D, camera, light, coll, marker
import fm_layout as L


def setup_render(res=(1600, 900), samples=32):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    ee = sc.eevee
    ee.taa_render_samples = samples
    for attr, val in (("use_shadows", True), ("use_raytracing", True), ("shadow_ray_count", 2),
                      ("shadow_step_count", 8), ("use_gtao", True), ("gtao_distance", 3.0),
                      ("fast_gi_distance", 6.0)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception:
                pass
    try:
        ee.shadow_pool_size = "1024"
    except Exception:
        pass
    try:
        ee.ray_tracing_method = "SCREEN"
    except Exception:
        pass
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except Exception:
        pass
    sc.view_settings.exposure = 0.15
    sc.render.film_transparent = False


def setup_world():
    sc = bpy.context.scene
    w = bpy.data.worlds.get("W_Lobby") or bpy.data.worlds.new("W_Lobby")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    # Generated do mundo = direcao (-1..1): 0 = horizonte, 1 = zenite. Azul saturado e nao muito claro (AgX lava claros)
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.30, 0.55, 0.95, 1)
    cr.elements[1].position = 0.7
    cr.elements[1].color = (0.03, 0.16, 0.75, 1)
    e = cr.elements.new(0.18)
    e.color = (0.16, 0.40, 0.92, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.25
    # luz ambiente separada do ceu visto pela camera: neutra/quente (sombras nao ficam azuladas)
    amb = nt.nodes.new("ShaderNodeBackground")
    amb.inputs["Color"].default_value = (0.62, 0.66, 0.74, 1)
    amb.inputs["Strength"].default_value = 0.9
    lp = nt.nodes.new("ShaderNodeLightPath")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(amb.outputs[0], mx.inputs[1])
    nt.links.new(bg.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])


def setup_sun():
    # sol quente, baixo-lateral pela frente-esquerda (luz no rosto da forja vista do spawn)
    sun = light("SUN_Key", "SUN", (0, 0, 200), 4.8, (1.0, 0.87, 0.68), 0.0,
                rot=(D(50), D(0), D(-32)))
    sun.data.angle = D(3.0)
    fill = light("SUN_Fill_Sky", "SUN", (0, 0, 200), 0.9, (1.0, 0.85, 0.70), 0.0, rot=(D(60), 0, D(150)))
    fill.data.use_shadow = False


def cameras():
    fz = L.FLOOR
    cams = {
        "CAM_Spawn": ((0, -112, 12.0), (0, 10, 28), 18),
        "CAM_Front": ((0, -150, 60), (0, 20, 18), 22),
        "CAM_FrontLeft": ((-60, -150, 70), (-10, 10, 14), 22),
        "CAM_FrontRight": ((70, -150, 70), (10, 10, 14), 22),
        "CAM_Left": ((-108, 4, 34), (10, 10, 16), 18),
        "CAM_Right": ((124, -20, 40), (0, 10, 14), 20),
        "CAM_Back": ((10, 104, 72), (0, -40, 4), 18),
        "CAM_BirdEye": ((0, -210, 210), (0, 10, 0), 24),
        "CAM_Ignis": ((6, -34, 11), (0, 2, 9), 24),
        "CAM_Portals": ((0, 56, 36), (0, 113, 38), 14),
        "CAM_Mine": ((-38, -30, 11), (-72, -48, 10), 18),
        "CAM_Waterwheel": ((86, -6, 14), (62, 20, 11), 20),
        "CAM_Konoha": ((-107, 126, 38), (-96, 230, 32), 16),
        "CAM_Ref1": ((0, -96, 26), (0, 30, 26), 16),
        "CAM_ForgeInterior": ((-15.5, 7.5, 11.0), (4, 24, 8.0), 14),
        "CAM_Shop": ((29.0, -44.5, 10.5), (40, -34, 6.5), 14),
        "CAM_Mill": ((52.0, 14.2, 11.0), (44, 24, 9.0), 12),
        "CAM_MineInside": ((-78, -52, 10), (-100, -74, 8), 16),
    }
    for n, (loc, tgt, lens) in cams.items():
        camera(n, loc, tgt, lens)
    bpy.context.scene.camera = bpy.data.objects["CAM_Spawn"]


def scale_reference():
    """dummy Roblox R15 (5.2 studs) permanente"""
    def dummy(name, x, y, z, ang=0.0, s=1.0, c="_SCALE_REFERENCE"):
        mb = MB(name, c)
        from fm_parts import Frame
        F = Frame(x, y, z, ang)
        mb.box((0.9 * s, 0.9 * s, 2.0 * s), F.p(-0.5 * s, 0, 1.0 * s), F.r(), "Dummy_Grey", 0.08)
        mb.box((0.9 * s, 0.9 * s, 2.0 * s), F.p(0.5 * s, 0, 1.0 * s), F.r(), "Dummy_Grey", 0.08)
        mb.box((2.0 * s, 1.0 * s, 2.0 * s), F.p(0, 0, 3.0 * s), F.r(), "Dummy_Grey", 0.08)
        mb.box((0.9 * s, 0.9 * s, 2.0 * s), F.p(-1.5 * s, 0, 3.0 * s), F.r(), "Dummy_Grey", 0.08)
        mb.box((0.9 * s, 0.9 * s, 2.0 * s), F.p(1.5 * s, 0, 3.0 * s), F.r(), "Dummy_Grey", 0.08)
        mb.box((1.15 * s, 1.15 * s, 1.15 * s), F.p(0, 0, 4.6 * s), F.r(), "Dummy_Grey", 0.25)
        return mb.finish()
    dummy("SCALE_Dummy_Spawn", 3, L.SPAWN[1] + 6, L.SPAWN_Z)
    dummy("SCALE_Dummy_Plaza", 6, -14, L.FLOOR + 0.3, D(180))
    dummy("SCALE_Dummy_Portal", L.PORTAL_X[0] + 4, 100, L.TERR, D(180))
    dummy("SCALE_Dummy_Mine", -66, -40, L.FLOOR + 0.3, D(45))
    dummy("SCALE_Dummy_Door", -13, -2, L.FLOOR + 0.3, D(180))


def clouds():
    """nuvens cartoon ao fundo (aglomerados de esferas), fora do alcance do jogador"""
    import random
    rng = random.Random(1212)
    mb = MB("SKY_Clouds", "02_TERRAIN", rng)
    for i in range(16):
        a = math.radians(rng.uniform(-10, 190))
        r = rng.uniform(520, 820)
        cx, cy = math.cos(a) * r, math.sin(a) * r + 60
        cz = rng.uniform(170, 280)
        n = rng.randint(6, 10)
        L_ = rng.uniform(60, 120)
        for k in range(n):
            f = k / (n - 1) - 0.5
            rr = rng.uniform(16, 30) * (1.25 - abs(f))
            mb.ico(rr, (cx + f * L_ * math.cos(a + 1.57), cy + f * L_ * math.sin(a + 1.57), cz + rng.uniform(-4, 8) + rr * 0.3),
                   "Cloud", 2, (1.0, 1.0, 0.62), jitter=0.12)
    mb.finish()


def compositor():
    """nevoa de profundidade (mist) + bloom leve; falha silenciosa se a API mudar"""
    sc = bpy.context.scene
    try:
        vl = sc.view_layers[0]
        vl.use_pass_mist = True
        w = sc.world
        w.mist_settings.start = 60.0
        w.mist_settings.depth = 900.0
        w.mist_settings.falloff = "QUADRATIC"
        ng = bpy.data.node_groups.new("CMP_Lobby", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        N = ng.nodes
        rl = N.new("CompositorNodeRLayers")
        out = N.new("NodeGroupOutput")
        mix = N.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["B"].default_value = (0.62, 0.76, 0.95, 1.0)
        mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = 0.55
        ng.links.new(rl.outputs["Mist"], mm.inputs[0])
        ng.links.new(mm.outputs[0], mix.inputs["Factor"])
        ng.links.new(rl.outputs["Image"], mix.inputs["A"])
        gl = N.new("CompositorNodeGlare")
        try:
            gl.glare_type = "BLOOM"
        except Exception:
            pass
        for nm, val in (("Threshold", 1.2), ("Strength", 0.35), ("Size", 0.6)):
            if nm in gl.inputs:
                gl.inputs[nm].default_value = val
        ng.links.new(mix.outputs["Result"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], out.inputs[0])
        sc.compositing_node_group = ng
        sc.render.use_compositing = True
        print("COMPOSITOR ok")
    except Exception as e:
        print("COMPOSITOR falhou:", e)