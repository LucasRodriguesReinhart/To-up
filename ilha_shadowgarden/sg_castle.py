# sg_castle - CASTELO da Ilha 3 (Shadow Garden): o heroi da ilha, a SEDE da ordem. Substitui sg_blockout.castle.
#   muralha sobre a borda sul do P3 (ameias, mata-caes) + portao central (vao 16 x 18) entre 2 torres com VERGA BAIXA
#   (da praca o olho passa por cima dela e acha o emblema) + passagem leste aberta ate o ceu com 2 torrinhas + cortina
#   oeste ate a ala oeste + escadas Gate/EastP3; nave = CASCA do Mining Hall (face interna = retangulo do salao,
#   parede 4, teto opaco e colidivel em HALL_CEIL), porta com arquivoltas ogivais alternando pedra violeta/obsidiana e
#   medalhao da ordem no timpano; janelas altas (vidro frio de luar, o mesmo do hall); EMBLEMA MONUMENTAL da ordem
#   (sg_emblem) no lugar da antiga rosacea: medalhao de obsidiana com contorno de energia, campo de pedra violeta e
#   grande arco ogival de prata que abraca o porche; clerestorio com lancetas de energia violeta, telhado preto-violeta
#   com cumeeira/rincoes de prata, naves laterais, contrafortes com pinaculos e arcobotantes; 2 torres da fachada com
#   varanda de mata-caes; TORRE-COROA heroi com linhas de energia nas arestas, lancetas violeta e pontas de energia;
#   alas NAO entraveis (oeste sobre o terreno bravo, leste no beco junto a nave), janelas quentes (vida humana);
#   6 estandartes da ordem (sg_emblem.banner, debrum DOURADO) em ritmo simetrico: torres do portao, torres da fachada
#   e fachada da nave ladeando o JANELAO.
# REFINAMENTO v2 (refs/v2, 2026-09-28) - catedral de agulhas:
#   1. JANELAO ogival violeta aceso (14 de largura, SG_VioletDeep_Glow, maineis de obsidiana) na fachada entre a verga
#      da porta e o emblema monumental (que subiu para Z+56); a "boca de luz" da referencia. Wimperg rebaixado.
#   2. coroa mais alta e densa: fileira nova de pinaculos na cornija do 1o corpo da torre-coroa, agulhas secundarias
#      mais altas com alturas alternadas e pontas violeta-neon, agulhas de torres/torrinhas com gabarito maior,
#      lucarnas quentes nos telhados das naves laterais (CROWN_SPIRE_TOP 214 continua o maximo).
#   3. fileiras ritmicas de janelas quentes (Window_Warm) nos corpos ACIMA do teto do salao, nas alas e nas torres
#      (as altas continuam violeta). Ritmo por vao/face, nunca aleatorio.
#   4. lanternas da ordem (sg_emblem): lantern_pedestal nos parapeitos da muralha a cada ~12 (so Neon, sem luz real)
#      e lantern_post 2x no patamar do portao.
#   5. terracos com vida: ameias de obsidiana nas varandas + pinheiros pequenos em floreiras de obsidiana.
#   Camadas de material: BASE (soco de obsidiana + cordao de prata) / CORPO (pedra do castelo, faixas de obsidiana nos
#   andares, molduras violeta) / COROAMENTO (mata-caes de obsidiana, remate violeta, agulhas preto-violeta com aneis e
#   remates de prata). Nenhum simbolo alem do emblema da ordem.
#   Dentro do salao: SO a casca (pele de pedra de interior, teto, nervuras do teto). O acabamento e do agente HALL.
# Colisao propria: paredes da nave com o vao da porta, teto, contrafortes, porche, torres, muralha (vaos do portao e
# da passagem leste), cortina, alas. Nada colidivel dentro de MINE_RECT entre piso+0,3 e piso+12.
import math, random
import sg_lib as SL
import fm_lib
from sg_lib import MB, col_box, col_box2, light, ngon_col, box_walls_col
import sg_layout as L
import fm_parts as FP

# ------------------------------------------------------------------ materiais novos (2 de 9)
fm_lib.MATS.setdefault("Stone_SGCasInterior", (fm_lib.S(104, 104, 120), 0.8, 0.0, 0, None, 0.08))  # pele interna
# vidro frio de luar: MESMOS valores do sg_hall (dentro e fora casam)
fm_lib.MATS.setdefault("Glass_SGHallMoon", (fm_lib.S(96, 124, 186), 0.4, 0.0, 0.4, fm_lib.S(110, 145, 220), 0.0))
import sg_emblem as EM

# REFINAMENTO 2026-09-28: paleta com FUNCAO (sg_lib.SMATS) - base/soco/faixas = obsidiana, corpo = Stone_SG_Castle,
# molduras nobres = pedra violeta, remates = prata, ferragens = ferro negro, energia (so linhas e focos) = neon violeta
OB = "Stone_SG_Obsidian"
VI = "Stone_SG_Violet"
SV = "Metal_SG_Silver"
BI = "Metal_SG_BlackIron"
# overhaul 15 (hierarquia pedida: dungeon > alquimia > summon > MAGIA DO CASTELO > ambiente): o janelao da fachada e as
# lancetas/seteiras da torre-coroa eram o maior Neon da ilha (~2.000 studs2 de violeta forte, acima do summon); agora
# violeta SUAVE (Neon escuro). O foco medio do castelo fica so no crescente do emblema monumental (VG_EMB).
VG = "SG_VioletSoft_Glow"
VG_EMB = "SG_VioletDeep_Glow"
RG = "SG_Rune_Glow"
WW_M = "Window_Warm"
# passe de ACABAMENTO (2026-09-29): brilho magico do castelo BAIXO. Linhas/remates secundarios em violeta SUAVE (Neon
# escuro); violeta forte (VG) so onde tem funcao: o janelao da fachada e a torre-coroa. Janelas comuns = luz QUENTE.
VS = "SG_VioletSoft_Glow"
WD = "Wood_SG_Dark"
# luz do comodo atras do vidro (o mesmo material das janelas da vila: Neon MEDIO quente, so dentro da moldura)
ROOM = "SG_VilRoom_Glow"
fm_lib.MATS.setdefault(ROOM, (fm_lib.S(178, 96, 40), 0.5, 0.0, 1.25, fm_lib.S(178, 96, 40), 0.0))
CM_ = "Stone_SG_Castle"

Z = L.P3
Z2 = L.P2
ZB = Z - 0.4                        # base das paredes (afunda no piso)
ZT = 33.0                           # base do que nasce no terreno bravo (acima da caixa da dungeon, z 32)
CEIL = L.HALL_CEIL                  # 80,2
HX0, HY0, HX1, HY1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
TW = L.HALL_WALL
OX0, OY0, OX1, OY1 = HX0 - TW, HY0 - TW, HX1 + TW, HY1 + TW     # -51,5, 40,5, 51,5, 146,5 (face externa)
# SETOR 04b (salao maior, 2026-09-29): a casca cresce junto com o salao (96 x 99 x 44): nave 3 mais larga de cada
# lado (parede 3,5), 11 mais comprida para o norte e 20 mais alta; o corpo central da fachada (porta, arco do emblema,
# janelao) fica com a mesma largura. Atras, a torre-coroa desce ate o piso com a ABSIDE do trono na base.
EAVE = CEIL + 8.0                   # 108,2 cornija das naves laterais
CLR = 22.0                          # meia largura do corpo central (clerestorio / fachada central)
CLR_TOP = CEIL + 32.0               # 132,2 beiral do telhado da nave
NAVE_RISE = 30.0                    # cumeeira ~150, de quatro aguas na frente (a coroa aparece da praca)
AISLE_HI = EAVE + 12.8              # 121,0 topo do telhado de meia-agua das naves laterais (encosta no clerestorio)
# ritmo da nave casado com o interior (sg_hall): 4 janelas por lado no eixo dos vitrais, contrafortes nas pilastras
WIN_Y = [HY0 + 16.0 + k * (HY1 - HY0 - 32.0) / 3.0 for k in range(4)]                 # 60, 82,33, 104,67, 127
_DY = WIN_Y[1] - WIN_Y[0]
BUTT_Y = [WIN_Y[0] - _DY / 2] + [(a + b) / 2 for a, b in zip(WIN_Y, WIN_Y[1:])] + [WIN_Y[-1] + _DY / 2]  # 48,8..138,2
# saliencia do contraforte por lado: a oeste corre o BECO (borda do P3 em x ~ -57): contraforte RASO (lesena em talude)
# para o beco continuar com >= 3,5 livres; a leste (patio da dungeon / ala leste) o contraforte cheio
BUTT_P = {-1: 1.3, 1: 3.4}
WIN_A, WIN_RISE = 3.0, 3.9          # meia largura / flecha do arco (vao 6 x 21,3, igual ao vitral interno)
WIN_SILL = Z + 17.6                 # 69,8 (acima de piso+14; o peitoril interno e a galeria alta do salao)
WIN_SPRING = Z + 35.0               # 87,2 -> apice 91,1 (abaixo do teto em 100,2)
DW, DH = L.HALL_DOOR_W, L.HALL_DOOR_H
APSE_RISE = L.APSE_KEY - L.APSE_SPRING   # flecha do arco triunfal / abobada do presbiterio (04b)
ARCH_RISE = 9.5                     # flecha das arquivoltas do portal (nascem na verga, 70,2)
SOC = Z + 2.6                       # topo do soco de obsidiana (cordao de prata logo acima)
# emblema monumental da fachada (centro piso+58, acima do janelao, abaixo da empena) e o arco de prata que o emoldura
# (04b: a fachada subiu 20 com a nave: emblema, arco e janelao sobem junto, o janelao fica mais alto)
EMB_Z, EMB_R = Z + 76.0, 9.5
ARC_A, ARC_ZR, ARC_RISE = 15.0, Z + 32.0, 58.0
# JANELAO da fachada (refs/v2): boca de luz violeta entre a verga da porta (70,2) e o emblema (base ~103,5)
JAN_A, JAN_SILL, JAN_SPRING, JAN_RISE = 7.0, Z + 30.0, Z + 54.0, 4.6      # 82,2 / 106,2 / apice 110,8
JAN_TR = Z + 42.0                   # travessa do rendilhado do janelao
GAB_W, GAB_TOP = 13.0, CLR_TOP + 18.0
FT_SPIRE = 36.0                     # agulha das torres da fachada (abaixo da flecha da coroa)
WALL_TOP = Z + 12.0                 # 64,2 passeio da muralha
GATE_R = min(7.0, (L.GATEHOUSE_TOWERS[1][0] - L.GATEHOUSE_W / 2 - 0.06) / math.cos(math.pi / 8))   # face plana 0,06 atras do vao
EG_X, EG_W = L.EAST_WALL_GAP
EG_R = 3.6
EG_AP = EG_R * math.cos(math.pi / 8)
EG_TURRETS = [(EG_X - EG_W / 2 - EG_AP - 0.06, -6.2), (EG_X + EG_W / 2 + EG_AP + 0.06, -6.2)]
SW_TOWER = (L.WALL_X[0] - 0.5, -6.2, 6.5)
CR_X, CR_Y, CR_R, CR_TOP = L.CROWN_TOWER
BACK_TURRETS = [(-47.0, 149.0, 4.5), (47.0, 149.0, 4.5)]     # quinas de tras (a oeste deixam o beco passar)
FAC_TURRETS = [(-CLR, 38.4, 3.2), (CLR, 38.4, 3.2)]
# alas (nao entraveis): oeste sobre o terreno bravo, leste no beco entre a nave e o patio da dungeon
WW = (-94.0, 65.0, -62.0, 133.0)    # x0, y0, x1, y1 corpo da ala oeste
WW_EAVE = 86.2
EW = (OX1 + 3.4, 50.0, 60.5, 143.0)  # ala leste (encosta nos contrafortes)
EW_EAVE = Z + 12.0
WING_TOWERS = [(-95.0, 65.0, 6.5, 112.0, 26.0), (-95.0, 133.0, 6.0, 102.0, 20.0), (-66.0, 138.0, 6.5, 114.0, 24.0),
               (59.0, 151.0, 6.0, 108.0, 22.0)]
WALL_TOWERS = [(-46.0, -6.0, 4.6), (62.0, -6.0, 4.6)]      # torres intermediarias da muralha (sul da face: y -10,3)
CURTAIN_TOWER = (-82.0, 16.0, 5.5)                          # torre da cortina oeste

WARM = (1.0, 0.72, 0.45)
VIOLET = (0.62, 0.45, 1.0)

P1, P2, P3 = L.P1, L.P2, L.P3
CAMS = {
    "CAM_SGCas_FrontHigh": ((0.0, -230.0, 150.0), (0.0, 70.0, 112.0), 24),
    "CAM_SGCas_West": ((-300.0, 60.0, 150.0), (0.0, 80.0, 105.0), 24),
    "CAM_SGCas_East": ((300.0, 30.0, 150.0), (0.0, 80.0, 105.0), 24),
    "CAM_SGCas_BackNE": ((210.0, 360.0, 190.0), (0.0, 95.0, 110.0), 24),
    "CAM_SGCas_PlayerHeight_Plaza": ((6.0, -150.0, P1 + 5.2), (0.0, 60.0, P3 + 62.0), 22),
    "CAM_SGCas_PlayerHeight_Gate": ((-8.0, -52.0, P2 + 5.2), (0.0, -6.0, P3 + 16.0), 22),
    "CAM_SGCas_PlayerHeight_Forecourt": ((-30.0, 6.0, P3 + 5.2), (6.0, 60.0, P3 + 36.0), 20),
    "CAM_SGCas_PlayerHeight_WestAlley": ((-55.5, 58.0, P3 + 5.2), (-52.0, 140.0, P3 + 18.0), 20),
    "CAM_SGCas_PlayerHeight_DungeonYard": ((96.0, 36.0, P3 + 5.2), (40.0, 110.0, P3 + 40.0), 20),
    "CAM_SGCas_PlayerHeight_Terrace": ((-40.0, 172.0, P3 + 5.2), (0.0, 140.0, P3 + 66.0), 20),
    "CAM_SGCas_PlayerHeight_EastGap": ((112.0, -46.0, P2 + 5.2), (112.0, -4.0, P3 + 10.0), 22),
    # OVERHAUL 03 (2026-09-29): closes na ALTURA DO JOGADOR (olho a 5,2), angulos naturais de quem anda por ali
    "CAM_SGCas_OV_WallBase": ((-16.5, -21.0, P2 + 5.2), (-32.0, -9.3, P2 + 7.5), 22),
    "CAM_SGCas_OV_WallTop": ((-17.0, -19.0, P2 + 5.2), (-30.0, -9.3, P3 + 12.0), 22),
    "CAM_SGCas_OV_GateIn": ((5.0, 10.0, P3 + 5.2), (0.0, -6.0, P3 + 13.0), 22),
    "CAM_SGCas_OV_Buttress": ((-55.8, 60.0, P3 + 5.2), (-51.5, 71.2, P3 + 7.0), 20),
    "CAM_SGCas_OV_Flyer": ((96.0, 42.0, P3 + 5.2), (40.0, 67.3, P3 + 44.0), 24),
    "CAM_SGCas_OV_NaveWindow": ((-56.0, 92.0, P3 + 5.2), (-51.5, 104.7, P3 + 22.0), 22),
    "CAM_SGCas_OV_Pinnacle": ((-5.0, 25.0, P3 + 5.2), (-13.0, 36.5, P3 + 24.0), 22),
    "CAM_SGCas_OV_Corner": ((-36.0, 25.0, P3 + 5.2), (-49.0, 40.0, P3 + 9.0), 20),
    "CAM_SGCas_OV_RoofSeam": ((76.0, 42.0, P3 + 5.2), (56.0, 62.0, P3 + 13.0), 20),
    "CAM_SGCas_OV_Porch": ((-9.0, 28.0, P3 + 5.2), (-8.0, 38.0, P3 + 12.0), 22),
    "CAM_SGCas_OV_Rail": ((-30.0, 160.0, P3 + 5.2), (-14.0, 142.0, P3 + 6.0), 20),
    "CAM_SGCas_OV_TreePit": ((-30.0, -108.0, P1 + 5.2), (-40.0, -98.0, P1 + 2.0), 22),
    "CAM_SGCas_OV_GateArch": ((-6.0, -44.0, P2 + 5.2), (0.0, -28.0, P2 + 9.0), 22),
    "CAM_SGCas_OV_Parterre": ((-8.0, 1.0, P3 + 5.2), (-22.0, 12.0, P3 + 1.5), 22),
}

# rota extra: patio -> contorno da torre oeste da fachada -> beco oeste -> terraco norte (atras da coroa)
EXTRA_ROUTES = {
    # 04b: a nave cresceu (face externa oeste em x -51,5, contrafortes rasos do lado do beco): o beco segue colado
    # na borda do P3 e desemboca no terraco norte, a oeste da torre-coroa (que desceu para y 158)
    "PATIO->BECO_OESTE->TERRACO": ([(0.0, 20.0), (-40.0, 24.0), (-60.0, 28.0), (-70.0, 36.0), (-69.5, 44.0),
                                    (-66.5, 49.6), (-61.0, 56.0), (-56.5, 62.0), (-55.5, 100.0), (-55.4, 140.0), (-54.8, 150.0), (-52.0, 158.0),
                                    (-40.0, 165.0), (-26.0, 171.0)], P3),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ geometria base
def _fin(mb):
    """finish + limpeza das lascas de area nula que o tubo fechado do sg_emblem (congelado) deixa na emenda do anel"""
    import bmesh
    ob = mb.finish()
    if ob is None:
        return ob
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bad = [f for f in bm.faces if f.calc_area() < 1e-5]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES_ONLY")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        bm.to_mesh(ob.data)
        ob.data.update()
    bm.free()
    return ob


def _P(W, u, t, z):
    (ox, oy), (ux, uy), (nx, ny) = W
    return (ox + ux * u + nx * t, oy + uy * u + ny * t, z)


def _dedupe(poly):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > 1e-4 or abs(p[1] - out[-1][1]) > 1e-4:
            out.append(p)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) < 1e-4 and abs(out[0][1] - out[-1][1]) < 1e-4:
        out.pop()
    return out


def panel(mb, W, poly, t0, t1, m, inner_m=None):
    """prisma de um poligono no plano (u, z) da parede W, de t0 a t1 (t = normal). inner_m: material da face t0"""
    poly = _dedupe(poly)
    bm = mb.bm
    a = [bm.verts.new(_P(W, u, t0, z)) for u, z in poly]
    b = [bm.verts.new(_P(W, u, t1, z)) for u, z in poly]
    n = len(poly)
    fa = bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)
    if inner_m:
        fa.material_index = mb._mi_for(inner_m)


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


def ogive(uc, a, zr, rise, d=0.0, n=6):
    """arco ogival (2 arcos) de (uc-a-d, zr) pelo apice ate (uc+a+d, zr); d = afastamento (moldura)"""
    rise = max(rise, a)
    c = (rise * rise - a * a) / (2.0 * a)
    R = a + c + d
    th1 = math.acos(max(-1.0, min(1.0, -c / R)))
    left = [(uc + c + R * math.cos(th), zr + R * math.sin(th)) for th in
            [math.pi + (th1 - math.pi) * k / n for k in range(n + 1)]]
    left[-1] = (uc, left[-1][1])
    right = [(2 * uc - u, z) for (u, z) in reversed(left[:-1])]
    return left + right


def wall_run(mb, W, u0, u1, zb, zt, t0, t1, opens, m, inner_m=None):
    """parede de u0 a u1 com vaos ogivais: opens = [(uc, a, peitoril, nascenca, flecha)]"""
    cur = u0
    for uc, a, zs, zr, rise in sorted(opens):
        l, r = uc - a, uc + a
        if l - cur > 0.01:
            panel(mb, W, rect(cur, l, zb, zt), t0, t1, m, inner_m)
        if zs - zb > 0.01:
            panel(mb, W, rect(l, r, zb, zs), t0, t1, m, inner_m)
        panel(mb, W, [(r, zt), (l, zt)] + ogive(uc, a, zr, rise), t0, t1, m, inner_m)
        cur = r
    if u1 - cur > 0.01:
        panel(mb, W, rect(cur, u1, zb, zt), t0, t1, m, inner_m)


def window(mb, W, uc, a, zs, zr, rise, t_glass, t_out, glass_m="Glass_SGHallMoon", frame_m=VI, fw=0.8,
           dp=0.45, mullion=True, sill=True, sill_m=OB, lead=True, hood=False, back_m=None):
    """vidro ogival no meio da parede + moldura (ombreiras + arquivolta numa peca so) + mainel + peitoril.
    Acabamento: chumbo de ferro negro sobre o vidro (le VIDRO, nao plano de luz), pingadeira (hood) opcional;
    glass_m='shutter' -> folhas de madeira fechadas com ferragens (quarto sem luz: nunca um retangulo escuro)."""
    arc = ogive(uc, a, zr, rise)
    shut = glass_m == "shutter"
    if glass_m == WW_M:
        # overhaul 03: LUZ INTERIOR - os 3/5 de baixo sao o comodo aceso (Neon medio quente, um pouco mais fundo) e o
        # resto e vidro ambar sem brilho (a mesma leitura das janelas da vila); nunca a janela inteira em luz
        zl = zs + (zr - zs) * 0.62
        panel(mb, W, rect(uc - a, uc + a, zs, zl), t_glass - 0.14, t_glass + 0.02, ROOM)
        panel(mb, W, [(uc - a, zl), (uc + a, zl)] + list(reversed(arc)), t_glass - 0.08, t_glass + 0.08, WW_M)
        if back_m:
            # overhaul 15 (pendencia do salao): nas paredes da nave o lado de DENTRO desta janela e o vitral de luar
            # do Mining Hall (Glass 0,3 no Roblox): sem fundo, o Neon quente do comodo aparecia atras do vitral.
            # Fundo opaco escuro atras do comodo aceso e do vidro ambar (invisivel por fora).
            panel(mb, W, [(uc - a, zs), (uc + a, zs)] + list(reversed(arc)), t_glass - 0.3, t_glass - 0.16, back_m)
    else:
        panel(mb, W, [(uc - a, zs), (uc + a, zs)] + list(reversed(arc)), t_glass - 0.08, t_glass + 0.08,
              WD if shut else glass_m)
    tf = t_glass + 0.08
    if shut:
        panel(mb, W, rect(uc - 0.05, uc + 0.05, zs, zr + rise * 0.55), tf, tf + 0.08, BI)
        for zz in (zs + (zr - zs) * 0.22, zs + (zr - zs) * 0.8):
            panel(mb, W, rect(uc - a, uc + a, zz - 0.1, zz + 0.1), tf, tf + 0.09, BI)
    elif lead:
        step = 1.7 if a > 1.5 else 1.3
        nz = int((zr - zs - 0.4) / step)
        for k in range(1, nz + 1):
            zz = zs + (zr - zs) * k / (nz + 1)
            panel(mb, W, rect(uc - a, uc + a, zz - 0.06, zz + 0.06), tf, tf + 0.08, BI)
        if not mullion:
            panel(mb, W, rect(uc - 0.06, uc + 0.06, zs, zr + rise * 0.6), tf, tf + 0.08, BI)
    if hood and frame_m:
        h0 = ogive(uc, a, zr, rise, d=fw)
        h1 = ogive(uc, a, zr, rise, d=fw + 0.42)
        panel(mb, W, h0 + list(reversed(h1)), t_out + dp - 0.2, t_out + dp + 0.22, OB)
        for s in (-1, 1):
            u0_, u1_ = sorted((s * (a + fw - 0.05), s * (a + fw + 0.62)))
            panel(mb, W, rect(uc + u0_, uc + u1_, zr - 0.9, zr + 0.02), t_out + dp - 0.2, t_out + dp + 0.26, OB)
    if mullion:
        panel(mb, W, rect(uc - 0.22, uc + 0.22, zs, zr + rise * 0.45), t_glass - 0.3, t_glass + 0.3, frame_m)
        panel(mb, W, rect(uc - a, uc + a, zr - 0.2, zr + 0.2), t_glass - 0.3, t_glass + 0.3, frame_m)
    if frame_m:
        outer = ogive(uc, a, zr, rise, d=fw)
        band = [(uc - a, zs), (uc - a, zr)] + arc[1:-1] + [(uc + a, zr), (uc + a, zs), (uc + a + fw, zs),
                                                         (uc + a + fw, zr)] + list(reversed(outer))[1:-1] + \
               [(uc - a - fw, zr), (uc - a - fw, zs)]
        panel(mb, W, band, t_out - 0.05, t_out + dp, frame_m)
    if sill:
        panel(mb, W, rect(uc - a - fw - 0.3, uc + a + fw + 0.3, zs - 0.55, zs), t_out - 0.05, t_out + dp + 0.35, sill_m)


def ngon_pts(cx, cy, r, n, rot0=None):
    rot0 = 180.0 / n if rot0 is None else rot0
    return [(cx + r * math.cos(math.radians(rot0 + 360.0 * k / n)), cy + r * math.sin(math.radians(rot0 + 360.0 * k / n)))
            for k in range(n)]


def frustum(mb, cx, cy, r0, r1, n, z0, z1, m, rot0=None, top=True):
    bm = mb.bm
    a = [bm.verts.new((x, y, z0)) for x, y in ngon_pts(cx, cy, r0, n, rot0)]
    b = [bm.verts.new((x, y, z1)) for x, y in ngon_pts(cx, cy, r1, n, rot0)]
    bm.faces.new(list(reversed(a)))
    if top:
        bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def rect_frustum(mb, x0, y0, x1, y1, z0, z1, e0, e1, m):
    """bloco retangular com talude (base alargada e0, topo e1)"""
    bm = mb.bm
    a = [bm.verts.new(p) for p in ((x0 - e0, y0 - e0, z0), (x1 + e0, y0 - e0, z0), (x1 + e0, y1 + e0, z0),
                                   (x0 - e0, y1 + e0, z0))]
    b = [bm.verts.new(p) for p in ((x0 - e1, y0 - e1, z1), (x1 + e1, y0 - e1, z1), (x1 + e1, y1 + e1, z1),
                                   (x0 - e1, y1 + e1, z1))]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def shaft(mb, cx, cy, r, n, z0, z1, m, rot0=None):
    mb.prism(ngon_pts(cx, cy, r, n, rot0), z0, z1, m)


def spire(mb, cx, cy, r, n, z0, h, m, rot0=None, flare=0.1, rings=(0.36,), ring_m=SV):
    """agulha gotica: beiral levemente alargado + cone ingreme; aneis de prata no beiral e ao longo do cone"""
    bm = mb.bm
    e = [bm.verts.new((x, y, z0)) for x, y in ngon_pts(cx, cy, r * (1.0 + flare), n, rot0)]
    k = [bm.verts.new((x, y, z0 + h * 0.08)) for x, y in ngon_pts(cx, cy, r * 0.9, n, rot0)]
    top = bm.verts.new((cx, cy, z0 + h))
    bm.faces.new(list(reversed(e)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((e[i], e[j], k[j], k[i]))
        bm.faces.new((k[i], k[j], top))
    mb._post(e + k + [top], m, None, 0, 1)
    if ring_m and r > 1.6:
        rr = r * (1.0 + flare)
        frustum(mb, cx, cy, rr + 0.12, rr + 0.12, n, z0 - 0.35, z0 + 0.05, ring_m, rot0)
        def rad(z):
            return r * 0.9 * (1.0 - ((z - z0) / h - 0.08) / 0.92)
        for f in rings:
            zf = z0 + h * f
            dz = 0.28 if h < 20 else 0.4
            frustum(mb, cx, cy, rad(zf - dz) + 0.16, rad(zf + dz) + 0.16, n, zf - dz, zf + dz, ring_m, rot0)


def ring(mb, C, U, V, N, r0, r1, t0, t1, m, n=24, a0=0.0):
    """anel (coroa circular) no plano (U, V) com espessura ao longo de N: rosacea, aneis de tracaria"""
    bm = mb.bm

    def p(r, ang, t):
        return tuple(C[i] + U[i] * r * math.cos(ang) + V[i] * r * math.sin(ang) + N[i] * t for i in range(3))
    angs = [a0 + 2 * math.pi * k / n for k in range(n)]
    fi = [bm.verts.new(p(r0, a, t0)) for a in angs]
    fo = [bm.verts.new(p(r1, a, t0)) for a in angs]
    bi = [bm.verts.new(p(r0, a, t1)) for a in angs]
    bo = [bm.verts.new(p(r1, a, t1)) for a in angs]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((fi[i], fo[i], fo[j], fi[j]))
        bm.faces.new((bi[j], bo[j], bo[i], bi[i]))
        bm.faces.new((fo[i], bo[i], bo[j], fo[j]))
        bm.faces.new((fi[j], bi[j], bi[i], fi[i]))
    mb._post(fi + fo + bi + bo, m, None, 0, 1)


def disc(mb, C, U, V, N, r, t0, t1, m, n=24):
    bm = mb.bm

    def p(ang, t):
        return tuple(C[i] + U[i] * r * math.cos(ang) + V[i] * r * math.sin(ang) + N[i] * t for i in range(3))
    angs = [2 * math.pi * k / n for k in range(n)]
    f = [bm.verts.new(p(a, t0)) for a in angs]
    b = [bm.verts.new(p(a, t1)) for a in angs]
    bm.faces.new(f)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((f[j], f[i], b[i], b[j]))
    mb._post(f + b, m, None, 0, 1)


def hip_roof(mb, x0, y0, x1, y1, z0, h, m, ridge_frac=0.5):
    """telhado de quatro aguas (cumeeira ao longo do lado maior)"""
    bm = mb.bm
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    base = [bm.verts.new(p) for p in ((x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))]
    if (x1 - x0) >= (y1 - y0):
        hw = (x1 - x0) / 2 * ridge_frac
        r = [bm.verts.new((cx - hw, cy, z0 + h)), bm.verts.new((cx + hw, cy, z0 + h))]
        fs = [(base[0], base[1], r[1], r[0]), (base[1], base[2], r[1]), (base[2], base[3], r[0], r[1]),
              (base[3], base[0], r[0])]
    else:
        hw = (y1 - y0) / 2 * ridge_frac
        r = [bm.verts.new((cx, cy - hw, z0 + h)), bm.verts.new((cx, cy + hw, z0 + h))]
        fs = [(base[0], base[1], r[0]), (base[1], base[2], r[1], r[0]), (base[2], base[3], r[1]),
              (base[3], base[0], r[0], r[1])]
    bm.faces.new(list(reversed(base)))
    for f in fs:
        bm.faces.new(f)
    mb._post(base + r, m, None, 0, 1)


def face_frame(cx, cy, ap, phi_deg):
    """referencial de parede na face de um poligono (centro da face, u tangente, t para fora)"""
    ph = math.radians(phi_deg)
    return ((cx + ap * math.cos(ph), cy + ap * math.sin(ph)), (-math.sin(ph), math.cos(ph)), (math.cos(ph), math.sin(ph)))


def louvers(mb, W, u0, u1, z0, z1, t, m=None):
    """venezianas de madeira (sotao / campanario / quarto fechado): fundo escuro no recuo + palhetas inclinadas"""
    m = m or WD
    panel(mb, W, rect(u0, u1, z0, z1), t - 0.1, t + 0.04, OB)
    n = max(2, int((z1 - z0) / 0.55))
    for k in range(n):
        zc = z0 + (k + 0.6) * (z1 - z0) / (n + 0.2)
        panel(mb, W, [(u0, zc - 0.16), (u1, zc - 0.16), (u1, zc + 0.12), (u0, zc + 0.12)], t + 0.04, t + 0.2, m)


def lancet_win(mb, W, uc, z0, h, w=1.0, t=0.0, glass=WW_M, frame_m=OB, dp=0.42, fw=0.26, bar=True, sill=True):
    """JANELA pequena de verdade numa face plana (plano externo em t): VIDRO com a luz interior rente a face, MOLDURA
    saliente (ombreiras + arco ogival numa peca) que cria o RECUO, PEITORIL com pingadeira e travessa de ferro no vidro.
    glass='louver' -> venezianas de madeira no lugar do vidro (quarto fechado)"""
    a = w / 2
    rise = a * 1.4
    zr = z0 + h - rise
    arc = ogive(uc, a, zr, rise, n=3)
    if glass == "louver":
        louvers(mb, W, uc - a, uc + a, z0, zr, t)
        panel(mb, W, [(uc - a, zr), (uc + a, zr)] + list(reversed(arc))[1:-1], t - 0.1, t + 0.04, OB)
    elif glass == WW_M:
        zl = z0 + (zr - z0) * 0.6                     # overhaul 03: comodo aceso embaixo, vidro ambar em cima
        panel(mb, W, rect(uc - a, uc + a, z0, zl), t - 0.16, t - 0.02, ROOM)
        panel(mb, W, [(uc - a, zl), (uc + a, zl)] + list(reversed(arc)), t - 0.1, t + 0.04, WW_M)
    else:
        panel(mb, W, [(uc - a, z0), (uc + a, z0)] + list(reversed(arc)), t - 0.1, t + 0.04, glass)
    outer = ogive(uc, a, zr, rise, d=fw, n=3)
    band_ = [(uc - a, z0), (uc - a, zr)] + arc[1:-1] + [(uc + a, zr), (uc + a, z0), (uc + a + fw, z0),
                                                      (uc + a + fw, zr)] + list(reversed(outer))[1:-1] + \
            [(uc - a - fw, zr), (uc - a - fw, z0)]
    panel(mb, W, band_, t - 0.05, t + dp, frame_m)
    if sill:
        # peitoril com pingadeira: mais largo e mais saliente que a moldura
        panel(mb, W, rect(uc - a - fw - 0.18, uc + a + fw + 0.18, z0 - 0.34, z0 + 0.02), t - 0.05, t + dp + 0.22,
              frame_m)
    if bar and glass != "louver":
        zb = z0 + (zr - z0) * 0.55
        panel(mb, W, rect(uc - a, uc + a, zb - 0.07, zb + 0.07), t + 0.04, t + 0.12, BI)
        if w >= 1.3:
            panel(mb, W, rect(uc - 0.06, uc + 0.06, z0, zr + rise * 0.5), t + 0.04, t + 0.12, BI)


def slit(mb, W, z0, h, w=0.9, m="Window_Warm", pointed=True):
    """seteira/lanceta das torres: agora janela de verdade (moldura + recuo + vidro + peitoril), nao plano emissivo"""
    lancet_win(mb, W, 0.0, z0, h, w, 0.0, glass=m)


def wlancet(mb, W, uc, z0, h, w=1.0, t=0.0, m=WW_M):
    """lanceta ogival pequena e quente na face de uma parede cujo plano externo esta em t (ritmo de janelas da ref v2)"""
    lancet_win(mb, W, uc, z0, h, w, t, glass=m)


def socle(mb, x, y, r, n, z0, z1, rot, e=0.9):
    """soco de obsidiana (base alargada) + cordao de prata no topo: a BASE de tudo o que e castelo"""
    frustum(mb, x, y, r + e, r + 0.25, n, z0, z1, OB, rot)
    frustum(mb, x, y, r + 0.42, r + 0.42, n, z1 - 0.05, z1 + 0.4, SV, rot)


def band(mb, x, y, r, n, z, rot, m=OB, h=1.2, e=0.5):
    """faixa horizontal (marca de andar) em volta de um fuste. Overhaul 03: CORDAO com perfil - recorte por baixo
    (pingadeira), face e topo em talude (antes: anel de face reta, lia 'pneu')"""
    rr = 180.0 / n if rot is None else rot
    EM._lathe(mb, (x, y, z), [(r + 0.05, 0.0), (r + e, h * 0.28), (r + e, h * 0.7), (r + 0.1, h)], m, n,
              math.radians(rr), caps=(False, False))


# ------------------------------------------------------------------ OVERHAUL 03 (2026-09-29): kit de PROFUNDIDADE
# Camadas: PAREDE -> RECUO -> PILAR/TRIM -> JANELA -> MOLDURA -> VIDRO. No Roblox nao ha textura: a pedra tem de ler pela
# geometria. Ferramentas (todas no referencial de parede W = (origem, u, normal para fora)):
#   ledge   perfil (t, z) extrudado ao longo de u: soco em talude, cordao com pingadeira, cornija, capa chanfrada;
#   block   bloco de cantaria com as 4 arestas da face chanfradas (le "pedra lavrada" so pela luz);
#   ashlar  paramento em fiadas de 2 alturas com juntas desencontradas, recortado em volta dos vaos;
#   strip   casca de uma faixa entre 2 curvas no plano (u, z) (arcobotante, aduelas, mata-caes);
#   pinnacle PINACULO do kit (corpo de quinas chanfradas + gabletes, agulha OCTOGONAL com colar e 1 anel, crochés,
#           florao de prata) no lugar da caixa + piramide de 4 lados.
ASH = "Stone_SG_Block_B"            # silhar (tom FIXO um valor acima do corpo: as juntas chanfradas leem mais escuras)
CAPL = "Stone_SG_TrimLow"           # remate perto do jogador (um valor abaixo do Stone_SG_Trim: 14.01)
fm_lib.MATS.setdefault(CAPL, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
NAVY = "Roof_SG_Navy"
COURSES = (1.05, 0.78)              # as 2 alturas de fiada do castelo


def _faces_ok(mb, fs):
    import bmesh
    bmesh.ops.recalc_face_normals(mb.bm, faces=[f for f in fs if f is not None])


def ledge(mb, W, u0, u1, prof, m):
    """perfil [(t, z)] (poligono simples no plano t-z da parede W) extrudado de u0 a u1"""
    bm = mb.bm
    prof = _dedupe(prof)
    a = [bm.verts.new(_P(W, u0, t, z)) for t, z in prof]
    b = [bm.verts.new(_P(W, u1, t, z)) for t, z in prof]
    n = len(prof)
    fs = [bm.faces.new(a), bm.faces.new(list(reversed(b)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    _faces_ok(mb, fs)
    mb._post(a + b, m, None, 0, 1)


def block(mb, W, u0, u1, z0, z1, t0, t1, ch, m):
    """bloco de cantaria: face de tras (u0..u1, z0..z1) em t0, face da frente recuada 'ch' nas 4 arestas em t1"""
    bm = mb.bm
    ch = min(ch, (u1 - u0) * 0.3, (z1 - z0) * 0.3)
    back = [bm.verts.new(_P(W, u, t0, z)) for u, z in ((u0, z0), (u1, z0), (u1, z1), (u0, z1))]
    fr = [bm.verts.new(_P(W, u, t1, z)) for u, z in ((u0 + ch, z0 + ch), (u1 - ch, z0 + ch), (u1 - ch, z1 - ch),
                                                     (u0 + ch, z1 - ch))]
    fs = [bm.faces.new(back), bm.faces.new(list(reversed(fr)))]
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((back[i], fr[i], fr[j], back[j])))
    _faces_ok(mb, fs)
    mb._post(back + fr, m, None, 0, 1)


def _cut(rects, e0, e1, ez0, ez1):
    out = []
    for a, b, ra, rb in rects:
        if e1 <= a or e0 >= b or ez1 <= ra or ez0 >= rb:
            out.append((a, b, ra, rb))
            continue
        if e0 - a > 0.35:
            out.append((a, e0 - 0.06, ra, rb))
        if b - e1 > 0.35:
            out.append((e1 + 0.06, b, ra, rb))
        m0, m1 = max(a, e0 - 0.06), min(b, e1 + 0.06)
        if ez0 - ra > 0.3:
            out.append((m0, m1, ra, ez0 - 0.05))
        if rb - ez1 > 0.3:
            out.append((m0, m1, ez1 + 0.05, rb))
    return out


def ashlar(mb, W, u0, u1, z0, z1, t=0.0, excl=(), m=ASH, PL=3.1, dep=0.12, ch=0.07, phase=0.0, gap=0.08,
           hs=COURSES):
    """paramento de CANTARIA em relevo raso na face (plano externo em t): fiadas de 2 alturas escaladas para fechar
    z0..z1, blocos de ~PL com juntas desencontradas fiada a fiada; excl = [(u0, u1, z0, z1)] vaos (janela + moldura)"""
    if z1 - z0 < 0.5 or u1 - u0 < 0.5:
        return
    per = hs[0] + hs[1]
    npair = max(1, int(round((z1 - z0) / per)))
    sc = (z1 - z0) / (npair * per)
    zz, k = z0, 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        rects = [(u0, u1, zz + gap / 2, zz + h - gap / 2)]
        for e in excl:
            rects = _cut(rects, *e)
        off = phase + (k % 2) * PL * 0.5
        for a, b, ra, rb in rects:
            cuts = [a] + [u0 + off + PL * j for j in range(-1, int((u1 - u0) / PL) + 3)
                          if a + 0.7 < u0 + off + PL * j < b - 0.7] + [b]
            for c0, c1 in zip(cuts, cuts[1:]):
                p0 = c0 + (gap / 2 if c0 > a else 0.0)
                p1 = c1 - (gap / 2 if c1 < b else 0.0)
                if p1 - p0 > 0.2 and rb - ra > 0.2:
                    block(mb, W, p0, p1, ra, rb, t - 0.03, t + dep, ch, m)
        zz += h
        k += 1


def strip(mb, W, lo, hi, t0, t1, m):
    """casca fechada entre a curva de baixo 'lo' e a de cima 'hi' (listas [(u, z)] com o mesmo numero de pontos, par a
    par), de t0 a t1: arcobotante (intradorso curvo + extradorso reto), aduela, arquinho do mata-caes"""
    bm = mb.bm
    L0 = [(bm.verts.new(_P(W, u, t0, z)), bm.verts.new(_P(W, u, t1, z))) for u, z in lo]
    H0 = [(bm.verts.new(_P(W, u, t0, z)), bm.verts.new(_P(W, u, t1, z))) for u, z in hi]
    fs = []
    for i in range(len(lo) - 1):
        fs.append(bm.faces.new((L0[i][0], L0[i + 1][0], H0[i + 1][0], H0[i][0])))
        fs.append(bm.faces.new((L0[i][1], H0[i][1], H0[i + 1][1], L0[i + 1][1])))
        fs.append(bm.faces.new((L0[i][0], L0[i][1], L0[i + 1][1], L0[i + 1][0])))
        fs.append(bm.faces.new((H0[i][0], H0[i + 1][0], H0[i + 1][1], H0[i][1])))
    for k in (0, -1):
        fs.append(bm.faces.new((L0[k][0], H0[k][0], H0[k][1], L0[k][1])))
    _faces_ok(mb, fs)
    mb._post([v for p in L0 + H0 for v in p], m, None, 0, 1)


def sq_ch(x, y, hw, c, rot=0.0):
    """quadrado de meia-aresta hw com quinas chanfradas em c (octogono irregular anti-horario), girado de rot"""
    pts = [(-hw + c, -hw), (hw - c, -hw), (hw, -hw + c), (hw, hw - c), (hw - c, hw), (-hw + c, hw), (-hw, hw - c),
           (-hw, -hw + c)]
    ca, sa = math.cos(rot), math.sin(rot)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def finial(mb, x, y, z, s=1.0, m=SV):
    """FLORAO de prata (torno de 6): colar, bulbo, gola e ponta, assentado em z (os pequenos, longe do olho, com
    menos aneis)"""
    prof = [(0.17, 0.0), (0.24, 0.1), (0.14, 0.22), (0.3, 0.46), (0.22, 0.68), (0.09, 0.84), (0.13, 0.96),
            (0.0, 1.45)]
    if s < 1.2:
        prof = [(0.2, 0.0), (0.14, 0.2), (0.3, 0.46), (0.1, 0.82), (0.0, 1.45)]
    EM._lathe(mb, (x, y, z), [(r * s, h * s) for r, h in prof], m, 6, math.pi / 6)


def pinnacle(mb, x, y, z0, s=1.0, hb=3.0, hn=None, body_m=CM_, spire_m=NAVY, gab=True, crock=True, rot=0.0,
             ring_m=SV, cap_m=OB):
    """PINACULO do kit do castelo (substitui caixa + piramide de 4 lados, 03.10/12.12): corpo quadrado de quinas
    chanfradas (hb) com cornija de obsidiana e GABLETE nas 4 faces, agulha OCTOGONAL com colar, 1 anel de prata,
    4 crochés nas arestas e florao. s = escala (1 = grande, ~0,6 = pequeno). Devolve o topo."""
    hn = 5.6 * s if hn is None else hn
    hw = 1.0 * s
    zt = z0 + hb
    mb.prism(sq_ch(x, y, hw, 0.24 * s, rot), z0, zt, body_m)
    # cornija do corpo (sai 0,12 e volta em talude)
    rr = hw * 1.08
    frustum(mb, x, y, rr + 0.1 * s, rr - 0.05 * s, 8, zt - 0.04, zt + 0.22 * s, cap_m, math.degrees(rot) + 22.5)
    if gab:
        bm = mb.bm
        for k in range(4):
            a = rot + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            tx, ty = -sa, ca

            def P(u, t, zz):
                return (x + ca * t + tx * u, y + sa * t + ty * u, zz)
            gw, gh, g0, g1 = 0.72 * s, 1.35 * s, hw * 0.55, hw + 0.14 * s
            pts = ((-gw, zt), (gw, zt), (0.0, zt + gh))
            A = [bm.verts.new(P(u, g0, zz)) for u, zz in pts]
            B = [bm.verts.new(P(u, g1, zz)) for u, zz in pts]
            fs = [bm.faces.new(A), bm.faces.new(list(reversed(B)))]
            for i in range(3):
                j = (i + 1) % 3
                fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
            _faces_ok(mb, fs)
            mb._post(A + B, body_m, None, 0, 1)
    rn = 0.8 * s
    SL.spire(mb, (x, y), rn, zt + 0.2 * s, hn, spire_m, n=8)
    zr = zt + 0.2 * s + hn * 0.42
    rad = rn * (1.0 - 0.42) + 0.1 * s
    if ring_m:
        frustum(mb, x, y, rad + 0.06 * s, rad - 0.04 * s, 8, zr - 0.14 * s, zr + 0.14 * s, ring_m)
    if crock:
        bm = mb.bm
        zc = zt + 0.2 * s + hn * 0.66
        rc = rn * (1.0 - 0.66)
        for k in range(4):
            a = math.pi / 8 + k * math.pi / 2                       # arestas (vertices) da agulha de 8 lados
            ca, sa = math.cos(a), math.sin(a)
            tx, ty = -sa, ca
            base = [(x + ca * rc * 0.8 - tx * 0.14 * s, y + sa * rc * 0.8 - ty * 0.14 * s, zc - 0.3 * s),
                    (x + ca * rc * 0.8 + tx * 0.14 * s, y + sa * rc * 0.8 + ty * 0.14 * s, zc - 0.3 * s),
                    (x + ca * rc * 0.7, y + sa * rc * 0.7, zc + 0.25 * s)]
            tip = (x + ca * (rc + 0.42 * s), y + sa * (rc + 0.42 * s), zc + 0.18 * s)
            V = [bm.verts.new(p) for p in base] + [bm.verts.new(tip)]
            fs = [bm.faces.new((V[0], V[2], V[1])), bm.faces.new((V[0], V[1], V[3])),
                  bm.faces.new((V[1], V[2], V[3])), bm.faces.new((V[2], V[0], V[3]))]
            _faces_ok(mb, fs)
            mb._post(V, spire_m, None, 0, 1)
    top = zt + 0.2 * s + hn
    finial(mb, x, y, top - 0.45 * s, 0.9 * s)
    return top + 0.95 * s


def hidden_pt(x, y):
    """ponto (na frente de uma face) dentro de outra massa do castelo? (nave, alas, muralha): face que nao se ve"""
    if OX0 - 0.3 < x < OX1 + 0.3 and OY0 - 0.3 < y < OY1 + 0.3:
        return True
    for x0, y0, x1, y1 in (WW, EW):
        if x0 - 0.3 < x < x1 + 0.3 and y0 - 0.3 < y < y1 + 0.3:
            return True
    return L.WALL_X[0] - 0.5 < x < L.WALL_X[1] + 0.5 and L.WALL_Y0 - 1.2 < y < L.WALL_Y1 + 0.5


def tower_ashlar(mb, x, y, r, n, rot, z0, z1, phis=None, cord=True, zmin_fn=None):
    """silhar em fiadas nas faces VISIVEIS de um fuste poligonal (z0..z1) + cordao com pingadeira no topo.
    zmin_fn(face_center) -> cota minima do silhar naquela face (ex.: piso do patio do lado de dentro da muralha)"""
    ap = r * math.cos(math.pi / n)
    side = 2 * r * math.sin(math.pi / n)
    r0 = 180.0 / n if rot is None else rot
    for k in range(n):
        phi = (r0 + 360.0 * k / n + 180.0 / n) % 360.0
        if phis is not None and not any(abs(((phi - p + 180.0) % 360.0) - 180.0) < 1.0 for p in phis):
            continue
        W = face_frame(x, y, ap, phi)
        cx, cy = _P(W, 0.0, 0.6, 0.0)[:2]
        if hidden_pt(cx, cy):
            continue
        za = z0 if zmin_fn is None else max(z0, zmin_fn(cx, cy))
        ashlar(mb, W, -side / 2 + 0.04, side / 2 - 0.04, za, z1, 0.0, PL=min(2.9, side / 2 - 0.05),
               phase=0.6 * (k % 2))
    if cord:
        band(mb, x, y, r, n, z1 + 0.05, r0, h=0.8, e=0.42)


def drip(z, e=0.5, h=0.62, back=-0.1):
    """perfil de CORDAO com pingadeira (t, z): recorte por baixo, face da frente, topo em talude (agua escorre)"""
    return [(back, z - h * 0.45), (e * 0.55, z - h * 0.45), (e, z - h * 0.18), (e, z + h * 0.12),
            (e * 0.45, z + h * 0.55), (back, z + h * 0.55)]


def plinth(zb, z1, e0=0.85, e1=0.4, back=-0.1):
    """perfil de SOCO: fiada de base saliente e0 e talude (45 graus) ate a saliencia e1 no topo z1"""
    zt = z1 - (e0 - e1)
    return [(back, zb), (e0, zb), (e0, zt), (e1, z1), (back, z1)]


def wall_base(mb, W, u0, u1, t=0.0, excl=(), zb=ZB, z1=None, soc=True, ash=True, cord=True, phase=0.0):
    """a ZONA DO OLHO de uma parede do castelo: soco de obsidiana em talude + cordao de prata, silhar em fiadas ate
    +8 e cordao de obsidiana com pingadeira. W em t = face da parede (t cresce para fora)"""
    Wt = (_P(W, 0.0, t, 0.0)[:2], W[1], W[2])
    z1 = Z + 8.0 if z1 is None else z1
    if soc:
        ledge(mb, Wt, u0, u1, plinth(zb, SOC, 0.85, 0.42), OB)
        ledge(mb, Wt, u0 - 0.02, u1 + 0.02, [(-0.1, SOC), (0.62, SOC), (0.62, SOC + 0.3), (-0.1, SOC + 0.3)], SV)
    if ash:
        ashlar(mb, Wt, u0, u1, SOC + 0.34, z1 - 0.3, 0.0, excl, phase=phase)
    if cord:
        ledge(mb, Wt, u0, u1, drip(z1, 0.5), OB)


def small_tower(mb, x, y, r, z0, ztop, sph, rot=22.5, slits=(270.0,)):
    """torre octogonal simples: soco, fuste, cordao, parapeito com mata-caes, agulha navy, remate de prata"""
    zs = max(z0 + 3.0, Z + 2.6)
    socle(mb, x, y, r, 8, z0, zs, rot, e=0.8)
    shaft(mb, x, y, r, 8, zs, ztop, "Stone_SG_Castle", rot)
    tower_ashlar(mb, x, y, r, 8, rot, zs + 0.45, Z + 9.7)            # overhaul 03: zona do olho em fiadas
    parapet_ring(mb, x, y, r, 8, ztop, 1.8, OB, rot, merlons=False)
    spire(mb, x, y, r - 0.2, 8, ztop + 1.8, sph, "Roof_SG_Navy", rot)
    finial(mb, x, y, ztop + 1.6 + sph, 1.3)
    ap = r * math.cos(math.pi / 8)
    for phi in slits:
        slit(mb, face_frame(x, y, ap, phi), ztop - 9.0, 3.0, 0.8)


def parapet_ring(mb, cx, cy, r, n, z0, h, m, rot0=None, corbel_m=OB, merlons=True, cap_m=VI):
    """parapeito com mata-caes: fiada de misulas + anel saliente + ameias"""
    ap = r * math.cos(math.pi / n)
    side = 2 * r * math.sin(math.pi / n)
    rot0 = 180.0 / n if rot0 is None else rot0
    for k in range(n):
        phi = rot0 + 360.0 * k / n + 180.0 / n
        W = face_frame(cx, cy, ap, phi)
        for f in ((-0.28, 0.28) if side > 5 else (0.0,)):
            panel(mb, W, rect(f * side - 0.35, f * side + 0.35, z0 - 1.6, z0), -0.2, 0.8, corbel_m)
    frustum(mb, cx, cy, r + 0.9, r + 0.9, n, z0, z0 + h, m, rot0)
    if cap_m:
        frustum(mb, cx, cy, r + 1.1, r + 1.1, n, z0 + h - 0.45, z0 + h, cap_m, rot0)
    if merlons:
        for k in range(n):
            phi = rot0 + 360.0 * k / n + 180.0 / n
            W = face_frame(cx, cy, ap + 0.9 * math.cos(math.pi / n), phi)
            for f in ((-0.25, 0.25) if side > 5 else (0.0,)):
                panel(mb, W, rect(f * side - 0.6, f * side + 0.6, z0 + h, z0 + h + 1.4), -1.0, 0.0, m)


# ------------------------------------------------------------------ 1. muralha, portao, passagem leste, cortina oeste
def muralha(banners):
    """OVERHAUL 03 (03.11/03.12/03.13/12.04): muralha em camadas - talude de obsidiana + filete de prata, PARAMENTO
    EM FIADAS no terco de baixo, cordao com pingadeira no nivel do P3, MATA-CAES de verdade (misulas em 3 degraus com
    arquinhos entre elas sobre o vazio escuro), parapeito com capa chanfrada e merloes em 2 larguras (o largo com
    seteira em cruz) alternando com as ameias; face do patio com rodape em talude, silhar e cordao. Lanternas so nos
    NOS (ao lado das torres): 6 em vez de 13."""
    rng = random.Random(5101)
    mb = MB("SG_Cas_Muralha", "04_CASTLE", rng, detail="near")
    wy0, wy1 = L.WALL_Y0, L.WALL_Y1
    gw = L.GATEHOUSE_W
    cuts = [(-gw / 2, gw / 2), (EG_X - EG_W / 2, EG_X + EG_W / 2)]
    xs = [L.WALL_X[0]] + [c for ab in cuts for c in ab] + [L.WALL_X[1]]
    front = wy0 - 0.3                           # 0,3 a frente da face do arrimo (sem z-fight com o terreno)
    # torres que cobrem a face (x, meia-largura da sombra): o silhar nao gasta pedra dentro delas
    tw_ = [(SW_TOWER[0], SW_TOWER[2] + 1.4)] + [(x, r + 1.2) for x, y, r in WALL_TOWERS] + \
          [(x, GATE_R + 1.2) for x, y, r in L.GATEHOUSE_TOWERS] + [(x, EG_R + 0.9) for x, y in EG_TURRETS]
    tw_ += [(CURTAIN_TOWER[0], 0.0)]

    def excl_towers(z0, z1):
        return [(x - h, x + h, z0 - 1.0, z1 + 1.0) for x, h in tw_ if h > 0]
    Wo = ((0.0, front), (1.0, 0.0), (0.0, -1.0))        # face externa (u = x, t para o P2)
    Wi = ((0.0, wy1), (1.0, 0.0), (0.0, 1.0))           # face do patio
    zt = WALL_TOP
    for a, b in zip(xs[0::2], xs[1::2]):
        mb.box2((a, front, Z2 - 0.6), (b, wy1, WALL_TOP), "Stone_SG_Block", 0.0)
        # base: talude de obsidiana + filete de prata; paramento em fiadas ate o cordao do P3
        ledge(mb, Wo, a, b, [(-0.05, Z2 - 0.6), (0.9, Z2 - 0.6), (0.9, Z2 + 0.7), (0.14, Z2 + 3.2), (-0.05, Z2 + 3.2)],
              OB)
        ledge(mb, Wo, a, b, [(-0.05, Z2 + 3.2), (0.32, Z2 + 3.2), (0.32, Z2 + 3.5), (-0.05, Z2 + 3.5)], SV)
        ashlar(mb, Wo, a + 0.05, b - 0.05, Z2 + 3.56, Z - 0.72, 0.0, excl_towers(Z2, Z), phase=0.3)
        ledge(mb, Wo, a, b, drip(Z - 0.25, 0.55, 0.9), OB)
        # MATA-CAES: fundo escuro, misulas em 3 degraus, arquinhos (segmento de arco) entre elas, parapeito
        ledge(mb, Wo, a, b, [(-0.05, zt - 3.35), (0.05, zt - 3.35), (0.05, zt - 1.5), (-0.05, zt - 1.5)], OB)
        n = max(1, int(round((b - a) / 2.9)))
        step = (b - a) / n
        cx = [a + (k + 0.5) * step for k in range(n)]
        for k, x in enumerate(cx):
            ledge(mb, Wo, x - 0.36, x + 0.36, [(-0.05, zt - 3.35), (0.3, zt - 3.35), (0.3, zt - 2.78), (0.55, zt - 2.78),
                                               (0.55, zt - 2.2), (0.84, zt - 2.2), (0.84, zt - 1.55),
                                               (-0.05, zt - 1.55)], OB)
        for x0_, x1_ in zip([a] + cx, cx + [b]):
            u0_, u1_ = x0_ + (0.36 if x0_ > a else 0.0), x1_ - (0.36 if x1_ < b else 0.0)
            if u1_ - u0_ < 0.6:
                continue
            uc, ha = (u0_ + u1_) / 2, (u1_ - u0_) / 2
            zs = zt - 2.25
            arc = [(uc - ha * math.cos(math.pi * i / 6), zs + 0.5 * math.sin(math.pi * i / 6)) for i in range(7)]
            panel(mb, Wo, [(u0_, zt - 1.5)] + arc + [(u1_, zt - 1.5)], 0.22, 0.72, "Stone_SG_Block")
        panel(mb, Wo, rect(a, b, zt - 1.6, zt), -0.2, 0.74, "Stone_SG_Block")
        ledge(mb, Wo, a - 0.02, b + 0.02, [(-0.6, zt), (0.88, zt), (0.88, zt + 0.14), (0.6, zt + 0.36), (-0.6, zt + 0.36)],
              OB)
        # merloes em 2 larguras (A-B) sobre as misulas pares; ameia (vao) nas impares
        for k, x in enumerate(cx):
            if k % 2:
                continue
            wide = (k // 2) % 2 == 0
            w = min(2.3 if wide else 1.4, step * 0.95)
            mb.box((w, 1.3, 1.9), (x, front - 0.1, zt + 0.36 + 0.95), (0, 0, 0), "Stone_SG_Block", 0.0)
            FP.frustum(mb, (x, front - 0.1, zt + 2.24), w + 0.22, 1.52, w - 0.3, 1.0, 0.34, OB)
            if wide:
                # seteira: fenda vertical com o furo (oillet) em baixo - sem cruz (nada de 2o sistema de simbolos)
                panel(mb, Wo, rect(x - 0.1, x + 0.1, zt + 0.95, zt + 2.0), 0.74, 0.79, OB)
                panel(mb, Wo, rect(x - 0.2, x + 0.2, zt + 0.66, zt + 0.98), 0.74, 0.79, OB)
        # face do PATIO: rodape em talude, silhar em fiadas e cordao a +8
        ledge(mb, Wi, a, b, plinth(Z - 0.3, Z + 1.25, 0.5, 0.22), OB)
        ashlar(mb, Wi, a + 0.05, b - 0.05, Z + 1.3, Z + 7.7, 0.0, excl_towers(Z, Z + 8.0), phase=1.1)
        ledge(mb, Wi, a, b, drip(Z + 8.0, 0.45), OB)
        mb.box2((a, wy1 - 0.8, WALL_TOP), (b, wy1, WALL_TOP + 1.1), "Stone_SG_Block", 0.0)
        ledge(mb, Wi, a, b, [(-0.9, WALL_TOP + 1.1), (0.12, WALL_TOP + 1.1), (0.12, WALL_TOP + 1.26),
                             (-0.2, WALL_TOP + 1.4), (-0.9, WALL_TOP + 1.4)], OB)
        col_box2("SG_CasWall", (a, wy0, Z - 0.5), (b, wy1, WALL_TOP))
    # lanternas da ordem SO nos nos, no passeio atras do parapeito. OVERHAUL 12 (12.04): as 2 das torres intermediarias
    # (-38 e 54) SAIRAM - torre intermediaria nao e passagem; ficam o portao (+-23), o canto oeste e o vao leste
    for lx in (-71.0, -23.0, 23.0, 96.0):
        EM.lantern_pedestal(mb, mb, mb, (lx, front + 1.5, WALL_TOP), 0.0, 0.8)
    # --- torre-portaria: VERGA baixa entre as 2 torres (vao 16 x 18 livre). Baixa de proposito: da praca o olho passa
    # por cima dela e encontra o emblema monumental da fachada. Overhaul 03 (03.12): verga de ADUELAS em arco abatido
    # (juntas radiais, extradorso curvo) com FECHO saliente; a grade levadica tem MALHA (3 travessas) e sai de um SULCO
    # no intradorso, correndo em trilhos nas ombreiras.
    gz = Z + L.GATEHOUSE_H
    gh = 3.6
    gy0, gy1 = wy0 - 1.6, wy1 + 1.4
    mb.box2((-gw / 2 - 0.5, gy0, gz), (gw / 2 + 0.5, gy1, gz + gh), "Stone_SG_Castle", 0.0)
    col_box2("SG_CasWall", (-gw / 2, gy0, gz), (gw / 2, gy1, gz + gh))
    hw = gw / 2 + 0.6
    FZ = gz - 11.0                                  # foco das juntas radiais

    def ext(u):
        return gz + 2.05 + 0.65 * (1.0 - (u / hw) ** 2)
    for yy, sgn in ((gy0, -1), (gy1, 1)):
        W = ((0.0, yy), (1.0, 0.0), (0.0, sgn))
        panel(mb, W, rect(-hw - 0.2, hw + 0.2, gz - 0.02, gz + 2.95), -0.05, 0.1, OB)
        nv = 9
        us = [-hw + 2 * hw * k / nv for k in range(nv + 1)]

        def top_of(ub):
            u = ub
            for _ in range(3):
                zt_ = ext(u)
                u = ub * (zt_ - FZ) / (gz - FZ)
            return u, ext(u)
        for k in range(nv):
            ua, ub = us[k] + 0.05, us[k + 1] - 0.05
            ta, tb = top_of(ua), top_of(ub)
            key = k == nv // 2
            if key:
                ta, tb = (ta[0], ta[1] + 0.45), (tb[0], tb[1] + 0.45)
            poly = [(ua, gz), (ub, gz), tb, ta]
            panel(mb, W, poly, 0.08, 0.78 if key else 0.5, VI if (key or k % 2 == 0) else CM_)
        ledge(mb, W, -hw - 0.3, hw + 0.3, [(-0.05, gz + 2.9), (0.62, gz + 2.9), (0.82, gz + 3.18), (0.82, gz + 3.45),
                                           (0.35, gz + 3.9), (-0.05, gz + 3.9)], VI)
    mb.box2((-gw / 2 - 0.5, gy0 - 0.3, gz + gh), (gw / 2 + 0.5, gy1 + 0.3, gz + 3.9), VI, 0.0)
    # grade levadica recolhida: sulco escuro no intradorso, 9 barras com ponta, 3 travessas; trilhos nas ombreiras
    mb.box2((-gw / 2, -6.45, gz - 0.03), (gw / 2, -5.55, gz + 0.02), OB, 0.0)
    for k in range(9):
        x = -gw / 2 + 0.9 + k * (gw - 1.8) / 8
        mb.box2((x - 0.11, -6.11, gz - 1.25), (x + 0.11, -5.89, gz + 0.05), BI, 0.0)
        mb.cyl(0.15, 0.45, (x, -6.0, gz - 1.47), (math.pi, 0, math.pi / 4), BI, n=4, r2=0.0, bevel=0.0)
    for zz in (gz - 0.22, gz - 0.68, gz - 1.14):
        mb.box2((-gw / 2 + 0.25, -6.16, zz - 0.08), (gw / 2 - 0.25, -5.84, zz + 0.08), BI, 0.0)
    for sx in (-1, 1):
        xf = sx * (gw / 2 + 0.06)
        a_, b_ = sorted((xf, xf - sx * 0.03))
        mb.box2((a_, -6.3, Z + 0.05), (b_, -5.7, gz), OB, 0.0)
        for yy in (-6.38, -5.62):
            a2, b2 = sorted((xf, xf - sx * 0.07))
            mb.box2((a2, yy - 0.07, Z + 0.05), (b2, yy + 0.07, gz), BI, 0.0)
    # --- torres do portao (planta), face plana alinhada ao vao; estandarte da ordem na face sul
    for (x, y, r0) in L.GATEHOUSE_TOWERS:
        r = GATE_R
        rot = 22.5
        socle(mb, x, y, r, 8, Z2 - 0.6, Z2 + 4.0, rot)
        shaft(mb, x, y, r, 8, Z2 + 4.0, Z + 36.0, "Stone_SG_Castle", rot)
        tower_ashlar(mb, x, y, r, 8, rot, Z2 + 4.45, Z - 0.75, phis=(225.0, 270.0, 315.0))
        tower_ashlar(mb, x, y, r, 8, rot, Z + 0.3, Z + 7.7)
        band(mb, x, y, r, 8, WALL_TOP - 1.6, rot, h=1.6, e=0.35)
        parapet_ring(mb, x, y, r, 8, Z + 36.0, 2.4, OB, rot)
        spire(mb, x, y, r - 0.4, 8, Z + 38.4, 23.0, "Roof_SG_Navy", rot, rings=(0.34,))
        finial(mb, x, y, Z + 61.0, 2.0)
        ap = r * math.cos(math.pi / 8)
        s = 1 if x > 0 else -1
        out_phi = 0.0 if s > 0 else 180.0
        for phi, zz, h, w in ((270.0 + s * 45.0, Z + 14.0, 3.4, 0.9), (out_phi, Z + 27.0, 3.4, 0.9),
                              (270.0 + s * 45.0, Z + 21.0, 3.0, 0.85), (out_phi, Z + 8.9, 3.0, 0.85),
                              (270.0 + s * 45.0, Z + 29.0, 3.0, 0.85)):
            slit(mb, face_frame(x, y, ap, phi % 360.0), zz, h, w)
        # lucarna pequena na agulha (face sul e face de fora): caixa de obsidiana, janela quente e telhadinho
        for phi in (270.0, out_phi):
            a = math.radians(phi)
            d = (r - 0.4) * 0.62
            lz = Z + 38.4 + 23.0 * 0.2
            lx, ly = x + d * math.cos(a), y + d * math.sin(a)
            mb.box((1.5, 1.9, 2.8), (lx, ly, lz + 1.4), (0, 0, a), OB, 0.0)
            lancet_win(mb, face_frame(lx, ly, 0.75, phi), 0.0, lz + 0.45, 1.8, 0.7, 0.0, glass=WW_M, dp=0.22, fw=0.16,
                       bar=False)
            dormer_roof(mb, lx, ly, lz + 2.8, 1.9, 1.5, 1.8, a)
        W = face_frame(x, y, ap, 270.0)
        banners.append((_P(W, 0.0, 0.45, Z + 33.0), -math.pi / 2, 3.8, 17.0, 0.45))
        ngon_col("SG_CasTower", x, y, 8, r, Z2 - 0.5, Z + 36.0, rot)
    # lanternas de poste no patamar do portao (lado do patio), fora do vao de 16
    for sx in (-1, 1):
        EM.lantern_post(mb, mb, (sx * 11.0, 1.6, Z), 0.0, h=7.0, s=0.9)
    # --- passagem leste (aberta ate o ceu) com 2 torrinhas
    for x, y in EG_TURRETS:
        socle(mb, x, y, EG_R, 8, Z2 - 0.6, Z2 + 3.0, 22.5, e=0.6)
        shaft(mb, x, y, EG_R, 8, Z2 + 3.0, Z + 18.0, "Stone_SG_Castle", 22.5)
        tower_ashlar(mb, x, y, EG_R, 8, 22.5, Z2 + 3.45, Z - 0.75, phis=(225.0, 270.0, 315.0))
        tower_ashlar(mb, x, y, EG_R, 8, 22.5, Z + 0.3, Z + 7.7)
        frustum(mb, x, y, EG_R + 0.7, EG_R + 0.7, 8, Z + 18.0, Z + 19.6, OB, 22.5)
        frustum(mb, x, y, EG_R + 0.85, EG_R + 0.85, 8, Z + 19.2, Z + 19.6, VI, 22.5)
        spire(mb, x, y, EG_R + 0.2, 8, Z + 19.6, 13.5, "Roof_SG_Navy", 22.5)
        finial(mb, x, y, Z + 32.7, 1.2)
        slit(mb, face_frame(x, y, EG_AP, 270.0), Z + 9.4, 2.8, 0.8)
        ngon_col("SG_CasTower", x, y, 8, EG_R, Z2 - 0.5, Z + 18.0, 22.5)
    # --- torre de canto sudoeste + cortina oeste pela borda do P3 ate a ala oeste
    x, y, r = SW_TOWER
    socle(mb, x, y, r, 8, ZT, Z2 + 4.0, 22.5, e=1.0)
    shaft(mb, x, y, r, 8, Z2 + 4.0, Z + 20.0, "Stone_SG_Castle", 22.5)
    tower_ashlar(mb, x, y, r, 8, 22.5, Z2 + 4.45, Z - 0.7, cord=False)
    band(mb, x, y, r, 8, Z - 0.6, 22.5)
    tower_ashlar(mb, x, y, r, 8, 22.5, Z + 0.75, Z + 7.7)
    parapet_ring(mb, x, y, r, 8, Z + 20.0, 2.2, OB, 22.5)
    spire(mb, x, y, r - 0.3, 8, Z + 22.2, 18.0, "Roof_SG_Navy", 22.5)
    finial(mb, x, y, Z + 40.0, 1.6)
    slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), 270.0), Z + 9.2, 3.2, 0.9)
    ngon_col("SG_CasTower", x, y, 8, r, Z2 - 0.5, Z + 20.0, 22.5)
    for (x, y, r) in WALL_TOWERS:
        small_tower(mb, x, y, r, Z2 - 0.6, Z + 21.0, 16.0, slits=(270.0, 90.0, 315.0))
        ngon_col("SG_CasTower", x, y, 8, r, Z2 - 0.5, Z + 21.0, 22.5)
    x, y, r = CURTAIN_TOWER
    small_tower(mb, x, y, r, ZT, Z + 24.0, 18.0, slits=(180.0, 0.0, 270.0))
    ngon_col("SG_CasTower", x, y, 8, r, Z - 0.5, Z + 24.0, 22.5)
    edge = [(L.WALL_X[0], wy0), (-78.0, 40.0), (-60.0, 60.0)]
    th = 3.4
    for (ax, ay), (bx, by) in zip(edge, edge[1:]):
        dx, dy = bx - ax, by - ay
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = -uy, ux                        # para fora (oeste) no contorno anti-horario
        ang = math.atan2(dy, dx)
        cx, cy = (ax + bx) / 2 + nx * th / 2, (ay + by) / 2 + ny * th / 2
        top = Z + 10.0
        mb.box((ln + th, th, top - ZT), (cx, cy, (ZT + top) / 2), (0, 0, ang), "Stone_SG_Block", 0.0)
        mb.box((ln + th, th + 0.8, 1.2), (cx + nx * 0.4, cy + ny * 0.4, top - 0.6), (0, 0, ang), OB, 0.0)
        # face do patio (a rota do beco passa a ~8): rodape em talude, silhar, cordao; merloes com capa chanfrada
        Wc = ((ax, ay), (ux, uy), (-nx, -ny))
        u_a = 7.5 if ay < 0 else 0.4                 # (a torre da cortina cobre o comeco do 1o lance)
        ledge(mb, Wc, 0.0, ln, plinth(Z - 0.3, Z + 1.25, 0.5, 0.22), OB)
        ashlar(mb, Wc, u_a, ln - 0.4, Z + 1.3, Z + 7.7, 0.0,
               [(math.hypot(CURTAIN_TOWER[0] - ax, CURTAIN_TOWER[1] - ay) - CURTAIN_TOWER[2] - 1.2,
                 math.hypot(CURTAIN_TOWER[0] - ax, CURTAIN_TOWER[1] - ay) + CURTAIN_TOWER[2] + 1.2, Z, Z + 9.0)],
               phase=0.6)
        ledge(mb, Wc, 0.0, ln, drip(Z + 8.0, 0.45), OB)
        n = max(1, int(ln / 3.4))
        for k in range(n):
            if k % 2 == 0:
                t = (k + 0.5) / n
                px, py = ax + dx * t + nx * (th - 0.6), ay + dy * t + ny * (th - 0.6)
                w = 1.9 if (k // 2) % 2 == 0 else 1.3
                mb.box((w, 1.2, 1.8), (px, py, top + 0.9), (0, 0, ang), "Stone_SG_Block", 0.0)
                FP.frustum(mb, (px, py, top + 1.8), w + 0.2, 1.4, w - 0.3, 0.9, 0.32, OB, ang=ang)
        col_box("SG_CasCurtain", (ln + th, th, top - Z + 0.5), (cx, cy, (Z - 0.5 + top) / 2), (0, 0, ang))
    _fin(mb)


def banzo(mb, name, s, yb_max, post=True):
    """banzo continuo da escada 'name' da planta (receita 01.01 / 02.13, mesma do sg_entry e da vila): paramento em
    fiadas de 2 alturas sob a linha inclinada, rodape que acompanha os focinhos, capa inclinada em pecas com
    pingadeira e o pilarete de arranque do kit no pe. Substitui os blocos em dente de serra (03.17)"""
    import sg_entry as SE
    foot, deg, w, n, tread, g = L.stair_frame(name)
    rise = (L.STAIR_TOP_Z[name] - foot[2]) / n
    ya, yb = foot[1], min(foot[1] + tread * n, yb_max)
    ta = foot[2] + 1.25
    k = rise / tread
    tb = ta + k * (yb - ya)
    xc = foot[0]
    x0, x1 = sorted((xc + s * (w / 2), xc + s * (w / 2 + 1.4)))
    zb = foot[2] - 0.3
    c0, ci = zb, 0
    while c0 < tb - 0.05:
        c1 = min(c0 + (1.0, 0.8)[ci % 2], tb)
        if c1 <= ta:
            poly = [(ya, c0), (yb, c0), (yb, c1), (ya, c1)]
        else:
            ys0 = ya + max(0.0, (c0 - ta) / k)
            ys1 = min(yb, ya + (c1 - ta) / k)
            poly = [(ys0, c0), (yb, c0), (yb, c1), (ys1, c1)]
            if c0 < ta:
                poly.append((ya, ta))
        off = (0.0, 1.3)[ci % 2]
        cuts = [ya] + [ya + off + 2.6 * j for j in range(1, 12) if ya + off + 2.6 * j < yb - 0.8] + [yb]
        for u0, u1 in zip(cuts, cuts[1:]):
            bp = SE._dedupe(SE._clip_y(poly, u0 + 0.04, u1 - 0.04))
            if len(bp) >= 3 and abs(SL.area(bp)) > 0.2 and max(p[0] for p in bp) - min(p[0] for p in bp) > 0.3:
                SE.yz_block(mb, x0, x1, bp, SE.PAR_M, 0.07)   # 16.01: o mesmo chanfro do banzo da entrada (0,07)
        c0, ci = c1, ci + 1

    def zn(y):
        return foot[2] + rise + (y - ya) * rise / tread
    xr = xc + s * (w / 2 + 0.06)
    mb.beam((xr, ya + 0.1, zn(ya + 0.1) + 0.36), (xr, yb - 0.1, zn(yb - 0.1) + 0.36), 0.14, 0.5, SE.REL_M, 0.0)
    xm = xc + s * (w / 2 + 0.7)
    from mathutils import Vector
    A = Vector((xm, ya - 0.2, ta - 0.2 * k))
    B = Vector((xm, yb, tb))
    dd = B - A
    nseg = max(1, int(round(dd.length / 2.5)))
    for j in range(nseg):
        p0 = A + dd * (j / nseg) + dd.normalized() * (0.03 if j else 0.0)
        p1 = A + dd * ((j + 1) / nseg) - dd.normalized() * (0.03 if j < nseg - 1 else 0.0)
        mb.beam((p0.x, p0.y, p0.z + 0.26), (p1.x, p1.y, p1.z + 0.26), 1.75, 0.32, SE.CAP_M, 0.06)
    mb.beam((xm, A.y + 0.1, A.z + 0.1 * k + 0.04), (xm, B.y - 0.1, B.z - 0.1 * k + 0.04), 1.56, 0.12, SE.CAP_M, 0.0)
    if post:
        SE._post(mb, xc + s * (w / 2 + 1.0), ya - 0.1, foot[2], 1.5, 2.9, lamp=False)


def stairs():
    mb = MB("SG_Cas_Escadas", "04_CASTLE", random.Random(5103), detail="near")
    SL.plan_stair(mb, "Gate", stringers=False)
    SL.plan_stair(mb, "EastP3", stringers=False)
    for s in (-1, 1):
        banzo(mb, "Gate", s, -10.4, post=False)       # o pe da escada do portao ja e marcado pelos postes do arco
        banzo(mb, "EastP3", s, -10.1)
    mb.finish()


# ------------------------------------------------------------------ 2. nave: casca do Mining Hall
# faixas horizontais da casca (z0, z1, t0, t1, material): cornija, parapeito, remate, soco, cordao, faixa das janelas
SIDE_BANDS = [(EAVE - 1.0, EAVE + 0.4, TW - 0.2, TW + 0.8, OB), (EAVE + 0.4, EAVE + 2.0, TW - 0.9, TW, CM_),
              (EAVE + 1.7, EAVE + 2.1, TW - 1.0, TW + 0.15, VI), (ZB, SOC, TW - 0.1, TW + 0.7, OB),
              (SOC - 0.05, SOC + 0.35, TW - 0.1, TW + 0.8, SV), (WIN_SILL - 1.6, WIN_SILL - 0.55, TW - 0.1, TW + 0.5, OB)]


def nave():
    rng = random.Random(5201)
    mb = MB("SG_Cas_Nave", "04_CASTLE", rng, detail="near")
    IM = "Stone_SGCasInterior"
    CM = "Stone_SG_Castle"
    tg = TW * 0.5                                        # vidro no meio da parede
    opens_side = [(y, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE) for y in WIN_Y]
    # paredes laterais (u = y), face interna exata no retangulo do salao
    for W in (((HX0, 0.0), (0.0, 1.0), (-1.0, 0.0)), ((HX1, 0.0), (0.0, 1.0), (1.0, 0.0))):
        west = W[2][0] < 0
        wall_run(mb, W, HY0, HY1, ZB, EAVE, 0.0, TW, opens_side, CM, IM)
        for y in WIN_Y:
            window(mb, W, y, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, tg, TW, glass_m=WW_M, hood=True, back_m=OB)
        # cornija de obsidiana (coroamento) + parapeito baixo com remate violeta
        # acabamento: as faixas laterais passam a saliencia delas alem das quinas (ext = t1 - TW) e as faixas das
        # fachadas sul/norte comecam na face interna delas -> quina fechada, sem dente nem ponta cortada no ar
        for bi, (z0_, z1_, t0_, t1_, m_) in enumerate(SIDE_BANDS):
            if west and bi in (3, 4):
                continue                                    # soco/cordao: vem do wall_base (beco oeste)
            ext = max(0.0, t1_ - TW) if z0_ < EAVE + 0.3 else 0.0   # parapeito/remate terminam na empena
            panel(mb, W, rect(HY0 - TW - ext, HY1 + TW + ext, z0_, z1_), t0_, t1_, m_)
        if west:
            # OVERHAUL 03 (03.08): beco oeste na altura do olho - soco em talude, silhar em fiadas entre os
            # contrafortes e cordao com pingadeira a +8 (a torre da fachada cobre ate y 48, a torrinha de tras de 133)
            excl = [(y - 1.75, y + 1.75, ZB, Z + 40.0) for y in BUTT_Y]
            wall_base(mb, W, 49.8, OY1 - 2.3, t=TW, excl=excl)
    # fachada sul (u = x, t para fora = -y): naves laterais com janela + corpo central com a porta
    WS = ((0.0, HY0), (1.0, 0.0), (0.0, -1.0))
    WN = ((0.0, HY1), (1.0, 0.0), (0.0, 1.0))
    for W, front in ((WS, True), (WN, False)):
        for s in (-1, 1):
            u0, u1 = (OX0, -CLR) if s < 0 else (CLR, OX1)
            uw = s * (CLR + (OX1 - CLR) * 0.4)           # 04b: janela no meio da nave lateral (era 33 com 46)
            opens = [(uw, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE)] if front else []   # fundo fechado: altar do hall
            wall_run(mb, W, u0, u1, ZB, EAVE, 0.0, TW, opens, CM, IM)
            if front:
                window(mb, W, uw, WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE, tg, TW, glass_m=WW_M, hood=True)
            # empena de meia-agua da nave lateral (esconde o perfil do telhado)
            uo, ui = (OX0, -CLR) if s < 0 else (OX1, CLR)
            panel(mb, W, [(uo, EAVE), (ui, EAVE), (ui, AISLE_HI + 1.6), (uo, EAVE + 3.2)], 0.4, TW, CM)
            panel(mb, W, [(uo, EAVE + 2.6), (ui, AISLE_HI + 1.0), (ui, AISLE_HI + 2.2), (uo, EAVE + 3.8)], TW - 0.2,
                  TW + 0.6, OB)
            for bi, (z0_, z1_, t0_, t1_, m_) in enumerate(SIDE_BANDS):
                if z0_ >= EAVE + 0.3:
                    continue                                  # parapeito: a empena da nave lateral ja fecha a quina
                if bi in (3, 4):
                    continue                                  # soco/cordao: wall_base (zona do olho) abaixo
                ua = s * (OX1 - (TW - t0_))                   # face interna da faixa lateral
                # overhaul 03 (03.18): na fachada a faixa MORRE num bloco de arremate antes da torrinha (antes entrava
                # ate o eixo da torrinha); no fundo morre na torre-coroa (04b: a base dela abre a abside do trono)
                ub = s * (CLR + 3.5) if front else s * (L.APSE_HW + 0.1)   # 04b: atras morre na torre-coroa
                panel(mb, W, rect(min(ua, ub), max(ua, ub), z0_, z1_), t0_, t1_, m_)
                if front and bi in (0, 5):
                    us0, us1 = sorted((s * (CLR + 2.5), s * (CLR + 3.6)))
                    block(mb, W, us0, us1, z0_ - 0.45, z1_ + 0.3, TW - 0.1, t1_ + 0.22, 0.12, ASH)
            # zona do olho: soco em talude, silhar e cordao (fachada: entre a torre da ponta e a torrinha; fundo: entre
            # a torrinha de tras e a torre-coroa, voltado para o terraco)
            if front:
                ua_, ub_ = sorted((s * (OX1 - 3.5), s * (CLR + 3.9)))      # ate a torre da fachada (x 58)
                wall_base(mb, W, ua_, ub_, t=TW, phase=0.9)
            else:
                ua_, ub_ = sorted((s * (OX1 - 4.2), s * 11.6))             # da torrinha de tras ate a torre-coroa
                wall_base(mb, W, ua_, ub_, t=TW, phase=0.4)
            # ritmo de janelas quentes na empena da nave lateral (sotao, acima do teto do salao: nada de interior falso)
            # (04b: posicao e altura seguem a empena da nave lateral, que ficou mais larga e mais inclinada)
            for f_ in (0.22, 0.5, 0.78):
                uu = CLR + (OX1 - CLR) * f_
                ztop = AISLE_HI + 1.6 + (EAVE + 3.2 - AISLE_HI - 1.6) * f_ - 1.6
                hw_ = min(4.4, ztop - EAVE - 0.9)
                wlancet(mb, W, s * uu, ztop - hw_, hw_, 1.0, t=TW + 0.02)
        if front:
            panel(mb, W, rect(-CLR, -DW / 2, ZB, CLR_TOP), 0.0, TW, CM, IM)
            panel(mb, W, rect(DW / 2, CLR, ZB, CLR_TOP), 0.0, TW, CM, IM)
            panel(mb, W, rect(-DW / 2, DW / 2, Z + DH, CLR_TOP), 0.0, TW, CM, IM)
        else:
            # 04b: ARCO TRIUNFAL no eixo (a abside do trono fica na base da torre-coroa, atras desta parede)
            # o vao na casca e o contorno da ORDEM EXTERNA (as 3 ordens escalonadas que fecham ate o presbiterio sao
            # do sg_hall, dentro da espessura desta parede)
            ho = L.TRI_HW + L.TRI_ORDERS * L.TRI_STEP
            panel(mb, W, rect(-CLR, -ho, ZB, CLR_TOP), 0.0, TW, CM, IM)
            panel(mb, W, rect(ho, CLR, ZB, CLR_TOP), 0.0, TW, CM, IM)
            panel(mb, W, [(ho, CLR_TOP), (-ho, CLR_TOP)] + ogive(0.0, L.TRI_HW, Z + L.TRI_SPRING, L.TRI_RISE,
                                                                 d=ho - L.TRI_HW), 0.0, TW, CM, IM)
        if front:
            # soco + cordao de prata do corpo central (fora do vao da porta)
            for s_ in (-1, 1):
                u0_, u1_ = sorted((s_ * (CLR - 2.6), s_ * (DW / 2 + 5.6)))
                wall_base(mb, W, u0_, u1_, t=TW, ash=False, cord=False)
            # faixas de obsidiana marcando os andares (fora do arco do emblema). Overhaul 03 (03.18): o toco entre o
            # ombro do arco e a torrinha saiu (a faixa entrava no fuste colada a janela); a faixa da torrinha fica na
            # mesma cota com pingadeira (band com perfil)
            for s_ in (-1, 1):
                # pilha de janelas quentes ladeando o arco do emblema (2 andares, acima do teto do salao)
                # (acabamento: estreitas e no vao livre entre a banda do arco e a torrinha - antes entravam na torrinha)
                for z0w in (Z + 38.3, Z + 45.8, Z + 53.3, Z + 60.8, Z + 68.3, Z + 75.8):   # 04b: 6 andares (a fachada subiu)
                    wlancet(mb, W, s_ * 18.5, z0w, 3.4, 0.8, t=TW + 0.02)
            # coroamento da fachada: misulas de obsidiana + parapeito; no meio, a EMPENA que recebe o arco de prata do
            # emblema (o parapeito se interrompe onde o arco sobe)
            for k in range(14):
                u = -CLR + (k + 0.5) * 2 * CLR / 14
                if abs(u) < GAB_W - 0.8:
                    continue
                panel(mb, W, rect(u - 0.4, u + 0.4, CLR_TOP - 1.8, CLR_TOP), TW - 0.2, TW + 0.8, OB)
            for s_ in (-1, 1):
                a_, b_ = sorted((s_ * (CLR + 0.6), s_ * GAB_W))
                a2, b2 = sorted((s_ * (CLR + 0.8), s_ * GAB_W))
                panel(mb, W, rect(a_, b_, CLR_TOP, CLR_TOP + 2.4), TW - 1.4, TW + 0.8, CM)
                panel(mb, W, rect(a2, b2, CLR_TOP + 2.0, CLR_TOP + 2.6), TW - 1.6, TW + 1.0, VI)
            for k in range(8):
                u = -CLR + 1.2 + k * (2 * CLR - 2.4) / 7
                if abs(u) < GAB_W + 0.6:
                    continue
                panel(mb, W, rect(u - 0.9, u + 0.9, CLR_TOP + 2.6, CLR_TOP + 4.4), TW - 1.2, TW + 0.6, OB)
            # empena central (pedra do corpo), rampantes de obsidiana, remate de prata
            gz1 = GAB_TOP
            panel(mb, W, [(-GAB_W, CLR_TOP - 2.0), (GAB_W, CLR_TOP - 2.0), (GAB_W, CLR_TOP + 2.4), (0.0, gz1),
                          (-GAB_W, CLR_TOP + 2.4)], TW - 1.4, TW, CM)
            for sd in (-1, 1):
                a, b = (sd * (GAB_W + 0.4), CLR_TOP + 2.2), (0.0, gz1)
                L2 = math.hypot(b[0] - a[0], b[1] - a[1])
                tilt = math.atan2(b[1] - a[1], b[0] - a[0])
                mb.box((L2 + 1.2, 2.4, 1.0), _P(W, (a[0] + b[0]) / 2, TW - 0.4, (a[1] + b[1]) / 2 + 0.35),
                       (0, -tilt, 0), OB, 0.0)
                mb.box((L2 + 1.0, 0.5, 0.3), _P(W, (a[0] + b[0]) / 2, TW + 0.55, (a[1] + b[1]) / 2 + 0.95),
                       (0, -tilt, 0), SV, 0.0)
                # pinaculos nos pes da empena (kit)
                px = sd * (GAB_W + 0.4)
                pp = _P(W, px, TW - 0.3, 0)
                pinnacle(mb, pp[0], pp[1], CLR_TOP + 2.3, 0.85, hb=3.4, hn=6.0, body_m=OB, crock=False)
            mb.box((1.6, 1.6, 2.2), _P(W, 0.0, TW - 0.5, gz1 + 0.6), (0, 0, 0), OB, 0.0)
            pp = _P(W, 0.0, TW - 0.5, 0)
            finial(mb, pp[0], pp[1], gz1 + 1.65, 2.2)
            continue
        # empena de tras (encosta na torre-coroa)
        g_lo = CLR_TOP + 1.9
        apex = CLR_TOP + NAVE_RISE + 1.9
        panel(mb, W, [(-CLR, CLR_TOP), (CLR, CLR_TOP), (CLR, g_lo), (0.0, apex), (-CLR, g_lo)], 0.8, TW, CM)
        for s in (-1, 1):
            a = (s * CLR, g_lo)
            b = (0.0, apex)
            L2 = math.hypot(b[0] - a[0], b[1] - a[1])
            tilt = math.atan2(b[1] - a[1], b[0] - a[0])
            mid = _P(W, (a[0] + b[0]) / 2, 2.4, (a[1] + b[1]) / 2 + 0.2)
            mb.box((L2 + 0.8, 3.6, 0.9), mid, (0, -tilt, 0), OB, 0.0)
        pp = _P(W, 0.0, TW - 1.0, 0)
        finial(mb, pp[0], pp[1], apex + 0.2, 2.6)
    # clerestorio (acima do teto interno): paredes x +-CLR com janelas cegas (vidro rente, sem vazar o sotao)
    for s in (-1, 1):
        W = ((s * (CLR - 2.0), 0.0), (0.0, 1.0), (s * 1.0, 0.0))
        panel(mb, W, rect(HY0, HY1, CEIL + 2.0, CLR_TOP), 0.0, 2.0, CM)
        for y in WIN_Y:
            # lancetas altas do clerestorio: energia violeta (o castelo "respira" violeta no alto)
            window(mb, W, y, 1.9, AISLE_HI + 1.6, CLR_TOP - 5.0, 2.8, 2.05, 2.0, glass_m=WW_M, mullion=True, fw=0.6,
                   dp=0.35)
        panel(mb, W, rect(HY0 - TW, HY1 + TW, CLR_TOP - 0.9, CLR_TOP + 0.3), 1.6, 2.7, OB)
    # contrafortes (em degraus) + pinaculos + arcobotantes ate o clerestorio
    # OVERHAUL 03 (03.09): contraforte com RESSALTOS de talude real (45 graus) e pingadeira, soco em talude, silhar e
    # cordao na zona do olho; ARCOBOTANTE como perfil extrudado (intradorso em quarto de elipse que nasce vertical no
    # pilar e encosta horizontal no clerestorio, extradorso reto com capa de obsidiana); pinaculos do kit
    for y in BUTT_Y:
        for s in (-1, 1):
            xo = s * OX1
            bp = BUTT_P[s]                                         # saliencia do 1o lance (oeste raso: beco)
            bp2 = min(2.4, bp * 0.72)                              # 2o lance
            Wb = ((xo, 0.0), (0.0, 1.0), (float(s), 0.0))           # u = y, t = saliencia a partir da face da nave
            ledge(mb, Wb, y - 2.1, y + 2.1, plinth(ZB, SOC, bp + 0.7, bp + 0.22), OB)
            ledge(mb, Wb, y - 1.78, y + 1.78, [(-0.1, SOC), (bp + 0.18, SOC), (bp + 0.18, SOC + 0.3), (-0.1, SOC + 0.3)],
                  SV)
            # 1o lance (bp x 3,2) com talude de 45 graus ate o 2o lance + pingadeira sob o talude
            zt1 = Z + 18.6
            ledge(mb, Wb, y - 1.6, y + 1.6, [(-0.1, SOC), (bp, SOC), (bp, zt1), (bp2 - 0.05, zt1 + bp - bp2 + 0.05),
                                             (-0.1, zt1 + bp - bp2 + 0.05)], CM)
            ledge(mb, Wb, y - 1.72, y + 1.72, [(bp - 0.15, zt1 - 0.65), (bp + 0.22, zt1 - 0.55), (bp + 0.22, zt1 - 0.3),
                                               (bp - 0.15, zt1 - 0.05)], OB)
            # silhar nas 3 faces do 1o lance + cordao a +8 contornando (casa com o da parede)
            Wf_ = ((xo + s * bp, 0.0), (0.0, 1.0), (float(s), 0.0))
            ashlar(mb, Wf_, y - 1.6, y + 1.6, SOC + 0.34, Z + 7.7, 0.0, PL=2.05, phase=0.55 if s > 0 else 0.0)
            ledge(mb, Wf_, y - 2.1, y + 2.1, drip(Z + 8.0, 0.5), OB)
            for sy in (-1, 1):
                Ws_ = ((0.0, y + sy * 1.6), (float(s), 0.0), (0.0, float(sy)))
                if bp > 2.0:
                    ashlar(mb, Ws_, OX1 + 0.02, OX1 + bp, SOC + 0.34, Z + 7.7, 0.0, PL=2.3, phase=0.4)
                ledge(mb, Ws_, OX1 - 0.1, OX1 + bp + 0.5, drip(Z + 8.0, 0.5), OB)
            # 2o lance ate o pe do pinaculo
            z2 = zt1 + bp - bp2 + 0.05
            ledge(mb, Wb, y - 1.3, y + 1.3, [(-0.1, z2 - 0.1), (bp2, z2 - 0.1), (bp2, EAVE + 3.0),
                                             (-0.1, EAVE + 3.0)], CM)
            ptop = pinnacle(mb, xo + s * bp2 / 2.0, y, EAVE + 3.0, 1.0 if bp2 > 2.0 else 0.62, hb=7.0, hn=9.5)
            # pinaculo no topo do clerestorio onde o arcobotante encosta (Tier C: sem crochés)
            pinnacle(mb, s * (CLR + 0.6), y, CLR_TOP + 0.2, 0.85, hb=3.0, hn=7.6, crock=False)
            # arcobotante
            zc, dp_, dw_ = EAVE + 3.4, OX1 + 0.2, CLR
            b_ = AISLE_HI + 1.4 - zc
            z_ex0, z_ex1 = EAVE + 9.8, AISLE_HI + 5.8
            lo, hi = [], []
            for i in range(9):
                th = (math.pi / 2) * i / 8
                d = dw_ + (dp_ - dw_) * math.cos(th)
                lo.append((d, zc + b_ * math.sin(th)))
                hi.append((d, z_ex0 + (dp_ - d) / (dp_ - dw_) * (z_ex1 - z_ex0)))
            Wfl = ((0.0, y), (float(s), 0.0), (0.0, 1.0))
            strip(mb, Wfl, lo, hi, -0.55, 0.55, CM)
            mb.beam((s * dp_, y, z_ex0 + 0.12), (s * dw_, y, z_ex1 + 0.12), 1.4, 0.3, OB, 0.0)
            col_box2("SG_CasButtress", (min(xo, xo + s * bp), y - 1.6, Z - 0.5), (max(xo, xo + s * bp), y + 1.6, Z + 20.0))
    # teto interno (opaco) + nervuras transversais alinhadas aos contrafortes
    mb.box2((OX0 + 0.3, OY0 + 0.3, CEIL), (OX1 - 0.3, OY1 - 0.3, CEIL + 2.0), IM, 0.0)
    for y in BUTT_Y:
        mb.box2((HX0, y - 0.7, CEIL - 1.0), (HX1, y + 0.7, CEIL), "Stone_SG_Trim", 0.0)
    mb.box2((-0.7, HY0, CEIL - 1.0), (0.7, HY1, CEIL), "Stone_SG_Trim", 0.0)
    for x in (HX0 + 0.5, HX1 - 0.5):
        mb.box2((x - 0.5, HY0, CEIL - 0.9), (x + 0.5, HY1, CEIL), "Stone_SG_Trim", 0.0)
    mb.finish()
    # colisao: paredes com o vao da porta + teto que segura a camera
    box_walls_col("SG_CasHall", (HX0, HY0, HX1, HY1), Z - 0.5, EAVE, TW,
                  doors=[("S", 0.0, DW, DH), ("N", 0.0, 2 * (L.TRI_HW + L.TRI_ORDERS * L.TRI_STEP), L.TRI_SPRING + 0.5)])
    col_box2("SG_CasHallCeil", (OX0, OY0, CEIL), (OX1, OY1, CEIL + 2.0))


def nave_roof(mb, e=1.6, yf=HY0 - 2.0, yb=OY1 + 1.4):
    """telhado da nave: quatro aguas na frente (atras do parapeito da fachada), empena atras (na torre-coroa);
    solido fechado + fiadas de ardosia recortadas nas aguas + cumeeira e rincoes"""
    bm = mb.bm
    k = NAVE_RISE / CLR
    zE = CLR_TOP - k * e
    zR = CLR_TOP + NAVE_RISE
    H = CLR + e
    yr = yf + H
    FL, FR = (-H, yf, zE), (H, yf, zE)
    BL, BR = (-H, yb, zE), (H, yb, zE)
    RF, RB = (0.0, yr, zR), (0.0, yb, zR)
    vs = {n: bm.verts.new(p) for n, p in (("FL", FL), ("FR", FR), ("BL", BL), ("BR", BR), ("RF", RF), ("RB", RB))}
    for f in (("FL", "RF", "RB", "BL"), ("FR", "BR", "RB", "RF"), ("FL", "FR", "RF"), ("BL", "RB", "BR"),
              ("FL", "BL", "BR", "FR")):
        bm.faces.new([vs[n] for n in f])
    mb._post(list(vs.values()), "Roof_SG_Navy", None, 0, 1)
    th = math.atan2(zR - zE, H)
    Ls = math.hypot(H, zR - zE)
    rows = int(Ls / 1.9)
    for i in range(rows):
        f0, f1 = i / rows, min(1.0, (i + 1.25) / rows)
        fm = (f0 + f1) / 2
        z = zE + fm * (zR - zE)
        rl = (f1 - f0) * Ls
        for sd in (-1, 1):
            x = sd * H * (1.0 - fm)
            ya = yf + f1 * H
            nx, nz = sd * math.sin(th), math.cos(th)
            mb.box((rl, yb - ya, 0.45), (x + nx * 0.22, (ya + yb) / 2, z + nz * 0.22), (0, sd * th, 0), "Roof_SG_Navy", 0.0)
        xl = 2 * H * (1.0 - f1)
        if xl > 0.6:
            y = yf + fm * H
            mb.box((xl, rl, 0.45), (0.0, y - math.sin(th) * 0.22, z + math.cos(th) * 0.22), (th, 0, 0), "Roof_SG_Navy", 0.0)
    # beiral com ESPESSURA (acabamento): testeira de obsidiana ao longo das aguas laterais (antes a agua terminava em
    # lamina de espessura zero)
    for sd in (-1, 1):
        x0_, x1_ = sorted((sd * (H - 0.45), sd * (H + 0.12)))
        mb.box2((x0_, yf + 0.2, zE - 0.75), (x1_, yb, zE + 0.32), OB, 0.0)
    mb.beam((0.0, yr, zR + 0.4), (0.0, yb, zR + 0.4), 1.1, 1.1, "Roof_SG_Navy", 0.0)
    mb.beam((0.0, yr, zR + 1.05), (0.0, yb, zR + 1.05), 0.5, 0.3, SV, 0.0)          # cumeeira de prata
    for sd in (-1, 1):
        mb.beam((0.0, yr, zR + 0.4), (sd * H, yf, zE + 0.4), 0.9, 0.9, "Roof_SG_Navy", 0.0)
        mb.beam((0.0, yr, zR + 0.95), (sd * H, yf, zE + 0.95), 0.4, 0.28, SV, 0.0)   # rincoes de prata
    return zR + 0.9


def dormer_front(mb, W, uc, z0, hw, h):
    """frente da lucarna (03.16): empena de pedra fechando o triangulo do telhadinho, TESTEIRA de obsidiana nas 2
    aguas (bochechas = as faces laterais da caixa) e florao no fecho"""
    panel(mb, W, [(uc - hw, z0), (uc + hw, z0), (uc, z0 + h)], -0.3, 0.05, CM_)
    for sg in (-1, 1):
        a, b = _P(W, uc + sg * (hw + 0.3), 0.18, z0 - 0.2), _P(W, uc, 0.18, z0 + h + 0.2)
        mb.beam(a, b, 0.34, 0.3, OB, 0.0)
    pt = _P(W, uc, 0.1, 0.0)
    finial(mb, pt[0], pt[1], z0 + h + 0.1, 0.6)


def roofs():
    rng = random.Random(5301)
    mb = MB("SG_Cas_Telhados", "04_CASTLE", rng, detail="near")
    # telhado da nave: navy ingreme, fiadas de ardosia, cumeeira escura + crista de prata
    ridge = nave_roof(mb)
    # OVERHAUL 03 (03.16): CRISTA de ferro continua (fita recortada em ritmo A-B) com florao a cada 8, no lugar da
    # fileira de hastes com cruzinhas
    ya_, yb_ = OY0 + CLR + 3.0, OY1 - 2.0
    Wr = ((0.0, 0.0), (0.0, 1.0), (1.0, 0.0))
    top = []
    nstep = int((yb_ - ya_) / 0.5)
    for i in range(nstep + 1):
        yy = ya_ + (yb_ - ya_) * i / nstep
        ph = (yy - ya_) % 2.0
        hz = 0.55 + 0.55 * (1.0 - abs(ph - 1.0)) ** 2
        top.append((yy, ridge + 0.2 + hz))
    panel(mb, Wr, [(ya_, ridge + 0.15), (yb_, ridge + 0.15)] + list(reversed(top)), -0.06, 0.06, BI)
    mb.box2((-0.1, ya_, ridge + 0.1), (0.1, yb_, ridge + 0.3), BI, 0.0)
    yy = ya_ + 4.0
    while yy < yb_ - 1.0:
        EM._lathe(mb, (0.0, yy, ridge + 0.2), [(0.1, 0.0), (0.16, 0.3), (0.28, 0.9), (0.12, 1.3), (0.2, 1.55),
                                              (0.0, 2.3)], BI, 6, 0.0)
        yy += 8.0
    # fleche (agulha fina) no cruzeiro da nave, mais alta (coroa densa da ref v2)
    fy = (OY0 + OY1) / 2 + 6.0
    shaft(mb, 0.0, fy, 2.2, 8, ridge - 2.0, ridge + 4.0, OB, 22.5)
    spire(mb, 0.0, fy, 2.4, 8, ridge + 4.0, 16.0, "Roof_SG_Navy", 22.5, rings=(0.4,))
    finial(mb, 0.0, fy, ridge + 19.5, 1.5)                   # overhaul 03: florao de prata (a ponta de neon saiu)
    # lucarnas escuras no telhado da nave (quebram a agua comprida; sem luz: sotao)
    for yy in [OY0 + (OY1 - OY0) * f_ for f_ in (0.215, 0.5, 0.785)]:     # 04b: ritmo pela nave nova
        for s in (-1, 1):
            xo = s * 13.0
            zr = CLR_TOP + NAVE_RISE * (1.0 - 13.0 / CLR) + 0.9
            mb.box2((min(xo, xo - s * 5.0), yy - 2.0, zr - 3.0), (max(xo, xo - s * 5.0), yy + 2.0, zr + 3.4),
                    "Stone_SG_Castle", 0.0)
            mb.gable_roof(xo - s * 2.5, yy, 5.0, 4.0, zr + 3.4, 2.8, "Roof_SG_Navy", thick=0.45, over=0.35, axis="X",
                          shingles=False, ridge_m="Roof_SG_Navy")
            Wl = ((xo, 0.0), (0.0, 1.0), (s * 1.0, 0.0))
            dormer_front(mb, Wl, yy, zr + 3.4, 2.0, 2.8)
            window(mb, Wl, yy, 0.8, zr - 0.2, zr + 2.0, 1.0, 0.02, 0.0, glass_m="shutter", mullion=False,
                   fw=0.35, dp=0.25, sill=False)
    # meia-aguas das naves laterais (da cornija ao clerestorio)
    # acabamento: a agua nasce ATRAS do parapeito da cornija (calha), nao atravessa mais o parapeito e a cornija
    for s in (-1, 1):
        xo, xi = s * (OX1 - 1.0), s * CLR
        zo, zi = EAVE + 0.4, AISLE_HI
        L2 = math.hypot(xi - xo, zi - zo)
        tilt = math.atan2(zi - zo, xi - xo)
        rows = int(L2 / 1.9)
        for k in range(rows):
            f0, f1 = k / rows, min(1.0, (k + 1.3) / rows)
            ax, az = xo + (xi - xo) * f0, zo + (zi - zo) * f0
            bx, bz = xo + (xi - xo) * f1, zo + (zi - zo) * f1
            mb.box((math.hypot(bx - ax, bz - az), OY1 - OY0 - 2.0, 0.6), ((ax + bx) / 2, (OY0 + OY1) / 2, (az + bz) / 2 + 0.3),
                   (0, -tilt, 0), "Roof_SG_Navy", 0.0)
    # lucarnas QUENTES nas meia-aguas das naves laterais (ritmo por vao: no eixo dos vitrais, entre os arcobotantes)
    for yy in WIN_Y:
        for s in (-1, 1):
            xo2 = s * (OX1 - 1.0 - 0.283 * (OX1 - 1.0 - CLR))      # 04b: mesma posicao relativa na agua
            f = (OX1 - 1.0 - abs(xo2)) / (OX1 - 1.0 - CLR)
            zr = EAVE + 0.4 + f * (AISLE_HI - EAVE - 0.4)
            mb.box2((min(xo2, xo2 - s * 4.4), yy - 1.9, zr - 2.6), (max(xo2, xo2 - s * 4.4), yy + 1.9, zr + 2.6),
                    "Stone_SG_Castle", 0.0)
            mb.gable_roof(xo2 - s * 2.2, yy, 4.4, 3.8, zr + 2.6, 2.4, "Roof_SG_Navy", thick=0.45, over=0.35, axis="X",
                          shingles=False, ridge_m="Roof_SG_Navy")
            dormer_front(mb, ((xo2, 0.0), (0.0, 1.0), (s * 1.0, 0.0)), yy, zr + 2.6, 1.9, 2.4)
            lancet_win(mb, ((xo2, 0.0), (0.0, 1.0), (s * 1.0, 0.0)), yy, zr + 0.85, 1.6, 0.9, 0.0, glass=WW_M,
                       dp=0.3, fw=0.2)
    mb.finish()


# ------------------------------------------------------------------ 3. fachada: porta, arquivoltas, emblema monumental
def facade(banners):
    rng = random.Random(5401)
    mb = MB("SG_Cas_Fachada", "04_CASTLE", rng, detail="hero")
    CM = "Stone_SG_Castle"
    fy = OY0                                              # face externa da fachada (y 40)
    W = ((0.0, fy), (1.0, 0.0), (0.0, -1.0))              # u = x, t = para fora (-y)
    zd = Z + DH                                           # verga 70,2
    # porche em degraus (3 ordens) - nada invade o vao de 16. Arquivoltas alternando pedra violeta / obsidiana
    orders = 3
    ow = 1.2
    arch_m = (VI, OB, VI)
    # OVERHAUL 03 (03.15): colunelos de 12 lados com BASE ATICA (plinto + toro + escocia + toro) e CAPITEL EM CESTO
    # com abaco chanfrado (torno), em cantaria de remate (le a forma); ARQUIVOLTAS com perfil (toro na aresta de dentro,
    # cavete, filete) varridas ao longo da ogiva; timpano REBAIXADO com moldura em toro; pinaculos do kit
    base_prof = [(0.62, 0.0), (0.62, 0.1), (0.54, 0.2), (0.58, 0.3), (0.46, 0.42), (0.42, 0.5), (0.46, 0.56),
                 (0.5, 0.62), (0.4, 0.74)]
    cap_prof = [(0.4, 0.0), (0.47, 0.07), (0.4, 0.15), (0.44, 0.35), (0.56, 0.6), (0.66, 0.74)]
    arch_prof = [(0.6, 0.0), (-0.6, 0.0), (-0.6, 1.08), (-0.46, 1.1), (-0.3, 0.98), (-0.12, 0.94), (0.02, 1.08),
                 (0.2, 1.3), (0.44, 1.3), (0.6, 1.1)]
    for k in range(orders):
        t0, t1 = k * ow, (k + 1) * ow
        for s in (-1, 1):
            u0 = s * (DW / 2 + k * ow)
            u1 = s * (DW / 2 + orders * ow + 2.0)
            panel(mb, W, rect(min(u0, u1), max(u0, u1), ZB, zd), t0, t1, CM)
            panel(mb, W, rect(min(u0, u1), max(u0, u1), ZB, SOC), t1 - 0.05, t1 + 0.12, OB)
            cp = _P(W, s * (DW / 2 + k * ow + 0.1), t0 + 0.1, 0.0)
            mb.box((1.34, 1.34, 0.36), (cp[0], cp[1], Z + 0.18), (0, 0, 0), OB, 0.06)
            EM._lathe(mb, (cp[0], cp[1], Z + 0.36), base_prof, CAPL, 12, 0.0)
            mb.cyl(0.4, zd - 1.2 - (Z + 1.1), (cp[0], cp[1], (Z + 1.1 + zd - 1.2) / 2), (0, 0, 0), arch_m[k], 12,
                   bevel=0.0)
            EM._lathe(mb, (cp[0], cp[1], zd - 1.2), cap_prof, CAPL, 12, 0.0)
            mb.box((1.42, 1.42, 0.2), (cp[0], cp[1], zd - 0.36), (0, 0, 0), CAPL, 0.05)
            mb.box((1.3, 1.3, 0.16), (cp[0], cp[1], zd - 0.08), (0, 0, 0), CAPL, 0.04)
        path = [_P(W, u, t0, z) for u, z in ogive(0.0, DW / 2, zd, ARCH_RISE, d=(k + 0.5) * ow)]
        mb.sweep(path, [(a * ow / 1.2, b) for a, b in arch_prof], arch_m[k], True, None, up=(0.0, -1.0, 0.0))
    # capiteis (friso de obsidiana na verga, filete de prata)
    pw = DW / 2 + orders * ow + 2.0
    panel(mb, W, rect(-pw, pw, zd, zd + 0.9), -0.1, orders * ow + 0.4, OB)
    panel(mb, W, rect(-pw, pw, zd + 0.9, zd + 1.15), -0.1, orders * ow + 0.5, SV)
    # massa do porche ate a empena (wimperg) BAIXA (rebaixada na v2 para o janelao aparecer), apontando para o janelao
    outer_all = ogive(0.0, DW / 2, zd, ARCH_RISE, d=orders * ow)
    gab_top = zd + ARCH_RISE + orders * ow + 1.0
    panel(mb, W, [(pw, zd), (pw, zd + 6.0), (0.0, gab_top), (-pw, zd + 6.0), (-pw, zd)] + outer_all,
          orders * ow - 0.6, orders * ow + 0.2, CM)
    # timpano rebaixado (fundo 0,3 atras da ordem de dentro) + moldura em toro ao longo da ogiva e da verga
    panel(mb, W, [(-DW / 2, zd), (DW / 2, zd)] + list(reversed(ogive(0.0, DW / 2, zd, ARCH_RISE))), -0.3, -0.12, OB)
    roll = [(0.2 * math.cos(2 * math.pi * i / 6), 0.2 * math.sin(2 * math.pi * i / 6)) for i in range(6)]
    mb.sweep([_P(W, u, 0.05, z) for u, z in ogive(0.0, DW / 2, zd, ARCH_RISE, d=-0.2)], roll, VI, True, None,
             up=(0.0, -1.0, 0.0))
    mb.box((DW - 0.4, 0.4, 0.4), _P(W, 0.0, 0.05, zd + 0.2), (0, 0, 0), VI, 0.05)
    EM.plaque(mb, mb, mb, mb, _P(W, 0.0, 0.1, zd + 4.3), -math.pi / 2, 2.9)
    # PORTA (OVERHAUL 04.01, 2026-09-29, agente do setor 04): a porta mais importante da ilha ganha FOLHAS. Com a parede
    # de 4, uma folha de 8 aberta entraria no salao: cada folha e DOBRADICA (2 panos de ~3,3 articulados) e fica aberta
    # e dobrada contra a ombreira, dentro do vao (vao livre de 14,5; colisao propria). Tabuas verticais com junta,
    # 3 ferragens em T com cravos, dobradicas de pino visiveis na dobra (vista de fora) e no batente (vista de dentro),
    # argola de puxar. SOLEIRA em pedras (fiada do porche e fiada do vao, juntas desencontradas, filetes de prata) e
    # INTRADORSO com 3 caixotoes rasos (grelha de obsidiana, degrau interno, fundo de pedra violeta).
    yf0 = fy - orders * ow
    for (ya_, yb_), cuts in (((yf0 + 0.3, fy - 0.2), (-8.0, -4.0, 0.0, 4.0, 8.0)),
                             ((fy + 0.2, HY0), (-8.0, -2.7, 2.7, 8.0))):
        for xa_, xb_ in zip(cuts, cuts[1:]):
            ga = 0.03 if xa_ > -DW / 2 + 1e-6 else 0.0
            gb = 0.03 if xb_ < DW / 2 - 1e-6 else 0.0
            mb.box2((xa_ + ga, ya_, Z - 0.3), (xb_ - gb, yb_, Z + 0.06), OB, 0.04)
    mb.box2((-DW / 2, yf0 - 0.12, Z - 0.3), (DW / 2, yf0 + 0.3, Z + 0.09), SV, 0.03)
    mb.box2((-DW / 2, fy - 0.2, Z - 0.3), (DW / 2, fy + 0.2, Z + 0.08), SV, 0.03)
    # intradorso em caixotoes: fundo violeta, grelha de obsidiana (2 longarinas + 4 travessas), degrau interno
    zi = zd
    mb.box2((-DW / 2, fy, zi - 0.06), (DW / 2, HY0, zi + 0.02), VI, 0.0)
    for ya_, yb_ in ((fy, fy + 0.5), (HY0 - 0.5, HY0)):
        mb.box2((-DW / 2, ya_, zi - 0.44), (DW / 2, yb_, zi - 0.04), OB, 0.05)
    for xc_ in (-DW / 2 + 0.25, -2.58, 2.58, DW / 2 - 0.25):
        mb.box2((xc_ - 0.25, fy + 0.5, zi - 0.44), (xc_ + 0.25, HY0 - 0.5, zi - 0.04), OB, 0.05)
    for xa_, xb_ in ((-7.5, -2.83), (-2.33, 2.33), (2.83, 7.5)):
        ya_, yb_ = fy + 0.5, HY0 - 0.5
        for p0_, p1_ in (((xa_, ya_), (xb_, ya_ + 0.22)), ((xa_, yb_ - 0.22), (xb_, yb_)),
                         ((xa_, ya_ + 0.22), (xa_ + 0.22, yb_ - 0.22)), ((xb_ - 0.22, ya_ + 0.22), (xb_, yb_ - 0.22))):
            mb.box2((p0_[0], p0_[1], zi - 0.24), (p1_[0], p1_[1], zi - 0.05), OB, 0.03)
    # folhas dobradas: pano A (junto da ombreira, articulado no batente do lado do salao) e pano B (face a vista,
    # articulado ao A na frente); o fecho de cada folha fica do lado do salao
    LT = 0.34
    LY0, LY1 = fy + 0.62, HY0 - 0.05
    lz0, lz1 = Z + 0.1, zd - 0.5
    hz = (Z + 2.4, Z + 8.9, zd - 2.7)
    for s in (-1, 1):
        xo = s * (DW / 2 - 0.02)
        xa = xo - s * LT
        xb = xa - s * 0.03
        xc = xb - s * LT
        mb.box2((min(xo, xa), LY0, lz0), (max(xo, xa), LY1, lz1), WD, 0.04)
        nb = 4
        wbd = (LY1 - LY0) / nb
        for i in range(nb):
            y0_ = LY0 + i * wbd + (0.025 if i else 0.0)
            y1_ = LY0 + (i + 1) * wbd - (0.025 if i < nb - 1 else 0.0)
            mb.box2((min(xb, xc), y0_, lz0), (max(xb, xc), y1_, lz1), WD, 0.05)
        # travessas de tras (cinta) nas pontas de cima e de baixo do pano B
        for zz in (lz0 + 0.5, lz1 - 0.5):
            mb.box2((min(xc, xc - s * 0.06), LY0 + 0.1, zz - 0.3), (max(xc, xc - s * 0.06), LY1 - 0.1, zz + 0.3), WD,
                    0.03)
        rs = (0, -s * math.pi / 2, 0)                    # eixo z local -> para o centro do vao
        xf = xc - s * 0.06                               # face das ferragens
        for zz in hz:
            # ferragem em T: tira ate perto do fecho + travessa vertical na dobra
            mb.box2((min(xf, xf - s * 0.07), LY0 + 0.2, zz - 0.16), (max(xf, xf - s * 0.07), LY1 - 0.45, zz + 0.16),
                    BI, 0.02)
            mb.box2((min(xf, xf - s * 0.08), LY0 + 0.14, zz - 0.72), (max(xf, xf - s * 0.08), LY0 + 0.44, zz + 0.72),
                    BI, 0.02)
            mb.cyl(0.13, 0.24, (xf - s * 0.07 - 0.0 * s, LY1 - 0.45, zz), (0, 0, 0), BI, n=8, bevel=0.0)
            for q in range(5):
                yy = LY0 + 0.75 + q * (LY1 - LY0 - 1.5) / 4.0
                mb.cyl(0.075, 0.08, (xf - s * 0.11, yy, zz), rs, BI, n=6, r2=0.035, bevel=0.0)
            for zz2 in (zz - 0.5, zz + 0.5):
                mb.cyl(0.07, 0.08, (xf - s * 0.12, LY0 + 0.29, zz2), rs, BI, n=6, r2=0.035, bevel=0.0)
            # dobradicas de pino: na dobra A|B (frente) e no batente (lado do salao)
            mb.cyl(0.13, 0.95, (xa - s * 0.015, LY0 - 0.08, zz), (0, 0, 0), BI, n=8, bevel=0.0)
            mb.cyl(0.15, 1.05, (xo - s * 0.1, LY1 + 0.02, zz), (0, 0, 0), BI, n=8, bevel=0.0)
            mb.box2((min(xo, xo + s * 0.02), LY1 - 0.9, zz - 0.18), (max(xo, xo + s * 0.02), LY1 + 0.05, zz + 0.18),
                    BI, 0.0)
        # argola: espelho redondo + aro pendurado
        yr, zr_ = LY1 - 0.8, Z + 4.7
        mb.cyl(0.3, 0.07, (xf - s * 0.035, yr, zr_), rs, BI, n=10, bevel=0.0)
        mb.cyl(0.1, 0.16, (xf - s * 0.1, yr, zr_), rs, BI, n=8, bevel=0.0)
        rp = [(xf - s * 0.14, yr + 0.36 * math.sin(2 * math.pi * k / 12), zr_ - 0.36 + 0.36 * math.cos(2 * math.pi * k / 12))
              for k in range(13)]
        mb.tube(rp, 0.055, BI, 6)
        col_box2("SG_CasDoorLeaf", (min(xo, xc) - 0.02, LY0, Z - 0.5), (max(xo, xc) + 0.02, LY1, lz1))
    for s in (-1, 1):
        a = (s * pw, zd + 6.0)
        b = (0.0, gab_top)
        L2 = math.hypot(b[0] - a[0], b[1] - a[1])
        tilt = math.atan2(b[1] - a[1], b[0] - a[0])
        mb.box((L2 + 0.6, 1.4, 0.8), _P(W, (a[0] + b[0]) / 2, orders * ow + 0.1, (a[1] + b[1]) / 2 + 0.35),
               (0, -tilt, 0), OB, 0.0)
        mb.box((L2 + 0.4, 0.3, 0.25), _P(W, (a[0] + b[0]) / 2, orders * ow + 0.85, (a[1] + b[1]) / 2 + 0.78),
               (0, -tilt, 0), SV, 0.0)
        # pinaculos do porche: pilar de pedra violeta de QUINAS CHANFRADAS com soco em talude, 2 cordoes e o
        # pinaculo do kit (antes: caixa lisa + piramide de 4 lados)
        px = s * (pw - 0.4)
        pc = _P(W, px, orders * ow + 0.4, 0.0)
        FP.frustum(mb, (pc[0], pc[1], Z - 0.3), 2.3, 2.3, 1.75, 1.75, SOC - Z + 0.3, OB)
        mb.prism(sq_ch(pc[0], pc[1], 0.8, 0.22), SOC, zd + 8.0, VI)
        for zz in (zd - 0.1, zd + 4.0):
            frustum(mb, pc[0], pc[1], 1.05, 0.9, 8, zz, zz + 0.4, OB, 22.5)
        pinnacle(mb, pc[0], pc[1], zd + 8.0, 0.8, hb=2.2, hn=6.2, body_m=VI)
    gp = _P(W, 0.0, orders * ow - 0.2, 0.0)
    finial(mb, gp[0], gp[1], gab_top - 0.2, 1.4)
    # --- JANELAO ogival violeta (ref v2): a "boca de luz" da fachada, entre a verga da porta e o emblema. Uma das POUCAS
    # janelas violeta (funcao). Acabamento: vidro com chumbo RECUADO atras de uma moldura funda de obsidiana (1,3) e de
    # uma ordem externa de pedra violeta (1,6); RENDILHADO de obsidiana (3 maineis, 2 subarcos ogivais e oculo no
    # timpano, travessa) em vez da grade reta; peitoril com pingadeira.
    tf = 0.3                                              # face do campo violeta do emblema (t 0..0,3)
    window(mb, W, 0.0, JAN_A, JAN_SILL, JAN_SPRING, JAN_RISE, tf + 0.15, tf, glass_m=VG, frame_m=OB, fw=1.0,
           dp=1.3, mullion=False, sill=True, sill_m=OB, lead=True)
    jv0 = ogive(0.0, JAN_A, JAN_SPRING, JAN_RISE, d=1.0)
    jv1 = ogive(0.0, JAN_A, JAN_SPRING, JAN_RISE, d=1.55)
    panel(mb, W, jv0 + list(reversed(jv1)), tf - 0.05, tf + 1.6, VI)
    for s in (-1, 1):
        u0j, u1j = sorted((s * (JAN_A + 1.0), s * (JAN_A + 1.55)))
        panel(mb, W, rect(u0j, u1j, JAN_SILL - 0.55, JAN_SPRING), tf - 0.05, tf + 1.6, VI)
    td0, td1 = tf + 0.05, tf + 0.85                        # rendilhado: atras da moldura, na frente do vidro
    zsub = JAN_SPRING + 3.6
    for uj, ztop in ((-3.5, zsub - 0.2), (0.0, JAN_SPRING + 0.9), (3.5, zsub - 0.2)):
        panel(mb, W, rect(uj - 0.25, uj + 0.25, JAN_SILL, ztop), td0, td1, OB)
    panel(mb, W, rect(-JAN_A, JAN_A, JAN_TR - 0.22, JAN_TR + 0.22), td0, td1, OB)
    for uc_ in (-3.5, 3.5):
        i0 = ogive(uc_, 3.25, JAN_SPRING, 3.6, n=6)
        i1 = ogive(uc_, 3.25, JAN_SPRING, 3.6, d=0.45, n=6)
        panel(mb, W, i0 + list(reversed(i1)), td0, td1, OB)
    C = (0.0, fy, JAN_SPRING + 4.45)
    ring(mb, C, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0), 1.4, 1.85, td0, td1, OB, 16)
    # torrinhas-contraforte da fachada (marcam o corpo central) com agulhas
    for x, y, r in FAC_TURRETS:
        socle(mb, x, y, r, 8, ZB, SOC, 22.5, e=0.6)
        shaft(mb, x, y, r, 8, SOC, CLR_TOP + 10.0, CM, 22.5)
        tower_ashlar(mb, x, y, r, 8, 22.5, SOC + 0.45, Z + 7.7)
        for zz, hh in ((EAVE - 1.0, 1.4), (CLR_TOP - 0.9, 1.2)):
            band(mb, x, y, r, 8, zz, 22.5, h=hh, e=0.45)
        band(mb, x, y, r, 8, WIN_SILL - 1.6, 22.5, h=1.05, e=0.45)
        frustum(mb, x, y, r + 0.6, r + 0.6, 8, CLR_TOP + 10.0, CLR_TOP + 11.4, OB, 22.5)
        frustum(mb, x, y, r + 0.75, r + 0.75, 8, CLR_TOP + 11.0, CLR_TOP + 11.4, VI, 22.5)
        spire(mb, x, y, r, 8, CLR_TOP + 11.4, 20.0, "Roof_SG_Navy", 22.5, rings=(0.36,))
        finial(mb, x, y, CLR_TOP + 31.0, 1.4)
        slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), 270.0), EAVE + 10.0, 3.2, 0.9)
        col_box("SG_CasFacTurret", (2 * r, 2 * r, 20.0), (x, y, Z + 9.5))
    _fin(mb)
    emblem_monument()
    # colisao do porche (fora do vao)
    for s in (-1, 1):
        u0, u1 = s * (DW / 2 + ow), s * pw          # a 1a ordem (rente ao vao) fica sem colisao: vao livre de 16
        col_box2("SG_CasPorch", (min(u0, u1), fy - orders * ow, Z - 0.5), (max(u0, u1), fy, zd + 7.0))
    light("L_SGCas_Door", "POINT", (0.0, fy - 5.0, Z + 11.0), 700.0, WARM, 0.6)


def emblem_monument():
    """O SIMBOLO DA ORDEM na fachada: emblema monumental (sg_emblem) num medalhao de obsidiana com contorno de
    energia violeta, sobre um campo de pedra violeta emoldurado por um grande arco ogival de prata que abraca o porche.
    E o primeiro ponto que o olho encontra vindo da praca (a verga do portao da muralha e baixa para nao tapa-lo)."""
    mb = MB("SG_Cas_Emblema", "04_CASTLE", random.Random(5451), detail="hero")
    fy = OY0
    W = ((0.0, fy), (1.0, 0.0), (0.0, -1.0))
    zd = Z + DH
    arc = ogive(0.0, ARC_A, ARC_ZR, ARC_RISE, n=10)
    # campo violeta dentro do arco (acima da verga do porche)
    panel(mb, W, [(-ARC_A, zd), (ARC_A, zd)] + list(reversed(arc)), 0.0, 0.3, VI)
    # arco de prata (banda interna) + banda externa de obsidiana; ombreiras descem ate o soco
    a_sv = ogive(0.0, ARC_A, ARC_ZR, ARC_RISE, d=0.9, n=10)
    a_ob = ogive(0.0, ARC_A, ARC_ZR, ARC_RISE, d=2.6, n=10)
    panel(mb, W, arc + list(reversed(a_sv)), -0.05, 1.0, SV)
    panel(mb, W, a_sv + list(reversed(a_ob)), -0.05, 0.95, OB)
    for s in (-1, 1):
        u0, u1 = sorted((s * ARC_A, s * (ARC_A + 0.9)))
        u2, u3 = sorted((s * (ARC_A + 0.9), s * (ARC_A + 2.6)))
        panel(mb, W, rect(u0, u1, SOC + 0.35, ARC_ZR), -0.05, 1.0, SV)
        panel(mb, W, rect(u2, u3, SOC + 0.35, ARC_ZR), -0.05, 0.95, OB)
        # capitel da ombreira (onde o arco nasce)
        panel(mb, W, rect(min(u0, u2) - 0.3, max(u1, u3) + 0.3, ARC_ZR - 1.0, ARC_ZR), -0.05, 1.3, OB)
        # luminaria baixa no pe da ombreira: caixa de obsidiana chanfrada, aro de prata e o vidro em violeta SUAVE
        # rebaixado dentro do aro (acabamento: antes era uma placa de neon forte em cima de uma caixa)
        ux = s * (ARC_A + 1.3)
        mb.box((3.0, 1.6, 0.56), _P(W, ux, 1.9, Z + 0.28), (0, 0, 0), OB, 0.08)
        mb.box((2.6, 1.2, 0.1), _P(W, ux, 1.9, Z + 0.6), (0, 0, 0), SV, 0.0)
        mb.box((2.2, 0.8, 0.1), _P(W, ux, 1.9, Z + 0.58), (0, 0, 0), VS, 0.0)
    # medalhao: disco de obsidiana, contorno de energia (neon violeta) e aro de obsidiana
    C = (0.0, fy, EMB_Z)
    U, V, N = (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, -1.0, 0.0)
    R0 = EMB_R * 1.2
    disc(mb, C, U, V, N, R0, 0.3, 1.0, OB, 32)
    ring(mb, C, U, V, N, R0, R0 + 0.55, 0.3, 0.9, VS, 32)
    ring(mb, C, U, V, N, R0 + 0.55, R0 + 1.25, 0.3, 1.1, OB, 32)
    EM.emblem(mb, mb, mb, _P(W, 0.0, 1.0, EMB_Z), -math.pi / 2, EMB_R, depth=1.2, monumental=True,
              glow=VG_EMB)   # 15: lavanda clara (SG_Rune_Glow) virava branco no bloom
    _fin(mb)
    light("L_SGCas_Emblem", "POINT", (0.0, fy - 9.0, Z + 40.0), 950.0, VIOLET, 1.0)


# ------------------------------------------------------------------ 4. torres da fachada + torrinhas de tras
def towers(banners):
    rng = random.Random(5501)
    mb = MB("SG_Cas_Torres", "04_CASTLE", rng, detail="near")
    CM = "Stone_SG_Castle"
    for x, y, r, top in L.FRONT_TOWERS:
        rot = 22.5
        ap = r * math.cos(math.pi / 8)
        s = 1 if x > 0 else -1
        # BASE: soco de obsidiana + cordao de prata / CORPO: pedra do castelo com faixas de obsidiana nos andares /
        # COROAMENTO: varanda com mata-caes de obsidiana, parapeito com remate violeta, agulha preto-violeta com aneis
        socle(mb, x, y, r, 8, ZB, Z + 3.4, rot, e=1.1)
        shaft(mb, x, y, r, 8, Z + 3.4, top, CM, rot)
        tower_ashlar(mb, x, y, r, 8, rot, Z + 3.85, Z + 10.2)          # overhaul 03: zona do olho em fiadas
        band(mb, x, y, r, 8, Z + 15.0, rot, h=1.0, e=0.4)
        band(mb, x, y, r, 8, top - 14.0, rot, h=1.2, e=0.5)
        parapet_ring(mb, x, y, r, 8, EAVE + 0.4, 1.9, OB, rot)                     # varanda com ameias de obsidiana
        # (acabamento: as floreiras com pinheiro da varanda sairam - ficavam metade no ar, fora do anel do parapeito)
        out_phi = 0.0 if s > 0 else 180.0
        # janelas: fileiras ritmicas QUENTES (vida) nos andares; ultimo andar em lancetas de energia violeta
        for phi in (out_phi, 270.0 + 45.0 * s, 90.0 - 45.0 * s):
            slit(mb, face_frame(x, y, ap, phi % 360.0), Z + 18.0, 3.4, 0.9)
        for phi in (out_phi, 270.0 + 45.0 * s, 90.0 - 45.0 * s):
            slit(mb, face_frame(x, y, ap, phi % 360.0), Z + 28.0, 3.0, 0.85)
        for phi in (270.0, out_phi, 270.0 + 45.0 * s, 90.0 - 45.0 * s):
            slit(mb, face_frame(x, y, ap, phi % 360.0), EAVE + 5.0, 3.6, 0.9)
        for phi in (270.0, out_phi, 270.0 + 45.0 * s):
            slit(mb, face_frame(x, y, ap, phi % 360.0), Z + 52.0, 3.0, 0.85)
        for phi in (270.0, out_phi, 90.0):
            Wf = face_frame(x, y, ap, phi)
            window(mb, Wf, 0.0, 1.3, top - 11.5, top - 5.6, 2.2, -0.02, 0.0, glass_m=WW_M, mullion=True,
                   fw=0.55, dp=0.35)
        parapet_ring(mb, x, y, r, 8, top, 2.6, OB, rot)
        spire(mb, x, y, r - 1.3, 8, top + 2.6, FT_SPIRE, "Roof_SG_Navy", rot, rings=(0.3, 0.62))
        finial(mb, x, y, top + FT_SPIRE + 2.3, 2.4)
        # lucarnas na agulha (4 faces, luz violeta) e pinaculos nos cantos do parapeito
        for k in range(4):
            phi = math.radians(90.0 * k)
            d = (r - 1.3) * 0.62
            lx, ly = x + d * math.cos(phi), y + d * math.sin(phi)
            lz = top + 2.6 + FT_SPIRE * 0.24
            mb.box((1.6, 2.2, 3.2), (lx, ly, lz + 1.6), (0, 0, phi), OB, 0.0)
            # janelinha da lucarna: vidro quente com moldura (antes: placa de neon violeta)
            lancet_win(mb, face_frame(lx, ly, 0.8, math.degrees(phi)), 0.0, lz + 0.5, 2.1, 0.8, 0.0, glass=WW_M,
                       dp=0.25, fw=0.18, bar=False)
            dormer_roof(mb, lx, ly, lz + 3.2, 2.2, 1.6, 2.2, phi)
        for k in range(4):
            a = math.radians(rot + 45.0 + 90.0 * k)
            px, py = x + (r + 0.4) * math.cos(a), y + (r + 0.4) * math.sin(a)
            hp = 10.5 if k % 2 == 0 else 8.0                   # alturas alternadas (coroa densa da ref v2)
            pinnacle(mb, px, py, top + 2.6, 0.62, hb=2.4, hn=hp - 1.0, body_m=OB, crock=False, rot=a)
        # estandarte da ordem pendurado sob a varanda, na face que olha a praca (o uplight de neon no pe saiu: competia
        # com a arquitetura)
        # OVERHAUL 12 (12.05/16.02): o estandarte das torres da fachada SAIU - repetia o par das torres do portao (que
        # marcam o portao e o eixo) e o emblema monumental da fachada no mesmo quadro
        ngon_col("SG_CasTower", x, y, 8, r, Z - 0.5, top, rot)
    for x, y, r in BACK_TURRETS:
        socle(mb, x, y, r, 8, ZB, Z + 3.0, 22.5, e=0.7)
        shaft(mb, x, y, r, 8, Z + 3.0, CLR_TOP + 4.0, CM, 22.5)
        tower_ashlar(mb, x, y, r, 8, 22.5, Z + 3.45, Z + 9.6)
        band(mb, x, y, r, 8, EAVE - 1.0, 22.5, e=0.4)
        parapet_ring(mb, x, y, r, 8, CLR_TOP + 4.0, 1.8, OB, 22.5)
        spire(mb, x, y, r, 8, CLR_TOP + 5.8, 25.0, "Roof_SG_Navy", 22.5, rings=(0.36,))
        finial(mb, x, y, CLR_TOP + 30.4, 1.6)
        for phi in (90.0, 0.0 if x > 0 else 180.0):
            slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), phi), Z + 22.0, 3.2, 0.8)
            slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), phi), Z + 38.0, 3.0, 0.8)
            slit(mb, face_frame(x, y, r * math.cos(math.pi / 8), phi), EAVE + 6.0, 3.2, 0.8)
        ngon_col("SG_CasTower", x, y, 8, r, Z - 0.5, EAVE, 22.5)
    mb.finish()


def standards(banners):
    """estandartes da ordem (sg_emblem.banner): roxo profundo, barra negra, debrum DOURADO, emblema; ritmo simetrico
    (2 nas torres do portao da muralha; as 2 das torres da fachada sairam no overhaul 12)"""
    # acabamento: 4 estandartes (os 2 que ladeavam o janelao sairam - repetiam o emblema monumental logo acima) e
    # SUPORTE de verdade: cada verga presa na parede por 2 bracos de ferro negro com escora e chapa de fixacao
    mb = MB("SG_Cas_Estandartes", "04_CASTLE", random.Random(5801), detail="near")
    for top, yaw, w, h, off in banners:
        EM.banner(mb, mb, mb, mb, top, yaw, w, h, trim=EM.BRONZE)   # debrum de bronze (14.04; era dourado)
        fx, fy_ = math.cos(yaw), math.sin(yaw)
        ux, uy = math.sin(yaw), -math.cos(yaw)
        for sd in (-1, 1):
            du = sd * (w / 2 + 0.25)
            wx, wy = top[0] + ux * du - fx * off, top[1] + uy * du - fy_ * off     # ponto na face da parede
            mb.beam((wx - fx * 0.1, wy - fy_ * 0.1, top[2]), (wx + fx * (off + 0.2), wy + fy_ * (off + 0.2), top[2]),
                    0.22, 0.26, BI, 0.0)
            mb.beam((wx - fx * 0.05, wy - fy_ * 0.05, top[2] - 1.3), (wx + fx * off * 0.85, wy + fy_ * off * 0.85,
                    top[2] - 0.1), 0.16, 0.16, BI, 0.0)
            mb.box((0.7, 0.12, 1.9), (wx + fx * 0.02, wy + fy_ * 0.02, top[2] - 0.6), (0, 0, yaw + math.pi / 2), BI, 0.0)
    _fin(mb)


# ------------------------------------------------------------------ 04b: base da torre-coroa com a abside do trono
# janelas da abside vistas de fora: (face em graus, meia largura, peitoril, nascenca, flecha) acima do piso (= sg_hall)
APSE_WINDOWS_OUT = [(90.0, 3.4, 10.5, 25.5, 4.2), (30.0, 1.9, 14.0, 23.5, 2.8), (150.0, 1.9, 14.0, 23.5, 2.8)]


def crown_shell():
    """as 2 metades (anti-horario) da CASCA da base da torre-coroa: por fora o 12-gono (vertices a 15 + 30k graus), por
    dentro o presbiterio (x = +-APSE_HW, desde a face interna da nave) e o meio hexagono da abside"""
    x, y, r = CR_X, CR_Y, CR_R
    ap = r * math.cos(math.pi / 12)
    V = lambda a, rr=r: (x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a)))
    hw, ri = L.APSE_HW, L.APSE_R
    x315 = V(315.0)
    east = [(hw, OY1 - 0.02), (x315[0], OY1 - 0.02), x315, V(345.0), V(15.0), V(45.0), V(75.0), (x, y + ap),
            (x, y + ri * math.sin(math.radians(60.0))), V(60.0, ri), V(0.0, ri)]
    west = [(2 * x - px, py) for px, py in reversed(east)]
    return [SL.ccw(east), SL.ccw(west)]


def crown_ring(mb, prof, m):
    """anel com perfil [(raio, z)] (poligono fechado) em volta da torre-coroa SO nas faces de fora (vertices de 315 a
    225 graus passando pelo norte): as 3 faces de dentro da nave nao ganham soco/cordao (estariam no salao)"""
    x, y, n = CR_X, CR_Y, 12
    angs = [315.0 + 30.0 * k for k in range(10)]                    # 315 ... 585 (= 225)
    bm = mb.bm
    rows = [[bm.verts.new((x + rr * math.cos(math.radians(a)), y + rr * math.sin(math.radians(a)), z)) for rr, z in prof]
            for a in angs]
    fs = []
    np_ = len(prof)
    for i in range(len(angs) - 1):
        A, B = rows[i], rows[i + 1]
        for j in range(np_):
            k = (j + 1) % np_
            fs.append(bm.faces.new((A[j], A[k], B[k], B[j])))
    fs.append(bm.faces.new(rows[0]))
    fs.append(bm.faces.new(list(reversed(rows[-1]))))
    _faces_ok(mb, fs)
    mb._post([v for r_ in rows for v in r_], m, None, 0, 1)


# ------------------------------------------------------------------ 5. torre-coroa (heroi)
def crown():
    rng = random.Random(5601)
    mb = MB("SG_Cas_Coroa", "04_CASTLE", rng, detail="near")
    CM = "Stone_SG_Castle"
    x, y, r, top = CR_X, CR_Y, CR_R, CR_TOP
    n = 12
    rot = 15.0
    ap = r * math.cos(math.pi / n)
    z1 = Z + 90.0                                          # 1o corpo ate ~142 (04b: +18 com a nave)
    r2 = r - 1.6
    ap2 = r2 * math.cos(math.pi / n)
    # SETOR 04b: a base da torre guarda a ABSIDE do trono (presbiterio + meio hexagono, sg_layout.apse_poly) aberta
    # para a nave pelo arco triunfal. Ate o teto do salao a torre e uma CASCA (2 metades: fora = 12-gono, dentro =
    # abside); acima, o fuste cheio. As 3 faces de dentro da nave (240/270/300 graus) nao existem por fora.
    shell_halves = crown_shell()
    for poly in shell_halves:
        mb.prism(poly, ZB, CEIL, CM)
    shaft(mb, x, y, r, n, CEIL, z1, CM, rot)
    crown_ring(mb, [(r - 0.3, ZB), (r + 1.3, ZB), (r + 0.25, Z + 4.0), (r - 0.3, Z + 4.0)], OB)          # soco
    crown_ring(mb, [(r - 0.3, Z + 3.95), (r + 0.42, Z + 3.95), (r + 0.42, Z + 4.4), (r - 0.3, Z + 4.4)], SV)
    band(mb, x, y, r, n, EAVE - 1.0, rot, e=0.7)
    # OVERHAUL 03: zona do olho no terraco - silhar em fiadas nas faces que o jogador alcanca (as de dentro da nave
    # ficam lisas) e cordao com pingadeira a +10
    side = 2 * r * math.sin(math.pi / n)
    for k in range(n):
        phi = rot + 360.0 * k / n + 180.0 / n
        W = face_frame(x, y, ap, phi)
        if _P(W, 0.0, 0.0, 0.0)[1] < OY1 + 1.5:
            continue
        ashlar(mb, W, -side / 2 + 0.05, side / 2 - 0.05, Z + 4.4, Z + 9.7, 0.0, PL=2.9, phase=0.7 * (k % 2))
    h_ = 0.9
    crown_ring(mb, [(r - 0.3, Z + 9.8), (r + 0.05, Z + 9.8), (r + 0.45, Z + 9.8 + h_ * 0.28), (r + 0.45, Z + 9.8 + h_ * 0.7),
                    (r + 0.1, Z + 9.8 + h_), (r - 0.3, Z + 9.8 + h_)], OB)
    # contrafortes diagonais em 2 lances com talude e pinaculo do kit no recuo (03.14: a LINHA DE ENERGIA que
    # corria na face de cada um SAIU - era neon colado na arquitetura). 04b: so os 2 de tras (NE/NO); os do sul
    # cairiam na juncao com a nave
    for k in range(2):
        a = math.radians(45.0 + 90.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        bx, by = x + (ap + 1.2) * ca, y + (ap + 1.2) * sa
        mb.box((3.2, 3.0, Z + 40.0 - ZB), (bx, by, (ZB + Z + 40.0) / 2), (0, 0, a), CM, 0.0)
        Wd = ((bx, by), (-sa, ca), (ca, sa))
        ledge(mb, Wd, -1.5, 1.5, [(-1.7, Z + 39.9), (1.6, Z + 39.9), (0.5, Z + 41.0), (-1.7, Z + 41.0)], CM)
        mb.box((2.4, 2.6, z1 - Z - 40.9), (bx - 0.4 * ca, by - 0.4 * sa, (Z + 40.9 + z1) / 2), (0, 0, a), CM, 0.0)
        mb.box((4.0, 3.8, Z + 4.0 - ZB), (bx, by, (ZB + Z + 4.0) / 2), (0, 0, a), OB, 0.0)
        mb.box((4.1, 3.9, 0.4), (bx, by, Z + 4.2), (0, 0, a), SV, 0.0)
        Wd0 = ((bx + 1.6 * ca, by + 1.6 * sa), (-sa, ca), (ca, sa))
        ashlar(mb, Wd0, -1.5, 1.5, Z + 4.4, Z + 9.7, 0.0, PL=1.9, phase=0.5)
        ledge(mb, Wd0, -1.9, 1.9, drip(Z + 10.1, 0.45), OB)
        mb.box((2.2, 2.4, 8.0), (bx - 0.6 * ca, by - 0.6 * sa, z1 + 4.0), (0, 0, a), CM, 0.0)
        pinnacle(mb, bx - 0.6 * ca, by - 0.6 * sa, z1 + 8.0, 1.0, hb=2.2, hn=9.0, crock=False, rot=a)
        col_box("SG_CasCrown", (3.2, 3.0, 20.0), (bx, by, Z + 9.5), (0, 0, a))
    # 04b: as janelas da ABSIDE aparecem por fora (vitral da lua ao norte, lancetas de luar a NE/NO: o mesmo vidro de
    # luar do salao) + fileira quente nos andares de cima (vida) e energia violeta no andar alto
    for phi, a_, zs_, zr_, ri_ in APSE_WINDOWS_OUT:
        window(mb, face_frame(x, y, ap, phi), 0.0, a_, Z + zs_, Z + zr_, ri_, -0.02, 0.0, glass_m="Glass_SGHallMoon",
               mullion=a_ > 2.0, fw=0.6, dp=0.5, hood=True)
    for phi in (0.0, 180.0):
        slit(mb, face_frame(x, y, ap, phi), Z + 24.0, 3.2, 0.9)
    for phi in (30.0, 90.0, 150.0):
        slit(mb, face_frame(x, y, ap, phi), Z + 36.0, 3.0, 0.85)
    for phi in (0.0, 30.0, 60.0, 90.0, 120.0, 150.0, 180.0):
        Wf = face_frame(x, y, ap, phi)
        window(mb, Wf, 0.0, 1.1, Z + 60.0, Z + 67.5, 1.9, -0.02, 0.0, glass_m=VG, mullion=False, fw=0.5, dp=0.45)
    frustum(mb, x, y, r + 0.9, r + 0.9, n, z1, z1 + 1.4, OB, rot)
    frustum(mb, x, y, r + 1.05, r + 1.05, n, z1 + 1.0, z1 + 1.4, VI, rot)
    # fileira de pinaculos do kit na cornija do 1o corpo (alturas alternadas: ritmo A-B)
    for k in range(n):
        adeg = rot + 360.0 * k / n
        if k % 3 == 1:                                        # os contrafortes diagonais ja tem pinaculo proprio
            continue
        a = math.radians(adeg)
        px, py = x + (r + 0.35) * math.cos(a), y + (r + 0.35) * math.sin(a)
        hp = 6.2 if k % 2 == 0 else 8.4
        pinnacle(mb, px, py, z1 + 1.4, 0.7, hb=2.4, hn=hp, body_m=OB, crock=False, rot=a)
    # 2o corpo recuado: campanario com lancetas altas; faces alternadas em energia violeta (ritmo), o resto veneziana
    zc = top - 6.0
    shaft(mb, x, y, r2, n, z1 + 1.4, zc, CM, rot)
    for k in range(n):
        phi = (rot + 360.0 * k / n + 180.0 / n) % 360.0
        Wf = face_frame(x, y, ap2, phi)
        lit = int(round(phi)) % 60 == 30
        window(mb, Wf, 0.0, 1.5, z1 + 16.0, zc - 12.0, 2.6, -0.02, 0.0,
               glass_m=VG if lit else "shutter", mullion=True, fw=0.6, dp=0.4)
    band(mb, x, y, r2, n, z1 + 10.0, rot, h=1.0, e=0.5)
    # coroamento: mata-caes de obsidiana + parapeito ate o topo da alvenaria (178) com remate violeta
    parapet_ring(mb, x, y, r2, n, zc, top - zc, OB, rot, merlons=False)
    # coroa de agulhas: 4 torrinhas-pinaculo grandes nas diagonais + 8 pinaculos do kit (alturas alternadas). As pontas
    # de neon SAIRAM (03.14/15.04): remate = florao de prata
    for k in range(n):
        a = math.radians(rot + 360.0 * k / n)
        if k % 3 == 1:                                        # vertices a 45, 135, 225, 315 graus
            rr = r2 - 0.6
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            shaft(mb, px, py, 2.4, 8, top - 1.0, top + 11.0, CM, 22.5)
            band(mb, px, py, 2.4, 8, top + 3.6, 22.5, h=0.7, e=0.3)
            frustum(mb, px, py, 2.9, 2.9, 8, top + 11.0, top + 12.2, OB, 22.5)
            frustum(mb, px, py, 3.05, 3.05, 8, top + 11.8, top + 12.2, VI, 22.5)
            spire(mb, px, py, 2.5, 8, top + 12.2, 17.0, "Roof_SG_Navy", 22.5, rings=(0.3, 0.62))
            finial(mb, px, py, top + 28.6, 1.5)
            slit(mb, face_frame(px, py, 2.4 * math.cos(math.pi / 8), math.degrees(a)), top + 5.4, 3.6, 0.8, m=VG)
        else:
            rr = r2 + 0.3
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            hs = 12.5 if k % 2 == 0 else 10.0                 # alturas alternadas: floresta de agulhas (ref v2)
            shaft(mb, px, py, 1.3, 6, top, top + 5.0, OB, 0.0)
            pinnacle(mb, px, py, top + 5.0, 1.15, hb=1.6, hn=hs, crock=False, rot=a)
    # flecha principal (sai direto do coroamento) com 4 lucarnas violeta e aneis de prata, ate CROWN_SPIRE_TOP;
    # no topo, o florao de prata (o orbe de neon saiu: brilho da coroa so nas lancetas)
    rs = 10.2
    sh = L.CROWN_SPIRE_TOP - 3.2 - top
    spire(mb, x, y, rs, n, top, sh, "Roof_SG_Navy", rot, flare=0.12, rings=(0.3, 0.55, 0.78))
    for phi in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(phi)
        d = rs * 0.66
        lz = top + sh * 0.2
        lx, ly = x + d * math.cos(a), y + d * math.sin(a)
        mb.box((2.4, 2.8, 4.0), (lx, ly, lz + 2.0), (0, 0, a), OB, 0.0)
        lancet_win(mb, face_frame(lx, ly, 1.2, phi), 0.0, lz + 0.8, 2.6, 1.0, 0.0, glass=VG, frame_m=VI, dp=0.3,
                   fw=0.22, bar=False)
        dormer_roof(mb, lx, ly, lz + 4.0, 2.8, 2.4, 2.6, a)
    mb.rod((x, y, top + sh - 0.4), (x, y, L.CROWN_SPIRE_TOP - 2.6), 0.3, SV, 6)
    finial(mb, x, y, L.CROWN_SPIRE_TOP - 2.8, 2.2)
    mb.box((0.3, 2.6, 0.3), (x, y, top + sh + 1.3), (0, 0, 0), SV, 0.0)
    mb.finish()
    # colisao: casca da abside (as 2 metades, por dentro do contorno), teto da abside e o fuste cheio acima do salao
    for poly in shell_halves:
        SL.col_poly("SG_CasCrown", poly, Z - 0.5, CEIL, step=2.0, mode="inter")
    col_box2("SG_CasCrown", (-L.APSE_HW, HY1, Z + L.APSE_KEY), (L.APSE_HW, CR_Y + L.APSE_R, CEIL))
    ngon_col("SG_CasCrown", x, y, n, r, CEIL, top, rot)


def dormer_roof(mb, x, y, z0, w, d, h, a):
    """telhadinho de lucarna em 2 aguas com a cumeeira PARA FORA (empena na face, a = rumo da face) e testeira de
    obsidiana: substitui a piramide de 4 lados em cima das lucarnas. w = largura na face, d = profundidade"""
    ca, sa = math.cos(a), math.sin(a)
    tx, ty = -sa, ca

    def P(u, t, zz):
        return (x + ca * t + tx * u, y + sa * t + ty * u, zz)
    bm = mb.bm
    hw, hd = w / 2 + 0.2, d / 2 + 0.25
    V = [bm.verts.new(P(u, t, zz)) for u, t, zz in ((-hw, -hd, z0), (hw, -hd, z0), (hw, hd, z0), (-hw, hd, z0),
                                                    (0.0, -hd, z0 + h), (0.0, hd, z0 + h))]
    fs = [bm.faces.new((V[0], V[1], V[2], V[3])), bm.faces.new((V[0], V[3], V[5], V[4])),
          bm.faces.new((V[1], V[4], V[5], V[2])), bm.faces.new((V[0], V[4], V[1])), bm.faces.new((V[3], V[2], V[5]))]
    _faces_ok(mb, fs)
    mb._post(V, NAVY, None, 0, 1)
    for sg in (-1, 1):
        mb.beam(P(sg * (hw + 0.05), hd + 0.02, z0 - 0.05), P(0.0, hd + 0.02, z0 + h + 0.12), 0.36, 0.3, OB, 0.0)
    pt = P(0.0, hd - 0.1, 0.0)
    finial(mb, pt[0], pt[1], z0 + h - 0.1, 0.7)


# ------------------------------------------------------------------ 6. alas (NAO entraveis: sem porta nenhuma)
def wings():
    rng = random.Random(5701)
    mb = MB("SG_Cas_Alas", "04_CASTLE", rng, detail="near")
    CM = "Stone_SG_Castle"
    # --- ala oeste sobre o terreno bravo: soco de pedra escura, corpo, telhado de ardosia ingreme, lucarnas
    x0, y0, x1, y1 = WW
    rect_frustum(mb, x0, y0, x1, y1, ZT, Z - 1.0, 3.2, 1.2, OB)
    mb.box2((x0, y0, Z - 1.0), (x1, y1, WW_EAVE), CM, 0.0)
    mb.box2((x0 - 0.6, y0 - 0.6, Z - 1.0), (x1 + 0.6, y1 + 0.6, SOC), OB, 0.0)
    mb.box2((x0 - 0.75, y0 - 0.75, SOC - 0.05), (x1 + 0.75, y1 + 0.75, SOC + 0.35), SV, 0.0)
    mb.box2((x0 - 0.4, y0 - 0.4, Z + 16.0), (x1 + 0.4, y1 + 0.4, Z + 17.0), OB, 0.0)
    mb.box2((x0 - 0.7, y0 - 0.7, WW_EAVE - 1.1), (x1 + 0.7, y1 + 0.7, WW_EAVE), OB, 0.0)
    cx = (x0 + x1) / 2
    w = x1 - x0
    rise = 20.0
    mb.gable_roof(cx, (y0 + y1) / 2, w, y1 - y0, WW_EAVE, rise, "Roof_SG_Navy", thick=0.8, over=1.4, axis="Y",
                  ridge_m=SV)
    for yy, sg in ((y0, -1), (y1, 1)):
        mb.gable_wall(cx, yy + sg * 0.4, w, WW_EAVE, rise, 0.8, "Y", CM)
    # janelas quentes (2 andares) nas 4 faces; nenhuma porta
    # (acabamento: faixas de janela recuadas das torres de canto - as das pontas entravam nas torres)
    faces = [(((x1, 0.0), (0.0, 1.0), (1.0, 0.0)), y0 + 5.0, y1 - 5.0),
             (((x0, 0.0), (0.0, 1.0), (-1.0, 0.0)), y0 + 9.5, y1 - 9.5),
             (((0.0, y0), (1.0, 0.0), (0.0, -1.0)), x0 + 10.0, x1 - 11.0),
             (((0.0, y1), (1.0, 0.0), (0.0, 1.0)), x0 + 10.0, x1 - 11.0)]
    # OVERHAUL 03: zona do olho nas faces que o jogador ve do beco / da entrada do beco / do terraco (silhar em volta
    # das janelas do terreo, cordao com pingadeira acima delas); a face oeste (terreno bravo) fica lisa
    ash_span = {0: (y0 + 0.6, y1 - 0.6), 2: (x1 - 16.0, x1 - 0.6), 3: (x1 - 16.0, x1 - 0.6)}
    for fi, (W, u0, u1) in enumerate(faces):
        nwin = max(2, int((u1 - u0) / 9.0) + 1)
        excl = []
        for k in range(nwin):
            u = u0 + (u1 - u0) * k / (nwin - 1)
            excl.append((u - 1.9, u + 1.9, Z + 5.2, Z + 11.0))
            for j, zz in enumerate((Z + 6.0, Z + 20.0)):
                lit = (k + j + fi) % 3 != 2                    # ref v2: maioria quente (vida), venezianas pontuais
                window(mb, W, u, 1.0, zz, zz + 3.0, 1.4, 0.02, 0.0,
                       glass_m="Window_Warm" if lit else "shutter", mullion=False, fw=0.45, dp=0.62, sill=True)
        if fi in ash_span:
            ua_, ub_ = ash_span[fi]
            ashlar(mb, W, ua_, ub_, SOC + 0.72, Z + 11.2, 0.0, excl, phase=0.3 * fi)
            ledge(mb, W, ua_ - 0.3, ub_ + 0.3, drip(Z + 11.5, 0.5), OB)
    for yy in (y0 + 14.0, (y0 + y1) / 2, y1 - 14.0):
        dx0 = x1 - 1.0
        mb.box2((dx0 - 5.0, yy - 2.2, WW_EAVE + 0.5), (dx0, yy + 2.2, WW_EAVE + 6.0), CM, 0.0)
        mb.gable_roof(dx0 - 2.5, yy, 5.0, 4.4, WW_EAVE + 6.0, 3.0, "Roof_SG_Navy", thick=0.5, over=0.4, axis="X",
                      shingles=False, ridge_m="Roof_SG_Navy")
        lancet_win(mb, ((dx0, 0.0), (0.0, 1.0), (1.0, 0.0)), yy, WW_EAVE + 2.4, 2.3, 1.0, 0.0, glass=WW_M,
                   dp=0.3, fw=0.22)
    col_box2("SG_CasWingW", (x0, y0, Z - 0.5), (x1, y1, WW_EAVE))
    # --- ala leste: corpo baixo no beco (deixa as janelas da nave livres acima), telhado de ardosia
    ex0, ey0, ex1, ey1 = EW
    mb.box2((ex0, ey0, ZB), (ex1, ey1, EW_EAVE), CM, 0.0)
    mb.box2((ex0, ey0 - 0.4, ZB), (ex1 + 0.6, ey1 + 0.4, SOC), OB, 0.0)
    mb.box2((ex0, ey0 - 0.55, SOC - 0.05), (ex1 + 0.75, ey1 + 0.55, SOC + 0.35), SV, 0.0)
    mb.box2((ex0, ey0 - 0.6, EW_EAVE - 1.0), (ex1 + 0.6, ey1 + 0.6, EW_EAVE), OB, 0.0)
    mb.gable_roof((ex0 + ex1) / 2, (ey0 + ey1) / 2, ex1 - ex0, ey1 - ey0, EW_EAVE, 5.0, "Roof_SG_Navy", thick=0.6,
                  over=0.8, axis="Y", ridge_m=SV)
    for yy in (ey0 + 0.3, ey1 - 0.3):
        mb.gable_wall((ex0 + ex1) / 2, yy, ex1 - ex0, EW_EAVE, 5.0, 0.6, "Y", CM)
    W = ((ex1, 0.0), (0.0, 1.0), (1.0, 0.0))
    excl = []
    for k in range(6):
        u = ey0 + 9.0 + k * (ey1 - ey0 - 18.0) / 5
        excl.append((u - 2.1, u + 2.1, Z + 3.3, Z + 9.9))
        window(mb, W, u, 1.1, Z + 4.0, Z + 7.6, 1.5, 0.02, 0.0, glass_m="Window_Warm" if k % 3 != 1 else "shutter",
               mullion=False, fw=0.45, dp=0.62)
        mb.box((0.5, 1.4, 1.2), (ex1 + 0.3, u, EW_EAVE - 1.8), (0, 0, 0), OB, 0.0)
    # OVERHAUL 03: silhar em volta das janelas (face do patio da dungeon) e nas empenas de ponta (sul: patio; norte:
    # terraco), ate a cornija
    ashlar(mb, W, ey0 + 0.2, ey1 - 0.2, SOC + 0.72, EW_EAVE - 1.1, 0.0, excl, phase=0.5)
    for yy, sg in ((ey0, -1.0), (ey1, 1.0)):
        We = ((0.0, yy), (1.0, 0.0), (0.0, sg))
        ashlar(mb, We, ex0 + 0.3, ex1 - 0.2, SOC + 0.72, EW_EAVE - 1.1, 0.0, (), phase=0.8)
    col_box2("SG_CasWingE", (ex0 - 3.4, ey0, Z - 0.5), (ex1, ey1, EW_EAVE + 2.0))
    # --- torres das alas (agulhas escalonadas ate a coroa)
    for ti, (tx, ty, tr, ttop, sph) in enumerate(WING_TOWERS):
        sph += 4.0                                             # gabarito maior das agulhas secundarias (ref v2)
        socle(mb, tx, ty, tr, 8, ZT, SOC, 22.5, e=1.0)
        shaft(mb, tx, ty, tr, 8, SOC, ttop, CM, 22.5)
        band(mb, tx, ty, tr, 8, (Z + ttop) / 2, 22.5, h=1.0, e=0.45)
        parapet_ring(mb, tx, ty, tr, 8, ttop, 2.0, OB, 22.5)   # ameias de obsidiana (terracos da ref v2)
        spire(mb, tx, ty, tr - 0.4, 8, ttop + 2.0, sph, "Roof_SG_Navy", 22.5, rings=(0.36,))
        mb.rod((tx, ty, ttop + 2.0 + sph - 0.3), (tx, ty, ttop + 4.6 + sph), 0.2, SV, 6)
        apx = tr * math.cos(math.pi / 8)
        for phi in (0.0, 90.0, 180.0, 270.0):
            slit(mb, face_frame(tx, ty, apx, phi), ttop - 12.0, 3.4, 1.0)
        for phi in (0.0, 180.0):
            slit(mb, face_frame(tx, ty, apx, phi), ttop - 23.0, 3.0, 0.9)
        ngon_col("SG_CasWingTower", tx, ty, 8, tr, Z - 0.5, ttop, 22.5)
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    banners = []
    muralha(banners)
    stairs()
    nave()
    roofs()
    facade(banners)
    towers(banners)
    crown()
    wings()
    standards(banners)
    light("L_SGCas_Gate", "POINT", (0.0, L.WALL_Y0 - 5.0, Z + 9.0), 600.0, WARM, 0.6)
    light("L_SGCas_EastGap", "POINT", (EG_X, L.WALL_Y0 - 4.0, Z + 7.0), 380.0, WARM, 0.5)
