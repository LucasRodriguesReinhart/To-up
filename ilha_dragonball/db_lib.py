# db_lib - base da Ilha 2 (Dragon Ball) sobre o pipeline do lobby (lobby_area/forja_mineradora/fm_lib.py) e os
# helpers genericos da Ilha 1 (ilha_naruto/il_lib.py: poligonos, colisao por poligono/anel, marcadores).
# Aqui: colecoes da ilha 2, paleta DRAGON BALL (DMATS), traducao Roblox dos prefixos novos, niveis de piso e helpers
# de escada/guarda SO VISUAIS (a colisao de tudo que e andavel e do db_col, congelado).
# COMPARTILHADO E CONGELADO (dono: integracao). Agentes de zona NAO editam.
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
NARUTO = os.path.normpath(os.path.join(HERE, "..", "ilha_naruto"))
LOBBY = os.path.normpath(os.path.join(HERE, "..", "lobby_area", "forja_mineradora"))
for p in (LOBBY, NARUTO, HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
# ordem final do sys.path: HERE, NARUTO, LOBBY  (os db_* tem prioridade)

import bpy
from mathutils import Vector
import fm_lib
from fm_lib import MB, D, S, col_box, col_box2, col_ramp, light, camera, add_variants, MATS, RBX_CAL
import il_lib as IL                   # helpers genericos + paleta Konoha (reuso de Stone_*, Metal_Gold, DB_Energy_Glow...)
from il_lib import (ccw, clip, area, arc_pts, x_intervals, ribbon_poly, col_poly, col_annulus, prism, annulus,
                    yaw_to)
import fm_parts as FP
from fm_parts import Frame
import db_layout as L

COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_MINING_ZONE", "04_CAPSULE_LANDMARK", "05_TECH_VILLAGE",
        "06_SUMMON", "07_WATER", "08_NEXT_ISLAND", "08_PURCHASE_GATES", "09_PROPS", "10_VEGETATION", "11_LIGHTING",
        "12_VFX_HELPERS", "13_COLLISION", "14_GAMEPLAY_MARKERS", "15_EXPORT", "_SCALE_REFERENCE"]
fm_lib.COLS = COLS
IL.COLS = COLS
# pisos da planta (detail="far" apoia o fundo das pecas nestes niveis)
fm_lib._FLOOR_LEVELS = tuple(sorted(set(L.LEVELS)))

# ------------------------------------------------------------------ traducao Roblox dos prefixos novos
# (prefixo, Enum.Material, transparencia, CastShadow) - entram NA FRENTE das regras do lobby
_NEW_RULES = [("Sand_", "Sand", 0.0, False), ("Glass_DB", "Glass", 0.35, False)]
for r in reversed(_NEW_RULES):
    if r not in fm_lib.RBX_RULES:
        fm_lib.RBX_RULES.insert(0, r)

# ------------------------------------------------------------------ paleta DRAGON BALL (lida na concept aprovada)
# nomes com os PREFIXOS do lobby -> herdam textura de detalhe (TEX_RULES) e Enum.Material (RBX_RULES).
# (cor_linear, rough, metal, emissao, cor_emissao, variacao)
DMATS = {
    # terreno quente
    "Sand_DB":              (S(226, 178, 118), 0.95, 0.0, 0, None, 0.14),   # areia da arena / trilhas
    "Cliff_Rock_DB":        (S(198, 118, 70), 0.9, 0.0, 0, None, 0.14),     # arenito laranja (penhascos, mesas)
    "Cliff_Rock_DB_Dark":   (S(132, 74, 48), 0.9, 0.0, 0, None, 0.12),      # estratos escuros / sombra
    "Cliff_Rock_DB_Top":    (S(226, 170, 116), 0.9, 0.0, 0, None, 0.10),    # borda de topo iluminada
    "Cliff_Rock_DB_Dusk":   (S(104, 84, 112), 0.9, 0.0, 0, None, 0.10),     # transicao Shadow Garden (saida)
    "Grass_DB":             (S(108, 182, 64), 0.9, 0.0, 0, None, 0.18),     # verde tropical vivo (controlado)
    "Dirt_DB":              (S(176, 120, 78), 0.95, 0.0, 0, None, 0.14),    # terra dos canteiros
    # construido
    "Stone_Paving_DB":      (S(236, 226, 206), 0.85, 0.0, 0, None, 0.14),   # calcamento claro (promenade, pracas)
    "Stone_DB_Block":       (S(214, 188, 150), 0.85, 0.0, 0, None, 0.14),   # muros de arrimo em blocos de arenito
    "Stone_DB_Dusk":        (S(120, 108, 132), 0.85, 0.0, 0, None, 0.10),   # calcamento/pedra da transicao SG
    "Plaster_DB_White":     (S(244, 245, 248), 0.6, 0.0, 0, None, 0.04),    # branco Capsule
    "Plaster_DB_Navy":      (S(30, 42, 88), 0.6, 0.0, 0, None, 0.04),       # azul-marinho (pilares, frisos)
    "Roof_DB_Blue":         (S(46, 104, 196), 0.55, 0.0, 0, None, 0.06),    # azul Capsule (cupulas, faixas)
    "Roof_DB_Orange":       (S(226, 112, 44), 0.65, 0.0, 0, None, 0.08),    # telhado marcial laranja
    "Metal_DB_Steel":       (S(176, 184, 196), 0.35, 0.8, 0, None, 0.04),   # estrutura tecnica
    "Metal_DB_Dark":        (S(62, 68, 82), 0.45, 0.7, 0, None, 0.04),      # trims escuros tecnicos
    "Glass_DB_Blue":        (S(110, 186, 236), 0.08, 0.0, 0.25, S(90, 170, 230), 0.0),   # vidro azul (Glass no Roblox)
    # energia (Neon no Roblox): azul-ciano Capsule; laranja DB ja existe (DB_Energy_Glow)
    "DB_Cyan_Glow":         (S(90, 214, 255), 0.3, 0.0, 3.0, S(90, 214, 255), 0.0),
    "DB_Ball_Glow":         (S(255, 150, 20), 0.3, 0.0, 2.2, S(255, 140, 20), 0.0),   # esferas do dragao (acento)
    "DB_Star_Red":          (S(200, 24, 24), 0.4, 0.0, 0, None, 0.0),                 # estrelas das esferas
    "Water_DB":             (S(56, 170, 226), 0.1, 0.0, 0.1, S(56, 170, 226), 0.0),
}
for k, v in DMATS.items():
    MATS.setdefault(k, v)
for k in ("DB_Cyan_Glow", "DB_Ball_Glow"):
    RBX_CAL.setdefault(k, (None, [int(c) for c in fm_lib.to_srgb(DMATS[k][0])]))
add_variants("Sand_DB", [("Sand_DB", 6), ("Sand_DB_B", 4, (214, 164, 104))], cap=2)
add_variants("Cliff_Rock_DB", [("Cliff_Rock_DB", 5), ("Cliff_Rock_DB_B", 3, (214, 138, 84)),
                               ("Cliff_Rock_DB_C", 2, (176, 102, 62))], cap=2)
add_variants("Stone_Paving_DB", [("Stone_Paving_DB", 5), ("Stone_Paving_DB_B", 3, (222, 210, 188))], cap=2)
add_variants("Stone_DB_Block", [("Stone_DB_Block", 5), ("Stone_DB_Block_B", 3, (200, 172, 134))], cap=2)
add_variants("Grass_DB", [("Grass_DB", 6), ("Grass_DB_B", 4, (92, 164, 58))], cap=2)

# prefixos de dono (export Roblox): DB_<Zona>_<Coisa>
OWNER_PREFIX = {"terrain": ("DB_Ter_", "DB_Sky_"), "mining": ("DB_Mine_",), "entrance": ("DB_Ent_",),
                "capsule": ("DB_Cap_",), "village": ("DB_Hub_", "DB_Twr_"), "summon": ("DB_Sum_",),
                "water": ("DB_Water_",), "exit": ("DB_Exit_",), "gate_sg": ("GATE_ShadowGarden",),
                "props": ("DB_Prop_",), "vegetation": ("DB_Veg_",), "vfx": ("VFX_",)}


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


def arena():
    return ccw(L.arena_poly(3.0))


def prom_outer():
    return ccw(L.prom_poly(3.0))


def summon_poly():
    return ccw(L.summon_poly(5.0))


def hub_poly():
    return ccw(L.HUB_POLY)


def cap_poly():
    return ccw(L.CAP_POLY)


def exit_shelf_polys():
    return [ribbon_poly(L.EXIT_PATH, L.EXIT_PATH_HW), ribbon_poly(L.HUB_EXIT_LINK, L.HUB_EXIT_LINK_HW)]


def ground_z(x, y):
    return L.zone_of(x, y)


# ------------------------------------------------------------------ escadas / guardas SO VISUAIS (colisao: db_col)
def vis_stairs(mb, base, ang, width, n, rise, tread, m="Stone_Paving_DB", side_m="Stone_DB_Block", stringers=True):
    """escada visual (fm_parts.stairs com col=False): sobe na direcao ang (rad) a partir do pe (x, y, z)"""
    return FP.stairs(mb, "Vis", base, ang, width, n, rise=rise, tread=tread, m=m, side_m=side_m,
                     stringers=stringers, col=False)


def vis_fence(mb, pts, h=3.0, post_step=4.0, m="Wood_Dark", rail_m="Wood_Plank", rope=False):
    return FP.fence(mb, "Vis", pts, h=h, post_step=post_step, m=m, rail_m=rail_m, col=False, rope=rope)


def vis_parapet(mb, pts, h=2.0, w=1.2, m="Stone_DB_Block", cap_m="Stone_Paving_DB"):
    return FP.stone_parapet(mb, "Vis", pts, h=h, w=w, m=m, cap_m=cap_m, col=False)


# ------------------------------------------------------------------ referencia de escala
def dummy(name, x, y, z, ang=0.0, visible=True):
    """boneco R15 de 5,2 studs (mesma convencao do lobby e da Ilha 1)"""
    mb = MB(name, "_SCALE_REFERENCE")
    F = Frame(x, y, z, ang)
    for dx, dz, sx, sz in ((-0.5, 1.0, 0.9, 2.0), (0.5, 1.0, 0.9, 2.0), (0, 3.0, 2.0, 2.0), (-1.5, 3.0, 0.9, 2.0),
                           (1.5, 3.0, 0.9, 2.0)):
        mb.box((sx, 0.9 if sx < 2 else 1.0, sz), F.p(dx, 0, dz), F.r(), "Dummy_Grey", 0.08)
    mb.box((1.15, 1.15, 1.15), F.p(0, 0, 4.6), F.r(), "Dummy_Grey", 0.25)
    ob = mb.finish()
    ob.hide_render = not visible
    return ob


# ------------------------------------------------------------------ geometria comum (planta estrelada a partir da origem)
def ray_poly(poly, ang_deg, cx=0.0, cy=0.0):
    """maior distancia do centro ate o contorno 'poly' na direcao ang (poligono estrelado em relacao ao centro)"""
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


def rim_r(ang_deg):
    return ray_poly(L.ISLAND_RIM, ang_deg)


def ring_band(mb, inner_fn, outer_fn, z0, z1, m, step=3.0, wall_m=None, walls=(True, True), a0=0.0, a1=360.0):
    """faixa entre dois contornos polares (r_in(ang), r_out(ang)) com tampo em z1 e paredes internas/externas de z0
    a z1. Fechada quando a0..a1 = 0..360."""
    wall_m = wall_m or m
    closed = abs((a1 - a0) - 360.0) < 1e-6
    n = max(3, int(round((a1 - a0) / step)))
    angs = [a0 + (a1 - a0) * i / n for i in range(n if closed else n + 1)]
    bm = mb.bm
    ti, to, bi, bo = [], [], [], []
    for a in angs:
        ri, ro = inner_fn(a), outer_fn(a)
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        ti.append(bm.verts.new((c * ri, s * ri, z1)))
        to.append(bm.verts.new((c * ro, s * ro, z1)))
        bi.append(bm.verts.new((c * ri, s * ri, z0)))
        bo.append(bm.verts.new((c * ro, s * ro, z0)))
    m_top, m_wall = [], []
    cnt = len(angs) if closed else len(angs) - 1
    for i in range(cnt):
        j = (i + 1) % len(angs)
        m_top.append(bm.faces.new((ti[i], to[i], to[j], ti[j])))
        if walls[0]:
            m_wall.append(bm.faces.new((ti[i], ti[j], bi[j], bi[i])))
        if walls[1]:
            m_wall.append(bm.faces.new((to[i], bo[i], bo[j], to[j])))
    verts = ti + to + bi + bo
    # materiais separados: tampo (todas as faces) e depois paredes (faces ligadas aos vertices de baixo)
    mb._post(ti + to, m, None, 0, 1)
    if m_wall:
        mb._post(bi + bo, wall_m, None, 0, 1)
    return verts


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


def blob_poly(x, y, r, n=12, rng=None, amp=0.18, rot=0.0):
    """contorno irregular (pegada de rocha) em volta de (x, y)"""
    import random
    rng = rng or random.Random(int(x * 13 + y * 7) & 0xffff)
    return [(x + r * (1.0 + rng.uniform(-amp, amp)) * math.cos(rot + 2 * math.pi * i / n),
             y + r * (1.0 + rng.uniform(-amp, amp)) * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]


def octo_col(area, x, y, r, z0, z1):
    """coluna de colisao octogonal (2 caixas quadradas a 0 e 45 graus)"""
    s = r * 1.66
    for a in (0.0, math.pi / 4):
        col_box(area, (s, s, z1 - z0), (x, y, (z0 + z1) / 2), (0, 0, a))
