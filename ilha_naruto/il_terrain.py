# il_terrain - zona TERRAIN da Ilha 1 (Naruto / Vila da Folha), prefixo TER_, colecao 02_TERRAIN.
# Substitui no blockout: terrain(), terrace_guards(), stairs_all().
#   il_terrain_rock : penhascos da borda (colunas castanho-douradas com labio de grama), prateleira em lobulos,
#                     penhasco baixo em 3 faixas ate o mar, macico do fundo (3 patamares, 2 sulcos, picos NO/NE)
#   il_terrain_stone: muros de arrimo em fiadas + capeamento, nicho da bica, muro G->T2 na diagonal do recorte,
#                     balaustradas/muretas, escadas (radiais, T2, entrada, moinho, laterais G->anel, vale->T1),
#                     booleanas 2D de poligonos (poly_bool / offset_poly)
#   aqui            : superficies (gramados G/T1/T2/plato recortados 0,5 da borda e sem o leito do riacho, leito e
#                     taludes do riacho do vale, anel pavimentado, ruas da vila, caminhos das casas, piso do fosso),
#                     rotas extras do QA (EXTRA_ROUTES) e build()
# A colisao do chao e da borda vem do il_core (il_col.terrain_col): os topos aqui batem com L.G/RING/PIT/T1/T2 e o
# leito do riacho usa o MESMO poligono da colisao (il_col.stream_bed_poly). Rodada 2: _studio/terrain/PROGRESSO.md.
import math, random
from mathutils import Vector
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


# ------------------------------------------------------------------ rotas extras do QA (pecas novas desta zona)
def _side_route(ang):
    sx = -1.0 if math.cos(math.radians(ang)) < 0 else 1.0
    P = ST.side_stair_pts
    return [(0.0, -100.0), (sx * 17.0, -100.0), (sx * 30.0, -95.0), P(ang, ST.SIDE_FOOT_R + 4.5),
            P(ang, ST.SIDE_FOOT_R - 0.6), P(ang, ST.SIDE_TOP_R + 1.0), P(ang, 80.0), P(ang, 71.0)]


def _mill_route():
    V = ST.vs_pt
    lat = ST.VS_LAT
    return [(90.0, 12.0), (91.4, 13.0), (91.4, 22.8), (86.0, 27.5), V(84.0, -12.5), V(84.0, lat),
            V(ST.VS_S0 + 1.0, lat), V(ST.VS_S1 - 0.8, lat), V(ST.VS_S1 + ST.VS_LAND / 2, lat),
            V(ST.VS_S1 + ST.VS_LAND / 2, 3.5), (95.0, 60.0), (92.0, 64.0)]


EXTRA_ROUTES = {
    "PRACA->GRAMADO_SO->ANEL": (_side_route(L.SIDE_STAIRS[0][0]), L.G),
    "PRACA->GRAMADO_SE->ANEL": (_side_route(L.SIDE_STAIRS[1][0]), L.G),
    "MOINHO->T1_SAIDA": (_mill_route(), L.G),
}


def _register_paths():
    """os caminhos das casas tambem viram rotas do QA (e a vegetacao mantem 4 studs de folga deles)"""
    for name, pts, z, route in house_paths_spec():
        if route:
            EXTRA_ROUTES["CAMINHO_" + name] = (route, z)


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


RIM_INSET = 0.5          # o gramado para 0,5 antes da borda (as tampas de grama das colunas do penhasco cobrem)
SPILL_OUT = 2.9          # as quedas da borda comecam 2,9 para fora (contrato com a agua)
NICHE, NICHE_BACK, WALL_X = ST.NICHE, ST.NICHE_BACK, ST.WALL_X    # nicho da bica no muro x=108
HEAD_Y = 60.0            # ao norte disto o leito encosta no muro x = 108 (cabeceira da bica)


def rim_in():
    return ST.offset_poly(IL.rim(), RIM_INSET)


def bed_poly():
    import il_col
    return il_col.stream_bed_poly()


def lawns(rng):
    import il_col
    mb = MB("TER_Ground", C, rng, detail="far")
    zb = L.SHELF_Z - 1.0
    rin = rim_in()
    bed = bed_poly()
    for p in g_polys():
        for q in ST.poly_bool(p, rin, "inter"):
            for r in ST.poly_bool(q, bed, "diff"):          # leito do riacho do vale (contrato terreno x agua)
                IL.prism(mb, r, zb, L.G, DARK, GRASS)
    t1 = IL.clip(il_col.t1_poly_notched(), 0.0, 1.0, L.T2_WALL_Y)
    # rasgo atras do nicho da bica (a verga/capa do muro cobrem o rasgo por cima; 0,35 alem das ombreiras)
    ny0, ny1 = NICHE[0] - 0.35, NICHE[1] + 0.35
    slot = [(NICHE_BACK - 0.25, ny0), (WALL_X + 0.6, ny0), (WALL_X + 0.6, ny1), (NICHE_BACK - 0.25, ny1)]
    ex, ey = L.EXIT_START
    ux, uy = L.exit_dir()
    band = [(ex + ux * d + (-uy) * s, ey + uy * d + ux * s) for d, s in ((-0.1, -8.2), (30.0, -8.2), (30.0, 8.2),
                                                                         (-0.1, 8.2))]   # cruza o muro x=108 (sem furo)
    for q in ST.poly_bool(t1, rin, "inter"):
        for r in ST.poly_bool(q, slot, "diff"):
            if len(r) < 3:
                continue
            for r2 in ST.poly_bool(r, band, "diff"):     # sob o calcamento da ponte de saida (leito escuro do il_exit)
                if len(r2) >= 3:
                    IL.prism(mb, r2, zb, L.T1, DARK, GRASS)
    # T2 ate dentro do pe do paredao (as colunas do fundo e as gargantas das quedas assentam sobre ele)
    t2 = IL.clip(il_col.t2_poly_notched(), 0.0, 1.0, L.BACK_CLIFF_Y + 4.4)
    for q in ST.poly_bool(t2, rin, "inter"):
        IL.prism(mb, q, zb, L.T2, DARK, GRASS)
    # plato de cima: corpo recuado atras dos 3 patamares do paredao (as colunas fecham a frente)
    cl = IL.clip(IL.rim(), 0.0, -1.0, -217.0)          # (integracao) antes y >= 190,2: escondia o patamar A e os sulcos
    for q in (ST.poly_bool(cl, rin, "inter") if len(cl) >= 3 else []):
        IL.prism(mb, q, zb, L.CLIFF_TOP, DARK, GRASS)
    mb.finish()


def stream_bed(rng):
    """leito do riacho do vale (contrato terreno x agua): o TER_Ground ja saiu do poligono do leito (o mesmo do
    il_col); aqui o fundo em L.STREAM_BED (poco mais fundo sob a roda d'agua), do muro x=108 ate 2,9 alem da borda SE,
    e o talude curto de pedra nas 2 margens (a lamina d'agua em L.STREAM_WATER morre dentro dele)"""
    bed = bed_poly()
    rin = rim_in()
    zb = L.SHELF_Z - 1.0
    mb = MB("TER_Stream_Bed", C, rng, detail="far")
    # cabeceira (y >= HEAD_Y): o muro x = 108 fecha o leito (x >= 107,9); o resto segue o poligono inteiro
    head = IL.clip(IL.clip(bed, 0.0, -1.0, -HEAD_Y), -1.0, 0.0, -(WALL_X - 0.1))
    tail = IL.clip(bed, 0.0, 1.0, HEAD_Y)
    fl = []
    for q in (head, tail):
        if len(q) >= 3:
            fl += ST.poly_bool(q, ST.offset_poly(IL.rim(), -SPILL_OUT), "inter")   # labio SE: 2,9 alem da borda
    wy = L.WHEEL[1]
    for p in fl:
        parts = ((IL.clip(p, 0.0, -1.0, -(wy + 7.0)), L.STREAM_BED),
                 (IL.clip(IL.clip(p, 0.0, 1.0, wy + 7.0), 0.0, -1.0, -(wy - 7.0)), L.STREAM_BED - 1.2),
                 (IL.clip(p, 0.0, 1.0, wy - 7.0), L.STREAM_BED))
        for q, zt in parts:
            if len(q) >= 3 and abs(IL.area(q)) > 0.5:
                mb.prism(IL.ccw(q), zb, zt, DARK, 0.0)
    mb.finish()
    # talude de pedra: cunhas ao longo do contorno do leito (dentro da ilha, a leste do muro)
    tb = MB("TER_Stream_Banks", C, rng, detail="near")
    ring = ST.resample_poly(bed, 2.6)
    n = len(ring)
    nb = 0
    for i in range(n):
        a, b = Vector((*ring[i], 0.0)), Vector((*ring[(i + 1) % n], 0.0))
        mid = (a + b) * 0.5
        if (mid.y > HEAD_Y and mid.x < WALL_X + 0.25) or not ST._pip(mid.x, mid.y, rin):
            continue
        e = b - a
        if e.length < 0.8:
            continue
        e.normalize()
        nv = Vector((-e.y, e.x, 0.0))                   # para dentro do leito (contorno anti-horario)
        a2, b2 = a + e * 0.07, b - e * 0.07
        zt = L.G + rng.uniform(0.14, 0.22)
        z0 = L.STREAM_BED - 0.3
        o_out, o_top, o_toe = -0.5, rng.uniform(0.4, 0.55), rng.uniform(1.7, 1.9)
        bot = [a2 + nv * o_out, b2 + nv * o_out, b2 + nv * o_toe, a2 + nv * o_toe]
        top = [a2 + nv * o_out, b2 + nv * o_out, b2 + nv * o_top, a2 + nv * o_top]
        bot = [(q.x, q.y, z0) for q in bot]
        top = [(q.x, q.y, zt) for q in top]
        ST.hexa(tb, bot, top, ST.WD if rng.random() < 0.28 else ST.WL, 0.0)
        nb += 1
    tb.finish()
    return nb


# ------------------------------------------------------------------ pavimentos
# ruas sobre o gramado: rejunte 0,1 acima da grama e lajes 0,12..0,17 acima do rejunte (regra de folga >= 0,1)
GROUT_UP = 0.12
STREET_H = 0.38


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


def pave_polar(mb, r0, r1, a0, a1, z, rng, row=3.2, blen=4.2, gap=0.2, stagger=0, m=PAVE, avoid=None, h=0.26):
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
            _stone(mb, pts, z, rng, m, h)
            n += 1
    return n


def pave_rect(mb, origin, ang, x0, x1, y0, y1, z, rng, tile=(3.2, 3.0), gap=0.2, m=PAVE, outside_r=None,
              grout=True, h=STREET_H):
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
            mb.prism(IL.ccw(g), z - 0.3, z + GROUT_UP, "Stone_TerGrout", 0.0)
        elif outside_r is not None:
            # base de rejunte em faixas (acompanha o corte do arco)
            yy = y0
            while yy < y1 - 0.05:
                yb = min(yy + 1.5, y1)
                q = cut([W(x0, yy), W(x1, yy), W(x1, yb), W(x0, yb)])
                if len(q) >= 3 and abs(IL.area(q)) > 0.3:
                    mb.prism(IL.ccw(q), z - 0.3, z + GROUT_UP, "Stone_TerGrout", 0.0)
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
                    _stone(mb, pts, z, rng, m, h)
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
    # (sem entrar no corpo/capa dos muros radiais de 26 e 200 graus, 1,4 + 0,3 de espessura)
    n += pave_polar(mb, r_out, L.T1_WALL_R - 0.1, a0 + 1.3, a1 - 1.3, L.RING, rng, row=3.6, blen=4.6, stagger=1)
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
            mb.prism(IL.ccw(q), z1 - 0.3, z1 + GROUT_UP, "Stone_TerGrout", 0.0)
    n = pave_polar(mb, ra, rb, a_s, a_e, z1, rng, row=3.5, blen=4.0, avoid=avoid, h=STREET_H)
    ro = rb + 0.25
    # eixo central: da rua em arco ate o pe da escada do T2
    n += pave_rect(mb, (0.0, 0.0), 0.0, -6.0, 6.0, rb - 1.0, L.T2_STAIR_Y0 - 0.15, z1, rng, outside_r=ro)
    # ramal ao ramen (-38,107): da rua em arco ate a frente (y 101); a casa (38,107) tem caminho proprio (paths)
    rx = L.RAMEN[0]
    n += pave_rect(mb, (0.0, 0.0), 0.0, rx - 3.9, rx + 3.9, 93.0, 100.9, z1, rng, tile=(2.6, 2.8), outside_r=ro)
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


# ------------------------------------------------------------------ caminhos de lajota das casas (4 de largura)
PATH_W = 4.0
ARC_RO = 103.55          # borda de fora da rua em arco do T1 (rb + 0,25)


def _disk(r, n=160):
    return [(r * math.cos(math.tau * i / n), r * math.sin(math.tau * i / n)) for i in range(n)]


def _rect_rot(c, ang, hl, hw):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))]


def _house_rects(pad=0.55):
    """pegadas das casas/predios que os caminhos contornam (casa + base de pedra)"""
    out = []
    for hx, hy, w, d, yaw, roof in L.HOUSES_T1 + L.HOUSES_T2 + L.EAST_HOUSES:
        out.append(_rect_rot((hx, hy), yaw, w / 2 + pad, d / 2 + pad))
    hx, hy, w, d = L.HOUSES_T2[1][:4]
    out.append(_rect_rot((hx - 1.5, hy - 0.5), 0.0, w * 0.45 + pad, 6.0 + pad))     # pegada real (il_houses)
    out.append(_rect_rot((L.EAST_HOUSES[0][0], L.EAST_HOUSES[0][1]), 0.0, 7.9 + 0.2, 6.9 + 0.2))   # podio casa leste
    mx, my, mw, md = L.MILL
    out.append(_rect_rot((mx, my), 0.0, mw / 2 + 0.6, md / 2 + 0.6))
    return out


def pave_path(mb, pts, z, rng, w=PATH_W, tile=(2.6, 2.0), gap=0.2, avoid=(), m=PAVE):
    """calcada de lajes ao longo de uma polilinha: cada trecho e um retangulo cortado pelas BISSETRIZES nas juncoes
    (lajes de trechos vizinhos nunca se sobrepoem: sem z-fighting), rejunte 0,1 acima do gramado, lajes 0,12..0,17
    acima do rejunte; avoid = poligonos que o caminho contorna (casas, rua em arco, rua da saida)"""
    P = [Vector((q[0], q[1], 0.0)) for q in pts]
    n = len(P)
    cnt = 0

    def keep(poly, cl):
        for nx, ny, c in cl:
            poly = IL.clip(poly, nx, ny, c)
            if len(poly) < 3:
                return []
        out = [poly]
        for av in avoid:
            out = ST.poly_bool_many(out, av, "diff")
        return [q for q in out if len(q) >= 3 and abs(IL.area(q)) > 0.25]
    for i in range(n - 1):
        a, b = P[i], P[i + 1]
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        t = d / ln
        cl = []
        e0 = e1 = 0.0
        if i > 0:
            bis = ((a - P[i - 1]).normalized() + t).normalized()
            cl.append((-bis.x, -bis.y, -(bis.x * a.x + bis.y * a.y)))
            e0 = w
        if i < n - 2:
            bis = (t + (P[i + 2] - b).normalized()).normalized()
            cl.append((bis.x, bis.y, bis.x * b.x + bis.y * b.y))
            e1 = w
        ca, sa = t.x, t.y

        def W(x, y):
            return (a.x + x * ca - y * sa, a.y + x * sa + y * ca)
        for g in keep([W(-e0, -w / 2), W(ln + e1, -w / 2), W(ln + e1, w / 2), W(-e0, w / 2)], cl):
            mb.prism(IL.ccw(g), z - 0.3, z + GROUT_UP, "Stone_TerGrout", 0.0)
        y = -w / 2
        row = 0
        while y < w / 2 - 0.3:
            yb = min(y + tile[1], w / 2)
            x = -e0 - (tile[0] * 0.5 if row % 2 else 0.0)
            while x < ln + e1 - 0.3:
                xb = min(x + tile[0] * rng.uniform(0.85, 1.15), ln + e1)
                xa = max(x, -e0)
                if xb - xa > 0.6:
                    h_ = gap * 0.5
                    slab = [W(xa + h_, y + h_), W(xb - h_, y + h_), W(xb - h_, yb - h_), W(xa + h_, yb - h_)]
                    for q in keep(slab, cl):
                        _stone(mb, q, z, rng, m, STREET_H)
                        cnt += 1
                x = xb
            y = yb
            row += 1
    return cnt


def _exit_street_poly():
    ang = math.radians(L.EXIT_DEG)
    r0, r1 = 102.3, math.hypot(*L.EXIT_START)
    return _rect_rot(((r0 + r1) / 2 * math.cos(ang), (r0 + r1) / 2 * math.sin(ang)), ang, (r1 - r0) / 2, 7.3)


def house_paths_spec():
    """(nome, polilinha, nivel, rota do QA) de cada caminho: da frente da casa ate a rua/anel mais proximo.
    T1: fachada sul -> rua em arco (ou rua da saida); T2: fachada -> travessa ate os ramais da praca do T2;
    vale leste: fachada oeste -> trilha pela margem leste do riacho ate a ponte em arco"""
    out = []
    h0 = L.HOUSES_T1[0]
    xm = h0[0] - h0[2] / 2 + 5.5                           # meio do bloco principal da casa (38,107)
    y_f = h0[1] - h0[3] / 2 - 0.55
    out.append(("CASA_T1_38", [(xm, y_f), (xm, 94.0)], L.T1, [(xm, y_f - 1.4), (xm, 99.0)]))
    h1 = L.HOUSES_T1[1]
    y_f = h1[1] - h1[3] / 2 - 0.55
    out.append(("CASA_T1_-84", [(h1[0], y_f), (h1[0], y_f - 3.5), (-64.5, 76.4)], L.T1,
                [(h1[0], y_f - 1.4), (h1[0], y_f - 3.5), (-66.5, 79.0)]))
    h2 = L.HOUSES_T1[2]
    x2 = h2[0] - h2[2] / 2 + 6.0
    y_f = h2[1] - h2[3] / 2 - 0.55
    out.append(("CASA_T1_84", [(x2, y_f), (x2, 88.0)], L.T1, [(x2, y_f - 1.4), (x2, 90.0)]))
    h3 = L.HOUSES_T1[3]
    y_f = h3[1] - h3[3] / 2 - 0.55
    out.append(("CASA_T1_-112", [(h3[0], y_f), (h3[0], y_f - 3.6), (-83.3, 55.2)], L.T1,
                [(h3[0], y_f - 1.4), (h3[0], y_f - 3.6), (-86.0, 57.0)]))
    # T2 oeste: travessa y 135,5 da casa (-126,136) (fachada leste) ate o ramal da loja; ramal da casa (-98,160)
    t0, t2 = L.HOUSES_T2[0], L.HOUSES_T2[2]
    xe = t2[0] + t2[2] / 2 + 0.55
    out.append(("CASA_T2_-126", [(xe, 135.5), (-65.0, 135.5)], L.T2, [(xe + 1.4, 135.5), (-67.0, 135.5)]))
    y_f = t0[1] - t0[3] / 2 - 0.55
    out.append(("CASA_T2_-98", [(t0[0], y_f), (t0[0], 137.5)], L.T2, [(t0[0], y_f - 1.4), (t0[0], 135.5)]))
    # T2 leste: casa (96,5; 149,5) (pegada real 1,5 a oeste) -> travessa y 135,4 -> ramal do predio azul leste
    t1 = L.HOUSES_T2[1]
    x1 = t1[0] - 1.5
    y_f = t1[1] - 0.5 - 6.0 - 0.55
    out.append(("CASA_T2_96", [(x1, y_f), (x1, 137.4)], L.T2, [(x1, y_f - 1.4), (x1, 135.4), (67.0, 135.4)]))
    out.append(("CASA_T2_96_travessa", [(x1 + 2.0, 135.4), (65.0, 135.4)], L.T2, None))
    # vale leste: casa (136,36) -> margem leste (por fora do apoio da roda d'agua) -> casa (134,-26) -> ponte em arco
    e0, e1 = L.EAST_HOUSES
    xw1 = e1[0] - e1[2] / 2 - 2.55
    lane = [(xw1, e1[1]), (126.3, 30.5), (129.9, 20.5), (130.0, 4.0), (126.8, -8.0), (123.8, -19.5), (123.8, -37.0)]
    out.append(("CASAS_LESTE", lane, L.G, [(xw1 - 0.5, e1[1]), (126.3, 30.5), (129.9, 20.5), (130.0, 4.0),
                                           (126.8, -8.0), (123.8, -19.5), (123.8, -36.0)]))
    return out


def house_paths(rng):
    mb = MB("TER_Paths", C, rng, detail="far")
    houses = _house_rects()
    arc = _disk(ARC_RO)
    ex = _exit_street_poly()
    n = 0
    for name, pts, z, _ in house_paths_spec():
        av = list(houses) + ([arc, ex] if z == L.T1 else [])
        n += pave_path(mb, pts, z, rng, avoid=av)
    mb.finish()
    return n


def pit_floor(rng):
    mb = MB("TER_Pit_Floor", C, rng, detail="far")
    IL.prism(mb, IL.arc_pts(L.PIT_R + 0.2, 0.0, 360.0, 3.75)[:-1], L.PIT - 1.2, L.PIT, "Dirt_Pit")
    # manchas mais escuras (terra revolvida) - planas, 0,12 acima do piso (folga >= 0,1) e sem se sobrepor
    placed = []
    k = 0
    for t in range(90):
        if len(placed) >= 22:
            break
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
                sc = (L.PIT_R - 1.0) / math.hypot(px, py)
                px, py = px * sc, py * sc
            pts.append((px, py))
        pts = IL.ccw(pts)
        if any(ST.poly_bool(pts, q, "inter") for q in placed):
            continue
        placed.append(pts)
        m = "Dirt_TerPatch" if k % 3 else "Dirt_Pit_B"
        mb.prism(pts, L.PIT - 0.1, L.PIT + 0.12, m, 0.0)
        k += 1
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    lawns(random.Random(11))
    pit_floor(random.Random(12))
    ring_paving(random.Random(13))
    streets(random.Random(14))
    house_paths(random.Random(16))
    stream_bed(random.Random(15))
    ST.walls(random.Random(21))
    ST.guards(random.Random(22))
    ST.stairs(random.Random(23))
    R.upper_cliffs(random.Random(31))
    R.shelf_and_lower(random.Random(32))
    R.back_massif(random.Random(33))


_register_paths()
