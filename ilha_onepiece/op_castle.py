# op_castle.py - CASTELO DE WANO (marco heroi da Ilha 5 ONE PIECE / WANO; dono "castle", prefixo OP_Cas_)
# V3 (rodada 2 do usuario, G4: "o predio principal, seu conceito ainda esta pouco fraco, paredes lisas sem presenca"):
#   PAREDES COM PRESENCA (face3): shitami-itabari preto-azulado na base de cada andar + reboco frio so em cima, faixas
#   salientes (koshi-nageshi, nageshi, viga de beiral) com cantoneiras douradas, pilares aparentes por baia, janelas com
#   caixilho GROSSO rebocado (renji com grade, katomado em sino no 4o/5o andar, 2 fileiras no 3o), ishi-otoshi nos
#   cantos do 3o andar; CAIBROS brancos pendendo sob cada testeira (franja serrilhada do anime); FRONTOES chidori3 com
#   timpano ornamentado (tirante, brasao de ouro, kitsune-goshi, gegyo dourado, cravos); ENGAWA vermelha no terreo (2o
#   nivel de balaustrada, com colisao) e varanda do 5o andar mais rica (rail3: giboshi, balaustres); torre mais afunilada
#   (VT 0,88/0,84/0,84) e 5o andar 3 mais alto; materiais novos Roof_OP_Castle / Plaster_OP_Castle / Wood_OP_Sumi.
#   Orcamento: 91,2k tris (teto 92k justificado: tris pagos com cull_hidden, LOD 1 nas costas/lados, muros do fundo lisos).
# V2 (V2-2, feedback do usuario 10/10 item U3: "o modelo do palacio central" FEIO - capturas 03 e 14). Refs:
#   ref_02 (castelo + arvore do anime) e ref_03 (Flower Capital). Diagnostico do V1: caixas brancas largas com
#   tampas de chapa azul finas, janelinhas pretas, telhado sem peso; muro do patio e telhados do adro alcancaveis sem
#   colisao (gate 'visual' da V2-0 vermelho).
#   V2 = A MESMA LINGUA DO KIT V2 (op_kit2) EM ESCALA MONUMENTAL:
#   TORRE (tenshu) de 5 ANDARES dentro dos volumes TRAVADOS de L.KEEP_TIERS (a arvore respeita a mesma envoltoria):
#     andar 1 = salao (terreo acessivel), andar 2 = mezanino do 1o volume (saia mokoshi R0 entre os dois), andares
#     3/4/5 = os volumes de cima. 5 TELHADOS (R0..R4) em TELHA ONDULADA do kit V2 (canal + capa na geometria, perfil
#     CONCAVO: ingreme junto da parede e raso no beiral, cantos levantados, beiral grosso de 2 tabuas), BEIRAIS
#     REBOCADOS de branco (nurigome: testeira, forro e tabeiras brancas como no castelo do anime - linhas claras sob
#     os telhados escuros), capas de espigao com onigawara nas 4 pontas, rufo escuro na base de cada parede.
#     FRONTOES: CHIDORI-HAFU (empena triangular de reboco com madeiramento escuro e gegyo) em R1 (par na frente, 1 em
#     cada outra face), R2 (grande na frente/fundos, menor nos lados), R3 (lados); KARAHAFU em R3 (frente/fundos) e o
#     KARAHAFU DOURADO de R0 sobre a porta (portico com pilares, timpano com o brasao, tabeira de ouro - o portao
#     dourado da ref_02). R4 = irimoya do topo com SHACHIHOKO dourados e remates de ouro so na cumeeira.
#     Paredes: reboco off-white com faixa escura de viga sob cada beiral e verga (nageshi), FILEIRA DE JANELAS com
#     caixilho escuro, peitoril e grade (renji) em cada andar, nas 4 faces (360 graus). VARANDA VERMELHA (mawari-en)
#     no 5o andar. Base em ISHIGAKI aparelhado em talude (fiadas desencontradas, cantos sangi-zumi, capa de lajes).
#   SALAO (terreo) COM VIDA: assoalho + 2 campos de TATAMI com debrum, pilares com consolo, teto em caixotoes,
#     estrado (jodan) com 3 almofadas, apoio de braco, mesinha laqueada e suporte de espadas; biombos dourados de 6
#     folhas, rolo com o brasao no tokonoma, 2 ARMADURAS de exposicao (vermelho-laca e ouro) sobre baus, 2 suportes de
#     espadas nas paredes laterais, 4 andon de piso, 3 lanternas de papel (as 3 luzes L_OPCas_Hall_*). Sem sistema.
#   PATIO (136,2): mirante com guarda-corpo vermelho (kit V2), muros dobei com capa de TELHA ONDULADA e COLISAO ALTA
#     (o topo nao e alcancavel: era o FAIL da V2-0), 2 yagura de canto refeitos no kit V2, portao do patio, 2 toro
#     kasuga (kit V2), cerca sagrada (TAMAGAKI) com SHIMENAWA em volta da base da arvore (as raizes ficam fora do
#     alcance: a colisao alta da cerca fecha o 'corpo dentro' das raizes medido pelo gate).
#   ADRO (98,2): portao vermelho (telhado do kit V2 com colisao), mureta da bacia COM colisao, portao de madeira no pe
#     da subida (telhado com colisao), postes de lanterna do kit V2, escadas de pedra; ESTANDARTES: so os 2 da falesia
#     (U16), com colisao na vara e no peso (o topo da vara fica a < 6 do patio).
# COLISAO: salao (paredes com o vao da porta, piso, teto, pilares, estrado, biombos, folhas, armaduras, suportes),
#   caixas dos andares de cima, base de pedra, portico, portoes + telhados dos portoes, torreoes, toro, postes,
#   muros (ate CC+8,8), cerca da arvore (ate CC+8,8), mureta da bacia, estandartes. Chao/escadas/guardas: op_col.
# Ordem do build_op: roda ANTES do op_tree (o check_castle do op_tree le as malhas OP_Cas_*).
# MATERIAL: so os do op_lib (telha do castelo = Roof_OP_Blue, o azul-ardosia escuro da paleta; beirais Plaster_OP).
import math, random, os
import bpy
from mathutils import Vector
import op_lib as DL
from op_lib import MB, Frame, light, col_box, col_ramp, ccw
import op_layout as L
import op_kit as K
import op_kit2 as K2
from op_kit import (WD, WM, LAC, GOLD, IRON, PL, RB, RR, ST, STD, STP, LIT, LGLOW, INDIGO, CWHITE, CRED, bb, bx, sub,
                    loft, lathe, lathe_y, ext, beam, even)

C = "04_CASTLE"
CC, CF, CL, P = L.CC, L.CF, L.CL, L.P
KX, KY = L.KEEP_C
T = L.KEEP_TIERS                        # (hx, hy, z0, altura da parede, beiral)
WALL = "Stone_OP_Wall"
DARK = "Roof_OP_Ridge"                  # fundo escuro das janelas cenograficas (o mais escuro da paleta)
ROOF = "Roof_OP_Castle"                 # V3: telha azul-marinho PROFUNDA do castelo do anime (op_lib)
PL = "Plaster_OP_Castle"                # V3: reboco frio branco-lilas (op_lib) em TODO o conjunto do castelo
SUMI = "Wood_OP_Sumi"                   # V3: tabuas shitami, pilares, faixas (preto-azulado, op_lib)
FRAME = "Plaster_OP_Castle"             # V3: caixilho GROSSO rebocado (nurigome): a janela le como VAO escuro no branco
FAS = PL                                # testeiras/tabeiras rebocadas (a linha clara sob cada telhado)
SOFFIT = RR                             # forro do beiral escuro: o telhado le como MASSA escura vista da praca
TATAMI = "Cloth_OP_Tatami"
CBLACK = "Cloth_OP_Black"
STRAW = "Cloth_OP_Straw"
WARM = (1.0, 0.64, 0.36)
FLOOR = 0.45                            # piso do salao acima do patio (degrau na soleira)
PLINTH = 4.5                            # base de cantaria da torre
DOOR_W, DOOR_H = L.KEEP_DOOR[2], L.KEEP_DOOR[3]
ZG = 0.14                               # folga anti z-fight (> 0,12) entre faces paralelas de materiais diferentes
COURT_GATE_Y = 440.5                    # portao do patio: logo depois do topo da CasteloB (439)
SE_TURRET = (58.0, 365.0, 12.0)         # yagura SE (centro na borda da proa, girada com ela)
SW_TURRET = (-57.0, 367.0, 10.0)        # sumi-yagura SO (menor; equilibra a frente da proa)
COL_TALL = 8.8                          # colisao alta (muros/cerca): topo acima do pulo (7,2) a partir do patio


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


class plastered:
    """dentro do bloco, a 'madeira' das pecas do kit V2 (testeira, tabeiras, caibros, gegyo, rincoes) vira REBOCO
    BRANCO: beiral nurigome do castelo. O madeiramento das empenas (op_kit._gable_timber) continua escuro."""

    def __enter__(self):
        self.w = K2.WD
        K2.WD = FAS

    def __exit__(self, *a):
        K2.WD = self.w


def _prof(t, c):
    """perfil concavo normalizado (0 na parede, 1 no beiral): inclinacao c x maior junto da parede que no beiral"""
    return (c * t - 0.5 * (c - 1.0) * t * t) / (0.5 * (c + 1.0))


def _face_frames(F):
    return (("F", F), ("B", sub(F, ang=math.pi)), ("R", sub(F, ang=-math.pi / 2)), ("L", sub(F, ang=math.pi / 2)))


# ================================================================== SAIA DO CASTELO (telhado entre andares)
def cskirt(mb, F, Xi, Yi, Xe, Ye, z_top, rise, m=None, tv=0.6, lift=1.6, conc=2.2, lod=0, chid=None, kara=None,
           gold=True, amp=0.3, P=2.0, fas=0.8, oni=True, kara_gold=False, up=4.0, back_lod=None, rows=None):
    """SAIA de 4 aguas do kit V2 em escala de castelo: da parede de cima (Xi, Yi; topo z_top) ate o beiral (Xe, Ye),
    caindo 'rise'. Perfil concavo (conc), cantos levantados (lift) so nos triangulos dos espigoes (casa nas 2 aguas),
    telha ondulada (K2.tiles) com forro REBOCADO, testeira dupla rebocada, capas de espigao com onigawara, rufo escuro
    junto da parede de cima.
      chid = {"F"|"B"|"R"|"L": [(xc, w, yf)]}: chidori-hafu (K2._chidori) com a empena em yf (fracao da aba)
      kara = {"F"|"B": (w, subida)}: o beiral sobe em sino no meio da face (karahafu de beiral, timpano + gegyo)
    Devolve {face: (H, A, Ao, Bi, Bo)} - H(x, y) no referencial da face (x ao longo, +y para fora)."""
    m = m or ROOF
    chid = chid or {}
    kara = kara or {}
    back_lod = lod if back_lod is None else back_lod
    k_in = rise * conc / (0.5 * (conc + 1.0))
    k_out = rise / (0.5 * (conc + 1.0))
    rows = rows or (0.0, 0.12, 0.32, 0.6, 1.0)
    out = {}
    for key, Fk in _face_frames(F):
        A, Ao, Bi, Bo = (Xi, Xe, Yi, Ye) if key in "FB" else (Yi, Ye, Xi, Xe)
        kd = kara.get(key)

        def H(x, y, A=A, Ao=Ao, Bi=Bi, Bo=Bo, kd=kd):
            t = (y - Bi) / (Bo - Bi)
            if t <= 0.0:
                return z_top + k_in * (-t)
            z = z_top - rise * _prof(t, conc) if t < 1.0 else z_top - rise - k_out * (t - 1.0)
            tc = min(t, 1.0)
            s = min(1.0, max(0.0, (abs(x) - A) / (Ao - A)))
            z += lift * s * s * tc * tc
            if kd:
                w, rk = kd
                u = abs(x) / (w / 2)
                if u < 1.0:
                    z += rk * 0.5 * (1.0 + math.cos(math.pi * u)) * max(0.0, (tc - 0.12) / 0.88) ** 1.5
            return z
        out[key] = (H, A, Ao, Bi, Bo)
        lk = lod if key == "F" else back_lod
        ylo = (lambda x, A=A, Ao=Ao, Bi=Bi, Bo=Bo: Bi - 0.4 if abs(x) <= A else Bi + (abs(x) - A) * (Bo - Bi) / (Ao - A))
        K2.tiles(mb, Fk, K2._wave(-Ao, Ao, P, amp, 0 if kd else lk), ylo, Bo, H, m, tv, soffit=SOFFIT,
                 rows=rows if (kd or lk == 0) else (0.0, 0.2, 0.5, 1.0), coarse=2.0 if kd else 4.0)
        # testeira dupla (rebocada; ouro no sino do karahafu dourado)
        xs = [-Ao + 0.4 + (2 * Ao - 0.8) * f for f in (0.0, 0.04, 0.1, 0.18, 0.28, 0.4, 0.5, 0.6, 0.72, 0.82, 0.9,
                                                        0.96, 1.0)]
        if kd:
            xs += [(-kd[0] / 2) * (1 - 2 * i / 24.0) for i in range(25)]
        xs = sorted(set(round(x, 3) for x in xs))
        yb = Bo - 0.3
        segs = [(xs, FAS)]
        if kd and kara_gold:
            w2 = kd[0] / 2
            segs = [([x for x in xs if x <= -w2 + 1e-6], FAS), ([x for x in xs if -w2 - 1e-6 <= x <= w2 + 1e-6], GOLD),
                    ([x for x in xs if x >= w2 - 1e-6], FAS)]
        for sx_, mm in segs:
            if len(sx_) < 2:
                continue
            K.strip(mb, Fk, [(x, yb, H(x, yb) - tv) for x in sx_], (0, 1, 0), -0.2, 0.2, -fas, 0.0, mm)
            if lk == 0 or kd:
                K.strip(mb, Fk, [(x, yb - 0.34, H(x, yb) - tv - fas + 0.04) for x in sx_[1:-1] or sx_], (0, 1, 0),
                        -0.15, 0.15, -0.45, 0.02, mm if mm != GOLD else FAS)
        # rufo (mizukiri) escuro na base da parede de cima
        bb(mb, Fk, -A - 0.15, A + 0.15, Bi - 0.1, Bi + 0.35, z_top - 0.12, z_top + 0.42, RR)
        if kd:                                                  # timpano do karahafu + gegyo
            w, rk = kd
            yv = Bo - 1.0
            xx = [(-w / 2) * 0.96 + w * 0.96 * i / 24 for i in range(25)]
            base = lambda x: H(x, yv) - rk * 0.5 * (1.0 + math.cos(math.pi * min(1.0, abs(x) / (w / 2)))) * \
                max(0.0, ((yv - Bi) / (Bo - Bi) - 0.12) / 0.88) ** 1.5
            top = [(x, H(x, yv) - tv - 0.45) for x in xx]
            bot = [(x, base(x) - tv - 0.45) for x in xx]
            if max(t[1] - b[1] for t, b in zip(top, bot)) > 0.6:
                ext(mb, Fk, bot + list(reversed(top)), "y", yv - 0.3, yv, PL)
                for x in (-w * 0.2, w * 0.2):
                    zt_, zb_ = H(x, yv) - tv - 0.45, base(x) - tv - 0.45
                    if zt_ - zb_ > 0.6:
                        bb(mb, Fk, x - 0.16, x + 0.16, yv - 0.05, yv + 0.12, zb_, zt_, WD)
            Fg = sub(Fk, 0.0, 0.0, 0.0, math.pi / 2)
            K._gegyo(mb, Fg, Bo - 0.25, H(0.0, Bo - 0.3) - tv - fas, 1, GOLD if kara_gold else FAS, 1.2, True)
        for xc, w, yf in chid.get(key, ()):
            with plastered():
                K2._chidori(mb, Fk, H, tv * 0.85, xc, w, Bi + (Bo - Bi) * yf, m, z_top + up, PL, gold, lk, P * 0.9,
                            amp * 0.9)
    # capas de espigao (ponta levantada + onigawara)
    Hf = out["F"][0]
    for sx in (1, -1):
        for sy in (1, -1):
            pts = [(sx * (Xe + 0.55), sy * (Ye + 0.55), Hf(Xe, Ye) + 0.95)]
            for f in (0.0, 0.12, 0.35, 0.65, 1.0):
                x, y = Xe - f * (Xe - Xi), Ye - f * (Ye - Yi)
                pts.append((sx * x, sy * y, Hf(x, y) + 0.32))
            K2._hipcap(mb, F, pts, 1.15, oni)
    return out


def wall_top(sk, key, Bw):
    """topo da parede de baixo sob a saia sk, na linha Bw (meia largura/profundidade da parede de baixo)"""
    H, A, Ao, Bi, Bo = sk[key]
    return H(0.0, Bw) - 0.6 - 0.3


# ================================================================== paredes
def cwin(mb, Ff, s, z, w, h, t=1.0, kind="dark", lod=0):
    """janela de castelo RECUADA: moldura escura 0,15 a frente do reboco, peitoril, barras (renji) e fundo escuro
    ('dark', cenografica) ou papel aceso com kumiko visto de dentro ('hall', parede de espessura t)"""
    x0, x1 = s - w / 2, s + w / 2
    j = 0.34
    g = ZG
    bb(mb, Ff, x0 - j, x0 + g, -0.5, 0.62, z - 0.1, z + h + 0.1, FRAME)                  # V3: caixilho grosso
    bb(mb, Ff, x1 - g, x1 + j, -0.5, 0.62, z - 0.1, z + h + 0.1, FRAME)
    bb(mb, Ff, x0 - j - 0.12, x1 + j + 0.12, -0.5, 0.66, z + h - g, z + h + 0.42, FRAME)
    bb(mb, Ff, x0 - j - 0.22, x1 + j + 0.22, -0.5, 0.8, z - 0.46, z + g, SUMI)           # peitoril com pingadeira
    nb = max(3, int(round(w / (0.5 if lod == 0 else 0.95))))
    flat = kind == "dark" and lod >= 1                      # lod 1: sem furo na parede, fundo escuro saliente
    for i in range(1, nb):
        xx = x0 + w * i / nb
        if flat:
            bb(mb, Ff, xx - 0.12, xx + 0.12, 0.06, 0.2, z, z + h, PL)
        else:
            bb(mb, Ff, xx - 0.11, xx + 0.11, -0.42, -0.2, z, z + h, WD if kind == "dark" else PL)
    if flat:
        bb(mb, Ff, x0 + 0.02, x1 - 0.02, 0.0, 0.06, z, z + h, DARK)
    elif kind == "dark":
        bb(mb, Ff, x0, x1, -0.86, -0.72, z, z + h, DARK)
        if lod == 0:
            bb(mb, Ff, x0, x1, -0.5, -0.36, z + h * 0.48, z + h * 0.48 + 0.16, WD)    # travessa
    else:
        bb(mb, Ff, x0, x1, -t * 0.55 - 0.03, -t * 0.55 + 0.03, z, z + h, LIT)          # papel no meio da parede
        bb(mb, Ff, s - 0.06, s + 0.06, -t * 0.55 - 0.18, -t * 0.55 - 0.05, z, z + h, WD)
        bb(mb, Ff, x0, x1, -t * 0.55 - 0.18, -t * 0.55 - 0.05, z + h / 2 - 0.06, z + h / 2 + 0.06, WD)
        bb(mb, Ff, x0 - 0.3, x1 + 0.3, -t - 0.16, -t + 0.18, z - 0.3, z + g, WD)        # peitoril interno
        bb(mb, Ff, x0 - 0.3, x1 + 0.3, -t - 0.16, -t + 0.18, z + h - g, z + h + 0.3, WD)


def story(mb, F, hx, hy, z0, ztop, t, wins, wz, ww, wh, kind="dark", door=False, lod=0, band=True, sill_band=True):
    """paredes de um andar: reboco (com os vaos) de z0 ate ztop[face], faixa escura de viga sob o beiral, verga
    (nageshi) continua sobre as janelas e faixa do peitoril; wins = {face: [s, ...]}"""
    for key, Ff, ln, d in faces(F, hx, hy):
        side = key in "RL"
        a, b = (-ln / 2 + t, ln / 2 - t) if side else (-ln / 2, ln / 2)
        zt = ztop[key]
        holes = [(s - ww / 2, s + ww / 2, wz, wz + wh) for s in wins.get(key, ())] if (kind != "dark" or lod == 0) else []
        if door and key == "F":
            holes.append((-DOOR_W / 2, DOOR_W / 2, -1.0, FLOOR + DOOR_H))
        K.panel(mb, Ff, a, b, z0, zt, -t, 0.0, holes, PL)
        for s in wins.get(key, ()):
            cwin(mb, Ff, s, wz, ww, wh, t, kind, lod)
        if band:
            bb(mb, Ff, -ln / 2 - 0.25, ln / 2 + 0.25, -0.3, 0.25, zt - 1.1, zt, SUMI)      # viga de beiral (faixa)
        if wins.get(key) and sill_band:
            zn = wz + wh + 0.9
            if zn < zt - 1.5:
                bb(mb, Ff, -ln / 2 - 0.2, ln / 2 + 0.2, -0.3, 0.2, zn, zn + 0.35, SUMI)    # nageshi
            zs = wz - 1.1
            if zs > z0 + 0.6:
                bb(mb, Ff, -ln / 2 - 0.2, ln / 2 + 0.2, -0.3, 0.2, zs, zs + 0.3, SUMI)     # faixa do peitoril
        # pilares de canto escuros (amarram as faces)
        bb(mb, Ff, ln / 2 - 0.45, ln / 2 + 0.25, -0.45, 0.25, z0, zt, SUMI)


# ================================================================== base de cantaria
def _courses(key, z0, z1, hmin, hmax):
    """cotas das fiadas de z0 (pe) a z1 (topo das pedras): alturas hmin..hmax sorteadas, a ultima ajustada"""
    zs = [z0]
    c = 0
    while zs[-1] < z1 - 1e-6:
        z2 = min(z1, zs[-1] + hmin + (hmax - hmin) * K._h01(key, "fiada", c))
        if z1 - z2 < hmin * 0.6:
            z2 = z1
        zs.append(z2)
        c += 1
    return zs


def sangi_corners(mb, F, hx, hy, z_top, zs, batter, key, proud=0.15, lift=0.2):
    """cantos travados (sangi-zumi) por FIADA: 1 pedra por canto, comprida numa face e curta na outra, alternando"""
    tb = math.tan(math.radians(batter))
    nc = len(zs) - 1
    lx = ly = 0.0
    for c in range(nc):
        za = zs[c] + lift + 0.03
        zb_ = zs[c + 1] - 0.03 if c == nc - 1 else zs[c + 1] + lift - 0.03
        if zb_ - za < 0.3:
            continue
        lx, ly = (2.6, 1.5) if c % 2 == 0 else (1.5, 2.6)
        for sx in (-1, 1):
            for sy in (-1, 1):
                def ring(z):
                    o = (z_top - z) * tb + proud
                    X, Y = sx * (hx + o), sy * (hy + o)
                    return [(X, Y, z), (sx * (hx - lx), Y, z), (sx * (hx - lx), sy * (hy - ly), z), (X, sy * (hy - ly), z)]
                loft(mb, F, [ring(za), ring(zb_)], STD if K._h01(key, sx, sy, c, "d") < 0.17 else ST)
    return lx, ly


def ishigaki_keep(mb, F, hx, hy, z_top, z_bot, batter, key, gap=None):
    """base da torre em cantaria APARELHADA por fiadas em talude, juntas desencontradas, 1 pedra em 6 escura (nunca 2
    vizinhas), cantos em sangi-zumi, capa de lajes"""
    tb = math.tan(math.radians(batter))
    zc = z_top - 0.4
    zs = _courses(key, z_bot, zc, 1.35, 2.0)
    sangi_corners(mb, F, hx, hy, zc, zs, batter, key)
    for k, Ff, ln, d in faces(F, hx, hy):
        half = ln / 2
        for a, b in ([(-half + 0.6, gap[0] - 0.3), (gap[1] + 0.3, half - 0.6)] if (gap and k == "F") else
                     [(-half + 0.6, half - 0.6)]):
            bb(mb, Ff, a, b, -1.9, -0.4, z_bot + 0.4, zc - 0.05, STD)                        # miolo escuro (juntas)
        below = []
        for c in range(len(zs) - 1):
            za, zb_ = zs[c], zs[c + 1]
            lc = ((2.6 if c % 2 == 0 else 1.5) if k in "FB" else (1.5 if c % 2 == 0 else 2.6)) + 0.06
            x, xend = -half + lc, half - lc
            x -= 1.2 * K._h01(key, k, c, "o") if c % 2 else 0.0
            x = max(x, -half + lc)
            row, prev, n = [], False, 0
            while x < xend - 0.3:
                x2 = min(xend, x + {"F": 3.4, "B": 4.6}.get(k, 3.8) + 2.0 * K._h01(key, k, c, n))   # V3: fundos/lados com pedras maiores
                if xend - x2 < 1.2:
                    x2 = xend
                spans = [(x, x2)]
                if gap and k == "F":
                    spans = [(a, b) for a, b in ((x, min(x2, gap[0])), (max(x, gap[1]), x2)) if b - a > 0.5]
                for a, b in spans:
                    dark = (K._h01(key, k, c, n, "d") < 1.0 / 6.0 and not prev and
                            not any(a < q1 and b > q0 for q0, q1 in below))
                    df = 0.04 * (K._h01(key, k, c, n, "f") - 0.5)
                    K.stone(mb, Ff, a + 0.03, b - 0.03, za + 0.03, zb_ - 0.03, -1.2, (zc - za) * tb + df,
                            (zc - zb_) * tb + df, 0.1, STD if dark else WALL)
                    prev = dark
                    if dark:
                        row.append((a, b))
                x = x2
                n += 1
            below = row
        a0, a1 = (-half - 0.25, half + 0.25) if k in "FB" else (-half + 1.35, half - 1.35)
        x, n = a0, 0
        while x < a1 - 0.3:
            x2 = min(a1, x + 2.6 + 1.4 * K._h01(key, k, "cap", n))
            if a1 - x2 < 1.0:
                x2 = a1
            for a, b in ([(x, x2)] if not (gap and k == "F") else
                         [(p, q) for p, q in ((x, min(x2, gap[0])), (max(x, gap[1]), x2)) if q - p > 0.5]):
                K.stone(mb, Ff, a + 0.03, b - 0.03, zc, z_top, -1.6, 0.25, 0.25, 0.08, STP)
            x = x2
            n += 1


# ================================================================== SHACHIHOKO
def shachi(mb, F, x, z, out, s=1.0):
    """SHACHIHOKO dourado na ponta da cumeeira: cabeca grande embaixo com a boca virada para dentro, corpo grosso em
    arco, cauda que volta para dentro e abre em V (2 lobos largos), dorsal, peitorais, olhos"""
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
    u, zz, r = pts[4]
    ext(mb, Fs, [(u + r * 0.8, z + zz - 0.7 * s), (u + r + 0.9 * s, z + zz + 0.1 * s), (u + r * 0.8, z + zz + 0.55 * s)],
        "y", -0.1 * s, 0.1 * s, GOLD)
    u, zz, r = pts[2]
    for sy in (-1, 1):
        ext(mb, Fs, [(u - 0.2 * s, z + zz - 0.2 * s), (u + 0.9 * s, z + zz - 0.9 * s), (u + 0.6 * s, z + zz + 0.2 * s)],
            "y", sy * 0.95 * s, sy * 1.1 * s, GOLD)
    u, zz, r = pts[1]
    bb(mb, Fs, -2.3 * s, -1.2 * s, -0.42 * s, 0.42 * s, z + zz - 0.12 * s, z + zz + 0.02 * s, RR)        # boca
    for sy in (-1, 1):
        lathe_y(mb, Fs, (u + 0.15 * s, sy * 0.78 * s, z + zz + 0.5 * s),
                [(0.26 * s, -0.1 * s * sy), (0.26 * s, 0.14 * sy * s)], 8, RR)
    bb(mb, Fs, -1.9 * s, 0.7 * s, -0.6 * s, 0.6 * s, z - 0.1, z + 0.55 * s, GOLD)


# ================================================================== V3: PAREDES COM PRESENCA (feedback G4 10/10)
# "paredes lisas sem presenca": cada andar agora e EMBASAMENTO de tabuas sobrepostas (shitami-itabari, preto-azulado)
# + reboco so em cima, dividido por FAIXAS salientes (koshi-nageshi, nageshi, viga de beiral) e PILARES aparentes que
# marcam as baias; janelas com caixilho GROSSO saliente (renji com grade branca, katomado em sino nos andares altos),
# ishi-otoshi nos cantos do 3o andar, caibros brancos sob cada beiral (a franja serrilhada do anime), cantoneiras
# douradas nas pontas das faixas. Nenhum plano de reboco maior que ~12 x 8 sem subdivisao.
def band(mb, Ff, a, b, z0, z1, d=0.42, caps=True, m=None):
    """faixa horizontal saliente (nageshi/viga) de a ate b; cantoneiras douradas nas 2 pontas"""
    bb(mb, Ff, a, b, -0.1, d, z0, z1, m or SUMI)
    if caps:
        for e, s in ((a, 1), (b, -1)):
            bb(mb, Ff, e - 0.06 * s, e + 0.5 * s, -0.12, d + 0.07, z0 - 0.05, z1 + 0.05, GOLD)


def boards(mb, Ff, spans, z0, z1, lod=0, step=0.78, proud=0.36):
    """SHITAMI-ITABARI: tabuas horizontais sobrepostas (borda de baixo grossa, sombra sob cada tabua) em perfil
    serrilhado extrudado ao longo de x + mata-juntas verticais (oshibuchi) a cada ~2,3 (lod 0)"""
    n = max(2, int(round((z1 - z0) / step)))
    h = (z1 - z0) / n
    poly = [(0.0, z0), (proud, z0)]
    for i in range(1, n):
        z = z0 + h * i
        poly += [(proud - 0.17, z), (proud, z + 0.001)]
    poly += [(proud - 0.17, z1), (0.0, z1)]
    for a, b in spans:
        if b - a < 0.4:
            continue
        ext(mb, Ff, poly, "x", a, b, SUMI)
        if lod == 0:
            for x in K.even(a + 0.3, b - 0.3, 2.3)[1:-1] if b - a > 3.0 else []:
                bb(mb, Ff, x - 0.11, x + 0.11, proud - 0.2, proud + 0.14, z0 + 0.05, z1, SUMI)


def _cut(spans, a, b):
    """tira o intervalo (a, b) da lista de vaos"""
    out = []
    for p, q in spans:
        if b <= p or a >= q:
            out.append((p, q))
            continue
        if a > p:
            out.append((p, a))
        if b < q:
            out.append((b, q))
    return out


def kato_outline(w, h, n=7):
    """contorno do KATOMADO (janela em sino): base reta, lados que se abrem para baixo, topo em arco ogival com bico"""
    hw = w / 2
    right = [(hw * 1.08, 0.0), (hw, h * 0.22), (hw * 0.97, h * 0.55)]
    for i in range(1, n + 1):
        t = i / float(n + 1)
        a = t * math.pi / 2
        right.append((hw * 0.97 * math.cos(a) ** 0.9, h * 0.55 + h * 0.38 * math.sin(a)))
    right.append((0.0, h * 1.06))
    left = [(-x, z) for x, z in reversed(right[:-1])]
    return right + left


def win3(mb, Ff, s, z, w, h, kind="renji", lod=0, bars_m=None):
    """janela V3 com PROFUNDIDADE: caixilho grosso saliente 0,62 (preto-azulado), peitoril mais fundo, fundo escuro
    0,16 a frente do reboco (o caixilho cria a sombra); 'renji' = grade vertical branca; 'kato' = katomado em sino;
    'small' = janelinha com 1 montante"""
    x0, x1 = s - w / 2, s + w / 2
    WF = FRAME
    if kind == "kato":
        ol = [(s + x, z + zz) for x, zz in kato_outline(w, h, 5 if lod == 0 else 3)]
        cz = z + h * 0.5
        out = DL.offset_poly(ol, 0.36)
        inn = ccw(ol)
        out = ccw(out)
        ring = lambda pts, y: [(x, y, zz) for x, zz in pts]
        if len(out) == len(inn):
            loft(mb, Ff, [ring(out, 0.0), ring(out, 0.58), ring(inn, 0.58), ring(inn, 0.2)], WF, caps=(False, False))
        ext(mb, Ff, inn, "y", 0.04, 0.2, DARK)
        bb(mb, Ff, x0 - 0.5, x1 + 0.5, -0.1, 0.78, z - 0.42, z, SUMI)                # peitoril
        for xx in ((s - w * 0.2, s + w * 0.2) if lod == 0 else ()):
            bb(mb, Ff, xx - 0.08, xx + 0.08, 0.2, 0.34, z, z + h * 0.95, bars_m or PL)
        return
    j = 0.36
    bb(mb, Ff, x0 - j, x0, -0.1, 0.62, z, z + h, WF)
    bb(mb, Ff, x1, x1 + j, -0.1, 0.62, z, z + h, WF)
    bb(mb, Ff, x0 - j - 0.12, x1 + j + 0.12, -0.1, 0.66, z + h, z + h + 0.42, WF)        # verga
    bb(mb, Ff, x0 - j - 0.22, x1 + j + 0.22, -0.1, 0.8, z - 0.46, z, SUMI)               # peitoril fundo
    bb(mb, Ff, x0, x1, -0.1, 0.16, z, z + h, DARK)
    if kind == "small":
        bb(mb, Ff, s - 0.09, s + 0.09, 0.16, 0.36, z, z + h, bars_m or PL)
        return
    nb = max(3, int(round(w / (0.56 if lod == 0 else 0.9))))
    for i in range(1, nb):
        xx = x0 + w * i / nb
        bb(mb, Ff, xx - 0.1, xx + 0.1, 0.16, 0.42, z, z + h, bars_m or PL)


def ishiotoshi(mb, Ff, x, z0, z1, w=3.0, d=1.6):
    """ISHI-OTOSHI (balcao de pedra-derrubada) saliente: caixa rebocada com pilaretes escuros, fundo inclinado de
    tabuas, janelinha com grade na frente e telhadinho de agua unica com testeira branca"""
    a, b = x - w / 2, x + w / 2
    bb(mb, Ff, a, b, -0.1, d, z0, z1, PL)
    ext(mb, Ff, [(-0.1, z0 - 1.3), (d, z0), (-0.1, z0)], "x", a, b, SUMI)                # fundo inclinado
    for e in (a, b):
        bb(mb, Ff, e - 0.18, e + 0.18, -0.1, d + 0.16, z0 - 0.2, z1, SUMI)
    bb(mb, Ff, a - 0.18, b + 0.18, -0.1, d + 0.2, z0 - 0.3, z0 + 0.2, SUMI)
    win3(mb, sub(Ff, 0.0, d, 0.0), x, z0 + 0.75, w * 0.5, max(0.9, (z1 - z0) - 1.6), "renji", 1)
    ext(mb, Ff, [(-0.1, z1 + 1.15), (d + 0.75, z1 + 0.25), (d + 0.75, z1 - 0.12), (-0.1, z1 + 0.7)], "x", a - 0.5,
        b + 0.5, ROOF)
    bb(mb, Ff, a - 0.5, b + 0.5, d + 0.42, d + 0.8, z1 - 0.46, z1 + 0.02, FAS)
    for e in (a - 0.5, b + 0.5):
        bb(mb, Ff, e - 0.06, e + 0.06, d + 0.4, d + 0.82, z1 - 0.5, z1 + 0.06, GOLD)


def face3(mb, Ff, ln, zb, zt, side, t=1.0, lod=0, kosh=None, rows=(), posts=(), bands=(), holes=(), ishi=(),
          ishi_z=None, head=True, board_gap=(), pz0=None, ishi_w=2.6):
    """UMA FACE de um andar V3 (referencial na face: y=0 no reboco, +y fora). Reboco de zb ate zt (com vaos 'holes'),
    shitami de zb ate zb+kosh (aberto nas janelas que descem ate ele e em board_gap), koshi-nageshi, pilares 'posts'
    entre as janelas, fileiras de janelas rows = [(z, h, w, [(s, tipo)])], faixas 'bands' (z0, z1), ishi-otoshi nos x
    de 'ishi', viga de beiral (zt-1 .. zt) e pilar de canto saliente."""
    a, b = (-ln / 2 + t, ln / 2 - t) if side else (-ln / 2, ln / 2)
    K.panel(mb, Ff, a, b, zb if pz0 is None else pz0, zt, -t, 0.0, list(holes), PL)
    zk = zb
    if kosh:
        zk = zb + kosh
        spans = [(-ln / 2, ln / 2)]
        for z, h, w, ws in rows:
            if z < zk + 0.2:
                for s, kd in ws:
                    spans = _cut(spans, s - w / 2 - 0.6, s + w / 2 + 0.6)
        for p, q in board_gap:
            spans = _cut(spans, p, q)
        boards(mb, Ff, spans, zb, zk, lod if not side else 1)        # mata-juntas so na frente (paga o orcamento)
        band(mb, Ff, -ln / 2 - 0.3, ln / 2 + 0.3, zk - 0.08, zk + 0.42, 0.52)
        zk += 0.42
    zh = zt - 1.0 if head else zt
    for x in posts:
        bb(mb, Ff, x - 0.3, x + 0.3, -0.1, 0.32, zk, zh, SUMI)
    for z0, z1 in bands:
        band(mb, Ff, -ln / 2 - 0.3, ln / 2 + 0.3, z0, z1, 0.4)
    for z, h, w, ws in rows:
        for s, kd in ws:
            win3(mb, Ff, s, z, w, h, kd, lod)
    for x in ishi:
        ishiotoshi(mb, Ff, x, ishi_z[0], ishi_z[1], ishi_w)
    if head:
        band(mb, Ff, -ln / 2 - 0.3, ln / 2 + 0.3, zt - 1.0, zt, 0.5)
    bb(mb, Ff, ln / 2 - 0.75, ln / 2 + 0.5, -0.75, 0.5, zb, zt, SUMI)                    # pilar de canto


def rafters(mb, F, sk, keys="FRL", step=1.5, skip=None, fas=0.8):
    """CAIBROS brancos (nurigome) sob o beiral de cada saia, com as pontas PENDENDO 0,5 abaixo da testeira: a FRANJA
    SERRILHADA clara sob os telhados escuros do castelo do anime (le de lado e de baixo). Fora dos cantos (espigao) e
    do sino do karahafu (skip = {face: meia largura})."""
    skip = skip or {}
    for key, Fk in _face_frames(F):
        if key not in keys:
            continue
        H, A, Ao, Bi, Bo = sk[key]
        ya, yb_ = Bo - 2.4, Bo - 0.5
        xm = A + (ya - Bi) * (Ao - A) / (Bo - Bi) - 0.5
        for x in K.even(-xm, xm, step):
            if abs(x) < skip.get(key, -1.0):
                continue
            zt_ = H(x, yb_ + 0.2) - 0.6 - fas + 0.12
            bb(mb, Fk, x - 0.22, x + 0.22, ya, yb_, zt_ - 0.62, zt_, FAS)


def mon(mb, Ff, x, z, R, y=0.0, n=10):
    """brasao economico em disco (para timpanos): placa escura, anel dourado, miolo escuro, botao e 8 petalas de ouro"""
    lathe_y(mb, Ff, (x, y, z), [(R * 1.28, 0.0), (R * 1.28, 0.14)], n, SUMI)
    lathe_y(mb, Ff, (x, y, z), [(R, 0.14), (R, 0.3)], n, GOLD)
    lathe_y(mb, Ff, (x, y, z), [(R * 0.78, 0.3), (R * 0.78, 0.44)], n, SUMI)
    lathe_y(mb, Ff, (x, y, z), [(R * 0.22, 0.44), (R * 0.22, 0.6)], 8, GOLD)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        bx(mb, Ff, x + R * 0.5 * math.cos(a), y + 0.5, z + R * 0.5 * math.sin(a), R * 0.36, 0.14, R * 0.18, GOLD, 0.0,
           ry=-a)


def chidori3(mb, F, Hf, tv, xc, w, yd, zr, lod=0, P=1.8, amp=0.27, crest_on=True):
    """CHIDORI-HAFU do castelo V3 (mesma geometria do K2._chidori, timpano ORNAMENTADO): aguas onduladas, timpano de
    reboco com tirante escuro, treliça KITSUNE-GOSHI (preto-azulado) no triangulo de cima, painel com o BRASAO (disco
    de ouro) entre tirante e treliça, tabeiras brancas com cravos dourados, GEGYO DOURADO e cumeeira com onigawara"""
    X, ovc = w / 2, 0.9
    yfront = yd + ovc
    pc = 1.0
    zt = Hf(xc + X + ovc, yfront) + 0.5 + pc * (X + ovc)
    if zt > zr - 0.6:
        zt = zr - 0.6
        pc = (zt - Hf(xc + X + ovc, yfront) - 0.5) / (X + ovc)
    yb = yd
    while yb > 0.3 and Hf(xc, yb) < zt + 0.4:
        yb -= 0.25
    tvc = tv * 0.8
    Hs = lambda u, v: zt - pc * abs(v)
    Fa = sub(F, xc, 0.0, 0.0, -math.pi / 2)
    Fb = sub(F, xc, 0.0, 0.0, math.pi / 2)
    K2.tiles(mb, Fa, K2._wave(-yfront, -yb, P * 0.8, amp * 0.85, lod), lambda u: 0.0, X + ovc, Hs, ROOF, tvc,
             soffit=SOFFIT, rows=(0.0, 0.5, 1.0))
    K2.tiles(mb, Fb, K2._wave(yb, yfront, P * 0.8, amp * 0.85, lod), lambda u: 0.0, X + ovc, Hs, ROOF, tvc,
             soffit=SOFFIT, rows=(0.0, 0.5, 1.0))
    zbase = Hf(xc, yd) - 0.3
    top = lambda x: zt - pc * abs(x - xc) - tvc - 0.06
    Xi = X
    while Xi > 0.5 and top(xc + Xi) < zbase + 0.3:
        Xi -= 0.1
    poly = [(xc - Xi, zbase), (xc + Xi, zbase), (xc + Xi, top(xc + Xi)), (xc, top(xc)), (xc - Xi, top(xc - Xi))]
    ext(mb, F, poly, "y", yd - 0.5, yd - 0.28, PL)
    yo0, yo1 = yd - 0.28, yd - 0.1
    hgt = top(xc) - zbase
    # tirante (kiri-otoshi) escuro na base, com cantoneiras douradas
    zt0 = zbase + 0.15
    zt1 = zt0 + (0.7 if hgt > 4.0 else 0.5)
    xa = Xi
    while xa > 0.5 and top(xc + xa) < zt1 + 0.2:
        xa -= 0.1
    bb(mb, F, xc - xa, xc + xa, yo0, yo1 + 0.1, zt0, zt1, SUMI)
    for s in (-1, 1):
        bb(mb, F, xc + s * xa - 0.35, xc + s * xa + 0.35, yo0 - 0.02, yo1 + 0.16, zt0 - 0.04, zt1 + 0.04, GOLD)
    # painel do brasao + treliça
    zl = zt1
    if crest_on and hgt > 4.2:
        R = min(1.15, (hgt - 1.0) * 0.17)
        zc = zt1 + 0.45 + R * 1.28
        mon(mb, F, xc, zc, R, yo0)
        zl = zc + R * 1.28 + 0.5
    if top(xc) - zl > 1.0 and lod == 0:
        step = 0.95
        n = int((Xi - 0.3) / step)
        for i in range(-n, n + 1):
            x = xc + i * step
            zz = top(x) - 0.35
            if zz - zl > 0.3:
                bb(mb, F, x - 0.07, x + 0.07, yo0, yo0 + 0.16, zl, zz, SUMI)
        z = zl
        while z < top(xc) - 0.6:
            hx = (top(xc) - 0.35 - z) / max(pc, 0.3)
            if hx > 0.4:
                bb(mb, F, xc - hx, xc + hx, yo0, yo0 + 0.14, z - 0.06, z + 0.06, SUMI)
            z += step
    # tabeiras brancas (hafu) com cravos dourados
    for s in (-1, 1):
        K.strip(mb, F, [(xc + s * (X + ovc) * u, yfront - 0.12, Hs(0, (X + ovc) * u) - tvc) for u in (0.0, 0.5, 1.0)],
                (0, 1, 0), -0.17, 0.17, -0.8, 0.06, FAS)
        for u in (0.38, 0.72):
            xx = xc + s * (X + ovc) * u
            zz = Hs(0, (X + ovc) * u) - tvc - 0.4
            bb(mb, F, xx - 0.22, xx + 0.22, yfront + 0.05, yfront + 0.16, zz - 0.22, zz + 0.22, GOLD)
    Fg = sub(F, xc, 0.0, 0.0, math.pi / 2)
    K._gegyo(mb, Fg, yfront - 0.12, zt - tvc - 0.8, 1, GOLD, 1.05, True)
    K.ridge(mb, Fg, yb, yfront + 0.15, zt + 0.12, pc, 1.4, True, 0.7, True, 1, (False, True))


def gibo3(mb, F, x, y, z, s=1.0):
    """giboshi dourado ECONOMICO (5 lados, bulbo + ponta): le igual ao do kit a distancia, 1/3 dos tris"""
    lathe(mb, F, (x, y, z), [(0.25 * s, 0.0), (0.31 * s, 0.3 * s), (0.13 * s, 0.6 * s), (0.02 * s, 0.82 * s)], 5, GOLD)


def rail3(mb, F, pts, h=2.6, step=2.6, gibo_every=1, struts=0.0, m=None):
    """GUARDA-CORPO VERMELHO V3: pilaretes 0,4 com GIBOSHI DOURADO (todos ou 1 a cada n + cantos), corrimao grosso
    (kasagi) que passa das pontas com ponteiras douradas, travessa media, rodape e balaustres curtos (tsuka) entre
    rodape e travessa a cada 'struts' (0 = sem). pts = [(x, y)] no referencial F (z=0 no piso)."""
    m = m or LAC
    P_ = [Vector((p[0], p[1], 0.0)) for p in pts]
    k = 0
    for i, (a, b) in enumerate(zip(P_, P_[1:])):
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        ang = math.atan2(d.y, d.x)
        c = (a + b) / 2
        e = 0.3
        bx(mb, F, c.x, c.y, h - 0.17, ln + 2 * e, 0.5, 0.34, m, 0.0, rz=ang)                  # kasagi
        bx(mb, F, c.x, c.y, h * 0.58, ln, 0.18, 0.22, m, 0.0, rz=ang)                        # hira-geta
        bx(mb, F, c.x, c.y, 0.3, ln, 0.26, 0.26, m, 0.0, rz=ang)                            # ji-fuku
        nseg = max(1, int(math.ceil(ln / step)))
        for j in range(nseg + (1 if i == len(P_) - 2 else 0)):
            q = a + d * (j / nseg)
            corner = j == 0 or (i == len(P_) - 2 and j == nseg)
            bx(mb, F, q.x, q.y, (h - 0.34) / 2, 0.42, 0.42, h - 0.34, m, 0.0, rz=ang)
            if corner or (gibo_every and k % gibo_every == 0):
                gibo3(mb, F, q.x, q.y, h, 1.1 if corner else 0.95)
            k += 1
        if struts:
            for t in K.even(0.0, ln, struts):
                q = a + d * (t / ln)
                bx(mb, F, q.x, q.y, (0.43 + h * 0.58 - 0.11) / 2, 0.16, 0.16, h * 0.58 - 0.11 - 0.43, m, 0.0, rz=ang)
    for q in (P_[0], P_[-1]):                                       # ponteiras douradas do kasagi
        bx(mb, F, q.x, q.y, h - 0.17, 0.62, 0.62, 0.44, GOLD, 0.0)


# ================================================================== TORRE (5 andares)
# saias: (Xi, Yi) = parede de cima, (Xe, Ye) = beiral, z_top (junto da parede de cima), queda ate o beiral
# V3: volumes de cima MAIS ESBELTOS (afunila mais: 0,88 / 0,84 / 0,84 da envoltoria travada de L.KEEP_TIERS) e o 5o
# andar 3 studs MAIS ALTO (presenca na silhueta vista da praca e da avenida); saias com mais queda (o telhado domina)
VT = [T[0]] + [(T[i][0] * k, T[i][1] * k) + tuple(T[i][2:]) for i, k in ((1, 0.88), (2, 0.84), (3, 0.84))]
TOP_EXTRA = 3.0
R0 = (T[0][0], T[0][1], T[0][0] + 4.4, T[0][1] + 4.4, 16.0, 2.3)             # mokoshi do 1o volume (sobre o salao)
R1 = (VT[1][0], VT[1][1], T[0][0] + 4.6, T[0][1] + 4.6, T[1][2] + 0.6, 6.8)     # 1o volume -> 3o andar
R2 = (VT[2][0], VT[2][1], VT[1][0] + 4.3, VT[1][1] + 4.3, T[2][2] + 0.6, 6.6)     # 3o -> 4o andar
R3 = (VT[3][0], VT[3][1], VT[2][0] + 3.9, VT[2][1] + 3.9, T[3][2] + 0.6, 5.6)     # 4o -> 5o andar
KARA0 = (16.0, 3.0)                     # karahafu dourado sobre a porta (largura, subida do sino)
KARA3 = (12.0, 2.4)                     # karahafu de R3 (frente)
PORCH_X, PORCH_Y = 6.6, 3.85            # pilares do portico (x, distancia da parede)
ENG_D, ENG_Z, ENG_H = 3.0, PLINTH + 0.5, 2.3    # ENGAWA vermelha do terreo: fundura, piso, altura do guarda-corpo
ENG_X0 = PORCH_X + 1.5                  # a engawa da frente para antes do portico
TOP_RINFO = {}


def engawa(mb, F):
    """ENGAWA (varanda vermelha) em volta do terreo, sobre a capa da cantaria: assoalho, testeira vermelha com
    cantoneiras douradas, misulas escuras, guarda-corpo vermelho com giboshi dourados (o 2o nivel de balaustrada;
    o anel vermelho da base do castelo do anime). Aberta so no portico."""
    hx0, hy0 = T[0][0], T[0][1]
    for k, Ff, ln, d in faces(F, hx0, hy0):
        if k in "FB":
            spans = [(-ln / 2 - ENG_D, -ENG_X0), (ENG_X0, ln / 2 + ENG_D)] if k == "F" else [(-ln / 2 - ENG_D, ln / 2 + ENG_D)]
        else:
            spans = [(-ln / 2, ln / 2)]
        for a, b in spans:
            bb(mb, Ff, a, b, -0.1, ENG_D, ENG_Z - 0.32, ENG_Z, WM)
            bb(mb, Ff, a, b, ENG_D - 0.4, ENG_D + 0.06, ENG_Z - 0.95, ENG_Z - 0.3, LAC)
            for e in (a, b):
                if abs(abs(e) - (ln / 2 + ENG_D)) < 0.01 or k == "F":
                    bb(mb, Ff, e - 0.4, e + 0.4, ENG_D - 0.46, ENG_D + 0.12, ENG_Z - 1.0, ENG_Z - 0.26, GOLD)
            for x in K.even(a + 0.6, b - 0.6, 4.0 if k == "F" else 6.0):
                K2.bracket2(mb, Ff, x, 1.0, ENG_D - 1.45, ENG_Z - 0.32, 0.42, 1.2, SUMI, False)
    Y, Xr = hy0 + ENG_D - 0.3, hx0 + ENG_D - 0.3
    ring = [(ENG_X0, hy0 + 0.4), (ENG_X0, Y), (Xr, Y), (Xr, -Y), (-Xr, -Y), (-Xr, Y), (-ENG_X0, Y), (-ENG_X0, hy0 + 0.4)]
    rail3(mb, sub(F, 0.0, 0.0, ENG_Z), ring, ENG_H, 3.1, 3, 0.0)
    return ring


def engawa_cols(F):
    hx0, hy0 = T[0][0], T[0][1]
    for k, Ff, ln, d in faces(F, hx0, hy0):
        if k in "FB":
            spans = [(-ln / 2 - ENG_D, -ENG_X0), (ENG_X0, ln / 2 + ENG_D)] if k == "F" else [(-ln / 2 - ENG_D, ln / 2 + ENG_D)]
        else:
            spans = [(-ln / 2, ln / 2)]
        for a, b in spans:
            col_box("OP_CasEngawa", (b - a, ENG_D, ENG_Z), Ff.p((a + b) / 2, ENG_D / 2, ENG_Z / 2), Ff.r())
            col_box("OP_CasEngawa", (b - a, 0.7, ENG_Z + ENG_H), Ff.p((a + b) / 2, ENG_D - 0.3, (ENG_Z + ENG_H) / 2),
                    Ff.r())
    Ff = faces(F, hx0, hy0)[0][1]
    for s in (-1, 1):                                       # pontas da engawa no portico
        col_box("OP_CasEngawa", (0.7, ENG_D, ENG_Z + ENG_H), Ff.p(s * ENG_X0, ENG_D / 2, (ENG_Z + ENG_H) / 2), Ff.r())


def keep(mb):
    F = keep_frame()
    hx0, hy0 = T[0][0], T[0][1]
    # ---- base de cantaria (talude) com a passagem da porta
    gap = (-DOOR_W / 2 - 1.1, DOOR_W / 2 + 1.1)
    ishigaki_keep(mb, F, hx0 + 0.8, hy0 + 0.8, PLINTH, -0.6, 20.0, "kp", gap)
    Ff = faces(F, hx0, hy0)[0][1]
    for s in (-1, 1):                                       # bochechas da passagem (pedra escura aparelhada)
        x = s * (DOOR_W / 2 + 0.55)
        bb(mb, Ff, x - 0.55, x + 0.55, -0.2, 2.5, -0.3, PLINTH + 0.2, ST)
        bb(mb, Ff, x - 0.7, x + 0.7, -0.2, 2.7, PLINTH + 0.2, PLINTH + 0.55, STP)
    bb(mb, Ff, -DOOR_W / 2 - 0.2, DOOR_W / 2 + 0.2, 0.0, 2.6, -0.3, 0.22, STP)            # degrau de pedra
    for k, Fw, ln, d in faces(F, hx0, hy0):                 # soleira escura sobre a cantaria (mizukiri)
        bb(mb, Fw, -ln / 2 - 0.2, ln / 2 + 0.2, -0.3, 0.3, PLINTH, PLINTH + 0.5, SUMI)
    engawa(mb, F)
    # ---- telhados (de cima para baixo: cada saia define o topo das paredes de baixo)
    rw = (0.0, 0.18, 0.45, 1.0)                         # V3: 4 fileiras (paga caibros/frontoes)
    s3 = cskirt(mb, F, *R3, kara={"F": KARA3}, lod=0, back_lod=1, up=3.6, lift=1.6, P=2.3, rows=rw)
    s2 = cskirt(mb, F, *R2, lod=0, back_lod=1, up=4.6, lift=1.9, oni=False, P=2.3, rows=rw)
    s1 = cskirt(mb, F, *R1, lod=0, back_lod=1, up=3.6, lift=2.1, P=2.4, rows=rw)
    s0 = cskirt(mb, F, *R0, kara={"F": KARA0}, kara_gold=True, lod=0, back_lod=1, lift=0.9, conc=1.8,
                rows=(0.0, 0.3, 0.65, 1.0), P=2.4)
    # frontoes V3 (timpano ornamentado): R1 par na frente + 1 nos lados/fundos, R2 grande na frente/fundos e nos lados;
    # R3 so com o karahafu na frente (os chidori laterais de R3 furavam o piso da varanda do 5o andar na V2)
    for sk, z_top, up, lst in ((s1, R1[4], 3.6, {"F": [(-10.6, 10.0)], "B": [(0.0, 13.0)], "R": [(0.0, 12.0)],
                                                  "L": [(0.0, 12.0)]}),
                               (s2, R2[4], 4.6, {"F": [(0.0, 14.0)], "B": [(0.0, 14.0)], "R": [(0.0, 10.0)],
                                                 "L": [(0.0, 10.0)]}),
                               ):
        for key, Fk in _face_frames(F):
            H, A, Ao, Bi, Bo = sk[key]
            items = list(lst.get(key, ()))
            if sk is s1 and key == "F":
                items = [(-10.6, 10.0), (10.6, 10.0)]
            for xc, w in items:
                chidori3(mb, Fk, H, 0.6 * 0.85, xc, w, Bi + (Bo - Bi) * 0.55, z_top + up, 0 if key == "F" else 1,
                         1.8, 0.27, key != "B")
    rafters(mb, F, s0, "F", 1.6, {"F": KARA0[0] / 2 + 0.6})
    rafters(mb, F, s0, "RL", 1.9)
    rafters(mb, F, s1, "F", 1.65)
    rafters(mb, F, s1, "RL", 1.75)
    rafters(mb, F, s2, "F", 1.6)
    rafters(mb, F, s2, "RL", 1.7)
    rafters(mb, F, s3, "FRL", 1.4, {"F": KARA3[0] / 2 + 0.6})
    top = lambda sk, hx, hy: {"F": wall_top(sk, "F", hy), "B": wall_top(sk, "B", hy), "R": wall_top(sk, "R", hx),
                              "L": wall_top(sk, "L", hx)}
    # ---- andar 1 (salao): reboco de 2 com as janelas de papel; shitami ate 9,6; friso com janelinhas e pilares
    zt0 = R0[4] + 0.3
    hall_posts = {"F": [-24.3, -20.6, -13.5, -7.6, 7.6, 13.5, 20.6, 24.3], "B": [-24.3, -20.6, -10.8, 0.0, 10.8, 20.6, 24.3],
                  "R": [-18.6, -9.4, 0.0, 9.4, 18.6], "L": [-18.6, -9.4, 0.0, 9.4, 18.6]}
    for k, Fw, ln, d in faces(F, hx0, hy0):
        side = k in "RL"
        holes = [(s - 1.5, s + 1.5, 5.8, 8.8) for s in HALL_WINS[k]]
        if k == "F":
            holes.append((-DOOR_W / 2, DOOR_W / 2, -1.0, FLOOR + DOOR_H))
        lod = 1 if k == "B" else 0
        up_row = [(s, "renji" if k == "F" else "small") for s in HALL_WINS[k]] if not lod else []
        gaps = [(s - 1.86, s + 1.86) for s in HALL_WINS[k]] + ([(-ENG_X0 + 0.3, ENG_X0 - 0.3)] if k == "F" else [])
        face3(mb, Fw, ln, ENG_Z, zt0, side, 2.0, lod, kosh=9.6 - ENG_Z, rows=[(11.3, 1.7, 2.4, up_row)],
              posts=hall_posts[k], holes=holes, board_gap=gaps, pz0=0.0)
        for s in HALL_WINS[k]:
            cwin(mb, Fw, s, 5.8, 3.0, 3.0, 2.0, "hall", 0)
    # ---- andar 2 (mezanino do 1o volume): galeria de janelas entre pilares, de R0 ate sob R1
    t1 = top(s1, hx0, hy0)
    wm = {"F": [-25.0, -19.5, -14.0, 14.0, 19.5, 25.0], "B": [-21.0, -7.0, 7.0, 21.0],
          "R": [-14.0, 0.0, 14.0], "L": [-14.0, 0.0, 14.0]}
    pm = {"F": [-22.25, -16.75, -11.0, 11.0, 16.75, 22.25], "B": [-14.0, 0.0, 14.0], "R": [-19.0, -7.0, 7.0, 19.0],
          "L": [-19.0, -7.0, 7.0, 19.0]}
    for k, Fw, ln, d in faces(F, hx0, hy0):
        lod = 1                                             # mezanino: quase todo na sombra entre R0 e R1
        face3(mb, Fw, ln, R0[4] - 0.3, t1[k], k in "RL", 1.0, lod,
              rows=[(16.95, 1.8, 2.3, [(s, "renji") for s in wm[k]])], posts=pm[k], head=False,
              bands=[(t1[k] - 0.55, t1[k])])
    # ---- andar 3 (volume 1): shitami alto, 2 fileiras de janelas, ishi-otoshi nos cantos
    hx1, hy1 = VT[1][0], VT[1][1]
    t2 = top(s2, hx1, hy1)
    z1b = R1[4] - 0.2
    for k, Fw, ln, d in faces(F, hx1, hy1):
        lod = 1 if k == "B" else 0
        nb = 6 if k in "FB" else 5
        bay = (ln - 2 * 3.6) / nb if k in "FB" else (ln - 2.0) / nb
        x0 = -bay * nb / 2
        ws = [x0 + bay * (i + 0.5) for i in range(nb)]
        ps = [x0 + bay * i for i in range(nb + 1)]
        zt_ = t2[k]
        ra = 30.0
        rb = max(ra + 3.4, zt_ - 1.0 - 0.5 - 1.5)
        face3(mb, Fw, ln, z1b, zt_, k in "RL", 1.0, lod, kosh=28.0 - z1b,
              rows=[(ra, 2.5, 2.3, [(s, "renji") for s in ws]),
                    (rb, 1.4, 1.6, [(s, "small") for s in (ws if k == "F" else ws[1::2])])],
              posts=ps, bands=[(ra + 2.5 + 0.55, ra + 2.5 + 0.95)],
              ishi=[-ln / 2 + 2.0, ln / 2 - 2.0] if k == "F" else (), ishi_z=(ra + 0.4, rb + 0.8))
    # ---- andar 4 (volume 2): shitami, fileira de janelas com KATOMADO alternado, friso com pilares
    hx2, hy2 = VT[2][0], VT[2][1]
    t3 = top(s3, hx2, hy2)
    z2b = R2[4] - 0.2
    for k, Fw, ln, d in faces(F, hx2, hy2):
        lod = 1 if k == "B" else 0
        nb = 5 if k in "FB" else 4
        bay = (ln - 2.4) / nb
        x0 = -bay * nb / 2
        ws = [x0 + bay * (i + 0.5) for i in range(nb)]
        ps = [x0 + bay * i for i in range(nb + 1)]
        kinds = [("kato" if (0.4 < abs(i - (nb - 1) / 2.0) < 1.2 and lod == 0) else "renji") for i in range(nb)]
        face3(mb, Fw, ln, z2b, t3[k], k in "RL", 1.0, lod, kosh=44.9 - z2b,
              rows=[(46.8, 2.8, 2.3, [(s, kd) for s, kd in zip(ws, kinds)])], posts=ps,
              bands=[(50.6, 51.0)])
    # ---- portico do karahafu dourado (pilares, viga, timpano com o brasao)
    H0 = s0["F"][0]
    Fp = Ff
    for s in (-1, 1):
        x = s * PORCH_X
        zt = H0(x, hy0 + PORCH_Y) - 0.6 - 0.8
        K.rock_base(mb, Fp, x, PORCH_Y, 0.0, 0.9, 0.5)
        bb(mb, Fp, x - 0.4, x + 0.4, PORCH_Y - 0.4, PORCH_Y + 0.4, 0.3, zt, LAC, 0.06)
        bb(mb, Fp, x - 0.47, x + 0.47, PORCH_Y - 0.47, PORCH_Y + 0.47, 0.3, 0.8, IRON)
        bb(mb, Fp, x - 0.5, x + 0.5, PORCH_Y - 0.5, PORCH_Y + 0.5, zt - 0.7, zt - 0.3, GOLD)
        beam(mb, Fp, (x, PORCH_Y, zt - 1.2), (x, 0.0, zt - 1.2), 0.45, 0.55, LAC)
    zk = H0(PORCH_X, hy0 + PORCH_Y) - 0.6 - 0.8 - 1.6
    bb(mb, Fp, -PORCH_X - 0.6, PORCH_X + 0.6, PORCH_Y - 0.42, PORCH_Y + 0.42, zk - 0.8, zk, LAC)          # kashira-nuki
    bb(mb, Fp, -PORCH_X - 0.75, PORCH_X + 0.75, PORCH_Y - 0.5, PORCH_Y + 0.5, zk, zk + 0.3, GOLD)
    yv = PORCH_Y + 0.05
    xs = [-PORCH_X + 0.4 + (2 * PORCH_X - 0.8) * i / 16 for i in range(17)]
    tops = [(x, H0(x, hy0 + yv) - 0.6 - 0.85) for x in xs]
    ext(mb, Fp, [(xs[0], zk + 0.3), (xs[-1], zk + 0.3)] + list(reversed(tops)), "y", yv - 0.35, yv - 0.15, PL)
    zc = (zk + 0.3 + min(z for _, z in tops)) / 2 + 0.3
    mon(mb, Fp, 0.0, zc, 1.0, yv - 0.15, 12)
    for s in (-1, 1):                                       # montantes dourados do timpano
        x = s * 3.4
        bb(mb, Fp, x - 0.14, x + 0.14, yv - 0.13, yv + 0.02, zk + 0.3, H0(x, hy0 + yv) - 0.6 - 0.9, GOLD)
    # porta: caixilho, verga, folhas ABERTAS para dentro (madeira escura, cintas de ferro, cravos dourados)
    for s in (-1, 1):
        x = s * (DOOR_W / 2 + 0.3)
        bb(mb, Fp, x - 0.3 - (ZG if s > 0 else 0.0), x + 0.3 + (ZG if s < 0 else 0.0), -2.25, 0.2, FLOOR - 0.3,
           FLOOR + DOOR_H + 0.5, WD)
    bb(mb, Fp, -DOOR_W / 2 - 0.6, DOOR_W / 2 + 0.6, -2.25, 0.2, FLOOR + DOOR_H - ZG, FLOOR + DOOR_H + 0.7, WD)
    bb(mb, Fp, -DOOR_W / 2, DOOR_W / 2, -2.1, 0.0, -0.3, FLOOR, WD)
    for s in (-1, 1):
        x = s * (DOOR_W / 2 - 0.2)
        y0, y1 = -2.1, -2.1 - DOOR_W / 2 + 0.2
        bb(mb, Fp, min(x, x - s * 0.36), max(x, x - s * 0.36), y1, y0, FLOOR + 0.05, FLOOR + DOOR_H - 0.1, WD)
        xf = x - s * 0.36
        for zz in (FLOOR + 1.2, FLOOR + DOOR_H / 2, FLOOR + DOOR_H - 1.3):
            bb(mb, Fp, min(xf, xf - s * 0.12), max(xf, xf - s * 0.12), y1 + 0.1, y0 - 0.1, zz - 0.18, zz + 0.18, IRON)
            for yy in K.even(y1 + 0.3, y0 - 0.3, 0.9):
                bb(mb, Fp, min(xf, xf - s * 0.22), max(xf, xf - s * 0.22), yy - 0.09, yy + 0.09, zz - 0.09, zz + 0.09, GOLD)
    # ---- andar 5 (mais alto): portas de correr para a varanda, katomado, friso; VARANDA VERMELHA rica; irimoya
    hx3, hy3, z03, hw3, over3 = VT[3]
    h3 = z03 + hw3 + TOP_EXTRA
    zb = R3[4] + 0.75                                       # piso da varanda
    doors = {"F": [-3.9, 3.9], "B": [-3.9, 3.9]}
    for k, Fw, ln, d in faces(F, hx3, hy3):
        side = k in "RL"
        lod = 1 if k == "B" else 0
        dz = zb + 0.05
        holes = [(s - 1.9, s + 1.9, dz - 0.15, dz + 5.5) for s in doors.get(k, ())]
        if k in "FB":
            rows = [(dz + 7.3, 2.6, 2.0, [(-3.9, "kato" if not lod else "renji"), (3.9, "kato" if not lod else "renji")]),
                    (dz + 7.6, 2.0, 1.2, [(0.0, "small")])]
            ps = [-6.6, -1.4, 1.4, 6.6]
        else:
            rows = [(dz + 1.6, 2.8, 2.3, [(-4.6, "renji"), (0.0, "kato" if not lod else "renji"), (4.6, "renji")]),
                    (dz + 7.6, 2.0, 1.6, [(-4.6, "small"), (0.0, "small"), (4.6, "small")])]
            ps = [-6.9, -2.3, 2.3, 6.9]
        face3(mb, Fw, ln, z03 - 0.6, h3, side, 1.0, lod, rows=rows, posts=ps, bands=[(dz + 5.9, dz + 6.4)],
              holes=holes)
        for s in doors.get(k, ()):
            z0d = dz
            bb(mb, Fw, s - 2.0, s - 1.7, -0.9, 0.3, z0d, z0d + 5.4, SUMI)
            bb(mb, Fw, s + 1.7, s + 2.0, -0.9, 0.3, z0d, z0d + 5.4, SUMI)
            for a_, y_ in ((-1.7, -0.62), (0.0, -0.42)):
                bb(mb, Fw, s + a_, s + a_ + 1.7, y_ - 0.08, y_ + 0.08, z0d, z0d + 5.3, SUMI)
                bb(mb, Fw, s + a_ + 0.25, s + a_ + 1.45, y_ - 0.16, y_ - 0.06, z0d + 1.4, z0d + 5.0, PL)
                bb(mb, Fw, s + a_ + 0.79, s + a_ + 0.91, y_ - 0.2, y_ - 0.08, z0d + 1.4, z0d + 5.0, SUMI)
                bb(mb, Fw, s + a_ + 0.25, s + a_ + 1.45, y_ - 0.2, y_ - 0.08, z0d + 3.15, z0d + 3.27, SUMI)
    dep = 2.7
    Xb, Yb = hx3 + dep, hy3 + dep
    for k, Fw, ln, d in faces(F, hx3, hy3):
        bb(mb, Fw, -ln / 2 - dep, ln / 2 + dep, 0.0, dep, zb - 0.32, zb, WM)
        bb(mb, Fw, -ln / 2 - dep, ln / 2 + dep, dep - 0.5, dep + 0.06, zb - 0.95, zb - 0.3, LAC)       # testeira
        for e in (-ln / 2 - dep, ln / 2 + dep):
            bb(mb, Fw, e - 0.42, e + 0.42, dep - 0.56, dep + 0.12, zb - 1.0, zb - 0.26, GOLD)
        for x in K.even(-ln / 2 + 0.6, ln / 2 - 0.6, 2.6):
            K2.bracket2(mb, Fw, x, -0.2, dep - 0.35, zb - 0.32, 0.4, 1.5, SUMI, k == "F")
    Fz = sub(F, 0.0, 0.0, zb)
    ring = [(-Xb + 0.25, -Yb + 0.25), (Xb - 0.25, -Yb + 0.25), (Xb - 0.25, Yb - 0.25), (-Xb + 0.25, Yb - 0.25),
            (-Xb + 0.25, -Yb + 0.25)]
    rail3(mb, Fz, ring, 3.0, 2.4, 2, 2.0)
    with plastered():
        rinfo = K2.roof2(mb, F, 2 * hx3, 2 * hy3, h3, "irimoya", ROOF, ov=4.2, g_over=1.7, s0=0.44, s1=1.05,
                         lift=1.8, tv=0.6, dg=0.45, lod=0, back_lod=1, gable_m=PL, gable_style="timber", gold=True,
                         courses=2, rafters=False, hafu_m=FAS, ridge_w=2.6, P=2.4)
    TOP_RINFO.clear()
    TOP_RINFO.update(rinfo)
    Hf, Xe, Ye = rinfo["Hf"], rinfo["Xe"], rinfo["Ye"]
    for x in K.even(-Xe + 3.0, Xe - 3.0, 1.6):                 # caibros brancos do beiral de cima (frente)
        ya, yb_ = Ye - 2.2, Ye - 0.5
        zt_ = Hf(x, Ye - 0.3) - 0.6 - 0.62 + 0.12             # pendem abaixo da testeira (franja serrilhada)
        bb(mb, F, x - 0.2, x + 0.2, ya, yb_, zt_ - 0.58, zt_, FAS)
    xs_ = rinfo["Xg"] + 1.7 - 0.2
    for s in (-1, 1):
        shachi(mb, F, s * xs_, rinfo["top"] - 2.0 - 0.45, s, 1.12)
    Xg = rinfo["Xg"]                                        # brasao de ouro nas empenas do irimoya de cima (lados)
    zg = Hf(Xg, 0.0) - 0.6 - 2.6
    for s in (-1, 1):
        mon(mb, sub(F, 0.0, 0.0, 0.0, -s * math.pi / 2), 0.0, zg, 0.9, Xg - 0.5, 10)
    return F


def keep_cols():
    F = keep_frame()
    hx0, hy0 = T[0][0], T[0][1]
    for k, Fw, ln, d in faces(F, hx0, hy0):                 # paredes do terreo (porta aberta na frente)
        side = k in "RL"
        a, b = (-ln / 2 + 2.0, ln / 2 - 2.0) if side else (-ln / 2 - 0.8, ln / 2 + 0.8)     # V3: cobre os cantos
        spans = [(a, -DOOR_W / 2), (DOOR_W / 2, b)] if k == "F" else [(a, b)]
        for x0, x1 in spans:
            p = Fw.p((x0 + x1) / 2, -0.6, 11.5)
            col_box("OP_CasKeep", (x1 - x0, 2.8, 23.0), p, Fw.r())
        if k == "F":
            p = Fw.p(0.0, -0.6, (FLOOR + DOOR_H + 23.0) / 2)
            col_box("OP_CasKeep", (DOOR_W, 2.8, 23.0 - FLOOR - DOOR_H), p, Fw.r())
            for s in (-1, 1):
                x0, x1 = (DOOR_W / 2 + 0.0, hx0 + 2.4) if s > 0 else (-hx0 - 2.4, -DOOR_W / 2)
                col_box("OP_CasKeep", (x1 - x0, 2.4, PLINTH), Fw.p((x0 + x1) / 2, 1.2, PLINTH / 2), Fw.r())
        # V3: fundos/lados - a colisao da ENGAWA (piso ate 5,0, fundura 3,0) cobre a capa da cantaria
    engawa_cols(F)
    col_box("OP_CasKeepCeil", (2 * hx0 - 4.0, 2 * hy0 - 4.0, 0.8), F.p(0, 0, 12.85), F.r())
    col_box("OP_CasHall", (2 * hx0 - 4.0, 2 * hy0 - 2.0, 0.95), F.p(0, 1.0, FLOOR - 0.475), F.r())
    col_box("OP_CasHall", (DOOR_W + 0.8, 2.6, 0.52), F.p(0, hy0 + 1.3, 0.22 - 0.26), F.r())
    col_box("OP_CasKeepUpper", (2 * hx0, 2 * hy0, 10.0), F.p(0, 0, 13.25 + 5.0), F.r())
    for i in (1, 2, 3):
        hx, hy, z0, hw, over = VT[i]
        za, zb_ = z0 - 1.0, z0 + hw + 3.0
        col_box("OP_CasKeepUpper", (2 * hx, 2 * hy, zb_ - za), F.p(0, 0, (za + zb_) / 2), F.r())
    # saia R0 (a mais baixa: o portico encosta nela) e portico
    Ff = faces(F, hx0, hy0)[0][1]
    for k, Fw, ln, d in faces(F, hx0, hy0):
        col_box("OP_CasKeepUpper", (ln + 8.8, 4.6, 3.2), Fw.p(0.0, 2.2, 14.4), Fw.r())
    for s in (-1, 1):
        col_box("OP_CasKeep", (1.6, 1.6, 12.0), Ff.p(s * PORCH_X, PORCH_Y, 6.0), Ff.r())
    for s in (-1, 1):                                       # folhas da porta abertas (para dentro)
        col_box("OP_CasHall", (0.5, DOOR_W / 2, DOOR_H), Ff.p(s * (DOOR_W / 2 - 0.38), -2.1 - DOOR_W / 4 + 0.1,
                                                            FLOOR + DOOR_H / 2), Ff.r())


# ================================================================== SALAO (terreo acessivel) COM VIDA
HALL_WINS = {"F": [-17.0, -10.0, 10.0, 17.0], "B": [-16.0, -5.5, 5.5, 16.0], "R": [-14.0, -4.7, 4.7, 14.0],
             "L": [-14.0, -4.7, 4.7, 14.0]}
HALL_COLS = [(sx * 15.0, y) for sx in (-1, 1) for y in (-10.0, 0.0, 10.0)]
HALL_LIGHTS = [("L_OPCas_Hall_1", (0.0, 9.0)), ("L_OPCas_Hall_2", (-12.0, -6.0)), ("L_OPCas_Hall_3", (12.0, -6.0))]
ARMORS = [(-19.5, -15.5, 0.35), (19.5, -15.5, -0.35)]           # (x, y, giro) - armaduras ao lado do estrado
RACKS = [(-24.4, 4.0, math.pi / 2), (24.4, 4.0, -math.pi / 2)]   # suportes de espadas encostados nas laterais
ANDONS = [(-17.5, -12.0), (17.5, -12.0), (-17.5, 13.5), (17.5, 13.5)]


def yoroi(mb, F, x, y, z, ang):
    """ARMADURA DE EXPOSICAO (vermelho-laca e ouro) sentada sobre o bau (karabitsu): saia de placas em 3 fiadas,
    couraca, ombreiras, gola, elmo com protetor de nuca, abas e kuwagata dourado em V, mascara"""
    Fa = sub(F, x, y, 0.0, ang)
    bb(mb, Fa, -1.2, 1.2, -0.85, 0.85, z, z + 1.25, WD)                                  # bau
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(mb, Fa, sx * 1.2 - 0.18, sx * 1.2 + 0.18, sy * 0.85 - 0.18, sy * 0.85 + 0.18, z + 0.05, z + 1.3, GOLD)
    bb(mb, Fa, -1.3, 1.3, -0.95, 0.95, z + 1.25, z + 1.45, WD)
    zb = z + 1.45
    for i, (r0, r1, h) in enumerate(((1.05, 1.18, 0.55), (0.95, 1.08, 0.55), (0.85, 0.98, 0.5))):  # kusazuri
        z0 = zb + 0.5 * i
        lathe(mb, Fa, (0, 0, z0), [(r1, 0.0), (r0, h)], 8, LAC, math.pi / 8)
        lathe(mb, Fa, (0, 0, z0 + h - 0.12), [(r0 + 0.04, 0.0), (r0 + 0.02, 0.1)], 8, GOLD, math.pi / 8)
    zd = zb + 1.45
    lathe(mb, Fa, (0, 0, zd), [(0.72, 0.0), (0.86, 0.5), (0.9, 1.0), (0.78, 1.45), (0.55, 1.6)], 8, LAC, math.pi / 8)
    for zz in (0.35, 0.75, 1.15):                                                    # cordoes das placas
        lathe(mb, Fa, (0, 0, zd + zz), [(0.9, 0.0), (0.9, 0.08)], 8, GOLD, math.pi / 8)
    for sx in (-1, 1):                                                               # ombreiras (sode)
        bx(mb, Fa, sx * 1.1, 0.0, zd + 1.0, 0.22, 1.2, 1.3, LAC, 0.0, ry=sx * 0.3)
        bx(mb, Fa, sx * 1.16, 0.0, zd + 1.55, 0.26, 1.24, 0.14, GOLD, 0.0, ry=sx * 0.3)
    lathe(mb, Fa, (0, 0, zd + 1.55), [(0.38, 0.0), (0.4, 0.3)], 8, IRON)                # gola
    zk = zd + 1.85
    lathe(mb, Fa, (0, 0, zk), [(0.95, 0.0), (0.8, 0.25), (0.62, 0.45)], 8, LAC, math.pi / 8)   # shikoro
    lathe(mb, Fa, (0, 0, zk + 0.4), [(0.6, 0.0), (0.58, 0.3), (0.42, 0.62), (0.12, 0.8)], 8, IRON)   # hachi
    for sx in (-1, 1):
        bx(mb, Fa, sx * 0.72, 0.35, zk + 0.45, 0.12, 0.55, 0.45, LAC, 0.0, rz=sx * 0.5)  # fukigaeshi
        ext(mb, Fa, [(sx * 0.12, zk + 0.75), (sx * 0.95, zk + 1.85), (sx * 0.72, zk + 1.95), (sx * 0.05, zk + 0.95)],
            "y", 0.55, 0.65, GOLD)                                                    # kuwagata
    bb(mb, Fa, -0.3, 0.3, 0.5, 0.72, zk - 0.15, zk + 0.3, RR)                           # mascara
    bb(mb, Fa, -0.12, 0.12, 0.5, 0.78, zk + 0.6, zk + 0.82, GOLD)                       # maedate
    return Fa


def sword_rack(mb, F, x, y, z, ang, n=3, w=3.4):
    """suporte de espadas (katana-kake): base laqueada, 2 montantes recortados, n espadas deitadas (saya preta,
    tsuba dourada, cabo trancado)"""
    Fr = sub(F, x, y, 0.0, ang)
    bb(mb, Fr, -w / 2, w / 2, -0.4, 0.4, z, z + 0.25, LAC)
    for s in (-1, 1):
        ext(mb, Fr, [(-0.3, z + 0.25), (0.3, z + 0.25), (0.22, z + 0.6 + 0.55 * n), (-0.22, z + 0.6 + 0.55 * n)],
            "x", s * (w / 2 - 0.5) - 0.12, s * (w / 2 - 0.5) + 0.12, LAC)
    for i in range(n):
        zz = z + 0.65 + 0.55 * i
        ln = w + 0.6 - 0.25 * i
        mb.rod(Fr.p(-ln / 2, 0.08, zz), Fr.p(ln / 2 - 1.1, 0.08, zz), 0.1, CBLACK, 6)            # saya
        lathe_y(mb, sub(Fr, ang=math.pi / 2), (0.08, -(ln / 2 - 1.1), zz), [(0.2, 0.0), (0.2, 0.06)], 8, GOLD)  # tsuba
        mb.rod(Fr.p(ln / 2 - 1.04, 0.08, zz), Fr.p(ln / 2, 0.08, zz), 0.09, CWHITE, 6)          # tsuka


def tatami_field(mb, F, x0, x1, y0, y1, z):
    """campo de tatami (2,5 x 5,0) em fiadas desencontradas, debrum (heri) indigo nas bordas longas"""
    n = int(round((x1 - x0) / 2.5))
    w = (x1 - x0) / n
    for i in range(n):
        xa = x0 + i * w
        off = 2.5 if i % 2 else 5.0
        ys = [y0] + [y0 + off + 5.0 * k for k in range(12) if y0 + off + 5.0 * k < y1 - 1.0] + [y1]
        for ya, yb_ in zip(ys, ys[1:]):
            if yb_ - ya < 0.8:
                continue
            bb(mb, F, xa + 0.04, xa + w - 0.04, ya + 0.04, yb_ - 0.04, z, z + 0.14, TATAMI)
        bb(mb, F, xa + 0.04, xa + 0.18, y0 + 0.04, y1 - 0.04, z + 0.02, z + 0.17, WD)          # heri (1 por fiada)


def hall(mb):
    F = keep_frame()
    hx0, hy0 = T[0][0], T[0][1]
    X, Y = hx0 - 2.0, hy0 - 2.0
    zc = 12.45                                              # teto
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
    # 2 campos de tatami dos lados do corredor central de tabuas (porta -> estrado)
    for s in (-1, 1):
        a, b = sorted((s * 3.8, s * 13.8))
        tatami_field(mb, F, a, b, -12.6, 12.4, FLOOR)
        bb(mb, F, a - 0.2, b + 0.2, -12.8, -12.6, FLOOR, FLOOR + 0.2, WD)
        bb(mb, F, a - 0.2, b + 0.2, 12.4, 12.6, FLOOR, FLOOR + 0.2, WD)
    # estrado (jodan) ao fundo: tablado 0,75, viga de borda, biombos dourados, rolo com o brasao
    yd0, yd1 = -Y, -Y + 7.0
    zd = FLOOR + 0.75
    bb(mb, F, -13.0, 13.0, yd0, yd1, FLOOR - 0.1, zd - 0.12, WM)
    bb(mb, F, -13.4, 13.4, yd1 - 0.45, yd1 + 0.15, FLOOR - 0.1, zd + 0.02, WD)
    for x in K.even(-12.6, 12.6, 2.6):
        bb(mb, F, x - 1.24, x + 1.24, yd0 + 0.05, yd1 - 0.6, zd - 0.12, zd + 0.02, TATAMI)
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
            if k in (1, 4):                                 # pinheiro pintado (mancha verde) nos biombos
                for sg in (-1, 1):
                    bb(mb, Fb, -ln / 2 + 0.25, ln / 2 - 0.25, sg * 0.07, sg * 0.1, zd + 2.2, zd + 3.4, "Leaf_OP_Pine")
    # o senhor do castelo nao esta - o lugar dele: almofada principal + 2 laterais, apoio de braco, mesinha, espadas
    ym = yd0 + 3.6
    for x, s_ in ((0.0, 1.0), (-4.6, 0.82), (4.6, 0.82)):
        bb(mb, F, x - 1.0 * s_, x + 1.0 * s_, ym - 1.0 * s_, ym + 1.0 * s_, zd + 0.02, zd + 0.32, CRED if x == 0 else INDIGO,
           0.08)
    bb(mb, F, -1.9, -1.4, ym - 0.6, ym + 0.6, zd + 0.02, zd + 0.9, LAC)                 # kyosoku
    bb(mb, F, -2.0, -1.3, ym - 0.7, ym + 0.7, zd + 0.9, zd + 1.05, LAC)
    bb(mb, F, -1.2, 1.2, ym + 1.6, ym + 2.4, zd + 0.02, zd + 0.75, LAC)                 # mesinha
    bb(mb, F, -0.6, 0.6, ym + 1.75, ym + 2.25, zd + 0.75, zd + 0.85, GOLD)
    sword_rack(mb, F, 2.6, yd0 + 1.1, zd + 0.02, 0.0, 2, 2.8)
    # tokonoma: moldura escura saliente na parede do fundo, rolo branco com o brasao (sem texto)
    Fb = faces(F, X, Y)[1][1]
    Fi = sub(Fb, 0.0, 0.0, 0.0, math.pi)
    for s in (-1, 1):
        bb(mb, Fi, s * 2.6 - 0.35, s * 2.6 + 0.35, 0.0, 0.8, zd, 10.5, WD)
    bb(mb, Fi, -2.95, 2.95, 0.0, 0.8, 9.9, 10.6, WD)
    bb(mb, Fi, -2.25, 2.25, 0.0, 0.25, zd, 9.9, "Plaster_OP_Warm")
    bb(mb, Fi, -1.1, 1.1, 0.2, 0.42, 3.1, 8.9, CWHITE)
    bb(mb, Fi, -1.25, 1.25, 0.2, 0.6, 8.9, 9.2, WD)
    bb(mb, Fi, -1.25, 1.25, 0.2, 0.6, 2.85, 3.1, WD)
    crest(mb, sub(Fi, 0.0, 0.43, 0.0), 0.0, 6.6, 0.8, INDIGO, 0.14)
    # armaduras, suportes de espadas, andon de piso
    for x, y, a in ARMORS:
        yoroi(mb, F, x, y, FLOOR, a)
    for x, y, a in RACKS:
        sword_rack(mb, F, x, y, FLOOR, a, 3, 3.6)
    for x, y in ANDONS:
        K2.andon_floor(mb, F, x, y, FLOOR, 1.15)
    # pilares (com pedra-base, consolo em cima) e vigas-mestras sob o teto
    for x, y in HALL_COLS:
        K.rock_base(mb, F, x, y, FLOOR - 0.1, 1.1, 0.35)
        bb(mb, F, x - 0.62, x + 0.62, y - 0.62, y + 0.62, FLOOR, zc - 0.9, WD, 0.06)
        bb(mb, F, x - 1.6, x + 1.6, y - 0.5, y + 0.5, zc - 1.45, zc - 0.9, WD)
        bb(mb, F, x - 0.7, x + 0.7, y - 0.7, y + 0.7, FLOOR + 6.0, FLOOR + 6.3, GOLD)      # cinta dourada
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
        Fi = sub(Fw, 0.0, 0.0, 0.0, math.pi)
        spans = [(-ln / 2, -DOOR_W / 2 - 0.3), (DOOR_W / 2 + 0.3, ln / 2)] if k == "F" else [(-ln / 2, ln / 2)]
        if k == "B":
            spans = [(-ln / 2, -2.95), (2.95, ln / 2)]
        for a, b in spans:
            bb(mb, Fi, a, b, -0.15, 0.25, FLOOR, FLOOR + 1.6, WM)
            bb(mb, Fi, a, b, -0.15, 0.35, FLOOR + 1.6, FLOOR + 1.85, WD)
        bb(mb, Fi, -ln / 2, ln / 2, 0.0, 0.32, 9.6, 10.15, WD)
        bb(mb, Fi, -ln / 2, ln / 2, 0.0, 0.3, zc - 0.7, zc, WD)
        ws = sorted(-s for s in HALL_WINS[k])
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
        K.chochin(mb, F, (x, y, z - 1.6 - 2.3), 0.95, 2.3, CWHITE)
        light(nm, "POINT", F.p(x, y, 7.4), 260.0, WARM, 0.5)


def hall_cols():
    F = keep_frame()
    for x, y in HALL_COLS:
        col_box("OP_CasHall", (1.4, 1.4, 12.0), F.p(x, y, 6.0), F.r())
    Y = T[0][1] - 2.0
    col_box("OP_CasHall", (26.8, 7.6, 0.85), F.p(0.0, -Y + 3.5, FLOOR + 0.425 - 0.1), F.r())
    for s in (-1, 1):
        col_box("OP_CasHall", (9.4, 1.4, 4.7), F.p(s * 7.8, -Y + 1.6, FLOOR + 0.75 + 2.35), F.r())
    for x, y, a in ARMORS:
        Fa = sub(F, x, y, 0.0, a)
        col_box("OP_CasHall", (2.8, 2.2, 6.2), Fa.p(0.0, 0.0, FLOOR + 3.1), Fa.r())
    for x, y, a in RACKS:
        for dy in (0.0,):
            Fr = sub(F, x, y + dy, 0.0, a)
            col_box("OP_CasHall", (4.4, 1.0, 2.5), Fr.p(0.0, 0.0, FLOOR + 1.25), Fr.r())
    for x, y in ANDONS:
        col_box("OP_CasHall", (1.3, 1.3, 2.0), F.p(x, y, FLOOR + 1.0), F.r())


# ================================================================== BRASAO (anel + 8 petalas + miolo)
def crest(mb, Ff, x, z, R, m=INDIGO, th=0.1):
    """brasao circular da ilha no plano x-z do referencial (sai th para +y): anel, 8 petalas, miolo (V3: mais leve)"""
    n = 14
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
        for j in range(6):
            t = 2 * math.pi * j / 6
            u, v = R * 0.2 * math.cos(t), R * 0.12 * math.sin(t)
            poly.append((cx + u * math.cos(a) - v * math.sin(a), cz + u * math.sin(a) + v * math.cos(a)))
        ext(mb, Ff, poly, "y", -th, th, m)
    lathe_y(mb, Ff, (x, 0.0, z), [(R * 0.16, -th), (R * 0.16, th)], 10, m)


# ================================================================== PATIO
def dobei(mb, pts, z, h=4.6, key="db", sama=True, col=True, tile_lod=None):
    """muro de reboco (dobei) sobre soco de pedra, CAPA DE TELHA ONDULADA de 2 aguas (kit V2) com cumeeira, seteiras
    quadradas VAZADAS; COLISAO ALTA (ate CC+8,8: o topo do muro nao vira degrau - FAIL da V2-0). pts = polilinha"""
    for i, (a, b) in enumerate(zip(pts, pts[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            continue
        Fs = Frame(a[0], a[1], z, math.atan2(dy, dx))
        bb(mb, Fs, -0.3, ln + 0.3, -0.95, 0.95, -0.6, 0.9, ST)
        bb(mb, Fs, -0.3, ln + 0.3, -1.05, 1.05, 0.9, 1.15, STP)
        holes = []
        if sama and ln > 4.0:
            for x in K.even(1.6, ln - 1.6, 3.6):
                holes.append((x - 0.34, x + 0.34, 2.7, 3.38))
        K.panel(mb, Fs, 0.0, ln, 1.15, h, -0.6, 0.6, holes, PL)
        bb(mb, Fs, -0.2, ln + 0.2, -0.75, 0.75, h - 0.5, h, WD)
        Fm = sub(Fs, ln / 2, 0.0, 0.0)
        Hc = lambda x, y: h + 1.05 - 0.6 * abs(y)
        mx_, my_ = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx_, ny_ = -dy / ln, dx / ln                        # +y local do muro
        inner = L.point_in_poly(mx_ + nx_ * 3.0, my_ + ny_ * 3.0, L.COURT)
        for si, Fk in enumerate((Fm, sub(Fm, ang=math.pi))):
            wl = tile_lod or (1 if (si == 0) == inner else 2)  # V3: agua de FORA do patio lisa (lod 2: nao se ve de perto)
            K2.tiles(mb, Fk, K2._wave(-ln / 2 - 0.4, ln / 2 + 0.4, 2.1, 0.22, wl), lambda x: -0.1, 1.6, Hc, ROOF, 0.28,
                     soffit=SOFFIT, rows=(0.0, 0.5, 1.0), coarse=6.0)
            K.strip(mb, Fk, [(x, 1.3, Hc(x, 1.3) - 0.28) for x in (-ln / 2 - 0.4, ln / 2 + 0.4)], (0, 1, 0), -0.14,
                    0.14, -0.4, 0.0, FAS)
        bb(mb, Fs, -0.4, ln + 0.4, -0.32, 0.32, h + 0.85, h + 1.35, RR)
        mb.rod(Fs.p(-0.4, 0.0, h + 1.45), Fs.p(ln + 0.4, 0.0, h + 1.45), 0.22, RR, 6)
        if col:
            col_box("OP_CasWall", (ln + 0.8, 3.8, COL_TALL + 0.6), Fs.p(ln / 2, 0.0, (COL_TALL - 0.6) / 2), Fs.r())


def simple_base(mb, F, hb, z_top, z_bot, batter, key):
    """base de cantaria dos torreoes (desce pela rocha): fiadas em ANEL com talude e chanfro, cantos travados, capa"""
    tb = math.tan(math.radians(batter))
    zc = z_top - 0.4
    zs = _courses(key, z_bot, zc, 1.7, 2.5)
    ring = lambda o, z: [(sx * (hb + o), sy * (hb + o), z) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for c in range(len(zs) - 1):
        za, zb_ = zs[c], zs[c + 1]
        oa, ob = (zc - za) * tb, (zc - zb_) * tb
        loft(mb, F, [ring(oa, za), ring(ob, zb_ - 0.1), ring(ob - 0.1, zb_)], WALL if K._h01(key, c, "m") > 0.3 else ST)
    sangi_corners(mb, F, hb, hb, zc, zs, batter, key)
    bb(mb, F, -hb - 0.35, hb + 0.35, -hb - 0.35, hb + 0.35, zc, z_top, STP)


def turret(mb, cx, cy, ang, s, z_bot, key, big=True):
    """yagura de canto no kit V2 (2 andares no SE, 1 no SO) sobre base de cantaria que desce pela rocha: rodape de
    tabuas escuras, janelas com caixilho, saia ondulada com beiral rebocado e chidori, irimoya no topo"""
    F = Frame(cx, cy, CC, ang)
    hb = s / 2 + 0.8
    simple_base(mb, F, hb, 1.0, z_bot, 18.0, key)
    zm = (z_bot + 1.0) / 2                                  # colisao da base em talude (2 caixas)
    tb = math.tan(math.radians(18.0))
    for za, zb_, o in ((z_bot, zm, (0.6 - z_bot) * tb), (zm, 1.0, (0.6 - zm) * tb)):
        col_box("OP_CasTurret", (2 * (hb + o), 2 * (hb + o), zb_ - za), F.p(0, 0, (za + zb_) / 2), F.r())
    w2 = {k: ([-2.5, 2.5] if k == "F" else [0.0]) for k in "FBRL"}
    for k, Ff, ln, d in faces(F, s / 2, s / 2):            # rodape de tabuas (koshi-ita) com mata-juntas
        bb(mb, Ff, -ln / 2 - 0.16, ln / 2 + 0.16, -0.2, 0.16, 1.0, 2.8, WD)
        for x in K.even(-ln / 2 + 0.6, ln / 2 - 0.6, 2.2):
            bb(mb, Ff, x - 0.08, x + 0.08, 0.1, 0.3, 1.0, 2.8, WD)
    if big:
        s2 = s - 4.0
        sk = cskirt(mb, F, s2 / 2, s2 / 2, s / 2 + 2.6, s / 2 + 2.6, 13.4, 3.4, chid={"F": [(0.0, 5.6, 0.62)]},
                    lod=1, P=2.2, amp=0.26, fas=0.6, lift=0.9, up=2.6, oni=False)
        story(mb, F, s / 2, s / 2, 0.5, {k: wall_top(sk, k, s / 2) for k in "FBRL"}, 1.0, w2, 5.6, 2.4, 2.0, lod=1)
        h2 = 13.4 + 5.0
        story(mb, F, s2 / 2, s2 / 2, 13.4 - 0.6, {k: h2 for k in "FBRL"}, 1.0, {k: [0.0] for k in "FBRL"}, 14.9, 2.0,
              1.8, lod=1, sill_band=False)
        with plastered():
            r = K2.roof2(mb, F, s2, s2 + 0.01, h2, "irimoya", ROOF, ov=2.8, g_over=1.2, s0=0.42, s1=1.0, lift=1.0,
                         tv=0.5, lod=1, back_lod=1, gable_m=PL, rafters=False, hafu_m=FAS, P=2.4, courses=1)
    else:
        h2 = 9.6
        story(mb, F, s / 2, s / 2, 0.5, {k: h2 for k in "FBRL"}, 1.0, {k: ([-2.1, 2.1] if k == "F" else [0.0]) for k in "FBRL"}, 5.4, 2.2, 2.4,
              lod=1)
        with plastered():
            r = K2.roof2(mb, F, s, s + 0.01, h2, "irimoya", ROOF, ov=3.0, g_over=1.2, s0=0.42, s1=1.0, lift=1.1,
                         tv=0.5, lod=1, back_lod=1, gable_m=PL, rafters=False, hafu_m=FAS, P=2.4, courses=1,
                         chidori=dict(x=0.0, w=4.6, y=0.4))
    top_z = r["top"] - 2.0
    col_box("OP_CasTurret", (s + 2.0, s + 2.0, top_z + 1.0), F.p(0, 0, (top_z + 1.0) / 2), F.r())
    return F


def gate_roof(mb, F, W, D, zw, red=False, lod=0, col_name=None):
    """telhado de 2 aguas dos portoes no kit V2 (telha ondulada, testeira, tabeiras, onigawara) + COLISAO do
    telhado (o topo dos portoes fica ao alcance das escadas: FAIL da V2-0 no portao da subida)"""
    r = K2.roof2(mb, F, W, D, zw, "kirizuma", ROOF, ov=1.8, g_over=1.2, s0=0.42, s1=0.95, lift=0.7, tv=0.45,
                 lod=lod, back_lod=lod, gable_style="board", gold=red, rafters=False, hafu_m=LAC if red else WD,
                 ridge_w=1.8, courses=1)
    if col_name:
        z0, z1 = r["eave_z"] - 0.1, r["zr"] + 0.6
        col_box(col_name, (2 * r["Xe"] + 1.4, 2 * r["Ye"] + 0.8, z1 - z0), F.p(0.0, 0.0, (z0 + z1) / 2), F.r())
    return r


def koraimon(mb, cx, cy, ang, span, h, red=False, z=CC, key="kg", plaque=False, hikae=True, nuki_drop=3.0,
             col_name="OP_CasGate", roof_lod=0):
    """portao com 2 pilares principais, 2 pilares de apoio atras com telhadinhos (koraimon), viga (kabuki), travessa
    (nuki), telhado de 2 aguas do kit V2; pilares sobre pedra com cinta de ferro"""
    F = Frame(cx, cy, z, ang)                               # +y = frente (de onde se chega)
    pm = LAC if red else WD
    cw = 2.3 if red else 1.5
    back = 3.2 if red else 3.0
    xs = span / 2 + cw / 2
    for s in (-1, 1):
        x = s * xs
        K.rock_base(mb, F, x, 0.0, 0.0, cw * 0.95, 0.6)
        bb(mb, F, x - cw / 2, x + cw / 2, -cw / 2, cw / 2, 0.4, h, pm, 0.06)
        bb(mb, F, x - cw / 2 - 0.14, x + cw / 2 + 0.14, -cw / 2 - 0.14, cw / 2 + 0.14, 0.4, 1.4, IRON)
        if red:
            bb(mb, F, x - cw / 2 - 0.14, x + cw / 2 + 0.14, -cw / 2 - 0.14, cw / 2 + 0.14, h - 2.6, h - 2.2, GOLD)
        if not hikae:
            continue
        xb_ = s * (xs + (0.6 if red else 0.4))
        K.rock_base(mb, F, xb_, -back, 0.0, cw * 0.7, 0.5)
        bb(mb, F, xb_ - cw * 0.32, xb_ + cw * 0.32, -back - cw * 0.32, -back + cw * 0.32, 0.3, h * 0.66, pm, 0.05)
        for zz in (h * 0.3, h * 0.6):
            beam(mb, F, (x, 0.0, zz), (xb_, -back, zz), 0.36, 0.42, pm)
        Fr = sub(F, (x + xb_) / 2, -back / 2, 0.0, math.pi / 2)
        gate_roof(mb, Fr, back + cw + 0.6, cw + 0.4, h * 0.66 + 0.15, red, 2, col_name)
    zk = h - 1.8
    bb(mb, F, -xs - cw * 1.2, xs + cw * 1.2, -0.75, 0.75, zk, zk + 1.6, pm)
    bb(mb, F, -xs, xs, -0.4, 0.4, zk - nuki_drop, zk - nuki_drop + 0.7, pm)
    for x in (-span * 0.22, span * 0.22):
        bb(mb, F, x - 0.35, x + 0.35, -0.3, 0.3, zk - nuki_drop + 0.7, zk, pm)
    if red:
        for s in (-1, 1):
            e = s * (xs + cw * 1.2)
            bb(mb, F, min(e - s * 0.5, e + s * 0.14), max(e - s * 0.5, e + s * 0.14), -0.89, 0.89, zk - 0.14,
               zk + 1.74, GOLD)
    if plaque:
        crest(mb, sub(F, 0.0, 0.75, 0.0), 0.0, zk + 0.8, 1.0, GOLD, 0.12)
    gate_roof(mb, F, 2 * (xs + cw * 1.2) - 1.4, 3.4 if red else 2.4, h, red, roof_lod, col_name)
    return F, xs, cw, back


COURT_TOP = 0.14          # piso VISUAL do patio sobre a colisao (+0,14)
BAND = 8.0                # faixa de lajes em volta da torre
CURB = 0.25               # meia largura da borda de pedra entre lajes e cascalho


def _pave_rect(mb, court, r, slab, along, key, mats, z0, z1):
    """lajes (slab x slab, juntas desencontradas meia peca a cada fiada) no retangulo r recortado no patio"""
    x0, y0, x1, y1 = r
    u0, u1, v0, v1 = (x0, x1, y0, y1) if along == "x" else (y0, y1, x0, x1)
    n, row, v = 0, 0, v0
    while v < v1 - 0.3:
        vb = min(v1, v + slab)
        if v1 - vb < 1.0:
            vb = v1
        u = u0 - (slab * 0.5 if row % 2 else 0.0)
        while u < u1 - 0.3:
            ub = min(u1, u + slab)
            if u1 - ub < 1.0:
                ub = u1
            ua = max(u, u0)
            rect = (ua, v, ub, vb) if along == "x" else (v, ua, vb, ub)
            piece = L.clip_rect(court, rect)
            if len(piece) >= 3:
                tot = sum(w for _, w in mats)
                h = K._h01(key, row, round(ua, 1)) * tot
                m = mats[-1][0]
                for mm, w in mats:
                    h -= w
                    if h <= 0:
                        m = mm
                        break
                pc = DL.offset_poly(ccw(piece), -0.06)          # junta de 0,12 sobre a base escura (2 tris/laje)
                if len(pc) >= 3 and abs(L.area(pc)) > 0.5:
                    K.slab_poly(mb, ccw(pc), z1 - 0.3, z1, 0.0, m, sides=False)
                n += 1
            u = ub
        v, row = vb, row + 1
    return n


def _curb_line(mb, a, b, z0, z1, key, m=ST, hw=CURB):
    """borda de pedra ao longo de a-b (mundo): pecas de 3,0-4,0 com junta de 0,05"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(dx, dy)
    if ln < 0.5:
        return
    Fs = Frame(a[0], a[1], 0.0, math.atan2(dy, dx))
    x, k = 0.0, 0
    while x < ln - 0.2:
        x2 = min(ln, x + 6.0 + 2.0 * K._h01(key, k))
        if ln - x2 < 1.0:
            x2 = ln
        bb(mb, Fs, x + 0.025, x2 - 0.025, -hw, hw, z0, z1, m)
        x, k = x2, k + 1


def court_floor(mb):
    """piso do patio: LAJES 4 x 4 numa faixa de 8 em volta da torre, no EIXO porta -> mirante e no caminho do portao;
    o resto em CASCALHO recuado 0,3 da borda; borda de pedra escura entre lajes e cascalho; soleira do guarda-corpo.
    Tudo a +0,14 da colisao."""
    z1 = CC + COURT_TOP
    z0 = CC - 0.3
    tb = math.tan(math.radians(20.0))
    hx, hy = T[0][0] + 0.8 + 4.7 * tb, T[0][1] + 0.8 + 4.7 * tb
    kx0, kx1, ky0, ky1 = KX - hx, KX + hx, KY - hy, KY + hy
    bx0, bx1, by0, by1 = kx0 - BAND, kx1 + BAND, ky0 - BAND, ky1 + BAND
    court = ccw(L.COURT)
    c2 = 2 * CURB
    ya = 353.45
    xc = bx0 + 6.0
    strips = [(bx0, by0, bx1, ky0), (bx0, ky1, bx1, by1), (bx0, ky0, kx0, ky1), (kx1, ky0, bx1, ky1)]
    axis = [(-4.0, ya, 4.0, by0)]
    appr = [(bx0, by1, xc, 441.8), (-73.0, 441.8, xc, 447.8)]
    mats = [(STP, 6), ("Stone_OP_Plaza", 2)]
    n = 0
    for i, r in enumerate(strips + axis + appr):
        under = L.clip_rect(court, r)                       # base escura sob as lajes (le como junta)
        if len(under) >= 3:
            K.slab_poly(mb, ccw(under), z0, z1 - 0.08, 0.0, STD, sides=False)
        n += _pave_rect(mb, court, r, 4.0 if i != 6 else 3.0, "y" if i in (2, 3, 4, 5) else "x", ("pt", i), mats, z0, z1)
    zc0, zc1 = z0, z1 + 0.06
    _curb_line(mb, (bx0 - c2, by0 - CURB), (-4.0 - c2, by0 - CURB), zc0, zc1, "cb1")
    _curb_line(mb, (4.0 + c2, by0 - CURB), (bx1 + c2, by0 - CURB), zc0, zc1, "cb2")
    _curb_line(mb, (bx1 + CURB, by0), (bx1 + CURB, by1 + c2), zc0, zc1, "cb3")
    _curb_line(mb, (bx1, by1 + CURB), (xc, by1 + CURB), zc0, zc1, "cb4")
    _curb_line(mb, (bx0 - CURB, by1 + c2), (bx0 - CURB, by0), zc0, zc1, "cb5")
    _curb_line(mb, (-4.0 - CURB, by0), (-4.0 - CURB, ya - 0.05), zc0, zc1, "cb6")
    _curb_line(mb, (4.0 + CURB, ya - 0.05), (4.0 + CURB, by0), zc0, zc1, "cb7")
    cuts = [(bx0 - c2, by0 - c2, bx1 + c2, by1 + c2), (-4.0 - c2, 352.0, 4.0 + c2, by0), (bx0, by1, xc, 441.8),
            (-73.0, 441.8, xc, 447.8), (-79.5, 380.0, -62.2, 439.3)]
    pieces = [ccw(DL.offset_poly(court, -0.3))]
    for r in cuts:
        pieces = [q for pc in pieces for q in L.subtract_rect(pc, r)]
    for pc in pieces:
        K.slab_poly(mb, ccw(pc), z0, z1, 0.0, "Stone_OP_Court")
    rail = [RAIL_W, (-49.4, 358.8), (-24.0, 352.8), (24.0, 352.8), (49.4, 358.8), RAIL_E]
    for i, (a, b) in enumerate(zip(rail, rail[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        Fs = Frame(a[0], a[1], 0.0, math.atan2(dy, dx))
        x, k = -0.4 if i == 0 else 0.0, 0
        x_end = ln + (0.4 if i == len(rail) - 2 else 0.0)
        while x < x_end - 0.2:
            x2 = min(x_end, x + 3.0 + 1.0 * K._h01("sr", i, k))
            if x_end - x2 < 1.0:
                x2 = x_end
            bb(mb, Fs, x + 0.025, x2 - 0.025, -1.0, 0.6, z0, CC + 0.33, ST)
            x, k = x2, k + 1
    return n


WALLS = []                 # polilinhas dos muros dobei (para a borda de pedra ao pe)


def wall_curbs(mb):
    """BORDA de pedra (0,8) ao pe dos muros, do lado do patio"""
    for wi, pts in enumerate(WALLS):
        for i, (a, b) in enumerate(zip(pts, pts[1:])):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 2.0:
                continue
            nx, ny = -dy / ln, dx / ln
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            sd = 1.0 if L.point_in_poly(mx + nx * 2.0, my + ny * 2.0, L.COURT) else -1.0
            off = sd * (0.95 + 0.42)
            a2 = (a[0] + nx * off + dx / ln * 1.4, a[1] + ny * off + dy / ln * 1.4)
            b2 = (b[0] + nx * off - dx / ln * 1.4, b[1] + ny * off - dy / ln * 1.4)
            _curb_line(mb, a2, b2, CC - 0.3, CC + COURT_TOP + 0.2, ("wc", wi, i), ST, 0.4)


# cerca sagrada (tamagaki) em volta da base da arvore: as raizes medidas no patio ficam DENTRO (x 18..72, y 411..470)
FENCE = [(16.0, 475.6), (16.0, 452.0), (25.0, 444.5), (37.0, 432.0), (39.0, 416.0), (50.0, 408.0), (68.6, 405.0)]
SHIMENAWA_SEG = 3                       # segmento da cerca que leva a corda sagrada (de frente para a torre)


def tamagaki(mb):
    """CERCA SAGRADA da arvore: soco de pedra, mouroes de madeira escura com cabeca chanfrada, 2 travessas e ripas
    verticais (mizugaki), corda SHIMENAWA de palha com shide brancos no trecho de frente para a torre; colisao ALTA
    (CC+8,8): o jogador nao entra nas raizes (corpo dentro medido pelo gate)"""
    h = 3.4
    for i, (a, b) in enumerate(zip(FENCE, FENCE[1:])):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        Fs = Frame(a[0], a[1], CC, math.atan2(dy, dx))
        bb(mb, Fs, -0.5, ln + 0.5, -0.65, 0.65, -0.3, 0.55, ST)
        bb(mb, Fs, -0.6, ln + 0.6, -0.75, 0.75, 0.55, 0.75, STP)
        nseg = max(1, int(math.ceil(ln / 2.6)))
        xs = [ln * k / nseg for k in range(nseg + 1)]
        for x in xs:
            bb(mb, Fs, x - 0.24, x + 0.24, -0.24, 0.24, 0.75, h + 0.3, WD)
        for zz in (1.5, h - 0.5):
            bb(mb, Fs, -0.1, ln + 0.1, 0.24, 0.42, zz - 0.14, zz + 0.14, WD)
        for x in K.even(0.3, ln - 0.3, 1.9):
            bb(mb, Fs, x - 0.14, x + 0.14, 0.42, 0.56, 0.9, h - 0.2, WM)
        col_box("OP_CasFence", (ln + 2.4, 3.2, COL_TALL + 0.6), Fs.p(ln / 2, 0.3, (COL_TALL - 0.6) / 2), Fs.r())
        if i == SHIMENAWA_SEG:
            pts = []
            for k in range(13):
                u = k / 12.0
                pts.append((ln * u, -0.5, h - 0.4 - 0.9 * math.sin(math.pi * u)))     # lado da torre (-y)
            for p0, p1 in zip(pts, pts[1:]):
                beam(mb, Fs, p0, p1, 0.5, 0.5, STRAW)
            for k in range(1, 12, 2):
                x, y, z = pts[k]
                ext(mb, Fs, [(x - 0.25, z - 0.2), (x + 0.25, z - 0.2), (x + 0.25, z - 0.8), (x - 0.05, z - 0.8),
                             (x - 0.05, z - 1.4), (x + 0.25, z - 1.4), (x + 0.25, z - 2.0), (x - 0.25, z - 2.0)],
                    "y", y - 0.36, y - 0.3, CWHITE)


def court(mb):
    gx, gw = L.COURT_GATE[0], L.COURT_GATE[2]
    xs = gw / 2 + 0.75
    wl = [(-63.4, COURT_GATE_Y), (-63.4, 381.5)]
    dobei(mb, wl, CC, 4.6, "dbW")
    WALLS.clear()
    WALLS.extend([wl])
    wn = [(gx - xs, COURT_GATE_Y), (gx - xs, 437.3), (-89.3, 437.3), (-89.3, 469.2), (-40.0, 473.3), (20.0, 475.3), WALL_N_END]
    dobei(mb, wn, CC, 4.6, "dbN", sama=False, tile_lod=2)       # V3: muro do fundo (atras da torre) liso
    WALLS.append(wn)
    we = [(63.6, 370.6), (65.6, 373.6), (WALL_E_END[0], WALL_E_END[1])]
    dobei(mb, we, CC, 4.6, "dbE", sama=False, tile_lod=2)
    WALLS.append(we)
    for p in (wn[2], wn[3], wn[4], wn[5], we[1], wl[1]):           # pilares de canto (cobrem as juntas)
        bb(mb, Frame(p[0], p[1], CC, 0.0), -1.15, 1.15, -1.15, 1.15, -0.3, 5.0, PL)
        col_box("OP_CasWall", (3.4, 3.4, COL_TALL + 0.6), (p[0], p[1], CC + (COL_TALL - 0.6) / 2))
        bb(mb, Frame(p[0], p[1], CC, 0.0), -1.35, 1.35, -1.35, 1.35, -0.3, 1.3, ST)
    for p in (wn[-1], we[-1]):
        bb(mb, Frame(p[0], p[1], CC, 0.0), -1.25, 1.25, -1.25, 1.25, -0.3, 3.4, ST)
    # portao do patio (koraimon escuro) no topo da CasteloB, voltado para a escada (sul)
    F, xs_, cw, back = koraimon(mb, gx, COURT_GATE_Y, math.pi, gw, 11.0, False, CC, "kgP", nuki_drop=1.2, roof_lod=1,
                                col_name="OP_CasCourtGate")
    for s in (-1, 1):
        col_box("OP_CasCourtGate", (cw + 0.4, cw + 0.4, 11.0), F.p(s * xs_, 0.0, 5.5), F.r())
        col_box("OP_CasCourtGate", (1.4, 1.4, 7.3), F.p(s * (xs_ + 0.4), -back, 3.6), F.r())
    ang_e = math.atan2(372.0 - 358.0, 66.0 - 50.0)
    turret(mb, SE_TURRET[0], SE_TURRET[1], ang_e - math.pi, SE_TURRET[2], -9.4, "ySE", True)
    ang_w = math.atan2(358.0 - 376.0, -50.0 - (-64.0))
    turret(mb, SW_TURRET[0], SW_TURRET[1], ang_w + math.pi, SW_TURRET[2], -13.0, "ySW", False)
    rail = [RAIL_W, (-49.4, 358.8), (-24.0, 352.8), (24.0, 352.8), (49.4, 358.8), RAIL_E]
    K2.rail2(mb, Frame(0.0, 0.0, CC + 0.33, 0.0), rail, 3.4, 0.0, 3.4, LAC, True)
    for a, b in zip(rail, rail[1:]):                        # colisao ALTA do guarda-corpo (o corrimao nao e degrau)
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        col_box("OP_CasRail", (ln + 0.8, 1.0, COL_TALL + 0.6), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2,
                CC + (COL_TALL - 0.6) / 2), (0.0, 0.0, math.atan2(dy, dx)))
    for i, x in enumerate((-12.0, 12.0)):
        K2.toro2(mb, Frame(x, 375.0, CC + COURT_TOP, 0.0), "L_OPProp_Lamp_Cas_Toro_%d" % i, 1.0, 35.0)
        col_box("OP_CasLamp", (3.0, 3.0, 8.0), (x, 375.0, CC + 4.0))
    tamagaki(mb)
    court_floor(mb)


WALL_N_END = (60.0, 468.0)   # muro do fundo: termina ENCOSTADO na raiz NNE da arvore
WALL_E_END = (73.2, 439.4)   # muro leste: termina ENCOSTADO na raiz leste
RAIL_W = (-53.0, 362.8)
RAIL_E = (52.5, 361.0)


# ================================================================== ADRO, SUBIDA, ESTANDARTES
def banners(mb):
    """os 2 ESTANDARTES da falesia (U16: os unicos do castelo): pano branco com o brasao, vara com ponteiras douradas
    presa por 2 bracos de ferro chumbados na rocha, barra de peso; COLISAO na vara e no peso (ficam a < 6 do patio)"""
    import op_terrain as TR
    for idx, xc, yf in ((1, -16.15, 351.75), (6, 16.45, 352.0)):
        dr = 1.4 + 4.2 * TR.hh("cf", idx, "dr") ** 1.5
        ztop = CC - dr - 0.9
        zbot = 118.6
        Fb = Frame(xc, yf, 0.0, math.pi)
        yc = 0.3
        wdt = 5.6
        bb(mb, Fb, -wdt / 2, wdt / 2, yc, yc + 0.12, zbot + 0.3, ztop - 0.35, CWHITE)
        mb.rod(Fb.p(-wdt / 2 - 0.6, yc + 0.06, ztop), Fb.p(wdt / 2 + 0.6, yc + 0.06, ztop), 0.2, WD, 8)
        for s in (-1, 1):
            x = s * (wdt / 2 + 0.75)
            mb.rod(Fb.p(x - s * 0.05, yc + 0.06, ztop), Fb.p(x + s * 0.4, yc + 0.06, ztop), 0.28, GOLD, 8)
            xa = s * (wdt / 2 - 0.4)
            bb(mb, Fb, xa - 0.3, xa + 0.3, -0.45, 0.08, ztop - 1.6, ztop + 0.5, IRON)
            beam(mb, Fb, (xa, 0.0, ztop - 1.4), (xa, yc + 0.06, ztop - 0.15), 0.14, 0.16, IRON)
            beam(mb, Fb, (xa, 0.0, ztop + 0.3), (xa, yc + 0.06, ztop + 0.05), 0.14, 0.16, IRON)
            for zz in (ztop - 1.3, ztop + 0.25):
                mb.rod(Fb.p(xa, 0.02, zz), Fb.p(xa, 0.14, zz), 0.1, IRON, 6)
        for k in range(5):
            xx = -wdt / 2 + 0.4 + (wdt - 0.8) * k / 4
            bb(mb, Fb, xx - 0.22, xx + 0.22, yc - 0.12, yc + 0.24, ztop - 0.5, ztop + 0.3, CWHITE)
        bb(mb, Fb, -wdt / 2 - 0.15, wdt / 2 + 0.15, yc - 0.18, yc + 0.3, zbot + 0.05, zbot + 0.4, WD)
        crest(mb, sub(Fb, 0.0, yc + 0.06, 0.0), 0.0, ztop - (ztop - zbot) * 0.34, 1.75, INDIGO, 0.14)
        bb(mb, Fb, -wdt / 2 + 0.3, wdt / 2 - 0.3, yc - 0.12, yc + 0.24, zbot + 1.2, zbot + 1.75, INDIGO)
        col_box("OP_CasBanner", (wdt + 2.4, 1.2, 1.6), Fb.p(0.0, yc - 0.2, ztop - 0.2), Fb.r())
        col_box("OP_CasBanner", (wdt + 0.6, 1.2, 0.9), Fb.p(0.0, yc - 0.1, zbot + 0.2), Fb.r())


def adro(mb):
    gx, gy, gw = L.CASTLE_GATE
    F, xs, cw, back = koraimon(mb, gx, gy, math.pi, gw, 16.5, True, CF, "kgA", plaque=True)
    for s in (-1, 1):
        col_box("OP_CasGate", (cw + 0.6, cw + 0.6, 16.5), F.p(s * xs, 0.0, 8.25), F.r())
        col_box("OP_CasGate", (1.8, 1.8, 11.0), F.p(s * (xs + 0.6), -back, 5.5), F.r())
    for i, x in enumerate((-25.5, 25.5)):                   # postes de lanterna (kit V2), braco para o eixo
        K2.lamp_post(mb, Frame(x, 320.0, CF, 0.0 if x < 0 else math.pi), "L_OPProp_Lamp_Cas_Adro_%d" % i, 40.0, 8.6, 1.7)
        col_box("OP_CasLamp", (1.6, 1.6, 9.0), (x, 320.0, CF + 4.5))
    # mureta de cantaria na bacia (frente e lados; aberta no canal leste e na face da rocha) COM colisao
    off = ccw(DL.offset_poly(L.BASIN, 0.65))
    n = len(off)
    for i in range(n):
        a, b = off[i], off[(i + 1) % n]
        if min(a[1], b[1]) > 349.0:
            continue
        pts = [a, b]
        if max(a[0], b[0]) > 15.0 and min(a[1], b[1]) < 345.6 and max(a[1], b[1]) > 338.6:
            t0 = (338.6 - a[1]) / (b[1] - a[1])
            t1 = (345.6 - a[1]) / (b[1] - a[1])
            lerp = lambda t: (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
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
        bb(mb, Fp, -ln / 2 - 0.55, ln / 2 + 0.55, -0.6, 0.6, -0.3, 1.15, WALL)
        bb(mb, Fp, -ln / 2 - 0.65, ln / 2 + 0.65, -0.75, 0.75, 1.15, 1.5, STP)
        bb(mb, Fp, -ln / 2 - 0.5, ln / 2 + 0.5, -0.75, 0.75, -0.45, 0.25, STD)
        col_box("OP_CasBasinWall", (ln + 1.3, 1.5, 1.8), Fp.p(0.0, 0.0, 0.6), Fp.r())
    # portao de madeira (kabukimon) no pe da subida - telhado com colisao
    F2, xs2, cw2, back2 = koraimon(mb, -71.0, 334.6, math.pi, 12.0, SUB_GATE_H, False, CF, "kgS", hikae=False, roof_lod=1,
                                   nuki_drop=1.2)
    for s in (-1, 1):
        col_box("OP_CasGate", (cw2 + 0.4, cw2 + 0.4, SUB_GATE_H), F2.p(s * xs2, 0.0, SUB_GATE_H / 2), F2.r())


SUB_GATE_H = 12.0
GUARD_T = 1.3
GUARD_H = 1.1
GUARD_BATTER = 10.0


def stair_guard(mb, nm, ground):
    """GUARDA DE PEDRA das subidas A/B: fiada de cima inclinada em pedras, capa em pecas com pingadeira, muro de
    ishigaki em fiadas por fora onde o chao de fora e mais baixo, miolo escuro, pilaretes de arranque/chegada"""
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    F = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
    rise = L.stair_rise(nm)
    tb = math.tan(math.radians(GUARD_BATTER))
    line = lambda y: rise * (y / tread + 1.0)
    top = lambda y: line(y) + GUARD_H
    zu = lambda y: top(y) - 0.3
    zl = lambda y: line(y) - 0.9
    Y1 = tread * n
    W = w / 2
    key = ("sg", nm)
    for s in (-1, 1):
        xo = lambda y, z: s * (W + GUARD_T + (zu(y) - z) * tb)
        X = lambda v: s * v
        ys = [min(Y1, 1.5 * i) for i in range(int(Y1 / 1.5) + 2)]
        gz = []
        for y in ys:
            hz = -99.0
            for dd in (0.7, 2.0, 3.6):
                p = F.p(s * (W + GUARD_T + dd), y, 0.0)
                z = ground.z(p.x, p.y, top=foot[2] + 60.0, floor=foot[2] - 60.0) - foot[2]
                hz = max(hz, z)
            gz.append(max(-0.3, hz - 0.4))
        gat = lambda y: gz[min(len(gz) - 1, max(0, int(round(y / 1.5))))]

        def sec(y, z0, z1, xin):
            pts = [(xin, y, z0), (xo(y, z0), y, z0), (xo(y, z1 - 0.1), y, z1 - 0.1), (xo(y, z1) - s * 0.1, y, z1),
                   (xin + s * 0.1, y, z1), (xin, y, z1 - 0.1)]
            return pts if s > 0 else list(reversed(pts))

        def core(y, z0, z1, xin):
            pts = [(xin, y, z0), (xo(y, z0) - s * 0.25, y, z0), (xo(y, z1) - s * 0.25, y, z1), (xin, y, z1)]
            return pts if s > 0 else list(reversed(pts))
        loft(mb, F, [core(y, zl(y) + 0.3, zu(y) - 0.15, X(W + 0.25)) for y in (0.3, Y1 - 0.3)], STD)
        y, k, prev = 0.0, 0, False
        while y < Y1 - 0.3:
            y2 = min(Y1, y + 3.4 + 1.6 * K._h01(key, s, "u", k))
            if Y1 - y2 < 1.4:
                y2 = Y1
            dark = K._h01(key, s, "ud", k) < 0.16 and not prev
            loft(mb, F, [sec(yy, zl(yy), zu(yy), X(W)) for yy in (y + 0.03, y2 - 0.03)], STD if dark else WALL)
            prev = dark
            y, k = y2, k + 1

        def csec(yy):
            xa, xb = X(W - 0.12), X(W + GUARD_T + 0.12)
            pts = [(xa, yy, zu(yy)), (xb, yy, zu(yy)), (xb, yy, top(yy) - 0.08), (xb - s * 0.08, yy, top(yy)),
                   (xa + s * 0.08, yy, top(yy)), (xa, yy, top(yy) - 0.08)]
            return pts if s > 0 else list(reversed(pts))
        y, k = 0.0, 0
        while y < Y1 - 0.3:
            y2 = min(Y1, y + 3.0 + 0.8 * K._h01(key, s, "c", k))
            if Y1 - y2 < 1.2:
                y2 = Y1
            loft(mb, F, [csec(y + 0.03), csec(y2 - 0.03)], STP)
            y, k = y2, k + 1
        zmin = min(gz)
        if zmin < zl(Y1) - 0.5:
            zs = _courses((key, s), zmin, zl(Y1), 1.5, 2.1)
            used = []
            for c in range(len(zs) - 1):
                za, zb_ = zs[c], zs[c + 1]
                ystart = max(0.0, tread * ((za + 0.25 + 0.9) / rise - 1.0))
                ycross = tread * ((zb_ + 0.9) / rise - 1.0)
                y, k, prev = ystart, 0, False
                while y < Y1 - 0.3:
                    y2 = min(Y1, y + 2.8 + 1.4 * K._h01(key, s, c, k))
                    if Y1 - y2 < 1.0:
                        y2 = Y1
                    if y < ycross < y2 and ycross - y > 0.6 and y2 - ycross > 0.6:
                        y2 = ycross
                    gmin = min(gat(y), gat(y2), gat((y + y2) / 2))
                    zb0 = max(za, gmin) + 0.03
                    t0, t1 = min(zb_, zl(y)) - 0.03, min(zb_, zl(y2)) - 0.03
                    if min(t0, t1) - zb0 > 0.35:
                        dark = K._h01(key, s, c, k, "d") < 0.16 and not prev
                        loft(mb, F, [sec(y + 0.03, zb0, t0, X(W)), sec(y2 - 0.03, zb0, t1, X(W))],
                             STD if dark else WALL)
                        prev = dark
                        used.append((y, y2))
                    y, k = y2, k + 1
            if used:
                ya, yb_ = min(a for a, b in used), max(b for a, b in used)
                loft(mb, F, [core(yy, zmin + 0.35, zl(yy) + 0.1, X(W + 0.2)) for yy in (ya + 0.1, yb_ - 0.1)], STD)
        for y0, y1 in ((0.0, 1.3), (Y1 - 1.3, Y1)):
            zt = top(y1) + 0.35
            bb(mb, F, X(W - 0.2), X(W + GUARD_T + 0.2), y0, y1, -0.3, zt, ST)
            lathe(mb, F, (X(W + GUARD_T / 2), (y0 + y1) / 2, zt), [(1.05, 0.0), (1.05, 0.16), (0.3, 0.45), (0.1, 0.52)],
                  4, STP, math.pi / 4)


def stairs(mb):
    import op_tree
    ground = op_tree.Ground(-100.0, 330.0, -55.0, 445.0)
    for nm in ("Adro", "CasteloA", "CasteloB"):
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        guard = nm in ("CasteloA", "CasteloB")
        Fst = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
        K.stair_stone(mb, Fst, w, n, rise=L.stair_rise(nm), tread=tread, z_floor=-0.3, cheek_h=1.0, newels=False,
                      cheeks=not guard)
        if guard:
            stair_guard(mb, nm, ground)
        else:                                               # banzo: colisao inclinada sobre a capa (2 lados)
            rise = L.stair_rise(nm)
            for s in (-1, 1):
                x = s * (w / 2 + 0.55)
                a = Fst.p(x, 0.0, rise + 1.0 + 0.3)
                b = Fst.p(x, tread * n, rise * (n + 1) + 1.0 + 0.3)
                col_ramp("OP_CasStairCheek", a, b, 1.9, 2.0)
    K2.toro2(mb, Frame(-77.0, 388.0, CL, 0.0), "L_OPProp_Lamp_Cas_Patamar", 0.9, 30.0)
    col_box("OP_CasLamp", (3.2, 3.2, 7.0), (-77.0, 388.0, CL + 3.5))


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
        print("OP_CAS orcamento: tris %d / 92000 (V3: teto justificado) | MeshParts~ %d / 59 | colisoes %d | luzes de dia %d / 4 | "
              "topo da torre %.1f (KEEP_TOP_Z %.1f)" % (tris, mps, ncol, nl, top, L.KEEP_TOP_Z))
    return tris, mps, ncol


def kz(z):
    """cota local depois do estiramento dos andares de cima (contrato com op_tree.castle_envelope; V2: sem estiramento)"""
    return z


def dummies():
    """bonecos de escala (5,2) nos pontos das folhas - so com OP_CAS_DUMMIES=1 (SCALE_: fora do export e do gate)"""
    for i, (x, y, z, a) in enumerate(DUMMIES):
        DL.dummy("SCALE_Dummy_Cas_%d" % i, x, y, z, a, visible=True)


def build():
    rng = random.Random(4600)
    # 2 objetos (MeshParts = materiais por objeto): torre + salao | patio + adro + subidas + estandartes
    mk = MB("OP_Cas_Keep", C, rng, detail="near", floor=-999)
    keep(mk)
    hall(mk)
    cut = K.cull_hidden(mk)
    mk.finish()
    keep_cols()
    hall_cols()
    mc = MB("OP_Cas_Court", C, rng, detail="near", floor=-999)
    court(mc)
    adro(mc)
    stairs(mc)
    banners(mc)
    cut2 = K.cull_hidden(mc)
    mc.finish()
    print("OP_CAS faces escondidas cortadas: torre %d | patio/adro %d" % (cut, cut2))
    if os.environ.get("OP_CAS_DUMMIES"):
        dummies()
    stats()


# ================================================================== cameras (folhas V2-2)
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
        "CAM_OP_Cas_Jogo_Praca": ((4.0, 236.0, P + 13.0), (0.0, 404.0, CC + 34.0), 24),
        "CAM_OP_Cas_Captura03": ((0.0, 262.0, P + 7.0), (0.0, 380.0, CC + 22.0), 24),
        "CAM_OP_Cas_Ref03": ((0.0, 150.0, P + 46.0), (0.0, 404.0, CC + 36.0), 30),
        "CAM_OP_Cas_Jogo_Patio": ((-14.0, 352.0, CC + 11.0), (0.0, 404.0, CC + 30.0), 24),
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
        "CAM_OP_Cas_PH_SalaoArmadura": ((-10.0, 404.0, CC + FLOOR + e), (-19.5, 419.5, CC + 3.5), 22),
        "CAM_OP_Cas_PH_Mirante": ((-18.0, 357.0, CC + e), (40.0, 280.0, P + 10.0), 22),
        "CAM_OP_Cas_PH_Fundo": ((-52.0, 462.0, CC + e), (20.0, 432.0, CC + 18.0), 22),
        "CAM_OP_Cas_PH_Arvore": ((34.0, 396.0, CC + e), (48.0, 440.0, CC + 9.0), 22),
        "CAM_OP_Cas_C_Telhado": ((-50.0, 366.0, CC + 31.0), (-30.0, 383.0, CC + 24.0), 26),
        "CAM_OP_Cas_C_Chidori": ((-22.0, 352.0, CC + 44.0), (0.0, 384.0, CC + 41.0), 26),
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
        # V3 (paredes com presenca): camera do jogo na avenida + closes por andar, frontoes, engawa, caibros
        "CAM_OP_Cas_Jogo_Avenida": ((3.0, 62.0, L.T1 + 13.0), (0.0, 404.0, CC + 40.0), 22),
        "CAM_OP_Cas_C_Andar1": ((-44.0, 362.0, CC + 7.0), (-16.0, 381.0, CC + 9.0), 24),
        "CAM_OP_Cas_C_Andar3": ((-36.0, 352.0, CC + 30.0), (-8.0, 388.0, CC + 31.0), 26),
        "CAM_OP_Cas_C_Andar4": ((-26.0, 362.0, CC + 48.0), (-4.0, 392.0, CC + 48.0), 26),
        "CAM_OP_Cas_C_FrontaoR2": ((5.0, 360.0, CC + 50.0), (0.0, 393.0, CC + 45.0), 26),
        "CAM_OP_Cas_C_Engawa": ((-40.0, 368.0, CC + 7.5), (-18.0, 380.0, CC + 5.5), 24),
        "CAM_OP_Cas_C_Caibros": ((-36.0, 364.0, CC + 5.5), (-22.0, 380.0, CC + 14.5), 26),
        "CAM_OP_Cas_C_TopoLado": ((-44.0, 396.0, CC + 80.0), (0.0, 404.0, CC + 76.0), 26),
        "CAM_OP_Cas_C_Lateral": ((-70.0, 404.0, CC + 30.0), (0.0, 404.0, CC + 34.0), 26),
    })
    return out


DUMMIES = [(4.0, 300.0, P, 0.0), (9.0, 331.0, CF, 0.0), (-69.0, 364.0, _sz("CasteloA", 364.0), 0.0),
           (-74.0, 388.0, CL, 0.0), (-68.0, 452.0, CC, 0.0), (3.0, 395.0, CC + FLOOR, 0.0), (-26.0, 362.0, CC, 0.0),
           (-68.5, 437.0, _sz("CasteloB", 437.0), 0.0), (-6.0, 372.0, CC, 0.0), (-8.0, 410.0, CC + FLOOR, 0.0),
           (22.0, 425.0, CC, 0.0)]
