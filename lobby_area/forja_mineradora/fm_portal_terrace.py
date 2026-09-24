# fm_portal_terrace - dressing do terraco dos portais:
#   * cada escada anuncia o seu mundo (so dressing na borda do poco: a geometria de TER_PortalStairs, a largura util
#     dos lances e as rotas nao mudam). As pecas vao para o MB do proprio portal (dentro do lote px +-14):
#       Naruto: toro de pedra, nobori e sakura      DB: pedestais com as 7 esferas subindo ao lado
#       Shadow: grade gotica de ferro e velas roxas  DS: pergola de glicinia e lanternas de papel vermelhas
#       OP: corrimao de corda, tabuas de cais, barris  OPM: guarda-corpo de concreto com faixa neon, outdoor
#   * PORTAL_<key>_Difficulty: placa de dificuldade (1..6 pontos, moldura no BRILHO DO PORTAL v3 - DIFF_GLOW, nao o
#     K.GLOW antigo das espirais) + caixote de gemas brutas (minerio vindo daquele mundo; DIFF_GEM) ao pe de cada escada
#   * centro do terraco (x -26..26), entre Shadow Garden e Demon Slayer, falando a lingua dos portais v3 (mesmas
#     paletas e os mesmos helpers de fm_pv3_shadowgarden / fm_pv3_demonslayer):
#       PORTAL_Terrace_Ruin (x -26..-17): pano de parede gotica ARRUINADO de obsidiana com janela ogival vazada e
#         remates de prata (eco do Arco da Lua), mureta gotica partida, arvore morta retorcida em P_SG_Deadwood,
#         roseira seca com rosas violetas (miolo aceso) e lanterna gotica de prata na frente. Nada de cristal.
#       PORTAL_Terrace_Wisteria (x 16..26): glicinia grande + glicinia menor no estilo do DS (copa em guarda-chuva de
#         massas lisas lilas e CACHOS EM CAMADAS DE PETALAS EM SINO - cascade_plan/cascade do fm_pv3_demonslayer),
#         toro e mureta de pedra sagrada (Stone_DS_Rock).
#     Dois objetos (nao um): o fold de materiais pequenos do export junta cores parecidas de mesmo Enum DENTRO do
#     objeto - num objeto so, o remate prata do lado sombrio viraria lilas da glicinia. Os vaos de 4 studs entre
#     portais vizinhos ficam limpos (cada portal e uma peca independente).
import math
import random
from mathutils import Vector
from fm_lib import MB, D, col_box
from fm_parts import crate, barrel
import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L

T = L.TERR
PY = L.PORTAL_Y
Y0 = L.FLIGHT2_Y1
A = "Portal"
SY0, SY1 = 86.0, 99.4      # faixa ao lado do lance 2 (terraco, fora do poco px +-7.4)

# brilho de cada portal v3 (moldura e pontos da placa de dificuldade). K.GLOW continua sendo o contrato das
# espirais (aro de energia) e nao muda.
DIFF_GLOW = {"Naruto": "P_Naruto_Rim_Glow", "DragonBall": "P_DB_Rim_Glow", "ShadowGarden": "P_Shadow_Glow",
             "DemonSlayer": "P_DS_Glow", "OnePiece": "P_OP_Glow", "OnePunchMan": "P_OPM_Glow"}
# gemas do caixote: o brilho do portal, exceto o DB - o azul claro do aro (Kamehameha) em gema grossa lia como gelo;
# la o minerio e o ambar das esferas do dragao (P_DB_Ball_Amber, ja no portal DB)
DIFF_GEM = dict(DIFF_GLOW, DragonBall="P_DB_Ball_Amber")
# paletas do centro (as mesmas dos portais v3: nenhum material novo no export)
OBS, SIL, DW, ROSE, CORE = "P_SG_Obsidian", "P_SG_Silver", "P_SG_Deadwood", "P_SG_Rose", "P_SG_Core_Glow"
WIS, WIS_MID, WIS_TIP, BARK_DS = "P_DS_Glicinia", "P_DS_GlicMid", "P_DS_GlicTip", "Bark_Dark"
ROCK_DS = "Stone_DS_Rock"
XMIN_C = L.PORTAL_X[2] + 14.0 + 4.0 + 0.1     # -25.9: lote do Shadow Garden (px+14) mais a folga de 4
XMAX_C = L.PORTAL_X[3] - 14.0 - 4.0 - 0.1     # 25.9: lote do Demon Slayer (px-14) menos a folga de 4


def capsule(mb, loc, yaw, s=1.0):
    """capsula gigante (brinquedo) deitada e meio enterrada"""
    x, y, z = loc
    d = V(math.cos(yaw), math.sin(yaw), 0.12).normalized()
    c = V(x, y, z)
    mb.rod(c - d * 1.9 * s, c, 1.35 * s, "P_DB_White", 14)
    mb.rod(c, c + d * 1.9 * s, 1.35 * s, "P_DB_Orange", 14)
    mb.rod(c - d * 0.25 * s, c + d * 0.25 * s, 1.42 * s, "P_DB_Blue", 14)
    mb.ico(1.35 * s, c - d * 1.9 * s, "P_DB_White", 2)
    mb.ico(1.35 * s, c + d * 1.9 * s, "P_DB_Orange", 2)
    mb.cyl(0.45 * s, 0.4 * s, c - d * 1.0 * s + V(0, 0, 1.35 * s), (0, 0, 0), "P_DB_Blue", 10, bevel=0.0)


def bollard(mb, x, y, z):
    mb.cyl(0.6, 1.6, (x, y, z + 0.8), (0, 0, 0), "P_OPM_Concrete", 10, bevel=0.1)
    mb.cyl(0.64, 0.35, (x, y, z + 1.1), (0, 0, 0), "P_OPM_Yellow", 10, bevel=0.0)
    mb.cyl(0.64, 0.25, (x, y, z + 0.65), (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    col_box(A, (1.2, 1.2, 1.8), (x, y, z + 0.9))


# ------------------------------------------------------------------ dressing das escadas (vai no MB do portal)
def _nobori(mb, x, y, s, h=9.0):
    blk = "Wood_Dark"
    mb.box((0.4, 0.4, h), (x, y, T + h / 2), (0, 0, 0), blk, 0.0)
    mb.box((2.2, 0.3, 0.3), (x + s * 1.0, y, T + h - 0.5), (0, 0, 0), blk, 0.0)
    mb.box((1.7, 0.18, 6.0), (x + s * 1.05, y, T + h - 3.6), (0, 0, 0), "P_Naruto_Orange", 0.0)
    mb.box((0.28, 0.2, 6.0), (x + s * 1.95, y, T + h - 3.6), (0, 0, 0), "P_Naruto_Tile", 0.0)
    mb.cyl(0.5, 0.24, (x + s * 1.05, y - 0.12, T + h - 2.5), (D(90), 0, 0), "P_Naruto_Tile", 8, bevel=0.0)
    col_box(A, (0.6, 0.6, h), (x, y, T + h / 2))


def stairs_naruto(mb, px, rng):
    for s in (-1, 1):
        x = px + s * 8.7
        # toro baixinho (so a camara e o chapeu sobre um soco) no alto da escada
        mb.box((1.3, 1.3, 1.6), (x, 97.8, T + 0.8), (0, 0, 0), "Stone_Dark", 0.08)
        mb.cyl(0.55, 0.9, (x, 97.8, T + 2.05), (0, 0, D(30)), "P_Naruto_Glow", 6, bevel=0.0)
        mb.cyl(1.25, 0.6, (x, 97.8, T + 2.8), (0, 0, 0), "Stone_Dark", 6, r2=0.35, bevel=0.0)
        col_box(A, (1.6, 1.6, 3.2), (x, 97.8, T + 1.6))
        for y in (88.6, 92.8):
            _nobori(mb, px + s * 8.5, y, s)
    for (dx, y, h) in ((-10.6, 91.0, 7.5), (10.2, 95.2, 5.8)):
        K.sakura_small(mb, (px + dx, y, T), h, rng, reach=0.18)
        col_box(A, (1.2, 1.2, 4.0), (px + dx, y, T + 2.0))


def stairs_db(mb, px, rng):
    """as 7 esferas sobem ao lado da escada em pedestais cada vez mais altos (1 estrela -> 7 estrelas)"""
    for k in range(7):
        s = -1 if k % 2 == 0 else 1
        y = 86.6 + k * 2.1
        x = px + s * 8.9
        h = 1.2 + k * 0.5
        mb.cyl(0.9, h, (x, y, T + h / 2), (0, 0, 0), "P_DB_White", 8, bevel=0.0)
        mb.cyl(1.0, 0.3, (x, y, T + h - 0.1), (0, 0, 0), "P_DB_Orange", 8, bevel=0.0)
        mb.cyl(1.0, 0.25, (x, y, T + 0.35), (0, 0, 0), "P_DB_Blue", 8, bevel=0.0)
        b = V(x, y, T + h + 0.85)
        mb.ico(0.8, b, "P_DB_Ball", 2)
        for j in range(k + 1):
            if k == 0:
                p = b + V(0, -0.76, 0)
            else:
                a = D(90 + 360 * j / (k + 1))
                p = b + V(math.cos(a) * 0.36, -0.7, math.sin(a) * 0.36)
            K.octa(mb, p, 0.15, 0.15, "P_DB_Star")
        col_box(A, (1.8, 1.8, h + 1.6), (x, y, T + (h + 1.6) / 2))


def stairs_shadow(mb, px, rng):
    ir, gl = "Metal_Dark", "P_Shadow_Glow"
    for s in (-1, 1):
        x = px + s * 8.3
        ys = [SY0 + k * 1.1 for k in range(13)]
        for y in ys:
            mb.box((0.2, 0.2, 2.8), (x, y, T + 1.4), (0, 0, 0), ir, 0.0)
            K.cone(mb, V(x, y, T + 2.8), V(x, y, T + 3.5), 0.2, 0.0, ir, 4)
        for z in (T + 0.6, T + 2.3):
            mb.box((0.18, ys[-1] - ys[0] + 0.2, 0.26), (x, (ys[0] + ys[-1]) / 2, z), (0, 0, 0), ir, 0.0)
        for k in range(0, 12, 3):     # arcos ogivais entre montantes (le como grade gotica, nao cerca)
            y0, y1 = ys[k], ys[k + 3]
            arc = [V(x, y0 + (y1 - y0) * t, T + 1.5 + 0.7 * math.sin(math.pi * t) ** 0.6) for t in (0, 0.25, 0.5, 0.75, 1)]
            mb.tube(arc, 0.07, ir, 4)
        col_box(A, (0.6, ys[-1] - ys[0], 3.6), (x, (ys[0] + ys[-1]) / 2, T + 1.8))
        # velas roxas em castical de ferro
        for y in (88.6, 95.8):
            cx = px + s * 10.0
            mb.cyl(0.55, 0.3, (cx, y, T + 0.15), (0, 0, 0), ir, 6, bevel=0.0)
            mb.cyl(0.14, 2.6, (cx, y, T + 1.45), (0, 0, 0), ir, 5, bevel=0.0)
            mb.cyl(0.6, 0.22, (cx, y, T + 2.75), (0, 0, 0), ir, 6, bevel=0.0)
            for ox, hh in ((-0.28, 0.9), (0.28, 0.6), (0.0, 1.2)):
                mb.cyl(0.14, hh, (cx + ox, y, T + 2.86 + hh / 2), (0, 0, 0), "P_Shadow_Cloth", 6, bevel=0.0)
                K.octa(mb, (cx + ox, y, T + 2.86 + hh + 0.2), 0.12, 0.22, gl)
            col_box(A, (1.2, 1.2, 4.0), (cx, y, T + 2.0))


def stairs_demonslayer(mb, px, rng):
    ch, gl, wis = "P_DS_Char", "P_DS_Glow", "P_DS_Wisteria"
    zb = T + 8.0
    ys = (86.6, 98.8)
    # pergola leve: esteios finos, 2 longarinas e ripas finas; os cachos pendem entre as ripas
    for s in (-1, 1):
        xi, xo = px + s * 8.6, px + s * 12.2
        for x in (xi, xo):
            for y in ys:
                mb.box((0.42, 0.42, zb - T), (x, y, (T + zb) / 2), (0, 0, 0), ch, 0.0)
                col_box(A, (0.8, 0.8, zb - T), (x, y, (T + zb) / 2))
            mb.box((0.36, ys[1] - ys[0] + 1.0, 0.42), (x, (ys[0] + ys[1]) / 2, zb + 0.2), (0, 0, 0), ch, 0.0)
        for k in range(7):
            y = ys[0] + (ys[1] - ys[0]) * k / 6
            mb.box((abs(xo - xi) + 1.0, 0.24, 0.26), ((xi + xo) / 2, y, zb + 0.54), (0, 0, 0), ch, 0.0)
        for k in range(4):     # folhagem sobre as ripas (a pergola le como planta, nao como grade)
            y = ys[0] + 1.4 + (ys[1] - ys[0] - 2.8) * k / 3
            mb.ico(1.0, ((xi + xo) / 2 + rng.uniform(-0.3, 0.3), y, zb + 0.95), "Leaf_Pine_Light", 1, (1.8, 1.6, 0.55),
                   rot=(0, 0, rng.uniform(0, 3)))
        for k in range(8):
            x = xi + (xo - xi) * rng.uniform(0.12, 0.88)
            y = ys[0] + 0.4 + (ys[1] - ys[0] - 0.8) * (k + rng.uniform(0.15, 0.85)) / 8
            K.raceme(mb, V(x, y, zb + 0.45), rng.uniform(1.8, 2.8), wis, rng.uniform(0.36, 0.42), rng)
        K.chochin(mb, ((xi + xo) / 2, 92.7, zb + 0.6), r=0.7, h=1.3, paper=gl, cap=ch, hang=0.8, n=8, rod_m=ch)


def stairs_onepiece(mb, px, rng):
    for s in (-1, 1):
        x = px + s * 8.4
        ys = [SY0 + k * 4.45 for k in range(4)]
        tops = []
        for y in ys:
            mb.cyl(0.32, 3.0, (x, y, T + 1.5), (0, 0, rng.uniform(0, 1)), "Wood_Dark", 6, bevel=0.0)
            mb.cyl(0.36, 0.25, (x, y, T + 2.6), (0, 0, 0), "Rope", 6, bevel=0.0)
            tops.append(V(x, y, T + 2.6))
        for a_, b_ in zip(tops, tops[1:]):
            mb.tube([a_ + (b_ - a_) * t - V(0, 0, 0.6 * 4 * t * (1 - t)) for t in (0, 0.25, 0.5, 0.75, 1.0)], 0.12,
                    "Rope", 5)
        col_box(A, (0.7, ys[-1] - ys[0], 3.2), (x, (ys[0] + ys[-1]) / 2, T + 1.6))
    # tabuas de cais sobre o terraco (lado esquerdo) com barris
    K.deck(mb, px - 12.6, px - 9.4, 87.4, 97.4, T + 0.3, rng, "Wood_Plank", pw=1.0)
    for (x, y, z) in ((px - 11.0, 89.6, T + 0.3), (px - 11.2, 92.4, T + 0.3), (px + 10.6, 96.6, T)):
        K.barrel_small(mb, (x, y, z), 1.0, 2.3)
        col_box(A, (2.2, 2.2, 2.6), (x, y, z + 1.3))


def stairs_opm(mb, px, rng):
    con, gl, yel, dk = "P_OPM_Concrete", "P_OPM_Glow", "P_OPM_Yellow", "Metal_Dark"
    for s in (-1, 1):
        x = px + s * 8.3
        mb.box((0.7, SY1 - SY0, 1.3), (x, (SY0 + SY1) / 2, T + 0.65), (0, 0, 0), con, 0.08)
        mb.box((0.2, SY1 - SY0, 0.18), (x - s * 0.36, (SY0 + SY1) / 2, T + 1.15), (0, 0, 0), gl, 0.0)
        for y in (SY0 + 0.4, (SY0 + SY1) / 2, SY1 - 0.4):
            mb.box((0.95, 0.95, 1.6), (x, y, T + 0.8), (0, 0, 0), con, 0.06)
        col_box(A, (0.8, SY1 - SY0, 2.0), (x, (SY0 + SY1) / 2, T + 1.0))
    # outdoor vertical sobre coluna e frade zebrado (antes no vao OP|OPM; agora dentro do lote)
    bx, by = px - 12.1, 94.6
    mb.box((1.0, 1.0, 9.0), (bx, by, T + 4.5), (0, 0, 0), con, 0.1)
    mb.box((3.2, 0.8, 6.4), (bx, by - 0.2, T + 11.4), (0, 0, 0), dk, 0.08)
    mb.box((2.6, 0.2, 5.6), (bx, by - 0.65, T + 11.4), (0, 0, 0), "P_OPM_DarkGlass", 0.0)
    for z in (T + 14.3, T + 8.5):
        mb.box((2.8, 0.25, 0.2), (bx, by - 0.7, z), (0, 0, 0), gl, 0.0)
    mb.cyl(1.1, 0.25, (bx, by - 0.8, T + 12.2), (D(90), 0, 0), yel, 14, bevel=0.0)
    mb.box((0.9, 0.2, 0.8), (bx, by - 0.95, T + 12.3), (0, 0, 0), "P_OPM_Red", 0.0)
    col_box(A, (1.4, 1.4, 9.0), (bx, by, T + 4.5))
    bollard(mb, px - 12.4, 97.6, T)


# ------------------------------------------------------------------ placa de dificuldade + caixote de cristais
def difficulty(key, px, i, rng):
    # semente propria: a placa sai igual mesmo que o dressing das escadas (que consome o rng comum) mude
    rng = random.Random(3100 + i)
    mb = K.LeanMB("PORTAL_%s_Difficulty" % key, "06_PORTALS", rng, vcap=1)
    g = DIFF_GLOW[key]
    F = L.FLOOR
    x, y = px + 7.8, L.FLIGHT1_Y0 - 1.5
    mb.box((1.0, 1.0, 6.0), (x, y, F + 3.0), (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((3.6, 0.6, 2.2), (x, y - 0.3, F + 5.4), (0, 0, 0), "Wood_Plank", 0.08)
    # moldura luminosa na cor do portal (e o que o vfx pulsa) + pontos de dificuldade
    for dz in (-1.12, 1.12):
        mb.box((3.8, 0.18, 0.16), (x, y - 0.66, F + 5.4 + dz), (0, 0, 0), g, 0.0)
    for dx in (-1.83, 1.83):
        mb.box((0.16, 0.18, 2.4), (x + dx, y - 0.66, F + 5.4), (0, 0, 0), g, 0.0)
    for k in range(i + 1):
        mb.ico(0.28, (x - 1.25 + k * 0.5, y - 0.7, F + 5.4), g, 1)
    col_box(A, (1.2, 1.2, 6.0), (x, y, F + 3.0))
    # caixote aberto de cristais do mundo do portal (storytelling: minerio que chega pela escada)
    cx, cy = px - 7.2, L.FLIGHT1_Y0 - 3.0
    ca = 0.25
    dx, dy = math.cos(ca), math.sin(ca)
    mb.box((2.2, 2.2, 1.9), (cx, cy, F + 0.95), (0, 0, ca), "Wood_Plank", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.3, 0.3, 2.0), (cx + dx * sx * 1.1 - dy * sy * 1.1, cy + dy * sx * 1.1 + dx * sy * 1.1, F + 1.0),
                   (0, 0, ca), "Wood_Dark", 0.0)
    mb.box((2.34, 2.34, 0.26), (cx, cy, F + 1.72), (0, 0, ca), "Wood_Dark", 0.0)
    ore_gems(mb, (cx, cy, F + 1.8), 0.85, DIFF_GEM[key], rng, 5)
    col_box(A, (2.5, 2.5, 2.6), (cx, cy, F + 1.3), (0, 0, 0.25))
    mb.finish()


def ore_gems(mb, loc, s, m, rng, n=5):
    """cacho de gemas BRUTAS (minerio, nao gelo): prismas hexagonais GROSSOS e curtos (altura ~2.5x o raio) com ponta
    piramidal rombuda, apertados e abrindo em leque a partir do centro do caixote (o crystal_cluster, fino e
    pontudo, na cor clara do brilho lia como estilhaco de gelo)"""
    x, y, z = loc
    for i in range(n):
        if i == 0:
            a, off, tilt = 0.0, 0.0, 0.0
            r, h = 0.42 * s, 1.3 * s
        else:
            a = math.tau * (i - 1) / (n - 1) + rng.uniform(-0.3, 0.3)
            off, tilt = 0.52 * s, rng.uniform(0.35, 0.6)
            r, h = rng.uniform(0.28, 0.35) * s, rng.uniform(0.7, 1.0) * s
        base = V(x + math.cos(a) * off, y + math.sin(a) * off, z - 0.15 * s)
        d = V(math.cos(a) * math.sin(tilt), math.sin(a) * math.sin(tilt), math.cos(tilt))
        top = base + d * h
        K.cone(mb, base, top, r, r * 0.9, m, 6)
        K.cone(mb, top, top + d * r * 0.9, r * 0.9, 0.0, m, 6)


# ------------------------------------------------------------------ centro do terraco: lado Shadow Garden
def _tris(mb):
    return sum(len(f.verts) - 2 for f in mb.bm.faces)


def sg_ruin_window(mb, SG, cx, cy):
    """pano de parede gotica ARRUINADO (capela em ruina, eco do Arco da Lua), de frente para a praca: plinto
    octogonal de obsidiana com filete prata; dado inteiro ate o peitoril com friso prata corrido; acima dele uma
    JANELA OGIVAL (ogiva equilatera) vazada - o pano esquerdo sobe inteiro ate perto da ponta e termina num topo
    partido em degraus, o direito quebrou baixo (so o arranque da ogiva); pingadeira prata acompanhando a ogiva na
    frente; lascas caidas no pe do lado quebrado. Silhueta cheia (le de longe) e vao recortado contra o fundo."""
    zb = T + 0.4
    poly = SG.oct_poly(cx - 3.0, cx + 3.0, cy - 1.0, cy + 1.0, 0.5)
    mb.prism(poly, T - 0.3, zb, OBS, 0.0)
    SG.loop_band(mb, poly, 0.04, 0.2, zb - 0.08, zb + 0.05, SIL)
    HW, TH = 2.5, 0.9                     # meia largura e espessura do pano
    AI_, ZSL, ZS_ = 1.0, 1.5, 3.1         # meio vao da janela, peitoril e nascenca (relativos a zb)
    RI_ = 2.0 * AI_
    n = 6
    li = SG.lancet_half(AI_, RI_, ZS_, RI_, -1, n)
    ri = SG.lancet_half(AI_, RI_, ZS_, RI_, 1, n)
    mb.box((2 * HW, TH, ZSL), (cx, cy, zb + ZSL / 2), (0, 0, 0), OBS, 0.0)                  # dado (ate o peitoril)
    # pano esquerdo (anti-horario no plano XZ): peitoril -> jamba -> ogiva ate perto da ponta -> topo partido
    lx, lz = li[5]
    left = [(-HW, ZSL), (-AI_, ZSL)] + li[:6] + [(lx - 0.3, lz + 0.85), (-0.95, 5.5), (-1.45, 6.25), (-1.95, 5.95),
                                                  (-HW, 6.6)]
    # pano direito: quebrou baixo - so o arranque da ogiva (ate o 2o passo) e um topo em degraus
    right = [(AI_, ZSL), (HW, ZSL), (HW, 4.1), (1.85, 4.55), (1.3, 4.05)] + ri[:3][::-1]
    for pts in (left, right):
        K.plate(mb, pts, V(cx, cy, zb), (1, 0, 0), (0, 0, 1), TH, OBS)
    # prata: friso corrido no peitoril (frente) e pingadeira na ogiva (frente), que para antes das quebras
    mb.box((2 * HW + 0.12, 0.2, 0.2), (cx, cy - TH / 2 - 0.06, zb + ZSL + 0.02), (0, 0, 0), SIL, 0.0)
    sq = [(-0.11, -0.11), (0.11, -0.11), (0.11, 0.11), (-0.11, 0.11)]
    for s, k in ((-1, 5), (1, 2)):
        hp = SG.lancet_half(AI_, RI_, ZS_, RI_ + 0.24, s, n)[:k]
        mb.sweep([V(cx + u, cy - TH / 2 - 0.06, zb + z) for u, z in [(s * (AI_ + 0.24), ZS_ - 0.5)] + hp], sq, SIL,
                 True, up=(0, 1, 0))
    # lascas do lado partido no chao
    mb.box((1.5, 0.9, 0.8), (cx + HW + 0.2, cy - 1.7, T + 0.34), (0.14, 0.1, 0.6), OBS, 0.0)
    mb.box((0.9, 0.7, 0.55), (cx + 1.1, cy - 1.95, T + 0.24), (0.0, 0.2, -0.5), OBS, 0.0)
    col_box(A, (2 * HW + 0.3, TH + 0.4, 6.4), (cx, cy, T + 3.2))


def sg_ruin_wall(mb, a, b):
    """mureta gotica partida (topo em degraus quebrados) de obsidiana sobre soco com filete prata"""
    d = b - a
    ang = math.atan2(d.y, d.x)
    for i, h in enumerate((2.5, 1.6, 2.0, 0.9)):
        c = a + d * ((i + 0.5) / 4)
        mb.box((d.length / 4 - 0.08, 1.1, h), (c.x, c.y, T + h / 2), (0, 0, ang), OBS, 0.0)
    m = (a + b) / 2
    mb.box((d.length + 0.4, 1.45, 0.45), m + V(0, 0, 0.2), (0, 0, ang), OBS, 0.0)
    mb.box((d.length + 0.44, 1.49, 0.08), m + V(0, 0, 0.44), (0, 0, ang), SIL, 0.0)
    col_box(A, (d.length, 1.4, 2.6), m + V(0, 0, 1.3), (0, 0, ang))


def sg_dead_tree(mb, SG, x, y, h):
    """arvore morta retorcida em P_SG_Deadwood (o mesmo tronco torcido da roseira do portal): raizes curtas,
    tronco em S, 4 galhos em garra (dois com graveto) e ponta seca"""
    import fm_veg_kit as VK
    B = V(x, y, T)
    ctrl = [(0.0, 0.0, -0.4), (0.3, 0.1, h * 0.24), (-0.35, 0.05, h * 0.48), (0.05, -0.1, h * 0.7),
            (-0.2, -0.05, h * 0.86)]
    trunk = SG._cr([B + V(*c) for c in ctrl], 2)
    nt = len(trunk)
    n0 = len(mb.bm.faces)
    SG.twisted_trunk(mb, trunk, [h * (0.07 - 0.052 * (i / (nt - 1)) ** 0.9) for i in range(nt)], DW, n=7)
    for a in (0.6, 3.4):
        ca, sa = math.cos(a), math.sin(a)
        VK.ttube(mb, [B + V(ca * 0.25, sa * 0.25, 0.8), B + V(ca * 0.9, sa * 0.9, 0.18),
                      B + V(ca * 1.35, sa * 1.35, -0.3)], [0.4, 0.24, 0.1], DW, n=5, cap0=True)
    for f, a, l, twig in ((0.45, 0.5, 0.42, True), (0.6, 2.7, 0.38, False), (0.74, 4.4, 0.32, False),
                          (0.36, 5.5, 0.3, False)):
        b = trunk[int(round(f * (nt - 1)))]
        d0 = V(math.cos(a), math.sin(a), 0)
        d1 = V(math.cos(a + 0.6), math.sin(a + 0.6), 0)
        e1 = b + d0 * h * l * 0.55 + V(0, 0, h * l * 0.35)
        e2 = e1 + d1 * h * l * 0.45 + V(0, 0, h * l * 0.5)
        pts = SG._cr([b, e1, e2], 2)
        m = len(pts) - 1
        VK.ttube(mb, pts, [h * 0.03 * (1 - 0.85 * (i / m)) for i in range(m + 1)], DW, n=4, tip=True, cap0=True,
                 rot=D(45))
        if twig:
            tp = pts[m // 2 + 1]
            d2 = V(math.cos(a - 0.9), math.sin(a - 0.9), 0)
            VK.ttube(mb, [tp, tp + d2 * h * 0.07 + V(0, 0, h * 0.06), tp + d2 * h * 0.11 + V(0, 0, h * 0.13)],
                     [h * 0.012, h * 0.007, 0.0], DW, n=4, tip=True, cap0=True)
    SG._smooth_from(mb, n0)


def sg_rose(mb, c, axis, s=1.0, twist=0.0, ns=12):
    """rosa LISA em espiral: a mesma fita de petalas do fm_pv3_shadowgarden.rose (voltas de dentro altas e fechadas,
    de fora baixas e abertas, borda ondulada), com menos passos, e um botao aceso (lavanda) no miolo"""
    import bmesh
    c = Vector(c)
    ax = Vector(axis).normalized()
    ref = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    bm = mb.bm
    turns, th = 1.75, 0.09 * s
    rows = []
    for i in range(ns + 1):
        t = i / ns
        a = twist + turns * math.tau * t
        rd = e1 * math.cos(a) + e2 * math.sin(a)
        rr = s * (0.15 + 0.6 * t)
        rb, rt = rr * 0.55, rr * (1.0 + 0.25 * t)
        hb = s * (0.1 - 0.08 * t)
        ht = s * (0.9 - 0.38 * t + 0.05 * math.cos(3.0 * (a - twist)) * t)
        ib = c + ax * hb + rd * rb
        it = c + ax * ht + rd * rt
        rows.append([bm.verts.new(ib), bm.verts.new(it), bm.verts.new(it + rd * th), bm.verts.new(ib + rd * th)])
    fs, walls = [], []
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(4):
            f = bm.faces.new((r0[j], r0[(j + 1) % 4], r1[(j + 1) % 4], r1[j]))
            fs.append(f)
            if j in (0, 2):
                walls.append(f)
    fs.append(bm.faces.new(rows[0]))
    fs.append(bm.faces.new(list(reversed(rows[-1]))))
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post([v for r in rows for v in r], ROSE, None, 0, 1)
    for f in walls:
        if f.is_valid:
            f.smooth = True
    K.octa(mb, c + ax * (0.45 * s), 0.12 * s, 0.24 * s, CORE, n=5)


def sg_rose_bush(mb, SG, x, y, stems):
    """roseira seca baixa: toco torcido e hastes de P_SG_Deadwood, uma rosa violeta na ponta de cada haste
    (olhando para a frente e para cima, como as do portal). stems = [(dx, dy, altura, escala, giro)]"""
    import fm_veg_kit as VK
    B = V(x, y, T)
    for dx, dy, hz, sz, tw in stems:
        p0, p2 = B + V(dx * 0.15, dy * 0.15, -0.3), B + V(dx, dy, hz)
        p1 = (p0 + p2) / 2 + V(-dy * 0.3, dx * 0.3, 0.1)
        VK.ttube(mb, [p0, p1, p2], [0.2, 0.13, 0.09], DW, n=4, cap0=False, rot=D(45))
        d = (p2 - p1).normalized()
        sg_rose(mb, p2 - d * 0.1, (d + Vector((0, -0.8, 0.7))).normalized(), sz, tw, ns=9)


def sg_lantern(mb, x, y, h=3.7):
    """lanterna gotica: base octogonal de obsidiana, pe prata, haste, prato prata, vidro aceso (lavanda: o mesmo
    miolo das rosas e das chamas do portal) com 3 montantes prata, aro prata e telhado agulha de obsidiana"""
    z = T
    mb.cyl(0.85, 0.35, (x, y, z + 0.175), (0, 0, D(22.5)), OBS, 8, bevel=0.0)
    mb.cyl(0.6, 0.45, (x, y, z + 0.575), (0, 0, D(22.5)), SIL, 8, r2=0.3, bevel=0.0)
    zc = z + h
    mb.box((0.36, 0.36, zc - 1.6 - z), (x, y, (z + 0.8 + zc - 0.8) / 2), (0, 0, 0), OBS, 0.0)
    mb.cyl(0.62, 0.16, (x, y, zc - 0.72), (0, 0, 0), SIL, 6, bevel=0.0)
    mb.cyl(0.4, 1.1, (x, y, zc - 0.09), (0, 0, D(30)), CORE, 6, bevel=0.0)
    for k in range(3):
        a = D(90 + 120 * k)
        mb.box((0.13, 0.13, 1.12), (x + math.cos(a) * 0.4, y + math.sin(a) * 0.4, zc - 0.09), (0, 0, a), SIL, 0.0)
    mb.cyl(0.64, 0.14, (x, y, zc + 0.53), (0, 0, 0), SIL, 6, bevel=0.0)
    K.cone(mb, (x, y, zc + 0.6), (x, y, zc + 2.0), 0.72, 0.0, OBS, 6)
    K.octa(mb, (x, y, zc + 2.14), 0.15, 0.2, SIL)
    col_box(A, (1.8, 1.8, h + 1.2), (x, y, T + (h + 1.2) / 2))


# ------------------------------------------------------------------ centro do terraco: lado Demon Slayer
# cachos (dx, dy relativos ao tronco, comprimento visivel, raio da 1a camada) - escala 1.0 = glicinia de ~12 studs
SPOTS_BIG = [(-2.6, -1.8, 2.6, 0.5), (-1.0, -2.8, 3.0, 0.52), (0.9, -2.3, 2.0, 0.48), (2.5, -1.5, 2.6, 0.5),
             (-3.4, -0.3, 1.8, 0.47), (3.3, 0.7, 2.2, 0.48), (1.8, 2.6, 1.8, 0.48)]
SPOTS_SMALL = [(-2.4, -1.6, 2.2, 0.5), (-0.4, -2.8, 2.6, 0.52), (2.2, -1.6, 1.9, 0.48)]


def ds_wisteria(mb, DSM, x, y, s, rng, spots, xmax=XMAX_C, lite=False):
    """glicinia no estilo do portal Demon Slayer (s = escala; 1.0 ~ 12 studs): tronco lider retorcido (Bark_Dark) com
    raiz alargada e um galho lateral escondido na copa; copa em GUARDA-CHUVA (3 massas lisas lilas + coroa baixa) com
    3 massas menores em lilas medio quebrando o contorno; CACHOS EM CAMADAS DE PETALAS EM SINO (DSM.cascade_plan +
    DSM.cascade: lilas forte -> medio -> claro, botao rombo na ponta) pendendo da borda e abrindo para fora. Cada
    cacho e encurtado (ou descartado) ate caber no lote (xmax), nao tocar tronco/galho nem atravessar o vizinho.
    lite=True (arvore menor): 2 massas + coroa + 2 da borda, malhas mais leves e sem galho lateral."""
    def P(dx, dy, dz):
        return Vector((x + dx * s, y + dy * s, T + dz * s))
    tr = [P(0, 0, -0.3), P(0.45, -0.1, 2.4), P(-0.2, 0.15, 4.8), P(0.35, 0.1, 7.0), P(0.3, 0.2, 9.4)]
    tr_r = [r * s for r in (0.8, 0.66, 0.56, 0.47, 0.4)]
    DSM.tube(mb, tr, tr_r, 7 if lite else 8, lambda i, j: BARK_DS, smooth=True, cap0=True)
    K.cone(mb, P(0.02, 0.0, -0.25), P(0.1, 0.02, 1.0), 0.95 * s, 0.68 * s, BARK_DS, 7 if lite else 8)  # raiz alargada
    segs = list(zip(tr, tr[1:], tr_r))
    if not lite:
        br = [tr[2].lerp(tr[3], 0.5), P(-0.9, -0.6, 7.3), P(-1.4, -1.0, 9.1)]
        br_r = [0.32 * s, 0.26 * s, 0.2 * s]
        DSM.tube(mb, br, br_r, 6, lambda i, j: BARK_DS, smooth=True, cap0=False)
        segs += list(zip(br, br[1:], br_r))
    masses = [(P(-1.3, -1.0, 9.5), 2.2 * s, 2.0 * s, 1.2 * s), (P(1.7, -0.5, 9.7), 2.0 * s, 2.1 * s, 1.15 * s),
              (P(0.3, 1.8, 9.6), 2.2 * s, 1.9 * s, 1.2 * s)]
    crown = (P(0.35, 0.2, 10.6), 1.7 * s, 1.7 * s, 0.95 * s)
    edge = [(P(-3.2, -0.6, 9.1), 1.05 * s, 1.0 * s, 0.8 * s), (P(-0.4, -2.9, 9.2), 1.0 * s, 1.05 * s, 0.8 * s),
            (P(3.3, 0.8, 9.2), 0.95 * s, 1.0 * s, 0.78 * s)]
    if lite:
        masses, edge = masses[:2], edge[:2]
    for i, (c, rx, ry, rz) in enumerate(masses):
        DSM.blob(mb, c, rx, ry, rz, WIS, nu=9 if lite else 10, nv=5 if (i < 2 and not lite) else 4,
                 rot=rng.uniform(0, 1))
    c, rx, ry, rz = crown
    DSM.blob(mb, c, rx, ry, rz, WIS, nu=8 if lite else 10, nv=4, rot=rng.uniform(0, 1))
    for c, rx, ry, rz in edge:
        DSM.blob(mb, c, rx, ry, rz, WIS_MID, nu=7 if lite else 8, nv=4, rot=rng.uniform(0, 1))
    allm = masses + [crown] + edge
    placed, vis_pts, skip = [], [], []
    for dx, dy, ln, r0 in spots:
        sx, sy = x + dx * s + rng.uniform(-0.06, 0.06), y + dy * s + rng.uniform(-0.08, 0.08)
        r0 *= math.sqrt(s) * rng.uniform(0.97, 1.03)
        zs = [z for z in (DSM.under(c, rx, ry, rz, sx, sy) for c, rx, ry, rz in allm) if z is not None]
        if not zs:
            skip.append((dx, dy, "sem copa"))
            continue
        zu = min(zs)
        ztop = zu + DSM.HIDE
        out = Vector((dx, dy, 0)).normalized()
        sway = out * rng.uniform(0.25, 0.45) * s
        a_ = rng.uniform(0, math.tau)
        lat = Vector((math.cos(a_), math.sin(a_), 0))
        ln = ln * s + rng.uniform(-0.2, 0.2)

        def fail(pts_, rad_):
            for p, r in zip(pts_[1:], rad_[1:]):
                if p.x + r > xmax:
                    return "lote"
                if p.z < zu - 0.3 and any(DSM.seg_dist(p, a, b) < r + rr + 0.08 for a, b, rr in segs):
                    return "tronco"
                if p.z > zu - 0.2:
                    continue
                if any((p - q).length < r + qr + 0.03 for q, qr in vis_pts):
                    return "cacho"
            return ""
        why, plan = "curto", None
        while ln >= 1.0:
            plan = DSM.cascade_plan(r0, ln, Vector((sx, sy, ztop)), sway, lat, ztop - zu)
            why = fail(plan[0], plan[1])
            if not why:
                break
            ln -= 0.2
        if why:
            skip.append((dx, dy, why))
            continue
        placed.append(plan)
        vis_pts += [(q, qr) for q, qr in zip(plan[0], plan[1]) if q.z < zu - 0.2]
    for pts, rad, n in placed:
        DSM.cascade(mb, pts, rad, n, rot=rng.uniform(0, math.tau))
    lo = min(p.z for pts, _r, _n in placed for p in pts) if placed else None
    print("GLICINIA terraco (%.1f, %.1f) s=%.2f: %d cachos, ponta mais baixa T%+.2f, descartados %s" % (
        x, y, s, len(placed), (lo - T) if lo is not None else 0.0, skip))


def ds_toro(mb, x, y, s=0.8, yaw=0.0):
    """toro de pedra sagrada (a pedra do portal DS) enxuto, todo em pedra: base, fuste, prato, camara recuada entre
    3 montantes, chapeu hexagonal e joia (sem brilho: um Neon de 20 tris custaria uma MeshPart so para ele)"""
    z = T
    mb.cyl(1.15 * s, 0.5 * s, (x, y, z + 0.25 * s), (0, 0, yaw), ROCK_DS, 6, bevel=0.0)
    mb.cyl(0.45 * s, 2.3 * s, (x, y, z + 1.65 * s), (0, 0, yaw), ROCK_DS, 8, r2=0.36 * s, bevel=0.0)
    mb.cyl(0.95 * s, 0.4 * s, (x, y, z + 3.0 * s), (0, 0, yaw), ROCK_DS, 6, r2=1.1 * s, bevel=0.0)
    mb.cyl(0.5 * s, 1.1 * s, (x, y, z + 3.75 * s), (0, 0, yaw + D(30)), ROCK_DS, 6, bevel=0.0)
    for k in range(3):
        a = yaw + D(120 * k + 30)
        mb.box((0.26 * s, 0.26 * s, 1.1 * s), (x + math.cos(a) * 0.72 * s, y + math.sin(a) * 0.72 * s, z + 3.75 * s),
               (0, 0, a), ROCK_DS, 0.0)
    mb.cyl(1.6 * s, 0.7 * s, (x, y, z + 4.65 * s), (0, 0, yaw), ROCK_DS, 6, r2=0.42 * s, bevel=0.0)
    K.cone(mb, (x, y, z + 5.0 * s), (x, y, z + 5.75 * s), 0.3 * s, 0.0, ROCK_DS, 6)
    return z + 5.75 * s


def ds_stone_wall(mb, a, b):
    """mureta de pedra sagrada (a pedra do portal DS): duas fiadas de pedra natural de topo plano (prismas de
    contorno irregular, como os degraus do patio do portal), a de cima recuada e girada de leve"""
    d = b - a
    u = d.normalized()
    v = V(-u.y, u.x, 0)
    m = (a + b) / 2
    shape = [(-1.0, -0.7), (-0.6, -1.0), (0.3, -0.95), (0.9, -0.85), (1.0, 0.2), (0.75, 0.95), (-0.2, 1.0),
             (-0.95, 0.6)]

    def poly(hl, hw, off, rot):
        ca, sa = math.cos(rot), math.sin(rot)
        out = []
        for p, q in shape:
            p, q = p * ca - q * sa, p * sa + q * ca
            c = m + u * (p * hl + off) + v * (q * hw)
            out.append((c.x, c.y))
        return out
    mb.prism(poly(d.length / 2 + 0.2, 0.62, 0.0, 0.0), T - 0.2, T + 0.95, ROCK_DS, 0.0)
    mb.prism(poly(d.length / 2 - 0.3, 0.52, -0.15, 0.03), T + 0.9, T + 1.55, ROCK_DS, 0.1)


def build(rng):
    """centro do terraco (entre Shadow Garden e Demon Slayer). Semente propria: o rng comum chega aqui depois do
    dressing das escadas, que muda por portal - o centro sai igual de qualquer jeito."""
    import fm_pv3_shadowgarden as SG
    import fm_pv3_demonslayer as DSM
    r = random.Random(4417)
    # ---- lado Shadow Garden (x -25.9 .. -17): ruina gotica, arvore morta, roseira, lanterna gotica
    mb = K.LeanMB("PORTAL_Terrace_Ruin", "06_PORTALS", r, vcap=1)
    parts = []
    cx, cy = -22.4, 103.6
    sg_ruin_window(mb, SG, cx, cy)
    sg_ruin_wall(mb, V(-25.0, 106.5, T), V(-22.2, 109.5, T))
    parts.append(("ruina", _tris(mb)))
    sg_dead_tree(mb, SG, -20.2, 112.0, 10.5)
    col_box(A, (1.8, 1.8, 5.0), (-20.2, 112.0, T + 2.5))
    parts.append(("arvore", _tris(mb)))
    sg_rose_bush(mb, SG, cx - 1.85, cy - 2.2, [(-0.55, -0.3, 1.9, 0.95, 0.3), (0.6, -0.25, 1.45, 0.85, 1.4),
                                               (0.1, 0.35, 2.35, 0.9, 2.3)])
    parts.append(("roseira", _tris(mb)))
    sg_lantern(mb, -20.2, 95.2)
    parts.append(("lanterna", _tris(mb)))
    tw = parts[-1][1]
    obw = mb.finish()
    # ---- lado Demon Slayer (x 16 .. 25.9): glicinias em camadas de petalas, toro de pedra sagrada, mureta
    mbe = K.LeanMB("PORTAL_Terrace_Wisteria", "06_PORTALS", r, vcap=1)
    ds_wisteria(mbe, DSM, 19.8, 111.6, 1.0, r, SPOTS_BIG)
    col_box(A, (1.8, 1.8, 7.0), (19.8, 111.6, T + 3.5))
    parts.append(("glicinia", tw + _tris(mbe)))
    ds_wisteria(mbe, DSM, 20.8, 94.2, 0.7, r, SPOTS_SMALL, lite=True)
    col_box(A, (1.6, 1.6, 5.0), (20.8, 94.2, T + 2.5))
    parts.append(("glicinia2", tw + _tris(mbe)))
    a, b = V(16.4, 101.6, T), V(20.4, 104.4, T)
    u = (b - a).normalized()
    ang = math.atan2(u.y, u.x)
    ds_stone_wall(mbe, a, b)
    tp = b + u * 1.75
    ds_toro(mbe, tp.x, tp.y, 0.85, ang)
    ln = (b - a).length + 1.75 + 1.05
    col_box(A, (ln, 2.0, 4.9), a + u * (ln / 2) + V(0, 0, 2.45), (0, 0, ang))     # mureta + toro numa caixa
    parts.append(("toro+mureta", tw + _tris(mbe)))
    obe = mbe.finish()
    prev = 0
    txt = []
    for lab, t in parts:
        txt.append("%s=%d" % (lab, t - prev))
        prev = t
    print("TRIS terraco centro: " + " ".join(txt) + " total=%d" % prev)
    # os vaos de 4 studs ate os lotes do Shadow Garden e do Demon Slayer ficam limpos
    xw = min(v.co.x for v in obw.data.vertices)
    xe = max(v.co.x for v in obe.data.vertices)
    print("LOTE terraco centro: Ruin x >= %.2f (limite %.1f) %s | Wisteria x <= %.2f (limite %.1f) %s" % (
        xw, XMIN_C, "OK" if xw >= XMIN_C else "INVADE O VAO", xe, XMAX_C, "OK" if xe <= XMAX_C else "INVADE O VAO"))

