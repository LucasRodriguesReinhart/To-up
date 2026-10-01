# k_dougong.py - conjuntos de dougong em 3 graus + conjunto de CANTO. Origem local: topo da prancha (pingbanfang), eixo da
# coluna; frente = -Y. Pecas: dou (bloco com a metade inferior chanfrada em tronco), gong (braco com pontas arredondadas por
# baixo - juansha), qiao/ang (braco perpendicular; o ang termina em bico inclinado), shuatou (cabeca de gafanhoto).
# Escala Tang/cartoon (brackets grandes). S = passo (tiao).
import math
from mathutils import Vector, Matrix
from k_core import *

S = 1.05            # avanco por passo
AH = .9             # altura do braco
AT = .78            # espessura do braco
Z1, Z2, Z3 = .82, 2.22, 3.62     # fundo dos bracos de cada nivel
Z_TOP = Z3 + AH                  # 4.52: onde pousam a terca do beiral e as vigas do plano da parede

def t_dou(w, h, taper=.7):
    r = w / math.sqrt(2)
    bm = t_lathe([(0, 0), (r * taper, 0), (r, h * .42), (r, h), (0, h)], 4, smooth=False)
    xf(bm, rot=(0, 0, 45)); bevel_sharp(bm, .07, 1); return bm

def t_gong(L, h=AH, t=AT):
    e = L / 2
    half = [(e, h), (e, h * .56), (e - .16, h * .3), (e - .42, h * .1), (e - .8, 0)]
    poly = [(-a, b) for a, b in half[::-1]] + half[::-1][::-1]
    poly = [(-e + .8, 0), (-e + .42, h * .1), (-e + .16, h * .3), (-e, h * .56), (-e, h)] + [(e, h), (e, h * .56), (e - .16, h * .3), (e - .42, h * .1), (e - .8, 0)]
    bm = t_prism(poly[::-1], 'Y', -t / 2, t / 2); bevel_sharp(bm, .06, 1); return bm

def t_ang(back, front, h=AH, t=AT, beak=1.55, drop=.55):
    """braco ao longo de Y (de +back ate -front) terminando em bico (ang) que desce `drop` e avanca `beak`."""
    poly = [(back, 0), (back, h), (-front, h), (-front - beak, -drop + .12), (-front - beak + .1, -drop), (-front + .25, 0)]
    bm = t_prism(poly, 'X', -t / 2, t / 2); bevel_sharp(bm, .06, 1); return bm

def t_shua(back, front, h=AH, t=AT):
    """shuatou: ponta facetada (cabeca de gafanhoto)."""
    poly = [(back, 0), (back, h), (-front, h), (-front - .55, h * .62), (-front - .62, h * .3), (-front - .3, 0)]
    bm = t_prism(poly, 'X', -t / 2, t / 2); bevel_sharp(bm, .06, 1); return bm

def _bico_ouro(B, y, z, rotz=0.0, k=1.0):
    bm = t_prism([(0, 0), (0, .5), (-.62, .02), (-.56, -.12)], 'X', -AT / 2 - .03, AT / 2 + .03)
    B.add(xf(bm, rot=(0, 0, rotz), loc=(0, 0, 0)), 'ouro', .6) if False else None

def _sheng(B, x, y, z, rot=0.0):
    # hierarquia do ouro: so a fiada de cima (a que carrega a terca) e dourada; as de baixo sao jade escuro
    B.add(xf(t_dou(1.18, .74), rot=(0, 0, rot), loc=(x, y, z)), 'ouro' if z > Z2 + AH - .01 else 'jadeE')

def _frente(B, rotz=0.0, passos=2, lados=True, kx=1.0):
    """bracos de UMA face (frente = -Y antes de girar rotz graus)."""
    def P(bm, loc=(0, 0, 0)):
        return xf(xf(bm, loc=loc), rot=(0, 0, rotz))
    def Q(x, y):
        a = math.radians(rotz); return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
    # nivel 1: gua gong (paralelo) + qiao (perpendicular, 1 passo)
    if lados: B.add(P(t_gong(4.5), (0, 0, Z1)), 'jade')
    B.add(P(xf(t_gong(2 * S + 1.7), rot=(0, 0, 90)), (0, 0, Z1)), 'jade')
    for (x, y) in ((-1.85, 0), (1.85, 0)) if lados else ():
        q = Q(x, y); _sheng(B, q[0], q[1], Z1 + AH, rotz)
    q = Q(0, -S); _sheng(B, q[0], q[1], Z1 + AH, rotz)
    if passos == 1:
        B.add(P(t_gong(4.5), (0, -S, Z2)), 'jade')
        B.add(P(t_shua(1.4, S + .2), (0, 0, Z2)), 'jade')
        for x in (-1.85, 1.85):
            q = Q(x, -S); _sheng(B, q[0], q[1], Z2 + AH, rotz)
        return
    # nivel 2: wan gong no plano da parede, gua gong no 1o passo, ANG atravessando ate o 2o passo
    if lados: B.add(P(t_gong(6.5), (0, 0, Z2)), 'jade')
    B.add(P(t_gong(4.5), (0, -S, Z2)), 'jade')
    B.add(P(t_ang(1.9, 2 * S + .35), (0, 0, Z2)), 'jade')
    B.add(P(t_prism([(-2 * S - .35 - 1.57, -.47), (-2 * S - .35 - .95, -.18), (-2 * S - .35 - 1.0, .02), (-2 * S - .35 - 1.5, -.5)], 'X', -AT / 2 - .04, AT / 2 + .04), (0, 0, Z2)), 'ouro', .6)
    pts = [(-1.85, -S), (1.85, -S), (0, -2 * S)] + ([(-2.85, 0), (2.85, 0)] if lados else [])
    for (x, y) in pts:
        q = Q(x, y); _sheng(B, q[0], q[1], Z2 + AH, rotz)
    # nivel 3: xiang gong no 2o passo, wan gong no 1o passo, shuatou no topo
    B.add(P(t_gong(4.5), (0, -2 * S, Z3)), 'jade')
    B.add(P(t_gong(6.5), (0, -S, Z3)), 'jade')
    B.add(P(t_shua(1.9, 2 * S + .5), (0, 0, Z3)), 'jade')

def principal():
    """grau principal (2 passos) - Hero Assets."""
    B = Builder('KIT_dougong_principal', 201)
    B.add(t_dou(2.05, 1.22), 'jadeE', .45)
    _frente(B, 0, 2)
    _sheng(B, 0, 0, Z1 + AH); _sheng(B, 0, 0, Z2 + AH)
    return B

def intermediario():
    """grau intermediario (1 passo) - edificios secundarios."""
    B = Builder('KIT_dougong_intermediario', 202)
    B.add(t_dou(2.05, 1.22), 'jadeE', .45)
    _frente(B, 0, 1); _sheng(B, 0, 0, Z1 + AH)
    return B

def simples():
    """grau simples 'um dou, tres sheng' - muros, galerias, suporte ambiental."""
    B = Builder('KIT_dougong_simples', 203)
    B.add(t_dou(2.05, 1.22), 'jadeE', .45)
    B.add(xf(t_gong(4.5), loc=(0, 0, Z1)), 'jade')
    for x in (-1.85, 0, 1.85): _sheng(B, x, 0, Z1 + AH)
    return B

def canto():
    """conjunto de CANTO (canto frontal-direito: faces -Y e +X): as duas faces + braco diagonal a 45 graus, mais longo,
    com ang duplo. E ele que sustenta a viga de canto do beiral."""
    B = Builder('KIT_dougong_canto', 204)
    B.add(t_dou(2.3, 1.22), 'jadeE', .45)
    _frente(B, 0, 2); _frente(B, 90, 2)
    k = math.sqrt(2)
    def D(bm, z): return xf(xf(bm, loc=(0, 0, z)), rot=(0, 0, 45))
    B.add(D(xf(t_gong(2 * S * k + 1.7), rot=(0, 0, 90)), Z1), 'jade')
    B.add(D(t_ang(2.0, 2 * S * k + .35, beak=1.9, drop=.65), Z2), 'jade')
    B.add(D(t_ang(2.0, 2 * S * k + 1.2, beak=2.1, drop=.7), Z3), 'jade')
    for (d, z) in ((S * k, Z1 + AH), (2 * S * k, Z2 + AH)):
        a = math.radians(45); x, y = (0 * math.cos(a) + d * math.sin(a), 0 * math.sin(a) - d * math.cos(a))
        _sheng(B, x, y, z, 45)
    _sheng(B, 0, 0, Z1 + AH); _sheng(B, 0, 0, Z2 + AH)
    return B
