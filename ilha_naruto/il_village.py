# il_village - zona VILLAGE da Ilha 1 (Vila da Folha): salao principal (entravel), loja de armas ninja (entravel),
# torre d'agua redonda (sem porta), barraca de ramen (entravel) e os 2 estandartes da escadaria central.
# Substitui il_blockout.village(). Posicoes/niveis/raios de il_layout (MAIN_HALL, BLUE_W, BLUE_E, RAMEN, T1, T2).
# Referencias: ref_14/15/17 (salao redondo vermelho de 2 niveis ladeado por 2 predios redondos azuis).
# Orcamento: cada predio e UM objeto (casca + interior) com teto de variantes (VMB) -> MeshParts por material.
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import mk
import fm_lib
from fm_lib import D, S, col_box, col_box2, light
import il_layout as L
import fm_parts as FP
from fm_parts import Frame
import fm_portal_kit as PK
import il_village_kit as K
from il_village_kit import VMB, pol, W, tan_box, tan_frame, col_ring, col_disk

# ------------------------------------------------------------------ materiais novos da zona (<= 6)
fm_lib.MATS.setdefault("Metal_VilSteel", (S(198, 206, 216), 0.3, 0.9, 0, None, 0.02))     # laminas
fm_lib.MATS.setdefault("Cloth_VilNoren", (S(240, 232, 214), 0.9, 0.0, 0, None, 0.04))     # cortina do ramen
fm_lib.MATS.setdefault("Cloth_VilLantern", (S(212, 46, 34), 0.8, 0.0, 0, None, 0.04))     # papel vermelho

T1, T2 = L.T1, L.T2
HX, HY, HR = L.MAIN_HALL
SX, SY, SR = L.BLUE_W
EX, EY, ER = L.BLUE_E
RX, RY, RW, RD, RYAW = L.RAMEN
COLL = "04_VILLAGE"

# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    "CAM_Village_Hall34": ((30.0, 114.0, T2 + 16.0), (0.0, 158.0, T2 + 16.0), 22),
    "CAM_Village_Player": ((3.0, 131.0, T2 + 5.0), (0.0, 160.0, T2 + 13.0), 18),
    "CAM_Village_HallInterior": ((0.8, 144.2, T2 + 7.5), (0.0, 170.0, T2 + 6.0), 14),
    "CAM_Village_HallDesk": ((-8.0, 150.5, T2 + 6.5), (1.5, 170.0, T2 + 6.0), 16),
    "CAM_Village_HallUp": ((6.0, 146.0, T2 + 3.0), (-2.0, 162.0, T2 + 22.0), 14),
    "CAM_Village_WeaponInterior": ((SX + 1.2, SY - 8.2, T2 + 7.0), (SX - 1.0, SY + 7.0, T2 + 4.5), 14),
    "CAM_Village_Weapon": ((SX + 26.0, SY - 26.0, T2 + 8.0), (SX, SY, T2 + 11.0), 20),
    "CAM_Village_Ramen": ((RX + 9.0, RY - 20.0, T1 + 7.0), (RX, RY + 1.0, T1 + 5.0), 20),
    "CAM_Village_RamenBack": ((RX + 17.0, RY + 13.0, T1 + 9.0), (RX, RY, T1 + 5.0), 20),
    "CAM_Village_RamenInside": ((RX - 6.5, RY - 5.0, T1 + 5.5), (RX + 3.0, RY + 4.0, T1 + 3.2), 14),
    "CAM_Village_Tower": ((EX - 24.0, EY - 28.0, T2 + 10.0), (EX, EY, T2 + 15.0), 20),
    "CAM_Village_Back": ((16.0, 198.0, L.CLIFF_TOP + 34.0), (0.0, 150.0, T2 + 8.0), 22),
    "CAM_Village_Side": ((-112.0, 138.0, T2 + 26.0), (-20.0, 158.0, T2 + 10.0), 20),
    "CAM_Village_SideE": ((112.0, 138.0, T2 + 26.0), (20.0, 158.0, T2 + 10.0), 20),
    "CAM_Village_Banners": ((3.0, 87.5, T1 + 3.0), (0.0, 110.0, T1 + 8.0), 16),
}

DOOR_A = 270.0      # todas as portas ao sul
def leaf_pose(s, x_hinge, y_hinge, length, open_deg=45.0):
    """centro (x, y local) e yaw de uma folha de porta aberta para dentro (90 + open_deg graus, rente a parede
    curva); s = -1 oeste, +1 leste; x_hinge = distancia (sem sinal) da dobradica ao eixo da porta"""
    a = math.radians(open_deg)
    dx, dy = s * math.sin(a), math.cos(a)
    return (s * x_hinge + dx * length / 2, y_hinge + dy * length / 2), -s * a


# ================================================================== SALAO PRINCIPAL
HALL = dict(r_pl=22.0, r_wo=20.5, r_wi=19.2, fl=1.2, wall_top=15.9, door_hw=5.0, door_h=12.4,
            up_ro=13.8, up_ri=12.8, up_top=27.3, ceil=15.8, ceil2=26.4)
SKIRT1 = [(26.0, 14.0), (22.5, 15.2), (18.0, 17.2), (13.4, 19.7)]
ROOF2 = [(17.8, 25.2), (14.0, 27.8), (10.2, 30.4), (6.6, 32.8)]
BOOKCASES = (50.0, 70.0, 110.0, 130.0)


def main_hall():
    C = (HX, HY, T2)
    H = HALL
    rng = random.Random(4101)
    mb = VMB("VIL_MainHall", COLL, rng, detail="hero", vcap=1)
    fl = H["fl"]
    dh = math.degrees(math.asin(H["door_hw"] / H["r_wo"]))
    # ---- embasamento de pedra + escada de 2 degraus ao sul (ate a praca do T2, y ~137.3)
    K.plinth(mb, C, H["r_pl"], fl, rng, notch=(H["door_hw"], -19.0), n=48)
    mb.box((2 * H["door_hw"], 1.7, 0.6), W(C, 0, -21.85, 0.3), (0, 0, 0), "Stone_Wall_Light", 0.1)
    mb.box((2 * H["door_hw"], 2.1, fl), W(C, 0, -20.1, fl / 2), (0, 0, 0), "Stone_Wall_Light", 0.1)
    mb.box((2 * H["door_hw"] + 0.2, 0.25, 0.14), W(C, 0, -22.62, 0.55), (0, 0, 0), "Stone_Wall_Dark", 0.0)
    for s in (-1, 1):
        mb.box((0.9, 3.4, 1.5), W(C, s * (H["door_hw"] + 0.45), -20.8, 0.75), (0, 0, 0), "Stone_Wall_Dark", 0.12)
    # ---- tambor de baixo: reboco creme com vao da porta (vao livre 9,6 x 12,4)
    K.ring_wall(mb, C, H["r_wi"], H["r_wo"], 0.6, H["wall_top"], "Plaster_Cream", 48, gaps=[(DOOR_A, dh)])
    K.lathe(mb, C, [(H["r_wi"], fl + H["door_h"]), (H["r_wo"], fl + H["door_h"]), (H["r_wo"], H["wall_top"]),
                    (H["r_wi"], H["wall_top"])], "Plaster_Cream", 4, DOOR_A - dh, DOOR_A + dh)
    # rodape de pedra e faixa de laca vermelha no alto (arquitrave)
    K.ring_wall(mb, C, H["r_wo"] - 0.1, H["r_wo"] + 0.3, 0.9, 2.4, "Stone_Wall_Dark", 56, gaps=[(DOOR_A, dh + 1.5)])
    K.lathe(mb, C, [(H["r_wo"] - 0.1, 13.9), (H["r_wo"] + 0.35, 13.9), (H["r_wo"] + 0.35, 14.8),
                    (H["r_wo"] - 0.1, 14.8)], "Wood_Lacquer_Red", 56)
    # pilares de laca vermelha (18 posicoes; a da porta fica vazia; os 2 do portal sao maiores, com aneis de ouro)
    for k in range(1, 18):
        a = DOOR_A + 20.0 * k
        big = k in (1, 17)
        rr = 1.05 if big else 0.82
        p = pol(C, H["r_wo"] + 0.25, a)
        mb.cyl(rr, 13.0, p + Vector((0, 0, fl + 6.5)), (0, 0, 0), "Wood_Lacquer_Red", 10, bevel=0.0)
        mb.box((rr * 2 + 0.6, rr * 2 + 0.6, 0.8), p + Vector((0, 0, fl + 0.4)), (0, 0, math.radians(a)),
               "Stone_Wall_Light", 0.0)
        mb.box((rr * 2 + 0.5, rr * 2 + 0.5, 0.5), p + Vector((0, 0, 13.65)), (0, 0, math.radians(a)), "Wood_Dark", 0.0)
        if big:
            for zz in (fl + 1.4, 11.8):
                mb.cyl(rr + 0.12, 0.35, p + Vector((0, 0, zz)), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
    # faixa de janelas quentes entre os pilares
    for k in range(1, 17):
        K.drum_window(mb, C, H["r_wo"], DOOR_A + 10.0 + 20.0 * k, 3.3, 6.0, 10.6, jambs=False)
    # ---- portal: batentes, verga, placa dourada, lanternas
    for s in (-1, 1):
        mb.box((0.8, 1.7, H["door_h"] + 0.2), W(C, s * (H["door_hw"] + 0.2), -19.85, fl + H["door_h"] / 2),
               (0, 0, 0), "Wood_Lacquer_Red", 0.1)
    mb.box((2 * H["door_hw"] + 1.6, 1.8, 0.9), W(C, 0, -19.95, fl + H["door_h"] + 0.35), (0, 0, 0),
           "Wood_Lacquer_Red", 0.1)
    mb.box((4.6, 0.3, 1.0), W(C, 0, -21.0, 14.35), (0, 0, 0), "Metal_Gold", 0.05)
    mb.box((4.0, 0.3, 0.6), W(C, 0, -21.12, 14.35), (0, 0, 0), "Wood_Dark", 0.0)
    for s in (-1, 1):
        K.paper_lantern(mb, W(C, s * 7.6, -24.0, 14.6), r=1.05, h=2.0, paper="Lantern_Glow", cap="Wood_Dark",
                        band="Cloth_Red", hang=0.9)
    # folhas da porta ABERTAS para dentro (145 graus: descansam junto a parede curva, sem fechar a circulacao)
    for s in (-1, 1):
        lc, yaw = leaf_pose(s, H["door_hw"] - 0.25, -18.6, 4.6, 55.0)
        mb.box((0.3, 4.6, H["door_h"] - 0.2), W(C, lc[0], lc[1], fl + H["door_h"] / 2), (0, 0, yaw), "Wood_Dark", 0.06)
        for zz in (2.6, fl + H["door_h"] / 2, H["door_h"] - 0.6):
            mb.box((0.4, 4.4, 0.35), W(C, lc[0], lc[1], zz), (0, 0, yaw), "Metal_Gold", 0.0)
    # ---- 1o beiral (terracota) a +14: casca, fiadas (nervuras claras), testeira creme, cachorros
    K.cone_roof(mb, C, SKIRT1, 0.8, "Roof_Terracotta", n=48, ribs=30, rib_m="Roof_Terracotta", rib_w=0.6,
                rib_h=0.3, fascia=(25.7, 26.35, 13.05, 14.25), fascia_m="Plaster_Cream", rafters=24,
                rafter_r=(20.9, 25.6), courses=(22.6, 18.3), course_m="Roof_Terracotta_B")
    # ---- tambor de cima (raio ~14) com janelas redondas
    K.lathe(mb, C, [(H["up_ri"], H["ceil"]), (H["up_ro"], H["ceil"]), (H["up_ro"], H["up_top"]),
                    (H["up_ri"], H["up_top"])], "Plaster_Cream", 40)
    for z0 in (19.4, 24.3):
        K.lathe(mb, C, [(H["up_ro"] - 0.1, z0), (H["up_ro"] + 0.3, z0), (H["up_ro"] + 0.3, z0 + 0.8),
                        (H["up_ro"] - 0.1, z0 + 0.8)], "Wood_Lacquer_Red", 36)
    for k in range(12):
        K.oculus(mb, C, H["up_ro"], DOOR_A + 15.0 + 30.0 * k, 22.1, 1.15)
        tan_box(mb, C, H["up_ro"] + 0.2, DOOR_A + 30.0 * k, (0.7, 0.5, 4.0), 22.1, "Wood_Lacquer_Red")
    # ---- 2o telhado conico + disco-emblema + terraco do topo com guarda-corpo + pinaculo
    K.cone_roof(mb, C, ROOF2, 0.7, "Roof_Terracotta", n=40, ribs=20, rib_m="Roof_Terracotta", rib_w=0.55,
                rib_h=0.28, fascia=(17.6, 18.15, 24.35, 25.45), fascia_m="Plaster_Cream", rafters=0,
                rafter_r=(14.4, 17.4), courses=(12.6,), course_m="Roof_Terracotta_B")
    zt = ROOF2[-1][1]
    K.lathe(mb, C, [(0.4, zt - 0.4), (7.0, zt - 0.4), (7.0, zt + 0.3), (0.4, zt + 0.3)], "Stone_Wall_Light", 24)
    for k in range(16):
        a = 360.0 * k / 16
        mb.box((0.38, 0.38, 1.5), pol(C, 6.55, a, zt + 1.05), (0, 0, math.radians(a)), "Wood_Lacquer_Red", 0.0)
    PK.ring(mb, W(C, 0, 0, zt + 1.75), 6.55, (1, 0, 0), (0, 1, 0), 0.34, 0.3, "Wood_Lacquer_Red", n=16)
    PK.ring(mb, W(C, 0, 0, zt + 0.9), 6.55, (1, 0, 0), (0, 1, 0), 0.2, 0.2, "Wood_Lacquer_Red", n=16)
    K.lathe(mb, C, [(0.4, zt + 0.2), (3.3, zt + 0.2), (3.3, zt + 2.4), (0.4, zt + 2.4)], "Plaster_Cream", 16)
    K.lathe(mb, C, [(3.25, zt + 1.6), (3.55, zt + 1.6), (3.55, zt + 2.3), (3.25, zt + 2.3)], "Wood_Lacquer_Red", 16)
    K.lathe(mb, C, [(4.3, zt + 2.3), (1.0, zt + 4.3), (0.6, zt + 4.3), (0.6, zt + 3.9), (3.9, zt + 1.9)],
            "Roof_Terracotta", 16)
    mb.cyl(0.95, 0.9, W(C, 0, 0, zt + 4.7), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
    mb.cyl(0.35, 3.2, W(C, 0, 0, zt + 6.7), (0, 0, 0), "Metal_Gold", 8, bevel=0.0)
    mb.ico(0.75, W(C, 0, 0, zt + 7.2), "Metal_Gold", 1)
    mb.cyl(0.26, 2.4, W(C, 0, 0, zt + 9.3), (0, 0, 0), "Metal_Gold", 6, r2=0.02, bevel=0.0)
    for s in (-1, 1):
        mb.cyl(0.18, 2.2, W(C, s * 0.9, 0, zt + 5.9), (0, s * 0.35, 0), "Metal_Gold", 6, r2=0.03, bevel=0.0)
    # disco-emblema grande na frente do 2o telhado (folha estilizada no circulo), inclinado com a agua
    tilt = math.radians(16.0)
    nrm = Vector((0.0, -math.cos(tilt), math.sin(tilt)))
    ec = W(C, 0, -15.3, 29.6)
    mb.box((3.8, 3.4, 3.6), ec + Vector((0, 2.3, -1.4)), (0, 0, 0), "Roof_Terracotta", 0.1)
    K.emblem_disk(mb, ec, nrm, 3.4, n=28)
    hall_interior(mb, C)
    mb.finish()
    # ---- colisao: embasamento, degraus, parede com vao, verga, pilares do portal
    A = "VillageHall"
    col_ring(A, C, H["r_wo"] - 0.3, H["r_pl"], 0.0, fl, K.arc_spans([(DOOR_A, 14.0)]), seg=20.0)
    col_disk(A, C, H["r_wi"] + 0.1, 0.0, fl + 0.22, n=12)
    col_box2(A, W(C, -H["door_hw"], -22.7, 0.0), W(C, H["door_hw"], -21.0, 0.6))
    col_box2(A, W(C, -H["door_hw"], -21.0, 0.0), W(C, H["door_hw"], -16.0, fl))
    col_ring(A, C, H["r_wi"], H["r_wo"] + 0.4, fl, H["wall_top"], K.arc_spans([(DOOR_A, dh)]), seg=19.0)
    col_box2(A, W(C, -H["door_hw"], -H["r_wo"] - 0.4, fl + H["door_h"]), W(C, H["door_hw"], -H["r_wi"] + 0.4,
                                                                               H["wall_top"]))
    for k in (1, 17):
        col_box(A, (2.2, 2.2, 13.0), pol(C, H["r_wo"] + 0.25, DOOR_A + 20.0 * k, fl + 6.5))
    for s in (-1, 1):     # folhas da porta abertas
        lc, yaw = leaf_pose(s, H["door_hw"] - 0.25, -18.6, 4.6, 55.0)
        col_box(A, (0.4, 4.6, H["door_h"] - 0.2), W(C, lc[0], lc[1], fl + H["door_h"] / 2), (0, 0, yaw))
    zf = fl + 0.22
    col_box(A, (10.4, 4.0, 3.5), W(C, 0, DESK_Y, zf + 1.75))
    for a in BOOKCASES:
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        col_box(A, (3.6, 1.5, 8.9), F.p(0, 0.75, 4.45), F.r())
    col_r = (H["up_ri"] + H["up_ro"]) / 2
    for k in range(8):
        col_box(A, (1.7, 1.7, 13.4), pol(C, col_r, 22.5 + 45.0 * k, zf + 6.7))
    for a in (190.0, 350.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        col_box(A, (4.4, 1.6, 1.7), F.p(0, 1.1, 0.85), F.r())
    light("L_Village_HallInterior", "POINT", W(C, 0, 0, 13.6), 5200, (1.0, 0.72, 0.45), 1.2)
    light("L_Village_HallDesk", "POINT", W(C, 0, 3.0, 11.0), 1400, (1.0, 0.76, 0.5), 0.8)
    mk("NPC_MainHall", W(C, 0, DESK_Y + 3.0, zf), (0, 0, math.pi), 2.0, "ARROWS", props={"floor": C[2] + zf})
    mk("PLAYER_INTERACT_MainHall", W(C, 0, DESK_Y - 4.0, zf), (0, 0, 0), 2.0, "SPHERE", props={"floor": C[2] + zf})


DESK_Y = 6.6


def hall_interior(mb, C):
    """interior do salao (no MESMO objeto da casca): assoalho, lambri, janelas, forro em anel, rotunda aberta ate o
    tambor de cima (pe-direito 14,4 no anel e 25 no centro), colunas, mesa do Kage, cadeira, estantes, tapete"""
    H = HALL
    rng = random.Random(4102)
    fl = H["fl"]
    zf = fl + 0.22            # topo do assoalho
    dh = math.degrees(math.asin(H["door_hw"] / H["r_wo"]))
    K.round_floor(mb, C, H["r_wi"] + 0.05, zf, rng, pw=1.5)
    # lambri escuro + faixa vermelha no alto + janelas por dentro + pilastras
    K.ring_wall(mb, C, H["r_wi"] - 0.22, H["r_wi"] + 0.02, zf, zf + 2.4, "Wood_Dark", 40, gaps=[(DOOR_A, dh + 1.8)])
    K.lathe(mb, C, [(H["r_wi"] - 0.3, 14.7), (H["r_wi"] + 0.02, 14.7), (H["r_wi"] + 0.02, 15.5),
                    (H["r_wi"] - 0.3, 15.5)], "Wood_Lacquer_Red", 40)
    for k in range(1, 17):
        K.drum_window(mb, C, H["r_wi"], DOOR_A + 10.0 + 20.0 * k, 3.3, 6.0, 10.6, out=-1, sill=False, jambs=False,
                      grid=False)
    for k in range(1, 18):
        tan_box(mb, C, H["r_wi"] - 0.25, DOOR_A + 20.0 * k, (1.2, 0.5, 12.4), zf + 6.2, "Wood_Lacquer_Red")
    # forro em anel (sob o 1o beiral) + vigas radiais + viga-anel sobre 8 colunas (carrega o tambor de cima)
    K.lathe(mb, C, [(H["up_ri"], H["ceil"]), (H["r_wi"] + 0.05, H["ceil"]), (H["r_wi"] + 0.05, H["ceil"] + 0.3),
                    (H["up_ri"], H["ceil"] + 0.3)], "Plaster_Cream", 48)
    for k in range(18):
        a = DOOR_A + 20.0 * k
        mb.beam(pol(C, H["up_ro"] + 0.4, a, H["ceil"] - 0.35), pol(C, H["r_wi"] - 0.1, a, H["ceil"] - 0.35), 0.6, 0.7,
                "Wood_Dark", 0.0)
    K.lathe(mb, C, [(H["up_ri"] - 0.4, 14.9), (H["up_ro"] + 0.5, 14.9), (H["up_ro"] + 0.5, H["ceil"]),
                    (H["up_ri"] - 0.4, H["ceil"])], "Wood_Dark", 32)
    col_r = (H["up_ri"] + H["up_ro"]) / 2
    for k in range(8):
        a = 22.5 + 45.0 * k
        p = pol(C, col_r, a)
        mb.cyl(0.8, 14.9 - zf, p + Vector((0, 0, (14.9 + zf) / 2)), (0, 0, 0), "Wood_Lacquer_Red", 10, bevel=0.0)
        mb.cyl(1.15, 0.7, p + Vector((0, 0, zf + 0.35)), (0, 0, 0), "Stone_Wall_Dark", 8, bevel=0.0)
        mb.box((2.0, 2.0, 0.6), p + Vector((0, 0, 14.6)), (0, 0, math.radians(a)), "Wood_Dark", 0.0)
        mb.cyl(0.9, 0.3, p + Vector((0, 0, zf + 11.5)), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
    # rotunda: face interna do tambor de cima (janelas redondas por dentro) + teto alto com vigas e florao
    for k in range(12):
        a = math.radians(DOOR_A + 15.0 + 30.0 * k)
        mb.cyl(1.35, 0.2, pol(C, H["up_ri"] - 0.08, DOOR_A + 15.0 + 30.0 * k, 22.1), (math.pi / 2, 0, a + math.pi / 2),
               "Window_Warm", 8, bevel=0.0)
    K.lathe(mb, C, [(0.5, H["ceil2"]), (H["up_ri"] + 0.05, H["ceil2"]), (H["up_ri"] + 0.05, H["ceil2"] + 0.3),
                    (0.5, H["ceil2"] + 0.3)], "Plaster_Cream", 40)
    for k in range(8):
        a = 22.5 + 45.0 * k
        mb.beam(pol(C, 1.2, a, H["ceil2"] - 0.35), pol(C, H["up_ri"] - 0.05, a, H["ceil2"] - 0.35), 0.55, 0.7,
                "Wood_Dark", 0.0)
    K.lathe(mb, C, [(H["up_ri"] - 0.3, 18.2), (H["up_ri"] + 0.02, 18.2), (H["up_ri"] + 0.02, 18.9),
                    (H["up_ri"] - 0.3, 18.9)], "Wood_Lacquer_Red", 32)
    mb.cyl(1.6, 0.6, W(C, 0, 0, H["ceil2"] - 0.3), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
    # grande lanterna de papel no centro da rotunda
    mb.rod(W(C, 0, 0, H["ceil2"] - 0.6), W(C, 0, 0, 20.4), 0.1, "Wood_Dark", 4)
    K.paper_lantern(mb, W(C, 0, 0, 20.4), r=2.6, h=3.8, paper="Lantern_Glow", cap="Wood_Lacquer_Red",
                    band="Cloth_Red", hang=0.2, n=12)
    # tapete redondo com a folha
    rc = W(C, 0, -3.5, zf)
    mb.cyl(7.2, 0.1, rc + Vector((0, 0, 0.06)), (0, 0, 0), "Cloth_Red", 32, bevel=0.0)
    PK.ring(mb, rc + Vector((0, 0, 0.1)), 6.7, (1, 0, 0), (0, 1, 0), 0.45, 0.08, "Metal_Gold", n=24)
    PK.ring(mb, rc + Vector((0, 0, 0.1)), 7.25, (1, 0, 0), (0, 1, 0), 0.25, 0.06, "Cloth_Canvas", n=24)
    K.leaf_symbol(mb, rc + Vector((0, 0, 0.17)), (1, 0, 0), (0, 1, 0), 4.6, "Emblem_Cream", th=0.08, w=0.2)
    # mesa do Kage: corpo de madeira escura, frente de laca com friso dourado, tampo claro
    dc = W(C, 0, DESK_Y, zf)
    mb.box((9.6, 3.4, 3.0), dc + Vector((0, 0, 1.5)), (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((10.4, 4.0, 0.35), dc + Vector((0, 0, 3.17)), (0, 0, 0), "Wood_Light", 0.06)
    mb.box((9.0, 0.2, 2.2), dc + Vector((0, -1.75, 1.6)), (0, 0, 0), "Wood_Lacquer_Red", 0.0)
    for zz in (0.55, 2.65):
        mb.box((9.2, 0.25, 0.2), dc + Vector((0, -1.82, zz)), (0, 0, 0), "Metal_Gold", 0.0)
    mb.cyl(0.75, 0.12, dc + Vector((0, -1.9, 1.6)), (math.pi / 2, 0, 0), "Metal_Gold", 10, bevel=0.0)
    top = dc + Vector((0, 0, 3.35))
    for x, y, h in ((-4.1, 0.6, 0.9), (-3.0, 0.9, 0.6), (-4.0, -0.7, 0.45), (3.3, 0.8, 0.75), (4.2, -0.2, 0.4)):
        mb.box((1.05, 0.8, h), top + Vector((x, y, h / 2)), (0, 0, rng.uniform(-0.15, 0.15)), "Emblem_Cream", 0.0)
    for i, (x, y) in enumerate(((-1.6, 1.1), (-1.1, 1.35), (-1.35, 1.6))):
        mb.cyl(0.2, 1.7, top + Vector((x + 3.6, y - 0.1, 0.2 + (0.35 if i == 2 else 0.0))), (0, math.pi / 2, 0.2),
               "Cloth_Canvas", 6, bevel=0.0)
    # pergaminho aberto + tinteiro + pincel
    mb.box((2.6, 1.3, 0.05), top + Vector((0.2, -0.4, 0.03)), (0, 0, 0.05), "Cloth_Canvas", 0.0)
    for s in (-1, 1):
        mb.cyl(0.14, 1.5, top + Vector((0.2 + s * 1.35, -0.4, 0.12)), (math.pi / 2, 0, 0.05), "Wood_Dark", 6,
               bevel=0.0)
    mb.box((0.9, 0.6, 0.2), top + Vector((1.9, 0.9, 0.1)), (0, 0, 0), "Stone_Wall_Dark", 0.0)
    mb.rod(top + Vector((2.6, 0.2, 0.1)), top + Vector((2.9, 1.3, 0.25)), 0.06, "Wood_Dark", 4)
    # cadeira alta atras do lugar do NPC
    ch = W(C, 0, DESK_Y + 5.6, zf)
    mb.box((2.8, 2.4, 0.5), ch + Vector((0, 0, 2.0)), (0, 0, 0), "Wood_Dark", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.35, 0.35, 2.0), ch + Vector((sx * 1.2, sy * 1.0, 1.0)), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((2.8, 0.45, 4.8), ch + Vector((0, 1.05, 4.6)), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((2.2, 0.2, 3.4), ch + Vector((0, 0.75, 4.4)), (0, 0, 0), "Cloth_Red", 0.0)
    mb.box((2.3, 2.0, 0.3), ch + Vector((0, 0, 2.4)), (0, 0, 0), "Cloth_Red", 0.0)
    # estantes no fundo (sobre os pilares, entre as janelas) e rolos pendurados nas laterais
    for a in BOOKCASES:
        K.bookcase(mb, tan_frame(C, H["r_wi"] - 0.3, a, zf), 3.6, 8.6, 1.5, rng, shelves=4)
    for a in (10.0, 170.0, 210.0, 330.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        mb.box((2.6, 0.12, 6.4), F.p(0, 0.62, 8.2), F.r(), "Cloth_Canvas", 0.0)
        mb.box((3.1, 0.3, 0.3), F.p(0, 0.66, 11.5), F.r(), "Wood_Dark", 0.0)
        mb.box((3.0, 0.3, 0.3), F.p(0, 0.66, 4.95), F.r(), "Wood_Dark", 0.0)
        tx = F.p(1, 0, 0) - F.p(0, 0, 0)
        if a in (10.0, 170.0):
            K.leaf_symbol(mb, F.p(0, 0.7, 8.8), tx, (0, 0, 1), 0.95, "Cloth_Red", th=0.06)
        else:
            for z in (6.5, 7.5, 8.5, 9.5):
                mb.box((1.4 if z != 8.5 else 1.8, 0.06, 0.18), F.p(rng.uniform(-0.3, 0.3), 0.7, z), F.r(),
                       "Wood_Dark", 0.0)
    # bancos baixos junto a parede (espera) a leste e oeste
    for a in (190.0, 350.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        mb.box((4.4, 1.6, 0.4), F.p(0, 1.1, 1.5), F.r(), "Wood_Plank", 0.0)
        for sx in (-1, 1):
            mb.box((0.4, 1.4, 1.3), F.p(sx * 1.8, 1.1, 0.65), F.r(), "Wood_Dark", 0.0)


# ================================================================== PREDIOS REDONDOS AZUIS
SHOP = dict(r_pl=13.6, r_wo=12.2, r_wi=11.0, fl=0.6, wall_top=15.1, door_hw=4.0, door_h=10.8,
            up_ro=8.2, up_ri=7.3, up_bot=14.2, up_top=21.2, ceil=15.0, ceil2=21.0,
            skirt=[(15.9, 13.6), (13.2, 14.7), (10.4, 16.0), (7.9, 17.4)])
ROOF_B = [(10.7, 20.6), (8.0, 21.9), (5.2, 23.4), (2.8, 24.6)]
TOWER = dict(r_pl=13.4, r_wo=12.0, r_wi=11.2, fl=0.6, wall_top=14.0, up_ro=8.2, up_ri=7.4, up_bot=13.4,
             up_top=19.4, skirt=[(15.5, 13.0), (12.8, 14.1), (10.2, 15.3), (7.9, 16.5)])


def round_blue_shell(mb, C, H, rng, door, windows="square", rib_seed=0.0):
    """casca comum dos predios redondos azuis: embasamento, tambor, pilares, janelas, beiral azul, tambor de cima"""
    fl = H["fl"]
    dh = math.degrees(math.asin(H["door_hw"] / H["r_wo"])) if door else 0.0
    gaps = [(DOOR_A, dh)] if door else []
    K.plinth(mb, C, H["r_pl"], fl, rng, n=36)
    K.ring_wall(mb, C, H["r_wi"], H["r_wo"], 0.4, H["wall_top"], "Plaster_Cream", 40, gaps=gaps)
    if door:
        K.lathe(mb, C, [(H["r_wi"], fl + H["door_h"]), (H["r_wo"], fl + H["door_h"]), (H["r_wo"], H["wall_top"]),
                        (H["r_wi"], H["wall_top"])], "Plaster_Cream", 4, DOOR_A - dh, DOOR_A + dh)
    K.ring_wall(mb, C, H["r_wo"] - 0.1, H["r_wo"] + 0.28, 0.7, 1.9, "Stone_Wall_Dark", 40,
                gaps=[(DOOR_A, dh + 2.0)] if door else [])
    K.lathe(mb, C, [(H["r_wo"] - 0.1, 11.9), (H["r_wo"] + 0.32, 11.9), (H["r_wo"] + 0.32, 12.7),
                    (H["r_wo"] - 0.1, 12.7)], "Wood_Lacquer_Red", 40)
    # pilares (12, de 30 em 30; com porta, os 2 vizinhos do vao ficam como batentes)
    off = 0.0 if door else 15.0
    for k in range(12):
        a = DOOR_A + off + 30.0 * k
        if door and k == 0:
            continue
        p = pol(C, H["r_wo"] + 0.2, a)
        mb.cyl(0.7, 11.4, p + Vector((0, 0, fl + 5.7)), (0, 0, 0), "Wood_Lacquer_Red", 8, bevel=0.0)
        mb.box((1.9, 1.9, 0.6), p + Vector((0, 0, fl + 0.3)), (0, 0, math.radians(a)), "Stone_Wall_Light", 0.0)
        mb.box((1.8, 1.8, 0.45), p + Vector((0, 0, 11.7)), (0, 0, math.radians(a)), "Wood_Dark", 0.0)
    # janelas entre os pilares
    for k in range(12):
        a = DOOR_A + off + 15.0 + 30.0 * k
        if door and k in (0, 11):
            continue
        if windows == "tall":
            if k % 2 == 1:
                K.drum_window(mb, C, H["r_wo"], a, 1.5, 4.8, 10.8, grid=False)
        else:
            K.drum_window(mb, C, H["r_wo"], a, 2.8, 5.0, 8.6, jambs=False)
    sk = H["skirt"]
    K.cone_roof(mb, C, sk, 0.7, "Roof_Blue", n=40, ribs=20, rib_m="Roof_Blue_B", rib_w=0.55, rib_h=0.26,
                fascia=(sk[0][0] - 0.3, sk[0][0] + 0.25, sk[0][1] - 0.85, sk[0][1] + 0.2), fascia_m="Roof_Blue_B",
                rafters=16, rafter_r=(H["r_wo"] + 0.4, sk[0][0] - 0.4), a_off=rib_seed)
    K.lathe(mb, C, [(H["up_ri"], H["up_bot"]), (H["up_ro"], H["up_bot"]), (H["up_ro"], H["up_top"]),
                    (H["up_ri"], H["up_top"])], "Plaster_Cream", 32)
    K.lathe(mb, C, [(H["up_ro"] - 0.1, H["up_top"] - 1.5), (H["up_ro"] + 0.28, H["up_top"] - 1.5),
                    (H["up_ro"] + 0.28, H["up_top"] - 0.8), (H["up_ro"] - 0.1, H["up_top"] - 0.8)],
                "Wood_Lacquer_Red", 32)
    for k in range(8):
        a = DOOR_A + 22.5 + 45.0 * k
        zc = (H["up_bot"] + H["up_top"]) / 2 + 0.6
        tan_box(mb, C, H["up_ro"] + 0.05, a, (1.4, 0.25, 1.4), zc, "Window_Warm")
        tan_box(mb, C, H["up_ro"] + 0.12, a, (1.9, 0.3, 0.3), zc + 0.85, "Wood_Dark")
        tan_box(mb, C, H["up_ro"] + 0.16, a, (2.0, 0.5, 0.3), zc - 0.85, "Wood_Dark")


# ------------------------------------------------------------------ LOJA DE ARMAS NINJA (oeste, entravel)
def weapon_shop():
    C = (SX, SY, T2)
    H = SHOP
    rng = random.Random(4201)
    mb = VMB("VIL_WeaponShop", COLL, rng, detail="near", vcap=1)
    fl = H["fl"]
    round_blue_shell(mb, C, H, rng, door=True)
    K.cone_roof(mb, C, ROOF_B, 0.6, "Roof_Blue", n=32, ribs=14, rib_m="Roof_Blue_B", rib_w=0.45, rib_h=0.24,
                fascia=(10.5, 11.0, 19.85, 20.8), fascia_m="Roof_Blue_B", rafters=0, rafter_r=(8.6, 10.4))
    K.lathe(mb, C, [(0.4, 24.3), (3.1, 24.3), (3.1, 24.9), (0.4, 24.9)], "Plaster_Cream", 16)
    K.lathe(mb, C, [(2.3, 24.9), (0.7, 26.2), (0.4, 26.2), (0.4, 24.9)], "Roof_Blue", 12)
    mb.cyl(0.4, 1.6, W(C, 0, 0, 26.9), (0, 0, 0), "Metal_Gold", 8, bevel=0.0)
    mb.ico(0.55, W(C, 0, 0, 27.9), "Metal_Gold", 1)
    # portal: batentes e verga de madeira escura + degrau de pedra + noren azul curto (acima de 9)
    dh = math.degrees(math.asin(H["door_hw"] / H["r_wo"]))
    for s in (-1, 1):
        mb.box((0.7, 1.6, H["door_h"] + 0.2), W(C, s * (H["door_hw"] + 0.15), -11.65, fl + H["door_h"] / 2),
               (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((2 * H["door_hw"] + 1.4, 1.7, 0.8), W(C, 0, -11.7, fl + H["door_h"] + 0.3), (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((2 * H["door_hw"] + 0.6, 1.5, 0.3), W(C, 0, -14.1, 0.15), (0, 0, 0), "Stone_Wall_Light", 0.08)
    for k in range(3):
        mb.box((2.4, 0.1, 2.3), W(C, -2.6 + 2.6 * k, -12.62, fl + H["door_h"] - 1.2), (0, 0, 0), "Cloth_Royal_Blue",
               0.0)
    # folhas da porta abertas para dentro (135 graus)
    for s in (-1, 1):
        lc, yaw = leaf_pose(s, H["door_hw"] - 0.3, -10.4, 3.8)
        mb.box((0.28, 3.8, H["door_h"] - 0.3), W(C, lc[0], lc[1], fl + H["door_h"] / 2 - 0.1), (0, 0, yaw),
               "Wood_Plank", 0.05)
    # placa pendurada num braco (icone de kunai), no pilar a oeste da porta: a face olha para ESE (praca/escada)
    a = DOOR_A - 30.0
    rad = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0))
    tng = Vector((-rad.y, rad.x, 0.0))
    mb.beam(pol(C, H["r_wo"] + 0.9, a, 10.6), pol(C, H["r_wo"] + 5.4, a, 10.6), 0.45, 0.55, "Wood_Dark", 0.0)
    mb.beam(pol(C, H["r_wo"] + 0.9, a, 8.2), pol(C, H["r_wo"] + 3.0, a, 10.4), 0.32, 0.32, "Wood_Dark", 0.0)
    bc = pol(C, H["r_wo"] + 3.4, a, 8.4)
    for s in (-1, 1):
        mb.rod(pol(C, H["r_wo"] + 3.4 + s * 1.5, a, 10.4), pol(C, H["r_wo"] + 3.4 + s * 1.5, a, 9.85), 0.07,
               "Metal_Dark", 4)
    brot = (0, 0, math.atan2(rad.y, rad.x))
    mb.box((3.8, 0.34, 2.8), bc, brot, "Wood_Plank", 0.08)
    for dz in (1.45, -1.45):
        mb.box((4.1, 0.4, 0.28), bc + Vector((0, 0, dz)), brot, "Wood_Dark", 0.0)
    for s in (-1, 1):
        d = (rad * 0.62 + Vector((0, 0, 0.78))).normalized()
        K.kunai(mb, bc + tng * s * 0.21 - rad * 0.3 - Vector((0, 0, 0.15)), d, tng * s, s=1.25, ring_n=8)
    shop_interior(mb, C, H)
    mb.finish()
    # colisao
    A = "VillageShop"
    col_disk(A, C, H["r_pl"] - 0.25, 0.0, fl, n=8)
    col_disk(A, C, H["r_wi"], 0.0, fl + 0.22, n=10)
    col_box2(A, W(C, -H["door_hw"] - 0.3, -H["r_pl"], 0.0), W(C, H["door_hw"] + 0.3, -H["r_wi"], fl))
    col_box2(A, W(C, -H["door_hw"] - 0.3, -14.85, 0.0), W(C, H["door_hw"] + 0.3, -H["r_pl"], 0.3))
    col_ring(A, C, H["r_wi"], H["r_wo"] + 0.3, fl, H["wall_top"], K.arc_spans([(DOOR_A, dh)]), seg=30.0)
    col_box2(A, W(C, -H["door_hw"], -H["r_wo"] - 0.3, fl + H["door_h"]), W(C, H["door_hw"], -H["r_wi"] + 0.4,
                                                                             H["wall_top"]))
    for s in (-1, 1):
        col_box(A, (1.8, 1.8, 11.4), pol(C, H["r_wo"] + 0.2, DOOR_A + s * 30.0, fl + 5.7))
        lc, yaw = leaf_pose(s, H["door_hw"] - 0.3, -10.4, 3.8)
        col_box(A, (0.4, 3.8, H["door_h"] - 0.3), W(C, lc[0], lc[1], fl + H["door_h"] / 2 - 0.1), (0, 0, yaw))
    zf = fl + 0.22
    col_box(A, (9.6, 2.0, 3.5), W(C, 0, SHOP_CY, zf + 1.75))
    for a, w in ((90.0, 7.4), (180.0, 5.2), (0.0, 5.2)):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        col_box(A, (w, 0.8, 7.0), F.p(0, 0.4, 3.5), F.r())
    for a in (142.0, 38.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        col_box(A, (4.2, 1.8, 5.0), F.p(0, 0.9, 2.5), F.r())
    for s in (-1, 1):
        col_box(A, (2.2, 2.2, 2.6), W(C, s * 6.9, -5.2, zf + 1.3))
    light("L_Village_ShopInterior", "POINT", W(C, 0, 0, 11.0), 2600, (1.0, 0.74, 0.48), 0.8)
    mk("NPC_WeaponShop", W(C, 0, SHOP_CY + 2.6, zf), (0, 0, math.pi), 2.0, "ARROWS", props={"floor": C[2] + zf})
    mk("PLAYER_INTERACT_WeaponShop", W(C, 0, SHOP_CY - 3.6, zf), (0, 0, 0), 2.0, "SPHERE",
       props={"floor": C[2] + zf})


SHOP_CY = 3.0


def shop_interior(mb, C, H):
    rng = random.Random(4202)
    fl = H["fl"]
    zf = fl + 0.22
    dh = math.degrees(math.asin(H["door_hw"] / H["r_wo"]))
    K.round_floor(mb, C, H["r_wi"] + 0.05, zf, rng, pw=1.4)
    K.ring_wall(mb, C, H["r_wi"] - 0.22, H["r_wi"] + 0.02, zf, zf + 2.2, "Wood_Dark", 40, gaps=[(DOOR_A, dh + 2.0)])
    for a in (225.0, 315.0):
        K.drum_window(mb, C, H["r_wi"], a, 2.8, 5.0, 8.6, out=-1, sill=False, jambs=False)
    for k in range(1, 12):
        tan_box(mb, C, H["r_wi"] - 0.22, DOOR_A + 30.0 * k, (1.0, 0.45, 13.6), zf + 6.8, "Wood_Lacquer_Red")
    # forro em anel + vigas + tambor de cima aberto (lanternim) com teto alto
    K.lathe(mb, C, [(H["up_ri"], H["ceil"]), (H["r_wi"] + 0.05, H["ceil"]), (H["r_wi"] + 0.05, H["ceil"] + 0.3),
                    (H["up_ri"], H["ceil"] + 0.3)], "Plaster_Cream", 32)
    K.lathe(mb, C, [(H["up_ri"] - 0.3, 14.3), (H["up_ro"] + 0.5, 14.3), (H["up_ro"] + 0.5, H["ceil"]),
                    (H["up_ri"] - 0.3, H["ceil"])], "Wood_Dark", 32)
    for k in range(12):
        a = DOOR_A + 30.0 * k
        mb.beam(pol(C, H["up_ro"] + 0.4, a, H["ceil"] - 0.3), pol(C, H["r_wi"] - 0.1, a, H["ceil"] - 0.3), 0.5, 0.6,
                "Wood_Dark", 0.0)
    K.lathe(mb, C, [(0.5, H["ceil2"]), (H["up_ri"] + 0.05, H["ceil2"]), (H["up_ri"] + 0.05, H["ceil2"] + 0.3),
                    (0.5, H["ceil2"] + 0.3)], "Plaster_Cream", 24)
    mb.cyl(0.55, 0.3, W(C, 0, 0, H["ceil2"] + 0.15), (0, 0, 0), "Plaster_Cream", 8, bevel=0.0)
    for k in range(6):
        a = 30.0 + 60.0 * k
        mb.beam(pol(C, 0.9, a, H["ceil2"] - 0.3), pol(C, H["up_ri"] - 0.05, a, H["ceil2"] - 0.3), 0.45, 0.6,
                "Wood_Dark", 0.0)
    for k in range(8):
        tan_box(mb, C, H["up_ri"] - 0.05, DOOR_A + 22.5 + 45.0 * k, (1.4, 0.25, 1.4), 18.4, "Window_Warm")
    mb.rod(W(C, 0, 0, H["ceil2"] - 0.3), W(C, 0, 0, 15.2), 0.08, "Wood_Dark", 4)
    K.paper_lantern(mb, W(C, 0, 0, 15.2), r=1.6, h=2.4, paper="Lantern_Glow", cap="Wood_Dark", band="Cloth_Royal_Blue",
                    hang=0.2, n=10)
    # balcao (frente de laca vermelha, tampo claro) - NPC atras, jogador na frente
    cc = W(C, 0, SHOP_CY, zf)
    mb.box((9.4, 1.8, 3.2), cc + Vector((0, 0, 1.6)), (0, 0, 0), "Wood_Dark", 0.06)
    mb.box((10.0, 2.3, 0.3), cc + Vector((0, -0.15, 3.35)), (0, 0, 0), "Wood_Light", 0.05)
    for k in range(4):
        mb.box((1.9, 0.14, 2.3), cc + Vector((-3.45 + 2.3 * k, -0.95, 1.65)), (0, 0, 0), "Wood_Lacquer_Red", 0.0)
    ct = cc + Vector((0, 0, 3.5))
    mb.box((2.6, 1.2, 0.14), ct + Vector((-2.6, -0.2, 0.07)), (0, 0, 0), "Wood_Plank", 0.0)
    for k in range(4):
        K.kunai(mb, ct + Vector((-3.3 + 0.45 * k, 0.05, 0.22)), (0.05, -1, 0), (0, 0, 1), s=0.8)
    K.shuriken(mb, ct + Vector((1.6, -0.3, 0.12)), (0, 0, 1), up=(1, 0, 0), R=0.75)
    K.shuriken(mb, ct + Vector((2.8, 0.1, 0.12)), (0, 0, 1), up=(1, 0, 0), R=0.6, spin=20.0)
    # parede do fundo (norte): painel com 3 katanas horizontais + faixa de shuriken
    F = tan_frame(C, H["r_wi"] - 0.3, 90.0, zf)
    tx, ty = F.p(1, 0, 0) - F.p(0, 0, 0), F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.box((7.4, 0.3, 5.6), F.p(0, 0.15, 6.4), F.r(), "Wood_Plank", 0.06)
    for z in (9.35, 3.45):
        mb.box((7.8, 0.4, 0.35), F.p(0, 0.2, z), F.r(), "Wood_Dark", 0.0)
    for i, z in enumerate((4.6, 6.2, 7.8)):
        for s in (-1, 1):
            mb.box((0.3, 0.7, 0.3), F.p(s * 2.4, 0.55, z - 0.25), F.r(), "Wood_Dark", 0.0)
        K.katana(mb, F.p(-3.0, 0.75, z), tx, ty, L=6.0, sheath=("Wood_Lacquer_Red" if i == 1 else None),
                 grip=("Cloth_Royal_Blue" if i == 0 else "Wood_Dark"))
    for k in range(5):
        K.shuriken(mb, F.p(-2.8 + 1.4 * k, 0.4, 8.7), ty, up=(0, 0, 1), R=0.5, spin=15.0 * k)
    # oeste: suporte de kunais (2 fileiras penduradas, ponta para baixo)
    F = tan_frame(C, H["r_wi"] - 0.3, 180.0, zf)
    ty = F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.box((5.2, 0.3, 4.6), F.p(0, 0.15, 6.0), F.r(), "Wood_Plank", 0.06)
    for z in (7.3, 4.8):
        mb.box((5.0, 0.5, 0.3), F.p(0, 0.45, z + 1.05), F.r(), "Wood_Dark", 0.0)
        for k in range(5):
            K.kunai(mb, F.p(-1.9 + 0.95 * k, 0.5, z), (0, 0, -1), ty, s=0.9)
    # leste: painel de shuriken (4 pequenos + 1 grande)
    F = tan_frame(C, H["r_wi"] - 0.3, 0.0, zf)
    ty = F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.box((5.2, 0.3, 4.6), F.p(0, 0.15, 6.0), F.r(), "Wood_Plank", 0.06)
    mb.box((5.6, 0.4, 0.3), F.p(0, 0.2, 8.4), F.r(), "Wood_Dark", 0.0)
    for i in (0, 2):
        for j in range(2):
            K.shuriken(mb, F.p(-1.7 + 1.7 * i, 0.4, 4.7 + 2.6 * j), ty, up=(0, 0, 1), R=0.7, spin=10.0 * (i + j))
    K.shuriken(mb, F.p(0, 0.45, 6.0), ty, up=(0, 0, 1), R=1.25, spin=45.0)
    # noroeste: cavalete de katanas no chao; nordeste: prateleira com caixas de shuriken
    F = tan_frame(C, H["r_wi"] - 0.3, 142.0, zf)
    tx = F.p(1, 0, 0) - F.p(0, 0, 0)
    for s in (-1, 1):
        mb.box((0.4, 1.2, 4.2), F.p(s * 1.9, 1.0, 2.1), F.r(), "Wood_Dark", 0.05)
        mb.box((0.5, 1.6, 0.3), F.p(s * 1.9, 1.0, 0.15), F.r(), "Wood_Dark", 0.0)
    for i, z in enumerate((1.6, 2.7, 3.8)):
        K.katana(mb, F.p(-2.8, 1.0, z), tx, (0, 0, 1), L=5.6, sheath=("Wood_Lacquer_Red" if i == 0 else None))
    F = tan_frame(C, H["r_wi"] - 0.3, 38.0, zf)
    tx = F.p(1, 0, 0) - F.p(0, 0, 0)
    for z in (0.2, 2.4, 4.6):
        mb.box((3.8, 1.3, 0.25), F.p(0, 0.75, z), F.r(), "Wood_Dark", 0.0)
    for s in (-1, 1):
        mb.box((0.3, 1.3, 5.0), F.p(s * 1.9, 0.75, 2.5), F.r(), "Wood_Dark", 0.0)
    for z in (0.33, 2.53):
        for k in range(3):
            mb.box((0.95, 0.9, 0.7), F.p(-1.2 + 1.2 * k, 0.8, z + 0.35), F.r(0, 0, rng.uniform(-0.2, 0.2)),
                   "Wood_Plank", 0.0)
            K.shuriken(mb, F.p(-1.2 + 1.2 * k, 0.8, z + 0.8), (0, 0, 1), up=tuple(tx), R=0.35)
    # barris de kunai junto a porta (lado de dentro)
    for s in (-1, 1):
        bc = W(C, s * 6.9, -5.2, zf)
        FP.barrel(mb, (bc.x, bc.y, bc.z), r=1.05, h=2.5)
        brng = random.Random(4210 + s)
        for k in range(5):
            aa = brng.uniform(0, math.tau)
            rr = brng.uniform(0.0, 0.6)
            d = Vector((math.cos(aa) * 0.3, math.sin(aa) * 0.3, 1.0)).normalized()
            p = bc + Vector((math.cos(aa) * rr, math.sin(aa) * rr, 2.3))
            K.kunai(mb, p, d, Vector((-math.sin(aa), math.cos(aa), 0)), s=0.85, ring=False)


# ------------------------------------------------------------------ TORRE D'AGUA (leste, sem porta nenhuma)
def water_tower():
    C = (EX, EY, T2)
    H = TOWER
    rng = random.Random(4301)
    mb = VMB("VIL_WaterTower", COLL, rng, detail="near", vcap=1)
    round_blue_shell(mb, C, H, rng, door=False, windows="tall", rib_seed=4.0)
    K.lathe(mb, C, [(0.5, H["up_top"] - 0.3), (H["up_ro"], H["up_top"] - 0.3), (H["up_ro"], H["up_top"]),
                    (0.5, H["up_top"])], "Wood_Dark", 24)
    # varanda circular (sem acesso): deck em anel sobre maos-francesas + guarda-corpo
    zd = H["up_top"]
    K.lathe(mb, C, [(H["up_ro"] - 0.2, zd), (11.2, zd), (11.2, zd + 0.45), (H["up_ro"] - 0.2, zd + 0.45)],
            "Wood_Plank", 40)
    for k in range(12):
        a = 15.0 + 30.0 * k
        mb.beam(pol(C, H["up_ro"] + 0.1, a, zd - 2.8), pol(C, 10.6, a, zd - 0.05), 0.35, 0.45, "Wood_Dark", 0.0)
    for k in range(16):
        a = 360.0 * k / 16
        mb.box((0.34, 0.34, 2.5), pol(C, 10.85, a, zd + 1.65), (0, 0, math.radians(a)), "Wood_Dark", 0.0)
    for z, w in ((zd + 2.9, 0.34), (zd + 1.7, 0.22)):
        PK.ring(mb, W(C, 0, 0, z), 10.85, (1, 0, 0), (0, 1, 0), w, w, "Wood_Dark", n=20)
    # caixa d'agua de madeira: aduelas + aros de ferro + tampa azul conica + pinaculo
    zt = zd + 0.45
    K.lathe(mb, C, [(0.5, zt), (6.0, zt), (6.0, zt + 7.6), (0.5, zt + 7.6)], "Wood_Dark", 20)
    nst = 22
    for k in range(nst):
        a = 360.0 * (k + 0.5) / nst
        hh = 7.8 + rng.uniform(-0.12, 0.12)
        tan_box(mb, C, 6.3, a, (2 * math.pi * 6.55 / nst - 0.1, 0.5, hh), zt + hh / 2, "Wood_Plank")
    for z in (zt + 0.9, zt + 3.9, zt + 6.9):
        K.lathe(mb, C, [(6.5, z - 0.25), (6.78, z - 0.25), (6.78, z + 0.25), (6.5, z + 0.25)], "Metal_Dark", 24)
    zl = zt + 7.7
    K.lathe(mb, C, [(7.6, zl), (4.4, zl + 1.8), (1.2, zl + 3.2), (0.6, zl + 3.2), (0.6, zl + 2.8), (4.2, zl + 1.3),
                    (7.6, zl - 0.45)], "Roof_Blue", 24)
    for k in range(12):
        a = 360.0 * (k + 0.5) / 12
        pts = [pol(C, 7.5, a, zl + 0.15), pol(C, 4.4, a, zl + 1.95), pol(C, 1.3, a, zl + 3.35)]
        for p0, p1 in zip(pts, pts[1:]):
            mb.beam(p0, p1, 0.36, 0.22, "Roof_Blue_B", 0.0)
    K.lathe(mb, C, [(7.4, zl - 0.55), (7.9, zl - 0.55), (7.9, zl + 0.2), (7.4, zl + 0.2)], "Roof_Blue_B", 24)
    mb.cyl(0.75, 1.8, W(C, 0, 0, zl + 3.9), (0, 0, 0), "Metal_Gold", 8, r2=0.45, bevel=0.0)
    mb.ico(0.6, W(C, 0, 0, zl + 5.1), "Metal_Gold", 1)
    # icone da folha pintado na frente da caixa (sul)
    K.emblem_disk(mb, pol(C, 6.95, DOOR_A, zt + 3.9), (0, -1, 0), 2.25, face="Emblem_Cream", rim="Metal_Gold",
                  back="Wood_Lacquer_Red", sym="Wood_Lacquer_Red", n=20, depth=0.5)
    # cano de descida (caixa -> reservatorio)
    a = DOOR_A + 55.0
    p1 = pol(C, 9.2, a, zt + 1.2)
    mb.rod(pol(C, 6.9, a, zt + 1.2), p1, 0.38, "Metal_Dark", 8)
    mb.rod(p1 + Vector((0, 0, 0.3)), pol(C, 9.2, a, 15.2), 0.38, "Metal_Dark", 8)
    mb.cyl(0.55, 0.5, p1, (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.finish()
    A = "VillageTower"
    col_disk(A, C, H["r_pl"] - 0.25, 0.0, H["fl"], n=12)
    col_disk(A, C, H["r_wo"] + 0.2, H["fl"], H["wall_top"], n=8)


# ================================================================== BARRACA DE RAMEN (T1, frente para o sul)
def ramen():
    F = Frame(RX, RY, T1, math.radians(RYAW))
    rng = random.Random(4401)
    mb = VMB("VIL_Ramen", COLL, rng, detail="near", vcap=1)
    hw, hd = RW / 2, RD / 2           # 9 x 6
    zf = 0.55                          # topo do assoalho
    zt = 10.4                          # topo das paredes / apoio do telhado
    red = "Cloth_VilLantern"
    # base de pedra + assoalho de tabuas
    mb.box((RW + 0.8, RD + 0.8, 1.0), F.p(0, 0, -0.15), F.r(), "Stone_Wall_Light", 0.12)
    mb.box((RW + 1.0, 0.3, 0.3), F.p(0, -hd - 0.35, 0.2), F.r(), "Stone_Wall_Dark", 0.0)
    FP.plank_floor(mb, F, RW - 0.4, RD - 0.4, zf - 0.2, rng, pw=1.3, h=0.22)
    # pilares
    for x, y in ((-hw, -hd), (hw, -hd), (-4.5, -hd), (4.5, -hd), (-hw, -2.0), (hw, -2.0), (-hw, hd), (hw, hd),
                 (0.0, hd)):
        mb.box((0.8, 0.8, zt - zf), F.p(x, y, (zt + zf) / 2), F.r(), "Wood_Dark", 0.08)
        mb.box((1.1, 1.1, 0.4), F.p(x, y, zf + 0.2), F.r(), "Stone_Wall_Dark", 0.0)
    # paredes laterais (y -2..6) e do fundo: rodape de tabua + reboco + travessas; janela na cozinha
    for s in (-1, 1):
        x = s * (hw - 0.05)
        mb.box((0.45, 8.0, 2.2), F.p(x, 2.0, zf + 1.1), F.r(), "Wood_Plank", 0.0)
        mb.box((0.35, 8.0, zt - zf - 2.2), F.p(x, 2.0, zf + 2.2 + (zt - zf - 2.2) / 2), F.r(), "Plaster_Cream", 0.0)
        for z in (zf + 2.25, 7.4):
            mb.box((0.55, 8.0, 0.35), F.p(x, 2.0, z), F.r(), "Wood_Dark", 0.0)
        mb.box((0.5, 2.8, 2.0), F.p(x, 2.6, 5.4), F.r(), "Window_Warm", 0.0)
        for yy in (1.2, 2.6, 4.0):
            mb.box((0.62, 0.22, 2.3), F.p(x, yy, 5.4), F.r(), "Wood_Dark", 0.0)
    mb.box((RW, 0.45, 2.2), F.p(0, hd - 0.05, zf + 1.1), F.r(), "Wood_Plank", 0.0)
    mb.box((RW, 0.35, zt - zf - 2.2), F.p(0, hd - 0.05, zf + 2.2 + (zt - zf - 2.2) / 2), F.r(), "Plaster_Cream", 0.0)
    for z in (zf + 2.25, 7.4):
        mb.box((RW, 0.55, 0.35), F.p(0, hd - 0.05, z), F.r(), "Wood_Dark", 0.0)
    # verga da frente, frechal lateral e tirantes (onde penduram as lanternas)
    mb.box((RW + 1.2, 0.9, 0.9), F.p(0, -hd, zt - 0.45), F.r(), "Wood_Dark", 0.08)
    for s in (-1, 1):
        mb.box((0.9, RD + 0.9, 0.8), F.p(s * hw, 0, zt - 0.4), F.r(), "Wood_Dark", 0.06)
    for y in (-2.0, 2.2):
        mb.box((RW, 0.6, 0.6), F.p(0, y, zt - 0.5), F.r(), "Wood_Dark", 0.0)
    # telhado verde de 4 aguas (kit de arquitetura do lobby), no mesmo objeto
    import fm_arch_kit as AK
    AK.hip_roof(mb, F, 0.0, 0.0, hw, hd, zt, 0.62, random.Random(4403), over=2.3, m="Roof_Green", m2=None, alt=0.0,
                patches=False, ridge_m="Wood_Dark", bevel=0.0, course=1.8, tile=(2.4, 3.4))
    # noren (cortinas) na verga: 6 panos com faixa vermelha no alto; barra a 7,0 (passa por baixo)
    for k in range(6):
        x = -7.55 + 3.02 * k
        mb.box((2.75, 0.1, 2.5), F.p(x, -hd - 0.55, 8.25), F.r(0.04 * (k % 2 * 2 - 1), 0, 0), "Cloth_VilNoren", 0.0)
        mb.box((2.75, 0.14, 0.4), F.p(x, -hd - 0.58, 9.3), F.r(), red, 0.0)
        if k in (1, 4):
            bowl_i = [(math.cos(math.radians(a)) * 0.75, math.sin(math.radians(a)) * 0.55) for a in range(180, 361, 30)]
            PK.plate(mb, bowl_i, F.p(x, -hd - 0.63, 7.9), (1, 0, 0), (0, 0, 1), 0.05, red)
    mb.box((RW + 0.6, 0.22, 0.22), F.p(0, -hd - 0.52, 9.55), F.r(), "Wood_Light", 0.0)
    # lanternas de papel vermelhas: 2 nos cantos da frente (sob o beiral) + 3 sobre o balcao
    for s in (-1, 1):
        K.paper_lantern(mb, F.p(s * (hw + 0.6), -hd - 1.4, 9.35), r=0.95, h=1.9, paper=red, cap="Wood_Dark",
                        band="Lantern_Glow", hang=0.45)
    for x in (-5.0, 0.0, 5.0):
        K.paper_lantern(mb, F.p(x, -2.0, zt - 0.8), r=0.75, h=1.5, paper=red, cap="Wood_Dark", band="Lantern_Glow",
                        hang=0.6)
    # placa no telhado da frente: tigela de ramen com hashi e vapor (sem texto)
    sc = F.p(0, -hd + 1.2, 12.6)
    tilt = -math.radians(18.0)
    for s in (-1, 1):
        mb.box((0.35, 0.35, 2.6), F.p(s * 2.6, -hd + 1.6, 11.3), F.r(), "Wood_Dark", 0.0)
    mb.box((7.2, 0.35, 2.6), sc, F.r(tilt, 0, 0), "Wood_Lacquer_Red", 0.08)
    mb.box((7.6, 0.3, 0.3), sc + Vector((0, 0.35, 1.35)), F.r(tilt, 0, 0), "Wood_Dark", 0.0)
    nrm = Vector((0.0, -math.cos(-tilt), math.sin(-tilt)))
    u = Vector((1.0, 0.0, 0.0))
    v = nrm.cross(u)
    bo = sc + nrm * 0.2 - v * 0.25
    bowl = [(math.cos(math.radians(a)) * 1.25, math.sin(math.radians(a)) * 0.95) for a in range(180, 361, 20)]
    PK.plate(mb, bowl, bo + nrm * 0.02, u, v, 0.14, "Emblem_Cream")
    PK.plate(mb, [(-1.25, -0.02), (1.25, -0.02), (1.1, -0.3), (-1.1, -0.3)], bo + nrm * 0.1, u, v, 0.12, red)
    for s in (0, 1):
        dd = (u * 0.35 + v).normalized()
        o2 = bo + u * (0.25 + 0.35 * s) + v * 0.05 + nrm * 0.1
        PK.plate(mb, [(0.0, -0.07), (1.5, -0.05), (1.5, 0.05), (0.0, 0.07)], o2, dd, nrm.cross(dd), 0.08, "Wood_Light")
    for k in range(3):
        x0 = -0.7 + 0.7 * k
        pts = [(x0 + 0.12 * math.sin(t * 3.0), 0.3 + t * 0.9) for t in (0.0, 0.33, 0.66, 1.0)]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            mb.beam(bo + u * xa + v * ya + nrm * 0.1, bo + u * xb + v * yb + nrm * 0.1, 0.1, 0.1, "Emblem_Cream", 0.0)
    # balcao do cliente (fundo livre de 6+ na frente) + banquinhos
    cy0, cy1 = 0.6, 2.0
    mb.box((15.6, cy1 - cy0, 3.1), F.p(0, (cy0 + cy1) / 2, zf + 1.55), F.r(), "Wood_Dark", 0.06)
    for k in range(8):
        mb.box((1.7, 0.12, 2.5), F.p(-6.85 + 1.96 * k, cy0 - 0.05, zf + 1.4), F.r(), "Wood_Plank", 0.0)
    mb.box((16.2, 1.9, 0.32), F.p(0, (cy0 + cy1) / 2 - 0.25, zf + 3.26), F.r(), "Wood_Light", 0.05)
    for k in range(6):
        x = -6.25 + 2.5 * k
        mb.cyl(0.26, 1.9, F.p(x, -1.1, zf + 0.95), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
        mb.cyl(0.72, 0.34, F.p(x, -1.1, zf + 2.05), (0, 0, 0), "Wood_Lacquer_Red", 10, bevel=0.0)
        mb.cyl(0.55, 0.12, F.p(x, -1.1, zf + 0.1), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
    ztop = zf + 3.42
    for x in (-5.0, 0.2, 4.9):
        b = F.p(x, 0.8, ztop)
        K.lathe(mb, b, [(0.25, 0.0), (0.42, 0.0), (0.66, 0.5), (0.58, 0.5), (0.25, 0.1)], "Emblem_Cream", 10)
        K.lathe(mb, b, [(0.55, 0.3), (0.63, 0.3), (0.66, 0.42), (0.58, 0.42)], red, 10)
        mb.cyl(0.55, 0.06, b + Vector((0, 0, 0.42)), (0, 0, 0), "Wood_Light", 10, bevel=0.0)
        for s in (-1, 1):
            mb.rod(b + Vector((0.15 * s, -0.3, 0.55)), b + Vector((0.3 + 0.15 * s, 0.6, 1.3)), 0.07, "Wood_Light", 4)
    mb.cyl(0.3, 0.8, F.p(-2.6, 1.2, ztop + 0.4), (0, 0, 0), "Wood_Lacquer_Red", 8, bevel=0.0)
    # cozinha: fogao de pedra com brilho, 2 panelas, bancada com tigelas, prateleiras, coifa e chamine
    by0, by1 = 4.2, 5.6
    mb.box((6.2, by1 - by0, 2.9), F.p(-5.1, (by0 + by1) / 2, zf + 1.45), F.r(), "Stone_Wall_Dark", 0.1)
    for x in (-6.4, -3.8):
        mb.box((1.3, 0.2, 0.8), F.p(x, by0 - 0.02, zf + 1.1), F.r(), "Forge_Glow_Soft", 0.0)
        mb.cyl(1.05, 1.7, F.p(x, (by0 + by1) / 2, zf + 2.9 + 0.85), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
        mb.cyl(1.12, 0.2, F.p(x, (by0 + by1) / 2, zf + 2.9 + 1.75), (0, 0, 0), "Wood_Dark", 10, bevel=0.0)
        mb.cyl(0.2, 0.3, F.p(x, (by0 + by1) / 2, zf + 2.9 + 1.98), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
    mb.box((10.2, by1 - by0, 2.9), F.p(3.2, (by0 + by1) / 2, zf + 1.45), F.r(), "Wood_Dark", 0.06)
    mb.box((10.4, by1 - by0 + 0.2, 0.25), F.p(3.2, (by0 + by1) / 2, zf + 3.0), F.r(), "Wood_Light", 0.0)
    for x in (0.2, 1.6, 3.0):
        for k in range(3):
            mb.cyl(0.55, 0.3, F.p(x, 4.9, zf + 3.28 + 0.3 * k), (0, 0, 0), "Emblem_Cream", 8, r2=0.42, bevel=0.0)
    mb.box((2.0, 1.1, 0.2), F.p(6.3, 4.9, zf + 3.23), F.r(0, 0, 0.1), "Wood_Plank", 0.0)
    mb.box((1.3, 0.3, 0.06), F.p(6.3, 4.8, zf + 3.37), F.r(0, 0, 0.1), "Metal_Dark", 0.0)
    for z in (6.2, 8.0):
        x0 = -8.0 if z < 7 else -1.2
        mb.box((8.0 - x0, 0.9, 0.22), F.p((x0 + 8.0) / 2, hd - 0.75, z), F.r(), "Wood_Dark", 0.0)
        for k in range(9):
            x = -7.4 + 1.85 * k
            if x < x0 + 0.4:
                continue
            if k % 3 == 1:
                mb.cyl(0.45, 0.9, F.p(x, hd - 0.75, z + 0.56), (0, 0, 0), "Emblem_Cream", 8, bevel=0.0)
            else:
                mb.cyl(0.5, 0.3, F.p(x, hd - 0.75, z + 0.26), (0, 0, 0), "Emblem_Cream", 8, r2=0.38, bevel=0.0)
    AK.hexa(mb, [F.p(-8.4, 3.9, 8.6), F.p(-1.8, 3.9, 8.6), F.p(-1.8, 5.8, 8.6), F.p(-8.4, 5.8, 8.6)],
            [F.p(-6.1, 4.8, 10.3), F.p(-4.1, 4.8, 10.3), F.p(-4.1, 5.6, 10.3), F.p(-6.1, 5.6, 10.3)], "Wood_Dark", 0.0)
    mb.cyl(0.55, 5.6, F.p(-5.1, 5.2, 12.9), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.cyl(0.85, 0.5, F.p(-5.1, 5.2, 15.6), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
    K.paper_lantern(mb, F.p(2.5, 3.3, zt - 0.8), r=0.7, h=1.3, paper="Lantern_Glow", cap="Wood_Dark", hang=0.8)
    mb.finish()
    A = "VillageRamen"
    col_box(A, (RW + 0.8, RD + 0.8, zf + 0.6), F.p(0, 0, zf / 2 - 0.3), F.r())
    for s in (-1, 1):
        col_box(A, (0.9, 8.4, zt - zf), F.p(s * (hw - 0.05), 2.0, (zt + zf) / 2), F.r())
    col_box(A, (RW + 0.8, 0.8, zt - zf), F.p(0, hd - 0.05, (zt + zf) / 2), F.r())
    for x in (-hw, -4.5, 4.5, hw):
        col_box(A, (0.9, 0.9, zt - zf), F.p(x, -hd, (zt + zf) / 2), F.r())
    col_box(A, (16.2, cy1 - cy0 + 0.3, 3.4), F.p(0, (cy0 + cy1) / 2 - 0.15, zf + 1.7), F.r())
    col_box(A, (16.6, by1 - by0, 3.2), F.p(-0.1, (by0 + by1) / 2, zf + 1.6), F.r())
    light("L_Village_Ramen", "POINT", F.p(0.0, 2.5, 8.2), 900, (1.0, 0.7, 0.42), 0.6)
    mk("NPC_Ramen", F.p(0, 3.1, zf), (0, 0, F.a + math.pi), 2.0, "ARROWS", props={"floor": T1 + zf})
    mk("PLAYER_INTERACT_Ramen", F.p(0, -2.9, zf), (0, 0, F.a), 2.0, "SPHERE", props={"floor": T1 + zf})


# ================================================================== ESTANDARTES (os 2 unicos da vila)
def banners():
    rng = random.Random(4501)
    mb = VMB("VIL_Banners", COLL, rng, detail="near", vcap=1)
    for s in (-1, 1):
        x, y, z = s * 8.5, 99.0, T1
        mb.box((1.9, 1.9, 1.1), (x, y + 0.3, z + 0.35), (0, 0, 0), "Stone_Wall_Light", 0.12)
        mb.box((1.3, 1.3, 0.5), (x, y + 0.3, z + 1.1), (0, 0, 0), "Stone_Wall_Light", 0.08)
        mb.cyl(0.28, 13.4, (x, y + 0.3, z + 1.2 + 6.7), (0, 0, 0), "Wood_Dark", 8, bevel=0.0)
        mb.cyl(0.45, 0.5, (x, y + 0.3, z + 14.7), (0, 0, 0), "Metal_Gold", 8, bevel=0.0)
        mb.cyl(0.3, 1.1, (x, y + 0.3, z + 15.4), (0, 0, 0), "Metal_Gold", 6, r2=0.02, bevel=0.0)
        FP.banner(mb, (x, y, z + 13.8), 0.0, w=3.6, h=8.6, cloth="Cloth_Red", trim="Metal_Gold", emblem=None)
        K.leaf_symbol(mb, Vector((x, y - 0.14, z + 13.8 - 8.6 * 0.45)), (1, 0, 0), (0, 0, 1), 1.35, "Emblem_Cream",
                      th=0.06, w=0.16)
        mb.box((3.0, 0.08, 0.22), (x, y - 0.14, z + 13.8 - 1.3), (0, 0, 0), "Emblem_Cream", 0.0)
    mb.finish()
    for s in (-1, 1):
        col_box("VillageBanners", (1.9, 1.9, 15.0), (s * 8.5, 99.3, T1 + 7.5))


def build():
    main_hall()
    weapon_shop()
    water_tower()
    ramen()
    banners()
