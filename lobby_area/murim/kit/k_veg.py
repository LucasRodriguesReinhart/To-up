# k_veg.py - vegetacao estilizada do kit: pinheiro em camadas (tronco em S, 5 massas assimetricas em dois tons), arbusto, tufo.
import math, random
from mathutils import Vector
from k_core import *
from k_props import crom, lerp_list

def pinheiro(seed=1, name='KIT_pinheiro_a', flip=1):
    B = Builder(name, 500 + seed); rnd = random.Random(seed)
    tr = crom([(0, 0, 0), (.55 * flip, .1, 2.3), (-.35 * flip, .25, 4.7), (.6 * flip, -.1, 6.9), (.2 * flip, 0, 8.7), (.0, 0, 9.6)], 5)
    B.add(t_tube(tr, lerp_list([.68, .56, .44, .33, .2, .1], len(tr)), 9), 'casca', .45)
    for a in range(5):                                            # raizes aparentes
        ang = math.radians(72 * a + 20)
        root = crom([(0, 0, .55), (.55 * math.cos(ang), .55 * math.sin(ang), .2), (1.05 * math.cos(ang), 1.05 * math.sin(ang), -.05)], 3)
        B.add(t_tube(root, lerp_list([.3, .2, .08], len(root)), 6), 'casca', .4)
    pads = [(-2.4 * flip, .3, 4.3, 2.7), (2.1 * flip, -.45, 5.5, 2.35), (-1.3 * flip, .25, 7.0, 2.05), (1.05 * flip, .1, 8.3, 1.65), (.1 * flip, 0, 9.7, 1.3)]
    for i, (x, y, z, r) in enumerate(pads):
        anchor = min(tr, key=lambda p: abs(p.z - (z - .7)))
        br = crom([tuple(anchor), ((anchor.x + x) / 2, (anchor.y + y) / 2, z - .9), (x * .8, y * .8, z - .45)], 3)
        B.add(t_tube(br, lerp_list([.22, .15, .08], len(br)), 6), 'casca', .42)
        B.add(xf(t_blob(r, (1.0, .86, .4), 2, lobes=6, lobe_amp=.17, seed=seed * 10 + i, flat_bottom=-.12 * r), rot=(0, 0, rnd.uniform(0, 360)), loc=(x, y, z)), 'pinho', .4 + .1 * i)
        B.add(xf(t_blob(r * .7, (1.0, .84, .42), 2, lobes=5, lobe_amp=.15, seed=seed * 20 + i, flat_bottom=-.1 * r), rot=(0, 0, rnd.uniform(0, 360)), loc=(x + .15 * flip, y, z + .34 * r)), 'folha', .5 + .08 * i)
    return B

def arbusto(seed=1, name='KIT_arbusto_a'):
    B = Builder(name, 520 + seed); rnd = random.Random(seed)
    for i, (x, y, r) in enumerate(((0, 0, 1.5), (1.25, .35, 1.1), (-1.1, -.3, 1.0), (.3, -.9, .85))):
        B.add(xf(t_blob(r, (1, 1, .78), 2, lobes=5, lobe_amp=.14, seed=seed * 7 + i, flat_bottom=-.35 * r), rot=(0, 0, rnd.uniform(0, 360)), loc=(x, y, r * .55)), 'pinho' if i % 2 == 0 else 'folha', .45 + .1 * i)
    return B

def tufo(seed=1, name='KIT_tufo_a'):
    B = Builder(name, 540 + seed); rnd = random.Random(seed)
    for i in range(8):
        a = rnd.uniform(0, math.tau); l = rnd.uniform(1.1, 1.9); o = rnd.uniform(.35, .8)
        bl = crom([(0, 0, 0), (math.cos(a) * o * .4, math.sin(a) * o * .4, l * .55), (math.cos(a) * o, math.sin(a) * o, l)], 3)
        bm = t_tube(bl, lerp_list([.13, .1, .02], len(bl)), 4, smooth=False); B.add(bm, 'folha', rnd.uniform(.35, .75))
    return B
