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
fm_lib.MATS.setdefault("Wood_VilLacquerDark", (S(118, 30, 24), 0.55, 0.0, 0, None, 0.06))  # testeira (laca escura)

# beirais (rodada 2): casca fina + testeira fina de laca escura + forro de madeira (os 3 predios redondos)
EAVE_TH = 0.55
FASCIA_M = "Wood_VilLacquerDark"
SOFFIT_M = "Wood_Dark_B"
BLUE_FASCIA_M = "Roof_Blue_B"          # nos azuis a borda fina fica azul (silhueta azul como nas refs)

T1, T2 = L.T1, L.T2
HX, HY, HR = L.MAIN_HALL
SX, SY, SR = L.BLUE_W
EX, EY, ER = L.BLUE_E
RX, RY, RW, RD, RYAW = L.RAMEN
COLL = "04_VILLAGE"

# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    # salao: 3/4, eixo desde o anel (estandartes + porta), altura do jogador, interior, fundo
    "CAM_Village_Hall34": ((30.0, 114.0, T2 + 16.0), (0.0, 158.0, T2 + 16.0), 22),
    "CAM_Village_Banners": ((0.0, 72.0, L.RING + 5.8), (0.0, 140.0, T1 + 12.0), 18),
    "CAM_Village_Player": ((3.0, 131.0, T2 + 5.0), (0.0, 160.0, T2 + 13.0), 18),
    "CAM_Village_HallEave": ((12.0, 133.0, T2 + 4.3), (0.0, 150.0, T2 + 15.8), 18),
    "CAM_Village_HallInterior": ((0.8, 144.2, T2 + 7.5), (0.0, 170.0, T2 + 6.0), 14),
    "CAM_Village_HallBack": ((40.0, 182.0, T2 + 34.0), (0.0, 160.0, T2 + 12.0), 22),
    # loja (BLUE_W): frente, camera de 3a pessoa entrando, no balcao, lanternim, fundo e lados
    "CAM_Village_Weapon": ((SX, SY - 38.0, T2 + 8.8), (SX, SY, T2 + 9.8), 20),
    "CAM_Village_WeaponPlayer": ((SX, SY - 24.0, T2 + 8.3), (SX, SY - 4.0, T2 + 6.8), 18),
    "CAM_Village_WeaponInterior": ((SX, SY - 9.5, T2 + 8.3), (SX, SY + 6.0, T2 + 3.3), 16),
    "CAM_Village_WeaponUp": ((SX, SY - 5.0, T2 + 2.8), (SX, SY + 2.0, T2 + 21.8), 14),
    "CAM_Village_WeaponBack": ((SX + 4.0, SY + 28.0, T2 + 15.8), (SX, SY, T2 + 9.8), 20),
    "CAM_Village_WeaponW": ((SX - 30.0, SY - 6.0, T2 + 9.8), (SX, SY, T2 + 9.8), 20),
    # BLUE_E (gemeo sem porta) + caixa d'agua atras
    "CAM_Village_Tower": ((EX, EY - 38.0, T2 + 8.8), (EX, EY, T2 + 9.8), 20),
    "CAM_Village_TowerBack": ((EX - 16.0, EY + 30.0, T2 + 14.0), (EX + 2.0, EY + 15.0, T2 + 8.0), 20),
    "CAM_Village_TowerE": ((EX + 40.0, EY + 12.0, T2 + 10.8), (EX, EY + 6.0, T2 + 8.0), 20),
    "CAM_Village_Twins": ((0.0, 92.0, T2 + 48.0), (0.0, 158.0, T2 + 10.0), 18),
    # ramen: 3/4, camera de 3a pessoa no ponto de interacao, olhando para fora, fundo e lados
    "CAM_Village_Ramen": ((RX + 18.0, RY - 23.0, T1 + 15.8), (RX, RY - 1.0, T1 + 7.8), 20),
    "CAM_Village_RamenPlayer": ((RX, RY - 16.0, T1 + 7.6), (RX, RY - 1.0, T1 + 4.3), 18),
    "CAM_Village_RamenInside": ((RX, RY - 3.5, T1 + 5.6), (RX, RY + 5.0, T1 + 3.6), 16),
    "CAM_Village_RamenOut": ((RX, RY + 3.0, T1 + 5.3), (RX, RY - 12.0, T1 + 8.3), 16),
    "CAM_Village_RamenBack": ((RX + 12.0, RY + 24.0, T1 + 19.8), (RX, RY, T1 + 7.8), 20),
    "CAM_Village_RamenE": ((RX + 20.0, RY + 8.0, T1 + 13.0), (RX, RY, T1 + 7.0), 20),
    "CAM_Village_Side": ((-112.0, 138.0, T2 + 26.0), (-20.0, 158.0, T2 + 10.0), 20),
    "CAM_Village_SideE": ((112.0, 138.0, T2 + 26.0), (20.0, 158.0, T2 + 10.0), 20),
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
BOOK_IN = 0.6         # recuo das estantes a partir da face interna da parede (pilastra ate r_wi - 0,5)


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
                mb.cyl(rr + 0.18, 0.35, p + Vector((0, 0, zz)), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
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
            mb.box((0.5, 4.4, 0.35), W(C, lc[0], lc[1], zz), (0, 0, yaw), "Metal_Gold", 0.0)
    # ---- 1o beiral (terracota) a +14: casca, fiadas (nervuras claras), testeira creme, cachorros
    # rodada 2: testeira FINA (0,6) em laca escura e forro de madeira (antes: testeira creme de 1,2 = aba de chapeu)
    K.cone_roof(mb, C, SKIRT1, EAVE_TH, "Roof_Terracotta", n=48, ribs=30, rib_m="Roof_Terracotta", rib_w=0.6,
                rib_h=0.3, fascia=K.eave_fascia(SKIRT1, EAVE_TH), fascia_m=FASCIA_M, rafters=24,
                rafter_r=(20.9, 25.5), courses=(22.6, 18.3), course_m="Roof_Terracotta_B", soffit=SOFFIT_M)
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
    K.cone_roof(mb, C, ROOF2, EAVE_TH, "Roof_Terracotta", n=40, ribs=20, rib_m="Roof_Terracotta", rib_w=0.55,
                rib_h=0.28, fascia=K.eave_fascia(ROOF2, EAVE_TH), fascia_m=FASCIA_M, rafters=0,
                rafter_r=(14.4, 17.4), courses=(12.6,), course_m="Roof_Terracotta_B", soffit=SOFFIT_M)
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
    mb.box((3.8, 3.4, 3.0), ec + Vector((0, 2.3, -1.1)), (0, 0, 0), "Roof_Terracotta", 0.1)   # acima do forro da rotunda
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
        F = tan_frame(C, H["r_wi"] - BOOK_IN, a, zf)
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
        mb.cyl(0.95, 0.3, p + Vector((0, 0, zf + 11.5)), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
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
    mb.cyl(1.6, 1.0, W(C, 0, 0, H["ceil2"] - 0.4), (0, 0, 0), "Metal_Gold", 10, bevel=0.0)
    # grande lanterna de papel no centro da rotunda
    mb.rod(W(C, 0, 0, H["ceil2"] - 0.6), W(C, 0, 0, 20.4), 0.1, "Wood_Dark", 4)
    K.paper_lantern(mb, W(C, 0, 0, 20.4), r=2.6, h=3.8, paper="Lantern_Glow", cap="Wood_Lacquer_Red",
                    band="Cloth_Red", hang=0.2, n=12)
    # tapete redondo com a folha
    rc = W(C, 0, -3.5, zf)
    mb.cyl(7.2, 0.1, rc + Vector((0, 0, 0.06)), (0, 0, 0), "Cloth_Red", 32, bevel=0.0)
    PK.ring(mb, rc + Vector((0, 0, 0.16)), 6.7, (1, 0, 0), (0, 1, 0), 0.45, 0.1, "Metal_Gold", n=24)
    PK.ring(mb, rc + Vector((0, 0, 0.16)), 7.3, (1, 0, 0), (0, 1, 0), 0.35, 0.1, "Cloth_Canvas", n=24)
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
        mb.cyl(0.14, 1.7, top + Vector((0.2 + s * 1.35, -0.4, 0.12)), (math.pi / 2, 0, 0.05), "Wood_Dark", 6,
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
    for a in BOOKCASES:      # 0,3 a frente da pilastra (sem face coplanar com o fundo da estante)
        K.bookcase(mb, tan_frame(C, H["r_wi"] - BOOK_IN, a, zf), 3.6, 8.6, 1.5, rng, shelves=4)
    for a in (10.0, 170.0, 210.0, 330.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        mb.box((2.6, 0.12, 6.4), F.p(0, 0.62, 8.2), F.r(), "Cloth_Canvas", 0.0)
        mb.box((3.1, 0.3, 0.3), F.p(0, 0.66, 11.5), F.r(), "Wood_Dark", 0.0)
        mb.box((3.0, 0.3, 0.3), F.p(0, 0.66, 4.95), F.r(), "Wood_Dark", 0.0)
        tx = F.p(1, 0, 0) - F.p(0, 0, 0)
        if a in (10.0, 170.0):
            K.leaf_symbol(mb, F.p(0, 0.82, 8.8), tx, (0, 0, 1), 0.95, "Cloth_Red", th=0.06)
        else:
            for z in (6.5, 7.5, 8.5, 9.5):
                mb.box((1.4 if z != 8.5 else 1.8, 0.06, 0.18), F.p(rng.uniform(-0.3, 0.3), 0.82, z), F.r(),
                       "Wood_Dark", 0.0)
    # bancos baixos junto a parede (espera) a leste e oeste
    for a in (190.0, 350.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        mb.box((4.4, 1.6, 0.4), F.p(0, 1.1, 1.5), F.r(), "Wood_Plank", 0.0)
        for sx in (-1, 1):
            mb.box((0.4, 1.4, 1.3), F.p(sx * 1.8, 1.1, 0.65), F.r(), "Wood_Dark", 0.0)


# ================================================================== PREDIOS REDONDOS AZUIS (GEMEOS)
# Rodada 2 (refs 14/17/18): BLUE_W (loja, entravel) e BLUE_E (sem porta) com a MESMA silhueta: tambor com pilares,
# beiral azul, tambor de cima com janelas, 2o telhado azul e oculo no topo, cumeeira na mesma cota. A loja ganhou
# porta de 9,1 livres (x -62,55..-53,45) com verga em z 35,6 (12,6 livres sobre o piso): o conjunto subiu 1,6 para o
# beiral passar acima da verga. Z relativo a T2.
BLUE = dict(r_pl=13.6, r_wo=12.2, r_wi=11.0, fl=0.6, wall_top=16.7, door_free=4.55, door_h=12.8,
            up_ro=8.2, up_ri=7.3, up_bot=15.8, up_top=23.0, ceil=16.6, ceil2=22.6, pil_top=13.7, band=(13.7, 14.5),
            skirt=[(15.9, 15.2), (13.2, 16.3), (10.4, 17.6), (7.9, 19.0)],
            roof_b=[(10.7, 22.2), (8.0, 23.5), (5.2, 25.0), (2.8, 26.2)],
            win=(2.8, 5.4, 9.4))     # janelas quadradas do terreo: largura, peitoril, verga (peitoril 4,8 acima da base)
SHOP = BLUE
SHOP_CY = 4.5         # centro do balcao (y local): balcao em y 157,5..159,5
TANK = (2.0, 19.0)    # caixa d'agua do BLUE_E (x, y local): atras do predio (y 169,4..176,6), topo abaixo da cumeeira


def blue_door_dh(H):
    """meia abertura (graus) do vao da porta, medida no raio INTERNO: vao reto de 2 x door_free na parede toda"""
    return math.degrees(math.asin(H["door_free"] / H["r_wi"]))


def blue_up_win_z(H):
    return (H["up_bot"] + H["up_top"]) / 2 + 0.6


def round_blue_shell(mb, C, H, rng, door, rib_seed=0.0):
    """casca comum dos predios redondos azuis: embasamento, tambor, pilares, janelas, beiral azul, tambor de cima,
    2o telhado e oculo (identica nos 2 predios; so a porta muda)"""
    fl = H["fl"]
    dh = blue_door_dh(H) if door else 0.0
    gaps = [(DOOR_A, dh)] if door else []
    K.plinth(mb, C, H["r_pl"], fl, rng, n=36)
    K.ring_wall(mb, C, H["r_wi"], H["r_wo"], 0.4, H["wall_top"], "Plaster_Cream", 40, gaps=gaps)
    if door:
        zd = fl + H["door_h"] + 0.1          # 0,1 acima da face de baixo da verga (sem face coplanar)
        K.lathe(mb, C, [(H["r_wi"], zd), (H["r_wo"], zd), (H["r_wo"], H["wall_top"]), (H["r_wi"], H["wall_top"])],
                "Plaster_Cream", 4, DOOR_A - dh, DOOR_A + dh)
    K.ring_wall(mb, C, H["r_wo"] - 0.1, H["r_wo"] + 0.28, 0.7, 1.9, "Stone_Wall_Dark", 40,
                gaps=[(DOOR_A, dh + 2.0)] if door else [])
    b0, b1 = H["band"]
    K.lathe(mb, C, [(H["r_wo"] - 0.1, b0), (H["r_wo"] + 0.32, b0), (H["r_wo"] + 0.32, b1), (H["r_wo"] - 0.1, b1)],
            "Wood_Lacquer_Red", 40)
    # pilares (12, de 30 em 30). Com porta: o vao fica entre 2 pilares (o do eixo sai). Sem porta: mesmo ritmo,
    # com uma janela no eixo (o predio le igual de frente, sem porta nenhuma)
    off = 0.0 if door else 15.0
    ph = H["pil_top"] - fl
    for k in range(12):
        a = DOOR_A + off + 30.0 * k
        if door and k == 0:
            continue
        p = pol(C, H["r_wo"] + 0.2, a)
        mb.cyl(0.7, ph, p + Vector((0, 0, fl + ph / 2)), (0, 0, 0), "Wood_Lacquer_Red", 8, bevel=0.0)
        mb.box((1.9, 1.9, 0.6), p + Vector((0, 0, fl + 0.3)), (0, 0, math.radians(a)), "Stone_Wall_Light", 0.0)
        mb.box((1.8, 1.8, 0.45), p + Vector((0, 0, H["pil_top"] - 0.35)), (0, 0, math.radians(a)), "Wood_Dark", 0.0)
    # janelas quadradas entre os pilares (peitoril 4,8 acima da base, 4 de altura)
    ww, wz0, wz1 = H["win"]
    for k in range(12):
        a = DOOR_A + off + 15.0 + 30.0 * k
        if door and k in (0, 11):
            continue
        K.drum_window(mb, C, H["r_wo"], a, ww, wz0, wz1, jambs=False)
    # beiral azul (testeira fina + forro de madeira)
    sk = H["skirt"]
    K.cone_roof(mb, C, sk, EAVE_TH, "Roof_Blue", n=40, ribs=20, rib_m="Roof_Blue_B", rib_w=0.55, rib_h=0.26,
                fascia=K.eave_fascia(sk, EAVE_TH), fascia_m=BLUE_FASCIA_M, rafters=16,
                rafter_r=(H["r_wo"] + 0.4, sk[0][0] - 0.45), a_off=rib_seed, soffit=SOFFIT_M)
    # tambor de cima com janelas acesas
    K.lathe(mb, C, [(H["up_ri"], H["up_bot"]), (H["up_ro"], H["up_bot"]), (H["up_ro"], H["up_top"]),
                    (H["up_ri"], H["up_top"])], "Plaster_Cream", 32)
    K.lathe(mb, C, [(H["up_ro"] - 0.1, H["up_top"] - 1.9), (H["up_ro"] + 0.28, H["up_top"] - 1.9),
                    (H["up_ro"] + 0.28, H["up_top"] - 1.2), (H["up_ro"] - 0.1, H["up_top"] - 1.2)],
                "Wood_Lacquer_Red", 32)
    zc = blue_up_win_z(H)
    for k in range(8):
        a = DOOR_A + 22.5 + 45.0 * k
        tan_box(mb, C, H["up_ro"] + 0.05, a, (1.4, 0.25, 1.4), zc, "Window_Warm")
        tan_box(mb, C, H["up_ro"] + 0.16, a, (1.9, 0.3, 0.35), zc + 0.87, "Wood_Dark")
        tan_box(mb, C, H["up_ro"] + 0.2, a, (2.0, 0.5, 0.35), zc - 0.87, "Wood_Dark")
    # 2o telhado azul + oculo (anel creme com o miolo rebaixado) + pinaculo dourado
    rb = H["roof_b"]
    K.cone_roof(mb, C, rb, EAVE_TH, "Roof_Blue", n=32, ribs=14, rib_m="Roof_Blue_B", rib_w=0.45, rib_h=0.24,
                fascia=K.eave_fascia(rb, EAVE_TH), fascia_m=BLUE_FASCIA_M, rafters=0, rafter_r=(8.6, 10.4),
                soffit=SOFFIT_M)
    zt = rb[-1][1]
    K.lathe(mb, C, [(1.7, zt - 0.3), (3.1, zt - 0.3), (3.1, zt + 0.6), (1.7, zt + 0.6)], "Plaster_Cream", 16)
    K.lathe(mb, C, [(0.3, zt - 0.2), (1.75, zt - 0.2), (1.75, zt + 0.3), (0.3, zt + 0.3)], "Roof_Blue_B", 16)
    mb.cyl(0.4, 1.6, W(C, 0, 0, zt + 1.1), (0, 0, 0), "Metal_Gold", 8, bevel=0.0)
    mb.ico(0.55, W(C, 0, 0, zt + 2.3), "Metal_Gold", 1)
    return dh


# ------------------------------------------------------------------ LOJA DE ARMAS NINJA (oeste, entravel)
def weapon_shop():
    C = (SX, SY, T2)
    H = SHOP
    rng = random.Random(4201)
    mb = VMB("VIL_WeaponShop", COLL, rng, detail="near", vcap=1)
    fl = H["fl"]
    df = H["door_free"]
    dh = round_blue_shell(mb, C, H, rng, door=True)
    # portal: batentes que cobrem a ponta da parede toda, verga (0,18 a frente da faixa de laca), degrau de pedra.
    # Sem noren: a verga fica a 12,6 do piso (camera livre na porta)
    for s in (-1, 1):
        mb.box((0.7, 2.6, H["door_h"] + 0.2), W(C, s * (df + 0.35), -11.2, fl + H["door_h"] / 2),
               (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((2 * df + 1.4, 2.0, 0.8), W(C, 0, -11.7, fl + H["door_h"] + 0.4), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((2 * df - 0.4, 0.3, 0.45), W(C, 0, -12.85, fl + H["door_h"] + 0.4), (0, 0, 0), "Cloth_Royal_Blue", 0.0)
    mb.box((2 * df + 0.6, 1.5, 0.3), W(C, 0, -14.1, 0.15), (0, 0, 0), "Stone_Wall_Light", 0.0)
    # folhas da porta abertas para dentro (135 graus), dobradica na face interna do batente
    for s in (-1, 1):
        lc, yaw = leaf_pose(s, df - 0.15, -9.9, 4.4)
        mb.box((0.28, 4.4, H["door_h"] - 0.3), W(C, lc[0], lc[1], fl + H["door_h"] / 2 - 0.1), (0, 0, yaw),
               "Wood_Plank", 0.0)
    # placa pendurada num braco (icone de kunai), no pilar a oeste da porta: a face olha para ESE (praca/escada)
    a = DOOR_A - 30.0
    rad = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0.0))
    tng = Vector((-rad.y, rad.x, 0.0))
    zs = 1.2
    mb.beam(pol(C, H["r_wo"] + 0.9, a, 10.6 + zs), pol(C, H["r_wo"] + 5.4, a, 10.6 + zs), 0.45, 0.55, "Wood_Dark", 0.0)
    mb.beam(pol(C, H["r_wo"] + 0.9, a, 8.2 + zs), pol(C, H["r_wo"] + 3.0, a, 10.4 + zs), 0.6, 0.36, "Wood_Dark", 0.0)
    bc = pol(C, H["r_wo"] + 3.4, a, 8.4 + zs)
    for s in (-1, 1):
        mb.rod(pol(C, H["r_wo"] + 3.4 + s * 1.5, a, 10.4 + zs), pol(C, H["r_wo"] + 3.4 + s * 1.5, a, 9.8 + zs), 0.07,
               "Metal_Dark", 4)
    brot = (0, 0, math.atan2(rad.y, rad.x))
    mb.box((3.8, 0.34, 2.8), bc, brot, "Wood_Plank", 0.0)
    for dz in (1.45, -1.45):
        mb.box((4.1, 0.5, 0.3), bc + Vector((0, 0, dz)), brot, "Wood_Dark", 0.0)
    for s in (-1, 1):
        d = (rad * 0.62 + Vector((0, 0, 0.78))).normalized()
        K.kunai(mb, bc + tng * s * 0.3 - rad * 0.3 - Vector((0, 0, 0.15)), d, tng * s, s=1.25, ring_n=8)
    shop_interior(mb, C, H)
    mb.finish()
    # colisao
    A = "VillageShop"
    col_disk(A, C, H["r_pl"] - 0.25, 0.0, fl, n=8)
    col_disk(A, C, H["r_wi"], 0.0, fl + 0.22, n=10)
    col_box2(A, W(C, -df - 0.3, -H["r_pl"], 0.0), W(C, df + 0.3, -H["r_wi"], fl))
    col_box2(A, W(C, -df - 0.3, -14.85, 0.0), W(C, df + 0.3, -H["r_pl"], 0.3))
    col_ring(A, C, H["r_wi"], H["r_wo"] + 0.3, fl, H["wall_top"], K.arc_spans([(DOOR_A, dh)]), seg=30.0)
    col_box2(A, W(C, -df, -H["r_wo"] - 0.5, fl + H["door_h"]), W(C, df, -H["r_wi"] + 0.4, H["wall_top"]))
    ph = H["pil_top"] - fl
    for s in (-1, 1):
        col_box(A, (1.8, 1.8, ph), pol(C, H["r_wo"] + 0.2, DOOR_A + s * 30.0, fl + ph / 2))
        lc, yaw = leaf_pose(s, df - 0.15, -9.9, 4.4)
        col_box(A, (0.4, 4.4, H["door_h"] - 0.3), W(C, lc[0], lc[1], fl + H["door_h"] / 2 - 0.1), (0, 0, yaw))
    zf = fl + 0.22
    col_box(A, (9.6, 2.0, 3.5), W(C, 0, SHOP_CY, zf + 1.75))
    for a, w in ((90.0, 7.4), (180.0, 5.2), (0.0, 5.2)):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        col_box(A, (w, 0.8, 7.0), F.p(0, 0.4, 3.5), F.r())
    for a in (142.0, 38.0):
        F = tan_frame(C, H["r_wi"] - 0.3, a, zf)
        col_box(A, (4.2, 1.8, 5.0), F.p(0, 0.9, 2.5), F.r())
    for s in (-1, 1):
        col_box(A, (2.2, 2.2, 2.6), W(C, s * 7.2, -4.6, zf + 1.3))
    light("L_Village_ShopInterior", "POINT", W(C, 0, 0, 12.5), 2800, (1.0, 0.74, 0.48), 0.8)
    mk("NPC_WeaponShop", W(C, 0, SHOP_CY + 2.6, zf), (0, 0, math.pi), 2.0, "ARROWS", props={"floor": C[2] + zf})
    mk("PLAYER_INTERACT_WeaponShop", W(C, 0, SHOP_CY - 3.6, zf), (0, 0, 0), 2.0, "SPHERE",
       props={"floor": C[2] + zf})


def shop_interior(mb, C, H):
    rng = random.Random(4202)
    fl = H["fl"]
    zf = fl + 0.22
    dh = blue_door_dh(H)
    K.round_floor(mb, C, H["r_wi"] + 0.05, zf, rng, pw=1.4)
    K.ring_wall(mb, C, H["r_wi"] - 0.22, H["r_wi"] + 0.02, zf, zf + 2.2, "Wood_Dark", 40, gaps=[(DOOR_A, dh + 3.0)])
    ww, wz0, wz1 = H["win"]
    for a in (225.0, 315.0):
        K.drum_window(mb, C, H["r_wi"], a, ww, wz0, wz1, out=-1, sill=False, jambs=False)
    hp = H["ceil"] - zf - 0.2
    for k in range(1, 12):
        tan_box(mb, C, H["r_wi"] - 0.22, DOOR_A + 30.0 * k, (1.0, 0.45, hp), zf + hp / 2, "Wood_Lacquer_Red")
    # forro em anel + vigas + tambor de cima aberto (lanternim) com teto alto
    K.lathe(mb, C, [(H["up_ri"], H["ceil"]), (H["r_wi"] + 0.05, H["ceil"]), (H["r_wi"] + 0.05, H["ceil"] + 0.3),
                    (H["up_ri"], H["ceil"] + 0.3)], "Plaster_Cream", 32)
    K.lathe(mb, C, [(H["up_ri"] - 0.3, H["ceil"] - 0.7), (H["up_ro"] + 0.5, H["ceil"] - 0.7),
                    (H["up_ro"] + 0.5, H["ceil"]), (H["up_ri"] - 0.3, H["ceil"])], "Wood_Dark", 32)
    for k in range(12):
        a = DOOR_A + 30.0 * k
        mb.beam(pol(C, H["up_ro"] + 0.4, a, H["ceil"] - 0.3), pol(C, H["r_wi"] - 0.1, a, H["ceil"] - 0.3), 0.5, 0.6,
                "Wood_Dark", 0.0)
    K.lathe(mb, C, [(0.5, H["ceil2"]), (H["up_ri"] + 0.05, H["ceil2"]), (H["up_ri"] + 0.05, H["ceil2"] + 0.3),
                    (0.5, H["ceil2"] + 0.3)], "Plaster_Cream", 24)
    mb.cyl(0.55, 0.3, W(C, 0, 0, H["ceil2"] - 0.15), (0, 0, 0), "Wood_Dark", 8, bevel=0.0)
    for k in range(6):
        a = 30.0 + 60.0 * k
        mb.beam(pol(C, 0.9, a, H["ceil2"] - 0.3), pol(C, H["up_ri"] - 0.05, a, H["ceil2"] - 0.3), 0.45, 0.6,
                "Wood_Dark", 0.0)
    zc = blue_up_win_z(H)
    for k in range(8):
        tan_box(mb, C, H["up_ri"] - 0.05, DOOR_A + 22.5 + 45.0 * k, (1.4, 0.25, 1.4), zc, "Window_Warm")
    # lanterna pendurada NO lanternim (fundo em z ~40, acima do ponto de interacao: camera livre)
    K.paper_lantern(mb, W(C, 0, 0, H["ceil2"] - 0.3), r=1.6, h=2.4, paper="Lantern_Glow", cap="Wood_Dark",
                    band="Cloth_Royal_Blue", hang=1.4, n=10)
    # balcao (frente de laca vermelha, tampo claro) - NPC atras, jogador na frente
    cc = W(C, 0, SHOP_CY, zf)
    mb.box((9.4, 2.0, 3.2), cc + Vector((0, 0, 1.6)), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((10.0, 2.5, 0.3), cc + Vector((0, -0.15, 3.35)), (0, 0, 0), "Wood_Light", 0.0)
    for k in range(4):
        mb.box((1.9, 0.3, 2.3), cc + Vector((-3.45 + 2.3 * k, -1.0, 1.65)), (0, 0, 0), "Wood_Lacquer_Red", 0.0)
    ct = cc + Vector((0, 0, 3.5))
    mb.box((2.6, 1.2, 0.14), ct + Vector((-2.6, -0.2, 0.07)), (0, 0, 0), "Wood_Plank", 0.0)
    for k in range(4):
        K.kunai(mb, ct + Vector((-3.3 + 0.45 * k, 0.05, 0.22)), (0.05, -1, 0), (0, 0, 1), s=0.8)
    K.shuriken(mb, ct + Vector((1.6, -0.3, 0.12)), (0, 0, 1), up=(1, 0, 0), R=0.75)
    K.shuriken(mb, ct + Vector((2.8, 0.1, 0.12)), (0, 0, 1), up=(1, 0, 0), R=0.6, spin=20.0)
    # parede do fundo (norte): painel com 3 katanas horizontais + faixa de shuriken
    F = tan_frame(C, H["r_wi"] - 0.3, 90.0, zf)
    tx, ty = F.p(1, 0, 0) - F.p(0, 0, 0), F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.box((7.4, 0.3, 5.6), F.p(0, 0.15, 6.4), F.r(), "Wood_Plank", 0.0)
    for z in (9.35, 3.45):
        mb.box((7.8, 0.5, 0.35), F.p(0, 0.25, z), F.r(), "Wood_Dark", 0.0)
    for i, z in enumerate((4.6, 6.2, 7.8)):
        for s in (-1, 1):
            mb.box((0.3, 0.5, 0.36), F.p(s * 2.4, 0.45, z - 0.25), F.r(), "Wood_Dark", 0.0)
        K.katana(mb, F.p(-3.0, 0.75, z), tx, ty, L=6.0, sheath=("Wood_Lacquer_Red" if i == 1 else None),
                 grip=("Cloth_Royal_Blue" if i == 0 else "Wood_Dark"))
    for k in range(5):
        K.shuriken(mb, F.p(-2.8 + 1.4 * k, 0.45, 8.7), ty, up=(0, 0, 1), R=0.5, spin=15.0 * k)
    # oeste: suporte de kunais (2 fileiras penduradas, ponta para baixo)
    F = tan_frame(C, H["r_wi"] - 0.3, 180.0, zf)
    ty = F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.box((5.2, 0.3, 4.6), F.p(0, 0.15, 6.0), F.r(), "Wood_Plank", 0.0)
    for z in (7.3, 4.8):
        mb.box((5.0, 0.5, 0.36), F.p(0, 0.45, z + 1.05), F.r(), "Wood_Dark", 0.0)
        for k in range(5):
            K.kunai(mb, F.p(-1.9 + 0.95 * k, 0.5, z - 0.15), (0, 0, -1), ty, s=0.9)   # argola dentro da trave
    # leste: painel de shuriken (4 pequenos + 1 grande)
    F = tan_frame(C, H["r_wi"] - 0.3, 0.0, zf)
    ty = F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.box((5.2, 0.3, 4.6), F.p(0, 0.15, 6.0), F.r(), "Wood_Plank", 0.0)
    mb.box((5.6, 0.5, 0.36), F.p(0, 0.25, 8.4), F.r(), "Wood_Dark", 0.0)
    for i in (0, 2):
        for j in range(2):
            K.shuriken(mb, F.p(-1.7 + 1.7 * i, 0.45, 4.7 + 2.6 * j), ty, up=(0, 0, 1), R=0.7, spin=10.0 * (i + j))
    K.shuriken(mb, F.p(0, 0.5, 6.0), ty, up=(0, 0, 1), R=1.25, spin=45.0)
    # noroeste: cavalete de katanas no chao; nordeste: prateleira com caixas de shuriken
    F = tan_frame(C, H["r_wi"] - 0.3, 142.0, zf)
    tx = F.p(1, 0, 0) - F.p(0, 0, 0)
    for s in (-1, 1):
        mb.box((0.4, 1.2, 4.2), F.p(s * 1.9, 1.0, 2.1), F.r(), "Wood_Dark", 0.0)
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
            K.shuriken(mb, F.p(-1.2 + 1.2 * k, 0.8, z + 0.9), (0, 0, 1), up=tuple(tx), R=0.35)
    # barris de kunai junto a porta (lado de dentro, fora do giro das folhas)
    for s in (-1, 1):
        bc = W(C, s * 7.2, -4.6, zf)
        FP.barrel(mb, (bc.x, bc.y, bc.z), r=1.05, h=2.5)
        brng = random.Random(4210 + s)
        for k in range(5):
            aa = brng.uniform(0, math.tau)
            rr = brng.uniform(0.0, 0.6)
            d = Vector((math.cos(aa) * 0.3, math.sin(aa) * 0.3, 1.0)).normalized()
            p = bc + Vector((math.cos(aa) * rr, math.sin(aa) * rr, 2.3))
            K.kunai(mb, p, d, Vector((-math.sin(aa), math.cos(aa), 0)), s=0.85, ring=False)


# ------------------------------------------------------------------ BLUE_E (leste): gemeo da loja, sem porta nenhuma
def water_tower():
    """predio redondo azul SEM porta (deposito da vila), com a mesma silhueta da loja; a caixa d'agua fica ATRAS
    (y >= 169), sobre um cavalete, com o topo bem abaixo da cumeeira, ligada ao predio por um cano"""
    C = (EX, EY, T2)
    H = BLUE
    rng = random.Random(4301)
    mb = VMB("VIL_WaterTower", COLL, rng, detail="near", vcap=1)
    round_blue_shell(mb, C, H, rng, door=False)
    # caixa d'agua no cavalete (atras)
    tx, ty = TANK
    T = W(C, tx, ty, 0.0)
    zd = 7.0                                   # deck do cavalete
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.8, 0.8, zd), T + Vector((sx * 2.7, sy * 2.7, zd / 2)), (0, 0, 0), "Wood_Dark", 0.0)
            mb.box((1.3, 1.3, 0.5), T + Vector((sx * 2.7, sy * 2.7, 0.25)), (0, 0, 0), "Stone_Wall_Dark", 0.0)
    for sy in (-1, 1):                          # travessas em X nas 2 faces L-O e nas 2 faces N-S
        mb.beam(T + Vector((-2.7, sy * 2.7, 1.2)), T + Vector((2.7, sy * 2.7, zd - 0.8)), 0.4, 0.4, "Wood_Dark", 0.0)
        mb.beam(T + Vector((sy * 2.7, -2.7, 1.2)), T + Vector((sy * 2.7, 2.7, zd - 0.8)), 0.4, 0.4, "Wood_Dark", 0.0)
    mb.box((7.0, 7.0, 0.5), T + Vector((0, 0, zd + 0.25)), (0, 0, 0), "Wood_Plank", 0.0)
    zt = zd + 0.5
    K.lathe(mb, T, [(0.5, zt), (3.3, zt), (3.3, zt + 5.4), (0.5, zt + 5.4)], "Wood_Dark", 16)
    nst = 16
    for k in range(nst):
        a = 360.0 * (k + 0.5) / nst
        hh = 5.6 + rng.uniform(-0.1, 0.1)
        tan_box(mb, T, 3.55, a, (2 * math.pi * 3.8 / nst - 0.12, 0.5, hh), zt + hh / 2, "Wood_Plank")
    for z in (zt + 0.8, zt + 4.6):
        K.lathe(mb, T, [(3.7, z - 0.25), (4.0, z - 0.25), (4.0, z + 0.25), (3.7, z + 0.25)], "Metal_Dark", 16)
    zl = zt + 5.6
    K.lathe(mb, T, [(4.4, zl), (2.4, zl + 1.2), (0.5, zl + 2.0), (0.5, zl - 0.45), (4.4, zl - 0.45)], "Roof_Blue", 16)
    mb.cyl(0.5, 1.0, T + Vector((0, 0, zl + 2.4)), (0, 0, 0), "Metal_Gold", 8, r2=0.3, bevel=0.0)
    # cano: desce do fundo da caixa e entra na parede de tras ABAIXO da janela norte (peitoril em 5,06)
    zp = 3.2
    xp = tx - 1.2
    yw = math.sqrt((H["r_wo"] + 0.05) ** 2 - xp ** 2)
    pk = T + Vector((-1.2, -1.6, zp))
    mb.rod(T + Vector((-1.2, -1.6, zd + 0.3)), pk, 0.38, "Metal_Dark", 8)
    mb.rod(pk, W(C, xp, yw, zp), 0.38, "Metal_Dark", 8)
    mb.cyl(0.6, 0.9, pk, (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.cyl(0.6, 0.5, W(C, xp, yw + 0.7, zp), (math.pi / 2, 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.finish()
    A = "VillageTower"
    col_disk(A, C, H["r_pl"] - 0.25, 0.0, H["fl"], n=12)
    col_disk(A, C, H["r_wo"] + 0.2, H["fl"], H["wall_top"], n=8)
    col_box(A, (7.0, 7.0, zl + 2.0), T + Vector((0, 0, (zl + 2.0) / 2)))


# ================================================================== BARRACA DE RAMEN (T1, frente para o sul)
# Rodada 2 (critica de level design): pe-direito >= 12 (viga da frente e beiral em z >= piso + 12 = 28,8), cumeeira
# ~34, noren no maximo 2,5 abaixo da viga (base >= 26) e interacao na metade da frente (camera ao ar livre).
RAMEN_ZF = 0.55          # topo do assoalho (relativo a T1)
RAMEN_ZT = 14.05         # topo das paredes / apoio do telhado: beiral = ZT - 0,62 x 2,3 = 12,62 (z 28,82)
RAMEN_NOREN = 2.4        # altura do noren (pendurado na viga)
RAMEN_IY = -4.0          # interacao (y local): metade da frente, y ~103


def ramen():
    F = Frame(RX, RY, T1, math.radians(RYAW))
    rng = random.Random(4401)
    mb = VMB("VIL_Ramen", COLL, rng, detail="near", vcap=1)
    hw, hd = RW / 2, RD / 2           # 9 x 6
    zf = RAMEN_ZF
    zt = RAMEN_ZT
    zb = zt - 0.9                     # face de baixo da viga da frente (13,15 -> z 29,35)
    red = "Cloth_VilLantern"
    # base de pedra + assoalho de tabuas
    mb.box((RW + 0.8, RD + 0.8, 1.0), F.p(0, 0, -0.3), F.r(), "Stone_Wall_Light", 0.04)   # topo 0,2: assoalho 0,15 acima
    mb.box((RW + 1.0, 0.3, 0.3), F.p(0, -hd - 0.35, 0.2), F.r(), "Stone_Wall_Dark", 0.0)
    FP.plank_floor(mb, F, RW - 0.4, RD - 0.4, zf - 0.2, rng, pw=1.3, h=0.22)
    # pilares
    for x, y in ((-hw, -hd), (hw, -hd), (-4.5, -hd), (4.5, -hd), (-hw, -2.0), (hw, -2.0), (-hw, hd), (hw, hd),
                 (0.0, hd)):
        mb.box((0.8, 0.8, zt - zf), F.p(x, y, (zt + zf) / 2), F.r(), "Wood_Dark", 0.0)
        mb.box((1.1, 1.1, 0.4), F.p(x, y, zf + 0.2), F.r(), "Stone_Wall_Dark", 0.0)
    # paredes laterais (y -2..6) e do fundo: rodape de tabua + reboco + travessas; janela na cozinha e respiro alto
    zp = zf + 2.2
    for s in (-1, 1):
        x = s * (hw - 0.05)
        mb.box((0.45, 8.0, 2.2), F.p(x, 2.0, zf + 1.1), F.r(), "Wood_Plank", 0.0)
        mb.box((0.35, 8.0, zt - zp), F.p(x, 2.0, zp + (zt - zp) / 2), F.r(), "Plaster_Cream", 0.0)
        for z in (zf + 2.25, 7.4, 11.2):
            mb.box((0.6, 8.0, 0.35), F.p(x, 2.0, z), F.r(), "Wood_Dark", 0.0)
        mb.box((0.6, 2.8, 2.0), F.p(x, 2.6, 5.4), F.r(), "Window_Warm", 0.0)
        for yy in (1.2, 2.6, 4.0):
            mb.box((0.85, 0.22, 2.3), F.p(x, yy, 5.4), F.r(), "Wood_Dark", 0.0)
        mb.box((0.6, 3.4, 1.1), F.p(x, 2.0, 9.3), F.r(), "Window_Warm", 0.0)
        for yy in (0.8, 2.0, 3.2):
            mb.box((0.85, 0.22, 1.3), F.p(x, yy, 9.3), F.r(), "Wood_Dark", 0.0)
    mb.box((RW, 0.45, 2.2), F.p(0, hd - 0.05, zf + 1.1), F.r(), "Wood_Plank", 0.0)
    mb.box((RW, 0.35, zt - zp), F.p(0, hd - 0.05, zp + (zt - zp) / 2), F.r(), "Plaster_Cream", 0.0)
    for z in (zf + 2.25, 7.4, 11.2):
        mb.box((RW, 0.6, 0.35), F.p(0, hd - 0.05, z), F.r(), "Wood_Dark", 0.0)
    # viga da frente (verga), frechal lateral e tirantes (onde penduram as lanternas)
    mb.box((RW + 1.2, 0.9, 0.9), F.p(0, -hd, zt - 0.45), F.r(), "Wood_Dark", 0.0)
    for s in (-1, 1):
        mb.box((0.9, RD + 0.9, 0.8), F.p(s * hw, 0, zt - 0.4), F.r(), "Wood_Dark", 0.0)
    for y in (-2.0, 2.2):
        mb.box((RW, 0.6, 0.6), F.p(0, y, zt - 0.5), F.r(), "Wood_Dark", 0.0)
    # telhado verde de 4 aguas (kit de arquitetura do lobby), no mesmo objeto: beiral 12,62, cumeeira 17,75
    import fm_arch_kit as AK
    AK.hip_roof(mb, F, 0.0, 0.0, hw, hd, zt, 0.62, random.Random(4403), over=2.3, m="Roof_Green", m2=None, alt=0.0,
                patches=False, ridge_m="Wood_Dark", bevel=0.0, course=1.8, tile=(2.4, 3.4))
    # noren: 6 panos pendurados na viga (2,4 de altura: base 2,4 abaixo da viga) + faixa vermelha continua no alto;
    # espessuras com >= 0,12 de folga entre faces de materiais diferentes (sem z-fighting)
    yn = -hd - 0.72
    zn = zb - 0.05 - RAMEN_NOREN / 2
    for k in range(6):
        x = -7.55 + 3.02 * k
        mb.box((2.75, 0.12, RAMEN_NOREN), F.p(x, yn, zn), F.r(0.03 * (k % 2 * 2 - 1), 0, 0), "Cloth_VilNoren", 0.0)
        if k in (1, 4):
            bowl_i = [(math.cos(math.radians(a)) * 0.8, math.sin(math.radians(a)) * 0.55) for a in range(180, 361, 30)]
            PK.plate(mb, bowl_i, F.p(x, yn - 0.16, zn + 0.1), (1, 0, 0), (0, 0, 1), 0.2, red)
    mb.box((RW + 0.2, 0.45, 0.45), F.p(0, -hd - 0.675, zb - 0.2), F.r(), red, 0.0)
    # lanternas de papel vermelhas: 2 nos cantos da frente (sob o beiral) + 3 sobre o balcao (altas)
    for s in (-1, 1):
        K.paper_lantern(mb, F.p(s * (hw + 0.6), -hd - 1.4, zt - 1.3), r=0.95, h=1.9, paper=red, cap="Wood_Dark",
                        band="Lantern_Glow", hang=0.45)
    for x in (-5.0, 0.0, 5.0):
        K.paper_lantern(mb, F.p(x, -2.0, zt - 0.8), r=0.75, h=1.5, paper=red, cap="Wood_Dark", band="Lantern_Glow",
                        hang=0.4)
    # placa no telhado da frente: tigela de ramen com hashi e vapor (sem texto)
    dz = zt - 10.4
    sc = F.p(0, -hd + 1.2, 12.6 + dz)
    tilt = -math.radians(18.0)
    for s in (-1, 1):
        mb.box((0.4, 0.4, 2.6), F.p(s * 2.6, -hd + 1.6, 11.3 + dz), F.r(), "Wood_Dark", 0.0)
    mb.box((7.2, 0.4, 2.6), sc, F.r(tilt, 0, 0), "Wood_Lacquer_Red", 0.0)
    mb.box((7.6, 0.4, 0.4), sc + Vector((0, 0.35, 1.35)), F.r(tilt, 0, 0), "Wood_Dark", 0.0)
    nrm = Vector((0.0, -math.cos(-tilt), math.sin(-tilt)))
    u = Vector((1.0, 0.0, 0.0))
    v = nrm.cross(u)
    bo = sc + nrm * 0.2 - v * 0.25
    bowl = [(math.cos(math.radians(a)) * 1.25, math.sin(math.radians(a)) * 0.95) for a in range(180, 361, 20)]
    PK.plate(mb, bowl, bo + nrm * 0.1, u, v, 0.2, "Emblem_Cream")
    PK.plate(mb, [(-1.25, -0.02), (1.25, -0.02), (1.1, -0.3), (-1.1, -0.3)], bo + nrm * 0.3, u, v, 0.2, red)
    for s in (0, 1):
        dd = (u * 0.35 + v).normalized()
        o2 = bo + u * (0.25 + 0.35 * s) + v * 0.05 + nrm * 0.3
        PK.plate(mb, [(0.0, -0.1), (1.5, -0.08), (1.5, 0.08), (0.0, 0.1)], o2, dd, nrm.cross(dd), 0.2, "Wood_Light")
    for k in range(3):
        x0 = -0.7 + 0.7 * k
        pts = [(x0 + 0.12 * math.sin(t * 3.0), 0.3 + t * 0.9) for t in (0.0, 0.33, 0.66, 1.0)]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            mb.beam(bo + u * xa + v * ya + nrm * 0.2, bo + u * xb + v * yb + nrm * 0.2, 0.14, 0.14, "Emblem_Cream",
                    0.0)
    # balcao do cliente (fundo livre de 6+ na frente) + banquinhos
    cy0, cy1 = 0.6, 2.0
    mb.box((15.6, cy1 - cy0, 3.1), F.p(0, (cy0 + cy1) / 2, zf + 1.55), F.r(), "Wood_Dark", 0.04)
    for k in range(8):
        mb.box((1.7, 0.2, 2.5), F.p(-6.85 + 1.96 * k, cy0 - 0.1, zf + 1.4), F.r(), "Wood_Plank", 0.0)
    mb.box((16.2, 1.9, 0.32), F.p(0, (cy0 + cy1) / 2 - 0.25, zf + 3.26), F.r(), "Wood_Light", 0.0)
    for k in range(6):
        x = -6.25 + 2.5 * k
        mb.cyl(0.26, 1.9, F.p(x, -1.1, zf + 0.95), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
        mb.cyl(0.72, 0.34, F.p(x, -1.1, zf + 2.05), (0, 0, 0), "Wood_Lacquer_Red", 10, bevel=0.0)
        mb.cyl(0.55, 0.12, F.p(x, -1.1, zf + 0.1), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
    ztop = zf + 3.42
    for x in (-5.0, 0.2, 4.9):
        b = F.p(x, 0.8, ztop)
        K.lathe(mb, b, [(0.25, 0.0), (0.42, 0.0), (0.66, 0.5), (0.58, 0.5), (0.25, 0.1)], "Emblem_Cream", 10)
        K.lathe(mb, b, [(0.5, 0.2), (0.72, 0.2), (0.76, 0.34), (0.56, 0.34)], red, 10)
        mb.cyl(0.55, 0.06, b + Vector((0, 0, 0.42)), (0, 0, 0), "Wood_Light", 10, bevel=0.0)
        for s in (-1, 1):
            mb.rod(b + Vector((0.15 * s, -0.3, 0.55)), b + Vector((0.3 + 0.15 * s, 0.6, 1.3)), 0.07, "Wood_Light", 4)
    mb.cyl(0.3, 0.8, F.p(-2.6, 1.2, ztop + 0.4), (0, 0, 0), "Wood_Lacquer_Red", 8, bevel=0.0)
    # cozinha: fogao de pedra com fogo (Lantern_Glow, 0,3 de espessura), 2 panelas, bancada com tigelas,
    # prateleiras, coifa e chamine (atravessa a agua de tras)
    by0, by1 = 4.2, 5.6
    mb.box((6.2, by1 - by0, 2.9), F.p(-5.1, (by0 + by1) / 2, zf + 1.45), F.r(), "Stone_Wall_Dark", 0.04)
    for x in (-6.4, -3.8):
        mb.box((1.3, 0.3, 0.8), F.p(x, by0 - 0.05, zf + 1.1), F.r(), "Lantern_Glow", 0.0)
        mb.cyl(1.05, 1.7, F.p(x, (by0 + by1) / 2, zf + 2.9 + 0.85), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
        mb.cyl(1.12, 0.2, F.p(x, (by0 + by1) / 2, zf + 2.9 + 1.8), (0, 0, 0), "Wood_Dark", 10, bevel=0.0)
        mb.cyl(0.2, 0.3, F.p(x, (by0 + by1) / 2, zf + 2.9 + 2.05), (0, 0, 0), "Wood_Dark", 6, bevel=0.0)
    mb.box((10.2, by1 - by0, 2.9), F.p(3.2, (by0 + by1) / 2, zf + 1.45), F.r(), "Wood_Dark", 0.04)
    mb.box((10.4, by1 - by0 + 0.2, 0.25), F.p(3.2, (by0 + by1) / 2, zf + 3.0), F.r(), "Wood_Light", 0.0)
    for x in (0.2, 1.6, 3.0):
        for k in range(3):
            mb.cyl(0.55, 0.3, F.p(x, 4.9, zf + 3.28 + 0.3 * k), (0, 0, 0), "Emblem_Cream", 8, r2=0.42, bevel=0.0)
    mb.box((2.0, 1.1, 0.2), F.p(6.3, 4.9, zf + 3.23), F.r(0, 0, 0.1), "Wood_Plank", 0.0)
    mb.box((1.3, 0.3, 0.12), F.p(6.3, 4.8, zf + 3.39), F.r(0, 0, 0.1), "Metal_Dark", 0.0)
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
    mb.cyl(0.55, 6.7, F.p(-5.1, 5.2, 13.65), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
    mb.cyl(0.85, 0.5, F.p(-5.1, 5.2, 17.05), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
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
    light("L_Village_Ramen", "POINT", F.p(0.0, 2.5, 10.2), 1100, (1.0, 0.7, 0.42), 0.6)
    mk("NPC_Ramen", F.p(0, 3.1, zf), (0, 0, F.a + math.pi), 2.0, "ARROWS", props={"floor": T1 + zf})
    mk("PLAYER_INTERACT_Ramen", F.p(0, RAMEN_IY, zf), (0, 0, F.a), 2.0, "SPHERE", props={"floor": T1 + zf})


# ================================================================== ESTANDARTES (os 2 unicos da vila)
# rodada 2: em x +-8,5 eles cobriam a porta do salao no eixo -> x +-11,5 e 11 de altura total (pano de 7)
BANNER_X, BANNER_Y = 11.5, 99.0
BANNER = dict(h_total=11.0, cloth=7.0, tip=1.1, w=3.2, top=9.3, pole_dy=0.5)


def banners():
    rng = random.Random(4501)
    mb = VMB("VIL_Banners", COLL, rng, detail="near", vcap=1)
    B = BANNER
    hw = B["w"] / 2
    for s in (-1, 1):
        x, y, z = s * BANNER_X, BANNER_Y, T1
        yp = y + B["pole_dy"]                     # mastro atras do pano
        # base de pedra + mastro + anel e ponta dourados (topo da ponta = 11)
        mb.box((1.9, 1.9, 1.1), (x, yp, z + 0.35), (0, 0, 0), "Stone_Wall_Light", 0.05)
        mb.box((1.3, 1.3, 0.5), (x, yp, z + 1.1), (0, 0, 0), "Stone_Wall_Light", 0.0)
        mb.cyl(0.28, 8.9, (x, yp, z + 1.3 + 4.45), (0, 0, 0), "Wood_Dark", 8, bevel=0.0)
        mb.cyl(0.45, 0.4, (x, yp, z + 10.1), (0, 0, 0), "Metal_Gold", 8, bevel=0.0)
        mb.cyl(0.3, B["h_total"] - 10.3, (x, yp, z + (10.3 + B["h_total"]) / 2), (0, 0, 0), "Metal_Gold", 6, r2=0.02,
               bevel=0.0)
        # travessa no alto (atras do pano) com pontas douradas
        zt = z + B["top"]
        mb.beam((x - hw - 0.5, yp - 0.2, zt), (x + hw + 0.5, yp - 0.2, zt), 0.5, 0.4, "Wood_Dark", 0.0)
        for k in (-1, 1):
            mb.box((0.55, 0.75, 0.75), (x + k * (hw + 0.7), yp - 0.2, zt), (0, 0, 0), "Metal_Gold", 0.0)
        # pano (espessura 0,2) com ponta em V; frisos dourados com 0,12 de folga de cada face (sem z-fighting)
        h = B["cloth"] - B["tip"]
        pts = [(-hw, 0.0), (hw, 0.0), (hw, -h), (0.0, -B["cloth"]), (-hw, -h)]
        PK.plate(mb, pts, Vector((x, y, zt)), (1, 0, 0), (0, 0, 1), 0.2, "Cloth_Red")
        mb.box((B["w"] + 0.2, 0.44, 0.45), (x, y, zt - 0.1), (0, 0, 0), "Metal_Gold", 0.0)
        for k in (-1, 1):
            mb.box((0.5, 0.44, h - 0.5), (x + k * (hw - 0.1), y, zt - 0.3 - (h - 0.5) / 2), (0, 0, 0), "Metal_Gold",
                   0.0)
        mb.box((B["w"] - 0.9, 0.2, 0.3), (x, y - 0.2, zt - 1.1), (0, 0, 0), "Emblem_Cream", 0.0)
        # folha em relevo (0,25 a frente do pano)
        K.leaf_symbol(mb, Vector((x, y - 0.24, zt - 0.3 - h * 0.5)), (1, 0, 0), (0, 0, 1), 1.3, "Emblem_Cream",
                      th=0.2, w=0.18)
    mb.finish()
    for s in (-1, 1):
        col_box("VillageBanners", (1.9, 1.9, B["h_total"]), (s * BANNER_X, BANNER_Y + B["pole_dy"],
                                                              T1 + B["h_total"] / 2))
        col_box("VillageBanners", (B["w"], 0.6, B["cloth"]), (s * BANNER_X, BANNER_Y,
                                                             T1 + B["top"] - B["cloth"] / 2))


def build():
    main_hall()
    weapon_shop()
    water_tower()
    ramen()
    banners()
