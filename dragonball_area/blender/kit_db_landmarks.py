# DRAGONBALL_LANDMARKS.  Origin = ground centre, front = -Y.
from dblib import *
from kit_db_tech import capsule_x, capsule_y
from kit_db_buildings import sphere_r_at, round_door

def complexo():
    """Main landmark: Capsule refinery HQ (footprint ~110 x 90, origin on the plateau top)."""
    asset('DRAGONBALL_LANDMARKS', 'Complexo_Capsule')
    R = 30.0
    # drum + dome
    disc('Tambor', (0, 0, 4), R, 8, 'cc_white', True)
    disc('TamborFaixa', (0, 0, 6.2), R + .15, 1.6, 'cc_blue', False)
    disc('TamborRodape', (0, 0, .5), R + .6, 1, 'cc_grey', True)
    ball('Cupula', (0, 0, 8), R*2, 'cc_white', col=True)
    for (z, m, t) in ((20, 'cc_blue', 1.6), (31, 'cc_blue', 1.2)):
        disc('AnelCupula', (0, 0, z), sphere_r_at(R, z - 8) + .2, t, m, False)
    disc('Lanterna', (0, 0, 37.6), 6, 1.2, 'cc_grey', False)
    dome('LanternaVidro', (0, 0, 38.2), 4.4, 'cc_window', sink=.1)
    ball('NucleoKi', (0, 0, 39), 3.4, 'ki_cyan', light='110,230,255,60,1.6', fx='ki')
    for k in range(14):
        a = k/14*2*PI
        if abs(a - 3*PI/2) < .35: continue
        rr = sphere_r_at(R, 14 - 8)
        porthole('Janela', (math.cos(a)*rr, math.sin(a)*rr, 14), 1.5, a, depth=.8)
    # giant emblem + lettering on the front of the dome
    M = frame((0, -sphere_r_at(R, 25 - 8) + .6, 25), (-.62, 0, 0))
    xf('B', 'EmblemaCupula', M, (0, 0, 0), (13, .6, 13), 'cc_white', emblem='capsule', ink='38,82,158')
    box('LetreiroSuporte', (0, -R - 4.5, 11.5), (36, 1.4, 5.4), 'cc_blue', (0, 0, 0), False)
    box('Letreiro', (0, -R - 5.25, 11.5), (34, .2, 4.4), 'cc_blue', (0, 0, 0), False, text='CAPSULE CORP.', textcolor='255,255,255')
    for x in (-15, 15):
        disc('LetreiroPoste', (x, -R - 4.5, 4.4), .5, 8.8, 'cc_grey', False)
    # entrance portico
    capsule_x('Marquise', (0, -R - 1, 9), 2.2, 14, 'cc_white')
    for x in (-7, 7):
        disc('Coluna', (x, -R - 2, 4), 1, 8, 'cc_white', False)
    box('Porta', (0, -R + .3, 3.6), (10, 1.2, 7.2), 'cc_window', (0, 0, 0), False)
    box('PortaMoldura', (0, -R + .1, 7.6), (11, 1.4, .8), 'cc_grey', (0, 0, 0), False)
    for i in range(3):
        box('Degrau', (0, -R - 3 - i*1.4, .6 - i*.2 - .2), (16, 1.4, .4 + (2-i)*.2), 'cc_grey', (0, 0, 0), True)
    # annex domes + connecting tubes
    for (x, y, r, m, acc) in ((-44, 14, 13, 'cc_yellow', 'cc_orange'), (-36, -26, 9, 'cc_white', 'cc_blue'), (40, -28, 10, 'cc_cream', 'cc_blue')):
        disc('AnexoBase', (x, y, 2.5), r, 5, 'cc_white', True)
        ball('Anexo', (x, y, 5), r*2, m, col=True)
        disc('AnexoFaixa', (x, y, 5.6), r + .12, 1.2, acc, False)
        for k in range(5):
            a = k/5*2*PI + .3
            rr = sphere_r_at(r, 3.4)
            porthole('JanelaAnexo', (x + math.cos(a)*rr, y + math.sin(a)*rr, 8.4), .8, a)
    capsule_x('TuboAnexo', (-36.5, 10, 7), 2.4, 13, 'cc_white')
    pipe('TuboAnexo', [(-30.5, -22, 6), (-22.5, -16.2, 6)], 2, 'cc_white', joints=False)
    pipe('TuboAnexo', [(33, -23, 6), (23.8, -16.6, 6)], 2, 'cc_white', joints=False)
    for p in ((-30.5, -22, 6), (33, -23, 6)):
        cyl('TuboAnel', p, 2.4, .8, 'cc_blue', 'Z', False)
    # mushroom tower with observation deck and antenna
    tx, ty = 40, 26
    disc('TorreBase', (tx, ty, 5), 9, 10, 'cc_white', True)
    disc('TorreBaseFaixa', (tx, ty, 8.6), 9.15, 1.2, 'cc_blue', False)
    disc('TorreHaste', (tx, ty, 40), 5, 64, 'cc_white', True)
    for z in (22, 36, 50, 64):
        disc('TorreAnel', (tx, ty, z), 5.4, 1, 'cc_blue', False)
    for z in (28, 44, 58):
        for a in (-PI/2, PI/2 + .3):
            box('TorreJanela', (tx + math.cos(a)*5.02, ty + math.sin(a)*5.02, z), (.3, 2, 3), 'cc_window', (0, 0, a), False)
    ball('TorreBulbo', (tx, ty, 80), 26, 'cc_white', col=True)
    disc('TorreDeck', (tx, ty, 78), 14.5, 2.4, 'cc_blue', False)
    for k in range(16):
        a = k/16*2*PI
        box('TorreDeckJanela', (tx + math.cos(a)*14.55, ty + math.sin(a)*14.55, 78), (.3, 4.6, 1.4), 'ki_cyan', (0, 0, a), False)
    disc('TorreTopo', (tx, ty, 93), 4, 1.2, 'cc_grey', False)
    disc('TorreAntena', (tx, ty, 101), .6, 16, 'cc_metal', False)
    for z in (97, 102):
        disc('TorreAntenaAnel', (tx, ty, z), 2.2 - (z - 97)*.2, .4, 'ki_cyan', False)
    ball('TorreFarol', (tx, ty, 109.6), 2.2, 'cc_red', light='255,80,60,40,1.2')
    box('TorreLogo', (tx, ty - 13.2, 84), (8, .4, 8), 'cc_white', (-.45, 0, 0), False, emblem='capsule', ink='38,82,158')
    # refinery wing: tanks, pipes to the dome, ki conduits
    for (x, y) in ((-46, 36), (-28, 36)):
        place('Refinador', (x, y, 0), 0, 1.25, Ctx.target)
    pipe('TuboRefino', [(-46, 30, 14), (-46, 30, 20), (-24, 26, 20), (-16, 20, 20)], 1.1, 'cc_metal_dark')
    pipe('TuboRefino', [(-28, 30, 10), (-28, 27, 12), (-20, 24, 12)], .9, 'cc_metal')
    for (a, b) in (((-10, -30, .3), (-10, -37, .3)), ((10, -30, .3), (10, -37, .3))):
        box('ConduteKi', ((a[0]+b[0])/2, (a[1]+b[1])/2, .15), (1, abs(b[1]-a[1]), .3), 'ki_cyan', (0, 0, 0), False)
    place('Antena_Parabolica', (22, 34, 0), 2.4, 1.4, Ctx.target)
    place('Gerador', (-17, -33, 0), 0, 1.2, Ctx.target)
    place('Container_Tech', (24, 44, 0), PI/2, 1, Ctx.target)

def santuario():
    """Invocation: seven spheres around the gacha seal, stone dragon coiling a pillar behind."""
    asset('DRAGONBALL_LANDMARKS', 'Santuario_Dragao')
    disc('Degrau', (0, 0, .35), 18.6, .7, 'temple_tile', True)
    disc('Plataforma', (0, 0, .9), 17, 1.8, 'temple_stone', True)
    disc('Selo', (0, 0, 1.85), 12, .12, 'temple_tile', False)
    ring('SeloAnel', (0, 0, 1.95), 11, .5, .14, 'ki_gold', 28, fx='summon')
    ring('SeloAnelInterno', (0, 0, 1.95), 6, .4, .14, 'ki_gold', 20)
    for k in range(7):
        a = PI/2 + k/7*2*PI
        rod('SeloEstrela', (math.cos(a)*11, math.sin(a)*11, 1.96), (math.cos(a + 4*PI/7)*11, math.sin(a + 4*PI/7)*11, 1.96), .35, 'ki_orange', h=.14)
    # 7 pedestals with the spheres (front opening for the path)
    for k in range(7):
        a = -PI/2 + .5 + k*(2*PI - 1.0)/6
        x, y = math.cos(a)*14.5, math.sin(a)*14.5
        disc('Pedestal', (x, y, 3), 1.3, 2.4, 'temple_stone', True)
        disc('PedestalTopo', (x, y, 4.3), 1.6, .3, 'temple_tile', False)
        place('Esfera_Dragao_%d' % (k + 1), (x, y, 4.45), a + PI/2, 1, Ctx.target)
    for (x, y) in ((-16, -16), (16, -16), (-16, 16), (16, 16)):
        disc('Lanterna', (x, y, 4), 1, 6, 'temple_stone', True)
        box('LanternaCasa', (x, y, 7.6), (2.4, 2.4, 1.8), 'temple_roof', (0, 0, 0), False)
        box('LanternaLuz', (x, y, 7.6), (1.6, 2.5, 1.2), 'ki_orange', (0, 0, 0), False, light='255,170,70,14,.7')
    # pillar + dragon
    px, py = 0.0, 24.0
    disc('PilarDragao', (px, py, 17), 4.4, 34, 'db_rock', True)
    for z in (8, 17, 26):
        disc('PilarEstrato', (px, py, z), 4.8, 1.2, 'db_rock_dark', False)
    disc('PilarTopo', (px, py, 34.4), 5, .8, 'db_grass', False)
    n = 46
    pts = []
    for i in range(n):
        t = i/(n - 1)
        ang = -PI/2 + t*2.3*2*PI
        rr = 7.2 - t*.8
        pts.append((px + math.cos(ang)*rr, py + math.sin(ang)*rr, 2.6 + t*30))
    for i, p in enumerate(pts):
        t = i/(n - 1)
        d = 6.2 - 1.4*abs(t - .6)*2 if i > 3 else 3.4 + i*.7
        ball('CorpoDragao', p, d, 'dragon' if i % 2 == 0 else 'dragon_dark', col=(i < 10))
        v = Vector(p) - Vector((px, py, p[2]))
        v.normalize()
        ball('Ventre', tuple(Vector(p) - v*d*.28 + Vector((0, 0, -.4))), d*.62, 'dragon_belly')
        if i % 3 == 1:
            wedge('Crista', tuple(Vector(p) + v*d*.2 + Vector((0, 0, d*.42))), (.6, d*.5, 1.6), 'dragon_horn', (0, 0, math.atan2(v.y, v.x)), False)
    # neck reaching forward over the seal, head looking down at the gacha
    last = Vector(pts[-1])
    neck = [last, last + Vector((-last.x*.35, -5, 3)), last + Vector((-last.x*.7, -10, 3.5)), last + Vector((-last.x, -14, 1.5))]
    for i, p in enumerate(neck[1:]):
        ball('Pescoco', tuple(p), 5 - i*.3, 'dragon')
        ball('PescocoVentre', tuple(p + Vector((0, 0, -1.2))), 3.2, 'dragon_belly')
    hx, hy, hz = tuple(neck[-1] + Vector((0, -3.2, -.6)))
    M = frame((hx, hy, hz), (.35, 0, 0))
    xf('B', 'Cabeca', M, (0, 0, 0), (5.2, 6, 3.8), 'dragon', col=False)
    xf('B', 'Focinho', M, (0, -4.6, -.4), (3.8, 4, 2.6), 'dragon', col=False)
    xf('W', 'Testa', M, (0, -1.8, 2.3), (5, 3.4, 1.2), 'dragon_dark', (0, 0, 0))
    xf('B', 'Mandibula', M, (0, -4, -2.4), (3.2, 4.4, 1), 'dragon_belly', (-.35, 0, 0))
    for s in (-1, 1):
        xf('B', 'Olho', M, (s*1.9, -2.6, 1.1), (1.2, 1.4, .7), 'dragon_eye')
        xf('B', 'Sobrancelha', M, (s*1.9, -2.3, 1.9), (1.8, 1.6, .4), 'dragon_dark', (0, s*.3, 0))
        xf('B', 'Chifre', M, (s*1.8, 3.2, 3.2), (.7, 5.6, .7), 'dragon_horn', (.7, 0, s*.35))
        xf('B', 'Bigode', M, (s*2.6, -5.8, -.6), (4.8, .25, .25), 'ki_gold', (0, s*.25, s*.5))
        xf('B', 'Presa', M, (s*1.2, -6.4, -1.3), (.4, .4, 1.2), 'dragon_horn')
        xf('B', 'Juba', M, (s*2.6, 2.2, 0), (1, 4, 3.4), 'dragon_dark', (0, s*.3, 0))
    # claws gripping the pillar
    for (i, s) in ((8, 1), (16, -1)):
        p = Vector(pts[i])
        tip = p + (Vector((px, py, p.z)) - p).normalized()*3 + Vector((0, 0, -3))
        rod('Braco', tuple(p), tuple(tip), 1.4, 'dragon')
        ball('Garra', tuple(tip), 2, 'dragon_horn')
    box('Placa', (-13, -21, 3.6), (12, .6, 2.6), 'temple_roof', (0, 0, 0), False, text='INVOCACAO', textcolor='255,230,160')
    for x in (-18, -8):
        disc('PlacaPoste', (x, -21, 1.8), .35, 3.6, 'temple_stone', False)

def arena():
    """Boss arena: tournament-style tiled stage with a temple gate at the back."""
    asset('DRAGONBALL_LANDMARKS', 'Arena_Torneio')
    S, H = 44.0, 3.0
    box('Palco', (0, 0, H/2), (S, S, H), 'temple_tile', (0, 0, 0), True)
    box('Borda', (0, 0, H - .2), (S + .8, S + .8, .6), 'temple_stone', (0, 0, 0), False)
    for k in range(1, 8):
        v = -S/2 + k*S/8
        box('Junta', (v, 0, H + .12), (.3, S, .08), 'temple_stone', (0, 0, 0), False)
        box('Junta', (0, v, H + .12), (S, .3, .08), 'temple_stone', (0, 0, 0), False)
    wedge('Escadaria', (0, -S/2 - 4, H/2), (14, 8, H), 'temple_stone', (0, 0, 0), True)
    for (x, y) in ((-S/2, -S/2), (S/2, -S/2), (-S/2, S/2), (S/2, S/2)):
        disc('Pilar', (x, y, 5.5), 1.4, 5, 'temple_stone', True)
        disc('PilarTopo', (x, y, 8.4), 1.9, .8, 'temple_roof', False)
        ball('PilarChama', (x, y, 9.4), 1.4, 'ki_orange', light='255,170,70,16,.8', fx='fire')
    # temple gate behind the stage
    gy = S/2 + 8
    for x in (-12, 12):
        disc('Coluna', (x, gy, 9), 1.6, 18, 'temple_roof', True)
        disc('ColunaBase', (x, gy, .8), 2.4, 1.6, 'temple_stone', False)
    box('Viga', (0, gy, 16.5), (30, 2.4, 2), 'temple_roof', (0, 0, 0), False)
    box('Telhado', (0, gy, 19.2), (36, 7, 1.4), 'temple_stone', (0, 0, 0), False)
    for s in (-1, 1):
        wedge('TelhadoAba', (0, gy + s*4.6, 20.6), (38, 3, 1.6), 'cc_orange', (0, 0, 0 if s < 0 else PI), False)
        wedge('TelhadoPonta', (s*19.5, gy, 20.6), (7, 3, 2.4), 'cc_orange', (0, 0, s*PI/2), False)
    box('TelhadoCumeeira', (0, gy, 21.6), (34, 2, 1.2), 'cc_orange', (0, 0, 0), False)
    box('Placa', (0, gy - 1.3, 13.6), (14, .5, 3), 'temple_stone', (0, 0, 0), False, text='TORNEIO', textcolor='196,64,48')
    for x in (-24, 24):
        box('Arquibancada', (x*1.25, 6, 1.2), (6, 30, 2.4), 'temple_stone', (0, 0, 0), True)
        box('Arquibancada', (x*1.35, 6, 3), (4, 30, 1.6), 'temple_tile', (0, 0, 0), True)

def portal():
    """Progression portal (next island) — Capsule warp ring."""
    asset('DRAGONBALL_LANDMARKS', 'Portal_Capsule')
    disc('Dais', (0, 0, .5), 14, 1, 'cc_grey', True)
    disc('Dais2', (0, 0, 1.3), 11.5, .6, 'cc_white', True)
    ring('DaisLuz', (0, 0, 1.64), 9.5, .4, .1, 'ki_cyan', 24)
    zc, R = 13.0, 10.0
    vring('Anel', (0, 0, zc), R, 2.6, 3.4, 'cc_white', 24, 0, False)
    vring('AnelFaixa', (0, -1.75, zc), R, 1.2, .2, 'cc_blue', 24, 0, False)
    vring('AnelFaixa', (0, 1.75, zc), R, 1.2, .2, 'cc_blue', 24, 0, False)
    vring('AnelLuz', (0, 0, zc), R - 1.5, .5, 3, 'ki_cyan', 24, 0, False)
    cyl('Energia', (0, 0, zc), R - 1.6, .4, 'ki_field', 'Y', False, fx='portal', swirl=1, light='110,230,255,40,1.6')
    ball('NucleoEnergia', (0, 0, zc), 3, 'ki_white')
    for a in (PI/2, PI/2 + 2*PI/3, PI/2 + 4*PI/3):
        x, z = math.cos(a)*(R + 1.2), zc + math.sin(a)*(R + 1.2)
        capsule_y('Grampo', (x, 0, z), 1.3, 3.6, 'cc_blue')
    for s in (-1, 1):
        box('Pe', (s*7, 0, 3.5), (3, 4, 5), 'cc_white', (0, 0, s*.0), True)
        place('Torre_Energia', (s*15.5, 1, 0), 0, 1.1, Ctx.target)
        place('Terminal', (s*6, -9.5, 1.6), 0, 1, Ctx.target)
    box('Placa', (0, -2.2, zc + R + 4.6), (18, .5, 3.4), 'cc_blue', (0, 0, 0), False, text='PROXIMA ILHA', textcolor='255,255,255')
    box('Placa2', (0, -2.2, zc + R + 2), (18, .5, 1.6), 'cc_navy', (0, 0, 0), False, text='MONTE NATAGUMO', textcolor='150,236,255')
    for x in (-8, 8):
        disc('PlacaSuporte', (x, 0, zc + R + 1.2), .35, 3, 'cc_grey', False)
    wedge('Rampa', (0, -16, .5), (10, 4, 1), 'cc_grey', (0, 0, 0), True)

def mine_entrance():
    """Capsule mine portal set into the mountain; tunnel 22 wide, origin at the mouth, tunnel goes +Y."""
    asset('DRAGONBALL_LANDMARKS', 'Entrada_Mina')
    for s in (-1, 1):
        box('Contraforte', (s*15, -1, 9), (6, 8, 18), 'cc_grey', (0, 0, 0), True)
        wedge('ContraforteRampa', (s*15, -7, 4), (6, 4, 8), 'cc_grey', (0, 0, 0), False)
        for z in range(2, 17, 3):
            box('Listra', (s*15, -5.05, z), (6.05, .1, 1.4), 'cc_orange' if (z // 3) % 2 == 0 else 'cc_navy', (0, 0, 0), False)
    box('Verga', (0, -1, 20), (36, 8, 4), 'cc_white', (0, 0, 0), True)
    box('VergaFaixa', (0, -5.05, 20), (36, .1, 1), 'cc_blue', (0, 0, 0), False)
    box('Letreiro', (0, -5.4, 24.6), (20, .6, 4), 'cc_blue', (0, 0, 0), False, text='MINA CAPSULE', textcolor='255,255,255')
    box('LogoMina', (-14, -5.2, 24.6), (4.4, .3, 4.4), 'cc_white', (0, 0, 0), False, emblem='capsule')
    box('LogoMina', (14, -5.2, 24.6), (4.4, .3, 4.4), 'cc_white', (0, 0, 0), False, emblem='capsule')
    for y in (0, 12, 24):
        place('Arco_Mina', (0, y, 0), 0, 1, Ctx.target)
    for (x, y) in ((-16, -9), (16, -9)):
        place('Luminaria_Mina', (x, y, 0), 0, 1, Ctx.target)
    ball('LuzAlerta', (0, -5.5, 17.2), 1.4, 'cc_orange', light='255,160,60,20,.8')

def build():
    complexo(); santuario(); arena(); portal(); mine_entrance()
