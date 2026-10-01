# fm_layout - planta travada do lobby (1 BU = 1 stud). X leste, Y norte (sentido Konoha), Z cima.
import math

SPAWN_Z = 0.0     # patamar do spawn
FLOOR = 4.0       # vale principal (praca, forja, mina, rio)
MID = 14.0        # ledge intermediario (canal superior + passeio entre portais)
TERR = 30.0       # terraco dos portais

# --- spawn e avenida
SPAWN = (0.0, -104.0, SPAWN_Z)
SPAWN_PAD = (-22, -118, 22, -92)          # x0,y0,x1,y1
# saida SUL para as ilhas (lobby ativo no jogo: Roblox z = -y). Portao no parapeito sul do spawn + ponte ate a praca de
# chegada da Vila da Folha (Area 1, borda em Roblox z 222 com piso em y 6.0). Trecho plano em z0 (sobre a colisao
# invisivel do corredor Lobby_Area1, topo y 0), escadaria de 6 degraus ate 6.2 e patamar encostando na ilha.
ISLES_GATE_HW = 12.0                        # meia largura da abertura / da ponte
ISLES_STAIRS_Y0 = -194.0                    # inicio da escadaria (desce em y = sobe para o sul)
ISLES_STAIRS_N, ISLES_STAIRS_RISE, ISLES_STAIRS_RUN = 6, 1.0334, 4.0
ISLES_END_Y = -222.0                        # borda da praca de chegada da Area 1
AVENUE = (-10, -92, 10, -70)
FRONT_STAIRS_Y0 = -70.0                     # 4 degraus: z0 -> z4, piso 2
FLOOR_SOUTH = -62.0

# --- praca e forja
PLAZA_C = (0.0, -26.0)
PLAZA_R = 30.0
FORGE_FRONT_Y = 4.0
FORGE_HALL = (-20, 4, 20, 22)
FORGE_WING_L = (-34, 6, -20, 32)
FORGE_WING_R = (20, 6, 34, 32)
CHIMNEY = (0.0, 30.0)
CHIMNEY_R = 10.0
CHIMNEY_TOP = 74.0
DAIS_R = 14.0
IGNIS = (0.0, -5.0)         # Ignis entre a lareira e a bigorna
ANVIL = (0.0, -10.0)
PLAYER_IGNIS = (0.0, -20.0)
DAIS_C = (0.0, -2.0)
FL = 5.0                    # piso interno da forja / tablado

# --- rio / roda
POOL = (52, 46, 68, 62)                     # tanque ao pe do vertedouro
RIVER_X = (58.0, 66.0)                      # canal de fuga (corre para -Y)
WHEEL_C = (62.0, 20.0)
WHEEL_R = 9.0
MILL = (42, 12, 54, 28)                     # casa da roda: engrenagens elevam a forca p/ eixo alto -> ala dos foles
SHOP = (26, -51, 50, -27)                   # loja (frente para -X / praca). 24x24 desde 2026-09-24 (era 18x18, apertada)
BRIDGE_MAIN_Y = -18.0
BRIDGE_BACK_Y = 41.0

# --- portais: x, e nome (facil -> dificil, esquerda -> direita) = ordem das areas do jogo (Config.Areas):
# 1 Vila da Folha, 2 Namekusei, 3 Monte Natagumo (Demon Slayer), 4 Jardim das Sombras (Shadow Garden), 5 Grand Line,
# 6 Cidade Z. (Ate 2026-09-24 Shadow Garden vinha antes do Demon Slayer; trocados para bater com as areas.)
PORTAL_X = [-108.0, -76.0, -44.0, 44.0, 76.0, 108.0]
PORTAL_KEYS = ["Naruto", "DragonBall", "DemonSlayer", "ShadowGarden", "OnePiece", "OnePunchMan"]
PORTAL_AREA = {"Naruto": 1, "DragonBall": 2, "DemonSlayer": 3, "ShadowGarden": 4, "OnePiece": 5, "OnePunchMan": 6}
PORTAL_Y = 113.0
FLIGHT1_Y0 = 47.0      # escada 1: y 47 -> 62, z 4 -> 14 (10 x 1.5)
MID_FRONT_Y = 62.0
CANAL_Y = (71.0, 80.0)  # canal superior (ledge MID)
UPPER_FRONT_Y = 80.0
FLIGHT2_Y1 = 100.0     # escada 2: y 80 -> 100, z 14 -> 30 (16 x 1.25)
TERR_BACK_Y = 128.0
SPILL_X = 60.0         # vertedouro: o canal do ledge cai no tanque
WEST_X = -125.0
EAST_X = 135.0

# --- mina (SW): boca na face NE do macico sudoeste, tunel entra para SW
MINE_MOUTH = (-67.0, -43.0)
MINE_DIR = math.radians(225.0)   # direcao para DENTRO do tunel
MINE_W = 14.0
MINE_H = 13.0

# --- limites do vale (poligonos das lajes, sentido anti-horario)
FLOOR_W = [(-52, -62), (58, -62), (58, 46), (52, 46), (52, 62), (-125, 62), (-125, 30), (-110, 0),
           (-92, -18), (-78, -32), (-56, -54)]
FLOOR_E = [(66, -62), (135, -62), (135, 62), (68, 62), (68, 46), (66, 46)]
MINE_FACE = ((-78, -32), (-56, -54))

# --- Konoha: corredor que sai do portal Naruto para +Y
KONOHA_PATH = [(-108, 124), (-108, 152), (-102, 182), (-96, 215), (-94, 250), (-94, 285)]
KONOHA_GORGE = (196.0, 226.0)    # vao com ponte (y)
KONOHA_GATE_Y = 282.0
