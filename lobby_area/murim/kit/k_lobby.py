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


def penhasco(seed=1):
    """bloco de penhasco do cinturao da borda. MASTER: e instanciado ~90 vezes pelo montador, porque
    num Builder unico os 90 blocos estouram o teto de 20 mil tris do importador.
    Faces largas e facetadas, topo com musgo, e uma fenda vertical para a silhueta nao virar caixa."""
    B = Builder('LOB_penhasco_%d' % seed, 30 + seed); rnd = random.Random(700 + seed)
    W, D, H = 18.0, 15.0, 26.0
    n = 7
    pts = []
    for i in range(n):
        a = math.tau * i / n
        r = 1.0 + .26 * math.sin(3.1 * a + seed)
        pts.append((math.cos(a) * W * .5 * r, math.sin(a) * D * .5 * r))
    B.add(t_prism(pts, 'Z', -H, 0, bev=.55, seg=1), 'pedra', .38 + .1 * (seed % 3))
    for k in range(3):                                                  # degraus de estratificacao
        z = -H * (.28 + k * .24)
        p2 = [(x * (1.0 + .06 * (k + 1)), y * (1.0 + .06 * (k + 1))) for (x, y) in pts]
        B.add(t_prism(p2, 'Z', z, z + 1.1, bev=.3, seg=1), 'junta', .3 + .14 * k)
    p3 = [(x * .82, y * .82) for (x, y) in pts]                         # topo com musgo
    B.add(t_prism(p3, 'Z', -.4, .9, bev=.4, seg=1), 'pinho', .45 + .12 * (seed % 2))
    for k in range(4):                                                  # lascas soltas no pe
        a = rnd.uniform(0, 6.28)
        B.add(xf(t_prism([(0, 0), (2.6, .9), (3.1, 3.0), (.6, 3.6)], 'Z', 0, rnd.uniform(2.0, 4.5), bev=.25),
                 rot=(0, 0, rnd.uniform(0, 360)),
                 loc=(math.cos(a) * W * .46, math.sin(a) * D * .46, -H * rnd.uniform(.5, .9))), 'pedra', rnd.uniform(.3, .6))
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
              'creme', .72 + .26 * (k % 4) / 4)
    return B

def pico(seed=1):
    """pico de fundo, puramente cenografico: silhueta importa, detalhe nao. Tres templates reusados em
    escalas diferentes; os mais distantes ganham valor mais claro para somir na nevoa."""
    B = Builder('LOB_pico_%d' % seed, 28); rnd = random.Random(300 + seed)
    # base MUITO mais larga e pico mais baixo: com raio 22 e altura 86+ eles saiam como lajes bege
    # estreitas boiando no ceu, sem leitura de montanha. Montanha distante e larga e baixa.
    H = 58.0 + seed * 11
    n = 7
    for nivel in range(5):
        t = nivel / 4.0
        z0, z1 = H * t * .90, H * ((t + .28) if nivel < 4 else 1.0)
        r = 62.0 * (1 - t * .86) + 5
        pts = []
        for i in range(n):
            a = math.tau * i / n + nivel * .4
            rr = r * (1.0 + .3 * math.sin(2.3 * a + seed * 1.7))
            pts.append((math.cos(a) * rr, math.sin(a) * rr))
        B.add(t_prism(pts, 'Z', z0, z1, bev=.9, seg=1), 'pedra', .25 + .17 * nivel)
    for k in range(3):                                                  # capa clara no alto
        z = H * (.74 + k * .085)
        r = 11.0 * (1 - k * .3)
        B.add(xf(t_lathe([(0, 0), (r, 0), (r * .6, 2.2), (0, 3.0)], 7), loc=(0, 0, z)), 'creme', .8 + .06 * k)
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
