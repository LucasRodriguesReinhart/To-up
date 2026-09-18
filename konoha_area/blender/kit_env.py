# KONOHA_PROPS / NATURE / ROCKS / MINING / DECORATION kits.
import math
from klib import *
from kit_parts import *

PI = math.pi

# ---------------------------------------------------------------- PROPS
def props():
    C = 'KONOHA_PROPS'
    asset(C, 'Caixote')
    box('Caixa', (0, 0, 1.2), (2.4, 2.4, 2.4), 'wood', col=False)
    for z in (.15, 2.25): box('Cinta', (0, 0, z), (2.55, 2.55, .3), 'wood_dark', col=False)
    rod('Diagonal', (-1, -1.25, .3), (1, -1.25, 2.1), .25, 'wood_light')

    asset(C, 'Barril')
    cyl('Barril', (0, 0, 1.5), 1.2, 3, 'wood', col=False)
    for z in (.4, 2.6): cyl('Aro', (0, 0, z), 1.27, .25, 'metal', col=False)
    cyl('Tampa', (0, 0, 3.02), 1.05, .1, 'wood_dark', col=False)

    asset(C, 'Banca_Mercado')
    box('Balcao', (0, 0, 1.5), (7, 3, 3), 'wood', col=True)
    box('Tampo', (0, 0, 3.1), (7.4, 3.4, .3), 'wood_light', col=False)
    for sx in (-1, 1):
        box('Poste', (sx*3.4, 1.3, 4.5), (.4, .4, 9), 'wood_dark', col=False)
        box('PosteFrente', (sx*3.4, -1.6, 3.8), (.4, .4, 7.6), 'wood_dark', col=False)
    for i in range(4):
        wedge('Toldo', (-2.65 + i*1.77, -.2, 8.2), (1.77, 5, 1.2), 'cloth_red' if i % 2 == 0 else 'cloth_white', (0,0,PI), col=False)
    for k in range(5):
        ball('Fruta', (-2.8 + k*1.4, -.6, 3.7), .9, ['cr_fire', 'cr_lightning', 'foliage_light', 'cr_earth', 'cloth_red'][k])
    box('Placa', (0, -1.75, 7.2), (5, .3, 1.2), 'wood', col=False, text='MERCADO')

    asset(C, 'Banco')
    for x in (-2.2, 2.2): box('Pe', (x, 0, .7), (.5, 1.6, 1.4), 'stone', col=False)
    box('Assento', (0, 0, 1.55), (6, 1.8, .4), 'wood', col=False)

    asset(C, 'Lanterna_Pedra')   # toro
    box('Base', (0, 0, .4), (2.4, 2.4, .8), 'stone', col=False)
    cyl('Haste', (0, 0, 2.2), .55, 2.8, 'stone', col=False)
    box('Suporte', (0, 0, 3.8), (2.2, 2.2, .5), 'stone', col=False)
    box('Luz', (0, 0, 4.8), (1.4, 1.4, 1.5), 'glow', col=False, light='255,190,120,12,0.8')
    wedge('Teto', (0, -.9, 6.0), (2.9, 1.8, .9), 'stone_dark', (0,0,0), col=False)
    wedge('Teto', (0, .9, 6.0), (2.9, 1.8, .9), 'stone_dark', (0,0,PI), col=False)
    ball('Joia', (0, 0, 6.7), .7, 'stone_dark')

    asset(C, 'Poste_Fios')
    cyl('Poste', (0, 0, 9), .45, 18, 'wood_dark', col=False)
    box('Travessa', (0, 0, 16.5), (5, .5, .5), 'wood_dark', col=False)
    for x in (-2, 0, 2): cyl('Isolador', (x, 0, 17), .22, .6, 'cloth_white', col=False)
    cyl('Transformador', (.8, .9, 13.5), .8, 2.2, 'tank', col=False)

    asset(C, 'Placa_Rua')
    box('Poste', (0, 0, 3), (.4, .4, 6), 'wood_dark', col=False)
    box('Placa', (0, -.3, 5), (4.4, .3, 1.8), 'wood_light', col=False, text='>')

    asset(C, 'Cerca')        # 8 studs along X
    for x in (-4, 0, 4): box('Mourao', (x, 0, 1.6), (.5, .5, 3.2), 'wood_dark', col=False)
    for z in (1.1, 2.6): box('Tabua', (0, 0, z), (8.4, .3, .5), 'wood', col=False)
    box('Colisao', (0, 0, 1.6), (8, .6, 3.2), 'invisible', col=True)

    asset(C, 'Ponte_Vermelha')   # spans 30 along Y
    n = 12
    for i in range(n):
        t = (i+.5)/n; y = -15 + 30*t
        z = .3 + math.sin(t*PI)*3.2
        ang = math.cos(t*PI)*math.atan(3.2*PI/30)
        box('Tabuado', (0, y, z), (9, 30/n+.1, .6), 'wood', (-ang,0,0), col=True)
    for sx in (-1, 1):
        for i in range(n+1):
            t = i/n; y = -15 + 30*t; z = .3 + math.sin(t*PI)*3.2
            if i % 3 == 0:
                box('PilarGuarda', (sx*4.4, y, z+1.6), (.7, .7, 3.4), 'roof_red', col=False)
                ball('Pomo', (sx*4.4, y, z+3.5), .8, 'gold')
            if i < n:
                t2 = (i+1)/n; y2 = -15 + 30*t2; z2 = .3 + math.sin(t2*PI)*3.2
                rod('Corrimao', (sx*4.4, y, z+2.8), (sx*4.4, y2, z2+2.8), .45, 'roof_red')
        box('Guarda', (sx*4.4, 0, 4.5), (.4, 30, 3), 'invisible', col=True)
    for sy in (-1, 1):
        box('Pilar', (0, sy*8, -3), (8, 1.6, 7), 'stone', col=True)

    asset(C, 'Ponte_Madeira')    # 22 along Y
    for i in range(11):
        box('Tabua', (0, -10 + i*2, .25), (7, 1.9, .5), 'wood' if i % 2 else 'wood_light', col=True)
    for sx in (-1, 1):
        for y in (-10, -3, 4, 11):
            box('Poste', (sx*3.4, y, 1.8), (.5, .5, 3.4), 'wood_dark', col=False)
        box('Corrimao', (sx*3.4, .5, 3.3), (.35, 22, .35), 'wood', col=False)
        box('Guarda', (sx*3.4, .5, 2), (.3, 22, 3), 'invisible', col=True)

    asset(C, 'Poste_Treino')
    cyl('Tronco', (0, 0, 3), 1.1, 6, 'trunk', col=True)
    cyl('Topo', (0, 0, 6.05), 1.0, .1, 'wood_light', col=False)
    for z in (2.2, 4.2): cyl('Faixa', (0, 0, z), 1.15, .35, 'rope', col=False)
    box('Marca', (0, -1.12, 3.2), (.8, .1, 1.2), 'cloth_white', col=False)

    asset(C, 'Alvo_Treino')
    for x in (-1.6, 1.6): box('Pe', (x, 0, 2.8), (.4, .4, 5.6), 'wood_dark', col=False)
    cyl('Alvo', (0, 0, 4.4), 2.3, .4, 'cloth_white', axis='Y', col=False)
    cyl('Anel', (0, -.12, 4.4), 1.6, .4, 'cloth_red', axis='Y', col=False)
    cyl('Centro', (0, -.24, 4.4), .7, .4, 'cloth_red', axis='Y', col=False)
    box('Kunai', (.5, -.6, 4.6), (.2, 1.4, .2), 'metal', (0, 0, .3), col=False)

# ---------------------------------------------------------------- NATURE
def canopy(center, r, rs, mats, n=6):
    cx, cy, cz = center
    ball('Copa', (cx, cy, cz), r*2, mats[0])
    for i in range(n):
        a = i/n*2*PI + rs.uniform(-.3, .3)
        rr = r*rs.uniform(.55, .8)
        ball('Copa', (cx+math.cos(a)*r*.75, cy+math.sin(a)*r*.75, cz+rs.uniform(-r*.35, r*.2)), rr*2, mats[(i+1) % len(mats)])
    ball('CopaTopo', (cx+rs.uniform(-1, 1), cy+rs.uniform(-1, 1), cz+r*.7), r*1.3, mats[-1])

def nature():
    C = 'KONOHA_NATURE'
    rs = rng(11)
    asset(C, 'Arvore_Folha_G')
    cyl('Tronco', (0, 0, 7), 1.5, 14, 'trunk', col=True)
    for a in (0, 2.1, 4.2):
        rod('Raiz', (0, 0, 1.6), (math.cos(a)*3.4, math.sin(a)*3.4, .1), 1.1, 'trunk', h=1.1)
    rod('Galho', (0, 0, 10), (4, 1, 15), .9, 'trunk')
    rod('Galho', (0, 0, 11), (-3.5, -1.5, 15.5), .9, 'trunk')
    canopy((0, 0, 17.5), 6.5, rs, ['foliage', 'foliage_dark', 'foliage', 'foliage_light'], 6)

    asset(C, 'Arvore_Folha_M')
    cyl('Tronco', (0, 0, 4.5), 1.0, 9, 'trunk', col=True)
    rod('Galho', (0, 0, 6.5), (2.5, -.8, 9.5), .7, 'trunk')
    canopy((0, 0, 11.5), 4.4, rs, ['foliage_dark', 'foliage', 'foliage_light'], 5)

    asset(C, 'Arvore_Gigante')
    cyl('Tronco', (0, 0, 22), 4.2, 44, 'trunk', col=True)
    for a in (0, 1.3, 2.5, 3.8, 5.1):
        rod('Raiz', (0, 0, 5), (math.cos(a)*9, math.sin(a)*9, .5), 2.4, 'trunk', h=2.4)
    for a, z in ((.4, 30), (2.6, 34), (4.5, 28)):
        rod('Galho', (0, 0, z), (math.cos(a)*12, math.sin(a)*12, z+9), 2.0, 'trunk')
    canopy((0, 0, 48), 15, rs, ['foliage_dark', 'foliage', 'foliage_dark', 'foliage_light'], 7)

    asset(C, 'Cedro')
    cyl('Tronco', (0, 0, 6), .9, 12, 'trunk', col=True)
    for i, (r, z) in enumerate(((5.5, 6), (4.6, 9.5), (3.6, 13), (2.4, 16), (1.2, 18.5))):
        cyl('Camada', (0, 0, z), r, 3.0, 'foliage_dark' if i % 2 == 0 else 'foliage', col=False)

    asset(C, 'Arbusto')
    ball('Arbusto', (0, 0, 1.6), 3.6, 'foliage')
    ball('Arbusto', (1.6, .6, 1.2), 2.6, 'foliage_dark')
    ball('Arbusto', (-1.4, -.4, 1.1), 2.4, 'foliage_light')

    asset(C, 'Tufo')
    for i in range(4):
        a = i * PI/2 + .4
        wedge('Folha', (math.cos(a)*.4, math.sin(a)*.4, .8), (.5, .9, 1.6), 'grass_dark' if i % 2 else 'foliage_light', (0, 0, a+PI/2), col=False)

    asset(C, 'Canteiro_Flores')
    box('Borda', (0, 0, .4), (8, 4, .8), 'stone', col=False)
    box('Terra', (0, 0, .75), (7.4, 3.4, .3), 'dirt_dark', col=False)
    for i in range(6):
        x = -3 + i*1.2
        ball('Folhagem', (x, rs.uniform(-.8, .8), 1.4), 1.3, 'foliage')
        ball('Flor', (x+.2, rs.uniform(-.8, .8), 2.0), .7, ['cr_fire', 'cloth_white', 'cr_lightning', 'cr_rare'][i % 4])

# ---------------------------------------------------------------- ROCKS
def rock(name, rs, s, m1='cliff', m2='cliff_dark', col=True, pieces=5):
    box('Nucleo', (0, 0, s*.45), (s*1.1, s*.9, s*.9), m1, (0, 0, rs.uniform(0, PI)), col=col)
    for i in range(pieces):
        a = i/pieces*2*PI + rs.uniform(-.4, .4)
        d = s*rs.uniform(.35, .55)
        sz = s*rs.uniform(.5, .8)
        box('Faceta', (math.cos(a)*d, math.sin(a)*d, sz*.4), (sz, sz*.85, sz*.8), m2 if i % 2 else m1,
            (rs.uniform(-.35, .35), rs.uniform(-.35, .35), a), col=False)
    wedge('Topo', (0, 0, s*.95), (s*.8, s*.7, s*.35), m1, (0, 0, rs.uniform(0, PI)), col=False)

def rocks():
    C = 'KONOHA_ROCKS'
    rs = rng(21)
    asset(C, 'Rocha_S'); rock('S', rs, 2.2, 'stone', 'stone_dark', col=False, pieces=3)
    asset(C, 'Rocha_M'); rock('M', rs, 5, 'cliff', 'cliff_dark')
    asset(C, 'Rocha_L'); rock('L', rs, 10, 'cliff', 'cliff_dark', pieces=6)
    asset(C, 'Rocha_Musgo')
    rock('Mg', rs, 6, 'stone', 'stone_dark')
    box('Musgo', (0, 0, 6.1), (5, 4, .6), 'grass', (0, 0, .4), col=False)
    asset(C, 'Rochedo_Veio')        # boulder with glowing chakra veins
    rock('V', rs, 8, 'stone', 'stone_dark', pieces=5)
    for i in range(4):
        a = i*PI/2 + .3
        box('VeioChakra', (math.cos(a)*4.1, math.sin(a)*4.1, 3 + i*.6), (.35, 3.2, .5), 'cr_chakra', (rs.uniform(-.8, .8), 0, a), col=False)

# ---------------------------------------------------------------- MINING
ELEMENTS = {'Chakra': 'cr_chakra', 'Fogo': 'cr_fire', 'Vento': 'cr_wind', 'Raio': 'cr_lightning',
            'Terra': 'cr_earth', 'Agua': 'cr_water', 'Raro': 'cr_rare'}

def crystal(x, y, z, h, w, m, tilt=(0, 0), yaw=0.0):
    rot = (tilt[0], tilt[1], yaw)
    from mathutils import Euler, Vector
    R = Euler(rot, 'XYZ').to_matrix()
    base = Vector((x, y, z))
    box('Cristal', base + R @ Vector((0, 0, h/2)), (w, w, h), m, rot, col=False)
    tip = R @ Vector((0, 0, h + w*.45))
    Rz = Euler(rot, 'XYZ')
    wedge('PontaCristal', base + tip + R @ Vector((0, -w/4, 0)), (w, w/2, w*.9), m, rot, col=False)
    from mathutils import Matrix
    R2 = (R @ Euler((0, 0, PI), 'XYZ').to_matrix()).to_euler('XYZ')
    wedge('PontaCristal', base + tip + R @ Vector((0, w/4, 0)), (w, w/2, w*.9), m, tuple(R2), col=False)

def crystal_cluster(name, m, rs, scale=1.0):
    asset('KONOHA_MINING', name)
    s = scale
    box('BaseRocha', (0, 0, .8*s), (4.5*s, 4*s, 1.6*s), 'stone_dark', (0, 0, .3), col=False)
    crystal(0, 0, 1*s, 6.5*s, 1.8*s, m, (0, 0), .2)
    for i in range(4):
        a = i/4*2*PI + .5
        crystal(math.cos(a)*1.6*s, math.sin(a)*1.6*s, .9*s, rs.uniform(2.6, 4.2)*s, rs.uniform(1.0, 1.4)*s, m,
                (math.sin(a)*.45, -math.cos(a)*.45), a)

def mining():
    C = 'KONOHA_MINING'
    rs = rng(31)
    for el, m in ELEMENTS.items():
        crystal_cluster('Cristal_' + el, m, rs, 1.0)
    crystal_cluster('Cristal_Chakra_G', 'cr_chakra', rs, 2.4)
    crystal_cluster('Cristal_Raro_G', 'cr_rare', rs, 2.0)

    asset(C, 'Escora_Mina')      # frame 14 wide, 14 tall
    for x in (-6.5, 6.5):
        box('Pilar', (x, 0, 7), (1.6, 1.6, 14), 'wood', col=True)
        rod('MaoFrancesa', (x, 0, 10), (x*.6, 0, 13.4), .8, 'wood_dark')
    box('Viga', (0, 0, 14.4), (16, 1.9, 1.9), 'wood', col=True)
    box('Placa', (0, -1.1, 16.4), (8, .4, 2.2), 'wood_dark', col=False, text='MINA')

    asset(C, 'Trilho')           # 8 along Y
    for y in (-3, 0, 3): box('Dormente', (0, y, .15), (5.2, .8, .3), 'wood_dark', col=False)
    for x in (-1.8, 1.8): box('Trilho', (x, 0, .45), (.3, 8.05, .35), 'metal', col=False)

    asset(C, 'Vagoneta')
    box('Cacamba', (0, 0, 2.2), (4, 5.4, 2.4), 'stone_dark', col=True)
    box('Borda', (0, 0, 3.45), (4.3, 5.7, .3), 'metal', col=False)
    for x in (-1.9, 1.9):
        for y in (-1.8, 1.8): cyl('Roda', (x, y, .9), .8, .5, 'trim_dark', axis='X', col=False)
    for i in range(4):
        box('Minerio', (rs.uniform(-1, 1), rs.uniform(-1.6, 1.6), 3.8), (1.4, 1.4, 1.2), 'ore_rock', (rs.uniform(0, 1), rs.uniform(0, 1), 0), col=False)
    crystal(0, .6, 3.4, 1.4, .8, 'cr_chakra', (.3, .2), 0)

    asset(C, 'Guindaste')
    box('Base', (0, 0, .8), (6, 6, 1.6), 'stone', col=True)
    box('Mastro', (0, 0, 11), (1.6, 1.6, 20), 'wood', col=True)
    rod('Lanca', (0, 0, 19), (0, -16, 23), 1.2, 'wood')
    rod('Tirante', (0, 0, 21.5), (0, -16, 23.4), .25, 'rope')
    rod('Corda', (0, -15.5, 23), (0, -15.5, 10), .2, 'rope')
    box('Balde', (0, -15.5, 8.8), (2.6, 2.6, 2.4), 'wood_dark', col=False)
    box('Pedras', (0, -15.5, 10.1), (2.2, 2.2, .7), 'ore_rock', col=False)
    rod('Contrapeso', (0, 0, 19), (0, 5, 18.5), 1.0, 'wood')
    box('Peso', (0, 5, 17.3), (2.4, 2.4, 2.4), 'stone_dark', col=False)
    cyl('Manivela', (1.4, 0, 4), 1.1, .8, 'wood_dark', axis='X', col=False)

    asset(C, 'Andaime')          # 10 wide along X, 3 levels, against a wall at +Y
    for x in (-5, 5):
        for y in (-1.5, 1.5): box('Poste', (x, y, 7.5), (.5, .5, 15), 'wood', col=False)
    for z in (5, 10, 15):
        box('Plataforma', (0, 0, z), (10.6, 3.6, .4), 'wood_light', col=True)
        box('Guarda', (0, -1.6, z+1.3), (10.6, .25, .3), 'wood_dark', col=False)
    rod('Escada', (-3.5, -1, 0), (-3.5, 1, 15), .5, 'wood_dark', h=1.4)

    asset(C, 'Pilha_Minerio')
    for i in range(7):
        a = i/7*2*PI
        box('Pedra', (math.cos(a)*1.6, math.sin(a)*1.6, .7), (1.8, 1.6, 1.4), 'ore_rock' if i % 2 else 'stone_dark', (rs.uniform(0, 1), rs.uniform(0, 1), a), col=False)
    box('PedraTopo', (0, 0, 1.8), (2, 2, 1.6), 'ore_rock', (.4, .3, .2), col=False)
    crystal(.4, -.3, 2.2, 1.6, .7, 'cr_chakra', (.3, 0), .4)

    asset(C, 'Lanterna_Mina')
    box('Poste', (0, 0, 3), (.45, .45, 6), 'wood_dark', col=False)
    rod('Braco', (0, 0, 5.8), (0, -1.6, 5.8), .3, 'wood_dark')
    box('Lampiao', (0, -1.6, 4.9), (.9, .9, 1.3), 'glow', col=False, light='255,190,110,14,0.9')
    box('TetoLampiao', (0, -1.6, 5.7), (1.2, 1.2, .3), 'trim_dark', col=False)

# ---------------------------------------------------------------- DECORATION
def decoration():
    C = 'KONOHA_DECORATION'
    asset(C, 'Estandarte_Folha')
    box('Mastro', (0, 0, 7), (.5, .5, 14), 'wood_dark', col=False)
    rod('Travessa', (-2.2, -.3, 13), (2.2, -.3, 13), .35, 'wood_dark')
    box('Pano', (0, -.4, 9.4), (3.8, .15, 7), 'cloth_red', col=False, emblem='leaf', sway=1)
    box('Barra', (0, -.4, 5.8), (4, .3, .3), 'gold', col=False)

    asset(C, 'Fio_Lanternas')   # 20 along X, hung at z 11
    for sx in (-10, 10): box('Suporte', (sx, 0, 5.5), (.4, .4, 11), 'wood_dark', col=False)
    rod('Fio', (-10, 0, 10.8), (0, 0, 9.6), .12, 'trim_dark')
    rod('Fio', (0, 0, 9.6), (10, 0, 10.8), .12, 'trim_dark')
    for i, x in enumerate((-6.5, -2, 2, 6.5)):
        z = 10.8 - (1 - abs(x)/10) * 1.2 - 1.0
        paper_lantern(x, 0, z, 'lantern' if i % 2 == 0 else 'cloth_white', light=(i == 1))

    asset(C, 'Vaso_Planta')
    cyl('Vaso', (0, 0, .7), .9, 1.4, 'roof_orange', col=False)
    ball('Planta', (0, 0, 2), 2.0, 'foliage')

    asset(C, 'Painel_Folha')     # large carved leaf emblem plate
    box('Moldura', (0, 0, 3), (6.4, .6, 6.4), 'wood_dark', col=False)
    box('Placa', (0, -.2, 3), (5.6, .5, 5.6), 'wall_cream', col=False, emblem='leaf')

def build_all():
    props(); nature(); rocks(); mining(); decoration()
