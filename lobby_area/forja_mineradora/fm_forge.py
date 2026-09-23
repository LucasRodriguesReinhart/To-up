# fm_forge - FORJA DO IGNIS (asset heroi). Planta:
#   salao x-20..20 y4..22 (piso 5) | lareira aberta na fachada (x-8..8, y-1.5..4) | Ignis y-5 | bigorna y-10
#   torre-chamine r10 em (0,30) com fornalha e foles | ala esq. = recebimento de minerio (trilho) + loft/varanda
#   ala dir. = casa dos foles (eixo da roda d'agua) + balcao de venda na frente
# Passe de acabamento (fabrica artesanal): alvenaria quente, boca da fornalha em aneis recuados com carvao, brasas e
# metal aquecido, moldura de ferro rebitada, oitao em balanco com brasao, telhados irregulares com lanternim,
# torre com cinta de ferro, respiros e coroa de janelas incandescentes. Anexos industriais em fm_forge_annex.
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, col_ramp, marker, light, arc, bezier
from fm_parts import (Frame, stairs, masonry_wall, timber_wall, arch, window_glow, banner, emblem_hammers,
                      lantern, hanging_lantern, crate, barrel, crystal_cluster, fence, pave_ring, pave_poly, P3, frustum)
from fm_forge_kit import (xz_prism, octagon, forge_roof, timber_wall_irr, board_gable, iron_bracket, chain_links,
                          hanging_chain, rivet, flame, tube_pt, Z)
import fm_layout as L

C = "03_FORGE"
F0 = L.FLOOR
FL = L.FL
SF, SFD = "Stone_Forge", "Stone_Forge_Dark"


def ring_masonry(mb, cx, cy, r_in, r_out, z0, z1, rng, course=2.0, gaps=(), m=SF, m2=SFD,
                 mix=0.25, taper=0.0, blk=2.8):
    """anel de alvenaria (torre). gaps = [(ang_centro_graus, meia_largura_studs, zlo, zhi)]"""
    z = z0
    row = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        f = (z - z0) / max(1e-3, (z1 - z0))
        ri = r_in - taper * f
        ro = r_out - taper * f
        rm = (ri + ro) / 2
        n = max(8, int(2 * math.pi * rm / blk))
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


def crest(mb, c, rng):
    """brasao da forja no oitao: tabua octogonal, moldura de ferro rebitada, martelos cruzados sobre bigorna"""
    cx, fy, cz = c

    def W(pts):
        return [(cx + u, cz + v) for u, v in pts]
    xz_prism(mb, W(octagon(11.4, 10.8, 2.8)), fy - 0.45, fy + 0.02, "Wood_Dark")
    outer, inner = octagon(9.8, 9.2, 2.4), octagon(8.0, 7.4, 1.95)
    for i in range(8):
        j = (i + 1) % 8
        xz_prism(mb, W([outer[i], outer[j], inner[j], inner[i]]), fy - 1.0, fy - 0.4, "Metal_Iron")
    xz_prism(mb, W(inner), fy - 0.8, fy - 0.4, "Metal_Dark")
    for i in range(8):
        j = (i + 1) % 8
        for f in (0.0, 0.5):
            u = outer[i][0] + (outer[j][0] - outer[i][0]) * f
            v = outer[i][1] + (outer[j][1] - outer[i][1]) * f
            ui = inner[i][0] + (inner[j][0] - inner[i][0]) * f
            vi = inner[i][1] + (inner[j][1] - inner[i][1]) * f
            rivet(mb, (cx + (u + ui) / 2, fy - 1.0, cz + (v + vi) / 2), (0, -1, 0), 0.24, "Metal_Brass")
    # cantoneiras de ferro na tabua de fundo
    for su in (-1, 1):
        for sv in (-1, 1):
            p = Vector((cx + su * 4.9, fy - 0.5, cz + sv * 4.6))
            mb.box((1.6, 0.14, 0.5), p + Vector((-su * 0.3, 0, 0)), (0, 0, su * sv * D(45)), "Metal_Dark", 0.02)
    emblem_hammers(mb, Vector((cx, fy - 0.85, cz + 0.75)), 0.0, s=1.2, m="Emblem_Cream", off=0.15)
    anvil = [(-2.3, 0.45), (-1.3, 0.05), (-0.75, 0.0), (-0.65, -0.55), (-1.25, -1.0), (1.25, -1.0), (0.65, -0.55),
             (0.75, 0.0), (1.9, 0.05), (1.9, 0.55), (-1.0, 0.6)]
    xz_prism(mb, [(cx + u, cz - 2.55 + v) for u, v in anvil], fy - 1.05, fy - 0.8, "Metal_Brass")
    # brasa incandescente no cruzamento dos martelos
    mb.ico(0.42, (cx, fy - 1.1, cz + 0.75), "Forge_Glow_Soft", 1, (1, 0.6, 1))


def roof_monitor(mb, rng, cx, y0, y1, w, zb, zt):
    """lanternim de ventilacao sobre a cumeeira: base, montantes, venezianas com brilho da forja, telhadinho"""
    hw = w / 2
    mb.box2((cx - hw - 0.25, y0 - 0.25, zb - 1.0), (cx + hw + 0.25, y1 + 0.25, zb + 0.5), "Wood_Dark", 0.1)
    mb.box2((cx - hw + 0.5, y0 + 0.3, zb + 0.4), (cx + hw - 0.5, y1 - 0.3, zt - 0.2), "Forge_Glow_Soft", 0.0)
    ny = 4
    for j in range(ny + 1):
        yy = y0 + (y1 - y0) * j / ny
        for s in (-1, 1):
            mb.box((0.5, 0.5, zt - zb), (cx + s * (hw - 0.15), yy, (zb + zt) / 2), (0, 0, rng.uniform(-0.03, 0.03)),
                   "Wood_Dark", 0.05)
    nl = 3
    for s in (-1, 1):
        for i in range(nl):
            z = zb + 0.9 + i * (zt - zb - 1.2) / (nl - 0.5)
            for j in range(ny):
                ya_ = y0 + (y1 - y0) * j / ny + 0.3
                yb_ = y0 + (y1 - y0) * (j + 1) / ny - 0.3
                mb.box((0.9, yb_ - ya_, 0.13), (cx + s * (hw - 0.2), (ya_ + yb_) / 2, z), (0, s * D(38), 0),
                       "Wood_Dark", 0.0)
    for yy in (y0, y1):
        mb.box2((cx - hw, yy - 0.25, zb), (cx + hw, yy + 0.25, zt), "Wood_Plank", 0.06)
    mb.box2((cx - hw - 0.2, y0 - 0.2, zt - 0.3), (cx + hw + 0.2, y1 + 0.2, zt), "Metal_Dark", 0.04)
    forge_roof(mb, cx, (y0 + y1) / 2, w + 0.2, y1 - y0, zt, 1.7, rng, thick=0.55, over=0.8, sag=0.08, row_h=1.1,
               seg=3.5, patches=0)


# ------------------------------------------------------------------ fundacao, tablado, piso
def foundation(rng):
    mb = MB("FORGE_Foundation_Dais", C, rng)
    x0, y0, x1, y1 = L.FORGE_HALL
    # plinto do salao e das alas (base de pedra aparente)
    mb.box2((x0 - 0.8, y0 - 0.2, F0 - 1.0), (x1 + 0.8, y1, FL - 0.3), SFD, 0.2)
    mb.box2((x0 - 0.8, y0 - 0.2, FL - 0.3), (x1 + 0.8, y0 + 2.2, FL), SFD, 0.1)
    for w in (L.FORGE_WING_L, L.FORGE_WING_R):
        mb.box2((w[0] - 0.8, w[1] - 0.6, F0 - 1.0), (w[2] + 0.8, w[3] + 0.6, F0 + 0.3), SFD, 0.2)
    # piso interno do salao (lajes)
    pave_poly(mb, [(x0 + 2.2, y0 + 2.2), (x1 - 2.2, y0 + 2.2), (x1 - 2.2, y1 - 2.2), (x0 + 2.2, y1 - 2.2)],
              FL - 0.3, rng, tile=3.3, h=0.3, grout=False, m=SF)
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
    masonry_wall(mb, (x0, fy), (x1, fy), FL, zs, t, rng, openings=ops, m=SF, m2=SFD, mix=0.28)
    for dx, w in doors:
        arch(mb, (dx, fy, 0), 0.0, w, 12.0, 3.0, t + 0.3, "Stone_Light", "Metal_Brass", n=9, band=1.2)
        # dobradicas de ferro nas ombreiras
        for sx in (-1, 1):
            for zz in (FL + 2.0, FL + 6.0):
                mb.box((0.9, 0.35, 0.45), (dx + sx * (w / 2 + 0.35), y0 - 0.12, zz), (0, 0, 0), "Metal_Dark", 0.03)
    # paredes laterais (portas internas para as alas: y 9..15)
    for sx in (x0 + t / 2, x1 - t / 2):
        masonry_wall(mb, (sx, y0), (sx, y1), FL, zs, t, rng, openings=[(5.0, 11.0, FL, 14.0, 2.5)], m=SF, m2=SFD,
                     mix=0.28)
        arch(mb, (sx, y0 + 8.0, 0), D(90), 6.0, 11.5, 2.5, t + 0.3, n=7, band=1.1)
    # parede de fundo (encontra a torre): trechos laterais + arco grande para a fornalha
    by = y1 - t / 2
    masonry_wall(mb, (x0, by), (-4.0, by), FL, zs, t, rng, m=SF, m2=SFD, mix=0.28)
    masonry_wall(mb, (4.0, by), (x1, by), FL, zs, t, rng, m=SF, m2=SFD, mix=0.28)
    # andar enxaimel (16..24) em volta, pecas levemente tortas
    timber_wall_irr(mb, (x0, fy), (x1, fy), zs, ze, t * 0.8, rng,
                    openings=[(3.5, 7.5, 18.0, 22.0), (32.5, 36.5, 18.0, 22.0)], post=3.3)
    for s0, s1 in ((3.5, 7.5), (32.5, 36.5)):
        window_glow(mb, (x0, fy), (x1, fy), s0, s1, 18.0, 22.0, t * 0.8)
    for sx in (x0 + t / 2, x1 - t / 2):
        timber_wall_irr(mb, (sx, y0), (sx, y1), zs, ze, t * 0.8, rng, post=3.6)
    timber_wall_irr(mb, (x0, by), (x1, by), zs, ze, t * 0.8, rng, post=3.4)
    # oitao frontal EM BALANCO (tabuas verticais) sobre viga e maos-francesas de ferro; oitao de fundo em tabuas
    jf = y0 - 1.1
    board_gable(mb, 0.0, jf, 40.0, ze, 13.0, 1.3, rng, facing=-1)
    board_gable(mb, 0.0, y1 - 0.2, 40.0, ze, 13.0, 1.3, rng, bw=1.9, facing=1)
    mb.box2((-20.6, jf - 0.2, ze - 0.8), (20.6, y0 + 0.3, ze + 0.1), "Wood_Dark", 0.1)
    for xx in (-18.4, -11.4, -7.8, 7.8, 11.4, 18.4):
        iron_bracket(mb, (xx, y0 + 0.05, ze - 0.8), (0, -1), 1.9, "Metal_Dark", 0.6, 0.34, scroll=abs(xx) > 10)
    for s in (-1, 1):
        hanging_lantern(mb, (s * 18.4, y0 - 1.55, ze - 1.15), name="L_Jetty_%d" % (s + 1), chain=0.4)
    for gy, off in ((jf - 0.25, 0.0), (y1 - 0.2 + 0.3, 0.0)):
        mb.beam((-20.8, gy, ze + 0.35), (20.8, gy + 0.05, ze + 0.45), 0.7, 0.8, "Wood_Dark", 0.08)
    # frechal inclinado nos beirais do oitao frontal (acompanha o telhado)
    for s in (-1, 1):
        mb.beam((s * 20.6, jf - 0.25, ze + 0.2), (0, jf - 0.25, ze + 13.0 - 0.1), 0.55, 0.7, "Wood_Dark", 0.06)
    crest(mb, Vector((0.0, jf, ze + 6.6)), rng)
    # contrafortes de pedra nos cantos
    for cx_ in (x0 - 0.4, x1 + 0.4):
        mb.box((2.6, 2.6, zs - FL + 1), (cx_, y0 + 0.4, (FL + zs) / 2 - 0.5), (0, 0, 0), SFD, 0.3)
        mb.box((3.0, 3.0, 0.8), (cx_, y0 + 0.4, zs + 0.2), (0, 0, 0), "Stone_Light", 0.2)
        for zz in (FL + 3.0, FL + 8.0):
            mb.box((2.9, 2.9, 0.5), (cx_, y0 + 0.4, zz), (0, 0, 0), "Metal_Dark", 0.04)
    mb.finish()

    # telhado irregular (cumeeira com barriga) + tesouras levemente tortas + lanternim de ventilacao
    rf = MB("FORGE_Hall_Roof", C, rng)
    forge_roof(rf, 0.0, (y0 + y1) / 2 - 0.5, 40.0, 17.0, ze, 13.0, rng, thick=0.9, over=1.8, sag=0.55, row_h=1.9,
               seg=7.0, patches=2)
    for yy in (8.0, 13.0, 18.0):
        yj = yy + rng.uniform(-0.25, 0.25)
        rf.beam((-19, yj, ze - 0.4), (19, yj + rng.uniform(-0.2, 0.2), ze - 0.4 + rng.uniform(-0.15, 0.15)), 0.9, 1.1,
                "Wood_Dark", 0.08)
        rf.beam((0, yj, ze - 0.4), (rng.uniform(-0.15, 0.15), yj, ze + 12.0), 0.8, 0.8, "Wood_Dark", 0.08)
        for s in (-1, 1):
            rf.beam((s * 19, yj, ze), (0, yj, ze + 12.4 + rng.uniform(-0.2, 0.1)), 0.8, 0.9, "Wood_Dark", 0.08)
            rf.beam((s * 9, yj, ze - 0.2), (s * rng.uniform(0.0, 0.3), yj, ze + 6), 0.6, 0.6, "Wood_Dark", 0.06)
    roof_monitor(rf, rng, 0.0, 7.0, 16.5, 5.2, ze + 13.0 - 0.65 * 2.6 - 0.2, ze + 15.9)
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
    wy = fy + 1.1
    # corpo de pedra: frente com arco grande, laterais
    masonry_wall(mb, (-8, wy), (8, wy), FL, 18.0, 2.2, rng, openings=[(2.5, 13.5, FL, 13.5, 3.5)],
                 m=SF, m2=SFD, course=1.5, mix=0.35)
    arch(mb, (0, wy, 0), 0.0, 11.0, 10.0, 3.5, 2.6, "Stone_Light", "Metal_Brass", n=11, band=1.4)
    for sx in (-7.0, 7.0):
        masonry_wall(mb, (sx, fy), (sx, y0), FL, 18.0, 2.0, rng, course=2.0, m=SF, m2=SFD)
    # boca PROFUNDA: dois aneis de aduelas recuados, cada vez menores, ate a garganta incandescente
    for (yy, hw, zsp, rise, band) in ((1.35, 4.85, 9.9, 2.9, 1.0), (2.75, 4.15, 9.5, 2.4, 0.9)):
        masonry_wall(mb, (-6.2, yy), (6.2, yy), FL, 14.2, 1.3, rng,
                     openings=[(6.2 - hw, 6.2 + hw, FL, zsp + rise, rise)], m=SFD, m2=SF, course=1.8, mix=0.3)
        arch(mb, (0, yy - 0.72, 0), 0.0, hw * 2, zsp, rise, 0.3, "Stone_Light", "Stone_Light", n=9, band=band,
             keystone=False)
    mb.box2((-5.6, 3.5, FL), (5.6, 4.0, 14.2), "Stone_Coal", 0.0)
    mb.box2((-3.9, 3.3, FL + 1.8), (3.9, 3.52, FL + 3.4), "Ember_Glow", 0.0)
    mb.box2((-1.3, 3.3, FL + 3.4), (1.3, 3.52, 11.0), "Fire_Glow_Outer", 0.0)
    # leito elevado: brasa viva por baixo, carvao amontoado (mais alto no meio) e brasas por cima
    mb.box2((-5.4, fy + 0.4, FL), (5.4, y0, FL + 1.8), SFD, 0.2)
    mb.box2((-5.0, fy + 0.8, FL + 1.5), (5.0, y0 - 0.3, FL + 1.9), "Fire_Glow_Mid", 0.0)
    for i in range(40):
        yy = rng.uniform(fy + 0.8, y0 - 0.6) if i >= 12 else rng.uniform(fy + 0.7, fy + 1.6)
        xm = 5.0 if yy < 0.7 else (4.5 if yy < 2.0 else 3.8)
        x = rng.uniform(-xm, xm) if i >= 12 else -4.6 + i * 0.84 + rng.uniform(-0.2, 0.2)
        hh = 0.5 * (1 - (x / 5.2) ** 2) + rng.uniform(0.0, 0.3)
        s = rng.uniform(1.1, 1.65)
        mb.rock((x, yy, FL + 1.75 + hh), (s, s * rng.uniform(0.8, 1.1), s * 0.6), "Stone_Coal", 0,
                (0, 0, rng.uniform(0, 6)))
    for i in range(18):
        x = rng.uniform(-3.4, 3.4)
        yy = rng.uniform(fy + 1.1, 2.6)
        hh = 0.6 * (1 - (x / 5.2) ** 2) + 0.4
        s = rng.uniform(0.55, 0.95)
        mb.rock((x, yy, FL + 1.85 + hh), (s, s, s * 0.6), "Ember_Glow", 0, (0, 0, rng.uniform(0, 6)))
    # barras de ferro aquecendo nas brasas (laranja) com as tenazes para fora
    for (x, sk) in ((-2.7, 0.5), (0.5, -0.3), (2.9, 0.35)):
        pin = Vector((x + sk * 2.0, 2.3, FL + 2.3))
        pout = Vector((x, -0.9, FL + 2.75))
        mb.beam(pin, pout, 0.55, 0.38, "Ember_Glow", 0.06)
        tip = pout + Vector((-sk * 0.7, -1.7, 0.6))
        for s in (-1, 1):
            mb.beam(pout + Vector((s * 0.14, 0.25, 0.0)), tip + Vector((s * 0.24, 0.0, 0.0)), 0.16, 0.16, "Metal_Dark",
                    0.0)
    # chamas em camadas: vermelha alta atras, laranja no meio, amarela baixa na frente
    rows = ((2.95, (3.8, 4.6), "Fire_Glow_Outer", 1.3, (-2.6, -0.9, 0.9, 2.6)),
            (1.9, (3.2, 4.3), "Fire_Glow_Mid", 1.15, (-3.5, -1.8, 0.0, 1.8, 3.5)),
            (0.75, (2.1, 3.1), "Fire_Glow_Core", 0.9, (-3.0, -1.1, 1.0, 2.9)))
    for (yy, (h0, h1), m, rr, xs) in rows:
        for x in xs:
            x += rng.uniform(-0.3, 0.3)
            h = rng.uniform(h0, h1) * (1.05 - abs(x) / 12)
            flame(mb, (x, yy + rng.uniform(-0.2, 0.2), FL + 2.0), rr * rng.uniform(0.85, 1.1), h, m, rng)
    # moldura de ferro rebitada contornando o arco + ombreiras de ferro
    ext = [Vector((math.cos(math.pi * i / 16) * 7.3, fy - 0.17, 10.0 + math.sin(math.pi * i / 16) * 5.3))
           for i in range(17)]
    mb.sweep(ext, [(-0.42, -0.17), (0.42, -0.17), (0.42, 0.17), (-0.42, 0.17)], "Metal_Dark", True, up=(0, 1, 0))
    for i in range(13):
        a = math.pi * (i + 0.5) / 13
        rivet(mb, (math.cos(a) * 7.3, fy - 0.34, 10.0 + math.sin(a) * 5.3), (0, -1, 0), 0.2, "Metal_Brass")
    for s in (-1, 1):
        mb.box((0.84, 0.34, 10.0 - FL), (s * 7.3, fy - 0.17, (FL + 10.0) / 2), (0, 0, 0), "Metal_Dark", 0.04)
        for zz in (FL + 1.2, FL + 3.4, FL + 5.6, FL + 7.8):
            rivet(mb, (s * 7.3, fy - 0.34, zz), (0, -1, 0), 0.2, "Metal_Brass")
    # verga de ferro sobre o arco, cornija de pedra sobre maos-francesas, bloco superior e peito da chamine
    mb.box2((-7.7, fy - 0.42, 16.0), (7.7, fy, 17.3), "Metal_Iron", 0.06)
    for i in range(7):
        rivet(mb, (-6.6 + i * 2.2, fy - 0.42, 16.65), (0, -1, 0), 0.22, "Metal_Brass")
    mb.box2((-9.0, fy - 1.35, 18.0), (9.0, y0 + 0.4, 19.2), "Stone_Light", 0.3)
    for x in (-7.5, -3.6, 3.6, 7.5):
        iron_bracket(mb, (x, fy, 18.0), (0, -1), 1.25, "Metal_Dark", 0.5, 0.28, scroll=False)
    # peito da chamine em fiadas de pedra, recuando em degraus ate o oitao em balanco
    masonry_wall(mb, (-8.0, fy + 2.6), (8.0, fy + 2.6), 19.2, 21.0, 5.5, rng, m=SF, m2=SFD, course=0.9, mix=0.35)
    mb.box2((-8.2, fy - 0.35, 20.9), (8.2, y0, 21.35), SFD, 0.12)
    masonry_wall(mb, (-6.2, fy + 3.1), (6.2, fy + 3.1), 21.35, 23.3, 4.5, rng, m=SF, m2=SFD, course=0.95, mix=0.35)
    mb.beam((0, fy + 0.7, 23.15), (0, y0 - 1.25, 24.15), 12.8, 0.45, SFD, 0.1)
    for s in (-1, 1):
        mb.box((0.5, 0.3, 3.6), (s * 7.95, fy - 0.2, 19.95), (0, 0, 0), "Metal_Dark", 0.03)
        mb.box((0.45, 0.3, 2.0), (s * 6.15, fy + 0.5, 22.3), (0, 0, 0), "Metal_Dark", 0.03)
    # correntes: guirlandas ate os cantos do salao + correntes com gancho penduradas da cornija
    for s in (-1, 1):
        chain_links(mb, (s * 8.6, fy - 1.0, 17.8), (s * 17.8, y0 - 0.3, 21.2), sag=2.2, link=1.25)
        hanging_chain(mb, (s * 7.5, fy - 1.1, 16.75), 1.9, link=0.95)
    # lanternas em bracos de ferro dos dois lados da boca
    for s in (-1, 1):
        a = Vector((s * 7.95, fy - 0.1, 14.2))
        b = Vector((s * 10.1, fy - 1.5, 14.2))
        mb.beam(a, b, 0.3, 0.3, "Metal_Dark", 0.0)
        mb.beam(a - Vector((0, 0, 1.3)), a + (b - a) * 0.6, 0.22, 0.22, "Metal_Dark", 0.0)
        hanging_lantern(mb, (b.x, b.y, b.z), name="L_HearthLamp_%d" % (s + 1), chain=0.35)
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
    zc = top - 8

    def ro(z):
        return (R - 0.9) - 1.1 * (z - 26.0) / (zc - 26.0)

    def P(a, r, z):
        return Vector((cx + math.cos(a) * r, cy + math.sin(a) * r, z))
    # base (alvenaria grossa) com arco frontal (para o salao) e porta traseira
    gaps = [(270.0, 4.0, FL, 17.0), (90.0, 2.8, FL, 13.0)]
    ring_masonry(mb, cx, cy, R - 2.2, R, F0 - 0.5, 26.0, rng, course=2.2, gaps=gaps, mix=0.3, blk=3.6)
    # fuste afilando: alvenaria 26..34, cinta de chapas de ferro 34..42 (onde chegam os tubos), alvenaria 42..coroa
    ring_masonry(mb, cx, cy, ro(26) - 1.9, ro(26), 26.0, 34.0, rng, course=2.0, mix=0.3, taper=ro(26) - ro(34), blk=3.2)
    ring_masonry(mb, cx, cy, ro(42) - 1.9, ro(42), 42.0, zc, rng, course=2.6, mix=0.35, taper=ro(42) - ro(zc), blk=3.8)
    rb = ro(38.0)
    mb.cyl(rb - 0.1, 8.2, (cx, cy, 38.0), (0, 0, 0), SFD, 20, bevel=0.0, caps=False)
    npan = 14
    pm = ("Metal_Iron", "Metal_Dark", "Metal_Iron", "Metal_Iron", "Metal_Rust", "Metal_Iron", "Metal_Dark")
    for i in range(npan):
        a = (i + 0.5) / npan * math.tau
        chord = 2 * (rb + 0.2) * math.sin(math.pi / npan)
        mb.box((0.36, chord + 0.05, 7.7 + rng.uniform(-0.15, 0.1)), P(a, rb + 0.18, 38.0), (0, 0, a), pm[i % len(pm)], 0.05)
        a2 = i / npan * math.tau
        mb.box((0.3, 0.6, 7.9), P(a2, rb + 0.42, 38.0), (0, 0, a2), "Metal_Dark", 0.03)
        for zz in (35.0, 37.0, 39.0, 41.0):
            rivet(mb, P(a2, rb + 0.55, zz), (math.cos(a2), math.sin(a2), 0), 0.19, "Metal_Brass")
    # cintas de ferro pesadas (duplas em cima) com rebites
    for (z, h, ext, m, nr) in ((26.0, 1.7, None, "Metal_Dark", 16), (33.6, 1.3, 0.62, "Metal_Dark", 12),
                               (42.4, 1.3, 0.62, "Metal_Dark", 12), (58.0, 1.5, 0.5, "Metal_Dark", 12),
                               (59.7, 0.5, 0.42, "Metal_Iron", 0), (80.0, 1.5, 0.5, "Metal_Dark", 12),
                               (81.7, 0.5, 0.42, "Metal_Iron", 0)):
        rr = (R + 0.55) if ext is None else ro(z) + ext
        mb.cyl(rr, h, (cx, cy, z), (0, 0, 0), m, 24, bevel=0.08)
        for i in range(nr):
            a = (i + 0.25) / nr * math.tau
            rivet(mb, P(a, rr - 0.02, z), (math.cos(a), math.sin(a), 0), 0.2, "Metal_Brass")

    # fendas incandescentes em grupo de tres na frente (moldura de pedra clara saliente)
    def slit_group(angs, z0, z1, w=1.05):
        a_mid = D(sum(angs) / len(angs))
        r = ro((z0 + z1) / 2)
        step = D(angs[1] - angs[0]) if len(angs) > 1 else D(11)
        edges = [D(angs[0]) - step / 2] + [D(a) + step / 2 for a in angs]
        for a in angs:
            mb.box((0.3, w, z1 - z0), P(D(a), r + 0.1, (z0 + z1) / 2), (0, 0, D(a)), "Forge_Glow_Soft", 0.0)
        for e in edges:
            mb.box((1.1, 0.6, z1 - z0 + 0.2), P(e, r + 0.05, (z0 + z1) / 2), (0, 0, e), "Stone_Light", 0.08)
        span = 2 * (r + 0.1) * math.sin((edges[-1] - edges[0]) / 2) + 0.9
        mb.box((1.2, span, 0.9), P(a_mid, r, z1 + 0.45), (0, 0, a_mid), "Stone_Light", 0.12)
        mb.box((1.5, span + 0.4, 0.55), P(a_mid, r + 0.1, z0 - 0.3), (0, 0, a_mid), "Stone_Light", 0.12)
        mb.box((0.25, span - 0.6, 0.25), P(a_mid, r + 0.62, (z0 + z1) / 2), (0, 0, a_mid), "Metal_Dark", 0.0)
    slit_group((259.0, 270.0, 281.0), 61.0, 74.0)
    slit_group((90.0,), 63.0, 71.0)
    slit_group((196.0,), 64.0, 72.0)
    slit_group((344.0,), 64.0, 72.0)

    # respiros com grade (brilho da fornalha) nas diagonais da frente e do fundo
    def grille(a_deg, z0, z1, w):
        a = D(a_deg)
        r = ro((z0 + z1) / 2)
        mb.box((0.3, w, z1 - z0), P(a, r + 0.08, (z0 + z1) / 2), (0, 0, a), "Forge_Glow_Soft", 0.0)
        t = Vector((-math.sin(a), math.cos(a), 0))
        c = P(a, r + 0.3, (z0 + z1) / 2)
        for s in (-1, 1):
            mb.box((0.7, 0.4, z1 - z0 + 0.8), c + t * s * (w / 2 + 0.2), (0, 0, a), "Metal_Dark", 0.04)
            mb.box((0.7, w + 1.2, 0.4), c + Z * s * ((z1 - z0) / 2 + 0.2), (0, 0, a), "Metal_Dark", 0.04)
        for k in (-1, 0, 1):
            mb.box((0.25, 0.22, z1 - z0), c + t * k * w * 0.28 + Vector((math.cos(a), math.sin(a), 0)) * 0.12,
                   (0, 0, a), "Metal_Dark", 0.0)
    for ad in (245.0, 295.0, 60.0, 130.0):
        grille(ad, 47.5, 51.0, 2.4)

    # coroa: colarinho alargado (sino) com cinta, cabeca com anel de janelas incandescentes, cornija de ferro rebitada
    mb.cyl(ro(zc) + 0.15, 3.4, (cx, cy, zc - 1.6), (0, 0, 0), SFD, 24, r2=R + 0.3, bevel=0.0, caps=False)
    mb.cyl(ro(zc - 3.2) + 0.45, 0.9, (cx, cy, zc - 3.0), (0, 0, 0), "Metal_Dark", 24, bevel=0.06)
    for i in range(8):
        a = (i + 0.5) / 8 * math.tau
        mb.beam(P(a, ro(zc - 3.0) + 0.35, zc - 3.0), P(a, R + 0.35, zc - 0.1), 0.7, 0.35, "Metal_Iron", 0.04)
    mb.cyl(R + 0.35, 1.2, (cx, cy, zc + 0.6), (0, 0, 0), "Metal_Dark", 24, bevel=0.08)
    nwin = 12
    zw0, zw1 = zc + 1.2, zc + 5.8
    mb.cyl(R - 1.0, zw1 - zw0, (cx, cy, (zw0 + zw1) / 2), (0, 0, 0), SFD, 24, bevel=0.0, caps=False)
    for i in range(nwin):
        a = i / nwin * math.tau
        a2 = (i + 0.5) / nwin * math.tau
        mb.box((1.4, 1.9, zw1 - zw0), P(a, R - 0.4, (zw0 + zw1) / 2), (0, 0, a), SF, 0.12)
        chord = 2 * (R - 0.75) * math.sin(math.pi / nwin)
        mb.box((0.4, chord * 0.64, zw1 - zw0 - 0.7), P(a2, R - 0.8, (zw0 + zw1) / 2 + 0.1), (0, 0, a2),
               "Forge_Glow_Soft", 0.0)
        mb.box((0.9, chord * 0.7, 0.35), P(a2, R - 0.45, zw0 + 0.25), (0, 0, a2), "Stone_Light", 0.05)
    mb.cyl(R + 0.4, 1.0, (cx, cy, zw1 + 0.5), (0, 0, 0), "Metal_Iron", 24, bevel=0.08)
    mb.cyl(R + 1.05, 0.8, (cx, cy, zw1 + 1.4), (0, 0, 0), "Metal_Dark", 24, r2=R + 0.75, bevel=0.1)
    for i in range(20):
        a = (i + 0.5) / 20 * math.tau
        rivet(mb, P(a, R + 1.0, zw1 + 1.3), (math.cos(a), math.sin(a), 0), 0.22, "Metal_Brass")
    # boca interna incandescente (visivel de cima e de longe)
    mb.cyl(R - 1.3, 0.3, (cx, cy, zw1 + 1.2), (0, 0, 0), "Forge_Emissive", 20, bevel=0.0)
    mb.cyl(R - 0.3, 0.5, (cx, cy, zw1 + 1.6), (0, 0, 0), "Metal_Dark", 24, bevel=0.0, caps=False)
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
            masonry_wall(mb, (x0, fy), (x1, fy), F0, zs, t, rng, openings=[(2.0, 6.0, F0, 8.5)], m=SF, m2=SFD, mix=0.28)
            timber_wall_irr(mb, (x0, fy), (x1, fy), zs, ze, t * 0.8, rng,
                        openings=[(2.0, 6.0, zs, 11.0), (8.5, 12.5, 12.5, 19.2)], post=3.5)
            window_glow(mb, (x0, fy), (x1, fy), 2.0, 6.0, F0 + 0.8, zs, t * 0.8)
            window_glow(mb, (x0, fy), (x1, fy), 2.0, 6.0, zs, 11.0, t * 0.8)
        else:
            masonry_wall(mb, (x0, fy), (x1, fy), F0, zs, t, rng, openings=[(9.5, 12.5, F0, 8.5)], m=SF, m2=SFD, mix=0.28)
            timber_wall_irr(mb, (x0, fy), (x1, fy), zs, ze, t * 0.8, rng,
                        openings=[(9.5, 12.5, zs, 11.5), (2.5, 6.0, 12.0, 15.5)], post=3.5)
            window_glow(mb, (x0, fy), (x1, fy), 2.5, 6.0, 12.0, 15.5, t * 0.8)
        # fundo (y1)
        by = y1 - t / 2
        masonry_wall(mb, (x0, by), (x1, by), F0, zs, t, rng, m=SF, m2=SFD, mix=0.28)
        timber_wall_irr(mb, (x0, by), (x1, by), zs, ze, t * 0.8, rng, openings=[(5.0, 9.0, 11.5, 15.0)], post=3.5)
        window_glow(mb, (x0, by), (x1, by), 5.0, 9.0, 11.5, 15.0, t * 0.8)
        # parede externa: L = portao do trilho (y 13..23); R = furo do eixo + janelas
        if side == "L":
            masonry_wall(mb, (ox, y0), (ox, y1), F0, zs, t, rng, openings=[(7.0, 17.0, F0, zs + 1)], m=SF, m2=SFD, mix=0.28)
            timber_wall_irr(mb, (ox, y0), (ox, y1), zs, ze, t * 0.8, rng, openings=[(7.0, 17.0, zs, 15.0)], post=3.3)
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
            masonry_wall(mb, (ox, y0), (ox, y1), F0, zs, t, rng, openings=[(4.0, 8.0, F0 + 2.5, zs)], m=SF, m2=SFD, mix=0.28)
            window_glow(mb, (ox, y0), (ox, y1), 4.0, 8.0, F0 + 2.5, zs, t)
            timber_wall_irr(mb, (ox, y0), (ox, y1), zs, ze, t * 0.8, rng, openings=[(13.0, 15.0, 14.5, 16.5)], post=3.3)
        # oitoes frente/fundo
        for gy in (fy, by):
            mb.gable_wall(cx, gy, x1 - x0, ze, 7.0, t * 0.8, "Y", "Plaster_Forge")
            off = -t * 0.45 if gy == fy else t * 0.45
            mb.beam((x0, gy + off, ze + 0.3), (x1, gy + off + rng.uniform(-0.05, 0.05), ze + 0.3 + rng.uniform(-0.1, 0.1)),
                    0.7, 0.8, "Wood_Dark", 0.06)
            kx = cx + rng.uniform(-0.2, 0.2)
            mb.beam((kx, gy + off, ze), (cx, gy + off, ze + 6.6), 0.6, 0.7, "Wood_Dark", 0.06)
            # escoras do oitao (em V) e barrotes dos beirais inclinados
            for s in (-1, 1):
                mb.beam((cx + s * 4.8, gy + off, ze + 0.5), (kx + s * 0.4, gy + off, ze + 4.6 + rng.uniform(-0.3, 0.3)),
                        0.45, 0.55, "Wood_Dark", 0.05)
                mb.beam((cx + s * (x1 - x0) / 2 * 1.02, gy + off * 1.4, ze + 0.1), (cx, gy + off * 1.4, ze + 7.0 - 0.1),
                        0.5, 0.65, "Wood_Dark", 0.05)
        # telhado irregular (ardosia escura, cumeeira com barriga, fileiras variando)
        forge_roof(mb, cx, (y0 + y1) / 2, x1 - x0, y1 - y0, ze, 7.0, rng, thick=0.8, over=1.4,
                   sag=0.4 if side == "L" else 0.3, row_h=1.65, seg=7.5, patches=1)
        for yy in (y0 + 6.5, y0 + 13, y0 + 19.5):
            yj = yy + rng.uniform(-0.3, 0.3)
            mb.beam((x0 + 1, yj, ze - 0.3), (x1 - 1, yj + rng.uniform(-0.2, 0.2), ze - 0.3 + rng.uniform(-0.12, 0.12)),
                    0.7, 0.9, "Wood_Dark", 0.06)
        # cintas de ferro nos cantos da alvenaria (base industrial)
        for (xx, yy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            if (side == "L" and xx == x1) or (side == "R" and xx == x0):
                continue
            for zz in (F0 + 2.4, zs - 0.8):
                mb.box((1.9, 1.9, 0.45), (xx, yy, zz), (0, 0, 0), "Metal_Dark", 0.04)
        # piso
        pave_poly(mb, [(x0 + t, y0 + t), (x1 - t, y0 + t), (x1 - t, y1 - t), (x0 + t, y1 - t)], F0 + 0.0, rng,
                  tile=3.2, h=0.3, grout=False)
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
    ze_hall = 24.0
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
    light("L_Hall_Fill", "POINT", (0, 13.0, 16.0), 650, (1.0, 0.62, 0.38), 4.0)
    # talha de corrente pendurada na tesoura central (gancho com lingote) e estante de lingotes aquecidos
    mb.box((1.2, 1.2, 1.0), (4.0, 13.0, ze_hall - 1.4), (0, 0, 0), "Metal_Dark", 0.06)
    mb.cyl(0.55, 0.5, (4.0, 13.0, ze_hall - 2.3), (D(90), 0, 0), "Metal_Iron", 10, bevel=0.0)
    hanging_chain(mb, (4.0, 13.0, ze_hall - 2.6), 7.2, link=0.9)
    mb.box((1.8, 0.7, 0.6), (4.35, 13.0, ze_hall - 11.3), (0, 0, 0.2), "Ember_Glow", 0.06)
    for k in range(4):
        mb.box((1.3, 0.5, 0.35), (15.2 - 1.2 + k * 0.8, 17.8, FL + 3.6), (0, 0, 0.15 * (k % 2)),
               "Ember_Glow" if k in (1, 2) else "Metal_Iron", 0.04)
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
    # (a tubulacao externa grossa ate a torre fica em fm_forge_annex.pipes)
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
    mb.box((1.6, 0.6, 0.25), (ax + 0.5, ay, FL + 3.7), (0, 0, 0.3), "Ember_Glow", 0.06)
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
    light("L_Hearth_Fire", "POINT", (0, 0.5, FL + 4.5), 1300, (1.0, 0.38, 0.08), 2.0)
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
    import fm_forge_annex
    fm_forge_annex.build(random.Random(405))
