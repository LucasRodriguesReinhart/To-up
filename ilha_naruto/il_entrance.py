# il_entrance - Ilha 1 (Naruto / Vila da Folha): ENTRADA (substitui il_blockout.entrance()).
#   1. Ponte de chegada (y L.LOBBY_Y -> L.ISLAND_S_Y, piso em L.G): tabuleiro de lajes transversais, meio-fio de pedra,
#      guarda-corpo de madeira (postes escuros, travessas claras), 8 LANTERNAS DE POSTE (padrao EXIT_Rails) nas
#      pilastras de y -182/-166/-150/-134 dos 2 lados, viaduto de 3 arcos de pedra; os pilares descem ate z -56
#      (talude + sapata) e assentam em PILHAS DE ROCHA que sobem do mar (a do pilar 3 funde com o penhasco da ilha);
#      2 pilaretes com giboshi dourado em cada ponta.                                                  (02_TERRAIN)
#   2. Patamar de chegada ate a borda alargada (x +-24) + passagem do portao + praca: lajes irregulares sobre
#      rejunte escuro (o patamar fecha o recorte do terreno), 4 toro nos cantos da praca.                (02_TERRAIN)
#   3. PORTAO PRINCIPAL (peca-heroi): 4 pilares de laca vermelha em sapatas de pedra, verga + frisos, misulas e
#      caibros, telhado de quatro aguas em telha verde vidrada em 2 niveis (UM tom: UV constante; peca escura so em
#      cumeeira, espigoes e testeira), placa com a folha em espiral (frente e verso), 2 lanternas de papel na verga,
#      alas de reboco creme emolduradas de vermelho sobre base de pedra e telhadinhos proprios, folhas do portao
#      ABERTAS encostadas nas alas (lado da praca).                                                     (04_VILLAGE)
#   4. 2 estandartes PENDURADOS nos pilares externos das alas (braco de ferro em G+14, pano 3 x 9), sem mastro:
#      a torre do summon fica livre vista da ponte (0, -160, 17).                                        (04_VILLAGE)
#   5. 2 leoes guardioes (il_lion, compartilhado com o portao DB) nos pedestais de L.LIONS, olhando para a ponte,
#      pata de fora na esfera; mureta baixa leao -> ala.                                                (04_VILLAGE)
# Regras da rodada 2 (RMB): bevel 0 se a menor dimensao < 1,0, senao <= 5%; nada com todas as dimensoes < 0,35;
# folga >= 0,1 entre faces de materiais diferentes; frisos/relevos com secao >= 0,3.
# Nada no eixo x = 0 entre a ponte e a escada do anel (vista do WORLD_ENTRY_Naruto livre).
import math
import random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, D, S, col_box, col_box2, light
import il_layout as L
import fm_lib
import fm_parts as FP
import fm_portal_kit as K
import fm_pv3_naruto as PN          # leaf_symbol: a folha de Konoha (espiral + ponta + talo) do portal do lobby
import il_lion                      # leao guardiao compartilhado (dono: esta zona)

# ------------------------------------------------------------------ materiais novos da zona (4 de 4)
_M = fm_lib.MATS.setdefault
_M("Stone_EntLion", (S(112, 116, 126), 0.85, 0.0, 0, None, 0.12))       # corpo dos leoes (cinza frio, mais escuro)
_M("Stone_EntLionMane", (S(172, 175, 184), 0.85, 0.0, 0, None, 0.12))   # juba/cachos/esfera dos leoes (claro frio)
_M("Roof_EntJadeDark", (S(38, 76, 54), 0.55, 0.0, 0, None, 0.08))       # cumeeira/espigao/testeira da telha verde
_M("Cloth_EntRed", (S(182, 34, 32), 0.9, 0.0, 0, None, 0.06))           # pano dos estandartes

G = L.G
HW = L.BRIDGE_W / 2.0             # 12: meia-largura caminhavel (= ponte do lobby)
CURB = 1.4                        # meio-fio de pedra sob o guarda-corpo (x 12..13.4)
XO = HW + CURB                    # face externa do tabuleiro / do viaduto
Y0, Y1 = L.LOBBY_Y, L.ISLAND_S_Y  # -198 (patamar do lobby) .. -118 (borda da ilha)
DECK_B = G - 2.8                  # fundo do tabuleiro
PIER_T = 5.0                      # espessura (y) dos pilares
SPAN = (Y1 - (Y0 + PIER_T) - 2 * PIER_T) / 3.0      # vao livre de cada arco (3 arcos iguais)
PIERS = [Y0 + PIER_T / 2 + i * (SPAN + PIER_T) for i in range(3)]
ARCH_R = SPAN / 2.0
Z_SPRING = DECK_B - 1.0 - ARCH_R  # nascente dos arcos (fecho 1 abaixo do tabuleiro)
PIER_FOOT = -56.0                 # sapata dos pilares (assenta na pilha de rocha que sobe do mar)
LANTERN_Y = [-182.0, -166.0, -150.0, -134.0]   # lanternas de poste a cada 16 nos 2 lados (8 no total)

GY = L.GATE_Y
OW = L.GATE_OPEN_W / 2.0          # 10
OH = L.GATE_OPEN_H                # 18
GHW = L.GATE_W / 2.0              # 26
XP = 12.2                         # eixo dos pilares centrais (face interna em x 10.4)
XQ = GHW - 1.4                    # eixo dos pilares externos (24.6)
BANNER_Z = G + 14.0               # braco de ferro dos estandartes (pilar externo da ala)
BANNER_W, BANNER_H = 3.0, 9.0     # pano (largura x altura total com a ponta)
ZW = G + L.GATE_OPEN_H - 0.2      # topo das paredes das alas (frechal): telhadinho logo abaixo da verga

PAVE, SL, SD = "Stone_Paving_Warm", "Stone_Wall_Light", "Stone_Wall_Dark"
RED, DARK, GOLD, CREAM = "Wood_Lacquer_Red", "Wood_Dark", "Metal_Gold", "Plaster_Cream"
IRON = "Metal_Iron"
TILE, TILED, GLOW, LION = "Roof_Green", "Roof_EntJadeDark", "Lantern_Glow", "Stone_EntLion"
MANE = "Stone_EntLionMane"

# cameras de revisao 360 (frente, 3/4, tras, 2 lados, altura do jogador)
CAMS = {
    "CAM_Entrance_Bridge": ((0.0, -210.0, G + 11.0), (0.0, -112.0, G + 13.0), 22),
    "CAM_Entrance_Gate34": ((-38.0, -150.0, G + 13.0), (2.0, -110.0, G + 15.0), 24),
    "CAM_Entrance_Back": ((6.0, -72.0, L.RING + 7.0), (0.0, -114.0, G + 14.0), 22),
    "CAM_Entrance_Player": ((3.5, -146.0, G + 4.8), (0.0, -108.0, G + 9.5), 22),
    "CAM_Entrance_SideE": ((82.0, -150.0, G + 16.0), (0.0, -142.0, G - 8.0), 20),
    "CAM_Entrance_SideW": ((-76.0, -112.0, G + 22.0), (0.0, -128.0, G + 2.0), 22),
    "CAM_Entrance_Lion": ((7.0, -130.0, G + 7.5), (18.0, -115.5, G + 7.0), 30),
}


# QA (il_qa): sondas de borda do patamar de chegada (entre a ponte e os leoes a guarda invisivel da borda tem que
# segurar) e das mureta leao -> ala; rota da ponte ate o pe da escada do anel pelo eixo e pela lateral do patamar
EXTRA_PROBES = [
    ("ENT_patamar_frente_L", 15.6, -117.2, L.G, 0.0, -1.0),
    ("ENT_patamar_frente_O", -15.6, -117.2, L.G, 0.0, -1.0),
    ("ENT_mureta_leao_L", 16.0, -112.5, L.G, 1.0, 0.0),
    ("ENT_mureta_leao_O", -16.0, -112.5, L.G, -1.0, 0.0),
]
EXTRA_ROUTES = {
    "ponte->patamar_lateral->praca": ([(0.0, -150.0), (0.0, -121.0), (8.0, -117.0), (15.0, -116.0), (15.0, -114.8),
                                        (9.0, -114.8), (0.0, -106.0), (0.0, -94.0)], L.G),
}


def rule_bevel(dims, bevel):
    """regra da rodada 2: bevel 0 se a menor dimensao < 1,0; senao no maximo 5% da menor dimensao"""
    mn = min(dims)
    if not bevel or mn < 1.0:
        return 0.0
    return min(bevel, 0.05 * mn)


class RMB(MB):
    """MB com as regras da rodada 2 (critica tecnica): microchanfro controlado (rule_bevel) e nada com TODAS as
    dimensoes < 0,35 (a peca e descartada). flat=False; vcap=1 = sem variantes tonais (1 MeshPart por material)."""
    skipped = 0

    def __init__(self, name, collection, rng=None, detail="hero", floor=None, vcap=None):
        MB.__init__(self, name, collection, rng, detail, floor)
        self.vcap = vcap

    def _family(self, m):
        if self.vcap == 1:
            return None
        return MB._family(self, m)

    def box(self, size, loc, rot=(0, 0, 0), m="Stone_Light", bevel=0.12, seg=1, tint=None):
        if max(size) < 0.35:
            RMB.skipped += 1
            return
        MB.box(self, size, loc, rot, m, rule_bevel(size, bevel), seg, tint)

    def beam(self, a, b, w, h=None, m="Wood_Dark", bevel=0.08, roll=0.0, tint=None):
        dims = ((Vector(b) - Vector(a)).length, w, h or w)
        if max(dims) < 0.35:
            RMB.skipped += 1
            return
        MB.beam(self, a, b, w, h, m, rule_bevel(dims, bevel), roll, tint)

    def cyl(self, r, h, loc, rot=(0, 0, 0), m="Metal_Iron", n=12, r2=None, bevel=0.08, seg=1, caps=True, tint=None,
            angle=0.5):
        rmin = r if r2 is None else min(r, r2)
        if max(2 * max(r, r2 or 0.0), h) < 0.35:
            RMB.skipped += 1
            return
        MB.cyl(self, r, h, loc, rot, m, n, r2, rule_bevel((2 * rmin, h), bevel), seg, caps, tint, angle)


def NMB(name, collection, rng=None, detail="hero"):
    """RMB sem variantes tonais: 1 MeshPart por material (portao/leoes tem muitas pecas pequenas repetidas)"""
    return RMB(name, collection, rng, detail, vcap=1)


def flat_mats(mb, mats, smooth=False):
    """UV constante (texel neutro da textura de detalhe) em todas as faces desses materiais: o material le como UM
    tom (a textura de telha pintava um codigo de barras nas fiadas vistas de cima)"""
    idx = {i for i, m in enumerate(mb.mats) if (m[1] if isinstance(m, tuple) else m) in mats}
    il_lion.flatten(mb, [f for f in mb.bm.faces if f.material_index in idx], smooth)


# ================================================================== PONTE + PRACA (02_TERRAIN)
def deck_paving(mb, rng):
    """lajes transversais (2-3 por fiada, juntas desencontradas), topo em G"""
    y = Y0
    while y < Y1 - 0.3:
        d = min(rng.uniform(2.3, 3.0), Y1 - y)
        n = 3 if rng.random() < 0.55 else 2
        if n == 2:
            xs = [-HW, rng.uniform(-3.5, 3.5), HW]
        else:
            xs = [-HW, -HW / 3 + rng.uniform(-1.6, 1.6), HW / 3 + rng.uniform(-1.6, 1.6), HW]
        for xa, xb in zip(xs, xs[1:]):
            h = 0.45 + rng.uniform(-0.03, 0.0)
            mb.box((xb - xa - 0.18, d - 0.18, h), ((xa + xb) / 2, y + d / 2, G - h / 2),
                   (0, 0, rng.uniform(-0.004, 0.004)), PAVE, 0.12)
        y += d


def curbs(mb, rng):
    for s in (-1, 1):
        y = Y0
        zt = G + 0.55
        while y < Y1 - 0.1:
            ln = min(rng.uniform(5.5, 7.5), Y1 - y)
            if Y1 - (y + ln) < 2.0:
                ln = Y1 - y
            mb.box((CURB, ln - 0.08, zt - DECK_B), (s * (HW + CURB / 2), y + ln / 2, (DECK_B + zt) / 2), (0, 0, 0),
                   SL, 0.12)
            y += ln
        # capa corrida escura sobre o meio-fio (le como mureta continua, nao como ameias)
        mb.box((1.5, Y1 - Y0, 0.32), (s * (HW + 0.75), (Y0 + Y1) / 2, zt + 0.16), (0, 0, 0), SD, 0.1)
        # cornija escura no pe do tabuleiro (linha que separa o tabuleiro do viaduto)
        mb.box((1.3, Y1 - Y0, 0.6), (s * (XO - 0.25), (Y0 + Y1) / 2, DECK_B - 0.3), (0, 0, 0), SD, 0.1)


def pilaster(mb, s, y, top):
    """pilastra de pedra no alinhamento do guarda-corpo (projeta para fora do tabuleiro) + misula por baixo"""
    x = s * 13.2
    mb.box((2.2, 2.2, top - (DECK_B - 0.6)), (x, y, (top + DECK_B - 0.6) / 2), (0, 0, 0), SL, 0.18)
    mb.box((2.6, 2.6, 0.4), (x, y, top + 0.2), (0, 0, 0), SD, 0.1)
    FP.frustum(mb, (s * 13.6, y, DECK_B - 2.6), 0.4, 1.2, 1.3, 2.2, 2.0, SD, top_off=(s * 0.05, 0.0))


def railing(mb, s, stops):
    """guarda-corpo de madeira sobre o meio-fio: postes escuros a cada ~4, travessas claras corridas entre as pilastras"""
    x = s * (HW + 0.7)
    zb = G + 0.7
    for ya, yb in zip(stops, stops[1:]):
        ya, yb = ya + 1.1, yb - 1.1           # faces das pilastras
        n = max(1, int(round((yb - ya) / 4.0)))
        for i in range(1, n):
            y = ya + (yb - ya) * i / n
            mb.box((0.8, 0.8, 3.3), (x, y, zb + 1.65), (0, 0, 0), DARK, 0.1)
            mb.box((1.05, 1.05, 0.3), (x, y, zb + 3.45), (0, 0, 0), DARK, 0.08)
        mb.beam((x, ya - 0.1, zb + 3.0), (x, yb + 0.1, zb + 3.0), 0.5, 0.45, "Wood_Light", 0.08)
        mb.beam((x, ya - 0.1, zb + 1.6), (x, yb + 0.1, zb + 1.6), 0.4, 0.35, "Wood_Light", 0.05)


def viaduct(mb):
    """3 arcos de pedra (semicirculo) + pilares descendo ao vazio; o solido do timpano e a propria abobada"""
    ux, uz = (0, 1, 0), (0, 0, 1)
    n = 12
    for i in range(3):
        ya = Y0 + PIER_T + i * (SPAN + PIER_T)
        ym = ya + SPAN / 2
        pts = [(ym - ARCH_R * math.cos(math.pi * k / n), Z_SPRING + ARCH_R * math.sin(math.pi * k / n))
               for k in range(n + 1)]
        for (y0, z0), (y1, z1) in zip(pts, pts[1:]):
            K.plate(mb, [(y0, z0), (y1, z1), (y1, DECK_B + 0.05), (y0, DECK_B + 0.05)], (0, 0, 0), ux, uz, 2 * XO, SL)
        for s in (-1, 1):
            FP.arch(mb, (s * (XO + 0.05), ym, 0.0), math.pi / 2, SPAN, Z_SPRING, ARCH_R, 0.9, SD, SL, n=11, band=1.4)
    for k, yc in enumerate(PIERS):
        zf = PIER_FOOT
        mb.box((2 * XO, PIER_T, DECK_B - (zf + 5.0)), (0, yc, (DECK_B + zf + 5.0) / 2), (0, 0, 0), SL, 0.2)
        # faixa escura na nascente dos arcos + pilastras laterais (ritmo vertical do viaduto)
        mb.box((2 * XO + 0.8, PIER_T + 0.8, 0.8), (0, yc, Z_SPRING - 0.4), (0, 0, 0), SD, 0.12)
        for s in (-1, 1):
            mb.box((0.6, PIER_T - 1.0, Z_SPRING - 0.8 - (zf + 6.0)), (s * (XO + 0.3), yc, (Z_SPRING - 0.8 + zf + 6.0) / 2),
                   (0, 0, 0), SL, 0.1)
        # pe do pilar: talude (alarga para baixo) + sapata escura assentada na pilha de rocha
        FP.frustum(mb, (0, yc, zf + 0.6), 2 * XO + 3.0, PIER_T + 3.0, 2 * XO, PIER_T, 5.4, SL)
        mb.box((2 * XO + 3.8, PIER_T + 3.8, 1.4), (0, yc, zf - 0.1), (0, 0, 0), SD, 0.07)
    # encontro norte (a abobada do 3o arco nasce na alvenaria encostada no penhasco)    # encontro norte (a abobada do 3o arco nasce na alvenaria encostada no penhasco)
    mb.box2((-XO, Y1 - 0.6, Z_SPRING - 10.0), (XO, Y1 + 5.0, DECK_B), SL, 0.2)


# pilhas de rocha sob os pilares (rodada 2): nada de ponta de rocha no ar. Cada pilar desce ate PIER_FOOT e assenta
# numa pilha de rocha que sobe do mar (z -114, o pe dos penhascos da ilha); a do pilar 3 encosta no penhasco da
# ilha (y -135 abaixo de z -20) e se funde com ele; a do pilar 1 (junto ao lobby) inclina para a ilha.
STACKS = [  # (y do pe, inclinacao do topo em y, semi-eixos do topo (x, y), escala do pe)
    (-190.5, -5.0, (16.8, 6.4), 1.3),
    (-166.5, -2.3, (16.6, 6.2), 1.3),
    (-139.0, -3.2, (17.0, 7.0), 1.25),
]


def stacks(mb, rng):
    zt = PIER_FOOT - 0.75
    for k, (yb, lean, (ax, ay), sc) in enumerate(STACKS):
        poly = FP._rock_poly(ax * sc, ay * sc, 10, rng, ex=2.6, jit=0.07, a0=0.15)
        FP.rock_column(mb, Vector((0.0, yb, 0.0)), poly, -114.0, zt, rng, "Cliff_Rock_Tan", taper=1.0 / sc, rings=4,
                       jitter=0.09, tilt=0.0, lean=(0.0, lean), chamfer=0.9)
        # 2 massas laterais mais baixas (quebram a silhueta: a pilha nao e um cone liso)
        for sx in (-1, 1):
            q = FP._rock_poly(rng.uniform(4.5, 6.0), rng.uniform(4.0, 5.5), 7, rng, ex=2.3, jit=0.1)
            FP.rock_column(mb, Vector((sx * ax * 0.95, yb + rng.uniform(-2.0, 2.0), 0.0)), q, -114.0,
                           zt - rng.uniform(9.0, 22.0), rng, "Cliff_Rock_Tan_Dark" if (k + sx) % 2 else "Cliff_Rock_Tan",
                           taper=0.62, rings=2, jitter=0.1, tilt=0.06, chamfer=0.6)


def post_lantern(mb, x, y, zb):
    """lanterna de poste de pedra (padrao das lanternas da ponte de saida, EXIT_Rails): fuste, prato, camara acesa
    com 4 montantes, tampa e chapeu piramidal. zb = topo da pilastra."""
    mb.box((1.3, 1.3, 2.6), (x, y, zb + 1.3), (0, 0, 0), SL, 0.0)
    mb.box((1.8, 1.8, 0.36), (x, y, zb + 2.6 + 0.18), (0, 0, 0), SD, 0.0)
    mb.box((1.0, 1.0, 1.5), (x, y, zb + 2.96 + 0.65), (0, 0, 0), GLOW, 0.0)          # pontas entram 0,1 nas lajes
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.36, 0.36, 1.3), (x + sx * 0.52, y + sy * 0.52, zb + 2.96 + 0.65), (0, 0, 0), SL, 0.0)
    mb.box((1.6, 1.6, 0.3), (x, y, zb + 4.26 + 0.15), (0, 0, 0), SD, 0.0)
    mb.cyl(1.2, 0.85, (x, y, zb + 4.56 + 0.42), (0, 0, math.pi / 4), SD, 4, r2=0.22, bevel=0.0)
    mb.cyl(0.2, 0.5, (x, y, zb + 5.41 + 0.25), (0, 0, 0), SD, 6, bevel=0.0)


def end_pilaret(mb, s, y):
    """pilarete de pedra na ponta do guarda-corpo, com giboshi dourado"""
    x = s * 13.2
    mb.box((2.2, 2.2, G + 4.6 - DECK_B), (x, y, (G + 4.6 + DECK_B) / 2), (0, 0, 0), SL, 0.18)
    mb.box((2.7, 2.7, 0.45), (x, y, G + 4.8), (0, 0, 0), SD, 0.12)
    mb.cyl(0.45, 0.5, (x, y, G + 5.25), (0, 0, 0), GOLD, 8, bevel=0.0)
    mb.ico(0.72, (x, y, G + 6.05), GOLD, 2, (1.0, 1.0, 0.95))
    K.cone(mb, (x, y, G + 6.6), (x, y, G + 7.15), 0.34, 0.06, GOLD, 8)


def plaza(mb, rng):
    """patamar de chegada (entre a ponte e o portao, ate os leoes) + passagem do portao + praca ate a escada"""
    # patamar de chegada ate a borda alargada da rodada 2 (ISLAND_RIM passa por (+-24, -118,6)): os pedestais dos
    # leoes (x 17,4..22,6) ficam inteiros sobre as lajes; na largura da ponte o patamar comeca depois da soleira
    rim, ry = 24.0, -118.35
    p1 = [(-rim, -117.2), (-rim + 1.1, ry), (-XO, ry), (-XO, Y1 + 0.65), (XO, Y1 + 0.65), (XO, ry), (rim - 1.1, ry),
          (rim, -117.2), (rim, -113.6), (-rim, -113.6)]                 # quinas chanfradas (a beira do penhasco recua)
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    ys = y1 + 1.0                                   # encosta no 1o degrau da escada do anel (pe em y -91)
    # passagem do portao + praca: o corredor |x| < 16 inteiro (o gramado do terreno termina em x = +-16; as sapatas
    # dos pilares e as bases das alas pousam em cima): sem frestas ate o vazio junto as sapatas
    p2 = [(x0, -113.6), (x1, -113.6), (x1, ys), (x0, ys)]
    for poly, zb in ((p1, G - 3.3), (p2, G - 0.6)):
        # rejunte escuro ACIMA da grama do terreno (topo G + 0.04) e lajes com topo em G + 0.16; o patamar desce
        # ate o fundo do recorte do terreno (z ~3,3) e fecha a frente do penhasco
        mb.prism(IL.ccw(poly), zb, G + 0.04, SD, 0.0)
        K.flag_floor(mb, poly, G - 0.2, rng, m=PAVE, tile=3.2, h=0.36, bevel=0.1, gap=0.2, mix=0.0, base=False)
    # soleira escura entre a ponte e o patamar + meio-fio lateral da praca
    mb.box((2 * XO, 0.9, 0.5), (0, Y1 + 0.2, G - 0.14), (0, 0, 0), SD, 0.08)
    for s in (-1, 1):
        mb.box((0.7, ys + 109.0, 0.6), (s * (x1 + 0.3), (ys - 109.0) / 2, G - 0.02), (0, 0, 0), SD, 0.1)
    # 4 toro nos cantos da praca (fora do eixo e do vao da escada)
    for s in (-1, 1):
        for y in (-103.5, y1 - 2.0):
            K.toro(mb, (s * 14.4, y, G + 0.05), s=1.0, m=SL, m2=SD, glow=GLOW, lit=False)
            col_box("EntPlaza", (2.6, 2.6, 6.6), (s * 14.4, y, G + 3.3))
        light("L_Entrance_Plaza_%s" % ("W" if s < 0 else "E"), "POINT", (s * 14.4, -103.5, G + 4.2), 140,
              (1.0, 0.62, 0.3), 0.3)


def bridge(rng):
    mb = RMB("ENT_Bridge", "02_TERRAIN", rng, detail="near")
    # laje-nucleo (rejunte escuro): 0,1 para dentro da face do meio-fio (sem z-fight com a pedra clara)
    mb.box2((-XO + 0.1, Y0, DECK_B), (XO - 0.1, Y1 + 0.4, G - 0.42), SD, 0.0)
    deck_paving(mb, rng)
    curbs(mb, rng)
    viaduct(mb)
    stacks(mb, rng)
    for s in (-1, 1):
        stops = [Y0 + 1.1] + LANTERN_Y + [Y1 - 1.1]
        for y in stops[1:-1]:
            pilaster(mb, s, y, G + 1.3)
            post_lantern(mb, s * 13.2, y, G + 1.7)
        for y in (stops[0], stops[-1]):
            end_pilaret(mb, s, y)
        railing(mb, s, stops)
    plaza(mb, rng)
    mb.finish()
    # colisao: tabuleiro + guarda-corpos altos (meio-fio + pilastras), 12 acima do piso (nao vira atalho)
    col_box2("EntBridge", (-HW, Y0 - 0.5, G - 3.0), (HW, Y1 + 2.0, G))
    for s in (-1, 1):
        xa, xb = sorted((s * HW, s * (XO + 1.0)))
        col_box2("EntBridge", (xa, Y0 - 0.5, G - 3.0), (xb, Y1 + 0.2, G + 12.0))


# ================================================================== PORTAO (04_VILLAGE)
def hip_roof(mb, cx, cy, z_e, W, Dp, rise, a, fr, th, rib=1.35, horns=True):
    """telhado de quatro aguas em telha vidrada: beiral com aba mais deitada (curva), fiadas de telha-canal em
    relevo, espigoes e cumeeira escuros com pontas levantadas, testeira escura. Soffit plano em z_e - th."""
    hw, hd = W / 2.0, Dp / 2.0
    bw, bd = hw - a, hd - a
    rw = max(0.4, (W - Dp) / 2.0)
    zb, zr = z_e + fr, z_e + rise
    bm = mb.bm

    def v(x, y, z):
        return bm.verts.new((cx + x, cy + y, z))
    Sf = [v(-hw, -hd, z_e - th), v(hw, -hd, z_e - th), v(hw, hd, z_e - th), v(-hw, hd, z_e - th)]
    E = [v(-hw, -hd, z_e), v(hw, -hd, z_e), v(hw, hd, z_e), v(-hw, hd, z_e)]
    B = [v(-bw, -bd, zb), v(bw, -bd, zb), v(bw, bd, zb), v(-bw, bd, zb)]
    R0, R1 = v(-rw, 0, zr), v(rw, 0, zr)
    F = bm.faces.new
    F((Sf[3], Sf[2], Sf[1], Sf[0]))
    for i in range(4):
        j = (i + 1) % 4
        F((Sf[i], Sf[j], E[j], E[i]))
        F((E[i], E[j], B[j], B[i]))
    F((B[0], B[1], R1, R0))
    F((B[1], B[2], R1))
    F((B[2], B[3], R0, R1))
    F((B[3], B[0], R0))
    mb._post(Sf + E + B + [R0, R1], TILE, None, 0, 1)
    C = Vector((cx, cy, 0))
    # testeira escura (ponta das telhas do beiral)
    for sy in (-1, 1):
        mb.box((W + 0.3, 0.32, th + 0.3), (cx, cy + sy * (hd + 0.06), z_e - th / 2 + 0.08), (0, 0, 0), TILED, 0.0)
    for sx in (-1, 1):
        mb.box((0.32, Dp + 0.3, th + 0.3), (cx + sx * (hw + 0.06), cy, z_e - th / 2 + 0.08), (0, 0, 0), TILED, 0.0)
    # fiadas de telha-canal (relevo na propria telha)
    rh, rwid = 0.32, 0.42
    up_len = math.hypot(bd, rise - fr)
    fl_len = math.hypot(a, fr)
    nx = int((2 * bw - 1.0) / rib)
    for i in range(nx + 1):
        x = -bw + 0.5 + i * (2 * bw - 1.0) / max(nx, 1)
        ax = abs(x)
        t = 1.0 if ax <= rw else (bw - ax) / (bw - rw)
        for sy in (-1, 1):
            n_up = Vector((0, sy * (rise - fr), bd)) / up_len * (rh * 0.35)
            if t > 0.12:
                p0 = C + Vector((x, sy * bd, zb))
                p1 = C + Vector((x, sy * bd * (1 - t), zb + (rise - fr) * t))
                mb.beam(p0 + n_up, p1 + n_up, rwid, rh, TILE, 0.0)
            n_fl = Vector((0, sy * fr, a)) / fl_len * (rh * 0.35)
            mb.beam(C + Vector((x, sy * hd, z_e)) + n_fl, C + Vector((x, sy * bd, zb)) + n_fl, rwid, rh, TILE, 0.0)
    ny = int((2 * bd - 1.0) / rib)
    for i in range(ny + 1):
        y = -bd + 0.5 + i * (2 * bd - 1.0) / max(ny, 1)
        t = 1.0 - abs(y) / bd
        for sx in (-1, 1):
            n_up = Vector((sx * (rise - fr), 0, bw - rw)) / math.hypot(rise - fr, bw - rw) * (rh * 0.35)
            if t > 0.12:
                p0 = C + Vector((sx * bw, y, zb))
                p1 = C + Vector((sx * (bw - (bw - rw) * t), y, zb + (rise - fr) * t))
                mb.beam(p0 + n_up, p1 + n_up, rwid, rh, TILE, 0.0)
            n_fl = Vector((sx * fr, 0, a)) / fl_len * (rh * 0.35)
            mb.beam(C + Vector((sx * hw, y, z_e)) + n_fl, C + Vector((sx * bw, y, zb)) + n_fl, rwid, rh, TILE, 0.0)
    # espigoes (4), com a ponta do beiral levantada
    lift = Vector((0, 0, 0.3))
    for sx in (-1, 1):
        for sy in (-1, 1):
            ce = C + Vector((sx * hw, sy * hd, z_e))
            cb = C + Vector((sx * bw, sy * bd, zb))
            cr = C + Vector((sx * rw, 0, zr))
            mb.beam(ce + lift, cb + lift, 0.66, 0.55, TILED, 0.0)
            mb.beam(cb + lift, cr + lift, 0.66, 0.55, TILED, 0.0)
            # ponta do beiral levantada (curta e grossa: le como telha virada, nao como espinho)
            tip = ce + Vector((sx * 0.55, sy * 0.55, 0.85))
            K.cone(mb, ce + Vector((-sx * 0.3, -sy * 0.3, 0.25)), tip, 0.5, 0.2, TILED, 6)
    # cumeeira + chifres nas pontas
    mb.beam(C + Vector((-rw - 0.35, 0, zr + 0.3)), C + Vector((rw + 0.35, 0, zr + 0.3)), 1.0, 0.9, TILED, 0.1)
    if horns:
        for sx in (-1, 1):
            p = C + Vector((sx * rw, 0, zr + 0.5))
            q = C + Vector((sx * (rw + 0.55), 0, zr + 1.9))
            K.cone(mb, p, q, 0.62, 0.26, TILED, 6)
            K.cone(mb, q - Vector((0, 0, 0.2)), q + Vector((-sx * 0.6, 0, 0.35)), 0.3, 0.1, TILED, 5)
    return zr


def rafters(mb, cx, cy, z_s, span, y_in, y_out, step=1.35, sides=None):
    """caibros sob o beiral: frente/tras (x em span, de y_in ate y_out) e laterais (sides = (x_in, x_out, y_span))"""
    x0, x1 = span
    n = int((x1 - x0) / step)
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / max(n, 1)
        for sy in (-1, 1):
            mb.beam((cx + x, cy + sy * y_in, z_s - 0.24), (cx + x, cy + sy * y_out, z_s - 0.24), 0.42, 0.46, DARK, 0.0)
    if sides:
        xi, xo, ys = sides
        m = int(2 * ys / step)
        for i in range(m + 1):
            y = -ys + 2 * ys * i / max(m, 1)
            for sx in (-1, 1):
                mb.beam((cx + sx * xi, cy + y, z_s - 0.24), (cx + sx * xo, cy + y, z_s - 0.24), 0.42, 0.46, DARK, 0.0)


def panel_frame(mb, xa, xb, za, zb, depth, w=0.36):
    """moldura vermelha interna de um painel de reboco (dos dois lados da parede)"""
    xm, zm = (xa + xb) / 2, (za + zb) / 2
    for z in (za, zb):
        mb.box((xb - xa + w, depth, w), (xm, GY, z), (0, 0, 0), RED, 0.0)
    for x in (xa, xb):
        mb.box((w, depth, zb - za), (x, GY, zm), (0, 0, 0), RED, 0.0)


def leaf_emblem(mb, yface, zc, s, m, back=False, w=0.26, h=0.22, res=14):
    """folha de Konoha em relevo na face y = yface (frente = -y; back = +y)"""
    u = (-1, 0, 0) if back else (1, 0, 0)
    PN.leaf_symbol(mb, (0.0, yface, zc), u, (0, 0, 1), s, m, w=w, h=h, res=res)


def plaque(mb, back=False):
    """placa-brasao na verga: quadro verde-escuro, moldura dourada, folha dourada (sem texto)"""
    sy = 1 if back else -1
    yb = GY + sy * 1.5                     # face da verga
    yc = yb + sy * 0.3
    zc = G + OH + 2.5
    mb.box((5.8, 0.6, 4.4), (0, yc, zc), (0, 0, 0), TILED, 0.1)
    for dz in (-2.25, 2.25):
        mb.box((6.6, 0.8, 0.45), (0, yc + sy * 0.1, zc + dz), (0, 0, 0), GOLD, 0.06)
    for dx in (-3.1, 3.1):
        mb.box((0.45, 0.8, 4.9), (dx, yc + sy * 0.1, zc), (0, 0, 0), GOLD, 0.06)
    # folha de Konoha (x do portal e o mesmo da placa: centro em x 0)
    PN.leaf_symbol(mb, (0.0, yc + sy * 0.3, zc), ((-1, 0, 0) if back else (1, 0, 0)), (0, 0, 1), 1.3, GOLD,
                   w=0.27, h=0.3, res=14)


def banner(mb, s):
    """estandarte PENDURADO no pilar externo da ala (sem mastro no chao): abracadeira e braco de ferro saindo da face
    de fora do pilar em BANNER_Z, mao-francesa por baixo e remate na ponta; trave escura com o pano 3 x 9 (ponta em
    V), filetes dourados salientes 0,11 e disco creme com a folha nas 2 faces (tudo >= 0,1 de folga)"""
    xp = s * XQ                                    # eixo do pilar externo
    xf = s * (XQ + 1.3)                            # face de fora do pilar (2,6)
    xa = xf + s * 4.3                              # ponta do braco
    y, z = GY, BANNER_Z
    mb.box((2.9, 2.9, 0.5), (xp, y, z), (0, 0, 0), IRON, 0.0)               # abracadeira (0,15 saliente)
    mb.beam((xf - s * 0.1, y, z), (xa, y, z), 0.42, 0.46, IRON, 0.0)        # braco
    mb.beam((xf - s * 0.1, y, z - 2.7), (xf + s * 2.4, y, z - 0.15), 0.36, 0.36, IRON, 0.0)   # mao-francesa
    mb.box((2.9, 2.9, 0.5), (xp, y, z - 2.7), (0, 0, 0), IRON, 0.0)         # abracadeira de baixo
    mb.ico(0.36, (xa + s * 0.25, y, z), IRON, 1)
    K.cone(mb, (xa + s * 0.25, y, z + 0.3), (xa + s * 0.25, y, z + 0.95), 0.2, 0.04, IRON, 5)
    # trave de madeira presa ao braco por 2 argolas; pano 3 x 9 (retangulo 7,9 + ponta 1,1)
    cx = xf + s * 2.2
    w, h, tip = BANNER_W, BANNER_H - 1.1, 1.1
    top = z - 0.75
    mb.beam((cx - 1.9, y, top), (cx + 1.9, y, top), 0.4, 0.4, DARK, 0.0)
    for dx in (-1.1, 1.1):
        mb.box((0.36, 0.5, 0.52), (cx + dx, y, z - 0.42), (0, 0, 0), IRON, 0.0)
    th = 0.18
    pts = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2, -h), (0.0, -h - tip), (-w / 2, -h)]
    bm = mb.bm
    vf = [bm.verts.new((cx + px, y - th / 2, top - 0.2 + pz)) for px, pz in pts]
    vb = [bm.verts.new((cx + px, y + th / 2, top - 0.2 + pz)) for px, pz in pts]
    bm.faces.new(list(reversed(vf)))
    bm.faces.new(vb)
    for i in range(5):
        j = (i + 1) % 5
        bm.faces.new((vf[i], vf[j], vb[j], vb[i]))
    mb._post(vf + vb, "Cloth_EntRed", None, 0, 1)
    # filetes dourados (0,4 de espessura: 0,11 saliente de cada face do pano)
    mb.box((w + 0.1, 0.4, 0.36), (cx, y, top - 0.38), (0, 0, 0), GOLD, 0.0)
    for sx in (-1, 1):
        mb.box((0.3, 0.4, h - 0.6), (cx + sx * (w / 2 - 0.1), y, top - 0.2 - h / 2 - 0.2), (0, 0, 0), GOLD, 0.0)
    # disco creme + folha (relevo 0,3) nas duas faces
    zc = top - 3.4
    for sy in (-1, 1):
        mb.cyl(1.2, 0.26, (cx, y + sy * 0.18, zc), (math.pi / 2, 0, 0), "Emblem_Cream", 20, bevel=0.0)
        u = (1, 0, 0) if sy < 0 else (-1, 0, 0)
        PN.leaf_symbol(mb, (cx, y + sy * 0.31, zc), u, (0, 0, 1), 0.74, "Cloth_EntRed", w=0.42, h=0.3, res=10)


def chochin(mb, loc, r=1.0, h=1.9, hang=1.2, n=8):
    """lanterna de papel pendurada (como fm_portal_kit.chochin, com folga >= 0,1 entre o papel, a faixa vermelha e as
    tampas: no Roblox o papel nao pisca atras da faixa). loc = ponto de fixacao em cima; devolve o centro."""
    top = Vector(loc)
    mb.rod(top, top - Vector((0, 0, hang)), 0.09, DARK, 6)
    c = top - Vector((0, 0, hang + 0.25 + h / 2))
    mb.cyl(r * 0.78, h * 0.5, c + Vector((0, 0, h * 0.25)), (0, 0, 0), GLOW, n, r2=r * 0.62, bevel=0.0)
    mb.cyl(r * 0.62, h * 0.5, c - Vector((0, 0, h * 0.25)), (0, 0, 0), GLOW, n, r2=r * 0.78, bevel=0.0)
    mb.cyl(r * 0.78 + 0.12, h * 0.16, c, (0, 0, 0), RED, n, bevel=0.0)
    for sgn in (-1, 1):
        mb.cyl(r * 0.62 + 0.12, 0.3, c + Vector((0, 0, sgn * (h / 2 + 0.1))), (0, 0, 0), DARK, n, bevel=0.0)
    return c


def door_leaf(mb, s):
    """folha do portao aberta (~174 graus), encostada atras da ala: tabuas + travessas escuras + cravos dourados"""
    hinge = Vector((s * (OW + 0.6), GY + 2.8, 0))
    ang = math.radians(6.0)
    d = Vector((s * math.cos(ang), math.sin(ang), 0))
    L_ = 9.8
    c = hinge + d * (L_ / 2)
    yaw = math.atan2(d.y, d.x)
    h = OH - 1.0
    mb.box((L_, 0.7, h), (c.x, c.y, G + 0.2 + h / 2), (0, 0, yaw), "Wood_Plank", 0.12)
    for z in (1.6, 6.0, 10.4, 14.8):
        mb.box((L_ + 0.1, 1.05, 0.8), (c.x, c.y, G + 0.2 + z), (0, 0, yaw), DARK, 0.06)
        for k in (-3.2, 0.0, 3.2):
            p = c + d * k
            mb.box((0.42, 1.25, 0.42), (p.x, p.y, G + 0.2 + z), (0, 0, yaw), GOLD, 0.0)
    col_box("EntGate", (L_, 1.0, h), (c.x, c.y, G + 0.2 + h / 2), (0, 0, yaw))


def gate(rng):
    mb = NMB("ENT_Gate", "04_VILLAGE", rng, detail="hero")
    z_lintel = G + OH                              # fundo da verga = altura livre do vao
    for s in (-1, 1):
        # ---- pilares centrais (os maiores) em sapata de pedra
        xs = s * (OW + 2.3)                        # sapata 4.6: face interna em x 10
        mb.box((4.6, 4.6, 2.2), (xs, GY, G + 1.1), (0, 0, 0), SL, 0.22)
        mb.box((4.2, 4.2, 0.45), (xs, GY, G + 2.4), (0, 0, 0), SD, 0.1)
        xp = s * XP
        zp0, zp1 = G + 2.6, G + 22.0
        mb.box((3.6, 3.6, zp1 - zp0), (xp, GY, (zp0 + zp1) / 2), (0, 0, 0), RED, 0.28)
        for z in (G + 3.1, G + 16.9):
            mb.box((3.85, 3.85, 0.45), (xp, GY, z), (0, 0, 0), GOLD, 0.05)
        mb.box((4.3, 4.3, 0.8), (xp, GY, zp1 + 0.4), (0, 0, 0), DARK, 0.1)
        col_box("EntGate", (4.6, 4.6, 23.0), (xs, GY, G + 11.5))
        # ---- pilares externos (ate o frechal da ala)
        xq = s * XQ
        mb.box((3.2, 3.2, 1.8), (xq, GY, G + 0.9), (0, 0, 0), SL, 0.2)
        mb.box((2.9, 2.9, 0.35), (xq, GY, G + 1.95), (0, 0, 0), SD, 0.08)
        mb.box((2.6, 2.6, ZW - G - 2.1), (xq, GY, (G + 2.1 + ZW) / 2), (0, 0, 0), RED, 0.22)
        mb.box((2.8, 2.8, 0.4), (xq, GY, G + 2.6), (0, 0, 0), GOLD, 0.05)
        mb.box((2.8, 2.8, 0.4), (xq, GY, ZW - 1.6), (0, 0, 0), GOLD, 0.05)
        mb.box((3.1, 3.1, 0.6), (xq, GY, ZW + 0.2), (0, 0, 0), DARK, 0.08)
        col_box("EntGate", (3.2, 3.2, ZW - G), (xq, GY, (G + ZW) / 2))
        # ---- ala: base de pedra, 2 paineis altos de reboco creme emoldurados de vermelho + friso
        xa, xb = s * 14.0, s * (XQ - 1.3)
        xa, xb = min(xa, xb), max(xa, xb)
        xm, wl = (xa + xb) / 2, xb - xa
        zr0, zr1 = G + 13.4, G + 14.0              # travessa entre o painel e o friso
        mb.box((wl, 2.4, 2.0), (xm, GY, G + 1.0), (0, 0, 0), SL, 0.15)
        mb.box((wl, 2.6, 0.3), (xm, GY, G + 2.15), (0, 0, 0), SD, 0.05)
        mb.box((wl, 1.2, ZW - G - 2.3), (xm, GY, (G + 2.3 + ZW) / 2), (0, 0, 0), CREAM, 0.0)
        mb.box((wl, 1.6, 0.7), (xm, GY, G + 2.65), (0, 0, 0), RED, 0.06)
        mb.box((wl, 1.6, zr1 - zr0), (xm, GY, (zr0 + zr1) / 2), (0, 0, 0), RED, 0.06)
        mb.box((wl, 1.7, 0.9), (xm, GY, ZW - 0.45), (0, 0, 0), RED, 0.06)
        mb.box((0.8, 1.6, zr0 - G - 3.0), (xm, GY, (G + 3.0 + zr0) / 2), (0, 0, 0), RED, 0.05)
        for k in (-1, 0, 1):
            mb.box((0.5, 1.5, ZW - 0.9 - zr1), (xm + k * wl / 3, GY, (zr1 + ZW - 0.9) / 2), (0, 0, 0), RED, 0.0)
        for pa, pb in ((xa + 0.4, xm - 0.4), (xm + 0.4, xb - 0.4)):
            panel_frame(mb, pa + 0.75, pb - 0.75, G + 3.85, zr0 - 0.85, 1.6)
        mb.box((wl + 0.6, 2.2, 0.5), (xm, GY, ZW + 0.25), (0, 0, 0), DARK, 0.05)
        col_box2("EntGate", (xa, GY - 1.3, G), (xb, GY + 1.3, ZW))
        # ---- telhadinho da ala (beiral logo abaixo da verga, como na ref_14)
        cxr = s * 21.0
        hip_roof(mb, cxr, GY, ZW + 1.2, 14.8, 8.6, 3.1, 1.4, 0.5, 0.7, rib=1.4, horns=False)
        rafters(mb, cxr, GY, ZW + 0.5, (-6.4, 6.4), 1.3, 4.05, step=1.4)
        # ---- folha do portao aberta + estandarte
        door_leaf(mb, s)
        banner(mb, s)
        # ---- lanterna de papel pendurada na verga
        c = chochin(mb, (s * 7.2, GY - 0.7, z_lintel), r=1.45, h=2.9, hang=0.8, n=10)
        light("L_Entrance_GateLantern_%s" % ("W" if s < 0 else "E"), "POINT", tuple(c), 160, (1.0, 0.62, 0.3), 0.4)
    # ---- verga, friso e travessa
    mb.box((28.0, 3.0, 2.2), (0, GY, z_lintel + 1.1), (0, 0, 0), RED, 0.22)
    mb.box((27.6, 2.3, 0.8), (0, GY, z_lintel + 2.6), (0, 0, 0), DARK, 0.06)
    mb.box((29.6, 2.8, 1.0), (0, GY, z_lintel + 3.5), (0, 0, 0), RED, 0.15)
    for s in (-1, 1):             # ponteiras de ouro: 0,1 alem da travessa em todas as faces
        mb.box((0.6, 3.0, 1.2), (s * 14.6, GY, z_lintel + 3.5), (0, 0, 0), GOLD, 0.0)
    # ---- misulas (blocos + bracos) e teras do beiral
    zt = z_lintel + 4.0                            # topo da travessa (G + 22)
    for x in (-XP, -6.1, 0.0, 6.1, XP):
        mb.box((1.5, 1.5, 1.0), (x, GY, zt + 0.5), (0, 0, 0), DARK, 0.06)
        mb.beam((x, GY - 5.6, zt + 1.4), (x, GY + 5.6, zt + 1.4), 0.9, 0.8, DARK, 0.06)
        for sy in (-1, 1):
            mb.beam((x, GY + sy * 1.4, zt + 0.35), (x, GY + sy * 4.9, zt + 1.05), 0.7, 0.6, DARK, 0.0)
    for sy in (-1, 1):
        mb.beam((-17.8, GY + sy * 5.0, zt + 2.2), (17.8, GY + sy * 5.0, zt + 2.2), 1.0, 0.8, DARK, 0.06)
    # ---- telhado grande (4 aguas) + caibros
    z_e = zt + 3.4                                  # soffit em zt + 2.6
    W1, D1 = 38.0, 18.4
    zr = hip_roof(mb, 0.0, GY, z_e, W1, D1, 5.0, 2.4, 0.9, 0.8, rib=1.35, horns=False)
    rafters(mb, 0.0, GY, z_e - 0.8, (-17.6, 17.6), 5.5, D1 / 2 - 0.15, step=1.35, sides=(15.8, W1 / 2 - 0.15, 4.6))
    # ---- tambor + telhadinho de cima
    mb.box((18.0, 4.6, 3.4), (0, GY, zr - 0.3), (0, 0, 0), RED, 0.1)
    mb.box((18.8, 5.2, 0.5), (0, GY, zr + 1.55), (0, 0, 0), DARK, 0.05)
    for x in (-6.0, 6.0):
        for sy in (-1, 1):
            mb.box((3.6, 0.3, 1.5), (x, GY + sy * 2.35, zr + 0.35), (0, 0, 0), DARK, 0.0)
    z_e2 = zr + 2.5
    zr2 = hip_roof(mb, 0.0, GY, z_e2, 22.0, 8.6, 3.3, 1.4, 0.5, 0.7, rib=1.35, horns=True)
    rafters(mb, 0.0, GY, z_e2 - 0.7, (-10.2, 10.2), 2.7, 4.15, step=1.35)
    mb.cyl(0.55, 0.9, (0, GY, zr2 + 1.1), (0, 0, 0), GOLD, 8, bevel=0.0)
    mb.ico(0.75, (0, GY, zr2 + 2.1), GOLD, 1, (1.0, 1.0, 1.2))
    K.cone(mb, (0, GY, zr2 + 2.6), (0, GY, zr2 + 3.6), 0.35, 0.05, GOLD, 6)
    # ---- placa-brasao (frente e verso)
    plaque(mb, back=False)
    plaque(mb, back=True)
    # telhados em UM tom: telha e peca escura sem o mosaico da textura de detalhe
    flat_mats(mb, (TILE, TILED))
    mb.finish()


# ================================================================== LEOES (04_VILLAGE)
LION_S = 1.0                      # escala do il_lion (leao ~8 de altura)
PED_W, PED_D, PED_H = 5.2, 4.4, 4.5   # pedestal (centro 0,2 ao norte de L.LIONS): frente em y -118,0 = beira do
PED_DY = 0.2                          # topo do penhasco (a borda da planta e -118,6); fundo em -113,6


def lions(rng):
    """2 leoes guardioes (il_lion) nos pedestais de L.LIONS, olhando para a ponte (sul); a pata de FORA pousa na
    esfera (lado de fora = longe do eixo)"""
    mb = NMB("ENT_Lions", "04_VILLAGE", rng, detail="near")
    yaw = math.pi                                  # +Y local do leao -> -Y do mundo (a ponte)
    for lx, ly in L.LIONS:
        py = ly + PED_DY
        z = il_lion.pedestal(mb, lx, py, G - 0.05, yaw, w=PED_W, d=PED_D, h=PED_H + 0.05, light_m=SL, dark_m=SD)
        side = -1 if lx > 0 else 1                 # olhando para -Y, a direita do leao e -X
        il_lion.lion(mb, lx, ly + 0.3, z, yaw, s=LION_S, side=side, ball_mat=MANE, body_m=LION, mane_m=MANE,
                     dark_m="Stone_Grout")
        col_box("EntLions", (PED_W, PED_D, PED_H), (lx, py, G + PED_H / 2))
        col_box("EntLions", (4.4 * LION_S, 4.4 * LION_S, 7.6 * LION_S), (lx, py, G + PED_H + 3.8 * LION_S))
        # mureta baixa pedestal -> base da ala: fecha a fresta de 2,3 entre o leao e a ala (o patamar leva so ao
        # portao; os gramados laterais sao acessados pela praca de dentro)
        ya, yb = py + PED_D / 2 - 0.1, GY - 1.1
        mb.box((1.4, yb - ya, 2.0), (lx, (ya + yb) / 2, G + 1.0), (0, 0, 0), SL, 0.05)
        mb.box((1.8, yb - ya + 0.3, 0.36), (lx, (ya + yb) / 2, G + 2.18), (0, 0, 0), SD, 0.0)
        col_box("EntLions", (1.6, yb - ya, 4.0), (lx, (ya + yb) / 2, G + 2.0))
    mb.finish()


def build():
    bridge(random.Random(5101))
    gate(random.Random(5102))
    lions(random.Random(5103))
