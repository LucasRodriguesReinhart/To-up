# sg_village - VILA da Ilha 3 (Shadow Garden): praca central + fonte, ruas com meio-fio, escada P1->P2 (so visual),
# 11 casas gothicas de meia-enxaimel (NAO entraveis: sem porta nenhuma), poucos postes de ferro no eixo e na rua da
# praca. So ambientacao (o ultimo na hierarquia): poucas pecas, cada uma com funcao de leitura.
# Substitui sg_blockout.village. Colisao propria: corpo de cada casa (caixa), torreao, postes. O piso, a escada, a
# bacia da fonte e as guardas sao do sg_col (congelado).
# REFINAMENTO 2026-09-28 (identidade da ordem): o eixo nobre (rua do P2 e patio) e desenhado pelo sg_court (lajes de
# marmore negro, borda de obsidiana, fio violeta); as ruas secundarias viram paralelepipedo escuro com meio-fio claro;
# a fonte leva o EMBLEMA da ordem (sg_emblem) no lugar da lua solta; o fio do eixo atravessa a praca ate a fonte; o par
# de postes do topo da escada P1P2 vira o arco de ferro negro (transicao praca -> vila alta); 2 estandartes pequenos
# da ordem nas casas do P2 que ladeiam o eixo; floreiras baixas de obsidiana nas bases das casas.
# REFINAMENTO v2 2026-09-28 (ref2_plaza): a PRACA GANHA O MARCO - estatua encapuzada de manto longo (pedra escura,
# lamina apontada para baixo, ~6 de altura) sobre a taca da fonte (sem colisao nova alem da bacia); 4 lanternas
# douradas (sg_emblem.lantern_pedestal, SO Neon) na borda da bacia externa; os postes soltos viram
# sg_emblem.lantern_post dourados (as MESMAS 3 luzes reais, realocadas para a lanterna nova); estandartes das casas
# com debrum DOURADO.
# ACABAMENTO 2026-09-29 (passe final, sem casa nova): variacao DIRIGIDA do kit (SPECS: win/frame/ridge/stone_head/
# shutters pelo PAPEL da casa - loja, empena gotica, casa comum); janela encastrada (vidro rente, caixilho de 0,42,
# montantes recuados, peitoril com pingadeira) com cabeca de verdade (capelo de ardosia em maos-francesas / verga com
# fecho / pingadeira gotica / cabeca ogival de madeira) no lugar do "^" de 2 vigas; frestas do torreao com ombreiras e
# cabeca em ponta; agua-furtada com aguas a meia-esquadria + cumeeira (nada de plano atravessando); remate de madeira no
# fecho de cada empena (os guarda-pos morrem num pendural) e cumeeira em rolo nas casas comuns; pote de ferro na
# chamine simples (saiu o bloco de rocha); flores em tufos achatados; SEM neon violeta na vila (fio da praca em pedra,
# medalhoes da bacia retirados, estandartes so no par do P2); a figura da fonte = sg_court.hooded_figure.
# OVERHAUL 02 (vila, 2026-09-29, "zero tolerancia"; a praca/fonte do setor 01 nao muda): o KIT das casas refeito
# (soco em fiadas, silhar + cunhais, janela moldura/recuo/vidro/luz, fiadas de ardosia com escama e cumeeira em pecas,
# chamine e agua-furtada com rufo, torreao com escarpa/cordoes/misulas/agulha em escama, lanterna de suporte fora dos
# montantes e abaixo do beiral), ruas em paralelepipedo com meio-fio chanfrado e terra batida no P2, escada P1P2 com
# banzo continuo e mureta de cantaria, arco de ferro do kit (iron_arch local), estandartes das casas e 20 das 22
# floreiras de chao fora. Detalhe por FACE (fachada completa; laterais e fundos com o mesmo kit simplificado) para caber
# nos 88k.
import math, random
import bmesh
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, Frame, light, octo_col, fm_lib
import sg_layout as L
import sg_emblem as EM

P1, P2, P3 = L.P1, L.P2, L.P3
COLL = "05_VILLAGE"
WIN = "Window_Warm"
WOOD = "Wood_SG_Dark"
STONE = "Stone_SG_Block"
STONE_H = "Stone_SG_Castle"      # v3: pavimento de pedra das casas um valor abaixo (os cunhais ficam no Block)
TRIM = "Stone_SG_Trim"
ROOF = "Roof_SG_Slate"
IRON = "Metal_SG_Iron"
# materiais novos da vila (3 de 5)
M_PL = "Plaster_SGVil"          # reboco apagado (frio-quente, escuro): o Plaster_SG claro demais vira "casa de conto clara"
M_COB = "Stone_SGVilCobble"     # calcamento escuro (desenho radial da praca, faixas das ruas)
M_SHUT = "Wood_SGVilNavy"       # persianas / postigos pintados de navy
fm_lib.MATS.setdefault(M_PL, (fm_lib.S(96, 88, 88), 0.8, 0.0, 0, None, 0.06))
fm_lib.MATS.setdefault(M_COB, (fm_lib.S(72, 76, 92), 0.9, 0.0, 0, None, 0.10))
fm_lib.MATS.setdefault(M_SHUT, (fm_lib.S(36, 42, 72), 0.75, 0.0, 0, None, 0.05))
# 4o material: a flor violeta dessaturada (o mesmo dos canteiros do patio, sg_court) nas floreiras das casas
M_BLOOM = "Leaf_SGPropBloom"
fm_lib.MATS.setdefault(M_BLOOM, (fm_lib.S(98, 66, 132), 0.85, 0.0, 0, None, 0.08))
OBS = "Stone_SG_Obsidian"
BIRON = "Metal_SG_BlackIron"
AXIS_HW = 6.0                   # meia-largura do eixo nobre no P2 (sg_court.PATH_W / 2)
DUN_PLAZA_Y = 33.0              # borda sul da praca de aproximacao da dungeon (sg_dungeon): as ruas do P3 param aqui

CAMS = {
    # 360 da vila (frente, tras, lados) + altura do jogador nas ruas do P1 e do P2
    "CAM_SGVil_Front": ((0.0, -196.0, P1 + 34.0), (0.0, -108.0, P1 + 2.0), 22),
    "CAM_SGVil_Back": ((0.0, -4.0, P3 + 30.0), (0.0, -96.0, P1 + 2.0), 22),
    "CAM_SGVil_SideW": ((-150.0, -96.0, P2 + 26.0), (-40.0, -100.0, P1 + 4.0), 22),
    "CAM_SGVil_SideE": ((160.0, -110.0, P2 + 26.0), (40.0, -100.0, P1 + 4.0), 22),
    "CAM_SGVil_P1W_Back": ((-66.0, -186.0, P1 + 16.0), (-62.0, -128.0, P1 + 6.0), 22),
    "CAM_SGVil_P1E_Back": ((70.0, -186.0, P1 + 16.0), (66.0, -128.0, P1 + 6.0), 22),
    "CAM_SGVil_P2_Back": ((-24.0, -14.0, P2 + 20.0), (-62.0, -52.0, P2 + 5.0), 20),
    "CAM_SGVil_P2E_Back": ((24.0, -14.0, P2 + 20.0), (44.0, -56.0, P2 + 5.0), 20),
    "CAM_SGVil_Turret": ((28.0, -124.0, P1 + 7.0), (50.0, -140.0, P1 + 11.0), 22),
    "CAM_SGVil_Shop": ((-38.0, -126.0, P1 + 5.2), (-52.0, -141.0, P1 + 6.0), 22),
    "CAM_SGVil_Fountain": ((12.0, -146.0, P1 + 7.0), (0.0, -128.0, P1 + 4.0), 24),
    "CAM_SGVil_PH_P1W": ((-22.0, -119.0, P1 + 5.2), (-100.0, -121.0, P1 + 7.0), 22),
    "CAM_SGVil_PH_P1E": ((22.0, -119.0, P1 + 5.2), (100.0, -118.0, P1 + 7.0), 22),
    "CAM_SGVil_PH_Stair": ((0.0, -114.0, P1 + 5.2), (0.0, -40.0, P2 + 9.0), 22),
    "CAM_SGVil_PH_P2E": ((-104.0, -45.0, P2 + 5.2), (40.0, -46.0, P2 + 6.0), 22),
    "CAM_SGVil_PH_P2Craft": ((6.0, -46.0, P2 + 5.2), (76.0, -56.0, P2 + 6.0), 22),
    # acabamento 2026-09-29: closes de detalhe (janela/caixilho, telhado/cumeeira/agua-furtada, empena gotica, marco)
    "CAM_SGVil_CU_Window": ((-45.0, -133.5, P1 + 9.6), (-50.5, -141.0, P1 + 9.2), 30),
    "CAM_SGVil_CU_Roof": ((-66.0, -130.0, P1 + 15.0), (-79.0, -142.0, P1 + 11.5), 30),
    "CAM_SGVil_CU_Gable": ((73.0, -121.0, P1 + 6.0), (80.0, -135.0, P1 + 9.0), 26),
    "CAM_SGVil_CU_Statue": ((5.0, -139.0, P1 + 13.5), (0.0, -128.0, P1 + 13.0), 30),
    # OVERHAUL 02 (2026-09-29): closes na altura do jogador - fachada, beiral, fundacao/esquina, chamine e cumeeira
    # (vistas do P2), torreao, rua do P2 com meio-fio e gramado, banzo da escada P1P2
    "CAM_SGVil_OV_Facade": ((-70.0, -124.0, P1 + 5.2), (-78.0, -137.0, P1 + 6.0), 24),
    "CAM_SGVil_OV_Eave": ((-73.5, -131.5, P1 + 5.2), (-80.0, -137.5, P1 + 8.6), 26),
    "CAM_SGVil_OV_Base": ((61.0, -106.5, P1 + 4.2), (66.5, -99.5, P1 + 1.6), 26),
    "CAM_SGVil_OV_Chimney": ((62.0, -84.5, P2 + 5.2), (73.0, -93.0, P1 + 21.0), 26),
    "CAM_SGVil_OV_Ridge": ((-56.0, -84.5, P2 + 5.2), (-68.0, -94.0, P1 + 19.0), 24),
    "CAM_SGVil_OV_Turret": ((35.0, -130.0, P1 + 5.2), (42.4, -140.4, P1 + 8.0), 26),
    "CAM_SGVil_OV_Street": ((-28.0, -40.5, P2 + 5.2), (-44.0, -48.5, P2 + 0.2), 24),
    "CAM_SGVil_OV_Stair": ((-13.0, -104.0, P1 + 5.2), (-8.0, -91.0, P1 + 3.2), 24),
}

# rotas extras: as ruas da vila tem que continuar livres (nada da vila no caminho)
EXTRA_ROUTES = {
    "VIL_RUA_P1_OESTE": ([(-20.0, -118.0), (-60.0, -120.0), (-98.0, -118.0)], P1),
    "VIL_RUA_P1_LESTE": ([(20.0, -118.0), (64.0, -120.0), (108.0, -116.0)], P1),
    "VIL_RUA_P2": ([(-108.0, -45.0), (-40.0, -44.0), (0.0, -45.0), (60.0, -45.0), (70.0, -56.0), (75.0, -60.0)], P2),
    "VIL_EIXO_P2": ([(0.0, -81.0), (0.0, -60.0), (0.0, -30.0)], P2),
    "VIL_PRACA_ANEL": ([(L.PLAZA_C[0] + 12.0 * math.cos(math.radians(a)), L.PLAZA_C[1] + 12.0 * math.sin(math.radians(a)))
                        for a in range(-90, 271, 45)], P1),
}
# a ponta oeste da rua do P2 (mirante sobre a cachoeira) tem guarda
EXTRA_PROBES = [("VIL_P2_mirante_oeste", -112.0, -45.0, P2, -1.0, 0.0, 10.0)]


# ------------------------------------------------------------------ utilidades
def ring_prism(mb, c, r0, r1, n, z0, z1, m, rot0=0.0):
    """anel poligonal (n lados, vertices em rot0 + k*360/n) de r0 a r1, de z0 a z1"""
    bm = mb.bm
    cx, cy = c
    ang = [math.radians(rot0) + 2 * math.pi * k / n for k in range(n)]
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


def ngon(c, r, n, rot0=0.0):
    return [(c[0] + r * math.cos(math.radians(rot0) + 2 * math.pi * k / n),
             c[1] + r * math.sin(math.radians(rot0) + 2 * math.pi * k / n)) for k in range(n)]


def tri_slab(mb, pts, nvec, th, m):
    """triangulo (3 pontos mundo no plano de fora) extrudado para dentro (-nvec) com espessura th"""
    bm = mb.bm
    a = [bm.verts.new(Vector(p)) for p in pts]
    b = [bm.verts.new(Vector(p) - nvec * th) for p in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


def poly_slab(mb, pts2, plane, th, m):
    """poligono 2D (u, v) num plano vertical: plane = (origem, eixo_u, eixo_v, normal) mundo; extruda -normal"""
    o, eu, ev, nv = plane
    bm = mb.bm
    a = [bm.verts.new(o + eu * u + ev * v) for u, v in pts2]
    b = [bm.verts.new(o + eu * u + ev * v - nv * th) for u, v in pts2]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    n = len(pts2)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[j], a[i], b[i], b[j]))
    mb._post(a + b, m, None, 0, 1)


class Face:
    """face de parede no referencial G da casa: centro c (2D local), tangente u, normal n = rot90(u) para fora"""

    def __init__(self, G, c, u, length):
        self.G, self.c, self.u, self.L = G, c, u, length
        self.n = (-u[1], u[0])
        self.yaw = G.a + math.atan2(u[1], u[0])

    def P(self, s, off, z):
        c, u, n = self.c, self.u, self.n
        return self.G.p(c[0] + u[0] * s + n[0] * off, c[1] + u[1] * s + n[1] * off, z)

    def box(self, mb, s, off, z, sx, sy, sz, m, rx=0.0, ry=0.0):
        mb.box((sx, sy, sz), self.P(s, off, z), (rx, ry, self.yaw), m, 0.0)

    def beam(self, mb, s0, z0, s1, z1, off, w, h, m=WOOD):
        mb.beam(self.P(s0, off, z0), self.P(s1, off, z1), w, h, m, 0.0)

    def nvec(self):
        a = self.G.a
        nx, ny = self.n
        return Vector((nx * math.cos(a) - ny * math.sin(a), nx * math.sin(a) + ny * math.cos(a), 0.0))


# ------------------------------------------------------------------ OVERHAUL 02 (2026-09-29, "zero tolerancia"): o KIT
# Nenhuma casa nova, nenhuma casa desenhada do zero: o MESMO kit (soco, silhar, cunhais, caixilho, capelo, ardosia,
# chamine, agua-furtada, lanterna de suporte) com variacao DIRIGIDA pelo papel da casa (SPECS). Regras do kit:
#   - SOCO: 2 fiadas de pedra (a de baixo em blocos com junta, a de cima recuada = ressalto) e um FILETE fino de
#     obsidiana como pingadeira (a bandeja preta lisa saiu);
#   - TERREO DE PEDRA: silhar em relevo raso (0,07) em fiadas de 2 alturas com juntas desencontradas, sobre um nucleo
#     escuro que so aparece nas juntas; cunhais em pedra media (nunca Trim claro) que seguem as fiadas, alternando
#     perna longa/curta e saliencia 0,22/0,15;
#   - JANELA: moldura (caixilho de madeira ou ombreiras de pedra) + RECUO (o vao fica 0,3 a 0,4 atras da face da
#     moldura) + VIDRO (grade de pinazios 2 x 3; o terco de cima e vidro ambar SEM brilho) + LUZ INTERIOR (so os 2/3 de
#     baixo em Neon medio quente, parcialmente coberto por cortina ou bando em ~40% das janelas). Nunca o vao inteiro
#     em Neon, nunca Window_Warm chapado;
#   - TELHADO: fiadas de ardosia em 2 alturas; as baixas com a borda RECORTADA em dentes (so vertices, nenhuma peca por
#     telha): faixas de escama alternadas com faixas lisas; cumeeira em PECAS com junta; remates torneados (madeira nas
#     casas comuns, ferro nas de mestre/loja) no lugar da piramide;
#   - AGUA-FURTADA: rufos de ardosia no encontro das bochechas com a agua principal e guarda-pos com espessura na
#     empena (nada de "casinha enfiada");
#   - CHAMINE: fuste em fiadas de 2 alturas, capa com ressalto duplo, RUFO inclinado no telhado e pote ceramico torneado;
#   - LANTERNA DE SUPORTE: o lugar dela e escolhido ANTES da estrutura aparente (nunca em cima de um montante), abaixo
#     da linha do beiral (antes o braco furava o telhado das casas de 1 pavimento), uma por casa comum e o par so nas
#     lojas; suporte de ferro com mao-francesa curva e remate torneado (sem cubo dourado).
M_ROOM = "SG_VilRoom_Glow"      # luz do comodo: Neon MEDIO quente, so dentro do caixilho (material novo)
fm_lib.MATS.setdefault(M_ROOM, (fm_lib.S(178, 96, 40), 0.5, 0.0, 1.25, fm_lib.S(178, 96, 40), 0.0))
M_CURT = "Cloth_SG_Navy"        # cortina / bando / persiana de pano (base: navy, o mesmo dos postigos)
M_PETAL_C = "Flower_White"      # miolo claro das flores (base)
M_DIRT = "Dirt_SG"              # terra batida junto ao meio-fio (base da ilha)
M_JNT = "Stone_SG_Floor"        # nucleo escuro que so aparece nas juntas
M_ASH = "Stone_SG_Castle_B"     # silhar do terreo de pedra (tom FIXO: sem sorteio de variante)
M_DRESS = "Stone_SG_Block_B"    # cunhais, soco, ombreiras, chamines (tom FIXO, um valor acima do silhar)
M_CAP = "Stone_SG_TrimLow"      # remates perto do jogador (peitoril, verga, cordao, capa): um valor abaixo do Trim
fm_lib.MATS.setdefault(M_CAP, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
M_POT = "Roof_Red"              # pote ceramico da chamine (base)
B_PROP = 0.05                   # chanfro de props de 1 a 3 studs (tabela 16.01)
B_CAST = 0.03                   # metal fundido


def _lathe(mb, c, prof, m, n=8, rot=0.0, closed=False, caps=(True, True)):
    EM._lathe(mb, c, prof, m, n, rot, closed, caps)


def finial_iron(mb, p, s=1.0, m=IRON):
    """remate de ferro torneado (colar, fuste, bulbo, ponta) assentado em p"""
    prof = [(0.26, 0.0), (0.1, 0.22), (0.1, 0.8), (0.22, 1.0), (0.08, 1.25), (0.0, 2.1)]
    _lathe(mb, tuple(p), [(r * s, h * s) for r, h in prof], m, 6, 0.0, caps=(False, True))


def finial_wood(mb, p, s=1.0):
    """pendural torneado de madeira no fecho da empena: gota pendurada, colar, bulbo e ponta (le peca torneada)"""
    prof = [(0.0, -1.3), (0.2, -0.9), (0.15, -0.45), (0.27, -0.2), (0.27, 0.4), (0.2, 0.62), (0.22, 0.95),
            (0.0, 1.45)]
    _lathe(mb, tuple(p), [(r * s, h * s) for r, h in prof], WOOD, 6, math.pi / 6)


def _hood(mb, f, s, z, w):
    """capelo de ardosia sobre a janela de madeira (telhadinho de 1 agua em 2 maos-francesas)"""
    t = math.radians(24.0)
    f.box(mb, s, 0.62, z + 0.32, w + 1.1, 1.05, 0.18, ROOF, rx=-t)
    f.box(mb, s, 0.1, z + 0.52, w + 1.0, 0.2, 0.3, WOOD)                     # testeira colada na parede
    for k in (-1, 1):
        sb = s + k * (w / 2 + 0.44)
        mb.beam(f.P(sb, 0.06, z - 0.42), f.P(sb, 0.86, z + 0.2), 0.14, 0.14, WOOD, 0.0)   # mao-francesa


def window_box(mb, f, s, zlo, w):
    """caixa de janela: corpo de madeira com REBORDO, pendurada sob o peitoril em 2 maos-francesas de ferro.
    JARDINAGEM 2026-09-29: o plantio e o do kit do sg_garden (o mesmo dos canteiros e do gramado) - terra rente ao
    rebordo, laminas atras, folhas PENDENTES transbordando a frente e as flores da CASA (tema dirigido por casa:
    sg_garden.BOX_THEME), no lugar dos lobos-cilindro e dos discos de 5 lados"""
    mb = LIFE[0] or mb
    zb = zlo - 0.72
    f.box(mb, s, 0.72, zb, w + 0.4, 0.56, 0.42, WOOD)
    f.box(mb, s, 0.74, zb + 0.24, w + 0.56, 0.66, 0.09, WOOD)                   # rebordo
    for k in (-1, 1):
        mb.beam(f.P(s + k * (w / 2 - 0.1), 0.05, zb - 0.9), f.P(s + k * (w / 2 - 0.1), 0.86, zb - 0.28), 0.1, 0.1,
                IRON, 0.0)
    import sg_garden as GD
    GD.window_box_planting(mb, f, s, zb, w)


def window(mb, f, s, zlo, w, h, head="hood", shutters=False, planter=False, style="cross", dress="open",
           stone=False, lod=0):
    """janela quente com MOLDURA + RECUO + VIDRO + LUZ INTERIOR:
      - vao a 0,03 da parede (o nucleo); moldura de 0,42 de profundidade -> o vao le recuado;
      - 2/3 de baixo = o comodo aceso (Neon medio, M_ROOM); terco de cima = vidro ambar sem brilho (Window_Warm);
      - grade de pinazios (cross: 2 x 3; lancet: 2 lumes ogivais; trio: 3 lumes de oficina);
      - dress: 'open' | 'curtain' (2 cortinas de pano + bando) | 'blind' (persiana de pano meio descida);
      - stone=True: ombreiras de pedra (M_DRESS) no lugar do caixilho de madeira (terreo de pedra);
      - lod=1 (laterais e fundos): a mesma janela sem capelo/fecho, com 1 so pano e grade 2 x 2."""
    zc = zlo + h / 2
    D = 0.42
    zs = zlo + h * 0.64                                                        # travessa (limite luz / vidro)
    f.box(mb, s, 0.03, (zlo + zs) / 2, w, 0.06, zs - zlo, M_ROOM)
    if not (lod == 1 and dress != "open"):
        f.box(mb, s, 0.03, (zs + zlo + h) / 2, w, 0.06, zlo + h - zs, WIN)
    if dress == "curtain" and lod == 0:
        for k in (-1, 1):
            f.box(mb, s + k * (w / 2 - w * 0.09), 0.08, (zlo + zlo + h) / 2 - 0.1, w * 0.18, 0.05, h - 0.2, M_CURT)
        f.box(mb, s, 0.09, zlo + h - 0.15, w, 0.06, 0.3, M_CURT)                # bando
    elif dress in ("blind", "curtain"):
        f.box(mb, s, 0.08, zlo + h - h * 0.2, w, 0.05, h * 0.4 + 0.02, M_CURT)  # persiana de pano meio descida
    if stone:
        for k in (-1, 1):
            f.box(mb, s + k * (w / 2 + 0.18), 0.22, zc + 0.05, 0.36, 0.44, h + 0.3, M_DRESS)
        if lod == 0:
            f.box(mb, s, 0.12, zlo + h + 0.1, w, 0.24, 0.2, WOOD)              # caixilho (so a verga, fino)
    else:
        f.box(mb, s, D / 2, zlo + h + 0.16, w + 0.64, D, 0.32, WOOD)          # caixilho: topo
        for k in (-1, 1):
            f.box(mb, s + k * (w / 2 + 0.16), D / 2, zc - 0.05, 0.32, D, h + 0.3, WOOD)
    # peitoril de pedra (sai 0,68) com pingadeira por baixo (lod 1: so o peitoril)
    f.box(mb, s, 0.26, zlo - 0.14, w + 0.8, 0.52, 0.2, M_CAP)
    if lod == 0:
        f.box(mb, s, 0.16, zlo - 0.3, w + 0.44, 0.32, 0.14, M_CAP)
    if style == "lancet":
        ra = min(w * 0.55, 1.1)
        nv = f.nvec()
        tri_slab(mb, [f.P(s - w / 2, 0.06, zlo + h), f.P(s + w / 2, 0.06, zlo + h), f.P(s, 0.06, zlo + h + ra)],
                 nv, 0.06, WIN)
        for k in (-1, 1):
            f.beam(mb, s + k * (w / 2 + 0.16), zlo + h + 0.02, s, zlo + h + ra + 0.3, D / 2, D, 0.3)
        f.box(mb, s, 0.12, zc + ra / 2, 0.1, 0.14, h + ra, WOOD)               # montante ate o fecho
        f.box(mb, s, 0.12, zs, w, 0.14, 0.12, WOOD)                            # travessa
        f.box(mb, s, 0.12, zlo + h * 0.32, w, 0.1, 0.07, WOOD)                 # pinazio
        f.box(mb, s, D / 2, zlo + h + ra + 0.42, 0.34, D + 0.06, 0.34, WOOD)   # fecho
    elif style == "trio":
        for k in (-1, 1):
            f.box(mb, s + k * w / 6, 0.12, zc, 0.12, 0.14, h, WOOD)
        f.box(mb, s, 0.12, zs, w, 0.14, 0.12, WOOD)                            # bandeira
        if head and lod == 0:
            _hood(mb, f, s, zlo + h + 0.32, w)
    else:
        if lod < 2:
            f.box(mb, s, 0.12, zc, 0.1, 0.14, h, WOOD)                         # montante
        f.box(mb, s, 0.12, zs, w, 0.14, 0.12, WOOD)                            # travessa
        if lod == 0:
            f.box(mb, s, 0.12, zlo + h * 0.32, w, 0.1, 0.07, WOOD)             # pinazio (grade 2 x 3)
        if head in ("arch", "hood") and lod == 0:
            _hood(mb, f, s, zlo + h + 0.32, w)
        elif head == "lintel":
            f.box(mb, s, 0.25, zlo + h + (0.5 if lod == 0 else 0.3), w + 1.1, 0.5, 0.5 if lod == 0 else 0.6, M_CAP,
                  0.0)
            if lod == 0:
                f.box(mb, s, 0.32, zlo + h + 0.55, 0.5, 0.62, 0.66, M_DRESS)    # fecho
        elif head == "label":
            f.box(mb, s, 0.25, zlo + h + (0.5 if lod == 0 else 0.3), w + 1.3, 0.5, 0.26 if lod == 0 else 0.6, M_CAP)
            if lod == 0:
                for k in (-1, 1):
                    f.box(mb, s + k * (w / 2 + 0.5), 0.25, zlo + h + 0.1, 0.3, 0.5, 0.6, M_CAP)
    if shutters:
        # postigos de tabuas navy (abertos, encostados no silhar), travessas e dobradicas de ferro
        for k in (-1, 1):
            cs = s + k * (w / 2 + 0.4 + w * 0.26 + 0.08)
            f.box(mb, cs, 0.17, zc, w * 0.52, 0.2, h + 0.1, M_SHUT, B_PROP)
            for zz in (zlo + h * 0.22, zlo + h * 0.78):
                f.box(mb, cs, 0.3, zz, w * 0.52 - 0.12, 0.08, 0.2, WOOD)
                f.box(mb, cs - k * (w * 0.26 - 0.2), 0.33, zz, 0.42, 0.08, 0.1, BIRON)
    if planter:
        window_box(mb, f, s, zlo, w)


def shopfront(mb, f, s, w=4.4):
    """vitrine de loja com persiana FECHADA (peitoril de balcao a 2,1: nunca le porta): persiana de RIPAS reais com
    folga e sombra atras, balcao de pedra em 3 consolas, bandeira acesa com pinazios, toldo de ardosia com TESTEIRA
    recortada em ondas e maos-francesas curvas de ferro"""
    z0, z1 = 2.1, 4.3
    f.box(mb, s, 0.06, (z0 + z1) / 2, w, 0.12, z1 - z0, M_JNT)                # fundo escuro (folga das ripas)
    n = 6
    ph = (z1 - z0 - 0.08) / n
    for i in range(n):
        f.box(mb, s, 0.18, z0 + 0.04 + ph * (i + 0.5), w - 0.04, 0.12, ph - 0.07, M_SHUT, rx=-0.12)
    f.box(mb, s, 0.26, z0 + 0.06, w, 0.12, 0.12, WOOD)                         # regua de baixo
    f.box(mb, s, 0.3, z0 + 0.3, 0.3, 0.1, 0.16, BIRON)                         # ferrolho
    # balcao: tampo de pedra em 3 consolas de 2 degraus + pano de pedra recuado
    f.box(mb, s, 0.5, z0 - 0.12, w + 0.8, 1.0, 0.26, M_CAP)
    for u in (-w / 2 + 0.2, 0.0, w / 2 - 0.2):
        f.box(mb, s + u, 0.34, z0 - 0.42, 0.4, 0.66, 0.34, M_DRESS)
        f.box(mb, s + u, 0.22, z0 - 0.78, 0.32, 0.42, 0.38, M_DRESS)
    f.box(mb, s, 0.1, (z0 - 0.25) / 2, w + 0.3, 0.2, z0 - 0.25, M_DRESS)
    for k in (-1, 1):
        f.box(mb, s + k * (w / 2 + 0.25), 0.22, (z0 - 0.3 + z1 + 0.5) / 2, 0.5, 0.4, z1 - z0 + 0.8, WOOD)
    f.box(mb, s, 0.22, z1 + 0.25, w + 1.0, 0.44, 0.5, WOOD)                    # verga
    f.box(mb, s, 0.03, z1 + 0.95, w, 0.06, 0.8, M_ROOM)                        # bandeira acesa
    for k in (-1, 0, 1):
        f.box(mb, s + k * w / 3, 0.12, z1 + 0.95, 0.12, 0.14, 0.8, WOOD)
    f.box(mb, s, 0.2, z1 + 1.45, w + 1.0, 0.36, 0.3, WOOD)
    # toldo de ardosia inclinado + testeira recortada em ondas (poligono, 1 peca) + maos-francesas curvas
    t = math.radians(28.0)
    W2, dep = w + 1.4, 2.0
    zt0 = z1 + 1.95
    f.box(mb, s, dep / 2 * math.cos(t) + 0.05, zt0 - dep / 2 * math.sin(t), W2, dep, 0.2, ROOF, rx=-t)
    ze_ = zt0 - dep * math.sin(t) - 0.08
    oe_ = dep * math.cos(t) + 0.02
    nw = max(4, int(round(W2 / 0.9)))
    pts = [(-W2 / 2, 0.12), (W2 / 2, 0.12)]
    for j in range(2 * nw + 1):
        u = W2 / 2 - j * W2 / (2 * nw)
        pts.append((u, -0.42 if j % 2 == 0 else -0.24))
    nv = f.nvec()
    ev = Vector((0.0, 0.0, 1.0))
    eu = Vector((math.cos(f.yaw), math.sin(f.yaw), 0.0))
    poly_slab(mb, [(p[0], p[1]) for p in pts], (f.P(s, oe_ + 0.1, ze_), eu, ev, nv), 0.1, WOOD)
    prof = [(-0.055, -0.055), (0.055, -0.055), (0.055, 0.055), (-0.055, 0.055)]
    for k in (-1, 1):
        sb = s + k * (w / 2 + 0.3)
        pts3 = []
        for i in range(6):
            a = (math.pi / 2) * i / 5
            pts3.append(tuple(f.P(sb, 0.1 + 1.2 * (1 - math.cos(a)), z1 + 0.25 + 0.85 * math.sin(a))))
        mb.sweep(pts3, prof, IRON, True, None, up=(eu.x, eu.y, 0.0))


WL_S = 0.68                    # escala da lanterna de suporte (a lanterna da ordem do kit, pequena)
LIFE = [None]                  # MB de vestir das casas (lanternas de suporte, caixas de janela): criado no build()


def wall_lantern(mb, f, s, za, base=0.0):
    """lanterna de suporte: espelho de ferro com chanfro, braco reto com MAO-FRANCESA CURVA (varrida), remate
    torneado na ponta e a lanterna da ordem (sg_emblem.lantern_head) pendurada. base = face da parede (0,07 no
    silhar). za = cota do braco (local)."""
    mb = LIFE[0] or mb
    f.box(mb, s, base + 0.07, za - 0.4, 0.44, 0.14, 1.0, IRON, B_CAST)
    mb.beam(f.P(s, base + 0.1, za), f.P(s, base + 1.42, za), 0.12, 0.15, IRON, 0.0)
    prof = [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)]
    eu = Vector((math.cos(f.yaw), math.sin(f.yaw), 0.0))
    pts = []
    for i in range(5):
        a = (math.pi / 2) * i / 4
        pts.append(tuple(f.P(s, base + 0.12 + 0.95 * (1 - math.cos(a)), za - 0.85 + 0.8 * math.sin(a))))
    mb.sweep(pts, prof, IRON, True, None, up=(eu.x, eu.y, 0.0))
    _lathe(mb, tuple(f.P(s, base + 1.46, za - 0.07)), [(0.12, 0.0), (0.12, 0.1), (0.0, 0.26)], IRON, 6)
    top = za - 0.08
    c = f.P(s, base + 1.18, top - 0.2 - 2.05 * WL_S)
    mb.rod(f.P(s, base + 1.18, top), f.P(s, base + 1.18, top - 0.25), 0.04, IRON, 4)
    EM.lantern_head(mb, mb, (c.x, c.y, c.z), f.yaw, WL_S)


def _lantern_slots(Lf, ss, ww, shutters, shop):
    """vaos livres de uma fachada para lanternas de suporte (entre janelas, contando os postigos, senao nas quinas)"""
    if shop:
        e = min(4.6, Lf / 2 - 1.9)          # fora das pernas dos cunhais e longe do toldo
        return [-e, e]
    he = (ww / 2 + 0.4 + ww * 0.52 + 0.1) if shutters else (ww / 2 + 0.4)
    ss = sorted(ss)
    gaps = [(a + b) / 2 for a, b in zip(ss, ss[1:]) if b - a - 2 * he >= 1.2]
    if gaps:
        return gaps
    edge = (max(abs(x) for x in ss) + he) if ss else 0.0
    if Lf / 2 - edge >= 1.2:
        return [-(edge + Lf / 2) / 2, (edge + Lf / 2) / 2]
    return []


def timber_face(mb, f, z0, z1, wins, rng, pattern="chevron", zsill=None, keep=()):
    """estrutura aparente (so do lado de fora): soleira, frechal, montantes e o PREENCHIMENTO dos vaos cheios
    ('chevron' escoras / 'cross' cruzes de Santo Andre / 'studs' montantes cerrados). keep = pontos da face onde vai
    uma lanterna de suporte: ali nao nasce montante (o espelho de ferro assenta no reboco, entre montantes)"""
    Lf = f.L
    f.box(mb, 0.0, 0.15, z0 + 0.22, Lf + 0.3, 0.3, 0.44, WOOD)
    f.box(mb, 0.0, 0.15, z1 - 0.22, Lf + 0.3, 0.3, 0.44, WOOD)
    xs = [-Lf / 2 + 0.22, Lf / 2 - 0.22]
    blocked = []
    for s, w in wins:
        xs += [s - w / 2 - 0.55, s + w / 2 + 0.55]
        blocked.append((s - w / 2 - 0.6, s + w / 2 + 0.6))
    xs = sorted(xs)
    full = list(xs)
    for a, b in zip(xs, xs[1:]):
        mid = (a + b) / 2
        if b - a > 3.4 and not any(b0 < mid < b1 for b0, b1 in blocked):
            near = [k for k in keep if a < k < b]
            if near:
                # o painel da lanterna: 2 montantes ladeando o espelho (o reboco fica livre atras dela)
                for k in near:
                    for d in (-0.95, 0.95):
                        if a + 0.5 < k + d < b - 0.5:
                            full.append(k + d)
            else:
                full.append(mid)
    full = sorted(full)
    for x in full:
        f.box(mb, x, 0.15, (z0 + z1) / 2, 0.42, 0.3, z1 - z0 - 0.3, WOOD)
    za, zb = z0 + 0.45, z1 - 0.45
    for a, b in zip(full, full[1:]):
        mid = (a + b) / 2
        win = [(b0, b1) for b0, b1 in blocked if b0 < mid < b1]
        lan = any(a < k < b for k in keep)
        if win:
            if zsill is None or zsill - za < 0.9 or b - a < 1.0:
                continue
            if pattern == "cross":
                f.beam(mb, a + 0.25, za, b - 0.25, zsill - 0.05, 0.12, 0.2, 0.28)
                f.beam(mb, a + 0.25, zsill - 0.05, b - 0.25, za, 0.12, 0.2, 0.28)
            elif pattern == "studs":
                n = max(1, int((b - a) / 1.2))
                for k in range(1, n):
                    f.box(mb, a + (b - a) * k / n, 0.12, (za + zsill) / 2, 0.26, 0.24, zsill - za, WOOD)
            continue
        if b - a < 1.0:
            continue
        if lan:
            # painel da lanterna: so uma travessa baixa (o reboco em volta do espelho fica limpo)
            f.box(mb, mid, 0.13, z0 + (z1 - z0) * 0.2, b - a, 0.26, 0.3, WOOD)
            continue
        if pattern == "cross":
            f.beam(mb, a + 0.2, za, b - 0.2, zb, 0.15, 0.3, 0.34)
            f.beam(mb, a + 0.2, zb, b - 0.2, za, 0.12, 0.24, 0.34)
        elif pattern == "studs":
            n = max(1, int(round((b - a) / 1.2)))
            for k in range(1, n):
                f.box(mb, a + (b - a) * k / n, 0.12, (z0 + z1) / 2, 0.3, 0.24, z1 - z0 - 0.5, WOOD)
            f.box(mb, mid, 0.13, (z0 + z1) / 2 - 0.2, b - a, 0.26, 0.3, WOOD)
        elif mid < 0:
            f.beam(mb, a + 0.2, za, b - 0.2, zb, 0.15, 0.3, 0.38)
        else:
            f.beam(mb, a + 0.2, zb, b - 0.2, za, 0.15, 0.3, 0.38)


def win_slots(Lf, w, n=None, margin=1.6):
    n = n if n is not None else max(1, int((Lf - 2 * margin + 1.2) / (w + 2.4)))
    step = (Lf - 2 * margin) / n
    return [-Lf / 2 + margin + step * (k + 0.5) for k in range(n)]


# ------------------------------------------------------------------ pedra: soco, silhar, cunhais
COURSES = (1.1, 0.8)            # as 2 alturas de fiada do terreo de pedra (silhar e cunhais seguem a mesma escala)
def socle(mb, G, x0, x1, y0, y1, back="-y"):
    """soco em 2 fiadas: a de baixo (-0,4..0,5) em blocos com junta de 0,08 sobre nucleo escuro, sai 0,42; a de cima
    (0,5..0,88) recuada 0,14 (ressalto) e continua; filete de obsidiana (0,88..0,98) como pingadeira"""
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
    W, D = x1 - x0, y1 - y0
    mb.box((W + 0.76, D + 0.76, 0.9), G.p(cxm, cym, 0.05), G.r(), M_JNT, 0.0)
    for key, (ax, ay), ln, ux in (("-y", (x0 - 0.08, y0 - 0.42), W + 1.0, 1),
                                  ("+y", (x0 - 0.08, y1 + 0.42), W + 1.0, 1),
                                  ("-x", (x0 - 0.42, y0 - 0.34), D + 0.68, 0),
                                  ("+x", (x1 + 0.42, y0 - 0.34), D + 0.68, 0)):
        nb = max(1, int(round(ln / 3.0))) if key == {"-y": "+y", "+y": "-y", "-x": "+x", "+x": "-x"}[back] else 1
        step = ln / nb
        for k in range(nb):
            a0 = k * step + (0.04 if k else 0.0)
            a1 = (k + 1) * step - (0.04 if k < nb - 1 else 0.0)
            bv = B_PROP if key == {"-y": "+y", "+y": "-y", "-x": "+x", "+x": "-x"}[back] else 0.0
            if ux:
                c = G.p(ax - 0.42 + (a0 + a1) / 2, ay, 0.05)
                mb.box((a1 - a0, 0.16, 0.9), c, G.r(), M_DRESS, bv)
            else:
                c = G.p(ax, ay + (a0 + a1) / 2, 0.05)
                mb.box((0.16, a1 - a0, 0.9), c, G.r(), M_DRESS, bv)
    mb.box((W + 0.56, D + 0.56, 0.38), G.p(cxm, cym, 0.69), G.r(), M_DRESS, B_PROP)
    mb.box((W + 0.66, D + 0.66, 0.1), G.p(cxm, cym, 0.93), G.r(), OBS, 0.03)


def ashlar(mb, f, z0, z1, legs, excl, phase=0, joints=True):
    """silhar em relevo raso (0,07) na face f: fiadas de 2 alturas (0,95 / 0,7) escaladas para fechar z0..z1, blocos
    de ~2,9 com juntas desencontradas (0,08) sobre o nucleo escuro. legs(k) = pernas dos cunhais nas 2 pontas da
    fiada k; excl = [(s0, s1, za, zb)] vaos (janela + ombreiras, postigos, loja)"""
    hs = COURSES
    n2 = max(1, int(round((z1 - z0) / sum(hs))))
    sc = (z1 - z0) / (n2 * sum(hs))
    zz = z0
    k = 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        za, zb = zz + 0.04, zz + h - 0.04
        la, lb = legs(k)
        # retangulos da fiada menos os vaos (o que sobra acima/abaixo de um vao vira peca baixa: sem buraco)
        rects = [(-f.L / 2 + la + 0.06, f.L / 2 - lb - 0.06, za, zb, True)]
        for e0, e1, ez0, ez1 in excl:
            out = []
            for a, b, ra, rb, full in rects:
                if e1 <= a or e0 >= b or ez1 <= ra or ez0 >= rb:
                    out.append((a, b, ra, rb, full))
                    continue
                if e0 - a > 0.3:
                    out.append((a, e0 - 0.05, ra, rb, full))
                if b - e1 > 0.3:
                    out.append((e1 + 0.05, b, ra, rb, full))
                m0, m1 = max(a, e0 - 0.05), min(b, e1 + 0.05)
                if ez0 - ra > 0.14:
                    out.append((m0, m1, ra, ez0 - 0.04, False))
                if rb - ez1 > 0.14:
                    out.append((m0, m1, ez1 + 0.04, rb, False))
            rects = out
        PL = 4.2
        off = (phase + k) % 2 * PL / 2
        for a, b, ra, rb, full in rects:
            cuts = [a, b]
            if joints and full:
                cuts = [a] + [(-f.L / 2 + off + PL * j) for j in range(-1, int(f.L / PL) + 3)
                              if a + 0.8 < -f.L / 2 + off + PL * j < b - 0.8] + [b]
            for c0, c1 in zip(cuts, cuts[1:]):
                p0 = c0 + (0.04 if c0 > a else 0.0)
                p1 = c1 - (0.04 if c1 < b else 0.0)
                if p1 - p0 > 0.12:
                    f.box(mb, (p0 + p1) / 2, 0.035, (ra + rb) / 2, p1 - p0, 0.07, rb - ra, M_ASH)
        zz += h
        k += 1


def quoins(mb, G, x0, x1, y0, y1, z0, z1, front="+y"):
    """cunhais que SEGUEM as fiadas do silhar (mesma escala): perna longa 1,5 / curta 0,9 alternadas, saliencia
    0,22 (longa) / 0,15 (curta), pedra media com chanfro. Devolve legs(k) por eixo para o silhar."""
    hs = COURSES
    n2 = max(1, int(round((z1 - z0) / sum(hs))))
    sc = (z1 - z0) / (n2 * sum(hs))
    la, lb = 1.5, 0.9
    zz = z0
    k = 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        pq = 0.22 if k % 2 == 0 else 0.15
        ax, ay = (la, lb) if k % 2 == 0 else (lb, la)
        for cx_, cy_ in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            sgx = 1.0 if cx_ > (x0 + x1) / 2 else -1.0
            sgy = 1.0 if cy_ > (y0 + y1) / 2 else -1.0
            fr = (front == "+y" and sgy > 0) or (front == "+x" and sgx > 0)
            mb.box((ax + pq, ay + pq, h - 0.08), G.p(cx_ - sgx * (ax - pq) / 2, cy_ - sgy * (ay - pq) / 2,
                                                       zz + h / 2), G.r(), M_DRESS, 0.06 if fr else 0.0)
        zz += h
        k += 1

    def legs_x(k):                     # faces +y / -y (ao longo de x)
        return ((la if k % 2 == 0 else lb),) * 2

    def legs_y(k):                     # faces +x / -x (ao longo de y)
        return ((lb if k % 2 == 0 else la),) * 2
    return legs_x, legs_y


# ------------------------------------------------------------------ telhado: fiadas, cumeeira, chamine
def slate_course(mb, G, xa, xb, ay, az, s, tr, lr, thr, teeth=0, depth=0.3, m=ROOF):
    """fiada de ardosia: placa no plano da agua (u = x de G ao longo da cumeeira; v descendo a agua a partir de
    (ay, az)); espessura thr para fora. teeth > 0: a borda de baixo RECORTADA em dentes (so vertices: nenhuma peca por
    telha)"""
    dy, dz = s * math.cos(tr), -math.sin(tr)
    ny, nz = s * math.sin(tr), math.cos(tr)
    out = [(xa, 0.0), (xb, 0.0)]
    if teeth:
        for j in range(2 * teeth + 1):
            out.append((xb - j * (xb - xa) / (2 * teeth), lr if j % 2 == 0 else lr - depth))
    else:
        out += [(xb, lr), (xa, lr)]
    bm = mb.bm
    lo = [bm.verts.new(G.p(u, ay + dy * v, az + dz * v)) for u, v in out]
    hi = [bm.verts.new(G.p(u, ay + dy * v + ny * thr, az + dz * v + nz * thr)) for u, v in out]
    n = len(out)
    faces = [bm.faces.new(lo), bm.faces.new(list(reversed(hi)))]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((lo[j], lo[i], hi[i], hi[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    mb._post(lo + hi, m, None, 0, 1)


def roof_z(ze, R, hd, cy, y, thr=0.34):
    """cota da FACE DE CIMA da agua principal em y (local), para rufos e golas"""
    t = math.atan2(R, hd)
    return ze + R - abs(y - cy) * math.tan(t) + thr / math.cos(t)


def chimney(mb, G, cx_, cy_, wx_, dp, z0, z1, kind, ze, R, hd, cy):
    """chamine do kit: fuste em fiadas de 2 alturas (0,62 cheia / 0,38 recuada), RUFO inclinado no telhado, capa com
    ressalto duplo e pote ceramico torneado ('stack' 1 pote, 'twin' 2 potes, 'hood' chapeu de ardosia em 2 aguas)"""
    t = math.atan2(R, hd)
    zr = roof_z(ze, R, hd, cy, cy_)
    zlow = min(roof_z(ze, R, hd, cy, cy_ - dp / 2), roof_z(ze, R, hd, cy, cy_ + dp / 2)) - 0.4
    mb.box((wx_ - 0.1, dp - 0.1, zlow - z0), G.p(cx_, cy_, (z0 + zlow) / 2), G.r(), M_DRESS, 0.0)
    zz = zlow
    k = 0
    top = z1 - 0.62
    while zz < top - 0.05:
        h = min((1.0, 0.5)[k % 2], top - zz)
        ins = 0.0 if k % 2 == 0 else 0.1
        mb.box((wx_ - ins, dp - ins, h), G.p(cx_, cy_, zz + h / 2), G.r(), M_DRESS, 0.0)
        zz += h
        k += 1
    # capa: 2 ressaltos + laje recuada
    mb.box((wx_ + 0.24, dp + 0.24, 0.2), G.p(cx_, cy_, top + 0.1), G.r(), M_DRESS, 0.0)
    mb.box((wx_ + 0.46, dp + 0.46, 0.24), G.p(cx_, cy_, top + 0.32), G.r(), M_CAP, 0.04)
    mb.box((wx_ + 0.16, dp + 0.16, 0.16), G.p(cx_, cy_, top + 0.52), G.r(), M_DRESS, 0.0)
    zt = top + 0.6
    # rufo: gola inclinada no plano da agua em volta do fuste (o fuste nao "sai" do telhado sem encaixe)
    sg = 1 if cy_ >= cy else -1
    if abs(cy_ - cy) < dp / 2 + 0.2:
        for s2 in (-1, 1):
            mb.box((wx_ + 0.5, 1.0, 0.14), G.p(cx_, cy + s2 * 0.45, ze + R + 0.35), G.r(-s2 * t, 0, 0), ROOF, 0.0)
    else:
        mb.box((wx_ + 0.5, dp / math.cos(t) + 0.5, 0.14), G.p(cx_, cy_, zr + 0.02), G.r(-sg * t, 0, 0), ROOF, 0.0)
    pot = [(0.3, 0.0), (0.33, 0.1), (0.25, 0.5), (0.35, 0.8), (0.29, 0.88)]
    if kind == "twin":
        for kk in (-1, 1):
            _lathe(mb, tuple(G.p(cx_ + kk * 0.55, cy_, zt)), pot, M_POT, 6)
    elif kind == "hood":
        for kx in (-1, 1):
            for ky in (-1, 1):
                mb.box((0.14, 0.14, 0.8), G.p(cx_ + kx * 0.55, cy_ + ky * 0.55, zt + 0.4), G.r(), IRON, 0.0)
        th2 = math.radians(32.0)
        for s2 in (-1, 1):
            mb.box((wx_ + 0.5, 1.05, 0.12), G.p(cx_, cy_ + s2 * 0.44, zt + 1.06), G.r(-s2 * th2, 0, 0), ROOF, 0.0)
    else:
        _lathe(mb, tuple(G.p(cx_, cy_, zt)), pot, M_POT, 6)


# ------------------------------------------------------------------ casa
def house(mb, idx, lot, spec, rng):
    x, y, w_lot, d_lot, deg, z = lot
    ya = math.radians(deg) - math.pi / 2
    gable_front = spec.get("gable_front", False)
    if gable_front:
        G = Frame(x, y, z, ya + math.pi / 2)
        W, D = d_lot, w_lot
        front = "+x"
    else:
        G = Frame(x, y, z, ya)
        W, D = w_lot, d_lot
        front = "+y"
    stories = spec["stories"]           # [("stone"|"timber", altura)]
    jet = spec.get("jetty", 0.0)
    R = spec["rise"]
    wx0, wx1, wy0, wy1 = -W / 2, W / 2, -D / 2, D / 2

    def faces(b):
        x0, x1, y0, y1 = b
        return {"+y": Face(G, (0.0, y1), (1.0, 0.0), x1 - x0), "-y": Face(G, (0.0, y0), (-1.0, 0.0), x1 - x0),
                "+x": Face(G, (x1, (y0 + y1) / 2), (0.0, -1.0), y1 - y0),
                "-x": Face(G, (x0, (y0 + y1) / 2), (0.0, 1.0), y1 - y0)}

    back = {"+y": "-y", "+x": "-x"}[front]
    socle(mb, G, wx0, wx1, wy0, wy1, back)
    zc = 1.0
    body = (wx0, wx1, wy0, wy1)
    top_b = body
    # a agua do telhado sobre a fachada (casas de 1 pavimento com o beiral na frente): a lanterna fica abaixo dela
    hd_top = (D + (jet * 1.6 if not gable_front and len(stories) > 1 else 0.0)) / 2
    tan_t = R / hd_top
    tur_s = spec["turret"][0] if spec.get("turret") and not gable_front and spec["turret"][1] > 0 else 0
    li = 0
    for si, (kind, h) in enumerate(stories):
        b = body
        if si > 0 and jet > 0:
            x0, x1, y0, y1 = body
            if gable_front:
                b = (x0, x1 + jet, y0, y1)
            else:
                b = (x0, x1, y0 - jet * 0.6, y1 + jet)
            bx0, bx1, by0, by1 = b
            mb.box((bx1 - bx0 + 0.3, by1 - by0 + 0.3, 0.5), G.p((bx0 + bx1) / 2, (by0 + by1) / 2, zc + 0.05), G.r(),
                   WOOD, 0.0)
            ff = faces(body)[front]
            lan_below = spec.get("_lan0", [])
            for s in win_slots(ff.L, 0.4, n=int(ff.L / 2.4), margin=0.8):
                if any(abs(s - q) < 0.75 for q in lan_below):
                    continue                     # a misula nao cai sobre o braco da lanterna do terreo
                ff.box(mb, s, jet / 2, zc - 0.45, 0.4, jet, 0.8, WOOD)
        x0, x1, y0, y1 = b
        stone = kind == "stone"
        mb.box((x1 - x0, y1 - y0, h), G.p((x0 + x1) / 2, (y0 + y1) / 2, zc + h / 2), G.r(),
               M_JNT if stone else M_PL, 0.0)
        fs = faces(b)
        if stone:
            lx, ly = quoins(mb, G, x0, x1, y0, y1, zc, zc + h, front)
        for key, f in fs.items():
            is_front = key == front
            style = spec.get("win", "cross") if (is_front and kind == "timber") else "cross"
            ww = {"trio": 3.0, "lancet": 1.6}.get(style, 1.7) if kind == "timber" else 1.6
            wh = {"trio": 2.2, "lancet": 2.0}.get(style, 2.4) if kind == "timber" else 2.5
            shop = spec.get("shop") and si == 0 and is_front
            if shop:
                slots = [(0.0, "shop")]           # a loja: persiana ao centro e o PAR de lanternas (sem janelas)
            elif is_front:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=spec.get("nwin", None))]
            elif key == back:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=1)]
            else:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=(1 if f.L < 11.0 else 2))]
            zl = zc + (1.9 if stone else 1.5)
            if si == 0 and len(stories) == 1:
                zl = zc + 2.0
            shut = bool(is_front and stone and not shop and spec.get("shutters"))
            wsl = [s for s, kd in slots if kd != "shop"]
            # lanternas de suporte (so na fachada do terreo): escolhidas ANTES da estrutura aparente
            lan = []
            za = zc + min(h, 6.8) - (1.25 if stone and len(stories) > 1 else 0.9)
            if si == 0 and is_front:
                cand = _lantern_slots(f.L, wsl, 1.4 if shop else ww, shut, shop)
                if tur_s:
                    cand = [c for c in cand if not (c * tur_s > 0 and abs(c) > f.L / 2 - 3.2)]
                if len(cand) > 1:
                    # casa comum: UMA lanterna, no vao mais perto do eixo da vila (x = 0: praca, escada, portao)
                    cand = sorted(cand, key=lambda c: abs(f.P(c, 0.0, 0.0).x))[:1]
                if len(stories) == 1 and not gable_front:
                    za = min(za, zc + h - 1.75 * tan_t - 0.35)
                lan = cand
                spec["_lan0"] = list(lan)
            wins = []
            dress_seq = spec.get("dress", "coc")
            boxes = spec.get("planter") and kind == "timber" and is_front
            nws = len([1 for _, kd in slots if kd == "w"])
            for wi, (s, kd) in enumerate([sl for sl in slots if sl[1] == "w"]):
                dr = {"c": "curtain", "o": "open", "b": "blind"}[dress_seq[(wi + si + (0 if is_front else 1))
                                                                           % len(dress_seq)]]
                # caixas de janela: no maximo 2 por fachada (as pontas; o miolo fica limpo), so no ultimo andar
                pl = bool(boxes) and si == len(stories) - 1 and (nws <= 2 or wi in (0, nws - 1))
                window(mb, f, s, zl, 1.4 if shop else ww, wh,
                       head=(spec.get("stone_head", "lintel") if stone else "hood"), shutters=shut, planter=pl,
                       style=style, dress=dr, stone=stone, lod=(0 if is_front else 1))
                wins.append((s, ww))
            if shop:
                shopfront(mb, f, 0.0)
            if kind == "timber":
                timber_face(mb, f, zc, zc + h, wins, rng, pattern=spec.get("frame", "chevron"), zsill=zl - 0.45,
                            keep=lan)
            else:
                # vaos: janela (ombreiras + peitoril + verga de madeira); os postigos e as vergas de pedra assentam
                # POR CIMA do silhar
                excl = [(s - ww / 2 - 0.42, s + ww / 2 + 0.42, zl - 0.45, zl + wh + 0.2) for s in wsl]
                if shop:
                    excl.append((-2.75, 2.75, 0.0, 5.92))
                legs = lx if key in ("+y", "-y") else ly
                ashlar(mb, f, zc, zc + h, legs, excl, phase=(0 if key in ("+y", "-y") else 1), joints=is_front)
            for q in lan:
                wall_lantern(mb, f, q, za, base=(0.07 if stone else 0.0))
                li += 1
        if stone and si < len(stories) - 1:
            mb.box((x1 - x0 + 0.5, y1 - y0 + 0.5, 0.4), G.p((x0 + x1) / 2, (y0 + y1) / 2, zc + h - 0.2), G.r(),
                   M_CAP, 0.04)                                               # cordao de pedra
        zc += h
        body = b
        top_b = b
    spec.pop("_lan0", None)
    ze = zc
    # ---- telhado ingreme (cumeeira ao longo de x de G) sobre o ultimo pavimento
    x0, x1, y0, y1 = top_b
    cy = (y0 + y1) / 2
    hd = (y1 - y0) / 2
    oe, og, th = 1.0, 0.8, 0.6
    t = math.atan2(R, hd)
    Ls = (hd + oe) / math.cos(t)
    dl = math.radians(3.0)
    tr = t - dl
    # fiadas em 2 alturas, contadas do beiral para cima: alta (lisa) / baixa (borda em dentes) alternadas
    nrow = max(4, int(round(Ls / 1.4)))
    wts = [1.3 if (nrow - 1 - k) % 2 == 0 else 0.8 for k in range(nrow)]
    tot = sum(wts)
    xa, xb = x0 - og, x1 + og
    nt = max(4, int(round((xb - xa) / 1.9)))
    for s in (-1, 1):
        acc = 0.0
        fr_slope = (front == "+y" and s > 0)
        for k in range(nrow):
            f0 = acc / tot
            acc += wts[k]
            f1 = min(1.0, (acc + 0.42) / tot)
            ay = cy + s * f0 * (hd + oe)
            az = ze + R - f0 * (R + oe * math.tan(t))
            lr = (f1 - f0) * Ls
            eave = k == nrow - 1
            scal = (nrow - 1 - k) in ((1, 3) if fr_slope else (1,))    # escama perto do beiral (a parte vista)
            if eave:
                trk, thk = tr, 0.3
            else:
                # a fiada de cima ASSENTA sobre a de baixo (ardosia fina): inclina o bastante para a borda passar
                # por cima dela -> a borda recortada em dentes aparece sobre a fiada de baixo
                v0 = wts[k] / tot * Ls
                below = 0.3 if k + 1 == nrow - 1 else 0.2
                trk, thk = t - math.atan2(below + 0.04, v0), 0.2
            slate_course(mb, G, xa, xb, ay, az, s, trk, lr, thk, teeth=(nt if scal else 0), depth=0.26)
        # guarda-po (tabua escura na borda da empena)
        for xe in (x0 - og - 0.1, x1 + og + 0.1):
            mb.beam(G.p(xe, cy, ze + R + th), G.p(xe, cy + s * (hd + oe), ze - oe * math.tan(t) + th * 0.6), 0.28,
                    0.7, WOOD, 0.0)
    # beiral: testeira ao longo da borda + cachorros (pontas de caibro) sob o balanco
    ez = ze - oe * math.tan(t)
    for s in (-1, 1):
        mb.box((x1 - x0 + 2 * og, 0.3, 0.55), G.p((x0 + x1) / 2, cy + s * (hd + oe - 0.12), ez - 0.05), G.r(), WOOD,
               0.0)
        nr = max(3, int((x1 - x0) / 2.8))
        if front == "+y" and s < 0:
            continue                          # beiral dos fundos: so a testeira (os cachorros ficam no da rua)
        for k in range(nr + 1):
            xr = x0 + 0.35 + (x1 - x0 - 0.7) * k / nr
            mb.beam(G.p(xr, cy + s * (hd - 0.1), ze - 0.32), G.p(xr, cy + s * (hd + oe - 0.3), ez - 0.2), 0.26, 0.32,
                    WOOD, 0.0)
    rt = ze + R + th / math.cos(t)
    # cumeeira em PECAS com junta (capa em V de ardosia, 1,25 + junta 0,1)
    Lr = xb - xa + 0.3
    npc = max(3, int(round(Lr / 1.8)))
    for k in range(npc):
        u0 = xa - 0.15 + Lr * k / npc + 0.05
        u1 = xa - 0.15 + Lr * (k + 1) / npc - 0.05
        mb.box((u1 - u0, 0.62, 0.62), G.p((u0 + u1) / 2, cy, rt - 0.28), G.r(math.pi / 4, 0, 0), ROOF, 0.0)
    for xe in (x0 - og - 0.1, x1 + og + 0.1):
        if spec.get("ridge", "crest") == "crest":
            # casa de mestre/loja: bloco de ferro no fecho + remate de ferro torneado
            mb.box((0.56, 0.56, 0.5), G.p(xe, cy, rt + 0.05), G.r(), WOOD, 0.0)
            finial_iron(mb, G.p(xe, cy, rt + 0.3), 1.0)
        else:
            finial_wood(mb, G.p(xe, cy, rt + 0.1), 1.0)
    # empenas (reboco + estrutura), janela de sotao
    for sx, key in ((1, "+x"), (-1, "-x")):
        f = Face(G, (x1 if sx > 0 else x0, cy), (0.0, -1.0) if sx > 0 else (0.0, 1.0), y1 - y0)
        nv = f.nvec()
        pts = [f.P(-hd, 0.0, ze), f.P(hd, 0.0, ze), f.P(0.0, 0.0, ze + R)]
        tri_slab(mb, pts, nv, 0.6, M_PL)
        f.box(mb, 0.0, 0.15, ze + 0.22, y1 - y0 + 0.3, 0.3, 0.44, WOOD)
        attic = (key == front) or spec.get("attic_all", False)
        zc_win = ze + 1.0
        zcol = (ze + 4.6) if attic else (ze + R * 0.42)
        if attic:
            ast = spec.get("win", "cross") if key == front else "cross"
            ast = "cross" if ast == "trio" else ast
            window(mb, f, 0.0, zc_win, 1.3, 1.7 if ast == "lancet" else 2.0,
                   head="hood" if key == front else None, style=ast,
                   dress=("curtain" if key == front else "blind"))
            f.box(mb, 0.0, 0.15, (zcol + 0.2 + ze + R - 0.6) / 2, 0.42, 0.3, ze + R - 0.6 - zcol - 0.2, WOOD)
        else:
            f.box(mb, 0.0, 0.15, ze + R * 0.46, 0.42, 0.3, R * 0.9, WOOD)
        half = hd * (1 - (zcol - ze) / R) - 0.3
        f.box(mb, 0.0, 0.15, zcol, 2 * half, 0.3, 0.42, WOOD)                 # linha alta
        for k in (-1, 1):
            f.beam(mb, k * (hd - 0.5), ze + 0.4, k * max(0.5 * half, 1.7), zcol - 0.1, 0.15, 0.3, 0.36)
    # ---- aguas-furtadas: corpo de reboco, empena de madeira com GUARDA-POS e RUFOS de ardosia no encontro das
    # bochechas com a agua principal (a fiada de escama de baixo passa na frente da base: sem avental solto)
    for side, xd in spec.get("dormers", []):
        s = 1 if side == "+y" else -1
        wd = 2.8
        yf = cy + s * (hd - 0.6)
        zr = ze + R * (1 - (hd - 0.6) / hd)
        zb = zr + th / math.cos(t) + 0.1
        zt = zb + 2.9
        yb = cy + s * hd * (1 - (zt - ze) / R)
        ya0, ya1 = sorted((yb - s * 0.4, yf))
        mb.box((wd, ya1 - ya0, zt - zr + 0.6), G.p(xd, (ya0 + ya1) / 2, (zr - 0.6 + zt) / 2), G.r(), M_PL, 0.0)
        rr = 1.7
        hw = wd / 2 + 0.35
        t2 = math.atan2(rr, hw)
        L2 = hw / math.cos(t2)
        ln = abs(yf - yb) + 1.0
        for s2 in (-1, 1):
            mb.box((L2, ln, 0.32), G.p(xd + s2 * hw / 2, (yf + yb) / 2 + s * 0.3, zt + rr / 2 + 0.16),
                   G.r(0, s2 * t2, 0), ROOF, 0.0)
        mb.box((0.42, ln + 0.1, 0.42), G.p(xd, (yf + yb) / 2 + s * 0.3, zt + rr + 0.2), G.r(0, math.pi / 4, 0), ROOF,
               0.0)
        fd = Face(G, (xd, yf), (s * 1.0, 0.0), wd)
        tri_slab(mb, [fd.P(-wd / 2, 0.0, zt), fd.P(wd / 2, 0.0, zt), fd.P(0.0, 0.0, zt + rr)], fd.nvec(), 0.4, WOOD)
        for k in (-1, 1):
            # guarda-pos da empena da agua-furtada (tabua com espessura na borda do telhadinho)
            mb.beam(fd.P(k * (hw + 0.05), 0.72, zt + 0.02), fd.P(0.0, 0.72, zt + rr + 0.34), 0.2, 0.42, WOOD, 0.0)
            # rufo de ardosia no encontro da bochecha com a agua principal
            xk = xd + k * (wd / 2 + 0.16)
            mb.beam(G.p(xk, yf, roof_z(ze, R, hd, cy, yf) - 0.06), G.p(xk, yb, roof_z(ze, R, hd, cy, yb) - 0.06),
                    0.34, 0.14, ROOF, 0.0)
        window(mb, fd, 0.0, zb + 0.5, 1.3, 1.8, head=None, dress="open", lod=2)
        finial_iron(mb, G.p(xd, (yf + yb) / 2 + s * 0.85, zt + rr + 0.38), 0.55)
    # ---- chamines (3 desenhos do kit; algumas casas com 2a chamine: a linha dos telhados nao se repete)
    chims = []
    if spec.get("chimney"):
        chims.append((spec["chimney"], spec.get("chim_kind", "stack"), spec.get("chim_h", 2.6)))
    if spec.get("chimney2"):
        chims.append((spec["chimney2"], spec.get("chim2_kind", "stack"), spec.get("chim2_h", 1.6)))
    for (cx_, cy_), kind, hx in chims:
        cx_ *= (x1 - x0) / 2
        cy_ = cy + cy_ * hd
        chimney(mb, G, cx_, cy_, 2.4 if kind == "twin" else 1.5, 1.5, ze - 0.5, ze + R + hx, kind, ze, R, hd, cy)
    # ---- torreao (canto da frente): base em ESCARPA, cordao a cada andar, frestas com molduras de pedra media,
    # fiada de MISULAS sob a cornija, agulha de 8 lados em beiral curvo com fiadas de escama e lucarna, remate torneado
    tur = spec.get("turret")
    if tur:
        sx, sy = tur
        tx, ty = (x0 if sx < 0 else x1) + sx * 0.6, (y1 + 0.6) if sy > 0 else (y0 - 0.6)
        wp = G.p(tx, ty, 0.0)
        r = 2.5
        zt1 = z + ze + 3.2
        c2 = (wp.x, wp.y)
        rot8 = math.radians(22.5)
        _lathe(mb, (wp.x, wp.y, z - 0.4), [(r + 0.75, 0.0), (r + 0.75, 0.5), (r + 0.62, 0.62), (r + 0.1, 2.0),
                                            (r + 0.22, 2.08), (r + 0.22, 2.3), (r, 2.38)], M_DRESS, 8, rot8,
               caps=(False, False))
        mb.prism(SL.ccw(ngon(c2, r, 8, 22.5)), z + 1.9, zt1, M_ASH)
        for zz in (z + 1.0 + stories[0][1], z + ze - 1.2):
            _lathe(mb, (wp.x, wp.y, zz), [(r - 0.02, 0.0), (r + 0.2, 0.08), (r + 0.2, 0.3), (r - 0.02, 0.38)], M_DRESS,
                   8, rot8, caps=(False, False))                                # cordao
        # misulas (1 por face) sob a cornija + cornija
        for k in range(8):
            a = math.radians(45.0 * k)
            ap_ = r * math.cos(math.pi / 8)
            px_, py_ = wp.x + (ap_ + 0.14) * math.cos(a), wp.y + (ap_ + 0.14) * math.sin(a)
            mb.box((0.34, 0.5, 0.34), (px_, py_, zt1 - 0.62), (0, 0, a), M_DRESS, 0.0)
            px_, py_ = wp.x + (ap_ + 0.26) * math.cos(a), wp.y + (ap_ + 0.26) * math.sin(a)
            mb.box((0.52, 0.52, 0.3), (px_, py_, zt1 - 0.3), (0, 0, a), M_DRESS, 0.03)
        _lathe(mb, (wp.x, wp.y, zt1), [(r - 0.1, -0.02), (r + 0.5, 0.0), (r + 0.62, 0.14), (r + 0.62, 0.34),
                                        (r + 0.45, 0.46), (r - 0.1, 0.46)], M_CAP, 8, rot8, caps=(False, True))
        # agulha: beiral curvo (sai 0,95 alem da cornija) + 3 fiadas de escama (degrau na borda) + remate de ferro
        zs0 = zt1 + 0.46
        H = 10.5
        prof = [(r + 0.95, 0.0), (r + 0.95, 0.12), (r + 0.55, 0.42)]
        for j, fz in enumerate((0.2, 0.42, 0.66)):
            rr0 = (r + 0.55) * (1 - fz) + 0.24 * fz
            prof += [(rr0 + 0.18, H * fz - 0.02), (rr0 - 0.02, H * fz + 0.05)]
        prof += [(0.3, H - 0.4), (0.0, H)]
        _lathe(mb, (wp.x, wp.y, zs0), prof, ROOF, 8, rot8, caps=(True, False))
        finial_iron(mb, (wp.x, wp.y, zs0 + H - 0.35), 0.9)
        # lucarna pequena (encara a rua): corpo, empena, telhadinho
        out = math.degrees(math.atan2(wp.y - G.o.y, wp.x - G.o.x))
        out = 45.0 * round(out / 45.0)
        a_ = math.radians(out)
        nx_, ny_ = math.cos(a_), math.sin(a_)
        zl_ = zs0 + H * 0.25
        rl = (r + 0.55) * (1 - 0.25) + 0.24 * 0.25
        cp = Vector((wp.x + nx_ * (rl - 0.35), wp.y + ny_ * (rl - 0.35), zl_ + 0.55))
        mb.box((1.0, 1.0, 1.1), cp, (0, 0, a_), M_PL, 0.0)
        mb.box((0.14, 0.62, 0.62), cp + Vector((nx_ * 0.5, ny_ * 0.5, 0.0)), (0, 0, a_), M_ROOM, 0.0)
        for k in (-1, 1):
            mb.box((0.7, 1.4, 0.12), cp + Vector((nx_ * 0.1, ny_ * 0.1, 0.75)) + Vector((-ny_ * k * 0.28,
                                                                                          nx_ * k * 0.28, 0.0)),
                   (0, -k * math.radians(40.0), a_ + math.pi / 2), ROOF, 0.0)
        # frestas quentes estreitas nas faces que dao para a rua (faces do octogono centradas em k*45 graus)
        ap = r * math.cos(math.pi / 8)
        for zz in (z + ze - 5.2, z + ze + 0.4):
            for da in (-45.0, 0.0, 45.0):
                a_ = math.radians(out + da)
                ux_, uy_ = -math.sin(a_), math.cos(a_)
                nx_, ny_ = math.cos(a_), math.sin(a_)
                p = Vector((wp.x + ap * nx_, wp.y + ap * ny_, zz))
                q = p + Vector((nx_ * 0.2, ny_ * 0.2, 0.0))
                mb.box((0.1, 0.6, 1.2), p + Vector((nx_ * 0.03, ny_ * 0.03, -0.3)), (0, 0, a_), M_ROOM, 0.0)
                mb.box((0.1, 0.6, 0.6), p + Vector((nx_ * 0.03, ny_ * 0.03, 0.6)), (0, 0, a_), WIN, 0.0)
                tri_slab(mb, [p + Vector((ux_ * 0.3 + nx_ * 0.07, uy_ * 0.3 + ny_ * 0.07, 0.9)),
                              p + Vector((-ux_ * 0.3 + nx_ * 0.07, -uy_ * 0.3 + ny_ * 0.07, 0.9)),
                              p + Vector((nx_ * 0.07, ny_ * 0.07, 1.3))], Vector((nx_, ny_, 0.0)), 0.06, WIN)
                for k in (-1, 1):
                    mb.box((0.42, 0.26, 1.9), q + Vector((ux_ * k * 0.43, uy_ * k * 0.43, -0.05)), (0, 0, a_), M_DRESS,
                           0.0)
                    mb.beam(q + Vector((ux_ * k * 0.43, uy_ * k * 0.43, 0.84)), q + Vector((0, 0, 1.5)), 0.42, 0.26,
                            M_DRESS, 0.0)
                mb.box((0.46, 0.34, 0.34), q + Vector((0, 0, 1.52)), (0, 0, a_), M_DRESS, 0.0)             # fecho
                mb.box((0.36, 0.98, 0.18), q + Vector((-nx_ * 0.02, -ny_ * 0.02, -1.0)), (0, 0, a_), M_CAP, 0.0)
        octo_col("SG_VilHouse", wp.x, wp.y, r + 0.3, z - 0.4, z + ze + 3.2)
    # ---- colisao do corpo (caixa)
    bx0, bx1, by0, by1 = body
    cxb, cyb = (min(bx0, wx0) + max(bx1, wx1)) / 2, (min(by0, wy0) + max(by1, wy1)) / 2
    sxb = max(bx1, wx1) - min(bx0, wx0) + 0.7
    syb = max(by1, wy1) - min(by0, wy0) + 0.7
    hb = ze + R * 0.55
    col_box("SG_VilHouse", (sxb, syb, hb + 0.4), G.p(cxb, cyb, hb / 2 - 0.2), G.r())


# especificacao das 11 casas (indice = sg_layout.HOUSE_LOTS): 1 ou 2 pavimentos, empena de frente ou de lado,
# balanco, aguas-furtadas, chamine (x relativo a meia-largura, y relativo a meia-profundidade), um torreao, lojas.
# Variacao DIRIGIDA do kit (o mesmo caixilho, peitoril, capelo, ardosia e madeira em todas; muda o PAPEL da casa):
#   win   'trio' lojas / 'lancet' casas de empena de frente (goticas) / 'cross' casas comuns
#   frame 'chevron' / 'cross' / 'studs' (o preenchimento da estrutura aparente)
#   ridge 'crest' remates de ferro (lojas e torreao) / 'roll' pendurais de madeira (comuns)
#   stone_head 'lintel' verga com fecho / 'label' pingadeira gotica;  shutters: postigos so onde a casa e de moradia
#   dress: sequencia de vestir das janelas ('c' cortina + bando, 'o' aberta, 'b' persiana de pano) - ~40% com pano
#   planter: caixas de janela SO nas janelas escolhidas da fachada de madeira (as pontas; o miolo fica limpo)
SPECS = [
    # P1 oeste
    dict(stories=[("stone", 6.4), ("timber", 5.6)], jetty=0.8, rise=8.4, shop=True, dormers=[("+y", 3.6)],
         chimney=(-0.62, -0.35), chim_kind="twin", attic_all=True,
         win="trio", frame="studs", ridge="crest", dress="oco"),
    dict(stories=[("timber", 6.8)], rise=9.8, dormers=[("+y", -2.6), ("+y", 2.6)], chimney=(0.6, -0.3), nwin=2,
         chim_kind="hood", planter=True, attic_all=True, win="cross", frame="chevron", ridge="roll", dress="cob"),
    dict(stories=[("stone", 6.0), ("timber", 5.4)], jetty=0.8, rise=9.8, gable_front=True, chimney=(-0.55, 0.5),
         chim_kind="stack", chim_h=3.4, win="lancet", frame="cross", ridge="roll", stone_head="label", dress="boo"),
    # P1 leste
    dict(stories=[("stone", 6.6), ("timber", 6.0)], jetty=0.8, rise=8.6, turret=(-1, 1), dormers=[("+y", 3.2)],
         chimney=(0.66, -0.4), chim_kind="twin", planter=True, attic_all=True,
         win="cross", frame="chevron", ridge="crest", shutters=True, dress="coo"),
    dict(stories=[("timber", 7.0)], rise=10.2, gable_front=True, chimney=(0.5, -0.5), attic_all=True,
         chim_kind="hood", planter=True, win="lancet", frame="studs", ridge="roll", dress="oc"),
    dict(stories=[("stone", 6.2), ("timber", 5.4)], jetty=0.8, rise=8.0, shop=True, dormers=[("+y", -2.8)],
         chimney=(0.6, -0.3), chim_kind="stack", chimney2=(-0.55, -0.4), chim2_kind="hood", attic_all=True,
         win="trio", frame="cross", ridge="crest", dress="obo"),
    # P2 oeste
    dict(stories=[("stone", 6.4), ("timber", 5.8)], jetty=0.8, rise=8.8, shop=True, dormers=[("+y", -3.6), ("+y", 3.6)],
         chimney=(0.62, -0.35), chim_kind="hood", planter=True, attic_all=True,
         win="trio", frame="chevron", ridge="crest", dress="coo"),
    dict(stories=[("timber", 6.8)], rise=11.0, gable_front=True, chimney=(-0.5, 0.45), chim_kind="twin", chim_h=2.0,
         win="lancet", frame="chevron", ridge="roll", dress="bo"),
    dict(stories=[("stone", 6.0), ("timber", 5.6)], jetty=0.8, rise=9.6, gable_front=True, chimney=(0.5, -0.5),
         chim_kind="stack", win="lancet", frame="studs", ridge="roll", stone_head="label",
         shutters=True, dress="oc"),
    # P2 leste
    dict(stories=[("timber", 6.8)], rise=9.0, dormers=[("+y", -2.6), ("+y", 2.6)], chimney=(-0.6, -0.3), nwin=2,
         chim_kind="hood", chimney2=(0.62, -0.3), chim2_kind="stack", planter=True, attic_all=True,
         win="cross", frame="cross", ridge="roll", dress="oc"),
    dict(stories=[("stone", 6.2), ("timber", 5.6)], jetty=0.8, rise=8.4, shop=True, dormers=[("+y", 2.8)],
         chimney=(-0.62, -0.35), chim_kind="twin", attic_all=True, win="trio", frame="studs", ridge="crest",
         dress="cob"),
]
GROUPS = [("P1W", (0, 1, 2)), ("P1E", (3, 4, 5)), ("P2W", (6, 7, 8)), ("P2E", (9, 10))]


# ------------------------------------------------------------------ praca + fonte
# OVERHAUL 01 (2026-09-29, "zero tolerancia"):
#   - PISO: nada de disco liso com fitas. Base escura (Stone_SG_Floor) que aparece SO nas juntas (0,1) e, por cima,
#     LAJES em aneis concentricos (~3 x 2, chanfro de 0,04), 2 tons alternados POR ANEL (variacao dirigida, nada
#     sorteado: materiais fixos, sem familia de variantes); rosacea de 16 setores FEITA DE PECAS (tom alternado por
#     setor); colar da fonte, anel do meio e borda em CANTARIA segmentada (pecas de ~3 com junta), um valor abaixo do
#     antigo Stone_SG_Trim; o "fio da ordem" que lia como trilho preto SAIU (a fonte e a escada ja dao o eixo).
#   - FONTE: bacia dodecagonal (mesmo envelope da colisao do sg_col) com pilastras de base e capitel e paineis de moldura
#     saliente; pe, fuste, tacas e colares num PERFIL DE TORNO continuo de 16 lados (bojo, labio enrolado, espessura);
#     agua em material proprio escuro-esverdeado SEM emissao nos 3 niveis, com bicas de agua caindo das tacas e anel de
#     espuma onde caem; as 4 lanternas da borda da bacia SAIRAM (ruido em volta do marco).
M_CAP = "Stone_SG_TrimLow"       # cantaria de remate (o mesmo do sg_entry: um valor abaixo do Stone_SG_Trim)
fm_lib.MATS.setdefault(M_CAP, (fm_lib.S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))
M_WATER = "Water_SGFountain"     # agua da fonte: escura, esverdeada, sem emissao (a Water_SG azul lia plastico)
fm_lib.MATS.setdefault(M_WATER, (fm_lib.S(44, 78, 88), 0.1, 0.0, 0, None, 0.0))
M_FALL = "Water_SGFoam"          # bicas e espuma: agua clara SEM emissao (a Water_Fall brilha na previa)
fm_lib.MATS.setdefault(M_FALL, (fm_lib.S(150, 180, 188), 0.3, 0.0, 0, None, 0.0))
M_SLAB_A = "Stone_Paving_SG_B"   # lajes, tom A (fixo: a variante B do calcamento)
M_SLAB_B = M_COB                 # lajes, tom B (um passo abaixo)
M_ASHLAR = "Stone_SG_Block_B"    # cantaria dos aneis
M_JOINT = "Stone_SG_Floor"       # leito escuro que so aparece nas juntas
M_BASIN = "Stone_SG_Castle_B"    # parede e fundo da bacia


def slab_ring(mb, c, r0, r1, n, z0, z1, m, a_off=0.0, gap=0.1, bevel=0.04, sub=1, skip=None):
    """anel de lajes: n pecas de r0 a r1 (juntas de 'gap'), cada peca com 'sub' segmentos no arco;
    m = material ou funcao(k) -> material; skip(k) -> True pula a peca"""
    for k in range(n):
        if skip and skip(k):
            continue
        a0 = a_off + 2 * math.pi * k / n
        a1 = a_off + 2 * math.pi * (k + 1) / n
        ri, ro = r0 + gap / 2, r1 - gap / 2
        di, do = (gap / 2) / ri, (gap / 2) / ro
        outer = [(c[0] + ro * math.cos(a0 + do + (a1 - a0 - 2 * do) * j / sub),
                  c[1] + ro * math.sin(a0 + do + (a1 - a0 - 2 * do) * j / sub)) for j in range(sub + 1)]
        inner = [(c[0] + ri * math.cos(a1 - di - (a1 - a0 - 2 * di) * j / sub),
                  c[1] + ri * math.sin(a1 - di - (a1 - a0 - 2 * di) * j / sub)) for j in range(sub + 1)]
        mm = m(k) if callable(m) else m
        mb.prism(SL.ccw(outer + inner), z0, z1, mm, bevel)


def fountain_statue(mb, x, y, zb, yaw, s=0.7):
    """a MESMA familia das guardas do patio (sg_court.hooded_figure: guardiao de pedra com a espada fincada), na
    versao ENCAPUZADA (o marco da ordem na praca; as guardas do portao usam elmo). Plinto octogonal com cornija.
    Pedra media fixa (Stone_SG_Block_B) com o vazio do capuz em obsidiana. Sem colisao (fica sobre a bacia)."""
    import sg_court as CT
    F = Frame(x, y, zb, yaw - math.pi / 2)
    mb.cyl(1.5 * s, 0.4 * s, F.p(0, 0, 0.2 * s), F.r(0, 0, math.pi / 8), OBS, n=8, bevel=0.0)
    mb.cyl(1.62 * s, 0.14 * s, F.p(0, 0, 0.45 * s), F.r(0, 0, math.pi / 8), M_CAP, n=8, bevel=0.0)
    CT.hooded_figure(mb, F, s, 0.52 * s, "Stone_SG_Block_B", OBS, kind="hood")


def _water_fall(mb, c, a, r0, z0, r1, z1, out=0.35, rad=0.09):
    """bica: fio de agua saindo do labio (r0, z0) e caindo em arco ate (r1, z1) na direcao a"""
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for i in range(7):
        t = i / 6.0
        u = 1 - t
        p0, p1, p2, p3 = (r0, z0), (r0 + out, z0 + 0.05), (r1, z0 - (z0 - z1) * 0.35), (r1, z1)
        r = u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0]
        zz = u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((c[0] + ca * r, c[1] + sa * r, zz))
    prof = [(rad * math.cos(2 * math.pi * i / 6), rad * math.sin(2 * math.pi * i / 6)) for i in range(6)]
    mb.sweep(pts, prof, M_FALL, True, None, up=(-sa, ca, 0.0))


def plaza():
    rng = random.Random(4101)
    mb = MB("SG_Vil_Plaza", COLL, rng, detail="near")
    c = L.PLAZA_C
    R = L.PLAZA_R
    z = P1
    # leito escuro (so aparece nas juntas das lajes)
    mb.prism(SL.ccw(ngon(c, R - 0.1, 64)), z - 0.25, z + 0.02, M_JOINT)
    zt = z + 0.07
    # colar de cantaria em volta da bacia
    slab_ring(mb, c, 7.45, 9.3, 16, z - 0.05, z + 0.1, M_ASHLAR, math.pi / 16, 0.1, 0.05, 2)
    # rosacea de 16 setores feita de pecas (tom por setor); aneis de dentro para fora: 1, 2 e 2 pecas por setor
    for r0, r1, sub_n in ((9.3, 11.6, 1), (11.6, 14.0, 2), (14.0, 16.4, 2)):
        slab_ring(mb, c, r0, r1, 16 * sub_n, z - 0.05, zt, lambda k, sn=sub_n: M_SLAB_A if (k // sn) % 2 else M_SLAB_B,
                  0.0, 0.1, 0.04, 2 if sub_n == 1 else 1)
    # anel de cantaria do meio
    slab_ring(mb, c, 16.4, 17.2, 24, z - 0.05, z + 0.09, M_ASHLAR, 0.0, 0.1, 0.04, 2)
    # campo externo: aneis de ~2 com pecas de ~3,2, juntas desencontradas e tom alternado POR ANEL
    rings = (17.2, 19.2, 21.2, 23.0, 24.8)
    for i, (r0, r1) in enumerate(zip(rings, rings[1:])):
        n = int(round(2 * math.pi * (r0 + r1) / 2 / 3.2))
        slab_ring(mb, c, r0, r1, n, z - 0.05, zt, M_SLAB_A if i % 2 == 0 else M_SLAB_B,
                  (math.pi / n) * (i % 2), 0.1, 0.04, 1)
    # borda de cantaria em segmentos de ~3 (meio-fio levemente acima)
    nb = int(round(2 * math.pi * 25.4 / 3.0))
    slab_ring(mb, c, 24.8, R, nb, z - 0.1, z + 0.13, M_ASHLAR, 0.0, 0.08, 0.05, 1)
    mb.finish()

    # fonte: bacia dodecagonal (casa com a colisao do sg_col: 12 lados, R 7, topo P1+2,6)
    mf = MB("SG_Vil_Fountain", COLL, rng, detail="near")
    rot = 0.0
    cx, cy = c
    mf.prism(SL.ccw(ngon(c, 7.55, 12, rot)), z - 0.1, z + 0.32, M_ASHLAR, 0.05)            # degrau
    ring_prism(mf, c, 6.05, 7.0, 12, z + 0.32, z + 2.3, M_BASIN, rot)                        # parede da bacia
    ring_prism(mf, c, 5.85, 7.25, 12, z + 2.3, z + 2.6, M_CAP, rot)                         # capeamento
    ring_prism(mf, c, 6.95, 7.12, 12, z + 2.2, z + 2.3, M_CAP, rot)                         # pingadeira
    ap = 7.0 * math.cos(math.radians(15.0))                                                  # apotema da face
    for k in range(12):
        a = math.radians(rot + 30.0 * k)
        px, py = c[0] + 7.02 * math.cos(a), c[1] + 7.02 * math.sin(a)
        # pilastra: base, fuste, capitel
        mf.box((0.98, 0.98, 0.3), (px, py, z + 0.47), (0, 0, a), M_ASHLAR, 0.04)
        mf.box((0.74, 0.74, 1.56), (px, py, z + 1.4), (0, 0, a), M_ASHLAR, 0.0)
        mf.box((0.96, 0.96, 0.22), (px, py, z + 2.09), (0, 0, a), M_CAP, 0.03)
        # painel da face: moldura saliente (o miolo fica rebaixado)
        am = a + math.radians(15.0)
        nx, ny = math.cos(am), math.sin(am)
        tx, ty = -ny, nx
        fx, fy = c[0] + (ap + 0.05) * nx, c[1] + (ap + 0.05) * ny
        hw, z0p, z1p = 1.15, z + 0.72, z + 1.98
        for sg in (-1, 1):
            mf.box((0.14, 0.12, z1p - z0p), (fx + tx * sg * hw, fy + ty * sg * hw, (z0p + z1p) / 2), (0, 0, am + math.pi / 2),
                   M_ASHLAR, 0.0)
        for zz in (z0p, z1p):
            mf.box((2 * hw + 0.14, 0.12, 0.14), (fx, fy, zz), (0, 0, am + math.pi / 2), M_ASHLAR, 0.0)
    mf.prism(SL.ccw(ngon(c, 6.1, 12, rot)), z + 0.32, z + 1.95, M_BASIN)                    # fundo da bacia
    mf.prism(SL.ccw(ngon(c, 6.08, 12, rot)), z + 1.95, z + 2.05, M_WATER)                    # lamina d'agua
    # coluna e tacas: UM perfil de torno (16 lados) do pe ate o fundo da taca de baixo, outro ate a taca de cima
    low = [(1.60, 1.90), (1.60, 2.30), (1.40, 2.42), (1.46, 2.58), (1.20, 2.72), (0.80, 2.95), (0.70, 3.40),
           (0.86, 3.90), (0.62, 4.50), (0.72, 4.70), (0.72, 4.85), (0.95, 5.05), (1.90, 5.35), (2.70, 5.70),
           (3.10, 6.05), (3.22, 6.25), (3.14, 6.42), (2.96, 6.40), (2.86, 6.10)]
    EM._lathe(mf, (cx, cy, z), low, M_CAP, 16, math.pi / 16)
    EM._lathe(mf, (cx, cy, z), [(2.9, 6.08), (2.9, 6.24)], M_WATER, 16, math.pi / 16)
    up = [(0.62, 6.10), (0.62, 6.32), (0.50, 6.46), (0.42, 7.00), (0.52, 7.50), (0.40, 7.90), (0.50, 8.05),
          (0.56, 8.18), (1.10, 8.42), (1.55, 8.70), (1.74, 8.92), (1.68, 9.10), (1.54, 9.08), (1.46, 8.90)]
    EM._lathe(mf, (cx, cy, z), up, M_CAP, 16, math.pi / 16)
    EM._lathe(mf, (cx, cy, z), [(1.49, 8.88), (1.49, 9.00)], M_WATER, 16, math.pi / 16)
    # bicas: 8 da taca de baixo para a bacia, 4 da de cima para a de baixo; espuma onde caem
    for k in range(4):
        _water_fall(mf, c, math.radians(45.0 + 90.0 * k), 3.16, z + 6.38, 3.78, z + 2.04, 0.3, 0.08)
        _water_fall(mf, c, math.radians(90.0 * k), 1.68, z + 9.04, 2.2, z + 6.22, 0.22, 0.06)
    EM._lathe(mf, (cx, cy, z), [(3.45, 2.04), (4.15, 2.04), (4.15, 2.08), (3.45, 2.08)], M_FALL, 16, 0.0,
              closed=True)
    EM._lathe(mf, (cx, cy, z), [(1.98, 6.23), (2.45, 6.23), (2.45, 6.27), (1.98, 6.27)], M_FALL, 16, 0.0,
              closed=True)
    # o MARCO da praca: o guardiao ENCAPUZADO da ordem sobre a taca de cima, encarando o sul (quem chega). O plinto
    # nasce de dentro da agua da taca (9,0); NENHUMA colisao nova (so a bacia do sg_col).
    fountain_statue(mf, cx, cy, z + 8.96, -math.pi / 2, 0.78)
    mf.finish()


# ------------------------------------------------------------------ ruas com meio-fio, escada P1->P2, muretas
def _street_list():
    out = []
    for i, (pts, w, z) in enumerate(L.STREETS):
        pts = list(pts)
        if z == P1 and abs(pts[0][0]) > 20 and abs(pts[0][1] - L.PLAZA_C[1]) < 20:
            # a rua da praca nasce DENTRO da praca (a borda de cantaria cobre a junta)
            sx = math.copysign(21.0, pts[0][0])
            pts = [(sx, pts[0][1])] + pts
        out.append((i, pts, w, z))
    return out


def _in_other_street(x, y, me, streets, pad=0.4):
    for i, pts, w, z in streets:
        if i == me:
            continue
        if L.polyline_dist(x, y, pts) < w / 2 + pad:
            return True
    return False


def _blocked_curb(x, y, z):
    if math.hypot(x - L.PLAZA_C[0], y - L.PLAZA_C[1]) < L.PLAZA_R + 0.3:
        return True
    if math.hypot(x - L.CRAFT_C[0], y - L.CRAFT_C[1]) < L.CRAFT_R + 0.5:
        return True
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        t = (x - foot[0]) * ux + (y - foot[1]) * uy
        d = abs(-(x - foot[0]) * uy + (y - foot[1]) * ux)
        if -tread - 1.5 <= t <= tread * n + 1.5 and d <= w / 2 + 1.4:
            return True
    zz = L.zone_of(x, y)
    return zz is None or abs(zz - z) > 0.1


def _offset_line(pts, off):
    out = []
    n = len(pts)
    for i in range(n):
        x, y = pts[i]
        if i == 0:
            dx, dy = pts[1][0] - x, pts[1][1] - y
        elif i == n - 1:
            dx, dy = x - pts[i - 1][0], y - pts[i - 1][1]
        else:
            ax, ay = x - pts[i - 1][0], y - pts[i - 1][1]
            bx, by = pts[i + 1][0] - x, pts[i + 1][1] - y
            la, lb = math.hypot(ax, ay) or 1, math.hypot(bx, by) or 1
            dx, dy = ax / la + bx / lb, ay / la + by / lb
        ln = math.hypot(dx, dy) or 1.0
        out.append((x - dy / ln * off, y + dx / ln * off))
    return out


def _resample(pts, step):
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(1, int(ln / step))
        for i in range(1, k + 1):
            out.append((a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k))
    return out


def _row_poly(la, lb, ra, rb, t0, t1, g=0.05):
    """quadrilatero de uma fiada (lados la->lb e ra->rb) entre as fracoes t0..t1 da largura, com junta g"""
    def lerp(p, q, t):
        return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)
    ln = max(0.2, math.hypot(lb[0] - la[0], lb[1] - la[1]))
    ga = g / ln
    a0, a1 = lerp(la, lb, ga), lerp(la, lb, 1 - ga)
    b0, b1 = lerp(ra, rb, ga), lerp(ra, rb, 1 - ga)
    return [lerp(a0, b0, t0), lerp(a1, b1, t0), lerp(a1, b1, t1), lerp(a0, b0, t1)]


def sett(mb, poly, z0, z1, m):
    """pedra de calcamento: tampo + 4 faces (sem fundo: assenta no leito)"""
    bm = mb.bm
    lo = [bm.verts.new((p[0], p[1], z0)) for p in poly]
    hi = [bm.verts.new((p[0], p[1], z1)) for p in poly]
    n = len(poly)
    faces = [bm.faces.new(hi)]
    for i in range(n):
        j = (i + 1) % n
        faces.append(bm.faces.new((lo[i], lo[j], hi[j], hi[i])))
    mb._post(lo + hi, m, None, 0, 1)


# tufos da borda do P2: (x, y, rumo da borda) diante das casas 6, 7, 8, 9 e 10 (lado de fora da terra batida)
EDGE_TUFTS = [(-62.0, -50.9, 0.0), (-93.5, -50.8, 0.0), (-56.5, -38.2, math.pi), (46.5, -38.3, math.pi),
              (37.5, -51.9, 0.0)]
CURB_PROF = [(-0.3, -0.3), (0.3, -0.3), (0.3, 0.19), (0.19, 0.3), (-0.3, 0.3)]   # chanfro do lado da rua


def streets():
    """ruas secundarias: leito escuro (so aparece nas juntas) + PARALELEPIPEDO em fiadas transversais de ~1,1 com
    relevo de 0,04, cada fiada em 2 pedras com a junta desencontrada fiada a fiada (0,42 / 0,58); meio-fio em pecas
    de ~2,2 com chanfro; no gramado do P2, faixa de terra batida junto ao meio-fio"""
    rng = random.Random(4102)
    sl = _street_list()
    objs = {P1: MB("SG_Vil_Streets_P1", COLL, rng, detail="near"), P2: MB("SG_Vil_Streets_P2", COLL, rng, detail="near"),
            P3: MB("SG_Vil_Streets_P3", COLL, rng, detail="near")}

    def cut_axis(poly):
        """tira do poligono a faixa do eixo nobre (|x| < AXIS_HW): o cruzamento e do caminho da ordem (sg_court)"""
        out = []
        for part in (SL.clip(poly, 1.0, 0.0, -AXIS_HW), SL.clip(poly, -1.0, 0.0, -AXIS_HW)):
            if len(part) >= 3 and abs(SL.area(part)) > 0.5:
                out.append(SL.ccw(part))
        return out

    for i, pts, w, z in sl:
        if all(abs(p[0]) < 1e-6 for p in pts):
            continue            # eixo nobre (rua do P2 e patio do castelo): desenhado pelo sg_court
        mb = objs[z]
        crosses = min(p[0] for p in pts) < -AXIS_HW < AXIS_HW < max(p[0] for p in pts)
        base = SL.ccw(SL.ribbon_poly(pts, w / 2))
        if z == P3:
            base = SL.ccw(SL.clip(base, 0.0, 1.0, DUN_PLAZA_Y))
            for poly in (cut_axis(base) if crosses else [base]):
                mb.prism(poly, z - 0.25, z + 0.05, M_COB)
            continue            # patio leste / dungeon: so o calcamento (o detalhe e das zonas do P3)
        for poly in (cut_axis(base) if crosses else [base]):
            mb.prism(poly, z - 0.25, z + 0.05, M_JNT)
        # fiadas de paralelepipedo (a linha central da rua da praca nasce dentro da praca: pula o que a praca cobre)
        core = _resample(pts, 1.5)
        hw = w / 2 - 0.64
        Lo, Ro = _offset_line(core, hw), _offset_line(core, -hw)
        for j in range(len(core) - 1):
            mx, my = (core[j][0] + core[j + 1][0]) / 2, (core[j][1] + core[j + 1][1]) / 2
            if math.hypot(mx - L.PLAZA_C[0], my - L.PLAZA_C[1]) < L.PLAZA_R + 0.6:
                continue
            if abs(mx) < AXIS_HW + 0.3 and crosses:
                continue
            if math.hypot(mx - L.CRAFT_C[0], my - L.CRAFT_C[1]) < L.CRAFT_R + 0.4:
                continue
            if _in_other_street(mx, my, i, sl, pad=-0.5):
                continue
            fj = 0.4 if j % 2 else 0.6
            for t0, t1 in ((0.0, fj - 0.012), (fj + 0.012, 1.0)):
                sett(mb, SL.ccw(_row_poly(Lo[j], Lo[j + 1], Ro[j], Ro[j + 1], t0, t1, 0.06)), z - 0.02, z + 0.09,
                     M_COB)
        # meio-fio dos dois lados (interrompido em cruzamentos, praca, escadas, porta do craft e fora do piso)
        for side in (-1, 1):
            line = _resample(_offset_line(pts, side * (w / 2 - 0.3)), 1.1)
            runs, run = [], []
            for p in line:
                if _blocked_curb(p[0], p[1], z) or _in_other_street(p[0], p[1], i, sl, pad=0.2):
                    if len(run) > 1:
                        runs.append(run)
                    run = []
                else:
                    run.append(p)
            if len(run) > 1:
                runs.append(run)
            prof = list(CURB_PROF) if side > 0 else [(-a_, b_) for a_, b_ in CURB_PROF]
            prof = SL.ccw(prof)
            for run in runs:
                k = 0
                while k < len(run) - 1:
                    j = min(len(run) - 1, k + 3)
                    if len(run) - 1 - j == 1:
                        j += 1                                  # sem toco de 1,1 na ponta
                    a, b = run[k], run[j]
                    ln = math.hypot(b[0] - a[0], b[1] - a[1])
                    if ln > 0.4:
                        ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
                        pa = (a[0] + ux * 0.035, a[1] + uy * 0.035, z + 0.06)
                        pb = (b[0] - ux * 0.035, b[1] - uy * 0.035, z + 0.06)
                        mb.sweep([pa, pb], prof, M_DRESS, True, None)
                    k = j
                if z == P2:
                    # terra batida de 0,6 entre o meio-fio e a grama (a rua nao corta a grama em linha seca)
                    ra = _offset_line(run, side * 0.3)
                    rb = _offset_line(run, side * 0.95)
                    for q in range(0, len(run) - 1, 6):
                        q1 = min(len(run) - 1, q + 6)
                        poly = [ra[q], ra[q1], rb[q1], rb[q]]
                        mb.prism(SL.ccw(poly), z - 0.1, z + 0.03, M_DIRT)
    # transicao rua/grama do P2 em pontos ESCOLHIDOS (a frente de cada casa, onde se pisa para chegar a ela): uma pedra
    # solta na borda da terra batida. Jardinagem 2026-09-29: os 2 tufos de espeto (material Grass) sairam - a borda do
    # gramado com a rua agora e CHEIA de tufos do campo do sg_garden (mais densos junto da terra batida)
    for x, y, a in EDGE_TUFTS:
        objs[P2].box((0.55, 0.42, 0.2), (x - 0.9 * math.cos(a), y - 0.9 * math.sin(a), P2 + 0.04), (0, 0, a + 0.5),
                     M_DRESS, 0.0)
    for o in objs.values():
        o.finish()
    # escada P1 -> P2 (so visual; a colisao e do sg_col): degraus de pedra do kit, BANZO continuo inclinado com capa
    # (no lugar dos dentes de serra), mureta de cantaria na borda do P2 e no mirante oeste
    ms = MB("SG_Vil_StairP1P2", COLL, rng, detail="near")
    SL.plan_stair(ms, "P1P2", m="Stone_SG_Block_B", side_m=M_ASH, stringers=False, riser_m=M_ASH)
    for s in (-1, 1):
        stair_banzo(ms, s)
        vil_parapet(ms, [(s * 8.0, -83.45), (s * 26.0, -83.45)], P2, ends=(False, True))
    vil_parapet(ms, [(-118.0, -55.0), (-119.2, -40.4), (-117.6, -35.0)], P2, ends=(True, True))
    ms.finish()


def stair_banzo(mb, s):
    """banzo da escada P1P2 (face interna em |x| = 8, onde fica a guarda do sg_col): paramento em fiadas de 2 alturas
    com juntas desencontradas sob a linha inclinada, rodape que acompanha os focinhos, capa inclinada em pecas com
    pingadeira e o pilarete de arranque (remate do kit) no pe"""
    import sg_entry as SE
    foot, deg, w, n, tread, g = L.stair_frame("P1P2")
    rise = (L.STAIR_TOP_Z["P1P2"] - foot[2]) / n
    ya, yb = foot[1], foot[1] + tread * n
    ta, tb = foot[2] + 1.25, L.STAIR_TOP_Z["P1P2"] + 1.25
    k = (tb - ta) / (yb - ya)
    x0, x1 = sorted((s * (w / 2), s * (w / 2 + 1.4)))
    zb = foot[2] - 0.3
    hs = (1.0, 0.8)
    c0, ci = zb, 0
    while c0 < tb - 0.05:
        c1 = min(c0 + hs[ci % 2], tb)
        if c1 <= ta:
            poly = [(ya, c0), (yb, c0), (yb, c1), (ya, c1)]
        else:
            ys0 = ya + max(0.0, (c0 - ta) / k)
            ys1 = ya + (c1 - ta) / k
            poly = [(ys0, c0), (yb, c0), (yb, c1), (ys1, c1)]
            if c0 < ta:
                poly.append((ya, ta))
        L0 = 2.6
        off = (0.0, 1.3)[ci % 2]
        cuts = [ya] + [ya + off + L0 * j for j in range(1, 9) if ya + off + L0 * j < yb - 0.8] + [yb]
        for u0, u1 in zip(cuts, cuts[1:]):
            bp = SE._dedupe(SE._clip_y(poly, u0 + 0.04, u1 - 0.04))
            if len(bp) >= 3 and abs(SL.area(bp)) > 0.2 and max(p[0] for p in bp) - min(p[0] for p in bp) > 0.3:
                SE.yz_block(mb, x0, x1, bp, M_ASH, 0.07)   # 16.01: o mesmo chanfro do banzo da entrada (0,07)
        c0, ci = c1, ci + 1

    def zn(y):
        return foot[2] + rise + (y - ya) * rise / tread
    xr = s * (w / 2 + 0.06)
    ra, rb = ya + 0.1, yb - 0.1
    mb.beam((xr, ra, zn(ra) + 0.36), (xr, rb, zn(rb) + 0.36), 0.14, 0.5, M_DRESS, 0.0)

    def zl(y):
        return ta + k * (y - ya)
    xm = s * (w / 2 + 0.7)
    A = Vector((xm, ya - 0.2, zl(ya - 0.2)))
    B = Vector((xm, yb + 0.3, zl(yb + 0.3)))
    dd = B - A
    nseg = max(1, int(round(dd.length / 2.5)))
    for j in range(nseg):
        p0 = A + dd * (j / nseg) + dd.normalized() * (0.03 if j else 0.0)
        p1 = A + dd * ((j + 1) / nseg) - dd.normalized() * (0.03 if j < nseg - 1 else 0.0)
        mb.beam((p0.x, p0.y, p0.z + 0.26), (p1.x, p1.y, p1.z + 0.26), 1.75, 0.32, M_CAP, 0.06)
    mb.beam((xm, A.y + 0.1, A.z + 0.1 * k + 0.04), (xm, B.y - 0.1, B.z - 0.1 * k + 0.04), 1.56, 0.12, M_CAP, 0.0)
    SE._post(mb, s * (w / 2 + 1.0), ya - 0.1, foot[2], 1.5, 2.9, lamp=False)


def vil_parapet(mb, pts, z, h=1.35, th=0.95, ends=(True, True)):
    """mureta de cantaria da vila: plinto, corpo em 2 fiadas de blocos com juntas desencontradas (sobre nucleo escuro),
    pingadeira e capa em pecas; pilaretes do kit (remate bola com colar) so nas pontas pedidas"""
    import sg_entry as SE
    n = len(pts)
    for i in range(n - 1):
        a, b = Vector((pts[i][0], pts[i][1], 0.0)), Vector((pts[i + 1][0], pts[i + 1][1], 0.0))
        d = (b - a).normalized()
        ea = a - d * (th / 2 if i > 0 else 0.0)
        eb = b + d * (th / 2 if i < n - 2 else 0.0)
        Ls = (eb - ea).length
        mb.beam((ea.x, ea.y, z + h / 2), (eb.x, eb.y, z + h / 2), th - 0.12, h, M_JNT, 0.0)
        mb.beam((ea.x, ea.y, z + 0.18), (eb.x, eb.y, z + 0.18), th + 0.28, 0.36, M_DRESS, 0.05)      # plinto
        for ci, (c0, c1) in enumerate(((0.36, h),)):
            L0 = 2.4
            off = (0.0, 1.2)[ci % 2]
            cuts = [0.0] + [off + L0 * j for j in range(1, 40) if 0.6 < off + L0 * j < Ls - 0.6] + [Ls]
            for u0, u1 in zip(cuts, cuts[1:]):
                p0 = ea + d * (u0 + (0.04 if u0 > 0 else 0.0))
                p1 = ea + d * (u1 - (0.04 if u1 < Ls else 0.0))
                mb.beam((p0.x, p0.y, z + (c0 + c1) / 2), (p1.x, p1.y, z + (c0 + c1) / 2), th, c1 - c0 - 0.07, M_ASH,
                        0.0)
        mb.beam((ea.x, ea.y, z + h + 0.05), (eb.x, eb.y, z + h + 0.05), th + 0.14, 0.1, M_CAP, 0.0)   # pingadeira
        k = max(1, int(round(Ls / 2.4)))
        for j in range(k):
            p0 = ea + d * (Ls * j / k + (0.03 if j else 0.0))
            p1 = ea + d * (Ls * (j + 1) / k - (0.03 if j < k - 1 else 0.0))
            mb.beam((p0.x, p0.y, z + h + 0.24), (p1.x, p1.y, z + h + 0.24), th + 0.34, 0.28, M_CAP, 0.06)
    for e, p in zip(ends, (pts[0], pts[-1])):
        if e:
            SE._post(mb, p[0], p[1], z, 1.4, h + 0.5, lamp=False)


# ------------------------------------------------------------------ postes de ferro (eixo principal + rua da praca)
LAMPS = [
    # (x, y, z, com_luz)  topo da escada P1P2 / cruzamento do eixo com a rua do P2 / rua da praca (O e L).
    # O pe da escada fica com as lanternas da praca (vestir): par proprio aqui virava cacho de postes.
    (-10.6, -80.6, P2, True), (10.6, -80.6, P2, True),
    (7.8, -51.6, P2, True),
    (-46.0, -125.3, P1, True), (48.0, -112.9, P1, True),
]


def iron_arch(mb, cx, y, z, hs, post_h=10.0, rise=5.4, area="SG_VilLamp"):
    """arco de ferro da vila (transicao praca -> vila alta), refeito com o KIT: postes de ferro FUNDIDO torneados
    (base em sino, anel a 1/3, colar, capitel em prato) sobre soco de obsidiana; VOLUTAS de ferro na nascenca do arco;
    2 trilhos ogivais com montantes; lanternas da ordem penduradas em bracos de mao-francesa curva; remate torneado
    e gota de prata no fecho. Devolve os centros dos vidros (as luzes reais)."""
    import sg_court as CT
    lan = []
    prof_sq = [(-0.05, -0.05), (0.05, -0.05), (0.05, 0.05), (-0.05, 0.05)]
    for s in (-1, 1):
        x = cx + s * hs
        mb.box((1.4, 1.4, 0.35), (x, y, z + 0.175), (0, 0, 0), OBS, 0.05)
        H = post_h - 0.35
        h1 = H * 0.36
        prof = [(0.55, 0.0), (0.55, 0.12), (0.46, 0.2), (0.5, 0.32), (0.34, 0.5), (0.24, 1.2),
                (0.22, h1 - 0.12), (0.3, h1 - 0.05), (0.3, h1 + 0.06), (0.21, h1 + 0.14), (0.18, H - 0.5),
                (0.26, H - 0.42), (0.26, H - 0.3), (0.2, H - 0.24), (0.3, H - 0.1), (0.42, H + 0.02),
                (0.42, H + 0.26), (0.3, H + 0.34)]
        _lathe(mb, (x, y, z + 0.35), prof, BIRON, 6, math.pi / 6, caps=(False, True))
        # voluta: espiral de ferro da face interna do poste ate o trilho de baixo (a nascenca deixa de ser um canto)
        cxv, czv = x - s * 0.62, z + post_h - 0.55
        pts = []
        for i in range(11):
            a = math.pi * 1.5 * i / 10
            rr = 0.62 * (1 - 0.55 * i / 10)
            pts.append((cxv + s * rr * math.cos(a), y, czv + rr * math.sin(a)))
        mb.sweep(pts, prof_sq, BIRON, True, None, up=(0.0, 1.0, 0.0))
        # braco da lanterna com mao-francesa curva
        ax = x - s * 1.25
        mb.beam((x - s * 0.2, y, z + 8.9), (ax + s * 0.1, y, z + 8.9), 0.12, 0.15, BIRON, 0.0)
        pts = []
        for i in range(6):
            a = (math.pi / 2) * i / 5
            pts.append((x - s * (0.22 + 0.8 * (1 - math.cos(a))), y, z + 8.15 + 0.7 * math.sin(a)))
        mb.sweep(pts, prof_sq, BIRON, True, None, up=(0.0, 1.0, 0.0))
        _lathe(mb, (ax, y, z + 8.95), [(0.08, 0.0), (0.12, 0.08), (0.08, 0.18), (0.0, 0.24)], BIRON, 6)
        sl = 0.62
        zb_ = z + 8.55 - 2.30 * sl
        mb.rod((ax, y, z + 8.9), (ax, y, z + 8.5), 0.04, BIRON, 4)
        lan.append(EM.lantern_head(mb, mb, (ax, y, zb_ + EM.LH_BASE * sl), 0.0, sl))
        col_box(area, (1.4, 1.4, post_h + 1.0), (x, y, z + (post_h + 1.0) / 2))
    zs = z + post_h + 0.35
    for off, rad in ((0.0, 0.18), (-0.95, 0.12)):
        for s in (-1, 1):
            p = CT.bez((cx + s * hs, off), (cx + s * hs, 0.52 * rise + off), (cx + s * 0.33 * hs, 0.86 * rise + off),
                       (cx, rise + off), 10)
            pr = [(rad * math.cos(2 * math.pi * i / 6), rad * math.sin(2 * math.pi * i / 6)) for i in range(6)]
            mb.sweep([(px, y, zs + pz) for px, pz in p], pr, BIRON, True, None, up=(0.0, 1.0, 0.0))
    for s in (-1, 1):
        o = CT.bez((cx + s * hs, 0.0), (cx + s * hs, 0.52 * rise), (cx + s * 0.33 * hs, 0.86 * rise), (cx, rise), 10)
        i_ = CT.bez((cx + s * hs, -0.95), (cx + s * hs, 0.52 * rise - 0.95), (cx + s * 0.33 * hs, 0.86 * rise - 0.95),
                    (cx, rise - 0.95), 10)
        for t in (3, 6, 8):
            mb.beam((o[t][0], y, zs + o[t][1] - 0.1), (i_[t][0], y, zs + i_[t][1] + 0.08), 0.1, 0.1, BIRON, 0.0)
    finial_iron(mb, (cx, y, zs + rise + 0.05), 0.75, BIRON)
    _lathe(mb, (cx, y, zs + rise - 2.3), [(0.0, 0.0), (0.16, 0.18), (0.24, 0.42), (0.18, 0.66), (0.06, 0.86),
                                           (0.05, 1.35)], "Metal_SG_Silver", 8)
    return lan


def lamps():
    rng = random.Random(4103)
    mb = MB("SG_Vil_Lamps", COLL, rng, detail="near")
    # topo da escada P1P2: o ARCO de ferro (kit da vila); as 2 luzes continuam nas lanternas do arco
    (xa, ya, za, _), (xb, yb, zb, _) = LAMPS[0], LAMPS[1]
    lan = iron_arch(mb, (xa + xb) / 2, ya, za, abs(xb - xa) / 2)
    for i, (x, y, zc) in enumerate(lan):
        light("L_SGVil_Lamp_%02d" % i, "POINT", (x, y, zc), 260.0, (1.0, 0.7, 0.4), 0.4)
    # postes soltos: o lantern_post da ordem (kit do setor 01); as luzes reais continuam dentro da lanterna
    for i, (x, y, z, lit) in enumerate(LAMPS):
        if i < 2:
            continue
        zc = z + 8.3
        EM.lantern_post(mb, mb, (x, y, z), 0.0, h=7.4)
        col_box("SG_VilLamp", (1.2, 1.2, 9.0), (x, y, z + 4.5))
        if lit:
            light("L_SGVil_Lamp_%02d" % i, "POINT", (x, y, zc), 260.0, (1.0, 0.7, 0.4), 0.4)
    mb.finish()


# ------------------------------------------------------------------ identidade nas casas: estandartes + floreiras
# estandartes pequenos da ordem SO no par do P2 (as 2 casas que ladeiam o eixo nobre na rua transversal: o estandarte
# diz "aqui cruza o caminho da ordem"). OVERHAUL 02: os estandartes das casas SAIRAM; floreiras de chao SO na casa de
# empena de frente de madeira do P2 (sem caixa de janela), em par simetrico; as outras 20 sairam (filler).
HOUSE_BANNERS = []              # OVERHAUL 02: sairam (roxo magico e emblema repetido na vila; o eixo nobre ja diz)
BANNER_W, BANNER_H = 1.8, 4.0
GROUND_PLANTERS = (7,)


def _house_axes(idx):
    x, y, w, d, deg, z = L.HOUSE_LOTS[idx]
    a = math.radians(deg)
    fwd = (math.cos(a), math.sin(a))                  # para onde a fachada olha
    lat = (-fwd[1], fwd[0])
    return x, y, w, d, z, fwd, lat


def ground_planter(mb, x, y, z, fwd, lat):
    """floreira de chao: cocho de pedra media sobre 2 pes, rebordo de remate, terra, folhagem em lobos que transbordam
    a borda e 3 cachos de flores de 2 tons"""
    yaw = math.atan2(lat[1], lat[0])
    for k in (-1, 1):
        mb.box((0.7, 0.34, 0.26), (x + lat[0] * k * 0.62, y + lat[1] * k * 0.62, z + 0.13), (0, 0, yaw), M_DRESS,
               B_PROP)
    mb.box((1.76, 0.74, 0.46), (x, y, z + 0.49), (0, 0, yaw), M_DRESS, B_PROP)
    mb.box((1.92, 0.9, 0.1), (x, y, z + 0.77), (0, 0, yaw), M_CAP, 0.03)
    # face de referencia: tangente = -lat -> normal = fwd (o "off" positivo aponta para a rua)
    f2 = Face(Frame(x, y, z, 0.0), (0.0, 0.0), (-lat[0], -lat[1]), 1.8)
    # jardinagem 2026-09-29: terra + plantio do kit (campanulas e flores-da-lua, folhas pendentes)
    import sg_garden as GD
    mb.box((1.62, 0.6, 0.08), (x, y, z + 0.78), (0, 0, yaw), GD.SOIL, 0.0)
    GD.ground_planter_planting(mb, f2, 0.82, 1.5)          # (z relativo: o Face ja soma o piso)


def house_identity(mb):
    for idx, hz in HOUSE_BANNERS:
        x, y, w, d, z, fwd, lat = _house_axes(idx)
        # quina da fachada mais perto do eixo (x = 0)
        s = 1.0 if -x * lat[0] > 0 else -1.0
        jet = SPECS[idx].get("jetty", 0.0)
        wall = (x + fwd[0] * (d / 2 + jet) + lat[0] * s * (w / 2 - 1.1),
                y + fwd[1] * (d / 2 + jet) + lat[1] * s * (w / 2 - 1.1))
        reach = BANNER_W / 2 + 0.55
        top = (wall[0] + fwd[0] * reach, wall[1] + fwd[1] * reach, z + hz)
        yaw = math.atan2(lat[1] * s, lat[0] * s)
        EM.banner(mb, mb, mb, mb, top, yaw, BANNER_W, BANNER_H, trim=EM.GOLD)
        mb.beam((wall[0], wall[1], z + hz - 1.5), (wall[0] + fwd[0] * (reach * 2 - 0.2), wall[1] + fwd[1] * (reach * 2 - 0.2),
                                                   z + hz - 0.05), 0.12, 0.14, IRON, 0.0)
        mb.box((0.44, 0.14, 0.9), (wall[0] + fwd[0] * 0.07, wall[1] + fwd[1] * 0.07, z + hz - 1.3), (0, 0, yaw), IRON,
               B_CAST)
    for idx in GROUND_PLANTERS:
        x, y, w, d, z, fwd, lat = _house_axes(idx)
        for s in (-1, 1):
            off = d / 2 + 0.42 + 0.62
            px = x + fwd[0] * off + lat[0] * s * (w / 2 - 1.6)
            py = y + fwd[1] * off + lat[1] * s * (w / 2 - 1.6)
            ground_planter(mb, px, py, z, fwd, lat)
            col_box("SG_VilPlanter", (0.95, 1.95, 1.0), (px, py, z + 0.4), (0, 0, math.atan2(fwd[1], fwd[0])))
    mb.finish()


# ------------------------------------------------------------------ build
def build():
    rng = random.Random(4100)
    plaza()
    streets()
    LIFE[0] = MB("SG_Vil_HouseDress", COLL, random.Random(4104), detail="near")
    for gname, idxs in GROUPS:
        mb = MB("SG_Vil_Houses_%s" % gname, COLL, rng, detail="near")
        for i in idxs:
            house(mb, i, L.HOUSE_LOTS[i], SPECS[i], rng)
        mb.finish()
    lamps()
    house_identity(LIFE[0])
    LIFE[0] = None
