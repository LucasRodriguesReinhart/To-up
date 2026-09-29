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
from sg_lib import MB, col_box2, light, Frame
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

DECK, P1 = L.DECK, L.P1
Y0, Y1 = L.BRIDGE_Y0, L.BRIDGE_Y1          # -262 .. -228
HW = L.DECK_W / 2.0                        # 9: face interna dos parapeitos / guardas
PAR_Z = DECK - 0.35                        # base dos parapeitos (assentados no corpo do tabuleiro)
PAR_H = 2.0                                # parede do parapeito (+ capa 0,45)
WARM = (1.0, 0.64, 0.34)

# (x do eixo do pilar, secao do fuste, altura do fuste, agulha, largura e altura do estandarte)
PORTICO_A = dict(y=L.PORTICO_A_Y, z=DECK, xc=11.3, s=3.2, H=16.0, spire=7.0, bw=2.6, bh=9.0, name="A")
PORTICO_B = dict(y=L.PORTICO_B_Y, z=P1, xc=11.6, s=4.0, H=22.0, spire=10.0, bw=3.3, bh=12.0, name="B")

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
    band = 1.2
    cA, cB = (yb, zs), (ya, zs)
    for i in range(len(arc) - 1):
        (y0, z0), (y1, z1) = arc[i], arc[i + 1]
        c = cA if i < 6 else cB
        my, mz = (y0 + y1) / 2 - c[0], (z0 + z1) / 2 - c[1]
        ln = math.hypot(my, mz)
        ny, nz = my / ln, mz / ln
        off = band / 2 - 0.1
        d = Vector((0, y1 - y0, z1 - z0))
        sh = d.normalized() * 0.07
        a = Vector((0, y0 + ny * off, z0 + nz * off)) + sh
        b = Vector((0, y1 + ny * off, z1 + nz * off)) - sh
        mb.beam(a, b, 19.6, band, "Stone_SG_Trim", 0.0)
    ap = arc[6]
    mb.box((20.0, 1.3, 1.9), (0, ap[0], ap[1] + 0.7), (0, 0, 0), "Stone_SG_Trim", 0.0)    # fecho
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
PAR_M = "Stone_SG_Castle"      # corpo dos parapeitos / muretas / pilaretes (um valor abaixo do Stone_SG_Block)
LAN_S = 0.85                   # escala das lanternas nos pilaretes


def _post(mb, x, y, z, size=1.6, h=PAR_H + 0.8, lamp=False):
    """pilarete: fuste escuro + capa clara (remate) + pinaculo, ou LANTERNA dourada da ordem no lugar do pinaculo"""
    mb.box((size, size, h), (x, y, z + h / 2), (0, 0, 0), PAR_M, 0.12)
    mb.box((size + 0.3, size + 0.3, 0.35), (x, y, z + h + 0.175), (0, 0, 0), "Stone_SG_Trim", 0.08)
    if lamp:
        # soco de obsidiana sobre a capa e a lanterna (base da lanterna assentada no soco: nada flutua)
        zt = z + h + 0.35
        mb.box((size - 0.2, size - 0.2, 0.5), (x, y, zt + 0.25), (0, 0, 0), "Stone_SG_Obsidian", 0.05)
        EM.lantern_head(mb, mb, (x, y, zt + 0.5 + 1.14 * LAN_S), 0.0, LAN_S)
    else:
        SL.spire(mb, (x, y), (size - 0.1) / math.sqrt(2.0), z + h + 0.35, 0.6, "Stone_SG_Trim", n=4)


def parapet_run(mb, pts, z, th=1.2, extra=(), skip=(), post=1.6, lit=()):
    """parede baixa + capa clara ao longo da polilinha (eixos alinhados); pilaretes SO nos vertices (pontas e cantos)
    e nos pontos 'extra' (p.ex. sobre os pilares da ponte). 'lit' = indices dos vertices cujo pilarete leva lanterna;
    extra = [(x, y)] ou [(x, y, lamp)].
    As pontas NAO passam do primeiro/ultimo ponto (a ponta sul da ponte fica em y -262 exato)."""
    n = len(pts)
    for i in range(n - 1):
        a, b = Vector((*pts[i], 0)), Vector((*pts[i + 1], 0))
        d = (b - a).normalized()
        ea = a - d * (th / 2 if i > 0 else 0.0)
        eb = b + d * (th / 2 if i < n - 2 else 0.0)
        mb.beam((ea.x, ea.y, z + PAR_H / 2), (eb.x, eb.y, z + PAR_H / 2), th, PAR_H, PAR_M, 0.1)
        mb.beam((ea.x, ea.y, z + PAR_H + 0.22), (eb.x, eb.y, z + PAR_H + 0.22), th + 0.35, 0.45, "Stone_SG_Trim", 0.08)
    posts = [Vector(p) for p in pts]
    for i, p in enumerate(posts):
        if any((p - Vector(q)).length < r for q, r in skip):
            continue
        q = Vector(p)
        if i == 0:
            q += (Vector(posts[1]) - Vector(posts[0])).normalized() * (post / 2 + 0.16)
        elif i == len(posts) - 1:
            q += (Vector(posts[-2]) - Vector(posts[-1])).normalized() * (post / 2 + 0.16)
        _post(mb, q.x, q.y, z, post, lamp=(i in lit))
    for p in extra:
        _post(mb, p[0], p[1], z, post, lamp=(len(p) > 2 and p[2]))


def stair_wall(mb, s):
    """mureta inclinada de cada lado da escadaria (faz o banzo): face interna em |x| = 9 (= guarda do sg_col)"""
    ya, yb = L.ENTRY_STAIR[1], L.ENTRY_STAIR_Y1          # -206 .. -188
    ta, tb = PAR_Z + PAR_H + 0.35, P1 - 0.35 + PAR_H + 0.35
    x0, x1 = sorted((s * HW, s * (HW + 1.4)))
    yz_prism(mb, x0, x1, [(ya, DECK - 1.5), (yb, DECK - 1.5), (yb, tb), (ya, ta)], PAR_M)
    xm = s * (HW + 0.7)
    mb.beam((xm, ya - 0.2, ta + 0.2), (xm, yb + 0.2, tb + 0.2), 1.75, 0.45, "Stone_SG_Trim", 0.08)
    # cinta de fiadas na face externa (le como alvenaria de arrimo): obsidiana (faixa nobre), nao cantaria clara
    for zz in (DECK + 1.0, DECK + 4.2):
        mb.box2((min(x0, x1) - (0.12 if s < 0 else 0), ya, zz), (max(x0, x1) + (0.12 if s > 0 else 0), yb, zz + 0.35),
                "Stone_SG_Obsidian", 0.0)
    # pilaretes COM LANTERNA em pares: pe (no patio), 2 no lance (tercos, ~5,8 como o ritmo da ponte) e topo (calcada)
    _post(mb, s * (HW + 0.8), ya + 0.4, PAR_Z, 1.6, PAR_H + 1.3, lamp=True)
    _post(mb, s * (HW + 0.8), yb - 0.6, P1 - 0.35, 1.6, PAR_H + 1.3, lamp=True)
    y_a, y_b = ya + 0.4, yb - 0.6
    for k in (1, 2):
        yy = y_a + (y_b - y_a) * k / 3.0
        zcap = ta + (tb - ta) * (yy - ya) / (yb - ya) + 0.2 + 0.225        # topo da capa inclinada nesse ponto
        _post(mb, s * (HW + 0.8), yy, zcap - 2.4, 1.6, 2.4 + 0.75, lamp=True)


def parapets():
    mb = MB("SG_Ent_Parapets", "18_ENTRY", random.Random(3102), detail="near")
    xh = L.ENTRY_HIGH[2]                   # 12
    xl = L.ENTRY_LOW[2]                    # 13
    for s in (-1, 1):
        skipA = [((s * PORTICO_A["xc"], PORTICO_A["y"]), 4.0)]
        # ponte -> canto sul do patio -> lateral do patio -> canto norte (pe da escada)
        # pilaretes dos pilares da ponte e da cabeceira (canto ponte -> patio) levam lanterna
        parapet_run(mb, [(s * (HW + 0.6), Y0), (s * (HW + 0.6), Y1 - 0.6), (s * (xl + 0.6), Y1 - 0.6),
                         (s * (xl + 0.6), L.ENTRY_STAIR[1] + 0.5), (s * (HW + 1.4), L.ENTRY_STAIR[1] + 0.5)],
                    PAR_Z, extra=[(s * (HW + 0.6), cy, True) for cy in PIERS],
                    skip=skipA + [((s * (HW + 1.4), L.ENTRY_STAIR[1] + 0.5), 1.0)], lit=(1,))
        stair_wall(mb, s)
        # calcada alta: borda sul (ao lado do topo da escada) + lateral ate a praca (o pilarete do fim, na boca da
        # praca, leva lanterna: fecha o corredor)
        skipB = [((s * PORTICO_B["xc"], PORTICO_B["y"]), 4.4), ((s * (HW + 1.4), L.ENTRY_STAIR_Y1 - 0.6), 1.0)]
        parapet_run(mb, [(s * (HW + 1.4), L.ENTRY_STAIR_Y1 - 0.6), (s * (xh + 0.6), L.ENTRY_STAIR_Y1 - 0.6),
                         (s * (xh + 0.6), L.P1_POLY[3][1])], P1 - 0.35, skip=skipB, lit=(2,))
    # RITMO DE LANTERNAS (referencia v2/v3): pares de lanternas douradas da ordem a ~5,6 na ponte (pedestais entre os
    # pilaretes com lanterna dos pilares -258 / -235,5 e da cabeceira -228,6), a ~10 na lateral do patio e da calcada
    # alta (o trecho -182 fica com a lanterna baixa do portico B). SO Neon (nenhuma luz real nova). As posicoes evitam
    # os pilaretes e os mastros dos estandartes.
    top_deck = PAR_Z + PAR_H + 0.445
    top_p1 = P1 - 0.35 + PAR_H + 0.445
    for s in (-1, 1):
        for yy in BRIDGE_LANTERNS:
            EM.lantern_pedestal(mb, mb, mb, (s * (HW + 0.6), yy, top_deck), 0.0, 0.9)
        for yy in (-221.5, -211.0):
            EM.lantern_pedestal(mb, mb, mb, (s * (xl + 0.6), yy, top_deck), 0.0, 0.9)
        for yy in (-170.0,):
            EM.lantern_pedestal(mb, mb, mb, (s * (xh + 0.6), yy, top_p1), 0.0, 0.9)
        bridge_banner(mb, s, top_deck)
    return mb.finish()


# ponte: pedestais de lanterna entre os pilaretes (ritmo ~5,6) e o par de estandartes no meio do vao
BRIDGE_LANTERNS = (-252.4, -241.1)
BRIDGE_BANNER_Y = -246.75


def bridge_banner(mb, s, top_deck):
    """mastro de ferro negro sobre o parapeito da ponte (soco de obsidiana na capa) com o estandarte da ordem de debrum
    dourado pendurado a frente, encarando o SUL (quem chega da Ilha 2). O pano fica acima de 4,5 do tabuleiro (so
    visual, sem colisao; a guarda do sg_col segue na face do parapeito)."""
    x, y = s * (HW + 0.6), BRIDGE_BANNER_Y
    z = top_deck
    mb.box((1.7, 1.7, 0.55), (x, y, z + 0.275), (0, 0, 0), "Stone_SG_Obsidian", 0.06)
    mb.box((1.3, 1.3, 0.35), (x, y, z + 0.725), (0, 0, 0), "Stone_SG_Violet", 0.0)
    mb.cyl(0.22, 12.4, (x, y, z + 0.9 + 6.2), (0, 0, 0), "Metal_SG_BlackIron", n=8, r2=0.16, bevel=0.0)
    mb.box((0.55, 0.55, 0.3), (x, y, z + 12.9), (0, 0, 0), EM.GOLD, 0.0)
    SL.spire(mb, (x, y), 0.34, z + 13.05, 1.3, "Metal_SG_Silver", n=4)
    EM.banner(mb, mb, mb, mb, (x, y - 0.36, z + 12.3), -math.pi / 2, 2.6, 8.0, trim=EM.GOLD)


def stair():
    mb = MB("SG_Ent_Stair", "18_ENTRY", random.Random(3103), detail="near")
    # v3: degraus um valor mais escuros (Stone_SG_Castle); o focinho vira Stone_SG_Block (le o degrau sem clarear o
    # lance inteiro): a cantaria clara fica so nos remates das muretas
    SL.plan_stair(mb, "Entry", m="Stone_SG_Castle", side_m="Stone_SG_Castle", stringers=False)
    # focinho em cada degrau (le a escada de longe, como na concept); rente ao piso do degrau
    foot, deg, w, n, tread, g = L.stair_frame("Entry")
    rise = (L.STAIR_TOP_Z["Entry"] - foot[2]) / n
    for i in range(n):
        y = foot[1] + tread * i - 0.075 + 0.22
        mb.box((w - 0.2, 0.44, 0.14), (foot[0], y, foot[2] + rise * (i + 1) - 0.05), (0, 0, 0), "Stone_SG_Block", 0.0)
    return mb.finish()


# ------------------------------------------------------------------ porticos
def lancet(mb, F, yo, w, z0, z1, m="Stone_SG_Trim"):
    """janela cega ogival em relevo (moldura clara) numa face do fuste; local +Y = normal da face"""
    t = 0.3
    for sg in (-1, 1):
        mb.box((t, 0.24, z1 - z0), F.p(sg * w / 2, yo, (z0 + z1) / 2), F.r(), m, 0.0)
        mb.beam(F.p(sg * w / 2, yo, z1 - 0.1), F.p(0.0, yo, z1 + w * 0.85), 0.24, t, m, 0.0)
    mb.box((w + 0.5, 0.34, 0.3), F.p(0, yo, z0), F.r(), m, 0.0)


def lantern(mb, x, y, z, tag):
    """lanterna baixa: pedestal de pedra + gaiola de ferro com vidro quente + chapeu de 4 aguas"""
    mb.box((1.5, 1.5, 1.9), (x, y, z + 0.95), (0, 0, 0), "Stone_SG_Castle", 0.1)
    mb.box((1.8, 1.8, 0.3), (x, y, z + 2.05), (0, 0, 0), "Stone_SG_Trim", 0.06)
    zc = z + 2.95
    mb.box((1.3, 1.3, 0.2), (x, y, zc - 0.75), (0, 0, 0), "Metal_SG_Iron", 0.0)
    mb.box((0.95, 0.95, 1.3), (x, y, zc), (0, 0, 0), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.16, 0.16, 1.5), (x + sx * 0.56, y + sy * 0.56, zc), (0, 0, 0), "Metal_SG_Iron", 0.0)
    mb.cyl(1.05, 0.75, (x, y, zc + 1.05), (0, 0, math.pi / 4), "Metal_SG_Iron", 4, r2=0.18, bevel=0.0)
    mb.box((0.26, 0.26, 0.5), (x, y, zc + 1.6), (0, 0, math.pi / 4), "Metal_SG_Silver", 0.0)
    light("L_SGEnt_Portico%s_Lantern" % tag, "POINT", (x, y, zc), 320.0, WARM, 0.4)


def pylon(mb, P, side):
    """um pilar do portico P no lado side (-1 oeste, +1 leste)"""
    xc, y, z, s, H = side * P["xc"], P["y"], P["z"], P["s"], P["H"]
    pl = s + 0.8
    apron = 2.2
    deep = 3.0 if P["name"] == "A" else 8.0               # o B passa da borda da calcada: base desce ate o terreno
    # plinto com avental na frente (sul) que leva a lanterna
    mb.box2((xc - pl / 2, y - pl / 2 - apron, z - deep), (xc + pl / 2, y + pl / 2, z + 0.7), "Stone_SG_Block", 0.12)
    mb.box2((xc - pl / 2 - 0.12, y - pl / 2 - apron - 0.12, z + 0.7), (xc + pl / 2 + 0.12, y + pl / 2 + 0.12, z + 1.0),
            "Stone_SG_Trim", 0.08)
    # base + chanfro de assento
    mb.box((s + 0.6, s + 0.6, 2.4), (xc, y, z + 2.2), (0, 0, 0), "Stone_SG_Castle", 0.15)
    FP.frustum(mb, (xc, y, z + 3.4), s + 0.6, s + 0.6, s, s, 0.6, "Stone_SG_Trim")
    zt = z + 4.0 + H
    mb.box((s, s, H), (xc, y, z + 4.0 + H / 2), (0, 0, 0), "Stone_SG_Castle", 0.15)
    # frisos (meio e topo) + cornija
    zm = z + 4.0 + H * 0.4
    mb.box((s + 0.4, s + 0.4, 0.5), (xc, y, zm), (0, 0, 0), "Stone_SG_Trim", 0.08)
    mb.box((s + 1.2, s + 1.2, 0.9), (xc, y, zt + 0.45), (0, 0, 0), "Stone_SG_Trim", 0.12)
    # coroa: bloco + gabletes nas 4 faces + pinaculos nos cantos + agulha navy + remate de prata
    cs = s - 0.2
    mb.box((cs, cs, 2.2), (xc, y, zt + 0.9 + 1.1), (0, 0, 0), "Stone_SG_Castle", 0.1)
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
        mb._post(v0 + v1, "Stone_SG_Trim", None, 0, 1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = xc + sx * (cs / 2 - 0.1), y + sy * (cs / 2 - 0.1)
            mb.box((0.7, 0.7, 0.8), (px, py, zc + 0.4), (0, 0, 0), "Stone_SG_Trim", 0.0)
            SL.spire(mb, (px, py), 0.5, zc + 0.8, 1.8 + s * 0.25, "Stone_SG_Trim", n=4)
    SL.spire(mb, (xc, y), cs / math.sqrt(2.0) * 0.92, zc, P["spire"], "Roof_SG_Navy", n=4)
    ztip = zc + P["spire"]
    mb.cyl(0.13, 1.4, (xc, y, ztip + 0.4), (0, 0, 0), "Metal_SG_Silver", 6, bevel=0.0)
    mb.cyl(0.42, 0.7, (xc, y, ztip + 1.15), (0, 0, 0), "Metal_SG_Silver", 4, r2=0.02, bevel=0.0)
    mb.cyl(0.42, 0.5, (xc, y, ztip + 0.55), (math.pi, 0, 0), "Metal_SG_Silver", 4, r2=0.02, bevel=0.0)
    # face SUL: estandarte DA ORDEM (sg_emblem.banner: roxo profundo, barra negra, prata, emblema) numa verga de ferro
    # negro presa ao fuste por 2 bracos
    yb = y - (s / 2 + 0.55)
    EM.banner(mb, mb, mb, mb, (xc, yb, zt - 0.9), -math.pi / 2, P["bw"], P["bh"], trim=EM.GOLD)
    for sg in (-1, 1):
        mb.beam((xc + sg * (P["bw"] / 2 + 0.1), y - s / 2 + 0.1, zt - 0.9), (xc + sg * (P["bw"] / 2 + 0.1), yb, zt - 0.9),
                0.22, 0.22, "Metal_SG_BlackIron", 0.0)
    # face interna (para o eixo) e face norte: janela cega ogival
    Fi = Frame(xc, y, 0.0, math.pi / 2 if side > 0 else -math.pi / 2)     # local +Y -> mundo -side*X (eixo)
    lancet(mb, Fi, s / 2 + 0.08, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    lancet(mb, Fi, s / 2 + 0.08, s * 0.42, z + 5.0, zm - 1.4 - s * 0.36)
    Fn = Frame(xc, y, 0.0, 0.0)
    lancet(mb, Fn, s / 2 + 0.08, s * 0.42, zm + 1.2, zt - 2.4 - s * 0.36)
    # lanterna baixa quente ao pe (no avental do plinto)
    lantern(mb, xc, y - pl / 2 - apron / 2 - 0.1, z + 1.0, P["name"] + ("_W" if side < 0 else "_E"))
    # colisao propria: fuste (inteiro) + plinto/lanterna (baixo). Face interna >= 9,2 do eixo
    col_box2("SG_EntPortico", (xc - (s + 0.6) / 2, y - (s + 0.6) / 2, z), (xc + (s + 0.6) / 2, y + (s + 0.6) / 2,
                                                                          zt + 1.0))
    col_box2("SG_EntPortico", (xc - pl / 2, y - pl / 2 - apron, z), (xc + pl / 2, y + pl / 2, z + 5.2))


def lintel_b(mb):
    """verga do portico B (o portao da ordem): viga de obsidiana entre os fustes, logo abaixo das cornijas, com filete
    violeta, cornija clara e o medalhao da ordem (sg_emblem.plaque) no meio, nas duas faces. Vao livre de 23,7."""
    P = PORTICO_B
    y, z, s = P["y"], P["z"], P["s"]
    xi = P["xc"] - s / 2 + 0.1                        # entra 0,1 no fuste
    zt = z + 4.0 + P["H"]
    z0, z1 = zt - 2.3, zt - 0.05
    dep = s * 0.6
    mb.box2((-xi, y - dep / 2, z0), (xi, y + dep / 2, z1), "Stone_SG_Obsidian", 0.0)
    mb.box2((-xi, y - dep / 2 - 0.12, z0 - 0.18), (xi, y + dep / 2 + 0.12, z0 + 0.06), "Stone_SG_Violet", 0.0)
    mb.box2((-xi, y - dep / 2 - 0.25, z1), (xi, y + dep / 2 + 0.25, z1 + 0.5), "Stone_SG_Trim", 0.0)
    for sgn in (-1, 1):
        c = (0.0, y + sgn * (dep / 2 + 0.3), (z0 + z1) / 2 - 0.05)
        EM.plaque(mb, mb, mb, mb, c, sgn * math.pi / 2, 1.0)


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
