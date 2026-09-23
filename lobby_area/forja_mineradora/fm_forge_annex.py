# fm_forge_annex - anexos industriais da Forja do Ignis (passe de acabamento): tubulacao grossa ate a torre,
# galeria + passarela metalica alta, elevador de canecas e guincho de minerio (ala esquerda), descarga de carrinho,
# telheiro de carvao, casa de foles externa (ala direita), torre de respiro, engrenagens na parede, respiros e
# pilhas de carvao na fachada. Nada aqui bloqueia rotas; tudo que se pode esbarrar tem COL_ForgeX.
import math
from mathutils import Vector, Matrix, Euler
from fm_lib import MB, D, col_box, col_box2, light
from fm_parts import crystal_cluster, crate, barrel, frustum, hanging_lantern
from fm_forge_kit import (big_pipe, pipe_clamp, gate_valve, handwheel, flange, rivet, iron_bracket, chain_links,
                          gear, tube_pt, xz_prism, forge_roof, Z)
import fm_layout as L

C = "03_FORGE"
F0 = L.FLOOR
FL = L.FL
A = "ForgeX"
CX, CY = L.CHIMNEY
R = L.CHIMNEY_R
ZC = L.CHIMNEY_TOP - 8.0


def ro(z):
    """raio externo do fuste da torre na cota z (mesma conicidade de fm_forge.chimney)"""
    if z < 26.0:
        return R
    return (R - 0.9) - 1.1 * (z - 26.0) / (ZC - 26.0)


def tpt(a_deg, r, z):
    a = D(a_deg)
    return Vector((CX + math.cos(a) * r, CY + math.sin(a) * r, z))


class LF:
    """referencial local 3D (origem + rotacao) para montar pecas tombadas/inclinadas"""

    def __init__(self, o, rot):
        self.o = Vector(o)
        self.M = Euler(rot).to_matrix()

    def p(self, x, y, z):
        return self.o + self.M @ Vector((x, y, z))

    def r(self, rx=0.0, ry=0.0, rz=0.0):
        return (self.M @ Euler((rx, ry, rz)).to_matrix()).to_euler()


# ------------------------------------------------------------------ tubulacao grossa ate a torre
def pipes(rng):
    mb = MB("FORGE_Pipes_Big", C, rng)
    # A (esquerda): sai do telhado da ala esquerda, sobe e entra na cinta de ferro da torre, com registro e respiro
    a0 = Vector((-25.6, 19.5, 21.5))
    a1 = Vector((-25.6, 19.5, 39.5))
    dA = (Vector((CX, CY, 0)) - Vector((a0.x, a0.y, 0))).normalized()
    a2 = Vector((CX, CY, 39.5)) - dA * 8.95
    rA = 2.1
    big_pipe(mb, [a0, a1, a2], rA, "Metal_Dark", "Metal_Iron", bend=4.2, step=7.5)
    gate_valve(mb, a1 + (a2 - a1) * 0.55, dA, rA * 0.95, up=(0, 0, 1))
    # respiro sobre o trecho reto (chapeu de cogumelo)
    v0 = a1 + dA * 5.6
    vb = Vector((v0.x, v0.y, 39.5 + rA - 0.3))
    mb.rod(vb, vb + Z * 4.2, 0.55, "Metal_Iron", 10)
    flange(mb, vb + Z * 1.2, Z, 0.8, "Metal_Dark", 0, n=10)
    mb.cyl(1.35, 0.5, vb + Z * 4.5, (0, 0, 0), "Metal_Dark", 10, r2=0.35, bevel=0.0)
    mb.cyl(0.7, 0.35, vb + Z * 4.1, (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    # berco: duas pernas do anel ate o telhado da ala
    c = Vector((a0.x, a0.y, 29.0))
    mb.rod(c - Z * 0.4, c + Z * 0.4, rA * 1.14, "Metal_Iron", 14)
    wcx = (L.FORGE_WING_L[0] + L.FORGE_WING_L[2]) / 2
    for sx in (-1, 1):
        fx = a0.x + sx * 3.2
        foot = Vector((fx, a0.y + 0.4, 19.5 + 7.0 * (1 - abs(fx - wcx) / 7.0) + 0.75))
        mb.beam(c + Vector((sx * rA * 0.9, 0, -0.2)), foot, 0.5, 0.5, "Metal_Dark", 0.04)
        mb.box((1.2, 1.2, 0.35), foot, (0, 0, 0), "Metal_Iron", 0.04)
    # placa de reforco na entrada da torre (sobre a cinta de ferro)
    _boss(mb, Vector((CX, CY, 39.5)) - dA * 9.45, -dA, 5.2)

    # B (direita): sobe do telhado da ala direita, vai ate a torre, escala a torre presa por abracadeiras e entra alto
    b0 = Vector((26.0, 13.0, 21.5))
    b1 = Vector((26.0, 13.0, 33.0))
    dB = (Vector((b0.x, b0.y, 0)) - Vector((CX, CY, 0))).normalized()
    b2 = Vector((CX, CY, 33.0)) + dB * 11.9
    b3 = Vector((b2.x, b2.y, 51.0))
    b4 = Vector((CX, CY, 51.0)) + dB * (ro(51.0) - 0.35)
    rB = 1.9
    big_pipe(mb, [b0, b1, b2, b3, b4], rB, "Metal_Dark", "Metal_Iron", bend=3.4, step=8.0)
    for zz in (37.0, 46.5):
        p = Vector((b2.x, b2.y, zz))
        pipe_clamp(mb, p, Z, rB, Vector((CX, CY, zz)) + dB * (ro(zz) + 0.45))
    gate_valve(mb, Vector((b2.x, b2.y, 42.2)), Z, rB * 0.9, up=dB)
    _boss(mb, Vector((CX, CY, 51.0)) + dB * (ro(51.0) + 0.1), dB, 5.2)
    # B2: tubo de cobre menor, paralelo ao B (feixe), mais baixo, entrando na base do fuste
    s = Vector((-dB.y, dB.x, 0))
    c0 = b0 + s * 3.1
    c0.z = 21.5
    c1 = Vector((c0.x, c0.y, 30.5))
    c2 = Vector((b2.x, b2.y, 30.5)) + s * 3.1
    dc = (Vector((c2.x, c2.y, 0)) - Vector((CX, CY, 0))).normalized()
    c3 = Vector((CX, CY, 30.5)) + dc * 8.9
    big_pipe(mb, [c0, c1, c2, c3], 0.95, "Metal_Copper", "Metal_Dark", bend=2.0, step=7.0, n=10, bolts=0)
    mb.finish()


def _boss(mb, p, d, size):
    """chapa quadrada rebitada onde o tubo encontra a torre"""
    d = Vector((d.x, d.y, 0)).normalized()
    ang = math.atan2(d.y, d.x)
    mb.box((0.45, size, size), p, (0, 0, ang), "Metal_Iron", 0.08)
    s = Vector((-d.y, d.x, 0))
    for i in range(8):
        a = math.tau * i / 8 + math.pi / 8
        q = p + d * 0.25 + s * math.cos(a) * size * 0.4 + Z * math.sin(a) * size * 0.4
        rivet(mb, q, d, 0.24, "Metal_Brass")


# ------------------------------------------------------------------ galeria na torre + passarela metalica alta
def gallery_catwalk(rng):
    mb = MB("FORGE_Catwalk", C, rng)
    zd = 30.0
    a0, a1 = 184.0, 224.0
    rin, rout = ro(zd) - 0.3, 12.4
    n = 10
    poly = [(CX + math.cos(D(a0 + (a1 - a0) * i / n)) * rout, CY + math.sin(D(a0 + (a1 - a0) * i / n)) * rout)
            for i in range(n + 1)]
    poly += [(CX + math.cos(D(a1 - (a1 - a0) * i / n)) * rin, CY + math.sin(D(a1 - (a1 - a0) * i / n)) * rin)
             for i in range(n + 1)]
    mb.prism(poly, zd - 0.45, zd, "Metal_Iron", 0.06)
    # vigas radiais e maos-francesas sob a galeria
    for a in (188.0, 204.0, 220.0):
        o = tpt(a, ro(zd - 0.5) - 0.1, zd - 0.45)
        iron_bracket(mb, o, (math.cos(D(a)), math.sin(D(a))), 3.2, "Metal_Dark", 0.6, 0.36)
    # guarda-corpo (vao onde chega a passarela)
    posts = [a0 + (a1 - a0) * i / 8 for i in range(9)]
    prev = None
    for a in posts:
        gap = 197.0 < a < 214.0
        p = tpt(a, rout - 0.35, zd)
        if not gap:
            mb.box((0.3, 0.3, 2.6), p + Z * 1.3, (0, 0, D(a)), "Metal_Dark", 0.03)
        if prev is not None and not gap and not (197.0 < prev[0] < 214.0):
            for hz in (1.25, 2.5):
                mb.beam(prev[1] + Z * hz, p + Z * hz, 0.22, 0.22, "Metal_Dark", 0.0)
        prev = (a, p)
    # porta da torre na galeria
    pd = tpt(204.0, ro(zd + 2.5) + 0.05, zd + 2.4)
    mb.box((0.6, 3.0, 4.6), pd, (0, 0, D(204.0)), "Stone_Light", 0.1)
    mb.box((0.5, 2.2, 4.0), pd + Vector((math.cos(D(204)), math.sin(D(204)), 0)) * 0.12 - Z * 0.3, (0, 0, D(204.0)),
           "Wood_Dark", 0.05)
    for zz in (-1.2, 0.6):
        mb.box((0.56, 2.3, 0.28), pd + Vector((math.cos(D(204)), math.sin(D(204)), 0)) * 0.2 + Z * zz,
               (0, 0, D(204.0)), "Metal_Dark", 0.02)
    light("L_TowerGallery", "POINT", tpt(204.0, rout - 1.0, zd + 4.2), 120, (1.0, 0.6, 0.3), 0.3)
    hanging_lantern(mb, tpt(212.0, ro(zd + 5.2) + 0.7, zd + 5.6), lights=False, chain=0.6)
    mb.box((1.4, 0.3, 0.3), tpt(212.0, ro(zd + 5.2) + 0.1, zd + 5.6), (0, 0, D(212.0)), "Metal_Dark", 0.02)

    # passarela: da galeria ate o topo do elevador de minerio (y 25.6, deck z 30)
    yc = 25.6
    xa, xb = tpt(204.0, rout - 0.6, zd).x, -35.7
    hw = 1.35
    mb.box2((xb, yc - hw, zd - 0.35), (xa, yc + hw, zd), "Metal_Iron", 0.05)
    # tabuas de grade (sulcos) sobre o deck
    nx = int((xa - xb) / 1.1)
    for i in range(nx):
        x = xb + 0.55 + i * (xa - xb) / nx
        mb.box((0.18, hw * 2 - 0.2, 0.08), (x, yc, zd + 0.02), (0, 0, 0), "Metal_Dark", 0.0)
    # trelicas laterais
    top, bot = zd + 1.35, zd - 1.9
    nseg = max(4, int((xa - xb) / 2.6))
    for s in (-1, 1):
        y = yc + s * hw
        mb.beam((xb, y, top), (xa, y, top), 0.26, 0.26, "Metal_Dark", 0.0)
        mb.beam((xb, y, zd - 0.2), (xa, y, zd - 0.2), 0.3, 0.42, "Metal_Dark", 0.0)
        mb.beam((xb, y, bot), (xa, y, bot), 0.34, 0.4, "Metal_Dark", 0.03)
        for i in range(nseg + 1):
            x = xb + (xa - xb) * i / nseg
            mb.box((0.28, 0.28, top - bot), (x, y, (top + bot) / 2), (0, 0, 0), "Metal_Dark", 0.0)
            if i < nseg:
                x2 = xb + (xa - xb) * (i + 1) / nseg
                if i % 2 == 0:
                    mb.beam((x, y, bot), (x2, y, zd - 0.3), 0.22, 0.22, "Metal_Rust", 0.0)
                else:
                    mb.beam((x, y, zd - 0.3), (x2, y, bot), 0.22, 0.22, "Metal_Rust", 0.0)
    # travessas inferiores
    for i in range(0, nseg + 1, 2):
        x = xb + (xa - xb) * i / nseg
        mb.box((0.3, hw * 2, 0.3), (x, yc, bot), (0, 0, 0), "Metal_Dark", 0.0)
    # sela sobre a cumeeira da ala esquerda
    wx = (L.FORGE_WING_L[0] + L.FORGE_WING_L[2]) / 2
    for s in (-1, 1):
        mb.beam((wx + s * 0.9, yc, 26.9), (wx, yc, bot), 0.5, 0.5, "Metal_Dark", 0.03)
    mb.box((2.6, 2.4, 0.4), (wx, yc, 27.1), (0, 0, 0), "Metal_Iron", 0.05)
    mb.finish()


# ------------------------------------------------------------------ elevador de canecas + guincho (ala esquerda)
def ore_lift(rng):
    mb = MB("FORGE_Ore_Lift", C, rng)
    x0, x1, y0, y1 = -39.4, -35.8, 24.0, 27.6
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    ztop = 30.0
    # torre de madeira: 4 montantes, travessas e cruzes de santo andre
    for x in (x0 + 0.35, x1 - 0.35):
        for y in (y0 + 0.35, y1 - 0.35):
            mb.box((0.7, 0.7, ztop - F0 + 0.2), (x + rng.uniform(-0.05, 0.05), y, (F0 + ztop) / 2), (0, 0, 0),
                   "Wood_Dark", 0.08)
    levels = [F0 + 0.4, 9.5, 15.0, 20.5, 25.5, ztop - 0.4]
    for z in levels:
        mb.beam((x0, y0 + 0.35, z), (x1, y0 + 0.35, z), 0.45, 0.55, "Wood_Dark", 0.05)
        mb.beam((x0, y1 - 0.35, z), (x1, y1 - 0.35, z), 0.45, 0.55, "Wood_Dark", 0.05)
        mb.beam((x0 + 0.35, y0, z), (x0 + 0.35, y1, z), 0.45, 0.55, "Wood_Dark", 0.05)
        mb.beam((x1 - 0.35, y0, z), (x1 - 0.35, y1, z), 0.45, 0.55, "Wood_Dark", 0.05)
    for za, zb in zip(levels, levels[1:]):
        for s in (1, -1):
            mb.beam((x0 + 0.1, y0 + 0.35 + (0 if s > 0 else y1 - y0 - 0.7), za),
                    (x0 + 0.1, y1 - 0.35 - (0 if s > 0 else y1 - y0 - 0.7), zb), 0.3, 0.4, "Wood_Plank", 0.03)
            mb.beam((x0 + 0.35 + (0 if s > 0 else x1 - x0 - 0.7), y0 + 0.1, za),
                    (x1 - 0.35 - (0 if s > 0 else x1 - x0 - 0.7), y0 + 0.1, zb), 0.3, 0.4, "Wood_Plank", 0.03)
    # pe (caixa de alimentacao) e plataforma do topo
    mb.box2((x0 + 0.2, y0 + 0.2, F0), (x1 - 0.2, y1 - 0.2, F0 + 2.4), "Wood_Plank", 0.1)
    for z in (F0 + 0.3, F0 + 2.1):
        mb.box2((x0 + 0.1, y0 + 0.1, z - 0.15), (x1 - 0.1, y1 - 0.1, z + 0.15), "Metal_Dark", 0.02)
    mb.box2((x0 - 0.3, y0 - 0.3, ztop - 0.35), (x1 + 0.1, y1 + 0.3, ztop), "Metal_Iron", 0.05)
    for (pa, pb) in (((x0 - 0.2, y0 - 0.2), (x0 - 0.2, y1 + 0.2)), ((x0 - 0.2, y1 + 0.2), (x1, y1 + 0.2))):
        mb.beam((pa[0], pa[1], ztop + 1.3), (pb[0], pb[1], ztop + 1.3), 0.22, 0.22, "Metal_Dark", 0.0)
        mb.box((0.26, 0.26, 1.35), (pb[0], pb[1], ztop + 0.65), (0, 0, 0), "Metal_Dark", 0.0)
    # correntes das canecas (sobe no lado sul, desce no norte) e roda de cabeca exposta
    ys, yn = y0 + 1.05, y1 - 1.05
    zc_, rw = ztop + 2.0, (yn - ys) / 2
    for y in (ys, yn):
        mb.beam((xc - 0.35, y, F0 + 1.8), (xc - 0.35, y, zc_), 0.14, 0.14, "Metal_Dark", 0.0)
        mb.beam((xc + 0.35, y, F0 + 1.8), (xc + 0.35, y, zc_), 0.14, 0.14, "Metal_Dark", 0.0)
    gear(mb, (xc, yc, zc_), (1, 0, 0), rw + 0.3, 0.7, 12, "Metal_Dark", "Metal_Iron", spokes=4)
    for s in (-1, 1):
        mb.box((0.5, 0.9, 2.6), (xc + s * 1.1, yc, ztop + 1.0), (0, 0, 0), "Wood_Dark", 0.05)
    mb.rod((xc - 1.5, yc, zc_), (xc + 1.5, yc, zc_), 0.22, "Metal_Iron", 8)
    # telhadinho sobre a roda
    forge_roof(mb, xc - 0.3, yc, x1 - x0 + 0.4, y1 - y0 + 0.2, ztop + 3.7, 1.6, rng, thick=0.5, over=0.5, sag=0.0,
               row_h=1.0, seg=5.0, patches=0)
    for x in (x0, x1 - 0.1):
        for y in (y0 - 0.05, y1 + 0.05):
            mb.box((0.3, 0.3, 3.7), (x, y, ztop + 1.85), (0, 0, 0), "Wood_Dark", 0.02)
    # canecas: cheias subindo (sul), vazias e viradas descendo (norte)
    z = F0 + 4.6
    k = 0
    while z < ztop - 1.2:
        frustum(mb, (xc, ys - 0.95, z - 0.6), 1.9, 1.2, 2.3, 1.7, 1.25, "Metal_Rust")
        mb.box((2.4, 0.2, 0.25), (xc, ys - 1.85, z + 0.62), (0, 0, 0), "Metal_Dark", 0.0)
        if k % 2 == 0:
            crystal_cluster(mb, (xc, ys - 1.0, z + 0.5), 0.36, "Crystal_Blue" if k % 4 == 0 else "Crystal_Purple",
                            rng, 3)
        else:
            frustum(mb, (xc, yn + 0.95, z + 0.65), 1.9, 1.2, 2.3, 1.7, -1.25, "Metal_Rust")
        z += 2.9
        k += 1
    # bica de descarga: do topo ate a escotilha no telhado da ala
    ya = y1 + 0.55
    pa = Vector((x1 + 0.1, ya, ztop - 0.8))
    pb = Vector((-31.1, ya, 24.7))
    mb.beam(pa, pb, 1.3, 0.3, "Wood_Plank", 0.03)
    for s in (-1, 1):
        mb.beam(pa + Vector((0, s * 0.62, 0.4)), pb + Vector((0, s * 0.62, 0.4)), 0.22, 0.8, "Wood_Dark", 0.0)
    for f in (0.3, 0.7):
        q = pa + (pb - pa) * f
        mb.box((0.3, 1.5, 0.3), q + Vector((0, 0, 0.85)), (0, 0, 0), "Metal_Dark", 0.0)
    crystal_cluster(mb, pa + (pb - pa) * 0.5 + Vector((0, 0, 0.2)), 0.22, "Crystal_Blue", rng, 3)
    # escotilha (agua-furtada) no telhado da ala esquerda
    hx, hy = -29.9, ya
    mb.box2((hx - 1.3, hy - 1.3, 21.6), (hx + 1.3, hy + 1.3, 25.4), "Wood_Plank", 0.08)
    mb.box2((hx - 1.2, hy - 0.8, 24.2), (hx - 0.9, hy + 0.8, 25.2), "Stone_Coal", 0.0)
    forge_roof(mb, hx, hy, 2.8, 2.6, 25.4, 1.2, rng, thick=0.4, over=0.35, sag=0.0, row_h=0.9, seg=4.0, patches=0)
    mb.finish()
    col_box2(A, (x0 - 0.3, y0 - 0.3, F0), (x1 + 0.2, y1 + 0.3, ztop + 3.0))

    # ---- guincho de braco sobre o portao do trilho + caçamba suspensa + sarilho na parede
    gm = MB("FORGE_Ore_Hoist", C, rng)
    wx = L.FORGE_WING_L[0]
    gy = L.FORGE_WING_L[1] + 12.0
    jr = Vector((wx - 0.1, gy - 1.2, 17.4))
    jt = Vector((wx - 6.2, gy - 1.2, 17.4))
    gm.beam(jr, jt, 0.75, 0.9, "Wood_Dark", 0.08)
    gm.box((0.9, 1.6, 2.6), jr + Vector((-0.2, 0, 0.2)), (0, 0, 0), "Metal_Dark", 0.05)
    gm.rod(jt + Vector((0.3, 0, 0.4)), Vector((wx - 0.2, gy - 1.2, 19.2)), 0.12, "Metal_Dark", 6)
    gm.cyl(0.55, 0.5, jt + Vector((0.4, 0, -0.75)), (D(90), 0, 0), "Metal_Iron", 10, bevel=0.0)
    for s in (-1, 1):
        gm.box((0.9, 0.12, 1.3), jt + Vector((0.4, s * 0.32, -0.55)), (0, 0, 0), "Metal_Dark", 0.0)
    bz = 12.4
    gm.rod(jt + Vector((-0.05, 0, -1.2)), Vector((jt.x - 0.05, jt.y, bz + 1.9)), 0.1, "Rope", 5)
    bc = Vector((jt.x - 0.05, jt.y, bz))
    gm.cyl(0.95, 1.4, bc, (0, 0, 0), "Metal_Iron", 10, r2=1.15, bevel=0.05)
    gm.cyl(1.2, 0.2, bc + Z * 0.62, (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    hb = [bc + Vector((0, -1.15, 0.5)), bc + Vector((0, -0.9, 1.5)), bc + Vector((0, 0, 1.95)), bc + Vector((0, 0.9, 1.5)),
          bc + Vector((0, 1.15, 0.5))]
    tube_pt(gm, hb, 0.09, "Metal_Dark", 5)
    crystal_cluster(gm, bc + Z * 0.6, 0.35, "Crystal_Purple", rng, 4)
    # sarilho (tambor com manivela) na parede, ao sul do portao
    wz = 8.2
    wy = L.FORGE_WING_L[1] + 4.8
    for s in (-1, 1):
        gm.box((1.2, 0.3, 2.4), (wx - 0.7, wy + s * 0.95, wz - 0.4), (0, 0, 0), "Metal_Dark", 0.03)
    gm.cyl(0.55, 1.6, (wx - 0.9, wy, wz), (D(90), 0, 0), "Wood_Plank", 10, bevel=0.0)
    for dy in (-0.55, 0.0, 0.55):
        gm.cyl(0.6, 0.12, (wx - 0.9, wy + dy, wz), (D(90), 0, 0), "Rope", 10, bevel=0.0)
    gm.rod((wx - 0.9, wy - 1.3, wz), (wx - 0.9, wy + 1.3, wz), 0.12, "Metal_Iron", 6)
    gm.beam((wx - 0.9, wy + 1.3, wz), (wx - 0.9, wy + 1.3, wz + 1.0), 0.14, 0.14, "Metal_Dark", 0.0)
    gm.rod((wx - 1.35, wy + 1.3, wz + 1.0), (wx - 0.9, wy + 1.3, wz + 1.0), 0.14, "Wood_Light", 6)
    gm.rod((wx - 1.3, wy, wz + 0.5), jr + Vector((-0.6, -0.5, -0.4)), 0.09, "Rope", 5)
    gm.finish()
    col_box2(A, (wx - 1.6, wy - 1.3, F0), (wx, wy + 1.3, wz + 1.6))

    # ---- descarga: carrinho tombado, monte de minerio e caixas ao norte do trilho
    dm = MB("FORGE_Ore_Unload", C, rng)
    cx_, cy_ = -37.2, 21.7
    F = LF((cx_, cy_, F0 + 2.0), (D(-68), 0, D(8)))
    dm.cyl(1.7, 1.6, F.p(0, 0, 0), F.r(0, 0, math.pi / 4), "Metal_Iron", 4, r2=2.1, bevel=0.06)
    dm.cyl(1.62, 1.3, F.p(0, 0, 0.2), F.r(0, 0, math.pi / 4), "Wood_Plank", 4, r2=2.0, bevel=0.0)
    dm.box((3.2, 2.0, 0.3), F.p(0, 0, -0.95), F.r(), "Metal_Dark", 0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = F.p(sx * 1.05, sy * 1.15, -1.3)
            dm.cyl(0.6, 0.28, q, F.r(D(90), 0, 0), "Metal_Dark", 10, bevel=0.0)
    for i in range(9):
        x = cx_ + rng.uniform(-1.8, 1.6)
        y = cy_ + 1.4 + rng.uniform(-0.6, 0.9)
        s = rng.uniform(0.7, 1.3)
        dm.rock((x, y, F0 + 0.25), (s * 1.3, s, s * 0.7), "Cliff_Rock_Dark", 0, (0, 0, rng.uniform(0, 6)))
    for k in range(3):
        crystal_cluster(dm, (cx_ - 1.2 + k * 1.2, cy_ + 1.5 + rng.uniform(-0.3, 0.3), F0 + 0.4), 0.42,
                        ("Crystal_Blue", "Crystal_Purple", "Crystal_Blue")[k], rng, 4)
    crate(dm, (-38.0, 12.4, F0), 1.8, 0.3, rng)
    # pa encostada no carrinho
    dm.beam((cx_ + 1.9, cy_ - 0.9, F0 + 0.2), (cx_ + 1.3, cy_ - 0.2, F0 + 3.6), 0.16, 0.16, "Wood_Light", 0.0)
    dm.box((0.8, 0.12, 0.9), (cx_ + 1.95, cy_ - 1.0, F0 + 0.55), (0, D(-15), D(45)), "Metal_Iron", 0.02)
    dm.finish()
    col_box2(A, (cx_ - 2.3, cy_ - 1.6, F0), (cx_ + 2.2, cy_ + 2.4, F0 + 3.2))
    col_box2(A, (-39.0, 11.4, F0), (-37.0, 13.4, F0 + 1.9))


# ------------------------------------------------------------------ telheiro de carvao (fundos da ala esquerda)
def coal_shed(rng):
    mb = MB("FORGE_Coal_Shed", C, rng)
    xa, xb = -29.6, -20.6
    yw, yp = L.FORGE_WING_L[3], 35.3
    # pilares + maos-francesas de madeira
    for x in (xa + 0.4, (xa + xb) / 2 + rng.uniform(-0.3, 0.3), xb - 0.4):
        mb.box((0.75, 0.75, 6.0), (x, yp, F0 + 3.0), (0, 0, rng.uniform(-0.04, 0.04)), "Wood_Dark", 0.08)
        mb.beam((x, yp, F0 + 4.6), (x, yp - 1.6, F0 + 6.1), 0.4, 0.45, "Wood_Dark", 0.04)
    mb.beam((xa, yp, F0 + 6.0), (xb, yp, F0 + 6.05), 0.7, 0.8, "Wood_Dark", 0.06)
    # caibros e telhado de chapa (meia-agua da parede para os pilares)
    z_w, z_p = F0 + 8.6, F0 + 6.4
    ang = math.atan2(z_w - z_p, yp - yw + 0.8)
    for i in range(5):
        x = xa + 0.3 + i * (xb - xa - 0.6) / 4
        mb.beam((x, yw, z_w - 0.3), (x, yp + 0.8, z_p - 0.1), 0.35, 0.45, "Wood_Dark", 0.03)
    nsh = 6
    for i in range(nsh):
        x0_ = xa - 0.4 + i * (xb - xa + 0.8) / nsh
        x1_ = x0_ + (xb - xa + 0.8) / nsh + 0.12
        mid = Vector(((x0_ + x1_) / 2, (yw + yp + 0.9) / 2, (z_w + z_p) / 2 + 0.25))
        m = "Metal_Rust" if i in (1, 4) else "Roof_Forge"
        mb.box((x1_ - x0_, math.hypot(yp + 0.9 - yw, z_w - z_p) + 0.3, 0.22), mid,
               (-ang + rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), 0), m, 0.03)
        for k in range(3):
            xx = x0_ + (k + 0.5) * (x1_ - x0_) / 3
            mb.box((0.14, math.hypot(yp + 0.9 - yw, z_w - z_p) + 0.3, 0.12), (xx, mid.y, mid.z + 0.16), (-ang, 0, 0), m, 0.0)
    # baias de carvao
    bx = [xa + 0.2, xa + 3.1, xb - 3.1, xb - 0.2]
    for x in bx:
        mb.box((0.3, 3.4, 2.0), (x, yw + 1.7, F0 + 1.0), (0, 0, 0), "Wood_Plank", 0.05)
    mb.box2((xa + 0.2, yw + 3.3, F0), (xb - 0.2, yw + 3.6, F0 + 1.3), "Wood_Plank", 0.05)
    for i in range(3):
        c0 = (bx[i] + bx[i + 1]) / 2
        for k in range(12):
            x = c0 + rng.uniform(-1.1, 1.1)
            y = yw + rng.uniform(0.5, 3.0)
            h = 1.2 * (1 - abs(x - c0) / 1.8) * (1 - (y - yw) / 5.0)
            s = rng.uniform(0.8, 1.3)
            mb.rock((x, y, F0 + 0.4 + h * rng.uniform(0.6, 1.0)), (s, s, s * 0.7), "Stone_Coal", 0,
                    (0, 0, rng.uniform(0, 6)))
    # sacos de carvao e pa
    for k, (x, y) in enumerate(((xb + 0.9, yw + 1.0), (xb + 0.8, yw + 2.4), (xb + 1.0, yw + 1.7))):
        zz = F0 + 0.75 + (1.2 if k == 2 else 0.0)
        mb.ico(0.75, (x, y, zz), "Rope", 1, (0.85, 0.72, 1.0), jitter=0.12)
        mb.cyl(0.28, 0.45, (x, y, zz + 0.85), (0, 0, 0), "Rope", 6, r2=0.4, bevel=0.0)
    mb.beam((xa + 1.6, yp - 0.6, F0 + 0.2), (xa + 1.3, yp - 1.1, F0 + 3.8), 0.16, 0.16, "Wood_Light", 0.0)
    mb.box((0.8, 0.14, 0.9), (xa + 1.62, yp - 0.55, F0 + 0.5), (D(10), 0, 0), "Metal_Iron", 0.02)
    # carrinho de mao com carvao
    wx, wy = -15.8, 34.0
    mb.cyl(1.1, 1.0, (wx, wy, F0 + 1.4), (0, 0, math.pi / 4), "Metal_Iron", 4, r2=1.5, bevel=0.04)
    for k in range(5):
        mb.rock((wx + rng.uniform(-0.6, 0.6), wy + rng.uniform(-0.6, 0.6), F0 + 1.95), (0.8, 0.8, 0.5), "Stone_Coal", 0)
    mb.cyl(0.45, 0.25, (wx + 1.6, wy, F0 + 0.5), (D(90), 0, 0), "Metal_Dark", 10, bevel=0.0)
    for s in (-1, 1):
        mb.beam((wx + 1.6, wy + s * 0.45, F0 + 0.5), (wx - 2.2, wy + s * 0.7, F0 + 1.9), 0.18, 0.18, "Wood_Light", 0.0)
        mb.beam((wx - 0.6, wy + s * 0.55, F0 + 0.9), (wx - 0.7, wy + s * 0.55, F0), 0.16, 0.16, "Wood_Dark", 0.0)
    mb.finish()
    col_box2(A, (xa, yw, F0), (xb, yw + 3.6, F0 + 2.1))
    for x in (xa + 0.4, xb - 0.4):
        col_box2(A, (x - 0.45, yp - 0.45, F0), (x + 0.45, yp + 0.45, F0 + 6.4))
    col_box2(A, (xb + 0.2, yw + 0.2, F0), (xb + 1.8, yw + 3.0, F0 + 2.0))
    col_box2(A, (wx - 2.3, wy - 0.9, F0), (wx + 2.1, wy + 0.9, F0 + 2.2))


# ------------------------------------------------------------------ casa de foles externa (fundos da ala direita)
def bellows_house(rng):
    mb = MB("FORGE_Bellows_House", C, rng)
    xa, xb = 20.8, 31.4
    yw, yp = L.FORGE_WING_R[3], 35.3
    yc = 33.9
    # base de pedra
    mb.box2((21.6, yw + 0.4, F0), (30.4, yp - 0.1, F0 + 1.2), "Stone_Forge_Dark", 0.15)
    # fole: tabua de baixo, cunha de couro com dobras, tabua de cima articulada no bocal
    bl, br = 22.4, 29.4
    zb = F0 + 1.6
    h0, h1 = 0.5, 2.7
    mb.box2((bl, yc - 1.45, F0 + 1.2), (br, yc + 1.45, zb), "Wood_Plank", 0.08)
    xz_prism(mb, [(bl, zb), (br, zb), (br, zb + h1), (bl, zb + h0)], yc - 1.25, yc + 1.25, "Leather_Bellows", 0.0,
             (0.0, 0.0))
    for k in range(1, 4):
        f = k / 4
        for s in (-1, 1):
            mb.beam((bl + 0.3, yc + s * 1.35, zb + h0 * f), (br + 0.05, yc + s * 1.35, zb + h1 * f), 0.4, 0.3,
                    "Leather", 0.04)
        mb.beam((br + 0.1, yc - 1.35, zb + h1 * f), (br + 0.1, yc + 1.35, zb + h1 * f), 0.4, 0.3, "Leather", 0.04)
    lift = math.atan2(h1 - h0, br - bl)
    mb.beam((bl - 0.2, yc, zb + h0 + 0.2), (br + 0.2, yc, zb + h1 + 0.2), 3.1, 0.4, "Wood_Plank", 0.08)
    for x in (bl + 1.5, bl + 3.8, br - 0.8):
        zz = zb + h0 + (x - bl) * math.tan(lift) + 0.45
        mb.box((0.35, 3.2, 0.2), (x, yc, zz), (0, -lift, 0), "Metal_Dark", 0.0)
    mb.cyl(0.75, 1.0, (bl - 0.4, yc, zb + 0.3), (0, D(90), 0), "Metal_Brass", 10, r2=0.45, bevel=0.0)
    # balancim no cavalete + biela ate a tampa do fole + manivela no eixo que sai da parede
    px = 30.3
    for s in (-1, 1):
        mb.beam((px + 0.8, yc + s * 1.3, F0), (px, yc + s * 0.45, 10.8), 0.5, 0.5, "Wood_Dark", 0.05)
    pv = Vector((px, yc, 10.6))
    ra = Vector((26.4, yc, 9.7))
    rb = Vector((31.2, yc, 10.9))
    mb.beam(ra, rb, 0.6, 0.7, "Wood_Dark", 0.05)
    mb.rod(pv - Vector((0, 0.8, 0)), pv + Vector((0, 0.8, 0)), 0.2, "Metal_Iron", 8)
    tz = zb + h0 + (26.4 - bl) * math.tan(lift) + 0.4
    mb.beam(ra, (26.4, yc, tz), 0.22, 0.22, "Metal_Dark", 0.0)
    shaft = Vector((29.0, yw, 11.4))
    mb.rod(shaft, shaft + Vector((0, 1.5, 0)), 0.3, "Metal_Iron", 8)
    gear(mb, shaft + Vector((0, 1.1, 0)), (0, 1, 0), 1.15, 0.4, 10, "Metal_Dark", "Metal_Iron", spokes=4)
    mb.beam(shaft + Vector((0.8, 1.4, 0.4)), rb + Vector((0, -0.4, 0)), 0.2, 0.2, "Metal_Dark", 0.0)
    mb.box((1.6, 0.4, 1.6), shaft + Vector((0, 0.15, 0)), (0, 0, 0), "Metal_Iron", 0.05)
    # meia-agua
    z_w, z_p = 13.8, 11.4
    for x in (xa + 0.4, (xa + xb) / 2, xb - 0.4):
        mb.box((0.75, 0.75, z_p - F0), (x, yp, (F0 + z_p) / 2), (0, 0, rng.uniform(-0.04, 0.04)), "Wood_Dark", 0.08)
    mb.beam((xa, yp, z_p - 0.2), (xb, yp, z_p - 0.15), 0.7, 0.8, "Wood_Dark", 0.06)
    ang = math.atan2(z_w - z_p, yp - yw + 0.8)
    nsh = 6
    for i in range(nsh):
        x0_ = xa - 0.4 + i * (xb - xa + 0.8) / nsh
        x1_ = x0_ + (xb - xa + 0.8) / nsh + 0.12
        mid = Vector(((x0_ + x1_) / 2, (yw + yp + 0.9) / 2, (z_w + z_p) / 2 + 0.25))
        mb.box((x1_ - x0_, math.hypot(yp + 0.9 - yw, z_w - z_p) + 0.3, 0.3), mid,
               (-ang + rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), 0), "Roof_Forge", 0.06, tint=rng.uniform(-1, 1))
    for i in range(4):
        x = xa + 0.4 + i * (xb - xa - 0.8) / 3
        mb.beam((x, yw, z_w - 0.35), (x, yp + 0.8, z_p - 0.1), 0.35, 0.45, "Wood_Dark", 0.03)
    hanging_lantern(mb, (25.0, yp - 0.6, z_p - 0.4), name="L_BellowsHouse", chain=0.8)
    # sacos de carvao encostados
    for k, (x, y) in enumerate(((xb + 0.2, yw + 1.3), (xb + 0.1, yw + 2.7))):
        mb.ico(0.72, (x - 0.9, y, F0 + 0.75), "Rope", 1, (0.85, 0.72, 1.0), jitter=0.12)
        mb.cyl(0.26, 0.45, (x - 0.9, y, F0 + 1.6), (0, 0, 0), "Rope", 6, r2=0.38, bevel=0.0)
    mb.finish()
    col_box2(A, (21.2, yw, F0), (30.8, yp - 0.2, F0 + 4.6))
    for x in (xa + 0.4, xb - 0.4):
        col_box2(A, (x - 0.45, yp - 0.45, F0), (x + 0.45, yp + 0.45, z_p))
    col_box2(A, (px - 0.6, yc - 1.8, F0), (px + 1.3, yc + 1.8, 12.0))

    # tubo de ar do fole ate a torre (sobe acima da cabeca e entra na base)
    pm = MB("FORGE_Pipes_Air", C, rng)
    dC = Vector((CX - 18.0, CY - yc, 0)).normalized()
    p0 = Vector((bl - 0.9, yc, zb + 0.3))
    p1 = Vector((18.2, yc, zb + 0.3))
    p2 = Vector((18.2, yc, 12.6))
    p3 = Vector((CX, CY, 12.6)) - dC * (R - 0.35)
    big_pipe(pm, [p0, p1, p2, p3], 1.2, "Metal_Dark", "Metal_Copper", bend=2.2, step=7.0, n=12, bolts=5)
    gate_valve(pm, Vector((18.2, yc, 8.6)), Z, 1.1, up=(-1, 0, 0))
    pipe_clamp(pm, p2 + (p3 - p2) * 0.55, (p3 - p2).normalized(), 1.2,
               Vector(((p2 + (p3 - p2) * 0.55).x, (p2 + (p3 - p2) * 0.55).y, 8.0)))
    pm.box((1.3, 1.3, 3.4), ((p2 + (p3 - p2) * 0.55).x, (p2 + (p3 - p2) * 0.55).y, F0 + 2.0), (0, 0, 0), "Stone_Forge_Dark",
           0.1)
    pm.finish()
    col_box2(A, (16.8, yc - 1.5, F0), (21.6, yc + 1.5, F0 + 3.7))
    q = p2 + (p3 - p2) * 0.55
    col_box2(A, (q.x - 0.8, q.y - 0.8, F0), (q.x + 0.8, q.y + 0.8, F0 + 3.8))


# ------------------------------------------------------------------ torre de respiro (telhado da ala direita)
def vent_tower(rng):
    mb = MB("FORGE_Vent_Tower", C, rng)
    vx, vy = 30.9, 11.2
    hw = 1.7
    zb, zl, zt = 20.8, 28.6, 31.8
    # corpo em tabuas com montantes e cintas de ferro
    mb.box2((vx - hw + 0.1, vy - hw + 0.1, zb), (vx + hw - 0.1, vy + hw - 0.1, zl), "Wood_Plank", 0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.5, 0.5, zt - zb + 0.3), (vx + sx * (hw - 0.1), vy + sy * (hw - 0.1), (zb + zt) / 2), (0, 0, 0),
                   "Wood_Dark", 0.05)
    for z in (24.5, zl):
        mb.box2((vx - hw - 0.05, vy - hw - 0.05, z - 0.2), (vx + hw + 0.05, vy + hw + 0.05, z + 0.2), "Metal_Dark", 0.02)
    # venezianas com brilho
    mb.box2((vx - hw + 0.4, vy - hw + 0.4, zl), (vx + hw - 0.4, vy + hw - 0.4, zt), "Forge_Glow_Soft", 0.0)
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = D(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        for k in range(3):
            z = zl + 0.55 + k * 0.95
            c = Vector((vx, vy, z)) + d * (hw - 0.15)
            mb.box((0.8, 2 * hw - 0.5, 0.12), c, _louver_rot(a), "Wood_Dark", 0.0)
    # capelo piramidal + espigao
    frustum(mb, (vx, vy, zt), 2 * hw + 1.0, 2 * hw + 1.0, 0.4, 0.4, 2.6, "Roof_Forge")
    mb.box((2 * hw + 1.2, 2 * hw + 1.2, 0.3), (vx, vy, zt + 0.1), (0, 0, 0), "Metal_Dark", 0.03)
    mb.cyl(0.18, 1.6, (vx, vy, zt + 3.2), (0, 0, 0), "Metal_Dark", 6, bevel=0.0)
    mb.cyl(0.35, 0.35, (vx, vy, zt + 2.7), (0, 0, 0), "Metal_Brass", 8, bevel=0.0)
    mb.finish()

    # respiros (chamines de chapa) nos telhados das alas
    rm = MB("FORGE_Roof_Vents", C, rng)
    for (x, y, z0, h, glow) in ((-31.0, 10.8, 21.4, 8.0, True), (22.9, 27.6, 21.4, 6.2, False)):
        rm.rod((x, y, z0), (x, y, z0 + h), 0.75, "Metal_Dark", 10)
        for zz in (z0 + 2.2, z0 + h - 1.6):
            rm.rod((x, y, zz - 0.2), (x, y, zz + 0.2), 0.92, "Metal_Iron", 10)
        if glow:
            rm.rod((x, y, z0 + h - 0.9), (x, y, z0 + h - 0.3), 0.8, "Forge_Glow_Soft", 10)
        rm.cyl(1.5, 0.8, (x, y, z0 + h + 0.7), (0, 0, 0), "Metal_Dark", 10, r2=0.3, bevel=0.0)
        for k in range(3):
            a = math.tau * k / 3
            rm.beam((x + math.cos(a) * 0.7, y + math.sin(a) * 0.7, z0 + h - 0.1),
                    (x + math.cos(a) * 1.1, y + math.sin(a) * 1.1, z0 + h + 0.4), 0.14, 0.14, "Metal_Dark", 0.0)
    rm.finish()


def _louver_rot(a):
    # palheta inclinada 38 graus (borda externa para baixo) numa face com normal 'a'
    return (Matrix.Rotation(a, 3, "Z") @ Matrix.Rotation(D(38), 3, "Y")).to_euler()


# ------------------------------------------------------------------ engrenagens na parede leste da ala direita
def wall_gears(rng):
    mb = MB("FORGE_Wall_Gears", C, rng)
    ex = L.FORGE_WING_R[2]
    ay = L.WHEEL_C[1]
    az = 15.5
    gx = ex + 1.9
    gear(mb, (gx, ay, az), (1, 0, 0), 3.0, 0.8, 18, "Metal_Dark", "Metal_Iron", spokes=6)
    py = ay + 4.15
    gear(mb, (gx, py, az), (1, 0, 0), 1.45, 0.8, 9, "Metal_Iron", "Metal_Dark", spokes=4, rot0=D(10))
    mb.rod((ex - 0.3, py, az), (gx + 0.7, py, az), 0.3, "Metal_Iron", 8)
    h = 2.2
    mb.box((0.4, h, h), (ex + 0.25, py, az), (0, 0, 0), "Metal_Iron", 0.06)
    for k in range(4):
        a = math.tau * k / 4 + math.pi / 4
        rivet(mb, (ex + 0.45, py + math.cos(a) * h * 0.36, az + math.sin(a) * h * 0.36), (1, 0, 0), 0.16)
    # guarda de chapa sobre a engrenagem grande
    arc_pts = [Vector((gx, ay + math.cos(D(a)) * 3.5, az + math.sin(D(a)) * 3.5)) for a in range(25, 156, 26)]
    for p0, p1 in zip(arc_pts, arc_pts[1:]):
        mb.beam(p0, p1, 1.0, 0.18, "Metal_Rust", 0.0)
    mb.finish()


# ------------------------------------------------------------------ fachada: caixas de carvao e estoque de barras
def facade_props(rng):
    mb = MB("FORGE_Facade_Props", C, rng)
    y0 = L.FORGE_HALL[1]
    # caixa de carvao (esquerda)
    x0, x1, ya, yb = -11.4, -8.9, y0 - 2.7, y0 - 0.25
    mb.box2((x0, ya, FL), (x1, yb, FL + 0.3), "Wood_Dark", 0.03)
    for (p, q) in (((x0, ya), (x1, ya + 0.3)), ((x0, yb - 0.3), (x1, yb)), ((x0, ya), (x0 + 0.3, yb)),
                   ((x1 - 0.3, ya), (x1, yb))):
        mb.box2((p[0], p[1], FL), (q[0], q[1], FL + 1.9), "Wood_Plank", 0.05)
    for (x, y) in ((x0, ya), (x1, ya), (x0, yb), (x1, yb)):
        mb.box((0.4, 0.4, 2.0), (x, y, FL + 1.0), (0, 0, 0), "Metal_Dark", 0.02)
    for k in range(10):
        s = rng.uniform(0.6, 0.95)
        mb.rock((rng.uniform(x0 + 0.6, x1 - 0.6), rng.uniform(ya + 0.6, yb - 0.6), FL + 1.7 + rng.uniform(0, 0.35)),
                (s, s, s * 0.7), "Stone_Coal", 0, (0, 0, rng.uniform(0, 6)))
    mb.beam((x1 - 0.3, ya + 0.4, FL + 1.6), (x1 + 0.3, ya - 0.6, FL + 3.9), 0.16, 0.16, "Wood_Light", 0.0)
    mb.box((0.14, 0.8, 0.9), (x1 - 0.35, ya + 0.55, FL + 1.35), (D(-20), 0, 0), "Metal_Iron", 0.02)
    # estoque de barras de ferro + balde de tempera (direita)
    xr0, xr1 = 8.9, 11.4
    for x in (xr0 + 0.2, xr1 - 0.2):
        mb.box((0.35, 2.2, 0.35), (x, y0 - 1.5, FL + 0.9), (0, 0, 0), "Wood_Dark", 0.03)
        mb.box((0.35, 0.35, 1.9), (x, y0 - 2.5, FL + 0.95), (0, 0, 0), "Wood_Dark", 0.03)
        mb.box((0.35, 0.35, 3.2), (x, y0 - 0.5, FL + 1.6), (0, 0, 0), "Wood_Dark", 0.03)
    for k in range(6):
        x = xr0 + 0.25 + k * 0.4
        m = "Metal_Heated" if k == 2 else ("Metal_Iron" if k % 2 else "Metal_Dark")
        mb.beam((x, y0 - 2.4, FL + 1.9), (x + 0.05, y0 - 0.45, FL + 3.4), 0.25, 0.25, m, 0.0)
    barrel(mb, (10.1, y0 - 4.3, FL), 0.75, 1.5)
    mb.cyl(0.78, 0.1, (10.1, y0 - 4.3, FL + 1.35), (0, 0, 0), "Water", 10, bevel=0.0)
    mb.finish()
    col_box2(A, (x0 - 0.2, ya - 0.2, FL), (x1 + 0.2, yb, FL + 2.0))
    col_box2(A, (xr0, y0 - 2.8, FL), (xr1, y0 - 0.2, FL + 3.4))
    col_box2(A, (9.2, y0 - 5.2, FL), (11.0, y0 - 3.4, FL + 1.6))


def build(rng):
    pipes(rng)
    gallery_catwalk(rng)
    ore_lift(rng)
    coal_shed(rng)
    bellows_house(rng)
    vent_tower(rng)
    wall_gears(rng)
    facade_props(rng)
