# k_kit2.py - segunda leva do kit (secao 7 do briefing): estandarte, suporte de espada, vaso, modulo de muro, pilar de muro,
# telhado de duas aguas para o portao pequeno. O portao em si e MONTAGEM de pecas ja existentes (coluna, arquitrave, prancha,
# dougong simples) + este telhado: e o kit trabalhando como kit.
import math, random
import bmesh
from mathutils import Vector, Matrix
from k_core import *
from k_props import crom, lerp_list, bmesh_tri_prism
import k_madeira

CHAMA = [(0, -.72), (.42, -.5), (.56, -.12), (.4, .22), (.22, .05), (.16, .42), (0, .78), (-.12, .4), (-.3, .18), (-.44, .3), (-.56, -.1), (-.42, -.5)]

def _octo(r, rot=22.5):
    return [(r * math.cos(math.radians(rot + 45 * i)), r * math.sin(math.radians(rot + 45 * i))) for i in range(8)]

def estandarte():
    """estandarte da seita: base de pedra, mastro com ponteira de lanca, travessa, pano vermelho ondulado com barras de ouro,
    emblema (espada sobre chama) e borlas. Pano virado para -Y. Altura ~21."""
    B = Builder('KIT_estandarte', 601)
    B.add(t_prism(_octo(1.5), 'Z', 0, .45, bev=.08), 'pedra', .45)
    B.add(t_prism(_octo(1.15), 'Z', .45, 1.25, bev=.12, seg=3), 'pedra', .58)
    B.add(t_lathe([(0, 1.25), (.62, 1.25), (.66, 1.4), (.5, 1.62), (.42, 1.7), (0, 1.7)], 16), 'bronze', .5)
    H = 19.5
    B.add(t_lathe([(0, 1.6), (.34, 1.6), (.36, H * .35), (.3, H * .8), (.24, H), (0, H)], 14), 'mad', .5)
    for z in (5.2, 12.4): B.add(t_lathe([(.3, z), (.42, z + .05), (.42, z + .3), (.3, z + .35)], 14), 'ouro', .55)
    B.add(t_lathe([(0, H), (.3, H), (.36, H + .25), (.2, H + .5), (.14, H + .62), (0, H + .62)], 12), 'bronze', .55)        # bucha
    B.add(xf(t_prism([(0, 0), (.42, .55), (.16, 1.15), (0, 2.1), (-.16, 1.15), (-.42, .55)], 'Y', -.07, .07, bev=.03), loc=(0, 0, H + .6)), 'ouro', .6)   # lanca
    zt = H - 1.2                                                                                                              # travessa
    B.add(xf(t_lathe([(0, -2.3), (.13, -2.3), (.15, 0), (.13, 2.3), (0, 2.3)], 8), rot=(0, 90, 0), loc=(0, -.42, zt)), 'mad', .5)
    for sx in (-1, 1): B.add(xf(t_blob(.24, (1, 1, 1), 1), loc=(sx * 2.3, -.42, zt)), 'ouro', .6)
    B.add(t_box(-.1, .1, -.5, 0, zt - .1, zt + .1), 'bronze', .5)
    # pano: grade ondulada com espessura (nao e um plano)
    W, Hp, NX, NZ = 3.6, 11.5, 8, 22
    bm = bmesh.new(); top = zt - .25
    def P(i, j, side):
        x = -W / 2 + W * i / NX; z = top - Hp * j / NZ
        wave = .16 * math.sin(j * .55 + i * .35) * (j / NZ) ** .7 + .05 * math.sin(i * 1.3)
        cut = 0.0
        if j == NZ: cut = .9 * (1 - abs(2 * i / NX - 1))                      # ponta em V invertido (rabo de andorinha)
        return Vector((x, -.42 + wave + side * .045, z + cut))
    F = [[bm.verts.new(P(i, j, -1)) for i in range(NX + 1)] for j in range(NZ + 1)]
    K = [[bm.verts.new(P(i, j, 1)) for i in range(NX + 1)] for j in range(NZ + 1)]
    for j in range(NZ):
        for i in range(NX):
            bm.faces.new((F[j][i], F[j][i + 1], F[j + 1][i + 1], F[j + 1][i])); bm.faces.new((K[j][i + 1], K[j][i], K[j + 1][i], K[j + 1][i + 1]))
    for j in range(NZ):
        bm.faces.new((F[j][0], F[j + 1][0], K[j + 1][0], K[j][0])); bm.faces.new((F[j + 1][NX], F[j][NX], K[j][NX], K[j + 1][NX]))
    for i in range(NX):
        bm.faces.new((F[0][i + 1], F[0][i], K[0][i], K[0][i + 1])); bm.faces.new((F[NZ][i], F[NZ][i + 1], K[NZ][i + 1], K[NZ][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = True
    B.add(bm, 'tecido', .5)
    # barras de ouro: a de baixo fica ACIMA do recorte em V e bem a frente do pano (na 1a versao a ondulacao a encobria no meio)
    B.add(t_box(-W / 2 - .04, W / 2 + .04, -.56, -.30, top - .75, top - .2, bev=.03), 'ouro', .6)
    B.add(t_box(-W / 2 - .04, W / 2 + .04, -.74, -.24, top - Hp + 2.0, top - Hp + 2.5, bev=.03), 'ouro', .6)
    zc = top - Hp * .42                                                                                                       # emblema
    B.add(xf(t_lathe([(0, 0), (1.35, 0), (1.35, .06), (1.18, .1), (1.18, .06), (0, .06)], 20), rot=(90, 0, 0), loc=(0, -.5, zc)), 'ouro', .55)
    B.add(xf(t_prism([(a * 1.25, b * 1.25) for a, b in CHAMA], 'Y', -.66, -.56, bev=.03), loc=(0, 0, zc - .05)), 'ouro', .62)
    B.add(xf(t_prism([(0, -1.05), (.12, -.62), (.12, .5), (-.12, .5), (-.12, -.62)], 'Y', -.74, -.66, bev=.02), loc=(0, 0, zc)), 'creme', .7)
    B.add(t_box(-.44, .44, -.76, -.66, zc + .5, zc + .64, bev=.02), 'bronze', .6)
    for sx in (-1, 1):                                                                                                        # borlas
        x = sx * (W / 2 - .15); zb = top - Hp + .2
        B.add(xf(t_blob(.15, (1, 1, 1), 1), loc=(x, -.42, zb)), 'ouro', .6)
        B.add(xf(t_lathe([(0, 0), (.07, 0), (.2, -1.0), (0, -1.08)][::-1], 8), loc=(x, -.42, zb - .08)), 'ouro', .5)
    return B

def suporte_espada():
    """pedestal de pedra com uma jian cravada de ponta para baixo: marco pequeno de caminho. Altura ~10."""
    B = Builder('KIT_suporte_espada', 602)
    B.add(t_box(-2.0, 2.0, -2.0, 2.0, 0, .55, bev=.1, seg=3), 'pedra', .45)
    B.add(t_box(-1.6, 1.6, -1.6, 1.6, .55, 1.15, bev=.1, seg=3), 'pedra', .55)
    B.add(t_prism(_octo(1.3), 'Z', 1.15, 3.1, bev=.14, seg=3), 'pedra', .6)
    for i in range(8):
        a = math.radians(45 * i); r = 1.23
        B.add(xf(t_box(-.32, .32, -.05, .05, 1.5, 2.75, bev=.04), rot=(0, 0, 45 * i + 90), loc=(r * math.cos(a), r * math.sin(a), 0)), 'pedra', .72)
    B.add(t_prism(_octo(1.5), 'Z', 3.1, 3.5, bev=.1, seg=3), 'pedra', .66)
    B.add(t_prism(_octo(.75), 'Z', 3.5, 3.72, bev=.05), 'bronze', .5)
    z0 = 3.6                                                                                                                 # lamina (secao em losango)
    bl = t_prism([(0, 0), (.5, .35), (.5, 4.2), (0, 4.45), (-.5, 4.2), (-.5, .35)], 'Y', -.09, .09, bev=.05)
    B.add(xf(bl, loc=(0, 0, z0)), 'aco', .6)
    B.add(xf(t_box(-.05, .05, -.11, .11, .3, 4.1), loc=(0, 0, z0)), 'aco', .8)                                                # nervura central
    zg = z0 + 4.4                                                                                                            # guarda em asa
    B.add(xf(t_prism([(-1.35, .1), (-1.05, -.22), (-.35, -.3), (0, -.12), (.35, -.3), (1.05, -.22), (1.35, .1), (.9, .34), (.3, .42), (-.3, .42), (-.9, .34)], 'Y', -.24, .24, bev=.07), loc=(0, 0, zg)), 'bronze', .55)
    B.add(xf(t_blob(.2, (1, 1, 1), 1), loc=(0, -.26, zg + .08)), 'ouro', .6)
    B.add(xf(t_lathe([(0, 0), (.2, 0), (.24, .9), (.2, 1.8), (0, 1.8)], 10), loc=(0, 0, zg + .38)), 'mad', .5)                # punho
    for k in range(3): B.add(xf(t_lathe([(.19, 0), (.28, .04), (.28, .16), (.19, .2)], 10), loc=(0, 0, zg + .55 + k * .55)), 'ouro', .6)
    B.add(xf(t_lathe([(0, 0), (.22, 0), (.4, .16), (.42, .4), (.26, .62), (0, .7)], 12), loc=(0, 0, zg + 2.15)), 'ouro', .55)  # pomo
    tas = crom([(0, .1, zg + 2.5), (.35, .25, zg + 2.2), (.55, .3, zg + 1.4), (.5, .3, zg + .6)], 4)                           # borla pendurada
    B.add(t_tube(tas, [.045] * len(tas), 5), 'tecido', .5)
    B.add(xf(t_lathe([(0, 0), (.08, 0), (.24, -.95), (0, -1.02)][::-1], 8), loc=(.5, .3, zg + .62)), 'tecido', .45)
    return B

def vaso():
    """vaso torneado de bronze com faixa jade, filetes de ouro e duas alcas em argola. Altura ~3.4."""
    B = Builder('KIT_vaso', 603)
    B.add(t_lathe([(0, 0), (.85, 0), (.95, .12), (.8, .3), (.95, .55), (1.45, 1.35), (1.5, 1.85), (1.25, 2.45), (.8, 2.85), (.72, 3.05), (.95, 3.3), (1.0, 3.42), (.82, 3.42), (.62, 3.1), (0, 3.1)], 20), 'bronze', .5)
    B.add(t_lathe([(1.34, 1.2), (1.5, 1.32), (1.54, 1.86), (1.36, 2.22)], 20), 'jade', .55)
    for z in (1.16, 2.2): B.add(t_lathe([(1.3, z), (1.56, z + .03), (1.56, z + .13), (1.3, z + .16)], 20), 'ouro', .6)
    for sx in (-1, 1):
        ring = [Vector((sx * (1.18 + .42 * math.cos(math.radians(a))), 0, 2.72 + .42 * math.sin(math.radians(a)))) for a in range(0, 361, 30)]
        B.add(t_tube(ring, [.09] * len(ring), 6, cap=False), 'bronze', .62)
    return B

# ---------------------------------------------------------------- muro
def _capa_muro(B, L, z0, meia=1.55, tile='telha'):
    """telhadinho de duas aguas sobre o muro: leito, telhas-capa individuais nas duas aguas, cumeeira, wadang nas pontas."""
    h = .95
    B.add(xf(t_prism([(-meia, 0), (meia, 0), (meia, .22), (.12, h), (-.12, h), (-meia, .22)], 'X', -L / 2, L / 2), loc=(0, 0, z0)), tile, .45)
    per = 1.35; n = int(L / per); x0 = -(n - 1) * per / 2; rnd = random.Random(61)
    for s in (-1, 1):
        for k in range(n):
            x = x0 + k * per
            a = Vector((x, s * (meia + .02), z0 + .2)); b = Vector((x, s * .16, z0 + h + .02))
            T = (b - a).normalized(); Bn = Vector((1, 0, 0)); Nn = T.cross(Bn) * (-s if True else 1)
            if Nn.z < 0: Nn = -Nn
            bm = bmesh.new(); SEG = 6
            ra, rb = .36, .30
            r0 = [bm.verts.new(a + Bn * (ra * math.cos(math.pi * i / SEG)) + Nn * (ra * .9 * math.sin(math.pi * i / SEG))) for i in range(SEG + 1)]
            r1 = [bm.verts.new(b + Bn * (rb * math.cos(math.pi * i / SEG)) + Nn * (rb * .9 * math.sin(math.pi * i / SEG))) for i in range(SEG + 1)]
            for i in range(SEG): bm.faces.new((r0[i], r0[i + 1], r1[i + 1], r1[i]))
            bm.faces.new(r0[::-1]); bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            for f in bm.faces: f.smooth = True
            B.add(bm, tile, rnd.random())
            M = Matrix((Bn, Nn, -T)).transposed()
            d = t_lathe([(0, 0), (.4, 0), (.42, .06), (.33, .11), (.16, .07), (0, .13)], 10); xf(d, rot=M); xf(d, loc=a + Nn * .13 - T * .04); B.add(d, tile, .35)
            g = t_lathe([(0, 0), (.13, 0), (.09, .05), (0, .07)], 8); xf(g, rot=M); xf(g, loc=a + Nn * .13 - T * .17); B.add(g, 'ouro', .6)
    B.add(xf(t_prism([(-.34, 0), (.34, 0), (.34, .3), (.2, .52), (-.2, .52), (-.34, .3)], 'X', -L / 2, L / 2, bev=.05), loc=(0, 0, z0 + h - .1)), tile, .5)

def muro_seg(L=9.0, H=8.6):
    """segmento de muro de 9: rodape de pedra de 2 fiadas com peitoril, pano vermelho com moldura em relevo dos dois lados,
    friso de madeira sob a capa e capa de telha de duas aguas. Eixo ao longo de X, centrado."""
    B = Builder('KIT_muro_seg', 611)
    k_madeira._rodape(B, w=L, zt=2.4, t=.72)
    B.add(t_box(-L / 2, L / 2, -.55, .55, 2.76, H, bev=.05), 'verm', .5)
    for s in (-1, 1):
        ya, yb = sorted((s * .55, s * .66))
        for (p, q, r, t) in ((-L / 2 + .55, L / 2 - .55, 3.2, 3.56), (-L / 2 + .55, L / 2 - .55, H - .9, H - .54), (-L / 2 + .55, -L / 2 + .91, 3.2, H - .54), (L / 2 - .91, L / 2 - .55, 3.2, H - .54)):
            B.add(t_box(p, q, ya, yb, r, t, bev=.05), 'vermS', .5)
        B.add(xf(t_prism([(0, -.5), (.5, 0), (0, .5), (-.5, 0)], 'Y', *((-.72, -.64) if s < 0 else (.64, .72)), bev=.03), loc=(0, 0, (3.4 + H - .7) / 2)), 'ouro', .6)
    B.add(t_box(-L / 2, L / 2, -.78, .78, H, H + .42, bev=.07), 'mad', .5)
    for s in (-1, 1): B.add(t_box(-L / 2, L / 2, *sorted((s * .78, s * .83)), H + .14, H + .28), 'ouro', .6)
    _capa_muro(B, L, H + .42)
    return B

def muro_pilar(H=10.2):
    """pilar de muro (cantos e encontros): base de pedra, fuste vermelho com almofadas, capa piramidal de telha e pinaculo."""
    B = Builder('KIT_muro_pilar', 612)
    # base em DUAS fiadas de blocos (casa com o rodape do muro), nao um bloco liso
    B.add(t_box(-1.05, 1.05, -1.05, 1.05, 0, 2.4), 'junta', .2)
    for r, (z0, z1) in enumerate(((0, 1.18), (1.22, 2.4))):
        if r == 0:
            B.add(t_box(-1.15, 1.15, -1.15, 1.15, z0, z1, bev=.09), 'pedra')
        else:
            for sx in (-1, 1): B.add(t_box(*sorted((sx * .03, sx * 1.15)), -1.15, 1.15, z0, z1, bev=.09), 'pedra')
    B.add(t_box(-1.28, 1.28, -1.28, 1.28, 2.4, 2.76, bev=.1, seg=3), 'pedra', .66)
    B.add(t_box(-.98, .98, -.98, .98, 2.76, H, bev=.06), 'verm', .5)
    for a in (0, 90, 180, 270): B.add(xf(t_box(-.62, .62, -1.06, -.98, 3.5, H - .7, bev=.05), rot=(0, 0, a)), 'vermS', .55)
    B.add(t_box(-1.2, 1.2, -1.2, 1.2, H, H + .4, bev=.07), 'mad', .5)
    B.add(xf(t_lathe([(0, 0), (1.85, 0), (1.9, .18), (1.2, .7), (.5, 1.35), (.3, 1.5), (0, 1.5)], 4, smooth=False), rot=(0, 0, 45), loc=(0, 0, H + .4)), 'telha', .5)
    B.add(xf(t_lathe([(0, 0), (.3, 0), (.42, .25), (.3, .5), (.16, .62), (.22, .85), (.08, 1.3), (0, 1.35)], 12), loc=(0, 0, H + 1.85)), 'ouro', .6)
    return B

PORTAO_RISE = 3.0

def telhado_portao(W=14.5, D=10.5, rise=PORTAO_RISE):
    """telhado de duas aguas (xuanshan) para o portao pequeno: agua curva, telhas-capa individuais, cumeeira de pontas
    reviradas, tabuas de empena com o peixe pendurado (xuanyu) em ouro. Origem no centro, beiral em z=0."""
    B = Builder('KIT_telhado_portao', 621); rnd = random.Random(62)
    def prof(t): return rise * (.38 * t + .62 * t * t)                       # mesmo perfil concavo do telhado grande
    NT = 8; half = D / 2
    for s in (-1, 1):
        bm = bmesh.new(); rows = []
        for j in range(NT + 1):
            t = j / NT; y = s * half * (1 - t); z = prof(t)
            rows.append((bm.verts.new((-W / 2, y, z)), bm.verts.new((W / 2, y, z)), bm.verts.new((-W / 2, y, z - .42)), bm.verts.new((W / 2, y, z - .42))))
        for j in range(NT):
            a, b = rows[j], rows[j + 1]
            bm.faces.new((a[0], a[1], b[1], b[0])); bm.faces.new((a[3], a[2], b[2], b[3]))
            bm.faces.new((a[2], a[0], b[0], b[2])); bm.faces.new((a[1], a[3], b[3], b[1]))
        bm.faces.new((rows[0][0], rows[0][2], rows[0][3], rows[0][1]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); B.add(bm, 'telha', .5)
        per = 1.35; n = int((W - .8) / per); x0 = -(n - 1) * per / 2
        for k in range(n):
            x = x0 + k * per
            for j in range(0, NT, 2):
                t0, t1 = j / NT, min(1, (j + 2) / NT)
                a = Vector((x, s * half * (1 - t0), prof(t0) + .04)); b = Vector((x, s * half * (1 - t1), prof(t1) + .02))
                T = (b - a).normalized(); Bn = Vector((1, 0, 0)); Nn = T.cross(Bn)
                if Nn.z < 0: Nn = -Nn
                tb = bmesh.new(); SEG = 6; ra, rb = .4, .33
                r0 = [tb.verts.new(a + Bn * (ra * math.cos(math.pi * i / SEG)) + Nn * (ra * .9 * math.sin(math.pi * i / SEG) + .07)) for i in range(SEG + 1)]
                r1 = [tb.verts.new(b + T * .1 + Bn * (rb * math.cos(math.pi * i / SEG)) + Nn * (rb * .9 * math.sin(math.pi * i / SEG))) for i in range(SEG + 1)]
                for i in range(SEG): tb.faces.new((r0[i], r0[i + 1], r1[i + 1], r1[i]))
                tb.faces.new(r0[::-1]); bmesh.ops.recalc_face_normals(tb, faces=tb.faces)
                for f in tb.faces: f.smooth = True
                B.add(tb, 'telha', rnd.random())
                if j == 0:
                    M = Matrix((Bn, Nn, -T)).transposed()
                    d = t_lathe([(0, 0), (.45, 0), (.47, .07), (.37, .12), (.18, .08), (0, .15)], 12); xf(d, rot=M); xf(d, loc=a + Nn * .16 - T * .05); B.add(d, 'telha', .35)
                    g = t_lathe([(0, 0), (.15, 0), (.1, .06), (0, .08)], 8); xf(g, rot=M); xf(g, loc=a + Nn * .16 - T * .2); B.add(g, 'ouro', .6)
        for sx in (-1, 1):                                                   # tabua de empena (bofeng) acompanhando a agua
            path = [Vector((sx * (W / 2 + .12), s * half * (1 - j / NT), prof(j / NT) - .25)) for j in range(NT + 1)]
            B.add(t_sweep([(-.14, -.42), (.14, -.42), (.14, .42), (-.14, .42)], path), 'verm', .5)
    zr = prof(1)
    B.add(xf(t_prism([(-.62, 0), (.62, 0), (.62, .3), (.44, .45), (.44, 1.05), (.58, 1.2), (.34, 1.5), (-.34, 1.5), (-.58, 1.2), (-.44, 1.05), (-.44, .45), (-.62, .3)], 'X', -W / 2 - .3, W / 2 + .3, bev=.06), loc=(0, 0, zr - .15)), 'telha', .5)
    for s in (-1, 1): B.add(t_box(-W / 2 - .2, W / 2 + .2, *sorted((s * .44, s * .5)), zr + .5, zr + .64), 'ouro', .6)
    for sx in (-1, 1):
        tip = crom([(sx * (W / 2 + .2), 0, zr + .9), (sx * (W / 2 + 1.0), 0, zr + 1.25), (sx * (W / 2 + 1.5), 0, zr + 2.05), (sx * (W / 2 + 1.25), 0, zr + 2.75)], 4)
        B.add(t_tube(tip, lerp_list([.5, .42, .28, .1], len(tip)), 10), 'telha', .5)
        B.add(xf(t_prism([(0, -.2), (.42, -.55), (.5, -1.15), (0, -1.75), (-.5, -1.15), (-.42, -.55)], 'X', -.07, .07, bev=.03), loc=(sx * (W / 2 + .3), 0, zr - .35)), 'ouro', .6)   # xuanyu
    return B
