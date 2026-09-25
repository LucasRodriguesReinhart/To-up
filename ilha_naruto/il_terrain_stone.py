# il_terrain_stone - alvenaria da Ilha 1 (zona terrain, prefixo TER_): muros de arrimo em fiadas com capeamento,
# guarda-corpos (balaustrada na frente da vila, mureta com capa no anel e nas quedas) e as escadas de pedra.
# Posicoes, vaos e colisoes iguais ao blockout (terrace_guards / stairs_all). Usado por il_terrain.build().
import math
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box, col_box2, col_ramp
import il_layout as L
import fm_parts as FP
from il_col import RADIAL_STAIRS, STAIR_TOP_R

WL = "Stone_Wall_Light"
WD = "Stone_Wall_Dark"
C = "02_TERRAIN"
GUARD_AREA = "TerrainGuard"
STAIR_AREA = "TerrainStairs"
WALL_AREA = "TerrainWall"
# nicho da bica no muro x=108 (contrato: centro (108, 80), boca em L.SPOUT[2], 3 x 3, verga de pedra)
WALL_X = 108.0
NICHE = (L.SPOUT[1] - 1.5, L.SPOUT[1] + 1.5, L.SPOUT[2] - 1.5, L.SPOUT[2] + 1.5)    # y0, y1, z0, z1
# recorte do T2 pela faixa da ponte de saida: a borda diagonal vai de T2_CUT_A (em y 126) a T2_CUT_B (em x 118)
T2_CUT_A = (L.T2_WALL_Y + L.T2_EXIT_CUT, L.T2_WALL_Y)          # (111,15; 126)
T2_CUT_B = (118.0, 118.0 - L.T2_EXIT_CUT)                        # (118; 132,85)
T2_CANAL_Y = 135.3       # a balaustrada em x 118 para no bordo sul do canal NE (a cantaria do canal fecha dali)
NICHE_BACK = WALL_X - 1.05       # face da placa escura do fundo (o muro tem a face em x ~108,15: nicho de ~1,2)


# ------------------------------------------------------------------ regras da critica tecnica (rodada 2)
def bev(size, want=0.12):
    """chanfro permitido: 0 se a menor dimensao < 1,0; senao no maximo 5% da menor dimensao"""
    m = min(size)
    return 0.0 if m < 1.0 else min(want, 0.05 * m)


# ------------------------------------------------------------------ geometria 2D (booleanas de poligonos simples)
def _pip(x, y, poly):
    ins = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            ins = not ins
        j = i
    return ins


def _seg_x(p1, p2, q1, q2):
    rx, ry = p2[0] - p1[0], p2[1] - p1[1]
    sx, sy = q2[0] - q1[0], q2[1] - q1[1]
    den = rx * sy - ry * sx
    if abs(den) < 1e-12:
        return None
    qx, qy = q1[0] - p1[0], q1[1] - p1[1]
    t = (qx * sy - qy * sx) / den
    u = (qx * ry - qy * rx) / den
    if 0.0 < t < 1.0 and 0.0 < u < 1.0:
        return t, u
    return None


def _clean(poly, eps=1e-5):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append(p)
    while len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def poly_bool(A, B, op="diff"):
    """booleana de 2 poligonos SIMPLES (Greiner-Hormann): op 'diff' = A - B, 'inter' = A & B.
    Devolve uma lista de poligonos anti-horarios. B ganha um deslocamento infimo (evita vertice sobre aresta).
    Limite: 'diff' com B inteiro dentro de A (furo) devolve A (nao ha furo em prisma)."""
    A = IL.ccw(_clean(A))
    B = [(p[0] + 1.7e-5, p[1] + 2.3e-5) for p in IL.ccw(_clean(B))]
    na, nb = len(A), len(B)
    ea = [[] for _ in range(na)]
    eb = [[] for _ in range(nb)]
    pts = []
    for i in range(na):
        p1, p2 = A[i], A[(i + 1) % na]
        for j in range(nb):
            r = _seg_x(p1, p2, B[j], B[(j + 1) % nb])
            if r:
                k = len(pts)
                pts.append((p1[0] + (p2[0] - p1[0]) * r[0], p1[1] + (p2[1] - p1[1]) * r[0]))
                ea[i].append((r[0], k))
                eb[j].append((r[1], k))
    if not pts:
        a_in_b = _pip(A[0][0], A[0][1], B)
        b_in_a = _pip(B[0][0], B[0][1], A)
        if op == "diff":
            return [] if a_in_b else [A]
        return [A] if a_in_b else ([B] if b_in_a else [])
    LA, LB = [], []
    posA, posB = {}, {}
    for i in range(na):
        LA.append((A[i], None))
        for _, k in sorted(ea[i]):
            posA[k] = len(LA)
            LA.append((pts[k], k))
    for j in range(nb):
        LB.append((B[j], None))
        for _, k in sorted(eb[j]):
            posB[k] = len(LB)
            LB.append((pts[k], k))
    # entrada/saida de A em B, na ordem de A
    inside = _pip(A[0][0], A[0][1], B)
    entry = {}
    for p, k in LA:
        if k is not None:
            entry[k] = not inside
            inside = not inside
    dirB = -1 if op == "diff" else 1
    want = False if op == "diff" else True
    seen = set()
    out = []
    for start in [k for p, k in LA if k is not None and entry[k] == want]:
        if start in seen:
            continue
        poly = []
        k = start
        onA = True
        guard_n = 0
        while True:
            seen.add(k)
            guard_n += 1
            if guard_n > 4 * (na + nb + len(pts)):
                break
            if onA:
                i = posA[k]
                poly.append(LA[i][0])
                i = (i + 1) % len(LA)
                while LA[i][1] is None:
                    poly.append(LA[i][0])
                    i = (i + 1) % len(LA)
                k = LA[i][1]
            else:
                i = posB[k]
                poly.append(LB[i][0])
                i = (i + dirB) % len(LB)
                while LB[i][1] is None:
                    poly.append(LB[i][0])
                    i = (i + dirB) % len(LB)
                k = LB[i][1]
            onA = not onA
            if k == start:
                break
        poly = _clean(poly)
        if len(poly) >= 3 and abs(IL.area(poly)) > 0.05:
            out.append(IL.ccw(poly))
    return out


def poly_bool_many(polys, B, op="diff"):
    out = []
    for p in polys:
        out += poly_bool(p, B, op)
    return out


def offset_poly(poly, d):
    """desloca um poligono simples d para DENTRO (d < 0: para fora); vertices em esquadria (miter limitado)"""
    P = IL.ccw(_clean(poly))
    n = len(P)
    out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        e1 = (b[0] - a[0], b[1] - a[1])
        e2 = (c[0] - b[0], c[1] - b[1])
        l1 = math.hypot(*e1) or 1.0
        l2 = math.hypot(*e2) or 1.0
        n1 = (-e1[1] / l1, e1[0] / l1)
        n2 = (-e2[1] / l2, e2[0] / l2)
        k = max(0.25, 1.0 + n1[0] * n2[0] + n1[1] * n2[1])
        out.append((b[0] + (n1[0] + n2[0]) * d / k, b[1] + (n1[1] + n2[1]) * d / k))
    return out


def resample_poly(pts, step, closed=True):
    """pontos a cada ~step ao longo de uma polilinha (fechada ou aberta)"""
    P = list(pts) + ([pts[0]] if closed else [])
    out = []
    for a, b in zip(P, P[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(round(ln / step)))
        for j in range(k):
            t = j / k
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    if not closed:
        out.append(P[-1])
    return out


def hexa(mb, bot, top, m, bevel=0.0):
    """solido de 8 vertices (bot/top: 4 pontos 3D cada, anti-horario visto de cima)"""
    vs = [mb.bm.verts.new(Vector(p)) for p in list(bot) + list(top)]
    for f in ((3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        try:
            mb.bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    mb._post(vs, m, None, bevel, 1)


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
def masonry(mb, path, face_side, z0, z1, rng, thick=1.4, course=1.8, blk=(3.3, 5.4), cap_h=0.55, cap_over=0.3,
            cap_raise=0.14, cap_m=WD, dark_p=0.1, gap=0.17, cap=True, holes=()):
    """face do muro na linha do caminho, voltada para a esquerda (face_side=+1) ou direita (-1) do sentido;
    o corpo fica do outro lado (dentro do terraco). Fiadas regulares, juntas desencontradas, fiada de base
    escura, blocos saindo 0,12..0,2 da face (sombra entre as pedras; >= 0,1 da face do chao que fica na linha:
    sem z-fighting), capeamento em lajes longas 0,14 acima do piso de cima.
    holes: [(s0, s1, z0, z1)] vaos na alvenaria (nicho da bica, verga...): os blocos sao recortados em volta."""
    ln, f = path
    if ln < 0.5:
        return 0
    # sem capa: a ultima fiada termina cap_raise acima do piso de cima (a junta de 0,17 nao pode baixar o topo)
    ztop_c = z1 + cap_raise - cap_h if cap else z1 + cap_raise + gap * 0.4 + 0.03
    H = ztop_c - z0
    nc = max(1, int(round(H / course)))
    ch = H / nc
    nb = 0

    def pieces(sa, sb, za, zb):
        """recorta o bloco [sa,sb]x[za,zb] pelos vaos: devolve os pedacos (s0, s1, z0, z1)"""
        out = [(sa, sb, za, zb)]
        for hs0, hs1, hz0, hz1 in holes:
            nxt = []
            for a, b, c0, c1 in out:
                if b <= hs0 or a >= hs1 or c1 <= hz0 or c0 >= hz1:
                    nxt.append((a, b, c0, c1))
                    continue
                if a < hs0:
                    nxt.append((a, hs0, c0, c1))
                if b > hs1:
                    nxt.append((hs1, b, c0, c1))
                m0, m1 = max(a, hs0), min(b, hs1)
                if c0 < hz0:
                    nxt.append((m0, m1, c0, hz0))
                if c1 > hz1:
                    nxt.append((m0, m1, hz1, c1))
            out = nxt
        return [q for q in out if q[1] - q[0] >= 0.5 and q[3] - q[2] >= 0.35]
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
            out = rng.uniform(0.12, 0.2)
            m = WD if (k == 0 and nc > 1) or rng.random() < dark_p else WL
            hh = ch - gap * 0.8 + rng.uniform(-0.04, 0.02)
            rz = rng.uniform(-0.012, 0.012)
            for pa, pb, qa, qb in pieces(sa, sb, za + ch * 0.5 - hh * 0.5, za + ch * 0.5 + hh * 0.5):
                p, t = f((pa + pb) * 0.5)
                left = Vector((-t.y, t.x, 0.0)) * face_side
                c = p - left * (thick * 0.5 - out)
                gs = gap if (pa, pb) == (sa, sb) else gap * 0.5
                mb.box((pb - pa - gs, thick, qb - qa), (c.x, c.y, (qa + qb) * 0.5),
                       (0, 0, math.atan2(t.y, t.x) + rz), m, 0.0)
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
def guard(mb, pts, z, kind="bal", area=GUARD_AREA, posts_every=1, step=None, col_w=1.2, col_off=0.0):
    """kind 'bal' = balaustrada (soco, balaustres, corrimao, pilaretes com capa); 'wall' = mureta macica com capa.
    Colisao: 1 caixa (L, col_w, 4) por trecho da polilinha (igual a il_col.guard / fm_parts.stone_parapet), deslocada
    col_off para a esquerda do sentido. step: vaos de ate 'step' com pilaretes intermediarios (so visual).
    Soco afundado 0,3 no piso (sem aresta rente ao gramado)."""
    P = [Vector((p[0], p[1], z)) for p in pts]
    n = len(P)
    for i, (a0, b0) in enumerate(zip(P, P[1:])):
        d0 = b0 - a0
        ln0 = d0.length
        if ln0 < 0.2:
            continue
        t0 = d0 / ln0
        ang = math.atan2(t0.y, t0.x)
        lf = Vector((-t0.y, t0.x, 0.0))
        cc = (a0 + b0) * 0.5 + lf * col_off
        col_box(area, (ln0, col_w, 4.0), (cc.x, cc.y, z + 2.0), (0, 0, ang))
        k = max(1, int(math.ceil(ln0 / step - 1e-6))) if step else 1
        for j in range(k):
            a = a0 + d0 * (j / k)
            b = a0 + d0 * ((j + 1) / k)
            ln = ln0 / k
            c = (a + b) * 0.5
            mb.box((ln + 0.05, 1.2, 0.8), (c.x, c.y, z + 0.1), (0, 0, ang), WD, 0.0)
            if kind == "bal":
                mb.box((ln + 0.05, 1.05, 0.42), (c.x, c.y, z + 2.02), (0, 0, ang), WL, 0.0)
                clear = ln - 1.4
                nbal = max(1, int(clear / 1.25))
                for q_ in range(nbal):
                    q = a + t0 * (0.7 + clear * (q_ + 0.5) / nbal)
                    mb.box((0.46, 0.46, 1.34), (q.x, q.y, z + 1.14), (0, 0, ang + math.pi / 4), WL, 0.0)
            else:
                mb.box((ln + 0.05, 0.95, 1.35), (c.x, c.y, z + 1.17), (0, 0, ang), WL, 0.0)
                mb.box((ln + 0.12, 1.35, 0.36), (c.x, c.y, z + 2.02), (0, 0, ang), WD, 0.0)
            last = (i == n - 2 and j == k - 1)
            for kk, q in enumerate([a, b] if last else [a]):
                if kind != "bal" and (i % posts_every) and kk == 0 and j == 0:
                    continue
                mb.box((1.3, 1.3, 2.45), (q.x, q.y, z + 1.22), (0, 0, ang), WL, bev((1.3, 1.3, 2.45)))
                mb.box((1.6, 1.6, 0.34), (q.x, q.y, z + 2.6), (0, 0, ang), WD, 0.0)


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


def exit_band_y(x):
    """trecho em y da faixa da ponte de saida (largura EXIT_W, sem folga) na vertical x"""
    ux, uy = L.exit_dir()
    sx, sy = L.EXIT_START
    yc = sy + (x - sx) * uy / ux
    hw = (L.EXIT_W / 2) / ux
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


def pilasters(mb, path, face_side, z0, z1, every=15.0, w=2.4, out=0.9, area="TerrainWall", skip=()):
    """contrafortes nos muros altos e compridos: cunhais em blocos alternados (claro/escuro) + capa que emenda no
    capeamento do muro; colisao propria (saem da face do muro para o lado caminhavel).
    skip: trechos (s0, s1) do caminho sem contraforte (nicho, escada encostada, leito do riacho)"""
    ln, f = path
    n = max(1, int(ln // every))
    for k in range(1, n + 1):
        s = ln * k / (n + 1)
        if any(s0 - w < s < s1 + w for s0, s1 in skip):
            continue
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
        mb.box((w + 0.7, out + 0.75, 0.62), (cc.x, cc.y, z1 + 0.14 - 0.31), (0, 0, yaw), WD, 0.0)
        col_box(area, (w + 0.4, out + 0.3, z1 - z0 + 0.6), (c.x, c.y, (z0 + z1) * 0.5 + 0.3), (0, 0, yaw))


def quoin(mb, corner, yaw, z0, z1, rng, s=1.8):
    """cunhal de quina (so visual): blocos alternados na quina convexa entre 2 muros, centro 0,55 para DENTRO na
    bissetriz (yaw + 90 graus aponta para dentro do terraco): sai ~0,7 das 2 faces"""
    x = corner[0] + math.cos(yaw + math.pi / 2) * 0.55
    y = corner[1] + math.sin(yaw + math.pi / 2) * 0.55
    nb = max(2, int(round((z1 - z0) / 1.8)))
    hb = (z1 - 0.55 - z0) / nb
    for i in range(nb):
        ss = s + (0.3 if i % 2 else 0.0)
        mb.box((ss, ss, hb - 0.12), (x, y, z0 + hb * (i + 0.5)), (0, 0, yaw), WD if i % 2 else WL, 0.0)


def pier(mb, x, y, z0, z1, yaw, s=3.0, area="TerrainWall"):
    """pilar de canto/arremate onde o muro morre na borda do penhasco ou encontra outro muro"""
    nb = max(2, int(round((z1 - z0) / 2.2)))
    hb = (z1 - 0.6 - z0) / nb
    for i in range(nb):
        ss = s + (0.3 if i % 2 else 0.0)
        mb.box((ss, ss, hb - 0.12), (x, y, z0 + hb * (i + 0.5)), (0, 0, yaw), WD if i % 2 else WL, 0.0)
    mb.box((s + 0.8, s + 0.8, 0.66), (x, y, z1 + 0.14 - 0.33), (0, 0, yaw), WD, 0.0)
    col_box(area, (s + 0.3, s + 0.3, z1 - z0 + 0.8), (x, y, (z0 + z1) * 0.5 + 0.4), (0, 0, yaw))


def bed_at_wall():
    """trecho em y onde o leito do riacho do vale encosta no muro x = 108 (None se nao encosta)"""
    import il_col
    bed = il_col.stream_bed_poly()
    ys = [y * 0.25 for y in range(200, 440) if _pip(WALL_X + 0.3, y * 0.25, bed)]
    return (min(ys), max(ys)) if ys else None


def bed_skip(ya):
    ys = bed_at_wall()
    return [(ys[0] - ya - 1.0, ys[1] - ya + 1.0)] if ys else []


def niche(mb):
    """nicho da bica no muro x = 108: placa escura no fundo, verga de pedra saliente e soleira (a agua poe a
    carranca e a lamina)"""
    ny0, ny1, nz0, nz1 = NICHE
    yc = (ny0 + ny1) * 0.5
    mb.box((0.3, ny1 - ny0 + 0.4, nz1 - nz0 + 0.4), (NICHE_BACK - 0.15, yc, (nz0 + nz1) * 0.5), (0, 0, 0), WD, 0.0)
    # verga: 0,25 alem da linha do muro (os blocos saem 0,12..0,2), com as pontas apoiadas no muro
    mb.box((1.65, ny1 - ny0 + 1.6, 0.9), (WALL_X + 0.25 - 0.825, yc, nz1 + 0.45), (0, 0, 0), WD, 0.0)
    mb.box((1.7, ny1 - ny0 + 0.5, 0.45), (WALL_X + 0.32 - 0.85, yc, nz0 - 0.225), (0, 0, 0), WL, 0.0)


# ------------------------------------------------------------------ muros de arrimo
def walls(rng):
    mb = MB("TER_Retaining_Walls", C, rng, detail="near")
    n = 0
    # muro interno do fosso (r 60): fosso -> anel, capa saliente (meio-fio da borda do fosso)
    n += masonry(mb, path_arc(L.PIT_R, 0.0, 360.0), +1, L.PIT - 0.4, L.RING, rng, thick=1.4, course=2.3,
                 blk=(3.9, 6.0), cap_h=0.6, cap_over=0.35, cap_raise=0.14, cap_m=WL, dark_p=0.12)
    # muro externo do anel (r 82 -> G), fora do setor do T1
    a0, a1 = L.T1_WALL_A
    n += masonry(mb, path_arc(L.RING_R1, a1, 360.0 + a0), -1, L.G - 0.5, L.RING, rng, thick=1.4, course=2.1,
                 blk=(3.6, 5.8), cap_raise=0.14)
    # muro T1 em arco (r 88), entre os entalhes das escadas
    for s0, s1 in t1_arc_spans():
        n += masonry(mb, path_arc(L.T1_WALL_R, s0, s1), +1, L.RING - 0.3, L.T1, rng, course=1.95)
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
        n += masonry(mb, path_line(pa, pb), fs, L.G - 0.5, L.RING, rng, course=1.5)
        n += masonry(mb, path_line(pb, pc), fs, L.G - 0.5, L.T1, rng, course=1.7)
        sk = [(VS_S0 - L.T1_WALL_R - 2.0, VS_S1 + VS_LAND - L.T1_WALL_R + 1.0)] if ang == a0 else []
        pilasters(mb, path_line(pb, pc), fs, L.G - 0.5, L.T1, every=14.0, skip=sk)
    # face x = 108 (T1 -> vale leste)
    y26 = 108.0 * math.tan(math.radians(a0))
    # a ponte de saida (tabuleiro no T1) cruza este muro: por baixo dela o capeamento fica dentro do tabuleiro
    yb0, yb1 = bridge_span_x(108.0)
    ny0, ny1, nz0, nz1 = NICHE
    for ya, yb, under in ((y26 - 0.7, yb0, False), (yb0, yb1, True), (yb1, L.T2_WALL_Y, False)):
        pth = path_line((WALL_X, ya), (WALL_X, yb))
        holes = ()
        if ya < ny0 < yb:
            # nicho da bica (contrato): vao 3 x 3, verga por cima, soleira saliente por baixo
            holes = ((ny0 - ya, ny1 - ya, nz0, nz1), (ny0 - 0.8 - ya, ny1 + 0.8 - ya, nz1, nz1 + 0.9),
                     (ny0 - 0.3 - ya, ny1 + 0.3 - ya, nz0 - 0.45, nz0))
        n += masonry(mb, pth, -1, L.G - 0.5, L.T1, rng, course=1.7, cap_raise=(-0.4 if under else 0.14),
                     holes=holes)
        if not under and yb - ya > 20.0:
            pilasters(mb, pth, -1, L.G - 0.5, L.T1, every=15.0, skip=[(ny0 - ya - 4.0, ny1 - ya + 4.0)] + bed_skip(ya))
    niche(mb)
    # sapata do muro onde o leito do riacho encosta nele (o fundo do leito fica 2,8 abaixo do gramado)
    ys = bed_at_wall()
    if ys:
        n += masonry(mb, path_line((WALL_X, ys[0] - 0.6), (WALL_X, ys[1] + 0.6)), -1, L.STREAM_BED - 0.3,
                     L.G - 0.5, rng, course=1.3, blk=(2.2, 3.6), cap=False, cap_raise=0.0, dark_p=0.55)
    # muro T2 (y 126): T1 -> T2 com o vao da escada central; x 108..118 desce ate o vale (G)
    hw = L.T2_STAIR_W / 2 + 0.6
    xw = -147.6
    n += masonry(mb, path_line((xw, L.T2_WALL_Y), (-hw, L.T2_WALL_Y)), -1, L.T1 - 0.3, L.T2, rng, course=1.95)
    n += masonry(mb, path_line((hw, L.T2_WALL_Y), (108.0, L.T2_WALL_Y)), -1, L.T1 - 0.3, L.T2, rng, course=1.95)
    # T2 recortado da faixa da ponte de saida (x - y <= T2_EXIT_CUT): muro G -> T2 de x 108 ate o recorte e na
    # DIAGONAL do recorte ate x 118; quina com cunhal; colisao propria da face (o chao do T2 e em faixas por dentro)
    xc = T2_CUT_A[0]
    n += masonry(mb, path_line((WALL_X, L.T2_WALL_Y), (xc, L.T2_WALL_Y)), -1, L.G - 0.5, L.T2, rng, course=1.8)
    n += masonry(mb, path_line(T2_CUT_A, T2_CUT_B), -1, L.G - 0.5, L.T2, rng, course=1.8)
    quoin(mb, T2_CUT_A, math.radians(22.5), L.G - 0.5, L.T2, rng)
    col_box2(WALL_AREA, (WALL_X, L.T2_WALL_Y - 0.25, L.G - 1.0), (xc, L.T2_WALL_Y + 2.6, L.T2))
    dx, dy = T2_CUT_B[0] - T2_CUT_A[0], T2_CUT_B[1] - T2_CUT_A[1]
    ld = math.hypot(dx, dy)
    ux, uy = dx / ld, dy / ld
    cx, cy = (T2_CUT_A[0] + T2_CUT_B[0]) * 0.5 - uy * 1.05, (T2_CUT_A[1] + T2_CUT_B[1]) * 0.5 + ux * 1.05
    col_box(WALL_AREA, (ld + 1.0, 2.6, L.T2 - L.G + 1.0), (cx, cy, (L.T2 + L.G - 1.0) * 0.5),
            (0, 0, math.atan2(dy, dx)))
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
              [(270.0, L.ENTRY_STAIR_W / 2 + 0.8), (360.0 + math.degrees(math.atan2(L.MILL_STAIR[1], 82.0)), 5.2)]
              + [(ang, w / 2 + SIDE_GAP_HW) for ang, w in L.SIDE_STAIRS],
              step=4.0, posts_every=2)
    # topo do muro T1 (arco r 88), vaos nas escadas radiais: balaustrada (frente da vila)
    arc_guard(mb, L.T1_WALL_R + 0.8, a0, a1, L.T1, "bal", [(ang, w / 2 + 0.8) for _, ang, w in RADIAL_STAIRS],
              step=5.0)
    # topo do muro T2 (y 126), vao da escada central
    hw = L.T2_STAIR_W / 2 + 0.8
    guard(mb, [(-L.T2_WALL_X[1] - 36, L.T2_WALL_Y + 0.8), (-hw, L.T2_WALL_Y + 0.8)], L.T2, "bal", step=7.5)
    # T2 sul -> quina do recorte -> DIAGONAL (fecha a fenda entre o T2 e a ponte de saida) -> x 118 ate o canal NE.
    # a linha da balaustrada fica 0,3 para dentro da borda diagonal; a colisao (2,2) passa 0,8 para fora dela
    k = 0.3 * math.sqrt(2.0)
    cut_in = L.T2_EXIT_CUT - k                              # x - y da linha da balaustrada
    y_s = L.T2_WALL_Y + 0.8
    p_a = (y_s + cut_in, y_s)
    p_b = (118.0 - 0.3, 118.0 - 0.3 - cut_in)
    p_c = (118.0 - 0.3, T2_CANAL_Y)
    guard(mb, [(hw, y_s), p_a], L.T2, "bal", step=7.5)
    guard(mb, [p_a, p_b, p_c], L.T2, "bal", step=5.0, col_w=2.2, col_off=-0.5)
    # T1 -> vale leste (x = 107,2): vao exato da faixa da ponte de saida (y 94,5 .. 119,9)
    yb0, yb1 = exit_band_y(107.2)
    guard(mb, [(107.2, 52.0), (107.2, yb0)], L.T1, "wall", step=6.0)
    guard(mb, [(107.2, yb1), (107.2, L.T2_WALL_Y)], L.T1, "wall")
    for ang in L.T1_WALL_A:
        a = math.radians(ang)
        p0 = (L.T1_WALL_R * math.cos(a), L.T1_WALL_R * math.sin(a))
        p1 = ((L.T1_WALL_R + 70) * math.cos(a), (L.T1_WALL_R + 70) * math.sin(a))
        if ang < 90:
            # linha 0,5 para dentro do T1 (a mureta fica sobre a capa do muro); vao do patamar da escada do vale
            s_end = (107.2 + 0.5 * math.sin(a)) / math.cos(a)
            guard(mb, [vs_pt(L.T1_WALL_R + 0.4, 0.5), vs_pt(VS_OPEN[0], 0.5)], L.T1, "wall", step=6.0)
            guard(mb, [vs_pt(VS_OPEN[1], 0.5), vs_pt(s_end, 0.5)], L.T1, "wall")
            continue
        r_end = ray_rim(ang) - 1.0          # no blockout passava da borda (ficava no ar): para na borda
        p1 = (r_end * math.cos(a), r_end * math.sin(a))
        guard(mb, [p0, p1], L.T1, "wall", step=6.0)
    mb.finish()


# ------------------------------------------------------------------ escadas (mesmas posicoes do stairs_all + novas)
def stair_flight(mb, area, base, ang, width, n, rise, tread, sides=(-1, 1), col=True):
    """escada com a MESMA geometria e colisao do fm_parts.stairs (degraus macicos, banzos em blocos, rampa pelo meio
    dos pisos, meia pisada final, banzo = rampa paralela 4 acima), com os chanfros da regra da rodada 2.
    sides: lados com banzo (+1 = esquerda do sentido de subida)"""
    F = FP.Frame(base[0], base[1], base[2], ang)
    sink = 0.3                                   # blocos afundados 0,3 no piso de baixo (sem aresta rente)
    for i in range(n):
        size = (tread + 0.15, width, rise * (i + 1) + sink)
        mb.box(size, F.p(tread * i + tread / 2, 0, (rise * (i + 1) - sink) / 2), F.r(), WL, bev(size, 0.14))
    for sd in sides:
        for i in range(n):
            h = rise * (i + 1) + 1.2
            size = (tread + 0.05, 1.2, h + sink)
            mb.box(size, F.p(tread * i + tread / 2, sd * (width / 2 + 0.6), (h - sink) / 2), F.r(), WD,
                   bev(size, 0.16))
    if col:
        bot = F.p(-tread / 2, 0, 0)
        top = F.p(tread * n - tread / 2, 0, rise * n)
        col_ramp(area, bot, top, width)
        q = F.p(tread * n - tread / 4 + 0.15, 0, rise * n - 0.5)
        col_box(area, (tread / 2 + 0.3, width, 1.0), (q.x, q.y, q.z), F.r())
        k = rise / tread
        H = 4.0
        T = H + 1.5
        off = k * (tread * k / 2 + H) / (1 + k * k)
        for sd in sides:
            y = sd * (width / 2 + 0.6)
            # a rampa do banzo comeca no pe (no fm_parts ela saia 'off' ~1,7 para fora do 1o degrau, a 3,6 de altura:
            # fechava o corredor entre o pe da escada do moinho e a porta dele); o 1o bloco do banzo tem caixa propria
            xa, xb = 0.0, tread * n - off
            a = F.p(xa, y, (xa + tread / 2) * k + H)
            b = F.p(xb, y, (xb + tread / 2) * k + H)
            col_ramp(area, a, b, 1.2, thick=T)
            q = F.p(tread / 2, y, 0.0)
            col_box(area, (tread + 0.05, 1.2, rise + 1.2 + 0.5), (q.x, q.y, q.z + (rise + 1.2 - 0.5) / 2), F.r())
    return F.p(tread * n, 0, rise * n)


def newels(mb, base, ang, w, sides=(-1, 1)):
    """pilaretes de pedra no pe da escada (os banzos comecam baixos): com colisao"""
    F = FP.Frame(base[0], base[1], base[2], ang)
    for sd in sides:
        q = F.p(-0.35, sd * (w / 2 + 0.6), 0.0)
        mb.box((1.8, 1.8, 0.8), (q.x, q.y, q.z + 0.1), F.r(), WD, 0.0)
        mb.box((1.45, 1.45, 2.6), (q.x, q.y, q.z + 1.8), F.r(), WL, bev((1.45, 1.45, 2.6)))
        mb.box((1.9, 1.9, 0.42), (q.x, q.y, q.z + 3.3), F.r(), WD, 0.0)
        col_box(STAIR_AREA, (1.8, 1.8, 3.6), (q.x, q.y, q.z + 1.8), F.r())


# escadas laterais gramado G -> anel (L.SIDE_STAIRS): radiais, pe em r 92,5, topo em r 84, 5 espelhos de 0,8
SIDE_FOOT_R = 92.5
SIDE_TOP_R = SIDE_FOOT_R - 5 * L.TREAD           # 84,0
SIDE_GAP_HW = 1.2 + 0.65                          # vao do guarda do anel: meia largura + banzo + meio pilarete


def side_stair_pts(ang, r):
    a = math.radians(ang)
    return (r * math.cos(a), r * math.sin(a))


def side_stairs(mb, rng):
    ns = 5
    rise = (L.RING - L.G) / ns
    for ang, w in L.SIDE_STAIRS:
        a = math.radians(ang)
        base = (SIDE_FOOT_R * math.cos(a), SIDE_FOOT_R * math.sin(a), L.G)
        d = a + math.pi
        stair_flight(mb, STAIR_AREA, base, d, w, ns, rise, L.TREAD)
        newels(mb, base, d, w)
        # patamar macico por cima do muro do anel (r 84 -> 82,2) + banzos continuando ate o guarda do anel
        F = FP.Frame(base[0], base[1], L.G, d)
        run = ns * L.TREAD
        ln = SIDE_TOP_R - (L.RING_R1 + 0.35) + 0.1      # para antes da capa do muro do anel (sem sobrepor topos)
        size = (ln, w + 2.4, L.RING + 0.14 - (L.G - 0.5))
        c = F.p(run - 0.1 + ln / 2, 0, 0)
        mb.box(size, (c.x, c.y, (L.RING + 0.14 + L.G - 0.5) / 2), F.r(), WL, bev(size, 0.1))
        for sd in (-1, 1):
            q = F.p(run - 0.1 + ln / 2, sd * (w / 2 + 0.6), 0)
            mb.box((ln + 0.1, 1.2, 1.06), (q.x, q.y, L.RING + 0.14 + 0.53), F.r(), WD, bev((ln, 1.2, 1.06)))
            col_box(STAIR_AREA, (ln + 0.3, 1.2, 4.0), (q.x, q.y, L.RING + 2.0), F.r())
        q = F.p(run + 1.0, 0, 0)
        col_box(STAIR_AREA, (2.6, w + 2.4, 1.0), (q.x, q.y, L.RING - 0.5), F.r())


# escada vale leste (G) -> T1 encostada no muro radial de 26 graus pelo lado do vale (L.VALLEY_STAIR): paralela ao
# muro, degraus de 0,08 a 8,08 ao sul da linha do muro, banzo so do lado de fora; patamar no topo com a abertura no
# guarda do muro (entra no T1); liga a porta do moinho a saida
VS_ANG = L.T1_WALL_A[0]
VS_N = L.VALLEY_STAIR["n"]
VS_W = L.VALLEY_STAIR["width"]
VS_RISE = (L.T1 - L.G) / VS_N
VS_TREAD = 1.65
VS_LAT = -(0.08 + VS_W / 2)                  # eixo da escada: lateral (+ = norte) em relacao a linha do muro
VS_S0 = 88.17                               # pe (distancia ao longo do raio de 26 graus): (81, 35)
VS_S1 = VS_S0 + VS_N * VS_TREAD             # topo (100,3; 44,4)
VS_LAND = 8.0                               # comprimento do patamar ao longo do muro
VS_OPEN = (VS_S1 + 0.7, VS_S1 + VS_LAND - 0.6)   # vao no guarda do muro (trecho em s)


def vs_pt(s, lat):
    """ponto a 's' ao longo do raio de 26 graus e 'lat' para a esquerda (norte) dele"""
    a = math.radians(VS_ANG)
    return (s * math.cos(a) - lat * math.sin(a), s * math.sin(a) + lat * math.cos(a))


def valley_stair(mb, rng):
    a = math.radians(VS_ANG)
    bx, by = vs_pt(VS_S0, VS_LAT)
    stair_flight(mb, STAIR_AREA, (bx, by, L.G), a, VS_W, VS_N, VS_RISE, VS_TREAD, sides=(-1,))
    newels(mb, (bx, by, L.G), a, VS_W, sides=(-1,))
    # patamar: faces em alvenaria (sul e leste), lajeado por cima, mureta nas bordas de fora
    lat_o = VS_LAT - VS_W / 2 - 1.2                  # face sul (alinhada com o banzo)
    s0, s1 = VS_S1 - 0.2, VS_S1 + VS_LAND
    n = masonry(mb, path_line(vs_pt(s0, lat_o), vs_pt(s1, lat_o)), -1, L.G - 0.5, L.T1, rng, course=1.7, cap=False,
                cap_raise=-0.45)
    n += masonry(mb, path_line(vs_pt(s1, lat_o), vs_pt(s1, 0.0)), -1, L.G - 0.5, L.T1, rng, course=1.7, cap=False,
                 cap_raise=-0.45)
    # lajeado ate 0,35 antes da linha do muro: a capa do muro (0,3 para fora) fica ao lado, sem sobrepor o topo
    cx, cy = vs_pt((s0 + s1) / 2, (lat_o - 0.35 - 0.35) / 2)
    mb.box((s1 - s0 + 0.2, -lat_o + 0.35 - 0.35, 0.6), (cx, cy, L.T1 + 0.14 - 0.3), (0, 0, a), WL, 0.0)
    lx0, ly0 = vs_pt(VS_S1 + 0.4, lat_o + 0.7)
    lx1, ly1 = vs_pt(s1 - 0.7, lat_o + 0.7)
    lx2, ly2 = vs_pt(s1 - 0.7, -0.4)
    guard(mb, [(lx0, ly0), (lx1, ly1), (lx2, ly2)], L.T1 + 0.14, "wall", step=5.0)
    # colisao: patamar (ate dentro do T1, por cima das faixas recortadas do nucleo) + face do muro ao longo da escada
    ccx, ccy = vs_pt((s0 + s1) / 2, (lat_o + 3.2) / 2)
    col_box(STAIR_AREA, (s1 - s0 + 0.4, 3.2 - lat_o, L.T1 - L.G + 1.0), (ccx, ccy, (L.T1 + L.G - 1.0) / 2),
            (0, 0, a))
    return n


def wall26_cols():
    """face do muro radial de 26 graus do lado do vale: as faixas de colisao do T1 (por dentro, em y) deixam
    recortes de ate 2,7 junto ao raio; a caixa fecha a face (anel -> G ate r 88, T1 -> G ate x 108)"""
    a = math.radians(VS_ANG)
    for s0, s1, zt in ((L.RING_R1 - 1.0, L.T1_WALL_R, L.RING), (L.T1_WALL_R, 108.0 / math.cos(a) - 0.4, L.T1)):
        cx, cy = vs_pt((s0 + s1) / 2, 0.8)
        col_box(WALL_AREA, (s1 - s0, 1.6, zt - L.G + 1.0), (cx, cy, (zt + L.G - 1.0) / 2), (0, 0, a))


def stairs(rng):
    mb = MB("TER_Stairs", C, rng, detail="near")
    n1 = 8
    r1 = (L.T1 - L.RING) / n1
    for key, ang, w in RADIAL_STAIRS:
        a = math.radians(ang)
        base = (82.5 * math.cos(a), 82.5 * math.sin(a), L.RING)
        stair_flight(mb, STAIR_AREA, base, a, w, n1, r1, L.TREAD)
        newels(mb, base, a, w)
    stair_flight(mb, STAIR_AREA, (0.0, L.T2_STAIR_Y0, L.T1), math.radians(90), L.T2_STAIR_W, 8, (L.T2 - L.T1) / 8,
                 L.TREAD)
    newels(mb, (0.0, L.T2_STAIR_Y0, L.T1), math.radians(90), L.T2_STAIR_W)
    ne = L.ENTRY_STAIR_N
    stair_flight(mb, STAIR_AREA, (0.0, -82.5 - ne * L.TREAD, L.G), math.radians(90), L.ENTRY_STAIR_W, ne,
                 (L.RING - L.G) / ne, L.TREAD)
    newels(mb, (0.0, -82.5 - ne * L.TREAD, L.G), math.radians(90), L.ENTRY_STAIR_W)
    x0 = math.sqrt(82.0 ** 2 - L.MILL_STAIR[1] ** 2) - 0.4
    stair_flight(mb, STAIR_AREA, (x0 + ne * L.TREAD, L.MILL_STAIR[1], L.G), math.radians(180), 8.0, ne,
                 (L.RING - L.G) / ne, L.TREAD)
    side_stairs(mb, rng)
    valley_stair(mb, rng)
    wall26_cols()
    mb.finish()
