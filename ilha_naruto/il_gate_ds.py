# il_gate_ds - portao de compra DEMON SLAYER (area 3): "PORTAO NICHIRIN". Dono: zona gates.
# Portao japones de madeira laqueada: dois pilares vermelhos octogonais com luva preta (nemaki) e aneis de ouro, trilho
# preto da barreira, viga baixa (nuki) que passa dos pilares, viga alta (kashiranuki) com montantes e roseta de ouro,
# misulas pretas e um telhado KARAHAFU (empena em sino) de telha cinza-ardosia com tabeira preta e pontas de ouro.
# Crista no GEGYO (centro da tabeira, frente e costas): TSUBA de ferro preto com aro de ouro e duas KATANAS nichirin
# cruzadas atras dela (laminas com lombo preto recortando contra a tabeira e o telhado); remate de ouro (joia) no meio
# da cumeeira = ponto mais alto (30,35). Parede da empena em reboco creme com grade de madeira escura.
# Ornamentos laterais (fora de +-12): lanternas de papel penduradas nas pontas do nuki, 12 cachos curtos de glicinia
# sob os beirais (glicinia MUITO controlada: so nos 4 cantos) e um suporte de espadas (katana-kake) de laca preta ao
# pe de cada pilar, com uma bainha vermelha e uma lamina exposta. Barreira vermelho-carmim (P_DS_Glow) retangular.
#
# PLANO (referencial do portao; z relativo ao tabuleiro):
#   vao 16 x 18 (retangulo)            pilares octogonais 2.6 em x = +-9.8 (face interna 8.5), trilho x 8.0..8.6
#   nuki z 18.35..19.7, x +-13.9      kashiranuki z 21.1..22.4, x +-11.4      misulas ate 23.45
#   karahafu: meia-largura 14.3, beiral z 22.6 nas pontas, cume 26.0 (+1.0 de telha), y +-4.2, tabeira ate +-4.65
#   crista (gegyo): tsuba R 2.0 em z 24.9, y +-5.6 | katanas a +-35 graus, pontas em z 28.5 (x +-5.2)
#   remate de ouro na cumeeira ate z 30.35 | lanternas x +-13.2 (z ~14.6..17.4) | glicinia x +-(12.3..13.9), y +-3.3
#   suportes de espadas x +-14.4 (12.6..16.2), y -2.8
# RODADA 2 (critica: "papelao; a barreira carmim le como PORTA VERMELHA fechada; nao e familia do DB"):
#   - CONTRASTE: pilares octogonais 3,0 em P_DS_Black com ANEIS vermelhos (nemaki de laca + 2 aneis) e nuki preto: a
#     barreira carmim fica emoldurada por preto nos 3 lados (le como energia, nao como folha de porta);
#   - PROFUNDIDADE (koraimon): pilares de apoio (hikae-bashira) atras, em y 6,4, ligados por 2 vigas de laca e
#     cobertos por telhadinhos proprios -> moldura de y -1,9 a 7,8;
#   - kit de familia: soleira 22 x 10, plintos, 2 pedestais 4x4x4 com SUPORTE ALTO DE KATANAS (3 espadas), 2 lanternas
#     de pedra e 4 TSUBAS flutuantes em brasa (VFX_GATE_DemonSlayer_Tsuba_*, miolo carmim aceso); os suportes baixos
#     do chao sairam;
#   - telha em Roof_Blue (menos 1 material novo); folgas >= 0,1 entre materiais (pontas de ouro da tabeira, capas
#     sob a cumeeira).
import math, random
import fm_lib
from fm_lib import S
import il_gate_std as GS
import il_gates_kit as GK
from il_gates_kit import G, GMB
import fm_portal_kit as K

KEY = "DemonSlayer"
# ------------------------------------------------------------------ materiais novos (3 dos 12 da zona)
_M = fm_lib.MATS.setdefault
_M("Metal_GateDS_Blade", (S(206, 214, 226), 0.18, 0.85, 0, None, 0.02))   # aco da lamina nichirin
_M("Leaf_GateDS_Wisteria", (S(176, 132, 232), 0.75, 0.0, 0, None, 0.06))  # glicinia lilas
RED, BLK, GOLD, STN = "Wood_Lacquer_Red", "P_DS_Black", "Metal_Gold", "Stone_Dark"
TILE, BLADE, WIS = "Roof_Blue", "Metal_GateDS_Blade", "Leaf_GateDS_Wisteria"
WD, PLA, LAN = "Wood_Dark", "Plaster_Cream", "Lantern_Glow"
GLOW = "P_DS_Glow"

CAMS = GK.cams_for(KEY)

PX = 9.8                     # eixo dos pilares
RW = 14.3                    # meia-largura do karahafu
ZE, RH, RU = 22.6, 3.4, 0.6  # beiral nas pontas, altura do sino, arrebite das pontas
RD = 4.2                     # meia-profundidade do telhado
CREST_Z = 24.9
A = "Gate" + KEY


def zb(x):
    """face de baixo do telhado karahafu (sino: convexo no meio, concavo e arrebitado nas pontas)"""
    t = min(1.0, abs(x) / RW)
    return ZE + RH * 0.5 * (1.0 + math.cos(math.pi * t)) + RU * t ** 4


def _oct(cx, cy, a, c):
    h = a / 2
    return [(cx - h + c, cy - h), (cx + h - c, cy - h), (cx + h, cy - h + c), (cx + h, cy + h - c),
            (cx + h - c, cy + h), (cx - h + c, cy + h), (cx - h, cy + h - c), (cx - h, cy - h + c)]


def _pillars(g, mb):
    for s in (-1, 1):
        px = s * PX
        g.box(mb, px - 1.65, px + 1.65, -1.8, 1.8, GK.BASE_Z, 0.9, STN, 0.15)            # base (face interna 8,15)
        g.prism(mb, _oct(px, 0.0, 3.0, 0.5), 0.9, 22.4, BLK, 0.08)                      # pilar PRETO 3 x 3
        g.prism(mb, _oct(px, 0.0, 3.4, 0.56), 0.9, 3.6, RED, 0.06)                      # nemaki de laca vermelha
        g.prism(mb, _oct(px, 0.0, 3.4, 0.56), 3.6, 3.9, GOLD, 0.0)                     # face interna 8,1
        for z0, z1 in ((9.3, 9.9), (17.3, 17.95)):                                      # aneis vermelhos
            g.prism(mb, _oct(px, 0.0, 3.3, 0.55), z0, z1, RED, 0.0)
            g.prism(mb, _oct(px, 0.0, 3.3, 0.55), z1, z1 + 0.25, GOLD, 0.0)
        # trilho da barreira (2 reguas pretas na face interna)
        xa, xb = sorted((s * 8.0, s * 8.6))
        for y0, y1 in ((-0.8, -0.32), (0.32, 0.8)):
            g.box(mb, xa, xb, y0, y1, 0.0, 18.35, BLK, 0.04)
        # misula (daito) + bracos (hijiki) sob o beiral
        g.box(mb, px - 1.5, px + 1.5, -1.3, 1.3, 22.4, 23.45, BLK, 0.1)
        g.box(mb, px - 1.6, px + 1.6, -1.4, 1.4, 22.4, 22.6, GOLD, 0.0)
        for yy in (-2.6, 2.6):
            g.box(mb, px - 0.45, px + 0.45, yy - 1.1, yy + 1.1, 23.0, 23.5, BLK, 0.06)
    # trilho de cima (a barreira acaba em 18.0 entre as reguas)
    for y0, y1 in ((-0.8, -0.32), (0.32, 0.8)):
        g.box(mb, -8.6, 8.6, y0, y1, 18.0, 18.36, BLK, 0.04)


def _beams(g, mb):
    g.box(mb, -13.9, 13.9, -0.75, 0.75, 18.35, 19.7, BLK, 0.12)                          # nuki (preto)
    for s in (-1, 1):
        xa, xb = sorted((s * 13.9, s * 14.15))
        g.box(mb, xa, xb, -0.8, 0.8, 18.3, 19.75, GOLD, 0.05)                           # ponteira de ouro
        xa, xb = sorted((s * 4.6, s * 5.5))
        g.box(mb, xa, xb, -0.45, 0.45, 19.7, 21.1, RED, 0.06)                           # montantes (tsuka)
    g.box(mb, -11.4, 11.4, -0.85, 0.85, 21.1, 22.4, RED, 0.12)                          # kashiranuki
    # roseta de ouro (4 lobos) entre as vigas, atravessando a espessura (le igual pela frente e por tras)
    pts = []
    for k in range(24):
        a = math.tau * k / 24
        r = 0.95 * (1.0 - 0.18 * (1.0 - abs(math.cos(2 * a))))
        pts.append((math.cos(a) * r, 20.4 + math.sin(a) * r))
    g.plate(mb, pts, 0.0, 1.9, GOLD)


def _roof(g, mb):
    n = 36
    xs = [-RW + 2 * RW * i / n for i in range(n + 1)]
    top = [(x, zb(x) + 1.0) for x in xs]
    bot = [(x, zb(x)) for x in xs]
    g.band(mb, top, bot, -RD, RD, TILE, 0.14)                                           # corpo do telhado
    g.band(mb, bot, [(x, z - 0.35) for x, z in bot], -RD + 0.3, RD - 0.3, WD, 0.0)      # forro de tabuas
    # telhas capa (maru-gawara) de frente para tras
    k = 0
    x = -RW + 0.55
    while x <= RW - 0.5:
        if abs(x) > 1.25:                     # as do meio ficariam rente a cumeeira (z-fighting): a cumeeira cobre
            g.cyl(mb, 0.27, 2 * RD, (x, 0.0, zb(x) + 1.08), TILE, 6, bev=0.0, axis="y")
        x += 0.95
        k += 1
    # tabeiras (hafu) pretas na frente e atras, pontas e gegyo de ouro
    xs2 = [-RW - 0.25 + 2 * (RW + 0.25) * i / n for i in range(n + 1)]
    for y0, y1 in ((-RD - 0.45, -RD + 0.05), (RD - 0.05, RD + 0.45)):
        g.band(mb, [(x, zb(x) + 1.45) for x in xs2], [(x, zb(x) - 0.55) for x in xs2], y0, y1, BLK, 0.1)
        for s in (-1, 1):
            xa, xb = sorted((s * (RW - 0.5), s * (RW + 0.4)))
            g.box(mb, xa, xb, y0 - 0.12, y1 + 0.12, zb(RW) - 0.7, zb(RW) + 1.6, GOLD, 0.06)
    # cumeeira (de frente para tras) com discos de ouro nas pontas
    zr = zb(0.0) + 0.9
    g.box(mb, -0.75, 0.75, -RD - 0.55, RD + 0.55, zr, zr + 0.95, BLK, 0.1)
    for y in (-RD - 0.6, RD + 0.6):
        g.cyl(mb, 0.55, 0.3, (0.0, y, zr + 0.48), GOLD, 12, bev=0.0, axis="y")
    # parede da empena (tsumakabe): reboco creme com grade de madeira escura
    xw = PX
    xs3 = [-xw + 2 * xw * i / 24 for i in range(25)]
    g.band(mb, [(x, zb(x) - 0.3) for x in xs3], [(x, 22.4) for x in xs3], -0.35, 0.35, PLA, 0.0)
    for x in (-6.6, -3.3, 0.0, 3.3, 6.6):
        g.box(mb, x - 0.2, x + 0.2, -0.47, 0.47, 22.4, zb(x) - 0.3, WD, 0.0)
    g.box(mb, -xw, xw, -0.47, 0.47, 23.1, 23.4, WD, 0.0)


def mokko(r, cz, n=32, cx=0.0):
    """contorno de tsuba mokko (4 lobos)"""
    pts = []
    for k in range(n):
        a = math.tau * k / n
        rr = r * (1.0 - 0.14 * (1.0 - abs(math.cos(2 * a))) ** 1.5)
        pts.append((cx + math.cos(a) * rr, cz + math.sin(a) * rr))
    return pts


def _crest(g, mb):
    """crista no GEGYO (centro da tabeira do karahafu), na frente e nas costas: TSUBA grande de ferro preto com aro de
    ouro e duas katanas nichirin cruzadas atras dela (cabos pretos com trancado de ouro para baixo, laminas com lombo
    preto para cima). As laminas claras recortam contra a tabeira preta e o telhado; os cabos, contra o reboco creme."""
    L, al = 8.4, math.radians(35.0)
    hl = L * 0.24
    cross = hl + 0.1                                 # cruzam na altura das guardas (escondidas pela tsuba grande)
    for sy in (-1, 1):
        yf = sy * (RD + 0.45)                        # face externa da tabeira
        cz = CREST_Z
        for s, dy in ((1, 0.62), (-1, 0.42)):
            yy = yf + sy * dy
            u = g.D(s * math.cos(al), 0.0, math.sin(al))
            grip = g.P(0.0, yy, cz) - u * cross
            nrm = g.uy if s > 0 else -g.uy
            K.katana(mb, grip, u, nrm, length=L, width=0.95, blade_m=BLADE, grip_m=BLK, guard_m=GOLD)
            mb.beam(grip - u * 0.1, grip + u * 0.3, 0.76, 0.64, GOLD, 0.0)            # kashira (0,1 fora do cabo)
            for k in range(2):                                                         # trancado do cabo
                c = grip + u * (0.6 + 0.5 * k)
                mb.beam(c - u * 0.12, c + u * 0.12, 0.76, 0.64, GOLD, 0.0)
            v = nrm.cross(u).normalized()
            lb = L - hl
            base = grip + u * (hl + 0.2)
            pts = [base + u * (t * lb * 0.84) + v * (0.95 / 2 - 0.1 + 0.06 * lb * t * t)
                   for t in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
            K.taper_tube(mb, pts, [0.15, 0.15, 0.14, 0.13, 0.12, 0.1], BLK, 6, True, up=tuple(g.uy))
        yt = yf + sy * 0.95
        # camadas com folga >= 0,1: aro de ouro [yt-0,18, yt+0,18], ferro preto ate yt+0,30, cubo/furos ate yt+0,44
        g.plate(mb, mokko(2.0, cz), yt, 0.36, GOLD)
        g.plate(mb, mokko(1.78, cz), yt + sy * 0.12, 0.36, BLK)
        g.cyl(mb, 0.55, 0.5, (0.0, yt + sy * 0.19, cz), GOLD, 12, bev=0.0, axis="y")
        for k in (0, 2):                                                               # hitsu-ana
            cx = (1.0 if k == 0 else -1.0) * 1.12
            g.plate(mb, [(cx - 0.24, cz - 0.55), (cx + 0.24, cz - 0.55), (cx + 0.24, cz + 0.55),
                         (cx - 0.24, cz + 0.55)], yt + sy * 0.19, 0.5, GOLD)
    # remate de ouro (joia em chama) no meio da cumeeira: o ponto alto da silhueta
    zr = zb(0.0) + 0.9 + 0.95
    g.cyl(mb, 0.55, 0.4, (0.0, 0.0, zr + 0.2), GOLD, 10, bev=0.0)
    g.ico(mb, 0.72, (0.0, 0.0, zr + 1.0), GOLD, 1, (1.0, 1.0, 1.25))
    g.cone(mb, (0.0, 0.0, zr + 1.6), (0.0, 0.0, zr + 2.5), 0.4, 0.04, GOLD, 8)


def _lanterns(g, mb):
    for s in (-1, 1):
        K.chochin(mb, g.P(s * 13.2, 0.0, 18.35), r=1.3, h=2.8, paper=LAN, cap=BLK, band=RED, hang=0.7, n=10,
                  rod_m=BLK)


def _wisteria(g, mb, rng):
    for s in (-1, 1):
        for yy in (-3.3, 3.3):
            for i, x in enumerate((12.3, 13.1, 13.9)):
                top = zb(x) - 0.25
                ln = (2.6, 2.1, 1.6)[i] * rng.uniform(0.85, 1.1)
                K.raceme(mb, g.P(s * x, yy + rng.uniform(-0.25, 0.25), top), ln, WIS, 0.46, rng)
            g.ico(mb, 0.72, (s * 13.1, yy, zb(13.1) - 0.2), WIS, 1, (1.9, 1.1, 0.55))


RPX, RPY = PX, 6.4          # pilares de apoio (hikae-bashira), atras dos principais


def _rear_posts(g, mb):
    """koraimon: pilar de apoio preto atras de cada pilar principal, nemaki vermelho, 2 vigas de laca ligando os dois
    e um telhadinho de duas aguas (cumeeira de frente para tras) por cima. O beiral de dentro fica em |x| >= 8,1."""
    for s in (-1, 1):
        px = s * RPX
        g.box(mb, px - 1.4, px + 1.4, RPY - 1.4, RPY + 1.4, GK.BASE_Z, 0.9, STN, 0.12)
        g.box(mb, px - 1.0, px + 1.0, RPY - 1.0, RPY + 1.0, 0.9, 15.0, BLK, 0.08)
        g.box(mb, px - 1.2, px + 1.2, RPY - 1.2, RPY + 1.2, 0.9, 2.7, RED, 0.06)
        g.box(mb, px - 1.3, px + 1.3, RPY - 1.3, RPY + 1.3, 2.7, 2.95, GOLD, 0.0)
        for z in (7.0, 12.2):
            g.box(mb, px - 0.4, px + 0.4, 1.3, 5.5, z, z + 1.0, RED, 0.05)
            for yy in (1.9, 4.9):                                                     # cavilhas de ouro
                g.box(mb, px - 0.52, px + 0.52, yy - 0.2, yy + 0.2, z + 0.3, z + 0.7, GOLD, 0.0)
        top = [(px - 1.7, 14.7), (px, 16.1), (px + 1.7, 14.7)]
        bot = [(px - 1.7, 14.25), (px, 15.65), (px + 1.7, 14.25)]
        g.band(mb, top, bot, 1.8, 8.0, TILE, 0.0)
        g.box(mb, px - 0.32, px + 0.32, 1.7, 8.1, 15.9, 16.45, BLK, 0.0)
        g.cyl(mb, 0.42, 0.3, (px, 8.2, 16.17), GOLD, 10, bev=0.0, axis="y")


def _rack(g, mb, s):
    """guardiao do pedestal: SUPORTE ALTO DE KATANAS (katana-kake) de laca preta, 3 espadas viradas para quem chega:
    bainha vermelha, lamina nichirin exposta e bainha preta com aneis de ouro"""
    cx, cy = s * GK.PED_C[0], GK.PED_C[1]
    z0 = GK.PED_TOP
    g.box(mb, cx - 1.8, cx + 1.8, cy - 0.6, cy + 0.6, z0, z0 + 0.4, BLK, 0.0)
    for dx in (-1.35, 1.35):
        g.box(mb, cx + dx - 0.24, cx + dx + 0.24, cy - 0.3, cy + 0.3, z0 + 0.4, z0 + 5.1, BLK, 0.0)
        for z in (1.4, 2.7, 4.0):
            g.box(mb, cx + dx - 0.2, cx + dx + 0.2, cy - 1.0, cy - 0.3, z0 + z, z0 + z + 0.28, BLK, 0.0)
    g.box(mb, cx - 1.95, cx + 1.95, cy - 0.35, cy + 0.35, z0 + 4.7, z0 + 5.1, BLK, 0.0)       # travessa de cima
    for sx in (-1, 1):
        xa, xb = sorted((cx + sx * 1.95, cx + sx * 2.25))
        g.box(mb, xa, xb, cy - 0.47, cy + 0.47, z0 + 4.58, z0 + 5.22, GOLD, 0.0)
    y = cy - 0.72
    # as tsubas ficam FORA do montante (x 1,11..1,59): em 1,8 (sem face rente ao montante)
    # 1: bainha vermelha (cabo para fora)
    z = z0 + 1.4 + 0.28 + 0.22
    g.beam(mb, (cx - s * 2.0, y, z), (cx + s * 1.7, y, z), 0.44, 0.44, RED, 0.0)
    g.box(mb, *sorted((cx - s * 2.0, cx - s * 2.3)), y - 0.28, y + 0.28, z - 0.28, z + 0.28, GOLD, 0.0)
    g.cyl(mb, 0.52, 0.18, (cx + s * 1.8, y, z), GOLD, 10, bev=0.0, axis="x")
    g.beam(mb, (cx + s * 1.85, y, z), (cx + s * 2.85, y, z), 0.4, 0.4, BLK, 0.0)
    # 2: lamina exposta (cabo para fora)
    z = z0 + 2.7 + 0.28 + 0.2
    K.katana(mb, g.P(cx + s * 3.05, y, z), g.D(-s, 0.0, 0.0), g.uy if s > 0 else -g.uy, length=4.8, width=0.62,
             blade_m=BLADE, grip_m=BLK, guard_m=GOLD)
    # 3: bainha preta com aneis de ouro e cabo vermelho
    z = z0 + 4.0 + 0.28 + 0.2
    g.beam(mb, (cx - s * 2.0, y, z), (cx + s * 1.7, y, z), 0.4, 0.4, BLK, 0.0)
    for t in (-1.6, 0.2):
        g.beam(mb, (cx + s * (t - 0.14), y, z), (cx + s * (t + 0.14), y, z), 0.62, 0.62, GOLD, 0.0)
    g.cyl(mb, 0.5, 0.18, (cx + s * 1.8, y, z), GOLD, 10, bev=0.0, axis="x")
    g.beam(mb, (cx + s * 1.85, y, z), (cx + s * 2.85, y, z), 0.38, 0.38, RED, 0.0)


def _tsuba(g):
    def build(mb, p):
        u = tuple(g.ux)
        # tsuba em brasa (miolo carmim aceso, como as esferas do DB brilham no ceu), aro, cubo e furos de ouro
        K.plate(mb, mokko(1.4, 0.0), p, u, (0, 0, 1), 0.3, GOLD)
        K.plate(mb, mokko(1.18, 0.0), p, u, (0, 0, 1), 0.52, GLOW)
        K.plate(mb, [(math.cos(math.tau * k / 8) * 0.38, math.sin(math.tau * k / 8) * 0.38) for k in range(8)],
                p, u, (0, 0, 1), 0.76, GOLD)
        for cx in (-0.78, 0.78):
            K.plate(mb, [(cx - 0.18, -0.42), (cx + 0.18, -0.42), (cx + 0.18, 0.42), (cx - 0.18, 0.42)], p, u,
                    (0, 0, 1), 0.76, GOLD)
    return build


def _collision(g):
    for s in (-1, 1):
        g.col(A, s * 8.0, s * 11.6, -1.8, 1.8, 0.0, 23.45)
        g.col(A, s * (RPX - 1.4), s * (RPX + 1.4), RPY - 1.4, RPY + 1.4, GK.BASE_Z, 15.0)
    GK.family_collision(g, A, ped_h=5.3)


def build_gate(gx, gy, gz, yaw):
    rng = random.Random(3303)
    F = GS.gate_frame(gx, gy, gz, yaw)
    g = G(F)
    mb = GMB("GATE_%s_Frame" % KEY, rng, detail="hero", vcap=1)
    _pillars(g, mb)
    _beams(g, mb)
    _roof(g, mb)
    _crest(g, mb)
    _lanterns(g, mb)
    _wisteria(g, mb, rng)
    _rear_posts(g, mb)
    GK.family_base(g, mb, A, accent=RED, glow=LAN, roof=TILE, finial=GOLD)
    for s in (-1, 1):
        _rack(g, mb, s)
        GK.inlay(g, mb, s, mokko(0.78, 0.0), GOLD)
    GK.tag(mb.finish(), KEY, "frame")
    GK.emblems(KEY, g, "Tsuba", _tsuba(g))
    _collision(g)
    GS.barrier(KEY, F, GLOW, shape="rect", rng=rng)
    GS.markers(KEY, F, yaw)
    GK.scale_dummy(KEY, g)
    GK.make_cams(CAMS)


def build():
    gx, gy, gz, yaw = GS.gallery_slot(KEY)
    build_gate(gx, gy, gz, yaw)
