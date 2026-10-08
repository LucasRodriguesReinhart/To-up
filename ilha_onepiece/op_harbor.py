# op_harbor - ZONA HARBOR da Ilha 5 (ONE PIECE / WANO), M3 (PLANO_OP secoes 0.8, 4.2, 4.3 e 9; PROMPT_USUARIO 11, 15-17).
# Substitui op_blockout.harbor. Prefixo OP_Port_ (dono "harbor" no export_op/studio_op/op_lib), colecao 16_HARBOR.
# Luzes so NightOnly (L_OPProp_Lamp_Porto_*). Colisoes simples com prefixo de area OP_Port* (COL_OP_Port...).
#
# O QUE E DESTE MODULO (o cais de PEDRA, as muralhas e a face oeste do porto sao do op_terrain; o terraco do summon e o
# lajeado dele, x 116..206 / y 150..264, sao do op_summon; o navio e a prancha sao do op_ship):
#   PIER do navio (x 222..234, y 110..200) e PALAFITA (x 222..246, y 40..76) a 42,2 = topo da colisao do op_col:
#     tabuas soltas com fresta (as frestas mostram as longarinas 0,3 abaixo), longarinas, travessas (cabecotes) sobre
#     ESTACAS de madeira com mancha d'agua (musgo) na linha do mar, contraventamento em X na face externa, testeira,
#     meio-fio de madeira na borda de atracacao, CABECOS de ferro, DEFENSAS (estacas de defensa + defensas de cabo
#     penduradas), guarda-corpo vermelho nas pontas do pier e em toda a borda d'agua da palafita (concept), estacas da
#     palafita em laca vermelha no perimetro (concept), PAVILHAO VERMELHO (H4, kit pavilion) com estrado e 2 bancos.
#     O op_terrain ainda cria OP_Ter_Piers (tampo liso do pier/palafita): este modulo REMOVE esse objeto (mesmo
#     procedimento do op_terrain com o OP_Cas_Cliff do blockout) - pedido registrado ao dono do terreno para tirar o
#     build_piers().
#   ESCADAS PortoA (rua alta 65,2 -> T1) e PortoB (cais -> rua alta): os 2 lances de 30 da planta em pedra do kit
#     (stair_stone: pedras desencontradas, espelho escuro, banzos inclinados, pilaretes com ANDON no arranque) + corrimao
#     inclinado de laca vermelha sobre os banzos (a guarda invisivel do op_col tem 4 de altura: o corrimao da a leitura).
#   4 ARMAZENS do kit (house, sem textura): H1 (kura de 2 pisos, kirizuma), H2 (galpao de 1 piso com alpendre de carga
#     e 2 portas), H3 (rua alta, 2 pisos, irimoya), H5 (ACRESCIMO deste modulo, documentado: kura de empena para o patio
#     de carga, no bolso livre do cais entre o arrimo da rua alta e o H1; nao toca rota, escada, SAFE_Cais nem pisos).
#     Portas FECHADAS (fachadas cenograficas: sem interior falso). Carga apoiada no chao junto as portas: barris,
#     caixas, fardos de arroz (tawara: palha + 3 cintas de cabo), jarros e um carrinho de mao (daihachi).
#   BARCOS pequenos (silhueta + acabamento simples, sem sistema): bote a remo na palafita, barco coberto (yakatabune)
#     no cais norte e bote fundeado na enseada; amarras com catenaria ate os cabecos. Amarras do NAVIO (proa, popa,
#     2 espringues) do costado ate os cabecos do pier.
#   POSTES de rua de Wano (kit) no pier e na palafita.
# AGUA: o mar local (36) e do Roblox (WATER_Sea do op_core). Nenhum marcador novo.
import math, random
import bpy, bmesh
from mathutils import Vector, geometry
import op_lib as DL
from op_lib import MB, Frame, col_box, camera
import op_layout as L
import op_kit as K
import op_ship as SH

COLL = "16_HARBOR"
H = L.HARBOR                    # 42,2
HM = L.HMID                     # 65,2
SEA = L.SEA                     # 36
WD, WM, LAC, GOLD, IRON = "Wood_OP_Dark", "Wood_OP_Mid", "Wood_OP_Lacquer", "Metal_OP_Gold", "Metal_OP_Iron"
HULL, ROPE, MOSS, STRAW = "Wood_OP_Hull", "Rope", "Cliff_OP_Moss", "Cloth_OP_Straw"
F0 = Frame(0.0, 0.0, 0.0, 0.0)
PIER_A = (222.0, 110.0, 234.0, 200.0)          # pier do navio (HARBOR_POLY)
PIER_B = (222.0, 40.0, 246.0, 76.0)            # palafita
X_ROOT = 223.0                                  # as tabuas comecam depois da capa de pedra do cais (op_terrain)
BOLLARDS_A = [116.0, 130.0, 145.0, 160.0, 178.0, 194.0]
WAREHOUSES = ("H1", "H2", "H3")                 # + H5 (telheiro aberto, shed())
H5 = ("H5", "armazem", 138.0, 90.0, 20.0, 14.0, -90.0, H, 2, "kirizuma", "Roof_OP_Blue")   # acrescimo (ver cabecalho)


def _spec(nm):
    if nm == "H5":
        return H5
    for b in L.BUILDINGS:
        if b[0] == nm:
            return b
    raise KeyError(nm)


def bframe(nm):
    s = _spec(nm)
    return Frame(s[2], s[3], s[7], math.radians(s[6]) - math.pi / 2)


# ================================================================== PIERS (pier do navio + palafita)
def pile(mb, x, y, z_top, r=0.5, m=WD, moss=False):
    mb.cyl(r, z_top - 29.0, (x, y, (z_top + 29.0) / 2.0), m=m, n=6, bevel=0.0)
    if moss:
        mb.cyl(r + 0.15, 1.5, (x, y, SEA + 0.35), m=MOSS, n=6, bevel=0.0, caps=False)


def deck_boards(mb, x0, x1, y0, y1, along_x=True, split=None):
    """tabuas soltas (fresta 0,1) com topo = colisao; along_x: tabuas atravessadas no eixo x"""
    if along_x:
        y = y0
        while y < y1 - 0.3:
            yb = min(y + 1.15, y1)
            mb.box((x1 - x0, yb - y - 0.1, 0.3), ((x0 + x1) / 2, (y + yb) / 2, H - 0.15), (0, 0, 0), WM, 0.0)
            y = yb
    else:
        x = x0
        while x < x1 - 0.3:
            xb = min(x + 1.15, x1)
            for ya, yb in (split or [(y0, y1)]):
                mb.box((xb - x - 0.1, yb - ya - 0.06, 0.3), ((x + xb) / 2, (ya + yb) / 2, H - 0.15), (0, 0, 0), WM, 0.0)
            x = xb


def pier_a(mb):
    x0, y0, x1, y1 = PIER_A
    deck_boards(mb, X_ROOT, x1, y0, y1, along_x=True)
    for x in (223.8, 227.0, 230.2, 233.4):                                         # longarinas
        mb.box((0.55, y1 - y0 - 0.4, 0.7), (x, (y0 + y1) / 2, H - 0.65), (0, 0, 0), WD, 0.0)
    rows = [y0 + 2.0 + i * (y1 - y0 - 4.0) / 14 for i in range(15)]
    for i, y in enumerate(rows):
        mb.box((x1 - x0 + 0.3, 0.9, 0.8), ((x0 + x1) / 2 + 0.6, y, H - 1.4), (0, 0, 0), WD, 0.0)   # cabecote
        for x in (223.6, 228.6, 233.6):
            pile(mb, x, y, H - 1.8, 0.5, WD, moss=(x > 233))
        # estaca de defensa na face de atracacao
        mb.box((0.5, 0.55, 7.6), (x1 + 0.45, y, H - 3.5), (0, 0, 0), WD, 0.0)
    # contraventamento em X na face externa e nas pontas
    for ya, yb in zip(rows, rows[1:]):
        mb.beam(Vector((233.9, ya, SEA + 1.4)), Vector((233.9, yb, H - 2.0)), 0.3, 0.35, WD, 0.0)
    for y in (rows[0], rows[-1]):
        mb.beam(Vector((223.6, y + (0.5 if y < 150 else -0.5), SEA + 1.4)), Vector((233.6, y + (0.5 if y < 150 else -0.5),
                                                                                    H - 2.0)), 0.3, 0.35, WD, 0.0)
    # testeira (face externa) e meio-fio de madeira na borda de atracacao (aberto na prancha)
    mb.box((0.35, y1 - y0 + 0.35, 1.0), (x1 + 0.18, (y0 + y1) / 2, H - 0.62), (0, 0, 0), WD, 0.0)
    for yy in (y0, y1):
        mb.box((x1 - X_ROOT + 0.35, 0.35, 1.0), ((X_ROOT + x1) / 2 + 0.17, yy + (-0.18 if yy == y0 else 0.18), H - 0.62),
               (0, 0, 0), WD, 0.0)
    gw0, gw1 = SH.GAP[0] - 1.0, SH.GAP[1] + 1.0
    cuts = sorted([y for y in BOLLARDS_A] + [gw0, gw1])
    runs, a = [], y0 + 0.4
    for y in BOLLARDS_A:
        runs.append((a, y - 1.0))
        a = y + 1.0
    runs.append((a, y1 - 0.4))
    final = []
    for ra, rb in runs:
        if rb <= gw0 or ra >= gw1:
            final.append((ra, rb))
        else:
            if ra < gw0:
                final.append((ra, gw0))
            if rb > gw1:
                final.append((gw1, rb))
    for ra, rb in final:
        if rb - ra > 0.5:
            mb.box((0.6, rb - ra, 0.45), (x1 - 0.32, (ra + rb) / 2, H + 0.225), (0, 0, 0), WD, 0.0)
    # cabecos de ferro sobre chapa de madeira
    for y in BOLLARDS_A:
        bollard(mb, x1 - 1.4, y)
    # guarda-corpo vermelho nas pontas do pier (a borda de atracacao fica aberta: meio-fio + cabecos)
    rail(mb, [(X_ROOT + 0.4, y0 + 0.3), (x1 - 0.3, y0 + 0.3)])
    rail(mb, [(X_ROOT + 0.4, y1 - 0.3), (x1 - 0.3, y1 - 0.3)])
    # defensas de cabo penduradas da borda
    for y in (124.0, 138.0, 168.0, 186.0):
        K.lathe(mb, F0, (x1 + 0.95, y, SEA + 2.2), [(0.3, 0.0), (0.48, 0.25), (0.48, 1.6), (0.3, 1.85)], 8, ROPE)
        SH.rope(mb, (x1 + 0.95, y, SEA + 4.05), (x1 - 0.3, y, H + 0.45), 0.06)


def rail(mb, pts, base=H, h=3.4, step=3.4, gold_at=()):
    """guarda-corpo vermelho do porto (mesma linguagem do kit, versao leve: pilaretes, corrimao que passa das pontas,
    travessa media; giboshi dourado so nos cantos pedidos)"""
    SH.lite_rail(mb, pts, base, h, step, gold=False)
    for i in gold_at:
        K.giboshi(mb, F0, pts[i][0], pts[i][1], base + h, 0.9)


def bollard(mb, x, y, z=H, col=True):
    mb.box((1.6, 1.6, 0.2), (x, y, z + 0.1), (0, 0, 0), WD, 0.0)
    K.lathe(mb, F0, (x, y, z + 0.2), [(0.62, 0.0), (0.62, 0.2), (0.44, 0.3), (0.4, 0.95), (0.58, 1.08), (0.58, 1.32),
                                     (0.36, 1.42)], 8, IRON)
    if col:
        col_box("OP_PortBollard", (1.4, 1.4, 1.5), (x, y, z + 0.75))
    return Vector((x, y, z + 1.1))


def palafita(mb):
    x0, y0, x1, y1 = PIER_B
    xs = [223.6, 229.2, 234.8, 240.4, 245.4]
    ys = [40.6, 46.4, 52.2, 58.0, 63.8, 69.6, 75.4]
    deck_boards(mb, X_ROOT, x1, y0, y1, along_x=False, split=[(y0, 58.0), (58.0, y1)])
    for y in ys:                                                                    # longarinas (ao longo de x)
        mb.box((x1 - x0 - 0.4, 0.55, 0.7), ((x0 + x1) / 2 + 0.2, y, H - 0.65), (0, 0, 0), WD, 0.0)
    for x in xs:                                                                    # cabecotes
        mb.box((0.9, y1 - y0 + 0.3, 0.8), (x, (y0 + y1) / 2, H - 1.4), (0, 0, 0), WD, 0.0)
        for y in ys:
            per = x > 245 or y < 41 or y > 75
            pile(mb, x, y, H - 1.8, 0.55 if per else 0.5, LAC if per else WD, moss=x > 245)
    # contraventamento vermelho nas faces d'agua
    for xa, xb in zip(xs, xs[1:]):
        for y in (ys[0], ys[-1]):
            mb.beam(Vector((xa, y, SEA + 1.4)), Vector((xb, y, H - 2.0)), 0.3, 0.35, LAC, 0.0)
    for ya, yb in zip(ys, ys[1:]):
        mb.beam(Vector((xs[-1], ya, SEA + 1.4)), Vector((xs[-1], yb, H - 2.0)), 0.3, 0.35, LAC, 0.0)
    # testeira
    mb.box((0.35, y1 - y0 + 0.7, 1.0), (x1 + 0.18, (y0 + y1) / 2, H - 0.62), (0, 0, 0), WD, 0.0)
    for yy, s in ((y0, -1), (y1, 1)):
        mb.box((x1 - X_ROOT + 0.35, 0.35, 1.0), ((X_ROOT + x1) / 2 + 0.17, yy + s * 0.18, H - 0.62), (0, 0, 0), WD, 0.0)
    # guarda-corpo vermelho em toda a borda d'agua (concept)
    rail(mb, [(X_ROOT + 0.4, y0 + 0.3), (x1 - 0.3, y0 + 0.3), (x1 - 0.3, y1 - 0.3), (X_ROOT + 0.4, y1 - 0.3)],
         gold_at=(1, 2))
    # PAVILHAO VERMELHO (H4, kit) virado para o cais
    s = _spec("H4")
    Fp = Frame(s[2], s[3], H, math.radians(s[6]) - math.pi / 2)
    W, D = s[4], s[5]
    K.pavilion(mb, Fp, W, D, 8.0, "yosemune", True, s[10], "F", 1.2, 1)
    for xx in (-4.6, 4.6):                                                          # bancos junto ao fundo
        K.bench(mb, Fp, xx, -D / 2 + 2.2, 5.0, 1.6, 1.7, 0.0, 1.2)
    for xx in (-W / 2 + 1.2, W / 2 - 1.2):                                          # chochin no beiral da frente
        c = Fp.p(xx, D / 2 - 0.5, 1.2 + 8.0 - 1.0)
        mb.rod(c, c - Vector((0, 0, 0.5)), 0.05, IRON, 4)
        K.chochin(mb, F0, (c.x, c.y, c.z - 0.5 - 1.5), 0.48, 1.5)
    # colisao: estrado (degrau de 1,2) + guarda-corpos do pavilhao (aberto no meio da frente)
    area = "OP_PortHouseH4"
    col_box(area, (D, W, 1.2), (s[2], s[3], H + 0.6))
    rz = H + 1.2 + 1.6
    for sy in (-1, 1):
        col_box(area, (D, 0.5, 3.2), Fp.p(sy * (W / 2 - 0.5), 0.0, 1.2 + 1.6), Fp.r(0, 0, math.pi / 2))
    col_box(area, (W, 0.5, 3.2), Fp.p(0.0, -D / 2 + 0.5, 1.2 + 1.6), Fp.r())
    for sx in (-1, 1):
        c = Fp.p(sx * (W / 4 + 1.3), D / 2 - 0.5, 1.2 + 1.6)
        col_box(area, (W / 2 - 2.6, 0.5, 3.2), c, Fp.r())
    return Fp


# ================================================================== ESCADAS PortoA / PortoB (pedra do kit)
def stair_rail(mb, F, x, n, rise, tread, cheek_h, h=2.3, step=4.6):
    """corrimao INCLINADO de laca sobre o banzo (pilaretes verticais + corrimao + travessa), F da escada"""
    ztl = lambda y: rise * (y / tread + 1.0) + cheek_h + 0.26
    y0, y1 = 1.0, tread * (n - 1) - 0.4
    k = max(1, int(math.ceil((y1 - y0) / step)))
    ys = [y0 + (y1 - y0) * i / k for i in range(k + 1)]
    for y in ys:
        mb.box((0.38, 0.38, h), F.p(x, y, ztl(y) + h / 2), F.r(), LAC, 0.0)
    a, b = F.p(x, y0 - 0.2, ztl(y0 - 0.2) + h - 0.12), F.p(x, y1 + 0.2, ztl(y1 + 0.2) + h - 0.12)
    mb.beam(a, b, 0.36, 0.26, LAC, 0.0)
    a, b = F.p(x, y0, ztl(y0) + h * 0.5), F.p(x, y1, ztl(y1) + h * 0.5)
    mb.beam(a, b, 0.16, 0.2, LAC, 0.0)
    K.giboshi(mb, F, x, ys[-1], ztl(ys[-1]) + h, 0.85)
    mb.box((0.5, 0.5, 0.16), F.p(x, ys[0], ztl(ys[0]) + h + 0.08), F.r(), LAC, 0.0)


def stairs(mb):
    for nm, lamp in (("PortoA", None), ("PortoB", "L_OPProp_Lamp_PortoEscB")):     # andon so no pe do cais
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        rise = L.stair_rise(nm)
        Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
        K.stair_stone(mb, Fs, w, n, rise=rise, tread=tread, z_floor=-0.3, cheek_h=1.0, newels=True, newel_lamp=lamp)
        for s in (-1, 1):
            stair_rail(mb, Fs, s * (w / 2 + 0.6), n, rise, tread, 1.0)
            # soco escuro corrido no pe do banzo (le como base de cantaria; o banzo alto nao fica um plano unico)
            c = Fs.p(s * (w / 2 + 1.25), tread * n / 2, 0.45)
            mb.box((0.4, tread * n + 0.6, 1.2), c, Fs.r(), "Stone_OP_Dark", 0.0)
            c = Fs.p(s * (w / 2 + 1.22), tread * n / 2 + 0.3, 1.25)
            mb.box((0.3, tread * n - 0.6, 0.3), c, Fs.r(), "Stone_OP_Dark", 0.0)
            c = Fs.p(s * (w / 2 + 0.6), -0.55, 0.0)
            col_box("OP_PortProp", (2.0, 1.7, 4.4), (c.x, c.y, foot[2] + 2.2), Fs.r())


# ================================================================== ARMAZENS (kit)
def wh_spec(nm):
    s = _spec(nm)
    base = dict(W=s[4], D=s[5], plinth=("ishigaki", 1.3), plaster="Plaster_OP", plaster_up="Plaster_OP", roof_m=s[10],
                lit=False, noren=None, lod=1, back_lod=1, side_lod=1, seed=4100 + WAREHOUSES.index(nm) * 53)
    if nm == "H1":        # kura de 2 pisos: saia de tabuas + reboco, porta de correr pesada, janela de barras no 2o piso
        base.update(floors=[dict(h=9.5, front=["plain", {"t": "door", "w": 5.8}, "plain"], left=["plaster"],
                                 right=["plaster"]),
                            dict(h=7.0, front=["plaster", "mushiko", "plaster"], pent=False, left=["plaster"],
                                 right=["plaster"])],
                    roof=dict(kind="kirizuma", ridge="x", pitch=0.6, over=2.6, g_over=1.8))
    elif nm == "H2":      # galpao de carga: 1 piso alto, 2 portas, alpendre corrido (hisashi) na frente
        base.update(plinth=("soco", 0.9), plaster="Plaster_OP_Warm",
                    floors=[dict(h=10.5, front=["plain", {"t": "door", "w": 5.6}, {"t": "door", "w": 5.6}, "plain"],
                                 left=["plaster"], right=["plaster"], front_pent=dict(z=8.8, depth=3.4))],
                    roof=dict(kind="kirizuma", ridge="x", pitch=0.55, over=2.8, g_over=1.6))
    else:                 # H3: armazem da rua alta, 2 pisos, irimoya (o unico de 4 aguas: marca a rua alta)
        base.update(floors=[dict(h=9.5, front=["plain", {"t": "door", "w": 5.8}, "plain"], left=["plaster"],
                                 right=["plaster"]),
                            dict(h=7.2, front=["plaster", "mushiko", "plaster"], pent=False, left=["plaster"],
                                 right=["plaster"])],
                    roof=dict(kind="irimoya", ridge="x", pitch=0.55, over=3.0, courses=2))
    return base


def shed(mb, nm="H5"):
    """H5: TELHEIRO DE CARGA aberto (4o armazem do porto): pilares sobre pedras, frechais, kirizuma do kit, fardos e
    caixas empilhados por dentro (sem paredes: nada de interior falso)"""
    F = bframe(nm)
    s = _spec(nm)
    W, D = s[4], s[5]
    xs = [-W / 2 + 0.5, -W / 6, W / 6, W / 2 - 0.5]
    for x in xs:
        for y in (-D / 2 + 0.5, D / 2 - 0.5):
            K.rock_base(mb, F, x, y, 0.0, 0.8, 0.4)
            K.bb(mb, F, x - 0.42, x + 0.42, y - 0.42, y + 0.42, 0.3, 8.0, WD)
    for y in (-D / 2 + 0.5, D / 2 - 0.5):
        K.bb(mb, F, -W / 2 - 0.4, W / 2 + 0.4, y - 0.45, y + 0.45, 7.2, 8.0, WD)
    for x in xs:
        K.bb(mb, F, x - 0.4, x + 0.4, -D / 2 - 0.3, D / 2 + 0.3, 8.0, 8.6, WD)
    # cobertura de tabuas (telhado de madeira do porto): 2 aguas em fiadas sobrepostas, cumeeira e tabeiras
    Dh, rise = D / 2 + 1.6, 3.4
    ang = math.atan2(rise, Dh)
    ln = math.hypot(Dh, rise)
    nb = 6
    for sy in (-1, 1):
        for k in range(nb):
            t0 = k / nb
            yy = sy * Dh * (1 - t0 - 0.5 / nb)
            zz = 8.6 + rise * (t0 + 0.5 / nb) + 0.12 * (k % 2)
            c = F.p(0.0, yy, zz)
            mb.box((W + 3.0, ln / nb + 0.35, 0.22), c, F.r(-sy * ang, 0, 0), "Roof_OP_Shingle", 0.0)
        for sx in (-1, 1):                                    # tabeira (barge board)
            c = F.p(sx * (W / 2 + 1.55), sy * Dh / 2, 8.6 + rise / 2 + 0.05)
            mb.box((0.25, ln + 0.3, 0.6), c, F.r(-sy * ang, 0, 0), WD, 0.0)
    K.bb(mb, F, -W / 2 - 1.7, W / 2 + 1.7, -0.45, 0.45, 8.6 + rise, 8.6 + rise + 0.55, "Roof_OP_Ridge")
    for x in xs:                                             # pendurais da tesoura
        K.bb(mb, F, x - 0.25, x + 0.25, -0.25, 0.25, 8.6, 8.6 + rise, WD)
    for i, (x, y) in enumerate(((-5.4, -2.4), (-5.4, 1.6))):
        for k in range(2):
            tawara(mb, F, x - 0.65 + 1.3 * k, y, 0.0, 0.0)
        tawara(mb, F, x, y, 1.15, 0.0)
    for (x, y, z, a) in ((4.0, -2.0, 0.0, 0.0), (5.8, -2.2, 0.0, 0.2), (4.8, -2.0, 0.9, -0.1)):
        K.crate(mb, F, x, y, z, 1.6, 1.3, 0.9, a)
    for x in xs:                                         # pilares da frente (o fundo, junto ao arrimo, e 1 caixa)
        col_box("OP_PortHouse" + nm, (1.0, 1.0, 8.0), F.p(x, D / 2 - 0.5, 4.0), F.r())
    col_box("OP_PortHouse" + nm, (W, 1.0, 8.0), F.p(0.0, -D / 2 + 0.5, 4.0), F.r())
    col_box("OP_PortHouse" + nm, (3.8, 6.6, 2.4), F.p(-5.4, -0.4, 1.2), F.r())
    col_box("OP_PortHouse" + nm, (3.4, 6.4, 1.9), F.p(4.9, 0.0, 0.95), F.r())


def warehouses(mb):
    out = {}
    for nm in WAREHOUSES:
        F = bframe(nm)
        sp = wh_spec(nm)
        out[nm] = K.house(mb, F, sp)
        K.house_cols("OP_PortHouse" + nm, F, sp)
    shed(mb, "H5")
    return out


# ------------------------------------------------------------------ carga do cais
def tawara(mb, F, x, y, z, ang=0.0):
    """fardo de arroz deitado: palha abaulada, 3 cintas de cabo, tampos recuados"""
    Fb = K.sub(F, x, y, z + 0.62, ang)
    K.lathe_y(mb, Fb, (0.0, 0.0, 0.0), [(0.42, -0.85), (0.58, -0.72), (0.64, -0.3), (0.64, 0.3), (0.58, 0.72),
                                        (0.42, 0.85)], 6, STRAW)
    for yy in (-0.5, 0.0, 0.5):
        K.lathe_y(mb, Fb, (0.0, 0.0, 0.0), [(0.67, yy - 0.06), (0.67, yy + 0.06)], 6, ROPE, caps=(False, False))


def cart(mb, F, x, y, ang=0.0):
    """carrinho de mao (daihachi): estrado de tabuas, 2 rodas de raios, varais"""
    Fc = K.sub(F, x, y, 0.0, ang)
    K.bb(mb, Fc, -1.4, 1.4, -2.2, 2.2, 1.55, 1.8, WM)
    for sx in (-1, 1):
        K.bb(mb, Fc, sx * 1.3 - 0.12, sx * 1.3 + 0.12, -2.4, 4.6, 1.35, 1.6, WD)
        rim = [Fc.p(sx * 1.7, 1.2 * math.cos(2 * math.pi * k / 12), 1.25 + 1.2 * math.sin(2 * math.pi * k / 12))
               for k in range(13)]
        mb.tube(rim, 0.11, WD, n=4)
        for k in range(4):
            a = k * math.pi / 4
            mb.rod(Fc.p(sx * 1.7, -1.15 * math.cos(a), 1.25 - 1.15 * math.sin(a)),
                   Fc.p(sx * 1.7, 1.15 * math.cos(a), 1.25 + 1.15 * math.sin(a)), 0.07, WD, 4)
    mb.rod(Fc.p(-1.9, 0.0, 1.25), Fc.p(1.9, 0.0, 1.25), 0.12, IRON, 6)
    K.bb(mb, Fc, -1.4, 1.4, 4.4, 4.6, 1.35, 1.6, WD)
    tawara(mb, Fc, -0.65, -0.9, 1.8, math.pi / 2)
    tawara(mb, Fc, 0.65, -0.9, 1.8, math.pi / 2)
    K.crate(mb, Fc, 0.0, 1.2, 1.8, 1.6, 1.2, 1.0, 0.1)


def cargo(mb):
    """carga encostada nas fachadas (fora das portas e das rotas)"""
    # H1 (frente para o norte, y 52): fardos empilhados e barris ao lado da porta
    F = F0
    for i, (x, y, z) in enumerate(((128.6, 54.0, H), (128.6, 55.9, H), (128.6, 54.95, H + 1.15))):
        tawara(mb, F, x, y, z, 0.0)
    K.barrel(mb, F, 131.2, 54.2, H, 0.75, 1.6)
    K.barrel(mb, F, 132.9, 54.5, H, 0.75, 1.6)
    col_box("OP_PortProp", (6.4, 3.4, 2.4), (130.6, 55.0, H + 1.2))
    # H2 (frente para o norte, y 49): carrinho e jarros sob o alpendre
    cart(mb, F, 185.5, 54.6, math.radians(80))
    col_box("OP_PortProp", (7.2, 3.0, 2.6), (184.6, 54.8, H + 1.3))
    for (x, y) in ((198.6, 51.8), (199.9, 52.9)):
        K.jar(mb, F, x, y, H, 0.6, 1.5, "Stone_OP_Dark", True)
    col_box("OP_PortProp", (2.8, 2.8, 1.6), (199.3, 52.4, H + 0.8))
    # H3 (rua alta, frente para o sul, y 113): barris e fardos ao lado da porta
    for (x, y) in ((168.2, 110.6), (169.9, 110.4)):
        K.barrel(mb, F, x, y, HM, 0.75, 1.6)
    for (x, y, z, a) in ((184.0, 110.8, HM, 0.1), (184.0, 110.8, HM + 0.9, 0.5)):
        K.crate(mb, F, x, y, z, 1.6, 1.3, 0.9, a)
    col_box("OP_PortProp", (3.6, 2.0, 1.7), (169.0, 110.5, HM + 0.85))
    col_box("OP_PortProp", (2.2, 2.0, 1.9), (184.0, 110.8, HM + 0.95))


# ================================================================== BARCOS
def boat(mb, cx, cy, ang, Lb=11.0, Bb=3.4, roof=False, z_g=None):
    """barco de madeira (bote/sampan): casco de estacoes com casca interna, banco(s), tabuado do fundo; roof=True -> barco
    coberto (yakatabune) com 4 esteios e telhado de 2 aguas. +y local = proa"""
    F = Frame(cx, cy, 0.0, ang)
    zg0 = SEA + 1.5 if z_g is None else z_g
    keel = SEA - 0.7
    n = 12
    bm = mb.bm
    rings = []
    meta = []
    for i in range(n + 1):
        t = i / n                                        # 0 = popa (espelho), 1 = proa
        yl = -Lb / 2 + Lb * t
        e = abs(2 * t - 1)
        hb = Bb / 2 * max(0.04, (1 - e ** 3.2) ** 0.5) if t > 0.5 else Bb / 2 * max(0.62, (1 - e ** 3.2) ** 0.5)
        zg = zg0 + 0.9 * max(0.0, 2 * t - 1) ** 2 + 0.35 * max(0.0, 1 - 2 * t) ** 2
        kz_ = keel + (zg - 0.4 - keel) * max(0.0, (t - 0.8) / 0.2) ** 1.6
        hi = max(0.03, hb - 0.16)
        zf = SEA + 0.3
        prof = [(hi, min(zf, zg - 0.3)), (hi, zg), (hb, zg), (hb * 0.97, zg - 0.55), (hb * 0.78, SEA - 0.1)]
        R = [(-u, yl, z) for u, z in prof] + [(0.0, yl, kz_)] + [(u, yl, z) for u, z in reversed(prof)]
        rings.append([bm.verts.new(F.p(*p)) for p in R])
        meta.append((yl, hb, hi, zg))
    fs = []
    for A, Bv in zip(rings, rings[1:]):
        for j in range(len(A) - 1):
            fs.append(bm.faces.new((A[j], Bv[j], Bv[j + 1], A[j + 1])))
    last = rings[0]                                      # espelho de popa: normal para -y local
    co2 = [Vector((v.co.x * math.cos(-ang) - v.co.y * math.sin(-ang), v.co.z, 0.0)) for v in last]
    for a, b, c in geometry.tessellate_polygon([co2]):
        f = bm.faces.new((last[a], last[b], last[c]))
        f.normal_update()
        d = F.p(0, -1, 0) - F.p(0, 0, 0)
        if f.normal.dot(d) < 0:
            f.normal_flip()
        fs.append(f)
    mb._post([v for r in rings for v in r], HULL, None, 0, 1)
    for f in fs:
        f.normal_update()
        if f.calc_center_median().z < SEA + 0.2:
            f.material_index = mb._mi_for(WD)
    # fundo (tabuado), bancos, borda (alcatrate) e remos
    pts = [(meta[i][2] - 0.05, meta[i][0]) for i in range(1, n)] + [(-(meta[i][2] - 0.05), meta[i][0]) for i in range(n - 1, 0, -1)]
    poly = [tuple(F.p(x, y, 0))[:2] for x, y in pts]
    mb.prism(DL.ccw(poly), SEA + 0.05, SEA + 0.32, WM)
    for t in ((0.3, 0.55, 0.8) if not roof else (0.18, 0.86)):
        yl = -Lb / 2 + Lb * t
        i = min(n, max(0, int(round(t * n))))
        hb, zg = meta[i][1], meta[i][3]
        K.bb(mb, F, -hb + 0.1, hb - 0.1, yl - 0.45, yl + 0.45, zg - 0.55, zg - 0.3, WM)
    for s in (-1, 1):
        cap = [F.p(s * (meta[i][1] - 0.05), meta[i][0], meta[i][3] + 0.08) for i in range(0, n + 1)]
        mb.tube(cap, 0.12, WD, n=4)
    if roof:                                             # yakata: esteios, cobertura de 2 aguas, cumeeira
        y0, y1 = -Lb * 0.22, Lb * 0.24
        hb = Bb / 2 - 0.35
        zt = zg0 + 3.6
        for sx in (-1, 1):
            for yy in (y0, y1):
                K.bb(mb, F, sx * hb - 0.15, sx * hb + 0.15, yy - 0.15, yy + 0.15, zg0 - 0.3, zt, WD)
            K.bb(mb, F, sx * hb - 0.12, sx * hb + 0.12, y0, y1, zt - 0.3, zt, WD)
        for sx in (-1, 1):
            a = math.atan2(1.0, hb + 0.6)
            c = F.p(sx * (hb + 0.6) / 2, (y0 + y1) / 2, zt + 0.55)
            mb.box((math.hypot(hb + 0.6, 1.0) + 0.2, y1 - y0 + 1.6, 0.22), c, (0, sx * a, ang), "Roof_OP_Blue", 0.0)
        K.bb(mb, F, -0.3, 0.3, y0 - 0.85, y1 + 0.85, zt + 1.0, zt + 1.35, "Roof_OP_Ridge")
        K.bb(mb, F, -hb, hb, y0 - 0.1, y1 + 0.1, zg0 - 0.35, zg0 - 0.1, WM)          # estrado
        for yy in (y0 + 0.4, y1 - 0.4):                                              # noren/sudare de bambu nas pontas
            K.bb(mb, F, -hb + 0.2, hb - 0.2, yy - 0.06, yy + 0.06, zt - 1.6, zt - 0.35, "Cloth_OP_Indigo")
        # ro (remo de popa)
        mb.beam(F.p(0.2, -Lb / 2 + 0.3, zg0 + 0.9), F.p(0.4, -Lb / 2 - 3.6, SEA + 0.2), 0.18, 0.12, WD, 0.0)
    else:                                                # 2 remos atravessados nos bancos
        for s in (-1, 1):
            mb.beam(F.p(s * 0.6, -Lb * 0.32, meta[n // 2][3] - 0.15), F.p(s * 0.9, Lb * 0.32, meta[n // 2][3] - 0.12),
                    0.12, 0.08, WM, 0.0)
            K.bb(mb, F, s * 0.9 - 0.06, s * 0.9 + 0.06, Lb * 0.24, Lb * 0.4, meta[n // 2][3] - 0.25,
                 meta[n // 2][3] - 0.05, WM)
    return F.p(0.0, Lb / 2 - 0.3, zg0 + 0.9), F.p(0.0, -Lb / 2 + 0.3, zg0 + 0.4)


def boats(mb):
    # bote a remo na palafita (lado leste), amarrado ao pe do guarda-corpo
    bow, stern = boat(mb, 251.0, 57.0, 0.0, 11.0, 3.4)
    SH.rope_sag(mb, bow, (245.7, 62.0, H + 1.0), 0.8, 0.09, 6)
    SH.rope_sag(mb, stern, (245.7, 52.0, H + 1.0), 0.8, 0.09, 6)
    # barco coberto no cais norte (faixa x 206..222), amarrado nos cabecos do cais
    bow, stern = boat(mb, 229.0, 213.0, 0.0, 14.0, 4.4, roof=True)
    b1 = bollard(mb, 220.6, 222.0, col=False)          # na borda do cais, dentro da guarda do op_col
    b2 = bollard(mb, 220.6, 206.0, col=False)
    SH.rope_sag(mb, bow, b1, 0.9, 0.1, 6)
    SH.rope_sag(mb, stern, b2, 0.9, 0.1, 6)


# ================================================================== AMARRAS DO NAVIO e postes
def ship_lines(mb):
    pts = {y: Vector((PIER_A[2] - 1.4, y, H + 1.1)) for y in BOLLARDS_A}
    for ys, yb in ((116.0, 116.0), (190.0, 194.0), (136.0, 130.0), (172.0, 178.0)):
        z = SH.zb(ys, -1)
        a = Vector((SH.SX - SH.wid(ys, z) - 0.1, ys, z + 0.25))
        SH.rope_sag(mb, a, pts[yb], 1.3, 0.13, 8)


LAMPS = [(225.0, 113.0), (225.0, 73.0)]


def lamps(mb):
    for i, (x, y) in enumerate(LAMPS):
        if i == 0:
            K.lantern_post(mb, Frame(x, y, H, 0.0), 8.6, 1.6, "L_OPProp_Lamp_Porto_%d" % i, 40.0)
        else:
            K.lantern_box_post(mb, Frame(x, y, H, 0.0), 7.6, "L_OPProp_Lamp_Porto_%d" % i, 35.0)
        col_box("OP_PortProp", (1.4, 1.4, 8.6), (x, y, H + 4.3))


# ================================================================== cameras de revisao
EYE = L.EYE
CAMS = {
    "CAM_OPPort_PH_DescidaA": ((174.0, 140.0, L.T1 - 15.6 * 0.767 + EYE), (232.0, 152.0, 52.0), 22),
    "CAM_OPPort_PH_DescidaB": ((160.0, 82.0, H + 20.0 * 0.767 + EYE), (234.0, 56.0, 46.0), 22),
    "CAM_OPPort_PH_Cais": ((215.5, 100.0, H + EYE), (238.0, 160.0, 54.0), 22),
    "CAM_OPPort_PH_Pier": ((226.5, 118.0, H + EYE), (246.0, 152.0, 54.0), 22),
    "CAM_OPPort_PH_Palafita": ((224.0, 47.0, H + EYE), (238.0, 60.0, H + 5.0), 22),
    "CAM_OPPort_Pier": ((262.0, 100.0, SEA + 9.0), (228.0, 150.0, SEA + 3.0), 24),
    "CAM_OPPort_Palafita": ((210.0, 14.0, 60.0), (238.0, 58.0, 45.0), 26),
    "CAM_OPPort_Armazens": ((152.0, 60.0, H + 6.5), (134.0, 86.0, H + 4.5), 24),
    "CAM_OPPort_ArmazemH3": ((206.0, 104.0, HM + 7.0), (176.0, 120.0, HM + 6.0), 24),
    "CAM_OPPort_Barcos": ((250.0, 226.0, 49.0), (229.0, 210.0, SEA + 1.5), 26),
    "CAM_OPPort_Escadas": ((112.0, 12.0, 96.0), (176.0, 100.0, 58.0), 24),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        camera(n, loc, tgt, lens)


def remove_terrain_piers():
    ob = bpy.data.objects.get("OP_Ter_Piers")
    if ob is not None:
        bpy.data.objects.remove(ob, do_unlink=True)
        return True
    return False


def build():
    removed = remove_terrain_piers()
    rnd = random.Random(8201)
    mp = MB("OP_Port_Piers", COLL, rnd, detail="far", floor=None)        # madeira: pier, palafita, barcos, amarras
    mbd = MB("OP_Port_Built", COLL, random.Random(8202), detail="far", floor=None)   # pedra/reboco: escadas, armazens
    parts = []

    def tri(m):
        return sum(len(f.verts) - 2 for f in m.bm.faces)
    for fn, m in ((pier_a, mp), (palafita, mp), (boats, mp), (ship_lines, mp), (lamps, mbd), (stairs, mbd),
                  (warehouses, mbd), (cargo, mbd)):
        t0 = tri(m)
        fn(m)
        parts.append("%s %d" % (fn.__name__, tri(m) - t0))
    print("op_harbor: tris por parte: " + ", ".join(parts))
    o1 = mp.finish()
    o2 = mbd.finish()
    cams()
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in (o1, o2) if o)
    print("op_harbor: %d tris (pier+palafita+barcos %d mat, construido %d mat); OP_Ter_Piers removido=%s" % (
        tris, len(o1.data.materials), len(o2.data.materials), removed))
