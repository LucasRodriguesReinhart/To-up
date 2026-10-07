# sg_court - VESTIR / PATIO-JARDIM do castelo e JARDIM-MIRANTE da Ilha 3 (Shadow Garden), PLANTA v4 (onda 2, agente
# do jardim, 2026-09-30). Roda ANTES do sg_veg (zona dressing). Prefixo SG_Prop_ (pedra, 09_PROPS) e SG_Veg_Gdn_
# (plantas, 10_VEGETATION).
# Pedido do usuario (jogando): "melhore a ambientacao do jardim, ta parecendo uma maquete na frente do castelo" e "voce
# spamou muita grama". Causas da maquete (PLANO 2): tudo na mesma altura, sebes de brinquedo iguais num retangulo
# preto chapado, espacamento uniforme e nada com escala maior que o jogador. O patio (200 x 74) vira um JARDIM-SALA:
#   1. CHAO todo do sg_court (o terreno desce 0,45 no patio: sg_terrain.court_garden_areas): eixo nobre de 20 em lajes
#      de marmore negro com o fio violeta baixo, CASCALHO de bordas irregulares (travessias nas rotas do QA, anel em
#      volta dos gramados e dos espelhos, roda da arvore), GRAMA no resto e terra nos canteiros;
#   2. 2 GRAMADOS REBAIXADOS 1,2 (o terreno recorta o topo: sg_terrain.COURT_LAWNS) com murete de cantaria, capa em
#      pecas e degraus nas 2 pontas (pilaretes com remate);
#   3. 2 ESPELHOS D'AGUA de 32 x 20 entre a travessia e a fachada: bacia de pedra estanque (fundo escuro; a agua e do
#      Roblox pelos WATER_Court_L/R, que o build reposiciona sobre a bacia real);
#   4. MASSAS DE ALTURA: sebes ALTAS (3-4, lances de altura variada) fechando as laterais e na frente da fachada,
#      sebes medias em L nas quinas dos espelhos, cones de teixo nos degraus, bolas de buxo nas estatuas, flores na
#      frente em DERIVAS, 2 ARVORES-MARCO de 34 (teixo de copa alta) com banco circular embaixo;
#   5. trepadeiras na face interna da muralha, estatuas da ordem no pe do porche, lanterna SO no no (cruzamento).
# JARDIM-MIRANTE (P3 leste, no lugar da antiga portaria): terraco de lajes em aneis, balaustrada na borda da vista,
# banco em exedra, a arvore velha da lua inclinada para a vista e flores; os 3 pinheiros vem do sg_veg (grupo Mirante).
# Historico da v3 (caminho da ordem no P1/P2, parterre, obeliscos): git, sg_court.py ate o commit 5329773. O eixo no
# P1/P2 agora e da vila (sg_village.AXIS_BY_VILLAGE).
# FINESSE 3B (2026-10-06, agente J): eixo nobre em lajes claras com borda e meio-fio (sem marmore negro nem fio Neon,
# 05.01), espelhos d'agua em bacia de cantaria com capa moldurada, pilares, patamar e bica (05.02), sebes em massas com
# coroamento ondulado e topiarias de 3 bolas (05.03), canteiro + banco circular das arvores-marco (05.04), canteiros de
# canto em chanfro, banco recuado e pisantes nos gramados (05.09), pergulas com banco nas pontas mortas (05.10), a
# estatua pequena saiu (06.03), guardiao encapuzado refeito para a escala 1,5 (hooded_figure) e a figura PROPRIA da
# fonte (fountain_figure, 02.03), muro-jardim/nichos/fonte/portico/miradouros no beco oeste (west_alley, 13.01),
# mirante com pergula, mesa, luneta e rosa dos ventos (13.04) e bordadura/soleiras/pilares no caminho dele (13.05).
# API usada por outros modulos (nao mudar): hooded_figure, fountain_figure, bez, _loft, _lathe_ax, RUNE_SEGS,
# OBELISK_RUNES, _glyph, COURT_LIGHTS.
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, fm_lib
import sg_layout as L
import sg_emblem as EM
import fm_parts as FP
import sg_veg as VEG                 # arvores (mesmas especies da ilha) + material do luar das folhas
import fm_veg_kit as VK
import sg_garden as GD               # kit de jardinagem (sebe, topiaria, flores, trepadeiras)

P1, P2, P3 = L.P1, L.P2, L.P3
COLL = "09_PROPS"
OBS = "Stone_SG_Obsidian"
MARB = "Stone_SG_MarbleBlack"
VIO = "Stone_SG_Violet"
TRIM = "Stone_SG_Trim"
BLOCK = "Stone_SG_Block"
SILVER = "Metal_SG_Silver"
IRON = "Metal_SG_BlackIron"
THREAD = "SG_VioletDeep_Glow"
RUNE = "SG_Rune_Glow"
CAP = "Stone_SG_TrimLow"
fm_lib.MATS.setdefault(CAP, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
WALLM = "Stone_SG_Castle_B"          # corpo do murete / bacia (a mesma dupla dos parapeitos da entrada)
RELM = "Stone_SG_Block_B"
THREAD_CASTLE = "SG_VioletSoft_Glow"
GRASS = "Grass_SG"
GRAVEL = GD.GRAVEL
SOIL = GD.SOIL
BOX = GD.LEAF_BOX
YEW = "Leaf_SG_Pine"                 # sebe alta / cones: o verde escuro das arvores (le teixo, nao buxo)
BLOOM = "Leaf_SGPropBloom"
fm_lib.MATS.setdefault(BLOOM, (fm_lib.S(98, 66, 132), 0.85, 0.0, 0, None, 0.08))

# ------------------------------------------------------------------ medidas do patio (planta v4)
FC = L.CASTLE_FORECOURT               # (-100, -13, 100, 61)
AXIS_HW = 10.0                         # eixo nobre de 20 (= rua do P3 da planta)
AXIS_Y = (L.WALL_Y1, 38.0)             # do portao (face interna da muralha) ao 1o degrau do porche (sg_castle)
PORCH = (-31.0, 38.0, 31.0, FC[3])     # degraus/estrado do porche (sg_castle): fora do chao do patio
LAWN_DEPTH = 1.2
MUR_T = 1.0                            # murete dos gramados (dentro do recorte do terreno)
STEP_Y = (2.6, 9.4)                    # vao dos degraus nas pontas dos gramados (y)
POOLS = [(-74.0, 32.0, -42.0, 52.0), (42.0, 32.0, 74.0, 52.0)]   # espelho (agua) 32 x 20
POOL_RIM = 1.2
POOL_LEVEL = P3 + 0.6
POOL_FLOOR = P3 + 0.1
TREES = [(-90.5, 2.5), (90.5, 2.5)]   # arvores-marco (teixo de 34) com banco circular
TREE_H = 34.0
STATUES = []        # FINESSE 3B (06.03): a estatua pequena (statue) saiu - os guardioes sao do sg_castle.guards
BEDS = [(-21.0, 34.5), (21.0, 34.5)]   # no lugar dela, so a deriva de flores ao pe do porche
NODE_LAMPS = []     # os postes do patio sao do sg_props (pontas dos degraus do porche, boca do beco oeste)
MED_C = (0.0, 20.0)
# arco de ferro do kit da vila no PE da escada do portao (rua do eixo do P2; a escada vai de y -40 a -23): entrada do
# recinto do castelo, lanternas quentes (so Neon). (x, y, z, meia-abertura) - a escada tem 20 de largura
GATE_ARCH = (0.0, -43.0, P2, 11.6)
# travessias (cascalho) = as rotas do QA CASTELO->PORTAO_DS (oeste) e CASTELO->JARDIM_MIRANTE (leste)
CROSS = {1: [(AXIS_HW - 0.5, 20.0), (60.0, 20.0), (101.5, 24.4)],
         -1: [(-(AXIS_HW - 0.5), 21.0), (-90.0, 30.0), (-101.5, 32.7)]}
CROSS_HW = 3.5
# sebes altas nas laterais: lances (y0, y1, h) e a abertura da travessia com 2 cones
SIDE_HEDGE = {1: [(-10.6, -3.5, 4.6), (-3.5, 5.0, 5.6), (5.0, 11.6, 5.0), (11.6, 16.0, 4.3),
                  (32.6, 40.0, 4.2), (40.0, 47.2, 5.3), (47.2, 53.0, 4.7)],
              -1: [(-10.6, -2.0, 4.8), (-2.0, 7.0, 5.5), (7.0, 15.4, 4.7), (15.4, 24.4, 4.2),
                   (41.0, 46.8, 4.6), (46.8, 53.0, 5.4)]}
SIDE_CONES = {1: (17.8, 30.8), -1: (26.2, 39.4)}
SIDE_X = 98.0
FACADE_HEDGE = [(35.0, 46.0, 3.6), (46.0, 57.5, 3.0), (57.5, 69.5, 4.1), (69.5, 81.5, 3.3), (81.5, 93.5, 4.3)]
FACADE_HEDGE_Y = 56.6
# arbustos (massa media entre a sebe alta e as flores): (x, y) por lado (x > 0; o oeste espelha)
SHRUBS = [(95.0, 1.5), (95.2, 13.0), (95.0, 42.5), (38.5, 54.2), (53.0, 54.0), (74.0, 54.3), (90.0, 53.9)]
VIOLET = (0.62, 0.42, 1.0)
COURT_LIGHTS = [("Court_Violet", (0.0, 30.5, P3 + 7.0), 420.0, VIOLET, 0.6)]
# jardim-mirante
MIR = L.MIRANTE_E                      # (132, 170, 16)
MIR_VIEW = (-72.0, 72.0)               # arco da balaustrada (graus; 0 = leste, a vista)
MIR_EXEDRA = (130.0, 230.0, 12.4)      # arco do banco em exedra (graus) e raio
MIR_TREE = (125.5, 184.0)              # a arvore velha da lua (inclinada para leste, para a vista)

CAMS = {
    "CAM_SGCourt_PH_Gate": ((0.0, -11.0, P3 + 5.2), (0.0, 40.0, P3 + 9.0), 20),
    "CAM_SGCourt_PH_GateDiag": ((-6.0, -4.5, P3 + 5.2), (62.0, 26.0, P3 + 5.0), 22),
    "CAM_SGCourt_PH_Door": ((8.0, 35.0, P3 + 5.6), (-46.0, 2.0, P3 + 3.0), 22),
    "CAM_SGCourt_PH_Lawn": ((24.0, 22.5, P3 + 5.2), (78.0, 2.0, P3 + 2.0), 22),
    "CAM_SGCourt_PH_GateArch": ((4.0, -78.0, P2 + 5.2), (0.0, -30.0, P2 + 11.0), 22),
    "CAM_SGCourt_High": ((0.0, -60.0, P3 + 150.0), (0.0, 24.0, P3), 20),
    "CAM_SGCourt_Top": ((0.0, 23.0, P3 + 230.0), (0.0, 24.0, P3), 18),
    "CAM_SGCourt_CU_Steps": ((25.5, 15.5, P3 + 3.6), (33.0, 4.0, P3 - 0.8), 24),
    "CAM_SGCourt_CU_Bed": ((27.0, 25.0, P3 + 3.2), (21.0, 33.0, P3 + 1.0), 24),
    "CAM_SGCourt_Tree": ((58.0, 16.0, P3 + 5.2), (90.0, 3.0, P3 + 9.0), 22),
    "CAM_SGCourt_Pool": ((30.0, 24.0, P3 + 5.2), (64.0, 46.0, P3 + 3.0), 22),
    "CAM_SGMir_PH": ((133.0, 142.0, P3 + 5.2), (136.0, 176.0, P3 + 3.5), 20),
    "CAM_SGMir_View": ((120.0, 166.0, P3 + 5.2), (190.0, 176.0, P3 + 2.0), 22),
    "CAM_SGMir_High": ((186.0, 128.0, P3 + 42.0), (130.0, 172.0, P3), 22),
    # FINESSE 3B (agente J): copias das CAM_A3_* da auditoria (o studio nao as cria; olho a 5,5)
    "CAM_A3_05_Patio_Caminho": ((3.0, 2.0, P3 + 5.5), (0.0, 30.0, P3), 22),
    "CAM_A3_05_Patio_W": ((-18.0, 8.0, P3 + 5.5), (-92.0, 30.0, P3 + 4.0), 20),
    "CAM_A3_05_Patio_E": ((18.0, 8.0, P3 + 5.5), (92.0, 30.0, P3 + 4.0), 20),
    "CAM_A3_05_Patio_Alto": ((0.0, -76.0, P3 + 72.0), (0.0, 25.0, P3), 20),
    "CAM_A3_06_Guardas": ((16.0, 44.0, P3 + 5.5), (-20.0, 58.0, P3 + 8.0), 20),
    "CAM_A3_06_Fachada_Patio": ((22.0, 8.0, P3 + 5.5), (0.0, 61.0, P3 + 26.0), 18),
    "CAM_A3_13_Beco_W1": ((-88.0, 30.0, P3 + 5.5), (-150.0, 46.0, P3 + 6.0), 20),
    "CAM_A3_13_Beco_W2": ((-148.0, 96.0, P3 + 5.5), (-136.0, 200.0, P3 + 8.0), 20),
    "CAM_A3_13_Beco_W3": ((-136.0, 240.0, P3 + 5.5), (-118.0, 334.0, P3 + 6.0), 20),
    "CAM_A3_13_Mirante_Caminho": ((150.0, 0.0, P3 + 5.5), (140.0, 120.0, P3 + 5.0), 20),
    "CAM_A3_13_Mirante": ((133.0, 142.0, P3 + 5.5), (136.0, 176.0, P3 + 3.5), 20),
    "CAM_A3_13_Mirante_Vista": ((120.0, 166.0, P3 + 5.5), (190.0, 176.0, P3), 20),
    "CAM_A3_02_Fonte_CU": ((10.0, -237.0, L.P1 + 5.5), (0.0, -222.0, L.P1 + 5.0), 20),
    # vistas de trabalho do agente J: figuras de perto
    "CAM_SGJ_Guard_CU": ((-27.0, 31.0, P3 + 7.5), (-34.5, 50.0, P3 + 11.0), 26),
    "CAM_SGJ_Fount_CU": ((5.0, -232.0, L.P1 + 9.5), (0.0, -222.0, L.P1 + 11.5), 26),
}

# rotas extras: a volta pelos gramados (no cascalho), ate o banco da arvore, em volta do espelho e o terraco do mirante
EXTRA_ROUTES = {
    "COURT_ANEL_GRAMADO_L": ([(12.0, 18.0), (31.7, 17.4), (31.7, -4.3), (84.3, -4.3), (84.3, 12.0)], P3),
    "COURT_ANEL_GRAMADO_O": ([(-12.0, 18.0), (-31.7, 17.4), (-31.7, -4.3), (-84.3, -4.3), (-84.3, 12.0)], P3),
    "COURT_DEGRAUS_L": ([(31.7, 6.0), (34.5, 6.0), (40.0, 6.0)], P3),
    "COURT_BANCO_L": ([(60.0, 20.0), (85.0, 16.0), (86.0, 8.0)], P3),
    "COURT_BANCO_O": ([(-60.0, 26.0), (-85.0, 16.0), (-86.0, 8.0)], P3),
    "COURT_ESPELHO_L": ([(30.0, 22.0), (38.0, 28.2), (78.2, 28.2), (78.2, 52.0)], P3),
    "COURT_ESPELHO_O": ([(-30.0, 24.0), (-38.0, 28.6), (-78.2, 29.6), (-78.2, 52.0)], P3),
    "MIRANTE_TERRACO": ([(132.0, 152.0), (132.0, 168.0), (141.0, 170.0), (128.0, 176.0)], P3),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ utilidades de forma (API: bez)
def ngon(c, r, n, rot=0.0):
    return [(c[0] + r * math.cos(rot + 2 * math.pi * k / n), c[1] + r * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)]


def disc(mb, c, r, z0, z1, m, n=40):
    mb.prism(SL.ccw(ngon(c, r, n)), z0, z1, m)


def ring(mb, c, r0, r1, z0, z1, m, n=48):
    """anel (coroa circular) fechado de r0 a r1, de z0 a z1"""
    bm = mb.bm
    cx, cy = c
    ang = [2 * math.pi * k / n for k in range(n)]
    ob = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z0)) for a in ang]
    ot = [bm.verts.new((cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)) for a in ang]
    ib = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0)) for a in ang]
    it = [bm.verts.new((cx + r0 * math.cos(a), cy + r0 * math.sin(a), z1)) for a in ang]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((it[i], it[j], ib[j], ib[i]))
        bm.faces.new((ot[i], ot[j], it[j], it[i]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    mb._post(ob + ot + ib + it, m, None, 0, 1)


def bez(p0, p1, p2, p3, n):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out



# ------------------------------------------------------------------ figura da ordem, estatua, runas (API de outros modulos)
def _loft(mb, rows, m, cap0="ngon", cap1="ngon", strip=None):
    """casca por secoes (listas de pontos MUNDO com a mesma contagem; uma secao de 1 ponto = polo).
    cap: 'ngon' (secao convexa), 'fan' (leque pelo centroide: secao estrelada), 'strip' (secao = arco externo de
    strip+1 pontos + linha interna de volta com strip+1 pontos: costura em faixa) ou None"""
    import bmesh
    from mathutils import Vector
    bm = mb.bm
    V = [[bm.verts.new(Vector(p)) for p in r] for r in rows]
    faces = []
    for A, B in zip(V, V[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        n = max(len(A), len(B))
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                faces.append(bm.faces.new((A[0], B[i], B[j])))
            elif len(B) == 1:
                faces.append(bm.faces.new((A[i], A[j], B[0])))
            else:
                faces.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    for cap, R in ((cap0, V[0]), (cap1, V[-1])):
        if cap is None or len(R) < 3:
            continue
        if cap == "ngon":
            faces.append(bm.faces.new(R))
        elif cap == "fan":
            cen = sum((v.co for v in R), Vector()) / len(R)
            cv = bm.verts.new(cen)
            for i in range(len(R)):
                faces.append(bm.faces.new((R[i], R[(i + 1) % len(R)], cv)))
        elif cap == "strip":
            M = strip
            for i in range(M):
                faces.append(bm.faces.new((R[i], R[i + 1], R[2 * M + 1 - (i + 1)], R[2 * M + 1 - i])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post([v for r in V for v in r], m, None, 0, 1)


def _lathe_ax(mb, o, ax, prof, m, n=8, ph=0.0):
    """solido de revolucao em torno de um eixo qualquer (o = origem MUNDO, ax = direcao); prof = [(raio, dist)]"""
    from mathutils import Vector
    ax = Vector(ax).normalized()
    o = Vector(o)
    ref = Vector((0.0, 0.0, 1.0)) if abs(ax.z) < 0.9 else Vector((1.0, 0.0, 0.0))
    e1 = ax.cross(ref).normalized()
    e2 = ax.cross(e1).normalized()
    rows = []
    for r, d in prof:
        if r < 1e-5:
            rows.append([o + ax * d])
        else:
            rows.append([o + ax * d + (e1 * math.cos(ph + 2 * math.pi * i / n) + e2 * math.sin(ph + 2 * math.pi * i / n)) * r
                         for i in range(n)])
    _loft(mb, rows, m)


BLADE_OF = {TRIM: "Stone_SG_Block_B", "Stone_SG_TrimLow": "Stone_SG_Block_B",
            "Stone_SG_Castle_B": "Stone_SG_Floor", "Stone_SG_Castle": "Stone_SG_Floor"}


def _fsec(W, cx, cy, z, rx, ryf, ryb, n, folds=0, amp=0.0, ph=0.0, back=0.0):
    """secao de manto: elipse (frente ryf, costas ryb) com n pontos, o 1o na frente (+Y local); 'folds' PREGAS de
    amplitude amp somadas ao raio (crista larga, vale mais raso: pano pesado), 'back' = pregas mais fundas atras"""
    out = []
    for k in range(n):
        a = math.pi / 2 + 2 * math.pi * k / n
        ca, sa = math.cos(a), math.sin(a)
        ry = ryf if sa > 0 else ryb
        d = 0.0
        if folds:
            c = math.cos(folds * (a - math.pi / 2) + ph)
            d = amp * (c if c > 0 else 0.6 * c) * (1.0 + (back if sa < 0 else 0.0))
        out.append(W(cx + (rx + d) * ca, cy + (ry + d) * sa, z))
    return out


def _shell(mb, W, rows, tip, m, M=14, th=0.13, cap0="strip"):
    """casca de capuz/veu: arco aberto na frente (meia-abertura al, graus) com espessura th; tip = ponta (polo)"""
    secs = []
    for z, cy, rx, ry, al in rows:
        a0, a1 = math.radians(90.0 + al), math.radians(450.0 - al)
        outer = [W(rx * math.cos(a0 + (a1 - a0) * i / M), cy + ry * math.sin(a0 + (a1 - a0) * i / M), z)
                 for i in range(M + 1)]
        inner = [W((rx - th) * math.cos(a1 - (a1 - a0) * i / M), cy + (ry - th) * math.sin(a1 - (a1 - a0) * i / M), z)
                 for i in range(M + 1)]
        secs.append(outer + inner)
    secs.append([W(*tip)])
    _loft(mb, secs, m, cap0, None, strip=M)


def _drape(mb, W, rows, m, M=12, nf=3):
    """manto/capa nas COSTAS: arco externo (de +hw a -hw por tras) com PREGAS GRANDES (nf pregas de 4 amostras,
    amplitude crescendo para baixo) + linha interna reta; rows = (z, hw, yb, yi, amp)"""
    secs = []
    for z, hw, yb, yi, amp in rows:
        outer, inner = [], []
        for i in range(M + 1):
            ph = math.pi * i / M
            fold = amp * (1.0, 0.25, -0.8, 0.25)[i % 4] if 0 < i < M else 0.0
            outer.append(W((hw + fold) * math.cos(ph), yi - (yi - yb + fold) * math.sin(ph), z))
        for i in range(M + 1):
            inner.append(W(-hw * 0.92 + 1.84 * hw * i / M, yi + 0.02, z))
        secs.append(outer + inner)
    _loft(mb, secs, m, "strip", "strip", strip=M)


def _limb(mb, W, s, a, b, r0, r1, m, n=10, cuff=0.0):
    """membro/manga de a a b (local), raio r0 -> r1; cuff > 0 = punho de manga alargado na ponta"""
    from mathutils import Vector
    wa, wb = W(*a), W(*b)
    ax = wb - wa
    Ln = ax.length
    prof = [(r0 * s, 0.0)]
    if cuff:
        prof += [(r1 * s, Ln - 0.24 * s), (cuff * s, Ln - 0.04 * s), (cuff * 0.9 * s, Ln + 0.05 * s)]
    else:
        prof += [(r1 * s, Ln)]
    _lathe_ax(mb, wa, ax, prof, m, n)


def _ball(mb, W, s, c, r, m, n=8):
    o = W(c[0], c[1], c[2] - r)
    _lathe_ax(mb, o, (0.0, 0.0, 1.0), [(0.0, 0.0), (r * 0.8 * s, 0.35 * r * s), (r * s, r * s), (r * 0.8 * s, 1.65 * r * s),
                                       (0.0, 2.0 * r * s)], m, n)


def _fist(mb, W, cx, cy, zh, m, hx=0.19, hy=0.18):
    """manopla/mao fechada (secoes chanfradas, nos dos dedos saltando na frente)"""
    def fs(z, a, b, ch, kn=0.0):
        pts = [(-a + ch, -b), (a - ch, -b), (a, -b + ch), (a, b - ch), (a - ch, b + kn), (-a + ch, b + kn),
               (-a, b - ch), (-a, -b + ch)]
        return [W(cx + u, cy + v, z) for u, v in pts]
    _loft(mb, [fs(zh - 0.16, hx - 0.05, hy - 0.04, 0.05), fs(zh - 0.06, hx, hy, 0.06, 0.04),
               fs(zh + 0.09, hx, hy, 0.06, 0.04), fs(zh + 0.16, hx - 0.04, hy - 0.04, 0.05)], m)


def hooded_figure(mb, F, s, z0, body, void=OBS, kind="guard"):
    """a FIGURA da ordem: GUARDIAO ENCAPUZADO de pedra (guardas da porta do castelo, sg_castle.guards: s 1,5 ~ 11 de
    altura). Referencial F (local +Y = frente), escala s, z0 = pe da figura (local). Altura ~7,45 s.
    FINESSE 3B (agente J, 06.03/02.03): refeita para LER na escala 1,5 - silhueta de massas grandes e secoes de 24
    lados (nada faceta): TUNICA longa com 6 PREGAS fundas que crescem para a barra, CINTO com fivela, CAPA nas costas
    em 3 pregas grandes (base larga = silhueta heroica, mais funda que a tunica), ESPALDEIRAS em calota sobre a capa,
    mangas com punho alargado, as 2 MANOPLAS no punho da ESPADA fincada a frente (lamina com sulco, guarda curva com
    pontas em gota, pomo em disco), CAPUZ fundo em casca de espessura com a ponta caindo para tras e o VAZIO escuro
    do rosto recuado. Mesmo numero de tris da figura antiga (~1,9k).
    kind: 'guard' (com a espada) ou 'hood' (sem arma: as maos juntas na frente do cinto)."""
    def W(x, y, z):
        return F.p(x * s, y * s, z0 + z * s)
    blade_m = BLADE_OF.get(body, "Stone_SG_Floor")
    N = 24
    YS = 1.24                                            # plano da espada (local y): a frente da barra da tunica
    # ---- tunica (casca aberta embaixo: assenta no plinto) com pregas que crescem para baixo
    robe = ((0.00, 1.20, 0.92, 0.98, 0.15), (1.60, 1.03, 0.76, 0.84, 0.11), (3.05, 0.87, 0.60, 0.68, 0.06),
            (3.80, 0.80, 0.53, 0.60, 0.025), (4.55, 0.92, 0.60, 0.62, 0.015), (5.12, 1.04, 0.52, 0.56, 0.0),
            (5.48, 0.76, 0.44, 0.48, 0.0), (5.78, 0.42, 0.32, 0.36, 0.0))
    _loft(mb, [_fsec(W, 0.0, 0.0, z, rx, rf, rb, N, 6, amp, 0.0, 0.4) for z, rx, rf, rb, amp in robe], body, None, None)
    # ---- cinto (anel saliente) e fivela
    _loft(mb, [_fsec(W, 0.0, 0.0, z, 0.85, 0.58, 0.65, N) for z in (3.70, 3.93)], body, None, None)
    mb.box((0.36 * s, 0.1 * s, 0.32 * s), W(0.0, 0.60, 3.815), F.r(), blade_m, 0.0)
    # ---- botas (bicos sob a barra)
    for sg in (-1, 1):
        x = sg * 0.42
        t0 = [(-0.2, 0.62), (0.2, 0.62), (0.2, 1.02), (0.0, 1.18), (-0.2, 1.02)]
        t1 = [(-0.17, 0.62), (0.17, 0.62), (0.17, 0.9), (0.0, 1.0), (-0.17, 0.9)]
        _loft(mb, [[W(x + a, b, 0.0) for a, b in t0], [W(x + a, b, 0.3) for a, b in t1]], body)
    # ---- capa nas costas: 3 pregas grandes, base larga
    _drape(mb, W, ((5.62, 0.86, -0.52, -0.18, 0.0), (5.20, 1.20, -0.68, -0.20, 0.05),
                   (3.90, 1.26, -0.92, -0.30, 0.18), (2.00, 1.40, -1.14, -0.36, 0.34),
                   (0.04, 1.56, -1.36, -0.40, 0.46)), body, 16)
    # tabardo na frente (do cinto a barra, ponta em V): a linha vertical que a espada continua
    tab = [(-0.36, 3.66), (0.36, 3.66), (0.33, 1.20), (0.0, 0.86), (-0.33, 1.20)]
    def front(z):                                        # frente da tunica (crista da prega) na altura z
        for (za, _, fa, _, aa), (zb, _, fb, _, ab) in zip(robe, robe[1:]):
            if za <= z <= zb:
                t = (z - za) / (zb - za)
                return fa + aa + (fb + ab - fa - aa) * t
        return robe[-1][2]
    _loft(mb, [[W(a, front(b) - 0.02, b) for a, b in tab], [W(a, front(b) + 0.1, b) for a, b in tab]], body)
    # ---- espaldeiras em calota (sobre a capa)
    for sg in (-1, 1):
        o = W(sg * 0.98, -0.04, 5.16)
        ax = F.p(sg * 0.9, 0.0, 0.5) - F.p(0.0, 0.0, 0.0)
        _lathe_ax(mb, o, ax, [(0.50 * s, -0.30 * s), (0.58 * s, -0.08 * s), (0.52 * s, 0.14 * s), (0.34 * s, 0.30 * s),
                              (0.0, 0.38 * s)], body, 10)
    # ---- bracos: manga do ombro ao cotovelo, antebraco com punho alargado ate a manopla no punho da espada
    hands = {1: 4.02, -1: 3.62} if kind == "guard" else {1: 3.98, -1: 3.98}
    for sg in (-1, 1):
        J = (sg * 0.92, 0.02, 5.00)
        E = (sg * 0.98, 0.40, 4.08)
        zh = hands[sg]
        hx = sg * 0.07 if kind == "guard" else sg * 0.2
        Wr = (hx + sg * 0.22, YS - 0.1 if kind == "guard" else 0.74, zh)
        _limb(mb, W, s, J, (E[0], E[1] + 0.04, E[2] - 0.04), 0.29, 0.27, body, 10)     # a manga cobre o cotovelo
        _limb(mb, W, s, E, Wr, 0.25, 0.25, body, 10, cuff=0.36)
        _fist(mb, W, hx, YS if kind == "guard" else 0.8, zh, body)
    # ---- capuz fundo (casca) com a ponta caida para tras + o vazio do rosto
    _shell(mb, W, ((5.40, -0.10, 0.80, 0.66, 20.0), (5.95, -0.04, 0.70, 0.68, 38.0), (6.50, -0.04, 0.65, 0.68, 42.0),
                   (6.94, -0.12, 0.56, 0.62, 34.0), (7.22, -0.30, 0.40, 0.50, 18.0)), (0.0, -0.74, 7.12), body, 14,
           0.13)
    _loft(mb, [_fsec(W, 0.0, -0.04, 5.62, 0.42, 0.32, 0.40, 10), _fsec(W, 0.0, -0.02, 6.45, 0.47, 0.38, 0.46, 10),
               _fsec(W, 0.0, -0.08, 6.95, 0.35, 0.30, 0.36, 10), [W(0.0, -0.12, 7.12)]], void)
    if kind != "guard":
        return
    # ---- ESPADA fincada a frente
    def blade_sec(z, hw, t, groove=True):
        g = 0.45 if groove else 1.0
        pts = [(-hw, 0.0), (-0.4 * hw, t), (0.0, g * t), (0.4 * hw, t), (hw, 0.0), (0.4 * hw, -t), (0.0, -g * t),
               (-0.4 * hw, -t)]
        return [W(a, YS + b, z) for a, b in pts]
    _loft(mb, [[W(0.0, YS, -0.10)], blade_sec(0.40, 0.15, 0.05, False), blade_sec(2.78, 0.21, 0.06),
               blade_sec(3.04, 0.21, 0.06, False)], blade_m, None, "fan")
    gp = []
    for i in range(9):
        x = -0.66 + 1.32 * i / 8
        gp.append(W(x, YS, 3.12 - 0.28 * (abs(x) / 0.66) ** 2))
    nrm = F.p(0.0, 1.0, 0.0) - F.p(0.0, 0.0, 0.0)
    mb.sweep(gp, [(0.0, 0.1 * s), (0.08 * s, 0.0), (0.0, -0.1 * s), (-0.08 * s, 0.0)], blade_m, True, None,
             up=tuple(nrm))
    for sg in (-1, 1):
        tip = W(sg * 0.66, YS, 2.86)
        _lathe_ax(mb, tip, W(sg * 0.70, YS, 2.62) - tip, [(0.0, -0.04 * s), (0.1 * s, 0.05 * s), (0.11 * s, 0.14 * s),
                                                         (0.0, 0.28 * s)], blade_m, 6)
    esc = [(-0.14, 2.96), (0.14, 2.96), (0.17, 3.24), (0.0, 3.34), (-0.17, 3.24)]
    _loft(mb, [[W(a, YS - 0.13, b) for a, b in esc], [W(a, YS + 0.13, b) for a, b in esc]], blade_m)
    EM._lathe(mb, tuple(W(0.0, YS, 0.0)), [(0.085 * s, 3.22 * s), (0.11 * s, 3.32 * s), (0.09 * s, 3.4 * s),
                                           (0.09 * s, 4.22 * s), (0.11 * s, 4.3 * s)], blade_m, 8, math.pi / 8)
    EM._lathe(mb, tuple(W(0.0, YS, 0.0)), [(0.08 * s, 4.28 * s), (0.2 * s, 4.38 * s), (0.23 * s, 4.5 * s),
                                           (0.19 * s, 4.62 * s), (0.0, 4.7 * s)], blade_m, 8, math.pi / 8)


def fountain_figure(mb, F, s, z0):
    """FINESSE 3B (agente J, 02.03): a figura PROPRIA da fonte da praca - a PORTADORA DA AGUA: moca de pedra CLARA
    (Stone_SG_TrimLow, o mesmo material do coroamento) de veu, tunica cintada alta e manto nas costas, com o CANTARO
    no ombro esquerdo inclinado para a frente (a boca para a taca: verte), a mao esquerda erguida sob o fundo e a
    direita no gargalo. Nada de capuz escuro nem espada: nao repete os guardioes da porta. Mesma assinatura do
    sg_village.fountain_figure: F (local +Y = frente), escala s (0,88 -> ~6,4 de altura), pe em z0 sobre o disco de
    raio 1,02 (a barra cabe em 0,80 s). <= 2k tris."""
    from mathutils import Vector
    body, void = "Stone_SG_TrimLow", OBS

    s = s * 1.07                                         # ~6,4 de altura com s 0,88 (a barra cabe no disco de 1,02)

    def W(x, y, z):
        return F.p(x * s, y * s, z0 + z * s)
    N = 24
    # tunica longa (barra estreita: cabe no disco de 1,02), cintura alta, busto, ombros caidos
    robe = ((0.00, 0.86, 0.72, 0.76, 0.10), (0.30, 0.80, 0.66, 0.70, 0.09), (1.50, 0.66, 0.52, 0.58, 0.06),
            (2.70, 0.60, 0.44, 0.50, 0.04), (3.35, 0.62, 0.44, 0.50, 0.02), (3.98, 0.45, 0.34, 0.38, 0.01),
            (4.50, 0.53, 0.43, 0.37, 0.0), (4.98, 0.60, 0.34, 0.34, 0.0), (5.30, 0.44, 0.27, 0.29, 0.0),
            (5.55, 0.19, 0.17, 0.19, 0.0))
    def hipx(z):                                         # contraposto: o quadril desloca para a direita
        return 0.07 * math.sin(math.pi * min(1.0, max(0.0, (z - 0.3) / 4.7)))
    _loft(mb, [_fsec(W, hipx(z), 0.02, z, rx, rf, rb, N, 7, amp, 0.0, 0.3) for z, rx, rf, rb, amp in robe], body,
          None, None)
    _loft(mb, [_fsec(W, hipx(z), 0.02, z, 0.54, 0.40, 0.42, N) for z in (4.12, 4.30)], body, None, None)   # cinta
    # o pe direito avancado (contraposto) sob a barra
    t0 = [(-0.15, 0.5), (0.15, 0.5), (0.15, 0.82), (0.0, 0.94), (-0.15, 0.82)]
    t1 = [(-0.12, 0.5), (0.12, 0.5), (0.12, 0.72), (0.0, 0.8), (-0.12, 0.72)]
    _loft(mb, [[W(0.26 + a, b, 0.0) for a, b in t0], [W(0.26 + a, b, 0.22) for a, b in t1]], body)
    # manto nas costas (do ombro a meia perna) em 3 pregas
    _drape(mb, W, ((5.30, 0.62, -0.38, -0.12, 0.0), (4.70, 0.80, -0.52, -0.14, 0.06), (3.20, 0.90, -0.70, -0.2, 0.14),
                   (1.10, 0.98, -0.90, -0.24, 0.2)), body, 12)
    # cabeca (oval) dentro do veu: o rosto le claro, sem o vazio escuro dos guardioes
    EM._lathe(mb, tuple(W(0.0, 0.06, 5.50)), [(0.14 * s, 0.0), (0.27 * s, 0.2 * s), (0.31 * s, 0.46 * s),
                                              (0.27 * s, 0.74 * s), (0.14 * s, 0.94 * s), (0.0, 1.0 * s)], body, 10)
    # veu: casca de abertura larga, caindo nos ombros
    _shell(mb, W, ((5.24, -0.10, 0.62, 0.50, 46.0), (5.75, -0.06, 0.45, 0.46, 60.0), (6.20, -0.02, 0.42, 0.45, 62.0),
                   (6.52, -0.06, 0.34, 0.38, 52.0), (6.70, -0.12, 0.2, 0.26, 34.0)), (0.0, -0.2, 6.78), body, 12, 0.1)
    # CANTARO a frente, a direita, inclinado para a taca: a boca para a frente e para baixo (verte), seguro pelas 2
    # maos (a direita sob o fundo erguido, a esquerda no gargalo) - le de baixo, da praca, em silhueta
    c = Vector((0.50, 0.66, 4.30))
    d = Vector((0.42, 0.50, -0.76)).normalized()
    foot = c - d * 0.86
    _lathe_ax(mb, W(*foot), W(*(foot + d)) - W(*foot),
              [(0.0, 0.0), (0.22 * s, 0.0), (0.27 * s, 0.09 * s), (0.22 * s, 0.2 * s), (0.48 * s, 0.58 * s),
               (0.52 * s, 0.86 * s), (0.4 * s, 1.14 * s), (0.18 * s, 1.36 * s), (0.16 * s, 1.52 * s),
               (0.26 * s, 1.64 * s), (0.18 * s, 1.7 * s), (0.0, 1.62 * s)], body, 12)
    neck = c + d * 0.62
    # bracos: direito com a mao sob o fundo do cantaro; esquerdo cruzando a frente ate o gargalo
    shR, elR, hdR = (0.60, -0.02, 5.02), (0.82, 0.30, 4.30), (0.40, 0.42, 4.92)
    shL, elL, hdL = (-0.60, -0.02, 5.02), (-0.50, 0.50, 4.30), (neck.x - 0.12, neck.y + 0.02, neck.z + 0.14)
    for sh, el, hd in ((shL, elL, hdL), (shR, elR, hdR)):
        _limb(mb, W, s, sh, el, 0.17, 0.15, body, 8)
        _ball(mb, W, s, el, 0.15, body, 6)
        _limb(mb, W, s, el, hd, 0.14, 0.12, body, 8, cuff=0.17)
        _ball(mb, W, s, hd, 0.13, body, 6)


# OVERHAUL 03 (03.05/15.03/16.07): a inscricao vira ENTALHE em pedra violeta SEM brilho dentro de um painel rebaixado
# com moldura; sequencia fixa (nada aleatorio).
# OVERHAUL 09 (2026-09-29, pedido da coordenacao): o ALFABETO UNICO da ilha foi REDESENHADO - o gancho em arco lia
# "r"/"L" a meia distancia. Agora sao RUNAS ANGULARES da ordem (inspiradas no futhark): haste vertical com ramos
# DIAGONAIS, sem curva de letra latina. Cada glifo = tracos ((u0, v0), (u1, v1)) numa caixa de 0,76 de altura
# (v de -0,38 a 0,38; u lateral). Usado aqui (obeliscos) e em sg_dungeon.rune (boca, marcos, portais, pisos).
_ST = ((0.0, -0.38), (0.0, 0.38))
RUNE_SEGS = (
    (_ST, ((0.0, 0.38), (0.24, 0.16)), ((0.0, 0.12), (0.24, -0.1))),                 # 0 dois ramos caindo a direita
    (_ST, ((0.0, 0.2), (0.22, 0.02)), ((0.22, 0.02), (0.0, -0.16))),                 # 1 espinho angular (thurs)
    (_ST, ((0.0, 0.38), (-0.24, 0.16)), ((0.0, 0.14), (-0.24, -0.08))),              # 2 dois ramos para baixo
    (_ST, ((0.0, -0.22), (-0.22, 0.06)), ((0.0, -0.22), (0.22, 0.06))),              # 3 garfo baixo, haste alta (algiz)
    (_ST, ((0.0, 0.22), (-0.22, -0.06)), ((0.0, 0.22), (0.22, -0.06))),              # 4 garfo alto invertido (yr)
    (_ST, ((0.0, 0.06), (-0.22, -0.12)), ((-0.22, -0.12), (0.0, -0.3))),              # 5 espinho baixo a esquerda
    (_ST, ((0.0, 0.38), (0.22, 0.2)), ((0.0, -0.12), (-0.22, -0.32))),               # 6 ramos opostos
    (_ST, ((0.0, 0.26), (0.24, 0.1)), ((0.24, 0.1), (0.24, -0.22))),                 # 7 gancho em angulo
    (((-0.17, -0.38), (-0.17, 0.38)), ((0.17, -0.38), (0.17, 0.38)),
     ((-0.17, 0.14), (0.17, -0.1))),                                                 # 8 duas hastes (hagal)
)
OBELISK_RUNES = (0, 3, 1, 5, 2)                  # a inscricao do obelisco (sequencia fixa)


def _glyph(mb, P, u0, zc, k, m):
    """runa k do alfabeto da ilha (RUNE_SEGS) em (u, z) da face P(u, t, z): tracos retos de secao 0,09 x 0,07"""
    sq = [(-0.045, -0.035), (0.045, -0.035), (0.045, 0.035), (-0.045, 0.035)]
    for (a0, b0), (a1, b1) in RUNE_SEGS[k % len(RUNE_SEGS)]:
        L_ = math.hypot(a1 - a0, b1 - b0)
        e = 0.03 / max(L_, 1e-6)                                  # ponta estendida: os tracos se encontram sem fresta
        a0, b0, a1, b1 = a0 - (a1 - a0) * e, b0 - (b1 - b0) * e, a1 + (a1 - a0) * e, b1 + (b1 - b0) * e
        mb.sweep([P(u0 + a0, 0.0, zc + b0), P(u0 + a1, 0.0, zc + b1)], sq, m, True, None, up=(0.0, 0.0, 1.0))


def obelisk(mb, x, y, z, face_yaw):
    """obelisco da ordem. Overhaul 03 (03.05): base em 3 MOLDURAS com perfil (plinto, toro, escocia, toro menor) e dado
    violeta; fuste com leve ENTASE (secao do meio 0,05 acima da reta) e filetes nas arestas; colar moldurado e
    piramidion de obsidiana com florao de prata; inscricao ENTALHADA (painel rebaixado + moldura + glifos em pedra
    violeta sem brilho) so na face que olha o eixo. A placa com emblema da base SAIU (16.02/12.11)."""
    from mathutils import Vector
    hw0, hw1, zs0, zs1 = 0.95, 0.6, z + 1.9, z + 14.2
    mb.box((3.6, 3.6, 0.45), (x, y, z + 0.175), (0, 0, 0), OBS, 0.08)
    FP.frustum(mb, (x, y, z + 0.4), 3.2, 3.2, 3.4, 3.4, 0.12, CAP)             # toro (sobe e volta)
    FP.frustum(mb, (x, y, z + 0.52), 3.4, 3.4, 3.1, 3.1, 0.12, CAP)
    mb.box((2.9, 2.9, 0.16), (x, y, z + 0.72), (0, 0, 0), OBS, 0.0)          # escocia (recuada)
    FP.frustum(mb, (x, y, z + 0.8), 2.9, 2.9, 3.05, 3.05, 0.09, CAP)          # toro menor
    FP.frustum(mb, (x, y, z + 0.89), 3.05, 3.05, 2.8, 2.8, 0.09, CAP)
    mb.box((2.8, 2.8, 0.62), (x, y, z + 1.29), (0, 0, 0), VIO, 0.06)          # dado
    FP.frustum(mb, (x, y, z + 1.6), 2.8, 2.8, 2.95, 2.95, 0.14, CAP)         # cornija do dado
    mb.box((2.95, 2.95, 0.1), (x, y, z + 1.79), (0, 0, 0), CAP, 0.0)
    FP.frustum(mb, (x, y, z + 1.84), 2.4, 2.4, 2.0, 2.0, 0.12, OBS)

    def hw(zz):
        f = (zz - zs0) / (zs1 - zs0)
        return hw0 + (hw1 - hw0) * f + 0.2 * f * (1.0 - f)                  # entase: +0,05 no meio
    rows = []
    for zz in (zs0, zs0 + (zs1 - zs0) * 0.33, zs0 + (zs1 - zs0) * 0.66, zs1):
        h_ = hw(zz)
        rows.append([Vector((x - h_, y - h_, zz)), Vector((x + h_, y - h_, zz)), Vector((x + h_, y + h_, zz)),
                     Vector((x - h_, y + h_, zz))])
    _loft(mb, rows, OBS)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pts = [(x + sx * hw(zz), y + sy * hw(zz), zz) for zz in (zs0 + 0.3, (zs0 + zs1) / 2, zs1 - 0.05)]
            mb.sweep(pts, [(0.18 * math.cos(2 * math.pi * i / 4 + math.pi / 4),
                            0.18 * math.sin(2 * math.pi * i / 4 + math.pi / 4)) for i in range(4)], OBS, True, None,
                     up=(1.0, 0.0, 0.0))
    # colar moldurado + piramidion de obsidiana (baixo) + florao de prata
    FP.frustum(mb, (x, y, zs1 - 0.02), 2 * hw1 + 0.1, 2 * hw1 + 0.1, 2 * hw1 + 0.44, 2 * hw1 + 0.44, 0.16, CAP)
    mb.box((2 * hw1 + 0.44, 2 * hw1 + 0.44, 0.12), (x, y, zs1 + 0.2), (0, 0, 0), CAP, 0.0)
    FP.frustum(mb, (x, y, zs1 + 0.26), 2 * hw1 + 0.2, 2 * hw1 + 0.2, 0.3, 0.3, 1.05, OBS)
    EM._lathe(mb, (x, y, zs1 + 1.22), [(0.14, 0.0), (0.2, 0.08), (0.11, 0.18), (0.24, 0.38), (0.17, 0.56),
                                       (0.07, 0.7), (0.0, 1.1)], SILVER, 6, math.pi / 6)
    for k in range(4):
        a = k * math.pi / 2
        front = abs(((a - face_yaw + math.pi) % (2 * math.pi)) - math.pi) < 0.1
        if not front:
            continue
        nx, ny = math.cos(a), math.sin(a)
        tx, ty = -ny, nx

        def P(u, t, zz):
            o = hw(zz) + t
            return (x + nx * o + tx * u, y + ny * o + ty * u, zz)
        # painel rebaixado: moldura de obsidiana saliente em volta do campo; os glifos = o fundo violeta do entalhe
        za, zb = z + 5.3, z + 12.9
        for su in (-1, 1):
            mb.sweep([P(su * 0.6, 0.0, za - 0.1), P(su * 0.6, 0.0, zb + 0.1)],
                     [(-0.1, 0.0), (0.1, 0.0), (0.1, 0.14), (-0.1, 0.14)], OBS, True, None, up=(nx, ny, 0.0))
        for zz in (za - 0.1, zb + 0.1):
            mb.sweep([P(-0.7, 0.0, zz), P(0.7, 0.0, zz)], [(0.0, -0.1), (0.14, -0.1), (0.14, 0.1), (0.0, 0.1)],
                     OBS, True, None, up=(0.0, 0.0, 1.0))
        for i, k in enumerate(OBELISK_RUNES):
            _glyph(mb, lambda u, t, zz: P(u, 0.01 + t, zz), -0.02, z + 6.2 + i * 1.45, k, VIO)
    col_box("SG_PropObelisk", (3.6, 3.6, 15.0), (x, y, z + 7.5))



# ------------------------------------------------------------------ contornos organicos (bordas irregulares do cascalho)
def _wob(t, ph, amp):
    """ruido suave ao longo do comprimento t (studs): 2 ondas lentas, nada de serrilha"""
    return amp * (0.6 * math.sin(t / 3.3 + ph) + 0.4 * math.sin(t / 1.9 + 2.1 * ph))


def round_rect(x0, y0, x1, y1, d, rc=None, n=5):
    """retangulo expandido de d com cantos arredondados (raio rc)"""
    rc = d if rc is None else rc
    X0, Y0, X1, Y1 = x0 - d, y0 - d, x1 + d, y1 + d
    pts = []
    for cx, cy, a0 in ((X1 - rc, Y0 + rc, -90.0), (X1 - rc, Y1 - rc, 0.0), (X0 + rc, Y1 - rc, 90.0),
                       (X0 + rc, Y0 + rc, 180.0)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + rc * math.cos(a), cy + rc * math.sin(a)))
    return pts


def wobble_closed(pts, amp, seed, step=2.2):
    """contorno fechado com a borda ondulada (para fora/dentro pela normal), amostrado a cada 'step'"""
    import sg_terrain as TER
    ph = (seed % 97) * 0.37
    out = []
    for i, (x, y, nx, ny) in enumerate(TER.resample_closed(pts, step)):
        w = _wob(i * step, ph, amp)
        out.append((x + nx * w, y + ny * w))
    return out


def wobble_ribbon(cl, hw, amp, seed, step=2.0):
    """faixa (caminho) ao longo da polilinha cl, meia-largura hw com as 2 bordas onduladas de forma independente"""
    pts = []
    for a, b in zip(cl, cl[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(round(ln / step)))
        for i in range(k):
            pts.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    pts.append(cl[-1])
    ph = (seed % 89) * 0.41
    L_, R_ = [], []
    acc = 0.0
    for i, p in enumerate(pts):
        if i:
            acc += math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
        q0 = pts[max(0, i - 1)]
        q1 = pts[min(len(pts) - 1, i + 1)]
        tx, ty = q1[0] - q0[0], q1[1] - q0[1]
        tl = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / tl, tx / tl
        e = 1.0 if 0 < i < len(pts) - 1 else 0.0
        wl = hw + e * _wob(acc, ph, amp)
        wr = hw + e * _wob(acc, ph + 1.7, amp)
        L_.append((p[0] + nx * wl, p[1] + ny * wl))
        R_.append((p[0] - nx * wr, p[1] - ny * wr))
    return L_ + list(reversed(R_))


def blob(cx, cy, rx, ry, seed, rot=0.0):
    import sg_terrain as TER
    return TER.blob(cx, cy, rx, ry, rot, seed, n=22, amp=0.12)


# ------------------------------------------------------------------ 1. o CHAO do patio (varredura: eixo, cascalho, terra, grama)
def lawn_rects():
    import sg_terrain as TER
    return list(TER.COURT_LAWNS)


def floor_layers():
    """(cortes, cascalho, terra) do patio em poligonos"""
    cuts = [SL.ccw([(-AXIS_HW, AXIS_Y[0] - 0.5), (AXIS_HW, AXIS_Y[0] - 0.5), (AXIS_HW, AXIS_Y[1]), (-AXIS_HW, AXIS_Y[1])]),
            [(PORCH[0], PORCH[1]), (PORCH[2], PORCH[1]), (PORCH[2], PORCH[3] + 1.0), (PORCH[0], PORCH[3] + 1.0)]]
    cuts += [[(a, b), (c, b), (c, d), (a, d)] for a, b, c, d in lawn_rects()]
    cuts += [[(a - POOL_RIM, b - POOL_RIM), (c + POOL_RIM, b - POOL_RIM), (c + POOL_RIM, d + POOL_RIM),
              (a - POOL_RIM, d + POOL_RIM)] for a, b, c, d in POOLS]
    gravel, soil = [], []
    for s in (-1, 1):
        gravel.append(wobble_ribbon(CROSS[s], CROSS_HW, 0.5, 11 + s))
        x0, y0, x1, y1 = [r for r in lawn_rects() if (r[0] > 0) == (s > 0)][0]
        gravel.append(wobble_closed(round_rect(x0, y0, x1, y1, 2.6, 2.0), 0.45, 21 + s))
        px0, py0, px1, py1 = [p for p in POOLS if (p[0] > 0) == (s > 0)][0]
        gravel.append(wobble_closed(round_rect(px0, py0, px1, py1 - 2.2, POOL_RIM + 2.4, 2.4), 0.4, 31 + s))
        tx, ty = TREES[0 if s < 0 else 1]
        gravel.append(blob(tx - s * 0.6, ty, 5.8, 5.2, 41 + s))
        # terra: pe da muralha, faixa da sebe da fachada, faixa das sebes laterais
        # (a roda da estatua fica em GRAMA: as flores nascem do gramado, nada de terra pelada no close)
        xa, xb = sorted((s * 37.5, s * 87.0))
        soil.append(wobble_closed([(xa, FC[1] - 0.5), (xb, FC[1] - 0.5), (xb, FC[1] + 3.2), (xa, FC[1] + 3.2)], 0.35,
                                  61 + s))
        xa, xb = sorted((s * 33.5, s * 99.0))
        soil.append(wobble_closed([(xa, FACADE_HEDGE_Y - 3.2), (xb, FACADE_HEDGE_Y - 3.2), (xb, FC[3] + 0.5),
                                   (xa, FC[3] + 0.5)], 0.35, 71 + s))
        xa, xb = sorted((s * (SIDE_X - 3.6), s * (FC[2] + 0.5)))
        soil.append(wobble_closed([(xa, FC[1] - 0.5), (xb, FC[1] - 0.5), (xb, FC[3] + 0.5), (xa, FC[3] + 0.5)], 0.3,
                                  81 + s))
    return cuts, gravel, soil


def court_floor():
    """o chao do patio inteiro (o terreno desce 0,45 aqui): faces de topo EXATAS na cota P3 por varredura (cascalho /
    terra / grama sem sobreposicao) + o eixo nobre (lajes com profundidade propria)"""
    import sg_terrain as TER
    mb = MB("SG_Prop_CourtFloor", COLL, random.Random(3601), detail="near")
    dom = [[(FC[0], FC[1]), (FC[2], FC[1]), (FC[2], FC[3]), (FC[0], FC[3])]]
    cuts, gravel, soil = floor_layers()
    nf = 0
    for fl, pts in TER.scan_regions(dom, [cuts, gravel, soil]):
        cut, grv, sl = fl
        if cut:
            continue
        TER.flat_face(mb, pts, P3, GRAVEL if grv else (SOIL if sl else GRASS))
        nf += 1
    noble_path(mb, AXIS_Y[0], AXIS_Y[1], 2 * AXIS_HW, P3, zb=P3 - 0.55)
    mb.finish(recalc=False)
    return nf


PATH_A = "Stone_Paving_SG"              # lajes do eixo, tom A (o chao andavel claro e quente da paleta)
PATH_B = "Stone_Paving_SG_B"            # tom B (= o tom A das ruas da vila: o eixo e um valor acima delas)
PATH_BORDER = "Stone_SG_Castle_B"       # faixa de borda em cantaria escura
PATH_JOINT = "Stone_SG_Floor"           # leito das juntas
# 4 lajes por fiada em modulos irregulares DIRIGIDOS (nenhuma junta entre 0,44 e 0,56: nada de faixa central)
PATH_SPLITS = ((0.23, 0.41, 0.71), (0.28, 0.59, 0.79), (0.19, 0.40, 0.66), (0.33, 0.60, 0.83), (0.25, 0.43, 0.74),
               (0.30, 0.58, 0.77))


def _slab(mb, x0, y0, x1, y1, z0, z1, m):
    """laje: tampo + 4 faces (sem fundo: assenta no leito) - 10 tris"""
    _cap_prism(mb, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, m)


def _cap_prism(mb, poly, z0, z1, m):
    """prisma sem o fundo (assenta em algo): tampo + faces laterais; poly anti-horario"""
    bm = mb.bm
    lo = [bm.verts.new((p[0], p[1], z0)) for p in poly]
    hi = [bm.verts.new((p[0], p[1], z1)) for p in poly]
    n = len(poly)
    bm.faces.new(hi)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    mb._post(lo + hi, m, None, 0, 1)


def noble_path(mb, y0, y1, W, z, thread_m=None, zb=None, row=2.6):
    """FINESSE 3B (05.01): o eixo nobre portao -> porta na LINGUAGEM DAS RUAS DA VILA, sem Neon e sem marmore negro:
    leito escuro (juntas de 0,12, 0,10 de fundo), CAMPO de lajes claras (tom A / tom B, 2/3 - 1/3) em fiadas de 2,2 /
    3,0 com 4 lajes por fiada em modulos irregulares, FIADA MESTRA de cantaria escura atravessando a cada 8 fiadas,
    FAIXA DE BORDA de cantaria escura (lajes ao comprido em pecas de 1,8 / 2,6) e MEIO-FIO de cantaria clara chanfrado
    em pecas de ~3 (0,16 acima das lajes). Marmore negro so nos 2 TAPETES (frente do portao e da porta), emoldurados.
    zb = fundo do leito (o terreno do patio desce 0,45: o leito fecha o rebaixo). thread_m: ignorado (o fio Neon saiu)."""
    hw = W / 2.0
    zb = z - 0.2 if zb is None else zb
    zt = z + 0.06                                        # topo das lajes
    zj = zt - 0.10                                       # leito (fundo das juntas)
    g = 0.06                                             # meia junta
    CURB, BORD = 0.62, 1.5
    mb.box2((-hw, y0, zb), (hw, y1, zj), PATH_JOINT, 0.0)
    # meio-fio chanfrado (perfil de 5 pontos) em pecas de ~3
    for sd in (-1, 1):
        xa, xb = sorted((sd * hw, sd * (hw - CURB)))
        n = max(1, int(round((y1 - y0) / 3.0)))
        for k in range(n):
            ya, yb = y0 + (y1 - y0) * k / n + (0.04 if k else 0.0), y0 + (y1 - y0) * (k + 1) / n - (0.04 if k < n - 1 else 0.0)
            inner = xa if sd > 0 else xb
            outer = xb if sd > 0 else xa
            prof = [(outer, zb + 0.1), (inner, zb + 0.1), (inner, zt + 0.08), (inner + sd * 0.1, zt + 0.16),
                    (outer, zt + 0.16)]
            _loft(mb, [[(px, ya, pz) for px, pz in prof], [(px, yb, pz) for px, pz in prof]], "Stone_SG_TrimLow")
    # faixa de borda: lajes ao comprido (ritmo 1,8 / 2,6)
    for sd in (-1, 1):
        xa, xb = sorted((sd * (hw - CURB), sd * (hw - CURB - BORD)))
        yy, k = y0, 0
        while yy < y1 - 0.4:
            ln = min((1.8, 2.6)[k % 2], y1 - yy)
            if y1 - (yy + ln) < 0.9:
                ln = y1 - yy
            _slab(mb, xa + g, yy + g, xb - g, yy + ln - g, zj, zt + 0.02, PATH_BORDER)
            yy += ln
            k += 1
    # tapetes de marmore (frente do portao e da porta): moldura de cantaria clara + 3 x 2 lajes negras
    fx = hw - CURB - BORD
    rugs = ((y0 + 0.0, y0 + 4.4), (y1 - 5.2, y1))
    for ra, rb in rugs:
        _slab(mb, -fx + g, ra + g, fx - g, ra + 0.8 - g, zj, zt, "Stone_SG_TrimLow")
        _slab(mb, -fx + g, rb - 0.8 + g, fx - g, rb - g, zj, zt, "Stone_SG_TrimLow")
        for i in range(3):
            xa = -fx + 2 * fx * i / 3
            xb = -fx + 2 * fx * (i + 1) / 3
            for j in range(2):
                ya = ra + 0.8 + (rb - ra - 1.6) * j / 2
                yb = ra + 0.8 + (rb - ra - 1.6) * (j + 1) / 2
                _slab(mb, xa + g, ya + g, xb - g, yb - g, zj, zt, MARB)
    # campo: fiadas 2,2 / 3,0 entre os tapetes; fiada mestra de cantaria a cada 8
    fa, fb = rugs[0][1], rugs[1][0]
    rows, acc = [], 0.0
    while acc < (fb - fa) - 1.0 or not rows:
        rows.append((2.2, 3.0)[len(rows) % 2])
        acc += rows[-1]
    kf = (fb - fa) / acc
    yy = fa
    for j, ln in enumerate(rows):
        ln *= kf
        if j and j % 8 == 0:
            _slab(mb, -fx + g, yy + g, fx - g, yy + 0.7 - g, zj, zt + 0.02, PATH_BORDER)
            yy += 0.7
            ln -= 0.7
        cuts = [0.0] + list(PATH_SPLITS[j % len(PATH_SPLITS)]) + [1.0]
        for i, (t0, t1) in enumerate(zip(cuts, cuts[1:])):
            m = PATH_A if ((j // 2) + i) % 3 != 1 else PATH_B
            _slab(mb, -fx + 2 * fx * t0 + g, yy + g, -fx + 2 * fx * t1 - g, yy + ln - g, zj, zt, m)
        yy += ln


# ------------------------------------------------------------------ 2. gramados rebaixados (murete + degraus)
def lawn_wall(mb, rect_, s):
    """murete de cantaria dentro do recorte do terreno (face de fora encosta de costas no espelho do terreno): corpo
    de P3-1,3 a P3+0,42, embasamento saliente por dentro, capa em pecas de 2,4 com pingadeira para os 2 lados;
    vao dos degraus nas 2 pontas (STEP_Y) com pilaretes de remate"""
    import sg_entry as SE
    x0, y0, x1, y1 = rect_
    T = MUR_T
    zb, zt = P3 - LAWN_DEPTH - 0.1, P3 + 0.42
    zl = P3 - LAWN_DEPTH
    g0, g1 = STEP_Y
    runs = [((x0, y0), (x1, y0), (0.0, 1.0)), ((x0, y1), (x1, y1), (0.0, -1.0)),
            ((x0, y0 + T), (x0, g0), (1.0, 0.0)), ((x0, g1), (x0, y1 - T), (1.0, 0.0)),
            ((x1, y0 + T), (x1, g0), (-1.0, 0.0)), ((x1, g1), (x1, y1 - T), (-1.0, 0.0))]
    for (a, b, (nx, ny)) in runs:
        # corpo (faixa de espessura T para dentro)
        pa = (a[0] + nx * T, a[1] + ny * T)
        pb = (b[0] + nx * T, b[1] + ny * T)
        xs, ys = sorted((a[0], b[0], pa[0], pb[0])), sorted((a[1], b[1], pa[1], pb[1]))
        mb.box2((xs[0], ys[0], zb), (xs[-1], ys[-1], zt), WALLM, 0.0)
        # embasamento por dentro (0,14 para fora da face interna, 0,4 de altura)
        q0 = (pa[0] + nx * 0.14, pa[1] + ny * 0.14)
        q1 = (pb[0] + nx * 0.14, pb[1] + ny * 0.14)
        xs, ys = sorted((pa[0], pb[0], q0[0], q1[0])), sorted((pa[1], pb[1], q0[1], q1[1]))
        if nx:                                                    # lados curtos: o embasamento para antes do muro longo
            ys = [ys[0] + (0.14 if abs(ys[0] - (y0 + T)) < 1e-6 else 0.0), ys[-1] - (0.14 if abs(ys[-1] - (y1 - T)) < 1e-6 else 0.0)]
        mb.box2((xs[0], ys[0], zl - 0.05), (xs[-1], ys[-1], zl + 0.4), RELM, 0.0)
        # fiada intermediaria (junta horizontal rebaixada: faixa 0,06 para dentro da face, 0,12 de altura)
        # capa em pecas: 0,12 para fora dos 2 lados, pingadeira
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        nseg = max(1, int(round(ln / 3.2)))
        ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
        for k in range(nseg):
            t0 = ln * k / nseg + (0.03 if k else -0.12)
            t1 = ln * (k + 1) / nseg - (0.03 if k < nseg - 1 else -0.12)
            c0 = (a[0] + ux * t0 - nx * 0.12, a[1] + uy * t0 - ny * 0.12)
            c1 = (a[0] + ux * t1 + nx * (T + 0.12), a[1] + uy * t1 + ny * (T + 0.12))
            mb.box2((min(c0[0], c1[0]), min(c0[1], c1[1]), zt), (max(c0[0], c1[0]), max(c0[1], c1[1]), zt + 0.2), CAP,
                    0.0)
    # pilaretes nas bocas dos degraus + degraus (2 lances de 0,6) + bochechas
    for xe, d in ((x0, 1.0), (x1, -1.0)):
        for ye in (g0, g1):
            px = xe + d * 0.7
            py = ye + (-0.7 if ye == g0 else 0.7)
            mb.prism(SE.chamfer_sq(px, py, 0.75, 0.16), zb, P3 + 0.95, WALLM)
            mb.box((1.7, 1.7, 0.16), (px, py, P3 + 1.03), (0, 0, 0), CAP, 0.0)
            SE.finial(mb, px, py, P3 + 1.11, 0.42, m=CAP, n=8)
        xa, xb = sorted((xe, xe + d * 1.0))
        mb.box2((xa, g0, zb + 0.03), (xb, g1, P3 - 0.04), CAP, 0.0)                 # patamar (soleira)
        xa, xb = sorted((xe + d * 1.0, xe + d * 2.75))
        mb.box2((xa, g0, zb + 0.03), (xb, g1, P3 - 0.6), CAP, 0.0)                   # degrau do meio
        for ye in (g0, g1):
            ya, yb = sorted((ye, ye + (0.5 if ye == g0 else -0.5)))
            xa, xb = sorted((xe + d * 1.4, xe + d * 2.9))
            mb.box2((xa, ya, zb), (xb, yb, P3 - 0.1), WALLM, 0.0)                    # bochecha
        xa, xb = sorted((xe, xe + d * 2.75))
        col_box2("SG_PropLawnStep", (xa, g0, P3 - 0.6 - 0.5), (xb, g1, P3 - 0.6))
    col_box2("SG_PropLawnFloor", (x0 + T, y0 + T, P3 - LAWN_DEPTH - 1.0), (x1 - T, y1 - T, P3 - LAWN_DEPTH))
    for (a, b, (nx, ny)) in runs:
        pa = (a[0] + nx * T, a[1] + ny * T)
        pb = (b[0] + nx * T, b[1] + ny * T)
        xs, ys = sorted((a[0], b[0], pa[0], pb[0])), sorted((a[1], b[1], pa[1], pb[1]))
        col_box2("SG_PropLawnWall", (xs[0], ys[0], P3 - LAWN_DEPTH), (xs[-1], ys[-1], zt + 0.2))
    lawn_dress(mb, rect_, s)


# FINESSE 3B (05.09): o gramado rebaixado deixa de ser so um retangulo com murete - CANTEIROS ELEVADOS nos 4 cantos com
# murete em CHANFRO DIRIGIDO (o longo no sentido do gramado: 7 x 3,4), BANCO RECUADO com espaldar no meio do murete
# do lado do castelo e um caminho de PISANTES em S de um degrau ao outro. As plantas dos canteiros sao derivas/arbustos
# do plants_half (transbordam o murete).
LAWN_BED = (7.0, 3.4)


def lawn_beds(rect_):
    """os 4 triangulos dos canteiros de canto (pontos no nivel do gramado)"""
    x0, y0, x1, y1 = rect_
    T = MUR_T
    a, b = LAWN_BED
    out = []
    for sx_, cx_ in ((1, x0 + T), (-1, x1 - T)):
        for sy_, cy_ in ((1, y0 + T), (-1, y1 - T)):
            out.append(((cx_, cy_), (cx_ + sx_ * a, cy_), (cx_, cy_ + sy_ * b), sx_, sy_))
    return out


def lawn_dress(mb, rect_, s):
    x0, y0, x1, y1 = rect_
    zl = P3 - LAWN_DEPTH
    for (c, pa, pb, sx_, sy_) in lawn_beds(rect_):
        # terra do canteiro (elevada 0,9) + murete diagonal com capa
        _cap_prism(mb, SL.ccw([c, pa, pb]), zl - 0.05, zl + 0.86, SOIL)
        ux, uy = pb[0] - pa[0], pb[1] - pa[1]
        ln = math.hypot(ux, uy)
        ux, uy = ux / ln, uy / ln
        nx, ny = -uy, ux
        if (c[0] - pa[0]) * nx + (c[1] - pa[1]) * ny > 0:      # normal para FORA do canteiro (lado do gramado)
            nx, ny = -nx, -ny
        q = lambda p, t: (p[0] + nx * t, p[1] + ny * t)
        _cap_prism(mb, SL.ccw([q(pa, 0.0), q(pb, 0.0), q(pb, 0.6), q(pa, 0.6)]), zl - 0.05, zl + 1.02, WALLM)
        _cap_prism(mb, SL.ccw([q((pa[0] - ux * 0.12, pa[1] - uy * 0.12), -0.1), q((pb[0] + ux * 0.12, pb[1] + uy * 0.12), -0.1),
                               q((pb[0] + ux * 0.12, pb[1] + uy * 0.12), 0.76), q((pa[0] - ux * 0.12, pa[1] - uy * 0.12), 0.76)]),
                   zl + 1.02, zl + 1.18, CAP)
    # banco recuado: assento sobre 2 pes, de costas para o murete do lado do castelo, com ESPALDAR alto e abas
    xc = (x0 + x1) / 2
    yw = y1 - MUR_T
    mb.box((5.2, 1.1, 0.28), (xc, yw - 0.75, zl + 1.42), (0, 0, 0), CAP, 0.0)
    for e in (-1, 1):
        mb.box((0.5, 0.9, 1.3), (xc + e * 2.0, yw - 0.7, zl + 0.63), (0, 0, 0), RELM, 0.0)
        mb.box((0.6, 1.3, 2.3), (xc + e * 2.85, yw - 0.55, zl + 1.15), (0, 0, 0), WALLM, 0.0)       # abas
    mb.box((6.3, 0.6, 1.6), (xc, yw + 0.1, P3 + 1.0), (0, 0, 0), WALLM, 0.0)                         # espaldar
    mb.box((6.7, 0.95, 0.2), (xc, yw + 0.1, P3 + 1.9), (0, 0, 0), CAP, 0.0)
    FP.frustum(mb, (xc, yw + 0.1, P3 + 2.0), 3.2, 0.7, 1.2, 0.5, 0.5, CAP)
    # pisantes em S de um degrau ao outro (y 6 +- 2,4), pecas de 1,7 x 1,15 com o ritmo do passo
    ym = (STEP_Y[0] + STEP_Y[1]) / 2
    xa_, xb_ = x0 + 3.6, x1 - 3.6
    n = int((xb_ - xa_) / 2.25)
    for k in range(n + 1):
        t = k / n
        x = xa_ + (xb_ - xa_) * t
        y = ym + 2.4 * math.sin(2 * math.pi * t) * (1 if s > 0 else -1)
        dy = 2.4 * 2 * math.pi * math.cos(2 * math.pi * t) / (xb_ - xa_) * (1 if s > 0 else -1)
        a = math.atan2(dy, 1.0)
        w, d = (0.85 + 0.12 * ((k * 7) % 3) / 2), 0.58
        pts = [(x + ca * u - sa * v, y + sa * u + ca * v) for (u, v) in ((-d, -w), (d, -w), (d, w), (-d, w))
               for ca, sa in ((math.cos(a), math.sin(a)),)]
        _cap_prism(mb, pts, zl - 0.1, zl + 0.07, RELM)


# ------------------------------------------------------------------ 3. espelhos d'agua
def pool(mb, rect_, name):
    """FINESSE 3B (05.02): espelho d'agua que NAO le piscina - bacia de CANTARIA erguida a altura de assento (o bordo e
    banco): corpo de silhar ate P3+0,92, CAPA MOLDURADA em pecas de ~4 (filete + laje com balanco de 0,2 para fora:
    pingadeira = a sombra embaixo), DEGRAU (soco) de 0,36 em volta, PILARES nos 4 cantos com capa e remate em
    piramide, PATAMAR de lajes no meio do lado da travessia com 2 URNAS no bordo e a BICA na cabeceira (estela com
    cornija e frontao, medalhao e bico sobre a lamina). Fundo de obsidiana. A agua e do Roblox (WATER_Court_<name>):
    as faces de dentro ficam EXATAS no retangulo da lamina e nada entra nele no nivel."""
    x0, y0, x1, y1 = rect_
    R = POOL_RIM + 0.2
    zr = P3 + 0.92                                     # topo do corpo
    zc = zr + 0.32                                     # topo da capa (P3 + 1,24)
    cx = (x0 + x1) / 2
    mb.box2((x0, y0, P3 - 0.56), (x1, y1, POOL_FLOOR), OBS, 0.0)
    # so na PREVIA (PREVIEW_ nao exporta): a lamina como o Roblox fara, para julgar a leitura do espelho
    pv = MB("PREVIEW_CourtWater_%s" % name, "00_REFERENCE", None, detail="far", floor=-999)
    pv.box2((x0, y0, POOL_LEVEL - 0.02), (x1, y1, POOL_LEVEL), "Water_SG", 0.0)
    pv.finish()
    sides = (((x0 - R, y0 - R), (x1 + R, y0), "x"), ((x0 - R, y1), (x1 + R, y1 + R), "x"),
             ((x0 - R, y0), (x0, y1), "y"), ((x1, y0), (x1 + R, y1), "y"))
    for (a, b, ax) in sides:
        mb.box2((a[0], a[1], P3 - 0.5), (b[0], b[1], zr), WALLM, 0.0)
        col_box2("SG_PropPool", (a[0], a[1], P3 - 0.5), (b[0], b[1], zc))
    # degrau (soco) em volta: 0,8 para fora, 0,36 de altura
    D = 0.8
    for (a, b) in (((x0 - R - D, y0 - R - D), (x1 + R + D, y0 - R)), ((x0 - R - D, y1 + R), (x1 + R + D, y1 + R + D)),
                   ((x0 - R - D, y0 - R), (x0 - R, y1 + R)), ((x1 + R, y0 - R), (x1 + R + D, y1 + R))):
        _cap_prism(mb, [(a[0], a[1]), (b[0], a[1]), (b[0], b[1]), (a[0], b[1])], P3 - 0.2, P3 + 0.36, RELM)
    # capa moldurada em pecas (o balcao da frente interrompe a capa no meio do lado sul)
    for (a, b, ax) in sides:
        ln = (b[0] - a[0]) if ax == "x" else (b[1] - a[1])
        n = max(1, int(round(ln / 4.0)))
        for k in range(n):
            t0 = ln * k / n + (0.03 if k else 0.0)
            t1 = ln * (k + 1) / n - (0.03 if k < n - 1 else 0.0)
            if ax == "x":
                p0, p1 = (a[0] + t0, a[1]), (a[0] + t1, b[1])
                e0, e1 = (0.0, 0.2 if a[1] < y0 else 0.12), (0.0, 0.12 if a[1] < y0 else 0.2)
            else:
                p0, p1 = (a[0], a[1] + t0), (b[0], a[1] + t1)
                e0, e1 = ((0.2, 0.0), (0.12, 0.0)) if a[0] < x0 else ((0.12, 0.0), (0.2, 0.0))
            _cap_prism(mb, [(p0[0] - e0[0] * 0.4, p0[1] - e0[1] * 0.4), (p1[0] + e1[0] * 0.4, p0[1] - e0[1] * 0.4),
                            (p1[0] + e1[0] * 0.4, p1[1] + e1[1] * 0.4), (p0[0] - e0[0] * 0.4, p1[1] + e1[1] * 0.4)],
                       zr - 0.02, zr + 0.1, CAP)
            _cap_prism(mb, [(p0[0] - e0[0], p0[1] - e0[1]), (p1[0] + e1[0], p0[1] - e0[1]),
                            (p1[0] + e1[0], p1[1] + e1[1]), (p0[0] - e0[0], p1[1] + e1[1])], zr + 0.1, zc, CAP)
    # pilares de canto
    for px in (x0 - R / 2 - 0.1, x1 + R / 2 + 0.1):
        for py in (y0 - R / 2 - 0.1, y1 + R / 2 + 0.1):
            mb.box((2.2, 2.2, 2.1), (px, py, P3 + 0.75), (0, 0, 0), RELM, 0.0)
            mb.box((2.6, 2.6, 0.22), (px, py, P3 + 1.91), (0, 0, 0), CAP, 0.0)
            FP.frustum(mb, (px, py, P3 + 2.02), 2.1, 2.1, 0.5, 0.5, 0.62, CAP)
    # PATAMAR no meio do lado sul (de frente para a travessia): laje larga de 2 degraus diante do bordo (sem colisao:
    # 0,36 - as rotas do patio passam a 2 do bordo)
    _cap_prism(mb, [(cx - 4.6, y0 - R - D - 1.0), (cx + 4.6, y0 - R - D - 1.0), (cx + 4.6, y0 - R), (cx - 4.6, y0 - R)],
               P3 - 0.2, P3 + 0.36, CAP)
    for e in (-1, 1):
        mb.box((1.0, 1.0, 0.9), (cx + e * 5.2, y0 - R - 0.5, P3 + 1.69), (0, 0, 0), RELM, 0.0)
        EM._lathe(mb, (cx + e * 5.2, y0 - R - 0.5, P3 + 2.14), [(0.36, 0.0), (0.5, 0.2), (0.62, 0.5), (0.42, 0.82),
                                                               (0.5, 0.92), (0.0, 0.95)], CAP, 8)
    # BICA na cabeceira (lado da fachada): estela com cornija e frontao, carranca e bico sobre a lamina
    yc = y1 + R / 2
    mb.box((2.8, 1.2, 2.5), (cx, yc + 0.1, zc + 1.25), (0, 0, 0), RELM, 0.0)
    mb.box((3.3, 1.6, 0.26), (cx, yc + 0.1, zc + 2.63), (0, 0, 0), CAP, 0.0)
    FP.frustum(mb, (cx, yc + 0.1, zc + 2.76), 3.0, 1.3, 0.6, 1.1, 0.7, CAP)
    mb.cyl(0.62, 0.22, (cx, yc - 0.55, zc + 1.3), (math.pi / 2, 0, 0), CAP, n=10, bevel=0.0)        # medalhao
    mb.box((0.34, 1.3, 0.24), (cx, y1 - 0.35, zc + 1.0), (0, 0, 0), CAP, 0.0)                    # bico
    col_box("SG_PropPool", (3.3, 1.6, 3.4), (cx, yc + 0.1, zc + 1.7))


def sync_water_markers():
    """os marcadores do espelho (sg_core, onda 0) passam a ficar sobre a bacia REAL (centro, 32 x 20, nivel, fundo)"""
    import bpy
    for nm, (x0, y0, x1, y1) in (("L", POOLS[0]), ("R", POOLS[1])):
        ob = bpy.data.objects.get("WATER_Court_%s" % nm)
        if ob is None:
            print("COURT AVISO marcador WATER_Court_%s inexistente" % nm)
            continue
        ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, POOL_LEVEL)
        ob["sx"], ob["sy"] = round(x1 - x0, 2), round(y1 - y0, 2)
        ob["level"], ob["floor"], ob["depth"] = POOL_LEVEL, POOL_FLOOR, round(POOL_LEVEL - POOL_FLOOR, 2)
        ob["note"] = ("espelho d'agua do patio-jardim (sg_court, onda 2): bacia estanque %.0f x %.0f, capa a %.2f "
                      "(0,06 acima da lamina); sx ao longo de X local, sy ao longo de Y local (fwd)" %
                      (x1 - x0, y1 - y0, POOL_LEVEL + 0.06 - P3))


# ------------------------------------------------------------------ 4. plantas: sebes, topiarias, derivas de flores
def tall_hedge(mg, a, b, w, h, seed, m=YEW, step=2.4):
    """FINESSE 3B (05.03): sebe de teixo em MASSAS - casca continua ao longo de a->b com secao de 9 pontos (pe alargado
    que assenta no chao, flancos levemente em talude, ombros redondos) e COROAMENTO ONDULADO: cristas a cada ~5,5
    (+-0,4) e a largura afinando nos vales (le lances podados que se fundem, nao caixa de cantos redondos)"""
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(2, int(round(L_ / step)))
    ux, uy = (b[0] - a[0]) / L_, (b[1] - a[1]) / L_
    nx, ny = -uy, ux
    z = P3 - 0.06
    ph = seed * 1.37
    rows = []
    for k in range(n + 1):
        t = L_ * k / n
        wv = math.sin(2 * math.pi * t / 5.5 + ph)
        end = min(1.0, t / 1.2, (L_ - t) / 1.2)                    # pontas arredondadas
        ht = h * (0.86 + 0.14 * end) + 0.4 * wv
        hw = w / 2 * (0.94 + 0.06 * wv) * (0.8 + 0.2 * end)
        px, py = a[0] + ux * t, a[1] + uy * t
        prof = [(-hw - 0.1, 0.0), (-hw, 0.55), (-hw + 0.08, 0.72 * ht), (-hw + 0.38, ht - 0.12), (0.0, ht),
                (hw - 0.38, ht - 0.12), (hw - 0.08, 0.72 * ht), (hw, 0.55), (hw + 0.1, 0.0)]
        rows.append([(px + nx * u, py + ny * u, z + v) for u, v in prof])
    _loft(mg, rows, m, "ngon", "ngon")


def cone(mg, x, y, z, h, r, m=YEW):
    """FINESSE 3B (05.03): topiaria de 3 BOLAS DECRESCENTES em fuste (grande na base, media, pequena no alto) com o
    FUSTE fino a mostra entre elas - um perfil so de revolucao (10 lados); nao o cone liso de antes"""
    GD._occ(x, y, r + 0.4)
    EM._lathe(mg, (x, y, z - 0.05), [(r * 0.55, 0.0), (r, 0.13 * h), (r * 0.9, 0.27 * h), (r * 0.12, 0.36 * h),
                                     (r * 0.1, 0.45 * h), (r * 0.64, 0.51 * h), (r * 0.56, 0.62 * h),
                                     (r * 0.09, 0.69 * h), (r * 0.08, 0.76 * h), (r * 0.4, 0.82 * h), (r * 0.3, 0.93 * h),
                                     (0.0, h)], m, 10, 0.2)


DRIFT_K = 0.62      # FINESSE 3B: derivas um pouco mais ralas (os tris foram para a pedra do patio, beco e mirante)


def drift(mg, cx, cy, rx, ry, kinds, seed, z=P3, dens=1.0, s=1.0, rot=0.0, ctx="patio"):
    """DERIVA de flores (mancha alongada de contorno organico): espiral de filotaxia dentro do blob, 1a especie no miolo,
    2a na borda; mais rala na borda (le grupo natural, nao canteiro de regua)"""
    poly = blob(cx, cy, rx, ry, seed, rot)
    ga = math.pi * (3.0 - math.sqrt(5.0))
    n = int(rx * ry * 2.2 * dens * DRIFT_K)
    got = 0
    for k in range(n):
        r = math.sqrt((k + 0.5) / n)
        a = k * ga + seed
        x = cx + r * rx * math.cos(a) * math.cos(rot) - r * ry * math.sin(a) * math.sin(rot)
        y = cy + r * rx * math.cos(a) * math.sin(rot) + r * ry * math.sin(a) * math.cos(rot)
        if not L.point_in_poly(x, y, poly):
            continue
        if r > 0.75 and GD.hh(x, y, 5) < 0.35:
            continue
        kind = kinds[0] if (r < 0.62 or len(kinds) == 1) else kinds[1]
        GD.plant(mg, kind, x, y, z, s * (1.08 + 0.18 * (1.0 - r)), rich=True)
        GD.PLANTED.append(("flor", x, y, z, ctx))
        GD._occ(x, y, 0.3)
        got += 1
    return got


def shrub(mg, x, y, z, r, seed, m=BOX):
    """arbusto baixo de folha (almofada lobada do kit, nao bola lisa)"""
    VK.puff(mg, (x, y, z - 0.08), r, m, random.Random(seed), 1, 0.8, under=None)


def plants_half(mb, mg, s):
    i = 0 if s < 0 else 1
    # sebes altas laterais (com a abertura da travessia marcada por 2 chamas de teixo)
    # (FINESSE 3B: cada trecho continuo e UMA sebe em massas e UMA caixa de colisao)
    runs, cur = [], None
    for (y0, y1, h) in SIDE_HEDGE[s]:
        if cur and abs(cur[1] - y0) < 0.01:
            cur = (cur[0], y1, max(cur[2], h))
        else:
            if cur:
                runs.append(cur)
            cur = (y0, y1, h)
    runs.append(cur)
    for k, (y0, y1, h) in enumerate(runs):
        tall_hedge(mg, (s * SIDE_X, y0), (s * SIDE_X, y1), 2.6, h * 0.92, 3.1 * k + s)
        xa, xb = sorted((s * (SIDE_X - 1.3), s * (SIDE_X + 1.3)))
        col_box2("SG_VegHedge", (xa, y0, P3), (xb, y1, P3 + h))
    for yc in SIDE_CONES[s]:
        cone(mg, s * SIDE_X, yc, P3, 7.2, 1.6)
        col_box("SG_VegHedge", (2.2, 2.2, 6.0), (s * SIDE_X, yc, P3 + 3.0))
    # sebe alta na frente da fachada (massas de alturas diferentes: le massa viva contra o paredao)
    x0_, x1_ = FACADE_HEDGE[0][0], FACADE_HEDGE[-1][1]
    hf = sum(h for _, _, h in FACADE_HEDGE) / len(FACADE_HEDGE)
    tall_hedge(mg, (s * x0_, FACADE_HEDGE_Y), (s * x1_, FACADE_HEDGE_Y), 2.2, hf, 2.0 + 2 * s)
    xa, xb = sorted((s * x0_, s * x1_))
    col_box2("SG_VegHedge", (xa, FACADE_HEDGE_Y - 1.1, P3), (xb, FACADE_HEDGE_Y + 1.1, P3 + hf))
    # sebe MEDIA em L na quina entre o porche e o espelho
    a, b, c = (s * 33.4, 53.6), (s * 33.4, 46.0), (s * 37.4, 46.0)
    tall_hedge(mg, a, (b[0], b[1] - 0.6), 1.3, 1.7, 7 + s, BOX, 1.6)
    tall_hedge(mg, (b[0] - s * 0.65, b[1]), c, 1.3, 1.5, 9 + s, BOX, 1.6)
    xa, xb = sorted((s * 32.7, s * 34.1))
    col_box2("SG_VegHedge", (xa, 45.4, P3), (xb, 53.6, P3 + 1.7))
    GD.topiary(mg, (s * 37.9, 46.0, P3 - 0.05), 0.9)
    # chamas de teixo nas bocas de dentro dos gramados (marcam os degraus vistos do eixo)
    x0 = [r for r in lawn_rects() if (r[0] > 0) == (s > 0)][0]
    xin = x0[0] if s > 0 else x0[2]
    xout = x0[2] if s > 0 else x0[0]
    for yc in (STEP_Y[0] - 5.2, STEP_Y[1] + 5.2):
        cone(mg, xin - s * 4.6, yc, P3, 4.4, 1.15)
        col_box("SG_VegTopiary", (1.6, 1.6, 4.0), (xin - s * 4.6, yc, P3 + 2.0))
    # derivas de flores (frente das massas): pe do porche, pe das sebes, gramado nos degraus, roda da arvore
    sx, sy = BEDS[i]
    drift(mg, sx, sy - 1.6, 3.4, 1.2, ("moon", "spike"), 7 + i, dens=1.2)
    for k, (yc, kinds) in enumerate(((-6.0, ("spike", "moon")), (7.5, ("bell", "moon")), (36.5, ("moon", "amber")),
                                    (48.5, ("spike", "bell")))):
        drift(mg, s * (SIDE_X - 3.1), yc, 0.9, 2.6 + 0.4 * (k % 2), kinds, 13 + k + 4 * i, dens=1.2)
    for k, (xc, rx) in enumerate(((43.0, 5.5), (62.5, 6.5), (84.5, 5.0))):
        drift(mg, s * xc, FACADE_HEDGE_Y - 2.0, rx, 0.8, ("spike", "moon") if k % 2 == 0 else ("moon", "spike"),
              23 + k + 3 * i, dens=1.0)
    zl = P3 - LAWN_DEPTH
    # canteiros elevados dos cantos (05.09): arbusto que transborda o murete + deriva de flores na terra
    for k, (c, pa, pb, sx_, sy_) in enumerate(lawn_beds(x0)):
        gx, gy = (c[0] + pa[0] + pb[0]) / 3, (c[1] + pa[1] + pb[1]) / 3
        shrub(mg, (c[0] + gx) / 2 + sx_ * 0.4, (c[1] + gy) / 2 + sy_ * 0.3, zl + 0.86, 1.25, 141 + k + 9 * i)
        drift(mg, gx + sx_ * 0.6, gy, 1.5, 0.7, ("moon", "spike") if k % 2 else ("bell", "moon"), 31 + k + 5 * i,
              z=zl + 0.86, dens=1.6)
    # 2 derivas soltas DENTRO do gramado rebaixado (encostadas no murete, nunca no meio: o gramado fica limpo)
    for k, (xc, yc, kinds) in enumerate(((49.0, 12.4, ("moon", "spike")), (69.5, -0.4, ("spike", "moon")))):
        drift(mg, s * xc, yc, 3.2, 0.9, kinds, 47 + k + 2 * i, z=zl, dens=1.0)
    tx, ty = TREES[i]
    for k, a in enumerate((205.0, 330.0)):
        ra = math.radians(a if s > 0 else 180.0 - a)
        drift(mg, tx + 6.6 * math.cos(ra), ty + 6.6 * math.sin(ra), 1.6, 1.0, ("bell", "moon"), 37 + k + 2 * i,
              rot=ra + math.pi / 2, dens=1.2)
    for lx, ly in NODE_LAMPS:
        if (lx > 0) == (s > 0):
            drift(mg, lx + s * 1.6, ly + 1.4, 1.0, 0.8, ("moon",), 43 + i, dens=1.3)
    # massa MEDIA: grupos de 2-3 arbustos lobados na frente das sebes altas (a flor fica na frente deles)
    for k, (xc, yc) in enumerate(SHRUBS):
        n = 2
        for j in range(n):
            a = GD.hh(xc, yc, j + 3) * math.tau
            d = 0.0 if j == 0 else 1.3
            shrub(mg, s * xc + math.cos(a) * d, yc + math.sin(a) * d * 0.6, P3, 1.55 - 0.3 * j, 101 + k * 7 + j + 50 * i)
        GD._occ(s * xc, yc, 2.2)
    # pe da muralha: arbustos baixos entre as trepadeiras (a grama do sg_garden adensa a borda)
    for k, xc in enumerate((40.5, 51.5, 64.5, 78.0, 85.0)):
        shrub(mg, s * xc, FC[1] + 1.6, P3, 1.0 + 0.25 * (k % 2), 91 + k + 7 * i)


def tree_bench(mb, x, y, r0=2.5, r1=3.6, zs=1.6):
    """FINESSE 3B (05.04): a arvore-marco ganha um CANTEIRO REDONDO elevado (parede de silhar de 0,4 que sobe a 2,6:
    e o ESPALDAR do banco, capa clara com balanco; terra a 0,8) e um BANCO CIRCULAR de pedra virado para fora, em 8
    pecas de assento sobre 8 pes (junta entre as pecas); a arvore e do sg_veg (agente G)"""
    rw = 2.1
    ring(mb, (x, y), rw, r0, P3 - 0.1, P3 + 2.55, WALLM, n=16)
    ring(mb, (x, y), rw - 0.12, r0 + 0.16, P3 + 2.55, P3 + 2.78, CAP, n=16)
    _cap_prism(mb, ngon((x, y), rw, 10), P3 - 0.1, P3 + 0.8, SOIL)
    for k in range(8):
        a0 = (k + 0.03) * math.tau / 8 + math.pi / 8
        a1 = (k + 0.97) * math.tau / 8 + math.pi / 8
        am = (a0 + a1) / 2
        pts = [(x + r0 * math.cos(a0), y + r0 * math.sin(a0)), (x + r1 * math.cos(a0), y + r1 * math.sin(a0)),
               (x + (r1 + 0.04) * math.cos(am), y + (r1 + 0.04) * math.sin(am)),
               (x + r1 * math.cos(a1), y + r1 * math.sin(a1)), (x + r0 * math.cos(a1), y + r0 * math.sin(a1))]
        _cap_prism(mb, SL.ccw(pts), P3 + zs - 0.28, P3 + zs, CAP)
        rm = (r0 + r1) / 2 + 0.1
        mb.box((0.5, 0.7, zs - 0.28), (x + rm * math.cos(am), y + rm * math.sin(am), P3 + (zs - 0.28) / 2),
               (0, 0, am), RELM, 0.0)
    SL.octo_col("SG_PropBench", x, y, r1, P3, P3 + zs)


def court():
    rng = random.Random(3603)
    mb = MB("SG_Prop_Court", COLL, rng, detail="near")
    mg = MB("SG_Veg_Gdn_Court", "10_VEGETATION", None, detail="near", floor=-999)
    for i, r in enumerate(lawn_rects()):
        lawn_wall(mb, r, 1 if r[0] > 0 else -1)
    for nm, p in (("L", POOLS[0]), ("R", POOLS[1])):
        pool(mb, p, nm)
    sync_water_markers()
    for x, y in NODE_LAMPS:
        EM.lantern_post(mb, mb, (x, y, P3), 0.0, h=7.4)
        col_box("SG_PropCourtLamp", (1.2, 1.2, 9.0), (x, y, P3 + 4.5))
    for x, y in TREES:
        tree_bench(mb, x, y)
    for s in (-1, 1):
        plants_half(mb, mg, s)
    GD.court_vines(mg)
    # arco de ferro no pe da escada do portao: o arco do KIT da vila (sg_village.iron_arch), no objeto do patio
    import sg_village as VL
    x, y, zz, hs = GATE_ARCH
    VL.iron_arch(mb, x, y, zz, hs, area="SG_PropArch")
    for s_ in (-1, 1):
        court_ends(mb, mg, s_)
    mirante(mb, mg)
    mirante_path(mb)
    mb.finish()
    west_alley()
    # arvores-marco: teixo de copa alta (tronco livre ate ~7,5: o banco fica embaixo da copa), no MESMO objeto das
    # plantas do patio (1 MeshPart por material)
    mt = mg
    old = VK.SUN
    VK.SUN = VEG.MOON_DIR
    try:
        for k, (x, y) in enumerate(TREES):
            VEG.pine(mt, x, y, P3, TREE_H * (1.0 if k else 0.94), random.Random(3620 + k), "marco", 0, near=True)
            col_box("SG_VegTrunk", (2.6, 2.6, 7.0), (x, y, P3 + 3.5))
            VEG.PLACED.append((x, y, P3, VEG.crown_r("marco", TREE_H), TREE_H, "marco"))
    finally:
        VK.SUN = old
    mg.finish(recalc=False)


# ------------------------------------------------------------------ 6. pontas do patio (05.10), beco oeste (13.01), caminho do mirante (13.05)
class _Path:
    """polilinha parametrizada pelo comprimento: pt(s, o) = ponto a s do inicio, deslocado o para a DIREITA"""

    def __init__(self, pts):
        self.pts = [tuple(p) for p in pts]
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
        self.L = self.cum[-1]

    def at(self, s):
        s = max(0.0, min(self.L, s))
        for i in range(len(self.pts) - 1):
            if s <= self.cum[i + 1] or i == len(self.pts) - 2:
                a, b = self.pts[i], self.pts[i + 1]
                ln = self.cum[i + 1] - self.cum[i]
                t = (s - self.cum[i]) / ln
                tx, ty = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
                return a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, tx, ty

    def pt(self, s, o):
        x, y, tx, ty = self.at(s)
        return (x + ty * o, y - tx * o)

    def yaw(self, s):
        x, y, tx, ty = self.at(s)
        return math.atan2(ty, tx)


def _pquad(mb, P, s0, s1, o0, o1, z0, z1, m):
    """bloco entre s0..s1 (ao longo) e o0..o1 (lateral) do caminho P, de z0 a z1 (sem fundo)"""
    _cap_prism(mb, SL.ccw([P.pt(s0, o0), P.pt(s1, o0), P.pt(s1, o1), P.pt(s0, o1)]), z0, z1, m)


def _pier(mb, x, y, yaw, w, h, z=P3, m=RELM, tall_cap=True):
    """pilar de cantaria com capa e remate em piramide (topo em z + h + 0,7)"""
    mb.box((w, w, h), (x, y, z + h / 2 - 0.1), (0, 0, yaw), m, 0.0)
    mb.box((w + 0.36, w + 0.36, 0.24), (x, y, z + h + 0.02), (0, 0, yaw), CAP, 0.0)
    if tall_cap:
        FP.frustum(mb, (x, y, z + h + 0.14), w + 0.1, w + 0.1, 0.3, 0.3, 0.6, CAP, ang=yaw)


def _bench(mb, P, s, o, ln, face, z=P3, back=0.0):
    """banco de pedra ao longo do caminho: assento (ln x 1,1 a 1,55) sobre 2 pes; face = +1/-1 lado para onde olha;
    back > 0: espaldar de altura back atras"""
    x, y = P.pt(s, o)
    yaw = P.yaw(s)
    mb.box((ln, 1.1, 0.28), (x, y, z + 1.42), (0, 0, yaw), CAP, 0.0)
    for e in (-1, 1):
        lx, ly = P.pt(s + e * (ln / 2 - 0.6), o)
        mb.box((0.5, 0.9, 1.3), (lx, ly, z + 0.63), (0, 0, yaw), RELM, 0.0)
    if back:
        bx, by = P.pt(s, o - face * 0.75)
        mb.box((ln + 0.2, 0.4, back), (bx, by, z + back / 2), (0, 0, yaw), WALLM, 0.0)
        mb.box((ln + 0.5, 0.7, 0.2), (bx, by, z + back + 0.1), (0, 0, yaw), CAP, 0.0)


def court_ends(mb, mg, s):
    """FINESSE 3B (05.10): a ponta morta do patio (entre o espelho e a sebe lateral) vira um LUGAR - pergula leve
    (4 pilares de silhar, vigas e caibros de ferro) sobre um tapete de lajes, com banco de espaldar virado para o
    espelho; deriva de flores ao pe dos pilares de fora"""
    cx, cy = s * 87.5, 45.5
    hx, hy = 4.6, 3.6
    for i in range(3):
        for j in range(3):
            xa, xb = cx - hx - 0.6 + (2 * hx + 1.2) * i / 3, cx - hx - 0.6 + (2 * hx + 1.2) * (i + 1) / 3
            ya, yb = cy - hy - 0.6 + (2 * hy + 1.2) * j / 3, cy - hy - 0.6 + (2 * hy + 1.2) * (j + 1) / 3
            _slab(mb, xa + 0.06, ya + 0.06, xb - 0.06, yb - 0.06, P3 - 0.1, P3 + 0.08,
                  CAP if (i + j) % 3 != 1 else RELM)
    zt = P3 + 8.2
    for px in (cx - hx, cx + hx):
        for py in (cy - hy, cy + hy):
            mb.box((0.85, 0.85, zt - P3), (px, py, (zt + P3) / 2), (0, 0, 0), WALLM, 0.0)
            mb.box((1.2, 1.2, 0.28), (px, py, zt + 0.14), (0, 0, 0), CAP, 0.0)
    for py in (cy - hy, cy + hy):
        mb.box((2 * hx + 2.2, 0.28, 0.46), (cx, py, zt + 0.51), (0, 0, 0), IRON, 0.0)
    for k in range(6):
        px = cx - hx - 0.6 + (2 * hx + 1.2) * k / 5
        mb.box((0.2, 2 * hy + 2.0, 0.32), (px, cy, zt + 0.9), (0, 0, 0), IRON, 0.0)
    # banco de espaldar no lado de fora (olha o espelho e a fachada)
    bx = cx + s * (hx - 0.9)
    mb.box((1.1, 5.4, 0.28), (bx, cy, P3 + 1.5), (0, 0, 0), CAP, 0.0)
    for e in (-1, 1):
        mb.box((0.9, 0.5, 1.36), (bx, cy + e * 2.0, P3 + 0.72), (0, 0, 0), RELM, 0.0)
    mb.box((0.36, 5.8, 1.5), (bx + s * 0.7, cy, P3 + 2.1), (0, 0, 0), WALLM, 0.0)
    mb.box((0.62, 6.2, 0.2), (bx + s * 0.7, cy, P3 + 2.95), (0, 0, 0), CAP, 0.0)
    for py in (cy - hy, cy + hy):
        drift(mg, cx + s * (hx + 1.0), py, 0.9, 1.1, ("bell", "moon"), 51 + int(py) + (s > 0), dens=1.4)
    GD._occ(cx, cy, 5.0)


ALLEY_W = 9.2          # face do muro-jardim do beco oeste (lado do castelo), a partir do eixo da rota


def west_alley():
    """FINESSE 3B (13.01): o beco oeste (rota da saida, ~290 de comprido) ganha RITMO e ACONTECIMENTOS sem tocar a rota
    (12 de lajes do sg_village): MURO-JARDIM de silhar baixo do lado do castelo (face a 9,2 do eixo; vaos de 9,5 /
    7,5 entre PILASTRAS com remate), 2 PORTOES de pilares altos onde os grupos de pinheiros do sg_veg aparecem, 2
    NICHOS (exedra com banco curvo), a FONTE DE PAREDE com bacia e 2 bancos, o PORTICO de pilares e vigas de ferro
    atravessando o caminho no meio e 2 MIRADOUROS do lado da borda (tapete de lajes + banco de espaldar virado para o
    mar). O muro (2,2) nao tem colisao (fica fora da rota, 3,2 alem da borda das lajes); portico e fonte tem."""
    mb = MB("SG_Prop_CourtWest", COLL, random.Random(3631), detail="near")
    P = _Path(L.EXIT_ROUTE[1:])
    O = ALLEY_W
    zb, zw, zc = P3 - 0.1, P3 + 1.9, P3 + 2.16
    NICHES = (36.0, 227.0)
    FOUNT = 96.0
    PORT = 150.0
    GAPS = ((56.0, 80.2), (176.8, 200.8))
    VIEWS = (68.0, 189.0)
    feats = [(8.0, 8.0)] + [(n - 5.2, n + 5.2) for n in NICHES] + [(FOUNT - 3.4, FOUNT + 3.4)] + list(GAPS) + \
        [(PORT - 3.2, PORT + 3.2), (253.0, 253.0)]
    feats.sort()
    # vaos de muro entre as pecas, com pilastras em ritmo A-B (9,5 / 7,5)
    for (a0, a1), (b0, b1) in zip(feats, feats[1:]):
        s0, s1 = a1, b0
        if s1 - s0 < 1.0:
            continue
        n = max(1, int(round((s1 - s0) / 8.5)))
        w = [(9.5 if k % 2 == 0 else 7.5) for k in range(n)]
        kw = (s1 - s0) / sum(w)
        cur = s0
        for k in range(n):
            nxt = cur + w[k] * kw
            _pquad(mb, P, cur, nxt, O, O + 0.7, zb, zw, WALLM)
            _pquad(mb, P, cur, nxt, O - 0.16, O + 0.86, zw, zc, CAP)
            if k:
                x, y = P.pt(cur, O + 0.35)
                _pier(mb, x, y, P.yaw(cur), 1.1, 2.7)
            cur = nxt
    # pilares das pontas e dos portoes (altos)
    for sq in (8.0, 253.0) + tuple(v for g in GAPS for v in g):
        x, y = P.pt(sq, O + 0.35)
        _pier(mb, x, y, P.yaw(sq), 1.5, 3.8 if sq not in (8.0, 253.0) else 3.0)
    for sq in (PORT - 3.2, PORT + 3.2, FOUNT - 3.4, FOUNT + 3.4):
        x, y = P.pt(sq, O + 0.35)
        _pier(mb, x, y, P.yaw(sq), 1.2, 2.9)
    # NICHOS: exedra semioctogonal recuada (parede de 2,7 com capa) e banco curvo
    for sn in NICHES:
        cxy = P.pt(sn, O + 0.35)
        x0_, y0_, tx, ty = P.at(sn)
        nx, ny = ty, -tx
        R_ = 4.6
        pts = [(cxy[0] + R_ * (math.cos(th) * tx + math.sin(th) * nx), cxy[1] + R_ * (math.cos(th) * ty + math.sin(th) * ny))
               for th in [math.pi - math.pi * k / 4 for k in range(5)]]
        for a, b in zip(pts, pts[1:]):
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            yaw = math.atan2(b[1] - a[1], b[0] - a[0])
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ox, oy = mx - cxy[0], my - cxy[1]
            on = math.hypot(ox, oy)
            mx, my = mx + ox / on * 0.35, my + oy / on * 0.35
            mb.box((ln + 0.5, 0.7, 2.75), (mx, my, P3 + 1.27), (0, 0, yaw), WALLM, 0.0)
            mb.box((ln + 0.7, 1.0, 0.24), (mx, my, P3 + 2.76), (0, 0, yaw), CAP, 0.0)
            bx, by = mx - ox / on * 1.05, my - oy / on * 1.05
            mb.box((ln - 0.1, 1.05, 0.26), (bx, by, P3 + 1.45), (0, 0, yaw), CAP, 0.0)
            mb.box((0.6, 0.8, 1.32), (bx, by, P3 + 0.64), (0, 0, yaw), RELM, 0.0)
    # FONTE DE PAREDE: estela com cornija e frontao, carranca com bica, bacia semioctogonal a frente; 2 bancos
    fx, fy = P.pt(FOUNT, O + 0.35)
    fyaw = P.yaw(FOUNT)
    mb.box((5.2, 1.1, 4.4), (fx, fy, P3 + 2.1), (0, 0, fyaw), WALLM, 0.0)
    mb.box((5.9, 1.5, 0.32), (fx, fy, P3 + 4.44), (0, 0, fyaw), CAP, 0.0)
    FP.frustum(mb, (fx, fy, P3 + 4.6), 5.4, 1.2, 1.0, 0.9, 1.1, CAP, ang=fyaw)
    mx_, my_ = P.pt(FOUNT, O - 0.3)
    mb.cyl(0.75, 0.26, (mx_, my_, P3 + 2.6), (math.pi / 2, 0, fyaw), CAP, n=10, bevel=0.0)
    sx_, sy_ = P.pt(FOUNT, O - 0.9)
    mb.box((0.32, 1.3, 0.24), (sx_, sy_, P3 + 2.15), (0, 0, fyaw + math.pi / 2), CAP, 0.0)
    bas = [P.pt(FOUNT - 2.4, O - 0.2), P.pt(FOUNT + 2.4, O - 0.2), P.pt(FOUNT + 1.6, O - 2.2), P.pt(FOUNT - 1.6, O - 2.2)]
    _cap_prism(mb, SL.ccw(bas), zb, P3 + 1.0, WALLM)
    bas_in = [P.pt(FOUNT - 1.95, O - 0.35), P.pt(FOUNT + 1.95, O - 0.35), P.pt(FOUNT + 1.3, O - 1.85),
              P.pt(FOUNT - 1.3, O - 1.85)]
    _cap_prism(mb, SL.ccw(bas_in), P3 + 0.5, P3 + 1.02, WALLM)
    col_box("SG_PropAlleyFount", (5.4, 3.4, 4.6), (P.pt(FOUNT, O - 0.6)[0], P.pt(FOUNT, O - 0.6)[1], P3 + 2.3),
            (0, 0, fyaw))
    for e in (-1, 1):
        _bench(mb, P, FOUNT + e * 6.6, O - 0.85, 4.2, -1)
    # PORTICO atravessando o caminho (pilares fora dos 12 da rota; vigas a 9,4)
    zt = P3 + 9.4
    for o in (-7.6, 7.6):
        for e in (-1, 1):
            x, y = P.pt(PORT + e * 2.6, o)
            mb.box((1.05, 1.05, zt - P3), (x, y, (zt + P3) / 2 - 0.05), (0, 0, P.yaw(PORT)), WALLM, 0.0)
            mb.box((1.4, 1.4, 0.3), (x, y, zt + 0.1), (0, 0, P.yaw(PORT)), CAP, 0.0)
        x, y = P.pt(PORT, o)
        col_box("SG_PropAlleyPortico", (6.3, 1.2, zt - P3), (x, y, (zt + P3) / 2), (0, 0, P.yaw(PORT)))
    for e in (-1, 1):
        a, b = P.pt(PORT + e * 2.6, -8.6), P.pt(PORT + e * 2.6, 8.6)
        mb.box((math.hypot(b[0] - a[0], b[1] - a[1]), 0.32, 0.6), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zt + 0.55),
               (0, 0, math.atan2(b[1] - a[1], b[0] - a[0])), IRON, 0.0)
    for k in range(7):
        o = -7.6 + 15.2 * k / 6
        a, b = P.pt(PORT - 3.6, o), P.pt(PORT + 3.6, o)
        mb.box((7.2, 0.22, 0.34), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zt + 1.02), (0, 0, P.yaw(PORT)), IRON, 0.0)
    # MIRADOUROS do lado da borda: tapete de lajes, banco de espaldar virado para o mar, 2 pilaretes
    for sv in VIEWS:
        for i in range(2):
            for j in range(2):
                _pquad(mb, P, sv - 3.6 + 3.6 * i + 0.06, sv + 3.6 * i - 0.06, -6.1 - 2.3 * j, -6.1 - 2.3 * (j + 1) + 0.12,
                       P3 + 0.05, P3 + 0.34, CAP if (i + j) % 2 == 0 else RELM)
        _bench(mb, P, sv, -9.6, 5.0, -1, back=2.6)
        for e in (-1, 1):
            x, y = P.pt(sv + e * 4.3, -9.4)
            _pier(mb, x, y, P.yaw(sv), 0.9, 1.6)
    mb.finish()


MIR_PATH = None


def mirante_path(mb):
    """FINESSE 3B (13.05): o caminho de lajes do sg_village ate o mirante (150 de reta) ganha BORDADURA (meio-fio de
    cantaria chanfrado em pecas de ~6 dos 2 lados), PATAMARES (fiada mestra de cantaria atravessando a cada ~26, como
    soleiras de cantaria clara), PARES DE PILARES em 3 nos (o do meio e um PORTAL alto) e um banco de espaldar no lado
    do castelo junto do portal"""
    pts, w, z = L.STREETS[8]
    P = _Path(pts)
    zt = z + 0.30                                       # topo das lajes do sg_village (PAVE)
    hw = w / 2
    for o0, o1 in ((-hw - 0.55, -hw + 0.05), (hw - 0.05, hw + 0.55)):
        n = int(P.L / 6.2)
        for k in range(n):
            s0, s1 = P.L * k / n + 0.05, P.L * (k + 1) / n - 0.05
            if s1 > P.L - 4.0:
                s1 = P.L - 4.0
            if s1 <= s0:
                continue
            _pquad(mb, P, s0, s1, o0, o1, z - 0.05, zt + 0.18, CAP)
    for k in range(1, 7):
        sk = P.L * k / 7
        _pquad(mb, P, sk - 0.6, sk + 0.6, -hw + 0.05, hw - 0.05, zt - 0.1, zt + 0.05, CAP)
    sm = P.L * 0.5
    for sq, h in ((P.L * 0.16, 2.6), (sm, 4.2), (P.L * 0.8, 2.6)):
        for o in (-hw - 1.6, hw + 1.6):
            x, y = P.pt(sq, o)
            _pier(mb, x, y, P.yaw(sq), 1.4 if h > 3 else 1.1, h)
    _bench(mb, P, sm + 6.5, -hw - 2.2, 4.6, 1, back=2.4)


# ------------------------------------------------------------------ 5. jardim-mirante
def mirante(mb, mg):
    """terraco do jardim-mirante: lajes em 3 aneis (o terreno desce 0,45 no disco), balaustrada na borda da vista,
    banco em exedra de costas para o castelo, a arvore velha da lua inclinada para a vista e flores"""
    cx, cy, R = MIR
    R1 = R + 0.6                                  # = rebaixo do terreno
    # leito escuro (juntas) e lajes
    mb.cyl(R1, 0.5, (cx, cy, P3 - 0.55), (0, 0, 0), "Stone_SG_Floor", n=40, bevel=0.0)
    # FINESSE 3B (13.04/16.06): o disco violeta do centro saiu - ROSA DOS VENTOS de cantaria clara embutida num disco
    # de obsidiana (o mirante aponta a vista), sem emblema nem brilho
    mb.cyl(3.4, 0.4, (cx, cy, P3 - 0.25), (0, 0, 0), OBS, n=16, bevel=0.0)
    star = []
    for k in range(16):
        a = math.pi / 2 * 0 + k * math.pi / 8
        r = (2.9 if k % 4 == 0 else (1.5 if k % 2 == 0 else 0.62))
        star.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    _cap_prism(mb, star, P3 - 0.2, P3 + 0.02, CAP)
    # ONDA 3 (z-fight): o anel de fora para 0,1 antes do rebaixo (o recorte do terreno e um 32-gono de raio R1: os
    # vertices das lajes em R1 saiam pela corda e o topo ficava coplanar com a grama em P3)
    for (ra, rb, n, mats) in ((3.48, 8.6, 8, (CAP, RELM)), (8.68, 13.2, 12, (RELM, CAP)),
                              (13.28, R1 - 0.1, 18, (CAP, RELM))):
        for k in range(n):
            a0 = (k + 0.012 * 16 / n) * math.tau / n
            a1 = (k + 1 - 0.012 * 16 / n) * math.tau / n
            arc0 = [(cx + ra * math.cos(a0 + (a1 - a0) * t / 2), cy + ra * math.sin(a0 + (a1 - a0) * t / 2))
                    for t in range(3)]
            arc1 = [(cx + rb * math.cos(a1 - (a1 - a0) * t / 2), cy + rb * math.sin(a1 - (a1 - a0) * t / 2))
                    for t in range(3)]
            _cap_prism(mb, SL.ccw(arc0 + arc1), P3 - 0.3, P3, mats[k % 2])
    # balaustrada (arco da vista): plinto, balaustres torneados, corrimao em pecas, pedestais a cada ~30 graus
    rb_ = R - 0.4
    a0, a1 = MIR_VIEW
    nped = 6
    peds = [a0 + (a1 - a0) * k / nped for k in range(nped + 1)]
    for k in range(nped):
        pa, pbb = math.radians(peds[k]), math.radians(peds[k + 1])
        seg = 4
        for j in range(seg):
            q0 = pa + (pbb - pa) * j / seg
            q1 = pa + (pbb - pa) * (j + 1) / seg
            c0 = (cx + rb_ * math.cos(q0), cy + rb_ * math.sin(q0))
            c1 = (cx + rb_ * math.cos(q1), cy + rb_ * math.sin(q1))
            ln = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
            mid = ((c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2)
            yaw = math.atan2(c1[1] - c0[1], c1[0] - c0[0])
            mb.box((ln + 0.04, 1.1, 0.5), (mid[0], mid[1], P3 + 0.25), (0, 0, yaw), WALLM, 0.0)
            mb.box((ln + 0.06, 1.0, 0.26), (mid[0], mid[1], P3 + 2.85), (0, 0, yaw), CAP, 0.0)
            EM._lathe(mb, (mid[0], mid[1], P3 + 0.5), [(0.18, 0.0), (0.32, 0.8), (0.14, 1.55), (0.24, 2.22)], RELM, 6)
    for a in peds:
        ra = math.radians(a)
        px, py = cx + rb_ * math.cos(ra), cy + rb_ * math.sin(ra)
        mb.box((1.5, 1.5, 3.3), (px, py, P3 + 1.6), (0, 0, ra), WALLM, 0.06)
        mb.box((1.8, 1.8, 0.24), (px, py, P3 + 3.36), (0, 0, ra), CAP, 0.0)
        EM._lathe(mb, (px, py, P3 + 3.48), [(0.42, 0.0), (0.5, 0.2), (0.3, 0.55), (0.0, 0.8)], CAP, 8)
    for k in range(4):
        qa = math.radians(a0 + (a1 - a0) * k / 4)
        qb = math.radians(a0 + (a1 - a0) * (k + 1) / 4)
        qm = (qa + qb) / 2
        ln = 2 * rb_ * math.sin((qb - qa) / 2) + 0.6
        col_box("SG_PropBalustrade", (ln, 1.2, 3.4), (cx + rb_ * math.cos(qm) * math.cos((qb - qa) / 2),
                                                      cy + rb_ * math.sin(qm) * math.cos((qb - qa) / 2), P3 + 1.7),
                (0, 0, qm + math.pi / 2))
    # banco em EXEDRA (oeste, de frente para a vista): assento curvo + encosto com remate + pes; voluta nas pontas
    e0, e1, er = MIR_EXEDRA
    nseg = 9
    for j in range(nseg):
        q0 = math.radians(e0 + (e1 - e0) * j / nseg)
        q1 = math.radians(e0 + (e1 - e0) * (j + 1) / nseg)
        for (r0, r1, z0, z1, m) in ((er - 0.9, er + 0.9, P3 + 1.4, P3 + 1.75, CAP),
                                    (er + 0.9, er + 1.5, P3 + 0.0, P3 + 3.6, WALLM),
                                    (er + 0.8, er + 1.6, P3 + 3.6, P3 + 3.85, CAP)):
            pts = [(cx + r0 * math.cos(q0), cy + r0 * math.sin(q0)), (cx + r1 * math.cos(q0), cy + r1 * math.sin(q0)),
                   (cx + r1 * math.cos(q1), cy + r1 * math.sin(q1)), (cx + r0 * math.cos(q1), cy + r0 * math.sin(q1))]
            _cap_prism(mb, SL.ccw(pts), z0, z1, m)
        if j % 2 == 0:
            qm = (q0 + q1) / 2
            mb.box((1.3, 0.6, 1.42), (cx + (er - 0.1) * math.cos(qm), cy + (er - 0.1) * math.sin(qm), P3 + 0.69),
                   (0, 0, qm), RELM, 0.0)
    for q in (e0, e1):
        qr = math.radians(q)
        px, py = cx + (er + 0.3) * math.cos(qr), cy + (er + 0.3) * math.sin(qr)
        mb.box((2.6, 0.9, 2.4), (px, py, P3 + 1.2), (0, 0, qr), WALLM, 0.08)
        EM._lathe_ax(mb, (px, py, P3 + 2.4), (math.cos(qr + math.pi / 2), math.sin(qr + math.pi / 2), 0.0),
                     [(0.0, -0.6), (0.62, -0.52), (0.7, 0.0), (0.62, 0.52), (0.0, 0.6)], CAP, 8)
    for k in range(5):
        qa = math.radians(e0 + (e1 - e0) * k / 5)
        qb = math.radians(e0 + (e1 - e0) * (k + 1) / 5)
        qm = (qa + qb) / 2
        ln = 2 * er * math.sin((qb - qa) / 2)
        col_box("SG_PropBench", (ln, 2.6, 1.75), (cx + (er + 0.2) * math.cos(qm), cy + (er + 0.2) * math.sin(qm),
                                                   P3 + 0.875), (0, 0, qm + math.pi / 2))
    # FINESSE 3B (13.04): composicao do mirante - PERGULA de ferro sobre o banco em exedra (pilares de silhar atras do
    # encosto, colunas de ferro na frente, 2 vigas curvas e caibros radiais: a trepadeira e do sg_garden), MESA DE
    # PEDRA com 2 bancos a nordeste, LUNETA de bronze apontada para a vista (o ponto focal na balaustrada) e 2
    # CANTEIROS baixos ladeando a chegada
    rp, rf, zt = 14.7, 10.3, P3 + 8.6
    for a in (140.0, 160.0, 180.0, 200.0, 220.0):
        ar = math.radians(a)
        px, py = cx + rp * math.cos(ar), cy + rp * math.sin(ar)
        mb.box((0.9, 0.9, zt - P3), (px, py, (zt + P3) / 2), (0, 0, ar), WALLM, 0.0)
        mb.box((1.25, 1.25, 0.3), (px, py, zt + 0.15), (0, 0, ar), CAP, 0.0)
    for a in (146.0, 180.0, 214.0):
        ar = math.radians(a)
        px, py = cx + rf * math.cos(ar), cy + rf * math.sin(ar)
        mb.box((0.8, 0.8, 0.5), (px, py, P3 + 0.25), (0, 0, ar), CAP, 0.0)
        mb.rod((px, py, P3 + 0.5), (px, py, zt + 0.3), 0.2, IRON, n=8)
    beam = [(-0.14, -0.22), (0.14, -0.22), (0.14, 0.22), (-0.14, 0.22)]
    for r_, z_ in ((rp, zt + 0.52), (rf, zt + 0.52)):
        pts = [(cx + r_ * math.cos(math.radians(a)), cy + r_ * math.sin(math.radians(a)), z_)
               for a in range(134, 228, 8)]
        mb.sweep(pts, beam, IRON, True, None)
    for a in range(136, 228, 10):
        ar = math.radians(a)
        rm = (rp + rf) / 2
        mb.box((rp - rf + 1.8, 0.2, 0.34), (cx + rm * math.cos(ar), cy + rm * math.sin(ar), zt + 0.91), (0, 0, ar), IRON,
               0.0)
    # mesa de pedra redonda com 2 bancos (nordeste, entre a arvore e a vista)
    ta = math.radians(52.0)
    tx_, ty_ = cx + 8.2 * math.cos(ta), cy + 8.2 * math.sin(ta)
    EM._lathe(mb, (tx_, ty_, P3), [(0.95, 0.0), (0.95, 0.22), (0.5, 0.5), (0.4, 1.9), (0.62, 2.2)], RELM, 10)
    mb.cyl(1.7, 0.24, (tx_, ty_, P3 + 2.32), (0, 0, 0), CAP, n=14, bevel=0.0)
    col_box("SG_PropMirTable", (2.8, 2.8, 2.45), (tx_, ty_, P3 + 1.22))
    for sd in (-1, 1):
        bx, by = tx_ + sd * 3.0 * math.cos(ta), ty_ + sd * 3.0 * math.sin(ta)
        mb.box((1.1, 3.4, 0.3), (bx, by, P3 + 1.5), (0, 0, ta), CAP, 0.0)
        for e in (-1, 1):
            mb.box((0.9, 0.5, 1.36), (bx - e * 1.2 * math.sin(ta), by + e * 1.2 * math.cos(ta), P3 + 0.67), (0, 0, ta),
                   RELM, 0.0)
    # LUNETA de bronze num pedestal torneado, apontada para leste (a vista), um pouco acima do horizonte
    la = math.radians(-16.0)
    lx, ly = cx + 12.2 * math.cos(la), cy + 12.2 * math.sin(la)
    EM._lathe(mb, (lx, ly, P3), [(0.78, 0.0), (0.78, 0.26), (0.42, 0.5), (0.3, 2.5), (0.52, 2.72), (0.52, 2.92)], RELM, 8)
    mb.box((0.5, 0.7, 0.6), (lx, ly, P3 + 3.2), (0, 0, la), "Metal_Gold", 0.0)
    el = math.radians(10.0)
    mb.cyl(0.26, 2.8, (lx + 0.3 * math.cos(la), ly + 0.3 * math.sin(la), P3 + 3.62), (0, math.pi / 2 - el, la),
           "Metal_Gold", n=8, r2=0.36, bevel=0.0)
    col_box("SG_PropMirScope", (1.6, 1.6, 3.6), (lx, ly, P3 + 1.8))
    # 2 canteiros baixos (meio-fio de cantaria octogonal + terra) ladeando a chegada do caminho (sul)
    for k, a in enumerate((250.0, 290.0)):
        ar = math.radians(a)
        qx, qy = cx + 12.6 * math.cos(ar), cy + 12.6 * math.sin(ar)
        ring(mb, (qx, qy), 1.55, 1.95, P3 - 0.05, P3 + 0.55, CAP, n=8)
        _cap_prism(mb, ngon((qx, qy), 1.6, 8), P3 - 0.05, P3 + 0.38, SOIL)
        drift(mg, qx, qy, 1.35, 1.35, ("moon", "spike") if k else ("spike", "bell"), 81 + k, z=P3 + 0.38, dens=3.2,
              ctx="mirante")
    # flores: atras do encosto (faixa de lavanda e lua) e em volta da arvore
    for k in range(3):
        q = math.radians(e0 + 25.0 + 35.0 * k)
        drift(mg, cx + (er + 3.4) * math.cos(q), cy + (er + 3.4) * math.sin(q), 2.6, 0.9,
              ("spike", "moon") if k != 1 else ("moon", "bell"), 61 + k, rot=q + math.pi / 2, dens=1.2, ctx="mirante")
    tx, ty = MIR_TREE
    drift(mg, tx - 2.4, ty + 1.8, 1.6, 1.1, ("bell", "moon"), 67, dens=1.3, ctx="mirante")
    for k, (dx, dy) in enumerate(((-3.0, -2.6), (2.6, 2.8))):
        shrub(mg, tx + dx, ty + dy, P3, 1.1, 71 + k)
    # a ARVORE VELHA DA LUA: tronco grosso e torto inclinado para leste (a vista), bracos e almofadas de saia (no
    # mesmo objeto das plantas do patio: 1 MeshPart por material)
    old = VK.SUN
    VK.SUN = VEG.MOON_DIR
    try:
        moon_tree(mg, tx, ty, P3, 17.0, random.Random(3703))
    finally:
        VK.SUN = old
    col_box("SG_VegTrunk", (2.4, 2.4, 7.0), (tx, ty, P3 + 3.5))
    VEG.PLACED.append((tx, ty, P3, 6.0, 17.0, "moon"))


def moon_tree(mb, x, y, z, h, rng):
    """pinheiro velho em guarda-chuva, inclinado para a vista (+X): tronco em 4 lances, bracos e almofadas achatadas
    de saia caida (as de cima com o luar). Materiais da ilha (folha / luar / fundo / casca)."""
    from mathutils import Vector
    tr = h * 0.075
    p0 = Vector((x, y, z - 0.6))
    p1 = Vector((x + h * 0.06, y - h * 0.02, z + h * 0.3))
    p2 = Vector((x + h * 0.22, y + h * 0.03, z + h * 0.56))
    p3 = Vector((x + h * 0.36, y + h * 0.01, z + h * 0.8))
    VK.ttube(mb, [p0, p1, p2, p3], [tr * 1.5, tr * 1.05, tr * 0.8, tr * 0.5], VEG.BARK, n=7, cap1=False)
    # raizes de pe
    for k in range(4):
        a = k * math.tau / 4 + 0.5
        VK.ttube(mb, [(x + math.cos(a) * tr * 0.4, y + math.sin(a) * tr * 0.4, z + tr * 1.1),
                      (x + math.cos(a) * tr * 2.1, y + math.sin(a) * tr * 2.1, z - 0.25)], [tr * 0.55, tr * 0.2],
                 VEG.BARK, n=4, cap1=False)
    pads = [(p3 + Vector((0.4, 0.0, h * 0.04)), h * 0.27, True)]
    arms = ((p1.lerp(p2, 0.5), 2.6, 0.28, 0.10), (p2, 0.9, 0.3, 0.14), (p2.lerp(p3, 0.4), -0.7, 0.26, 0.12),
            (p1.lerp(p2, 0.85), -2.2, 0.24, 0.08))
    for base, a, ln, up in arms:
        end = base + Vector((math.cos(a) * h * ln, math.sin(a) * h * ln, h * up))
        mid = base.lerp(end, 0.5) + Vector((0, 0, h * 0.05))
        VK.ttube(mb, [base, mid, end], [tr * 0.55, tr * 0.42, tr * 0.28], VEG.BARK, n=5, cap1=False)
        pads.append((end, h * rng.uniform(0.18, 0.22), False))
    for (pc, pr, top) in pads:
        VK.skirt(mb, (pc.x, pc.y, pc.z), pr, pr * 0.62, 7, VEG.LEAF, rng, droop=22, lob=0.26, shoulder=0.55,
                 under=0.12, under_m=VEG.SHADE, lit=VEG.MOON, lit_k=0.35 if top else 0.5, jit=0.14)


def build():
    GD.reset()
    nf = court_floor()
    court()
    print("COURT chao=%d trapezios; gramados=%d espelhos=%d estatuas=%d arvores-marco=%d" % (
        nf, len(lawn_rects()), len(POOLS), len(STATUES), len(TREES)))
