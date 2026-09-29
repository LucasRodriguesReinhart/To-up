# sg_court - VESTIR / PATIO E CAMINHOS NOBRES da Ilha 3 (Shadow Garden). Roda ANTES do sg_veg (zona dressing).
# O exterior deixa de ser "laje lisa": um SISTEMA de leitura, simetrico onde e cerimonial.
#   1. CAMINHO DA ORDEM (eixo nobre): calcada alta da entrada -> praca -> pe da escada P1P2 -> rua do eixo (P2) -> portao
#      da muralha -> patio -> porta do castelo. Lajes grandes de marmore negro, borda de obsidiana e um FIO violeta
#      (SG_VioletDeep_Glow) rente no centro; juntas de prata a cada 4 fiadas. Topo <= cota + 0,05 (nada de degrau).
#   2. PATIO DO CASTELO (CASTLE_FORECOURT): medalhao do EMBLEMA da ordem no chao (marmore negro/prata/violeta, rente),
#      2 canteiros sombrios (borda de obsidiana, sebes recortadas, flores violeta dessaturadas, 1 cipreste), 2 estatuas
#      da ordem (encapuzado de manto longo com a lamina) em pedestais com o medalhao, 2 obeliscos com runas, 4 postes de
#      ferro negro (par sul quente, par norte violeta), muretas com remate de obsidiana nas laterais (o patio muda de
#      funcao ali). O eixo (14) e as rotas CASTELO->DUNGEON / beco oeste ficam livres.
#   3. TRANSICOES: arco leve de ferro negro no pe da escada do portao (entrada do recinto do castelo) - mesma familia do
#      arco do topo da escada P1P2 (sg_village); 2 estandartes da ordem em mastros na saida norte da praca.
# Prefixo SG_Prop_, colecao 09_PROPS. Luzes: sg_lights (COURT_LIGHTS daqui). Simbolo: SO sg_emblem.
# REFINAMENTO v2 2026-09-28: RITMO de lanternas douradas (sg_emblem.lantern_pedestal, SO Neon) ao longo do eixo no P2,
# nos dois lados do caminho da ordem (fora do fio central e da largura util de 12), do topo da escada P1P2 ate o pe da
# escada do portao; o vao do cruzamento com a rua do P2 fica com o lantern_post da vila (7.8, -51.6). Estandartes dos
# mastros da praca com debrum DOURADO. Nos parapeitos do P2/P3 do terreno NAO se mexe: as lanternas ficam no chao.
# REFINAMENTO v3 2026-09-29: contraste caminho x patio com o calcamento escurecido - filete de cantaria clara rente na
# aresta externa do caminho da ordem (os dois lados, em todo o eixo) e a travessia do patio um valor abaixo do piso.
# ACABAMENTO 2026-09-29: hierarquia de brilho (fio do eixo na vila = pedra violeta sem brilho; patio do castelo no
# violeta BAIXO SG_VioletSoft_Glow: fio, halo do medalhao, runas dos obeliscos, lanternas do norte; arco do portao com
# lanternas quentes); os 2 mastros-estandarte da praca sairam (sinal repetido); a figura da ordem virou
# hooded_figure() (manto com pregas, capa, borda do capuz, punhos) - a mesma da fonte da praca (sg_village); flores
# dos canteiros em tufos achatados; vidro da lanterna do patio assentado no prato e no chapeu.
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, fm_lib
import sg_layout as L
import sg_emblem as EM
import fm_parts as FP
import sg_veg as VEG                 # cipreste do canteiro (mesma arvore da ilha) + material do luar das folhas
import fm_veg_kit as VK

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
# ACABAMENTO 2026-09-29 (hierarquia de brilho): na VILA (P1/P2) o fio do caminho da ordem vira PEDRA violeta sem brilho
# (o desenho continua, o neon sai); no patio do CASTELO (P3) o fio, o halo do medalhao, as runas dos obeliscos e as
# lanternas do norte ficam no violeta BAIXO (SG_VioletSoft_Glow). Lanternas de caminho: quentes.
THREAD_VIL = VIO
THREAD_CASTLE = "SG_VioletSoft_Glow"
WARM_G = "Lantern_Glow"
HEDGE = "Leaf_SG_Pine"
HEDGE_TOP = VEG.MOON                  # topo das sebes raspado pelo luar (o mesmo das copas)
SOIL = "Dirt_SG"
# material novo do vestir (1): flor violeta DESSATURADA dos canteiros (a vila usa o mesmo nos floreiras das casas)
BLOOM = "Leaf_SGPropBloom"
fm_lib.MATS.setdefault(BLOOM, (fm_lib.S(98, 66, 132), 0.85, 0.0, 0, None, 0.08))

FC = L.CASTLE_FORECOURT               # (-46, -3, 46, 40)
MED_C = (0.0, 20.0)                   # centro do medalhao (cruzamento do eixo com a travessia patio -> dungeon/beco)
MED_R = 8.5                           # raio do emblema (anel externo ~0,96 r); aro de obsidiana ate 1,365 r
MED_RIM = MED_R * 1.365
AXIS_W = 14.0                         # eixo do patio (livre)
PATH_W = 12.0                         # eixo na calcada alta, pe da escada e rua do P2
PARTERRE_X = (12.0, 37.0)             # |x| dos canteiros
PARTERRE_Y = (3.5, 15.0)
LAMPS = [(-8.4, 11.5, "warm"), (8.4, 11.5, "warm"), (-8.4, 28.5, "violet"), (8.4, 28.5, "violet")]
STATUES = [(-12.5, 33.5), (12.5, 33.5)]
OBELISKS = [(-21.0, 29.0), (21.0, 29.0)]
MURETS = [(-45.0, 0.0, 13.5), (45.0, 0.0, 13.5)]
GATE_ARCH = (0.0, -28.0, P2, 9.4)     # (x, y, z, meia-abertura) arco de ferro no pe da escada do portao
# acabamento 2026-09-29: os 2 mastros com estandarte na saida norte da praca SAIRAM (repetiam, na frente, os
# estandartes da fachada do castelo; o arco de ferro do topo da escada P1P2 ja marca a transicao)
PLAZA_MASTS = []
# lanternas do eixo no P2 (referencia v2): pares em x = +-7.6 (fora da largura util de 12 do caminho), a cada ~14;
# o vao -50 fica com o lantern_post da vila em (7.8, -51.6) (nada de cacho de postes no cruzamento)
AXIS_LANTERN_X = 7.6
AXIS_LANTERN_Y = (-78.0, -64.0, -36.0)
# luzes do patio (quem cria e o sg_lights; teto de 7 no vestir)
VIOLET = (0.62, 0.42, 1.0)
COURT_LIGHTS = [("Court_Violet", (0.0, 30.5, P3 + 7.0), 420.0, VIOLET, 0.6)]

CAMS = {
    # 360 do patio + altura do jogador (entrando pelo portao, na travessia, voltando da porta)
    "CAM_SGCourt_High": ((0.0, 0.0, P3 + 50.0), (0.0, 22.0, P3), 20),
    "CAM_SGCourt_PH_Gate": ((0.0, -1.0, P3 + 5.2), (0.0, 40.0, P3 + 9.0), 22),
    "CAM_SGCourt_PH_Cross": ((-40.0, 18.0, P3 + 5.2), (10.0, 24.0, P3 + 6.0), 22),
    "CAM_SGCourt_PH_Back": ((0.0, 35.0, P3 + 5.2), (0.0, -10.0, P3 + 5.0), 22),
    "CAM_SGCourt_SideE": ((44.0, 4.0, P3 + 24.0), (0.0, 22.0, P3 + 1.0), 22),
    "CAM_SGCourt_PH_P2Axis": ((0.0, -78.0, P2 + 5.2), (0.0, -20.0, P2 + 10.0), 22),
    "CAM_SGCourt_PH_PlazaN": ((0.0, -120.0, P1 + 5.2), (0.0, -90.0, P1 + 9.0), 22),
    "CAM_SGCourt_PH_EntryHigh": ((0.0, -186.0, P1 + 5.2), (0.0, -140.0, P1 + 6.0), 22),
}

# rotas extras: a volta pelos canteiros (entre o poste, o canteiro e a mureta) e o contorno das estatuas/obeliscos
EXTRA_ROUTES = {
    "COURT_JARDIM_O": ([(0.0, 1.6), (-10.3, 1.6), (-10.3, 17.2), (-39.5, 17.2), (-41.0, 9.0), (-39.5, 1.6),
                        (-10.3, 1.6)], P3),
    "COURT_JARDIM_L": ([(0.0, 1.6), (10.3, 1.6), (10.3, 17.2), (39.5, 17.2), (41.0, 9.0), (39.5, 1.6),
                        (10.3, 1.6)], P3),
    "COURT_ESTATUA_O": ([(0.0, 24.0), (-16.75, 24.0), (-16.75, 34.0)], P3),
    "COURT_ESTATUA_L": ([(0.0, 24.0), (16.75, 24.0), (16.75, 34.0)], P3),
    "COURT_ARCO_PORTAO": ([(0.0, -40.0), (0.0, -28.0), (0.0, -24.0)], P2),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ utilidades de forma
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


# ------------------------------------------------------------------ 1. caminho da ordem
def noble_path(mb, y0, y1, W, z, thread=(None, None), slabs=(None, None), border=(None, None), row=3.0,
               thread_m=THREAD_VIL):
    """eixo nobre ao longo de +Y (x = 0) de y0 a y1, largura W, piso na cota z.
    base de obsidiana (juntas/canal do fio) + bordas de obsidiana + lajes grandes de marmore negro (uma por lado e por
    fiada) + fio violeta no centro + junta de prata a cada 4 fiadas. thread/slabs/border = (y_ini, y_fim) opcionais
    (quando o medalhao come um trecho)."""
    hw = W / 2.0
    bd = 0.9                                     # borda
    mb.box2((-hw, y0, z - 0.2), (hw, y1, z + 0.02), OBS, 0.0)
    by0, by1 = border[0] if border[0] is not None else y0, border[1] if border[1] is not None else y1
    for s in (-1, 1):
        xa, xb = sorted((s * (hw - 0.24), s * (hw - bd)))
        mb.box2((xa, by0, z - 0.05), (xb, by1, z + 0.05), OBS, 0.0)
        # v3: filete de cantaria clara RENTE na aresta externa da borda: com o calcamento escurecido (refino v2b) o
        # marmore negro + obsidiana perdiam a aresta contra o piso do patio; o filete desenha o caminho a altura do olho
        xa, xb = sorted((s * hw, s * (hw - 0.24)))
        mb.box2((xa, by0, z - 0.05), (xb, by1, z + 0.05), TRIM, 0.0)
    # lajes (fiadas de ~3; junta 0,12 mostra a base escura)
    sy0, sy1 = slabs[0] if slabs[0] is not None else y0, slabs[1] if slabs[1] is not None else y1
    n = max(1, int(round((sy1 - sy0) / row)))
    dy = (sy1 - sy0) / n
    xin, xout = 0.55, hw - bd - 0.12
    for k in range(n):
        ya, yb = sy0 + k * dy + 0.06, sy0 + (k + 1) * dy - 0.06
        for s in (-1, 1):
            xa, xb = sorted((s * xin, s * xout))
            mb.box2((xa, ya, z - 0.05), (xb, yb, z + 0.045), MARB, 0.0)
        if k > 0 and k % 4 == 0:
            yj = sy0 + k * dy
            mb.box2((-xout, yj - 0.06, z - 0.05), (xout, yj + 0.06, z + 0.035), SILVER, 0.0)
    ty0, ty1 = thread[0] if thread[0] is not None else y0, thread[1] if thread[1] is not None else y1
    mb.box2((-0.14, ty0, z - 0.05), (0.14, ty1, z + 0.05), thread_m, 0.0)


def medallion(mb, c, r, z):
    """o EMBLEMA da ordem no chao do patio (acabamento 2026-09-29: o simbolo e o do sg_emblem.emblem_flat - o MESMO
    desenho limpo de toda a ilha, deitado e rente; nada de copia local). Aqui fica so a MOLDURA: leito de obsidiana
    ate 1,365 r (o campo negro do simbolo) com filete de cantaria na borda, rente ao piso. A lamina aponta para o norte
    (porta do castelo); o crescente no violeta BAIXO do patio. Tudo <= piso + 0,05."""
    cx, cy = c
    zb = z + 0.01                                             # topo do leito (acima do piso: sem z-fight)
    disc(mb, c, 1.3 * r, z - 0.1, zb, OBS, 64)                # leito / campo
    ring(mb, c, 1.3 * r, 1.365 * r, z - 0.1, z + 0.03, TRIM, 64)   # filete da borda
    if hasattr(EM, "emblem_flat"):
        EM.emblem_flat(mb, mb, mb, (cx, cy, zb), math.pi / 2, r, monumental=True, glow=THREAD_CASTLE, field=False)
    else:
        EM.emblem(mb, mb, mb, (cx, cy, zb), math.pi / 2, r, depth=0.04)     # (so se o sg_emblem for antigo)


def axis_south():
    """calcada alta da entrada ate a praca + o trecho entre a praca e o pe da escada P1P2 (P1)"""
    mb = MB("SG_Prop_NobleAxis_P1", COLL, random.Random(3601), detail="near")
    y_top = L.ENTRY_STAIR_Y1 + 0.35                  # topo da escadaria da entrada (-187,65)
    y_plaza_s = L.PLAZA_C[1] - L.PLAZA_R + 1.0       # a borda de cantaria da praca cobre a junta
    noble_path(mb, y_top, y_plaza_s, PATH_W, P1)
    foot = L.stair_frame("P1P2")[0]
    noble_path(mb, L.PLAZA_C[1] + L.PLAZA_R - 1.0, foot[1] - 0.02, PATH_W, P1)
    # estandartes da ordem em mastros na saida norte da praca (encaram a praca)
    for x, y in PLAZA_MASTS:
        mast_banner(mb, x, y, P1)
    mb.finish()


def mast_banner(mb, x, y, z, yaw=-math.pi / 2):
    """mastro de ferro negro com soco de obsidiana e o estandarte da ordem pendurado a frente (lado 'yaw')"""
    fx, fy = math.cos(yaw), math.sin(yaw)
    mb.box((1.5, 1.5, 0.9), (x, y, z + 0.35), (0, 0, 0), OBS, 0.1)
    mb.box((1.1, 1.1, 0.5), (x, y, z + 1.05), (0, 0, 0), VIO, 0.06)
    mb.cyl(0.24, 13.2, (x, y, z + 1.3 + 6.6), (0, 0, 0), IRON, n=8, r2=0.17, bevel=0.0)
    mb.cyl(0.36, 0.3, (x, y, z + 12.9), (0, 0, 0), IRON, n=8, bevel=0.0)
    SL.spire(mb, (x, y), 0.34, z + 14.5, 1.3, SILVER, n=4)
    mb.ico(0.22, (x, y, z + 14.45), SILVER, 1)
    top = (x + fx * 0.36, y + fy * 0.36, z + 12.6)
    EM.banner(mb, mb, mb, mb, top, yaw, 3.0, 7.4, trim=EM.GOLD)
    col_box("SG_PropMast", (1.2, 1.2, 14.0), (x, y, z + 7.0))


def axis_north():
    """rua do eixo no P2 + portao + patio do castelo (P3) com o medalhao; o arco de ferro no pe da escada do portao"""
    mb = MB("SG_Prop_NobleAxis_P2P3", COLL, random.Random(3602), detail="near")
    y_p2_0 = L.stair_top("P1P2")[1] + 0.02          # -83
    y_p2_1 = L.stair_frame("Gate")[0][1] - 0.02      # -26
    noble_path(mb, y_p2_0, y_p2_1, PATH_W, P2)
    # ritmo de lanternas douradas ladeando o caminho da ordem no P2 (SO Neon; colisao propria fina)
    for yy in AXIS_LANTERN_Y:
        for s in (-1, 1):
            EM.lantern_pedestal(mb, mb, mb, (s * AXIS_LANTERN_X, yy, P2), 0.0, 1.0)
            col_box("SG_PropLantern", (1.9, 1.9, 3.6), (s * AXIS_LANTERN_X, yy, P2 + 1.8))
    # patio: do portao (face sul da muralha) ate a porta; o medalhao come o trecho do meio
    cx, cy = MED_C
    y_gate = L.WALL_Y0 + 0.02                        # -8,98 (topo da escada do portao)
    y_door = L.CASTLE_FACADE_Y - 0.02
    hwA = AXIS_W / 2.0
    edge = math.sqrt(MED_RIM ** 2 - (hwA - 0.45) ** 2)      # onde a borda do eixo encontra o aro
    noble_path(mb, y_gate, cy - math.sqrt(MED_RIM ** 2 - hwA ** 2), AXIS_W, P3,
               thread=(None, cy - 0.96 * MED_R - 0.02), slabs=(None, cy - MED_RIM - 0.1), border=(None, cy - edge),
               thread_m=THREAD_CASTLE)
    noble_path(mb, cy + math.sqrt(MED_RIM ** 2 - hwA ** 2), y_door, AXIS_W, P3,
               thread=(cy + 1.213 * MED_R + 0.01, None), slabs=(cy + MED_RIM + 0.1, None), border=(cy + edge, None),
               thread_m=THREAD_CASTLE)
    medallion(mb, MED_C, MED_R, P3)
    for s in (-1, 1):
        cross_walk(mb, s)
    mb.finish()


def cross_walk(mb, s, hw=3.6, x_end=(44.0, 44.9)):
    """travessia secundaria do patio (do aro do medalhao ate a borda do patio): lajota escura (Stone_SG_Floor) com
    faixas de cantaria clara rentes nas bordas - abaixo do eixo nobre na hierarquia, acima do piso liso"""
    cx, cy = MED_C
    z = P3
    xe = x_end[1] if s > 0 else x_end[0]
    arc = []
    for k in range(9):
        yy = cy - hw + 2 * hw * k / 8
        arc.append((cx + s * math.sqrt(MED_RIM ** 2 - (yy - cy) ** 2), yy))
    poly = arc + [(s * xe, cy + hw), (s * xe, cy - hw)]
    mb.prism(SL.ccw(poly), z - 0.1, z + 0.03, "Stone_SG_Floor")
    for e in (-1, 1):
        ya, yb = sorted((cy + e * hw, cy + e * (hw - 0.55)))
        x0 = cx + s * math.sqrt(MED_RIM ** 2 - (cy + e * (hw - 0.3) - cy) ** 2)
        xa, xb = sorted((x0, s * xe))
        mb.box2((xa, ya, z - 0.05), (xb, yb, z + 0.045), TRIM, 0.0)
    # juntas transversais a cada 3,2 (fiadas), e a soleira na ponta
    xs = abs(cx + math.sqrt(MED_RIM ** 2 - hw ** 2))
    k = 1
    while xs + 3.2 * k < xe - 1.0:
        xj = s * (xs + 3.2 * k)
        mb.box2((xj - 0.07, cy - hw + 0.55, z - 0.05), (xj + 0.07, cy + hw - 0.55, z + 0.04), OBS, 0.0)
        k += 1
    xa, xb = sorted((s * (xe - 0.6), s * xe))
    mb.box2((xa, cy - hw, z - 0.05), (xb, cy + hw, z + 0.045), TRIM, 0.0)


# ------------------------------------------------------------------ 2. patio: canteiros, estatuas, obeliscos, postes
def hedge(mb, a, b, w=0.8, h=0.95, z=P3 + 0.5):
    """sebe recortada reta de a a b (xy), com o topo raspado de luar"""
    mb.beam((a[0], a[1], z + h / 2), (b[0], b[1], z + h / 2), w, h, HEDGE, 0.12)
    mb.beam((a[0], a[1], z + h + 0.04), (b[0], b[1], z + h + 0.04), w - 0.12, 0.08, HEDGE_TOP, 0.0)


def parterre(mb, s, rng):
    x0, x1 = sorted((s * PARTERRE_X[0], s * PARTERRE_X[1]))
    y0, y1 = PARTERRE_Y
    z = P3
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    bw = 0.9
    # borda de obsidiana (mureta baixa com chanfro no topo) + pilaretes de canto com pinaculo
    mb.box2((x0, y0, z - 0.1), (x1, y0 + bw, z + 0.8), OBS, 0.1)
    mb.box2((x0, y1 - bw, z - 0.1), (x1, y1, z + 0.8), OBS, 0.1)
    mb.box2((x0, y0 + bw, z - 0.1), (x0 + bw, y1 - bw, z + 0.8), OBS, 0.1)
    mb.box2((x1 - bw, y0 + bw, z - 0.1), (x1, y1 - bw, z + 0.8), OBS, 0.1)
    for px in (x0 + 0.6, x1 - 0.6):
        for py in (y0 + 0.6, y1 - 0.6):
            mb.box((1.3, 1.3, 1.3), (px, py, z + 0.55), (0, 0, 0), OBS, 0.1)
            mb.box((1.45, 1.45, 0.16), (px, py, z + 1.28), (0, 0, 0), VIO, 0.0)
            SL.spire(mb, (px, py), 0.62, z + 1.36, 0.9, OBS, n=4)
    # terra
    mb.box2((x0 + bw, y0 + bw, z - 0.1), (x1 - bw, y1 - bw, z + 0.62), SOIL, 0.0)
    # sebes: moldura, circulo do cipreste e a sebe mediana (o desenho e o mesmo nos dois canteiros, espelhado)
    i0, i1, j0, j1 = x0 + bw + 0.55, x1 - bw - 0.55, y0 + bw + 0.55, y1 - bw - 0.55
    hedge(mb, (i0 - 0.42, j0), (i1 + 0.42, j0))
    hedge(mb, (i0 - 0.42, j1), (i1 + 0.42, j1))
    hedge(mb, (i0, j0 + 0.42), (i0, j1 - 0.42))
    hedge(mb, (i1, j0 + 0.42), (i1, j1 - 0.42))
    rr = 2.5
    pts = ngon((cx, cy), rr, 8, math.pi / 8)
    for k in range(8):
        a, b = pts[k], pts[(k + 1) % 8]
        hedge(mb, a, b, w=0.75, h=1.2)
    hedge(mb, (i0 + 0.42, cy), (cx - rr - 0.2, cy), w=0.6, h=0.7)
    hedge(mb, (cx + rr + 0.2, cy), (i1 - 0.42, cy), w=0.6, h=0.7)
    # flores violeta em fileiras escalonadas (4 canteiros internos, 2 fileiras cada)
    for ya, yb in ((j0 + 0.45, cy - 0.45), (cy + 0.45, j1 - 0.45)):
        rows = (ya + (yb - ya) * 0.28, ya + (yb - ya) * 0.72)
        for xa, xb in ((i0 + 0.45, cx - rr - 0.6), (cx + rr + 0.6, i1 - 0.45)):
            nx = max(2, int((xb - xa) / 1.35))
            for ri, yy in enumerate(rows):
                for k in range(nx):
                    xx = xa + (xb - xa) * (k + 0.5 + (0.25 if ri else -0.25)) / nx
                    if not (xa + 0.3 < xx < xb - 0.3):
                        continue
                    # tufo baixo e achatado (acabamento: a bola de 0,62 lia como gema facetada)
                    mb.ico(0.5, (xx, yy, z + 0.78), BLOOM, 1, scale=(1.3, 1.3, 0.52))
    # cipreste no centro (a mesma especie da ilha: le como plantado, nao enfeite)
    old = VK.SUN
    VK.SUN = VEG.MOON_DIR
    try:
        VEG.cypress(mb, cx, cy, z + 0.5, 11.5, rng, 0)
    finally:
        VK.SUN = old
    col_box2("SG_PropParterre", (x0, y0, z - 0.1), (x1, y1, z + 1.8))


def lamp(mb, x, y, z, kind):
    """poste do patio (acabamento 2026-09-29): o lantern_post da ordem (soco de obsidiana, fuste de ferro negro, colar
    dourado, lanterna com montantes e chapeu) - a MESMA familia da praca, do eixo e das ruas, no lugar do poste de
    cilindros empilhados; lanterna na mesma cota (z + 8,3). Os 4 ficam quentes: o violeta do patio e o da luz central
    (Court_Violet) e o do medalhao, baixos."""
    EM.lantern_post(mb, mb, (x, y, z), 0.0, h=7.4)
    col_box("SG_PropCourtLamp", (1.2, 1.2, 9.0), (x, y, z + 4.5))


def hooded_figure(mb, F, s, z0, body, void=OBS):
    """a FIGURA da ordem (estatua do patio e coroamento da fonte da praca): encapuzado de manto longo com as maos sobre
    a lamina fincada a frente. Referencial F (local +Y = frente), escala s, z0 = pe da figura (local).
    Acabamento 2026-09-29: o manto deixa de ser um cone liso - barra de 12 lados, DOBRAS verticais (5 pregas que
    afinam para cima), capa curta sobre os ombros, capuz com a borda em ponta emoldurando o rosto (vazio escuro),
    mangas com punho. Pedra lisa, sem brilho: le por silhueta e sombra."""
    rot = F.r()
    mb.cyl(1.4 * s, 0.55 * s, F.p(0, 0, z0 + 0.275 * s), rot, body, n=16, r2=1.28 * s, bevel=0.0)       # barra
    mb.cyl(1.28 * s, 4.9 * s, F.p(0, 0, z0 + 3.0 * s), rot, body, n=16, r2=0.84 * s, bevel=0.0)       # manto
    for deg, w in ((122.0, 0.34), (58.0, 0.34), (196.0, 0.3), (-16.0, 0.3), (270.0, 0.36)):
        c, d = math.cos(math.radians(deg)), math.sin(math.radians(deg))
        mb.beam(F.p(1.24 * s * c, 1.24 * s * d, z0 + 0.5 * s), F.p(0.8 * s * c, 0.8 * s * d, z0 + 5.2 * s),
                w * s, 0.24 * s, body, 0.0)                                                      # pregas
    mb.cyl(1.12 * s, 1.15 * s, F.p(0, -0.04 * s, z0 + 5.35 * s), rot, body, n=14, r2=0.64 * s, bevel=0.0)  # capa
    mb.cyl(0.74 * s, 1.9 * s, F.p(0, -0.12 * s, z0 + 6.75 * s), F.r(0.2), body, n=12, r2=0.1 * s, bevel=0.0)  # capuz
    mb.box((0.56 * s, 0.3 * s, 0.7 * s), F.p(0, 0.3 * s, z0 + 6.42 * s), F.r(0.2), void, 0.0)            # rosto
    for sg in (-1, 1):
        mb.beam(F.p(sg * 0.42 * s, 0.47 * s, z0 + 5.95 * s), F.p(0, 0.36 * s, z0 + 7.05 * s), 0.2 * s, 0.24 * s,
                body, 0.0)                                                                       # borda do capuz
        # mangas descendo para o cabo, punho alargado, mao
        mb.beam(F.p(sg * 0.95 * s, 0.05 * s, z0 + 5.2 * s), F.p(sg * 0.32 * s, 1.28 * s, z0 + 3.92 * s),
                0.5 * s, 0.55 * s, body, 0.0)
        mb.box((0.46 * s, 0.34 * s, 0.5 * s), F.p(sg * 0.3 * s, 1.3 * s, z0 + 3.9 * s), rot, body, 0.0)
        mb.box((0.34 * s, 0.4 * s, 0.36 * s), F.p(sg * 0.17 * s, 1.42 * s, z0 + 3.72 * s), rot, body, 0.0)
    # espada ESCULPIDA na mesma pedra da figura (acabamento: antes lamina chata + barra negra solta como guarda):
    # lamina afunilada ate a ponta fincada no plinto, guarda com as pontas alargadas, cabo redondo, pomo de prata.
    yb = 1.5 * s
    FP.frustum(mb, tuple(F.p(0, yb, z0 + 0.1 * s)), 0.1 * s, 0.07 * s, 0.46 * s, 0.15 * s, 3.08 * s, body,
               ang=F.a)                                                                  # lamina (ponta embaixo)
    mb.box((0.14 * s, 0.17 * s, 2.7 * s), F.p(0, yb, z0 + 1.75 * s), rot, body, 0.02 * s)  # aresta central
    mb.box((1.0 * s, 0.24 * s, 0.2 * s), F.p(0, yb, z0 + 3.28 * s), rot, body, 0.05 * s)  # guarda
    for sg in (-1, 1):
        mb.box((0.16 * s, 0.3 * s, 0.32 * s), F.p(sg * 0.54 * s, yb, z0 + 3.3 * s), rot, body, 0.05 * s)  # pontas
    mb.cyl(0.11 * s, 0.72 * s, F.p(0, yb, z0 + 3.74 * s), rot, body, n=8, bevel=0.0)       # cabo
    mb.ico(0.2 * s, tuple(F.p(0, yb, z0 + 4.2 * s)), SILVER, 1)                           # pomo


def statue(mb, x, y, z, yaw):
    """estatua da ordem: figura encapuzada de manto longo, maos sobre a lamina fincada a frente; pedestal de obsidiana,
    dado de pedra violeta com o medalhao da ordem e cornija clara. Local +Y = frente (yaw)."""
    F = SL.Frame(x, y, z, yaw - math.pi / 2)
    a = F.a
    # pedestal com MOLDURAS (acabamento): soco, chanfro de assento, dado violeta, cornija em talude + filete, plinto
    mb.box((3.6, 3.6, 0.6), F.p(0, 0, 0.3), F.r(), OBS, 0.1)
    FP.frustum(mb, tuple(F.p(0, 0, 0.6)), 3.6, 3.6, 2.8, 2.8, 0.3, OBS, ang=a)
    mb.box((2.7, 2.7, 2.5), F.p(0, 0, 0.9 + 1.25), F.r(), VIO, 0.08)
    FP.frustum(mb, tuple(F.p(0, 0, 3.4)), 2.72, 2.72, 3.4, 3.4, 0.32, TRIM, ang=a)
    mb.box((3.4, 3.4, 0.12), F.p(0, 0, 3.78), F.r(), TRIM, 0.0)
    mb.box((3.0, 3.0, 0.23), F.p(0, 0, 3.935), F.r(), OBS, 0.06)
    EM.plaque(mb, mb, mb, mb, tuple(F.p(0, 1.35 + 0.3, 2.2)), yaw, 0.82)
    # figura em pedra CLARA (a da cantaria): le contra a fachada escura; o rosto e um vazio de obsidiana
    hooded_figure(mb, F, 1.0, 4.05, TRIM)
    col_box("SG_PropStatue", (3.6, 3.6, 11.0), (x, y, z + 5.5), (0, 0, yaw))


GLYPHS = (0.25, 0.75, 0.5, 0.75, 0.25, 0.5)        # a "inscricao": a mesma sequencia nas 4 faces (nada aleatorio)


def obelisk(mb, x, y, z, face_yaw):
    """obelisco da ordem (acabamento 2026-09-29): base em 3 molduras + chanfro de assento, fuste afunilado com as
    ARESTAS em filete (as faces leem rebaixadas entre elas), colar de cantaria e piramidion de prata no topo. As runas
    ficam SO na face que olha o eixo, rentes (0,03) e no violeta baixo - gravadas, nao letreiro de neon."""
    hw0, hw1, zs0, zs1 = 0.95, 0.6, z + 1.9, z + 14.2
    mb.box((3.6, 3.6, 0.55), (x, y, z + 0.225), (0, 0, 0), OBS, 0.1)
    mb.box((2.8, 2.8, 1.0), (x, y, z + 1.0), (0, 0, 0), VIO, 0.08)
    mb.box((3.0, 3.0, 0.25), (x, y, z + 1.6), (0, 0, 0), TRIM, 0.06)
    mb.box((2.4, 2.4, 0.2), (x, y, z + 1.82), (0, 0, 0), OBS, 0.0)
    FP.frustum(mb, (x, y, z + 1.92), 2.4, 2.4, 2.0, 2.0, 0.34, OBS)
    mb.cyl(hw0 * math.sqrt(2), zs1 - zs0, (x, y, (zs0 + zs1) / 2), (0, 0, math.pi / 4), OBS, n=4,
           r2=hw1 * math.sqrt(2), bevel=0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.rod((x + sx * hw0, y + sy * hw0, zs0 + 0.3), (x + sx * hw1, y + sy * hw1, zs1 - 0.05), 0.2, OBS,
                   4)                                                                      # filete da aresta
    mb.box((2 * hw1 + 0.4, 2 * hw1 + 0.4, 0.26), (x, y, zs1 + 0.1), (0, 0, 0), TRIM, 0.0)  # colar
    SL.spire(mb, (x, y), hw1 * math.sqrt(2) + 0.1, zs1 + 0.23, 1.8, SILVER, n=4)          # piramidion

    def hw(zz):
        return hw0 + (hw1 - hw0) * (zz - zs0) / (zs1 - zs0)
    for k in range(4):
        a = k * math.pi / 2
        front = abs(((a - face_yaw + math.pi) % (2 * math.pi)) - math.pi) < 0.1
        if not front:
            continue
        nx, ny = math.cos(a), math.sin(a)
        tx, ty = -ny, nx
        for i, cb in enumerate(GLYPHS[:5]):
            zc = z + 6.2 + i * 1.5
            off = hw(zc) - 0.02
            p = (x + nx * off, y + ny * off)
            mb.box((0.1, 0.12, 0.85), (p[0], p[1], zc), (0, 0, a), THREAD_CASTLE, 0.0)
            side = 1 if i % 2 == 0 else -1
            mb.box((0.1, 0.36, 0.1), (p[0] + tx * side * 0.16, p[1] + ty * side * 0.16, zc - 0.425 + cb * 0.85),
                   (side * 0.6, 0, a), THREAD_CASTLE, 0.0)
        zc = z + 4.1
        off = hw(zc) + 0.3
        EM.plaque(mb, mb, mb, mb, (x + nx * off, y + ny * off, zc), a, 0.62)
    col_box("SG_PropObelisk", (3.6, 3.6, 15.0), (x, y, z + 7.5))


def muret(mb, x, y0, y1, z):
    """mureta de transicao: corpo de pedra da muralha + remate de obsidiana + pilares de ponta"""
    mb.box2((x - 0.45, y0, z - 0.1), (x + 0.45, y1, z + 1.0), BLOCK, 0.08)
    mb.box2((x - 0.65, y0 - 0.1, z + 1.0), (x + 0.65, y1 + 0.1, z + 1.28), OBS, 0.06)
    for yy in (y0, y1):
        mb.box((1.5, 1.5, 1.7), (x, yy, z + 0.75), (0, 0, 0), BLOCK, 0.08)
        mb.box((1.75, 1.75, 0.3), (x, yy, z + 1.75), (0, 0, 0), OBS, 0.06)
        SL.spire(mb, (x, yy), 0.9, z + 1.9, 1.0, OBS, n=4)
    col_box2("SG_PropMuret", (x - 0.75, y0 - 0.75, z - 0.1), (x + 0.75, y1 + 0.75, z + 1.9))


def iron_arch(mb, cx, y, z, hs, glass, post_h=10.0, rise=5.4, lanterns=True, col=True, area="SG_PropArch"):
    """arco leve de ferro negro (transicao entre espacos): 2 postes com soco de obsidiana, arco ogival abatido de
    2 trilhos com montantes, remate de prata no fecho e lanternas penduradas para dentro. SEM emblema: os arcos ficam
    no eixo, na frente do emblema monumental da fachada (simbolo empilhado = ruido). Sem colisao no vao (so os
    postes). Devolve as posicoes das lanternas."""
    lan = []
    for s in (-1, 1):
        x = cx + s * hs
        mb.box((1.5, 1.5, 1.0), (x, y, z + 0.4), (0, 0, 0), OBS, 0.1)
        mb.box((1.2, 1.2, 0.2), (x, y, z + 1.0), (0, 0, 0), VIO, 0.0)
        mb.box((0.56, 0.56, post_h - 1.1), (x, y, z + 1.1 + (post_h - 1.1) / 2), (0, 0, 0), IRON, 0.0)
        for zz in (z + 4.2, z + post_h - 0.2):
            mb.box((0.8, 0.8, 0.22), (x, y, zz), (0, 0, 0), IRON, 0.0)
        mb.box((0.9, 0.9, 0.35), (x, y, z + post_h + 0.175), (0, 0, 0), IRON, 0.0)
        mb.box((0.34, 1.1, 0.34), (x, y, z + post_h + 0.1), (0, 0, 0), SILVER, 0.0)     # prata na nascenca do arco
        if lanterns:
            ax = x - s * 1.25
            mb.beam((x - s * 0.28, y, z + 8.9), (ax + s * 0.1, y, z + 8.9), 0.16, 0.2, IRON, 0.0)
            mb.beam((x - s * 0.28, y, z + 8.1), (x - s * 0.9, y, z + 8.9), 0.12, 0.14, IRON, 0.0)
            zc = z + 7.9
            mb.rod((ax, y, z + 8.9), (ax, y, zc + 0.75), 0.05, IRON, 4)
            mb.box((0.62, 0.62, 1.0), (ax, y, zc), (0, 0, 0), glass, 0.0)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    mb.box((0.14, 0.14, 1.12), (ax + sx * 0.34, y + sy * 0.34, zc), (0, 0, 0), IRON, 0.0)
            mb.box((0.9, 0.9, 0.14), (ax, y, zc - 0.55), (0, 0, 0), IRON, 0.0)
            SL.spire(mb, (ax, y), 0.7, zc + 0.55, 0.8, IRON, n=4)
            lan.append((ax, y, zc))
        if col:
            col_box(area, (1.4, 1.4, post_h + 1.0), (x, y, z + (post_h + 1.0) / 2))
    # arco: 2 trilhos (curva cubica abatida e pontuda no fecho) + montantes
    zs = z + post_h + 0.35
    for off, rad in ((0.0, 0.2), (-0.95, 0.13)):
        for s in (-1, 1):
            pts = bez((cx + s * hs, off), (cx + s * hs, 0.52 * rise + off), (cx + s * 0.33 * hs, 0.86 * rise + off),
                      (cx, rise + off), 10)
            prof = [(rad * math.cos(2 * math.pi * i / 6), rad * math.sin(2 * math.pi * i / 6)) for i in range(6)]
            # 'up' = normal do plano do arco: o referencial do perfil nao vira no trecho vertical (sem face torcida)
            mb.sweep([(px, y, zs + pz) for px, pz in pts], prof, IRON, True, None, up=(0.0, 1.0, 0.0))
    for s in (-1, 1):
        o = bez((cx + s * hs, 0.0), (cx + s * hs, 0.52 * rise), (cx + s * 0.33 * hs, 0.86 * rise), (cx, rise), 10)
        i = bez((cx + s * hs, -0.95), (cx + s * hs, 0.52 * rise - 0.95), (cx + s * 0.33 * hs, 0.86 * rise - 0.95),
                (cx, rise - 0.95), 10)
        for t in (3, 6, 8):
            mb.beam((o[t][0], y, zs + o[t][1] - 0.1), (i[t][0], y, zs + i[t][1] + 0.08), 0.12, 0.12, IRON, 0.0)
    SL.spire(mb, (cx, y), 0.34, zs + rise + 0.1, 1.2, IRON, n=4)          # remate do fecho
    mb.ico(0.16, (cx, y, zs + rise + 1.35), SILVER, 1)
    # fecho: gota de prata pendurada do trilho de baixo (marca o eixo sem repetir o simbolo)
    mb.rod((cx, y, zs + rise - 0.95), (cx, y, zs + rise - 1.6), 0.05, IRON, 4)
    mb.cyl(0.26, 0.7, (cx, y, zs + rise - 1.95), (0, 0, 0), SILVER, n=8, r2=0.02, bevel=0.0)
    mb.cyl(0.26, 0.3, (cx, y, zs + rise - 1.45), (math.pi, 0, 0), SILVER, n=8, r2=0.02, bevel=0.0)
    return lan


def court():
    rng = random.Random(3603)
    mb = MB("SG_Prop_Court", COLL, rng, detail="near")
    z = P3
    for s in (-1, 1):
        parterre(mb, s, random.Random(3610 + s))
    for x, y, kind in LAMPS:
        lamp(mb, x, y, z, kind)
    for x, y in STATUES:
        # de frente para quem chega (sul), um pouco voltadas para o eixo
        statue(mb, x, y, z, -math.pi / 2 - math.copysign(math.radians(18.0), x))
    for x, y in OBELISKS:
        obelisk(mb, x, y, z, math.pi if x > 0 else 0.0)
    for x, y0, y1 in MURETS:
        muret(mb, x, y0, y1, z)
    mb.finish()
    # arco de ferro no pe da escada do portao (entrada do recinto do castelo): lanternas QUENTES (so Neon) - o arco
    # fica na rua do P2 (vila): violeta forte ali era "magia" fora do lugar
    ma = MB("SG_Prop_GateArch", COLL, random.Random(3604), detail="near")
    x, y, zz, hs = GATE_ARCH
    iron_arch(ma, x, y, zz, hs, WARM_G)
    ma.finish()


def build():
    axis_south()
    axis_north()
    court()
