# op_capital.py - M4 da Ilha 5 (ONE PIECE / WANO): CAPITAL inteira (PLANO_OP secoes 4.3/4.4, 6, 8, 9; PROMPT_USUARIO
# 4, 5, 10, 15, 16). Zona "capital" do build_op (ZONE_MODULES["capital"] = ["op_capital"]). Prefixo OP_Cap_, colecao
# 05_CAPITAL. Luzes so NightOnly (L_OPProp_*, L_OPCap_Win_*) + 1 luz de interior de dia (L_OPCap_Int_Cha).
#
# O TRECHO M2 (op_m2_trecho: rua de chegada, lojas C1 C2 C5 C6, postes, escadaria Praca) e chamado DAQUI sem mudar
# nada (as mesmas funcoes, mesmos nomes OP_Cap_M2_*): o op_m2_trecho continua sendo o dono dele e nao regride. So o
# _blockout_rest() do trecho (o resto da capital em blockout) deixa de rodar: este modulo o substitui.
#
# FAMILIAS (todas com o op_kit; pecas novas so aqui):
#   A  kit inteiro: C7 (K.house ESQ lod 1, esquina-marco 3 pisos vermelha), CHA (K.house lod 0: casa de cha do
#      quarteirao oeste com INTERIOR REAL: piso, forro, balcao, prateleiras, estrado de tatami, mesa, almofadas,
#      chochin, luz de dia L_OPCap_Int_Cha), haiden do santuario (K.pavilion lod 1). Pavilhao do recanto = pav_lo.
#      PONTES VERMELHAS do canal oeste (y 182 / 252; visual daqui, colisao plana do op_col a 92,2; tabuleiro >= 92,66
#      sobre a capa do canal 92,5 - pedido do op_water).
#   B  "meia" (mid, inclui C4): frente do terreo com K.facade do kit (lojas, trelica, noren, porta) + laterais/fundos/pisos de
#      cima e TELHADO LEVE deste modulo (mesma linguagem: reboco recuado entre pilares, rodape de tabuas, viga de
#      beiral que passa do canto, telha em canais, beiral grosso, sori, espigoes, cumeeira com onigawara).
#   C  "fundo" (far): o mesmo corpo leve em todas as faces (janelas de papel com moldura, porta de correr, noren).
#   O telhado e ~60% do custo: o leve usa 3 linhas de grade na placa e canais a cada 3,4 (kit: 2,1-3,0).
# SETORES (planta do PLANO_OP 4.3; nada em intervalos iguais, cor POR CONJUNTO):
#   rua de chegada  C4 + C7 coladas no trecho (fecham a rua nas 2 vielas)
#   quarteirao O    fileira que encara a praca (W1 esquina verde, W2 loja, W2b casa recuada, RECANTO com pavilhao,
#                   W4 esquina, CHA com interior, W5 casa verde) + fundos para o cais do canal; alem do canal: X1..X3
#                   (casas de frente para o canal, patamares nas 2 pontes)
#   bairro do canal casas baixas dos 2 lados da viela do canal, MIRANTE na falesia, MOINHO da roda d'agua
#   terraco alto    mansoes de telhado verde (U1 sobre o arrimo, U2), casas e pavilhao de fundo
#   NE              SANTUARIO (torii pequeno, sando, 2 toro, 2 nobori, haiden aberto, honden de laca) + casas de
#                   telhado avermelhado
#   rua alta porto  bloco leste: beco N-S atras de C5-C7, travessa L-O ate o MIRANTE do porto, casas viradas para a
#                   viela leste (rota chegada -> summon) e para a travessa
# NAO e daqui: lajeado do terraco do summon (op_summon, x 116..206 / y 150..264), porto/H1-H5 (op_harbor), praca e
#   borda (op_plaza), canais/pontes do canal/roda (op_water), arvores (op_veg: ver VEG_SPOTS), terreno (op_terrain).
# COLISAO: corpo de cada casa (COL_OP_CapHouse<nome>; CAM_AREAS -> export_op), pavilhoes (estrado + guardas),
#   CHA (piso + paredes: da para entrar), postes/toro/estandartes/bancos. Pisos e escadas da planta sao do op_col.
# CAMERAS: CAM_OP_M4Cap_* (fora do export).
import math, random
import bpy
import op_lib as DL
from op_lib import MB, col_box, Frame, ccw, light
import op_layout as L
import op_kit as K
import op_m2_trecho as TR

T1, P, W3Z = L.T1, L.P, L.W3
Z_OFF = 0.15
COLL = "05_CAPITAL"
WD, WM, LAC, GOLD = K.WD, K.WM, K.LAC, K.GOLD
PL, PLW, PLS = K.PL, K.PLW, K.PLS
RB, RG, RRED, RR = K.RB, K.RG, K.RRED, K.RR
ST, STD, STP, STZ = K.ST, K.STD, K.STP, K.STZ
LIT = K.LIT
INDIGO, CRED, CWHITE = K.INDIGO, K.CRED, K.CWHITE
DIRT = "Dirt_OP"
STRAW = "Cloth_OP_Straw"
CP = K.CP
DH = 7.6                                      # porta das casas leves (vao 7,6; kit 8,4)
RIB3 = [(-0.3, -0.1), (0.0, 0.24), (0.3, -0.1)]
HIP4 = [(-0.5, -0.18), (-0.34, 0.36), (0.34, 0.36), (0.5, -0.18)]
SUMMON_RECT = (116.0, 150.0, 206.0, 264.0)    # lajeado do op_summon
TRECHO_RECT = (-17.0, 40.0, 17.0, 121.0)      # rua do trecho + escadaria Praca
CAM_AREAS = []                                 # areas de colisao das casas (export_op -> CAM_COL_AREAS)
VEG_SPOTS = []                                 # (x, y, z, tipo, nota) para o op_veg
_h = K._h01


def sub(F, x=0.0, y=0.0, z=0.0, ang=0.0):
    return K.sub(F, x, y, z, ang)


def bb(mb, F, x0, x1, y0, y1, z0, z1, m, bev=0.0):
    K.bb(mb, F, x0, x1, y0, y1, z0, z1, m, bev)


# ================================================================== PECAS LEVES (familias B e C)
# lite = familia C (fundo): canais a cada 4,4 so nas aguas longas, onigawara simples, kumiko 1 x 1, rodape de tabuas
# so na frente. A silhueta (beiral grosso, sori, espigoes, empena, cumeeira) e a MESMA da familia B.
SHIELD = [(-1.2, -0.7), (1.2, -0.7), (1.25, 0.6), (0.7, 1.6), (0.0, 1.95), (-0.7, 1.6), (-1.25, 0.6)]


def _win_lo(mb, Ff, s, z, w, hh, lit, lite=False):
    """janela de papel com moldura (peitoril com pingadeira, verga, ombreiras) e kumiko: papel 0,14 a frente do
    reboco, kumiko 0,14 a frente do papel"""
    x0, x1 = s - w / 2, s + w / 2
    bb(mb, Ff, x0 - 0.3, x1 + 0.3, -0.3, 0.16, z - 0.28, z, WD)
    bb(mb, Ff, x0 - 0.3, x1 + 0.3, -0.3, 0.06, z + hh, z + hh + 0.3, WD)
    bb(mb, Ff, x0 - 0.3, x0, -0.3, 0.04, z, z + hh, WD)
    bb(mb, Ff, x1, x1 + 0.3, -0.3, 0.04, z, z + hh, WD)
    bb(mb, Ff, x0, x1, -0.16, -0.08, z, z + hh, LIT if lit else PL)
    nb = 2 if lite else max(2, int(round(w / 1.05)))
    for i in range(1, nb):
        x = x0 + w * i / nb
        bb(mb, Ff, x - 0.07, x + 0.07, -0.08, 0.06, z, z + hh, WD)
    bb(mb, Ff, x0, x1, -0.08, 0.06, z + hh * 0.5 - 0.06, z + hh * 0.5 + 0.06, WD)


def _door_lo(mb, Ff, s, w, z0, dh, noren=None, lit=False, lite=False):
    """porta de correr: caixilho, soleira, 2 folhas de tabua com papel em cima (0,14 a frente), montante, noren"""
    x0, x1 = s - w / 2, s + w / 2
    bb(mb, Ff, x0 - 0.3, x0, -0.9, 0.04, z0 - 0.25, z0 + dh + 0.45, WD)
    bb(mb, Ff, x1, x1 + 0.3, -0.9, 0.04, z0 - 0.25, z0 + dh + 0.45, WD)
    bb(mb, Ff, x0, x1, -0.9, 0.04, z0 + dh, z0 + dh + 0.45, WD)
    bb(mb, Ff, x0 - 0.3, x1 + 0.3, -0.95, 0.2, z0 - 0.25, z0, WD)
    bb(mb, Ff, x0, x1, -0.78, -0.62, z0, z0 + dh, WM)
    zm = z0 + dh * 0.4
    pm = LIT if lit else PL
    bb(mb, Ff, x0 + 0.3, s - 0.18, -0.62, -0.48, zm, z0 + dh - 0.35, pm)
    bb(mb, Ff, s + 0.18, x1 - 0.3, -0.62, -0.48, zm, z0 + dh - 0.35, pm)
    bb(mb, Ff, s - 0.18, s + 0.18, -0.62, -0.34, z0, z0 + dh, WD)
    if not lite:
        for xa, xb in ((x0 + 0.3, s - 0.18), (s + 0.18, x1 - 0.3)):
            xm = (xa + xb) / 2
            bb(mb, Ff, xm - 0.06, xm + 0.06, -0.48, -0.34, zm, z0 + dh - 0.35, WD)
    if noren:
        K.noren_cloth(mb, Ff, x0, x1, z0 + dh - 0.12, min(3.0, dh * 0.4), noren)


def wall_lo(mb, Ff, L_, h, opens, pl, ground=True, full=True, boards=True, lite=False):
    """parede leve (mesma construcao do K.facade): soleira (so no terreo), viga de beiral que passa do canto nas
    faces 'full', pilares intermediarios, REBOCO recuado 0,22 entre pilares; no terreo rodape de tabuas + travessa
    escura. opens = [dict(t='win'|'door', s, w, h, z, lit, noren)]"""
    xi0, xi1 = -L_ / 2 + CP, L_ / 2 - CP
    z0 = 0.7 if ground else 0.0
    zt = h - 1.0
    if ground:
        bb(mb, Ff, -L_ / 2 if full else xi0, L_ / 2 if full else xi1, -0.95, 0.06, 0.0, 0.7, WD)
    ke = (-L_ / 2 - 0.9, L_ / 2 + 0.9) if full else (xi0, xi1)
    bb(mb, Ff, ke[0], ke[1], -0.95, 0.15, zt, h, WD)
    holes = []
    for o in opens:
        if o["t"] == "door":
            dh = o.get("h", DH)
            holes.append((o["s"] - o["w"] / 2 - 0.3, o["s"] + o["w"] / 2 + 0.3, z0 - 0.3, z0 + dh + 0.45))
            _door_lo(mb, Ff, o["s"], o["w"], z0, dh, o.get("noren"), o.get("lit", False), lite)
        else:
            _win_lo(mb, Ff, o["s"], o["z"], o["w"], o["h"], o.get("lit", True), lite)
    span = xi1 - xi0
    n = max(1, int(round(span / (6.0 if lite else 5.2))))
    for i in range(1, n):
        x = xi0 + span * i / n
        if any(a - 0.45 < x < b + 0.45 for a, b, _, _ in holes):
            continue
        if any(abs(x - o["s"]) < o["w"] / 2 + 0.75 for o in opens if o["t"] == "win"):
            continue
        bb(mb, Ff, x - 0.4, x + 0.4, -0.9, 0.0, z0, zt, WD)
    if ground and boards:
        K.panel(mb, Ff, xi0, xi1, z0, 2.4, -0.78, -0.2, holes, WM)
        K.panel(mb, Ff, xi0, xi1, 2.4, 2.65, -0.62, 0.02, holes, WD)
        K.panel(mb, Ff, xi0, xi1, 2.65, zt + 0.05, -0.8, -0.22, holes, pl)
    else:
        K.panel(mb, Ff, xi0, xi1, z0, zt + 0.05, -0.8, -0.22, holes, pl)


def auto_opens(L_, key, k, h, seed, lit_p=0.5, noren=INDIGO, door=True, lite=False):
    """vaos automaticos: frente do terreo = porta + janelas; fundos 1-2 janelas; laterais 1 janela se couber;
    pisos de cima = fileira de janelas. Posicoes sorteadas (sem intervalos iguais de casa para casa)."""
    out = []
    lit = lambda i: _h(seed, key, k, i, "l") < lit_p
    span = L_ - 2 * CP
    if k == 0:
        if key == "F":
            ds = (_h(seed, "d") - 0.5) * max(0.0, span - 10.0) * 0.6 if door else None
            if door:
                out.append(dict(t="door", s=ds, w=5.0, noren=noren if _h(seed, "n") < (0.45 if lite else 0.7) else None,
                                lit=lit(0)))
            for sgn in (-1, 1):
                if door:
                    a, b = (ds + 3.2, L_ / 2 - CP - 0.6) if sgn > 0 else (-L_ / 2 + CP + 0.6, ds - 3.2)
                else:
                    a, b = (0.6, L_ / 2 - CP - 0.6) if sgn > 0 else (-L_ / 2 + CP + 0.6, -0.6)
                if b - a >= 3.4:
                    w = min(5.2, b - a - 0.8)
                    out.append(dict(t="win", s=(a + b) / 2, w=w, h=3.2, z=3.3, lit=lit(sgn)))
        elif key == "B":
            n = 1 if (span < 14 or lite) else 2
            for i in range(n):
                s = -span / 2 + span * (i + 0.5) / n + (_h(seed, "b", i) - 0.5) * 2.0
                out.append(dict(t="win", s=s, w=3.0, h=2.8, z=4.2, lit=lit(10 + i)))
        else:
            if span >= 10:
                s = (_h(seed, key, "s") - 0.5) * (span - 6.0) * 0.5
                out.append(dict(t="win", s=s, w=2.8, h=2.8, z=4.4, lit=lit(20)))
    else:
        if key in "FB":
            n = max(1, int((span + 1.0) / (8.0 if lite else 6.5)))
            for i in range(n):
                s = -span / 2 + span * (i + 0.5) / n
                out.append(dict(t="win", s=s, w=min(3.8, span / n - 1.6), h=min(2.8, h - 3.4), z=1.5, lit=lit(30 + i)))
        elif span >= (16 if lite else 12):
            out.append(dict(t="win", s=0.0, w=2.8, h=min(2.6, h - 3.4), z=1.6, lit=lit(40)))
    return out


def pent_lo(mb, Ff, L_, depth, z_top, m=RB, pitch=0.42, tv=0.4, sp=1.9, brackets=True):
    """hisashi leve: placa com espessura, canais, testeira, frechal e misulas. Ff na face da parede"""
    X = L_ / 2
    zf = lambda x, y: z_top - pitch * y + 0.4 * min(1.0, abs(x) / X) ** 3 * min(1.0, max(0.0, y) / depth) ** 3
    K.sheet(mb, Ff, [(-X, depth), (X, depth), (X, -0.35), (-X, -0.35)], zf, tv, max(2, int(L_ / 6.0)), [0.0, 1.0], m)
    for x in K.even(-X + 0.35, X - 0.35, sp):
        K.sweep(mb, Ff, [(x, depth + 0.1, zf(x, depth)), (x, 0.2, zf(x, 0.2))], RIB3, m)
    K.strip(mb, Ff, [(x, depth - 0.28, zf(x, depth - 0.28) - tv) for x in (-X + 0.3, 0.0, X - 0.3)], (0, 1, 0),
            -0.15, 0.15, -0.42, 0.05, WD)
    bb(mb, Ff, -X + 0.2, X - 0.2, -0.12, 0.26, z_top - 0.32, z_top + 0.26, WD)
    if brackets:
        zd = zf(0.0, depth - 0.5) - tv - 0.25
        xs = [-X + 0.6, X - 0.6] + ([0.0] if L_ > 14 else [])
        for x in xs:
            K.bracket(mb, Ff, x, -0.1, zd, depth - 0.45, 0.4, 0.8)


def _oni_lo(mb, F, x, zr, sx, s=0.7):
    K.ext(mb, F, [(u * s, zr + v * s) for u, v in SHIELD], "x", x - 0.12 * sx, x + 0.42 * sx * s, RR)


def _ridge_lo(mb, F, x0, x1, zr, pu, gold=False, lite=False):
    hw = 1.05
    poly = [(-hw, zr - pu * hw - 0.05), (0.0, zr - 0.05), (hw, zr - pu * hw - 0.05), (hw, zr + 0.3), (-hw, zr + 0.3)]
    K.ext(mb, F, poly, "x", x0, x1, RR)
    bb(mb, F, x0 + 0.15, x1 - 0.15, -0.78, 0.78, zr + 0.26, zr + 0.62, RR)
    if not lite:
        bb(mb, F, x0 + 0.3, x1 - 0.3, -0.55, 0.55, zr + 0.58, zr + 0.92, RR)
    for sx, xe in ((-1, x0), (1, x1)):
        if lite:
            _oni_lo(mb, F, xe, zr, sx, 0.66)
        else:
            K.onigawara(mb, F, xe, zr, sx, 0.62, False, gold)
    return zr + (0.62 if lite else 0.92)


def roof_lo(mb, F, W, D, h, kind="irimoya", pitch=0.55, over=2.8, lift=1.0, tv=0.5, m=RB, gable=0.62, g_over=1.3,
            sp=None, gable_m=PL, gold=False, lite=False):
    """TELHADO LEVE irimoya / yosemune (cumeeira em x local; gira sozinho se D > W): placas com espessura e sori
    (K.Slope), canais a cada 'sp', capas dos espigoes, testeira, rincao, empena de reboco com tabeira e gegyo,
    cumeeira com onigawara. F na base do ultimo piso, h = topo da viga de beiral."""
    sp = sp or (4.4 if lite else 3.5)
    if kind == "kirizuma":
        return gable_lo(mb, F, W, D, h, pitch, over, 1.6, lift * 0.6, tv, m, gable_m, sp, gold, lite)
    if W < D - 1e-6:
        return roof_lo(mb, sub(F, ang=math.pi / 2), D, W, h, kind, pitch, over, lift, tv, m, gable, g_over, sp, gable_m,
                       gold, lite)
    Xw, Yw = W / 2 + 0.15, D / 2 + 0.15
    Xe, Ye = Xw + over, Yw + over
    zw = h + tv + 0.06
    irim = kind == "irimoya"
    yb = gable * Yw if irim else 0.45
    S = K.Slope(Xw, Yw, zw, pitch, pitch * 0.5, Xe, Ye, lift, pitch * 1.5 if irim else pitch, Yw - yb)
    k = Xw - Yw
    xg = k + yb
    go = g_over if irim else 0.0
    zr = S.zy(0.0, 0.0)
    zb = S.zy(xg, yb)
    dv = 8.0 if lite else 5.5
    for ik, Fk in enumerate((F, sub(F, ang=math.pi))):
        tw = over / (Ye - yb)
        K.sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (xg, yb), (-xg, yb)], S.zy, tv, max(2, int(2 * Xe / dv)), [0.0, tw, 1.0], m)
        if irim and yb > 0.05:
            K.sheet(mb, Fk, [(-xg - go, yb), (xg + go, yb), (xg + go, 0.0), (-xg - go, 0.0)], S.zy, tv, 2, [0.0, 1.0], m)
        twe = over / max(0.1, Xe - xg)
        K.sheet(mb, Fk, [(Xe, -Ye), (Xe, Ye), (xg, yb), (xg, -yb)], S.zx, tv, max(2, int(2 * Ye / dv)),
                [0.0, min(0.99, twe), 1.0], m)
        for x in K.even(-Xe + 0.4, Xe - 0.4, sp):
            ax = abs(x)
            if ax <= xg:
                line = [(x, Ye + 0.12), (x, Yw), (x, max(yb, 0.45))]
            else:
                ye = ax - k + 0.45
                if ye >= Ye - 0.7:
                    continue
                line = [(x, Ye + 0.12)] + ([(x, Yw)] if ye < Yw - 0.3 else []) + [(x, ye)]
            K.sweep(mb, Fk, [(px, py, S.zy(px, py)) for px, py in line], RIB3, m)
        if not lite:
            for y in K.even(-Ye + 0.4, Ye - 0.4, sp):
                ay = abs(y)
                xe = (xg + 0.45) if (irim and ay <= yb - 0.5) else (ay + k + 0.45)
                if xe < Xe - 0.7:
                    pts = [(Xe + 0.12, y)] + ([(Xw, y)] if xe < Xw - 0.3 else []) + [(xe, y)]
                    K.sweep(mb, Fk, [(px, py, S.zx(px, py)) for px, py in pts], RIB3, m)
        for sy in (1, -1):
            pts = [(Xe + 0.5, sy * (Ye + 0.5), S.zy(Xe, Ye) + 0.55)] + \
                  ([] if lite else [(Xe, sy * Ye, S.zy(Xe, Ye) + 0.04)]) + \
                  [(Xw, sy * Yw, S.zy(Xw, Yw) + 0.02), (xg, sy * yb, S.zy(xg, yb))]
            K.sweep(mb, Fk, pts, HIP4, RR)
            if not lite:
                K.beam(mb, Fk, (Xw - 0.8, sy * (Yw - 0.8), zw - tv - 0.75),
                       (Xe + 0.22, sy * (Ye + 0.22), S.zy(Xe, Ye) - tv - 0.32), 0.6, 0.62, WD)
        K._fascia(mb, Fk, lambda t: ((-Xe + 0.42) + (2 * Xe - 0.84) * t, Ye - 0.34), 10, (0, 1, 0), S.zy, tv, lod=1)
        if not lite:
            K._fascia(mb, Fk, lambda t: (Xe - 0.34, (-Ye + 0.42) + (2 * Ye - 0.84) * t), 8, (1, 0, 0), S.zx, tv, lod=1)
        if irim and yb > 1.0:
            yf_ = yb - 0.55
            bb(mb, Fk, xg - 0.62, xg + 0.36, -yf_, yf_, zb - 0.22, zb + 0.22, RR)
            top = lambda y: S.zy(xg, y) - tv - 0.05
            y1 = yb - (tv + 0.12) / S.pu
            if y1 > 0.4:
                ys = [y1, y1 * 0.5, 0.0, -y1 * 0.5, -y1]
                poly = [(-y1, zb - 0.05), (y1, zb - 0.05)] + [(y, top(y)) for y in ys]
                K.ext(mb, Fk, poly, "x", xg - 0.45, xg - 0.25, gable_m)
                bb(mb, Fk, xg - 0.27, xg - 0.09, -y1 * 0.55, y1 * 0.55, zb + 0.15, zb + 0.55, WD)
            xh = xg + go - 0.3
            ye = 0.0
            for i in range(1, 60):
                y = yb * i / 60
                if S.zy(xh, y) - tv - 0.7 < S.zx(xh - 0.2, y) + 0.4:
                    break
                ye = y
            if ye > 0.5:
                nseg = 2 if lite else 3
                for sy in (1, -1):
                    K._hafu(mb, Fk, xh, [sy * ye * i / nseg for i in range(nseg + 1)], S.zy, tv, 0.7)
                K._gegyo(mb, Fk, xh, S.zy(xh, 0.0) - tv - 0.7, 1, WD, 0.9, gold)
    rt = _ridge_lo(mb, F, -(xg + go + 0.2), xg + go + 0.2, zr, S.pu, gold, lite)
    return dict(top=rt + 1.6, zr=zr, eave_z=S.zy(0.0, Ye) - tv - 0.6)


def gable_lo(mb, F, W, D, h, pitch=0.62, over=2.6, g_over=1.6, lift=0.6, tv=0.5, m=RB, gable_m=PL, sp=3.5, gold=False,
             lite=False):
    """KIRIZUMA leve (duas aguas, cumeeira em x local): placas, canais, testeira, empena de reboco com tabuas,
    tabeira (hafu) e gegyo, cumeeira com onigawara"""
    Xw, Yw = W / 2, D / 2 + 0.15
    Xe, Ye = Xw + g_over, Yw + over
    zw = h + tv + 0.06
    S = K.Slope(Xw, Yw, zw, pitch, pitch * 0.5, Xe, Ye, lift)
    zr = S.zy(0.0, 0.0)
    tw = over / Ye
    for Fk in (F, sub(F, ang=math.pi)):
        K.sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (Xe, 0.0), (-Xe, 0.0)], S.zy, tv,
                max(2, int(2 * Xe / (8.0 if lite else 5.5))), [0.0, tw, 1.0], m)
        for x in K.even(-Xe + 0.4, Xe - 0.4, sp):
            K.sweep(mb, Fk, [(px, py, S.zy(px, py)) for px, py in ((x, Ye + 0.12), (x, Yw), (x, 0.45))], RIB3, m)
        K._fascia(mb, Fk, lambda t: ((-Xe + 0.5) + (2 * Xe - 1.0) * t, Ye - 0.3), 8, (0, 1, 0), S.zy, tv, lod=1)
        top = lambda y: S.zy(Xw, y) - tv - 0.05
        ymax = D / 2
        ys = [ymax, ymax * 0.5, 0.0, -ymax * 0.5, -ymax]
        poly = [(-ymax, h - 0.1), (ymax, h - 0.1)] + [(y, top(y)) for y in ys]
        K.ext(mb, Fk, poly, "x", Xw - 0.8, Xw - 0.24, gable_m)
        if not lite:
            for y in K.even(-ymax + 0.6, ymax - 0.6, 1.6):
                t = top(y) - 0.08
                if t > h + 0.8:
                    bb(mb, Fk, Xw - 0.26, Xw - 0.1, y - 0.09, y + 0.09, h + 0.1, t, WD)
        bb(mb, Fk, Xw - 0.3, Xw - 0.06, -ymax + 0.3, ymax - 0.3, h - 0.25, h + 0.15, WD)
        xh = Xe - 0.3
        for sy in (1, -1):
            K._hafu(mb, Fk, xh, [sy * (Ye - 0.05) * u for u in (0.0, Yw / Ye * 0.999, 1.0)], S.zy, tv, 0.9, WD, 0.2)
        K._gegyo(mb, Fk, xh, S.zy(xh, 0.0) - tv - 0.9, 1, WD, 0.9, gold)
    rt = _ridge_lo(mb, F, -(Xe + 0.17), Xe + 0.17, zr, pitch, gold, lite)
    return dict(top=rt + 1.6, zr=zr, eave_z=S.zy(0.0, Ye) - tv - 0.6)


def pav_lo(mb, F, W, D, h=7.4, roof_m=RB, red=False, deck=1.1):
    """PAVILHAO aberto leve (familia pavilhao, versao de recanto): pilares sobre pedras, estrado de tabuas com viga
    de borda, vigas de cabeca, guarda baixa nos 3 lados (aberto na frente +y), degrau de pedra, telhado leve"""
    pm = LAC if red else WD
    xs = [-W / 2 + 0.5, 0.0, W / 2 - 0.5] if W > 11 else [-W / 2 + 0.5, W / 2 - 0.5]
    ys = [-D / 2 + 0.5, D / 2 - 0.5]
    for x in xs:
        for y in ys:
            bb(mb, F, x - 0.75, x + 0.75, y - 0.75, y + 0.75, -0.2, 0.45, ST)
            bb(mb, F, x - 0.42, x + 0.42, y - 0.42, y + 0.42, 0.45, deck + h, pm)
    bb(mb, F, -W / 2 + 0.2, W / 2 - 0.2, -D / 2 + 0.2, D / 2 - 0.2, deck - 0.22, deck, WM)
    bb(mb, F, -W / 2, W / 2, -D / 2, D / 2, deck - 0.75, deck - 0.22, WD)
    for sy in (-1, 1):
        bb(mb, F, -W / 2 - 0.8, W / 2 + 0.8, sy * (D / 2 - 0.5) - 0.4, sy * (D / 2 - 0.5) + 0.4, deck + h - 0.9, deck + h, WD)
    for sx in (-1, 1):
        bb(mb, F, sx * (W / 2 - 0.5) - 0.38, sx * (W / 2 - 0.5) + 0.38, -D / 2 - 0.8, D / 2 + 0.8, deck + h - 0.88,
           deck + h - 0.02, WD)
    rails = [((-W / 2 + 0.5, -D / 2 + 0.5), (W / 2 - 0.5, -D / 2 + 0.5))]
    rails += [((s * (W / 2 - 0.5), -D / 2 + 0.5), (s * (W / 2 - 0.5), D / 2 - 0.5)) for s in (-1, 1)]
    for a, b in rails:
        K.beam(mb, F, (a[0], a[1], deck + 2.6), (b[0], b[1], deck + 2.6), 0.3, 0.3, pm)
        K.beam(mb, F, (a[0], a[1], deck + 1.2), (b[0], b[1], deck + 1.2), 0.22, 0.22, WD)
    K.stone(mb, sub(F, 0.0, D / 2 - 0.2), -2.2, 2.2, -0.3, deck * 0.5, -0.3, 1.5, 1.5, 0.08, STP)
    return roof_lo(mb, sub(F, z=deck), W, D, h, "irimoya", 0.55, 2.6, 1.0, 0.5, roof_m, 0.6, 1.2, 3.5, PL)


# ------------------------------------------------------------------ edificio leve (B e C)
LO_DEF = dict(plinth=("soco", 0.9), plaster=PLW, plaster_up=PL, lit_p=0.45, noren=INDIGO, lite=False,
              roof=dict(kind="irimoya", ridge="x", pitch=0.55, over=2.8, lift=1.0, m=RB), chochin=())


def _faces(Fz, W, D):
    return {"F": (sub(Fz, 0.0, D / 2), W, True), "B": (sub(Fz, 0.0, -D / 2, 0.0, math.pi), W, True),
            "R": (sub(Fz, W / 2, 0.0, 0.0, -math.pi / 2), D, False),
            "L": (sub(Fz, -W / 2, 0.0, 0.0, math.pi / 2), D, False)}


def lo_house(mb, F, spec, seed):
    """edificio leve. spec: W D plinth plaster plaster_up roof floors=[dict(h, setback=(frente, fundos), F/B/L/R =
    'auto' | [vaos] | dict(kit=bays, lod)), pents=(faces com hisashi entre este piso e o de baixo)] front_pent=dict(z,
    depth) (hisashi do terreo), chochin=[(x, z)], lite. Devolve dict(glow, roof)."""
    sp = dict(LO_DEF)
    sp.update(spec)
    W, D = sp["W"], sp["D"]
    lite = sp["lite"]
    pst, ph = sp["plinth"]
    K.foundation(mb, F, W + 0.6, D + 0.6, ph, pst, 1)
    z = ph
    glow = []
    prev = None
    last = None
    rm = sp["roof"].get("m", RB)
    for k, fl in enumerate(sp["floors"]):
        sf, sbk = fl.get("setback", (0.0, 0.0))
        Wk, Dk = W, D - sf - sbk
        cy = (sbk - sf) / 2
        Fk = sub(F, 0.0, cy, z)
        h = fl["h"]
        ground = k == 0
        pl = sp["plaster"] if ground else sp["plaster_up"]
        K.corner_posts(mb, Fk, Wk, Dk, 0.7 if ground else 0.0, h - 1.0, CP, 1)
        for key, (Ff, Lf, full) in _faces(Fk, Wk, Dk).items():
            fs = fl.get(key, "auto")
            if isinstance(fs, dict):
                r = K.facade(mb, Ff, Lf, h, fs["kit"], full, fs.get("door_w", K.DOOR_W), K.DOOR_H if ground else 3.6,
                             fs.get("plaster", pl), True, 0.9, fs.get("lod", 1), fs.get("noren", sp["noren"]), ground,
                             seed * 7 + k * 4 + "FBRL".index(key), ground, 5.2 if ground else 2.2)
                glow += r["glow"]
                continue
            if fs == "auto":
                fs = auto_opens(Lf, key, k, h, seed, sp["lit_p"], sp["noren"], fl.get("door", True), lite)
            wall_lo(mb, Ff, Lf, h, fs, pl, ground, full, (key == "F") or not lite, lite)
            glow += [Ff.p(o["s"], 0.6, o["z"] + o["h"] / 2) for o in fs if o["t"] == "win" and o.get("lit")]
        if k > 0:                                         # viga do piso + hisashi nas faces recuadas
            Wp, Dp, cyp = prev
            bb(mb, Fk, -Wk / 2 - 0.25, Wk / 2 + 0.25, -Dk / 2 - 0.25, Dk / 2 + 0.25, -0.35, 0.3, WD)
            pents = fl.get("pents")
            if pents is None:
                pents = ("F" if sf > 0 else "") + ("B" if sbk > 0 else "")
            for key in pents:
                if key == "F":
                    pent_lo(mb, sub(Fk, 0.0, Dk / 2), Wp + 1.0, sf + 2.0, 1.45, rm, sp=2.4 if lite else 1.9,
                            brackets=not lite)
                elif key == "B":
                    pent_lo(mb, sub(Fk, 0.0, -Dk / 2, 0.0, math.pi), Wp + 1.0, sbk + 2.0, 1.45, rm,
                            sp=2.4 if lite else 1.9, brackets=not lite)
        fp = fl.get("front_pent")
        if fp:
            pent_lo(mb, sub(Fk, 0.0, Dk / 2), Wk + 1.0, fp.get("depth", 2.6), fp.get("z", h - 1.6), rm)
        prev = (Wk, Dk, cy)
        last = (Fk, Wk, Dk, h)
        z += h
    Fk, Wk, Dk, h = last
    rf = dict(LO_DEF["roof"])
    rf.update(sp["roof"])
    gm = sp["plaster_up"] if len(sp["floors"]) > 1 else sp["plaster"]
    Fr, Wr, Dr = (Fk, Wk, Dk) if rf["ridge"] == "x" else (sub(Fk, ang=math.pi / 2), Dk, Wk)
    r = roof_lo(mb, Fr, Wr, Dr, h, rf["kind"], rf["pitch"], rf["over"], rf["lift"], 0.5, rm, rf.get("gable", 0.62),
                1.3, rf.get("sp"), gm, rf.get("gold", False), lite or rf.get("lite", False))
    Ff0 = sub(F, 0.0, D / 2, ph)
    for x, zz in sp["chochin"]:
        K.lantern_wall(mb, sub(Ff0, x, 0.15, zz), None, 0.0, 1.2)
    return dict(glow=glow, roof=r)


def lo_cols(area, F, spec):
    """colisao simples: soco + terreo numa caixa, 1 caixa por piso de cima"""
    sp = dict(LO_DEF)
    sp.update(spec)
    W, D = sp["W"], sp["D"]
    ph = sp["plinth"][1]
    fl = sp["floors"]
    h0 = ph + fl[0]["h"]
    col_box(area, (W + 0.6, D + 0.6, h0 + 0.3), F.p(0, 0, (h0 - 0.3) / 2), F.r())
    z = h0
    for f in fl[1:]:
        sf, sbk = f.get("setback", (0.0, 0.0))
        col_box(area, (W, D - sf - sbk, f["h"]), F.p(0, (sbk - sf) / 2, z + f["h"] / 2), F.r())
        z += f["h"]
    CAM_AREAS.append(area)


# ================================================================== CATALOGO (nome, familia, x, y, rumo da frente, cota, spec)
# familia "B" = frente do terreo do kit + resto leve; "C" = leve inteiro (lite). Rumo = direcao da FRENTE (graus).
def _F(x, y, z, deg):
    return Frame(x, y, z, math.radians(deg) - math.pi / 2)


def _fl(h, **kw):
    d = dict(h=h)
    d.update(kw)
    return d


def _roof(kind="irimoya", ridge="x", m=RB, pitch=0.55, over=2.8, lift=1.0, **kw):
    d = dict(kind=kind, ridge=ridge, m=m, pitch=pitch, over=over, lift=lift)
    d.update(kw)
    return d


DOORN = {"t": "door", "noren": INDIGO}
# ---------------------------------------------------- quarteirao OESTE (P): fileira que encara a praca (+x)
# ritmo: esquina verde de 2 pisos | loja de empena | casa baixa recuada | RECANTO (pavilhao) | esquina azul | CASA DE
# CHA (interior) | viela | casa verde de 2 pisos. Fundos para o cais do canal.
WEST = [
    ("W1", "B", -139.5, 140.5, 0.0, P, dict(W=25.0, D=28.0, plaster=PLS, plinth=("soco", 1.0),
        floors=[_fl(10.5, F=dict(kit=["shop", "lattice", "shop"], lod=1), front_pent=dict(z=9.0, depth=2.6)),
                _fl(8.0, setback=(2.2, 1.6))],
        roof=_roof("irimoya", "x", RG, 0.58, 3.0, 1.2), chochin=[(-8.0, 8.4), (8.0, 8.4)])),
    ("W2", "B", -139.0, 172.5, 0.0, P, dict(W=14.0, D=26.0, plaster=PLS,
        floors=[_fl(10.0, F=dict(kit=["shop", "koshi"], lod=1), front_pent=dict(z=8.6, depth=2.4)),
                _fl(7.6, setback=(1.4, 0.0))],
        roof=_roof("kirizuma", "y", RB, 0.62, 2.6, 0.6, lite=True))),
    ("W2b", "C", -141.5, 186.5, 0.0, P, dict(W=11.0, D=21.0, floors=[_fl(9.4)],
        roof=_roof("irimoya", "y", RB, 0.52, 2.6, 0.8))),
    ("W4", "B", -139.0, 230.0, 0.0, P, dict(W=18.0, D=28.0, plaster=PL, plinth=("soco", 1.0),
        floors=[_fl(10.5, F=dict(kit=["lattice", "shop", "koshi"], lod=1), front_pent=dict(z=9.0, depth=2.6)),
                _fl(8.2, setback=(1.8, 1.8))],
        roof=_roof("irimoya", "x", RB, 0.58, 3.0, 1.3))),
    ("W5", "B", -139.0, 283.0, 0.0, P, dict(W=24.0, D=26.0, plaster=PLW, plinth=("soco", 1.0),
        floors=[_fl(10.0, F=dict(kit=["koshi", DOORN, "koshi", "plain"], lod=1)),
                _fl(7.6, setback=(2.0, 1.0))],
        roof=_roof("irimoya", "x", RG, 0.56, 3.0, 1.1, lite=True))),
    ("W3b", "C", -153.0, 207.0, 180.0, P, dict(W=14.0, D=12.0, floors=[_fl(9.0)],
        roof=_roof("kirizuma", "x", RB, 0.6, 2.4, 0.6))),
]
# alem do canal (P): casas de frente para o canal (+x); patamares nas 2 pontes (y 170..194 e 246..259)
BEYOND = [
    ("X1", "C", -201.0, 142.0, 0.0, P, dict(W=24.0, D=18.0, floors=[_fl(9.6)], roof=_roof("irimoya", "x", RB, 0.55))),
    ("X2", "C", -202.0, 204.0, 0.0, P, dict(W=20.0, D=20.0, plaster=PL, floors=[_fl(10.0), _fl(7.4, setback=(1.6, 1.0))],
        roof=_roof("irimoya", "x", RG, 0.56))),
    ("X2b", "C", -202.5, 227.0, 0.0, P, dict(W=17.0, D=19.0, floors=[_fl(9.2)], roof=_roof("kirizuma", "y", RB, 0.6))),
    ("X3", "C", -202.0, 269.5, 0.0, P, dict(W=19.0, D=20.0, floors=[_fl(9.6)], roof=_roof("irimoya", "x", RB, 0.55))),
    ("X3b", "C", -200.5, 288.5, 0.0, P, dict(W=13.0, D=16.0, floors=[_fl(9.0)], roof=_roof("irimoya", "y", RG, 0.52))),
]
# ---------------------------------------------------- bairro do canal (T1): 2 lados da viela, moinho
BAIRRO = [
    ("SW1", "C", -59.0, 55.0, 90.0, T1, dict(W=18.0, D=20.0, floors=[_fl(10.0, front_pent=dict(z=8.6, depth=2.4))],
        roof=_roof("irimoya", "x", RB, 0.54, 2.8, 1.0))),
    ("SW2", "C", -81.0, 54.0, 90.0, T1, dict(W=15.0, D=18.0, floors=[_fl(9.4)], roof=_roof("kirizuma", "x", RB, 0.6))),
    ("SW3", "B", -101.0, 56.0, 90.0, T1, dict(W=18.0, D=18.0, plaster=PL,
        floors=[_fl(10.0, F=dict(kit=["koshi", DOORN, "plain"], lod=1)), _fl(7.4, setback=(1.4, 1.0))],
        roof=_roof("irimoya", "x", RG, 0.56, lite=True))),
    ("SW4", "C", -122.0, 53.0, 90.0, T1, dict(W=18.0, D=16.0, floors=[_fl(9.4)], roof=_roof("irimoya", "x", RB, 0.52))),
    ("SW5", "C", -149.0, 57.0, 90.0, T1, dict(W=12.0, D=12.0, floors=[_fl(8.6)], roof=_roof("kirizuma", "y", RB, 0.6))),
    ("NW1", "B", -58.0, 99.5, -90.0, T1, dict(W=18.0, D=21.0,
        floors=[_fl(10.0, F=dict(kit=["shop", "koshi"], lod=1), front_pent=dict(z=8.6, depth=2.4)),
                _fl(7.4, setback=(1.6, 0.0))],
        roof=_roof("kirizuma", "x", RB, 0.6, lite=True))),
    ("NW2", "C", -79.0, 101.0, -90.0, T1, dict(W=14.0, D=20.0, floors=[_fl(9.2)], roof=_roof("kirizuma", "y", RB, 0.6))),
    ("NW3", "B", -99.0, 100.0, -90.0, T1, dict(W=20.0, D=20.0, plaster=PL,
        floors=[_fl(10.0, F=dict(kit=["koshi", DOORN, "koshi"], lod=1)), _fl(7.6, setback=(1.6, 1.0))],
        roof=_roof("irimoya", "x", RG, 0.56, lite=True))),
    ("NW4", "C", -122.0, 100.0, -90.0, T1, dict(W=16.0, D=18.0, floors=[_fl(9.4)], roof=_roof("irimoya", "x", RB, 0.52))),
    ("S4", "B", -156.0, 92.0, 180.0, T1, dict(W=14.0, D=18.0, plaster=WM, plaster_up=WM, plinth=("soco", 1.2),
        floors=[_fl(10.5, F=dict(kit=[{"t": "door", "w": 5.8}, "plain", "plain"], lod=1, plaster=WM),
                    front_pent=dict(z=9.0, depth=2.2)),
                _fl(6.4)],
        roof=_roof("kirizuma", "y", RB, 0.62, 2.4, 0.5, lite=True), lit_p=0.2)),
]
# ---------------------------------------------------- terraco alto (W3): mansoes de telhado verde
TERRACE = [
    ("U1", "B", -152.0, 333.0, -90.0, W3Z, dict(W=32.0, D=22.0, plaster=PL, plinth=("ishigaki", 2.2),
        floors=[_fl(10.5, F=dict(kit=["shoji", "plaster", DOORN, "plaster", "shoji"], lod=1),
                    front_pent=dict(z=9.0, depth=2.6)),
                _fl(8.0, setback=(2.4, 2.4))],
        roof=_roof("irimoya", "x", RG, 0.6, 3.2, 1.4))),
    ("U2", "C", -128.0, 388.0, 0.0, W3Z, dict(W=22.0, D=22.0, plaster=PL, plinth=("ishigaki", 1.8),
        floors=[_fl(10.0), _fl(7.6, setback=(1.8, 1.8))],
        roof=_roof("irimoya", "x", RG, 0.58, 3.0, 1.2))),
    ("U3", "C", -178.0, 400.0, -90.0, W3Z, dict(W=22.0, D=18.0, floors=[_fl(9.6)], roof=_roof("irimoya", "x", RB, 0.54))),
    ("U4", "C", -199.0, 345.0, 0.0, W3Z, dict(W=18.0, D=20.0, plaster=PL, floors=[_fl(9.4), _fl(7.0, setback=(1.2, 1.2))],
        roof=_roof("kirizuma", "x", RG, 0.6))),
    ("U5", "C", -204.0, 382.0, 0.0, W3Z, dict(W=12.0, D=10.0, plinth=("soco", 1.2), plaster=PL, lit_p=0.0,
        floors=[_fl(8.0, F=[dict(t="door", s=0.0, w=4.0, h=6.4)], B=[], L=[], R=[]), _fl(5.6, F=[], B=[], L=[], R=[])],
        roof=_roof("kirizuma", "x", RG, 0.62, 2.0, 0.4))),
]
# ---------------------------------------------------- NE (P): casas de telhado avermelhado em volta do santuario
NE = [
    ("N2", "C", 190.0, 280.0, 90.0, P, dict(W=20.0, D=15.0, floors=[_fl(9.6)], roof=_roof("irimoya", "x", RRED, 0.55))),
    ("N6", "C", 166.0, 276.0, 90.0, P, dict(W=16.0, D=13.0, floors=[_fl(9.2)], roof=_roof("irimoya", "x", RB, 0.52))),
    ("N7", "C", 128.0, 273.0, 90.0, P, dict(W=16.0, D=12.0, floors=[_fl(9.2)], roof=_roof("kirizuma", "x", RRED, 0.6))),
    ("N5", "B", 110.0, 325.0, -90.0, P, dict(W=18.0, D=14.0, plaster=PL, plinth=("soco", 1.0),
        floors=[_fl(10.0, F=dict(kit=["shop", "lattice"], lod=1), front_pent=dict(z=8.6, depth=2.4)),
                _fl(7.6, setback=(1.4, 1.0))],
        roof=_roof("irimoya", "x", RRED, 0.58, 2.8, 1.2, lite=True))),
    ("N3", "C", 176.0, 326.0, -90.0, P, dict(W=18.0, D=14.0, floors=[_fl(9.4), _fl(7.0, setback=(1.2, 1.0))],
        roof=_roof("irimoya", "x", RRED, 0.54))),
    ("N8", "C", 196.0, 309.0, 180.0, P, dict(W=14.0, D=12.0, floors=[_fl(9.0)], roof=_roof("kirizuma", "x", RB, 0.6))),
    ("N9", "C", 157.0, 328.5, -90.0, P, dict(W=16.0, D=11.0, plaster=PL, floors=[_fl(9.0)],
        roof=_roof("irimoya", "x", RRED, 0.52))),
    ("N10", "C", 133.0, 327.5, -90.0, P, dict(W=14.0, D=12.0, floors=[_fl(9.2)], roof=_roof("kirizuma", "x", RB, 0.6))),
]
# ---------------------------------------------------- rua alta do porto (T1, bloco leste)
EAST = [
    ("E1", "C", 63.0, 51.0, 180.0, T1, dict(W=16.0, D=18.0, floors=[_fl(9.4)], roof=_roof("kirizuma", "y", RB, 0.6))),
    ("E4", "B", 62.0, 93.0, 90.0, T1, dict(W=16.0, D=20.0, plaster=PLS,
        floors=[_fl(10.0, F=dict(kit=["shop", "lattice"], lod=1), front_pent=dict(z=8.6, depth=2.4))],
        roof=_roof("kirizuma", "y", RB, 0.62, 2.6, 0.6, lite=True))),
    ("E5", "B", 84.0, 92.0, 90.0, T1, dict(W=22.0, D=22.0, plaster=PL, plinth=("soco", 1.0),
        floors=[_fl(10.5, F=dict(kit=["koshi", "shop", "lattice"], lod=1), front_pent=dict(z=9.0, depth=2.6)),
                _fl(8.0, setback=(2.0, 1.4))],
        roof=_roof("irimoya", "x", RB, 0.58, 3.0, 1.2), chochin=[(-7.0, 8.4), (7.0, 8.4)])),
    ("E6", "C", 107.0, 92.0, 90.0, T1, dict(W=18.0, D=18.0, plaster=PLW, floors=[_fl(10.0)],
        roof=_roof("irimoya", "x", RRED, 0.55))),
    ("E7", "C", 84.0, 58.0, 90.0, T1, dict(W=20.0, D=20.0, plaster=PL, floors=[_fl(9.8), _fl(7.4, setback=(1.6, 1.0))],
        roof=_roof("irimoya", "x", RB, 0.56))),
    ("E8", "C", 105.0, 57.0, 90.0, T1, dict(W=16.0, D=16.0, floors=[_fl(9.2)], roof=_roof("kirizuma", "x", RB, 0.6))),
    ("C4", "B", -28.0, 101.0, 0.0, T1, dict(W=16.0, D=24.0, plaster=PLS, plinth=("soco", 1.0),
        floors=[_fl(10.5, F=dict(kit=["shop", "lattice"], lod=0), R=dict(kit=["shop", "lattice", "shoji", "plaster"], lod=1),
                    front_pent=dict(z=9.0, depth=2.6)),
                _fl(8.2, setback=(1.8, 1.6), pents="FB")],
        roof=_roof("irimoya", "x", RG, 0.58, 3.0, 1.2), chochin=[(-4.2, 8.6), (4.2, 8.6)])),
]
SECTORS = {"Oeste": WEST, "Alem": BEYOND, "Bairro": BAIRRO, "Terraco": TERRACE, "NE": NE, "Leste": EAST}

# ---------------------------------------------------- familia A (kit inteiro)
C7_SPEC = dict(K.PRESETS["ESQ"], W=16.0, D=22.0, seed=7171, lod=1)
CHA = dict(W=18.0, D=22.0, plinth=("soco", 0.5), plaster=PLS, lod=0, back_lod=1, side_lod=1,
           floors=[dict(h=11.0, front=["lattice", {"t": "open", "w": 7.4}, "koshi"],
                        left=["plaster", "shoji", "plaster"], right=["plaster", "round", "plaster"],
                        back=["plaster", "plaster", "plaster"],
                        front_pent=dict(z=9.6, depth=2.8))],
           roof=dict(kind="irimoya", ridge="x", pitch=0.55, over=3.2, chidori=dict(x=0.0, w=6.4)),
           chochin=[(-6.2, 9.2), (6.2, 9.2)], seed=2626)
CHA_POS = (-138.0, 249.0, 0.0)                # (x, y, rumo): frente para a praca (+x), y 240..258 (vao 245..253)


# ================================================================== PAVIMENTO
def _quads(pts, hw):
    rb = L.ribbon(pts, hw)
    n = len(pts)
    left, right = rb[:n], list(reversed(rb[n:]))
    return [ccw([left[i], left[i + 1], right[i + 1], right[i]]) for i in range(n - 1)]


def _minus_convex(poly, convex):
    """partes de 'poly' FORA do poligono convexo (ccw)"""
    out = []
    cur = poly
    n = len(convex)
    for i in range(n):
        p, q = convex[i], convex[(i + 1) % n]
        a, b = -(q[1] - p[1]), (q[0] - p[0])
        c = -(a * p[0] + b * p[1])
        o = L._clip_half(cur, -a, -b, -c)
        if len(o) >= 3 and L.area(o) > 0.5:
            out.append(o)
        cur = L._clip_half(cur, a, b, c)
        if len(cur) < 3:
            break
    return out


def _minus_rects(pieces, rects):
    for r in rects:
        nxt = []
        for p in pieces:
            nxt += L.subtract_rect(p, r)
        pieces = nxt
    return pieces


def pave_region(mb, piece, z, key, big=False, mats=None):
    xs = [p[0] for p in piece]
    ys = [p[1] for p in piece]
    w, d = max(xs) - min(xs), max(ys) - min(ys)
    along = "x" if w >= d else "y"
    rows = ((4.4, 5.0), 5.2, 7.4) if big else ((3.0, 3.4), 3.4, 5.2)
    return K.pave(mb, ccw(piece), min(xs), max(xs), min(ys), max(ys), rows, STP, z + Z_OFF, z - 0.3, along=along,
                  key=key, mats=mats or [(STP, 5), (ST, 2), (STZ, 1)])


PLAZA_CVX = ccw(L.PLAZA)
CUT_ALL = [TRECHO_RECT, SUMMON_RECT]


def street_pieces(i):
    pts, w, z = L.STREETS[i]
    return [q for q in _quads(pts, w / 2)], z


def pave_streets(mbs):
    """todas as ruas e vielas da planta (L.STREETS 1..11; a 0 e do trecho, 12..14 ficam no lajeado do summon), sem
    sobreposicao (as retas cortam as diagonais), fora da praca e do lajeado do summon. mbs = {setor: MB}"""
    rects = {4: (-169.0, 120.0, -159.0, 298.0), 8: (-122.5, 120.0, -115.5, 300.0), 3: (-145.0, 76.0, -135.0, 108.0)}
    sector = {1: "Leste", 2: "Bairro", 3: "Bairro", 4: "Oeste", 5: "Alem", 6: "Oeste", 7: "Oeste", 8: "Oeste",
              9: "Terraco", 10: "NE", 11: "NE"}
    n = 0
    for i in range(1, 12):
        pts, w, z = L.STREETS[i]
        pieces = _quads(pts, w / 2)
        cut = list(CUT_ALL)
        if i == 2:
            cut.append(rects[3])
        if i in (6, 7):
            cut += [rects[4], rects[8]]
        if i == 11:
            cut.append((110.0, 270.0, 132.0, 290.2))
        pieces = _minus_rects(pieces, cut)
        out = []
        for p in pieces:
            out += _minus_convex(ccw(p), PLAZA_CVX)
        mb = mbs[sector[i]]
        for k, p in enumerate(out):
            if i == 5:                                     # cais oeste (alem do canal): terra batida
                mb.prism(ccw(p), z - 0.3, z + 0.12, DIRT)
            else:
                n += pave_region(mb, p, z, "st%d_%d" % (i, k), big=True)
    lane(mbs["Alem"], [(-186.0, 128.0), (-186.0, 294.0)], 0.1, P, "cO", "stones")
    return n


def lane(mb, pts, w, z, key, kind="dirt"):
    """beco proprio (fora de L.STREETS: sobre a pele de grama do terreno): terra batida com pedras de passo, ou
    lajes. Topo +0,12/+0,15 (a pele fica DENTRO do volume)"""
    n = 0
    for k, q in enumerate(_quads(pts, w / 2) if kind != "stones" else []):
        if kind == "dirt":
            mb.prism(ccw(q), z - 0.3, z + 0.12, DIRT)
        else:
            n += pave_region(mb, q, z, "%s%d" % (key, k))
    if kind in ("dirt", "stones"):
        tot = L.plen(pts)
        d = 1.4
        while d < tot - 1.0:
            acc = 0.0
            for a, b in zip(pts, pts[1:]):
                sl = math.dist(a, b)
                if acc + sl >= d:
                    t = (d - acc) / sl
                    x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                    ang = math.atan2(b[1] - a[1], b[0] - a[0])
                    jx = (_h(key, d) - 0.5) * 0.8
                    c, s = math.cos(ang), math.sin(ang)
                    r = 0.9 + 0.35 * _h(key, d, "r")
                    poly = [(x + jx * -s + r * math.cos(ang + j * math.pi / 3 + 0.3),
                             y + jx * c + r * math.sin(ang + j * math.pi / 3 + 0.3)) for j in range(6)]
                    K.slab_poly(mb, ccw(poly), z - 0.1, z + 0.26, 0.06, STP)
                    n += 1
                    break
                acc += sl
            d += (2.3 if kind == "dirt" else 4.2) + 0.6 * _h(key, d, "s")
    return n


# ------------------------------------------------------------------ CHAO DOS QUARTEIROES
# Terra batida nos quintais/becos entre as casas (o quarteirao deixa de ser gramado com casas soltas): prisma de topo
# +0,06 (a pele de grama fica DENTRO dele; as lajes das ruas, de topo +0,15 e chanfro ate +0,08, ficam por cima).
def _clip(poly, rect):
    return L.clip_rect(ccw(poly), rect)


YARDS = {
    "Oeste": [(L.P_BASE, (-159.0, 125.0, -122.6, 154.0), None), (L.P_BASE, (-159.0, 164.0, -122.6, 260.4),
              (-135.6, 193.0, -122.4, 220.0)), (L.P_BASE, (-159.0, 269.6, -122.6, 299.5), None)],
    "Alem": [(L.W2B, (-216.0, 127.0, -190.1, 295.0), None)],
    "Bairro": [(L.T1_BASE, (-131.0, 38.0, -48.0, 70.5), None), (L.T1_BASE, (-145.0, 40.0, -131.0, 68.6), None),
               (L.T1_BASE, (-160.0, 44.0, -145.0, 66.6), None), (L.T1_BASE, (-134.0, 83.0, -46.0, 116.5), None),
               (L.T1_BASE, (-169.5, 80.0, -145.2, 116.5), None)],
    "Leste": [(L.T1_BASE, (40.0, 40.0, 120.0, 104.6), None)],
    "NE": [(L.P_BASE, (118.0, 265.0, 222.0, 339.0), (132.0, 297.0, 170.0, 315.0))],
}


def yards(mb, key, z):
    for poly, rect, hole in YARDS.get(key, ()):
        pc = _clip(poly, rect)
        if len(pc) < 3:
            continue
        pieces = L.subtract_rect(pc, hole) if hole else [pc]
        for q in pieces:
            mb.prism(ccw(q), z - 0.3, z + 0.06, DIRT)
        if hole and key == "NE":                         # recinto do santuario: cascalho claro
            mb.prism(ccw(L.rect_poly(hole)), z - 0.3, z + 0.06, STP)


# ================================================================== PECAS DE LUGAR (torii, santuario, recantos)
def torii_small(mb, F, w=8.0, h=9.0, area="OP_CapTorii"):
    """TORII pequeno do santuario: pilares de laca sobre bases escuras, nuki que passa dos pilares, gakuzuka,
    shimaki e kasagi preto de pontas levantadas. F no centro do vao, no chao; pilares em x = +-w/2"""
    for s in (-1, 1):
        x = s * w / 2
        bb(mb, F, x - 0.85, x + 0.85, -0.85, 0.85, -0.3, 0.55, STD, 0.08)
        mb.cyl(0.55, h - 0.75, F.p(x, 0.0, 0.55 + (h - 0.75) / 2), (0, 0, 0), m=LAC, n=10, bevel=0.0)
        mb.cyl(0.62, 0.5, F.p(x, 0.0, 0.8), (0, 0, 0), m=RR, n=10, bevel=0.0)
        col_box(area, (1.4, 1.4, h), F.p(x, 0.0, h / 2), F.r())
    bb(mb, F, -w / 2 - 1.3, w / 2 + 1.3, -0.32, 0.32, h - 2.7, h - 2.0, LAC)
    bb(mb, F, -0.4, 0.4, -0.26, 0.26, h - 2.0, h - 0.95, LAC)
    bb(mb, F, -0.32, 0.32, -0.34, 0.34, h - 1.8, h - 1.15, GOLD)
    bb(mb, F, -w / 2 - 1.7, w / 2 + 1.7, -0.45, 0.45, h - 0.95, h - 0.4, LAC)
    X = w / 2 + 2.5
    xs = [-X + 2 * X * i / 10 for i in range(11)]
    K.strip(mb, F, [(x, 0.0, h - 0.42 + 0.75 * (abs(x) / X) ** 2.6) for x in xs], (0, 1, 0), -0.62, 0.62, 0.0, 0.55, RR)
    CAM_AREAS.append(area)


def shrine(mb):
    """SANTUARIO NE (telhado vermelho, conjunto avermelhado): torii pequeno (128, 306), sando de lajes ate o haiden,
    2 toro (1 aceso de noite), 2 nobori vermelhos no torii, HAIDEN = pavilhao aberto de laca (K.pavilion, frente
    para oeste, estrado acessivel) e HONDEN de laca com soco alto atras"""
    y0 = 306.0
    torii_small(mb, _F(128.0, y0, P + Z_OFF, 180.0), 8.0, 9.4)
    for s in (-1, 1):
        K.banner(mb, _F(130.6, y0 + s * 7.0, P + Z_OFF, 180.0), 12.0, CRED, CWHITE, 2.0, -s)
        col_box("OP_PropBanner", (1.9, 1.9, 12.0), (130.6, y0 + s * 7.0, P + 6.0))
        K.toro(mb, _F(137.0, y0 + s * 5.6, P + Z_OFF, 0.0), 0.9, "L_OPProp_Toro_Cap_NE" if s > 0 else None, 30.0)
        col_box("OP_PropToro", (2.6, 2.6, 7.0), (137.0, y0 + s * 5.6, P + 3.5))
    Fh = _F(146.5, y0, P, 180.0)
    K.pavilion(mb, Fh, 12.0, 9.4, 7.6, "irimoya", True, RRED, "F", 1.4, 1, True)
    pav_cols("OP_CapShrineDeck", Fh, 12.0, 9.4, 1.4)
    Fo = _F(161.5, y0, P, 180.0)
    hon = dict(W=9.0, D=8.0, plinth=("ishigaki", 2.0), plaster=PL, lit_p=0.0,
               floors=[_fl(7.8, F=dict(kit=[{"t": "door", "w": 7.0, "noren": None}], lod=1, plaster=LAC),
                           L=[], R=[], B=[])],
               roof=_roof("kirizuma", "y", RRED, 0.7, 2.6, 0.8, gold=True))
    lo_house(mb, Fo, hon, 5151)
    lo_cols("OP_CapHouseN1", Fo, hon)
    VEG_SPOTS.append((141.0, 318.0, P, "cerejeira", "santuario NE: emoldura o haiden pelo norte"))


def canal_bridge(mb, yc, key):
    """PONTE VERMELHA do canal oeste (visual; a colisao e do op_col, plana a 92,2): tabuleiro de tabuas com flecha
    baixa (>= 92,6 sobre o canal |x + 174| <= 4,8, capa do canal a 92,5; rampa curta ate as margens), 2 vigas de
    borda, ARCO de laca por baixo (2 longarinas curvas + montantes), guarda-corpo vermelho (pilaretes, corrimao e
    travessa seguindo a flecha, giboshi dourado nas pontas), encontros de pedra nas 2 capas."""
    xc, x0, x1 = -174.0, -181.2, -166.8
    F = Frame(0.0, 0.0, 0.0, 0.0)

    def zt(x):
        u = abs(x - xc)
        if u <= 5.2:
            return 92.66 + 0.24 * (1.0 - (u / 5.2) ** 2)
        t = min(1.0, (u - 5.2) / (abs(x1 - xc) - 5.2))
        return 92.66 + (P + 0.3 - 92.66) * t
    xs = [x0 + (x1 - x0) * i / 14 for i in range(15)]
    K.strip(mb, F, [(x, yc, zt(x)) for x in xs], (0, 1, 0), -4.4, 4.4, -0.32, 0.0, WM)
    for i in range(1, 14):                                 # juntas das tabuas (frisos escuros 0,14 abaixo do topo)
        x = xs[i]
        bb(mb, F, x - 0.05, x + 0.05, yc - 4.4, yc + 4.4, zt(x) - 0.3, zt(x) + 0.02, WD)
    for sy in (-1, 1):
        K.strip(mb, F, [(x, yc + sy * 4.75, zt(x)) for x in xs], (0, 1, 0), -0.35, 0.35, -0.75, 0.12, WD)
        # arco de laca sob o tabuleiro
        xa = [xc - 4.9 + 9.8 * i / 10 for i in range(11)]
        za = lambda x: 91.95 + 0.55 * math.cos(math.pi * (x - xc) / 10.4)
        K.strip(mb, F, [(x, yc + sy * 3.6, za(x)) for x in xa], (0, 1, 0), -0.32, 0.32, -0.42, 0.0, LAC)
        for x in (xc - 2.6, xc, xc + 2.6):
            bb(mb, F, x - 0.18, x + 0.18, yc + sy * 3.6 - 0.2, yc + sy * 3.6 + 0.2, za(x) - 0.1, zt(x) - 0.3, LAC)
        # guarda-corpo vermelho
        yr = yc + sy * 4.75
        px = [x0 + 0.4, xc - 4.6, xc - 1.6, xc + 1.6, xc + 4.6, x1 - 0.4]
        for j, x in enumerate(px):
            bb(mb, F, x - 0.22, x + 0.22, yr - 0.22, yr + 0.22, zt(x) - 0.1, zt(x) + 3.5, LAC)
            if j in (0, len(px) - 1):
                K.giboshi(mb, F, x, yr, zt(x) + 3.5, 1.0)
        rx = [x0 + 0.4 + (x1 - x0 - 0.8) * i / 10 for i in range(11)]
        K.strip(mb, F, [(x, yr, zt(x) + 3.3) for x in rx], (0, 1, 0), -0.17, 0.17, 0.0, 0.26, LAC)
        K.strip(mb, F, [(x, yr, zt(x) + 1.6) for x in rx], (0, 1, 0), -0.1, 0.1, 0.0, 0.18, LAC)
    for xe in (x0 + 0.8, x1 - 0.8):                        # encontros de pedra (sob a ponta do tabuleiro)
        bb(mb, F, xe - 0.9, xe + 0.9, yc - 5.4, yc + 5.4, 91.4, P + Z_OFF - 0.34, ST)


def recanto_oeste(mb):
    """RECANTO do quarteirao oeste (pausa na fileira que encara a praca): patio de terra com pedras de passo,
    pavilhao aberto do kit recuado, banco, toro"""
    y0, y1 = 193.0, 220.0
    mb.prism(ccw([(-135.5, y0), (-122.5, y0), (-122.5, y1), (-135.5, y1)]), P - 0.3, P + 0.12, DIRT)
    for i, yy in enumerate((203.0, 207.5, 212.0)):
        K.slab_poly(mb, ccw([(-131.0 + 2.6 * i, yy - 1.2), (-128.0 + 2.6 * i, yy - 1.2), (-128.0 + 2.6 * i, yy + 1.2),
                             (-131.0 + 2.6 * i, yy + 1.2)]), P - 0.1, P + 0.26, 0.06, STP)
    Fp = _F(-141.0, 207.5, P, 0.0)
    pav_lo(mb, Fp, 13.0, 10.0, 7.4, RB, False, 1.1)
    pav_cols("OP_CapPav", Fp, 13.0, 10.0, 1.1)
    K.bench(mb, Frame(0, 0, 0, 0), -126.0, 217.0, 5.0, 1.6, 1.6, 0.0, P + 0.12)
    col_box("OP_CapBench", (5.0, 1.6, 1.6), (-126.0, 217.0, P + 0.9))
    K.toro(mb, _F(-125.5, 197.0, P + 0.12, 0.0), 0.8)
    col_box("OP_PropToro", (2.4, 2.4, 6.2), (-125.5, 197.0, P + 3.1))
    VEG_SPOTS.append((-131.0, 216.5, P, "cerejeira", "recanto oeste: sombra sobre o banco, copa >= 4 da fachada"))


# ================================================================== CASA DE CHA COM INTERIOR
def cha_house(mb):
    x, y, deg = CHA_POS
    F = _F(x, y, P, deg)
    sp = CHA
    W, D = sp["W"], sp["D"]
    ph = sp["plinth"][1]
    h = sp["floors"][0]["h"]
    K.house(mb, F, sp, "L_OPCap_Win_Cha", 60.0)
    Fz = sub(F, z=ph)
    fy = D / 2
    # verga + reboco sobre o vao aberto (o kit deixa o vao 'open' livre ate a viga)
    bb(mb, Fz, -3.7, 3.7, fy - 0.9, fy + 0.05, 8.0, 8.45, WD)
    K.panel(mb, sub(Fz, 0.0, fy), -3.7, 3.7, 8.45, h - 0.95, -0.8, -0.22, [], PLS)
    K.noren_cloth(mb, sub(Fz, 0.0, fy), -3.5, 3.5, 7.95, 2.6, INDIGO)
    # degrau de pedra na frente do vao
    K.stone(mb, sub(F, 0.0, fy + 0.3), -3.4, 3.4, -0.3, 0.6, -0.3, 1.4, 1.4, 0.08, STP)
    # INTERIOR: assoalho (topo = topo da soleira 0,7), forro de tabuas com vigas, parede do fundo com porta de papel
    xi, yi = W / 2 - 0.95, D / 2 - 0.95
    bb(mb, Fz, -xi, xi, -yi, fy - 0.95, 0.35, 0.7, WM)
    for k in range(6):
        xx = -xi + 2 * xi * (k + 0.5) / 6
        bb(mb, Fz, xx - 0.05, xx + 0.05, -yi, fy - 0.95, 0.7, 0.72, WD)     # juntas das tabuas (0,02 acima: frisos)
    zc = h - 1.0
    bb(mb, Fz, -xi, xi, -yi, yi, zc - 0.25, zc, WM)
    for yy in (-6.0, 0.0, 6.0):
        bb(mb, Fz, -xi, xi, yy - 0.35, yy + 0.35, zc - 0.85, zc - 0.25, WD)
    yb = -D / 2 + 0.8                                      # face interna da parede do fundo
    Fb = sub(Fz, 0.0, yb)                                  # +y local = para dentro do salao
    for xa, xb in ((-2.6, -0.06), (0.06, 2.6)):
        bb(mb, Fb, xa, xb, 0.0, 0.14, 0.7, 7.6, WM)
        bb(mb, Fb, xa + 0.28, xb - 0.28, 0.14, 0.28, 3.2, 7.2, LIT)
        xm = (xa + xb) / 2
        bb(mb, Fb, xm - 0.05, xm + 0.05, 0.28, 0.42, 3.2, 7.2, WD)
    bb(mb, Fb, -2.9, 2.9, 0.0, 0.3, 7.6, 8.0, WD)
    K.noren_cloth(mb, sub(Fb, 0.0, -0.1), -2.4, 2.4, 7.55, 1.9, CRED)
    # prateleiras com potes nas 2 metades do fundo
    for xa, xb in ((-xi + 0.3, -3.4), (3.4, xi - 0.3)):
        for zz in (4.4, 6.2):
            bb(mb, Fb, xa, xb, 0.0, 0.9, zz - 0.14, zz, WM)
            for i, xx in enumerate(K.even(xa + 0.3, xb - 0.3, 0.95)):
                if _h("cha", xa, zz, i) < 0.7:
                    K.pot(mb, Fb, xx, 0.45, zz, 0.28, 0.55 + 0.35 * _h("cha", xa, zz, i, "h"),
                          (K.STD, PL, WM, ST)[int(_h("cha", zz, i, "m") * 4) % 4])
    # balcao (lado direito de quem entra = -x local... lado +x local) com tampo e potes
    bb(mb, Fz, xi - 3.4, xi - 2.2, -5.5, 3.5, 0.7, 3.6, WD)
    bb(mb, Fz, xi - 3.6, xi - 2.0, -5.7, 3.7, 3.6, 3.85, WM)
    for i, yy in enumerate((-4.0, -1.0, 2.0)):
        K.jar(mb, Fz, xi - 2.8, yy, 3.85, 0.42, 0.9, (K.STD, PL, K.STD)[i], lid=i == 1)
    # estrado de tatami (agari) do lado esquerdo, mesa baixa e almofadas
    xa = -xi
    bb(mb, Fz, xa, xa + 6.4, -yi + 1.4, 4.2, 0.7, 1.95, WD)
    bb(mb, Fz, xa + 0.1, xa + 6.3, -yi + 1.5, 4.1, 1.95, 2.15, STRAW)
    for yy in (-4.6, 0.4):
        bb(mb, Fz, xa + 0.1, xa + 6.3, yy - 0.05, yy + 0.05, 2.15, 2.18, WD)
    tx, ty = xa + 3.2, -1.2
    bb(mb, Fz, tx - 1.6, tx + 1.6, ty - 1.1, ty + 1.1, 3.05, 3.3, WM)
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fz, tx + sx * 1.3 - 0.12, tx + sx * 1.3 + 0.12, ty + sy * 0.8 - 0.12, ty + sy * 0.8 + 0.12, 2.15, 3.05, WD)
    for (cx_, cy_, m) in ((tx, ty - 2.2, CRED), (tx, ty + 2.2, INDIGO), (tx - 2.3, ty, CRED)):
        bb(mb, Fz, cx_ - 0.7, cx_ + 0.7, cy_ - 0.7, cy_ + 0.7, 2.15, 2.45, m)
    K.jar(mb, Fz, tx - 0.5, ty, 3.3, 0.25, 0.45, PL)
    K.jar(mb, Fz, tx + 0.5, ty + 0.2, 3.3, 0.2, 0.35, K.STD)
    # 2 chochin pendurados do forro
    for xx, yy in ((-2.0, 4.0), (2.4, -2.0)):
        mb.rod(Fz.p(xx, yy, zc - 0.25), Fz.p(xx, yy, zc - 1.4), 0.04, K.IRON, 6)
        K.chochin(mb, Fz, (xx, yy, zc - 1.4 - 1.5), 0.55, 1.5, CRED)
    light("L_OPCap_Int_Cha", "POINT", Fz.p(0.0, -1.0, 7.0), 260.0, K.WARM, 0.5)
    # COLISAO: soco + piso (entra pelo degrau), paredes, pilares da frente, balcao, estrado
    area = "OP_CapHouseCha"
    zf = ph + 0.7
    col_box(area, (W + 0.6, D + 0.6, zf + 0.3), F.p(0, 0, (zf - 0.3) / 2), F.r())
    col_box(area, (W, 1.0, h), F.p(0, -D / 2 + 0.5, zf + h / 2), F.r())
    for s in (-1, 1):
        col_box(area, (1.0, D, h), F.p(s * (W / 2 - 0.5), 0, zf + h / 2), F.r())
        col_box(area, (W / 2 - 3.8, 1.0, h), F.p(s * (W / 2 + 3.8) / 2, D / 2 - 0.5, zf + h / 2), F.r())
    col_box(area, (W, 1.2, h - 8.0), F.p(0, D / 2 - 0.6, ph + 8.0 + (h - 8.0) / 2), F.r())
    col_box("OP_CapChaMobilia", (1.6, 9.4, 3.2), Fz.p(xi - 2.8, -1.0, 2.2), F.r())
    col_box("OP_CapChaMobilia", (6.4, yi + 4.2 - 1.4, 1.5), Fz.p(xa + 3.2, (-yi + 1.4 + 4.2) / 2, 1.35), F.r())
    col_box("OP_CapChaMobilia", (6.8, 1.0, 0.6), F.p(0.0, fy + 0.85, 0.3), F.r())
    CAM_AREAS.append(area)


# ================================================================== SETORES
def pav_cols(area, F, W, D, deck):
    """pavilhao: estrado (sobe pelo degrau) + guardas dos 3 lados fechados (frente +y aberta)"""
    col_box(area, (W, D, deck), F.p(0, 0, deck / 2), F.r())
    for (a, b, c_, d_) in ((-W / 2, W / 2, -D / 2, -D / 2 + 0.6), (-W / 2, -W / 2 + 0.6, -D / 2, D / 2),
                           (W / 2 - 0.6, W / 2, -D / 2, D / 2)):
        col_box(area, (b - a, d_ - c_, 4.0), F.p((a + b) / 2, (c_ + d_) / 2, deck + 2.0), F.r())
    CAM_AREAS.append(area)


def _sector(name, specs, mb, ncol=True):
    for nm, tier, x, y, deg, z, sp in specs:
        F = _F(x, y, z, deg)
        seed = int(_h("cap", nm) * 9000) + 11
        sp = dict(sp, lite=(tier == "C"))
        lo_house(mb, F, sp, seed)
        if ncol:
            lo_cols("OP_CapHouse" + nm, F, sp)


def _kit_houses(mb):
    """C7: esquina-marco vermelha de 3 pisos (kit inteiro, ESQ) do lado leste da chegada, colada no trecho"""
    for nm, sp, (x, y, deg) in (("C7", C7_SPEC, (28.0, 93.0, 180.0)),):
        F = _F(x, y, T1, deg)
        K.house(mb, F, sp, "L_OPCap_Win_M4%s" % nm, 60.0)
        K.house_cols("OP_CapHouse" + nm, F, sp)
        CAM_AREAS.append("OP_CapHouse" + nm)


def lamp(mb, x, y, z, ang, name=None, h=8.6):
    K.lantern_post(mb, Frame(x, y, z, ang), h, 1.6, name, 40.0)
    col_box("OP_PropLamp", (0.9, 0.9, h), (x, y, z + h / 2))


def bench(mb, x, y, z, ang, L_=5.0):
    K.bench(mb, Frame(0, 0, 0, 0), x, y, L_, 1.6, 1.6, ang, z)
    col_box("OP_CapBench", (L_, 1.6, 1.6), (x, y, z + 0.8), (0, 0, ang))


def _oeste():
    mb = MB("OP_Cap_Oeste", COLL, random.Random(401), detail="hero")
    _sector("Oeste", WEST, mb)
    yards(mb, "Oeste", P)
    cha_house(mb)
    recanto_oeste(mb)
    for yc, k in ((182.0, "S"), (252.0, "N")):
        canal_bridge(mb, yc, k)
    lamp(mb, -124.2, 155.0, P + 0.12, 0.0, "L_OPProp_Lamp_Cap_Oeste", 8.6)
    lamp(mb, -124.2, 270.2, P + 0.12, 0.0, None, 8.6)
    return mb


def _alem(mb):
    _sector("Alem", BEYOND, mb)
    yards(mb, "Alem", P)
    for yy in (172.0, 245.5):
        bench(mb, -196.0, yy, P + 0.12, 0.0, 4.6)
    VEG_SPOTS.append((-204.0, 182.0, P, "pinheiro", "patamar da ponte sul do canal (alem)"))
    VEG_SPOTS.append((-204.0, 252.0, P, "cerejeira", "patamar da ponte norte do canal (alem)"))
    return mb


def _bairro():
    mb = MB("OP_Cap_Bairro", COLL, random.Random(403), detail="hero")
    _sector("Bairro", BAIRRO, mb)
    yards(mb, "Bairro", T1)
    # MIRANTE na falesia sul (entre SW4 e SW5): banco virado para o mar, mureta na borda
    bench(mb, -139.0, 56.0, T1 + 0.12, 0.0, 4.6)
    K.parapet(mb, Frame(-139.5, 45.0, T1 + 0.12, math.radians(-14.0)), 11.0, 2.2, 1.2, key="mirSW")
    col_box("OP_CapMureta", (11.0, 1.4, 2.4), (-139.5, 45.0, T1 + 1.2), (0, 0, math.radians(-14.0)))
    lane(mb, [(-139.0, 69.4), (-139.0, 52.0)], 3.0, T1, "lSW")
    lamp(mb, -133.0, 66.6, T1 + 0.12, 0.0, "L_OPProp_Lamp_Cap_Bairro", 8.4)
    lane(mb, [(-71.0, 72.5), (-71.0, 52.0)], 3.4, T1, "lSW2")
    VEG_SPOTS.append((-138.0, 59.0, T1, "cerejeira", "mirante sul do bairro do canal (sombra no banco)"))
    VEG_SPOTS.append((-110.5, 88.0, T1, "arbusto", "pe do NW3"))
    return mb


def _terraco(mb):
    _sector("Terraco", TERRACE, mb)
    # jardim da frente da U1 (sobre o arrimo do terraco): caminho de lajes da rua ate a porta
    lane(mb, [(-152.0, 321.8), (-152.0, 310.0), (-128.0, 310.0), (-121.5, 316.0)], 3.6, W3Z, "lU1", "paved")
    lamp(mb, -127.5, 357.0, W3Z + 0.12, 0.0, "L_OPProp_Lamp_Cap_Terraco", 8.4)
    VEG_SPOTS.append((-140.0, 306.0, W3Z, "cerejeira", "jardim da U1 sobre o arrimo (vista da praca)"))
    VEG_SPOTS.append((-188.0, 372.0, W3Z, "pinheiro", "terraco alto, entre U3 e U4"))
    return mb


def _ne():
    mb = MB("OP_Cap_NE", COLL, random.Random(405), detail="hero")
    _sector("NE", NE, mb)
    yards(mb, "NE", P)
    shrine(mb)
    lane(mb, [(137.6, 306.0), (141.6, 306.0)], 5.6, P, "sando", "paved")
    VEG_SPOTS.append((180.0, 306.0, P, "cerejeira", "entre honden e N8"))
    return mb


def _leste():
    mb = MB("OP_Cap_Leste", COLL, random.Random(406), detail="hero")
    _sector("Leste", EAST, mb)
    yards(mb, "Leste", T1)
    _kit_houses(mb)
    lane(mb, [(49.5, 104.6), (49.5, 44.0)], 6.4, T1, "bNS", "paved")
    lane(mb, [(52.7, 75.0), (114.0, 75.0)], 5.0, T1, "bLO", "paved")
    # MIRANTE do porto na ponta da travessa: banco, mureta na borda, poste aceso
    K.parapet(mb, Frame(119.6, 75.0, T1 + 0.12, math.pi / 2), 12.0, 2.2, 1.2, key="mirE")
    col_box("OP_CapMureta", (1.4, 12.0, 2.4), (119.6, 75.0, T1 + 1.2))
    bench(mb, 115.6, 69.6, T1 + 0.12, 0.0, 4.4)
    lamp(mb, 114.5, 78.8, T1 + 0.12, 0.0, "L_OPProp_Lamp_Cap_Porto", 8.4)
    VEG_SPOTS.append((112.0, 71.0, T1, "cerejeira", "mirante do porto (concept: cerejeiras sobre o porto)"))
    VEG_SPOTS.append((73.0, 43.0, T1, "pinheiro", "borda sul do bloco leste"))
    return mb


# ================================================================== CAMERAS
EYE = 5.65
CAMS = {
    # gerais
    "CAM_OP_M4Cap_Aerea": ((-20.0, -60.0, 250.0), (-40.0, 190.0, 88.0), 22),
    "CAM_OP_M4Cap_Aerea_Oeste": ((-330.0, 150.0, 200.0), (-145.0, 215.0, 92.0), 24),
    "CAM_OP_M4Cap_Aerea_NE": ((60.0, 190.0, 175.0), (165.0, 300.0, 92.0), 26),
    "CAM_OP_M4Cap_Aerea_Leste": ((30.0, -30.0, 150.0), (78.0, 78.0, 88.0), 26),
    "CAM_OP_M4Cap_Aerea_Bairro": ((-60.0, -40.0, 160.0), (-100.0, 80.0, 88.0), 26),
    # altura do jogador por setor
    "CAM_OP_M4Cap_PH_RuaOeste": ((-119.0, 126.0, P + EYE), (-123.0, 260.0, P + 7.0), 22),
    "CAM_OP_M4Cap_PH_PracaOeste": ((-74.0, 196.0, P + EYE), (-132.0, 232.0, P + 8.0), 22),
    "CAM_OP_M4Cap_PH_Cais": ((-164.0, 130.0, P + EYE), (-174.0, 260.0, P + 4.0), 22),
    "CAM_OP_M4Cap_PH_Bairro": ((-42.0, 84.0, T1 + EYE), (-150.0, 75.0, T1 + 6.0), 22),
    "CAM_OP_M4Cap_PH_Moinho": ((-126.0, 80.0, T1 + EYE), (-160.0, 93.0, T1 + 6.0), 24),
    "CAM_OP_M4Cap_PH_NE": ((104.0, 281.0, P + EYE), (200.0, 296.0, P + 7.0), 22),
    "CAM_OP_M4Cap_PH_Santuario": ((112.0, 302.0, P + EYE), (150.0, 306.0, P + 6.5), 24),
    "CAM_OP_M4Cap_PH_Terraco": ((-112.0, 316.0, W3Z + EYE), (-150.0, 352.0, W3Z + 8.0), 22),
    "CAM_OP_M4Cap_PH_RuaAltaPorto": ((20.0, 111.0, T1 + EYE), (120.0, 104.0, T1 + 7.0), 22),
    "CAM_OP_M4Cap_PH_Beco": ((49.5, 101.0, T1 + EYE), (50.0, 40.0, T1 + 5.0), 22),
    # closes
    "CAM_OP_M4Cap_Close_Cha": ((-111.0, 258.0, P + 6.0), (-128.0, 249.0, P + 5.5), 24),
    "CAM_OP_M4Cap_Close_ChaInterior": ((-129.2, 248.5, P + 1.2 + 5.2), (-146.0, 247.0, P + 1.2 + 3.0), 18),
    "CAM_OP_M4Cap_Close_C7": ((6.0, 108.0, T1 + 7.0), (30.0, 92.0, T1 + 11.0), 24),
    "CAM_OP_M4Cap_Close_C4": ((6.0, 84.0, T1 + 7.0), (-22.0, 100.0, T1 + 9.0), 24),
    "CAM_OP_M4Cap_Close_W1": ((-104.0, 128.0, P + 7.0), (-130.0, 145.0, P + 8.0), 24),
    "CAM_OP_M4Cap_Close_Moinho": ((-148.0, 70.5, T1 + 6.5), (-169.0, 91.0, T1 + 5.0), 24),
    "CAM_OP_M4Cap_Close_Santuario": ((121.0, 291.0, P + 6.0), (148.0, 306.0, P + 5.0), 24),
    "CAM_OP_M4Cap_Close_U1": ((-118.0, 304.0, W3Z + 6.0), (-150.0, 330.0, W3Z + 9.0), 24),
    "CAM_OP_M4Cap_Close_E5": ((70.0, 112.0, T1 + 6.5), (86.0, 95.0, T1 + 8.0), 24),
    "CAM_OP_M4Cap_Close_Fundo": ((-183.0, 196.0, P + 6.5), (-200.0, 232.0, P + 7.0), 24),
    "CAM_OP_M4Cap_Close_Ponte": ((-160.5, 168.0, P + 6.5), (-176.0, 184.0, P + 2.5), 24),
}


def _cams():
    for n, (loc, tgt, lens) in CAMS.items():
        DL.camera(n, loc, tgt, lens)


# ================================================================== BUILD
SENTINEL = "OP_Cap_Oeste"


def build():
    if bpy.data.objects.get(SENTINEL):
        return
    CAM_AREAS.clear()
    VEG_SPOTS.clear()
    # trecho M2 (dono: op_m2_trecho) - mesmas funcoes, sem o _blockout_rest()
    TR._street()
    TR._shops()
    TR._lamps_and_stair()
    TR._cams()
    mbs = {}
    mbs["Oeste"] = _oeste()
    mf = MB("OP_Cap_OesteFundo", COLL, random.Random(402), detail="far")   # alem do canal + terraco alto (1 objeto)
    mbs["Alem"] = _alem(mf)
    mbs["Bairro"] = _bairro()
    mbs["Terraco"] = _terraco(mf)
    mbs["NE"] = _ne()
    mbs["Leste"] = _leste()
    n = pave_streets(mbs)
    # escadas da planta que eram do blockout (Sudoeste, OesteAlta): pedra do kit como a escadaria Praca
    for nm in ("Sudoeste", "OesteAlta"):
        foot, deg, w, ns, tread, g = L.stair_frame(nm)
        Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
        K.stair_stone(mbs["Oeste"], Fs, w, ns, rise=L.stair_rise(nm), tread=tread, z_floor=-0.3, z_off=Z_OFF,
                      cheek_h=1.0, newels=True)
    for mb in {id(m): m for m in mbs.values()}.values():
        mb.finish()
    _cams()
    print("op_capital: %d casas leves, ruas %d lajes, CAM_AREAS %d" % (
        sum(len(v) for v in SECTORS.values()), n, len(CAM_AREAS)))
