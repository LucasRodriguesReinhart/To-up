# sn_layout.py - PLANTA do lobby SANTUARIO DO DEUS-FERREIRO. Coordenadas ROBLOX (origem do place, 1 stud):
#   X = leste, Z = sul (as ilhas seguem em +Z), Y = cima. Blender = (X, -Z, Y). Sem bpy.
# Partido (conceito E da prancha conceitos_lobby_ignis.html): ruinas claras de um templo do deus-ferreiro sobre um
# plato no lago. NORTE: a BIGORNA-TITA (marco central visivel de todo o mapa) e, aos pes dela, a FORJA DO IGNIS
# (ponto do golem fixo). CENTRO: a PRACA DAS RUNAS (circulo de lajes com anel de runas aceso). Em volta, no arco
# norte, a COLUNATA DOS PORTAIS (6 arcos antigos, facil -> dificil da esquerda para a direita). LESTE: o TEMPLO DOS
# MERCADORES (loja de mochilas). OESTE: as TABUAS DOS CAMPEOES (Top 100). SUL: terraco do SPAWN com escadaria,
# avenida de colunas, portao arruinado e a PONTE ANTIGA ate a Ilha 1 (z 222, piso 6). O MARTELO quebrado do deus
# esta cravado a noroeste.
import math

Y_PLAZA = 7.0           # praca, forja (contrato do Ignis: piso Y 7), avenida
Y_GRASS = 6.8
Y_SPAWN = 10.0          # terraco do spawn (5 degraus de 0,6 acima da praca)
Y_PORTAL = 8.2          # estrado dos portais (2 degraus de 0,6)
Y_SHOP = 8.2            # estilobato do templo dos mercadores (2 degraus)
Y_RANK = 7.6            # palco das Tabuas dos Campeoes (1 degrau)
Y_WATER = 2.2
Y_ISLE = 6.0
WALK = 16.0

C = (0.0, 0.0)          # centro da praca das runas
PLAZA_R = 40.0
RUNE_R = (24.0, 28.0)   # anel de runas
MEDAL_R = 10.0

# ------------------------------------------------------------------ IGNIS (contrato do golem: EXATO)
IGNIS_ROOT = (-0.9, 7.0, -60.7)
IGNIS_ANVIL = (-0.9, 7.0, -55.7)
IGNIS_BELLY_Y = 13.79
IGNIS_ENV = ((-9.9, 7.0, -64.7), (6.1, 31.0, -52.7))
IGNIS_FRONT = ((-9.9, 7.0, -52.7), (6.1, 13.0, -40.0))
LETREIRO_Y = 20.0
PLAYER_IGNIS = (-0.9, -46.0)

# ------------------------------------------------------------------ forja (abside) e bigorna-tita
FORGE_C = (0.0, -62.0)          # centro da abside da forja
FORGE_R = (15.0, 18.5)          # raio interno / externo do muro da abside (aberta para o sul)
FORGE_OPEN = (25.0, 155.0)      # arco ABERTO para a praca (graus atan2(dz,dx); sul = 90) - o resto e muro
ANVIL_C = (0.0, -118.0)         # centro da bigorna-tita
ANVIL_L = 120.0                 # comprimento (x), chifre para o leste
ANVIL_H = 62.0                  # altura acima do plinto
ANVIL_PLINTH = (-74.0, 74.0, -142.0, -92.0, 6.0)    # x0, x1, z0, z1, altura do plinto escalonado
HAMMER = dict(head=(-86.0, -78.0), tilt=58.0, yaw=-38.0, head_size=(34.0, 20.0, 20.0), handle_len=96.0, handle_r=3.4)

# ------------------------------------------------------------------ colunata dos portais
PORTAL_R = 55.0
PORTAL_ANG = [192.0, 214.0, 236.0, 304.0, 326.0, 348.0]
PORTALS = [("Naruto", 1), ("DragonBall", 2), ("ShadowGarden", 3), ("DemonSlayer", 4), ("OnePiece", 5),
           ("OnePunchMan", 6)]
PORTAL_W, PORTAL_H = 15.0, 21.0          # vao do arco


def portal_pos(i):
    a = math.radians(PORTAL_ANG[i])
    x, z = C[0] + PORTAL_R * math.cos(a), C[1] + PORTAL_R * math.sin(a)
    return (x, z), (-math.cos(a), -math.sin(a))      # posicao, direcao para onde a espiral olha (o centro)


# ------------------------------------------------------------------ servicos
SHOP_C = (68.0, 18.0)            # templo dos mercadores (centro), olhando para a praca
SHOP_FACE = (-0.96, -0.28)
SHOP_SIZE = (28.0, 22.0)         # frente x fundo
RANK_O = (-64.0, 18.0)           # origem do GlobalTop100 (quadros no plano local z = 0)
RANK_FACE = (0.96, -0.28)        # olha para a praca (leste-nordeste)
TOP100_HALF_W = 27.0
TOP100_DEPTH = (-1.2, 13.2)
TOP100_H = 26.5

# ------------------------------------------------------------------ sul: spawn, avenida, portao, ponte
SPAWN = (0.0, 64.0)
SPAWN_TERRACE = (-22.0, 22.0, 52.0, 80.0)          # x0, x1, z0, z1 (cota Y_SPAWN)
STAIR = dict(x0=-14.0, x1=14.0, z_top=52.0, n=5, rise=0.6, run=1.7)   # desce para -Z ate a praca
MAILBOX = (-13.0, 62.0)
AVENUE = (-11.0, 11.0, 80.0, 146.0)                 # avenida de colunas (cota Y_PLAZA, desce do terraco por rampa)
GATE = (0.0, 148.0)
BRIDGE = dict(x=0.0, z0=152.0, z1=222.0, w=16.0)
ISLE_LINK = (0.0, Y_ISLE, 222.0)

# ------------------------------------------------------------------ plato (ilha no lago)
PLATEAU = [(-60, -164), (60, -164), (112, -138), (142, -90), (150, -30), (146, 40), (124, 96), (72, 140), (20, 150),
           (-20, 150), (-72, 140), (-124, 96), (-146, 40), (-150, -30), (-142, -90), (-112, -138)]
PLATEAU_BOTTOM = -40.0
LAKE_R = 420.0

LOBBY_LAYOUT = {
    "Spawn": (SPAWN[0], round(Y_SPAWN + 3.3, 2), SPAWN[1]),
    "Ignis": (PLAYER_IGNIS[0], round(Y_PLAZA + 3.5, 2), PLAYER_IGNIS[1]),
}


def cams():
    """cameras de avaliacao (Roblox: olho, alvo, lente)"""
    return {
        "CAM_SN_Hero": ((26.0, 26.0, 18.0), (-4.0, 22.0, -88.0), 24),           # praca -> forja + bigorna
        "CAM_SN_Spawn": ((0.0, Y_SPAWN + 7.0, 72.0), (0.0, 22.0, -60.0), 24),   # o que o jogador ve ao nascer
        "CAM_SN_Forge": ((7.0, Y_PLAZA + 6.5, -36.0), (-1.0, 16.0, -70.0), 22), # chegando no Ignis
        "CAM_SN_ForgeClose": ((14.0, Y_PLAZA + 8.0, -44.0), (-4.0, 12.0, -66.0), 26),
        "CAM_SN_Anvil": ((70.0, 40.0, -40.0), (0.0, 40.0, -118.0), 26),
        "CAM_SN_Hammer": ((-40.0, 18.0, -20.0), (-86.0, 30.0, -80.0), 26),
        "CAM_SN_Plaza": ((0.0, 60.0, 44.0), (0.0, 7.0, -4.0), 26),
        "CAM_SN_Air": ((140.0, 170.0, 210.0), (0.0, 10.0, -30.0), 26),
    }
