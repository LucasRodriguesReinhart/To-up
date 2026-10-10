# op_lib - base da Ilha 5 (ONE PIECE / WANO) sobre o pipeline do lobby (lobby_area/forja_mineradora/fm_lib.py, SO
# LEITURA) e os helpers genericos da Ilha 1 (ilha_naruto/il_lib.py, SO LEITURA). Mesma estrutura do ds_lib da Ilha 4.
# Aqui: colecoes da ilha 5, paleta WANO (OPMATS, secao 10 do PLANO_OP), traducao Roblox dos prefixos novos, prefixos de
# dono e helpers (escada/guarda SO VISUAIS: a colisao de tudo que e andavel e do op_col).
# COMPARTILHADO E CONGELADO (dono: integracao / M1). Agentes de zona NAO editam (so acrescimos pontuais na paleta).
import os, sys, math
sys.dont_write_bytecode = True          # nada de __pycache__ nas pastas das outras ilhas (so leitura)
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
NARUTO = os.path.join(ROOT, "ilha_naruto")
DBDIR = os.path.join(ROOT, "ilha_dragonball")
LOBBY = os.path.join(ROOT, "lobby_area", "forja_mineradora")
for p in (LOBBY, NARUTO, DBDIR, HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
# ordem final do sys.path: HERE, DBDIR, NARUTO, LOBBY (os op_* tem prioridade)

import bpy, bmesh
from mathutils import Vector
import fm_lib
from fm_lib import MB, D, S, col_box, col_box2, col_ramp, light, camera, add_variants, MATS, RBX_CAL
import il_lib as IL
from il_lib import ccw, clip, arc_pts, x_intervals, ribbon_poly, prism, yaw_to
import fm_parts as FP
from fm_parts import Frame
import op_layout as L

COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_PLAZA", "04_CASTLE", "05_CAPITAL", "06_SUMMON",
        "07_WATER", "08_NEXT_ISLAND", "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "11_LIGHTING",
        "12_VFX_HELPERS", "13_COLLISION", "14_GAMEPLAY_MARKERS", "15_EXPORT", "16_HARBOR", "17_LANDMARKS",
        "18_ENTRY", "_SCALE_REFERENCE"]
fm_lib.COLS = COLS
IL.COLS = COLS
fm_lib._FLOOR_LEVELS = tuple(sorted(set(L.LEVELS)))

# ------------------------------------------------------------------ paleta WANO (PLANO_OP secao 10)
# (cor_linear, rough, metal, emissao, cor_emissao, variacao). Regra de valor (DIA): piso da praca/caminho (claro,
# quente) ~ reboco (claro) > pedra media > falesia (cinza clara-fria) > vegetacao (media) > madeira (escura) > telha
# azul-escura (a mais escura). Vermelho/dourado SO em pecas escolhidas (torii, pontes, varanda, portao, remates).
# Os nomes levam a palavra-chave do RBX_RULES (Wood, Plaster, Roof, Stone, Metal, Leaf, Grass, Flower, Cloth...).
OPMATS = {
    "Wood_OP_Dark":       (S(66, 46, 34), 0.8, 0.0, 0, None, 0.10),      # estrutura aparente, pilares, vigas, beirais
    "Wood_OP_Mid":        (S(128, 92, 60), 0.8, 0.0, 0, None, 0.12),     # tabuas, varandas, cais, cascos
    "Wood_OP_Lacquer":    (S(186, 42, 34), 0.55, 0.0, 0, None, 0.04),    # vermelho: torii, pontes, varanda, portao
    "Wood_OP_Hull":       (S(104, 66, 42), 0.8, 0.0, 0, None, 0.08),     # casco do navio
    "Plaster_OP":         (S(234, 228, 212), 0.85, 0.0, 0, None, 0.04),  # reboco claro (castelo, casas)
    "Plaster_OP_Warm":    (S(226, 210, 182), 0.85, 0.0, 0, None, 0.05),  # reboco quente (por CONJUNTO)
    "Plaster_OP_Shop":    (S(214, 196, 164), 0.85, 0.0, 0, None, 0.05),  # reboco das lojas da rua de chegada
    "Roof_OP_Blue":       (S(46, 58, 92), 0.7, 0.0, 0, None, 0.05),      # telha azul-escura (maioria)
    "Roof_OP_Green":      (S(58, 104, 84), 0.7, 0.0, 0, None, 0.05),     # telhado verde (terraco alto, esquinas)
    "Roof_OP_Red":        (S(150, 62, 46), 0.7, 0.0, 0, None, 0.05),     # telhado avermelhado (santuario, esquina-marco)
    "Roof_OP_Ridge":      (S(30, 36, 54), 0.7, 0.0, 0, None, 0.04),      # cumeeira, onigawara, beirais escuros
    "Roof_OP_Shingle":    (S(92, 70, 52), 0.8, 0.0, 0, None, 0.06),      # telhado de madeira (porto)
    "Metal_OP_Gold":      (S(220, 172, 70), 0.35, 0.8, 0, None, 0.0),    # dourado seletivo (shachihoko, remates, guarda)
    "Metal_OP_Iron":      (S(70, 70, 74), 0.5, 0.5, 0, None, 0.04),
    "Metal_OP_Steel":     (S(176, 184, 196), 0.3, 0.8, 0, None, 0.0),    # lamina da espada monumental
    "Stone_OP":           (S(160, 154, 142), 0.85, 0.0, 0, None, 0.08),  # ishigaki, socos, escadas, muros
    "Stone_OP_Path":      (S(172, 164, 148), 0.85, 0.0, 0, None, 0.06),  # caminhos, degraus (claro quente)
    "Stone_OP_Plaza":     (S(164, 156, 140), 0.85, 0.0, 0, None, 0.05),  # pavimento da praca (minerios leem por cima)
    "Stone_OP_Inlay":     (S(150, 128, 98), 0.85, 0.0, 0, None, 0.03),   # emblema RENTE do chao (tom abaixo, sem relevo)
    "Stone_OP_Dark":      (S(100, 98, 96), 0.85, 0.0, 0, None, 0.06),
    "Cliff_OP":           (S(132, 134, 140), 0.9, 0.0, 0, None, 0.10),   # falesia cinza clara (concept)
    "Cliff_OP_Dark":      (S(94, 98, 108), 0.9, 0.0, 0, None, 0.08),     # estratos escuros / quilha / caveira
    "Cliff_OP_Moss":      (S(90, 128, 70), 0.9, 0.0, 0, None, 0.08),     # topo das falesias com musgo
    "Cliff_OP_Void":      (S(38, 40, 48), 0.95, 0.0, 0, None, 0.0),      # cavidades da caveira (orbitas, nariz, boca)
    "Cliff_OP_Horn":      (S(58, 56, 62), 0.8, 0.0, 0, None, 0.04),      # chifres da caveira (rocha escura polida)
    "Cliff_OP_Warm":      (S(178, 170, 156), 0.9, 0.0, 0, None, 0.08),   # M4 op_terrain: face clara-quente das falesias
    "Cliff_OP_Cool":      (S(136, 138, 146), 0.9, 0.0, 0, None, 0.08),   # M4 op_terrain: estrato de baixo / massas de sombra
    "Grass_OP_Deep":      (S(72, 120, 56), 0.9, 0.0, 0, None, 0.08),     # M4 op_terrain: berma verde e capa que cai na falesia
    "Stone_OP_Wall":      (S(160, 154, 144), 0.85, 0.0, 0, None, 0.06),  # M4 op_terrain: pedra aparelhada dos arrimos
    "Dirt_OP_Dark":       (S(112, 92, 70), 0.95, 0.0, 0, None, 0.06),    # M4 op_terrain: leito, saia da pele, fundo dos canais
    "Cliff_OP_Face":      (S(121, 121, 129), 0.9, 0.0, 0, None, 0.08),   # M6b op_terrain (item 51): face das falesias (era Warm)
    "Cliff_OP_Shade":     (S(97, 103, 121), 0.9, 0.0, 0, None, 0.08),   # M6b op_terrain (item 51): massas de sombra (era Cool)
    "Cliff_OP_Crevice":   (S(66, 72, 90), 0.9, 0.0, 0, None, 0.06),      # M6b op_terrain (item 51): fendas entre colunas
    "Stone_OP_Court":     (S(158, 150, 136), 0.85, 0.0, 0, None, 0.05),  # M6b (item 25): cascalho do patio do castelo (op_castle)
    "Grass_OP":           (S(108, 156, 74), 0.9, 0.0, 0, None, 0.10),    # grama diurna
    "Dirt_OP":            (S(168, 140, 104), 0.95, 0.0, 0, None, 0.08),
    "Leaf_OP":            (S(66, 122, 62), 0.85, 0.0, 0, None, 0.06),
    "Leaf_OP_Pine":       (S(44, 94, 62), 0.85, 0.0, 0, None, 0.06),
    "Flower_OP_Blossom":  (S(240, 150, 198), 0.8, 0.0, 0, None, 0.04),   # flor de cerejeira (acento + arvore monumental)
    "Flower_OP_Light":    (S(250, 196, 224), 0.8, 0.0, 0, None, 0.03),
    "Flower_OP_Deep":     (S(206, 108, 164), 0.85, 0.0, 0, None, 0.03),  # M3 op_tree: face de baixo das massas da copa
    "Bark_OP":            (S(98, 74, 56), 0.9, 0.0, 0, None, 0.08),      # casca (arvore monumental e cerejeiras)
    "Bark_OP_Groove":     (S(46, 34, 28), 0.9, 0.0, 0, None, 0.06),      # V2 op_tree: fundo dos sulcos da casca (fibra le sem textura)
    "Leaf_OP_Sun":        (S(118, 164, 80), 0.85, 0.0, 0, None, 0.05),   # V2 op_tree/op_veg: topo ensolarado das almofadas de pinheiro
    "Cloth_OP_White":     (S(236, 232, 222), 0.85, 0.0, 0, None, 0.03),  # estandartes, velas
    "Cloth_OP_Indigo":    (S(44, 52, 96), 0.85, 0.0, 0, None, 0.03),     # noren, faixa dos estandartes
    "Cloth_OP_Red":       (S(176, 40, 34), 0.85, 0.0, 0, None, 0.03),
    "Cloth_OP_Sail":      (S(236, 226, 200), 0.85, 0.0, 0, None, 0.03),
    "Cloth_OP_Black":     (S(34, 32, 38), 0.85, 0.0, 0, None, 0.02),     # M3 op_ship: contorno/olhos do Jolly Roger, bandeira
    "Cloth_OP_Straw":     (S(226, 184, 86), 0.85, 0.0, 0, None, 0.04),   # M3 op_ship/op_harbor: chapeu de palha, fardos de arroz
    "Roof_OP_Teal":       (S(62, 148, 138), 0.7, 0.0, 0, None, 0.05),    # PLANO_V2 (V2-0) / op_kit2: telhado verde-agua (ref_03)
    "Roof_OP_Cobalt":     (S(60, 90, 168), 0.7, 0.0, 0, None, 0.05),    # PLANO_V2 (V2-0): telha azul-cobalto (avenida, ref_03)
    "Roof_OP_Violet":     (S(104, 84, 152), 0.7, 0.0, 0, None, 0.05),   # PLANO_V2 (V2-0): telha roxa (bairro do canal, lojas NE)
    "Roof_OP_RedV2":      (S(172, 62, 52), 0.7, 0.0, 0, None, 0.05),    # PLANO_V2 (V2-0): telha vermelha (rua alta do porto, esquinas)
    "Stone_OP_Curb":      (S(150, 144, 134), 0.85, 0.0, 0, None, 0.05),  # PLANO_V2 (V2-0): meio-fio de pedra (0,3) das vias com calcada
    "Stone_OP_Gutter":    (S(112, 108, 102), 0.9, 0.0, 0, None, 0.04),   # PLANO_V2 (V2-0): sarjeta (0,8, -0,15) entre leito e meio-fio
    "Leaf_OP_PinePad":    (S(52, 108, 66), 0.85, 0.0, 0, None, 0.05),    # PLANO_V2 (V2-0): almofada do pinheiro em nuvem (face de cima)
    "Leaf_OP_PineUnder":  (S(30, 68, 46), 0.85, 0.0, 0, None, 0.04),     # PLANO_V2 (V2-0): face de baixo da almofada (mais escura)
    "Cloth_OP_Tatami":    (S(192, 180, 124), 0.9, 0.0, 0, None, 0.04),   # KIT2 op_kit2: tatami dos interiores
    "Roof_OP_Castle":     (S(36, 42, 86), 0.7, 0.0, 0, None, 0.04),     # V3 op_castle: telha do castelo (azul-marinho profundo do anime)
    "Plaster_OP_Castle":  (S(228, 228, 236), 0.85, 0.0, 0, None, 0.03),  # V3 op_castle: reboco frio (branco-lilas do castelo do anime)
    "Wood_OP_Sumi":       (S(42, 42, 56), 0.75, 0.0, 0, None, 0.06),     # V3 op_castle: tabuas shitami/pilares/caixilhos (preto-azulado)
    "Glass_OP_Lantern":   (S(232, 160, 96), 0.4, 0.0, 1.0, S(240, 170, 110), 0.0),   # papel aceso DENTRO da armacao
    "Window_OP_Warm":     (S(250, 212, 160), 0.5, 0.0, 0.5, S(255, 190, 120), 0.0),  # shoji aceso, recuado
    "Water_OP_Basin":     (S(36, 120, 130), 0.15, 0.0, 0, None, 0.0),    # so previa (a agua e do Roblox)
    # so previa (00_REFERENCE): mar local, vizinhos
    "PREVIEW_Sea":        (S(40, 168, 186), 0.12, 0.0, 0.0, None, 0.0),
    "PREVIEW_SeaDeep":    (S(24, 110, 150), 0.12, 0.0, 0.0, None, 0.0),
    "PREVIEW_Falls":      (S(200, 236, 246), 0.2, 0.0, 0.15, S(200, 236, 246), 0.0),
    "PREVIEW_Neighbor":   (S(58, 56, 76), 0.9, 0.0, 0, None, 0.0),
    "OP_OreProxy":        (S(170, 170, 176), 0.8, 0.0, 0, None, 0.0),    # SO blockout (removido no export)
}
for k, v in OPMATS.items():
    MATS.setdefault(k, v)

# ------------------------------------------------------------------ traducao Roblox dos prefixos novos
_NEW_RULES = [("Glass_OP_Lantern", "Neon", 0.0, False),      # papel/vidro aceso DENTRO da armacao
              ("Window_OP", "SmoothPlastic", 0.0, False),
              ("Cliff_OP", "Slate", 0.0, True),
              ("Bark_OP", "Wood", 0.0, True),
              ("Cloth_OP", "Fabric", 0.0, True),
              ("Stone_OP_Inlay", "SmoothPlastic", 0.0, False)]
for r in reversed(_NEW_RULES):
    if r not in fm_lib.RBX_RULES:
        fm_lib.RBX_RULES.insert(0, r)
for k in ("Glass_OP_Lantern", "Window_OP_Warm"):
    RBX_CAL.setdefault(k, (None, [int(c) for c in fm_lib.to_srgb(OPMATS[k][0])]))
# blockout com materiais SIMPLES: sem textura de detalhe nos materiais da ilha (a forma tem de ler sozinha)
for _p in ("Stone_OP", "Wood_OP", "Roof_OP", "Plaster_OP", "Grass_OP", "Dirt_OP", "Cliff_OP"):
    if (_p, None) not in fm_lib.TEX_RULES:
        fm_lib.TEX_RULES = ((_p, None),) + tuple(fm_lib.TEX_RULES)
add_variants("Cliff_OP", [("Cliff_OP", 5), ("Cliff_OP_B", 3, (140, 136, 130))], cap=2)
add_variants("Stone_OP", [("Stone_OP", 5), ("Stone_OP_B", 3, (148, 144, 136))], cap=2)
add_variants("Grass_OP", [("Grass_OP", 6), ("Grass_OP_B", 4, (96, 142, 68))], cap=2)

# prefixos de dono (export Roblox): OP_<Zona>_<Coisa>
OWNER_PREFIX = {"terrain": ("OP_Ter_",), "entry": ("OP_Ent_",), "capital": ("OP_Cap_",), "plaza": ("OP_Plz_",),
                "castle": ("OP_Cas_",), "tree": ("OP_Tree_",), "harbor": ("OP_Port_",), "ship": ("OP_Ship_",),
                "summon": ("OP_Sum_",), "exit": ("OP_Exit_",), "gate_opm": ("GATE_OnePunchMan",),
                "landmarks": ("OP_Lmk_",), "water": ("OP_Water_",), "props": ("OP_Prop_",),
                "vegetation": ("OP_Veg_",), "vfx": ("VFX_",)}


# ------------------------------------------------------------------ cena
def reset_scene():
    fm_lib.COLS = COLS
    fm_lib.reset_scene()
    fm_lib._COL_COUNT.clear()


def mk(name, loc, rot=(0, 0, 0), size=2.0, kind="PLAIN_AXES", props=None, c="14_GAMEPLAY_MARKERS"):
    return fm_lib.marker(name, loc, rot, size, kind, c, props)


def rim():
    return ccw(L.ISLAND_RIM)


# ------------------------------------------------------------------ geometria 2D
def clip_half(poly, a, b, c):
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        fp, fq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t))
    return out


def scale_poly(poly, f, c):
    return [(c[0] + (x - c[0]) * f, c[1] + (y - c[1]) * f) for x, y in poly]


def offset_poly(poly, d):
    """desloca cada vertice d para fora (bissetriz; poligono anti-horario). d < 0 = para dentro"""
    P_ = ccw(poly)
    n = len(P_)
    out = []
    for i in range(n):
        a, b, c = P_[i - 1], P_[i], P_[(i + 1) % n]
        e0 = (b[0] - a[0], b[1] - a[1])
        e1 = (c[0] - b[0], c[1] - b[1])
        l0 = math.hypot(*e0) or 1.0
        l1 = math.hypot(*e1) or 1.0
        n0 = (e0[1] / l0, -e0[0] / l0)
        n1 = (e1[1] / l1, -e1[0] / l1)
        nx, ny = n0[0] + n1[0], n0[1] + n1[1]
        ln = math.hypot(nx, ny) or 1.0
        nx, ny = nx / ln, ny / ln
        k = max(0.5, nx * n0[0] + ny * n0[1])
        out.append((b[0] + nx * d / k, b[1] + ny * d / k))
    return out


def offset_poly_var(poly, dfun):
    P_ = ccw(poly)
    c = centroid(P_)
    n = len(P_)
    out = []
    for i in range(n):
        a, b, cc = P_[i - 1], P_[i], P_[(i + 1) % n]
        e0 = (b[0] - a[0], b[1] - a[1])
        e1 = (cc[0] - b[0], cc[1] - b[1])
        l0 = math.hypot(*e0) or 1.0
        l1 = math.hypot(*e1) or 1.0
        nx, ny = e0[1] / l0 + e1[1] / l1, -e0[0] / l0 - e1[0] / l1
        ln = math.hypot(nx, ny) or 1.0
        d = dfun(i, math.atan2(b[1] - c[1], b[0] - c[0]))
        out.append((b[0] + nx / ln * d, b[1] + ny / ln * d))
    return out


def centroid(poly):
    return (sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly))


def blob_poly(x, y, r, n=12, rng=None, amp=0.18, rot=0.0, sx=1.0):
    import random
    rng = rng or random.Random(int(x * 13 + y * 7) & 0xffff)
    return [(x + sx * r * (1.0 + rng.uniform(-amp, amp)) * math.cos(rot + 2 * math.pi * i / n),
             y + r * (1.0 + rng.uniform(-amp, amp)) * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def wall_ribbon(mb, pts, z0, z1, th, m, cap_m=None, cap_h=0.6, side=1.0):
    """muro (faixa vertical) ao longo da polilinha pts, espessura th para o lado 'side' (+1 = esquerda da polilinha)"""
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.3:
            continue
        nx, ny = -dy / ln * side, dx / ln * side
        cx, cy = (a[0] + b[0]) / 2 + nx * th / 2, (a[1] + b[1]) / 2 + ny * th / 2
        ang = math.atan2(dy, dx)
        mb.box((ln + th * 0.6, th, z1 - z0), (cx, cy, (z0 + z1) / 2), (0, 0, ang), m, 0.0)
        if cap_m:
            mb.box((ln + th * 0.6 + 0.2, th + 0.3, cap_h), (cx, cy, z1 + cap_h / 2), (0, 0, ang), cap_m, 0.0)


# ------------------------------------------------------------------ escadas / guardas SO VISUAIS (colisao: op_col)
def plan_stair(mb, name, m="Stone_OP_Path", riser_m="Stone_OP", side_m="Stone_OP", stringers=True, side_floor=None):
    """a escada 'name' da planta (op_layout.STAIRS) so no visual, casando com a colisao do op_col (mesmo envelope,
    mesmas cotas). Pisada com focinho saliente 0,12 e espelho recuado; banzos macicos ate side_floor (padrao: o pe)."""
    foot, deg, w, n, tread, g = L.stair_frame(name)
    rise = L.stair_rise(name)
    ang = math.radians(deg)
    F = Frame(foot[0], foot[1], foot[2], ang)
    TH, NOSE = 0.26, 0.12
    zf = foot[2] if side_floor is None else side_floor
    for i in range(n):
        ztop = rise * (i + 1)
        hc = ztop - TH - 0.02
        if hc > 0.02:
            mb.box((tread + 0.02, w - 0.06, hc), F.p(tread * i + tread / 2 + 0.01, 0, hc / 2), F.r(), riser_m, 0.0)
        x0, x1 = tread * i - NOSE, tread * (i + 1) + 0.01
        mb.box((x1 - x0, w, TH), F.p((x0 + x1) / 2, 0, ztop - TH / 2), F.r(), m, 0.04)
    if stringers:
        for s in (-1, 1):
            for i in range(n):
                h = rise * (i + 1) + 1.0 + (foot[2] - zf)
                mb.box((tread + 0.05, 1.2, h), F.p(tread * i + tread / 2, s * (w / 2 + 0.6), rise * (i + 1) + 1.0 - h / 2),
                       F.r(), side_m, 0.0)
    return F.p(tread * n, 0, rise * n)


def vis_fence(mb, pts, h=3.0, post_step=4.0, m="Wood_OP_Dark", rail_m="Wood_OP_Mid"):
    """cerca/guarda-corpo de madeira (mouroes + 2 travessas), so visual"""
    for a, b in zip(pts, pts[1:]):
        a, b = Vector(a), Vector(b)
        d = b - a
        ln = d.length
        if ln < 0.3:
            continue
        k = max(1, int(round(ln / post_step)))
        for i in range(k + 1):
            p = a + d * (i / k)
            mb.box((0.45, 0.45, h), (p.x, p.y, p.z + h / 2), (0, 0, math.atan2(d.y, d.x)), m, 0.0)
        for zz in (h * 0.45, h * 0.88):
            c = (a + b) / 2
            mb.box((ln, 0.22, 0.32), (c.x, c.y, c.z + zz), (0, 0, math.atan2(d.y, d.x)), rail_m, 0.0)


# ------------------------------------------------------------------ referencia de escala
def dummy(name, x, y, z, ang=0.0, visible=True):
    """boneco R15 de 5,2 studs (mesma convencao do lobby e das outras ilhas)"""
    mb = MB(name, "_SCALE_REFERENCE")
    F = Frame(x, y, z, ang)
    for dx, dz, sx, sz in ((-0.5, 1.0, 0.9, 2.0), (0.5, 1.0, 0.9, 2.0), (0, 3.0, 2.0, 2.0), (-1.5, 3.0, 0.9, 2.0),
                           (1.5, 3.0, 0.9, 2.0)):
        mb.box((sx, 0.9 if sx < 2 else 1.0, sz), F.p(dx, 0, dz), F.r(), "Dummy_Grey", 0.08)
    mb.box((1.15, 1.15, 1.15), F.p(0, 0, 4.6), F.r(), "Dummy_Grey", 0.25)
    ob = mb.finish()
    ob.hide_render = not visible
    return ob
