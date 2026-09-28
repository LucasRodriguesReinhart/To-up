# sg_lib - base da Ilha 3 (Shadow Garden) sobre o pipeline do lobby (lobby_area/forja_mineradora/fm_lib.py), os helpers
# genericos da Ilha 1 (ilha_naruto/il_lib.py) e da Ilha 2 (ilha_dragonball/db_lib.py: ring_band, dome, blob_poly...).
# Aqui: colecoes da ilha 3, paleta SHADOW GARDEN (SMATS), traducao Roblox dos prefixos novos e helpers de escada/guarda
# SO VISUAIS (a colisao de tudo que e andavel e do sg_col, congelado).
# COMPARTILHADO E CONGELADO (dono: integracao). Agentes de zona NAO editam.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
DBDIR = os.path.normpath(os.path.join(HERE, "..", "ilha_dragonball"))
NARUTO = os.path.normpath(os.path.join(HERE, "..", "ilha_naruto"))
LOBBY = os.path.normpath(os.path.join(HERE, "..", "lobby_area", "forja_mineradora"))
for p in (LOBBY, NARUTO, DBDIR, HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
# ordem final do sys.path: HERE, DBDIR, NARUTO, LOBBY  (os sg_* tem prioridade)

import bpy
from mathutils import Vector
import fm_lib
from fm_lib import MB, D, S, col_box, col_box2, col_ramp, light, camera, add_variants, MATS, RBX_CAL
import il_lib as IL
from il_lib import (ccw, clip, area, arc_pts, x_intervals, ribbon_poly, col_poly, col_annulus, prism, annulus,
                    yaw_to)
import fm_parts as FP
from fm_parts import Frame
import sg_layout as L

COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_MINING_HALL", "04_CASTLE", "05_VILLAGE", "06_SUMMON",
        "07_WATER", "08_NEXT_ISLAND", "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "11_LIGHTING",
        "12_VFX_HELPERS", "13_COLLISION", "14_GAMEPLAY_MARKERS", "15_EXPORT", "16_CRAFT", "17_DUNGEON",
        "18_ENTRY", "_SCALE_REFERENCE"]
fm_lib.COLS = COLS
IL.COLS = COLS
fm_lib._FLOOR_LEVELS = tuple(sorted(set(L.LEVELS + (L.DUN_Z,))))

# ------------------------------------------------------------------ traducao Roblox dos prefixos novos
_NEW_RULES = [("Glass_SG", "Glass", 0.3, False), ("SG_", "Neon", 0.0, False)]
for r in reversed(_NEW_RULES):
    if r not in fm_lib.RBX_RULES:
        fm_lib.RBX_RULES.insert(0, r)

# ------------------------------------------------------------------ paleta SHADOW GARDEN (lida na concept aprovada)
# elegancia escura: pedra fria azul-ardosia, navy, madeira escura, ardosia; roxo DESSATURADO so como acento de funcao;
# janelas/lanternas quentes pontuais. (cor_linear, rough, metal, emissao, cor_emissao, variacao)
SMATS = {
    # terreno frio
    "Cliff_Rock_SG":        (S(70, 74, 92), 0.9, 0.0, 0, None, 0.12),      # basalto azul-ardosia (penhascos, colunas)
    "Cliff_Rock_SG_Dark":   (S(44, 46, 60), 0.9, 0.0, 0, None, 0.10),      # estratos escuros / sombra
    "Cliff_Rock_SG_Top":    (S(104, 110, 128), 0.9, 0.0, 0, None, 0.10),   # borda de topo (luar)
    "Grass_SG":             (S(46, 70, 64), 0.9, 0.0, 0, None, 0.16),      # grama fria (verde-azulado escuro)
    "Dirt_SG":              (S(64, 58, 60), 0.95, 0.0, 0, None, 0.12),
    # construido
    "Stone_Paving_SG":      (S(128, 132, 148), 0.85, 0.0, 0, None, 0.12),  # calcamento frio claro (ruas, patios)
    "Stone_SG_Block":       (S(92, 96, 114), 0.85, 0.0, 0, None, 0.12),    # muros de arrimo / muralha
    "Stone_SG_Castle":      (S(78, 82, 102), 0.8, 0.0, 0, None, 0.10),     # alvenaria do castelo
    "Stone_SG_Trim":        (S(150, 154, 170), 0.8, 0.0, 0, None, 0.06),   # frisos, molduras, cantaria clara
    "Stone_SG_Floor":       (S(66, 68, 84), 0.7, 0.0, 0, None, 0.08),      # piso do salao (escuro polido)
    "Roof_SG_Slate":        (S(40, 46, 66), 0.6, 0.0, 0, None, 0.08),      # ardosia (telhados ingremes)
    "Roof_SG_Navy":         (S(30, 36, 72), 0.55, 0.0, 0, None, 0.06),     # coberturas do castelo (navy)
    "Wood_SG_Dark":         (S(58, 44, 40), 0.8, 0.0, 0, None, 0.10),      # enxaimel / portas / vigas
    "Plaster_SG":           (S(150, 142, 132), 0.7, 0.0, 0, None, 0.06),   # reboco da meia-enxaimel (quente apagado)
    "Metal_SG_Iron":        (S(56, 58, 68), 0.45, 0.8, 0, None, 0.04),     # ferro preto (grades, lanternas)
    "Metal_SG_Silver":      (S(176, 182, 198), 0.3, 0.9, 0, None, 0.02),   # prata (remates, simbolos)
    "Cloth_SG_Navy":        (S(32, 38, 78), 0.8, 0.0, 0, None, 0.04),      # estandartes
    "Cloth_SG_Violet":      (S(84, 64, 118), 0.8, 0.0, 0, None, 0.04),     # tecido roxo dessaturado (acento)
    "Glass_SG_Rose":        (S(96, 70, 150), 0.1, 0.0, 0.35, S(120, 80, 200), 0.0),   # vitral/rosacea (Glass)
    "Leaf_SG_Pine":         (S(30, 50, 48), 0.85, 0.0, 0, None, 0.10),     # pinheiro escuro
    "Water_SG":             (S(60, 110, 176), 0.1, 0.0, 0.12, S(70, 130, 210), 0.0),
    # brilhos (Neon no Roblox): violeta so em funcao (dungeon, invocacao, craft, rosacea); azul frio = lua/agua
    "SG_Violet_Glow":       (S(150, 100, 235), 0.3, 0.0, 2.6, S(150, 100, 235), 0.0),
    "SG_Moon_Glow":         (S(170, 200, 255), 0.3, 0.0, 2.0, S(170, 200, 255), 0.0),
}
for k, v in SMATS.items():
    MATS.setdefault(k, v)
for k in ("SG_Violet_Glow", "SG_Moon_Glow"):
    RBX_CAL.setdefault(k, (None, [int(c) for c in fm_lib.to_srgb(SMATS[k][0])]))
add_variants("Cliff_Rock_SG", [("Cliff_Rock_SG", 5), ("Cliff_Rock_SG_B", 3, (62, 66, 84)),
                               ("Cliff_Rock_SG_C", 2, (80, 84, 100))], cap=2)
add_variants("Stone_Paving_SG", [("Stone_Paving_SG", 5), ("Stone_Paving_SG_B", 3, (118, 122, 138))], cap=2)
add_variants("Stone_SG_Block", [("Stone_SG_Block", 5), ("Stone_SG_Block_B", 3, (84, 88, 104))], cap=2)
add_variants("Stone_SG_Castle", [("Stone_SG_Castle", 5), ("Stone_SG_Castle_B", 3, (70, 74, 94))], cap=2)
add_variants("Grass_SG", [("Grass_SG", 6), ("Grass_SG_B", 4, (40, 62, 58))], cap=2)

# prefixos de dono (export Roblox): SG_<Zona>_<Coisa>
OWNER_PREFIX = {"terrain": ("SG_Ter_", "SG_Sky_"), "entry": ("SG_Ent_",), "village": ("SG_Vil_",),
                "castle": ("SG_Cas_",), "hall": ("SG_Hall_",), "summon": ("SG_Sum_",), "craft": ("SG_Craft_",),
                "dungeon": ("SG_Dun_",), "water": ("SG_Water_",), "exit": ("SG_Exit_",),
                "gate_ds": ("GATE_DemonSlayer",), "props": ("SG_Prop_",), "vegetation": ("SG_Veg_",),
                "vfx": ("VFX_",)}


# ------------------------------------------------------------------ cena
def reset_scene():
    fm_lib.COLS = COLS
    fm_lib.reset_scene()
    fm_lib._COL_COUNT.clear()


def mk(name, loc, rot=(0, 0, 0), size=2.0, kind="PLAIN_AXES", props=None, c="14_GAMEPLAY_MARKERS"):
    return fm_lib.marker(name, loc, rot, size, kind, c, props)


# ------------------------------------------------------------------ poligonos da planta
def rim():
    return ccw(L.ISLAND_RIM)


def floor_poly(name):
    for nm, poly, z, pr in L.floors():
        if nm == name:
            return ccw(poly)
    raise KeyError(name)


def ground_z(x, y):
    return L.zone_of(x, y)


# ------------------------------------------------------------------ escadas / guardas SO VISUAIS (colisao: sg_col)
def vis_stairs(mb, base, ang, width, n, rise, tread, m="Stone_Paving_SG", side_m="Stone_SG_Block", stringers=True):
    """escada visual (fm_parts.stairs com col=False): sobe na direcao ang (rad) a partir do pe (x, y, z)"""
    return FP.stairs(mb, "Vis", base, ang, width, n, rise=rise, tread=tread, m=m, side_m=side_m,
                     stringers=stringers, col=False)


def plan_stair(mb, name, m="Stone_Paving_SG", side_m="Stone_SG_Block", stringers=True):
    """a escada 'name' da planta (sg_layout.STAIRS) so no visual, casando com a colisao do sg_col"""
    foot, deg, w, n, tread, g = L.stair_frame(name)
    rise = (L.STAIR_TOP_Z[name] - foot[2]) / n
    return vis_stairs(mb, foot, math.radians(deg), w, n, rise, tread, m, side_m, stringers)


def vis_fence(mb, pts, h=3.0, post_step=4.0, m="Metal_SG_Iron", rail_m="Metal_SG_Iron", rope=False):
    return FP.fence(mb, "Vis", pts, h=h, post_step=post_step, m=m, rail_m=rail_m, col=False, rope=rope)


def vis_parapet(mb, pts, h=2.0, w=1.2, m="Stone_SG_Block", cap_m="Stone_SG_Trim"):
    return FP.stone_parapet(mb, "Vis", pts, h=h, w=w, m=m, cap_m=cap_m, col=False)


# ------------------------------------------------------------------ referencia de escala
def dummy(name, x, y, z, ang=0.0, visible=True):
    """boneco R15 de 5,2 studs (mesma convencao do lobby e das Ilhas 1 e 2)"""
    mb = MB(name, "_SCALE_REFERENCE")
    F = Frame(x, y, z, ang)
    for dx, dz, sx, sz in ((-0.5, 1.0, 0.9, 2.0), (0.5, 1.0, 0.9, 2.0), (0, 3.0, 2.0, 2.0), (-1.5, 3.0, 0.9, 2.0),
                           (1.5, 3.0, 0.9, 2.0)):
        mb.box((sx, 0.9 if sx < 2 else 1.0, sz), F.p(dx, 0, dz), F.r(), "Dummy_Grey", 0.08)
    mb.box((1.15, 1.15, 1.15), F.p(0, 0, 4.6), F.r(), "Dummy_Grey", 0.25)
    ob = mb.finish()
    ob.hide_render = not visible
    return ob


# ------------------------------------------------------------------ geometria comum
def ray_poly(poly, ang_deg, cx=0.0, cy=0.0):
    """maior distancia do centro ate o contorno 'poly' na direcao ang"""
    a = math.radians(ang_deg)
    dx, dy = math.cos(a), math.sin(a)
    best = 0.0
    n = len(poly)
    for i in range(n):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        ex, ey = x1 - x0, y1 - y0
        den = dx * ey - dy * ex
        if abs(den) < 1e-9:
            continue
        t = ((x0 - cx) * ey - (y0 - cy) * ex) / den
        u = ((x0 - cx) * dy - (y0 - cy) * dx) / den
        if t > 0 and -1e-6 <= u <= 1 + 1e-6:
            best = max(best, t)
    return best


def dome(mb, c, r, z0, m, n=18, rings=6, squash=1.0, open_bottom=True):
    """hemisferio (cupula) de raio r assentado em z0 (centro c = (x, y))"""
    bm = mb.bm
    cx, cy = c
    rows = []
    for k in range(rings):
        phi = (math.pi / 2) * k / rings
        rr = r * math.cos(phi)
        zz = z0 + r * math.sin(phi) * squash
        rows.append([bm.verts.new((cx + rr * math.cos(2 * math.pi * i / n), cy + rr * math.sin(2 * math.pi * i / n), zz))
                     for i in range(n)])
    top = bm.verts.new((cx, cy, z0 + r * squash))
    for r0, r1 in zip(rows, rows[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
    last = rows[-1]
    for i in range(n):
        bm.faces.new((last[i], last[(i + 1) % n], top))
    if not open_bottom:
        bm.faces.new(list(reversed(rows[0])))
    mb._post([v for rr in rows for v in rr] + [top], m, None, 0, 1)


def spire(mb, c, r, z0, h, m, n=8):
    """agulha conica (telhado de torre gotica) de base n-gonal"""
    bm = mb.bm
    cx, cy = c
    ring = [bm.verts.new((cx + r * math.cos(2 * math.pi * i / n + math.pi / n),
                          cy + r * math.sin(2 * math.pi * i / n + math.pi / n), z0)) for i in range(n)]
    top = bm.verts.new((cx, cy, z0 + h))
    for i in range(n):
        bm.faces.new((ring[i], ring[(i + 1) % n], top))
    bm.faces.new(list(reversed(ring)))
    mb._post(ring + [top], m, None, 0, 1)


def blob_poly(x, y, r, n=12, rng=None, amp=0.18, rot=0.0):
    """contorno irregular (pegada de rocha) em volta de (x, y)"""
    import random
    rng = rng or random.Random(int(x * 13 + y * 7) & 0xffff)
    return [(x + r * (1.0 + rng.uniform(-amp, amp)) * math.cos(rot + 2 * math.pi * i / n),
             y + r * (1.0 + rng.uniform(-amp, amp)) * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def ngon_col(area, cx, cy, n, R, z0, z1, rot0=0.0):
    """poligono regular CHEIO (vertices em rot0 + k*360/n, raio R): n/2 faixas pelo centro. A uniao e o n-gono."""
    a = R * math.cos(math.pi / n)
    w = 2.0 * a * math.tan(math.pi / n) + 0.05
    for k in range(n // 2):
        ang = math.radians(rot0) + math.pi / n + k * 2.0 * math.pi / n
        col_box(area, (2.0 * a, w, z1 - z0), (cx, cy, (z0 + z1) / 2), (0, 0, ang))


def octo_col(area, x, y, r, z0, z1):
    ngon_col(area, x, y, 8, r, z0, z1)


def box_walls_col(area, rect, z0, z1, th, doors=()):
    """paredes de um recinto retangular (x0, y0, x1, y1 = FACE INTERNA) com espessura th para fora.
    doors: [(lado 'S'|'N'|'W'|'E', centro, largura, altura)] - vao aberto na parede (a verga acima fica)."""
    x0, y0, x1, y1 = rect
    sides = {"S": ((x0 - th, y0 - th), (x1 + th, y0)), "N": ((x0 - th, y1), (x1 + th, y1 + th)),
             "W": ((x0 - th, y0), (x0, y1)), "E": ((x1, y0), (x1 + th, y1))}
    for sd, ((a0, b0), (a1, b1)) in sides.items():
        ds = [d for d in doors if d[0] == sd]
        horiz = sd in ("S", "N")
        lo, hi = (a0, a1) if horiz else (b0, b1)
        cuts = sorted((c - w / 2, c + w / 2, h) for _, c, w, h in ds)
        cur = lo
        for c0, c1, h in cuts:
            if c0 > cur + 0.05:
                if horiz:
                    col_box2(area, (cur, b0, z0), (c0, b1, z1))
                else:
                    col_box2(area, (a0, cur, z0), (a1, c0, z1))
            if z0 + h < z1 - 0.05:                      # verga
                if horiz:
                    col_box2(area, (c0, b0, z0 + h), (c1, b1, z1))
                else:
                    col_box2(area, (a0, c0, z0 + h), (a1, c1, z1))
            cur = max(cur, c1)
        if hi > cur + 0.05:
            if horiz:
                col_box2(area, (cur, b0, z0), (hi, b1, z1))
            else:
                col_box2(area, (a0, cur, z0), (a1, hi, z1))
