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
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, fm_lib
import sg_layout as L
import sg_emblem as EM
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
PLAZA_MASTS = [(-11.5, -102.6), (11.5, -102.6)]
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
def noble_path(mb, y0, y1, W, z, thread=(None, None), slabs=(None, None), border=(None, None), row=3.0):
    """eixo nobre ao longo de +Y (x = 0) de y0 a y1, largura W, piso na cota z.
    base de obsidiana (juntas/canal do fio) + bordas de obsidiana + lajes grandes de marmore negro (uma por lado e por
    fiada) + fio violeta no centro + junta de prata a cada 4 fiadas. thread/slabs/border = (y_ini, y_fim) opcionais
    (quando o medalhao come um trecho)."""
    hw = W / 2.0
    bd = 0.9                                     # borda
    mb.box2((-hw, y0, z - 0.2), (hw, y1, z + 0.02), OBS, 0.0)
    by0, by1 = border[0] if border[0] is not None else y0, border[1] if border[1] is not None else y1
    for s in (-1, 1):
        xa, xb = sorted((s * hw, s * (hw - bd)))
        mb.box2((xa, by0, z - 0.05), (xb, by1, z + 0.05), OBS, 0.0)
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
    mb.box2((-0.14, ty0, z - 0.05), (0.14, ty1, z + 0.05), THREAD, 0.0)


def medallion(mb, c, r, z):
    """o EMBLEMA da ordem no chao, rente (sg_emblem em planta): lua violeta em eclipse (disco negro deslocado), aneis e
    lamina de prata, guarda/cabo de obsidiana, 8 raios curtos de prata sobre um aro de obsidiana. 'Cima' do emblema =
    norte (a lamina aponta para a porta do castelo). Camadas sem sobreposicao coplanar: 0,02 / 0,035 / 0,05."""
    cx, cy = c
    zt1, zt2, zt3 = z + 0.02, z + 0.035, z + 0.05
    ring(mb, c, 0.96 * r, 1.365 * r, z - 0.1, zt1, OBS, 64)             # aro
    ring(mb, c, 0.84 * r, 0.96 * r, z - 0.05, zt3, SILVER, 64)          # anel externo
    ring(mb, c, 0.80 * r, 0.84 * r, z - 0.1, zt1, MARB, 56)             # entre aneis
    ring(mb, c, 0.765 * r, 0.80 * r, z - 0.05, zt3, SILVER, 56)         # anel interno
    ring(mb, c, 0.74 * r, 0.765 * r, z - 0.1, zt1, THREAD, 56)          # halo da lua (linha de energia)
    disc(mb, c, 0.74 * r, z - 0.1, zt1, VIO, 48)                        # a lua
    disc(mb, (cx + 0.26 * r, cy + 0.10 * r), 0.64 * r, z - 0.08, zt2, OBS, 48)   # a sombra que come a lua
    # lamina (prata) apontando para o norte, ponta em triangulo
    bw = max(0.6, 0.10 * r)
    ya, yb = cy - 0.433 * r, cy + 0.993 * r
    mb.box2((cx - bw / 2, ya, z - 0.04), (cx + bw / 2, yb, zt3), SILVER, 0.0)
    mb.prism(SL.ccw([(cx - bw / 2, yb), (cx + bw / 2, yb), (cx, yb + 0.22 * r)]), z - 0.04, zt3, SILVER)
    # guarda e cabo (obsidiana, como no emblema) + pomo de prata
    gw = 0.09 * r
    mb.box2((cx - 0.31 * r, cy - 0.05 * r - gw / 2, z - 0.04), (cx + 0.31 * r, cy - 0.05 * r + gw / 2, zt3), OBS, 0.0)
    mb.box2((cx - gw / 2, cy - 0.57 * r, z - 0.04), (cx + gw / 2, cy - 0.11 * r, zt3), OBS, 0.0)
    disc(mb, (cx, cy - 0.62 * r), 0.075 * r, z - 0.04, zt3, SILVER, 12)
    # 8 raios (versao monumental) sobre o aro
    for k in range(8):
        t = 2 * math.pi * k / 8 + math.pi / 8
        Lr = r * (0.34 if k % 2 == 0 else 0.22)
        rm = r * 1.0 + Lr / 2
        mb.box((Lr, 0.07 * r, zt3 - z + 0.04), (cx + rm * math.cos(t), cy + rm * math.sin(t), (zt3 + z - 0.04) / 2),
               (0, 0, t), SILVER, 0.0)


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
    EM.banner(mb, mb, mb, mb, top, yaw, 3.0, 7.4)
    col_box("SG_PropMast", (1.2, 1.2, 14.0), (x, y, z + 7.0))


def axis_north():
    """rua do eixo no P2 + portao + patio do castelo (P3) com o medalhao; o arco de ferro no pe da escada do portao"""
    mb = MB("SG_Prop_NobleAxis_P2P3", COLL, random.Random(3602), detail="near")
    y_p2_0 = L.stair_top("P1P2")[1] + 0.02          # -83
    y_p2_1 = L.stair_frame("Gate")[0][1] - 0.02      # -26
    noble_path(mb, y_p2_0, y_p2_1, PATH_W, P2)
    # patio: do portao (face sul da muralha) ate a porta; o medalhao come o trecho do meio
    cx, cy = MED_C
    y_gate = L.WALL_Y0 + 0.02                        # -8,98 (topo da escada do portao)
    y_door = L.CASTLE_FACADE_Y - 0.02
    hwA = AXIS_W / 2.0
    edge = math.sqrt(MED_RIM ** 2 - (hwA - 0.45) ** 2)      # onde a borda do eixo encontra o aro
    noble_path(mb, y_gate, cy - math.sqrt(MED_RIM ** 2 - hwA ** 2), AXIS_W, P3,
               thread=(None, cy - 0.96 * MED_R - 0.02), slabs=(None, cy - MED_RIM - 0.1), border=(None, cy - edge))
    noble_path(mb, cy + math.sqrt(MED_RIM ** 2 - hwA ** 2), y_door, AXIS_W, P3,
               thread=(cy + 1.213 * MED_R + 0.01, None), slabs=(cy + MED_RIM + 0.1, None), border=(cy + edge, None))
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
                    mb.ico(0.62, (xx, yy, z + 0.86), BLOOM, 1, scale=(1.0, 1.0, 0.7))
    # cipreste no centro (a mesma especie da ilha: le como plantado, nao enfeite)
    old = VK.SUN
    VK.SUN = VEG.MOON_DIR
    try:
        VEG.cypress(mb, cx, cy, z + 0.5, 11.5, rng, 0)
    finally:
        VK.SUN = old
    col_box2("SG_PropParterre", (x0, y0, z - 0.1), (x1, y1, z + 1.8))


def lamp(mb, x, y, z, kind):
    """poste de ferro negro do patio: soco de obsidiana, fuste, gaiola com vidro quente (sul) ou violeta (norte)"""
    glass = WARM_G if kind == "warm" else RUNE
    mb.cyl(0.8, 0.9, (x, y, z + 0.35), (0, 0, math.pi / 8), OBS, n=8, bevel=0.0)
    mb.cyl(0.9, 0.16, (x, y, z + 0.86), (0, 0, math.pi / 8), VIO, n=8, bevel=0.0)
    mb.cyl(0.5, 0.5, (x, y, z + 1.15), (0, 0, math.pi / 8), IRON, n=8, r2=0.28, bevel=0.0)
    mb.cyl(0.24, 6.3, (x, y, z + 4.5), (0, 0, 0), IRON, n=8, r2=0.17, bevel=0.0)
    mb.cyl(0.4, 0.3, (x, y, z + 4.2), (0, 0, 0), IRON, n=8, bevel=0.0)
    zc = z + 8.3
    mb.box((1.35, 1.35, 0.25), (x, y, zc - 0.95), (0, 0, 0), IRON, 0.0)
    mb.cyl(0.35, 0.6, (x, y, zc - 1.3), (0, 0, 0), IRON, n=8, r2=0.2, bevel=0.0)
    mb.box((0.85, 0.85, 1.5), (x, y, zc), (0, 0, 0), glass, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.22, 0.22, 1.7), (x + sx * 0.5, y + sy * 0.5, zc), (0, 0, 0), IRON, 0.0)
    SL.spire(mb, (x, y), 1.08, zc + 0.85, 1.7, IRON, n=4)
    mb.ico(0.2, (x, y, zc + 2.7), SILVER, 1)
    col_box("SG_PropCourtLamp", (1.0, 1.0, 9.0), (x, y, z + 4.5))


def statue(mb, x, y, z, yaw):
    """estatua da ordem: figura encapuzada de manto longo, maos sobre a lamina fincada a frente; pedestal de obsidiana,
    dado de pedra violeta com o medalhao da ordem e cornija clara. Local +Y = frente (yaw)."""
    F = SL.Frame(x, y, z, yaw - math.pi / 2)
    mb.box((3.6, 3.6, 0.6), F.p(0, 0, 0.3), F.r(), OBS, 0.1)
    mb.box((3.1, 3.1, 0.3), F.p(0, 0, 0.75), F.r(), OBS, 0.06)
    mb.box((2.7, 2.7, 2.5), F.p(0, 0, 0.9 + 1.25), F.r(), VIO, 0.08)
    mb.box((3.4, 3.4, 0.4), F.p(0, 0, 3.4 + 0.2), F.r(), TRIM, 0.08)
    mb.box((3.0, 3.0, 0.25), F.p(0, 0, 3.8 + 0.125), F.r(), OBS, 0.0)
    EM.plaque(mb, mb, mb, mb, tuple(F.p(0, 1.35 + 0.3, 2.2)), yaw, 0.82)
    z0 = 4.05
    rot = F.r()
    # manto: barra alargada + corpo conico + ombros + capuz pontudo (inclinado para tras) + abertura escura do rosto.
    # Pedra CLARA (a da cantaria): a figura le contra a fachada escura; o rosto e um vazio de obsidiana
    ST = TRIM
    mb.cyl(1.38, 0.55, F.p(0, 0, z0 + 0.275), rot, ST, n=10, r2=1.26, bevel=0.0)
    mb.cyl(1.26, 4.9, F.p(0, 0, z0 + 0.55 + 2.45), rot, ST, n=10, r2=0.84, bevel=0.0)
    mb.cyl(0.98, 0.75, F.p(0, 0, z0 + 5.45 + 0.37), rot, ST, n=10, r2=0.62, bevel=0.0)
    mb.cyl(0.74, 1.9, F.p(0, -0.12, z0 + 6.75), F.r(0.2), ST, n=8, r2=0.1, bevel=0.0)
    mb.box((0.6, 0.3, 0.76), F.p(0, 0.4, z0 + 6.45), F.r(), OBS, 0.0)
    # bracos (mangas) descendo para o cabo; maos
    for s in (-1, 1):
        mb.beam(F.p(s * 0.95, 0.05, z0 + 5.2), F.p(s * 0.28, 1.35, z0 + 3.85), 0.5, 0.55, ST, 0.0)
        mb.box((0.34, 0.4, 0.36), F.p(s * 0.17, 1.42, z0 + 3.72), F.r(), ST, 0.0)
    # lamina fincada a frente (ponta para baixo), guarda e cabo negros, pomo de prata
    mb.box((0.5, 0.14, 3.1), F.p(0, 1.5, z0 + 1.6), F.r(), SILVER, 0.0)
    mb.box((1.6, 0.3, 0.26), F.p(0, 1.5, z0 + 3.28), F.r(), OBS, 0.0)
    mb.box((0.24, 0.24, 0.75), F.p(0, 1.5, z0 + 3.78), F.r(), OBS, 0.0)
    mb.ico(0.2, tuple(F.p(0, 1.5, z0 + 4.26)), SILVER, 1)
    col_box("SG_PropStatue", (3.6, 3.6, 11.0), (x, y, z + 5.5), (0, 0, yaw))


GLYPHS = (0.25, 0.75, 0.5, 0.75, 0.25, 0.5)        # a "inscricao": a mesma sequencia nas 4 faces (nada aleatorio)


def obelisk(mb, x, y, z, face_yaw):
    hw0, hw1, zs0, zs1 = 0.95, 0.6, z + 1.9, z + 14.2
    mb.box((3.6, 3.6, 0.55), (x, y, z + 0.225), (0, 0, 0), OBS, 0.1)
    mb.box((2.8, 2.8, 1.0), (x, y, z + 1.0), (0, 0, 0), VIO, 0.08)
    mb.box((3.0, 3.0, 0.25), (x, y, z + 1.6), (0, 0, 0), TRIM, 0.06)
    mb.box((2.3, 2.3, 0.2), (x, y, z + 1.8), (0, 0, 0), OBS, 0.0)
    mb.cyl(hw0 * math.sqrt(2), zs1 - zs0, (x, y, (zs0 + zs1) / 2), (0, 0, math.pi / 4), OBS, n=4,
           r2=hw1 * math.sqrt(2), bevel=0.0)
    SL.spire(mb, (x, y), hw1 * math.sqrt(2) + 0.05, zs1, 1.7, SILVER, n=4)

    def hw(zz):
        return hw0 + (hw1 - hw0) * (zz - zs0) / (zs1 - zs0)
    for k in range(4):
        a = k * math.pi / 2
        nx, ny = math.cos(a), math.sin(a)
        tx, ty = -ny, nx
        front = abs(((a - face_yaw + math.pi) % (2 * math.pi)) - math.pi) < 0.1
        zg0 = z + 6.4 if front else z + 4.2
        for i, cb in enumerate(GLYPHS if not front else GLYPHS[:4]):
            zc = zg0 + i * 1.55
            off = hw(zc) + 0.02
            p = (x + nx * off, y + ny * off)
            mb.box((0.1, 0.16, 0.95), (p[0], p[1], zc), (0, 0, a), RUNE, 0.0)
            side = 1 if i % 2 == 0 else -1
            mb.box((0.1, 0.46, 0.13), (p[0] + tx * side * 0.2, p[1] + ty * side * 0.2, zc - 0.475 + cb * 0.95),
                   (side * 0.6, 0, a), RUNE, 0.0)
        if front:
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
    # arco de ferro no pe da escada do portao (entrada do recinto do castelo): lanternas violeta (so Neon)
    ma = MB("SG_Prop_GateArch", COLL, random.Random(3604), detail="near")
    x, y, zz, hs = GATE_ARCH
    iron_arch(ma, x, y, zz, hs, RUNE)
    ma.finish()


def build():
    axis_south()
    axis_north()
    court()
