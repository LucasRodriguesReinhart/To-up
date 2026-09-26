# db_terrain_rock - rocha da Ilha 2 (dono: zona terrain): penhascos da borda (costelas verticais penduradas com
# estratos escuros e tufos verdes), a massa de baixo da ilha flutuante (nucleo afunilado + aneis de costelas que
# descem ate as nuvens), cristas baixas na borda, as 12 mesas/pilares/agulhas da planta e os 8 rochedos do plato.
# Identidade DRAGON BALL: arenito laranja quente, faixas horizontais escuras continuas (estratos) cortadas por
# fraturas verticais; NADA do paredao colunar bege da Ilha 1.
import math, random
from mathutils import Vector, noise
import db_lib as DL
from db_lib import MB, FP
import db_layout as L
import db_col
import db_terrain_field as TF

C = "02_TERRAIN"
ROCK = "Cliff_Rock_DB"
DARK = "Cliff_Rock_DB_Dark"
TOP = "Cliff_Rock_DB_Top"
GRASS = "Grass_DB"
G = L.GROUND

# estratos continuos da ilha (cota central, espessura, amplitude da ondulacao ao longo da borda)
STRATA = [(15.5, 1.5, 1.6), (4.5, 0.8, 1.2), (-9.0, 2.2, 2.4), (-33.0, 2.0, 3.0)]


# ------------------------------------------------------------------ geometria da borda
def rim_pts():
    return DL.rim()


def centroid():
    r = rim_pts()
    return (sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r))


def scaled_rim(s, jit=0.0, rng=None):
    cx, cy = centroid()
    out = []
    for x, y in rim_pts():
        k = s * (1.0 + (rng.uniform(-jit, jit) if rng else 0.0))
        out.append((cx + (x - cx) * k, cy + (y - cy) * k))
    return out


class Walker:
    """polilinha fechada parametrizada pelo comprimento: at(s) -> (ponto, tangente, normal para FORA)"""

    def __init__(self, pts):
        self.p = [Vector((x, y, 0.0)) for x, y in pts]
        self.acc = [0.0]
        n = len(self.p)
        for i in range(n):
            self.acc.append(self.acc[-1] + (self.p[(i + 1) % n] - self.p[i]).length)
        self.total = self.acc[-1]

    def point(self, s):
        s %= self.total
        n = len(self.p)
        lo, hi = 0, n
        while lo < hi - 1:
            mid = (lo + hi) // 2
            if self.acc[mid] <= s:
                lo = mid
            else:
                hi = mid
        a, b = self.p[lo], self.p[(lo + 1) % n]
        ln = self.acc[lo + 1] - self.acc[lo]
        return a + (b - a) * ((s - self.acc[lo]) / ln if ln > 1e-9 else 0.0)

    def at(self, s, h=2.0):
        p = self.point(s)
        t = self.point(s + h) - self.point(s - h)
        t.z = 0.0
        t = t.normalized() if t.length > 1e-9 else Vector((1.0, 0.0, 0.0))
        return p, t, Vector((t.y, -t.x, 0.0))      # contorno anti-horario: fora = direita

    def param(self, x, y):
        """s do ponto da polilinha mais proximo de (x, y)"""
        best = (1e18, 0.0)
        n = len(self.p)
        q = Vector((x, y, 0.0))
        for i in range(n):
            a, b = self.p[i], self.p[(i + 1) % n]
            d = b - a
            l2 = d.length_squared or 1e-9
            t = max(0.0, min(1.0, (q - a).dot(d) / l2))
            dd = (a + d * t - q).length_squared
            if dd < best[0]:
                best = (dd, self.acc[i] + t * math.sqrt(l2))
        return best[1]

    def sdist(self, s1, s2):
        d = abs(s1 - s2) % self.total
        return min(d, self.total - d)


# ------------------------------------------------------------------ o que a borda tem que respeitar
HW_EXIT = L.EXIT_W / 2 + 2.0


def exit_frame(x, y):
    ux, uy = L.exit_dir()
    sx, sy = L.EXIT_START
    return (x - sx) * ux + (y - sy) * uy, -(x - sx) * uy + (y - sy) * ux


def bridge_deck(x, y, pad=0.0):
    """cota da face de baixo do tabuleiro de uma ponte que passa por (x, y), ou None"""
    if abs(x) < L.ENTRY_STAIR_W / 2 + 1.6 + pad and y < L.ENTRY_STAIR_Y1 - 2.0:
        return L.DECK - 2.0
    t, d = exit_frame(x, y)
    if -16.0 <= t <= L.EXIT_BRIDGE_LEN and abs(d) < HW_EXIT + pad:
        return L.EXIT_Z - 2.0
    for k, (a0, a1) in L.SAT_BRIDGES.items():
        dd, tt = L.seg_dist(x, y, a0[0], a0[1], a1[0], a1[1])
        if dd < L.SAT_BRIDGE_W / 2 + 1.5 + pad:
            return L.GROUND - 2.0
        x0, y0, r0 = [(tx, ty, tr) for tx, ty, tr, kk, w in L.TOWER_SITES if kk == k][0]
        if math.hypot(x - x0, y - y0) < r0 + 1.5 + pad:
            return L.GROUND - 3.2
    return None


_WATER = None


def water_cut():
    global _WATER
    if _WATER is None:
        _WATER = [p for k, p in db_col.water_polys() if k == "g"]
    return _WATER


def in_water(x, y, pad=0.0):
    for p in water_cut():
        if L.point_in_poly(x, y, p):
            return True
        if pad > 0 and L.polyline_dist(x, y, list(p) + [p[0]]) < pad:
            return True
    return False


def near_mesa(x, y, k=1.0):
    for mx, my, r, top, kind in L.MESAS:
        if math.hypot(x - mx, y - my) < r * k:
            return True
    return False


_HUBX = None


def hub_ext():
    """contorno da vila estendido ate alem da borda nas cordas do contorno da ilha (o terraco vai ate a crista)"""
    global _HUBX
    if _HUBX is None:
        hp = DL.hub_poly()
        rim = list(rim_pts())
        rim = rim + [rim[0]]
        n = len(hp)
        ext = []
        for i in range(n):
            a, b = hp[i], hp[(i + 1) % n]
            da = L.polyline_dist(a[0], a[1], rim)
            db_ = L.polyline_dist(b[0], b[1], rim)
            if da < 1.0 and db_ < 1.0:
                dx, dy = b[0] - a[0], b[1] - a[1]
                ln = math.hypot(dx, dy)
                nx, ny = dy / ln, -dx / ln
                ext.append([a, b, (b[0] + nx * 14.0, b[1] + ny * 14.0), (a[0] + nx * 14.0, a[1] + ny * 14.0)])
        _HUBX = (hp, ext)
    return _HUBX


def in_hub_ext(x, y):
    hp, ext = hub_ext()
    if L.point_in_poly(x, y, hp):
        return True
    return any(L.point_in_poly(x, y, q) for q in ext)


def level_at(x, y):
    """cota do topo do terreno junto da borda (vila estendida ate a crista)"""
    if in_hub_ext(x, y):
        return L.HUB
    return L.zone_of(x, y)


# ------------------------------------------------------------------ folga do jogador em volta das rochas
# A colisao das mesas e dos rochedos e do db_col (congelada): octogono EXATO de raio r*0,95 (apotema 0,878 r). Toda
# peca de rocha que cruza a faixa do corpo do jogador (piso -1,5 .. piso +8,5) sobre chao ALCANCAVEL tem que caber
# nesse octogono; do lado de fora da ilha (ou colado na borda, atras da guarda de 4,6) a rocha continua livre.
RIM_CL = list(L.ISLAND_RIM) + [L.ISLAND_RIM[0]]
OCT_K = 0.95
BODY_LO, BODY_HI = 1.5, 8.5


def reach_w(x, y):
    """0..1: o jogador encosta em (x, y)? 0 fora da ilha ou junto da borda (guarda invisivel de 4,6), 1 alem dela"""
    if not L.point_in_poly(x, y, L.ISLAND_RIM):
        return 0.0
    d = L.polyline_dist(x, y, RIM_CL)
    return max(0.0, min(1.0, (d - 1.2) / 2.4))


def has_col(x, y, r):
    """a mesma regra do db_col.rocks(): coluna so para as rochas dentro da borda ou encostadas nela"""
    return L.point_in_poly(x, y, L.ISLAND_RIM) or min(
        math.hypot(x - px, y - py) for px, py in L.ISLAND_RIM) <= r + 1.0


class Clear:
    """limite horizontal de uma rocha sobre o chao alcancavel (o octogono da coluna do db_col).
    fit(): encolhe o contorno de uma peca (ao longo do raio da peca) ate 'k' do octogono onde ele cai no chao
    alcancavel; squeeze(): rede de seguranca depois do jitter da coluna (compressao suave e monotona, radial a partir
    do centro da rocha, so do lado alcancavel); free(): a peca inteira fica fora do chao alcancavel ou dentro do
    octogono (pecas satelite: costelas, contrafortes, companheiras)."""

    def __init__(self, x, y, r, col=True):
        self.x, self.y = x, y
        self.a = r * OCT_K * math.cos(math.pi / 8)
        lv = []
        for i in range(24):
            t = i * math.tau / 24
            for k in (0.0, 0.7, 1.4, 2.0):
                px, py = x + r * k * math.cos(t), y + r * k * math.sin(t)
                if reach_w(px, py) > 0.0:
                    lv.append(level_at(px, py))
        self.on = bool(col and lv)
        self.z_lo = (min(lv) if lv else G) - BODY_LO
        self.z_hi = (max(lv) if lv else G) + BODY_HI

    def bound(self, px, py):
        th = math.atan2(py - self.y, px - self.x)
        k = round((th - math.pi / 8) / (math.pi / 4))
        return self.a / math.cos(th - (math.pi / 8 + k * math.pi / 4))

    def hits(self, z0, z1):
        return self.on and z0 < self.z_hi and z1 > self.z_lo

    def inside(self, px, py, k):
        return reach_w(px, py) <= 0.0 or math.hypot(px - self.x, py - self.y) <= self.bound(px, py) * k

    def fit(self, c, poly, k=0.96, grow=1.35):
        """encolhe o que passa de k do octogono e ESTICA (ate grow x) o que ficou bem dentro dele, so no lado
        alcancavel: a face da rocha acompanha a colisao (nem entra-na-rocha, nem parede invisivel larga)"""
        out = []
        for px, py in poly:
            s = 1.0
            while s > 0.2 and not self.inside(c[0] + px * s, c[1] + py * s, k):
                s *= 0.96
            if s == 1.0:
                while s * 1.03 <= grow:
                    wx, wy = c[0] + px * s * 1.03, c[1] + py * s * 1.03
                    if reach_w(wx, wy) <= 0.0 or math.hypot(wx - self.x, wy - self.y) > self.bound(wx, wy) * (k - 0.04):
                        break
                    s *= 1.03
            out.append((px * s, py * s))
        return out

    def squeeze(self, verts, k0=0.9, k1=0.97):
        for v in verts:
            x, y = v.co.x, v.co.y
            w = reach_w(x, y)
            if w <= 0.0:
                continue
            dx, dy = x - self.x, y - self.y
            d = math.hypot(dx, dy)
            b = self.bound(x, y)
            lo = k0 * b
            if d <= lo:
                continue
            s = (k1 - k0) * b
            nd = lo + s * (1.0 - math.exp(-(d - lo) / s))
            f = (d + (nd - d) * w) / d
            v.co.x = self.x + dx * f
            v.co.y = self.y + dy * f

    def free(self, cx, cy, rad, z0, z1, k=0.97):
        if not self.hits(z0, z1):
            return True
        for i in range(16):
            t = i * math.tau / 16
            if not self.inside(cx + rad * math.cos(t), cy + rad * math.sin(t), k):
                return False
        return self.inside(cx, cy, k)

    def away(self, cx, cy, rad):
        """a peca inteira fica fora do chao alcancavel (encosta so em rocha que nao foi apertada)"""
        if reach_w(cx, cy) > 0.0:
            return False
        return all(reach_w(cx + rad * math.cos(i * math.tau / 16), cy + rad * math.sin(i * math.tau / 16)) <= 0.0
                   for i in range(16))


def _nv(mb):
    mb.bm.verts.ensure_lookup_table()
    return len(mb.bm.verts)


def _new_verts(mb, n0):
    bm = mb.bm
    bm.verts.ensure_lookup_table()
    return [bm.verts[i] for i in range(n0, len(bm.verts)) if bm.verts[i].is_valid]


# ------------------------------------------------------------------ coluna pendurada (costela de arenito)
def _grp(mb, faces, mat, variant=False):
    TF.assign(mb, faces, mat, variant=variant)


def hang(mb, cc, wp, z_top, z_bot, rng, m=ROCK, tip=0.2, pw=1.9, lean=(0.0, 0.0), lid=False, lid_th=0.5,
         band=2.2, strata=(), mids=(0.4, 0.7), jitter=0.09, top_jit=0.035, dark_from=0.74, tongues=0, tdir=None,
         chamfer=0.35, strata_amp=None, bottom_apex=True):
    """costela de rocha: contorno wp (offsets de cc, anti-horario) no topo z_top, afunila ate a ponta em z_bot.
    strata: [(z0, z1)] faixas escuras (sulco recuado) que cruzam a coluna; dark_from: fracao da altura (a partir
    do topo) onde a rocha passa ao tom escuro da sombra de baixo; lid: tampa de grama (topo em z_top + lid_th)."""
    H = z_top - z_bot
    if H < 1.5:
        return
    n = len(wp)
    fs = {0.0: None}
    band_f = None
    if band and band < H * 0.4:
        band_f = band / H
        fs[band_f] = "band"
    for za, zb in strata:
        if z_bot + 3.0 < za and zb < z_top - band - 1.2:
            fs[(z_top - zb) / H] = "s0"
            fs[(z_top - za) / H] = "s1"
    for f in mids:
        if all(abs(f - g) > 0.06 for g in fs):
            fs[f] = None
    if dark_from < 0.97 and all(abs(dark_from - g) > 0.04 for g in fs):
        fs[dark_from] = "dark"
    fs[0.93] = fs.get(0.93)
    order = sorted(fs)
    lx, ly = lean
    rings = []
    for f in order:
        z = z_top - f * H
        if 0.0 < f < 0.93 and fs[f] is None:
            z += rng.uniform(-0.06, 0.06) * H * 0.3
        sc = 1.0 - (1.0 - tip) * (f ** pw)
        kind = fs[f]
        if kind in ("s0", "s1"):
            sc *= 0.955
        lf = f ** 1.5
        jj = top_jit if f == 0.0 else jitter
        ring = []
        for px, py in wp:
            j = 1.0 + rng.uniform(-jj, jj)
            ring.append(mb.bm.verts.new((cc.x + px * sc * j + lx * lf, cc.y + py * sc * j + ly * lf, z)))
        rings.append((f, kind, ring))
    bm = mb.bm
    by_m = {}
    s_open = False
    for k in range(len(rings) - 1):
        f0, k0, r0 = rings[k]
        f1, k1, r1 = rings[k + 1]
        if k0 == "s0":
            s_open = True
        if k0 == "s1":
            s_open = False
        if band_f is not None and f1 <= band_f + 1e-9:
            mm = TOP
        elif s_open:
            mm = DARK
        elif f0 >= dark_from - 1e-6:
            mm = DARK
        else:
            mm = m
        for i in range(n):
            j = (i + 1) % n
            by_m.setdefault(mm, []).append(bm.faces.new((r1[i], r1[j], r0[j], r0[i])))
    # ponta
    fl, kl, rl = rings[-1]
    cx = sum(v.co.x for v in rl) / n
    cy = sum(v.co.y for v in rl) / n
    if bottom_apex:
        ap = bm.verts.new((cx + lx * 0.15, cy + ly * 0.15, z_bot))
        for i in range(n):
            j = (i + 1) % n
            by_m.setdefault(DARK, []).append(bm.faces.new((rl[j], rl[i], ap)))
    else:
        by_m.setdefault(DARK, []).append(bm.faces.new(list(reversed(rl))))
    # topo
    top = rings[0][2]
    tx = sum(v.co.x for v in top) / n
    ty = sum(v.co.y for v in top) / n
    rad = max(0.4, sum(math.hypot(v.co.x - tx, v.co.y - ty) for v in top) / n)

    def ring_from(src, s, dz):
        return [bm.verts.new((tx + (v.co.x - tx) * s, ty + (v.co.y - ty) * s, v.co.z + dz)) for v in src]
    if lid:
        ov = 1.0 + min(0.1, max(0.04, 0.4 / rad))
        ch = min(0.25, 0.5 / rad)
        ra = ring_from(top, ov, 0.0)
        rb = ring_from(top, ov, lid_th * 0.55)
        rc = ring_from(top, ov * (1.0 - ch), lid_th)
        gf = []
        for r0, r1 in ((top, ra), (ra, rb), (rb, rc)):
            for i in range(n):
                j = (i + 1) % n
                gf.append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
        gf.append(bm.faces.new(rc))
        by_m.setdefault(GRASS, []).extend(gf)
        if tongues:
            FP._tongues(mb, rings[1][2], top, (tx, ty), (tongues, GRASS, (1.0, 3.2), tdir), rng)
    else:
        ch = min(0.3, chamfer / rad)
        rc = ring_from(top, 1.0 - ch, chamfer)
        tf = []
        for i in range(n):
            j = (i + 1) % n
            tf.append(bm.faces.new((top[i], top[j], rc[j], rc[i])))
        tf.append(bm.faces.new(rc))
        by_m.setdefault(TOP, []).extend(tf)
    for mm, fl_ in by_m.items():
        _grp(mb, fl_, mm, variant=(mm in (ROCK, GRASS)))


def strata_at(s, total, z_top, z_bot, seed=0.0):
    out = []
    for k, (zc, th, amp) in enumerate(STRATA):
        u = s / total * 6.0
        nz = noise.noise(Vector((u + seed + k * 3.1, 0.37 * k, 0.5)))
        gate = noise.noise(Vector((u * 0.7 + seed * 0.3 + k * 5.7, 1.9, 0.1)))
        if (k == 1 and gate < 0.05) or (k != 1 and gate < -0.45):
            continue                     # a faixa some em trechos da borda (camadas que se afinam)
        z = zc + amp * nz * 1.6
        th = th * (1.0 + 0.5 * gate)
        if z_bot + 3.0 < z - th / 2 and z + th / 2 < z_top - 3.0:
            out.append((z - th / 2, z + th / 2))
    return out


def foot(rng, w, d, n=6, ex=None, face_out=True):
    """contorno de coluna em coords locais (x ao longo da borda, y para DENTRO): face plana para fora"""
    a0 = (math.radians(-90.0 - 180.0 / n) % (math.tau / n)) + rng.uniform(-0.1, 0.1)
    return FP._rock_poly(w * 0.5, d * 0.5, n, rng, ex=ex or rng.uniform(2.0, 2.8), jit=0.1, a0=a0)


def to_world(poly, t, inward):
    return [(t.x * px + inward.x * py, t.y * px + inward.y * py) for px, py in poly]


# ------------------------------------------------------------------ penhasco da borda (A1) + patamares (A2)
# O penhasco e feito de MASSAS: 3-5 costelas fundidas (larguras de 4,8 a 12, ~2,5x) com topo comum em degraus leves
# (sempre ABAIXO do piso: o terreno cobre a parte de dentro e nada fica coplanar com ele), no maximo UMA tampa de grama
# por massa (<= 1/3 das costelas) e uma fenda escura entre massas. Nos dois setores da frente (queda SW -> escadaria
# -> queda SE) corre um PATAMAR continuo em ~G-8 (estrato saliente com topo de grama e linguetas): o paredao le como
# camadas horizontais, nao como palicada de colunas.
LEDGE_Z = G - 8.0
TOP_STEPS = (0.08, 0.46, 0.84)          # degraus do topo de uma massa (abaixo do nivel do piso)


def front_sectors(W):
    """trechos (s0, s1) da borda da frente: recorte da escadaria (leste) -> queda SE e queda SW -> recorte (oeste)"""
    NX = L.ENTRY_STAIR_W / 2 + 2.2
    s_w = W.param(-NX - 3.5, -134.0)
    s_e = W.param(NX + 3.5, -134.0)
    s_sw = W.param(*L.FALL_SW)
    s_se = W.param(*L.FALL_SE)
    return [(s_e, s_se - 9.5), (s_sw + 9.5, s_w + W.total)]


def side_sectors(W):
    """os dois flancos (vistos nas cameras laterais): queda SE -> ponte da saida e cacho NO -> queda SW. O patamar
    corre mais alto no leste e mais baixo no oeste (nada de anel uniforme); pontes, plataformas e mesas o interrompem"""
    s_sw = W.param(*L.FALL_SW)
    s_se = W.param(*L.FALL_SE)
    s_ex = W.param(*L.EXIT_START)
    s_nw = W.param(-160.0, 92.0)
    return [(s_se + 9.5, s_ex - 14.0, G - 6.5), (s_nw, s_sw - 9.5, G - 10.5)]


def in_sectors(W, s, sectors):
    for s0, s1 in sectors:
        ss = s % W.total
        for k in (0.0, W.total):
            if s0 <= ss + k <= s1:
                return True
    return False


def cliffs(rng):
    mb = MB("DB_Ter_Cliffs", C, rng, detail="near", floor=-999)
    W = Walker(rim_pts())
    total = W.total
    falls = [W.param(*L.FALL_SW), W.param(*L.FALL_SE)]
    sectors = front_sectors(W)
    ledged = sectors + [(a, b) for a, b, z in side_sectors(W)]
    seed = rng.uniform(0, 50)
    s = rng.uniform(0, 3)
    s_end = s + total
    count = 0
    ledge_next = rng.uniform(8, 20)
    faces = []                     # (s, meia-largura, saliencia da face) das costelas: o patamar da frente as segue
    NX = L.ENTRY_STAIR_W / 2 + 2.2
    while s < s_end:
        wave = noise.noise(Vector((s / total * 7.0 + seed, 2.1, 0.7)))
        wave2 = noise.noise(Vector((s / total * 11.0 + seed, 1.3, 0.2)))
        nrib = rng.randint(3, 5)
        heavy = rng.random() < 0.22                         # massa com um contraforte largo e saliente no meio
        m_out = rng.uniform(0.5, 2.4)
        m_hang = 29.0 + 19.0 * wave2 + 9.0 * wave
        m_blunt = rng.random() < 0.5
        lid_k = rng.randrange(nrib) if rng.random() < 0.8 else None
        shape = rng.choice(("peak", "up", "down"))
        steps = []
        for k in range(nrib):
            u = k / max(1, nrib - 1)
            f = abs(u - 0.5) * 2.0 if shape == "peak" else (1.0 - u if shape == "up" else u)
            steps.append(TOP_STEPS[int(round(f * 2))] + rng.uniform(0.0, 0.05))
        mid = (nrib - 1) / 2.0
        for k in range(nrib):
            buttress = heavy and k == nrib // 2
            if buttress:
                w, D, out = rng.uniform(13.0, 17.0), rng.uniform(10.0, 13.0), m_out + rng.uniform(1.6, 3.2)
            else:
                w, D, out = rng.uniform(4.8, 12.0), rng.uniform(6.0, 9.0), m_out + rng.uniform(-0.5, 0.5)
            wide = w > 8.4
            sc = s + w * 0.5
            p, t, nout = W.at(sc)
            nin = -nout
            dfall = min(W.sdist(sc, f) for f in falls)
            # recorte da escadaria da chegada: a costela com o centro no vao desce para baixo da ponte; as vizinhas
            # (ombreiras) deslizam ao longo da borda ate a face ficar fora do vao
            in_notch = False
            if p.y < -110.0 and abs(p.x) < NX + w * 0.56:
                if abs(p.x) < NX - 1.0:
                    in_notch = True
                elif abs(t.x) > 0.3:
                    p = p + t * ((math.copysign(NX + w * 0.56, p.x) - p.x) / t.x)
            q = p + nin * 2.5
            lvl = level_at(q.x, q.y)
            lid = k == lid_k
            # topo da costela: abaixo do piso (o terreno cobre). No terraco da vila (saia de 1,0; cantos da borda
            # que a grade corta) o topo fica quase liso (<= 0,14 abaixo): a costela tapa o canto rente ao piso
            top = lvl - (steps[k] if lvl < L.HUB - 1.0 else 0.08 + (steps[k] - 0.08) * 0.08)
            z_top = top - (0.5 if lid else 0.35)
            deck = L.DECK - 2.0 if in_notch else None
            for uu in (-0.45, 0.0, 0.45):
                for v in (-out, 0.0, D - out):
                    pp = p + t * (w * uu) + nin * v
                    dk = bridge_deck(pp.x, pp.y, pad=1.0)
                    if dk is not None:
                        deck = dk if deck is None else min(deck, dk)
            if near_mesa(p.x - nout.x * 2, p.y - nout.y * 2, 0.78):
                s += w * rng.uniform(0.6, 0.75)
                continue
            wet = False
            if dfall < 4.6:
                wet = True
            else:
                for uu in (-0.5, 0.0, 0.5):
                    for v in (0.0, 2.0, D - out):
                        pp = p + t * (w * uu) + nin * v
                        if in_water(pp.x, pp.y, pad=0.8):
                            wet = True
            if wet:
                lid = False
                z_top = min(z_top, L.GROUND - 1.9 - 0.35)
                out = -0.9 if dfall < 4.6 else min(out, 0.4)
            elif dfall < 9.0:
                out = min(out, 1.2)
            if deck is not None:
                lid = False
                z_top = min(z_top, deck - 0.3 - 0.35)
                out = min(out, 1.0)
            if buttress and (deck is not None or wet):
                out = min(out, 1.0)
            # costela no nivel de uma prateleira/terraco que encosta num piso MAIS BAIXO alcancavel (bolsao ao lado da
            # prateleira da saida): nao avanca sobre ele - fica rasa, dentro da faixa da guarda da borda
            for uu in (-0.5, -0.25, 0.0, 0.25, 0.5):
                for v in (2.0, (D - out) * 0.5, D - out):
                    pp = p + t * (w * uu) + nin * v
                    if reach_w(pp.x, pp.y) > 0.0 and level_at(pp.x, pp.y) < z_top - 0.2:
                        D = min(D, out + 3.4)
            cc = p + nout * (out - D * 0.5)
            poly = foot(rng, w, D, n=7 if buttress else (6 if wide else 5))
            wp = to_world(poly, t, nin)
            # fundo da massa: profundidade comum (a do meio mais funda), pouca variacao por costela
            hang_d = m_hang * (1.0 + 0.16 * (1.0 - abs(k - mid) / max(1.0, mid))) * rng.uniform(0.9, 1.08)
            if buttress:
                hang_d += rng.uniform(8.0, 16.0)
            z_bot = min(z_top - 12.0, lvl - hang_d)
            lean_k = rng.uniform(1.0, 3.0) * (1.5 if buttress else 1.0)
            blunt = (m_blunt and rng.random() < 0.8) or (not m_blunt and rng.random() < 0.2)
            hang(mb, cc, wp, z_top, z_bot, rng, tip=rng.uniform(0.42, 0.62) if blunt else rng.uniform(0.12, 0.32),
                 pw=rng.uniform(1.2, 1.6) if blunt else rng.uniform(1.5, 2.4),
                 lean=(nin.x * lean_k, nin.y * lean_k), lid=lid,
                 band=rng.uniform(1.4, 3.0) if not lid else rng.uniform(1.0, 1.8),
                 strata=strata_at(sc, total, z_top, z_bot, seed), mids=(0.45,) if not buttress else (0.33, 0.66),
                 tongues=(rng.randint(1, 3) if lid else 0), tdir=(nout.x, nout.y),
                 dark_from=rng.uniform(0.62, 0.82), bottom_apex=not blunt)
            count += 1
            if deck is None and not wet and not in_notch:
                faces.append((sc, w * 0.5, out))
            if blunt and deck is None and not wet and rng.random() < 0.3:
                # lobo de baixo sob o fundo rombudo: silhueta em degrau (massa pesada, nao disco sobre espetos)
                H0 = z_top - z_bot
                cl = cc + nin * lean_k + t * rng.uniform(-w * 0.12, w * 0.12)
                zl = z_bot + min(3.0, H0 * 0.12)
                hang(mb, cl, to_world(foot(rng, w * rng.uniform(0.34, 0.5), D * rng.uniform(0.4, 0.55), n=5), t, nin),
                     zl, zl - rng.uniform(7.0, 16.0), rng, tip=rng.uniform(0.25, 0.5), pw=rng.uniform(1.3, 1.8),
                     lean=(nin.x * 1.5, nin.y * 1.5), lid=False, band=0.0, mids=(0.5,), dark_from=0.0, chamfer=0.4,
                     bottom_apex=rng.random() < 0.5)
                count += 1
            if buttress and deck is None and not wet:
                # lobo de baixo: o contraforte desce em degrau (silhueta escalonada, nada de cortina uniforme)
                H0 = z_top - z_bot
                zl = z_top - H0 * rng.uniform(0.38, 0.5)
                cl = cc - nout * (D * 0.18) + t * rng.uniform(-w * 0.15, w * 0.15)
                hang(mb, cl, to_world(foot(rng, w * rng.uniform(0.5, 0.66), D * 0.7, n=6), t, nin), zl,
                     z_bot - rng.uniform(10.0, 22.0), rng, tip=rng.uniform(0.12, 0.25), pw=rng.uniform(1.6, 2.2),
                     lean=(nin.x * 3.0, nin.y * 3.0), lid=False, band=0.0,
                     strata=strata_at(sc, total, zl, z_bot - 20.0, seed),
                     mids=(0.5,), dark_from=rng.uniform(0.5, 0.7), chamfer=0.6)
                count += 1
            # patamar saliente (A2) so onde nao corre o patamar continuo: costela mais baixa com tufo verde
            if (sc > ledge_next and deck is None and dfall > 11.0 and not in_notch
                    and not in_sectors(W, sc, ledged)):
                ledge_next = sc + rng.uniform(26.0, 46.0)
                w2 = rng.uniform(6.5, 11.0)
                D2 = rng.uniform(4.5, 7.0)
                o2 = out + rng.uniform(2.0, 4.0)
                c2 = p + t * rng.uniform(-2.0, 2.0) + nout * (o2 - D2 * 0.5)
                if bridge_deck(c2.x, c2.y, pad=4.0) is None and not near_mesa(c2.x, c2.y, 1.1):
                    zt2 = lvl - rng.uniform(5.0, 10.0)
                    hang(mb, c2, to_world(foot(rng, w2, D2, n=5), t, nin), zt2 - 0.5, zt2 - rng.uniform(20.0, 34.0),
                         rng, tip=rng.uniform(0.12, 0.25), lean=(nin.x * 2.0, nin.y * 2.0), lid=True, band=1.4,
                         strata=strata_at(sc, total, zt2, zt2 - 30.0, seed), mids=(0.5,),
                         tongues=rng.randint(1, 3), tdir=(nout.x, nout.y))
                    count += 1
            s += w * rng.uniform(0.55, 0.66)
        # entre massas: recuo com fenda escura (fratura vertical que le de longe)
        gap = rng.uniform(1.2, 3.2)
        pf, tf_, nf = W.at(s + gap * 0.5)
        dfall = min(W.sdist(s, f) for f in falls)
        if (dfall > 9.0 and bridge_deck(pf.x, pf.y, pad=2.0) is None and not near_mesa(pf.x, pf.y, 0.9)
                and not (pf.y < -110.0 and abs(pf.x) < NX + 4.0) and rng.random() < 0.6):
            wf = gap + rng.uniform(1.6, 2.6)
            qf = pf - nf * 2.5
            lf = level_at(qf.x, qf.y)
            cf = pf + nf * (-1.3 - 2.0)
            hang(mb, cf, to_world(foot(rng, wf, 4.4, n=5), tf_, -nf), lf - rng.uniform(1.2, 2.5),
                 lf - m_hang * rng.uniform(0.4, 0.65), rng, m=DARK, tip=0.3, lid=False, band=0.0,
                 mids=(0.5,), dark_from=0.0, chamfer=0.3)
            count += 1
        s += gap
    for s0, s1 in sectors:
        count += strata_ledge(mb, rng, W, s0, s1, faces, seed)
    for s0, s1, zl in side_sectors(W):
        count += strata_ledge(mb, rng, W, s0, s1, faces, seed, z0=zl, step=3.0)
    mb.finish()
    return count


def strata_ledge(mb, rng, W, s0, s1, faces, seed, z0=LEDGE_Z, step=2.0):
    """patamar continuo (estrato saliente) de um setor da frente: laje horizontal em ~G-8 com topo de grama, beiral de
    rocha clara, sombra escura por baixo e linguetas de grama. A saliencia acompanha a face das costelas (maior
    saliencia num raio de 3 + 1,2..2,2) e afina nas pontas; interrompe em ponte/mesa."""
    n = max(2, int((s1 - s0) / step))
    rows = []
    for i in range(n + 1):
        s = s0 + (s1 - s0) * i / n
        p, t, nout = W.at(s)
        o = None
        for sc, hw, out in faces:
            if W.sdist(s, sc) < hw + 3.0:
                o = out if o is None else max(o, out)
        if o is None:
            rows.append(None)
            continue
        ends = min(1.0, (s - s0) / 5.0, (s1 - s) / 5.0)
        prot = (1.2 + 1.0 * (0.5 + 0.5 * noise.noise(Vector((s * 0.09 + seed, 3.3, 0.4))))) * max(0.15, ends)
        zt = z0 + 0.7 * noise.noise(Vector((s * 0.03 + seed, 7.7, 0.1)))
        ro = o + prot
        po = p + nout * ro
        if bridge_deck(po.x, po.y, pad=2.5) is not None or near_mesa(po.x, po.y, 1.05):
            rows.append(None)
            continue
        pin = p - nout * 2.8
        pr = [(pin, zt), (p + nout * (ro - 0.45), zt), (po, zt - 0.4), (p + nout * (ro - 0.1), zt - 1.9),
              (p + nout * (o + prot * 0.3), zt - 2.8), (pin, zt - 3.2)]
        rows.append(([mb.bm.verts.new((v.x, v.y, z)) for v, z in pr], p, t, nout, ro, zt))
    mats = [GRASS, GRASS, TOP, DARK, DARK, DARK]
    by_m = {}
    bm = mb.bm
    runs = 0
    i = 0
    while i < len(rows):
        if rows[i] is None:
            i += 1
            continue
        j = i
        while j + 1 < len(rows) and rows[j + 1] is not None:
            j += 1
        if j - i >= 2:
            runs += 1
            for a in range(i, j):
                ra, rb = rows[a][0], rows[a + 1][0]
                for k in range(6):
                    k2 = (k + 1) % 6
                    by_m.setdefault(mats[k], []).append(bm.faces.new((ra[k], rb[k], rb[k2], ra[k2])))
            by_m.setdefault(ROCK, []).append(bm.faces.new(rows[i][0]))
            by_m.setdefault(ROCK, []).append(bm.faces.new(list(reversed(rows[j][0]))))
            # linguetas de grama caindo do beiral
            a = i + rng.randint(1, 3)
            while a < j:
                vs, p, t, nout, ro, zt = rows[a]
                wt = rng.uniform(1.2, 2.6)
                lt = rng.uniform(1.0, 2.8)
                c = p + nout * (ro + 0.06)
                back = -nout * 0.35
                pts = [c - t * (wt / 2), c + t * (wt / 2), c + nout * 0.12]
                zs = [zt - 0.3, zt - 0.3, zt - 0.3 - lt]
                fr = [bm.verts.new((q.x, q.y, z)) for q, z in zip(pts, zs)]
                bk = [bm.verts.new((q.x + back.x, q.y + back.y, z + (0.2 if k == 2 else 0.0)))
                      for k, (q, z) in enumerate(zip(pts, zs))]
                fl = [bm.faces.new(fr), bm.faces.new(list(reversed(bk)))]
                for k in range(3):
                    k2 = (k + 1) % 3
                    fl.append(bm.faces.new((fr[k2], fr[k], bk[k], bk[k2])))
                by_m.setdefault(GRASS, []).extend(fl)
                a += rng.randint(2, 4)
        else:
            for a in range(i, j + 1):
                for v in rows[a][0]:
                    bm.verts.remove(v)
        i = j + 1
    for mm, fl_ in by_m.items():
        _grp(mb, fl_, mm, variant=(mm in (ROCK, GRASS)))
    return runs


# ------------------------------------------------------------------ cristas baixas na borda
def crests(rng):
    mb = MB("DB_Ter_Crests", C, rng, detail="near", floor=-999)
    W = Walker(rim_pts())
    total = W.total
    falls = [W.param(*L.FALL_SW), W.param(*L.FALL_SE)]
    s = rng.uniform(0, 10)
    s_end = s + total
    n = 0
    while s < s_end:
        run = rng.randint(2, 5)
        for k in range(run):
            ln = rng.uniform(3.2, 7.0)
            sc = s + ln * 0.5
            p, t, nout = W.at(sc)
            nin = -nout
            skip = min(W.sdist(sc, f) for f in falls) < 6.5
            for u in (-0.6, 0.0, 0.6):
                pp = p + t * (ln * u)
                if bridge_deck(pp.x, pp.y, pad=4.5) is not None:
                    skip = True
                if abs(pp.x) < L.ENTRY_STAIR_W / 2 + 6.0 and pp.y < L.ENTRY_STAIR_Y1:
                    skip = True
                if near_mesa(pp.x, pp.y, 1.0) or in_water(pp.x, pp.y, pad=3.0):
                    skip = True
            if not skip:
                q = p + nin * 2.0
                lvl = level_at(q.x, q.y)
                hub = lvl > L.GROUND + 1.0
                hgt = rng.uniform(1.5, 2.6) if (hub or p.y < -100.0) else rng.uniform(2.2, 4.0)
                b = rng.uniform(1.1, 2.0)
                c = p + nin * rng.uniform(0.5, 1.6)
                poly = FP._rock_poly(ln * 0.5, b, rng.choice((5, 6)), rng, ex=rng.uniform(1.9, 2.5), jit=0.14)
                wp = to_world(poly, t, nin)
                lid = GRASS if rng.random() < 0.3 else None
                FP.rock_column(mb, c, wp, lvl - 0.8, lvl + hgt, rng, ROCK if rng.random() < 0.75 else DARK,
                               taper=rng.uniform(0.62, 0.82), rings=1, jitter=0.14, tilt=0.22, top_m=lid, lip=0.5,
                               chamfer=0.35, rim=False, band=(min(0.8, hgt * 0.3), TOP) if not lid else None,
                               bottom=False)
                n += 1
                if rng.random() < 0.35:
                    c2 = c + t * (ln * rng.choice((-0.55, 0.55))) + nin * rng.uniform(0.4, 1.2)
                    r2 = rng.uniform(0.6, 1.1)
                    mb.rock((c2.x, c2.y, lvl + r2 * 0.25), (r2 * 2.2, r2 * 1.8, r2 * 1.5), ROCK, 1,
                            (0, 0, rng.uniform(0, 6.28)), jitter=0.25)
            s += ln * rng.uniform(0.85, 1.0)
        s += rng.uniform(9.0, 20.0)
    mb.finish()
    return n


# ------------------------------------------------------------------ massa de baixo (ilha flutuante)
CAP_Z = G - 2.2                 # tampa escura sob o chao (abaixo do leito dos pocos, G - 1,6)
CORE_TOP = (CAP_Z, 0.975)       # parede de cima do nucleo (aberta no recorte da escadaria)
# nucleo cheio junto da borda ate bem abaixo da primeira fileira de costelas: o vao entre elas mostra rocha escura,
# nao o mar (a ilha le como massa pesada, nao disco sobre espetos)
CORE_PROFILE = [(12.0, 0.955), (0.0, 0.925), (-22.0, 0.81), (-48.0, 0.59), (-74.0, 0.34), (-95.0, 0.14)]
CORE_APEX = -108.0


def core_scale(z):
    pr = [CORE_TOP] + CORE_PROFILE
    if z >= pr[0][0]:
        return pr[0][1]
    for (z0, s0), (z1, s1) in zip(pr, pr[1:]):
        if z1 <= z <= z0:
            return s0 + (s1 - s0) * (z0 - z) / (z0 - z1)
    return pr[-1][1]


def underside(rng):
    mb = MB("DB_Ter_Underside", C, rng, detail="far", floor=-999)
    cx, cy = centroid()
    rim = rim_pts()
    # nucleo afunilado (escuro): aneis do contorno escalado, topo aberto (o chao/tampa fecha em cima)
    W = Walker(rim)
    k = 44
    base = [W.point(W.total * i / k) for i in range(k)]
    rings = []
    for zi, (z, s) in enumerate(CORE_PROFILE):
        ring = []
        for i, p in enumerate(base):
            j = 1.0 + rng.uniform(-0.035, 0.035) * (0.3 if zi == 0 else 1.0)
            x = cx + (p.x - cx) * s * j
            y = cy + (p.y - cy) * s * j
            zz = z + (rng.uniform(-2.0, 2.0) if zi > 0 else 0.0)
            ring.append(mb.bm.verts.new((x, y, zz)))
        rings.append(ring)
    fs_core = []
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(k):
            j = (i + 1) % k
            fs_core.append(mb.bm.faces.new((r1[i], r1[j], r0[j], r0[i])))
    ap = mb.bm.verts.new((cx + 6.0, cy - 10.0, CORE_APEX))
    for i in range(k):
        j = (i + 1) % k
        fs_core.append(mb.bm.faces.new((rings[-1][j], rings[-1][i], ap)))
    # parede de cima do nucleo (z 12 -> tampa), fina, aberta no recorte da escadaria da chegada
    kk = 180
    s0, s1 = CORE_PROFILE[0][1], CORE_TOP[1]
    top_pts = []
    for i in range(kk):
        p = W.point(W.total * i / kk)
        a = (cx + (p.x - cx) * s1, cy + (p.y - cy) * s1)
        top_pts.append((p, a, abs(a[0]) < L.ENTRY_STAIR_W / 2 + 2.6 and a[1] < -100.0))
    for i in range(kk):
        p0, a0, n0 = top_pts[i]
        p1, a1, n1 = top_pts[(i + 1) % kk]
        if n0 or n1:
            continue
        b0 = (cx + (p0.x - cx) * s0, cy + (p0.y - cy) * s0)
        b1 = (cx + (p1.x - cx) * s0, cy + (p1.y - cy) * s0)
        vs = [mb.bm.verts.new((b0[0], b0[1], 11.5)), mb.bm.verts.new((b1[0], b1[1], 11.5)),
              mb.bm.verts.new((a1[0], a1[1], CAP_Z)), mb.bm.verts.new((a0[0], a0[1], CAP_Z))]
        fs_core.append(mb.bm.faces.new(vs))
    TF.assign(mb, fs_core, DARK)
    # tampa do nucleo (so topo) sob o chao: arena e recorte da escadaria ficam abertos
    cap = []

    def notch_r(a):
        sa, ca = math.sin(math.radians(a)), math.cos(math.radians(a))
        if sa >= -0.2:
            return 1e9
        r = (-(L.ENTRY_STAIR_Y1 + 2.0)) / -sa
        return r if abs(r * ca) <= L.ENTRY_STAIR_W / 2 + 3.0 else 1e9
    step = 3.0
    zc = CAP_Z
    angs = [i * step for i in range(int(360 / step))]
    ti, to = [], []
    for a in angs:
        ri = L.arena_r(a) + 1.3
        ro = min(DL.rim_r(a) - 0.5, notch_r(a))
        ro = max(ro, ri + 0.5)
        c_, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        ti.append(mb.bm.verts.new((c_ * ri, s_ * ri, zc)))
        to.append(mb.bm.verts.new((c_ * ro, s_ * ro, zc)))
    for i in range(len(angs)):
        j = (i + 1) % len(angs)
        cap.append(mb.bm.faces.new((ti[i], to[i], to[j], ti[j])))
    TF.assign(mb, cap, DARK)
    # aneis de costelas penduradas presas ao nucleo (B, C, D): a silhueta desce em degraus ate a ponta
    n = 0
    # o primeiro anel (z 10) fica quase todo atras das costelas do penhasco: mais espacado
    for z_top, (wmin, wmax), (hmin, hmax), gap, nsides in ((10.0, (10.0, 17.0), (26.0, 44.0), (1.25, 1.6), 6),
                                                          (-20.0, (13.0, 21.0), (26.0, 42.0), (1.0, 1.35), 6),
                                                          (-46.0, (14.0, 24.0), (24.0, 40.0), (1.05, 1.5), 5),
                                                          (-72.0, (12.0, 18.0), (16.0, 28.0), (1.2, 1.7), 5)):
        s_ring = core_scale(z_top)
        Wr = Walker(scaled_rim(s_ring))
        s = rng.uniform(0, 8)
        while s < Wr.total:
            w = rng.uniform(wmin, wmax)
            sc = s + w * 0.5
            p, t, nout = Wr.at(sc)
            nin = -nout
            D = w * rng.uniform(0.6, 0.85)
            out = rng.uniform(1.5, 4.0)
            cc = p + nout * (out - D * 0.5)
            # nada invade as quedas d'agua (a cortina desce ~2..9 para fora da borda nos pontos de queda)
            bad = False
            for fx, fy in (L.FALL_SW, L.FALL_SE):
                if math.hypot(cc.x - fx, cc.y - fy) < w * 0.5 + 8.0 and z_top > -40.0:
                    bad = True
            if not bad:
                hh = rng.uniform(hmin, hmax)
                poly = foot(rng, w, D, n=nsides)
                zt = z_top + rng.uniform(-3.0, 3.0)
                lk = rng.uniform(2.0, 5.0)
                blunt = rng.random() < 0.45          # fundo gordo e arredondado (massa pesada), nao so espetos
                if blunt:
                    hh *= rng.uniform(0.6, 0.85)
                hang(mb, cc, to_world(poly, t, nin), zt, zt - hh, rng,
                     tip=rng.uniform(0.42, 0.62) if blunt else rng.uniform(0.1, 0.25),
                     pw=rng.uniform(1.2, 1.6) if blunt else rng.uniform(1.5, 2.2), lean=(nin.x * lk, nin.y * lk),
                     lid=False, band=0.0, strata=[(zz - th / 2, zz + th / 2) for zz, th, amp in STRATA
                                                  if th > 1.0 and zt - hh + 3.0 < zz - th / 2 and zz + th / 2 < zt - 1.2][:1],
                     mids=(), dark_from=rng.uniform(0.55, 0.75), jitter=0.1, top_jit=0.08, chamfer=0.6,
                     bottom_apex=not blunt)
                n += 1
            s += w * rng.uniform(*gap)
    mb.finish(recalc=False)
    return n


# ------------------------------------------------------------------ mesas / pilares / agulhas
CLUSTERS = {"NW": (0, 1, 2, 3), "Back": (4, 5, 6), "NE": (7, 8, 9), "Front": (10, 11)}
# pedras de ligacao dos cachos (fora da borda, nascem de baixo): (x, y, raio, topo, tipo). So BAIXAS e uma por cacho
# lateral: entre o NO, o fundo e o NE fica ceu (nada de palicada); o fundo nao ganha nenhuma (a cupula aparece)
FILLERS = {"NW": [(-168.0, 144.0, 7.5, 47.0, "pillar")],
           "Back": [],
           "NE": [(150.0, 160.0, 7.5, 52.0, "pillar")],
           "Front": [(-134.0, -118.0, 5.5, 40.0, "pillar"), (174.0, -6.0, 6.0, 44.0, "pillar")]}
# ombros de rocha que juntam cada cacho num macico so (topo abaixo do chao da ilha, fora das rotas): x, y, r, fundo
MASSIFS = {"NW": [(-162.0, 118.0, 23.0, 9.0), (-120.0, 178.0, 15.0, 12.0)],
           "Back": [(-32.0, 234.0, 21.0, 10.0), (30.0, 228.0, 17.0, 14.0)],
           "NE": [(142.0, 130.0, 19.0, 9.0), (120.0, 172.0, 13.0, 12.0)],
           "Front": []}
# ajustes por rocha da planta (indice de L.MESAS):
#  5 (mesa larga do fundo) fica entre a camera de tras e a cupula: corpo mais baixo e coroa em ESCADA descendo para
#    leste (o bloco alto no oeste; os outros abaixo da linha de visada da cupula)
#  6 (pilar do fundo, leste) e companheiro do heroi (pilar 4): receita atarracada, ombro largo
TWEAK = {5: {"rot": 0.0, "z1": 0.52, "crown": (0.0, 12.0, 23.0)},
         6: {"stout": True}}


def _stack(mb, rng, c, a, b, n, ex, rot, z0, z1, m, taper=0.94, lid=None, band=None, lean=None, chamfer=0.6,
           rings=2, jitter=0.1, tongues=None, tilt=0.06, K=None, fit=0.96, sq=(0.965, 0.995), notch=0, bottom=False,
           grow=1.35):
    """prisma de rocha (fm_parts.rock_column). K (Clear): se a peca cruza a faixa do corpo do jogador, o contorno
    ganha mais vertices e e ajustado ao octogono da coluna no lado alcancavel (fit: a face visual fica colada na
    colisao, sem parede invisivel larga) e os vertices finais passam pela compressao (squeeze, rede de seguranca do
    jitter). notch: vertices recuados depois do ajuste (fraturas verticais que leem de perto)"""
    ca, sa = math.cos(rot), math.sin(rot)
    squeeze = K is not None and K.hits(z0, z1)
    if squeeze:
        n = max(n, 13)
        jitter = min(jitter, 0.06)
        lean = None
    src = FP._rock_poly(a, b, n, rng, ex=ex, jit=0.1)
    poly = [(x * ca - y * sa, x * sa + y * ca) for x, y in src]
    n0 = 0
    if squeeze:
        poly = K.fit(c, poly, fit, grow)
        n0 = _nv(mb)
    if notch:
        idx = set(rng.sample(range(n), min(notch, max(1, n // 3))))
        poly = [(px * 0.82, py * 0.82) if i in idx else (px, py) for i, (px, py) in enumerate(poly)]
    out = FP.rock_column(mb, Vector((c[0], c[1], 0.0)), poly, z0, z1, rng, m, taper=taper, rings=rings,
                         jitter=jitter, tilt=tilt, lean=lean, top_m=lid, lip=1.2, chamfer=chamfer, rim=False,
                         band=band, tongues=tongues, bottom=bottom)
    if squeeze:
        K.squeeze(_new_verts(mb, n0), *sq)
    return out


def _tier(mb, rng, c, a, b, n, ex, rot, z0, z1, m, K=None, notch=0, **kw):
    """lance de pilar: se passa de 17 de altura, quebra em corpo de baixo + estrato escuro recuado + corpo de cima 4%
    mais estreito (patamar horizontal visivel: o lance le como camadas de arenito, nao como prisma liso)"""
    if z1 - z0 > 17.0:
        zm = z0 + (z1 - z0) * rng.uniform(0.42, 0.58)
        th = rng.uniform(0.9, 1.5)
        _stack(mb, rng, c, a, b, n, ex, rot, z0, zm, m, taper=rng.uniform(0.96, 0.99), rings=1, chamfer=0.0, K=K,
               notch=notch)
        _groove(mb, rng, c, a, b, n, rot, zm, th, K=K)
        z0 = zm + th
        a, b = a * 0.96, b * 0.96
        notch = 0
        kw["rings"] = 1
    return _stack(mb, rng, c, a, b, n, ex, rot, z0, z1, m, K=K, notch=notch, **kw)


def _ribs(mb, rng, c, a, b, rot, z0, z1, k, face=None, K=None):
    """costelas verticais salientes na face de um corpo (fraturas verticais do arenito). Onde o corpo foi apertado
    (lado alcancavel na faixa do jogador) nao ha costela: ela ficaria solta da face recuada"""
    if z1 - z0 < 5.0:
        return
    ca, sa = math.cos(rot), math.sin(rot)
    base = rng.uniform(0, math.tau) if face is None else face - rot
    body_sq = K is not None and K.hits(z0, z1)
    for i in range(k):
        th = base + (i - (k - 1) / 2.0) * rng.uniform(0.45, 0.8) + rng.uniform(-0.15, 0.15)
        px, py = a * math.cos(th), b * math.sin(th)
        nx, ny = math.cos(th) / a, math.sin(th) / b
        ln = math.hypot(nx, ny)
        nx, ny = nx / ln, ny / ln
        wx, wy = px * ca - py * sa, px * sa + py * ca
        gx, gy = nx * ca - ny * sa, nx * sa + ny * ca
        wr = a * rng.uniform(0.13, 0.22)
        dr = max(1.2, b * rng.uniform(0.16, 0.26))
        cc = (c[0] + wx + gx * dr * 0.2, c[1] + wy + gy * dr * 0.2)
        ang = math.atan2(gy, gx) + math.pi / 2
        za = z0 + rng.uniform(0.0, 2.5)
        zb = z1 - rng.uniform(0.6, 5.0)
        m = ROCK if rng.random() < 0.7 else DARK
        tp = rng.uniform(0.86, 0.96)
        if zb - za <= 4.0:
            continue
        if body_sq and not K.away(cc[0], cc[1], max(wr, dr) * 1.3):
            continue
        _stack(mb, rng, cc, wr, dr, 5, 2.2, ang, za, zb, m, taper=tp, rings=1, chamfer=0.4, jitter=0.08, tilt=0.1)


def _groove(mb, rng, c, a, b, n, rot, z, th, K=None):
    """estrato escuro: disco recuado entre dois corpos (le como faixa horizontal no paredao)"""
    _stack(mb, rng, c, a * 0.93, b * 0.93, n, 2.6, rot, z - 0.2, z + th + 0.2, DARK, taper=1.0, rings=1,
           chamfer=0.0, jitter=0.04, tilt=0.0, K=K, fit=0.88, sq=(0.89, 0.93))


def _root(mb, rng, c, a, b, n, ex, rot, z_top, z_bot, ld):
    """raiz pendurada: abaixo da ilha a rocha AFUNILA ate sumir nas nuvens (a mesma linguagem das costelas da massa
    de baixo) em vez de descer como coluna cheia ate o mar (que fazia a palicada)"""
    ca, sa = math.cos(rot), math.sin(rot)
    wp = [(px * ca - py * sa, px * sa + py * ca) for px, py in FP._rock_poly(a, b, n, rng, ex=ex, jit=0.08)]
    lk = rng.uniform(1.0, 4.0)
    hang(mb, Vector((c[0], c[1], 0.0)), wp, z_top, z_bot, rng, m=ROCK, tip=rng.uniform(0.2, 0.42),
         pw=rng.uniform(1.3, 1.9), lean=(-ld[0] * lk, -ld[1] * lk), lid=False, band=0.0,
         strata=[(zz - th / 2, zz + th / 2) for zz, th, amp in STRATA if th > 1.0], mids=(0.3, 0.6),
         dark_from=rng.uniform(0.3, 0.55), jitter=0.07, top_jit=0.03, chamfer=0.3, bottom_apex=rng.random() < 0.5)


def _tail(mb, rng, c, a, b, n, rot, z_top, depth):
    """ponta pendurada sob uma peca que nasce abaixo do topo da ilha (o fundo nunca fica aberto no ar)"""
    ca, sa = math.cos(rot), math.sin(rot)
    wp = [(px * ca - py * sa, px * sa + py * ca) for px, py in FP._rock_poly(a, b, n, rng, ex=2.2, jit=0.06)]
    hang(mb, Vector((c[0], c[1], 0.0)), wp, z_top, z_top - depth, rng, m=DARK, tip=rng.uniform(0.15, 0.3),
         pw=rng.uniform(1.4, 2.0), lid=False, band=0.0, mids=(0.5,), dark_from=0.0, jitter=0.06, top_jit=0.03,
         chamfer=0.3)


def _place(K, rng, x, y, base_ang, out_ang, d, rad, z0, z1, spread=1.0):
    """centro de uma peca satelite em volta da rocha: angulo perto de base_ang (depois o lado de fora da ilha); so
    onde ela nao entra no chao alcancavel fora do octogono da coluna"""
    tries = [base_ang + rng.uniform(-spread, spread)]
    tries += [base_ang + s * k for k in (0.3, 0.6, 0.9, 1.25, 1.6) for s in (-1, 1)]
    tries += [out_ang, out_ang + 0.35, out_ang - 0.35, out_ang + 0.7, out_ang - 0.7]
    for ang in tries:
        c = (x + math.cos(ang) * d, y + math.sin(ang) * d)
        if not K.on and not K.away(c[0], c[1], rad):
            continue                     # rocha sem coluna (longe da borda): o satelite nao pode chegar ao chao
        if K.free(c[0], c[1], rad, z0, z1):
            return c, ang
    return None, None


def _companion(mb, rng, K, x, y, r, Hv, zj, lean_dir, out_ang, spread, dist, size, hfrac, kind):
    """rocha companheira encostada (sempre MAIS BAIXA e mais larga que a principal): ombro de topo verde ou agulha"""
    a2, b2 = r * size[0], r * size[1]
    h2 = G + Hv * rng.uniform(*hfrac)
    z2 = zj - rng.uniform(4.0, 12.0)
    c2, ang = _place(K, rng, x, y, lean_dir, out_ang, r * dist, max(a2, b2) * 1.3, z2, h2, spread)
    if c2 is None:
        return
    if kind == "shoulder":
        _stack(mb, rng, c2, a2, b2, 6, 2.3, ang + math.pi / 2, z2, h2, ROCK, taper=rng.uniform(0.74, 0.9),
               lid=GRASS, band=(1.6, TOP), rings=2, tongues=(rng.randint(1, 3), GRASS, (1.0, 3.2), None))
    else:
        _stack(mb, rng, c2, a2, b2, 6, 2.1, ang, z2, h2, ROCK, taper=rng.uniform(0.5, 0.64), band=(1.8, TOP),
               rings=3, chamfer=min(1.5, a2 * 0.3))
    _tail(mb, rng, c2, a2 * 0.96, b2 * 0.96, 6, ang + (math.pi / 2 if kind == "shoulder" else 0.0), z2 + 0.8,
          rng.uniform(10.0, 22.0))


def _mesa(mb, rng, x, y, r, top, K, zj, face, rot, lean_dir, tw):
    Hv = top - G
    ld = (math.cos(lean_dir), math.sin(lean_dir))
    a, b = r * rng.uniform(1.05, 1.18), r * rng.uniform(0.84, 0.95)
    n = 9
    ex = rng.uniform(2.3, 2.9)
    z0 = G + Hv * rng.uniform(0.18, 0.28)
    z1 = G + Hv * tw.get("z1", rng.uniform(0.56, 0.66))
    _stack(mb, rng, (x, y), a, b, n, ex, rot, zj, z0, DARK, taper=0.95, rings=2, chamfer=0.0, K=K, notch=3)
    _ribs(mb, rng, (x, y), a * 0.98, b * 0.98, rot, zj, z0, 3, face, K=K)
    _ribs(mb, rng, (x, y), a * 0.98, b * 0.98, rot, zj, z0, 2, face + math.pi, K=K)
    g1 = rng.uniform(1.4, 2.4)
    _groove(mb, rng, (x, y), a * 0.95, b * 0.95, n, rot, z0, g1, K=K)
    off = r * 0.06
    c1 = (x + math.cos(rot) * off, y + math.sin(rot) * off)
    _stack(mb, rng, c1, a * 0.95, b * 0.95, n, ex, rot, z0 + g1, z1, ROCK, taper=0.95,
           lid=GRASS if rng.random() < 0.6 else None, band=(2.0, TOP), chamfer=0.4, K=K)
    _ribs(mb, rng, c1, a * 0.93, b * 0.93, rot, z0 + g1, z1, 3, face, K=K)
    _ribs(mb, rng, c1, a * 0.93, b * 0.93, rot, z0 + g1, z1, 2, face + math.pi, K=K)
    g2 = rng.uniform(1.0, 1.8)
    _groove(mb, rng, c1, a * 0.9, b * 0.9, n, rot, z1, g2, K=K)
    # coroa partida por fraturas verticais: 2-3 blocos lado a lado com alturas diferentes, topo plano de grama
    drops = tw.get("crown")
    k = len(drops) if drops else rng.choice((2, 3, 3))
    ax = (math.cos(rot), math.sin(rot))
    hi = rng.randrange(k)
    for i in range(k):
        u = -1.0 + (2.0 * i + 1.0) / k
        ci = (c1[0] + ax[0] * a * 0.9 * u * 0.62, c1[1] + ax[1] * a * 0.9 * u * 0.62)
        ai = a * 0.9 / k * rng.uniform(1.05, 1.2)
        zt = top - (drops[i] if drops else (0.0 if i == hi else rng.uniform(2.5, 8.0)))
        if zt - (z1 + g2) < 3.0:
            continue
        _stack(mb, rng, ci, ai, b * 0.88 * rng.uniform(0.92, 1.0), 7, rng.uniform(2.2, 2.8), rot,
               z1 + g2, zt, ROCK, taper=rng.uniform(0.9, 0.97), lid=GRASS, band=(2.4, TOP),
               tongues=(rng.randint(1, 3), GRASS, (1.0, 3.5), None), K=K)
    # corpo secundario: contraforte baixo encostado do lado de fora (nunca no chao alcancavel)
    for q in range(rng.randint(1, 2)):
        _companion(mb, rng, K, x, y, r, Hv, zj, lean_dir, face + math.pi, 0.9, rng.uniform(0.85, 1.05),
                   (rng.uniform(0.32, 0.45), rng.uniform(0.28, 0.4)), (0.3, 0.55), "shoulder")


def _pillar(mb, rng, x, y, r, top, K, zj, face, rot, lean_dir, tw):
    """pilar-mesa: 2-3 lances LARGOS e arredondados (cada lance 0,86-0,95 do de baixo, quase sem deslocamento: nada de
    haste de prismas empilhados); troca de lance = estrato escuro recuado OU degrau com faixa clara; grama no topo e no
    maximo um colar. Ombro largo (0,7-0,9 r, 30-50% da altura) SEMPRE encostado - do lado da ilha quando cabe, senao
    de lado/fora - e um segundo ombro mais baixo: a base le como mesa escalonada com patamares verdes"""
    Hv = top - G
    stout = tw.get("stout", False)
    a, b = r * rng.uniform(1.0, 1.1) * (1.06 if stout else 1.0), r * rng.uniform(0.84, 0.96)
    n = rng.choice((8, 9, 9))
    ex = rng.uniform(2.1, 2.5)
    k = 2 if (stout or Hv < 70.0) else 3
    fr = []
    for i in range(1, k):
        f = (i + rng.uniform(-0.2, 0.15)) / k
        lo = 0.3 if not fr else fr[-1] + 0.18
        fr.append(min(0.8, max(lo, f)))
    zs = [zj] + [G + Hv * f for f in fr] + [top]
    trans = [None] + [("groove" if rng.random() < 0.5 else "step") for _ in range(1, k)]
    ledge = rng.randrange(1, k) if (k > 1 and rng.random() < 0.4) else None
    c = (x, y)
    sc = 1.0
    rt = rot
    bb = b
    for i in range(k):
        last = i == k - 1
        if i > 0:
            sc *= rng.uniform(0.86, 0.95) if not stout else rng.uniform(0.84, 0.9)
            sh = r * rng.uniform(0.02, 0.07)
            dirn = lean_dir + rng.uniform(-0.6, 0.6)
            c = (c[0] + math.cos(dirn) * sh, c[1] + math.sin(dirn) * sh)
            rt += rng.uniform(-0.25, 0.25)
            bb = min(a * 0.98, b * rng.uniform(0.92, 1.06))
        za, zt = zs[i], zs[i + 1]
        if i > 0 and trans[i] == "groove":
            th = rng.uniform(1.0, 1.8)
            _groove(mb, rng, c, a * sc, bb * sc, n, rt, za, th, K=K)
            za += th
        nr = rng.choice((0, 1, 2, 2))
        if last:
            if rng.random() < 0.4:
                # topo fraturado: 2 blocos largos de alturas diferentes
                ax = (math.cos(rt), math.sin(rt))
                for q, sg in enumerate((-1, 1)):
                    cq = (c[0] + ax[0] * a * sc * 0.36 * sg, c[1] + ax[1] * a * sc * 0.36 * sg)
                    zt2 = zt - (0.0 if q == 0 else rng.uniform(3.0, 8.0))
                    _stack(mb, rng, cq, a * sc * 0.68, bb * sc * rng.uniform(0.9, 1.0), 8, ex, rt, za, zt2, ROCK,
                           taper=rng.uniform(0.88, 0.95), lid=GRASS, band=(2.0, TOP),
                           tongues=(rng.randint(1, 3), GRASS, (1.0, 3.2), None), K=K)
            else:
                _tier(mb, rng, c, a * sc, bb * sc, n, ex, rt, za, zt, ROCK, taper=rng.uniform(0.86, 0.94),
                      lid=GRASS, band=(2.0, TOP), rings=2 if zt - za > 22.0 else 1,
                      tongues=(rng.randint(2, 4), GRASS, (1.2, 3.6), None), K=K)
        else:
            nxt = trans[i + 1]
            lid = GRASS if ledge == i + 1 else None
            _tier(mb, rng, c, a * sc, bb * sc, n, ex, rt, za, zt, DARK if (i == 0 and rng.random() < 0.5) else ROCK,
                  taper=rng.uniform(0.9, 0.97), lid=lid,
                  band=(rng.uniform(1.6, 2.6), TOP) if (nxt == "step" or lid) else None,
                  rings=2 if zt - za > 22.0 else 1, K=K, notch=2 if i == 0 else 0,
                  tongues=(rng.randint(1, 3), GRASS, (1.0, 3.0), None) if lid else None)
        if nr:
            _ribs(mb, rng, c, a * sc * 0.95, bb * sc * 0.95, rt, za, zt, nr,
                  face if rng.random() < 0.5 else face + math.pi, K=K)
    # ombro largo (patamar verde a 30-50% da altura), do lado da ilha quando cabe; + ombro baixo do outro lado
    _companion(mb, rng, K, x, y, r, Hv, zj, face, face + math.pi, 0.5, rng.uniform(0.7, 0.9),
               (rng.uniform(0.7, 0.9), rng.uniform(0.55, 0.72)), (0.3, 0.5), "shoulder")
    if stout or rng.random() < 0.65:
        _companion(mb, rng, K, x, y, r, Hv, zj, lean_dir + rng.choice((-1.0, 1.0)) * 1.1, face + math.pi, 0.5,
                   rng.uniform(0.85, 1.05), (rng.uniform(0.5, 0.62), rng.uniform(0.42, 0.52)), (0.16, 0.3),
                   "shoulder")


def _spire(mb, rng, x, y, r, top, K, zj, face, rot, lean_dir, tw):
    """agulha (so as 2 da planta): 3 lances arredondados que afinam de verdade so no ultimo, ombro largo no pe"""
    Hv = top - G
    ld = (math.cos(lean_dir), math.sin(lean_dir))
    n = rng.choice((7, 8))
    a, b = r * rng.uniform(1.0, 1.08), r * rng.uniform(0.84, 0.94)
    k = 3
    fr = [rng.uniform(0.28, 0.36), rng.uniform(0.6, 0.7)]
    zs = [zj] + [G + Hv * f for f in fr] + [top]
    sc = 1.0
    c = (x, y)
    for i in range(k):
        last = i == k - 1
        if i > 0:
            sc *= rng.uniform(0.8, 0.88)
            sh = r * rng.uniform(0.04, 0.1)
            c = (c[0] + ld[0] * sh, c[1] + ld[1] * sh)
        za = zs[i]
        if i > 0 and rng.random() < 0.5:
            th = rng.uniform(1.0, 1.6)
            _groove(mb, rng, c, a * sc, b * sc, n, rot, za, th, K=K)
            za += th
        _stack(mb, rng, c, a * sc, b * sc, n, rng.uniform(2.0, 2.4), rot + i * rng.uniform(0.1, 0.3), za, zs[i + 1],
               DARK if i == 0 else ROCK, taper=rng.uniform(0.88, 0.95) if not last else rng.uniform(0.46, 0.56),
               band=(1.8, TOP) if i > 0 else None, rings=2 if i == 0 else (3 if last else 1),
               chamfer=(min(2.5, r * sc * 0.4) if last else 0.4),
               lean=(ld[0] * r * rng.uniform(0.06, 0.12), ld[1] * r * rng.uniform(0.06, 0.12)) if last else None,
               K=K, notch=2 if i == 0 else 0)
    _companion(mb, rng, K, x, y, r, Hv, zj, face, face + math.pi, 0.6, rng.uniform(0.75, 0.95),
               (rng.uniform(0.62, 0.78), rng.uniform(0.5, 0.62)), (0.22, 0.38), "shoulder")


def mesa_body(mb, rng, x, y, r, top, kind, primary=True, K=None, tw=None):
    tw = tw or {}
    K = K or Clear(x, y, r, False)
    cx, cy = centroid()
    face = math.atan2(cy - y, cx - x)              # lado que olha a ilha
    rot = rng.uniform(0, math.tau)
    rot = tw.get("rot", rot)
    lean_dir = face + math.pi + rng.uniform(-0.8, 0.8)   # inclina para FORA da ilha
    ld = (math.cos(lean_dir), math.sin(lean_dir))
    zb = (-62.0 - rng.uniform(0.0, 14.0)) if primary else (-46.0 - rng.uniform(0.0, 10.0))
    zj = G - rng.uniform(9.0, 15.0)                      # juncao corpo / raiz pendurada (sob o topo da ilha)
    if kind == "mesa":
        ra, rb, rn = r * 1.1, r * 0.88, 9
    else:
        ra, rb, rn = r * 0.98, r * 0.82, 7
    _root(mb, rng, (x, y), ra, rb, rn, 2.4, rot, zj + 1.0, zb, ld)
    if kind == "mesa":
        _mesa(mb, rng, x, y, r, top, K, zj, face, rot, lean_dir, tw)
    elif kind == "pillar":
        _pillar(mb, rng, x, y, r, top, K, zj, face, rot, lean_dir, tw)
    else:
        _spire(mb, rng, x, y, r, top, K, zj, face, rot, lean_dir, tw)


def mesas(rng):
    out = []
    for name, idx in CLUSTERS.items():
        mb = MB("DB_Ter_Mesas%s" % name, C, random.Random(rng.random()), detail="far", floor=-999)
        for i in idx:
            x, y, r, top, kind = L.MESAS[i]
            mesa_body(mb, mb.rng, x, y, r, top, kind, True, Clear(x, y, r, has_col(x, y, r)), TWEAK.get(i))
        for x, y, r, top, kind in FILLERS[name]:
            mesa_body(mb, mb.rng, x, y, r, top, kind, False, Clear(x, y, r, False))
        for x, y, r, dz in MASSIFS[name]:
            q = mb.rng
            rot = q.uniform(0, math.tau)
            zt = G - dz
            zm = zt - q.uniform(12.0, 18.0)
            zr = zm - q.uniform(6.0, 10.0)
            _root(mb, q, (x, y), r * 1.12, r * 0.83, 9, 2.4, rot, zr + 1.0, -52.0 - q.uniform(0.0, 14.0), (0.0, 0.0))
            _stack(mb, q, (x, y), r * 1.15, r * 0.85, 9, 2.4, rot, zr, zm, DARK, taper=0.9, rings=1, chamfer=0.0)
            _groove(mb, q, (x, y), r * 1.02, r * 0.76, 9, rot, zm, 1.6)
            _stack(mb, q, (x, y), r * 1.02, r * 0.76, 8, 2.4, rot, zm + 1.6, zt, ROCK, taper=0.86,
                   lid=GRASS, band=(2.2, TOP), tongues=(3, GRASS, (1.2, 3.6), None))
            _ribs(mb, q, (x, y), r * 1.0, r * 0.74, rot, zm + 1.6, zt, 3, None)
        out.append(mb.finish())
    # bica da cascata NW: laje saliente na face da mesa NW, sob o ponto de onde a agua sai
    tx, ty, tz = L.CASCADE_NW_TOP
    mb = MB("DB_Ter_MesaSpring", C, random.Random(77), detail="far", floor=-999)
    mx, my = L.MESAS[0][0], L.MESAS[0][1]
    ang = math.atan2(ty - my, tx - mx)
    c = (tx - math.cos(ang) * 3.2, ty - math.sin(ang) * 3.2)
    _stack(mb, mb.rng, c, 6.0, 4.0, 6, 2.3, ang + math.pi / 2, tz - 9.0, tz - 0.4, ROCK, taper=0.9,
           band=(1.2, TOP), chamfer=0.3, rings=1)
    _stack(mb, mb.rng, (tx - math.cos(ang) * 5.5, ty - math.sin(ang) * 5.5), 7.0, 5.0, 6, 2.3, ang + math.pi / 2,
           tz - 30.0, tz - 8.0, DARK, taper=0.85, rings=1, chamfer=0.0)
    out.append(mb.finish())
    return out


# ------------------------------------------------------------------ rochedos do plato
def plateau_rocks(rng):
    """massa primaria + corpo secundario + coroa deslocada, TUDO dentro do octogono da coluna do db_col (o jogador
    anda em volta: nada de pedra solta ou saliencia fora da colisao)"""
    mb = MB("DB_Ter_PlateauRocks", C, rng, detail="near", floor=-999)
    for x, y, r, h in L.PLATEAU_ROCKS:
        z = L.zone_of(x, y)
        K = Clear(x, y, r, True)
        rot = rng.uniform(0, math.tau)
        a, b = r * 0.92, r * rng.uniform(0.8, 0.88)
        n = 8
        z1 = z + h * rng.uniform(0.62, 0.72)
        if h >= 8.5:
            zm = z + h * rng.uniform(0.3, 0.38)
            _stack(mb, rng, (x, y), a, b, n, 2.3, rot, z - 1.0, zm, ROCK, taper=0.97, chamfer=0.0, rings=1, K=K,
                   notch=2)
            _groove(mb, rng, (x, y), a * 0.97, b * 0.97, n, rot, zm, 0.9, K=K)
            _stack(mb, rng, (x, y), a * 0.96, b * 0.96, n, 2.3, rot, zm + 0.9, z1, ROCK, taper=0.88,
                   band=(1.2, TOP), lid=GRASS if rng.random() < 0.4 else None, chamfer=0.4, rings=1, K=K)
        else:
            _stack(mb, rng, (x, y), a, b, n, 2.3, rot, z - 1.0, z1, ROCK, taper=0.86, band=(1.2, TOP),
                   lid=GRASS if rng.random() < 0.4 else None, chamfer=0.4, rings=2, K=K, notch=2)
        # coroa deslocada (fratura) + corpo secundario baixo encostado
        ang = rng.uniform(0, math.tau)
        c2 = (x + math.cos(ang) * r * 0.16, y + math.sin(ang) * r * 0.16)
        _stack(mb, rng, c2, a * 0.62, b * 0.7, 6, 2.1, rot + 0.4, z1 - 0.6, z + h, ROCK, taper=0.72,
               band=(min(1.4, h * 0.14), TOP), chamfer=0.6, rings=1, tilt=0.14, K=K, fit=0.82, grow=1.0)
        ang2 = ang + math.pi + rng.uniform(-0.8, 0.8)
        c3 = (x + math.cos(ang2) * r * 0.4, y + math.sin(ang2) * r * 0.4)
        _stack(mb, rng, c3, r * 0.42, r * 0.34, 6, 2.0, ang2, z - 0.8, z + h * rng.uniform(0.32, 0.46), DARK,
               taper=0.7, band=(0.8, TOP), chamfer=0.4, rings=1, tilt=0.12, K=K)
    mb.finish()
