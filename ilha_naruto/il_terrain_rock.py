# il_terrain_rock - penhascos da Ilha 1 (zona terrain, prefixo TER_): colunas de rocha castanho-dourada ao longo do
# contorno (topo -> prateleira), prateleira em lobulos com tampo de grama, penhasco baixo em 3 faixas (prateleira ->
# mar) com saliencias horizontais, macico do fundo em 3 patamares com os 2 sulcos das cachoeiras e os picos NO/NE.
# Tudo visual: a colisao do chao e da borda vem do il_core. Usado por il_terrain.build().
import math
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box2
import il_layout as L
import fm_parts as FP

TAN = "Cliff_Rock_Tan"
DARK = "Cliff_Rock_Tan_Dark"
TOP = "Cliff_Rock_Tan_Top"
GRASS = "Grass_Konoha"
C = "02_TERRAIN"

# cachoeiras que caem pela borda (o agente de agua): a prateleira abre um sulco e o penhasco baixo fica aberto
# (pontos da borda mais proximos das quedas do blockout: fim do riacho SE, canal oeste sob o summon, drenagem SO)
COVES = [(101.0, -75.0), (-158.0, 76.0), (-88.5, -71.0)]
SPILL = [(101.0, -75.0), (-158.0, 76.0)]      # colunas de cima rebaixadas (a agua passa por cima)
BACK_NOTCH_HW = 6.5                            # meia largura dos sulcos do paredao (x = +-80)
PEAKS = [(-116.0, 197.0, 95.0, 1), (111.0, 196.0, 91.0, -1)]   # x, y, topo, lado (para onde inclina)


# ------------------------------------------------------------------ geometria 2D
def resample_closed(poly, step):
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(round(ln / step)))
        for j in range(k):
            t = j / k
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def walker(pts):
    """polilinha aberta -> (comprimento, at(s) -> (ponto, tangente))"""
    P = [Vector((p[0], p[1], 0.0)) for p in pts]
    segs = []
    acc = 0.0
    for a, b in zip(P, P[1:]):
        ln = (b - a).length
        if ln < 1e-6:
            continue
        segs.append((acc, a, b, ln))
        acc += ln

    def point(s):
        s = min(max(s, 0.0), acc)
        for s0, a, b, ln in segs:
            if s <= s0 + ln + 1e-9:
                return a + (b - a) * ((s - s0) / ln)
        return segs[-1][2].copy()

    def at(s, h=1.5):
        p = point(s)
        t = point(s + h) - point(s - h)
        if t.length < 1e-6:
            t = Vector((1.0, 0.0, 0.0))
        return p, t.normalized()
    return acc, at


def nearest_on(poly, p):
    """ponto mais proximo no contorno fechado + normal para fora (contorno anti-horario)"""
    best = None
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = dx * dx + dy * dy
        t = 0.0 if ll < 1e-9 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / ll))
        q = (a[0] + dx * t, a[1] + dy * t)
        d = math.hypot(p[0] - q[0], p[1] - q[1])
        if best is None or d < best[0]:
            ln = math.sqrt(ll) or 1.0
            best = (d, q, (dy / ln, -dx / ln))
    return best[1], best[2]


def ground(x, y):
    return L.zone_of(x, y)


def rim_runs(step=1.0):
    """contorno da ilha em trechos de nivel constante (nivel do chao 3 studs para dentro da borda)"""
    dense = resample_closed(IL.rim(), step)
    n = len(dense)
    lv = []
    for i in range(n):
        o, p, q = dense[i - 1], dense[i], dense[(i + 1) % n]
        tx, ty = q[0] - o[0], q[1] - o[1]
        ln = math.hypot(tx, ty) or 1.0
        nx, ny = ty / ln, -tx / ln
        lv.append(ground(p[0] - nx * 3.0, p[1] - ny * 3.0))
    start = next(i for i in range(n) if lv[i] != lv[i - 1])
    runs = []
    cur = [dense[start]]
    cl = lv[start]
    for k in range(1, n + 1):
        i = (start + k) % n
        cur.append(dense[i])
        if k == n or lv[i] != cl:
            runs.append((cl, cur))
            cur = [dense[i]]
            cl = lv[i]
    return runs


def shelf_poly():
    """L.SHELF_RIM densificado, com os sulcos das cachoeiras (a prateleira recua ate a borda)"""
    rim = IL.rim()
    pts = resample_closed(IL.ccw(L.SHELF_RIM), 5.0)
    out = []
    for p in pts:
        best = min(COVES, key=lambda c: math.hypot(p[0] - c[0], p[1] - c[1]))
        d = math.hypot(p[0] - best[0], p[1] - best[1])
        if d < 20.0:
            q, nrm = nearest_on(rim, p)
            tgt = (q[0] + nrm[0] * 1.2, q[1] + nrm[1] * 1.2)
            k = 1.0 if d < 11.0 else (20.0 - d) / 9.0
            k = k * k * (3 - 2 * k)
            p = (p[0] + (tgt[0] - p[0]) * k, p[1] + (tgt[1] - p[1]) * k)
        out.append(p)
    return out


def near_cove(x, y, r):
    return any(math.hypot(x - c[0], y - c[1]) < r for c in COVES)


# ------------------------------------------------------------------ uma coluna (pegada orientada na borda)
def _foot(rng, a, b, n=None, ex=None):
    n = n or rng.choice((5, 6, 6, 7))
    a0 = (math.radians(-90.0 - 180.0 / n) % (math.tau / n)) + rng.uniform(-0.1, 0.1)
    return FP._rock_poly(a, b, n, rng, ex=ex or rng.uniform(2.0, 2.7), jit=0.1, a0=a0)


def column(mb, p, t, out, w, depth, z0, z1, rng, m=TAN, lid=True, rings=None, taper=None, tilt=0.03,
           band=True, tongues=0, lean=0.0, n=None, lip=0.55, ex=None):
    """coluna com a FACE para fora da linha (normal (t.y, -t.x)) a 'out' studs alem do ponto p"""
    a, b = w * 0.5 * 1.04, depth * 0.5
    poly = _foot(rng, a, b, n, ex)
    left = Vector((-t.y, t.x, 0.0))
    nout = -left
    cc = p + nout * (out - 0.88 * b)
    wp = FP._to_world(poly, t, left)
    h = z1 - z0
    rings = rings or (1 if h < 12 else (2 if h < 40 else 3))
    taper = taper if taper is not None else rng.uniform(0.9, 0.97)
    lv = None
    if lean:
        lv = (nout.x * lean, nout.y * lean)
    bd = (min(3.0, h * 0.16), TOP) if (band and h > 4.0) else None
    tg = None
    if tongues and lid:
        tg = (tongues, GRASS, (1.0, 3.2), (nout.x, nout.y))
    FP.rock_column(mb, cc, wp, z0, z1, rng, m, taper=taper, rings=rings, jitter=0.1, tilt=tilt, lean=lv,
                   top_m=(GRASS if lid else None), lip=lip, chamfer=(0.0 if lid else min(0.8, h * 0.08)),
                   rim=False, band=bd, tongues=tg, bottom=False)
    return cc, a, b


def _fits(cc, t, a, b, level):
    """a pegada inteira fica em chao >= level? (colunas altas nao podem invadir um nivel mais baixo)"""
    left = Vector((-t.y, t.x, 0.0))
    for u in (-0.8, 0.0, 0.8):
        for v in (-0.6, 0.0, 0.8):
            q = cc + t * (a * u) + left * (b * v)
            if ground(q.x, q.y) < level - 0.01 and _inside_rim(q.x, q.y):
                return False
    return True


_RIM_CACHE = []


def _inside_rim(x, y):
    if not _RIM_CACHE:
        _RIM_CACHE.append(IL.rim())
    import fm_lib
    return fm_lib.point_in_poly(x, y, _RIM_CACHE[0])


# ------------------------------------------------------------------ penhasco de cima (borda da ilha -> prateleira)
def _width(rng, narrow=(5.0, 8.5), wide=(11.0, 18.0), p_wide=0.42):
    return rng.uniform(*wide) if rng.random() < p_wide else rng.uniform(*narrow)


def upper_cliffs(rng):
    """colunas justapostas ao longo da borda: larguras bimodais (paredoes x agulhas), frente desencontrada (frestas
    escuras recuadas), topo com labio de grama rente ao gramado e dentes mais baixos; colunas altas com trinca
    horizontal (patamar) em cota propria"""
    from mathutils import noise
    mb = MB("TER_Cliffs_Upper", C, rng, detail="near")
    z_bot = L.SHELF_Z - 16.0
    ncol = 0
    sd = rng.uniform(0.0, 200.0)

    def _nz(u, k):
        return noise.noise(Vector((u * 0.04 + sd + 17.0 * k, sd * 0.21, 0.4)))
    for level, pts in rim_runs():
        total, at = walker(pts)
        if total < 2.0:
            continue
        tall = level >= L.CLIFF_TOP - 1
        s = 0.0
        while s < total - 0.3:
            w = _width(rng, (5.5, 9.0), (11.0, 19.0)) if not tall else _width(rng, (8.0, 12.0), (15.0, 26.0), 0.5)
            if total - s - w < 4.0:
                w = total - s
            if w < 3.0:
                break
            sc = s + w * 0.5
            p, t = at(sc)
            depth = rng.uniform(6.5, 10.0) if not tall else rng.uniform(9.0, 13.0)
            out = rng.uniform(0.3, 2.2)
            m = TAN if rng.random() > 0.18 else DARK
            recess = rng.random() < 0.14 and w < 10.0
            if recess:
                out, m = rng.uniform(-0.6, 0.2), DARK            # fresta: coluna recuada e escura
            top = level + 0.12
            lid = True
            q = rng.random()
            if q < 0.2:
                top -= rng.uniform(0.8, 2.8)                   # dente mais baixo (a grama cai um degrau)
            elif q < 0.28:
                lid = False
                top = level - rng.uniform(0.25, 0.8)            # crista de rocha nua
            if p.y < -110.0 and abs(p.x) < L.BRIDGE_W / 2 + 2.0:
                top, lid = L.G - 2.8, False                      # por baixo do tabuleiro da ponte de chegada
            elif p.y < -108.0 and abs(p.x) < L.ENTRY_PLAZA[2] + 2.5:
                top, lid = L.G - 0.4, False                      # borda da praca do portao: abaixo do piso dela
            for sx, sy in SPILL:
                if math.hypot(p.x - sx, p.y - sy) < 6.0:
                    top, lid = level - 1.3, False               # sangradouro das cachoeiras da borda
            left = Vector((-t.y, t.x, 0.0))
            a, b = w * 0.52, depth * 0.5
            cc = p - left * (out - 0.88 * b)
            k = 0
            while not _fits(cc, t, a, b, top - 0.2) and k < 3:
                depth *= 0.7
                w *= 0.8
                a, b = w * 0.52, depth * 0.5
                cc = p - left * (out - 0.88 * b)
                k += 1
            if not _fits(cc, t, a, b, top - 0.2):
                top = min(top, L.G + 0.12)
            h = top - z_bot
            if tall:
                # paredao norte: 3 patamares coerentes (cotas seguem um ruido ao longo da borda), base saliente
                za = 24.0 + 7.0 * _nz(sc, 1) + rng.uniform(-2.5, 2.5)
                zb_ = 48.0 + 6.0 * _nz(sc, 2) + rng.uniform(-2.5, 2.5)
                oa = out + rng.uniform(1.4, 3.4)
                ob = out + rng.uniform(0.4, 1.8)
                column(mb, p, t, oa, w * rng.uniform(0.96, 1.08), depth, z_bot, za, rng,
                       m=DARK if rng.random() < 0.4 else m, lid=rng.random() < 0.65, taper=0.98, tongues=1)
                column(mb, p, t, ob, w * rng.uniform(0.95, 1.04), depth, za - 0.8, zb_, rng, m=m,
                       lid=rng.random() < 0.5, taper=0.97, tongues=1)
                column(mb, p, t, out, w, depth, zb_ - 0.8, top, rng, m=m, lid=lid, taper=rng.uniform(0.9, 0.96),
                       tongues=rng.randint(0, 2))
                ncol += 3
            elif h > 16.0:
                # trinca horizontal: base saliente (ou recuada) ate uma cota propria, corpo por cima
                zm = z_bot + h * rng.uniform(0.3, 0.62)
                ob = out + rng.uniform(-0.6, 2.0)
                column(mb, p, t, ob, w * rng.uniform(0.94, 1.08), depth, z_bot, zm, rng,
                       m=DARK if rng.random() < 0.45 else m, lid=(ob > out + 0.9 and rng.random() < 0.5),
                       taper=rng.uniform(0.96, 1.02), tongues=1)
                column(mb, p, t, out, w, depth, zm - 0.8, top, rng, m=m, lid=lid, taper=rng.uniform(0.88, 0.96),
                       tongues=rng.randint(0, 2))
                ncol += 2
            else:
                column(mb, p, t, out, w, depth, z_bot, top, rng, m=m, lid=lid, tongues=rng.randint(0, 2))
                ncol += 1
            s += w * rng.uniform(0.8, 0.9) if w < total - s else w
    mb.finish()
    # fresta de chao G entre o terraco T2 (x <= 118) e a borda leste: as colunas cobrem; colisao fecha a fresta
    col_box2("TerrainRock", (118.0, 125.6, L.G - 1.0), (123.0, 149.0, L.T2))
    return ncol


# ------------------------------------------------------------------ prateleira + penhasco baixo (-> mar)
SHELF_TOP = L.SHELF_Z - 14.0          # fundo da prateleira (so aparece nas frestas entre os lobulos)


def shelf_and_lower(rng):
    """prateleira (gramado baixo entre a borda e os lobulos) + colunas dos lobulos do mar ate o topo, com tampo de
    grama em cotas variadas (lobulos em degraus) e 2 faixas de saliencia (cotas ~-38 e ~-78, quebradas por
    colunas inteiras); colunas de baixo afinam para o mar"""
    from mathutils import noise
    sp = shelf_poly()
    sh = MB("TER_Shelf", C, rng, detail="far")
    IL.prism(sh, IL.ccw(sp), L.SEA - 1.0, SHELF_TOP, DARK, GRASS)
    sh.finish()
    mb = MB("TER_Cliffs_Lower", C, rng, detail="far")
    rim = IL.rim()
    closed = list(sp) + [sp[0]]
    total, at = walker(closed)
    seed = rng.uniform(0.0, 300.0)
    ncol = 0
    s = 0.0
    while s < total - 1.0:
        w = _width(rng, (6.0, 9.5), (12.0, 20.0), 0.5)
        if total - s - w < 5.0:
            w = total - s
        sc = s + w * 0.5
        p, t = at(sc, 3.0)
        if near_cove(p.x, p.y, 9.5):
            s += 3.0
            continue
        nzv = noise.noise(Vector((s * 0.03 + seed, seed * 0.37, 0.5)))
        q, _ = nearest_on(rim, (p.x, p.y))
        dr = math.hypot(p.x - q[0], p.y - q[1])
        lvl = ground(q[0] - (p.x - q[0]) * 0.3, q[1] - (p.y - q[1]) * 0.3)
        ztop = L.SHELF_Z + 5.0 * nzv + (10.0 - dr) * 0.7 + rng.uniform(-2.0, 1.5)
        if lvl > L.G + 1.0 and rng.random() < 0.14:
            ztop = min(lvl - rng.uniform(4.0, 10.0), L.SHELF_Z + 30.0)     # mesa alta diante do paredao
        ztop = max(L.SHELF_Z - 11.0, min(ztop, lvl - 2.2))
        if p.y < -112.0 and abs(p.x) < L.BRIDGE_W / 2 + 3.0:
            ztop = min(ztop, L.G - 3.0)                          # abaixo do tabuleiro da ponte de chegada
        depth = max(7.0, dr + rng.uniform(2.0, 5.0))           # o lobulo vai ate debaixo do penhasco de cima
        o0 = rng.uniform(0.0, 1.8)
        m = TAN if rng.random() > 0.22 else DARK
        if rng.random() < 0.12 and w < 10.0:
            o0, m = o0 - 1.4, DARK
        b1 = -38.0 + rng.uniform(-7.0, 7.0)
        b2 = -78.0 + rng.uniform(-8.0, 6.0)
        o1 = o0 + rng.uniform(-0.8, 2.4)
        o2 = o1 + rng.uniform(-1.8, 0.6)
        brk1 = rng.random() > 0.3
        brk2 = rng.random() > 0.3
        zlow = L.SEA - 4.0
        z_a = (b1 - 0.6) if brk1 else ((b2 - 0.6) if brk2 else zlow)
        column(mb, p, t, o0, w, depth, z_a, ztop, rng, m=m, lid=rng.random() < 0.88,
               rings=(1 if ztop - z_a < 45 else 2), taper=rng.uniform(0.92, 0.99), tongues=rng.randint(0, 2))
        ncol += 1
        if brk1:
            z_b = (b2 - 0.6) if brk2 else zlow
            column(mb, p, t, o1, w * rng.uniform(0.92, 1.06), depth, z_b, b1, rng,
                   m=DARK if rng.random() < 0.4 else TAN, lid=(o1 > o0 + 1.0 and rng.random() < 0.45),
                   rings=1, taper=rng.uniform(0.97, 1.04), tilt=0.05)
            ncol += 1
        if brk2:
            column(mb, p, t, o2, w * rng.uniform(0.9, 1.05), depth, zlow, b2, rng,
                   m=DARK if rng.random() < 0.55 else TAN, lid=False, rings=1,
                   taper=rng.uniform(1.05, 1.16), tilt=0.06, n=rng.choice((5, 6)))
            ncol += 1
        s += w * rng.uniform(0.8, 0.9) if w < total - s else w
    mb.finish()
    return ncol


# ------------------------------------------------------------------ macico do fundo (face sul em y 186, 3 patamares)
def _tier_row(mb, rng, x0, x1, yf, yj, z0, ztop_fn, lid_p, wide=(12.0, 18.0), dark_p=0.25):
    x = x0
    t = Vector((1.0, 0.0, 0.0))
    n = 0
    while x < x1 - 0.5:
        w = _width(rng, (5.5, 8.5), wide, 0.45)
        if x1 - x - w < 4.0:
            w = x1 - x
        xc = x + w * 0.5
        if any(abs(xc - fx) < BACK_NOTCH_HW + w * 0.5 + 0.5 for fx, _ in L.BACK_FALLS):
            x += 2.0
            continue
        ztop, lid = ztop_fn(xc, w), rng.random() < lid_p
        if ztop > L.CLIFF_TOP + 1.0:
            lid = False
        p = Vector((xc, yf + rng.uniform(0.0, yj), 0.0))
        recess = rng.random() < 0.15 and w < 9.0
        m = DARK if (recess or rng.random() < dark_p) else TAN
        if recess:
            p.y += 0.8
        # face para -y (a vila): tangente +x -> normal para fora (t.y, -t.x) = (0, -1)
        column(mb, p, t, 0.0, w, rng.uniform(5.5, 7.5), z0, ztop, rng, m=m, lid=lid,
               rings=(2 if ztop - z0 > 14 else 1), taper=rng.uniform(0.9, 0.97), tongues=rng.randint(0, 2))
        n += 1
        x += w * rng.uniform(0.82, 0.92) if w < x1 - x else w
    return n


UPPER_HOUSES_X = (-78.0, -40.0, 0.0, 40.0, 80.0)


def back_massif(rng):
    """paredao do fundo: patamar A (T2 -> ~38), B (-> ~55), C (-> plato 72, crista quebrada), sulcos das 2 quedas
    em x = +-80 e picos NO/NE ate ~95 saindo do penhasco baixo, fora da borda"""
    from mathutils import noise
    mb = MB("TER_Back_Massif", C, rng, detail="near")
    y0 = L.BACK_CLIFF_Y
    xw, xe = -108.0, 102.0
    sd = rng.uniform(0.0, 100.0)

    def nz(x, k):
        return noise.noise(Vector((x * 0.045 + sd + k * 13.0, sd * 0.3, 0.2)))
    n = 0
    n += _tier_row(mb, rng, xw, xe, y0 - 0.35, 0.9, L.T2 - 1.0,
                   lambda x, w: 38.0 + 4.0 * nz(x, 1) + rng.uniform(-2.5, 2.5), 0.5)
    n += _tier_row(mb, rng, xw + 1.5, xe - 1.0, y0 + 1.4, 1.3, 32.0,
                   lambda x, w: 55.0 + 4.0 * nz(x, 2) + rng.uniform(-2.5, 2.5), 0.45)

    def ztop_c(x, w):
        corner = max(0.0, (abs(x) - 90.0) / 14.0)            # longe da casinha de x = +-80 (74..86)
        if corner > 0.0:
            return L.CLIFF_TOP + 2.0 + corner * rng.uniform(4.0, 9.0)        # crista quebrada nos cantos
        q = rng.random()
        if q < 0.14 and w < 9.0 and not any(abs(x - hx) < 9.0 for hx in UPPER_HOUSES_X):
            return L.CLIFF_TOP + rng.uniform(1.5, 3.5)                       # dente de rocha entre as casinhas
        if q < 0.3:
            return L.CLIFF_TOP - rng.uniform(0.8, 2.2)
        return L.CLIFF_TOP + 0.12
    n += _tier_row(mb, rng, xw + 3.0, xe - 2.0, y0 + 2.9, 1.2, 49.0, ztop_c, 0.8)
    # sulcos das 2 cachoeiras (x = +-80): fundo recuado escuro + pilastras de rocha emoldurando
    for fx, fy in L.BACK_FALLS:
        t = Vector((1.0, 0.0, 0.0))
        column(mb, Vector((fx, y0 + 4.6, 0.0)), t, 0.0, BACK_NOTCH_HW * 2.0 + 1.0, 6.0, L.T2 - 1.0,
               L.CLIFF_TOP - 0.8, rng, m=DARK, lid=False, rings=3, taper=0.98, band=False, n=6, ex=3.0)
        for s in (-1, 1):
            px = fx + s * (BACK_NOTCH_HW + 2.6)
            column(mb, Vector((px, y0 - 0.3, 0.0)), t, 0.0, 5.6, 8.0, L.T2 - 1.0, L.CLIFF_TOP + 1.2, rng, m=TAN,
                   lid=True, rings=3, taper=0.93, tongues=1)
            n += 1
        n += 1
    # picos dos cantos NO/NE (emolduram a vila): embasamento largo saindo do penhasco baixo + agulha + ombros
    for px, py, ztop, side in PEAKS:
        c = Vector((px, py, 0.0))
        f = Vector((-px, -py, 0.0)).normalized()          # frente: centro da ilha
        sdv = Vector((-f.y, f.x, 0.0))
        parts = [  # (desloc. lateral, desloc. frente, a, b, base, topo, taper, material, tampo)
            (0.0, -1.0, 14.0, 12.0, -60.0, 64.0, 0.82, DARK, True),
            (side * 1.5, 0.5, 11.5, 10.0, 58.0, ztop, 0.56, TAN, False),
            (side * 10.0, 2.0, 8.0, 7.5, 58.0, ztop - 11.0, 0.62, TAN, False),
            (-side * 8.5, 1.5, 7.5, 7.0, 58.0, L.CLIFF_TOP + 7.0, 0.78, TAN, True),
            (side * 2.0, -9.0, 8.0, 6.5, -20.0, ztop - 26.0, 0.72, DARK, False),
        ]
        for dx, dy, a, b, zb, zt, tp, m, lid in parts:
            cc = c + sdv * dx + f * dy
            poly = FP._rock_poly(a, b, rng.choice((6, 7)), rng, ex=rng.uniform(2.0, 2.6), jit=0.12)
            wp = FP._to_world(poly, sdv, -f)
            h = zt - zb
            lean = tuple((f * rng.uniform(0.5, 1.5) + sdv * (side * rng.uniform(0.5, 2.0))).xy) if zb > 0 else None
            FP.rock_column(mb, cc, wp, zb, zt, rng, m, taper=tp, rings=(3 if h > 50 else 2), jitter=0.12,
                           tilt=0.1, lean=lean, top_m=(GRASS if lid else None), lip=0.8,
                           chamfer=(0.0 if lid else 2.2), rim=False,
                           band=(min(4.0, h * 0.1), TOP), bottom=False)
            n += 1
    mb.finish()
    return n
