# il_scene - mundo, sol, mar, ilhotas flutuantes, nuvens, cameras de QA e referencia de escala da Ilha 1
import math, random
import bpy
from mathutils import Vector
import il_lib as IL
from il_lib import MB, D, camera, light
import il_layout as L
import fm_scene

# sol do meio da tarde vindo de sudoeste (as referencias: luz da frente-esquerda de quem chega do lobby)
SUN_DIR = Vector((-0.42, -0.62, 0.66)).normalized()


def setup(res=(1600, 900), samples=32):
    fm_scene.setup_render(res, samples)
    fm_scene.setup_world()
    fm_scene.SUN_DIR = SUN_DIR
    fm_scene.SUN_POWER = 5.0
    fm_scene.FOG.update(start=480.0, depth=2200.0, factor=0.2)
    fm_scene.setup_sun()
    # previa saturada como as referencias (cartoon): Standard em vez do AgX do lobby (AgX dessatura laranja/azul
    # fortes: a barreira DB saia salmao). So o Blender; a cor do Roblox vem de rbx_color.
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
                for nm, val in (("Threshold", 0.85), ("Strength", 0.45), ("Size", 0.65)):
                    if nm in nd.inputs:
                        nd.inputs[nm].default_value = val


ENERGY = ("DB_Energy_Glow", "P_Shadow_Glow", "P_DS_Glow", "P_OP_Glow", "P_Gold_Glow", "P_OPM_Glow", "P_DB_Glow")


def tone_emissives(cap=1.35, crystal=0.55, energy=0.75):
    """SO a previa do Blender: sob AgX, emissao 3-5 estoura em creme/branco (estrela, barreiras, cristais). Limita a
    forca da emissao para a cor ler saturada como nas referencias. A cor do Roblox (rbx_color/Neon) nao muda."""
    n = 0
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for nd in m.node_tree.nodes:
            if nd.type != "BSDF_PRINCIPLED":
                continue
            s = nd.inputs["Emission Strength"]
            if s.is_linked or s.default_value <= 0:
                continue
            lim = crystal if (m.name.startswith("Crystal_") and "Glow" not in m.name and "Core" not in m.name) else cap
            if m.name in ENERGY:
                lim = energy
            if m.name.startswith(("Lantern_Glow", "Window_Warm")):
                continue
            if s.default_value > lim:
                s.default_value = lim
                n += 1
    print("SCENE emissivos limitados: %d materiais" % n)


def sea():
    mb = MB("SKY_Sea", "02_TERRAIN", random.Random(3), detail="far", floor=-999)
    mb.box((4200.0, 4200.0, 1.0), (0, 0, L.SEA - 0.5), (0, 0, 0), "Sea_Water", 0.0)
    mb.finish()


def islets(detail="blockout"):
    """ilhotas flutuantes em volta (fora do alcance do jogador): rocha em cone invertido + gramado + arvores"""
    rng = random.Random(909)
    # rodada 2: todas a >= 420 do centro, fora do lobby (y local >= -180 ou |x| >= 360) e fora de uma faixa de 80 ao
    # longo do eixo da saida (45 graus a partir de (96,96)); rocha empilhada irregular, nao cone de festa
    spots = [(-430.0, 130.0, 40.0, 24.0), (380.0, -230.0, -10.0, 20.0), (-470.0, -40.0, 60.0, 16.0),
             (420.0, -120.0, 20.0, 22.0), (460.0, 60.0, 50.0, 18.0), (-300.0, 330.0, 50.0, 22.0),
             (-120.0, 440.0, 70.0, 16.0), (-390.0, -220.0, -30.0, 18.0), (60.0, 470.0, 30.0, 14.0)]
    mb = MB("SKY_Islets", "02_TERRAIN", rng, detail="far", floor=-999)
    import fm_veg_kit as VK
    for x, y, z, r in spots:
        # corpo: 4 rochas empilhadas afinando para baixo (pendente irregular)
        for k, (f, dz) in enumerate(((1.0, -0.35), (0.78, -0.95), (0.52, -1.5), (0.28, -2.0))):
            ox, oy = rng.uniform(-0.12, 0.12) * r, rng.uniform(-0.12, 0.12) * r
            mb.rock((x + ox, y + oy, z + dz * r), (2 * r * f, 2 * r * f * rng.uniform(0.8, 1.0), r * 0.9),
                    "Cliff_Rock_Tan" if k % 2 == 0 else "Cliff_Rock_Tan_Dark", 1, jitter=0.35, flat_bottom=False)
        pts = [(x + r * rng.uniform(0.85, 1.05) * math.cos(a), y + r * rng.uniform(0.85, 1.05) * math.sin(a))
               for a in [2 * math.pi * i / 9 for i in range(9)]]
        mb.prism(pts, z - 0.6, z + 0.4, "Grass_Konoha")
        for k in range(rng.randint(2, 4)):
            a = rng.uniform(0, 6.28)
            rr = rng.uniform(0, r * 0.55)
            VK.broadleaf(mb, (x + rr * math.cos(a), y + rr * math.sin(a), z + 0.4), rng.uniform(8, 13), rng, lod=2,
                         clear=3.0)
    mb.finish()


def clouds():
    rng = random.Random(1212)
    mb = MB("SKY_Clouds", "02_TERRAIN", rng, detail="far", floor=-999)
    # saia de nuvens abracando o pe dos penhascos (as refs 14/15/16/18): r 170-230, z -70..-40, mais densa sob as pontes
    for i in range(16):
        a = math.radians(i * 22.5 + rng.uniform(-8, 8))
        r = rng.uniform(175.0, 225.0)
        cx, cy = math.cos(a) * r, math.sin(a) * r + 20.0
        for k in range(rng.randint(4, 6)):
            rr = rng.uniform(14.0, 26.0)
            mb.ico(rr, (cx + rng.uniform(-22, 22), cy + rng.uniform(-22, 22), rng.uniform(-70.0, -42.0)), "Cloud", 2,
                   (1.25, 1.0, 0.55), jitter=0.12)
    for bx, by in ((0.0, -160.0), (0.0, -190.0), L.exit_point(70.0), L.exit_point(100.0)):
        for k in range(3):
            mb.ico(rng.uniform(16.0, 24.0), (bx + rng.uniform(-18, 18), by + rng.uniform(-18, 18), rng.uniform(-58, -38)),
                   "Cloud", 2, (1.3, 1.0, 0.5), jitter=0.12)
    for i in range(22):
        a = math.radians(rng.uniform(0, 360))
        r = rng.uniform(330, 700)
        cx, cy = math.cos(a) * r, math.sin(a) * r
        low = i % 2 == 0
        cz = rng.uniform(-70, -20) if low else rng.uniform(140, 260)
        n = rng.randint(5, 9)
        Ln = rng.uniform(60, 130)
        for k in range(n):
            f = k / (n - 1) - 0.5
            rr = rng.uniform(14, 28) * (1.25 - abs(f))
            mb.ico(rr, (cx + f * Ln * math.cos(a + 1.57), cy + f * Ln * math.sin(a + 1.57), cz + rng.uniform(-4, 8)),
                   "Cloud", 2, (1.0, 1.0, 0.62), jitter=0.12)
    mb.finish()


CAMS = {
    # visoes pedidas na missao
    "CAM_Entry": ((0, -150, L.G + 9.0), (0, 0, 10.0), 20),
    "CAM_Center": ((0, -72, L.RING + 11.0), (0, 120, 18.0), 18),
    "CAM_Front": ((0, -330, 170), (0, 20, 8), 24),
    "CAM_Left": ((-340, 10, 150), (0, 20, 8), 24),
    "CAM_Right": ((350, 0, 150), (0, 20, 8), 24),
    "CAM_Back": ((0, 390, 190), (0, 0, 0), 24),
    "CAM_BirdEye": ((0, -40, 560), (0, 30, 0), 24),
    "CAM_Mining": ((-42, -72, L.RING + 14.0), (8, 12, L.PIT + 4.0), 18),
    "CAM_Summon": ((-72, -12, L.RING + 8.0), (-128, 32, L.T1 + 16.0), 18),
    "CAM_Village": ((0, 52, L.RING + 10.0), (0, 150, L.T2 + 12.0), 18),
    "CAM_NextBridge": ((78, 78, L.T1 + 10.0), (176, 176, L.T1 + 10.0), 20),
    "CAM_DB_Gate": None,   # calculada (frente do portao)
    # altura do jogador (olho ~5,2 acima do chao; lente mais aberta, sem visao aerea) - passe de polimento
    "CAM_PlayerHeight_Entry": ((0, -115, L.G + 5.2), (0, -35, L.G + 2.0), 24),
    "CAM_PlayerHeight_Mining": ((0, -70, L.RING + 5.2), (0, 5, L.PIT + 2.0), 24),
    "CAM_PlayerHeight_Summon": ((-92, 18, L.T1 + 5.2), (L.SUMMON_C[0], L.SUMMON_C[1], L.T1 + 12.0), 22),
    "CAM_PlayerHeight_Gate": None,   # calculada (patamar de interacao do portao DB, olhando a barreira)
    # cameras que imitam cada referencia (comparacao lado a lado)
    "CAM_Ref14": ((0, -272, 182), (0, 38, 0), 26),
    "CAM_Ref15": ((-140, -250, 170), (12, 38, 0), 26),
    "CAM_Ref16": ((-212, -214, 112), (34, 34, 6), 24),
    "CAM_Ref17": ((0, 330, 300), (0, -30, 0), 26),
    "CAM_Ref18": ((0, -190, 345), (0, 46, 0), 24),
}


def cameras():
    for n, v in CAMS.items():
        if v is None:
            continue
        loc, tgt, lens = v
        camera(n, loc, tgt, lens)
    gp = L.gate_db_pos()
    ux, uy = L.exit_dir()
    camera("CAM_DB_Gate", (gp[0] - ux * 36.0 - uy * 9.0, gp[1] - uy * 36.0 + ux * 9.0, L.EXIT_Z + 10.0),
           (gp[0], gp[1], L.EXIT_Z + 18.0), 16)
    # altura do jogador: bem recuado na ponte antes do portao (40 studs, como a CAM_DB_Gate normal, so mais baixa)
    # - perto, a barreira de energia Neon estoura o bloom da previa (no Roblox nao acontece, Transparency 0,2)
    camera("CAM_PlayerHeight_Gate", (gp[0] - ux * 40.0 - uy * 7.0, gp[1] - uy * 40.0 + ux * 7.0, L.EXIT_Z + 5.2),
           (gp[0], gp[1], L.EXIT_Z + 9.0), 24)
    bpy.context.scene.camera = bpy.data.objects["CAM_Ref14"]


def scale_reference(visible=True):
    """dummy R15 de 5,2 studs (mesma convencao do lobby) nos pontos-chave"""
    from fm_parts import Frame

    def dummy(name, x, y, z, ang=0.0):
        mb = MB(name, "_SCALE_REFERENCE")
        F = Frame(x, y, z, ang)
        for dx, dz, sx, sz in ((-0.5, 1.0, 0.9, 2.0), (0.5, 1.0, 0.9, 2.0), (0, 3.0, 2.0, 2.0), (-1.5, 3.0, 0.9, 2.0),
                               (1.5, 3.0, 0.9, 2.0)):
            mb.box((sx, 0.9 if sx < 2 else 1.0, sz), F.p(dx, 0, dz), F.r(), "Dummy_Grey", 0.08)
        mb.box((1.15, 1.15, 1.15), F.p(0, 0, 4.6), F.r(), "Dummy_Grey", 0.25)
        ob = mb.finish()
        ob.hide_render = not visible
        return ob
    gp = L.gate_db_pos()
    spots = [("SCALE_Dummy_Entry", 3.0, -100.0, L.G), ("SCALE_Dummy_Ring", 4.0, -70.0, L.RING),
             ("SCALE_Dummy_Pit", 8.0, -30.0, L.PIT), ("SCALE_Dummy_Summon", -112.0, 18.0, L.T1 + 0.4),
             ("SCALE_Dummy_Hall", 4.0, 134.0, L.T2), ("SCALE_Dummy_DBGate", gp[0] - 8.0, gp[1] - 6.0, L.EXIT_Z),
             ("SCALE_Dummy_Mill", 86.0, 4.0, L.G)]
    for n, x, y, z in spots:
        dummy(n, x, y, z)
