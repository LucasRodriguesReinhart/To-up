# op_exit - SAIDA da Ilha 5 (ONE PIECE / WANO) para One Punch Man (area 6), M4 (PLANO_OP secoes 0.10, 3, 4.3, 7, 9 e
# 15.4; PROMPT_USUARIO secoes 12, 14 e 16 "Pontes"). Substitui op_blockout.exit_. Prefixo OP_Exit_, colecao
# 08_NEXT_ISLAND. Le a planta TRAVADA (op_layout): EXIT_START (206, 236, T1), rumo 15, ponte de 88, portao a 110,
# ancora a 134. Marcadores, portao (il_gate_opm da galeria, SEM redesenho: o op_core o poe no lugar) e TODA a colisao
# andavel (tabuleiro plano a T1 + guardas da ponte + guarda da ancora COL_OPAnchorGuard_001) sao do op_core/op_col.
#
# A PONTE VERMELHA DE SAIDA (a ponte da concept que vai para a caveira):
#   - TABULEIRO PLANO (o percurso e a colisao: nada de corcova que torne o caminho impraticavel). A CURVATURA da concept
#     esta na estrutura: um GRANDE ARCO de laca vermelha no vao central (pilar a pilar, 37 de luz, flecha 16) com
#     montantes vermelhos ate as transversinas, contraventamento escuro entre as 2 costelas; vaos laterais em viga
#     vermelha com MAOS-FRANCESAS que nascem dos pilares (ritmo pequeno-grande-pequeno).
#   - 2 PILARES DE PEDRA aparelhada na agua (fiadas duras + juntas recuadas, talhamar nas 2 pontas, talude, imposta
#     escura e berco vermelho do arco) e 2 ENCONTROS: oeste = bloco de pedra encostado no muro do terraco do summon (no
#     cais 42,2, com colisao) + soleira de pedra que fecha o chanfro entre a borda do terraco e o tabuado (a ponte e
#     esconsa 15 graus em relacao a borda); leste = bloco na falesia do promontorio sob a cabeca da ponte.
#   - Tabuado escuro de tabuas atravessadas sobre 4 longarinas, TESTEIRA vermelha continua com friso de ouro (mesma
#     linguagem da ponte de chegada, op_entry), GUARDA-CORPO vermelho completo (rail_run do op_entry: pilaretes com
#     cinta de ouro, corrimao kasagi, travessas; postes-mestre com giboshi nos pilares; ANDON nas 4 cabeceiras). O
#     guarda-corpo comeca EXATAMENTE onde o do terraco do summon termina (205,25; 225,6 / 246,4): sem fresta.
# PROMONTORIO: soleira larga de pedra na cabeca leste, CAMINHO de lajes (+0,12, o leito do op_terrain: meio-fio escuro
#   +0,3) ate a soleira do portao e do portao ate a CABECA DE PONTE da ancora: laje larga de pedra com 2 PILARES-MESTRE
#   (oyabashira de pedra com capa e giboshi de ouro) = onde a ponte da area 6 vai encostar; 2 toro de pedra.
# TERMINO SEGURO (PROMPT secao 14): OP_Exit_AnchorGuard (next_island_guard) = barreira PROVISORIA de madeira entre os
#   pilares-mestre (2 cavaletes em X + 3 travessas), a colisao e a COL_OPAnchorGuard_001 do op_col. Nao ha passagem que
#   leva a queda nem promessa falsa: sem ponte comecada para o vazio. A integracao da area 6 apaga a barreira.
# Orcamento (PLANO_OP secao 9): exit 18k tris / 24 MeshParts; colisoes proprias: encontro oeste (no cais) e 2 toro.
import math, random
from mathutils import Vector
import op_lib as DL
from op_lib import MB, col_box, light, Frame, ccw
import op_layout as L
import op_kit as K
import op_entry as E

C = "08_NEXT_ISLAND"
T1, SEA = L.T1, L.SEA
LN = L.EXIT_BRIDGE_LEN                      # 88
UX, UY = L.exit_dir()
ANG = math.atan2(UY, UX)
BF = Frame(L.EXIT_START[0], L.EXIT_START[1], 0.0, ANG)     # (d ao longo da ponte, v = esquerda, z absoluto)
WARM = (1.0, 0.66, 0.36)
EYE = L.EYE

LAC, WD, WM, GOLD = "Wood_OP_Lacquer", "Wood_OP_Dark", "Wood_OP_Mid", "Metal_OP_Gold"
STW, STD, STP = "Stone_OP_Wall", "Stone_OP_Dark", "Stone_OP_Path"

# tabuleiro (as mesmas medidas da ponte de chegada: guarda invisivel do op_col em |v| 9,0..10,2)
FAS = (9.45, 10.2)                 # testeira vermelha
RAIL_V = 9.82                      # eixo do guarda-corpo
PLANK_T = 0.3
TOP = T1 + 0.06                    # topo das tabuas (0,06 acima da colisao)
STR_B = TOP - PLANK_T - 0.9        # fundo das longarinas
TR_B = STR_B - 0.8                 # fundo das transversinas (T1 - 1,94)
TERR_X = 205.45                    # borda do lajeado do terraco do summon (op_summon: lajes ate 205,4)
D0, D1 = 2.7, 86.0                 # 1a tabua inteira (fora do terraco) / ultima (soleira leste a partir de D1)
PIERS = (22.0, 66.0)               # pilares na agua
PIER_HD, PIER_HV = 3.4, 9.6        # meia espessura (d) e meia largura (v) do pilar no topo
CAP_Z = T1 - 19.0                  # imposta dos pilares (69,2)
SEA_BOT = 26.0
RIB_V = 8.1                        # eixo das 2 costelas do arco
RIB_W, RIB_H = 1.5, 2.1            # secao da costela (largura v x altura radial)
HEAD = LN + L.ANCHOR_OPM_OFF       # 134: borda da ancora
GATE_D = LN + L.GATE_OPM_OFF       # 110: plano da barreira do portao
SOL = (GATE_D - 5.0, GATE_D + 5.0)   # soleira 22 x 10 do il_gate_std (topo +0,15)
PATH_HW = 5.55                     # caminho de lajes (o leito do op_terrain tem 5,6 de meia largura)


def P(d, v, z):
    return BF.p(d, v, z)


def d_edge(v):
    """d em que a linha v da ponte cruza a borda do terraco do summon (x = 205,45)"""
    return (TERR_X - L.EXIT_START[0] + UY * v) / UX


def hsh(*k):
    return K._h01(*k)


def quad_faces(mb, rings, m, closed=True, caps=False):
    """superficie entre aneis (mesmo numero de pontos), mundo; material explicito via _post"""
    bm = mb.bm
    V = [[bm.verts.new(Vector(p)) for p in r] for r in rings]
    n = len(V[0])
    for a, b in zip(V, V[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            try:
                bm.faces.new((a[i], a[j], b[j], b[i]))
            except ValueError:
                pass
    if caps:
        for r, rev in ((V[0], True), (V[-1], False)):
            try:
                bm.faces.new(list(reversed(r)) if rev else r)
            except ValueError:
                pass
    mb._post([v for r in V for v in r], m, None, 0, 1)


def coursed(mb, plan, z0, z1, key, m=STW, joint=STD, grow=0.0, course=(1.9, 0.8)):
    """massa de pedra aparelhada em FIADAS: faixa dura (face reta) + junta mole recuada 0,14 (linha de sombra);
    plan(g) -> poligono ccw (mundo) com crescimento g; 'grow' = talude total (o pe e 'grow' mais largo que o topo)"""
    z = z1
    j = 0
    H = max(1.0, z1 - z0)
    while z > z0 + 0.05:
        hard = j % 2 == 0
        hh = (course[0] + course[1] * hsh(key, j)) if hard else 0.3
        zb = max(z0, z - hh)
        gt = grow * (z1 - z) / H
        gb = grow * (z1 - zb) / H
        g0 = 0.0 if hard else -0.14
        quad_faces(mb, [[(x, y, zb) for x, y in plan(gb + g0)], [(x, y, z) for x, y in plan(gt + g0)]],
                   m if hard else joint, caps=False)
        z = zb
        j += 1


# ================================================================== tabuleiro + guarda-corpo
def deck(mb):
    # tabuas atravessadas 0,9 + junta 0,12 (topo 0,06 acima da colisao), entram 0,15 na testeira
    d = D0
    while d < D1 - 0.3:
        w = min(0.9, D1 - d)
        mb.box((w, 2 * FAS[0] + 0.3, PLANK_T), P(d + w / 2, 0.0, TOP - PLANK_T / 2), BF.r(), WD, 0.0)
        d += w + 0.12
    # longarinas (4) e testeira vermelha continua (comeca na borda do terraco, de cada lado)
    for v in (-6.4, -2.2, 2.2, 6.4):
        a = max(d_edge(v) + 0.3, -3.0)
        mb.beam(P(a, v, STR_B + 0.45), P(D1 + 1.5, v, STR_B + 0.45), 0.8, 0.9, WD, 0.0)
    for s in (-1, 1):
        vc = s * (FAS[0] + FAS[1]) / 2
        a = d_edge(vc) + 0.1
        mb.beam(P(a, vc, T1 + 0.35 - 0.8), P(D1 + 1.0, vc, T1 + 0.35 - 0.8), FAS[1] - FAS[0], 1.6, LAC, 0.0)
        a = d_edge(s * (FAS[1] + 0.07)) + 0.1
        mb.beam(P(a, s * (FAS[1] + 0.07), T1 - 1.1), P(D1 + 1.0, s * (FAS[1] + 0.07), T1 - 1.1), 0.14, 0.16, GOLD, 0.0)
    # transversinas sob as longarinas (a cada ~4,4; nos montantes do arco elas caem sobre os montantes)
    for d in stations():
        mb.box((0.7, 2 * 9.3, 0.8), P(d, 0.0, TR_B + 0.4), BF.r(), WD, 0.0)


def stations():
    out = []
    d = 6.0
    while d < D1 - 1.0:
        out.append(round(d, 2))
        d += 4.4
    return out


def rails(mb):
    """guarda-corpo vermelho: do fim do guarda-corpo do terraco do summon ate a soleira leste; postes-mestre nos
    pilares e no meio; ANDON nas 4 cabeceiras (luz NightOnly L_OPProp_Lamp_Saida_*)"""
    lamps = []
    for s in (-1, 1):
        v = s * RAIL_V
        da, db = d_edge(v) + 0.05, D1 - 0.4
        nodes = [(PIERS[0] - da) / (db - da), (44.0 - da) / (db - da), (PIERS[1] - da) / (db - da)]
        lamps += E.rail_run(mb, P(da, v, T1 + 0.35), P(db, v, T1 + 0.35), h=3.35, step=4.0, nodes=nodes,
                            lamps=[0.0, 1.0], lamp_s=0.95)
    return lamps


def west_head(mb):
    """encontro oeste: soleira de pedra no chanfro entre a borda do terraco e a 1a tabua + bloco de pedra encostado
    no muro do terraco, apoiado no cais (42,2)"""
    hv = FAS[1] + 0.2
    poly = [tuple(P(d_edge(-hv), -hv, 0)[:2]), tuple(P(D0 + 0.02, -hv, 0)[:2]), tuple(P(D0 + 0.02, hv, 0)[:2]),
            tuple(P(d_edge(hv), hv, 0)[:2])]
    K.slab_poly(mb, ccw(poly), TR_B, T1 + 0.3, 0.08, STP)
    # bloco (alinhado ao muro do terraco, x = 205,45) do cais ate sob a soleira; fiadas
    x0, x1 = TERR_X - 1.0, 209.8
    y0, y1 = 223.4, 248.6

    def plan(g):
        return ccw([(x0, y0 - g), (x1 + g, y0 - g), (x1 + g, y1 + g), (x0, y1 + g)])
    coursed(mb, plan, L.HARBOR - 0.4, TR_B, "absW", grow=0.9)
    mb.box((x1 - x0 + 0.6, y1 - y0 + 0.6, 0.7), ((x0 + x1) / 2 + 0.3, (y0 + y1) / 2, TR_B - 0.35), (0, 0, 0), STD, 0.0)
    col_box("OP_ExitAbut", (x1 - x0 + 1.8, y1 - y0 + 1.8, T1 - L.HARBOR), ((x0 + x1) / 2 + 0.9, (y0 + y1) / 2,
                                                                           (L.HARBOR + T1) / 2 - 1.0))


def east_head(mb):
    """encontro leste na falesia do promontorio (sob a cabeca da ponte; o pe some na rocha)"""
    def plan(g):
        return ccw([tuple(P(78.5 - g, -10.6 - g, 0)[:2]), tuple(P(D1 + 2.0, -10.6 - g, 0)[:2]),
                    tuple(P(D1 + 2.0, 10.6 + g, 0)[:2]), tuple(P(78.5 - g, 10.6 + g, 0)[:2])])
    coursed(mb, plan, 52.0, TR_B, "absE", grow=1.6)
    mb.box((D1 + 2.0 - 78.5 + 0.8, 22.6, 0.7), P((78.5 + D1 + 2.0) / 2 - 0.4, 0.0, TR_B - 0.35), BF.r(), STD, 0.0)


# ================================================================== pilares + arco
def pier_plan(dc, g):
    hd, hv = PIER_HD + g, PIER_HV + g
    nose = 2.8 + g * 0.5
    pts = [(dc + hd, -hv), (dc + hd, hv), (dc, hv + nose), (dc - hd, hv), (dc - hd, -hv), (dc, -hv - nose)]
    return ccw([tuple(P(d, v, 0)[:2]) for d, v in pts])


def piers(mb, br):
    for k, dc in enumerate(PIERS):
        # soco na linha d'agua + fuste em fiadas com talude + imposta escura + berco vermelho do arco
        quad_faces(mb, [[(x, y, SEA_BOT) for x, y in pier_plan(dc, 2.2)], [(x, y, SEA + 1.4) for x, y in
                                                                          pier_plan(dc, 2.2)]], STD, caps=True)
        coursed(mb, lambda g, dc=dc: pier_plan(dc, g), SEA + 1.4, CAP_Z - 0.8, "pier%d" % k, grow=1.4)
        quad_faces(mb, [[(x, y, CAP_Z - 0.8) for x, y in pier_plan(dc, 0.35)],
                        [(x, y, CAP_Z) for x, y in pier_plan(dc, 0.35)]], STD, caps=True)
        # berco (daiwa) vermelho sob cada costela + bloco escuro de apoio das vigas laterais
        for s in (-1, 1):
            br.box((2 * PIER_HD - 0.4, RIB_W + 0.8, 1.2), P(dc, s * RIB_V, CAP_Z + 0.6), BF.r(), LAC, 0.0)
            br.box((2 * PIER_HD - 1.6, RIB_W + 1.2, 0.35), P(dc, s * RIB_V, CAP_Z + 1.37), BF.r(), GOLD, 0.0)


def arch_pts(n=16):
    """eixo da costela: arco de circulo do berco do pilar 1 ao berco do pilar 2 (flecha ate sob as transversinas)"""
    da, db = PIERS[0] + PIER_HD - 0.6, PIERS[1] - PIER_HD + 0.6
    za = CAP_Z + 1.2 + RIB_H / 2
    zc = TR_B - RIB_H / 2 - 0.05
    half = (db - da) / 2
    f = zc - za
    R = (half * half + f * f) / (2 * f)
    cz = zc - R
    a0 = math.asin(half / R)
    out = []
    for i in range(n + 1):
        a = -a0 + 2 * a0 * i / n
        out.append(((da + db) / 2 + R * math.sin(a), cz + R * math.cos(a), a))
    return out, cz


def arch(mb):
    pts, cz = arch_pts()
    for s in (-1, 1):
        rings = []
        for d, z, a in pts:
            nd, nz = math.sin(a), math.cos(a)                  # normal radial (para fora)
            ring = []
            for dv, dr in ((-RIB_W / 2, -RIB_H / 2), (RIB_W / 2, -RIB_H / 2), (RIB_W / 2, RIB_H / 2),
                           (-RIB_W / 2, RIB_H / 2)):
                ring.append(tuple(P(d + nd * dr, s * RIB_V + dv, z + nz * dr)))
            rings.append(ring)
        quad_faces(mb, rings, LAC, caps=True)
        # cintas de ouro nas pontas da costela (0,12 para fora)
        for d, z, a in (pts[1], pts[-2]):
            mb.box((0.5, RIB_W + 0.24, RIB_H + 0.24), P(d, s * RIB_V, z), BF.r(0, -a, 0), GOLD, 0.0)
    # contraventamento entre as costelas (vigas escuras atravessadas) a cada 2 pontos do arco
    for i in range(2, len(pts) - 2, 2):
        d, z, a = pts[i]
        mb.box((0.7, 2 * RIB_V - RIB_W, 0.8), P(d, 0.0, z), BF.r(0, -a, 0), WD, 0.0)
    # montantes vermelhos: da costela ate a transversina (onde a folga passa de 0,8)
    for d in stations():
        if not (PIERS[0] + PIER_HD < d < PIERS[1] - PIER_HD):
            continue
        dz = d - (PIERS[0] + PIERS[1]) / 2
        R = math.hypot(pts[0][0] - (PIERS[0] + PIERS[1]) / 2, pts[0][1] - cz)
        zr = cz + math.sqrt(max(0.0, R * R - dz * dz)) + RIB_H / 2 - 0.1
        if TR_B - zr < 0.8:
            continue
        for s in (-1, 1):
            mb.box((0.8, 0.8, TR_B - zr + 0.1), P(d, s * RIB_V, (TR_B + zr) / 2), BF.r(), LAC, 0.0)


def side_spans(mb):
    """vaos laterais: viga-mestra vermelha (sob as longarinas, nas linhas das costelas) + maos-francesas que nascem do
    pilar e do encontro; montantes curtos do pilar ate a viga"""
    for (da, db, strut_from) in ((d_edge(0.0) + 1.5, PIERS[0] + PIER_HD, "pier0"),
                                 (PIERS[1] - PIER_HD, 79.0, "pier1")):
        for s in (-1, 1):
            v = s * RIB_V
            mb.beam(P(da, v, TR_B - 0.9), P(db, v, TR_B - 0.9), RIB_W, 1.8, LAC, 0.0)
            # mao-francesa: do pilar (a 6 abaixo do berco) ate 1/3 do vao
            if strut_from == "pier0":
                p0 = P(PIERS[0] - PIER_HD + 0.4, v, CAP_Z + 1.0)
                p1 = P(PIERS[0] - 9.0, v, TR_B - 1.8)
                p2 = P(d_edge(v) + 2.0, v, CAP_Z + 4.0)
                p3 = P(d_edge(v) + 8.5, v, TR_B - 1.8)
            else:
                p0 = P(PIERS[1] + PIER_HD - 0.4, v, CAP_Z + 1.0)
                p1 = P(PIERS[1] + 8.0, v, TR_B - 1.8)
                p2 = P(78.6, v, CAP_Z + 4.0)
                p3 = P(73.6, v, TR_B - 1.8)
            mb.beam(p0, p1, 1.1, 1.1, LAC, 0.0)
            mb.beam(p2, p3, 1.1, 1.1, LAC, 0.0)
            # montante sobre o pilar (do berco a viga)
            dp = PIERS[0] if strut_from == "pier0" else PIERS[1]
            mb.box((1.1, 1.1, TR_B - 1.8 - CAP_Z), P(dp - (1.6 if strut_from == "pier0" else -1.6), v,
                                                     (TR_B - 1.8 + CAP_Z) / 2), BF.r(), LAC, 0.0)


# ================================================================== promontorio
def flags_strip(mb, d0, d1, hw, z_top, key, m=STP):
    """lajes em fiadas atravessadas (2-3 lajes por fiada, juntas desencontradas), topo z_top, chanfro = junta"""
    d = d0
    r = 0
    while d < d1 - 0.2:
        ln = 1.7 + 0.9 * hsh(key, r)
        db = min(d1, d + ln)
        if d1 - db < 0.8:
            db = d1
        n = 2 + (1 if hsh(key, r, "n") > 0.5 else 0)
        cuts = [-hw] + sorted(-hw + 2 * hw * (k + 0.3 + 0.4 * hsh(key, r, k)) / n for k in range(n - 1)) + [hw]
        for va, vb in zip(cuts, cuts[1:]):
            poly = [tuple(P(d, va, 0)[:2]), tuple(P(db, va, 0)[:2]), tuple(P(db, vb, 0)[:2]), tuple(P(d, vb, 0)[:2])]
            K.slab_poly(mb, ccw(poly), z_top - 0.45, z_top, 0.07, m)
        d = db
        r += 1


def kerb(mb, d0, d1, v, key):
    d = d0
    k = 0
    while d < d1 - 0.2:
        db = min(d1, d + 2.4 + 1.2 * hsh(key, k))
        if d1 - db < 0.8:
            db = d1
        mb.box((db - d - 0.08, 0.6, 0.9), P((d + db) / 2, v, T1 - 0.15), BF.r(), STD, 0.06)
        d = db
        k += 1


def headland(mb, br):
    # soleira leste (cabeca da ponte): lajes largas +0,3, da ultima tabua ate o caminho
    flags_strip(mb, D1, LN + 4.5, FAS[1] + 0.2, T1 + 0.3, "hlE")
    # caminho de lajes no leito do op_terrain (+0,12) com meio-fio escuro (+0,3): ate a soleira do portao e depois
    for a, b, key in ((LN + 4.5, SOL[0] - 0.1, "pA"), (SOL[1] + 0.1, HEAD - 10.0, "pB")):
        flags_strip(mb, a, b, PATH_HW - 0.05, T1 + 0.12, key)
        for s in (-1, 1):
            kerb(mb, a, b, s * (PATH_HW + 0.3), key + str(s))
    # cabeca de ponte da ancora: laje larga +0,3 ate a borda + 2 pilares-mestre de pedra (oyabashira)
    flags_strip(mb, HEAD - 10.0, HEAD + 0.3, FAS[1] + 0.2, T1 + 0.3, "hlA")
    for s in (-1, 1):
        F = Frame(*P(HEAD - 1.4, s * (FAS[1] + 1.1), T1)[:2], T1, ANG)
        K.bb(mb, F, -1.0, 1.0, -1.0, 1.0, -0.6, 0.5, STD)
        K.bb(mb, F, -0.75, 0.75, -0.75, 0.75, 0.5, 4.6, "Stone_OP_Wall")
        K.bb(mb, F, -0.92, 0.92, -0.92, 0.92, 4.6, 5.0, STD)
        K.giboshi(br, F, 0.0, 0.0, 5.0, 1.7)
    # 2 toro de pedra flanqueando a cabeca de ponte (fora do vao de 18)
    for i, s in enumerate((-1, 1)):
        p = P(HEAD - 7.0, s * 14.0, T1)
        c = K.toro(br, Frame(p.x, p.y, T1 - 0.1, ANG), 1.05, m=STW)
        light("L_OPProp_Lamp_Saida_Toro_%d" % i, "POINT", tuple(c), 30.0, WARM, 0.2)
        col_box("OP_ExitToro", (2.6, 2.6, 6.6), (p.x, p.y, T1 + 3.2))


def anchor_guard():
    """barreira PROVISORIA (next_island_guard): 2 cavaletes em X de madeira + 3 travessas entre os pilares-mestre"""
    mg = MB("OP_Exit_AnchorGuard", C, random.Random(9101), detail="near")
    d = HEAD - 1.4
    for v in (-6.0, 6.0):
        F = Frame(*P(d, v, 0)[:2], T1, ANG)
        for s in (-1, 1):                                      # pernas em X (vistas de frente)
            K.beam(mg, F, (0.0, s * -1.5, 0.0), (0.0, s * 1.5, 3.2), 0.28, 0.28, WD)
        K.bb(mg, F, -0.25, 0.25, -1.7, 1.7, 0.0, 0.18, WD)     # sapata
    for z, h in ((T1 + 3.2, 0.36), (T1 + 2.0, 0.3), (T1 + 0.9, 0.3)):
        mg.box((0.3, 2 * (FAS[1] + 0.5), h), P(d + (0.0 if z > T1 + 3 else 0.18), 0.0, z), BF.r(), WM, 0.0)
    ob = mg.finish()
    ob["next_island_guard"] = True
    ob["note"] = "PROVISORIO: termino seguro da ancora One Punch Man (area 6 ainda nao existe); a integracao da area 6 apaga"
    return ob


# ================================================================== encaixe com a falesia (PROVISORIO, ver relatorio)
NOTCH = (77.0, 88.4, 10.5)          # d0, d1, meia largura: cabeca leste da ponte


def terrain_notch():
    """ENTALHE DA CABECA LESTE (acrescimo pontual de encaixe, documentado): o anel da falesia do op_terrain (aprovado)
    passa RETO pela cabeca da ponte de saida e o labio verde (89..90) cobre o fim do tabuado (88,26). Aqui so os
    vertices do OP_Ter_Cliff / OP_Ter_Ground DENTRO da pegada do encontro leste e acima do berco descem para baixo dele
    (sob a soleira e o encontro de pedra). PEDIDO ao dono do terreno: entalhe proprio na cabeca da ponte (como o
    FALL_NOTCH das quedas); quando existir, apagar esta funcao."""
    import bpy
    d0, d1, hw = NOTCH
    zc = TR_B - 0.1
    n = 0
    for nm in ("OP_Ter_Cliff", "OP_Ter_Ground"):
        ob = bpy.data.objects.get(nm)
        if not ob or ob.type != "MESH":
            continue
        M = ob.matrix_world
        Mi = M.inverted()
        for v in ob.data.vertices:
            w = M @ v.co
            dx, dy = w.x - L.EXIT_START[0], w.y - L.EXIT_START[1]
            d = dx * UX + dy * UY
            vv = -dx * UY + dy * UX
            if d0 <= d <= d1 and abs(vv) <= hw and w.z > zc:
                w.z = zc + (w.z - zc) * 0.01          # mantem a ordem vertical (sem face degenerada)
                v.co = Mi @ w
                n += 1
        ob.data.update()
    return n


# ================================================================== cameras de revisao
def cams():
    g = L.gate_opm_pos()
    a = L.anchor_opm_pos()
    sk = L.SKULL_C
    cs = {
        "CAM_OPExit_PH_Head": (tuple(P(-14.0, 3.0, T1 + EYE)), tuple(P(40.0, 0.0, T1 + 4.0)), 22),
        "CAM_OPExit_PH_Mid": (tuple(P(46.0, 6.0, T1 + EYE)), (sk[0] - 6.0, sk[1], 112.0), 22),
        "CAM_OPExit_PH_Gate": (tuple(P(GATE_D - 30.0, -3.0, T1 + EYE)), (g[0], g[1], T1 + 8.0), 22),
        "CAM_OPExit_PH_Anchor": (tuple(P(GATE_D + 6.0, 3.0, T1 + EYE)), tuple(P(HEAD + 20.0, 0.0, T1 + 1.0)), 22),
        "CAM_OPExit_PH_EastHead": (tuple(P(68.0, 5.0, T1 + EYE)), tuple(P(98.0, -1.0, T1 + 2.0)), 22),
        "CAM_OPExit_Elev": (tuple(P(44.0, -78.0, 66.0)), tuple(P(44.0, 0.0, 72.0)), 24),
        "CAM_OPExit_Under": (tuple(P(30.0, -34.0, 50.0)), tuple(P(44.0, 0.0, 78.0)), 22),
        "CAM_OPExit_HeadW": ((232.0, 206.0, 58.0), tuple(P(6.0, 0.0, 74.0)), 26),
        "CAM_OPExit_Promontorio": (tuple(P(52.0, 66.0, 160.0)), tuple(P(104.0, -30.0, 96.0)), 26),
    }
    for n, (loc, tgt, lens) in cs.items():
        DL.camera(n, loc, tgt, lens)


# ================================================================== build
def build():
    br = MB("OP_Exit_Bridge", C, random.Random(9001), detail="near")
    deck(br)
    lamps = rails(br)
    arch(br)
    side_spans(br)
    st = MB("OP_Exit_Stone", C, random.Random(9002), detail="near")
    piers(st, br)
    west_head(st)
    east_head(st)
    headland(st, br)
    st.finish()
    br.finish()
    for i, c in enumerate(lamps):
        light("L_OPProp_Lamp_Saida_%d" % i, "POINT", tuple(c), 130.0, WARM, 0.35)
    anchor_guard()
    nn = terrain_notch()
    cams()
    print("OP_EXIT ok (entalhe leste: %d vertices do terreno baixados)" % nn)
