# k_props.py - pecas-heroi pequenas do kit: chiwen (com o cabo de espada cravado), bestas de espigao (imortal na ave,
# bestas, chuishou), lanterna de palacio hexagonal (gongdeng), lanterna vermelha, forro em caixotoes, tabua e terca do dougong.
import math
from mathutils import Vector, Matrix
from k_core import *

def crom(pts, n=6):
    """Catmull-Rom: amostra uma curva suave passando pelos pontos desenhados."""
    P = [Vector(p) for p in pts]; P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]; out = []
    for i in range(1, len(P) - 2):
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * P[i]) + (-P[i - 1] + P[i + 1]) * t + (2 * P[i - 1] - 5 * P[i] + 4 * P[i + 1] - P[i + 2]) * t2 + (-P[i - 1] + 3 * P[i] - 3 * P[i + 1] + P[i + 2]) * t3))
    out.append(P[-2]); return out

def lerp_list(vals, m):
    out = []
    for i in range(m):
        f = i / (m - 1) * (len(vals) - 1); a = int(math.floor(f)); b = min(a + 1, len(vals) - 1); out.append(vals[a] + (vals[b] - vals[a]) * (f - a))
    return out

def chiwen(gold='ouro'):
    """chiwen na ponta +X da cumeeira (cabeca virada para -X mordendo a cumeeira; corpo sobe por fora e enrola para dentro).
    Origem: ponta da cumeeira, z = base da cumeeira. ~7 studs de altura (exagero cartoon)."""
    B = Builder('KIT_chiwen', 401)
    B.add(t_box(-.9, 2.7, -1.0, 1.0, 0, 2.1, bev=.18, seg=3), 'telha', .45)                                     # sela sobre a ponta da cumeeira
    body = [(-.2, 0, 2.5), (.9, 0, 2.05), (1.95, 0, 2.45), (2.6, 0, 3.55), (2.5, 0, 4.9), (1.85, 0, 6.0), (.8, 0, 6.6), (-.25, 0, 6.45), (-.85, 0, 5.75), (-.62, 0, 5.05), (0, 0, 5.0)]
    rad = [1.22, 1.28, 1.22, 1.1, .97, .84, .71, .58, .46, .35, .2]
    cp = crom(body, 5); bm = t_tube(cp, lerp_list(rad, len(cp)), 12); xf(bm, scale=(1, .74, 1)); B.add(bm, gold, .5)
    B.add(xf(t_blob(1.38, (1.32, .88, .98), 2), loc=(-.35, 0, 3.35)), gold, .55)                               # cranio
    B.add(t_prism([(-.5, 3.55), (-2.95, 3.3), (-3.3, 2.95), (-3.1, 2.55), (-.5, 2.5)], 'Y', -.8, .8, bev=.16, seg=3), gold, .5)    # maxila sobre a cumeeira
    for s in (-1, 1):
        B.add(t_prism([(-.3, .5), (-2.2, .62), (-2.5, 1.0), (-2.2, 1.45), (-.3, 1.6)], 'Y', *sorted((s * .7, s * 1.05)), bev=.1), gold, .5)   # bochechas / mandibula
        B.add(xf(t_lathe([(0, 0), (.17, 0), (.05, .55), (0, .6)], 8), rot=(180, 0, 0), loc=(-2.85, s * .52, 2.62)), 'creme', .8)                 # presas
        B.add(xf(t_blob(.36, (1, .7, 1), 1), loc=(-1.15, s * .86, 3.85)), 'creme', .8)                                                          # olho
        B.add(xf(t_blob(.18, (1, .7, 1), 1), loc=(-1.27, s * 1.06, 3.85)), 'ferro', .2)
        brow = crom([(-1.85, s * .92, 4.05), (-1.25, s * 1.0, 4.4), (-.6, s * .95, 4.2)], 4)
        B.add(t_tube(brow, lerp_list([.16, .2, .1], len(brow)), 8), gold, .6)
        horn = crom([(-.1, s * .6, 4.35), (.6, s * .78, 4.95), (1.35, s * .72, 5.2), (1.9, s * .55, 5.0)], 5)
        B.add(t_tube(horn, lerp_list([.27, .2, .12, .04], len(horn)), 8), 'creme', .75)
    nose = [Vector((-3.05 + .34 * math.cos(math.radians(a)), 0, 3.55 + .34 * math.sin(math.radians(a)))) for a in range(-60, 240, 30)]
    B.add(t_tube(nose, lerp_list([.26, .2, .1], len(nose)), 8), gold, .6)                                          # focinho enrolado
    c0 = Vector((.95, 0, 4.4))
    for i in (9, 16, 23, 30):                                                                                     # barbatanas dorsais largas (nao espinhos)
        if i >= len(cp) - 1: break
        p = cp[i]; t = (cp[i + 1] - cp[i - 1]).normalized(); o = (p - c0); o.y = 0; o = (o - t * o.dot(t)).normalized()
        k = 1.2 - .02 * i; r = lerp_list(rad, len(cp))[i]
        a, b, c = p + o * (r * .7) - t * .85 * k, p + o * (r * .7) + t * .75 * k, p + o * (r + .62 * k) + t * .55 * k
        bm = bmesh_tri_prism(a, b, c, .34); B.add(bm, gold, .62)
    hp = cp[24]; ho = (hp - c0); ho.y = 0; ho.normalize()                                                          # cabo de espada cravado nas costas
    M = ho.to_track_quat('Z', 'Y').to_matrix()
    for prof, key in (([(0, 0), (.17, 0), (.17, 1.25), (0, 1.25)], 'mad'), ([(0, 1.25), (.3, 1.3), (.26, 1.6), (0, 1.68)], 'ouro')):
        bm = t_lathe(prof, 10); xf(bm, rot=M); xf(bm, loc=hp + ho * .55); B.add(bm, key, .6)
    g = t_box(-.62, .62, -.2, .2, -.12, .12, bev=.05); xf(g, rot=M); xf(g, loc=hp + ho * .62); B.add(g, 'bronze', .55)
    return B

def bmesh_tri_prism(a, b, c, th):
    import bmesh
    bm = bmesh.new(); n = (b - a).cross(c - a).normalized() * (th / 2)
    v = [bm.verts.new(p + n) for p in (a, b, c)] + [bm.verts.new(p - n) for p in (a, b, c)]
    bm.faces.new(v[0:3]); bm.faces.new(v[3:6][::-1])
    for i in range(3): bm.faces.new((v[i], v[(i + 1) % 3], v[3 + (i + 1) % 3], v[3 + i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); return bm

def besta(kind=0, gold='ouro'):
    """besta de espigao sentada, virada para -Y (para fora). kind: 0 leao, 1 cavalo, 2 peixe, 3 touro."""
    B = Builder('KIT_besta_%d' % kind, 410 + kind)
    B.add(t_box(-.46, .46, -.6, .6, 0, .18, bev=.05), 'telha', .45)
    B.add(xf(t_blob(.52, (.85, 1.05, 1.08), 1), loc=(0, .1, .66)), gold, .5)
    B.add(xf(t_blob(.3, (.8, .8, 1.3), 1), loc=(0, -.3, .5)), gold, .55)
    hs = (1.25, 1.1, 1.1) if kind == 0 else (.9, 1.0, 1.0)
    B.add(xf(t_blob(.36, hs, 1, lobes=6 if kind == 0 else 0, lobe_amp=.18), loc=(0, -.34, 1.32)), gold, .58)
    B.add(xf(t_blob(.2, (.9, 1.5 if kind == 1 else 1.1, .85), 1), loc=(0, -.68 if kind == 1 else -.6, 1.22)), gold, .62)
    for s in (-1, 1):
        if kind == 3: B.add(t_tube(crom([(s * .2, -.3, 1.55), (s * .5, -.3, 1.7), (s * .62, -.32, 1.98)], 3), [.1, .09, .07, .06, .05, .04, .02], 6), 'creme', .8)
        else: B.add(xf(t_lathe([(0, 0), (.12, 0), (.04, .34 if kind == 1 else .24), (0, .36 if kind == 1 else .26)], 6), rot=(0, 14 * s, 0), loc=(s * .22, -.28, 1.58)), gold, .6)
    if kind == 2: B.add(bmesh_tri_prism(Vector((0, .0, 1.1)), Vector((0, .6, .9)), Vector((0, .35, 1.75)), .16), gold, .62)
    tail = crom([(0, .55, .5), (0, .86, .85), (0, .8, 1.3), (0, .55, 1.5)], 3)
    B.add(t_tube(tail, lerp_list([.17, .15, .1, .04], len(tail)), 6), gold, .6)
    return B

def imortal(gold='ouro'):
    """o imortal montado na ave, que abre a fila de bestas na ponta do espigao."""
    B = Builder('KIT_imortal', 420)
    B.add(t_box(-.46, .46, -.7, .6, 0, .18, bev=.05), 'telha', .45)
    B.add(xf(t_blob(.46, (.8, 1.45, .8), 1), loc=(0, -.05, .62)), gold, .5)
    B.add(xf(t_blob(.22, (.9, 1, 1), 1), loc=(0, -.78, 1.02)), gold, .58)
    B.add(xf(t_lathe([(0, 0), (.1, 0), (0, .36)], 6), rot=(100, 0, 0), loc=(0, -.95, 1.0)), 'creme', .8)
    B.add(bmesh_tri_prism(Vector((0, .45, .7)), Vector((0, 1.05, .78)), Vector((0, .85, 1.42)), .2), gold, .6)
    B.add(xf(t_blob(.3, (.85, .85, 1.15), 1), loc=(0, .05, 1.22)), gold, .55)
    B.add(xf(t_blob(.2, (1, 1, 1), 1), loc=(0, 0, 1.68)), 'creme', .75)
    B.add(xf(t_lathe([(0, 0), (.3, 0), (.1, .16), (.07, .42), (0, .46)], 8), loc=(0, 0, 1.78)), gold, .6)
    return B

def chuishou(gold='ouro'):
    """cabeca de besta grande que fecha a fila, no degrau do espigao; virada para -Y."""
    B = Builder('KIT_chuishou', 421)
    B.add(t_box(-.8, .8, -.9, 1.0, 0, .3, bev=.08), 'telha', .45)
    B.add(xf(t_blob(.95, (.92, 1.2, 1.0), 2), loc=(0, .1, 1.15)), gold, .52)
    B.add(t_prism([(-.2, 1.2), (-1.75, 1.0), (-1.95, .7), (-1.75, .42), (-.2, .38)], 'X', -.55, .55, bev=.1, seg=2), gold, .5) if False else None
    B.add(xf(t_prism([(.2, 1.25), (1.75, 1.05), (1.95, .72), (1.72, .45), (.2, .4)], 'X', -.56, .56, bev=.1), rot=(0, 0, 180)), gold, .5)
    for s in (-1, 1):
        B.add(xf(t_blob(.24, (.7, 1, 1), 1), loc=(s * .66, -.62, 1.45)), 'creme', .8); B.add(xf(t_blob(.12, (.7, 1, 1), 1), loc=(s * .78, -.74, 1.45)), 'ferro', .2)
        horn = crom([(s * .4, .1, 1.9), (s * .62, .55, 2.45), (s * .55, 1.1, 2.7), (s * .4, 1.5, 2.55)], 4)
        B.add(t_tube(horn, lerp_list([.24, .18, .1, .03], len(horn)), 8), 'creme', .75)
    for i, y in enumerate((.5, .95, 1.35)):
        B.add(bmesh_tri_prism(Vector((0, y - .3, 1.9 - i * .25)), Vector((0, y + .3, 1.75 - i * .3)), Vector((0, y + .2, 2.55 - i * .4)), .2), gold, .62)
    return B

def lanterna_palacio():
    """gongdeng hexagonal pendurada. Origem no ponto de fixacao (z=0); desce ~6.2."""
    B = Builder('KIT_lanterna_palacio', 430)
    B.add(t_tube([Vector((0, 0, 0)), Vector((0, 0, -1.0))], [.07, .07], 6), 'bronze', .5)
    B.add(xf(t_lathe([(0, 0), (.22, 0), (.26, -.12), (.12, -.24), (0, -.26)][::-1], 8), loc=(0, 0, -.05)), 'bronze', .55)
    hexr = lambda prof: xf(t_lathe(prof, 6, smooth=False), rot=(0, 0, 30))
    B.add(hexr([(0, -.95), (.3, -.95), (.46, -1.12), (1.32, -1.5), (1.46, -1.72), (1.15, -1.78), (0, -1.78)][::-1]), 'mad', .45)             # coroa
    B.add(hexr([(1.12, -1.78), (1.2, -1.8), (1.2, -1.98), (1.12, -2.0)][::-1]), 'ouro', .6)
    B.add(hexr([(0, -2.0), (1.0, -2.0), (1.0, -4.15), (0, -4.15)][::-1]), 'chama', .6)                                                         # paineis de seda (emissivo)
    for i in range(6):
        a = math.radians(60 * i); c, s = math.cos(a), math.sin(a)
        B.add(xf(t_box(-.1, .1, -.1, .1, -4.2, -1.95, bev=.03), rot=(0, 0, 60 * i), loc=(1.04 * c, 1.04 * s, 0)), 'mad', .5)                 # montantes
        am = math.radians(60 * i + 30); cm, sm = math.cos(am), math.sin(am)
        for zz in (-2.45, -3.7): B.add(xf(t_box(-.5, .5, -.035, .035, -.05, .05), rot=(0, 0, 60 * i + 120), loc=(.92 * cm, .92 * sm, zz)), 'mad', .5)
        B.add(xf(t_box(-.035, .035, -.035, .035, -3.7, -2.45), rot=(0, 0, 60 * i + 120), loc=(.92 * cm, .92 * sm, 0)), 'verm', .5)
        tip = crom([(1.3 * c, 1.3 * s, -1.6), (1.62 * c, 1.62 * s, -1.5), (1.8 * c, 1.8 * s, -1.2), (1.66 * c, 1.66 * s, -.98)], 3)
        B.add(t_tube(tip, lerp_list([.1, .08, .06, .03], len(tip)), 6), 'ouro', .6)                                                          # ponteira revirada
        B.add(t_tube([Vector((1.78 * c, 1.78 * s, -1.22)), Vector((1.78 * c, 1.78 * s, -2.3))], [.03, .03], 5), 'tecido', .5)
        B.add(xf(t_lathe([(0, 0), (.06, 0), (.14, -.85), (0, -.9)][::-1], 6), loc=(1.78 * c, 1.78 * s, -2.3)), 'tecido', .45)
        B.add(xf(t_blob(.1, (1, 1, 1), 1), loc=(1.78 * c, 1.78 * s, -2.3)), 'ouro', .6)
    B.add(hexr([(0, -4.15), (1.12, -4.15), (1.2, -4.22), (1.2, -4.38), (.62, -4.72), (.26, -4.86), (0, -4.86)]), 'mad', .45)
    B.add(xf(t_blob(.22, (1, 1, 1), 1), loc=(0, 0, -5.02)), 'ouro', .6)
    B.add(xf(t_lathe([(0, 0), (.1, 0), (.3, -1.2), (.18, -1.32), (0, -1.34)][::-1], 8), loc=(0, 0, -5.15)), 'tecido', .45)
    return B

def lanterna_vermelha():
    """lanterna redonda vermelha (linguagem do modulo C1 aprovado): gomos, tampas de ouro e borla."""
    B = Builder('KIT_lanterna_vermelha', 431)
    B.add(t_tube([Vector((0, 0, 0)), Vector((0, 0, -.8))], [.06, .06], 6), 'bronze', .5)
    prof = [(0, -.8), (.55, -.8), (.62, -1.0), (1.2, -1.35), (1.55, -2.1), (1.55, -2.7), (1.2, -3.45), (.62, -3.8), (.55, -4.0), (0, -4.0)]
    B.add(t_lathe(prof[::-1], 20), 'tecido', .5)
    for i in range(10):
        a = math.radians(36 * i); pts = [Vector((r * 1.015 * math.cos(a), r * 1.015 * math.sin(a), z)) for r, z in prof[2:-2]]
        B.add(t_tube(crom([tuple(p) for p in pts], 3), [.035] * (3 * (len(pts) - 1) + 1), 5), 'ouro', .6)
    for z0, z1 in ((-1.02, -.78), (-4.02, -3.78)): B.add(t_lathe([(0, z1), (.66, z1), (.7, (z0 + z1) / 2), (.66, z0), (0, z0)], 16), 'ouro', .55)
    B.add(xf(t_lathe([(0, 0), (.09, 0), (.28, -1.3), (0, -1.4)][::-1], 8), loc=(0, 0, -4.1)), 'ouro', .5)
    return B

def forro_alpendre(L=9.0):
    """tianhua: forro plano em caixotoes (3x3) com rosaceas de ouro. Origem no centro, face para baixo em z=0."""
    B = Builder('KIT_forro_alpendre', 440)
    B.add(t_box(-L / 2, L / 2, -L / 2, L / 2, 0, .3), 'vermS', .4)
    n = 3; c = L / n
    for i in range(n + 1):
        p = -L / 2 + i * c
        B.add(t_box(p - .22, p + .22, -L / 2, L / 2, -.34, 0, bev=.06), 'jade', .5); B.add(t_box(-L / 2, L / 2, p - .22, p + .22, -.34, 0, bev=.06), 'jade', .5)
    for i in range(n):
        for j in range(n):
            x, y = -L / 2 + (i + .5) * c, -L / 2 + (j + .5) * c
            B.add(xf(t_lathe([(0, 0), (.62, 0), (.5, .1), (.3, .12), (.2, .2), (0, .22)], 12), rot=(180, 0, 0), loc=(x, y, 0)), 'ouro', .6)
            B.add(t_box(x - 1.05, x + 1.05, y - 1.05, y + 1.05, -.06, 0, bev=.03), 'jadeE', .45)
    return B

def tabua_dougong(L=9.0, h=8.0):
    """gongdianban: tabua vermelha atras/entre os dougong, fechando da prancha ate o forro."""
    B = Builder('KIT_tabua_dougong', 441)
    B.add(t_box(-L / 2, L / 2, -.2, .2, 0, h, bev=.04), 'verm', .45)
    return B

def terca(L=9.0):
    """tiaoyan fang: terca quadrada do beiral que corre sobre os dougong (origem no centro, fundo em z=0)."""
    B = Builder('KIT_terca', 442)
    B.add(t_box(-L / 2, L / 2, -.5, .5, 0, 1.0, bev=.08), 'verm', .5)
    for s in (-1, 1): B.add(t_box(-L / 2, L / 2, *sorted((s * .5, s * .55)), .38, .62), 'ouro', .6)
    return B
