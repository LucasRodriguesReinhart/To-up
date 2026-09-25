# il_terrain - zona TERRAIN da Ilha 1 (Naruto / Vila da Folha), prefixo TER_, colecao 02_TERRAIN.
# Substitui no blockout: terrain(), terrace_guards(), stairs_all().
#   il_terrain_rock : penhascos da borda (colunas castanho-douradas com labio de grama), prateleira em lobulos,
#                     penhasco baixo em 3 faixas ate o mar, macico do fundo (3 patamares, 2 sulcos, picos NO/NE)
#   il_terrain_stone: muros de arrimo em fiadas + capeamento, balaustradas/muretas (vaos do blockout), escadas
#   aqui            : superficies (gramados G/T1/T2/plato, anel pavimentado, ruas da vila, piso do fosso) e build()
# A colisao do chao e da borda vem do il_core (il_col.terrain_col): os topos aqui batem com L.G/RING/PIT/T1/T2.
import math, random
import fm_lib
import il_lib as IL
from il_lib import MB
import il_layout as L
import il_terrain_rock as R
import il_terrain_stone as ST

C = "02_TERRAIN"
GRASS = "Grass_Konoha"
DARK = "Cliff_Rock_Tan_Dark"
PAVE = "Stone_Paving_Warm"

# materiais novos da zona (familia do lobby + zona no nome)
fm_lib.MATS.setdefault("Dirt_TerPatch", (fm_lib.S(122, 78, 48), 0.95, 0.0, 0, None, 0.16))   # manchas do fosso
fm_lib.MATS.setdefault("Stone_TerGrout", (fm_lib.S(96, 88, 80), 0.95, 0.0, 0, None, 0.05))   # rejunte do anel/ruas

# cameras de revisao (360 graus + altura do jogador)
CAMS = {
    "CAM_Terrain_SW": ((-250.0, -215.0, 18.0), (-105.0, -62.0, -18.0), 24),
    "CAM_Terrain_Front": ((70.0, -320.0, 40.0), (10.0, -80.0, -10.0), 24),
    "CAM_Terrain_East": ((340.0, 40.0, 50.0), (110.0, 40.0, 0.0), 24),
    "CAM_Terrain_West": ((-340.0, 90.0, 55.0), (-110.0, 60.0, 5.0), 24),
    "CAM_Terrain_North": ((-90.0, 400.0, 70.0), (0.0, 180.0, 30.0), 24),
    "CAM_Terrain_Back": ((24.0, 128.0, L.T2 + 5.5), (0.0, 190.0, 52.0), 18),
    "CAM_Terrain_Stairs": ((7.0, 70.0, L.RING + 5.5), (0.0, 108.0, L.T1 + 4.0), 18),
    "CAM_Terrain_Ring": ((-60.0, -36.0, L.RING + 5.5), (34.0, 40.0, L.RING + 1.0), 18),
    "CAM_Terrain_Valley": ((127.0, 32.0, L.G + 5.5), (104.0, 112.0, L.T1 + 2.0), 18),
    "CAM_Terrain_Lawn": ((-40.0, -112.0, L.G + 5.5), (-80.0, -20.0, L.RING), 18),
    "CAM_Terrain_CornerSW": ((-92.0, -78.0, L.G + 6.0), (-120.0, -38.0, L.G + 2.0), 18),
    "CAM_Terrain_T2West": ((-112.0, 104.0, L.T1 + 6.0), (-146.0, 130.0, L.T2 - 2.0), 18),
    "CAM_Terrain_Top": ((0.0, 30.0, 170.0), (0.0, 112.0, 0.0), 30),
    "CAM_Terrain_Mill": ((62.0, -22.0, L.RING + 5.5), (92.0, 14.0, L.G + 2.0), 18),
    "CAM_Terrain_SECove": ((66.0, -100.0, L.G + 7.0), (106.0, -76.0, -6.0), 20),
}


# ------------------------------------------------------------------ poligonos dos gramados
def g_polys():
    """chao G: crescente sul (fora do anel, setor 200..386 graus, sem a praca do portao) + vale leste"""
    rim = IL.rim()
    a0, a1 = L.T1_WALL_A
    out = []
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    for w0, w1, side in ((a1, 270.0, -1), (270.0, 360.0 + a0, 1)):
        p = IL.wedge_clip(rim, w0, w1)
        p = IL.replace_apex_with_arc(p, L.RING_R1 - 0.6, w1, w0, 3.0)
        # recorta a praca do portao (piso da entrada) - fica so o gramado em volta
        out.append(IL.clip(p, 0.0, -1.0, -y1))                               # y >= y1
        q = IL.clip(p, 0.0, 1.0, y1)                                          # y <= y1
        q = IL.clip(q, -side, 0.0, -abs(x1)) if side > 0 else IL.clip(q, 1.0, 0.0, -abs(x0))
        out.append(q)
    v = IL.clip(rim, -1.0, 0.0, -107.6)                                       # x >= 107.6
    v = IL.clip(v, 0.0, 1.0, L.T2_WALL_Y)                                     # y <= 126
    t = math.radians(a0)
    v = IL.clip(v, math.sin(t), -math.cos(t), 0.0)                           # acima do raio de 26 graus
    out.append(v)
    return [IL.ccw(p) for p in out if len(p) >= 3 and abs(IL.area(p)) > 1.0]


def lawns(rng):
    import il_col
    mb = MB("TER_Ground", C, rng, detail="far")
    zb = L.SHELF_Z - 1.0
    for p in g_polys():
        IL.prism(mb, p, zb, L.G, DARK, GRASS)
    t1 = IL.clip(il_col.t1_poly_notched(), 0.0, 1.0, L.T2_WALL_Y)
    IL.prism(mb, t1, zb, L.T1, DARK, GRASS)
    t2 = IL.clip(il_col.t2_poly_notched(), 0.0, 1.0, L.BACK_CLIFF_Y)
    IL.prism(mb, t2, zb, L.T2, DARK, GRASS)
    # plato de cima: corpo recuado atras dos 3 patamares do paredao (as colunas fecham a frente)
    cl = IL.clip(IL.rim(), 0.0, -1.0, -(L.BACK_CLIFF_Y + 4.2))
    IL.prism(mb, IL.ccw(cl), zb, L.CLIFF_TOP, DARK, GRASS)
    mb.finish()


# ------------------------------------------------------------------ pavimentos
def _stone(mb, pts, z, rng, m=PAVE, h=0.26):
    dz = rng.uniform(-0.03, 0.03)
    mb.prism(IL.ccw(pts), z - 0.12, z + h - 0.12 + dz, m, 0.0)


def _avoid_clip(poly, avoid):
    """corta o poligono fora do circulo avoid = (cx, cy, R) (semiplano tangente no rumo do centroide)"""
    if not avoid:
        return poly
    cx, cy, R = avoid
    mx = sum(p[0] for p in poly) / len(poly) - cx
    my = sum(p[1] for p in poly) / len(poly) - cy
    d = math.hypot(mx, my)
    if d > R + 8.0:
        return poly
    if d < 1e-6:
        return []
    ux, uy = mx / d, my / d
    return IL.clip(poly, -ux, -uy, -(R + ux * cx + uy * cy))


def pave_polar(mb, r0, r1, a0, a1, z, rng, row=3.2, blen=4.2, gap=0.2, stagger=0, m=PAVE, avoid=None):
    """lajes em fiadas concentricas (anel / rua em arco), cada laje e um quadrilatero (corda);
    avoid = (cx, cy, R): nenhuma laje entra nesse circulo (ex. piso da praca do summon)"""
    nr = max(1, int(round((r1 - r0) / row)))
    dr = (r1 - r0) / nr
    n = 0
    for i in range(nr):
        ra, rb = r0 + dr * i + gap * 0.5, r0 + dr * (i + 1) - gap * 0.5
        rm = (ra + rb) * 0.5
        span = math.radians(a1 - a0)
        ns = max(1, int(round(span * rm / blen)))
        da = span / ns
        off = (0.5 if (i + stagger) % 2 else 0.0) * da
        for k in range(ns + (1 if off else 0)):
            ta = math.radians(a0) + da * k - off
            tb = ta + da
            ta, tb = max(ta, math.radians(a0)), min(tb, math.radians(a1))
            if (tb - ta) * rm < 0.8:
                continue
            ga = gap * 0.5 / rm
            ta, tb = ta + ga, tb - ga
            pts = [(ra * math.cos(ta), ra * math.sin(ta)), (ra * math.cos(tb), ra * math.sin(tb)),
                   (rb * math.cos(tb), rb * math.sin(tb)), (rb * math.cos(ta), rb * math.sin(ta))]
            pts = _avoid_clip(pts, avoid)
            if len(pts) < 3 or abs(IL.area(pts)) < 0.8:
                continue
            _stone(mb, pts, z, rng, m)
            n += 1
    return n


def pave_rect(mb, origin, ang, x0, x1, y0, y1, z, rng, tile=(3.2, 3.0), gap=0.2, m=PAVE, outside_r=None,
              grout=True):
    """lajes num retangulo local (x ao longo do rumo 'ang'), fiadas desencontradas; bordas cortadas certinho.
    outside_r: corta as lajes contra o circulo r >= outside_r (encosta na rua em arco sem sobrepor)"""
    ca, sa = math.cos(ang), math.sin(ang)
    ox, oy = origin

    def W(x, y):
        return (ox + x * ca - y * sa, oy + x * sa + y * ca)

    def cut(poly):
        if outside_r is None:
            return poly
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        rr = math.hypot(cx, cy) or 1.0
        return IL.clip(poly, -cx / rr, -cy / rr, -outside_r)
    if grout:
        g = cut([W(x0, y0), W(x1, y0), W(x1, y1), W(x0, y1)]) if outside_r is None else None
        if g:
            mb.prism(IL.ccw(g), z - 0.3, z + 0.03, "Stone_TerGrout", 0.0)
        elif outside_r is not None:
            # base de rejunte em faixas (acompanha o corte do arco)
            yy = y0
            while yy < y1 - 0.05:
                yb = min(yy + 1.5, y1)
                q = cut([W(x0, yy), W(x1, yy), W(x1, yb), W(x0, yb)])
                if len(q) >= 3 and abs(IL.area(q)) > 0.3:
                    mb.prism(IL.ccw(q), z - 0.3, z + 0.03, "Stone_TerGrout", 0.0)
                yy = yb
    n = 0
    y = y0
    row = 0
    while y < y1 - 0.3:
        yb = min(y + tile[1], y1)
        if y1 - yb < 1.0:
            yb = y1
        x = x0 - (tile[0] * 0.5 if row % 2 else 0.0)
        while x < x1 - 0.3:
            xb = min(x + tile[0], x1)
            if x1 - xb < 1.0:
                xb = x1
            xa = max(x, x0)
            if xb - xa > 0.8:
                g = gap * 0.5
                pts = cut([W(xa + g, y + g), W(xb - g, y + g), W(xb - g, yb - g), W(xa + g, yb - g)])
                if len(pts) >= 3 and abs(IL.area(pts)) > 0.6:
                    _stone(mb, pts, z, rng, m)
                    n += 1
            x = xb
        y = yb
        row += 1
    return n


def ring_paving(rng):
    mb = MB("TER_Ring_Paving", C, rng, detail="far")
    # corpo do anel (rejunte escuro entre as lajes; atras do muro do fosso e do muro externo)
    zb, zt = L.PIT - 0.5, L.RING - 0.05
    for h0, h1 in ((0.0, 180.0), (180.0, 360.0)):
        IL.annulus(mb, L.RING_R0 + 0.8, L.RING_R1 - 0.6, h0, h1, zb, zt, "Stone_TerGrout", 3.0)
    IL.annulus(mb, L.RING_R1 - 0.8, L.T1_WALL_R + 0.3, L.T1_WALL_A[0], L.T1_WALL_A[1], zb, zt, "Stone_TerGrout",
               3.0)
    a0, a1 = L.T1_WALL_A
    r_in = L.PIT_R + 1.4
    r_out = L.RING_R1 - 1.45
    n = pave_polar(mb, r_in, r_out, a1, 360.0 + a0, L.RING, rng, row=3.2, blen=4.4)
    n += pave_polar(mb, r_in, r_out, a0, a1, L.RING, rng, row=3.2, blen=4.4)
    # faixa do anel ao pe do muro T1 (r 80.5..88) no setor da vila: fiadas extras
    n += pave_polar(mb, r_out, L.T1_WALL_R - 0.1, a0, a1, L.RING, rng, row=3.6, blen=4.6, stagger=1)
    mb.finish()
    return n


def streets(rng):
    """ruas da vila: eixo central (escada C -> escada T2), rua em arco no T1 ligando as escadas radiais ate a praca
    do summon, ramais ao ramen/casa, rua ate o inicio da saida, praca do T2 e ramais ate a loja de armas e o predio
    azul leste"""
    mb = MB("TER_Streets", C, rng, detail="far")
    z1, z2 = L.T1, L.T2
    ra, rb = 96.3, 103.3            # rua em arco: do topo das escadas radiais (r 96.1) ate r 103.3
    a_s, a_e = 40.0, 166.0          # do rumo da saida ate a borda da praca do summon (recortada no circulo)
    avoid = (L.SUMMON_C[0], L.SUMMON_C[1], L.SUMMON_R + 0.3)
    k = int((a_e - a_s) / 2.0)
    for i in range(k):
        t0 = math.radians(a_s + (a_e - a_s) * i / k)
        t1 = math.radians(a_s + (a_e - a_s) * (i + 1) / k)
        q = [(ra * math.cos(t0), ra * math.sin(t0)), (ra * math.cos(t1), ra * math.sin(t1)),
             ((rb + 0.1) * math.cos(t1), (rb + 0.1) * math.sin(t1)), ((rb + 0.1) * math.cos(t0), (rb + 0.1) * math.sin(t0))]
        q = _avoid_clip(q, avoid)
        if len(q) >= 3 and abs(IL.area(q)) > 0.3:
            mb.prism(IL.ccw(q), z1 - 0.3, z1 + 0.03, "Stone_TerGrout", 0.0)
    n = pave_polar(mb, ra, rb, a_s, a_e, z1, rng, row=3.5, blen=4.0, avoid=avoid)
    ro = rb + 0.25
    # eixo central: da rua em arco ate o pe da escada do T2
    n += pave_rect(mb, (0.0, 0.0), 0.0, -6.0, 6.0, rb - 1.0, L.T2_STAIR_Y0 - 0.15, z1, rng, outside_r=ro)
    # ramais ao ramen (-38,107) e a casa (38,107): da rua em arco ate a frente (y 101)
    for sx in (-1, 1):
        hx = sx * 38.0
        n += pave_rect(mb, (0.0, 0.0), 0.0, hx - 3.9, hx + 3.9, 93.0, 100.9, z1, rng, tile=(2.6, 2.8),
                       outside_r=ro)
    # rua ate o inicio da ponte de saida (96,96), no rumo 45 graus
    re_ = math.hypot(*L.EXIT_START)
    n += pave_rect(mb, (0.0, 0.0), math.radians(L.EXIT_DEG), rb - 1.0, re_ - 0.2, -7.0, 7.0, z1, rng,
                   tile=(3.2, 3.5), outside_r=ro)
    # praca do T2 diante do salao + ramais ate as portas dos predios redondos (x = +-58, y 140)
    top = L.T2_STAIR_Y0 + 8 * L.TREAD + 0.25
    n += pave_rect(mb, (0.0, 0.0), 0.0, -30.0, 30.0, top, 137.8, z2, rng)
    for sx in (-1, 1):
        xa, xb = (30.25, 65.0) if sx > 0 else (-65.0, -30.25)
        n += pave_rect(mb, (0.0, 0.0), 0.0, xa, xb, 131.0, 139.8, z2, rng, tile=(3.2, 2.9))
    mb.finish()
    return n


def pit_floor(rng):
    mb = MB("TER_Pit_Floor", C, rng, detail="far")
    IL.prism(mb, IL.arc_pts(L.PIT_R + 0.2, 0.0, 360.0, 3.75)[:-1], L.PIT - 1.2, L.PIT, "Dirt_Pit")
    # manchas mais escuras (terra revolvida) - planas, nao atrapalham os corredores
    for k in range(22):
        a = rng.uniform(0.0, math.tau)
        r = rng.uniform(12.0, 54.0)
        cx, cy = r * math.cos(a), r * math.sin(a)
        rad = rng.uniform(4.0, 9.0)
        nv = 9
        pts = []
        for i in range(nv):
            th = math.tau * i / nv + rng.uniform(-0.15, 0.15)
            rr = rad * rng.uniform(0.65, 1.15) * (1.35 if i % 3 == 0 else 1.0)
            px, py = cx + rr * math.cos(th) * 1.3, cy + rr * math.sin(th)
            if math.hypot(px, py) > L.PIT_R - 1.0:
                s = (L.PIT_R - 1.0) / math.hypot(px, py)
                px, py = px * s, py * s
            pts.append((px, py))
        m = "Dirt_TerPatch" if k % 3 else "Dirt_Pit_B"
        mb.prism(IL.ccw(pts), L.PIT - 0.1, L.PIT + 0.04 + 0.008 * k, m, 0.0)     # cotas distintas: sem z-fight
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    lawns(random.Random(11))
    pit_floor(random.Random(12))
    ring_paving(random.Random(13))
    streets(random.Random(14))
    ST.walls(random.Random(21))
    ST.guards(random.Random(22))
    ST.stairs(random.Random(23))
    R.upper_cliffs(random.Random(31))
    R.shelf_and_lower(random.Random(32))
    R.back_massif(random.Random(33))
