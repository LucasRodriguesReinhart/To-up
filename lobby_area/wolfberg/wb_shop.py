# wb_shop.py - LOJA DE MOCHILAS do lobby Wolfberg: predio proprio (terreo de pedra OCO com porta em arco, vitrine em
# bay-window com toldo listrado, placa pendurada "MOCHILAS", andar enxaimel em balanco, telhado de 2 aguas com a
# cumeeira ao longo de Z e UMA agua-furtada virada para a praca, chamine) + INTERIOR PROJETADO (piso de tabuas, tapete,
# balcao em L com livro-caixa/balanca/mochila, portao de balcao, parede de fundo com prateleiras e janela entre elas,
# parede norte com ganchos + manequins, bau aberto com rolos de couro e corda, candelabro de ferro, 2 lampioes, vigas
# do forro, escada + mezanino cenografico com guarda-corpo, janelas REAIS para a luz entrar).
# Contrato (wb_layout.SHOP): x 54..80, z -22..4, piso Y_SHOP 7,4; porta na face OESTE em z -9 (6 x 9); vitrine z -18,5..
# -12,5; NPC (72, -9) olha -X atras do balcao (tampo em x 67); jogador (62, -9) olha +X. Chao livre em x 60..64 e
# 70..74, z -12..-6. Vidro: as janelas do terreo sao aberturas reais (luz na previa); os vidros vao num objeto
# WB_Shop_Glass__WB_Glass escondido no render (hide_render) mas exportado (Glass no Roblox).
import math
import random

import bmesh
import fm_lib
import wb_lib as W
import wb_layout as L
from mathutils import Matrix, Vector
from wb_kit import (Fr, bx, bb, beam, cyl, lathe, text, window, timber_face, roof, chimney, lantern, lantern_wall,
                    hanging_sign, crate, sack, barrel, ST, STD, TB, PK, PKL, RF, RFD, PL, PLO, IR, GL, TXT, RAD)
from wb_lib import RB, V

PREFIX = "WB_Shop_"
COLL = "05_SERVICES"
LE, LED = "WB_Leather", "WB_LeatherDark"
C_RED, C_BLUE, C_GREEN, C_GOLD, C_PURPLE, C_CREAM = ("WB_Cloth_Red", "WB_Cloth_Blue", "WB_Cloth_Green", "WB_Cloth_Gold",
                                                     "WB_Cloth_Purple", "WB_Cloth_Cream")
BRASS, ROPE, PAPER, GLOW, DARK = "WB_Brass", "WB_Rope", "WB_Paper", "WB_LampGlow", "WB_Dark"

# cotas (locais: piso da loja = 0 = Y_SHOP)
S = L.SHOP
CX, CZ = (S["x0"] + S["x1"]) / 2, (S["z0"] + S["z1"]) / 2          # 67, -9
Y0 = L.Y_SHOP
WD = S["x1"] - S["x0"]            # 26 (quadrado)
HW = WD / 2                       # 13
WALL = 1.2                        # espessura do terreo
HI = HW - WALL                    # 11,8: meia largura interna
GH = L.SHOP_WALL_H                # 13: pe-direito interno
SLAB0, SLAB1 = GH, GH + 0.6       # forro (piso do andar) 13..13,6
JET = 0.9                         # balanco do andar
UW = 1.0                          # espessura das paredes do andar
HWU = HW + JET                    # 13,9
EAVE = L.SHOP_EAVE_Y - Y0         # 22
PITCH = 42.0
DOOR_W, DOOR_H = L.SHOP_DOOR_W, L.SHOP_DOOR_H     # 6 x 9
MEZ = 6.9                         # cota do mezanino (topo da laje = 7,3)
NICHE_TOP = 11.3                  # topo do nicho da mochila sobre a porta


# ------------------------------------------------------------------ helpers de frame
def LX(F, xr, zr):
    """x local (ao longo de F.t) do ponto Roblox (xr, zr)"""
    return (RB(xr, zr, 0.0) - V((F.o.x, F.o.y, 0.0))).dot(F.t)


def LY(F, xr, zr):
    return (RB(xr, zr, 0.0) - V((F.o.x, F.o.y, 0.0))).dot(F.f)


def span(F, a, b):
    """(x0, x1) locais ordenados de 2 pontos Roblox (x, z) na face F"""
    p, q = LX(F, *a), LX(F, *b)
    return (min(p, q), max(p, q))


def face_in(F, side):
    """frame da face INTERNA (origem no meio da face interna, na base, olhando para DENTRO da loja)"""
    if side == "W":
        return Fr(F.p(0, HI, 0), (-F.f.x, -F.f.y))
    if side == "E":
        return Fr(F.p(0, -HI, 0), (F.f.x, F.f.y))
    if side == "N":
        return Fr(F.p(HI, 0, 0), (-F.t.x, -F.t.y))
    return Fr(F.p(-HI, 0, 0), (F.t.x, F.t.y))


def colr(lo, hi):
    """caixa de colisao a partir de 2 cantos ROBLOX (x, y, z)"""
    return fm_lib.col_box2("Shop", RB(lo[0], lo[2], lo[1]), RB(hi[0], hi[2], hi[1]))


def wall_open(b, Ff, x0, x1, z0, z1, depth, openings, m):
    """parede na face Ff (plano da face em y=0, massa de y=-depth a 0) com aberturas retangulares reais
    [(ox0, ox1, oz0, oz1)] (sem sobreposicao em x)"""
    xa = x0
    for (ox0, ox1, oz0, oz1) in sorted(openings):
        ox0, ox1 = max(ox0, x0), min(ox1, x1)
        if ox0 - xa > 0.01:
            bb(b, Ff, xa, ox0, -depth, 0.0, z0, z1, m)
        if oz0 - z0 > 0.01:
            bb(b, Ff, ox0, ox1, -depth, 0.0, z0, oz0, m)
        if z1 - oz1 > 0.01:
            bb(b, Ff, ox0, ox1, -depth, 0.0, oz1, z1, m)
        xa = ox1
    if x1 - xa > 0.01:
        bb(b, Ff, xa, x1, -depth, 0.0, z0, z1, m)


def win_open(b, g, Ff, cx, zc, ww, wh, depth=WALL, shutters=True, sill=True, mull=True):
    """janela do terreo numa ABERTURA real (cx, zc, ww x wh) da parede de espessura depth: caixilho de madeira no vao,
    cruzeta, vidro (no Build g escondido), peitoril de pedra fora, tabua de peitoril dentro, venezianas"""
    fw = 0.35
    ya, yb = -depth + 0.3, -0.3                      # caixilho recuado 0,3 dos dois lados
    x0, x1, z0, z1 = cx - ww / 2, cx + ww / 2, zc - wh / 2, zc + wh / 2
    bb(b, Ff, x0 - 0.05, x0 + fw, ya, yb, z0 - 0.05, z1 + 0.05, TB)
    bb(b, Ff, x1 - fw, x1 + 0.05, ya, yb, z0 - 0.05, z1 + 0.05, TB)
    bb(b, Ff, x0, x1, ya, yb, z1 - fw, z1 + 0.05, TB)
    bb(b, Ff, x0, x1, ya, yb, z0 - 0.05, z0 + fw, TB)
    ym = (ya + yb) / 2
    if mull:
        bb(b, Ff, cx - 0.1, cx + 0.1, ym - 0.12, ym + 0.12, z0 + fw, z1 - fw, TB)
        bb(b, Ff, x0 + fw, x1 - fw, ym - 0.12, ym + 0.12, zc - 0.1, zc + 0.1, TB)
    if g is not None:
        bb(g, Ff, x0 + fw, x1 - fw, ym - 0.04, ym + 0.04, z0 + fw, z1 - fw, GL)
    if sill:
        bb(b, Ff, x0 - 0.35, x1 + 0.35, -0.3, 0.45, z0 - 0.5, z0 + 0.12, STD)            # peitoril de pedra (fora)
        bb(b, Ff, x0 - 0.25, x1 + 0.25, -depth - 0.3, -depth + 0.2, z0 - 0.1, z0 + 0.2, PK)   # tabua (dentro)
    if shutters:
        sw = ww * 0.46
        for s in (-1, 1):
            xa = cx + s * (ww / 2 + 0.12)
            lo, hi = min(xa, xa + s * sw), max(xa, xa + s * sw)
            bb(b, Ff, lo, hi, 0.08, 0.3, z0 - 0.1, z1 + 0.1, PK)
            bb(b, Ff, lo + 0.1, hi - 0.1, 0.3, 0.42, z0 + 0.5, z0 + 0.8, TB)
            bb(b, Ff, lo + 0.1, hi - 0.1, 0.3, 0.42, z1 - 0.8, z1 - 0.5, TB)


def flowerbox(b, Ff, x0, x1, zb, seed=0, flowers="WB_FlowerRed"):
    """floreira sob um peitoril (zb = base do peitoril): caixa de tabuas + folhas e flores"""
    bb(b, Ff, x0 - 0.2, x1 + 0.2, 0.0, 0.8, zb - 0.75, zb - 0.1, PK)
    for xa in (x0 - 0.1, x1 - 0.2):
        beam(b, Ff, (xa + 0.15, 0.1, zb - 1.5), (xa + 0.15, 0.7, zb - 0.7), 0.2, 0.2, TB)
    r = random.Random(("fbox", seed, round(x0, 2)).__repr__())
    n = max(3, int((x1 - x0) / 0.55))
    for k in range(n):
        xa = x0 + (k + 0.5) * (x1 - x0) / n
        b.sphere(Ff.p(xa + r.uniform(-0.1, 0.1), 0.4 + r.uniform(-0.15, 0.15), zb - 0.05 + r.uniform(0.05, 0.3)),
                 r.uniform(0.26, 0.36), "WB_Leaf", seg=6)
        b.sphere(Ff.p(xa + r.uniform(-0.15, 0.15), 0.42 + r.uniform(-0.1, 0.1), zb + 0.25 + r.uniform(0.0, 0.25)),
                 r.uniform(0.18, 0.26), flowers if r.random() < 0.75 else "WB_FlowerYellow", seg=6)


def arch_ring(b, Ff, cx, zc, ri, ro, y0, y1, m, n=9):
    """meio-anel de aduelas (arco) na face Ff, centro (cx, zc), de y0 a y1"""
    bm = bmesh.new()
    for k in range(n):
        a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
        quad = [(cx + ro * math.cos(a0), zc + ro * math.sin(a0)), (cx + ro * math.cos(a1), zc + ro * math.sin(a1)),
                (cx + ri * math.cos(a1), zc + ri * math.sin(a1)), (cx + ri * math.cos(a0), zc + ri * math.sin(a0))]
        v0 = [bm.verts.new(Ff.p(px, y0, pz)) for (px, pz) in quad]
        v1 = [bm.verts.new(Ff.p(px, y1, pz)) for (px, pz) in quad]
        bm.faces.new(list(reversed(v0)))
        bm.faces.new(v1)
        for i in range(4):
            bm.faces.new((v0[i], v0[(i + 1) % 4], v1[(i + 1) % 4], v1[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.001)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


# ------------------------------------------------------------------ props
def backpack(b, F, x, y, z, color=LE, s=1.0, turn=0.0, flap=LED, hang=False):
    """mochila: corpo com bevel, aba, bolso frontal, tira com fivela, 2 alcas atras, alca de mao em cima.
    Frente (aba/bolso) para +y do frame; base em z (ou topo da alca de mao em z se hang)"""
    h = 2.6 * s
    Fb = F.sub(x, y, z - h - 0.3 * s if hang else z, turn)
    bx(b, Fb, 0.0, 0.0, h / 2, 2.0 * s, 1.1 * s, h, color, bevel=0.15 * s)
    bx(b, Fb, 0.0, 0.3 * s, h - 0.4 * s, 2.06 * s, 0.9 * s, 0.9 * s, flap, bevel=0.1 * s)      # aba
    bx(b, Fb, 0.0, 0.62 * s, h * 0.38, 1.2 * s, 0.4 * s, h * 0.38, flap, bevel=0.08 * s)       # bolso
    bb(b, Fb, -0.16 * s, 0.16 * s, 0.7 * s, 0.9 * s, h * 0.3, h - 0.3 * s, LED)                # tira
    bb(b, Fb, -0.22 * s, 0.22 * s, 0.86 * s, 0.98 * s, h * 0.42, h * 0.42 + 0.3 * s, BRASS)   # fivela
    for sx in (-1, 1):
        bb(b, Fb, sx * 0.6 * s - 0.15 * s, sx * 0.6 * s + 0.15 * s, -0.78 * s, -0.5 * s, 0.3 * s, h - 0.4 * s, LED)
    bb(b, Fb, -0.4 * s, 0.4 * s, -0.3 * s, -0.08 * s, h - 0.15 * s, h + 0.3 * s, LED)         # alca de mao
    return Fb


def mannequin(b, F, x, y, turn=0.0, color=C_RED):
    """manequim de madeira: base, haste, torso torneado, pescoco e cabeca; veste mochila nas costas (-y)"""
    Fm = F.sub(x, y, 0, turn)
    cyl(b, Fm, (0, 0, -0.1), (0, 0, 0.35), 1.05, TB, seg=12)
    cyl(b, Fm, (0, 0, 0.3), (0, 0, 3.4), 0.18, TB, seg=6)
    lathe(b, Fm, 0, 0, [(0.55, 3.3), (0.95, 3.8), (1.05, 4.6), (1.0, 5.6), (0.85, 6.3), (0.5, 6.7), (0.28, 6.8),
                        (0.28, 7.15), (0.4, 7.2)], PKL, 10)
    b.sphere(Fm.p(0, 0, 7.75), 0.58, PKL, seg=8)
    backpack(b, Fm, 0.0, -1.1, 3.5, color, 0.9, turn=180.0)
    for sx in (-1, 1):                                                                         # alcas na frente
        bb(b, Fm, sx * 0.55 - 0.14, sx * 0.55 + 0.14, 0.78, 1.0, 3.9, 6.2, LED)


def scale_prop(b, F, x, y, z):
    """balanca de pratos: base e coluna de ferro, travessao, 2 pratos de latao com correntes, pesos"""
    Fs = F.sub(x, y, z, 0)
    cyl(b, Fs, (0, 0, 0.0), (0, 0, 0.18), 0.55, IR, seg=10)
    cyl(b, Fs, (0, 0, 0.15), (0, 0, 2.3), 0.09, IR, seg=6)
    bb(b, Fs, -1.3, 1.3, -0.07, 0.07, 2.2, 2.34, IR)
    b.sphere(Fs.p(0, 0, 2.4), 0.14, BRASS, seg=6)
    for sx in (-1, 1):
        px = sx * 1.15
        lathe(b, Fs, px, 0, [(0.1, 0.0), (0.62, 0.0), (0.68, 0.14), (0.58, 0.17), (0.1, 0.07)], BRASS, 10, z0=0.7)
        for k in range(3):
            a = 2 * math.pi * k / 3
            cyl(b, Fs, (px + 0.55 * math.cos(a), 0.55 * math.sin(a), 0.84), (px, 0, 2.2), 0.025, IR, seg=4)
    cyl(b, Fs, (-1.15, 0.0, 0.87), (-1.15, 0.0, 1.25), 0.22, IR, seg=8)                    # peso no prato
    cyl(b, Fs, (0.75, -0.75, 0.0), (0.75, -0.75, 0.32), 0.2, IR, seg=8)
    cyl(b, Fs, (1.15, -0.85, 0.0), (1.15, -0.85, 0.22), 0.16, IR, seg=8)


def ledger(b, F, x, y, z, turn=0.0):
    """livro-caixa aberto (capa de couro escuro, 2 blocos de paginas), tinteiro e pena"""
    Fl = F.sub(x, y, z, turn)
    bx(b, Fl, 0.0, 0.0, 0.08, 2.5, 1.7, 0.16, LED, bevel=0.03)
    for sx in (-1, 1):
        bx(b, Fl, sx * 0.6, 0.0, 0.31, 1.12, 1.5, 0.3, PAPER, bevel=0.02)
    bb(b, Fl, -0.08, 0.08, -0.85, 0.85, 0.16, 0.52, LED)                                     # lombada
    cyl(b, Fl, (1.9, 0.2, 0.0), (1.9, 0.2, 0.42), 0.22, DARK, seg=8)                          # tinteiro
    cyl(b, Fl, (1.9, 0.2, 0.4), (2.5, -0.5, 1.3), 0.03, C_CREAM, seg=4)                       # pena
    cyl(b, Fl, (2.2, -0.15, 0.92), (2.5, -0.5, 1.3), 0.11, C_CREAM, seg=4, r1=0.02)


def chest(b, F, x, y, turn=0.0, open_deg=108.0, rope_side=1):
    """bau de tabuas com cantoneiras de ferro, tampa aberta (girada no fundo -y), rolos de couro dentro, corda ao lado"""
    Fc = F.sub(x, y, 0, turn)
    w, d, h, lid = 3.2, 2.2, 1.9, 0.55
    bx(b, Fc, 0, 0, h / 2 - 0.05, w, d, h + 0.1, PK, bevel=0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(b, Fc, sx * w / 2 - 0.14, sx * w / 2 + 0.14, sy * d / 2 - 0.14, sy * d / 2 + 0.14, 0.0, h + 0.05, IR)
    bb(b, Fc, -w / 2 - 0.06, w / 2 + 0.06, -d / 2 - 0.06, d / 2 + 0.06, h - 0.3, h + 0.02, IR)
    bb(b, Fc, -w / 2 - 0.06, w / 2 + 0.06, -d / 2 - 0.06, d / 2 + 0.06, 0.0, 0.3, IR)
    bb(b, Fc, -0.3, 0.3, d / 2 - 0.02, d / 2 + 0.12, h - 0.75, h - 0.25, BRASS)                  # fecho
    a = RAD(open_deg)
    cy = -d / 2 + (d / 2) * math.cos(a) - math.sin(a) * lid / 2
    cz = h + (d / 2) * math.sin(a) + math.cos(a) * lid / 2
    bx(b, Fc, 0, cy, cz, w, d, lid, PK, bevel=0.04, rx=open_deg)
    bx(b, Fc, 0, cy - math.sin(a) * 0.1, cz + math.cos(a) * 0.1, w + 0.12, 0.3, lid + 0.1, IR, rx=open_deg)
    for (lx, ly, lz, r) in ((-0.9, -0.2, 0.9, 0.42), (0.1, -0.1, 0.95, 0.45), (-0.4, 0.3, 1.7, 0.4), (0.9, 0.2, 1.0, 0.38)):
        cyl(b, Fc, (lx, ly - 0.75, lz), (lx, ly + 0.75, lz), r, LE, seg=10)
        cyl(b, Fc, (lx, ly - 0.78, lz), (lx, ly + 0.78, lz), r * 0.55, LED, seg=8)
    # corda enrolada no chao ao lado (anel de 10 segmentos + ponta)
    Fr_ = Fc.sub(rope_side * (w / 2 + 1.3), -0.2, 0, 0)
    n = 10
    pts = [(0.9 * math.cos(2 * math.pi * k / n), 0.9 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        beam(b, Fr_, (pts[k][0], pts[k][1], 0.3), (pts[(k + 1) % n][0], pts[(k + 1) % n][1], 0.3), 0.5, 0.6, ROPE)
    beam(b, Fr_, (-0.6, 0.2, 0.75), (0.6, -0.2, 0.75), 0.3, 0.3, ROPE)


def chandelier(b, F, x, y, z_ring, z_beam, name=None):
    """candelabro de ferro: aro octogonal com 8 velas (vela + chama neon), correntes ate a viga; luz de dia quente"""
    Fc = F.sub(x, y, 0, 0)
    n = 8
    r = 2.3
    pts = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    for k in range(n):
        beam(b, Fc, (pts[k][0], pts[k][1], z_ring), (pts[(k + 1) % n][0], pts[(k + 1) % n][1], z_ring), 0.26, 0.32, IR)
        px, py = pts[k]
        cyl(b, Fc, (px, py, z_ring + 0.1), (px, py, z_ring + 0.32), 0.26, IR, seg=8)
        cyl(b, Fc, (px, py, z_ring + 0.3), (px, py, z_ring + 1.05), 0.15, C_CREAM, seg=6)
        lathe(b, Fc, px, py, [(0.11, 0.0), (0.16, 0.18), (0.06, 0.5), (0.0, 0.62)], GLOW, 6, z0=z_ring + 1.02)
    cyl(b, Fc, (0, 0, z_ring - 0.3), (0, 0, z_ring + 0.4), 0.35, IR, seg=8)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.4
        beam(b, Fc, (r * math.cos(a), r * math.sin(a), z_ring + 0.3), (0, 0, z_ring + 2.2), 0.08, 0.08, IR)
    cyl(b, Fc, (0, 0, z_ring + 2.0), (0, 0, z_beam + 0.2), 0.07, IR, seg=4)
    if name:
        fm_lib.light(name, "POINT", Fc.p(0, 0, z_ring + 1.2), 150.0, (1.0, 0.78, 0.5), 1.2)


def hook(b, F, x, z, y0=0.1):
    """gancho de ferro na parede (frame olhando para dentro, parede em y=0): placa + braco + ponta"""
    bb(b, F, x - 0.22, x + 0.22, y0 - 0.25, y0 + 0.06, z - 0.3, z + 0.3, IR)
    bb(b, F, x - 0.07, x + 0.07, y0, y0 + 0.75, z - 0.07, z + 0.07, IR)
    bb(b, F, x - 0.07, x + 0.07, y0 + 0.62, y0 + 0.75, z, z + 0.42, IR)


def railing(b, F, a, c, z0, h=2.6, posts=3, every=0.75):
    """guarda-corpo de a ate c (locais, no plano z0): postes, corrimao e balaustres"""
    a, c = V((a[0], a[1], z0)), V((c[0], c[1], z0))
    d = c - a
    n = d.length
    u = d / n
    for k in range(posts):
        p = a + u * (0.15 + (n - 0.3) * k / max(1, posts - 1))
        bb(b, Fr(F.p(p.x, p.y, 0), (F.f.x, F.f.y)), -0.15, 0.15, -0.15, 0.15, z0, z0 + h, TB)
    b.beam(F.p(a.x, a.y, z0 + h - 0.15), F.p(c.x, c.y, z0 + h - 0.15), 0.3, 0.3, TB)
    m = max(1, int(n / every))
    for k in range(1, m):
        p = a + u * (n * k / m)
        b.beam(F.p(p.x, p.y, z0), F.p(p.x, p.y, z0 + h - 0.3), 0.12, 0.12, PK)


# ------------------------------------------------------------------ o predio
def build(coll=COLL):
    rng = random.Random(1207)
    b = W.Build("WB_Shop_Building", coll)
    g = W.Build("WB_Shop_Glass", coll)
    F = Fr.rbx(CX, CZ, Y0, -1.0, 0.0)          # centro da loja, olhando a praca (-X); +x local = norte (-Z)
    FF, FB, FR, FL = (F.face(s, WD, WD) for s in ("F", "B", "R", "L"))       # oeste, leste, norte, sul (fora)
    IW, IE, IN_, IS = (face_in(F, s) for s in ("W", "E", "N", "S"))          # faces internas (olham para dentro)
    FFu, FBu, FRu, FLu = (F.face(s, 2 * HWU, 2 * HWU) for s in ("F", "B", "R", "L"))   # andar em balanco
    XW = S["x0"]
    ZN, ZS = S["z0"], S["z1"]
    XE = S["x1"]
    Z0 = -0.3                                  # base das paredes (dentro do soco)
    # ---------------------------------------------------------------- base: soco, piso, soleira
    bb(b, F, -HW - 0.4, HW + 0.4, -HW - 0.4, HW + 0.4, -1.4, -0.35, STD)
    bb(b, F, -HI, HI, -HI, HI, -0.6, 0.0, PK)                                       # piso de tabuas
    dx0, dx1 = span(FF, (XW, CZ - DOOR_W / 2), (XW, CZ + DOOR_W / 2))                # vao da porta (-3..3)
    bb(b, FF, dx0, dx1, -WALL - 0.05, 0.0, -0.6, 0.0, PK)                           # piso do vao
    bb(b, FF, dx0 - 1.0, dx1 + 1.0, 0.0, 1.8, -0.9, 0.0, STD, bevel=0.06)           # soleira (2 degraus de 0,2)
    bb(b, FF, dx0 - 1.4, dx1 + 1.4, 1.8, 3.0, -0.9, -0.2, STD, bevel=0.06)
    for Ff in (FB, FR, FL):
        bb(b, Ff, -HW - 0.4, HW + 0.4, 0.0, 0.4, -1.2, 0.9, STD)                    # faixa do soco
    bb(b, FF, -HW - 0.4, dx0 - 0.9, 0.0, 0.4, -1.2, 0.9, STD)
    bb(b, FF, dx1 + 0.9, HW + 0.4, 0.0, 0.4, -1.2, 0.9, STD)
    # ---------------------------------------------------------------- terreo de pedra OCO com aberturas reais
    bx0, bx1 = span(FF, (XW, L.SHOP_WINDOW[1]), (XW, L.SHOP_WINDOW[2]))             # vitrine (3,5..9,5)
    BZ0, BZ1, BD = 2.4, 7.6, 1.2
    ops = {}
    wx0, wx1 = span(FF, (XW, -1.0), (XW, 2.0))                                      # janela ao sul da porta
    ops["W"] = [(dx0, dx1, Z0 - 0.1, NICHE_TOP), (bx0, bx1, BZ0, BZ1), (wx0, wx1, 5.2, 8.4)]
    ex0, ex1 = span(FB, (XE, -11.5), (XE, -6.5))
    e1x0, e1x1 = span(FB, (XE, -19.0), (XE, -14.0))                                  # clerestorios sobre as estantes
    e2x0, e2x1 = span(FB, (XE, -4.0), (XE, 1.0))
    ops["E"] = [(ex0, ex1, 4.5, 9.5), (e1x0, e1x1, 10.0, 11.7), (e2x0, e2x1, 10.0, 11.7)]
    nx0, nx1 = span(FR, (70.0, ZN), (74.0, ZN))
    cx0_, cx1_ = span(FR, (58.5, ZN), (62.5, ZN))                                    # clerestorio sobre os ganchos
    ops["N"] = [(nx0, nx1, 4.5, 8.5), (cx0_, cx1_, 9.9, 11.7)]
    s1x0, s1x1 = span(FL, (57.5, ZS), (60.5, ZS))
    s2x0, s2x1 = span(FL, (71.0, ZS), (75.5, ZS))
    ops["S"] = [(s1x0, s1x1, 5.0, 8.6), (s2x0, s2x1, 2.6, 6.2)]
    wall_open(b, FF, -HW, HW, Z0, SLAB1 - 0.1, WALL, ops["W"], ST)
    wall_open(b, FB, -HW, HW, Z0, SLAB1 - 0.1, WALL, ops["E"], ST)
    wall_open(b, FR, -HW + WALL, HW - WALL, Z0, SLAB1 - 0.1, WALL, ops["N"], ST)
    wall_open(b, FL, -HW + WALL, HW - WALL, Z0, SLAB1 - 0.1, WALL, ops["S"], ST)
    # faixa sobre a porta com o NICHO da mochila (recuo 0,6 entre dx0..dx1, z 9..11,3)
    bb(b, FF, dx0, dx1, -WALL, -0.6, DOOR_H, NICHE_TOP, ST)
    bb(b, FF, dx0, -2.6, -0.6, 0.0, DOOR_H, NICHE_TOP, ST)
    bb(b, FF, 2.6, dx1, -0.6, 0.0, DOOR_H, NICHE_TOP, ST)
    # janelas do terreo (aberturas com caixilho; vidro no Build escondido)
    win_open(b, g, FB, (ex0 + ex1) / 2, 7.0, ex1 - ex0, 5.0)
    win_open(b, g, FR, (nx0 + nx1) / 2, 6.5, nx1 - nx0, 4.0)
    win_open(b, g, FR, (cx0_ + cx1_) / 2, 10.8, cx1_ - cx0_, 1.8, mull=False, shutters=False)
    for (a_, c_) in ((e1x0, e1x1), (e2x0, e2x1)):
        win_open(b, g, FB, (a_ + c_) / 2, 10.85, c_ - a_, 1.7, mull=False, shutters=False)
    win_open(b, g, FF, (wx0 + wx1) / 2, 6.8, wx1 - wx0, 3.2)
    flowerbox(b, FF, wx0, wx1, 4.7, "w")
    flowerbox(b, FL, s1x0, s1x1, 4.5, "s1")
    flowerbox(b, FL, s2x0, s2x1, 2.1, "s2")
    flowerbox(b, FR, nx0, nx1, 4.0, "n")
    win_open(b, g, FL, (s1x0 + s1x1) / 2, 6.8, s1x1 - s1x0, 3.6)
    win_open(b, g, FL, (s2x0 + s2x1) / 2, 4.4, s2x1 - s2x0, 3.6)
    # ---------------------------------------------------------------- porta em arco (aberta: folhas encostadas dentro)
    jw = 0.9
    for s in (-1, 1):
        xj = s * (DOOR_W / 2 + jw / 2)
        bb(b, FF, xj - jw / 2, xj + jw / 2, -0.3, 0.35, -0.3, DOOR_H - 0.4, STD)
    arch_ring(b, FF, 0.0, DOOR_H - 0.4, DOOR_W / 2, DOOR_W / 2 + jw, -0.3, 0.35, STD)
    bb(b, FF, -2.3, 2.3, -0.75, 0.25, DOOR_H + 0.05, DOOR_H + 0.3, PK)                 # prateleira do nicho
    backpack(b, FF, 0.0, -0.2, DOOR_H + 0.3, C_RED, 0.6, turn=0.0)                   # a mochila-icone
    bb(b, FF, dx0 - 0.6, dx1 + 0.6, -WALL - 0.35, -WALL + 0.1, DOOR_H, DOOR_H + 0.7, TB)   # verga de madeira (dentro)
    for s in (-1, 1):
        Fl = FF.sub(s * DOOR_W / 2, -WALL - 0.1, 0, -s * 12.0)
        lo, hi = (0.15, 3.0) if s > 0 else (-3.0, -0.15)
        bb(b, Fl, lo, hi, -0.28, -0.02, 0.15, DOOR_H - 0.45, PK)
        for z in (DOOR_H * 0.22, DOOR_H * 0.7):
            bb(b, Fl, lo + 0.15, hi - 0.15, -0.4, -0.26, z - 0.22, z + 0.22, TB)
            xa = (hi - 0.3) if s > 0 else (lo + 0.3)
            bb(b, Fl, min(xa, xa - s * 1.2), max(xa, xa - s * 1.2), -0.48, -0.38, z - 0.12, z + 0.12, IR)
        b.sphere(Fl.p(lo + 0.7 if s > 0 else hi - 0.7, -0.45, DOOR_H * 0.5), 0.17, IR, seg=6)
    # ---------------------------------------------------------------- vitrine (bay window) + toldo listrado
    bb(b, FF, bx0 - 0.3, bx1 + 0.3, -0.9, BD, BZ0 - 0.1, BZ0 + 0.15, PK)                 # piso/peitoril (topo 2,55)
    bb(b, FF, bx0 - 0.3, bx1 + 0.3, 0.0, BD - 0.1, 1.0, BZ0 - 0.1, STD)                  # misula de pedra
    bb(b, FF, bx0 + 0.3, bx1 - 0.3, 0.0, BD - 0.5, 0.2, 1.0, STD)
    bb(b, FF, bx0 - 0.3, bx1 + 0.3, -0.3, BD, BZ1, BZ1 + 0.4, TB)                        # teto/verga
    for xa in (bx0 - 0.3, bx1 - 0.05):
        bb(b, FF, xa, xa + 0.35, BD - 0.35, BD, BZ0, BZ1 + 0.4, TB)                      # montantes da frente
        bb(b, FF, xa, xa + 0.35, -0.2, 0.3, BZ0, BZ1 + 0.4, TB)                          # montantes na parede
        bb(b, FF, xa, xa + 0.35, 0.3, BD - 0.35, BZ0 + 0.05, BZ0 + 0.4, TB)               # travessas das laterais
        bb(b, FF, xa, xa + 0.35, 0.3, BD - 0.35, BZ1 - 0.25, BZ1, TB)
    bb(b, FF, bx0, bx1, BD - 0.35, BD, BZ0 + 0.05, BZ0 + 0.4, TB)
    for xa in (bx0 + 1.9, bx1 - 1.9):
        bb(b, FF, xa - 0.12, xa + 0.12, BD - 0.3, BD - 0.05, BZ0 + 0.3, BZ1, TB)
    bb(g, FF, bx0 + 0.05, bx1 - 0.05, BD - 0.22, BD - 0.14, BZ0 + 0.3, BZ1, GL)
    bb(g, FF, bx0 - 0.18, bx0 - 0.1, 0.3, BD - 0.35, BZ0 + 0.3, BZ1 - 0.2, GL)
    bb(g, FF, bx1 + 0.1, bx1 + 0.18, 0.3, BD - 0.35, BZ0 + 0.3, BZ1 - 0.2, GL)
    for k, (xa, col) in enumerate(((bx0 + 1.1, C_RED), ((bx0 + bx1) / 2, C_BLUE), (bx1 - 1.1, C_GREEN))):
        backpack(b, FF, xa, 0.42, BZ0 + 0.15, col, 0.85, turn=(-10.0, 0.0, 10.0)[k])
    # toldo listrado (vermelho) com aba e bracos de ferro
    aw_c, aw_w = (bx0 + bx1) / 2, bx1 - bx0 + 1.0
    bx(b, FF, aw_c, 1.25, 9.05, aw_w, 2.8, 0.25, "WB_CanvasRed", rx=-24.0)
    for k in range(int(aw_w / 0.96)):
        xa = aw_c - aw_w / 2 + 0.48 + k * 0.96
        bx(b, FF, xa, 2.5, 8.05, 0.92, 0.22, 0.85, "WB_CanvasRed")
    for xa in (bx0 + 0.2, bx1 - 0.2):
        beam(b, FF, (xa, 0.1, 7.1), (xa, 2.35, 8.35), 0.18, 0.18, IR)
        bb(b, FF, xa - 0.18, xa + 0.18, 0.0, 0.35, 6.8, 9.7, IR)
    # ---------------------------------------------------------------- placa pendurada, lanterna da porta
    hanging_sign(b, FF, -8.6, 9.3, "MOCHILAS")
    # tabuleta na fachada sobre o toldo (legivel da praca)
    bb(b, FF, bx0 - 0.9, bx1 + 0.9, 0.05, 0.35, 10.1, 12.1, PK, bevel=0.06)
    for (z0_, z1_) in ((9.95, 10.3), (11.9, 12.25)):
        bb(b, FF, bx0 - 1.05, bx1 + 1.05, 0.0, 0.45, z0_, z1_, TB)
    for xa in (bx0 - 1.05, bx1 + 0.7):
        bb(b, FF, xa, xa + 0.35, 0.0, 0.45, 9.95, 12.25, TB)
    text(b, FF, "MOCHILAS", 1.0, TXT, (bx0 + bx1) / 2, 0.37, 11.1, 0.12, bold=True)
    lantern_wall(b, FF, -4.6, 10.3, "L_WB_Lamp_Shop_Door")
    # ---------------------------------------------------------------- forro / piso do andar (balanco) + cachorros
    bb(b, F, -HWU, HWU, -HWU, HWU, SLAB0, SLAB1, PK)
    for Ff in (FFu, FBu, FRu, FLu):
        n = 9
        for k in range(n):
            xa = -HWU + (k + 0.5) * 2 * HWU / n
            bb(b, Ff, xa - 0.3, xa + 0.3, -JET - 0.8, 0.1, SLAB0 - 0.6, SLAB0 + 0.1, TB)
    # ---------------------------------------------------------------- andar enxaimel (oco, janelas reais com vidro)
    zc = SLAB1 + (EAVE - SLAB1) * 0.5
    bays = [-HWU, -10.5, -6.9, -1.7, 1.7, 6.9, 10.5, HWU]
    wins = {"F": (1, 3, 5), "B": (1, 5), "R": (1, 5), "L": (1, 5)}
    flowers = {"F": "WB_FlowerRed", "R": "WB_FlowerPink", "L": "WB_FlowerYellow", "B": None}
    for side, Ff in (("F", FFu), ("B", FBu), ("R", FRu), ("L", FLu)):
        ks = wins[side]
        cxs = [(bays[k] + bays[k + 1]) / 2 for k in ks]
        x0, x1 = (-HWU, HWU) if side in ("F", "B") else (-HWU + UW, HWU - UW)
        wall_open(b, Ff, x0, x1, SLAB1 - 0.1, EAVE + 0.1, UW, [(c - 1.2, c + 1.2, zc - 1.3, zc + 1.3) for c in cxs], PL)
        timber_face(b, Ff, -HWU + 0.2, HWU - 0.2, SLAB1, EAVE, bays=bays, skip=set(ks))
        for i, c in enumerate(cxs):
            window(b, Ff, c, zc, 2.4, 2.6, shutters=True, flowers=flowers[side], box=flowers[side] is not None,
                   seed="shop%s%d" % (side, i))
    # ---------------------------------------------------------------- telhado (cumeeira ao longo de Z, agua-furtada p/ praca), chamine
    zr = roof(b, F, 2 * HWU, 2 * HWU, EAVE, PITCH, over=1.4, thick=0.7, m=RF, mr=RFD, gable=True, pl=PL,
              gable_timber=True, fascia=True, dormers=1, seed="shop", flowers="WB_FlowerRed")
    chx, chy = -7.0, -9.5
    chimney(b, F, chx, chy, SLAB1 - 0.5, 33.0, w=2.4)
    fm_lib.marker("VFX_Smoke_House_SHOP", F.p(chx, chy, 34.0), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "smoke_thin", "rate": 2})
    # lenha empilhada e caixote encostados na face norte; barril de agua no canto NE
    zg = L.Y_GRASS - Y0                                                                 # -0,6: grama em volta
    Fw = Fr(F.p(LX(F, 65.0, ZN - 1.4), LY(F, 65.0, ZN - 1.4), zg), (F.t.x, F.t.y))      # olha -Z (para fora)
    for (lx_, lz_) in ((-1.5, 0.42), (-0.5, 0.42), (0.5, 0.42), (1.5, 0.42), (-1.0, 1.15), (0.0, 1.15), (1.0, 1.15),
                       (-0.5, 1.88), (0.5, 1.88)):
        cyl(b, Fw, (lx_, -1.0, lz_), (lx_, 1.0, lz_), 0.42, "WB_Bark", seg=7)
    crate(b, Fw, 3.4, 0.2, 2.0, turn=8.0)
    barrel(b, Fr(F.p(LX(F, 78.4, ZN - 1.6), LY(F, 78.4, ZN - 1.6), zg), (F.t.x, F.t.y)), 0, 0, 1.0, 2.5)
    fm_lib.col_box("Shop", (6.6, 2.6, 2.6), F.p(LX(F, 65.8, ZN - 1.4), LY(F, 65.8, ZN - 1.4), 1.0), (0, 0, F.yaw()))
    fm_lib.col_box("Shop", (2.4, 2.4, 2.6), F.p(LX(F, 78.4, ZN - 1.6), LY(F, 78.4, ZN - 1.6), 1.0), (0, 0, F.yaw()))
    # ================================================================ INTERIOR
    # reboco interno (paineis com as mesmas aberturas), postes de canto, frechal, postes intermediarios
    pz0, pz1 = 0.5, SLAB0 - 0.9
    for side, Fi, Fo in (("W", IW, FF), ("E", IE, FB), ("N", IN_, FR), ("S", IS, FL)):
        Fp = Fi.sub(0, 0.1, 0)
        ops_in = []
        for (ox0, ox1, oz0, oz1) in ops[side]:
            # mapeia a abertura da face externa para a interna (x invertido)
            ops_in.append((-ox1, -ox0, oz0 if oz0 > Z0 else pz0 - 0.1, min(oz1, DOOR_H) if (oz0 <= Z0) else oz1))
        wall_open(b, Fp, -HI, HI, pz0, pz1, 0.2, ops_in, PL)
        bb(b, Fi, -HI - 0.05, HI + 0.05, -0.15, 0.4, pz1 - 0.2, pz1 + 0.3, TB)        # frechal
        bb(b, Fi, -HI - 0.05, HI + 0.05, -0.15, 0.35, 0.0, pz0 + 0.1, TB)              # rodape
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(b, F, sx * HI - 0.45 * sx, sx * HI + 0.08 * sx, sy * HI - 0.45 * sy, sy * HI + 0.08 * sy, 0.0, pz1, TB)
    posts = {"W": [LX(IW, XW, -12.25), LX(IW, XW, -2.3)], "E": [LX(IE, XE, -12.0), LX(IE, XE, -6.0)],
             "N": [LX(IN_, 69.0, ZN), LX(IN_, 75.6, ZN)], "S": [LX(IS, 62.5, ZS), LX(IS, 68.5, ZS), LX(IS, 77.0, ZS)]}
    for side, Fi in (("W", IW), ("E", IE), ("N", IN_), ("S", IS)):
        for xa in posts[side]:
            bb(b, Fi, xa - 0.22, xa + 0.22, -0.15, 0.4, 0.0, pz1 - 0.1, TB)
    # forro: vigas transversais (leste-oeste) e viga mestra (norte-sul) sobre o balcao
    for xa in (-10.0, -5.0, 0.0, 5.0, 10.0):
        bb(b, F, xa - 0.45, xa + 0.45, -HI - 0.5, HI + 0.5, SLAB0 - 0.9, SLAB0 + 0.1, TB)
    bb(b, F, -HI - 0.5, HI + 0.5, -0.45, 0.45, SLAB0 - 1.7, SLAB0 - 0.75, TB)
    # tapete na frente do balcao (centrado no jogador)
    ry0, ry1 = sorted((LY(F, 57.5, -9.0), LY(F, 64.5, -9.0)))
    rx0, rx1 = sorted((LX(F, 60.0, -14.0), LX(F, 60.0, -4.0)))
    bb(b, F, rx0, rx1, ry0, ry1, 0.04, 0.12, C_RED, bevel=0.03)
    bb(b, F, rx0 + 0.6, rx1 - 0.6, ry0 + 0.6, ry1 - 0.6, 0.12, 0.16, C_GOLD, bevel=0.02)
    bb(b, F, rx0 + 1.0, rx1 - 1.0, ry0 + 1.0, ry1 - 1.0, 0.16, 0.19, C_RED, bevel=0.01)
    # ---------------------------------------------------------------- balcao em L (tampo em x 67), portao de balcao
    cx0, cx1 = sorted((LX(F, L.SHOP_COUNTER_X, -20.0), LX(F, L.SHOP_COUNTER_X, 0.4)))       # -9,4..11
    cy0, cy1 = sorted((LY(F, 65.5, CZ), LY(F, 68.5, CZ)))                                   # -1,5..1,5
    bb(b, F, cx0, cx1, cy0, cy1, -0.1, 3.3, PK)
    bb(b, F, cx0 - 0.4, cx1 + 0.4, cy0 - 0.4, cy1 + 0.4, 3.3, 3.7, TB, bevel=0.06)
    bb(b, F, cx0, cx1, cy1 - 0.1, cy1 + 0.14, 0.0, 0.5, TB)
    for xa in (cx0 + 0.3, cx0 + 5.4, cx0 + 10.5, cx0 + 15.6, cx1 - 0.3):
        bb(b, F, xa - 0.22, xa + 0.22, cy1 - 0.2, cy1 + 0.18, 0.0, 3.3, TB)
    lx0, lx1 = sorted((LX(F, 70.0, -20.0), LX(F, 70.0, -17.5)))                             # perna curta (norte)
    ly0, ly1 = sorted((LY(F, 68.5, CZ), LY(F, 77.0, CZ)))
    bb(b, F, lx0, lx1, ly0, ly1, -0.1, 3.3, PK)
    bb(b, F, lx0 - 0.4, lx1 + 0.4, ly0, cy0 - 0.4, 3.3, 3.7, TB, bevel=0.06)
    # portao de balcao (ripas) fechando a passagem z 0,4..2,8
    gx0, gx1 = sorted((LX(F, 67.0, 0.4), LX(F, 67.0, 2.75)))
    for z in (0.6, 2.75):
        bb(b, F, gx0 - 0.05, gx1 + 0.05, -0.1, 0.1, z - 0.15, z + 0.15, TB)
    for xa in (gx0 + 0.3, gx0 + 0.85, gx0 + 1.4, gx0 + 1.95):
        bb(b, F, xa - 0.16, xa + 0.16, -0.07, 0.07, 0.3, 3.15, PK)
    for z in (0.9, 2.5):
        bb(b, F, gx0 - 0.35, gx0 + 0.1, -0.14, 0.14, z - 0.12, z + 0.12, IR)
    # sobre o balcao: livro-caixa (frente do NPC), mochila em exposicao, balanca na perna curta, saco
    ledger(b, F, LX(F, 67.0, -6.3), LY(F, 66.9, CZ), 3.7, turn=-8.0)
    backpack(b, F, LX(F, 67.0, -13.6), 0.0, 3.7, C_GOLD, 0.9, turn=18.0)
    scale_prop(b, F, LX(F, 72.5, -18.75), LY(F, 72.5, CZ), 3.7)
    sack(b, F, LX(F, 76.0, -18.6), LY(F, 76.0, CZ), 0.9, z=3.7)
    # banquinho do vendedor (fora do chao livre)
    cyl(b, F, (LX(F, 70.5, -3.6), LY(F, 70.5, CZ), 0.0), (LX(F, 70.5, -3.6), LY(F, 70.5, CZ), 2.2), 0.7, PK, seg=8)
    cyl(b, F, (LX(F, 70.5, -3.6), LY(F, 70.5, CZ), 2.1), (LX(F, 70.5, -3.6), LY(F, 70.5, CZ), 2.35), 0.85, PKL, seg=10)
    # ---------------------------------------------------------------- parede de fundo: 2 estantes com janela no meio
    shelf_h = (2.8, 6.0, 9.2)
    units = [(LX(IE, XE, -20.0), LX(IE, XE, -12.5)), (LX(IE, XE, -5.5), LX(IE, XE, 2.0))]
    for (ua, ub) in units:
        ua, ub = min(ua, ub), max(ua, ub)
        for xa in (ua, (ua + ub) / 2, ub):
            bb(b, IE, xa - 0.22, xa + 0.22, -0.15, 1.55, 0.0, shelf_h[-1] + 0.5, TB)
        for h in shelf_h:
            bb(b, IE, ua - 0.22, ub + 0.22, -0.15, 1.45, h - 0.25, h, PK)
    packs = [(-16.3, 0, C_BLUE, -6), (-13.7, 0, LE, 5), (-19.4, 1, C_RED, 0), (-16.4, 1, C_GREEN, -8),
             (-13.6, 1, C_PURPLE, 6), (-18.4, 2, C_GOLD, 0), (-14.6, 2, LE, 4),
             (-4.4, 0, C_GREEN, 5), (-0.6, 0, C_BLUE, -4), (-4.2, 1, C_PURPLE, 0), (-1.6, 1, C_RED, 7), (0.9, 1, LE, -5),
             (-3.6, 2, C_BLUE, 0), (0.2, 2, C_GREEN, 0)]
    for (zr, lvl, col, tw) in packs:
        backpack(b, IE, LX(IE, XE, zr), 0.66, shelf_h[lvl], col, 0.9, turn=tw)
    cyl(b, IE, (LX(IE, XE, -18.2) - 0.7, 0.7, 9.55), (LX(IE, XE, -18.2) + 0.7, 0.7, 9.55), 0.33, C_CREAM, seg=8)
    cyl(b, IE, (LX(IE, XE, 1.2) - 0.7, 0.7, 6.35), (LX(IE, XE, 1.2) + 0.7, 0.7, 6.35), 0.33, C_BLUE, seg=8)
    # ---------------------------------------------------------------- parede norte: trilho de ganchos, manequins, lampiao
    hx0, hx1 = sorted((LX(IN_, 56.0, ZN), LX(IN_, 66.0, ZN)))
    bb(b, IN_, hx0, hx1, -0.15, 0.3, 8.8, 9.3, TB)
    for xr in (56.6, 58.8, 61.0, 63.2, 65.4):
        hook(b, IN_, LX(IN_, xr, ZN), 9.05, y0=0.3)
    for xr, col in ((56.6, C_PURPLE), (61.0, C_GREEN), (65.4, C_BLUE)):
        backpack(b, IN_, LX(IN_, xr, ZN), 1.03, 9.2, col, 0.9, turn=0.0, hang=True)
    for xr, col in ((58.6, C_RED), (63.2, C_BLUE)):
        mannequin(b, IN_, LX(IN_, xr, ZN), LY(IN_, xr, -19.0), turn=0.0, color=col)
    lantern_wall(b, IN_, LX(IN_, 67.3, ZN), 9.4, "L_WB_Shop_Lamp_N")
    # vaso: meio barril com arbusto no canto NW
    Fv = Fr(F.p(LX(F, 56.4, -19.5), LY(F, 56.4, -19.5), 0), (F.f.x, F.f.y))
    lathe(b, Fv, 0, 0, [(0.78, 0.0), (0.9, 0.5), (0.9, 1.3), (0.82, 1.5)], PK, 10)
    cyl(b, Fv, (0, 0, 0.4), (0, 0, 0.64), 0.93, IR, seg=10)
    cyl(b, Fv, (0, 0, 1.15), (0, 0, 1.39), 0.93, IR, seg=10)
    for k in range(4):
        a = 2 * math.pi * k / 4 + 0.3
        b.sphere(Fv.p(0.35 * math.cos(a), 0.35 * math.sin(a), 2.0 + 0.2 * (k % 2)), 0.62, "WB_Leaf", seg=7)
    b.sphere(Fv.p(0, 0, 2.5), 0.55, "WB_Leaf", seg=7)
    # ---------------------------------------------------------------- parede sul (dentro): lampiao noturno sobre o bau
    lantern_wall(b, IS, LX(IS, 72.6, ZS), 9.2, "L_WB_Lamp_Shop_Wall")
    # ---------------------------------------------------------------- escada + mezanino cenografico (parede sul)
    sx0, sx1 = LX(IS, 56.5, ZS), LX(IS, 65.0, ZS)            # -10,5..-2
    sy1 = LY(IS, 65.0, -0.4)                                  # 3,2 (largura da escada, da parede para dentro)
    nst = 12
    run, rise = (sx1 - sx0) / nst, MEZ / nst
    for i in range(nst):
        xa = sx0 + i * run
        zt = (i + 1) * rise
        bb(b, IS, xa - 0.05, xa + run + 0.1, -0.05, sy1, zt - 0.3, zt, PK, bevel=0.02)
        bb(b, IS, xa - 0.05, xa + 0.1, -0.05, sy1 - 0.1, max(0.0, zt - rise - 0.05), zt - 0.3, PKL)
    b.beam(IS.p(sx0 - 0.1, sy1 + 0.02, -0.55), IS.p(sx1 + 0.05, sy1 + 0.02, MEZ - 0.55), 0.3, 0.9, TB)      # longarina
    rail_pts = [(sx0 + (i + 0.5) * run, sy1 + 0.17, (i + 1) * rise) for i in (0, 4, 8, 11)]
    for (xa, ya, za) in rail_pts:
        bb(b, IS, xa - 0.14, xa + 0.14, ya - 0.14, ya + 0.14, za, za + 2.7, TB)
    b.beam(IS.p(rail_pts[0][0], rail_pts[0][1], rail_pts[0][2] + 2.55), IS.p(rail_pts[-1][0], rail_pts[-1][1], rail_pts[-1][2] + 2.55),
           0.3, 0.26, TB)
    for i in range(nst):
        xa = sx0 + (i + 0.5) * run
        if i in (0, 4, 8, 11):
            continue
        b.beam(IS.p(xa, sy1 + 0.17, (i + 1) * rise), IS.p(xa, sy1 + 0.17, (i + 1) * rise + 2.4), 0.12, 0.12, PK)
    # debaixo da escada: barril, caixote, saco
    barrel(b, IS, LX(IS, 63.0, ZS), 1.7, 1.0, 2.4)
    crate(b, IS, LX(IS, 61.0, ZS), 2.3, 1.6, turn=-14.0)
    sack(b, IS, LX(IS, 59.3, ZS), 1.4, 1.3)
    # mezanino: laje, vigas de borda, maos-francesas, guarda-corpo, caixotes
    mx0, mx1 = sx1, LX(IS, 72.0, ZS)                          # -2..5
    my1 = LY(IS, 72.0, -4.5)                                  # 7,3
    bb(b, IS, mx0 - 0.1, mx1, -0.15, my1, MEZ, MEZ + 0.4, PK)
    bb(b, IS, mx0 - 0.1, mx1, my1 - 0.5, my1 + 0.05, MEZ - 0.55, MEZ + 0.05, TB)
    bb(b, IS, mx0 - 0.3, mx0 + 0.2, -0.1, my1 + 0.05, MEZ - 0.55, MEZ + 0.05, TB)
    for xa in (LX(IS, 66.0, ZS), LX(IS, 69.8, ZS)):
        b.beam(IS.p(xa, 0.0, 3.4), IS.p(xa, my1 - 0.3, MEZ - 0.35), 0.5, 0.5, TB)
    railing(b, IS, (mx0, my1 - 0.2), (mx1 - 0.15, my1 - 0.2), MEZ + 0.4, posts=3)
    railing(b, IS, (mx0 + 0.05, my1 - 0.2), (mx0 + 0.05, sy1 + 0.2), MEZ + 0.4, posts=2)
    crate(b, IS, mx1 - 1.3, 1.4, 2.0, z=MEZ + 0.4, turn=10.0)
    crate(b, IS, mx1 - 3.4, 1.2, 1.6, z=MEZ + 0.4, turn=-6.0)
    sack(b, IS, mx1 - 2.0, 3.3, 1.2, z=MEZ + 0.4)
    # bau aberto no canto SE (rolos de couro + corda), rolo de couro encostado
    chest(b, IS, LX(IS, 74.9, ZS), LY(IS, 74.9, 0.6), turn=0.0, rope_side=-1)
    cyl(b, IS, (LX(IS, 76.9, ZS), 0.9, 0.0), (LX(IS, 76.9, ZS) + 0.1, 0.3, 3.4), 0.38, LE, seg=8)
    # ---------------------------------------------------------------- candelabro sobre o balcao (luz de dia)
    chandelier(b, F, LX(F, 66.5, CZ), LY(F, 66.5, CZ), 9.3, SLAB0 - 1.7, "L_WB_Shop_Chandelier")
    # ---------------------------------------------------------------- fechamento
    objs = b.finish()
    gl = g.finish()
    for o in gl:
        o.hide_render = True
        try:
            o.visible_shadow = False
        except Exception:
            pass
    objs += gl
    # ---------------------------------------------------------------- marcadores de gameplay
    def yaw(fx, fz):
        return round(math.degrees(math.atan2(-fx, -fz)), 2)
    nx, nz = L.SHOP_NPC
    px, pz = L.SHOP_PLAYER
    M = "15_GAMEPLAY_MARKERS"
    fm_lib.marker("NPC_Shop", RB(nx, nz, Y0), (0, 0, 0), 2.0, "PLAIN_AXES", M,
                  {"npc": "npc vendedor ", "prompt": "LojaPrompt (Comprar, 12/18)", "face_x": -1.0, "face_z": 0.0,
                   "yaw_deg": yaw(-1, 0), "nota": "atras do balcao (tampo em x 67), chao livre x 70..74 z -12..-6"})
    fm_lib.marker("INTERACT_Shop", RB(nx, nz, Y0 + 3.2), (0, 0, 0), 2.0, "PLAIN_AXES", M, {"prompt_range": 12})
    fm_lib.marker("PLAYER_INTERACT_Shop", RB(px, pz, Y0), (0, 0, 0), 2.0, "PLAIN_AXES", M,
                  {"face_x": 1.0, "face_z": 0.0, "yaw_deg": yaw(1, 0), "nota": "chao livre e plano x 60..64 z -12..-6"})
    fm_lib.marker("PADLOJA_Shop", RB(px, pz, Y0 + 0.05), (0, 0, 0), 2.0, "PLAIN_AXES", M,
                  {"alvo": "workspace.LojaMochilas.PadLoja (10x0,2x10, so marca)", "face_x": 1.0, "face_z": 0.0,
                   "yaw_deg": yaw(1, 0)})
    fm_lib.marker("DOOR_Shop", RB(L.SHOP_DOOR[0], L.SHOP_DOOR[1], Y0), (0, 0, 0), 2.0, "PLAIN_AXES", M,
                  {"largura": DOOR_W, "altura": DOOR_H, "face_x": -1.0, "face_z": 0.0, "yaw_deg": yaw(-1, 0)})
    # ---------------------------------------------------------------- colisao (Roblox: x, y, z)
    T = Y0 + SLAB1
    XI0, XI1 = XW + WALL, XE - WALL          # 55,2 / 78,8
    ZI0, ZI1 = ZN + WALL, ZS - WALL          # -20,8 / 2,8
    dz0, dz1 = CZ - DOOR_W / 2, CZ + DOOR_W / 2
    colr((XW, Y0 - 0.5, ZN), (XI0, T, dz0))                        # parede oeste norte da porta
    colr((XW, Y0 - 0.5, dz1), (XI0, T, ZS))                        # parede oeste sul da porta
    colr((XW, Y0 + DOOR_H, dz0), (XI0, T, dz1))                    # verga sobre a porta
    colr((XI1, Y0 - 0.5, ZN), (XE, T, ZS))                         # parede leste
    colr((XI0, Y0 - 0.5, ZN), (XI1, T, ZI0))                       # parede norte
    colr((XI0, Y0 - 0.5, ZI1), (XI1, T, ZS))                       # parede sul
    colr((XW - BD - 0.1, Y0 - 0.5, L.SHOP_WINDOW[1] - 0.3), (XW, Y0 + 9.8, L.SHOP_WINDOW[2] + 0.3))   # vitrine (fora)
    colr((XI0, Y0 - 1.0, ZI0), (XI1, Y0, ZI1))                     # piso interno
    colr((XW, Y0 - 1.0, dz0), (XI0, Y0, dz1))                      # piso do vao
    colr((XW - 1.8, Y0 - 1.0, dz0 - 1.0), (XW, Y0, dz1 + 1.0))     # soleira
    colr((XW - 3.0, Y0 - 1.0, dz0 - 1.4), (XW - 1.8, Y0 - 0.2, dz1 + 1.4))
    colr((65.1, Y0, -20.8), (68.9, Y0 + 3.7, 2.8))                 # balcao + portao (fecha a passagem)
    colr((68.5, Y0, -20.8), (77.2, Y0 + 3.7, -17.5))               # perna curta do L
    colr((77.2, Y0, -20.8), (78.8, Y0 + 10.0, -12.3))              # estante norte
    colr((77.2, Y0, -5.7), (78.8, Y0 + 10.0, 2.8))                 # estante sul
    for xr in (58.6, 63.2):
        colr((xr - 1.1, Y0, -20.8), (xr + 1.1, Y0 + 8.4, -17.9))   # manequins
    colr((56.3, Y0, -0.6), (65.2, Y0 + 7.4, 2.8))                  # escada (bloqueada)
    colr((65.0, Y0 + MEZ, -4.6), (72.2, Y0 + MEZ + 0.4, 2.8))      # laje do mezanino
    colr((73.2, Y0, -0.6), (76.6, Y0 + 3.2, 2.8))                  # bau
    colr((70.8, Y0, 0.4), (73.2, Y0 + 0.8, 2.6))                   # corda
    colr((69.6, Y0, -4.5), (71.4, Y0 + 2.4, -2.7))                 # banquinho
    colr((55.2, Y0, -20.8), (57.6, Y0 + 2.6, -18.3))               # vaso
    return objs


# cameras de QA: (nome, olho Roblox (x, y, z), alvo, lente mm)
CAMS = [
    ("CAM_WB_Shop_Praca", (28.0, 16.0, -3.0), (66.0, 18.0, -9.0), 22),
    ("CAM_WB_Shop_Fachada", (36.0, 13.0, 0.0), (66.0, 17.0, -9.0), 24),
    ("CAM_WB_Shop_Porta", (56.0, 12.4, -9.0), (74.0, 11.0, -9.0), 18),
    ("CAM_WB_Shop_Canto", (57.6, 12.6, -2.8), (74.0, 10.0, -16.0), 20),
    ("CAM_WB_Shop_Sul", (110.0, 32.0, 30.0), (66.0, 18.0, -8.0), 24),
    ("CAM_WB_Shop_Vitrine", (66.5, 12.0, -3.0), (56.0, 10.5, -17.0), 22),
    ("CAM_WB_Shop_Norte", (38.0, 17.0, -36.0), (68.0, 14.0, -8.0), 26),
]
