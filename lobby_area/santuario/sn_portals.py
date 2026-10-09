# sn_portals.py - SEMICIRCULO DOS PORTAIS (oeste da praca): os 6 portais APROVADOS (vila_medieval/vm_portals ->
# fm_pv3_* + fm_portals.onepiece, SO LEITURA, mesmas sementes do portal_studio) com a planta trocada em memoria
# (vm_portals.L = sn_layout), cada um sobre um ESTRADO ANTIGO do santuario:
#   - estrado de 12 lados em 2 degraus (cota 7 -> 8,2), lajes chanfradas no topo, anel entalhado com runas acesas
#     na cor do mundo, degrau dianteiro largo voltado para a praca;
#   - placa de pedra com o NOME DO MUNDO em letras de ouro no degrau da frente;
#   - 2 braseiros nos cantos da frente; atras, um arco-fragmento quebrado (2 colunas + 3 aduelas) emoldurando o portal;
#   - cristais da cor do mundo brotando na borda de tras.
# Nada a menos de 12 studs do centro do disco do portal na frente (circulacao livre).
import math
import os
import sys

import bpy
import fm_lib
import sn_lib as SL
import sn_layout as L
from sn_kit import column, worn_block, rubble, crystal_cluster, brazier, moss_patch, rng
from wb_kit import Fr, bb, beam, cyl, text
from wb_lib import RB, V

COLL = "06_PORTALS"
AREA = "Court"
DAIS_R = (15.0, 13.4)            # raio do degrau de baixo / de cima (12 lados)
WORLD = {
    "Naruto":       ("NARUTO", "SN_CrystalAmber", (255, 170, 60)),
    "DragonBall":   ("DRAGON BALL", "SN_CrystalAmber", (255, 150, 40)),
    "ShadowGarden": ("SHADOW GARDEN", "SN_CrystalViolet", (186, 120, 255)),
    "DemonSlayer":  ("DEMON SLAYER", "SN_CrystalRed", (255, 80, 70)),
    "OnePiece":     ("ONE PIECE", "SN_CrystalBlue", (90, 170, 255)),
    "OnePunchMan":  ("ONE PUNCH MAN", "SN_CrystalAmber", (255, 210, 90)),
}


def portals():
    vila = os.path.join(SL.W.ROOT, "lobby_area", "vila_medieval")
    if vila not in sys.path:
        sys.path.insert(0, vila)
    import fm_pv3
    import vm_portals
    fm_pv3.load()
    fm_lib.make_materials()
    vm_portals.L = L
    before = set(bpy.data.objects)
    report = vm_portals.build()
    new = [o for o in bpy.data.objects if o not in before]
    return new, report


def _poly(n, r, rot=0.0):
    return [(r * math.cos(rot + 2 * math.pi * k / n), r * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]


def dais(b, i):
    key, aid = L.PORTALS[i]
    label, crys, rgb = WORLD[key]
    (x, z), (fx, fz) = L.portal_pos(i)
    F = Fr.rbx(x, z, L.Y_PLAZA, fx, fz)                 # +y local = para a praca
    y0 = L.Y_GRASS - 0.6
    r0, r1 = DAIS_R
    rot = math.pi / 12
    from wb_kit import poly_prism
    poly_prism(b, F, _poly(12, r0, rot), y0 - L.Y_PLAZA, 7.6 - L.Y_PLAZA, "SN_Ashlar_Dark")
    poly_prism(b, F, _poly(12, r0 + 0.25, rot), 7.6 - L.Y_PLAZA - 0.3, 7.6 - L.Y_PLAZA, "SN_Ashlar")
    poly_prism(b, F, _poly(12, r1, rot), 7.6 - L.Y_PLAZA, L.Y_PORTAL - L.Y_PLAZA - 0.04, "SN_Carved")
    # lajes do topo (anel externo do estrado de cima) + runas acesas na cor do mundo no friso
    zt = L.Y_PORTAL - L.Y_PLAZA - 0.04
    rr = rng("dais", i)
    for k in range(12):
        a0 = rot + 2 * math.pi * k / 12
        a1 = rot + 2 * math.pi * (k + 1) / 12
        am = (a0 + a1) / 2
        rm = r1 - 0.9
        p0 = (rm * math.cos(a0 + 0.04), rm * math.sin(a0 + 0.04), zt + 0.02)
        p1 = (rm * math.cos(a1 - 0.04), rm * math.sin(a1 - 0.04), zt + 0.02)
        beam(b, F, p0, p1, 1.5, 0.12, "SN_Plaza")
        # glifo aceso no espelho do degrau de cima (face vertical do 12-gono)
        gx, gy = (r1 + 0.02) * math.cos(am), (r1 + 0.02) * math.sin(am)
        tx, ty = -math.sin(am), math.cos(am)
        for s in (-1, 1):
            beam(b, F, (gx + tx * s * 0.9, gy + ty * s * 0.9, zt - 0.35), (gx + tx * s * 0.3, gy + ty * s * 0.3, zt - 0.15),
                 0.12, 0.14, "SN_Rune")
    # placa com o nome do mundo no degrau da frente
    Fp = Fr(F.p(0, r0 - 0.4, 0), (F.f.x, F.f.y))
    bb(b, Fp, -len(label) * 0.62 - 1.2, len(label) * 0.62 + 1.2, -0.6, 0.15, y0 - L.Y_PLAZA, 1.15, "SN_Carved")
    text(b, Fp, label, 0.78, "SN_Gold", 0.0, 0.2, 0.62, thick=0.18, bold=True)
    # braseiros nos cantos da frente
    for s in (-1, 1):
        a = math.pi / 2 + s * 0.62
        brazier(b, F, (r1 - 1.6) * math.cos(a), (r1 - 1.6) * math.sin(a), zt, 3.6, "L_SN_Brazier_P%d_%d" % (i + 1, s))
    # arco-fragmento quebrado atras (2 colunas, uma inteira e uma partida, e aduelas caidas)
    bk = -(r1 - 2.4)
    for s, broken in ((-1, None), (1, 9.5)):
        column(b, F, s * 11.5, bk, zt, 18.0, r0=1.25, seed=("pc", i, s), broken=broken)
    for k in range(3):
        worn_block(b, F, 11.5 + rr.uniform(-2.5, 2.5) + 2.5, bk + rr.uniform(-3, 3), zt + 0.7, (2.4, 1.6, 1.4), "SN_Ashlar",
                   seed=("ad", i, k), chips=3, turn=rr.uniform(0, 180), tilt=(rr.uniform(-15, 15), rr.uniform(-15, 15)))
    # lintel quebrado apoiado na coluna inteira, inclinado ate o chao
    worn_block(b, F, -6.5, bk - 0.4, zt + 9.0, (13.0, 1.8, 1.6), "SN_Ashlar", seed=("lin", i), chips=3, turn=0.0,
               tilt=(0.0, -38.0))
    crystal_cluster(b, F, -7.0, bk - 1.2, zt, 1.5, crys, seed=("pcr", i))
    crystal_cluster(b, F, 8.0, bk - 0.6, zt, 1.1, crys, seed=("pcr2", i))
    moss_patch(b, F, -9.0, -6.0, zt + 0.03, 6.0, 4.0, seed=("pm", i))
    moss_patch(b, F, 10.0, 4.0, 7.6 - L.Y_PLAZA + 0.03, 4.0, 3.0, seed=("pm2", i))
    rubble(b, F, 13.5, -9.0, 7.6 - L.Y_PLAZA, 3.0, 6, "SN_Ashlar", seed=("pr", i))
    # colisao: estrado (2 cilindros como caixas giradas) e colunas
    for (rad, top) in ((r0, 7.6), (r1, L.Y_PORTAL)):
        for k in range(3):
            fm_lib.col_box(AREA, (rad * 2 * 0.87, rad * 2 * 0.5, top - y0), F.p(0, 0, (top + y0) / 2 - L.Y_PLAZA),
                           (0, 0, F.yaw() + k * math.pi / 3))
    for s in (-1, 1):
        fm_lib.col_box(AREA, (2.8, 2.8, 18.0), F.p(s * 11.5, bk, zt + 9.0), (0, 0, F.yaw()))
    fm_lib.marker("LETREIRO_Portal%d" % (i + 1), F.p(0, 4.0, 26.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"texto": label, "alcance": 150})


def build():
    SL.register()
    for k, (lbl, crys, rgb) in WORLD.items():
        if crys not in fm_lib.MATS:
            fm_lib.MATS[crys] = (fm_lib.S(*rgb), 0.3, 0.0, 1.8, fm_lib.S(*rgb), 0.0)
    fm_lib.make_materials()
    new, report = portals()
    b = SL.Build("WB_Court_Dais", COLL)
    for i in range(len(L.PORTALS)):
        dais(b, i)
    objs = b.finish()
    return new, report, objs
