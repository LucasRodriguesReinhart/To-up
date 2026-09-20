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
def leao(lado=1):
    """shishi sobre pedestal: corpo agachado, juba em cachos, boca aberta, pata sobre esfera (lado 1) ou filhote (-1).
    Virado para -Y. Altura ~7."""
    B = Builder('LOB_leao_%s' % ('esfera' if lado > 0 else 'filhote'), 720 + (0 if lado > 0 else 1))
    B.add(t_box(-2.6, 2.6, -3.4, 3.4, 0, .6, bev=.1, seg=3), 'pedra', .45)
    B.add(t_box(-2.3, 2.3, -3.1, 3.1, .6, 2.4, bev=.14, seg=3), 'pedra', .55)
    for a in (0, 90, 180, 270):
        B.add(xf(t_box(-1.4, 1.4, -3.16, -2.9, 1.0, 2.0, bev=.07), rot=(0, 0, a)), 'pedra', .7)
    B.add(t_box(-2.5, 2.5, -3.3, 3.3, 2.4, 2.8, bev=.1, seg=3), 'pedra', .6)
    z0 = 2.8
    B.add(xf(t_blob(1.5, (.85, 1.35, 1.0), 2), loc=(0, .55, z0 + 1.6)), 'pedra', .5)              # corpo
    for sx in (-1, 1):                                                                             # patas
        B.add(xf(t_box(-.45, .45, -1.3, .5, 0, 1.5, bev=.16, seg=3), loc=(sx * .95, -1.5, z0)), 'pedra', .58)
        B.add(xf(t_blob(.52, (1, 1.15, .8), 1), loc=(sx * .95, -2.5, z0 + .45)), 'pedra', .62)
        B.add(xf(t_box(-.5, .5, -.5, .6, 0, 1.9, bev=.18, seg=3), loc=(sx * 1.15, 1.5, z0)), 'pedra', .55)
    B.add(xf(t_blob(1.25, (1.05, .95, 1.0), 2, lobes=7, lobe_amp=.2, seed=3), loc=(0, -1.15, z0 + 3.0)), 'pedra', .52)   # cabeca
    for i in range(14):                                                                            # juba
        a = math.radians(360 * i / 14 + 12); r = 1.35
        B.add(xf(t_blob(.42, (1, 1, .9), 1, seed=i), loc=(r * math.cos(a) * .9, -.55 + .3 * math.sin(a), z0 + 3.0 + r * math.sin(a) * .85)), 'pedra', .45 + .3 * ((i * 3) % 5) / 5)
    B.add(xf(t_blob(.62, (1.05, .85, .72), 1), loc=(0, -2.15, z0 + 2.7)), 'pedra', .62)            # focinho
    B.add(xf(t_box(-.44, .44, -.38, .38, -.2, .2, bev=.08), loc=(0, -2.45, z0 + 2.45)), 'corte', .3)
    for sx in (-1, 1):
        B.add(xf(t_blob(.24, (1, .75, 1), 1), loc=(sx * .55, -2.05, z0 + 3.25)), 'pedra', .75)
        B.add(xf(t_blob(.12, (1, .7, 1), 1), loc=(sx * .62, -2.3, z0 + 3.25)), 'corte', .2)
    if lado > 0: B.add(xf(t_blob(.85, (1, 1, 1), 2, lobes=8, lobe_amp=.12), loc=(-.95, -2.8, z0 + .85)), 'pedra', .8)
    else: B.add(xf(t_blob(.62, (.9, 1.1, .9), 1, lobes=5, lobe_amp=.18), loc=(.95, -2.7, z0 + .7)), 'pedra', .78)
    tail = crom([(0, 1.9, z0 + 1.2), (.7, 2.6, z0 + 2.2), (.4, 2.3, z0 + 3.2), (-.3, 2.7, z0 + 3.6)], 4)
    B.add(t_tube(tail, lerp_list([.35, .3, .25, .4], len(tail)), 7), 'pedra', .6)
    return B

# ---------------------------------------------------------------- PONTE-LUA
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
