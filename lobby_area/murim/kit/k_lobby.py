# k_lobby.py - pecas que o LOBBY exige e o kit do Gate 1 nao tinha: Torre do Fogo, Espada Ancestral, props da forja
# (fornalha, bigorna, fole, calha de tempera, altar de laminas, braseiro), leao guardiao, ponte-lua, rocha, bambu,
# bordo, postes de treino e boneco. Mesma linguagem do kit: perfis desenhados, chanfro por escala, tintas de k_core.
import math, random
import bmesh
from mathutils import Vector, Matrix
from k_core import *
from k_props import crom, lerp_list, bmesh_tri_prism
from k_veg import _pad_folha

def _octo(r, rot=22.5):
    return [(r * math.cos(math.radians(rot + 45 * i)), r * math.sin(math.radians(rot + 45 * i))) for i in range(8)]

# ---------------------------------------------------------------- TORRE DO FOGO (chamine monumental da Forja)
def torre_fogo(H=46.0):
    """chamine de tijolo em 3 tramos que afinam, com aneis de bronze, boca de brasa no topo e uma escada de ferro.
    Origem no piso do terraco da Forja; sai pelo telhado. Altura total ~H+4."""
    B = Builder('LOB_torre_fogo', 701)
    tramos = [(0, H * .42, 4.6, 4.0), (H * .42, H * .74, 3.9, 3.4), (H * .74, H, 3.3, 2.9)]
    for i, (z0, z1, r0, r1) in enumerate(tramos):
        n = max(3, int((z1 - z0) / 2.6))                       # fiadas de tijolo: aneis levemente alternados
        for k in range(n):
            a = z0 + (z1 - z0) * k / n; b = z0 + (z1 - z0) * (k + 1) / n
            ra = r0 + (r1 - r0) * k / n; rb = r0 + (r1 - r0) * (k + 1) / n
            off = .05 if k % 2 else 0.0
            B.add(t_prism(_octo(ra + off), 'Z', a, b - .06, bev=.07), 'ferro', .35 + .3 * ((k * 7 + i * 3) % 5) / 5)
        B.add(t_prism(_octo(r1 + .3), 'Z', z1 - .5, z1 + .35, bev=.12, seg=3), 'bronze', .55)
    ztop = H
    B.add(t_prism(_octo(3.4), 'Z', ztop, ztop + 1.5, bev=.14, seg=3), 'bronze', .5)       # coroa
    B.add(t_prism(_octo(3.0), 'Z', ztop + .2, ztop + 1.7), 'ferro', .2)                    # boca
    B.add(t_prism(_octo(2.7), 'Z', ztop + .1, ztop + .9), 'brasa', .8)                     # brasa
    for i in range(8):                                                                      # dentes da coroa
        a = math.radians(45 * i + 22.5)
        B.add(xf(t_box(-.5, .5, -.28, .28, 0, 1.15, bev=.06), rot=(0, 0, 45 * i + 22.5), loc=(3.3 * math.cos(a), 3.3 * math.sin(a), ztop + 1.4)), 'bronze', .6)
    for k in range(int(H / 1.9)):                                                           # escada de ferro lateral
        z = 3 + k * 1.9
        if z > H - 2: break
        B.add(t_box(-.12, .12, -1.1, 1.1, z, z + .22, bev=.04), 'ferro', .3)
    for s in (-1, 1):
        B.add(t_box(-.16, .16, s * 1.1 - .16, s * 1.1 + .16, 2.6, H - 1.5, bev=.04), 'ferro', .25)
    return B

# ---------------------------------------------------------------- ESPADA ANCESTRAL (landmark do patio)
def picareta_ancestral(H=30.0):
    """PICARETA monumental cravada no pedestal: cabo enfaixado, virola de bronze e cabeca de aco com
    bico de um lado e lamina do outro. Substitui a espada que estava aqui - o jogo e de mineracao, e o
    monumento do patio central tem de contar isso. Origem na base do cabo (topo do pedestal)."""
    B = Builder('LOB_picareta_ancestral', 702)
    hc = H * .74                                                                  # cabo
    B.add(t_lathe([(0, 0), (.95, 0), (1.05, 1.4), (.86, hc * .55), (.92, hc - 2.2), (.7, hc)], 16), 'mad', .45)
    for k in range(9):                                                            # enfaixamento do cabo
        z = 1.8 + k * (hc - 8.0) / 9
        B.add(xf(t_lathe([(.88, 0), (1.02, .06), (1.02, .34), (.88, .42)], 14), loc=(0, 0, z)), 'tecido', .42 + .06 * (k % 3))
    for k in range(4):                                                            # anilhas de bronze
        z = hc * .30 + k * hc * .14
        B.add(xf(t_lathe([(.9, 0), (1.14, .05), (1.14, .3), (.9, .36)], 16), loc=(0, 0, z)), 'bronze', .55)
    zc = hc                                                                       # virola sob a cabeca
    B.add(xf(t_lathe([(.72, 0), (1.35, .25), (1.42, 1.5), (1.15, 2.1), (.72, 2.3)], 16), loc=(0, 0, zc)), 'bronze', .6)
    # CABECA: perfil em L achatado, bico afilado de um lado e lamina larga do outro
    cab = t_prism([(-7.8, .0), (-4.2, 1.15), (-1.3, 1.5), (1.3, 1.5), (4.6, 1.2), (6.4, .35),
                   (6.4, -.9), (4.6, -1.5), (1.3, -1.9), (-1.3, -1.9), (-4.2, -1.55), (-7.8, -.7)],
                  'Y', -.72, .72, bev=.16, seg=3)
    xf(cab, loc=(0, 0, zc + 3.0))
    B.add(cab, 'aco', .58)
    # bico: ponta longa e fina para a esquerda
    bic = t_prism([(0, 1.5), (0, -1.9), (-4.6, -.55), (-4.6, .2)], 'Y', -.5, .5, bev=.1, seg=2)
    xf(bic, loc=(-7.6, 0, zc + 3.0))
    B.add(bic, 'aco', .82)
    # lamina: aba larga para a direita, com gume
    lam = t_prism([(0, 1.2), (0, -1.5), (3.4, -2.1), (3.4, 1.8)], 'Y', -.62, .62, bev=.12, seg=2)
    xf(lam, loc=(6.3, 0, zc + 3.0))
    B.add(lam, 'aco', .74)
    B.add(xf(t_box(-3.4, 3.4, -.76, -.70, zc + 2.2, zc + 3.9, bev=.05), loc=(0, 0, 0)), 'ouro', .62)   # gravacao
    for k in range(5):
        x = -2.6 + k * 1.3
        B.add(t_box(x - .22, x + .22, -.8, -.74, zc + 2.5, zc + 3.6, bev=.04), 'ouro', .5 + .08 * k)
    for sx in (-1, 1):                                                            # fitas da seita
        f = crom([(sx * .8, .2, zc + 1.2), (sx * 2.4, .5, zc - 1.2), (sx * 1.7, -.3, zc - 4.2), (sx * 2.8, .4, zc - 6.6)], 5)
        B.add(t_tube(f, lerp_list([.2, .32, .26, .1], len(f)), 6), 'tecido', .5)
    return B

def pedestal_espada(R=9.0, H=5.2):
    """estrado octogonal da Espada Ancestral: base sumeru simplificada, degraus, inscricoes e 4 aneis de bronze."""
    B = Builder('LOB_pedestal_espada', 703)
    B.add(t_prism(_octo(R + 1.6), 'Z', 0, .7, bev=.12, seg=3), 'pedra', .45)
    B.add(t_prism(_octo(R + .9), 'Z', .7, 1.5, bev=.12, seg=3), 'pedra', .5)
    B.add(t_prism(_octo(R), 'Z', 1.5, H - 1.2, bev=.16, seg=3), 'pedra', .58)
    B.add(t_prism(_octo(R - .8), 'Z', 2.2, H - 2.0), 'junta', .25)
    for i in range(8):                                                            # paineis com nuvem em relevo
        a = math.radians(45 * i); r = R - .12
        B.add(xf(t_box(-2.4, 2.4, -.22, .22, 2.3, H - 2.1, bev=.1, seg=2), rot=(0, 0, 45 * i + 90), loc=(r * math.cos(a), r * math.sin(a), 0)), 'pedra', .7)
        B.add(xf(t_prism([(-1.0, 0), (-.5, -.3), (0, -.12), (.5, -.3), (1.0, 0), (.6, .34), (0, .5), (-.6, .34)], 'Y', -.42, -.22, bev=.05), rot=(0, 0, 45 * i + 90), loc=(r * math.cos(a), r * math.sin(a), (2.3 + H - 2.1) / 2)), 'ouro', .6)
    B.add(t_prism(_octo(R + .7), 'Z', H - 1.2, H, bev=.14, seg=3), 'pedra', .62)
    B.add(t_prism(_octo(2.6), 'Z', H, H + .35, bev=.08), 'bronze', .5)
    return B

# ---------------------------------------------------------------- FORJA: fornalha, bigorna, fole, tempera, laminas
def fornalha(W=16.0, D=9.0, H=13.0):
    """lareira monumental: corpo de pedra escura com boca em arco, verga de bronze, brasa e carvao. Frente = -Y."""
    B = Builder('LOB_fornalha', 711)
    aw, ah, asp = W * .34, H * .52, H * .28                                        # vao em arco
    def arco(x, z):
        if z <= asp: return abs(x) <= aw
        t = (z - asp) / max(.01, ah - asp); return abs(x) <= aw * math.sqrt(max(0, 1 - t * t))
    nx, nz = 13, 9                                                                 # blocos maiores: 35 mil tris nao passa no importador (teto 20 mil)
    for i in range(nx):
        x0 = -W / 2 + W * i / nx; x1 = -W / 2 + W * (i + 1) / nx
        for k in range(nz):
            z0 = H * k / nz; z1 = H * (k + 1) / nz
            if arco((x0 + x1) / 2, (z0 + z1) / 2) and (z0 + z1) / 2 < ah: continue
            B.add(t_box(x0 + .04, x1 - .04, -D / 2, D / 2, z0 + .04, z1 - .04, bev=.09), 'ferro')
    B.add(t_box(-aw - .8, aw + .8, -D / 2 - .5, -D / 2 + .3, ah - .5, ah + 1.1, bev=.12, seg=3), 'bronze', .55)
    B.add(t_box(-aw, aw, -D / 2 + .6, D / 2, .3, ah * .34), 'brasa', .85)          # brasa dentro
    B.add(t_box(-aw + .6, aw - .6, -D / 2 + 1.2, D / 2 - .6, ah * .3, ah * .38), 'chama', .8)
    B.add(t_box(-W / 2 - .7, W / 2 + .7, -D / 2 - .7, D / 2 + .7, H, H + 1.2, bev=.14, seg=3), 'bronze', .5)
    for sx in (-1, 1):                                                             # pilastras
        B.add(t_box(sx * (W / 2 - .3) - .5, sx * (W / 2 - .3) + .5, -D / 2 - .4, D / 2, 0, H, bev=.1), 'bronze', .42)
    return B

def bigorna():
    """bigorna sobre cepo de madeira com cintas de ferro. Altura ~3.2."""
    B = Builder('LOB_bigorna', 712)
    B.add(t_lathe([(0, 0), (1.5, 0), (1.45, .3), (1.25, 1.5), (1.35, 1.8), (0, 1.8)], 12), 'mad', .45)
    for z in (.35, 1.35): B.add(t_lathe([(1.28, z), (1.5, z + .04), (1.5, z + .3), (1.28, z + .34)], 12), 'ferro', .35)
    B.add(t_box(-1.4, 1.4, -.8, .8, 1.8, 2.15, bev=.08), 'ferro', .3)
    B.add(t_box(-1.0, 1.0, -.5, .5, 2.15, 2.7, bev=.08), 'ferro', .35)
    B.add(t_box(-2.2, 2.2, -.75, .75, 2.7, 3.2, bev=.12, seg=3), 'ferro', .4)
    B.add(xf(t_lathe([(0, 0), (.62, 0), (.5, .6), (.3, 1.0), (0, 1.05)], 10), rot=(0, 90, 0), loc=(-3.1, 0, 2.95)), 'ferro', .45)
    return B

def fole(L=9.0):
    """fole de caixa de pistao (fengxiang): caixa de madeira com cintas, alavanca e bico de ferro. Bico para -X."""
    B = Builder('LOB_fole', 713)
    B.add(t_box(-L / 2, L / 2, -2.0, 2.0, 0, 3.6, bev=.12, seg=3), 'madM', .45)
    for x in (-L / 2 + 1.2, 0, L / 2 - 1.2):
        B.add(t_box(x - .22, x + .22, -2.1, 2.1, -.05, 3.7, bev=.05), 'ferro', .35)
    B.add(t_box(-L / 2 - 2.6, -L / 2, -.4, .4, 1.5, 2.1, bev=.08), 'ferro', .4)
    B.add(xf(t_lathe([(0, 0), (.3, 0), (.34, 2.6), (0, 2.7)], 10), rot=(0, 90, 0), loc=(L / 2 + .2, 0, 2.4)), 'mad', .5)
    B.add(t_box(L / 2 + 2.5, L / 2 + 3.4, -.7, .7, 1.9, 2.9, bev=.1), 'mad', .55)
    for k in range(3): B.add(t_box(-L / 2 + .5 + k * 2.6, -L / 2 + 1.9 + k * 2.6, -2.15, -2.05, .6, 3.0, bev=.04), 'ferro', .5)
    return B

def calha_tempera(L=7.0):
    """calha de tempera: tanque de pedra com agua e aro de ferro."""
    B = Builder('LOB_calha_tempera', 714)
    B.add(t_box(-L / 2, L / 2, -1.6, 1.6, 0, 2.2, bev=.12, seg=3), 'pedra', .45)
    B.add(t_box(-L / 2 + .45, L / 2 - .45, -1.15, 1.15, .5, 2.25), 'agua' if 'agua' in PAINTS else 'jade', .6)
    for z in (.3, 1.7): B.add(t_box(-L / 2 - .08, L / 2 + .08, -1.68, 1.68, z, z + .26, bev=.05), 'ferro', .35)
    return B

def altar_laminas(L=11.0):
    """estante inclinada com laminas em fases de acabamento (a forja contando o que faz)."""
    B = Builder('LOB_altar_laminas', 715)
    B.add(t_box(-L / 2, L / 2, -1.5, 1.5, 0, 1.1, bev=.1), 'pedra', .45)
    B.add(t_box(-L / 2, L / 2, -1.5, -1.1, 1.1, 4.6, bev=.08), 'mad', .5)
    B.add(t_box(-L / 2, L / 2, -1.1, 1.5, 1.1, 1.5, bev=.06), 'mad', .55)
    rnd = random.Random(715)
    n = 7
    for k in range(n):
        x = -L / 2 + 1.0 + k * (L - 2.0) / (n - 1)
        h = 3.2 + rnd.uniform(-.5, .8); tint = 'aco' if k % 3 else 'ferro'
        bl = t_prism([(0, 0), (.32, .3), (.32, h - .5), (0, h), (-.32, h - .5), (-.32, .3)], 'Y', -.07, .07, bev=.03)
        xf(bl, rot=(14, 0, rnd.uniform(-4, 4)), loc=(x, .55, 1.5)); B.add(bl, tint, rnd.random())
        B.add(xf(t_box(-.3, .3, -.1, .1, -.5, 0, bev=.03), rot=(14, 0, 0), loc=(x, .55, 1.5)), 'mad', .5)
    return B

def braseiro():
    """ding de bronze com brasa: tres pes, corpo, duas alcas e fogo. Altura ~4.2."""
    B = Builder('LOB_braseiro', 716)
    for i in range(3):
        a = math.radians(120 * i + 30)
        B.add(xf(t_lathe([(0, 0), (.42, 0), (.5, .3), (.34, 1.6), (.26, 2.0), (0, 2.0)], 10), loc=(1.5 * math.cos(a), 1.5 * math.sin(a), 0)), 'bronze', .45)
    B.add(t_lathe([(0, 1.9), (2.1, 1.9), (2.4, 2.4), (2.5, 3.1), (2.3, 3.6), (2.45, 3.8), (2.5, 3.95), (2.2, 3.95), (2.05, 3.5), (0, 3.4)], 18), 'bronze', .5)
    B.add(t_lathe([(2.1, 2.5), (2.55, 2.6), (2.58, 2.95), (2.15, 3.05)], 18), 'jade', .55)
    for sx in (-1, 1):
        ring = [Vector((sx * (2.3 + .55 * math.cos(math.radians(a))), 0, 4.1 + .55 * math.sin(math.radians(a)))) for a in range(0, 361, 36)]
        B.add(t_tube(ring, [.14] * len(ring), 6, cap=False), 'bronze', .6)
    B.add(t_lathe([(0, 3.3), (1.9, 3.3), (1.7, 3.9), (1.0, 4.3), (0, 4.4)], 14), 'brasa', .8)
    B.add(t_lathe([(0, 4.0), (1.0, 4.1), (.6, 4.9), (0, 5.4)], 12), 'chama', .85)
    return B

# ---------------------------------------------------------------- LEAO GUARDIAO
def leao(lado=1, H=4.2, log=False):
    """SHISHI sobre pedestal xumizuo. lado=+1 macho (pata na bola), -1 femea (pata no filhote).
    Terceira versao. As duas minhas falharam: caixa sobre caixa virou pilha de caixas, e perfil
    extrudado virou laje com as pernas enterradas. Esta saiu de tres abordagens independentes
    modeladas e RENDERIZADAS em paralelo, com juri; venceu a que monta massas sobrepostas.
    O que corrige o ursinho e geometrico: cabeca mais larga que alta, olho afundado sob aba de
    sobrancelha, orelha chata para tras, vao entre as patas e juba em COROA - nao cachos no topo."""
    """Shishi (leao-guardiao chines) sentado sobre pedestal xumizuo.
    lado>0 = macho (pata sobre a esfera), lado<0 = femea (pata sobre o filhote). Encara -Y.
    H = altura do leao sentado (sem pedestal); o pedestal tem 0.85H."""
    macho = lado > 0
    B = Builder('LOB_leao_%s' % ('esfera' if lado > 0 else 'filhote'), 770 + (0 if macho else 1))
    S = H / 4.2
    Z0 = 3.57                     # topo do pedestal = 0.85H
    sr = 1 if macho else -1       # lado da pata levantada (quebra o espelho do par)

    def A(bm, key, r=None):
        return B.add(xf(bm, scale=S) if abs(S - 1) > 1e-6 else bm, key, r)

    def L(bm, key, r=None):
        return A(xf(bm, loc=(0, 0, Z0)), key, r)

    def LM(bm, sx, key, r=None):
        return L(mirror_x(bm) if sx < 0 else bm, key, r)

    def marca(t):
        if log: print('BG>   %-10s %5d' % (t, B.tris()))

    # ------------------------------------------------ PEDESTAL (xumizuo: base, cintura estreita, cimalha, lotus)
    A(t_box(-1.98, 1.98, -2.10, 2.10, 0, .40, bev=.09, seg=2), 'pedra', .42)
    A(t_box(-1.80, 1.80, -1.92, 1.92, .40, .72, bev=.07, seg=1), 'pedra', .58)
    A(t_box(-1.44, 1.44, -1.56, 1.56, .72, 2.40, bev=.10, seg=2), 'pedra', .48)
    for sy in (-1, 1):            # cartelas nas 4 faces da cintura
        A(t_box(-1.00, 1.00, sy * 1.56 - .05, sy * 1.56 + .05, 1.02, 2.08, bev=.07, seg=1), 'junta', .28)
    for sx in (-1, 1):
        A(t_box(sx * 1.44 - .05, sx * 1.44 + .05, -.86, .86, 1.02, 2.08, bev=.07, seg=1), 'junta', .28)
    A(t_box(-1.72, 1.72, -1.84, 1.84, 2.40, 2.74, bev=.10, seg=2), 'pedra', .62)
    pet = [(-.26, 0), (.26, 0), (.18, .26), (0, .34), (-.18, .26)]
    for i in range(4):            # lotus na frente
        A(xf(t_prism(pet, 'Y', -.12, .12, bev=.04, seg=1), loc=(-1.05 + 2.10 * i / 3, -1.80, 2.74)), 'pedra', .7)
    for sx in (-1, 1):            # lotus nas laterais
        for i in range(3):
            A(xf(t_prism(pet, 'X', -.12, .12, bev=.04, seg=1), loc=(sx * 1.74, -.90 + 1.80 * i / 2, 2.74)), 'pedra', .72)
    A(t_box(-1.80, 1.80, -1.92, 1.92, 2.94, 3.12, bev=.06, seg=1), 'pedra', .66)
    A(t_box(-1.94, 1.94, -2.06, 2.06, 3.10, Z0, bev=.12, seg=2), 'pedra', .52)
    marca('pedestal')

    # ------------------------------------------------ TRONCO (uma massa so, perfil lateral ESTREITO)
    tronco = [(1.30, .10), (1.46, .80), (1.34, 1.76), (.86, 2.10), (.10, 2.28), (-.52, 2.38),
              (-.86, 2.16), (-.96, 1.62), (-.80, 1.10), (-.30, .96), (.32, .82), (.86, .58), (1.12, .22)]
    L(t_prism(tronco, 'X', -.66, .66, bev=.40, seg=2), 'pedra', .45)
    # flanco: massa torneada que tira a cara de laje das laterais do tronco
    L(xf(t_lathe([(0, -.70), (.44, -.64), (.70, -.30), (.76, .10), (.62, .48), (.36, .66), (0, .72)], 12),
         scale=(1.06, 1.10, .92), loc=(0, .16, 1.62)), 'pedra', .48)
    # peito: BARRIL torneado que EMBRULHA os ombros (prisma chapado virava painel recuado entre caixas)
    L(xf(t_lathe([(0, -.62), (.42, -.58), (.66, -.34), (.74, .06), (.66, .42), (.40, .62), (0, .68)], 13),
         scale=(1.52, 1.00, 1.14), loc=(0, -.60, 1.66)), 'pedra', .52)
    # ancas: coxas TORNEADAS (a placa prismatica virava um disco chapado colado no flanco)
    anca = [(0, -.86), (.52, -.80), (.84, -.44), (.94, .06), (.80, .52), (.46, .80), (0, .90)]
    dedo = [(-.18, 0), (-.18, .15), (-.04, .21), (.10, .15), (.10, 0)]
    for sx in (-1, 1):
        LM(xf(t_lathe(anca, 12), scale=(.52, .86, 1.0), rot=(-8, 0, 0), loc=(.60, .90, 1.02)), sx, 'pedra', .5)
        LM(t_prism([(1.04, 0), (.28, 0), (.20, .32), (.62, .44), (1.10, .36)], 'X', .44, 1.02, bev=.10, seg=1), sx, 'pedra', .62)
        for k in range(3):        # dedos da pata traseira
            LM(xf(t_prism(dedo, 'X', .50 + .17 * k, .65 + .17 * k, bev=.04, seg=1), loc=(0, .38, .03)), sx, 'pedra', .72)
    marca('tronco')

    # ------------------------------------------------ PATAS DIANTEIRAS (ombro cheio, canela fina, pata larga)
    for sx in (-1, 1):
        levanta = (sx == sr)
        LM(t_prism([(-1.34, 2.02), (-.52, 1.96), (-.44, 1.04), (-.80, .80), (-1.30, .90)], 'X', .34, 1.04, bev=.30, seg=2), sx, 'pedra', .56)  # ombro
        if levanta:               # canela para a frente e para baixo, pata sobre a esfera
            LM(t_prism([(-1.28, 1.16), (-.70, 1.10), (-.86, .80), (-1.48, .86)], 'X', .40, .98, bev=.22, seg=2), sx, 'pedra', .6)
            LM(t_prism([(-1.98, 1.32), (-1.90, .88), (-1.32, .78), (-1.02, .92), (-1.12, 1.28), (-1.60, 1.44)], 'X', .36, 1.02, bev=.20, seg=2), sx, 'pedra', .66)
            for k in range(3):
                LM(xf(t_prism(dedo, 'X', .44 + .18 * k, .60 + .18 * k, bev=.04, seg=1), loc=(0, -1.90, .80)), sx, 'pedra', .74)
        else:
            LM(t_prism([(-1.26, 1.10), (-.62, 1.04), (-.64, .34), (-1.24, .32)], 'X', .40, .96, bev=.24, seg=2), sx, 'pedra', .6)
            LM(t_prism([(-1.74, 0), (-.72, 0), (-.68, .30), (-1.14, .46), (-1.66, .40)], 'X', .32, 1.06, bev=.15, seg=2), sx, 'pedra', .66)
            for k in range(3):
                LM(xf(t_prism(dedo, 'X', .38 + .21 * k, .57 + .21 * k, bev=.04, seg=1), loc=(0, -1.60, .02)), sx, 'pedra', .74)
    marca('patas')

    # ------------------------------------------------ PESCOCO
    L(t_prism([(-1.02, 1.98), (-.34, 2.10), (-.06, 2.66), (-.46, 3.10), (-1.12, 2.98), (-1.26, 2.44)], 'X', -.64, .64, bev=.22, seg=2), 'pedra', .5)

    # ------------------------------------------------ CABECA: cranio MAIS LARGO que alto (0.45H x 0.33H)
    HY, HZ = -.86, 2.98
    cranio = [(-.95, .22), (-.88, .52), (-.58, .66), (-.20, .70), (.20, .70), (.58, .66), (.88, .52), (.95, .22),
              (.88, -.22), (.60, -.54), (.22, -.70), (-.22, -.70), (-.60, -.54), (-.88, -.22)]
    L(xf(t_prism(cranio, 'Y', -.62, .44, bev=.26, seg=2), loc=(0, HY, HZ)), 'pedra', .46)
    marca('cranio')
    # juba: disco raso atras do cranio + cachos cobrindo a coroa E as laterais
    juba = [(0, -.44), (.55, -.46), (.90, -.38), (1.05, -.14), (1.09, .16), (.97, .44), (.72, .62), (.38, .72), (0, .76)]
    L(xf(t_lathe(juba, 16), rot=(-90, 0, 0), scale=(1.06, 1, .92), loc=(0, HY + .24, HZ)), 'pedra', .4)
    knob = [(0, 0), (.18, .04), (.23, .14), (.13, .25), (0, .28)]
    for i in range(11):           # coroa interna, do queixo direito ao queixo esquerdo por cima
        a = -24 + 228 * i / 10 + (0 if macho else 6)
        ar = math.radians(a); k = .82 + .42 * math.sin(math.radians(min(180, max(0, a))))
        L(xf(t_lathe(knob, 6), scale=k, rot=(24, 90 - a, 0),
             loc=(1.00 * math.cos(ar), HY - .18, HZ + .92 * math.sin(ar))), 'pedra', .35 + .4 * ((i * 5) % 7) / 7)
    for i in range(7):            # coroa externa, mais atras e maior
        a = -4 + 188 * i / 6 + (0 if macho else 8)
        ar = math.radians(a); k = .88 + .34 * math.sin(math.radians(min(180, max(0, a))))
        L(xf(t_lathe(knob, 6), scale=k * 1.18, rot=(-4, 90 - a, 0),
             loc=(1.12 * math.cos(ar), HY + .30, HZ + 1.02 * math.sin(ar))), 'pedra', .3 + .45 * ((i * 3) % 5) / 5)
    # cachos espalhados pelo FLANCO da juba (raio colhido do proprio perfil; senao de perfil vira casco liso)
    for j, (d, th, kt, ks, r) in enumerate(((-.12, 28, 26, 1.00, 1.05), (-.12, -20, 24, .90, 1.05), (.16, 6, -2, 1.05, 1.09),
                                            (.16, 46, -4, .92, 1.09), (.46, 24, -26, .86, .97), (.46, -14, -28, .80, .97))):
        for sx in (-1, 1):
            LM(xf(t_lathe(knob, 6), scale=ks, rot=(kt, 90 - th, 0),
                  loc=(1.03 * r * math.cos(math.radians(th)), HY + .24 + d, HZ + .89 * r * math.sin(math.radians(th)))),
               sx, 'pedra', .32 + .4 * ((j * 3) % 5) / 5)
    for i in range(3):            # rufo: cachos ASSENTADOS na linha do dorso (nada de bolhas soltas)
        L(xf(t_lathe(knob, 6), scale=.86 - .16 * i, rot=(-74, 0, 0),
             loc=(.34 * (1 if i % 2 else -1), .08 + .36 * i, 2.30 - .13 * i)), 'pedra', .42 + .16 * i)
    marca('juba')

    # ------------------------------------------------ CARA: focinho CURTO e LARGO, nariz grande, boca larga
    FZ = HZ - .24
    L(xf(t_prism([(-.58, .20), (-.50, .32), (0, .38), (.50, .32), (.58, .20), (.56, -.22), (.32, -.48), (-.32, -.48), (-.56, -.22)], 'Y', -1.80, -1.42, bev=.10, seg=1), loc=(0, 0, FZ)), 'pedra', .58)
    for sx in (-1, 1):            # coxins do bigode: os dois lobos que fazem o focinho de felino
        L(xf(t_lathe([(0, 0), (.20, .05), (.28, .15), (.24, .28), (0, .33)], 9), rot=(90, 0, 0), loc=(sx * .27, -1.78, FZ - .16)), 'pedra', .68)
    L(xf(t_prism([(-.30, 0), (-.26, .18), (0, .24), (.26, .18), (.30, 0), (.20, -.14), (-.20, -.14)], 'Y', -1.98, -1.76, bev=.06, seg=1), loc=(0, 0, FZ + .12)), 'pedra', .66)  # nariz grande e chato
    for sx in (-1, 1):
        L(xf(t_box(-.06, .06, -2.01, -1.93, -.06, .05, bev=.02, seg=1), loc=(sx * .15, 0, FZ + .07)), 'corte', .2)
    if macho:                     # boca aberta: cavidade recuada entre os coxins + presas nos cantos
        L(xf(t_box(-.42, .42, -1.76, -1.46, -.26, .0, bev=.04, seg=1), loc=(0, 0, FZ - .28)), 'corte', .15)
        for sx in (-1, 1):
            L(xf(t_prism([(-.09, 0), (.09, 0), (0, -.26)], 'Y', -1.80, -1.64, bev=.02, seg=1), loc=(sx * .31, 0, FZ - .16)), 'creme', .9)
        L(xf(t_prism([(-.36, 0), (.36, 0), (.30, -.24), (-.30, -.24)], 'Y', -1.86, -1.62, bev=.06, seg=1), loc=(0, 0, FZ - .52)), 'pedra', .72)    # queixo
    else:
        L(xf(t_box(-.34, .34, -1.88, -1.74, -.04, .04, bev=.02, seg=1), loc=(0, 0, FZ - .32)), 'corte', .15)
        L(xf(t_prism([(-.38, 0), (.38, 0), (.32, -.26), (-.32, -.26)], 'Y', -1.88, -1.60, bev=.06, seg=1), loc=(0, 0, FZ - .40)), 'pedra', .72)
    cej = crom([Vector((.10, -1.56, HZ + .16)), Vector((.44, -1.66, HZ + .36)), Vector((.82, -1.58, HZ + .18))], 4)
    for sx in (-1, 1):
        LM(t_tube(cej, lerp_list([.11, .17, .11], len(cej)), 7), sx, 'pedra', .74)       # sobrancelha saliente (~0.08H)
        # olho: globo claro esbugalhado + pupila pequena (nunca um buraco preto)
        L(xf(t_lathe([(.17, 0), (.25, .07), (.32, 0), (.25, -.06), (.17, 0)], 8), rot=(-90, 0, 0), loc=(sx * .48, -1.52, HZ + .0)), 'pedra', .8)
        L(xf(t_lathe([(0, 0), (.13, .05), (.18, .13), (.13, .20), (0, .22)], 9), rot=(90, 0, 0), loc=(sx * .48, -1.50, HZ + .0)), 'pedra', .9)
        L(xf(t_lathe([(0, 0), (.085, .01), (.085, .05), (0, .06)], 8), rot=(90, 0, 0), loc=(sx * .48, -1.70, HZ + .0)), 'corte', .1)
        L(xf(t_prism([(-.12, -.17), (.11, -.18), (.19, .02), (.10, .20), (-.07, .22), (-.17, .07)], 'Y', -.05, .05, bev=.04, seg=1),
             rot=(0, 0, -40 * sx), scale=(1, 1, .8), loc=(sx * .86, HY - .14, HZ + .20)), 'pedra', .6)   # orelha chata caida para tras, encostada na juba
    L(xf(t_lathe([(0, 0), (.09, .03), (.11, .10), (.06, .17), (0, .19)], 8), rot=(90, 0, 0), loc=(0, -1.60, HZ + .30)), 'pedra', .8)   # no da testa
    marca('cara')

    # ------------------------------------------------ COLEIRA COM GUIZO (faixa visivel no peito)
    colar = crom([Vector((-.92, -1.00, HZ - 1.30)), Vector((0, -1.30, HZ - 1.00)), Vector((.92, -1.00, HZ - 1.30))], 4)
    L(t_tube(colar, lerp_list([.07, .10, .07], len(colar)), 6), 'ouro', .85)
    L(xf(t_lathe([(0, 0), (.13, .04), (.16, .15), (.11, .25), (0, .28)], 9), rot=(178, 0, 0), loc=(0, -1.28, HZ - 1.06)), 'ouro', .9)

    # ------------------------------------------------ CAUDA: pluma de chama de pedra encostada na anca
    cau = crom([Vector((.42, 1.30, .86)), Vector((.98, 1.80, 1.46)), Vector((1.00, 1.72, 2.10)),
                Vector((.70, 1.38, 2.48)), Vector((.34, 1.02, 2.46))], 4)
    L(t_tube(cau, lerp_list([.42, .34, .27, .20, .13], len(cau)), 7), 'pedra', .56)
    fol = [(-.22, 0), (.22, 0), (.14, .40), (0, .54), (-.16, .36)]
    for k in range(8):            # labaredas deitadas SOBRE a cauda, cada uma seguindo a tangente do caminho
        i = 2 + k * 2; p, q = cau[i], cau[min(i + 2, len(cau) - 1)]
        d = (q - p); d = d.normalized() if d.length > 1e-5 else Vector((0, 0, 1))
        ang = math.degrees(math.atan2(-d.y, d.z)) + (18 if k % 2 else -14)
        L(xf(t_prism(fol, 'X', -.07, .07, bev=.05, seg=1), rot=(ang, 0, 0), scale=.78 + .05 * k,
             loc=(p.x + (.16 if k % 2 else -.16), p.y, p.z)), 'pedra', .5 + .06 * k)
    marca('cauda')

    # ------------------------------------------------ ATRIBUTO SOB A PATA
    if macho:
        L(xf(t_lathe([(0, -.54), (.31, -.46), (.50, -.23), (.54, 0), (.50, .23), (.31, .46), (0, .54)], 14), loc=(sr * .66, -1.66, .54)), 'pedra', .8)
        for k in range(3):        # fitas de brocado na esfera
            L(xf(t_lathe([(.31, 0), (.38, .05), (.31, .10), (.25, .05), (.31, 0)], 12), rot=(74, 0, 60 * k),
                 loc=(sr * .66, -1.66, .54)), 'bronze', .9)
    else:                         # filhote de barriga para cima, brincando sob a pata
        cx, cy = sr * .64, -1.64
        L(xf(t_lathe([(0, -.46), (.26, -.40), (.36, -.12), (.33, .18), (0, .30)], 11), rot=(74, 0, 22), loc=(cx, cy + .16, .44)), 'pedra', .82)
        L(xf(t_lathe([(0, 0), (.24, .06), (.29, .17), (.19, .29), (0, .33)], 10), rot=(-52, 0, 0), loc=(cx - .06, cy - .46, .60)), 'pedra', .86)
        for i in range(6):        # jubinha
            a = 360 * i / 6 + 20
            L(xf(t_lathe([(0, 0), (.10, .02), (.12, .09), (0, .14)], 6), rot=(30, 90 - a, 0),
                 loc=(cx - .06 + .27 * math.cos(math.radians(a)), cy - .58, .60 + .27 * math.sin(math.radians(a)))), 'pedra', .55)
        for k in range(2):        # patinhas para cima
            L(xf(t_prism([(-.09, 0), (.09, 0), (.11, .30), (-.07, .32)], 'X', -.08, .08, bev=.04, seg=1),
                 loc=(cx + (.20 if k else -.16), cy - .12 - .20 * k, .48)), 'pedra', .7)
    marca('atributo')
    return B

def ponte_lua(L=36.0, W=9.0, F=4.2):
    """arco alto de pedra com balaustrada, degraus nas rampas e pedra de fecho. Ao longo de X, centrada."""
    B = Builder('LOB_ponte_lua', 730)
    N = 16
    def z(t):
        # a rampa tem de MORRER no chao: antes o deck somava 1.0 de espessura sobre sin(0)=0 e sobrava
        # um degrau de 1.2 studs na entrada, dos dois lados. Agora a curva comeca negativa o bastante
        # para que topo do deck = 0 nas pontas.
        return F * math.sin(math.pi * t) - 1.0
    for k in range(N):
        t0, t1 = k / N, (k + 1) / N
        x0, x1 = -L / 2 + L * t0, -L / 2 + L * t1
        B.add(t_prism([(x0, z(t0)), (x1, z(t1)), (x1, z(t1) + 1.0), (x0, z(t0) + 1.0)], 'X', -W / 2, W / 2, bev=.06), 'verm', .45 + .25 * (k % 3) / 3)
        d = int(abs(t0 - .5) > .18)                                              # degraus nas rampas
        if d: B.add(t_prism([(x0, z(t0) + 1.0), (x1, z(t0) + 1.0), (x1, z(t0) + 1.25), (x0, z(t0) + 1.25)], 'X', -W / 2, W / 2, bev=.05), 'piso', .5)
    for s in (-1, 1):                                                             # balaustrada
        # PAINEL CHEIO de pedra sob o corrimao. Antes era so o corrimao fino sobre pilaretes, e de longe
        # a ponte lia como tabua com grade; ponte-lua de jardim chines tem guarda-corpo macico.
        for k in range(24):
            t0, t1 = k / 24, (k + 1) / 24
            x0, x1 = -L / 2 + L * t0, -L / 2 + L * t1
            B.add(t_prism([(x0, z(t0) + 1.0), (x1, z(t1) + 1.0), (x1, z(t1) + 1.42), (x0, z(t0) + 1.42)], 'X',
                          *sorted((s * (W / 2 - .12), s * (W / 2 - .72))), bev=.05), 'verm', .42 + .2 * (k % 3) / 3)
            if k % 2 == 0:                                                        # almofada em relevo no painel
                B.add(t_prism([(x0 + .5, z(t0) + 1.14), (x1 - .5, z(t1) + 1.14), (x1 - .5, z(t1) + 1.3), (x0 + .5, z(t0) + 1.3)], 'X',
                              *sorted((s * (W / 2 - .06), s * (W / 2 - .14))), bev=.03), 'junta', .5)
        pts = [Vector((-L / 2 + L * i / 24, s * (W / 2 - .42), z(i / 24) + 1.52)) for i in range(25)]
        B.add(t_sweep([(-.34, 0), (.34, 0), (.34, .3), (-.34, .3)], pts), 'vermS', .6)
        for i in range(0, 25, 3):
            p = pts[i]
            B.add(xf(t_box(-.3, .3, -.3, .3, -1.35, .0, bev=.06), loc=(p.x, p.y, p.z)), 'pedra', .55)
            B.add(xf(t_lathe([(0, 0), (.34, 0), (.4, .16), (.3, .4), (.18, .52), (0, .56)], 10), loc=(p.x, p.y, p.z + .55)), 'pedra', .62)
    B.add(t_box(-1.3, 1.3, -W / 2 - .2, W / 2 + .2, F - .3, F + 1.15, bev=.1), 'pedra', .7)   # pedra de fecho
    for s in (-1, 1):
        B.add(xf(t_prism([(-.9, 0), (-.4, -.4), (0, -.15), (.4, -.4), (.9, 0), (.5, .45), (0, .62), (-.5, .45)], 'Y', 0, .18, bev=.04), loc=(0, s * (W / 2 + .2), F + .35)), 'ouro', .6)
    return B

# ---------------------------------------------------------------- NATUREZA E TREINO
def rocha(seed=1, r=3.2):
    """rocha facetada em cunha (taihu estilizada): massa principal + duas lascas."""
    B = Builder('LOB_rocha_%d' % seed, 740 + seed); rnd = random.Random(seed)
    bm = t_blob(r, (1.25, .95, .85), 1, lobes=4, lobe_amp=.3, seed=seed, flat_bottom=-r * .5)
    bevel_sharp(bm, .18, 1, angle=.35)
    xf(bm, rot=(rnd.uniform(-8, 8), rnd.uniform(-8, 8), rnd.uniform(0, 360)), loc=(0, 0, r * .55))
    B.add(bm, 'pedra', .4)
    for k in range(2):
        a = rnd.uniform(0, math.tau); d = r * .75
        b2 = t_blob(r * rnd.uniform(.3, .5), (1.1, .9, .7), 1, lobes=3, lobe_amp=.35, seed=seed * 10 + k, flat_bottom=-r * .2)
        bevel_sharp(b2, .12, 1, angle=.35)
        xf(b2, rot=(0, 0, rnd.uniform(0, 360)), loc=(math.cos(a) * d, math.sin(a) * d, r * .3))
        B.add(b2, 'pedra', .62)
    return B

def bambu(seed=1, n=7):
    """moita de bambu: colmos com nos, inclinacao leve e folhas em leque no topo."""
    B = Builder('LOB_bambu_%d' % seed, 750 + seed); rnd = random.Random(seed)
    for k in range(n):
        a = rnd.uniform(0, math.tau); d = rnd.uniform(0, 1.9)
        x, y = math.cos(a) * d, math.sin(a) * d
        H = rnd.uniform(9, 16); r = rnd.uniform(.17, .26)
        tilt = rnd.uniform(.02, .07); ta = rnd.uniform(0, math.tau)
        pts = [Vector((x + math.cos(ta) * tilt * z * z / H, y + math.sin(ta) * tilt * z * z / H, z)) for z in [H * i / 8 for i in range(9)]]
        B.add(t_tube(pts, [r * (1 - .3 * i / 8) for i in range(9)], 7), 'bambu', rnd.uniform(.35, .8))
        for i in range(1, 8):
            p = pts[i]; B.add(xf(t_lathe([(r * .95, 0), (r * 1.22, .06), (r * 1.22, .2), (r * .95, .26)], 7), loc=(p.x, p.y, p.z)), 'bambu', .3)
        for f in range(5):                                                        # folhas
            fa = rnd.uniform(0, math.tau); fz = H * rnd.uniform(.72, .97)
            p = Vector((x + math.cos(ta) * tilt * fz * fz / H, y + math.sin(ta) * tilt * fz * fz / H, fz))
            tip = p + Vector((math.cos(fa) * 2.4, math.sin(fa) * 2.4, rnd.uniform(-.7, .9)))
            mid = (p + tip) / 2 + Vector((0, 0, .5))
            B.add(bmesh_tri_prism(p, mid + Vector((math.cos(fa + 1.4) * .34, math.sin(fa + 1.4) * .34, 0)), tip, .06), 'folha', rnd.uniform(.4, .85))
    return B

def bordo(seed=1, H=17.0):
    """BORDO de patio: tronco curto que se abre em pernadas e copa larga em camadas de lente.
    Mesmo motivo da reescrita do pinheiro - a copa de blobs nao tinha aresta para o bevel morder e
    lia como massa de plastilina."""
    B = Builder('LOB_bordo_%d' % seed, 760 + seed); rnd = random.Random(seed)
    r0 = H / 19.0
    NU = 0.34 * H
    pts, raios = [], []
    for i in range(7):
        t = i / 6.0
        pts.append(Vector((math.sin(t * 2.3) * .07 * H, math.cos(t * 1.7) * .05 * H, t * NU * 1.35)))
        raios.append(r0 * (1.45 if i == 0 else (1.0 - .55 * t)))
    B.add(t_tube(pts, raios, 8), 'casca', .45)
    for a in range(4):
        ang = math.radians(90 * a + 30)
        raiz = crom([(0, 0, r0 * 1.3), (math.cos(ang) * r0 * 1.3, math.sin(ang) * r0 * 1.3, r0 * .25),
                     (math.cos(ang) * r0 * 1.9, math.sin(ang) * r0 * 1.9, -.05)], 3)
        B.add(t_tube(raiz, lerp_list([r0 * .4, r0 * .28, r0 * .1], len(raiz)), 6), 'casca', .38)
    topo = pts[-1]
    for i in range(3):                                             # tres pernadas
        ang = math.radians(120 * i + rnd.uniform(-22, 22))
        pta = Vector((math.cos(ang) * H * .22, math.sin(ang) * H * .22, H * .72))
        br = crom([tuple(topo), tuple((topo + pta) / 2 + Vector((0, 0, H * .05))), tuple(pta)], 4)
        B.add(t_tube(br, lerp_list([r0 * .58, r0 * .36, r0 * .2], len(br)), 6), 'casca', .5)
        for k in range(2):
            R = H * (.26 - .06 * k) * rnd.uniform(.9, 1.1)
            esp = R * rnd.uniform(.22, .28)
            pad = _pad_folha(R, esp, lobos=7, amp=.26, entalhes=2, seg=16, seed=seed * 17 + i * 3 + k)
            xf(pad, rot=(rnd.uniform(-7, 7), rnd.uniform(-7, 7), rnd.uniform(0, 360)),
               loc=(pta.x * (1 + .12 * k), pta.y * (1 + .12 * k), pta.z + H * (.06 + .11 * k)))
            B.add(pad, 'bordo', .35 + .2 * (i + k) / 4)
    R = H * .30
    pad = _pad_folha(R, R * .24, lobos=5, amp=.24, entalhes=2, seg=18, seed=seed)
    xf(pad, loc=(0, 0, H * .95)); B.add(pad, 'bordo', .58)
    return B

def poste_treino(H=6.0):
    """poste de madeira cravado, com marcas de uso e uma cinta de corda."""
    B = Builder('LOB_poste_treino', 770)
    B.add(t_lathe([(0, 0), (.62, 0), (.66, H * .5), (.58, H - .3), (.5, H), (0, H)], 12), 'madM', .5)
    for k in range(3):
        z = H * (.45 + .17 * k)
        B.add(xf(t_lathe([(.5, 0), (.7, .04), (.7, .3), (.5, .34)], 12), loc=(0, 0, z)), 'mad', .35)
    B.add(t_lathe([(0, 0), (.9, 0), (.8, .3), (0, .36)], 12), 'pedra', .45)
    return B

def boneco_treino():
    """boneco de palha com poste, bracos de madeira e cintas."""
    B = Builder('LOB_boneco_treino', 771)
    B.add(t_lathe([(0, 0), (.5, 0), (.44, 4.2), (0, 4.4)], 10), 'madM', .5)
    B.add(xf(t_lathe([(0, 0), (1.05, .3), (1.15, 1.4), (.85, 2.3), (0, 2.5)], 12), loc=(0, 0, 2.6)), 'palha' if 'palha' in PAINTS else 'creme', .55)
    B.add(xf(t_blob(.78, (1, 1, 1.15), 1), loc=(0, 0, 5.7)), 'palha' if 'palha' in PAINTS else 'creme', .6)
    B.add(t_box(-2.6, 2.6, -.22, .22, 4.5, .0 + 4.9, bev=.06), 'mad', .5)
    for z in (3.2, 4.2): B.add(xf(t_lathe([(.9, z), (1.12, z + .05), (1.12, z + .3), (.9, z + .35)], 12)), 'tecido', .4)
    return B

def estante_armas(L=8.0):
    """bingqi jia: estante com lancas, alabardas e bastoes."""
    B = Builder('LOB_estante_armas', 772); rnd = random.Random(772)
    B.add(t_box(-L / 2, L / 2, -.9, .9, 0, .55, bev=.09), 'mad', .45)
    for sx in (-1, 1): B.add(t_box(sx * (L / 2 - .4) - .3, sx * (L / 2 - .4) + .3, -.4, .4, .55, 5.2, bev=.07), 'mad', .5)
    for z in (2.4, 4.6): B.add(t_box(-L / 2 + .2, L / 2 - .2, -.3, .3, z, z + .35, bev=.05), 'mad', .55)
    n = 6
    for k in range(n):
        x = -L / 2 + 1.0 + k * (L - 2.0) / (n - 1); h = rnd.uniform(7.5, 9.5)
        B.add(xf(t_lathe([(0, 0), (.14, 0), (.13, h), (0, h)], 7), rot=(rnd.uniform(-3, 3), rnd.uniform(-4, 4), 0), loc=(x, 0, .5)), 'madM', rnd.random())
        tipo = k % 3
        if tipo == 0: B.add(xf(t_prism([(0, 0), (.3, .5), (.14, 1.5), (0, 2.0), (-.14, 1.5), (-.3, .5)], 'Y', -.06, .06, bev=.03), loc=(x, 0, h + .3)), 'aco', .7)
        elif tipo == 1:
            B.add(xf(t_prism([(0, 0), (.22, .4), (.1, 1.2), (0, 1.6), (-.1, 1.2), (-.22, .4)], 'Y', -.05, .05, bev=.03), loc=(x, 0, h + .3)), 'aco', .75)
            B.add(xf(t_prism([(0, .3), (.9, .8), (1.0, 1.3), (.2, 1.0)], 'Y', -.05, .05, bev=.03), loc=(x, 0, h + .3)), 'aco', .6)
        else: B.add(xf(t_lathe([(.13, 0), (.26, .1), (.26, .5), (.13, .6)], 8), loc=(x, 0, h + .2)), 'bronze', .5)
    return B


def banco_nuvem(seed=1):
    """nuvem do banco que fecha a base do penhasco. OPACA de proposito: a cor aqui e assada em atlas e
    nao existe alpha, entao nevoa tem de ser MALHA com degrade assado, nunca transparencia."""
    B = Builder('LOB_nuvem', 29); rnd = random.Random(909)
    for k in range(9):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0, 9)
        r = rnd.uniform(4.5, 9.5)
        B.add(xf(t_blob(r, (1.35, 1.0, .34), 2, lobes=5, lobe_amp=.2, seed=k, flat_bottom=-.22 * r),
                 loc=(math.cos(a) * d, math.sin(a) * d, rnd.uniform(-1.6, 1.6))),
              'nevoa', .70 + .10 * (k % 4) / 4)
    return B

def cascata(seed=1):
    """queda d'agua do perimetro: TRES laminas defasadas para dar volume sem alpha, mais a espuma no
    labio e a bruma embaixo. Nasce no labio do primeiro patamar e morre no banco de nuvem."""
    B = Builder('LOB_cascata', 27); rnd = random.Random(404)
    H = 44.0
    for k in range(3):
        w = 4.6 - k * 1.1
        dy = -.35 * k
        pts = [Vector((0, dy, 0)), Vector((1.2, dy - .8, -H * .3)), Vector((1.0, dy - 1.6, -H * .66)), Vector((1.6, dy - 2.2, -H))]
        B.add(t_sweep([(-w, 0), (w, 0), (w, .42), (-w, .42)], crom([tuple(p) for p in pts], 7)),
              'agua', .55 + .18 * k)
    B.add(xf(t_blob(3.4, (1.5, .9, .5), 2, lobes=5, lobe_amp=.24, seed=3), loc=(0, 0, .5)), 'creme', .85)
    for k in range(5):                                                  # bruma na base
        B.add(xf(t_blob(rnd.uniform(2.4, 4.6), (1.4, 1.0, .42), 1, lobes=4, lobe_amp=.3, seed=k),
                 loc=(rnd.uniform(-3, 4), rnd.uniform(-4, 1), -H + rnd.uniform(-2, 3))), 'creme', rnd.uniform(.7, .95))
    return B


# constantes do monumento (vinham do escopo de modulo do rascunho vencedor)
_PC = Vector((0.0, -0.40, 8.80))          # centro da perola = centro da volta
_RP = 2.35
_AL = math.radians(55)                    # plano da volta deitado 55 graus: a helice SOBE enquanto gira
_E1 = Vector((1, 0, 0)); _E2 = Vector((0, math.sin(_AL), math.cos(_AL))); _NN = _E1.cross(_E2)
_NUCA = Vector((-3.40, -1.20, 14.20))
_FACE = Vector((0.86, -0.28, -0.42))      # cabeca quase deitada: o observador ve o PERFIL dela
_CAUDA = [(6.40, 1.60, 9.40), (6.20, 3.00, 7.90), (5.20, 4.40, 6.50), (3.00, 5.30, 5.70),
          (0.00, 5.45, 5.55), (-2.90, 4.90, 5.95), (-4.40, 3.40, 6.55), (-4.30, 1.30, 6.95)]
_PESC = [(-2.95, 0.05, 12.35), (-3.45, -0.75, 13.35)]
PC, RP, AL, E1, E2, NN = _PC, _RP, _AL, _E1, _E2, _NN
NUCA, FACE, CAUDA, PESC = _NUCA, _FACE, _CAUDA, _PESC

# ---------------------------------------------------------------- MONUMENTO DO PATIO
# O brief novo pediu, conforme a referencia, "um monumento central de dragao dourado envolvendo uma
# esfera luminosa". Substitui a picareta que estava aqui (pedida numa rodada anterior); deixei a
# picareta_ancestral no arquivo caso o usuario queira reaproveita-la em outro ponto do lobby.
# Saiu de tres abordagens modeladas e RENDERIZADAS em paralelo, com juri; venceu a que constroi a
# silhueta lateral primeiro e so depois engrossa por partes.
def _volta(s):
    """ponto da volta em s=0..1: 300 graus em torno da perola, subindo 3.1 ao longo do eixo (helice, nao anel)."""
    fi = math.radians(195 + 300 * s)
    h = -1.50 + 3.10 * s
    d = 3.95 - .62 * s
    return PC + E1 * (d * math.cos(fi)) + E2 * (d * math.sin(fi)) + NN * h


def _espinha():
    """CAUDA baixa por tras, com a ponta abanando no ar a direita -> VOLTA de 300 graus em torno da perola
    (entra pela esquerda embaixo por tras, cruza a frente EMBAIXO, sobe pela direita, passa por cima ATRAS,
    e sai em cima a esquerda, deixando um VAO aberto onde se ve a perola) -> PESCOCO em S ate a nuca."""
    key = list(CAUDA); rr = [.15, .26, .40, .54, .66, .76, .84, .88]
    NA = 20
    for i in range(NA):
        s = i / (NA - 1.0)
        key.append(tuple(_volta(s))); rr.append(.92 + .26 * s)
    key += PESC + [tuple(NUCA)]
    rr += [1.12, 1.04, .96]
    cp = crom(key, 3)
    return cp, lerp_list(rr, len(cp))


def _frame(Fv, roll=0.0):
    Xl = Vector(Fv).normalized()
    Yl = Vector((0, 0, 1)).cross(Xl)
    Yl = Yl.normalized() if Yl.length > 1e-5 else Vector((0, 1, 0))
    Zl = Xl.cross(Yl).normalized()
    if roll:
        R = Matrix.Rotation(math.radians(roll), 3, Xl); Yl = R @ Yl; Zl = R @ Zl
    return Xl, Yl, Zl


# ================================================================== MODO SILHUETA (chapa fina no plano XZ)
def _fita(B, pts, rad, key, th=0.16, rnd=.5):
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = Vector((b.x - a.x, 0, b.z - a.z))
        if d.length < 1e-6: continue
        nv = Vector((-d.z, 0, d.x)).normalized()
        ra, rb = rad[i], rad[i + 1]
        poly = [(a.x + nv.x * ra, a.z + nv.z * ra), (b.x + nv.x * rb, b.z + nv.z * rb),
                (b.x - nv.x * rb, b.z - nv.z * rb), (a.x - nv.x * ra, a.z - nv.z * ra)]
        try: B.add(t_prism(poly, 'Y', -th, th), key, rnd)
        except ValueError: pass


def silhueta():
    B = Builder('D3_sil', 780)
    cp, cr = _espinha()
    _fita(B, [Vector((p.x, 0, p.z)) for p in cp], cr, 'ouro')
    per = [(0, -RP)] + [(RP * math.cos(math.radians(a)), RP * math.sin(math.radians(a))) for a in range(-78, 79, 18)] + [(0, RP)]
    B.add(xf(t_lathe(per, 18), loc=(PC.x, 0, PC.z)), 'chama', .85)
    Xl, Yl, Zl = _frame(Vector((FACE.x, 0, FACE.z)))
    M = Matrix(((Xl.x, 0, Zl.x), (Xl.y, 1, Zl.y), (Xl.z, 0, Zl.z)))
    cab = [(-.50, .95), (.20, 1.30), (.85, 1.20), (1.45, 1.45), (2.05, 1.20), (2.80, 1.00), (3.50, .92),
           (3.95, 1.05), (4.30, .72), (4.20, .25), (3.60, .02), (2.60, -.18), (1.60, -.30),
           (3.55, -1.45), (3.65, -1.85), (2.70, -2.05), (1.75, -1.85), (1.10, -1.40), (.40, -1.05), (-.40, -.90)]
    B.add(xf(t_prism(cab, 'Y', -.18, .18), rot=M, loc=NUCA), 'ouro', .5)
    def W(p): return NUCA + Xl * p[0] + Vector((0, 1, 0)) * p[1] + Zl * p[2]
    for s in (-1, 1):
        _fita(B, [W(q) for q in ((.60, 0, 1.25), (-.05, 0, 1.85), (-.95, 0, 2.10), (-1.75, 0, 2.00), (-2.30, 0, 1.75))], [.30, .23, .17, .11, .05], 'creme')
        _fita(B, [W(q) for q in ((-.90, 0, 2.05), (-1.40, 0, 2.45), (-1.80, 0, 2.60))], [.13, .09, .035], 'creme')
        _fita(B, [W(q) for q in ((3.80, 0, .10), (4.80, 0, .45), (5.55, 0, .05), (5.30, 0, -.75), (4.30, 0, -1.40))], [.14, .11, .08, .05, .025], 'creme')
    return B


# ================================================================== MODO VOLUME
def meu_dragao(H=17.0):
    S = H / 17.0
    B = Builder('LOB_dragao_perola', 780)

    def A(bm, key, r=None):
        return B.add(xf(bm, scale=S) if abs(S - 1) > 1e-6 else bm, key, r)

    def octo(r, rot=22.5):
        return [(r * math.cos(math.radians(rot + 45 * i)), r * math.sin(math.radians(rot + 45 * i))) for i in range(8)]

    def placa(p, ux, uz, poly, th, key, rnd=.5):
        """chapa desenhada no plano (ux=ao longo, uz=para fora) e extrudada na espessura th."""
        uy = uz.cross(ux).normalized()
        M = Matrix(((ux.x, uy.x, uz.x), (ux.y, uy.y, uz.y), (ux.z, uy.z, uz.z)))
        return A(xf(t_prism(poly, 'Y', -th, th), rot=M, loc=p), key, rnd)

    # ---------------------------------------------------------- PEDESTAL octogonal em patamares (0 -> 5)
    A(t_prism(octo(8.60), 'Z', 0.00, 0.62, bev=.14, seg=2), 'pedra', .42)
    A(t_prism(octo(8.05), 'Z', 0.62, 1.28, bev=.12, seg=2), 'pedra', .52)
    A(t_prism(octo(7.45), 'Z', 1.28, 1.92, bev=.12, seg=2), 'pedra', .60)
    A(t_prism(octo(6.85), 'Z', 1.92, 3.86, bev=.10, seg=2), 'verm', .46)
    ap = 6.85 * math.cos(math.radians(22.5))
    for i in range(8):
        a = math.radians(45 * i); cx, cy = ap * math.cos(a), ap * math.sin(a)
        A(xf(t_box(-2.10, 2.10, -.20, .20, 2.20, 3.58, bev=.07, seg=1), rot=(0, 0, 45 * i + 90), loc=(cx, cy, 0)), 'ouro', .62)
        A(xf(t_box(-1.78, 1.78, -.14, .14, 2.38, 3.40, bev=.05, seg=1), rot=(0, 0, 45 * i + 90), loc=(cx * 1.005, cy * 1.005, 0)), 'junta', .30)
        A(xf(t_lathe([(0, 0), (.44, 0), (.36, .10), (.20, .13), (0, .16)], 10), rot=(-90, 0, 45 * i - 90), loc=(cx * 1.04, cy * 1.04, 2.90)), 'ouro', .70)
    A(t_prism(octo(7.42), 'Z', 3.86, 4.36, bev=.14, seg=2), 'pedra', .64)
    A(t_prism(octo(7.05), 'Z', 4.36, 5.00, bev=.12, seg=2), 'pedra', .56)
    A(t_prism(octo(6.30), 'Z', 4.92, 5.10, bev=.06, seg=1), 'bronze', .60)
    # rochedo: um morro de pedra e cinco volutas de nuvem de ouro (nao batatas soltas)
    A(xf(t_blob(3.90, (1.20, 1.20, .30), 2, lobes=5, lobe_amp=.20, seed=5, flat_bottom=-.35), loc=(0, -.4, 5.25)), 'pedra', .48)
    for i, a in enumerate((30, 100, 170, 250, 320)):
        ar = math.radians(a); r = 4.55
        A(xf(t_lathe([(0, 0), (1.35, .08), (1.50, .48), (1.05, .86), (.42, 1.02), (0, 1.05)], 10),
             scale=(1.10, .74, .80), rot=(0, 0, a), loc=(r * math.cos(ar), -.4 + r * math.sin(ar), 5.02)), 'ouro', .55 + .06 * (i % 3))

    # ---------------------------------------------------------- PEROLA (lisa, sem enfeite)
    per = [(0, -RP)] + [(RP * math.cos(math.radians(a)), RP * math.sin(math.radians(a))) for a in range(-78, 79, 12)] + [(0, RP)]
    A(xf(t_lathe(per, 22), loc=PC), 'chama', .85)

    # ---------------------------------------------------------- CORPO
    cp, cr = _espinha()
    A(t_tube(cp, cr, 14), 'ouro', .50)
    n = len(cp)

    def nobody(i):
        i = max(1, min(n - 2, i)); p = cp[i]
        t = (cp[i + 1] - cp[i - 1]).normalized()
        o = p - PC
        o = (o - t * o.dot(t)); o = o.normalized() if o.length > 1e-5 else Vector((0, 0, 1))
        return p, t, o, cr[i]

    # crista dorsal: labaredas BAIXAS e deitadas para tras (nao espinhos radiais)
    chama = [(-.62, 0), (.46, 0), (.34, .40), (.02, .62), (-.52, .40), (-.88, .18)]
    for i in range(4, n - 2, 3):
        p, t, o, r = nobody(i)
        k = .62 + .95 * (i / n)
        placa(p + o * (r * .82), t, o, [(a * k, b * k) for a, b in chama], .09, 'verm' if i % 2 else 'vermS', .45 + .3 * (i % 5) / 5)

    # fiadas de escamas: tres placas largas e rasas na parte de cima, espacadas
    esc = [(-.30, 0), (.30, 0), (.22, .09), (0, .13), (-.22, .09)]
    for i in range(5, n - 3, 3):
        p, t, o, r = nobody(i)
        sd = t.cross(o).normalized()
        for lado in (-1, 0, 1):
            d = (o * math.cos(math.radians(40 * lado)) + sd * math.sin(math.radians(40 * lado))).normalized()
            placa(p + d * (r * .92), t, d, [(a * r * 1.5, b * r * 1.5) for a, b in esc], .04, 'bronze', .55 + .3 * (i % 4) / 4)
    # barriga: faixas largas na face de dentro
    for i in range(4, n - 4, 3):
        p, t, o, r = nobody(i)
        placa(p - o * (r * .88), t, -o, [(-.22, 0), (.22, 0), (.17, .09), (-.17, .09)], r * .60, 'bronze', .50)

    p0, t0, o0, r0 = nobody(2)                         # leque de chama na ponta da cauda
    sd0 = t0.cross(o0).normalized()
    for k, (ang, sz) in enumerate(((0, 1.35), (36, 1.05), (-36, 1.05), (70, .72), (-70, .72))):
        d = (o0 * math.cos(math.radians(ang)) + sd0 * math.sin(math.radians(ang))).normalized()
        a = p0 - t0 * .22; b = p0 + t0 * .22; c = p0 + d * sz - t0 * .60
        A(bmesh_tri_prism(a, b, c, .12), 'verm', .5 + .08 * k)

    # ---------------------------------------------------------- PATAS (4 curtas, garra de 4 dedos)
    def pata(punho, dv, uv, sz):
        dv = Vector(dv).normalized(); uv = Vector(uv).normalized()
        sd = dv.cross(uv).normalized(); uv = sd.cross(dv).normalized()
        A(xf(t_blob(sz * .62, (1.25, 1.05, .72), 1), loc=punho - uv * sz * .10), 'ouro', .58)
        for k, ang in enumerate((-50, -17, 17, 50)):
            d = (dv * math.cos(math.radians(ang)) + sd * math.sin(math.radians(ang))).normalized()
            g = crom([tuple(punho + d * sz * .42), tuple(punho + d * sz * .98 - uv * sz * .24), tuple(punho + d * sz * 1.32 - uv * sz * .82)], 3)
            A(t_tube(g, lerp_list([sz * .23, sz * .14, sz * .03], len(g)), 6), 'creme', .80 + .04 * k)

    def perna(ombro, cotovelo, punho, dv, uv, sz, rombro=.98):
        ombro = Vector(ombro)
        A(xf(t_blob(rombro, (1.05, 1.0, .90), 2), loc=ombro), 'ouro', .52)
        path = crom([tuple(ombro), tuple(Vector(cotovelo)), tuple(Vector(punho))], 5)
        A(t_tube(path, lerp_list([rombro * .80, rombro * .46, sz * .50], len(path)), 8), 'ouro', .55)
        A(xf(t_blob(sz * .50, (1.0, .82, .82), 1, lobes=4, lobe_amp=.30, seed=3), loc=Vector(cotovelo)), 'verm', .50)
        pata(Vector(punho), dv, uv, sz)

    # dianteira direita: AGARRA A PEROLA por cima-frente (e esta garra que conta a historia)
    perna(_volta(.85) + Vector((.45, -.55, -.35)), (1.90, -.95, 10.95), (1.05, -2.45, 10.05),
          (-.58, -.46, -.68), (.40, -.72, .57), 1.08)
    # dianteira esquerda: aberta no ar, a esquerda
    perna(_volta(.955) + Vector((-.55, -.35, -.40)), (-3.60, -1.10, 10.90), (-4.85, -1.95, 9.45),
          (-.35, -.62, -.70), (.32, -.36, .88), 1.02)
    # traseira direita: apoiada no rochedo, na frente
    perna(_volta(.30) + Vector((.45, -.30, -.30)), (3.40, -3.25, 5.90), (4.55, -2.95, 5.35),
          (.55, -.62, -.56), (.20, .12, .97), .98, rombro=.90)
    # traseira esquerda: apoiada no rochedo, na frente
    perna(_volta(.12) + Vector((-.45, -.30, -.30)), (-3.90, -2.85, 5.85), (-4.90, -2.45, 5.35),
          (-.62, -.55, -.56), (.18, .15, .97), .92, rombro=.86)

    # ---------------------------------------------------------- CABECA (massas redondas; nada de placa chapada)
    Xl, Yl, Zl = _frame(FACE)
    M = Matrix(((Xl.x, Yl.x, Zl.x), (Xl.y, Yl.y, Zl.y), (Xl.z, Yl.z, Zl.z)))

    def Hd(bm, key, r=None): return A(xf(bm, rot=M, loc=NUCA), key, r)
    def W(p): return NUCA + Xl * p[0] + Yl * p[1] + Zl * p[2]

    Hd(xf(t_blob(1.16, (1.08, 1.02, .96), 2), loc=(.80, 0, .28)), 'ouro', .50)                      # cranio
    Hd(xf(t_blob(.80, (1.32, .92, .84), 2), loc=(2.05, 0, .10)), 'ouro', .54)                       # focinho: massa grossa junto ao cranio
    Hd(xf(t_blob(.64, (1.48, .84, .78), 2), loc=(3.40, 0, -.02)), 'ouro', .56)                      # focinho: massa fina adiante (afina = camelo)
    Hd(xf(t_blob(.44, (.95, 1.10, .98), 1), loc=(4.30, 0, .06)), 'ouro', .62)                       # bulbo do nariz
    Hd(xf(t_lathe([(0, 0), (.44, .05), (.36, .32), (.16, .44), (0, .48)], 10), loc=(.58, 0, 1.02)), 'ouro', .64)   # bossa da testa (chimu)
    for s in (-1, 1):
        Hd(xf(t_blob(.46, (1.10, .78, .58), 1), loc=(1.52, s * .76, .80)), 'ouro', .60)             # arcada da sobrancelha
        Hd(xf(t_blob(.58, (1.15, .88, .84), 1), loc=(1.62, s * .68, -.30)), 'ouro', .55)            # bochecha
        Hd(xf(t_blob(.13, (1, 1, .8), 1), loc=(4.36, s * .30, .24)), 'corte', .15)                  # narina
    Hd(t_prism([(1.50, -.30), (2.80, -.40), (3.90, -.44), (4.38, -.34), (4.30, -.62), (3.40, -.76), (2.30, -.76), (1.50, -.62)],
               'Y', -.54, .54, bev=.08, seg=2), 'ouro', .58)                                        # labio superior, enfiado sob o focinho
    jaw = [(0, 0), (1.20, -.06), (2.30, -.16), (2.75, -.44), (1.90, -.74), (.70, -.72), (-.05, -.46)]
    bmj = t_prism(jaw, 'Y', -.50, .50, bev=.14, seg=2); xf(bmj, rot=(0, 28, 0)); xf(bmj, loc=(1.35, 0, -.55))
    Hd(bmj, 'ouro', .60)                                                                            # mandibula, boca bem aberta
    Hd(xf(t_box(-1.05, 1.05, -.42, .42, -.18, .18, bev=.04, seg=1), rot=(0, 18, 0), loc=(2.55, 0, -1.16)), 'corte', .12)
    Hd(xf(t_prism([(-.66, 0), (.60, -.05), (.34, .22), (-.60, .24)], 'Y', -.26, .26, bev=.05, seg=1), rot=(0, 22, 0), loc=(2.50, 0, -1.28)), 'verm', .40)
    for s in (-1, 1):
        for x in (2.15, 2.80, 3.45):
            Hd(xf(t_lathe([(0, 0), (.11, 0), (.045, .32), (0, .38)], 7), rot=(180, 0, 0), loc=(x, s * .46, -.60)), 'creme', .85)
        for x in (2.45, 3.20):
            Hd(xf(t_lathe([(0, 0), (.10, 0), (.04, .30), (0, .36)], 7), rot=(0, 20, 0), loc=(x, s * .40, -1.58)), 'creme', .85)
    for s in (-1, 1):                                                                               # olhos salientes sob a arcada
        Hd(xf(t_blob(.36, (1.0, .82, .95), 1), loc=(1.68, s * .84, .40)), 'creme', .88)
        Hd(xf(t_blob(.175, (1, .9, 1), 1), loc=(1.84, s * .94, .40)), 'corte', .12)
        Hd(xf(t_prism([(-.22, -.18), (.20, -.24), (.32, .06), (.11, .28), (-.20, .20)], 'Y', -.07, .07, bev=.04, seg=1), loc=(.22, s * 1.02, .52)), 'ouro', .70)
    for s in (-1, 1):                                                                               # chifres de veado, curtos e jogados para TRAS
        hp = crom([tuple(W(q)) for q in ((.50, s * .52, 1.16), (-.15, s * .76, 1.58), (-1.05, s * .88, 1.72), (-1.85, s * .84, 1.58), (-2.42, s * .70, 1.28))], 4)
        A(t_tube(hp, lerp_list([.33, .25, .18, .11, .05], len(hp)), 7), 'bronze', .58)
        f1 = crom([tuple(W(q)) for q in ((-1.00, s * .86, 1.70), (-1.45, s * 1.16, 2.00), (-1.88, s * 1.28, 2.10))], 4)
        A(t_tube(f1, lerp_list([.15, .10, .04], len(f1)), 6), 'bronze', .60)
        f2 = crom([tuple(W(q)) for q in ((-1.78, s * .86, 1.58), (-2.10, s * 1.02, 1.92), (-2.34, s * 1.10, 2.06))], 4)
        A(t_tube(f2, lerp_list([.11, .08, .03], len(f2)), 6), 'bronze', .62)
    for s in (-1, 1):                                                                               # bigodes: saem do nariz e voltam para TRAS, ondulando
        bg = crom([tuple(W(q)) for q in ((4.35, s * .52, .10), (5.25, s * .92, .34), (5.60, s * 1.54, -.10), (4.95, s * 2.10, -.72), (3.70, s * 2.44, -1.28), (2.35, s * 2.50, -1.60))], 5)
        A(t_tube(bg, lerp_list([.15, .13, .10, .07, .045, .02], len(bg)), 6), 'creme', .80)
        bb = crom([tuple(W(q)) for q in ((3.10, s * .34, -1.75), (3.25, s * .50, -2.48), (2.70, s * .60, -3.10))], 4)
        A(t_tube(bb, lerp_list([.16, .10, .035], len(bb)), 6), 'creme', .76)
    for s in (-1, 1):                                                                               # barba de fogo sob o queixo
        placa(W((1.05, s * .42, -1.30)), -Xl, Vector(Zl) * -1, [(-.28, 0), (.28, 0), (.20, .50), (-.06, .72), (-.42, .48)], .09, 'verm', .55)
    # juba: tufos DEITADOS para tras, em volta da nuca e descendo pelo pescoco
    for k in range(9):
        a = math.radians(-105 + 210 * k / 8)
        p = W((.10, 1.05 * math.sin(a), .20 + 1.00 * math.cos(a)))
        o = (p - W((.10, 0, .20))).normalized()
        placa(p, -Xl, o, [(-.30, 0), (.30, 0), (.22, .55), (-.05, .82), (-.45, .58), (-.72, .26)], .10,
              'verm' if k % 2 else 'vermS', .42 + .35 * (k % 4) / 4)

    xs = [v.co.x for v in B.bm.verts]; ys = [v.co.y for v in B.bm.verts]; zs = [v.co.z for v in B.bm.verts]
    print('BG> bbox x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f  raio %.2f' %
          (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs), max(math.hypot(v.co.x, v.co.y) for v in B.bm.verts)))
    return B


# ================================================================== execucao

# ---------------------------------------------------------------- ROCHA (forma-base refeita)
# O usuario reprovou a versao anterior com precisao: "volumes bege separados, formados por camadas
# geometricas empilhadas", "aneis de volumes claros muito repetidos, com espacos azuis entre eles",
# "nao tente resolver isso somente afastando, afinando ou aumentando os modelos atuais. REVISE A
# FORMA-BASE". O penhasco antigo era prisma de 7 lados com 3 degraus concentricos e o pico
# empilhava 5 niveis decrescentes - empilhamento regular, zero verticalidade.
# Esta versao saiu de tres abordagens modeladas e RENDERIZADAS em paralelo, com juri, e venceu a
# que constroi a rocha como FEIXE DE COLUNAS VERTICAIS fundidas: os modulos encaixam lado a lado
# formando parede continua, sem buraco azul e sem leitura de anel.
def _perf_rocha(rnd, r, n=6, irr=.30, ecc=1.0, a0=None, cx=0.0, cy=0.0):
    """secao horizontal de uma coluna de rocha: poligono irregular anti-horario."""
    a0 = rnd.uniform(0, math.tau) if a0 is None else a0
    pts = []
    for i in range(n):
        a = a0 + math.tau * i / n + rnd.uniform(-.20, .20)
        rr = r * (1 + irr * rnd.uniform(-1, 1))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr * ecc))
    return pts

def _fuste(poly, niveis, rnd=None, jit=0.0, bev=0.0, seg=1, topo=True, base=True):
    """COLUNA: a secao `poly` e repetida em cada nivel (z, escala, dx, dy) e os aneis sao costurados.
    Da conicidade, inclinacao e barriga de graca; `jit` quebra as arestas verticais retas."""
    bm = bmesh.new(); rings = []
    for (z, s, dx, dy) in niveis:
        ring = []
        for (x, y) in poly:
            k = 1.0 + (jit * rnd.uniform(-1, 1) if (jit and rnd) else 0.0)
            ring.append(bm.verts.new((x * s * k + dx, y * s * k + dy, z)))
        rings.append(ring)
    n = len(poly)
    for a, b in zip(rings, rings[1:]):
        for i in range(n):
            try: bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
            except ValueError: pass
    for ring, rev, ok in ((rings[0], True, base), (rings[-1], False, topo)):
        if ok:
            try: bm.faces.new(ring[::-1] if rev else ring)
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bevel_sharp(bm, bev, seg)
    return bm

def _niveis(z0, z1, escalas, dx=0.0, dy=0.0, curva=1.7, zs=None):
    """niveis entre z0 (base) e z1 (topo) com as escalas dadas; (dx,dy) = recuo da BASE em relacao ao
    topo (pe encolhido = penhasco em balanco, nunca caixa). zs = reparticao vertical nao uniforme."""
    m = len(escalas); out = []
    for i, s in enumerate(escalas):
        t = i / (m - 1) if zs is None else zs[i]
        k = (1 - t) ** curva
        out.append((z0 + (z1 - z0) * t, s, dx * k, dy * k))
    return out

def penhasco(seed=0):
    """MODULO DO CINTURAO (passo 17): feixe de colunas verticais fundidas, de larguras MUITO diferentes,
    com o RITMO sorteado pela seed - nenhum modulo repete o desenho do outro.
    Encaixe lateral: a coluna da borda esquerda e recuada e a da direita avancada, as duas passam do
    meio-passo; no encontro uma fica na frente da outra e a junta some. A cortina escura atras fecha a
    parede inteira, entao nunca aparece ceu entre os dedos. Topo plano em z=0 (o lobby assenta nele);
    so a franja de mato e dois dentes de rocha do labio passam disso."""
    B = Builder('LOB_penhasco_%d' % seed, 30 + seed)
    rnd = random.Random(1700 + seed * 37)
    P = 17.0                                   # passo do cinturao
    XB = P * .5 + 1.2                          # borda: invade o vizinho

    # ---- 1. CORTINA: colunas largas e achatadas atras. Parede fechada + fundo escuro entre os dedos.
    #        Desce MAIS que a maioria da frente, para o pe da frente ter sempre rocha escura atras.
    x = -XB - 1.2; i = 0
    while x < XB + 1.2:
        r = rnd.uniform(5.2, 6.6)
        pol = _perf_rocha(rnd, r, 7, .15, ecc=.55, cx=x, cy=rnd.uniform(.4, 2.0))
        B.add(_fuste(pol, _niveis(-24.0 - rnd.uniform(0, 6.0), 0.0, (.58, .80, .93, 1.0), dy=2.0, curva=1.3),
                     rnd, .035, bev=.35), 'junta', .18 + .13 * (i % 3))
        x += r * rnd.uniform(1.0, 1.25); i += 1

    # ---- 2. FRENTE: torroes de larguras sorteadas. O CORPO da parede e macico ate uns -20; so dois
    #        torroes por modulo descem em dedo ate -34. Pe quase sempre quebrado em toco (largo), nunca
    #        uma franja de pontas iguais.
    fr = []                                     # (x, y, raio, z do pe, escala do pe)
    rE = rnd.uniform(4.2, 5.1)
    fr.append((-XB, -2.5 - rnd.uniform(0, .6), rE, -26.0 - rnd.uniform(0, 4.0), rnd.uniform(.55, .78)))
    x, r = -XB, rE
    fundo = []
    while True:
        r2 = rnd.uniform(2.6, 6.4)
        x2 = x + (r + r2) * rnd.uniform(.48, .62)
        if x2 + r2 * .5 > XB - 1.6: break
        fr.append([x2, -rnd.uniform(2.6, 5.4), r2, -17.5 - rnd.uniform(0, 5.5), rnd.uniform(.62, 1.0)])
        fundo.append(len(fr) - 1)
        x, r = x2, r2
    rD = rnd.uniform(4.2, 5.1)
    fr.append((XB, -5.4 - rnd.uniform(0, .8), rD, -27.0 - rnd.uniform(0, 4.0), rnd.uniform(.55, .78)))
    for k in rnd.sample(fundo, min(2, len(fundo))):          # os dois dedos que descem fundo
        fr[k][3] = -29.0 - rnd.uniform(0, 5.0); fr[k][4] = rnd.uniform(.20, .38)
    for i, (x, y, r, zb, pe) in enumerate(fr):
        pol = _perf_rocha(rnd, r, 6, .26, ecc=.80, cx=x, cy=y)
        esc = (pe, pe * .35 + .52, .82, .92, .98, 1.0)
        B.add(_fuste(pol, _niveis(zb, 0.0, esc, dy=-rnd.uniform(1.6, 3.6), curva=1.9,
                                  zs=(0, .26, .52, .72, .88, 1.0)), rnd, .05, bev=.30),
              'pedra', .30 + .16 * (i % 4))

    # ---- 3. SULCO: lasca escura ENFIADA na junta de duas colunas - e a sombra que separa um torrao do
    #        outro; sem ela as colunas viram uma so parede lisa
    for a, b in zip(fr, fr[1:]):
        if rnd.random() < .70:
            xm = (a[0] + a[2] + b[0] - b[2]) * .5
            ym = max(a[1], b[1]) + rnd.uniform(.8, 1.8)
            zt = -rnd.uniform(.5, 6.0); h = rnd.uniform(10.0, 20.0)
            pol = _perf_rocha(rnd, rnd.uniform(.9, 1.5), 4, .22, ecc=.45, cx=xm, cy=ym)
            B.add(_fuste(pol, _niveis(zt - h, zt, (.25, .70, 1.0), dy=-1.0), rnd, .07, bev=.16),
                  'casca_escura' if rnd.random() < .4 else 'junta', .25 + rnd.uniform(0, .25))

    # ---- 4. ESPOROES: contrafortes encostados na face, topos em cotas MUITO diferentes = silhueta
    #        quebrada. Largos e curtos: eles engrossam a parede, nao a transformam em pente.
    for k in range(4):
        x = -XB + rnd.uniform(0, 2 * XB)
        r = rnd.uniform(1.9, 3.6)
        zt = -rnd.uniform(1.0, 11.0)
        pol = _perf_rocha(rnd, r, 5, .30, ecc=.72, cx=x, cy=-7.1 - rnd.uniform(0, 1.4))
        B.add(_fuste(pol, _niveis(zt - rnd.uniform(8.0, 19.0), zt, (.48, .70, .90, 1.0), dy=-1.6, curva=1.5),
                     rnd, .06, bev=.24), 'pedra' if k % 3 else 'junta', .42 + .14 * (k % 4))

    # ---- 5. FRANJA de mato no labio: pecas sobrepostas de larguras, alturas e quedas diferentes, COM
    #        falhas (nunca uma fita verde continua), mais dois dentes de rocha que quebram o topo reto
    x = -XB - .6
    while x < XB:
        w = rnd.uniform(1.5, 3.4)
        if rnd.random() < .18: x += w * 1.4; continue                  # falha: rocha nua no labio
        pol = _perf_rocha(rnd, w, 6, .38, ecc=.24, cx=x + w * .8, cy=-6.5 - rnd.uniform(0, 1.3))
        B.add(t_prism(pol, 'Z', -.8 - rnd.uniform(0, 3.4), .06 + rnd.uniform(0, .62), bev=.2, seg=1),
              'pinho' if rnd.random() < .72 else 'folha', .40 + rnd.uniform(0, .32))
        x += w * rnd.uniform(1.15, 1.55)
    for k in range(2):
        xd = -XB + rnd.uniform(1.5, 2 * XB - 1.5)
        pol = _perf_rocha(rnd, rnd.uniform(1.0, 1.9), 5, .30, ecc=.5, cx=xd, cy=-7.1 - rnd.uniform(0, .8))
        B.add(_fuste(pol, _niveis(-4.0, rnd.uniform(.7, 1.4), (.9, 1.0, .74, .40), curva=1.0),
                     rnd, .06, bev=.2), 'pedra', .55 + .2 * k)
    for k in range(2):                          # dois tufos fundos, dentro das fendas
        pol = _perf_rocha(rnd, rnd.uniform(1.0, 1.6), 5, .32, ecc=.55,
                          cx=-XB + rnd.uniform(1, 2 * XB - 1), cy=-7.0 - rnd.uniform(0, 1.0))
        z = -rnd.uniform(4.0, 12.0)
        B.add(t_prism(pol, 'Z', z - .6, z + rnd.uniform(.5, 1.1), bev=.22, seg=1), 'pinho', .45 + .2 * k)
    return B

def pico(seed=0):
    """MONTANHA DE FUNDO: mesma linguagem do penhasco - FEIXE de agulhas verticais fundidas, de alturas
    diferentes, convergindo para um cume FORA do centro. Nao ha degrau concentrico nem cone: o que da a
    forma e a silhueta serrilhada do feixe. Um pedestal largo e escuro amarra os pes (nada de volumes
    soltos boiando). Nuvem NAO entra aqui: nuvem e o banco_nuvem, com linguagem propria de blob macio."""
    B = Builder('LOB_pico_%d' % seed, 28 + seed)
    rnd = random.Random(910 + seed * 53)
    H = 62.0 + seed * 23.0
    R0 = H * .34
    ad = rnd.uniform(0, math.tau)
    sx, sy = math.cos(ad) * R0 * .26, math.sin(ad) * R0 * .26      # cume deslocado do centro da base

    # ---- 1. FEIXE: 11 massas verticais GORDAS e fundidas. A altura cai com a distancia ao cume, entao
    #        a silhueta e um macico serrilhado e assimetrico - nunca um cone nem um bolo de niveis.
    ags = [(0.0, 0.0)]
    for anel, (d, n) in enumerate(((.42, 4), (.78, 6))):
        for j in range(n):
            a = math.tau * (j + rnd.uniform(-.20, .20)) / n + anel * .8 + ad
            ags.append((math.cos(a) * R0 * d * rnd.uniform(.86, 1.10),
                        math.sin(a) * R0 * d * rnd.uniform(.86, 1.10)))
    for i, (x, y) in enumerate(ags):
        d = math.hypot(x - sx, y - sy) / R0
        h = H * max(.20, (1 - .70 * d ** .92)) * rnd.uniform(.82, 1.06)
        r = R0 * (.54 - .17 * d) * rnd.uniform(.86, 1.12)
        pol = _perf_rocha(rnd, r, 6, .28, ecc=rnd.uniform(.62, .95), cx=x, cy=y)
        conv = .26 + .14 * d                                       # topo puxado para o eixo do cume
        B.add(_fuste(pol, _niveis(-7.0, h, (1.0, .96, .88, .77, .64, .48, .30),
                                  dx=-(sx - x) * conv, dy=-(sy - y) * conv, curva=1.15),
                     rnd, .065, bev=.45),
              'monteS' if (i % 4 == 3) else 'monte', .40 + .05 * (i % 5))

    # ---- 1b. CUME NEVADO: uma calota clara no alto de cada agulha alta. A 700 studs a silhueta
    #        sozinha nao diz "montanha"; a faixa de neve diz, e nao custa geometria nova de verdade.
    for (x, y) in ags[:5]:
        d = math.hypot(x - sx, y - sy) / R0
        h = H * max(.20, (1 - .70 * d ** .92))
        if h < H * .60: continue
        r = R0 * (.54 - .17 * d) * .52
        B.add(t_prism(_perf_rocha(rnd, r, 6, .26, ecc=.8, cx=x - (sx - x) * .26, cy=y - (sy - y) * .26),
                      'Z', h * .78, h * .995, bev=.4, seg=1), 'monteN', .5)

    # ---- 2. CONTRAFORTES: massas baixas encostadas no pe, para o macico nao nascer do chao em parede
    for k in range(4):
        a = ad + rnd.uniform(0, math.tau)
        d = R0 * rnd.uniform(.95, 1.25)
        x, y = math.cos(a) * d, math.sin(a) * d
        r = R0 * rnd.uniform(.22, .36)
        pol = _perf_rocha(rnd, r, 6, .30, ecc=.85, cx=x, cy=y)
        B.add(_fuste(pol, _niveis(-7.0, H * rnd.uniform(.12, .30), (1.0, .88, .70, .46),
                                  dx=-math.cos(a) * r * .8, dy=-math.sin(a) * r * .8, curva=1.0),
                     rnd, .07, bev=.4), 'monteS' if k % 2 else 'monte', .42 + .04 * (k % 3))

    # ---- 3. SULCOS: lascas escuras enfiadas entre as massas - a fenda vertical que da escala e altura
    for k in range(4):
        a = ad + math.pi * .3 + k * 1.7
        d = R0 * rnd.uniform(.40, .80)
        x, y = sx + math.cos(a) * d, sy + math.sin(a) * d
        pol = _perf_rocha(rnd, R0 * rnd.uniform(.10, .16), 4, .26, ecc=.34, a0=a + 1.57, cx=x, cy=y)
        B.add(_fuste(pol, _niveis(-4.0, H * rnd.uniform(.45, .80), (.9, 1.0, .78, .50, .22),
                                  dx=-math.cos(a) * R0 * .10, dy=-math.sin(a) * R0 * .10, curva=1.0),
                     rnd, .08, bev=.3), 'monteS', .38 + .03 * k)

    # ---- 4. VERDE: so no pe e em prateleiras baixas, rente a rocha (nunca placa boiando no flanco)
    for k in range(7):
        a = rnd.uniform(0, math.tau); d = R0 * rnd.uniform(.60, 1.15)
        t = rnd.uniform(.0, .20)
        pol = _perf_rocha(rnd, R0 * rnd.uniform(.16, .30), 6, .34, ecc=.8,
                          cx=math.cos(a) * d + sx * t, cy=math.sin(a) * d + sy * t)
        z = H * t
        B.add(t_prism(pol, 'Z', z - 2.6, z + rnd.uniform(.3, 1.2), bev=.3, seg=1),
              'monteS', .44 + .03 * (k % 4))
    return B
# =================================================================== COLAR EM k_lobby.py (fim)


# =================================================================== SERRA DE FUNDO
# Terceira tentativa, e as duas anteriores ensinaram o mesmo:
#
#  1a) pico() ampliado - feixe de agulhas crespas esticado para 200 studs. Cada faceta virou uma faixa
#      chapada de vinte studs: leu como CHAPA CORRUGADA. Peca de kit ampliada nao vira cenario.
#  2a) faixas de serra enfileiradas em anel - a silhueta ficou certa, mas apareceu HACHURA fina por
#      toda a montanha. Nao era tinta nem ruido de shader (troquei a paleta e desliguei o ruido, e a
#      hachura continuou): eram os segmentos VIZINHOS se sobrepondo quase no mesmo plano, dois
#      poligonos disputando o mesmo pixel. Reduzir a quantidade so diminuiu, porque basta UM par.
#
# A unica forma de garantir que nao existe superficie coplanar e nao existir emenda: aqui a serra e um
# ANEL FECHADO, malha unica, colocada uma vez. E o mesmo motivo pelo qual a neve nao e uma capa POR
# CIMA da rocha e sim a FAIXA DE CIMA da mesma cortina, dividida na cota da neve - as duas bandas
# encostam pela aresta, nunca se empilham.
def _serra_perfil(a, seed, cumes):
    """altura normalizada em funcao do angulo. Tudo em harmonicas INTEIRAS do circulo, para o perfil
    fechar exatamente em a=0 e a=2pi: uma emenda de altura no fecho e tao visivel quanto uma emenda
    de geometria."""
    h = .50
    for (k, amp, fase) in ((2, .16, .7 * seed), (3, .11, 1.9 * seed), (5, .07, .4 * seed),
                           (7, .05, 2.6 * seed), (11, .030, 1.2 * seed), (17, .016, .9 * seed)):
        h += amp * math.sin(k * a + fase)
    for (ac, amp, larg) in cumes:                       # cume = gaussiana larga no angulo, nunca pico agudo
        d = abs((a - ac + math.pi) % math.tau - math.pi)
        h += amp * math.exp(-(d / larg) ** 2)
    return h


def anel_serra(nome, R=470.0, alt=150.0, prof=150.0, gy=1.05, n=150, seed=1, zb=-150.0, neve=.62):
    """CORTINA circular fechada: sem emenda, logo sem duas superficies disputando o mesmo pixel.

    A versao anterior desta funcao ainda hachurava, e a medicao mostrou por que: 624 vertices
    coincidentes num total de 1248, ou seja, METADE da malha desenhada em dobro. Eu emitia a faixa
    linha->dentro tanto na banda de rocha quanto na de neve. A cortina e uma so e cada trecho dela
    pertence a UMA banda:
        fora   -> linha    rocha, saia externa do pe ate a cota da neve
        linha  -> crista   neve  (onde nao ha neve as duas coincidem e o quad e pulado)
        crista -> dentro   rocha, encosta de tras
    """
    B = Builder(nome, 60 + seed)
    rnd = random.Random(1200 + seed * 37)
    cumes = [(rnd.uniform(0, math.tau), rnd.uniform(.30, .62), rnd.uniform(.16, .34)) for _ in range(rnd.randint(5, 7))]
    hs = [_serra_perfil(math.tau * i / n, seed, cumes) for i in range(n)]
    m = max(hs); mn = min(hs)
    hs = [alt * (.26 + .74 * (h - mn) / (m - mn + 1e-6)) for h in hs]
    for i in range(n):                                  # degrau lateral: tira a curva unica lisa
        if rnd.random() < .18: hs[i] *= rnd.uniform(.82, .94)
    corte = sorted(hs)[int(n * neve)]                   # cota da neve
    def raio_fora(i):
        return R + prof * .5 * (1 + .10 * math.sin(7 * math.tau * i / n))
    def z_neve(i):
        return hs[i] if hs[i] <= corte else max(corte, hs[i] - alt * .17)
    def r_neve(i):
        return R if hs[i] <= corte else R + prof * .06
    def mk(bm, i, rr, z):
        a = math.tau * i / n
        return bm.verts.new((math.cos(a) * rr, math.sin(a) * rr * gy, z))
    # --- banda de rocha: saia externa + encosta de tras, numa malha so
    bmR = bmesh.new()
    fora = [mk(bmR, i, raio_fora(i), zb) for i in range(n)]
    linR = [mk(bmR, i, r_neve(i), z_neve(i)) for i in range(n)]
    criR = [mk(bmR, i, R, hs[i]) for i in range(n)]
    dent = [mk(bmR, i, R - prof * .34, zb * .55) for i in range(n)]
    for (a_, b_) in ((fora, linR), (criR, dent)):
        for i in range(n):
            j = (i + 1) % n
            try: bmR.faces.new((a_[i], a_[j], b_[j], b_[i]))
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bmR, faces=bmR.faces)
    # --- banda de neve: SO o trecho entre a cota da neve e a crista, e so onde ha neve
    bmN = bmesh.new()
    linN = [mk(bmN, i, r_neve(i), z_neve(i)) for i in range(n)]
    criN = [mk(bmN, i, R, hs[i]) for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        if hs[i] <= corte and hs[j] <= corte: continue  # sem neve aqui: o quad seria de area zero
        try: bmN.faces.new((linN[i], linN[j], criN[j], criN[i]))
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bmN, faces=bmN.faces)
    B.add(bmR, 'monte', .48)
    if bmN.faces: B.add(bmN, 'monteN', .56)
    else: bmN.free()
    return B


def anel_nevoa(nome, R=400.0, larg=70.0, alt=34.0, gy=1.06, n=120, seed=1, zb=-120.0):
    """FAIXA de nevoa, tambem em anel fechado. Os blobs do banco_nuvem, ampliados e enfileirados, liam
    como fileira de travesseiros - cada um com contorno e sombra propria. Nevoa opaca so funciona se
    nao tiver contorno para o olho pegar."""
    B = Builder(nome, 70 + seed)
    bm = bmesh.new()
    def h(i):
        a = math.tau * i / n
        v = .55 + .22 * math.sin(3 * a + seed) + .13 * math.sin(7 * a + 2 * seed) + .08 * math.sin(13 * a)
        return max(.16, v)
    def P(i, rr, z):
        a = math.tau * i / n
        return bm.verts.new((math.cos(a) * rr, math.sin(a) * rr * gy, z))
    fora = [P(i, R + larg * .5, zb) for i in range(n)]
    topo = [P(i, R, alt * h(i)) for i in range(n)]
    dentro = [P(i, R - larg * .5, zb) for i in range(n)]
    for (a_, b_) in ((fora, topo), (topo, dentro)):
        for i in range(n):
            j = (i + 1) % n
            try: bm.faces.new((a_[i], a_[j], b_[j], b_[i]))
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    B.add(bm, 'nevoa', .62)
    return B


# =================================================================== PICARETA "FURIA DA AURORA"
# MONUMENTO DA PRACA, no lugar do dragao.
#
# O pedido foi picareta MAGICA, com a "Dwarven Pickaxe Handpainted" do Sketchfab como referencia
# (imagem 42.png). O modelo nao era baixavel (HTTP 403 confirmado), e o usuario mandou no lugar a
# foice "Desolate Devil" com a instrucao de ADAPTAR AQUELA FOICE. E o que esta aqui: a meia-lua nao
# foi desenhada, foi RECORTADA da malha da foice.
#
# O que veio da foice, literalmente: a ilha da lamina do Desolator.fbx, sem o colo espinhoso, cortada
# no plano X e espelhada - as duas meias-luas sao 3.872 dos 9.988 triangulos e trazem o acabamento
# esculpido original (recortes, vincos, espinhos do dorso). A lamina da foice era fina demais para
# monumento (raiz de 0,53), entao cada vertice foi empurrado para LONGE da polilinha do gume: o gume
# nao se mexe um milimetro, a curva assinatura da foice fica intacta, e a massa cresce so para dentro
# (raiz de 0,53 para 1,28). Engaste, gema, garras, virolas, cabo e pomo sao do kit.
#
# A malha fica em picareta_aurora.blend e nao e reconstruida a cada build: o recorte depende de
# indices de ilha e de planos de corte medidos naquele FBX, e refazer isso a cada geracao seria
# fragil a toa. Aqui ela so e anexada e reempacotada num Builder, slot por slot, preservando a cor
# de vertice ('rnd') que o bake usa.
#
# Limite honesto do pipeline: a cor aqui e ASSADA em atlas RGB, sem alfa e sem emissivo, entao o
# verde e MATERIA (gemas, veio de jade rente ao gume, ranhuras das virolas) e nunca o halo luminoso
# da referencia. Nao ha como fugir disso sem mudar o pipeline inteiro.
PIC_BLEND = 'picareta_aurora.blend'
PIC_MALHA = 'MON_picareta_aurora'
PIC_ALT = 19.28                                       # altura da malha como esta no arquivo

def minha_picareta(H=19.0):
    import os
    B = Builder('LOB_picareta_aurora', 777)
    cam = os.path.join(os.path.dirname(os.path.abspath(__file__)), PIC_BLEND)
    nome = PIC_MALHA
    if nome not in bpy.data.meshes:
        with bpy.data.libraries.load(cam) as (dados, alvo): alvo.meshes = [nome]
    me = bpy.data.meshes[nome]
    esc = H / PIC_ALT
    # um bmesh por slot de material: o Builder monta os slots a partir das tintas que recebe, entao a
    # malha precisa voltar separada por tinta. 'P_ouro' -> 'ouro'.
    fonte = bmesh.new(); fonte.from_mesh(me)
    lay = fonte.loops.layers.color.get('rnd')
    for idx, mat in enumerate(me.materials):
        if mat is None: continue
        key = mat.name[2:] if mat.name.startswith('P_') else mat.name
        faces = [f for f in fonte.faces if f.material_index == idx]
        if not faces: continue
        bm = bmesh.new()
        lay2 = bm.loops.layers.color.new('rnd')
        vmap = {}
        for f in faces:
            vs = []
            for v in f.verts:
                if v not in vmap: vmap[v] = bm.verts.new(v.co * esc)
                vs.append(vmap[v])
            try: nf = bm.faces.new(vs)
            except ValueError: continue
            if lay is not None:
                for lo, lb in zip(f.loops, nf.loops): lb[lay2] = lo[lay]
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        B.add(bm, key, rnd='keep')
    fonte.free()
    return B
