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
    # O vertice mais apertado contra a telha nao era o topo do aro: era o ornamento da coroa projetado
    # para a frente (medido em x=-122.9, z=21.9, contra a cumeeira em 21.95). Escalar sozinho ganhava
    # 0.09; baixar a coroa 0.30 junto com a escala 0.92 leva a folga para ~0.44. O medalhao encosta um
    # pouco mais no apice da ogiva, que e como uma pedra-chave se comporta de qualquer jeito.
    _coroa(B, tema, ztop + 1.15, -ESP / 2 - .55, P, V, G)
    # Folga contra a telha do Santuario: 0.06 no pad de -6.5 e 0.75 no de +6.5, ZERO vertices atravessando
    # (medido subindo um raio de cada vertice das 30 malhas). Baixar a coroa nao ajuda: naquele ponto a
    # agua do telhado desce junto, entao a folga fica igual e o medalhao so afunda mais no vao.
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
    """Medalhao no fecho do arco. A COR identifica a area (vem do Config.Temas); a FORMA identifica
    o anime. Refeito depois de pesquisar anime por anime: a versao anterior era exatamente o clichê
    que cada dossie apontou como erro comum."""
    S = 1.08                                              # as marcas novas sao mais finas que o clichê antigo: pedem mais tamanho
    def A(bm, tinta, r=.6, dy=0.0, dz=0.0):
        B.add(xf(bm, scale=S, loc=(0, Y + dy, Z + dz)), tinta, r)

    if tema == 'chakra':
        # Naruto: o hitai-ate. Uma PLACA de metal atravessada por uma faixa de pano que corre para os
        # dois lados do arco - o portal inteiro usa a bandana. Le pela faixa horizontal, a distancia.
        # A faixa para nos contrafortes: com 4.6 de cada lado ela dava 12.7 de vao total e os pads ficam
        # de 13 em 13 - encostaria no portal vizinho. E as duas pontas tem comprimentos diferentes e
        # caem em bisel, que e como a bandana amarrada realmente fica.
        for i, sx in enumerate((-1, 1)):
            comp = (2.9, 3.4)[i]
            A(xf(t_box(0, comp, -.16, .16, -.46, .46, bev=.06), scale=(sx, 1, 1), loc=(sx * 1.55, 0, 0)), G, .45)
            pta = t_prism([(0, -.44), (1.15, -.30), (1.15, .30), (0, .44)], 'Y', -.17, .17, bev=.04)
            xf(pta, rot=(0, (-26, 22)[i], 0), loc=(sx * (1.55 + comp), 0, -.30))
            A(pta, G, .62)
        A(xf(t_box(-1.75, 1.75, -.34, .34, -.62, .62, bev=.16, seg=3), loc=(0, -.42, 0)), V, .82)
        A(xf(t_box(-1.5, 1.5, -.12, .12, -.4, .4, bev=.1), loc=(0, -.74, 0)), P, .35)
        esp = [Vector((math.cos(i / 26 * math.tau * 1.15) * (.12 + .46 * i / 26), -.92,
                       math.sin(i / 26 * math.tau * 1.15) * (.12 + .46 * i / 26))) for i in range(27)]
        A(t_tube(esp, [.13] * 27, 6), P, .3)
        A(xf(t_prism([(0, 0), (.55, .30), (.10, .62), (-.30, .28)], 'Y', -.98, -.84, bev=.03), loc=(.22, 0, .18)), P, .25)
        for sx in (-1, 1):
            for sz in (-1, 1):
                A(xf(t_lathe([(0, 0), (.15, 0), (.12, .09), (0, .11)], 8), rot=(-90, 0, 0), loc=(sx * 1.5, -.78, sz * .42)), P, .5)

    elif tema == 'ki':
        # Dragon Ball / Namekusei: o selo da Ajisa. Anel continuo e liso (corpo do dragao fechando o
        # circulo) com glifo namekuseijin rigido no meio, e os dois chifres da casa namekuseijin.
        A(xf(t_lathe([(1.45, 0), (1.95, 0), (1.95, .34), (1.45, .34)], 26), rot=(90, 0, 0)), V, .8, dy=-.42)
        A(xf(t_lathe([(1.18, 0), (1.45, 0), (1.45, .2), (1.18, .2)], 22), rot=(90, 0, 0)), P, .35, dy=-.5)
        A(xf(t_lathe([(0, 0), (1.22, 0), (1.22, .18), (0, .18)], 22), rot=(90, 0, 0)), P, .28, dy=-.2)
        for i in range(3):
            w = (.86, .58, .74)[i]
            A(xf(t_box(-w, w, -.14, .14, -.15, .15, bev=.05), loc=(0, -.74, .52 - i * .52)), V, .6 + .12 * i)
        A(xf(t_box(-.16, .16, -.14, .14, -.66, .66, bev=.05), loc=(-.62, -.74, 0)), V, .55)
        for sx in (-1, 1):
            A(xf(t_prism([(0, 0), (.30, .22), (.12, 1.55), (-.16, .30)], 'Y', -.18, .18, bev=.05),
                 rot=(0, 26 * sx, 0), loc=(sx * 1.35, -.3, 1.5)), P, .62)

    elif tema == 'nichirin':
        # Demon Slayer / Natagumo: o brinco hanafuda como placa pendente e a glicinia caindo do arco.
        # Katana flamejante ficou de fora de proposito: e o clichê que o dossie mandou evitar.
        A(xf(t_box(-.14, .14, -.16, .16, -.2, 1.5, bev=.04), loc=(0, -.5, .9)), P, .4)
        A(xf(t_box(-.82, .82, -.30, .30, -1.5, .78, bev=.14, seg=3), loc=(0, -.52, -.2)), V, .88)
        for k in range(3):
            A(xf(t_box(-.62, .62, -.12, .12, -.1 + k * .34, .06 + k * .34, bev=.04), loc=(0, -.86, -.58)), P, .3 + .2 * k)
        A(xf(t_lathe([(0, 0), (.42, 0), (.36, .16), (0, .2)], 14), rot=(-90, 0, 0), loc=(0, -.92, .26)), P, .24)
        for sx in (-1, 1):
            for j in range(3):
                bx = sx * (1.35 + j * .62); alt = 2.4 - j * .5
                for k in range(6):
                    t = k / 5.0
                    r = .40 * (1 - t) + .10
                    A(xf(t_blob(r, (1.0, .8, .9), 1, lobes=3, lobe_amp=.22, seed=j * 7 + k),
                         loc=(bx + math.sin(k * 1.1) * .16, -.62, -.35 - t * alt)), V if k % 2 else G, .4 + .5 * (k % 3) / 3)

    elif tema == 'sombra':
        # Jardim das Sombras: roda de oito raios com cabos projetados e a mao de teatro de sombras.
        # O dossie foi direto: o clichê e tratar sombra como LUZ (nevoa roxa emissiva com lascas).
        A(xf(t_lathe([(1.55, 0), (1.92, 0), (1.92, .3), (1.55, .3)], 24), rot=(90, 0, 0)), P, .5, dy=-.4)
        for i in range(8):
            a8 = math.tau * i / 8
            # raio e cabo encurtados: com 1.6/2.55 e escala 1.08 os cabos de cima furavam a telha do
            # Santuario neste pad (medido: 2 vertices acima da telha). Agora o topo da roda fica 0.4 abaixo.
            A(xf(t_box(-.13, .13, -.14, .14, .0, 1.42, bev=.04), rot=(0, -math.degrees(a8) + 90, 0), loc=(0, -.4, 0)), P, .45)
            A(xf(t_box(-.10, .10, -.18, .18, 1.66, 2.12, bev=.04), rot=(0, -math.degrees(a8) + 90, 0), loc=(0, -.4, 0)), V, .7 + .2 * (i % 2))
        A(xf(t_lathe([(0, 0), (.52, 0), (.52, .26), (0, .26)], 16), rot=(90, 0, 0)), V, .9, dy=-.62)
        A(xf(t_box(-.46, .46, -.12, .12, -.5, .18, bev=.07), loc=(0, -.78, -.3)), G, .8)
        for i in range(4):
            A(xf(t_box(-.09, .09, -.10, .10, 0, .62 - abs(i - 1.5) * .12, bev=.03),
                 rot=(0, -14 + i * 9, 0), loc=(-.33 + i * .22, -.78, .12)), G, .7 + .07 * i)

    elif tema == 'mare':
        # One Piece: o Log Pose. Esfera de vidro grossa num aro de bronze rebitado, com tres agulhas
        # penduradas em alturas diferentes. Caveira e chapeu de palha entregam "pirata generico".
        A(xf(t_lathe([(1.30, 0), (1.62, 0), (1.62, .5), (1.30, .5)], 22), rot=(90, 0, 0)), P, .45, dy=-.5)
        for i in range(8):
            a8 = math.tau * i / 8
            A(xf(t_lathe([(0, 0), (.14, 0), (.11, .08), (0, .1)], 8), rot=(-90, 0, 0),
                 loc=(math.cos(a8) * 1.46, -.78, math.sin(a8) * 1.46)), V, .65)
        A(xf(t_lathe([(0, -1.12), (.58, -.96), (1.12, 0), (.58, .96), (0, 1.12)], 18), rot=(90, 0, 0)), G, .82, dy=-.62)
        for i, (ax, az, h) in enumerate(((-.42, .30, .72), (.10, -.10, 1.05), (.50, .34, .58))):
            A(xf(t_box(-.05, .05, -.05, .05, -h, 0, bev=.02), loc=(ax, -1.25, az + .3)), P, .3 + .2 * i)
            A(xf(t_lathe([(0, 0), (.11, 0), (.08, .12), (0, .15)], 8), rot=(180, 0, 0), loc=(ax, -1.25, az + .3 - h)), V, .85)
        A(xf(t_box(-.52, .52, -.14, .14, -.12, .12, bev=.05), loc=(0, -.5, 1.62)), P, .55)

    else:
        # Cidade Z (One Punch Man): o meteoro de 200 m PARTIDO, com o furo de soco limpo atravessando.
        # "Punho + linhas de velocidade" era o clichê citado no dossie - e era o que estava aqui.
        for sx in (-1, 1):
            met = t_blob(1.32, (.92, .95, 1.0), 2, lobes=5, lobe_amp=.17, seed=3 + sx)
            xf(met, loc=(sx * .95, -.55, 0))
            A(met, P, .4 if sx < 0 else .52)
            for k in range(5):
                a5 = 1.1 + k * 1.25
                A(xf(t_lathe([(0, 0), (.26, 0), (.22, -.1), (0, -.13)], 9), rot=(-90, 0, 0),
                     loc=(sx * .95 + math.cos(a5) * .7, -1.45, math.sin(a5) * .72)), P, .22 + .12 * k)
        A(xf(t_lathe([(.30, 0), (.52, 0), (.52, 1.15), (.30, 1.15)], 16), rot=(90, 0, 0)), V, .88, dy=-1.1)
        A(xf(t_lathe([(0, 0), (.32, 0), (.32, .9), (0, .9)], 14), rot=(90, 0, 0)), G, .3, dy=-.2)
        for k in range(4):
            A(xf(t_prism([(0, -.12), (.85 + .3 * k, 0), (0, .12)], 'Y', -1.2, -1.02, bev=.02),
                 rot=(0, -70 + k * 46, 0), loc=(0, 0, -.9 + k * .6)), P, .35 + .15 * k)

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
