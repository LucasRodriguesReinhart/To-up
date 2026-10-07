# Dragon Ball area library: reuses the Konoha primitive layer (klib) and adds the Vale Capsule palette
# plus a few shape helpers (domes, rings, arcs, pipes).
import sys, math
KONOHA = r"C:\Users\lucas\OneDrive\Desktop\To up\konoha_area\blender"
if KONOHA not in sys.path: sys.path.append(KONOHA)
import klib
from klib import *
from mathutils import Vector, Euler

ROOT = r"C:\Users\lucas\OneDrive\Desktop\To up\dragonball_area"
PI = math.pi

klib.PALETTE.update({
 # terrain
 'db_grass':((88,176,66),'Plastic','s'), 'db_grass_dark':((70,150,60),'Plastic','s'), 'db_grass_light':((128,196,80),'Plastic','s'),
 'db_rock':((190,118,70),'Plastic',''), 'db_rock_dark':((150,88,54),'Plastic',''), 'db_rock_light':((212,146,90),'Plastic',''),
 'db_rock_red':((168,84,54),'Plastic',''), 'db_rock_deep':((112,70,48),'Plastic',''),
 'db_dirt':((168,116,76),'Plastic','s'), 'db_dirt_dark':((132,92,64),'Plastic','s'), 'db_sand':((240,218,166),'Plastic','s'),
 'db_crater':((110,80,64),'Plastic','s'), 'db_scorch':((84,64,58),'Plastic',''),
 'db_path':((238,230,206),'SmoothPlastic',''), 'db_paving':((212,212,206),'Plastic','s'), 'db_asphalt':((112,120,132),'SmoothPlastic',''),
 'db_line':((70,150,235),'SmoothPlastic',''),
 'db_water':((70,186,240),'Glass','g'), 'db_water_deep':((44,140,210),'Glass','g'), 'db_foam':((214,242,252),'SmoothPlastic','g'),
 # capsule architecture
 'cc_white':((248,248,244),'SmoothPlastic',''), 'cc_cream':((244,232,200),'SmoothPlastic',''), 'cc_yellow':((252,212,104),'SmoothPlastic',''),
 'cc_peach':((250,196,150),'SmoothPlastic',''), 'cc_mint':((170,226,200),'SmoothPlastic',''), 'cc_pink':((246,170,178),'SmoothPlastic',''),
 'cc_blue':((58,128,222),'SmoothPlastic',''), 'cc_blue_dark':((38,82,158),'SmoothPlastic',''), 'cc_navy':((36,46,84),'SmoothPlastic',''),
 'cc_orange':((255,142,44),'SmoothPlastic',''), 'cc_red':((226,62,52),'SmoothPlastic',''), 'cc_grey':((170,178,190),'SmoothPlastic',''),
 'cc_metal':((194,202,214),'Metal',''), 'cc_metal_dark':((92,100,114),'Metal',''), 'cc_rubber':((46,48,56),'SmoothPlastic',''),
 'cc_window':((130,206,250),'Glass','g'), 'cc_window_dark':((52,86,128),'SmoothPlastic',''), 'cc_screen':((120,240,255),'Neon','n'),
 'cc_lamp':((255,244,200),'Neon','n'),
 # ki energy
 'ki_cyan':((96,232,255),'Neon','n'), 'ki_blue':((80,150,255),'Neon','n'), 'ki_gold':((255,214,80),'Neon','n'),
 'ki_purple':((196,116,255),'Neon','n'), 'ki_orange':((255,150,50),'Neon','n'), 'ki_white':((230,250,255),'Neon','n'),
 'ki_field':((110,230,255),'Neon','g'), 'ki_crystal':((150,236,255),'Glass','g'),
 # dragon / spheres
 'db_ball':((255,154,34),'Glass',''), 'db_star':((214,36,30),'SmoothPlastic',''),
 'dragon':((74,160,86),'SmoothPlastic',''), 'dragon_dark':((50,120,66),'SmoothPlastic',''), 'dragon_belly':((238,214,130),'SmoothPlastic',''),
 'dragon_eye':((255,50,40),'Neon','n'), 'dragon_horn':((246,240,220),'SmoothPlastic',''),
 'temple_stone':((226,218,196),'SmoothPlastic',''), 'temple_tile':((196,188,170),'Plastic',''), 'temple_roof':((196,64,48),'SmoothPlastic',''),
 # nature
 'tree_ball':((72,168,70),'SmoothPlastic',''), 'tree_ball_light':((120,194,82),'SmoothPlastic',''), 'tree_ball_dark':((46,128,72),'SmoothPlastic',''),
 'tree_ajisa':((64,168,150),'SmoothPlastic',''), 'db_trunk':((150,104,66),'Wood',''), 'palm_leaf':((82,178,76),'SmoothPlastic',''),
 'flower_pink':((255,150,190),'SmoothPlastic',''), 'flower_yellow':((255,228,90),'SmoothPlastic',''), 'flower_white':((255,252,240),'SmoothPlastic',''),
 'cloud':((255,255,255),'SmoothPlastic',''), 'cloud_shade':((226,238,250),'SmoothPlastic',''),
})

# ---------- helpers ----------
def dome(name, loc, r, m, sink=0.0, col=False, **kw):
    """Roblox balls are uniform: a dome is a sphere sunk into its base (sink = fraction of radius below loc)."""
    x, y, z = loc
    return ball(name, (x, y, z - r*sink), r*2, m, col=col, **kw)

def disc(name, loc, r, h, m, col=None, **kw):
    return cyl(name, loc, r, h, m, 'Z', col, **kw)

def ring(name, loc, r, thick, h, m, n=16, col=False, rz0=0.0, **kw):
    """Polygonal ring of boxes around a vertical axis."""
    x, y, z = loc
    L = 2*r*math.tan(PI/n) + .05
    out = []
    for i in range(n):
        a = rz0 + i/n*2*PI
        out.append(box(name, (x + math.cos(a)*r, y + math.sin(a)*r, z), (thick, L, h), m, (0, 0, a), col, **kw))
    return out

def vring(name, loc, r, thick, depth, m, n=16, rz=0.0, col=False, a0=0.0, a1=2*PI, **kw):
    """Vertical ring (arch when a0..a1 is partial) in the local XZ plane, rotated by rz around Z."""
    x, y, z = loc
    span = a1 - a0
    full = abs(span - 2*PI) < 1e-6
    steps = n if full else max(2, int(round(n*span/(2*PI))))
    L = 2*r*math.tan(span/steps/2) + .05
    out = []
    ca, sa = math.cos(rz), math.sin(rz)
    for i in range(steps):
        a = a0 + (i + .5)*span/steps
        lx, lz = math.cos(a)*r, math.sin(a)*r
        px, py = x + lx*ca, y + lx*sa
        # box long axis = local X rotated to the tangent
        out.append(box(name, (px, py, z + lz), (L, depth, thick), m, (0, -(a + PI/2), rz), col, **kw))
    return out

def pipe(name, pts, r, m, col=False, joints=True, **kw):
    """Cylinder pipe through a list of points with ball joints."""
    out = []
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        d = b - a
        q = d.to_track_quat('X', 'Z')
        out.append(part('C', name, (a+b)/2, (d.length, r*2, r*2), m, tuple(q.to_euler('XYZ')), col, **kw))
    if joints:
        for p in pts[1:-1]:
            out.append(ball(name + 'Junta', p, r*2.2, m))
    return out

def porthole(name, loc, r, facing, m_frame='cc_metal', m_glass='cc_window', depth=.4):
    """Round window (flat cylinder) facing angle `facing` around Z."""
    x, y, z = loc
    cyl(name + 'Aro', (x, y, z), r + .25, depth, m_frame, 'X', False, rot=(0, 0, facing))
    cyl(name, (x + math.cos(facing)*.08, y + math.sin(facing)*.08, z), r, depth + .04, m_glass, 'X', False, rot=(0, 0, facing))

# ---------- local-frame placement (tilted assemblies such as crystals) ----------
from mathutils import Matrix
def frame(loc, rot=(0, 0, 0)):
    return Matrix.Translation(Vector(loc)) @ Euler(rot, 'XYZ').to_matrix().to_4x4()

def xf(shape, name, M, loc, dims, m, rot=(0, 0, 0), col=False, **kw):
    R = M.to_3x3() @ Euler(rot, 'XYZ').to_matrix()
    return part(shape, name, tuple(M @ Vector(loc)), dims, m, tuple(R.to_euler('XYZ')), col, **kw)

def crystal(name, loc, h, w, m, tilt=(0, 0, 0), col=False, **kw):
    """Square crystal prism with a 4-corner-wedge pyramid tip; origin at its base."""
    M = frame(loc, tilt)
    body = h*.72
    xf('B', name, M, (0, 0, body/2), (w, w, body), m, col=col, **kw)
    tip = h - body
    for (sx, sy, a) in ((1, 1, 0), (-1, 1, PI/2), (-1, -1, PI), (1, -1, -PI/2)):
        xf('K', name + 'Ponta', M, (sx*w/4, sy*w/4, body + tip/2), (w/2, w/2, tip), m, (0, 0, a))

def emblem_board(name, loc, size, m, rz=0.0, kind='capsule', ink=None, depth=.3):
    kw = {'emblem': kind}
    if ink: kw['ink'] = ink
    return box(name, loc, (size, depth, size), m, (0, 0, rz), False, **kw)
