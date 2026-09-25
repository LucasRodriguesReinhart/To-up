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
    fm_scene.FOG.update(start=260.0, depth=1400.0, factor=0.35)
    fm_scene.setup_sun()
    bpy.context.scene.view_settings.exposure = 0.55


def sea():
    mb = MB("SKY_Sea", "02_TERRAIN", random.Random(3), detail="far", floor=-999)
    mb.box((4200.0, 4200.0, 1.0), (0, 0, L.SEA - 0.5), (0, 0, 0), "Sea_Water", 0.0)
    mb.finish()


def islets(detail="blockout"):
    """ilhotas flutuantes em volta (fora do alcance do jogador): rocha em cone invertido + gramado + arvores"""
    rng = random.Random(909)
    spots = [(-330.0, 120.0, 40.0, 26.0), (-300.0, -170.0, -10.0, 20.0), (-420.0, -20.0, 80.0, 16.0),
             (330.0, -150.0, 20.0, 24.0), (390.0, 60.0, 70.0, 18.0), (250.0, 330.0, 50.0, 22.0),
             (-210.0, 360.0, 90.0, 16.0), (80.0, -380.0, -30.0, 18.0), (-120.0, -390.0, 60.0, 14.0)]
    mb = MB("SKY_Islets", "02_TERRAIN", rng, detail="far", floor=-999)
    for x, y, z, r in spots:
        mb.cyl(r, r * 1.6, (x, y, z - r * 0.8), (0, 0, rng.uniform(0, 1)), "Cliff_Rock_Tan", 7, r2=r * 0.15,
               bevel=0.0)
        mb.cyl(r * 1.02, 1.2, (x, y, z + 0.1), (0, 0, 0), "Grass_Konoha", 7, bevel=0.0)
        for k in range(rng.randint(1, 3)):
            a = rng.uniform(0, 6.28)
            rr = rng.uniform(0, r * 0.5)
            h = rng.uniform(7, 12)
            tx, ty = x + rr * math.cos(a), y + rr * math.sin(a)
            mb.cyl(0.8, h * 0.5, (tx, ty, z + h * 0.25), (0, 0, 0), "Bark", 5, bevel=0.0)
            mb.ico(h * 0.35, (tx, ty, z + h * 0.62), "Leaf_Pine_Light", 1, (1, 1, 0.85))
    mb.finish()


def clouds():
    rng = random.Random(1212)
    mb = MB("SKY_Clouds", "02_TERRAIN", rng, detail="far", floor=-999)
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
    # cameras que imitam cada referencia (comparacao lado a lado)
    "CAM_Ref14": ((0, -272, 182), (0, 38, 0), 26),
    "CAM_Ref15": ((-140, -250, 170), (12, 38, 0), 26),
    "CAM_Ref16": ((-212, -214, 112), (34, 34, 6), 24),
    "CAM_Ref17": ((0, 372, 205), (0, -22, 0), 26),
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
    camera("CAM_DB_Gate", (gp[0] - ux * 32.0 - uy * 8.0, gp[1] - uy * 32.0 + ux * 8.0, L.EXIT_Z + 9.0),
           (gp[0], gp[1], L.EXIT_Z + 11.0), 20)
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
