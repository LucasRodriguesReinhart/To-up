# sg_court - VESTIR / PATIO E CAMINHOS NOBRES da Ilha 3 (Shadow Garden). Roda ANTES do sg_veg (zona dressing).
# O exterior deixa de ser "laje lisa": um SISTEMA de leitura, simetrico onde e cerimonial.
#   1. CAMINHO DA ORDEM (eixo nobre): calcada alta da entrada -> praca -> pe da escada P1P2 -> rua do eixo (P2) -> portao
#      da muralha -> patio -> porta do castelo. Lajes grandes de marmore negro, borda de obsidiana e um FIO violeta
#      (SG_VioletDeep_Glow) rente no centro; juntas de prata a cada 4 fiadas. Topo <= cota + 0,05 (nada de degrau).
#   2. PATIO DO CASTELO (CASTLE_FORECOURT): (o medalhao do EMBLEMA no chao saiu no ajuste 19: o eixo segue continuo),
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
# OVERHAUL 12 (2026-09-29, props globais): lanterna SO nos NOS - os 3 pares de pedestais do eixo do P2 e o par de
# postes do patio SAIRAM (os arcos de ferro nas 2 pontas do eixo, o poste do cruzamento e os postes do patamar do
# portao ja marcam os nos); remate do mastro (codigo parado) em florao torneado no lugar da piramide.
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, fm_lib
import sg_layout as L
import sg_emblem as EM
import fm_parts as FP
import sg_veg as VEG                 # cipreste do canteiro (mesma arvore da ilha) + material do luar das folhas
import fm_veg_kit as VK
import sg_garden as GD           # kit de jardinagem (sebe de buxo, flores, trepadeiras)

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
# overhaul 01 (2026-09-29): cantaria de remate um valor abaixo do Stone_SG_Trim (o mesmo do sg_entry e da praca)
CAP = "Stone_SG_TrimLow"
fm_lib.MATS.setdefault(CAP, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
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
MED_C = (0.0, 20.0)                   # cruzamento do eixo com a travessia patio -> dungeon/beco (era o centro do
                                      # medalhao da lua no chao, que SAIU no ajuste 19)
AXIS_W = 14.0                         # eixo do patio (livre)
PATH_W = 12.0                         # eixo na calcada alta, pe da escada e rua do P2
PARTERRE_X = (12.0, 37.0)             # |x| dos canteiros
PARTERRE_Y = (3.5, 15.0)
# OVERHAUL 03 (03.04): o par NORTE (-+8,4; 28,5) SAIU - cortava a estatua ao meio na linha de visao de quem sobe
# para a porta (mover para x +-9,5 / y 23 caia de novo no cone de quem vem do portao). A porta ja tem a luz quente
# dela (L_SGCas_Door) e o violeta baixo central (Court_Violet); o par sul marca a entrada do patio.
# OVERHAUL 12 (12.04): o par sul tambem SAIU - repetia, 10 studs adiante, o par de postes do patamar do portao
# (sg_castle, o NO de verdade: topo da escada + portao). O patio fica com o portao, as estatuas e a luz central.
LAMPS = []
STATUES = [(-12.5, 33.5), (12.5, 33.5)]
OBELISKS = [(-21.0, 29.0), (21.0, 29.0)]
MURETS = [(-45.0, 0.0, 13.5), (45.0, 0.0, 13.5)]
GATE_ARCH = (0.0, -28.0, P2, 9.4)     # (x, y, z, meia-abertura) arco de ferro no pe da escada do portao
# acabamento 2026-09-29: os 2 mastros com estandarte na saida norte da praca SAIRAM (repetiam, na frente, os
# estandartes da fachada do castelo; o arco de ferro do topo da escada P1P2 ja marca a transicao)
PLAZA_MASTS = []
# lanternas do eixo no P2 (referencia v2): pares em x = +-7.6 (fora da largura util de 12 do caminho), a cada ~14;
# o vao -50 fica com o lantern_post da vila em (7.8, -51.6) (nada de cacho de postes no cruzamento)
# OVERHAUL 12 (12.04/16.04): os 3 pares de pedestais SAIRAM (cerca de luz a cada 14). Os NOS do eixo ja tem lanterna:
# topo da escada P1P2 = arco de ferro da vila (2 lanternas acesas), cruzamento com a rua do P2 = poste da vila
# (7.8, -51.6, aceso), pe da escada do portao = arco de ferro do patio (GATE_ARCH, 2 lanternas). Nenhuma luz real muda.
AXIS_LANTERN_X = 7.6
AXIS_LANTERN_Y = ()
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
               thread_m=THREAD_VIL, filete=True):
    """eixo nobre ao longo de +Y (x = 0) de y0 a y1, largura W, piso na cota z.
    base de obsidiana (juntas/canal do fio) + bordas de obsidiana + lajes grandes de marmore negro (uma por lado e por
    fiada) + fio no centro. thread/slabs/border = (y_ini, y_fim) opcionais (quando o medalhao come um trecho).
    Overhaul 01 (2026-09-29): fiadas em RITMO A-B (2,4 / 3,6) com chanfro de 0,04, junta de prata SO a cada 8 fiadas e
    o filete claro da aresta so onde o piso em volta nao contrasta (filete=False na calcada alta e na praca; e em
    cantaria baixa, nao mais no Stone_SG_Trim quase branco)."""
    hw = W / 2.0
    bd = 0.9                                     # borda
    mb.box2((-hw, y0, z - 0.2), (hw, y1, z + 0.02), OBS, 0.0)
    by0, by1 = border[0] if border[0] is not None else y0, border[1] if border[1] is not None else y1
    for s in (-1, 1):
        xa, xb = sorted((s * (hw - (0.24 if filete else 0.0)), s * (hw - bd)))
        mb.box2((xa, by0, z - 0.05), (xb, by1, z + 0.05), OBS, 0.0)
        if filete:
            xa, xb = sorted((s * hw, s * (hw - 0.24)))
            mb.box2((xa, by0, z - 0.05), (xb, by1, z + 0.05), CAP, 0.0)
    sy0, sy1 = slabs[0] if slabs[0] is not None else y0, slabs[1] if slabs[1] is not None else y1
    Lr = sy1 - sy0
    pat = (2.4, 3.6)
    rows, acc = [], 0.0
    while acc < Lr - 0.6 or not rows:
        rows.append(pat[len(rows) % 2])
        acc += rows[-1]
    k_ = Lr / acc
    xin, xout = 0.55, hw - bd - 0.12
    yy = sy0
    for k, ln in enumerate(rows):
        ya, yb = yy + 0.06, yy + ln * k_ - 0.06
        for s in (-1, 1):
            xa, xb = sorted((s * xin, s * xout))
            mb.box2((xa, ya, z - 0.05), (xb, yb, z + 0.045), MARB, 0.04)
        if k > 0 and k % 8 == 0:
            mb.box2((-xout, yy - 0.06, z - 0.05), (xout, yy + 0.06, z + 0.035), SILVER, 0.0)
        yy += ln * k_
    ty0, ty1 = thread[0] if thread[0] is not None else y0, thread[1] if thread[1] is not None else y1
    mb.box2((-0.14, ty0, z - 0.05), (0.14, ty1, z + 0.05), thread_m, 0.0)


def axis_south():
    """calcada alta da entrada ate a praca + o trecho entre a praca e o pe da escada P1P2 (P1)"""
    mb = MB("SG_Prop_NobleAxis_P1", COLL, random.Random(3601), detail="near")
    y_top = L.ENTRY_STAIR_Y1 + 0.35                  # topo da escadaria da entrada (-187,65)
    y_plaza_s = L.PLAZA_C[1] - L.PLAZA_R + 1.0       # a borda de cantaria da praca cobre a junta
    noble_path(mb, y_top, y_plaza_s, PATH_W, P1, filete=False)
    foot = L.stair_frame("P1P2")[0]
    noble_path(mb, L.PLAZA_C[1] + L.PLAZA_R - 1.0, foot[1] - 0.02, PATH_W, P1, filete=False)
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
    # remate do kit (12.12): florao torneado no lugar da piramide de 4 lados + bola
    EM._lathe(mb, (x, y, z + 13.05), [(0.2, 0.0), (0.14, 0.2), (0.3, 0.46), (0.1, 0.82), (0.0, 1.45)], SILVER, 6,
              math.pi / 6)
    top = (x + fx * 0.36, y + fy * 0.36, z + 12.6)
    EM.banner(mb, mb, mb, mb, top, yaw, 3.0, 7.4, trim=EM.BRONZE)
    col_box("SG_PropMast", (1.2, 1.2, 14.0), (x, y, z + 7.0))


def axis_north():
    """rua do eixo no P2 + portao + patio do castelo (P3) com o eixo continuo; o arco de ferro no pe da escada do portao"""
    mb = MB("SG_Prop_NobleAxis_P2P3", COLL, random.Random(3602), detail="near")
    y_p2_0 = L.stair_top("P1P2")[1] + 0.02          # -83
    y_p2_1 = L.stair_frame("Gate")[0][1] - 0.02      # -26
    noble_path(mb, y_p2_0, y_p2_1, PATH_W, P2)
    # (vazio desde o overhaul 12: o eixo so tem lanterna nos NOS - ver AXIS_LANTERN_Y)
    for yy in AXIS_LANTERN_Y:
        for s in (-1, 1):
            EM.lantern_pedestal(mb, mb, mb, (s * AXIS_LANTERN_X, yy, P2), 0.0, 1.0)
            col_box("SG_PropLantern", (1.9, 1.9, 3.6), (s * AXIS_LANTERN_X, yy, P2 + 1.8))
    # patio: do portao (face sul da muralha) ate a porta, CONTINUO. Ajuste 19 (2026-09-30): o medalhao da lua no chao
    # SAIU (o jogador lia como placa de teleporte) - no lugar dele o mesmo piso do eixo segue sem emenda e as 2
    # travessias encostam na borda do eixo
    y_gate = L.WALL_Y0 + 0.02                        # -8,98 (topo da escada do portao)
    y_door = L.CASTLE_FACADE_Y - 0.02
    noble_path(mb, y_gate, y_door, AXIS_W, P3, thread_m=THREAD_CASTLE)
    for s in (-1, 1):
        cross_walk(mb, s)
    mb.finish()


def cross_walk(mb, s, hw=3.6, x_end=(44.0, 44.9)):
    """travessia secundaria do patio (da borda do eixo nobre ate a borda do patio): lajota escura (Stone_SG_Floor) com
    faixas de cantaria clara rentes nas bordas - abaixo do eixo nobre na hierarquia, acima do piso liso. Ajuste 19: sem
    o medalhao, nasce reta na borda do eixo (x = +-AXIS_W / 2) no cruzamento MED_C"""
    cx, cy = MED_C
    z = P3
    xe = x_end[1] if s > 0 else x_end[0]
    x0 = cx + s * AXIS_W / 2.0
    poly = [(x0, cy - hw), (x0, cy + hw), (s * xe, cy + hw), (s * xe, cy - hw)]
    mb.prism(SL.ccw(poly), z - 0.1, z + 0.03, "Stone_SG_Floor")
    for e in (-1, 1):
        ya, yb = sorted((cy + e * hw, cy + e * (hw - 0.55)))
        xa, xb = sorted((x0, s * xe))
        mb.box2((xa, ya, z - 0.05), (xb, yb, z + 0.045), CAP, 0.0)
    # juntas transversais a cada 3,2 (fiadas), e a soleira na ponta
    xs = abs(x0)
    k = 1
    while xs + 3.2 * k < xe - 1.0:
        xj = s * (xs + 3.2 * k)
        mb.box2((xj - 0.07, cy - hw + 0.55, z - 0.05), (xj + 0.07, cy + hw - 0.55, z + 0.04), OBS, 0.0)
        k += 1
    xa, xb = sorted((s * (xe - 0.6), s * xe))
    mb.box2((xa, cy - hw, z - 0.05), (xb, cy + hw, z + 0.045), CAP, 0.0)


# ------------------------------------------------------------------ 2. patio: canteiros, estatuas, obeliscos, postes
def hedge(mb, a, b, w=0.8, h=0.95, z=P3 + 0.5):
    """sebe de BUXO de a a b (xy). JARDINAGEM 2026-09-29 (sg_garden): topo ARREDONDADO (perfil de 8 pontos: paredes
    quase retas e meia-cana em 3 lances; antes topo chanfrado de 6 lados + faixa de luar colada) no verde do buxo"""
    GD.hedge_round(mb, a, b, w, h, z, GD.LEAF_BOX)


def parterre(mb, s, rng, mg=None):
    """canteiro do patio = JARDIM DE LUA formal (jardinagem 2026-09-29, pedido do usuario). Mesmo envelope e mesma
    colisao de antes (a volta COURT_JARDIM_* nao muda); a mureta de obsidiana, os pilaretes e o cipreste ficam.
    Dentro: sebe de buxo de topo arredondado na moldura com BOLAS de topiaria nas quinas e nas bocas dos caminhos,
    rosas brancas entremeadas no topo da sebe, CASCALHO nos caminhos (cruz + roda em volta do cipreste, que ganha
    uma sebe redonda de 12 lances), e 4 compartimentos de cantaria baixa com FAIXAS de cor: lavanda junto da moldura,
    massa de flores-da-lua no meio, campanulas junto do caminho (espelhado: o desenho le simetrico do eixo).
    mb = pedra/sebes/cipreste (SG_Prop_Court), mg = plantas (SG_Veg_Gdn_Court)."""
    mg = mg or mb
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
    # overhaul 03 (03.06/12.12): dado de canto de quinas chanfradas, capa moldurada e o remate do kit (bola com
    # colar, cantaria baixa) no lugar da piramide de 4 lados
    import sg_entry as SE
    for px in (x0 + 0.6, x1 - 0.6):
        for py in (y0 + 0.6, y1 - 0.6):
            mb.prism(SE.chamfer_sq(px, py, 0.65, 0.16), z - 0.1, z + 1.12, OBS)
            mb.box((1.5, 1.5, 0.14), (px, py, z + 1.19), (0, 0, 0), CAP, 0.03)
            mb.box((1.3, 1.3, 0.12), (px, py, z + 1.32), (0, 0, 0), CAP, 0.03)
            SE.finial(mb, px, py, z + 1.38, 0.4, m=CAP, n=8)
    # terra (leito do canteiro) + cascalho em toda a area de dentro da moldura (os caminhos do jardim)
    zt = z + 0.62
    mb.box2((x0 + bw, y0 + bw, z - 0.1), (x1 - bw, y1 - bw, zt), SOIL, 0.0)
    i0, i1, j0, j1 = x0 + bw + 0.55, x1 - bw - 0.55, y0 + bw + 0.55, y1 - bw - 0.55
    mb.box2((i0 + 0.3, j0 + 0.3, zt - 0.04), (i1 - 0.3, j1 - 0.3, zt + 0.04), GD.GRAVEL, 0.0)
    zg = zt + 0.04
    # moldura de buxo (sebe arredondada) + bolas de topiaria nas 4 quinas
    hedge(mb, (i0 + 0.3, j0), (i1 - 0.3, j0))
    hedge(mb, (i0 + 0.3, j1), (i1 - 0.3, j1))
    hedge(mb, (i0, j0 + 0.3), (i0, j1 - 0.3))
    hedge(mb, (i1, j0 + 0.3), (i1, j1 - 0.3))
    for px in (i0, i1):
        for py in (j0, j1):
            GD.topiary(mb, (px, py, z + 0.5), 0.66, squash=0.95)
    # rosas brancas no topo das sebes compridas (a roseira entremeada no buxo)
    for py in (j0, j1):
        GD.hedge_roses(mg, (i0 + 0.9, py), (i1 - 0.9, py), z + 0.5 + 0.95, step=2.3)
    # roda do cipreste: sebe redonda de 12 lances (r 2,4) com 4 bocas; bolas pequenas nas bocas do caminho em cruz
    rr = 2.4
    for k in range(12):
        a0 = math.radians(15.0 + 30.0 * k)
        a1 = math.radians(15.0 + 30.0 * (k + 1))
        if k % 3 == 2:
            continue                                   # bocas a 0/90/180/270 (a cruz de cascalho chega ao cipreste)
        hedge(mb, (cx + rr * math.cos(a0), cy + rr * math.sin(a0)), (cx + rr * math.cos(a1), cy + rr * math.sin(a1)),
              w=0.62, h=0.8)
    for k in range(4):
        a = math.radians(90.0 * k)
        for sg in (-1, 1):
            b = a + sg * math.radians(15.0)
            GD.topiary(mb, (cx + (rr + 0.05) * math.cos(b), cy + (rr + 0.05) * math.sin(b), z + 0.5), 0.36)
    # 4 compartimentos de flores em faixas (entre a moldura, o caminho em cruz e a roda)
    for (xa, xb) in ((i0 + 0.75, cx - rr - 0.9), (cx + rr + 0.9, i1 - 0.75)):
        GD.formal_bed(mb, mg, xa, xb, j0 + 0.75, cy - 0.65, zg, outer=-1)
        GD.formal_bed(mb, mg, xa, xb, cy + 0.65, j1 - 0.75, zg, outer=1)
    # cipreste no centro (a mesma especie da ilha: le como plantado, nao enfeite)
    old = VK.SUN
    VK.SUN = VEG.MOON_DIR
    try:
        VEG.cypress(mb, cx, cy, z + 0.5, 7.6, rng, 0)          # overhaul 03: 11,5 tapava a fachada
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


def muret(mb, x, y0, y1, z):
    """mureta de transicao. Overhaul 03 (03.07): corpo de cantaria em 2 fiadas com juntas desencontradas, CAPA
    moldurada com pingadeira nos 2 lados e os pilaretes do kit (plinto + toro, fuste chanfrado, capitel, bola com
    colar) nas pontas - antes corpo-caixa, remate-caixa, pilar-caixa e piramide"""
    import sg_entry as SE
    for zc_, hc_, off in ((z - 0.1, 0.62, 0.0), (z + 0.52, 0.5, 1.2)):
        cuts = [y0 + 0.8] + [y0 + 0.8 + off + 2.4 * j for j in range(1, 8) if y0 + 0.8 + off + 2.4 * j < y1 - 1.4] +                [y1 - 0.8]
        for a_, b_ in zip(cuts, cuts[1:]):
            mb.box2((x - 0.45, a_ + 0.04, zc_ + 0.03), (x + 0.45, b_ - 0.04, zc_ + hc_ - 0.03), SE.PAR_M, 0.05)
    mb.box2((x - 0.4, y0, z - 0.1), (x + 0.4, y1, z + 1.0), SE.PAR_M, 0.0)
    for sx in (-1, 1):
        a_, b_ = sorted((x + sx * 0.3, x + sx * 0.66))
        mb.box2((a_, y0 + 0.6, z + 1.0), (b_, y1 - 0.6, z + 1.12), CAP, 0.0)
    FP.frustum(mb, (x, (y0 + y1) / 2, z + 1.12), 1.32, y1 - y0 - 1.2, 1.0, y1 - y0 - 1.4, 0.2, CAP)
    for yy in (y0, y1):
        SE._post(mb, x, yy, z - 0.1, 1.4, 1.35, lamp=False)
    col_box2("SG_PropMuret", (x - 0.75, y0 - 0.75, z - 0.1), (x + 0.75, y1 + 0.75, z + 1.9))


def court():
    rng = random.Random(3603)
    mb = MB("SG_Prop_Court", COLL, rng, detail="near")
    # jardinagem 2026-09-29: as plantas do jardim do patio num objeto proprio (1 MeshPart por material)
    mg = MB("SG_Veg_Gdn_Court", "10_VEGETATION", None, detail="near", floor=-999)
    z = P3
    for s in (-1, 1):
        parterre(mb, s, random.Random(3610 + s), mg)
    GD.court_vines(mg)                  # roseiras trepadeiras na face interna da muralha, atras dos canteiros
    mg.finish(recalc=False)
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
    # overhaul 03: o arco do KIT da vila (sg_village.iron_arch: postes torneados, volutas, maos-francesas, remate
    # torneado) - o CT.iron_arch antigo (postes-caixa, piramide no fecho) saiu daqui
    import sg_village as VL
    ma = MB("SG_Prop_GateArch", COLL, random.Random(3604), detail="near")
    x, y, zz, hs = GATE_ARCH
    VL.iron_arch(ma, x, y, zz, hs, area="SG_PropArch")
    ma.finish()


def build():
    GD.reset()
    axis_south()
    axis_north()
    court()
