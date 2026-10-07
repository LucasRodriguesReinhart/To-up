# Architectural components shared by all Konoha buildings.  Front of every asset faces -Y (south).
import math
from klib import *

PI = math.pi
FACE_ROT = {'S': 0.0, 'N': PI, 'E': PI/2, 'W': -PI/2}

class Body:
    def __init__(self, cx, cy, z0, w, d, h):
        self.cx, self.cy, self.z0, self.w, self.d, self.h = cx, cy, z0, w, d, h
    @property
    def top(self): return self.z0 + self.h
    def face(self, face, u, out):
        c = (self.cx, self.cy)
        if face == 'S': return (c[0]+u, c[1]-self.d/2-out)
        if face == 'N': return (c[0]-u, c[1]+self.d/2+out)
        if face == 'E': return (c[0]+self.w/2+out, c[1]+u)
        return (c[0]-self.w/2-out, c[1]-u)

def body(name, b, m, col=True):
    return box(name, (b.cx, b.cy, b.z0+b.h/2), (b.w, b.d, b.h), m, col=col)

def plate(b, face, u, zc, pw, ph, t, m, name, out=0.0, col=False, **kw):
    x, y = b.face(face, u, out + t/2)
    return box(name, (x, y, zc), (pw, t, ph), m, (0, 0, FACE_ROT[face]), col=col, **kw)

def window(b, face, u, zc, pw=3.0, ph=3.2, lit=False, sill=True, shutter=None):
    plate(b, face, u, zc, pw+.7, ph+.7, .3, 'wood_dark', 'MolduraJanela')
    plate(b, face, u, zc, pw, ph, .3, 'window_lit' if lit else 'glass', 'Vidro', out=.08)
    plate(b, face, u, zc, .22, ph, .2, 'wood_dark', 'Caixilho', out=.25)
    if sill: plate(b, face, u, zc-ph/2-.45, pw+1.1, .35, .9, 'wood', 'Peitoril')
    if shutter:
        plate(b, face, u, zc+ph/2+.55, pw+1.4, .5, 1.2, shutter, 'Toldo', out=.1)

def window_row(b, face, zc, n, spacing, pw=3.0, ph=3.2, lit_every=0, **kw):
    for i in range(n):
        u = (i - (n-1)/2) * spacing
        window(b, face, u, zc, pw, ph, lit=bool(lit_every) and i % lit_every == 0, **kw)

def door(b, face, u, w=4.2, h=7.0, m='wood', frame='wood_dark'):
    plate(b, face, u, b.z0+h/2+.1, w+.8, h+.6, .3, frame, 'PortalPorta')
    plate(b, face, u, b.z0+h/2, w, h, .3, m, 'Porta', out=.1)

def band(b, z, m='wood', t=.5, grow=.35, name='Friso'):
    return box(name, (b.cx, b.cy, z), (b.w+grow*2, b.d+grow*2, t), m, col=False)

def skirt(b, z, depth, rise, m, inset=.6):
    """Konoha eave ring: sloped tiles sticking out of every wall, hip corners."""
    cx, cy, w, d = b.cx, b.cy, b.w, b.d
    zc = z - rise/2
    oy = d/2 + depth/2 - inset
    ox = w/2 + depth/2 - inset
    wedge('Beiral', (cx, cy-oy, zc), (w, depth, rise), m, (0,0,0), col=False)
    wedge('Beiral', (cx, cy+oy, zc), (w, depth, rise), m, (0,0,PI), col=False)
    wedge('Beiral', (cx+ox, cy, zc), (d, depth, rise), m, (0,0,PI/2), col=False)
    wedge('Beiral', (cx-ox, cy, zc), (d, depth, rise), m, (0,0,-PI/2), col=False)
    for sx, sy, r in ((1,-1,-PI/2), (-1,-1,PI), (1,1,0), (-1,1,PI/2)):
        corner('BeiralCanto', (cx+sx*ox, cy+sy*oy, zc), (depth, depth, rise), m, (0,0,r), col=False)

def gable(b, z, rise, m, over=1.2, ridge='trim_dark', along='X'):
    """Two-slope roof. along='X': ridge runs east-west."""
    cx, cy = b.cx, b.cy
    if along == 'X':
        L, half = b.w + over*2, b.d/2 + over
        wedge('Telhado', (cx, cy-half/2, z+rise/2), (L, half, rise), m, (0,0,0), col=True)
        wedge('Telhado', (cx, cy+half/2, z+rise/2), (L, half, rise), m, (0,0,PI), col=True)
        box('Cumeeira', (cx, cy, z+rise+.15), (L+.4, .9, .5), ridge, col=False)
        box('Testeira', (cx, cy-half+.15, z-.1), (L, .3, .5), ridge, col=False)
    else:
        L, half = b.d + over*2, b.w/2 + over
        wedge('Telhado', (cx-half/2, cy, z+rise/2), (L, half, rise), m, (0,0,-PI/2), col=True)
        wedge('Telhado', (cx+half/2, cy, z+rise/2), (L, half, rise), m, (0,0,PI/2), col=True)
        box('Cumeeira', (cx, cy, z+rise+.15), (.9, L+.4, .5), ridge, col=False)

def flat_roof(b, m='wall_tan', lip=.5):
    box('Laje', (b.cx, b.cy, b.top+.25), (b.w+lip, b.d+lip, .5), m, col=True)

def tank(x, y, z, r=2.2, h=4.0, band_m='metal', legs=True):
    if legs:
        box('BaseCaixa', (x, y, z+.6), (r*1.6, r*1.6, 1.2), 'wood_dark', col=False)
        z += 1.2
    cyl('CaixaDagua', (x, y, z+h/2), r, h, 'tank', col=False)
    cyl('TampaCaixa', (x, y, z+h+.2), r+.25, .4, 'trim_dark', col=False)
    cyl('AroCaixa', (x, y, z+h*.3), r+.08, .35, band_m, col=False)
    cyl('AroCaixa', (x, y, z+h*.7), r+.08, .35, band_m, col=False)

def balcony(b, face, u, z, width, depth=2.6, m='wood', rail='wall_white'):
    x, y = b.face(face, u, depth/2)
    r = FACE_ROT[face]
    box('PisoVaranda', (x, y, z), (width, depth, .5), m, (0,0,r), col=True)
    fx, fy = b.face(face, u, depth-.15)
    box('ParapeitoVaranda', (fx, fy, z+1.3), (width, .3, 2.2), rail, (0,0,r), col=False)
    box('CorrimaoVaranda', (fx, fy, z+2.5), (width+.3, .5, .3), m, (0,0,r), col=False)
    for s in (-1, 1):
        sx, sy = b.face(face, u + s*(width/2-.15), depth/2)
        box('LateralVaranda', (sx, sy, z+1.3), (.3, depth, 2.2), rail, (0,0,r), col=False)

def stairs_side(b, face, u, z_top, run=10, width=3, m='wood'):
    """Exterior stair along a wall, starting at u and rising toward +u; landing at z_top."""
    x, y = b.face(face, u + run/2, width/2)
    r = FACE_ROT[face] - PI/2
    rise = z_top - b.z0
    wedge('EscadaExterna', (x, y, b.z0 + rise/2), (width, run, rise), m, (0,0,r), col=True)
    for i in range(1, int(rise)):
        t = i / rise
        sx, sy = b.face(face, u + run*t, width/2)
        box('Degrau', (sx, sy, b.z0 + i + .05), (width, .18, .12), 'wood_dark', (0,0,r), col=False)
    ex, ey = b.face(face, u, width - .1)
    fx, fy = b.face(face, u + run, width - .1)
    rod('CorrimaoEscada', (ex, ey, b.z0 + 3), (fx, fy, z_top + 3), .25, 'wood_dark')

def vsign(x, y, z, text, m='cloth_white', h=6.0, rot=0.0, w=1.8):
    box('PlacaVertical', (x, y, z), (w, .35, h), m, (0,0,rot), col=False, text=text)
    box('TopoPlaca', (x, y, z+h/2+.2), (w+.4, .5, .4), 'trim_dark', (0,0,rot), col=False)

def hsign(b, face, u, zc, text, w, h=2.4, m='wood'):
    plate(b, face, u, zc, w, h, .35, m, 'Letreiro', out=.2, text=text)

def noren(b, face, u, ztop, w=6.0, panels=4, m='noren', text=None):
    plate(b, face, u, ztop, w+.6, .3, .3, 'wood_dark', 'VaraNoren', out=.6)
    pw = w / panels
    for i in range(panels):
        uu = u - w/2 + pw*(i+.5)
        p = plate(b, face, uu, ztop-1.4, pw-.12, 2.6, .12, m, 'Noren', out=.62)
    if text:
        plate(b, face, u, ztop-1.2, w*.8, 1.4, .05, m, 'TextoNoren', out=.72, text=text)

def paper_lantern(x, y, z, m='lantern', light=False):
    cyl('LanternaPapel', (x, y, z), .75, 1.5, m, col=False, light='255,170,110,10,0.6' if light else 0)
    cyl('TampaLanterna', (x, y, z+.85), .45, .25, 'trim_dark', col=False)
    cyl('TampaLanterna', (x, y, z-.85), .45, .25, 'trim_dark', col=False)

def ac_unit(b, face, u, zc):
    plate(b, face, u, zc, 2.6, 1.8, 1.2, 'tank', 'ArCondicionado', out=0)
    plate(b, face, u, zc, 1.6, 1.2, .1, 'trim_dark', 'Grade', out=1.2)

def planter(x, y, z, w=3.0, rot=0.0, flowers=('cr_fire','cr_lightning','cloth_white')):
    box('Floreira', (x, y, z+.5), (w, 1.1, 1.0), 'wood', (0,0,rot), col=False)
    n = max(2, int(w/1.1))
    for i in range(n):
        ox = (i-(n-1)/2)*(w/n)
        dx, dy = ox*math.cos(rot), ox*math.sin(rot)
        ball('Folhagem', (x+dx, y+dy, z+1.2), .9, 'foliage')
        if i % 2 == 0:
            ball('Flor', (x+dx, y+dy, z+1.7), .45, flowers[i % len(flowers)])
