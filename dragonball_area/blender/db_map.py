# Vale Capsule map composition (uses terrain/geometry helpers from db_layout).
from db_layout import *

def rect(name, x0, x1, y0, y1, m='db_path', z=.16, col=False):
    return box(name, ((x0+x1)/2, (y0+y1)/2, z/2), (x1-x0, y1-y0, z), m, col=col)

def face_rz(nx, ny):
    """rz that turns an asset's -Y front toward direction (nx, ny)."""
    return math.atan2(nx, -ny)

# ---------------------------------------------------------------- PATHS + ARRIVAL PAD
def paths():
    Pt = G('DRAGONBALL_TERRAIN/Caminhos'); into(Pt)
    # arrival landing pad (raised lookout: the first view sees over the whole valley)
    px, py, pr = PAD
    disc('PistaPouso', (px, py, PAD_Z/2), pr, PAD_Z, 'cc_white', True)
    disc('PistaFaixa', (px, py, PAD_Z - 1.4), pr + .15, 1.2, 'cc_blue', False)
    disc('PistaRodape', (px, py, .6), pr + .8, 1.2, 'cc_grey', True)
    disc('PistaTopo', (px, py, PAD_Z + .1), pr - .8, .2, 'db_paving', True)
    ring('PistaLuz', (px, py, PAD_Z + .24), pr - 2.2, .5, .1, 'ki_cyan', 36)
    box('PistaEmblema', (px, py - 4, PAD_Z + .23), (14, 14, .06), 'cc_white', col=False, emblem='capsule', emblemface='Top', ink='38,82,158')
    wedge('RampaPista', (0, -150, PAD_Z/2), (18, 20, PAD_Z), 'cc_grey', (0, 0, PI), True)
    for s in (-1, 1):
        rod('GuardaRampa', (s*9.3, -160, PAD_Z + 1.4), (s*9.3, -140, 1.4), .45, 'cc_blue', True, h=.45)
    # avenue and ring road around the quarry (10 wide, 10 studs from the rim)
    rect('Avenida', -9, 9, -140, -102, 'db_path')
    for x in (-9.6, 9.6):
        box('FaixaAvenida', (x, -121, .1), (1.2, 38, .2), 'db_line', col=False)
    rect('AnelSul', -86, 96, -112, -102, 'db_paving')
    rect('AnelNorte', -86, 96, 54, 64, 'db_paving')
    rect('AnelOeste', -86, -76, -112, 64, 'db_paving', .15)
    rect('AnelLeste', 86, 96, -112, 64, 'db_paving', .15)
    rect('AcessoSul', -2, 14, -102, -92, 'db_path', .14)
    rect('AcessoNorte', -2, 14, 44, 54, 'db_path', .14)
    rect('AcessoOeste', -76, -64, -32, -16, 'db_path', .14)
    rect('AcessoLeste', 76, 86, -32, -16, 'db_path', .14)
    # west town
    rect('RuaVila', -176, -86, -45, -35, 'db_asphalt')
    rect('RuaVilaNS', -125, -115, -104, 40, 'db_asphalt', .15)
    disc('PracaVila', (-120, -40, .1), 15, .2, 'db_paving', False)
    disc('PracaVilaCanteiro', (-120, -40, .3), 6, .4, 'db_grass_light', False)
    for x in (-160, -140, -100):
        box('FaixaRua', (x, -40, .17), (6, .5, .04), 'flower_white', col=False)
    # spurs
    rect('TrilhaSantuario', -42, -9, -138, -126, 'db_path', .14)
    rect('TrilhaArena', 9, 58, -144, -132, 'db_path', .14)
    rect('TrilhaCratera', 96, 128, 6, 18, 'db_dirt', .14)
    rect('TrilhaPortal', 144, 156, 50, 98, 'db_path', .14)
    rect('TrilhaPortalLigacao', 96, 156, 40, 50, 'db_path', .15)
    # canyon trail to the Ki cave
    rect('TrilhaCanion', -126, -114, 40, 156, 'db_dirt', .14)
    rect('TrilhaCanionOeste', -158, -114, 150, 162, 'db_dirt', .15)
    rect('TrilhaCaverna', -158, -146, 150, 170, 'db_dirt', .16)
    # mine yard
    rect('PatioMina', -40, 10, 64, 166, 'db_dirt', .14)

# ---------------------------------------------------------------- WATER
def water():
    W = G('DRAGONBALL_TERRAIN/Agua'); into(W)
    cx, cy, rx, ry = LAKE
    for i in range(-9, 9):
        t = (i + .5)/9
        ym = cy + t*ry
        k = math.sqrt(max(0, 1 - t*t))
        w = 2*rx*k + 6
        box('LeitoLago', (cx, ym, -7), (w, ry/9 + .3, 2), 'db_rock_dark', col=True)
        box('Agua', (cx, ym, -2.3), (w - 1, ry/9 + .1, .6), 'db_water', col=False)
    for i in range(40):
        a, a2 = i/40*2*PI, (i+1)/40*2*PI
        x1, y1 = cx + math.cos(a)*(rx+2), cy + math.sin(a)*(ry+2)
        x2, y2 = cx + math.cos(a2)*(rx+2), cy + math.sin(a2)*(ry+2)
        box('Margem', ((x1+x2)/2, (y1+y2)/2, -2), (math.hypot(x2-x1, y2-y1) + 1.2, 7, 4.3), 'db_sand', (0, 0, math.atan2(y2-y1, x2-x1)), True)
    wy = mountain_front(cx) - 1
    for i in range(4):
        box('Cachoeira', (cx - 6 + i*4, wy, 30), (4.1, 1.4, 64), 'db_water', col=False, fx='waterfall' if i == 1 else '')
    box('PocoCachoeira', (cx, wy - 8, -1.9), (22, 12, .6), 'db_foam', col=False, fx='mist')

# ---------------------------------------------------------------- QUARRY (Pedreira Energetica)
def _ramp_hit(x, y, pad=1.5):
    for (a0, a1, b0, b1, hs) in QRAMPS.values():
        if hs in 'NS':
            rim_y = b0 if hs == 'S' else b1
            if a0 - pad <= x <= a1 + pad and abs(y - rim_y) < 10: return True
        else:
            rim_x = a0 if hs == 'W' else a1
            if b0 - pad <= y <= b1 + pad and abs(x - rim_x) < 10: return True
    return False

def quarry():
    Q = G('DRAGONBALL_MINING/Pedreira_Energetica'); into(Q)
    box('PisoPedreira', (QC[0], QC[1], QFLOOR - 4), (QRX*2 + 6, QRY*2 + 6, 8), 'db_dirt', col=True)
    N = 64
    deco_i = 0
    for i in range(N):
        t0, t1 = i/N*2*PI, (i+1)/N*2*PI
        x1, y1 = quarry_point(t0, 1.5)
        x2, y2 = quarry_point(t1, 1.5)
        mx, my = (x1+x2)/2, (y1+y2)/2
        if _ramp_hit(mx, my): continue
        ang = math.atan2(y2-y1, x2-x1)
        L = math.hypot(x2-x1, y2-y1) + 1.4
        nx, ny = QC[0] - mx, QC[1] - my
        nl = math.hypot(nx, ny); nx, ny = nx/nl, ny/nl
        box('ParedePedreira', (mx - nx*2.5, my - ny*2.5, (QFLOOR + .3)/2), (L, 8, -QFLOOR + .3), 'db_rock', (0, 0, ang), True)
        box('BordaPedreira', (mx - nx*2.5, my - ny*2.5, .35), (L + .2, 8.2, .4), 'db_rock_light', (0, 0, ang), False)
        for (zz, mm, hh) in ((-2.8, 'db_rock_dark', 1.2), (-6.4, 'db_rock_red', 1.6)):
            box('Estrato', (mx + nx*1.7, my + ny*1.7, zz), (L, .8, hh), mm, (0, 0, ang), False)
        if i % 4 == 1:
            name = 'Cristal_Parede' if deco_i % 2 == 0 else 'Veio_Ki'
            fz = QFLOOR + (2.5 if name == 'Cristal_Parede' else 1.5)
            P(name, mx + nx*1.3, my + ny*1.3, face_rz(nx, ny), 1.2 if name == 'Cristal_Parede' else 1, fz)
            deco_i += 1
    rot = {'S': PI, 'N': 0.0, 'W': PI/2, 'E': -PI/2}
    for name, (a0, a1, b0, b1, hs) in QRAMPS.items():
        cx, cy = (a0+a1)/2, (b0+b1)/2
        width, run = ((a1-a0), (b1-b0)) if hs in 'NS' else ((b1-b0), (a1-a0))
        wedge('Rampa' + name, (cx, cy, QFLOOR/2), (width, run, -QFLOOR), 'db_dirt_dark', (0, 0, rot[hs]), True)
        for s in (-1, 1):
            if hs in 'NS':
                hi, lo = (b0, b1) if hs == 'S' else (b1, b0)
                g = cx + s*(width/2 + .4)
                a, b = (g, hi), (g, lo)
            else:
                hi, lo = (a0, a1) if hs == 'W' else (a1, a0)
                g = cy + s*(width/2 + .4)
                a, b = (hi, g), (lo, g)
            rod('GuardaRampa', (a[0], a[1], 1.6), (b[0], b[1], QFLOOR + 1.6), .5, 'cc_grey', True, h=2.4)
            rod('LuzRampa', (a[0], a[1], 2.95), (b[0], b[1], QFLOOR + 2.95), .55, 'ki_cyan', h=.25)
    M = 72
    pts = [quarry_point(i/M*2*PI, 6.5) for i in range(M)]
    for i in range(M):
        x1, y1 = pts[i]; x2, y2 = pts[(i+1) % M]
        if _ramp_hit((x1+x2)/2, (y1+y2)/2, 2.5): continue
        if i % 2 == 0:
            disc('PosteGrade', (x1, y1, 1.7), .3, 3.4, 'cc_grey', False)
        rod('Corrimao', (x1, y1, 3.1), (x2, y2, 3.1), .35, 'cc_blue')
        rod('BarraGrade', (x1, y1, 1.8), (x2, y2, 1.8), .2, 'cc_white')
        rod('GradeColisao', (x1, y1, 1.7), (x2, y2, 1.7), .6, 'invisible', True, h=3.4)
    for (x, y) in ((-8, -98), (20, -98), (-8, 50), (20, 50), (-70, -38), (-70, -10), (82, -38), (82, -10)):
        P('Torre_Energia', x, y, 0, .8)
    for (x, y, rz, txt) in ((-26, -99, 0, 'PEDREIRA ENERGETICA'), (34, 51, PI, 'PEDREIRA ENERGETICA')):
        box('PlacaPedreira', (x, y, 5.4), (15, .5, 2.6), 'cc_blue', (0, 0, rz), False, text=txt, textcolor='255,255,255')
        for dx in (-6.5, 6.5):
            disc('PostePlaca', (x + dx, y, 2.6), .3, 5.2, 'cc_grey', False)
    P('Broca_Mineradora', -62, 44, .4)
    P('Broca_Mineradora', 76, -92, 2.2, .9)
    P('Painel_Capsule', -58, -96, face_rz(.25, -1), .9)
    P('Luminaria_Mina', -70, -84, face_rz(1, 1))
    P('Luminaria_Mina', 80, 38, face_rz(-1, -1))
    P('Luminaria_Mina', -72, 34, face_rz(1, -1))
    P('Container_Tech', 80, -72, PI/2)
    P('Caixa_Carga', 76, -58, .3)
    # conveyor: from the NE rim up to the refinery plateau (ore -> refinery story)
    A, B = Vector((40, 46, 3.8)), Vector((40, PLATEAU[2] + 2, PLAT_Z + 3.8))
    rod('EsteiraEstrutura', tuple(A - Vector((0, 0, .6))), tuple(B - Vector((0, 0, .6))), 4.6, 'cc_grey', True, h=1)
    rod('EsteiraCinta', tuple(A), tuple(B), 3.8, 'cc_rubber', h=.3)
    for s in (-1, 1):
        rod('EsteiraLateral', tuple(A + Vector((s*2.3, 0, .3))), tuple(B + Vector((s*2.3, 0, .3))), .3, 'cc_blue', h=.9)
    for k in range(1, 4):
        p = A.lerp(B, k/4)
        for s in (-1, 1):
            disc('EsteiraPerna', (p.x + s*1.8, p.y, (p.z - .8)/2), .3, p.z - .8, 'cc_metal_dark', False)
    pitch = math.atan2(B.z - A.z, B.y - A.y)
    for k in range(7):
        p = A.lerp(B, (k + .5)/7)
        box('MinerioNaEsteira', (p.x + (k % 2 - .5)*1.2, p.y, p.z + .6), (1.1, 1.3, 1), 'ki_cyan' if k % 3 == 0 else 'db_rock_dark', (pitch, 0, 0), False)
    P('Gerador', 28, 38, PI/2, .8)
    P('Terminal', 50, 40, PI)

# ---------------------------------------------------------------- PLATEAU + CAPSULE COMPLEX
def plateau():
    L = G('DRAGONBALL_LANDMARKS/Complexo'); into(L)
    x0, x1, y0, y1 = PLATEAU
    box('Plato', ((x0+x1)/2, (y0+y1)/2, (PLAT_Z - 2)/2), (x1-x0, y1-y0, PLAT_Z + 2), 'cc_grey', col=True)
    box('PlatoPiso', ((x0+x1)/2, (y0+y1)/2, PLAT_Z + .1), (x1-x0 - .6, y1-y0 - .6, .2), 'db_paving', col=True)
    box('PlatoFaixa', ((x0+x1)/2, y0 - .06, PLAT_Z - 2), (x1-x0, .2, 1.2), 'cc_blue', col=False)
    box('PlatoFaixa', (x0 - .06, (y0+y1)/2, PLAT_Z - 2), (.2, y1-y0, 1.2), 'cc_blue', col=False)
    box('PlatoFaixa', (x1 + .06, (y0+y1)/2, PLAT_Z - 2), (.2, y1-y0, 1.2), 'cc_blue', col=False)
    for x in range(int(x0) + 8, int(x1), 16):
        if 68 < x < 92: continue
        box('PlatoPilastra', (x, y0 - .4, PLAT_Z/2), (2, .8, PLAT_Z), 'cc_white', col=False)
    wedge('RampaPlato', (80, 70, PLAT_Z/2), (18, 16, PLAT_Z), 'cc_grey', (0, 0, 0), True)
    for s in (-1, 1):
        rod('GuardaPlato', (80 + s*9.3, 62, 1.4), (80 + s*9.3, 78, PLAT_Z + 1.4), .45, 'cc_blue', True, h=.45)
    for k in range(1, 8):
        box('DegrauPlato', (80, 62 + k*2, k*PLAT_Z/8 + .03), (17.6, .25, .12), 'cc_white', col=False)
    wedge('RampaPortal', (x1 + 8, 128, PLAT_Z/2), (12, 16, PLAT_Z), 'cc_grey', (0, 0, PI/2), True)
    P('Complexo_Capsule', COMPLEX[0], COMPLEX[1], 0, 1, PLAT_Z)
    P('Nave_Gravidade', 26, 102, .5, .85, PLAT_Z)
    disc('PistaNave', (26, 102, PLAT_Z + .3), 12, .3, 'cc_white', False)
    ring('PistaNaveLuz', (26, 102, PLAT_Z + .48), 11, .4, .08, 'ki_cyan', 24)
    for (x, y) in ((16, 84), (132, 84), (16, 158)):
        P('Poste_Luz_Tech', x, y, face_rz((COMPLEX[0]-x), (COMPLEX[1]-y)), 1, PLAT_Z)
    P('Bandeira_Capsule', 44, 82, 0, 1, PLAT_Z)
    P('Bandeira_Capsule', 116, 82, 0, 1, PLAT_Z)
    P('Drone', 50, 88, .4, 1.4, PLAT_Z + 14)
    P('Drone', 118, 104, 2, 1.4, PLAT_Z + 22)
    P('Drone', -8, 20, 1, 1.4, 16)

# ---------------------------------------------------------------- MOUNTAIN + MINE + CANYON + CAVE
def mountain():
    M = G('DRAGONBALL_ROCKS/Montanha'); into(M)
    rs = rng(41)
    x = -214.0
    while x < 216:
        front = mountain_front(x)
        if MINE_C - 30 < x < MINE_C + 30 or CAVE[0] - 20 < x < CAVE[1] + 16:
            x += 6; continue
        base = 1.0 + .7*max(0, (-x - 60)/140) + .35*max(0, (x - 40)/160)
        s = base*rs.uniform(.85, 1.15)
        name = 'Penhasco' if s > 1.05 or abs(x - MINE_C) > 70 else 'Penhasco_Baixo'
        P(name, x, front + 17*s, rs.uniform(-.12, .12), s)
        P('Penhasco', x + rs.uniform(-8, 8), front + 34*s + 22, rs.uniform(-.2, .2), s*rs.uniform(1.15, 1.45))
        x += 30*s*rs.uniform(.72, .9)
    fy = mountain_front(MINE_C)
    for sx in (-1, 1):
        P('Penhasco', MINE_C + sx*36, fy + 17, 0, 1.0)
    P('Penhasco', MINE_C, fy + 58, .1, 1.35)
    Mn = G('DRAGONBALL_MINING/Mina_Capsule'); into(Mn)
    P('Entrada_Mina', MINE_C, fy, 0, 1, 0)
    for sx in (-1, 1):
        box('ParedeTunel', (MINE_C + sx*15, fy + 20, 12), (8, 40, 24), 'db_rock_dark', col=True)
    box('TetoTunel', (MINE_C, fy + 20, 25), (38, 40, 6), 'db_rock', col=True)
    box('FundoTunel', (MINE_C, fy + 41, 12), (24, 2, 24), 'dark_void', col=True)
    P('Penhasco_Baixo', MINE_C, fy + 22, 0, 1.0, 26)
    for (dx, dy, n, rz, s) in ((-8, 36, 'Cristal_Ki', .4, 1.1), (8, 30, 'Cristal_Ki_Ouro', 2, 1.1), (6, 38, 'Cristal_Ki_G', 3.4, .6)):
        P(n, MINE_C + dx, fy + dy, rz, s)
    for (dx, dy) in ((-10.8, 12), (10.8, 20), (-10.8, 28)):
        P('Cristal_Parede', MINE_C + dx, fy + dy, face_rz(-math.copysign(1, dx), 0), 1, 3)
    for y in range(int(fy) - 60, int(fy) + 36, 8):
        P('Trilho_Tech', MINE_C, y, 0, 1, .15)
    P('Vagoneta_Tech', MINE_C, fy - 20, 0, 1, .3)
    box('LuzTunel', (MINE_C, fy + 24, 21.5), (1, 1, 1), 'ki_cyan', col=False, light='110,230,255,40,1.3')
    # mine yard dressing (edges only; the middle stays free for ores)
    for (n, x, y, rz) in (('Container_Tech', -34, 150, PI/2), ('Caixa_Carga', -34, 138, .3), ('Barril_Metal', 4, 146, 0),
                          ('Barril_Metal', 6, 142, 0), ('Luminaria_Mina', -36, 90, face_rz(1, 0)), ('Luminaria_Mina', 6, 120, face_rz(-1, 0)),
                          ('Painel_Capsule', -30, 70, face_rz(.3, -1)), ('Cone', -2, 70, 0), ('Cone', 2, 70, 0)):
        P(n, x, y, rz, .8 if n == 'Painel_Capsule' else 1)
    # canyon of pillars (natural landmark)
    C = G('DRAGONBALL_ROCKS/Canion_Colunas'); into(C)
    for (n, x, y, s, rz) in (('Pilar_C', -178, 128, 1.5, .3), ('Pilar_A', -150, 136, 1.35, 1.2), ('Pilar_B', -100, 152, 1.2, 2),
                             ('Rocha_Equilibrio', -172, 62, 1.15, .6), ('Pilar_B', -142, 66, 1.0, 4), ('Pilar_A', -186, 96, .95, 2.2),
                             ('Pilar_C', -48, 172, 1.1, 1), ('Pilar_B', 176, 146, 1.3, .5), ('Pilar_A', 146, -126, .75, 3),
                             ('Pilar_C', 184, 30, .7, 2.5), ('Pilar_B', -160, -128, .8, 1.4), ('Rocha_Equilibrio', 168, -64, .75, 2)):
        P(n, x, y, rz, s)
    P('Arco_Rocha', -120, 126, 0, 1.0)
    P('Mesa_Natural', -174, 34, .3, 1)
    for (x, y, s) in ((-134, 150, 1.2), (-106, 136, 1), (-162, 112, 1.1), (-190, 150, 1.3), (-104, 72, .8), (-150, 44, 1)):
        P('Rocha_L', x, y, rs.uniform(0, 6), s)
    for (x, y) in ((-132, 116), (-108, 112), (-164, 158), (-168, 78), (-96, 92)):
        P('Rocha_M', x, y, rs.uniform(0, 6), rs.uniform(.8, 1.2))
    # Ki cave (hidden behind the canyon)
    Cv = G('DRAGONBALL_MINING/Caverna_Ki'); into(Cv)
    x0, x1, y0, y1 = CAVE
    box('TetoCaverna', ((x0+x1)/2, (y0+y1)/2, 21), (x1-x0+8, y1-y0+8, 4), 'db_rock_deep', col=True)
    box('ParedeFundo', ((x0+x1)/2, y1+2, 10), (x1-x0+8, 4, 20), 'db_rock_deep', col=True)
    box('ParedeOeste', (x0-2, (y0+y1)/2, 10), (4, y1-y0+8, 20), 'db_rock_deep', col=True)
    box('ParedeLeste', (x1+2, (y0+y1)/2, 10), (4, y1-y0+8, 20), 'db_rock_deep', col=True)
    box('FrenteA', ((x0 - 4 - 158)/2, y0 - 2, 10), (-158 - (x0 - 4), 4, 20), 'db_rock', col=True)
    box('FrenteB', ((-146 + x1 + 4)/2, y0 - 2, 10), (x1 + 4 + 146, 4, 20), 'db_rock', col=True)
    box('Verga', (-152, y0 - 2, 17), (12.5, 4, 6), 'db_rock', col=True)
    P('Penhasco', (x0+x1)/2, y0 + 16, .05, 1.25, 23)
    for (n, x, y, rz, s) in (('Cristal_Ki_Roxo', -166, 190, .4, 1.3), ('Cristal_Ki_Ouro', -140, 190, 2.2, 1.2), ('Cristal_Ki_G', -167, 176, 1, .6),
                             ('Cristal_Ki_Roxo', -137, 172, 4, 1), ('Cristal_Ki', -154, 193, 5, 1)):
        P(n, x, y, rz, s)
    P('Cristal_Parede', -171.6, 184, face_rz(1, 0), 1.1, 5)
    P('Cristal_Parede', -132.4, 180, face_rz(-1, 0), 1.1, 5)
    for (a, b) in (((-170, 170, 12), (-160, 172, 16)), ((-140, 195.8, 8), (-150, 195.8, 14)), ((-132.2, 176, 3), (-132.2, 186, 9))):
        rod('FissuraKi', a, b, .45, 'ki_purple', h=.45)
    box('LuzCaverna', (-152, 181, 18), (1, 1, 1), 'ki_purple', col=False, light='200,130,255,44,1.5', fx='summon')
    box('PlacaCaverna', (-152, y0 - 4.3, 12), (12, .5, 2.2), 'db_rock_dark', col=False, text='CAVERNA DE KI', textcolor='210,160,255')

# ---------------------------------------------------------------- CRATER
def crater():
    Cr = G('DRAGONBALL_MINING/Cratera'); into(Cr)
    cx, cy = CRATER
    import dbshapes
    dbshapes.crater_bowl('Cratera_Malha', Cr, cx, cy, 17, CR_R - 1, 6, 2.6)
    for (r, top) in ((CR_R - 1, -2.0), (CR_R - 6, -4.0), (CR_R - 11, -6.0)):
        disc('CrateraColisao', (cx, cy, (top - 12)/2), r, 12 + top, 'invisible', True)
    rs = rng(55)
    for i in range(22):
        a = i/22*2*PI
        if abs(a - PI) < .4: continue
        r = CR_R + rs.uniform(-.5, 1.5)
        x, y = cx + math.cos(a)*r, cy + math.sin(a)*r
        if i % 3 == 0:
            P('Rocha_M', cx + math.cos(a)*(r + 5), cy + math.sin(a)*(r + 5), a, rs.uniform(.7, 1.1), 1)
    wedge('RampaCratera', (cx - CR_R + 7, cy, -3), (10, 16, 6), 'invisible', (0, 0, PI/2), True)
    e = P('Pod_Espacial', cx + 17, cy + 11, 2.4, 1.2, -4.6)
    e.rotation_euler = (.45, -.3, 2.4)
    for (x, y, rz) in ((cx - 18, cy - 24, .3), (cx + 28, cy - 12, 2), (cx - 8, cy + 28, 4)):
        P('Rocha_Fissura', x, y, rz, 1)
    for (x, y, s) in ((cx + 34, cy + 20, 1.2), (cx + 30, cy - 26, 1.0)):
        P('Rocha_L', x, y, rs.uniform(0, 6), s)
    box('PlacaCratera', (cx - 38, cy + 14, 4.6), (12, .5, 2.4), 'db_rock_dark', (0, 0, PI/2), False, text='CRATERA', textcolor='255,200,120')
    for dy in (-5, 5):
        disc('PostePlaca', (cx - 38, cy + 14 + dy, 2.2), .3, 4.4, 'cc_grey', False)
    box('LuzCratera', (cx, cy, 4), (1, 1, 1), 'ki_gold', col=False, light='255,210,100,40,1.1', fx='ki')

# ---------------------------------------------------------------- DISTRICTS (town + industry)
N_, S_, E_, W_ = PI, 0.0, PI/2, -PI/2     # rz so the front faces north/south/east/west

def districts():
    B = G('DRAGONBALL_BUILDINGS/Vila_Capsule'); into(B)
    for (n, x, y, rz) in (
        ('Apartamento_Redondo', -150, -14, S_), ('Torre_Cogumelo', -96, -16, S_), ('Loja_Lanches', -100, -60, N_),
        ('Loja_Ferramentas', -150, -60, N_), ('Casa_Domo_M', -150, -90, E_), ('Casa_Domo_P', -100, -88, W_),
        ('Casa_Capsula', -96, 16, W_), ('Casa_Domo_Dupla', -152, 20, E_), ('Casa_Antena', -176, -24, E_),
        ('Garagem', -140, -112, N_), ('Laboratorio', -100, 46, S_), ('Casa_Domo_P', -174, 2, E_),
        ('Casa_Domo_M', -130, -142, N_ + .5), ('Casa_Antena', -100, -118, N_ - .3)):
        P(n, x, y, rz)
    P('Capsula_HoiPoi', -120, -40, .6, 1.6, .5)
    P('Veiculo_Hover', -136, -98, .2, 1, 1.2)
    P('Veiculo_Hover', -106, -30, 1.7, 1, 1.4)
    for (x, y, rz) in ((-110, -45.5, 0), (-130, -34.5, PI), (-160, -45.5, 0), (-120, -60, E_), (-120, 10, W_)):
        P('Poste_Luz_Tech', x, y, rz)
    for (x, y, rz) in ((-128, -54, 0), (-112, -26, PI), (-136, 2, E_)):
        P('Banco_Tech', x, y, rz)
    P('Maquina_Venda', -86, -52, W_)
    P('Maquina_Venda', -164, -52, N_)
    Ind = G('DRAGONBALL_BUILDINGS/Industria'); into(Ind)
    P('Deposito', 110, -62, W_)
    P('Fabrica_Pequena', 114, -22, W_)
    P('Casa_Montanha', 146, -88, W_ + .4)
    P('Container_Tech', 106, -88, .2)
    P('Container_Tech', 106, -88, .2, 1, 5.6)
    P('Caixa_Carga', 100, -42, .5)

def landmarks_place():
    L = G('DRAGONBALL_LANDMARKS/Pontos'); into(L)
    P('Santuario_Dragao', SANCT[0], SANCT[1], PI/2)
    P('Arena_Torneio', ARENA[0], ARENA[1], -PI/2)
    P('Portal_Capsule', PORTAL[0], PORTAL[1], face_rz(-1, -1))
    # arrival dressing: flags + lamps along the avenue (kept low so the view stays open)
    A = G('DRAGONBALL_DECORATION/Chegada'); into(A)
    for s in (-1, 1):
        P('Bandeira_Capsule', s*17, -186, 0, 1, PAD_Z)
        P('Terminal', s*12, -168, 0, 1, PAD_Z)
        for y in (-136, -116):
            P('Poste_Luz_Tech', s*12, y, face_rz(-s, 0))
    P('Capsula_HoiPoi', 30, -170, .4, 1.2)
    P('Caixa_Carga', -26, -166, .3)
    P('Caixa_Carga', -30, -168, 1.1, .8)
    P('Barril_Metal', 26, -160, 0)

# ---------------------------------------------------------------- NATURE
def _free(x, y, r=6):
    if not in_poly(x, y) or not in_poly(x*1.05, y*1.05): return False
    if quarry_f(x, y, 20 + r) <= 1: return False
    if lake_f(x, y, 6 + r) <= 1: return False
    if math.hypot(x - CRATER[0], y - CRATER[1]) < CR_R + 8 + r: return False
    if PLATEAU[0] - 6 < x < PLATEAU[1] + 6 and PLATEAU[2] - 22 < y < PLATEAU[3] + 4: return False
    if y > mountain_front(x) - 6 - r: return False
    if -44 < x < 14 and y > 60: return False                         # mine yard
    if abs(x) < 64 and y < -100: return False                          # arrival plaza + sight lines
    if math.hypot(x - SANCT[0], y - SANCT[1]) < 32 + r: return False
    if abs(x - ARENA[0]) < 38 and abs(y - ARENA[1]) < 30: return False
    if math.hypot(x - PORTAL[0], y - PORTAL[1]) < 22: return False
    if -180 < x < -84 and -122 < y < 56: return False                  # town blocks (dressed separately)
    if -128 < x < -112 and 36 < y < 160: return False                 # canyon trail
    if 94 < x < 128 and 0 < y < 24: return False
    if 140 < x < 160 and 36 < y < 100: return False
    if 96 < x < 124 and -96 < y < -8: return False
    return True

def nature():
    V = G('DRAGONBALL_NATURE/Vegetacao'); into(V)
    rs = rng(88)
    placed = []
    tries = 0
    while len(placed) < 95 and tries < 5000:
        tries += 1
        x, y = rs.uniform(-196, 196), rs.uniform(-200, 175)
        big = rs.random() < .45
        r = 9 if big else 6
        if not _free(x, y, r): continue
        if any(math.hypot(x - px, y - py) < pr + r for (px, py, pr) in placed): continue
        placed.append((x, y, r))
        n = 'Arvore_Bola_G' if big else rs.choice(['Arvore_Bola_M', 'Arvore_Bola_M', 'Arvore_Ajisa'])
        P(n, x, y, rs.uniform(0, 6), rs.uniform(.85, 1.15))
        if rs.random() < .5:
            P('Arbusto_Bola', x + rs.uniform(-7, 7), y + rs.uniform(-7, 7), rs.uniform(0, 6), rs.uniform(.8, 1.3))
    # town greenery (manual)
    T = G('DRAGONBALL_NATURE/Vila_Jardins'); into(T)
    for (n, x, y, s) in (('Arvore_Bola_M', -134, -24, 1), ('Arvore_Bola_M', -106, -52, .9), ('Arvore_Ajisa', -164, -76, 1),
                         ('Arvore_Bola_G', -170, -100, 1), ('Arvore_Bola_M', -84, -96, 1), ('Arvore_Ajisa', -132, 30, 1),
                         ('Arvore_Bola_M', -166, 30, 1), ('Arvore_Bola_G', -84, 28, .9), ('Arvore_Ajisa', -164, -8, .9),
                         ('Arvore_Bola_M', -118, -122, 1), ('Arvore_Bola_M', -86, 4, .8)):
        P(n, x, y, rs.uniform(0, 6), s)
    for (x, y) in ((-112, -50), (-128, -30), (-140, -70), (-90, -76), (-160, 8), (-104, 30), (-146, -104), (-80, -120), (-40, -150), (40, -150)):
        P('Flores', x, y, rs.uniform(0, 6), 1)
    for (x, y) in ((-124, -54), (-116, -26), (-88, -40), (-172, -46), (-60, -110), (60, -112), (-30, -112), (26, -112)):
        P('Arbusto_Bola', x, y, rs.uniform(0, 6), rs.uniform(.8, 1.2))
    # lake shore
    Lk = G('DRAGONBALL_NATURE/Lago'); into(Lk)
    cx, cy, rx, ry = LAKE
    for i, a in enumerate((.2, 1.0, 2.1, 2.7, 3.5, 4.3, 5.2, 5.9)):
        x, y = cx + math.cos(a)*(rx + 9), cy + math.sin(a)*(ry + 9)
        if y > mountain_front(x) - 8: continue
        P('Palmeira' if i % 2 == 0 else 'Arvore_Ajisa', x, y, a + 2, rs.uniform(.9, 1.2))
    for a in (.6, 2.4, 3.9, 5.5):
        P('Rocha_M', cx + math.cos(a)*(rx + 3), cy + math.sin(a)*(ry + 3), a, .9, -1)
    # rim rocks + flowers along the island edge
    Rm = G('DRAGONBALL_ROCKS/Borda'); into(Rm)
    for (x, y, ang) in edge_points(70, .975):
        if abs(x) < 50 and y < -150: continue
        if y > mountain_front(x) - 4: continue
        if math.hypot(x - STREAM[-2][0], y - STREAM[-2][1]) < 20: continue
        P(rs.choice(['Rocha_L', 'Rocha_M', 'Rocha_M']), x, y, rs.uniform(0, 6), rs.uniform(.8, 1.4), -2)

# ---------------------------------------------------------------- SKY (background layers)
def sky():
    S = G('DRAGONBALL_DECORATION/Ceu'); into(S)
    rs = rng(7)
    for (x, y, z, s, rz) in ((-270, 30, -20, 1.3, .4), (262, -80, 6, 1.1, 2), (230, 230, 30, .9, 1), (-236, -176, -36, .95, 3),
                             (-120, 300, 50, 1.2, 5), (120, -290, -60, .9, 2.5)):
        P('Ilhota_Flutuante', x, y, rz, s, z)
    for i in range(22):
        a = i/22*2*PI + rs.uniform(-.1, .1)
        r = rs.uniform(250, 340)
        x, y = math.cos(a)*r, math.sin(a)*r
        if -40 < math.degrees(math.atan2(y, x)) + 90 < 40 and y < 0 and rs.random() < .5: continue
        P(rs.choice(['Nuvem_G', 'Nuvem_M']), x, y, rs.uniform(0, 6), rs.uniform(1.2, 2.4), rs.uniform(-70, 120))
    for i in range(10):
        a = rs.uniform(0, 2*PI)
        r = rs.uniform(120, 200)
        P('Nuvem_G', math.cos(a)*r, math.sin(a)*r, rs.uniform(0, 6), rs.uniform(2, 3), rs.uniform(-80, -45))

# ---------------------------------------------------------------- GAMEPLAY MARKERS
def _pit_spots():
    rs = rng(123)
    x0, x1 = QC[0] - QRX, QC[0] + QRX
    y0, y1 = QC[1] - QRY, QC[1] + QRY
    spots = []
    for y in range(int(y0) + 8, int(y1) - 5, 11):
        for x in range(int(x0) + 8, int(x1) - 5, 11):
            px, py = x + rs.uniform(-2, 2), y + rs.uniform(-2, 2)
            if quarry_f(px, py, -9) > 1: continue
            if any(a0 - 5 <= px <= a1 + 5 and b0 - 5 <= py <= b1 + 5 for (a0, a1, b0, b1, hs) in QRAMPS.values()): continue
            if any(math.hypot(px-sx, py-sy) < 9 for (sx, sy) in spots): continue
            spots.append((px, py))
    return spots

def gameplay():
    Gp = G('DRAGONBALL_GAMEPLAY'); into(Gp); clear_collection(Gp)
    marker('GP_Entry', (0, -188, PAD_Z + 3.5))
    marker('GP_Safe', (0, -176, PAD_Z + 3.5))
    marker('GP_Gacha', (SANCT[0], SANCT[1], 1.85))
    marker('GP_ReturnPad', (13, -192, PAD_Z + .3))
    marker('GP_Boss', (ARENA[0], ARENA[1], 3.3))
    marker('GP_NextArea', (PORTAL[0], PORTAL[1], 1.75))
    pit = _pit_spots()
    fy = mountain_front(MINE_C)
    zones = [('PedreiraEnergetica', (QC[0], QC[1], QFLOOR), (QRX*2 - 16, QRY*2 - 16)),
             ('PatioMina', (MINE_C + 1, 110, 0), (30, 66)),
             ('TunelCapsule', (MINE_C, fy + 18, 0), (18, 30)),
             ('CavernaKi', (-152, 181, 0), (32, 22)),
             ('Cratera', (CRATER[0], CRATER[1], -6), (40, 40))]
    for name, (x, y, z), (w, d) in zones:
        marker('GP_Zone', (x, y, z), zone=name, sizeX=w, sizeZ=d)
    marker('GP_Block', (CRATER[0] - CR_R + 7, CRATER[1], -3), radius=9)
    marker('GP_Block', (CRATER[0] + 17, CRATER[1] + 11, -4), radius=7)
    marker('GP_Block', (MINE_C, fy - 4, 0), radius=8)
    ores = {
        'PedreiraEnergetica': [(x, y, QFLOOR) for (x, y) in pit],
        'PatioMina': [(MINE_C + dx, y, 0) for (dx, y) in ((-12, 84), (8, 92), (-10, 104), (10, 116), (-12, 128), (6, 140), (-4, 152))],
        'TunelCapsule': [(MINE_C - 4, fy + 12, 0), (MINE_C + 4, fy + 22, 0), (MINE_C - 3, fy + 30, 0)],
        'CavernaKi': [(-160, 178, 0), (-146, 184, 0), (-152, 172, 0)],
        'Cratera': [(CRATER[0], CRATER[1], -6), (CRATER[0] + 8, CRATER[1] - 8, -6), (CRATER[0] - 6, CRATER[1] + 9, -6), (CRATER[0] - 12, CRATER[1] - 8, -6)],
    }
    for zone, pts in ores.items():
        for (x, y, z) in pts:
            marker('GP_Ore', (x, y, z + .1), zone=zone)
    return len(pit)

TOPS = ['DRAGONBALL_TERRAIN', 'DRAGONBALL_BUILDINGS', 'DRAGONBALL_LANDMARKS', 'DRAGONBALL_MINING', 'DRAGONBALL_ROCKS',
        'DRAGONBALL_NATURE', 'DRAGONBALL_DECORATION', 'DRAGONBALL_CAPSULE_TECH', 'DRAGONBALL_PROPS', 'DRAGONBALL_GAMEPLAY']

def build(parts=('terrain', 'terreno', 'paths', 'water', 'quarry', 'plateau', 'mountain', 'crater', 'districts', 'landmarks', 'nature', 'sky', 'gameplay')):
    for t in TOPS:
        c = coll(t)
        for ch in list(c.children):
            clear_collection(ch); bpy.data.collections.remove(ch)
        clear_collection(c)
    def terreno():
        import dbterrain
        dbterrain.island_mesh(G('DRAGONBALL_TERRAIN/Terreno'))
    fns = {'terreno': terreno, 'terrain': terrain, 'paths': paths, 'water': water, 'quarry': quarry, 'plateau': plateau, 'mountain': mountain,
           'crater': crater, 'districts': districts, 'landmarks': landmarks_place, 'nature': nature, 'sky': sky, 'gameplay': gameplay}
    for p in parts: fns[p]()
