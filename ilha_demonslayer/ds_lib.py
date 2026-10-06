# ds_lib - base da Ilha 4 (DEMON SLAYER) sobre o pipeline do lobby (lobby_area/forja_mineradora/fm_lib.py, SO LEITURA)
# e os helpers genericos da Ilha 1 (ilha_naruto/il_lib.py, SO LEITURA). Mesma estrutura do sg_lib da Ilha 3.
# Aqui: colecoes da ilha 4, paleta DEMON SLAYER (DSMATS, secao 9 do PLANO_DS), traducao Roblox dos prefixos novos,
# prefixos de dono e helpers (escada/guarda SO VISUAIS: a colisao de tudo que e andavel e do ds_col).
# COMPARTILHADO E CONGELADO (dono: integracao / onda 0). Agentes de zona NAO editam (so acrescimos pontuais na paleta).
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
# ordem final do sys.path: HERE, DBDIR, NARUTO, LOBBY (os ds_* tem prioridade)

import bpy, bmesh
from mathutils import Vector
import fm_lib
from fm_lib import MB, D, S, col_box, col_box2, col_ramp, light, camera, add_variants, MATS, RBX_CAL
import il_lib as IL
from il_lib import ccw, clip, arc_pts, x_intervals, ribbon_poly, prism, yaw_to
import fm_parts as FP
from fm_parts import Frame
import ds_layout as L

COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_CLEARING", "04_FORGE", "05_VILLAGE", "06_SUMMON",
        "07_WATER", "08_NEXT_ISLAND", "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "11_LIGHTING",
        "12_VFX_HELPERS", "13_COLLISION", "14_GAMEPLAY_MARKERS", "15_EXPORT", "18_ENTRY", "_SCALE_REFERENCE"]
fm_lib.COLS = COLS
IL.COLS = COLS
fm_lib._FLOOR_LEVELS = tuple(sorted(set(L.LEVELS)))

# ------------------------------------------------------------------ paleta DEMON SLAYER (PLANO_DS secao 9)
# (cor_linear, rough, metal, emissao, cor_emissao, variacao). Regra de valor: caminho (claro, quente) > reboco (claro)
# > pedra media > penhasco (medio-frio) > vegetacao (medio-escura) > madeira (escura) > telhado (mais escuro).
# Os nomes levam a palavra-chave do RBX_RULES (Wood, Plaster, Roof, Stone, Metal, Leaf, Grass, Dirt).
DSMATS = {
    "Wood_DS_Dark":       (S(58, 40, 30), 0.8, 0.0, 0, None, 0.10),      # estrutura aparente, pilares, vigas, beirais
    "Wood_DS_Mid":        (S(104, 72, 48), 0.8, 0.0, 0, None, 0.12),     # tabuas, engawa, pontes, cercas
    "Wood_DS_Lacquer":    (S(150, 38, 30), 0.55, 0.0, 0, None, 0.04),    # SO torii e noren da forja
    "Plaster_DS":         (S(228, 216, 192), 0.85, 0.0, 0, None, 0.05),  # reboco claro e quente
    "Plaster_DS_Kura":    (S(238, 234, 224), 0.85, 0.0, 0, None, 0.03),  # armazem branco
    "Plaster_DS_Ochre":   (S(222, 204, 172), 0.85, 0.0, 0, None, 0.05),  # ds_kit (1b): reboco -6% quente, POR CASA
    "Plaster_DS_Ash":     (S(214, 210, 198), 0.85, 0.0, 0, None, 0.05),  # ds_kit (1b): reboco -6% frio, POR CASA
    "Plaster_DS_Shoji":   (S(204, 196, 176), 0.85, 0.0, 0, None, 0.02),  # ds_kit (1b): papel de shoji APAGADO
    "Roof_DS_Tile":       (S(52, 58, 72), 0.7, 0.0, 0, None, 0.06),      # telha escura azul-ardosia
    "Roof_DS_Ridge":      (S(38, 42, 54), 0.7, 0.0, 0, None, 0.04),      # cumeeira e onigawara
    "Stone_DS":           (S(124, 120, 112), 0.85, 0.0, 0, None, 0.10),  # ishigaki, socos, escadas
    "Stone_DS_Path":      (S(156, 146, 128), 0.85, 0.0, 0, None, 0.10),  # lajes dos caminhos (as mais claras do chao)
    "Stone_DS_Laje":      (S(136, 125, 108), 0.85, 0.0, 0, None, 0.08),  # lajes do patio/trilha (onda 1a): pedra quente media
                                                                         # (ONDA 4: era 128,118,104 - mesmo valor do Stone_DS
                                                                         # do arrimo ao lado; agora 1 degrau acima, abaixo do Path)
    "Stone_DS_Dark":      (S(72, 70, 70), 0.8, 0.0, 0, None, 0.08),      # base da forja, fornalha, podio do summon
    "Cliff_DS":           (S(86, 92, 104), 0.9, 0.0, 0, None, 0.12),     # penhasco em estratos, cinza-azulado
    "Cliff_DS_Dark":      (S(62, 66, 78), 0.9, 0.0, 0, None, 0.10),      # estrato escuro / quilha
    "Cliff_DS_Moss":      (S(70, 92, 66), 0.9, 0.0, 0, None, 0.08),      # quina com musgo (topo dos estratos)
    "Metal_DS_Iron":      (S(64, 62, 60), 0.5, 0.5, 0, None, 0.04),      # ferro envelhecido
    "Metal_DS_Rust":      (S(112, 66, 42), 0.85, 0.2, 0, None, 0.06),    # acento de ferrugem
    "Glass_DS_Lantern":   (S(255, 192, 118), 0.4, 0.0, 1.2, S(255, 170, 90), 0.0),    # papel/vidro de lanterna aceso
    "Window_DS_Warm":     (S(255, 204, 140), 0.5, 0.0, 0.7, S(255, 180, 110), 0.0),   # shoji aceso, recuado
    "Bamboo_DS":          (S(106, 136, 66), 0.7, 0.0, 0, None, 0.08),     # ONDA 4: era 118,150,72 (verde-limao, o verde
                                                                         # mais claro da ilha); segue o mais claro da vegetacao
    "Bamboo_DS_Dry":      (S(170, 160, 104), 0.7, 0.0, 0, None, 0.06),
    "Leaf_DS_Broad":      (S(46, 84, 48), 0.85, 0.0, 0, None, 0.06),
    "Leaf_DS_Cedar":      (S(34, 66, 46), 0.85, 0.0, 0, None, 0.06),
    "Leaf_DS_Shrub":      (S(66, 104, 56), 0.85, 0.0, 0, None, 0.06),
    "Leaf_DS_Bamboo":     (S(94, 130, 60), 0.85, 0.0, 0, None, 0.06),    # ds_veg (3a): folha do bambu (mais clara que o capim)
                                                                         # (ONDA 4: era 104,142,64)
    "Bark_DS":            (S(70, 52, 40), 0.9, 0.0, 0, None, 0.08),
    "Grass_DS":           (S(84, 118, 62), 0.9, 0.0, 0, None, 0.10),
    "Dirt_DS":            (S(132, 106, 76), 0.95, 0.0, 0, None, 0.10),   # chao da clareira (contraste com os minerios)
    "Dirt_DS_Dark":       (S(98, 80, 60), 0.95, 0.0, 0, None, 0.08),
    "Wisteria_DS":        (S(150, 110, 205), 0.8, 0.0, 0, None, 0.04),   # SO nos 4 acentos
    "Wisteria_DS_Light":  (S(186, 156, 230), 0.8, 0.0, 0, None, 0.02),
    "Fire_DS_Glow":       (S(255, 122, 40), 0.5, 0.0, 2.2, S(255, 122, 40), 0.0),   # boca da fornalha
    "Ember_DS_Glow":      (S(255, 84, 24), 0.5, 0.0, 1.6, S(255, 84, 24), 0.0),     # brasas
    "Cloth_DS_Indigo":    (S(46, 40, 86), 0.85, 0.0, 0, None, 0.04),     # estandartes do summon (filete violeta escuro)
    "Cloth_DS_Red":       (S(150, 36, 30), 0.85, 0.0, 0, None, 0.04),    # noren da forja
    "Stone_DS_Brick":     (S(150, 98, 72), 0.85, 0.0, 0, None, 0.06),    # ds_forge (2b): tijolo refratario da boca/fornalha
    "Stone_DS_Soot":      (S(44, 40, 40), 0.9, 0.0, 0, None, 0.04),      # ds_forge (2b): fuligem, carvao, juntas fundas
    "Metal_DS_Steel":     (S(150, 158, 170), 0.3, 0.8, 0, None, 0.0),    # ds_forge (2b): aco da lamina (ji)
    "Metal_DS_Hamon":     (S(206, 212, 220), 0.25, 0.8, 0, None, 0.0),   # ds_forge (2b): fio temperado (hamon/boshi)
    "Metal_DS_Brass":     (S(176, 138, 70), 0.4, 0.8, 0, None, 0.0),     # ds_forge (2b): habaki, fuchi, seppa
    "Lacquer_DS_Black":   (S(30, 28, 32), 0.45, 0.0, 0, None, 0.0),      # ds_forge (2b): saya, ito, suportes de laca
    "Rope_DS_Straw":      (S(186, 160, 106), 0.9, 0.0, 0, None, 0.06),   # ds_forge (2b): shimenawa e sacos de carvao
    "Water_DS_Trough":    (S(36, 50, 60), 0.15, 0.0, 0, None, 0.0),      # ds_forge (2b): agua parada do cocho de tempera
    "Plaster_DS_Clay":    (S(184, 152, 120), 0.9, 0.0, 0, None, 0.05),   # ds_forge (2b): reboco de barro quente da forja
                                                                         # (ONDA 4: era 190,150,108 - pessego; menos saturado,
                                                                         # mesma familia do reboco da vila, ainda mais quente)
    "Cloth_DS_Linen":     (S(214, 206, 184), 0.9, 0.0, 0, None, 0.04),   # ds_props (3b): algodao cru (varal, tenugui, fitas)
    "Cloth_DS_Ai":        (S(52, 70, 108), 0.9, 0.0, 0, None, 0.04),     # ds_props (3b): azul aizome (yukata, guarda-sol)
    # so previa (00_REFERENCE): mar de nuvens, lua, vizinhos
    "Cloud_DS":           (S(60, 70, 104), 0.95, 0.0, 0.04, S(70, 82, 120), 0.0),
    "Cloud_DS_Shade":     (S(40, 48, 78), 0.95, 0.0, 0.02, S(48, 56, 90), 0.0),
    "DS_MoonDisc_Glow":   (S(206, 220, 255), 0.6, 0.0, 0.8, S(206, 220, 255), 0.0),
    "DS_Star_Glow":       (S(200, 214, 255), 0.6, 0.0, 1.0, S(200, 214, 255), 0.0),
    "PREVIEW_Neighbor":   (S(58, 56, 76), 0.9, 0.0, 0, None, 0.0),
    "PREVIEW_Lobby":      (S(90, 96, 104), 0.9, 0.0, 0, None, 0.0),
    "DS_OreProxy":        (S(170, 170, 176), 0.8, 0.0, 0, None, 0.0),    # SO blockout (removido no export)
}
for k, v in DSMATS.items():
    MATS.setdefault(k, v)

# ------------------------------------------------------------------ traducao Roblox dos prefixos novos
_NEW_RULES = [("Glass_DS_Lantern", "Neon", 0.0, False),      # papel/vidro aceso DENTRO da armacao
              ("Window_DS", "SmoothPlastic", 0.0, False),     # shoji aceso: SmoothPlastic quente (como Window_Warm)
              ("Wisteria_DS", "SmoothPlastic", 0.0, False),
              ("Bamboo_DS", "Wood", 0.0, True),
              ("Cliff_DS", "Slate", 0.0, True),
              ("Bark_DS", "Wood", 0.0, True),
              ("Cloth_DS", "Fabric", 0.0, True),
              ("Fire_DS", "Neon", 0.0, False), ("Ember_DS", "Neon", 0.0, False)]
for r in reversed(_NEW_RULES):
    if r not in fm_lib.RBX_RULES:
        fm_lib.RBX_RULES.insert(0, r)
for k in ("Glass_DS_Lantern", "Fire_DS_Glow", "Ember_DS_Glow", "Window_DS_Warm"):
    RBX_CAL.setdefault(k, (None, [int(c) for c in fm_lib.to_srgb(DSMATS[k][0])]))
# blockout com materiais SIMPLES: sem textura de detalhe nos materiais da ilha (a forma tem de ler sozinha)
for _p in ("Stone_DS", "Wood_DS", "Roof_DS", "Plaster_DS", "Grass_DS", "Dirt_DS"):
    if (_p, None) not in fm_lib.TEX_RULES:
        fm_lib.TEX_RULES = ((_p, None),) + tuple(fm_lib.TEX_RULES)
add_variants("Cliff_DS", [("Cliff_DS", 5), ("Cliff_DS_B", 3, (78, 84, 96))], cap=2)
add_variants("Stone_DS", [("Stone_DS", 5), ("Stone_DS_B", 3, (112, 108, 100))], cap=2)
add_variants("Grass_DS", [("Grass_DS", 6), ("Grass_DS_B", 4, (76, 108, 58))], cap=2)

# prefixos de dono (export Roblox): DS_<Zona>_<Coisa>
OWNER_PREFIX = {"terrain": ("DS_Ter_",), "entry": ("DS_Ent_",), "village": ("DS_Vil_",), "clearing": ("DS_Clr_",),
                "forge": ("DS_Frg_",), "summon": ("DS_Sum_",), "exit": ("DS_Exit_",), "gate_op": ("GATE_OnePiece",),
                "water": ("DS_Water_",), "props": ("DS_Prop_",), "vegetation": ("DS_Veg_",), "vfx": ("VFX_",)}


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
    """Sutherland-Hodgman: parte do poligono com a*x + b*y + c >= 0"""
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
    P = ccw(poly)
    n = len(P)
    out = []
    for i in range(n):
        a, b, c = P[i - 1], P[i], P[(i + 1) % n]
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
    """offset_poly com deslocamento VARIAVEL por vertice: dfun(i, angulo em volta do centroide) -> d (variacao
    DIRIGIDA - senoides - nao sorteio)"""
    P = ccw(poly)
    c = centroid(P)
    n = len(P)
    out = []
    for i in range(n):
        a, b, cc = P[i - 1], P[i], P[(i + 1) % n]
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
    """contorno irregular (pegada de rocha) em volta de (x, y)"""
    import random
    rng = rng or random.Random(int(x * 13 + y * 7) & 0xffff)
    return [(x + sx * r * (1.0 + rng.uniform(-amp, amp)) * math.cos(rot + 2 * math.pi * i / n),
             y + r * (1.0 + rng.uniform(-amp, amp)) * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def sloped_prism(mb, poly, z0, zfun, m, top_m=None, top_t=0.3):
    """prisma com o TOPO inclinado (z = zfun(x, y) em cada vertice; use zfun linear para o topo ficar plano) e o fundo
    em z0. top_m: tampo fino (top_t) de outro material por cima"""
    P = ccw(poly)
    bm = mb.bm
    vb = [bm.verts.new((x, y, z0)) for x, y in P]
    ztop = [zfun(x, y) - (top_t if top_m else 0.0) for x, y in P]
    vt = [bm.verts.new((x, y, z)) for (x, y), z in zip(P, ztop)]
    n = len(P)
    bm.faces.new(list(reversed(vb)))
    bm.faces.new(vt)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m, None, 0, 1)
    if top_m:
        vb2 = [bm.verts.new((x, y, z)) for (x, y), z in zip(P, ztop)]
        vt2 = [bm.verts.new((x, y, zfun(x, y))) for x, y in P]
        bm.faces.new(list(reversed(vb2)))
        bm.faces.new(vt2)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((vb2[i], vb2[j], vt2[j], vt2[i]))
        mb._post(vb2 + vt2, top_m, None, 0, 1)


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


# ------------------------------------------------------------------ escadas / guardas SO VISUAIS (colisao: ds_col)
def plan_stair(mb, name, m="Stone_DS_Path", riser_m="Stone_DS", side_m="Stone_DS", stringers=True, side_floor=None):
    """a escada 'name' da planta (ds_layout.STAIRS) so no visual, casando com a colisao do ds_col (mesmo envelope,
    mesmas cotas). Blockout: pisada inteira com focinho saliente 0,12 e espelho recuado num tom abaixo; banzos laterais
    macicos ate side_floor (padrao: o pe da escada) - o lance le como pedra cortada no arrimo."""
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


def vis_fence(mb, pts, h=3.0, post_step=4.0, m="Wood_DS_Dark", rail_m="Wood_DS_Mid"):
    """cerca baixa de madeira (mouroes + 2 travessas), so visual"""
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
