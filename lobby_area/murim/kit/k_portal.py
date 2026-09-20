# k_portal.py - PORTAL do Santuario, um por area, no formato da REFERENCIA que o usuario mandou (pixel art):
# arco de topo ogival, contrafortes laterais, medalhao no fecho do arco, veios brilhantes na pedra e o vao
# preenchido por CAMADAS CONCENTRICAS que recuam (funil) da borda ate o centro aceso.
# O usuario liberou o portal da estetica chinesa: paleta PROPRIA por area, tirada do Config.Temas do jogo.
#
# Medidas travadas por medicao, nao por gosto:
#   - o disco de teleporte que o jogo ja tem tem 6.4 de diametro  -> o vao precisa de pelo menos isso;
#   - os seis pads ficam de 13 em 13 studs                        -> o portal inteiro tem de caber em ~11;
#   - o telhado do Santuario passa a 17.3 acima do piso nos dois pads do meio -> nada pode subir de 16.5.
# Dai vem o conjunto abaixo: 10.8 de largura por 16.4 de altura (silhueta 1.5, alta como na referencia).
import math, random
import bmesh
from mathutils import Vector, Matrix
from k_core import *
from k_props import crom, lerp_list

W_VAO = 6.8          # largura do vao (o disco do jogo tem 6.4: entra com folga)
H_VAO = 11.0         # altura do vao ate o topo da ogiva
TR    = 1.30         # espessura do anel do arco (fino de proposito: anel, nao lapide)
ESP   = 1.9          # profundidade em Y
Z0    = 0.90         # piso do vao acima do plinto
XB    = 5.60         # meia-largura externa do conjunto
ZB    = 9.50         # topo dos contrafortes: baixo de proposito, para o arco e o medalhao subirem livres

def _nrm(a, b):
    L = math.hypot(a, b) or 1.0
    return (a / L, b / L)

def arco_poly(w, h, n=24, z0=0.0):
    """contorno de um vao de topo ogival: lados retos ate (h - w/2) e topo em arco alongado.
    Pontos (x, z) em sentido anti-horario, comecando embaixo a esquerda."""
    r = w / 2; zr = h - r
    pts = [(-r, z0), (r, z0), (r, z0 + zr)]
    for i in range(1, n):
        a = math.pi * i / n                                   # 0 -> pi, da direita para a esquerda
        pts.append((r * math.cos(a), z0 + zr + r * math.sin(a) * 1.30))   # alonga o topo: ogiva, nao meia-lua
    pts.append((-r, z0 + zr))
    return pts

def offset_poly(pts, d, z_min=None):
    """desloca um contorno fechado para fora (d>0) ou para dentro (d<0) em meia-esquadria.
    E isto que faz o arco virar um ANEL concentrico: com dois arco_poly de larguras diferentes
    a faixa engrossava no topo e o portal lia como lapide."""
    n = len(pts); out = []
    for i in range(n):
        xp, zp = pts[i - 1]; x, z = pts[i]; xn, zn = pts[(i + 1) % n]
        n1 = _nrm(z - zp, -(x - xp)); n2 = _nrm(zn - z, -(xn - x))
        mx, mz = n1[0] + n2[0], n1[1] + n2[1]
        L = math.hypot(mx, mz)
        if L < 1e-6: mx, mz, L = n1[0], n1[1], 1.0
        mx /= L; mz /= L
        c = max(mx * n1[0] + mz * n1[1], .40)                 # trava a esquadria: canto vivo nao explode
        x2, z2 = x + mx * d / c, z + mz * d / c
        if z_min is not None and z2 < z_min: z2 = z_min
        out.append((x2, z2))
    return out

def _pontos_nrm(pts):
    """normal externa media de cada vertice do contorno (para pendurar veios e selos no anel)."""
    n = len(pts); out = []
    for i in range(n):
        xp, zp = pts[i - 1]; x, z = pts[i]; xn, zn = pts[(i + 1) % n]
        n1 = _nrm(z - zp, -(x - xp)); n2 = _nrm(zn - z, -(xn - x))
        out.append(_nrm(n1[0] + n2[0], n1[1] + n2[1]))
    return out

def _faixa(p_int, p_ext, y0, y1, liso=False):
    """solido entre dois contornos (uma faixa fechada), extrudado em Y."""
    bm = bmesh.new(); n = len(p_int)
    vi0 = [bm.verts.new((x, y0, z)) for x, z in p_int]; ve0 = [bm.verts.new((x, y0, z)) for x, z in p_ext]
    vi1 = [bm.verts.new((x, y1, z)) for x, z in p_int]; ve1 = [bm.verts.new((x, y1, z)) for x, z in p_ext]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vi0[i], ve0[i], ve0[j], vi0[j]))
        bm.faces.new((vi1[j], ve1[j], ve1[i], vi1[i]))
        bm.faces.new((ve0[i], ve1[i], ve1[j], ve0[j]))
        bm.faces.new((vi0[j], vi1[j], vi1[i], vi0[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = liso                        # chapado: o sombreado liso era o que embolava a pedra
    return bm

def _tampa(pts, y0, y1, liso=True):
    """solido preenchido de um contorno (para as camadas do vao)."""
    bm = bmesh.new(); n = len(pts)
    v0 = [bm.verts.new((x, y0, z)) for x, z in pts]; v1 = [bm.verts.new((x, y1, z)) for x, z in pts]
    bmesh.ops.contextual_create(bm, geom=v0); bmesh.ops.contextual_create(bm, geom=v1)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((v0[i], v1[i], v1[j], v0[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces: f.smooth = liso
    return bm


# ---------------------------------------------------------------- as pecas
def portal_moldura(tema='chakra', name=None):
    """moldura do portal de UMA area: anel ogival, contrafortes soltos, medalhao do anime e veios acesos.
    Frente = -Y. Origem no piso do terraco."""
    name = name or ('POR_moldura_' + tema)
    P = 'T_%s_pedra' % tema; V = 'T_%s_veio' % tema; G = 'T_%s_borda' % tema
    B = Builder(name, 901 + hash(tema) % 50)
    ii = arco_poly(W_VAO, H_VAO, 24, Z0)                      # contorno do vao
    ee = offset_poly(ii, TR, z_min=0.0)                       # anel concentrico
    ff = offset_poly(ii, TR + .55, z_min=0.0)                 # ressalto das duas faces
    gg = offset_poly(ii, -.34, z_min=Z0)                      # labio interno aceso

    anel = _faixa(ii, ee, -ESP / 2, ESP / 2)
    bevel_sharp(anel, .10, 1, angle=.5); B.add(anel, P, .50)
    for s in (-1, 1):                                         # moldura que abraca cada face (degrau da referencia)
        m = _faixa(gg, ff, s * ESP / 2, s * (ESP / 2 + .38))
        bevel_sharp(m, .07, 1, angle=.5); B.add(m, P, .62)
    lab = _faixa(ii, gg, -ESP / 2 - .40, -ESP / 2 - .10)      # labio aceso em volta do vao
    B.add(lab, V, .80)

    # ---- dovelas: juntas de pedra cortando o anel, para ele nao ler como um tubo liso
    nn = _pontos_nrm(ii)
    for i in range(0, len(ii), 2):
        x, z = ii[i]; nx, nz = nn[i]
        j = xf(t_box(-.075, .075, -ESP / 2 - .02, ESP / 2 + .02, 0, TR, bev=.02),
               rot=(0, -math.degrees(math.atan2(nz, nx)) + 90, 0), loc=(x, 0, z))
        B.add(j, P, .30 + .30 * ((i // 2) % 3) / 2.0)

    # ---- veios acesos correndo na pedra do anel (os riscos magenta da referencia)
    rnd = random.Random(9)
    for i in range(3, len(ii) - 1, 2):
        x, z = ii[i]; nx, nz = nn[i]; d = rnd.uniform(.35, TR - .30); h = rnd.uniform(.35, .95)
        B.add(xf(t_box(-.10, .10, -.10, .10, -h / 2, h / 2, bev=.02),
                 rot=(0, -math.degrees(math.atan2(nz, nx)) + 90, 0),
                 loc=(x + nx * d, -ESP / 2 - .46, z + nz * d)), V, rnd.uniform(.45, .95))

    # ---- CONTRAFORTES: pilones soltos do anel e mais baixos que ele, com ceu entre o capitel e o arco.
    # Era isto que faltava: com contraforte da altura do ombro o conjunto lia como uma lapide unica.
    for sx in (-1, 1):
        a, b = 4.45, XB
        B.add(t_box(sx * (a - .10), sx * b, -ESP / 2 - 1.30, ESP / 2 + 1.30, 0, 1.30, bev=.14, seg=2), P, .34)
        fuste = [(sx * a, 1.30), (sx * b, 1.30), (sx * (b - .38), ZB - 2.30), (sx * (a + .06), ZB - 2.30)]
        if sx < 0: fuste = fuste[::-1]
        B.add(t_prism(fuste, 'Y', -ESP / 2 - 1.05, ESP / 2 + 1.05, bev=.16, seg=2), P, .46)
        B.add(t_box(min(sx * (a - .24), sx * (b + .16)), max(sx * (a - .24), sx * (b + .16)),
                    -ESP / 2 - 1.24, ESP / 2 + 1.24, ZB - 2.30, ZB - 1.15, bev=.12, seg=2), P, .58)
        cap = [(sx * (a - .20), ZB - 1.15), (sx * (b + .12), ZB - 1.15), (sx * (b - .60), ZB), (sx * (a + .28), ZB)]
        if sx < 0: cap = cap[::-1]
        B.add(t_prism(cap, 'Y', -ESP / 2 - .92, ESP / 2 + .92, bev=.10), P, .70)
        B.add(xf(t_prism([(0, 0), (.34, .55), (0, 1.55), (-.34, .55)], 'Y', -.26, .26, bev=.04),
                 loc=(sx * ((a + b) / 2), 0, ZB)), V, .90)                     # ponta acesa no capitel
        # escora diagonal do capitel ate o anel (arcobotante): costura o vazio sem fechar
        esc = [(sx * (a + .05), ZB - 1.05), (sx * (a + .72), ZB - 1.05), (sx * 3.52, ZB + 1.95), (sx * 3.05, ZB + 1.95)]
        if sx < 0: esc = esc[::-1]
        B.add(t_prism(esc, 'Y', -.55, .55, bev=.09), P, .40)
        B.add(xf(t_lathe([(0, 0), (.46, 0), (.38, .32), (0, .40)], 12), rot=(90, 0, 0),
                 loc=(sx * ((a + b) / 2), -ESP / 2 - 1.20, 5.40)), V, .88)     # gema do contraforte

    # ---- plinto do conjunto
    B.add(t_box(-XB - .55, XB + .55, -ESP / 2 - 1.90, ESP / 2 + 1.90, -.62, 0, bev=.16, seg=2), P, .26)

    # ---- MEDALHAO no fecho do arco: a marca do anime da area (o que separa os 6 a primeira vista)
    ztop = Z0 + (H_VAO - W_VAO / 2) + (W_VAO / 2) * 1.30      # apice do vao
    _coroa(B, tema, ztop + 1.45, -ESP / 2 - .55, P, V, G)   # centro no apice EXTERNO do anel: o medalhao coroa, nao tapa o vao
    _ornamentos(B, tema, P, V, G)
    return B

def portal_camada(nivel=0, tema='chakra', name=None):
    """uma das camadas concentricas do vao. Elas RECUAM em Y (0 na frente, 2 no fundo): o vao vira um funil
    e o centro aceso puxa o olho. Malhas separadas para o Roblox poder dar cor/brilho diferente a cada uma."""
    n = nivel
    name = name or ('POR_camada_%d_%s' % (n, tema))
    B = Builder(name, 910 + n)
    ii = arco_poly(W_VAO, H_VAO, 24, Z0)
    c = [ii, offset_poly(ii, -1.30, z_min=Z0 + 1.05), offset_poly(ii, -2.60, z_min=Z0 + 2.10)]
    y0, y1 = (-.34 + .44 * n, -.02 + .44 * n)                 # cada camada mais funda que a anterior
    tinta = ('T_%s_borda' % tema, 'T_%s_meio' % tema, 'T_%s_centro' % tema)[n]
    if n == 2:
        B.add(_tampa(c[2], y0, y1), tinta, .30)
    else:
        B.add(_faixa(c[n + 1], c[n], y0, y1, liso=True), tinta, .30 + .30 * n)
    return B

def portal_vortice(tema='chakra', name=None):
    """as tres camadas numa malha so. Elas eram separadas para o Roblox poder tingir cada uma; agora a cor
    ja vem assada no atlas, entao separar so gastaria 12 malhas e 12 MeshParts a mais."""
    name = name or ('POR_vortice_' + tema)
    B = Builder(name, 915)
    ii = arco_poly(W_VAO, H_VAO, 24, Z0)
    c = [ii, offset_poly(ii, -1.30, z_min=Z0 + 1.05), offset_poly(ii, -2.60, z_min=Z0 + 2.10)]
    for n in (0, 1, 2):
        y0, y1 = (-.34 + .44 * n, -.02 + .44 * n)
        tinta = ('T_%s_borda' % tema, 'T_%s_meio' % tema, 'T_%s_centro' % tema)[n]
        if n == 2: B.add(_tampa(c[2], y0, y1), tinta, .30)
        else:      B.add(_faixa(c[n + 1], c[n], y0, y1, liso=True), tinta, .30 + .30 * n)
    return B

def portal_base(tema='chakra', name=None):
    """disco de pedra no chao na frente do portal: marca onde o jogador para."""
    name = name or ('POR_base_' + tema)
    B = Builder(name, 903 + hash(tema) % 30)
    B.add(t_lathe([(0, 0), (3.6, 0), (3.6, .38), (3.2, .5), (0, .5)], 24), 'T_%s_pedra' % tema, .45)
    B.add(t_lathe([(0, .5), (2.6, .5), (2.6, .62), (0, .62)], 24), 'T_%s_meio' % tema, .5)
    for i in range(8):
        a = math.tau * i / 8
        B.add(xf(t_box(-.5, .5, -.16, .16, .5, .66, bev=.04), rot=(0, 0, math.degrees(a)),
                 loc=(math.cos(a) * 3.05, math.sin(a) * 3.05, 0)), 'T_%s_veio' % tema, .6)
    return B

def portal_fragmento(seed=1, tema='chakra', name=None):
    """lasca de pedra flutuando ao lado do portal aceso."""
    name = name or ('POR_fragmento_%d_%s' % (seed, tema))
    B = Builder(name, 904 + seed); rnd = random.Random(seed)
    bm = t_blob(.55, (.7, .7, 1.5), 1, lobes=3, lobe_amp=.4, seed=seed)
    bevel_sharp(bm, .1, 1, angle=.3)
    xf(bm, rot=(rnd.uniform(-20, 20), rnd.uniform(-20, 20), rnd.uniform(0, 360)))
    B.add(bm, 'T_%s_borda' % tema, .7)
    return B


# ---------------------------------------------------------------- a marca de cada anime
def _coroa(B, tema, Z, Y, P, V, G):
    """medalhao no fecho do arco. Construido em volta da PROPRIA origem e so depois levado para (0, Y, Z):
    assim a escala do conjunto e um numero so e ele cabe debaixo do telhado."""
    S = 1.00                                              # travado pelo teto do Santuario: o aro nao pode passar de 16.5
    def A(bm, tinta, r=.6, dy=0.0, dz=0.0):
        B.add(xf(bm, scale=S, loc=(0, Y + dy, Z + dz)), tinta, r)

    # o aro e o disco sao torneados em torno de Z: sem o giro de 90 eles ficavam DEITADOS e o medalhao
    # lia como um pretzel visto de cima em vez de uma medalha encarando o jogador.
    A(xf(t_lathe([(1.55, 0), (2.05, 0), (2.05, .34), (1.55, .34)], 22), rot=(90, 0, 0)), P, .45, dy=-.10)
    A(xf(t_lathe([(0, 0), (1.62, 0), (1.62, .22), (0, .22)], 22), rot=(90, 0, 0)), P, .30, dy=.30)
    for i in range(12):                                                                # cravos no aro
        a = math.tau * i / 12
        A(xf(t_box(-.10, .10, -.12, .12, -.10, .10, bev=.03), loc=(math.cos(a) * 1.80, -.30, math.sin(a) * 1.80)), V, .55 + .4 * (i % 2))

    if tema == 'chakra':                                   # Naruto: espiral de chakra + duas kunai cruzadas
        pts = [Vector((math.cos(t / 33.0 * math.tau * 2.1) * (.28 + 1.20 * t / 33.0), -.34,
                       math.sin(t / 33.0 * math.tau * 2.1) * (.28 + 1.20 * t / 33.0))) for t in range(34)]
        A(t_tube(pts, [.26 - .15 * (i / 33.0) for i in range(34)], 7), V, .85)
        for sx in (-1, 1):
            k = t_prism([(0, 0), (.20, .45), (0, 3.10), (-.20, .45)], 'Y', -.10, .10, bev=.04)
            xf(k, rot=(0, 30 * sx, 0), loc=(sx * 1.30, .30, -.55))
            A(k, G, .78)
            A(xf(t_lathe([(0, 0), (.28, 0), (.24, .45), (0, .50)], 8), rot=(0, 30 * sx, 0),
                 loc=(sx * 1.95, .30, -1.70)), P, .50)
    elif tema == 'ki':                                     # Dragon Ball: esfera de 4 estrelas + raios de ki
        A(xf(t_lathe([(0, -1.25), (.62, -1.08), (1.25, 0), (.62, 1.08), (0, 1.25)], 16), rot=(90, 0, 0)), G, .80, dy=-.55)
        for (ex, ez) in ((0, .46), (-.46, -.17), (.46, -.17), (0, -.63)):
            est = [(math.cos(math.tau * i / 10) * (.24 if i % 2 == 0 else .10),
                    math.sin(math.tau * i / 10) * (.24 if i % 2 == 0 else .10)) for i in range(10)]
            A(xf(t_prism(est, 'Y', -1.90, -1.72, bev=.02), loc=(ex, 0, ez)), V, .92)
        for i in range(10):
            a = math.tau * i / 10 + .3; L = 1.15 + (i % 3) * .45
            A(xf(t_prism([(0, -.16), (L, 0), (0, .16)], 'Y', -.66, -.46, bev=.03),
                 rot=(0, -math.degrees(a), 0), loc=(math.cos(a) * 1.75, 0, math.sin(a) * 1.75)), V, .6 + .3 * (i % 2))
    elif tema == 'nichirin':                               # Demon Slayer: lamina nichirin + ondas da respiracao
        A(xf(t_prism([(0, 0), (.32, .45), (.32, 3.55), (0, 4.10), (-.32, 3.55), (-.32, .45)], 'Y', -.15, .15, bev=.05),
             loc=(0, -.62, -1.30)), G, .88)
        A(xf(t_box(-.95, .95, -.24, .24, -.28, .08, bev=.06), loc=(0, -.62, -1.30)), P, .50)
        A(xf(t_lathe([(0, 0), (.22, 0), (.20, 1.25), (0, 1.35)], 8), rot=(180, 0, 0), loc=(0, -.62, -1.40)), P, .60)
        for i in range(7):
            xx = -2.05 + i * .68
            onda = [Vector((xx + .34 * math.sin(k * .9), -.50, -2.05 + k * .19)) for k in range(6)]
            A(t_tube(onda, [.14] * 6, 5), V, .5 + .4 * (i % 2))
    elif tema == 'sombra':                                 # olho aceso + lascas de sombra
        A(xf(t_prism([(-1.60, 0), (-.75, .72), (.75, .72), (1.60, 0), (.75, -.72), (-.75, -.72)], 'Y', -.72, -.46, bev=.06)), P, .45)
        A(xf(t_lathe([(0, 0), (.55, 0), (.44, .26), (0, .32)], 14), rot=(90, 0, 0)), G, .92, dy=-.95)
        A(xf(t_lathe([(0, 0), (.23, 0), (.18, .18), (0, .22)], 10), rot=(90, 0, 0)), P, .18, dy=-1.15)
        for i in range(9):
            a = math.tau * i / 9 + .2; d = 1.75 + (i % 3) * .40
            A(xf(t_prism([(0, -.45), (.30, 0), (0, .80), (-.30, 0)], 'Y', -.60, -.42, bev=.03),
                 rot=(0, 0, math.degrees(a)), loc=(math.cos(a) * d, 0, math.sin(a) * d)), V, .4 + .5 * (i % 2))
    elif tema == 'mare':                                   # One Piece: leme de navio + ondas
        A(xf(t_lathe([(1.00, 0), (1.38, 0), (1.38, .26), (1.00, .26)], 20), rot=(90, 0, 0)), P, .50, dy=-.70)
        A(xf(t_lathe([(0, 0), (.44, 0), (.44, .28), (0, .28)], 14), rot=(90, 0, 0)), V, .82, dy=-.70)
        for i in range(8):
            a = math.tau * i / 8
            A(xf(t_box(-.14, .14, -.13, .13, .26, 1.95, bev=.04), rot=(0, -math.degrees(a) + 90, 0), loc=(0, -.70, 0)), P, .60)
            A(xf(t_box(-.18, .18, -.16, .16, 1.35, 2.20, bev=.05), rot=(0, -math.degrees(a) + 90, 0), loc=(0, -.70, 0)), V, .55 + .3 * (i % 2))
        for i in range(6):
            xx = -1.90 + i * .76
            onda = [Vector((xx + .42 * math.sin(k * 1.1), -.50, -2.25 + .26 * math.cos(k * 1.1))) for k in range(6)]
            A(t_tube(onda, [.16] * 6, 5), G, .5 + .4 * (i % 2))
    else:                                                  # serio: punho e linhas de impacto
        A(xf(t_blob(1.00, (1.1, .8, 1.0), 2, lobes=4, lobe_amp=.16), loc=(0, -.92, 0)), G, .80)
        for i in range(4):
            A(xf(t_box(-.30, .30, -.26, .26, -.38 + i * .25, -.14 + i * .25, bev=.07), loc=(0, -1.42, .18)), V, .5 + .12 * i)
        for i in range(12):
            a = math.tau * i / 12; L = 1.35 + (i % 3) * .50
            A(xf(t_prism([(0, -.13), (L, 0), (0, .13)], 'Y', -.58, -.44, bev=.02),
                 rot=(0, -math.degrees(a), 0), loc=(math.cos(a) * 1.55, 0, math.sin(a) * 1.55)), V, .45 + .5 * (i % 2))

def _ornamentos(B, tema, P, V, G):
    """detalhe no fuste dos contrafortes, tambem por tema."""
    for sx in (-1, 1):
        x = sx * 4.88
        if tema == 'chakra':                               # pergaminho enrolado
            B.add(xf(t_lathe([(0, -1.35), (.46, -1.35), (.46, 1.35), (0, 1.35)], 10), rot=(90, 0, 0),
                     loc=(x, -ESP / 2 - 1.05, 3.30)), G, .60)
            for z2 in (-1.28, 1.28):
                B.add(xf(t_lathe([(0, z2 - .11), (.56, z2 - .11), (.56, z2 + .11), (0, z2 + .11)], 10), rot=(90, 0, 0),
                         loc=(x, -ESP / 2 - 1.05, 3.30)), P, .45)
        elif tema == 'ki':                                 # chamas de ki subindo
            for k in range(4):
                B.add(xf(t_prism([(0, 0), (.38, .62), (.16, .98), (.27, 1.70), (0, 2.30), (-.27, 1.70), (-.16, .98), (-.38, .62)],
                                 'Y', -ESP / 2 - 1.02, -ESP / 2 - .82, bev=.05),
                         loc=(x + (k % 2) * .52 - .26, 0, 2.00 + k * 1.55)), V, .40 + .18 * k)
        elif tema == 'nichirin':                           # xadrez do haori
            for k in range(9):
                zz = 1.90 + k * .92
                B.add(t_box(x - .86 + (k % 2) * .52, x - .34 + (k % 2) * .52, -ESP / 2 - .98, -ESP / 2 - .80, zz, zz + .64, bev=.03),
                      V if k % 2 else G, .40 + .40 * (k % 3) / 3)
        elif tema == 'sombra':                             # olhos menores acompanhando o fuste
            for k in range(3):
                zz = 2.90 + k * 2.45
                B.add(xf(t_prism([(-.56, 0), (0, .31), (.56, 0), (0, -.31)], 'Y', -ESP / 2 - .98, -ESP / 2 - .80),
                         loc=(x, 0, zz)), G, .85)
        elif tema == 'mare':                               # corda trancada
            pts = [Vector((x + .26 * math.sin(k * .9), -ESP / 2 - .96, 1.70 + k * .56)) for k in range(13)]
            B.add(t_tube(pts, [.20] * 13, 6), G, .60)
            for k in range(0, 13, 2):
                B.add(xf(t_lathe([(.22, 0), (.31, .05), (.31, .18), (.22, .23)], 8), rot=(90, 0, 0),
                         loc=(x + .26 * math.sin(k * .9), -ESP / 2 - .96, 1.70 + k * .56)), P, .50)
        else:                                              # serio: rachaduras de impacto
            rnd2 = random.Random(77 + sx)
            for k in range(7):
                zz = 1.80 + k * 1.22; L = rnd2.uniform(.7, 1.7); ang = rnd2.uniform(-40, 40)
                B.add(xf(t_prism([(0, -.11), (L, 0), (0, .11)], 'Y', -ESP / 2 - .98, -ESP / 2 - .84, bev=.02),
                         rot=(0, ang, 0), loc=(x, 0, zz)), V, rnd2.uniform(.4, .9))
