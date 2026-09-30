# sg_entry - ENTRADA da Ilha 3 (Shadow Garden), 3a na hierarquia: a primeira impressao de quem chega da Ilha 2.
# Substitui sg_blockout.entry. Sul da ilha, eixo x = 0:
#   ponte de chegada gotica (tabuleiro de lajes frias, parapeito baixo com cornija e cachorros, 2 pilares com talha-mar
#   descendo em ponta para as nuvens e um arco ogival entre eles) -> patio baixo (DECK) com o PORTICO A -> escadaria
#   (sg_lib.plan_stair "Entry", sem banzo: as muretas inclinadas fazem o papel) -> calcada alta (P1) com o PORTICO B.
# Portico = par de pilares escuros com coroa de gabletes + agulha navy + remate de prata, ESTANDARTE navy com emblema de
# prata na face sul (sinalizacao da entrada) e lanterna baixa quente ao pe (4 luzes no total). Vao livre >= 18 no eixo.
# Colisao PROPRIA so dos pilares (fora do caminho de 18). Piso, escada, ponte e guardas: sg_col (congelado).
import math, random
from mathutils import Vector
import sg_lib as SL
import fm_parts as FP
from sg_lib import MB, col_box2, light, Frame, fm_lib
import sg_layout as L
import sg_emblem as EM
# REFINAMENTO 2026-09-28: o estandarte navy com o "tridente" virou o estandarte DA ORDEM (sg_emblem.banner) e o portico
# B ganhou a verga de obsidiana com o medalhao da ordem (sg_emblem.plaque): a entrada fala pelo mesmo simbolo do castelo.
# REFINAMENTO v2 2026-09-28: CHEGADA CERIMONIAL da referencia v2 (ref2_entry): RITMO de lanternas douradas
# (sg_emblem.lantern_pedestal, SO Neon - as 4 luzes reais continuam as das lanternas dos porticos) sobre os parapeitos
# da ponte (3 pares), da lateral do patio (2 pares) e da calcada alta (2 pares); estandartes dos porticos com debrum
# DOURADO (trim="Metal_Gold").
# REFINAMENTO v3 2026-09-29 (ref2_main / ref2_entry: o corredor cerimonial mais forte do mapa):
#   - pedra da escadaria, das muretas inclinadas e dos parapeitos UM VALOR MAIS ESCURA (Stone_SG_Castle); a cantaria clara
#     (Stone_SG_Trim) fica SO no remate (capa); cintas das muretas em obsidiana; meio-fio da ponte em obsidiana (moldura
#     escura do calcamento, como o caminho da ordem);
#   - ritmo de pares de lanternas douradas a ~5,6 na ponte (pilaretes dos pilares e da cabeceira com lanterna no lugar do
#     pinaculo + pedestais entre eles), PILARETES COM LANTERNA na mureta da escadaria (pe, meio do lance e topo, em pares)
#     e no fim da calcada alta; SO Neon (as 4 luzes reais continuam as dos porticos);
#   - par de ESTANDARTES da ordem com debrum dourado em mastros sobre o parapeito no meio da ponte (encaram quem chega):
#     o ritmo estandarte (ponte) -> portico A -> portico B da referencia.

# ACABAMENTO 2026-09-29: o par de estandartes em mastro no meio da ponte SAIU (o sinal da ordem fica nos 2 porticos);
# um pedestal de lanterna ocupa o lugar do mastro (o ritmo de ~5,6 fecha); os 2 pares de pilaretes-lanterna do meio do
# lance da escadaria SAIRAM (cerca de luz que escondia a escada: fica o par do pe e o do topo); pedestais de lanterna
# dos parapeitos na escala 0,8 (a base cabe na capa, nada sobrando no ar).
# OVERHAUL 01 "zero tolerancia" (2026-09-29): lanternas SO nos NOS (comeco e fim da ponte, porticos, topo da escada:
# de 28 para 10); parapeito de cantaria com arcada cega, plinto, pingadeira e capa segmentada; pilarete com base
# moldurada, fuste chanfrado, capitel em 2 degraus e remate do kit (bola com colar); banzo da escadaria em fiadas de
# cantaria com juntas desencontradas, rodape e capa inclinada em pecas; degraus de pedra (sg_lib.plan_stair); fustes dos
# porticos com quinas chanfradas, colunelos e fiadas no terco de baixo, janelas cegas com vazio + moldura com espessura,
# gabletes com cimalha e florao, pinaculos do kit; verga B com perfil e fecho esculpido (sem placa); estandarte so no
# portico B; lanterna baixa em balaustre com a lanterna do kit; aduelas radiais no arco da ponte.
# OVERHAUL 12 (2026-09-29, props globais): de 10 para 6 lanternas - a da cabeceira da ponte e a do topo da escada
# sairam (cada uma a ~9 studs da lanterna baixa acesa do portico A/B: o no fica com UMA lanterna por lado); agulha dos
# porticos octogonal com anel e florao de prata (sem piramide de 4 lados); estandarte do portico B na largura estreita.

DECK, P1 = L.DECK, L.P1
Y0, Y1 = L.BRIDGE_Y0, L.BRIDGE_Y1          # -262 .. -228
HW = L.DECK_W / 2.0                        # 9: face interna dos parapeitos / guardas
PAR_Z = DECK - 0.35                        # base dos parapeitos (assentados no corpo do tabuleiro)
PAR_H = 2.0                                # parede do parapeito (+ capa 0,45)
WARM = (1.0, 0.64, 0.34)
# OVERHAUL 01 (2026-09-29): cantaria de REMATE perto do jogador um valor abaixo do Stone_SG_Trim (164 lia plastico
# branco no Roblox; auditoria 14.01): capas, capiteis, molduras e remates. O Stone_SG_Trim fica so no que e alto/longe.
CAP_M = "Stone_SG_TrimLow"
fm_lib.MATS.setdefault(CAP_M, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))

# (x do eixo do pilar, secao do fuste, altura do fuste, agulha, largura e altura do estandarte)
PORTICO_A = dict(y=L.PORTICO_A_Y, z=DECK, xc=11.3, s=3.2, H=16.0, spire=7.0, bw=2.6, bh=9.0, name="A")
PORTICO_B = dict(y=L.PORTICO_B_Y, z=P1, xc=11.6, s=4.0, H=22.0, spire=10.0, bw=2.6, bh=12.0, name="B")   # ov12: estreito

CAMS = {
    # frente: chegando da Ilha 2 pela ponte (um pouco acima, de lado)
    "CAM_SGEnt_Front": ((16.0, -322.0, DECK + 16.0), (0.0, -214.0, DECK + 12.0), 24),
    # altura do jogador na ponta da ponte olhando a subida
    "CAM_SGEnt_PlayerBridge": ((0.0, -259.0, DECK + 5.2), (0.0, -176.0, P1 + 12.0), 22),
    # altura do jogador no topo da escada: o portico B emoldura a praca e o castelo
    "CAM_SGEnt_PlayerStairTop": ((0.0, -187.0, P1 + 5.2), (0.0, -40.0, P1 + 34.0), 22),
    # tras: da praca olhando de volta para o sul (costas dos porticos, saida para a Ilha 2)
    "CAM_SGEnt_Back": ((6.0, -150.0, P1 + 8.0), (0.0, -236.0, DECK + 6.0), 22),
    # lados: ponte (arco e pilares) e o conjunto patio/escada/calcada
    "CAM_SGEnt_SideW": ((-74.0, -236.0, DECK + 20.0), (0.0, -220.0, DECK + 6.0), 24),
    "CAM_SGEnt_SideE_Low": ((96.0, -300.0, DECK - 14.0), (0.0, -244.0, DECK - 22.0), 24),
    # overhaul 01 (2026-09-29): closes na altura do jogador - escada, banzo, parapeito, lanterna, praca, fonte,
    # estatua da fonte, banco e poste (as guardas do patio usam CAM_SG_AU_GuardFront/Side do sg_scene)
    "CAM_SGEnt_OV_Stair": ((-5.0, -215.0, DECK + 5.2), (3.0, -196.0, DECK + 4.0), 22),
    "CAM_SGEnt_OV_Banzo": ((-3.5, -199.0, DECK + 8.8), (9.8, -190.0, P1 + 1.2), 24),
    "CAM_SGEnt_OV_Parapet": ((-3.0, -251.0, DECK + 5.2), (9.6, -240.0, DECK + 2.0), 24),
    "CAM_SGEnt_OV_Lantern": ((5.2, -233.6, DECK + 5.4), (9.6, -228.6, DECK + 4.6), 35),
    "CAM_SGEnt_OV_Plaza": ((-14.0, -151.0, P1 + 5.2), (0.0, -128.0, P1 + 0.5), 22),
    "CAM_SGEnt_OV_Fountain": ((9.0, -142.0, P1 + 5.2), (0.0, -128.0, P1 + 5.0), 26),
    "CAM_SGEnt_OV_Statue": ((4.0, -141.0, P1 + 5.2), (0.0, -128.0, P1 + 11.8), 40),
    "CAM_SGEnt_OV_Bench": ((-4.5, -143.0, P1 + 4.2), (-10.9, -148.5, P1 + 1.0), 28),
    "CAM_SGEnt_OV_PlazaLamp": ((-10.0, -150.5, P1 + 5.2), (-16.7, -144.7, P1 + 5.4), 24),
    "CAM_SGEnt_OV_GuardFront": ((-9.4, 22.0, L.P3 + 4.8), (-12.5, 33.5, L.P3 + 7.6), 24),
    "CAM_SGEnt_OV_GuardSide": ((-2.6, 36.8, L.P3 + 5.2), (-12.5, 33.5, L.P3 + 7.6), 24),
    # inspecao (fora da altura do jogador): a figura da fonte e a guarda de perto
    "CAM_SGEnt_OV_StatueHi": ((3.0, -137.5, P1 + 13.0), (0.0, -128.0, P1 + 12.2), 35),
    "CAM_SGEnt_OV_GuardHi": ((-10.3, 27.0, L.P3 + 9.0), (-12.5, 33.5, L.P3 + 8.2), 30),
}

# rota extra: o jogador contorna o pilar do portico A por dentro do vao (o caminho de 18 fica livre)
EXTRA_ROUTES = {
    "PATIO_PORTICO_A_LATERAL": ([(0.0, -226.0), (-7.8, -222.0), (-7.8, -210.0), (0.0, -207.5)], DECK),
    "CALCADA_PORTICO_B_LATERAL": ([(0.0, -186.0), (7.6, -182.0), (7.6, -170.0), (0.0, -164.0)], P1),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ geometria auxiliar
def loft(mb, poly0, z0, poly1, z1, m, bevel=0.0, caps=(True, True)):
    """tronco entre dois poligonos (mesmo numero de vertices, anti-horario) em z0 e z1"""
    bm = mb.bm
    v0 = [bm.verts.new((x, y, z0)) for x, y in poly0]
    v1 = [bm.verts.new((x, y, z1)) for x, y in poly1]
    n = len(v0)
    if caps[0]:
        bm.faces.new(list(reversed(v0)))
    if caps[1]:
        bm.faces.new(v1)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
    mb._post(v0 + v1, m, None, bevel, 1)


def point_down(mb, poly, z, apex, m):
    """ponta invertida (piramide para baixo) sob o poligono em z"""
    bm = mb.bm
    ring = [bm.verts.new((x, y, z)) for x, y in poly]
    tip = bm.verts.new(apex)
    n = len(ring)
    bm.faces.new(ring)
    for i in range(n):
        bm.faces.new((ring[(i + 1) % n], ring[i], tip))
    mb._post(ring + [tip], m, None, 0, 1)


def yz_prism(mb, x0, x1, pts, m):
    """poligono CONVEXO no plano YZ [(y, z)] extrudado de x0 a x1"""
    bm = mb.bm
    va = [bm.verts.new((x0, y, z)) for y, z in pts]
    vb = [bm.verts.new((x1, y, z)) for y, z in pts]
    n = len(pts)
    bm.faces.new(list(reversed(va)))
    bm.faces.new(vb)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((va[i], va[j], vb[j], vb[i]))
    mb._post(va + vb, m, None, 0, 1)


def ogive(y0, y1, zs, n=6):
    """intradorso de arco ogival equilatero de y0 a y1 (nascencas em zs): [(y, z)] do pe sul ao pe norte"""
    r = y1 - y0
    pts = []
    for k in range(n + 1):
        t = math.pi - (math.pi / 3.0) * k / n
        pts.append((y1 + r * math.cos(t), zs + r * math.sin(t)))
    for k in range(1, n + 1):
        t = math.pi / 3.0 - (math.pi / 3.0) * k / n
        pts.append((y0 + r * math.cos(t), zs + r * math.sin(t)))
    return pts


def spandrel(mb, x0, x1, arc, ztop, m):
    """tímpano macico entre o intradorso 'arc' e ztop, de x0 a x1 (faixas convexas: sem ngon concavo)"""
    bm = mb.bm
    A = [(bm.verts.new((x0, y, z)), bm.verts.new((x0, y, ztop))) for y, z in arc]
    B = [(bm.verts.new((x1, y, z)), bm.verts.new((x1, y, ztop))) for y, z in arc]
    for i in range(len(arc) - 1):
        bm.faces.new((A[i][0], A[i + 1][0], A[i + 1][1], A[i][1]))
        bm.faces.new((B[i][0], B[i][1], B[i + 1][1], B[i + 1][0]))
        bm.faces.new((A[i][0], B[i][0], B[i + 1][0], A[i + 1][0]))
        bm.faces.new((A[i][1], A[i + 1][1], B[i + 1][1], B[i][1]))
    for k in (0, -1):
        bm.faces.new((A[k][0], A[k][1], B[k][1], B[k][0]))
    mb._post([v for p in A + B for v in p], m, None, 0, 1)


def pier_poly(cy, hx, hy, tip):
    """planta do pilar da ponte: retangulo com talha-mar em ponta nos dois lados (leste/oeste)"""
    return [(-hx - tip, cy), (-hx, cy - hy), (hx, cy - hy), (hx + tip, cy), (hx, cy + hy), (-hx, cy + hy)]


# ------------------------------------------------------------------ ponte de chegada
BR_BODY_X = 10.2           # meia-largura do corpo do tabuleiro (face externa do parapeito)
BR_Z_SOFFIT = 25.4         # fundo do tabuleiro
PIERS = (-258.0, -235.5)   # eixo dos 2 pilares
PIER_HY = 3.5


def bridge():
    rng = random.Random(3101)
    mb = MB("SG_Ent_Bridge", "18_ENTRY", rng, detail="near")
    # corpo do tabuleiro: da ponta sul (y -262 exato) ate dentro do patio (escondido sob o piso do terreno)
    mb.box2((-BR_BODY_X, Y0, BR_Z_SOFFIT), (BR_BODY_X, Y1 + 2.0, DECK - 0.35), "Stone_SG_Block", 0.0)
    # encontro norte (base do canto do parapeito do patio, entra no penhasco)
    mb.box2((-14.4, Y1 - 4.0, 18.0), (14.4, Y1 + 2.0, DECK - 0.35), "Stone_SG_Block", 0.0)
    # cornija + cachorros (mesa de cachorros gotica) nos 2 lados
    for s in (-1, 1):
        mb.box2((s * (BR_BODY_X - 0.4), Y0, 25.9), (s * (BR_BODY_X + 0.55), Y1 - 1.0, 26.75), "Stone_SG_Trim", 0.08)
        y = Y0 + 1.3
        while y < Y1 - 1.5:
            mb.box((0.7, 0.8, 1.0), (s * (BR_BODY_X + 0.2), y, 25.4), (0, 0, 0), "Stone_SG_Trim", 0.0)
            y += 2.4
    # pilares com talha-mar: 3 estagios com ressalto (friso claro) e ponta escura para as nuvens
    for cy in PIERS:
        top = pier_poly(cy, 9.4, PIER_HY, 3.2)
        mb.prism(SL.ccw(top), 8.0, 24.6, "Stone_SG_Block")
        loft(mb, top, 24.6, pier_poly(cy, 9.4, PIER_HY, 0.9), BR_Z_SOFFIT + 0.5, "Stone_SG_Trim")   # capeamento das pontas
        mb.prism(SL.ccw(pier_poly(cy, 9.8, PIER_HY + 0.35, 3.5)), 7.2, 8.0, "Stone_SG_Trim")
        loft(mb, pier_poly(cy, 8.2, 3.0, 2.7), -14.0, pier_poly(cy, 9.2, PIER_HY - 0.1, 3.0), 7.2, "Stone_SG_Block")
        mb.prism(SL.ccw(pier_poly(cy, 8.6, 3.3, 3.0)), -14.8, -14.0, "Stone_SG_Trim")
        low = pier_poly(cy, 6.2, 2.4, 2.1)
        loft(mb, low, -34.0, pier_poly(cy, 7.9, 2.9, 2.6), -14.8, "Stone_SG_Block")
        point_down(mb, low, -34.0, (0.0, cy + 0.4, -58.0), "Cliff_Rock_SG_Dark")
        # quina clara no bico do talha-mar (le a ponta gotica de longe)
        for sx in (-1, 1):
            mb.beam((sx * 12.45, cy, -14.0), (sx * 12.45, cy, 7.2), 0.5, 0.5, "Stone_SG_Trim", 0.0)
            mb.beam((sx * 12.45, cy, 8.0), (sx * 12.45, cy, 24.6), 0.5, 0.5, "Stone_SG_Trim", 0.0)
    # arco ogival entre os pilares (timpano + aduelas claras salientes + fecho)
    ya, yb = PIERS[0] + PIER_HY, PIERS[1] - PIER_HY
    zs = BR_Z_SOFFIT - 1.3 - (yb - ya) * 0.866
    arc = ogive(ya, yb, zs, 6)
    spandrel(mb, -9.4, 9.4, arc, BR_Z_SOFFIT + 0.2, "Stone_SG_Block")
    # aduelas RADIAIS individuais nas 2 faces (overhaul 01: antes eram vigas de 19,6 que liam em degraus), um pouco
    # abaixo do intradorso para o anel do arco ler tambem por baixo; fecho maior no vertice
    band = 1.3
    cA, cB = (yb, zs), (ya, zs)

    def ring(pts, c):
        out = []
        for i in range(len(pts) - 1):
            (y0_, z0_), (y1_, z1_) = pts[i], pts[i + 1]
            for t in (0.0, 0.5):
                out.append((y0_ + (y1_ - y0_) * t, z0_ + (z1_ - z0_) * t))
        out.append(pts[-1])
        res = []
        for py, pz in out:
            ny, nz = py - c[0], pz - c[1]
            ln = math.hypot(ny, nz)
            res.append(((py - ny / ln * 0.08, pz - nz / ln * 0.08), (py + ny / ln * band, pz + nz / ln * band)))
        return res
    halves = (ring(arc[:7], cA), ring(arc[6:], cB))
    for sx in (-1, 1):
        xa, xb = sorted((sx * 9.2, sx * 9.72))
        for hi, rr in enumerate(halves):
            rng_ = range(len(rr) - 2) if hi == 0 else range(1, len(rr) - 1)
            for j in rng_:
                (i0, o0), (i1, o1) = rr[j], rr[j + 1]
                gy, gz = (i1[0] - i0[0]), (i1[1] - i0[1])
                gl = math.hypot(gy, gz)
                ey, ez = gy / gl * 0.03, gz / gl * 0.03
                q = [(i0[0] + ey, i0[1] + ez), (i1[0] - ey, i1[1] - ez), (o1[0] - ey, o1[1] - ez),
                     (o0[0] + ey, o0[1] + ez)]
                yz_prism(mb, xa, xb, q, "Stone_SG_Trim")
        ap = arc[6]
        yz_prism(mb, xa - (0.1 if sx < 0 else 0), xb + (0.1 if sx > 0 else 0),
                 [(ap[0] - 0.55, ap[1] - 0.2), (ap[0] + 0.55, ap[1] - 0.2), (ap[0] + 0.8, ap[1] + band + 0.5),
                  (ap[0] - 0.8, ap[1] + band + 0.5)], "Stone_SG_Trim")                          # fecho
    # tabuleiro de lajes (fiada corrida, juntas escuras); topo = DECK
    mb.box2((-HW, Y0, DECK - 0.75), (HW, Y1, DECK - 0.25), "Stone_SG_Floor", 0.0)
    CURB = 1.1
    for sx in (-1, 1):
        yy = Y0
        while yy < Y1 - 0.05:
            ye = min(yy + 4.25, Y1)
            xa, xb = sorted((sx * HW, sx * (HW - CURB)))
            mb.box2((xa, yy + 0.07, DECK - 0.35), (xb, ye - 0.07, DECK), "Stone_SG_Obsidian", 0.06)
            yy = ye
    row = 2.45
    y = Y0
    k = 0
    while y < Y1 - 0.05:
        yy = min(y + row, Y1)
        x = -HW + CURB
        widths = [2.4, 3.0, 3.6]
        if k % 2:
            x -= 1.3
        while x < HW - CURB - 0.05:
            w = rng.choice(widths)
            xa, xb = max(x, -HW + CURB), min(x + w, HW - CURB)
            if xb - xa > 0.6:
                h = 0.35 + rng.uniform(-0.03, 0.02)
                mb.box2((xa + 0.09, y + 0.09, DECK - 0.35), (xb - 0.09, yy - 0.09, DECK - 0.35 + h),
                        "Stone_Paving_SG", 0.07)
            x += w
        y = yy
        k += 1
    return mb.finish()


# ------------------------------------------------------------------ parapeitos / balaustradas (so visual: guardas no sg_col)
# OVERHAUL 01 (2026-09-29): o parapeito deixa de ser viga + viga. Linguagem unica de cantaria perto do jogador:
#   plinto (base mais larga, 0,45 acima do piso) -> corpo recuado -> ARCADA CEGA na face que o jogador ve (colunelos e
#   timpanos ogivais em relevo de 0,14, um valor acima do corpo) -> pingadeira -> CAPA segmentada (pecas de ~2,4 com
#   junta, cantaria um valor abaixo do Stone_SG_Trim). Pilarete = plinto + toro, fuste de quinas chanfradas, capitel em
#   2 degraus e remate do kit (bola com colar) ou a lanterna da ordem so nos NOS (comeco/fim da ponte e topo da escada).
PAR_M = "Stone_SG_Castle_B"    # corpo dos parapeitos / muretas / pilaretes (um valor abaixo do Stone_SG_Block)
REL_M = "Stone_SG_Block_B"     # relevo (arcada cega, plinto, rodape): um valor acima do corpo
LAN_S = 0.85                   # escala das lanternas nos pilaretes


def _lathe(mb, c, prof, m, n=8, rot=0.0, closed=False):
    EM._lathe(mb, c, prof, m, n, rot, closed)


def finial(mb, x, y, z, r=0.42, m=CAP_M, n=8):
    """remate do kit: bola com colar (torno de 8 lados) assentada em z"""
    prof = [(0.95, 0.0), (0.95, 0.12), (0.48, 0.32), (0.92, 0.56), (1.0, 0.86), (0.70, 1.20), (0.0, 1.40)]
    _lathe(mb, (x, y, z), [(a * r, b * r) for a, b in prof], m, n, math.pi / n)


def chamfer_sq(x, y, hs, c):
    """quadrado de meia-aresta hs com as quinas chanfradas em c (octogono irregular, anti-horario)"""
    return [(x - hs + c, y - hs), (x + hs - c, y - hs), (x + hs, y - hs + c), (x + hs, y + hs - c),
            (x + hs - c, y + hs), (x - hs + c, y + hs), (x - hs, y + hs - c), (x - hs, y - hs + c)]


def _post(mb, x, y, z, size=1.6, h=PAR_H + 0.8, lamp=False):
    """pilarete: plinto + toro, fuste de quinas chanfradas, capitel em 2 degraus (topo em z + h + 0,35) e remate do kit
    (bola com colar) ou a LANTERNA da ordem assentada num prato de obsidiana"""
    sp = size + 0.34
    mb.box((sp, sp, 0.55), (x, y, z + 0.275), (0, 0, 0), REL_M, 0.08)
    FP.frustum(mb, (x, y, z + 0.55), sp, sp, size + 0.04, size + 0.04, 0.16, REL_M)
    mb.prism(chamfer_sq(x, y, size / 2, 0.16), z + 0.71, z + h - 0.02, PAR_M)
    mb.box((size + 0.12, size + 0.12, 0.16), (x, y, z + h + 0.06), (0, 0, 0), CAP_M, 0.04)
    mb.box((size + 0.38, size + 0.38, 0.21), (x, y, z + h + 0.245), (0, 0, 0), CAP_M, 0.06)
    zt = z + h + 0.35
    if lamp:
        mb.box((1.12 * LAN_S + 0.1, 1.12 * LAN_S + 0.1, 0.16), (x, y, zt + 0.08), (0, 0, 0), "Stone_SG_Obsidian", 0.04)
        EM.lantern_head(mb, mb, (x, y, zt + 0.16 + EM.LH_BASE * LAN_S), 0.0, LAN_S)
    else:
        finial(mb, x, y, zt, 0.44, n=6)


def face_spandrel(mb, org, d, nrm, arc, ztop, off0, off1, m):
    """timpano em relevo numa face: regiao entre o intradorso 'arc' [(t, z)] e ztop, em faixas convexas; t ao longo
    de d a partir de org, espessura de off0 a off1 ao longo da normal nrm"""
    bm = mb.bm

    def P(t, zz, o):
        return (org.x + d.x * t + nrm.x * o, org.y + d.y * t + nrm.y * o, zz)
    A = [(bm.verts.new(P(t, zz, off0)), bm.verts.new(P(t, ztop, off0))) for t, zz in arc]
    B = [(bm.verts.new(P(t, zz, off1)), bm.verts.new(P(t, ztop, off1))) for t, zz in arc]
    faces = []
    for i in range(len(arc) - 1):
        faces.append(bm.faces.new((A[i][0], A[i + 1][0], A[i + 1][1], A[i][1])))
        faces.append(bm.faces.new((B[i][0], B[i][1], B[i + 1][1], B[i + 1][0])))
        faces.append(bm.faces.new((A[i][0], B[i][0], B[i + 1][0], A[i + 1][0])))
        faces.append(bm.faces.new((A[i][1], A[i + 1][1], B[i + 1][1], B[i][1])))
    for k in (0, -1):
        faces.append(bm.faces.new((A[k][0], A[k][1], B[k][1], B[k][0])))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for p in A + B for v in p], m, None, 0, 1)


def pointed_arc(t0, t1, zs, rise, n=3):
    """intradorso ogival abatido de t0 a t1 (nascencas em zs, fecho em zs + rise): 2 arcos de raio 0,6 do vao
    achatados na vertical"""
    span = t1 - t0
    R = 0.6 * span
    phi = math.acos((0.5 * span - R) / R)
    k = rise / (R * math.sin(phi))
    left = []
    for i in range(n + 1):
        th = math.pi - (math.pi - phi) * i / n
        left.append((t0 + R + R * math.cos(th), zs + k * R * math.sin(th)))
    right = [(t0 + t1 - t, zz) for t, zz in reversed(left[:-1])]
    left[-1] = ((t0 + t1) / 2, zs + rise)
    return left + right


def arcade(mb, pa, pb, nrm, z, th, clear=()):
    """arcada cega em relevo na face 'nrm' do trecho pa->pb (eixo do muro): colunelos + timpanos ogivais.
    clear = [(t0, t1)] trechos ocupados por pilaretes (a arcada se divide entre eles)"""
    d = (pb - pa)
    Ltot = d.length
    d.normalize()
    off0, dep = th / 2 - 0.02, 0.14
    zp, zt = z + 0.8, z + PAR_H - 0.02
    free = []
    cur = 0.0
    for c0, c1 in sorted(clear):
        if c0 > cur + 0.6:
            free.append((cur, c0))
        cur = max(cur, c1)
    if Ltot > cur + 0.6:
        free.append((cur, Ltot))
    rib = 0.22
    for f0, f1 in free:
        nb = max(1, int(round((f1 - f0) / 2.3)))
        w = (f1 - f0) / nb
        ang = math.atan2(d.y, d.x)
        for k in range(nb + 1):
            t = f0 + k * w
            t = min(max(t, f0 + rib / 2), f1 - rib / 2)
            c = pa + d * t + nrm * (off0 + dep / 2)
            mb.box((rib, dep, zt - zp), (c.x, c.y, (zp + zt) / 2), (0, 0, ang), REL_M, 0.0)
        for k in range(nb):
            t0, t1 = f0 + k * w + rib / 2, f0 + (k + 1) * w - rib / 2
            if k == 0:
                t0 = max(t0, f0 + rib)
            if k == nb - 1:
                t1 = min(t1, f1 - rib)
            if t1 - t0 < 0.5:
                continue
            arc = pointed_arc(t0, t1, zt - 0.62, 0.46, 2)
            face_spandrel(mb, pa, d, nrm, arc, zt, off0, off0 + dep, REL_M)


def parapet_run(mb, pts, z, th=1.2, extra=(), skip=(), post=1.6, lit=()):
    """parapeito de cantaria ao longo da polilinha (eixos alinhados): plinto, corpo, arcada cega na face vista (a do
    eixo nos trechos ao longo de Y; as duas nos trechos curtos ao longo de X), pingadeira e capa segmentada. Pilaretes
    SO nos vertices (pontas e cantos) e nos pontos 'extra'. 'lit' = indices dos vertices cujo pilarete leva lanterna;
    extra = [(x, y)] ou [(x, y, lamp)]. As pontas NAO passam do primeiro/ultimo ponto (a ponta sul da ponte fica em
    y -262 exato). O topo da capa fica em z + PAR_H + 0,445 (o mesmo de antes)."""
    n = len(pts)
    zc = z + PAR_H
    posts = []
    for i, p in enumerate(pts):
        pv = Vector((p[0], p[1], 0))
        if any((pv - Vector((q[0], q[1], 0))).length < r for q, r in skip):
            continue
        q = Vector(pv)
        if i == 0:
            q += (Vector((*pts[1], 0)) - Vector((*pts[0], 0))).normalized() * (post / 2 + 0.16)
        elif i == n - 1:
            q += (Vector((*pts[-2], 0)) - Vector((*pts[-1], 0))).normalized() * (post / 2 + 0.16)
        posts.append((q, i in lit))
    for p in extra:
        posts.append((Vector((p[0], p[1], 0)), len(p) > 2 and p[2]))
    for i in range(n - 1):
        a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0))
        d = (b - a).normalized()
        ea = a - d * (th / 2 if i > 0 else 0.0)
        eb = b + d * (th / 2 if i < n - 2 else 0.0)
        mb.beam((ea.x, ea.y, z + PAR_H / 2), (eb.x, eb.y, z + PAR_H / 2), th, PAR_H, PAR_M, 0.0)
        mb.beam((ea.x, ea.y, z + 0.4), (eb.x, eb.y, z + 0.4), th + 0.34, 0.8, REL_M, 0.06)        # plinto
        mb.beam((ea.x, ea.y, zc + 0.06), (eb.x, eb.y, zc + 0.06), th + 0.16, 0.12, CAP_M, 0.0)   # pingadeira
        Ls = (eb - ea).length
        k = max(1, int(round(Ls / 2.4)))
        for j in range(k):
            pa_ = ea + d * (Ls * j / k + (0.03 if j else 0.0))
            pb_ = ea + d * (Ls * (j + 1) / k - (0.03 if j < k - 1 else 0.0))
            mb.beam((pa_.x, pa_.y, zc + 0.285), (pb_.x, pb_.y, zc + 0.285), th + 0.42, 0.33, CAP_M, 0.07)
        # arcada: trechos ocupados pelos pilaretes deste trecho
        clear = []
        for q, _ in posts:
            t = (q - ea).dot(d)
            dist = (q - (ea + d * t)).length
            if dist < 0.8 and -1.5 < t < Ls + 1.5:
                clear.append((t - (post + 0.34) / 2 - 0.05, t + (post + 0.34) / 2 + 0.05))
        nrm = Vector((-d.y, d.x, 0.0))
        if abs(d.x) < 0.3:
            faces = [nrm if nrm.x * a.x < 0 else -nrm]
        else:
            faces = [nrm, -nrm]
        for f in faces:
            arcade(mb, ea, eb, f, z, th, clear)
    for q, lamp in posts:
        _post(mb, q.x, q.y, z, post, lamp=lamp)


def yz_block(mb, x0, x1, pts, m, bevel=0.0):
    """poligono CONVEXO no plano YZ [(y, z)] extrudado de x0 a x1 (com chanfro opcional)"""
    bm = mb.bm
    va = [bm.verts.new((x0, y, z)) for y, z in pts]
    vb = [bm.verts.new((x1, y, z)) for y, z in pts]
    n = len(pts)
    faces = [bm.faces.new(list(reversed(va))), bm.faces.new(vb)]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    import bmesh
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(va + vb, m, None, bevel, 1)


def _dedupe(poly, eps=1e-3):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1]) > eps:
            out.append((p[0], p[1]))
    while len(out) > 1 and abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def _clip_y(poly, ya, yb):
    p = SL.clip(poly, 1.0, 0.0, yb)
    return SL.clip(p, -1.0, 0.0, -ya)


def stair_wall(mb, mh, s):
    """banzo da escadaria (mureta inclinada de cada lado, face interna em |x| = 9 = guarda do sg_col):
    paramento de CANTARIA em fiadas horizontais alternadas (1,2 / 0,9) com juntas desencontradas e chanfro (a junta le
    rebaixada), rodape inclinado na face da escada (acompanha os focinhos), capa inclinada em pecas com junta e
    pingadeira, e os pilaretes de arranque (pe: remate do kit; topo: lanterna)"""
    ya, yb = L.ENTRY_STAIR[1], L.ENTRY_STAIR_Y1          # -206 .. -188
    ta, tb = PAR_Z + PAR_H + 0.35, P1 - 0.35 + PAR_H + 0.35
    k = (tb - ta) / (yb - ya)
    x0, x1 = sorted((s * HW, s * (HW + 1.4)))
    zb = DECK - 1.5
    hs = (1.2, 0.9)
    c0, ci = zb, 0
    while c0 < tb - 0.05:
        c1 = min(c0 + hs[ci % 2], tb)
        # fiada: faixa [c0, c1] sob a linha inclinada z = ta + k (y - ya)
        if c1 <= ta:
            poly = [(ya, c0), (yb, c0), (yb, c1), (ya, c1)]
        else:
            ys0 = ya + max(0.0, (c0 - ta) / k)
            ys1 = ya + (c1 - ta) / k
            poly = [(ys0, c0), (yb, c0), (yb, c1), (ys1, c1)]
            if c0 < ta:
                poly.append((ya, ta))
        # blocos de ~2,6 com juntas desencontradas fiada a fiada
        L0 = 2.6
        off = (0.0, 1.3)[ci % 2]
        cuts = [ya] + [ya + off + L0 * j for j in range(1, 9) if ya + off + L0 * j < yb - 0.8] + [yb]
        for u0, u1 in zip(cuts, cuts[1:]):
            bp = _dedupe(_clip_y(poly, u0 + 0.03, u1 - 0.03))
            if len(bp) >= 3 and abs(SL.area(bp)) > 0.2 and max(p[0] for p in bp) - min(p[0] for p in bp) > 0.3:
                yz_block(mh, x0, x1, bp, PAR_M, 0.07)
        c0, ci = c1, ci + 1
    # rodape inclinado na face da escada: a aresta de baixo passa 0,08 acima dos focinhos
    foot, deg, w, n, tread, g = L.stair_frame("Entry")
    rise = (L.STAIR_TOP_Z["Entry"] - foot[2]) / n

    def zn(y):
        return foot[2] + rise + (y - ya) * rise / tread
    xr = s * (HW - 0.08)
    ra, rb = ya + 0.1, yb - 0.1
    mb.beam((xr, ra, zn(ra) + 0.42), (xr, rb, zn(rb) + 0.42), 0.2, 0.62, REL_M, 0.04)

    # capa inclinada em pecas (junta a cada ~2,5) + pingadeira
    def zl(y):
        return ta + k * (y - ya)
    xm = s * (HW + 0.7)
    A = Vector((xm, ya - 0.2, zl(ya - 0.2)))
    B = Vector((xm, yb + 0.2, zl(yb + 0.2)))
    dd = B - A
    nseg = max(1, int(round(dd.length / 2.5)))
    for j in range(nseg):
        p0 = A + dd * (j / nseg) + dd.normalized() * (0.03 if j else 0.0)
        p1 = A + dd * ((j + 1) / nseg) - dd.normalized() * (0.03 if j < nseg - 1 else 0.0)
        mb.beam((p0.x, p0.y, p0.z + 0.28), (p1.x, p1.y, p1.z + 0.28), 1.8, 0.36, CAP_M, 0.07)
    mb.beam((xm, A.y + 0.1, A.z + 0.1 * k + 0.04), (xm, B.y - 0.1, B.z - 0.1 * k + 0.04), 1.58, 0.14, CAP_M, 0.0)
    # arranque (pe e topo: dado com remate do kit). OVERHAUL 12 (12.04): a lanterna do topo SAIU - a 9 studs dela a
    # lanterna baixa do portico B ja marca o mesmo no (2 lanternas por lado lia cacho)
    _post(mb, s * (HW + 0.8), ya + 0.4, PAR_Z, 1.6, PAR_H + 1.3, lamp=False)
    _post(mb, s * (HW + 0.8), yb - 0.6, P1 - 0.35, 1.6, PAR_H + 1.3, lamp=False)


def parapets():
    mb = MB("SG_Ent_Parapets", "18_ENTRY", random.Random(3102), detail="near")
    mh = MB("SG_Ent_StairWalls", "18_ENTRY", random.Random(3105), detail="hero")
    xh = L.ENTRY_HIGH[2]                   # 12
    xl = L.ENTRY_LOW[2]                    # 13
    for s in (-1, 1):
        skipA = [((s * PORTICO_A["xc"], PORTICO_A["y"]), 4.0)]
        # ponte -> canto sul do patio -> lateral do patio -> canto norte (pe da escada). LANTERNAS SO NOS NOS: o
        # pilarete da ponta sul (comeco da ponte); o da cabeceira leva remate desde o overhaul 12 (o fim da ponte e o
        # portico A, com a lanterna baixa acesa a 9 studs); os dos pilares levam remate
        parapet_run(mb, [(s * (HW + 0.6), Y0), (s * (HW + 0.6), Y1 - 0.6), (s * (xl + 0.6), Y1 - 0.6),
                         (s * (xl + 0.6), L.ENTRY_STAIR[1] + 0.5), (s * (HW + 1.4), L.ENTRY_STAIR[1] + 0.5)],
                    PAR_Z, extra=[(s * (HW + 0.6), cy, False) for cy in PIERS],
                    skip=skipA + [((s * (HW + 1.4), L.ENTRY_STAIR[1] + 0.5), 1.0)], lit=(0,))
        stair_wall(mb, mh, s)
        # calcada alta: borda sul (ao lado do topo da escada) + lateral ate a praca (sem lanterna: o portico B e os
        # postes da praca ja marcam os nos)
        skipB = [((s * PORTICO_B["xc"], PORTICO_B["y"]), 4.4), ((s * (HW + 1.4), L.ENTRY_STAIR_Y1 - 0.6), 1.0)]
        parapet_run(mb, [(s * (HW + 1.4), L.ENTRY_STAIR_Y1 - 0.6), (s * (xh + 0.6), L.ENTRY_STAIR_Y1 - 0.6),
                         (s * (xh + 0.6), L.P1_POLY[3][1])], P1 - 0.35, skip=skipB)
    mh.finish()
    return mb.finish()


def stair():
    mb = MB("SG_Ent_Stair", "18_ENTRY", random.Random(3103), detail="near")
    # overhaul 01: degraus de PEDRA (sg_lib.plan_stair com pisadas partidas em 4-5 pedras de juntas desencontradas,
    # focinho saliente 0,12 chanfrado e mais claro, espelho recuado e mais escuro)
    SL.plan_stair(mb, "Entry", m="Stone_SG_Block_B", side_m="Stone_SG_Castle_B", stringers=False,
                  riser_m="Stone_SG_Castle_B")
    return mb.finish()


# ------------------------------------------------------------------ porticos
def arch_band(mb, F, yo0, yo1, cx, zs, w, band, m, nseg=4):
    """arco ogival EQUILATERO de espessura real: faixa entre o intradorso (vao w, nascencas em zs) e o extradorso
    (+band), no plano local XZ de F, de yo0 a yo1 ao longo de +Y local. Cada meio arco tem o centro no pe oposto."""
    import bmesh
    ai = math.radians(60.0)
    ao = math.acos((w / 2) / (w + band))
    for sg in (-1, 1):
        inn = [(cx + sg * (-w / 2 + w * math.cos(ai * i / nseg)), zs + w * math.sin(ai * i / nseg))
               for i in range(nseg + 1)]
        out = [(cx + sg * (-w / 2 + (w + band) * math.cos(ao * i / nseg)), zs + (w + band) * math.sin(ao * i / nseg))
               for i in range(nseg + 1)]
        inn[-1] = (cx, inn[-1][1])
        out[-1] = (cx, out[-1][1])
        for i in range(nseg):
            q = [inn[i], inn[i + 1], out[i + 1], out[i]]
            bm = mb.bm
            va = [bm.verts.new(F.p(px, yo0, pz)) for px, pz in q]
            vb = [bm.verts.new(F.p(px, yo1, pz)) for px, pz in q]
            faces = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
            for a in range(4):
                b = (a + 1) % 4
                faces.append(bm.faces.new((va[a], va[b], vb[b], vb[a])))
            bmesh.ops.recalc_face_normals(bm, faces=faces)
            mb._post(va + vb, m, None, 0, 1)


def lancet(mb, F, yo, w, z0, z1, m=CAP_M, void="Stone_SG_Obsidian"):
    """janela cega ogival de verdade numa face do fuste (local +Y = normal da face, yo = face): vazio escuro rente a
    face, moldura saliente 0,3 (ombreiras + arco com espessura real) e peitoril com pingadeira. O fecho do arco fica
    onde ficava o antigo (z1 + 0,85 w)."""
    import bmesh
    band, dep = 0.26, 0.3
    zs = max(z1 + 0.85 * w - (0.866 * w + band * 0.9), z0 + 0.8)
    pts = [(-w / 2, z0), (w / 2, z0), (w / 2, zs)]
    pts += [(-w / 2 + w * math.cos(math.radians(a)), zs + w * math.sin(math.radians(a))) for a in (20.0, 40.0)]
    pts += [(0.0, zs + 0.866 * w)]
    pts += [(w / 2 - w * math.cos(math.radians(a)), zs + w * math.sin(math.radians(a))) for a in (40.0, 20.0)]
    pts += [(-w / 2, zs)]
    bm = mb.bm
    va = [bm.verts.new(F.p(px, yo - 0.12, pz)) for px, pz in pts]
    vb = [bm.verts.new(F.p(px, yo + 0.02, pz)) for px, pz in pts]
    faces = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        faces.append(bm.faces.new((va[i], va[j], vb[j], vb[i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(va + vb, void, None, 0, 1)
    # ombreiras + arco com espessura (faixa entre intradorso e extradorso)
    for sg in (-1, 1):
        mb.box((band, dep, zs - z0), F.p(sg * (w / 2 + band / 2), yo + dep / 2 - 0.1, (z0 + zs) / 2), F.r(), m, 0.0)
    arch_band(mb, F, yo - 0.1, yo + dep - 0.1, 0.0, zs, w, band, m, 3)
    # peitoril com pingadeira
    mb.box((w + 2 * band + 0.3, dep + 0.16, 0.2), F.p(0, yo + dep / 2 - 0.02, z0 - 0.1), F.r(), m, 0.0)
    mb.box((w + 2 * band + 0.1, dep, 0.1), F.p(0, yo + dep / 2 - 0.1, z0 - 0.25), F.r(), m, 0.0)


def lantern(mb, x, y, z, tag):
    """lanterna baixa ao pe do portico: BALAUSTRE torneado curto de pedra + a lanterna da ordem (kit); a luz real fica
    no centro do vidro"""
    prof = [(0.66, 0.0), (0.66, 0.18), (0.50, 0.26), (0.38, 0.42), (0.32, 0.62), (0.44, 0.92), (0.32, 1.18),
            (0.38, 1.28), (0.62, 1.34), (0.62, 1.50)]
    _lathe(mb, (x, y, z), prof, "Stone_SG_Castle_B", 8, math.pi / 8)
    c = EM.lantern_head(mb, mb, (x, y, z + 1.5 + EM.LH_BASE * 0.95), 0.0, 0.95)
    light("L_SGEnt_Portico%s_Lantern" % tag, "POINT", c, 320.0, WARM, 0.4)


def spire8(mb, x, y, r, z0, h, m="Roof_SG_Navy", ring_m="Metal_SG_Silver"):
    """agulha octogonal do portico (a mesma leitura das agulhas das torres do castelo): beiral alargado 10 %, cone
    ingreme, anel de prata a 0,36 h, florao de prata torneado (colar, bulbo, gola, ponta) no topo"""
    rot = math.pi / 8
    _lathe(mb, (x, y, z0), [(r * 1.1, 0.0), (r * 0.9, h * 0.08), (0.12, h - 0.02), (0.0, h)], m, 8, rot)
    zf = h * 0.36

    def rad(z):
        return r * 0.9 + (0.12 - r * 0.9) * (z - h * 0.08) / (h * 0.92 - 0.02)
    _lathe(mb, (x, y, z0), [(rad(zf - 0.22) - 0.05, zf - 0.22), (rad(zf - 0.22) + 0.13, zf - 0.16),
                            (rad(zf + 0.16) + 0.13, zf + 0.16), (rad(zf + 0.22) - 0.05, zf + 0.22)], ring_m, 8, rot)
    prof = [(0.17, 0.0), (0.24, 0.1), (0.14, 0.22), (0.3, 0.46), (0.22, 0.68), (0.09, 0.84), (0.13, 0.96),
            (0.0, 1.45)]
    k = 1.3
    _lathe(mb, (x, y, z0 + h - 0.35), [(a * k, b * k) for a, b in prof], ring_m, 6, math.pi / 6)


def pinnacle(mb, px, py, z0, h, r=0.34, m=CAP_M):
    """pinaculo do kit (altos): fuste octogonal, colar, agulha de 8 lados e botao"""
    mb.prism(chamfer_sq(px, py, r, r * 0.29), z0, z0 + 0.8, m)
    mb.box((2 * r + 0.16, 2 * r + 0.16, 0.14), (px, py, z0 + 0.87), (0, 0, 0), m, 0.03)
    SL.spire(mb, (px, py), r * 1.02, z0 + 0.94, h, m, n=8)
    _lathe(mb, (px, py, z0 + 0.94 + h - 0.1), [(0.07, 0.0), (0.13, 0.08), (0.10, 0.18), (0.0, 0.26)], m, 6)


def pylon(mb, P, side):
    """um pilar do portico P no lado side (-1 oeste, +1 leste)"""
    xc, y, z, s, H = side * P["xc"], P["y"], P["z"], P["s"], P["H"]
    pl = s + 0.8
    apron = 2.2
    deep = 3.0 if P["name"] == "A" else 8.0               # o B passa da borda da calcada: base desce ate o terreno
    # plinto com avental na frente (sul) que leva a lanterna
    mb.box2((xc - pl / 2, y - pl / 2 - apron, z - deep), (xc + pl / 2, y + pl / 2, z + 0.7), "Stone_SG_Block", 0.12)
    mb.box2((xc - pl / 2 - 0.12, y - pl / 2 - apron - 0.12, z + 0.7), (xc + pl / 2 + 0.12, y + pl / 2 + 0.12, z + 1.0),
            CAP_M, 0.08)
    # base + chanfro de assento
    mb.box((s + 0.6, s + 0.6, 2.4), (xc, y, z + 2.2), (0, 0, 0), "Stone_SG_Castle_B", 0.15)
    FP.frustum(mb, (xc, y, z + 3.4), s + 0.6, s + 0.6, s, s, 0.6, CAP_M)
    zt = z + 4.0 + H
    zm = z + 4.0 + H * 0.4
    ch = 0.34                                             # chanfro das quinas do fuste
    # fuste de quinas CHANFRADAS: terco de baixo em fiadas de cantaria (juntas chanfradas), o resto inteiro
    zc_ = z + 4.0
    for hh in (1.3, 1.1, 1.3):
        mb.prism(chamfer_sq(xc, y, s / 2, ch), zc_, zc_ + hh, "Stone_SG_Castle_B", bevel=0.06)
        zc_ += hh
    mb.prism(chamfer_sq(xc, y, s / 2, ch), zc_, zt, "Stone_SG_Castle_B")
    # colunelos nos chanfros (do assento ate o friso e do friso ate a cornija)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cxp, cyp = xc + sx * (s / 2 - ch * 0.5), y + sy * (s / 2 - ch * 0.5)
            mb.rod((cxp, cyp, z + 4.0), (cxp, cyp, zm - 0.25), 0.13, CAP_M, 6)
            mb.rod((cxp, cyp, zm + 0.25), (cxp, cyp, zt), 0.13, CAP_M, 6)
    # frisos (meio e topo) + cornija
    mb.box((s + 0.4, s + 0.4, 0.5), (xc, y, zm), (0, 0, 0), CAP_M, 0.08)
    mb.box((s + 1.2, s + 1.2, 0.9), (xc, y, zt + 0.45), (0, 0, 0), CAP_M, 0.12)
    # coroa: bloco + gabletes com espessura, cimalha nas vertentes e florao + pinaculos do kit + agulha navy
    cs = s - 0.2
    mb.box((cs, cs, 2.2), (xc, y, zt + 0.9 + 1.1), (0, 0, 0), "Stone_SG_Castle_B", 0.1)
    zc = zt + 0.9 + 2.2
    gh = cs * 0.55
    for k in range(4):
        a = k * math.pi / 2
        F = Frame(xc, y, 0.0, a)
        pts = [(-cs / 2, 0.0), (cs / 2, 0.0), (0.0, gh)]
        bm = mb.bm
        yo0, yo1 = cs / 2 - 0.45, cs / 2 + 0.12
        v0 = [bm.verts.new(F.p(px, yo0, zc - 0.6 + pz)) for px, pz in pts]
        v1 = [bm.verts.new(F.p(px, yo1, zc - 0.6 + pz)) for px, pz in pts]
        bm.faces.new(v0)
        bm.faces.new(list(reversed(v1)))
        for i in range(3):
            j = (i + 1) % 3
            bm.faces.new((v0[i], v0[j], v1[j], v1[i]))
        mb._post(v0 + v1, "Stone_SG_Castle_B", None, 0, 1)
        # cimalha: as 2 vertentes em cantaria saliente + florao no vertice
        for sg in (-1, 1):
            pa_ = F.p(sg * (cs / 2 + 0.1), (yo0 + yo1) / 2 + 0.06, zc - 0.6 - 0.02)
            pb_ = F.p(0.0, (yo0 + yo1) / 2 + 0.06, zc - 0.6 + gh + 0.06)
            mb.beam(pa_, pb_, 0.72, 0.24, CAP_M, 0.04)
        fp = F.p(0.0, yo1 - 0.1, zc - 0.6 + gh + 0.12)
        finial(mb, fp.x, fp.y, fp.z, 0.2, n=6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = xc + sx * (cs / 2 - 0.1), y + sy * (cs / 2 - 0.1)
            pinnacle(mb, px, py, zc, 1.3 + s * 0.25)
    # OVERHAUL 12 (12.12): a piramide de 4 lados (+ losango de prata de 4) virou a AGULHA OCTOGONAL da familia das
    # torres do castelo (beiral alargado, anel de prata a 1/3) com o florao de prata torneado no topo
    spire8(mb, xc, y, cs / 2 * 0.92, zc, P["spire"])
    Fi = Frame(xc, y, 0.0, math.pi / 2 if side > 0 else -math.pi / 2)     # local +Y -> mundo -side*X (eixo)
    Fn = Frame(xc, y, 0.0, 0.0)
    Fs = Frame(xc, y, 0.0, math.pi)
    if P["name"] == "B":
        # face SUL do portico B (o portao da ordem): estandarte da ordem numa verga presa ao fuste por 2 bracos.
        # O portico A ficou SEM estandarte (16.02: metade dos estandartes da entrada; o sinal fica no portao)
        yb = y - (s / 2 + 0.55)
        EM.banner(mb, mb, mb, mb, (xc, yb, zt - 0.9), -math.pi / 2, P["bw"], P["bh"], trim=EM.BRONZE)
        for sg in (-1, 1):
            mb.beam((xc + sg * (P["bw"] / 2 + 0.1), y - s / 2 + 0.1, zt - 0.9),
                    (xc + sg * (P["bw"] / 2 + 0.1), yb, zt - 0.9), 0.22, 0.22, "Metal_SG_BlackIron", 0.0)
    else:
        lancet(mb, Fs, s / 2, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    # face interna (para o eixo) e face norte: janela cega ogival
    lancet(mb, Fi, s / 2, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    lancet(mb, Fi, s / 2, s * 0.42, z + 5.0 + 0.6, zm - 1.4 - s * 0.36)
    lancet(mb, Fn, s / 2, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    # lanterna baixa quente ao pe (no avental do plinto)
    lantern(mb, xc, y - pl / 2 - apron / 2 - 0.1, z + 1.0, P["name"] + ("_W" if side < 0 else "_E"))
    # colisao propria: fuste (inteiro) + plinto/lanterna (baixo). Face interna >= 9,2 do eixo
    col_box2("SG_EntPortico", (xc - (s + 0.6) / 2, y - (s + 0.6) / 2, z), (xc + (s + 0.6) / 2, y + (s + 0.6) / 2,
                                                                          zt + 1.0))
    col_box2("SG_EntPortico", (xc - pl / 2, y - pl / 2 - apron, z), (xc + pl / 2, y + pl / 2, z + 5.2))


def lintel_b(mb):
    """verga do portico B (o portao da ordem): viga de obsidiana entre os fustes com PERFIL (filete + cavete + cimalha
    em cima, filete embaixo), campo rebaixado entre as faixas e um FECHO esculpido no meio das 2 faces (sem emblema:
    o emblema monumental da fachada esta no mesmo eixo). Vao livre de 23,7."""
    P = PORTICO_B
    y, z, s = P["y"], P["z"], P["s"]
    xi = P["xc"] - s / 2 + 0.1                        # entra 0,1 no fuste
    zt = z + 4.0 + P["H"]
    z0, z1 = zt - 2.3, zt - 0.05
    dep = s * 0.6
    mb.box2((-xi, y - dep / 2, z0), (xi, y + dep / 2, z1), "Stone_SG_Obsidian", 0.0)
    # faixas que emolduram o campo (o campo fica rebaixado 0,14 entre elas)
    mb.box2((-xi, y - dep / 2 - 0.14, z0 - 0.02), (xi, y + dep / 2 + 0.14, z0 + 0.3), CAP_M, 0.04)
    mb.box2((-xi, y - dep / 2 - 0.14, z1 - 0.42), (xi, y + dep / 2 + 0.14, z1 - 0.12), CAP_M, 0.04)
    # cimalha: filete + cavete (talude) + laje
    mb.box2((-xi, y - dep / 2 - 0.2, z1 - 0.12), (xi, y + dep / 2 + 0.2, z1 + 0.04), CAP_M, 0.0)
    FP.frustum(mb, (0.0, y, z1 + 0.04), 2 * xi, dep + 0.4, 2 * xi, dep + 0.9, 0.3, CAP_M)
    mb.box2((-xi, y - dep / 2 - 0.5, z1 + 0.34), (xi, y + dep / 2 + 0.5, z1 + 0.54), CAP_M, 0.05)
    # fecho esculpido (trapezio: mais largo em cima) nas 2 faces
    for sgn in (-1, 1):
        F = Frame(0.0, y, 0.0, 0.0 if sgn > 0 else math.pi)
        bm = mb.bm
        q = [(-0.55, z0 + 0.3), (0.55, z0 + 0.3), (0.8, z1 - 0.12), (-0.8, z1 - 0.12)]
        va = [bm.verts.new(F.p(px, dep / 2 - 0.05, pz)) for px, pz in q]
        vb = [bm.verts.new(F.p(px, dep / 2 + 0.3, pz)) for px, pz in q]
        import bmesh
        faces = [bm.faces.new(va), bm.faces.new(list(reversed(vb)))]
        for a in range(4):
            b = (a + 1) % 4
            faces.append(bm.faces.new((va[a], va[b], vb[b], vb[a])))
        bmesh.ops.recalc_face_normals(bm, faces=faces)
        mb._post(va + vb, CAP_M, None, 0.05, 1)


def porticos():
    mb = MB("SG_Ent_Porticos", "18_ENTRY", random.Random(3104), detail="hero")
    for P in (PORTICO_A, PORTICO_B):
        for side in (-1, 1):
            pylon(mb, P, side)
    lintel_b(mb)
    return mb.finish()


def build():
    bridge()
    stair()
    parapets()
    porticos()
