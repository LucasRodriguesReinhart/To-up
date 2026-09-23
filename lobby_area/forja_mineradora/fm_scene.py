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
    sc.view_settings.exposure = 0.45
    sc.render.film_transparent = False


# ------------------------------------------------------------------ luz de fim de tarde (contraste quente x frio)
# Vetor que APONTA PARA O SOL (Blender, x leste / y norte / z cima): oeste-sudoeste, elevacao ~30 graus.
# Raspa a fachada da forja (face -Y) pela esquerda de quem chega do spawn. O materials_export usa o MESMO
# vetor no Lighting do Roblox (Roblox = (x, z, -y) do Blender).
SUN_DIR = Vector((-0.77, -0.41, 0.50)).normalized()
SUN_COLOR = (1.0, 0.78, 0.52)
SUN_POWER = 5.5
AMB_COLOR = (0.42, 0.52, 0.78)       # ceu que ilumina as sombras: frio
AMB_POWER = 0.55
FOG = dict(start=90.0, depth=480.0, factor=0.7, color=(0.66, 0.78, 0.95), curve=1.5)   # nevoa LINEAR de profundidade


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
    # Generated do mundo = direcao (-1..1): 0 = horizonte, 1 = zenite. Horizonte claro e frio (casa com a cor da
    # nevoa: as montanhas distantes somem no ceu, nao num degrau), zenite azul saturado (concept)
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.50, 0.68, 0.95, 1)
    cr.elements[1].position = 0.62
    cr.elements[1].color = (0.03, 0.15, 0.78, 1)
    e = cr.elements.new(0.16)
    e.color = (0.20, 0.44, 0.93, 1)
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 1.2
    # luz ambiente separada do ceu visto pela camera: azul frio e fraca -> sombras frias contra o sol quente
    amb = nt.nodes.new("ShaderNodeBackground")
    amb.inputs["Color"].default_value = (*AMB_COLOR, 1)
    amb.inputs["Strength"].default_value = AMB_POWER
    lp = nt.nodes.new("ShaderNodeLightPath")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(amb.outputs[0], mx.inputs[1])
    nt.links.new(bg.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])


def setup_sun():
    # sol de fim de tarde, quente e baixo (elevacao ~30), de oeste-sudoeste: vetor em SUN_DIR
    q = SUN_DIR.to_track_quat("Z", "Y")          # o SUN ilumina ao longo de -Z local -> +Z local aponta para o sol
    sun = light("SUN_Key", "SUN", (0, 0, 200), SUN_POWER, SUN_COLOR, 0.0, rot=tuple(q.to_euler()))
    sun.data.angle = D(2.0)
    sun["sun_dir_blender"] = tuple(round(c, 3) for c in SUN_DIR)
    # contraluz de ceu: azul fraco do lado oposto ao sol (separa silhuetas; nada de fill quente que lava a sombra)
    back = Vector((-SUN_DIR.x, -SUN_DIR.y, 0.9)).normalized()
    qb = back.to_track_quat("Z", "Y")
    fill = light("SUN_Fill_Sky", "SUN", (0, 0, 200), 0.35, (0.55, 0.68, 1.0), 0.0, rot=tuple(qb.to_euler()))
    fill.data.use_shadow = False
    compositor()


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
    ds = [dummy("SCALE_Dummy_Spawn", 3, L.SPAWN[1] + 6, L.SPAWN_Z),
          dummy("SCALE_Dummy_Plaza", 6, -14, L.FLOOR + 0.3, D(180)),
          dummy("SCALE_Dummy_Portal", L.PORTAL_X[0] + 4, 100, L.TERR, D(180)),
          dummy("SCALE_Dummy_Mine", -66, -40, L.FLOOR + 0.3, D(45)),
          dummy("SCALE_Dummy_Door", -13, -2, L.FLOOR + 0.3, D(180))]
    # continuam no arquivo (medida no viewport), mas fora das cameras de aprovacao
    for o in ds:
        if o is not None:
            o.hide_render = True


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
    """nevoa de profundidade LINEAR (passe Mist, so na geometria: o ceu fica fora pela mascara de profundidade) +
    bloom leve; falha silenciosa se a API mudar"""
    sc = bpy.context.scene
    try:
        vl = sc.view_layers[0]
        vl.use_pass_mist = True
        vl.use_pass_z = True
        w = sc.world
        w.mist_settings.start = FOG["start"]
        w.mist_settings.depth = FOG["depth"]
        w.mist_settings.falloff = "LINEAR"
        old = bpy.data.node_groups.get("CMP_Lobby")
        if old is not None:
            bpy.data.node_groups.remove(old)
        ng = bpy.data.node_groups.new("CMP_Lobby", "CompositorNodeTree")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        N = ng.nodes
        rl = N.new("CompositorNodeRLayers")
        out = N.new("NodeGroupOutput")
        mix = N.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["B"].default_value = (*FOG["color"], 1.0)
        # entrada suave (^curve) sobre o passe LINEAR: o meio-plano (portais a ~260 do CAM_Front) nao lava;
        # a 300 studs ~20%, nas cordilheiras (>500) chega aos 70%
        pw = N.new("ShaderNodeMath"); pw.operation = "POWER"; pw.inputs[1].default_value = FOG["curve"]
        ng.links.new(rl.outputs["Mist"], pw.inputs[0])
        mm = N.new("ShaderNodeMath"); mm.operation = "MULTIPLY"; mm.inputs[1].default_value = FOG["factor"]
        ng.links.new(pw.outputs[0], mm.inputs[0])
        # ceu (profundidade ~infinita) nao recebe nevoa: o degrade do setup_world ja faz o horizonte
        sky = N.new("ShaderNodeMath"); sky.operation = "LESS_THAN"; sky.inputs[1].default_value = 2500.0
        ng.links.new(rl.outputs["Depth"], sky.inputs[0])
        mk = N.new("ShaderNodeMath"); mk.operation = "MULTIPLY"
        ng.links.new(mm.outputs[0], mk.inputs[0])
        ng.links.new(sky.outputs[0], mk.inputs[1])
        ng.links.new(mk.outputs[0], mix.inputs["Factor"])
        ng.links.new(rl.outputs["Image"], mix.inputs["A"])
        gl = N.new("CompositorNodeGlare")
        try:
            gl.inputs["Type"].default_value = "Bloom"      # Blender 5.x: tipo e entrada MENU (padrao = Streaks)
        except Exception:
            try:
                gl.glare_type = "BLOOM"
            except Exception:
                pass
        for nm, val in (("Threshold", 1.2), ("Strength", 0.3), ("Size", 0.6)):
            if nm in gl.inputs:
                gl.inputs[nm].default_value = val
        ng.links.new(mix.outputs["Result"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], out.inputs[0])
        sc.compositing_node_group = ng
        sc.render.use_compositing = True
        print("COMPOSITOR ok")
    except Exception as e:
        print("COMPOSITOR falhou:", e)