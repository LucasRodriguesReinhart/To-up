# il_summon - PECA-HEROI No 1 da Ilha 1: torre estrelada de invocacao + praca redonda (zona summon).
# Prefixo SUM_, colecao 05_SUMMON; pecas moveis VFX_SUM_* em 12_VFX_HELPERS. Substitui il_blockout.summon().
# Referencias: refs/ref_08..12 (torre em 5 angulos) e ref_14/15/18 (posicao na ilha).
#
# Referencial da torre (F): origem = L.SUMMON_TOWER no nivel T1; +v = frente (L.SUMMON_FACE_DEG, para o anel e a
# entrada); +u = lateral; z para cima a partir de T1. O eixo vertical da torre (esfera armilar) fica em v = AX.
#   base (rodada 2): soco escuro 40 x 19,6 com 4 pedestais externos 4x4x5 nas quinas (lanterna japonesa de 4 de
#   altura) + podio de alvenaria azul-acinzentada com friso de ouro grosso e estrelas de 4 pontas; 2 pedestais
#   internos 3x3x3 com cristais grandes; escadaria frontal de 5 degraus com bordas azuis brilhando -> PATAMAR de 7 de
#   fundo (sem lanternas: a camera da invocacao fica atras do jogador) -> PORTAL recuado num nicho (energia azul +
#   estrela de cristal; nao se entra: e a maquina de invocacao; SUMMON_Interact/PlayerPosition ficam no patamar);
#   corpo L1 (portal) -> cornija de ouro -> L2 (janela-estrela) -> cornija -> coroa L3 -> prato de ouro;
#   esfera armilar: gaiola fixa + 3 aneis moveis (VFX_SUM_Ring_1..3) + estrela de cristal em 2 Neon alternados por
#   faceta (VFX_SUM_Star) + constelacao azul em 2 asas; 2 mastros laterais com estandartes e lanternas penduradas.
# Praca: piso redondo de mosaico (roxo + estrela + aneis dourados, pecas lado a lado acima do gramado: sem
# z-fighting), balaustrada de pedra e ouro aberta para a escada do anel (170 graus, il_col.RADIAL_STAIRS) e para a
# vila (NE); livre >= 14 x 14 na frente da torre. Rotas proprias no QA: EXTRA_ROUTES (fim do arquivo de cameras).
# Regra de chanfro da rodada 2 (BV): so peca grande recebe chanfro; nada de lasca (ver il_summon_kit.spike).
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box, mk
import il_layout as L
import fm_lib
from fm_lib import light
import fm_parts as FP
from fm_parts import Frame
import fm_portal_kit as PK
from il_col import RADIAL_STAIRS, STAIR_TOP_R
import il_summon_kit as K

# ------------------------------------------------------------------ materiais novos da zona (6 de 6)
_S = fm_lib.S
fm_lib.MATS.setdefault("Crystal_SumPortal_Glow", (_S(58, 70, 232), 0.3, 0.0, 1.15, _S(64, 84, 255), 0.0))
fm_lib.MATS.setdefault("Crystal_SumStar_Glow", (_S(178, 222, 255), 0.2, 0.0, 2.6, _S(150, 206, 255), 0.0))
fm_lib.MATS.setdefault("Stone_SumFloor_Pale", (_S(212, 194, 236), 0.8, 0.0, 0, None, 0.06))
fm_lib.MATS.setdefault("Stone_SumBlock", (_S(140, 144, 188), 0.8, 0.0, 0, None, 0.08))    # bloco claro (rodada 2: mais claro)
# estrela da esfera (rodada 2): 2 Neon alternados por faceta -> le como cristal lapidado no Roblox
fm_lib.MATS.setdefault("Crystal_SumAmber_Glow", (_S(255, 160, 40), 0.3, 0.0, 3.0, _S(255, 138, 20), 0.0))
fm_lib.MATS.setdefault("Crystal_SumYellow_Glow", (_S(255, 228, 120), 0.3, 0.0, 3.0, _S(255, 214, 90), 0.0))

# ------------------------------------------------------------------ referencial e medidas (studs)
TX, TY = L.SUMMON_TOWER
FACE = math.radians(L.SUMMON_FACE_DEG)
YAW = FACE - math.pi / 2                       # o blockout usa o mesmo: +Y local = frente
Z0 = L.T1
F = Frame(TX, TY, Z0, YAW)
XU = Vector((math.cos(YAW), math.sin(YAW), 0.0))       # +u (mundo)
YV = Vector((-math.sin(YAW), math.cos(YAW), 0.0))      # +v = frente (mundo)
ZZ = Vector((0.0, 0.0, 1.0))
CX, CY = L.SUMMON_C
PR = L.SUMMON_R

AX = -3.0                    # v do eixo vertical (esfera, coroa, L2)
# rodada 2: plinto 5,5 mais largo de cada lado (pedestais de lanterna 4x4x5 nas 4 quinas) e podio ate os pedestais
PLINTH = (20.0, -11.6, 8.0)  # meia largura u, v de tras, v da frente (soco escuro, z -0.5..0.8)
PLZ = 0.8
POD = (16.0, -10.2, 7.2)     # podio de alvenaria (z 0.8..2.75) + friso de ouro grosso (2.75..3.3)
POD_TOP = 3.3
OUT_PED = (18.0, 5.8, -9.4, 4.0, 5.0)        # pedestais externos: u, v frente, v tras, lado, altura
IN_PED = (9.6, 5.6, 3.0, 3.0)                # pedestais internos dos cristais: u, v, lado, altura (sobre o podio)
LANT_H = 4.0                 # altura das lanternas dos pedestais externos
ST_W, ST_N, ST_RISE, ST_TREAD = 7.6, 5, 0.8, 1.6
# patamar do portal (rodada 2): o portal foi recuado para um NICHO no corpo L1 (plano da energia em PV) e o patamar
# vai de PV ate o topo da escada: 7 de fundo, sem lanternas (a camera da invocacao fica atras do jogador, sobre a
# escada). O jogador sobe a escada e para diante do portal: SUMMON_Interact e SUMMON_PlayerPosition ficam aqui.
PV = -1.4                    # v do plano da energia do portal (fundo do nicho)
LAND_Z = ST_N * ST_RISE      # 4.0 patamar do portal
LAND_V = (PV, 5.6)           # -1.4 .. 5.6
ST_FOOT = LAND_V[1] + ST_N * ST_TREAD       # 13.6 pe da escada
CORR = ST_W / 2 + 1.2        # meia largura do corredor da escada (com os banzos) = 5.0
PORT_HW, PORT_SPRING = 4.0, 12.0            # vao do portal (8 x 16 ate o fecho)
NICHE_TOP = PORT_SPRING + PORT_HW + 0.3     # teto do nicho (acima do fecho do arco)
L1 = (7.3, -8.8, 1.2, POD_TOP, 20.4)        # corpo L1: meia largura, v tras, v frente (boca do nicho), z0, z1
L2 = (6.0, -7.7, 1.1, 21.3, 31.8)
L3 = (4.6, AX - 4.6, AX + 4.6, 32.6, 36.4)
ZS = 46.0                    # centro da esfera armilar (acima de T1)
CAGE_R = 9.2
MAST_U, MAST_V = 10.4, AX
FREE_V = (ST_FOOT, ST_FOOT + 14.0)          # espaco livre na frente (14 x 14)
BUT_V = 2.35                 # v dos contrafortes da frente do L1 (ladeiam o frontispicio)
L1_SWIN = (13.4, 18.1, 1.3)  # janelas dos lados do L1: z do peitoril, z da nascenca, meia largura (arco pleno)
L1_BWIN = (7.0, 14.8, 1.7)   # janela gotica do fundo do L1
BAN_TH = math.radians(35.0)  # estandartes girados 35 graus para a frente: leem de frente, dos lados e de tras


def P(u, v, z=0.0):
    return F.p(u, v, z)


def RT(rx=0.0, ry=0.0, rz=0.0):
    return F.r(rx, ry, rz)


def to_local(x, y):
    d = Vector((x - TX, y - TY, 0.0))
    return d.dot(XU), d.dot(YV)


def in_footprint(x, y, pad=0.0):
    """ponto dentro da pegada da torre (soco + escada)"""
    u, v = to_local(x, y)
    if abs(u) < PLINTH[0] + pad and PLINTH[1] - pad < v < PLINTH[2] + pad:
        return True
    return abs(u) < CORR + 1.4 + pad and PLINTH[2] - 0.1 < v < ST_FOOT + pad


# escada do anel (terreno): eixo radial a 170 graus, topo em r = STAIR_TOP_R
_SA = [a for k, a, w in RADIAL_STAIRS if k == "SUMMON"][0]
_SW = [w for k, a, w in RADIAL_STAIRS if k == "SUMMON"][0]
SU = Vector((math.cos(math.radians(_SA)), math.sin(math.radians(_SA)), 0.0))    # sobe a escada (para fora)
SL = Vector((-SU.y, SU.x, 0.0))
S_HW = _SW / 2 + 1.2         # meia largura com os banzos


def stair_zone(x, y, pad=0.0):
    """ponto sobre o entalhe da escada do anel (nao pavimentar)"""
    p = Vector((x, y, 0.0))
    return p.dot(SU) < STAIR_TOP_R + 0.2 + pad and abs(p.dot(SL)) < S_HW + pad


# cameras de revisao (360 graus + altura do jogador)
def _cam(u, v, z, tu, tv, tz, lens):
    a, b = P(u, v, z), P(tu, tv, tz)
    return ((round(a.x, 2), round(a.y, 2), round(a.z, 2)), (round(b.x, 2), round(b.y, 2), round(b.z, 2)), lens)


PLAYER_V = 3.4               # v do SUMMON_PlayerPosition (no patamar, olhando o portal)

CAMS = {
    # 360 graus (a torre inteira, da base ao topo da constelacao ~ 60 acima do T1)
    "CAM_Summon_Front": _cam(0.0, 84.0, 24.0, 0.0, AX, 31.0, 22),
    "CAM_Summon_34": _cam(-50.0, 62.0, 28.0, 0.0, AX, 30.0, 22),
    "CAM_Summon_Side": _cam(-88.0, 4.0, 26.0, 0.0, AX, 30.0, 22),
    "CAM_Summon_Side2": _cam(86.0, 8.0, 26.0, 0.0, AX, 30.0, 22),
    "CAM_Summon_Back": _cam(10.0, -84.0, 30.0, 0.0, AX, 30.0, 22),
    "CAM_Summon_High": _cam(40.0, 64.0, 70.0, 0.0, AX, 28.0, 22),
    "CAM_Summon_Top": ((CX + 0.01, CY - 6.0, L.T1 + 150.0), (CX, CY, L.T1), 24),
    # altura do jogador (olho a 4,6): na praca olhando a torre, e no patamar olhando o portal
    "CAM_Summon_Player": _cam(-4.5, 31.0, 4.6, 0.0, AX, 22.0, 18),
    "CAM_Summon_LandEye": _cam(1.4, LAND_V[1] - 0.4, LAND_Z + 4.6, 0.0, PV, LAND_Z + 6.5, 15),
    # camera da animacao de invocacao (atras do jogador, sobre a escada): prova o patamar livre
    "CAM_Summon_Landing": _cam(0.0, PLAYER_V + 10.5, LAND_Z + 5.5, 0.0, PV, LAND_Z + 5.0, 18),
    "CAM_Summon_Base": _cam(16.0, 36.0, 9.0, 0.0, 1.0, 5.0, 20),
    # chegada pela escada do anel (170 graus): o jogador ve a torre de frente, a 3/4
    "CAM_Summon_Arrive": ((-78.0, 13.0, L.RING + 5.4), (-110.0, 24.0, L.T1 + 12.0), 20),
    # vista geral a partir da entrada (a torre na ilha, como nas refs 14/15)
    "CAM_Summon_Far": ((-20.0, -95.0, L.G + 60.0), (-133.0, 36.0, L.T1 + 28.0), 30),
}

# rotas registradas no QA (il_qa.module_routes): subir a escada da torre ate o patamar diante do portal, e chegar
# do T1 a NE (rua em arco da vila) pela abertura NE da balaustrada ate o centro da praca
_NE = math.radians(42.0)                      # = VILLAGE_A (abertura NE da balaustrada, a partir do centro da praca)
EXTRA_ROUTES = {
    "PRACA->PORTAL": ([(CX, CY)] + [tuple(P(0.0, v, 0.0).xy) for v in (ST_FOOT + 3.0, ST_FOOT - 0.3,
                                                                      LAND_V[1] - 0.6, PLAYER_V, PV + 1.9)], L.T1),
    "T1_NO->SUMMON": ([(CX + r * math.cos(_NE), CY + r * math.sin(_NE)) for r in (44.0, 34.0, 27.0, 20.0, 10.0)] +
                      [(CX, CY)], L.T1),
}


# ------------------------------------------------------------------ utilidades
def BV(size, b):
    """regra de chanfro da rodada 2 (critica tecnica): 0 se a menor dimensao < 1,0; senao <= 5% da menor dimensao.
    Chanfro pequeno em peca fina so vira lasca (triangulo fino) na malha do Roblox."""
    mn = min(size)
    if mn < 1.0 or not b:
        return 0.0
    bv = min(b, 0.05 * mn)
    return bv if bv >= 0.15 else 0.0     # abaixo de 0,15 o chanfro nao se ve e so gera lascas


def face_skin(mb, a_uv, b_uv, z0, z1, rng, openings=(), thick=0.8, course=2.0, blk=(2.4, 4.0),
              m="Stone_SumBlock", m2="Summon_Stone", quoins=(True, True), base_dark=True, mix=0.1):
    """pele de alvenaria (blocos) numa face vertical da torre; a_uv, b_uv em (u, v) locais"""
    a = P(a_uv[0], a_uv[1], 0.0)
    b = P(b_uv[0], b_uv[1], 0.0)
    openings = [tuple([o[0], o[1], Z0 + o[2], Z0 + o[3]] + list(o[4:])) for o in openings]
    FP.masonry_wall(mb, (a.x, a.y), (b.x, b.y), Z0 + z0, Z0 + z1, thick, rng, m=m, m2=m2, course=course, mix=mix,
                    openings=openings, blk=blk, core=False, quoins=quoins, base_dark=base_dark,
                    bevel=BV((thick, course, blk[0]), 0.14))


def lbox(mb, size, u, v, z, m, bevel=0.1, rz=0.0):
    """caixa no referencial da torre (z = centro, relativo a T1)"""
    mb.box(size, P(u, v, z), RT(0, 0, rz), m, BV(size, bevel))


def lbox2(mb, u0, v0, z0, u1, v1, z1, m, bevel=0.1):
    lbox(mb, (abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, m, bevel)


def lcol(size, u, v, z, area="SummonTower"):
    col_box(area, size, P(u, v, z), RT())


def lcol2(u0, v0, z0, u1, v1, z1, area="SummonTower"):
    lcol((abs(u1 - u0), abs(v1 - v0), abs(z1 - z0)), (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2, area)


def gold_star4(gold, u, v, z, r, face="v+", depth=0.34):
    """estrela dourada de 4 pontas aplicada numa face (v+ frente, v- tras, u+ / u- lados). Sem borda (a borda fina
    de 0,12 virava lasca): bipiramide, a metade de tras entra na parede."""
    if face in ("v+", "v-"):
        s = 1.0 if face == "v+" else -1.0
        K.star(gold, P(u, v + s * 0.05, z), XU, ZZ, 4, r, r * 0.28, depth, "Metal_Gold")
    else:
        s = 1.0 if face == "u+" else -1.0
        K.star(gold, P(u + s * 0.05, v, z), YV, ZZ, 4, r, r * 0.28, depth, "Metal_Gold")


def larch(mb, u, v, width, z_spring, rise, depth, m="Stone_SumBlock", key_m="Summon_Stone", n=9, band=1.3,
          keystone=True, seed=0):
    """arco de aduelas (semi-elipse) no plano u-z da torre, centrado em (u, v); como fm_parts.arch, mas sem chanfro
    (regra da rodada 2) e com as impostas altas o bastante para nao virar lamina"""
    c = P(u, v, 0.0)
    d = XU
    hw = width / 2
    pts = []
    for i in range(n + 1):
        t = math.pi * i / n
        pts.append((math.cos(t) * (hw + band / 2), math.sin(t) * (rise + band / 2)))
    lr = random.Random(701 + seed)
    for i in range(n):
        (x0, z0), (x1, z1) = pts[i], pts[i + 1]
        mid = c + d * ((x0 + x1) / 2) + Vector((0, 0, z_spring + (z0 + z1) / 2))     # c ja esta em T1
        ln = math.hypot(x1 - x0, z1 - z0) + 0.05
        tilt = math.atan2(z1 - z0, x1 - x0)
        key = keystone and i == n // 2
        mm = key_m if key else m
        sc = 1.25 if key else lr.uniform(0.94, 1.1)
        dep = depth * (1.14 if key else lr.uniform(0.98, 1.07))
        mb.box((ln - 0.12, dep, band * sc), mid + Vector((0, 0, band * (sc - 1) * 0.3)),
               (0, -tilt + lr.uniform(-0.025, 0.025), YAW), mm, 0.0)
    for s in (-1, 1):
        lbox(mb, (band + 0.4, depth + 0.3, 0.6), u + s * (hw + band / 2), v, z_spring - 0.3, m, 0.0)


def lstairs(stone, glow, area="SummonTower"):
    """escadaria frontal (5 degraus) com banzos e bordas azuis brilhando; como fm_parts.stairs (mesma colisao:
    rampa pelo meio dos pisos + meia pisada final + banzos-guarda), com chanfro pela regra da rodada 2"""
    base = P(0.0, ST_FOOT, 0.0)
    ang = FACE + math.pi
    Fs = Frame(base.x, base.y, base.z, ang)
    rise, tread, n, width = ST_RISE, ST_TREAD, ST_N, ST_W
    for i in range(n):
        sz = (tread + 0.15, width, rise * (i + 1))
        stone.box(sz, Fs.p(tread * i + tread / 2, 0, rise * (i + 1) / 2), Fs.r(), "Summon_Stone", BV(sz, 0.14))
        for s in (-1, 1):
            h = rise * (i + 1) + 1.2
            sb = (tread + 0.05, 1.2, h)
            stone.box(sb, Fs.p(tread * i + tread / 2, s * (width / 2 + 0.6), h / 2), Fs.r(), "Summon_Stone_Dark",
                      BV(sb, 0.16))
            # borda azul brilhando: faixa de 0,4 x 0,3 na quina do piso + espelho (salta 0,15 das faces)
            y = s * (width / 2 - 0.35)
            xf = tread * i - 0.075               # face do espelho do degrau i
            glow.box((tread, 0.4, 0.3), Fs.p(xf + tread / 2, y, rise * (i + 1)), Fs.r(), "Summon_Blue_Glow", 0.0)
            glow.box((0.3, 0.4, rise + 0.15), Fs.p(xf, y, rise * i + (rise + 0.15) / 2), Fs.r(),
                     "Summon_Blue_Glow", 0.0)
    bot = Fs.p(-tread / 2, 0, 0)
    top = Fs.p(tread * n - tread / 2, 0, rise * n)
    IL.col_ramp(area, bot, top, width)
    q = Fs.p(tread * n - tread / 4 + 0.15, 0, rise * n - 0.5)
    col_box(area, (tread / 2 + 0.3, width, 1.0), (q.x, q.y, q.z), Fs.r())
    k = rise / tread
    H = 4.0
    T = H + 1.5
    off = k * (tread * k / 2 + H) / (1 + k * k)
    for s in (-1, 1):
        y = s * (width / 2 + 0.6)
        xa, xb = -off, tread * n - off
        IL.col_ramp(area, Fs.p(xa, y, (xa + tread / 2) * k + H), Fs.p(xb, y, (xb + tread / 2) * k + H), 1.2, thick=T)


# ------------------------------------------------------------------ praca: piso de mosaico
def _ring_pieces(r0, r1, step_len, a_off=0.0):
    """pecas (poligonos mundo) de um anel em volta do centro da praca, cortadas no entalhe da escada"""
    out = []
    rm = (r0 + r1) / 2
    n = max(8, int(round(2 * math.pi * rm / step_len)))
    for i in range(n):
        a0 = a_off + 360.0 * i / n
        a1 = a_off + 360.0 * (i + 1) / n
        g = math.degrees(0.11 / rm)
        pts = IL.arc_pts(r1, a0 + g, a1 - g, max(1.0, (a1 - a0) / 2.0), CX, CY)
        pts += IL.arc_pts(r0, a1 - g, a0 + g, max(1.0, (a1 - a0) / 2.0), CX, CY)
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        if in_footprint(cx, cy, -0.6):
            continue
        if stair_zone(cx, cy):
            pts = IL.clip(pts, -SU.x, -SU.y, -(STAIR_TOP_R + 0.25))
            if len(pts) < 3 or abs(IL.area(pts)) < 0.3:
                continue
        out.append(IL.ccw(pts))
    return out


# piso (rodada 2): o gramado do T1 passa inteiro por baixo da praca com o topo EXATAMENTE em T1, e no Roblox
# superficies de materiais diferentes a menos de 0,1 piscam (z-fighting). Entao: base escura 0,15 acima do gramado;
# mosaico (roxo, faixas claras, aneis de ouro, lajes) em pecas LADO A LADO (sem sobreposicao) 0,15 acima da base,
# com o rejunte da base aparecendo entre elas; enfeites (contorno e miolo da estrela, estrelinhas) sao facetados
# (bipiramides / vigas em losango: as faces ja sao o chanfro) e sobem 0,2-0,3 acima do mosaico.
ZB = 0.15            # topo da base escura (acima de T1)
ZL1 = 0.30           # topo do mosaico


def plaza_floor():
    rng = random.Random(601)
    mb = MB("SUM_Plaza_Floor", "05_SUMMON", rng, detail="far")
    # base escura (rejunte / meio-fio), cortada na linha do topo da escada do anel
    disc = IL.arc_pts(PR + 0.25, 0.0, 360.0, 4.0, CX, CY)[:-1]
    disc = IL.clip(disc, -SU.x, -SU.y, -(STAIR_TOP_R + 0.25))
    mb.prism(IL.ccw(disc), Z0 - 0.3, Z0 + ZB, "Summon_Stone_Dark")
    # colisao do patamar: o mosaico fica 0,30 acima do chao T1 (degrau do santuario); sem isto o jogador afundava
    # 0,30 no piso, porque a colisao do terreno (il_col.terrain_col) e plana em T1 embaixo da praca inteira.
    IL.col_poly("SummonPlaza", disc, Z0 - 1.0, Z0 + ZL1, 4.0, mode="inter")
    # faixas do mosaico (r0, r1, material, comprimento da peca): o roxo tambem e faixa (entre os aneis)
    bands = [(12.45, 12.95, "Metal_Gold", 3.0), (13.05, 14.3, "Stone_SumFloor_Pale", 2.6),
             (14.4, 14.9, "Metal_Gold", 3.0), (15.0, 22.5, "Summon_Floor", 3.6),
             (22.6, 23.2, "Stone_SumFloor_Pale", 3.0), (23.3, 25.25, "Summon_Floor", 3.2),
             (25.35, 26.05, "Metal_Gold", 3.2), (26.15, 27.95, "Stone_Paving_Warm", 2.5)]
    for r0, r1, m, st in bands:
        for poly in _ring_pieces(r0, r1, st, 1.0 if m != "Stone_Paving_Warm" else 2.0):
            mb.prism(poly, Z0, Z0 + ZL1, m)
    # estrela de 5 pontas no centro (uma ponta para a torre): estrela clara + roxo em cunhas em volta (recortado)
    to_t = math.atan2(TY - CY, TX - CX)
    rot = to_t - math.pi / 2
    sp = K.star_pts(5, 10.2, 4.1, rot)
    mb.prism(IL.ccw([(CX + x, CY + y) for x, y in sp]), Z0, Z0 + ZL1, "Stone_SumFloor_Pale")
    rc = 12.35
    for i in range(len(sp)):
        a, b = sp[i], sp[(i + 1) % len(sp)]
        ta, tb = math.degrees(math.atan2(a[1], a[0])), math.degrees(math.atan2(b[1], b[0]))
        while tb < ta:
            tb += 360.0
        arc = IL.arc_pts(rc, tb, ta, 4.0, CX, CY)
        w = [(CX + a[0], CY + a[1]), (CX + b[0], CY + b[1])] + [tuple(p) for p in arc]
        mb.prism(IL.ccw(w), Z0, Z0 + ZL1, "Summon_Floor")
    # contorno de ouro: vigas em losango meio enterradas (crista 0,26 acima do mosaico)
    for i in range(len(sp)):
        a, b = sp[i], sp[(i + 1) % len(sp)]
        mb.beam((CX + a[0], CY + a[1], Z0 + ZL1 - 0.02), (CX + b[0], CY + b[1], Z0 + ZL1 - 0.02),
                0.4, 0.4, "Metal_Gold", 0.0, roll=math.pi / 4)
    # miolo: estrela de ouro facetada (bipiramide rasa deitada no piso)
    # (borda vertical de 0,3 com o centro 0,05 acima do mosaico: as facetas comecam 0,2 acima - nada rasante)
    K.star(mb, (CX, CY, Z0 + ZL1 + 0.05), (1, 0, 0), (0, 1, 0), 5, 3.2, 1.3, 0.3, "Metal_Gold", rot=rot, edge=0.3)
    # estrelinhas de 4 pontas douradas facetadas no campo roxo (fora da pegada da torre)
    for i in range(10):
        a = math.radians(18.0 + 36.0 * i)
        x, y = CX + 18.9 * math.cos(a), CY + 18.9 * math.sin(a)
        if in_footprint(x, y, 1.5):
            continue
        K.star(mb, (x, y, Z0 + ZL1 + 0.05), (1, 0, 0), (0, 1, 0), 4, 1.7, 0.5, 0.24, "Metal_Gold", rot=a, edge=0.3)
    mb.finish()


# ------------------------------------------------------------------ praca: balaustrada (pedra clara + ouro)
RB = 26.9            # raio da balaustrada
VILLAGE_A = 42.0     # abertura para a vila (NE), graus a partir do centro da praca
VILLAGE_HW = 5.6


def _rail_blocked(a_deg):
    x = CX + RB * math.cos(math.radians(a_deg))
    y = CY + RB * math.sin(a_deg * math.pi / 180.0)
    p = Vector((x, y, 0.0))
    if abs(p.dot(SL)) < S_HW + 0.35 and p.dot(SU) < STAIR_TOP_R + 3.0:
        return "stair"
    d = (a_deg - VILLAGE_A + 180.0) % 360.0 - 180.0
    if abs(math.radians(d) * RB) < VILLAGE_HW:
        return "village"
    if in_footprint(x, y, 0.9):
        return "tower"
    return None


def rail_spans():
    step = 0.25
    n = int(360 / step)
    flags = [_rail_blocked(i * step) for i in range(n)]
    # comeca num ponto bloqueado para as corridas nao cruzarem o zero
    i0 = next(i for i in range(n) if flags[i])
    spans = []
    cur = None
    for k in range(1, n + 1):
        i = (i0 + k) % n
        a = i0 * step + k * step
        if flags[i] is None:
            if cur is None:
                cur = [a, a, flags[(i - 1) % n]]
            cur[1] = a
        elif cur is not None:
            spans.append((cur[0], cur[1], cur[2], flags[i]))
            cur = None
    return spans


def plaza_rail():
    rng = random.Random(611)
    mb = MB("SUM_Plaza_Rail", "05_SUMMON", rng, detail="near")
    zb = Z0 + ZL1 - 0.05
    for a0, a1, why0, why1 in rail_spans():
        ln = math.radians(a1 - a0) * RB
        nb = max(1, int(round(ln / 4.3)))
        angs = [a0 + (a1 - a0) * i / nb for i in range(nb + 1)]
        pts = [Vector((CX + RB * math.cos(math.radians(a)), CY + RB * math.sin(math.radians(a)), zb)) for a in angs]
        for i, (p, a) in enumerate(zip(pts, angs)):
            end = i in (0, len(pts) - 1)
            gate = (i == 0 and why0 in ("stair", "village")) or (i == len(pts) - 1 and why1 in ("stair", "village"))
            rz = math.radians(a)
            s = 1.35 if gate else 1.0
            h = 3.6 if gate else 2.8
            mb.box((1.5 * s, 1.5 * s, 0.4), p + Vector((0, 0, 0.2)), (0, 0, rz), "Stone_Wall_Light", 0.0)
            mb.box((1.15 * s, 1.15 * s, h), p + Vector((0, 0, h / 2 + 0.3)), (0, 0, rz), "Stone_Wall_Light", 0.0)
            mb.box((1.5 * s, 1.5 * s, 0.35), p + Vector((0, 0, h + 0.47)), (0, 0, rz), "Stone_Wall_Light", 0.0)
            top = p + Vector((0, 0, h + 0.65))
            if gate or (i % 3 == 1 and not end):
                # lanterninha no poste
                mb.box((0.95 * s, 0.95 * s, 0.3), top + Vector((0, 0, 0.12)), (0, 0, rz), "Metal_Gold", 0.0)
                mb.box((0.72 * s, 0.72 * s, 0.95 * s), top + Vector((0, 0, 0.25 + 0.47 * s)), (0, 0, rz),
                       "Lantern_Glow", 0.0)
                mb.cyl(0.85 * s, 0.55 * s, top + Vector((0, 0, 0.25 + 0.95 * s + 0.27 * s)), (0, 0, rz + math.pi / 4),
                       "Metal_Gold", 4, r2=0.3, bevel=0.0)
            else:
                mb.box((0.62, 0.62, 0.3), top + Vector((0, 0, 0.12)), (0, 0, rz), "Metal_Gold", 0.0)
                PK.octa(mb, top + Vector((0, 0, 0.62)), 0.36, 0.42, "Metal_Gold", rot=rz)
        for a, b in zip(pts, pts[1:]):
            d = b - a
            if d.length < 1.6:
                continue
            u = d.normalized()
            a2, b2 = a + u * 0.55, b - u * 0.55
            mb.beam(a2 + Vector((0, 0, 0.35)), b2 + Vector((0, 0, 0.35)), 0.95, 0.5, "Stone_Wall_Light", 0.0)
            mb.beam(a2 + Vector((0, 0, 2.45)), b2 + Vector((0, 0, 2.45)), 0.8, 0.42, "Stone_Wall_Light", 0.0)
            mb.beam(a2 + Vector((0, 0, 2.79)), b2 + Vector((0, 0, 2.79)), 0.5, 0.3, "Metal_Gold", 0.0)
            nbal = max(1, int(d.length / 1.45) - 1)
            for k in range(nbal):
                q = a2 + (b2 - a2) * ((k + 1) / (nbal + 1))
                mb.box((0.48, 0.48, 1.6), q + Vector((0, 0, 1.4)), (0, 0, math.atan2(d.y, d.x) + math.pi / 4),
                       "Stone_Wall_Light", 0.0)
        # colisao: cordas de ate ~24 graus
        nc = max(1, int(math.ceil((a1 - a0) / 24.0)))
        for k in range(nc):
            ca = a0 + (a1 - a0) * k / nc
            cb = a0 + (a1 - a0) * (k + 1) / nc
            pa = Vector((CX + RB * math.cos(math.radians(ca)), CY + RB * math.sin(math.radians(ca)), zb))
            pb = Vector((CX + RB * math.cos(math.radians(cb)), CY + RB * math.sin(math.radians(cb)), zb))
            d = pb - pa
            c = (pa + pb) / 2
            col_box("SummonRail", (d.length + 1.2, 1.3, 4.4), (c.x, c.y, zb + 2.0), (0, 0, math.atan2(d.y, d.x)))
    mb.finish()


# ------------------------------------------------------------------ torre: pedra (soco, podio, escada, corpos)
def tower_stone(stone, gold, glow):
    rng = random.Random(621)
    pu, pv0, pv1 = PLINTH
    # soco escuro (2 alas + fundo) com fiada de blocos nas faces
    for s in (-1, 1):
        lbox2(stone, s * CORR, pv0, -0.5, s * pu, pv1, PLZ - 0.1, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -CORR, pv0, -0.5, CORR, POD[1], PLZ - 0.1, "Summon_Stone_Dark", 0.0)
    sk = dict(course=1.4, blk=(2.2, 3.4), thick=0.7, m="Summon_Stone_Dark", m2="Summon_Stone", base_dark=False,
              quoins=(False, False))
    face_skin(stone, (-pu - 0.2, pv1 + 0.2), (-CORR, pv1 + 0.2), -0.5, PLZ, rng, **sk)
    face_skin(stone, (CORR, pv1 + 0.2), (pu + 0.2, pv1 + 0.2), -0.5, PLZ, rng, **sk)
    for s in (-1, 1):
        face_skin(stone, (s * (pu + 0.2), pv1 + 0.5), (s * (pu + 0.2), pv0 - 0.5), -0.5, PLZ, rng, **sk)
    face_skin(stone, (-pu - 0.5, pv0 - 0.2), (pu + 0.5, pv0 - 0.2), -0.5, PLZ, rng, **sk)
    # rodape de ouro do soco (0,45 de altura, 0,55 de balanco)
    for s in (-1, 1):
        lbox2(gold, s * CORR, pv1 + 0.1, PLZ - 0.25, s * (pu + 0.65), pv1 + 0.65, PLZ + 0.2, "Metal_Gold", 0.0)
        lbox2(gold, s * (pu + 0.1), pv0 - 0.65, PLZ - 0.25, s * (pu + 0.65), pv1 + 0.65, PLZ + 0.2, "Metal_Gold", 0.0)
    lbox2(gold, -pu - 0.65, pv0 - 0.65, PLZ - 0.25, pu + 0.65, pv0 - 0.1, PLZ + 0.2, "Metal_Gold", 0.0)
    # podio (ate os pedestais externos): nucleo escuro + pele de alvenaria (2 fiadas) + friso de ouro grosso
    du, dv0, dv1 = POD
    zf = 2.75
    # nucleo escuro + fiada de topo clara (o topo do podio e pedra; o ouro fica so nas bordas, sem sobrepor o topo)
    for s in (-1, 1):
        lbox2(stone, s * CORR, dv0 + 0.2, PLZ - 0.1, s * (du - 0.2), dv1 - 0.2, zf, "Summon_Stone_Dark", 0.0)
        lbox2(stone, s * CORR, dv0 + 0.2, zf, s * (du - 0.2), dv1 - 0.2, POD_TOP, "Summon_Stone", 0.0)
    lbox2(stone, -CORR, dv0 + 0.2, PLZ - 0.1, CORR, LAND_V[0], zf, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -CORR, dv0 + 0.2, zf, CORR, LAND_V[0], POD_TOP, "Summon_Stone", 0.0)
    for s in (-1, 1):
        face_skin(stone, (s * CORR, dv1 + 0.1), (s * (du + 0.3), dv1 + 0.1), PLZ, zf, rng, course=1.0,
                  blk=(2.0, 3.2), thick=0.6)
        face_skin(stone, (s * du, dv1 + 0.4), (s * du, dv0 - 0.4), PLZ, zf, rng, course=1.0, blk=(2.0, 3.2),
                  thick=0.6)
    face_skin(stone, (-du - 0.3, dv0), (du + 0.3, dv0), PLZ, zf, rng, course=1.0, blk=(2.0, 3.4), thick=0.6)
    # friso de ouro grosso (0,55) so nas bordas do podio: frente, lados e fundo
    for s in (-1, 1):
        lbox2(gold, s * CORR, dv1 - 0.2, zf, s * (du + 0.45), dv1 + 0.45, POD_TOP, "Metal_Gold", 0.0)
        lbox2(gold, s * (du - 0.2), dv0 - 0.45, zf, s * (du + 0.45), dv1 + 0.45, POD_TOP, "Metal_Gold", 0.0)
    lbox2(gold, -du - 0.45, dv0 - 0.45, zf, du + 0.45, dv0 + 0.2, POD_TOP, "Metal_Gold", 0.0)
    # estrelas de 4 pontas douradas nos paineis do podio (frente, lados entre os pedestais e fundo)
    zs = (PLZ + zf) / 2
    for s in (-1, 1):
        for v in (-4.6, 0.6):
            gold_star4(gold, s * (du + 0.3), v, zs, 0.8, "u+" if s > 0 else "u-")
        for u in (IN_PED[0], 13.3):
            gold_star4(gold, s * u, dv1 + 0.4, zs, 0.8, "v+")
    for u in (-12.0, -6.0, 0.0, 6.0, 12.0):
        gold_star4(gold, u, dv0 - 0.3, zs, 0.8, "v-")
    # escadaria frontal (5 degraus) com banzos e bordas azuis
    lstairs(stone, glow)
    # patamar do portal (7 de fundo: do fundo do nicho ate o topo da escada)
    lbox2(stone, -CORR + 0.05, LAND_V[0], 0.0, CORR - 0.05, LAND_V[1], LAND_Z, "Summon_Stone", 0.0)
    # --- corpo L1: nucleo com o NICHO do portal (fundo em PV) + contrafortes de canto + pele de alvenaria
    hw, v0, v1, z0, z1 = L1
    nw = PORT_HW + 0.8                               # face interna do nucleo dos lados do nicho
    lbox2(stone, -hw, v0, z0, hw, PV, z1, "Summon_Stone_Dark", 0.0)
    for s in (-1, 1):
        lbox2(stone, s * nw, PV, z0, s * hw, v1, z1, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -nw, PV, NICHE_TOP, nw, v1, z1, "Summon_Stone_Dark", 0.0)
    # paredes do nicho: fiadas alternadas (continuam as ombreiras do frontispicio) + abobada de aduelas
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Summon_Stone" if k % 2 == 0 else "Stone_SumBlock"
            lbox(stone, (0.8, v1 - PV - 0.1, zz1 - zz0 - 0.08), s * (PORT_HW + 0.4), (PV + v1) / 2, (zz0 + zz1) / 2,
                 m, 0.0)
    larch(stone, 0.0, (PV + v1) / 2, 2 * PORT_HW, PORT_SPRING, PORT_HW, v1 - PV - 0.1, m="Summon_Stone",
          key_m="Stone_SumBlock", n=9, band=2.4, keystone=False, seed=1)
    # janelas altas do L1: uma em cada lado (acima da asa do mastro) e uma gotica no fundo
    s_side = (v1 - 0.6) - MAST_V
    side_op = (s_side - 1.75, s_side + 1.75, L1_SWIN[0] - 0.2, L1_SWIN[1] + L1_SWIN[2] + 0.5, L1_SWIN[2] + 0.45)
    for s in (-1, 1):
        face_skin(stone, (s * (hw + 0.25), v1 - 0.6), (s * (hw + 0.25), v0 + 0.6), z0, z1, rng, course=2.1,
                  blk=(2.6, 4.2), thick=0.8, openings=[side_op])
        for dv in (-1, 1):
            lbox(stone, (0.9, 0.7, L1_SWIN[1] - L1_SWIN[0]), s * (hw + 0.5), MAST_V + dv * (L1_SWIN[2] + 0.35),
                 (L1_SWIN[0] + L1_SWIN[1]) / 2, "Summon_Stone", 0.0)
    back_op = (hw - 0.6 - 2.1, hw - 0.6 + 2.1, L1_BWIN[0] - 0.2, L1_BWIN[1] + L1_BWIN[2] + 0.6, L1_BWIN[2] + 0.5)
    face_skin(stone, (hw - 0.6, v0 - 0.25), (-hw + 0.6, v0 - 0.25), z0, z1, rng, course=2.1, blk=(2.6, 4.2),
              thick=0.8, openings=[back_op])
    for s in (-1, 1):
        lbox(stone, (0.75, 0.9, L1_BWIN[1] - L1_BWIN[0]), s * (L1_BWIN[2] + 0.38), v0 - 0.5,
             (L1_BWIN[0] + L1_BWIN[1]) / 2, "Summon_Stone", 0.0)
    for su in (-1, 1):
        for vv in (v0, BUT_V):
            _buttress(stone, gold, su * hw, vv, z0, 22.2, 2.5, rng, spire=2.8,
                      edges=((-1, 1), (1, 1)) if vv > 0 else ((-1, -1), (1, -1)))
    # pele da frente do nucleo acima do timpano (atras do frontao)
    face_skin(stone, (-hw + 0.9, v1 + 0.35), (hw - 0.9, v1 + 0.35), 16.8, z1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, quoins=(False, False), base_dark=False)
    # frontispicio do portal: ombreiras, aduelas, timpano, frontao
    for s in (-1, 1):
        for k in range(6):
            zz0 = z0 + k * 1.45
            zz1 = min(zz0 + 1.45, PORT_SPRING)
            if zz1 <= zz0 + 0.1:
                continue
            m = "Stone_SumBlock" if k % 2 == 0 else "Summon_Stone"
            w = 2.3 if k % 2 == 0 else 2.0
            lbox(stone, (w, 2.9, zz1 - zz0 - 0.08), s * (PORT_HW + 1.1), 2.55, (zz0 + zz1) / 2, m, 0.14)
        # fundo do timpano (atras das aduelas)
        lbox2(stone, s * (PORT_HW + 0.35), v1, PORT_SPRING, s * 6.3, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    lbox2(stone, -PORT_HW - 0.4, v1, PORT_SPRING + PORT_HW + 0.2, PORT_HW + 0.4, 3.3, 18.2, "Summon_Stone_Dark", 0.0)
    larch(stone, 0.0, 2.6, 2 * PORT_HW, PORT_SPRING, PORT_HW, 2.9, n=9, band=1.5, keystone=True, seed=2)
    # frontao (duas aguas) com beirada de ouro grossa
    apex = (0.0, 22.6)
    for s in (-1, 1):
        a = P(s * 6.9, 3.45, 17.6)
        b = P(apex[0], 3.45, apex[1])
        stone.beam(a, b, 1.9, 1.2, "Stone_SumBlock", 0.0)
        ga = P(s * 7.2, 3.55, 18.45)
        gb = P(0.0, 3.55, apex[1] + 0.85)
        gold.beam(ga, gb, 2.2, 0.6, "Metal_Gold", 0.0)
    tri = [(-6.3, 17.6), (6.3, 17.6), (0.0, apex[1] - 0.2)]
    PK.plate(stone, tri, P(0.0, 3.0, 0.0), XU, ZZ, 1.0, "Summon_Stone_Dark")
    # --- cornija 1 (pedra + ouro grosso), com braco ate os mastros
    lbox2(stone, -hw - 1.0, v0 - 1.0, z1, hw + 1.0, 2.4, z1 + 0.6, "Summon_Stone_Dark", 0.0)
    lbox2(gold, -hw - 1.3, v0 - 1.3, z1 + 0.6, hw + 1.3, 2.6, z1 + 1.3, "Metal_Gold", 0.0)
    # --- corpo L2 (janela-estrela na frente, janelas menores nos lados e no fundo)
    hw2, w0, w1, y0, y1 = L2
    lbox2(stone, -hw2, w0, y0, hw2, w1, y1, "Summon_Stone_Dark", 0.0)
    wcs = hw2 - 0.2                      # centro da janela ao longo da pele (a pele vai de -wcs a +wcs)
    win_front = (wcs - 3.5, wcs + 3.5, y0 + 1.0, y0 + 6.8 + 3.5, 3.5)
    face_skin(stone, (-hw2 + 0.2, w1 + 0.35), (hw2 - 0.2, w1 + 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    face_skin(stone, (hw2 - 0.2, w0 - 0.35), (-hw2 + 0.2, w0 - 0.35), y0, y1, rng, course=1.8, blk=(2.2, 3.6),
              thick=0.8, openings=[win_front])
    ln_side = (w1 - 0.6) - (w0 + 0.6)
    for s in (-1, 1):
        a_uv = (s * (hw2 + 0.35), w1 - 0.6) if s > 0 else (s * (hw2 + 0.35), w0 + 0.6)
        b_uv = (s * (hw2 + 0.35), w0 + 0.6) if s > 0 else (s * (hw2 + 0.35), w1 - 0.6)
        side_win = (ln_side / 2 - 2.3, ln_side / 2 + 2.3, y0 + 2.4, y0 + 8.6, 2.3)
        face_skin(stone, a_uv, b_uv, y0, y1, rng, course=1.8, blk=(2.2, 3.6), thick=0.8, openings=[side_win])
    for su in (-1, 1):
        for vv in (w0, w1):
            _buttress(stone, gold, su * hw2, vv, y0, y1 + 1.4, 1.9, rng, spire=3.3, course=1.6)
    # janela-estrela da frente: aduelas + fundo de energia (o fundo fica no glow)
    larch(stone, 0.0, w1 + 0.4, 5.2, y0 + 6.8, 2.6, 1.3, n=7, band=0.9, keystone=True, seed=3)
    for s in (-1, 1):
        lbox2(stone, s * 2.6, w1 - 0.1, y0 + 1.4, s * 3.5, w1 + 1.05, y0 + 6.8, "Summon_Stone", 0.0)
    lbox2(gold, -3.8, w1 - 0.1, y0 + 0.85, 3.8, w1 + 1.3, y0 + 1.45, "Metal_Gold", 0.0)
    # --- cornija 2 (pedra + ouro grosso)
    lbox2(stone, -hw2 - 0.9, w0 - 0.9, y1, hw2 + 0.9, w1 + 0.9, y1 + 0.5, "Summon_Stone_Dark", 0.0)
    lbox2(gold, -hw2 - 1.2, w0 - 1.2, y1 + 0.5, hw2 + 1.2, w1 + 1.2, y1 + 1.15, "Metal_Gold", 0.0)
    # --- coroa L3 + pinaculos
    h3, c0, c1, q0, q1 = L3
    lbox2(stone, -h3, c0, q0, h3, c1, q1, "Summon_Stone_Dark", 0.0)
    for (a_uv, b_uv) in (((-h3 - 0.3, c1 + 0.3), (h3 + 0.3, c1 + 0.3)), ((h3 + 0.3, c0 - 0.3), (-h3 - 0.3, c0 - 0.3)),
                         ((h3 + 0.3, c1 + 0.3), (h3 + 0.3, c0 - 0.3)), ((-h3 - 0.3, c0 - 0.3), (-h3 - 0.3, c1 + 0.3))):
        face_skin(stone, a_uv, b_uv, q0, q1 - 0.25, rng, course=1.9, blk=(2.0, 3.2), thick=0.7, quoins=(False, False))
    # coroa: friso de ouro de 0,6 (cresce para baixo: o prato da esfera nao sobe, o anel 2 gira rente a ele)
    lbox2(gold, -h3 - 0.8, c0 - 0.8, q1 - 0.25, h3 + 0.8, c1 + 0.8, q1 + 0.35, "Metal_Gold", 0.0)
    for su in (-1, 1):
        for vv in (c0, c1):
            _buttress(stone, gold, su * h3, vv, q0, q1 + 0.9, 1.3, rng, spire=1.8, course=1.4)
    return rng


def _buttress(stone, gold, u, v, z0, z1, w, rng, spire=2.6, course=2.1, edges=()):
    """contraforte/pilar de canto em blocos alternados, capitel de ouro grosso e pinaculo dourado.
    edges: quinas (du, dv) que recebem cantoneira vertical de ouro"""
    for du, dv in edges:
        lbox(gold, (0.4, 0.4, z1 - z0 - 0.6), u + du * (w / 2 - 0.08), v + dv * (w / 2 - 0.08), (z0 + z1) / 2,
             "Metal_Gold", 0.0)
    z = z0
    k = 0
    while z < z1 - 0.05:
        h = min(course, z1 - z)
        m = "Stone_SumBlock" if k % 2 == 0 else "Summon_Stone"
        ww = w if k % 2 == 0 else w - 0.3
        lbox(stone, (ww, ww, h - 0.08), u, v, z + h / 2, m, 0.14)
        z += h
        k += 1
    lbox(gold, (w + 0.5, w + 0.5, 0.55), u, v, z1 + 0.27, "Metal_Gold", 0.0)
    lbox(gold, (w * 0.72, w * 0.72, 0.45), u, v, z1 + 0.77, "Metal_Gold", 0.0)
    a = P(u, v, z1 + 0.99)
    K.spike(gold, a, a + Vector((0, 0, spire)), w * 0.36, "Metal_Gold", 4)


# ------------------------------------------------------------------ torre: ouro, estrelas, energia
def tower_details(stone, gold, glow):
    hw, v0, v1, z0, z1 = L1
    # energia do portal (fundo do nicho) + estrela de cristal + faiscas + circulo de invocacao no patamar
    pts = K.arch_poly(PORT_HW - 0.05, LAND_Z - 0.05, PORT_SPRING, 14)
    PK.plate(glow, pts, P(0.0, PV + 0.08, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, PV + 0.75, 9.4), XU, ZZ, 5, 2.7, 1.12, 0.55, "Crystal_SumStar_Glow", edge=0.3)
    rng = random.Random(631)
    for k in range(9):
        uu = rng.uniform(-3.0, 3.0)
        zz = rng.uniform(LAND_Z + 1.2, PORT_SPRING + 2.6)
        if abs(uu) < 2.9 and 6.4 < zz < 12.4:
            continue
        K.star(glow, P(uu, PV + 0.35, zz), XU, ZZ, 4, rng.uniform(0.6, 0.85), 0.22, 0.25, "Crystal_SumStar_Glow")
    cc = (PV + LAND_V[1]) / 2 - 0.6                   # centro do circulo de invocacao (diante do portal)
    for r in (2.3, 1.25):
        PK.ring(glow, P(0.0, cc, LAND_Z), r, XU, YV, 0.4, 0.3, "Summon_Blue_Glow", 0, 360, 24)
    # cristais pequenos dos lados da boca do nicho (fora do eixo do jogador e da camera)
    cr = MB("SUM_Crystals", "05_SUMMON", random.Random(632), detail="hero")
    for s in (-1, 1):
        K.gem_cluster(cr, P(s * 4.3, 4.9, LAND_Z), 0.42, "Crystal_Blue", random.Random(640 + s))
    # arquivolta de ouro + chave com estrela
    PK.ring(gold, P(0.0, 4.1, PORT_SPRING), PORT_HW + 0.15, XU, ZZ, 0.4, 0.4, "Metal_Gold", 0, 180, 16)
    PK.ring(gold, P(0.0, 4.1, PORT_SPRING), PORT_HW + 1.62, XU, ZZ, 0.4, 0.4, "Metal_Gold", 0, 180, 18)
    for s in (-1, 1):
        lbox(gold, (0.4, 0.4, PORT_SPRING - LAND_Z), s * (PORT_HW + 0.15), 4.1, (LAND_Z + PORT_SPRING) / 2,
             "Metal_Gold", 0.0)
        lbox(gold, (2.8, 3.3, 0.6), s * (PORT_HW + 1.1), 2.55, PORT_SPRING + 0.2, "Metal_Gold", 0.0)
        lbox(gold, (2.8, 3.3, 0.6), s * (PORT_HW + 1.1), 2.55, POD_TOP + 0.3, "Metal_Gold", 0.0)
    # estrela de ouro com miolo azul no frontao (e a do fecho do arco)
    K.star(gold, P(0.0, 4.0, 19.6), XU, ZZ, 4, 2.6, 0.72, 0.55, "Metal_Gold", edge=0.35)
    K.star(glow, P(0.0, 4.45, 19.6), XU, ZZ, 4, 1.05, 0.34, 0.38, "Summon_Blue_Glow", edge=0.2)
    # estrelas de 4 pontas nos contrafortes (frente) e nos lados do corpo L1
    for s in (-1, 1):
        gold_star4(gold, s * hw, BUT_V + 1.25, 8.0, 0.8, "v+")
    # janelas altas dos lados do L1 (energia + estrelinha + arco e ombreiras de ouro)
    zs0, zsp, shw = L1_SWIN
    for s in (-1, 1):
        sp = K.arch_poly(shw, zs0, zsp, 8)
        PK.plate(glow, sp, P(s * (hw + 0.1), MAST_V, 0.0), YV, ZZ, 0.2, "Crystal_SumPortal_Glow")
        K.star(glow, P(s * (hw + 0.45), MAST_V, zsp - 0.6), YV, ZZ, 4, 0.95, 0.26, 0.28, "Crystal_SumStar_Glow",
               edge=0.2)
        PK.ring(gold, P(s * (hw + 0.95), MAST_V, zsp), shw + 0.25, YV, ZZ, 0.35, 0.35, "Metal_Gold", 0, 180, 10)
        lbox(gold, (0.45, 2 * shw + 1.2, 0.4), s * (hw + 0.8), MAST_V, zs0 - 0.15, "Metal_Gold", 0.0)
    # janela gotica do fundo do L1 (arco apontado) + estrela de ouro com miolo azul por cima
    zb0, zbs, bhw = L1_BWIN
    gp = [(-bhw, zb0), (bhw, zb0), (bhw, zbs)]
    for i in range(1, 6):
        t = i / 6.0
        a = math.radians(60.0 * t)
        gp.append((bhw - 2 * bhw * (1 - math.cos(a)), zbs + 2 * bhw * math.sin(a)))
    gp.append((0.0, zbs + 2 * bhw * math.sin(math.radians(60.0))))
    for i in range(5, 0, -1):
        t = i / 6.0
        a = math.radians(60.0 * t)
        gp.append((-(bhw - 2 * bhw * (1 - math.cos(a))), zbs + 2 * bhw * math.sin(a)))
    gp.append((-bhw, zbs))
    PK.plate(glow, gp, P(0.0, v0 - 0.12, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, v0 - 0.5, zbs - 1.2), XU, ZZ, 4, 1.25, 0.32, 0.3, "Crystal_SumStar_Glow", edge=0.2)
    gtop = zbs + 2 * bhw * math.sin(math.radians(60.0))
    for s in (-1, 1):
        lbox(gold, (0.4, 0.4, zbs - zb0), s * (bhw + 0.15), v0 - 1.0, (zb0 + zbs) / 2, "Metal_Gold", 0.0)
        gold.beam(P(s * (bhw + 0.15), v0 - 1.0, zbs), P(0.0, v0 - 1.0, gtop + 0.3), 0.4, 0.4, "Metal_Gold", 0.0)
    lbox(gold, (2 * bhw + 1.6, 1.1, 0.45), 0.0, v0 - 0.6, zb0 - 0.2, "Metal_Gold", 0.0)
    gold_star4(gold, 0.0, v0 - 0.65, 18.9, 1.05, "v-")
    K.star(glow, P(0.0, v0 - 1.05, 18.9), XU, ZZ, 4, 0.55, 0.18, 0.25, "Summon_Blue_Glow", edge=0.2)
    # --- janela-estrela (L2 frente) + janelas menores
    hw2, w0, w1, y0, y1 = L2
    pts = K.arch_poly(2.6, y0 + 1.4, y0 + 6.8, 10)
    PK.plate(glow, pts, P(0.0, w1 + 0.12, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, w1 + 0.7, y0 + 5.6), XU, ZZ, 5, 2.15, 0.9, 0.45, "Crystal_SumStar_Glow", edge=0.25)
    PK.plate(glow, pts, P(0.0, w0 - 0.12, 0.0), XU, ZZ, 0.2, "Crystal_SumPortal_Glow")
    K.star(glow, P(0.0, w0 - 0.6, y0 + 5.6), XU, ZZ, 5, 1.7, 0.72, 0.4, "Crystal_SumStar_Glow", edge=0.2)
    vs = (w0 + w1) / 2
    for s in (-1, 1):
        sp = K.arch_poly(2.1, y0 + 2.4, y0 + 6.5, 8)
        PK.plate(glow, sp, P(s * (hw2 + 0.12), vs, 0.0), YV, ZZ, 0.2, "Crystal_SumPortal_Glow")
        K.star(glow, P(s * (hw2 + 0.55), vs, y0 + 5.4), YV, ZZ, 4, 1.35, 0.36, 0.35, "Crystal_SumStar_Glow", edge=0.2)
        PK.ring(gold, P(s * (hw2 + 0.95), vs, y0 + 6.5), 2.35, YV, ZZ, 0.35, 0.35, "Metal_Gold", 0, 180, 12)
    PK.ring(gold, P(0.0, w1 + 1.15, y0 + 6.8), 2.75, XU, ZZ, 0.35, 0.35, "Metal_Gold", 0, 180, 14)
    PK.ring(gold, P(0.0, w0 - 1.15, y0 + 6.8), 2.75, XU, ZZ, 0.35, 0.35, "Metal_Gold", 0, 180, 14)
    # estrela de 4 pontas sobre a janela (cornija 2)
    K.star(gold, P(0.0, w1 + 1.4, y1 + 0.3), XU, ZZ, 4, 1.8, 0.5, 0.45, "Metal_Gold", edge=0.3)
    K.star(glow, P(0.0, w1 + 1.75, y1 + 0.3), XU, ZZ, 4, 0.75, 0.25, 0.3, "Summon_Blue_Glow", edge=0.2)
    # --- coroa: emblema da frente + prato de ouro da esfera
    h3, c0, c1, q0, q1 = L3
    K.star(gold, P(0.0, c1 + 0.55, (q0 + q1) / 2 - 0.2), XU, ZZ, 4, 1.7, 0.46, 0.4, "Metal_Gold", edge=0.25)
    K.star(glow, P(0.0, c1 + 0.85, (q0 + q1) / 2 - 0.2), XU, ZZ, 4, 0.65, 0.2, 0.28, "Summon_Blue_Glow", edge=0.2)
    gold.cyl(4.7, 0.45, P(0.0, AX, q1 + 0.35 + 0.22), RT(), "Metal_Gold", 16, r2=4.1, bevel=0.0)
    PK.ring(gold, P(0.0, AX, q1 + 1.15), 4.0, XU, YV, 0.45, 0.5, "Metal_Gold", 0, 360, 24)
    return cr


# ------------------------------------------------------------------ mastros, estandartes, pedestais, lanternas
def out_pedestal(stone, gold, u, v):
    """pedestal externo 4 x 4 x 5 (sobre o soco, nas quinas): base escura, faixa de ouro, 3 fiadas alternadas,
    cantoneiras e capitel de ouro, estrelas nas faces de fora. Devolve a cota do topo (relativa a T1)."""
    side, hgt = OUT_PED[3], OUT_PED[4]
    z = PLZ
    lbox(stone, (side + 0.6, side + 0.6, 0.5), u, v, z + 0.25, "Summon_Stone_Dark", 0.0)
    lbox(gold, (side + 0.35, side + 0.35, 0.4), u, v, z + 0.7, "Metal_Gold", 0.0)
    zb, zt = z + 0.9, z + hgt - 0.55
    hs = (zt - zb) / 3.0
    for k in range(3):
        ww = side if k % 2 == 0 else side - 0.3
        lbox(stone, (ww, ww, hs - 0.08), u, v, zb + hs * (k + 0.5), "Stone_SumBlock" if k != 1 else "Summon_Stone",
             0.2)
    for du in (-1, 1):
        for dv in (-1, 1):
            lbox(gold, (0.45, 0.45, zt - zb), u + du * (side / 2 - 0.12), v + dv * (side / 2 - 0.12), (zb + zt) / 2,
                 "Metal_Gold", 0.0)
    lbox(gold, (side + 0.5, side + 0.5, 0.55), u, v, zt + 0.275, "Metal_Gold", 0.0)
    su = 1 if u > 0 else -1
    sv = 1 if v > 0 else -1
    zm = (zb + zt) / 2
    gold_star4(gold, u + su * side / 2, v, zm, 1.05, "u+" if su > 0 else "u-")
    gold_star4(gold, u, v + sv * side / 2, zm, 1.05, "v+" if sv > 0 else "v-")
    return z + hgt


def in_pedestal(stone, gold, u, v):
    """pedestal interno 3 x 3 x 3 dos cristais grandes (sobre o podio) + bacia. Devolve a cota da bacia."""
    side, hgt = IN_PED[2], IN_PED[3]
    z = POD_TOP
    lbox(stone, (side + 0.4, side + 0.4, 0.45), u, v, z + 0.225, "Summon_Stone_Dark", 0.0)
    lbox(stone, (side, side, hgt - 1.0), u, v, z + 0.45 + (hgt - 1.0) / 2, "Stone_SumBlock", 0.0)
    lbox(gold, (side + 0.4, side + 0.4, 0.55), u, v, z + hgt - 0.275, "Metal_Gold", 0.0)
    gold_star4(gold, u, v + side / 2, z + 0.45 + (hgt - 1.0) / 2, 0.85, "v+")
    stone.cyl(1.4, 0.5, P(u, v, z + hgt + 0.25), RT(), "Summon_Stone_Dark", 8, r2=1.8, bevel=0.0)
    return z + hgt + 0.5


def masts_and_lanterns(stone, gold, glow):
    rng = random.Random(651)
    bn = MB("SUM_Banners", "05_SUMMON", rng, detail="near")
    hw, v0, v1, z0, z1 = L1
    hw2, w0, w1, y0, y1 = L2
    z_pole = 29.8
    for s in (-1, 1):
        u = s * MAST_U
        # mastro em blocos + asa de ligacao com o corpo L1 + braco na cornija
        _buttress(stone, gold, u, MAST_V, POD_TOP, 31.0, 2.0, rng, spire=3.0, course=2.0,
                  edges=((s, 1), (s, -1)))
        for zc in (13.0, 22.5):
            lbox(gold, (2.4, 2.4, 0.5), u, MAST_V, zc, "Metal_Gold", 0.0)
        lbox2(stone, s * (hw - 0.1), MAST_V - 0.95, POD_TOP, s * (MAST_U - 0.9), MAST_V + 0.95, 12.0,
              "Summon_Stone", 0.0)
        lbox2(gold, s * (hw - 0.1), MAST_V - 1.15, 12.0, s * (MAST_U - 0.7), MAST_V + 1.15, 12.5, "Metal_Gold", 0.0)
        gold_star4(gold, s * ((hw + MAST_U) / 2 - 0.4), MAST_V + 0.95, 8.0, 0.75, "v+")
        gold_star4(gold, s * ((hw + MAST_U) / 2 - 0.4), MAST_V - 0.95, 8.0, 0.75, "v-")
        lbox2(stone, s * (hw + 0.8), MAST_V - 0.8, z1, s * (MAST_U - 0.9), MAST_V + 0.8, z1 + 0.9, "Summon_Stone_Dark",
              0.0)
        # haste horizontal girada 35 graus para a frente (referencial Fb no eixo do mastro): sai da parede do L2,
        # atravessa o mastro e leva o estandarte, que assim le de frente, dos lados e de tras
        mw = P(u, MAST_V, 0.0)
        Fb = Frame(mw.x, mw.y, Z0, YAW + s * BAN_TH)
        ub = Vector(Fb.p(1, 0, 0)) - Vector(Fb.p(0, 0, 0))
        stub = (MAST_U - (hw2 + 0.35)) / math.cos(BAN_TH)
        a = Fb.p(-s * stub, 0.0, z_pole)
        b = Fb.p(s * 7.0, 0.0, z_pole)
        bn.rod(a, b, 0.3, "Wood_Dark", 8)
        K.spike(gold, b, b + ub * (s * 1.5), 0.45, "Metal_Gold", 4)
        gold.ico(0.5, Fb.p(s * 6.8, 0.0, z_pole), "Metal_Gold", 1)
        for uu in (-s * (stub - 0.25), s * 1.3, s * 5.9):
            gold.box((0.4, 0.8, 0.8), Fb.p(uu, 0.0, z_pole), Fb.r(), "Metal_Gold", 0.0)
        K.banner(bn, gold, bn, Fb, 1.5 if s > 0 else -5.7, 5.7 if s > 0 else -1.5, 0.0, z_pole - 0.5, 12.6, tip=1.6)
        # lanterna pendurada na haste, entre o corpo e o mastro
        K.hang_lantern(stone, glow, gold, Fb.p(-s * 2.4, 0.0, z_pole - 0.3), 1.0, drop=0.9)
        # lanternas penduradas nos cantos da frente do L2 (bracos de ouro)
        br0 = P(s * (hw2 + 0.95), w1, 29.6)
        br1 = P(s * (hw2 + 2.3), w1 + 0.4, 29.6)
        gold.beam(br0, br1, 0.35, 0.35, "Metal_Gold", 0.0)
        gold.beam(P(s * (hw2 + 0.95), w1, 28.2), br1 - ZZ * 0.1, 0.3, 0.3, "Metal_Gold", 0.0)
        K.hang_lantern(stone, glow, gold, br1, 0.85, drop=0.55)
    bn.finish()
    # 4 pedestais externos 4x4x5 nas quinas do soco, com lanterna japonesa de 4 de altura (frente primeiro)
    ou, ovf, ovb = OUT_PED[0], OUT_PED[1], OUT_PED[2]
    corners = [(s * ou, ovf) for s in (-1, 1)] + [(s * ou, ovb) for s in (-1, 1)]
    lamp_c = []
    sh = (LANT_H - 1.38) / 4.1
    for (u, v) in corners:
        ztop = out_pedestal(stone, gold, u, v)
        lamp_c.append(K.corner_lantern(stone, glow, gold, F, u, v, ztop, 1.0, sh))
    # 2 pedestais internos 3x3x3 dos cristais grandes (sobre o podio, dos dois lados do patamar)
    for s in (-1, 1):
        in_pedestal(stone, gold, s * IN_PED[0], IN_PED[1])
    # postes com lanterninha no pe da escada (fora do patamar)
    for s in (-1, 1):
        u, v = s * (CORR + 0.65), ST_FOOT - 0.8
        zp = ZL1 - 0.05                          # assenta no mosaico da praca
        lbox(stone, (1.5, 1.5, 0.45), u, v, zp + 0.225, "Summon_Stone_Dark", 0.0)
        lbox(stone, (1.1, 1.1, 2.9), u, v, zp + 0.45 + 1.45, "Stone_SumBlock", 0.0)
        lbox(gold, (1.5, 1.5, 0.4), u, v, zp + 3.55, "Metal_Gold", 0.0)
        lbox(glow, (0.85, 0.85, 0.85), u, v, zp + 4.2, "Lantern_Glow", 0.0)
        for du in (-1, 1):
            for dv in (-1, 1):
                lbox(gold, (0.3, 0.3, 1.1), u + du * 0.45, v + dv * 0.45, zp + 4.27, "Metal_Gold", 0.0)
        gold.cyl(0.95, 0.6, P(u, v, zp + 4.8 + 0.3), RT(0, 0, math.pi / 4), "Metal_Gold", 4, r2=0.3, bevel=0.0)
    return lamp_c


def crystals_big(cr):
    for s in (-1, 1):
        u, v = s * IN_PED[0], IN_PED[1]
        base = P(u, v, POD_TOP + IN_PED[3] + 0.45)
        K.gem_cluster(cr, base, 1.3, "Crystal_Blue", random.Random(660 + s))
    cr.finish()


# ------------------------------------------------------------------ esfera armilar, estrela, constelacao
def sphere(gold, glow):
    c = P(0.0, AX, ZS)
    fr = MB("SUM_Sphere_Frame", "05_SUMMON", random.Random(671), detail="hero")
    # gaiola fixa: 2 meridianos + equador
    PK.ring(fr, c, CAGE_R, XU, ZZ, 0.62, 0.7, "Metal_Gold", 0, 360, 44)
    PK.ring(fr, c, CAGE_R, YV, ZZ, 0.62, 0.7, "Metal_Gold", 0, 360, 44)
    PK.ring(fr, c, CAGE_R, XU, YV, 0.55, 0.65, "Metal_Gold", 0, 360, 44)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        d = XU * math.cos(a) + YV * math.sin(a)
        K.star(fr, c + d * CAGE_R, d.cross(ZZ), ZZ, 4, 0.8, 0.24, 0.3, "Metal_Gold", edge=0.2)
    # remate: bola, haste, estrela de 4 pontas com gema azul, ponta
    top = c + ZZ * CAGE_R
    fr.ico(0.65, top + ZZ * 0.5, "Metal_Gold", 1)
    fr.rod(top + ZZ * 0.4, top + ZZ * 3.7, 0.24, "Metal_Gold", 6)
    sc = top + ZZ * 2.1
    K.star(fr, sc, XU, ZZ, 4, 1.75, 0.45, 0.42, "Metal_Gold", edge=0.3)
    K.star(fr, sc, YV, ZZ, 4, 1.2, 0.35, 0.35, "Metal_Gold", edge=0.2)
    K.star(fr, sc, XU, ZZ, 4, 0.7, 0.26, 0.62, "Summon_Blue_Glow", edge=0.2)
    K.spike(fr, top + ZZ * 3.7, top + ZZ * 4.9, 0.3, "Metal_Gold", 4)
    fr.finish()
    # pecas moveis (VFX): 3 aneis + estrela
    specs = [
        # nome, raio, secao (w, h), eixo do plano (inclinacao), inclinacao graus, eixo de giro, rpm, enfeites
        ("VFX_SUM_Ring_1", 11.4, (0.95, 0.75), XU, 16.0, "z", 2.0, 10),
        ("VFX_SUM_Ring_2", 8.3, (0.72, 0.7), None, 90.0, "-z", 4.0, 4),
        ("VFX_SUM_Ring_3", 7.35, (0.66, 0.65), (XU * math.cos(math.radians(120)) + YV * math.sin(math.radians(120))),
         58.0, "normal", 6.0, 4),
    ]
    rings = []
    for name, rr, (w, h), tilt_ax, tilt, spin, rpm, nst in specs:
        mb = MB(name, "12_VFX_HELPERS", random.Random(len(name) * 13), detail="hero")
        if tilt_ax is None:
            ang = math.radians(30.0)
            u = XU * math.cos(ang) + YV * math.sin(ang)
            v = ZZ.copy()
        else:
            ta = Vector(tilt_ax).normalized()
            other = ZZ.cross(ta).normalized()           # horizontal, perpendicular ao eixo de inclinacao
            u = ta
            v = (other * math.cos(math.radians(tilt)) + ZZ * math.sin(math.radians(tilt))).normalized()
        nrm = u.cross(v).normalized()
        PK.ring(mb, c, rr, u, v, w, h, "Metal_Gold", 0, 360, 56 if rr > 10 else 44)
        for k in range(nst):
            a = 2 * math.pi * (k + 0.5) / nst
            d = u * math.cos(a) + v * math.sin(a)
            tng = (-u * math.sin(a) + v * math.cos(a)).normalized()
            # enfeite centrado na faixa do anel: nao sai da casca radial do anel (os aneis giram um dentro do
            # outro e dentro da gaiola; folga radial >= 0,15 entre cascas)
            p = c + d * rr
            K.star(mb, p, tng, nrm, 5, 0.85, 0.36, 0.22, "Summon_Star_Glow", edge=0.2)
        ob = mb.finish()
        axis = (0.0, 0.0, 1.0) if spin == "z" else ((0.0, 0.0, -1.0) if spin == "-z" else tuple(round(x, 4) for x in nrm))
        ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
        ob["axis"] = [round(x, 4) for x in axis]
        ob["rpm"] = rpm
        ob["vfx"] = "anel da esfera armilar (gira no eixo 'axis' passando por 'pivot')"
        rings.append(ob)
    # estrela de cristal: facetas alternadas ambar / amarelo (2 Neon). Sem o contorno de ouro de antes: a estrela das
    # refs e so cristal, e o contorno era 1 MeshPart a mais na conta dos VFX (ja no teto)
    st = MB("VFX_SUM_Star", "12_VFX_HELPERS", random.Random(691), detail="hero")
    K.star_duo(st, c, XU, ZZ, 5, 6.6, 2.8, 1.7, "Crystal_SumAmber_Glow", "Crystal_SumYellow_Glow", edge=0.9)
    ob = st.finish()
    ob["pivot"] = [round(c.x, 3), round(c.y, 3), round(c.z, 3)]
    ob["axis"] = [0.0, 0.0, 1.0]
    ob["rpm"] = 5.0
    ob["vfx"] = "estrela de cristal (2 Neon alternados por faceta) girando devagar no eixo vertical"
    return c


# constelacao (rodada 2): 2 ASAS, uma de cada lado da esfera, no plano da fachada girado -35 graus em torno do eixo
# (azimutes no referencial da torre, medidos a partir de +u como no resto do modulo: asa direita -35+-25, asa
# esquerda 145+-25). O giro abre as asas de frente para o sul (entrada, anel, vistas gerais das refs 14/15/18); a
# cadeia de tras saiu. Cada estrela: (desvio de azimute, raio a partir do eixo, dz a partir do centro da esfera, raio
# da estrela). Raio 20-28, dz -2..+10, estrelas de 2,8 a 3,8, linhas de 0,4.
WING_AZ = (-35.0, 145.0)
WING = [(18.0, 20.5, 6.5, 3.0), (6.0, 25.0, 10.0, 3.6), (-10.0, 28.0, 4.5, 2.8), (12.0, 25.5, -2.0, 3.8),
        (-22.0, 21.0, 1.0, 3.2)]
WING_LINKS = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]


def constellation(c):
    rng = random.Random(701)
    mb = MB("SUM_Constellation", "05_SUMMON", rng, detail="hero")
    for w, base in enumerate(WING_AZ):
        pts = []
        face = math.radians(base) + YAW          # rumo (mundo) da asa: as estrelas ficam de frente para a normal
        for k, (da, r, dz, sz) in enumerate(WING):
            # a asa esquerda e o espelho da direita pelo eixo, com a altura trocada em 2 estrelas (nao fica simetrica)
            if w == 1 and k in (1, 3):
                dz = WING[3 if k == 1 else 1][2]
            a = math.radians(base + (da if w == 0 else -da))
            d = XU * math.cos(a) + YV * math.sin(a)
            p = c + d * r + ZZ * dz
            pts.append((p, sz))
            K.const_star(mb, p, sz, "Summon_Blue_Glow", "Crystal_SumStar_Glow", rot=face)
        for i, j in WING_LINKS:
            (a, sa), (b, sb) = pts[i], pts[j]
            dd = b - a
            e = dd.normalized()
            a2, b2 = a + e * sa * 0.55, b - e * sb * 0.55
            mb.beam(a2, b2, 0.4, 0.4, "Summon_Blue_Glow", 0.0)
            # brilhos miudos ao longo da linha
            for t in (0.5,):
                q = a2 + (b2 - a2) * t
                PK.octa(mb, q, 0.55, 0.7, "Crystal_SumStar_Glow", rot=face + math.pi / 4)
    mb.finish()


# ------------------------------------------------------------------ colisao da torre
def tower_collision():
    pu, pv0, pv1 = PLINTH
    for s in (-1, 1):
        lcol2(s * CORR, pv0 - 0.65, -0.6, s * (pu + 0.65), pv1 + 0.65, PLZ)                  # soco (lados)
        lcol2(s * CORR, POD[1] - 0.45, PLZ, s * (POD[0] + 0.45), POD[2] + 0.45, POD_TOP)    # podio (lados)
    lcol2(-CORR, pv0 - 0.65, -0.6, CORR, LAND_V[0], POD_TOP)             # soco + podio (fundo)
    lcol2(-CORR, LAND_V[0], -0.2, CORR, LAND_V[1], LAND_Z)               # patamar do portal (7 de fundo)
    hw, v0, v1, z0, z1 = L1
    lcol2(-hw - 1.3, v0 - 1.3, POD_TOP, hw + 1.3, PV, L3[4])              # corpo atras do nicho (plano do portal)
    lcol2(-hw - 1.3, PV, PORT_SPRING + PORT_HW, hw + 1.3, v1 + 0.1, L3[4])   # sobre o nicho (L1 + L2 + coroa)
    lcol2(-PORT_HW, v1 + 0.1, PORT_SPRING + PORT_HW, PORT_HW, 4.3, 18.2)  # timpano (frente, sobre o arco)
    for s in (-1, 1):
        lcol2(s * PORT_HW, PV, POD_TOP, s * (hw + 1.3), 4.3, 18.2)        # paredes do nicho + ombreiras
        lcol2(s * (hw - 0.1), MAST_V - 1.1, POD_TOP, s * (MAST_U + 1.0), MAST_V + 1.1, 31.0)   # asa + mastro
        ih = IN_PED[3] + 0.5
        lcol((IN_PED[2] + 0.4, IN_PED[2] + 0.4, ih), s * IN_PED[0], IN_PED[1], POD_TOP + ih / 2)   # pedestal interno
        lcol((1.5, 1.5, 5.7), s * (CORR + 0.65), ST_FOOT - 0.8, 2.85)        # poste do pe da escada
        oh = OUT_PED[4] + LANT_H
        for v in (OUT_PED[1], OUT_PED[2]):
            lcol((OUT_PED[3] + 0.6, OUT_PED[3] + 0.6, oh), s * OUT_PED[0], v, PLZ + oh / 2)   # pedestal + lanterna


# ------------------------------------------------------------------ build
def build():
    plaza_floor()
    plaza_rail()
    stone = MB("SUM_Tower_Stone", "05_SUMMON", random.Random(620), detail="near")
    gold = MB("SUM_Tower_Gold", "05_SUMMON", random.Random(622), detail="near")
    glow = MB("SUM_Tower_Glow", "05_SUMMON", random.Random(623), detail="hero")
    tower_stone(stone, gold, glow)
    cr = tower_details(stone, gold, glow)
    lamp_c = masts_and_lanterns(stone, gold, glow)
    crystals_big(cr)
    c = sphere(gold, glow)
    constellation(c)
    stone.finish()
    gold.finish()
    glow.finish()
    tower_collision()
    # luzes (4): estrela (quente), portal (fria), 2 lanternas de canto da frente (quentes)
    light("L_Summon_Star", "POINT", c, 9000, (1.0, 0.74, 0.34), 3.0)
    light("L_Summon_Portal", "POINT", P(0.0, PV + 3.0, 9.0), 1800, (0.36, 0.52, 1.0), 1.2)
    for n, p in zip(("L_Summon_Lantern_L", "L_Summon_Lantern_R"), lamp_c[:2]):
        light(n, "POINT", p, 320, (1.0, 0.62, 0.28), 0.4)
    # marcadores de gameplay (rodada 2: a interacao e no PATAMAR, diante do portal, onde o jogador para)
    mk("SUMMON_Main", P(0.0, 0.0, 0.0), (0, 0, YAW), 4.0, "ARROWS",
       props={"face_deg": L.SUMMON_FACE_DEG, "star_pivot": [round(c.x, 3), round(c.y, 3), round(c.z, 3)],
              "height": round(ZS + CAGE_R + 4.9, 1), "free_zone_v": list(FREE_V), "free_zone_w": 14.0,
              "note": "raiz da torre de invocacao (+Y local = frente); zona livre na frente: v local em free_zone_v"})
    mk("SUMMON_Interact", P(0.0, PV + 1.9, LAND_Z + 0.12), (0, 0, YAW), 2.0, "SPHERE",
       props={"radius": 6.0, "portal_plane_v": PV,
              "note": "patamar do portal, 1,9 a frente do plano da energia (ProximityPrompt da invocacao)"})
    cam = P(0.0, PLAYER_V + 10.5, LAND_Z + 5.5)
    look = P(0.0, PV, LAND_Z + 5.5)
    mk("SUMMON_PlayerPosition", P(0.0, PLAYER_V, LAND_Z + 0.12), (0, 0, YAW + math.pi), 2.0, "ARROWS",
       props={"camera_pos": [round(cam.x, 2), round(cam.y, 2), round(cam.z, 2)],
              "camera_look": [round(look.x, 2), round(look.y, 2), round(look.z, 2)],
              "note": "jogador no patamar olhando o portal; camera da animacao atras dele, sobre a escada (livre)"})
