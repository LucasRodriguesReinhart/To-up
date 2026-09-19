# k_pedra.py - pecas de PEDRA do kit: base sumeru (segmento + pilar de canto), piso, escada, balaustrada, tambor, jardineira.
# Grade modular do terraco: MOD = 5.25 studs.
import math
from mathutils import Vector
from k_core import *

MOD = 5.25
TZ = 4.0          # altura do terraco (topo do piso)

# perfil da base sumeru (u para fora, v para cima), desenhado de baixo para cima:
# guijiao (rodape) / xiafang / xiaxiao (gola inferior) / shuyao (cintura) / shangxiao (gola superior) / shangfang (capa)
SUMERU = [(0.0, 0.0), (0.95, 0.0), (0.95, 0.55), (0.86, 0.74), (0.68, 0.78), (0.68, 1.14), (0.62, 1.22), (0.47, 1.38),
          (0.30, 1.54), (0.20, 1.62), (0.20, 2.50), (0.30, 2.57), (0.47, 2.72), (0.60, 2.90), (0.64, 2.98), (0.84, 3.02),
          (0.84, 3.70), (0.76, 3.88), (0.58, 3.98), (0.0, 3.98)]

def sumeru_seg():
    """segmento reto de MOD de comprimento ao longo de +X, face externa virada para -Y, origem no canto inferior interno."""
    B = Builder('KIT_sumeru_seg', 11)
    B.add(t_sweep(SUMERU, [Vector((0, 0, 0)), Vector((MOD, 0, 0))]), 'pedra', .5)
    # painel entalhado na cintura (almofada arredondada) + pilarete no eixo do poste da balaustrada
    B.add(t_box(0.75, MOD - 0.75, -0.36, -0.15, 1.74, 2.38, bev=.1, seg=3), 'pedra', .62)
    B.add(t_box(1.35, MOD - 1.35, -0.42, -0.30, 1.90, 2.22, bev=.07, seg=2), 'pedra', .7)
    B.add(t_box(-0.42, 0.42, -0.50, -0.15, 1.62, 2.50, bev=.08), 'pedra', .4)
    # juntas das fiadas do rodape e da capa (blocos): ranhuras finas como pequenos dentes escuros
    for x in (MOD * .5,):
        B.add(t_box(x - .035, x + .035, -0.96, -0.80, 0.02, 0.56), 'junta', .2)
        B.add(t_box(x - .035, x + .035, -0.85, -0.70, 3.04, 3.68), 'junta', .2)
    return B

def sumeru_canto():
    """pilar de canto (jiaozhu) que fecha o encontro de dois segmentos; origem no vertice externo do terraco."""
    B = Builder('KIT_sumeru_canto', 12)
    B.add(t_box(-1.05, 1.05, -1.05, 1.05, 0, 0.62, bev=.1), 'pedra', .45)
    B.add(t_box(-0.92, 0.92, -0.92, 0.92, 0.62, 3.0, bev=.12, seg=3), 'pedra', .55)
    B.add(t_box(-1.02, 1.02, -1.02, 1.02, 3.0, 3.98, bev=.14, seg=3), 'pedra', .5)
    for s in ((0, -0.95, 0), (0.95, 0, 90), (0, 0.95, 180), (-0.95, 0, 270)):
        B.add(xf(t_box(-0.55, 0.55, -0.07, 0.07, 1.15, 2.6, bev=.06), rot=(0, 0, s[2]), loc=(s[0], s[1], 0)), 'pedra', .68)
    return B

def piso_mod():
    """modulo de piso MOD x MOD: lajes chanfradas em amarracao, juntas rebaixadas sobre leito escuro. Topo em z=0."""
    B = Builder('KIT_piso_mod', 21)
    B.add(t_box(0, MOD, 0, MOD, -0.5, -0.09), 'junta', .25)
    g = 0.07; rows = 3; rh = MOD / rows
    for r in range(rows):
        cuts = [0, MOD * .5, MOD] if r % 2 == 0 else [0, MOD * .25, MOD * .75, MOD]
        for a, b in zip(cuts, cuts[1:]):
            dz = B.rnd.uniform(-0.025, 0.0)
            B.add(t_box(a + g, b - g, r * rh + g, (r + 1) * rh - g, -0.4, dz, bev=.05, seg=2), 'piso')
    return B

def escada(n=5, rise=TZ / 5, tread=1.9, w=2 * MOD):
    """lance frontal: degraus com bocel, duas pedras de bochecha (chuidai) inclinadas e blocos de arranque.
    origem no centro da borda do terraco, descendo para -Y."""
    B = Builder('KIT_escada', 31)
    hw = w / 2 - 1.25
    for i in range(1, n):                       # o degrau 0 e a propria borda do terraco
        ztop = TZ - rise * i
        y1 = -tread * (i - 1); y0 = y1 - tread
        B.add(t_box(-hw, hw, y0 - 0.16, y1, 0.0, ztop, bev=.09, seg=2), 'pedra')
    L = tread * (n - 1)
    for sx in (-1, 1):
        x0, x1 = (hw, hw + 1.25) if sx > 0 else (-hw - 1.25, -hw)
        poly = [(0.3, 0.0), (-L - 1.9, 0.0), (-L - 1.9, 0.75), (-L - 0.9, 0.95), (0.0, TZ + 0.42), (0.3, TZ + 0.42)]
        B.add(t_prism(poly[::-1], 'X', x0, x1, bev=.12, seg=3), 'pedra', .6)
        B.add(t_box(x0 - 0.12, x1 + 0.12, -L - 2.75, -L - 1.55, 0, 1.25, bev=.14, seg=3), 'pedra', .42)
        B.add(xf(t_lathe([(0, 0), (.5, 0), (.62, .18), (.5, .42), (0, .5)], 14), loc=((x0 + x1) / 2, -L - 2.15, 1.25)), 'pedra', .5)
    return B

# ---- balaustrada -------------------------------------------------------------------------------------------------
NUVEM = [(0, 0), (.62, 0), (.70, .10), (.62, .22), (.50, .28), (.56, .40), (.80, .62), (.88, .90), (.78, 1.18), (.56, 1.40),
         (.34, 1.52), (.22, 1.66), (.0, 1.72)]   # remate do poste: gola + botao de nuvem

def bal_poste(B=None, x=0.0, y=0.0, z=0.0):
    own = B is None
    if own: B = Builder('KIT_bal_poste', 41)
    B.add(xf(t_box(-.66, .66, -.66, .66, 0, .42, bev=.08), loc=(x, y, z)), 'pedra', .45)
    B.add(xf(t_box(-.56, .56, -.56, .56, .42, 3.25, bev=.1, seg=3), loc=(x, y, z)), 'pedra', .55)
    for a in (0, 90, 180, 270):                                  # almofada rebaixada em cada face (moldura em relevo)
        B.add(xf(t_box(-.34, .34, -.60, -.54, .85, 2.75, bev=.05), rot=(0, 0, a), loc=(x, y, z)), 'pedra', .7)
    B.add(xf(t_box(-.64, .64, -.64, .64, 3.25, 3.5, bev=.08), loc=(x, y, z)), 'pedra', .5)
    B.add(xf(t_lathe(NUVEM, 20), scale=(.72, .72, .78), loc=(x, y, z + 3.5)), 'pedra', .62)
    return B

RUYI = [(-.95, 0), (-.55, -.22), (0, -.12), (.55, -.22), (.95, 0), (1.05, .28), (.8, .5), (.5, .42), (.34, .62), (.12, .78),
        (-.12, .78), (-.34, .62), (-.5, .42), (-.8, .5), (-1.05, .28)]   # nuvem ruyi em relevo no painel

def bal_seg():
    """segmento de MOD: poste em x=0 + corrimao, vaso (jingping), painel (huaban) com nuvem ruyi e soleira ate x=MOD."""
    B = Builder('KIT_bal_seg', 42)
    bal_poste(B)
    a, b = .56, MOD - .56
    B.add(t_box(a, b, -.42, .42, 0, .36, bev=.07), 'pedra', .45)                                   # soleira
    B.add(t_box(a, b, -.22, .22, .36, 1.95, bev=.05), 'pedra', .58)                                # painel
    B.add(t_box(a + .3, b - .3, -.30, .30, .55, 1.78, bev=.09, seg=3), 'pedra', .66)               # almofada
    for s in (-1, 1):
        B.add(xf(t_prism(RUYI, 'Y', -.05, .05, bev=.03), scale=(1.15, 1, 1.0), loc=((a + b) / 2, s * .33, .82)), 'pedra', .78)
    rail = [(-.40, 0), (-.30, -.2), (.30, -.2), (.40, 0), (.40, .22), (.24, .4), (-.24, .4), (-.40, .22)]
    B.add(t_sweep([(u, v + 2.75) for u, v in rail], [Vector((a - .1, 0, 0)), Vector((b + .1, 0, 0))]), 'pedra', .6)
    B.add(xf(t_lathe([(0, 0), (.30, 0), (.36, .08), (.22, .2), (.30, .34), (.34, .46), (.2, .58), (0, .58)], 10), loc=((a + b) / 2, 0, 1.95)), 'pedra', .7)
    for xx in (a + .55, b - .55):
        B.add(t_box(xx - .22, xx + .22, -.2, .2, 1.95, 2.56, bev=.06), 'pedra', .52)
    return B

def bal_tambor():
    """baogushi: pedra-tambor em voluta que arremata a balaustrada junto a escada (encosta no poste, aponta para -Y)."""
    B = Builder('KIT_bal_tambor', 43)
    poly = [(0.0, 0.0), (-2.7, 0.0), (-2.7, .45), (-2.45, .6)] + arc_pts(-1.55, 1.3, 1.08, 215, 10, 12) + [(-.2, 1.95), (0, 2.3)]
    B.add(t_prism([(a, b) for a, b in poly][::-1], 'X', -.3, .3, bev=.1, seg=3), 'pedra', .55)
    for s in (-1, 1):
        B.add(xf(t_lathe([(0, 0), (.78, 0), (.84, .05), (.6, .1), (.3, .14), (0, .16)], 18), rot=(0, 90 * s, 0), loc=(s * .3, -1.55, 1.3)), 'pedra', .7)
    return B

def tambor_coluna():
    """zhuchu: plinto quadrado + tambor bojudo com dois filetes. Origem na base, topo em z=1.5."""
    B = Builder('KIT_col_base', 51)
    B.add(t_box(-1.95, 1.95, -1.95, 1.95, 0, .45, bev=.1, seg=3), 'pedra', .45)
    B.add(t_lathe([(0, .45), (1.5, .45), (1.72, .55), (1.86, .78), (1.88, 1.0), (1.76, 1.24), (1.52, 1.4), (1.4, 1.44), (1.4, 1.5), (0, 1.5)], 28), 'pedra', .6)
    B.add(t_lathe([(1.62, .5), (1.8, .56), (1.8, .66), (1.62, .7)], 28), 'pedra', .72)
    return B

def jardineira():
    """jardineira octogonal de pedra com pes, corpo bojudo, borda e terra. Topo da terra em z=1.75."""
    B = Builder('KIT_jardineira', 61)
    def octo(r): return [(r * math.cos(math.radians(22.5 + 45 * i)), r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    B.add(t_prism(octo(2.0), 'Z', 0, .35, bev=.08), 'pedra', .42)
    B.add(t_prism(octo(2.35), 'Z', .35, 1.55, bev=.16, seg=3), 'pedra', .56)
    B.add(t_prism(octo(2.6), 'Z', 1.55, 1.95, bev=.1, seg=3), 'pedra', .64)
    B.add(t_prism(octo(2.1), 'Z', 1.6, 1.78), 'casca', .3)
    for i in range(8):
        a = math.radians(45 * i); r = 2.28
        B.add(xf(t_box(-.55, .55, -.06, .06, .62, 1.3, bev=.05), rot=(0, 0, 45 * i + 90), loc=(r * math.cos(a), r * math.sin(a), 0)), 'pedra', .7)
    return B
