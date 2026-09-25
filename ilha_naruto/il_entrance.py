# il_entrance - Ilha 1 (Naruto / Vila da Folha): ENTRADA (substitui il_blockout.entrance()).
#   1. Ponte de chegada (y L.LOBBY_Y -> L.ISLAND_S_Y, piso em L.G): tabuleiro de lajes transversais, meio-fio de pedra,
#      guarda-corpo de madeira (postes escuros, travessas claras), 4 toro alternados a cada 16 em pilastras, viaduto de
#      3 arcos de pedra com pilares descendo ao vazio, 2 pilaretes com giboshi dourado em cada ponta.      (02_TERRAIN)
#   2. Praca do portao + patamar de chegada: lajes irregulares, 4 toro nos cantos.                        (02_TERRAIN)
#   3. PORTAO PRINCIPAL (peca-heroi): 4 pilares de laca vermelha em sapatas de pedra, verga + frisos, misulas e
#      caibros, telhado de quatro aguas em telha verde vidrada em 2 niveis, placa com a folha em espiral (frente e
#      verso), 2 lanternas de papel penduradas na verga, alas de reboco creme emolduradas de vermelho sobre base de
#      pedra e telhadinhos proprios, folhas do portao ABERTAS encostadas nas alas (lado da praca).          (04_VILLAGE)
#   4. 2 estandartes vermelhos com a folha ladeando o portao (no mesmo objeto do portao).                 (04_VILLAGE)
#   5. 2 leoes de pedra (komainu) nos pedestais de L.LIONS.                                              (04_VILLAGE)
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

# ------------------------------------------------------------------ materiais novos da zona (3 de 4)
_M = fm_lib.MATS.setdefault
_M("Stone_EntLion", (S(116, 120, 128), 0.85, 0.0, 0, None, 0.12))       # pedra dos komainu (fria, contrasta c/ pedestal)
_M("Roof_EntJadeDark", (S(38, 76, 54), 0.55, 0.0, 0, None, 0.08))       # cumeeira/espigao/beiral da telha verde
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
LANTERNS = [(-1, -182.0), (1, -166.0), (-1, -150.0), (1, -134.0)]   # toro alternados a cada 16 (lado, y)

GY = L.GATE_Y
OW = L.GATE_OPEN_W / 2.0          # 10
OH = L.GATE_OPEN_H                # 18
GHW = L.GATE_W / 2.0              # 26
XP = 12.2                         # eixo dos pilares centrais (face interna em x 10.4)
XQ = GHW - 1.4                    # eixo dos pilares externos (24.6)
BANNER_X = 31.6                   # estandartes (fora do telhadinho das alas)
LION_K = 1.15                     # escala do corpo do komainu (pedestal fixo 5 x 5)
ZW = G + L.GATE_OPEN_H - 0.2      # topo das paredes das alas (frechal): telhadinho logo abaixo da verga

PAVE, SL, SD = "Stone_Paving_Warm", "Stone_Wall_Light", "Stone_Wall_Dark"
RED, DARK, GOLD, CREAM = "Wood_Lacquer_Red", "Wood_Dark", "Metal_Gold", "Plaster_Cream"
TILE, TILED, GLOW, LION = "Roof_Green", "Roof_EntJadeDark", "Lantern_Glow", "Stone_EntLion"

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


class NMB(MB):
    """MB sem variantes tonais: 1 MeshPart por material (portao/leoes tem muitas pecas pequenas repetidas)"""

    def _mi_for(self, m):
        return self._mi(m)


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
    zb = G - 44.0
    for k, yc in enumerate(PIERS):
        mb.box((2 * XO, PIER_T, DECK_B - zb), (0, yc, (DECK_B + zb) / 2), (0, 0, 0), SL, 0.2)
        # faixa escura na nascente dos arcos + pilastras laterais (ritmo vertical do viaduto)
        mb.box((2 * XO + 0.8, PIER_T + 0.8, 0.8), (0, yc, Z_SPRING - 0.4), (0, 0, 0), SD, 0.12)
        for s in (-1, 1):
            mb.box((0.6, PIER_T - 1.0, Z_SPRING - 0.8 - zb), (s * (XO + 0.3), yc, (Z_SPRING - 0.8 + zb) / 2),
                   (0, 0, 0), SL, 0.1)
        # base do pilar: tronco de piramide afinando para baixo + ponta de rocha
        FP.frustum(mb, (0, yc, zb - 20.0), 9.0, 2.6, 2 * XO, PIER_T, 20.0, SL)
        mb.rock((0, yc, zb - 22.0), (8.0, 3.2, 5.0), SD, 1, flat_bottom=False)
    # encontro norte (a abobada do 3o arco nasce na alvenaria encostada no penhasco)
    mb.box2((-XO, Y1 - 0.6, Z_SPRING - 10.0), (XO, Y1 + 5.0, DECK_B), SL, 0.2)


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
    rim = 22.0
    rim_y = Y1 + (rim - 13.0) / 19.0 * 4.0          # borda da ilha em x = 22 (ISLAND_RIM (13,-118)-(32,-114))
    p1 = [(-13.0, Y1), (13.0, Y1), (rim, rim_y), (rim, -113.6), (-rim, -113.6), (-rim, rim_y)]
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    ys = y1 + 1.0                                   # encosta no 1o degrau da escada do anel (pe em y -91)
    p2 = [(-OW - 0.2, -113.6), (OW + 0.2, -113.6), (OW + 0.2, -109.0), (x1, -109.0), (x1, ys), (x0, ys),
          (x0, -109.0), (-OW - 0.2, -109.0)]
    for poly in (p1, p2):
        # rejunte escuro ACIMA da grama do terreno (topo G + 0.04) e lajes com topo em G + 0.16
        mb.prism(IL.ccw(poly), G - 0.6, G + 0.04, SD, 0.0)
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
    mb = MB("ENT_Bridge", "02_TERRAIN", rng, detail="near")
    mb.box2((-XO, Y0, DECK_B), (XO, Y1 + 0.4, G - 0.42), SD, 0.0)        # laje-nucleo (rejunte escuro)
    deck_paving(mb, rng)
    curbs(mb, rng)
    viaduct(mb)
    for s in (-1, 1):
        stops = [Y0 + 1.1] + [y for side, y in LANTERNS if side == s] + [Y1 - 1.1]
        for y in stops[1:-1]:
            pilaster(mb, s, y, G + 1.3)
            K.toro(mb, (s * 13.2, y, G + 1.5), s=1.0, m=SL, m2=SD, glow=GLOW, lit=False)
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
                   w=0.27, h=0.24, res=14)


def banner(mb, s):
    """estandarte alto (pano vermelho com disco creme e a folha), pau escuro com remate dourado"""
    x, y = s * BANNER_X, GY - 1.0
    mb.box((2.3, 2.3, 1.2), (x, y, G + 0.6), (0, 0, 0), SL, 0.15)
    mb.box((1.7, 1.7, 0.4), (x, y, G + 1.4), (0, 0, 0), SD, 0.08)
    mb.cyl(0.38, 26.4, (x, y, G + 1.6 + 13.2), (0, 0, 0), DARK, 8, bevel=0.0)
    mb.cyl(0.5, 0.5, (x, y, G + 28.1), (0, 0, 0), GOLD, 8, bevel=0.0)
    mb.ico(0.5, (x, y, G + 28.6), GOLD, 1)
    K.cone(mb, (x, y, G + 28.9), (x, y, G + 30.2), 0.32, 0.05, GOLD, 6)
    yc = y - 0.55
    top = G + 26.2
    FP.banner(mb, (x, yc, top), 0.0, w=4.6, h=13.6, cloth="Cloth_EntRed", trim=GOLD, emblem=None)
    zc = top - 5.4
    for sy in (-1, 1):
        mb.cyl(1.75, 0.14, (x, yc + sy * 0.16, zc), (math.pi / 2, 0, 0), "Emblem_Cream", 20, bevel=0.0)
        u = (1, 0, 0) if sy < 0 else (-1, 0, 0)
        PN.leaf_symbol(mb, (x, yc + sy * 0.23, zc), u, (0, 0, 1), 1.05, "Cloth_EntRed", w=0.3, h=0.16, res=10)
    col_box("EntGate", (2.3, 2.3, 8.0), (x, y, G + 4.0))


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
        c = K.chochin(mb, (s * 7.2, GY - 0.7, z_lintel), r=1.45, h=2.9, paper=GLOW, cap=DARK, band=RED, hang=0.8, n=10,
                      rod_m=DARK)
        light("L_Entrance_GateLantern_%s" % ("W" if s < 0 else "E"), "POINT", tuple(c), 160, (1.0, 0.62, 0.3), 0.4)
    # ---- verga, friso e travessa
    mb.box((28.0, 3.0, 2.2), (0, GY, z_lintel + 1.1), (0, 0, 0), RED, 0.22)
    mb.box((27.6, 2.3, 0.8), (0, GY, z_lintel + 2.6), (0, 0, 0), DARK, 0.06)
    mb.box((29.6, 2.8, 1.0), (0, GY, z_lintel + 3.5), (0, 0, 0), RED, 0.15)
    for s in (-1, 1):
        mb.box((0.5, 3.0, 1.1), (s * 14.6, GY, z_lintel + 3.5), (0, 0, 0), GOLD, 0.04)
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
    mb.finish()


# ================================================================== LEOES (04_VILLAGE)
def komainu(mb, lx, ly, s):
    """komainu sentado, robusto e estilizado (juba em cachos, cauda em chama), olhando para quem chega"""
    # pedestal
    mb.box((5.0, 5.0, 0.8), (lx, ly, G + 0.4), (0, 0, 0), SL, 0.15)
    mb.box((4.2, 4.2, 2.8), (lx, ly, G + 2.2), (0, 0, 0), SL, 0.15)
    mb.box((2.9, 0.4, 1.8), (lx, ly - 2.2, G + 2.2), (0, 0, 0), SD, 0.06)
    mb.box((4.8, 4.8, 0.5), (lx, ly, G + 3.85), (0, 0, 0), SD, 0.12)
    z0 = G + 4.1
    F = FP.Frame(lx, ly, z0, -s * D(14.0))
    r = F.r()
    yaw = r[2]
    k_ = LION_K

    def P(x, y, z):
        return F.p(x * k_, y * k_, z * k_)

    def ico(rad, p, m, sub, sc=(1, 1, 1), rot=r):
        mb.ico(rad * k_, P(*p), m, sub, sc, rot)

    def box(size, p, m, bev, rot=r):
        mb.box(tuple(v * k_ for v in size), P(*p), rot, m, bev * k_)

    def disc(rad, h, p, m=LION, rot=(math.pi / 2, 0, yaw)):
        mb.cyl(rad * k_, h * k_, P(*p), rot, m, 8, bevel=0.0)
    box((3.6, 4.2, 0.45), (0, 0.1, 0.22), LION, 0.15)
    # ancas (massas redondas atras) e patas traseiras dobradas
    for k in (-1, 1):
        ico(1.0, (k * 0.98, 0.85, 1.25), LION, 2, (0.95, 1.4, 1.1))
        ico(1.0, (k * 1.18, -0.25, 0.62), LION, 1, (0.55, 0.8, 0.4))
    # tronco sentado (inclinado para tras) + peito estufado
    ico(1.0, (0, 0.35, 2.15), LION, 2, (1.2, 1.3, 1.8), (D(-14), 0, yaw))
    ico(1.0, (0, -0.55, 2.55), LION, 2, (1.15, 0.95, 1.25))
    # patas dianteiras (colunas firmes) + patas + perola dourada entre elas
    for k in (-1, 1):
        disc(0.5, 2.5, (k * 0.74, -1.02, 1.55), rot=(D(4), 0, yaw))
        ico(1.0, (k * 0.76, -1.35, 0.62), LION, 1, (0.62, 0.8, 0.42))
    ico(0.58, (0, -1.95, 1.0), GOLD, 2)
    # juba: massa atras da cabeca + coroa de cachos redondos em volta do rosto (discos virados para a frente)
    ico(1.0, (0, -0.4, 4.15), LION, 2, (1.6, 1.15, 1.6))
    for i in range(10):
        a = D(-72 + i * 36)
        disc(0.52, 0.55, (math.cos(a) * 1.5, -1.42, 4.15 + math.sin(a) * 1.45))
    for k in (-1, 1):
        disc(0.46, 0.5, (k * 0.95, -1.3, 2.95))
    # cabeca: rosto, focinho largo, nariz, olhos grandes, sobrancelhas, boca (a/un), orelhas
    ico(1.0, (0, -1.35, 4.2), LION, 2, (1.12, 0.9, 1.0))
    box((1.55, 0.95, 0.85), (0, -2.1, 3.8), LION, 0.28)
    box((0.7, 0.45, 0.42), (0, -2.58, 4.08), SD, 0.1)
    for k in (-1, 1):
        ico(0.3, (k * 0.46, -2.1, 4.52), SD, 1)
        box((0.75, 0.5, 0.36), (k * 0.46, -2.02, 4.88), LION, 0.1, rot=(D(18), 0, yaw))
        ico(1.0, (k * 1.05, -0.95, 5.0), LION, 1, (0.42, 0.25, 0.34))
    box((1.05, 0.3, 0.4 if s > 0 else 0.2), (0, -2.5, 3.46), SD, 0.0)     # boca aberta (a) / fechada (un)
    for k in (-1, 0, 1):
        disc(0.36, 0.4, (k * 0.55, -1.05, 5.3 - abs(k) * 0.15))
    # cauda em chama (3 labaredas subindo das costas)
    for dy, dz, sc in ((1.7, 2.6, 1.0), (1.85, 3.5, 0.8), (1.75, 4.3, 0.6)):
        ico(1.0, (0, dy, dz), LION, 1, (0.75 * sc, 0.45 * sc, 0.8 * sc), (D(20), 0, yaw))
    for k in (-1, 1):
        ico(1.0, (k * 0.55, 1.8, 3.4), LION, 1, (0.4, 0.3, 0.6), (0, D(-25) * k, yaw))
    col_box("EntLions", (5.0, 5.0, 4.1), (lx, ly, G + 2.05))
    col_box("EntLions", (3.4 * LION_K, 4.2 * LION_K, 5.6 * LION_K), (lx, ly, z0 + 2.8 * LION_K))


def lions(rng):
    mb = NMB("ENT_Lions", "04_VILLAGE", rng, detail="near")
    for lx, ly in L.LIONS:
        komainu(mb, lx, ly, 1 if lx > 0 else -1)
    mb.finish()


def build():
    bridge(random.Random(5101))
    gate(random.Random(5102))
    lions(random.Random(5103))
