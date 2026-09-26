# db_props - VESTIR (onda 3), PROPS da Ilha 2 (Dragon Ball): prefixo DB_Prop_, colecao 09_PROPS.
# Conta a historia Capsule/mineracao SEM texto, logo ou personagem:
#   - caixas Capsule (caixas brancas/azuis arredondadas, cinta, trava, botao) em pilhas pequenas + capsula-conteiner
#     deitada no berco; tambores de combustivel amarelos com cintas azul-marinho;
#   - quiosques Capsule sem texto: maquina de capsulas (gacha: janela de vidro com bolinhas coloridas, capsula
#     gigante deitada no topo) e cabine redonda (vidro na frente, anel ciano, beiral, cupula azul, antena);
#   - bancos Capsule, postes Capsule (lampiao ambar entre discos brancos, capuz azul) SO nos cruzamentos das trilhas
#     radiais com o promenade (onde nenhuma zona pos luz), 1 lanterna de pedra na aproximacao do summon;
#   - mercado: carrinho de frutas com toldo + cestos, sacos e potes no passeio (os balcoes do db_village ja estao
#     cheios de mercadoria); dojo: patio de treino ao sul (tatames laranja/marinho, suporte de barras, kettlebells,
#     barra fixa, saco de pancada); oficina: patio de pecas ao sul (motor no palete, bau de ferramentas, cilindros de
#     gas, disco de flutuacao sobressalente, caixas, tambores) + scooter Capsule; 2 scooters no total;
#   - mineracao na BORDA DE FORA do promenade: carrinhos VAZIOS no toco de trilho, tremonhas VAZIAS, cavaletes de
#     picaretas; NADA na arena; seixos pequenos FORA da arena.
#   - rodada final (criticos): LANTERNAS DE CAMINHO so emissivas (Lantern_Glow, SEM objeto de luz, SEM colisao: o teto
#     de colisoes do vestir e 90 e a vegetacao ja usa 45) - poste Capsule leve a cada ~12 alternando os lados das 4
#     trilhas radiais, par no pe e no topo das escadas da vila/saida (onde nenhuma zona ja pos lanterna; a da saida e
#     marcial como as bochechas dela), lanterna marcial a cada ~16 no lado de dentro da trilha da saida ate a
#     transicao Shadow Garden; linha de postes de topo CIANO no lado sul da rua da vila (x 16..63 + o par do topo da
#     escada lateral leste) + seta de piso azul (>>) na juncao rua/ligacao da saida + mastro-farol ciano (~48) do lado
#     da vila, visivel por cima da oficina do topo da escadaria do Capsule.
#   - moitas: 1a passada recusa posicao com parte solta de DB_Veg_Shrubs a menos de r+0,5; se so moita impede, a 2a
#     passada escolhe a que menos pisa em moita e, no fim, as partes de moita que um prop ATRAVESSA (BVH) saem.
# Tudo e validado NA HORA do build contra a cena (as outras zonas e a vegetacao ja montadas): raios verticais na
# colisao (COL_*) e no visual (malhas DB_*, inclusive DB_Veg_*), nivel do piso, rotas do db_qa (+ modulos), escadas,
# marcadores (NPC_/PLAYER_INTERACT_/SUMMON_/...), disco e zona livre do summon, arena, pontes e vaos de porta.
# Cada grupo tem posicoes alternativas; o que nao cabe e PULADO e impresso ("PROPS pulado ...").
# Colisao so dos props grandes (pilhas de caixas, quiosques, carrinhos, tremonhas, cavaletes, postes dos
# cruzamentos, bancos, mastro-farol),
# caixas simples DENTRO do visual, topo = topo do visual onde da para subir.
# Orcamento da fatia (de 50k/90/6/90/12 do vestir): 20k tris, 40 MeshParts, 3 materiais novos, 45 colisoes.
# Objetos por KIT (1 MeshPart por material): DB_Prop_Capsule (branco/azul/marinho/vidro/ciano/amarelo/lampiao),
# DB_Prop_Work (madeira/metal/lona/seixos), DB_Prop_Market (mercado), DB_Prop_Dojo (patio de treino).
import math, random
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import fm_lib
import db_lib as DL
from db_lib import col_box, Frame
import db_layout as L
import db_col
import db_capsule_kit as K
import db_village_kit as VG

C = "09_PROPS"
GUTTER = 3.0            # sarjeta do chao em volta do promenade (db_terrain: o chao so comeca ~0,5-3 alem da borda)
G, H, A = L.GROUND, L.HUB, L.ARENA

# ------------------------------------------------------------------ materiais (2 novos de 3)
fm_lib.MATS.setdefault("Plaster_DBPropYellow", (fm_lib.S(246, 190, 46), 0.55, 0.0, 0, None, 0.0))   # tambor/bau
WHITE, BLUE, NAVY, GLASS = "Plaster_DB_White", "Roof_DB_Blue", "Plaster_DB_Navy", "Glass_DB_Blue"
CYAN, YELLOW, LAMP = "DB_Cyan_Glow", "Plaster_DBPropYellow", "Lantern_Glow"
WD, WP, DARK, STEEL, CANVAS = "Wood_Dark", "Wood_Plank", "Metal_DB_Dark", "Metal_DB_Steel", "Cloth_Canvas"
ROCK, ROCKD = "Cliff_Rock_DB", "Cliff_Rock_DB_Dark"
fm_lib.MATS.setdefault("Cloth_DBPropBurlap", (fm_lib.S(172, 128, 80), 0.95, 0.0, 0, None, 0.0))    # juta dos sacos
SACK = "Cloth_DBPropBurlap"
ORANGE, LACQ, APPLE, LEAF, CLOTH = "Roof_DB_Orange", "Wood_Lacquer_Red", "DB_Star_Red", "Leaf_Palm", "Cloth_Red"

# ------------------------------------------------------------------ cameras de revisao (altura do jogador + 360)
CAMS = {
    "CAM_DBProp_Market": ((-66.0, 95.0, H + 5.2), (-86.0, 110.0, H + 2.4), 22),
    "CAM_DBProp_MarketW": ((-100.0, 94.0, H + 5.2), (-84.0, 110.0, H + 2.0), 22),
    "CAM_DBProp_MarketCart": ((-82.5, 96.5, H + 5.2), (-76.0, 102.0, H + 2.6), 22),
    "CAM_DBProp_Village": ((-20.0, 86.0, H + 5.2), (-36.0, 96.0, H + 3.0), 22),
    "CAM_DBProp_Dojo": ((106.0, -52.0, G + 6.0), (121.0, -35.0, G + 2.0), 22),
    "CAM_DBProp_DojoN": ((136.0, -26.0, G + 7.0), (116.0, -40.0, G + 1.0), 22),
    "CAM_DBProp_PromS": ((-6.0, -64.0, G + 5.2), (-30.0, -78.0, G + 2.0), 22),
    "CAM_DBProp_PromSW": ((-58.0, -20.0, G + 5.2), (-78.0, -38.0, G + 2.0), 22),
    "CAM_DBProp_PromNE": ((24.0, 44.0, G + 5.2), (46.0, 62.0, G + 2.0), 22),
    "CAM_DBProp_PromSE": ((62.0, -16.0, G + 5.2), (80.0, -38.0, G + 2.0), 22),
    "CAM_DBProp_Workshop": ((18.0, 82.0, H + 5.2), (36.0, 96.0, H + 2.0), 22),
    "CAM_DBProp_Heli": ((-104.0, 52.0, G + 6.0), (-122.0, 68.0, G + 2.0), 22),
    "CAM_DBProp_Exit": ((52.0, 28.0, G + 5.2), (66.0, 46.0, G + 3.0), 22),
    "CAM_DBProp_EntryE": ((6.0, -96.0, G + 5.2), (28.0, -76.0, G + 3.0), 22),
    "CAM_DBProp_Overview": ((0.0, -200.0, 125.0), (0.0, -30.0, 18.0), 22),
    # lanternas de caminho e a linha ate a saida (rodada final)
    "CAM_DBProp_CapStairE": ((0.0, 131.0, L.CAP + 5.2), (112.0, 53.0, H + 6.0), 22),
    "CAM_DBProp_StreetE": ((14.0, 86.0, H + 5.2), (96.0, 84.0, H + 3.0), 24),
    "CAM_DBProp_PathSW": ((-50.0, -58.0, G + 5.2), (-110.0, -76.0, G + 3.0), 22),
    "CAM_DBProp_PathW": ((-72.0, 14.0, G + 5.2), (-120.0, 48.0, G + 3.0), 22),
    "CAM_DBProp_PathSE": ((50.0, -56.0, G + 5.2), (112.0, -60.0, G + 3.0), 22),
    "CAM_DBProp_HubStair": ((0.0, 52.0, G + 6.0), (0.0, 80.0, H + 3.0), 22),
    "CAM_DBProp_ExitPath": ((70.0, 20.0, G + 6.2), (126.0, 62.0, L.EXIT_Z + 3.0), 22),
    "CAM_DBProp_LanternsAir": ((40.0, -150.0, 150.0), (10.0, -10.0, 20.0), 24),
    "CAM_DBProp_Junction": ((84.0, 94.0, H + 5.2), (106.0, 78.0, H + 0.5), 22),
    "CAM_DBProp_HubStairW": ((-78.0, 54.0, G + 6.0), (-78.0, 82.0, H + 3.0), 22),
}

EXTRA_ROUTES = {}
EXTRA_PROBES = []

# posicoes das luzes dos postes que este modulo montou (o db_lights acende SO os postes que ficaram)
LAMP_SPOTS = []          # (nome da luz, centro, energia W, cor) - acesas pelo db_lights
WARM = (1.0, 0.62, 0.3)
WARM_W = (1.0, 0.76, 0.52)
REPORT = []


# ------------------------------------------------------------------ util de geometria
def yaw_to(x, y, tx, ty):
    return math.atan2(ty - y, tx - x)


def rbox(mb, size, loc, yaw, m, bev=0.2):
    """caixa ARREDONDADA de verdade (chanfro em todas as arestas: o MB do lobby, sem a regra de chanfro do VMB)"""
    fm_lib.MB.box(mb, size, tuple(loc), (0.0, 0.0, yaw), m, bev, 1)


def ico(mb, r, c, m, sub=0):
    fm_lib.MB.ico(mb, r, tuple(c), m, sub)


def dome(mb, c, r, z0, m, n=12, k=3, sq=1.0):
    """cupula solida (torno): quarto de circulo de raio r sobre z0"""
    prof = [(0.06, z0), (r, z0)]
    for i in range(1, k):
        t = (math.pi / 2) * i / k
        prof.append((r * math.cos(t), z0 + r * sq * math.sin(t)))
    prof.append((0.06, z0 + r * sq))
    K.lathe(mb, c, prof, m, n)


# ------------------------------------------------------------------ KIT CAPSULE (objeto DB_Prop_Capsule)
def cap_crate(mb, x, y, z, s, yaw, body=WHITE, band=BLUE, latch=True, button=False):
    """caixa Capsule: corpo arredondado, cinta no meio, trava marinho na frente (+x local), botao no topo"""
    F = Frame(x, y, z, yaw)
    h = s * 0.84
    rbox(mb, (s, s, h), F.p(0, 0, h / 2), yaw, body, 0.26 * s / 2.4)
    mb.box((s + 0.08, s + 0.08, 0.32), F.p(0, 0, h * 0.52), F.r(), band, 0.0)
    if latch:
        mb.box((0.14, 0.7, 0.56), F.p(s / 2 + 0.07, 0, h * 0.52), F.r(), NAVY, 0.0)
    if button:
        mb.cyl(0.36, 0.14, F.p(0, 0, h + 0.07), F.r(), NAVY if body != NAVY else BLUE, 8, bevel=0.0)
    return z + h


def capsule_container(mb, x, y, z, yaw):
    """capsula gigante deitada (o formato Capsule, sem texto) num berco azul-marinho"""
    F = Frame(x, y, z, yaw)
    R, hl = 1.05, 1.35
    ax = F.p(1, 0) - F.p(0, 0)
    VG.pill(mb, F.p(0, 0, R + 0.42), (ax.x, ax.y, 0.0), R, hl, WHITE, n=12, k_cap=3, nose=(BLUE, 38.0),
            tail=(BLUE, 38.0))
    mb.box((2 * hl + 0.3, 0.36, 0.36), F.p(0, 0, R + 0.42), F.r(), BLUE, 0.0)
    for sx in (-1, 1):
        mb.box((0.55, 1.9, 0.62), F.p(sx * hl * 0.72, 0, 0.31), F.r(), NAVY, 0.0)
    return 2 * R + 0.42


def drum(mb, x, y, z, m=YELLOW, r=0.88, h=2.25):
    """tambor de combustivel: corpo, 2 cintas (aneis abertos), tampa com bocal"""
    mb.cyl(r, h, (x, y, z + h / 2), (0, 0, 0), m, 12, bevel=0.0)
    for zz in (0.5, h - 0.5):
        mb.cyl(r + 0.07, 0.24, (x, y, z + zz), (0, 0, 0), NAVY, 12, bevel=0.0, caps=False)
    mb.cyl(0.26, 0.16, (x + r * 0.45, y, z + h + 0.08), (0, 0, 0), NAVY, 6, bevel=0.0)
    return z + h


def drum_group(mb, x, y, z, yaw, n=3, area="DB_PropDrums"):
    """2 tambores lado a lado (+1 encaixado atras); colisao: 1 caixa por fileira, dentro dos tambores"""
    F = Frame(x, y, z, yaw)
    pts = [(-0.95, -0.95), (0.95, -0.95), (0.0, 0.7)][:n]
    for i, (u, v) in enumerate(pts):
        p = F.p(u, v)
        drum(mb, p.x, p.y, z, YELLOW if i != 2 else BLUE)
    col_box(area, (3.0, 1.2, 2.25), F.p(0.0, -0.95, 1.125), F.r())
    if n > 2:
        col_box(area, (1.2, 1.2, 2.25), F.p(0.0, 0.7, 1.125), F.r())


def kiosk_vend(mb, x, y, z, yaw, area="DB_PropKiosk"):
    """maquina de capsulas (quiosque Capsule sem texto): frente = +x local"""
    F = Frame(x, y, z, yaw)
    mb.box((2.1, 2.9, 0.42), F.p(0, 0, 0.21), F.r(), NAVY, 0.0)
    rbox(mb, (1.8, 2.6, 4.0), F.p(0, 0, 0.42 + 2.0), yaw, WHITE, 0.32)
    mb.box((1.84, 2.64, 0.34), F.p(0, 0, 1.9), F.r(), BLUE, 0.0)
    rbox(mb, (2.1, 2.9, 0.7), F.p(0, 0, 4.42 + 0.35), yaw, BLUE, 0.28)
    # janela de vidro com as capsulas (meio-embutidas: no Roblox o vidro e translucido)
    mb.box((0.12, 1.9, 1.75), F.p(0.92, 0, 3.25), F.r(), GLASS, 0.0)
    rng = random.Random(int(x * 7 + y * 13) & 0xffff)
    cols = [YELLOW, BLUE, WHITE, YELLOW, NAVY, WHITE]
    for i in range(6):
        u = -0.62 + 0.62 * (i % 3) + rng.uniform(-0.08, 0.08)
        v = 2.72 + 0.62 * (i // 3) + rng.uniform(-0.05, 0.05)
        ico(mb, 0.27, F.p(0.93, u, v), cols[i], 0)
    # tela ciano (sem texto), boca de saida, manopla
    mb.box((0.1, 0.9, 0.5), F.p(0.91, 0.55, 2.2), F.r(), CYAN, 0.0)
    mb.box((0.3, 1.1, 0.5), F.p(0.86, -0.25, 1.05), F.r(), NAVY, 0.0)
    K.cyl_axis(mb, 0.26, 0.3, F.p(0.98, -0.55, 2.2), F.p(1, 0) - F.p(0, 0), NAVY, 8)
    # capsula gigante deitada no topo (o "letreiro" sem letra)
    ax = F.p(0, 1) - F.p(0, 0)
    VG.pill(mb, F.p(0, 0, 5.12 + 0.52), (ax.x, ax.y, 0.0), 0.52, 0.75, YELLOW, n=10, k_cap=3, nose=(WHITE, 40.0),
            tail=(WHITE, 40.0))
    col_box(area, (1.7, 2.5, 5.1), F.p(0, 0, 2.55), F.r())
    return z + 6.2


def kiosk_booth(mb, x, y, z, yaw, area="DB_PropKiosk"):
    """cabine Capsule redonda (informacao/comunicador, sem texto): frente de vidro para +x local"""
    F = Frame(x, y, z, yaw)
    c = (x, y)
    r = 1.45
    mb.cyl(1.75, 0.36, (x, y, z + 0.18), (0, 0, 0), NAVY, 12, bevel=0.0)
    mb.cyl(r, 4.3, (x, y, z + 0.36 + 2.15), (0, 0, 0), WHITE, 14, bevel=0.0)
    a0 = math.degrees(yaw)
    K.lathe(mb, c, [(r - 0.05, z + 1.1), (r + 0.1, z + 1.1), (r + 0.1, z + 4.0), (r - 0.05, z + 4.0)], GLASS, 6,
            a0 - 52.0, a0 + 52.0)
    K.lathe(mb, c, [(r - 0.02, z + 0.62), (r + 0.12, z + 0.62), (r + 0.12, z + 0.9), (r - 0.02, z + 0.9)], BLUE, 14)
    K.lathe(mb, c, [(r - 0.02, z + 4.25), (r + 0.1, z + 4.25), (r + 0.1, z + 4.45), (r - 0.02, z + 4.45)], CYAN, 14)
    mb.cyl(2.05, 0.3, (x, y, z + 4.66 + 0.15), (0, 0, 0), WHITE, 14, bevel=0.0)
    dome(mb, c, 1.55, z + 4.96, BLUE, 14, 3, 0.8)
    top = z + 4.96 + 1.55 * 0.8
    mb.rod((x, y, top - 0.1), (x, y, top + 1.1), 0.09, NAVY, 5)
    ico(mb, 0.24, (x, y, top + 1.2), CYAN, 0)
    col_box(area, (2.0, 2.0, 4.8), (x, y, z + 2.4), (0, 0, yaw))
    return top + 1.4


def cap_lamp(mb, x, y, z, h=4.4, area="DB_PropLamp", col=True, lite=False, glow=LAMP):
    """poste Capsule (a familia do portal/vila): soco marinho, fuste branco com anel azul, lampiao ambar entre discos
    brancos, capuz azul. Devolve o centro do lampiao.
    lite: o mesmo desenho com menos lados (os postes de caminho/escada, que se repetem as dezenas);
    col=False: so visual (poste de caminho FORA da faixa de andar; o teto de colisoes do vestir nao comporta 1 caixa
    por poste); glow: o material do lampiao (ambar; ciano = a linha de postes que leva a saida)."""
    if lite:                     # ~150 tris: soco e fuste sextavados, sem pescoco, capuz conico
        mb.cyl(0.85, 0.5, (x, y, z + 0.25), (0, 0, math.pi / 6), NAVY, 6, bevel=0.0)
        mb.cyl(0.32, h + 0.42, (x, y, z + 0.5 + (h + 0.42) / 2), (0, 0, 0), WHITE, 6, bevel=0.0, caps=False)
        mb.cyl(0.46, 0.36, (x, y, z + 0.5 + h * 0.42), (0, 0, 0), BLUE, 6, bevel=0.0)
        t = z + 0.5 + h
        mb.cyl(0.86, 0.24, (x, y, t + 0.54), (0, 0, 0), WHITE, 8, bevel=0.0)
        mb.cyl(0.58, 1.2, (x, y, t + 0.66 + 0.6), (0, 0, 0), glow, 8, bevel=0.0, caps=False)
        mb.cyl(0.9, 0.24, (x, y, t + 1.86 + 0.12), (0, 0, 0), WHITE, 8, bevel=0.0)
        mb.cyl(0.74, 0.62, (x, y, t + 2.1 + 0.31), (0, 0, 0), BLUE, 8, r2=0.14, bevel=0.0)
        if col:
            col_box(area, (0.95, 0.95, t + 2.1 - z), (x, y, (z + t + 2.1) / 2))
        return Vector((x, y, t + 1.26))
    n1, n2 = 10, 8
    mb.cyl(0.85, 0.5, (x, y, z + 0.25), (0, 0, 0), NAVY, n1, bevel=0.0)
    mb.cyl(0.32, h, (x, y, z + 0.5 + h / 2), (0, 0, 0), WHITE, n2, bevel=0.0)
    mb.cyl(0.46, 0.36, (x, y, z + 0.5 + h * 0.42), (0, 0, 0), BLUE, n2, bevel=0.0)
    t = z + 0.5 + h
    mb.cyl(0.36, 0.42, (x, y, t + 0.21), (0, 0, 0), NAVY, n2, bevel=0.0)
    mb.cyl(0.86, 0.24, (x, y, t + 0.54), (0, 0, 0), WHITE, n1, bevel=0.0)
    mb.cyl(0.58, 1.2, (x, y, t + 0.66 + 0.6), (0, 0, 0), glow, n1, bevel=0.0)
    mb.cyl(0.9, 0.24, (x, y, t + 1.86 + 0.12), (0, 0, 0), WHITE, n1, bevel=0.0)
    dome(mb, (x, y), 0.72, t + 2.1, BLUE, n1, 2, 0.8)
    if col:
        col_box(area, (0.95, 0.95, t + 2.1 - z), (x, y, (z + t + 2.1) / 2))
    return Vector((x, y, t + 1.26))


def beacon_mast(mb, x, y, z, area="DB_PropBeacon"):
    """mastro-farol Capsule (sem texto): soco marinho octogonal, fuste branco afunilado com aneis azuis e 2 faixas
    ciano acesas, plataforma branca, farol ciano entre discos, capuz azul e antena com ponta ciano.
    ~48 de altura (abaixo das torres comm/mirante): o farol passa por cima da abobada da oficina para quem esta no
    topo da escadaria do Capsule e marca o caminho da saida."""
    mb.cyl(1.75, 0.8, (x, y, z + 0.4), (0, 0, math.pi / 8), NAVY, 8, bevel=0.0)
    mb.cyl(1.25, 0.6, (x, y, z + 1.1), (0, 0, math.pi / 8), WHITE, 8, bevel=0.0)
    H = 40.0
    mb.cyl(0.7, H, (x, y, z + 1.4 + H / 2), (0, 0, 0), WHITE, 10, r2=0.42, bevel=0.0, caps=False)
    for k, f in enumerate((0.16, 0.34, 0.52, 0.70, 0.88)):
        rr = 0.7 + (0.42 - 0.7) * f + 0.14
        mb.cyl(rr, 0.55, (x, y, z + 1.4 + H * f), (0, 0, 0), CYAN if k in (1, 3) else BLUE, 10, bevel=0.0)
    t = z + 1.4 + H
    mb.cyl(1.5, 0.36, (x, y, t + 0.18), (0, 0, 0), WHITE, 12, bevel=0.0)
    mb.cyl(1.62, 0.2, (x, y, t + 0.46), (0, 0, 0), BLUE, 12, bevel=0.0)
    mb.cyl(0.95, 2.0, (x, y, t + 0.56 + 1.0), (0, 0, 0), CYAN, 10, bevel=0.0, caps=False)
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        mb.box((0.2, 0.2, 2.0), (x + math.cos(a) * 1.0, y + math.sin(a) * 1.0, t + 1.56), (0, 0, a), NAVY, 0.0)
    mb.cyl(1.35, 0.3, (x, y, t + 2.56 + 0.15), (0, 0, 0), WHITE, 12, bevel=0.0)
    dome(mb, (x, y), 1.1, t + 2.86, BLUE, 12, 3, 0.7)
    top = t + 2.86 + 1.1 * 0.7
    mb.rod((x, y, top - 0.1), (x, y, top + 2.6), 0.1, NAVY, 5)
    ico(mb, 0.36, (x, y, top + 2.8), CYAN, 1)
    col_box(area, (2.3, 2.3, 1.4 + H), (x, y, z + (1.4 + H) / 2), (0, 0, math.pi / 8))     # 1 caixa so (teto)
    return top + 3.2


def chevron(mb, x, y, z, yaw, m=BLUE, n=2, gap=2.3):
    """seta de piso (>>) de lajotas azuis planas, sem texto: pontas para +x local; topo = z"""
    F = Frame(x, y, 0.0, yaw)
    th = 0.1
    for k in range(n):
        u0 = (k - (n - 1) / 2.0) * gap
        for sg in (-1, 1):
            # braco: paralelogramo da ponta (u0, 0) para tras e para o lado
            tip_o, tip_i = (u0 + 0.62, 0.0), (u0 - 0.62, 0.0)
            back_o, back_i = (u0 - 1.35, sg * 1.95), (u0 - 2.59, sg * 1.95)
            pts = [F.p(*tip_o), F.p(*back_o), F.p(*back_i), F.p(*tip_i)]
            pts = [(p.x, p.y) for p in pts]
            if sg < 0:
                pts.reverse()
            mb.prism(pts, z - th, z, m, 0.0)


def bench(mb, x, y, z, yaw, area="DB_PropBench"):
    """banco Capsule: 2 pes marinho, assento branco arredondado, encosto azul (quem senta olha para +x local)"""
    F = Frame(x, y, z, yaw)
    for sy in (-1, 1):
        mb.box((1.3, 0.5, 1.0), F.p(0.0, sy * 1.7, 0.5), F.r(), NAVY, 0.0)
        mb.box((0.3, 0.4, 1.3), F.p(-0.62, sy * 1.7, 1.6), F.r(0, -0.18, 0), NAVY, 0.0)
    rbox(mb, (1.6, 4.4, 0.3), F.p(0, 0, 1.15), yaw, WHITE, 0.1)
    fm_lib.MB.box(mb, (0.26, 4.4, 0.85), tuple(F.p(-0.72, 0, 2.05)), F.r(0, -0.18, 0), BLUE, 0.1, 1)
    col_box(area, (1.5, 4.2, 1.3), F.p(0, 0, 0.65), F.r())


def scooter(mb, x, y, z, yaw, area="DB_PropScooter"):
    """scooter Capsule flutuante estacionada (frente = +x local): casco-capsula branco com nariz azul, banco
    marinho, coluna e guidao, farol ciano, 2 sapatas de flutuacao com brilho ciano, pezinho, aleta azul"""
    F = Frame(x, y, z, yaw)
    fw = F.p(1, 0) - F.p(0, 0)
    VG.pill(mb, F.p(0.0, 0, 1.3), (-fw.x, -fw.y, 0.0), 0.6, 1.05, WHITE, n=10, k_cap=3, nose=(BLUE, 42.0))
    K.cyl_axis(mb, 0.64, 0.3, F.p(-0.25, 0, 1.3), fw, BLUE, 10)
    mb.box((1.15, 0.72, 0.26), F.p(-0.45, 0, 1.97), F.r(), NAVY, 0.0)
    mb.rod(F.p(0.85, 0, 1.6), F.p(1.12, 0, 2.7), 0.12, NAVY, 6)
    mb.rod(F.p(1.12, -0.72, 2.72), F.p(1.12, 0.72, 2.72), 0.09, NAVY, 6)
    for sg in (-1, 1):
        mb.rod(F.p(1.12, sg * 0.5, 2.72), F.p(1.12, sg * 0.85, 2.72), 0.14, BLUE, 6)
    K.cyl_axis(mb, 0.24, 0.22, F.p(1.27, 0, 2.38), fw, CYAN, 8)
    mb.box((0.12, 0.95, 0.6), F.p(1.02, 0, 2.95), F.r(0, -0.35, 0), GLASS, 0.0)
    for sx in (-0.95, 0.95):
        mb.cyl(0.52, 0.32, F.p(sx, 0, 0.62), F.r(), NAVY, 10, bevel=0.0)
        mb.cyl(0.4, 0.1, F.p(sx, 0, 0.42), F.r(), CYAN, 10, bevel=0.0)
    mb.beam(F.p(-0.2, 0.38, 1.0), F.p(-0.1, 0.9, 0.05), 0.2, 0.22, NAVY, 0.0)
    mb.box((1.0, 0.18, 0.5), F.p(-1.35, 0, 1.75), F.r(0, -0.35, 0), BLUE, 0.0)
    col_box(area, (3.2, 1.5, 2.2), F.p(0.05, 0, 1.1), F.r())


def tool_chest(mb, x, y, z, yaw):
    """bau de ferramentas amarelo Capsule com gavetas marinho (frente = +x local)"""
    F = Frame(x, y, z, yaw)
    rbox(mb, (1.5, 2.6, 2.2), F.p(0, 0, 1.1), yaw, YELLOW, 0.14)
    for k in range(3):
        mb.box((0.1, 2.2, 0.42), F.p(0.78, 0, 0.55 + 0.6 * k), F.r(), NAVY, 0.0)
    mb.box((1.62, 2.72, 0.24), F.p(0, 0, 2.3), F.r(), NAVY, 0.0)


def gas_cylinders(mb, x, y, z, yaw):
    F = Frame(x, y, z, yaw)
    for i, (u, v, m) in enumerate(((0.0, -0.55, BLUE), (0.0, 0.45, WHITE), (0.75, -0.05, BLUE))):
        p = F.p(u, v)
        mb.cyl(0.42, 2.4, (p.x, p.y, z + 1.2), (0, 0, 0), m, 10, bevel=0.0)
        mb.cyl(0.42, 0.4, (p.x, p.y, z + 2.6), (0, 0, 0), m, 10, r2=0.16, bevel=0.0)
        mb.cyl(0.12, 0.3, (p.x, p.y, z + 2.9), (0, 0, 0), NAVY, 6, bevel=0.0)


def spare_pad(mb, x, y, z, yaw):
    """sapata de flutuacao sobressalente encostada (disco marinho com anel ciano)"""
    F = Frame(x, y, z, yaw)
    ax = F.p(math.cos(0.35), 0, math.sin(0.35)) - F.p(0, 0, 0)
    c = F.p(0.0, 0, 1.25)
    K.cyl_axis(mb, 1.25, 0.42, c, ax, NAVY, 14)
    K.cyl_axis(mb, 0.9, 0.12, c + ax.normalized() * 0.25, ax, CYAN, 14)


# ------------------------------------------------------------------ KIT DE TRABALHO (objeto DB_Prop_Work)
def rails_stub(mw, F, ln=5.4):
    for u in (-ln / 2 + 0.6, 0.0, ln / 2 - 0.6):
        mw.box((0.62, 3.3, 0.24), F.p(u, 0, 0.12), F.r(), WD, 0.0)
    for sy in (-1, 1):
        mw.box((ln, 0.3, 0.3), F.p(0, sy * 1.1, 0.39), F.r(), STEEL, 0.0)
    mw.box((0.55, 3.1, 0.9), F.p(ln / 2 + 0.2, 0, 0.45), F.r(), WD, 0.0)


def mine_cart(mw, x, y, z, yaw, rails=True, area="DB_PropCart"):
    """carrinho de mina VAZIO (fundo escuro a mostra) sobre um toco de trilho com para-choque; frente = +x local"""
    F = Frame(x, y, z, yaw)
    if rails:
        rails_stub(mw, F)
    zw = 0.54 + 0.5 if rails else 0.5
    for sx in (-1, 1):
        for sy in (-1, 1):
            K.cyl_axis(mw, 0.5, 0.26, F.p(sx * 1.0, sy * 1.1, zw), F.p(0, 1) - F.p(0, 0), DARK, 8)
    mw.box((2.9, 1.9, 0.3), F.p(0, 0, zw + 0.32), F.r(), DARK, 0.0)
    zb = zw + 0.47
    mw.cyl(1.55, 1.45, F.p(0, 0, zb + 0.725), F.r(0, 0, math.pi / 4), STEEL, 4, r2=1.98, bevel=0.0)
    zt = zb + 1.45
    mw.box((2.5, 2.5, 0.08), F.p(0, 0, zt + 0.02), F.r(), DARK, 0.0)
    for sx in (-1, 1):
        mw.box((0.24, 2.9, 0.26), F.p(sx * 1.42, 0, zt), F.r(), DARK, 0.0)
        mw.box((2.9, 0.24, 0.26), F.p(0, sx * 1.42, zt), F.r(), DARK, 0.0)
    mw.box((0.5, 0.9, 0.35), F.p(-1.75, 0, zw + 0.3), F.r(), DARK, 0.0)
    col_box(area, (3.0, 2.8, zt + 0.13), F.p(0, 0, (zt + 0.13) / 2), F.r())
    return z + zt


def ore_bin(mw, x, y, z, yaw, area="DB_PropBin"):
    """tremonha de madeira VAZIA sobre 4 pes, cantoneiras de ferro e bica de chapa (frente = +x local)"""
    F = Frame(x, y, z, yaw)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mw.box((0.45, 0.45, 1.7), F.p(sx * 1.35, sy * 0.95, 0.85), F.r(), WD, 0.0)
    z0, z1 = 1.6, 3.3
    mw.box((3.2, 2.4, 0.25), F.p(0, 0, z0 + 0.12), F.r(), DARK, 0.0)
    for sx in (-1, 1):
        mw.box((0.28, 2.4, z1 - z0), F.p(sx * 1.46, 0, (z0 + z1) / 2), F.r(), WP, 0.0)
        mw.box((3.2, 0.28, z1 - z0), F.p(0, sx * 1.06, (z0 + z1) / 2), F.r(), WP, 0.0)
        for sy in (-1, 1):
            mw.box((0.36, 0.36, z1 - z0 + 0.1), F.p(sx * 1.52, sy * 1.12, (z0 + z1) / 2), F.r(), DARK, 0.0)
    mw.box((1.3, 1.1, 0.16), F.p(2.05, 0, z0 - 0.35), F.r(0, 0.5, 0), STEEL, 0.0)
    for sy in (-1, 1):
        mw.box((1.3, 0.14, 0.45), F.p(2.05, sy * 0.55, z0 - 0.2), F.r(0, 0.5, 0), STEEL, 0.0)
    col_box(area, (3.1, 2.3, z1), F.p(0, 0, z1 / 2), F.r())
    return z + z1


def pickaxe(mw, a, b, hd):
    a, b, hd = Vector(a), Vector(b), Vector(hd)
    ax = (b - a).normalized()
    hd = (hd - ax * hd.dot(ax)).normalized()
    mw.beam(a, b + ax * 0.12, 0.2, 0.2, WP, 0.0)
    for sg in (-1, 1):
        mw.beam(b, b + hd * sg * 0.62 - ax * 0.22, 0.22, 0.26, STEEL, 0.0)


def shovel(mw, a, b):
    a, b = Vector(a), Vector(b)
    ax = (b - a).normalized()
    mw.beam(a + ax * 0.95, b, 0.17, 0.17, WP, 0.0)
    mw.beam(a, a + ax * 1.05, 0.9, 0.12, STEEL, 0.0)


def pick_rack(mw, x, y, z, yaw, rng, area="DB_PropRack"):
    """cavalete de madeira com picaretas e pa encostadas (as ferramentas pendem para a frente, +x local)"""
    F = Frame(x, y, z, yaw)
    w = 4.4
    for sy in (-1, 1):
        mw.box((1.5, 0.5, 0.3), F.p(0, sy * w / 2, 0.15), F.r(), WD, 0.0)
        mw.box((0.5, 0.5, 3.5), F.p(-0.2, sy * w / 2, 1.9), F.r(), WD, 0.0)
    for zz in (1.0, 3.1):
        mw.box((0.36, w + 0.5, 0.36), F.p(-0.1, 0, zz), F.r(), WD, 0.0)
    kinds = ("pick", "pick", "shovel", "pick")
    for i, k in enumerate(kinds):
        yy = -1.6 + 1.07 * i + rng.uniform(-0.08, 0.08)
        a = F.p(0.95, yy, 0.05)
        b = F.p(0.2, yy + rng.uniform(-0.12, 0.12), 3.3)
        if k == "pick":
            pickaxe(mw, a, b, F.p(0, 1) - F.p(0, 0))
        else:
            shovel(mw, a, b)
    col_box(area, (1.2, w + 0.4, 3.6), F.p(0.15, 0, 1.8), F.r())


def wood_crate(mw, x, y, z, s, yaw):
    F = Frame(x, y, z, yaw)
    mw.box((s, s, s * 0.9), F.p(0, 0, s * 0.45), F.r(), WP, 0.0)
    for zz in (0.22, s * 0.9 - 0.22):
        mw.box((s + 0.08, s + 0.08, 0.24), F.p(0, 0, zz), F.r(), WD, 0.0)
    return z + s * 0.9


def sack(mw, x, y, z, rng, s=1.0, lying=False):
    """saco de juta estufado (2 troncos de cone) com a boca amarrada; deitado = 2 troncos no eixo horizontal"""
    if lying:
        a = rng.uniform(0, math.tau)
        u = Vector((math.cos(a), math.sin(a), 0.0))
        c = Vector((x, y, z + 0.55 * s))
        K.cyl_axis(mw, 0.5 * s, 0.7 * s, c - u * 0.35 * s, u, SACK, 8, r2=0.62 * s)
        K.cyl_axis(mw, 0.62 * s, 0.7 * s, c + u * 0.35 * s, u, SACK, 8, r2=0.42 * s)
        return
    t = (rng.uniform(-0.06, 0.06), rng.uniform(-0.06, 0.06), rng.uniform(0, 1))
    mw.cyl(0.6 * s, 0.6 * s, (x, y, z + 0.3 * s), t, SACK, 8, r2=0.72 * s, bevel=0.0)
    mw.cyl(0.72 * s, 0.62 * s, (x, y, z + 0.9 * s), t, SACK, 8, r2=0.4 * s, bevel=0.0)
    mw.cyl(0.24 * s, 0.34 * s, (x, y, z + 1.36 * s), (0, 0, 0), SACK, 6, r2=0.32 * s, bevel=0.0)


def pebbles(mw, x, y, z, rng, n=5, rad=2.2):
    """seixos pequenos achatados (<= 0,7 de altura: nao viram obstaculo nem 'minerio')"""
    for i in range(n):
        a = rng.uniform(0, math.tau)
        r = rad * math.sqrt(rng.random())
        s = rng.uniform(0.45, 1.05) * (1.3 if i == 0 else 1.0)
        m = ROCK if rng.random() > 0.3 else ROCKD
        fm_lib.MB.rock(mw, (x + math.cos(a) * r, y + math.sin(a) * r, z + s * 0.16),
                       (s * rng.uniform(1.0, 1.5), s * rng.uniform(0.8, 1.1), min(0.7, s * rng.uniform(0.45, 0.7))),
                       m, 1 if s > 0.8 else 0, (0, 0, rng.uniform(0, 6)), 0.22)


def engine_pallet(mw, x, y, z, yaw):
    """motor de veiculo Capsule sobre palete (bloco escuro, 2 cilindros de aco, tubos)"""
    F = Frame(x, y, z, yaw)
    for sy in (-0.85, 0.0, 0.85):
        mw.box((2.6, 0.45, 0.28), F.p(0, sy, 0.14), F.r(), WD, 0.0)
    mw.box((2.6, 2.1, 0.18), F.p(0, 0, 0.37), F.r(), WP, 0.0)
    mw.box((1.7, 1.5, 1.1), F.p(-0.2, 0, 1.01), F.r(), DARK, 0.0)
    for sy in (-0.45, 0.45):
        K.cyl_axis(mw, 0.42, 1.2, F.p(0.9, sy, 1.05), F.p(1, 0) - F.p(0, 0), STEEL, 10)
    mw.rod(F.p(-0.9, -0.5, 1.6), F.p(-0.9, 0.5, 1.6), 0.14, STEEL, 6)
    mw.rod(F.p(-0.2, 0.0, 1.56), F.p(-0.2, 0.0, 2.1), 0.18, STEEL, 6)


# ------------------------------------------------------------------ KIT DO MERCADO (objeto DB_Prop_Market)
FRUITS = (ORANGE, APPLE, LEAF)


def fruit_mound(mm, c, r, m, rng, z):
    """monte de fruta LISO (nada facetado que leia como pedra/cristal): cupula baixa de torno com sombreamento liso +
    frutas redondas lisas por cima; verde = 2 melancias ovais; laranja ganha uma folhinha"""
    cx, cy = c[0], c[1]
    if m == LEAF:
        prof = [(0.06, z), (r * 0.9, z), (r * 0.75, z + r * 0.16), (0.06, z + r * 0.2)]
        K.lathe(mm, (cx, cy), prof, WP, 8)
        a = rng.uniform(0, math.pi)
        for sg in (-1, 1):
            q = (cx + math.cos(a) * sg * r * 0.36, cy + math.sin(a) * sg * r * 0.36, z + r * 0.5)
            VG.ellipsoid(mm, q, (r * 0.52, r * 0.36, r * 0.34), a + 0.4 * sg, m, sub=1)
        return
    prof = [(0.06, z), (r, z), (r * 0.86, z + r * 0.26), (r * 0.5, z + r * 0.46), (0.06, z + r * 0.52)]
    K.lathe(mm, (cx, cy), prof, m, 10, smooth=[1, 2, 3])
    for k in range(3):
        a = rng.uniform(0, math.tau / 3) + k * math.tau / 3
        q = (cx + math.cos(a) * r * 0.38, cy + math.sin(a) * r * 0.38, z + r * 0.5)
        K.sphere(mm, q, r * 0.3, m, sub=1, smooth=True)
    if m == ORANGE:
        mm.box((0.36, 0.18, 0.1), (cx + 0.1, cy, z + r * 0.62), (0, 0.4, rng.uniform(0, 3)), LEAF, 0.0)


def basket(mm, x, y, z, m, rng, r=0.8):
    """cesto de vime (tronco de cone aberto por cima) com fruta amontoada"""
    mm.cyl(r * 0.75, 0.62, (x, y, z + 0.31), (0, 0, 0), WP, 8, r2=r, bevel=0.0)
    mm.cyl(r + 0.05, 0.14, (x, y, z + 0.6), (0, 0, 0), WD, 8, bevel=0.0, caps=False)
    fruit_mound(mm, (x, y), r * 0.92, m, rng, z + 0.6)


def produce_cart(mm, x, y, z, yaw, rng, area="DB_PropMarket"):
    """carrinho de feira (frente = +x local, o lado da vitrine; alcas atras): 2 rodas grandes nas laterais, leito de
    tabuas, vitrine em 2 degraus (3 caixas de fruta inclinadas na frente, 2 cestos no degrau alto de tras) e toldo
    vermelho em 2 postes com o beiral da frente acima de 6,2"""
    F = Frame(x, y, z, yaw)
    ay = F.p(0, 1) - F.p(0, 0)
    zb = 1.75
    mm.box((2.8, 4.4, 0.3), F.p(0, 0, zb), F.r(), WP, 0.0)
    mm.box((2.8, 4.5, 0.3), F.p(0, 0, zb - 0.32), F.r(), WD, 0.0)
    mm.box((0.25, 4.4, 1.3), F.p(-1.28, 0, zb + 0.8), F.r(), WD, 0.0)            # costas da vitrine
    mm.box((0.22, 4.4, 0.3), F.p(1.3, 0, zb + 0.28), F.r(), WD, 0.0)             # labio da frente
    for sy in (-1, 1):
        mm.box((2.8, 0.22, 0.9), F.p(0, sy * 2.1, zb + 0.6), F.r(), WD, 0.0)
        K.cyl_axis(mm, 1.1, 0.28, F.p(-0.25, sy * 2.42, 1.1), ay, WD, 10)
        K.cyl_axis(mm, 0.34, 0.42, F.p(-0.25, sy * 2.48, 1.1), ay, ORANGE, 6)
        mm.box((0.4, 0.4, zb - 0.45), F.p(1.05, sy * 1.7, (zb - 0.45) / 2), F.r(), WD, 0.0)
        mm.beam(F.p(-1.2, sy * 1.0, zb - 0.1), F.p(-3.0, sy * 1.1, zb - 0.55), 0.24, 0.24, WD, 0.0)
        mm.box((0.26, 0.26, 6.7 - zb), F.p(-1.15, sy * 1.95, zb + (6.7 - zb) / 2), F.r(), WD, 0.0)
    # degrau alto de tras (cestos) e caixas inclinadas da frente (fruta)
    mm.box((1.0, 4.0, 0.7), F.p(-0.65, 0, zb + 0.5), F.r(), WP, 0.0)
    for i, (yy, m) in enumerate(((-1.0, APPLE), (1.0, LEAF))):
        p = F.p(-0.65, yy)
        basket(mm, p.x, p.y, z + zb + 0.85, m, rng, 0.62)
    for i, m in enumerate(FRUITS):
        yy = -1.35 + 1.35 * i
        mm.box((1.3, 1.2, 0.4), F.p(0.55, yy, zb + 0.42), F.r(0, 0.28, 0), WP, 0.0)
        fruit_mound(mm, F.p(0.5, yy), 0.6, m, rng, z + zb + 0.58)
    # toldo inclinado para a frente + sanefa (beiral da frente em ~6,3)
    mm.box((3.6, 5.0, 0.22), F.p(0.1, 0, 6.95), F.r(0, 0.24, 0), CLOTH, 0.0)
    mm.box((0.26, 5.1, 0.5), F.p(1.8, 0, 6.5), F.r(), CLOTH, 0.0)
    col_box(area, (2.8, 4.6, 2.8), F.p(0, 0, 1.4), F.r())


def jar(mm, x, y, z, s, m):
    VG.jar(mm, x, y, z, s, m, rim_m=m, n=8)


# ------------------------------------------------------------------ KIT DO DOJO (objeto DB_Prop_Dojo)
def mat(md, x, y, z, w, d, yaw):
    """tatame de treino laranja com borda azul-marinho (topo 0,12 acima do piso: dentro da tolerancia)"""
    F = Frame(x, y, z, yaw)
    md.box((w, d, 0.1), F.p(0, 0, 0.05), F.r(), ORANGE, 0.0)
    for sx in (-1, 1):
        md.box((0.36, d + 0.36, 0.12), F.p(sx * (w / 2 + 0.0), 0, 0.06), F.r(), NAVY, 0.0)
        md.box((w, 0.36, 0.12), F.p(0, sx * (d / 2), 0.06), F.r(), NAVY, 0.0)


def weight_rack(md, x, y, z, yaw, area="DB_PropDojo"):
    """suporte laqueado com 2 barras de anilhas (as anilhas por fora dos montantes)"""
    F = Frame(x, y, z, yaw)
    md.box((1.4, 4.2, 0.3), F.p(0, 0, 0.15), F.r(), WD, 0.0)
    for sy in (-1, 1):
        md.box((0.45, 0.45, 2.7), F.p(0, sy * 1.75, 1.65), F.r(), LACQ, 0.0)
        for zz in (1.35, 2.45):
            md.box((0.5, 0.3, 0.26), F.p(0.3, sy * 1.75, zz - 0.2), F.r(), DARK, 0.0)
    ay = F.p(0, 1) - F.p(0, 0)
    for zz, ro, ri in ((1.35, 0.72, 0.52), (2.45, 0.58, 0.44)):
        md.rod(F.p(0.3, -2.75, zz), F.p(0.3, 2.75, zz), 0.1, STEEL, 6)
        for sy in (-1, 1):
            K.cyl_axis(md, ro, 0.28, F.p(0.3, sy * 2.15, zz), ay, DARK, 10)
            K.cyl_axis(md, ri, 0.24, F.p(0.3, sy * 2.45, zz), ay, DARK, 10)
    col_box(area, (1.2, 4.0, 3.0), F.p(0.1, 0, 1.5), F.r())


def kettlebell(md, x, y, z, s=1.0):
    K.sphere(md, (x, y, z + 0.5 * s), 0.52 * s, DARK, sub=1, smooth=True)
    md.rod((x - 0.3 * s, y, z + 0.9 * s), (x - 0.25 * s, y, z + 1.3 * s), 0.1 * s, STEEL, 5)
    md.rod((x + 0.3 * s, y, z + 0.9 * s), (x + 0.25 * s, y, z + 1.3 * s), 0.1 * s, STEEL, 5)
    md.rod((x - 0.27 * s, y, z + 1.3 * s), (x + 0.27 * s, y, z + 1.3 * s), 0.1 * s, STEEL, 5)


def plate_stack(md, x, y, z):
    for k, r in enumerate((0.78, 0.72, 0.6, 0.5)):
        md.cyl(r, 0.24, (x, y, z + 0.12 + 0.26 * k), (0, 0, 0.3 * k), DARK, 10, bevel=0.0)


def pullup_bar(md, x, y, z, yaw, area="DB_PropDojo"):
    """barra fixa: 2 postes laqueados em sapata de madeira, barra de aco a 6,6 (passa-se por baixo, entre os postes)"""
    F = Frame(x, y, z, yaw)
    for sy in (-1, 1):
        md.box((1.0, 1.0, 0.36), F.p(0, sy * 2.0, 0.18), F.r(), WD, 0.0)
        md.box((0.46, 0.46, 7.0), F.p(0, sy * 2.0, 3.5 + 0.18), F.r(), LACQ, 0.0)
        md.box((0.56, 0.56, 0.24), F.p(0, sy * 2.0, 7.3), F.r(), DARK, 0.0)
        col_box(area, (0.5, 0.5, 7.1), F.p(0, sy * 2.0, 3.55), F.r())
    md.rod(F.p(0, -2.2, 6.6), F.p(0, 2.2, 6.6), 0.12, STEEL, 6)


def punching_bag(md, x, y, z, yaw, area="DB_PropDojo"):
    """saco de pancada marinho (cintas laranja) pendurado de um poste laqueado com braco"""
    F = Frame(x, y, z, yaw)
    md.box((1.3, 1.3, 0.4), F.p(0, 0, 0.2), F.r(), WD, 0.0)
    md.box((0.5, 0.5, 7.2), F.p(0, 0, 3.8), F.r(), LACQ, 0.0)
    md.box((2.6, 0.4, 0.4), F.p(1.1, 0, 7.2), F.r(), LACQ, 0.0)
    md.beam(F.p(0.2, 0, 6.0), F.p(1.2, 0, 7.05), 0.3, 0.3, LACQ, 0.0)
    md.rod(F.p(2.1, 0, 7.0), F.p(2.1, 0, 5.8), 0.07, STEEL, 4)
    md.cyl(0.72, 2.8, F.p(2.1, 0, 4.4), F.r(), NAVY, 10, bevel=0.0)
    for zz in (3.2, 5.6):
        md.cyl(0.76, 0.24, F.p(2.1, 0, zz), F.r(), ORANGE, 10, bevel=0.0, caps=False)
    col_box(area, (0.6, 0.6, 7.4), F.p(0, 0, 3.7), F.r())
    col_box(area, (1.3, 1.3, 2.8), F.p(2.1, 0, 4.4), F.r())


def martial_lantern(md, x, y, z, yaw, area="DB_PropDojo", col=True):
    """lanterna marcial de poste (a familia do dojo/mercado): sapata de madeira, poste laqueado, caixa de papel ambar
    com montantes escuros e chapeu laranja em piramide. Devolve o centro da luz."""
    F = Frame(x, y, z, yaw)
    md.box((1.3, 1.3, 0.5), F.p(0, 0, 0.25), F.r(), WD, 0.0)
    md.box((0.55, 0.55, 4.4), F.p(0, 0, 0.5 + 2.2), F.r(), LACQ, 0.0)
    md.box((1.35, 1.35, 0.3), F.p(0, 0, 5.05), F.r(), WD, 0.0)
    md.box((1.0, 1.0, 1.25), F.p(0, 0, 5.2 + 0.62), F.r(), LAMP, 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            md.box((0.22, 0.22, 1.35), F.p(sx * 0.55, sy * 0.55, 5.2 + 0.62), F.r(), WD, 0.0)
    md.cyl(1.2, 0.7, F.p(0, 0, 6.45 + 0.35), F.r(0, 0, math.pi / 4), ORANGE, 4, r2=0.16, bevel=0.0)
    if col:
        col_box(area, (0.6, 0.6, 7.1), F.p(0, 0, 3.55), F.r())
    return F.p(0, 0, 5.85)


def dojo_bench(md, x, y, z, yaw):
    """banco baixo de tabua com toalha laranja dobrada e jarra d'agua"""
    F = Frame(x, y, z, yaw)
    for sy in (-1, 1):
        md.box((0.9, 0.4, 0.95), F.p(0, sy * 1.5, 0.475), F.r(), WD, 0.0)
    md.box((1.1, 3.8, 0.28), F.p(0, 0, 1.09), F.r(), WD, 0.0)
    md.box((0.8, 0.9, 0.24), F.p(0.05, -0.9, 1.35), F.r(0, 0, 0.1), ORANGE, 0.0)
    md.cyl(0.36, 0.8, F.p(0.0, 1.0, 1.63), F.r(), NAVY, 8, r2=0.26, bevel=0.0)


# ------------------------------------------------------------------ validador (cena montada)
SHRUBS = "DB_Veg_Shrubs"


def _mesh_arrays(ob):
    me = ob.data
    nv = len(me.vertices)
    co = np.empty(nv * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    M = np.array(ob.matrix_world, dtype=np.float64)
    co = co @ M[:3, :3].T + M[:3, 3]
    ed = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ed)
    return co, ed.reshape(-1, 2)


def _labels(nv, ed):
    """componentes conexas (partes soltas) por propagacao de rotulo + salto de ponteiro"""
    lab = np.arange(nv, dtype=np.int64)
    if not len(ed):
        return lab
    a, b = ed[:, 0], ed[:, 1]
    for _ in range(400):
        m = np.minimum(lab[a], lab[b])
        old = lab.copy()
        np.minimum.at(lab, a, m)
        np.minimum.at(lab, b, m)
        lab = lab[lab]
        if np.array_equal(lab, old):
            break
    return lab


def shrub_islands():
    """bbox de cada parte solta das moitas/tufos/flores da vegetacao (DB_Veg_Shrubs, montada ANTES dos props):
    (lo[k,3], hi[k,3], rotulo por vertice, rotulo por face)"""
    ob = bpy.data.objects.get(SHRUBS)
    if ob is None or ob.type != "MESH" or not len(ob.data.vertices):
        return None, None, None, None
    co, ed = _mesh_arrays(ob)
    lab = _labels(len(co), ed)
    uniq, inv = np.unique(lab, return_inverse=True)
    k = len(uniq)
    lo = np.full((k, 3), 1e9)
    hi = np.full((k, 3), -1e9)
    for j in range(3):
        np.minimum.at(lo[:, j], inv, co[:, j])
        np.maximum.at(hi[:, j], inv, co[:, j])
    pv = np.array([p.vertices[0] for p in ob.data.polygons], dtype=np.int64)
    return lo, hi, inv, inv[pv] if len(pv) else pv


def glow_index():
    """KD-tree dos centros de face com Lantern_Glow das OUTRAS zonas (para nao dobrar lanterna onde ja existe)"""
    from mathutils.kdtree import KDTree
    pts, who = [], []
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name.startswith(("COL_", "DB_Prop_")):
            continue
        idx = {i for i, m in enumerate(o.data.materials) if m and m.name.startswith("Lantern_Glow")}
        if not idx:
            continue
        mw = o.matrix_world
        for p in o.data.polygons:
            if p.material_index in idx:
                pts.append(mw @ p.center)
                who.append(o.name)
    if not pts:
        return None
    kd = KDTree(len(pts))
    for i, p in enumerate(pts):
        kd.insert(p, i)
    kd.balance()
    return kd, who


class Scene:
    """consulta a cena ja montada (outras zonas + vegetacao): colisao COL_* e visual (malhas) por raio vertical"""

    def __init__(self):
        bpy.context.view_layer.update()          # matrix_world das caixas COL_ recem-criadas
        verts, polys = [], []
        for o in bpy.data.objects:
            if o.type != "MESH" or not o.name.startswith("COL_") or o.name.startswith("COL_DB_Prop"):
                continue
            mw = o.matrix_world
            base = len(verts)
            verts += [mw @ v.co for v in o.data.vertices]
            polys += [[base + i for i in p.vertices] for p in o.data.polygons]
        self.col = BVHTree.FromPolygons(verts, polys)
        self.vis = []
        for o in bpy.data.objects:
            if o.type != "MESH" or o.name.startswith(("COL_", "DB_Prop_", "DB_Sky_", "SCALE_")) or o.hide_render:
                continue
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
            hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
            self.vis.append([o, lo, hi, None])
        self.markers = [(o.name, o.location.copy()) for o in bpy.data.objects if o.type == "EMPTY" and o.name.startswith(
            ("NPC_", "PLAYER_INTERACT_", "SUMMON_", "GATE_", "ISLAND_", "WORLD_", "PATH_ENTRY_CENTER"))]
        self.lights = [(o.name, o.location.copy()) for o in bpy.data.objects if o.type == "LIGHT"]
        self.shrub_lo, self.shrub_hi, self.shrub_lab, self.shrub_poly_lab = shrub_islands()
        self.glow = glow_index()

    def shrub_hit(self, x, y, r, z0, z1, pad=0.5):
        """alguma parte solta das moitas (DB_Veg_Shrubs) com bbox a menos de r+pad do disco (x, y, r), na faixa z?"""
        lo, hi = self.shrub_lo, self.shrub_hi
        if lo is None or not len(lo):
            return False
        dx = np.maximum(np.maximum(lo[:, 0] - x, x - hi[:, 0]), 0.0)
        dy = np.maximum(np.maximum(lo[:, 1] - y, y - hi[:, 1]), 0.0)
        m = (dx * dx + dy * dy < (r + pad) ** 2) & (hi[:, 2] > z0 - 0.3) & (lo[:, 2] < z1)
        return bool(m.any())

    def shrub_count(self, x, y, r, z0, z1, pad=0.5):
        lo, hi = self.shrub_lo, self.shrub_hi
        if lo is None or not len(lo):
            return 0
        dx = np.maximum(np.maximum(lo[:, 0] - x, x - hi[:, 0]), 0.0)
        dy = np.maximum(np.maximum(lo[:, 1] - y, y - hi[:, 1]), 0.0)
        m = (dx * dx + dy * dy < (r + pad) ** 2) & (hi[:, 2] > z0 - 0.3) & (lo[:, 2] < z1)
        return int(m.sum())

    def glow_near(self, x, y, z, rad=5.0, dz=6.0):
        """ja existe lanterna (Lantern_Glow de outra zona) perto?"""
        if self.glow is None:
            return None
        for co, idx, d in self.glow[0].find_range(Vector((x, y, z)), rad + dz):
            if math.hypot(co.x - x, co.y - y) < rad and abs(co.z - z) < dz:
                return self.glow[1][idx]
        return None

    def _bvh(self, rec):
        if rec[3] is None:
            o = rec[0]
            mw = o.matrix_world
            me = o.data
            me.calc_loop_triangles()          # n-gonos concavos do chao: triangulacao correta (nada de leque)
            rec[3] = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [tuple(t.vertices) for t in me.loop_triangles])
        return rec[3]

    def col_top(self, x, y, z0, dist):
        hit = self.col.ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)), dist)
        return hit[0].z if hit[0] is not None else None

    def vis_top(self, x, y, z0, dist, who=None):
        best = None
        for rec in self.vis:
            o, lo, hi, _ = rec
            if not (lo.x - 0.01 <= x <= hi.x + 0.01 and lo.y - 0.01 <= y <= hi.y + 0.01):
                continue
            if hi.z < z0 - dist or lo.z > z0:
                continue
            hit = self._bvh(rec).ray_cast(Vector((x, y, z0)), Vector((0, 0, -1)), dist)
            if hit[0] is not None and (best is None or hit[0].z > best):
                best = hit[0].z
                if who is not None:
                    who[0] = o.name
        return best


def _stair_rects():
    """retangulos (quadro, comprimento, largura) das escadas da planta, com folga nas pontas"""
    out = []
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        out.append((Frame(base[0], base[1], 0.0, ang), -tread - 3.0, tread * n + 3.5, w / 2 + 2.2, nm, tread * n, w))
    return out


def _routes():
    import db_qa
    pls = []
    for nm, (pts, z0) in list(db_qa.routes().items()) + list(db_qa.open_routes().items()):
        pls.append((nm, [tuple(p[:2]) for p in pts]))
    try:
        mr, _ = db_qa.module_routes()
        for nm, (pts, z0) in mr.items():
            pls.append((nm, [tuple(p[:2]) for p in pts]))
    except Exception as ex:
        print("PROPS aviso: rotas dos modulos indisponiveis (%s)" % ex)
    return pls


# zonas proibidas extras (x0, y0, x1, y1, motivo): vaos de porta, frente de escada, praca de entrada, mercado
NO_GO = [
    (8.0, 104.0, 24.5, 128.0, "portao da oficina"),
    (-98.5, 109.5, -73.5, 140.0, "mercado (pavilhao + barracas + corredor)"),
    (95.0, -21.0, 109.5, -7.0, "degraus do dojo"),
    (-23.5, -113.0, 23.5, -73.0, "praca de entrada"),
    (-90.5, -10.0, -74.5, 6.0, "zona livre 14x14 na frente da escada do summon"),
    (-16.0, 104.0, 16.0, 136.0, "escadaria do Capsule"),
]


MBS = []                 # os 4 kits (contagem de tris por grupo para o relatorio)
COST = []                # (tris, grupo)


def _tri_count():
    n = 0
    for mb in MBS:
        n += sum(len(f.verts) - 2 for f in mb.bm.faces)
    return n


class Placer:
    def __init__(self):
        self.sc = Scene()
        self.stairs = _stair_rects()
        self.routes = _routes()
        try:
            import db_terrain
            self.streets = [(list(p), w) for p, w in getattr(db_terrain, "HUB_STREETS", [])]
        except Exception:
            self.streets = []
        self.placed = []          # (x, y, r)
        self.n_ok = 0
        self.n_skip = 0

    def check(self, x, y, r, h, z_floor, route_clear=2.6, lamp=False, gutter=GUTTER, shrubs=True):
        """None = cabe. lamp=True: poste de caminho/escada/rua (pode ficar COLADO na borda da trilha, da ponte e da
        escada e na calcada da rua; continua fora da faixa de andar, das rotas e das zonas proibidas).
        shrubs: recusa quando uma parte solta das moitas da vegetacao (ja montada) fica a menos de r+0,5 do disco."""
        # nivel: tudo no mesmo piso
        pts = [(x, y)] + [(x + r * math.cos(t), y + r * math.sin(t)) for t in [k * math.pi / 8 for k in range(16)]]
        pts += [(x + r * 0.72 * math.cos(t), y + r * 0.72 * math.sin(t)) for t in [k * math.pi / 4 + 0.2 for k in range(8)]]
        pts += [(x + r * 0.4 * math.cos(t), y + r * 0.4 * math.sin(t)) for t in [k * math.pi / 2 + 0.4 for k in range(4)]]
        for px, py in pts:
            if abs(L.zone_of(px, py) - z_floor) > 0.01:
                return "nivel"
            if not L.point_in_poly(px, py, L.ISLAND_RIM):
                return "fora da ilha"
        rr = math.hypot(x, y)
        ang = math.degrees(math.atan2(y, x))
        if rr - r < L.prom_r(ang) + gutter:
            return "arena/promenade/sarjeta"
        if math.hypot(x - L.SUMMON_C[0], y - L.SUMMON_C[1]) < 27.0 + r:
            return "disco do summon"
        for x0, y0, x1, y1, why in NO_GO:
            if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
                return why
        for F, u0, u1, hw, nm, run, w in self.stairs:
            dx, dy = x - F.o.x, y - F.o.y
            u = dx * math.cos(F.a) + dy * math.sin(F.a)
            v = -dx * math.sin(F.a) + dy * math.cos(F.a)
            if lamp:
                if -0.6 - r < u < run + 0.6 + r and abs(v) < w / 2 + r + 0.2:
                    return "escada " + nm
            elif u0 - r < u < u1 + r and abs(v) < hw + r:
                return "escada " + nm
        # pontes (chegada, saida, satelites)
        if y < L.BRIDGE_Y1 + 20.0 and abs(x) < L.ENTRY_STAIR_W / 2 + 3.0 + r:
            return "ponte/escadaria de chegada"
        for k, (a0, a1) in L.SAT_BRIDGES.items():
            d, t = L.seg_dist(x, y, a0[0], a0[1], a1[0], a1[1])
            if d < L.SAT_BRIDGE_W / 2 + (0.2 if lamp else 2.0) + r:
                return "ponte do satelite"
        for pts_, w in L.GROUND_PATHS:
            if L.polyline_dist(x, y, pts_) < w / 2 + r + (0.05 if lamp else 0.3):
                return "trilha calcada"
        if not lamp:
            for pts_, hw in self.streets:
                if L.polyline_dist(x, y, pts_) < hw + r + 0.3:
                    return "rua da vila"
        for nm, pl in self.routes:
            if len(pl) > 1 and L.polyline_dist(x, y, pl) < r + route_clear:
                return "rota " + nm
        for nm, p in self.sc.markers:
            if math.hypot(x - p.x, y - p.y) < r + 4.5 and abs(p.z - z_floor) < 8.0:
                return "marcador " + nm
        for px, py, pr in self.placed:
            if math.hypot(x - px, y - py) < r + pr + 0.6:
                return "outro prop"
        if shrubs and self.sc.shrub_hit(x, y, r, z_floor, z_floor + h):
            return "moita da vegetacao"
        # raios: colisao e visual
        for px, py in pts:
            zc = self.sc.col_top(px, py, z_floor + h + 0.3, h + 3.0)
            if zc is None:
                return "sem piso de colisao"
            if zc > z_floor + 0.35:
                return "colisao existente (%.1f)" % (zc - z_floor)
            if zc < z_floor - 0.35:
                return "buraco/agua"
            who = [""]
            zv = self.sc.vis_top(px, py, z_floor + h + 0.3, h + 3.0, who)
            if zv is None or zv < z_floor - 0.4:
                return "sem piso visual em (%.1f,%.1f): %s" % (px, py, "nada" if zv is None else "%s %.2f" % (
                    who[0], zv - z_floor))
            if zv > z_floor + 0.55:
                return "visual de %s (%.1f)" % (who[0], zv - z_floor)
        return None

    def place(self, name, cands, r, h, fn, z_floor=None, route_clear=2.6, lamp=False, gutter=GUTTER,
              shrub_fallback=True, quiet=False):
        """tenta as posicoes (x, y, yaw) em ordem; monta a primeira livre. 1a passada: longe das moitas da vegetacao;
        se nenhuma serve SO por causa de moita e shrub_fallback, 2a passada sem essa regra (as partes de moita que o
        prop atravessar de verdade saem no fim, em clear_shrub_overlaps)"""
        why, why2 = [], []
        passes = (True, False) if shrub_fallback else (True,)
        for shrubs in passes:
            only_shrub = False
            best = None
            for i, (x, y, yaw) in enumerate(cands):
                z = L.zone_of(x, y) if z_floor is None else z_floor
                res = self.check(x, y, r, h, z, route_clear, lamp, gutter, shrubs)
                if res is None:
                    if shrubs:
                        best = (0, i, x, y, z, yaw)
                        break
                    # 2a passada: entre as que cabem, a que menos pisa em moita (empate: a mais perto da planta)
                    n_sh = self.sc.shrub_count(x, y, r, z, z + h)
                    if best is None or n_sh < best[0]:
                        best = (n_sh, i, x, y, z, yaw)
                    continue
                only_shrub |= res == "moita da vegetacao"
                (why if shrubs else why2).append("(%.0f,%.0f): %s" % (x, y, res))
            if best is not None:
                n_sh, i, x, y, z, yaw = best
                t0 = _tri_count()
                fn(x, y, z, yaw)
                COST.append((_tri_count() - t0, name))
                self.placed.append((x, y, r))
                self.n_ok += 1
                REPORT.append("ok %s (%.1f, %.1f)%s" % (name, x, y, "" if shrubs else " [sobre %d partes de moita]" % n_sh))
                return (x, y, z, yaw)
            if not only_shrub:
                break
        self.n_skip += 1
        REPORT.append("PULADO %s -> %s" % (name, "; ".join(why[:6])))
        if not quiet:
            print("PROPS pulado %s -> %s%s" % (name, "; ".join(why[:8]),
                                               (" || sem a regra da moita: " + "; ".join(why2[:10])) if why2 else ""))
        return None


# ------------------------------------------------------------------ plano (posicoes da planta + alternativas)
def around(x, y, yaw, d=3.0):
    """posicao + 4 alternativas deslocadas (mesmo rumo)"""
    return [(x, y, yaw), (x + d, y, yaw), (x - d, y, yaw), (x, y + d, yaw), (x, y - d, yaw)]


def near(x, y, yaw_fn, rmax=7.0, step=1.75):
    """a posicao da planta e depois aneis em volta dela (ate rmax), do mais perto para o mais longe; yaw_fn(x, y)"""
    out = [(x, y, yaw_fn(x, y))]
    k = 1
    while k * step <= rmax + 1e-6:
        rr = k * step
        n = max(6, int(round(2 * math.pi * rr / step)))
        for i in range(n):
            t = 2 * math.pi * i / n + 0.3 * k
            px, py = x + rr * math.cos(t), y + rr * math.sin(t)
            out.append((px, py, yaw_fn(px, py)))
        k += 1
    return out


def prom_pt(a_deg, off):
    r = L.prom_r(a_deg) + off
    a = math.radians(a_deg)
    return r * math.cos(a), r * math.sin(a)


def prom_cands(a_deg, off, face_in=True, da=(0.0, 3.0, -3.0, 6.0, -6.0)):
    """posicoes na borda de fora do promenade (angulo, afastamento), viradas para a arena"""
    out = []
    for d in da:
        for o in (off, off + 2.5):
            x, y = prom_pt(a_deg + d, o)
            yaw = math.atan2(-y, -x) if face_in else math.atan2(y, x)
            out.append((x, y, yaw))
    return out


# ------------------------------------------------------------------ lanternas de caminho / escada / rua (emissivo)
LANE_H = 3.6            # fuste do poste de caminho: lampiao entre 4,8 e 6,0 acima do piso (altura da cabeca)
LANE_R = 1.0            # raio do disco livre do poste (soco 0,85)
LANE_TOP = 7.0          # altura total para os raios do validador
LANES = []              # (tipo, x, y, z) dos postes de caminho montados (relatorio)
CUE_GLOW = CYAN         # a linha de postes da rua da vila que leva a saida: topo ciano (o resto e ambar)


def pl_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def pl_at(pts, d):
    """ponto e tangente unitaria a d (comprimento de arco) ao longo da polilinha (grampeado nas pontas)"""
    acc = 0.0
    segs = list(zip(pts, pts[1:]))
    for i, (a, b) in enumerate(segs):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if d <= acc + ln or i == len(segs) - 1:
            t = max(0.0, min(1.0, (d - acc) / ln))
            ux, uy = (b[0] - a[0]) / ln, (b[1] - a[1]) / ln
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), (ux, uy)
        acc += ln


def side_cands(pts, d, side, lats, shifts=(0.0, 1.5, -1.5, 3.0, -3.0, 4.5, -4.5)):
    """posicoes ao lado da polilinha (side +1 = esquerda de quem anda no sentido dos pontos)"""
    out = []
    for sh in shifts:
        (px, py), (ux, uy) = pl_at(pts, d + sh)
        for lat in lats:
            out.append((px - uy * side * lat, py + ux * side * lat, math.atan2(uy, ux)))
    return out


def lane_lamp(mc, kind, glow=LAMP):
    def f(x, y, z, yaw):
        cap_lamp(mc, x, y, z, LANE_H, col=True, lite=True, glow=glow)   # integracao: poste com colisao (teto do vestir 130)
        LANES.append((kind, x, y, z))
    return f


def mlamp(md, kind):
    def f(x, y, z, yaw):
        martial_lantern(md, x, y, z, yaw, col=True)
        LANES.append((kind, x, y, z))
    return f


def place_pair(P, name, ca, cb, fa, fb, r, h, route_clear=2.0, gutter=GUTTER):
    """par simetrico (as 2 pontas da escada/ponte): tenta as mesmas alternativas dos 2 lados juntas; se nenhuma serve
    aos dois, cada lado por conta propria"""
    for (xa, ya, wa), (xb, yb, wb) in zip(ca, cb):
        za, zb = L.zone_of(xa, ya), L.zone_of(xb, yb)
        if P.check(xa, ya, r, h, za, route_clear, True, gutter) is None and \
                P.check(xb, yb, r, h, zb, route_clear, True, gutter) is None:
            fa(xa, ya, za, wa)
            fb(xb, yb, zb, wb)
            P.placed += [(xa, ya, r), (xb, yb, r)]
            P.n_ok += 2
            REPORT.append("ok %s par (%.1f, %.1f) (%.1f, %.1f)" % (name, xa, ya, xb, yb))
            return 2
    n = 0
    for tag, c, f in (("A", ca, fa), ("B", cb, fb)):
        n += P.place(name + "_" + tag, c, r, h, f, route_clear=route_clear, lamp=True, gutter=gutter,
                     shrub_fallback=False) is not None
    return n


def lanterns(P, mc, md):
    LANES.clear()

    def lit_by(pts, z):
        for x, y in pts:
            w = P.sc.glow_near(x, y, z + 5.0, 5.0, 6.0)
            if w:
                return w
        return None

    # 1) trilhas calcadas radiais: 1 poste a cada ~12, alternando os lados (a de 12 de largura do summon e so a
    #    aproximacao da escada, coberta pelo par do pe da escada)
    for i, (pts, w) in enumerate(L.GROUND_PATHS):
        if w > 8.0:
            continue
        ln = pl_len(pts)
        d0 = 0.0
        while d0 < ln:
            (px, py), _ = pl_at(pts, d0)
            a = math.degrees(math.atan2(py, px))
            if math.hypot(px, py) - L.prom_r(a) >= GUTTER + 2.5:
                break
            d0 += 0.5
        end = ln - (7.0 if i in (0, 1) else 3.0)          # a ponta das trilhas 0 e 1 e a cabeceira da ponte
        k, d = 0, d0 + 1.5
        while d <= end:
            side = 1 if k % 2 == 0 else -1
            lats = (w / 2 + 1.1, w / 2 + 1.7)
            cands = side_cands(pts, d, side, lats) + side_cands(pts, d, -side, lats, (0.0, 2.0, -2.0))
            (px, py), _ = pl_at(pts, d)
            who = lit_by([(px, py)], G)
            if who:
                REPORT.append("lanterna ja existe na trilha %d d=%.0f (%s)" % (i, d, who))
            else:
                P.place("lanterna_trilha%d_%02d" % (i, k), cands, LANE_R, LANE_TOP, lane_lamp(mc, "trilha"),
                        route_clear=2.0, lamp=True, shrub_fallback=False)
            k += 1
            d += 12.0

    # 2) pares no pe e no topo das escadas da vila (3), do summon e da saida
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if not (nm.startswith("Hub") or nm in ("Summon", "Exit")):
            continue
        F = Frame(base[0], base[1], 0.0, ang)
        run = tread * n
        z0, z1 = base[2], base[2] + rise * n
        # pe: antes do 1o degrau ou AO LADO dos 2-3 primeiros (quando o pe encosta no promenade); topo: logo depois
        # do ultimo degrau, ja no piso de cima
        for end, us, zz in (("pe", (-1.0, -1.7, 0.5, 1.3, 2.1, -2.5), z0),
                            ("topo", tuple(run + 1.3 + d_ for d_ in (0.0, 0.6, 1.2, 1.9, 2.7, 3.5)), z1)):
            nom = [F.p(us[0], s_ * (w / 2 + 1.25)) for s_ in (1, -1)]
            who = lit_by([(p.x, p.y) for p in nom], zz)
            if who:
                REPORT.append("escada %s %s ja tem lanterna (%s)" % (nm, end, who))
                continue
            ca, cb = [], []
            for u_ in us:
                for dv in (0.0, 0.5, 1.1):
                    for s_, lst in ((1, ca), (-1, cb)):
                        q = F.p(u_, s_ * (w / 2 + 1.25 + dv))
                        lst.append((q.x, q.y, ang))
            glow = CUE_GLOW if nm == "Hub2" and end == "topo" else LAMP
            # o pe das escadas da vila e da saida ENCOSTA no promenade (as laterais sao o muro do terraco): ali o
            # par fica na margem de fora do promenade, colado no muro (longe do meio, onde se anda)
            gut = -2.2 if end == "pe" else 0.3
            if nm == "Exit":             # a escada da saida ja tem lanternas marciais nas bochechas: mesma familia
                fa = fb = mlamp(md, "escada")
            else:
                fa = fb = lane_lamp(mc, "escada", glow)
            place_pair(P, "lanterna_escada_%s_%s" % (nm, end), ca, cb, fa, fb, LANE_R, LANE_TOP, route_clear=2.0,
                       gutter=gut)

    # 3) cabeceiras das pontes dos satelites (no chao, antes do tabuleiro)
    for kind, (a0, a1) in L.SAT_BRIDGES.items():
        ang = math.atan2(a1[1] - a0[1], a1[0] - a0[0])
        F = Frame(a0[0], a0[1], 0.0, ang)
        nom = [F.p(-1.0, s_ * (L.SAT_BRIDGE_W / 2 + 1.4)) for s_ in (1, -1)]
        who = lit_by([(p.x, p.y) for p in nom], G)
        if who:
            REPORT.append("ponte %s ja tem lanterna (%s)" % (kind, who))
            continue
        ca, cb = [], []
        for du in (0.0, 0.8, 1.6, 2.6, 3.6):
            for dv in (0.0, 0.6, 1.3):
                for s_, lst in ((1, ca), (-1, cb)):
                    q = F.p(-1.0 - du, s_ * (L.SAT_BRIDGE_W / 2 + 1.4 + dv))
                    lst.append((q.x, q.y, ang))
        place_pair(P, "lanterna_ponte_%s" % kind, ca, cb, lane_lamp(mc, "ponte"), lane_lamp(mc, "ponte"), LANE_R,
                   LANE_TOP, route_clear=2.0)

    # 4) trilha da saida: lanterna marcial a cada ~16 no lado de DENTRO (o da vila, a esquerda de quem sai) ate o
    #    comeco da transicao Shadow Garden (SG_TRANSITION_D antes da ponte); depois dela so as roxas do db_exit
    pts = L.EXIT_PATH
    ln = pl_len(pts)
    stop = ln - L.SG_TRANSITION_D - 2.0

    ml = mlamp(md, "saida")
    k, d = 0, 7.0
    while d <= stop:
        lats = (L.EXIT_PATH_HW - 1.9, L.EXIT_PATH_HW - 2.6, L.EXIT_PATH_HW - 3.3)
        cands = [c for c in side_cands(pts, d, 1, lats, (0.0, 2.0, -2.0, 4.0, -4.0, 6.0, -6.0, 8.0))]
        P.place("lanterna_saida_%02d" % k, cands, 1.0, 7.3, ml, z_floor=L.EXIT_Z, route_clear=2.0, lamp=True,
                shrub_fallback=False)
        k += 1
        d += 16.0

    # 5) rua da vila -> saida (quem sai do Capsule nao via o caminho): postes de topo CIANO no lado sul da rua
    #    principal (y ~77,5, junto do parapeito da frente do terraco, fora do corredor livre), a cada ~12 de x 16 ate
    #    a escada lateral leste (o par ciano do topo dela continua a linha), + seta de piso na juncao rua/ligacao da
    #    saida e o mastro-farol ciano do lado da vila (aparece por cima da oficina para quem desce do Capsule)
    try:
        import db_terrain
        st = list(db_terrain.HUB_STREETS[0][0])
        hw = db_terrain.HUB_STREETS[0][1]
    except Exception:
        st, hw = [(0.0, 81.2), (52.0, 81.5), (78.0, 82.5), (96.0, 87.0)], 4.3
    st = [p for p in st if p[0] >= -0.5]
    for k, s0 in enumerate((16.0, 28.0, 40.0, 52.0, 63.0)):
        cands = side_cands(st, s0, -1, (hw - 0.5, hw - 0.9, hw - 0.1, hw - 1.4), (0.0, 1.5, -1.5, 3.0, -3.0))
        P.place("poste_rua_saida_%d" % k, cands, LANE_R, LANE_TOP, lane_lamp(mc, "rua", CUE_GLOW), z_floor=H,
                route_clear=2.0, lamp=True, shrub_fallback=False)

    link = L.HUB_EXIT_LINK
    yaw = math.atan2(link[1][1] - link[0][1], link[1][0] - link[0][0])
    ok = False
    dbg = []
    # a seta fica sobre UMA familia de lajes (as da rua tem topo +0,14, as da ligacao +0,10, a base 0): amostra os
    # bracos de verdade e aceita onde >= 80% dos pontos estao na laje mais alta e o topo da seta fica <= H + 0,15
    for sh in (0.0, 1.5, 3.0, 4.5, 5.5, 6.5, 7.5, -1.5):
        for lat in (0.0, 1.0, -1.0):
            cx = 96.0 + math.cos(yaw) * sh - math.sin(yaw) * lat
            cy = 87.0 + math.sin(yaw) * sh + math.cos(yaw) * lat
            F = Frame(cx, cy, 0.0, yaw)
            zs = []
            for u0 in (-1.15, 1.15):
                for sg in (-1, 1):
                    for t in (0.0, 0.5, 1.0):
                        q = F.p(u0 - 1.97 * t, sg * 1.95 * t)
                        zs.append(P.sc.vis_top(q.x, q.y, H + 3.0, 5.0))
            if any(z is None for z in zs):
                dbg.append("sh=%.1f lat=%.0f sem piso" % (sh, lat))
                continue
            m = max(zs)
            good = sum(1 for z in zs if abs(z - m) <= 0.035)
            dbg.append("sh=%.1f lat=%.0f max=%+.2f min=%+.2f bons=%d/%d" % (sh, lat, m - H, min(zs) - H, good, len(zs)))
            if good < 0.8 * len(zs) or m > H + 0.115 or min(zs) < m - 0.3:
                continue
            top = m + 0.035
            chevron(mc, cx, cy, top, yaw)
            REPORT.append("ok seta_piso_saida (%.1f, %.1f) topo=H%+.2f" % (cx, cy, top - H))
            ok = True
            break
        if ok:
            break
    if not ok:
        print("PROPS pulado seta_piso_saida (piso irregular na juncao rua/ligacao): %s" % " | ".join(dbg))

    P.place("farol_saida", near(106.0, 98.0, lambda x, y: 0.0, 7.0), 1.9, 51.0,
            lambda x, y, z, yaw: beacon_mast(mc, x, y, z), route_clear=2.0, shrub_fallback=True)

    kinds = {}
    for kd, x, y, z in LANES:
        kinds[kd] = kinds.get(kd, 0) + 1
    print("PROPS lanternas de caminho (so brilho, sem luz): %d %s" % (len(LANES), kinds))


def clear_shrub_overlaps(objs):
    """rede de seguranca: as partes soltas de moita/tufo/flor (DB_Veg_Shrubs) que um prop ATRAVESSA de verdade
    (interseccao de triangulos, BVH) saem da malha das moitas; o resto da vegetacao nao e tocado"""
    import bmesh
    ob = bpy.data.objects.get(SHRUBS)
    if ob is None or not len(ob.data.polygons):
        return 0, 0
    bpy.context.view_layer.update()
    co, ed = _mesh_arrays(ob)
    polys = [tuple(p.vertices) for p in ob.data.polygons]
    sh = BVHTree.FromPolygons([Vector(v) for v in co], polys)
    lab = _labels(len(co), ed)
    kill = set()
    for po in objs:
        if po is None or not len(po.data.polygons):
            continue
        mw = po.matrix_world
        bvh = BVHTree.FromPolygons([mw @ v.co for v in po.data.vertices], [tuple(p.vertices) for p in po.data.polygons])
        for ip, js in bvh.overlap(sh):
            kill.add(int(lab[polys[js][0]]))
    if not kill:
        return 0, 0
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bm.verts.ensure_lookup_table()
    dead = [bm.verts[i] for i in range(len(bm.verts)) if int(lab[i]) in kill]
    nt = sum(len(f.verts) - 2 for f in {f for v in dead for f in v.link_faces})
    bmesh.ops.delete(bm, geom=dead, context="VERTS")
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return len(kill), nt


def veg_overlaps(objs):
    """relatorio: pares de triangulos prop x vegetacao que se cruzam, por objeto da vegetacao (canteiros fora: sao piso)"""
    out = {}
    for vn in ("DB_Veg_Shrubs", "DB_Veg_Palms", "DB_Veg_Rocks", "DB_Veg_Planters"):
        vo = bpy.data.objects.get(vn)
        if vo is None or not len(vo.data.polygons):
            continue
        mw = vo.matrix_world
        vb = BVHTree.FromPolygons([mw @ v.co for v in vo.data.vertices], [tuple(p.vertices) for p in vo.data.polygons])
        n = 0
        for po in objs:
            if po is None:
                continue
            pm = po.matrix_world
            pb = BVHTree.FromPolygons([pm @ v.co for v in po.data.vertices], [tuple(p.vertices) for p in po.data.polygons])
            n += len(pb.overlap(vb))
        out[vn] = n
    return out


def build():
    rng = random.Random(9090)
    LAMP_SPOTS.clear()
    REPORT.clear()
    P = Placer()
    mc = K.CMB("DB_Prop_Capsule", C, rng=random.Random(9101), detail="hero")
    mw = K.CMB("DB_Prop_Work", C, rng=random.Random(9102), detail="near")
    mm = K.CMB("DB_Prop_Market", C, rng=random.Random(9103), detail="near")
    md = K.CMB("DB_Prop_Dojo", C, rng=random.Random(9104), detail="near")
    MBS[:] = [mc, mw, mm, md]
    COST.clear()

    # ---------------- estacoes de mineracao na borda de fora do promenade (nada na arena)
    def st_entry(x, y, z, yaw):          # cavalete de picaretas + tremonha vazia (ao lado da praca de entrada)
        F = Frame(x, y, z, yaw)
        p = F.p(0.0, -2.9)
        pick_rack(mw, p.x, p.y, z, yaw, rng)
        q = F.p(-0.6, 2.6)
        ore_bin(mw, q.x, q.y, z, yaw + math.pi / 2)
    P.place("estacao_mineracao_S", prom_cands(248.0, 8.4) + prom_cands(248.0, 12.5, da=(0.0, 4.0, -4.0, 8.0, -8.0)) +
            prom_cands(240.0, 8.4, da=(0.0, -3.0, -6.0, -9.0)), 5.2, 3.6, st_entry)

    def st_cart(x, y, z, yaw):           # carrinho vazio no toco de trilho + tremonha
        F = Frame(x, y, z, yaw)
        p = F.p(0.0, -2.2)
        mine_cart(mw, p.x, p.y, z, yaw + math.pi / 2)
        q = F.p(0.3, 3.4)
        ore_bin(mw, q.x, q.y, z, yaw)
    P.place("estacao_mineracao_SW", prom_cands(203.0, 8.8), 5.6, 3.6, st_cart)

    def st_rack_crates(x, y, z, yaw):    # cavalete + caixas de madeira + sacos
        F = Frame(x, y, z, yaw)
        p = F.p(0.0, -1.8)
        pick_rack(mw, p.x, p.y, z, yaw, rng)
        q = F.p(-0.4, 2.6)
        t = wood_crate(mw, q.x, q.y, z, 1.8, yaw + 0.2)
        wood_crate(mw, q.x, q.y, t, 1.5, yaw - 0.3)
        s = F.p(0.8, 4.2)
        sack(mw, s.x, s.y, z, rng)
        col_box("DB_PropCrates", (1.7, 1.7, t - z + 1.35), (q.x, q.y, (z + t + 1.35) / 2), (0, 0, yaw + 0.2))
    P.place("estacao_mineracao_NW", prom_cands(132.0, 8.2), 5.0, 3.6, st_rack_crates)

    def st_ne(x, y, z, yaw):             # carrinho vazio sem trilho + tremonha + caixas Capsule (o lado tech)
        F = Frame(x, y, z, yaw)
        p = F.p(0.0, -2.4)
        mine_cart(mw, p.x, p.y, z, yaw + math.pi / 2 + 0.25, rails=False)
        q = F.p(0.2, 2.2)
        ore_bin(mw, q.x, q.y, z, yaw + math.pi)
        c = F.p(-0.4, 5.6)
        t = cap_crate(mc, c.x, c.y, z, 2.2, yaw + 0.3, WHITE, BLUE)
        cap_crate(mc, c.x, c.y, t, 1.8, yaw - 0.2, BLUE, WHITE, button=True)
        col_box("DB_PropCrates", (1.9, 1.9, t - z + 1.5), (c.x, c.y, (z + t + 1.5) / 2), (0, 0, yaw + 0.3))
    P.place("estacao_mineracao_NE", prom_cands(52.0, 9.6), 6.4, 3.6, st_ne)

    def st_se(x, y, z, yaw):             # carrinho no trilho + cavalete
        F = Frame(x, y, z, yaw)
        p = F.p(0.0, 2.4)
        mine_cart(mw, p.x, p.y, z, yaw - math.pi / 2)
        q = F.p(-0.2, -3.2)
        pick_rack(mw, q.x, q.y, z, yaw, rng)
    P.place("estacao_mineracao_SE", prom_cands(334.0, 9.2), 6.0, 3.6, st_se)

    # ---------------- quiosques Capsule (sem texto)
    def k_entry(x, y, z, yaw):
        kiosk_vend(mc, x, y, z, yaw)
    P.place("quiosque_capsulas_entrada", [(x, y, yaw_to(x, y, 0.0, -88.0)) for x, y in
                                          ((29.0, -78.0), (30.0, -75.0), (31.5, -81.0), (27.5, -72.0))], 2.2, 6.2,
            k_entry)

    def k_exit(x, y, z, yaw):
        kiosk_booth(mc, x, y, z, yaw)
        F = Frame(x, y, z, yaw)
        b = F.p(0.6, 4.0)
        bench(mc, b.x, b.y, z, yaw - 0.35)
    P.place("cabine_trilha_saida", [(x, y, yaw_to(x, y, 74.0, 27.0)) for x, y in
                                    ((68.0, 52.0), (64.0, 55.0), (72.0, 50.0), (60.0, 58.0))], 5.6, 6.6, k_exit)

    def k_village(x, y, z, yaw):
        kiosk_booth(mc, x, y, z, yaw)
        F = Frame(x, y, z, yaw)
        s = F.p(0.8, -3.6)
        scooter(mc, s.x, s.y, z, yaw + 1.2)
    P.place("cabine_vila_oeste", near(-36.0, 95.5, lambda x, y: yaw_to(x, y, -8.0, 100.0), 6.0), 5.3, 6.6,
            k_village)

    # ---------------- bancos (olham a arena ou o jardim)
    for nm, cands in (("banco_N_oeste", [(-26.0, 71.2), (-31.0, 70.0), (-21.0, 72.0)]),
                      ("banco_N_leste", [(28.0, 71.0), (33.0, 69.5), (23.0, 72.0)])):
        P.place(nm, [(x, y, math.atan2(-y, -x)) for x, y in cands], 2.4, 2.6,
                lambda x, y, z, yaw: bench(mc, x, y, z, yaw))
    P.place("banco_jardim_SW", [(x, y, yaw_to(x, y, -82.0, -88.0)) for x, y in
                                ((-69.0, -72.5), (-72.0, -72.0), (-66.0, -74.0))], 2.6, 2.6,
            lambda x, y, z, yaw: bench(mc, x, y, z, yaw))

    # ---------------- postes Capsule nos cruzamentos trilha x promenade (nenhuma zona pos luz ali)
    def lamp_at(tag):
        def f(x, y, z, yaw):
            LAMP_SPOTS.append(("L_DBLit_Lamp_" + tag, cap_lamp(mc, x, y, z), 240.0, WARM))
        return f
    def path_side(pts, lat_sign):
        """ao lado da trilha calcada, logo depois da sarjeta do promenade: (distancia ao longo, lado)"""
        (ax, ay), (bx, by) = pts[0], pts[1]
        ln = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / ln, (by - ay) / ln
        out = []
        for s in (lat_sign, -lat_sign):
            for lat in (4.8, 6.5):
                for d in (3.0, 6.0, 9.0, 12.0, 15.0, 18.0):
                    x, y = ax + ux * d - uy * s * lat, ay + uy * d + ux * s * lat
                    out.append((x, y, 0.0))
        return out
    paths = {"SW": L.GROUND_PATHS[0][0], "SE": L.GROUND_PATHS[1][0], "E": L.GROUND_PATHS[2][0],
             "W": L.GROUND_PATHS[3][0]}
    for tag, sg in (("SW", -1), ("SE", 1), ("E", 1), ("W", 1)):
        P.place("poste_" + tag, path_side(paths[tag], sg), 1.0, 7.4, lamp_at(tag))

    # ---------------- heliponto: carga Capsule (caixas, conteiner-capsula, tambores)
    def heli_cargo(x, y, z, yaw):
        F = Frame(x, y, z, yaw)          # +x local = para o heliponto
        a, b = F.p(0.0, -1.3), F.p(0.0, 1.3)
        cap_crate(mc, a.x, a.y, z, 2.4, yaw, WHITE, BLUE)
        cap_crate(mc, b.x, b.y, z, 2.4, yaw + 0.05, BLUE, WHITE)
        t = cap_crate(mc, *F.p(0.0, -0.4)[:2], z + 2.02, 2.1, yaw + 0.35, WHITE, NAVY, button=True)
        col_box("DB_PropCrates", (2.3, 4.9, 2.02), F.p(0.0, 0, 1.01), F.r())
        col_box("DB_PropCrates", (1.7, 1.7, t - z - 2.02), F.p(0.0, -0.4, (2.02 + t - z) / 2), F.r(0, 0, 0.35))
        c = F.p(-3.4, 0.2)
        capsule_container(mc, c.x, c.y, z, yaw + math.pi / 2)
        col_box("DB_PropCrates", (1.8, 3.4, 2.4), (c.x, c.y, z + 1.2), (0, 0, yaw))
        d = F.p(0.2, 4.4)
        drum_group(mc, d.x, d.y, z, yaw + math.pi, 3)
    P.place("carga_heliponto", near(-115.0, 62.0, lambda x, y: yaw_to(x, y, -140.0, 58.0), 7.0), 5.8, 5.0,
            heli_cargo)

    # ---------------- cabeceira da ponte do satelite SW (carga de chegada)
    def sat_cargo(x, y, z, yaw):
        F = Frame(x, y, z, yaw)
        t = cap_crate(mc, x, y, z, 2.3, yaw, WHITE, BLUE)
        cap_crate(mc, x, y, t, 1.9, yaw + 0.4, BLUE, WHITE, button=True)
        col_box("DB_PropCrates", (2.0, 2.0, t - z + 1.6), (x, y, (z + t + 1.6) / 2), (0, 0, yaw))
        d = F.p(0.2, 3.5)
        drum_group(mc, d.x, d.y, z, yaw, 2)
    P.place("carga_satelite_SW", [(x, y, yaw_to(x, y, -124.0, -78.0)) for x, y in
                                  ((-114.0, -86.0), (-112.0, -89.0), (-117.0, -89.5), (-110.0, -84.0))], 3.6, 4.0,
            sat_cargo)

    # ---------------- oficina: patio de pecas ao sul (fora do portao e do lote)
    def ws_yard(x, y, z, yaw):
        F = Frame(x, y, z, yaw)          # +x local = norte (a parede sul da oficina)
        p = F.p(1.2, -4.5)
        tool_chest(mc, p.x, p.y, z, yaw + math.pi)
        g = F.p(1.6, -2.1)
        gas_cylinders(mc, g.x, g.y, z, yaw)
        col_box("DB_PropYard", (2.0, 4.6, 2.4), F.p(1.4, -3.5, 1.2), F.r())
        e = F.p(-1.4, 0.4)
        engine_pallet(mw, e.x, e.y, z, yaw + 0.3)
        col_box("DB_PropYard", (2.5, 2.0, 2.2), (e.x, e.y, z + 1.1), (0, 0, yaw + 0.3))
        c = F.p(1.1, 3.2)
        t = cap_crate(mc, c.x, c.y, z, 2.3, yaw + 0.1, WHITE, BLUE)
        cap_crate(mc, c.x, c.y, t, 1.9, yaw - 0.3, WHITE, NAVY, button=True)
        col_box("DB_PropCrates", (2.0, 2.0, t - z + 1.6), (c.x, c.y, (z + t + 1.6) / 2), (0, 0, yaw + 0.1))
        s = F.p(-1.9, 3.0)
        spare_pad(mc, s.x, s.y, z, yaw + math.pi)
        d = F.p(-2.2, 5.8)
        drum_group(mc, d.x, d.y, z, yaw, 3)
        sc = F.p(-3.2, -3.4)
        scooter(mc, sc.x, sc.y, z, yaw + math.pi / 2 + 0.3)
    P.place("patio_oficina", near(34.0, 95.0, lambda x, y: math.pi / 2, 4.0), 7.6, 3.2, ws_yard)

    # ---------------- mercado: carrinho de feira no passeio (os balcoes do db_village ja estao cheios) + potes,
    # cestos e sacos nas laterais do carrinho; a vitrine olha para quem sobe a rua do mercado (sudoeste)
    def market_e(x, y, z, yaw):
        produce_cart(mm, x, y, z, yaw, rng)
        F = Frame(x, y, z, yaw)
        for u, v, sc_, m in ((0.9, -3.5, 0.95, BLUE), (-0.4, -3.7, 0.8, ORANGE), (0.4, -4.6, 0.7, BLUE)):
            p = F.p(u, v)
            jar(mm, p.x, p.y, z, sc_, m)
        p = F.p(1.9, -3.1)
        basket(mm, p.x, p.y, z, ORANGE, rng, 0.75)
        p = F.p(1.8, 3.3)
        basket(mm, p.x, p.y, z, APPLE, rng, 0.75)
        s1 = F.p(-0.3, 3.7)
        sack(mm, s1.x, s1.y, z, rng, 1.0)
        s2 = F.p(-1.4, 3.3)
        sack(mm, s2.x, s2.y, z, rng, 0.9)
        s3 = F.p(0.6, 4.6)
        sack(mm, s3.x, s3.y, z, rng, 0.85, lying=True)
    P.place("mercado_carrinho_feira", near(-76.0, 102.0, lambda x, y: yaw_to(x, y, -86.0, 94.0), 5.0), 5.2, 7.0,
            market_e)

    # ---------------- dojo: patio de treino ao sul (entre o pavilhao, a rocha do plato (108, -34) e a borda), em 3
    # grupos que se acomodam em volta da planta (a vegetacao do vestir e montada antes e tambem ocupa essa area)
    def dojo_mats(x, y, z, yaw):         # 2 tatames laranja/marinho + lanterna marcial (a luz do patio)
        F = Frame(x, y, z, yaw)
        m1 = F.p(-2.6, -0.2)
        mat(md, m1.x, m1.y, z, 5.0, 5.0, yaw)
        m2 = F.p(2.7, 0.2)
        mat(md, m2.x, m2.y, z, 4.4, 4.4, yaw + 0.1)
        ln = F.p(0.2, 3.7)
        LAMP_SPOTS.append(("L_DBLit_DojoYard", martial_lantern(md, ln.x, ln.y, z, yaw), 340.0, WARM_W))
    P.place("dojo_tatames", near(121.0, -31.5, lambda x, y: 0.0, 6.0), 5.9, 7.2, dojo_mats, route_clear=2.0)

    def dojo_bars(x, y, z, yaw):         # barra fixa + saco de pancada
        F = Frame(x, y, z, yaw)
        pullup_bar(md, x, y, z, yaw)
        bg = F.p(2.9, -1.3)
        punching_bag(md, bg.x, bg.y, z, yaw + math.pi / 2)

    def dojo_weights(x, y, z, yaw):      # suporte de barras + kettlebells + anilhas + banco com toalha e jarra
        F = Frame(x, y, z, yaw)
        weight_rack(md, x, y, z, yaw + math.pi / 2)
        for u, v in ((-1.3, -1.9), (0.1, -2.1)):
            p = F.p(u, v)
            kettlebell(md, p.x, p.y, z, 1.15)
        ps = F.p(1.8, -2.0)
        plate_stack(md, ps.x, ps.y, z)
        bn = F.p(0.0, 2.3)
        dojo_bench(md, bn.x, bn.y, z, yaw + math.pi / 2)
    # o grupo menor (pesos) antes: se a barra/saco precisar sair da planta (vegetacao em cima), ela anda, nao ele some
    P.place("dojo_pesos", near(124.5, -39.5, lambda x, y: 0.0, 6.0), 3.6, 3.0, dojo_weights, route_clear=2.0)
    P.place("dojo_barra_saco", near(116.5, -39.0, lambda x, y: 0.0, 11.0), 4.2, 7.6, dojo_bars, route_clear=2.0)

    # ---------------- LANTERNAS DE CAMINHO (a assinatura da concept: luz quente ao longo de toda trilha e escada).
    # So brilho (Lantern_Glow), SEM objeto de luz: o teto de luzes de dia fica como esta. Sem colisao (ver cap_lamp).
    lanterns(P, mc, md)

    # ---------------- aproximacao do summon: 1 lanterna de pedra (marcial) por lado FORA da zona livre
    # (o summon ja tem postes no pe da escada; aqui so seixos e a luz do db_lights)
    # ---------------- seixos pequenos fora da arena (perto das rochas do plato e dos jardins)
    def peb(x, y, z, yaw):
        pebbles(mw, x, y, z, random.Random(int(x * 31 + y * 17) & 0xffff), 4, 1.9)
    for i, (x, y) in enumerate(((-110.0, -40.0), (-138.0, -48.0), (98.0, -40.0), (126.0, 18.0), (-128.0, 30.0),
                                (-40.0, -108.0), (40.0, -106.0), (-100.0, -100.0), (-60.0, 64.0), (140.0, -12.0))):
        P.place("seixos_%02d" % i, around(x, y, 0.0, 4.0), 2.4, 0.8, peb, route_clear=1.5)

    mc.finish()
    mw.finish()
    mm.finish()
    md.finish()
    objs = [bpy.data.objects.get(n) for n in ("DB_Prop_Capsule", "DB_Prop_Work", "DB_Prop_Market", "DB_Prop_Dojo")]
    print("PROPS cruzamentos prop x vegetacao (antes da limpeza): %s" % veg_overlaps(objs))
    nk, nt = clear_shrub_overlaps(objs)
    print("PROPS moitas atravessadas por prop removidas: %d partes soltas (%d tris); depois: %s" % (
        nk, nt, veg_overlaps(objs)))
    print("PROPS montados: " + "; ".join(r[3:] for r in REPORT if r.startswith("ok ")))
    agg = {}
    for t, nm in COST:
        k = nm.rstrip("0123456789_AB").replace("_par", "")
        agg[k] = agg.get(k, 0) + t
    print("PROPS tris por grupo: %s" % sorted(((v, k) for k, v in agg.items()), reverse=True)[:14])
    for r in REPORT:
        if not r.startswith(("ok ", "PULADO")):
            print("PROPS nota: " + r)
    ncol = sum(1 for o in bpy.data.objects if o.name.startswith("COL_DB_Prop"))
    print("PROPS grupos montados=%d pulados=%d luzes=%d colisoes=%d" % (P.n_ok, P.n_skip, len(LAMP_SPOTS), ncol))
    for ob in (bpy.data.objects.get(n) for n in ("DB_Prop_Capsule", "DB_Prop_Work", "DB_Prop_Market", "DB_Prop_Dojo")):
        if ob is not None:
            print("PROPS %s tris=%d materiais=%s" % (ob.name, sum(len(p.vertices) - 2 for p in ob.data.polygons),
                                                     [m.name for m in ob.data.materials]))
