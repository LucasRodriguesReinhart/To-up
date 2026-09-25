# db_capsule - ZONA CAPSULE (marco heroi) da Ilha 2 (Dragon Ball): o predio-cupula estilo Capsule no terraco CAP
# (34,2), ENTRAVEL, com os 2 anexos (nao entraveis), o terraco (calcamento, desenho de piso, muros de arrimo, guarda-
# corpos) e a escadaria grande HUB -> CAP com lanternas. Planta: db_layout (CAPSULE_*, CAP_POLY, CAP_STAIR).
#   exterior: soco + tambor ALTO (14,85: escotilhas, pilastras, faixa azul, cornija) -> cupula eliptica com nervuras e
#             paralelo -> clerestorio de vidro azul com montantes -> capa azul com faixa branca -> colar + antena (radar)
#             emblema EMBUTIDO (borda azul-marinho + disco azul + anel C branco, SEM texto) que acompanha a curvatura
#             da cupula, acima da cobertura do pavilhao: visivel inteiro do pe da escadaria
#   entrada : pavilhao de laje azul baixa (topo Z + 15,1; porta 10 x 12 ABERTA, bandeira ambar, pilares azul-marinho
#             com lanterna na frente da testeira)
#   interior: FOYER (10 x 20, forro plano 14,2, paineis dourados) -> CORREDOR (10 x 8, pe-direito 14) -> SALAO (r 21, pe-direito
#             18 na parede, 30 no oculo): piso desenhado, anel de 8 colunas esbeltas com viga-anel de luz, balcao de
#             recepcao (NPC_Capsule), plataforma do holograma (VFX), paineis com faixas de luz, nicho O com o pedestal
#             das 7 esferas (UNICO acento Dragon Ball do interior), nicho L com tela, cupula interna com nervuras.
#   anexos  : tambor branco + faixa de vidro + cupula azul; SEM porta; porta redonda de passarela (z = CAP + 10)
#             virada para a torre (O -> comunicacao, L -> mirante); elo baixo envidracado ate a cupula
# Colisao: so dos volumes proprios (DB_Cap*): casca, salao, nichos, foyer, corredor, pilares, colunas, balcao, pedestal,
# plataforma, anexos, elos, pilares da escada. O piso do terraco, a rampa da escada e as guardas sao do db_col.
import math, random
from mathutils import Vector
import db_lib as DL
from db_lib import col_box, col_box2, mk, light, octo_col, Frame
import db_layout as L
import db_col
import fm_lib
import db_capsule_kit as K

S_ = fm_lib.S
# ------------------------------------------------------------------ materiais novos (3 de 7)
NEW_MATS = {
    "Plaster_DBCapRib": (S_(206, 214, 228), 0.55, 0.0, 0, None, 0.0),     # nervuras / linhas de painel da cupula
    "Plaster_DBCapWall": (S_(212, 224, 242), 0.6, 0.0, 0, None, 0.0),     # paineis internos azul-gelo
    "Stone_DBCapFloor": (S_(222, 226, 232), 0.35, 0.0, 0, None, 0.0),     # piso polido do interior
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

COLL = "04_CAPSULE_LANDMARK"
VFXC = "12_VFX_HELPERS"
Z = L.CAP
H = L.HUB
CX, CY = L.CAPSULE_C
R = L.CAPSULE_R                     # 29: raio externo do tambor
HR = L.CAPSULE_HALL_R               # 21: raio do salao
C2 = (CX, CY)
ZD = 2.5                            # tambor mais alto que o do blockout (concept: tambor alto, cupula acima do portico)
ZS = Z + 12.0 + ZD                  # arranque da cupula (topo do tambor): a base da cupula sai acima do pavilhao
DA, DBV = 29.0, 25.0                # semi-eixos da cupula externa
PH_CL = 60.0                        # latitude da base do clerestorio
E_OUT = K.Ell(CX, CY, ZS, DA, DBV)
# emblema embutido (acompanha a curvatura): centro em (EMB_TH, EMB_PH); raios da borda azul-marinho, do disco azul e
# do anel C. Visivel inteiro do pe da escadaria (a cobertura do pavilhao fica abaixo da linha de visada).
EMB_TH, EMB_PH = 270.0, 28.0
EMB_R = (6.1, 5.5, 2.55, 4.35)
ZI = Z + 18.0                       # arranque da cupula interna (topo da parede do salao)
IA, IB = HR, 12.0
PH_O = math.degrees(math.acos(4.6 / IA))    # oculo da cupula interna (r 4,6)
E_IN = K.Ell(CX, CY, ZI, IA, IB)
PAV_GAP = 21.5                      # meia abertura (graus) do tambor atras do pavilhao
D2R = math.pi / 180.0

WHITE, NAVY, BLUE, GLASS = "Plaster_DB_White", "Plaster_DB_Navy", "Roof_DB_Blue", "Glass_DB_Blue"
RIB, WALL, FLOOR = "Plaster_DBCapRib", "Plaster_DBCapWall", "Stone_DBCapFloor"
CYAN, STEEL, WARM, LAMP, GOLD = "DB_Cyan_Glow", "Metal_DB_Steel", "Window_Warm", "Lantern_Glow", "Metal_Gold"
PAVE, BLOCK, BLOCK_B = "Stone_Paving_DB", "Stone_DB_Block", "Stone_DB_Block_B"
BALL, STAR = "DB_Ball_Glow", "DB_Star_Red"

X0, Y0, X1, Y1 = L.CAPSULE_FOYER    # -10, 135, 10, 145
DW = L.CAPSULE_DOOR_W / 2.0         # 5
DH = L.CAPSULE_DOOR_H               # 12
WT = 1.2                            # espessura das paredes do pavilhao
YB = 148.2                          # fundo do pavilhao (enterrado no tambor)
HW = 14.2                           # altura das paredes do pavilhao = forro plano do foyer (pe-direito 14,2)
ROOF_Y0 = Y0 + 0.35                 # cobertura recuada da fachada (as lanternas dos pilares ficam na frente dela)
ROOF_EAVE, ROOF_CROWN = 0.45, 0.9   # cobertura: laje com lombada suave (topo Z + 15,1)
CW = L.CAPSULE_CORRIDOR[2]          # 5: meia largura do corredor
CY0, CY1 = L.CAPSULE_CORRIDOR[1], CY - math.sqrt(HR * HR - CW * CW)   # 145 .. 153,6 (face do salao)
BALLS_C = (CX - 22.2, CY)           # pedestal das esferas (nicho oeste)
NICHE_W = 4.5                       # meia largura dos nichos
NICHE_B = 25.0                      # fundo dos nichos (raio)

# ------------------------------------------------------------------ cameras de revisao (360 + jogador + interior)
CAMS = {
    "CAM_DBCap_Front": ((0.0, 62.0, H + 26.0), (0.0, 172.0, Z + 17.0), 24),
    "CAM_DBCap_Back": ((30.0, 246.0, Z + 58.0), (0.0, 174.0, Z + 14.0), 24),
    "CAM_DBCap_Left": ((-108.0, 128.0, Z + 22.0), (-6.0, 172.0, Z + 14.0), 24),
    "CAM_DBCap_Right": ((108.0, 118.0, Z + 22.0), (6.0, 172.0, Z + 14.0), 24),
    "CAM_DBCap_Aerial": ((-74.0, 84.0, Z + 72.0), (0.0, 170.0, Z + 10.0), 24),
    "CAM_DBCap_PlayerStair": ((-5.0, 104.0, H + 5.2), (0.0, 150.0, Z + 15.0), 22),
    "CAM_DBCap_PlayerDoor": ((-3.0, 129.5, H + 5.25 + 5.2), (0.0, 142.0, Z + 7.5), 22),
    "CAM_DBCap_PlayerForecourt": ((-30.0, 137.0, Z + 5.2), (0.0, 138.0, Z + 8.0), 22),
    "CAM_DBCap_HallA": ((0.0, 157.0, Z + 5.2), (0.0, 187.0, Z + 7.0), 20),
    "CAM_DBCap_HallB": ((12.0, 186.0, Z + 6.5), (-20.0, 170.0, Z + 5.0), 18),
    "CAM_DBCap_HallUp": ((0.0, 157.0, Z + 3.5), (0.0, 177.0, Z + 25.0), 16),
}

# ------------------------------------------------------------------ rotas e sondas extras (db_qa)
_HALL_ARC = [(CX + 17.5 * math.cos(a * D2R), CY + 17.5 * math.sin(a * D2R)) for a in range(250, -71, -10)]
EXTRA_ROUTES = {
    "CAP_ESCADA->PORTA->FOYER->CORREDOR->SALAO->INTERACAO": (
        [(0.0, 110.0), (0.0, 117.0), (0.0, 125.0), (0.0, 133.0), (0.0, 135.6), (0.0, 139.0), (0.0, 144.0),
         (0.0, 149.0), (0.0, 153.0), (0.0, 158.0), (0.0, 166.0), (0.0, 174.0), (CX, CY + 6.0)], H),
    "CAP_TERRACO_O->PORTA": ([(-44.0, 146.0), (-24.0, 138.0), (-13.5, 134.2), (-10.6, 133.8), (-8.6, 133.0),
                             (-7.0, 132.85), (-4.0, 132.9), (-2.0, 133.8), (0.0, 136.0), (0.0, 140.0)], Z),
    "CAP_TERRACO_L->PORTA": ([(44.0, 146.0), (24.0, 138.0), (13.5, 134.2), (10.6, 133.8), (8.6, 133.0),
                             (7.0, 132.85), (4.0, 132.9), (2.0, 133.8), (0.0, 136.0), (0.0, 140.0)], Z),
    "CAP_SALAO->ESFERAS": ([(0.0, 156.0), (-6.0, 157.6), (-11.3, 160.6), (-15.2, 165.2), (-17.2, 171.0),
                            (-18.0, 174.0)], Z),
    "CAP_SALAO->TELA": ([(0.0, 156.0), (6.0, 157.6), (11.3, 160.6), (15.2, 165.2), (17.2, 171.0), (21.5, 174.0)], Z),
    "CAP_SALAO_DEAMBULATORIO": ([(0.0, 156.0)] + _HALL_ARC + [(0.0, 156.0)], Z),
    "CAP_TERRACO_LATERAIS": ([(-40.0, 142.0), (-56.0, 152.0), (-64.0, 160.0)], Z),
}
EXTRA_PROBES = [
    ("CAP_FOYER_parede_O", -6.0, 140.0, Z, -1.0, 0.0, 4.5),
    ("CAP_FOYER_parede_L", 6.0, 140.0, Z, 1.0, 0.0, 4.5),
    ("CAP_CORREDOR_O", -3.0, 149.0, Z, -1.0, 0.0, 3.5),
    ("CAP_SALAO_fundo", CX, CY + 18.0, Z, 0.0, 1.0, 4.5),
    ("CAP_NICHO_tela_fundo", CX + 22.0, CY, Z, 1.0, 0.0, 4.0),
    ("CAP_TERRACO_fundo", 20.0, 202.0, Z, 0.0, 1.0, 6.0),
    ("CAP_TERRACO_frente_O", -40.0, 134.0, Z, 0.0, -1.0, 4.0),
]


def adist(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def _links():
    """elos baixos entre a cupula e cada anexo (centro, rumo, comprimento)"""
    out = []
    for ax, ay, ar in L.CAPSULE_ANNEX:
        dx, dy = ax - CX, ay - CY
        dist = math.hypot(dx, dy)
        ux, uy = dx / dist, dy / dist
        r0, r1 = R - 2.0, dist - ar + 1.5
        cm = (r0 + r1) / 2.0
        out.append(dict(c=(CX + ux * cm, CY + uy * cm), ang=math.atan2(uy, ux), L=r1 - r0, W=8.0,
                        th=math.degrees(math.atan2(uy, ux))))
    return out


LINKS = _links()
LINK_TH = [lk["th"] for lk in LINKS]


# ------------------------------------------------------------------ pecas pequenas
def lamp_head(mb, p, s=1.0):
    """cabeca de lanterna Capsule: base azul-marinho, vidro ambar, montantes, chapeu azul em piramide, remate dourado"""
    x, y, z = p
    mb.box((1.5 * s, 1.5 * s, 0.25), (x, y, z + 0.125), (0, 0, 0), NAVY, 0.0)
    zc = z + 0.25 + 0.7 * s
    mb.box((1.15 * s, 1.15 * s, 1.4 * s), (x, y, zc), (0, 0, 0), LAMP, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.24, 0.24, 1.5 * s), (x + sx * 0.62 * s, y + sy * 0.62 * s, zc), (0, 0, 0), NAVY, 0.0)
    zt = z + 0.25 + 1.4 * s
    mb.cyl(1.1 * s, 0.7 * s, (x, y, zt + 0.35 * s), (0, 0, math.pi / 4), BLUE, 4, r2=0.2 * s, bevel=0.0)
    K.sphere(mb, (x, y, zt + 0.7 * s + 0.24), 0.28, GOLD, sub=1)
    return zt + 0.7 * s + 0.52


def offset_poly(poly, d):
    """contorno convexo anti-horario deslocado d para fora (esquadria nos cantos)"""
    n = len(poly)
    out = []
    for i in range(n):
        p0, p1, p2 = Vector((*poly[i - 1], 0)), Vector((*poly[i], 0)), Vector((*poly[(i + 1) % n], 0))
        e0, e1 = (p1 - p0).normalized(), (p2 - p1).normalized()
        n0, n1 = Vector((e0.y, -e0.x, 0)), Vector((e1.y, -e1.x, 0))
        m = (n0 + n1) * (d / (1.0 + n0.dot(n1)))
        out.append((p1.x + m.x, p1.y + m.y))
    return out


# ------------------------------------------------------------------ exterior da cupula principal
def build_dome():
    mb = K.CMB("DB_Cap_Dome", COLL)
    # tambor (aberto atras do pavilhao): soco, rodape, parede lisa, faixa azul, friso, cornija
    zb0 = Z + 9.4 + ZD                  # faixa azul no alto do tambor (continua na frente do pavilhao)
    drum = [(28.4, Z - 0.3), (30.3, Z - 0.3), (30.3, Z + 0.9), (29.35, Z + 0.9), (29.35, Z + 1.6), (R, Z + 1.6),
            (R, zb0), (R + 0.3, zb0), (R + 0.3, zb0 + 1.4), (R, zb0 + 1.4), (R, zb0 + 1.9), (29.75, zb0 + 1.9),
            (29.75, zb0 + 2.45), (R, zb0 + 2.95), (28.4, zb0 + 2.95)]
    dmats = [BLOCK, BLOCK, BLOCK, NAVY, NAVY, WHITE, BLUE, BLUE, BLUE, WHITE, NAVY, NAVY, NAVY, NAVY, WHITE]
    for s0, s1 in K.spans([(270.0, PAV_GAP)]):
        K.lathe(mb, C2, drum, WHITE, K.seg_n(s0, s1, 64), s0, s1, smooth=[5, 7, 9], mats=dmats)
    # escotilhas redondas e pilastras claras no tambor (fora do pavilhao e dos elos)
    zw = (Z + 1.6 + zb0) / 2.0
    for i in range(24):
        th = 7.5 + 15.0 * i
        if adist(th, 270.0) < 27.0 or min(adist(th, t) for t in LINK_TH) < 13.0:
            continue
        K.porthole(mb, CX, CY, R, th, zw, 1.9, n=12)
    for i in range(24):
        th = 15.0 * i
        if adist(th, 270.0) < 24.0 or min(adist(th, t) for t in LINK_TH) < 10.0:
            continue
        t = th * D2R
        mb.box((0.6, 0.9, zb0 - Z - 1.6), (CX + (R + 0.05) * math.cos(t), CY + (R + 0.05) * math.sin(t), zw), (0, 0, t),
               RIB, 0.0)
    # cupula: casca eliptica lisa + nervuras (meridianos) + 2 paralelos
    prof, sm = K.shell_prof(DA, DBV, ZS, 0.0, PH_CL, 12, 0.6)
    K.lathe(mb, C2, prof, WHITE, 64, smooth=sm)
    for i in range(12):
        K.rib_meridian(mb, E_OUT, 15.0 + 30.0 * i, 0.5, PH_CL - 0.5, 10, 0.6, 0.24, 0.3, RIB)
    # paralelo baixo: passa POR TRAS do emblema (a placa cobre a faixa) e deixa branco limpo ate o clerestorio
    K.rib_parallel(mb, E_OUT, EMB_PH - 4.0, 0.0, 360.0, 64, 0.5, 0.2, 0.3, RIB)
    # clerestorio (faixa de vidro azul perto do topo) + peitoril + montantes + aba
    rc = DA * math.cos(PH_CL * D2R)
    zc = ZS + DBV * math.sin(PH_CL * D2R)
    K.ring(mb, C2, rc - 0.9, rc + 0.55, zc - 0.5, zc + 0.05, NAVY, 48)
    K.lathe(mb, C2, [(rc - 0.5, zc), (rc + 0.05, zc), (rc - 0.55, zc + 2.8), (rc - 1.1, zc + 2.8)], GLASS, 48,
            smooth=[1])
    # fundo opaco atras do vidro (no Roblox o Glass tem 35% de transparencia: mostra fundo escuro, nao o oco)
    K.ring(mb, C2, rc - 1.65, rc - 1.4, zc - 0.4, zc + 2.95, NAVY, 32)
    for i in range(24):
        t = (7.5 + 15.0 * i) * D2R
        a = (CX + (rc + 0.15) * math.cos(t), CY + (rc + 0.15) * math.sin(t), zc + 0.05)
        b = (CX + (rc - 0.45) * math.cos(t), CY + (rc - 0.45) * math.sin(t), zc + 2.75)
        mb.beam(a, b, 0.45, 0.45, NAVY, 0.0)
    zl = zc + 2.8
    K.ring(mb, C2, rc - 1.6, rc + 0.9, zl, zl + 0.7, NAVY, 48)
    # capa azul (com faixa branca) + colar + antena
    ca, cb = rc + 0.35, 7.5
    ph_t = math.degrees(math.acos(2.0 / ca))
    prof, sm = K.shell_prof(ca, cb, zl + 0.7, 0.0, ph_t, 8, 0.5, k_hidden=3)
    K.lathe(mb, C2, prof, BLUE, 48, smooth=sm)
    E_CAP = K.Ell(CX, CY, zl + 0.7, ca, cb)
    K.rib_parallel(mb, E_CAP, 34.0, 0.0, 360.0, 48, 0.9, 0.22, 0.3, WHITE)
    z_top = zl + 0.7 + cb * math.sin(ph_t * D2R)
    mb.cyl(2.4, 1.4, (CX, CY, z_top + 0.3), (0, 0, 0), STEEL, 16, bevel=0.0)
    mb.cyl(0.32, 7.4, (CX, CY, z_top + 4.7), (0, 0, 0), STEEL, 8, bevel=0.0)
    mb.box((3.2, 0.32, 0.32), (CX, CY, z_top + 6.2), (0, 0, 0), STEEL, 0.0)
    mb.box((0.32, 2.2, 0.32), (CX, CY, z_top + 7.0), (0, 0, 0), STEEL, 0.0)
    K.sphere(mb, (CX, CY, z_top + 8.8), 0.6, CYAN, sub=1)
    emblem(mb)
    ob = mb.finish()
    # radar pequeno que gira no mastro (peca movel)
    rz = z_top + 3.4
    vr = K.CMB("VFX_DBCAP_Radar", VFXC)
    vr.box((2.4, 0.35, 0.35), (CX + 1.2, CY, rz), (0, 0, 0), STEEL, 0.0)
    K.cyl_axis(vr, 1.6, 0.45, Vector((CX + 2.6, CY, rz + 0.35)), Vector((1.0, 0.0, 0.55)), WHITE, 16)
    K.cyl_axis(vr, 0.35, 1.2, Vector((CX + 2.3, CY, rz + 0.2)), Vector((1.0, 0.0, 0.55)), STEEL, 8)
    vo = vr.finish()
    vo["pivot"] = (CX, CY, rz)
    vo["axis"] = (0.0, 0.0, 1.0)
    vo["rpm"] = 6.0
    return ob, z_top


def emblem(mb):
    """emblema EMBUTIDO na frente da cupula (sem texto): borda azul-marinho + disco azul + anel C branco, as 3 placas
    acompanhando a curvatura da casca (relevo maximo 0,8: 0,36 / 0,58 / 0,8), sem 'lata' saliente. O C abre para a
    direita de quem olha (U = +x)."""
    rn, rb, c0, c1 = EMB_R
    K.dome_patch(mb, E_OUT, EMB_TH, EMB_PH, [0.0, 1.8, 3.4, 4.8, rn], -0.6, 0.36, NAVY, n=48)
    K.dome_patch(mb, E_OUT, EMB_TH, EMB_PH, [0.0, 2.0, 3.8, rb], 0.0, 0.58, BLUE, n=48)
    K.dome_patch(mb, E_OUT, EMB_TH, EMB_PH, [c0, (c0 + c1) / 2.0, c1], 0.4, 0.8, WHITE, 42.0, 318.0, n=36)


# ------------------------------------------------------------------ pavilhao de entrada, foyer e corredor
def build_entrance():
    mb = K.CMB("DB_Cap_Entrance", COLL, detail="near")
    F = Frame(0.0, 0.0, Z, 0.0)
    # paredes do pavilhao (vao da porta 10 x 12 na frente)
    mb.box2((X0, Y0, Z), (-DW, Y0 + WT, Z + HW), WHITE, 0.0)
    mb.box2((DW, Y0, Z), (X1, Y0 + WT, Z + HW), WHITE, 0.0)
    mb.box2((-DW, Y0, Z + DH), (DW, Y0 + WT, Z + HW), WHITE, 0.0)
    mb.box2((X0, Y0, Z), (X0 + WT, YB, Z + HW), WHITE, 0.0)
    mb.box2((X1 - WT, Y0, Z), (X1, YB, Z + HW), WHITE, 0.0)
    # fundo do foyer (dos lados do corredor) + verga da passagem para o corredor
    mb.box2((X0 + WT, Y1, Z), (-CW - WT, Y1 + WT, Z + HW), WHITE, 0.0)
    mb.box2((CW + WT, Y1, Z), (X1 - WT, Y1 + WT, Z + HW), WHITE, 0.0)
    mb.box2((-CW - WT, Y1, Z + DH), (CW + WT, Y1 + WT, Z + HW), WHITE, 0.0)
    # cobertura: laje azul com lombada suave e testeira azul-marinho, recuada 0,35 da fachada (topo Z + 15,1: fica
    # abaixo da linha de visada do pe da escadaria ate o emblema da cupula). Forro plano do foyer em Z + HW.
    k = 16
    RW = X1 + 0.6
    roof = [(RW * math.cos(math.pi - math.pi * i / k), HW + ROOF_EAVE + (ROOF_CROWN - ROOF_EAVE) *
             math.sin(math.pi - math.pi * i / k)) for i in range(k + 1)] + [(RW, HW), (-RW, HW)]
    K.extrude_uz(mb, roof, F, ROOF_Y0, YB, BLUE, cap_m=NAVY)
    # pilares azul-marinho com lanterna (ladeiam a porta)
    for s in (-1, 1):
        px = s * 6.7
        mb.box((2.8, 1.9, 1.2), (px, 134.65, Z + 0.6), (0, 0, 0), WHITE, 0.1)
        mb.box((2.2, 1.3, 11.0), (px, 134.65, Z + 6.7), (0, 0, 0), NAVY, 0.1)
        mb.box((2.8, 1.9, 0.8), (px, 134.65, Z + 12.6), (0, 0, 0), WHITE, 0.1)
        mb.box((0.2, 1.34, 8.0), (px, 134.65, Z + 6.7), (0, 0, 0), CYAN, 0.0)
        lamp_head(mb, (px, 134.65, Z + 13.0), 0.85)
    # moldura da porta: umbrais + arco azul-marinho, bandeira ambar (frente e verso), travessa e raios
    yf = Y0 - 0.35
    for s in (-1, 1):
        mb.box2((s * DW, yf, Z), (s * (DW + 1.2), Y0 + 0.05, Z + DH), NAVY, 0.0)
    # arco abatido (cabe sob o forro): a bandeira brilha em ambar (Lantern_Glow = Neon no Roblox), frente e verso
    ra, rf = HW - DH - 0.15, HW - DH - 0.65
    arch = K.semi_ell(6.2, ra, DH, 14) + K.semi_ell(5.0, rf, DH, 14, rev=True)
    K.extrude_uz(mb, arch, F, yf, Y0 + 0.05, NAVY)
    fan = K.semi_ell(5.0, rf, DH, 14)
    K.extrude_uz(mb, fan, F, Y0 - 0.15, Y0 + 0.02, LAMP)
    K.extrude_uz(mb, fan, F, Y0 + WT - 0.02, Y0 + WT + 0.15, LAMP)
    mb.box2((-DW, yf + 0.05, Z + DH - 0.25), (DW, Y0, Z + DH + 0.25), NAVY, 0.0)
    for a in (45.0, 90.0, 135.0):
        t = a * D2R
        mb.beam((0.0, Y0 - 0.25, Z + DH + 0.2), (4.9 * math.cos(t), Y0 - 0.25, Z + DH + (rf - 0.1) * math.sin(t)), 0.3,
                0.3, NAVY, 0.0)
    # rodape azul-marinho e faixa azul (continua a faixa do tambor, que subiu ZD) por fora
    zb0 = Z + 9.4 + ZD
    for s in (-1, 1):
        mb.box2((s * (DW + 1.2), Y0 - 0.15, Z), (s * X1, Y0 + 0.1, Z + 1.0), NAVY, 0.0)
        mb.box2((s * (DW + 1.2), Y0 - 0.2, zb0), (s * (X1 + 0.2), Y0 + 0.1, zb0 + 1.4), BLUE, 0.0)
        mb.box2((s * (X1 - 0.1), Y0 - 0.15, Z), (s * (X1 + 0.15), YB - 0.8, Z + 1.0), NAVY, 0.0)
        mb.box2((s * (X1 - 0.1), Y0 - 0.2, zb0), (s * (X1 + 0.2), YB - 0.6, zb0 + 1.4), BLUE, 0.0)
        # escotilha na lateral (por fora e por dentro)
        K.porthole(mb, 0.0, 141.4, X1, 0.0 if s > 0 else 180.0, Z + 6.8, 1.7)
        K.porthole(mb, 0.0, 141.4, -(X1 - WT), 180.0 if s > 0 else 0.0, Z + 6.8, 1.7, proud=0.2)
    # ---- foyer (interior)
    mb.box2((X0 + WT, Y0, Z - 0.1), (X1 - WT, Y1, Z + 0.08), FLOOR, 0.0)
    mb.box2((-DW, Y0 - 0.25, Z - 0.1), (DW, Y0 + WT, Z + 0.11), NAVY, 0.0)       # soleira
    K.ring(mb, (0.0, 140.6), 2.8, 3.5, Z + 0.04, Z + 0.11, BLUE, 32)
    for s in (-1, 1):
        mb.box2((s * (X1 - WT - 0.2), Y0 + WT, Z), (s * (X1 - WT), Y1, Z + 0.9), NAVY, 0.0)
        mb.box2((s * DW, Y0 + WT, Z), (s * (X1 - WT), Y0 + WT + 0.2, Z + 0.9), NAVY, 0.0)
        # paineis e frisos dourados (Metal_Gold: dourado no Roblox sem virar Neon; a luz quente vem da PointLight)
        mb.box2((s * (X1 - WT - 0.15), Y0 + WT, Z + 10.2), (s * (X1 - WT), Y1, Z + 10.5), GOLD, 0.0)
        mb.box2((s * (CW + WT), Y1 - 0.15, Z + 10.2), (s * (X1 - WT), Y1, Z + 10.5), GOLD, 0.0)
        mb.box2((s * (CW + WT + 0.25), Y1 - 0.12, Z + 1.2), (s * (X1 - WT - 0.25), Y1, Z + 9.8), GOLD, 0.0)
        mb.box2((s * (CW + WT + 0.1), Y1 - 0.18, Z + 0.9), (s * (X1 - WT - 0.1), Y1, Z + 1.2), NAVY, 0.0)
    # forro: faixa de luz ambar no eixo + anel azul-marinho sobre o anel do piso (nada abaixo de Z + 14)
    mb.box2((-0.6, Y0 + 1.6, Z + HW - 0.15), (0.6, Y1 - 0.6, Z + HW), LAMP, 0.0)
    K.ring(mb, (0.0, 140.6), 3.1, 3.8, Z + HW - 0.2, Z + HW, NAVY, 32)
    # moldura da passagem foyer -> corredor
    for s in (-1, 1):
        mb.box2((s * (CW - 0.1), Y1 - 0.3, Z), (s * (CW + 1.0), Y1 + 0.2, Z + DH), NAVY, 0.0)
        mb.box2((s * (CW - 0.15), Y1 - 0.4, Z + 0.9), (s * (CW + 0.25), Y1 - 0.25, Z + DH - 0.4), GOLD, 0.0)
    mb.box2((-CW - 1.0, Y1 - 0.3, Z + DH), (CW + 1.0, Y1 + 0.2, Z + DH + 0.9), NAVY, 0.0)
    mb.box2((-CW + 0.2, Y1 - 0.4, Z + DH - 0.4), (CW - 0.2, Y1 - 0.25, Z + DH - 0.05), GOLD, 0.0)
    # ---- corredor (dentro da casca do tambor)
    for s in (-1, 1):
        mb.box2((s * CW, CY0, Z), (s * (CW + WT), CY1, Z + 14.6), WHITE, 0.0)
        mb.box2((s * (CW - 0.12), CY0 + 0.3, Z + 0.9), (s * CW, CY1 - 0.4, Z + 12.8), WALL, 0.0)
        mb.box2((s * (CW - 0.18), CY0, Z), (s * CW, CY1, Z + 0.9), NAVY, 0.0)
        for yy in (147.6, 151.2):
            mb.box2((s * (CW - 0.22), yy - 0.12, Z + 1.6), (s * (CW - 0.1), yy + 0.12, Z + 11.6), BLUE, 0.0)
        mb.box2((s * (CW - 0.9), CY0, Z + 0.05), (s * CW, CY1, Z + 0.12), NAVY, 0.0)
    mb.box2((-CW - WT, CY0, Z + 14.0), (CW + WT, CY1, Z + 14.6), WHITE, 0.0)
    mb.box2((-0.45, CY0 + 0.6, Z + 13.85), (0.45, CY1 - 0.6, Z + 14.0), CYAN, 0.0)
    # piso do corredor termina antes do disco do salao (sem faces coplanares)
    mb.box2((-CW, CY0, Z - 0.1), (CW, CY1 - 0.5, Z + 0.1), FLOOR, 0.0)
    # moldura do portal do salao
    for s in (-1, 1):
        mb.box2((s * (CW - 0.1), CY1 - 0.2, Z), (s * (CW + 1.3), CY1 + 0.5, Z + 14.0), NAVY, 0.0)
    mb.box2((-CW - 1.3, CY1 - 0.2, Z + 14.0), (CW + 1.3, CY1 + 0.5, Z + 15.2), NAVY, 0.0)
    return mb.finish()


# ------------------------------------------------------------------ salao sob a cupula
def niche(mb, a_deg, kind):
    t = a_deg * D2R
    u = Vector((math.cos(t), math.sin(t), 0.0))
    tv = Vector((-math.sin(t), math.cos(t), 0.0))

    def P(r, s, z):
        return (CX + u.x * r + tv.x * s, CY + u.y * r + tv.y * s, z)
    rot = (0.0, 0.0, t)
    rm = (HR + NICHE_B) / 2.0
    for s in (-1, 1):
        mb.box((NICHE_B - HR + 0.6, 1.0, 11.6), P(rm + 0.2, s * (NICHE_W + 0.5), Z + 5.8), rot, WALL, 0.0)
        mb.box((0.5, 1.2, 11.6), P(HR - 0.25, s * (NICHE_W + 0.6), Z + 5.8), rot, NAVY, 0.0)
    mb.box((1.0, 2 * NICHE_W + 2.0, 11.6), P(NICHE_B + 0.5, 0.0, Z + 5.8), rot, WALL, 0.0)
    mb.box((NICHE_B - HR + 1.0, 2 * NICHE_W + 2.0, 0.6), P(rm + 0.2, 0.0, Z + 11.3), rot, WHITE, 0.0)
    r0f, r1f = HR + 0.15, NICHE_B + 0.2               # piso do nicho comeca fora do disco do salao (sem coplanar)
    mb.box((r1f - r0f, 2 * NICHE_W, 0.18), P((r0f + r1f) / 2.0, 0.0, Z - 0.01), rot, FLOOR, 0.0)
    mb.box((1.0, 2 * NICHE_W + 1.2, 0.14), P(HR - 0.05, 0.0, Z + 0.05), rot, NAVY, 0.0)      # soleira do nicho
    mb.box((0.5, 2 * NICHE_W + 2.4, 1.0), P(HR - 0.25, 0.0, Z + 11.5), rot, NAVY, 0.0)
    mb.box((0.25, 2 * NICHE_W - 1.0, 9.4), P(NICHE_B - 0.1, 0.0, Z + 5.4), rot, NAVY, 0.0)
    mb.box((NICHE_B - HR, 0.3, 0.3), P(rm, NICHE_W - 0.2, Z + 10.6), rot, BLUE, 0.0)
    mb.box((NICHE_B - HR, 0.3, 0.3), P(rm, -NICHE_W + 0.2, Z + 10.6), rot, BLUE, 0.0)
    if kind == "balls":
        K.torus(mb, Vector(P(NICHE_B - 0.3, 0.0, Z + 6.8)), 2.7, 0.2, CYAN, axis=tuple(u), n=36, k=6)
    else:
        mb.box((0.2, 7.0, 5.4), P(NICHE_B - 0.3, 0.0, Z + 5.6), rot, GLASS, 0.0)
        mb.box((0.25, 7.4, 0.3), P(NICHE_B - 0.32, 0.0, Z + 2.6), rot, BLUE, 0.0)
        mb.box((0.25, 7.4, 0.3), P(NICHE_B - 0.32, 0.0, Z + 8.6), rot, BLUE, 0.0)


def build_hall():
    mb = K.CMB("DB_Cap_Hall", COLL, detail="near")
    GAPS = [(270.0, 13.8), (180.0, 12.4), (0.0, 12.4)]
    wall = [(HR + 1.2, Z), (HR + 1.2, Z + 18.0), (HR, Z + 18.0), (HR, Z + 9.05), (HR - 0.25, Z + 9.05),
            (HR - 0.25, Z + 8.7), (HR - 0.1, Z + 8.7), (HR - 0.1, Z + 0.8), (HR - 0.2, Z + 0.8), (HR - 0.2, Z)]
    wmats = [WHITE, WHITE, WHITE, CYAN, CYAN, CYAN, WALL, NAVY, NAVY, NAVY]
    for s0, s1 in K.spans(GAPS):
        K.lathe(mb, C2, wall, WHITE, K.seg_n(s0, s1, 80), s0, s1, smooth=[2, 6], mats=wmats)
    for (a, h), zt in zip(GAPS, (14.0, 11.0, 11.0)):
        K.ring(mb, C2, HR, HR + 1.2, Z + zt, Z + 17.0, WHITE, 6, a - h, a + h, smooth_in=True)
    K.lathe(mb, C2, [(HR - 0.55, Z + 16.9), (HR + 0.05, Z + 16.9), (HR + 0.05, Z + 18.0), (HR - 0.15, Z + 18.0),
                     (HR - 0.15, Z + 18.3), (HR - 0.45, Z + 18.3), (HR - 0.45, Z + 18.0), (HR - 0.55, Z + 18.0)],
            NAVY, 80, mats=[NAVY, NAVY, NAVY, BLUE, BLUE, BLUE, BLUE, NAVY])
    # telas de vidro no alto (baias longe das aberturas e da recepcao)
    for i in range(16):
        bc = 11.25 + 22.5 * i
        if min(adist(bc, g) for g in (270.0, 180.0, 0.0, 90.0)) < 20.0:
            continue
        K.ring(mb, C2, HR - 0.08, HR + 0.05, Z + 10.4, Z + 15.6, GLASS, 6, bc - 7.8, bc + 7.8, smooth_in=True)
    # pilastras azul-marinho
    for i in range(16):
        a = 22.5 * i
        if min(adist(a, g) for g in (270.0, 180.0, 0.0, 90.0)) < 1.0:
            continue
        t = a * D2R
        rp = HR - 0.2
        mb.box((0.6, 1.3, 16.9), (CX + rp * math.cos(t), CY + rp * math.sin(t), Z + 8.45), (0, 0, t), NAVY, 0.0)
    # fundo da recepcao (norte): painel azul-marinho curvo + disco de vidro com aro ciano + faixas
    K.ring(mb, C2, HR - 0.4, HR + 0.02, Z + 1.0, Z + 15.0, NAVY, 12, 75.0, 105.0, smooth_in=True)
    yb = CY + HR - 0.4
    K.cyl_axis(mb, 3.7, 0.5, Vector((CX, yb - 0.2, Z + 9.6)), Vector((0.0, 1.0, 0.0)), CYAN, 40)
    K.cyl_axis(mb, 3.2, 0.5, Vector((CX, yb - 0.35, Z + 9.6)), Vector((0.0, 1.0, 0.0)), GLASS, 40)
    K.ring(mb, C2, HR - 0.55, HR - 0.38, Z + 4.4, Z + 4.75, BLUE, 12, 77.0, 103.0)
    # nichos
    niche(mb, 180.0, "balls")
    niche(mb, 0.0, "screen")
    # cupula interna (casca com a face lisa para DENTRO) + nervuras + faixa de luz + oculo
    prof, sm = K.shell_prof(IA, IB, ZI, 0.0, PH_O, 12, 0.6, inner_visible=True)
    K.lathe(mb, C2, prof, WHITE, 64, smooth=sm)
    for i in range(16):
        K.rib_meridian(mb, E_IN, 22.5 * i, 1.0, PH_O - 1.5, 10, 0.6, 0.3, 0.3, RIB, inward=True)
    K.rib_parallel(mb, E_IN, 40.0, 0.0, 360.0, 64, 0.4, 0.14, 0.3, BLUE, inward=True)
    zo = ZI + IB * math.sin(PH_O * D2R)
    K.lathe(mb, C2, [(4.0, zo - 0.6), (4.4, zo - 0.6), (4.4, zo - 0.45), (5.7, zo - 0.45), (5.7, zo + 0.5),
                     (4.0, zo + 0.5)], NAVY, 32, mats=[BLUE, BLUE, NAVY, NAVY, NAVY, NAVY])
    mb.cyl(4.3, 0.3, (CX, CY, zo + 0.3), (0, 0, 0), GLASS, 32, bevel=0.0)
    # poco de luz sobre o oculo: tubo + fundo azul opaco (o Glass do Roblox deixa ver o fundo: 'ceu', nao o oco)
    K.ring(mb, C2, 4.3, 4.7, zo + 0.45, zo + 2.4, WALL, 32)
    mb.cyl(4.7, 0.3, (CX, CY, zo + 2.55), (0, 0, 0), BLUE, 32, bevel=0.0)
    # anel de 8 colunas esbeltas + viga-anel com luz por baixo
    for i in range(8):
        t = (22.5 + 45.0 * i) * D2R
        px, py = CX + 13.5 * math.cos(t), CY + 13.5 * math.sin(t)
        K.lathe(mb, (px, py), [(0.35, Z), (1.15, Z), (1.15, Z + 1.0), (0.7, Z + 1.0), (0.7, Z + 7.0), (0.8, Z + 7.0),
                               (0.8, Z + 7.4), (0.7, Z + 7.4), (0.7, Z + 21.75), (1.05, Z + 21.75), (1.05, Z + 22.45),
                               (0.35, Z + 22.45)], WHITE, 12, smooth=[3, 7],
                mats=[NAVY, NAVY, NAVY, WHITE, BLUE, BLUE, BLUE, WHITE, NAVY, NAVY, NAVY, WHITE])
    K.lathe(mb, C2, [(12.5, Z + 22.4), (13.1, Z + 22.4), (13.1, Z + 22.25), (13.9, Z + 22.25), (13.9, Z + 22.4),
                     (14.5, Z + 22.4), (14.5, Z + 23.4), (12.5, Z + 23.4)], WHITE, 56, smooth=[5, 7],
            mats=[WHITE, BLUE, BLUE, BLUE, WHITE, WHITE, WHITE, WHITE])
    # piso: disco polido, anel azul-marinho sob as colunas, anel azul do deambulatorio, raios azuis
    mb.cyl(HR + 0.1, 0.2, (CX, CY, Z - 0.03), (0, 0, 0), FLOOR, 72, bevel=0.0)      # topo Z + 0,07
    K.ring(mb, C2, 12.4, 14.6, Z + 0.05, Z + 0.12, NAVY, 64)
    K.ring(mb, C2, 17.3, 17.9, Z + 0.05, Z + 0.12, BLUE, 72)
    for i in range(8):
        t = (22.5 + 45.0 * i) * D2R
        mb.box((7.0, 0.45, 0.07), (CX + 8.9 * math.cos(t), CY + 8.9 * math.sin(t), Z + 0.085), (0, 0, t), BLUE, 0.0)
    return mb.finish()


def build_props():
    mb = K.CMB("DB_Cap_HallProps", COLL, detail="near")
    # balcao da recepcao (arco ao norte; o NPC fica atras, o jogador na frente)
    K.lathe(mb, C2, [(9.2, Z), (10.8, Z), (10.8, Z + 3.0), (9.2, Z + 3.0)], WHITE, 16, 58.0, 122.0, smooth=[1, 3])
    K.lathe(mb, C2, [(8.9, Z + 3.0), (11.05, Z + 3.0), (11.05, Z + 3.35), (8.9, Z + 3.35)], NAVY, 16, 56.0, 124.0)
    K.ring(mb, C2, 9.05, 9.25, Z + 0.6, Z + 1.9, BLUE, 16, 60.0, 120.0, smooth_in=True)
    K.ring(mb, C2, 9.0, 9.25, Z + 2.2, Z + 2.5, BLUE, 16, 60.0, 120.0)
    for sx in (-1, 1):
        mb.box((0.5, 0.4, 0.5), (CX + sx * 2.6, CY + 10.3, Z + 3.6), (0, 0, 0), NAVY, 0.0)
        mb.box((1.3, 0.16, 0.85), (CX + sx * 2.6, CY + 10.25, Z + 4.25), (0.3, 0.0, 0.0), GLASS, 0.0)
    # plataforma do holograma (andavel, degrau 0,5)
    mb.cyl(4.5, 0.46, (CX, CY, Z + 0.23), (0, 0, 0), WHITE, 48, bevel=0.0)
    K.ring(mb, C2, 4.05, 4.55, Z + 0.38, Z + 0.52, CYAN, 48)
    mb.cyl(4.05, 0.08, (CX, CY, Z + 0.46), (0, 0, 0), NAVY, 48, bevel=0.0)
    K.ring(mb, C2, 2.5, 2.85, Z + 0.46, Z + 0.54, CYAN, 40)
    mb.cyl(1.3, 0.12, (CX, CY, Z + 0.48), (0, 0, 0), GLASS, 24, bevel=0.0)
    # pedestal das 7 esferas (nicho oeste)
    px, py = BALLS_C
    mb.cyl(2.6, 0.5, (px, py, Z + 0.25), (0, 0, 0), NAVY, 32, bevel=0.0)
    K.ring(mb, (px, py), 1.0, 1.9, Z + 0.5, Z + 3.1, WHITE, 32, smooth_out=True)
    K.ring(mb, (px, py), 1.2, 1.98, Z + 2.2, Z + 2.5, CYAN, 32)
    mb.cyl(2.45, 0.3, (px, py, Z + 3.25), (0, 0, 0), NAVY, 32, bevel=0.0)
    view = Vector((1.0, 0.0, 0.5)).normalized()          # as estrelas olham para o salao
    tu = Vector((0.0, 1.0, 0.0))
    tv = view.cross(tu).normalized() * -1.0
    pats = {1: [(0, 0)], 2: [(-0.5, 0), (0.5, 0)], 3: [(0, 0.6), (-0.52, -0.3), (0.52, -0.3)],
            4: [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)],
            5: [(-0.55, -0.55), (0.55, -0.55), (-0.55, 0.55), (0.55, 0.55), (0, 0)],
            6: [(-1.0, 0.5), (0.0, 0.5), (1.0, 0.5), (-1.0, -0.5), (0.0, -0.5), (1.0, -0.5)],
            7: [(0, 0)] + [(math.cos(k * math.pi / 3), math.sin(k * math.pi / 3)) for k in range(6)]}
    br = 0.7
    spots = [(0.0, 0.0, 4)] + [(1.5 * math.cos((k * 60.0 + 30.0) * D2R), 1.5 * math.sin((k * 60.0 + 30.0) * D2R), c)
                               for k, c in enumerate((1, 2, 3, 5, 6, 7))]
    for dx, dy, cnt in spots:
        center = (dx == 0.0 and dy == 0.0)
        hz = 0.6 if center else 0.22
        mb.cyl(0.45, hz, (px + dx, py + dy, Z + 3.4 + hz / 2), (0, 0, 0), GOLD, 12, bevel=0.0)
        bc = Vector((px + dx, py + dy, Z + 3.4 + hz + br - 0.08))
        K.sphere(mb, bc, br, BALL, sub=2)
        for u, v in pats[cnt]:
            n = (view + tu * (u * 0.5) + tv * (v * 0.5)).normalized()
            fm_lib.MB.cyl(mb, 0.15, 0.14, tuple(bc + n * (br - 0.03)), tuple(K.rot_to(n)), STAR, 8, bevel=0.0)
    return mb.finish()


def build_holo():
    """holograma que gira sobre a plataforma (peca movel VFX)"""
    mb = K.CMB("VFX_DBCAP_Holo", VFXC)
    c = Vector((CX, CY, Z + 12.0))
    K.torus(mb, c, 3.4, 0.16, CYAN, axis=(0.0, 0.0, 1.0), n=48, k=6)
    K.torus(mb, c, 3.2, 0.13, CYAN, axis=(0.866, 0.0, 0.5), n=44, k=6)
    K.torus(mb, c, 3.0, 0.13, CYAN, axis=(-0.433, 0.75, 0.5), n=44, k=6)
    K.torus(mb, c + Vector((0, 0, -3.2)), 1.6, 0.12, CYAN, axis=(0.0, 0.0, 1.0), n=32, k=6)
    K.sphere(mb, c, 1.35, GLASS, sub=2)
    ob = mb.finish()
    ob["pivot"] = tuple(c)
    ob["axis"] = (0.0, 0.0, 1.0)
    ob["rpm"] = 4.0
    return ob


# ------------------------------------------------------------------ anexos (nao entraveis) + elos
def build_annexes():
    mb = K.CMB("DB_Cap_Annexes", COLL, detail="near")
    towers = {k: (x, y) for x, y, r, k, w in L.TOWER_SITES}
    ports = []
    for (ax, ay, ar), side, tk in zip(L.CAPSULE_ANNEX, ("W", "E"), ("comm", "lookout")):
        c = (ax, ay)
        tx, ty = towers[tk]
        pd = math.degrees(math.atan2(ty - ay, tx - ax))
        ld = math.degrees(math.atan2(CY - ay, CX - ax))
        drum = [(ar - 0.8, Z - 0.3), (ar + 0.7, Z - 0.3), (ar + 0.7, Z + 0.8), (ar + 0.35, Z + 0.8), (ar + 0.35, Z + 1.4),
                (ar, Z + 1.4), (ar, Z + 3.0), (ar + 0.4, Z + 3.0), (ar + 0.4, Z + 3.4), (ar + 0.12, Z + 3.4),
                (ar + 0.12, Z + 6.2), (ar + 0.4, Z + 6.2), (ar + 0.4, Z + 6.6), (ar, Z + 6.6), (ar, Z + 13.2),
                (ar + 0.45, Z + 13.2), (ar + 0.45, Z + 14.0), (ar - 0.8, Z + 14.0)]
        am = [BLOCK, BLOCK, BLOCK, NAVY, NAVY, WHITE, NAVY, NAVY, NAVY, GLASS, NAVY, NAVY, NAVY, WHITE, NAVY, NAVY,
              NAVY, WHITE]
        K.lathe(mb, c, drum, WHITE, 48, smooth=[5, 9, 13], mats=am)
        K.ring(mb, c, ar - 0.5, ar - 0.25, Z + 3.3, Z + 6.3, NAVY, 32)     # fundo opaco atras da faixa de vidro
        for i in range(24):
            t = (7.5 + 15.0 * i) * D2R
            mb.box((0.45, 0.4, 2.8), (ax + (ar + 0.2) * math.cos(t), ay + (ar + 0.2) * math.sin(t), Z + 4.8),
                   (0, 0, t), NAVY, 0.0)
        cb = 0.72 * ar
        E = K.Ell(ax, ay, Z + 14.0, ar + 0.05, cb)
        ph_t = math.degrees(math.acos(1.6 / (ar + 0.05)))
        prof, sm = K.shell_prof(ar + 0.05, cb, Z + 14.0, 0.0, ph_t, 9, 0.5, k_hidden=3)
        K.lathe(mb, c, prof, BLUE, 48, smooth=sm)
        K.rib_parallel(mb, E, 36.0, 0.0, 360.0, 48, 0.9, 0.22, 0.3, WHITE)
        ztop = Z + 14.0 + cb * math.sin(ph_t * D2R)
        mb.cyl(1.9, 0.9, (ax, ay, ztop + 0.2), (0, 0, 0), WHITE, 16, bevel=0.0)
        mb.cyl(0.22, 3.4, (ax, ay, ztop + 2.3), (0, 0, 0), STEEL, 6, bevel=0.0)
        K.sphere(mb, (ax, ay, ztop + 4.2), 0.4, CYAN, sub=1)
        for i in range(12):
            th = 15.0 + 30.0 * i
            if adist(th, pd) < 30.0 or adist(th, ld) < 26.0:
                continue
            K.porthole(mb, ax, ay, ar, th, Z + 10.0, 1.3, n=12)
        # porta redonda da passarela de vidro (a zona das torres encaixa o tubo aqui)
        t = pd * D2R
        d = Vector((math.cos(t), math.sin(t), 0.0))
        pc = Vector((ax, ay, Z + 10.0))
        K.cyl_axis(mb, 4.3, 1.2, pc + d * (ar + 0.1), d, WHITE, 32)
        K.cyl_axis(mb, 3.7, 2.0, pc + d * (ar + 0.4), d, NAVY, 32)
        K.cyl_axis(mb, 2.75, 2.1, pc + d * (ar + 0.5), d, GLASS, 32)
        pf = pc + d * (ar + 1.45)
        ports.append((side, tk, pf, t))
    # elos baixos envidracados (sem porta) entre a cupula e os anexos
    for lk in LINKS:
        (lx, ly), ang, Ln = lk["c"], lk["ang"], lk["L"]
        rot = (0.0, 0.0, ang)
        mb.box((Ln, 8.0, 10.4), (lx, ly, Z + 5.2), rot, WHITE, 0.0)
        mb.box((Ln, 8.3, 0.9), (lx, ly, Z + 0.45), rot, NAVY, 0.0)
        mb.box((Ln - 0.4, 8.2, 2.4), (lx, ly, Z + 5.4), rot, GLASS, 0.0)
        mb.box((Ln, 8.6, 0.5), (lx, ly, Z + 10.15), rot, NAVY, 0.0)
        mb.box((Ln + 0.4, 9.0, 0.8), (lx, ly, Z + 10.8), rot, BLUE, 0.0)
        ca, sa = math.cos(ang), math.sin(ang)
        for f in (-0.18, 0.18):
            for s in (-1, 1):
                q = (lx + ca * Ln * f - sa * s * 4.12, ly + sa * Ln * f + ca * s * 4.12, Z + 5.4)
                mb.box((0.4, 0.3, 2.6), q, rot, NAVY, 0.0)
    ob = mb.finish()
    for side, tk, pf, t in ports:
        mk("SKYWALK_PORT_Cap%s" % side, tuple(pf), (0.0, 0.0, t - math.pi / 2), 3.0, "CIRCLE",
           props={"tower": tk, "z": Z + 10.0, "tube_r": 2.6, "collar_r": 3.7,
                  "note": "face da porta redonda do anexo Capsule: o tubo de vidro da zona towers encaixa aqui"})
    return ob


# ------------------------------------------------------------------ terraco CAP: calcamento, desenho, arrimo, guardas
def cap_guard_runs():
    """os mesmos trechos das guardas invisiveis do db_col (terrace_guards) no contorno do CAP"""
    pts = DL.ccw(DL.cap_poly())
    z = L.CAP
    stairs = db_col.stair_list()
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)

    def near_stair_top(x, y):
        for nm, base, ang, w, n, rise, tread, g in stairs:
            if abs(base[2] + rise * n - z) > 0.3:
                continue
            tx = base[0] + math.cos(ang) * tread * n
            ty = base[1] + math.sin(ang) * tread * n
            dx, dy = x - tx, y - ty
            along = abs(-dx * math.sin(ang) + dy * math.cos(ang))
            depth = abs(dx * math.cos(ang) + dy * math.sin(ang))
            if along < w / 2 + 0.8 and depth < 3.0:
                return True
        return False

    def keep(x, y):
        d = Vector((x - cx, y - cy, 0))
        if d.length < 1e-3:
            return False
        d.normalize()
        ox, oy = x + d.x * 1.6, y + d.y * 1.6
        if not L.point_in_poly(ox, oy, L.ISLAND_RIM):
            return False
        if z - L.zone_of(ox, oy) <= 2.3:
            return False
        if db_col._opening(ox, oy):
            return False
        return not near_stair_top(x, y)
    runs = [list(r) for r in db_col._runs(pts, keep, step=1.0)]
    # junta trechos contiguos (o contorno fecha no vertice 0)
    merged = True
    while merged and len(runs) > 1:
        merged = False
        for i in range(len(runs)):
            for j in range(len(runs)):
                if i != j and (runs[i][-1] - runs[j][0]).length < 1.6:
                    runs[i] = runs[i] + runs[j]
                    runs.pop(j)
                    merged = True
                    break
            if merged:
                break
    return runs


def simplify(run, tol=0.05):
    """reduz uma polilinha amostrada aos cantos"""
    out = [run[0]]
    for i in range(1, len(run) - 1):
        a, b, c = out[-1], run[i], run[i + 1]
        d1, d2 = (b - a), (c - b)
        if d1.length < 1e-6 or d2.length < 1e-6:
            continue
        if abs(d1.normalized().cross(d2.normalized()).z) > tol:
            out.append(b)
    out.append(run[-1])
    return out


def _dist_poly_edge(x, y, poly):
    best = 1e9
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        d, _ = L.seg_dist(x, y, a[0], a[1], b[0], b[1])
        best = min(best, d)
    return best


def free_ground(x, y):
    """ponto livre do terraco (para o desenho do piso): dentro do CAP, longe da borda e dos predios"""
    if not L.point_in_poly(x, y, L.CAP_POLY):
        return False
    if _dist_poly_edge(x, y, L.CAP_POLY) < 2.4:
        return False
    if math.hypot(x - CX, y - CY) < 31.4:
        return False
    if abs(x) < 11.6 and y < 150.0:
        return False
    for ax, ay, ar in L.CAPSULE_ANNEX:
        if math.hypot(x - ax, y - ay) < ar + 2.0:
            return False
    for lk in LINKS:
        (lx, ly), ang = lk["c"], lk["ang"]
        dx, dy = x - lx, y - ly
        a = dx * math.cos(ang) + dy * math.sin(ang)
        b = -dx * math.sin(ang) + dy * math.cos(ang)
        if abs(a) < lk["L"] / 2 + 1.0 and abs(b) < lk["W"] / 2 + 1.4:
            return False
    return True


def _inlay_runs(samples):
    runs, cur = [], []
    for p in samples:
        if free_ground(p[0], p[1]):
            cur.append(p)
        else:
            if len(cur) > 2:
                runs.append(cur)
            cur = []
    if len(cur) > 2:
        runs.append(cur)
    return runs


def build_terrace():
    mb = K.CMB("DB_Cap_Terrace", COLL, rng=random.Random(4101), detail="near")
    poly = DL.ccw(list(L.CAP_POLY))
    # nucleo (muro liso atras da alvenaria) + calcamento (topo 0,05 acima do piso de colisao)
    mb.prism(offset_poly(poly, 0.6), H - 0.4, Z - 0.7, BLOCK)
    mb.prism(poly, Z - 0.7, Z + 0.05, PAVE)
    # muro de arrimo em blocos de arenito (HUB -> CAP), aberto na escadaria
    hx = L.CAP_STAIR[2] / 2 + 1.2
    rng = random.Random(4102)
    n = len(poly)
    for i in range(n):
        a, b = Vector((*poly[i], 0)), Vector((*poly[(i + 1) % n], 0))
        t = (b - a).normalized()
        nn = Vector((t.y, -t.x, 0))
        segs = [(a, b)]
        if abs(a.y - L.CAP_STAIR[1]) < 0.1 and abs(b.y - L.CAP_STAIR[1]) < 0.1:
            segs = [(a, Vector((-hx, a.y, 0))), (Vector((hx, a.y, 0)), b)]
        for p, q in segs:
            ext0 = 0.0 if abs(abs(p.x) - hx) < 0.01 and abs(p.y - L.CAP_STAIR[1]) < 0.1 else 0.7
            ext1 = 0.0 if abs(abs(q.x) - hx) < 0.01 and abs(q.y - L.CAP_STAIR[1]) < 0.1 else 0.7
            pa = p + nn * 0.5 - t * ext0
            pb = q + nn * 0.5 + t * ext1
            DL.FP.masonry_wall(mb, (pa.x, pa.y), (pb.x, pb.y), H - 0.3, Z - 0.7, 1.0, rng, m=BLOCK, m2=BLOCK_B,
                               course=1.9, blk=(3.2, 5.4), core=False, bevel=0.0)
    # capeamento branco na borda (aberto na escadaria)
    path = [Vector((hx, L.CAP_STAIR[1], 0))] + [Vector((*p, 0)) for p in poly[1:]] + [Vector((*poly[0], 0))] + \
           [Vector((-hx, L.CAP_STAIR[1], 0))]
    off = offset_poly(poly, 0.475)
    opath = [(hx, L.CAP_STAIR[1] - 0.475)] + list(off[1:]) + [off[0]] + [(-hx, L.CAP_STAIR[1] - 0.475)]
    mb.prism(DL.ribbon_poly(opath, 0.775), Z - 0.7, Z + 0.12, WHITE)
    # desenho do piso: aneis concentricos a cupula (azul + arenito) e raios de arenito (sol em volta do predio)
    for rr, w, m in ((34.0, 0.9, BLUE), (40.5, 0.6, BLOCK_B), (48.0, 0.6, BLOCK_B), (57.0, 0.6, BLOCK_B)):
        samples = [(CX + rr * math.cos(a * D2R), CY + rr * math.sin(a * D2R)) for a in [i * 2.0 for i in range(181)]]
        for run in _inlay_runs(samples):
            mb.prism(DL.ribbon_poly(run, w / 2), Z - 0.05, Z + 0.13, m)       # aneis 0,03 acima dos raios
    for k in range(24):
        a = 7.5 + 15.0 * k
        if adist(a, 270.0) < 12.0:
            continue
        samples = [(CX + r * math.cos(a * D2R), CY + r * math.sin(a * D2R)) for r in [31.5 + 0.8 * i for i in range(46)]]
        for run in _inlay_runs(samples):
            mb.prism(DL.ribbon_poly([run[0], run[-1]], 0.25), Z - 0.05, Z + 0.1, BLOCK_B)
    # guarda-corpo branco com capeamento azul nas linhas das guardas do db_col (aberto na escadaria)
    runs = cap_guard_runs()
    zb = Z + 0.12
    lamp_spots = [(-24.0, 132.0), (24.0, 132.0), (-48.0, 132.0), (48.0, 132.0), (-73.0, 146.0), (73.0, 146.0),
                  (-50.0, 199.0), (50.0, 199.0)]
    posts = []
    for run in runs:
        cs = simplify(run)
        for p, q in zip(cs, cs[1:]):
            d = q - p
            Ln = d.length
            if Ln < 0.3:
                continue
            ang = math.atan2(d.y, d.x)
            c = (p + q) / 2
            mb.box((Ln + 0.25, 1.0, 1.9), (c.x, c.y, zb + 0.95), (0, 0, ang), WHITE, 0.0)
            mb.box((Ln + 0.25, 1.12, 0.3), (c.x, c.y, zb + 0.15), (0, 0, ang), NAVY, 0.0)
            mb.box((Ln + 0.45, 1.3, 0.35), (c.x, c.y, zb + 2.07), (0, 0, ang), BLUE, 0.0)
            k = max(1, int(round(Ln / 9.0)))
            for i in range(k + 1):
                posts.append((p + d * (i / k), ang))
    # postes: os regulares (sem repetir nas juntas) + os de lanterna nos pontos marcados (sobre a linha da guarda)
    placed = []
    for sx, sy in lamp_spots:
        best = None
        for run in runs:
            cs = simplify(run)
            for p, q in zip(cs, cs[1:]):
                d, t = L.seg_dist(sx, sy, p.x, p.y, q.x, q.y)
                if best is None or d < best[0]:
                    best = (d, p + (q - p) * t, math.atan2(q.y - p.y, q.x - p.x))
        if best and best[0] < 2.0:
            placed.append((best[1], best[2], True))
    for pp, ang in posts:
        if any((pp - o).length < 2.6 for o, a, lm in placed):
            continue
        placed.append((pp, ang, False))
    for pp, ang, lm in placed:
        mb.box((1.4, 1.4, 2.6), (pp.x, pp.y, zb + 1.3), (0, 0, ang), NAVY, 0.0)
        mb.box((1.65, 1.65, 0.3), (pp.x, pp.y, zb + 2.75), (0, 0, ang), BLUE, 0.0)
        if lm:
            lamp_head(mb, (pp.x, pp.y, zb + 2.9), 0.75)
    return mb.finish()


# ------------------------------------------------------------------ escadaria grande HUB -> CAP
def build_stair():
    mb = K.CMB("DB_Cap_Stair", COLL, rng=random.Random(4201), detail="near")
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if nm != "Cap":
            continue
        DL.vis_stairs(mb, base, ang, w, n, rise, tread, PAVE, BLOCK)
        y0s, y1s = base[1], base[1] + n * tread
        zl0 = base[2] + rise + 1.2                      # topo do banzo no 1o degrau

        def zl(y):
            return zl0 + rise * (y - y0s) / tread
        for s in (-1, 1):
            x = s * (w / 2 + 0.6)
            # balaustrada branca MAIS LARGA que o banzo de blocos (1,2) e descendo sobre ele: esconde o serrilhado
            mb.beam((x, y0s, zl(y0s) - 0.05), (x, y1s, zl(y1s) - 0.05), 1.3, 2.5, WHITE, 0.0)
            mb.beam((x, y0s, zl(y0s) + 1.5), (x, y1s, zl(y1s) + 1.5), 1.45, 0.35, BLUE, 0.0)
            # pilares: pe (na praca) e topo (recuado e para fora: abre o acesso lateral a porta; desce ate a praca)
            for px, py, pz1, hs, top in ((s * 12.1, y0s, H + 3.4, 1.1, False), (s * 12.6, y1s - 1.1, Z + 3.4, 0.9, True)):
                pz0 = H
                mb.box2((px - hs, py - hs, pz0), (px + hs, py + hs, pz1), WHITE, 0.0)
                for zb in ((H, Z) if top else (H,)):
                    mb.box2((px - hs - 0.1, py - hs - 0.1, zb - 0.2), (px + hs + 0.1, py + hs + 0.1, zb + 0.9), NAVY,
                            0.0)
                mb.box2((px - hs - 0.2, py - hs - 0.2, pz1), (px + hs + 0.2, py + hs + 0.2, pz1 + 0.35), BLUE, 0.0)
                lamp_head(mb, (px, py, pz1 + 0.35), 0.85 if top else 0.95)
                col_box2("DB_CapStair", (px - hs, py - hs, pz0), (px + hs, py + hs, pz1 + 1.6))
    return mb.finish()


# ------------------------------------------------------------------ colisao dos volumes proprios
def build_collisions():
    # casca externa do tambor, aberta atras do pavilhao (|x| < 10)
    g = math.degrees(math.asin(10.0 / 29.7))
    K.chords("DB_CapShell", CX, CY, 29.7, 1.2, Z - 0.5, Z + 16.0, 270.0 + g, 270.0 - g + 360.0, 9.0)
    # parede do salao (vao do corredor ao sul e dos 2 nichos)
    gs = math.degrees(math.asin(6.2 / 21.6))
    gn = math.degrees(math.asin((NICHE_W + 1.0) / 21.6))
    for a0, a1 in ((270.0 + gs, 360.0 - gn), (gn, 180.0 - gn), (180.0 + gn, 270.0 - gs)):
        K.chords("DB_CapHall", CX, CY, 21.6, 1.2, Z - 0.5, Z + 20.0, a0, a1, 9.0)
    # nichos (laterais + fundo)
    for a in (180.0, 0.0):
        t = a * D2R
        u = Vector((math.cos(t), math.sin(t), 0.0))
        tv = Vector((-math.sin(t), math.cos(t), 0.0))
        rm = (HR + NICHE_B) / 2.0
        for s in (-1, 1):
            p = Vector((CX, CY, 0)) + u * (rm + 0.2) + tv * (s * (NICHE_W + 0.5))
            col_box("DB_CapHall", (NICHE_B - HR + 1.2, 1.0, 12.5), (p.x, p.y, Z + 5.75), (0, 0, t))
        p = Vector((CX, CY, 0)) + u * (NICHE_B + 0.5)
        col_box("DB_CapHall", (1.0, 2 * NICHE_W + 2.0, 12.5), (p.x, p.y, Z + 5.75), (0, 0, t))
    # pavilhao: frente (com vao da porta), verga, laterais, fundo do foyer, corredor, pilares
    A = "DB_CapFoyer"
    col_box2(A, (X0, Y0, Z - 0.5), (-DW, Y0 + WT, Z + HW + 2.0))
    col_box2(A, (DW, Y0, Z - 0.5), (X1, Y0 + WT, Z + HW + 2.0))
    col_box2(A, (-DW, Y0, Z + DH), (DW, Y0 + WT, Z + HW + 2.0))
    col_box2(A, (X0, Y0, Z - 0.5), (X0 + WT, YB, Z + HW + 2.0))
    col_box2(A, (X1 - WT, Y0, Z - 0.5), (X1, YB, Z + HW + 2.0))
    col_box2(A, (X0 + WT, Y1, Z - 0.5), (-CW - WT, Y1 + WT + 0.2, Z + HW))
    col_box2(A, (CW + WT, Y1, Z - 0.5), (X1 - WT, Y1 + WT + 0.2, Z + HW))
    for s in (-1, 1):
        col_box2(A, (s * CW, CY0, Z - 0.5), (s * (CW + WT), CY1 + 0.3, Z + 15.0))
        col_box2(A, (s * 5.6, 134.0, Z - 0.5), (s * 7.8, 135.3, Z + 15.5))
    # colunas do salao, balcao (3 cordas), plataforma (faixas), pedestal
    B = "DB_CapProps"
    for i in range(8):
        t = (22.5 + 45.0 * i) * D2R
        col_box(B, (1.6, 1.6, 23.0), (CX + 13.5 * math.cos(t), CY + 13.5 * math.sin(t), Z + 11.0), (0, 0, t))
    K.chords(B, CX, CY, 10.0, 1.8, Z - 0.5, Z + 3.35, 58.0, 122.0, 22.0)
    dais = [(CX + 4.4 * math.cos(a * D2R), CY + 4.4 * math.sin(a * D2R)) for a in range(0, 360, 15)]
    DL.col_poly(B, dais, Z - 0.5, Z + 0.46, step=1.6, mode="inter")
    octo_col(B, BALLS_C[0], BALLS_C[1], 2.3, Z - 0.5, Z + 5.2)
    # anexos (anel de cordas) e elos
    for ax, ay, ar in L.CAPSULE_ANNEX:
        K.chords("DB_CapAnnex", ax, ay, ar + 0.1, 1.2, Z - 0.5, Z + 15.0, 0.0, 360.0, 30.0)
    for lk in LINKS:
        (lx, ly), ang, Ln = lk["c"], lk["ang"], lk["L"]
        col_box("DB_CapAnnex", (Ln, 8.3, 12.0), (lx, ly, Z + 5.5), (0, 0, ang))


# ------------------------------------------------------------------ luzes (6) e marcadores
def build_lights():
    light("L_DBCap_Foyer", "POINT", (0.0, 140.6, Z + 11.0), 2400, (1.0, 0.72, 0.4), 1.0)
    light("L_DBCap_Corridor", "POINT", (0.0, 149.4, Z + 11.0), 700, (0.9, 0.94, 1.0), 0.8)
    light("L_DBCap_HallCenter", "POINT", (CX, CY, Z + 17.5), 6000, (0.93, 0.96, 1.0), 3.0)
    light("L_DBCap_Reception", "POINT", (CX, CY + 12.0, Z + 8.0), 1200, (1.0, 0.86, 0.7), 1.5)
    light("L_DBCap_Balls", "POINT", (CX - 18.5, CY, Z + 7.5), 700, (1.0, 0.62, 0.25), 0.6)
    light("L_DBCap_Screen", "POINT", (CX + 18.5, CY, Z + 6.5), 900, (0.45, 0.85, 1.0), 0.8)


def build_markers():
    mk("NPC_Capsule", (CX, CY + 12.0, Z), (0, 0, math.pi), 1.5, "SPHERE",
       props={"floor": Z, "note": "atras do balcao de recepcao (arco norte do salao), olhando para a entrada"})
    mk("PLAYER_INTERACT_Capsule", (CX, CY + 6.0, Z), (0, 0, 0), 1.5, "SPHERE",
       props={"floor": Z, "note": "na frente do balcao, entre a plataforma do holograma e a recepcao"})


def build():
    build_dome()
    build_entrance()
    build_hall()
    build_props()
    build_holo()
    build_annexes()
    build_terrace()
    build_stair()
    build_collisions()
    build_lights()
    build_markers()
