# DRAGONBALL_BUILDINGS: West City / Capsule-style rounded architecture.  Origin = ground centre, front = -Y.
from dblib import *
from kit_db_tech import capsule_x, capsule_y

def sphere_r_at(R, dz):
    return math.sqrt(max(R*R - dz*dz, 0.0))

def round_door(name, x, y, z, w, h, m_frame='cc_white', m_door='cc_navy', facing=-PI/2):
    """Door with a rounded top on a wall facing `facing` (default -Y)."""
    ca, sa = math.cos(facing), math.sin(facing)
    rz = facing + PI/2
    box(name + 'Moldura', (x, y, z + h*.4), (w + .8, 1.2, h*.8), m_frame, (0, 0, rz), False)
    cyl(name + 'MolduraArco', (x, y, z + h*.8), w/2 + .4, 1.2, m_frame, 'Y', False, rot=(0, 0, facing + PI/2))
    box(name, (x + ca*.3, y + sa*.3, z + h*.4), (w, 1.2, h*.8), m_door, (0, 0, rz), False)
    cyl(name + 'Arco', (x + ca*.3, y + sa*.3, z + h*.8), w/2, 1.2, m_door, 'Y', False, rot=(0, 0, facing + PI/2))
    box(name + 'Degrau', (x + ca*1.2, y + sa*1.2, .2), (w + 2, 2, .4), 'cc_grey', (0, 0, rz), False)

def dome_house(nm, R, wall, roof, accent, windows=4, extra=None, seed=1):
    asset('DRAGONBALL_BUILDINGS', nm)
    zc = -R*.2
    ball('Cupula', (0, 0, zc), R*2, wall, col=True)
    disc('Rodape', (0, 0, .6), sphere_r_at(R, .6 - zc) + .25, 1.2, accent, False)
    disc('FaixaCor', (0, 0, R*.55), sphere_r_at(R, R*.55 - zc) + .15, 1.0, accent, False)
    capz = zc + R*.95
    disc('Tampa', (0, 0, capz), sphere_r_at(R, capz - zc) + .1, .8, roof, False)
    ball('TampaTopo', (0, 0, capz + .3), sphere_r_at(R, capz - zc)*1.3, roof)
    dz = 2.2 - zc
    round_door('Porta', 0, -sphere_r_at(R, dz) + .2, 0, 2.6, 4.6)
    wz = R*.35
    for i in range(windows):
        a = -PI/2 + (i + 1)*2*PI/(windows + 1)
        rr = sphere_r_at(R, wz - zc) - .05
        porthole('Janela', (math.cos(a)*rr, math.sin(a)*rr, wz), R*.12 + .3, a)
    if extra: extra(R, zc)

def build():
    # --- dome houses (three silhouettes) ---
    def chimney(R, zc):
        disc('Chamine', (R*.35, R*.2, zc + R*.9 + 1.5), .8, 4, 'cc_grey', False)
        disc('ChamineTopo', (R*.35, R*.2, zc + R*.9 + 3.6), 1, .5, 'cc_red', False)
    dome_house('Casa_Domo_P', 7.5, 'cc_cream', 'cc_orange', 'cc_blue', 4, chimney)

    def antenna(R, zc):
        top = zc + R
        disc('Mastro', (0, 0, top + 3), .25, 6, 'cc_metal', False)
        ball('Ponta', (0, 0, top + 6.2), .7, 'cc_red')
        M = frame((-R*.45, R*.2, zc + R*.9 + 1.5), (.6, 0, .8))
        xf('C', 'Prato', M, (0, 0, 0), (.4, 4, 4), 'cc_white', (0, PI/2, 0))
        xf('B', 'Suporte', M, (0, 0, -1), (.3, .3, 2), 'cc_metal_dark')
    dome_house('Casa_Domo_M', 9.5, 'cc_white', 'cc_blue', 'cc_yellow', 5, antenna)

    # --- double dome with connecting tube and garage ---
    asset('DRAGONBALL_BUILDINGS', 'Casa_Domo_Dupla')
    for (x, R, m) in ((-5, 9, 'cc_yellow'), (9, 6, 'cc_white')):
        ball('Cupula', (x, 0, -R*.2), R*2, m, col=True)
        disc('Rodape', (x, 0, .6), sphere_r_at(R, .6 + R*.2) + .25, 1.2, 'cc_blue', False)
    capsule_x('Tubo', (2.5, 0, 5), 2.2, 6, 'cc_white')
    for x in (0.5, 2.5, 4.5):
        porthole('JanelaTubo', (x, -2.1, 5.2), .55, -PI/2)
    round_door('Porta', -5, -8.3, 0, 2.6, 4.6)
    box('Garagem', (9, -5.2, 2), (5, 1, 4), 'cc_navy', (0, 0, 0), False)
    for z in (1, 2, 3):
        box('GaragemFaixa', (9, -5.75, z), (4.6, .1, .15), 'cc_grey', (0, 0, 0), False)
    for a in (-2.2, -.9, .5):
        porthole('Janela', (-5 + math.cos(a)*8.3, math.sin(a)*8.3, 4.4), .9, a)
    box('Numero', (-5, -8.2, 6.4), (2, .2, 1), 'cc_white', (0, 0, 0), False, text='12', textcolor='38,82,158')
    disc('Tampa', (-5, 0, 6.9), 3.4, .8, 'cc_orange', False)

    # --- capsule house on stilts ---
    asset('DRAGONBALL_BUILDINGS', 'Casa_Capsula')
    for x in (-5, 5):
        disc('Pilar', (x, 0, 3), 1.2, 6, 'cc_grey', True)
    capsule_x('Corpo', (0, 0, 10.5), 5, 12, 'cc_white', True)
    for x in (-3, 3):
        cyl('Faixa', (x, 0, 10.5), 5.15, .8, 'cc_blue', 'X', False)
    for x in (-6, 0, 6):
        porthole('Janela', (x, -5.0, 11.5 if x == 0 else 11), 1.2 if x == 0 else .9, -PI/2)
    box('Varanda', (0, -6.8, 5.8), (8, 4, .6), 'cc_white', (0, 0, 0), True)
    cyl('GradeVaranda', (0, -8.6, 7), .15, 8, 'cc_blue', 'X', False)
    wedge('Escada', (7.2, -6.8, 2.9), (3, 6, 5.8), 'cc_grey', (0, 0, PI/2), True)
    box('Porta', (0, -4.5, 7.8), (2.4, 1, 3.6), 'cc_navy', (0, 0, 0), False)
    ball('Luz', (11.4, 0, 10.5), 1, 'cc_lamp', light='255,236,190,14,.6')

    # --- antenna house: yellow drum + dome + dish ---
    asset('DRAGONBALL_BUILDINGS', 'Casa_Antena')
    disc('Tambor', (0, 0, 3.5), 6.5, 7, 'cc_yellow', True)
    disc('Faixa', (0, 0, 6.6), 6.65, .6, 'cc_orange', False)
    ball('Cupula', (0, 0, 7), 13, 'cc_white', col=True)
    disc('Varanda', (0, 0, 7.2), 8, .5, 'cc_white', True)
    ring('Grade', (0, 0, 8), 7.8, .2, 1.4, 'cc_blue', 20)
    round_door('Porta', 0, -6.4, 0, 2.6, 4.6)
    for a in (-2.4, -.7, 1.0, 2.5):
        box('Janela', (math.cos(a)*6.5, math.sin(a)*6.5, 3.6), (.3, 2.2, 1.8), 'cc_window', (0, 0, a), False)
    disc('Mastro', (2.5, 1.5, 15.5), .3, 4, 'cc_metal', False)
    M = frame((2.5, 1.5, 17.6), (.5, 0, 2.3))
    xf('C', 'Prato', M, (0, 0, 0), (.4, 5, 5), 'cc_white', (0, PI/2, 0))
    xf('A', 'Receptor', M, (0, 0, 1.8), (.6, .6, .6), 'cc_red')

    # --- round apartment block ---
    asset('DRAGONBALL_BUILDINGS', 'Apartamento_Redondo')
    z = 0
    tones = ['cc_cream', 'cc_white', 'cc_peach']
    for i, r in enumerate((10, 9.4, 8.8)):
        h = 7
        disc('Andar', (0, 0, z + h/2), r, h, tones[i], True)
        disc('Laje', (0, 0, z + h + .3), r + 2, .6, 'cc_white', True)
        ring('Grade', (0, 0, z + h + 1.2), r + 1.8, .2, 1.2, 'cc_blue', 20)
        for k in range(8):
            a = k/8*2*PI + i*.2
            if i == 0 and abs(a - 3*PI/2) < .4: continue
            box('Janela', (math.cos(a)*(r - .05), math.sin(a)*(r - .05), z + 4), (.3, 2.6, 2.6), 'cc_window', (0, 0, a), False)
        z += h + .6
    dome('Cobertura', (0, 0, z), 6.5, 'cc_blue', sink=.3)
    capsule_x('CaixaAgua', (3, 2, z + 5), 1.6, 4, 'cc_white')
    round_door('Porta', 0, -10, 0, 3, 5)
    box('Placa', (0, -10.4, 6.2), (8, .3, 1.4), 'cc_blue', (0, 0, 0), False, text='RESIDENCIAL', textcolor='255,255,255')

    # --- shops: box with rounded ends and striped awning ---
    def shop(nm, wall, awn, label):
        asset('DRAGONBALL_BUILDINGS', nm)
        box('Corpo', (0, 0, 4), (14, 10, 8), wall, (0, 0, 0), True)
        for s in (-1, 1):
            disc('Ponta', (s*7, 0, 4), 5, 8, wall, True)
        box('Teto', (0, 0, 8.4), (15, 10.6, .8), 'cc_white', (0, 0, 0), False)
        for s in (-1, 1):
            disc('TetoPonta', (s*7, 0, 8.4), 5.3, .8, 'cc_white', False)
        box('Vitrine', (0, -5.02, 3.4), (10, .2, 4), 'cc_window', (0, 0, 0), False)
        box('Porta', (0, -5.06, 2.2), (2.6, .2, 4.4), 'cc_navy', (0, 0, 0), False)
        for k in range(6):
            wedge('Toldo', (-6.25 + k*2.5, -6.4, 6.4), (2.5, 3, 1.2), awn if k % 2 == 0 else 'cc_white', (0, 0, 0), False)
        box('Letreiro', (0, -5.3, 9.8), (11, .5, 2.4), 'cc_white', (0, 0, 0), False, text=label, textcolor='38,82,158')
        dome('Globo', (5, 0, 8.8), 1.6, 'cc_lamp', light='255,236,190,16,.7')
    shop('Loja_Lanches', 'cc_pink', 'cc_red', 'LANCHONETE')
    shop('Loja_Ferramentas', 'cc_mint', 'cc_blue', 'FERRAMENTAS')

    # --- laboratory vault ---
    asset('DRAGONBALL_BUILDINGS', 'Laboratorio')
    cyl('Abobada', (0, 0, 0), 9, 20, 'cc_white', 'X', True)
    for x in (-6, 0, 6):
        cyl('Faixa', (x, 0, 0), 9.15, .8, 'cc_blue', 'X', False)
    box('Base', (0, 0, .5), (20.6, 18.6, 1), 'cc_grey', (0, 0, 0), True)
    for s in (-1, 1):
        cyl('Parede', (s*10.05, 0, 0), 8.6, .3, 'cc_cream', 'X', False)
    round_door('Porta', -10.3, 0, 0, 3, 5.2, facing=PI)
    for x in (-5, 5):
        porthole('Claraboia', (x, -6.2, 6.4), 1.2, -PI/2)
    for (x, y) in ((-4, 2), (4, 3)):
        disc('Exaustor', (x, y, 8.6), 1, 2.4, 'cc_metal', False)
        disc('ExaustorTopo', (x, y, 9.9), 1.4, .3, 'cc_metal_dark', False)
    pipe('Tubo', [(10.2, -3, 2), (12.5, -3, 2), (12.5, -3, 7), (6, -3, 8.6)], .5, 'cc_metal_dark')
    box('Letreiro', (0, -8.2, 4.2), (10, .3, 1.8), 'cc_blue', (0, 0, 0), False, text='LABORATORIO', textcolor='255,255,255')
    box('Logo', (10.4, 0, 5), (.2, 4, 4), 'cc_cream', (0, 0, -PI/2), False, emblem='capsule')

    # --- mushroom tower (West City skyline) ---
    asset('DRAGONBALL_BUILDINGS', 'Torre_Cogumelo')
    disc('Base', (0, 0, 2), 5, 4, 'cc_white', True)
    disc('BaseFaixa', (0, 0, 4.2), 5.1, .5, 'cc_blue', False)
    disc('Haste', (0, 0, 20), 2.4, 34, 'cc_white', True)
    for z in (10, 18, 26):
        disc('AnelHaste', (0, 0, z), 2.6, .6, 'cc_grey', False)
    ball('Bulbo', (0, 0, 42), 17, 'cc_yellow', col=True)
    disc('Mirador', (0, 0, 41), 9.4, 2.2, 'cc_white', False)
    for k in range(10):
        a = k/10*2*PI
        box('JanelaMirador', (math.cos(a)*9.45, math.sin(a)*9.45, 41), (.3, 3.4, 1.4), 'cc_window', (0, 0, a), False)
    disc('Antena', (0, 0, 53), .3, 6, 'cc_metal', False)
    ball('AntenaLuz', (0, 0, 56.3), 1, 'cc_red', light='255,80,60,14,.6')
    round_door('Porta', 0, -4.8, 0, 2.4, 3.4)

    # --- arched garage with hover car bay ---
    asset('DRAGONBALL_BUILDINGS', 'Garagem')
    cyl('Arco', (0, 0, 0), 8, 16, 'cc_grey', 'Y', True)
    for y in (-5, 0, 5):
        cyl('Nervura', (0, y, 0), 8.15, .6, 'cc_white', 'Y', False)
    cyl('Frente', (0, -8.05, 0), 7.6, .3, 'cc_white', 'Y', False)
    box('Portao', (0, -8.3, 2.8), (9, .3, 5.6), 'cc_navy', (0, 0, 0), False)
    for z in (1.2, 2.4, 3.6, 4.8):
        box('PortaoFaixa', (0, -8.5, z), (8.6, .1, .2), 'cc_grey', (0, 0, 0), False)
    box('LuzPortao', (0, -8.5, 6.2), (6, .3, .3), 'ki_cyan', (0, 0, 0), False)
    box('Letreiro', (0, -8.4, 7.3), (7, .3, 1), 'cc_blue', (0, 0, 0), False, text='GARAGEM', textcolor='255,255,255')
    box('Piso', (0, -12, .08), (10, 8, .16), 'db_asphalt', (0, 0, 0), False)

    # --- small factory ---
    asset('DRAGONBALL_BUILDINGS', 'Fabrica_Pequena')
    box('Galpao', (0, 0, 5), (20, 14, 10), 'cc_white', (0, 0, 0), True)
    cyl('Telhado', (0, 0, 10), 7, 20.4, 'cc_blue', 'X', False)
    box('Faixa', (0, -7.05, 3), (20.05, .2, 1), 'cc_orange', (0, 0, 0), False)
    box('Portao', (-5, -7.1, 3.2), (6, .2, 6.4), 'cc_grey', (0, 0, 0), False)
    for x in (2, 6):
        box('Janela', (x, -7.1, 6.5), (3, .2, 2), 'cc_window', (0, 0, 0), False)
    for (x, y, h) in ((6, 4, 22), (1, 4, 18)):
        disc('Chamine', (x, y, h/2), 1.3, h, 'cc_grey', True)
        disc('ChamineFaixa', (x, y, h - 2), 1.4, 1, 'cc_orange', False)
    disc('Tanque', (-14, 3, 5), 3, 10, 'cc_cream', True)
    dome('TanqueTopo', (-14, 3, 10), 3, 'cc_white', sink=.1)
    pipe('Tubo', [(-14, 0, 8), (-14, -4, 8), (-10, -4, 8)], .5, 'cc_metal_dark')
    box('Letreiro', (4, -7.3, 9), (10, .3, 1.8), 'cc_blue', (0, 0, 0), False, text='REFINO DE KI', textcolor='255,255,255')

    # --- warehouse ---
    asset('DRAGONBALL_BUILDINGS', 'Deposito')
    box('Corpo', (0, 0, 4.5), (24, 16, 9), 'cc_cream', (0, 0, 0), True)
    cyl('Teto', (0, 0, 9), 8, 24.4, 'cc_white', 'X', False)
    box('Faixa', (0, -8.05, 1), (24.05, .2, 2), 'cc_blue', (0, 0, 0), False)
    box('Doca', (4, -8.1, 3.6), (8, .3, 6.4), 'cc_grey', (0, 0, 0), False)
    box('Plataforma', (4, -10, .6), (10, 4, 1.2), 'cc_metal_dark', (0, 0, 0), True)
    box('Logo', (-6.5, -8.15, 6), (6, .2, 6), 'cc_cream', (0, 0, 0), False, emblem='capsule')

    # --- mountain family house (subtle nod) ---
    asset('DRAGONBALL_BUILDINGS', 'Casa_Montanha')
    ball('Casa', (0, 0, -1), 13, 'cc_white', col=True)
    disc('FaixaVermelha', (0, 0, 2.2), 6.1, 1.2, 'cc_red', False)
    disc('Topo', (0, 0, 5.2), 2.2, .8, 'cc_red', False)
    disc('Chamine', (3, 2, 6), .7, 3, 'cc_grey', False)
    round_door('Porta', 0, -6.2, 0, 2.2, 3.6)
    for a in (-2.3, -.8):
        porthole('Janela', (math.cos(a)*5.5, math.sin(a)*5.5, 2.6), .7, a)
    ball('Anexo', (8, 3, -.5), 7, 'cc_white', col=True)
    disc('AnexoFaixa', (8, 3, 1.2), 3.2, .8, 'cc_red', False)
    for x in (-10, -4):
        disc('Varal', (x, -8, 2.5), .15, 5, 'db_trunk', False)
    rod('Corda', (-10, -8, 4.8), (-4, -8, 4.8), .08, 'flower_white')
    for (x, m) in ((-8.5, 'cc_orange'), (-6.4, 'cc_blue')):
        box('Roupa', (x, -8, 4), (1.4, .1, 1.4), m, (0, 0, 0), False, sway=1)
