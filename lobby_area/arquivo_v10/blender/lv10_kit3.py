# lv10_kit3.py - pecas da REVISAO 3 do trecho: cordoes de fachada, braseiro de parede, ponte pedonal
# em arco, arvore de copa redonda, alamo v3 (mais massa de folhas), rochedo estratificado.
import bpy, bmesh, math, random, importlib, sys
sys.path.insert(0, r"C:\Users\lucas\OneDrive\Desktop\To up\lobby_area\blender")
import lvlib
from lvlib import box, cyl, ball, lathe, torus, ngon_prism, ring_prism, reg_poly, puff_cloud, _xform
from lv10_kit import noisy_ball

TAU = math.tau

def string_course(out, x0, x1, y, z, h=.6, d=.5, mat='SLT', gold=False):
    """cordao horizontal (faixa saliente) numa fachada com frente em +Y"""
    L = abs(x1 - x0); xc = (x0 + x1) / 2
    out.add(mat, box((L, d, h), (xc, y + d / 2 - .05, z + h / 2), bevel=.05))
    if gold:
        out.add('GLD', box((L, .12, .1), (xc, y + d + .02, z + h * .5)))

def sconce(out, pos, rot_z=0.0, s=1.0):
    """braseiro de parede: misula de pedra + taca de ouro + brasa (nao ocupa o piso). pos = ponto na parede (frente +Y)."""
    x, y, z = pos
    def P(bm):
        _xform(bm, (0, 0, 0), (0, 0, rot_z)); _xform(bm, (x, y, z)); return bm
    out.add('SLT', P(box((1.2 * s, 1.4 * s, .5 * s), (0, .7 * s, -.25 * s), bevel=.06)))
    out.add('SLT', P(ngon_prism([(-.5 * s, 0), (.5 * s, 0), (.2 * s, 1.3 * s), (-.2 * s, 1.3 * s)], .9 * s, (0, 0, 0), (math.pi / 2, 0, 0))))
    out.add('GLD', P(lathe([(.3 * s, 0), (.95 * s, .45 * s), (1.05 * s, .8 * s), (.8 * s, .95 * s)], (0, 1.1 * s, 0), seg=12)))
    out.add('EMB', P(ball(.62 * s, (0, 1.1 * s, 1.0 * s), seg=8, scl=(1, 1, .75))))

def footbridge(out, p0, p1, z, rise=2.2, W=4.6, mat='SLT'):
    """ponte pedonal em arco entre p0 e p1 (plano XY): tabuleiro subindo 'rise' no meio, balaustres,
    corrimao com filete de ouro, arco de alvenaria por baixo e pilares nas cabeceiras."""
    x0, y0 = p0; x1, y1 = p1
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy); a = math.atan2(dy, dx)
    n = 12
    seg = L / n
    for i in range(n):
        t0, t1 = i / n, (i + 1) / n
        zc = z + rise * math.sin(math.pi * (t0 + t1) / 2)
        pitch = math.atan2(rise * (math.sin(math.pi * t1) - math.sin(math.pi * t0)), seg)
        cx, cy = x0 + dx * (t0 + t1) / 2, y0 + dy * (t0 + t1) / 2
        bm = box((seg + .08, W, .7), (0, 0, 0))
        _xform(bm, (0, 0, 0), (0, -pitch, 0)); _xform(bm, (0, 0, 0), (0, 0, a)); _xform(bm, (cx, cy, zc - .35))
        out.add(mat, bm)
        for side in (-1, 1):
            ox, oy = -math.sin(a) * side * (W / 2 - .3), math.cos(a) * side * (W / 2 - .3)
            out.add(mat, lathe([(.22, 0), (.3, .15), (.15, .4), (.3, .95), (.32, 1.2), (.16, 1.55), (.26, 1.7)], (cx + ox, cy + oy, zc), seg=7))
    for side in (-1, 1):
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            zc0, zc1 = z + rise * math.sin(math.pi * t0) + 1.75, z + rise * math.sin(math.pi * t1) + 1.75
            cx, cy = x0 + dx * (t0 + t1) / 2, y0 + dy * (t0 + t1) / 2
            ox, oy = -math.sin(a) * side * (W / 2 - .3), math.cos(a) * side * (W / 2 - .3)
            pitch = math.atan2(zc1 - zc0, seg)
            bm = box((seg + .1, .5, .32), (0, 0, 0)); _xform(bm, (0, 0, 0), (0, -pitch, 0)); _xform(bm, (0, 0, 0), (0, 0, a))
            _xform(bm, (cx + ox, cy + oy, (zc0 + zc1) / 2)); out.add(mat, bm)
            bm = box((seg + .1, .24, .06), (0, 0, 0)); _xform(bm, (0, 0, 0), (0, -pitch, 0)); _xform(bm, (0, 0, 0), (0, 0, a))
            _xform(bm, (cx + ox, cy + oy, (zc0 + zc1) / 2 + .19)); out.add('GLD', bm)
    # arco segmentar SOB o tabuleiro: semicirculo largo com o topo encostado no tabuleiro (o resto fica sob a agua)
    R = L * .48
    bm = torus(R, .6, (0, 0, 0), (0, 0, 0), seg=24, sides=8, arc=math.pi)
    _xform(bm, (0, 0, 0), (math.pi / 2, 0, 0)); _xform(bm, (0, 0, 0), (0, 0, a)); _xform(bm, ((x0 + x1) / 2, (y0 + y1) / 2, z - .55 - R))
    out.add('ASH', bm)
    # laje-tímpano entre o arco e o tabuleiro (fecha o vao visivel acima da agua)
    bm = box((L * .7, W * .7, 1.6), (0, 0, 0)); _xform(bm, (0, 0, 0), (0, 0, a)); _xform(bm, ((x0 + x1) / 2, (y0 + y1) / 2, z - .9))
    out.add('ASH', bm)
    for t in (0.0, 1.0):
        cx, cy = x0 + dx * t, y0 + dy * t
        out.add('ASH', box((3.2, W + .8, 4.2), (cx, cy, z - 2.1), (0, 0, a)))
        out.add(mat, box((3.4, W + 1.0, .5), (cx, cy, z - .2), (0, 0, a), bevel=.08))

def round_tree(out, pos, h=11.0, r=3.6, seed=1, mat='LFV', flowers=None):
    """arvore verde de copa redonda (massa de folhas em esferas fundidas) com tronco e ramos"""
    x, y, z = pos
    rnd = random.Random(seed)
    out.add('TRK', lathe([(.55, 0), (.4, h * .45), (.22, h * .62)], (x, y, z), seg=8))
    cs = []
    for i in range(4):
        aa = rnd.random() * TAU
        bm = cyl(.14, h * .28, (0, 0, 0), seg=5)
        _xform(bm, (0, 0, 0), (math.radians(38 + rnd.random() * 20), 0, 0)); _xform(bm, (0, 0, 0), (0, 0, aa)); _xform(bm, (x, y, z + h * .5))
        out.add('TRK', bm)
        cs.append((x + math.cos(aa) * r * .55, y + math.sin(aa) * r * .55, z + h * .62 + rnd.random() * r * .3, r * (.55 + rnd.random() * .2)))
    cs += [(x, y, z + h * .7, r * .8), (x + (rnd.random() - .5) * r * .5, y + (rnd.random() - .5) * r * .5, z + h * .7 + r * .5, r * .62)]
    out.add(mat, puff_cloud(cs, r, seed=seed, seg=10))
    if flowers:
        for i in range(8):
            aa = rnd.random() * TAU; rr = r * (.7 + rnd.random() * .3)
            out.add(flowers, ball(.26, (x + math.cos(aa) * rr, y + math.sin(aa) * rr, z + h * .7 + rnd.random() * r * .6), seg=5))

def poplar3(out, pos, h=26.0, r=2.6, seed=1, mat='LFG', mat2='LFG2', density=1.0):
    """alamo dourado v3: mais massa de folhas (plumas maiores e sobrepostas + tufos nos ramos),
    ramificacao legivel, silhueta afinando; density/h/r variam por individuo."""
    x, y, z = pos
    rnd = random.Random(seed)
    out.add('TRK', lathe([(.5, 0), (.36, h * .3), (.2, h * .7), (.06, h * .96)], (x, y, z), seg=8))
    nb = 8
    for i in range(nb):
        t = .2 + .62 * i / (nb - 1)
        a = rnd.random() * TAU
        env = math.sin(math.pi * (.06 + .92 * t)) ** .7 * (1 - .5 * t) + .1
        L = r * env * 1.15
        bm = cyl(.08, L, (0, 0, 0), seg=5)
        _xform(bm, (0, 0, 0), (math.radians(48 + rnd.random() * 16), 0, 0)); _xform(bm, (0, 0, 0), (0, 0, a)); _xform(bm, (x, y, z + h * t))
        out.add('TRK', bm)
        ex, ey, ez = x + math.cos(a) * L * .78, y + math.sin(a) * L * .78, z + h * t + L * .62
        out.add(mat2 if i % 2 else mat, noisy_ball(.55 * (r / 2.6), (ex, ey, ez), seed=seed * 7 + i, seg=8, amp=.2, scl=(1.1, 1.1, 1.5)))
    n = int(90 * density)
    for i in range(n):
        t = .14 + .86 * (i / (n - 1)) ** .95
        env = math.sin(math.pi * (.06 + .92 * t)) ** .7 * (1 - .5 * t) + .1
        R = r * env
        a = rnd.random() * TAU
        d = R * (.1 + .9 * rnd.random())
        rr = (.62 + .45 * rnd.random()) * (1 - .3 * t) * (r / 2.6)
        bm = noisy_ball(rr, (0, 0, 0), seed=seed * 31 + i, seg=7, amp=.18, scl=(.55, .55, 1.7))
        _xform(bm, (0, 0, 0), (math.radians(6 + 30 * (d / max(R, .01))), 0, 0))
        _xform(bm, (0, 0, 0), (0, 0, a + math.pi / 2))
        _xform(bm, (x + math.cos(a) * d, y + math.sin(a) * d, z + h * t))
        out.add(mat if (i % 3) else mat2, bm)
    for k in range(3):
        out.add(mat, noisy_ball(.34 * (r / 2.6), (x + (rnd.random() - .5) * .4, y + (rnd.random() - .5) * .4, z + h * (.97 + .03 * k)), seed=seed + k, seg=7, amp=.1, scl=(.5, .5, 2.4)))

def cliff(out, pos, r=14.0, h=20.0, seed=1, mat='RCK', cap=True, tree=True):
    """rochedo estratificado: camadas de elipsoides irregulares empilhadas com recuo, topo achatado
    com tampa de grama, musgo nas prateleiras e arvore/arbustos. Massa natural, nao cone."""
    x, y, z = pos
    rnd = random.Random(seed)
    nl = 5
    top = z
    for i in range(nl):
        t = i / (nl - 1)
        rr = r * (1.0 - .32 * t) * (.92 + rnd.random() * .16)
        zz = z + h * (t * .82) + rr * .12
        ox, oy = (rnd.random() - .5) * r * .35, (rnd.random() - .5) * r * .35
        bm = noisy_ball(rr, (0, 0, 0), seed=seed * 13 + i, seg=10, amp=.16, scl=(1.0 + rnd.random() * .3, .85 + rnd.random() * .3, .42))
        _xform(bm, (0, 0, 0), (0, 0, rnd.random() * TAU)); _xform(bm, (x + ox, y + oy, zz))
        out.add(mat, bm)
        top = zz + rr * .42 * .75
        if i % 2 == 0 and i < nl - 1:
            aa = rnd.random() * TAU
            out.add('LFV', puff_cloud([(x + ox + math.cos(aa) * rr * .7, y + oy + math.sin(aa) * rr * .7, zz + rr * .36, rr * .22)], 1, seed=seed + i, seg=7))
    if cap:
        out.add('GRS', noisy_ball(r * .55, (x, y, top), seed=seed + 99, seg=10, amp=.1, scl=(1.05, .9, .18)))
        for k in range(3):
            aa = rnd.random() * TAU; dd = r * .25 * rnd.random()
            out.add('LFV', puff_cloud([(x + math.cos(aa) * dd, y + math.sin(aa) * dd, top + .4, .9 + rnd.random() * .8)], 1, seed=seed + k, seg=7))
        if tree:
            round_tree(out, (x + r * .15, y - r * .1, top), h=8 + rnd.random() * 3, r=2.6 + rnd.random(), seed=seed + 5)

def island_skirt(out, cx, cy, r_top, r_bot, z_top, depth, seed=1, mat='RCK'):
    """base rochosa da ilha flutuante (cone invertido irregular) para fechar o 'vazio' sob a plataforma"""
    rnd = random.Random(seed)
    prof = [(r_top, 0), (r_top * .98, -depth * .12), (r_top * .86, -depth * .4), (r_bot * 1.1, -depth * .75), (r_bot * .5, -depth * .95), (0.05, -depth)]
    bm = lathe(prof, (0, 0, 0), seg=28)
    for v in bm.verts:
        if v.co.z < -.1:
            k = 1 + (rnd.random() - .5) * .22
            v.co.x *= k; v.co.y *= k; v.co.z += (rnd.random() - .5) * depth * .05
    _xform(bm, (cx, cy, z_top))
    out.add(mat, bm)
