# db_veg_kit - kit de vegetacao da Ilha 2 (Dragon Ball), zona "dressing" / vegetacao (prefixo DB_Veg_).
# Cartoon tropical da concept aprovada: palmeiras de coroa cheia (folhas arqueadas e pontudas, 2 verdes), moitas
# redondas low-poly (topo iluminado lima, fundo verde escuro), flores quentes pousadas nas moitas, tufos de laminas,
# rochas de arenito no estilo do db_terrain_rock (prisma facetado com faixa de topo clara, as vezes tampo de grama),
# canteiros em BOLHA MACIA levantados como monte baixo com orla chanfrada (+ moitinhas e tufos de laminas na orla),
# manchas de terra rachada, arvores de sombra de copa redonda (NAO sakura, NAO pinheiro), floreiras Capsule (brancas,
# faixa azul) e as versoes LEVES (so de longe) de folhosa/palmeira/moita para o topo das mesas.
# Primitivas de malha do fm_veg_kit (blob, tier, ttube, spike, blossom, grass_tuft) com a paleta DB.
# Materiais: base (Bark, Leaf_Palm, Leaf_Pine_Light, Grass_DB(_B), Dirt_DB, Cliff_Rock_DB*, Plaster_DB_White,
# Roof_DB_Blue, Stone_DB_Block, Flower_White) + 3 novos (Leaf_DBVegLime, Leaf_DBVegDeep, Leaf_DBVegBloom).
import math, random
from mathutils import Vector, noise
import fm_lib
from fm_lib import S
import fm_veg_kit as VK
import fm_parts as FP
import db_lib as DL

# ------------------------------------------------------------------ materiais novos (3 de 3)
NEW_MATS = {
    "Leaf_DBVegLime": (S(150, 204, 82), 0.85, 0.0, 0, None, 0.06),     # topo iluminado das copas/moitas
    "Leaf_DBVegDeep": (S(46, 116, 56), 0.85, 0.0, 0, None, 0.08),      # verde escuro quente (fundo, folhas baixas)
    "Leaf_DBVegBloom": (S(255, 118, 64), 0.7, 0.0, 0, None, 0.04),     # flor coral/hibisco (acento quente)
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

LIME, DEEP, BLOOM = "Leaf_DBVegLime", "Leaf_DBVegDeep", "Leaf_DBVegBloom"
PALM, MID, BARK = "Leaf_Palm", "Leaf_Pine_Light", "Bark"
WHITE_F = "Flower_White"
GRASS, GRASS_B, DIRT = "Grass_DB", "Grass_DB_B", "Dirt_DB"
ROCK, DARK, TOP = "Cliff_Rock_DB", "Cliff_Rock_DB_Dark", "Cliff_Rock_DB_Top"
WHITE, BLUE, BLOCK = "Plaster_DB_White", "Roof_DB_Blue", "Stone_DB_Block"
TAU = math.tau

# paletas de moita: (cor principal, topo iluminado, fundo)
SHRUB_PAL = [(PALM, LIME, DEEP), (MID, LIME, DEEP), (DEEP, MID, DEEP), (PALM, LIME, DEEP), (MID, PALM, DEEP)]


def assign(mb, faces, m, uv=False):
    """material EXATO (sem sorteio de variante) + tinta; UV planar opcional (texturas de detalhe)"""
    VK._assign(mb, faces, m)
    if uv:
        mb._uv(faces, m)


def _face(mb, vs, out):
    try:
        out.append(mb.bm.faces.new(vs))
    except ValueError:
        pass


def gblob(mb, c, r, hz, m, rng, seg=6, under_m=DEEP, jit=0.12, squash=(1.0, 1.0), lit=None, lit_k=0.55, fan=True):
    """VK.blob (elipsoide facetado: equador em c, topo iluminado em 'lit', fundo em under_m) com o leque de baixo
    OPCIONAL: fan=False para bolotas APOIADAS no chao (o fundo nunca aparece: poupa seg tris). tris = 6*seg (5*seg)"""
    bm = mb.bm
    cx, cy, cz = c
    rot = rng.uniform(0, TAU)
    s0 = rng.random() * 50
    rings = []
    for li, (fz, fr) in enumerate(((-0.3, 0.74), (0.0, 1.0), (0.46, 0.8))):
        ring = []
        for i in range(seg):
            a = rot + (i + li * 0.5) * TAU / seg
            nn = noise.noise(Vector((math.cos(a) * 1.5 + s0, math.sin(a) * 1.5, li * 1.1)))
            k = fr * (1.0 + nn * jit * 2.0 + rng.uniform(-jit, jit))
            ring.append(bm.verts.new((cx + math.cos(a) * r * k * squash[0], cy + math.sin(a) * r * k * squash[1],
                                      cz + hz * fz + rng.uniform(-jit, jit) * hz * 0.3)))
        rings.append(ring)
    top = bm.verts.new((cx + rng.uniform(-0.1, 0.1) * r, cy + rng.uniform(-0.1, 0.1) * r, cz + hz * 0.82))
    low, side = [], []
    if fan:
        bot = bm.verts.new((cx, cy, cz - hz * 0.44))
        for i in range(seg):
            _face(mb, (rings[0][(i + 1) % seg], rings[0][i], bot), low)
    for li in range(2):
        r0, r1 = rings[li], rings[li + 1]
        for i in range(seg):
            j = (i + 1) % seg
            _face(mb, (r0[i], r0[j], r1[i]), side)
            _face(mb, (r0[j], r1[j], r1[i]), side)
    for i in range(seg):
        _face(mb, (rings[2][i], rings[2][(i + 1) % seg], top), side)
    if lit:
        on, off = VK._split_lit(side, Vector((cx, cy, cz)), lit_k)
        assign(mb, on, lit)
        assign(mb, off, m)
    else:
        assign(mb, side, m)
    if low:
        assign(mb, low, under_m or m)


def blade_tuft(mb, x, y, z, s, rng, m=PALM, n=3):
    """tufo de laminas em leque: cada lamina e um espeto de 3 lados SEM a tampa de baixo (enterrada): 3 tris"""
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        a = a0 + i * TAU / n + rng.uniform(-0.3, 0.3)
        d = s * rng.uniform(0.05, 0.25)
        b = Vector((x + math.cos(a) * d, y + math.sin(a) * d, z - 0.1))
        hh = s * rng.uniform(0.7, 1.25)
        lean = s * rng.uniform(0.25, 0.55)
        t = b + Vector((math.cos(a) * lean, math.sin(a) * lean, hh))
        VK.ttube(mb, [b, t], [s * 0.13, 0.0], m, n=3, cap0=False, cap1=False, tip=True, rot=a)


# ------------------------------------------------------------------ palmeira
def frond(mb, base, ang, ln, w, m, rng, lift=0.62, droop=0.38):
    """folha de palmeira em 3 lances (arqueia de verdade): sai de um ponto, sobe e abre ate o joelho (35%, a parte
    mais larga), segue e comeca a cair (68%) e cai ate a ponta ('droop' x ln abaixo da base). Secao TRIANGULAR fechada
    (vinco alto no meio, bordas caidas, barriga plana): le dos dois lados, inclusive de baixo. 12 tris"""
    d = Vector((math.cos(ang), math.sin(ang), 0.0))
    s = Vector((-d.y, d.x, 0.0))
    up = Vector((0.0, 0.0, 1.0))
    b = lift + droop

    def at(t):
        return base + d * (ln * t * (1.0 - 0.14 * t)) + up * (ln * (lift * t - b * t * t))

    secs = []
    for t, wf in ((0.35, 1.0), (0.68, 0.7)):
        c = at(t)
        ww = w * wf * rng.uniform(0.9, 1.1)
        sec = [c - s * ww * 0.5 - up * ww * 0.22, c + up * ww * 0.12, c + s * ww * 0.5 - up * ww * 0.22]
        secs.append([mb.bm.verts.new(p) for p in sec])
    root = mb.bm.verts.new(at(0.02))           # pe da folha num ponto (a secao de 0,3 x largura nao aparecia)
    tip = mb.bm.verts.new(at(1.0))
    faces = []
    for k in range(3):
        _face(mb, (root, secs[0][(k + 1) % 3], secs[0][k]), faces)
    for r0, r1 in zip(secs, secs[1:]):
        for k in range(3):
            k2 = (k + 1) % 3
            _face(mb, (r0[k], r0[k2], r1[k2], r1[k]), faces)
    last = secs[-1]
    for k in range(3):
        _face(mb, (last[k], last[(k + 1) % 3], tip), faces)
    assign(mb, faces, m)


def palm(mb, x, y, z, h, rng, lean=0.18, lean_dir=None, fronds=8, tr=0.62, leaf=PALM, low_leaf=DEEP):
    """palmeira cartoon de coroa CHEIA: tronco curvo afunilado (5 lados, pe alargado) + miolo escuro + 'fronds'
    folhas largas em 2 andares (as de cima em 'leaf', mais erguidas; as de baixo em 'low_leaf', mais caidas).
    ~140-150 tris (tronco de 3 lances sem tampa, folha de 12 tris). retorna (x, y) do topo e o raio do tronco no pe"""
    a = rng.uniform(0.0, TAU) if lean_dir is None else lean_dir
    ux, uy = math.cos(a), math.sin(a)
    pts, radii = [], []
    for i in range(4):
        t = i / 3.0
        off = lean * h * t * t
        pts.append(Vector((x + ux * off, y + uy * off, z - 0.45 + (h + 0.45) * t)))
        radii.append(tr * (1.55 if i == 0 else (1.18 - 0.42 * t)))
    # topo do tronco fica dentro do miolo: sem tampa
    VK.ttube(mb, pts, radii, BARK, n=5, cap0=False, cap1=False, rot=rng.uniform(0, TAU))
    top = pts[-1]
    VK.blob(mb, (top.x, top.y, top.z - 0.1), tr * 1.5, tr * 1.35, DEEP, rng, seg=4, under_m=DEEP, jit=0.1)
    rot = rng.uniform(0.0, TAU)
    ln0 = max(4.8, min(8.2, h * 0.5))
    for k in range(fronds):
        low = k % 2 == 1
        b = rot + k * TAU / fronds + rng.uniform(-0.18, 0.18)
        ln = ln0 * rng.uniform(0.88, 1.06) * (0.92 if low else 1.0)
        frond(mb, top + Vector((0.0, 0.0, 0.05 if low else 0.35)), b, ln, ln * rng.uniform(0.34, 0.4),
              low_leaf if low else leaf, rng, lift=(0.4 if low else 0.85) + rng.uniform(-0.08, 0.08),
              droop=(0.8 if low else 0.5) + rng.uniform(-0.06, 0.08))
    return (top.x, top.y), tr * 1.55


# ------------------------------------------------------------------ moitas, flores, tufos
def shrub(mb, x, y, z, s, rng, pal=None, seg=None, squash=None, lumps=None, flat=1.0):
    """moita redonda em COUVE-FLOR: 1 bolota principal + 1-3 bolotas menores coladas (a silhueta recortada le como
    folhagem, nao como pedra/gema). Corpo 'pal[0]', so as faces bem voltadas ao sol em 'pal[1]', fundo 'pal[2]'.
    Apoiada no chao (fundo ~0,1 abaixo de z; sem o leque de baixo, que nunca aparece). Facetas pelo tamanho: 6/5
    lados na moita grande (>= 1,8), 5/4 na pequena (~25-30 + 20-25 por bolota). retorna (centro, raio, altura)"""
    m, lit, under = pal or SHRUB_PAL[rng.randrange(len(SHRUB_PAL))]
    big = s >= 1.8
    seg = seg or (6 if big else 5)
    hz = s * rng.uniform(0.8, 0.95) * flat
    cz = z + hz * 0.44 - 0.1
    sq = squash or (rng.uniform(0.95, 1.1), rng.uniform(0.92, 1.05))
    gblob(mb, (x, y, cz), s * 0.86, hz, m, rng, seg=seg, under_m=under, jit=0.16, squash=sq, lit=lit, lit_k=0.66,
          fan=False)
    n = rng.choice((1, 1, 2)) if lumps is None else lumps
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        a = a0 + i * TAU / max(1, n) + rng.uniform(-0.5, 0.5)
        rr = s * rng.uniform(0.44, 0.58)
        d = s * rng.uniform(0.5, 0.66)
        gblob(mb, (x + math.cos(a) * d, y + math.sin(a) * d, z + rr * 0.34 - 0.08 + hz * rng.uniform(0.0, 0.25)),
              rr, rr * 0.92, m if rng.random() < 0.7 else under, rng, seg=5 if big else 4, under_m=under, jit=0.16,
              lit=lit, lit_k=0.66, fan=False)
    return (x, y, cz), s, hz


def clump(mb, x, y, z, s, rng, pal=None):
    """moitinha da ORLA dos canteiros (0,7-1,3): 1 bolota de 5 lados + as vezes 1 menor encostada (25-45 tris)"""
    pal = pal or SHRUB_PAL[rng.randrange(len(SHRUB_PAL))]
    return shrub(mb, x, y, z, s, rng, pal, seg=5, lumps=1 if rng.random() < 0.4 else 0, flat=0.8,
                 squash=(rng.uniform(1.05, 1.2), rng.uniform(0.95, 1.08)))


def shrub_group(mb, x, y, z, s, rng, n=None, pal=None):
    """moita composta: 1 moita grande + 1 menor encostada (tamanhos bem diferentes)"""
    n = n or rng.choice((1, 1, 2))
    pal = pal or SHRUB_PAL[rng.randrange(len(SHRUB_PAL))]
    out = [shrub(mb, x, y, z, s, rng, pal)]
    a0 = rng.uniform(0, TAU)
    for i in range(n - 1):
        a = a0 + i * rng.uniform(1.9, 2.6)
        ss = s * rng.uniform(0.5, 0.66)
        d = s * 0.8 + ss * 0.5
        p2 = pal if rng.random() < 0.6 else SHRUB_PAL[rng.randrange(len(SHRUB_PAL))]
        out.append(shrub(mb, x + math.cos(a) * d, y + math.sin(a) * d, z, ss, rng, p2, seg=5, lumps=1))
    return out


def flower_bush(mb, x, y, z, s, rng, color=BLOOM, n=None):
    """moita com flores (5 petalas achatadas) pousadas no topo: o acento quente dos canteiros"""
    (cx, cy, cz), r, hz = shrub(mb, x, y, z, s, rng, (rng.choice((PALM, MID, DEEP)), LIME, DEEP), lumps=0)
    n = n or 3
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        a = a0 + i * TAU / n + rng.uniform(-0.4, 0.4)
        q = rng.uniform(0.2, 0.55)
        zz = cz + hz * 0.82 * (1.0 - q * q * 1.2) + 0.08
        VK.blossom(mb, (cx + math.cos(a) * q * r * 0.86, cy + math.sin(a) * q * r * 0.86, zz), max(0.38, s * 0.3),
                   color, rng)


def blossoms(mb, x, y, z, r, rng, n, color=BLOOM):
    """flores soltas rentes ao canteiro (acento quente barato: 10 tris cada)"""
    for i in range(n):
        a = rng.uniform(0, TAU)
        d = r * math.sqrt(rng.random())
        VK.blossom(mb, (x + math.cos(a) * d, y + math.sin(a) * d, z + 0.18), rng.uniform(0.34, 0.5), color, rng)


def tuft(mb, x, y, z, s, rng, m=PALM, n=None):
    """tufo de laminas em leque (3-4 espetos): 3 tris por lamina"""
    blade_tuft(mb, x, y, z, s, rng, m=m, n=n or rng.randint(3, 4))


# ------------------------------------------------------------------ rochas de arenito (estilo db_terrain_rock)
def rock(mb, x, y, z, r, h, rng, m=ROCK, lid=False, band=True, n=None):
    """prisma de arenito facetado (fm_parts.rock_column): contorno de superelipse irregular, afunila, topo inclinado
    com chanfro, faixa de topo clara (Cliff_Rock_DB_Top) ou tampo de grama. Base 0,6 enterrada.
    retorna o raio do circulo INSCRITO no anel do topo (o menor anel), para a coluna octogonal de colisao"""
    n = n or rng.choice((6, 7, 7, 8))
    rot = rng.uniform(0.0, TAU)
    a, b = r * rng.uniform(1.0, 1.18), r * rng.uniform(0.78, 0.95)
    src = FP._rock_poly(a, b, n, rng, ex=rng.uniform(1.9, 2.5), jit=0.08)
    ca, sa = math.cos(rot), math.sin(rot)
    poly = [(px * ca - py * sa, px * sa + py * ca) for px, py in src]
    FP.rock_column(mb, Vector((x, y, 0.0)), poly, z - 0.6, z + h, rng, m, taper=rng.uniform(0.7, 0.84), rings=1,
                   jitter=0.06, tilt=0.1, top_m=GRASS if lid else None, lip=0.5, chamfer=min(0.5, h * 0.18),
                   rim=False, band=(min(0.9, h * 0.3), TOP) if (band and not lid) else None, bottom=False)
    ring = FP._LAST_TOP.get("ring") or []
    best = r
    k = len(ring)
    for i in range(k):
        (x0, y0, _), (x1, y1, _) = ring[i], ring[(i + 1) % k]
        ex, ey = x1 - x0, y1 - y0
        ln = math.hypot(ex, ey) or 1e-6
        best = min(best, abs((x - x0) * ey - (y - y0) * ex) / ln)
    return best


def pebble(mb, x, y, z, s, rng, m=ROCK):
    """seixo facetado baixo (domo de 5-6 lados)"""
    VK.dome(mb, (x, y, z - s * 0.2), s, s * rng.uniform(0.5, 0.75), m, rng, seg=rng.choice((5, 6)), jit=0.18,
            bottom=False)


# ------------------------------------------------------------------ canteiros e manchas rentes ao chao
def outline(x, y, r, rng, n=14, aspect=1.0, rot=0.0, amp=0.16):
    """contorno organico (harmonicos baixos + ruido): pontos (x, y) anti-horarios"""
    ph = [rng.uniform(0, TAU) for _ in range(3)]
    am = [amp * rng.uniform(0.6, 1.0), amp * rng.uniform(0.3, 0.7), amp * rng.uniform(0.15, 0.4)]
    ca, sa = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        t = i * TAU / n
        k = 1.0 + am[0] * math.cos(2 * t + ph[0]) + am[1] * math.cos(3 * t + ph[1]) + am[2] * math.cos(5 * t + ph[2])
        k *= rng.uniform(0.95, 1.05)
        px, py = math.cos(t) * r * k * aspect, math.sin(t) * r * k / aspect
        out.append((x + px * ca - py * sa, y + px * sa + py * ca))
    return out


def flat_patch(mb, poly, c, surf, dz, m, ring=None, ring_m=None, ring_dz=None, uv=True, mid_ring=True):
    """mancha rente ao chao: miolo em leque (centro + anel a 55%) no material m, e orla opcional (poligono 'ring'
    de fora, mesma contagem de pontos) em ring_m um pouco mais baixa. Cada vertice e assentado na superficie real
    (surf(x, y) -> z). Faces so para cima (vista de cima/de lado rasante)."""
    bm = mb.bm
    cx, cy = c
    n = len(poly)

    def V(px, py, d):
        return bm.verts.new((px, py, surf(px, py) + d))
    vc = V(cx, cy, dz)
    outer = [V(px, py, dz) for px, py in poly]
    fin = []
    if mid_ring:
        mid = [V(cx + (px - cx) * 0.55, cy + (py - cy) * 0.55, dz) for px, py in poly]
        for i in range(n):
            j = (i + 1) % n
            _face(mb, (vc, mid[i], mid[j]), fin)
            _face(mb, (mid[i], outer[i], outer[j], mid[j]), fin)
    else:
        for i in range(n):
            _face(mb, (vc, outer[i], outer[(i + 1) % n]), fin)
    assign(mb, fin, m, uv)
    if ring:
        rd = ring_dz if ring_dz is not None else dz - 0.02
        lo = [V(px, py, rd) for px, py in poly]
        ro = [V(px, py, rd) for px, py in ring]
        fr = []
        for i in range(n):
            j = (i + 1) % n
            _face(mb, (lo[i], ro[i], ro[j], lo[j]), fr)
        assign(mb, fr, ring_m, uv)


def soft_outline(x, y, r, rng, n=16, aspect=1.0, rot=0.0, jit=0.12):
    """contorno de BOLHA MACIA: raios do db_lib.blob_poly (n >= 14, jitter <= 0,15) suavizados com os vizinhos (sem
    dente nem ponta) + 1 harmonico baixo (forma organica, nao elipse). Extensao <= 1,21 r (folga do Site: 1,24 r)"""
    n = max(14, n)
    raw = DL.blob_poly(0.0, 0.0, 1.0, n, rng, amp=min(0.15, jit))
    rs = [math.hypot(px, py) for px, py in raw]
    rs = [(rs[i - 1] + 2.0 * rs[i] + rs[(i + 1) % n]) * 0.25 for i in range(n)]
    ph, a2 = rng.uniform(0, TAU), rng.uniform(0.03, 0.07)
    ca, sa = math.cos(rot), math.sin(rot)
    out = []
    for i in range(n):
        t = i * TAU / n
        k = rs[i] * (1.0 + a2 * math.cos(2 * t + ph))
        px, py = math.cos(t) * r * k * aspect, math.sin(t) * r * k / aspect
        out.append((x + px * ca - py * sa, y + px * sa + py * ca))
    return out


def mound(mb, poly, c, surf, h, m=GRASS, rim_m=GRASS_B, edge=-0.06, uv=True):
    """canteiro em MONTE BAIXO arredondado: miolo a 'h' acima do chao, aneis a 55% (0,94 h) e 82% (0,6 h) e a borda
    enterrada ('edge'): a faixa externa (82% -> borda) e o CHANFRO da orla, no verde mais escuro. Cada vertice e
    assentado no chao real (surf). Canteiro pequeno (<= 5): um anel so (72%, 0,68 h). 5n tris (3n no pequeno)"""
    bm = mb.bm
    cx, cy = c
    n = len(poly)
    big = max(math.hypot(px - cx, py - cy) for px, py in poly) > 5.0
    ks = ((0.55, 0.94), (0.82, 0.6)) if big else ((0.72, 0.68),)

    def V(px, py, d):
        return bm.verts.new((px, py, surf(px, py) + d))
    vc = V(cx, cy, h)
    rings = [[V(cx + (px - cx) * k, cy + (py - cy) * k, h * f) for px, py in poly] for k, f in ks]
    outer = [V(px, py, edge) for px, py in poly]
    top, rim = [], []
    for i in range(n):
        _face(mb, (vc, rings[0][i], rings[0][(i + 1) % n]), top)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            _face(mb, (r0[i], r1[i], r1[j], r0[j]), top)
    last = rings[-1]
    for i in range(n):
        j = (i + 1) % n
        _face(mb, (last[i], outer[i], outer[j], last[j]), rim)
    assign(mb, top, m, uv)
    assign(mb, rim, rim_m, uv)
    return ks[-1][0], ks[-1][1] * h


def bed(mb, x, y, r, rng, surf, aspect=1.0, rot=None, n=14, h=0.4, m=GRASS, rim_m=GRASS_B):
    """canteiro de grama em BOLHA MACIA levantado como monte baixo (0,3-0,45) com orla chanfrada mais escura. As
    moitinhas e os tufos da orla vem depois (db_veg.Stage.bed, com teste de sitio). retorna o contorno"""
    rot = rng.uniform(0, TAU) if rot is None else rot
    poly = soft_outline(x, y, r, rng, n, aspect, rot)
    mound(mb, poly, (x, y), surf, h, m, rim_m)
    return poly


def edge_tufts(mb, poly, c, surf, rng, step=1.8, avoid=(), k=0.93, zk=0.05, s=(0.7, 1.1), cap=None):
    """tufos de laminas (3 laminas, 9 tris) a cada ~'step' studs ao longo da ORLA do canteiro (no chanfro, a k do
    raio): quebra vertical da borda. Pula onde ja tem moitinha (avoid = [(x, y, raio)]). retorna quantos"""
    cx, cy = c
    n = len(poly)
    pts = [(cx + (px - cx) * k, cy + (py - cy) * k) for px, py in poly]
    per = sum(math.hypot(pts[(i + 1) % n][0] - pts[i][0], pts[(i + 1) % n][1] - pts[i][1]) for i in range(n))
    cnt = max(3, int(per / step))
    if cap:
        cnt = min(cnt, cap)
    stp = per / cnt
    got = 0
    walk = rng.uniform(0.0, stp)
    i, acc = 0, 0.0
    for q in range(cnt):
        target = walk + q * stp
        while i < n:
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            ln = math.hypot(bx - ax, by - ay)
            if acc + ln >= target:
                break
            acc += ln
            i += 1
        if i >= n:
            break
        t = (target - acc) / (ln or 1.0)
        px, py = ax + (bx - ax) * t + rng.uniform(-0.25, 0.25), ay + (by - ay) * t + rng.uniform(-0.25, 0.25)
        if any(math.hypot(px - ax_, py - ay_) < ar + 0.35 for ax_, ay_, ar in avoid):
            continue
        blade_tuft(mb, px, py, surf(px, py) + zk, rng.uniform(*s), rng, m=PALM if rng.random() < 0.65 else GRASS_B,
                   n=3)
        got += 1
    return got


def cracked_patch(mb, x, y, r, rng, surf, aspect=1.0, dz=0.045):
    """mancha de terra rachada (plana): leque de terra escura + rachaduras ramificadas (fitas de 0,26) um pouco acima"""
    rot = rng.uniform(0, TAU)
    poly = outline(x, y, r, rng, 11, aspect, rot, amp=0.2)
    flat_patch(mb, poly, (x, y), surf, dz, DIRT)
    bm = mb.bm
    faces = []

    def strip(p0, p1, w):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        ln = math.hypot(dx, dy)
        if ln < 0.4:
            return
        nx, ny = -dy / ln * w * 0.5, dx / ln * w * 0.5
        vs = [bm.verts.new((px, py, surf(px, py) + dz + 0.03)) for px, py in
              ((p0[0] - nx, p0[1] - ny), (p1[0] - nx * 0.4, p1[1] - ny * 0.4), (p1[0] + nx * 0.4, p1[1] + ny * 0.4),
               (p0[0] + nx, p0[1] + ny))]
        _face(mb, vs, faces)
    a0 = rng.uniform(0, TAU)
    for k in range(rng.randint(4, 6)):
        a = a0 + k * TAU / 5 + rng.uniform(-0.4, 0.4)
        p = (x + math.cos(a) * r * 0.12, y + math.sin(a) * r * 0.12)
        for s in range(3):
            a += rng.uniform(-0.6, 0.6)
            ln = r * rng.uniform(0.2, 0.3) * (aspect if abs(math.cos(a - rot)) > 0.7 else 1.0)
            q = (p[0] + math.cos(a) * ln, p[1] + math.sin(a) * ln)
            strip(p, q, 0.3 - s * 0.03)
            if s == 1 and rng.random() < 0.6:
                b = a + rng.choice((-1, 1)) * rng.uniform(0.8, 1.3)
                strip(q, (q[0] + math.cos(b) * ln * 0.7, q[1] + math.sin(b) * ln * 0.7), 0.24)
            p = q
    assign(mb, faces, DARK)


# ------------------------------------------------------------------ arvore de sombra (vila)
def shade_tree(mb, x, y, z, h, rng, clear=6.2, leaf=None):
    """folhosa tropical de copa redonda (NAO sakura, NAO pinheiro): tronco claro torto que abre em 3 bracos, copa de
    4-5 domos facetados (o maior no alto), topo lima e fundo escuro; a copa comeca acima de 'clear' (o jogador passa
    por baixo). ~300 tris. retorna (raio do tronco no pe, raio da copa, (pe, primeiro joelho do tronco))"""
    leaf = leaf or rng.choice((PALM, MID))
    tr = max(0.55, h * 0.048)
    w = rng.uniform(0, TAU)
    R = h * 0.33
    zc = z + max(clear + R * 0.7, h * 0.6)
    p0 = Vector((x, y, z - 0.5))
    p1 = Vector((x + math.cos(w) * h * 0.05, y + math.sin(w) * h * 0.05, z + (zc - z) * 0.5))
    p2 = Vector((x - math.cos(w) * h * 0.03, y - math.sin(w) * h * 0.03, zc - R * 0.15))
    VK.ttube(mb, [p0, p1, p2], [tr * 1.45, tr, tr * 0.72], BARK, n=6, cap1=False)
    for k in range(3):
        a = w + 0.6 + k * TAU / 3
        VK.spike(mb, (x, y, z + h * 0.05), (x + math.cos(a) * tr * 2.8, y + math.sin(a) * tr * 2.8, z - 0.3),
                 tr * 0.55, BARK, 3, rot=a)
    VK.blob(mb, (p2.x, p2.y, zc + R * 0.35), R * 0.8, R * 1.0, leaf, rng, seg=7, under_m=DEEP, lit=LIME, lit_k=0.64)
    n = rng.choice((4, 5))
    a0 = rng.uniform(0, TAU)
    for i in range(n - 1):
        a = a0 + i * TAU / (n - 1) + rng.uniform(-0.35, 0.35)
        d = R * rng.uniform(0.55, 0.72)
        rr = R * rng.uniform(0.5, 0.64)
        c = Vector((p2.x + math.cos(a) * d, p2.y + math.sin(a) * d, zc - R * rng.uniform(0.0, 0.18)))
        c.z = max(c.z, z + clear + rr * 0.48)
        VK.ttube(mb, [p1.lerp(p2, 0.6), c - Vector((0, 0, rr * 0.25))], [tr * 0.5, tr * 0.3], BARK, n=4, cap1=False)
        VK.blob(mb, c, rr, rr * 0.95, leaf if i % 2 == 0 else MID, rng, seg=6, under_m=DEEP, lit=LIME, lit_k=0.64)
    return tr * 1.45, R * 1.3, (p0 + Vector((0.0, 0.0, 0.05)), p1)


# ------------------------------------------------------------------ coroas das mesas (so vistas de longe: detail far)
def crown_tree(mb, x, y, z, h, rng, leaf=None, sides=None):
    """folhosa de copa redonda LEVE para o topo das mesas: tronco de 4 lados que entorta + domo principal (5 lados,
    topo lima, fundo escuro: aparece de baixo) + 1-2 domos laterais de 4 lados. ~70-95 tris. retorna o raio da copa"""
    leaf = leaf or rng.choice((PALM, MID, PALM))
    tr = max(0.5, h * 0.05)
    w = rng.uniform(0, TAU)
    R = h * 0.34
    zc = z + h * 0.62
    p0 = Vector((x, y, z - 0.4))
    p1 = Vector((x + math.cos(w) * h * 0.05, y + math.sin(w) * h * 0.05, z + h * 0.34))
    p2 = Vector((x - math.cos(w) * h * 0.02, y - math.sin(w) * h * 0.02, zc))
    VK.ttube(mb, [p0, p1, p2], [tr * 1.35, tr, tr * 0.7], BARK, n=4, cap0=False, cap1=False, rot=rng.uniform(0, TAU))
    gblob(mb, (p2.x, p2.y, zc + R * 0.3), R * 0.85, R * 0.95, leaf, rng, seg=5, under_m=DEEP, jit=0.12, lit=LIME,
          lit_k=0.62)
    n = sides or rng.choice((1, 2))
    a0 = rng.uniform(0, TAU)
    for i in range(n):
        a = a0 + i * TAU / n + rng.uniform(-0.4, 0.4)
        rr = R * rng.uniform(0.55, 0.68)
        d = R * rng.uniform(0.6, 0.75)
        gblob(mb, (p2.x + math.cos(a) * d, p2.y + math.sin(a) * d, zc - R * rng.uniform(0.0, 0.15)), rr, rr * 0.92,
              MID if leaf == PALM else PALM, rng, seg=4, under_m=DEEP, jit=0.12, lit=LIME, lit_k=0.62)
    return R * 1.35


def crown_palm(mb, x, y, z, h, rng, lean=0.14, lean_dir=None, fronds=6):
    """palmeira LEVE para o topo das mesas: tronco de 4 lados em 2 lances + 'fronds' folhas de 1 joelho (6 tris:
    sobe ate o joelho largo e cai ate a ponta), 2 verdes alternados. ~50-60 tris. retorna o raio da coroa"""
    a = rng.uniform(0, TAU) if lean_dir is None else lean_dir
    ux, uy = math.cos(a), math.sin(a)
    tr = 0.55
    pts = [Vector((x + ux * lean * h * t * t, y + uy * lean * h * t * t, z - 0.4 + (h + 0.4) * t)) for t in (0, 0.5, 1)]
    VK.ttube(mb, pts, [tr * 1.4, tr, tr * 0.72], BARK, n=4, cap0=False, cap1=True, rot=rng.uniform(0, TAU))
    top = pts[-1]
    up = Vector((0.0, 0.0, 1.0))
    ln = max(4.2, min(7.0, h * 0.5))
    rot = rng.uniform(0, TAU)
    for k in range(fronds):
        low = k % 2 == 1
        b = rot + k * TAU / fronds + rng.uniform(-0.2, 0.2)
        d = Vector((math.cos(b), math.sin(b), 0.0))
        s = Vector((-d.y, d.x, 0.0))
        L_ = ln * rng.uniform(0.88, 1.05) * (0.9 if low else 1.0)
        w = L_ * rng.uniform(0.34, 0.4)
        knee = top + d * L_ * 0.42 + up * L_ * (0.2 if low else 0.34)
        tip = top + d * L_ * 0.95 - up * L_ * (0.42 if low else 0.22)
        root = mb.bm.verts.new(top + up * 0.1)
        sec = [mb.bm.verts.new(p) for p in (knee - s * w * 0.5 - up * w * 0.2, knee + up * w * 0.12,
                                             knee + s * w * 0.5 - up * w * 0.2)]
        tv = mb.bm.verts.new(tip)
        faces = []
        for i in range(3):
            j = (i + 1) % 3
            _face(mb, (root, sec[j], sec[i]), faces)
            _face(mb, (sec[i], sec[j], tv), faces)
        assign(mb, faces, DEEP if low else PALM)
    return ln * 0.8


def crown_bush(mb, x, y, z, s, rng):
    """moita do topo das mesas: a moita comum de 5/4 lados (25-45 tris)"""
    return shrub(mb, x, y, z, s, rng, SHRUB_PAL[rng.randrange(len(SHRUB_PAL))], seg=5,
                 lumps=1 if rng.random() < 0.5 else 0)


# ------------------------------------------------------------------ floreira Capsule
def planter(mb, x, y, z, r, rng, h=1.15):
    """floreira Capsule (a mesma familia das da praca de entrada): vaso branco que abre para cima, faixa azul, terra
    de grama. ~110 tris. retorna a cota da terra"""
    mb.cyl(r, h, (x, y, z + h / 2 - 0.05), (0, 0, 0), WHITE, 12, r2=r * 1.08, bevel=0.0)
    mb.cyl(r * 1.06, 0.34, (x, y, z + h * 0.55), (0, 0, 0), BLUE, 12, bevel=0.0)
    soil = z + h - 0.06
    mb.cyl(r * 0.96, 0.2, (x, y, soil - 0.08), (0, 0, 0), GRASS, 12, bevel=0.0)
    return soil
