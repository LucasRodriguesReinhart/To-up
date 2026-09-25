# il_terrain_stone - alvenaria da Ilha 1 (zona terrain, prefixo TER_): muros de arrimo em fiadas com capeamento,
# guarda-corpos (balaustrada na frente da vila, mureta com capa no anel e nas quedas) e as escadas de pedra.
# Posicoes, vaos e colisoes iguais ao blockout (terrace_guards / stairs_all). Usado por il_terrain.build().
import math
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box
import il_layout as L
import fm_parts as FP
from il_col import RADIAL_STAIRS, STAIR_TOP_R

WL = "Stone_Wall_Light"
WD = "Stone_Wall_Dark"
C = "02_TERRAIN"
GUARD_AREA = "TerrainGuard"
STAIR_AREA = "TerrainStairs"


# ------------------------------------------------------------------ caminhos (reta / arco) parametrizados por s
def path_line(a, b):
    a = Vector((a[0], a[1], 0.0))
    b = Vector((b[0], b[1], 0.0))
    d = b - a
    ln = d.length
    t = d / ln

    def f(s):
        return a + t * s, t
    return ln, f


def path_arc(r, a0, a1, cx=0.0, cy=0.0):
    """arco anti-horario de a0 a a1 (graus, a1 > a0)"""
    ln = r * math.radians(a1 - a0)

    def f(s):
        th = math.radians(a0) + s / r
        c, sn = math.cos(th), math.sin(th)
        return Vector((cx + r * c, cy + r * sn, 0.0)), Vector((-sn, c, 0.0))
    return ln, f


# ------------------------------------------------------------------ muro de arrimo em fiadas
def masonry(mb, path, face_side, z0, z1, rng, thick=1.4, course=1.8, blk=(2.8, 4.8), cap_h=0.55, cap_over=0.3,
            cap_raise=0.06, cap_m=WD, dark_p=0.1, gap=0.17, cap=True):
    """face do muro na linha do caminho, voltada para a esquerda (face_side=+1) ou direita (-1) do sentido;
    o corpo fica do outro lado (dentro do terraco). Fiadas regulares, juntas desencontradas, fiada de base
    escura, blocos saindo 0,05..0,16 da face (sombra entre as pedras), capeamento em lajes longas."""
    ln, f = path
    if ln < 0.5:
        return 0
    ztop_c = z1 + cap_raise - (cap_h if cap else 0.0)
    H = ztop_c - z0
    nc = max(1, int(round(H / course)))
    ch = H / nc
    nb = 0
    for k in range(nc):
        za = z0 + ch * k
        s = -rng.uniform(0.3, blk[0] * 0.9) if k % 2 else -rng.uniform(0.0, 0.6)
        while s < ln - 0.05:
            w = rng.uniform(*blk)
            sa, sb = max(s, 0.0), min(s + w, ln)
            if ln - sb < 1.3:
                sb = ln
            s = sb
            if sb - sa < 0.5:
                continue
            p, t = f((sa + sb) * 0.5)
            left = Vector((-t.y, t.x, 0.0)) * face_side
            out = rng.uniform(0.05, 0.16)
            c = p - left * (thick * 0.5 - out)
            m = WD if (k == 0 and nc > 1) or rng.random() < dark_p else WL
            hh = ch - gap * 0.8 + rng.uniform(-0.04, 0.02)
            mb.box((sb - sa - gap, thick, hh), (c.x, c.y, za + ch * 0.5), (0, 0, math.atan2(t.y, t.x)
                                                                                   + rng.uniform(-0.012, 0.012)),
                   m, 0.0)
            nb += 1
    if cap:
        s = -rng.uniform(0.0, 2.0)
        while s < ln - 0.05:
            w = rng.uniform(3.6, 6.0)
            sa, sb = max(s, 0.0), min(s + w, ln)
            if ln - sb < 1.6:
                sb = ln
            s = sb
            if sb - sa < 0.5:
                continue
            p, t = f((sa + sb) * 0.5)
            left = Vector((-t.y, t.x, 0.0)) * face_side
            dep = thick + cap_over
            c = p - left * (dep * 0.5 - cap_over)
            mb.box((sb - sa - 0.1, dep, cap_h), (c.x, c.y, z1 + cap_raise - cap_h * 0.5),
                   (0, 0, math.atan2(t.y, t.x)), cap_m, 0.0)
            nb += 1
    return nb


# ------------------------------------------------------------------ guarda-corpos (mesma colisao do stone_parapet)
def guard(mb, pts, z, kind="bal", area=GUARD_AREA, posts_every=1):
    """kind 'bal' = balaustrada (soco, balaustres, corrimao, pilaretes com capa); 'wall' = mureta macica com capa.
    Colisao: 1 caixa (L, 1.2, 4) por segmento, igual a il_col.guard / fm_parts.stone_parapet."""
    P = [Vector((p[0], p[1], z)) for p in pts]
    n = len(P)
    for i, (a, b) in enumerate(zip(P, P[1:])):
        d = b - a
        ln = d.length
        if ln < 0.2:
            continue
        t = d / ln
        ang = math.atan2(t.y, t.x)
        c = (a + b) * 0.5
        mb.box((ln + 0.05, 1.2, 0.5), (c.x, c.y, z + 0.25), (0, 0, ang), WD, 0.0)
        if kind == "bal":
            mb.box((ln + 0.05, 1.05, 0.42), (c.x, c.y, z + 2.02), (0, 0, ang), WL, 0.0)
            # balaustres entre os pilaretes
            clear = ln - 1.4
            nbal = max(1, int(clear / 1.25))
            for k in range(nbal):
                q = a + t * (0.7 + clear * (k + 0.5) / nbal)
                mb.box((0.46, 0.46, 1.34), (q.x, q.y, z + 1.14), (0, 0, ang + math.pi / 4), WL, 0.0)
        else:
            mb.box((ln + 0.05, 0.95, 1.35), (c.x, c.y, z + 1.17), (0, 0, ang), WL, 0.0)
            mb.box((ln + 0.12, 1.35, 0.36), (c.x, c.y, z + 2.02), (0, 0, ang), WD, 0.0)
        ends = [a] if i < n - 2 else [a, b]
        for k, q in enumerate(ends):
            if kind != "bal" and (i % posts_every) and k == 0:
                continue
            mb.box((1.3, 1.3, 2.45), (q.x, q.y, z + 1.22), (0, 0, ang), WL, 0.12)
            mb.box((1.6, 1.6, 0.34), (q.x, q.y, z + 2.6), (0, 0, ang), WD, 0.1)
        col_box(area, (ln, 1.2, 4.0), (c.x, c.y, z + 2.0), (0, 0, ang))


def arc_spans(r, a0, a1, gaps):
    spans = [(a0, a1)]
    for ang, hw in gaps:
        da = math.degrees(hw / r)
        new = []
        for s0, s1 in spans:
            g0, g1 = ang - da, ang + da
            if g1 <= s0 or g0 >= s1:
                new.append((s0, s1))
                continue
            if g0 > s0:
                new.append((s0, g0))
            if g1 < s1:
                new.append((g1, s1))
        spans = new
    return [(s0, s1) for s0, s1 in spans if s1 - s0 >= 0.5]


def arc_guard(mb, r, a0, a1, z, kind, gaps, step=4.0, posts_every=1):
    for s0, s1 in arc_spans(r, a0, a1, gaps):
        guard(mb, IL.arc_pts(r, s0, s1, step), z, kind, posts_every=posts_every)


# ------------------------------------------------------------------ utilidades
def ray_rim(ang_deg):
    """raio (a partir da origem) ate a borda da ilha no angulo dado"""
    u = (math.cos(math.radians(ang_deg)), math.sin(math.radians(ang_deg)))
    rim = IL.rim()
    best = None
    for i in range(len(rim)):
        a, b = rim[i], rim[(i + 1) % len(rim)]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = u[0] * ey - u[1] * ex
        if abs(den) < 1e-9:
            continue
        t = (a[0] * ey - a[1] * ex) / den
        v = (a[0] * u[1] - a[1] * u[0]) / den
        if t > 0 and 0.0 <= v <= 1.0:
            best = t if best is None else min(best, t)
    return best


def bridge_span_x(x):
    """trecho em y que a ponte de saida (largura EXIT_W + folga) ocupa ao cruzar a vertical x"""
    ux, uy = L.exit_dir()
    sx, sy = L.EXIT_START
    yc = sy + (x - sx) * uy / ux
    hw = (L.EXIT_W / 2 + 1.0) / ux
    return yc - hw, yc + hw


def t1_arc_spans():
    """trechos do muro T1 (r 88) entre os entalhes das escadas radiais (mesmos entalhes do il_col)"""
    a0, a1 = L.T1_WALL_A
    gaps = []
    for _, ang, w in RADIAL_STAIRS:
        hw = w / 2 + 0.6
        gaps.append((ang, math.degrees(math.asin(hw / L.T1_WALL_R))))
    spans = [(a0, a1)]
    for g, da in gaps:
        new = []
        for s0, s1 in spans:
            if g + da <= s0 or g - da >= s1:
                new.append((s0, s1))
                continue
            if g - da > s0:
                new.append((s0, g - da))
            if g + da < s1:
                new.append((g + da, s1))
        spans = new
    return spans


def pilasters(mb, path, face_side, z0, z1, every=15.0, w=2.4, out=0.9, area="TerrainWall"):
    """contrafortes nos muros altos e compridos: cunhais em blocos alternados (claro/escuro) + capa que emenda no
    capeamento do muro; colisao propria (saem da face do muro para o lado caminhavel)"""
    ln, f = path
    n = max(1, int(ln // every))
    for k in range(1, n + 1):
        s = ln * k / (n + 1)
        p, t = f(s)
        left = Vector((-t.y, t.x, 0.0)) * face_side
        yaw = math.atan2(t.y, t.x)
        c = p + left * (out * 0.5 - 0.15)
        zt = z1 - 0.55
        nb = max(2, int(round((zt - z0) / 2.4)))
        hb = (zt - z0) / nb
        for i in range(nb):
            ww = w + (0.35 if i % 2 else 0.0)
            mb.box((ww, out + 0.3, hb - 0.12), (c.x, c.y, z0 + hb * (i + 0.5)), (0, 0, yaw), WD if i % 2 else WL, 0.0)
        cc = p + left * ((out + 0.35) * 0.5 - 0.2)
        mb.box((w + 0.7, out + 0.75, 0.62), (cc.x, cc.y, z1 + 0.06 - 0.31), (0, 0, yaw), WD, 0.0)
        col_box(area, (w + 0.4, out + 0.3, z1 - z0 + 0.6), (c.x, c.y, (z0 + z1) * 0.5 + 0.3), (0, 0, yaw))


def pier(mb, x, y, z0, z1, yaw, s=3.0, area="TerrainWall"):
    """pilar de canto/arremate onde o muro morre na borda do penhasco ou encontra outro muro"""
    nb = max(2, int(round((z1 - z0) / 2.2)))
    hb = (z1 - 0.6 - z0) / nb
    for i in range(nb):
        ss = s + (0.3 if i % 2 else 0.0)
        mb.box((ss, ss, hb - 0.12), (x, y, z0 + hb * (i + 0.5)), (0, 0, yaw), WD if i % 2 else WL, 0.0)
    mb.box((s + 0.8, s + 0.8, 0.66), (x, y, z1 + 0.06 - 0.33), (0, 0, yaw), WD, 0.08)
    col_box(area, (s + 0.3, s + 0.3, z1 - z0 + 0.8), (x, y, (z0 + z1) * 0.5 + 0.4), (0, 0, yaw))


# ------------------------------------------------------------------ muros de arrimo
def walls(rng):
    mb = MB("TER_Retaining_Walls", C, rng, detail="near")
    n = 0
    # muro interno do fosso (r 60): fosso -> anel, capa saliente (meio-fio da borda do fosso)
    n += masonry(mb, path_arc(L.PIT_R, 0.0, 360.0), +1, L.PIT - 0.4, L.RING, rng, thick=1.4, course=1.75,
                 blk=(3.2, 5.0), cap_h=0.6, cap_over=0.35, cap_raise=0.12, cap_m=WL, dark_p=0.12)
    # muro externo do anel (r 82 -> G), fora do setor do T1
    a0, a1 = L.T1_WALL_A
    n += masonry(mb, path_arc(L.RING_R1, a1, 360.0 + a0), -1, L.G - 0.5, L.RING, rng, thick=1.4, course=1.5,
                 blk=(3.0, 4.8), cap_raise=0.1)
    # muro T1 em arco (r 88), entre os entalhes das escadas
    for s0, s1 in t1_arc_spans():
        n += masonry(mb, path_arc(L.T1_WALL_R, s0, s1), +1, L.RING - 0.3, L.T1, rng, course=1.55)
    # paredes dos entalhes das escadas radiais (anel -> T1)
    for _, ang, w in RADIAL_STAIRS:
        u = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang)), 0.0))
        v = Vector((-u.y, u.x, 0.0))
        hw = w / 2 + 0.6
        rin = math.sqrt(L.T1_WALL_R ** 2 - hw * hw)
        for sd in (-1, 1):
            a = u * rin + v * (sd * hw)
            b = u * (STAIR_TOP_R + 0.2) + v * (sd * hw)
            n += masonry(mb, path_line(a, b), -sd, L.RING - 0.3, L.T1, rng, course=1.55, blk=(2.4, 4.2),
                         cap=False)
    # muros radiais 26 e 200 graus (T1 -> G e ponta da faixa do anel -> G)
    r26 = 108.0 / math.cos(math.radians(a0))
    r200 = ray_rim(a1) + 0.5
    for ang, r_end, fs in ((a0, r26, -1), (a1, r200, +1)):
        u = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        pa = (u[0] * (L.RING_R1 - 1.4), u[1] * (L.RING_R1 - 1.4))
        pb = (u[0] * L.T1_WALL_R, u[1] * L.T1_WALL_R)
        pc = (u[0] * r_end, u[1] * r_end)
        n += masonry(mb, path_line(pa, pb), fs, L.G - 0.5, L.RING, rng, course=1.5, cap_raise=0.1)
        n += masonry(mb, path_line(pb, pc), fs, L.G - 0.5, L.T1, rng, course=1.7)
        pilasters(mb, path_line(pb, pc), fs, L.G - 0.5, L.T1, every=14.0)
    # face x = 108 (T1 -> vale leste)
    y26 = 108.0 * math.tan(math.radians(a0))
    # a ponte de saida (tabuleiro no T1) cruza este muro: por baixo dela o capeamento fica dentro do tabuleiro
    yb0, yb1 = bridge_span_x(108.0)
    for ya, yb, under in ((y26 - 0.7, yb0, False), (yb0, yb1, True), (yb1, L.T2_WALL_Y, False)):
        pth = path_line((108.0, ya), (108.0, yb))
        n += masonry(mb, pth, -1, L.G - 0.5, L.T1, rng, course=1.7, cap_raise=(-0.4 if under else 0.06))
        if not under and yb - ya > 20.0:
            pilasters(mb, pth, -1, L.G - 0.5, L.T1, every=15.0)
    # muro T2 (y 126): T1 -> T2 com o vao da escada central; x 108..118 desce ate o vale (G)
    hw = L.T2_STAIR_W / 2 + 0.6
    xw = -147.6
    n += masonry(mb, path_line((xw, L.T2_WALL_Y), (-hw, L.T2_WALL_Y)), -1, L.T1 - 0.3, L.T2, rng, course=1.55)
    n += masonry(mb, path_line((hw, L.T2_WALL_Y), (108.0, L.T2_WALL_Y)), -1, L.T1 - 0.3, L.T2, rng, course=1.55)
    n += masonry(mb, path_line((108.0, L.T2_WALL_Y), (118.6, L.T2_WALL_Y)), -1, L.G - 0.5, L.T2, rng, course=1.8)
    # pilares de arremate: muro T2 na borda oeste, canto do x=108 com o raio de 26 graus, muro radial de 200 graus
    # na borda (o canto x=108 / y=126 fica livre: e onde o riacho despenca do T2)
    pier(mb, xw + 1.9, L.T2_WALL_Y - 0.9, L.T1 - 0.3, L.T2, 0.0)
    pier(mb, 108.4, y26 - 0.2, L.G - 0.5, L.T1, 0.0)
    u200 = (math.cos(math.radians(a1)), math.sin(math.radians(a1)))
    rp = r200 - 2.4
    pier(mb, u200[0] * rp + 0.35 * u200[1] * -1.0, u200[1] * rp + 0.35 * u200[0], L.G - 0.5, L.T1, math.radians(a1))
    # paredes do entalhe da escada T2
    top = L.T2_STAIR_Y0 + 8 * L.TREAD + 0.2
    for sd in (-1, 1):
        n += masonry(mb, path_line((sd * hw, L.T2_WALL_Y), (sd * hw, top)), sd, L.T1 - 0.3, L.T2, rng,
                     course=1.55, blk=(1.8, 3.8), cap=False)
    mb.finish()
    return n


# ------------------------------------------------------------------ guarda-corpos (mesmos vaos do terrace_guards)
def guards(rng):
    mb = MB("TER_Guards", C, rng, detail="near")
    a0, a1 = L.T1_WALL_A
    # borda externa do anel onde fora e G: vaos da escada da entrada e da escada do moinho
    arc_guard(mb, L.RING_R1 - 0.7, a1, 360.0 + a0, L.RING, "wall",
              [(270.0, L.ENTRY_STAIR_W / 2 + 0.8), (360.0 + math.degrees(math.atan2(L.MILL_STAIR[1], 82.0)), 5.2)],
              step=4.0, posts_every=2)
    # topo do muro T1 (arco r 88), vaos nas escadas radiais: balaustrada (frente da vila)
    arc_guard(mb, L.T1_WALL_R + 0.8, a0, a1, L.T1, "bal", [(ang, w / 2 + 0.8) for _, ang, w in RADIAL_STAIRS],
              step=4.0)
    # topo do muro T2 (y 126), vao da escada central
    hw = L.T2_STAIR_W / 2 + 0.8
    guard(mb, [(-L.T2_WALL_X[1] - 36, L.T2_WALL_Y + 0.8), (-hw, L.T2_WALL_Y + 0.8)], L.T2, "bal")
    guard(mb, [(hw, L.T2_WALL_Y + 0.8), (107.0, L.T2_WALL_Y + 0.8)], L.T2, "bal")
    # T1 -> vale leste (x = 108), aberta na ponte de saida; raios 26/200 graus
    ex = L.EXIT_START
    y_bridge = ex[1] + (108.0 - ex[0])
    guard(mb, [(107.2, 52.0), (107.2, y_bridge - 10.0)], L.T1, "wall")
    guard(mb, [(107.2, y_bridge + 10.0), (107.2, L.T2_WALL_Y)], L.T1, "wall")
    for ang in L.T1_WALL_A:
        a = math.radians(ang)
        p0 = (L.T1_WALL_R * math.cos(a), L.T1_WALL_R * math.sin(a))
        p1 = ((L.T1_WALL_R + 70) * math.cos(a), (L.T1_WALL_R + 70) * math.sin(a))
        if ang < 90:
            t = (107.2 - p0[0]) / (p1[0] - p0[0])
            p1 = (107.2, p0[1] + (p1[1] - p0[1]) * t)
        else:
            r_end = ray_rim(ang) - 1.0          # no blockout passava da borda (ficava no ar): para na borda
            p1 = (r_end * math.cos(a), r_end * math.sin(a))
        guard(mb, [p0, p1], L.T1, "wall")
    mb.finish()


# ------------------------------------------------------------------ escadas (mesmas posicoes do stairs_all)
def newels(mb, base, ang, w):
    """pilaretes de pedra no pe da escada (os banzos comecam baixos): com colisao"""
    F = FP.Frame(base[0], base[1], base[2], ang)
    for sd in (-1, 1):
        q = F.p(-0.35, sd * (w / 2 + 0.6), 0.0)
        mb.box((1.8, 1.8, 0.5), (q.x, q.y, q.z + 0.25), F.r(), WD, 0.0)
        mb.box((1.45, 1.45, 2.6), (q.x, q.y, q.z + 1.8), F.r(), WL, 0.12)
        mb.box((1.9, 1.9, 0.42), (q.x, q.y, q.z + 3.3), F.r(), WD, 0.1)
        col_box(STAIR_AREA, (1.8, 1.8, 3.6), (q.x, q.y, q.z + 1.8), F.r())


def stairs(rng):
    mb = MB("TER_Stairs", C, rng, detail="near")
    n1 = 8
    r1 = (L.T1 - L.RING) / n1
    for key, ang, w in RADIAL_STAIRS:
        a = math.radians(ang)
        base = (82.5 * math.cos(a), 82.5 * math.sin(a), L.RING)
        FP.stairs(mb, STAIR_AREA, base, a, w, n1, r1, L.TREAD, WL, WD)
        newels(mb, base, a, w)
    FP.stairs(mb, STAIR_AREA, (0.0, L.T2_STAIR_Y0, L.T1), math.radians(90), L.T2_STAIR_W, 8, (L.T2 - L.T1) / 8,
              L.TREAD, WL, WD)
    newels(mb, (0.0, L.T2_STAIR_Y0, L.T1), math.radians(90), L.T2_STAIR_W)
    ne = L.ENTRY_STAIR_N
    FP.stairs(mb, STAIR_AREA, (0.0, -82.5 - ne * L.TREAD, L.G), math.radians(90), L.ENTRY_STAIR_W, ne,
              (L.RING - L.G) / ne, L.TREAD, WL, WD)
    newels(mb, (0.0, -82.5 - ne * L.TREAD, L.G), math.radians(90), L.ENTRY_STAIR_W)
    x0 = math.sqrt(82.0 ** 2 - L.MILL_STAIR[1] ** 2) - 0.4
    FP.stairs(mb, STAIR_AREA, (x0 + ne * L.TREAD, L.MILL_STAIR[1], L.G), math.radians(180), 8.0, ne,
              (L.RING - L.G) / ne, L.TREAD, WL, WD)
    mb.finish()
