# op_m2_trecho.py - M2 da Ilha 5 (ONE PIECE / WANO): TRECHO DE QUALIDADE FINAL (PLANO_OP secao 14, M2.2), feito so com
# o op_kit. E o padrao que o lead valida no Roblox ANTES de multiplicar o kit (M4: op_capital / op_plaza).
#   build()        zona "capital": RUA DE CHEGADA (lajes em fiadas com junta rebaixada, guias, soleiras), lojas C1, C2,
#                  C5 e C6 do kit (fachada comercial, telhado, varanda, karahafu, chidori, chochin), postes de rua de
#                  Wano, ESCADARIA Praca (pedra em blocos, banzos inclinados com capa e pilaretes, andon no pe).
#                  O RESTO da capital continua em BLOCKOUT (op_blockout.house, escadas, torii do santuario, ruas) ate o
#                  M4 - mesma geometria do M1, sem as pecas que o trecho substitui.
#   build_praca()  zona "plaza" (via op_m2_praca): FAIXA SUL DA PRACA (y 118..170): borda de lajes, eixo de chegada,
#                  campos de lajes 6 x 6 com faixas de pedra (desenho), ARRIMO de pedra aparelhada na queda para a rua
#                  (a faixa |x| <= 120, y 109..170 e excluida do op_terrain), MURETA na borda, 2 toro e 2 estandartes
#                  na chegada da escadaria, EMBLEMA REBAIXADO de verdade no piso em (0, 216) (miolo, 8 petalas e anel em
#                  pedra de incrustacao 0,07 abaixo do piso + junta chanfrada; nada acima de piso + 0,15, sem colisao).
#                  Fora da faixa: piso PROVISORIO liso (1 prisma) + estandartes dos cantos e lanternas do norte com o
#                  kit, ate o op_plaza (M4).
# COTAS: piso visual = colisao + Z_OFF (0,15). O op_terrain deixa SEM pele (corpo a piso - 0,5) a PLAZA e as L.STREETS;
#        nas faixas laterais da rua (|x| 12..16,9) a pele de grama fica 0,15 ABAIXO do topo da laje, dentro do volume
#        dela (nada visivel coplanar). O piso da MiningZone fica a +0,15 (<= +0,3 do PRACA_LIVRE; raycast e na colisao).
# DONOS / PREFIXOS: OP_Cap_M2_* (capital), OP_Plz_M2_* (praca), OP_Ter_M2_Arrimo (arrimo da faixa: e terreno, conta no
#        dono terrain). Luzes so NightOnly (L_OPProp_*, L_OPCap_Win_*). Colisoes: corpo das lojas (OP_CapHouse<nome>,
#        mesmas areas do blockout -> CAM_COL_AREAS do export), postes/andon (OP_PropLamp), toro (OP_PropToro),
#        estandartes (OP_PropBanner), mureta (OP_PlzMureta). Piso/escadas/guardas continuam do op_col (congelado).
# CAMERAS: CAM_OP_M2_* (altura do jogador e closes do trecho; criadas no build, fora do export).
# REGISTRO: build_op.ZONE_MODULES["capital"] = ["op_m2_trecho"], ["plaza"] = ["op_m2_praca"] (acrescimo pontual).
# V2-3 (agente da capital): build() APOSENTADO - o trecho M2 foi absorvido pela quadra AvO do op_capital V2 (kit2);
#        build_praca() continua aqui para o op_m2_praca (zona plaza, agente da praca).
import math, random
import bpy
import op_lib as DL
from op_lib import MB, col_box, Frame, ccw, light
import op_layout as L
import op_blockout as BO
import op_kit as K

T1, P = L.T1, L.P
Z_OFF = 0.15                                   # piso visual do trecho acima da colisao
TRECHO = ("C1", "C2", "C5", "C6")
STREET_RECT = (-16.9, 44.8, 16.9, 109.0)       # rua de chegada pavimentada (de fachada a fachada)
STRIP_Y1 = 170.0                               # fim da faixa sul da praca
QS = 7.2                                       # lado das lajes dos campos da praca
EMBLEM_SQ = 15.0                               # meia largura do quadro do emblema
SENTINEL = "OP_Cap_M2_Rua"
SENTINEL_P = "OP_Plz_M2_Faixa"


def _spec(nm):
    for b in L.BUILDINGS:
        if b[0] == nm:
            return b
    raise KeyError(nm)


def shop_frame(nm):
    nm_, fam, x, y, w, d, deg, z, fl, roof, rm = _spec(nm)
    return Frame(x, y, z, math.radians(deg) - math.pi / 2)


# M6b item 19: fundos que dao para o beco do bloco leste (C6) com janelas, nao reboco liso
BACKS = {"C6": ["plaster", "shoji", "koshi", "plaster"]}


def shop_spec(nm):
    nm_, fam, x, y, w, d, deg, z, fl, roof, rm = _spec(nm)
    sp = dict(K.PRESETS[nm], W=w, D=d, roof_m=rm, seed=1000 + TRECHO.index(nm) * 37)
    if nm in BACKS:
        floors = [dict(f) for f in sp["floors"]]
        floors[0]["back"] = BACKS[nm]
        sp["floors"] = floors
    return sp


def paved_footprint():
    """poligonos (ccw, local) onde o trecho traz o PROPRIO piso (para o op_terrain/op_plaza nao porem tampo ali)"""
    x0, y0, x1, y1 = STREET_RECT
    return [L.rect_poly(STREET_RECT), strip_poly()]


# ================================================================== CAPITAL: rua de chegada + lojas + escadaria
def _street():
    mb = MB(SENTINEL, "05_CAPITAL", random.Random(201), detail="hero", floor=-999)
    reg = ccw(L.rect_poly(STREET_RECT))
    zt = T1 + Z_OFF
    zb = T1 - 0.3
    n = 0
    n += K.pave(mb, reg, -16.9, 16.9, 44.8, 47.4, ((2.6,), 3.0, 4.6), K.ST, zt, zb, key="sol", mats=[(K.ST, 5), (K.STD, 1)])
    n += K.pave(mb, reg, -7.4, 7.4, 47.4, 104.2, ((3.0,), 3.4, 5.0), K.STP, zt, zb, key="eix", mats=[(K.STP, 6), (K.STZ, 2)])
    for s in (-1, 1):
        xa, xb = (7.4, 8.6) if s > 0 else (-8.6, -7.4)
        n += K.pave(mb, reg, xa, xb, 47.4, 104.2, ((1.2,), 3.2, 4.8), K.ST, zt, zb, along="y", key="guia%d" % s)
        xa, xb = (8.6, 16.9) if s > 0 else (-16.9, -8.6)
        n += K.pave(mb, reg, xa, xb, 47.4, 104.2, ((2.6,), 2.8, 4.0), K.STZ, zt, zb, key="lat%d" % s,
                    mats=[(K.STZ, 5), (K.STP, 2)])
    n += K.pave(mb, reg, -16.9, 16.9, 104.2, 109.0, ((2.4,), 3.2, 4.8), K.STP, zt, zb, key="pe", mats=[(K.STP, 3), (K.ST, 2)])
    mb.finish()
    return n


def _shops():
    mb = MB("OP_Cap_M2_Lojas", "05_CAPITAL", random.Random(202), detail="hero")
    out = {}
    for nm in TRECHO:
        F = shop_frame(nm)
        sp = shop_spec(nm)
        out[nm] = K.house(mb, F, sp, "L_OPCap_Win_M2%s" % nm, 70.0)
        K.house_cols("OP_CapHouse" + nm, F, sp)
    K.cull_hidden(mb)                                        # M6b: faces que ninguem ve (orcamento)
    mb.finish(recalc=False)                                  # M6c: sem recalc depois do corte (casca aberta virava)
    return out


LAMPS_RUA = [(-8.0, 54.0), (8.0, 66.0), (-8.0, 77.0), (8.0, 90.0)]


def _lamps_and_stair():
    mb = MB("OP_Cap_M2_Escadaria", "05_CAPITAL", random.Random(203), detail="hero")
    foot, deg, w, n, tread, g = L.stair_frame("Praca")
    Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
    # pilaretes de arranque com ANDON (sobre o banzo: nada no chao da rua, a viela leste fica livre)
    K.stair_stone(mb, Fs, w, n, rise=L.stair_rise("Praca"), tread=tread, z_floor=-0.3, z_off=Z_OFF, cheek_h=1.0,
                  newels=True, newel_lamp="L_OPProp_Lamp_M2Esc")
    for s in (-1, 1):                                        # colisao dos pilaretes de arranque (andam na rua)
        col_box("OP_PropLamp", (2.0, 1.7, 4.4), (s * (w / 2 + 0.6), foot[1] - 0.55, T1 + 2.2))
    ml = mb                                                  # postes no MESMO MB da escadaria (materiais em comum)
    for i, (x, y) in enumerate(LAMPS_RUA):                   # postes de rua (travessa ao longo da rua)
        K.lantern_post(ml, Frame(x, y, T1 + Z_OFF, math.pi / 2), 9.0, 1.7, "L_OPProp_Lamp_M2Rua_%d" % i, 40.0)
        col_box("OP_PropLamp", (0.9, 0.9, 9.0), (x, y, T1 + 4.5))
    K.bench(ml, Frame(0.0, 0.0, 0.0, 0.0), -27.0, 91.6, 6.0, 1.8, 1.7, 0.0, T1)     # recanto da viela do canal
    col_box("OP_CapBench", (6.0, 1.8, 1.7), (-27.0, 91.6, T1 + 0.85))
    K.cull_hidden(mb)                                        # M6b
    mb.finish(recalc=False)                                  # M6c


def _blockout_rest():
    """o RESTO da capital em blockout (igual ao op_blockout.capital do M1, sem C1/C2/C5/C6, sem a escada Praca, sem as
    lanternas da rua e sem a laje da rua de chegada - essas pecas sao do trecho)"""
    rng = random.Random(55)
    mb = MB("OP_Cap_Blockout", "05_CAPITAL", rng, detail="far", floor=None)
    for spec in L.BUILDINGS:
        if spec[0].startswith("H") or spec[0] in TRECHO:
            continue
        BO.house(mb, spec)
    for nm in ("Sudoeste", "OesteAlta"):
        DL.plan_stair(mb, nm)
    BO.torii(mb, L.SHRINE_TORII[0], L.SHRINE_TORII[1], P, 0.0, 8.0, 9.0, "OP_CapTorii", 0.6)
    mb.finish()
    mp = MB("OP_Cap_Streets", "05_CAPITAL", rng, detail="far", floor=-999)
    cut = [(STREET_RECT[0] - 0.1, STREET_RECT[1] - 0.8, STREET_RECT[2] + 0.1, STREET_RECT[3]), (-15.3, 100.0, 15.3, 121.0)]
    for i, (pts, w, z) in enumerate(L.STREETS):
        if i == 0:
            continue
        pieces = [ccw(L.ribbon(pts, w / 2))]
        for r in cut:
            nxt = []
            for p in pieces:
                nxt += L.subtract_rect(p, r)
            pieces = nxt
        for p in pieces:
            mp.prism(ccw(p), z - 0.2, z + 0.12, "Stone_OP_Path")
    mp.finish()


CAMS = {
    # altura do jogador (olho +5,5) e closes do trecho
    "CAM_OP_M2_Rua_Chegada": ((0.0, 47.0, T1 + 5.65), (0.0, 140.0, P + 9.0), 22),
    "CAM_OP_M2_Rua_LojaC1": ((-4.0, 64.0, T1 + 5.65), (-16.0, 55.0, T1 + 6.5), 22),
    "CAM_OP_M2_Rua_LojaC6": ((4.0, 62.0, T1 + 5.65), (16.0, 72.0, T1 + 7.5), 22),
    "CAM_OP_M2_Rua_LojaC2": ((6.0, 80.0, T1 + 5.65), (-17.0, 73.0, T1 + 8.0), 22),
    "CAM_OP_M2_Rua_LojaC5": ((-5.0, 44.0, T1 + 5.65), (16.0, 53.0, T1 + 8.0), 22),
    "CAM_OP_M2_Escadaria": ((3.0, 98.0, T1 + 5.65), (0.0, 135.0, P + 5.0), 22),
    "CAM_OP_M2_Praca_Volta": ((6.0, 140.0, P + 5.65), (0.0, 60.0, T1 + 4.0), 22),
    "CAM_OP_M2_Praca_Borda": ((44.0, 132.0, P + 5.65), (-10.0, 119.0, P + 2.0), 24),
    "CAM_OP_M2_Arrimo_Viela": ((40.0, 108.0, T1 + 5.65), (6.0, 120.0, P + 1.0), 22),
    "CAM_OP_M2_Emblema": ((0.0, 194.0, P + 12.0), (0.0, 214.0, P), 26),
    "CAM_OP_M2_Trecho_Alto": ((62.0, 18.0, 150.0), (0.0, 112.0, 92.0), 24),
    "CAM_OP_M2_Trecho_Oeste": ((-70.0, 70.0, 120.0), (6.0, 92.0, 96.0), 24),
}


def _cams():
    for n, (loc, tgt, lens) in CAMS.items():
        DL.camera(n, loc, tgt, lens)


def build():
    if bpy.data.objects.get(SENTINEL):
        return
    n = _street()
    _shops()
    _lamps_and_stair()
    _blockout_rest()
    _cams()
    print("op_m2_trecho: rua %d lajes, lojas %s" % (n, ",".join(TRECHO)))


# ================================================================== PRACA: faixa sul + emblema + provisorio
def strip_poly():
    """faixa sul pavimentada (ccw, local): borda sul na linha do P_BASE (y 118), chanfros como a PLAZA, ate y 170"""
    return ccw([(-64.0, 118.0), (64.0, 118.0), (96.0, 124.0), (112.0, 140.0), (115.73, 170.0), (-115.73, 170.0),
                (-110.0, 142.0), (-92.0, 126.0)])


# bordas da faixa que caem para o T1 (arrimo + mureta): leste em polilinha (P_BASE), oeste reta (P_BASE y 118)
EDGE_E = [(15.25, 118.0), (64.0, 118.0), (96.0, 124.0), (112.0, 140.0), (116.0, 170.0)]
EDGE_W = [(-120.0, 118.0), (-64.0, 118.0), (-15.25, 118.0)]


def _seg_frames(pts, inset):
    """para cada segmento da borda (praca a ESQUERDA do sentido): (meio deslocado 'inset' para dentro, angulo do
    Frame com +y local = para FORA, comprimento, normal de fora)"""
    out = []
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        nx, ny = dy / ln, -dx / ln
        mx, my = (a[0] + b[0]) / 2 - nx * inset, (a[1] + b[1]) / 2 - ny * inset
        out.append(((mx, my), math.atan2(ny, nx) - math.pi / 2, ln, (nx, ny)))
    return out


def _pave_strip(mb):
    S = strip_poly()
    pieces = [ccw(p) for p in L.subtract_rect(S, (-15.3, 117.0, 15.3, 119.8))]
    zt, zb = P + Z_OFF, P - 0.3
    n = 0

    def pv(x0, x1, y0, y1, rows, m, along="x", key="f", mats=None, bond=0.5):
        k = 0
        for i, reg in enumerate(pieces):
            k += K.pave(mb, reg, x0, x1, y0, y1, rows, m, zt, zb, along=along, bond=bond, key="%s%d" % (key, i),
                        mats=mats)
        return k
    n += pv(-120.0, 120.0, 118.0, 121.4, ((3.4,), 3.4, 5.0), K.STP, key="borda", mats=[(K.STP, 4), (K.ST, 1)])
    n += pv(-8.0, 8.0, 121.4, STRIP_Y1, ((3.0,), 3.2, 4.8), K.STP, key="eixo", mats=[(K.STP, 5), (K.STZ, 1)])
    XB = (45.4, 46.6)
    YB = (145.4, 146.6)
    for s in (-1, 1):
        lo = lambda a, b: (min(s * a, s * b), max(s * a, s * b))
        xa, xb = lo(8.0, 9.2)
        n += pv(xa, xb, 121.4, STRIP_Y1, ((1.2,), 3.2, 4.8), K.ST, "y", "guia%d" % s)
        for a, b in ((XB[0], XB[1]),):
            xa, xb = lo(a, b)
            n += pv(xa, xb, 121.4, STRIP_Y1, ((1.2,), 3.4, 5.0), K.ST, "y", "fx%d%d" % (s, int(a)))
        for a, b in ((YB[0], YB[1]),):
            xa, xb = lo(9.2, 120.0)
            n += pv(xa, xb, a, b, ((1.2,), 3.4, 5.0), K.ST, "x", "fy%d%d" % (s, int(a)))
        xs = [(9.2, XB[0]), (XB[1], 120.0)]
        ys = [(121.4, YB[0]), (YB[1], STRIP_Y1)]
        for xi, (a, b) in enumerate(xs):
            for yi, (c, d) in enumerate(ys):
                xa, xb = lo(a, b)
                x0 = xa if s > 0 else xb                    # campos alinhados a partir do eixo (simetria)
                if s > 0:
                    n += pv(xa, xb, c, d, ((QS,), QS, QS), K.STZ, "x", "c%d%d%d" % (s, xi, yi), bond=0.0)
                else:
                    # do lado oeste a fiada comeca no eixo: espelha usando a mesma sequencia (lajes de 6 a partir de -a)
                    m = int((b - a) // QS)
                    edges = [-a - QS * j for j in range(m + 1)]
                    if -b < edges[-1] - 0.6:
                        edges.append(-b)
                    else:
                        edges[-1] = -b
                    for u0, u1 in zip(edges[1:], edges[:-1]):
                        n += pv(u0, u1, c, d, ((QS,), 30.0, 30.0), K.STZ, "x", "c%d%d%d%d" % (s, xi, yi, int(u0)),
                                bond=0.0)
    return n


def _emblem(mb, cx, cy):
    """EMBLEMA REBAIXADO: quadro de lajes (circulo r 13 -> quadrado 30 x 30), anel externo de incrustacao (r 11,2-13),
    anel de pedra da praca (9,4-11,2), 8 petalas de incrustacao alternando com 8 fundos (2,2-9,4) e miolo de
    incrustacao (r 2,2). Incrustacao com topo 0,07 ABAIXO do piso e chanfro 0,05 (rebaixo + junta); tudo emenda
    pelas mesmas cordas (grade angular de 32): sem fresta. Nada acima de piso + 0,15."""
    zt, zi, zb = P + Z_OFF, P + Z_OFF - 0.07, P - 0.3
    G = [2 * math.pi * k / 32 for k in range(32)]
    pol = lambda r, a: (cx + r * math.cos(a), cy + r * math.sin(a))
    R0, R1, R2, R3 = 2.2, 9.4, 11.2, 13.0
    K.slab_poly(mb, ccw([pol(R0, a) for a in G]), zb, zi, 0.05, K.STI)
    rs = [2.2, 3.4, 4.6, 5.8, 7.0, 8.2, 9.4]
    wfun = lambda r: 0.3 * math.sin(math.pi * (r - R0) / (R1 - R0)) ** 0.8
    for k in range(8):
        th = k * math.pi / 4
        petal = [pol(r, th - wfun(r)) for r in rs] + [pol(r, th + wfun(r)) for r in reversed(rs[1:-1])]
        K.slab_poly(mb, ccw(petal), zb, zi, 0.05, K.STI)
        arc_in = [pol(R0, G[4 * k + j]) for j in range(5)] if k < 7 else [pol(R0, G[28 + j]) for j in range(4)] + [pol(R0, 0.0)]
        nxt = th + math.pi / 4
        arc_out = [pol(R1, a) for a in ([G[4 * k + j] for j in range(5)] if k < 7 else [G[28 + j] for j in range(4)] + [0.0])]
        bg = arc_in + [pol(r, nxt - wfun(r)) for r in rs[1:-1]] + list(reversed(arc_out)) + \
            [pol(r, th + wfun(r)) for r in reversed(rs[1:-1])]
        K.slab_poly(mb, ccw(bg), zb, zt, 0.05, K.STZ)
    for j in range(16):                                         # anel de pedra e anel de incrustacao (desencontrados)
        a3 = [G[(2 * j + i) % 32] if (2 * j + i) < 32 else G[(2 * j + i) % 32] + 2 * math.pi for i in range(3)]
        K.slab_poly(mb, ccw([pol(R1, a) for a in a3] + [pol(R2, a) for a in reversed(a3)]), zb, zt, 0.05, K.STZ)
        b3 = [G[(2 * j + 1 + i) % 32] + (2 * math.pi if 2 * j + 1 + i >= 32 else 0.0) for i in range(3)]
        K.slab_poly(mb, ccw([pol(R2, a) for a in b3] + [pol(R3, a) for a in reversed(b3)]), zb, zi, 0.05, K.STI)
    sq = lambda a: (cx + EMBLEM_SQ / max(abs(math.cos(a)), abs(math.sin(a))) * math.cos(a),
                    cy + EMBLEM_SQ / max(abs(math.cos(a)), abs(math.sin(a))) * math.sin(a))
    for k in range(8):                                          # quadro: circulo -> quadrado
        a5 = [G[(4 * k + j) % 32] + (2 * math.pi if 4 * k + j >= 32 else 0.0) for j in range(5)]
        K.slab_poly(mb, ccw([pol(R3, a) for a in a5] + [sq(a5[-1]), sq(a5[0])]), zb, zt, 0.07, K.STP)


def _praca_props(mb):
    """mureta + arrimo da borda que cai para a rua, toro e estandartes da chegada, estandartes dos cantos, lanternas
    do norte"""
    zt = P + Z_OFF
    ma = MB("OP_Ter_M2_Arrimo", "02_TERRAIN", random.Random(301), detail="hero")
    for side, pts in (("E", EDGE_E), ("W", EDGE_W)):
        for i, ((mx, my), ang, ln, nrm) in enumerate(_seg_frames(pts, 0.0)):
            h = zt - T1
            paved = not (side == "W" and i == 0)               # oeste alem de x -64: grama da praca (sem lajes)
            if paved:                                          # sob as lajes da faixa: topo escondido, face 0,14 a frente
                K.retaining_wall(ma, Frame(mx, my, zt, ang), ln + 1.2, h, 6.0, key="rw%s%d" % (side, i), cap=False,
                                 top=-0.16, face_off=0.14, core_lift=0.15)
            else:                                              # capa propria 0,15 acima da pele de grama
                K.retaining_wall(ma, Frame(mx, my, zt, ang), ln + 1.2, h, 6.0, key="rw%s%d" % (side, i),
                                 core_lift=0.15)              # M6b item 22: fundo do miolo 0,27 acima do das pedras
    ma.finish()
    for side, pts in (("E", [(15.6, 118.0)] + EDGE_E[1:]), ("W", [(-118.0, 118.0), (-15.6, 118.0)])):
        for i, ((mx, my), ang, ln, nrm) in enumerate(_seg_frames(pts, 0.95)):
            F = Frame(mx, my, zt, ang)                          # mureta ao longo do segmento (x local = segmento)
            K.parapet(mb, F, ln + 0.6, 2.3, 1.3, key="mu%s%d" % (side, i))
            col_box("OP_PlzMureta", (ln + 0.6, 1.6, 2.9), (mx, my, P + 1.45), (0, 0, ang))
    for i, s in enumerate((-1, 1)):
        x = s * 19.5
        K.toro(mb, Frame(x, 122.6, zt - 0.05, 0.0), 1.0, "L_OPProp_Toro_M2_%d" % i, 35.0)
        col_box("OP_PropToro", (2.8, 2.8, 7.6), (x, 122.6, P + 3.8))
        bx_ = s * 24.5
        K.banner(mb, Frame(bx_, 121.0, zt - 0.05, 0.0), 16.0, K.CWHITE, K.INDIGO, 2.6, s)
        col_box("OP_PropBanner", (1.9, 1.9, 16.0), (bx_, 121.0, P + 8.0))
    for (x, y) in L.BANNERS:                                    # estandartes dos cantos (fora da zona + 8)
        ang = math.atan2(L.MINE_C[1] - y, L.MINE_C[0] - x) - math.pi / 2
        K.banner(mb, Frame(x, y, zt - 0.05, ang), 18.0, K.CWHITE, K.INDIGO, 2.8, 1)
        col_box("OP_PropBanner", (1.9, 1.9, 18.0), (x, y, P + 9.0))
    for i, x in enumerate((-21.25, 21.25)):                     # lanternas do norte (pe do adro)
        K.lantern_box_post(mb, Frame(x, 306.0, zt - 0.05, 0.0), 7.6, "L_OPProp_Lamp_PracaN_%d" % i, 35.0)
        col_box("OP_PropLamp", (1.1, 1.1, 7.6), (x, 306.0, P + 3.8))


def _fallback_north():
    """piso PROVISORIO da praca fora da faixa sul (dono futuro: op_plaza/op_terrain no M4): 1 prisma liso no topo do
    trecho (P + 0,15), com o quadro do emblema recortado"""
    mf = MB("OP_Plz_M2_PisoProvisorio", "03_PLAZA", random.Random(302), detail="far", floor=-999)
    north = L.clip_rect(ccw(L.PLAZA), (-200.0, STRIP_Y1, 200.0, 400.0))
    ex, ey = L.EMBLEM_C
    for p in L.subtract_rect(north, (ex - EMBLEM_SQ, ey - EMBLEM_SQ, ex + EMBLEM_SQ, ey + EMBLEM_SQ)):
        mf.prism(ccw(p), P - 0.3, P + Z_OFF, "Stone_OP_Plaza")
    mf.finish()


def build_praca():
    if bpy.data.objects.get(SENTINEL_P):
        return
    mb = MB(SENTINEL_P, "03_PLAZA", random.Random(300), detail="hero", floor=-999)
    n = _pave_strip(mb)
    _emblem(mb, *L.EMBLEM_C)                                 # emblema no mesmo MB das lajes (mesmas pedras)
    mb.finish()
    mp = MB("OP_Plz_M2_Borda", "03_PLAZA", random.Random(304), detail="hero")
    _praca_props(mp)
    K.cull_hidden(mp)                                        # M6b
    mp.finish(recalc=False)                                  # M6c
    _fallback_north()
    print("op_m2_praca: faixa sul %d lajes + emblema + borda" % n)
