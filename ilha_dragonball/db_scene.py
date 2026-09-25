# db_scene - mundo, sol, mar, ilhotas flutuantes, nuvens, cameras de QA e referencia de escala da Ilha 2 (Dragon Ball).
# Sol, tonemap e bloom: os mesmos da Ilha 1 (il_scene.setup) - a direcao de arte muda pela paleta e pela forma.
import math, random
import bpy
from mathutils import Vector
import db_lib as DL
from db_lib import MB, camera, dome
import db_layout as L
import il_scene           # setup/tone_emissives (sem dependencia da planta da Ilha 1)


def setup(res=(1600, 900), samples=32):
    il_scene.setup(res=res, samples=samples)


def tone_emissives():
    il_scene.ENERGY = tuple(il_scene.ENERGY) + ("DB_Cyan_Glow", "DB_Ball_Glow")
    il_scene.tone_emissives()


def sea():
    mb = MB("DB_Sky_Sea", "02_TERRAIN", random.Random(3), detail="far", floor=-999)
    mb.box((4200.0, 4200.0, 1.0), (0, 0, L.SEA - 0.5), (0, 0, 0), "Sea_Water", 0.0)
    mb.finish()


# a Ilha 1 fica ao SUL no referencial desta ilha (centro local ~(0, -458)): nada de ilhota no setor 225..315 graus
ISLET_SPOTS = [(-360.0, 120.0, 46.0, 22.0, True), (340.0, 180.0, 60.0, 18.0, False), (-300.0, 330.0, 70.0, 20.0, False),
               (60.0, 420.0, 40.0, 16.0, True), (380.0, -60.0, 30.0, 20.0, True), (-420.0, -40.0, 56.0, 16.0, False),
               (250.0, 380.0, 90.0, 14.0, False), (-160.0, 440.0, 26.0, 18.0, True), (440.0, 110.0, 16.0, 14.0, False)]


def islets():
    """ilhotas flutuantes em volta (fora do alcance): rocha pendente em estratos laranja + topo verde + palmeiras,
    algumas com um pod Capsule (a concept tem casinhas-domo nas ilhotas)"""
    rng = random.Random(909)
    mb = MB("DB_Sky_Islets", "02_TERRAIN", rng, detail="far", floor=-999)
    for x, y, z, r, pod in ISLET_SPOTS:
        for k, (f, dz) in enumerate(((1.0, -0.35), (0.8, -0.95), (0.55, -1.55), (0.3, -2.1))):
            ox, oy = rng.uniform(-0.12, 0.12) * r, rng.uniform(-0.12, 0.12) * r
            mb.rock((x + ox, y + oy, z + dz * r), (2 * r * f, 2 * r * f * rng.uniform(0.8, 1.0), r * 0.9),
                    "Cliff_Rock_DB" if k % 2 == 0 else "Cliff_Rock_DB_Dark", 1, jitter=0.3, flat_bottom=False)
        pts = [(x + r * rng.uniform(0.85, 1.05) * math.cos(a), y + r * rng.uniform(0.85, 1.05) * math.sin(a))
               for a in [2 * math.pi * i / 9 for i in range(9)]]
        mb.prism(pts, z - 0.6, z + 0.4, "Grass_DB")
        for k in range(rng.randint(1, 3)):
            a = rng.uniform(0, 6.28)
            rr = rng.uniform(0, r * 0.5)
            DL.FP.palm(mb, (x + rr * math.cos(a), y + rr * math.sin(a), z + 0.4), rng.uniform(9, 13), rng)
        if pod:
            px, py = x + r * 0.25, y - r * 0.2
            mb.cyl(3.4, 2.4, (px, py, z + 1.6), m="Plaster_DB_White", n=12, bevel=0.0)
            dome(mb, (px, py), 3.4, z + 2.8, "Roof_DB_Blue", n=12, rings=4, squash=0.85)
    mb.finish()


def clouds():
    rng = random.Random(1212)
    mb = MB("DB_Sky_Clouds", "02_TERRAIN", rng, detail="far", floor=-999)
    # saia de nuvens abracando o pe dos penhascos (a concept: a ilha nasce das nuvens)
    for i in range(18):
        a = math.radians(i * 20.0 + rng.uniform(-8, 8))
        R = DL.rim_r(math.degrees(a)) + rng.uniform(10.0, 40.0)
        cx, cy = math.cos(a) * R, math.sin(a) * R
        for k in range(rng.randint(4, 6)):
            rr = rng.uniform(14.0, 26.0)
            mb.ico(rr, (cx + rng.uniform(-22, 22), cy + rng.uniform(-22, 22), rng.uniform(-66.0, -36.0)), "Cloud", 2,
                   (1.25, 1.0, 0.55), jitter=0.12)
    for i in range(20):
        a = math.radians(rng.uniform(0, 360))
        if 225 < math.degrees(a) % 360 < 315:
            continue
        r = rng.uniform(340, 720)
        cx, cy = math.cos(a) * r, math.sin(a) * r
        low = i % 2 == 0
        cz = rng.uniform(-70, -20) if low else rng.uniform(150, 270)
        n = rng.randint(5, 9)
        Ln = rng.uniform(60, 130)
        for k in range(n):
            f = k / (n - 1) - 0.5
            rr = rng.uniform(14, 28) * (1.25 - abs(f))
            mb.ico(rr, (cx + f * Ln * math.cos(a + 1.57), cy + f * Ln * math.sin(a + 1.57), cz + rng.uniform(-4, 8)),
                   "Cloud", 2, (1.0, 1.0, 0.62), jitter=0.12)
    mb.finish()


G, A, H, S_, C = L.GROUND, L.ARENA, L.HUB, L.SUM, L.CAP
CAMS = {
    # visoes pedidas na missao (secao 37)
    "CAM_DB_Entry": ((0, -178, L.DECK + 10.0), (0, -70, G + 10.0), 20),
    "CAM_DB_Front": ((0, -380, 175), (0, 30, 20), 24),
    "CAM_DB_Left": ((-400, 30, 150), (0, 30, 20), 24),
    "CAM_DB_Right": ((400, 20, 150), (0, 30, 20), 24),
    "CAM_DB_Back": ((0, 440, 200), (0, 20, 20), 24),
    "CAM_DB_BirdEye": ((0, -20, 640), (0, 20, 0), 24),
    "CAM_DB_Mining": ((-52, -72, G + 14.0), (10, 10, A + 4.0), 18),
    "CAM_DB_Capsule": ((0, 88, H + 9.0), (0, 174, C + 22.0), 18),
    "CAM_DB_Summon": ((-72, -34, G + 10.0), (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], S_ + 18.0), 18),
    "CAM_DB_ShadowGate": None,     # calculada (frente do portao SG, na ponte de saida)
    # altura do jogador (olho ~5,2 acima do chao)
    "CAM_DB_PlayerHeight_Entry": ((0, -110, G + 5.2), (0, -30, G + 2.0), 24),
    "CAM_DB_PlayerHeight_Mining": ((0, -63, G + 5.2), (0, 6, A + 2.0), 24),
    "CAM_DB_PlayerHeight_Summon": ((-84, -8, G + 5.2), (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], S_ + 14.0), 22),
    "CAM_DB_PlayerHeight_ShadowGate": None,   # calculada (na ponte, 40 antes do portao)
    # cameras que imitam a concept aprovada (comparacao lado a lado)
    "CAM_DB_Ref_Main": ((0, -300, 235), (0, 30, 0), 26),
    "CAM_DB_Ref_Top": ((0, 0, 720), (0, 1, 0), 26),
    "CAM_DB_Ref_Front": ((0, -330, 130), (0, 40, 40), 24),
    "CAM_DB_Ref_Side": ((-360, -150, 150), (0, 30, 20), 24),
    "CAM_DB_Ref_Summon": ((-96, -26, S_ + 8.0), (L.SUMMON_TOWER[0], L.SUMMON_TOWER[1], S_ + 22.0), 20),
    "CAM_DB_Ref_Village": ((-58, 116, H + 6.0), (-86, 128, H + 5.0), 20),
    "CAM_DB_Ref_Capsule": ((0, 112, H + 5.0), (0, 174, C + 16.0), 20),
    "CAM_DB_Ref_Environment": ((-78, 70, H + 10.0), (-132, 110, 50.0), 20),
    "CAM_DB_Ref_Gate": None,       # calculada (portao SG de frente, como o painel da concept)
    # interior do Capsule (secao 17/30: nada de fachada falsa)
    "CAM_DB_CapsuleInterior": ((0, 138.0, C + 5.2), (0, 176.0, C + 6.0), 18),
}


def cameras():
    for n, v in CAMS.items():
        if v is None:
            continue
        loc, tgt, lens = v
        camera(n, loc, tgt, lens)
    gp = L.gate_sg_pos()
    ux, uy = L.exit_dir()
    z = L.EXIT_Z
    camera("CAM_DB_ShadowGate", (gp[0] - ux * 38.0 - uy * 9.0, gp[1] - uy * 38.0 + ux * 9.0, z + 11.0),
           (gp[0], gp[1], z + 16.0), 18)
    camera("CAM_DB_PlayerHeight_ShadowGate", (gp[0] - ux * 40.0 - uy * 5.0, gp[1] - uy * 40.0 + ux * 5.0, z + 5.2),
           (gp[0], gp[1], z + 9.0), 24)
    camera("CAM_DB_Ref_Gate", (gp[0] - ux * 30.0, gp[1] - uy * 30.0, z + 7.0), (gp[0], gp[1], z + 14.0), 22)
    bpy.context.scene.camera = bpy.data.objects["CAM_DB_Ref_Main"]


def scale_reference(visible=True):
    gp = L.gate_sg_pos()
    ux, uy = L.exit_dir()
    spots = [("SCALE_Dummy_Entry", 3.0, -92.0, G), ("SCALE_Dummy_Prom", 4.0, -64.0, G),
             ("SCALE_Dummy_Arena", 8.0, -30.0, A), ("SCALE_Dummy_Summon", -112.0, -4.0, S_ + 0.1),
             ("SCALE_Dummy_Capsule", 16.0, 116.0, H), ("SCALE_Dummy_CapsuleDoor", 3.0, 133.0, C),
             ("SCALE_Dummy_Hub", -40.0, 90.0, H),
             ("SCALE_Dummy_SGGate", gp[0] - ux * 9.0 - uy * 4.0, gp[1] - uy * 9.0 + ux * 4.0, L.EXIT_Z)]
    for n, x, y, z in spots:
        DL.dummy(n, x, y, z, visible=visible)
