# op_harbor - ZONA HARBOR da Ilha 5 (ONE PIECE / WANO). M3 (PLANO_OP 0.8, 4.2, 4.3, 9) + V2-2 PORTO (PLANO_V2 secao 5).
# Prefixo OP_Port_ (dono "harbor" no export_op/studio_op/op_lib), colecao 16_HARBOR. Pecas moveis VFX_OP_* em
# 12_VFX_HELPERS (dono "vfx"). Luzes de rua so NightOnly (L_OPProp_Lamp_Porto_*); 1 luz de dia no interior do armazem
# aberto (L_OPPort_Int_Armazem, interior 4 do PLANO_V2 3.5). Colisoes simples COL_OP_Port*.
#
# V2-2 (feedback 10/10, U9: "area de navegacao fraca, so os barcos porem sem dinamica, sem a sensacao de estar num
# ambiente de embarcacao de verdade"; U13: "estrutura numa montanha sem necessidade e feia"; U16 bandeiras):
#   * SAIU o H3 (armazem de 2 pisos no topo da muralha / rua alta) e a carga dele: a muralha fica limpa com a PortoA.
#     O "escritorio do porto" desceu para o cais, dentro do armazem aberto.
#   * PECAS MOVEIS (sistema que o jogo JA tem: tag IlhaMovel do montar -> LocalScript ILHA_NARUTO_Movel; atributos
#     pivot/axis/rpm = giro, bob(+rate) = sobe/desce). Sem colisao (cenario sobre a agua):
#       VFX_OP_Boat_1  2 sampans AMARRADOS de contrabordo na doca entre a palafita e o pier, presos as argolas do cais;
#                      o de dentro esta sendo CARREGADO pelo guindaste (bob 0,30)
#       VFX_OP_Boat_2  barco de pesca com a rede amontoada, cestos e o farol de pesca (isaribi) na palafita (bob 0,40)
#       VFX_OP_Boat_3  yakatabune (barco coberto) no cais norte (bob 0,35)
#       VFX_OP_Crane_Drum  tambor do guindaste com as barras de manobra, GIRANDO (rpm 5, eixo x: enrola o cabo)
#       VFX_OP_Crane_Load  lingada de fardos SUBINDO devagar do sampan ate a altura do cais e descendo (bob 3,8 /
#                      rate 0,06 = ciclo de 16,7 s: sobe 11,7 s a ~0,33/s = a velocidade de aro do tambor, desce 5 s)
#     + VFX_OP_Junk (op_ship). Cabos que mudam de comprimento: cabo FIXO da ponta da lanca ate o ponto mais alto da
#     lingada + cabo MOVEL (mais fino, dentro do fixo) na propria lingada -> nunca abre fresta.
#   * CAIS COM VIDA: GUINDASTE de madeira (mastro com escoras sobre sapata de pedra, lanca, moitoes, estai, tambor em
#     cavaletes), fardos esperando a lingada, ESCADA DE MARINHEIRO na muralha da doca, cestos de peixe, REDES DE PESCA
#     secando em varais junto a muralha (malha de cabo + boias), BARCO EM REPARO em cavaletes (sapateiro com piche),
#     carrinho de carga, pilhas de carga (kit V2 goods_pile), carga esperando embarque no pier.
#   * ARMAZEM ABERTO (no lugar do H2; interior 4 do PLANO_V2): soco de pedra, piso de tabuas a 0,9 com RAMPA DE CARGA,
#     estrutura de madeira aparente (pilares, frechal, tesouras com pendural), paredes de tabuas, frente ABERTA com os
#     portoes de correr empurrados para as pontas, telhado V2 (op_kit2.roof2), carga empilhada dentro, BALANCA de
#     mercador pendurada na tesoura, ESCRITORIO DO PORTO no canto (estrado de tatami, escrivaninha, livros, cofre,
#     biombo, andon). H1 virou uma fileira de 2 KURA do kit V2 (op_kit2.kura). H4 (pavilhao vermelho da palafita) e H5
#     (telheiro de carga) continuam.
#   * Postes: lamp_post do kit V2 (o poste antigo do op_kit saiu).
# Coordenadas dos armazens/pavilhao sao DESTE modulo (a V2-0 tirou o H3 do L.BUILDINGS e vai trocar a lista): nao
# dependem mais do L.BUILDINGS.
#
# O QUE CONTINUA (M3/M6b): PIER do navio e PALAFITA (estacas, longarinas, cabecos, defensas, guarda-corpos), ESCADAS
#   PortoA/PortoB com a muralha de cantaria, amarras do navio, argolas do cais. AGUA: o mar local (36) e do Roblox
#   (WATER_Sea do op_core); nenhum marcador novo.
import math, random
import bpy, bmesh
from mathutils import Vector, geometry
import op_lib as DL
from op_lib import MB, Frame, col_box, col_ramp, camera
import op_layout as L
import op_kit as K
import op_kit2 as K2
import op_ship as SH

COLL = "16_HARBOR"
H = L.HARBOR                    # 42,2
HM = L.HMID                     # 65,2
SEA = L.SEA                     # 36
WD, WM, LAC, GOLD, IRON = "Wood_OP_Dark", "Wood_OP_Mid", "Wood_OP_Lacquer", "Metal_OP_Gold", "Metal_OP_Iron"
HULL, ROPE, MOSS, STRAW = "Wood_OP_Hull", "Rope", "Cliff_OP_Moss", "Cloth_OP_Straw"
ST, STP, STD, STEEL = "Stone_OP", "Stone_OP_Path", "Stone_OP_Dark", "Metal_OP_Steel"
F0 = Frame(0.0, 0.0, 0.0, 0.0)
PIER_A = (222.0, 110.0, 234.0, 200.0)          # pier do navio (HARBOR_POLY)
PIER_B = (222.0, 40.0, 246.0, 76.0)            # palafita
X_ROOT = 223.0                                  # as tabuas comecam depois da capa de pedra do cais (op_terrain)
BOLLARDS_A = [116.0, 130.0, 145.0, 160.0, 178.0, 194.0]
# (nome, familia, x, y, w, d, rumo da FRENTE, cota, pisos, telhado, cor) - proprios deste modulo (V2)
SPECS = {
    "H4": ("H4", "pavilhao", 236.0, 58.0, 18.0, 14.0, 180.0, H, 1, "hip", "Roof_OP_Red"),
    "H5": ("H5", "armazem", 138.0, 90.0, 20.0, 14.0, -90.0, H, 2, "kirizuma", "Roof_OP_Blue"),
}
KURAS = [(129.4, 44.2, 11.0, 15.0, 12.5, "Roof_OP_Blue", 11), (141.6, 44.2, 11.0, 15.0, 10.6, "Roof_OP_Cobalt", 23)]
ARM_C, ARM_W, ARM_D, ARM_FZ, ARM_H = (192.0, 42.0), 22.0, 14.0, 0.9, 7.6   # armazem aberto (frente para o norte)
CRANE_M = (219.6, 80.6)                         # mastro do guindaste (canto da doca)
LOAD_C = (230.0, 88.9)                          # lingada (sobre o sampan de dentro)
LOAD_LOW = SEA + 1.3                            # fundo da lingada na posicao BAIXA (modelada assim: bob vai de 0 a +A)
LOAD_A, LOAD_RATE, DRUM_RPM = 3.8, 0.06, 5.0
DRUM_C, DRUM_R = (219.6, 77.0, H + 2.45), 0.65   # tambor + RODA de manobra (r 2,2) no cavalete leste
WHEEL_R = 2.2
CRANE_TOP, JIB_HEEL_Z, JIB_TIP_Z = H + 14.0, H + 3.6, H + 11.6
# barcos a >= 6 da borda alcancavel (o gate 'visual' conta todo piso a <= 6 de um piso alcancado; a guarda nao conta)
SAMPANS = [(230.0, 92.6, 11.0, 3.4), (233.9, 91.7, 10.6, 3.3)]   # contrabordo no meio da doca (proa para o norte)
FISHER = (234.0, 31.0, 12.0, 3.6)              # barco de pesca ao sul da palafita (proa para +x)
ROWBOAT = (234.6, 26.8, 9.6, 3.0)               # bote de contrabordo por fora do barco de pesca
SKIFF = (229.8, 237.0, 8.4, 2.7)                # bote junto do yakatabune (cais norte)
LONJA_C, LONJA_W, LONJA_D, LONJA_H = (178.0, 76.0), 14.0, 9.0, 6.8   # lonja (mercado de peixe coberto)
YAKATA = (230.6, 214.0, 14.0, 4.4)             # barco coberto no cais norte
HAULED = (199.0, 88.4)                          # barco em reparo nos cavaletes (ao longo de x)
NET_RACKS = [(170.6, 178.4), (180.6, 188.4)]    # varais de rede junto a muralha (y ~96,6)
NET_Y = 96.6
BOAT_BOB = {"VFX_OP_Boat_1": 0.30, "VFX_OP_Boat_2": 0.40, "VFX_OP_Boat_3": 0.35}
BOAT_KEEP = {HULL: HULL, WM: HULL}              # pecas moveis: 2 materiais (casco/tabuado claro + madeira escura)
# materiais de POUCO uso (pecas do kit) trocados por vizinhos de cor proxima: cada material = 1 MeshPart no export
REMAP_BUILT = {"Cloth_OP_Tatami": STRAW, "Cloth_OP_Black": WD, "Window_OP_Warm": "Glass_OP_Lantern",
               "Plaster_OP_Warm": "Plaster_OP", "Roof_OP_Shingle": WD, "Stone_OP_Wall": ST, "Cloth_OP_Red": LAC,
               "Cloth_OP_White": "Plaster_OP"}
REMAP_PIERS = {"Cloth_OP_Red": LAC, "Wood_OP_Hull": WM, "Stone_OP_Path": ST, "Stone_OP_Dark": ST,
               "Window_OP_Warm": "Glass_OP_Lantern"}


def _spec(nm):
    return SPECS[nm]


def bframe(nm):
    s = _spec(nm)
    return Frame(s[2], s[3], s[7], math.radians(s[6]) - math.pi / 2)


# ================================================================== PIERS (pier do navio + palafita)
def pile(mb, x, y, z_top, r=0.5, m=WD, moss=False):
    # M6b: sem tampas (a de cima encosta no cabecote, a de baixo fica no fundo do mar) - paga a muralha das escadas
    mb.cyl(r, z_top - 29.0, (x, y, (z_top + 29.0) / 2.0), m=m, n=6, bevel=0.0, caps=False)
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
    for a, b in zip(pts, pts[1:]):        # V2 (gate): o corrimao e chao alcancavel -> colisao da altura dele
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        col_box("OP_PortRail", (ln + 0.4, 0.6, h), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, base + h / 2),
                (0.0, 0.0, math.atan2(b[1] - a[1], b[0] - a[0])))
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
        if x < 224.0:
            continue            # M6b: a 1a fileira (x 223,6: cabecote + estacas) fica DENTRO do muro do cais
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
        c = Fp.p(sx * (W / 4 + 1.1), D / 2 - 0.5, 1.2 + 1.6)
        col_box(area, (W / 2 - 2.2, 0.6, 3.2), c, Fp.r())
    roof_cols_measured(mb, Fp, area, W, D, 3.0)
    return Fp


def roof_cols_measured(mb, F, area, W, D, ov):
    """V2 (gate 'visual'): colisao do telhado de 4 aguas do pavilhao (alcancavel do topo do guarda-corpo). As cotas
    sao MEDIDAS na malha ja montada (raio de cima no bmesh): beira e cumeeira; 2 aguas compridas + 2 tacaniças"""
    from mathutils.bvhtree import BVHTree
    bvh = BVHTree.FromBMesh(mb.bm)

    def zt(x, y):
        p = F.p(x, y, 0.0)
        h = bvh.ray_cast(Vector((p.x, p.y, H + 60.0)), Vector((0, 0, -1)), 80.0)
        return h[0].z if h[0] is not None else None
    Ye, Xe = D / 2 + ov - 0.4, W / 2 + ov - 0.4
    x0 = (W - D) / 2                                     # ponta da cumeeira
    run = Xe - x0
    z1, z2 = zt(-x0 * 0.5, Ye), zt(-x0 * 0.5, Ye * 0.45)
    z3, z4 = zt(Xe, 0.0), zt(x0 + run * 0.45, 0.0)
    if None in (z1, z2, z3, z4):
        print("AVISO op_harbor: telhado do pavilhao nao medido")
        return
    k1 = (z2 - z1) / (Ye * 0.55)                         # caimento medido na agua (fora da cumeeira)
    k2 = (z4 - z3) / (run * 0.55)
    zr1, zr2 = z1 + k1 * Ye, z3 + k2 * run
    a1, a2 = math.atan(k1), math.atan(k2)
    for sy in (-1, 1):
        c = F.p(0.0, sy * Ye / 2, 0.0)
        col_box(area, (W + 2 * ov - 1.0, math.hypot(Ye, zr1 - z1), 0.8), (c.x, c.y, (zr1 + z1) / 2 - 0.45),
                F.r(-sy * a1, 0.0, 0.0))
    for sx in (-1, 1):
        c = F.p(sx * (x0 + run / 2), 0.0, 0.0)
        col_box(area, (math.hypot(run, zr2 - z3), D + 2 * ov - 1.0, 0.8), (c.x, c.y, (zr2 + z3) / 2 - 0.45),
                F.r(0.0, sx * a2, 0.0))
    zc = zt(0.0, 0.0)                                    # cumeeira (topo da peca de remate)
    if zc is not None:
        c = F.p(0.0, 0.0, 0.0)
        col_box(area, (W - D + 2.4, 2.4, max(1.0, zc - zr1 + 1.0)), (c.x, c.y, (zc + zr1) / 2 - 0.3), F.r())
    print("op_harbor: telhado do pavilhao medido: beira %.1f / %.1f, cumeeira %.1f / %.1f" % (z1, z3, zr1, zr2))


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
    mb.beam(a, b, 0.34, 0.34, LAC, 0.0, math.pi / 4)     # V2: secao em losango (o topo nao vira 'chao' no gate)
    a, b = F.p(x, y0, ztl(y0) + h * 0.5), F.p(x, y1, ztl(y1) + h * 0.5)
    mb.beam(a, b, 0.16, 0.2, LAC, 0.0)
    K.giboshi(mb, F, x, ys[-1], ztl(ys[-1]) + h, 0.85)
    mb.box((0.5, 0.5, 0.16), F.p(x, ys[0], ztl(ys[0]) + h + 0.08), F.r(), LAC, 0.0)


SWALL_T = 1.2                   # espessura da muralha lateral no topo (= banzo do kit: o corrimao e a guarda do op_col
SWALL_M, SWALL_D, SWALL_CAP = "Stone_OP_Wall", "Stone_OP_Dark", "Stone_OP_Path"   # ficam no meio dela)
# talude (graus) da face de fora por lado (s = -1, +1 no referencial da escada). PortoA +1 = norte, encostado no arrimo
# do T1 (y 150): sem talude (nao invade o arrimo)
SWALL_BATTER = {"PortoA": (5.0, 0.0), "PortoB": (5.0, 5.0)}
# V2: a muralha NORTE da PortoA engrossa ate o arrimo do T1 (y 150): fecha a fenda de 2,8 x 23 entre a escada e o
# arrimo (fresta medida pelo gate 'visual' / auditoria V2: 'rua alta do porto, ate 3,8')
SWALL_TW = {"PortoA": (SWALL_T, 4.0), "PortoB": (SWALL_T, SWALL_T)}


def _q4(mb, Fs, pts, m, want):
    """quad com a normal virada para 'want' (local Fs); so as faces que se veem (economia de tris)"""
    W = [Fs.p(*p) for p in pts]
    nrm = (W[1] - W[0]).cross(W[2] - W[0]) + (W[2] - W[0]).cross(W[3] - W[0])
    if nrm.dot(Fs.p(*want) - Fs.p(0.0, 0.0, 0.0)) < 0:
        W.reverse()
    mb.quad(*W, m)


def stair_wall(mb, Fs, s, w, n, rise, tread, cheek_h, zf, batter, key, tw=None):
    """M6b (item 37): MURALHA lateral da escada (no lugar dos banzos do kit, que nas escadas de 23 viravam paineis lisos
    de 3,6 x 23): fiadas horizontais de 1,4..2,3 em pedras de 3,6..6,4 com juntas desencontradas (0,06) sobre miolo
    escuro rebaixado 0,22, 1 pedra em 6 em outro tom, face com recuo +-0,05 por pedra e TALUDE (face sai para baixo),
    topo das fiadas cortado pela linha da escada (trapezios sob a capa) e CAPA clara inclinada em lajes com pingadeira
    0,15 - a mesma linguagem de cantaria do muro do cais. Cada pedra so com a FRENTE (2 tris; pontas so nas 2
    extremidades da muralha): a junta de 0,06 deixa ver o miolo escuro 0,22 atras. Referencial Fs da escada (x
    atravessado, +y sobe), lado s."""
    t = math.tan(math.radians(batter))
    ztl = lambda y: rise * (y / tread + 1.0) + cheek_h          # linha do banzo (o corrimao pousa na capa: ztl + 0,26)
    zt = lambda y: ztl(y) - 0.1                                 # pe da capa = topo das pedras
    yat = lambda z: (z + 0.1 - cheek_h) / rise * tread - tread  # y em que zt(y) = z
    Y0, Y1 = 0.03, tread * n - 0.03
    u_in = w / 2 - 0.1                                          # costas dentro dos blocos dos espelhos (escondidas)
    tw = SWALL_T if tw is None else tw
    face = lambda y, z: w / 2 + tw + t * max(0.0, zt(y) - z)
    P = lambda u, y, z: (s * u, y, z)
    OUT, UP, BK, FW = (s, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0), (0.0, 1.0, 0.0)
    # miolo escuro (aparece so nas juntas), 0,22 atras da face: so a face
    _q4(mb, Fs, [P(face(Y0, zf) - 0.22, Y0, zf), P(face(Y1, zf) - 0.22, Y1, zf), P(face(Y1, zt(Y1)) - 0.22, Y1, zt(Y1)),
                 P(face(Y0, zt(Y0)) - 0.22, Y0, zt(Y0))], SWALL_D, OUT)
    z, c, n_st = zf, 0, 0
    while True:
        hc = 1.4 + 0.9 * K._h01(key, s, "c", c)
        z2 = z + hc
        y_lo = max(Y0, yat(z + 0.3))
        if y_lo > Y1 - 0.6:
            break
        y_t = yat(z2 + 0.25)                                    # dali para cima a fiada tem a altura cheia
        cuts = [y_lo]
        yy = y_lo + (0.0 if c % 2 else 1.6 * K._h01(key, s, "o", c))
        k = 0
        while True:
            yy += 3.6 + 2.8 * K._h01(key, s, c, k)
            k += 1
            if yy >= Y1 - 1.2:
                break
            cuts.append(yy)
        if y_lo + 0.6 < y_t < Y1 - 0.6:
            cuts = sorted([q for q in cuts if abs(q - y_t) > 1.0] + [y_t])
        cuts.append(Y1)
        for j, (ya, yb) in enumerate(zip(cuts, cuts[1:])):
            if yb - ya < 0.3:
                continue
            ya2, yb2 = ya + (0.03 if ya > Y0 + 1e-3 else 0.0), yb - (0.03 if yb < Y1 - 1e-3 else 0.0)
            ta = (zt(ya2) if ya2 <= y_t + 1e-6 else z2) - 0.03
            tb = (zt(yb2) if yb2 <= y_t + 1e-6 else z2) - 0.03
            za = z + (0.03 if c else 0.0)
            df = 0.1 * (K._h01(key, s, c, j, "d") - 0.5)
            m = SWALL_M if K._h01(key, s, c, j, "m") > 0.16 else "Stone_OP"
            fa0, fa1, fb0, fb1 = face(ya2, za) + df, face(ya2, ta) + df, face(yb2, za) + df, face(yb2, tb) + df
            _q4(mb, Fs, [P(fa0, ya2, za), P(fb0, yb2, za), P(fb1, yb2, tb), P(fa1, ya2, ta)], m, OUT)
            # (sem topo: sob a capa nao aparece e nas juntas a fresta mostra o miolo escuro, que e a leitura da junta)
            # pontas so nas 2 extremidades da muralha; entre pedras a junta de 0,06 mostra o miolo escuro (a junta)
            if ya2 <= Y0 + 1e-3:
                _q4(mb, Fs, [P(u_in, ya2, za), P(fa0, ya2, za), P(fa1, ya2, ta), P(u_in, ya2, ta)], m, BK)
            if yb2 >= Y1 - 1e-3:
                _q4(mb, Fs, [P(u_in, yb2, za), P(fb0, yb2, za), P(fb1, yb2, tb), P(u_in, yb2, tb)], m, FW)
            n_st += 1
        z = z2
        c += 1
    # capa clara inclinada em lajes (junta 0,06), pingadeira 0,15 dos 2 lados
    xa, xb = w / 2 - 0.15, w / 2 + tw + 0.15
    cp = lambda y: [P(xa, y, ztl(y) - 0.1), P(xb, y, ztl(y) - 0.1), P(xb, y, ztl(y) + 0.26), P(xa, y, ztl(y) + 0.26)]
    y, k = 0.05, 0
    while y < Y1 - 0.2:
        y2 = min(Y1, y + 4.2 + 1.8 * K._h01(key, s, "cap", k))
        if Y1 - y2 < 1.0:
            y2 = Y1
        K.loft(mb, Fs, [cp(y + (0.03 if k else 0.0)), cp(y2 - (0.03 if y2 < Y1 else 0.0))], SWALL_CAP)
        y, k = y2, k + 1
    return n_st


def newels(mb, Fs, s, w, n, rise, tread, cheek_h, zf, lamp, tw=None):
    """pilaretes de arranque/chegada sobre a muralha (os do kit vinham junto com os banzos): o de arranque com ANDON
    quando 'lamp' (mesma luz L_OPProp_Lamp_PortoEscB_0/1 do kit), o de chegada com tampa piramidal"""
    tw = SWALL_T if tw is None else tw
    xa, xb = (w / 2, w / 2 + tw) if s > 0 else (-w / 2 - tw, -w / 2)
    for yc, ztp in ((-0.55, cheek_h + 0.75), (tread * n - 0.45, rise * n + cheek_h + 0.75)):
        K.bb(mb, Fs, xa - 0.2, xb + 0.2, yc - 0.65, yc + 0.65, zf, ztp - 0.3, SWALL_M)
        if lamp and yc < 0:
            xm = (xa + xb) / 2
            K.bb(mb, Fs, xm - 0.95, xm + 0.95, yc - 0.85, yc + 0.85, ztp - 0.3, ztp - 0.06, SWALL_CAP)
            K.bb(mb, Fs, xm - 0.32, xm + 0.32, yc - 0.32, yc + 0.32, ztp - 0.06, ztp + 0.5, WD)
            c = K._box_lantern(mb, Fs, (xm, yc, ztp + 0.64), 0.55, 0.55, 1.4)
            DL.light("%s_%d" % (lamp, 0 if s < 0 else 1), "POINT", Fs.p(*c), 35.0, K.WARM, 0.2)
        else:
            K.lathe(mb, Fs, ((xa + xb) / 2, yc, ztp - 0.3), [(0.95, 0.0), (0.95, 0.16), (0.3, 0.42), (0.1, 0.5)], 4,
                    SWALL_CAP, math.pi / 4)


def stair_wall_col(Fs, nm, s, w, n, rise, tread, cheek_h, tw, batter):
    """V2 (gate 'visual'): a CAPA da muralha e uma faixa andavel ao lado da escada e o TALUDE da face de fora engorda
    a pedra ate ~2 no pe. Colisao: 3 caixas RETAS por lado (tercos da escada), da capa ate a pedra do talude, com o
    topo 8,5 acima da capa no fim de cada terco (cerca invisivel como a guarda da escada do op_col). Caixas retas e
    encostadas, sem sobreposicao: o gate conta o topo de toda colisao como piso e o teste 'dentro da caixa' dele erra
    onde caixas se sobrepoem (pontas inclinadas de rampa deixavam o pilarete de arranque descoberto)."""
    area = "OP_PortStairWall" + nm
    ztl = lambda y: rise * (y / tread + 1.0) + cheek_h + 0.26
    L_ = tread * n
    t = math.tan(math.radians(batter))
    xin = w / 2 - 0.15
    for k in range(3):
        y0, y1 = L_ * k / 3 - (1.4 if k == 0 else 0.0), L_ * (k + 1) / 3
        xout = w / 2 + tw + 0.15 + t * (ztl(y1) - 0.36)
        top = ztl(y1) + 8.5
        col_box(area, (xout - xin, y1 - y0, top + 0.3), Fs.p(s * (xin + xout) / 2, (y0 + y1) / 2, top / 2 - 0.15),
                Fs.r())


_WMB = [None]          # MB proprio da muralha das escadas (pedras com so as faces visiveis: fecha com recalc=False)


def stairs(mb):
    wm = _WMB[0] or mb
    for nm, lamp in (("PortoA", None), ("PortoB", "L_OPProp_Lamp_PortoEscB")):     # andon so no pe do cais
        foot, deg, w, n, tread, g = L.stair_frame(nm)
        rise = L.stair_rise(nm)
        Fs = Frame(foot[0], foot[1], foot[2], math.radians(deg) - math.pi / 2)
        # M6b: degraus do kit SEM banzos (cheeks=False): as laterais sao a muralha de cantaria (stair_wall)
        K.stair_stone(mb, Fs, w, n, rise=rise, tread=tread, z_floor=-0.3, cheek_h=1.0, cheeks=False)
        for i, s in enumerate((-1, 1)):
            tw = SWALL_TW[nm][i]
            stair_wall(wm, Fs, s, w, n, rise, tread, 1.0, -0.3, SWALL_BATTER[nm][i], "sw" + nm, tw)
            newels(mb, Fs, s, w, n, rise, tread, 1.0, -0.3, lamp, tw)
            stair_rail(mb, Fs, s * (w / 2 + 0.6), n, rise, tread, 1.0)
            c = Fs.p(s * (w / 2 + 0.6), -0.55, 0.0)
            col_box("OP_PortProp", (2.0, 1.7, 4.4), (c.x, c.y, foot[2] + 2.2), Fs.r())
            stair_wall_col(Fs, nm, s, w, n, rise, tread, 1.0, tw, SWALL_BATTER[nm][i])



# ================================================================== ARMAZENS V2
def kura_row(mb):
    """H1 V2: 2 KURA do kit V2 lado a lado (empena para o cais, porta-cofre, namako, telhado pesado), viela de 1,2"""
    for i, (x, y, W, D, h, roof, seed) in enumerate(KURAS):
        F = Frame(x, y, H, 0.0)
        info = K2.kura(mb, F, W, D, roof, tsuma=True, lod=1, seed=seed, h=h)
        col_box("OP_PortHouseH1", (W + 1.0, D + 1.0, 1.4 + h), F.p(0.0, 0.0, (1.4 + h) / 2))
        # V2 (gate 'visual'): o telhado se alcanca descendo do T1 -> 2 aguas com colisao (topo ~0,4 sob a telha)
        Ye = W / 2 + 0.12 + 1.9
        ze, zr = info["eave_z"] + 0.7 + 0.62, info["ridge_z"]
        ang = math.atan2(zr - ze, Ye)
        for sx in (-1, 1):
            c = F.p(sx * Ye / 2, 0.0, 0.0)
            col_box("OP_PortHouseH1", (math.hypot(Ye, zr - ze), D + 2 * 1.7 + 0.3, 0.8),
                    (c.x, c.y, (ze + zr) / 2 - 0.45), (0.0, sx * ang, 0.0))
        col_box("OP_PortHouseH1", (3.0, D + 2 * 1.7 + 0.6, 1.9), F.p(0.0, 0.0, zr - F.o.z + 0.4))   # cumeeira
        col_box("OP_PortHouseH1", (6.8, 1.6, 0.8), F.p(0.0, D / 2 + 1.05, 1.15))     # soleira da porta-cofre


def armazem(mb):
    """ARMAZEM ABERTO (H2 V2, interior 4 do PLANO_V2): ver cabecalho. Frente (+y) para o cais."""
    W, D, fz, h = ARM_W, ARM_D, ARM_FZ, ARM_H
    Fa = Frame(ARM_C[0], ARM_C[1], H, 0.0)
    area = "OP_PortHouseH2"
    # soco de pedra + capa, piso de tabuas (frestas mostram a capa escura 0,12 abaixo)
    K.bb(mb, Fa, -W / 2 - 0.45, W / 2 + 0.45, -D / 2 - 0.45, D / 2 + 0.45, -0.3, fz - 0.24, ST)
    K.bb(mb, Fa, -W / 2 - 0.35, W / 2 + 0.35, -D / 2 - 0.35, D / 2 + 0.35, fz - 0.24, fz - 0.12, STP)
    for x in K.even(-W / 2 + 0.2, W / 2 - 0.2, 1.6):
        K.bb(mb, Fa, x - 0.76, x + 0.76, -D / 2 + 0.2, D / 2 + 0.25, fz - 0.12, fz, WM)
    # RAMPA DE CARGA no meio da frente (6 de largura, 0,9 -> 0 em 3,75) sobre 2 longarinas
    y0, y1 = D / 2 + 0.45, D / 2 + 4.2
    ln = math.hypot(y1 - y0, fz)
    pit = math.atan2(fz, y1 - y0)
    for k in range(6):
        s = (k + 0.5) / 6
        c = Fa.p(0.0, y0 + (y1 - y0) * s, fz * (1 - s) - 0.08)
        mb.box((6.0, ln / 6 - 0.06, 0.16), c, Fa.r(pit, 0.0, 0.0), WM, 0.0)
    for x in (-2.5, 2.5):
        K.beam(mb, Fa, (x, y1 - 0.1, 0.0), (x, y0, fz - 0.3), 0.4, 0.3, WD)
    col_ramp(area, Fa.p(0.0, y1, 0.0), Fa.p(0.0, y0 - 0.2, fz), 6.0, 1.0)
    # PAREDES (estrutura aparente + tabuado) e FRENTE ABERTA (so pilares e frechal nos 4 vaos do meio)
    K2._body(mb, Fa, W, D, fz, h,
             {"F": ["board", "open", "open", "open", "open", "board"], "B": ["board"] * 5,
              "R": ["board", "lattice", "board"], "L": ["board"] * 3}, lod=1, lit=False)
    # portoes de correr (itado) empurrados para as pontas, na frente dos vaos fechados
    for s in (-1, 1):
        xa, xb = s * (W / 2 - 0.55), s * (W / 2 - 4.25)
        K.bb(mb, Fa, xa, xb, D / 2 + 0.2, D / 2 + 0.42, fz, fz + 6.7, WM)
        for zz in (fz + 0.5, fz + 3.3, fz + 6.2):
            K.bb(mb, Fa, xa, xb, D / 2 + 0.42, D / 2 + 0.56, zz - 0.14, zz + 0.14, WD)
        K.bb(mb, Fa, xa - s * 0.1, xb + s * 0.1, D / 2 + 0.15, D / 2 + 0.6, fz + 6.75, fz + 7.0, IRON)   # trilho
    # TELHADO V2 (kirizuma, cumeeira ao longo de x) + TESOURAS aparentes por dentro
    Fr = K.sub(Fa, 0.0, 0.0, fz)
    r = K2.roof2(mb, Fr, W, D, h, "kirizuma", "Roof_OP_Blue", ov=2.6, g_over=1.6, s0=0.42, s1=0.95, lift=0.5, tv=0.5,
                 lod=1, back_lod=1, ends=("timber", "timber"), courses=2, rafters=True)
    zr = r["zr"]
    for x in (-6.97, 0.0, 6.97):
        K.bb(mb, Fr, x - 0.3, x + 0.3, -D / 2 + 0.45, D / 2 - 0.45, h - 0.1, h + 0.45, WD)          # tirante
        zk = r["Hf"](x, 0.0) - 0.5 - 0.45
        K.bb(mb, Fr, x - 0.24, x + 0.24, -0.24, 0.24, h + 0.45, zk, WD)                        # pendural
        for sy in (-1, 1):
            K.beam(mb, Fr, (x, sy * (D / 2 - 1.4), h + 0.45), (x, sy * 0.3, zk - 0.6), 0.3, 0.3, WD)
    zk0 = r["Hf"](0.0, 0.0) - 0.5 - 0.45
    K.bb(mb, Fr, -W / 2 + 0.3, W / 2 - 0.3, -0.22, 0.22, zk0 - 0.05, zk0 + 0.3, WD)          # terca da cumeeira
    # placa (kanban) sobre a abertura + 2 chochin no frechal da frente
    K.bb(mb, Fa, -2.6, 2.6, D / 2 + 0.06, D / 2 + 0.3, fz + h - 2.1, fz + h - 0.7, WD)
    K.bb(mb, Fa, -2.2, 2.2, D / 2 + 0.3, D / 2 + 0.44, fz + h - 1.85, fz + h - 0.95, "Plaster_OP_Warm")
    K.lathe_y(mb, Fa, (0.0, D / 2 + 0.44, fz + h - 1.4), [(0.34, 0.0), (0.34, 0.12)], 10, LAC)
    Ff = K.sub(Fa, 0.0, D / 2, fz)
    for i, s in enumerate((-1, 1)):
        K2.eave_lantern(mb, Ff, s * (W / 2 - 2.4), h - 0.9, "L_OPProp_Lamp_PortoArm_%d" % i, 20.0)
    # ---------------------------------------------------------------- INTERIOR (a carga e o escritorio do porto)
    # caixas em 2 alturas no fundo (lado oeste)
    for k, x in enumerate((-9.6, -8.0, -6.4, -4.8)):
        K.crate(mb, Fa, x, -5.8, fz, 1.5, 1.2, 1.0, 0.04 * ((k % 3) - 1))
        if k < 3:
            K.crate(mb, Fa, x + 0.2, -5.8, fz + 1.0, 1.3, 1.1, 0.9, 0.06 * (k - 1))
    col_box(area, (6.6, 1.6, 1.9), Fa.p(-7.2, -5.8, fz + 0.95))
    # piramide de fardos de arroz
    for (y, z) in ((-2.4, 0.0), (-1.3, 0.0), (-0.2, 0.0), (-1.85, 0.95), (-0.75, 0.95), (-1.3, 1.9)):
        K2.tawara(mb, Fa, -8.4, y, fz + z, 0.0, 0.55, 1.7)
        K2.tawara(mb, Fa, -6.6, y, fz + z, 0.0, 0.55, 1.7)
    col_box(area, (3.8, 3.4, 2.4), Fa.p(-7.5, -1.3, fz + 1.2))
    # barris e jarros no fundo (lado leste do meio)
    K2.goods_pile(mb, K.sub(Fa, 1.6, -5.3, fz), "barrels")
    col_box(area, (5.0, 3.0, 1.6), Fa.p(2.4, -5.4, fz + 0.8))
    # BALANCA de mercador pendurada na tesoura oeste: fardo sendo pesado
    xs_, ys_ = -6.97, 2.4
    zb_ = fz + h                                       # face de baixo do tirante
    mb.rod(Fa.p(xs_, ys_, zb_), Fa.p(xs_, ys_, fz + 4.7), 0.06, ROPE, 4)
    K.bb(mb, Fa, xs_ - 0.12, xs_ + 0.12, ys_ - 1.7, ys_ + 1.5, fz + 4.55, fz + 4.75, WD)      # travessao
    K.lathe(mb, Fa, (xs_, ys_ + 1.35, fz + 3.6), [(0.0, 0.0), (0.32, 0.12), (0.34, 0.5), (0.15, 0.62)], 6, IRON)
    mb.rod(Fa.p(xs_, ys_ + 1.35, fz + 4.55), Fa.p(xs_, ys_ + 1.35, fz + 4.22), 0.04, IRON, 4)
    mb.rod(Fa.p(xs_, ys_ - 1.4, fz + 4.55), Fa.p(xs_, ys_ - 1.4, fz + 2.75), 0.06, ROPE, 4)
    K2.tawara(mb, Fa, xs_, ys_ - 1.4, fz + 1.75, math.pi / 2, 0.5, 1.5)
    K.crate(mb, Fa, xs_ + 0.1, ys_ + 0.2, fz, 1.6, 1.4, 0.9, 0.0)
    col_box(area, (2.0, 3.6, 2.8), Fa.p(xs_, ys_ - 0.4, fz + 1.4))
    # ESCRITORIO DO PORTO (canto leste do fundo): estrado com tatami, escrivaninha, livros, cofre, biombo, andon
    x0, x1, y0_, y1_ = 4.4, 10.3, -6.4, -1.4
    zt = fz + 0.6
    K.bb(mb, Fa, x0, x1, y0_, y1_, fz, zt - 0.12, WD)
    K.bb(mb, Fa, x0 + 0.16, x1 - 0.16, y0_ + 0.16, y1_ - 0.16, zt - 0.12, zt, "Cloth_OP_Tatami")
    K.bb(mb, Fa, x0 + 1.0, x0 + 3.0, y1_ + 0.05, y1_ + 0.7, fz, fz + 0.3, ST)                 # pedra de descalcar
    K.bb(mb, Fa, 6.2, 8.8, -4.3, -3.1, zt + 0.72, zt + 0.86, WD)                               # tampo da escrivaninha
    for xx in (6.35, 8.65):
        K.bb(mb, Fa, xx - 0.1, xx + 0.1, -4.2, -3.2, zt, zt + 0.72, WD)
    for k, (dx, z0b, hh) in enumerate(((6.7, 0.0, 0.16), (6.72, 0.16, 0.14), (7.35, 0.0, 0.2))):    # livros de conta
        K.bb(mb, Fa, dx - 0.32, dx + 0.32, -3.95, -3.45, zt + 0.86 + z0b, zt + 0.86 + z0b + hh,
             "Plaster_OP_Warm" if k != 1 else LAC)
    K.bb(mb, Fa, 7.7, 8.5, -4.0, -3.4, zt + 0.86, zt + 0.98, WD)                              # abaco (soroban)
    K.bb(mb, Fa, 6.9, 8.1, -2.6, -1.8, zt, zt + 0.12, LAC)                         # almofada
    K.bb(mb, Fa, 9.0, 10.0, -6.0, -5.2, zt, zt + 0.7, WD)                                     # cofre (senryo-bako)
    for zz in (zt + 0.18, zt + 0.52):
        K.bb(mb, Fa, 8.96, 10.04, -6.04, -5.16, zz - 0.06, zz + 0.06, IRON)
    for k in range(4):                                                                         # biombo de 4 folhas
        xa_ = 4.9 + k * 1.15
        yo = -6.05 + (0.22 if k % 2 else 0.0)
        K.bb(mb, Fa, xa_, xa_ + 1.12, yo, yo + 0.1, zt, zt + 2.2, WD)
        K.bb(mb, Fa, xa_ + 0.12, xa_ + 1.0, yo + 0.1, yo + 0.16, zt + 0.15, zt + 2.05, "Plaster_OP_Warm")
    K2.andon_floor(mb, Fa, 5.0, -2.2, zt, 0.9)
    col_box(area, (x1 - x0, y1_ - y0_, 0.6), Fa.p((x0 + x1) / 2, (y0_ + y1_) / 2, fz + 0.3))
    DL.light("L_OPPort_Int_Armazem", "POINT", Fa.p(0.0, -2.0, fz + 5.2), 220.0, K.WARM, 0.5)
    # ---------------------------------------------------------------- COLISAO (paredes, piso, telhado)
    col_box(area, (W + 0.9, D + 0.9, 1.1), Fa.p(0.0, 0.0, fz - 0.55))
    col_box(area, (W + 0.4, 1.0, h), Fa.p(0.0, -D / 2 + 0.4, fz + h / 2))
    for s in (-1, 1):
        col_box(area, (1.0, D, h), Fa.p(s * (W / 2 - 0.4), 0.0, fz + h / 2))
        col_box(area, (3.9, 1.4, h), Fa.p(s * (W / 2 - 2.1), D / 2 - 0.2, fz + h / 2))
    Ye = r["Ye"]
    for sy in (-1, 1):                     # as 2 aguas (a beira fica ~7,5 acima do cais: alcancavel de cima da carga)
        za, zb2 = r["Hf"](0.0, sy * Ye), r["Hf"](0.0, 0.0)
        ang = math.atan2(zb2 - za, Ye)
        c = Fr.p(0.0, sy * Ye / 2, (za + zb2) / 2 - 0.45)
        col_box(area, (W + 2 * 1.6, math.hypot(Ye, zb2 - za), 0.8), c, Fa.r(-sy * ang, 0.0, 0.0))
    return r


def lonja(mb):
    """LONJA (mercado de peixe coberto) no meio do cais: 8 pilares sobre pedras, frechais, telhado V2 de 2 aguas,
    2 bancadas compridas com tabuleiros de peixe, cestos e tinas no chao. Aberta dos 4 lados (o vento do mar)."""
    W, D, h = LONJA_W, LONJA_D, LONJA_H
    F = Frame(LONJA_C[0], LONJA_C[1], H, 0.0)
    xs = [-W / 2 + 0.4, -W / 6, W / 6, W / 2 - 0.4]
    for x in xs:
        for y in (-D / 2 + 0.4, D / 2 - 0.4):
            K.rock_base(mb, F, x, y, 0.0, 0.7, 0.4)
            K.bb(mb, F, x - 0.36, x + 0.36, y - 0.36, y + 0.36, 0.3, h - 0.6, WD)
    for y in (-D / 2 + 0.4, D / 2 - 0.4):
        K.bb(mb, F, -W / 2 - 0.2, W / 2 + 0.2, y - 0.42, y + 0.42, h - 0.6, h, WD)
    for x in xs:
        K.bb(mb, F, x - 0.3, x + 0.3, -D / 2 + 0.2, D / 2 - 0.2, h - 0.5, h - 0.05, WD)
    r = K2.roof2(mb, F, W - 0.8, D - 0.8, h, "kirizuma", "Roof_OP_Blue", ov=2.0, g_over=1.4, s0=0.42, s1=0.95,
                 lift=0.5, tv=0.45, lod=1, back_lod=1, ends=("board", "board"), courses=2, rafters=False)
    # bancadas com tabuleiros de peixe
    for y in (-1.5, 1.5):
        K.bb(mb, F, -W / 2 + 1.4, W / 2 - 1.4, y - 0.8, y + 0.8, 0.95, 1.15, WM)
        for x in (-W / 2 + 1.7, 0.0, W / 2 - 1.7):
            K.bb(mb, F, x - 0.13, x + 0.13, y - 0.65, y + 0.65, 0.0, 0.95, WD)
        for k, x in enumerate((-4.4, -1.5, 1.5, 4.4)):
            K.bb(mb, F, x - 1.15, x + 1.15, y - 0.62, y + 0.62, 1.15, 1.3, WD)
            for j in range(2):
                a = 0.3 + 0.9 * j + k
                Ff = K.sub(F, x - 0.4 + 0.8 * j, y + 0.18 * math.sin(a), 1.42, 0.25 * math.cos(a))
                K.lathe_y(mb, Ff, (0.0, 0.0, 0.0), [(0.03, -0.5), (0.16, -0.18), (0.08, 0.32), (0.14, 0.45)], 4, STEEL)
    for (x, y) in ((-5.6, 3.7), (-4.4, 3.9), (5.2, -3.7), (3.9, -3.9)):                             # cestos e tinas
        K.lathe(mb, F, (x, y, 0.0), [(0.4, 0.0), (0.58, 0.5), (0.62, 0.58)], 7, STRAW)
    K2.barrel2(mb, F, 6.0, 3.6, 0.0, 0.62, 1.0)
    col_box("OP_PortLonja", (W - 2.6, 4.8, 1.3), F.p(0.0, 0.0, 0.65))
    for sx in (-1, 1):
        for sy in (-1, 1):
            col_box("OP_PortLonja", (0.8, 0.8, h), F.p(sx * (W / 2 - 0.4), sy * (D / 2 - 0.4), h / 2))
    Ye = r["Ye"]
    for sy in (-1, 1):                         # as 2 aguas: a beira fica a ~5,5 do cais (alcancavel de cima da bancada)
        za, zb2 = r["Hf"](0.0, sy * Ye), r["Hf"](0.0, 0.0)
        ang = math.atan2(zb2 - za, Ye)
        c = F.p(0.0, sy * Ye / 2, (za + zb2) / 2 - 0.4)
        col_box("OP_PortLonja", (W + 4.6, math.hypot(Ye, zb2 - za), 1.0), c, F.r(-sy * ang, 0.0, 0.0))
    col_box("OP_PortLonja", (W + 5.2, 2.2, 1.8), F.p(0.0, 0.0, r["zr"] + 0.5))         # cumeeira + onigawara


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
    for sy in (-1, 1):                    # V2 (gate): a cobertura se alcanca da muralha da PortoB -> 2 aguas com colisao
        col_box("OP_PortHouse" + nm, (W + 3.0, ln, 0.6), F.p(0.0, sy * Dh / 2, 8.6 + rise / 2 - 0.2),
                F.r(-sy * ang, 0, 0))
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
    tri = lambda: sum(len(f.verts) - 2 for f in mb.bm.faces)
    t0 = tri()
    kura_row(mb)
    t1 = tri()
    r = armazem(mb)
    t2 = tri()
    shed(mb, "H5")
    print("op_harbor: armazens: kura %d, armazem aberto %d, telheiro %d" % (t1 - t0, t2 - t1, tri() - t2))
    return r


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
    """carga do cais V2 (fora das portas, das rotas e do SAFE_Cais): na frente das kura, ao lado do armazem aberto,
    no pier esperando o embarque e os fardos esperando a lingada do guindaste"""
    K2.goods_pile(mb, Frame(125.6, 56.6, H, 0.0), "crates")
    col_box("OP_PortProp", (6.0, 2.0, 1.9), (127.0, 56.6, H + 0.95))
    K2.goods_pile(mb, Frame(206.4, 40.6, H, math.pi / 2), "barrels")
    col_box("OP_PortProp", (2.8, 5.2, 1.6), (206.3, 41.0, H + 0.8))
    cart(mb, Frame(0.0, 0.0, H, 0.0), 208.2, 49.6, -math.pi / 2)
    col_box("OP_PortProp", (7.4, 3.2, 2.7), (209.2, 49.6, H + 1.35))
    # meio do cais: caixas e barris a caminho do armazem (fora da rota e a 8 do SAFE_Cais)
    K2.goods_pile(mb, Frame(203.6, 66.0, H, 0.3), "crates")
    col_box("OP_PortProp", (5.8, 2.6, 1.9), (204.6, 66.3, H + 0.95), (0.0, 0.0, 0.3))
    # pier: carga esperando o embarque (lado oeste, o corredor do meio fica livre)
    for y in (126.0,):
        K2.goods_pile(mb, Frame(224.4, y, H, math.pi / 2), "crates")
        col_box("OP_PortProp", (2.4, 5.4, 1.9), (224.4, y + 1.2, H + 0.95))
    # fardos esperando a lingada (ao sul do tambor do guindaste)
    Fp = Frame(219.8, 73.6, H, 0.0)
    for (y, z) in ((-0.55, 0.0), (0.55, 0.0), (0.0, 0.95)):
        K2.tawara(mb, Fp, 0.0, y, z, 0.0, 0.55, 1.7)
    col_box("OP_PortProp", (2.0, 2.4, 1.9), (219.8, 73.6, H + 0.95))


# ================================================================== GUINDASTE (parte fixa + 2 pecas moveis)
def _jib():
    m = Vector((CRANE_M[0], CRANE_M[1], 0.0))
    t = Vector((LOAD_C[0], LOAD_C[1], 0.0))
    d = (t - m).normalized()
    heel = Vector((m.x + d.x * 0.6, m.y + d.y * 0.6, JIB_HEEL_Z))
    tip = Vector((t.x, t.y, JIB_TIP_Z))
    return d, heel, tip


def load_top_low():
    return LOAD_LOW + 3.2                  # topo do gato da lingada na posicao baixa


def crane(mb, mbs):
    """GUINDASTE de madeira do canto da doca (14 de altura: le da camera do jogo): mastro escorado sobre sapata de
    pedra (mbs), lanca inclinada sobre a doca com escora, estai, moitoes, cavaletes do tambor e o cabo FIXO (tambor ->
    roldana do topo -> ao longo da lanca -> desce da ponta ate o ponto mais alto da lingada)"""
    mx, my = CRANE_M
    d, heel, tip = _jib()
    K.bb(mbs, F0, mx - 1.7, mx + 1.7, my - 1.7, my + 1.7, H - 0.2, H + 0.45, ST)
    K.bb(mbs, F0, mx - 1.55, mx + 1.55, my - 1.55, my + 1.55, H + 0.45, H + 0.57, STP)
    zt = CRANE_TOP
    K.bb(mb, F0, mx - 0.5, mx + 0.5, my - 0.5, my + 0.5, H + 0.57, zt, WD)
    K.lathe(mb, F0, (mx, my, zt), [(0.62, 0.0), (0.66, 0.22), (0.28, 0.62)], 4, WD, math.pi / 4)
    for zz in (H + 3.3, H + 7.0, zt - 1.2):
        K.bb(mb, F0, mx - 0.6, mx + 0.6, my - 0.6, my + 0.6, zz - 0.16, zz + 0.16, IRON)
    for dx, dy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):                        # escoras
        mb.beam(Vector((mx + dx * 1.3, my + dy * 1.3, H + 0.57)), Vector((mx + dx * 0.32, my + dy * 0.32, H + 4.0)),
                0.36, 0.36, WD, 0.0)
    # lanca + escora da lanca + pino de articulacao + estai do topo do mastro ate a ponta
    mb.beam(heel, tip, 0.6, 0.7, WD, 0.0)
    q = heel.lerp(tip, 0.42)
    mb.beam(Vector((mx + d.x * 0.45, my + d.y * 0.45, H + 7.6)), q, 0.34, 0.34, WD, 0.0)
    for k in (0.15, 0.7):
        p = heel.lerp(tip, k)
        K.bb(mb, F0, p.x - 0.42, p.x + 0.42, p.y - 0.42, p.y + 0.42, p.z - 0.12, p.z + 0.12, IRON)
    K.lathe_y(mb, Frame(heel.x, heel.y, 0.0, math.atan2(-d.x, d.y) + math.pi / 2), (0.0, 0.0, heel.z),
              [(0.3, -0.8), (0.3, 0.8)], 6, IRON)
    SH.rope(mb, (mx + d.x * 0.3, my + d.y * 0.3, zt - 0.5), tip + Vector((0, 0, 0.45)), 0.12)
    SH.rope(mb, (mx - d.x * 0.3, my - d.y * 0.3, zt - 0.5), (mx - d.x * 2.6, my - d.y * 2.6, H + 0.5), 0.1)  # contra
    # moitao da ponta e roldana do topo
    K.lathe(mb, F0, (tip.x, tip.y, tip.z - 1.35), [(0.0, 0.0), (0.38, 0.15), (0.4, 0.95), (0.2, 1.1)], 6, WD)
    hb = Vector((mx + d.x * 0.66, my + d.y * 0.66, zt - 0.8))
    K.lathe(mb, F0, (hb.x, hb.y, hb.z - 0.45), [(0.0, 0.0), (0.34, 0.1), (0.34, 0.8), (0.0, 0.9)], 6, WD)
    # cavaletes do tambor (2 cavaletes em A, mancal de ferro) e travessas no chao
    cx, cy, cz = DRUM_C
    for x in (cx - 1.42, cx + 1.42):
        for sy in (-1, 1):
            mb.beam(Vector((x, cy + sy * 1.5, H)), Vector((x, cy + sy * 0.2, cz + 0.3)), 0.3, 0.3, WD, 0.0)
        K.bb(mb, F0, x - 0.17, x + 0.17, cy - 1.75, cy + 1.75, H, H + 0.32, WD)
        K.bb(mb, F0, x - 0.17, x + 0.17, cy - 0.85, cy + 0.85, cz - 1.0, cz - 0.78, WD)
        K.bb(mb, F0, x - 0.22, x + 0.22, cy - 0.34, cy + 0.34, cz - 0.32, cz + 0.45, IRON)
    for y in (cy - 1.55, cy + 1.55):
        K.bb(mb, F0, cx - 1.6, cx + 1.6, y - 0.16, y + 0.16, H, H + 0.28, WD)
    # cabo fixo: do alto do tambor ate a roldana do topo, ao longo da lanca e descendo da ponta
    a0 = Vector((cx, cy + 0.15, cz + DRUM_R + 0.05))
    SH.rope(mb, a0, hb + Vector((0, 0, -0.1)), 0.1)
    SH.rope(mb, hb + Vector((0, 0, 0.35)), tip + Vector((0, 0, -0.25)), 0.1)
    SH.rope(mb, Vector((tip.x, tip.y, tip.z - 1.35)), Vector((tip.x, tip.y, load_top_low() + LOAD_A)), 0.11)
    col_box("OP_PortProp", (3.4, 3.4, 0.6), (mx, my, H + 0.3))
    col_box("OP_PortProp", (2.6, 2.6, 13.4), (mx, my, H + 7.2))
    col_box("OP_PortProp", (4.4, 3.6, 4.7), (cx + 0.3, cy, H + 2.35))


def crane_vfx():
    """VFX_OP_Crane_Drum: tambor + RODA DE MANOBRA (raios e cavilhas) + manivela de 4 barras, girando a 5 rpm no
    eixo x (enrola o cabo: a face de cima anda para longe do mastro). VFX_OP_Crane_Load: lingada subindo em rampa
    lenta e descendo (bob + rate)"""
    cx, cy, cz = DRUM_C
    md = SH.VMB("VFX_OP_Crane_Drum", {}, WM)
    rot = (0.0, math.pi / 2, 0.0)
    md.cyl(DRUM_R, 2.3, (cx, cy, cz), rot, WM, n=10, bevel=0.0)
    for x in (cx - 1.18, cx + 1.18):                                             # flanges
        md.cyl(DRUM_R + 0.34, 0.14, (x, cy, cz), rot, WM, n=10, bevel=0.0)
    for x in (cx - 0.62, cx, cx + 0.62):                                         # voltas de cabo enroladas
        md.cyl(DRUM_R + 0.1, 0.42, (x, cy, cz), rot, ROPE, n=10, bevel=0.0)
    md.cyl(0.17, 4.6, (cx + 0.3, cy, cz), rot, IRON, n=6, bevel=0.0)             # eixo
    xw = cx + 1.95                                                               # RODA (fora do cavalete leste)
    md.cyl(0.42, 0.5, (xw, cy, cz), rot, WD, n=8, bevel=0.0)
    ring = [Vector((xw, cy + WHEEL_R * math.cos(2 * math.pi * k / 16), cz + WHEEL_R * math.sin(2 * math.pi * k / 16)))
            for k in range(17)]
    md.tube(ring, 0.16, WD, n=4)
    for k in range(8):
        a = 2 * math.pi * k / 8 + 0.2
        u = Vector((0.0, math.cos(a), math.sin(a)))
        c = Vector((xw, cy, cz))
        md.beam(c + u * 0.3, c + u * (WHEEL_R - 0.08), 0.16, 0.16, WD, 0.0)
        md.rod(c + u * WHEEL_R, c + u * (WHEEL_R + 0.55), 0.09, WD, 4)           # cavilha (pega)
    xh = cx - 1.85                                                               # manivela de 4 barras (oeste)
    md.cyl(0.3, 0.42, (xh, cy, cz), rot, WD, n=8, bevel=0.0)
    for k in range(2):
        a = k * math.pi / 2 + 0.4
        p = Vector((0.0, math.cos(a), math.sin(a))) * 1.25
        md.beam(Vector((xh, cy, cz)) - p, Vector((xh, cy, cz)) + p, 0.17, 0.17, WD, 0.0)
    obd = SH.finish_mixed(md)
    SH.mover(obd, (cx, cy, cz), (1.0, 0.0, 0.0), rpm=DRUM_RPM, zone="porto", dist=220.0)
    # lingada: 3 fardos em piramide numa rede, gato, e o cabo MOVEL (fino, por dentro do fixo)
    ml = SH.VMB("VFX_OP_Crane_Load", {}, STRAW)
    lx, ly = LOAD_C
    Fl = Frame(lx, ly, LOAD_LOW, 0.0)
    for (y, z) in ((-0.55, 0.0), (0.55, 0.0), (0.0, 0.92)):
        K2.tawara(ml, Fl, 0.0, y, z, 0.0, 0.5, 1.5)
    hook = Vector((lx, ly, LOAD_LOW + 2.75))
    for dx, dy in ((0.85, 1.05), (-0.85, 1.05), (0.85, -1.05), (-0.85, -1.05)):
        ml.tube([hook, Vector((lx + dx, ly + dy, LOAD_LOW + 0.9)), Vector((lx + dx * 0.4, ly + dy * 0.5, LOAD_LOW - 0.05))],
                0.06, ROPE, n=3)
    ml.tube([Vector((lx + 0.86 * math.cos(2 * math.pi * j / 8), ly + 1.08 * math.sin(2 * math.pi * j / 8),
                     LOAD_LOW + 0.85)) for j in range(9)], 0.06, ROPE, n=3)
    K.lathe(ml, F0, (lx, ly, hook.z), [(0.0, 0.0), (0.2, 0.1), (0.22, 0.32), (0.1, 0.45)], 6, IRON)
    mrope_top = load_top_low() + LOAD_A
    ml.rod(Vector((lx, ly, hook.z + 0.4)), Vector((lx, ly, mrope_top - 0.02)), 0.07, ROPE, 4, caps=False)
    obl = SH.finish_mixed(ml)
    SH.mover(obl, (lx, ly, LOAD_LOW + 1.0), (0.0, 0.0, 1.0), bob=LOAD_A, rate=LOAD_RATE, zone="porto", dist=220.0)
    return obd, obl


# ================================================================== BARCOS (casco de estacoes, casca orientada)
def boat2(mb, F, Lb, Bb, kind="sampan"):
    """barco de madeira: F no centro do casco NA LINHA D'AGUA (+y = proa). Casco de 13 estacoes com casca interna
    (borda com espessura), alcatrate, tabuado do fundo, bancos. kind: 'sampan' | 'pesca' | 'yakata'. Devolve dict
    com hb(y), zg(y) e pontos de amarracao (proa/popa, local)"""
    n = 12

    def t_(y):
        return (y + Lb / 2) / Lb

    def hb(y):
        t = t_(y)
        e = abs(2 * t - 1)
        return Bb / 2 * (max(0.05, (1 - e ** 3.2) ** 0.5) if t > 0.5 else max(0.62, (1 - e ** 3.2) ** 0.5))

    def zg(y):
        t = t_(y)
        return 1.5 + 0.9 * max(0.0, 2 * t - 1) ** 2 + 0.35 * max(0.0, 1 - 2 * t) ** 2

    def ring(y):
        t = t_(y)
        h, g = hb(y), zg(y)
        kz = -0.7 + (g - 0.4 + 0.7) * max(0.0, (t - 0.8) / 0.2) ** 1.6
        hi = max(0.03, h - 0.16)
        zin = min(0.3, g - 0.3)
        side = [(hi, zin, "in"), (hi, g, "top"), (h, g, "out"), (h * 0.97, g - 0.55, "out"), (h * 0.78, -0.1, "out")]
        port = [(-u, z, k) for u, z, k in side]
        stb = [(h * 0.78, -0.1, "out"), (h * 0.97, g - 0.55, "out"), (h, g, "top"), (hi, g, "in"), (hi, zin, "in")]
        return port + [(0.0, kz, "out")] + stb
    ys = [-Lb / 2 + Lb * i / n for i in range(n + 1)]
    SH.shell_hull(mb, F, ys, ring, lambda j, nn, zc, kd: (WM if kd == "in" else (WD if kd == "top" or zc < 0.1 else HULL)),
                  0.4)
    # fundo (tabuado), bancos, alcatrate
    pts = [(hb(y) - 0.2, y) for y in ys[1:-1]] + [(-(hb(y) - 0.2), y) for y in reversed(ys[1:-1])]
    poly = [tuple(F.p(x, y, 0))[:2] for x, y in pts]
    mb.prism(DL.ccw(poly), F.o.z + 0.05, F.o.z + 0.32, WM)
    for t in ((0.3, 0.55, 0.8) if kind != "yakata" else (0.18, 0.86)):
        y = -Lb / 2 + Lb * t
        K.bb(mb, F, -hb(y) + 0.12, hb(y) - 0.12, y - 0.42, y + 0.42, zg(y) - 0.55, zg(y) - 0.3, WM)
    for s in (-1, 1):
        mb.tube([F.p(s * (hb(y) - 0.05), y, zg(y) + 0.08) for y in ys], 0.12, WD, n=4)
    bow = (0.0, Lb / 2 - 0.4, zg(Lb / 2 - 0.4) + 0.1)
    stern = (0.0, -Lb / 2 + 0.3, zg(-Lb / 2 + 0.3) + 0.1)
    if kind == "sampan":                                 # ro (remo de popa) apoiado e 2 remos nos bancos
        K.beam(mb, F, (0.25, -Lb / 2 + 0.4, zg(-Lb / 2) + 0.7), (0.5, -Lb / 2 - 2.8, 0.3), 0.18, 0.12, WD)
        for s in (-1, 1):
            K.beam(mb, F, (s * 0.55, -Lb * 0.3, zg(0) - 0.1), (s * 0.8, Lb * 0.3, zg(0) - 0.08), 0.12, 0.08, WM)
    elif kind == "yakata":                               # esteios, cobertura de 2 aguas, cumeeira, noren de bambu
        y0, y1 = -Lb * 0.22, Lb * 0.24
        h_ = Bb / 2 - 0.35
        zg0 = zg(0.0)
        zt = zg0 + 3.6
        for sx in (-1, 1):
            for yy in (y0, y1):
                K.bb(mb, F, sx * h_ - 0.15, sx * h_ + 0.15, yy - 0.15, yy + 0.15, zg0 - 0.3, zt, WD)
            K.bb(mb, F, sx * h_ - 0.12, sx * h_ + 0.12, y0, y1, zt - 0.3, zt, WD)
        a = math.atan2(1.0, h_ + 0.6)
        for sx in (-1, 1):
            c = F.p(sx * (h_ + 0.6) / 2, (y0 + y1) / 2, zt + 0.55)
            mb.box((math.hypot(h_ + 0.6, 1.0) + 0.2, y1 - y0 + 1.6, 0.22), c, F.r(0.0, sx * a, 0.0), "Roof_OP_Blue", 0.0)
        K.bb(mb, F, -0.3, 0.3, y0 - 0.85, y1 + 0.85, zt + 1.0, zt + 1.35, "Roof_OP_Ridge")
        K.bb(mb, F, -h_, h_, y0 - 0.1, y1 + 0.1, zg0 - 0.35, zg0 - 0.1, WM)
        for yy in (y0 + 0.4, y1 - 0.4):
            K.bb(mb, F, -h_ + 0.2, h_ - 0.2, yy - 0.06, yy + 0.06, zt - 1.6, zt - 0.35, "Cloth_OP_Indigo")
            K.bb(mb, F, -h_ - 0.1, h_ + 0.1, yy - 0.14, yy + 0.14, zt - 0.35, zt - 0.08, WD)
        K.beam(mb, F, (0.2, -Lb / 2 + 0.3, zg0 + 0.9), (0.4, -Lb / 2 - 3.6, 0.2), 0.18, 0.12, WD)
    return dict(hb=hb, zg=zg, bow=bow, stern=stern)


def _moor(mb, F, local, world, sag=0.6):
    SH.rope_sag(mb, F.p(*local), Vector(world), sag, 0.09, 6)


def quay_bollards(mb):
    """cabecos da borda do cais norte (amarras do yakatabune e do bote; ficam dentro da guarda do op_col)"""
    for y in (206.0, 222.0, 242.0):
        bollard(mb, 220.6, y, col=True)


def argola_pt(y):
    return (221.15 - 0.42, y, H + 0.12)


def boats_vfx():
    out = []
    # VFX_OP_Boat_1: 2 sampans de contrabordo na doca, presos as argolas; o de dentro recebe a lingada
    mb = SH.VMB("VFX_OP_Boat_1", BOAT_KEEP, WD)
    infos = []
    for i, (x, y, Lb, Bb) in enumerate(SAMPANS):
        F = Frame(x, y, SEA, 0.0)
        infos.append((F, boat2(mb, F, Lb, Bb, "sampan"), Lb, Bb))
    (FA, A, LA, BA), (FB, B, LB, BB) = infos
    _moor(mb, FA, (-A["hb"](LA / 2 - 2.2) + 0.05, LA / 2 - 2.2, A["zg"](LA / 2 - 2.2) + 0.1), argola_pt(ARGOLAS[1]), 0.5)
    _moor(mb, FA, (-A["hb"](-LA / 2 + 1.6) + 0.05, -LA / 2 + 1.6, A["zg"](-LA / 2 + 1.6) + 0.1), argola_pt(ARGOLAS[0]),
          0.5)
    for yy in (-2.5, 2.5):                                           # amarras de contrabordo
        a = FA.p(A["hb"](yy) - 0.05, yy, A["zg"](yy) + 0.12)
        b = FB.p(-B["hb"](yy + FA.o.y - FB.o.y) + 0.05, yy + FA.o.y - FB.o.y, B["zg"](yy + FA.o.y - FB.o.y) + 0.12)
        SH.rope_sag(mb, a, b, 0.25, 0.08, 4)
    for s in (-1, 1):                                                # defensas de palha entre os 2 cascos
        K.lathe(mb, F0, (FA.o.x + (FB.o.x - FA.o.x) / 2, FA.o.y + s * 2.0, SEA + 0.6),
                [(0.25, 0.0), (0.38, 0.2), (0.38, 0.9), (0.25, 1.1)], 6, ROPE)
    # o de dentro ja tem 2 fardos na proa; o de fora carrega caixas e uma pilha sob esteira
    K2.tawara(mb, K.sub(FA, 0.0, LA / 2 - 3.2, 0.32), -0.3, 0.0, 0.0, math.pi / 2, 0.5, 1.5)
    K2.tawara(mb, K.sub(FA, 0.0, LA / 2 - 3.2, 0.32), 0.45, 0.6, 0.0, math.pi / 2 + 0.2, 0.5, 1.5)
    K.crate(mb, FB, 0.0, 1.0, 0.32, 1.6, 1.3, 1.0, 0.1)
    K.crate(mb, FB, 0.1, 1.0, 1.32, 1.3, 1.1, 0.8, -0.15)
    K.lathe_y(mb, K.sub(FB, 0.0, -2.0, 0.32 + 0.55, math.pi / 2), (0.0, 0.0, 0.0),
              [(0.3, -1.1), (0.75, -0.9), (0.8, 0.0), (0.75, 0.9), (0.3, 1.1)], 6, STRAW)
    ob = SH.finish_mixed(mb)
    out.append(SH.mover(ob, (FA.o.x, FA.o.y, SEA), bob=BOAT_BOB["VFX_OP_Boat_1"]))
    # VFX_OP_Boat_2: barco de pesca no lado SUL da palafita (rede amontoada, cestos, farol de pesca, toldo de esteira)
    # + bote de contrabordo por fora (mesma peca: amarrados juntos sobem e descem juntos)
    mb = SH.VMB("VFX_OP_Boat_2", BOAT_KEEP, WD)
    x, y, Lb, Bb = FISHER
    F = Frame(x, y, SEA, -math.pi / 2)
    P = boat2(mb, F, Lb, Bb, "pesca")
    for (dx, dy, r, hh) in ((0.0, 0.6, 1.1, 0.55), (0.35, 1.6, 0.8, 0.45), (-0.3, -0.4, 0.85, 0.4)):   # rede
        K.lathe(mb, F, (dx, dy, 0.32), [(r, 0.0), (r * 0.9, hh * 0.6), (r * 0.5, hh), (0.0, hh * 1.1)], 7, ROPE)
    for (dx, dy) in ((-0.75, 3.0), (0.7, 3.4)):                                                       # cestos
        K.lathe(mb, F, (dx, dy, 0.32), [(0.32, 0.0), (0.45, 0.5), (0.48, 0.58)], 6, STRAW)
    yb = Lb / 2 - 1.5                                                                                 # isaribi
    K.bb(mb, F, -0.1, 0.1, yb - 0.1, yb + 0.1, 0.32, P["zg"](yb) + 3.2, WD)
    K.beam(mb, F, (0.0, yb, P["zg"](yb) + 3.0), (0.0, yb + 1.4, P["zg"](yb) + 3.4), 0.12, 0.12, WD)
    K.lathe(mb, F, (0.0, yb + 1.4, P["zg"](yb) + 2.75), [(0.12, 0.0), (0.42, 0.45), (0.5, 0.7)], 6, IRON,
            caps=(True, False))
    ya, yz = -Lb / 2 + 0.6, -Lb / 2 + 3.4                                                             # toldo
    arc = [(math.cos(math.pi * k / 5) * (Bb / 2 - 0.25), math.sin(math.pi * k / 5) * 1.6) for k in range(6)]
    for yy in (ya, yz):
        mb.tube([F.p(u, yy, P["zg"](yy) + v) for u, v in arc], 0.07, WD, n=3)
    G = [[F.p(u, yy, P["zg"](yy) + v + 0.05) for yy in (ya, yz)] for u, v in arc]
    cen = F.p(0.0, (ya + yz) / 2, P["zg"](ya))
    for i in range(5):
        for side, off in ((1, 0.0), (-1, -0.12)):
            q = [G[i][0], G[i][1], G[i + 1][1], G[i + 1][0]]
            vs = [mb.bm.verts.new(p + Vector((0, 0, off))) for p in q]
            f = mb.bm.faces.new(vs)
            f.normal_update()
            if f.normal.dot(((q[0] + q[2]) / 2 - cen) * side) < 0:
                f.normal_flip()
            mb.shell.add(f)
            mb._post(vs, STRAW, None, 0, 1)
    for yy, xw in ((Lb / 2 - 2.4, x + Lb / 2 - 3.0), (-Lb / 2 + 1.8, x - Lb / 2 + 2.6)):            # amarras
        _moor(mb, F, (-P["hb"](yy) + 0.05, yy, P["zg"](yy) + 0.1), (xw, 40.3, H + 1.0), 0.7)
    x2, y2, L2, B2 = ROWBOAT
    F2 = Frame(x2, y2, SEA, -math.pi / 2)
    R2 = boat2(mb, F2, L2, B2, "sampan")
    for yy in (-2.0, 2.0):
        SH.rope_sag(mb, F2.p(-R2["hb"](yy) + 0.05, yy, R2["zg"](yy) + 0.1),
                    F.p(P["hb"](yy + (x2 - x)) - 0.05, yy + (x2 - x), P["zg"](yy) + 0.1), 0.25, 0.08, 4)
    ob = SH.finish_mixed(mb)
    out.append(SH.mover(ob, (x, y, SEA), bob=BOAT_BOB["VFX_OP_Boat_2"]))
    # VFX_OP_Boat_3: yakatabune no cais norte, amarrado aos cabecos, e um bote preso a um cabeco mais ao norte
    mb = SH.VMB("VFX_OP_Boat_3", BOAT_KEEP, WD)
    x, y, Lb, Bb = YAKATA
    F = Frame(x, y, SEA, 0.0)
    P = boat2(mb, F, Lb, Bb, "yakata")
    _moor(mb, F, P["bow"], (220.6, 222.0, H + 1.1), 0.9)
    _moor(mb, F, P["stern"], (220.6, 206.0, H + 1.1), 0.9)
    x3, y3, L3, B3 = SKIFF
    F3 = Frame(x3, y3, SEA, 0.0)
    R3 = boat2(mb, F3, L3, B3, "sampan")
    _moor(mb, F3, R3["bow"], (220.6, 242.0, H + 1.1), 0.8)
    ob = SH.finish_mixed(mb)
    out.append(SH.mover(ob, (x, y, SEA), bob=BOAT_BOB["VFX_OP_Boat_3"]))
    return out


def hauled_boat(mb):
    """BARCO EM REPARO: sampan puxado para o cais em 3 cavaletes com calcos, tabuas novas encostadas, panela de
    piche e malho (static: tem colisao)"""
    x, y = HAULED
    zw = H + 1.95                                          # 'linha d'agua' do casco erguido (quilha a H + 1,25)
    F = Frame(x, y, zw, -math.pi / 2)                      # proa para +x
    P = boat2(mb, F, 11.0, 3.4, "sampan")
    for yy in (-3.4, 0.0, 3.2):
        for s in (-1, 1):
            K.bb(mb, F, s * 1.35 - 0.14, s * 1.35 + 0.14, yy - 0.14, yy + 0.14, -1.95, -0.7, WD)
        K.bb(mb, F, -1.7, 1.7, yy - 0.22, yy + 0.22, -0.95, -0.7, WD)
        for s in (-1, 1):
            K.bb(mb, F, s * 0.9 - 0.18, s * 0.9 + 0.18, yy - 0.2, yy + 0.2, -0.7, -0.32, WM)
    for k in range(3):                                     # tabuas novas encostadas no cavalete
        K.beam(mb, F, (2.6 + 0.3 * k, -2.0 + 0.5 * k, -1.95), (2.0 + 0.3 * k, 1.8 + 0.5 * k, -0.5), 0.5, 0.1, WM)
    K.jar(mb, F, -2.4, -4.6, -1.95, 0.45, 0.8, STD)
    K.beam(mb, F, (-2.0, -3.4, -1.85), (-1.2, -3.0, -1.85), 0.12, 0.12, WD)
    K.bb(mb, F, -1.35, -1.0, -3.25, -2.75, -1.95, -1.5, WD)
    col_box("OP_PortProp", (12.0, 6.6, 2.9), (x, y - 0.25, H + 1.45))      # casco + tabuas encostadas + panela


# ================================================================== REDES SECANDO, CESTOS, ESCADA DA DOCA
def nets(mb):
    """2 varais de rede junto a muralha: esteios sobre pedra, vara, a rede jogada por cima da vara (malha de cabo:
    cordas verticais com barriga + 3 fiadas) com boias de cortica na barra"""
    for xa, xb in NET_RACKS:
        for x in (xa, xb):
            K.rock_base(mb, F0, x, NET_Y, H, 0.55, 0.35)
            K.bb(mb, F0, x - 0.18, x + 0.18, NET_Y - 0.18, NET_Y + 0.18, H + 0.2, H + 6.4, WD)
            mb.beam(Vector((x, NET_Y - 0.1, H + 4.6)), Vector((x, NET_Y + 1.6, H + 0.3)), 0.14, 0.14, WD, 0.0)
        mb.rod(Vector((xa - 0.4, NET_Y, H + 6.25)), Vector((xb + 0.4, NET_Y, H + 6.25)), 0.14, WD, 6)
        for s in (-1, 1):
            xs = [xa + 0.45 + (xb - xa - 0.9) * i / 8 for i in range(9)]

            def P(x, v, s=s, xa=xa, xb=xb):
                drop = 4.9 + 0.5 * math.sin(1.7 * x) + (0.3 if s < 0 else 0.0)
                bul = 0.55 * math.sin(math.pi * v) * (0.8 + 0.3 * math.sin(0.9 * x))
                return Vector((x, NET_Y + s * (0.12 + 0.35 * v + bul), H + 6.15 - v * drop))
            for x in xs:
                mb.tube([P(x, v) for v in (0.0, 0.33, 0.66, 1.0)], 0.05, ROPE, n=3)
            for v in (0.33, 0.66, 1.0):
                mb.tube([P(xx, v) for xx in [xa + 0.45 + (xb - xa - 0.9) * i / 5 for i in range(6)]], 0.05, ROPE, n=3)
            for x in xs[::2]:
                p = P(x, 1.0)
                K.bb(mb, F0, p.x - 0.22, p.x + 0.22, p.y - 0.14, p.y + 0.14, p.z - 0.12, p.z + 0.12, WM)
        col_box("OP_PortProp", (xb - xa + 1.0, 2.8, 6.4), ((xa + xb) / 2, NET_Y, H + 3.2))


def baskets(mb):
    """cestos de peixe junto a doca (entre as argolas): palha, boca cheia de peixe (fuso escuro)"""
    for i, (x, y) in enumerate(((219.5, 89.9), (219.7, 91.5), (219.2, 98.0), (219.9, 99.4))):
        F = Frame(x, y, H, 0.6 * i)
        K.lathe(mb, F, (0.0, 0.0, 0.0), [(0.42, 0.0), (0.62, 0.55), (0.66, 0.62)], 8, STRAW)
        for k in range(3):
            a = 2.1 * k + i
            Ff = K.sub(F, 0.18 * math.cos(a), 0.18 * math.sin(a), 0.7, a + 0.8)
            K.lathe_y(mb, Ff, (0.0, 0.0, 0.0), [(0.02, -0.45), (0.13, -0.22), (0.15, 0.06), (0.06, 0.3), (0.12, 0.42)],
                      4, STEEL)
    col_box("OP_PortProp", (1.8, 3.0, 0.9), (219.6, 90.7, H + 0.45))
    col_box("OP_PortProp", (1.8, 2.8, 0.9), (219.6, 98.7, H + 0.45))


def ladder(mb, y=101.6):
    """escada de marinheiro na muralha da doca (do cais ate a agua), longarinas com a ponta curvada sobre a borda"""
    for yy in (y - 0.55, y + 0.55):
        mb.beam(Vector((222.42, yy, SEA - 0.8)), Vector((222.42, yy, H - 0.05)), 0.2, 0.22, WD, 0.0)
        mb.beam(Vector((222.42, yy, H - 0.05)), Vector((221.7, yy, H + 0.95)), 0.2, 0.22, WD, 0.0)
    z = SEA - 0.4
    while z < H - 0.3:
        mb.rod(Vector((222.42, y - 0.5, z)), Vector((222.42, y + 0.5, z)), 0.07, WD, 4)
        z += 0.85


# ================================================================== AMARRAS DO NAVIO, argolas e postes
def ship_lines(mb):
    pts = {y: Vector((PIER_A[2] - 1.4, y, H + 1.1)) for y in BOLLARDS_A}
    for ys, yb in ((116.0, 116.0), (190.0, 194.0), (136.0, 130.0), (172.0, 178.0)):
        z = SH.zb(ys, -1)
        a = Vector((SH.SX - SH.wid(ys, z) - 0.1, ys, z + 0.25))
        SH.rope_sag(mb, a, pts[yb], 1.3, 0.13, 8)



ARGOLAS = [86.0, 94.0, 102.0]       # argolas de amarracao na beira da doca (x 222): os sampans amarram nas 2 primeiras
#                                     (V2: a de y 80 saiu - la fica a sapata do guindaste)


def argolas(mb):
    """argola de ferro deitada no lajeado, presa numa chapa com olhal, junto a beira d'agua da doca (x 222)"""
    for y in ARGOLAS:
        x = 221.15
        mb.box((0.9, 0.7, 0.1), (x, y, H + 0.05), (0, 0, 0), IRON, 0.0)                     # chapa
        mb.box((0.26, 0.3, 0.34), (x + 0.12, y, H + 0.27), (0, 0, 0), IRON, 0.0)            # olhal
        c = Vector((x - 0.42, y, H + 0.1))
        ring = [c + Vector((0.5 * math.cos(2 * math.pi * k / 7), 0.42 * math.sin(2 * math.pi * k / 7), 0.0))
                for k in range(8)]
        mb.tube(ring, 0.07, IRON, n=3)


LAMPS = [(224.0, 113.6, 0.0), (223.7, 72.4, 0.0)]


def lamps(mb):
    """postes do kit V2 (poste de madeira com chochin sob telhadinho) na raiz do pier e na palafita"""
    for i, (x, y, a) in enumerate(LAMPS):
        K2.lamp_post(mb, Frame(x, y, H, a), "L_OPProp_Lamp_Porto_%d" % i, 35.0)
        col_box("OP_PortProp", (3.4, 1.6, 8.2), (x + 0.9, y, H + 4.1))          # poste + braco do chochin


# ================================================================== cameras de revisao
EYE = L.EYE
CAMS = {
    "CAM_OPPort_PH_DescidaA": ((174.0, 140.0, L.T1 - 15.6 * 0.767 + EYE), (232.0, 152.0, 52.0), 22),
    "CAM_OPPort_PH_DescidaB": ((160.0, 82.0, H + 20.0 * 0.767 + EYE), (234.0, 56.0, 46.0), 22),
    "CAM_OPPort_PH_Cais": ((168.0, 50.0, H + EYE), (214.0, 92.0, H + 6.0), 20),
    "CAM_OPPort_PH_Lonja": ((176.0, 64.0, H + EYE), (180.0, 80.0, H + 2.5), 22),
    "CAM_OPPort_PH_Doca": ((214.0, 60.0, H + EYE), (228.0, 96.0, H + 3.0), 20),
    "CAM_OPPort_PH_Pier": ((228.0, 114.0, H + EYE), (272.0, 92.0, H + 6.0), 20),
    "CAM_OPPort_PH_Palafita": ((226.0, 44.0, H + EYE), (262.0, 70.0, H + 3.0), 20),
    "CAM_OPPort_PH_Armazem": ((190.0, 60.0, H + EYE), (192.0, 40.0, H + 4.0), 22),
    "CAM_OPPort_Armazem_Int": ((186.0, 47.0, H + 0.9 + EYE), (198.0, 37.0, H + 2.5), 20),
    "CAM_OPPort_Guindaste": ((204.0, 70.0, H + 9.0), (226.0, 86.0, H + 5.0), 22),
    "CAM_OPPort_Doca": ((244.0, 78.0, H + 7.0), (229.0, 93.0, SEA + 1.0), 22),
    "CAM_OPPort_Junco": ((236.0, -14.0, H + 6.0), (272.0, 27.0, SEA + 10.0), 22),
    "CAM_OPPort_Redes": ((190.0, 86.0, H + EYE), (178.0, 98.0, H + 3.5), 22),
    "CAM_OPPort_Barcos": ((250.0, 226.0, 49.0), (229.0, 210.0, SEA + 1.5), 26),
    "CAM_OPPort_Escadas": ((112.0, 12.0, 96.0), (176.0, 100.0, 58.0), 24),
    "CAM_OPPort_Jogo": ((110.0, -10.0, 125.0), (205.0, 95.0, 45.0), 20),
    "CAM_OPPort_Pesca": ((218.0, 14.0, H + 3.0), (234.0, 30.0, SEA + 1.5), 24),
    "CAM_OPPort_PH_Lingada": ((227.5, 124.0, H + EYE), (237.0, 135.0, 52.0), 22),
    "CAM_OPPort_ArmazemFora": ((210.0, 62.0, H + 9.0), (192.0, 42.0, H + 4.0), 22),
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
    # madeira: pier, palafita, guindaste, redes, barco em reparo (casca orientada: SH.finish_mixed)
    mp = SH.MapMB("OP_Port_Piers", COLL, rnd, REMAP_PIERS, detail="far", floor=None)
    mbd = SH.MapMB("OP_Port_Built", COLL, random.Random(8202), REMAP_BUILT, detail="far", floor=None)   # pedra/reboco
    _WMB[0] = MB("OP_Port_Muralha", COLL, random.Random(8203), detail="far", floor=None)  # M6b: muralha das escadas
    parts = []

    def tri(m):
        return sum(len(f.verts) - 2 for f in m.bm.faces)
    tot = lambda: tri(mp) + tri(mbd) + tri(_WMB[0])
    for nm, fn in (("pier_a", lambda: pier_a(mp)), ("palafita", lambda: palafita(mp)),
                   ("ship_lines", lambda: ship_lines(mp)), ("argolas", lambda: argolas(mbd)),
                   ("lamps", lambda: lamps(mbd)), ("stairs", lambda: stairs(mbd)),
                   ("warehouses", lambda: warehouses(mbd)), ("cargo", lambda: cargo(mbd)),
                   ("crane", lambda: crane(mp, mbd)), ("hauled_boat", lambda: hauled_boat(mp)),
                   ("nets", lambda: nets(mp)), ("baskets", lambda: baskets(mp)), ("ladder", lambda: ladder(mp)),
                   ("lonja", lambda: lonja(mbd)), ("quay_bollards", lambda: quay_bollards(mp))):
        t0 = tot()
        fn()
        parts.append("%s %d" % (nm, tot() - t0))
    print("op_harbor: tris por parte: " + ", ".join(parts))
    o1 = SH.finish_mixed(mp)
    o2 = mbd.finish()
    o3 = _WMB[0].finish(recalc=False)      # orientacao das faces calculada uma a uma (_q4): sem recalc
    _WMB[0] = None
    mv = boats_vfx() + list(crane_vfx())
    cams()
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in (o1, o2, o3) if o)
    print("op_harbor: %d tris (pier/madeira %d mat, construido %d mat, muralha %d mat); OP_Ter_Piers removido=%s" % (
        tris, len(o1.data.materials), len(o2.data.materials), len(o3.data.materials), removed))
    for o in mv:
        print("op_harbor: %-20s %5d tris %d mat  bob %.2f rate %.2f rpm %.1f eixo %s pivo (%.1f, %.1f, %.1f)" % (
            o.name, sum(len(p.vertices) - 2 for p in o.data.polygons), len(o.data.materials), o["bob"], o["rate"],
            o["rpm"], tuple(round(v, 2) for v in o["axis"]), *o["pivot"]))
