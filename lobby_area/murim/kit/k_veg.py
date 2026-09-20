# k_veg.py - vegetacao estilizada do kit: pinheiro em camadas (tronco em S, 5 massas assimetricas em dois tons), arbusto, tufo.
import math, random
from mathutils import Vector
from k_core import *
from k_props import crom, lerp_list

def _pad_folha(R, esp, lobos=5, amp=.22, entalhes=1, seg=16, seed=0, queda=.22):
    """CAMADA de folhagem como LENTE achatada, gerada de DISCO e nao de esfera.
    A razao espessura/diametro fica em 0.20-0.28 (a icosfera estava em 1.0, que e o que lia como
    pelucia). O raio e modulado por um numero IMPAR de lobos para nao criar simetria obvia, leva
    entalhe fundo para a silhueta morder para dentro, e as pontas caem - e o contorno, nao o detalhe,
    que faz folhagem estilizada parecer desenhada."""
    rnd = random.Random(seed)
    bm = bmesh.new()
    fase = rnd.uniform(0, 6.28)
    fundo = set()
    for e in range(entalhes):
        fundo.add(int(seg * (rnd.random())) % seg)
    raios = []
    for i in range(seg):
        a = math.tau * i / seg
        r = R * (1 + amp * math.cos(lobos * a + fase))
        if i % 2 == 0: r *= rnd.uniform(.82, 1.0)
        if i in fundo: r *= .55                                    # entalhe: morde para dentro
        raios.append(r)
    centro_sup = bm.verts.new((0, 0, esp * .5))
    centro_inf = bm.verts.new((0, 0, -esp * .5))
    anelA, anelB, borda = [], [], []
    for i in range(seg):
        a = math.tau * i / seg
        r = raios[i]
        ca, sa = math.cos(a), math.sin(a)
        # espessura maxima em 0.45R, borda fina: e a borda nitida que pega luz
        anelA.append(bm.verts.new((ca * r * .45, sa * r * .45, esp * .5)))
        anelB.append(bm.verts.new((ca * r * .45, sa * r * .45, -esp * .5)))
        borda.append(bm.verts.new((ca * r, sa * r, -queda * esp * (1 + .6 * (r / R)))))
    for i in range(seg):
        j = (i + 1) % seg
        bm.faces.new((centro_sup, anelA[i], anelA[j]))
        bm.faces.new((centro_inf, anelB[j], anelB[i]))
        bm.faces.new((anelA[i], borda[i], borda[j], anelA[j]))
        bm.faces.new((anelB[j], borda[j], borda[i], anelB[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = False                            # chapado: cada plano pega UM valor do atlas
    bevel_sharp(bm, esp * .10, 1, angle=.45)
    return bm

def pinheiro(seed=1, name='KIT_pinheiro_a', flip=1, H=18.0):
    """PINHEIRO DE JARDIM CHINES (pinus tabuliformis, o "pinheiro-mesa"): tronco torto e EXPOSTO ate
    0.40H, galhos quase horizontais, e a copa em camadas achatadas com ceu entre elas.
    Reescrito depois da pesquisa: a versao de blobs de icosfera lia como brocolis de pelucia e, sem
    tronco nu, nao tinha elemento de escala conhecida - dai a queixa de "arvore miuda"."""
    B = Builder(name, 500 + seed); rnd = random.Random(seed)
    r0 = H / 22.0
    NU = 0.40 * H                                                  # tronco nu obrigatorio
    # ---- tronco: curva em S, torcao e alargamento de raiz
    pts, raios = [], []
    for i in range(9):
        t = i / 8.0
        desv = math.sin(t * math.pi) * .10 * H * flip
        pts.append(Vector((desv + t * .08 * H * flip, math.sin(t * 4.1) * .03 * H, t * H)))
        raios.append(r0 * (1.5 if i == 0 else (1.0 - .75 * t ** .6)))
    B.add(t_tube(pts, raios, 8), 'casca', .45)
    for a in range(5):                                             # contrafortes de raiz
        ang = math.radians(72 * a + 21)
        raiz = crom([(0, 0, r0 * 1.4), (math.cos(ang) * r0 * 1.2, math.sin(ang) * r0 * 1.2, r0 * .3),
                     (math.cos(ang) * r0 * 1.8, math.sin(ang) * r0 * 1.8, -.05)], 3)
        B.add(t_tube(raiz, lerp_list([r0 * .42, r0 * .3, r0 * .1], len(raiz)), 6), 'casca', .38)
    # ---- camadas: espacamento DECRESCENTE, raio decrescente, ceu entre elas
    n = 6
    for i in range(n):
        t = i / (n - 1.0)
        z = NU + (H - NU) * (t ** .82)
        R = H * (.30 - .17 * t) * rnd.uniform(.92, 1.08)
        esp = R * rnd.uniform(.21, .27)                            # 4:1 a 5:1, nao 1:1
        ang = math.radians(137.5 * i + rnd.uniform(-15, 15))       # angulo aureo entre galhos
        dx = math.cos(ang) * R * .30; dy = math.sin(ang) * R * .30
        # galho quase horizontal sustentando a camada, furando a borda em algumas
        incl = math.radians(-5 + 23 * t)
        comp = R * (1.05 if i % 3 else 1.18)
        g = crom([(0, 0, z - esp * .8),
                  (math.cos(ang) * comp * .5, math.sin(ang) * comp * .5, z - esp * .55 + math.sin(incl) * comp * .5),
                  (math.cos(ang) * comp, math.sin(ang) * comp, z - esp * .3 + math.sin(incl) * comp)], 4)
        B.add(t_tube(g, lerp_list([r0 * .35, r0 * .24, r0 * .15], len(g)), 6), 'casca', .42)
        pad = _pad_folha(R, esp, lobos=(5 if i % 2 else 7), amp=.22, entalhes=1 + (i % 2),
                         seg=16, seed=seed * 31 + i)
        xf(pad, rot=(rnd.uniform(-5, 5), rnd.uniform(-5, 5), rnd.uniform(0, 360)),
           loc=(dx + pts[-1].x * t, dy, z))
        B.add(pad, 'pinho' if i % 2 else 'folha', .35 + .09 * i)
    return B

def arbusto(seed=1, name='KIT_arbusto_a'):
    B = Builder(name, 520 + seed); rnd = random.Random(seed)
    for i, (x, y, r) in enumerate(((0, 0, 1.5), (1.25, .35, 1.1), (-1.1, -.3, 1.0), (.3, -.9, .85))):
        B.add(xf(t_blob(r, (1, 1, .78), 2, lobes=5, lobe_amp=.14, seed=seed * 7 + i, flat_bottom=-.35 * r), rot=(0, 0, rnd.uniform(0, 360)), loc=(x, y, r * .55)), 'pinho' if i % 2 == 0 else 'folha', .45 + .1 * i)
    return B

def tufo(seed=1, name='KIT_tufo_a'):
    B = Builder(name, 540 + seed); rnd = random.Random(seed)
    for i in range(8):
        a = rnd.uniform(0, math.tau); l = rnd.uniform(1.1, 1.9); o = rnd.uniform(.35, .8)
        bl = crom([(0, 0, 0), (math.cos(a) * o * .4, math.sin(a) * o * .4, l * .55), (math.cos(a) * o, math.sin(a) * o, l)], 3)
        bm = t_tube(bl, lerp_list([.13, .1, .02], len(bl)), 4, smooth=False); B.add(bm, 'folha', rnd.uniform(.35, .75))
    return B
