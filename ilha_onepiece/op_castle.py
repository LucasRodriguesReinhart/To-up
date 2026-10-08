# op_castle.py - CASTELO ELEVADO (marco heroi da Ilha 5 ONE PIECE / WANO, M3; dono "castle", prefixo OP_Cas_)
# PROMPT_USUARIO secoes 2, 8, 15-17 + PLANO_OP secoes 0.5, 4.3, 8, 9. Substitui castle() do op_blockout.
#   TORRE (tenshu) de 4 andares escalonados = os volumes TRAVADOS de L.KEEP_TIERS (a arvore respeita a mesma
#     envoltoria: op_tree.castle_envelope). Base de cantaria em talude (ishigaki) com cantos travados; reboco claro
#     off-white (Plaster_OP 234/228/212: nao estoura no bloom do dia), faixa escura de viga + misulas sob cada beiral,
#     janelas recuadas de barras brancas sobre fundo escuro (cenograficas) e janelas de papel aceso no salao.
#     Telhados ESCUROS escalonados: saia intermediaria no terreo, saias de 4 aguas com beiral grosso, sori e capas de
#     espigao entre os andares, CHIDORI-HAFU (par na frente/fundos do 1o telhado, um grande no 2o, nos lados do 1o e
#     do 3o), KARAHAFU de beiral (onda) na frente e no fundo do 3o telhado, irimoya no topo com chidori e
#     SHACHIHOKO dourados nas pontas da cumeeira. 4o andar com VARANDA VERMELHA em volta (mawari-en). 360 graus:
#     as 4 faces tem janelas, faixas, misulas e empenas proprias (nada de face lisa escondida).
#   TERREO ACESSIVEL: porta aberta 6 x 9 sob um alpendre de KARAHAFU dourado, folhas abertas para dentro, SALAO REAL
#     52 x 42 (piso de tabuas com junta, teto em caixotoes, pilares, nageshi, rodape, estrado ao fundo com biombos
#     dourados e rolo com o brasao, 3 lanternas de papel penduradas = as 3 luzes L_OPCas_Hall_*), retorno pela mesma
#     porta. Andares de cima: CENOGRAFICOS (colisao em caixa, sem quartos).
#   PATIO (136,2) em proa: guarda-corpo VERMELHO de laca no mirante da frente (entre 2 torreoes de canto), muro dobei
#     (reboco + capa de telha + seteiras vazadas) no flanco da subida, no oeste e no fundo, terminando ENCOSTADO na
#     base da arvore; portao do patio (koraimon) no topo da escada CasteloB; 2 toro.
#   ADRO (98,2): PORTAO VERMELHO (36 de vao, pilares de laca com pilares de apoio e telhadinhos, viga com o brasao
#     dourado, telhado com onigawara dourada) sobre o topo da escada Adro, mureta de cantaria na bacia da cachoeira,
#     portao de madeira (kabukimon) no pe da subida, 2 postes de lanterna. Escadas Adro / CasteloA / CasteloB em
#     pedra do op_kit no envelope do op_col. ESTANDARTES brancos com o brasao circular (anel + 8 petalas + miolo, o
#     mesmo desenho do emblema da praca; sem texto) nos 2 paineis planos da falesia, com suporte real (vara com
#     ponteiras, 2 bracos de ferro chumbados na rocha, barra de peso).
#   Sem funcao inventada (sem trono, chefe, upgrade): o castelo e marco visual + salao visitavel.
# COLISAO (simples, sem fechar portas): salao (paredes com o vao da porta, piso, teto, pilares, estrado, biombos,
#   folhas da porta), caixas dos andares de cima, base de pedra, alpendre, portoes (pilares), torreoes, toro, postes.
#   O chao/escadas/guardas sao do op_col (congelado).
# Ordem do build_op: roda ANTES do op_tree (o check_castle do op_tree le as malhas OP_Cas_*).
import math, random, os
import bpy
from mathutils import Vector
import op_lib as DL
from op_lib import MB, Frame, light, col_box, ccw
import op_layout as L
import op_kit as K
from op_kit import (WD, WM, LAC, GOLD, IRON, PL, RB, RR, ST, STD, STP, LIT, LGLOW, INDIGO, CWHITE, bb, bx, sub,
                    loft, lathe, lathe_y, ext, beam, even)

C = "04_CASTLE"
CC, CF, CL, P = L.CC, L.CF, L.CL, L.P
KX, KY = L.KEEP_C
T = L.KEEP_TIERS                        # (hx, hy, z0, altura da parede, beiral)
WALL = "Stone_OP_Wall"
DARK = "Roof_OP_Ridge"                  # fundo escuro das janelas cenograficas (o mais escuro da paleta)
WARM = (1.0, 0.64, 0.36)
FLOOR = 0.45                            # piso do salao acima do patio (degrau na soleira)
PLINTH = 4.5                            # base de cantaria da torre
DOOR_W, DOOR_H = L.KEEP_DOOR[2], L.KEEP_DOOR[3]
PITCH = 0.42
RIB_TRI = [(-0.3, -0.12), (0.0, 0.24), (0.3, -0.12)]    # canal de telha triangular (le igual de longe; 2/3 dos tris)
# telhados-saia entre os andares: (indice do andar de baixo, profundidade, z_top no pe da parede de cima)
SKIRTS = [(0, (T[0][1] - T[1][1]) + T[0][4], T[1][2] + 0.6),
          (1, (T[1][1] - T[2][1]) + T[1][4], T[2][2] + 0.6),
          (2, (T[2][1] - T[3][1]) + T[2][4], T[3][2] + 0.6)]
MID_SKIRT = (16.0, 3.2)                 # saia intermediaria do terreo (z_top na parede, profundidade)
COURT_GATE_Y = 440.5                    # portao do patio: logo depois do topo da CasteloB (439)
SE_TURRET = (58.0, 365.0, 12.0)         # yagura SE (centro na borda da proa, girada com ela)
SW_TURRET = (-57.0, 367.0, 10.0)        # sumi-yagura SO (menor; equilibra a frente da proa)


# ================================================================== utilidades
def keep_frame():
    return Frame(KX, KY, CC, math.pi)                   # +y local = frente (praca, -Y do mundo)


def faces(F, hx, hy):
    """(chave, referencial da face (y=0 na face, +y fora, z relativo), comprimento, meia profundidade)"""
    out = []
    for key, ang, ln, d in (("F", 0.0, 2 * hx, hy), ("B", math.pi, 2 * hx, hy), ("R", -math.pi / 2, 2 * hy, hx),
                            ("L", math.pi / 2, 2 * hy, hx)):
        Fa = sub(F, 0.0, 0.0, 0.0, ang)
        out.append((key, sub(Fa, 0.0, d, 0.0), ln, d))
    return out


def slope_for(Xi, Yi, depth, z_top, pitch):
    return K.Slope(Xi + depth, Yi + depth, z_top - pitch * depth, pitch, pitch * 0.5, Xi + depth, Yi + depth, 0.0)


def fascia(mb, Fk, x0, x1, y, zf, tv, depth=0.55, d2=0.38, dense=None, second=True):
    """beiral grosso (testeira + 2a tabua recuada) seguindo zf com amostragem DENSA onde ha karahafu"""
    xs = [x0 + (x1 - x0) * t for t in (0.0, 0.07, 0.2, 0.5, 0.8, 0.93, 1.0)]
    if dense:
        a, b = dense
        xs += [a + (b - a) * i / 20 for i in range(21)]
    xs = sorted(set(round(x, 3) for x in xs if x0 - 1e-6 <= x <= x1 + 1e-6))
    K.strip(mb, Fk, [(x, y, zf(x, y) - tv) for x in xs], (0, 1, 0), -0.18, 0.18, -depth, 0.06, WD)
    if not second:
        return
    K.strip(mb, Fk, [(x, y - 0.3, zf(x, y) - tv - depth + 0.04) for x in xs[1:-1]], (0, 1, 0), -0.14, 0.14, -d2, 0.02,
            WD)


def skirt(mb, F, Xi, Yi, depth, z_top, pitch=PITCH, tv=0.5, lift=1.0, m=RB, chid=None, kara=None, gold=False, sp=2.0,
          oni=True, second=True):
    """SAIA de 4 aguas entre andares (o K.roof_skirt do kit + vaos de canal sob os chidori + KARAHAFU de beiral):
    chid = {"F"|"B"|"R"|"L": [(xc, w, yd)]} no referencial DA FACE (+y fora, x ao longo da face);
    kara = {"F"|"B": (w, rise)} = o beiral sobe em sino no meio da face (tímpano de reboco por baixo, gegyo dourado)"""
    chid = chid or {}
    kara = kara or {}
    Xe, Ye = Xi + depth, Yi + depth

    def base_y(x, y):
        d = max(0.0, abs(y) - Yi + 0.35)
        return z_top - pitch * (abs(y) - Yi) + lift * (min(1.0, abs(x) / Xe) ** 3) * (min(1.0, d / depth) ** 3)

    def base_x(x, y):
        d = max(0.0, abs(x) - Xi + 0.35)
        return z_top - pitch * (abs(x) - Xi) + lift * (min(1.0, abs(y) / Ye) ** 3) * (min(1.0, d / depth) ** 3)

    def bump(face, x, y):
        if face not in kara:
            return 0.0
        w, rise = kara[face]
        u = abs(x) / (w / 2)
        if u >= 1.0:
            return 0.0
        y0 = Yi + depth * 0.2
        t = max(0.0, (y - y0) / (Ye - y0))
        return rise * 0.5 * (1.0 + math.cos(math.pi * u)) * t ** 1.4
    for Fk, fy, fx in ((F, "F", "R"), (sub(F, ang=math.pi), "B", "L")):
        zfy = (lambda x, y, fy=fy: base_y(x, y) + bump(fy, x, y))
        kd = fy in kara
        nu = max(4, int(2 * Xe / (1.1 if kd else 4.2)))
        tks = [0.0, 0.25, 0.5, 0.75, 1.0] if kd else [0.0, 0.5, 1.0]
        K.sheet(mb, Fk, [(-Xe, Ye), (Xe, Ye), (Xi, Yi - 0.35), (-Xi, Yi - 0.35)], zfy, tv, nu, tks, m)
        K.sheet(mb, Fk, [(Xe, -Ye), (Xe, Ye), (Xi - 0.35, Yi), (Xi - 0.35, -Yi)], base_x, tv, max(3, int(2 * Ye / 4.2)),
                [0.0, 0.5, 1.0], m)
        skip_y = [(xc, w / 2 + 1.1) for xc, w, yd in chid.get(fy, ())]
        skip_x = [(-xc, w / 2 + 1.1) for xc, w, yd in chid.get(fx, ())]
        lines = []
        for x in K.even(-Xi + 0.4, Xi - 0.4, sp):
            if any(abs(x - a) < h for a, h in skip_y):
                lines.append([(x, Ye + 0.14), (x, Ye - 0.9)])
                continue
            if kd and abs(x) < kara[fy][0] / 2 + 0.5:
                lines.append([(x, Ye + 0.14)] + [(x, Ye - depth * t) for t in (0.0, 0.2, 0.4, 0.6, 0.8)] + [(x, Yi + 0.2)])
            else:
                lines.append([(x, Ye + 0.14), (x, Yi + 0.2)])
        K.ribs(mb, Fk, lines, zfy, 1, m, RIB_TRI)
        lines = []
        for y in K.even(-Yi + 0.4, Yi - 0.4, sp):
            if any(abs(y - a) < h for a, h in skip_x):
                lines.append([(Xe + 0.14, y), (Xe - 0.9, y)])
            else:
                lines.append([(Xe + 0.14, y), (Xi + 0.2, y)])
        K.ribs(mb, Fk, lines, base_x, 1, m, RIB_TRI)
        for sy in (1, -1):                                      # capas dos espigoes (ponta levantada)
            pts = [(Xe + 0.5, sy * (Ye + 0.5), base_y(Xe, Ye) + 0.5)] + \
                  [(Xe + (Xi - Xe) * u, sy * (Ye + (Yi - Ye) * u), base_y(Xe + (Xi - Xe) * u, Ye + (Yi - Ye) * u))
                   for u in (0.0, 0.5, 1.0)]
            K.sweep(mb, Fk, pts, [(a * 0.85, b * 0.85) for a, b in K.HIPP], RR)
            if oni:
                K.onigawara(mb, sub(Fk, pts[0][0], pts[0][1], 0.0, math.atan2(sy * 1.0, 1.0)), -0.1, pts[0][2] - 0.05,
                            1, 0.42, False)
        fascia(mb, Fk, -Xe + 0.4, Xe - 0.4, Ye - 0.3, zfy, tv, dense=((-kara[fy][0] / 2, kara[fy][0] / 2) if kd else None),
               second=second)
        Fs = sub(Fk, ang=-math.pi / 2)                          # a agua lateral (+x de Fk) vista como "frente"
        fascia(mb, Fs, -Ye + 0.4, Ye - 0.4, Xe - 0.3, lambda u, v: base_x(v, -u), tv, second=second)
        for sy in (1, -1):                                      # rincao (sumigi) sob o espigao
            beam(mb, Fk, (Xi + 0.4, sy * (Yi + 0.4), z_top - tv - 0.6),
                 (Xe + 0.2, sy * (Ye + 0.2), base_y(Xe, Ye) - tv - 0.3), 0.6, 0.62, WD)
        if kd:                                                  # timpano do karahafu + gegyo dourado
            w, rise = kara[fy]
            yv = Ye - 0.95
            xs = [(-w / 2) * 0.97 + w * 0.97 * i / 24 for i in range(25)]
            top = [(x, zfy(x, yv) - tv - 0.5) for x in xs]
            bot = [(x, base_y(x, yv) - tv - 0.5) for x in xs]
            poly = [p for p in bot] + [p for p in reversed(top)]
            ext(mb, Fk, poly, "y", yv - 0.25, yv, PL)
            for x in (-w * 0.22, w * 0.22):                     # montantes de madeira no timpano
                zt_ = zfy(x, yv) - tv - 0.5
                zb_ = base_y(x, yv) - tv - 0.5
                if zt_ - zb_ > 0.5:
                    bb(mb, Fk, x - 0.16, x + 0.16, yv - 0.05, yv + 0.1, zb_, zt_, WD)
            Fg = sub(Fk, 0.0, 0.0, 0.0, math.pi / 2)
            K._gegyo(mb, Fg, Ye - 0.3, zfy(0.0, Ye - 0.3) - tv - 0.62, 1, WD, 1.2, True)
    for sx in (-1, 1):                                          # rufo contra a parede de cima
        bb(mb, F, -Xi - 0.15, Xi + 0.15, sx * Yi - 0.12, sx * Yi + 0.3, z_top - 0.3, z_top + 0.3, WD)
        bb(mb, F, sx * Xi - 0.12, sx * Xi + 0.3, -Yi - 0.15, Yi + 0.15, z_top - 0.3, z_top + 0.3, WD)
    for key, Ff, ln, d in faces(F, Xi, Yi):                     # chidori-hafu
        for xc, w, yd in chid.get(key, ()):
            Xi_f, Yi_f = (Xi, Yi) if key in "FB" else (Yi, Xi)
            S = slope_for(Xi_f, Yi_f, depth, z_top, pitch)
            chidori(mb, sub(Ff, 0.0, -d, 0.0), S, tv, xc, w, yd, m, gold)
    return dict(base_y=base_y, base_x=base_x, Xe=Xe, Ye=Ye)


def chidori(mb, F, S, tv, xc, w, yd, m=RB, gold=False):
    """CHIDORI-HAFU leve (o K.chidori_gable do kit sem a trelica de ventilacao e com canais retos): 2 aguas que morrem
    na agua de baixo, tabeiras, triangulo de reboco recuado 0,2 com frechal e pendural escuros, gegyo, cumeeira com
    telha-ponteira na frente"""
    X, ov, pd = w / 2, 0.9, 0.62
    ze = S.zy(xc, yd) + 0.35
    zt = ze + pd * (X + ov)
    p = S.p
    yfront = yd + ov
    yback = lambda dx: S.Yw - (zt - pd * dx - S.zw) / p
    zf = lambda x, y: zt - pd * abs(x - xc)
    for sg in (-1, 1):
        q = [(xc + sg * (X + ov), yfront), (xc, yfront), (xc, yback(0.0) - 0.2), (xc + sg * (X + ov), yback(X + ov) - 0.2)]
        if sg > 0:
            q = [q[1], q[0], q[3], q[2]]
        K.sheet(mb, F, q, zf, tv * 0.8, 2, [0.0, 1.0], m)
        K.ribs(mb, F, [[(xc + sg * dx, yfront + 0.14), (xc + sg * dx, yback(dx) + 0.2)]
                       for dx in K.even(0.5, X + ov - 0.3, 1.6)], zf, 1, m, RIB_TRI)
        K.strip(mb, F, [(xc + sg * (X + ov) * u, yfront - 0.3, zf(xc + sg * (X + ov) * u, yfront) - tv * 0.8)
                        for u in (0.0, 1.0)], (0, 1, 0), -0.18, 0.18, -0.7, 0.08, WD)
    zbase = S.zy(xc, yd) - 0.15
    top = lambda x: zf(x, yd) - tv * 0.8 - 0.08
    Xi = X - 0.1
    while Xi > 0.5 and top(xc + Xi) < zbase + 0.3:
        Xi -= 0.1
    ext(mb, F, [(xc - Xi, zbase), (xc + Xi, zbase), (xc + Xi, top(xc + Xi)), (xc, top(xc)), (xc - Xi, top(xc - Xi))],
        "y", yd - 0.45, yd - 0.25, PL)
    bb(mb, F, xc - Xi * 0.8, xc + Xi * 0.8, yd - 0.27, yd - 0.09, zbase + 0.2, zbase + 0.75, WD)          # frechal
    bb(mb, F, xc - 0.2, xc + 0.2, yd - 0.27, yd - 0.09, zbase + 0.75, top(xc) - 0.05, WD)                # pendural
    Fg = sub(F, xc, 0.0, 0.0, math.pi / 2)
    K._gegyo(mb, Fg, yfront - 0.3, zt - tv * 0.8 - 0.7, 1, WD, 0.8, gold)
    y0, y1 = yback(0.0) - 0.4, yfront + 0.15
    Fr = sub(F, xc, 0.0, 0.0, math.pi / 2)
    hw = 0.7
    ext(mb, Fr, [(-hw, zt - pd * hw - 0.05), (0.0, zt - 0.05), (hw, zt - pd * hw - 0.05), (hw, zt + 0.45),
                 (-hw, zt + 0.45)], "x", y0, y1, RR)
    mb.rod(Fr.p(y0, 0.0, zt + 0.55), Fr.p(y1, 0.0, zt + 0.55), 0.3, RR, 6)
    ext(mb, Fr, [(-0.9, zt - 0.6), (0.9, zt - 0.6), (0.95, zt + 0.4), (0.6, zt + 1.15), (0.0, zt + 1.4), (-0.6, zt + 1.15),
                 (-0.95, zt + 0.4)], "x", y1 - 0.1, y1 + 0.3, RR)                                      # onigawara
    if gold:
        mb.rod(Fr.p(y1 + 0.2, 0.0, zt + 0.5), Fr.p(y1 + 0.5, 0.0, zt + 0.5), 0.36, GOLD, 8)


def cwin(mb, Ff, s, z, w, h, t=1.0, kind="dark", lod=0):
    """janela de castelo RECUADA: moldura escura 0,15 a frente do reboco, peitoril, barras brancas (renji) e fundo
    escuro ('dark', cenografica) ou papel aceso com kumiko visto de dentro ('hall', parede de espessura t)"""
    x0, x1 = s - w / 2, s + w / 2
    j = 0.32
    bb(mb, Ff, x0 - j, x0, -0.5, 0.15, z - 0.1, z + h + 0.1, WD)
    bb(mb, Ff, x1, x1 + j, -0.5, 0.15, z - 0.1, z + h + 0.1, WD)
    bb(mb, Ff, x0 - j, x1 + j, -0.5, 0.15, z + h, z + h + 0.34, WD)
    bb(mb, Ff, x0 - j - 0.15, x1 + j + 0.15, -0.5, 0.32, z - 0.34, z, WD)               # peitoril com pingadeira
    nb = max(3, int(round(w / (0.55 if lod == 0 else 0.8))))
    for i in range(1, nb):
        xx = x0 + w * i / nb
        bb(mb, Ff, xx - 0.12, xx + 0.12, -0.42, -0.2, z, z + h, PL)
    if kind == "dark":
        bb(mb, Ff, x0, x1, -0.86, -0.72, z, z + h, DARK)
    else:
        bb(mb, Ff, x0, x1, -t * 0.55 - 0.03, -t * 0.55 + 0.03, z, z + h, LIT)          # papel no meio da parede
        bb(mb, Ff, s - 0.06, s + 0.06, -t * 0.55 - 0.18, -t * 0.55 - 0.05, z, z + h, WD)          # kumiko em cruz
        bb(mb, Ff, x0, x1, -t * 0.55 - 0.18, -t * 0.55 - 0.05, z + h / 2 - 0.06, z + h / 2 + 0.06, WD)
        bb(mb, Ff, x0 - 0.3, x1 + 0.3, -t - 0.12, -t + 0.05, z - 0.3, z, WD)            # peitoril interno
        bb(mb, Ff, x0 - 0.3, x1 + 0.3, -t - 0.12, -t + 0.05, z + h, z + h + 0.3, WD)


def misulas(mb, Ff, ln, z, step):
    """misulas (cachorros) sob a viga de beiral: blocos com o pe chanfrado (ext de 4 pontos)"""
    for x in K.even(-ln / 2 + 0.8, ln / 2 - 0.8, step):
        ext(mb, Ff, [(0.0, z), (1.15, z), (1.15, z - 0.42), (0.0, z - 0.8)], "x", x - 0.22, x + 0.22, WD)


def tier_walls(mb, F, hx, hy, z0, ztop, t, wins, wz, ww, wh, kind="dark", hall_door=False, brackets=3.0, lod=0):
    """paredes de um andar: reboco (com os vaos) de z0 ate ztop[face] (sob o beiral), faixa escura de viga + misulas
    sob o beiral, janelas. wins = {face: [s, ...]}"""
    for key, Ff, ln, d in faces(F, hx, hy):
        side = key in "RL"
        a, b = (-ln / 2 + t, ln / 2 - t) if side else (-ln / 2, ln / 2)
        zt = ztop[key]
        holes = [(s - ww / 2, s + ww / 2, wz, wz + wh) for s in wins.get(key, ())]
        if hall_door and key == "F":
            holes.append((-DOOR_W / 2, DOOR_W / 2, -1.0, FLOOR + DOOR_H))
        K.panel(mb, Ff, a, b, z0, zt, -t, 0.0, holes, PL)
        for s in wins.get(key, ()):
            cwin(mb, Ff, s, wz, ww, wh, t, kind, lod)
        bb(mb, Ff, -ln / 2 - 0.25, ln / 2 + 0.25, -0.3, 0.25, zt - 1.25, zt, WD)        # viga de beiral (faixa)
        bb(mb, Ff, -ln / 2 - 0.2, ln / 2 + 0.2, -0.3, 0.2, zt - 2.6, zt - 2.25, WD)      # verga continua (nageshi)
        if brackets:
            misulas(mb, Ff, ln, zt - 1.25, brackets)


# ================================================================== base de cantaria
def corner_stack(mb, F, cx, cy, sx, sy, z_top, h, batter, key):
    """canto travado (sangi-zumi) de base em talude: 3 fiadas com o lado comprido alternado"""
    tb = math.tan(math.radians(batter))
    zs = [z_top - h * f for f in (0.0, 0.36, 0.7, 1.0)]
    for c in range(3):
        za, zb_ = zs[c + 1], zs[c]
        lx, ly = (2.8, 1.7) if c % 2 == 0 else (1.7, 2.8)

        def ring(z, g):
            o = (z_top - z) * tb
            X, Y = cx + sx * (o - g), cy + sy * (o - g)
            return [(X, Y, z), (X - sx * (lx + o), Y, z), (X - sx * (lx + o), Y - sy * (ly + o), z),
                    (X, Y - sy * (ly + o), z)]
        loft(mb, F, [ring(za + 0.04, 0.0), ring(zb_ - 0.04, 0.0)], ST if K._h01(key, c) > 0.3 else STD)


def ishigaki_box(mb, F, hx, hy, z_top, h, batter, key, gap=None):
    """base retangular de cantaria em talude (face no topo em +-hx/+-hy), 4 faces + cantos; gap = (x0, x1) aberto
    na frente (passagem da porta)"""
    for k, Ff, ln, d in faces(F, hx, hy):
        Lf = ln - 2 * 1.75
        spans = [(-Lf / 2, Lf / 2)]
        if gap and k == "F":
            spans = [(-Lf / 2, gap[0]), (gap[1], Lf / 2)]
        for a, b in spans:
            if b - a < 0.6:
                continue
            K.retaining_wall(mb, sub(Ff, (a + b) / 2, 0.0, z_top), b - a, h, batter, WALL, STP, "%s%s%.0f" % (key, k, a),
                             cap=True, z0=-0.4)
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner_stack(mb, F, sx * hx, sy * hy, sx, sy, z_top, h + 0.4, batter, (key, sx, sy))


# ================================================================== SHACHIHOKO
def shachi(mb, F, x, z, out, s=1.0):
    """SHACHIHOKO dourado na ponta da cumeeira (perfil no plano da cumeeira, lido de frente): CABECA grande e rombuda
    embaixo com a boca (fenda escura) virada para dentro, corpo grosso subindo em arco, cauda que volta para dentro e
    abre em V (2 lobos largos) - a silhueta de peixe vem da cabeca + V da cauda, nao de uma ponta afinada"""
    Fs = sub(F, x, 0.0, 0.0, 0.0 if out > 0 else math.pi)
    pts = [(-1.75, 1.05, 0.55), (-1.25, 1.1, 1.05), (-0.55, 1.35, 1.25), (0.1, 2.05, 1.2), (0.45, 3.0, 1.02),
           (0.38, 3.9, 0.82), (0.0, 4.55, 0.62), (-0.45, 4.9, 0.46)]
    pts = [(u * s, zz * s, r * s) for u, zz, r in pts]
    n = 10
    rings = []
    for i, (u, zz, r) in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        tu, tz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(tu, tz) or 1.0
        nu_, nz_ = -tz / ln, tu / ln
        rings.append([(u + r * math.cos(2 * math.pi * k / n) * nu_, 0.82 * r * math.sin(2 * math.pi * k / n),
                       z + zz + r * math.cos(2 * math.pi * k / n) * nz_) for k in range(n)])
    loft(mb, Fs, rings, GOLD)
    tu, tz = pts[-1][0], z + pts[-1][1]
    for ang, ln_ in ((math.radians(100.0), 2.3), (math.radians(168.0), 2.3)):     # cauda em V (2 lobos)
        dx, dz = math.cos(ang), math.sin(ang)
        px, pz = -dz, dx
        lobe = [(tu + px * 0.28 * s, tz + pz * 0.28 * s), (tu + (dx * ln_ * 0.55 + px * 0.6) * s, tz + (dz * ln_ * 0.55 + pz * 0.6) * s),
                (tu + dx * ln_ * s, tz + dz * ln_ * s), (tu + (dx * ln_ * 0.6 - px * 0.35) * s, tz + (dz * ln_ * 0.6 - pz * 0.35) * s),
                (tu - px * 0.28 * s, tz - pz * 0.28 * s)]
        ext(mb, Fs, lobe, "y", -0.14 * s, 0.14 * s, GOLD)
    u, zz, r = pts[4]                                       # dorsal unica (lado de fora do arco)
    ext(mb, Fs, [(u + r * 0.8, z + zz - 0.7 * s), (u + r + 0.9 * s, z + zz + 0.1 * s), (u + r * 0.8, z + zz + 0.55 * s)],
        "y", -0.1 * s, 0.1 * s, GOLD)
    u, zz, r = pts[2]
    for sy in (-1, 1):                                      # peitorais
        ext(mb, Fs, [(u - 0.2 * s, z + zz - 0.2 * s), (u + 0.9 * s, z + zz - 0.9 * s), (u + 0.6 * s, z + zz + 0.2 * s)],
            "y", sy * 0.95 * s, sy * 1.1 * s, GOLD)
    u, zz, r = pts[1]
    bb(mb, Fs, -2.3 * s, -1.2 * s, -0.42 * s, 0.42 * s, z + zz - 0.12 * s, z + zz + 0.02 * s, RR)        # boca
    for sy in (-1, 1):                                      # olhos
        lathe_y(mb, Fs, (u + 0.15 * s, sy * 0.78 * s, z + zz + 0.5 * s),
                [(0.26 * s, -0.1 * s * sy), (0.26 * s, 0.14 * sy * s)], 8, RR)
    bb(mb, Fs, -1.9 * s, 0.7 * s, -0.6 * s, 0.6 * s, z - 0.1, z + 0.55 * s, GOLD)


# ================================================================== TORRE
def keep(mb):
    F = keep_frame()
    hx0, hy0 = T[0][0], T[0][1]
    # ---- base de cantaria (talude) com a passagem da porta
    gap = (-DOOR_W / 2 - 1.1, DOOR_W / 2 + 1.1)
    ishigaki_box(mb, F, hx0 + 0.8, hy0 + 0.8, PLINTH, PLINTH, 20.0, "kp", gap)
    Ff = faces(F, hx0, hy0)[0][1]
    for s in (-1, 1):                                       # bochechas da passagem (pedra escura aparelhada)
        x = s * (DOOR_W / 2 + 0.55)
        bb(mb, Ff, x - 0.55, x + 0.55, -0.2, 2.5, -0.3, PLINTH + 0.2, ST)
        bb(mb, Ff, x - 0.7, x + 0.7, -0.2, 2.7, PLINTH + 0.2, PLINTH + 0.55, STP)
    bb(mb, Ff, -DOOR_W / 2 - 0.2, DOOR_W / 2 + 0.2, 0.0, 2.6, -0.3, 0.22, STP)            # degrau de pedra (kutsunugi)
    for k, Fw, ln, d in faces(F, hx0, hy0):                 # soleira escura sobre a cantaria (mizukiri)
        bb(mb, Fw, -ln / 2 - 0.2, ln / 2 + 0.2, -0.3, 0.3, PLINTH, PLINTH + 0.5, WD)
    # ---- alturas das paredes (sob o beiral de cada saia)
    tops = []
    for i, depth, zt in SKIRTS:
        hxn, hyn = T[i + 1][0], T[i + 1][1]
        hx, hy = T[i][0], T[i][1]
        f = zt - PITCH * (hy - hyn) - 0.5 + 0.25
        s_ = zt - PITCH * (hx - hxn) - 0.5 + 0.25
        tops.append({"F": f, "B": f, "R": s_, "L": s_})
    # ---- terreo: paredes de 2 (salao), janelas de papel aceso no salao, janelas escuras no meio-piso de cima
    wl = HALL_WINS
    lower = {k: MID_SKIRT[0] + 0.3 for k in "FBRL"}
    tier_walls(mb, F, hx0, hy0, 0.0, lower, 2.0, wl, 5.8, 3.0, 3.0, "hall", True, brackets=False)
    wu = {"F": [-22.0, -15.0, -7.5, 0.0, 7.5, 15.0, 22.0], "B": [-22.0, -11.0, 0.0, 11.0, 22.0],
          "R": [-16.0, -8.0, 0.0, 8.0, 16.0], "L": [-16.0, -8.0, 0.0, 8.0, 16.0]}
    for k, Fw, ln, d in faces(F, hx0, hy0):                 # meio-piso de cima do terreo (16 .. beiral)
        side = k in "RL"
        a, b = (-ln / 2 + 1.0, ln / 2 - 1.0) if side else (-ln / 2, ln / 2)
        zt = tops[0][k]
        K.panel(mb, Fw, a, b, MID_SKIRT[0] - 0.2, zt, -1.0, 0.0, [(s - 1.2, s + 1.2, 17.4, 19.6) for s in wu[k]], PL)
        for s in wu[k]:
            cwin(mb, Fw, s, 17.4, 2.4, 2.2, 1.0, "dark", 1)
        bb(mb, Fw, -ln / 2 - 0.25, ln / 2 + 0.25, -0.3, 0.25, zt - 1.25, zt, WD)
        misulas(mb, Fw, ln, zt - 1.25, 3.0)
    skirt(mb, F, hx0, hy0, MID_SKIRT[1], MID_SKIRT[0], 0.45, 0.42, 0.5, oni=False, sp=3.0)  # saia intermediaria do terreo
    # ---- alpendre de KARAHAFU dourado sobre a porta (pilares no patio, viga, consolos)
    Fp = faces(F, hx0, hy0)[0][1]
    kz = 11.9
    kr = K.roof_kara(mb, Fp, 12.4, 3.4, kz, 0.3, 1.7, 0.45, RB, True)
    yp = 3.15
    for s in (-1, 1):
        x = s * 5.5
        K.rock_base(mb, Fp, x, yp, 0.0, 0.85, 0.5)
        bb(mb, Fp, x - 0.36, x + 0.36, yp - 0.36, yp + 0.36, 0.3, 10.15, WD, 0.06)
        bb(mb, Fp, x - 0.42, x + 0.42, yp - 0.42, yp + 0.42, 0.3, 0.75, IRON)
        bb(mb, Fp, x - 0.45, x + 0.45, yp - 0.45, yp + 0.45, 9.6, 10.15, GOLD)
        beam(mb, Fp, (x, yp, 10.15), (x, 0.0, 10.15), 0.5, 0.6, WD)               # viga de amarracao na parede
    bb(mb, Fp, -6.2, 6.2, yp - 0.4, yp + 0.4, 10.15, 10.85, WD)                    # viga da frente
    bb(mb, Fp, -1.4, 1.4, yp + 0.38, yp + 0.52, 10.25, 10.75, GOLD)               # placa dourada (lisa, sem texto)
    # porta: caixilho, verga, folhas ABERTAS para dentro (madeira escura, cintas de ferro, cravos dourados)
    for s in (-1, 1):
        x = s * (DOOR_W / 2 + 0.3)
        bb(mb, Fp, x - 0.3, x + 0.3, -2.1, 0.2, FLOOR - 0.3, FLOOR + DOOR_H + 0.5, WD)
    bb(mb, Fp, -DOOR_W / 2 - 0.6, DOOR_W / 2 + 0.6, -2.1, 0.2, FLOOR + DOOR_H, FLOOR + DOOR_H + 0.7, WD)
    bb(mb, Fp, -DOOR_W / 2, DOOR_W / 2, -2.1, 0.0, -0.3, FLOOR, WD)                 # soleira (piso do vao)
    for s in (-1, 1):
        x = s * (DOOR_W / 2 - 0.2)
        y0, y1 = -2.1, -2.1 - DOOR_W / 2 + 0.2
        bb(mb, Fp, min(x, x - s * 0.36), max(x, x - s * 0.36), y1, y0, FLOOR + 0.05, FLOOR + DOOR_H - 0.1, WD)
        xf = x - s * 0.36                                   # face de dentro da folha (voltada para o eixo)
        for zz in (FLOOR + 1.2, FLOOR + DOOR_H / 2, FLOOR + DOOR_H - 1.3):
            bb(mb, Fp, min(xf, xf - s * 0.12), max(xf, xf - s * 0.12), y1 + 0.1, y0 - 0.1, zz - 0.18, zz + 0.18, IRON)
            for yy in K.even(y1 + 0.3, y0 - 0.3, 0.9):
                bb(mb, Fp, min(xf, xf - s * 0.22), max(xf, xf - s * 0.22), yy - 0.09, yy + 0.09, zz - 0.09, zz + 0.09, GOLD)
    # ---- andares 1..3 (paredes de 1, cenograficos)
    wins = [None,
            {"F": [-16.0, -5.5, 5.5, 16.0], "B": [-16.0, -5.5, 5.5, 16.0], "R": [-12.0, -4.0, 4.0, 12.0],
             "L": [-12.0, -4.0, 4.0, 12.0]},
            {"F": [-11.0, -3.7, 3.7, 11.0], "B": [-11.0, 0.0, 11.0], "R": [-8.0, 0.0, 8.0], "L": [-8.0, 0.0, 8.0]},
            {"R": [-5.0, 0.0, 5.0], "L": [-5.0, 0.0, 5.0]}]
    wzs = [None, 29.6, 46.6, 61.4]
    for i in (1, 2):
        hx, hy, z0, hw, over = T[i]
        tier_walls(mb, F, hx, hy, z0 - 0.6, tops[i], 1.0, wins[i], wzs[i], 2.6, 2.4, brackets=(3.0 if i == 1 else 0),
                   lod=1)
    # ---- saias com chidori / karahafu
    chid0 = {"F": [(-11.5, 11.0, hy0), (11.5, 11.0, hy0)], "B": [(0.0, 15.0, hy0)],
             "R": [(0.0, 15.0, hx0)], "L": [(0.0, 15.0, hx0)]}
    skirt(mb, F, T[1][0], T[1][1], SKIRTS[0][1], SKIRTS[0][2], chid=chid0, sp=2.6)
    chid1 = {"F": [(0.0, 15.0, T[1][1])], "B": [(0.0, 15.0, T[1][1])]}
    skirt(mb, F, T[2][0], T[2][1], SKIRTS[1][1], SKIRTS[1][2], chid=chid1, sp=2.8, oni=False, second=False)
    chid2 = {"R": [(0.0, 9.0, T[2][0])], "L": [(0.0, 9.0, T[2][0])]}
    skirt(mb, F, T[3][0], T[3][1], SKIRTS[2][1], SKIRTS[2][2], chid=chid2, kara={"F": (13.0, 2.3), "B": (13.0, 2.3)},
          gold=True, sp=2.8, oni=False, second=False)
    # ---- 4o andar: paredes, portas de correr para a varanda, VARANDA VERMELHA em volta, telhado irimoya
    hx3, hy3, z03, hw3, over3 = T[3]
    h3 = z03 + hw3
    zb = SKIRTS[2][2] + 0.75                                # piso da varanda
    t3 = {k: h3 for k in "FBRL"}
    doors = {"F": [-4.2, 4.2], "B": [-4.2, 4.2]}
    for k, Fw, ln, d in faces(F, hx3, hy3):
        side = k in "RL"
        a, b = (-ln / 2 + 1.0, ln / 2 - 1.0) if side else (-ln / 2, ln / 2)
        holes = [(s - 1.3, s + 1.3, wzs[3], wzs[3] + 2.4) for s in wins[3].get(k, ())]
        holes += [(s - 2.1, s + 2.1, zb - 0.1, zb + 5.6) for s in doors.get(k, ())]
        K.panel(mb, Fw, a, b, z03 - 0.6, h3, -1.0, 0.0, holes, PL)
        for s in wins[3].get(k, ()):
            cwin(mb, Fw, s, wzs[3], 2.6, 2.4)
        for s in doors.get(k, ()):                         # portas de correr para a varanda (caixilho + 2 folhas)
            z0d = zb + 0.05
            bb(mb, Fw, s - 2.1, s - 1.8, -0.9, 0.1, z0d, z0d + 5.4, WD)
            bb(mb, Fw, s + 1.8, s + 2.1, -0.9, 0.1, z0d, z0d + 5.4, WD)
            bb(mb, Fw, s - 2.1, s + 2.1, -0.9, 0.1, z0d + 5.0, z0d + 5.6, WD)
            for a_, y_ in ((-1.8, -0.62), (0.0, -0.42)):
                bb(mb, Fw, s + a_, s + a_ + 1.8, y_ - 0.08, y_ + 0.08, z0d, z0d + 5.0, WD)
                bb(mb, Fw, s + a_ + 0.25, s + a_ + 1.55, y_ - 0.16, y_ - 0.06, z0d + 1.4, z0d + 4.7, PL)
                bb(mb, Fw, s + a_ + 0.84, s + a_ + 0.96, y_ - 0.2, y_ - 0.08, z0d + 1.4, z0d + 4.7, WD)
        bb(mb, Fw, -ln / 2 - 0.25, ln / 2 + 0.25, -0.3, 0.25, h3 - 1.0, h3, WD)
    # varanda: piso de tabuas em consolos sobre a saia, viga de borda, guarda-corpo vermelho fechado
    dep = 2.7
    Xb, Yb = hx3 + dep, hy3 + dep
    ring = [(-Xb, -Yb), (Xb, -Yb), (Xb, Yb), (-Xb, Yb)]
    for k, Fw, ln, d in faces(F, hx3, hy3):
        bb(mb, Fw, -ln / 2 - dep, ln / 2 + dep, 0.0, dep, zb - 0.32, zb, WM)
        bb(mb, Fw, -ln / 2 - dep, ln / 2 + dep, dep - 0.45, dep, zb - 0.8, zb - 0.3, WD)
        for x in K.even(-ln / 2 + 0.6, ln / 2 - 0.6, 3.4):
            ext(mb, Fw, [(-0.2, zb - 0.3), (dep - 0.1, zb - 0.3), (dep - 0.1, zb - 0.8), (-0.2, zb - 1.5)], "x", x - 0.2,
                x + 0.2, WD)
    K.red_rail(mb, F, ring + [ring[0]], 3.2, zb, 4.4)
    rinfo = K.roof_hip(mb, F, 2 * hx3, 2 * hy3, h3, "irimoya", 0.55, over3, 0.66, 1.4, 1.4, 0.55, 1, PL, "timber",
                       False, RB, 1.5, None, dict(x=0.0, w=8.0), True)
    xs = rinfo["xg"] + rinfo["go"] - 0.4
    for s in (-1, 1):
        shachi(mb, F, s * xs, rinfo["top"] - 2.6, s, 1.05)
    return F


def keep_cols():
    F = keep_frame()
    hx0, hy0 = T[0][0], T[0][1]
    for k, Fw, ln, d in faces(F, hx0, hy0):                 # paredes do terreo (porta aberta na frente)
        side = k in "RL"
        a, b = (-ln / 2 + 2.0, ln / 2 - 2.0) if side else (-ln / 2, ln / 2)
        spans = [(a, -DOOR_W / 2), (DOOR_W / 2, b)] if k == "F" else [(a, b)]
        for x0, x1 in spans:
            p = Fw.p((x0 + x1) / 2, -1.0, 11.5)
            col_box("OP_CasKeep", (x1 - x0, 2.0, 23.0), p, Fw.r())
        if k == "F":
            p = Fw.p(0.0, -1.0, (FLOOR + DOOR_H + 23.0) / 2)
            col_box("OP_CasKeep", (DOOR_W, 2.0, 23.0 - FLOOR - DOOR_H), p, Fw.r())
            # base de pedra da frente (fora), com a passagem
            for s in (-1, 1):
                x0, x1 = (DOOR_W / 2 + 0.0, hx0 + 2.4) if s > 0 else (-hx0 - 2.4, -DOOR_W / 2)
                col_box("OP_CasKeep", (x1 - x0, 2.4, PLINTH), Fw.p((x0 + x1) / 2, 1.2, PLINTH / 2), Fw.r())
        else:
            col_box("OP_CasKeep", (ln + 4.8, 2.4, PLINTH), Fw.p(0.0, 1.2, PLINTH / 2), Fw.r())
    col_box("OP_CasKeepCeil", (2 * hx0 - 4.0, 2 * hy0 - 4.0, 0.8), F.p(0, 0, 12.85), F.r())
    # piso do salao (+0,45) incluindo o vao da porta
    col_box("OP_CasHall", (2 * hx0 - 4.0, 2 * hy0 - 2.0, 0.95), F.p(0, 1.0, FLOOR - 0.475), F.r())
    col_box("OP_CasHall", (DOOR_W + 0.8, 2.6, 0.52), F.p(0, hy0 + 1.3, 0.22 - 0.26), F.r())
    # andares de cima (caixas)
    col_box("OP_CasKeepUpper", (2 * hx0, 2 * hy0, 10.0), F.p(0, 0, 13.25 + 5.0), F.r())
    for i in (1, 2, 3):
        hx, hy, z0, hw, over = T[i]
        col_box("OP_CasKeepUpper", (2 * hx, 2 * hy, hw + 4.0), F.p(0, 0, z0 - 1.0 + (hw + 4.0) / 2), F.r())
    # alpendre: pilares
    Fp = faces(F, hx0, hy0)[0][1]
    for s in (-1, 1):
        col_box("OP_CasKeep", (1.4, 1.4, 10.2), Fp.p(s * 5.5, 3.15, 5.1), Fp.r())
    # folhas da porta abertas (para dentro)
    for s in (-1, 1):
        col_box("OP_CasHall", (0.5, DOOR_W / 2, DOOR_H), Fp.p(s * (DOOR_W / 2 - 0.38), -2.1 - DOOR_W / 4 + 0.1,
                                                            FLOOR + DOOR_H / 2), Fp.r())


# ================================================================== SALAO (terreo acessivel)
HALL_WINS = {"F": [-17.0, -10.0, 10.0, 17.0], "B": [-16.0, -5.5, 5.5, 16.0], "R": [-14.0, -4.7, 4.7, 14.0],
             "L": [-14.0, -4.7, 4.7, 14.0]}
HALL_COLS = [(sx * 15.0, y) for sx in (-1, 1) for y in (-10.0, 0.0, 10.0)]
HALL_LIGHTS = [("L_OPCas_Hall_1", (0.0, 9.0)), ("L_OPCas_Hall_2", (-12.0, -6.0)), ("L_OPCas_Hall_3", (12.0, -6.0))]


def hall(mb):
    F = keep_frame()
    hx0, hy0 = T[0][0], T[0][1]
    X, Y = hx0 - 2.0, hy0 - 2.0
    zc = 12.45                                              # teto
    # piso de tabuas (junta rebaixada pelo chanfro) com moldura escura
    bw = 1.3
    n = int((2 * X - 1.2) / bw)
    w = (2 * X - 1.2) / n
    for i in range(n):
        x0 = -X + 0.6 + i * w
        poly = [F.p(x0, -Y + 0.6), F.p(x0 + w, -Y + 0.6), F.p(x0 + w, Y), F.p(x0, Y)]
        K.slab_poly(mb, ccw([(p.x, p.y) for p in poly]), CC + FLOOR - 0.35, CC + FLOOR, 0.05, WM, sides=False)
    bb(mb, F, -X, X, -Y, -Y + 0.6, FLOOR - 0.35, FLOOR + 0.05, WD)
    for s in (-1, 1):
        bb(mb, F, s * X - (0.6 if s > 0 else 0.0), s * X + (0.6 if s < 0 else 0.0), -Y, Y, FLOOR - 0.35, FLOOR + 0.05, WD)
    # estrado (jodan) ao fundo: tablado 0,75, viga de borda, biombos dourados, rolo com o brasao
    yd0, yd1 = -Y, -Y + 7.0
    zd = FLOOR + 0.75
    bb(mb, F, -13.0, 13.0, yd0, yd1, FLOOR - 0.1, zd - 0.12, WM)
    bb(mb, F, -13.4, 13.4, yd1 - 0.55, yd1 + 0.05, FLOOR - 0.1, zd + 0.02, WD)
    for x in K.even(-12.6, 12.6, 1.4):
        bb(mb, F, x - 0.66, x + 0.66, yd0 + 0.05, yd1 - 0.6, zd - 0.12, zd - 0.02, WM)
    for s in (-1, 1):                                       # biombos de 6 folhas em zigue-zague
        x0 = s * 3.4
        for k in range(6):
            xa = x0 + s * k * 1.45
            yy = yd0 + 1.4 + (0.45 if k % 2 else 0.0)
            yb_ = yd0 + 1.4 + (0.0 if k % 2 else 0.45)
            xb_ = xa + s * 1.45
            p0, p1 = (xa, yy), (xb_, yb_)
            ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
            Fb = sub(F, (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, 0.0, ang)
            bb(mb, Fb, -ln / 2, ln / 2, -0.06, 0.06, zd + 0.3, zd + 4.4, GOLD)
            bb(mb, Fb, -ln / 2, ln / 2, -0.1, 0.1, zd + 4.4, zd + 4.65, WD)
            bb(mb, Fb, -ln / 2, ln / 2, -0.1, 0.1, zd + 0.05, zd + 0.3, WD)
            bb(mb, Fb, ln / 2 - 0.08, ln / 2 + 0.08, -0.11, 0.11, zd + 0.05, zd + 4.65, WD)
    # tokonoma: moldura escura saliente na parede do fundo, rolo branco com o brasao (sem texto)
    Fb = faces(F, X, Y)[1][1]                               # face interna do fundo, +y = para fora (-y local)
    Fi = sub(Fb, 0.0, 0.0, 0.0, math.pi)                    # +y = para dentro do salao
    for s in (-1, 1):
        bb(mb, Fi, s * 2.6 - 0.35, s * 2.6 + 0.35, 0.0, 0.8, zd, 10.5, WD)
    bb(mb, Fi, -2.95, 2.95, 0.0, 0.8, 9.9, 10.6, WD)
    bb(mb, Fi, -2.25, 2.25, 0.0, 0.25, zd, 9.9, "Plaster_OP_Warm")
    bb(mb, Fi, -1.1, 1.1, 0.25, 0.37, 3.1, 8.9, CWHITE)
    bb(mb, Fi, -1.25, 1.25, 0.2, 0.45, 8.9, 9.2, WD)
    bb(mb, Fi, -1.25, 1.25, 0.2, 0.45, 2.85, 3.1, WD)
    crest(mb, sub(Fi, 0.0, 0.33, 0.0), 0.0, 6.6, 0.8, INDIGO, 0.14)
    # pilares (com pedra-base, consolo em cima) e vigas-mestras sob o teto
    for x, y in HALL_COLS:
        K.rock_base(mb, F, x, y, FLOOR - 0.1, 1.1, 0.35)
        bb(mb, F, x - 0.62, x + 0.62, y - 0.62, y + 0.62, FLOOR, zc - 0.9, WD, 0.06)
        bb(mb, F, x - 1.6, x + 1.6, y - 0.5, y + 0.5, zc - 1.45, zc - 0.9, WD)      # consolo (sashi-hijiki)
    for s in (-1, 1):
        bb(mb, F, s * 15.0 - 0.55, s * 15.0 + 0.55, -Y, Y, zc - 0.9, zc, WD)
    # teto em caixotoes: forro claro + grelha escura
    bb(mb, F, -X, X, -Y, Y, zc, zc + 0.4, "Plaster_OP_Warm")
    for x in K.even(-X, X, 4.4)[:-1]:
        xx = x + (2 * X / len(K.even(-X, X, 4.4))) / 2
        bb(mb, F, xx - 0.22, xx + 0.22, -Y, Y, zc - 0.45, zc, WD)
    for y in K.even(-Y, Y, 4.2)[:-1]:
        yy = y + (2 * Y / len(K.even(-Y, Y, 4.2))) / 2
        bb(mb, F, -X, X, yy - 0.22, yy + 0.22, zc - 0.45, zc, WD)
    # paredes internas: rodape de tabuas, nageshi, pilares embutidos entre as janelas
    for k, Fw, ln, d in faces(F, X, Y):
        Fi = sub(Fw, 0.0, 0.0, 0.0, math.pi)                # +y para dentro
        spans = [(-ln / 2, -DOOR_W / 2 - 0.3), (DOOR_W / 2 + 0.3, ln / 2)] if k == "F" else [(-ln / 2, ln / 2)]
        for a, b in spans:                                  # rodape de tabuas (aberto na porta)
            bb(mb, Fi, a, b, 0.0, 0.25, FLOOR, FLOOR + 1.6, WM)
            bb(mb, Fi, a, b, 0.0, 0.35, FLOOR + 1.6, FLOOR + 1.85, WD)
        bb(mb, Fi, -ln / 2, ln / 2, 0.0, 0.32, 9.6, 10.15, WD)
        bb(mb, Fi, -ln / 2, ln / 2, 0.0, 0.3, zc - 0.7, zc, WD)
        ws = HALL_WINS[k]
        ws = sorted(-s for s in ws)                         # Fi espelha x
        stops = [-ln / 2 + 0.4] + ws + [ln / 2 - 0.4]
        if k == "F":
            stops = sorted(stops + [-DOOR_W / 2 - 1.6, DOOR_W / 2 + 1.6])
        posts = set()
        for a, b in zip(stops, stops[1:]):
            m_ = (a + b) / 2
            if k == "F" and abs(m_) < DOOR_W / 2 + 0.8:
                continue
            posts.add(round(m_, 2))
        for x in sorted(posts):
            bb(mb, Fi, x - 0.4, x + 0.4, 0.0, 0.42, FLOOR, zc - 0.7, WD)
    # lanternas de papel penduradas (fonte visivel das 3 luzes do salao)
    for nm, (x, y) in HALL_LIGHTS:
        z = zc - 0.45
        mb.rod(F.p(x, y, z), F.p(x, y, z - 1.6), 0.06, IRON, 6)
        c = K.chochin(mb, F, (x, y, z - 1.6 - 2.3), 0.95, 2.3, CWHITE)
        light(nm, "POINT", F.p(x, y, 7.4), 260.0, WARM, 0.5)


def hall_cols():
    F = keep_frame()
    for x, y in HALL_COLS:
        col_box("OP_CasHall", (1.4, 1.4, 12.0), F.p(x, y, 6.0), F.r())
    Y = T[0][1] - 2.0
    col_box("OP_CasHall", (26.8, 7.6, 0.85), F.p(0.0, -Y + 3.5, FLOOR + 0.425 - 0.1), F.r())
    for s in (-1, 1):
        col_box("OP_CasHall", (9.4, 1.4, 4.7), F.p(s * 7.8, -Y + 1.6, FLOOR + 0.75 + 2.35), F.r())


# ================================================================== BRASAO (anel + 8 petalas + miolo)
def crest(mb, Ff, x, z, R, m=INDIGO, th=0.1):
    """brasao circular da ilha no plano x-z do referencial (sai th para +y): anel, 8 petalas, miolo"""
    n = 18
    ro, ri = R, R * 0.8
    rings = []
    for rr, yy in ((ro, -th), (ro, th), (ri, th), (ri, -th)):
        rings.append([(x + rr * math.cos(2 * math.pi * j / n), yy, z + rr * math.sin(2 * math.pi * j / n)) for j in range(n)])
    rings.append(rings[0])
    loft(mb, Ff, rings, m, caps=(False, False))
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        cx, cz = x + R * 0.5 * math.cos(a), z + R * 0.5 * math.sin(a)
        poly = []
        for j in range(8):
            t = 2 * math.pi * j / 8
            u, v = R * 0.2 * math.cos(t), R * 0.12 * math.sin(t)
            poly.append((cx + u * math.cos(a) - v * math.sin(a), cz + u * math.sin(a) + v * math.cos(a)))
        ext(mb, Ff, poly, "y", -th, th, m)
    lathe_y(mb, Ff, (x, 0.0, z), [(R * 0.16, -th), (R * 0.16, th)], 10, m)


# ================================================================== PATIO
def dobei(mb, pts, z, h=4.6, key="db", sama=True):
    """muro de reboco (dobei) sobre soco de pedra, capa de telha de 2 aguas com canais e cumeeira, seteiras quadradas
    VAZADAS; pts = polilinha (mundo)"""
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            continue
        Fs = Frame(a[0], a[1], z, math.atan2(dy, dx))
        bb(mb, Fs, -0.3, ln + 0.3, -0.95, 0.95, -0.4, 1.0, ST)
        bb(mb, Fs, -0.3, ln + 0.3, -1.05, 1.05, 0.9, 1.15, STP)
        holes = []
        if sama and ln > 4.0:
            for x in K.even(1.6, ln - 1.6, 3.6):
                holes.append((x - 0.34, x + 0.34, 2.7, 3.38))
        K.panel(mb, Fs, 0.0, ln, 1.15, h, -0.6, 0.6, holes, PL)
        bb(mb, Fs, -0.2, ln + 0.2, -0.75, 0.75, h - 0.5, h, WD)
        zf = lambda x, y: h + 1.05 - 0.55 * abs(y)
        for sy in (1, -1):
            K.sheet(mb, Fs, [(-0.4, sy * 1.55), (ln + 0.4, sy * 1.55), (ln + 0.4, 0.0), (-0.4, 0.0)] if sy > 0 else
                    [(ln + 0.4, sy * 1.55), (-0.4, sy * 1.55), (-0.4, 0.0), (ln + 0.4, 0.0)], zf, 0.28,
                    max(1, int(ln / 6)), [0.0, 1.0], RB)
            K.ribs(mb, Fs, [[(x, sy * 1.66), (x, sy * 0.2)] for x in K.even(-0.2, ln + 0.2, 2.8)], zf, 1, RB, RIB_TRI)
            K.strip(mb, Fs, [(x, sy * 1.4, zf(x, 1.4) - 0.28) for x in (-0.4, ln + 0.4)], (0, sy, 0), -0.14, 0.14, -0.4,
                    0.02, WD)
        bb(mb, Fs, -0.4, ln + 0.4, -0.32, 0.32, h + 0.85, h + 1.35, RR)
        mb.rod(Fs.p(-0.4, 0.0, h + 1.45), Fs.p(ln + 0.4, 0.0, h + 1.45), 0.22, RR, 6)


def simple_base(mb, F, hb, z_top, z_bot, batter, key):
    """base de cantaria barata (torreoes, longe do jogador): talude em 3 fiadas com junta recuada 0,12 + capa +
    cantos travados"""
    tb = math.tan(math.radians(batter))
    zs = [z_top - 0.4, z_top - 0.4 - (z_top - z_bot) * 0.36, z_top - 0.4 - (z_top - z_bot) * 0.7, z_bot]
    ring = lambda o, z: [(sx * (hb + o), sy * (hb + o), z) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for c in range(3):
        za, zb_ = zs[c + 1] + 0.06, zs[c] - 0.06
        o0, o1 = (z_top - za) * tb - 0.12, (z_top - zb_) * tb - 0.12
        loft(mb, F, [ring(o0, za), ring(o1, zb_)], WALL if c % 2 == 0 else ST)
        loft(mb, F, [ring(o0 - 0.12, za - 0.08), ring(o0 - 0.12, za + 0.08)], STD) if c < 2 else None
    bb(mb, F, -hb - 0.1, hb + 0.1, -hb - 0.1, hb + 0.1, z_top - 0.4, z_top, STP)
    for sx in (-1, 1):
        for sy in (-1, 1):
            corner_stack(mb, F, sx * hb, sy * hb, sx, sy, z_top - 0.4, z_top - 0.4 - z_bot, batter, (key, sx, sy))


def mini_roof(mb, F, hl, hd, z, pitch=0.6, tv=0.3):
    """telhadinho de 2 aguas (pilares de apoio do portao): 2 placas com telha, cumeeira e testeira"""
    zf = lambda x, y: z + pitch * (hd - abs(y))
    for sy in (1, -1):
        K.sheet(mb, F, [(-hl, sy * hd), (hl, sy * hd), (hl, 0.0), (-hl, 0.0)], zf, tv, 2, [0.0, 1.0], RB)
        K.strip(mb, F, [(x, sy * (hd - 0.2), zf(x, hd - 0.2) - tv) for x in (-hl, hl)], (0, sy, 0), -0.12, 0.12, -0.35,
                0.02, WD)
    bb(mb, F, -hl - 0.1, hl + 0.1, -0.3, 0.3, zf(0, 0) - 0.1, zf(0, 0) + 0.4, RR)


def turret(mb, cx, cy, ang, s, z_bot, key, big=True):
    """yagura de canto (2 andares no SE, 1 no SO) sobre base de cantaria que desce pela rocha"""
    F = Frame(cx, cy, CC, ang)
    hb = s / 2 + 0.8
    simple_base(mb, F, hb, 1.0, z_bot, 18.0, key)
    h1 = 8.0
    zt1 = 1.0 + h1
    if big:
        s2 = s - 4.0
        skz = zt1 + 0.5 + 2.0 + 0.6
        dep = (s - s2) / 2 + 2.6
        ftop = skz - PITCH * (s / 2 - s2 / 2) - 0.5 + 0.25
        tier_walls(mb, F, s / 2, s / 2, 0.5, {k: ftop for k in "FBRL"}, 1.0,
                   {k: [0.0] for k in "FBRL"}, 4.4, 3.6, 2.0, brackets=False, lod=1)
        skirt(mb, F, s2 / 2, s2 / 2, dep, skz, chid={"F": [(0.0, 6.0, s / 2)]}, sp=3.0, oni=False, second=False)
        h2 = skz + 5.2
        tier_walls(mb, F, s2 / 2, s2 / 2, skz - 0.6, {k: h2 for k in "FBRL"}, 1.0, {k: [0.0] for k in "FBRL"},
                   skz + 1.6, 2.0, 1.8, brackets=False, lod=1)
        K.roof_hip(mb, F, s2, s2 + 0.01, h2, "irimoya", 0.6, 2.8, 0.6, 1.2, 1.2, 0.5, 1, PL, "timber", False, RB)
    else:
        h2 = zt1 + 1.2
        tier_walls(mb, F, s / 2, s / 2, 0.5, {k: h2 for k in "FBRL"}, 1.0, {k: [0.0] for k in "FBRL"}, 4.4, 3.2,
                   2.0, brackets=False, lod=1)
        dep = s / 2 + 2.4 - 0.6
        zt = h2 + 0.5 + 0.62 * dep
        skirt(mb, F, 0.6, 0.6, dep, zt, 0.62, 0.45, 0.9, sp=2.6, oni=False, second=False)
        lathe(mb, F, (0.0, 0.0, zt - 0.3), [(1.0, 0.0), (1.0, 0.5), (0.55, 0.8), (0.62, 1.3), (0.3, 1.9), (0.06, 2.5)], 8,
              RR)
        h2 = zt
    col_box("OP_CasTurret", (s, s, h2 + 2.0), F.p(0, 0, (h2 + 2.0) / 2), F.r())
    return F


def koraimon(mb, cx, cy, ang, span, h, red=False, z=CC, key="kg", plaque=False, hikae=True):
    """portao com 2 pilares principais, 2 pilares de apoio atras com telhadinhos (koraimon), viga (kabuki) que passa
    dos pilares, travessa (nuki), telhado de 2 aguas com onigawara; pilares sobre pedra com cinta de ferro"""
    F = Frame(cx, cy, z, ang)                               # +y = frente (de onde se chega)
    pm = LAC if red else WD
    cw = 2.3 if red else 1.5
    back = 3.2 if red else 3.0
    xs = span / 2 + cw / 2
    for s in (-1, 1):
        x = s * xs
        K.rock_base(mb, F, x, 0.0, 0.0, cw * 0.95, 0.6)
        bb(mb, F, x - cw / 2, x + cw / 2, -cw / 2, cw / 2, 0.4, h, pm, 0.06)
        bb(mb, F, x - cw / 2 - 0.08, x + cw / 2 + 0.08, -cw / 2 - 0.08, cw / 2 + 0.08, 0.4, 1.4, IRON)
        if red:
            bb(mb, F, x - cw / 2 - 0.08, x + cw / 2 + 0.08, -cw / 2 - 0.08, cw / 2 + 0.08, h - 2.6, h - 2.2, GOLD)
        if not hikae:
            continue
        # pilar de apoio + travessas + telhadinho perpendicular
        xb_ = s * (xs + (0.6 if red else 0.4))
        K.rock_base(mb, F, xb_, -back, 0.0, cw * 0.7, 0.5)
        bb(mb, F, xb_ - cw * 0.32, xb_ + cw * 0.32, -back - cw * 0.32, -back + cw * 0.32, 0.3, h * 0.66, pm, 0.05)
        for zz in (h * 0.3, h * 0.6):
            beam(mb, F, (x, 0.0, zz), (xb_, -back, zz), 0.36, 0.42, pm)
        Fr = sub(F, (x + xb_) / 2, -back / 2, 0.0, math.pi / 2)
        mini_roof(mb, Fr, (back + cw + 1.6) / 2, cw * 0.5 + 0.9, h * 0.66 + 0.15)
    # kabuki (viga de cabeca) e nuki
    zk = h - 1.8
    bb(mb, F, -xs - cw * 1.2, xs + cw * 1.2, -0.75, 0.75, zk, zk + 1.6, pm)
    bb(mb, F, -xs, xs, -0.4, 0.4, zk - 3.0, zk - 2.3, pm)
    for x in (-span * 0.22, span * 0.22):
        bb(mb, F, x - 0.35, x + 0.35, -0.3, 0.3, zk - 2.3, zk, pm)
    if red:
        for s in (-1, 1):                                   # remates dourados nas pontas da viga
            bb(mb, F, s * (xs + cw * 1.2) - 0.25 * s - 0.25, s * (xs + cw * 1.2) - 0.25 * s + 0.25, -0.8, 0.8, zk - 0.05,
               zk + 1.65, GOLD)
    if plaque:
        crest(mb, sub(F, 0.0, 0.75, 0.0), 0.0, zk + 0.8, 1.0, GOLD, 0.12)
    # telhado principal (kirizuma) sobre a viga
    K.roof_gable(mb, F, 2 * (xs + cw * 1.2) + 1.0, 3.6 if red else 2.6, h, 0.62, 2.6 if red else 1.8,
                 1.6 if red else 1.0, 0.8, 0.5, 1, WD, "board", False, RB, 0.6, 1.6, 1.0, None, red)
    return F, xs, cw, back


def court(mb):
    rng = random.Random(4602)
    # muro dobei: flanco da subida (x = -64), oeste e fundo, ate a base da arvore
    gx, gw = L.COURT_GATE[0], L.COURT_GATE[2]
    xs = gw / 2 + 0.75
    wl = [(-63.4, COURT_GATE_Y), (-63.4, 381.5)]
    dobei(mb, wl, CC, 4.6, "dbW")
    wn = [(gx - xs, COURT_GATE_Y), (gx - xs, 437.0), (-89.3, 437.0), (-89.3, 469.2), (-40.0, 473.3), (20.0, 475.3), WALL_N_END]
    dobei(mb, wn, CC, 4.6, "dbN", sama=False)
    we = [(63.6, 370.6), (65.6, 373.6), (WALL_E_END[0], WALL_E_END[1])]
    dobei(mb, we, CC, 4.6, "dbE", sama=False)
    for p in (wn[2], wn[3], wn[4], wn[5], we[1], wl[1]):           # pilares de canto (cobrem as juntas)
        bb(mb, Frame(p[0], p[1], CC, 0.0), -1.0, 1.0, -1.0, 1.0, -0.3, 5.0, PL)
        bb(mb, Frame(p[0], p[1], CC, 0.0), -1.2, 1.2, -1.2, 1.2, -0.3, 1.2, ST)
    for p in (wn[-1], we[-1]):                              # terminal junto da base da arvore: pilar de pedra
        bb(mb, Frame(p[0], p[1], CC, 0.0), -1.0, 1.0, -1.0, 1.0, -0.3, 3.4, ST)
    # portao do patio (koraimon escuro) no topo da CasteloB, voltado para a escada (sul)
    F, xs_, cw, back = koraimon(mb, gx, COURT_GATE_Y, math.pi, gw, 11.0, False, CC, "kgP")
    for s in (-1, 1):
        col_box("OP_CasCourtGate", (cw + 0.4, cw + 0.4, 11.0), F.p(s * xs_, 0.0, 5.5), F.r())
        col_box("OP_CasCourtGate", (1.4, 1.4, 7.3), F.p(s * (xs_ + 0.4), -back, 3.6), F.r())
    # torreoes de canto da proa
    ang_e = math.atan2(372.0 - 358.0, 66.0 - 50.0)
    turret(mb, SE_TURRET[0], SE_TURRET[1], ang_e - math.pi, SE_TURRET[2], -9.4, "ySE", True)
    ang_w = math.atan2(358.0 - 376.0, -50.0 - (-64.0))
    turret(mb, SW_TURRET[0], SW_TURRET[1], ang_w + math.pi, SW_TURRET[2], -13.0, "ySW", False)
    # GUARDA-CORPO VERMELHO do mirante (borda da proa), entre os 2 torreoes
    rail = [RAIL_W, (-49.4, 358.8), (-24.0, 352.8), (24.0, 352.8), (49.4, 358.8), RAIL_E]
    K.red_rail(mb, Frame(0.0, 0.0, CC, 0.0), rail, 3.6, 0.0, 4.2)
    # toro de pedra no caminho da porta
    for i, x in enumerate((-12.0, 12.0)):
        K.toro(mb, Frame(x, 375.0, CC, 0.0), 1.05, "L_OPProp_Lamp_Cas_Toro_%d" % i, 35.0)
        col_box("OP_CasLamp", (3.0, 3.0, 8.0), (x, 375.0, CC + 4.0))


WALL_N_END = (60.0, 468.0)   # muro do fundo: termina ENCOSTADO na raiz NNE da arvore (medido: raiz em x 62..74)
WALL_E_END = (73.2, 439.4)   # muro leste: termina ENCOSTADO na raiz leste (que passa por cima da borda em y 440..448)
RAIL_W = (-53.0, 362.8)    # pontas do guarda-corpo junto dos torreoes (ajustadas pela geometria dos torreoes)
RAIL_E = (52.5, 361.0)


# ================================================================== ADRO, SUBIDA, ESTANDARTES
def banners(mb):
    """estandartes brancos com o brasao nos paineis planos da falesia: vara com ponteiras douradas presa por 2 bracos
    de ferro chumbados na rocha, pano 0,25 a frente do painel, barra de peso, brasao saindo dos 2 lados"""
    import op_terrain as TR
    for idx, xc, yf in ((1, -16.15, 351.75), (6, 16.45, 352.0)):
        dr = 1.4 + 4.2 * TR.hh("cf", idx, "dr") ** 1.5
        ztop = CC - dr - 0.9
        zbot = 118.6
        Fb = Frame(xc, yf, 0.0, math.pi)                    # +y = para fora da rocha (-Y do mundo)
        yc = 0.3                                            # pano 0,3 a frente do painel
        wdt = 5.6
        bb(mb, Fb, -wdt / 2, wdt / 2, yc, yc + 0.12, zbot + 0.3, ztop - 0.35, CWHITE)
        mb.rod(Fb.p(-wdt / 2 - 0.6, yc + 0.06, ztop), Fb.p(wdt / 2 + 0.6, yc + 0.06, ztop), 0.2, WD, 8)
        for s in (-1, 1):
            x = s * (wdt / 2 + 0.75)
            mb.rod(Fb.p(x - s * 0.05, yc + 0.06, ztop), Fb.p(x + s * 0.4, yc + 0.06, ztop), 0.28, GOLD, 8)
            # braco de ferro: chapa chumbada (entra 0,4 na rocha) + mao-francesa ate a vara
            xa = s * (wdt / 2 - 0.4)
            bb(mb, Fb, xa - 0.3, xa + 0.3, -0.45, 0.08, ztop - 1.6, ztop + 0.5, IRON)
            beam(mb, Fb, (xa, 0.0, ztop - 1.4), (xa, yc + 0.06, ztop - 0.15), 0.14, 0.16, IRON)
            beam(mb, Fb, (xa, 0.0, ztop + 0.3), (xa, yc + 0.06, ztop + 0.05), 0.14, 0.16, IRON)
            for zz in (ztop - 1.3, ztop + 0.25):
                mb.rod(Fb.p(xa, 0.02, zz), Fb.p(xa, 0.14, zz), 0.1, IRON, 6)
        for k in range(5):                                  # alcas do pano na vara
            xx = -wdt / 2 + 0.4 + (wdt - 0.8) * k / 4
            bb(mb, Fb, xx - 0.22, xx + 0.22, yc - 0.12, yc + 0.24, ztop - 0.5, ztop + 0.3, CWHITE)
        bb(mb, Fb, -wdt / 2 - 0.15, wdt / 2 + 0.15, yc - 0.18, yc + 0.3, zbot + 0.05, zbot + 0.4, WD)    # peso
        crest(mb, sub(Fb, 0.0, yc + 0.06, 0.0), 0.0, ztop - (ztop - zbot) * 0.34, 1.75, INDIGO, 0.14)
        bb(mb, Fb, -wdt / 2 + 0.3, wdt / 2 - 0.3, yc - 0.12, yc + 0.24, zbot + 1.2, zbot + 1.75, INDIGO)  # faixa


def adro(mb):
    # PORTAO VERMELHO do adro sobre o topo da escada Adro (de frente para a praca)
    gx, gy, gw = L.CASTLE_GATE
    F, xs, cw, back = koraimon(mb, gx, gy, math.pi, gw, 16.5, True, CF, "kgA", plaque=True)
    for s in (-1, 1):
        col_box("OP_CasGate", (cw + 0.6, cw + 0.6, 16.5), F.p(s * xs, 0.0, 8.25), F.r())
        col_box("OP_CasGate", (1.8, 1.8, 11.0), F.p(s * (xs + 0.6), -back, 5.5), F.r())
    # postes de lanterna no adro (fora do eixo e da escada)
    for i, x in enumerate((-25.5, 25.5)):
        K.lantern_post(mb, Frame(x, 320.0, CF, 0.0), 9.0, 1.7, "L_OPProp_Lamp_Cas_Adro_%d" % i, 40.0)
        col_box("OP_CasLamp", (1.2, 1.2, 9.0), (x, 320.0, CF + 4.5))
    # mureta de cantaria na bacia (frente e lados; aberta no canal leste e na face da rocha)
    off = ccw(DL.offset_poly(L.BASIN, 0.65))                # linha da mureta 0,65 FORA da bacia (no piso do adro)
    n = len(off)
    for i in range(n):
        a, b = off[i], off[(i + 1) % n]
        if min(a[1], b[1]) > 349.0:
            continue                                        # lado da rocha (a queda bate ali)
        pts = [a, b]
        if max(a[0], b[0]) > 15.0 and min(a[1], b[1]) < 345.6 and max(a[1], b[1]) > 338.6:
            # corta o vao do canal leste (y 338,6 .. 345,6)
            t0 = (338.6 - a[1]) / (b[1] - a[1])
            t1 = (345.6 - a[1]) / (b[1] - a[1])
            lerp = lambda t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            # recorta o intervalo do vao no parametro t do segmento e fica com o pedaco mais longo fora dele
            # (a versao anterior usava lerp(t0) com t0 < 0 na aresta NE e criava uma peca falsa sobre a boca)
            g0, g1 = sorted((t0, t1))
            antes, depois = (0.0, min(max(g0, 0.0), 1.0)), (max(min(g1, 1.0), 0.0), 1.0)
            ta, tb = antes if (antes[1] - antes[0]) >= (depois[1] - depois[0]) else depois
            pts = [lerp(ta), lerp(tb)]
        a, b = pts
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 1.0:
            continue
        Fp = Frame((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, CF, math.atan2(dy, dx))
        bb(mb, Fp, -ln / 2 - 0.55, ln / 2 + 0.55, -0.6, 0.6, -0.3, 1.15, WALL)              # mureta: corpo
        bb(mb, Fp, -ln / 2 - 0.65, ln / 2 + 0.65, -0.75, 0.75, 1.15, 1.5, STP)              # capa com pingadeira
        bb(mb, Fp, -ln / 2 - 0.5, ln / 2 + 0.5, -0.75, 0.75, -0.3, 0.25, STD)              # soco escuro
    # portao de madeira (kabukimon) no pe da subida
    F2, xs2, cw2, back2 = koraimon(mb, -71.0, 334.6, math.pi, 12.0, 9.5, False, CF, "kgS", hikae=False)
    for s in (-1, 1):
        col_box("OP_CasGate", (cw2 + 0.4, cw2 + 0.4, 9.5), F2.p(s * xs2, 0.0, 4.75), F2.r())


def stairs(mb):
    for nm in ("Adro", "CasteloA", "CasteloB"):
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        K.stair_stone(mb, Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2), w, n,
                      rise=L.stair_rise(nm), tread=tread, z_floor=-0.3, cheek_h=1.0, newels=(nm == "CasteloB"))
    # lanterna de pedra no patamar da subida
    K.toro(mb, Frame(-77.0, 388.0, CL, 0.0), 0.9, "L_OPProp_Lamp_Cas_Patamar", 30.0)
    col_box("OP_CasLamp", (2.6, 2.6, 7.0), (-77.0, 388.0, CL + 3.5))


# ================================================================== orcamento / build
def stats(verbose=True):
    import studio_op
    tris, mps = 0, 0
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("OP_Cas_"):
            t = sum(len(p.vertices) - 2 for p in o.data.polygons)
            m = studio_op.est_meshparts(o)
            tris += t
            mps += m
            if verbose:
                print("OP_CAS %-18s tris %6d  MP~ %2d  mats %d" % (o.name, t, m, len(o.data.materials)))
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_OP_Cas"))
    nl = sum(1 for o in bpy.data.objects if o.type == "LIGHT" and o.name.startswith("L_OPCas"))
    top = max(((o.matrix_world @ v.co).z for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("OP_Cas_Keep")
               for v in o.data.vertices), default=0.0)
    if verbose:
        print("OP_CAS orcamento: tris %d / 70000 | MeshParts~ %d / 55 | colisoes %d / 60 | luzes de dia %d / 4 | "
              "topo da torre %.1f" % (tris, mps, ncol, nl, top))
    return tris, mps, ncol


def build():
    rng = random.Random(4600)
    mk = MB("OP_Cas_Keep", C, rng, detail="near", floor=-999)
    keep(mk)
    hall(mk)
    mk.finish()
    keep_cols()
    hall_cols()
    mc = MB("OP_Cas_Court", C, rng, detail="near", floor=-999)
    court(mc)
    mc.finish()
    ma = MB("OP_Cas_Adro", C, rng, detail="near", floor=-999)
    adro(ma)
    stairs(ma)
    banners(ma)
    ma.finish()
    stats()


# ================================================================== cameras (folhas M3)
def _sz(nm, y):
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    t = (y - foot[1] + tread / 2) / tread
    return foot[2] + max(0.0, min(float(n), t)) * L.stair_rise(nm)


def cams():
    e = L.EYE
    out = {}
    c = (KX, KY, CC + 40.0)
    for k in range(8):
        a = math.radians(-90.0 + 45.0 * k)
        out["CAM_OP_Cas_360_%d" % k] = ((c[0] + math.cos(a) * 200.0, c[1] + math.sin(a) * 200.0, CC + 52.0), c, 30)
    out.update({
        "CAM_OP_Cas_PH_Adro": ((6.0, 298.0, P + e), (0.0, 345.0, CF + 16.0), 22),
        "CAM_OP_Cas_PH_AdroDentro": ((16.0, 331.0, CF + e), (-22.0, 352.0, 121.0), 22),
        "CAM_OP_Cas_PH_SubidaPe": ((-50.0, 326.0, CF + e), (-71.0, 345.0, CF + 9.0), 22),
        "CAM_OP_Cas_PH_Subida": ((-71.0, 350.0, _sz("CasteloA", 350.0) + e), (-71.0, 400.0, CL + 12.0), 22),
        "CAM_OP_Cas_PH_Patamar": ((-74.0, 384.0, CL + e), (-71.0, 445.0, CC + 7.0), 22),
        "CAM_OP_Cas_PH_Portao": ((-71.0, 426.0, _sz("CasteloB", 426.0) + e), (-71.0, 446.0, CC + 6.0), 22),
        "CAM_OP_Cas_PH_PatioEntrada": ((-71.0, 452.0, CC + e), (0.0, 400.0, CC + 28.0), 22),
        "CAM_OP_Cas_PH_Patio": ((-42.0, 364.0, CC + e), (0.0, 395.0, CC + 22.0), 22),
        "CAM_OP_Cas_PH_Porta": ((5.0, 359.0, CC + e), (0.0, 381.0, CC + 7.5), 24),
        "CAM_OP_Cas_PH_Salao": ((9.0, 384.0, CC + FLOOR + e), (-4.0, 422.0, CC + 4.5), 20),
        "CAM_OP_Cas_PH_SalaoVolta": ((-10.0, 419.0, CC + FLOOR + e), (2.0, 381.0, CC + 4.5), 20),
        "CAM_OP_Cas_PH_Mirante": ((-18.0, 357.0, CC + e), (40.0, 280.0, P + 10.0), 22),
        "CAM_OP_Cas_PH_Fundo": ((-52.0, 462.0, CC + e), (20.0, 432.0, CC + 18.0), 22),
        "CAM_OP_Cas_C_Telhado": ((-50.0, 366.0, CC + 31.0), (-30.0, 383.0, CC + 24.0), 26),
        "CAM_OP_Cas_C_Varanda": ((-30.0, 372.0, CC + 66.0), (0.0, 393.0, CC + 61.0), 26),
        "CAM_OP_Cas_C_Shachi": ((-26.0, 378.0, CC + 84.0), (-9.0, 404.0, CC + 80.0), 30),
        "CAM_OP_Cas_C_Kara": ((6.0, 352.0, CC + 62.0), (0.0, 391.0, CC + 57.0), 28),
        "CAM_OP_Cas_C_Estandarte": ((2.0, 324.0, CF + 10.0), (16.0, 351.5, 125.5), 40),
        "CAM_OP_Cas_C_Porta": ((-10.0, 362.0, CC + 3.8), (0.0, 381.0, CC + 7.0), 24),
        "CAM_OP_Cas_C_PortaoVermelho": ((-16.0, 302.0, P + 9.0), (0.0, 324.5, CF + 11.0), 24),
        "CAM_OP_Cas_C_Yagura": ((22.0, 344.0, CC + 16.0), (58.0, 365.0, CC + 10.0), 26),
        "CAM_OP_Cas_C_Muro": ((-48.0, 450.0, CC + 7.0), (-89.0, 466.0, CC + 3.0), 24),
        "CAM_OP_Cas_C_MuroArvoreN": ((28.0, 446.0, CC + 14.0), (58.0, 469.0, CC + 3.0), 26),
        "CAM_OP_Cas_C_MuroArvoreE": ((50.0, 410.0, CC + 11.0), (73.0, 440.0, CC + 3.0), 26),
    })
    return out


DUMMIES = [(4.0, 300.0, P, 0.0), (9.0, 331.0, CF, 0.0), (-69.0, 364.0, _sz("CasteloA", 364.0), 0.0),
           (-74.0, 388.0, CL, 0.0), (-68.0, 452.0, CC, 0.0), (3.0, 395.0, CC + FLOOR, 0.0), (-26.0, 362.0, CC, 0.0),
           (-68.5, 437.0, _sz("CasteloB", 437.0), 0.0)]
