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
# API usada por outros modulos (nao mudar): hooded_figure, bez, _loft, _lathe_ax, RUNE_SEGS, OBELISK_RUNES, _glyph,
# COURT_LIGHTS.
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
STATUES = [(-21.0, 34.5), (21.0, 34.5)]
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


def hooded_figure(mb, F, s, z0, body, void=OBS, kind="guard"):
    """a FIGURA da ordem (estatuas do patio e coroamento da fonte da praca). Referencial F (local +Y = frente),
    escala s, z0 = pe da figura (local). Altura ~7,3 s.
    OVERHAUL 01 (2026-09-29): GUARDIAO DE PEDRA em armadura fantastica estilizada, massas planas e duras (nada de
    cone/saco inflavel): sapatos, grevas e joelheiras, coxotes, saia de lamas, peitoral com quilha, cinto, gorjal,
    ESPALDEIRAS em 2 lamas, bracos com cotoveleira e manopla, as 2 maos (uma sobre a outra) no punho da ESPADA fincada
    a frente; tabardo liso na frente e MANTO de dobras duras nas costas (base larga = silhueta heroica).
    Espada de verdade: lamina de secao em losango com SULCO, ponta entrando no plinto, guarda em perfil curvo com
    quillons caidos e pontas em gota, punho com anel, pomo facetado com colar. Lamina e punho um valor MAIS ESCUROS que
    o corpo (le objeto na mao).
    kind: 'guard' (as guardas do portao do castelo: ELMO fechado com viseira em cruz e crista baixa, capuz caido nas
    costas) ou 'hood' (o marco da praca: CAPUZ de formas definidas com a borda dobrada e o vazio escuro do rosto)."""
    from mathutils import Vector

    def W(x, y, z):
        return F.p(x * s, y * s, z0 + z * s)

    def ell(cx, cy, z, rx, ryf, ryb=None, n=8, ridge=0.0, ph=math.pi / 2):
        """secao eliptica (frente ryf, costas ryb) com n pontos, o 1o na frente; ridge = quilha na frente"""
        ryb = ryf if ryb is None else ryb
        out = []
        for k in range(n):
            a = ph + 2 * math.pi * k / n
            ca, sa = math.cos(a), math.sin(a)
            yy = (ryf if sa > 0 else ryb) * sa
            if k == 0:
                yy += ridge
            out.append(W(cx + rx * ca, cy + yy, z))
        return out
    blade_m = BLADE_OF.get(body, "Stone_SG_Floor")
    # ---- pernas (x = +-0,40): sapato, greva, joelheira, coxote
    for sg in (-1, 1):
        x = sg * 0.40
        foot0 = [(-0.21, -0.30), (0.21, -0.30), (0.21, 0.40), (0.0, 0.62), (-0.21, 0.40)]
        foot1 = [(-0.20, -0.28), (0.20, -0.28), (0.20, 0.12), (0.0, 0.26), (-0.20, 0.12)]
        _loft(mb, [[W(x + a, b, 0.0) for a, b in foot0], [W(x + a, b, 0.34) for a, b in foot1]], body)
        _loft(mb, [ell(x, 0.0, 0.30, 0.21, 0.22), ell(x, 0.02, 0.92, 0.25, 0.29, 0.26),
                   ell(x, 0.02, 1.55, 0.23, 0.25)], body)
        _loft(mb, [ell(x, 0.03, 1.48, 0.25, 0.27), ell(x, 0.05, 1.70, 0.30, 0.30, 0.27, ridge=0.08),
                   ell(x, 0.03, 1.95, 0.25, 0.26)], body)
        _loft(mb, [ell(x, 0.02, 1.90, 0.26, 0.28), ell(sg * 0.36, 0.0, 3.30, 0.32, 0.33)], body)
    # ---- saia de lamas (2 lamas escalonadas) e tabardo
    _loft(mb, [ell(0, -0.02, 3.95, 0.60, 0.42, 0.44, 10), ell(0, -0.02, 3.52, 0.74, 0.50, 0.50, 10)], body)
    _loft(mb, [ell(0, -0.02, 3.60, 0.70, 0.48, 0.48, 10), ell(0, -0.02, 3.12, 0.82, 0.54, 0.54, 10)], body)
    tab = [(-0.34, 3.40), (0.34, 3.40), (0.31, 1.40), (0.0, 1.08), (-0.31, 1.40)]
    _loft(mb, [[W(a, 0.42, b) for a, b in tab], [W(a, 0.52, b) for a, b in tab]], body)
    # ---- manto nas costas: arco externo com dobras duras (amplitude cresce para baixo) + linha interna
    M = 10
    secs = []
    for z, hw, yb, yi, amp in ((5.50, 0.92, -0.66, -0.26, 0.0), (4.70, 1.00, -0.72, -0.30, 0.03),
                               (3.20, 1.12, -0.80, -0.34, 0.06), (1.60, 1.20, -0.88, -0.36, 0.08),
                               (0.02, 1.26, -0.94, -0.38, 0.09)):
        outer, inner = [], []
        for i in range(M + 1):
            ph = math.pi * i / M
            fold = amp * (1 if i % 2 else -0.6) if 0 < i < M else 0.0
            px = (hw + fold) * math.cos(ph)
            py = yi - (yi - yb + fold) * math.sin(ph)
            outer.append(W(px, py, z))
        for i in range(M + 1):
            xx = -hw * 0.9 + 1.8 * hw * i / M
            inner.append(W(xx, yi + 0.02, z))
        secs.append(outer + inner)
    _loft(mb, secs, body, "strip", "strip", strip=M)
    # ---- tronco: peitoral com quilha, cinto, gorjal
    _loft(mb, [ell(0, -0.02, 3.88, 0.56, 0.36, 0.40, 10), ell(0, -0.02, 4.30, 0.66, 0.44, 0.44, 10, 0.02),
               ell(0, -0.02, 4.90, 0.74, 0.52, 0.48, 10, 0.07), ell(0, -0.02, 5.45, 0.72, 0.42, 0.46, 10, 0.03),
               ell(0, -0.04, 5.72, 0.46, 0.26, 0.34, 10)], body)
    _loft(mb, [ell(0, -0.02, 3.84, 0.61, 0.42, 0.45, 10), ell(0, -0.02, 4.02, 0.62, 0.43, 0.46, 10)], body)
    _loft(mb, [ell(0, -0.04, 5.60, 0.40, 0.36, 0.38, 8), ell(0, -0.04, 6.02, 0.30, 0.28, 0.30, 8)], body)
    # ---- espaldeiras: calota + lama de baixo, apontando para fora e um pouco para cima
    for sg in (-1, 1):
        o = W(sg * 0.74, -0.04, 5.36)
        ax = F.p(sg * 0.9, 0.0, 0.45) - F.p(0.0, 0.0, 0.0)
        _lathe_ax(mb, o, ax, [(0.54 * s, -0.28 * s), (0.58 * s, -0.06 * s), (0.50 * s, 0.16 * s),
                              (0.34 * s, 0.32 * s), (0.0, 0.42 * s)], body, 8)
        o2 = W(sg * 0.86, -0.04, 5.10)
        _lathe_ax(mb, o2, ax, [(0.50 * s, -0.20 * s), (0.60 * s, -0.04 * s), (0.54 * s, 0.10 * s),
                               (0.30 * s, 0.14 * s)], body, 8)
    # ---- bracos: ombro -> cotovelo -> punho; manopla fechada no punho da espada (direita em cima)
    YS = 0.98                                            # plano da espada (local y)
    hands = {1: 4.10, -1: 3.78}                          # altura do centro de cada mao
    for sg in (-1, 1):
        J = Vector((sg * 0.80, -0.02, 5.22))
        E = Vector((sg * 0.80, 0.24, 4.36))
        zh = hands[sg]
        Wr = Vector((sg * 0.30, YS - 0.06, zh + 0.02))
        wJ, wE, wW = W(*J), W(*E), W(*Wr)
        _lathe_ax(mb, wJ, wE - wJ, [(0.21 * s, 0.0), (0.18 * s, (wE - wJ).length)], body, 8)
        _lathe_ax(mb, wE, wW - wE, [(0.18 * s, -0.04 * s), (0.16 * s, (wW - wE).length - 0.14 * s),
                                    (0.22 * s, (wW - wE).length - 0.06 * s), (0.25 * s, (wW - wE).length + 0.06 * s)],
                  body, 8)
        ce = W(sg * 0.86, 0.18, 4.34)
        _lathe_ax(mb, ce, F.p(sg * 0.55, -0.6, -0.1) - F.p(0, 0, 0), [(0.22 * s, -0.06 * s), (0.20 * s, 0.08 * s),
                                                                     (0.10 * s, 0.18 * s), (0.0, 0.21 * s)], body, 6)
        # manopla: punho fechado envolvendo o cabo (o cabo passa pelo meio): loft de secoes chanfradas com os nos dos
        # dedos saltando na frente; o polegar da mao de cima dobra sobre o indicador
        cxh = sg * 0.07

        def fsec(z, hx, hy, ch, knuck=0.0):
            pts = [(-hx + ch, -hy), (hx - ch, -hy), (hx, -hy + ch), (hx, hy - ch), (hx - ch, hy + knuck),
                   (-hx + ch, hy + knuck), (-hx, hy - ch), (-hx, -hy + ch)]
            return [W(cxh + a, YS + b, z) for a, b in pts]
        _loft(mb, [fsec(zh - 0.16, 0.14, 0.14, 0.05), fsec(zh - 0.07, 0.19, 0.18, 0.06, 0.04),
                   fsec(zh + 0.09, 0.19, 0.18, 0.06, 0.04), fsec(zh + 0.16, 0.15, 0.14, 0.05)], body)
        if sg > 0:
            _lathe_ax(mb, W(cxh + 0.16, YS + 0.10, zh + 0.12), W(cxh - 0.06, YS + 0.20, zh + 0.10)
                      - W(cxh + 0.16, YS + 0.10, zh + 0.12), [(0.055 * s, 0.0), (0.05 * s, 0.2 * s), (0.0, 0.26 * s)],
                      body, 6)
    # ---- cabeca
    if kind == "hood":
        # capuz em CASCA de espessura 0,1: arco aberto na frente (a abertura estreita embaixo e no alto: ogiva), bico
        # caindo para tras; a borda da abertura e a propria espessura da casca. Dentro, o vazio escuro recuado.
        secs = []
        for z, cy, rx, ry, al in ((5.60, -0.06, 0.64, 0.58, 16.0), (6.00, -0.02, 0.52, 0.52, 34.0),
                                  (6.45, 0.00, 0.49, 0.52, 40.0), (6.85, -0.04, 0.42, 0.50, 30.0),
                                  (7.12, -0.20, 0.28, 0.40, 14.0)):
            a0, a1 = math.radians(90.0 + al), math.radians(450.0 - al)
            M2 = 12
            outer = [W(rx * math.cos(a0 + (a1 - a0) * i / M2), cy + ry * math.sin(a0 + (a1 - a0) * i / M2), z)
                     for i in range(M2 + 1)]
            inner = [W((rx - 0.1) * math.cos(a1 - (a1 - a0) * i / M2), cy + (ry - 0.1) * math.sin(a1 - (a1 - a0) * i / M2), z)
                     for i in range(M2 + 1)]
            secs.append(outer + inner)
        secs.append([W(0.0, -0.58, 7.32)])
        _loft(mb, secs, body, "strip", None, strip=12)
        _loft(mb, [ell(0, -0.04, 5.80, 0.34, 0.26, 0.34, 8), ell(0, -0.02, 6.45, 0.40, 0.30, 0.40, 8),
                   ell(0, -0.06, 6.90, 0.30, 0.26, 0.32, 8), [W(0.0, -0.10, 7.08)]], void)
    else:
        _loft(mb, [ell(0, 0.02, 5.94, 0.36, 0.36, 0.36, 8), ell(0, 0.02, 6.10, 0.43, 0.44, 0.42, 8),
                   ell(0, 0.02, 6.56, 0.45, 0.46, 0.43, 8, 0.05), ell(0, 0.02, 6.88, 0.42, 0.43, 0.41, 8, 0.04),
                   ell(0, 0.0, 7.06, 0.33, 0.33, 0.33, 8), ell(0, 0.0, 7.17, 0.17, 0.17, 0.17, 8),
                   [W(0.0, 0.0, 7.21)]], body)
        # viseira em cruz: fenda horizontal + reforco vertical (vazio escuro e nervura de pedra)
        _loft(mb, [[W(a, 0.36, b) for a, b in ((-0.30, 6.56), (0.30, 6.56), (0.28, 6.64), (-0.28, 6.64))],
                   [W(a, 0.50, b) for a, b in ((-0.30, 6.56), (0.30, 6.56), (0.28, 6.64), (-0.28, 6.64))]], void)
        _loft(mb, [[W(a, 0.40, b) for a, b in ((-0.05, 6.14), (0.05, 6.14), (0.05, 6.52), (-0.05, 6.52))],
                   [W(a, 0.52, b) for a, b in ((-0.05, 6.14), (0.05, 6.14), (0.05, 6.52), (-0.05, 6.52))]], body)
        # crista baixa ao longo do elmo
        cr = [(-0.30, 7.04), (0.26, 7.06), (0.14, 7.34), (-0.22, 7.38)]
        _loft(mb, [[W(-0.05, b, c) for b, c in cr], [W(0.05, b, c) for b, c in cr]], body)
        # capuz caido nas costas (a ordem): rolo de tecido de pedra atras do gorjal
        _loft(mb, [ell(0, -0.42, 5.56, 0.56, 0.26, 0.30, 8), ell(0, -0.48, 5.92, 0.46, 0.24, 0.28, 8),
                   ell(0, -0.46, 6.14, 0.28, 0.14, 0.16, 8)], body)
    # ---- ESPADA fincada a frente
    def blade_sec(z, hw, t, groove=True):
        g = 0.45 if groove else 1.0
        pts = [(-hw, 0.0), (-0.4 * hw, t), (0.0, g * t), (0.4 * hw, t), (hw, 0.0), (0.4 * hw, -t), (0.0, -g * t),
               (-0.4 * hw, -t)]
        return [W(a, YS + b, z) for a, b in pts]
    _loft(mb, [[W(0.0, YS, -0.14)], blade_sec(0.42, 0.16, 0.055, False), blade_sec(0.62, 0.17, 0.056),
               blade_sec(2.70, 0.21, 0.06), blade_sec(3.02, 0.21, 0.06, False)], blade_m, None, "fan")
    # guarda: perfil curvo com os quillons caindo, secao em losango, pontas em gota; escudete no centro
    gp = []
    for i in range(9):
        x = -0.62 + 1.24 * i / 8
        gp.append(W(x, YS, 3.10 - 0.26 * (abs(x) / 0.62) ** 2))
    nrm = F.p(0.0, 1.0, 0.0) - F.p(0.0, 0.0, 0.0)
    mb.sweep(gp, [(0.0, 0.09 * s), (0.075 * s, 0.0), (0.0, -0.09 * s), (-0.075 * s, 0.0)], blade_m, True, None,
             up=tuple(nrm))
    for sg in (-1, 1):
        tip = W(sg * 0.62, YS, 2.84)
        _lathe_ax(mb, tip, W(sg * 0.66, YS, 2.62) - tip, [(0.0, -0.04 * s), (0.09 * s, 0.05 * s), (0.10 * s, 0.13 * s),
                                                         (0.0, 0.27 * s)], blade_m, 6)
    esc = [(-0.13, 2.94), (0.13, 2.94), (0.16, 3.22), (0.0, 3.30), (-0.16, 3.22)]
    _loft(mb, [[W(a, YS - 0.12, b) for a, b in esc], [W(a, YS + 0.12, b) for a, b in esc]], blade_m)
    # punho (com anel a mostra entre a guarda e as maos) e pomo facetado com colar
    EM._lathe(mb, tuple(W(0.0, YS, 0.0)), [(0.08 * s, 3.20 * s), (0.09 * s, 3.28 * s), (0.09 * s, 3.40 * s),
                                           (0.115 * s, 3.45 * s), (0.09 * s, 3.50 * s), (0.09 * s, 4.25 * s),
                                           (0.08 * s, 4.30 * s)], blade_m, 8, math.pi / 8)
    EM._lathe(mb, tuple(W(0.0, YS, 0.0)), [(0.07 * s, 4.27 * s), (0.13 * s, 4.32 * s), (0.13 * s, 4.37 * s),
                                           (0.09 * s, 4.40 * s), (0.19 * s, 4.47 * s), (0.21 * s, 4.56 * s),
                                           (0.19 * s, 4.65 * s), (0.08 * s, 4.71 * s), (0.0, 4.73 * s)], blade_m, 8,
              math.pi / 8)


def statue(mb, x, y, z, yaw):
    """estatua da ordem: o GUARDIAO de pedra (hooded_figure 'guard': armadura, elmo, espada fincada) sobre pedestal de
    obsidiana com dado de pedra violeta. Overhaul 01: o dado ganhou PAINEL rebaixado com moldura de obsidiana nas 4
    faces e a placa com emblema SAIU (16.02/12.11: o emblema da porta e da fachada ja estao no quadro). Local +Y =
    frente (yaw)."""
    F = SL.Frame(x, y, z, yaw - math.pi / 2)
    a = F.a
    # pedestal com MOLDURAS: soco, chanfro de assento, dado violeta com paineis, cornija em talude + filete, plinto
    mb.box((3.6, 3.6, 0.6), F.p(0, 0, 0.3), F.r(), OBS, 0.1)
    FP.frustum(mb, tuple(F.p(0, 0, 0.6)), 3.6, 3.6, 2.8, 2.8, 0.3, OBS, ang=a)
    mb.box((2.7, 2.7, 2.5), F.p(0, 0, 0.9 + 1.25), F.r(), VIO, 0.08)
    for k in range(4):
        Fk = SL.Frame(x, y, z, a + k * math.pi / 2)
        for sg in (-1, 1):
            mb.box((0.16, 0.12, 1.9), Fk.p(sg * 0.98, 1.39, 2.15), Fk.r(), OBS, 0.0)
        for zz in (1.2, 3.1):
            mb.box((2.12, 0.12, 0.16), Fk.p(0.0, 1.39, zz), Fk.r(), OBS, 0.0)
    # overhaul 03 (03.03): cornija em CAVETE (curva concava em 3 lances) no lugar do talude reto
    for zc_, w0_, w1_, hc_ in ((3.4, 2.72, 2.8, 0.13), (3.53, 2.8, 3.02, 0.1), (3.63, 3.02, 3.4, 0.09)):
        FP.frustum(mb, tuple(F.p(0, 0, zc_)), w0_, w0_, w1_, w1_, hc_, CAP, ang=a)
    mb.box((3.4, 3.4, 0.12), F.p(0, 0, 3.78), F.r(), CAP, 0.0)
    mb.box((3.0, 3.0, 0.23), F.p(0, 0, 3.935), F.r(), OBS, 0.06)
    # guardiao em cantaria clara (um valor abaixo do antigo Stone_SG_Trim): le contra a fachada escura
    hooded_figure(mb, F, 1.0, 4.05, CAP, kind="guard")
    col_box("SG_PropStatue", (3.6, 3.6, 11.0), (x, y, z + 5.5), (0, 0, yaw))


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


def wobble_closed(pts, amp, seed, step=1.6):
    """contorno fechado com a borda ondulada (para fora/dentro pela normal), amostrado a cada 'step'"""
    import sg_terrain as TER
    ph = (seed % 97) * 0.37
    out = []
    for i, (x, y, nx, ny) in enumerate(TER.resample_closed(pts, step)):
        w = _wob(i * step, ph, amp)
        out.append((x + nx * w, y + ny * w))
    return out


def wobble_ribbon(cl, hw, amp, seed, step=1.5):
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
    noble_path(mb, AXIS_Y[0], AXIS_Y[1], 2 * AXIS_HW, P3, thread_m=THREAD_CASTLE, zb=P3 - 0.55)
    mb.finish(recalc=False)
    return nf


def noble_path(mb, y0, y1, W, z, thread_m=THREAD_CASTLE, zb=None, row=3.0):
    """eixo nobre ao longo de +Y (x = 0): leito de obsidiana (juntas/canal do fio) + bordas de obsidiana com filete de
    cantaria + lajes de marmore negro em ritmo A-B (2,4 / 3,6) com chanfro + fio violeta baixo no centro + junta de
    prata a cada 8 fiadas. zb = fundo do leito (o terreno do patio desce 0,45: o leito fecha o rebaixo)"""
    hw = W / 2.0
    bd = 0.9
    zb = z - 0.2 if zb is None else zb
    mb.box2((-hw, y0, zb), (hw, y1, z - 0.16), OBS, 0.0)
    for s in (-1, 1):
        xa, xb = sorted((s * (hw - 0.24), s * (hw - bd)))
        mb.box2((xa, y0, z - 0.2), (xb, y1, z + 0.0), OBS, 0.0)
        xa, xb = sorted((s * hw, s * (hw - 0.24)))
        mb.box2((xa, y0, z - 0.15), (xb, y1, z + 0.12), CAP, 0.0)
    Lr = y1 - y0
    pat = (2.4, 3.6)
    rows, acc = [], 0.0
    while acc < Lr - 0.6 or not rows:
        rows.append(pat[len(rows) % 2])
        acc += rows[-1]
    k_ = Lr / acc
    xin, xout = 0.55, hw - bd - 0.12
    yy = y0
    for k, ln in enumerate(rows):
        ya, yb = yy + 0.06, yy + ln * k_ - 0.06
        for s in (-1, 1):
            xa, xb = sorted((s * xin, s * xout))
            mb.box2((xa, ya, z - 0.1), (xb, yb, z + 0.05), MARB, 0.04)
        if k > 0 and k % 8 == 0:
            mb.box2((-xout, yy - 0.06, z - 0.2), (xout, yy + 0.06, z - 0.04), SILVER, 0.0)
        yy += ln * k_
    mb.box2((-0.14, y0, z - 0.2), (0.14, y1, z + 0.08), thread_m, 0.0)


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
        mb.box2((xs[0], ys[0], zl - 0.05), (xs[-1], ys[-1], zl + 0.4), RELM, 0.03)
        # fiada intermediaria (junta horizontal rebaixada: faixa 0,06 para dentro da face, 0,12 de altura)
        # capa em pecas: 0,12 para fora dos 2 lados, pingadeira
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        nseg = max(1, int(round(ln / 2.4)))
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
            mb.box((1.7, 1.7, 0.16), (px, py, P3 + 1.03), (0, 0, 0), CAP, 0.04)
            SE.finial(mb, px, py, P3 + 1.11, 0.42, m=CAP, n=8)
        xa, xb = sorted((xe, xe + d * 1.0))
        mb.box2((xa, g0, zb + 0.03), (xb, g1, P3 - 0.04), CAP, 0.05)                # patamar (soleira)
        xa, xb = sorted((xe + d * 1.0, xe + d * 2.75))
        mb.box2((xa, g0, zb + 0.03), (xb, g1, P3 - 0.6), CAP, 0.05)                  # degrau do meio
        for ye in (g0, g1):
            ya, yb = sorted((ye, ye + (0.5 if ye == g0 else -0.5)))
            xa, xb = sorted((xe + d * 1.4, xe + d * 2.9))
            mb.box2((xa, ya, zb), (xb, yb, P3 - 0.1), WALLM, 0.03)                   # bochecha
        xa, xb = sorted((xe, xe + d * 2.75))
        col_box2("SG_PropLawnStep", (xa, g0, P3 - 0.6 - 0.5), (xb, g1, P3 - 0.6))
    col_box2("SG_PropLawnFloor", (x0 + T, y0 + T, P3 - LAWN_DEPTH - 1.0), (x1 - T, y1 - T, P3 - LAWN_DEPTH))
    for (a, b, (nx, ny)) in runs:
        pa = (a[0] + nx * T, a[1] + ny * T)
        pb = (b[0] + nx * T, b[1] + ny * T)
        xs, ys = sorted((a[0], b[0], pa[0], pb[0])), sorted((a[1], b[1], pa[1], pb[1]))
        col_box2("SG_PropLawnWall", (xs[0], ys[0], P3 - LAWN_DEPTH), (xs[-1], ys[-1], zt + 0.2))


# ------------------------------------------------------------------ 3. espelhos d'agua
def pool(mb, rect_, name):
    """bacia estanque: fundo de obsidiana em POOL_FLOOR, paredes de cantaria, capa em pecas com pingadeira (0,06 acima
    da lamina) e dados de canto um pouco mais altos. A agua e do Roblox (WATER_Court_<name>)."""
    x0, y0, x1, y1 = rect_
    R = POOL_RIM
    zc = POOL_LEVEL + 0.06
    mb.box2((x0, y0, P3 - 0.56), (x1, y1, POOL_FLOOR), OBS, 0.0)
    # so na PREVIA (PREVIEW_ nao exporta): a lamina como o Roblox fara, para julgar a leitura do espelho
    pv = MB("PREVIEW_CourtWater_%s" % name, "00_REFERENCE", None, detail="far", floor=-999)
    pv.box2((x0, y0, POOL_LEVEL - 0.02), (x1, y1, POOL_LEVEL), "Water_SG", 0.0)
    pv.finish()
    for (a, b) in (((x0 - R, y0 - R), (x1 + R, y0)), ((x0 - R, y1), (x1 + R, y1 + R)), ((x0 - R, y0), (x0, y1)),
                   ((x1, y0), (x1 + R, y1))):
        mb.box2((a[0], a[1], P3 - 0.5), (b[0], b[1], zc), WALLM, 0.0)
        col_box2("SG_PropPool", (a[0], a[1], P3 - 0.5), (b[0], b[1], zc + 0.22))
    # capa: pecas de ~2,6 nos 4 lados (0,1 para dentro sobre a agua e 0,12 para fora)
    for (a, b, horiz) in (((x0 - R, y0 - R), (x1 + R, y0), True), ((x0 - R, y1), (x1 + R, y1 + R), True),
                          ((x0 - R, y0), (x0, y1), False), ((x1, y0), (x1 + R, y1), False)):
        ln = (b[0] - a[0]) if horiz else (b[1] - a[1])
        n = max(1, int(round(ln / 2.6)))
        for k in range(n):
            t0 = ln * k / n + (0.03 if k else 0.0)
            t1 = ln * (k + 1) / n - (0.03 if k < n - 1 else 0.0)
            if horiz:
                p0 = (a[0] + t0 - (0.12 if k == 0 else 0.0), a[1] - 0.12)
                p1 = (a[0] + t1 + (0.12 if k == n - 1 else 0.0), b[1] + 0.12)
            else:
                p0 = (a[0] - 0.12, a[1] + t0 + 0.12)
                p1 = (b[0] + 0.12, a[1] + t1 - 0.12)
            mb.box2((p0[0], p0[1], zc), (p1[0], p1[1], zc + 0.2), CAP, 0.0)
    for cx in (x0 - R / 2, x1 + R / 2):
        for cy in (y0 - R / 2, y1 + R / 2):
            mb.box((R + 0.5, R + 0.5, zc + 0.42 - (P3 - 0.44)), (cx, cy, (P3 - 0.44 + zc + 0.42) / 2), (0, 0, 0),
                   RELM, 0.06)
            mb.box((R + 0.7, R + 0.7, 0.14), (cx, cy, zc + 0.49), (0, 0, 0), CAP, 0.04)


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
def tall_hedge(mg, a, b, w, h, seed, m=YEW):
    """sebe ALTA de teixo: lances de ~3 com altura e largura levemente variadas (o topo nao e regua) e topo de luar"""
    L_ = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(round(L_ / 3.2)))
    ux, uy = (b[0] - a[0]) / L_, (b[1] - a[1]) / L_
    for k in range(n):
        t0 = L_ * k / n - (0.25 if k else 0.0)
        t1 = L_ * (k + 1) / n + (0.25 if k < n - 1 else 0.0)
        hk = h * (1.0 + 0.05 * math.sin(seed + k * 2.3))
        wk = w * (1.0 + 0.05 * math.cos(seed * 0.7 + k * 1.9))
        GD.hedge_round(mg, (a[0] + ux * t0, a[1] + uy * t0), (a[0] + ux * t1, a[1] + uy * t1), wk, hk, P3 - 0.05, m)


def cone(mg, x, y, z, h, r, m=YEW):
    """teixo podado em CHAMA (ogiva: barriga baixa, ponta fina) - topiaria, nao cone de papel"""
    GD._occ(x, y, r + 0.4)
    EM._lathe(mg, (x, y, z - 0.05), [(r * 0.86, 0.0), (r, 0.12 * h), (r * 0.94, 0.3 * h), (r * 0.72, 0.55 * h),
                                     (r * 0.4, 0.8 * h), (r * 0.12, 0.96 * h), (0.0, h)], m, 10, 0.2)


def drift(mg, cx, cy, rx, ry, kinds, seed, z=P3, dens=1.0, s=1.0, rot=0.0, ctx="patio"):
    """DERIVA de flores (mancha alongada de contorno organico): espiral de filotaxia dentro do blob, 1a especie no miolo,
    2a na borda; mais rala na borda (le grupo natural, nao canteiro de regua)"""
    poly = blob(cx, cy, rx, ry, seed, rot)
    ga = math.pi * (3.0 - math.sqrt(5.0))
    n = int(rx * ry * 2.2 * dens)
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
    for k, (y0, y1, h) in enumerate(SIDE_HEDGE[s]):
        tall_hedge(mg, (s * SIDE_X, y0), (s * SIDE_X, y1), 2.6, h, 3.1 * k + s)
        xa, xb = sorted((s * (SIDE_X - 1.3), s * (SIDE_X + 1.3)))
        col_box2("SG_VegHedge", (xa, y0, P3), (xb, y1, P3 + h))
    for yc in SIDE_CONES[s]:
        cone(mg, s * SIDE_X, yc, P3, 7.2, 1.6)
        col_box("SG_VegHedge", (2.2, 2.2, 6.0), (s * SIDE_X, yc, P3 + 3.0))
    # sebe alta na frente da fachada (lances de alturas diferentes: le massa viva contra o paredao)
    for k, (x0, x1, h) in enumerate(FACADE_HEDGE):
        tall_hedge(mg, (s * x0, FACADE_HEDGE_Y), (s * x1, FACADE_HEDGE_Y), 2.2, h, 5.3 * k + 2 * s)
        xa, xb = sorted((s * x0, s * x1))
        col_box2("SG_VegHedge", (xa, FACADE_HEDGE_Y - 1.1, P3), (xb, FACADE_HEDGE_Y + 1.1, P3 + h))
    # sebe MEDIA em L na quina entre o porche e o espelho
    a, b, c = (s * 33.4, 53.6), (s * 33.4, 46.0), (s * 37.4, 46.0)
    GD.hedge_round(mg, a, b, 1.3, 1.7, P3 - 0.05, BOX)
    GD.hedge_round(mg, (b[0], b[1] + 0.6), c, 1.3, 1.5, P3 - 0.05, BOX)
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
    # bolas de buxo ao pe das estatuas
    sx, sy = STATUES[i]
    for dx in (-2.6, 2.6):
        GD.topiary(mg, (sx + dx, sy - 1.2, P3 - 0.05), 0.85)
    # derivas de flores (frente das massas): roda da estatua, pe das sebes, gramado nos degraus, roda da arvore
    drift(mg, sx, sy - 2.7, 3.2, 1.1, ("moon", "spike"), 7 + i, dens=1.5)
    drift(mg, sx + s * 2.9, sy + 0.4, 0.9, 2.2, ("bell", "moon"), 9 + i, dens=1.2)
    for k, (yc, kinds) in enumerate(((-6.0, ("spike", "moon")), (7.5, ("bell", "moon")), (36.5, ("moon", "amber")),
                                    (48.5, ("spike", "bell")))):
        drift(mg, s * (SIDE_X - 3.1), yc, 0.9, 2.6 + 0.4 * (k % 2), kinds, 13 + k + 4 * i, dens=1.2)
    for k, (xc, rx) in enumerate(((43.0, 5.5), (62.5, 6.5), (84.5, 5.0))):
        drift(mg, s * xc, FACADE_HEDGE_Y - 2.0, rx, 0.8, ("spike", "moon") if k % 2 == 0 else ("moon", "spike"),
              23 + k + 3 * i, dens=1.0)
    zl = P3 - LAWN_DEPTH
    for xe, sg in ((xin, 1.0), (xout, -1.0)):
        for ye in (STEP_Y[0] - 2.1, STEP_Y[1] + 2.1):
            drift(mg, xe + s * sg * 2.6, ye, 1.4, 1.3, ("moon", "spike") if sg > 0 else ("bell", "moon"),
                  31 + int(ye) + i, z=zl, dens=1.2)
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


def tree_bench(mb, x, y, r0=2.35, r1=3.25, zs=1.75):
    """banco circular em volta do tronco da arvore-marco: 8 tabuas de cantaria em octogono sobre 8 pes"""
    for k in range(8):
        a0 = (k + 0.04) * math.tau / 8 + math.pi / 8
        a1 = (k + 0.96) * math.tau / 8 + math.pi / 8
        pts = [(x + r0 * math.cos(a0), y + r0 * math.sin(a0)), (x + r1 * math.cos(a0), y + r1 * math.sin(a0)),
               (x + r1 * math.cos(a1), y + r1 * math.sin(a1)), (x + r0 * math.cos(a1), y + r0 * math.sin(a1))]
        mb.prism(SL.ccw(pts), P3 + zs - 0.3, P3 + zs, CAP)
        am = (a0 + a1) / 2
        rm = (r0 + r1) / 2
        mb.box((0.5, 0.7, zs - 0.3 + 0.1), (x + rm * math.cos(am), y + rm * math.sin(am), P3 + (zs - 0.3) / 2 - 0.05),
               (0, 0, am), RELM, 0.05)
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
    for x, y in STATUES:
        statue(mb, x, y, P3, -math.pi / 2 - math.copysign(math.radians(16.0), x))
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
    mirante(mb, mg)
    mb.finish()
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


# ------------------------------------------------------------------ 5. jardim-mirante
def mirante(mb, mg):
    """terraco do jardim-mirante: lajes em 3 aneis (o terreno desce 0,45 no disco), balaustrada na borda da vista,
    banco em exedra de costas para o castelo, a arvore velha da lua inclinada para a vista e flores"""
    cx, cy, R = MIR
    R1 = R + 0.6                                  # = rebaixo do terreno
    # leito escuro (juntas) e lajes
    mb.cyl(R1, 0.5, (cx, cy, P3 - 0.55), (0, 0, 0), "Stone_SG_Floor", n=40, bevel=0.0)
    mb.cyl(3.4, 0.4, (cx, cy, P3 - 0.25), (0, 0, 0), OBS, n=16, bevel=0.0)
    EM._lathe(mb, (cx, cy, P3 - 0.1), [(1.3, 0.0), (1.3, 0.17), (0.0, 0.21)], VIO, 16)
    for (ra, rb, n, mats) in ((3.48, 8.6, 10, (CAP, RELM)), (8.68, 13.2, 16, (RELM, CAP)), (13.28, R1, 22, (CAP, RELM))):
        for k in range(n):
            a0 = (k + 0.012 * 16 / n) * math.tau / n
            a1 = (k + 1 - 0.012 * 16 / n) * math.tau / n
            arc0 = [(cx + ra * math.cos(a0 + (a1 - a0) * t / 2), cy + ra * math.sin(a0 + (a1 - a0) * t / 2))
                    for t in range(3)]
            arc1 = [(cx + rb * math.cos(a1 - (a1 - a0) * t / 2), cy + rb * math.sin(a1 - (a1 - a0) * t / 2))
                    for t in range(3)]
            mb.prism(SL.ccw(arc0 + arc1), P3 - 0.3, P3, mats[k % 2])
    # balaustrada (arco da vista): plinto, balaustres torneados, corrimao em pecas, pedestais a cada ~30 graus
    rb_ = R - 0.4
    a0, a1 = MIR_VIEW
    nped = 6
    peds = [a0 + (a1 - a0) * k / nped for k in range(nped + 1)]
    for k in range(nped):
        pa, pbb = math.radians(peds[k]), math.radians(peds[k + 1])
        seg = 5
        for j in range(seg):
            q0 = pa + (pbb - pa) * j / seg
            q1 = pa + (pbb - pa) * (j + 1) / seg
            c0 = (cx + rb_ * math.cos(q0), cy + rb_ * math.sin(q0))
            c1 = (cx + rb_ * math.cos(q1), cy + rb_ * math.sin(q1))
            ln = math.hypot(c1[0] - c0[0], c1[1] - c0[1])
            mid = ((c0[0] + c1[0]) / 2, (c0[1] + c1[1]) / 2)
            yaw = math.atan2(c1[1] - c0[1], c1[0] - c0[0])
            mb.box((ln + 0.04, 1.1, 0.5), (mid[0], mid[1], P3 + 0.25), (0, 0, yaw), WALLM, 0.04)
            mb.box((ln + 0.06, 1.0, 0.26), (mid[0], mid[1], P3 + 2.85), (0, 0, yaw), CAP, 0.06)
            EM._lathe(mb, (mid[0], mid[1], P3 + 0.5), [(0.18, 0.0), (0.32, 0.8), (0.14, 1.55), (0.24, 2.22)], RELM, 6)
    for a in peds:
        ra = math.radians(a)
        px, py = cx + rb_ * math.cos(ra), cy + rb_ * math.sin(ra)
        mb.box((1.5, 1.5, 3.3), (px, py, P3 + 1.6), (0, 0, ra), WALLM, 0.06)
        mb.box((1.8, 1.8, 0.24), (px, py, P3 + 3.36), (0, 0, ra), CAP, 0.05)
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
    nseg = 12
    for j in range(nseg):
        q0 = math.radians(e0 + (e1 - e0) * j / nseg)
        q1 = math.radians(e0 + (e1 - e0) * (j + 1) / nseg)
        for (r0, r1, z0, z1, m) in ((er - 0.9, er + 0.9, P3 + 1.4, P3 + 1.75, CAP),
                                    (er + 0.9, er + 1.5, P3 + 0.0, P3 + 3.6, WALLM),
                                    (er + 0.8, er + 1.6, P3 + 3.6, P3 + 3.85, CAP)):
            pts = [(cx + r0 * math.cos(q0), cy + r0 * math.sin(q0)), (cx + r1 * math.cos(q0), cy + r1 * math.sin(q0)),
                   (cx + r1 * math.cos(q1), cy + r1 * math.sin(q1)), (cx + r0 * math.cos(q1), cy + r0 * math.sin(q1))]
            mb.prism(SL.ccw(pts), z0, z1, m)
        if j % 2 == 0:
            qm = (q0 + q1) / 2
            mb.box((1.3, 0.6, 1.42), (cx + (er - 0.1) * math.cos(qm), cy + (er - 0.1) * math.sin(qm), P3 + 0.69),
                   (0, 0, qm), RELM, 0.05)
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
