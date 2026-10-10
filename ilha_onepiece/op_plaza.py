# op_plaza.py - V2-3 da Ilha 5 (ONE PIECE / WANO): PRACA DE MINERACAO (PLANO_V2 secoes 2, 3.2 'Eixo', 3.3, 8 U16, 9;
# feedback 10/10 U5/U16 + rodada 2 G3 "pontes, lanternas e caminho aprovados"). Zona "plaza" do build_op
# (ZONE_MODULES_V2_0["plaza"] = ["op_plaza"]: o op_m2_praca/op_m2_trecho.build_praca da V1 NAO roda mais - borda do
# trecho M2 com frestas e estandartes). Prefixo OP_Plz_, colecao 03_PLAZA. Le SO a planta V2 (op_layout) e o kit V2
# (op_kit2: lamp_andon, toro2, rail2 = a linguagem aprovada); do op_kit V1 so as primitivas (bb/lathe/bench/cull).
#
# DIAGNOSTICO: "a praca le como um grande vazio cinza" (prisma liso + emblema colado + borda sem desenho). O centro
# continua LIVRE (70 minerios: PRACA_LIVRE, piso PLANO 92,2 na colisao do op_col), entao a resposta e DESENHO DE PISO +
# BORDA VIVA, nada no meio:
#   PISO = a linguagem do street2 aprovado (lajes ~3,4 x 1,7 assentadas em fiadas com junta de 0,08 sobre BERCO
#     escuro; cada laje e SO a face de cima, como as ruas da capital: topo P + 0,2 = o mesmo das ruas -> a praca emenda
#     RENTE na rua da fachada oeste e no sando), em 4 desenhos:
#     - EIXO (PLANO_V2 3.2): faixa de x +-15 (a largura da avenida + calcadas) em pedra clara assentada no sentido N-S,
#       com guias de pedra, da escadaria Praca ate o pe da escada Adro (sob o portao vermelho): "a avenida continua ate
#       o castelo" sem relevo nenhum (rente);
#     - EIXO TRANSVERSAL (y 209..223) do mesmo assentamento: liga a escada do Summon (leste) a viela da casa de cha
#       (oeste) passando pelo emblema;
#     - MEDALHAO r 27,2 em volta do EMBLEMA REBAIXADO (o do M2, mantido: incrustacao 0,07 abaixo do piso, miolo + 8
#       petalas + anel, quadro circulo -> quadrado 30 x 30 = a largura do eixo) com lajes radiais e anel de incrustacao;
#     - CAMPOS: paineis de ~24 x 24 entre linhas de pedra (guias de 0,9 em Stone_OP_Curb), lajes E-O em tons
#       misturados (praca / pedra / 1 clara em 10) - de cima (camera do jogo) le como um piso desenhado, na altura do
#       jogador como pedra assentada;
#     - BORDA de 3 em lajes ao longo do contorno (soleira da praca).
#   BORDA (tudo fora da MiningZone + 8; NENHUM estandarte - U16):
#     - quedas de 4 para a rua do arrimo (sul), viela leste e terraco do Summon (leste): MEIO-FIO DE PEDRA no labio
#       (1,2 x 0,95, capa de lajes) com o GUARDA-CORPO VERMELHO do kit2 (rail2) por cima - a mesma linguagem das pontes
#       aprovadas; a capa encosta no labio do arrimo (y 118 = borda da colisao): a junta rua x praca (fresta de 0,2..0,8
#       medida em y 117..119) fica sob o meio-fio; aberturas na escadaria Praca e na escada do Summon, com 2 toro2;
#     - oeste (mesmo nivel da rua da fachada oeste): MURETAS BAIXAS de assento (1,35) em trechos de ~12 com vao de 5
#       (passagem para as lojas), tampo de tabuas em trecho alternado, andon do kit2 nas bocas das vielas;
#     - norte (arrimo do adro): bancos encostados ao muro, andon entre eles, 2 toro2 no pe da escada Adro.
# COLISAO (op_col faz o piso): meio-fio + guarda-corpo (1 caixa por trecho), muretas, bancos, andon/toro (caixa ate a
#   guarda de 8,5: nao viram degrau). ~45 caixas, todas fora da MiningZone. LUZES so NightOnly (L_OPProp_Lamp_Plz_*).
# ORCAMENTO: plaza <= 34k tris (teto do export 34k / 36 MeshParts). CAMERAS CAM_OP_V23Plz_* (folhas; fora do export).
# REUSO: pave_poly/face_poly/clip_convex (assentamento de lajes por fiadas recortado num poligono convexo) servem ao
#   op_entry (patio do torii) e ao op_exit (promontorio).
import math
import bpy
import op_lib as DL
from op_lib import MB, Frame, ccw, col_box, light
import op_layout as L
import op_kit as K
import op_kit2 as K2
import op_col

C = "03_PLAZA"
P = L.P
ZT = P + 0.2                      # topo das lajes (= ruas da capital: STREET_DZ 0,2)
ZB = P + 0.12                     # berco escuro (0,12 acima do topo do terreno: sem z-fight)
GAP = 0.04                        # meia junta (junta de 0,08 como o street2)
EYE = L.EYE
CX, CY = L.EMBLEM_C
AX = 15.0                         # meia largura do eixo (avenida 18 + calcadas)
AXB = 0.9                         # guia de pedra do eixo / do transversal / linhas dos paineis
XB = (209.0, 223.0)               # eixo transversal (Summon <-> viela da casa de cha)
R_MED, R_RING = 26.0, 27.2        # medalhao (lajes radiais ate 26) + anel de incrustacao ate 27,2
EDGE_W = 3.0                      # borda de lajes do contorno
XLINES = (39.0, 63.0, 87.0)       # linhas dos paineis (|x|)
YLINES = (142.0, 166.0, 190.0, 242.0, 266.0, 290.0)
# regiao pavimentada (CONVEXA, ccw): o piso P da praca (P_BASE) de x -116 a 116 e de y 118 (labio do arrimo) a 314
# (o canto NO (-110, 300) da planta fica sob a escada OesteAlta: a diagonal (-96, 314) -> (-116, 294) passa por ele)
REG = [(-116.0, 118.0), (64.0, 118.0), (96.0, 124.0), (112.0, 140.0), (116.0, 170.0), (116.0, 314.0), (-96.0, 314.0),
       (-116.0, 294.0)]
SANDO = (107.6, 290.6, 130.0, 301.4)          # sando NE (rua 15 da capital, a partir de x 108)
STR, STZ, STP, STD, STI, CURB = "Stone_OP", "Stone_OP_Plaza", "Stone_OP_Path", "Stone_OP_Dark", "Stone_OP_Inlay", \
    "Stone_OP_Curb"
WALL, WM, WD = "Stone_OP_Wall", "Wood_OP_Mid", "Wood_OP_Dark"
FIELD = [(STZ, 7), (STR, 3), (STP, 1)]
SX_F, SY_F = 4.0, 2.0              # lajes dos campos (a escala da praca de 232: o street2 da rua e 3 x 1,5)
LANE = [(STP, 6), (STZ, 1)]
STATS = {}


def h01(*k):
    return K._h01("plz2", *k)


def pick(mats, *key):
    tot = sum(w for _, w in mats)
    x = h01(*key) * tot
    for m, w in mats:
        x -= w
        if x <= 0:
            return m
    return mats[-1][0]


# ================================================================== geometria 2D (convexo)
def clip_convex(poly, clip):
    """poly (qualquer) recortado pelo convexo ccw 'clip' (Sutherland-Hodgman)"""
    out = list(poly)
    n = len(clip)
    for i in range(n):
        a, b = clip[i], clip[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        out = DL.clip_half(out, -ey, ex, ey * a[0] - ex * a[1])       # lado esquerdo da aresta (dentro de um ccw)
        if len(out) < 3:
            return []
    return out


def cut_disc(poly, c, r):
    """tira do poligono o disco (c, r) por um corte TANGENTE (semiplano fora da tangente na direcao do centroide):
    o pedaco que fica esta inteiro fora do disco; a sobra (<= 0,1) cai no berco escuro = le como junta"""
    n_ = len(poly)
    if all(L.seg_dist(c[0], c[1], poly[i][0], poly[i][1], poly[(i + 1) % n_][0], poly[(i + 1) % n_][1])[0] >= r
           for i in range(n_)) and not L.point_in_poly(c[0], c[1], poly):
        return poly
    mx = sum(p[0] for p in poly) / len(poly)
    my = sum(p[1] for p in poly) / len(poly)
    dx, dy = mx - c[0], my - c[1]
    d = math.hypot(dx, dy) or 1.0
    nx, ny = dx / d, dy / d
    out = DL.clip_half(poly, nx, ny, -(nx * c[0] + ny * c[1] + r))
    return out if len(out) >= 3 else []


def area(p):
    return abs(L.area(p)) if len(p) >= 3 else 0.0


def face_poly(mb, pts, z, m):
    """face plana (so o topo, virada para cima) - poligono convexo"""
    pts = ccw(pts)
    vs = [mb.bm.verts.new((p[0], p[1], z)) for p in pts]
    mb.bm.faces.new(vs)
    mb._post(vs, m, None, 0, 1)


def _rot(p, o, a):
    c, s = math.cos(a), math.sin(a)
    x, y = p[0] - o[0], p[1] - o[1]
    return (x * c + y * s, -x * s + y * c)


def _unrot(p, o, a):
    c, s = math.cos(a), math.sin(a)
    return (o[0] + p[0] * c - p[1] * s, o[1] + p[0] * s + p[1] * c)


def pave_poly(mb, poly, z, mats, key, ang=0.0, sx=3.4, sy=1.7, holes=(), disc=None, origin=(0.0, 0.0), gap=GAP,
              bond=0.5, min_area=0.12):
    """LAJES EM FIADAS (street2): fiadas de 'sy' ao longo do rumo 'ang' (comprimento sorteado 0,8..1,2 x sx, juntas
    desencontradas de fiada a fiada), recortadas no convexo 'poly', menos os retangulos 'holes' (mundo, eixo) e o
    disco 'disc' (c, r). Cada laje = face de cima a z com a junta 'gap' de cada lado. Devolve o numero de lajes."""
    if len(poly) < 3:
        return 0
    lp = ccw([_rot(p, origin, ang) for p in poly])
    u0, u1 = min(p[0] for p in lp), max(p[0] for p in lp)
    v0, v1 = min(p[1] for p in lp), max(p[1] for p in lp)
    r = math.floor((v0 - 0.0) / sy)
    n = 0
    while r * sy < v1:
        va, vb = r * sy + gap, (r + 1) * sy - gap
        off = (bond * sx if r % 2 else 0.0) + 0.23 * sx * h01(key, r, "o")
        u = math.floor((u0 + off) / sx) * sx - off - sx
        k = 0
        while u < u1:
            w = sx * (0.8 + 0.4 * h01(key, r, k))
            ua, ub = u + gap, u + w - gap
            u += w
            k += 1
            if ub < u0 or ua > u1:
                continue
            q = clip_convex([(ua, va), (ub, va), (ub, vb), (ua, vb)], lp)
            if len(q) < 3:
                continue
            pieces = [[_unrot(p, origin, ang) for p in q]]
            if disc:
                pieces = [cut_disc(p, disc[0], disc[1]) for p in pieces]
                pieces = [p for p in pieces if len(p) >= 3]
            for hr in holes:
                nxt = []
                for p in pieces:
                    xs_ = [t[0] for t in p]
                    ys_ = [t[1] for t in p]
                    if max(xs_) <= hr[0] or min(xs_) >= hr[2] or max(ys_) <= hr[1] or min(ys_) >= hr[3]:
                        nxt.append(p)
                    else:
                        nxt += [s for s in L.subtract_rect(ccw(p), hr) if len(s) >= 3]
                pieces = nxt
            for p in pieces:
                if area(p) >= min_area:
                    face_poly(mb, p, z, pick(mats, key, r, k))
                    n += 1
        r += 1
    return n


def berco(mb, poly, z, holes=()):
    """berco escuro (aparece nas juntas): o convexo menos os retangulos"""
    pieces = [ccw(poly)]
    for hr in holes:
        nxt = []
        for p in pieces:
            nxt += [s for s in L.subtract_rect(ccw(p), hr) if len(s) >= 3] if _hits(p, hr) else [p]
        pieces = nxt
    for p in pieces:
        face_poly(mb, p, z, STD)


def _hits(p, hr):
    xs_ = [t[0] for t in p]
    ys_ = [t[1] for t in p]
    return not (max(xs_) <= hr[0] or min(xs_) >= hr[2] or max(ys_) <= hr[1] or min(ys_) >= hr[3])


def _bbox(poly):
    xs_ = [p[0] for p in poly]
    ys_ = [p[1] for p in poly]
    return (min(xs_), min(ys_), max(xs_), max(ys_))


# ================================================================== piso
def stair_holes(pad=0.35):
    out = []
    for nm in ("Praca", "Adro", "OesteAlta", "Summon", "Mirante"):
        out.append(_bbox(op_col.stair_footprint(nm, pad)))
    out.append(SANDO)
    return out


def rin():
    return ccw(DL.offset_poly(ccw(REG), -EDGE_W))


def floor():
    mb = MB("OP_Plz_Piso", C, detail="far", floor=-999)
    mb2 = MB("OP_Plz_Piso_Eixo", C, detail="far", floor=-999)
    HO = stair_holes()
    disc = ((CX, CY), R_RING)
    RI = rin()
    n = {}
    # --- berco (toda a regiao, menos as escadas, o sando e o MEDALHAO: o emblema e o medalhao sao lajes com chanfro
    # cujas juntas em V fecham sem berco; o berco sob a incrustacao rebaixada seria quase coplanar a ela)
    sqd = (CX - R_RING, CY - R_RING, CX + R_RING, CY + R_RING)
    berco(mb, REG, ZB, list(HO) + [sqd])
    NW = 64
    for i in range(NW):
        a0, a1 = 2 * math.pi * i / NW, 2 * math.pi * (i + 1) / NW
        sqp = lambda a: (CX + R_RING / max(abs(math.cos(a)), abs(math.sin(a))) * math.cos(a),
                         CY + R_RING / max(abs(math.cos(a)), abs(math.sin(a))) * math.sin(a))
        w = [(CX + R_RING * math.cos(a0), CY + R_RING * math.sin(a0)), sqp(a0), sqp(a1),
             (CX + R_RING * math.cos(a1), CY + R_RING * math.sin(a1))]
        if area(w) > 0.05:
            berco(mb, w, ZB, HO)
    # --- eixo N-S (lajes ao longo de y) + guias
    ax_in = clip_convex([(-AX + AXB, 100.0), (AX - AXB, 100.0), (AX - AXB, 330.0), (-AX + AXB, 330.0)], RI)
    n["eixo"] = pave_poly(mb2, ax_in, ZT, LANE, "eixo", ang=math.pi / 2, sx=3.4, sy=1.7, holes=HO, disc=disc)
    for s in (-1, 1):
        g = clip_convex([(s * (AX - AXB), 100.0), (s * AX, 100.0), (s * AX, 330.0), (s * (AX - AXB), 330.0)], RI)
        n["guias"] = n.get("guias", 0) + pave_poly(mb2, g, ZT, [(CURB, 1)], "gx%d" % s, ang=math.pi / 2, sx=2.6, sy=AXB,
                                                     holes=HO, disc=disc, origin=(s * (AX - AXB), 0.0))
    # --- eixo transversal (lajes no sentido N-S, como o eixo) + guias
    for s in (-1, 1):
        xa, xb = sorted((s * AX, s * 140.0))
        band = clip_convex([(xa, XB[0] + AXB), (xb, XB[0] + AXB), (xb, XB[1] - AXB), (xa, XB[1] - AXB)], RI)
        n["transv"] = n.get("transv", 0) + pave_poly(mb2, band, ZT, LANE, "tr%d" % s, ang=math.pi / 2, holes=HO,
                                                      disc=disc)
        for yg in ((XB[0], XB[0] + AXB), (XB[1] - AXB, XB[1])):
            g = clip_convex([(xa, yg[0]), (xb, yg[0]), (xb, yg[1]), (xa, yg[1])], RI)
            n["guias"] += pave_poly(mb2, g, ZT, [(CURB, 1)], "gt%d_%d" % (s, int(yg[0])), sx=2.6, sy=AXB, holes=HO,
                                    disc=disc, origin=(0.0, yg[0]))
    # --- paineis (lajes E-O) entre as linhas
    cols = [AX] + list(XLINES) + [140.0]
    rows_s = [100.0] + [y for y in YLINES if y < XB[0]] + [XB[0]]
    rows_n = [XB[1]] + [y for y in YLINES if y > XB[1]] + [330.0]
    nl = 0
    npn = 0
    for s in (-1, 1):
        for ci, (ca, cb) in enumerate(zip(cols, cols[1:])):
            xa = ca + (AXB / 2 if ci > 0 else 0.0)
            xb = cb - (AXB / 2 if ci < len(cols) - 2 else 0.0)
            for rows in (rows_s, rows_n):
                for ri_, (ra, rb) in enumerate(zip(rows, rows[1:])):
                    ya = ra + (AXB / 2 if ri_ > 0 else 0.0)
                    yb = rb - (AXB / 2 if ri_ < len(rows) - 2 else 0.0)
                    x0, x1 = sorted((s * xa, s * xb))
                    pnl = clip_convex([(x0, ya), (x1, ya), (x1, yb), (x0, yb)], RI)
                    npn += pave_poly(mb, pnl, ZT, FIELD, "p%d_%d_%d" % (s, ci, int(ya)), sx=SX_F, sy=SY_F, holes=HO,
                                     disc=disc)
                    # linha horizontal no topo do painel (menos a ultima)
                    if ri_ < len(rows) - 2:
                        g = clip_convex([(x0, rb - AXB / 2), (x1, rb - AXB / 2), (x1, rb + AXB / 2), (x0, rb + AXB / 2)], RI)
                        nl += pave_poly(mb2, g, ZT, [(CURB, 1)], "ly%d_%d_%d" % (s, ci, int(rb)), sx=2.6, sy=AXB,
                                        holes=HO, disc=disc, origin=(0.0, rb - AXB / 2))
            # linha vertical a direita da coluna (menos a ultima)
            if ci < len(cols) - 2:
                x0, x1 = sorted((s * (cb - AXB / 2), s * (cb + AXB / 2)))
                for ya, yb in ((100.0, XB[0]), (XB[1], 330.0)):
                    g = clip_convex([(x0, ya), (x1, ya), (x1, yb), (x0, yb)], RI)
                    nl += pave_poly(mb2, g, ZT, [(CURB, 1)], "lx%d_%d_%d" % (s, ci, int(ya)), ang=math.pi / 2, sx=2.6,
                                    sy=AXB, holes=HO, disc=disc, origin=(x0, 0.0))
    n["paineis"], n["linhas"] = npn, nl
    # --- borda de lajes no contorno (fiadas ao longo de cada aresta, cantos em meia-esquadria)
    Rg = ccw(REG)
    nb = 0
    for i in range(len(Rg)):
        a, b = Rg[i], Rg[(i + 1) % len(Rg)]
        ai, bi = RI[i], RI[(i + 1) % len(RI)]
        quad = ccw([a, b, bi, ai])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        nb += pave_poly(mb, quad, ZT, [(STP, 3), (STR, 2)], "bd%d" % i, ang=ang, sx=3.0, sy=EDGE_W / 2, holes=HO,
                        origin=a)
    # faixa NE fora da regiao convexa (x 116..117,6, y 262..314): ate a frente das lojas NE
    ne = [(116.0, 262.0), (117.6, 262.0), (117.6, 314.0), (116.0, 314.0)]
    berco(mb, ne, ZB, HO)
    nb += pave_poly(mb, ne, ZT, [(STP, 3), (STR, 2)], "bdne", ang=math.pi / 2, sx=3.0, sy=1.6, holes=HO,
                    origin=(116.0, 262.0))
    n["borda"] = nb
    mb.finish(recalc=False)
    mb2.finish(recalc=False)
    return n


# ------------------------------------------------------------------ medalhao + emblema rebaixado (o do M2)
EMB_SQ = 15.0


def emblem():
    """EMBLEMA REBAIXADO (desenho do M2 mantido): miolo + 8 petalas + anel de incrustacao 0,07 abaixo do piso,
    fundos e anel de pedra rentes, quadro circulo r 13 -> quadrado 30 x 30; em volta, o MEDALHAO: lajes radiais do
    quadrado ate r 26 (2 aneis, juntas desencontradas) e anel de incrustacao 26..27,2"""
    mb = MB("OP_Plz_Emblema", C, detail="far", floor=-999)
    zt, zi, zb = ZT, ZT - 0.07, P - 0.05
    cx, cy = CX, CY
    G = [2 * math.pi * k / 32 for k in range(32)]
    pol = lambda r, a: (cx + r * math.cos(a), cy + r * math.sin(a))
    R0, R1, R2, R3 = 2.2, 9.4, 11.2, 13.0
    slab = lambda poly, z1, m, c=0.05: K.slab_poly(mb, ccw(poly), zb, z1, c, m, False)   # so chanfro + topo
    slab([pol(R0, a) for a in G], zi, STI)
    rs = [2.2, 3.4, 4.6, 5.8, 7.0, 8.2, 9.4]
    wfun = lambda r: 0.3 * math.sin(math.pi * (r - R0) / (R1 - R0)) ** 0.8
    for k in range(8):
        th = k * math.pi / 4
        petal = [pol(r, th - wfun(r)) for r in rs] + [pol(r, th + wfun(r)) for r in reversed(rs[1:-1])]
        slab(petal, zi, STI)
        arc_in = [pol(R0, G[4 * k + j]) for j in range(5)] if k < 7 else [pol(R0, G[28 + j]) for j in range(4)] + [pol(R0, 0.0)]
        nxt = th + math.pi / 4
        arc_out = [pol(R1, a) for a in ([G[4 * k + j] for j in range(5)] if k < 7 else [G[28 + j] for j in range(4)] + [0.0])]
        bg = arc_in + [pol(r, nxt - wfun(r)) for r in rs[1:-1]] + list(reversed(arc_out)) + \
            [pol(r, th + wfun(r)) for r in reversed(rs[1:-1])]
        slab(bg, zt, STZ)
    for j in range(16):
        a3 = [G[(2 * j + i) % 32] + (2 * math.pi if (2 * j + i) >= 32 else 0.0) for i in range(3)]
        slab([pol(R1, a) for a in a3] + [pol(R2, a) for a in reversed(a3)], zt, STR)
        b3 = [G[(2 * j + 1 + i) % 32] + (2 * math.pi if 2 * j + 1 + i >= 32 else 0.0) for i in range(3)]
        slab([pol(R2, a) for a in b3] + [pol(R3, a) for a in reversed(b3)], zi, STI)
    sq = lambda a: (cx + EMB_SQ / max(abs(math.cos(a)), abs(math.sin(a))) * math.cos(a),
                    cy + EMB_SQ / max(abs(math.cos(a)), abs(math.sin(a))) * math.sin(a))
    for k in range(8):
        a5 = [G[(4 * k + j) % 32] + (2 * math.pi if 4 * k + j >= 32 else 0.0) for j in range(5)]
        slab([pol(R3, a) for a in a5] + [sq(a5[-1]), sq(a5[0])], zt, STP, 0.07)
    # medalhao: 2 aneis de lajes radiais (quadrado -> r 19,4 -> r 24) com juntas desencontradas + anel de incrustacao
    NGm = 64
    Gm = [2 * math.pi * k / NGm for k in range(NGm + 1)]
    RM = 22.6                                     # > canto do quadrado (15 x raiz 2 = 21,2)

    def sqr(a, r):                                # ponto no 'raio' r do quadrado/circulo misto (quadrado em r <= 15)
        return pol(r, a)
    for ring, (step, off) in enumerate(((4, 0), (2, 1))):            # anel de fora em lajes menores (32): junta viva
        for i in range(off, NGm + off, step):
            aa = [Gm[(i + j) % NGm] + (2 * math.pi if i + j >= NGm else 0.0) for j in range(step + 1)]
            if ring == 0:
                inner = [sq(a) for a in aa]
                poly = inner + [pol(RM, a) for a in reversed(aa)]
            else:
                poly = [pol(RM, a) for a in aa] + [pol(R_MED, a) for a in reversed(aa)]
            # o quadrado tem cantos em 45 graus: os 4 pontos 'sq' de cada arco ficam no mesmo lado (step 4 = 22,5
            # graus, cantos na grade): o lado de dentro e reto
            slab(poly, zt, pick([(STP, 2), (STZ, 3), (STR, 2)], "med", ring, i), 0.06)
    for i in range(0, NGm, 2):
        aa = [Gm[i], Gm[i + 1], Gm[i + 2]]
        slab([pol(R_MED, a) for a in aa] + [pol(R_RING, a) for a in reversed(aa)], zi, STI, 0.04)
    mb.finish()


# ================================================================== borda
def _edge_pts():
    return ccw(REG)


DROP_EDGES = [  # (a, b, [aberturas (t0, t1) em distancia ao longo]) - quedas para T1
    ((-116.0, 118.0), (-15.9, 118.0)),
    ((15.9, 118.0), (64.0, 118.0)),
    ((64.0, 118.0), (96.0, 124.0)),
    ((96.0, 124.0), (112.0, 140.0)),
    ((112.0, 140.0), (116.0, 170.0)),
    ((116.0, 170.0), (116.0, 207.4)),
    ((116.0, 224.6), (116.0, 262.0)),
]
KERB_W, KERB_H = 1.2, 0.75
COL_TALL = 11.0                   # caixas de guarda/toro/andon: topo P + 10,5 (> 1,55 do assento + pulo 7,2 + folga)


def kerb_rail(mb, mr):
    """meio-fio de pedra no labio + guarda-corpo vermelho (rail2) por cima; 1 caixa de colisao por trecho"""
    n = 0
    for a, b in DROP_EDGES:
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = -uy, ux                                    # para DENTRO da praca (regiao ccw)
        ang = math.atan2(dy, dx)
        F = Frame(a[0], a[1], P, ang)                       # +x ao longo, +y para dentro
        # corpo em blocos de 2,2..3,6 (juntas de 0,06) + capa de lajes com pingadeira para dentro
        x = 0.0
        k = 0
        while x < ln - 0.2:
            x2 = min(ln, x + 3.0 + 1.6 * h01("kb", a[0], a[1], k))
            if ln - x2 < 0.9:
                x2 = ln
            K.bb(mb, F, x + 0.03, x2 - 0.03, 0.02, KERB_W - 0.02, -0.25, KERB_H - 0.2,
                 WALL if h01("kbm", a[0], k) > 0.18 else STR)
            x, k = x2, k + 1
        x = -0.1
        k = 0
        while x < ln + 0.1 - 0.2:
            x2 = min(ln + 0.1, x + 3.4 + 1.4 * h01("kc", a[0], a[1], k))
            if ln + 0.1 - x2 < 0.9:
                x2 = ln + 0.1
            K.bb(mb, F, x + 0.03, x2 - 0.03, -0.06, KERB_W + 0.12, KERB_H - 0.2, KERB_H, STP, 0.04)
            x, k = x2, k + 1
        K2.rail2(mr, F, [(0.25, KERB_W / 2), (ln - 0.25, KERB_W / 2)], h=2.55, base=KERB_H, step=3.2)
        cx, cy = a[0] + ux * ln / 2 + nx * KERB_W / 2, a[1] + uy * ln / 2 + ny * KERB_W / 2
        # guarda ALTA (como as do op_col): o corrimao nao vira degrau para toro/andon/telhados vizinhos
        col_box("OP_PlzRail", (ln + 0.4, KERB_W + 0.3, COL_TALL), (cx, cy, P - 0.5 + COL_TALL / 2), (0.0, 0.0, ang))
        n += 1
    return n


WEST_X = -116.0
WEST_FREE = [(140.0, 151.0), (167.0, 204.0), (220.0, 257.0), (273.0, 284.0)]   # entre as bocas das vielas (y 159/212/265)
# (o canto SO, y 118..140, fica ABERTO: e a entrada da rota Bairro do canal -> quarteirao oeste pela escada Sudoeste)


def west_walls(mb):
    """muretas baixas de assento (1,35) em trechos de ~12 com vao de 5; tampo de tabuas no trecho alternado"""
    n = 0
    segs = []
    for a, b in WEST_FREE:
        ln = b - a
        k = max(1, int(round((ln + 5.0) / 17.0)))
        w = (ln - 5.0 * (k - 1)) / k
        for i in range(k):
            y0 = a + i * (w + 5.0)
            segs.append((y0, y0 + w))
    x0, x1 = WEST_X + 0.5, WEST_X + 1.6
    h = 1.35
    for i, (y0, y1) in enumerate(segs):
        F = Frame((x0 + x1) / 2, (y0 + y1) / 2, P, math.pi / 2)     # +x = ao longo (y do mundo)
        L_ = y1 - y0
        x = -L_ / 2
        k = 0
        while x < L_ / 2 - 0.2:                                         # blocos de cantaria (2 fiadas desencontradas)
            x2 = min(L_ / 2, x + 1.8 + 1.2 * h01("ww", i, k))
            if L_ / 2 - x2 < 0.8:
                x2 = L_ / 2
            K.bb(mb, F, x + 0.03, x2 - 0.03, -0.55, 0.55, -0.25, 0.55, STD if h01("wwm", i, k) > 0.55 else WALL)
            x, k = x2, k + 1
        x = -L_ / 2
        k = 0
        while x < L_ / 2 - 0.2:
            x2 = min(L_ / 2, x + 1.2 + 1.4 * h01("wx", i, k))
            if L_ / 2 - x2 < 0.8:
                x2 = L_ / 2
            K.bb(mb, F, x + 0.03, x2 - 0.03, -0.55, 0.55, 0.55, h - 0.22, WALL if h01("wxm", i, k) > 0.3 else STD)
            x, k = x2, k + 1
        K.bb(mb, F, -L_ / 2 - 0.1, L_ / 2 + 0.1, -0.68, 0.68, h - 0.22, h, STP, 0.05)          # capa
        if i % 2 == 0:                                                    # tampo de tabuas (assento)
            for j in range(3):
                K.bb(mb, F, -L_ / 2 + 0.5, L_ / 2 - 0.5, -0.6 + j * 0.4 + 0.02, -0.6 + (j + 1) * 0.4 - 0.02, h, h + 0.14,
                     WM)
            for xx in (-L_ / 2 + 0.9, 0.0, L_ / 2 - 0.9):
                K.bb(mb, F, xx - 0.12, xx + 0.12, -0.66, 0.66, h + 0.02, h + 0.2, WD)
        hc = h + (0.2 if i % 2 == 0 else 0.0)                         # colisao = topo visual (sem degrau extra)
        col_box("OP_PlzMureta", (1.5, L_ + 0.3, hc + 0.3), ((x0 + x1) / 2, (y0 + y1) / 2, P - 0.3 + (hc + 0.3) / 2))
        n += 1
    return n, segs


# andon (kit2) e toro2 (kit2) da borda; bancos encostados ao muro norte
ANDON = [(-40.0, 121.4, 0.0), (40.0, 121.4, 0.0), (-88.0, 121.4, 0.0), (88.0, 125.4, 0.0),
         (112.6, 204.6, 0.0), (112.6, 227.4, 0.0),
         (-113.0, 152.6, 0.0), (-113.0, 205.6, 0.0), (-113.0, 258.6, 0.0),
         (-42.0, 311.6, 0.0), (42.0, 311.6, 0.0)]
TORO = [(-19.0, 122.8, 0.95), (19.0, 122.8, 0.95), (-21.5, 308.6, 0.95), (21.5, 308.6, 0.95)]
BENCHES = [(-30.0, 312.0), (30.0, 312.0), (-54.0, 312.0), (54.0, 312.0), (-78.0, 312.0), (78.0, 312.0)]


def props(mp):
    n = 0
    nl = 0
    for i, (x, y, a) in enumerate(ANDON):
        nm = "L_OPProp_Lamp_Plz_%d" % i if i % 2 == 0 else None
        nl += 1 if nm else 0
        K2.lamp_andon(mp, Frame(x, y, ZT, a), nm)
        col_box("OP_PlzLamp", (2.3, 2.3, COL_TALL), (x, y, P - 0.5 + COL_TALL / 2))
        n += 1
    for i, (x, y, s) in enumerate(TORO):
        K2.toro2(mp, Frame(x, y, ZT, 0.0), "L_OPProp_Toro_Plz_%d" % i if i % 2 == 0 else None, s)
        col_box("OP_PlzToro", (3.7 * s, 3.7 * s, COL_TALL), (x, y, P - 0.5 + COL_TALL / 2))
        n += 1
    F0 = Frame(0.0, 0.0, 0.0, 0.0)
    for x, y in BENCHES:
        K.bench(mp, F0, x, y, 7.0, 1.8, 1.7, 0.0, ZT)
        col_box("OP_PlzBench", (7.0, 1.8, 1.9), (x, y, P + 0.95))
        n += 1
    return n


# ================================================================== cameras (folhas; fora do export)
CAMS = {
    "CAM_OP_V23Plz_Cima_Jogo": ((-30.0, 170.0, P + 42.0), (10.0, 232.0, P), 24),
    "CAM_OP_V23Plz_Cima_Sul": ((0.0, 92.0, P + 74.0), (0.0, 205.0, P), 22),
    "CAM_OP_V23Plz_Zenite": ((0.0, 216.0, 420.0), (0.0, 216.5, P), 30),
    "CAM_OP_V23Plz_PH_Norte": ((6.0, 190.0, P + EYE), (0.0, 320.0, P + 8.0), 22),
    "CAM_OP_V23Plz_PH_Leste": ((60.0, 230.0, P + EYE), (118.0, 216.0, P + 3.0), 22),
    "CAM_OP_V23Plz_PH_Oeste": ((-60.0, 205.0, P + EYE), (-118.0, 226.0, P + 3.0), 22),
    "CAM_OP_V23Plz_PH_Sul": ((-20.0, 160.0, P + EYE), (-40.0, 118.0, P + 1.0), 22),
    "CAM_OP_V23Plz_Junta_Rua": ((-36.0, 100.0, L.T1 + EYE), (-48.0, 122.0, P + 0.5), 24),
    "CAM_OP_V23Plz_Close_Emblema": ((0.0, 190.0, P + 13.0), (0.0, 216.0, P), 28),
}


def cams():
    for n_, (loc, tgt, lens) in CAMS.items():
        if bpy.data.objects.get(n_) is None:
            DL.camera(n_, loc, tgt, lens)


def _tris(name):
    ob = bpy.data.objects.get(name)
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob else 0


def build():
    if bpy.data.objects.get("OP_Plz_Piso"):
        return
    n = floor()
    emblem()
    mb = MB("OP_Plz_Borda", C, detail="hero")
    mr = MB("OP_Plz_Guarda", C, detail="near")
    nc = kerb_rail(mb, mr)
    nw, segs = west_walls(mb)
    mp = MB("OP_Plz_Props", C, detail="near")
    npr = props(mp)
    for m_ in (mb, mr, mp):
        K.cull_hidden(m_)
        m_.finish(recalc=False)
    cams()
    tot = sum(_tris(o.name) for o in bpy.data.objects if o.name.startswith("OP_Plz_") and o.type == "MESH")
    print("op_plaza V2: lajes %s | guarda %d trechos, muretas %d, props %d (col %d) | tris %d (piso %d, eixo %d, "
          "emblema %d, borda %d, guarda %d, props %d)" % (n, nc, nw, npr, nc + nw + npr, tot, _tris("OP_Plz_Piso"),
                                                          _tris("OP_Plz_Piso_Eixo"), _tris("OP_Plz_Emblema"),
                                                          _tris("OP_Plz_Borda"), _tris("OP_Plz_Guarda"),
                                                          _tris("OP_Plz_Props")))
