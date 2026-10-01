# DRAGONBALL_CAPSULE_TECH / DRAGONBALL_PROPS / DRAGONBALL_MINING / DRAGONBALL_DECORATION
# Asset origin = ground centre, front = -Y.  Big, simple, rounded shapes; neon only for energy.
from dblib import *

def capsule_x(name, loc, r, L, m, col=False, **kw):
    """Pill lying along X."""
    x, y, z = loc
    cyl(name, (x, y, z), r, L, m, 'X', col, **kw)
    for s in (-1, 1):
        ball(name + 'Ponta', (x + s*L/2, y, z), r*2, m)

def capsule_y(name, loc, r, L, m, col=False, **kw):
    x, y, z = loc
    cyl(name, (x, y, z), r, L, m, 'Y', col, **kw)
    for s in (-1, 1):
        ball(name + 'Ponta', (x, y + s*L/2, z), r*2, m)

# ------------------------------------------------------------------ CAPSULE TECH
def tech():
    asset('DRAGONBALL_CAPSULE_TECH', 'Poste_Luz_Tech')
    disc('Base', (0, 0, .4), 1.2, .8, 'cc_grey', True)
    disc('Poste', (0, 0, 6.5), .35, 12, 'cc_white', False)
    disc('Faixa', (0, 0, 3), .42, .6, 'cc_blue', False)
    rod('Braco', (0, 0, 12.2), (0, -3.2, 13.2), .35, 'cc_white')
    capsule_x('Luminaria', (0, -3.6, 13), .7, 2.4, 'cc_white')
    box('LuzLuminaria', (0, -3.6, 12.35), (2.6, 1, .2), 'cc_lamp', (0, 0, 0), False, light='255,236,190,22,.9')
    box('ColisaoPoste', (0, 0, 4), (.8, .8, 8), 'invisible', (0, 0, 0), True)

    asset('DRAGONBALL_CAPSULE_TECH', 'Torre_Energia')
    disc('Base', (0, 0, 1), 3.4, 2, 'cc_grey', True)
    disc('BaseAro', (0, 0, 2.2), 3.0, .4, 'cc_blue', False)
    disc('Coluna', (0, 0, 11), 1.1, 18, 'cc_white', True)
    for i, z in enumerate((7, 12, 17)):
        disc('AnelKi', (0, 0, z), 2.3 - i*.3, .5, 'ki_cyan', False)
    for a in (0, PI/2, PI, 3*PI/2):
        box('Aleta', (math.cos(a)*1.6, math.sin(a)*1.6, 5), (1.8, .35, 6), 'cc_blue', (0, 0, a), False)
    ball('Orbe', (0, 0, 21.4), 3.2, 'ki_cyan', light='110,230,255,26,1.2', fx='ki')
    disc('Coroa', (0, 0, 20), 1.8, .6, 'cc_metal', False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Gerador')
    box('Esqui', (0, 0, .5), (10, 5, 1), 'cc_metal_dark', (0, 0, 0), True)
    capsule_x('Corpo', (0, 0, 3.6), 2.6, 7, 'cc_white', True)
    for x in (-2.2, 0, 2.2):
        cyl('Bobina', (x, 0, 3.6), 2.75, .6, 'cc_blue', 'X', False)
    cyl('NucleoKi', (0, -2.7, 3.6), 1, .3, 'ki_cyan', 'Y', False, light='110,230,255,14,.8')
    box('Painel', (4.8, -1.5, 2.6), (1.4, 1, 2.4), 'cc_grey', (0, 0, 0), False)
    box('Tela', (4.8, -2.05, 3), (1, .1, .8), 'cc_screen', (0, 0, 0), False)
    box('Logo', (0, 2.66, 3.6), (2.4, .2, 2.4), 'cc_white', (0, 0, PI), False, emblem='capsule')
    pipe('Cabo', [(-5, 1.5, 3), (-6.5, 1.5, 1.2), (-8, 1.5, .3)], .35, 'cc_rubber')

    asset('DRAGONBALL_CAPSULE_TECH', 'Refinador')
    disc('Base', (0, 0, .6), 6.4, 1.2, 'cc_grey', True)
    disc('Tanque', (0, 0, 8), 5, 14, 'cc_cream', True)
    for z in (4, 12):
        disc('Faixa', (0, 0, z), 5.15, 1, 'cc_blue', False)
    dome('Tampa', (0, 0, 15), 5, 'cc_white', sink=.1)
    disc('Visor', (0, -4.95, 8), 1.4, .3, 'ki_cyan', False, rot=(PI/2, 0, 0))
    box('Visor', (0, -4.96, 8), (2.4, .3, 5), 'ki_cyan', (0, 0, 0), False, light='110,230,255,16,.8')
    box('Funil', (6.8, 0, 13), (4, 4, 3), 'cc_metal', (0, 0, 0), False)
    wedge('FunilBico', (6.8, 0, 10.5), (4, 4, 2), 'cc_metal', (PI, 0, 0), False)
    pipe('Tubo', [(4.6, 2.6, 3), (8, 2.6, 3), (8, 2.6, .8)], .7, 'cc_metal_dark')
    for z in range(2, 15, 2):
        box('Degrau', (-5.3, 0, z), (.2, 1.6, .2), 'cc_metal_dark', (0, 0, 0), False)
    for s in (-1, 1):
        box('Escada', (-5.3, s*.8, 8), (.2, .2, 14), 'cc_metal_dark', (0, 0, 0), False)
    box('Logo', (0, 4.95, 9), (4, .25, 4), 'cc_cream', (0, 0, PI), False, emblem='capsule')

    asset('DRAGONBALL_CAPSULE_TECH', 'Esteira')   # 12 long along Y, belt top z 4
    box('Estrutura', (0, 0, 3.2), (4.4, 12, 1), 'cc_grey', (0, 0, 0), True)
    box('Cinta', (0, 0, 3.8), (3.6, 12.05, .25), 'cc_rubber', (0, 0, 0), False)
    for s in (-1, 1):
        box('Lateral', (s*2.3, 0, 4.1), (.3, 12, .8), 'cc_blue', (0, 0, 0), False)
        for y in (-5, 5):
            box('Perna', (s*1.8, y, 1.4), (.4, .4, 2.8), 'cc_metal_dark', (0, 0, 0), False)
    for (x, y, m) in ((-.8, -3.5, 'ki_cyan'), (.7, 1, 'db_rock_dark'), (-.4, 4.2, 'ki_cyan'), (.9, -1, 'db_rock')):
        box('MinerioNaEsteira', (x, y, 4.35), (1, 1.2, .9), m, (0, 0, x), False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Terminal')
    box('Pedestal', (0, 0, 1.4), (1.6, 1.2, 2.8), 'cc_white', (0, 0, 0), True)
    box('Faixa', (0, -.62, 1.2), (1.62, .05, .3), 'cc_blue', (0, 0, 0), False)
    box('Tela', (0, -.2, 3.3), (2.6, .3, 1.8), 'cc_navy', (-.5, 0, 0), False)
    box('TelaLuz', (0, -.36, 3.28), (2.2, .1, 1.4), 'cc_screen', (-.5, 0, 0), False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Drone')
    ball('Corpo', (0, 0, 0), 2.2, 'cc_white')
    disc('Aro', (0, 0, 0), 1.35, .35, 'cc_blue', False)
    cyl('Olho', (0, -1.05, .1), .45, .2, 'ki_cyan', 'Y', False)
    for a in (PI/4, 3*PI/4, 5*PI/4, 7*PI/4):
        rod('Braco', (0, 0, .3), (math.cos(a)*2, math.sin(a)*2, .5), .2, 'cc_grey')
        disc('Helice', (math.cos(a)*2, math.sin(a)*2, .6), .9, .08, 'cc_metal_dark', False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Veiculo_Hover')
    capsule_y('Carroceria', (0, 0, 2.2), 1.6, 5, 'cc_yellow', True)
    box('Assoalho', (0, 0, 1.6), (3.6, 6.4, .8), 'cc_white', (0, 0, 0), False)
    dome('Cupula', (0, .6, 3.2), 1.5, 'cc_window', sink=.2)
    for s in (-1, 1):
        capsule_y('Turbina', (s*2.1, -.4, 1.3), .6, 3.4, 'cc_white')
        box('Jato', (s*2.1, -.4, .6), (.8, 3, .15), 'ki_cyan', (0, 0, 0), False)
    box('Farol', (0, -4.1, 2.2), (1.6, .2, .4), 'cc_lamp', (0, 0, 0), False)
    box('Logo', (1.62, 0, 2.3), (.2, 1.5, 1.5), 'cc_yellow', (0, 0, PI/2), False, emblem='capsule')

    asset('DRAGONBALL_CAPSULE_TECH', 'Capsula_HoiPoi')   # giant display capsule
    capsule_x('Metade', (-1.6, 0, 2.2), 2, 3.4, 'cc_white', True)
    cyl('Metade2', (1.8, 0, 2.2), 2, 3.4, 'cc_grey', 'X', True)
    ball('Ponta2', (3.5, 0, 2.2), 4, 'cc_grey')
    cyl('Junta', (.1, 0, 2.2), 2.1, .5, 'cc_blue', 'X', False)
    cyl('Botao', (-1.6, 0, 4.25), .45, .3, 'cc_red', 'Z', False)
    box('Numero', (-1.6, -2.02, 2.2), (1.4, .1, 1.1), 'cc_white', (0, 0, 0), False, text='No.7', textcolor='36,46,84')
    box('Apoio', (0, 0, .2), (5, 2.4, .4), 'cc_metal_dark', (0, 0, 0), False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Container_Tech')
    box('Corpo', (0, 0, 3), (12, 6, 5.6), 'cc_white', (0, 0, 0), True)
    for s in (-1, 1):
        cyl('BordaTopo', (0, s*2.9, 5.8), .35, 12, 'cc_grey', 'X', False)
    box('Faixa', (0, -3.02, 2), (12.05, .1, .8), 'cc_blue', (0, 0, 0), False)
    box('Porta', (5.2, -3.02, 3.2), (1.2, .1, 4.2), 'cc_grey', (0, 0, 0), False)
    box('Logo', (-2, -3.05, 3.8), (2.4, .1, 2.4), 'cc_white', (0, 0, 0), False, emblem='capsule')
    for x in (-5.4, 5.4):
        box('Pe', (x, 0, .1), (1, 6.2, .2), 'cc_metal_dark', (0, 0, 0), False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Antena_Parabolica')
    box('Base', (0, 0, .5), (3, 3, 1), 'cc_grey', (0, 0, 0), True)
    disc('Mastro', (0, 0, 4), .4, 6, 'cc_white', False)
    M = frame((0, -.6, 7.4), (-.7, 0, 0))
    xf('C', 'Prato', M, (0, 0, 0), (.5, 7, 7), 'cc_white', (0, PI/2, 0))
    xf('C', 'PratoAro', M, (0, 0, -.05), (.55, 7.3, 7.3), 'cc_grey', (0, PI/2, 0))
    xf('B', 'Haste', M, (0, 0, 1.6), (.2, .2, 3.2), 'cc_metal_dark')
    xf('A', 'Receptor', M, (0, 0, 3.3), (.8, .8, .8), 'cc_red')

    asset('DRAGONBALL_CAPSULE_TECH', 'Broca_Mineradora')
    box('Plataforma', (0, 0, .6), (9, 9, 1.2), 'cc_metal_dark', (0, 0, 0), True)
    for (sx, sy) in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        rod('Perna', (sx*4, sy*4, 1), (sx*1.2, sy*1.2, 16), .7, 'cc_yellow')
    disc('Cabeca', (0, 0, 17), 2.2, 3, 'cc_white', False)
    disc('Faixa', (0, 0, 17.8), 2.3, .6, 'cc_blue', False)
    disc('Eixo', (0, 0, 9), .8, 13, 'cc_metal', False)
    for z in (4, 7, 10, 13):
        disc('Rosca', (0, 0, z), 1.3, .4, 'cc_metal_dark', False)
    ball('LuzAlerta', (0, 0, 19), 1.2, 'cc_orange', light='255,160,60,12,.7')
    box('Cabine', (5.8, -3, 3.6), (3, 3, 4.8), 'cc_white', (0, 0, 0), True)
    box('JanelaCabine', (5.8, -4.52, 4.4), (2.2, .1, 1.6), 'cc_window', (0, 0, 0), False)
    box('Brilho', (0, 0, 1.25), (3, 3, .1), 'ki_cyan', (0, 0, PI/4), False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Nave_Gravidade')   # round Capsule spaceship
    for (sx, sy) in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
        rod('Perna', (sx*6, sy*6, 8), (sx*9, sy*9, .6), 1, 'cc_grey', True)
        disc('Pata', (sx*9, sy*9, .3), 1.8, .6, 'cc_metal_dark', False)
    ball('Casco', (0, 0, 16), 22, 'cc_white', col=True)
    disc('Anel', (0, 0, 14.5), 11.6, 2.2, 'cc_blue_dark', False)
    disc('AnelLuz', (0, 0, 14.5), 11.7, .5, 'ki_cyan', False)
    for i in range(8):
        a = i/8*2*PI
        porthole('Janela', (math.cos(a)*10.6, math.sin(a)*10.6, 19), .9, a)
    disc('Topo', (0, 0, 27), 2.4, 1.2, 'cc_grey', False)
    disc('Antena', (0, 0, 30), .25, 5, 'cc_metal', False)
    ball('AntenaLuz', (0, 0, 32.6), .9, 'cc_red', light='255,80,60,10,.6')
    box('Logo', (0, -10.2, 20), (7, .3, 7), 'cc_white', (0, 0, 0), False, emblem='capsule')
    wedge('Rampa', (0, -13, 3.3), (5, 10, 6.6), 'cc_grey', (0, 0, 0), True)
    box('Escotilha', (0, -9.2, 9.2), (4.6, 2, 5), 'cc_navy', (0, 0, 0), False)

    asset('DRAGONBALL_CAPSULE_TECH', 'Pod_Espacial')
    ball('Casco', (0, 0, 3.8), 7.6, 'cc_white', col=True)
    disc('Anel', (0, 0, 2.6), 3.7, .9, 'cc_grey', False)
    M = frame((0, -3.55, 4.6), (-.35, 0, 0))
    xf('C', 'Vidro', M, (0, 0, 0), (.6, 4.2, 4.2), 'cc_red', (0, 0, PI/2))
    xf('C', 'VidroAro', M, (0, .12, 0), (.5, 4.8, 4.8), 'cc_grey', (0, 0, PI/2))
    M2 = frame((0, -4.6, 6.8), (-1.2, 0, 0))
    xf('C', 'Tampa', M2, (0, 0, 0), (.5, 4.6, 4.6), 'cc_white', (0, 0, PI/2))
    for a in (PI/3, PI, 5*PI/3):
        rod('Pe', (math.cos(a)*2.4, math.sin(a)*2.4, 1.2), (math.cos(a)*3.8, math.sin(a)*3.8, 0), .35, 'cc_metal_dark')

# ------------------------------------------------------------------ PROPS
def props():
    asset('DRAGONBALL_PROPS', 'Banco_Tech')
    capsule_x('Assento', (0, 0, 1.6), .45, 4, 'cc_white')
    box('Encosto', (0, .55, 2.5), (4.6, .3, 1.4), 'cc_blue', (0, 0, 0), False)
    for x in (-1.6, 1.6):
        box('Pe', (x, 0, .7), (.4, .8, 1.4), 'cc_grey', (0, 0, 0), False)
    box('ColisaoBanco', (0, 0, .9), (5, 1.4, 1.8), 'invisible', (0, 0, 0), True)

    asset('DRAGONBALL_PROPS', 'Grade_Tech')   # 8-long railing along X
    for x in (-4, 4):
        disc('Poste', (x, 0, 1.6), .25, 3.2, 'cc_grey', False)
        ball('Topo', (x, 0, 3.3), .6, 'cc_blue')
    cyl('Corrimao', (0, 0, 3), .18, 8, 'cc_blue', 'X', False)
    cyl('Barra', (0, 0, 1.8), .12, 8, 'cc_white', 'X', False)

    asset('DRAGONBALL_PROPS', 'Caixa_Carga')
    box('Caixa', (0, 0, 1.5), (3, 3, 3), 'cc_white', (0, 0, 0), True)
    for z in (.2, 2.8):
        box('Aresta', (0, 0, z), (3.1, 3.1, .4), 'cc_orange', (0, 0, 0), False)
    box('Logo', (0, -1.52, 1.5), (1.4, .06, 1.4), 'cc_white', (0, 0, 0), False, emblem='capsule')

    asset('DRAGONBALL_PROPS', 'Barril_Metal')
    disc('Barril', (0, 0, 1.6), 1.1, 3.2, 'cc_blue', True)
    for z in (.6, 2.6):
        disc('Aro', (0, 0, z), 1.16, .25, 'cc_metal', False)
    disc('Tampa', (0, 0, 3.25), .8, .1, 'cc_white', False)

    asset('DRAGONBALL_PROPS', 'Maquina_Venda')
    box('Corpo', (0, 0, 3), (3.4, 2.4, 6), 'cc_red', (0, 0, 0), True)
    box('Vitrine', (-.4, -1.22, 3.6), (2.2, .1, 3.6), 'cc_window', (0, 0, 0), False)
    box('Luz', (-.4, -1.24, 5.6), (2.2, .1, .5), 'cc_lamp', (0, 0, 0), False)
    box('Botoes', (1.2, -1.22, 3.6), (.6, .1, 2.4), 'cc_white', (0, 0, 0), False)
    dome('Topo', (0, 0, 6), 1.4, 'cc_white', sink=.4)

    asset('DRAGONBALL_PROPS', 'Cone')
    box('BaseCone', (0, 0, .1), (1.6, 1.6, .2), 'cc_rubber', (0, 0, 0), False)
    for i, (r, z) in enumerate(((.6, .6), (.45, 1.2), (.3, 1.7))):
        disc('Cone', (0, 0, z), r, .6, 'cc_orange' if i != 1 else 'cc_white', False)

    asset('DRAGONBALL_PROPS', 'Placa_Tech')   # blank sign frame (text set on placement)
    for x in (-4.5, 4.5):
        disc('Poste', (x, 0, 3), .3, 6, 'cc_grey', False)
    capsule_x('Moldura', (0, 0, 5.2), .3, 9, 'cc_blue')

# ------------------------------------------------------------------ MINING (decorative, not breakable ores)
def mining():
    tones = {'Cristal_Ki': 'ki_cyan', 'Cristal_Ki_Ouro': 'ki_gold', 'Cristal_Ki_Roxo': 'ki_purple'}
    for nm, m in tones.items():
        r = rng(len(nm))
        asset('DRAGONBALL_MINING', nm)
        _rock_base(r)
        crystal('Cristal', (0, 0, .6), 6, 1.4, m, (0, .12, 0))
        crystal('Cristal', (1.2, .4, .6), 4, 1.0, m, (.2, .5, .6))
        crystal('Cristal', (-1.1, -.3, .6), 3.6, .9, m, (-.3, -.45, -.4))
        crystal('Cristal', (.2, -1.2, .6), 2.6, .7, 'ki_white', (-.5, .1, 0))
        box('Luz', (0, 0, 2), (.4, .4, .4), m, (0, 0, 0), False, light={'ki_cyan': '110,230,255,12,.8', 'ki_gold': '255,214,90,12,.8', 'ki_purple': '200,130,255,12,.8'}[m])
    asset('DRAGONBALL_MINING', 'Cristal_Ki_G')
    r = rng(99)
    for (x, y, sc) in ((0, 0, 1), (3, 2, .7), (-3, 1, .8), (1, -3, .6)):
        box('RochaBase', (x, y, 1.2*sc), (5*sc, 4.5*sc, 2.4*sc), r.choice(['db_rock_dark', 'db_rock']), (0, 0, r.uniform(0, 3)), True)
    crystal('CristalG', (0, 0, 2), 18, 4, 'ki_cyan', (0, .1, 0))
    crystal('CristalG', (3.6, 1.6, 1.6), 12, 3, 'ki_cyan', (.15, .45, .5))
    crystal('CristalG', (-3.4, .8, 1.6), 11, 2.8, 'ki_blue', (-.1, -.5, -.3))
    crystal('CristalG', (1, -3.4, 1.2), 8, 2.2, 'ki_white', (-.5, .15, 0))
    crystal('CristalG', (-1.6, 3.2, 1.2), 7, 2, 'ki_cyan', (.5, -.2, 0))
    box('Luz', (0, 0, 8), (.5, .5, .5), 'ki_cyan', (0, 0, 0), False, light='110,230,255,30,1.2', fx='ki')

    asset('DRAGONBALL_MINING', 'Veio_Ki')   # glowing vein on a wall face (facing -Y), 12 x 6
    pts = [(-6, 0, 1), (-3.5, 0, 2.8), (-1, 0, 1.6), (1.5, 0, 4), (4, 0, 2.6), (6, 0, 4.8)]
    for a, b in zip(pts, pts[1:]):
        rod('Veio', a, b, .5, 'ki_cyan', h=.5)
    crystal('Cristal', (1.5, -.2, 4), 2.4, .7, 'ki_cyan', (-1.1, 0, .3))
    crystal('Cristal', (-3.5, -.2, 2.8), 1.8, .6, 'ki_white', (-1.3, 0, -.4))

    c = asset('DRAGONBALL_MINING', 'Rocha_Fissura')
    import dbshapes
    dbshapes.to_object('Fissura_Malha', dbshapes.boulder('Fissura_Malha', c, size=(8, 7, 5.6), seed=17, sub=2, tone='db_rock_dark'), c, smooth=False)
    box('Colisao', (0, 0, 2.2), (6, 5, 4.4), 'invisible', (0, 0, .3), True)
    for (a, b) in (((-3, -3.1, 3.5), (0, -3.2, 1.6)), ((0, -3.2, 1.6), (2.4, -3.2, 3.8)), ((3.6, -1, 3), (3.6, 1.8, 1))):
        rod('Fissura', a, b, .3, 'ki_cyan', h=.3)

    asset('DRAGONBALL_MINING', 'Trilho_Tech')   # 8 long along Y
    for x in (-1.1, 1.1):
        box('Trilho', (x, 0, .45), (.3, 8, .3), 'cc_metal', (0, 0, 0), False)
    for y in (-3, -1, 1, 3):
        box('Dormente', (0, y, .15), (3.6, .6, .3), 'cc_metal_dark', (0, 0, 0), False)

    asset('DRAGONBALL_MINING', 'Vagoneta_Tech')
    capsule_y('Cacamba', (0, 0, 2.2), 1.6, 3, 'cc_yellow', True)
    box('Carga', (0, 0, 3.6), (2.4, 4, 1), 'db_rock_dark', (0, 0, 0), False)
    for (x, y) in ((.6, -.8), (-.5, .9)):
        crystal('Minerio', (x, y, 3.8), 2, .7, 'ki_cyan', (0, .3, x))
    for s in (-1, 1):
        for y in (-1.6, 1.6):
            cyl('Roda', (s*1.3, y, .7), .6, .4, 'cc_rubber', 'X', False)

    asset('DRAGONBALL_MINING', 'Luminaria_Mina')
    for a in (0, 2*PI/3, 4*PI/3):
        rod('Tripe', (math.cos(a)*1.8, math.sin(a)*1.8, 0), (0, 0, 6), .3, 'cc_metal_dark')
    box('Holofote', (0, -.4, 6.6), (2.4, 1.2, 1.6), 'cc_yellow', (-.3, 0, 0), False)
    box('Lente', (0, -1.05, 6.4), (2, .1, 1.2), 'cc_lamp', (-.3, 0, 0), False, light='255,240,200,24,1')

    asset('DRAGONBALL_MINING', 'Arco_Mina')   # metal tunnel frame, 22 wide, depth 3 along Y
    for s in (-1, 1):
        box('Pilar', (s*10.5, 0, 6), (1.6, 3, 12), 'cc_grey', (0, 0, 0), True)
        box('FaixaPilar', (s*10.5, -1.55, 6), (1.2, .1, 10), 'cc_blue', (0, 0, 0), False)
    vring('Arco', (0, 0, 12), 10.5, 1.6, 3, 'cc_grey', 14, 0, False, a0=0, a1=PI)
    vring('ArcoLuz', (0, -1.6, 12), 9.6, .4, .2, 'ki_cyan', 14, 0, False, a0=.1, a1=PI-.1)

    asset('DRAGONBALL_MINING', 'Cristal_Parede')   # crystals bursting sideways out of a wall (face -Y)
    for (x, z, h, w, rx, rz, m) in ((0, 3, 6, 1.6, -1.25, 0, 'ki_cyan'), (1.8, 1.4, 4, 1.1, -1.0, .5, 'ki_cyan'),
                                    (-1.6, 4.6, 3.6, 1, -1.5, -.6, 'ki_white'), (-.4, .8, 2.6, .8, -.8, -.2, 'ki_blue')):
        crystal('Cristal', (x, .4, z), h, w, m, (rx, 0, rz))
    box('Luz', (0, -1.5, 3), (.3, .3, .3), 'ki_cyan', (0, 0, 0), False, light='110,230,255,14,.9')

def _rock_base(r):
    for (x, y, s) in ((0, 0, 1), (1.4, .8, .6), (-1.2, .6, .7)):
        box('RochaBase', (x, y, .6*s), (3*s, 2.6*s, 1.2*s), r.choice(['db_rock_dark', 'db_rock']), (0, 0, r.uniform(0, 3)), False)

# ------------------------------------------------------------------ DECORATION
def decoration():
    star_layouts = {1: [(0, 0)], 2: [(-.3, 0), (.3, 0)], 3: [(0, .3), (-.3, -.2), (.3, -.2)],
                    4: [(-.3, .3), (.3, .3), (-.3, -.3), (.3, -.3)], 5: [(0, .38), (-.36, .1), (.36, .1), (-.22, -.32), (.22, -.32)],
                    6: [(-.3, .36), (.3, .36), (-.38, 0), (.38, 0), (-.3, -.36), (.3, -.36)],
                    7: [(0, 0), (-.3, .36), (.3, .36), (-.4, 0), (.4, 0), (-.3, -.36), (.3, -.36)]}
    for n, pts in star_layouts.items():
        asset('DRAGONBALL_DECORATION', 'Esfera_Dragao_%d' % n)
        ball('Esfera', (0, 0, 1.6), 3.2, 'db_ball')
        ball('Brilho', (-.55, -1.05, 2.3), .7, 'flower_white')
        for (sx, sz) in pts:
            for a in (0, PI/4):
                box('Estrela', (sx*1.4, -1.45, 1.6 + sz*1.4), (.34, .06, .34), 'db_star', (0, a, 0), False)
        disc('Suporte', (0, 0, .15), .9, .3, 'temple_stone', False)

    asset('DRAGONBALL_DECORATION', 'Bandeira_Capsule')
    disc('Mastro', (0, 0, 8), .25, 16, 'cc_metal', False)
    ball('Ponta', (0, 0, 16.2), .6, 'cc_blue')
    box('Bandeira', (2.8, 0, 13.2), (5.4, .15, 4.6), 'cc_white', (0, 0, 0), False, emblem='capsule', sway=1)
    box('Faixa', (2.8, 0, 11.1), (5.4, .17, .5), 'cc_blue', (0, 0, 0), False, sway=1)

    asset('DRAGONBALL_DECORATION', 'Painel_Capsule')   # billboard 20 x 10
    for x in (-8, 8):
        disc('Coluna', (x, 0, 7), .6, 14, 'cc_grey', True)
    box('Painel', (0, 0, 14), (22, 1, 10), 'cc_white', (0, 0, 0), True)
    box('Moldura', (0, -.1, 9.2), (22.4, 1.2, .6), 'cc_blue', (0, 0, 0), False)
    box('Logo', (-6.5, -.56, 14.4), (7, .1, 7), 'cc_white', (0, 0, 0), False, emblem='capsule')
    box('Texto', (4, -.56, 14.8), (12, .1, 4), 'cc_white', (0, 0, 0), False, text='CAPSULE', textcolor='38,82,158')
    box('Subtexto', (4, -.56, 11.8), (12, .1, 1.8), 'cc_white', (0, 0, 0), False, text='MINERACAO DE KI', textcolor='70,150,235')

def build():
    tech(); props(); mining(); decoration()
