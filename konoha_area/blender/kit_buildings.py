# KONOHA_BUILDINGS kit. Origin = ground centre of footprint, front faces -Y.
import math
from klib import *
from kit_parts import *

CAT = 'KONOHA_BUILDINGS'

def casa_p_duas_aguas():
    asset(CAT, 'Casa_P_DuasAguas')
    b = Body(0, 0, 0, 12, 10, 9)
    box('Fundacao', (0, 0, .3), (13, 11, .6), 'stone', col=True)
    body('Paredes', b, 'wall_cream')
    band(b, 8.8, 'wood')
    for x in (-6, 6):
        box('Pilar', (x, -5.1, 4.5), (.6, .6, 9), 'wood', col=False)
    door(b, 'S', -2.8)
    window(b, 'S', 2.6, 5, 3.4, 3.0, shutter='roof_red')
    window(b, 'E', 0, 5, 3, 3)
    window(b, 'W', 1.5, 5.2, 2.6, 2.6, lit=True)
    gable(b, 9, 4.2, 'roof_red', over=1.4)
    tank(4.2, 2.5, 9, r=1.5, h=2.6)
    planter(2.6, -6, 0, 3.4)
    paper_lantern(-5.4, -6.1, 7.2)

def casa_p_laje_caixa():
    asset(CAT, 'Casa_P_LajeCaixa')
    b = Body(0, 0, 0, 11, 11, 10)
    box('Fundacao', (0, 0, .3), (12, 12, .6), 'stone', col=True)
    body('Paredes', b, 'wall_tan')
    band(b, 1.0, 'wall_peach', t=2, grow=.2, name='Rodape')
    door(b, 'S', 2.4)
    window(b, 'S', -2.6, 5.5, 3, 3.4, lit=True)
    window(b, 'W', 0, 5.5, 3.4, 3)
    ac_unit(b, 'E', -2, 6.5)
    skirt(Body(0, 0, 0, 11, 11, 10), 10.6, 2.2, 1.4, 'roof_green')
    flat_roof(b, 'wall_tan')
    box('Parapeito', (0, 0, 11.4), (11.4, 11.4, .9), 'wall_peach', col=False)
    tank(-1.5, 1.5, 10.5, r=2.6, h=4.2, band_m='cloth_red')
    box('Antena', (3.6, -3, 13.5), (.2, .2, 5), 'metal', col=False)
    rod('AntenaHaste', (2.6, -3, 15.5), (4.6, -3, 15.5), .15, 'metal')

def casa_m_varanda_escada():
    asset(CAT, 'Casa_M_VarandaEscada')
    b1 = Body(0, 0, 0, 16, 12, 9)
    b2 = Body(0, 0, 9, 16, 12, 8.5)
    box('Fundacao', (0, 0, .3), (17, 13, .6), 'stone', col=True)
    body('Terreo', b1, 'wall_peach')
    body('Andar', b2, 'wall_cream')
    door(b1, 'S', -4.5)
    window(b1, 'S', .6, 5, 3.0, 3.0)
    window(b1, 'S', 5.0, 5, 3.6, 3.2, lit=True, shutter='roof_orange')
    skirt(b1, 9.4, 2.4, 1.6, 'roof_orange')
    window_row(b2, 'S', 13.2, 3, 4.8, 2.6, 2.8)
    balcony(b2, 'S', 0, 9.6, 12, 2.6)
    window(b2, 'W', 0, 13.2, 3, 2.8)
    stairs_side(b1, 'E', -5.5, 9, run=11, width=2.8)
    box('PatamarEscada', (9.4, 6.2, 9.1), (2.8, 3, .4), 'wood', col=True)
    skirt(b2, 18.0, 2.0, 1.3, 'roof_red')
    flat_roof(b2, 'wall_tan')
    tank(4.5, 2.5, 17.8, r=2.0, h=3.4)
    vsign(-8.6, -6.4, 12, 'CASA', 'cloth_white', h=5.5)

def casa_m_escalonada():
    asset(CAT, 'Casa_M_Escalonada')
    b1 = Body(0, 0, 0, 18, 13, 9)
    b2 = Body(-2.5, 1.5, 9, 11, 9, 8)
    box('Fundacao', (0, 0, .3), (19, 14, .6), 'stone', col=True)
    body('Terreo', b1, 'wall_white')
    band(b1, 3.2, 'roof_blue', t=.5, grow=.1, name='FaixaAzul')
    door(b1, 'S', 5.5, m='roof_blue')
    window_row(b1, 'S', 5.6, 2, 5.2, 3.2, 3.2, lit_every=2)
    window(b1, 'E', 0, 5.6, 3.4, 3.2)
    skirt(b1, 9.4, 2.2, 1.5, 'roof_blue')
    box('Terraco', (0, 0, 9.3), (18.2, 13.2, .6), 'wall_tan', col=True)
    body('Andar', b2, 'wall_cream')
    window(b2, 'S', 0, 13, 4.2, 3, lit=True)
    window(b2, 'E', 0, 13, 2.8, 2.8)
    gable(b2, 17, 3.6, 'roof_blue', over=1.2)
    planter(5.5, -5, 9.6, 4.5)
    planter(7.6, 1.5, 9.6, 3.0, rot=math.pi/2)
    tank(6, 4, 9.6, r=1.7, h=3)

def casa_g_tres_andares():
    asset(CAT, 'Casa_G_TresAndares')
    box('Fundacao', (0, 0, .3), (19, 17, .6), 'stone', col=True)
    colors = ['wall_tan', 'wall_cream', 'wall_white']
    roofs = ['roof_red', 'roof_red', 'roof_orange']
    for i in range(3):
        b = Body(0, 0, i*9, 18 - i*1.5, 16 - i*1.5, 9)
        body('Andar%d' % (i+1), b, colors[i])
        if i == 0:
            door(b, 'S', 0, w=5, m='wood_light')
            window_row(b, 'S', 5.4, 2, 10, 3.2, 3.0)
        else:
            window_row(b, 'S', i*9+4.8, 3, 5, 2.8, 3.0, lit_every=2 if i == 1 else 0)
        window_row(b, 'E', i*9+4.8, 2, 7, 2.8, 3.0)
        window_row(b, 'W', i*9+4.8, 2, 7, 2.8, 3.0)
        skirt(b, i*9+9.3, 2.4 - i*.2, 1.5, roofs[i])
    top = Body(0, 0, 27, 15, 13, 0)
    flat_roof(Body(0, 0, 0, 15, 13, 27), 'curb')
    tank(-3.5, 2, 27.5, r=2.4, h=4)
    tank(3.2, 2.5, 27.5, r=1.8, h=3.2, band_m='cloth_red')
    box('CasaMaquinas', (3, -3, 29), (4, 3.5, 3.6), 'wall_tan', col=False)
    vsign(9.6, -8.4, 15, 'HOTEL', 'cloth_red', h=9, w=2.2)

def torre_cilindrica():
    asset(CAT, 'Torre_Cilindrica')
    cyl('BaseTorre', (0, 0, .4), 7.2, .8, 'stone', col=True)
    for i, (r, h, m) in enumerate([(6.5, 9, 'wall_white'), (6.0, 8, 'wall_cream'), (5.4, 7, 'wall_white')]):
        z0 = [0.8, 9.8, 18.8][i]
        cyl('CorpoTorre', (0, 0, z0+h/2), r, h, m, col=True)
        cyl('AnelAzul', (0, 0, z0+h+.3), r+1.3, .6, 'roof_blue', col=False)
        cyl('AnelAzulSup', (0, 0, z0+h+.8), r+.6, .5, 'roof_blue', col=False)
        n = 6 if i < 2 else 5
        for k in range(n):
            a = k / n * 2 * math.pi + i * .3
            x, y = math.cos(a)*(r+.05), math.sin(a)*(r+.05)
            box('JanelaTorre', (x, y, z0+h*.55), (.3, 2.2, 2.8), 'window_lit' if (k+i) % 3 == 0 else 'glass', (0,0,a), col=False)
            box('MolduraTorre', (x*1.005, y*1.005, z0+h*.55), (.2, 2.8, 3.4), 'wood_dark', (0,0,a), col=False)
    cyl('CupulaA', (0, 0, 27.6), 4.4, 1.2, 'roof_blue', col=False)
    cyl('CupulaB', (0, 0, 28.7), 3.0, 1.0, 'roof_blue', col=False)
    cyl('CupulaC', (0, 0, 29.6), 1.6, .8, 'roof_blue', col=False)
    box('Mastro', (0, 0, 32), (.3, .3, 4), 'metal', col=False)
    box('PortaTorre', (0, -6.6, 3.8), (3.6, .6, 6.2), 'wood', col=False)
    box('MolduraPorta', (0, -6.5, 4.1), (4.4, .5, 6.8), 'wood_dark', col=False)

def loja_ramen():
    asset(CAT, 'Loja_Ramen')
    b = Body(0, 1.5, 0, 14, 9, 8.5)
    box('Fundacao', (0, 0, .3), (15, 13, .6), 'wood_dark', col=True)
    body('Cozinha', b, 'wood_light')
    for x in (-6.8, 6.8):
        box('PilarFrente', (x, -4.6, 4.6), (.8, .8, 8.6), 'wood', col=True)
    box('Balcao', (0, -3.4, 1.9), (12.5, 2.2, 3.2), 'wood', col=True)
    box('TampoBalcao', (0, -3.6, 3.6), (13, 2.8, .35), 'wood_light', col=False)
    for x in (-4.5, -1.5, 1.5, 4.5):
        cyl('Banqueta', (x, -5.6, 1.4), .7, 2.6, 'wood_dark', col=False)
        cyl('Assento', (x, -5.6, 2.8), .9, .3, 'cloth_red', col=False)
        cyl('Tigela', (x, -3.6, 4.0), .55, .5, 'cloth_white', col=False)
    box('Coberta', (0, -2, 8.9), (15.5, 13.5, .6), 'wood', col=True)
    wedge('Aba', (0, -6.4, 8.3), (15.5, 3.2, 1.4), 'wood_dark', (0,0,0), col=False)
    fb = Body(0, -3.2, 0, 14, 2, 8.6)
    noren(fb, 'S', 0, 7.6, w=12, panels=5, text='RAMEN')
    paper_lantern(-7.6, -5.4, 6.6)
    paper_lantern(7.6, -5.4, 6.6)
    b2 = Body(1, 2.5, 9.2, 9, 7, 5.5)
    body('Sobrado', b2, 'wood_light')
    window(b2, 'S', -1.5, 12, 4.2, 2.4)
    gable(b2, 14.7, 2.6, 'wood', over=1.0)
    tank(-4.5, 3.2, 9.2, r=1.8, h=3.4, band_m='cloth_red')
    rod('Corda', (-6.2, 3.2, 11), (-2.8, 3.2, 13.2), .2, 'cloth_red')
    b3 = Body(0, 1.5, 0, 14, 9, 8.5)
    window(b3, 'N', 0, 5.5, 3, 2.2)

def loja_dango():
    asset(CAT, 'Loja_Dango')
    b = Body(0, 1, 0, 12, 9, 9)
    box('Fundacao', (0, 0, .3), (13, 12, .6), 'stone', col=True)
    body('Loja', b, 'wall_peach')
    door(b, 'S', 3.2, w=4, m='cloth_white')
    window(b, 'S', -2.6, 4.2, 4.4, 3.4, lit=True, sill=False)
    for i in range(6):
        x = -5.5 + i*2.2
        wedge('ToldoListrado', (x, -5.2, 7.3), (2.2, 3.2, 1.4), 'cloth_red' if i % 2 == 0 else 'cloth_white', (0,0,0), col=False)
    gable(b, 9, 3.6, 'roof_red', over=1.2)
    vsign(-6.9, -4.3, 5.2, 'DANGO', 'cloth_white', h=5.4)
    box('Banco', (-3.5, -8.2, 1.2), (6, 2, .4), 'cloth_red', col=False)
    for x in (-6, -1): box('PeBanco', (x, -8.2, .5), (.4, 1.6, 1), 'wood_dark', col=False)
    box('HasteSombrinha', (2.5, -8.4, 3.5), (.25, .25, 7), 'wood', col=False)
    cyl('Sombrinha', (2.5, -8.4, 7), 3.6, .35, 'cloth_red', col=False)
    cyl('SombrinhaTopo', (2.5, -8.4, 7.4), 1.8, .5, 'cloth_red', col=False)
    for k in range(3):
        ball('Dango', (-5 + k*.9, -8.2, 1.8), .7, ['cloth_white', 'cr_wind', 'lantern'][k])

def loja_armas():
    asset(CAT, 'Loja_Armas')
    b1 = Body(0, 0, 0, 13, 11, 9)
    b2 = Body(0, .5, 9, 12, 10, 7)
    box('Fundacao', (0, 0, .3), (14, 12, .6), 'stone_dark', col=True)
    body('Terreo', b1, 'wood_dark')
    body('Andar', b2, 'wall_tan')
    door(b1, 'S', -3.5, m='wood_light')
    window(b1, 'S', 3, 4.8, 4.6, 3.2, lit=True)
    skirt(b1, 9.4, 2.0, 1.3, 'trim_dark')
    window_row(b2, 'S', 12.8, 2, 5, 3, 2.6)
    gable(b2, 16, 3.4, 'trim_dark', over=1.2, along='Y')
    hsign(b1, 'S', 0, 8.0, 'ARMAS NINJA', 9, h=1.6, m='trim_dark')
    # shuriken & kunai sign
    box('Kunai', (7.4, -6.2, 9.5), (.6, .3, 5), 'metal', (0,0,0), col=False)
    wedge('PontaKunai', (7.4, -6.2, 12.6), (1.2, .3, 1.2), 'metal', (math.pi/2,0,0), col=False)
    cyl('AroKunai', (7.4, -6.2, 6.6), .6, .3, 'metal', axis='Y')
    for k in range(4):
        box('Shuriken', (-7.2, -6.2, 10), (2.6, .25, .6), 'metal', (0, k*math.pi/4, 0), col=False)
    box('Caixote', (-5.5, -7, 1), (2, 2, 2), 'wood', col=False)

def loja_flores():
    asset(CAT, 'Loja_Flores')
    b = Body(0, 1, 0, 12, 10, 10)
    box('Fundacao', (0, 0, .3), (13, 12, .6), 'stone', col=True)
    body('Loja', b, 'wall_white')
    window(b, 'S', -2.5, 5, 5, 4.2, lit=True, sill=False)
    door(b, 'S', 3.6, w=3.6, m='roof_green')
    skirt(b, 10.5, 2.4, 1.5, 'roof_green')
    flat_roof(b, 'wall_tan')
    for i, z in enumerate((.9, 2.2)):
        box('Prateleira', (-2.5, -5.8 - i*.9, z), (8, 1.4, .3), 'wood', col=False)
        for k in range(5):
            ball('Buque', (-6 + k*1.7, -5.8 - i*.9, z+.8), 1.0, ['cr_fire', 'cloth_white', 'cr_lightning', 'cr_rare', 'cr_wind'][(k+i) % 5])
    hsign(b, 'S', 0, 8.6, 'FLORES', 7, h=1.8, m='roof_green')
    planter(-4, 1, 10.5, 3.5)
    planter(3, 3, 10.5, 3.0, rot=math.pi/2)

def academia():
    asset(CAT, 'Academia')
    b = Body(0, 0, 0, 44, 16, 11)
    box('Fundacao', (0, 0, .4), (46, 18, .8), 'stone', col=True)
    body('Ala', b, 'wall_peach')
    band(b, 3.5, 'roof_orange', t=.6, grow=.1)
    window_row(b, 'S', 7, 6, 6.6, 3.4, 3.2, lit_every=3)
    skirt(b, 11.4, 2.6, 1.6, 'roof_orange')
    flat_roof(b, 'wall_tan')
    c = Body(0, -1, 0, 14, 18, 19)
    body('Torre', c, 'wall_cream')
    door(c, 'S', 0, w=6, h=8, m='wood_light')
    window(c, 'S', 0, 14, 5, 3.4, lit=True)
    gable(Body(0, -1, 0, 14, 18, 19), 19.2, 5, 'roof_red', over=1.2, along='Y')
    box('PlacaAcademia', (0, -10.3, 10.6), (10, .4, 2.4), 'wood', col=False, text='ACADEMIA NINJA')
    box('Emblema', (0, -10.5, 21.0), (2.8, .3, 2.8), 'cloth_red', col=False, emblem='leaf')
    # swing under the tree spot on the west
    for x in (-16, -12):
        box('PosteBalanco', (x, -12, 3.5), (.5, .5, 7), 'wood', col=False)
    box('TraveBalanco', (-14, -12, 7), (5, .5, .5), 'wood', col=False)
    rod('Corda', (-14.5, -12, 7), (-14.5, -12, 2.2), .12, 'rope')
    rod('Corda', (-13.5, -12, 7), (-13.5, -12, 2.2), .12, 'rope')
    box('Assento', (-14, -12, 2.1), (1.6, .8, .25), 'wood', col=False)

def muralha_modulo():
    """20-stud wall segment. Wall runs along X, village side = +Y."""
    asset(CAT, 'Muralha_Modulo')
    box('BaseMuralha', (0, 0, 1.5), (20.2, 5, 3), 'stone', col=True)
    box('CorpoMuralha', (0, 0, 9), (20.2, 3.6, 13), 'wall_cream', col=True)
    for x in (-10, 0):
        box('JuntaMuralha', (x, -1.85, 8.5), (.35, .2, 11), 'wall_tan', col=False)
    box('FaixaMuralha', (0, -1.9, 12.6), (20.2, .3, .7), 'wood_dark', col=False)
    box('TopoMuralha', (0, 0, 15.8), (20.6, 4.4, .8), 'wood_dark', col=True)
    wedge('CoberturaExterna', (0, -2.6, 15.3), (20.6, 1.6, 1.0), 'roof_green', (0,0,0), col=False)

def torre_vigia():
    asset(CAT, 'Torre_Vigia')
    box('BaseTorre', (0, 0, 1.5), (9, 9, 3), 'stone', col=True)
    b = Body(0, 0, 3, 7, 7, 17)
    body('CorpoTorre', b, 'wall_cream')
    for f in ('S', 'N', 'E', 'W'):
        window(b, f, 0, 17, 2.4, 2.2, sill=False)
    band(b, 12, 'wood_dark', t=.6, grow=.2)
    box('Mirante', (0, 0, 20.4), (9.5, 9.5, .7), 'wood', col=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('PilarMirante', (sx*4.3, sy*4.3, 23), (.6, .6, 5), 'wood_dark', col=False)
    skirt(Body(0, 0, 0, 8.6, 8.6, 0), 26.2, 1.8, 1.4, 'roof_green')
    box('TetoMirante', (0, 0, 26.2), (8.6, 8.6, .6), 'roof_green', col=False)
    wedge('Pinaculo', (0, -2.15, 27.4), (8.6, 4.3, 1.8), 'roof_green', (0,0,0), col=False)
    wedge('Pinaculo', (0, 2.15, 27.4), (8.6, 4.3, 1.8), 'roof_green', (0,0,math.pi), col=False)
    box('Parapeito', (0, -4.6, 21.6), (9.5, .3, 1.8), 'wood_dark', col=False)
    box('Estandarte', (0, -3.8, 14.6), (3.4, .2, 5.5), 'cloth_red', col=False, emblem='leaf')

def quiosque_invocacao():
    asset(CAT, 'Quiosque_Invocacao')
    box('Plataforma', (0, 0, .35), (18, 14, .7), 'stone', col=True)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box('Coluna', (sx*7.6, sy*5.6, 5.5), (1.1, 1.1, 10), 'roof_red', col=True)
            box('Sapata', (sx*7.6, sy*5.6, 1.0), (1.8, 1.8, .6), 'trim_dark', col=False)
    box('VigaTopo', (0, 0, 10.6), (17, 13, 1.0), 'wood_dark', col=False)
    skirt(Body(0, 0, 0, 16, 12, 0), 12.2, 3.0, 2.2, 'roof_red')
    box('TetoCentro', (0, 0, 11.6), (16, 12, 1.2), 'roof_red', col=False)
    gable(Body(0, 0, 0, 12, 8, 0), 12.2, 3.2, 'roof_red', over=.4)
    box('PlacaInvocacao', (0, -7.2, 9.4), (9, .4, 1.8), 'wood', col=False, text='INVOCACAO')
    paper_lantern(-5.5, -6.6, 8.6)
    paper_lantern(5.5, -6.6, 8.6)

def guarita_portao():
    asset(CAT, 'Guarita_Portao')
    b = Body(0, 0, 0, 9, 6, 7.5)
    box('Base', (0, 0, .3), (10, 7, .6), 'stone', col=True)
    body('Guarita', b, 'wall_cream')
    box('Balcao', (0, -3.2, 3.4), (8.6, .6, .4), 'wood', col=False)
    plate(b, 'S', 0, 5.4, 7.6, 3.2, .2, 'dark_void', 'AberturaGuarita', out=.05)
    box('TetoGuarita', (0, -.8, 7.9), (11, 9, .6), 'roof_green', col=True)
    box('PlacaGuarita', (0, -3.8, 9), (6, .35, 1.6), 'wood', col=False, text='RECEPCAO')

def build_all():
    for fn in (casa_p_duas_aguas, casa_p_laje_caixa, casa_m_varanda_escada, casa_m_escalonada,
               casa_g_tres_andares, torre_cilindrica, loja_ramen, loja_dango, loja_armas, loja_flores,
               academia, muralha_modulo, torre_vigia, quiosque_invocacao, guarita_portao):
        fn()
