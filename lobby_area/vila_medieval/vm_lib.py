# vm_lib - base do lobby VILA MEDIEVAL sobre o pipeline do lobby Vila-Forja (lobby_area/forja_mineradora/fm_lib.py,
# fm_parts.py, export_roblox.py, fm_pv3*.py: SO LEITURA, nada e editado la; aqui so se CONFIGURA e se acrescenta).
# - coloca o pipeline do lobby no sys.path (sem gravar __pycache__ nas pastas dos outros);
# - colecoes do lobby novo; paleta da vila (VMMATS: cores do Roblox SEM calibracao = a cor que o Studio recebe);
# - conversao Roblox <-> Blender (a planta do PLANO_VM e escrita em coordenadas ROBLOX: X leste, Z sul, Y cima);
# - primitivas de blockout (casa enxaimel, telhado de duas aguas, faixa de caminho) e boneco de escala.
import os, sys, math
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
LOBBY = os.path.join(ROOT, "lobby_area", "forja_mineradora")
for p in (LOBBY, HERE):
    if p in sys.path:
        sys.path.remove(p)
    sys.path.insert(0, p)
# ordem final: HERE, LOBBY (os vm_* tem prioridade)

import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import fm_lib
from fm_lib import MB, D, S, col_box, col_box2, col_ramp, light, camera, MATS, RBX_CAL
from fm_parts import Frame
import vm_layout as L

COLS = ["00_REFERENCE", "01_BLOCKOUT", "02_TERRAIN", "03_TOWN", "04_FORGE", "05_SERVICES", "06_PORTALS",
        "07_EXIT", "08_WATER", "09_VEGETATION", "11_LIGHTING", "12_VFX_HELPERS", "13_COLLISION",
        "15_GAMEPLAY_MARKERS", "_SCALE_REFERENCE"]
EXPORT_GROUPS = ["02_TERRAIN", "03_TOWN", "04_FORGE", "05_SERVICES", "06_PORTALS", "07_EXIT", "08_WATER",
                 "09_VEGETATION"]
fm_lib.COLS = COLS
fm_lib._FLOOR_LEVELS = tuple(sorted({L.Y_GRASS, L.Y_PAVE, L.Y_NORTH_GRASS, L.Y_NORTH, L.Y_SPAWN, L.Y_SHOP,
                                     L.Y_PORTAL}))

# ------------------------------------------------------------------ paleta da vila (SPEC: cor Roblox, sem textura)
# (cor_linear, rough, metal, emissao, cor_emissao, variacao). Nomes com o prefixo da familia do RBX_RULES do fm_lib
# (Roof / Plaster / Wood_ / Stone_ / Stone_Paving / Grass / Dirt / Leaf_ / Bark / Metal_ / Water) -> Enum.Material
# e sombra corretos sem regra nova. Nenhuma entra em RBX_CAL: a cor do Blender E a cor do Studio.
# Reboco NUNCA branco puro (bloom do dia do Roblox): creme 235,225,200 e no maximo isso.
VMMATS = {
    "Roof_VM_Terracotta":   (S(200, 110, 60), 0.75, 0.0, 0, None, 0.0),    # telha laranja (SPEC)
    "Roof_VM_Terracotta_B": (S(182, 96, 54), 0.75, 0.0, 0, None, 0.0),     # telha mais escura (variacao POR CASA)
    "Roof_VM_Ridge":        (S(150, 78, 44), 0.75, 0.0, 0, None, 0.0),     # cumeeira / beiral
    "Plaster_VM_Cream":     (S(235, 225, 200), 0.9, 0.0, 0, None, 0.0),    # reboco creme (SPEC, teto de valor)
    "Plaster_VM_Ochre":     (S(226, 208, 176), 0.9, 0.0, 0, None, 0.0),    # reboco ocre claro (por casa)
    "Plaster_VM_Peach":     (S(232, 210, 186), 0.9, 0.0, 0, None, 0.0),    # reboco pessego claro (por casa)
    "Wood_VM_Timber":       (S(74, 50, 36), 0.8, 0.0, 0, None, 0.0),       # vigas do enxaimel (marrom escuro)
    "Wood_VM_Plank":        (S(128, 88, 58), 0.8, 0.0, 0, None, 0.0),      # portas, tabuas, carroca
    # V2b (08/10): a validacao do V1 no Roblox mostrou a pedra FRIA/azulada (o ceu do Roblox ainda puxa para o azul);
    # a ref_01 tem pedra cinza QUENTE bege-acinzentada -> todos os tons de pedra/paralelepipedo foram esquentados aqui
    # (so numeros de cor; os tons do kit - Warm/Grey/Mortar/Cob - tambem moram aqui e vencem o setdefault do vm_kit)
    "Stone_VM_Base":        (S(150, 143, 132), 0.85, 0.0, 0, None, 0.0),   # pedra cinza quente (terreo, muretas)
    "Stone_VM_Dark":        (S(108, 102, 96), 0.85, 0.0, 0, None, 0.0),    # soco, capas, chamine da forja
    "Stone_VM_Trim":        (S(178, 170, 154), 0.85, 0.0, 0, None, 0.0),   # cantaria clara (quinas, escadas)
    "Stone_VM_Warm":        (S(160, 148, 130), 0.85, 0.0, 0, None, 0.0),   # kit: pedra bege-acinzentada (2o tom)
    "Stone_VM_Grey":        (S(140, 136, 128), 0.85, 0.0, 0, None, 0.0),   # kit: pedra cinza neutra-quente (3o tom)
    "Stone_VM_Mortar":      (S(72, 68, 66), 0.9, 0.0, 0, None, 0.0),       # kit: junta recuada + vidraca (escuro)
    "Stone_Paving_VM":      (S(186, 172, 148), 0.85, 0.0, 0, None, 0.0),   # paralelepipedo bege-cinza
    "Stone_Paving_VM_Edge": (S(152, 140, 122), 0.85, 0.0, 0, None, 0.0),   # meio-fio / anel do medalhao
    "Stone_Paving_VM_Cob":  (S(198, 180, 150), 0.85, 0.0, 0, None, 0.0),   # kit: paralelepipedo bege quente
    "Stone_Paving_VM_CobB": (S(174, 158, 132), 0.85, 0.0, 0, None, 0.0),   # kit: 2o tom
    "Stone_Paving_VM_Joint": (S(112, 100, 86), 0.9, 0.0, 0, None, 0.0),   # kit: areia/junta da rua
    "Metal_VM_Bronze":      (S(176, 138, 70), 0.4, 0.8, 0, None, 0.0),     # medalhao (picareta + bigorna)
    "Metal_VM_Iron":        (S(70, 70, 76), 0.5, 0.6, 0, None, 0.0),       # ferragens, bigorna, roda
    "Grass_VM":             (S(98, 168, 62), 0.9, 0.0, 0, None, 0.0),      # grama verde saturada
    "Grass_VM_Hill":        (S(112, 160, 72), 0.9, 0.0, 0, None, 0.0),     # colinas (um tom mais claro e frio)
    "Dirt_VM":              (S(150, 122, 88), 0.95, 0.0, 0, None, 0.0),    # terra batida (bordas, quintais)
    "Cliff_VM_Rock":        (S(134, 128, 122), 0.9, 0.0, 0, None, 0.0),    # rocha do plato (vira Slate; V2b: quente)
    "Cliff_VM_Far":         (S(150, 166, 192), 0.95, 0.0, 0, None, 0.0),   # montanhas distantes (perspectiva aerea)
    "Cliff_VM_FarSnow":     (S(226, 232, 240), 0.95, 0.0, 0, None, 0.0),   # neve das montanhas (nao branco puro)
    "Leaf_VM_Pine":         (S(46, 104, 60), 0.85, 0.0, 0, None, 0.0),     # pinheiro estilizado
    "Leaf_VM_Round":        (S(84, 150, 62), 0.85, 0.0, 0, None, 0.0),     # copa redonda
    "Bark_VM":              (S(96, 66, 44), 0.9, 0.0, 0, None, 0.0),
    "Water_VM":             (S(64, 150, 190), 0.1, 0.0, 0, None, 0.0),     # canal (opaco no Roblox)
    "Window_VM_Dark":       (S(54, 62, 80), 0.4, 0.0, 0, None, 0.0),      # vidraca de dia (escura, nao preta)
    "Cloth_VM_Red":         (S(176, 54, 44), 0.85, 0.0, 0, None, 0.0),     # estandartes / toldo da loja
    "Cloth_VM_Blue":        (S(56, 86, 150), 0.85, 0.0, 0, None, 0.0),     # toldo/estandarte do ranking
    "Forge_Glow_VM":        (S(255, 128, 40), 0.5, 0.0, 2.0, S(255, 120, 36), 0.0),   # boca da fornalha (Neon)
    # so previa / QA (fora do export)
    "QA_Envelope":          (S(255, 40, 200), 0.9, 0.0, 0.6, S(255, 40, 200), 0.0),
    "PREVIEW_Island1":      (S(150, 140, 120), 0.9, 0.0, 0, None, 0.0),
}
for k, v in VMMATS.items():
    MATS.setdefault(k, v)

# traducao Roblox dos nomes novos (o maior prefixo vence no fm_lib.rbx_rule)
_NEW_RULES = [("Forge_Glow_VM", "Neon", 0.0, False),
              ("Window_VM", "SmoothPlastic", 0.0, True),
              ("Cliff_VM_FarSnow", "Snow", 0.0, False),
              ("Cliff_VM", "Slate", 0.0, True),
              ("Stone_Paving_VM", "SmoothPlastic", 0.0, False),
              ("Water_VM", "SmoothPlastic", 0.0, False),
              ("Cloth_VM", "Fabric", 0.0, True)]
for r in reversed(_NEW_RULES):
    if r not in fm_lib.RBX_RULES:
        fm_lib.RBX_RULES.insert(0, r)
# blockout com materiais LISOS: sem textura de detalhe (a forma tem de ler sozinha; no Roblox nao ha textura)
for _p in ("Roof_VM", "Plaster_VM", "Wood_VM", "Stone_VM", "Stone_Paving_VM", "Grass_VM", "Dirt_VM", "Bark_VM",
           "Cliff_VM"):
    if (_p, None) not in fm_lib.TEX_RULES:
        fm_lib.TEX_RULES = ((_p, None),) + tuple(fm_lib.TEX_RULES)

# prefixos de dono (orcamento do export): VM_<Zona>_<Coisa>; PORTAL_ = portais aprovados (fm_pv3, so leitura)
OWNER_PREFIX = [("VM_Ter_", "terrain"), ("VM_Bg_", "backdrop"), ("VM_Town_", "town"), ("VM_House_", "houses"),
                ("VM_Frg_", "forge"), ("VM_Shop_", "services"), ("VM_Rank_", "services"), ("VM_Mail_", "services"),
                ("PORTAL_", "portals"), ("VM_Court_", "portals"), ("VM_Exit_", "exit"), ("VM_Water_", "water"),
                ("VM_Veg_", "vegetation")]


# ------------------------------------------------------------------ Roblox <-> Blender
def B(x, z, y=0.0):
    """ponto Roblox (X, Z[, Y]) -> Vector Blender (x, -z, y)"""
    return Vector((x, -z, y))


def B2(x, z):
    return (x, -z)


def R(v):
    """Vector Blender -> tupla Roblox (X, Y, Z)"""
    return (v[0], v[2], -v[1])


def yaw_b(fx, fz):
    """direcao Roblox (fx, fz) no plano -> angulo do Blender (rad, a partir de +X, anti-horario)"""
    return math.atan2(-fz, fx)


def face_frame(x, z, y, fx, fz):
    """Frame (fm_parts) com origem em (x, z, y) Roblox cujo +X local = direcao (fx, fz) Roblox"""
    return Frame(x, -z, y, yaw_b(fx, fz))


# ------------------------------------------------------------------ cena
def reset_scene():
    fm_lib.COLS = COLS
    fm_lib.reset_scene()
    fm_lib._COL_COUNT.clear()


def mk(name, rx, rz, ry, fx=0.0, fz=-1.0, props=None, size=2.0, kind="PLAIN_AXES"):
    """marcador de gameplay (vira Part invisivel em LOBBY_FORJA.GAMEPLAY_MARKERS): posicao ROBLOX + direcao para onde
    olha (fx, fz). Grava face_x/face_z/yaw_deg Roblox nas props (o lead le direto do Studio)."""
    p = dict(props or {})
    n = math.hypot(fx, fz) or 1.0
    p.setdefault("face_x", round(fx / n, 4))
    p.setdefault("face_z", round(fz / n, 4))
    p.setdefault("yaw_deg", round(math.degrees(math.atan2(-fx, -fz)), 2))   # yaw Roblox (0 = olha -Z)
    rot = (0.0, 0.0, yaw_b(fx, fz) + math.pi / 2)    # +Y local do empty = direcao do olhar (convencao dos NPC_)
    return fm_lib.marker(name, B(rx, rz, ry), rot, size, kind, "15_GAMEPLAY_MARKERS", p)


def qa_box(name, lo, hi):
    """volume de QA (Roblox lo/hi), SO no 00_REFERENCE: nunca exportado; o vm_qa confere que nada o invade"""
    a, b = B(lo[0], lo[2], lo[1]), B(hi[0], hi[2], hi[1])
    p0 = Vector((min(a.x, b.x), min(a.y, b.y), min(a.z, b.z)))
    p1 = Vector((max(a.x, b.x), max(a.y, b.y), max(a.z, b.z)))
    mb = MB(name, "00_REFERENCE", detail="far", floor=-999)
    mb.box2(p0, p1, "QA_Envelope", 0.0)
    ob = mb.finish()
    ob.display_type = "WIRE"
    ob.hide_render = True
    ob["qa_lo"] = tuple(lo)
    ob["qa_hi"] = tuple(hi)
    return ob


# ------------------------------------------------------------------ geometria 2D
def ccw(poly):
    a = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        a += x0 * y1 - x1 * y0
    return list(poly) if a > 0 else list(reversed(poly))


def bpoly(poly_r):
    """poligono Roblox [(X, Z)] -> poligono Blender anti-horario"""
    return ccw([(x, -z) for x, z in poly_r])


def circle_r(cx, cz, r, n=32, a0=0.0, a1=360.0):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n)]


def ribbon_r(pts, w):
    """faixa (poligono Roblox) de largura w em volta da polilinha pts (Roblox)"""
    left, right = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dz = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dz) or 1.0
        nx, nz = -dz / ln, dx / ln
        left.append((p[0] + nx * w / 2, p[1] + nz * w / 2))
        right.append((p[0] - nx * w / 2, p[1] - nz * w / 2))
    return left + list(reversed(right))


def sector_r(cx, cz, r0, r1, a0, a1, n=24):
    """setor de anel (Roblox), angulos em graus (atan2(dz, dx))"""
    outer = [(cx + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
              cz + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    inner = [(cx + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / n)),
              cz + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / n))) for i in range(n + 1)]
    return outer + inner


def clip_half(poly, a, b, c):
    """Sutherland-Hodgman: parte do poligono com a*x + b*z + c >= 0 (mesma rotina do ds_lib)"""
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


def clip_box(poly, x0=None, x1=None, z0=None, z1=None):
    """recorta o poligono (Roblox) pela caixa x0 <= x <= x1, z0 <= z <= z1 (None = sem limite)"""
    p = list(poly)
    if x0 is not None:
        p = clip_half(p, 1, 0, -x0)
    if x1 is not None and p:
        p = clip_half(p, -1, 0, x1)
    if z0 is not None and p:
        p = clip_half(p, 0, 1, -z0)
    if z1 is not None and p:
        p = clip_half(p, 0, -1, z1)
    return p


def in_poly(x, z, poly):
    return fm_lib.point_in_poly(x, z, poly)


def slab(mb, poly_r, y0, y1, m):
    """prisma vertical de um poligono Roblox entre as cotas Roblox y0..y1"""
    mb.prism(bpoly(poly_r), y0, y1, m)


def path_len(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


# ------------------------------------------------------------------ colisao (coordenadas Roblox)
def colr(area, lo, hi):
    """caixa de colisao alinhada (Roblox lo/hi = (X, Y, Z))"""
    a, b = B(lo[0], lo[2], lo[1]), B(hi[0], hi[2], hi[1])
    return col_box2(area, a, b)


def colr_rot(area, cx, cz, cy, sx, sz, sy, fx, fz):
    """caixa de colisao girada: centro Roblox, tamanho (ao longo de f, transversal, altura), f = eixo longo"""
    return col_box(area, (sx, sz, sy), B(cx, cz, cy), (0, 0, yaw_b(fx, fz)))


def col_poly_strips(area, poly_r, y_top, thick=3.0, step=8.0, holes=()):
    """piso de colisao de um poligono qualquer (Roblox) por faixas em X de largura 'step' (caixas alinhadas; a borda
    da faixa segue o poligono no X do meio). holes = [(x0, x1, z0, z1)] retangulos SEM piso (levada, poco da roda)."""
    xs0 = [p[0] for p in poly_r]
    lo, hi = min(xs0), max(xs0)
    br = set()
    x = lo
    while x < hi - 0.01:
        br.add(round(x, 4))
        x += step
    br.add(round(hi, 4))
    for h in holes:
        for e in (h[0], h[1]):
            if lo < e < hi:
                br.add(round(e, 4))
    br = sorted(br)
    n = 0
    for xa, xb in zip(br, br[1:]):
        if xb - xa < 0.05:
            continue
        xm = (xa + xb) / 2
        zs = []
        m = len(poly_r)
        for i in range(m):
            (ax, az), (bx, bz) = poly_r[i], poly_r[(i + 1) % m]
            if (ax <= xm < bx) or (bx <= xm < ax):
                t = (xm - ax) / (bx - ax)
                zs.append(az + (bz - az) * t)
        zs.sort()
        ivs = [(zs[k], zs[k + 1]) for k in range(0, len(zs) - 1, 2)]
        for h in holes:
            if h[0] <= xm <= h[1]:
                cut = []
                for a, b in ivs:
                    if b <= h[2] or a >= h[3]:
                        cut.append((a, b))
                        continue
                    if a < h[2]:
                        cut.append((a, h[2]))
                    if b > h[3]:
                        cut.append((h[3], b))
                ivs = cut
        for a, b in ivs:
            if b - a > 0.05:
                colr(area, (xa, y_top - thick, a), (xb, y_top, b))
                n += 1
    return n


# ------------------------------------------------------------------ primitivas de blockout
def roof_gable(mb, F, w, d, z_eave, pitch_deg, m_roof, m_ridge, over=1.2, thick=0.7, ridge_axis="x"):
    """telhado de duas aguas no Frame F (local: x em [-w/2, w/2], y em [-d/2, d/2]); ridge_axis = eixo local da
    cumeeira. Retorna a cota do topo da cumeeira (local z)."""
    if ridge_axis == "x":
        span, length = d, w
    else:
        span, length = w, d
    half = span / 2.0
    ang = math.radians(pitch_deg)
    rise = half * math.tan(ang)
    slope = (half + over) / math.cos(ang)
    for s in (-1, 1):
        # placa inclinada: do beiral (com aba 'over', abaixo do frechal) ate a cumeeira; centro no meio das duas pontas
        z_low = z_eave - over * math.tan(ang)
        czs = (z_low + z_eave + rise) / 2.0 + thick / 2.0
        off = s * (half + over) / 2.0
        if ridge_axis == "x":
            mb.box((length + 2 * over, slope, thick), F.p(0, off, czs), F.r(-s * ang, 0, 0), m_roof, 0.0)
        else:
            mb.box((slope, length + 2 * over, thick), F.p(off, 0, czs), F.r(0, s * ang, 0), m_roof, 0.0)
    top = z_eave + rise + thick * 0.6
    if ridge_axis == "x":
        mb.box((length + 2 * over + 0.4, 1.0, 1.0), F.p(0, 0, top), F.r(), m_ridge, 0.0)
    else:
        mb.box((1.0, length + 2 * over + 0.4, 1.0), F.p(0, 0, top), F.r(), m_ridge, 0.0)
    return z_eave + rise


def gable_tri(mb, F, span, z_base, rise, y_off, thick, m, axis="x"):
    """triangulo de oitao (parede) no Frame F. axis='x': triangulo no plano local y=y_off, base ao longo de x"""
    hw = span / 2.0
    pts = [(-hw, 0.0), (hw, 0.0), (0.0, rise)]
    vs = []
    for t in (-thick / 2, thick / 2):
        for a, b in pts:
            if axis == "x":
                vs.append(mb.bm.verts.new(F.p(a, y_off + t, z_base + b)))
            else:
                vs.append(mb.bm.verts.new(F.p(y_off + t, a, z_base + b)))
    f0, f1 = vs[:3], vs[3:]
    mb.bm.faces.new(f0)
    mb.bm.faces.new(list(reversed(f1)))
    for i in range(3):
        j = (i + 1) % 3
        mb.bm.faces.new((f0[j], f0[i], f1[i], f1[j]))
    mb._post(vs, m, 0.0, 0, 1)


def timber_face(mb, F, x0, x1, y, z0, z1, m, post=3.0, w=0.45, depth=0.35, diag=True, sgn=1):
    """estrutura de madeira aparente numa fachada local (plano y = y, normal +-y): frechais, montantes e X/diagonais"""
    yy = y + sgn * depth / 2.0
    L_ = x1 - x0
    mb.box((L_ + w, depth, w), F.p((x0 + x1) / 2, yy, z0 + w / 2), F.r(), m, 0.0)
    mb.box((L_ + w, depth, w), F.p((x0 + x1) / 2, yy, z1 - w / 2), F.r(), m, 0.0)
    n = max(1, int(round(L_ / post)))
    xs = [x0 + L_ * i / n for i in range(n + 1)]
    for x in xs:
        mb.box((w, depth, z1 - z0), F.p(x, yy, (z0 + z1) / 2), F.r(), m, 0.0)
    if diag:
        for i, (a, b) in enumerate(zip(xs, xs[1:])):
            if i % 2 == 0:
                for s in (-1, 1):
                    pa = F.p(a if s > 0 else b, yy, z0 + w)
                    pb = F.p(b if s > 0 else a, yy, z1 - w)
                    mb.beam(pa, pb, w * 0.8, depth, m, 0.0)


def house(name, spec, coll="03_TOWN", col_area="House"):
    """CASA ENXAIMEL de blockout (SPEC 'Kit da vila'): terreo de pedra, andar(es) de reboco creme em balanco com vigas
    escuras (montantes + X), telhado ingreme de telha laranja (2 aguas) com cumeeira, oitao de reboco, chamine de
    pedra, porta de madeira e janelas. spec: dict(x, z, fx, fz, w, d, floors, ground_h, floor_h, pitch, plaster,
    roof, ridge ('x' = cumeeira paralela a fachada | 'y' = oitao para a rua), chimney (+1/-1/0), dormer, y)."""
    import random
    rng = random.Random(abs(hash((round(spec["x"], 1), round(spec["z"], 1)))) & 0xffff)
    y0 = spec.get("y", L.Y_PAVE)
    F = face_frame(spec["x"], spec["z"], y0, spec["fx"], spec["fz"])
    # local: +X = olhar da fachada -> giramos para a fachada ficar em +y local: usamos Frame com o angulo do olhar
    # e chamamos a frente de y local = +d/2 via um segundo Frame rodado de -90
    F = Frame(F.o.x, F.o.y, F.o.z, F.a - math.pi / 2)        # agora +y local = para onde a casa olha
    w, d = spec["w"], spec["d"]
    gh, fh, nf = spec.get("ground_h", 7.0), spec.get("floor_h", 6.0), spec.get("floors", 2)
    jet = spec.get("jetty", 0.8)
    pl = spec.get("plaster", "Plaster_VM_Cream")
    rf = spec.get("roof", "Roof_VM_Terracotta")
    mb = MB(name, coll, rng, detail="far", floor=y0)
    # soco escuro + terreo de pedra
    mb.box((w + 0.6, d + 0.6, 0.8), F.p(0, 0, 0.4), F.r(), "Stone_VM_Dark", 0.0)
    mb.box((w, d, gh - 0.8), F.p(0, 0, 0.8 + (gh - 0.8) / 2), F.r(), "Stone_VM_Base", 0.0)
    # quinas de cantaria clara (leem como pedra arredondada a distancia)
    for sx in (-1, 1):
        for sy in (-1, 1):
            for k in range(3):
                zc = 1.4 + k * (gh - 1.6) / 3.0
                mb.box((1.3, 1.3, (gh - 1.6) / 3.0 - 0.25), F.p(sx * (w / 2 - 0.45), sy * (d / 2 - 0.45), zc + (gh - 1.6) / 6.0),
                       F.r(), "Stone_VM_Trim", 0.0)
    # porta (frente = +y) e janelas do terreo
    mb.box((4.0, 0.5, 6.4), F.p(spec.get("door_x", 0.0), d / 2 + 0.05, 0.8 + 3.2), F.r(), "Wood_VM_Plank", 0.0)
    mb.box((5.0, 0.6, 0.6), F.p(spec.get("door_x", 0.0), d / 2 + 0.1, 0.8 + 6.7), F.r(), "Wood_VM_Timber", 0.0)
    # andares de reboco em balanco
    zb = gh
    W, Dd = w + 2 * jet, d + 2 * jet
    for i in range(nf - 1):
        mb.box((W, Dd, fh), F.p(0, 0, zb + fh / 2), F.r(), pl, 0.0)
        # vigas nas 4 fachadas
        timber_face(mb, F, -W / 2, W / 2, Dd / 2, zb, zb + fh, "Wood_VM_Timber", post=3.0, sgn=1)
        timber_face(mb, F, -W / 2, W / 2, -Dd / 2, zb, zb + fh, "Wood_VM_Timber", post=3.0, sgn=-1)
        Fs = Frame(F.o.x, F.o.y, F.o.z, F.a + math.pi / 2)
        timber_face(mb, Fs, -Dd / 2, Dd / 2, W / 2, zb, zb + fh, "Wood_VM_Timber", post=3.0, sgn=1)
        timber_face(mb, Fs, -Dd / 2, Dd / 2, -W / 2, zb, zb + fh, "Wood_VM_Timber", post=3.0, sgn=-1)
        # janelas (2 a 3 na frente, 2 atras)
        nwin = 3 if W > 13 else 2
        for k in range(nwin):
            xw = -W / 2 + W * (k + 0.5) / nwin
            for sy in (1, -1):
                mb.box((1.6, 0.5, 2.3), F.p(xw, sy * (Dd / 2 + 0.2), zb + fh * 0.52), F.r(), "Window_VM_Dark", 0.0)
        zb += fh
        W, Dd = W + 2 * jet * (1 if i == 0 and nf > 2 else 0), Dd + 2 * jet * (1 if i == 0 and nf > 2 else 0)
    # telhado
    ridge = spec.get("ridge", "x")
    pitch = spec.get("pitch", 52.0)
    top = roof_gable(mb, F, W, Dd, zb, pitch, rf, "Roof_VM_Ridge", over=1.3, ridge_axis=ridge)
    span = Dd if ridge == "x" else W
    rise = span / 2 * math.tan(math.radians(pitch))
    if ridge == "x":
        for s in (-1, 1):
            gable_tri(mb, Frame(F.o.x, F.o.y, F.o.z, F.a + math.pi / 2), Dd, zb, rise, s * W / 2, 0.6, pl, axis="x")
    else:
        for s in (-1, 1):
            gable_tri(mb, F, W, zb, rise, s * Dd / 2, 0.6, pl, axis="x")
            # vigas no oitao (le como enxaimel ate a cumeeira)
            yy = s * (Dd / 2 + 0.2)
            mb.box((0.45, 0.35, rise * 0.92), F.p(0, yy, zb + rise * 0.46), F.r(), "Wood_VM_Timber", 0.0)
            for sx in (-1, 1):
                mb.beam(F.p(sx * W / 2 * 0.9, yy, zb + 0.3), F.p(0, yy, zb + rise * 0.9), 0.4, 0.35, "Wood_VM_Timber", 0.0)
    # chamine de pedra
    ch = spec.get("chimney", 1)
    if ch:
        cx = ch * (W / 2 - 2.2) if ridge == "x" else ch * 1.6
        cy = -Dd / 4 if ridge == "x" else ch * (Dd / 2 - 2.2)
        mb.box((2.0, 2.0, rise + 2.2), F.p(cx, cy, zb + (rise + 2.2) / 2), F.r(), "Stone_VM_Base", 0.0)
        mb.box((2.5, 2.5, 0.5), F.p(cx, cy, zb + rise + 2.4), F.r(), "Stone_VM_Dark", 0.0)
    # agua-furtada na frente (le no perfil do telhado)
    if spec.get("dormer") and ridge == "x":
        zz = zb + rise * 0.25
        mb.box((3.6, 3.0, 3.4), F.p(0, Dd / 2 - 1.2 - rise * 0.25 / math.tan(math.radians(pitch)), zz + 1.7), F.r(), pl, 0.0)
        mb.box((2.0, 0.4, 2.0), F.p(0, Dd / 2 - rise * 0.25 / math.tan(math.radians(pitch)) + 0.35, zz + 1.8), F.r(),
               "Window_VM_Dark", 0.0)
        Fd = Frame(*F.p(0, Dd / 2 - 1.2 - rise * 0.25 / math.tan(math.radians(pitch)), 0)[:2], F.o.z, F.a + math.pi / 2)
        roof_gable(mb, Fd, 3.6, 4.2, zz + 3.4, 50.0, rf, "Roof_VM_Ridge", over=0.5, thick=0.5, ridge_axis="x")
    ob = mb.finish()
    # colisao: o volume inteiro (terreo + andares em balanco ate o beiral) - fachada fechada, nao entravel
    c = F.p(0, 0, 0)
    col_box(col_area, (w + 2 * jet + 0.2, d + 2 * jet + 0.2, zb + 2.0), (c.x, c.y, y0 + (zb + 2.0) / 2 - 1.0), F.r())
    return ob, y0 + top


def tree_round(mb, x, z, y, h, rng, leaf="Leaf_VM_Round"):
    Fp = B(x, z, y)
    tr = max(0.6, h * 0.07)
    mb.cyl(tr, h * 0.45, (Fp.x, Fp.y, y + h * 0.225), (0, 0, 0), "Bark_VM", 6, r2=tr * 0.75, bevel=0.0)
    r = h * 0.3
    mb.ico(r, (Fp.x, Fp.y, y + h * 0.62), leaf, 1, (1.0, 1.0, 0.85), jitter=0.12)
    mb.ico(r * 0.72, (Fp.x + r * 0.45, Fp.y + r * 0.2, y + h * 0.5), leaf, 1, (1.0, 1.0, 0.85), jitter=0.12)
    mb.ico(r * 0.7, (Fp.x - r * 0.4, Fp.y - r * 0.3, y + h * 0.52), leaf, 1, (1.0, 1.0, 0.85), jitter=0.12)


def tree_pine(mb, x, z, y, h, rng, leaf="Leaf_VM_Pine"):
    Fp = B(x, z, y)
    tr = max(0.5, h * 0.05)
    mb.cyl(tr, h * 0.3, (Fp.x, Fp.y, y + h * 0.15), (0, 0, 0), "Bark_VM", 6, bevel=0.0)
    for k, (f0, f1, rr) in enumerate(((0.18, 0.55, 0.30), (0.40, 0.78, 0.24), (0.62, 1.0, 0.17))):
        mb.cyl(h * rr, h * (f1 - f0), (Fp.x, Fp.y, y + h * (f0 + f1) / 2), (0, 0, rng.uniform(0, 1)), leaf, 7,
               r2=h * 0.02, bevel=0.0)


def dummy(name, rx, rz, ry, fx=0.0, fz=-1.0, visible=True):
    """boneco R15 de 5,2 studs (mesma convencao do lobby e das ilhas), olhando (fx, fz) Roblox"""
    mb = MB(name, "_SCALE_REFERENCE")
    F = face_frame(rx, rz, ry, fx, fz)
    F = Frame(F.o.x, F.o.y, F.o.z, F.a - math.pi / 2)
    for dx, dz, sx, sz in ((-0.5, 1.0, 0.9, 2.0), (0.5, 1.0, 0.9, 2.0), (0, 3.0, 2.0, 2.0), (-1.5, 3.0, 0.9, 2.0),
                           (1.5, 3.0, 0.9, 2.0)):
        mb.box((sx, 0.9 if sx < 2 else 1.0, sz), F.p(dx, 0, dz), F.r(), "Dummy_Grey", 0.08)
    mb.box((1.15, 1.15, 1.15), F.p(0, 0, 4.6), F.r(), "Dummy_Grey", 0.25)
    ob = mb.finish()
    ob.hide_render = not visible
    return ob
