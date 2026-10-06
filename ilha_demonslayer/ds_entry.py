# ds_entry - ENTRADA da Ilha 4 (DEMON SLAYER), vindo da Shadow Garden (onda 1c; PLANO_DS secoes 3.4, 4.2 e 12;
# PROMPT_USUARIO secao 13). Substitui ds_blockout.entry. Prefixo DS_Ent_, colecao 18_ENTRY.
# A narrativa, da ancora da SG para dentro (eixo local +Y; a ponte vai de y -100 a 0):
#   SOLEIRA de pedra escura (u 0..10, o unico trecho de pedra: casa com a cantaria da SG que fica para tras) sobre a
#   1a rocha-pilar -> PONTE de madeira escura (tabuas atravessadas sobre 4 longarinas, testeira com meio-fio, guarda-
#   corpo koran com corrimao, nuki passante e rodape; postes-mestre com giboshi so nos NOS) -> PATAMAR de descanso no
#   meio (u 45..55: tabuado longitudinal entre 2 travessas, os 2 POSTES-LANTERNA da ponte, a maior rocha-pilar) ->
#   ultimo vao com MUSGO e SAMAMBAIA no encontro de ishigaki -> TORII de entrada (myojin: hashira inclinado com nemaki
#   preto sobre base de pedra, nuki com espiga e cunhas, gakuzuka, shimaki laqueado, kasagi preto com sori e capa de
#   telha escura com canais e cumeeira) -> PATIO de lajes (sando claro do torii a escada da trilha + lajes escuras no
#   resto), 2 TORO de pedra (kasuga) acesos, cerca baixa na borda do penhasco e a escada da Trilha.
# Estrutura da ponte: 3 apoios - rocha-pilar da soleira (u 8), rocha-pilar do patamar (u 50) e o encontro de ishigaki
# no penhasco da ilha (u 94..101) - com cavaletes de madeira e MAOS-FRANCESAS (escoras inclinadas) ate 13 de cada no.
# Colisao: tabuleiro, guardas, patio e escada sao do ds_col (congelado). Aqui so torii e toro (os nos/postes ficam
# dentro da faixa da guarda invisivel).
# ONDA 3b (ds_props): toro, cerca baixa, guarda-corpo e caixa de lanterna sao as do ds_kit (toro kasuga, railing,
# _box_lantern), nas MESMAS posicoes e com os MESMOS nomes de luz; o koran so acrescenta ao railing do kit a inclinacao do
# tabuleiro e os postes-mestre com giboshi (ornamento proprio de ponte, que o kit nao tem). andon() fica so por historico.
import math, random
from mathutils import Vector, Matrix
import ds_lib as DL
from ds_lib import MB, col_box, light, Frame, ccw
import ds_layout as L
import ds_kit as K

T0, T1, T4 = L.T0, L.T1, L.T4
C = "18_ENTRY"
WARM = (1.0, 0.62, 0.30)

# materiais (paleta DSMATS; P_DS_Black = o preto do portao DS aprovado na ilhota da SG: 0 materiais novos)
LAC, BLK = "Wood_DS_Lacquer", "P_DS_Black"
TILE, RIDGE = "Roof_DS_Tile", "Roof_DS_Ridge"
WD, WM = "Wood_DS_Dark", "Wood_DS_Mid"
ST, STD, STP = "Stone_DS", "Stone_DS_Dark", "Stone_DS_Path"
CL, CLD, CLM = "Cliff_DS", "Cliff_DS_Dark", "Cliff_DS_Moss"
GLOW, BRZ, IRON = "Glass_DS_Lantern", "Metal_DS_Rust", "Metal_DS_Iron"
FERN = "Leaf_DS_Shrub"

# ponte de chegada no referencial (u, v): u = 0 na ancora da SG ... 100 no patio; v = esquerda de quem chega (-x)
FA = Frame(L.PREV_X, L.PREV_Y, 0.0, math.pi / 2)
BL = L.BRIDGE_IN_LEN
HW = L.DECK_W / 2.0                    # 9: face interna das guardas invisiveis
RAIL_V = 9.3                           # eixo do guarda-corpo (dentro da guarda invisivel de 9,0 a 10,2)
SILL_U = 10.0                          # fim da soleira de pedra
REST_U = (45.0, 55.0)                  # patamar de descanso
PIERS_A = (8.0, 50.0)                  # rochas-pilar da ponte de chegada (u)
ABUT_U = 93.5                          # face do encontro de ishigaki da ilha
STR_V = (-6.6, -2.4, 2.4, 6.6)         # longarinas
PLANK_T = 0.32                         # espessura das tabuas (topo = tabuleiro + 0,06)


def zf_arr(u):
    """topo do tabuleiro da ponte de chegada (rampa 52,2 -> 54,2, igual a colisao)"""
    return L.DECK + (L.T0 - L.DECK) * max(0.0, min(1.0, u / BL)) + 0.06


# ================================================================== primitivas proprias
def loft(mb, rings, m, caps=(True, True), closed=True, tint=None):
    """superficie entre aneis de pontos (mesmo numero de pontos; anel de 1 ponto = apice). Fecha as pontas."""
    bm = mb.bm
    V = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
    for a, b in zip(V, V[1:]):
        if len(a) == 1 and len(b) == 1:
            continue
        if len(a) == 1 or len(b) == 1:
            apex, ring = (a[0], b) if len(a) == 1 else (b[0], a)
            n = len(ring)
            for i in range(n if closed else n - 1):
                try:
                    bm.faces.new((ring[i], ring[(i + 1) % n], apex))
                except ValueError:
                    pass
            continue
        n = len(a)
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            try:
                bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError:
                pass
    for k, flag in ((0, caps[0]), (-1, caps[1])):
        if flag and len(V[k]) > 2:
            try:
                bm.faces.new(V[k] if k else list(reversed(V[k])))
            except ValueError:
                pass
    mb._post([v for r in V for v in r], m, tint, 0, 1)


def lathe(mb, c, prof, m, n=12, rot=0.0, caps=(True, True), sx=1.0, sy=1.0):
    """perfil [(r, z)] girado em volta do eixo vertical que passa por c = (x, y, z0)"""
    rings = []
    for r, z in prof:
        if r <= 1e-4:
            rings.append([(c[0], c[1], c[2] + z)])
        else:
            rings.append([(c[0] + sx * r * math.cos(rot + 2 * math.pi * i / n),
                           c[1] + sy * r * math.sin(rot + 2 * math.pi * i / n), c[2] + z) for i in range(n)])
    loft(mb, rings, m, caps)


def ring_at(F, cx, cy, z, r, n, rot=0.0):
    return [tuple(F.p(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + r * math.sin(rot + 2 * math.pi * i / n), z))
            for i in range(n)]


def fbox(mb, F, u0, v0, z0, u1, v1, z1, m, bev=0.0, rx=0.0):
    """caixa por cantos no referencial F"""
    mb.box((abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), F.p((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2), F.r(rx), m, bev)


def fbeam(mb, F, a, b, w, h, m, bev=0.0):
    mb.beam(F.p(*a), F.p(*b), w, h, m, bev)


# ================================================================== torii (myojin) - SO 2 na ilha: entrada e saida
TOR_PX0, TOR_PX1 = 7.0, 6.72           # centro do pilar no pe / no topo (uchikorobi: inclina para dentro)
TOR_R0, TOR_R1 = 0.95, 0.82            # raio do pilar no pe / no topo
TOR_HP = 17.0                          # topo do pilar = base do shimaki (no centro)
TOR_NUKI = 14.0                        # base do nuki = vao livre de 14
TOR_KL = 23.6                          # comprimento do kasagi


def _sori(x, amp=1.05):
    """curvatura (sori) do shimaki/kasagi: reto no meio, sobe para as pontas"""
    t = max(0.0, (abs(x) - 2.0) / (TOR_KL / 2 - 2.0))
    return amp * t ** 2.1


def torii(name, x, y, z, ang, area, coll=C, seed=7):
    """torii myojin de laca vermelha escura com preto. ang = rumo de quem atravessa (rad). Vao livre 12 x 14.
    Ordem de baixo para cima: dai-ishi (placa + kamebara de pedra escura) -> nemaki preto -> hashira laqueado inclinado
    -> nuki com espiga e cunhas (kusabi) -> gakuzuka -> daiwa preto -> shimaki laqueado com sori -> kasagi preto com
    sori e ponta chanfrada -> capa de telha escura (2 aguas, canais de telha, cumeeira, onigawara)."""
    mb = MB(name, coll, random.Random(seed), detail="hero")
    F = Frame(x, y, z, ang - math.pi / 2)            # +x local = atravessado; +y local = quem atravessa
    rot = ang - math.pi / 2

    def pcx(zz):
        t = (zz - 0.95) / (TOR_HP - 0.95)
        return TOR_PX0 + (TOR_PX1 - TOR_PX0) * t, TOR_R0 + (TOR_R1 - TOR_R0) * t
    for s in (-1, 1):
        c0 = F.p(s * TOR_PX0, 0, 0)
        # dai-ishi: placa octogonal chanfrada (enterrada 0,3) + kamebara (cupula baixa)
        lathe(mb, (c0.x, c0.y, c0.z), [(2.0, -0.3), (2.0, 0.3), (1.8, 0.48)], STD, 8, rot + math.pi / 8)
        lathe(mb, (c0.x, c0.y, c0.z), [(1.55, 0.46), (1.48, 0.7), (1.2, 0.9), (TOR_R0 + 0.16, 1.0)], STD, 12, rot)
        # hashira: tronco inclinado (16 lados) ate o topo (que acompanha o sori do shimaki)
        ztop = TOR_HP + _sori(TOR_PX1) + 0.15
        loft(mb, [ring_at(F, s * TOR_PX0, 0, 0.95, TOR_R0, 16), ring_at(F, s * TOR_PX1, 0, ztop, TOR_R1, 16)], LAC)
        # nemaki (manga preta da base) com labio no topo
        xa, ra = pcx(0.95)
        xb, rb = pcx(2.75)
        loft(mb, [ring_at(F, s * xa, 0, 0.9, ra + 0.1, 16), ring_at(F, s * xb, 0, 2.75, rb + 0.1, 16)], BLK)
        xc, rc = pcx(2.85)
        loft(mb, [ring_at(F, s * xb, 0, 2.72, rb + 0.17, 16), ring_at(F, s * xc, 0, 2.92, rc + 0.17, 16)], BLK)
        # daiwa: anel preto no topo do pilar, logo abaixo do shimaki
        xd, rd = pcx(TOR_HP - 0.6)
        loft(mb, [ring_at(F, s * xd, 0, TOR_HP - 0.62, rd + 0.11, 16),
                  ring_at(F, s * TOR_PX1, 0, TOR_HP + _sori(TOR_PX1) + 0.02, TOR_R1 + 0.11, 16)], BLK)
        col_box(area, (2.3, 2.3, TOR_HP + 1.0), F.p(s * TOR_PX0, 0, (TOR_HP + 1.0) / 2), F.r())
    # nuki: atravessa os pilares e sai 1,7 de cada lado (espiga); cunhas (kusabi) por fora de cada pilar
    xn, rn = pcx(TOR_NUKI + 0.5)
    half = xn + rn + 1.75
    fbox(mb, F, -half, -0.39, TOR_NUKI, half, 0.39, TOR_NUKI + 1.0, LAC, 0.06)
    for s in (-1, 1):
        fbox(mb, F, s * (xn + rn + 0.06), -0.5, TOR_NUKI - 0.14, s * (xn + rn + 0.44), 0.5, TOR_NUKI + 1.16, LAC, 0.05)
    # gakuzuka (montante do meio) com placas pretas de encaixe em cima e em baixo
    fbox(mb, F, -0.48, -0.33, TOR_NUKI + 1.0, 0.48, 0.33, TOR_HP, LAC, 0.05)
    for z0 in (TOR_NUKI + 1.0, TOR_HP - 0.16):
        fbox(mb, F, -0.62, -0.42, z0, 0.62, 0.42, z0 + 0.16, BLK, 0.03)
    # shimaki (verga de baixo) com o mesmo sori do kasagi
    SL = 2 * (TOR_PX1 + 3.1)
    xs = [-SL / 2 + SL * i / 14 for i in range(15)]
    secs = []
    for xx in xs:
        zb = TOR_HP + _sori(xx)
        secs.append([tuple(F.p(xx, yy, zz)) for yy, zz in ((-0.48, zb), (0.48, zb), (0.48, zb + 0.86), (-0.48, zb + 0.86))])
    loft(mb, secs, LAC)
    # kasagi preto: mais alto e mais fundo nas pontas, ponta chanfrada (o topo passa da base)
    secs = []
    n = 16
    for i in range(n + 1):
        xx = -TOR_KL / 2 + TOR_KL * i / n
        t = abs(xx) / (TOR_KL / 2)
        zb = TOR_HP + 0.86 + _sori(xx)
        h = 0.82 + 0.22 * t * t
        d = 1.34 + 0.16 * t * t
        xb = xx - math.copysign(0.42, xx) if i in (0, n) else xx      # chanfro da ponta (hana)
        secs.append([tuple(F.p(xb, -d / 2, zb)), tuple(F.p(xb, d / 2, zb)),
                     tuple(F.p(xx, d / 2 + 0.06, zb + h)), tuple(F.p(xx, -d / 2 - 0.06, zb + h))])
    loft(mb, secs, BLK)
    # capa de telha: 2 aguas finas com beiral, acompanhando o sori
    E, R = 1.42, 0.58

    def zk(xx):
        t = abs(xx) / (TOR_KL / 2)
        return TOR_HP + 0.86 + _sori(xx) + 0.82 + 0.22 * t * t
    secs = []
    KR = TOR_KL / 2 + 0.25
    for i in range(n + 1):
        xx = -KR + 2 * KR * i / n
        z0 = zk(max(-TOR_KL / 2, min(TOR_KL / 2, xx))) - 0.04 + (0.05 if i in (0, n) else 0.0)
        secs.append([tuple(F.p(xx, -E, z0)), tuple(F.p(xx, -E, z0 + 0.2)), tuple(F.p(xx, 0, z0 + 0.2 + R)),
                     tuple(F.p(xx, E, z0 + 0.2)), tuple(F.p(xx, E, z0)), tuple(F.p(xx, 0, z0 + R - 0.05))])
    loft(mb, secs, TILE)
    # canais de telha (marugawara): costelas descendo cada agua, a cada 0,74
    k = int((2 * KR - 0.6) / 0.74)
    for i in range(k + 1):
        xx = -KR + 0.3 + (2 * KR - 0.6) * i / k
        z0 = zk(max(-TOR_KL / 2, min(TOR_KL / 2, xx))) - 0.04
        for s in (-1, 1):
            a = (xx, s * (E - 0.06), z0 + 0.2 + R * 0.06 / E + 0.05)
            b = (xx, s * 0.32, z0 + 0.2 + R * (1 - 0.32 / E) + 0.05)
            fbeam(mb, F, a, b, 0.26, 0.16, TILE)
    # cumeeira arredondada + onigawara nas pontas
    secs = []
    for i in range(n + 1):
        xx = -(KR - 0.15) + 2 * (KR - 0.15) * i / n
        zr = zk(max(-TOR_KL / 2, min(TOR_KL / 2, xx))) - 0.04 + 0.2 + R
        secs.append([tuple(F.p(xx, 0.3 * math.cos(a), zr + 0.05 + 0.26 * math.sin(a)))
                     for a in (math.radians(d) for d in (0, 50, 90, 130, 180, 270))])
    loft(mb, secs, RIDGE)
    for s in (-1, 1):
        xx = s * (KR - 0.05)
        zr = zk(s * TOR_KL / 2) - 0.04 + 0.2 + R
        mb.box((0.5, 0.86, 0.9), F.p(xx, 0, zr + 0.25), F.r(0, s * 0.22, 0), RIDGE, 0.06)
    return mb.finish()


# ================================================================== toro (kasuga-doro) de pedra
def toro(mb, x, y, z, s=1.0, ang=0.0, light_name=None, area="DS_EntToro"):
    """lanterna de pedestal kasuga DO KIT (ds_kit.toro: base, fuste com aneis, plataforma, camara com aberturas
    recuadas e papel aceso dentro, chapeu com warabite, hoju) - mesma altura (~7) e mesma luz da peca local antiga"""
    K.toro(mb, Frame(x, y, z, ang), "kasuga", s * 0.95, light_name, 160.0)
    col_box(area, (2.6 * s, 2.6 * s, 6.6 * s), (x, y, z + 3.3 * s))


# ================================================================== lanterna de no (andon) sobre poste
def andon(mb, c, rot, s=1.0):
    """lanterna de caixa no topo de um poste: bandeja, 4 cantoneiras, papel aceso RECUADO, trelica (koshi) 0,15 a
    frente do papel, quadro de cima e chapeu de 4 aguas com botao. c = topo do poste"""
    x, y, z = c
    R = (0, 0, rot)

    def P(a, b, h):
        ca, sa = math.cos(rot), math.sin(rot)
        return (x + (a * ca - b * sa) * s, y + (a * sa + b * ca) * s, z + h * s)
    mb.box((1.6 * s, 1.6 * s, 0.2 * s), P(0, 0, 0.1), R, WD, 0.05)
    for a in (-1, 1):
        for b in (-1, 1):
            mb.box((0.18 * s, 0.18 * s, 1.36 * s), P(a * 0.62, b * 0.62, 0.88), R, WD, 0.0)
    mb.box((1.04 * s, 1.04 * s, 1.22 * s), P(0, 0, 0.84), R, GLOW, 0.0)
    for k in range(4):                                      # trelica em cada face (montante + travessa)
        ca, sa = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)
        mb.box((0.08 * s, 0.1 * s, 1.26 * s), P(ca * 0.67, sa * 0.67, 0.86), (0, 0, rot + k * math.pi / 2), WD, 0.0)
        mb.box((0.08 * s, 1.2 * s, 0.1 * s), P(ca * 0.67, sa * 0.67, 0.86), (0, 0, rot + k * math.pi / 2), WD, 0.0)
    mb.box((1.6 * s, 1.6 * s, 0.16 * s), P(0, 0, 1.6), R, WD, 0.04)
    lathe(mb, P(0, 0, 1.66), [(1.34 * s, 0.0), (1.36 * s, 0.1 * s), (0.9 * s, 0.38 * s), (0.28 * s, 0.66 * s),
                              (0.2 * s, 0.72 * s)], RIDGE, 4, rot + math.pi / 4)
    lathe(mb, P(0, 0, 2.36), [(0.2 * s, 0.0), (0.24 * s, 0.12 * s), (0.12 * s, 0.3 * s), (0.0, 0.36 * s)], BRZ, 8, rot)


def giboshi(mb, c, s=1.0, rot=0.0):
    """remate em cebola (giboshi) de bronze envelhecido sobre colar - o poste-mestre da ponte japonesa"""
    x, y, z = c
    lathe(mb, (x, y, z), [(0.48 * s, -0.36 * s), (0.5 * s, 0.0), (0.42 * s, 0.1 * s), (0.3 * s, 0.16 * s)], BRZ, 8, rot)
    lathe(mb, (x, y, z + 0.14 * s), [(0.28 * s, 0.0), (0.48 * s, 0.26 * s), (0.46 * s, 0.48 * s), (0.28 * s, 0.7 * s),
                                     (0.1 * s, 0.9 * s), (0.0, 1.1 * s)], BRZ, 10, rot)


# ================================================================== guarda-corpo (koran) de ponte
class _SlopeFrame:
    """referencial do guarda-corpo do kit sobre o tabuleiro inclinado: x = u, y = 0 no eixo v, z somado ao piso zf(u)"""

    def __init__(self, F, v, zf):
        self.F, self.v, self.zf, self.a = F, v, zf, F.a

    def p(self, x, y, z=0.0):
        return self.F.p(x, y + self.v, z + self.zf(x))

    def r(self, rx=0.0, ry=0.0, rz=0.0):
        return self.F.r(rx, ry, rz)


def koran(mb, F, u0, u1, v, zf, nodes=(), step=3.4, top=3.66, node_top=4.35, post_from=0.38, lanterns=(),
          lamp_names=(), ends=(True, True)):
    """guarda-corpo de ponte = ds_kit.railing (pilaretes com capitel, kasagi que passa das pontas, travessa media e
    baixa, montante curto no meio do vao) seguindo a inclinacao do tabuleiro (zf) em vaos de ~step; postes-mestre
    (mais grossos, com giboshi) em 'nodes' e nas pontas; postes-lanterna com a caixa de lanterna do kit em 'lanterns'"""
    ln = u1 - u0
    k = max(1, int(round(ln / step)))
    flat = abs(zf(u0) - zf(u1)) < 0.02 and abs(zf((u0 + u1) / 2) - zf(u0)) < 0.02
    # tabuleiro plano: 1 lance so (travessas inteiras, pilaretes a cada ~step); inclinado: 1 lance por vao (cada
    # travessa segue a rampa; o degrau de 0,07 entre vaos fica sob o capitel do pilarete)
    pts = [(u0, 0.0), (u1, 0.0)] if flat else [(u0 + ln * i / k, 0.0) for i in range(k + 1)]
    old = (K.MIN_BEVEL, K.MIN_BEVEL_SIZE)
    K.MIN_BEVEL, K.MIN_BEVEL_SIZE = 0.07, 0.5               # o mesmo opt-in da vila (chanfro < 0,07 sai)
    try:
        K.railing(mb, _SlopeFrame(F, v, zf), pts, top - post_from - 0.12, post_from, step + (0.5 if flat else 0.0))
    finally:
        K.MIN_BEVEL, K.MIN_BEVEL_SIZE = old
    nodes = list(nodes) + ([u0] if ends[0] else []) + ([u1] if ends[1] else [])
    for u in nodes:
        z = zf(u)
        fbox(mb, F, u - 0.42, v - 0.42, z + post_from - 0.2, u + 0.42, v + 0.42, z + node_top, WD, 0.06)
        fbox(mb, F, u - 0.5, v - 0.5, z + node_top - 0.5, u + 0.5, v + 0.5, z + node_top - 0.3, BRZ, 0.03)
        p = F.p(u, v, z + node_top)
        giboshi(mb, (p.x, p.y, p.z), 1.0, F.a)
    for i, u in enumerate(lanterns):
        z = zf(u)
        fbox(mb, F, u - 0.46, v - 0.46, z + post_from - 0.2, u + 0.46, v + 0.46, z + 5.1, WD, 0.06)
        fbox(mb, F, u - 0.55, v - 0.55, z + 3.4, u + 0.55, v + 0.55, z + 3.62, BRZ, 0.03)
        Fl = Frame(*F.p(u, v, 0.0)[:2], 0.0, F.a)
        c, _ = K._box_lantern(mb, Fl, (0.0, 0.0, z + 5.24), 0.6, 0.6, 1.4)
        if i < len(lamp_names) and lamp_names[i]:
            light(lamp_names[i], "POINT", tuple(Fl.p(*c)), 160.0, WARM, 0.4)


# ================================================================== rocha-pilar (coluna de estratos que sobe das nuvens)
SEA = L.SEA_CLOUD - 15.0               # pe das colunas: abaixo do mar de nuvens (-60), nunca aparece solto


def rock_column(mb, F, cu, cv, z_top, ru, rv, rng, z_bot=SEA, n=10, moss=True, flare=0.45):
    """coluna de rocha em ESTRATOS horizontais (penhasco da ilha: cinza-azulado, faixas alternadas claras/escuras com
    recuo e saliencia), paredes quase verticais, coroa chanfrada com musgo, alargando para baixo ate sumir no mar de
    nuvens: le como pilar estrutural da ponte, nunca como ilhota solta"""
    ang = [2 * math.pi * i / n + rng.uniform(-0.14, 0.14) for i in range(n)]
    f = [1.0 + rng.uniform(-0.16, 0.16) for _ in range(n)]
    f = [(f[i - 1] + 2 * f[i] + f[(i + 1) % n]) / 4 for i in range(n)]
    H = z_top - z_bot

    def width(z):
        t = max(0.0, min(1.0, (z_top - z) / H))
        return 1.0 + flare * t ** 1.4

    def ring(z, sc, jit, off):
        out = []
        for i in range(n):
            k = sc * f[i] * (1.0 + jit[i])
            out.append(tuple(F.p(cu + off[0] + ru * k * math.cos(ang[i]), cv + off[1] + rv * k * math.sin(ang[i]), z)))
        return out
    z = z_top
    if moss:                                                # coroa: musgo por cima, chanfro curto para a 1a faixa
        j0 = [rng.uniform(-0.03, 0.03) for _ in range(n)]
        loft(mb, [ring(z_top - 0.8, 1.0, j0, (0, 0)), ring(z_top - 0.25, 0.99, j0, (0, 0)),
                  ring(z_top, 0.95, j0, (0, 0))], CLM)
        z = z_top - 0.8
    # estratos: camada DURA (alta, face reta, um pouco saliente) + camada MOLE (fina, recuada) -> linhas de sombra
    # horizontais fortes com paredes retas (penhasco em estratos), nunca "pneus" empilhados
    k = 0
    off = (0.0, 0.0)
    while z > z_bot + 0.5:
        hard = k % 2 == 0
        if z > 20.0:
            h = rng.uniform(3.6, 6.4) if hard else rng.uniform(0.7, 1.4)
        else:
            h = rng.uniform(9.0, 14.0) if hard else rng.uniform(1.4, 2.4)
        zb = max(z_bot, z - h)
        d = rng.uniform(0.99, 1.04) if hard else rng.uniform(0.88, 0.92)
        jit = [rng.uniform(-0.05, 0.05) for _ in range(n)]
        if hard:
            off = (off[0] + rng.uniform(-0.5, 0.5), off[1] + rng.uniform(-0.5, 0.5))
        loft(mb, [ring(zb, width(zb) * d, jit, off), ring(z, width(z) * d * 0.985, jit, off)], CL if hard else CLD)
        z = zb
        k += 1


# ================================================================== ishigaki (muro de pedra em talude, junta rebaixada)
def ishigaki(mb, poly, z_top, z_bot, rng, batter=0.13, open_test=None, stone=ST, core=STD, depth=1.0,
             ls_range=(1.9, 3.6), h_range=(1.3, 2.1)):
    """muro de arrimo em talude a partir do contorno do TOPO (poly, anti-horario). Nucleo escuro recuado 0,24 + pedras
    em fiadas desencontradas (juntas de 0,2 rebaixadas); nas quinas convexas as pedras de canto alternam de lado a
    cada fiada (sangi-zumi). open_test(xm, ym) -> True: aresta sem muro (encostada no terreno)."""
    P = ccw(poly)
    n = len(P)
    open_edges = set(i for i in range(n) if open_test and open_test((P[i][0] + P[(i + 1) % n][0]) / 2,
                                                                     (P[i][1] + P[(i + 1) % n][1]) / 2))
    H = z_top - z_bot
    # nucleo (tronco do contorno: no topo recuado, no pe afastado pelo talude)
    top = DL.offset_poly(P, -0.26)
    bot = DL.offset_poly(P, -0.26 + batter * H)
    loft(mb, [[(x, y, z_bot) for x, y in bot], [(x, y, z_top - 0.05) for x, y in top]], core)
    turn = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
        e0 = (b[0] - a[0], b[1] - a[1])
        e1 = (c[0] - b[0], c[1] - b[1])
        cr = e0[0] * e1[1] - e0[1] * e1[0]
        ang = math.atan2(cr, e0[0] * e1[0] + e0[1] * e1[1])
        turn.append(ang)                                   # > 0 = quina convexa (anti-horario)
    tilt = -math.atan(batter)
    k = 0
    z_hi = z_top
    while z_hi > z_bot + 0.4:
        h = rng.uniform(*h_range)
        z_lo = z_bot if z_hi - h < z_bot + 0.8 else z_hi - h
        zc = (z_hi + z_lo) / 2
        off = batter * (z_top - zc)
        for i in range(n):
            if i in open_edges:
                continue
            a, b = P[i], P[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            Le = math.hypot(dx, dy)
            if Le < 1.0:
                continue
            ux, uy = dx / Le, dy / Le
            nx, ny = uy, -ux                                # para fora
            t0, t1 = 0.0, Le
            for end, vi in ((0, i), (1, (i + 1) % n)):
                ph = turn[vi]
                e = off * math.tan(abs(ph) / 2) if abs(ph) < 2.6 else off
                prev_open = ((i - 1) % n in open_edges) if end == 0 else (((i + 1) % n) in open_edges)
                if ph > 0.05:                               # convexa: estende ate a quina deslocada
                    own = (k + i) % 2 == 0
                    adj = e + (0.0 if own or prev_open else -depth)
                elif ph < -0.05:                            # concava: recua
                    adj = -e - depth * 0.6
                else:
                    adj = 0.0
                if end == 0:
                    t0 -= adj
                else:
                    t1 += adj
            t = t0
            while t < t1 - 0.3:
                ls = rng.uniform(*ls_range)
                if t1 - (t + ls) < 1.0:
                    ls = t1 - t
                tm = t + ls / 2
                pr = off - depth / 2 + rng.uniform(-0.05, 0.13)      # relevo: cada pedra sai um pouco diferente
                cx = a[0] + ux * tm + nx * pr
                cy = a[1] + uy * tm + ny * pr
                hh = (z_hi - z_lo - 0.2) * rng.uniform(0.8, 1.0)
                zz = zc + rng.uniform(-0.5, 0.5) * (z_hi - z_lo - 0.2 - hh)
                mb.box((ls - 0.22, depth, hh), (cx, cy, zz), (tilt + rng.uniform(-0.03, 0.03), 0,
                                                              math.atan2(uy, ux) + rng.uniform(-0.025, 0.025)), stone, 0.12)
                t += ls
        z_hi = z_lo
        k += 1


# ================================================================== vegetacao de transicao (samambaia)
def fern(mb, x, y, z, s, rng, n=None):
    """touceira de samambaia: frondes em arco (lamina fina com espessura, afinando na ponta), roseta aberta"""
    n = n or rng.randint(6, 8)
    a0 = rng.uniform(0, 2 * math.pi)
    for k in range(n):
        a = a0 + 2 * math.pi * k / n + rng.uniform(-0.2, 0.2)
        Lf = s * rng.uniform(1.7, 2.5)
        lift = rng.uniform(0.75, 1.0)
        ca, sa = math.cos(a), math.sin(a)
        secs = []
        for i in range(6):
            t = i / 5
            r = Lf * t
            h = Lf * lift * (0.95 * t - 0.8 * t * t) + 0.05
            w = s * 0.42 * math.sin(math.pi * min(1.0, t * 1.15) ** 0.8) + 0.02
            px, py, pz = x + ca * r, y + sa * r, z + h
            secs.append([(px - sa * w, py + ca * w, pz), (px + sa * w, py - ca * w, pz), (px, py, pz - 0.06 * s)])
        loft(mb, secs, FERN)


# ================================================================== ponte de chegada
def _bents(mb, F, zf, u_p, z_c, legs_v=6.6, struts=(), strut_reach=13.0, rng=None):
    """no de apoio sobre a rocha: travessa (hari) com pontas aparentes, 2 pernas, tirante passante, X de contraventamento
    e maos-francesas ate as travessas a +-strut_reach"""
    zt = zf(u_p) - 1.26                                     # face de baixo das longarinas
    fbox(mb, F, u_p - 0.55, -10.7, zt - 1.15, u_p + 0.55, 10.7, zt, WD, 0.06)
    if z_c < zt - 1.6:
        for s in (-1, 1):
            fbox(mb, F, u_p - 0.5, s * legs_v - 0.5, z_c - 0.4, u_p + 0.5, s * legs_v + 0.5, zt - 1.15, WD, 0.05)
        zm = (z_c + zt - 1.15) / 2
        fbox(mb, F, u_p - 0.3, -legs_v - 1.3, zm - 0.35, u_p + 0.3, legs_v + 1.3, zm + 0.35, WM, 0.03)
        for s in (-1, 1):
            fbeam(mb, F, (u_p, -s * legs_v, z_c + 0.4), (u_p, s * legs_v, zt - 1.6), 0.36, 0.5, WD)
    for d in struts:
        ue = u_p + d * strut_reach
        ze = zf(ue) - 1.26
        fbox(mb, F, ue - 0.45, -10.4, ze - 0.95, ue + 0.45, 10.4, ze, WD, 0.05)
        for s in (-1, 1):
            fbeam(mb, F, (u_p + d * 1.4, s * legs_v, z_c + 0.6), (ue - d * 0.3, s * legs_v, ze - 0.9), 0.78, 0.78, WD,
                  0.05)


def deck(mb, F, u0, u1, zf, rest=None, rng=None):
    """tabuas atravessadas (0,94 + junta 0,12) entre as testeiras; no patamar 'rest' (u_a, u_b) o tabuado corre ao longo
    da ponte, emoldurado por 2 travessas"""
    u = u0
    while u < u1 - 0.3:
        if rest and rest[0] - 0.2 <= u < rest[1]:
            u = rest[1] + 0.25
            continue
        w = 0.94
        if u + w > u1:
            w = u1 - u
        if rest and u < rest[0] - 0.2 and u + w > rest[0] - 0.32:
            w = rest[0] - 0.32 - u
            if w < 0.3:
                u = rest[1] + 0.25
                continue
        z = zf(u + w / 2)
        fbox(mb, F, u, -9.1, z - PLANK_T, u + w, 9.1, z, WM, 0.0)
        u += w + 0.12
    if rest:
        ua, ub = rest
        z = zf((ua + ub) / 2)
        for uu in (ua, ub):
            fbox(mb, F, uu - 0.28, -9.1, zf(uu) - PLANK_T - 0.02, uu + 0.28, 9.1, zf(uu) + 0.02, WD, 0.03)
        k = 9
        w = (18.2 - 0.12 * (k - 1)) / k
        for i in range(k):
            v0 = -9.1 + i * (w + 0.12)
            fbeam(mb, F, (ua + 0.3, v0 + w / 2, zf(ua + 0.3) - PLANK_T / 2), (ub - 0.3, v0 + w / 2, zf(ub - 0.3) - PLANK_T / 2),
                  w, PLANK_T, WM)


def sides(mb, F, u0, u1, zf, low=1.3):
    """testeiras (tabua de bordo com meio-fio 0,32 acima do piso) e as 4 longarinas"""
    for s in (-1, 1):
        fbeam(mb, F, (u0, s * RAIL_V, zf(u0) + 0.38 - (low + 0.38) / 2), (u1, s * RAIL_V, zf(u1) + 0.38 - (low + 0.38) / 2),
              0.6, low + 0.38, WD, 0.05)
    for v in STR_V:
        fbeam(mb, F, (u0, v, zf(u0) - PLANK_T - 0.5), (u1, v, zf(u1) - PLANK_T - 0.5), 0.8, 1.0, WD, 0.04)


def arrival_bridge():
    rng = random.Random(4101)
    mb = MB("DS_Ent_Bridge", C, rng, detail="near")
    zf = zf_arr
    # --- soleira de pedra escura (u 0..10): laje grossa, lajes de topo em 3 fiadas, parapeito baixo com capa
    fbox(mb, FA, -0.2, -10.2, zf(5) - 2.4, SILL_U + 0.4, 10.2, zf(5) - PLANK_T - 0.08, STD, 0.08)
    for r, (ua, ub) in enumerate(((0.05, 3.3), (3.45, 6.7), (6.85, SILL_U))):
        cuts = [-9.0, -3.1 + (0.8 if r % 2 else -0.6), 3.0 + (-0.7 if r % 2 else 0.5), 9.0]
        for va, vb in zip(cuts, cuts[1:]):
            fbox(mb, FA, ua, va + 0.07, zf(ua) - PLANK_T - 0.08, ub, vb - 0.07, zf((ua + ub) / 2), STD, 0.06)
    for s in (-1, 1):
        fbox(mb, FA, 0.3, s * 9.0, zf(0) - 0.1, SILL_U - 0.5, s * 10.3, zf(5) + 1.25, STD, 0.08)
        fbox(mb, FA, 0.2, s * 8.9, zf(5) + 1.25, SILL_U - 0.4, s * 10.4, zf(5) + 1.55, ST, 0.08)
        # pilar-marco de pedra no fim da soleira: dado + capitel + chapeu (ali comeca a madeira)
        fbox(mb, FA, SILL_U - 0.8, s * 8.85, zf(SILL_U) - 0.1, SILL_U + 0.8, s * 10.65, zf(SILL_U) + 3.1, STD, 0.1)
        fbox(mb, FA, SILL_U - 1.0, s * 8.75, zf(SILL_U) + 3.1, SILL_U + 1.0, s * 10.75, zf(SILL_U) + 3.45, ST, 0.08)
        p = FA.p(SILL_U, s * 9.75, zf(SILL_U) + 3.45)
        lathe(mb, (p.x, p.y, p.z), [(1.3, 0.0), (1.32, 0.12), (0.62, 0.62), (0.26, 0.86), (0.0, 1.04)], ST, 4,
              FA.a + math.pi / 4)
    # --- madeira: testeiras, longarinas, tabuado, patamar
    sides(mb, FA, SILL_U, BL + 0.3, zf)
    deck(mb, FA, SILL_U + 0.05, BL, zf, rest=REST_U)
    # --- guarda-corpo: comeca no pilar-marco de pedra, poste-mestre com giboshi na ponta da ilha, postes-lanterna no
    #     patamar (os unicos nos com luz na ponte)
    names = {-1: "L_DSProp_Lamp_Bridge_R", 1: "L_DSProp_Lamp_Bridge_L"}
    for s in (-1, 1):
        koran(mb, FA, SILL_U + 0.8, BL - 0.6, s * RAIL_V, zf, lanterns=(sum(REST_U) / 2,), lamp_names=(names[s],),
              ends=(False, True))
    # --- apoios: a rocha da soleira recebe a laje de pedra e as 2 primeiras travessas; a rocha do patamar tem cavalete
    #     + maos-francesas; o encontro de ishigaki recebe as longarinas no berco e lanca 2 maos-francesas
    for u in (SILL_U + 1.0, 15.0):
        zt = zf(u) - 1.26
        fbox(mb, FA, u - 0.5, -10.7, zt - 1.15, u + 0.5, 10.7, zt, WD, 0.06)
    _bents(mb, FA, zf, PIERS_A[1], zf(PIERS_A[1]) - 10.5, struts=(-1, 1), rng=rng)
    seat = zf(ABUT_U) - PLANK_T - 1.0                       # face de baixo das longarinas no encontro
    ue = ABUT_U - 13.0
    ze = zf(ue) - 1.26
    fbox(mb, FA, ue - 0.45, -10.4, ze - 0.95, ue + 0.45, 10.4, ze, WD, 0.05)
    for s in (-1, 1):                                       # maos-francesas do encontro
        fbeam(mb, FA, (ABUT_U + 0.2, s * 6.6, seat - 7.5), (ue + 0.3, s * 6.6, ze - 0.9), 0.78, 0.78, WD, 0.05)
    mb.finish()
    # rochas-pilar e encontro (objeto proprio: pedra)
    mr = MB("DS_Ent_BridgeRock", C, random.Random(4102), detail="near")
    rock_column(mr, FA, PIERS_A[0] + 1.0, 0.0, zf(SILL_U) - 2.3, 7.0, 11.4, random.Random(41))
    rock_column(mr, FA, PIERS_A[1], 0.0, zf(PIERS_A[1]) - 10.5, 6.2, 12.0, random.Random(42))
    abut = [tuple(FA.p(u, v, 0))[:2] for u, v in ((ABUT_U, -10.8), (ABUT_U, 10.8), (101.5, 10.8), (101.5, -10.8))]
    ishigaki(mr, abut, seat - 0.5, seat - 14.0, random.Random(43), open_test=lambda x, y: y > 0.5)
    fbox(mr, FA, ABUT_U - 0.4, -10.9, seat - 0.55, 101.0, 10.9, seat, ST, 0.08)      # berco (capa) das longarinas
    mr.finish()


# ================================================================== patio T0: lajes, cerca, escada, toro
def _court_paving(mb, rng):
    """lajes do patio: SANDO claro (Stone_DS_Path, lajes grandes) da ponte ao torii e a escada da Trilha, ramal para
    o bambuzal; o resto em lajes escuras menores (Stone_DS). Topo 0,18 acima do piso (junta = o chao, rebaixado)."""
    court = DL.offset_poly(ccw(L.ENTRY_COURT), -0.7)
    sando = ccw(L.ribbon([(0.0, -0.5), (0.0, 20.0), (-6.0, 30.0), (-12.0, 36.0), (-12.0, 40.5)], 4.6))
    branch = ccw(L.ribbon([(3.0, 22.0), (14.0, 25.5), (24.0, 30.0)], 2.6))
    holes = [((-L.TORII_W / 2 - 1.0, 8.0), 2.3), ((L.TORII_W / 2 + 1.0, 8.0), 2.3), ((-12.0, 16.0), 1.9),
             ((12.0, 16.0), 1.9), ((-20.0, 23.0), 3.2)]
    stair = (-18.6, 38.6, -5.4, 60.0)
    z = T0 + 0.24
    # berco escuro sob as lajes: as juntas leem escuras (sombra), independente do tampo do terreno embaixo
    mb.prism(ccw(DL.offset_poly(court, -0.15)), T0 + 0.04, T0 + 0.12, STD)
    y = 0.15
    row = 0
    while y < 42.0:
        h = rng.choice((1.5, 1.8, 2.1))
        x = -27.0 + (rng.uniform(0.0, 1.2) if row % 2 else 0.0)
        while x < 29.0:
            w = rng.uniform(1.8, 3.2)
            cx, cy = x + w / 2, y + h / 2
            inside = L.point_in_poly(cx, cy, court)
            in_s = L.point_in_poly(cx, cy, sando)
            in_b = L.point_in_poly(cx, cy, branch)
            hole = any(math.hypot(cx - hx, cy - hy) < hr + max(w, h) * 0.4 for (hx, hy), hr in holes)
            st = stair[0] <= cx <= stair[2] and cy >= stair[1]
            if inside and not hole and not st and all(L.point_in_poly(px, py, court) for px, py in
                                                       ((x + 0.2, y + 0.2), (x + w - 0.2, y + 0.2),
                                                        (x + 0.2, y + h - 0.2), (x + w - 0.2, y + h - 0.2))):
                m = STP if (in_s or in_b) else ST
                mb.box((w - 0.18, h - 0.18, 0.4), (cx, cy, z - 0.2), (0, 0, rng.uniform(-0.012, 0.012)), m, 0.07)
            x += w
        y += h
        row += 1


def _fence(mb, pts, z, h=2.6, step=2.7):
    """cerca baixa de borda = guarda-corpo baixo do kit (ds_kit.railing), a mesma das bordas da clareira (ds_props)"""
    old = (K.MIN_BEVEL, K.MIN_BEVEL_SIZE)
    K.MIN_BEVEL, K.MIN_BEVEL_SIZE = 0.07, 0.5
    try:
        K.railing(mb, Frame(0.0, 0.0, z - 0.06, 0.0), pts, h, 0.0, step + 0.5)
    finally:
        K.MIN_BEVEL, K.MIN_BEVEL_SIZE = old


def court():
    rng = random.Random(4201)
    mb = MB("DS_Ent_Court", C, rng, detail="near")
    import bpy
    if bpy.data.objects.get("DS_Ter_Paving") is None:
        # as lajes do patio sao do ds_terrain (onda 1a: sando + lados, 0,14 acima com junta); estas so entram com o
        # terreno em blockout (estudio da zona), para a leitura do patio nao depender da ordem das ondas
        _court_paving(mb, rng)
    # cerca baixa na borda sul do patio (asas da ponte) e na quina sudoeste (penhasco)
    _fence(mb, [(-10.6, 0.7), (-21.3, 0.7), (-24.0, 13.0)], T0)
    _fence(mb, [(10.6, 0.7), (21.3, 0.7)], T0)
    DL.plan_stair(mb, "Trilha")
    mb.finish()
    mt = MB("DS_Ent_Toro", C, random.Random(4202), detail="near")
    toro(mt, -12.0, 16.0, T0, 0.98, 0.0, "L_DSProp_Toro_In_L")
    toro(mt, 12.0, 16.0, T0, 0.98, 0.0, "L_DSProp_Toro_In_R")
    mt.finish()


def vegetation():
    """transicao de vegetacao: samambaias e musgo no ultimo vao e no encontro (o roxo frio da SG fica para tras)"""
    rng = random.Random(4301)
    mv = MB("DS_Ent_Ferns", C, rng, detail="near")
    zt = zf_arr(ABUT_U) - PLANK_T - 1.0
    for u, v, z, s in ((ABUT_U + 1.2, -10.3, zt, 1.0), (ABUT_U + 3.0, 10.2, zt, 1.15), (ABUT_U + 5.5, -10.0, zt, 0.8),
                       (PIERS_A[1] + 2.0, -10.4, zf_arr(50) - 10.6, 1.0), (PIERS_A[1] - 3.0, 9.6, zf_arr(50) - 10.6, 0.9)):
        p = FA.p(u, v, 0)
        fern(mv, p.x, p.y, z, s, rng)
    for x, y, s in ((-23.2, 7.0, 1.0), (24.6, 6.0, 0.9), (-19.0, 36.0, 0.9), (-4.0, 40.8, 0.75), (26.0, 30.0, 1.0)):
        fern(mv, x, y, T0 + 0.1, s, rng)
    mv.finish()


# ================================================================== cameras de estudio (closes da zona)
def _c(a, b, lens):
    return (tuple(round(c, 2) for c in a), tuple(round(c, 2) for c in b), lens)


def _pa(u, v, z):
    return tuple(FA.p(u, v, z))


CAMS = {
    "CAM_DSEnt_FromSG": _c(_pa(-26.0, 0.5, L.DECK + 5.5), _pa(110.0, 0.0, T0 + 8.0), 22),
    "CAM_DSEnt_Torii": _c((3.0, -16.0, L.T0 + 5.2), (0.0, 8.0, T0 + 11.5), 22),
    "CAM_DSEnt_ToriiTop": _c((7.0, -5.0, T0 + 16.5), (3.0, 8.0, T0 + 19.0), 32),
    "CAM_DSEnt_ToriiBase": _c((-2.0, 1.0, T0 + 3.2), (-7.0, 8.0, T0 + 1.8), 30),
    "CAM_DSEnt_Toro": _c((-6.0, 9.0, T0 + 5.0), (-12.0, 16.0, T0 + 4.0), 32),
    "CAM_DSEnt_Court": _c((14.0, 36.0, T0 + 5.5), (-3.0, 2.0, T0 + 4.0), 22),
    "CAM_DSEnt_RailNode": _c(_pa(41.0, -3.0, zf_arr(41) + 5.2), _pa(50.0, 9.3, zf_arr(50) + 4.5), 26),
    "CAM_DSEnt_SideE": _c(_pa(52.0, -78.0, zf_arr(50) + 4.0), _pa(52.0, 0.0, zf_arr(50) - 14.0), 22),
    "CAM_DSEnt_Under": _c(_pa(66.0, -34.0, zf_arr(66) - 30.0), _pa(48.0, 0.0, zf_arr(48) - 6.0), 22),
    "CAM_DSEnt_Abutment": _c(_pa(80.0, -22.0, zf_arr(80) - 2.0), _pa(96.0, 0.0, zf_arr(96) - 6.0), 24),
    "CAM_DSEnt_Sill": _c(_pa(18.0, -5.0, zf_arr(18) + 5.2), _pa(4.0, 9.0, zf_arr(4) + 1.5), 26),
}


def build():
    arrival_bridge()
    torii("DS_Ent_Torii", L.TORII_IN[0], L.TORII_IN[1], T0, math.pi / 2, "DS_EntTorii", C, 7)
    court()
    vegetation()
