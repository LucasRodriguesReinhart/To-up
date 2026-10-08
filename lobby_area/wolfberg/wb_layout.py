# wb_layout - PLANTA do lobby WOLFBERG (Vila da Forja). Tudo em coordenadas ROBLOX (origem do place, 1 BU = 1 stud):
#   X = leste, Z = sul (as ilhas seguem em +Z), Y = cima. A forja fica ao NORTE (-Z); o spawn olha -Z para ela.
#   Blender = (X, -Z, Y). Este arquivo NAO importa bpy.
#
# PARTIDO (ver DIRECAO_WB.md): UM eixo (X = 0) e UMA praca. Norte: Forja do Ignis (marco, 2 fornalhas de pedra abertas
# para a praca). Praca da Forja em volta: fonte a oeste, barracas de mercado a leste, cerca de madeira e placa
# "Bem-vindo a Wolfberg" ao sul (spawn logo atras da placa, olhando a forja = o enquadramento da referencia).
# Leste da praca: Loja de Mochilas (predio proprio, com interior). Oeste: Mural dos Campeoes (Top 100) em loggia de
# pedra. Sudoeste pela rua: Caminho dos Mundos (os 6 portais aprovados). Sul pela rua: portao da vila e ponte reta
# ate a Ilha 1 (z 222, piso 6). Nada de canal, nada de bancos na frente dos portais, nada dentro de casa.
import math

# ------------------------------------------------------------------ cotas (Y Roblox)
Y_PAVE = 7.0           # praca, ruas, piso da forja (contrato do Ignis: piso Y = 7) - UM nivel so
Y_GRASS = 6.8
Y_SHOP = 7.4           # piso da loja (1 soleira de 0,4)
Y_RANK = 7.6           # palco do Mural dos Campeoes (1 degrau de 0,6)
Y_PORTAL = 8.2         # terraco dos portais (2 degraus de 0,6) = cota T do pad dos portais aprovados
Y_WATER = 2.2          # lago em volta do plato
Y_BED = -2.0
Y_ISLE = 6.0           # fim da ponte = praca de chegada da Ilha 1 (z 222)
WALK = 16.0

# ------------------------------------------------------------------ plato (ilha da vila; contorno andavel)
PLATEAU = [(-76, -132), (40, -136), (96, -120), (126, -84), (134, -30), (130, 40), (118, 96), (86, 136), (40, 152),
           (-30, 154), (-80, 148), (-120, 156), (-175, 148), (-214, 114), (-232, 64), (-226, 10), (-190, -34),
           (-136, -72), (-100, -112)]      # sudoeste alargado: o patio dos portais (r 74 de (-134, 62)) cabe inteiro
PLATEAU_BOTTOM = -40.0
LAKE_R = 420.0                       # borda externa do lago (depois vem a margem distante / colinas)

# ------------------------------------------------------------------ eixo e spawn
SPAWN = (0.0, 32.0)                  # na praca, logo atras (norte) da cerca de boas-vindas, olhando a forja (-Z)
FENCE_Z = 40.0                       # linha da cerca sul da praca (abertura x -7..7)
FENCE_X = (-40.0, 44.0)
FENCE_GAP = 7.0
SIGN = (13.0, 42.5)                  # placa "BEM-VINDO A WOLFBERG" (2 faces), ao lado da abertura
MAILBOX = (-15.0, 36.0)              # correio (workspace.MailBox) junto ao spawn, olhando leste
SIGNPOST = (19.0, 24.0)              # poste de direcoes (Forja / Loja / Campeoes / Mundos / Ilhas)

# ------------------------------------------------------------------ praca da forja (poligono organico, paralelepipedo)
PLAZA = [(-40, -40), (40, -40), (48, -34), (54, -26), (54, 8), (50, 40), (-40, 40)]      # convexo; a forja comeca em z -40
FOUNTAIN = (-26.0, 8.0)              # fonte (oeste, como na referencia)
FOUNTAIN_R = 7.0
STALLS = [  # (x, z, olha para (dx, dz), lona)                                  barracas a leste
    (34.0, 24.0, (-1, 0), "WB_CanvasRed"),
    (44.0, 4.0, (-1, 0), "WB_CanvasBlue"),
    (36.0, -16.0, (-1, 0), "WB_CanvasGreen"),
]
CART = (-30.0, -32.0, (1, 0))        # carroca com barris (encostada no canto NW da praca)
OAKS = [(-30.0, 50.0), (56.0, 48.0), (-13.0, 50.0), (12.0, 108.0), (-14.0, 113.0), (-56.0, 96.0), (-100.0, 24.0),
        (86.0, -8.0)]

# ------------------------------------------------------------------ FORJA DO IGNIS (marco). Contrato do golem: EXATO.
IGNIS_ROOT = (-0.9, 7.0, -60.7)
IGNIS_ANVIL = (-0.9, 7.0, -55.7)
IGNIS_BELLY_Y = 13.79
IGNIS_ENV = ((-9.9, 7.0, -64.7), (6.1, 31.0, -52.7))        # envoltoria LIVRE do golem (nada dentro)
IGNIS_FRONT = ((-9.9, 7.0, -52.7), (6.1, 13.0, -40.0))      # chao livre e plano na cota 7 diante do golem
LETREIRO_Y = 20.0
FORGE = dict(x0=-26.0, x1=26.0, z_front=-46.0, z_back=-86.0)   # salao: 52 x 40; vao central aberto x -12..12
FORGE_BAY = (-12.0, 12.0)            # vao do Ignis (aberto, sem parede, pe-direito livre ate 33)
FORGE_TIE_Y = 33.0                   # tirantes / verga do vao (acima da envoltoria 31)
FORGE_EAVE_Y = 36.0                  # bloco central (oitao para a praca); alas com meia-agua (beiral 24,5)
FORGE_RIDGE_Y = 54.6
FORGE_WING_EAVE_Y = 24.5
FORGE_BAY_HALF = 13.0
HEARTHS = [(-19.0, -50.0), (19.0, -50.0)]      # 2 fornalhas de pedra em arco, abertas para a praca (+Z), fogo dentro
HEARTH_W, HEARTH_H = 8.0, 9.0
CHIMNEYS = [(-19.0, -64.0), (19.0, -64.0)]
CHIMNEY_TOP = 64.0
FORGE_SIGN = (0.0, -46.0, 38.5)      # letreiro "FORJA DE WOLFBERG" na viga alta do vao
FORGE_YARD = [(-40, -46), (-27, -46), (-27, -92), (-40, -92)]
FORGE_FLOOR = [(-27, -40), (27, -40), (27, -86), (-27, -86)]   # piso de lajes do salao (cota 7)     # quintal oeste (lenha, carvao)
FORGE_YARD_E = [(27, -46), (40, -46), (40, -92), (27, -92)]       # quintal leste (barris de tempera, estabulo)

# ------------------------------------------------------------------ LESTE: Loja de Mochilas (predio proprio, interior)
SHOP = dict(x0=54.0, x1=80.0, z0=-22.0, z1=4.0)                  # 26 x 26; porta na face OESTE (praca)
SHOP_DOOR = (54.0, -9.0)
SHOP_DOOR_W, SHOP_DOOR_H = 6.0, 9.0
SHOP_WINDOW = (54.0, -18.5, -12.5)   # vitrine na face oeste (x, z0, z1)
SHOP_NPC = (72.0, -9.0)              # 'npc vendedor ' atras do balcao, olhando -X
SHOP_COUNTER_X = 67.0
SHOP_PLAYER = (62.0, -9.0)           # jogador / PadLoja (na frente do balcao)
SHOP_WALL_H = 13.0                   # pe-direito do terreo (interior)
SHOP_EAVE_Y = Y_SHOP + 22.0

# ------------------------------------------------------------------ OESTE: Mural dos Campeoes (GlobalTop100)
RANK_O = (-58.0, -11.0)               # origem do GlobalTop100 (GroundPivot); quadros no plano local z=0
RANK_FACE = (1.0, 0.0)               # +Z local (visitantes) = leste (praca)
TOP100_HALF_W = 27.0                 # 2 quadros de 26 (x +-13,4)
TOP100_DEPTH = (-1.2, 13.2)          # quadros em z 0 .. podios ate z 12,4 (referencial local)
TOP100_H = 26.5
RANK_WALL = dict(x0=-64.0, x1=-58.0, z0=-42.0, z1=20.0, top=Y_RANK + 31.0)    # muro de pedra de fundo
RANK_STAGE = [(-60, -42), (-41, -42), (-41, 20), (-60, 20)]                  # palco (cota Y_RANK)
RANK_ROOF = dict(x0=-66.0, x1=-40.0, z0=-44.0, z1=22.0, eave=Y_RANK + 32.0, ridge=Y_RANK + 40.0)
RANK_BOX = [(-66, -44), (-40, -44), (-40, 22), (-66, 22)]                    # pegada total (checagem)

# ------------------------------------------------------------------ SUDOESTE: Caminho dos Mundos (portais aprovados)
WEST_ROAD = [(-40.0, 34.0), (-66.0, 44.0), (-86.0, 54.0), (-100.0, 62.0)]   # termina no vao do portico (z 62)
ROAD_W = 14.0
COURT_C = (-134.0, 62.0)
COURT_R = 40.0
COURT_RING = (40.0, 74.0, 85.0, 275.0)        # terraco: r0, r1, angulo0, angulo1 (graus, atan2(dz, dx))
PORTAL_R = 56.0
PORTAL_STEP_DEG = 31.0
PORTALS = [("Naruto", 1), ("DragonBall", 2), ("ShadowGarden", 3), ("DemonSlayer", 4), ("OnePiece", 5),
           ("OnePunchMan", 6)]
COURT_SIGN = (-92.0, 50.0)           # poste "CAMINHO DOS MUNDOS" com 6 setas na entrada do patio


def portal_bearing(i):
    """i = 0..5 -> angulo (graus) do portal em volta do COURT_C. Naruto ao SUL, One Punch Man ao NORTE: quem entra
    pelo leste ve facil -> dificil da esquerda para a direita."""
    return 180.0 + (i - 2.5) * PORTAL_STEP_DEG


def portal_pos(i):
    a = math.radians(portal_bearing(i))
    x, z = COURT_C[0] + PORTAL_R * math.cos(a), COURT_C[1] + PORTAL_R * math.sin(a)
    return (x, z), (-math.cos(a), -math.sin(a))


# ------------------------------------------------------------------ SUL: rua, largo do poco, portao, ponte reta
SOUTH_ROAD = [(0.0, 40.0), (0.0, 142.0)]
SOUTH_ROAD_W = 16.0
WELL = (-9.0, 96.0)                  # poco no larguinho da rua sul
GATE = (0.0, 142.0)                  # portao da vila (2 torres de pedra + arco + portas abertas)
GATE_HW = 8.0
GATE_TOWER_W = 9.0
GATE_TOWER_H = 26.0
BRIDGE = dict(x=0.0, z0=148.0, z1=222.0, w=16.0)      # ponte de pedra reta (desce de 7 para 6)
ISLE_LANDING = (-12.0, 12.0, 213.0, 222.0)
ISLE_LINK = (0.0, Y_ISLE, 222.0)

# ------------------------------------------------------------------ casas (fachadas fechadas, 360 graus)
# id, x, z, olha para (x, z), w (fachada), d (fundo), andares, cumeeira ('x' paralela a fachada | 'y' oitao p/ rua),
# reboco, telha, chamine (+1 direita / -1 esquerda), agua-furtada, balanco do andar, placa (texto)


def _h(i, x, z, tx, tz, w, d, nf, ridge, pl="WB_Plaster", rf="WB_Roof", ch=1, dormer=False, jetty=True, sign=None,
       balcony=False, y=Y_PAVE):
    return dict(id=i, x=x, z=z, fx=tx - x, fz=tz - z, w=w, d=d, floors=nf, ridge=ridge, plaster=pl, roof=rf,
                chimney=ch, dormer=dormer, jetty=jetty, sign=sign, balcony=balcony, y=y)


HOUSES = [
    # praca: cantos (olham o centro da praca)
    _h("TAV", 58.0, -48.0, 0.0, -10.0, 24, 17, 3, "y", "WB_Plaster_Ochre", "WB_Roof_Dark", ch=1, dormer=True,
       sign="TAVERNA", balcony=True),                                    # taverna (NE), diagonal para a praca
    _h("PAD", -58.0, -58.0, -10.0, -34.0, 20, 15, 2, "x", ch=-1, dormer=True, sign="PADARIA"),   # NW, diagonal
    _h("SW", -46.0, 62.0, -44.0, 44.0, 20, 15, 2, "y", "WB_Plaster_Ochre", ch=1),               # sul da rua oeste
    _h("SE", 66.0, 24.0, 40.0, 14.0, 20, 15, 3, "x", ch=-1, dormer=True, balcony=True),          # leste, ao lado da loja
    # vizinhos da forja (quintais)
    _h("FW", -50.0, -82.0, -26.0, -80.0, 18, 14, 2, "y", "WB_Plaster_Ochre", "WB_Roof_Dark", ch=1),
    _h("FE", 50.0, -80.0, 26.0, -78.0, 20, 14, 2, "x", ch=-1, sign="ESTABULO"),
    # rua oeste (Caminho dos Mundos): dos dois lados
    _h("W1", -80.0, 28.0, -74.0, 44.0, 20, 15, 2, "x", ch=1, dormer=True),
    _h("W2", -72.0, 70.0, -80.0, 50.0, 20, 15, 3, "y", "WB_Plaster_Ochre", "WB_Roof_Dark", ch=-1, balcony=True),
    # rua sul (chegada das ilhas): casas dos dois lados, alternadas, mais perto da rua
    _h("S1W", -22.0, 70.0, 0.0, 70.0, 20, 15, 2, "x", "WB_Plaster_Ochre", ch=1, dormer=True),
    _h("S1E", 22.0, 64.0, 0.0, 64.0, 18, 14, 3, "y", ch=-1, balcony=True),
    _h("S2W", -24.0, 98.0, 0.0, 98.0, 22, 16, 3, "y", ch=1, dormer=True, sign="ALBERGUE"),
    _h("S2E", 22.0, 92.0, 0.0, 92.0, 20, 15, 2, "x", "WB_Plaster_Ochre", "WB_Roof_Dark", ch=-1),
    _h("S3W", -21.0, 126.0, 0.0, 126.0, 18, 14, 2, "y", ch=1),
    _h("S3E", 22.0, 120.0, 0.0, 120.0, 18, 14, 2, "x", "WB_Plaster_Ochre", ch=-1, dormer=True),
]

# ------------------------------------------------------------------ LobbyLayout NOVO (ServerScriptService.Core.LobbyLayout)
LOBBY_LAYOUT = {
    "Spawn": (SPAWN[0], round(Y_PAVE + 3.3, 2), SPAWN[1]),
    "Shop": (SHOP_PLAYER[0], round(Y_SHOP + 3.5, 2), SHOP_PLAYER[1]),
    "ShopFacing": (SHOP_NPC[0], round(Y_SHOP + 3.5, 2), SHOP_NPC[1]),
    "Ignis": (-0.9, round(Y_PAVE + 3.5, 2), -46.0),
    "PortalIsland": (-104.0, round(Y_PAVE + 3.5, 2), 62.0),
}
SPAWN_LOBBY_PART = (SPAWN[0], round(Y_PAVE + 0.1, 2), SPAWN[1])
MAILBOX_POS = (MAILBOX[0], Y_PAVE, MAILBOX[1])

# ------------------------------------------------------------------ rotas de QA (Roblox X, Z)


def routes():
    r = {}
    r["SPAWN->IGNIS"] = ([(0, 32), (0, 10), (0, -20), (0, -40), (-0.9, -46.0)], Y_PAVE)
    r["SPAWN->LOJA"] = ([(0, 32), (20, 10), (40, -6), (52, -9), (56, -9), (SHOP_PLAYER[0], -9)], Y_PAVE)
    r["SPAWN->CAMPEOES"] = ([(0, 32), (-12, 22), (-14, -6), (-30, -20), (-38, -24), (-48, -24)], Y_PAVE)   # vao sul da loggia (quadro FORCA)
    r["SPAWN->CORREIO"] = ([(0, 32), (-8, 34), (-12.0, 36.0)], Y_PAVE)
    for i, (k, aid) in enumerate(PORTALS):
        (px, pz), (fx, fz) = portal_pos(i)
        front = (px + fx * 13.0, pz + fz * 13.0)
        pad = (px + fx * 6.0, pz + fz * 6.0)
        disc = (px + fx * 2.6, pz + fz * 2.6)
        mid = (COURT_C[0] + 14.0 * math.cos(math.radians(portal_bearing(i))),
               COURT_C[1] + 14.0 * math.sin(math.radians(portal_bearing(i))))
        r["SPAWN->PORTAL%d_%s" % (aid, k)] = ([(0, 32), (-30, 34)] + WEST_ROAD[1:] + [(-110, 62), mid, front, pad, disc],
                                               Y_PAVE)
    r["SPAWN->ILHA1"] = ([(0, 32), (0, 44), (0, 100), (0, 140), (0, 150), (0, 200), (0, 221.5)], Y_PAVE)
    return r


# ------------------------------------------------------------------ cameras (Roblox: posicao, alvo, lente mm)
EYE = 6.5


def cams():
    c = {}
    # a REFERENCIA: por cima da cerca/placa, olhando a praca e a forja (sol a sudoeste)
    c["CAM_WB_Ref"] = ((6.0, Y_PAVE + 30.0, 84.0), (-2.0, Y_PAVE + 12.0, -46.0), 26)
    c["CAM_WB_P_Spawn"] = ((0.0, Y_PAVE + 10.0, 45.0), (0.0, Y_PAVE + 8.0, -20.0), 22)
    c["CAM_WB_Frg_Side"] = ((64.0, Y_PAVE + 26.0, -14.0), (0.0, Y_PAVE + 18.0, -66.0), 28)
    c["CAM_WB_P_Praca"] = ((-30.0, Y_PAVE + EYE, 30.0), (10.0, Y_PAVE + 14.0, -40.0), 22)
    c["CAM_WB_P_Forja"] = ((8.0, Y_PAVE + EYE, -28.0), (-2.0, Y_PAVE + 16.0, -62.0), 20)
    c["CAM_WB_P_Loja"] = ((36.0, Y_PAVE + EYE, 0.0), (66.0, Y_PAVE + 10.0, -9.0), 22)
    c["CAM_WB_I_Loja"] = ((57.0, Y_SHOP + 5.0, -9.0), (74.0, Y_SHOP + 4.5, -9.0), 20)       # dentro da loja
    c["CAM_WB_P_Campeoes"] = ((-10.0, Y_PAVE + 9.0, 6.0), (-58.0, Y_PAVE + 18.0, -11.0), 24)
    c["CAM_WB_P_Mundos"] = ((-96.0, Y_PAVE + EYE, 56.0), (-150.0, Y_PAVE + 14.0, 62.0), 18)
    c["CAM_WB_P_RuaSul"] = ((4.0, Y_PAVE + EYE, 50.0), (0.0, Y_PAVE + 10.0, 150.0), 24)
    c["CAM_WB_P_Portao"] = ((0.0, Y_PAVE + EYE, 170.0), (0.0, Y_PAVE + 14.0, 100.0), 24)     # da ponte, olhando a vila
    c["CAM_WB_Air_Sul"] = ((60.0, 190.0, 300.0), (-20.0, 0.0, 0.0), 24)
    c["CAM_WB_Air_Oeste"] = ((-360.0, 170.0, 140.0), (-30.0, 0.0, 20.0), 24)
    c["CAM_WB_Air_Norte"] = ((80.0, 170.0, -320.0), (0.0, 0.0, 30.0), 24)
    return c


# ------------------------------------------------------------------ orcamento (export_wb)
BUDGET_OWNER = {"terrain": (60000, 70), "backdrop": (40000, 20), "town": (110000, 140), "houses": (180000, 240),
                "forge": (80000, 70), "services": (60000, 70), "portals": (110000, 160), "exit": (30000, 30),
                "water": (6000, 8), "vegetation": (70000, 60), "props": (40000, 40)}
BUDGET = {"static_tris": 720000, "static_meshes": 900, "vfx_tris": 12000, "vfx_meshes": 24, "total_tris": 732000,
          "total_meshes": 924, "materials": 120, "shadow_meshes": 360, "day_lights": 30, "col": 1000}
