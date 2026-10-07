# Konoha island layout.  Blender: X east, Y north (progression), Z up; street ground z = 0.
# In Roblox the model is pivoted to area.centro + (0, 6, 0).
import math
from mathutils import Vector
from klib import *
from kit_parts import Body

PI = math.pi
R_ISLAND = 178.0
WALL_C, WALL_RX, WALL_RY = (0.0, -8.0), 165.0, 140.0
RIVER = [(69, 116), (67, 90), (66, 62), (69, 30), (70, 0), (68, -22), (74, -55), (92, -85), (108, -110), (124, -130), (146, -160)]
QUARRY = (-82.0, 52.0, -66.0, 40.0)         # central pit: x0 x1 y0 y1
QFLOOR = -8.0
PLATFORM = (-122.0, -30.0, 54.0, 108.0)
SANCT = (-62.0, -104.0)                      # summoning sanctuary centre
RAMPS = {  # name: (x0, x1, y0, y1, high side)
    'Sul': (-8.0, 8.0, -66.0, -44.0, 'S'), 'Norte': (-8.0, 8.0, 18.0, 40.0, 'N'),
    'Oeste': (-82.0, -60.0, -18.0, -2.0, 'W'), 'Leste': (30.0, 52.0, -28.0, -12.0, 'E')}
MESA = (-28.0, 0.0, -22.0, 2.0)
TERRACES = [(-78.0, -58.0, -62.0, -42.0), (28.0, 48.0, -62.0, -42.0), (-78.0, -58.0, 16.0, 36.0), (28.0, 48.0, 16.0, 36.0)]
PLAT_Z = 6.0
TUNNEL = (90.0, 110.0)
CAVE = (-176.0, -148.0, 62.0, 98.0)

def G(path): return coll(path)

def P(name, x, y, rz=0.0, s=1.0, z=0.0, target=None, label=None):
    return place(name, (x, y, z), rz, s, target or Ctx.target, label)

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    L2 = dx*dx + dy*dy
    t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / L2)) if L2 else 0
    qx, qy = ax + t*dx, ay + t*dy
    return math.hypot(px-qx, py-qy)

def river_dist(x, y):
    return min(seg_dist(x, y, *RIVER[i], *RIVER[i+1]) for i in range(len(RIVER)-1))

def in_island(x, y):
    if abs(x) <= 46 and -198 <= y <= -150: return True
    return (abs(x)/R_ISLAND)**2.6 + (abs(y+2)/R_ISLAND)**2.6 <= 1.0

def mountain_front(x):
    return 118 + (abs(x)/180)**3*10

def wall_point(t):
    return (WALL_C[0] + WALL_RX*math.cos(t), WALL_C[1] + WALL_RY*math.sin(t))

# ------------------------------------------------------------------ TERRAIN
def terrain():
    T = G('KONOHA_TERRAIN'); into(T)
    for c in list(T.children): clear_collection(c); bpy.data.collections.remove(c)
    clear_collection(T)
    ground = G('KONOHA_TERRAIN/Solo'); into(ground)
    step = 4.0
    rows = 0
    y = -198.0
    while y < 190:
        cy = y + step/2
        run = None
        x = -190.0
        def flush(a, b):
            box('Solo', ((a+b)/2, cy, -5), (b-a, step, 10), 'grass', col=True)
        while x < 190:
            cx = x + step/2
            ok = in_island(cx, cy)
            if ok and QUARRY[0] < cx < QUARRY[1] and QUARRY[2] < cy < QUARRY[3]: ok = False
            if ok and river_dist(cx, cy) < 8.0: ok = False
            if ok and cy > mountain_front(cx) + 6: ok = False
            if ok and abs(cx) > 150 and cy > 34: ok = False
            if ok:
                if run is None: run = x
            elif run is not None:
                flush(run, x); run = None
            x += step
        if run is not None: flush(run, x)
        y += step
    # underside strata give the floating island a strong silhouette from other islands
    rs = rng(3)
    under = G('KONOHA_TERRAIN/BaseDaIlha'); into(under)
    for i, (z0, z1, k, m) in enumerate(((-9.5, -22, .95, 'cliff'), (-22, -38, .82, 'cliff_dark'), (-38, -58, .62, 'cliff'), (-58, -84, .38, 'cliff_dark'), (-84, -104, .16, 'stone_dark'))):
        s2 = 16
        yy = -190
        while yy < 190:
            cy = yy + s2/2
            run = None
            xx = -190
            while xx <= 190:
                cx = xx + s2/2
                inside = (abs(cx)/(R_ISLAND*k))**2.6 + (abs(cy+2)/(R_ISLAND*k))**2.6 <= 1.0
                if inside and run is None: run = xx
                if (not inside) and run is not None:
                    box('Estrato', ((run+xx)/2, cy, (z0+z1)/2), (xx-run+rs.uniform(0, 4), s2+.2, z0-z1), m, (0, 0, rs.uniform(-.03, .03)), col=False)
                    run = None
                xx += s2
            yy += s2
    # rim boulders
    rim = G('KONOHA_TERRAIN/BordaRochosa'); into(rim)
    for i in range(44):
        a = i/44*2*PI + rs.uniform(-.04, .04)
        ca, sa = math.cos(a), math.sin(a)
        r = R_ISLAND / ((abs(ca)**2.6 + abs(sa)**2.6)**(1/2.6))
        x, y = ca*r*.985, sa*r*.985 - 2
        if abs(x) < 50 and y < -150: continue
        if y > 110: continue
        P(rs.choice(['Rocha_L', 'Rocha_M', 'Rocha_L']), x, y, rs.uniform(0, 6.28), rs.uniform(.8, 1.5), -3)

# ------------------------------------------------------------------ PATHS
def paths():
    Pt = G('KONOHA_TERRAIN/Caminhos'); into(Pt)
    def rect(name, x0, x1, y0, y1, m='path', z=.12):
        box(name, ((x0+x1)/2, (y0+y1)/2, z/2), (x1-x0, y1-y0, z+.02), m, col=False)
    rect('PracaChegada', -46, 46, -198, -150, 'paving', .2)
    rect('Soleira', -13, 13, -156, -138, 'paving', .22)
    rect('RuaPrincipal', -10, 10, -140, -66, 'path')
    for x in (-10.6, 10.6):
        box('MeioFio', (x, -103, .2), (1.2, 74, .4), 'curb', col=False)
    # ring road around the central quarry
    rect('AnelSul', -90, 60, -74, -66, 'paving', .16)
    rect('AnelNorte', -90, 60, 40, 48, 'paving', .16)
    rect('AnelOeste', -90, -82, -66, 40, 'paving', .16)
    rect('AnelLeste', 52, 60, -66, 40, 'paving', .16)
    rect('RuaOeste', -100, -90, -18, -2)
    rect('RuaNorte', -8, 8, 48, 60)
    rect('BecoSantuario', -32, -10, -110, -98)
    rect('BecoSudeste', 10, 62, -93, -85)
    rect('TrilhaNordeste', 20, 58, 58, 66)
    rect('PatioMina', 76, 140, 40, 116, 'dirt', .14)
    rect('CampoTreino', 86, 142, -58, 30, 'dirt', .14)
    rect('TrilhaPatio', 80, 96, 30, 42, 'path')
    rect('RuaTreino', 80, 104, -27, -13)
    # NW raised residential platform (academy) with retaining wall and stairs on its east face
    x0, x1, y0, y1 = PLATFORM
    box('Plataforma', ((x0+x1)/2, (y0+y1)/2, (PLAT_Z-8)/2), (x1-x0, y1-y0, PLAT_Z+8), 'grass', col=True)
    for (cx, cy, w, d) in (((x0+x1)/2, y0-.6, x1-x0+1.2, 1.2), (x1+.6, (y0+y1)/2, 1.2, y1-y0)):
        box('MuroArrimo', (cx, cy, PLAT_Z/2-.3), (w, d, PLAT_Z+.8), 'stone', col=True)
        box('CapaMuro', (cx, cy, PLAT_Z+.25), (w+.6, d+.6, .5), 'wall_tan', col=False)
    wedge('EscadaPlataforma', (-24, 62, PLAT_Z/2), (12, 12, PLAT_Z), 'stone', (0, 0, PI/2), col=True)
    for i in range(1, 6):
        box('Degrau', (-18 - i*2, 62, i + .05), (.25, 12, .12), 'stone_dark', col=False)
    box('RuaPlataformaTopo', (-76, 87, PLAT_Z+.06), (88, 6, .14), 'path', col=False)

# ------------------------------------------------------------------ RIVER
def river():
    Rv = G('KONOHA_TERRAIN/Rio'); into(Rv)
    for i in range(len(RIVER)-1):
        a, b = Vector((*RIVER[i], 0)), Vector((*RIVER[i+1], 0))
        d = b - a; L = d.length + 2.5
        ang = math.atan2(d.y, d.x) - PI/2
        mid = (a+b)/2
        box('LeitoRio', (mid.x, mid.y, -6), (18, L, 2), 'stone_dark', (0, 0, ang), col=True)
        box('Agua', (mid.x, mid.y, -2.4), (14, L, .5), 'water', (0, 0, ang), col=False)
        n = Vector((math.cos(ang), math.sin(ang), 0))
        for s in (-1, 1):
            q = mid + n*s*8.25
            box('Margem', (q.x, q.y, -2.4), (3.5, L, 5.6), 'stone', (0, 0, ang), col=True)
        for k in range(2):
            t = .25 + .5*k
            p0 = a.lerp(b, t) + n*(k*2-1)*3
            box('CorrenteFolha', (p0.x, p0.y, -2.1), (.25, 3, .06), 'water_foam', (0, 0, ang), col=False,
                fa='%.1f,%.1f,-2.1' % (p0.x - d.x*.12, p0.y - d.y*.12), fb='%.1f,%.1f,-2.1' % (p0.x + d.x*.12, p0.y + d.y*.12))
    # barrier where the river leaves the wall
    box('BarreiraRio', (110, -113, 4), (22, 2, 18), 'invisible', (0, 0, -.8), col=True)
    # waterfall from the monument and waterfall off the island edge
    wx, wy = RIVER[0]
    for i in range(4):
        box('Cachoeira', (wx - 4.5 + i*3, wy + 1, 30), (3.1, 1.2, 66), 'water', col=False, fx='waterfall' if i == 1 else '')
    box('PocoCachoeira', (wx, wy - 4, -2.3), (16, 10, .5), 'water_foam', col=False, fx='mist')
    ex, ey = RIVER[-2]
    for i in range(4):
        box('CachoeiraBorda', (ex + 10 + i*2.6, ey - 18 - i*1.2, -40), (3, 1.2, 76), 'water', (0, 0, -.7), col=False)

# ------------------------------------------------------------------ QUARRY PIT
def _wall_run(name, axis, fixed, a0, a1, gaps, thick, inward, m='cliff'):
    """Pit wall along X (axis='X', fixed=y) or Y (fixed=x) from a0 to a1, skipping gap intervals."""
    cuts = sorted(gaps)
    segs, cur = [], a0
    for g0, g1 in cuts:
        if g0 > cur: segs.append((cur, g0))
        cur = max(cur, g1)
    if cur < a1: segs.append((cur, a1))
    h = -QFLOOR
    for s0, s1 in segs:
        mid, L = (s0+s1)/2, s1-s0
        c = fixed + inward*thick/2
        if axis == 'X':
            box(name, (mid, c, QFLOOR/2), (L, thick, h), m, col=True)
            for zz, mm in ((-2.6, 'cliff_dark'), (-5.6, 'cliff_light')):
                box('Estrato', (mid, fixed + inward*(thick+.25), zz), (L, .6, 1.0), mm, col=False)
        else:
            box(name, (c, mid, QFLOOR/2), (thick, L, h), m, col=True)
            for zz, mm in ((-2.6, 'cliff_dark'), (-5.6, 'cliff_light')):
                box('Estrato', (fixed + inward*(thick+.25), mid, zz), (.6, L, 1.0), mm, col=False)

def quarry():
    """Central ninja quarry: the main, extensive mining field in the heart of the village."""
    Q = G('KONOHA_MINING/Pedreira_Central'); into(Q)
    x0, x1, y0, y1 = QUARRY
    rs = rng(9)
    box('PisoPedreira', ((x0+x1)/2, (y0+y1)/2, QFLOOR-4), (x1-x0, y1-y0, 8), 'dirt', col=True)
    T = 4.0
    r = RAMPS
    _wall_run('ParedeSul', 'X', y0, x0, x1, [(r['Sul'][0], r['Sul'][1])], T, 1)
    _wall_run('ParedeNorte', 'X', y1, x0, x1, [(r['Norte'][0], r['Norte'][1])], T, -1)
    _wall_run('ParedeOeste', 'Y', x0, y0, y1, [(r['Oeste'][2], r['Oeste'][3])], T, 1)
    _wall_run('ParedeLeste', 'Y', x1, y0, y1, [(r['Leste'][2], r['Leste'][3])], T, -1)
    # ramps (walkable wedges, rise from the pit floor to street level)
    rot = {'S': PI, 'N': 0.0, 'W': PI/2, 'E': -PI/2}
    for name, (a0, a1, b0, b1, hs) in r.items():
        cx, cy = (a0+a1)/2, (b0+b1)/2
        if hs in 'NS':
            width, run = a1-a0, b1-b0
        else:
            width, run = b1-b0, a1-a0
        wedge('Rampa' + name, (cx, cy, QFLOOR/2), (width, run, -QFLOOR), 'dirt_dark', (0, 0, rot[hs]), col=True)
        for s in (-1, 1):
            if hs in 'NS':
                hi, lo = (b0, b1) if hs == 'S' else (b1, b0)
                gx = cx + s*(width/2+.3)
                rod('GuardaRampa', (gx, hi, 1.4), (gx, lo, QFLOOR + 1.4), .5, 'wood', col=True, h=2.2)
            else:
                hi, lo = (a0, a1) if hs == 'W' else (a1, a0)
                gy = cy + s*(width/2+.3)
                rod('GuardaRampa', (hi, gy, 1.4), (lo, gy, QFLOOR + 1.4), .5, 'wood', col=True, h=2.2)
    # rim: rope fence with posts, gaps at the ramps
    def rim(axis, fixed, a0, a1, gaps):
        cur = a0
        pieces = []
        for g0, g1 in sorted(gaps):
            if g0 > cur: pieces.append((cur, g0))
            cur = max(cur, g1)
        if cur < a1: pieces.append((cur, a1))
        for s0, s1 in pieces:
            n = max(1, int((s1-s0)//10))
            for k in range(n+1):
                v = s0 + (s1-s0)*k/n
                pos = (v, fixed) if axis == 'X' else (fixed, v)
                box('PosteBorda', (pos[0], pos[1], 1.6), (.6, .6, 3.2), 'wood_dark', col=False)
            if axis == 'X':
                box('CordaBorda', ((s0+s1)/2, fixed, 2.6), (s1-s0, .25, .25), 'rope', col=False)
                box('BordaColisao', ((s0+s1)/2, fixed, 1.6), (s1-s0, .5, 3.2), 'invisible', col=True)
            else:
                box('CordaBorda', (fixed, (s0+s1)/2, 2.6), (.25, s1-s0, .25), 'rope', col=False)
                box('BordaColisao', (fixed, (s0+s1)/2, 1.6), (.5, s1-s0, 3.2), 'invisible', col=True)
    rim('X', y0 - .6, x0 - .6, x1 + .6, [(r['Sul'][0] - .8, r['Sul'][1] + .8)])
    rim('X', y1 + .6, x0 - .6, x1 + .6, [(r['Norte'][0] - .8, r['Norte'][1] + .8)])
    rim('Y', x0 - .6, y0, y1, [(r['Oeste'][2] - .8, r['Oeste'][3] + .8)])
    rim('Y', x1 + .6, y0, y1, [(r['Leste'][2] - .8, r['Leste'][3] + .8)])
    for (x, y, rz, txt) in ((-14, -70, 0, 'PEDREIRA CENTRAL'), (14, 44, PI, 'PEDREIRA CENTRAL')):
        box('PlacaPedreira', (x, y, 5.4), (12, .5, 2.6), 'wood', (0, 0, rz), col=False, text=txt)
        for dx in (-5, 5):
            box('PostePlaca', (x + dx*math.cos(rz), y, 2.5), (.5, .5, 5), 'wood_dark', col=False)

# ------------------------------------------------------------------ MOUNTAIN + FACES + MINE + CAVE
def mountain():
    M = G('KONOHA_LANDMARKS/Monte_Hokage'); into(M)
    rs = rng(5)
    for x in range(-180, 181, 20):
        front = mountain_front(x) + rs.uniform(-1.5, 1.5)
        h = 96 - (abs(x)/180)**2*30 + rs.uniform(-5, 5)
        back = 196
        cx = x
        if TUNNEL[0] <= x <= TUNNEL[1]:
            box('Macico', (cx, (front+back)/2, (18+h)/2), (20.5, back-front, h-18), 'cliff', col=True)
            box('MacicoFundo', (cx, (150+back)/2, 9), (20.5, back-150, 18), 'cliff', col=True)
        else:
            box('Macico', (cx, (front+back)/2, (h-8)/2), (20.5, back-front, h+8), 'cliff', col=True)
        box('CapaGrama', (cx, (front+back)/2 + 1, h+.7), (21, back-front-2, 1.4), 'grass', col=False)
        for zz, m in ((14, 'cliff_dark'), (33, 'cliff_light'), (86, 'cliff_dark')):
            if zz < h - 3 and not (TUNNEL[0]-2 <= x <= TUNNEL[1]+2 and zz < 20):
                box('Estrato', (cx, front - .8, zz), (20.6, 2, 2.2 if m == 'cliff_dark' else 1.4), m, col=False)
        # facets on the face of the cliff (skip portraits, waterfall and tunnel)
        for k in range(3):
            fz = rs.uniform(6, h - 8)
            fx = cx + rs.uniform(-7, 7)
            if -64 < fx < 64 and 38 < fz < 82: continue
            if 60 < fx < 124 and fz < 36: continue
            box('Faceta', (fx, front - 1.5, fz), (rs.uniform(5, 9), 4, rs.uniform(7, 14)), rs.choice(['cliff_light', 'cliff_dark', 'cliff']),
                (0, rs.uniform(-.15, .15), rs.uniform(-.2, .2)), col=False)
        if x % 40 == 0 and not (TUNNEL[0] <= x <= TUNNEL[1]):
            P('Cedro' if abs(x) > 60 else 'Arvore_Folha_M', cx + rs.uniform(-5, 5), front + 14, rs.uniform(0, 6), rs.uniform(1.1, 1.5), h + 1)
        if x % 40 == 20:
            P('Arvore_Folha_G', cx + rs.uniform(-5, 5), front + 30, rs.uniform(0, 6), rs.uniform(1.0, 1.3), h + 1)
    # carved portrait niche + faces
    box('Nicho', (0, 119.5, 60), (140, 4, 42), 'cliff_dark', col=False)
    for i, x in enumerate((-48, -16, 16, 48)):
        P('Rosto_Hokage_%d' % (i+1), x, 122, 0, 1.12, 44)
    # zig-zag stair to the lookout
    St = G('KONOHA_LANDMARKS/Escadaria_Mirante'); into(St)
    wedge('Lance1', (-51, 104, PLAT_Z + 5.5), (5, 22, 11), 'stone', (0, 0, PI/2), col=True)
    box('Patamar1', (-65, 107, PLAT_Z + 10.75), (6, 12, .5), 'stone', col=True)
    wedge('Lance2', (-79, 110, PLAT_Z + 16.5), (5, 22, 11), 'stone', (0, 0, PI/2), col=True)
    box('Mirante', (-98, 110, PLAT_Z + 21.75), (16, 14, .5), 'wood_light', col=True)
    box('BaseMirante', (-98, 110, (PLAT_Z + 21.5)/2), (14, 12, PLAT_Z + 21.5), 'cliff_dark', col=True)
    for (a, b) in (((-40, 101.3), (-62, 101.3)), ((-68, 107.3), (-90, 107.3)), ((-106, 103), (-90, 103))):
        pass
    rod('Corrimao', (-40, 101.4, PLAT_Z + 3), (-62, 101.4, PLAT_Z + 14), .3, 'wood_dark')
    rod('Corrimao', (-68, 107.4, PLAT_Z + 14), (-90, 107.4, PLAT_Z + 25), .3, 'wood_dark')
    box('GuardaMirante', (-98, 103, PLAT_Z + 23.5), (16, .4, 3), 'wood', col=True)
    box('GuardaMirante', (-106, 110, PLAT_Z + 23.5), (.4, 14, 3), 'wood', col=True)
    P('Estandarte_Folha', -104, 114, 0, 1, PLAT_Z + 22)
    P('Banco', -94, 115, PI, 1, PLAT_Z + 22)
    box('Luneta', (-99, 104.5, PLAT_Z + 25), (.8, 3.4, .8), 'metal', (-.3, 0, .5), col=False)
    box('TripeLuneta', (-99, 105, PLAT_Z + 23.2), (.3, .3, 3), 'wood_dark', col=False)
    # side ridges
    R = G('KONOHA_LANDMARKS/Cordilheiras'); into(R)
    for side in (-1, 1):
        for y in (110, 90, 70, 50, 30):
            h = {110: 74, 90: 60, 70: 50, 50: 42, 30: 34}[y] + rs.uniform(-4, 4)
            inner = side*(150 + rs.uniform(-2, 2))
            outer = side*196
            cx = (inner+outer)/2; w = abs(outer-inner)
            if side < 0 and y in (70, 90):
                box('Cordilheira', (cx, y, (18+h)/2), (w, 20.5, h-18), 'cliff', col=True)
                box('CordilheiraFundo', ((-196-176)/2, y, 1), (20, 20.5, 34), 'cliff', col=True)
            else:
                box('Cordilheira', (cx, y, (h-8)/2), (w, 20.5, h+8), 'cliff', col=True)
            box('CapaGrama', (cx, y, h+.7), (w, 21, 1.4), 'grass', col=False)
            box('Estrato', (inner - side*.8, y, h*.4), (2, 20.8, 2), 'cliff_dark', col=False)
            if y in (110, 70, 30):
                P('Cedro', cx + side*6, y, rs.uniform(0, 6), 1.3, h + 1)
    # secret cave
    Cv = G('KONOHA_MINING/Caverna_Secreta'); into(Cv)
    x0, x1, y0, y1 = CAVE
    box('PisoCaverna', ((x0+x1)/2, (y0+y1)/2, -4), (x1-x0+4, y1-y0+8, 8), 'mine_floor', col=True)
    box('TetoCaverna', ((x0+x1)/2, (y0+y1)/2, 19), (x1-x0+4, y1-y0+8, 2), 'cliff_dark', col=True)
    box('ParedeSul', ((x0+x1)/2, y0-2, 9), (x1-x0+4, 4, 18), 'cliff_dark', col=True)
    box('ParedeNorte', ((x0+x1)/2, y1+2, 9), (x1-x0+4, 4, 18), 'cliff_dark', col=True)
    box('FrenteA', (x1+1, (y0+76)/2 - 1, 9), (6, 76-y0+2, 18), 'cliff', col=True)
    box('FrenteB', (x1+1, (86+y1)/2 + 1, 9), (6, y1-86+2, 18), 'cliff', col=True)
    box('Escuridao', (x0-1, (y0+y1)/2, 9), (1, y1-y0, 18), 'dark_void', col=False)
    P('Cristal_Raro_G', -170, 92, .5, 1, 0)
    P('Cristal_Raro', -172, 68, 2.1, 1.1, 0)
    P('Cristal_Raio', -158, 95, 4.0, 1, 0)
    P('Cristal_Chakra', -150, 64, 1.0, .9, 0)
    box('LuzCaverna', (-162, 80, 17.5), (1, 1, 1), 'cr_rare', col=False, light='200,120,255,40,1.4')
    P('Torii_Santuario', -134, 81, PI/2, 1, 0)
    P('Lanterna_Pedra', -137, 72, 0, 1, 0)
    P('Lanterna_Pedra', -137, 90, 0, 1, 0)
    for (x, y, s) in ((-138, 62, 1.1), (-132, 100, 1.2), (-142, 56, .9)):
        P('Arvore_Folha_G', x, y, rs.uniform(0, 6), s, 0)
    P('Arbusto', -142, 76, 0, 1.4, 0)
    P('Arbusto', -142, 88, 1, 1.2, 0)
    # the great mine
    Mn = G('KONOHA_MINING/Mina_Monumento'); into(Mn)
    fx = (TUNNEL[0]+TUNNEL[1])/2
    front = mountain_front(fx)
    P('Grande_Mina', fx, front - 1, 0, 1, 0)
    box('PisoTunel', (fx, (front+150)/2, -4), (TUNNEL[1]-TUNNEL[0]+1, 150-front+2, 8), 'mine_floor', col=True)
    box('TetoTunelLuz', (fx, 140, 17), (1, 1, 1), 'cr_chakra', col=False, light='90,220,255,36,1.3')
    for (x, y, el, rz) in ((93, 146, 'Cristal_Chakra', 0), (107, 130, 'Cristal_Agua', 2), (93, 128, 'Cristal_Raio', 4)):
        P(el, x, y, rz, 1, 0)
    for y in range(int(front) + 4, 150, 8):
        P('Trilho', fx, y, 0, 1, 0)
    P('Cristal_Chakra_G', fx - 28, front - 6, .3, 1.2, 0)
    for (cx, cy, cz, s, tilt) in ((128, 119, 26, 2.2, -.35), (140, 121, 44, 1.6, -.5), (76, 119, 34, 1.5, .4)):
        e = P('Cristal_Chakra_G', cx, cy, 0, s, cz)
        e.rotation_euler = (math.radians(55), tilt, 0)
    P('Cristal_Chakra_G', fx + 27, front - 8, 2.5, 1.1, 0)
    for s in (-1, 1):
        P('Lanterna_Mina', fx + s*14, front - 8, 0, 1.1, 0)

# ------------------------------------------------------------------ WALL
def wall():
    W = G('KONOHA_BUILDINGS/Muralha'); into(W)
    ts = []
    t = -PI/2 + .17
    while t < math.radians(20):
        ts.append(t); t += .088
    for side in (-1, 1):
        for i, t in enumerate(ts):
            x, y = wall_point(t)
            x *= side
            dx, dy = -WALL_RX*math.sin(t)*side, WALL_RY*math.cos(t)
            nx, ny = -dy, dx
            if side < 0: nx, ny = dy, -dx
            rz = math.atan2(-nx, ny)
            if side > 0 and river_dist(x, y) < 14:
                P('Muralha_Modulo', x, y, rz, 1, 5, label='Muralha_Comporta')
                continue
            P('Muralha_Modulo', x, y, rz, 1, 0)
            if i in (4, 12):
                P('Torre_Vigia', x - nx*.0, y, rz, 1, 0)
    P('Portao_Principal', 0, -146, 0, 1, 0)

# ------------------------------------------------------------------ DISTRICTS
FACE_E, FACE_W, FACE_S, FACE_N = PI/2, -PI/2, 0.0, PI

def districts():
    B = G('KONOHA_BUILDINGS/Vila_Casas'); into(B)
    # commercial street between the gate and the central quarry
    P('Loja_Ramen', -19, -78, FACE_E)
    P('Casa_P_DuasAguas', -19, -91.5, FACE_E)
    P('Loja_Flores', -19, -128, FACE_E)
    P('Loja_Dango', 19, -78, FACE_W)
    P('Loja_Armas', 20, -100, FACE_W)
    P('Casa_G_TresAndares', 22, -122, FACE_W)
    # south-east lane
    P('Casa_M_Escalonada', 46, -108, FACE_N)
    P('Casa_P_DuasAguas', 46, -128, FACE_N)
    # west ring of houses facing the quarry
    P('Casa_M_Escalonada', -102, -50, FACE_E)
    P('Torre_Cilindrica', -100, -28, FACE_E)
    P('Casa_G_TresAndares', -104, 12, FACE_E)
    P('Casa_M_VarandaEscada', -104, 36, FACE_E)
    P('Casa_P_LajeCaixa', -134, -40, FACE_E)
    P('Casa_P_LajeCaixa', -134, -8, FACE_E)
    P('Casa_P_DuasAguas', -132, 18, FACE_E)
    # north: residence, academy platform, north-east district
    P('Residencia_Hokage', 0, 84, 0)
    P('Academia', -76, 68, 0, 1, PLAT_Z)
    P('Casa_M_VarandaEscada', -108, 98, 0, 1, PLAT_Z)
    P('Casa_P_LajeCaixa', -44, 94, 0, 1, PLAT_Z)
    P('Casa_P_DuasAguas', -112, 68, FACE_E, 1, PLAT_Z)
    P('Torre_Cilindrica', 40, 78, FACE_W)
    P('Casa_M_Escalonada', 40, 100, FACE_W)
    P('Casa_M_Escalonada', 150, 2, FACE_W)
    # arrival plaza
    A = G('KONOHA_BUILDINGS/Chegada'); into(A)
    for x in (-40, 40):
        P('Estandarte_Folha', x, -154, 0)
    P('Painel_Folha', 0, -197, PI)
    for x in (-38, 38):
        P('Cristal_Chakra_G', x, -190, .6 if x < 0 else 2.2, .9)
        P('Arvore_Folha_M', x*1.12, -176, 1, 1)
    for x in (-20, 20):
        P('Lanterna_Pedra', x, -160, 0)
    P('Banca_Mercado', -32, -164, FACE_E)
    P('Banca_Mercado', 32, -164, FACE_W)
    P('Banco', -14, -190, 0)
    P('Banco', 14, -190, 0)
    P('Guarita_Portao', 26, -140, FACE_W)

def landmarks_place():
    L = G('KONOHA_LANDMARKS/Pontos'); into(L)
    P('Santuario_Invocacao', SANCT[0], SANCT[1], PI/2)
    P('Arena_Chefe', 104, 80, 0)
    P('Portal_Progressao', 134, 50, -PI/4)
    P('Ponte_Vermelha', 68, -20, PI/2)
    P('Ponte_Madeira', 66, 62, PI/2)

def dressing():
    D = G('KONOHA_DECORATION/Ruas'); into(D)
    rs = rng(77)
    for y in (-84, -116):
        P('Fio_Lanternas', 0, y, 0)
    poles = [(-12.5, y) for y in (-138, -115, -92, -70)] + [(12.5, y) for y in (-138, -115, -92, -70)]
    for (x, y) in poles:
        P('Poste_Fios', x, y, 0)
    for side in (-12.5, 12.5):
        ys = [p[1] for p in poles if p[0] == side]
        for a, b in zip(ys, ys[1:]):
            rod('Fio', (side, a, 17), (side, b, 17), .1, 'trim_dark')
    for (x, y) in ((-12, 58), (12, 58), (58, -94), (-34, -96), (-34, -112), (-88, 44), (58, 44), (-88, -72), (58, -72)):
        P('Lanterna_Pedra', x, y, 0, .9)
    for (x, y, rz) in ((-13, -95, 0), (12, -110, 0), (-12, -114, 0), (58, -84, 1), (-94, -60, 2), (62, 20, 0)):
        P(rs.choice(['Barril', 'Caixote']), x, y, rz)
    for (x, y) in ((-36, -93), (-36, -115)):
        P('Vaso_Planta', x, y, 0)
    for x in (-40, 30):
        P('Estandarte_Folha', x, -76, 0)
        P('Estandarte_Folha', x, 52, PI)
    # training ground
    Tg = G('KONOHA_DECORATION/Campo_Treino'); into(Tg)
    for (x, y) in ((96, 22), (104, 22), (112, 22), (132, -52), (138, -44)):
        P('Poste_Treino', x, y, rs.uniform(0, 6))
    for (x, y, r) in ((92, -54, 0), (124, 24, PI), (140, -20, PI/2)):
        P('Alvo_Treino', x, y, r)
    for (x, y, s) in ((120, -40, 1), (94, -38, .8), (130, 4, .9)):
        P('Rochedo_Veio', x, y, rs.uniform(0, 6), s)
    for (x, y, s) in ((88, 8, 1), (140, -30, 1.2), (110, -52, .9), (100, 0, .7)):
        P('Rocha_M', x, y, rs.uniform(0, 6), s)
    P('Cristal_Raio', 126, 28, 0, 1.2)
    P('Cristal_Vento', 86, -48, 1, 1.2)
    for i in range(6):
        P('Cerca', 90 + i*8.2, -60, 0)
    for (x, y) in ((140, 28), (86, 28)):
        P('Rocha_Musgo', x, y, 1, .8)
    P('Banco', 100, -10, 0)
    P('Estandarte_Folha', 118, 30, PI)
    P('Estandarte_Folha', 106, 30, PI)
    box('PlacaTreino', (84, -20, 5), (8, .5, 2.4), 'wood', (0, 0, PI/2), col=False, text='CAMPO DE TREINO')
    # mine yard
    My = G('KONOHA_DECORATION/Patio_Mina'); into(My)
    P('Vagoneta', 92, 96, .2, 1, .6)
    P('Pilha_Minerio', 128, 100, 0, 1.4)
    P('Pilha_Minerio', 80, 88, 1, 1.1)
    P('Cristal_Agua', 78, 104, 0, 1.1)
    P('Cristal_Fogo', 136, 76, 0, 1.1)
    for (x, y) in ((80, 46), (124, 44), (138, 100)):
        P('Lanterna_Mina', x, y, rs.uniform(0, 6))
    for (x, y) in ((84, 70), (126, 64)):
        P('Caixote', x, y, rs.uniform(0, 6))
        P('Barril', x + 3, y + 2)
    # vegetation inside the village
    V = G('KONOHA_NATURE/Vila_Arvores'); into(V)
    for (x, y, n, s) in ((-116, 44, 'Arvore_Folha_G', 1.1), (-40, -136, 'Arvore_Folha_M', 1), (64, -120, 'Arvore_Folha_M', 1.1),
                         (-146, -24, 'Arvore_Folha_G', 1), (-146, 30, 'Arvore_Folha_M', 1), (-136, -64, 'Arvore_Folha_M', 1.1),
                         (132, -78, 'Arvore_Folha_G', 1), (152, 24, 'Arvore_Folha_M', 1), (78, 64, 'Arvore_Folha_G', 1),
                         (140, 110, 'Arvore_Folha_G', 1.1), (58, 104, 'Arvore_Folha_M', 1), (100, -84, 'Arvore_Folha_M', 1.1),
                         (138, -74, 'Arvore_Folha_G', 1), (-94, -72, 'Arvore_Folha_G', 1), (62, -50, 'Arvore_Folha_M', .9),
                         (-24, 52, 'Arvore_Folha_M', .9), (24, 52, 'Arvore_Folha_M', .9), (-100, -96, 'Arvore_Folha_G', 1),
                         (-30, -150, 'Arvore_Folha_M', .8)):
        P(n, x, y, rs.uniform(0, 6), s)
    for (x, y) in ((64, -58), (80, 32), (-128, -84), (120, -96), (-92, -84), (66, 30), (-118, -20), (34, 52)):
        P('Arbusto', x, y, rs.uniform(0, 6), rs.uniform(.8, 1.2))
    # forest outside the wall
    F = G('KONOHA_NATURE/Floresta'); into(F)
    k = 0
    for i in range(60):
        a = -PI/2 + (i/60 - .5)*PI*1.28
        ca, sa = math.cos(a), math.sin(a)
        r = R_ISLAND / ((abs(ca)**2.6 + abs(sa)**2.6)**(1/2.6))
        f = rs.uniform(.84, .93)
        x, y = ca*r*f, sa*r*f - 2
        if abs(x) < 52 and y < -140: continue
        if river_dist(x, y) < 14: continue
        if (x/WALL_RX)**2 + ((y-WALL_C[1])/WALL_RY)**2 < 1.12: continue
        k += 1
        name = 'Arvore_Gigante' if k % 7 == 0 else ('Arvore_Folha_G' if k % 2 else 'Arvore_Folha_M')
        P(name, x, y, rs.uniform(0, 6), rs.uniform(.9, 1.25) if name != 'Arvore_Gigante' else .8)
        if k % 3 == 0:
            P('Arbusto', x + rs.uniform(-6, 6), y + rs.uniform(-6, 6), 0, 1.3)

# ------------------------------------------------------------------ GAMEPLAY MARKERS
def _pit_spots():
    rs = rng(123)
    x0, x1, y0, y1 = QUARRY
    blocked = []
    for (a0, a1, b0, b1, hs) in RAMPS.values():
        blocked.append((a0-5, a1+5, b0-5, b1+5))
    deco = []
    spots = []
    for y in range(int(y0) + 9, int(y1) - 6, 11):
        for x in range(int(x0) + 9, int(x1) - 6, 11):
            px, py = x + rs.uniform(-2, 2), y + rs.uniform(-2, 2)
            if any(a0 <= px <= a1 and b0 <= py <= b1 for (a0, a1, b0, b1) in blocked): continue
            if any(math.hypot(px-dx, py-dy) < 6 for (dx, dy) in deco): continue
            if any(math.hypot(px-sx, py-sy) < 9 for (sx, sy) in spots): continue
            spots.append((px, py))
    return spots, deco

def gameplay():
    Gp = G('KONOHA_GAMEPLAY'); into(Gp); clear_collection(Gp)
    marker('GP_Entry', (0, -184, 3.5))
    marker('GP_Safe', (0, -172, 3.5))
    marker('GP_Gacha', (SANCT[0], SANCT[1], 1.25))
    marker('GP_ReturnPad', (22, -178, .2))
    marker('GP_Boss', (104, 80, .32))
    marker('GP_NextArea', (130, 46, .3))
    pit, deco = _pit_spots()
    zones = [('PedreiraCentral', (-15, -13, QFLOOR), (126, 98)), ('CampoTreino', (112, -16, 0), (52, 80)),
             ('PatioMina', (106, 78, 0), (60, 68)), ('TunelMina', (100, 134, 0), (18, 26)), ('CavernaSecreta', (-162, 80, 0), (24, 32))]
    for name, (x, y, z), (w, d) in zones:
        marker('GP_Zone', (x, y, z), zone=name, sizeX=w, sizeZ=d)
    for (x, y) in deco:
        marker('GP_Block', (x, y, QFLOOR), radius=6)
    ores = {
        'PedreiraCentral': pit,
        'CampoTreino': [(96, -46), (112, -40), (126, -10), (96, -8), (114, 8)],
        'PatioMina': [(86, 56), (100, 50), (120, 56), (132, 84), (84, 100), (120, 104), (132, 66)],
        'TunelMina': [(96, 132), (104, 140), (98, 146)],
        'CavernaSecreta': [(-164, 72), (-158, 88), (-168, 82)],
    }
    zz = {'PedreiraCentral': QFLOOR}
    for zone, pts in ores.items():
        for (x, y) in pts:
            marker('GP_Ore', (x, y, zz.get(zone, 0) + .1), zone=zone)
    return len(pit)

def build(parts=('terrain', 'paths', 'river', 'quarry', 'mountain', 'wall', 'districts', 'landmarks', 'dressing', 'gameplay')):
    for top in ('KONOHA_BUILDINGS/Muralha', 'KONOHA_BUILDINGS/Vila_Casas', 'KONOHA_BUILDINGS/Chegada', 'KONOHA_LANDMARKS/Monte_Hokage',
                'KONOHA_LANDMARKS/Escadaria_Mirante', 'KONOHA_LANDMARKS/Cordilheiras', 'KONOHA_LANDMARKS/Pontos',
                'KONOHA_MINING/Pedreira_Central', 'KONOHA_MINING/Caverna_Secreta', 'KONOHA_MINING/Mina_Monumento',
                'KONOHA_DECORATION/Ruas', 'KONOHA_DECORATION/Campo_Treino', 'KONOHA_DECORATION/Patio_Mina',
                'KONOHA_NATURE/Vila_Arvores', 'KONOHA_NATURE/Floresta', 'KONOHA_TERRAIN/Caminhos', 'KONOHA_TERRAIN/Rio'):
        c = coll(top); clear_collection(c)
    old = bpy.data.collections.get('Pedreira_Ninja')
    if old: clear_collection(old); bpy.data.collections.remove(old)
    fns = {'terrain': terrain, 'paths': paths, 'river': river, 'quarry': quarry, 'mountain': mountain, 'wall': wall,
           'districts': districts, 'landmarks': landmarks_place, 'dressing': dressing, 'gameplay': gameplay}
    for p in parts: fns[p]()
