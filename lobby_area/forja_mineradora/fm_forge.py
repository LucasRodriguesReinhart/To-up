# fm_forge - FORJA DO IGNIS (asset heroi). Planta:
#   salao x-20..20 y4..22 (piso 5) | lareira aberta na fachada (x-8..8, y-1.5..4) | Ignis y-5 | bigorna y-10
#   torre-chamine r10 em (0,30) com fornalha e foles | ala esq. = recebimento de minerio (trilho) + loft/varanda
#   ala dir. = casa dos foles (eixo da roda d'agua) + balcao de venda na frente
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, col_ramp, marker, light, arc, bezier
from fm_parts import (Frame, stairs, masonry_wall, timber_wall, arch, window_glow, banner, emblem_hammers,
                      lantern, hanging_lantern, crate, barrel, crystal_cluster, fence, pave_ring, pave_poly, P3, frustum)
import fm_layout as L

C = "03_FORGE"
F0 = L.FLOOR
FL = L.FL


def ring_masonry(mb, cx, cy, r_in, r_out, z0, z1, rng, course=2.0, gaps=(), m="Stone_Light", m2="Stone_Dark",
                 mix=0.25, taper=0.0):
    """anel de alvenaria (torre). gaps = [(ang_centro_graus, meia_largura_studs, zlo, zhi)]"""
    z = z0
    row = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        f = (z - z0) / max(1e-3, (z1 - z0))
        ri = r_in - taper * f
        ro = r_out - taper * f
        rm = (ri + ro) / 2
        n = max(8, int(2 * math.pi * rm / 2.8))
        off = (0.5 if row % 2 else 0.0)
        for i in range(n):
            a = (i + off) / n * math.tau
            skip = False
            for (gc, ghw, zl, zh) in gaps:
                da = math.atan2(math.sin(a - D(gc)), math.cos(a - D(gc)))
                if abs(da * rm) < ghw + 1.4 and z + h > zl + 0.01 and z < zh - 0.01:
                    skip = True
                    break
            if skip:
                continue
            chord = 2 * ro * math.sin(math.pi / n) + 0.05
            c = Vector((cx + math.cos(a) * rm, cy + math.sin(a) * rm, z + h / 2))
            mm = m2 if rng.random() < mix else m
            mb.box((ro - ri + rng.uniform(-0.05, 0.15), chord - 0.12, h - 0.1), c, (0, 0, a), mm, 0.14)
        z += h
        row += 1


def chain(mb, a, b, sag=1.5, link=0.7, m="Metal_Dark"):
    a, b = Vector(a), Vector(b)
    L_ = (b - a).length
    n = max(2, int(L_ / link))
    pts = []
    for i in range(n + 1):
        t = i / n
        p = a + (b - a) * t
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for i, (p0, p1) in enumerate(zip(pts, pts[1:])):
        mb.beam(p0, p1, 0.18 if i % 2 else 0.42, 0.42 if i % 2 else 0.18, m, 0.0)


def pipe(mb, pts, r=1.1, m="Metal_Dark", flange_m="Metal_Iron", flange_step=6.0):
    pts = [Vector(p) for p in pts]
    mb.tube(pts, r, m, 12)
    from fm_lib import resample
    for p in resample(pts, flange_step)[1:-1] + [pts[0], pts[-1]]:
        # flange: anel curto orientado pela tangente mais proxima
        i = min(range(len(pts) - 1), key=lambda k: (pts[k] - p).length + (pts[k + 1] - p).length)
        t = (pts[i + 1] - pts[i]).normalized()
        mb.rod(p - t * 0.25, p + t * 0.25, r * 1.28, flange_m, 12)


# ------------------------------------------------------------------ fundacao, tablado, piso
def foundation(rng):
    mb = MB("FORGE_Foundation_Dais", C, rng)
    x0, y0, x1, y1 = L.FORGE_HALL
    # plinto do salao e das alas (base de pedra aparente)
    mb.box2((x0 - 0.8, y0 - 0.2, F0 - 1.0), (x1 + 0.8, y1, FL - 0.3), "Stone_Dark", 0.2)
    mb.box2((x0 - 0.8, y0 - 0.2, FL - 0.3), (x1 + 0.8, y0 + 2.2, FL), "Stone_Dark", 0.1)
    for w in (L.FORGE_WING_L, L.FORGE_WING_R):
        mb.box2((w[0] - 0.8, w[1] - 0.6, F0 - 1.0), (w[2] + 0.8, w[3] + 0.6, F0 + 0.3), "Stone_Dark", 0.2)
    # piso interno do salao (lajes)
    pave_poly(mb, [(x0 + 2.2, y0 + 2.2), (x1 - 2.2, y0 + 2.2), (x1 - 2.2, y1 - 2.2), (x0 + 2.2, y1 - 2.2)],
              FL - 0.3, rng, tile=2.6, h=0.3, grout=False)
    # tablado semicircular diante da lareira (1 degrau)
    cx, cy = L.DAIS_C
    R = L.DAIS_R + 1
    poly = [(cx + math.cos(D(a)) * R, cy + math.sin(D(a)) * R) for a in range(180, 361, 10)] + [(R, y0), (-R, y0)]
    mb.prism(poly, F0 - 0.5, FL - 0.35, "Stone_Dark", bevel=0.25)
    pave_ring(mb, cx, cy, 0.0, R - 1.2, FL - 0.35, rng, 180, 360, ring_w=2.4, h=0.35, m="Stone_Paving")
    mb.box2((-R + 1, cy, FL - 0.35), (R - 1, y0 - 0.2, FL), "Stone_Paving", 0.1)
    # meio-fio do tablado
    for a in range(180, 360, 8):
        p = Vector((cx + math.cos(D(a + 4)) * (R - 0.6), cy + math.sin(D(a + 4)) * (R - 0.6), FL - 0.2))
        mb.box((1.2, 2 * R * math.sin(D(4)) - 0.1, 0.9), p, (0, 0, D(a + 4)), "Stone_Light", 0.15)
    mb.finish()
    col_box2("Forge", (-R, cy, F0 - 1), (R, y0, FL))
    col_box("Forge", (R * 1.4, R * 0.9, FL - F0 + 1), (cx, cy - R * 0.45, (F0 - 1 + FL) / 2))
    col_box("Forge", (R * 0.95, R * 0.35, FL - F0 + 1), (cx, cy - R * 0.93, (F0 - 1 + FL) / 2))
    col_box2("Forge", (x0, y0, F0 - 1), (x1, y1, FL))


# ------------------------------------------------------------------ salao principal
def hall(rng):
    x0, y0, x1, y1 = L.FORGE_HALL
    t = 2.2
    zs = 16.0       # topo da alvenaria
    ze = 24.0       # beiral
    mb = MB("FORGE_Hall_Walls", C, rng)
    # parede frontal (y0..y0+t): portas em x=+-14.5 (6 de vao, arco)
    fy = y0 + t / 2
    doors = [(-14.5, 6.0), (14.5, 6.0)]
    ops = [(dx + 20 - w / 2, dx + 20 + w / 2, FL, 15.0, 3.0) for dx, w in doors]
    masonry_wall(mb, (x0, fy), (x1, fy), FL, zs, t, rng, openings=ops)
    for dx, w in doors:
        arch(mb, (dx, fy, 0), 0.0, w, 12.0, 3.0, t + 0.3, "Stone_Light", "Stone_Light", n=9, band=1.2)
    # paredes laterais (portas internas para as alas: y 9..15)
    for sx in (x0 + t / 2, x1 - t / 2):
        masonry_wall(mb, (sx, y0), (sx, y1), FL, zs, t, rng, openings=[(5.0, 11.0, FL, 14.0, 2.5)])
        arch(mb, (sx, y0 + 8.0, 0), D(90), 6.0, 11.5, 2.5, t + 0.3, n=7, band=1.1)
    # parede de fundo (encontra a torre): trechos laterais + arco grande para a fornalha
    by = y1 - t / 2
    masonry_wall(mb, (x0, by), (-4.0, by), FL, zs, t, rng)
    masonry_wall(mb, (4.0, by), (x1, by), FL, zs, t, rng)
    # andar enxaimel (16..24) em volta: frente com janelas, laterais cegas (alas encostam), fundo
    timber_wall(mb, (x0, fy), (x1, fy), zs, ze, t * 0.8, rng,
                openings=[(3.5, 7.5, 18.0, 22.0), (32.5, 36.5, 18.0, 22.0)], post=3.3)
    for s0, s1 in ((3.5, 7.5), (32.5, 36.5)):
        window_glow(mb, (x0, fy), (x1, fy), s0, s1, 18.0, 22.0, t * 0.8)
    for sx in (x0 + t / 2, x1 - t / 2):
        timber_wall(mb, (sx, y0), (sx, y1), zs, ze, t * 0.8, rng, post=3.6)
    timber_wall(mb, (x0, by), (x1, by), zs, ze, t * 0.8, rng, post=3.4)
    # oitoes (frente e fundo) com enxaimel e emblema
    for gy in (fy, by):
        mb.gable_wall(0, gy, 40.0, ze, 13.0, t * 0.8, "Y", "Plaster")
        for s in (-1, 1):
            for k in range(1, 5):
                xx = s * k * 4.4
                zt = ze + 13.0 * (1 - abs(xx) / 20.0)
                off = -t * 0.45 if gy == fy else t * 0.45
                mb.beam((xx, gy + off, ze), (xx, gy + off, zt - 0.3), 0.5, 0.7, "Wood_Dark", 0.06)
        off = -t * 0.45 if gy == fy else t * 0.45
        mb.beam((-20, gy + off, ze + 0.4), (20, gy + off, ze + 0.4), 0.8, 0.9, "Wood_Dark", 0.08)
    # placa do emblema no oitao frontal (losango escuro + martelos cruzados)
    ez = ze + 6.2
    mb.cyl(4.6, 0.6, (0, y0 - 0.35, ez), (D(90), D(45), 0), "Wood_Dark", 4, bevel=0.15)
    mb.cyl(3.9, 0.5, (0, y0 - 0.65, ez), (D(90), D(45), 0), "Metal_Dark", 4, bevel=0.1)
    emblem_hammers(mb, Vector((0, y0 - 0.9, ez)), 0.0, s=1.05, m="Emblem_Cream", off=0.1)
    # beiral em consolos de madeira (frente)
    for xx in range(-18, 19, 6):
        mb.beam((xx, y0 - 0.2, ze - 2.2), (xx, y0 - 1.8, ze - 0.2), 0.6, 0.7, "Wood_Dark", 0.06)
    # contrafortes de pedra nos cantos
    for cx_ in (x0 - 0.4, x1 + 0.4):
        mb.box((2.6, 2.6, zs - FL + 1), (cx_, y0 + 0.4, (FL + zs) / 2 - 0.5), (0, 0, 0), "Stone_Dark", 0.3)
        mb.box((3.0, 3.0, 0.8), (cx_, y0 + 0.4, zs + 0.2), (0, 0, 0), "Stone_Light", 0.2)
    mb.finish()

    # telhado (cumeeira em Y) + tesouras internas
    rf = MB("FORGE_Hall_Roof", C, rng)
    rf.gable_roof(0, (y0 + y1) / 2 - 0.5, 40.0, 17.0, ze, 13.0, "Roof", thick=0.9, over=1.8, axis="Y")
    for yy in (8.0, 13.0, 18.0):
        rf.beam((-19, yy, ze - 0.4), (19, yy, ze - 0.4), 0.9, 1.1, "Wood_Dark", 0.08)
        rf.beam((0, yy, ze - 0.4), (0, yy, ze + 12.0), 0.8, 0.8, "Wood_Dark", 0.08)
        for s in (-1, 1):
            rf.beam((s * 19, yy, ze), (0, yy, ze + 12.4), 0.8, 0.9, "Wood_Dark", 0.08)
            rf.beam((s * 9, yy, ze - 0.2), (0, yy, ze + 6), 0.6, 0.6, "Wood_Dark", 0.06)
    rf.finish()

    # colisao do salao
    A = "Forge"
    for a_, b_ in ((-20, -17.5), (-11.5, 11.5), (17.5, 20)):
        col_box2(A, (a_, y0, FL), (b_, y0 + t, ze))
    col_box2(A, (-17.5, y0, 15.0), (-11.5, y0 + t, ze))
    col_box2(A, (11.5, y0, 15.0), (17.5, y0 + t, ze))
    for sx0, sx1 in ((x0, x0 + t), (x1 - t, x1)):
        col_box2(A, (sx0, y0, FL), (sx1, y0 + 5, ze))
        col_box2(A, (sx0, y0 + 11, FL), (sx1, y1, ze))
        col_box2(A, (sx0, y0 + 5, 14.0), (sx1, y0 + 11, ze))
    col_box2(A, (x0, y1 - t, FL), (-5.0, y1, ze))
    col_box2(A, (5.0, y1 - t, FL), (x1, y1, ze))


# ------------------------------------------------------------------ lareira aberta (fachada)
def hearth(rng):
    y0 = L.FORGE_HALL[1]
    mb = MB("FORGE_Hearth", C, rng)
    fy = -1.5
    # corpo de pedra: frente com arco grande, laterais, topo
    masonry_wall(mb, (-8, fy + 1.1), (8, fy + 1.1), FL, 18.0, 2.2, rng, openings=[(2.5, 13.5, FL, 13.5, 3.5)],
                 m="Stone_Light", m2="Stone_Dark", course=1.5, mix=0.35)
    arch(mb, (0, fy + 1.1, 0), 0.0, 11.0, 10.0, 3.5, 2.6, "Stone_Dark", "Metal_Brass", n=11, band=1.4)
    for sx in (-7.0, 7.0):
        masonry_wall(mb, (sx, fy), (sx, y0), FL, 18.0, 2.0, rng, course=1.5)
    mb.box2((-8.6, fy - 0.6, 18.0), (8.6, y0 + 0.4, 19.2), "Stone_Dark", 0.3)
    mb.box2((-7.6, fy - 0.1, 19.2), (7.6, y0, 21.0), "Stone_Light", 0.3)
    # soleira do fogo (leito elevado), brasas e chamas
    mb.box2((-5.4, fy + 0.4, FL), (5.4, y0, FL + 1.8), "Stone_Dark", 0.2)
    mb.box2((-4.6, fy + 1.4, FL + 1.8), (4.6, y0 - 0.2, FL + 2.3), "Forge_Emissive", 0.1)
    for i in range(22):
        x = rng.uniform(-4.2, 4.2)
        y = rng.uniform(fy + 1.8, y0 - 0.6)
        h = rng.uniform(2.0, 5.5) * (1.25 - abs(x) / 8.0)
        mb.cyl(rng.uniform(0.6, 1.3), h, (x, y, FL + 2.2 + h / 2), (rng.uniform(-0.2, 0.2), rng.uniform(-0.2, 0.2), 0),
               "Forge_Emissive" if i % 3 else "Lantern_Glow", 5, r2=0.05, bevel=0.0)
    for i in range(18):
        mb.rock((rng.uniform(-4.4, 4.4), rng.uniform(fy + 1.6, y0 - 0.4), FL + 2.3), (0.9, 0.8, 0.5), "Metal_Heated", 0)
    # fundo do nicho escurecido (fuligem)
    mb.box2((-5.5, y0 - 0.3, FL), (5.5, y0, 14.0), "Metal_Dark", 0.0)
    # coifa de ferro sobre o arco
    frustum(mb, (0, fy - 1.4, 13.9), 13.0, 3.2, 9.0, 1.2, 3.6, "Metal_Dark", top_off=(0.0, 1.0))
    mb.box((13.4, 3.4, 0.5), (0, fy - 1.4, 13.9), (0, 0, 0), "Metal_Iron", 0.08)
    for x in (-5.5, -2.75, 0, 2.75, 5.5):
        mb.cyl(0.28, 0.3, (x, fy - 3.15, 14.2), (D(90), 0, 0), "Metal_Brass", 6, bevel=0.0)
    # correntes decorativas da lareira ate os cantos do salao
    for s in (-1, 1):
        chain(mb, (s * 8.2, fy - 0.6, 17.6), (s * 17.6, y0 - 0.3, 20.8), sag=2.2)
        chain(mb, (s * 8.2, fy - 0.6, 12.8), (s * 11.2, y0 - 0.3, 17.5), sag=1.0)
    # duto da lareira: sai do topo e sobe para a torre
    # chamine curta da lareira (sai pelo topo do bloco, abaixo do emblema do oitao)
    mb.box((5.0, 3.6, 3.4), (0, 1.0, 22.7), (0, 0, 0), "Stone_Dark", 0.25)
    mb.box((5.8, 4.4, 0.6), (0, 1.0, 24.6), (0, 0, 0), "Metal_Dark", 0.08)
    mb.box((3.2, 2.2, 0.3), (0, 1.0, 24.95), (0, 0, 0), "Forge_Emissive", 0.0)
    mb.finish()
    col_box2("Forge", (-8.6, fy - 0.6, FL), (8.6, y0, 21.0))
    # estandartes vermelhos ao lado da lareira
    bn = MB("FORGE_Banners", C, rng)
    for s in (-1, 1):
        banner(bn, (s * 9.9, y0 - 0.45, 20.8), 0.0, w=2.8, h=6.2, cloth="Cloth_Red", trim="Metal_Brass", emblem="hammers")
    bn.finish()


# ------------------------------------------------------------------ torre-chamine
def chimney(rng):
    cx, cy = L.CHIMNEY
    R = L.CHIMNEY_R
    top = L.CHIMNEY_TOP
    mb = MB("FORGE_Chimney_Tower", C, rng)
    # base (alvenaria grossa) com arco frontal (para o salao) e porta traseira
    gaps = [(270.0, 4.0, FL, 17.0), (90.0, 2.8, FL, 13.0)]
    ring_masonry(mb, cx, cy, R - 2.2, R, F0 - 0.5, 26.0, rng, course=2.0, gaps=gaps, mix=0.3)
    # fuste afilando (26 -> topo), fendas iluminadas voltadas para a frente
    slits = [(260.0, 0.9, 70.0, 80.0), (270.0, 0.9, 70.0, 80.0), (280.0, 0.9, 70.0, 80.0),
             (265.0, 0.9, 50.0, 57.0), (275.0, 0.9, 50.0, 57.0), (90.0, 0.9, 62.0, 70.0)]
    ring_masonry(mb, cx, cy, R - 2.8, R - 0.9, 26.0, top - 8, rng, course=2.2, gaps=slits, mix=0.35, taper=1.1)
    # cintas de ferro
    for z, rr in ((26.0, R - 0.55), (40.0, R - 1.05), (58.0, R - 1.4), (84.0, R - 1.85)):
        mb.cyl(rr + 0.45, 1.0, (cx, cy, z), (0, 0, 0), "Metal_Iron", 24, bevel=0.1, caps=False)
        for i in range(12):
            a = i / 12 * math.tau
            mb.cyl(0.28, 0.2, (cx + math.cos(a) * (rr + 0.55), cy + math.sin(a) * (rr + 0.55), z), (0, D(90), a),
                   "Metal_Brass", 6, bevel=0.0)
    # fendas: vidro incandescente recuado
    for (ac, hw, zl, zh) in slits:
        a = D(ac)
        rr = R - 1.9 - 1.1 * ((zl + zh) / 2 - 26) / (top - 8 - 26)
        mb.box((0.6, 1.3, zh - zl), (cx + math.cos(a) * rr, cy + math.sin(a) * rr, (zl + zh) / 2), (0, 0, a),
               "Forge_Emissive", 0.0)
    # coroa: colar alargado + ameias + borda incandescente
    zc = top - 8
    mb.cyl(R - 1.0, 3.0, (cx, cy, zc + 1.5), (0, 0, 0), "Stone_Dark", 20, r2=R + 0.6, bevel=0.2, caps=False)
    mb.cyl(R + 0.9, 2.2, (cx, cy, zc + 4.1), (0, 0, 0), "Metal_Dark", 20, bevel=0.2, caps=False)
    mb.cyl(R - 0.2, 0.8, (cx, cy, zc + 5.5), (0, 0, 0), "Forge_Emissive", 20, bevel=0.0, caps=False)
    for i in range(10):
        a = i / 10 * math.tau
        mb.box((2.4, 2.2, 2.6), (cx + math.cos(a) * (R + 0.2), cy + math.sin(a) * (R + 0.2), zc + 6.4), (0, 0, a),
               "Stone_Light", 0.2)
    # boca interna incandescente (visivel de cima e de longe)
    mb.cyl(R - 2.2, 0.4, (cx, cy, zc + 4.0), (0, 0, 0), "Forge_Emissive", 20, bevel=0.0)
    mb.finish()
    A = "Forge"
    # colisao do anel: 16 caixas, sem a frente (arco) e o fundo (porta)
    for i in range(16):
        a = (i + 0.5) / 16 * math.tau
        deg = math.degrees(a) % 360
        c = Vector((cx + math.cos(a) * (R - 1.1), cy + math.sin(a) * (R - 1.1), (F0 + 30) / 2))
        near_front = abs(((deg - 270 + 180) % 360) - 180) < 20
        near_back = abs(((deg - 90 + 180) % 360) - 180) < 14
        if near_front or near_back:
            col_box(A, (2.2, 2 * R * math.sin(math.pi / 16) + 0.3, 30 - 17.0), (c.x, c.y, 17.0 + (30 - 17.0) / 2),
                    (0, 0, a))
            continue
        col_box(A, (2.2, 2 * R * math.sin(math.pi / 16) + 0.3, 30 - F0), c, (0, 0, a))
    col_box("Forge", (2 * R, 2 * R, top - 30), (cx, cy, (30 + top) / 2))


# ------------------------------------------------------------------ fornalha e foles (dentro da torre)
def furnace(rng):
    cx, cy = L.CHIMNEY
    mb = MB("FORGE_Furnace_Interior", C, rng)
    mb.cyl(8.2, FL - 0.3 - (F0 - 1.0), (cx, cy, (FL - 0.3 + F0 - 1.0) / 2), (0, 0, 0), "Stone_Grout", 20, bevel=0.0)
    pave_poly(mb, [(cx + math.cos(D(a)) * 7.6, cy + math.sin(D(a)) * 7.6) for a in range(0, 360, 20)], FL - 0.3, rng,
              tile=2.2, h=0.3, grout=False)
    col_box("Forge", (16.0, 16.0, 1.0), (cx, cy, FL - 0.5), (0, 0, 0), "Floor")
    # cadinho/fornalha no fundo da torre
    fx, fy = cx, cy + 2.2
    mb.cyl(3.6, 5.0, (fx, fy, FL + 2.5), (0, 0, 0), "Stone_Dark", 12, bevel=0.3)
    mb.cyl(3.7, 3.0, (fx, fy, FL + 6.4), (0, 0, 0), "Metal_Dark", 12, r2=1.4, bevel=0.2)
    mb.cyl(1.4, 20.0, (fx, fy, FL + 17.8), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    mb.box((3.0, 1.2, 2.4), (fx, fy - 3.3, FL + 2.6), (0, 0, 0), "Forge_Emissive", 0.1)
    arch(mb, (fx, fy - 3.4, 0), 0.0, 3.2, FL + 3.6, 1.0, 1.0, "Stone_Light", "Metal_Brass", n=5, band=0.7)
    # calha de fundido ate a lingoteira
    mb.beam((fx, fy - 3.6, FL + 1.6), (fx - 3.5, fy - 6.5, FL + 0.9), 0.9, 0.5, "Metal_Iron", 0.05)
    mb.box((3.2, 2.0, 0.7), (fx - 4.2, fy - 7.0, FL + 0.35), (0, 0, D(-40)), "Metal_Heated", 0.05)
    # carvao
    for i in range(10):
        mb.rock((cx + 5.0 + rng.uniform(-1, 1), cy - 1 + rng.uniform(-2, 2), FL + 0.3), (1.3, 1.2, 0.9), "Metal_Dark", 0)
    light("L_Furnace", "POINT", (fx, fy - 4.5, FL + 3.0), 900, (1.0, 0.45, 0.12), 1.0)
    mb.finish()
    col_box("Forge", (7.6, 7.6, 7.0), (fx, fy, FL + 3.5))


# ------------------------------------------------------------------ alas
def wings(rng):
    t = 1.6
    zs = 8.5
    ze = 19.5
    for side, w in (("L", L.FORGE_WING_L), ("R", L.FORGE_WING_R)):
        x0, y0, x1, y1 = w
        cx = (x0 + x1) / 2
        mb = MB("FORGE_Wing_" + side, C, rng)
        outer = x0 if side == "L" else x1
        ox = outer + (t / 2 if side == "L" else -t / 2)
        # frente (y0): base de pedra + enxaimel; L: porta do loft no alto; R: porta para o balcao
        fy = y0 + t / 2
        if side == "L":
            masonry_wall(mb, (x0, fy), (x1, fy), F0, zs, t, rng, openings=[(2.0, 6.0, F0, 8.5)])
            timber_wall(mb, (x0, fy), (x1, fy), zs, ze, t * 0.8, rng,
                        openings=[(2.0, 6.0, zs, 11.0), (8.5, 12.5, 12.5, 19.2)], post=3.5)
            window_glow(mb, (x0, fy), (x1, fy), 2.0, 6.0, F0 + 0.8, zs, t * 0.8)
            window_glow(mb, (x0, fy), (x1, fy), 2.0, 6.0, zs, 11.0, t * 0.8)
        else:
            masonry_wall(mb, (x0, fy), (x1, fy), F0, zs, t, rng, openings=[(9.5, 12.5, F0, 8.5)])
            timber_wall(mb, (x0, fy), (x1, fy), zs, ze, t * 0.8, rng,
                        openings=[(9.5, 12.5, zs, 11.5), (2.5, 6.0, 12.0, 15.5)], post=3.5)
            window_glow(mb, (x0, fy), (x1, fy), 2.5, 6.0, 12.0, 15.5, t * 0.8)
        # fundo (y1)
        by = y1 - t / 2
        masonry_wall(mb, (x0, by), (x1, by), F0, zs, t, rng)
        timber_wall(mb, (x0, by), (x1, by), zs, ze, t * 0.8, rng, openings=[(5.0, 9.0, 11.5, 15.0)], post=3.5)
        window_glow(mb, (x0, by), (x1, by), 5.0, 9.0, 11.5, 15.0, t * 0.8)
        # parede externa: L = portao do trilho (y 13..23); R = furo do eixo + janelas
        if side == "L":
            masonry_wall(mb, (ox, y0), (ox, y1), F0, zs, t, rng, openings=[(7.0, 17.0, F0, zs + 1)])
            timber_wall(mb, (ox, y0), (ox, y1), zs, ze, t * 0.8, rng, openings=[(7.0, 17.0, zs, 15.0)], post=3.3)
            # portao: montantes grossos, verga e folhas abertas para dentro
            for yy in (y0 + 7.0, y0 + 17.0):
                mb.box((2.0, 1.2, 15.0 - F0), (ox, yy, (F0 + 15.0) / 2), (0, 0, 0), "Wood_Dark", 0.15)
            mb.box((2.2, 12.4, 1.4), (ox, y0 + 12.0, 15.4), (0, 0, 0), "Wood_Dark", 0.15)
            for yy, ang in ((y0 + 7.6, D(70)), (y0 + 16.4, D(-70))):
                fx_ = ox + 0.8 + math.cos(ang) * 2.4
                mb.box((0.5, 4.8, 9.5), (ox + 2.6, yy + (2.2 if yy < y0 + 12 else -2.2) * 0 + 0, F0 + 5.0),
                       (0, 0, ang), "Wood_Plank", 0.1)
            for yy in (y0 + 7.0, y0 + 17.0):
                for zz in (F0 + 1.5, 13.5):
                    mb.box((2.3, 1.5, 0.5), (ox, yy, zz), (0, 0, 0), "Metal_Dark", 0.05)
        else:
            masonry_wall(mb, (ox, y0), (ox, y1), F0, zs, t, rng, openings=[(4.0, 8.0, F0 + 2.5, zs)])
            window_glow(mb, (ox, y0), (ox, y1), 4.0, 8.0, F0 + 2.5, zs, t)
            timber_wall(mb, (ox, y0), (ox, y1), zs, ze, t * 0.8, rng, openings=[(13.0, 15.0, 14.5, 16.5)], post=3.3)
        # oitoes frente/fundo
        for gy in (fy, by):
            mb.gable_wall(cx, gy, x1 - x0, ze, 7.0, t * 0.8, "Y", "Plaster")
            off = -t * 0.45 if gy == fy else t * 0.45
            mb.beam((x0, gy + off, ze + 0.3), (x1, gy + off, ze + 0.3), 0.7, 0.8, "Wood_Dark", 0.06)
            mb.beam((cx, gy + off, ze), (cx, gy + off, ze + 6.6), 0.6, 0.7, "Wood_Dark", 0.06)
        # telhado
        mb.gable_roof(cx, (y0 + y1) / 2, x1 - x0, y1 - y0, ze, 7.0, "Roof", thick=0.8, over=1.4, axis="Y")
        for yy in (y0 + 6.5, y0 + 13, y0 + 19.5):
            mb.beam((x0 + 1, yy, ze - 0.3), (x1 - 1, yy, ze - 0.3), 0.7, 0.9, "Wood_Dark", 0.06)
        # piso
        pave_poly(mb, [(x0 + t, y0 + t), (x1 - t, y0 + t), (x1 - t, y1 - t), (x0 + t, y1 - t)], F0 + 0.0, rng,
                  tile=2.4, h=0.3, grout=False)
        mb.finish()
        # colisao das alas
        A = "Forge"
        if side == "L":
            col_box2(A, (x0, y0, F0), (x0 + 2.0, y0 + t, ze))
            col_box2(A, (x0 + 6.0, y0, F0), (x0 + 8.5, y0 + t, ze))
            col_box2(A, (x0 + 12.5, y0, F0), (x1, y0 + t, ze))
            col_box2(A, (x0 + 2.0, y0, 11.0), (x0 + 6.0, y0 + t, ze))
            col_box2(A, (x0 + 8.5, y0, F0), (x0 + 12.5, y0 + t, 12.5))
            col_box2(A, (x0, y0, F0), (x0 + t, y0 + 7.0, ze))
            col_box2(A, (x0, y0 + 17.0, F0), (x0 + t, y1, ze))
            col_box2(A, (x0, y0 + 7.0, 15.0), (x0 + t, y0 + 17.0, ze))
        else:
            col_box2(A, (x0, y0, F0), (x0 + 9.5, y0 + t, ze))
            col_box2(A, (x0 + 12.5, y0, F0), (x1, y0 + t, ze))
            col_box2(A, (x0 + 9.5, y0, 11.5), (x0 + 12.5, y0 + t, ze))
            col_box2(A, (x1 - t, y0, F0), (x1, y1, ze))
        col_box2(A, (x0, y1 - t, F0), (x1, y1, ze))
        col_box2(A, (x0 - 1, y0 - 1, ze), (x1 + 1, y1 + 1, ze + 7))


# ------------------------------------------------------------------ loft + varanda + escada (ala esquerda)
def loft_balcony(rng):
    x0, y0, x1, y1 = L.FORGE_WING_L
    mb = MB("FORGE_Loft_Balcony", C, rng)
    zl = 12.5
    # loft interno (armazenamento) sobre a metade frontal da ala
    mb.box2((x0 + 1.6, y0 + 1.6, zl - 0.6), (x1, y0 + 12.0, zl), "Wood_Plank", 0.08)
    for yy in (y0 + 4, y0 + 8, y0 + 12):
        mb.box2((x0 + 1.6, yy - 0.5, zl - 1.4), (x1, yy + 0.5, zl - 0.6), "Wood_Dark", 0.08)
    for xx in (x0 + 7.0,):
        mb.box((1.0, 1.0, zl - F0), (xx, y0 + 12.0, (F0 + zl) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    fence(mb, "ForgeLoft", [(x0 + 1.8, y0 + 12.2, zl), (x1 - 0.2, y0 + 12.2, zl)], h=2.8, post_step=3.0)
    for i in range(5):
        crate(mb, (x0 + 3 + (i % 3) * 3.0, y0 + 9.5 - (i // 3) * 3.0, zl), 2.2, rng.uniform(-0.2, 0.2), rng)
    barrel(mb, (x1 - 2.5, y0 + 9.0, zl))
    barrel(mb, (x1 - 2.5, y0 + 6.0, zl))
    # varanda externa diante do oitao (y 0.5..6)
    by0 = y0 - 6.0
    mb.box2((x0 + 0.5, by0, zl - 0.6), (x1 - 0.5, y0, zl), "Wood_Plank", 0.08)
    for xx in (x0 + 1.2, x1 - 1.2):
        for yy in (by0 + 0.7,):
            mb.box((1.0, 1.0, zl - F0), (xx, yy, (F0 + zl) / 2), (0, 0, 0), "Wood_Dark", 0.1)
            mb.beam((xx, yy, zl - 3.5), (xx, y0 - 0.1, zl - 0.8), 0.6, 0.6, "Wood_Dark", 0.05)
    fence(mb, "ForgeLoft", [(x0 + 0.8, y0 - 0.2, zl), (x0 + 0.8, by0 + 0.4, zl), (x1 - 6.8, by0 + 0.4, zl)],
          h=2.8, post_step=3.0)
    fence(mb, "ForgeLoft", [(x1 - 0.8, by0 + 0.4, zl), (x1 - 0.8, y0 - 0.2, zl)], h=2.8, post_step=3.0)
    # quadro de lideres (leaderboard) na varanda, preso ao oitao
    mb.box2((x0 + 3.0, y0 - 0.6, zl + 1.0), (x0 + 10.0, y0 - 0.1, zl + 5.4), "Wood_Dark", 0.15)
    mb.box2((x0 + 3.5, y0 - 0.8, zl + 1.4), (x0 + 9.5, y0 - 0.5, zl + 5.0), "Cloth_Navy", 0.02)
    marker("LEADERBOARD_Balcony", (x0 + 6.5, y0 - 0.9, zl + 3.2), (0, 0, 0), 2, "SINGLE_ARROW")
    # escada externa: da praca (sul) ate a varanda, 9 degraus (z4 -> z12.5), piso 1.5
    sx = x1 - 3.8
    stairs(mb, "ForgeLoft", (sx, by0 - 9 * 1.5, F0), D(90), 5.0, 9, (zl - F0) / 9, 1.5, "Wood_Plank", "Wood_Dark")
    mb.finish()
    A = "ForgeLoft"
    col_box2(A, (x0 + 1.6, y0 + 1.6, zl - 1.4), (x1 - 1.6, y0 + 12.0, zl))
    col_box2(A, (x0 + 0.5, by0, zl - 1.0), (x1 - 0.5, y0, zl))
    # poste do loft fica fora da rota principal; porta do loft no oitao (s 2..6 -> x0+2..x0+6, z 11..16.2)
    marker("DOOR_Loft", (x0 + 4.0, y0, zl), (0, 0, 0), 1.5)


# ------------------------------------------------------------------ balcao de venda (frente da ala direita)
def stall(rng):
    x0, y0, x1, y1 = L.FORGE_WING_R
    mb = MB("FORGE_Counter_Stall", C, rng)
    sy0 = y0 - 6.0
    # meia-agua: da parede (z13) ate os pilares (z10)
    for xx in (x0 + 1.0, (x0 + x1) / 2, x1 - 1.0):
        mb.box((0.9, 0.9, 10.0 - F0), (xx, sy0 + 0.5, (F0 + 10.0) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    mb.beam((x0 + 0.4, sy0 + 0.5, 10.0), (x1 - 0.4, sy0 + 0.5, 10.0), 0.9, 1.0, "Wood_Dark", 0.08)
    ang = math.atan2(3.0, 6.0)
    for i in range(6):
        yy = sy0 - 0.8 + i * 1.3
        zz = 10.0 + (yy - sy0 + 0.8) * 3.0 / 7.4 + 0.5
        mb.box((x1 - x0 + 1.6, 1.5, 0.45), (((x0 + x1) / 2), yy, zz), (-ang, 0, 0), "Roof_Red" if i % 2 else "Cloth_Red",
               0.08)
    # balcao (topo z 7.3) com frente de tabuas e tampo
    mb.box2((x0 + 1.5, sy0 + 1.0, F0), (x1 - 4.5, sy0 + 2.4, F0 + 3.0), "Wood_Plank", 0.1)
    mb.box2((x0 + 1.2, sy0 + 0.8, F0 + 3.0), (x1 - 4.2, sy0 + 2.7, F0 + 3.4), "Wood_Light", 0.1)
    # passagem lateral para o atendente (x1-4.5..x1-1)
    # prateleiras na parede da ala (lingotes, cristais, pocoes)
    for zz in (F0 + 2.5, F0 + 4.6, F0 + 6.7):
        mb.box2((x0 + 1.0, y0 - 1.1, zz), (x1 - 5.0, y0 - 0.1, zz + 0.3), "Wood_Light", 0.05)
        for k in range(6):
            xx = x0 + 2.0 + k * 1.5
            if (k + int(zz)) % 3 == 0:
                mb.box((1.0, 0.6, 0.45), (xx, y0 - 0.6, zz + 0.52), (0, 0, 0), "Metal_Brass", 0.06)
            elif (k + int(zz)) % 3 == 1:
                crystal_cluster(mb, (xx, y0 - 0.6, zz + 0.3), 0.3, "Crystal_Blue" if k % 2 else "Crystal_Purple",
                                rng, 3)
            else:
                mb.cyl(0.32, 0.9, (xx, y0 - 0.6, zz + 0.75), (0, 0, 0), "Crystal_Purple", 8, r2=0.2, bevel=0.0)
    # itens no tampo
    mb.box((1.4, 0.8, 0.5), (x0 + 3.0, sy0 + 1.7, F0 + 3.65), (0, 0, 0.2), "Metal_Brass", 0.06)
    crystal_cluster(mb, (x0 + 6.0, sy0 + 1.7, F0 + 3.4), 0.35, "Crystal_Blue", rng, 4)
    hanging_lantern(mb, (x0 + 4.0, sy0 + 0.5, 9.5), name="L_Stall_A", chain=1.0)
    hanging_lantern(mb, (x1 - 4.0, sy0 + 0.5, 9.5), name="L_Stall_B", chain=1.0)
    # placa pendurada com lingote
    mb.box((3.6, 0.3, 1.8), ((x0 + x1) / 2, sy0 + 0.2, 8.2), (0, 0, 0), "Wood_Dark", 0.1)
    mb.box((1.6, 0.35, 0.7), ((x0 + x1) / 2, sy0 - 0.05, 8.2), (0, 0, 0), "Metal_Brass", 0.06)
    mb.finish()
    A = "ForgeStall"
    col_box2(A, (x0 + 1.2, sy0 + 0.8, F0), (x1 - 4.2, sy0 + 2.7, F0 + 3.4))
    col_box2(A, (x0 + 0.5, y0 - 1.2, F0), (x1 - 4.8, y0, F0 + 7.2))
    for xx in (x0 + 1.0, (x0 + x1) / 2, x1 - 1.0):
        col_box(A, (0.9, 0.9, 10.0 - F0), (xx, sy0 + 0.5, (F0 + 10.0) / 2))
    marker("NPC_Balcao", ((x0 + x1) / 2 - 2, sy0 + 4.2, F0), (0, 0, D(180)), 2, props={"role": "vendedor_forja"})
    marker("INTERACT_Balcao", ((x0 + x1) / 2 - 2, sy0 + 1.7, F0 + 3.4), (0, 0, 0), 1.5)
    marker("PLAYER_INTERACT_Balcao", ((x0 + x1) / 2 - 2, sy0 - 2.5, F0), (0, 0, 0), 1.5)


# ------------------------------------------------------------------ interior do salao e da ala direita (foles)
def interior(rng):
    x0, y0, x1, y1 = L.FORGE_HALL
    mb = MB("FORGE_Interior_Props", C, rng)
    # bancadas ao longo das paredes laterais (deixam o eixo porta->arco livre)
    for sx in (-1, 1):
        bx = sx * 15.2
        mb.box2((bx - 2.0, 16.0, FL), (bx + 2.0, 19.6, FL + 3.0), "Wood_Plank", 0.1)
        mb.box2((bx - 2.3, 15.8, FL + 3.0), (bx + 2.3, 19.8, FL + 3.4), "Wood_Light", 0.1)
        # suporte de ferramentas na parede de fundo
        mb.box2((bx - 3.0, y1 - 2.5, FL + 5.0), (bx + 3.0, y1 - 2.2, FL + 8.5), "Wood_Dark", 0.05)
        for k in range(5):
            xx = bx - 2.4 + k * 1.2
            mb.beam((xx, y1 - 2.6, FL + 8.0), (xx, y1 - 2.6, FL + 5.4), 0.25, 0.25, "Wood_Light", 0.0)
            mb.box((0.9, 0.5, 0.5), (xx, y1 - 2.6, FL + 5.2), (0, 0, 0), "Metal_Iron", 0.05)
    # tanque de tempera (agua) e rebolo
    mb.box2((-11.5, 7.0, FL), (-6.5, 9.4, FL + 2.4), "Wood_Plank", 0.1)
    mb.box2((-11.1, 7.4, FL + 2.0), (-6.9, 9.0, FL + 2.3), "Water", 0.0)
    for x in (-11.5, -6.5):
        mb.box((0.3, 2.6, 0.4), (x, 8.2, FL + 1.8), (0, 0, 0), "Metal_Dark", 0.03)
    mb.cyl(1.6, 0.6, (8.5, 8.2, FL + 3.0), (0, D(90), 0), "Stone_Light", 14, bevel=0.1)
    mb.box2((7.2, 7.4, FL), (9.8, 9.0, FL + 1.6), "Wood_Dark", 0.1)
    # armas e picaretas em cavaletes
    for k in range(4):
        xx = 9.5 + k * 1.5
        mb.beam((xx, 20.4, FL), (xx, 20.4, FL + 4.2), 0.25, 0.3, "Wood_Light", 0.0)
        mb.box((2.2, 0.35, 0.6), (xx, 20.2, FL + 4.2), (0, 0, D(90)), "Metal_Iron", 0.05)
    # carvao em sacos/barris perto do arco
    for p in ((-6.5, 18.8), (-8.8, 18.8), (6.5, 18.8)):
        barrel(mb, (p[0], p[1], FL), 1.0, 2.4)
    for i in range(3):
        crate(mb, (-17.0 + i * 0.4, 8.0 + i * 2.6, FL), 2.0, rng.uniform(-0.2, 0.2), rng)
    # lustres de ferro com lanternas
    for yy in (9.0, 16.0):
        hanging_lantern(mb, (-7.0, yy, 23.6), name="L_Hall_%d_A" % int(yy), chain=6.0)
        hanging_lantern(mb, (7.0, yy, 23.6), name="L_Hall_%d_B" % int(yy), chain=6.0)
    light("L_Hall_Fill", "POINT", (0, 13.0, 16.0), 1400, (1.0, 0.7, 0.45), 4.0)
    mb.finish()
    A = "ForgeInt"
    for sx in (-1, 1):
        col_box2(A, (sx * 15.2 - 2.3, 15.8, FL), (sx * 15.2 + 2.3, 19.8, FL + 3.4))
    col_box2(A, (-11.5, 7.0, FL), (-6.5, 9.4, FL + 2.4))
    col_box2(A, (7.2, 7.0, FL), (9.8, 9.4, FL + 4.6))

    # ---- ala direita: eixo da roda, engrenagens, foles, duto para a torre
    wx0, wy0, wx1, wy1 = L.FORGE_WING_R
    m2 = MB("FORGE_Bellows_Machinery", C, rng)
    az = 15.5
    ay = L.WHEEL_C[1]
    # eixo principal (vem da casa da roda) ate a engrenagem
    m2.rod((wx1 + 0.5, ay, az), (wx0 + 6.0, ay, az), 0.55, "Wood_Dark", 10)
    for xx in (wx1 - 3.0, wx0 + 8.5):
        m2.box((1.4, 1.2, az - F0), (xx, ay, (F0 + az) / 2 - 0.4), (0, 0, 0), "Wood_Dark", 0.1)
        m2.box((1.8, 1.8, 1.0), (xx, ay, az - 0.5), (0, 0, 0), "Metal_Iron", 0.08)
    # came/manivela que aciona os foles
    m2.cyl(2.2, 0.9, (wx0 + 6.0, ay, az), (0, D(90), 0), "Metal_Iron", 16, bevel=0.1)
    for i in range(16):
        a = i / 16 * math.tau
        m2.box((0.9, 0.6, 0.6), (wx0 + 6.0, ay + math.cos(a) * 2.35, az + math.sin(a) * 2.35), (a, 0, 0), "Metal_Dark",
               0.05)
    m2.beam((wx0 + 5.4, ay + 1.6, az - 1.2), (wx0 + 5.4, ay + 6.0, F0 + 5.8), 0.5, 0.5, "Wood_Dark", 0.05)
    # foles: tabua de baixo, tabua de cima inclinada, couro plissado, bocal
    bx, by = wx0 + 5.0, ay + 7.0
    m2.box((5.0, 3.2, 0.5), (bx, by, F0 + 2.0), (0, 0, 0), "Wood_Plank", 0.08)
    m2.box((5.0, 3.2, 0.5), (bx, by, F0 + 5.2), (0, D(-8), 0), "Wood_Plank", 0.08)
    for k in range(4):
        z = F0 + 2.6 + k * 0.7
        m2.box((4.4 - k * 0.2, 3.4, 0.55), (bx + 0.2 * k, by, z), (0, D(-2 * k), 0), "Leather", 0.15)
    m2.box((1.5, 1.0, 1.0), (bx - 3.0, by, F0 + 3.2), (0, 0, 0), "Metal_Brass", 0.08)
    for zz in (F0 + 0.7,):
        m2.box((5.4, 3.4, 1.4), (bx, by, zz), (0, 0, 0), "Stone_Dark", 0.15)
    # duto de ar: do bocal, atravessa a parede da ala (x=20) e entra na torre
    cx, cy = L.CHIMNEY
    pipe(m2, [(bx - 3.6, by, F0 + 3.2), (wx0 + 0.5, by, F0 + 3.2), (wx0 - 4.0, by, F0 + 6.0),
              (cx + L.CHIMNEY_R - 0.5, cy - 1.0, F0 + 8.0)], r=0.9)
    # tubo grande externo: do telhado da ala subindo ate a torre (exaustao)
    pipe(m2, [(wx0 + 7.0, wy1 - 5.0, 21.0), (wx0 + 7.0, wy1 - 5.0, 27.0), (wx0 + 3.0, wy1 - 4.0, 33.0),
              (cx + L.CHIMNEY_R - 1.0, cy + 1.5, 36.0)], r=1.4)
    light("L_WingR", "POINT", (wx0 + 7, ay + 2, 13.0), 250, (1.0, 0.65, 0.35), 0.5)
    m2.finish()
    col_box("ForgeInt", (2.0, 12.0, 3.0), ((wx0 + wx1) / 2 + 1, ay, az), (0, 0, D(90)))
    col_box2("ForgeInt", (bx - 3.6, by - 1.8, F0), (bx + 2.6, by + 1.8, F0 + 5.6))

    # ---- ala esquerda: fim do trilho, tremonha e calha de minerio para a torre
    lx0, ly0, lx1, ly1 = L.FORGE_WING_L
    m3 = MB("FORGE_OreIntake", C, rng)
    hx, hy = lx0 + 10.5, ly0 + 12.0   # tremonha no fim do trilho (portao oeste y=18)
    # tremonha (funil) sobre base de madeira
    for sx in (-1, 1):
        for sy in (-1, 1):
            m3.box((0.9, 0.9, 7.0), (hx + sx * 2.4, hy + sy * 1.8, F0 + 3.5), (0, 0, 0), "Wood_Dark", 0.1)
    m3.cyl(3.6, 3.0, (hx, hy, F0 + 8.5), (0, 0, D(45)), "Wood_Plank", 4, r2=1.6, bevel=0.1)
    crystal_cluster(m3, (hx, hy, F0 + 9.6), 0.6, "Crystal_Blue", rng, 6)
    # calha inclinada coberta: da tremonha atravessando a parede x=-20 ate a torre
    cx, cy = L.CHIMNEY
    a = Vector((hx + 1.5, hy, F0 + 7.0))
    b = Vector((cx - L.CHIMNEY_R + 0.8, cy - 1.0, F0 + 11.5))
    m3.beam(a, b, 2.2, 0.4, "Wood_Plank", 0.05)
    for s in (-1, 1):
        m3.beam(a + Vector((0, s * 1.1, 0.6)), b + Vector((0, s * 1.1, 0.6)), 0.3, 1.2, "Wood_Dark", 0.03)
    m3.beam(a + Vector((0, 0, 1.4)), b + Vector((0, 0, 1.4)), 2.6, 0.3, "Wood_Dark", 0.03)
    mid = (a + b) / 2
    m3.box((1.0, 1.0, mid.z - F0), (mid.x, mid.y, (F0 + mid.z) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    # tubo de exaustao da ala esquerda ate a torre
    pipe(m3, [(lx1 - 6.0, ly1 - 4.0, 21.0), (lx1 - 6.0, ly1 - 4.0, 28.0), (lx1 - 2.0, ly1 - 3.0, 34.0),
              (cx - L.CHIMNEY_R + 1.0, cy + 1.5, 38.0)], r=1.4)
    # baias de minerio (parede oeste, atras do portao)
    for k in range(2):
        yy = ly0 + 20.0 + k * 4.6
        m3.box2((lx0 + 1.8, yy - 2.0, F0), (lx0 + 6.5, yy + 2.0, F0 + 2.2), "Wood_Plank", 0.08)
        crystal_cluster(m3, (lx0 + 4.2, yy, F0 + 2.0), 0.55, ("Crystal_Blue", "Crystal_Purple")[k], rng, 5)
    hanging_lantern(m3, (lx0 + 7.0, ly0 + 18.0, 16.6), name="L_WingL_A", chain=3.0)
    m3.finish()
    col_box2("ForgeInt", (hx - 3.0, hy - 2.4, F0), (hx + 3.0, hy + 2.4, F0 + 10.0))
    col_box2("ForgeInt", (lx0 + 1.8, ly0 + 18.0, F0), (lx0 + 6.5, ly0 + 26.6, F0 + 2.2))


# ------------------------------------------------------------------ bigorna + Ignis + marcadores
def anvil_and_ignis(rng):
    ax, ay = L.ANVIL
    mb = MB("FORGE_Anvil", C, rng)
    # bigorna na altura da cintura do avatar (topo ~3.4): o Ignis aparece da cintura para cima atras dela
    mb.cyl(1.8, 1.5, (ax, ay, FL + 0.75), (0, 0, 0), "Wood_Dark", 10, r2=1.6, bevel=0.12)
    for z in (FL + 0.3, FL + 1.3):
        mb.cyl(1.86, 0.25, (ax, ay, z), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    mb.box((2.8, 1.9, 0.6), (ax, ay, FL + 1.8), (0, 0, 0), "Metal_Dark", 0.12)
    mb.box((1.6, 1.1, 0.8), (ax, ay, FL + 2.5), (0, 0, 0), "Metal_Dark", 0.1)
    mb.box((4.4, 1.8, 0.75), (ax, ay, FL + 3.2), (0, 0, 0), "Metal_Iron", 0.12)
    mb.cyl(0.9, 2.2, (ax - 3.2, ay, FL + 3.3), (0, D(-90), 0), "Metal_Iron", 8, r2=0.08, bevel=0.0)
    mb.box((0.9, 1.5, 0.6), (ax + 2.5, ay, FL + 3.3), (0, 0, 0), "Metal_Iron", 0.08)
    mb.box((1.6, 0.6, 0.25), (ax + 0.5, ay, FL + 3.7), (0, 0, 0.3), "Metal_Heated", 0.06)
    mb.cyl(0.8, 1.4, (ax + 3.4, ay + 1.5, FL + 0.7), (0, 0, 0), "Metal_Iron", 10, r2=0.9, bevel=0.05)
    mb.finish()
    col_box("ForgeNPC", (5.0, 2.4, 3.8), (ax, ay, FL + 1.9))

    # Ignis (NPC ferreiro, escala 1.35x avatar): corpo em blocos, avental, cabelo espetado vermelho, martelo
    ix, iy = L.IGNIS
    s = 1.35
    ig = MB("NPC_Ignis_Model", C, rng)
    F = Frame(ix, iy, FL, D(180))  # olha para -Y (jogadores)
    for sx in (-0.5, 0.5):
        ig.box((0.95 * s, 0.95 * s, 2.0 * s), F.p(sx * s, 0, 1.0 * s), F.r(), "Cloth_Navy", 0.1)
        ig.box((1.05 * s, 1.2 * s, 0.5 * s), F.p(sx * s, -0.1 * s, 0.25 * s), F.r(), "Leather", 0.08)
    ig.box((2.2 * s, 1.15 * s, 2.1 * s), F.p(0, 0, 3.05 * s), F.r(), "Wood_Light", 0.12)
    ig.box((2.0 * s, 0.2 * s, 2.9 * s), F.p(0, 0.62 * s, 2.7 * s), F.r(), "Leather", 0.05)
    for sx in (-1, 1):
        ig.box((1.0 * s, 1.0 * s, 2.1 * s), F.p(sx * 1.6 * s, 0, 3.0 * s), F.r(), "Skin", 0.12)
        ig.box((1.1 * s, 1.1 * s, 0.6 * s), F.p(sx * 1.6 * s, 0, 3.9 * s), F.r(), "Leather", 0.08)
    ig.box((1.25 * s, 1.2 * s, 1.25 * s), F.p(0, 0, 4.75 * s), F.r(), "Skin", 0.3)
    for i in range(9):
        a = i / 9 * math.pi - math.pi / 2
        ig.cyl(0.35 * s, 1.3 * s, F.p(math.sin(a) * 0.5 * s, -math.cos(a) * 0.2 * s + 0.25 * s, 5.55 * s),
               F.r(math.cos(a) * 0.9 - 0.4, math.sin(a) * 0.9, 0), "Hair_Red", 5, r2=0.02, bevel=0.0)
    ig.box((1.35 * s, 1.3 * s, 0.5 * s), F.p(0, 0.05 * s, 5.35 * s), F.r(), "Hair_Red", 0.15)
    # martelo erguido na mao direita
    hp = F.p(1.6 * s, 0.9 * s, 3.2 * s)
    ig.beam(hp, hp + Vector((0.4, -0.9, 2.4)) * s, 0.3 * s, 0.3 * s, "Wood_Light", 0.02)
    ig.box((1.6 * s, 0.8 * s, 0.8 * s), hp + Vector((0.45, -1.0, 2.6)) * s, (0, 0, 0), "Metal_Dark", 0.08)
    ig.finish()
    col_box("ForgeNPC", (3.4, 2.0, 7.0), (ix, iy, FL + 3.5))
    marker("NPC_Ignis", (ix, iy, FL), (0, 0, D(180)), 3, "ARROWS", props={"npc": "Ignis", "scale": 1.35})
    marker("INTERACT_Ignis", (ax, ay, FL + 3.8), (0, 0, 0), 2, "SPHERE", props={"prompt_range": 18})
    px, py = L.PLAYER_IGNIS
    marker("PLAYER_INTERACT_Ignis", (px, py, F0 + 0.3), (0, 0, 0), 3, "CIRCLE",
           props={"note": "area livre r=8 na praca para varios jogadores"})
    light("L_Hearth_Fire", "POINT", (0, 0.5, FL + 4.5), 2200, (1.0, 0.45, 0.12), 2.0)
    light("L_Hearth_Spill", "SPOT", (0, -3.0, 13.0), 1800, (1.0, 0.5, 0.2), 1.5, rot=(D(35), 0, D(180)))


def build():
    rng = random.Random(404)
    foundation(rng)
    hall(rng)
    hearth(rng)
    chimney(rng)
    furnace(rng)
    wings(rng)
    loft_balcony(rng)
    stall(rng)
    interior(rng)
    anvil_and_ignis(rng)
