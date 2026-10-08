# vm_layout - PLANTA TRAVADA do lobby VILA MEDIEVAL (V0). Tudo em coordenadas ROBLOX (origem do place, 1 BU = 1 stud):
#   X = leste, Z = sul (as ilhas seguem em +Z), Y = cima. A forja fica ao NORTE (-Z), o spawn olha -Z para ela.
#   Blender = (X, -Z, Y)  (mesma convencao do export_roblox: Roblox = (x, z, -y) do Blender).
# Planta aprovada: ref/planta_aprovada_v1.png (escala medida: ~0,316 stud/px; spawn (600,840)px = (0, 94)).
# Este arquivo NAO importa bpy (o vm_qa e as folhas leem daqui sem Blender).
import math

# ------------------------------------------------------------------ cotas (Y Roblox)
Y_GRASS = 5.8          # grama do plato ao sul do canal (o piso de colisao fica em 6,0: 0,2 imperceptivel)
Y_PAVE = 6.0           # praca, ruas, patio dos portais, ponte das ilhas (= piso 6 da Vila da Folha em z 222)
Y_NORTH_GRASS = 6.8    # grama ao norte do canal
Y_NORTH = 7.0          # rua norte, largo e piso da forja (contrato do Ignis: piso Y = 7)
Y_SPAWN = 9.6          # terraco do spawn (5 degraus de 0,72 acima da praca)
Y_SHOP = 6.4           # piso da loja (1 soleira de 0,4)
Y_RANK = 6.4           # palco do ranking (1 degrau de 0,4)
Y_PORTAL = 7.2         # terraco em semicirculo dos portais (2 degraus de 0,6); = cota T do portal_studio
Y_WATER = 2.6          # espelho d'agua do canal e da levada da roda
Y_CANAL_BED = 0.6
Y_ISLE = 6.0           # piso da praca de chegada da Ilha 1 (Vila da Folha)
WALK = 16.0            # WalkSpeed padrao do Roblox (studs/s) para o tempo a pe

# ------------------------------------------------------------------ plato (contorno do chao andavel)
PLATEAU = [(-126, -126), (124, -126), (166, -96), (168, 62), (150, 118), (104, 146), (64, 153), (38, 153),
           (12, 147), (-30, 141), (-84, 150), (-150, 153), (-196, 137), (-222, 96), (-224, 40), (-208, 6),
           (-178, -2), (-131, -2), (-129, -22), (-128, -60)]
PLATEAU_BOTTOM = -34.0

# ------------------------------------------------------------------ spawn (terraco + escadaria para a praca)
SPAWN = (0.0, 94.0)
SPAWN_TERRACE = [(-17, 88), (17, 88), (20, 91), (20, 109), (17, 112), (-17, 112), (-20, 109), (-20, 91)]
SPAWN_STAIR = dict(x0=-10.0, x1=10.0, z_foot=80.0, n=5, rise=0.72, run=1.6)     # sobe para +Z ate z 88
MAILBOX = (-14.0, 100.0)            # correio no terraco, ao lado do spawn

# ------------------------------------------------------------------ praca central
PLAZA_C = (0.0, 50.0)
PLAZA_R = 36.0
MEDAL_R = 9.0                       # medalhao rebaixado 0,12 (picareta + bigorna), sem colisao propria

# ------------------------------------------------------------------ eixo norte: rua, canal, ponte, largo, forja
STREET_HW = 9.0                     # meia largura da rua do eixo (18 de paralelepipedo)
STREET_S = (15.0, 1.0)              # z da praca ate a cabeceira sul da ponte
CANAL_Z = (-18.0, -6.0)             # agua do canal (12 de largura); muros de 1 stud dos dois lados
CANAL_X = (-129.0, 166.0)
BRIDGE_Z = (1.0, -21.0)             # tabuleiro da ponte de pedra (sul -> norte)
BRIDGE_CROWN = 7.4                  # cota do meio da ponte (6,0 -> 7,4 -> 7,0)
STREET_N = (-21.0, -36.0)
FORGE_SQ = [(-26, -36), (24, -36), (24, -50.0), (-26, -50.0)]   # largo da forja (cota 7); o piso do salao segue ate -77

# FORJA (marco). Contrato do golem novo (sessao Ignis 3D): Root (-0,9; 7; -60,7) olhando +Z, bigorna a +5 em Z.
IGNIS_ROOT = (-0.9, 7.0, -60.7)
IGNIS_ANVIL = (-0.9, 7.0, -55.7)
IGNIS_BELLY_Y = 13.79
# ENVOLTORIA LIVRE do golem (sem geometria nem colisao da forja dentro): X -9,9..6,1  Y 7..31  Z -64,7..-52,7
IGNIS_ENV = ((-9.9, 7.0, -64.7), (6.1, 31.0, -52.7))
# chao livre e plano na cota 7 diante do golem (o jogador chega pela frente)
IGNIS_FRONT = ((-9.9, 7.0, -52.7), (6.1, 13.0, -40.0))
LETREIRO_Y = 20.0
FORGE_HALL = (-16.0, 14.0, -50.0, -77.0)          # x0, x1, z_frente, z_fundo (salao aberto pela frente, pe-direito 26)
FORGE_TIE_Y = 33.0                                # linha dos tirantes/verga acima da envoltoria (31)
FORGE_WING_W = (-34.0, -16.0, -52.0, -88.0)       # ala oeste (carvao / deposito)
FORGE_WING_E = (14.0, 31.0, -52.0, -88.0)         # ala leste (martelo-pilao movido pela roda)
CHIMNEY = (0.0, -86.0)
CHIMNEY_TOP = 94.0
RACE_X = (33.0, 39.0)                             # levada da roda: sai do canal e corre para o norte
RACE_Z = (-19.0, -84.0)
WHEEL = (36.0, 9.4, -66.0)                         # centro da roda d'agua (eixo X), raio 7,5
WHEEL_R = 7.5

# ------------------------------------------------------------------ leste: loja de mochilas
SHOP = (62.0, 90.0, 30.0, 56.0)                   # x0, x1, z0, z1 (porta na face oeste, z 43)
SHOP_DOOR = (62.0, 43.0)
SHOP_WALL_H = 16.0
SHOP_STREET = [(34, 37), (62, 37), (62, 49), (34, 49)]
SHOP_NPC = (78.0, 43.0)                           # npc vendedor (atras do balcao, olhando -X)
SHOP_PLAYER = (69.0, 43.0)                        # jogador / PadLoja (na frente do balcao)

# ------------------------------------------------------------------ oeste: ranking + rua + patio dos portais
RANK_O = (-84.0, 20.0)                            # origem do GlobalTop100 (GroundPivot), +Z local = visitantes
RANK_FACE = (0.40, 0.92)                          # olha a rua oeste e a praca (sul-sudeste)
TOP100_HALF_W = 27.0                              # 2 quadros de 26 (x +-13,4) + aparas
TOP100_DEPTH = (-1.2, 13.2)                       # quadro em z 0 .. podios ate z 12,4
TOP100_H = 26.5
WEST_ROAD = [(-30, 52), (-58, 58), (-84, 64), (-104, 70)]
ROAD_W = 14.0
COURT_C = (-128.0, 72.0)
COURT_R = 40.0                                    # disco central do patio (cota 6)
COURT_RING = (40.0, 74.0, 85.0, 275.0)            # terraco dos portais: r0, r1, angulo0, angulo1 (graus, atan2(dz,dx))
PORTAL_R = 56.0                                   # raio do plano da espiral
PORTAL_STEP_DEG = 31.0
# ordem facil -> dificil = Config.Areas do jogo HOJE (Ilha 3 = Shadow Garden, Ilha 4 = Demon Slayer, Ilha 5 = Wano)
PORTALS = [("Naruto", 1), ("DragonBall", 2), ("ShadowGarden", 3), ("DemonSlayer", 4), ("OnePiece", 5),
           ("OnePunchMan", 6)]


def portal_bearing(i):
    """i = 0..5 -> angulo (graus, atan2(dz, dx)) do portal em volta do COURT_C. Naruto ao SUL (+Z), One Punch Man ao
    NORTE: quem entra pelo leste olhando o oeste ve facil -> dificil da esquerda para a direita."""
    return 180.0 + (i - 2.5) * PORTAL_STEP_DEG


def portal_pos(i):
    a = math.radians(portal_bearing(i))
    x, z = COURT_C[0] + PORTAL_R * math.cos(a), COURT_C[1] + PORTAL_R * math.sin(a)
    return (x, z), (-math.cos(a), -math.sin(a))      # posicao do plano da espiral, direcao para onde a espiral olha


# ------------------------------------------------------------------ sudeste: rua curva + portao + ponte da Ilha 1
EXIT_ROAD = [(24, 74), (38, 90), (48, 108), (52, 128), (50, 146)]
GATE = (50.0, 148.0)
GATE_HW = 9.0
ISLE_BRIDGE = [(50, 146), (50, 162), (45, 177), (33, 191), (17, 202), (5, 209), (0, 213), (0, 222)]
ISLE_BRIDGE_W = 16.0
ISLE_LANDING = (-12.0, 12.0, 213.0, 222.0)        # ultimo trecho na largura da praca da ilha (x +-12)
ISLE_LINK = (0.0, Y_ISLE, 222.0)                  # borda da praca de chegada da Vila da Folha (fm_terrain_isles)

# ------------------------------------------------------------------ casas (blockout do kit enxaimel)
# id, x, z, olha para (x, z), w (fachada), d (fundo), andares, cumeeira ('x' paralela a fachada | 'y' oitao p/ rua),
# reboco, telha, chamine, agua-furtada


def _h(i, x, z, tx, tz, w, d, nf, ridge, pl="Plaster_VM_Cream", rf="Roof_VM_Terracotta", ch=1, dormer=False, y=Y_PAVE,
       gh=7.0):
    return dict(id=i, x=x, z=z, fx=tx - x, fz=tz - z, w=w, d=d, floors=nf, ridge=ridge, plaster=pl, roof=rf,
                chimney=ch, dormer=dormer, y=y, ground_h=gh)


HOUSES = [
    # rua do eixo (sul do canal) e cantos norte da praca
    _h("S1W", -22.0, 6.0, 0.0, 6.0, 14, 11, 3, "x", ch=1, dormer=True),
    _h("S1E", 22.0, 6.0, 0.0, 6.0, 13, 11, 2, "y", "Plaster_VM_Ochre", "Roof_VM_Terracotta_B", ch=-1),
    _h("PNW", -38.0, 21.0, 0.0, 50.0, 14, 12, 3, "y", "Plaster_VM_Peach", ch=1),
    _h("PNE", 38.0, 21.0, 0.0, 50.0, 15, 12, 2, "x", ch=-1, dormer=True),
    _h("PSW", -38.0, 84.0, 0.0, 50.0, 14, 12, 2, "x", "Plaster_VM_Ochre", ch=1),
    # rua norte (entre o canal e o largo da forja)
    _h("N1W", -22.0, -29.0, 0.0, -29.0, 13, 11, 2, "y", "Plaster_VM_Peach", "Roof_VM_Terracotta_B", ch=1,
       y=Y_NORTH),
    _h("N1E", 21.0, -29.0, 0.0, -29.0, 12, 11, 3, "x", ch=-1, dormer=True, y=Y_NORTH),
    _h("N2W", -46.0, -44.0, -20.0, -44.0, 14, 12, 2, "x", "Plaster_VM_Ochre", ch=1, y=Y_NORTH),
    _h("N2E", 50.0, -34.0, 36.0, -40.0, 13, 11, 2, "y", ch=-1, y=Y_NORTH),
    # rua curva do sudeste (chegada das ilhas) - casas dos DOIS lados (enquadramento da ref_01)
    _h("E1", 62.0, 86.0, 40.0, 92.0, 14, 12, 3, "x", ch=1, dormer=True),
    _h("E2", 70.0, 108.0, 48.0, 108.0, 13, 11, 2, "y", "Plaster_VM_Peach", "Roof_VM_Terracotta_B", ch=-1),
    _h("E3", 70.0, 130.0, 51.0, 128.0, 14, 11, 2, "x", "Plaster_VM_Ochre", ch=1),
    _h("W0", 33.0, 103.0, 47.0, 104.0, 12, 11, 2, "y", ch=1),
    _h("W1", 32.0, 125.0, 51.0, 126.0, 13, 12, 3, "x", "Plaster_VM_Peach", ch=-1, dormer=True),
    _h("W2", 30.0, 142.0, 50.0, 142.0, 11, 10, 2, "y", "Plaster_VM_Ochre", "Roof_VM_Terracotta_B", ch=1),
    # rua oeste (para os portais) e vizinhanca da loja
    _h("R1", -58.0, 76.0, -58.0, 58.0, 14, 11, 2, "x", ch=1),
    _h("R2", -80.0, 87.0, -80.0, 64.0, 13, 11, 3, "y", "Plaster_VM_Peach", ch=-1),
    _h("SH1", 66.0, 70.0, 36.0, 60.0, 13, 11, 2, "y", "Plaster_VM_Ochre", "Roof_VM_Terracotta_B", ch=1),
]

# ------------------------------------------------------------------ LobbyLayout NOVO (ServerScriptService.Core.LobbyLayout)
# posicoes de HumanoidRootPart (~3,3-3,5 acima do piso), como hoje
LOBBY_LAYOUT = {
    "Spawn": (0.0, round(Y_SPAWN + 3.3, 2), 94.0),
    "Shop": (SHOP_PLAYER[0], round(Y_SHOP + 3.5, 2), SHOP_PLAYER[1]),
    "ShopFacing": (SHOP_NPC[0], round(Y_SHOP + 3.5, 2), SHOP_NPC[1]),
    "Ignis": (-0.9, round(Y_NORTH + 3.5, 2), -46.0),      # ~15,1 do belly (prompt 18 / servidor 22)
    "PortalIsland": (-112.0, round(Y_PAVE + 3.5, 2), 72.0),
}
SPAWN_LOBBY_PART = (0.0, round(Y_SPAWN + 0.1, 2), 94.0)        # workspace["Mystical Spawn Point"].SpawnLobby
MAILBOX_POS = (MAILBOX[0], Y_SPAWN, MAILBOX[1])                 # workspace.MailBox (base no piso do terraco)

# ------------------------------------------------------------------ rotas de QA (andador sobre COL_; Roblox X, Z)
SP_FOOT = [(0.0, 94.0), (0.0, 89.0), (0.0, 84.0), (0.0, 79.0)]  # spawn -> pe da escadaria


def routes():
    r = {}
    r["SPAWN->IGNIS"] = (SP_FOOT + [(0, 60), (0, 20), (0, 2), (0, -12), (0, -22), (0, -36), (-0.9, -44.0)], Y_SPAWN)
    r["SPAWN->LOJA"] = (SP_FOOT + [(14, 64), (34, 47), (50, 43), (58, 43), (63, 43), (SHOP_PLAYER[0], 43)], Y_SPAWN)
    r["SPAWN->RANKING"] = (SP_FOOT + [(-20, 62), (-36, 51), (-56, 44), (-70, 38), (-78.0, 34.0)], Y_SPAWN)
    r["SPAWN->CORREIO"] = ([(0.0, 94.0), (-6, 98), (-11.0, 100.0)], Y_SPAWN)
    for i, (k, aid) in enumerate(PORTALS):
        (px, pz), (fx, fz) = portal_pos(i)
        front = (px + fx * 13.0, pz + fz * 13.0)        # pe do terraco (r 43)
        pad = (px + fx * 6.0, pz + fz * 6.0)            # no pad, 6 studs antes da espiral
        disc = (px + fx * 2.6, pz + fz * 2.6)           # encosta no Disco
        mid = (COURT_C[0] + 14.0 * math.cos(math.radians(portal_bearing(i))),
               COURT_C[1] + 14.0 * math.sin(math.radians(portal_bearing(i))))
        r["SPAWN->PORTAL%d_%s" % (aid, k)] = (SP_FOOT + [(-20, 62), (-34, 53)] + WEST_ROAD[1:] +
                                               [(-118, 72), mid, front, pad, disc], Y_SPAWN)
    r["SPAWN->ILHA1"] = (SP_FOOT + [(12, 70)] + EXIT_ROAD + ISLE_BRIDGE[1:-1] + [(0, 221.5)], Y_SPAWN)
    return r


# ------------------------------------------------------------------ cameras (Roblox: posicao, alvo, lente mm)
EYE = 6.5     # camera de 3a pessoa ~1,5 acima da cabeca


def cams():
    c = {}
    # enquadramento da ref_01: na rua curva do sudeste olhando a praca; casas dos dois lados, chamine da forja ao fundo
    c["CAM_VM_Ref_01"] = ((53.0, Y_PAVE + 7.0, 140.0), (30.0, Y_PAVE + 14.0, 64.0), 20)
    c["CAM_VM_P_Spawn"] = ((0.0, Y_SPAWN + EYE + 1.5, 104.0), (0.0, 16.0, 0.0), 22)
    c["CAM_VM_P_Praca"] = ((-16.0, Y_PAVE + EYE, 70.0), (2.0, 13.0, 20.0), 20)
    c["CAM_VM_P_Rua"] = ((4.0, Y_PAVE + EYE, 20.0), (0.0, 18.0, -60.0), 22)
    c["CAM_VM_P_Forja"] = ((6.0, Y_NORTH + EYE, -32.0), (-1.0, 17.0, -62.0), 20)
    c["CAM_VM_P_Loja"] = ((40.0, Y_PAVE + EYE, 46.0), (78.0, 11.0, 43.0), 20)
    c["CAM_VM_P_Ranking"] = ((-60.0, Y_PAVE + EYE, 58.0), (-86.0, 15.0, 18.0), 20)
    c["CAM_VM_P_Portais"] = ((-98.0, Y_PAVE + EYE, 72.0), (-180.0, 15.0, 72.0), 18)
    c["CAM_VM_P_Saida"] = ((51.0, Y_PAVE + EYE, 141.0), (10.0, 7.0, 214.0), 20)     # no portao, olhando a ponte
    c["CAM_VM_Air_Sul"] = ((40.0, 170.0, 290.0), (-20.0, 0.0, 10.0), 24)
    c["CAM_VM_Air_Oeste"] = ((-330.0, 150.0, 120.0), (-20.0, 0.0, 20.0), 24)
    c["CAM_VM_Air_Norte"] = ((60.0, 150.0, -300.0), (0.0, 0.0, 40.0), 24)
    return c


# camera ortografica de cima, no MESMO recorte da planta aprovada (1200 x 1140 px, 0,316 stud/px)
PLAN_PX = (1200, 1140)
PLAN_SCALE = 0.3159
PLAN_CENTER = ((600 - 600) * PLAN_SCALE, 94.0 + (570 - 840) * PLAN_SCALE)     # centro da imagem em Roblox (X, Z)
PLAN_W = PLAN_PX[0] * PLAN_SCALE


def plan_px(x, z):
    """Roblox (X, Z) -> pixel da planta aprovada"""
    return (600 + x / PLAN_SCALE, 840 + (z - 94.0) / PLAN_SCALE)


# ------------------------------------------------------------------ orcamento (PLANO_VM secao 7)
BUDGET_OWNER = {"terrain": (40000, 60), "backdrop": (12000, 6), "town": (40000, 50), "houses": (90000, 180),
                "forge": (60000, 60), "services": (40000, 50), "portals": (110000, 160), "exit": (18000, 24),
                "water": (6000, 12), "vegetation": (40000, 50)}
BUDGET = {"static_tris": 450000, "static_meshes": 600, "vfx_tris": 12000, "vfx_meshes": 24, "total_tris": 462000,
          "total_meshes": 624, "materials": 110, "shadow_meshes": 300, "day_lights": 30, "col": 900}
