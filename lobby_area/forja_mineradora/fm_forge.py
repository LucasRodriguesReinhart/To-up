# fm_forge - FORJA DO IGNIS (asset heroi). Planta (inalterada):
#   salao x-20..20 y4..22 (piso 5) | lareira aberta na fachada (x-8..8, y-1.5..4) | Ignis y-5 | bigorna y-10
#   torre-chamine (0,30) nascendo da casa da fornalha x-13..13 y20..40 | ala esq. = recebimento de minerio (trilho) +
#   loft/varanda + guindaste | ala dir. = casa dos foles (eixo da roda d'agua, fole gigante na fachada leste) + balcao
# Passe "fabrica artesanal": fachada em tabuado vertical e chapas de ferro rebitadas com fuligem na metade de cima
# (o reboco creme fica so nas casas), boca da forja retangular chanfrada com moldura rebitada, garganta incandescente
# em degrade e chamas em laminas, coifa de ferro -> fumeiro -> torre, alas com telhados de formas diferentes
# (meia-agua x duas aguas) dentro do mesmo envelope, alas fechadas por dentro. Torre/casa em fm_forge_tower;
# anexos em fm_forge_annex. No fim os objetos sao agrupados por area (menos MeshParts no Roblox).
import math, random
from mathutils import Vector, Matrix
from fm_lib import D, col_box, col_box2, marker, light
from fm_parts import (Frame, masonry_wall, arch, window_glow, banner, emblem_hammers, hanging_lantern, crate, barrel,
                      crystal_cluster, fence, pave_ring, pave_poly, stairs)
from fm_forge_kit import (FB, xz_prism, octagon, forge_roof, forge_shed_roof, clad_wall, board_gable, iron_bracket,
                          chain_links, hanging_chain, rivet, flame_blade, boss, rufo, tube_pt, Z, WING_EAVE, WING_RISE_L,
                          WING_RISE_R)
import fm_layout as L

C = "03_FORGE"
F0 = L.FLOOR
FL = L.FL
SF, SFD = "Stone_Forge", "Stone_Forge_Dark"


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
        i = min(range(len(pts) - 1), key=lambda k: (pts[k] - p).length + (pts[k + 1] - p).length)
        t = (pts[i + 1] - pts[i]).normalized()
        mb.rod(p - t * 0.25, p + t * 0.25, r * 1.28, flange_m, 12)


def crest(mb, c, rng, s=1.0):
    """brasao da forja no oitao: tabua octogonal, moldura de ferro rebitada, martelos cruzados sobre bigorna"""
    cx, fy, cz = c

    def W(pts):
        return [(cx + u * s, cz + v * s) for u, v in pts]
    xz_prism(mb, W(octagon(11.4, 10.8, 2.8)), fy - 0.45, fy + 0.02, "Wood_Dark")
    outer, inner = octagon(9.8, 9.2, 2.4), octagon(8.0, 7.4, 1.95)
    for i in range(8):
        j = (i + 1) % 8
        xz_prism(mb, W([outer[i], outer[j], inner[j], inner[i]]), fy - 1.0, fy - 0.4, "Metal_Dark")
    xz_prism(mb, W(inner), fy - 0.8, fy - 0.4, "Metal_Dark")
    for i in range(8):
        j = (i + 1) % 8
        u = (outer[i][0] + outer[j][0]) / 2
        v = (outer[i][1] + outer[j][1]) / 2
        ui = (inner[i][0] + inner[j][0]) / 2
        vi = (inner[i][1] + inner[j][1]) / 2
        rivet(mb, (cx + s * (u + ui) / 2, fy - 1.0, cz + s * (v + vi) / 2), (0, -1, 0), 0.26, "Metal_Brass")
    emblem_hammers(mb, Vector((cx, fy - 0.85, cz + 0.75 * s)), 0.0, s=1.2 * s, m="Emblem_Cream", off=0.15)
    anvil = [(-2.3, 0.45), (-1.3, 0.05), (-0.75, 0.0), (-0.65, -0.55), (-1.25, -1.0), (1.25, -1.0), (0.65, -0.55),
             (0.75, 0.0), (1.9, 0.05), (1.9, 0.55), (-1.0, 0.6)]
    xz_prism(mb, [(cx + u * s, cz + (v - 2.55) * s) for u, v in anvil], fy - 1.05, fy - 0.8, "Metal_Brass")
    mb.ico(0.42 * s, (cx, fy - 1.1, cz + 0.75 * s), "Forge_Glow_Soft", 1, (1, 0.6, 1))


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
                       "Metal_Dark", 0.0)
    for yy in (y0, y1):
        mb.box2((cx - hw, yy - 0.25, zb), (cx + hw, yy + 0.25, zt), "Wood_Dark", 0.06)
    mb.box2((cx - hw - 0.2, y0 - 0.2, zt - 0.3), (cx + hw + 0.2, y1 + 0.2, zt), "Metal_Dark", 0.04)
    forge_roof(mb, cx, (y0 + y1) / 2, w + 0.2, y1 - y0, zt, 1.7, rng, thick=0.55, over=0.8, sag=0.08, row_h=1.1,
               seg=3.5, patches=0)


# ------------------------------------------------------------------ fundacao, tablado, piso
def foundation(rng):
    mb = FB("FORGE_Foundation_Dais", C, rng, detail="near")
    x0, y0, x1, y1 = L.FORGE_HALL
    mb.box2((x0 - 0.8, y0 - 0.2, F0 - 1.0), (x1 + 0.8, y1, FL - 0.3), SFD, 0.2)
    mb.box2((x0 - 0.8, y0 - 0.2, FL - 0.3), (x1 + 0.8, y0 + 2.2, FL), SFD, 0.1)
    # plinto das alas so no perimetro (topo 4.25) + contrapiso de rejunte: o piso interno (4.04..4.34) nunca fica
    # coplanar com o plinto (z-fighting em 4.29/4.30)
    e, bnd = 0.8, 1.6
    for (wx0, wy0, wx1, wy1) in (L.FORGE_WING_L, L.FORGE_WING_R):
        zt = F0 + 0.25
        mb.box2((wx0 - e, wy0 - 0.6, F0 - 1.0), (wx1 + e, wy0 + bnd, zt), SFD, 0.2)
        mb.box2((wx0 - e, wy1 - bnd, F0 - 1.0), (wx1 + e, wy1 + 0.6, zt), SFD, 0.2)
        mb.box2((wx0 - e, wy0 + bnd, F0 - 1.0), (wx0 + bnd, wy1 - bnd, zt), SFD, 0.2)
        mb.box2((wx1 - bnd, wy0 + bnd, F0 - 1.0), (wx1 + e, wy1 - bnd, zt), SFD, 0.2)
        mb.box2((wx0 + bnd, wy0 + bnd, F0 - 0.5), (wx1 - bnd, wy1 - bnd, F0 + 0.1), SFD, 0.0)
    pave_poly(mb, [(x0 + 2.2, y0 + 2.2), (x1 - 2.2, y0 + 2.2), (x1 - 2.2, y1 - 2.2), (x0 + 2.2, y1 - 2.2)],
              FL - 0.3, rng, tile=3.3, h=0.3, grout=False, m="Stone_Paving")
    cx, cy = L.DAIS_C
    R = L.DAIS_R + 1
    poly = [(cx + math.cos(D(a)) * R, cy + math.sin(D(a)) * R) for a in range(180, 361, 10)] + [(R, y0), (-R, y0)]
    mb.prism(poly, F0 - 0.5, FL - 0.35, SFD, bevel=0.25)
    pave_ring(mb, cx, cy, 0.0, R - 1.2, FL - 0.35, rng, 180, 360, ring_w=2.4, h=0.35, m="Stone_Paving")
    mb.box2((-R + 1, cy, FL - 0.35), (R - 1, y0 - 0.2, FL), "Stone_Paving", 0.1)
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
    rise = 13.0
    mb = FB("FORGE_Hall_Walls", C, rng, detail="near")

    def zroof(x):
        return ze + rise * (1 - abs(x) / 20.0)
    # parede frontal: portas em x=+-14.5 (6 de vao, arco)
    fy = y0 + t / 2
    doors = [(-14.5, 6.0), (14.5, 6.0)]
    ops = [(dx + 20 - w / 2, dx + 20 + w / 2, FL, 15.0, 3.0) for dx, w in doors]
    masonry_wall(mb, (x0, fy), (x1, fy), FL, zs, t, rng, openings=ops, m=SF, m2=SFD, mix=0.1, course=1.9,
                 blk=(2.4, 4.0))
    for dx, w in doors:
        arch(mb, (dx, fy, 0), 0.0, w, 12.0, 3.0, t + 0.3, "Stone_Light", "Metal_Brass", n=9, band=1.2)
        for sx in (-1, 1):
            for zz in (FL + 2.0, FL + 6.0):
                mb.box((0.9, 0.35, 0.45), (dx + sx * (w / 2 + 0.35), y0 - 0.12, zz), (0, 0, 0), "Metal_Dark", 0.03)
    # laterais (portas internas para as alas: y 9..15)
    for sx in (x0 + t / 2, x1 - t / 2):
        masonry_wall(mb, (sx, y0), (sx, y1), FL, zs, t, rng, openings=[(5.0, 11.0, FL, 14.0, 2.5)], m=SF, m2=SFD,
                     mix=0.1, course=1.9, blk=(2.4, 4.0))
        arch(mb, (sx, y0 + 8.0, 0), D(90), 6.0, 11.5, 2.5, t + 0.3, n=7, band=1.1)
    # fundo: so os trechos fora da casa da fornalha (o trecho central e a frente da casa, em fm_forge_tower)
    by = y1 - t / 2
    masonry_wall(mb, (x0, by), (-13.0, by), FL, zs, t, rng, m=SF, m2=SFD, mix=0.1, course=1.9, blk=(2.4, 4.0))
    masonry_wall(mb, (13.0, by), (x1, by), FL, zs, t, rng, m=SF, m2=SFD, mix=0.1, course=1.9, blk=(2.4, 4.0))
    # andar de cima: tabuado vertical + chapas de ferro rebitadas, fuligem na metade de cima (fabrica, nao casa)
    ct = t * 0.8
    clad_wall(mb, (x0, fy), (-7.0, fy), zs, ze, ct, rng, openings=[(3.5, 7.5, 18.0, 22.0)], out=-1, iron=(2,),
              post=3.3)
    clad_wall(mb, (7.0, fy), (x1, fy), zs, ze, ct, rng, openings=[(5.5, 9.5, 18.0, 22.0)], out=-1, iron=(0, 3),
              post=3.3)
    for (a_, b_, s0, s1) in (((x0, fy), (-7.0, fy), 3.5, 7.5), ((7.0, fy), (x1, fy), 5.5, 9.5)):
        window_glow(mb, a_, b_, s0, s1, 18.0, 22.0, ct, m="Forge_Glow_Soft")
    clad_wall(mb, (x0 + t / 2, y0), (x0 + t / 2, y1), zs, ze, ct, rng, out=1, iron=(1, 4), post=3.6)
    clad_wall(mb, (x1 - t / 2, y0), (x1 - t / 2, y1), zs, ze, ct, rng, out=-1, iron=(0, 3), post=3.6)
    clad_wall(mb, (x0, by), (-13.0, by), zs, ze, ct, rng, out=1, zt=lambda s: zroof(x0 + s) - 0.1, post=3.5,
              iron=(0,))
    clad_wall(mb, (13.0, by), (x1, by), zs, ze, ct, rng, out=1, zt=lambda s: zroof(13.0 + s) - 0.1, post=3.5)
    # oitao frontal EM BALANCO (tabuas verticais, fuligem no alto) sobre viga e maos-francesas de ferro
    jf = y0 - 1.1
    board_gable(mb, 0.0, jf, 40.0, ze, rise, 1.3, rng, facing=-1, m_top="Wood_Soot", soot_at=0.6)
    for (xa, xb) in ((-20.6, -2.3), (2.3, 20.6)):
        mb.box2((xa, jf - 0.2, ze - 0.8), (xb, y0 + 0.3, ze + 0.1), "Wood_Dark", 0.1)
    for xx in (-18.4, -11.4, 11.4, 18.4):
        iron_bracket(mb, (xx, y0 + 0.05, ze - 0.8), (0, -1), 1.9, "Metal_Dark", 0.6, 0.34, rm="Metal_Dark",
                     scroll=abs(xx) > 15)
    # (sem lanternas brancas na fachada: o fogo da boca e o ponto mais claro; ganchos seguram as guirlandas)
    for s in (-1, 1):
        mb.box((0.5, 0.9, 0.5), (s * 17.8, y0 - 0.6, 21.4), (0, 0, 0), "Metal_Dark", 0.0)
    mb.beam((-20.8, jf - 0.25, ze + 0.35), (20.8, jf - 0.2, ze + 0.45), 0.7, 0.8, "Wood_Dark", 0.08)
    for s in (-1, 1):
        mb.beam((s * 20.6, jf - 0.25, ze + 0.2), (0, jf - 0.25, ze + rise - 0.1), 0.55, 0.7, "Wood_Dark", 0.06)
    crest(mb, Vector((0.6, jf, ze + 6.4)), rng, s=0.76)     # menor: o fumeiro sobe rente ao oitao ao lado dele
    # contrafortes de pedra nos cantos
    for cx_ in (x0 - 0.4, x1 + 0.4):
        mb.box((2.6, 2.6, zs - FL + 1), (cx_, y0 + 0.4, (FL + zs) / 2 - 0.5), (0, 0, 0), SFD, 0.3)
        mb.box((3.0, 3.0, 0.8), (cx_, y0 + 0.4, zs + 0.2), (0, 0, 0), "Stone_Light", 0.2)
        for zz in (FL + 3.0, FL + 8.0):
            mb.box((2.9, 2.9, 0.5), (cx_, y0 + 0.4, zz), (0, 0, 0), "Metal_Dark", 0.04)
    mb.finish()

    # telhado irregular (cumeeira com barriga) + tesouras levemente tortas + lanternim de ventilacao
    rf = FB("FORGE_Hall_Roof", C, rng, detail="near", far_z=40.0)
    # beiral 1.4 (nao 1.8): o canto do beiral ficava na visada spawn -> Shadow Garden / Demon Slayer
    forge_roof(rf, 0.0, (y0 + y1) / 2 - 0.5, 40.0, 17.0, ze, rise, rng, thick=0.9, over=1.4, sag=0.55, row_h=1.9,
               seg=7.0, patches=0)
    for yy in (8.0, 13.0, 18.0):
        yj = yy + rng.uniform(-0.25, 0.25)
        rf.beam((-19, yj, ze - 0.4), (19, yj + rng.uniform(-0.2, 0.2), ze - 0.4 + rng.uniform(-0.15, 0.15)), 0.9, 1.1,
                "Wood_Dark", 0.08)
        rf.beam((0, yj, ze - 0.4), (rng.uniform(-0.15, 0.15), yj, ze + 12.0), 0.8, 0.8, "Wood_Dark", 0.08)
        for s in (-1, 1):
            rf.beam((s * 19, yj, ze), (0, yj, ze + 12.4 + rng.uniform(-0.2, 0.1)), 0.8, 0.9, "Wood_Dark", 0.08)
            rf.beam((s * 9, yj, ze - 0.2), (s * rng.uniform(0.0, 0.3), yj, ze + 6), 0.6, 0.6, "Wood_Dark", 0.06)
    roof_monitor(rf, rng, 0.0, 7.0, 16.5, 5.2, ze + rise - 0.65 * 2.6 - 0.2, ze + 15.9)
    rf.finish()

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
    mb = FB("FORGE_Hearth", C, rng, detail="hero")
    fy = -1.5
    wy = fy + 1.2                     # parede frontal y -1.5..0.9
    hw, zt_, ch = 5.2, 13.0, 1.4      # boca RETANGULAR chanfrada (nao arco de forno de pao)
    ops = [(8.0 - hw, 8.0 + hw, FL, zt_)]
    masonry_wall(mb, (-8, wy), (8, wy), FL, 11.0, 2.4, rng, openings=ops, m=SF, m2=SFD, course=1.6, mix=0.12,
                 blk=(2.2, 3.6))
    # pedra do entorno escurecida de fuligem acima da boca
    masonry_wall(mb, (-8, wy), (8, wy), 11.0, 15.4, 2.4, rng, openings=ops, m=SFD, m2=SF, course=1.5, mix=0.25,
                 blk=(2.2, 3.6))
    for sx in (-6.5, 6.5):
        masonry_wall(mb, (sx, 0.9), (sx, y0), FL, 15.4, 3.0, rng, m=SFD, m2=SF, course=2.0, mix=0.3, blk=(2.4, 3.6))
    mb.box2((-5.0, 0.9, zt_), (5.0, y0, 15.4), SFD, 0.0)            # teto da garganta
    # peito de pedra enegrecida atras/acima da coifa (fecha ate o oitao)
    masonry_wall(mb, (-7.0, 2.2), (7.0, 2.2), 15.4, 24.0, 3.6, rng, m=SFD, m2=SF, course=1.7, mix=0.25,
                 blk=(2.2, 3.6))
    # faces internas da boca em pedra em brasa + cantos chanfrados
    SH = "Stone_Heated"
    for s in (-1, 1):
        mb.box2((s * hw - (0.12 if s > 0 else 0.0), fy + 0.02, FL), (s * hw + (0.12 if s < 0 else 0.0), 0.9, zt_ - ch),
                SH, 0.0)
        xz_prism(mb, [(s * hw, zt_ - ch), (s * hw, zt_), (s * (hw - ch), zt_)], fy + 0.02, 0.9, SFD)
        mb.beam((s * hw, (fy + 0.9) / 2, zt_ - ch), (s * (hw - ch), (fy + 0.9) / 2, zt_), 2.36, 0.14, SH, 0.0)
    mb.box2((-(hw - ch), fy + 0.02, zt_ - 0.12), (hw - ch, 0.9, zt_), SH, 0.0)
    # garganta (y 0.9..4) forrada em degrade: brasa viva embaixo, laranja, rubro e pedra em brasa no alto
    # (o fundo escurece para cima: as laminas de chama na frente saltam contra ele)
    bands = ((FL + 2.6, FL + 3.9, "Fire_Glow_Core"), (FL + 3.9, FL + 5.3, "Fire_Glow_Mid"),
             (FL + 5.3, FL + 6.9, "Ember_Glow"), (FL + 6.9, zt_, "Stone_Heated"))
    for za, zb, m in bands:
        mb.box2((-5.0, y0 - 0.25, za), (5.0, y0 - 0.05, zb), m, 0.0)
        for s in (-1, 1):
            mb.box2((s * 4.95 - 0.1, 0.9, za), (s * 4.95 + 0.1, y0 - 0.2, zb), m, 0.0)
    mb.box2((-5.0, 0.9, zt_ - 0.18), (5.0, y0 - 0.2, zt_ - 0.02), "Stone_Heated", 0.0)
    # leito de brasas 1 stud mais alto (o fogo aparece por cima da bigorna, topo ~8.6)
    zb_ = FL + 2.6
    mb.box2((-5.0, -1.15, FL), (5.0, y0 - 0.2, zb_), SFD, 0.15)
    mb.box2((-5.15, -1.45, zb_ - 0.35), (5.15, -1.0, zb_ + 0.05), "Ember_Glow", 0.0)
    mb.box2((-4.8, -0.9, zb_ - 0.1), (4.8, y0 - 0.3, zb_ + 0.15), "Fire_Glow_Mid", 0.0)
    for i in range(22):
        x = rng.uniform(-4.4, 4.4)
        yy = rng.uniform(-0.7, 3.4)
        hh = 0.45 * (1 - (x / 5.2) ** 2) + rng.uniform(0.0, 0.25)
        s = rng.uniform(0.9, 1.35)
        mb.rock((x, yy, zb_ + 0.1 + hh), (s, s * rng.uniform(0.8, 1.1), s * 0.55), "Stone_Coal", 0,
                (0, 0, rng.uniform(0, 6)))
    for i in range(12):
        x = rng.uniform(-3.8, 3.8)
        yy = rng.uniform(-0.6, 2.6)
        s = rng.uniform(0.5, 0.85)
        mb.rock((x, yy, zb_ + 0.35 + 0.5 * (1 - (x / 5.2) ** 2)), (s, s, s * 0.6), "Ember_Glow", 0,
                (0, 0, rng.uniform(0, 6)))
    # barras aquecendo nas brasas com as tenazes para fora
    for (x, sk) in ((-2.7, 0.5), (0.5, -0.3), (2.9, 0.35)):
        pin = Vector((x + sk * 2.0, 2.3, zb_ + 0.6))
        pout = Vector((x, -1.1, zb_ + 1.0))
        mb.beam(pin, pout, 0.5, 0.36, "Ember_Glow", 0.0)
        tip = pout + Vector((-sk * 0.7, -1.7, 0.6))
        for s in (-1, 1):
            mb.beam(pout + Vector((s * 0.14, 0.25, 0.0)), tip + Vector((s * 0.24, 0.0, 0.0)), 0.16, 0.16, "Metal_Dark",
                    0.0)
    # chamas em 3 camadas de laminas: rubras altas e largas atras, laranja no meio, amarelas baixas na frente
    rows = ((3.0, "Fire_Glow_Outer", 1.9, (5.0, 5.4), (-3.5, -1.2, 1.2, 3.5)),
            (1.9, "Fire_Glow_Mid", 1.55, (4.0, 4.5), (-3.9, -1.95, 0.0, 1.95, 3.9)),
            (0.6, "Fire_Glow_Core", 1.2, (2.6, 3.2), (-3.0, -1.05, 1.05, 3.0)))
    for (yy, m, w, (h0, h1), xs) in rows:
        for x in xs:
            x += rng.uniform(-0.25, 0.25)
            h = rng.uniform(h0, h1) * (1.06 - abs(x) / 16)
            flame_blade(mb, (x, yy + rng.uniform(-0.2, 0.2), zb_ + 0.05), w * rng.uniform(0.9, 1.1), h, m, rng,
                        depth=0.5, yaw=rng.uniform(-0.3, 0.3), lean=0.35)
    # moldura de ferro rebitada seguindo o chanfro + verga rebitada
    path = [Vector(p) for p in ((-hw, fy, FL), (-hw, fy, zt_ - ch), (-hw + ch, fy, zt_), (hw - ch, fy, zt_),
                                (hw, fy, zt_ - ch), (hw, fy, FL))]
    mb.sweep(path, [(0.0, -0.5), (0.95, -0.5), (0.95, 0.0), (0.0, 0.0)], "Metal_Dark", True, up=(0, 1, 0))
    for (p, q) in zip(path, path[1:]):
        ln = (q - p).length
        n = max(1, int(ln / 1.8))
        d = (q - p).normalized()
        outv = Vector((-d.z, 0.0, d.x))
        for k in range(n):
            c = p + d * (ln * (k + 0.5) / n) + outv * 0.5
            rivet(mb, (c.x, fy - 0.5, c.z), (0, -1, 0), 0.22, "Metal_Brass", 0.14)
    mb.box2((-7.8, fy - 0.45, 13.95), (7.8, fy, 15.3), "Metal_Dark", 0.06)
    for i in range(7):
        rivet(mb, (-6.6 + i * 2.2, fy - 0.45, 14.62), (0, -1, 0), 0.24, "Metal_Brass", 0.16)
    # coifa de ferro rebitada: trapezio que afunila para o fumeiro (duto em fm_forge_tower)
    from fm_parts import frustum
    frustum(mb, (0.0, -0.9, 15.4), 12.0, 2.6, 4.3, 3.7, 5.2, "Metal_Burnt")
    mb.box2((-6.3, -2.45, 15.2), (6.3, 0.6, 15.75), "Metal_Dark", 0.05)
    for u in (-0.6, -0.2, 0.2, 0.6):
        a = Vector((u * 6.0, -2.25, 15.7))
        b = Vector((u * 2.15, -2.8, 20.5))
        mb.beam(a, b, 0.42, 0.22, "Metal_Dark", 0.0)
        for f in (0.2, 0.55, 0.9):
            q = a + (b - a) * f
            rivet(mb, (q.x, q.y - 0.12, q.z), (0, -1, -0.1), 0.2, "Metal_Brass", 0.12)
    # correntes: guirlandas ate os cantos do salao + corrente com gancho na borda da coifa
    for s in (-1, 1):
        chain_links(mb, (s * 6.4, fy - 0.9, 16.2), (s * 17.8, y0 - 0.3, 21.2), sag=2.0, link=1.25)
        hanging_chain(mb, (s * 6.3, fy - 1.0, 15.5), 1.9, link=0.95)
    mb.finish()
    col_box2("Forge", (-8.6, fy - 0.6, FL), (8.6, y0, 21.0))
    bn = FB("FORGE_Banners", C, rng, detail="near")
    for s in (-1, 1):
        banner(bn, (s * 9.9, y0 - 0.45, 20.8), 0.0, w=2.8, h=6.2, cloth="Cloth_Red", trim="Metal_Brass",
               emblem="hammers")
    bn.finish()


# ------------------------------------------------------------------ alas
def wings(rng):
    t = 1.6
    zs = 8.5
    ze = WING_EAVE
    for side, w in (("L", L.FORGE_WING_L), ("R", L.FORGE_WING_R)):
        x0, y0, x1, y1 = w
        cx = (x0 + x1) / 2
        rise = WING_RISE_L if side == "L" else WING_RISE_R
        mb = FB("FORGE_Wing_" + side, C, rng, detail="near")
        outer = x0 if side == "L" else x1
        ox = outer + (t / 2 if side == "L" else -t / 2)
        ix = (x1 - t / 2) if side == "L" else (x0 + t / 2)
        if side == "L":
            # meia-agua: alta no lado de fora (x0), baixa no patio (x1) -> abre a visada spawn->Shadow Garden
            def zroof(x):
                return ze + rise * (x1 - x) / (x1 - x0)
            kinks = ()
        else:
            def zroof(x):
                return ze + rise * (1 - abs(x - cx) / ((x1 - x0) / 2))
            kinks = ((x1 - x0) / 2,)

        def base_wall(a, b, ops):
            masonry_wall(mb, a, b, F0, F0 + 1.1, t, rng, m=SFD, m2=SFD, course=1.1, blk=(2.8, 4.4), openings=ops)
            masonry_wall(mb, a, b, F0 + 1.1, zs, t, rng, m=SF, m2=SFD, course=2.35, mix=0.1, blk=(2.8, 4.4),
                         openings=ops)
        ct = t * 0.8
        # frente (y0) e fundo (y1): tabuado ate a linha do telhado
        fy, by = y0 + t / 2, y1 - t / 2
        zt_front = (lambda s, _x0=x0: zroof(_x0 + s) - 0.1)
        if side == "L":
            base_wall((x0, fy), (x1, fy), [(2.0, 6.0, F0 + 1.1, zs)])
            clad_wall(mb, (x0, fy), (x1, fy), zs, ze, ct, rng, openings=[(2.0, 6.0, zs, 11.0), (8.5, 12.5, 12.5, 18.8)],
                      out=-1, zt=zt_front, kinks=kinks, iron=(3,), post=3.5)
            window_glow(mb, (x0, fy), (x1, fy), 2.0, 6.0, F0 + 1.1, 11.0, ct, m="Forge_Glow_Soft")
        else:
            base_wall((x0, fy), (x1, fy), [(9.5, 12.5, F0, zs)])
            clad_wall(mb, (x0, fy), (x1, fy), zs, ze, ct, rng, openings=[(9.5, 12.5, zs, 11.5), (2.5, 6.0, 12.0, 15.5)],
                      out=-1, zt=zt_front, kinks=kinks, iron=(1,), post=3.5)
            window_glow(mb, (x0, fy), (x1, fy), 2.5, 6.0, 12.0, 15.5, ct, m="Forge_Glow_Soft")
        base_wall((x0, by), (x1, by), [])
        clad_wall(mb, (x0, by), (x1, by), zs, ze, ct, rng, openings=[(5.0, 9.0, 11.5, 15.0)], out=1, zt=zt_front,
                  kinks=kinks, iron=((0,) if side == "L" else (3,)), post=3.5)
        window_glow(mb, (x0, by), (x1, by), 5.0, 9.0, 11.5, 15.0, ct, m="Forge_Glow_Soft")
        # parede externa: L = portao do trilho (y 13..23) com vao LIVRE ate a verga (15.4); R = furo do eixo
        if side == "L":
            zo_top = ze + rise
            base_wall((ox, y0), (ox, y1), [(7.0, 17.0, F0, zs + 1)])
            hi_win = [(2.6, 4.6, 20.2, 23.2), (11.0, 13.0, 19.8, 22.8), (20.8, 22.8, 20.2, 23.2)]
            clad_wall(mb, (ox, y0), (ox, y1), zs, zo_top, ct, rng, openings=[(7.0, 17.0, zs, 15.0)] + hi_win, out=1,
                      iron=(4,), post=3.3)
            for (s0, s1, za, zb) in hi_win:      # lanternins altos: quebram a parede alta da meia-agua
                window_glow(mb, (ox, y0), (ox, y1), s0, s1, za, zb, ct, m="Forge_Glow_Soft")
            for yy in (y0 + 7.0, y0 + 17.0):
                mb.box((2.0, 1.2, 15.0 - F0), (ox, yy, (F0 + 15.0) / 2), (0, 0, 0), "Wood_Dark", 0.15)
            mb.box((2.2, 12.4, 1.4), (ox, y0 + 12.0, 15.4), (0, 0, 0), "Wood_Dark", 0.15)
            for yy, ang in ((y0 + 7.6, D(70)), (y0 + 16.4, D(-70))):
                mb.box((0.5, 4.8, 9.5), (ox + 2.6, yy, F0 + 5.0), (0, 0, ang), "Wood_Plank", 0.1)
            for yy in (y0 + 7.0, y0 + 17.0):
                for zz in (F0 + 1.5, 13.5):
                    mb.box((2.3, 1.5, 0.5), (ox, yy, zz), (0, 0, 0), "Metal_Dark", 0.05)
        else:
            base_wall((ox, y0), (ox, y1), [(4.0, 8.0, F0 + 2.5, zs)])
            window_glow(mb, (ox, y0), (ox, y1), 4.0, 8.0, F0 + 2.5, zs, t, m="Forge_Glow_Soft")
            clad_wall(mb, (ox, y0), (ox, y1), zs, ze, ct, rng, openings=[(13.0, 15.0, 14.5, 16.5)], out=-1,
                      iron=(2, 5), post=3.3)
        # face interna (patio, y 22..32): fecha a ala; aberturas so para a calha (L) e o duto dos foles (R, colar)
        yi0 = L.FORGE_HALL[3]
        if side == "L":
            base_wall((ix, yi0), (ix, y1), [])
            clad_wall(mb, (ix, yi0), (ix, y1), zs, ze, ct, rng, openings=[(0.6, 3.6, 11.4, 15.2)], out=-1, iron=(1,),
                      post=3.4)
            for (p0, p1) in (((ix + 0.6, yi0 + 0.2, 11.0), (ix + 1.05, yi0 + 4.0, 11.4)),
                             ((ix + 0.6, yi0 + 0.2, 15.2), (ix + 1.05, yi0 + 4.0, 15.6)),
                             ((ix + 0.6, yi0 + 0.2, 11.0), (ix + 1.05, yi0 + 0.6, 15.6)),
                             ((ix + 0.6, yi0 + 3.6, 11.0), (ix + 1.05, yi0 + 4.0, 15.6))):
                mb.box2(p0, p1, "Metal_Dark", 0.0)
        else:
            base_wall((ix, yi0), (ix, y1), [])
            clad_wall(mb, (ix, yi0), (ix, y1), zs, ze, ct, rng, out=1, iron=(2,), post=3.4)
            for sgn in (-1, 1):
                boss(mb, (ix + sgn * (t / 2 + 0.25), 27.0, 7.3), (sgn, 0, 0), 2.6)
        # telhados de formas diferentes no mesmo envelope (cumeeira <= 26.5)
        if side == "L":
            forge_shed_roof(mb, x0, x1, y0, y1, ze + rise, ze, rng, thick=0.8, over=1.4, over_hi=0.7, sag=0.35,
                            row_h=1.65, seg=7.5, patches=0)
        else:
            forge_roof(mb, cx, (y0 + y1) / 2, x1 - x0, y1 - y0, ze, rise, rng, thick=0.8, over=1.4, sag=0.3,
                       row_h=1.65, seg=7.5, patches=0)
        for yy in (y0 + 6.5, y0 + 13, y0 + 19.5):
            yj = yy + rng.uniform(-0.3, 0.3)
            mb.beam((x0 + 1, yj, ze - 0.3), (x1 - 1, yj + rng.uniform(-0.2, 0.2), ze - 0.3 + rng.uniform(-0.12, 0.12)),
                    0.7, 0.9, "Wood_Dark", 0.06)
        for (xx, yy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            if (side == "L" and xx == x1 and yy == y0) or (side == "R" and xx == x0 and yy == y0):
                continue
            for zz in (F0 + 2.4, zs - 0.8):
                mb.box((1.9, 1.9, 0.45), (xx, yy, zz), (0, 0, 0), "Metal_Dark", 0.04)
        pave_poly(mb, [(x0 + t, y0 + t), (x1 - t, y0 + t), (x1 - t, y1 - t), (x0 + t, y1 - t)], F0 + 0.04, rng,
                  tile=3.6, h=0.3, grout=False, m=SF)
        mb.finish()
        # colisao das alas
        A = "Forge"
        if side == "L":
            col_box2(A, (x0, y0, F0), (x0 + 2.0, y0 + t, ze))
            col_box2(A, (x0 + 6.0, y0, F0), (x0 + 8.5, y0 + t, ze))
            col_box2(A, (x0 + 12.5, y0, F0), (x1, y0 + t, ze))
            col_box2(A, (x0 + 2.0, y0, 11.0), (x0 + 6.0, y0 + t, ze))
            col_box2(A, (x0 + 8.5, y0, F0), (x0 + 12.5, y0 + t, 12.5))
            col_box2(A, (x0, y0, F0), (x0 + t, y0 + 7.0, ze + rise))
            col_box2(A, (x0, y0 + 17.0, F0), (x0 + t, y1, ze + rise))
            col_box2(A, (x0, y0 + 7.0, 15.0), (x0 + t, y0 + 17.0, ze + rise))
            col_box2(A, (x1 - t, yi0, F0), (x1, y1, ze))
        else:
            col_box2(A, (x0, y0, F0), (x0 + 9.5, y0 + t, ze))
            col_box2(A, (x0 + 12.5, y0, F0), (x1, y0 + t, ze))
            col_box2(A, (x0 + 9.5, y0, 11.5), (x0 + 12.5, y0 + t, ze))
            col_box2(A, (x1 - t, y0, F0), (x1, y1, ze))
            col_box2(A, (x0, yi0, F0), (x0 + t, y1, ze))
        col_box2(A, (x0, y1 - t, F0), (x1, y1, ze))
        # telhado: caixas inclinadas no caimento (espessura 1), nao um bloco na altura da cumeeira
        k_ = rise / (x1 - x0) if side == "L" else rise / ((x1 - x0) / 2)
        ang = math.atan(k_)
        if side == "L":
            slopes = [(x0 - 0.7, x1 + 1.4, 1.0)]        # desce para +x
        else:
            slopes = [(x0 - 1.4, cx, -1.0), (cx, x1 + 1.4, 1.0)]
        for (xa, xb, sd) in slopes:
            xm = (xa + xb) / 2
            ztop = zroof(xm) + 0.8
            lng = (xb - xa) / math.cos(ang)
            c = Vector((xm, (y0 + y1) / 2, ztop - 0.5 / math.cos(ang)))
            col_box(A, (lng, y1 - y0 + 2.0, 1.0), c, (0, sd * ang, 0))


# ------------------------------------------------------------------ loft + varanda + escada (ala esquerda)
def loft_balcony(rng):
    x0, y0, x1, y1 = L.FORGE_WING_L
    mb = FB("FORGE_Loft_Balcony", C, rng, detail="near")
    zl = 12.5
    mb.box2((x0 + 1.6, y0 + 1.6, zl - 0.6), (x1, y0 + 12.0, zl), "Wood_Plank", 0.08)
    for yy in (y0 + 4, y0 + 8, y0 + 12):
        mb.box2((x0 + 1.6, yy - 0.5, zl - 1.4), (x1, yy + 0.5, zl - 0.6), "Wood_Dark", 0.08)
    for xx in (x0 + 7.0,):
        mb.box((1.0, 1.0, zl - F0), (xx, y0 + 12.0, (F0 + zl) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    fence(mb, "ForgeLoft", [(x0 + 1.8, y0 + 12.2, zl), (x1 - 0.2, y0 + 12.2, zl)], h=2.8, post_step=3.0,
          rail_m="Wood_Plank")
    for i in range(5):
        crate(mb, (x0 + 3 + (i % 3) * 3.0, y0 + 9.5 - (i // 3) * 3.0, zl), 2.2, rng.uniform(-0.2, 0.2), rng)
    barrel(mb, (x1 - 2.5, y0 + 9.0, zl))
    barrel(mb, (x1 - 2.5, y0 + 6.0, zl))
    by0 = y0 - 6.0
    mb.box2((x0 + 0.5, by0, zl - 0.6), (x1 - 0.5, y0, zl), "Wood_Plank", 0.08)
    for xx in (x0 + 1.2, x1 - 1.2):
        for yy in (by0 + 0.7,):
            mb.box((1.0, 1.0, zl - F0), (xx, yy, (F0 + zl) / 2), (0, 0, 0), "Wood_Dark", 0.1)
            mb.beam((xx, yy, zl - 3.5), (xx, y0 - 0.1, zl - 0.8), 0.6, 0.6, "Wood_Dark", 0.05)
    fence(mb, "ForgeLoft", [(x0 + 0.8, y0 - 0.2, zl), (x0 + 0.8, by0 + 0.4, zl), (x1 - 6.8, by0 + 0.4, zl)],
          h=2.8, post_step=3.0, rail_m="Wood_Plank")
    fence(mb, "ForgeLoft", [(x1 - 0.8, by0 + 0.4, zl), (x1 - 0.8, y0 - 0.2, zl)], h=2.8, post_step=3.0,
          rail_m="Wood_Plank")
    mb.box2((x0 + 3.0, y0 - 0.6, zl + 1.0), (x0 + 10.0, y0 - 0.1, zl + 5.4), "Wood_Dark", 0.15)
    mb.box2((x0 + 3.5, y0 - 0.8, zl + 1.4), (x0 + 9.5, y0 - 0.5, zl + 5.0), "Cloth_Navy", 0.02)
    marker("LEADERBOARD_Balcony", (x0 + 6.5, y0 - 0.9, zl + 3.2), (0, 0, 0), 2, "SINGLE_ARROW")
    sx = x1 - 3.8
    stairs(mb, "ForgeLoft", (sx, by0 - 9 * 1.5, F0), D(90), 5.0, 9, (zl - F0) / 9, 1.5, "Wood_Plank", "Wood_Dark")
    mb.finish()
    A = "ForgeLoft"
    col_box2(A, (x0 + 1.6, y0 + 1.6, zl - 1.4), (x1 - 1.6, y0 + 12.0, zl))
    col_box2(A, (x0 + 0.5, by0, zl - 1.0), (x1 - 0.5, y0, zl))
    marker("DOOR_Loft", (x0 + 4.0, y0, zl), (0, 0, 0), 1.5)


# ------------------------------------------------------------------ balcao de venda (frente da ala direita)
def stall(rng):
    x0, y0, x1, y1 = L.FORGE_WING_R
    mb = FB("FORGE_Counter_Stall", C, rng, detail="near")
    sy0 = y0 - 6.0
    for xx in (x0 + 1.0, (x0 + x1) / 2, x1 - 1.0):
        mb.box((0.9, 0.9, 10.0 - F0), (xx, sy0 + 0.5, (F0 + 10.0) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    mb.beam((x0 + 0.4, sy0 + 0.5, 10.0), (x1 - 0.4, sy0 + 0.5, 10.0), 0.9, 1.0, "Wood_Dark", 0.08)
    ang = math.atan2(3.0, 6.0)
    for i in range(6):
        yy = sy0 - 0.8 + i * 1.3
        zz = 10.0 + (yy - sy0 + 0.8) * 3.0 / 7.4 + 0.5
        mb.box((x1 - x0 + 1.6, 1.5, 0.45), (((x0 + x1) / 2), yy, zz), (-ang, 0, 0), "Roof_Red" if i % 2 else "Cloth_Red",
               0.08)
    mb.box2((x0 + 1.5, sy0 + 1.0, F0), (x1 - 4.5, sy0 + 2.4, F0 + 3.0), "Wood_Plank", 0.1)
    mb.box2((x0 + 1.2, sy0 + 0.8, F0 + 3.0), (x1 - 4.2, sy0 + 2.7, F0 + 3.4), "Wood_Plank", 0.1)
    for zz in (F0 + 2.5, F0 + 4.6, F0 + 6.7):
        mb.box2((x0 + 1.0, y0 - 1.1, zz), (x1 - 5.0, y0 - 0.1, zz + 0.3), "Wood_Plank", 0.05)
        for k in range(5):   # 5 itens: o 6o ficava fora da prateleira (x=29.5)
            xx = x0 + 2.0 + k * 1.5
            if (k + int(zz)) % 3 == 0:
                mb.box((1.0, 0.6, 0.45), (xx, y0 - 0.6, zz + 0.52), (0, 0, 0), "Metal_Brass", 0.06)
            elif (k + int(zz)) % 3 == 1:
                crystal_cluster(mb, (xx, y0 - 0.6, zz + 0.3), 0.3, "Crystal_Blue" if k % 2 else "Crystal_Purple",
                                rng, 3)
            else:
                mb.cyl(0.32, 0.9, (xx, y0 - 0.6, zz + 0.75), (0, 0, 0), "Crystal_Purple", 8, r2=0.2, bevel=0.0)
    mb.box((1.4, 0.8, 0.5), (x0 + 3.0, sy0 + 1.7, F0 + 3.65), (0, 0, 0.2), "Metal_Brass", 0.06)
    crystal_cluster(mb, (x0 + 6.0, sy0 + 1.7, F0 + 3.4), 0.35, "Crystal_Blue", rng, 4)
    hanging_lantern(mb, (x0 + 4.0, sy0 + 0.5, 9.5), name="L_Stall_A", chain=1.0)
    hanging_lantern(mb, (x1 - 4.0, sy0 + 0.5, 9.5), name="L_Stall_B", chain=1.0)
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


# ------------------------------------------------------------------ fole em cunha sanfonada (xz_prism)
def wedge_bellows(mb, x_hinge, x_far, yc, zb, h0, h1, width, rng, top_mb=None):
    """fole: tabua de baixo fixa, couro em cunha com dobras (vincos) e tampo articulado na ponta do bocal.
    O tampo + couro podem ir para outro objeto (top_mb) para o vfx animar."""
    tm = top_mb or mb
    sd = 1.0 if x_far > x_hinge else -1.0
    xa, xb = min(x_hinge, x_far), max(x_hinge, x_far)
    mb.box2((xa, yc - width / 2, zb - 0.5), (xb, yc + width / 2, zb), "Wood_Plank", 0.08)
    ph = h0 if sd > 0 else h1
    pf = h1 if sd > 0 else h0
    xz_prism(tm, [(xa, zb), (xb, zb), (xb, zb + pf), (xa, zb + ph)], yc - width / 2 + 0.2, yc + width / 2 - 0.2,
             "Leather_Bellows")
    for k in range(1, 4):
        f = k / 4
        for s in (-1, 1):
            tm.beam((xa + 0.3, yc + s * (width / 2 - 0.1), zb + ph * f), (xb - 0.05, yc + s * (width / 2 - 0.1), zb + pf * f),
                    0.36, 0.28, "Leather", 0.0)
        xe = x_far
        tm.beam((xe, yc - width / 2 + 0.1, zb + h1 * f), (xe, yc + width / 2 - 0.1, zb + h1 * f), 0.36, 0.28, "Leather",
                0.0)
    lift = math.atan2(h1 - h0, xb - xa)
    tm.beam((x_hinge, yc, zb + h0 + 0.2), (x_far + sd * 0.2, yc, zb + h1 + 0.2), width + 0.1, 0.4, "Wood_Plank", 0.06)
    for f in (0.3, 0.6, 0.9):
        x = x_hinge + (x_far - x_hinge) * f
        zz = zb + h0 + (h1 - h0) * f + 0.43
        tm.box((0.35, width + 0.2, 0.18), (x, yc, zz), (0, -sd * lift, 0), "Metal_Dark", 0.0)
    return Vector((x_hinge, yc, zb + h0 + 0.2))


# ------------------------------------------------------------------ interior do salao e da ala direita (foles)
def interior(rng):
    x0, y0, x1, y1 = L.FORGE_HALL
    ze_hall = 24.0
    mb = FB("FORGE_Interior_Props", C, rng, detail="near")
    for sx in (-1, 1):
        bx = sx * 15.2
        mb.box2((bx - 2.0, 16.0, FL), (bx + 2.0, 19.6, FL + 3.0), "Wood_Plank", 0.1)
        mb.box2((bx - 2.3, 15.8, FL + 3.0), (bx + 2.3, 19.8, FL + 3.4), "Wood_Plank", 0.1)
        mb.box2((bx - 3.0, y1 - 2.5, FL + 5.0), (bx + 3.0, y1 - 2.2, FL + 8.5), "Wood_Dark", 0.05)
        for k in range(5):
            xx = bx - 2.4 + k * 1.2
            mb.beam((xx, y1 - 2.6, FL + 8.0), (xx, y1 - 2.6, FL + 5.4), 0.25, 0.25, "Wood_Plank", 0.0)
            mb.box((0.9, 0.5, 0.5), (xx, y1 - 2.6, FL + 5.2), (0, 0, 0), "Metal_Dark", 0.05)
    # tanque de tempera
    mb.box2((-11.5, 7.0, FL), (-6.5, 9.4, FL + 2.4), "Wood_Plank", 0.1)
    mb.box2((-11.1, 7.4, FL + 2.0), (-6.9, 9.0, FL + 2.3), "Water", 0.0)
    for x in (-11.5, -6.5):
        mb.box((0.3, 2.6, 0.4), (x, 8.2, FL + 1.8), (0, 0, 0), "Metal_Dark", 0.03)
    # rebolo: armacao de madeira em cavalete, eixo de ferro, manivela e cocho d'agua embaixo
    gx, gy, gz = 8.5, 8.2, FL + 3.0
    mb.cyl(1.6, 0.6, (gx, gy, gz), (0, D(90), 0), "Stone_Light", 14, bevel=0.1)
    mb.rod((gx - 1.9, gy, gz), (gx + 1.9, gy, gz), 0.16, "Metal_Iron", 8)
    for sx in (-1, 1):
        px = gx + sx * 1.4
        for sy in (-1, 1):
            mb.beam((px, gy + sy * 1.2, FL), (px, gy, gz - 0.2), 0.3, 0.3, "Wood_Dark", 0.0)
        mb.box((0.5, 0.5, 0.5), (px, gy, gz), (0, 0, 0), "Wood_Dark", 0.0)
    mb.beam((gx + 1.9, gy, gz), (gx + 1.9, gy, gz - 1.0), 0.18, 0.18, "Metal_Dark", 0.0)
    mb.rod((gx + 1.9, gy, gz - 1.0), (gx + 2.5, gy, gz - 1.0), 0.14, "Wood_Plank", 6)
    mb.box2((gx - 1.0, gy - 0.9, FL), (gx + 1.0, gy + 0.9, FL + 1.3), "Wood_Plank", 0.05)
    mb.box2((gx - 0.8, gy - 0.7, FL + 1.1), (gx + 0.8, gy + 0.7, FL + 1.25), "Water", 0.0)
    # estacao junto a lareira (por dentro): suporte de tenazes e prateleira de laminas na parede frontal
    sy = y0 + 2.4
    mb.box2((2.0, sy, FL + 3.8), (7.0, sy + 0.3, FL + 7.6), "Wood_Dark", 0.03)
    for k in range(4):
        xx = 2.6 + k * 1.2
        mb.beam((xx, sy + 0.45, FL + 7.2), (xx - 0.15, sy + 0.45, FL + 4.0), 0.14, 0.14, "Metal_Dark", 0.0)
        mb.beam((xx + 0.2, sy + 0.45, FL + 7.2), (xx + 0.35, sy + 0.45, FL + 4.2), 0.14, 0.14, "Metal_Dark", 0.0)
    mb.box2((2.0, sy, FL + 2.3), (7.0, sy + 1.0, FL + 2.6), "Wood_Plank", 0.03)
    for k in range(3):
        mb.box((1.6, 0.35, 0.08), (2.9 + k * 1.6, sy + 0.55, FL + 2.66), (0, 0, 0.1), "Metal_Iron", 0.0)
    for k in range(4):
        xx = 9.5 + k * 1.5
        mb.beam((xx, 20.4, FL), (xx, 20.4, FL + 4.2), 0.25, 0.3, "Wood_Plank", 0.0)
        mb.box((2.2, 0.35, 0.6), (xx, 20.2, FL + 4.2), (0, 0, D(90)), "Metal_Iron", 0.05)
    for p in ((-6.5, 18.8), (-8.8, 18.8), (6.5, 18.8)):
        barrel(mb, (p[0], p[1], FL), 1.0, 2.4)
    for i in range(3):
        crate(mb, (-17.0 + i * 0.4, 8.0 + i * 2.6, FL), 2.0, rng.uniform(-0.2, 0.2), rng)
    for yy in (9.0, 16.0):
        hanging_lantern(mb, (-7.0, yy, 23.6), name="L_Hall_%d_A" % int(yy), chain=6.0)
        hanging_lantern(mb, (7.0, yy, 23.6), name="L_Hall_%d_B" % int(yy), chain=6.0)
    light("L_Hall_Fill", "POINT", (0, 13.0, 16.0), 650, (1.0, 0.62, 0.38), 4.0)
    mb.box((1.2, 1.2, 1.0), (4.0, 13.0, ze_hall - 1.4), (0, 0, 0), "Metal_Dark", 0.06)
    mb.cyl(0.55, 0.5, (4.0, 13.0, ze_hall - 2.3), (D(90), 0, 0), "Metal_Dark", 10, bevel=0.0)
    hanging_chain(mb, (4.0, 13.0, ze_hall - 2.6), 7.2, link=0.9)
    mb.box((1.8, 0.7, 0.6), (4.35, 13.0, ze_hall - 11.3), (0, 0, 0.2), "Ember_Glow", 0.06)
    for k in range(4):
        mb.box((1.3, 0.5, 0.35), (15.2 - 1.2 + k * 0.8, 17.8, FL + 3.6), (0, 0, 0.15 * (k % 2)),
               "Ember_Glow" if k in (1, 2) else "Metal_Dark", 0.04)
    mb.finish()
    A = "ForgeInt"
    for sx in (-1, 1):
        col_box2(A, (sx * 15.2 - 2.3, 15.8, FL), (sx * 15.2 + 2.3, 19.8, FL + 3.4))
    col_box2(A, (-11.5, 7.0, FL), (-6.5, 9.4, FL + 2.4))
    col_box2(A, (6.6, 6.8, FL), (10.6, 9.6, FL + 4.6))

    # ---- ala direita: eixo da roda, came, fole em cunha, duto pelo patio ate a casa da fornalha
    wx0, wy0, wx1, wy1 = L.FORGE_WING_R
    m2 = FB("FORGE_Bellows_Machinery", C, rng, detail="near")
    az = 15.5
    ay = L.WHEEL_C[1]
    m2.rod((wx1 + 0.5, ay, az), (wx0 + 6.0, ay, az), 0.55, "Wood_Dark", 10)
    for xx in (wx1 - 3.0, wx0 + 8.5):
        m2.box((1.4, 1.2, az - F0), (xx, ay, (F0 + az) / 2 - 0.4), (0, 0, 0), "Wood_Dark", 0.1)
        m2.box((1.8, 1.8, 1.0), (xx, ay, az - 0.5), (0, 0, 0), "Metal_Iron", 0.08)
    m2.cyl(2.2, 0.9, (wx0 + 6.0, ay, az), (0, D(90), 0), "Metal_Iron", 16, bevel=0.1)
    for i in range(16):
        a = i / 16 * math.tau
        m2.box((0.9, 0.6, 0.6), (wx0 + 6.0, ay + math.cos(a) * 2.35, az + math.sin(a) * 2.35), (a, 0, 0), "Metal_Dark",
               0.0)
    bx, by = wx0 + 6.5, ay + 7.0
    hinge = wedge_bellows(m2, bx - 2.6, bx + 2.6, by, F0 + 1.9, 0.5, 2.9, 3.0, rng)
    m2.box2((bx - 2.9, by - 1.7, F0), (bx + 2.9, by + 1.7, F0 + 1.4), SFD, 0.12)
    m2.beam((wx0 + 5.4, ay + 1.6, az - 1.2), (bx + 2.2, by, F0 + 1.9 + 2.9 + 0.5), 0.45, 0.45, "Wood_Dark", 0.0)
    m2.cyl(0.7, 1.0, (bx - 3.1, by, F0 + 2.3), (0, D(90), 0), "Metal_Brass", 10, r2=0.45, bevel=0.0)
    cx, cy = L.CHIMNEY
    pts = [(bx - 3.6, by, F0 + 2.3), (wx0 - 0.2, by, F0 + 3.3), (16.5, 27.4, 10.4), (13.25, 28.0, 10.4)]
    pipe(m2, pts, r=0.9)
    import fm_forge_tower as T
    boss(m2, (T.HX + 0.2, 28.0, 10.4), (1, 0, 0), 2.6)
    light("L_WingR", "POINT", (wx0 + 7, ay + 2, 13.0), 250, (1.0, 0.65, 0.35), 0.5)
    m2.finish()
    col_box("ForgeInt", (2.0, 12.0, 3.0), ((wx0 + wx1) / 2 + 1, ay, az), (0, 0, D(90)))
    col_box2("ForgeInt", (bx - 3.6, by - 1.8, F0), (bx + 2.9, by + 1.8, F0 + 5.6))
    col_box2("ForgeInt", (wx0 + 4.6, ay - 1.0, F0), (wx0 + 9.4, ay + 7.0, 10.0))
    col_box2("ForgeInt", (wx1 - 3.8, ay - 0.7, F0), (wx1 - 2.2, ay + 0.7, az))
    col_box2("ForgeInt", (T.HX, 26.2, F0), (wx0, 29.6, 11.6))

    # ---- ala esquerda: fim do trilho, tremonha e calha de minerio ate a boca da casa da fornalha
    lx0, ly0, lx1, ly1 = L.FORGE_WING_L
    m3 = FB("FORGE_OreIntake", C, rng, detail="near")
    hx, hy = lx0 + 10.5, ly0 + 12.0
    for sx in (-1, 1):
        for sy in (-1, 1):
            m3.box((0.9, 0.9, 7.0), (hx + sx * 2.4, hy + sy * 1.8, F0 + 3.5), (0, 0, 0), "Wood_Dark", 0.1)
    m3.cyl(3.6, 3.0, (hx, hy, F0 + 8.5), (0, 0, D(45)), "Wood_Plank", 4, r2=1.6, bevel=0.1)
    crystal_cluster(m3, (hx, hy, F0 + 9.6), 0.6, "Crystal_Blue", rng, 6)
    # calha coberta em dois trechos: sai da tremonha para o norte e cruza o patio ate a boca na parede oeste
    segs = [(Vector((hx + 0.9, hy + 1.4, F0 + 7.2)), Vector((hx + 1.6, hy + 5.2, F0 + 8.2))),
            (Vector((hx + 1.6, hy + 5.2, F0 + 8.2)), Vector((-13.3, 28.0, 15.2)))]
    for a, b in segs:
        m3.beam(a, b, 2.2, 0.4, "Wood_Plank", 0.05)
        for s in (-1, 1):
            d = (b - a).normalized()
            side = Vector((-d.y, d.x, 0)).normalized() * 1.1 * s
            m3.beam(a + side + Vector((0, 0, 0.6)), b + side + Vector((0, 0, 0.6)), 0.3, 1.2, "Wood_Dark", 0.0)
        m3.beam(a + Vector((0, 0, 1.4)), b + Vector((0, 0, 1.4)), 2.6, 0.3, "Wood_Dark", 0.0)
    a, b = segs[1]
    mid = a + (b - a) * 0.55
    m3.box((1.0, 1.0, mid.z - F0), (mid.x, mid.y, (F0 + mid.z) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    for f in (0.3, 0.8):
        q = a + (b - a) * f
        m3.beam((q.x, q.y - 1.3, q.z + 0.9), (q.x, q.y + 1.3, q.z + 0.9), 0.25, 0.25, "Metal_Dark", 0.0)
    for k in range(2):
        yy = ly0 + 20.0 + k * 4.6
        m3.box2((lx0 + 1.8, yy - 2.0, F0), (lx0 + 6.5, yy + 2.0, F0 + 2.2), "Wood_Plank", 0.08)
        crystal_cluster(m3, (lx0 + 4.2, yy, F0 + 2.0), 0.55, "Crystal_Blue", rng, 5)
    hanging_lantern(m3, (lx0 + 7.0, ly0 + 18.0, 16.6), name="L_WingL_A", chain=3.0)
    m3.finish()
    col_box2("ForgeInt", (hx - 3.0, hy - 2.4, F0), (hx + 3.0, hy + 2.4, F0 + 10.0))
    col_box2("ForgeInt", (lx0 + 1.8, ly0 + 18.0, F0), (lx0 + 6.5, ly0 + 26.6, F0 + 2.2))
    col_box2("ForgeInt", (mid.x - 0.6, mid.y - 0.6, F0), (mid.x + 0.6, mid.y + 0.6, mid.z))


# ------------------------------------------------------------------ bigorna + Ignis + marcadores
def anvil_and_ignis(rng):
    ax, ay = L.ANVIL
    mb = FB("FORGE_Anvil", C, rng, detail="hero")
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

    ix, iy = L.IGNIS
    s = 1.35
    ig = FB("NPC_Ignis_Model", C, rng, detail="hero")
    F = Frame(ix, iy, FL, D(180))
    for sx in (-0.5, 0.5):
        ig.box((0.95 * s, 0.95 * s, 2.0 * s), F.p(sx * s, 0, 1.0 * s), F.r(), "Cloth_Navy", 0.1)
        ig.box((1.05 * s, 1.2 * s, 0.5 * s), F.p(sx * s, -0.1 * s, 0.25 * s), F.r(), "Leather", 0.08)
    ig.box((2.2 * s, 1.15 * s, 2.1 * s), F.p(0, 0, 3.05 * s), F.r(), "Wood_Plank", 0.12)
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
    hp = F.p(1.6 * s, 0.9 * s, 3.2 * s)
    ig.beam(hp, hp + Vector((0.4, -0.9, 2.4)) * s, 0.3 * s, 0.3 * s, "Wood_Plank", 0.02)
    ig.box((1.6 * s, 0.8 * s, 0.8 * s), hp + Vector((0.45, -1.0, 2.6)) * s, (0, 0, 0), "Metal_Dark", 0.08)
    ig.finish()
    col_box("ForgeNPC", (3.4, 2.0, 7.0), (ix, iy, FL + 3.5))
    marker("NPC_Ignis", (ix, iy, FL), (0, 0, D(180)), 3, "ARROWS", props={"npc": "Ignis", "scale": 1.35})
    marker("INTERACT_Ignis", (ax, ay, FL + 3.8), (0, 0, 0), 2, "SPHERE", props={"prompt_range": 18})
    px, py = L.PLAYER_IGNIS
    marker("PLAYER_INTERACT_Ignis", (px, py, F0 + 0.3), (0, 0, 0), 3, "CIRCLE",
           props={"note": "area livre r=8 na praca para varios jogadores"})
    # o fogo da boca e a luz principal da fachada (unica com sombra no Roblox): laranja, banha tablado e praca
    light("L_Hearth_Fire", "POINT", (0, -3.0, FL + 4.0), 1500, (1.0, 0.45, 0.12), 2.0)
    light("L_Hearth_Spill", "SPOT", (0, -3.0, 13.0), 1600, (1.0, 0.5, 0.2), 1.5, rot=(D(35), 0, D(180)))
    # marcadores para o vfx
    marker("VFX_Hearth_Fire", (0.0, 1.4, FL + 2.7), (0, 0, 0), 2,
           props={"particle": "fire", "size": [10.0, 4.6, 5.3],
                  "note": "centro do leito de brasas da boca; size = largura x profundidade x altura das chamas"})
    marker("VFX_Anvil_Sparks", (ax + 0.5, ay, FL + 3.9), (0, 0, 0), 1.5,
           props={"particle": "sparks", "note": "faiscas a cada martelada do Ignis (topo da bigorna)"})


def _join(name, parts):
    """junta objetos (mesma area) num so: menos MeshParts no Roblox (1 por material por objeto)"""
    import bpy
    obs = [bpy.data.objects.get(n) for n in parts]
    obs = [o for o in obs if o is not None]
    if not obs:
        return None
    base = obs[0]
    if len(obs) > 1:
        vl = bpy.context.view_layer
        vl.update()                      # sincroniza as bases (objetos recem-criados) antes de selecionar
        for o in vl.objects:
            if o is not None:
                o.select_set(False)
        for o in obs:
            o.select_set(True)
        vl.objects.active = base
        with bpy.context.temp_override(active_object=base, object=base, selected_objects=obs,
                                       selected_editable_objects=obs):
            bpy.ops.object.join()
        base.select_set(False)
    base.name = name
    base.data.name = name
    return base


def build():
    rng = random.Random(404)
    foundation(rng)
    hall(rng)
    hearth(rng)
    import fm_forge_tower
    fm_forge_tower.build(random.Random(406))
    wings(rng)
    loft_balcony(rng)
    stall(rng)
    interior(rng)
    anvil_and_ignis(rng)
    import fm_forge_annex
    fm_forge_annex.build(random.Random(405))
    # agrupamento por area (a pegada xy de cada grupo continua compacta: vegetacao/props respeitam)
    _join("FORGE_Chimney_Tower", ["FORGE_Chimney_Tower", "FORGE_Furnace_Interior", "FORGE_Pipes_Big"])
    _join("FORGE_Hall", ["FORGE_Hall_Walls", "FORGE_Hall_Roof", "FORGE_Banners", "FORGE_Interior_Props",
                         "FORGE_Foundation_Dais"])
    _join("FORGE_Hearth", ["FORGE_Hearth", "FORGE_Facade_Props"])
    _join("FORGE_Wing_L", ["FORGE_Wing_L", "FORGE_Loft_Balcony", "FORGE_OreIntake", "FORGE_Ore_Crane",
                           "FORGE_Roof_Vents_L", "FORGE_Coal_Shed"])
    _join("FORGE_Wing_R", ["FORGE_Wing_R", "FORGE_Counter_Stall", "FORGE_Bellows_Machinery", "FORGE_Vent_Tower",
                           "FORGE_Roof_Vents_R", "FORGE_Wall_Gears", "FORGE_Bellows_House", "FORGE_Pipes_Air"])
    _join("FORGE_Yard_W", ["FORGE_Ore_Lift", "FORGE_Ore_Unload"])
