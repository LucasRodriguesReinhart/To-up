# k_telhado.py - telhado wudian (4 aguas) do kit: agua com calhas, telhas-capa individuais, wadang/dishui, tabua de beiral,
# forro, caibros redondos + caibros voadores, espigao com bestas, cumeeira principal. Tudo deriva de UMA funcao de superficie
# (curva concava juzhe: beiral quase deitado, topo ingreme; beiral reto no centro e canto levantado so no ultimo vao).
import math, random
import bmesh
from mathutils import Vector, Matrix
from k_core import *

class Roof:
    def __init__(s, EX, EY, RS, H, ZE, PER=1.35, LIFT=3.0, SL=9.5, OUT=1.3, LT=2.15):
        # LT = comprimento da telha-capa. Telhado maior pede telha maior: alem de ser o certo para a leitura a distancia,
        # e o que mantem a malha abaixo do teto de 20 mil triangulos do importador do Roblox.
        s.EX, s.EY, s.RS, s.RF, s.H, s.ZE, s.PER, s.LIFT, s.SL, s.OUT, s.LT = EX, EY, RS, EY, H, ZE, PER, LIFT, SL, OUT, LT
    def g(s, t): return .38 * t + .62 * t * t
    def w(s, a, b): return ((1 - smooth01(a / s.SL)) * (1 - smooth01(b / s.SL))) ** 1.35
    def front(s, x, t, dn=0.0):
        a = s.EX - abs(x); b = s.RF * t; w = s.w(max(a, 0), b); sx = 1 if x >= 0 else -1
        p = Vector((x + sx * s.OUT * w * .7071, -s.EY + s.RF * t - s.OUT * w * .7071, s.ZE + s.H * s.g(t) + s.LIFT * w))
        return p + s.n_front(x, t) * dn if dn else p
    def side(s, y, t, dn=0.0):
        a = s.EY - abs(y); b = s.RS * t; w = s.w(max(a, 0), b); sy = 1 if y >= 0 else -1
        p = Vector((s.EX - s.RS * t + s.OUT * w * .7071, y + sy * s.OUT * w * .7071, s.ZE + s.H * s.g(t) + s.LIFT * w))
        return p + s.n_side(y, t) * dn if dn else p
    def n_front(s, x, t):
        e = 1e-3; n = (s.front(x + e, t) - s.front(x - e, t)).cross(s.front(x, t + e) - s.front(x, t - e))
        n.normalize(); return n if n.z > 0 else -n
    def n_side(s, y, t):
        e = 1e-3; n = (s.side(y + e, t) - s.side(y - e, t)).cross(s.side(y, t + e) - s.side(y, t - e))
        n.normalize(); return n if n.z > 0 else -n
    def lim(s, which, t): return (s.EX - s.RS * t) if which == 'front' else (s.EY - s.RF * t)
    def P(s, which, c, t, dn=0.0): return s.front(c, t, dn) if which == 'front' else s.side(c, t, dn)
    def N(s, which, c, t): return s.n_front(c, t) if which == 'front' else s.n_side(c, t)
    def half(s, which): return s.EX if which == 'front' else s.EY

def _grid(R, which, NX, NT, t0, t1, dn, flip=False, corr=0.0, over=0.0):
    bm = bmesh.new(); rows = []
    for j in range(NT + 1):
        t = t0 + (t1 - t0) * j / NT; L = R.lim(which, t) + over; row = []
        for i in range(NX + 1):
            c = -L + 2 * L * i / NX
            cc = max(-R.lim(which, t) + 1e-4, min(R.lim(which, t) - 1e-4, c)) if over == 0 else c
            p = R.P(which, cc, t, dn)
            if corr: p = p + R.N(which, cc, t) * (-corr * (0.5 - 0.5 * math.cos(math.tau * c / R.PER)))
            row.append(bm.verts.new(p))
        rows.append(row)
    for j in range(NT):
        for i in range(NX):
            f = bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
            f.smooth = True
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    up = sum((f.normal.z for f in bm.faces)) > 0
    if up == flip: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    return bm

def agua(R, which, name, tile='telha'):
    """agua do telhado: leito das telhas-canal (com calhas entre as fiadas) + telhas-capa individuais + wadang + dishui."""
    B = Builder(name, 301 if which == 'front' else 302)
    half = R.half(which)
    NX = int(round(2 * half / (R.PER / 4)))
    B.add(_grid(R, which, NX, 14, 0.0, 1.0, 0.0, corr=.11), tile, .5)
    # --- telhas-capa (tongwa): meia-cana afunilada, cada uma apoiada sobre a de baixo
    tb = bmesh.new(); lay = tb.loops.layers.color.new('rnd'); rnd = random.Random(7 if which == 'front' else 8)
    wd = bmesh.new(); wlay = wd.loops.layers.color.new('rnd')
    kmax = int((half - .35) / R.PER); LT = getattr(R, 'LT', 2.15); SEG = 6
    row_starts = []
    for k in range(-kmax, kmax + 1):
        c = k * R.PER; tmax = min(1.0, (half - abs(c)) / (R.RS if which == 'front' else R.RF)) - .01
        if tmax <= .05: continue
        n = 40; ts = [tmax * i / n for i in range(n + 1)]; ps = [R.P(which, c, t) for t in ts]
        acc = [0.0]
        for a, b in zip(ps, ps[1:]): acc.append(acc[-1] + (b - a).length)
        def at(sv):
            sv = max(0.0, min(acc[-1], sv))
            for i in range(n):
                if acc[i + 1] >= sv:
                    f = (sv - acc[i]) / max(1e-6, acc[i + 1] - acc[i]); return ts[i] + (ts[i + 1] - ts[i]) * f
            return ts[-1]
        s0 = 0.0; first = True
        while s0 < acc[-1] - .25:
            s1 = min(acc[-1], s0 + LT); ta, tbb = at(s0), at(s1)
            pa, pb = R.P(which, c, ta), R.P(which, c, tbb); T = (pb - pa).normalized()
            Nn = R.N(which, c, (ta + tbb) / 2); Bn = T.cross(Nn).normalized(); Nn = Bn.cross(T).normalized()
            ra, rb = .43, .35; la, lb = .10, .0; r = rnd.random()
            ringa = [tb.verts.new(pa + Bn * (ra * math.cos(math.pi * i / SEG)) + Nn * (ra * .92 * math.sin(math.pi * i / SEG) + la - .04)) for i in range(SEG + 1)]
            ringb = [tb.verts.new(pb + T * .12 + Bn * (rb * math.cos(math.pi * i / SEG)) + Nn * (rb * .92 * math.sin(math.pi * i / SEG) + lb - .04)) for i in range(SEG + 1)]
            fs = [tb.faces.new((ringa[i], ringa[i + 1], ringb[i + 1], ringb[i])) for i in range(SEG)]
            fs.append(tb.faces.new(ringa[::-1]))
            for f in fs:
                f.smooth = True
                for l in f.loops: l[lay] = (r, r, r, 1)
            if first:
                row_starts.append((c, pa, T, Nn, Bn)); first = False
            s0 = s1
    bmesh.ops.recalc_face_normals(tb, faces=tb.faces)
    B.add(tb, tile, 'keep')
    # --- wadang (disco com aro e botao) na ponta de cada fiada e dishui (pingente) entre fiadas
    for (c, pa, T, Nn, Bn) in row_starts:
        M = Matrix((Bn, Nn, -T)).transposed()          # colunas: X=Bn, Y=N, Z=-T (para fora/baixo)
        d = t_lathe([(0, 0), (.47, 0), (.49, .07), (.40, .13), (.36, .08), (.2, .08), (.17, .15), (0, .17)], 12)
        xf(d, rot=M); xf(d, loc=pa + Nn * .16 - T * .05); B.add(d, tile, .35)
        g = t_lathe([(0, 0), (.16, 0), (.12, .06), (0, .08)], 8); xf(g, rot=M); xf(g, loc=pa + Nn * .16 - T * .21); B.add(g, 'ouro', .6)
    for (c0, p0, T0, N0, B0), (c1, p1, T1, N1, B1) in zip(row_starts, row_starts[1:]):
        pm = (p0 + p1) / 2; Tm = (T0 + T1).normalized(); Bm = (p1 - p0).normalized(); Zd = Vector((0, 0, 1))
        out = Vector((-Tm.x, -Tm.y, 0)).normalized()
        poly = [(-.56, .04), (.56, .04), (.5, -.22), (.26, -.46), (0, -.7), (-.26, -.46), (-.5, -.22)]
        pm2 = R.P(which, (c0 + c1) / 2, 0.0) - R.N(which, (c0 + c1) / 2, 0.0) * .1
        bm = bmesh.new(); f0 = [bm.verts.new(pm2 + Bm * a + Zd * b + out * .02) for a, b in poly]; f1 = [bm.verts.new(pm2 + Bm * a + Zd * b + out * .16) for a, b in poly]
        bm.faces.new(f0[::-1]); bm.faces.new(f1)
        for i in range(len(poly)): bm.faces.new((f0[i], f0[(i + 1) % len(poly)], f1[(i + 1) % len(poly)], f1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); B.add(bm, tile, .3)
    return B

def beiral(R, which, name):
    """estrutura sob a agua: tabua do beiral, forro de tabuas, caibros redondos (yanchuan) e caibros voadores (feizi)."""
    B = Builder(name, 311 if which == 'front' else 312)
    half = R.half(which); run = R.RF if which == 'front' else R.RS
    t_in = 5.9 / run
    B.add(_grid(R, which, int(half * 2 / 1.2), 5, 0.012, t_in, -.5, flip=True, over=0.0), 'vermS', .4)          # forro
    # tabua do beiral (lianyan): faixa sob a borda das telhas
    path = [R.P(which, -half + 2 * half * i / 60, 0.0, -.34) for i in range(61)]
    out = Vector((0, -1, 0)) if which == 'front' else Vector((1, 0, 0))
    path = [p - out * .16 for p in path]
    B.add(t_sweep([(-.2, -.3), (.2, -.3), (.2, .3), (-.2, .3)], path), 'verm', .5)
    # caibros
    sp = 1.12; n = int((half - 1.2) / sp); other = R.RS if which == 'front' else R.RF
    for k in range(-n, n + 1):
        c = k * sp
        d_hip = (half - abs(c)) * run / other            # os caibros morrem na linha do espigao (viga de canto)
        if d_hip < 2.2: continue
        def Q(d_in, off):
            return R.P(which, c, d_in / run, -off)
        d_in = min(5.7, d_hip - .7)
        if d_in - 1.7 > .9:
            a, b = Q(d_in, .5 + .46 + .27), Q(1.7, .5 + .46 + .27)
            B.add(t_tube([a, b], [.27, .27], 8), 'verm', .5)
            e = (b - a).normalized(); B.add(t_tube([b, b + e * .1], [.28, .28], 8), 'jade', .55)
        a2, b2 = Q(min(2.9, d_hip - .5), .5 + .22), Q(.3, .5 + .22)
        e2 = (b2 - a2).normalized(); nn = R.N(which, c, .1); sd = e2.cross(nn).normalized(); up = sd.cross(e2).normalized()
        bm = bmesh.new()
        r0 = [bm.verts.new(a2 + sd * u + up * v) for u, v in ((-.2, -.22), (.2, -.22), (.2, .22), (-.2, .22))]
        r1 = [bm.verts.new(b2 + sd * u + up * v) for u, v in ((-.2, -.22), (.2, -.22), (.2, .22), (-.2, .22))]
        for i in range(4): bm.faces.new((r0[i], r0[(i + 1) % 4], r1[(i + 1) % 4], r1[i]))
        bm.faces.new(r0[::-1]); bm.faces.new(r1); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); B.add(bm, 'verm', .5)
        bm = bmesh.new()
        r0 = [bm.verts.new(b2 + sd * u + up * v) for u, v in ((-.21, -.23), (.21, -.23), (.21, .23), (-.21, .23))]
        r1 = [bm.verts.new(b2 + e2 * .1 + sd * u + up * v) for u, v in ((-.21, -.23), (.21, -.23), (.21, .23), (-.21, .23))]
        for i in range(4): bm.faces.new((r0[i], r0[(i + 1) % 4], r1[(i + 1) % 4], r1[i]))
        bm.faces.new(r1); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); B.add(bm, 'jade', .55)
    return B

def viga_canto(R, name='KIT_viga_canto'):
    """laojiaoliang + zijiaoliang: viga diagonal sob o espigao, do eixo da coluna de canto ate alem da ponta do beiral, com
    ponteira de ouro. E nela que os caibros do canto morrem."""
    B = Builder(name, 315)
    ts = [(-.045 + i * (.62 + .045) / 14) for i in range(15)]
    def HP(t, off):
        tt = max(t, 0.0); p = R.front(R.EX - R.RS * tt - 1e-4, tt, -off)
        if t < 0:
            p0, p1 = R.front(R.EX - 1e-4, 0.0, -off), R.front(R.EX - R.RS * .03 - 1e-4, .03, -off)
            p = p0 + (p0 - p1).normalized() * (-t / .03) * (p0 - p1).length + Vector((0, 0, 1)) * (t * t * 60)
        return p
    low = [HP(t, .5 + .46 + .62) for t in ts[2:]]
    upp = [HP(t, .5 + .3) for t in ts]
    B.add(t_sweep([(-.5, -.62), (.5, -.62), (.5, .62), (-.5, .62)], low), 'verm', .5)
    B.add(t_sweep([(-.42, -.34), (.42, -.34), (.42, .34), (-.42, .34)], upp), 'verm', .55)
    e = (upp[0] - upp[1]).normalized()
    # ponteira: a viga de cima afina e sobe (cunha) e recebe uma luva de ouro; a de baixo termina em topo chanfrado
    tipp = [upp[0] - e * .1, upp[0] + e * .55 + Vector((0, 0, .12)), upp[0] + e * 1.05 + Vector((0, 0, .34))]
    B.add(t_tube(tipp, [.44, .33, .12], 8, smooth=False), 'ouro', .6)
    e2 = (low[0] - low[1]).normalized()
    B.add(t_tube([low[0] - e2 * .05, low[0] + e2 * .35], [.62, .4], 8, smooth=False), 'jade', .55)
    return B, upp[0], e

ESPIGAO = [(-.78, -.1), (.78, -.1), (.78, .42), (.58, .56), (.5, .98), (.62, 1.1), (.4, 1.42), (-.4, 1.42), (-.62, 1.1), (-.5, .98), (-.58, .56), (-.78, .42)]

def hip_path(R, t0=0.0, t1=1.0, n=26, dn=.05):
    return [R.front(R.EX - R.RS * t - 1e-4, t, dn) for t in [t0 + (t1 - t0) * i / n for i in range(n + 1)]]

def espigao(R, name='KIT_espigao'):
    """espigao diagonal frontal-direito: trecho baixo (com as bestas) ate t=.42, trecho alto dali a cumeeira, e ponta
    revirada alem do canto. Devolve (Builder, lista de ancoras (pos, tangente) para as bestas)."""
    B = Builder(name, 321)
    lo = hip_path(R, 0.0, .42, 14); hi = hip_path(R, .40, 1.0, 16)
    T0 = (lo[0] - lo[1]).normalized()
    tip = [lo[0] + T0 * d + Vector((0, 0, 1)) * (k) for d, k in ((1.5, .75), (1.1, .42), (.7, .2), (.35, .06))]
    B.add(t_sweep([(u * .78, v * .78) for u, v in ESPIGAO], tip + lo, smooth=False), 'telha', .45)
    B.add(t_sweep(ESPIGAO, hi, smooth=False), 'telha', .5)
    end = tip[0]; curl = [end + T0 * (.0 + .55 * math.sin(a)) + Vector((0, 0, 1)) * (.55 - .55 * math.cos(a)) for a in [math.radians(x) for x in range(0, 200, 25)]]
    B.add(t_tube(curl, [.5 - .4 * i / (len(curl) - 1) for i in range(len(curl))], 10), 'telha', .5)
    anchors = []
    for t in (.06, .135, .21, .285, .42):
        a, b = R.front(R.EX - R.RS * t - 1e-4, t, .05), R.front(R.EX - R.RS * (t + .02) - 1e-4, t + .02, .05)
        anchors.append((a, (a - b).normalized()))
    return B, anchors

CUME = [(-1.1, 0), (1.1, 0), (1.1, .4), (.82, .58), (.66, .62), (.66, 1.72), (.86, 1.86), (.86, 2.12), (.56, 2.42), (-.56, 2.42), (-.86, 2.12), (-.86, 1.86), (-.66, 1.72), (-.66, .62), (-.82, .58), (-1.1, .4)]

def cumeeira(R, name='KIT_cumeeira'):
    """cumeeira principal (zhengji) ao longo de X, com faixa e perolas de ouro nas duas faces."""
    B = Builder(name, 331)
    L = R.EX - R.RS; z = R.ZE + R.H - .25
    B.add(t_sweep(CUME, [Vector((-L - .2, 0, z)), Vector((L + .2, 0, z))]), 'telha', .5)
    for s in (-1, 1):
        ya, yb = sorted((s * .66, s * .72))
        for zz in (z + .78, z + 1.5): B.add(t_box(-L, L, ya, yb, zz, zz + .1), 'ouro', .6)
        nper = int(2 * L / 2.2)
        for i in range(nper + 1):
            x = -L + 1.1 + i * (2 * L - 2.2) / max(1, nper)
            B.add(xf(t_lathe([(0, 0), (.26, 0), (.2, .1), (0, .14)], 10), rot=(-90 * s, 0, 0), loc=(x, s * .66, z + 1.18)), 'ouro', .65)
    return B, z
