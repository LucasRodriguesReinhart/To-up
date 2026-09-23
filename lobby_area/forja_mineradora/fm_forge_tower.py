# fm_forge_tower - ALTO-FORNO da Forja do Ignis (passe fabrica): casa da fornalha em alvenaria que abraca a base
# da torre (os telhados do salao morrem nela), fuste atarracado r~12 sobre talude, 2 cintas de ferro grossas +
# cinta da casa, duas fendas altas arqueadas incandescentes para a praca, coroa de alto-forno (anel de chapas com
# 4 bocas arqueadas + 8 pequenas, labio incandescente continuo, dentes de ferro, luz interna), fumeiro da lareira,
# tubos laterais descendo para o telhado do salao e o interior da fornalha (grelha, cadinho, ventaneira, lingoteira).
import math
from mathutils import Vector
from fm_lib import D, col_box, col_box2, light, marker
from fm_parts import masonry_wall, arch, pave_poly
from fm_forge_kit import (FB, xz_prism, rivet, big_pipe, gate_valve, boss, rufo, chain_links, tube_pt, flange, Z,
                          wing_roof_z, WING_RISE_R)
import fm_layout as L

C = "03_FORGE"
F0 = L.FLOOR
FL = L.FL
SF, SFD = "Stone_Forge", "Stone_Forge_Dark"
CX, CY = L.CHIMNEY
TOP = L.CHIMNEY_TOP
# casa da fornalha: frente = trecho central da parede de fundo do salao (y 19.8..22), laterais x=+-12 (t 2),
# fundo y=39 (t 2); alvenaria ate HZ, deque em 33, parapeito com capa ate HZ+0.7
HX = 13.0
HY0, HY1 = 19.8, 40.0
HZ = 34.0
ZDECK = 33.0
# fuste: talude 33 -> 36.6 (r 10.4 -> 11.95), cinta 1, alvenaria 38.6 -> 60.4 (r 11.9 -> 11.4), cinta 2, coroa
ZT0, ZT1 = ZDECK, 36.6
ZS0, ZS1 = 38.6, 60.4
RS0, RS1 = 11.9, 11.4
ZC0, ZC1 = 63.2, 72.2          # anel da coroa (9 de altura)
RC = 12.55                     # raio medio das chapas da coroa (R + 2.5)
SLIT = (1.3, 45.0, 55.3)       # meia-largura, peitoril, nascenca do arco das fendas altas


def ro(z):
    """raio externo do fuste na cota z"""
    if z <= ZS0:
        return RS0
    return RS0 - (RS0 - RS1) * min(1.0, (z - ZS0) / (ZS1 - ZS0))


def tpt(a, r, z):
    return Vector((CX + math.cos(a) * r, CY + math.sin(a) * r, z))


# ------------------------------------------------------------------ anel de alvenaria (recorte fino nos vaos)
def ring_core(mb, z0, z1, rfn, thick, m, gaps=(), n=24):
    """nucleo sem tampas no meio da espessura do anel (sem frestas para o ceu / sem vazar luz no Roblox).
    gaps (mesmo formato do ring_wall) abrem o nucleo nas passagens (arco da fornalha); faixas em z nos limites."""
    rc = lambda z: rfn(z) - thick / 2
    cuts = [z0, z1] + [min(max(zz, z0), z1) for g in gaps for zz in (g[2], g[3])]
    zs = sorted(set(round(z, 3) for z in cuts))
    for za, zb in zip(zs, zs[1:]):
        if zb - za < 0.05:
            continue
        zm = (za + zb) / 2
        for i in range(n):
            a0, a1 = math.tau * i / n, math.tau * (i + 1) / n
            am = (a0 + a1) / 2
            r_m = rc(zm)
            if any(g[2] <= zm <= g[3] and abs(((am - D(g[0]) + math.pi) % math.tau) - math.pi) * r_m <
                   g[1] + (a1 - a0) / 2 * r_m for g in gaps):
                continue
            p = [Vector((CX + math.cos(a) * rc(z), CY + math.sin(a) * rc(z), z))
                 for (a, z) in ((a0, za), (a1, za), (a1, zb), (a0, zb))]
            mb.quad(p[0], p[1], p[2], p[3], m)


def ring_wall(mb, z0, z1, rfn, thick, rng, course=2.6, blk=4.4, gaps=(), m=SF, m2=SFD, mix=0.1, base_m=None,
              bevel=0.14, skip=None, core_m=None, core_gaps=False):
    """anel de blocos com raio externo rfn(z). gaps = [(ang_graus, meia_largura, zlo, zhi, arco)] recortam os
    blocos na borda do vao (arco = altura da zona em que o vao estreita em elipse). Fiada de base em base_m.
    core_m: nucleo sem tampas no meio da espessura (ring_core); core_gaps=True tambem abre o nucleo nos vaos
    (passagens); False = o nucleo fica atras dos vaos como fundo (fendas com brilho recuado)."""
    z = z0
    row = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        if z1 - (z + h) < 0.7:
            h = z1 - z
        r_o = rfn(z + h / 2)
        rm = r_o - thick / 2
        n = max(8, int(round(math.tau * rm / blk)))
        off = (0.5 if row % 2 else 0.0) + rng.uniform(-0.08, 0.08)
        for i in range(n):
            spans = [((i + off) / n * math.tau, (i + 1 + off) / n * math.tau)]
            for (gc, ghw, zl, zh, rise) in gaps:
                if z + h <= zl + 0.01 or z >= zh - 0.01:
                    continue
                hw = ghw
                if rise > 0 and z + h > zh - rise:
                    t = min(1.0, max(0.0, (z + h * 0.5 - (zh - rise)) / rise))
                    hw = ghw * math.sqrt(max(0.0, 1 - t * t))
                    if hw < 0.2:
                        continue
                ga = hw / rm
                new = []
                for (sa, sb) in spans:
                    cc = D(gc) + math.tau * round(((sa + sb) / 2 - D(gc)) / math.tau)
                    lo, hi = cc - ga, cc + ga
                    if hi <= sa or lo >= sb:
                        new.append((sa, sb))
                        continue
                    if lo > sa:
                        new.append((sa, lo))
                    if hi < sb:
                        new.append((hi, sb))
                spans = new
            for (sa, sb) in spans:
                if (sb - sa) * rm < 0.45:
                    continue
                am = (sa + sb) / 2
                c = Vector((CX + math.cos(am) * rm, CY + math.sin(am) * rm, z + h / 2))
                if skip and skip(c):
                    continue
                chord = 2 * r_o * math.sin((sb - sa) / 2) - 0.14
                mm = base_m if (row == 0 and base_m) else (m2 if rng.random() < mix else m)
                mb.box((thick + rng.uniform(-0.04, 0.12), chord, h - 0.1), c, (0, 0, am), mm, bevel)
        z += h
        row += 1
    if core_m:
        ring_core(mb, z0 + 0.05, z1 - 0.05, rfn, thick, core_m, gaps if core_gaps else ())


# ------------------------------------------------------------------ fenda alta arqueada com grade
def tall_slit(mb, ang_deg, rng):
    a = D(ang_deg)
    e = Vector((math.cos(a), math.sin(a), 0.0))
    t = Vector((-math.sin(a), math.cos(a), 0.0))
    hw, z0, zsp = SLIT
    zm = (z0 + zsp + hw) / 2
    r_o = ro(zm)
    rc = r_o - 0.9                       # nucleo
    c0 = Vector((CX, CY, 0.0)) + e * r_o
    # brilho recuado em degrade (fica por fora do nucleo, dentro do vao): laranja vivo embaixo, rubro no alto
    zc_ = z0 + (zsp - z0) * 0.55
    for (za, zb, m) in ((z0 - 0.2, zc_, "Fire_Glow_Mid"), (zc_, zsp + hw + 0.2, "Ember_Glow")):
        mb.box((0.3, hw * 2 + 0.3, zb - za), Vector((CX, CY, (za + zb) / 2)) + e * (rc + 0.2), (0, 0, a), m, 0.0)
    # grade de ferro: barras verticais juntas + 2 travessas (le respiro de fornalha, nao caixilho de janela)
    zg = zsp + hw * 0.75
    for k in (-0.93, -0.31, 0.31, 0.93):
        mb.box((0.3, 0.24, zg - z0), c0 - e * 0.35 + t * k + Z * ((z0 + zg) / 2), (0, 0, a), "Metal_Dark", 0.0)
    for zz in (z0 + 4.6, zsp):
        mb.box((0.34, hw * 2, 0.3), c0 - e * 0.35 + Z * zz, (0, 0, a), "Metal_Dark", 0.0)
    # moldura de ferro rebitada (ombreiras + arco) e peitoril de pedra escura
    mb.box((2.3, hw * 2 + 1.6, 0.8), c0 - e * 0.75 + Z * (z0 - 0.4), (0, 0, a), SFD, 0.1)
    for s in (-1, 1):
        mb.box((0.5, 0.9, zsp - z0 + 0.1), c0 - e * 0.1 + t * s * (hw + 0.45) + Z * ((z0 + zsp) / 2), (0, 0, a),
               "Metal_Dark", 0.0)
        for zz in (z0 + 1.2, z0 + 4.6, zsp - 1.0):
            rivet(mb, c0 + e * 0.15 + t * s * (hw + 0.45) + Z * zz, e, 0.24, "Metal_Iron", 0.14)
    n = 5
    rr = hw + 0.45
    for i in range(n):
        t0, t1 = math.pi * i / n, math.pi * (i + 1) / n
        tm = (t0 + t1) / 2
        p = c0 - e * 0.1 + t * (math.cos(tm) * rr) + Z * (zsp + math.sin(tm) * rr)
        ln = 2 * rr * math.sin((t1 - t0) / 2) + 0.12
        mb.box((0.5, ln, 0.9), p, (tm - math.pi / 2, 0, a), "Metal_Dark", 0.0)


# ------------------------------------------------------------------ coroa de alto-forno
def crown(mb, rng):
    half = RC * math.sin(math.pi / 24)
    th = 0.72
    nseg = 24
    rust_k = {1, 5, 9, 13, 17, 19, 23}
    for k in range(nseg):
        a = D(15.0 * k)
        tang = a + math.pi / 2
        org = (CX + math.cos(a) * RC, CY + math.sin(a) * RC)
        kind = "big" if k % 6 == 0 else ("small" if k % 2 == 0 else "plain")
        if kind == "plain":
            xz_prism(mb, [(-half, ZC0), (half, ZC0), (half, ZC1), (-half, ZC1)], -th / 2, th / 2, "Metal_Dark", tang,
                     org)
        else:
            ow, zs, zsp = (1.2, ZC0 + 0.8, ZC0 + 4.4) if kind == "big" else (0.6, ZC0 + 2.8, ZC0 + 4.7)
            xz_prism(mb, [(-half, ZC0), (half, ZC0), (half, zs), (-half, zs)], -th / 2, th / 2, "Metal_Dark", tang, org)
            # moldura em U invertido: sobe pela ombreira esquerda, arco, desce pela direita (poligono concavo simples)
            poly = [(-half, zs), (-ow, zs), (-ow, zsp)] + [(math.cos(math.pi - math.pi * i / 6) * ow,
                                                            zsp + math.sin(math.pi - math.pi * i / 6) * ow)
                                                           for i in range(1, 6)] + \
                   [(ow, zsp), (ow, zs), (half, zs), (half, ZC1), (-half, ZC1)]
            xz_prism(mb, poly, -th / 2, th / 2, "Metal_Dark", tang, org)
            if kind == "big":
                # sobrancelha de ferro sobre a boca grande
                for i in range(4):
                    t0, t1 = math.pi * i / 4, math.pi * (i + 1) / 4
                    p0 = (math.cos(t0) * (ow + 0.3), zsp + math.sin(t0) * (ow + 0.3))
                    p1 = (math.cos(t1) * (ow + 0.3), zsp + math.sin(t1) * (ow + 0.3))
                    q0 = Vector((org[0], org[1], 0)) + Vector((math.cos(tang), math.sin(tang), 0)) * p0[0]
                    q1 = Vector((org[0], org[1], 0)) + Vector((math.cos(tang), math.sin(tang), 0)) * p1[0]
                    e = Vector((math.cos(a), math.sin(a), 0))
                    mb.beam((q0.x + e.x * 0.45, q0.y + e.y * 0.45, p0[1]), (q1.x + e.x * 0.45, q1.y + e.y * 0.45, p1[1]),
                            0.5, 0.42, "Metal_Dark", 0.0)
        # tira de costura rebitada entre chapas
        a2 = D(15.0 * k + 7.5)
        mb.box((0.34, 0.46, ZC1 - ZC0 + 0.1), tpt(a2, RC + th / 2 + 0.1, (ZC0 + ZC1) / 2), (0, 0, a2), "Metal_Iron", 0.0)
        if k in rust_k:
            # escorrido de ferrugem descendo da costura de cima (varias chapas, nao uma chapa inteira)
            u = rng.uniform(-half * 0.5, half * 0.5)
            ln = rng.uniform(2.4, 4.2)
            zt_ = ZC1 - 0.45
            drip = [(u - 0.28, zt_), (u + 0.26, zt_), (u + 0.16, zt_ - ln * 0.55), (u + 0.05, zt_ - ln),
                    (u - 0.1, zt_ - ln * 0.7), (u - 0.2, zt_ - ln * 0.3)]
            if kind != "plain":
                drip = [(p[0], max(p[1], zsp + ow + 0.35)) for p in drip]
            xz_prism(mb, drip, -th / 2 - 0.01, -th / 2 - 0.07, "Metal_Rust", tang, org)   # v+ aponta para dentro
    # brilho interno em degrade (visto pelas bocas): amarelo embaixo, laranja, rubro no alto -> le calor de
    # fornalha, nao vidraca de farol
    rin = RC - th / 2 - 0.2
    for (za, zb, m) in ((ZC0, ZC0 + 2.3, "Fire_Glow_Core"), (ZC0 + 2.3, ZC0 + 4.3, "Fire_Glow_Mid"),
                        (ZC0 + 4.3, ZC1, "Ember_Glow")):
        mb.cyl(rin, zb - za, (CX, CY, (za + zb) / 2), (0, 0, 0), m, 24, bevel=0.0, caps=False)
    mb.cyl(rin, 0.4, (CX, CY, ZC0 + 1.4), (0, 0, 0), "Fire_Glow_Core", 24, bevel=0.0)
    # labio: aba de ferro em balanco com a face de BAIXO incandescente (anel continuo visivel da praca)
    nl = 24
    r_l = RC + th / 2 + 1.15
    for k in range(nl):
        a = math.tau * (k + 0.5) / nl
        ch = 2 * r_l * math.sin(math.pi / nl) + 0.06
        mb.box((1.25, ch, 0.36), tpt(a, RC + th / 2 + 0.5, ZC1 - 0.12), (0, 0, a), "Furnace_Glow", 0.0)
        mb.box((1.5, ch + 0.12, 0.5), tpt(a, RC + th / 2 + 0.62, ZC1 + 0.31), (0, 0, a), "Metal_Dark", 0.0)
    mb.cyl(RC - th / 2 - 0.05, 0.5, (CX, CY, ZC1 + 0.31), (0, 0, 0), "Metal_Dark", 24, bevel=0.0, caps=False)
    # dentes de ferro EM PONTA na borda (serrilha de chapa, nao ameia de castelo), alternando altura
    for k in range(24):
        a = D(15.0 * k + 7.5)
        hgt = 1.8 if k % 2 == 0 else 1.15
        zb_ = ZC1 + 0.52
        xz_prism(mb, [(-0.6, zb_), (0.6, zb_), (0.1, zb_ + hgt), (-0.1, zb_ + hgt)], -0.22, 0.22, "Metal_Dark",
                 a + math.pi / 2, (CX + math.cos(a) * (RC + 0.4), CY + math.sin(a) * (RC + 0.4)))
    # mensula de pedra (base da coroa) + consolos de ferro por baixo
    mb.cyl(RC + th / 2 + 0.05, ZC0 - 62.4, (CX, CY, (ZC0 + 62.4) / 2), (0, 0, 0), SFD, 24, bevel=0.0)
    for k in range(12):
        a = D(30.0 * k + 15.0)
        mb.box((1.3, 0.7, 1.2), tpt(a, ro(61.8) + 0.55, 61.8), (0, 0, a), "Metal_Dark", 0.0)
    light("L_Tower_Crown", "POINT", (CX, CY, (ZC0 + ZC1) / 2), 1400, (1.0, 0.45, 0.12), 4.0)


# ------------------------------------------------------------------ casa da fornalha
def furnace_house(mb, rng):
    t_s = 2.0
    # orcamento: blocos chanfrados so ate z 14.5 (onde o jogador chega perto); acima, blocos retos (junta aparente)
    fz0, fm0 = mb.far_z, mb.far_min
    mb.far_z, mb.far_min = 14.5, 2.6
    # fiada de base sempre escura + parede em blocos grandes (mix baixo; a variacao vem das variantes de valor)
    walls = [((-12.0, 22.0), (-12.0, 38.0), [(4.0, 8.0, 12.6, 17.6)]),                 # oeste: boca da calha
             ((12.0, 22.0), (12.0, 38.0), []),                                           # leste
             ((-HX, 39.0), (HX, 39.0), [(10.0, 16.0, F0, 15.5)])]                        # fundo: nicho da fornalha
    for a, b, ops in walls:
        masonry_wall(mb, a, b, F0 - 0.5, F0 + 1.3, t_s, rng, m=SFD, m2=SFD, course=1.8, blk=(3.8, 5.6),
                     openings=[o for o in ops if o[2] <= F0 + 1.3])
        masonry_wall(mb, a, b, F0 + 1.3, HZ, t_s, rng, m=SF, m2=SFD, course=2.7, mix=0.1, blk=(3.8, 5.8),
                     openings=ops)
    # frente (= parede de fundo do salao no trecho central): arco de 10 para a torre, recorte folgado p/ aduelas
    fy = 20.9
    masonry_wall(mb, (-HX, fy), (HX, fy), FL, HZ, 2.2, rng, m=SF, m2=SFD, course=2.7, mix=0.1, blk=(3.8, 5.8),
                 openings=[(HX - 5.0 - 1.3, HX + 5.0 + 1.3, FL, 17.0 + 1.3, 2.5 + 1.3)])
    arch(mb, (0.0, fy, 0), 0.0, 10.0, 14.5, 2.5, 2.5, "Stone_Light", "Stone_Light", n=9, band=1.3)
    for s in (-1, 1):   # cunhais claros nas ombreiras do arco
        for k in range(4):
            wq = 1.3 if k % 2 == 0 else 0.9
            mb.box((wq, 2.5, 2.3 - 0.1), (s * (5.0 + wq / 2), fy, FL + 2.3 * (k + 0.5) + 0.05), (0, 0, 0),
                   "Stone_Light", 0.12)
    # cunhais escuros nos cantos de fundo
    z = F0 - 0.5
    k = 0
    while z < HZ - 0.3:
        h = min(2.7, HZ - z)
        for sx in (-1, 1):
            size = (3.3, 2.3, h - 0.1) if k % 2 == 0 else (2.3, 3.3, h - 0.1)
            mb.box((size[0], size[1], size[2]), (sx * (HX - size[0] / 2 + 0.12), HY1 - size[1] / 2 + 0.12, z + h / 2),
                   (0, 0, 0), SFD, 0.14)
        z += h
        k += 1
    mb.far_z, mb.far_min = fz0, fm0
    # contrafortes com capa inclinada (quebram o bloco liso da casa): fundo x=+-7.5, laterais
    from fm_parts import frustum
    for (cx_, cy_, nx, ny) in ((-7.5, HY1, 0, 1), (7.5, HY1, 0, 1), (-HX, 34.0, -1, 0), (HX, 36.2, 1, 0)):
        wdt, dep, ztp = 2.4, 1.8, 25.0
        c = Vector((cx_ + nx * dep / 2, cy_ + ny * dep / 2, 0))
        sx_, sy_ = (dep, wdt) if nx else (wdt, dep)
        mb.box((sx_, sy_, ztp - F0 + 0.5), (c.x, c.y, (F0 - 0.5 + ztp) / 2), (0, 0, 0), SFD, 0.14)
        frustum(mb, (c.x, c.y, ztp), sx_, sy_, sx_ if ny else 0.3, 0.3 if ny else sy_, 2.6, "Stone_Light",
                top_off=(-nx * (dep / 2 - 0.15), -ny * (dep / 2 - 0.15)))
    # cinta de ferro rebitada (fundo e laterais) e capa do parapeito
    zb0, zb1 = 29.4, 30.7
    mb.box2((-HX - 0.1, HY1 - 0.05, zb0), (HX + 0.1, HY1 + 0.3, zb1), "Metal_Dark", 0.0)
    for sx in (-1, 1):
        mb.box2((sx * HX - 0.05 * sx if sx > 0 else sx * HX - 0.3, 22.0, zb0),
                (sx * HX + 0.3 if sx > 0 else sx * HX + 0.05, HY1 + 0.3, zb1), "Metal_Dark", 0.0)
    for i in range(7):
        x = -HX + 1.5 + i * (2 * HX - 3.0) / 6
        rivet(mb, (x, HY1 + 0.3, (zb0 + zb1) / 2), (0, 1, 0), 0.26, "Metal_Iron", 0.16)
    for sx in (-1, 1):
        for i in range(5):
            rivet(mb, (sx * (HX + 0.3), 23.5 + i * 3.8, (zb0 + zb1) / 2), (sx, 0, 0), 0.26, "Metal_Iron", 0.16)
    cap = "Stone_Light"
    for (x0, y0, x1, y1, n) in ((-HX - 0.2, HY1 - 2.2, HX + 0.2, HY1 + 0.2, 4), (-HX - 0.2, HY0 - 0.2, HX + 0.2, 22.0, 4)):
        for i in range(n):
            xa = x0 + (x1 - x0) * i / n
            xb = x0 + (x1 - x0) * (i + 1) / n
            mb.box2((xa + 0.05, y0, HZ), (xb - 0.05, y1, HZ + 0.7), cap, 0.0)
    for sx in (-1, 1):
        for i in range(3):
            ya = 22.0 + (HY1 - 2.2 - 22.0) * i / 3
            yb = 22.0 + (HY1 - 2.2 - 22.0) * (i + 1) / 3
            xa, xb = (sx * HX - 2.2, sx * HX + 0.2) if sx > 0 else (sx * HX - 0.2, sx * HX + 2.2)
            mb.box2((xa, ya + 0.05, HZ), (xb, yb - 0.05, HZ + 0.7), cap, 0.0)
    mb.box2((-HX + 1.0, 22.0, ZDECK - 0.4), (HX - 1.0, HY1 - 1.0, ZDECK), SFD, 0.0)
    # boca de alimentacao da calha de minerio (oeste): moldura rebitada, fresta incandescente, portinhola levantada
    ox = -HX
    ya, yb, za, zb = 26.0, 30.0, 12.6, 17.6
    mb.box2((ox + 0.9, ya, za), (ox + 1.2, yb, zb), "Furnace_Glow", 0.0)
    for (p0, p1) in (((ox - 0.35, ya - 0.5, za - 0.5), (ox + 0.1, yb + 0.5, za)),
                     ((ox - 0.35, ya - 0.5, zb), (ox + 0.1, yb + 0.5, zb + 0.5)),
                     ((ox - 0.35, ya - 0.5, za), (ox + 0.1, ya, zb)), ((ox - 0.35, yb, za), (ox + 0.1, yb + 0.5, zb))):
        mb.box2(p0, p1, "Metal_Dark", 0.0)
    for (yy, zz) in ((ya - 0.25, za - 0.25), (yb + 0.25, za - 0.25), (ya - 0.25, zb + 0.25), (yb + 0.25, zb + 0.25),
                     ((ya + yb) / 2, zb + 0.25)):
        rivet(mb, (ox - 0.35, yy, zz), (-1, 0, 0), 0.24, "Metal_Iron", 0.14)
    hinge = Vector((ox - 0.45, (ya + yb) / 2, zb + 0.35))
    ph = 2.8
    dirp = Vector((-math.sin(D(112)), 0.0, -math.cos(D(112))))
    mb.box((0.22, yb - ya + 0.2, ph), hinge + dirp * (ph / 2), (0, D(112), 0), "Metal_Iron", 0.0)
    for yy in (ya + 0.6, yb - 0.6):
        mb.box((0.3, 0.35, ph * 0.9), hinge + dirp * (ph / 2) + Vector((-0.12, yy - (ya + yb) / 2, 0)), (0, D(112), 0),
               "Metal_Dark", 0.0)
    tip = hinge + dirp * ph
    chain_links(mb, (ox - 0.2, (ya + yb) / 2 - 1.6, zb + 3.2), (tip.x, tip.y - 1.6, tip.z), sag=0.3, link=0.8,
                th=0.14)
    mb.box((0.5, 0.5, 0.5), (ox - 0.2, (ya + yb) / 2 - 1.6, zb + 3.2), (0, 0, 0), "Metal_Dark", 0.0)
    # nicho de fundo: verga de ferro rebitada, cunhais claros, portinhola da fornalha e cinzeiro incandescente
    ny = HY1
    mb.box2((-3.0, 38.2, F0), (3.0, 38.6, 15.5), SFD, 0.0)
    mb.box2((-3.8, 37.9, 15.5), (3.8, ny + 0.25, 16.7), "Metal_Dark", 0.06)
    for i in range(6):
        rivet(mb, (-3.2 + i * 1.28, ny + 0.25, 16.1), (0, 1, 0), 0.24, "Metal_Iron", 0.14)
    for s in (-1, 1):
        for k in range(4):
            wq = 1.2 if k % 2 == 0 else 0.8
            h = (15.5 - F0) / 4
            mb.box((wq, 2.1, h - 0.1), (s * (3.0 + wq / 2), 39.0, F0 + h * (k + 0.5)), (0, 0, 0), "Stone_Light", 0.12)
    dz0, dz1 = F0 + 2.4, F0 + 6.4
    mb.box2((-2.1, 38.55, dz0 - 0.5), (2.1, 38.95, dz1 + 0.5), "Metal_Dark", 0.0)
    mb.box2((-1.7, 38.9, dz0), (1.7, 39.25, dz1), "Metal_Iron", 0.05)
    for zz in (dz0 + 0.8, dz1 - 0.8):
        mb.box2((-1.9, 39.2, zz - 0.2), (0.9, 39.45, zz + 0.2), "Metal_Dark", 0.0)
    mb.box2((0.7, 39.2, (dz0 + dz1) / 2 - 0.3), (1.4, 39.6, (dz0 + dz1) / 2 + 0.3), "Metal_Brass", 0.0)
    mb.box2((-1.3, 39.2, dz1 - 1.3), (1.3, 39.3, dz1 - 1.0), "Furnace_Glow", 0.0)
    mb.box2((-2.2, 38.6, F0 + 0.35), (2.2, 38.9, F0 + 1.7), "Furnace_Glow", 0.0)
    for k in range(6):
        mb.box((0.18, 0.2, 1.4), (-1.9 + k * 0.76, 39.0, F0 + 1.0), (0, 0, 0), "Metal_Dark", 0.0)
    for i in range(7):
        s = rng.uniform(0.7, 1.1)
        mb.rock((rng.uniform(-3.5, 3.5), ny + rng.uniform(0.4, 1.6), F0 + 0.2), (s * 1.2, s, s * 0.6), "Stone_Coal", 0,
                (0, 0, rng.uniform(0, 6)))
    mb.beam((3.4, ny + 0.6, F0 + 0.2), (2.9, ny + 0.3, F0 + 3.8), 0.16, 0.16, "Wood_Dark", 0.0)
    mb.box((0.8, 0.12, 0.9), (3.45, ny + 0.75, F0 + 0.5), (D(-15), 0, 0), "Metal_Iron", 0.0)
    # colisao da casa
    A = "Forge"
    col_box2(A, (-HX, 22.0, F0 - 1), (-11.0, HY1, HZ + 1))
    col_box2(A, (11.0, 22.0, F0 - 1), (HX, HY1, HZ + 1))
    col_box2(A, (-HX, 38.0, F0 - 1), (HX, HY1, HZ + 1))
    col_box2(A, (-HX, HY0, FL), (-5.0, 22.0, HZ + 1))
    col_box2(A, (5.0, HY0, FL), (HX, 22.0, HZ + 1))
    col_box2(A, (-5.0, HY0, 17.0), (5.0, 22.0, HZ + 1))


# ------------------------------------------------------------------ torre (interior + fuste + coroa)
def tower(rng):
    mb = FB("FORGE_Chimney_Tower", C, rng, detail="near", far_z=30.0)
    furnace_house(mb, rng)

    def inside_walls(c):
        return c.y < 22.3 or c.y > 37.7
    # base (so o lado de dentro aparece: fornalha) - blocos sem chanfro, nucleo de rejunte atras
    ring_wall(mb, FL - 0.3, 30.0, lambda z: 10.0, 2.2, rng, course=2.6, blk=4.6,
              gaps=[(270.0, 5.0, FL - 1, 17.0, 2.5)], mix=0.12, base_m=SFD, bevel=0.0, skip=inside_walls,
              core_m=SFD, core_gaps=True)
    mb.cyl(8.0, 0.6, (CX, CY, 30.3), (0, 0, 0), SFD, 20, bevel=0.0)                       # forro da fornalha
    # talude (mensula) do deque ate o fuste, cinta 1
    mb.cyl(10.4, ZT1 - ZT0, (CX, CY, (ZT0 + ZT1) / 2), (0, 0, 0), SFD, 24, r2=RS0 + 0.05, bevel=0.0, caps=False)
    gaps = []
    for ad in (259.0, 281.0, 90.0):
        gaps.append((ad, SLIT[0] + 0.9, SLIT[1] - 0.8, SLIT[2] + SLIT[0] + 1.35, SLIT[0] + 1.35))
    mb.detail = "hero"      # o fuste e a silhueta heroi: blocos sempre chanfrados
    ring_wall(mb, ZS0, ZS1, ro, 1.8, rng, course=2.75, blk=4.7, gaps=gaps, mix=0.1, base_m=SFD, bevel=0.14,
              core_m=SFD)
    mb.detail = "near"
    for ad in (259.0, 281.0, 90.0):
        tall_slit(mb, ad, rng)
    # so 3 cintas grossas encostadas na pedra: casa (29.4..30.7), base do fuste e sob a coroa
    for (z0, z1) in ((ZT1, ZS0), (ZS1, 62.4)):
        r = ro((z0 + z1) / 2) + 0.05
        mb.cyl(r + 0.25, z1 - z0, (CX, CY, (z0 + z1) / 2), (0, 0, 0), "Metal_Dark", 24, bevel=0.0)
        for i in range(10):
            a = D(36.0 * i + 18.0)
            rivet(mb, tpt(a, r + 0.25, (z0 + z1) / 2), (math.cos(a), math.sin(a), 0), 0.3, "Metal_Iron", 0.18)
    crown(mb, rng)
    mb.finish()
    # colisao: anel interno (frente aberta ate o arco), casa e bloco da torre acima do forro
    A = "Forge"
    for i in range(16):
        a = (i + 0.5) / 16 * math.tau
        deg = math.degrees(a) % 360
        c = Vector((CX + math.cos(a) * 8.9, CY + math.sin(a) * 8.9, (F0 + 30) / 2))
        w = 2 * 10.0 * math.sin(math.pi / 16) + 0.3
        if abs(((deg - 270 + 180) % 360) - 180) < 20:
            col_box(A, (2.2, w, 30 - 17.0), (c.x, c.y, 17.0 + (30 - 17.0) / 2), (0, 0, a))
            continue
        col_box(A, (2.2, w, 30 - F0), c, (0, 0, a))
    col_box(A, (2 * HX, HY1 - 22.0, ZDECK - 30.0 + 1.0), (CX, (22.0 + HY1) / 2, (30.0 + ZDECK) / 2))
    col_box(A, (2 * RS0, 2 * RS0, TOP - ZDECK), (CX, CY, (ZDECK + TOP) / 2))
    col_box2(A, (-3.0, 37.9, F0), (3.0, HY1, 16.7))


# ------------------------------------------------------------------ fornalha (dentro da torre)
def furnace(mb, rng):
    pave_poly(mb, [(CX + math.cos(D(a)) * 7.7, CY + math.sin(D(a)) * 7.7) for a in range(0, 360, 20)], FL - 0.3,
              rng, tile=2.9, h=0.3, grout=True, m=SF, grout_m=SFD)
    col_box("Forge", (16.0, 16.0, 1.0), (CX, CY, FL - 0.5), (0, 0, 0), "Floor")
    # contrapiso sob o piso da fornalha e soleira do arco (sem fresta ate o chao do vale entre o salao e a torre)
    mb.cyl(8.3, FL - 0.32 - (F0 - 0.5), (CX, CY, (F0 - 0.5 + FL - 0.32) / 2), (0, 0, 0), SFD, 20, bevel=0.0)
    mb.box2((-5.6, HY0 - 0.3, F0 - 0.5), (5.6, 23.6, FL - 0.02), SFD, 0.0)
    fx, fy = CX, CY + 2.2
    fb = fy + 1.2        # corpo recuado: o cilindro nao tampa mais a boca da camara
    # corpo do forno (pedra), capelo de ferro e fumeiro ate o forro
    mb.cyl(3.6, 5.0, (fx, fb, FL + 2.5), (0, 0, 0), SFD, 12, bevel=0.3)
    mb.cyl(3.7, 3.0, (fx, fb, FL + 6.4), (0, 0, 0), "Metal_Dark", 12, r2=1.4, bevel=0.2)
    mb.cyl(1.4, 30.0 - (FL + 7.9), (fx, fb, (FL + 7.9 + 30.0) / 2), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    for zz in (FL + 12.0, FL + 18.0):
        flange(mb, (fx, fb, zz), Z, 1.75, "Metal_Iron", 0, n=10, w=0.5)
    # boca do forno: bloco de pedra na frente do corpo com a camara aberta ~1.2 recuada atras da moldura de ferro
    my = fy - 3.6
    yk = fb - 3.66                               # fundo da camara (na frente da face do cilindro)
    for s in (-1, 1):
        mb.box2((min(s * 1.4, s * 2.4), my + 0.55, FL), (max(s * 1.4, s * 2.4), fb - 2.5, FL + 3.8), SFD, 0.1)
    mb.box2((fx - 2.4, my + 0.55, FL + 3.0), (fx + 2.4, fb - 2.5, FL + 3.8), SFD, 0.1)
    for (p0, p1) in (((fx - 1.9, my - 0.2, FL), (fx - 1.4, my + 0.6, FL + 3.6)),
                     ((fx + 1.4, my - 0.2, FL), (fx + 1.9, my + 0.6, FL + 3.6)),
                     ((fx - 1.9, my - 0.2, FL + 3.0), (fx + 1.9, my + 0.6, FL + 3.6)),
                     ((fx - 1.9, my - 0.2, FL), (fx + 1.9, my + 0.6, FL + 0.6))):
        mb.box2(p0, p1, "Metal_Dark", 0.0)       # moldura
    # leito de carvao baixo, grelha, brasas por cima e fundo incandescente (a camara fica aberta)
    mb.box2((fx - 1.4, my + 0.55, FL + 0.55), (fx + 1.4, yk, FL + 1.0), "Stone_Coal", 0.0)
    mb.box2((fx - 1.35, yk - 0.1, FL + 1.0), (fx + 1.35, yk, FL + 2.95), "Furnace_Glow", 0.0)
    for k in range(5):
        mb.box((0.18, yk - my - 0.7, 0.18), (fx - 1.0 + k * 0.5, (my + 0.6 + yk) / 2, FL + 1.08), (0, 0, 0),
               "Metal_Dark", 0.0)
    for i in range(6):
        mb.rock((fx + rng.uniform(-0.95, 0.95), rng.uniform(my + 0.8, yk - 0.3), FL + 1.3), (0.62, 0.55, 0.4),
                "Fire_Glow_Core" if i % 2 else "Ember_Glow", 0)
    arch(mb, (fx, my - 0.3, 0), 0.0, 3.2, FL + 3.6, 1.0, 0.9, "Stone_Light", "Stone_Light", n=5, band=0.7)
    # ventaneira (tuyere) onde chega o duto dos foles pela parede leste
    tube_pt(mb, [Vector((7.6, 28.2, 12.0)), Vector((5.6, 28.8, 12.0)), Vector((4.0, 30.4, FL + 3.2)),
                 Vector((2.6, 31.6, FL + 3.2))], 0.7, "Metal_Iron", 10)
    flange(mb, (4.8, 29.6, 10.1), (-1.6, 1.6, -3.8), 0.95, "Metal_Dark", 0, n=10, w=0.4)
    # bica de vazamento -> cadinho -> lingoteira (bordas escuras, so o metal incandescente)
    mb.beam((fx - 1.5, fy - 3.4, FL + 1.4), (fx - 3.6, fy - 5.6, FL + 0.95), 0.8, 0.45, "Metal_Iron", 0.0)
    mb.beam((fx - 1.6, fy - 3.4, FL + 1.62), (fx - 3.5, fy - 5.5, FL + 1.18), 0.36, 0.08, "Fire_Glow_Core", 0.0)
    mx, my2 = fx - 4.6, fy - 6.7
    mb.box((3.4, 2.1, 0.7), (mx, my2, FL + 0.35), (0, 0, D(-40)), "Metal_Dark", 0.05)
    for k in (-1, 0, 1):
        q = Vector((mx, my2, 0)) + Vector((math.cos(D(-40)), math.sin(D(-40)), 0)) * (k * 1.05)
        mb.box((0.78, 1.4, 0.12), (q.x, q.y, FL + 0.72), (0, 0, D(-40)), "Fire_Glow_Core", 0.0)
    cx_, cy_ = fx - 5.3, fy - 1.4
    mb.box2((cx_ - 1.4, cy_ - 1.4, FL), (cx_ + 1.4, cy_ + 1.4, FL + 1.1), SFD, 0.1)
    mb.cyl(1.05, 1.4, (cx_, cy_, FL + 1.8), (0, 0, 0), "Metal_Dark", 10, r2=1.25, bevel=0.0)
    mb.cyl(1.0, 0.1, (cx_, cy_, FL + 2.45), (0, 0, 0), "Fire_Glow_Core", 10, bevel=0.0)
    # carvao
    for i in range(9):
        mb.rock((CX + 5.2 + rng.uniform(-1, 1), CY + 1.5 + rng.uniform(-1.6, 1.6), FL + 0.3), (1.3, 1.2, 0.9), "Stone_Coal", 0)
    light("L_Furnace", "POINT", (fx, fy - 5.8, FL + 3.4), 800, (1.0, 0.45, 0.12), 1.0)
    col_box("Forge", (7.6, fb + 3.6 - (my - 0.2), 7.0), (fx, (fb + 3.6 + my - 0.2) / 2, FL + 3.5))


# ------------------------------------------------------------------ fumeiro: coifa da lareira -> telhado -> torre
def flue_and_pipes(mb, rng):
    ang_roof = math.atan2(13.0, 20.0)
    # fumeiro: sai do topo da coifa (fm_forge.hearth), corre sobre o peito, sobe RENTE ao oitao ao lado do brasao,
    # passa por cima do telhado ao lado do lanternim e entra na torre (z~40.6) com colar rebitado.
    # |x| <= 6: fora de todas as linhas de visada spawn -> portais
    xr = -6.0
    yf = -0.9
    zr = 40.6
    yT = CY - math.sqrt(ro(zr) ** 2 - xr ** 2)
    rD = 1.75
    big_pipe(mb, [(0.0, yf, 20.4), (0.0, yf, 22.2), (xr, yf, 22.2), (xr, yf, zr), (xr, yT + 0.2, zr)], rD,
             "Metal_Dark", "Metal_Brass", bend=2.4, step=5.5, bolts=0)
    gate_valve(mb, Vector((xr, yf, 29.5)), Z, rD * 0.95, up=(-1, 0, 0))
    en = Vector((xr, yT - CY, 0.0)).normalized()
    boss(mb, (xr + en.x * 0.1, yT + en.y * 0.1 + 0.05, zr), en, 4.8)
    for zz in (26.0, 34.0):          # abracadeiras presas no oitao
        mb.rod((xr, yf, zz - 0.3), (xr, yf, zz + 0.3), rD * 1.14, "Metal_Iron", 12)
        mb.beam((xr, yf + rD * 0.9, zz), (xr, 2.75, zz), 0.4, 0.4, "Metal_Dark", 0.0)
    zroof = 37.0 - 13.0 * abs(xr) / 20.0 + 0.9
    for yy in (8.5, 15.5):           # cavaletes sobre o telhado
        for sx in (-1.0, 1.0):
            zfoot = 37.0 - 13.0 * abs(xr + sx) / 20.0 + 0.9
            mb.beam((xr + sx, yy, zfoot - 0.1), (xr + sx * 0.3, yy, zr - rD * 0.9), 0.35, 0.35, "Metal_Dark", 0.0)
        mb.rod((xr, yy - 0.3, zr), (xr, yy + 0.3, zr), rD * 1.14, "Metal_Iron", 12)
    # tubos laterais: saem dos flancos da torre, cotovelo de 45 e descem para o telhado do salao (|x|<=18, z<=26.5)
    rP = 1.9
    for (adeg, zo, xin, valve_z) in ((212.0, 45.0, -17.2, 33.5), (332.0, 49.0, 16.9, 35.5)):
        a = D(adeg)
        e = Vector((math.cos(a), math.sin(a), 0.0))
        p0 = tpt(a, ro(zo) - 0.3, zo)
        p1 = p0 + e * 3.6
        dist = (xin - p1.x) / e.x
        p2 = p1 + e * dist - Z * dist
        zin = 37.0 - 13.0 * abs(xin) / 20.0 + 0.9
        p3 = Vector((p2.x, p2.y, zin - 0.9))
        big_pipe(mb, [p0, p1, p2, p3], rP, "Metal_Dark", "Metal_Brass", bend=3.2, step=5.0, bolts=0)
        boss(mb, tpt(a, ro(zo) + 0.1, zo), e, 5.0)
        sx = 1.0 if xin > 0 else -1.0
        rufo(mb, (p3.x, p3.y, zin - 0.1), rP, (0.0, sx * ang_roof))
        gate_valve(mb, Vector((p3.x, p3.y, valve_z)), Z, rP * 0.9, up=e)
    # tubo de cobre C: parede leste da casa -> telhado da ala direita (colar rebitado na parede)
    c0 = Vector((HX + 0.2, 28.5, 24.5))
    c1 = Vector((19.4, 28.5, 24.5))
    zc = wing_roof_z(21.8, "R")
    c2 = Vector((21.8, 28.5, zc + 0.3))
    c3 = Vector((21.8, 28.5, zc - 0.8))
    big_pipe(mb, [c0, c1, c2, c3], 0.95, "Metal_Copper", "Metal_Dark", bend=1.6, step=5.0, n=10, bolts=0)
    boss(mb, (HX + 0.2, 28.5, 24.5), (1, 0, 0), 2.6)
    rufo(mb, (21.8, 28.5, zc - 0.1), 0.95, (0.0, -math.atan2(WING_RISE_R, 7.0)))


def build(rng):
    tower(rng)
    mb = FB("FORGE_Pipes_Big", C, rng, detail="near", far_z=30.0)
    flue_and_pipes(mb, rng)
    mb.finish()
    mi = FB("FORGE_Furnace_Interior", C, rng, detail="near")
    furnace(mi, rng)
    mi.finish()
