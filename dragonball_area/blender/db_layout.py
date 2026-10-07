# Vale Capsule (Dragon Ball) island layout.  Blender: X east, Y north (progression), Z up; ground z = 0.
# In Roblox the model is pivoted to area.centro + (0, 6, 0).
import math
from mathutils import Vector
from dblib import *

# ---------------------------------------------------------------- key coordinates
OUTLINE_RAW = [(-40, -204), (40, -204), (60, -176), (112, -166), (150, -138), (170, -96), (160, -56), (186, -34), (196, 12),
               (188, 52), (162, 68), (178, 112), (162, 158), (112, 192), (40, 200), (-40, 200), (-112, 192), (-166, 162),
               (-192, 110), (-178, 64), (-196, 22), (-194, -30), (-166, -66), (-178, -112), (-152, -150), (-100, -168), (-56, -176)]
QC, QRX, QRY, QN = (6.0, -24.0), 70.0, 68.0, 4.0        # central quarry (superellipse)
QFLOOR = -10.0
QRAMPS = {  # name: (x0, x1, y0, y1, high side)  (inside the pit; high end meets the rim)
    'Sul': (-2.0, 14.0, -92.0, -66.0, 'S'), 'Norte': (-2.0, 14.0, 18.0, 44.0, 'N'),
    'Oeste': (-64.0, -38.0, -32.0, -16.0, 'W'), 'Leste': (50.0, 76.0, -32.0, -16.0, 'E')}
PLATEAU = (12.0, 136.0, 78.0, 162.0)
PLAT_Z = 10.0
LAKE = (-80.0, 110.0, 38.0, 34.0)                      # cx cy rx ry
STREAM = [(-114, 106), (-138, 98), (-160, 92), (-184, 86), (-206, 82)]
CRATER = (156.0, 12.0)
CR_R = 30.0
SANCT = (-60.0, -132.0)
ARENA = (84.0, -138.0)
PORTAL = (156.0, 116.0)
MINE_X = (-26.0, -2.0)                                  # mine tunnel width (x0, x1)
CAVE = (-172.0, -132.0, 166.0, 196.0)                   # x0 x1 y0 y1
PAD = (0.0, -180.0, 20.0)
PAD_Z = 8.0
COMPLEX = (80.0, 116.0)
MINE_C = -14.0

def G(path): return coll(path)

def P(name, x, y, rz=0.0, s=1.0, z=0.0, target=None, label=None):
    return place(name, (x, y, z), rz, s, target or Ctx.target, label)

def chaikin(pts, it=2):
    for _ in range(it):
        out = []
        n = len(pts)
        for i in range(n):
            a, b = Vector(pts[i]), Vector(pts[(i+1) % n])
            out += [tuple(a.lerp(b, .25)), tuple(a.lerp(b, .75))]
        pts = out
    return pts

OUTLINE = chaikin(OUTLINE_RAW, 3)

def in_poly(x, y, poly=None):
    poly = poly or OUTLINE
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi)*(y - yi)/(yj - yi) + xi:
            inside = not inside
        j = i
    return inside

def scaled_poly(k, cx=0.0, cy=0.0):
    return [(cx + (x-cx)*k, cy + (y-cy)*k) for (x, y) in OUTLINE]

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    L2 = dx*dx + dy*dy
    t = max(0, min(1, ((px-ax)*dx + (py-ay)*dy) / L2)) if L2 else 0
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))

def stream_dist(x, y):
    return min(seg_dist(x, y, *STREAM[i], *STREAM[i+1]) for i in range(len(STREAM)-1))

def quarry_f(x, y, grow=0.0):
    return (abs(x-QC[0])/(QRX+grow))**QN + (abs(y-QC[1])/(QRY+grow))**QN

def quarry_point(t, grow=0.0):
    c, s = math.cos(t), math.sin(t)
    r = 1.0 / ((abs(c)/(QRX+grow))**QN + (abs(s)/(QRY+grow))**QN)**(1/QN)
    return QC[0] + c*r, QC[1] + s*r

def lake_f(x, y, grow=0.0):
    cx, cy, rx, ry = LAKE
    return ((x-cx)/(rx+grow))**2 + ((y-cy)/(ry+grow))**2

def mountain_front(x):
    """y where the northern massif starts."""
    return 164 + 5*math.sin(x*.045) + (abs(x)/190)**3*14

# ---------------------------------------------------------------- TERRAIN
def terrain():
    T = G('DRAGONBALL_TERRAIN'); into(T)
    ground = G('DRAGONBALL_TERRAIN/Solo'); into(ground)
    step = 4.0
    y = -208.0
    while y < 204:
        cy = y + step/2
        run = None
        x = -204.0
        def flush(a, b):
            box('Solo', ((a+b)/2, cy, -5), (b-a, step, 10), 'invisible', col=True)
        while x < 204:
            cx = x + step/2
            ok = in_poly(cx, cy)
            if ok and quarry_f(cx, cy, 1.0) <= 1: ok = False
            if ok and lake_f(cx, cy, 1.0) <= 1: ok = False
            if ok and math.hypot(cx-CRATER[0], cy-CRATER[1]) < CR_R - 1: ok = False
            if ok:
                if run is None: run = x
            elif run is not None:
                flush(run, x); run = None
            x += step
        if run is not None: flush(run, x)
        y += step
    # meadow tint patches (break the flat green; slightly raised to avoid z-fighting)
    rs = rng(21)
    Pt = G('DRAGONBALL_TERRAIN/Manchas'); into(Pt)
    for i in range(34):
        x, y = rs.uniform(-180, 180), rs.uniform(-190, 150)
        if not in_poly(x, y) or quarry_f(x, y, 16) <= 1 or lake_f(x, y, 10) <= 1: continue
        if math.hypot(x-CRATER[0], y-CRATER[1]) < CR_R + 12: continue
        if PLATEAU[0]-4 < x < PLATEAU[1]+4 and PLATEAU[2]-4 < y < PLATEAU[3]+4: continue
        w, d = rs.uniform(14, 34), rs.uniform(10, 26)
        box('ManchaGrama', (x, y, .04), (w, d, .1), rs.choice(['db_grass_light', 'db_grass_dark']), (0, 0, rs.uniform(0, PI)), col=False)
    # underside strata: the floating island silhouette seen from the other islands
    under = G('DRAGONBALL_TERRAIN/BaseDaIlha'); into(under)
    layers = ((-10.5, -24, .97, 'db_rock'), (-24, -40, .86, 'db_rock_dark'), (-40, -60, .68, 'db_rock'),
              (-60, -84, .46, 'db_rock_red'), (-84, -108, .24, 'db_rock_deep'), (-108, -126, .1, 'db_rock_dark'))
    for (z0, z1, k, m) in layers:
        poly = scaled_poly(k, 0, 0)
        s2 = 16
        yy = -208
        while yy < 204:
            cy = yy + s2/2
            run = None
            xx = -208
            while xx <= 208:
                cx = xx + s2/2
                inside = in_poly(cx, cy, poly)
                if inside and run is None: run = xx
                if (not inside) and run is not None:
                    box('Estrato', ((run+xx)/2, cy, (z0+z1)/2), (xx-run+rs.uniform(0, 4), s2+.2, z0-z1), m, (0, 0, rs.uniform(-.03, .03)), col=False)
                    run = None
                xx += s2
            yy += s2
    # stalactite rocks under the island
    for i in range(14):
        a = i/14*2*PI + rs.uniform(-.1, .1)
        r = rs.uniform(30, 110)
        x, y = math.cos(a)*r, math.sin(a)*r
        h = rs.uniform(20, 46)
        box('Estalactite', (x, y, -100 - h/2 + 20), (rs.uniform(10, 22), rs.uniform(10, 22), h), rs.choice(['db_rock_dark', 'db_rock_deep']),
            (rs.uniform(-.1, .1), rs.uniform(-.1, .1), rs.uniform(0, PI)), col=False)

def edge_points(n, inset=.985, skip=None):
    """Evenly spaced points on the island outline (for rim rocks / trees)."""
    L = []
    tot = 0.0
    for i in range(len(OUTLINE)):
        a, b = Vector(OUTLINE[i]), Vector(OUTLINE[(i+1) % len(OUTLINE)])
        L.append((a, b, (b-a).length)); tot += (b-a).length
    out = []
    for k in range(n):
        d = k/n*tot
        for a, b, l in L:
            if d <= l:
                p = a.lerp(b, d/l) if l else a
                out.append((p.x*inset, p.y*inset, math.atan2((b-a).y, (b-a).x)))
                break
            d -= l
    return out
