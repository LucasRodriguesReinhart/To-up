# k_madeira.py - pecas de MADEIRA PINTADA do kit: coluna, arquitrave pintada (caihua simplificado) com queti, prancha
# pingbanfang, viga do alpendre, vaos de parede (janela "bu bu jin", porta com pregos e pushou, parede com janela octogonal), placa.
# Origem local das pecas: piso do terraco em z=0. VAO = 9 studs entre eixos de coluna.
import math
from mathutils import Vector
from k_core import *

VAO = 9.0
H_COL = 13.0          # topo da coluna / da arquitrave
Z_ARQ = 11.3          # fundo da arquitrave
R_COL = 1.2

def coluna():
    """fuste com entasis sobre o tambor (z 1.5), sapata de bronze, faixa pintada jade com filetes de ouro no topo."""
    B = Builder('KIT_coluna', 101)
    L = H_COL - 1.5
    B.add(xf(t_lathe([(0, 0), (R_COL, 0), (R_COL + .04, L * .30), (R_COL - .03, L * .62), (R_COL - .13, L * .9), (R_COL - .16, L), (0, L)], 28), loc=(0, 0, 1.5)), 'verm', .5)
    B.add(xf(t_lathe([(R_COL - .02, 0), (R_COL + .16, .06), (R_COL + .16, .5), (R_COL + .1, .62), (R_COL + .02, .66)], 28), loc=(0, 0, 1.5)), 'bronze', .5)
    zb = H_COL - 2.6
    B.add(xf(t_lathe([(R_COL - .12, 0), (R_COL - .02, .04), (R_COL - .04, 1.5), (R_COL - .15, 1.54)], 28), loc=(0, 0, zb)), 'jade', .5)
    for z in (zb - .06, zb + 1.42):
        B.add(xf(t_lathe([(R_COL - .13, 0), (R_COL + .06, .04), (R_COL + .06, .2), (R_COL - .13, .24)], 28), loc=(0, 0, z)), 'ouro', .5)
    for a in range(4):                                         # quatro losangos dourados na faixa (leitura a media distancia)
        ang = math.radians(45 + 90 * a); r = R_COL - .02
        B.add(xf(t_prism([(0, -.42), (.3, 0), (0, .42), (-.3, 0)], 'Y', -.06, .06, bev=.02), rot=(0, 0, math.degrees(ang) + 90), loc=(r * math.cos(ang), r * math.sin(ang), zb + .74)), 'ouro', .6)
    return B

QUETI = [(1.0, Z_ARQ), (4.15, Z_ARQ), (4.15, Z_ARQ - .24), (3.78, Z_ARQ - .32), (3.58, Z_ARQ - .54), (3.22, Z_ARQ - .58), (2.98, Z_ARQ - .8),
         (2.62, Z_ARQ - .83), (2.38, Z_ARQ - 1.1), (1.98, Z_ARQ - 1.14), (1.78, Z_ARQ - 1.46), (1.38, Z_ARQ - 1.56), (1.0, Z_ARQ - 1.92)]

def _queti(B, sx):
    poly = [(sx * a, b) for a, b in QUETI]
    if sx > 0: poly = poly[::-1]
    B.add(t_prism(poly, 'Y', -.28, .28, bev=.06), 'jade', .55)
    cx = sum(a for a, b in poly) / len(poly); cz = sum(b for a, b in poly) / len(poly)
    inner = [(cx + (a - cx) * .62, cz + (b - cz) * .62 + .1) for a, b in poly]
    B.add(t_prism(inner, 'Y', -.34, .34, bev=.04), 'ouro', .6)

def arquitrave():
    """da e'fang de um vao (eixo a eixo, ao longo de X, centrada em y=0) + dois queti. Pintura: campo jade, filetes de
    ouro, caixas de extremidade (gutou) com rosacea, cartucho central (fangxin) vermelho com moldura de ouro."""
    B = Builder('KIT_arquitrave', 102)
    h = VAO / 2
    B.add(t_box(-h, h, -.62, .62, Z_ARQ, H_COL, bev=.09), 'jade', .5)
    for s in (-1, 1):
        y0, y1 = (s * .62, s * .69) if s > 0 else (s * .69, s * .62)
        for z in (Z_ARQ + .16, H_COL - .3):
            B.add(t_box(-h + 1.1, h - 1.1, min(y0, y1), max(y0, y1), z, z + .14), 'ouro', .6)
        for sx in (-1, 1):                                       # gutou: caixa vermelha com rosacea
            xa, xb = sorted((sx * (h - 1.25), sx * (h - 2.75)))
            B.add(t_box(xa, xb, min(y0, y1), max(y0, y1) + (.02 if s > 0 else -.02), Z_ARQ + .42, H_COL - .42, bev=.03), 'verm', .55)
            for k, (rr, key, d) in enumerate(((.46, 'ouro', .09), (.3, 'jadeE', .13), (.13, 'ouro', .17))):
                B.add(xf(t_lathe([(0, 0), (rr, 0), (rr * .8, d), (0, d)], 14), rot=(-90 * s, 0, 0), loc=((xa + xb) / 2, s * .64, (Z_ARQ + H_COL) / 2)), key, .6)
            xl = sx * (h - 3.0)
            B.add(t_box(min(xl, xl + sx * .14), max(xl, xl + sx * .14), min(y0, y1), max(y0, y1), Z_ARQ + .3, H_COL - .44), 'ouro', .6)
        fx = [(-2.35, 0), (-1.95, .44), (1.95, .44), (2.35, 0), (1.95, -.44), (-1.95, -.44)]
        zc = (Z_ARQ + H_COL) / 2 - .02
        B.add(xf(t_prism([(a * 1.07, b * 1.2) for a, b in fx], 'Y', 0, .1), loc=(0, s * .62 if s > 0 else s * .62 - .1, zc)), 'ouro', .6)
        B.add(xf(t_prism(fx, 'Y', 0, .16, bev=.03), loc=(0, s * .62 if s > 0 else s * .62 - .16, zc)), 'vermS', .5)
        B.add(xf(t_prism([(0, -.26), (.5, 0), (0, .26), (-.5, 0)], 'Y', 0, .22, bev=.02), loc=(0, s * .62 if s > 0 else s * .62 - .22, zc)), 'ouro', .7)
    _queti(B, 1); _queti(B, -1)
    return B

def prancha():
    """pingbanfang: prancha larga sobre colunas e arquitrave, onde pousam os dougong."""
    B = Builder('KIT_prancha', 103)
    B.add(t_box(-VAO / 2, VAO / 2, -1.2, 1.2, H_COL, H_COL + .5, bev=.08), 'jadeE', .5)
    for s in (-1, 1):
        B.add(t_box(-VAO / 2, VAO / 2, min(s * 1.2, s * 1.26), max(s * 1.2, s * 1.26), H_COL + .16, H_COL + .32), 'ouro', .6)
    return B

def viga_alpendre(L=7.0):
    """baotou liang: viga que amarra a coluna do alpendre (y=-L) a coluna da parede (y=0). Vermelha, pontas jade."""
    B = Builder('KIT_viga_alpendre', 104)
    B.add(t_box(-.55, .55, -L, 0, 10.2, 11.7, bev=.1), 'verm', .5)
    for ya, yb in ((-L + 1.0, -L + 2.3), (-2.3, -1.0)):
        B.add(t_box(-.6, .6, ya, yb, 10.16, 11.74, bev=.04), 'jade', .55)
        for y in (ya - .02, yb - .1): B.add(t_box(-.63, .63, y, y + .12, 10.14, 11.76), 'ouro', .6)
    return B

# ---- vaos de parede ---------------------------------------------------------------------------------------------
def _rodape(B, w=VAO, zt=2.8, t=.75):
    """kanqiang: duas fiadas de blocos chanfrados + peitoril moldurado."""
    h1 = zt * .5
    for r, cuts in enumerate(([-w / 2, -w / 6, w / 6, w / 2], [-w / 2, -w / 3, 0, w / 3, w / 2])):
        for a, b in zip(cuts, cuts[1:]):
            B.add(t_box(a + .04, b - .04, -t, t, r * h1 + (.0 if r == 0 else .04), (r + 1) * h1 - .04, bev=.09, seg=2), 'pedra')
    B.add(t_box(-w / 2, w / 2, -t + .12, t - .12, 0, zt), 'junta', .2)
    B.add(t_box(-w / 2, w / 2, -t - .16, t + .16, zt, zt + .36, bev=.1, seg=3), 'pedra', .66)

def _bubujin(B, x0, x1, z0, z1, y, d=.26, bar=.24, key='mad'):
    """trelica 'bu bu jin' (passo a passo): retangulos aninhados ligados por barras curtas. Tudo em geometria."""
    def rect(a0, a1, b0, b1):
        for (p, q, r, s) in ((a0, a1, b0, b0 + bar), (a0, a1, b1 - bar, b1), (a0, a0 + bar, b0, b1), (a1 - bar, a1, b0, b1)):
            B.add(t_box(p, q, y - d, y, r, s, bev=.035), key, .5)
    w, h = x1 - x0, z1 - z0
    i1 = min(w, h) * .2; i2 = min(w, h) * .4
    rect(x0, x1, z0, z1); rect(x0 + i1, x1 - i1, z0 + i1, z1 - i1); rect(x0 + i2, x1 - i2, z0 + i2, z1 - i2)
    xm, zm = (x0 + x1) / 2, (z0 + z1) / 2
    for zz in (z0 + h * .3, zm, z1 - h * .3):                    # ligacoes horizontais
        for (p, q) in ((x0, x0 + i1), (x1 - i1, x1)): B.add(t_box(p, q, y - d, y, zz - bar / 2, zz + bar / 2, bev=.035), key, .5)
    for xx in (xm,):
        for (r, s) in ((z0, z0 + i1), (z1 - i1, z1), (z0 + i1, z0 + i2), (z1 - i2, z1 - i1)): B.add(t_box(xx - bar / 2, xx + bar / 2, y - d, y, r, s, bev=.035), key, .5)
    for zz in (z0 + h * .22, z1 - h * .22):
        for (p, q) in ((x0 + i1, x0 + i2), (x1 - i2, x1 - i1)): B.add(t_box(p, q, y - d, y, zz - bar / 2, zz + bar / 2, bev=.035), key, .5)

def vao_janela():
    """vao com rodape de pedra e duas folhas de janela trelicada sobre fundo creme. Frente = -Y."""
    B = Builder('KIT_vao_janela', 111)
    _rodape(B)
    z0, z1 = 3.16, Z_ARQ; w = VAO / 2 - R_COL + .25
    B.add(t_box(-w, w, -.1, .1, z0, z1), 'creme', .5)                       # "papel" atras da trelica
    for (a, b, c, d) in ((-w, w, z0, z0 + .55), (-w, w, z1 - .6, z1), (-w, -w + .55, z0, z1), (w - .55, w, z0, z1), (-.3, .3, z0, z1)):
        B.add(t_box(a, b, -.4, .4, c, d, bev=.08), 'verm', .5)
    for (a, b) in ((-w + .55, -.3), (.3, w - .55)):
        for s in (-1, 1):
            if s > 0: _bubujin(B, a + .12, b - .12, z0 + .67, z1 - .72, -.1)
            else:
                # verso: grade simples (so para nao ficar liso visto de dentro)
                B.add(t_box(a + .12, b - .12, .1, .3, (z0 + z1) / 2 - .12, (z0 + z1) / 2 + .12), 'mad', .5)
    return B

def _prego(B, x, y, z, r=.2):
    B.add(xf(t_lathe([(0, 0), (r, 0), (r * .92, r * .4), (r * .6, r * .75), (0, r * .9)], 8), rot=(90, 0, 0), loc=(x, y, z)), 'ouro', .6)

def vao_porta():
    """vao de porta: soleira, ombreiras, duas folhas com moldura, pregos dourados 5x4 e pushou de bronze, verga com 4 menzan,
    bandeira trelicada. Frente = -Y."""
    B = Builder('KIT_vao_porta', 112)
    w = VAO / 2 - R_COL + .25; zt = 9.2
    B.add(t_box(-w, w, -.45, .45, 0, .5, bev=.1), 'mad', .45)                                        # soleira
    for sx in (-1, 1):
        a, b = sorted((sx * w, sx * (w - .62)))
        B.add(t_box(a, b, -.42, .42, .5, Z_ARQ, bev=.08), 'verm', .5)                                # ombreira
        xa, xb = sorted((sx * .04, sx * (w - .62)))
        B.add(t_box(xa, xb, -.2, .16, .5, zt, bev=.05), 'verm', .55)                                  # folha
        for (p, q, r, s) in ((xa + .12, xb - .12, .7, 1.0), (xa + .12, xb - .12, zt - .5, zt - .2), (xa + .12, xa + .42, .7, zt - .2), (xb - .42, xb - .12, .7, zt - .2)):
            B.add(t_box(p, q, -.3, -.2, r, s, bev=.04), 'vermS', .5)                                  # moldura da folha
        B.add(t_box(xa + .42, xb - .42, -.26, -.2, 4.95, 5.2, bev=.03), 'vermS', .5)
        cols = 4; rows = 5
        for i in range(cols):
            for j in range(rows):
                px = xa + .8 + i * ((xb - xa) - 1.6) / (cols - 1); pz = 5.75 + j * (zt - 1.1 - 5.75) / (rows - 1)
                _prego(B, px, -.2, pz)
        for i in range(cols):
            for j in range(2):
                px = xa + .8 + i * ((xb - xa) - 1.6) / (cols - 1); _prego(B, px, -.2, 1.6 + j * 1.3)
        # pushou: disco, focinho, orelhas e argola
        px = sx * .95; pz = 4.2
        B.add(xf(t_lathe([(0, 0), (.62, 0), (.66, .08), (.5, .2), (.3, .3), (0, .34)], 14), rot=(90, 0, 0), loc=(px, -.2, pz)), 'bronze', .5)
        for e in (-1, 1): B.add(xf(t_blob(.2, (1, .7, 1.2), 1), loc=(px + e * .4, -.34, pz + .45)), 'bronze', .55)
        B.add(xf(t_blob(.22, (1.2, 1, .9), 1), loc=(px, -.52, pz - .08)), 'bronze', .6)
        ring = [Vector((px + .46 * math.cos(math.radians(a)), -.56, pz - .62 + .46 * math.sin(math.radians(a)))) for a in range(0, 360, 30)]
        ring.append(ring[0])
        B.add(t_tube(ring, [.085] * len(ring), 8, cap=False), 'bronze', .65)
    B.add(t_box(-w, w, -.46, .46, zt, zt + .7, bev=.08), 'verm', .5)                                   # verga
    for i in range(4):                                                                                  # menzan hexagonais
        px = -w + 1.15 + i * (2 * w - 2.3) / 3
        hexa = [(.4 * math.cos(math.radians(30 + 60 * k)), .4 * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
        B.add(xf(t_prism(hexa, 'Y', -.78, -.46, bev=.05), loc=(px, 0, zt + .35)), 'ouro', .6)
        B.add(xf(t_prism([(a * .5, b * .5) for a, b in hexa], 'Y', -.84, -.78, bev=.02), loc=(px, 0, zt + .35)), 'vermS', .5)
    B.add(t_box(-w + .62, w - .62, -.1, .1, zt + .7, Z_ARQ), 'creme', .5)                               # bandeira
    B.add(t_box(-w + .62, w - .62, -.4, .4, Z_ARQ - .5, Z_ARQ, bev=.08), 'verm', .5)
    n = 5; ww = (2 * w - 1.24)
    for i in range(n):
        a = -w + .62 + i * ww / n
        _cell = (a + .1, a + ww / n - .1)
        for (p, q, r, s) in ((_cell[0], _cell[1], zt + .82, zt + 1.04), (_cell[0], _cell[1], Z_ARQ - .82, Z_ARQ - .6), (_cell[0], _cell[0] + .22, zt + .82, Z_ARQ - .6), (_cell[1] - .22, _cell[1], zt + .82, Z_ARQ - .6)):
            B.add(t_box(p, q, -.36, -.1, r, s, bev=.03), 'mad', .5)
    return B

def vao_parede():
    """vao cego (laterais e fundos): rodape de pedra, pano vermelho com moldura em relevo e janela octogonal trelicada alta."""
    B = Builder('KIT_vao_parede', 113)
    _rodape(B)
    w = VAO / 2 - R_COL + .25; z0, z1 = 3.16, Z_ARQ
    B.add(t_box(-w, w, -.5, .5, z0, z1, bev=.05), 'verm', .5)
    for s in (-1, 1):
        ya, yb = sorted((s * .5, s * .62))
        for (p, q, r, t) in ((-w + .5, w - .5, z0 + .45, z0 + .85), (-w + .5, w - .5, z1 - .85, z1 - .45), (-w + .5, -w + .9, z0 + .45, z1 - .45), (w - .9, w - .5, z0 + .45, z1 - .45)):
            B.add(t_box(p, q, ya, yb, r, t, bev=.06), 'vermS', .5)
    zc = 7.5; R = 1.75
    def octo(r): return [(r * math.cos(math.radians(22.5 + 45 * i)), r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    B.add(xf(t_prism(octo(R + .42), 'Y', -.72, .72, bev=.08), loc=(0, 0, zc)), 'mad', .5)
    B.add(xf(t_prism(octo(R), 'Y', -.78, .78), loc=(0, 0, zc)), 'creme', .5)
    for s in (-1, 1):
        for k in (-1, 0, 1):
            ln = R * 1.7 if k == 0 else R * 1.25
            ya, yb = sorted((s * .78, s * .96))
            B.add(xf(t_box(-.11, .11, ya, yb, -ln / 2 * 1.0, ln / 2 * 1.0, bev=.03), loc=(k * .8, 0, zc)), 'mad', .5)
            B.add(xf(t_box(-ln / 2, ln / 2, ya, yb, -.11, .11, bev=.03), loc=(0, 0, zc + k * .8)), 'mad', .5)
    return B

def placa():
    """bian'e sem texto: tabua jade escuro, moldura de ouro em dois degraus e o emblema da seita (espada sobre chama)."""
    B = Builder('KIT_placa', 121)
    B.add(t_box(-2.6, 2.6, -.18, .18, -1.25, 1.25, bev=.06), 'ouro', .5)
    B.add(t_box(-2.3, 2.3, -.26, .0, -.98, .98, bev=.05), 'jadeE', .5)
    B.add(t_box(-2.42, 2.42, -.22, 0, -1.08, 1.08, bev=.03), 'vermS', .45)
    chama = [(0, -.72), (.42, -.5), (.56, -.12), (.4, .22), (.22, .05), (.16, .42), (0, .78), (-.12, .4), (-.3, .18), (-.44, .3), (-.56, -.1), (-.42, -.5)]
    B.add(xf(t_prism(chama, 'Y', -.34, -.26, bev=.03), loc=(0, 0, -.05)), 'ouro', .6)
    B.add(t_prism([(0, -.86), (.1, -.5), (.1, .38), (-.1, .38), (-.1, -.5)], 'Y', -.42, -.34, bev=.02), 'creme', .7)
    B.add(t_box(-.36, .36, -.44, -.34, .38, .5, bev=.02), 'bronze', .6)
    B.add(t_box(-.07, .07, -.43, -.34, .5, .82, bev=.02), 'mad', .5)
    for sx in (-1, 1):
        B.add(xf(t_prism([(0, -.3), (.34, 0), (0, .3), (-.34, 0)], 'Y', -.32, -.26, bev=.02), loc=(sx * 1.55, 0, 0)), 'ouro', .6)
        B.add(t_box(sx * 1.9 - .16, sx * 1.9 + .16, .1, 2.3, .62, .94, bev=.04), 'mad', .45)      # maos-francesas que prendem a placa a tabua
        B.add(t_box(sx * 1.9 - .16, sx * 1.9 + .16, .1, 1.5, -1.0, -.7, bev=.04), 'mad', .45)
    return B
