# lv_floor.py - plataforma do lobby: praca central com medalhao, cruz de eixos,
# aneis de canal com agua, boulevard sul com embutidos azuis, escadarias e bases.
# Alturas: corredor z=0, piso principal z=5, terracos z=8. +Y = norte (Forja).
import math
import importlib
import lvlib
importlib.reload(lvlib)
from lvlib import box, cyl, lathe, torus, ngon_prism, ring_prism, reg_poly, stairs
import lv_kit
importlib.reload(lv_kit)

TAU = math.tau
FLOOR = 5.0      # topo do piso principal
TERR = 8.0       # topo dos terracos
WATER_Z = 3.1    # nivel da agua
BASIN_Z = 0.8    # fundo do canal
ROT8 = TAU / 16  # octogono alinhado (lados nos eixos)

# raios da composicao central
R_PLAZA = 42     # praca central octogonal
R_CAN_IN = 46    # borda interna do canal
R_CAN_OUT = 72   # borda externa do canal
R_OUTER = 86     # plataforma externa

W_WALK_NS = 30   # eixo norte-sul
W_WALK_EW = 18   # eixo leste-oeste
GAZ_ANGLES = [TAU/8, 3*TAU/8, 5*TAU/8, 7*TAU/8]   # diagonais

def _octagon_ring_pts(r):
    return reg_poly(r, 8, ROT8)

def base_platform(out):
    """Plataforma geral + saia. Cobre x -150..150, y -168..130 (terracos a parte)."""
    # aterro geral do sitio: fecha todo vao entre octogono, jardins e terracos
    out.add('STONE', box((306, 316, 9.0), (0, -3, -0.1)))   # topo z=4.4, saia ate -4.6
    # nucleo sob a praca central e canais
    out.add('TRIM', ngon_prism(reg_poly(R_OUTER + 4, 8, ROT8), 4.6, (0, 0, -4.2)))
    # placas dos eixos
    out.add('TRIM', box((W_WALK_NS + 10, 120, 4.6), (0, -100, -1.9)))     # sul ate o portao
    out.add('TRIM', box((W_WALK_NS + 10, 60, 4.6), (0, 75, -1.9)))        # norte ate o terraco
    out.add('TRIM', box((160, W_WALK_EW + 10, 4.6), (0, 0, -1.9)))        # leste-oeste
    # pisos superiores
    # praca central octogonal
    out.add('TILE', ngon_prism(reg_poly(R_PLAZA, 8, ROT8), 4.6, (0, 0, FLOOR - 4.6)))
    # borda da praca: anel de guia dourada + meio-fio
    p_out = _octagon_ring_pts(R_PLAZA + 1.2)
    p_in = _octagon_ring_pts(R_PLAZA - .4)
    out.add('MARB', ring_prism(p_out, p_in, .55, (0, 0, FLOOR - .05)))
    out.add('GOLD', ring_prism(_octagon_ring_pts(R_PLAZA - .5), _octagon_ring_pts(R_PLAZA - 1.1), .12, (0, 0, FLOOR + .01)))
    # plataforma externa (anel entre canal e borda)
    out.add('TILE2', ring_prism(_octagon_ring_pts(R_OUTER), _octagon_ring_pts(R_CAN_OUT), 4.2, (0, 0, FLOOR - 4.2)))
    # paredes do canal
    out.add('STONE', ring_prism(_octagon_ring_pts(R_CAN_OUT + .8), _octagon_ring_pts(R_CAN_OUT - .6), FLOOR - BASIN_Z, (0, 0, BASIN_Z)))
    out.add('STONE', ring_prism(_octagon_ring_pts(R_CAN_IN + .6), _octagon_ring_pts(R_CAN_IN - .8), FLOOR - BASIN_Z, (0, 0, BASIN_Z)))
    # fundo do canal
    out.add('TRIM', ring_prism(_octagon_ring_pts(R_CAN_OUT), _octagon_ring_pts(R_CAN_IN), .8, (0, 0, BASIN_Z - .8)))
    # meio-fio dourado nas bordas do canal
    out.add('GOLD', ring_prism(_octagon_ring_pts(R_CAN_OUT + 1.0), _octagon_ring_pts(R_CAN_OUT + .5), .14, (0, 0, FLOOR + .01)))
    out.add('GOLD', ring_prism(_octagon_ring_pts(R_CAN_IN - .5), _octagon_ring_pts(R_CAN_IN - 1.0), .14, (0, 0, FLOOR + .01)))

def water_ring(out):
    """Agua do canal em anel (sera Glass no Studio)."""
    out.add('WATER', ring_prism(_octagon_ring_pts(R_CAN_OUT - .4), _octagon_ring_pts(R_CAN_IN + .4), .45, (0, 0, WATER_Z - .45)))

def axis_walks(out):
    """Cruz de eixos por cima do canal: aterros solidos N e S, pontes farao L/O."""
    # norte: liga praca ao terraco do spawn
    out.add('TILE', box((W_WALK_NS, 62, 4.6), (0, R_PLAZA + 29, FLOOR - 2.3)))
    # sul: boulevard ate o portao
    out.add('TILE', box((W_WALK_NS, 122, 4.6), (0, -(R_PLAZA + 59), FLOOR - 2.3)))
    # laterais L/O curtas (da praca ate a borda interna do canal) - pontes cruzam o canal
    for s in (-1, 1):
        out.add('TILE', box((10, W_WALK_EW, 4.6), (s * (R_PLAZA + 3), 0, FLOOR - 2.3)))
        # do lado externo do canal ate a plataforma externa
        out.add('TILE', box((16, W_WALK_EW, 4.6), (s * (R_CAN_OUT + 7), 0, FLOOR - 2.3)))
    # guias douradas do eixo N-S (linhas continuas, ref. piso da imagem 3)
    for s in (-1, 1):
        out.add('GOLD', box((.5, 62, .1), (s * (W_WALK_NS/2 - 2.2), R_PLAZA + 29, FLOOR + .03)))
        out.add('GOLD', box((.5, 122, .1), (s * (W_WALK_NS/2 - 2.2), -(R_PLAZA + 59), FLOOR + .03)))
    # faixa azul central do boulevard sul com borda dourada
    out.add('BLUE', box((3.2, 118, .09), (0, -(R_PLAZA + 59), FLOOR + .02)))
    for s in (-1, 1):
        out.add('GOLD', box((.45, 118, .11), (s * 2.05, -(R_PLAZA + 59), FLOOR + .03)))
    # faixa azul tambem no tramo norte
    out.add('BLUE', box((3.2, 58, .09), (0, R_PLAZA + 29, FLOOR + .02)))
    for s in (-1, 1):
        out.add('GOLD', box((.45, 58, .11), (s * 2.05, R_PLAZA + 29, FLOOR + .03)))

def medallion(out):
    """Medalhao central: aneis dourados, faixa azul com padrao, estrela de 8 pontas,
    e monumento de cristal no centro (identidade de mineracao)."""
    z = FLOOR
    # disco base levemente elevado
    out.add('TILE2', cyl(15.5, .22, (0, 0, z), seg=32))
    out.add('GOLD', ring_prism(reg_poly(15.5, 32), reg_poly(14.6, 32), .3, (0, 0, z + .01)))
    out.add('BLUE', ring_prism(reg_poly(14.2, 32), reg_poly(11.8, 32), .27, (0, 0, z + .01)))
    out.add('GOLD', ring_prism(reg_poly(11.5, 32), reg_poly(11.0, 32), .3, (0, 0, z + .01)))
    # raios dourados dentro da faixa azul
    for i in range(16):
        a = i / 16 * TAU
        out.add('GOLD', box((.35, 2.6, .3), (math.cos(a) * 13.0, math.sin(a) * 13.0, z + .07), (0, 0, a + math.pi/2)))
    # estrela de 8 pontas azul
    pts = []
    for i in range(16):
        a = i / 16 * TAU + TAU/32
        r = 10.2 if i % 2 == 0 else 4.6
        pts.append((math.cos(a) * r, math.sin(a) * r))
    out.add('BLUE', ngon_prism(pts, .3, (0, 0, z + .015)))
    out.add('GOLD', ngon_prism([(x*.42, y*.42) for x, y in pts], .34, (0, 0, z + .02)))
    # dais central com cristal
    out.add('MARB', lathe([(6.4, 0), (6.6, .5), (5.6, .8), (5.2, 1.4), (5.6, 1.7), (4.6, 2.0)], (0, 0, z), seg=24))
    out.add('GOLD', torus(4.9, .14, (0, 0, z + 2.05), seg=24, sides=5))
    lv_kit.crystal_cluster(out, (0, 0, z + 2.0), r=2.8, h=12.0, seed=11)
    lv_kit.crystal_cluster(out, (0, 0, z + 1.9), r=4.2, h=5.5, seed=23)
    # 4 postes dourados baixos em volta
    for i in range(4):
        a = i / 4 * TAU + TAU/8
        px, py = math.cos(a) * 8.6, math.sin(a) * 8.6
        out.add('MARB', lathe([(.5, 0), (.62, .2), (.3, .5), (.34, 1.6), (.5, 1.9)], (px, py, z + .28), seg=8))
        out.add('NEON', lvlib.ball(.42, (px, py, z + 2.5), seg=8))
    # ---- embutidos da praca (alem do medalhao) ----
    # anel intermediario
    out.add('GOLD', ring_prism(reg_poly(28.6, 32), reg_poly(28.1, 32), .1, (0, 0, z + .015)))
    out.add('BLUE', ring_prism(reg_poly(27.9, 32), reg_poly(26.7, 32), .09, (0, 0, z + .015)))
    out.add('GOLD', ring_prism(reg_poly(26.5, 32), reg_poly(26.0, 32), .1, (0, 0, z + .015)))
    # faixas diagonais em direcao aos gazebos
    for a in GAZ_ANGLES:
        mx, my = math.cos(a) * 28.5, math.sin(a) * 28.5
        out.add('BLUE', lvlib.box((2.2, 23, .09), (mx, my, z + .02), (0, 0, a + math.pi/2)))
        for sgn in (-1, 1):
            ox, oy = -math.sin(a) * sgn * 1.45, math.cos(a) * sgn * 1.45
            out.add('GOLD', lvlib.box((.4, 23, .11), (mx + ox, my + oy, z + .02), (0, 0, a + math.pi/2)))

def gazebo_islands(out):
    """Plataformas redondas dos gazebos no meio do canal, ligadas por passarelas."""
    R_ISLE = (R_CAN_IN + R_CAN_OUT) / 2   # centro do anel
    for k, a in enumerate(GAZ_ANGLES):
        cx, cy = math.cos(a) * R_ISLE, math.sin(a) * R_ISLE
        # ilha
        out.add('STONE', cyl(12.5, FLOOR - BASIN_Z + .2, (cx, cy, BASIN_Z - .2), seg=24))
        out.add('TILE2', cyl(11.8, .5, (cx, cy, FLOOR - .5), seg=24))
        # passarela ate a praca central
        dx, dy = math.cos(a), math.sin(a)
        L = R_ISLE - R_PLAZA + 2
        mx, my = math.cos(a) * (R_PLAZA + L/2 - 1), math.sin(a) * (R_PLAZA + L/2 - 1)
        out.add('TILE2', box((L, 7.5, 1.6), (mx, my, FLOOR - 1.6), (0, 0, a)))
        # balaustrada da passarela
        for sside in (-1, 1):
            px1 = math.cos(a) * (R_PLAZA + .5) - dy * sside * 4.1
            py1 = math.sin(a) * (R_PLAZA + .5) + dx * sside * 4.1
            px2 = math.cos(a) * (R_ISLE - 11.5) - dy * sside * 4.1
            py2 = math.sin(a) * (R_ISLE - 11.5) + dx * sside * 4.1
            lv_kit.balustrade(out, (px1, py1), (px2, py2), FLOOR - .1, h=2.6)

def south_stairs_and_edge(out):
    """Escadaria do portao sul descendo ao nivel do corredor + bordas da plataforma."""
    # escada: FLOOR(5) -> 0 entre y=-166 e -182, largura 34
    n = 7
    rise = FLOOR / n
    run = 16 / n
    for i in range(n):
        out.add('MARB', box((34, run + .14, rise), (0, -167 - (i + .5) * run, FLOOR - (i + 1) * rise + rise/2), bevel=.05))
    # plintos laterais da escada
    for s in (-1, 1):
        out.add('MARB', box((3, 18, 6.2), (s * 18.5, -175, 2.4), bevel=.15))
        out.add('GOLD', box((3.2, 18.2, .25), (s * 18.5, -175, 5.65)))
        # postes recebendo quem chega do corredor
        lv_kit.lamp_post(out, (s * 18.5, -186, 0), scale=1.1)
    # bordas/saia da plataforma sul (evita "mesa flutuante")
    for s in (-1, 1):
        out.add('STONE', box((6, 120, 11), (s * (W_WALK_NS/2 + 8), -101, -.5)))
    # rodape que fecha o vao entre a praca e o eixo sul
    out.add('STONE', box((W_WALK_NS + 22, 4, 11), (0, -164, -.5)))

def north_terrace(out):
    """Terraco do spawn (z=8) com escadaria larga a partir da praca."""
    y0 = R_PLAZA + 58   # inicio do terraco (y=100)? praca r42 + walk 62 -> y=104
    # plataforma
    out.add('TILE', box((104, 52, 5.0), (0, y0 + 24, TERR - 5.0)))
    out.add('STONE', box((108, 54, 2.2), (0, y0 + 24, TERR - 7.0)))
    # escadaria de acesso (5 -> 8): 4 degraus
    n = 4
    rise = (TERR - FLOOR) / n
    run = 2.2
    for i in range(n):
        out.add('MARB', box((W_WALK_NS + 6, run + .12, rise), (0, y0 - 2 - (n - i - .5) * run, FLOOR + i * rise + rise/2), bevel=.04))
    # plintos da escadaria com postes
    for s in (-1, 1):
        out.add('MARB', box((3.4, n * run + 2.4, 4.2), (s * (W_WALK_NS/2 + 4.4), y0 - 2 - n * run / 2, FLOOR - .4), bevel=.15))
        out.add('GOLD', box((3.6, n * run + 2.6, .22), (s * (W_WALK_NS/2 + 4.4), y0 - 2 - n * run / 2, FLOOR + 3.85)))
    # faixa azul central continua no terraco
    out.add('BLUE', box((3.2, 46, .09), (0, y0 + 23, TERR + .02)))
    for s in (-1, 1):
        out.add('GOLD', box((.45, 46, .11), (s * 2.05, y0 + 23, TERR + .03)))
    # medalhao do spawn: fica no EIXO NORTE (nivel 5), onde o jogador nasce (0, 66)
    out.add('GOLD', ring_prism(reg_poly(6.8, 24), reg_poly(6.0, 24), .12, (0, 66, FLOOR + .02)))
    out.add('BLUE', ring_prism(reg_poly(5.8, 24), reg_poly(4.6, 24), .1, (0, 66, FLOOR + .02)))
    out.add('GOLD', ring_prism(reg_poly(4.4, 24), reg_poly(3.9, 24), .12, (0, 66, FLOOR + .02)))

def side_terraces(out):
    """Terracos leste/oeste (z=8) atras do canal, com escadas a partir do eixo L-O."""
    for s in (-1, 1):
        x0 = R_OUTER + 2   # 88
        out.add('TILE', box((56, 86, 5.0), (s * (x0 + 28), 0, TERR - 5.0)))
        out.add('STONE', box((58, 88, 2.4), (s * (x0 + 28), 0, TERR - 7.2)))
        # escada 5->8 no eixo (sobe afastando-se do centro)
        n = 4
        rise = (TERR - FLOOR) / n
        run = 2.0
        for i in range(n):
            out.add('MARB', box((run + .12, W_WALK_EW + 4, rise), (s * (86 + (i + .5) * run), 0, FLOOR + i * rise + rise/2), bevel=.04))

def garden_aprons(out):
    """Jardins rebaixados flanqueando o boulevard sul (ref: vegetacao densa dos lados)."""
    for s in (-1, 1):
        # canteirao de grama com borda de pedra
        out.add('STONE', box((66, 118, 4.2), (s * 56, -101, FLOOR - 4.4)))
        out.add('GRASS', box((63, 115, .5), (s * 56, -101, FLOOR - .6)))
        out.add('MARB', box((1.4, 118, 1.1), (s * (W_WALK_NS/2 + 1.0), -101, FLOOR - .4), bevel=.1))
    # tambem jardins nos cantos norte (entre terraco do spawn e terracos laterais)
    for s in (-1, 1):
        out.add('STONE', box((58, 44, 4.2), (s * 84, 78, FLOOR - 4.4)))
        out.add('GRASS', box((55, 41, .5), (s * 84, 78, FLOOR - .6)))
