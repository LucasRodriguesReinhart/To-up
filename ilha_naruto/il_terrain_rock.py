# il_terrain_rock - penhascos da Ilha 1 (zona terrain, prefixo TER_) - rodada 2.
#   colunas de rocha castanho-dourada com TOM POR COLUNA (Cliff_Rock_Tan / _B / _C) e frestas escuras; tampa de
#   grama (0,4 de tampa + 0,6 de beiral caido) sempre ABAIXO do gramado vizinho; sangrias das 4 quedas pela borda
#   (SE, OESTE, NE: colunas rebaixadas e recuadas numa janela de +-6 pela pegada; DRENAGEM: nada sai mais de 2,4);
#   penhasco baixo com fundos variados e afunilados, colunas externas destacadas e enseadas nas quedas; 3
#   promontorios em 2 patamares (G-10 / G-20); paredao curvo em patamares (64 / 72 / 84) com os 3 sulcos das
#   quedas do fundo. Visual (a colisao do chao e da borda vem do il_core), menos a fresta leste do T2 (COL_TerrainRock).
#   Usado por il_terrain.build(): upper_cliffs, shelf_and_lower (nucleo, promontorios, penhasco baixo), back_massif.
import math
from mathutils import Vector
import fm_lib
import il_lib as IL
from il_lib import MB, col_box2
import il_layout as L
import fm_parts as FP

TAN = "Cliff_Rock_Tan"
TAN_B = "Cliff_Rock_Tan_B"
TAN_C = "Cliff_Rock_Tan_C"
DARK = "Cliff_Rock_Tan_Dark"
TOP = "Cliff_Rock_Tan_Top"
GRASS = "Grass_Konoha"
C = "02_TERRAIN"
TONES = ((TAN, 5.0), (TAN_B, 3.0), (TAN_C, 2.0))

LID_EPS = 0.12            # a tampa de grama fica este tanto ABAIXO do gramado vizinho (nunca acima)
LID_T = 0.4               # espessura da tampa de grama
LID_DROP = 0.6            # beiral de grama caido pela face
Z_BOT = L.SHELF_Z - 16.0  # pe medio das colunas de cima (o penhasco baixo cobre)

# ------------------------------------------------------------------ quedas pela borda (contrato terreno x agua)
FALLS = {"SE": (101.0, -75.0), "W": (-158.0, 76.0), "NE": (118.05, 147.7), "DRAIN": (-88.5, -71.0)}
# (integracao) NE: centro da crista real da queda (y 140,7..154,7, afastada da ponte de saida), janela +2,5
WIN_EXTRA = {"NE": 2.5}
SPILL_KEYS = ("SE", "W", "NE")     # sangrias: colunas de cima rebaixadas 1,3 (SE: abaixo do leito do riacho)
WIN = 6.0                          # meia janela ao longo da borda (pela PEGADA da coluna)
DRAIN_MAX_OUT = 2.4                # drenagem: nenhuma coluna de cima sai mais que isto da borda (janela de 12)
SPILL_FACE = 0.5                   # sangrias: a face das colunas fica no maximo isto fora da borda (queda a 2,9)
COVE_HW = 10.0                     # enseada no penhasco baixo (meia largura ao longo da borda)
COVES = [FALLS[k] for k in ("SE", "W", "DRAIN", "NE")]      # compat
SPILL = [FALLS[k] for k in SPILL_KEYS]                      # compat


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


_RIM = {}


def _rim():
    if not _RIM:
        pts = IL.rim()
        cum = [0.0]
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            cum.append(cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        _RIM.update(pts=pts, cum=cum, total=cum[-1])
    return _RIM


def rim_param(x, y):
    """(s ao longo da borda anti-horaria a partir do vertice 0, ponto da borda, normal para fora, distancia com
    sinal: + fora da ilha)"""
    R = _rim()
    pts, cum = R["pts"], R["cum"]
    best = None
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / ll))
        qx, qy = a[0] + dx * t, a[1] + dy * t
        d = math.hypot(x - qx, y - qy)
        if best is None or d < best[0]:
            ln = math.sqrt(ll)
            best = (d, cum[i] + ln * t, (qx, qy), (dy / ln, -dx / ln))
    d, s, q, nrm = best
    sgn = -1.0 if fm_lib.point_in_poly(x, y, pts) else 1.0
    return s, q, nrm, d * sgn


def s_gap(s1, s2):
    """distancia ao longo da borda (circular)"""
    T = _rim()["total"]
    d = abs(s1 - s2) % T
    return min(d, T - d)


_FALL_S = {}


def fall_s(key):
    if key not in _FALL_S:
        _FALL_S[key] = rim_param(*FALLS[key])[0]
    return _FALL_S[key]


def fall_hit(s, half, win=WIN):
    """chave da queda cuja janela (+-win ao longo da borda) a pegada [s-half, s+half] cruza (ou None)"""
    for k in FALLS:
        if s_gap(s, fall_s(k)) < half + win + WIN_EXTRA.get(k, 0.0):
            return k
    return None


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


# ------------------------------------------------------------------ tom por coluna
class Tones:
    """sorteia o tom de cada coluna (Tan / _B / _C, nunca o mesmo da vizinha) - cada tom vira uma MeshPart de cor
    solida no Roblox; o escuro (fresta) e escolhido por quem chama"""

    def __init__(self, rng):
        self.rng = rng
        self.last = None

    def __call__(self):
        cands = [(m, w) for m, w in TONES if m != self.last]
        x = self.rng.random() * sum(w for _, w in cands)
        pick = cands[-1][0]
        for m, w in cands:
            x -= w
            if x <= 0:
                pick = m
                break
        self.last = pick
        return pick


# ------------------------------------------------------------------ uma coluna de rocha (construtor proprio)
def _set(mb, faces, mat, variant=False):
    if not faces:
        return
    mi = mb._mi_for(mat) if variant else mb._mi(mat)
    tt = mb.rng.uniform(-1.0, 1.0)
    for f in faces:
        f.material_index = mi
        f[mb.tint] = tt
        f.smooth = False
        f.normal_update()
    mb._uv(faces, mat)


def rock(mb, cc, wp, z0, z1, rng, m, lid=False, taper=0.94, bot=1.0, rings=None, jitter=0.1, tilt=0.03,
         band=True, tongues=None, lean=None, closed=False, chamfer=None):
    """prisma de rocha facetado com tom EXPLICITO. wp: contorno (dx, dy) em relacao a cc; taper: escala do topo;
    bot < 1: fundo afunilado (ponta pendurada, fecha o fundo); lid: tampa de grama com topo em z1 (LID_T de tampa
    + LID_DROP de beiral caido), o ponto mais alto nunca passa de z1; sem lid: chanfro de rocha no topo.
    tongues: (k, (dx, dy)) linguetas de grama descendo pela face. Retorna o centro do topo."""
    n = len(wp)
    h = z1 - z0
    if h < 0.6:
        return None
    cap = min(LID_T + LID_DROP, h * 0.4) if lid else min(0.6 if chamfer is None else chamfer, h * 0.12)
    zr = z1 - cap
    hr = zr - z0
    if rings is None:
        rings = 1 if hr < 12 else (2 if hr < 40 else (3 if hr < 90 else 4))
    fs = [k / rings for k in range(rings + 1)]
    fb = None
    if bot < 0.97:
        fb = min(0.4, 12.0 / max(hr, 1.0))
        if all(abs(fb - f) > 0.04 for f in fs):
            fs = sorted(fs + [fb])
    tx, ty = rng.uniform(-tilt, tilt), rng.uniform(-tilt, tilt)
    tmax = max(px * tx + py * ty for px, py in wp) * taper
    lx, ly = lean if lean else (0.0, 0.0)
    R = []
    last = len(fs) - 1
    for i, f in enumerate(fs):
        z = z0 + hr * f
        if 0 < f < 1 and f != fb:
            z += rng.uniform(-0.1, 0.1) * hr / rings
        sb = 1.0 if fb is None else (bot + (1.0 - bot) * min(1.0, f / fb))
        sc = sb * (1.0 + (taper - 1.0) * (f ** 1.3))
        lf = f ** 1.6
        ring = []
        for (px, py) in wp:
            j = 1.0 + rng.uniform(-jitter, jitter) * (0.4 if i == 0 else 1.0)
            zz = z + ((px * sc * tx + py * sc * ty - tmax) if i == last else 0.0)
            ring.append(mb.bm.verts.new((cc.x + px * sc * j + lx * lf, cc.y + py * sc * j + ly * lf, zz)))
        R.append(ring)
    band_i = None
    if band and hr > 5.0:
        bt = min(3.0, hr * 0.16)
        below, top = R[-2], R[-1]
        ring = []
        for vb, vt in zip(below, top):
            dz = vt.co.z - vb.co.z
            k = (dz - bt) / dz if dz > 1e-6 else 0.5
            ring.append(mb.bm.verts.new(vb.co.lerp(vt.co, min(max(k, 0.15), 0.9))))
        R.insert(len(R) - 1, ring)
        band_i = len(R) - 2
    rock_f, band_f, grass_f = [], [], []
    for k in range(len(R) - 1):
        r0, r1 = R[k], R[k + 1]
        for i in range(n):
            j = (i + 1) % n
            f = mb.bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
            (band_f if (band_i is not None and k >= band_i) else rock_f).append(f)
    top = R[-1]
    cx = sum(v.co.x for v in top) / n
    cy = sum(v.co.y for v in top) / n
    rad = max(0.3, sum(math.hypot(v.co.x - cx, v.co.y - cy) for v in top) / n)

    def ring_from(src, s, dz):
        return [mb.bm.verts.new((cx + (v.co.x - cx) * s, cy + (v.co.y - cy) * s, v.co.z + dz)) for v in src]
    upper = band_f if band_i is not None else rock_f
    if lid:
        ov = 1.0 + min(0.12, max(0.05, 0.4 / rad))
        ch = min(0.3, 0.45 / rad)
        ra = ring_from(top, ov, 0.0)
        rb = ring_from(top, ov, cap * (LID_DROP / (LID_T + LID_DROP)))
        rc = ring_from(top, ov * (1.0 - ch), cap)
        seq = [top, ra, rb, rc]
        for r0, r1 in zip(seq, seq[1:]):
            for i in range(n):
                j = (i + 1) % n
                grass_f.append(mb.bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
        grass_f.append(mb.bm.faces.new(rc))
    elif cap > 0.05:
        ch = min(0.35, cap / rad)
        rc = ring_from(top, 1.0 - ch, cap)
        for i in range(n):
            j = (i + 1) % n
            upper.append(mb.bm.faces.new((top[i], top[j], rc[j], rc[i])))
        upper.append(mb.bm.faces.new(rc))
    else:
        upper.append(mb.bm.faces.new(top))
    if closed or bot < 0.97:
        rock_f.append(mb.bm.faces.new(list(reversed(R[0]))))
    _set(mb, rock_f, m)
    _set(mb, band_f, TOP)
    _set(mb, grass_f, GRASS, variant=True)
    if tongues and lid and tongues[0] > 0:
        FP._tongues(mb, R[-2], top, (cx, cy), (tongues[0], GRASS, (1.0, 3.0), tongues[1]), rng)
    return Vector((cx, cy, z1))


def _foot(rng, a, b, n=None, ex=None):
    n = n or rng.choice((5, 6, 6, 7))
    a0 = (math.radians(-90.0 - 180.0 / n) % (math.tau / n)) + rng.uniform(-0.1, 0.1)
    return FP._rock_poly(a, b, n, rng, ex=ex or rng.uniform(2.0, 2.7), jit=0.1, a0=a0)


def column(mb, p, t, out, w, depth, z0, z1, rng, m=TAN, lid=True, rings=None, taper=None, tilt=0.03,
           band=True, tongues=0, lean=0.0, n=None, ex=None, bot=1.0, closed=False):
    """coluna com a FACE para fora da linha (normal (t.y, -t.x)) a ~out (+0,15 * fundo/2) alem do ponto p"""
    a, b = w * 0.5 * 1.04, depth * 0.5
    poly = _foot(rng, a, b, n, ex)
    left = Vector((-t.y, t.x, 0.0))
    nout = -left
    cc = p + nout * (out - 0.88 * b)
    wp = FP._to_world(poly, t, left)
    taper = taper if taper is not None else rng.uniform(0.9, 0.97)
    lv = (nout.x * lean, nout.y * lean) if lean else None
    rock(mb, cc, wp, z0, z1, rng, m, lid=lid, taper=taper, bot=bot, rings=rings, tilt=tilt, band=band,
         tongues=((tongues, (nout.x, nout.y)) if tongues else None), lean=lv, closed=closed)
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


_BED = None


def _pip(x, y, poly):
    ins = False
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            ins = not ins
    return ins


def _bed_hit(cc, t, a, b):
    """a pegada da coluna (grade 5x5) cai dentro do leito do riacho do vale (+0,6)?"""
    global _BED
    if _BED is None:
        import il_col
        _BED = il_col.stream_bed_poly()
    left = Vector((-t.y, t.x, 0.0))
    for u in (-1.0, -0.5, 0.0, 0.5, 1.0):
        for v in (-1.0, -0.5, 0.0, 0.5, 1.0):
            q = cc + t * (a * u) + left * (b * v)
            for dx, dy in ((0, 0), (0.6, 0), (-0.6, 0), (0, 0.6), (0, -0.6)):
                if _pip(q.x + dx, q.y + dy, _BED):
                    return True
    return False


def _hits_box(cc, t, a, b, box):
    left = Vector((-t.y, t.x, 0.0))
    x0, y0, x1, y1 = box
    for u in (-1.0, -0.5, 0.0, 0.5, 1.0):
        for v in (-1.0, 0.0, 1.0):
            q = cc + t * (a * u) + left * (b * v)
            if x0 <= q.x <= x1 and y0 <= q.y <= y1:
                return True
    return False


def _inside_rim(x, y):
    return fm_lib.point_in_poly(x, y, _rim()["pts"])


def podium_box(m=0.5):
    """embasamento de pedra da casa leste (134,-26) (il_houses: pegada + 0,9) - desce ate L.SHELF_Z - 2"""
    x, y, w, d = L.EAST_HOUSES[0][:4]
    e = 0.9 + m
    return (x - w / 2 - e, y - d / 2 - e, x + w / 2 + e, y + d / 2 + e)


# ------------------------------------------------------------------ penhasco de cima (borda da ilha -> prateleira)
def _width(rng, narrow=(5.0, 8.5), wide=(11.0, 18.0), p_wide=0.42):
    return rng.uniform(*wide) if rng.random() < p_wide else rng.uniform(*narrow)


def in_massif(s, margin=0.0):
    """o trecho da borda de (116,160) a (-150,120) (anti-horario) e coberto pelo paredao"""
    cum = _rim()["cum"]
    return cum[13] + margin <= s <= cum[20] - margin


def upper_cliffs(rng):
    """colunas justapostas ao longo da borda: larguras bimodais, tom por coluna, frestas escuras de ~1,0 entre
    parte delas, frente desencontrada, tampa de grama 0,12 ABAIXO do gramado (dentes mais baixos, cristas nuas);
    colunas altas com trinca horizontal. Sangrias (SE, O, NE): toda coluna cuja pegada cruza a janela de +-6
    baixa 1,3 e recua (a SE fica abaixo do leito do riacho); drenagem: nada sai mais de 2,4 da borda. O trecho do
    paredao (borda norte) fica por conta do back_massif."""
    mb = MB("TER_Cliffs_Upper", C, rng, detail="near")
    tone = Tones(rng)
    ncol = 0
    pod = podium_box()
    for level, pts in rim_runs():
        total, at = walker(pts)
        if total < 2.0:
            continue
        s = 0.0
        while s < total - 0.3:
            w = _width(rng, (5.5, 9.0), (11.0, 17.0))
            if total - s - w < 4.0:
                w = total - s
            if w < 3.0:
                break
            sc = s + w * 0.5
            p, t = at(sc)
            srim = rim_param(p.x, p.y)[0]
            if in_massif(srim, 3.0):
                s += w
                continue
            depth = rng.uniform(6.5, 10.0)
            out = rng.uniform(0.3, 2.0)
            m = tone()
            if rng.random() < 0.12 and w < 10.0:
                out, m = rng.uniform(-0.6, 0.2), DARK            # fresta: coluna recuada e escura
            top = level - LID_EPS
            lid = True
            q = rng.random()
            if q < 0.2:
                top -= rng.uniform(0.8, 2.8)                   # dente mais baixo (a grama cai um degrau)
            elif q < 0.28:
                lid = False
                top = level - rng.uniform(0.3, 0.9)             # crista de rocha nua
            if p.y < -110.0 and abs(p.x) - (abs(t.x) * w * 0.55 + abs(t.y) * depth) < L.BRIDGE_W / 2 + 1.4:
                top, lid = L.G - 2.8, False                      # por baixo do tabuleiro da ponte de chegada
            elif p.y < -108.0 and abs(p.x) < L.ENTRY_PLAZA[2] + 2.5:
                top, lid = L.G - 0.4, False                      # borda da praca do portao: abaixo do piso dela
            fk = fall_hit(srim, w * 0.52)
            if fk in SPILL_KEYS:
                top, lid = level - 1.3, False                    # sangria: a lamina passa por cima
                if fk == "SE":
                    top = min(top, L.STREAM_BED - 0.2)          # o leito do riacho do vale corta a borda ali
                if rng.random() < 0.5:
                    m = DARK
            left = Vector((-t.y, t.x, 0.0))
            a, b = w * 0.52, depth * 0.5
            if fk in SPILL_KEYS:
                out = min(out, SPILL_FACE - 0.25 * b)            # recua: a queda comeca 2,9 fora da borda
            elif fk == "DRAIN":
                out = min(out, DRAIN_MAX_OUT - 0.3 - 0.25 * b)   # galeria de drenagem a 2,6 da borda
            cc = p - left * (out - 0.88 * b)
            k = 0
            while not _fits(cc, t, a, b, top - 0.2) and k < 3:
                depth *= 0.7
                w *= 0.8
                a, b = w * 0.52, depth * 0.5
                cc = p - left * (out - 0.88 * b)
                k += 1
            if not _fits(cc, t, a, b, top - 0.2):
                top = min(top, L.G - LID_EPS)
            if _bed_hit(cc, t, a, b):
                top, lid = min(top, L.STREAM_BED - 0.2), False   # (integracao) coluna que invade o leito do riacho
            if _hits_box(cc, t, a, b, pod):
                s += w * 0.85                                    # o embasamento da casa leste e a face ali
                continue
            zb = Z_BOT + rng.uniform(-4.0, 2.5)
            h = top - zb
            if h > 16.0:
                # trinca horizontal: base saliente (ou recuada) ate uma cota propria, corpo por cima
                zm = zb + h * rng.uniform(0.3, 0.62)
                ob = out + rng.uniform(-0.6, 2.0)
                if fk in SPILL_KEYS or fk == "DRAIN":
                    ob = min(ob, out)
                column(mb, p, t, ob, w * rng.uniform(0.94, 1.08), depth, zb, zm, rng,
                       m=DARK if rng.random() < 0.45 else tone(), lid=(ob > out + 0.9 and rng.random() < 0.5),
                       taper=rng.uniform(0.96, 1.02), tongues=1)
                column(mb, p, t, out, w, depth, zm - 0.8, top, rng, m=m, lid=lid, taper=rng.uniform(0.88, 0.96),
                       tongues=rng.randint(0, 2))
                ncol += 2
            else:
                column(mb, p, t, out, w, depth, zb, top, rng, m=m, lid=lid, tongues=rng.randint(0, 2))
                ncol += 1
            if rng.random() < 0.32 and w < total - s:
                s += w + rng.uniform(0.7, 1.3)                   # fresta escura de ~1 ate a proxima
            else:
                s += w * rng.uniform(0.8, 0.9) if w < total - s else w
    mb.finish()
    # fresta de chao G entre o terraco T2 (x <= 118) e a borda leste: colisao fecha a fresta no nivel do T2, so onde
    # o T2 existe (y >= 132,85: o canto x 108..118 / y 126..133 e vale, sob a ponte de saida) e FORA do corredor da
    # ponte de saida (|lateral| >= 9,5 do eixo de 45 graus: y - x >= 13,44)
    y0 = 118.0 - L.T2_EXIT_CUT
    col_box2("TerrainRock", (118.0, y0, L.G - 1.0), (119.4, 149.0, L.T2))
    col_box2("TerrainRock", (119.4, 135.5, L.G - 1.0), (121.9, 149.0, L.T2))
    return ncol


# ------------------------------------------------------------------ prateleira + penhasco baixo (-> mar)
LOW_BOT = (-100.0, -60.0)             # fundos pendurados (afunilados) do penhasco baixo
DETACH_P = 0.2                        # fracao das colunas externas destacadas (vao de ar/mar)
# promontorios: nome, ponto da borda (aprox), A2 (meia largura na borda), D2 (avanco), A1, D1 (patamar de cima)
PROMS = [
    ("W", (-155.8, 20.0), 25.0, 22.0, 16.0, 12.5),     # sob o summon (a oeste)
    ("SE", (137.9, -27.0), 23.0, 20.0, 15.0, 12.0),    # sob o vale (a casa leste fica no patamar G-10)
    ("SW", (-46.0, -107.8), 20.0, 19.0, 13.0, 11.0),   # ao lado da ponte de chegada
]
PROM_Z = (L.G - 10.0, L.G - 20.0)
# baias: trechos da borda (s ao longo do contorno) onde o penhasco baixo NAO avanca (parede lisa ate o mar): os
# flancos de cada promontorio (ele se destaca) e 3 trechos soltos; rampa suave de BAY_RAMP nas pontas
BAYS_EXTRA = [(70.0, 92.0), (262.0, 282.0), (880.0, 902.0)]
BAY_FLANK = (3.0, 20.0)
BAY_RAMP = 6.0
# penhasco baixo em LOBULOS: grupos de colunas com topo comum (degraus legiveis), cotas relativas a G
LOBE_LEN = (22.0, 40.0)
LOBE_DZ = (-6.0, -9.5, -14.5, -19.0, -26.0)


def offset_closed(poly, d):
    """contorno fechado deslocado d para FORA (d < 0: para dentro), juntas em esquadria limitada"""
    P = IL.ccw(poly)
    n = len(P)
    out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        l1 = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        l2 = math.hypot(c[0] - b[0], c[1] - b[1]) or 1.0
        n1 = ((b[1] - a[1]) / l1, -(b[0] - a[0]) / l1)
        n2 = ((c[1] - b[1]) / l2, -(c[0] - b[0]) / l2)
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        ml = math.hypot(mx, my)
        if ml < 1e-6:
            mx, my, ml = n1[0], n1[1], 1.0
        mx, my = mx / ml, my / ml
        k = d / max(mx * n1[0] + my * n1[1], 0.5)
        out.append((b[0] + mx * k, b[1] + my * k))
    return out


def lobe(c, t, n, A, D, rng, k=16, back=6.0, e=2.4, jit=0.06):
    """contorno de um lobulo (promontorio): base 'back' para dentro da borda, arco em superelipse ate D para fora.
    Devolve (poligono anti-horario, arco no sentido anti-horario = normal para fora a direita)"""
    arc = []
    for i in range(k + 1):
        th = i / k * math.pi
        cth, sth = math.cos(th), math.sin(th)
        rr = (abs(cth) ** e + abs(sth) ** e) ** (-1.0 / e)
        j = 1.0 + rng.uniform(-jit, jit) * (1.0 if 0 < i < k else 0.0)
        p = c + t * (A * cth * rr * j) + n * (D * sth * rr * j)
        arc.append((p.x, p.y))
    arc.reverse()                                      # de -t para +t passando pela ponta: anti-horario
    a0 = c - t * (A * 1.02) - n * back
    a1 = c + t * (A * 1.02) - n * back
    poly = [(a0.x, a0.y)] + arc + [(a1.x, a1.y)]
    return IL.ccw(poly), arc


_PROM = []


def prom_shapes():
    """(nome, centro na borda, tangente, normal, poligono G-20, arco G-20, poligono G-10, arco G-10) - fixo"""
    if not _PROM:
        import random
        for i, (name, p, A2, D2, A1, D1) in enumerate(PROMS):
            rng = random.Random(4100 + i)
            s, q, nrm, d = rim_param(*p)
            c = Vector((q[0], q[1], 0.0))
            n = Vector((nrm[0], nrm[1], 0.0))
            t = Vector((-nrm[1], nrm[0], 0.0))
            p2, a2 = lobe(c, t, n, A2, D2, rng)
            p1, a1 = lobe(c, t, n, A1, D1, rng, k=12)
            _PROM.append((name, c, t, n, p2, a2, p1, a1, offset_closed(p2, 3.0)))
    return _PROM


def in_prom(x, y):
    return any(fm_lib.point_in_poly(x, y, sh[8]) for sh in prom_shapes())


_BAYS = []


def bays():
    if not _BAYS:
        for sh, (name, p, A2, D2, A1, D1) in zip(prom_shapes(), PROMS):
            sc = rim_param(sh[1].x, sh[1].y)[0]
            _BAYS.append((sc - A2 - BAY_FLANK[1], sc - A2 - BAY_FLANK[0]))
            _BAYS.append((sc + A2 + BAY_FLANK[0], sc + A2 + BAY_FLANK[1]))
        _BAYS.extend(BAYS_EXTRA)
    return _BAYS


def bay_factor(s):
    """0 = lobulo normal, 1 = baia (o penhasco baixo encosta na borda)"""
    T = _rim()["total"]
    k = 0.0
    for s0, s1 in bays():
        for sh in (-T, 0.0, T):
            a, b = s0 + sh, s1 + sh
            if a - BAY_RAMP < s < b + BAY_RAMP:
                u = min(1.0, (s - (a - BAY_RAMP)) / BAY_RAMP, ((b + BAY_RAMP) - s) / BAY_RAMP)
                k = max(k, u * u * (3.0 - 2.0 * u))
    return k


def lower_outline():
    """contorno do penhasco baixo: L.SHELF_RIM (lobulos 9-20 fora) com enseadas nas quedas e as baias puxadas ate
    1,5 fora da borda"""
    out = []
    for p in shelf_poly():
        s, q, nrm, d = rim_param(*p)
        k = bay_factor(s)
        if k > 0.0:
            tx, ty = q[0] + nrm[0] * 1.5, q[1] + nrm[1] * 1.5
            p = (p[0] + (tx - p[0]) * k, p[1] + (ty - p[1]) * k)
        out.append(p)
    return out


def promontories(rng):
    """3 promontorios em 2 patamares (G-10 junto a borda, G-20 avancando 15-25): colunas no contorno (tom por
    coluna, tampa de grama), miolo com topo PLANO de grama (a vegetacao e da integracao), ~20% das colunas
    externas destacadas 3-6 com vao de ar/mar"""
    mb = MB("TER_Promontories", C, rng, detail="near")
    tone = Tones(rng)
    pod = podium_box(0.2)
    z1, z2 = PROM_Z
    n = 0
    for name, c, t, nrm, p2, a2, p1, a1, _ in prom_shapes():
        IL.prism(mb, offset_closed(p2, -1.4), z2 - 8.0, z2, DARK, GRASS)
        IL.prism(mb, offset_closed(p1, -1.4), z1 - 7.0, z1, DARK, GRASS)
        for arc, ztop, z0, wr, dp, low in ((a2, z2, None, (5.5, 11.0), (7.0, 10.0), True),
                                           (a1, z1, z2 - 6.0, (5.0, 9.0), (6.0, 8.0), False)):
            total, at = walker(arc)
            s = 0.0
            while s < total - 0.5:
                w = rng.uniform(*wr)
                if total - s - w < 3.0:
                    w = total - s
                p, tt = at(s + w * 0.5, 2.0)
                depth = rng.uniform(*dp)
                if _hits_box(p - Vector((tt.y, -tt.x, 0.0)) * (depth * 0.4), tt, w * 0.5, depth * 0.5, pod):
                    s += w * 0.85                                # o embasamento da casa leste ocupa ali
                    continue
                out = rng.uniform(0.2, 1.1)
                m = tone() if rng.random() > 0.1 else DARK
                top = ztop - LID_EPS - (rng.uniform(1.2, 2.6) if rng.random() < 0.12 else 0.0)
                if low:
                    zb1 = -50.0 + rng.uniform(-10.0, 8.0)
                    column(mb, p, tt, out + rng.uniform(0.8, 2.2), w * rng.uniform(0.95, 1.08), depth, L.SEA - 4.0,
                           zb1, rng, m=DARK if rng.random() < 0.45 else tone(), lid=False, rings=1,
                           taper=rng.uniform(1.0, 1.08))
                    column(mb, p, tt, out, w, depth, zb1 - 0.8, top, rng, m=m, lid=True, rings=2,
                           tongues=rng.randint(0, 2))
                    n += 2
                    if rng.random() < DETACH_P:
                        nout = Vector((tt.y, -tt.x, 0.0))
                        pd = p + nout * rng.uniform(3.0, 6.0) + tt * rng.uniform(-1.0, 1.0)
                        zt = ztop - rng.uniform(4.0, 12.0)
                        hang = rng.random() < 0.4
                        column(mb, pd, tt, 0.0, w * rng.uniform(0.45, 0.7), rng.uniform(4.5, 6.5),
                               rng.uniform(*LOW_BOT) if hang else L.SEA - 4.0, zt, rng, m=tone(),
                               lid=rng.random() < 0.75, bot=rng.uniform(0.3, 0.55) if hang else 1.0, tongues=1)
                        n += 1
                else:
                    column(mb, p, tt, out, w, depth, z0, top, rng, m=m, lid=True, tongues=rng.randint(0, 2))
                    n += 1
                s += w * rng.uniform(0.82, 0.92) if w < total - s else w
    mb.finish()
    return n


def core(rng):
    """nucleo escuro da ilha: fundo das frestas e dos fundos pendurados (a borda recuada 1,2, do mar ate logo abaixo
    dos gramados, que ficam em L.SHELF_Z - 1)"""
    mb = MB("TER_Cliff_Core", C, rng, detail="far", floor=L.SEA - 4.0)
    mb.prism(IL.ccw(offset_closed(IL.rim(), -1.2)), L.SEA - 4.0, L.SHELF_Z - 1.2, DARK, 0.0)
    mb.finish()


def shelf_and_lower(rng):
    """penhasco baixo: colunas dos lobulos (L.SHELF_RIM, 9-20 fora da borda) do mar ate o topo, tampo de grama em
    cotas variadas, 2 faixas de saliencia (~-38 e ~-78) e fundos variados: parte das colunas termina pendurada e
    afunilada entre -60 e -110 (o nucleo escuro, recuado, aparece atras); ~20% destacadas 3-6 para fora; enseadas
    recuadas nas 4 quedas; nada no trecho do paredao nem sob os promontorios (que tem colunas proprias)"""
    core(rng)
    promontories(rng)
    sp = lower_outline()
    mb = MB("TER_Cliffs_Lower", C, rng, detail="far")
    tone = Tones(rng)
    closed = list(sp) + [sp[0]]
    total, at = walker(closed)
    ncol = 0
    s = 0.0
    zlow = L.SEA - 4.0
    lobe_end, lobe_dz = -1.0, None
    lobe = []                                                # colunas do lobulo atual: (s0, s1, topo)

    def flush():
        """miolo do lobulo: topo PLANO de grama entre as colunas do contorno e o pe do penhasco de cima"""
        if len(lobe) < 2:
            lobe.clear()
            return
        sa, sb = min(c[0] for c in lobe) + 0.8, max(c[1] for c in lobe) - 0.8
        z = min(c[2] for c in lobe) + LID_EPS
        lobe.clear()
        if sb - sa < 4.0:
            return
        k = max(2, int((sb - sa) / 3.0))
        outer, inner = [], []
        for i in range(k + 1):
            pp, tt = at(sa + (sb - sa) * i / k, 2.0)
            nout = Vector((tt.y, -tt.x, 0.0))
            o = pp - nout * 0.9
            s_, qq, qn, dd = rim_param(pp.x, pp.y)
            outer.append((o.x, o.y))
            inner.append((qq[0] - qn[0] * 1.5, qq[1] - qn[1] * 1.5))
        IL.prism(mb, outer + inner[::-1], z - 8.0, z, DARK, GRASS)
    while s < total - 1.0:
        if s >= lobe_end:                                    # novo lobulo: topo comum, cota diferente da anterior
            flush()
            lobe_end = s + rng.uniform(*LOBE_LEN)
            lobe_dz = rng.choice([d for d in LOBE_DZ if d != lobe_dz])
        w = _width(rng, (6.0, 9.5), (12.0, 18.0), 0.45)
        if total - s - w < 5.0:
            w = total - s
        sc = s + w * 0.5
        p, t = at(sc, 3.0)
        srim, q, qn, dsg = rim_param(p.x, p.y)
        if in_massif(srim, 6.0) or in_prom(p.x, p.y):
            flush()
            s += 3.0
            continue
        fk = fall_hit(srim, w * 0.5, COVE_HW)
        if fk is not None:
            flush()
            # enseada: coluna recuada rente a borda, do mar ate o pe das colunas de cima (a queda passa na frente)
            tq = Vector((-qn[1], qn[0], 0.0))
            pq = Vector((q[0], q[1], 0.0))
            wc = min(w, 8.0)
            b = rng.uniform(6.0, 8.0) * 0.5
            face = 0.9 if fk == "DRAIN" else SPILL_FACE
            column(mb, pq, tq, face - 0.25 * b - rng.uniform(0.0, 0.8), wc, b * 2.0, zlow,
                   Z_BOT + rng.uniform(1.0, 4.0), rng, m=DARK if rng.random() < 0.5 else tone(), lid=False,
                   rings=2, taper=rng.uniform(0.95, 1.02))
            ncol += 1
            s += wc * rng.uniform(0.75, 0.9)
            continue
        dr = max(0.0, dsg)
        lvl = ground(q[0] - (p.x - q[0]) * 0.3, q[1] - (p.y - q[1]) * 0.3)
        bay = bay_factor(srim) > 0.5 or dr < 4.0
        lid_ok = not bay
        dent = False
        if bay:
            flush()
            ztop = Z_BOT + rng.uniform(1.0, 4.0)                   # baia: a parede segue lisa ate o mar
        else:
            ztop = L.G + lobe_dz - LID_EPS
            if lvl > L.G + 1.0 and lobe_dz > -8.0:
                ztop = min(lvl - 6.0, L.SHELF_Z + 30.0) - LID_EPS  # mesa alta diante do terraco
            dent = rng.random() < 0.12
            if dent:
                ztop -= rng.uniform(1.0, 2.5)                      # dente: a grama da borda cai um degrau
        clamped = ztop > lvl - 2.2
        ztop = min(ztop, lvl - 2.2)
        if not (bay or dent or clamped):
            lobe.append((sc - w * 0.45, sc + w * 0.45, ztop))
        if p.y < -112.0 and abs(p.x) < L.BRIDGE_W / 2 + 3.0:
            ztop = min(ztop, L.G - 3.0)                          # abaixo do tabuleiro da ponte de chegada
        depth = max(7.0, dr + rng.uniform(2.0, 5.0))           # o lobulo vai ate debaixo do penhasco de cima
        o0 = rng.uniform(0.0, 1.8)
        m = tone()
        if rng.random() < 0.12 and w < 10.0:
            o0, m = o0 - 1.4, DARK
        b1 = -38.0 + rng.uniform(-7.0, 7.0)
        b2 = -78.0 + rng.uniform(-8.0, 6.0)
        o1 = o0 + rng.uniform(-0.8, 2.4)
        o2 = o1 + rng.uniform(-1.8, 0.6)
        brk1 = rng.random() > 0.3
        brk2 = rng.random() > 0.3
        hang = rng.random() < 0.38                           # fundo pendurado, afunilado (-60..-100)
        zh = rng.uniform(*LOW_BOT)
        if hang:
            brk2 = False
            if brk1 and zh > b1 - 8.0:
                zh = b1 - rng.uniform(10.0, 20.0)
        z_a = (b1 - 0.6) if brk1 else ((b2 - 0.6) if brk2 else (zh if hang else zlow))
        column(mb, p, t, o0, w, depth, z_a, ztop, rng, m=m, lid=lid_ok and rng.random() < 0.92,
               rings=(1 if ztop - z_a < 45 else 2), taper=rng.uniform(0.92, 0.99), tongues=rng.randint(0, 2),
               bot=(rng.uniform(0.3, 0.55) if (hang and not brk1) else 1.0))
        ncol += 1
        if brk1:
            z_b = (b2 - 0.6) if brk2 else (zh if hang else zlow)
            column(mb, p, t, o1, w * rng.uniform(0.92, 1.06), depth, z_b, b1, rng,
                   m=DARK if rng.random() < 0.4 else tone(), lid=(o1 > o0 + 1.0 and rng.random() < 0.45),
                   rings=1, taper=rng.uniform(0.97, 1.04), tilt=0.05, bot=(rng.uniform(0.3, 0.55) if hang else 1.0))
            ncol += 1
        if brk2:
            column(mb, p, t, o2, w * rng.uniform(0.9, 1.05), depth, zlow, b2, rng,
                   m=DARK if rng.random() < 0.55 else tone(), lid=False, rings=1,
                   taper=rng.uniform(1.05, 1.16), tilt=0.06, n=rng.choice((5, 6)))
            ncol += 1
        # coluna externa destacada: 3-6 para fora, mais baixa, vao de ar/mar entre ela e o lobulo
        under_bridge = p.y < -108.0 and abs(p.x) < L.BRIDGE_W / 2 + 8.0
        if rng.random() < DETACH_P and not (under_bridge or bay) and fall_hit(srim, w, COVE_HW + 4.0) is None:
            nout = Vector((t.y, -t.x, 0.0))
            pd = p + nout * (o0 + rng.uniform(3.0, 6.0)) + t * rng.uniform(-w * 0.2, w * 0.2)
            zt = ztop - rng.uniform(3.0, 10.0)
            dh = rng.random() < 0.4
            column(mb, pd, t, 0.0, w * rng.uniform(0.4, 0.65), rng.uniform(4.0, 6.5),
                   rng.uniform(*LOW_BOT) if dh else zlow, zt, rng, m=tone(), lid=rng.random() < 0.75,
                   rings=2, bot=(rng.uniform(0.3, 0.5) if dh else 1.0), tongues=1)
            ncol += 1
        s += w * rng.uniform(0.8, 0.9) if w < total - s else w
    flush()
    mb.finish()
    return ncol


# ------------------------------------------------------------------ paredao do fundo (rodada 2: curvo, em patamares)
# Face (para a vila) acompanhando a borda de (-150,120) a (116,160): nas alas a face fica 0,6 fora da borda; no centro
# e o pe do paredao em y = L.BACK_CLIFF_Y (186). Para tras (para fora da ilha) o macico vai ate BACK_OUT fora da
# borda. Patamares: A = 64 (frente, recuo de 8-13 ate B), B = plato em 72 (construcoes de cima: 2 a oeste x -70..-50,
# 1 pagode a leste x ~55, y 198-215), C = 84 so no centro (x -20..34, recuo 8-12 atras de B). Colunas frontais de
# cada patamar sobem 6-18 acima dele (menos na frente das construcoes). As alas so tem o patamar A e descem em degraus
# nas pontas. 3 sulcos (L.BACK_FALLS): garganta escura de GORGE_D com a coluna de fundo em L.CLIFF_TOP - 0,3.
H_A = 64.0
H_B = L.CLIFF_TOP - LID_EPS          # 71,88: 0,12 abaixo do plato do il_terrain (sem z-fight se ele existir)
H_C = 84.0
BACK_OUT = 10.5                       # face de tras do paredao: fora da borda (a base saliente chega a ~12)
WING_FACE = 0.6                       # face das alas: fora da borda (a guarda invisivel fica na borda)
UPPER_SITES = [(-76.0, -44.0), (39.0, 71.0)]    # faixas x das construcoes de cima: patamar B plano e livre
SITE_BACK_Y = 216.8                   # ali o plato vai ate y 216 (sai da planta: permitido so nessas areas)
TIER_C_X = (-20.0, 34.0)
GORGE_HW = 7.25          # (integracao) quedas do fundo com 14 de largura
GORGE_D = 7.0
MASSIF_CORE_Z = 40.0                  # nucleo escuro do paredao ate aqui; os miolos dos patamares descem ate ele
MASSIF_RAW = [(-150.0, 120.0), (-134.0, 160.0), (-108.0, 186.0), (102.13, 186.0), (116.0, 160.0)]


def _path():
    """face do paredao (oeste -> leste) reamostrada, alas deslocadas WING_FACE para fora; devolve (comprimento, at,
    u das 2 juncoes ala/centro)"""
    raw = [Vector((p[0], p[1], 0.0)) for p in MASSIF_RAW]
    seg = [(a, b, (b - a).length) for a, b in zip(raw, raw[1:])]
    uj = (seg[0][2] + seg[1][2], seg[0][2] + seg[1][2] + seg[2][2])
    pts = []
    u = 0.0
    for k, (a, b, ln) in enumerate(seg):
        n = max(1, int(ln / 0.5))
        for i in range(n + (1 if k == len(seg) - 1 else 0)):
            pts.append((a + (b - a) * (i / n), u + ln * i / n))
        u += ln
    out = []
    for i, (p, uu) in enumerate(pts):
        a = pts[max(0, i - 3)][0]
        b = pts[min(len(pts) - 1, i + 3)][0]
        d = (b - a).normalized()
        nl = Vector((-d.y, d.x, 0.0))
        wgt = 1.0 - min(1.0, max(0.0, min(uu - (uj[0] - 3.0), (uj[1] + 3.0) - uu) / 4.0))
        q = p + nl * (WING_FACE * wgt)
        out.append((q.x, q.y))
    total, at = walker(out)
    return total, at, uj


def _back_d(F, N):
    """distancia ao longo de N ate o paredao ficar BACK_OUT fora da borda"""
    lo = 0.0
    d = 0.0
    while d < 80.0:
        q = F + N * d
        if rim_param(q.x, q.y)[3] >= BACK_OUT:
            break
        lo = d
        d += 1.0
    hi = d
    for _ in range(6):
        mid = (lo + hi) * 0.5
        q = F + N * mid
        if rim_param(q.x, q.y)[3] >= BACK_OUT:
            hi = mid
        else:
            lo = mid
    return hi


def _near_site(x, pad):
    return any(a - pad <= x <= b + pad for a, b in UPPER_SITES)


def _near_gorge(x, pad):
    return any(abs(x - fx) < GORGE_HW + pad for fx, _ in L.BACK_FALLS)


class Massif:
    def __init__(self, rng):
        from mathutils import noise
        self.total, self.at, self.uj = _path()
        self.sd = rng.uniform(0.0, 100.0)
        self.noise = noise
        self._cache = {}

    def nz(self, u, k):
        return self.noise.noise(Vector((u * 0.05 + self.sd + 11.0 * k, self.sd * 0.3, 0.7)))

    def center(self, u):
        return self.uj[0] + 1.0 < u < self.uj[1] - 1.0

    def u_of_x(self, x):
        """u do trecho central (face em y 186) cuja face passa por x"""
        lo, hi = self.uj[0], self.uj[1]
        for _ in range(30):
            mid = (lo + hi) * 0.5
            if self.at(mid)[0].x < x:
                lo = mid
            else:
                hi = mid
        return (lo + hi) * 0.5

    def prof(self, u):
        """perfil na posicao u: F, T, N (para fora), fundo, dA (inicio do patamar B), dC (ou None), altura de A"""
        key = round(u, 2)
        if key in self._cache:
            return self._cache[key]
        F, T = self.at(u, 1.5)
        N = Vector((-T.y, T.x, 0.0))
        back = _back_d(F, N)
        x = F.x
        if self.center(u):
            # construcoes de cima: o plato plano pode sair da planta ate y 216 (casas em y 198-215)
            dist = min([max(0.0, a - x, x - b) for a, b in UPPER_SITES])
            wgt = min(1.0, max(0.0, 1.0 - (dist - 4.0) / 6.0))
            ext = (SITE_BACK_Y - F.y) / max(N.y, 0.3)
            if wgt > 0.0 and ext > back:
                back += (ext - back) * wgt
        dA = back
        if self.center(u) and back >= 17.0:
            dA = min(13.0, max(8.0, 10.0 + 3.0 * self.nz(u, 1)))
            if _near_site(x, 3.0):
                dA = min(dA, 10.5)
            if back - dA < 5.0:
                dA = back
        dC = None
        if dA < back and TIER_C_X[0] < x < TIER_C_X[1]:
            ramp = min(1.0, (x - TIER_C_X[0]) / 8.0, (TIER_C_X[1] - x) / 8.0)
            dc = dA + 10.0 + 2.0 * self.nz(u, 2)
            dc += (1.0 - ramp) * (back - dc)
            if back - dc >= 5.0:
                dC = dc
        e = min(u, self.total - u)
        hA = H_A if e > 25.0 else (57.0 if e > 12.0 else 50.0)
        r = (F, T, N, back, dA, dC, hA)
        self._cache[key] = r
        return r


def _face_col(mb, P, fdir, w, depth, z0, z1, rng, m, lid=True, flush=0.3, **kw):
    """coluna com a face virada para fdir e rente ao ponto P (a pegada fica atras de P; flush = recuo/fundo)"""
    t = Vector((-fdir.y, fdir.x, 0.0))
    b = depth * 0.5
    return column(mb, P, t, -flush * b, w, depth, z0, z1, rng, m=m, lid=lid, **kw)


def _fill(mb, M, u0, u1, d0f, d1f, z):
    """miolo de um patamar entre u0 e u1: quadrilatero entre as profundidades d0f(prof) e d1f(prof), topo de grama"""
    a, b = M.prof(u0), M.prof(u1)
    da0, da1 = d0f(a), d1f(a)
    db0, db1 = d0f(b), d1f(b)
    if da0 is None or db0 is None or da1 - da0 < 1.0 or db1 - db0 < 1.0:
        return
    pts = [a[0] + a[2] * da0, b[0] + b[2] * db0, b[0] + b[2] * db1, a[0] + a[2] * da1]
    IL.prism(mb, [(p.x, p.y) for p in pts], MASSIF_CORE_Z - 1.0, z, DARK, GRASS)


def back_massif(rng):
    """paredao do fundo curvo em 3 patamares com os 3 sulcos das quedas (ver o cabecalho da secao)"""
    mb = MB("TER_Back_Massif", C, rng, detail="near")
    M = Massif(rng)
    tone = Tones(rng)
    total = M.total
    n = 0
    zT2 = L.T2 - 1.0
    # ---- miolos (topos planos de grama) em faixas de ~5 ao longo da face
    k = max(2, int(total / 5.0))
    cuts = sorted(set([total * i / k for i in range(k + 1)] +
                      [M.u_of_x(fx + s * GORGE_HW) for fx, _ in L.BACK_FALLS for s in (-1, 1)]))
    for u0, u1 in zip(cuts, cuts[1:]):
        if u1 - u0 < 0.02:
            continue
        um = M.prof((u0 + u1) * 0.5)
        gorge = M.center(u0) and _near_gorge(um[0].x, 0.0)
        # cada miolo passa por baixo da fileira frontal do patamar seguinte (sem fresta aberta ate o mar)
        # (os miolos vao todos ate o fundo: o de baixo fica escondido dentro do corpo do de cima)
        if not gorge:
            _fill(mb, M, u0, u1, lambda p: 1.2, lambda p: p[3] - 1.5, um[6])
        _fill(mb, M, u0, u1, lambda p: (p[4] + 1.2) if p[4] < p[3] else None, lambda p: p[3] - 1.5, H_B)
        _fill(mb, M, u0, u1, lambda p: (p[5] + 1.2) if p[5] is not None else None, lambda p: p[3] - 1.5, H_C)
    # ---- nucleo escuro do paredao (nada vaza pelas frestas ate o mar): faixa 2 atras da face ate 2 antes do fundo,
    #      do mar ate logo abaixo dos miolos; recuado ate o fundo das gargantas nos sulcos
    inner, outer = [], []
    k2 = max(2, int(total / 4.0))
    for i in range(k2 + 1):
        u = total * i / k2
        F, T, N, back, dA, dC, hA = M.prof(u)
        d_in = (GORGE_D + 0.6) if (M.center(u) and _near_gorge(F.x, 0.6)) else 2.0
        a, b = F + N * d_in, F + N * max(d_in + 1.0, back - 2.0)
        inner.append((a.x, a.y))
        outer.append((b.x, b.y))
    IL.prism(mb, inner + outer[::-1], L.SEA - 4.0, MASSIF_CORE_Z, DARK)
    # ---- frente do patamar A (do chao do T2/T1 ate 64; colunas frontais +6..18; alas em degraus nas pontas)
    u = 0.0
    while u < total - 0.5:
        w = _width(rng, (5.5, 9.0), (10.0, 15.0), 0.4)
        if total - u - w < 4.0:
            w = total - u
        F, T, N, back, dA, dC, hA = M.prof(u + w * 0.5)
        x = F.x
        if M.center(u + w * 0.5) and _near_gorge(x, w * 0.5 + 0.3):
            u += 1.5
            continue
        q = rng.random()
        crag_hi = 7.0 if _near_site(x, 5.0) else 18.0
        if q < 0.34 and hA >= H_A - 0.1:
            top, lid = hA + rng.uniform(6.0, crag_hi), rng.random() < 0.6
            w = max(w, rng.uniform(7.0, 9.5))                    # coluna frontal alta: bloco, nao agulha
        elif q < 0.5:
            top, lid = hA - rng.uniform(1.5, 4.0), True
        else:
            top, lid = hA - LID_EPS, True
        zf = ground(F.x - N.x * 2.5, F.y - N.y * 2.5) - 1.0
        m = DARK if rng.random() < 0.1 else tone()
        dep = min(dA + 1.5, 10.0)
        P = F + N * (rng.uniform(1.2, 2.8) if rng.random() < 0.15 else 0.0)     # algumas recuadas (sombra)
        if rng.random() < 0.6 and top - zf > 24.0:
            # trinca horizontal: base rente a face ate uma cota propria, corpo por cima recuado (estrato)
            zm = zf + (top - zf) * rng.uniform(0.35, 0.6)
            _face_col(mb, P, -N, w * rng.uniform(0.98, 1.06), dep, zf, zm, rng,
                      DARK if rng.random() < 0.35 else tone(), lid=rng.random() < 0.35, rings=1,
                      taper=rng.uniform(0.98, 1.02))
            _face_col(mb, P + N * rng.uniform(0.6, 1.8), -N, w, dep, zm - 0.8, top, rng, m, lid=lid,
                      tongues=rng.randint(0, 2), rings=2, taper=rng.uniform(0.9, 0.97))
            n += 2
        else:
            _face_col(mb, P, -N, w, dep, zf, top, rng, m, lid=lid, tongues=rng.randint(0, 2),
                      rings=3 if top - zf > 40 else 2, taper=rng.uniform(0.9, 0.97))
            n += 1
        u += w * rng.uniform(0.82, 0.9) if rng.random() > 0.3 else w + rng.uniform(0.6, 1.2)
    # ---- frente do patamar B (72) e do C (84), recuadas
    for tier in ("B", "C"):
        u = 0.0
        while u < total - 0.5:
            w = _width(rng, (5.5, 9.0), (10.0, 14.0), 0.4)
            F, T, N, back, dA, dC, hA = M.prof(u + w * 0.5)
            d = dA if tier == "B" else dC
            if d is None or d >= back - 0.5 or (tier == "B" and _near_gorge(F.x, w * 0.5)):
                u += 2.0
                continue
            P = F + N * d
            base, h = (hA, H_B) if tier == "B" else (H_B, H_C)
            q = rng.random()
            if q < 0.3 and not _near_site(F.x, 6.0) and not _near_gorge(F.x, 8.0):
                top, lid = h + rng.uniform(6.0, 18.0 if tier == "C" else 14.0), rng.random() < 0.6
                w = max(w, rng.uniform(7.0, 9.5))
            elif q < 0.45:
                top, lid = h - rng.uniform(1.5, 3.0), True
            else:
                top, lid = h - LID_EPS, True
            dnext = (dC if (tier == "B" and dC is not None) else back) - d
            _face_col(mb, P, -N, w, min(dnext + 1.0, 9.0), base - 8.0, top, rng,
                      DARK if rng.random() < 0.1 else tone(), lid=lid, tongues=rng.randint(0, 2),
                      taper=rng.uniform(0.9, 0.97))
            n += 1
            u += w * rng.uniform(0.82, 0.9) if rng.random() > 0.3 else w + rng.uniform(0.6, 1.2)
    # ---- sulcos das quedas do fundo: garganta escura, coluna de fundo em CLIFF_TOP - 0,3, pilastras altas
    for fx, fy in L.BACK_FALLS:
        F, T, N, back, dA, dC, hA = M.prof(M.u_of_x(fx))
        Fx = Vector((fx, L.BACK_CLIFF_Y, 0.0))
        _face_col(mb, Fx + N * GORGE_D, -N, GORGE_HW * 2.0 + 2.0, max(dA - GORGE_D + 3.0, 5.0), zT2,
                  L.CLIFF_TOP - 0.3, rng, DARK, lid=False, band=False, rings=3, taper=0.99, n=6, ex=3.0)
        for s in (-1, 1):
            wf = rng.uniform(5.5, 7.0)
            Pf = Fx + T * (s * (GORGE_HW + wf * 0.5))
            _face_col(mb, Pf, -N, wf, dA + 1.0, zT2, H_B + rng.uniform(5.0, 12.0), rng, tone(),
                      lid=rng.random() < 0.5, rings=3, taper=0.95, tongues=1)
            n += 1
        # fundo da garganta (a queda cai ali; o gramado do T2 termina em y 186)
        mb.prism([(fx - GORGE_HW, L.BACK_CLIFF_Y - 0.4), (fx + GORGE_HW, L.BACK_CLIFF_Y - 0.4),
                  (fx + GORGE_HW, L.BACK_CLIFF_Y + GORGE_D + 0.6), (fx - GORGE_HW, L.BACK_CLIFF_Y + GORGE_D + 0.6)],
                 L.T2 - 6.0, L.T2 - 0.3, DARK, 0.0)
        n += 1
    # ---- pele de tras (para o mar): do mar ate o topo do patamar mais alto daquele trecho, base saliente
    u = 0.0
    while u < total - 0.5:
        w = _width(rng, (7.0, 10.0), (11.0, 16.0), 0.5)
        if total - u - w < 4.0:
            w = total - u
        F, T, N, back, dA, dC, hA = M.prof(u + w * 0.5)
        h = H_C if dC is not None else (H_B if dA < back else hA)
        P = F + N * back
        zb = rng.uniform(-45.0, 5.0)
        q = rng.random()
        if _near_site(F.x, 7.0) and h == H_B:
            q = 1.0                                          # atras das construcoes de cima: plato plano ate y 216
        top = h + rng.uniform(3.0, 12.0) if q < 0.3 else (h - rng.uniform(1.5, 4.0) if q < 0.45 else h - LID_EPS)
        m = tone()
        _face_col(mb, P + N * rng.uniform(1.0, 3.0), N, w * rng.uniform(0.95, 1.08), 9.0, L.SEA - 4.0, zb, rng,
                  DARK if rng.random() < 0.4 else tone(), lid=False, rings=2, taper=rng.uniform(1.0, 1.06))
        _face_col(mb, P, N, w, 9.0, zb - 0.8, top, rng, m, lid=top < h, rings=3, tongues=rng.randint(0, 2),
                  taper=rng.uniform(0.97, 1.0), flush=0.22)
        n += 2
        u += w * rng.uniform(0.76, 0.84)                     # pele fechada (o miolo escuro nao aparece)
    # ---- lobulos do lado do mar: grupos de colunas saindo 6-12 da pele de tras com topo de grama em cotas variadas
    #      (quebram a parede lisa de 180 vista do norte); ~30% do comprimento fica liso
    u = rng.uniform(0.0, 8.0)
    zprev = None
    while u < total - 8.0:
        ln = rng.uniform(16.0, 30.0)
        if rng.random() < 0.3:
            u += ln
            continue
        zt = rng.choice([z for z in (-26.0, -10.0, 6.0, 22.0) if z != zprev])
        zprev = zt
        dd = rng.uniform(6.0, 12.0)
        uu = u
        while uu < min(u + ln, total - 3.0):
            w = rng.uniform(6.0, 11.0)
            F, T, N, back, dA, dC, hA = M.prof(uu + w * 0.5)
            hang = rng.random() < 0.3
            _face_col(mb, F + N * (back + dd + rng.uniform(-1.0, 1.0)), N, w, dd + 3.0,
                      rng.uniform(*LOW_BOT) if hang else L.SEA - 4.0, zt + rng.uniform(-0.6, 0.4) - LID_EPS, rng,
                      tone(), lid=True, rings=2, tongues=1, bot=rng.uniform(0.35, 0.55) if hang else 1.0)
            n += 1
            uu += w * rng.uniform(0.8, 0.9)
        u += ln + rng.uniform(4.0, 10.0)
    # ---- pontas: 2 colunas atravessando o fundo, viradas para fora da ponta (a borda segue com as colunas comuns)
    for u, sgn in ((0.0, -1.0), (total, 1.0)):
        F, T, N, back, dA, dC, hA = M.prof(u)
        for f in (0.26, 0.74):
            P = F + N * (back * f) + T * (sgn * 0.8)
            zb = rng.uniform(-40.0, -10.0)
            wcap = back * 0.56
            _face_col(mb, P + T * (sgn * 1.5), T * sgn, wcap, 8.0, L.SEA - 4.0, zb, rng, DARK, lid=False, rings=2,
                      taper=1.04)
            _face_col(mb, P, T * sgn, wcap, 8.0, zb - 0.8, hA - LID_EPS - rng.uniform(0.0, 3.0), rng, tone(),
                      lid=True, rings=3, tongues=1)
            n += 2
    mb.finish()
    return n
