# sg_village_int - INTERIORES das 7 casas da vila (onda 1, agente 1e, 2026-09-30). Pedido do usuario: "modele as
# casas por dentro para deixar elas funcionais e acessiveis".
# Chamado pelo sg_village.build() depois do exterior de cada casa (o exterior devolve as janelas, a lareira/chamine e
# o telhado). Tudo em coordenadas REAIS do lote (sg_village.lot_frame: +Y = frente, porta no meio da frente), menos o
# forro do telhado e as tesouras, que usam o referencial do kit (sg_village.KitXF) para casar com a ardosia.
#   - FORRO DE PAREDE (reboco, 0,5) no objeto do EXTERIOR (nao some de longe): a parede de 1 da colisao = casca + forro;
#     vaos da porta e das janelas iguais aos da casca; de dentro cada janela mostra POSTIGOS FECHADOS navy recuados
#     0,24 (a luz acesa de fora fica 0,40 atras deles: nada coplanar), com guarnicao e peitoril de madeira.
#   - INTERIOR (objeto SG_Vil_Int_<casa>, o cliente esconde a mais de 90): piso de tabuas (A/C) ou lajes (taverna) com
#     o topo a 0,30 (= rua), rodape, vigamento do teto, lareira de pedra acesa (brasa Neon contida), escada reta de
#     madeira com corrimao e balaustres (a da onda 0: 6 de largura ao longo do fundo), guarda-corpo do vao, moveis.
#   - COLISAO (a da onda 0, refeita aqui porque o blockout da vila sai): paredes com o vao da porta, piso interno,
#     laje do andar, escada (sg_col.stair_col), guarda, lareira, mesa/balcao/cama/bancada, forro. + soco e peitos de
#     chamine.
#   - LUZ: as 4 luzes reais da onda 0 (L_SGVil_House_H1/H2/H5/H7) passam para a frente da lareira; as outras casas/
#     andares ganham luz SO de previa (AREA, PREVIEW_L_SGVil_*: o export so leva POINT/SPOT) no lugar dos marcadores
#     propostos no relatorio (1 por andar, quente).
import math, random
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, Frame, light, fm_lib
import sg_layout as L
import sg_col
import sg_village as V

WOOD, M_JNT, M_DRESS = V.WOOD, V.M_JNT, V.M_DRESS
M_ROOM, M_CLOTH = V.M_ROOM, V.M_CURT
# PALETA DO INTERIOR (5 materiais por casa = 5 MeshParts): madeira, pedra clara (linho, cera, lajes), pedra escura
# (ferro, fuligem, leito), tecido navy (tapete, coberta, postigos, livros) e a brasa. O forro de parede (reboco) fica
# no objeto do exterior.
M_PL = M_DRESS          # linho / cera / papel
M_CAP = M_DRESS
M_SHUT = M_CLOTH        # postigos por dentro (navy)
IRON = M_JNT            # ferragens
FLOOR = 0.30                 # topo do piso interno (= topo da rua e do caminho)
WALL = 1.0                   # casca 0,5 + forro 0,5 (colisao da onda 0)
B = 0.05                     # chanfro dos moveis
REAL_LIGHT = ("H1", "H2", "H5", "H7")


# ------------------------------------------------------------------ primitivas no referencial do lote (reais)
def tb(mb, F, cx, cy, z0, sx, sy, sz, m, bevel=B, yaw=0.0):
    """caixa pela BASE (z0) no lote"""
    mb.box((sx, sy, sz), F.p(cx, cy, z0 + sz / 2), F.r(0, 0, yaw), m, bevel)


def bm_(mb, F, a, b, w, h, m=WOOD):
    mb.beam(F.p(*a), F.p(*b), w, h, m, 0.0)


def rod(mb, F, a, b, r, m=IRON, n=6):
    mb.rod(F.p(*a), F.p(*b), r, m, n)


def lcol(area, F, cx, cy, z0, sx, sy, sz, yaw=0.0):
    col_box(area, (sx, sy, sz), F.p(cx, cy, z0 + sz / 2), F.r(0, 0, yaw))


def rot2(u, v, a):
    return (u * math.cos(a) - v * math.sin(a), u * math.sin(a) + v * math.cos(a))


class Sub:
    """sub-referencial dentro do lote (moveis girados): p(u, v) -> (x, y) do lote"""

    def __init__(self, cx, cy, yaw):
        self.cx, self.cy, self.a = cx, cy, yaw

    def xy(self, u, v):
        du, dv = rot2(u, v, self.a)
        return (self.cx + du, self.cy + dv)


def sbox(mb, F, S, u, v, z0, sx, sy, sz, m, bevel=B):
    x, y = S.xy(u, v)
    tb(mb, F, x, y, z0, sx, sy, sz, m, bevel, S.a)


# ------------------------------------------------------------------ moveis (Tier B: base, corpo, remate)
def table(mb, F, cx, cy, lx, ly, h=3.4, yaw=0.0):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR + h - 0.32, lx, ly, 0.32, WOOD, 0.08)               # tampo
    for k in (-1, 1):
        sbox(mb, F, S, 0, k * (ly / 2 - 0.45), FLOOR + h - 0.8, lx - 1.0, 0.2, 0.48, WOOD, 0.0)    # saia
    for ku in (-1, 1):
        for kv in (-1, 1):
            u, v = ku * (lx / 2 - 0.55), kv * (ly / 2 - 0.55)
            sbox(mb, F, S, u, v, FLOOR, 0.5, 0.5, h - 0.32, WOOD, 0.0)              # perna
    sbox(mb, F, S, 0, 0, FLOOR + 0.7, lx - 1.1, 0.24, 0.24, WOOD, 0.0)              # travessa


def chair(mb, F, cx, cy, yaw, back=True):
    """cadeira: assento 1,8 a 2,1 do chao, 4 pernas, encosto com 2 montantes e 2 travessas (yaw = para onde olha)"""
    S = Sub(cx, cy, yaw)
    zs = FLOOR + 1.95
    sbox(mb, F, S, 0, 0, zs, 1.8, 1.8, 0.22, WOOD, 0.06)
    for ku in (-1, 1):
        for kv in (-1, 1):
            sbox(mb, F, S, ku * 0.7, kv * 0.7, FLOOR, 0.26, 0.26, 1.95, WOOD, 0.0)
    if back:
        for ku in (-1, 1):
            sbox(mb, F, S, ku * 0.7, -0.78, zs, 0.26, 0.26, 2.3, WOOD, 0.0)
        sbox(mb, F, S, 0, -0.8, zs + 1.6, 1.6, 0.18, 0.62, WOOD, 0.03)


def stool(mb, F, cx, cy):
    p = F.p(cx, cy, FLOOR)
    mb.cyl(0.85, 0.24, (p.x, p.y, p.z + 2.0), m=WOOD, n=6, bevel=0.05)
    for k in range(3):
        a = 2 * math.pi * k / 3 + 0.3
        mb.beam((p.x + 0.55 * math.cos(a), p.y + 0.55 * math.sin(a), p.z + 1.9),
                (p.x + 0.8 * math.cos(a), p.y + 0.8 * math.sin(a), p.z), 0.22, 0.22, WOOD, 0.0)


def bench(mb, F, cx, cy, ln, yaw=0.0):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR + 1.8, ln, 1.3, 0.24, WOOD, 0.06)
    for k in (-1, 1):
        sbox(mb, F, S, k * (ln / 2 - 0.7), 0, FLOOR, 0.3, 1.1, 1.8, WOOD, 0.03)
    sbox(mb, F, S, 0, 0, FLOOR + 0.5, ln - 1.6, 0.2, 0.2, WOOD, 0.02)


def rug(mb, F, cx, cy, lx, ly, yaw=0.0):
    """tapete grosso (0,14: nada rente ao piso) com barra"""
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR, lx, ly, 0.14, M_CLOTH, 0.04)


def shelf(mb, F, cx, cy, yaw, wd, h, dp=1.5, items="books", z0=None):
    """estante: 2 laterais, fundo, 4 prateleiras, cornija e o que guarda (livros, potes, louca, garrafas) arrumado
    por prateleira (sem sorteio)"""
    S = Sub(cx, cy, yaw)
    z0 = FLOOR if z0 is None else z0
    for k in (-1, 1):
        sbox(mb, F, S, k * (wd / 2 - 0.15), 0, z0, 0.3, dp, h, WOOD, 0.0)
    sbox(mb, F, S, 0, -dp / 2 + 0.08, z0, wd - 0.3, 0.16, h, WOOD, 0.0)
    sbox(mb, F, S, 0, 0.05, z0 + h, wd + 0.4, dp + 0.3, 0.3, WOOD, 0.06)
    n = 3
    for i in range(n):
        zz = z0 + 0.25 + (h - 0.8) * i / (n - 1)
        sbox(mb, F, S, 0, 0.05, zz, wd - 0.3, dp - 0.1, 0.18, WOOD, 0.0)
        if i == n - 1:
            continue
        zi = zz + 0.18
        if items == "books":
            # 3 lotes de livros por prateleira (alturas e tons dirigidos), com vaos entre os lotes
            lots = ((-0.36, 0.22, 1.5), (0.0, 0.2, 1.25), (0.3, 0.16, 1.4)) if i % 2 == 0 else \
                   ((-0.3, 0.26, 1.3), (0.08, 0.14, 1.55), (0.34, 0.12, 1.2))
            for j, (fu, fw, bh) in enumerate(lots):
                sbox(mb, F, S, fu * wd, -0.05, zi, fw * wd, 1.0, bh, M_CLOTH if (j + i) % 2 else WOOD, 0.0)
        else:
            k = 0
            u = -wd / 2 + 0.9
            while u < wd / 2 - 0.6:
                x, y = S.xy(u, 0.0)
                p = F.p(x, y, zi)
                if items == "pots":
                    V._lathe(mb, (p.x, p.y, p.z), [(0.3, 0.0), (0.46, 0.35), (0.42, 0.8), (0.24, 1.0), (0.3, 1.12),
                                                   (0.0, 1.12)], M_DRESS if k % 2 else M_CLOTH, 6)
                else:                                                     # garrafas / frascos
                    V._lathe(mb, (p.x, p.y, p.z), [(0.26, 0.0), (0.28, 0.7), (0.12, 0.95), (0.1, 1.3),
                                                   (0.0, 1.3)], M_JNT if k % 2 else M_CLOTH, 6)
                u += 1.05
                k += 1


def bed(mb, F, cx, cy, yaw, lx=5.2, ly=9.0):
    """cama: cabeceira alta com remates, pe mais baixo, estrado, colchao, coberta navy dobrada e travesseiro claro.
    yaw = para onde o PE aponta (a cabeceira fica em v = -ly/2)"""
    S = Sub(cx, cy, yaw)
    hb = 6.0
    for k in (-1, 1):
        sbox(mb, F, S, k * (lx / 2 - 0.2), -ly / 2 + 0.2, FLOOR, 0.4, 0.4, hb, WOOD, 0.05)
        sbox(mb, F, S, k * (lx / 2 - 0.2), ly / 2 - 0.2, FLOOR, 0.4, 0.4, 2.8, WOOD, 0.05)
        sbox(mb, F, S, k * (lx / 2 - 0.12), 0, FLOOR + 0.8, 0.24, ly - 0.6, 0.8, WOOD, 0.03)
        V._lathe(mb, tuple(F.p(*S.xy(k * (lx / 2 - 0.2), -ly / 2 + 0.2), z=FLOOR + hb)),
                 [(0.24, 0.0), (0.3, 0.18), (0.0, 0.5)], WOOD, 6)
    sbox(mb, F, S, 0, -ly / 2 + 0.2, FLOOR + 2.2, lx - 0.8, 0.26, 2.6, WOOD, 0.04)     # cabeceira
    sbox(mb, F, S, 0, ly / 2 - 0.2, FLOOR + 1.3, lx - 0.8, 0.22, 1.2, WOOD, 0.04)      # pe
    sbox(mb, F, S, 0, 0, FLOOR + 1.3, lx - 0.5, ly - 0.7, 0.9, M_PL, 0.12)             # colchao
    sbox(mb, F, S, 0, 0.9, FLOOR + 2.0, lx - 0.3, ly * 0.62, 0.36, M_CLOTH, 0.12)      # coberta
    sbox(mb, F, S, 0, ly * 0.3 - 0.1, FLOOR + 2.34, lx - 0.3, 0.9, 0.24, M_CLOTH, 0.1)  # dobra
    sbox(mb, F, S, 0, -ly / 2 + 1.1, FLOOR + 2.1, lx - 1.2, 1.1, 0.5, M_PL, 0.2)       # travesseiro


def chest(mb, F, cx, cy, yaw, lx=3.2, ly=1.8, h=2.0):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR, lx, ly, h, WOOD, 0.06)
    sbox(mb, F, S, 0, 0, FLOOR + h, lx + 0.1, ly + 0.1, 0.35, WOOD, 0.1)
    for u in (-lx / 2 + 0.4, lx / 2 - 0.4):
        sbox(mb, F, S, u, 0, FLOOR + 0.1, 0.18, ly + 0.08, h + 0.3, M_JNT, 0.02)          # cintas de ferro
    sbox(mb, F, S, 0, ly / 2 + 0.04, FLOOR + h - 0.6, 0.4, 0.1, 0.5, M_JNT, 0.02)          # fecho


def wardrobe(mb, F, cx, cy, yaw, lx=4.4, ly=2.0, h=8.0):
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, FLOOR, lx, ly, 0.5, WOOD, 0.06)
    sbox(mb, F, S, 0, 0, FLOOR + 0.5, lx - 0.2, ly - 0.2, h - 1.0, WOOD, 0.0)
    sbox(mb, F, S, 0, 0.05, FLOOR + h - 0.5, lx + 0.4, ly + 0.3, 0.5, WOOD, 0.08)
    for k in (-1, 1):
        sbox(mb, F, S, k * lx / 4, ly / 2 - 0.02, FLOOR + 0.9, lx / 2 - 0.35, 0.14, h - 1.8, WOOD, 0.04)  # portas
        sbox(mb, F, S, k * 0.3, ly / 2 + 0.08, FLOOR + h * 0.45, 0.14, 0.1, 0.7, M_JNT, 0.02)


def barrel(mb, F, cx, cy, z0=None, r=1.1, h=2.8, lying=False, yaw=0.0):
    """barril: aduelas em torno de 12 lados com bojo, 2 aros de ferro"""
    z0 = FLOOR if z0 is None else z0
    prof = [(r * 0.86, 0.0), (r, h * 0.5), (r * 0.86, h)]
    ring1 = [(r * 0.9, h * 0.12), (r * 0.93, h * 0.2)]
    if not lying:
        p = F.p(cx, cy, z0)
        V._lathe(mb, (p.x, p.y, p.z), prof, WOOD, 8)
        for zz in (0.1, 0.8):
            V._lathe(mb, (p.x, p.y, p.z + h * zz), [(r * 0.9 + 0.06, 0.0), (r * 0.95 + 0.06, h * 0.08)], M_JNT, 8,
                     caps=(False, False))
    else:
        S = Sub(cx, cy, yaw)
        a = F.p(*S.xy(-h / 2, 0.0), z=z0 + r)
        b = F.p(*S.xy(h / 2, 0.0), z=z0 + r)
        mb.rod(a, b, r * 0.94, WOOD, 8)
        for t in (0.18, 0.82):
            c = a + (b - a) * t
            d = (b - a).normalized() * 0.12
            mb.rod(c - d, c + d, r * 0.94 + 0.14, M_JNT, 8)


def crate(mb, F, cx, cy, z0=None, s=2.2, yaw=0.0):
    z0 = FLOOR if z0 is None else z0
    S = Sub(cx, cy, yaw)
    sbox(mb, F, S, 0, 0, z0, s, s, s, WOOD, 0.08)
    for k in (-1, 1):
        sbox(mb, F, S, 0, k * (s / 2 + 0.03), z0 + 0.15, s - 0.2, 0.08, 0.3, WOOD, 0.02)
        sbox(mb, F, S, 0, k * (s / 2 + 0.03), z0 + s - 0.45, s - 0.2, 0.08, 0.3, WOOD, 0.02)


def candle(mb, F, x, y, z, s=1.0):
    p = F.p(x, y, z)
    mb.cyl(0.2 * s, 0.6 * s, (p.x, p.y, p.z + 0.3 * s), m=M_PL, n=5, bevel=0.0)
    V._lathe(mb, (p.x, p.y, p.z + 0.62 * s), [(0.0, 0.0), (0.12 * s, 0.14 * s), (0.0, 0.42 * s)], M_ROOM, 4)


# ------------------------------------------------------------------ lareira de pedra (acesa, brilho contido)
def fireplace(mb, F, x0, y0, y1, dep, zt, nm, big=False, upper=None):
    """peito de chamine de cantaria encostado na parede 'left' (x0 = face do forro): fiadas de 2 alturas, BOCA em arco
    abatido com fundo de fuligem, lareira (brasa Neon medio + chama baixa + 3 toras + cavaletes de ferro), consolo de
    madeira, lajeado da lareira na frente. upper = (z0, z1, dx, y0, y1) peito do andar de cima ate a chamine."""
    xf = x0 + dep
    yc = (y0 + y1) / 2
    wd = y1 - y0
    bw = 4.2 if big else 3.2
    bh = 3.9 if big else 3.3
    G0 = Frame(0.0, 0.0, 0.0, 0.0)
    # corpo em fiadas (face da frente vazada na boca)
    hs = (1.7, 1.2)
    zz, k = 0.0, 0
    while zz < zt - 0.05:
        h = min(hs[k % 2], zt - zz)
        ins = 0.0 if k % 2 == 0 else 0.1
        za, zb = zz + 0.04, zz + h - 0.04
        if za >= bh + FLOOR - 0.05:
            tb(mb, F, x0 + (dep - ins) / 2, yc, za, dep - ins, wd - ins, zb - za, M_DRESS, 0.0)
        else:
            for s0, s1 in ((y0, yc - bw / 2), (yc + bw / 2, y1)):
                tb(mb, F, x0 + (dep - ins) / 2, (s0 + s1) / 2, za, dep - ins, s1 - s0, zb - za, M_DRESS, 0.0)
            if zb > bh + FLOOR:
                tb(mb, F, x0 + (dep - ins) / 2, yc, bh + FLOOR, dep - ins, bw, zb - bh - FLOOR, M_DRESS, 0.0)
        zz += h
        k += 1
    # boca: fundo de fuligem, teto e arco abatido de aduelas
    tb(mb, F, x0 + 0.3, yc, FLOOR, 0.6, bw, bh, M_JNT, 0.0)
    tb(mb, F, x0 + dep / 2, yc, FLOOR + bh - 0.3, dep - 0.2, bw, 0.3, M_JNT, 0.0)
    n = 5
    for i in range(n):
        a0 = math.pi * (0.15 + 0.7 * i / n)
        a1 = math.pi * (0.15 + 0.7 * (i + 1) / n)
        am = (a0 + a1) / 2
        r = bw / 2 / math.cos(math.pi * 0.35)
        ym = yc - r * math.cos(am)
        zm = FLOOR + bh - 0.6 - r * math.sin(math.pi * 0.15) + r * math.sin(am)
        tb(mb, F, xf + 0.1, ym, zm - 0.35, 0.3, 2 * r * math.sin((a1 - a0) / 2) - 0.08, 0.7, M_DRESS, 0.0)
    # consolo de madeira (prateleira) sobre misulas
    zmn = FLOOR + bh + 1.0
    tb(mb, F, xf + 0.35, yc, zmn, 1.0, wd + 0.8, 0.35, WOOD, 0.06)
    for s in (-1, 1):
        tb(mb, F, xf + 0.2, yc + s * (wd / 2 - 0.4), zmn - 0.9, 0.6, 0.4, 0.9, WOOD, 0.03)
    # objetos no consolo (dirigidos: 2 castiçais + 1 pote)
    for s in (-1, 1):
        candle(mb, F, xf + 0.35, yc + s * (wd / 2 - 0.3), zmn + 0.35, 1.0)
    V._lathe(mb, tuple(F.p(xf + 0.35, yc + 0.8, zmn + 0.35)), [(0.3, 0.0), (0.42, 0.4), (0.25, 0.8), (0.3, 0.9),
                                                                (0.0, 0.9)], M_CLOTH, 6)
    # lajeado da lareira (0,10 acima do piso) e fogo
    tb(mb, F, xf + 1.1, yc, FLOOR, 2.2, bw + 2.4, 0.12, M_DRESS, 0.04)
    tb(mb, F, x0 + dep * 0.55, yc, FLOOR, dep * 0.9, bw - 0.2, 0.2, M_JNT, 0.0)
    for s in (-1, 1):                                                      # cavaletes de ferro
        tb(mb, F, xf - 0.5, yc + s * (bw / 2 - 0.7), FLOOR + 0.2, 1.4, 0.14, 0.14, M_JNT, 0.0)
        tb(mb, F, xf - 0.05, yc + s * (bw / 2 - 0.7), FLOOR + 0.2, 0.14, 0.14, 1.0, M_JNT, 0.0)
    xfire = x0 + dep * 0.55
    for i, (dy, ang) in enumerate(((-0.5, 0.25), (0.5, -0.25), (0.0, 0.0))):
        zc = FLOOR + 0.55 + 0.3 * (i == 2)
        a = F.p(xfire - 0.8, yc + dy - math.sin(ang) * 1.2, zc)
        b = F.p(xfire + 0.6, yc + dy + math.sin(ang) * 1.2, zc)
        mb.rod(a, b, 0.28, WOOD, 5)
    # brasa (Neon medio: SG_VilRoom_Glow) em 2 camas baixas + 3 linguas de chama pequenas: brilho CONTIDO na boca
    tb(mb, F, xfire - 0.1, yc, FLOOR + 0.2, 1.2, bw * 0.55, 0.18, M_ROOM, 0.03)
    for dy, hh in ((-0.45, 1.0), (0.1, 1.35), (0.55, 0.85)):
        p = F.p(xfire - 0.1, yc + dy, FLOOR + 0.62)
        V._lathe(mb, (p.x, p.y, p.z), [(0.0, 0.0), (0.26, 0.18), (0.16, hh * 0.55), (0.0, hh)], M_ROOM, 5)
    if upper:
        z0u, z1u, dxu, uy0, uy1 = upper
        zz, k = z0u, 0
        while zz < z1u - 0.05:
            h = min((3.2, 2.4)[k % 2], z1u - zz)
            ins = 0.0 if k % 2 == 0 else 0.1
            tb(mb, F, x0 + (dxu - ins) / 2, (uy0 + uy1) / 2, zz + 0.04, dxu - ins, (uy1 - uy0) - ins, h - 0.08,
               M_DRESS, 0.0)
            zz += h
            k += 1


# ------------------------------------------------------------------ escada de madeira + guarda-corpo
def stair_wood(mb, F, xs, yb, sw, n, rise, tread, open_side=1):
    """escada reta de madeira que sobe em +X a partir de (xs, yb): degraus (pisada com focinho + espelho), banzo
    fechado do lado aberto (com o fechamento de tabuas embaixo), banzo de parede, CORRIMAO sobre balaustres (1 por
    degrau) e pilares de arranque/chegada torneados"""
    ys = yb + open_side * sw / 2                      # lado aberto
    yw = yb - open_side * sw / 2                      # lado da parede
    for i in range(n):
        zt = rise * (i + 1)
        x0 = xs + tread * i
        tb(mb, F, x0 + tread / 2 + 0.05, yb, zt - 0.18, tread + 0.12, sw - 0.1, 0.18, WOOD, 0.0)    # pisada
    zt_ = rise * n
    xe = xs + tread * n
    k = rise / tread
    # banzos inclinados (sob a linha dos focinhos)
    for yy, th in ((ys - open_side * 0.2, 0.4), (yw + open_side * 0.12, 0.24)):
        a = (xs - 0.3, yy, rise * 0.5 - 0.9)
        b = (xe, yy, zt_ - 0.9)
        bm_(mb, F, a, b, th, 1.5)
    # fechamento de tabuas sob o banzo do lado aberto (armario sob a escada): pecas verticais ate o banzo
    npan = int(min(xe - xs - 2.0, 9.0) / 1.6)
    for j in range(npan):
        xa = xs + 1.2 + 1.6 * j
        xb = xa + 1.5
        zt_a = rise * 0.5 + (xa - xs) * k - 1.7
        if zt_a < 0.8:
            continue
        tb(mb, F, (xa + xb) / 2, ys - open_side * 0.2, FLOOR, 1.5, 0.14, zt_a - FLOOR, WOOD, 0.02)
    # corrimao + balaustres
    rh = 3.0
    for i in range(1, n, 2):
        x = xs + tread * i + 0.4
        if x > xe - 0.4:
            break
        zb = rise * (i + 1)
        tb(mb, F, x, ys - open_side * 0.3, zb, 0.24, 0.24, rh - 0.1, WOOD, 0.0)
    a = (xs - 0.2, ys - open_side * 0.3, rise + rh)
    b = (xe, ys - open_side * 0.3, zt_ + rh)
    bm_(mb, F, a, b, 0.36, 0.3)
    # pilar de arranque e de chegada (quadrado com remate)
    for (x, zb, hh) in ((xs - 0.3, 0.0, rise + rh + 0.4), (xe + 0.3, zt_, rh + 0.4)):
        tb(mb, F, x, ys - open_side * 0.3, FLOOR if zb == 0 else zb, 0.62, 0.62, hh, WOOD, 0.06)
        V._lathe(mb, tuple(F.p(x, ys - open_side * 0.3, (FLOOR if zb == 0 else zb) + hh)),
                 [(0.36, 0.0), (0.2, 0.2), (0.28, 0.42), (0.0, 0.72)], WOOD, 4, math.pi / 4)


def rail(mb, F, a, b, z, h=3.2, step=3.0, posts=True):
    """guarda-corpo de madeira: rodape, corrimao e balaustres; pilares nas pontas"""
    ax, ay = a
    bx, by = b
    ln = math.hypot(bx - ax, by - ay)
    if ln < 0.5:
        return
    ux, uy = (bx - ax) / ln, (by - ay) / ln
    bm_(mb, F, (ax, ay, z + 0.18), (bx, by, z + 0.18), 0.3, 0.36)
    bm_(mb, F, (ax, ay, z + h), (bx, by, z + h), 0.4, 0.3)
    nn = max(1, int(ln / step))
    for j in range(1, nn):
        x, y = ax + ux * ln * j / nn, ay + uy * ln * j / nn
        tb(mb, F, x, y, z + 0.36, 0.22, 0.22, h - 0.5, WOOD, 0.0)
    if posts:
        for (x, y) in (a, b):
            tb(mb, F, x, y, z, 0.56, 0.56, h + 0.35, WOOD, 0.05)


# ------------------------------------------------------------------ forro de parede, janelas por dentro, porta
def wall_faces(F, w, d):
    return {"front": V.Face(F, (0.0, d / 2), (1.0, 0.0), w), "back": V.Face(F, (0.0, -d / 2), (-1.0, 0.0), w),
            "right": V.Face(F, (w / 2, 0.0), (0.0, -1.0), d), "left": V.Face(F, (-w / 2, 0.0), (0.0, 1.0), d)}


def s_on(wall, c):
    return {"front": c, "back": -c, "right": -c, "left": c}[wall]


def linings(mbx, mi, F, hrec, info, levels):
    """forro de reboco (0,5) dos 4 lados em cada andar, com os vaos da porta e das janelas + a janela vista de dentro
    (postigos fechados recuados 0,24, guarnicao, peitoril) e o rodape de madeira"""
    nm, tp, x, y, w, d, deg, z = hrec
    fs = wall_faces(F, w, d)
    dw2 = (V.DW / 2 + 0.1) * V.K
    dh = (V.DH + 0.1) * V.K
    for li, (z0, z1) in enumerate(levels):
        for wall, f in fs.items():
            side = wall in ("right", "left")
            s0, s1 = (-(d / 2 - WALL), d / 2 - WALL) if side else (-(w / 2 - 0.5), w / 2 - 0.5)
            holes = []
            if li == 0 and wall == "front":
                holes.append((-dw2, dw2, -1.0, dh))
            wins = [wd for wd in info["windows"] if wd["wall"] == wall and wd["story"] == li]
            for wd in wins:
                s = s_on(wall, wd["c"])
                holes.append((s - wd["w"] / 2, s + wd["w"] / 2, wd["z0"], wd["z1"]))
            V.slab_holes(mbx, f, s0, s1, z0 - 0.1, z1, -WALL, -0.5, holes, V.M_PL)
            # rodape (sai 0,14; para no vao da porta e na lareira)
            skip = [(-dw2 - 0.4, dw2 + 0.4)] if (li == 0 and wall == "front") else []
            if wall == "left":
                skip.append((info["hearth"][0] - 0.3, info["hearth"][1] + 0.3))
            if li == 1 and wall == "back" and tp in ("A", "B"):
                skip.append((-1e9, 1e9))                     # atras da escada: o banzo de parede faz o papel
            V.band_face(mi, f, -WALL - 0.14, -WALL + 0.0, z0, z0 + 0.62, WOOD, ext=0.0, gaps=skip)
            for wd in wins:
                s = s_on(wall, wd["c"])
                ww, za, zb = wd["w"], wd["z0"], wd["z1"]
                # postigos fechados (2 folhas navy + travessa) recuados 0,24 no vao do forro
                f.box(mi, s, -WALL + 0.3, (za + zb) / 2, ww, 0.06, zb - za, M_SHUT)          # postigos fechados
                f.box(mi, s, -WALL + 0.1, (za + zb) / 2, 0.16, 0.06, zb - za, WOOD)             # 2 folhas
                f.box(mi, s, -WALL - 0.3, za - 0.1, ww + 0.9, 0.6, 0.2, WOOD)                  # peitoril
    # porta por dentro: guarnicao e as 2 FOLHAS abertas, encostadas na parede (165 graus)
    f = fs["front"]
    gw = 0.5
    for k in (-1, 1):
        f.box(mi, k * (dw2 + gw / 2), -WALL - 0.1, (FLOOR + dh) / 2, gw, 0.2, dh - FLOOR + gw, WOOD)
    f.box(mi, 0.0, -WALL - 0.1, dh + gw / 2, 2 * dw2 + 2 * gw, 0.2, gw, WOOD)
    th = math.radians(165.0)
    lw = V.DW / 2 * V.K - 0.1
    lh = V.DH * V.K - 0.2
    for k in (-1, 1):
        hx, hy = k * (dw2 - 0.12), d / 2 - WALL - 0.2
        ux, uy = (-k * math.cos(th), -math.sin(th))            # direcao da folha a partir da dobradica
        yaw = math.atan2(uy, ux)
        S = Sub(hx, hy, yaw)
        # tabuas verticais (4) + 3 travessas + ferragens em T + argola
        sbox(mi, F, S, lw / 2, 0.0, FLOOR + 0.06, lw, 0.34, lh, WOOD, 0.0)
        for zz in (0.9, lh / 2, lh - 1.2):
            sbox(mi, F, S, lw / 2, -0.24, FLOOR + zz, lw - 0.4, 0.14, 0.5, WOOD, 0.02)
            sbox(mi, F, S, lw * 0.35, 0.22, FLOOR + zz + 0.1, lw * 0.7, 0.08, 0.26, M_JNT, 0.0)
        x_, y_ = S.xy(lw - 0.6, 0.3)
        p = F.p(x_, y_, FLOOR + lh * 0.46)
        mi.box((0.14, 0.14, 0.7), (p.x, p.y, p.z), (0, 0, S.a + F.a), M_JNT, 0.0)


def floor_boards(mi, F, x0, x1, y0, y1, zt, m=WOOD, along="x", pw=3.0, holes=()):
    """piso de tabuas (junta de 0,08 sobre o leito escuro 0,18 abaixo do topo) entre x0..x1, y0..y1; holes = retangulos
    (x0, y0, x1, y1) sem piso (vao da escada, vazio do mezanino)"""
    def cut(a0, a1, b0, b1):
        rects = [(a0, a1, b0, b1)]
        for hx0, hy0, hx1, hy1 in holes:
            out = []
            for (p0, p1, q0, q1) in rects:
                if hx1 <= p0 or hx0 >= p1 or hy1 <= q0 or hy0 >= q1:
                    out.append((p0, p1, q0, q1))
                    continue
                if hx0 > p0:
                    out.append((p0, hx0, q0, q1))
                if hx1 < p1:
                    out.append((hx1, p1, q0, q1))
                m0, m1 = max(p0, hx0), min(p1, hx1)
                if hy0 > q0:
                    out.append((m0, m1, q0, hy0))
                if hy1 < q1:
                    out.append((m0, m1, hy1, q1))
            rects = out
        return rects
    for (a0, a1, b0, b1) in cut(x0, x1, y0, y1):
        tb(mi, F, (a0 + a1) / 2, (b0 + b1) / 2, zt - 0.3, a1 - a0, b1 - b0, 0.12, M_JNT, 0.0)
        n = max(1, int(round((b1 - b0) / pw)))
        for j in range(n):
            c0 = b0 + (b1 - b0) * j / n + 0.04
            c1 = b0 + (b1 - b0) * (j + 1) / n - 0.04
            # 2 pecas por fiada com a junta desencontrada
            sp = a0 + (a1 - a0) * (0.38 if j % 2 else 0.64)
            for (e0, e1) in ((a0, sp - 0.04), (sp + 0.04, a1)):
                if e1 - e0 > 0.3:
                    tb(mi, F, (e0 + e1) / 2, (c0 + c1) / 2, zt - 0.18, e1 - e0, c1 - c0, 0.18, m, 0.0)


def flag_floor(mi, F, x0, x1, y0, y1, zt, sz=3.0):
    """lajeado da taverna: lajes de ~3 em fiadas desencontradas, 2 tons de pedra (junta de 0,1 sobre o leito)"""
    tb(mi, F, (x0 + x1) / 2, (y0 + y1) / 2, zt - 0.4, x1 - x0, y1 - y0, 0.12, M_JNT, 0.0)
    ny = max(1, int(round((y1 - y0) / sz)))
    for j in range(ny):
        c0 = y0 + (y1 - y0) * j / ny + 0.05
        c1 = y0 + (y1 - y0) * (j + 1) / ny - 0.05
        off = (sz / 2) * (j % 2)
        xs = [x0] + [x0 + off + sz * i for i in range(1, 40) if x0 + off + sz * i < x1 - 0.8] + [x1]
        for i, (e0, e1) in enumerate(zip(xs, xs[1:])):
            tb(mi, F, (e0 + e1) / 2, (c0 + c1) / 2, zt - 0.28, e1 - e0 - 0.1, c1 - c0, 0.28,
               M_DRESS if (i + j) % 3 else M_CAP, 0.04)


def ceiling(mi, F, iw, idp, zc, holes, joist_step=5.0):
    """teto do terreo = laje do andar: forro de tabuas (face de baixo em zc), leito e piso de tabuas (topo zc + 1);
    vigas aparentes de 0,7 x 1,0 a cada ~3,2 (param no vao da escada/vazio) e vigas de borda no vao"""
    x0, x1, y0, y1 = -iw / 2, iw / 2, -idp / 2, idp / 2
    floor_boards(mi, F, x0, x1, y0, y1, zc + 1.0, holes=holes)
    # forro (face de baixo) em pecas por retangulo livre
    for (a0, a1, b0, b1) in _free_rects(x0, x1, y0, y1, holes):
        tb(mi, F, (a0 + a1) / 2, (b0 + b1) / 2, zc, a1 - a0, b1 - b0, 0.12, WOOD, 0.0)
    xs = [x0 + joist_step * (k + 0.5) for k in range(int(iw / joist_step))]
    for xj in xs:
        segs = [(y0, y1)]
        for hx0, hy0, hx1, hy1 in holes:
            if hx0 - 0.4 < xj < hx1 + 0.4:
                nsg = []
                for a, b in segs:
                    if hy1 <= a or hy0 >= b:
                        nsg.append((a, b))
                        continue
                    if hy0 > a:
                        nsg.append((a, hy0))
                    if hy1 < b:
                        nsg.append((hy1, b))
                segs = nsg
        for a, b in segs:
            if b - a > 1.0:
                tb(mi, F, xj, (a + b) / 2, zc - 1.0, 0.7, b - a, 1.0, WOOD, 0.05)
    for hx0, hy0, hx1, hy1 in holes:
        for yy in (hy0, hy1):
            if y0 + 0.5 < yy < y1 - 0.5:
                tb(mi, F, (hx0 + hx1) / 2, yy + (0.35 if yy == hy1 else -0.35), zc - 1.0, hx1 - hx0, 0.7, 1.12, WOOD,
                   0.05)


def _free_rects(x0, x1, y0, y1, holes):
    rects = [(x0, x1, y0, y1)]
    for hx0, hy0, hx1, hy1 in holes:
        out = []
        for (p0, p1, q0, q1) in rects:
            if hx1 <= p0 or hx0 >= p1 or hy1 <= q0 or hy0 >= q1:
                out.append((p0, p1, q0, q1))
                continue
            if hx0 > p0:
                out.append((p0, hx0, q0, q1))
            if hx1 < p1:
                out.append((hx1, p1, q0, q1))
            m0, m1 = max(p0, hx0), min(p1, hx1)
            if hy0 > q0:
                out.append((m0, m1, q0, hy0))
            if hy1 < q1:
                out.append((m0, m1, hy1, q1))
        rects = out
    return rects


# ------------------------------------------------------------------ telhado por dentro (referencial do kit)
def roof_inside(mbx, mi, F, info):
    """forro inclinado de tabuas (0,6 abaixo da ardosia), meia-parede de reboco (joelho) do frechal ate o forro nas
    paredes do beiral, frechal de madeira e TESOURAS (linha, pendural, pernas e escoras) - 'forro aberto ate as
    tesouras'. Tudo no referencial do kit (casa com a ardosia)."""
    G = info["G"]
    ze, R, hd, cy = info["ze"], info["R"], info["hd"], info["cy"]
    bx0, bx1, by0, by1 = info["body0"]
    t = math.atan2(R, hd)
    tn = math.tan(t)
    lx0, lx1 = bx0 + 0.5, bx1 - 0.5                  # face interna do forro (kit)
    ly0, ly1 = by0 + 0.5, by1 - 0.5

    def zu(yy):                                       # face de baixo da ardosia
        return ze + R - abs(yy - cy) * tn
    gap = 0.3                                         # 0,6 real abaixo da ardosia
    info["zboard"] = lambda gy: (zu(gy) - gap - 0.12) * V.K
    with V.KitXF([mbx, mi], F):
        for s, yw in ((1, ly1), (-1, ly0)):
            zk = zu(yw) - gap - 0.12
            # meia-parede (joelho) de reboco do frechal ate o forro
            if zk > ze + 0.05:
                mbx.box((lx1 - lx0, 0.25, zk - ze + 0.1), G.p((lx0 + lx1) / 2, yw + s * 0.125, (ze + zk) / 2 + 0.05),
                        G.r(), V.M_PL, 0.0)
            mi.box((lx1 - lx0, 0.3, 0.32), G.p((lx0 + lx1) / 2, yw - s * 0.15, zk - 0.16), G.r(), WOOD, 0.02)  # frechal
            # forro inclinado: placa de yw ate a cumeeira, 0,12 de espessura, topo a 'gap' abaixo da ardosia
            ya, yb_ = yw, cy
            za, zb_ = zu(ya) - gap, zu(yb_) - gap
            ln = math.hypot(yb_ - ya, zb_ - za)
            ang = math.atan2(zb_ - za, abs(yb_ - ya))
            mid = G.p((lx0 + lx1) / 2, (ya + yb_) / 2, (za + zb_) / 2 - 0.06 / math.cos(ang))
            mi.box((lx1 - lx0, ln, 0.12), mid, G.r(-s * ang, 0, 0), WOOD, 0.0)
        # cumeeira interna + tesouras
        mi.box((lx1 - lx0, 0.5, 0.6), G.p((lx0 + lx1) / 2, cy, zu(cy) - gap - 0.4), G.r(), WOOD, 0.03)
        nt = max(2, int((lx1 - lx0) / 5.0))
        dxs = [xd for sd_, xd in info.get("dormers", [])]
        for j in range(nt):
            xt = lx0 + (lx1 - lx0) * (j + 0.5) / nt
            for xd in dxs:
                if abs(xt - xd) < 2.2:
                    xt = xd + (2.3 if xt >= xd else -2.3)
            zt_ = max(ze + 0.5, min(zu(ly0), zu(ly1)) - gap - 0.5)
            info.setdefault("trusses", []).append((xt, zt_ - 0.225))
            mi.box((0.4, ly1 - ly0, 0.45), G.p(xt, (ly0 + ly1) / 2, zt_), G.r(), WOOD, 0.03)            # linha
            ztop = zu(cy) - gap - 0.35
            mi.box((0.4, 0.4, ztop - zt_), G.p(xt, cy, (zt_ + ztop) / 2), G.r(), WOOD, 0.03)          # pendural
            for s, yw in ((1, ly1), (-1, ly0)):
                a = G.p(xt, yw - s * 0.2, zt_ + 0.1)
                b = G.p(xt, cy + s * 0.25, ztop - 0.1)
                mi.beam(a, b, 0.36, 0.42, WOOD, 0.0)                                                  # perna
                c = G.p(xt, cy + s * 0.2, zt_ + 0.3)
                e = G.p(xt, cy + s * (abs(yw - cy) * 0.5), (zt_ + ztop) / 2 + 0.2)
                mi.beam(c, e, 0.26, 0.3, WOOD, 0.0)                                                   # escora


# ------------------------------------------------------------------ luzes e colisao
def house_light(nm, F, fx, fy, z, prev_name=None, energy=260.0):
    p = F.p(fx, fy, z)
    if prev_name is None:
        light("L_SGVil_House_%s" % nm, "POINT", (p.x, p.y, p.z), energy, (1.0, 0.66, 0.36), 0.5)
    else:
        ob = light(prev_name, "AREA", (p.x, p.y, p.z), energy, (1.0, 0.7, 0.42), 1.0)
        try:
            ob.data.size = 6.0
        except Exception:
            pass
    return (p.x, p.y, p.z)


def collisions(area, F, hrec, T, eave):
    """a colisao da onda 0 (sg_blockout.house) com o piso interno a 0,30 e o soco: paredes de 1 com o vao da porta
    8 x 11, forro (segura a camera)"""
    nm, tp, x, y, w, d, deg, z = hrec
    t = WALL
    dw, dh = L.HOUSE_DOOR
    for sx, sy, lx, ly in ((0, -d / 2 + t / 2, w, t), (-w / 2 + t / 2, 0, t, d), (w / 2 - t / 2, 0, t, d)):
        col_box(area, (lx, ly, eave + 0.5), F.p(sx, sy, eave / 2 - 0.25), F.r())
    for s in (-1, 1):
        seg = (w - dw) / 2
        col_box(area, (seg, t, eave + 0.5), F.p(s * (dw / 2 + seg / 2), d / 2 - t / 2, eave / 2 - 0.25), F.r())
    col_box(area, (dw, t, eave - dh), F.p(0, d / 2 - t / 2, dh + (eave - dh) / 2), F.r())
    col_box(area + "Roof", (w, d, 1.0), F.p(0, 0, eave + 0.5), F.r())
    col_box(area, (w - 2 * t, d - 2 * t, 1.0), F.p(0, 0, FLOOR - 0.5), F.r())            # piso interno
    # soco (sai 0,84 da parede, 2 de altura), aberto na porta
    so = 0.84
    for sx, sy, lx, ly in ((0, -d / 2 - so / 2, w + 2 * so, so), (-w / 2 - so / 2, 0, so, d), (w / 2 + so / 2, 0, so, d)):
        col_box(area + "Socle", (lx, ly, 2.0), F.p(sx, sy, 1.0), F.r())
    for s in (-1, 1):
        seg = (w + 2 * so - dw - 1.2) / 2
        col_box(area + "Socle", (seg, so, 2.0), F.p(s * (dw / 2 + 0.6 + seg / 2), d / 2 + so / 2, 1.0), F.r())


# ------------------------------------------------------------------ interior por tipo
def interior(mbx, hrec, spec, info):
    nm, tp, x, y, w, d, deg, z = hrec
    T = L.HOUSE_TYPES[tp]
    F = V.lot_frame(hrec)
    rng = random.Random(4300 + int(nm[1:]))
    mi = MB("SG_Vil_Int_%s" % nm, V.COLL, rng, detail="near")
    area = "SG_VilHouse%s" % nm
    iw, idp = w - 2 * WALL, d - 2 * WALL
    two = T["floors"] == 2
    h0 = T["h0"]
    zf = h0 + 1.0
    eave = info["ze"] * V.K
    # lareira na parede 'left' (onda 0: x = -w/2 + 1 + 1,2, y = 1): peito de 2,4 x 6 (taverna: 3,0 x 10)
    big = tp == "B"
    dep = 3.3
    hy0, hy1 = (-2.0, 8.0) if big else (-2.0, 4.0)
    xl = -iw / 2
    info["hearth"] = (hy0, hy1)
    levels = [(FLOOR, h0 if two else eave)] + ([(zf, eave)] if two else [])
    linings(mbx, mi, F, hrec, info, levels)
    # piso do terreo
    floor_boards(mi, F, -iw / 2, iw / 2, -idp / 2, idp / 2, FLOOR, pw=(3.2 if tp == "B" else 3.0))
    # lareira (+ peito do andar de cima ate a base da chamine)
    ch = info["chimneys"][0] if info.get("chimneys") else None
    upper = None
    zch = ch[4] if ch else eave
    if two and ch:
        cu, cv, cwx, cdp, _ = ch
        upper = (zf, zch + 0.4, max(1.2, (cu + cwx / 2) - xl + 0.1), cv - cdp / 2 - 0.1, cv + cdp / 2 + 0.1)
    fireplace(mi, F, xl, hy0, hy1, dep, (h0 + 0.46 if two else zch + 0.4), nm, big=big, upper=upper)
    lcol(area, F, xl + dep / 2, (hy0 + hy1) / 2, 0.0, dep, hy1 - hy0, (h0 if two else zch))
    if upper:
        lcol(area, F, xl + upper[2] / 2, (upper[3] + upper[4]) / 2, zf, upper[2], upper[4] - upper[3], zch - zf)
    fx_light = (xl + dep + 2.2, (hy0 + hy1) / 2, FLOOR + 3.2)
    if nm in REAL_LIGHT:
        house_light(nm, F, *fx_light)
    else:
        house_light(nm, F, 0.0, 0.0, (h0 if two else eave) - 1.5, prev_name="PREVIEW_L_SGVil_%s_T" % nm, energy=900.0)
    if two:
        house_light(nm, F, 2.0, 3.0, eave - 1.0, prev_name="PREVIEW_L_SGVil_%s_A" % nm, energy=900.0)
    # escada + laje + guarda (a da onda 0)
    holes = []
    if two:
        rise = h0 + 1.0
        n = int(math.ceil(rise / 0.83))
        tread = 1.6
        sw = 6.0
        xs = -iw / 2 + 2.0
        yb = -idp / 2 + sw / 2
        xe = xs + n * tread
        stair_wood(mi, F, xs, yb, sw, n, rise / n, tread, open_side=1)
        sg_col.stair_col(area + "Stair", F.p(xs, yb, 0.0), F.a, sw, n, rise / n, tread, guards=False)
        holes = [(-iw / 2, -idp / 2, xe, -idp / 2 + sw)]
        void = spec.get("void")
        if void:
            holes.append(void)
        # laje (colisao): tudo menos o vao da escada e o vazio
        for (a0, a1, b0, b1) in _free_rects(-iw / 2, iw / 2, -idp / 2, idp / 2, holes):
            if a1 - a0 > 0.3 and b1 - b0 > 0.3:
                lcol(area + "Floor", F, (a0 + a1) / 2, (b0 + b1) / 2, zf - 1.0, a1 - a0, b1 - b0, 1.0)
        ceiling(mi, F, iw, idp, h0, holes)
        # guarda no vao da escada (onda 0) + corrimao visual
        gy = -idp / 2 + sw + 0.3
        gx0, gx1 = -iw / 2, xe - 1.0
        lcol(area + "Guard", F, (gx0 + gx1) / 2, gy, zf, gx1 - gx0, 0.6, 3.6)
        rail(mi, F, (gx0 + 0.3, gy), (gx1, gy), zf, 3.2)
        if void:
            vx0, vy0, vx1, vy1 = void
            for a, b in (((vx0, vy0), (vx1, vy0)), ((vx1, vy0), (vx1, vy1)), ((vx1, vy1), (vx0, vy1)),
                         ((vx0, vy1), (vx0, vy0))):
                ax, ay = a[0] + (0.3 if a[0] == vx0 else -0.3), a[1] + (0.3 if a[1] == vy0 else -0.3)
                bx, by = b[0] + (0.3 if b[0] == vx0 else -0.3), b[1] + (0.3 if b[1] == vy0 else -0.3)
                rail(mi, F, (ax, ay), (bx, by), zf, 3.2)
                ln = math.hypot(bx - ax, by - ay)
                lcol(area + "Guard", F, (ax + bx) / 2, (ay + by) / 2, zf, ln + 0.6, 0.6, 3.6,
                     yaw=math.atan2(by - ay, bx - ax))
        # piso do andar: as tabuas ja sairam no ceiling(); lambril de canto nada
    collisions(area, F, hrec, T, eave)
    if spec.get("shop") is not None:
        # a loja: balcao de pedra e persiana (sai 2,0 da fachada ate 4,2 de altura)
        lcol(area + "Socle", F, spec["shop"], d / 2 + 1.0, 0.0, V.SHOP_W * V.K + 1.6, 2.0, 4.2)
    roof_inside(mbx, mi, F, info)
    # turret: colisao no mundo
    if info.get("turret"):
        tx, ty, r, ztop = info["turret"]
        p = F.p(tx * V.K, ty * V.K, 0.0)
        SL.octo_col(area + "Turret", p.x, p.y, (r + 0.3) * V.K, z - 0.8, z + ztop * V.K)
    # moveis por papel
    {"A": furnish_a, "B": furnish_b, "C": furnish_c}[tp](mi, F, area, hrec, spec, info, iw, idp, h0, zf)
    mi.finish()


def furnish_a(mi, F, area, hrec, spec, info, iw, idp, h0, zf):
    nm = hrec[0]
    # terreo: mesa de 4 lugares (colisao da onda 0 deslocada p/ o tamanho novo), tapete, cadeira de bracos junto ao fogo
    table(mi, F, 4.0, 2.5, 8.0, 4.0)
    lcol(area, F, 4.0, 2.5, 0.0, 8.0, 4.0, 3.4)
    rug(mi, F, 4.0, 2.5, 11.5, 7.2)
    for cx, cy, yw in ((2.0, -0.7, math.pi / 2), (6.0, -0.7, math.pi / 2)):
        chair(mi, F, cx, cy, yw)
    bench(mi, F, 4.0, 5.5, 6.6)
    chair(mi, F, -8.0, 5.4, math.pi)                     # junto ao fogo
    # aparador com louca + estante na parede da direita (y -3,5..2,5)
    shelf(mi, F, iw / 2 - 0.8, -0.5, math.pi / 2, 6.0, 9.0, 1.6, items="pots" if nm in ("H3",) else "books")
    lcol(area, F, iw / 2 - 0.8, -0.5, 0.0, 1.6, 6.0, 9.0)
    # bancada do OFICIO sob a janela da frente direita (x 8,6..13,8)
    wb_x = 11.2 if spec.get("shop", 0) >= 0 or True else -11.2
    craft_bench(mi, F, nm, wb_x, idp / 2 - 0.95)
    lcol(area, F, wb_x, idp / 2 - 0.95, 0.0, 5.2, 1.9, 3.6)
    # sob a escada (ponta alta): barris e caixotes
    barrel(mi, F, 5.5, -idp / 2 + 1.4)
    barrel(mi, F, 8.2, -idp / 2 + 1.3, r=1.0, h=2.5)
    crate(mi, F, 10.8, -idp / 2 + 1.4, s=2.2)
    # andar de cima: cama, bau, guarda-roupa, escrivaninha, tapete
    _lift(bed)(mi, F, iw / 2 - 2.7, idp / 2 - 4.6, math.pi, z=zf)
    lcol(area, F, iw / 2 - 2.7, idp / 2 - 4.6, zf, 5.2, 9.0, 2.2)
    _lift(chest)(mi, F, iw / 2 - 2.7, 0.9, 0.0, z=zf)
    _lift(table)(mi, F, iw / 2 - 6.4, idp / 2 - 1.2, 1.7, 1.7, 2.5, z=zf)            # criado-mudo
    candle(mi, F, iw / 2 - 6.4, idp / 2 - 1.2, zf + 2.5, 1.1)
    wardrobe_z(mi, F, -4.3, idp / 2 - 1.0, zf)
    lcol(area, F, -4.3, idp / 2 - 1.0, zf, 4.4, 2.0, 8.0)
    desk_z(mi, F, -iw / 2 + 1.1, 7.2, zf)
    rug_z(mi, F, 0.0, 3.0, 10.0, 6.5, zf)


def _lift(fn):
    """chama um movel 'de piso' com o piso do andar de cima (troca FLOOR temporariamente)"""
    def wrap(*a, z=0.0, **k):
        global FLOOR
        old = FLOOR
        FLOOR = z + 0.0
        try:
            return fn(*a, **k)
        finally:
            FLOOR = old
    return wrap


def chest_z(mi, F, cx, cy, zf):
    _lift(chest)(mi, F, cx, cy, math.pi / 2, z=zf)


def wardrobe_z(mi, F, cx, cy, zf):
    _lift(wardrobe)(mi, F, cx, cy, math.pi, z=zf)


def rug_z(mi, F, cx, cy, lx, ly, zf):
    _lift(rug)(mi, F, cx, cy, lx, ly, z=zf)


def desk_z(mi, F, cx, cy, zf):
    _lift(table)(mi, F, cx, cy, 2.2, 5.0, 2.9, z=zf)
    _lift(chair)(mi, F, cx + 2.1, cy, math.pi, z=zf)
    candle(mi, F, cx, cy - 1.6, zf + 2.9, 1.0)
    tb(mi, F, cx, cy + 0.6, zf + 2.9, 1.4, 2.0, 0.3, M_CLOTH, 0.04)       # livro aberto (capa)
    tb(mi, F, cx, cy + 0.6, zf + 3.2, 1.2, 1.8, 0.08, M_PL, 0.0)          # folhas


def craft_bench(mi, F, nm, cx, cy):
    """bancada do oficio da casa (dirigida): ferreiro = bigorna, tenaz e martelo; boticario = frascos e pilao;
    cartografo = mapa enrolado e compasso; mestre de armas = cabide de espadas"""
    S = Sub(cx, cy, math.pi)
    sbox(mi, F, S, 0, 0, FLOOR + 3.3, 5.2, 1.9, 0.3, WOOD, 0.06)
    for ku in (-1, 1):
        for kv in (-1, 1):
            sbox(mi, F, S, ku * 2.2, kv * 0.65, FLOOR, 0.4, 0.4, 3.3, WOOD, 0.04)
    sbox(mi, F, S, 0, 0, FLOOR + 0.8, 4.6, 1.5, 0.16, WOOD, 0.02)          # prateleira de baixo
    if nm == "H2":
        x, y = S.xy(-1.2, 0.0)
        p = F.p(x, y, FLOOR)
        tb(mi, F, x, y, FLOOR, 1.1, 1.1, 2.0, WOOD, 0.06)                   # cepo
        tb(mi, F, x, y, FLOOR + 2.0, 1.9, 0.8, 0.5, M_JNT, 0.05)             # bigorna
        tb(mi, F, x, y, FLOOR + 2.5, 1.2, 0.7, 0.3, M_JNT, 0.05)
        for u in (0.6, 1.4):
            a = F.p(*S.xy(u, 0.2), z=FLOOR + 3.62)
            b = F.p(*S.xy(u + 0.1, -0.6), z=FLOOR + 3.62)
            mi.beam(a, b, 0.16, 0.12, WOOD, 0.0)
            mi.box((0.5, 0.3, 0.3), a, (0, 0, S.a), M_JNT, 0.04)
    elif nm == "H3":
        for j, u in enumerate((-1.8, -1.0, -0.2, 0.8)):
            p = F.p(*S.xy(u, 0.2), z=FLOOR + 3.6)
            V._lathe(mi, (p.x, p.y, p.z), [(0.26, 0.0), (0.3, 0.6), (0.1, 0.85), (0.1, 1.1), (0.0, 1.1)],
                     M_CLOTH if j % 2 else M_JNT, 6)
        p = F.p(*S.xy(1.8, 0.0), z=FLOOR + 3.6)
        V._lathe(mi, (p.x, p.y, p.z), [(0.45, 0.0), (0.5, 0.5), (0.4, 0.7), (0.0, 0.7)], M_DRESS, 8)   # pilao
    elif nm == "H5":
        a = F.p(*S.xy(-1.8, 0.2), z=FLOOR + 3.85)
        b = F.p(*S.xy(0.6, 0.2), z=FLOOR + 3.85)
        mi.rod(a, b, 0.25, M_PL, 8)                                          # mapa enrolado
        tb(mi, F, *S.xy(1.4, -0.1), FLOOR + 3.6, 1.8, 1.3, 0.06, M_PL, 0.0, S.a)   # folha aberta
        candle(mi, F, *S.xy(2.2, 0.5), FLOOR + 3.6, 1.0)
    else:
        for u in (-1.6, -0.5, 0.6):
            a = F.p(*S.xy(u, 0.55), z=FLOOR + 3.6)
            mi.beam(a, a + Vector((0, 0, 4.2)), 0.2, 0.08, M_JNT, 0.0)       # laminas encostadas
            mi.box((0.9, 0.2, 0.2), a + Vector((0, 0, 1.0)), (0, 0, S.a), WOOD, 0.02)
        chest(mi, F, *S.xy(1.6, 0.0), S.a, 1.6, 1.4, 1.2)


def furnish_b(mi, F, area, hrec, spec, info, iw, idp, h0, zf):
    z = 0.0
    """taverna: balcao com tampo e frente almofadada, prateleiras de garrafas e barris deitados atras; 5 mesas com
    banquetas; lustre de ferro com velas pendurado no vazio; no mezanino 2 camas, baus e uma mesa"""
    # balcao (onda 0: 12 x 2,2 x 3,6 em (8, 6,5))
    bx, by = 8.0, 6.5
    tb(mi, F, bx, by, FLOOR, 12.0, 2.0, 3.3, WOOD, 0.04)
    tb(mi, F, bx, by, FLOOR + 3.3, 12.4, 2.6, 0.32, WOOD, 0.08)
    for j in range(6):
        tb(mi, F, bx - 5.0 + 2.0 * j, by - 1.05, FLOOR + 0.6, 1.5, 0.12, 2.2, WOOD, 0.04)       # almofadas
    tb(mi, F, bx, by - 1.1, FLOOR, 12.2, 0.3, 0.35, M_DRESS, 0.03)                               # rodape de pedra
    lcol(area, F, bx, by, 0.0, 12.4, 2.6, 3.6)
    for j, u in enumerate((-4.0, -2.2, 3.0)):
        p = F.p(bx + u, by, FLOOR + 3.62)
        V._lathe(mi, (p.x, p.y, p.z), [(0.36, 0.0), (0.38, 0.8), (0.0, 0.8)], WOOD, 6)          # canecas
    # atras do balcao: estante de garrafas na parede da frente e barris deitados em berco
    shelf(mi, F, bx - 1.0, idp / 2 - 0.8, math.pi, 8.0, 7.0, 1.4, items="bottles")
    for j, xx in enumerate((12.4, 15.2)):
        tb(mi, F, xx, idp / 2 - 1.6, FLOOR, 2.6, 2.4, 0.6, WOOD, 0.04)
        barrel(mi, F, xx, idp / 2 - 1.6, z0=FLOOR + 0.6, r=1.15, h=2.4, lying=True, yaw=math.pi / 2)
    # mesas redondas com banquetas
    table(mi, F, -10.4, 10.9, 8.0, 2.6, 3.4)                     # mesa comprida sob a janela
    lcol(area, F, -10.4, 10.9, 0.0, 8.0, 2.6, 3.6)
    bench(mi, F, -10.4, 8.6, 7.0)
    for (cx, cy) in ((4.5, -2.5), (11.5, -2.5), (8.0, 1.8)):
        p = F.p(cx, cy, FLOOR)
        mi.cyl(1.9, 0.3, (p.x, p.y, p.z + 3.1), m=WOOD, n=8, bevel=0.06)
        mi.cyl(0.35, 2.95, (p.x, p.y, p.z + 1.6), m=WOOD, n=5, bevel=0.0)
        mi.cyl(1.0, 0.22, (p.x, p.y, p.z + 0.11), m=WOOD, n=6, bevel=0.0)
        lcol(area, F, cx, cy, 0.0, 3.0, 3.0, 3.4)
        for k in range(3):
            a = 2 * math.pi * k / 3 + 0.5
            stool(mi, F, cx + 3.0 * math.cos(a), cy + 3.0 * math.sin(a))
        V._lathe(mi, tuple(F.p(cx + 0.5, cy, FLOOR + 3.4)), [(0.34, 0.0), (0.36, 0.7), (0.0, 0.7)], WOOD, 6)
    # lustre de ferro com velas (no vazio do mezanino)
    vx0, vy0, vx1, vy1 = spec["void"]
    lx, ly = (vx0 + vx1) / 2, (vy0 + vy1) / 2
    zl = zf + 4.0
    p = F.p(lx, ly, zl)
    V._lathe(mi, (p.x, p.y, p.z), [(3.2, 0.0), (3.4, 0.2), (3.2, 0.4), (2.9, 0.2)], M_JNT, 12, closed=True)
    for k in range(8):
        a = 2 * math.pi * k / 8
        cx, cy = lx + 3.2 * math.cos(a), ly + 3.2 * math.sin(a)
        candle(mi, F, cx, cy, zl + 0.4, 1.2)
    for k in range(3):
        a = 2 * math.pi * k / 3
        mi.rod((p.x + 3.1 * math.cos(a), p.y + 3.1 * math.sin(a), p.z + 0.3), (p.x, p.y, p.z + 4.2), 0.06, M_JNT, 4)
    gy = (ly / V.K) if not info["gf"] else (-lx / V.K)
    ztop = F.o.z + info["zboard"](gy) if "zboard" in info else p.z + 8.0
    mi.rod((p.x, p.y, p.z + 4.2), (p.x, p.y, ztop), 0.12, M_JNT, 4)
    # mezanino: 2 camas na parede da direita, baus, mesa e 2 cadeiras no fundo
    for yy in (8.7, 2.4):
        _lift(bed)(mi, F, iw / 2 - 4.6, yy, math.pi / 2, z=zf)
        lcol(area, F, iw / 2 - 4.6, yy, zf, 9.0, 5.2, 2.2)
        _lift(chest)(mi, F, iw / 2 - 10.7, yy, math.pi / 2, 1.6, 3.0, 1.8, z=zf)


def furnish_c(mi, F, area, hrec, spec, info, iw, idp, h0, zf):
    nm = hrec[0]
    if nm == "H4":
        # OFICINA DO MINERADOR: bancada no fundo (torno, ferramentas, lanterna), cabide de picaretas na parede da
        # direita, carrinho de mina (vazio, coberto com lona) sobre um trecho de trilho, barris e caixotes
        S = Sub(1.0, -idp / 2 + 1.0, 0.0)
        sbox(mi, F, S, 0, 0, FLOOR + 3.3, 11.0, 1.9, 0.32, WOOD, 0.06)
        for u in (-5.1, -1.7, 1.7, 5.1):
            sbox(mi, F, S, u, 0, FLOOR, 0.45, 1.6, 3.3, WOOD, 0.04)
        sbox(mi, F, S, 0, 0.1, FLOOR + 0.9, 10.2, 1.5, 0.16, WOOD, 0.02)
        lcol(area, F, 1.0, -idp / 2 + 1.0, 0.0, 11.0, 1.9, 3.6)
        # torno de bancada e ferramentas
        x, y = S.xy(-3.8, 0.3)
        tb(mi, F, x, y, FLOOR + 3.62, 1.2, 0.8, 0.8, M_JNT, 0.05)
        rod(mi, F, (x, y + 0.6, FLOOR + 4.1), (x, y - 0.6, FLOOR + 4.1), 0.07, M_JNT, 4)
        for u in (-1.2, 0.2):
            a = F.p(*S.xy(u, 0.2), z=FLOOR + 3.66)
            mi.beam(a, F.p(*S.xy(u + 1.2, 0.0), z=FLOOR + 3.66), 0.18, 0.14, WOOD, 0.0)
            mi.box((0.3, 0.6, 0.3), a, (0, 0, S.a), M_JNT, 0.03)
        # quadro de ferramentas na parede do fundo (tabua + ganchos)
        tb(mi, F, 1.0, -idp / 2 + 0.12, FLOOR + 4.6, 6.4, 0.24, 3.4, WOOD, 0.03)
        for j, u in enumerate((-2.4, -1.2, 0.0, 1.2, 2.4)):
            x = 1.0 + u
            rod(mi, F, (x, -idp / 2 + 0.3, FLOOR + 7.4), (x, -idp / 2 + 0.3, FLOOR + 5.2 + 0.4 * (j % 2)), 0.1, WOOD, 4)
            tb(mi, F, x, -idp / 2 + 0.3, FLOOR + 5.0 + 0.4 * (j % 2), 0.9 if j % 2 else 0.5, 0.2, 0.4, M_JNT, 0.02)
        # lanterna de oficina pendurada na linha da tesoura
        tz = [t for t in info.get("trusses", [])]
        if tz:
            xt, ztie = min(tz, key=lambda t: abs(t[0] * V.K + 4.0))
            lantern(mi, F, 1.0, xt * V.K if info["gf"] else -3.0, ztie * V.K, 5.0)
        else:
            lantern(mi, F, 1.0, -4.0, info["ze"] * V.K, 5.0)
        # cabide de picaretas (parede da direita)
        xr = iw / 2 - 0.2
        tb(mi, F, xr, -4.6, FLOOR + 6.2, 0.3, 5.0, 0.5, WOOD, 0.04)
        for j, yy in enumerate((-6.2, -3.2)):
            pickaxe(mi, F, xr - 0.45, yy, FLOOR + 6.4, big=(j % 2 == 0))
        # carrinho de mina sobre trilho curto
        ore_cart(mi, F, 6.0, 1.0)
        lcol(area, F, 6.0, 1.0, 0.0, 3.2, 5.0, 3.4)
        for (cx, cy) in ((-5.5, 5.0), (-3.2, 5.6)):
            barrel(mi, F, cx, cy)
        crate(mi, F, 8.8, -3.4, s=2.2)
        crate(mi, F, 8.8, -3.4, z0=FLOOR + 2.2, s=1.8, yaw=0.3)
        lcol(area, F, 8.8, -3.4, 0.0, 2.4, 2.4, 4.0)
    else:
        # CASA DA GUARDA (simples): cama em ALCOVA (tabique de madeira + cortina), mesa com 2 cadeiras, cabide de
        # lancas e escudos, bau, prateleira
        bed(mi, F, 8.0, -3.4, 0.0)
        lcol(area, F, 8.0, -3.4, 0.0, 5.2, 9.0, 2.2)
        # tabique da alcova (x 5,0) com a cortina aberta
        tb(mi, F, 5.0, -3.8, FLOOR, 0.4, 8.4, 8.0, WOOD, 0.04)
        tb(mi, F, 7.9, 0.5, FLOOR + 7.6, 6.2, 0.4, 0.4, WOOD, 0.03)
        tb(mi, F, 5.8, 0.55, FLOOR + 0.4, 1.1, 0.2, 7.2, M_CLOTH, 0.05)
        lcol(area, F, 5.0, -3.8, 0.0, 0.4, 8.4, 8.0)
        table(mi, F, 1.4, 0.4, 6.0, 3.0, 3.4)
        lcol(area, F, 1.4, 0.4, 0.0, 6.0, 3.0, 3.4)
        for cx, cy, yw in ((0.0, -1.9, math.pi / 2), (2.8, 2.7, -math.pi / 2)):
            chair(mi, F, cx, cy, yw)
        candle(mi, F, 1.4, 0.4, FLOOR + 3.4, 1.2)
        # cabide de lancas na parede da frente (lado esquerdo da porta) e escudos
        yr = idp / 2 - 0.35
        tb(mi, F, -7.2, yr, FLOOR + 1.0, 4.4, 0.4, 0.4, WOOD, 0.03)
        tb(mi, F, -7.2, yr, FLOOR + 6.4, 4.4, 0.4, 0.4, WOOD, 0.03)
        for j, xx in enumerate((-8.8, -7.7, -6.6, -5.5)):
            rod(mi, F, (xx, yr - 0.2, FLOOR + 0.6), (xx, yr - 0.2, FLOOR + 9.4), 0.1, WOOD, 4)
            p = F.p(xx, yr - 0.2, FLOOR + 9.4)
            V._lathe(mi, (p.x, p.y, p.z), [(0.18, 0.0), (0.2, 0.2), (0.0, 1.0)], M_JNT, 4)
        for yy in (-5.2, 6.0):
            p = F.p(-iw / 2 + 0.4, yy, FLOOR + 6.4)
            mi.cyl(1.2, 0.3, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_CLOTH, n=10, bevel=0.05)
            mi.cyl(0.35, 0.36, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_JNT, n=8, bevel=0.03)
        chest(mi, F, -2.5, -idp / 2 + 1.2, 0.0, 3.2, 1.8, 2.0)
        shelf(mi, F, iw / 2 - 0.8, 4.2, math.pi / 2, 4.2, 6.5, 1.4, items="pots")
        lcol(area, F, iw / 2 - 0.8, 4.2, 0.0, 1.4, 4.2, 6.5)


def pickaxe(mi, F, x, y, z, big=True):
    """picareta pendurada pela cabeca: cabo de madeira para baixo, cabeca de ferro curva em 2 pontas"""
    ln = 4.2 if big else 3.4
    rod(mi, F, (x, y, z), (x, y, z - ln), 0.14, WOOD, 6)
    a = F.p(x, y - 1.3, z - 0.25)
    b = F.p(x, y + 1.3, z - 0.25)
    c = F.p(x, y, z + 0.1)
    mi.beam(a, c, 0.24, 0.3, M_JNT, 0.0)
    mi.beam(c, b, 0.24, 0.3, M_JNT, 0.0)
    tb(mi, F, x, y, z - 0.25, 0.42, 0.5, 0.5, M_JNT, 0.04)


def ore_cart(mi, F, cx, cy):
    """carrinho de mina de madeira com cintas de ferro, 4 rodas com aro, puxador, carga coberta por LONA (sem
    minerio a vista) sobre 2 trilhos e dormentes"""
    for yy in (-2.8, -1.4, 0.0, 1.4, 2.8):
        tb(mi, F, cx, cy + yy, FLOOR, 3.6, 0.6, 0.2, WOOD, 0.03)
    for s in (-1, 1):
        tb(mi, F, cx + s * 1.0, cy, FLOOR + 0.2, 0.24, 7.0, 0.22, M_JNT, 0.02)
    zb = FLOOR + 1.3
    tb(mi, F, cx, cy, zb, 2.8, 4.4, 0.25, WOOD, 0.04)
    for s in (-1, 1):
        tb(mi, F, cx + s * 1.3, cy, zb + 0.25, 0.25, 4.4, 1.8, WOOD, 0.04)
        tb(mi, F, cx, cy + s * 2.1, zb + 0.25, 2.8, 0.25, 1.8, WOOD, 0.04)
        for yy in (-1.3, 1.3):
            tb(mi, F, cx + s * 1.44, cy + yy, zb + 0.1, 0.06, 0.3, 2.0, M_JNT, 0.0)
    tb(mi, F, cx, cy, zb + 1.9, 2.7, 4.3, 0.5, M_CLOTH, 0.25)                       # lona
    for sx in (-1, 1):
        for sy in (-1, 1):
            p = F.p(cx + sx * 1.0, cy + sy * 1.4, FLOOR + 0.42 + 0.72)
            mi.cyl(0.72, 0.26, (p.x, p.y, p.z), (0, math.pi / 2, F.a), M_JNT, n=10, bevel=0.03)
            mi.cyl(0.3, 0.34, (p.x, p.y, p.z), (0, math.pi / 2, F.a), WOOD, n=6, bevel=0.0)
    bm_(mi, F, (cx, cy + 2.2, zb + 0.9), (cx, cy + 3.4, zb + 1.2), 0.2, 0.2, M_JNT)


def lantern(mi, F, x, y, ztop, drop):
    """lanterna de oficina pendurada: corrente, tampa, gaiola de ferro de 4 montantes e o nucleo quente"""
    p = F.p(x, y, ztop)
    zb = ztop - drop
    mi.rod((p.x, p.y, ztop), (p.x, p.y, zb + 1.3), 0.05, M_JNT, 4)
    V._lathe(mi, (p.x, p.y, zb + 1.0), [(0.62, 0.0), (0.2, 0.3), (0.0, 0.34)], M_JNT, 6)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        mi.box((0.1, 0.1, 1.0), (p.x + 0.45 * math.cos(a), p.y + 0.45 * math.sin(a), zb + 0.5), (0, 0, a), M_JNT, 0.0)
    mi.box((0.9, 0.9, 0.14), (p.x, p.y, zb + 0.07), (0, 0, F.a), M_JNT, 0.02)
    V._lathe(mi, (p.x, p.y, zb + 0.14), [(0.22, 0.0), (0.26, 0.4), (0.0, 0.72)], M_ROOM, 6)
