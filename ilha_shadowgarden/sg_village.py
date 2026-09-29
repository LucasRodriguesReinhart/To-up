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
import math, random
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


def window(mb, f, s, zlo, w, h, head="arch", shutters=False, planter=False):
    """janela quente com caixilho escuro em cruz, peitoril de pedra, cabeca (arco ogival de madeira / verga de pedra)"""
    zc = zlo + h / 2
    f.box(mb, s, 0.02, zc, w, 0.3, h, WIN)                                   # vidro quente
    f.box(mb, s, 0.2, zlo + h + 0.12, w + 0.6, 0.2, 0.3, WOOD)                # caixilho: topo
    f.box(mb, s, 0.2, zlo - 0.05, w + 0.6, 0.2, 0.3, WOOD)                    # base
    for k in (-1, 1):
        f.box(mb, s + k * (w / 2 + 0.15), 0.2, zc, 0.3, 0.2, h + 0.3, WOOD)    # ombreiras
    f.box(mb, s, 0.22, zc, 0.22, 0.2, h, WOOD)                                # montante
    f.box(mb, s, 0.22, zlo + h * 0.62, w, 0.2, 0.22, WOOD)                    # travessa
    f.box(mb, s, 0.3, zlo - 0.3, w + 0.9, 0.55, 0.26, TRIM)                   # peitoril
    if head == "arch":
        f.beam(mb, s - w / 2 - 0.35, zlo + h + 0.2, s, zlo + h + 1.0, 0.2, 0.3, 0.36)
        f.beam(mb, s + w / 2 + 0.35, zlo + h + 0.2, s, zlo + h + 1.0, 0.2, 0.3, 0.36)
    elif head == "lintel":
        f.box(mb, s, 0.18, zlo + h + 0.5, w + 1.0, 0.45, 0.6, TRIM)
    if shutters:
        for k in (-1, 1):
            f.box(mb, s + k * (w * 0.75 + 0.45), 0.14, zc, w * 0.5, 0.22, h, M_SHUT)
    if planter:
        mb = LIFE[0] or mb      # detalhe de vida vai no objeto de vestir da vila (1 MeshPart por material, nao por grupo)
        # caixa de janela: pendurada sob o peitoril (2 maos-francesas de ferro), folhagem e flores violeta
        # dessaturadas subindo na frente do vidro (vida humana, nao enfeite: so nas janelas da frente)
        f.box(mb, s, 0.78, zlo - 0.72, w + 0.5, 0.62, 0.5, WOOD)
        f.box(mb, s, 0.8, zlo - 0.36, w + 0.3, 0.5, 0.3, "Leaf_SG_Pine")
        for k in (-1, 1):
            mb.beam(f.P(s + k * (w / 2 - 0.1), 0.05, zlo - 1.55), f.P(s + k * (w / 2 - 0.1), 0.95, zlo - 0.98), 0.14,
                    0.14, IRON, 0.0)
        nb = max(2, int((w + 0.3) / 0.62))
        for k in range(nb):
            u = -(w + 0.3) / 2 + (w + 0.3) * (k + 0.5) / nb
            mb.ico(0.27, tuple(f.P(s + u, 0.8 + (0.08 if k % 2 else -0.06), zlo - 0.16)), M_BLOOM, 1,
                   scale=(1.0, 1.0, 0.75))


def shopfront(mb, f, s, w=4.4):
    """vitrine de loja com persiana FECHADA: mais larga que alta, peitoril de balcao a 2,1 do chao (nunca le como porta),
    bandeira quente em cima e toldo de ardosia"""
    z0, z1 = 2.1, 4.3
    f.box(mb, s, 0.05, (z0 + z1) / 2, w, 0.3, z1 - z0, M_SHUT)                 # persiana fechada
    for i in range(4):
        f.box(mb, s, 0.22, z0 + 0.35 + i * 0.5, w, 0.14, 0.2, WOOD)            # ripas
    f.box(mb, s, 0.45, z0 - 0.15, w + 0.8, 0.9, 0.3, TRIM)                     # balcao de pedra
    f.box(mb, s, 0.25, z0 - 0.9, w + 0.4, 0.3, 1.2, TRIM)                      # almofada sob o balcao
    for k in (-1, 1):
        f.box(mb, s + k * (w / 2 + 0.25), 0.2, (z0 - 0.3 + z1 + 0.5) / 2, 0.5, 0.35, z1 - z0 + 0.8, WOOD)
    f.box(mb, s, 0.2, z1 + 0.25, w + 1.0, 0.4, 0.5, WOOD)                      # verga
    f.box(mb, s, 0.04, z1 + 0.95, w, 0.3, 0.8, WIN)                            # bandeira quente
    for k in (-1, 0, 1):
        f.box(mb, s + k * w / 3, 0.2, z1 + 0.95, 0.22, 0.2, 0.8, WOOD)
    f.box(mb, s, 0.2, z1 + 1.45, w + 1.0, 0.35, 0.3, WOOD)
    # toldo de ardosia inclinado
    t = math.radians(28.0)
    f.box(mb, s, 1.0, z1 + 1.75, w + 1.4, 2.1, 0.28, ROOF, rx=-t)
    for k in (-1, 1):
        f.beam(mb, s + k * (w / 2 + 0.3), z1 + 0.9, s + k * (w / 2 + 0.3), z1 + 1.6, 1.7, 0.22, 0.22, IRON)
        f.beam(mb, s + k * (w / 2 + 0.3), z1 + 0.9, s + k * (w / 2 + 0.3), z1 + 1.9, 0.3, 0.22, 0.22, IRON)


WL_S = 0.68                    # escala da lanterna de suporte (a mesma lanterna dourada da ordem, pequena)
LIFE = [None]                  # MB de vestir das casas (lanternas de suporte, caixas de janela): criado no build()


def wall_lantern(mb, f, s, za):
    """lanterna de suporte na fachada: espelho de ferro negro na parede, braco com mao-francesa e a lanterna dourada da
    ordem (sg_emblem.lantern_head, vidro Lantern_Glow - SO Neon) pendurada por uma haste. za = cota do braco (local)."""
    mb = LIFE[0] or mb
    f.box(mb, s, 0.12, za - 0.35, 0.5, 0.2, 1.1, BIRON)
    mb.beam(f.P(s, 0.1, za), f.P(s, 1.45, za), 0.16, 0.2, BIRON, 0.0)
    mb.beam(f.P(s, 0.1, za - 0.85), f.P(s, 0.95, za - 0.02), 0.12, 0.14, BIRON, 0.0)
    mb.box((0.26, 0.26, 0.14), f.P(s, 1.45, za + 0.1), (0, 0, f.yaw), EM.GOLD, 0.0)      # remate da ponta do braco
    top = za - 0.12
    c = f.P(s, 1.2, top - 0.2 - 2.05 * WL_S)
    mb.rod(f.P(s, 1.2, top), f.P(s, 1.2, top - 0.25), 0.05, BIRON, 4)
    EM.lantern_head(mb, mb, (c.x, c.y, c.z), f.yaw, WL_S)


def _lantern_slots(Lf, ss, ww, shutters, shop):
    """onde vao as lanternas de suporte numa fachada: nos vaos LIVRES entre janelas (contando as persianas), senao nas
    quinas (se couber); lojas: nas quinas, fora do toldo"""
    if shop:
        return [-(Lf / 2 - 0.95), Lf / 2 - 0.95]
    he = (ww + 0.45) if shutters else (ww / 2 + 0.3)
    ss = sorted(ss)
    gaps = [(a + b) / 2 for a, b in zip(ss, ss[1:]) if b - a - 2 * he >= 1.2]
    if gaps:
        return [gaps[0], gaps[-1]] if len(gaps) >= 2 else gaps
    edge = (max(abs(x) for x in ss) + he) if ss else 0.0
    if Lf / 2 - edge >= 1.2:
        return [-(edge + Lf / 2) / 2, (edge + Lf / 2) / 2]
    return []


def timber_face(mb, f, z0, z1, wins, rng):
    """estrutura aparente (so do lado de fora): soleira, frechal, montantes e escoras em chevron nos vaos cheios"""
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
            full.append(mid)
    full = sorted(full)
    for x in full:
        f.box(mb, x, 0.15, (z0 + z1) / 2, 0.42, 0.3, z1 - z0 - 0.3, WOOD)
    for a, b in zip(full, full[1:]):
        mid = (a + b) / 2
        if b - a < 1.0 or any(b0 < mid < b1 for b0, b1 in blocked):
            continue
        if mid < 0:
            f.beam(mb, a + 0.2, z0 + 0.45, b - 0.2, z1 - 0.45, 0.15, 0.3, 0.38)
        else:
            f.beam(mb, a + 0.2, z1 - 0.45, b - 0.2, z0 + 0.45, 0.15, 0.3, 0.38)


def win_slots(Lf, w, n=None, margin=1.6):
    n = n if n is not None else max(1, int((Lf - 2 * margin + 1.2) / (w + 2.4)))
    step = (Lf - 2 * margin) / n
    return [-Lf / 2 + margin + step * (k + 0.5) for k in range(n)]


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

    # base de pedra (sobe 1,0; afunda 0,4)
    mb.box((W + 0.7, D + 0.7, 1.4), G.p(0, 0, 0.3), G.r(), OBS, 0.12)
    zc = 1.0
    body = (wx0, wx1, wy0, wy1)
    top_b = body
    for si, (kind, h) in enumerate(stories):
        b = body
        if si > 0 and jet > 0:
            x0, x1, y0, y1 = body
            if gable_front:
                b = (x0, x1 + jet, y0, y1)
            else:
                b = (x0, x1, y0 - jet * 0.6, y1 + jet)
            # banda do piso em balanco + misulas sob o balanco da frente
            bx0, bx1, by0, by1 = b
            mb.box((bx1 - bx0 + 0.3, by1 - by0 + 0.3, 0.5), G.p((bx0 + bx1) / 2, (by0 + by1) / 2, zc + 0.05), G.r(),
                   WOOD, 0.0)
            ff = faces(body)[front]
            for s in win_slots(ff.L, 0.4, n=int(ff.L / 2.4), margin=0.8):
                ff.box(mb, s, jet / 2, zc - 0.45, 0.4, jet, 0.8, WOOD)
        x0, x1, y0, y1 = b
        mat = STONE_H if kind == "stone" else M_PL
        mb.box((x1 - x0, y1 - y0, h), G.p((x0 + x1) / 2, (y0 + y1) / 2, zc + h / 2), G.r(), mat, 0.0)
        fs = faces(b)
        for key, f in fs.items():
            is_front = key == front
            ww = 1.7 if kind == "timber" else 1.6
            wh = 2.4 if kind == "timber" else 2.5
            shop = spec.get("shop") and si == 0 and is_front
            if shop:
                slots = [(0.0, "shop")] + ([(-f.L / 2 + 2.4, "w"), (f.L / 2 - 2.4, "w")] if f.L >= 12.5 else [])
            elif is_front:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=spec.get("nwin", None))]
            else:
                slots = [(s, "w") for s in win_slots(f.L, ww, n=(1 if f.L < 11.0 else 2))]
            zl = zc + (1.9 if kind == "stone" else 1.5)
            if si == 0 and len(stories) == 1:
                zl = zc + 2.0
            wins = []
            for s, kd in slots:
                if kd == "shop":
                    shopfront(mb, f, s)
                    continue
                window(mb, f, s, zl, 1.4 if shop else ww, wh, head=("lintel" if kind == "stone" else "arch"),
                       shutters=(is_front and kind == "stone" and not shop),
                       planter=bool(is_front and spec.get("planter") and kind == "timber"))
                wins.append((s, ww))
            if kind == "timber":
                timber_face(mb, f, zc, zc + h, wins, rng)
            if si == 0 and is_front:
                # lanternas de suporte na fachada da rua (v3): ladeando a loja, ou nos vaos entre as janelas
                za = zc + min(h, 6.8) - 0.9
                tur_s = 0
                if spec.get("turret") and not gable_front and spec["turret"][1] > 0:
                    tur_s = spec["turret"][0]                                 # o torreao ocupa essa quina da frente
                for sl_ in _lantern_slots(f.L, [s for s, kd in slots if kd != "shop"], ww,
                                          is_front and kind == "stone" and not shop, shop):
                    if tur_s and sl_ * tur_s > 0 and abs(sl_) > f.L / 2 - 3.2:
                        continue
                    wall_lantern(mb, f, sl_, za)
        if kind == "stone" and si < len(stories) - 1:
            mb.box((x1 - x0 + 0.5, y1 - y0 + 0.5, 0.45), G.p((x0 + x1) / 2, (y0 + y1) / 2, zc + h - 0.2), G.r(),
                   TRIM, 0.0)                                                 # cordao de pedra
        if kind == "stone":
            # cunhais (pedra clara alternada nas quinas)
            pq, la, lb = 0.22, 1.5, 0.9
            for cx_, cy_ in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
                sgx, sgy = math.copysign(1, cx_), math.copysign(1, cy_)
                for k in range(int(h / 1.6)):
                    zz = zc + 0.8 + k * 1.6
                    ax, ay = (la, lb) if k % 2 == 0 else (lb, la)
                    mb.box((ax, ay, 0.8), G.p(cx_ - sgx * (ax / 2 - pq), cy_ - sgy * (ay / 2 - pq), zz), G.r(), STONE,
                           0.0)
        zc += h
        body = b
        top_b = b
    ze = zc
    # ---- telhado ingreme (cumeeira ao longo de x de G) sobre o ultimo pavimento
    x0, x1, y0, y1 = top_b
    cy = (y0 + y1) / 2
    hd = (y1 - y0) / 2
    oe, og, th = 1.0, 0.8, 0.6
    t = math.atan2(R, hd)
    Ls = (hd + oe) / math.cos(t)
    rows = max(4, int(Ls / 1.6))
    dl = math.radians(3.0)
    tr = t - dl
    for s in (-1, 1):
        # fiadas de ardosia: cada fiada um pouco menos inclinada -> a borda de baixo sobra sobre a seguinte (sombra)
        for k in range(rows):
            f0 = k / rows
            f1 = min(1.0, (k + 1.35) / rows)
            ay = cy + s * f0 * (hd + oe)
            az = ze + R - f0 * (R + oe * math.tan(t))
            lr = (f1 - f0) * Ls
            dy, dz = s * math.cos(tr), -math.sin(tr)
            ny, nz = s * math.sin(tr), math.cos(tr)
            thr = 0.5 if k else th
            mb.box((x1 - x0 + 2 * og, lr, thr), G.p((x0 + x1) / 2, ay + dy * lr / 2 + ny * thr / 2,
                                                    az + dz * lr / 2 + nz * thr / 2), G.r(-s * tr, 0, 0), ROOF, 0.0)
        # guarda-po (tabua escura na borda da empena)
        for xe in (x0 - og - 0.1, x1 + og + 0.1):
            mb.beam(G.p(xe, cy, ze + R + th), G.p(xe, cy + s * (hd + oe), ze - oe * math.tan(t) + th * 0.6), 0.28,
                    0.7, WOOD, 0.0)
    # beiral de madeira escura (v3): testeira ao longo da borda do telhado + cachorros (pontas de caibro) a cada ~2
    # sob o balanco, do frechal a testeira - a sombra do beiral e o que da escala de casa (e nao de caixa com telhado)
    ez = ze - oe * math.tan(t)
    for s in (-1, 1):
        mb.box((x1 - x0 + 2 * og, 0.3, 0.55), G.p((x0 + x1) / 2, cy + s * (hd + oe - 0.12), ez - 0.05), G.r(), WOOD,
               0.0)
        nr = max(3, int((x1 - x0) / 2.0))
        for k in range(nr + 1):
            xr = x0 + 0.35 + (x1 - x0 - 0.7) * k / nr
            mb.beam(G.p(xr, cy + s * (hd - 0.1), ze - 0.32), G.p(xr, cy + s * (hd + oe - 0.3), ez - 0.2), 0.26, 0.32,
                    WOOD, 0.0)
    rt = ze + R + th / math.cos(t)
    mb.box((x1 - x0 + 2 * og + 0.2, 0.75, 0.75), G.p((x0 + x1) / 2, cy, rt - 0.2), G.r(math.pi / 4, 0, 0), IRON, 0.0)
    for xe in (x0 - og + 0.2, x1 + og - 0.2):
        mb.cyl(0.3, 2.2, G.p(xe, cy, rt + 1.0), G.r(), IRON, n=4, r2=0.02, bevel=0.0)   # pinaculo de ferro
    # empenas (reboco + estrutura), janela de sotao
    for sx, key in ((1, "+x"), (-1, "-x")):
        f = Face(G, (x1 if sx > 0 else x0, cy), (0.0, -1.0) if sx > 0 else (0.0, 1.0), y1 - y0)
        nv = f.nvec()
        pts = [f.P(-hd, 0.0, ze), f.P(hd, 0.0, ze), f.P(0.0, 0.0, ze + R)]
        tri_slab(mb, pts, nv, 0.6, M_PL)
        f.box(mb, 0.0, 0.15, ze + 0.22, y1 - y0 + 0.3, 0.3, 0.44, WOOD)
        attic = (key == front) or spec.get("attic_all", False)
        zc_win = ze + 1.0
        if attic:
            window(mb, f, 0.0, zc_win, 1.3, 2.0, head="arch" if key == front else None)
            f.box(mb, 0.0, 0.15, (zc_win + 3.3 + ze + R - 0.6) / 2, 0.42, 0.3, ze + R - 0.6 - zc_win - 3.3, WOOD)
        else:
            f.box(mb, 0.0, 0.15, ze + R * 0.46, 0.42, 0.3, R * 0.9, WOOD)
        zcol = (ze + 4.4) if attic else (ze + R * 0.42)
        half = hd * (1 - (zcol - ze) / R) - 0.3
        f.box(mb, 0.0, 0.15, zcol, 2 * half, 0.3, 0.42, WOOD)                 # linha alta
        for k in (-1, 1):
            f.beam(mb, k * (hd - 0.5), ze + 0.4, k * max(0.5 * half, 1.7), zcol - 0.1, 0.15, 0.3, 0.36)
    # ---- aguas-furtadas
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
            mb.box((L2 + 0.2, ln, 0.32), G.p(xd + s2 * hw / 2, (yf + yb) / 2 + s * 0.3, zt + rr / 2 + 0.16),
                   G.r(0, s2 * t2, 0), ROOF, 0.0)
        fd = Face(G, (xd, yf), (s * 1.0, 0.0), wd)
        tri_slab(mb, [fd.P(-wd / 2, 0.0, zt), fd.P(wd / 2, 0.0, zt), fd.P(0.0, 0.0, zt + rr)], fd.nvec(), 0.4, WOOD)
        window(mb, fd, 0.0, zb + 0.5, 1.3, 1.8, head=None)
        mb.cyl(0.18, 1.2, G.p(xd, (yf + yb) / 2 + s * 0.8, zt + rr + 0.7), G.r(), IRON, n=4, r2=0.02, bevel=0.0)
    # ---- chamines (v3: 3 desenhos - 'stack' fuste simples, 'twin' fuste largo com 2 potes de ferro, 'hood' fuste com
    # chapeu de ardosia em 4 pes - e uma 2a chamine em algumas casas: a linha dos telhados deixa de ser repetida)
    chims = []
    if spec.get("chimney"):
        chims.append((spec["chimney"], spec.get("chim_kind", "stack"), spec.get("chim_h", 2.6)))
    if spec.get("chimney2"):
        chims.append((spec["chimney2"], spec.get("chim2_kind", "stack"), spec.get("chim2_h", 1.6)))
    for (cx_, cy_), kind, hx in chims:
        cx_ *= (x1 - x0) / 2
        cy_ = cy + cy_ * hd
        zz0 = ze - 0.5
        zz1 = ze + R + hx
        wx_ = 2.4 if kind == "twin" else 1.5
        mb.box((wx_, 1.5, zz1 - zz0), G.p(cx_, cy_, (zz0 + zz1) / 2), G.r(), STONE, 0.0)
        mb.box((wx_ + 0.3, 1.8, 0.3), G.p(cx_, cy_, zz1 - 1.1), G.r(), OBS, 0.0)            # cinta escura
        mb.box((wx_ + 0.5, 2.0, 0.4), G.p(cx_, cy_, zz1 + 0.2), G.r(), TRIM, 0.0)
        if kind == "twin":
            for k in (-1, 1):
                mb.cyl(0.36, 1.0, G.p(cx_ + k * 0.6, cy_, zz1 + 0.9), G.r(), IRON, n=8, r2=0.28, bevel=0.0)
        elif kind == "hood":
            for kx in (-1, 1):
                for ky in (-1, 1):
                    mb.box((0.22, 0.22, 0.9), G.p(cx_ + kx * 0.7, cy_ + ky * 0.7, zz1 + 0.85), G.r(), IRON, 0.0)
            mb.cyl(1.5, 0.75, G.p(cx_, cy_, zz1 + 1.65), G.r(0, 0, math.pi / 4), ROOF, n=4, r2=0.12, bevel=0.0)
        else:
            mb.box((0.7, 0.7, 0.8), G.p(cx_ - 0.3, cy_, zz1 + 0.8), G.r(), "Cliff_Rock_SG_Dark", 0.0)
    # ---- torreao (canto da frente)
    tur = spec.get("turret")
    if tur:
        sx, sy = tur
        tx, ty = (x0 if sx < 0 else x1) + sx * 0.6, (y1 + 0.6) if sy > 0 else (y0 - 0.6)
        wp = G.p(tx, ty, 0.0)
        r = 2.5
        zt0 = z - 0.4
        zt1 = z + ze + 3.2
        c2 = (wp.x, wp.y)
        mb.prism(SL.ccw(ngon(c2, r + 0.35, 8, 22.5)), z - 0.4, z + 1.0, STONE)
        mb.prism(SL.ccw(ngon(c2, r, 8, 22.5)), z + 1.0, zt1, STONE_H)
        mb.prism(SL.ccw(ngon(c2, r + 0.45, 8, 22.5)), zt1, zt1 + 0.6, TRIM)
        SL.spire(mb, c2, r + 0.9, zt1 + 0.6, 10.5, ROOF, n=8)
        mb.cyl(0.26, 2.6, (wp.x, wp.y, zt1 + 0.6 + 10.5 + 0.9), (0, 0, 0), IRON, n=4, r2=0.02, bevel=0.0)
        # frestas quentes estreitas nas faces que dao para a rua (faces do octogono centradas em k*45 graus)
        out = math.degrees(math.atan2(wp.y - G.o.y, wp.x - G.o.x))
        out = 45.0 * round(out / 45.0)
        ap = r * math.cos(math.pi / 8)
        for zz in (z + ze - 5.2, z + ze + 0.4):
            for da in (-45.0, 0.0, 45.0):
                a_ = math.radians(out + da)
                ux_, uy_ = -math.sin(a_), math.cos(a_)
                p = Vector((wp.x + ap * math.cos(a_), wp.y + ap * math.sin(a_), zz))
                mb.box((0.25, 0.6, 1.8), p, (0, 0, a_), WIN, 0.0)
                mb.box((0.4, 1.1, 0.3), p + Vector((0, 0, -1.05)), (0, 0, a_), TRIM, 0.0)
                mb.beam(p + Vector((ux_ * 0.55, uy_ * 0.55, 0.9)), p + Vector((0, 0, 1.45)), 0.3, 0.3, TRIM, 0.0)
                mb.beam(p - Vector((ux_ * 0.55, uy_ * 0.55, -0.9)), p + Vector((0, 0, 1.45)), 0.3, 0.3, TRIM, 0.0)
        octo_col("SG_VilHouse", wp.x, wp.y, r + 0.3, z - 0.4, z + ze + 3.2)
    # ---- colisao do corpo (caixa)
    bx0, bx1, by0, by1 = body
    cxb, cyb = (min(bx0, wx0) + max(bx1, wx1)) / 2, (min(by0, wy0) + max(by1, wy1)) / 2
    sxb = max(bx1, wx1) - min(bx0, wx0) + 0.7
    syb = max(by1, wy1) - min(by0, wy0) + 0.7
    hb = ze + R * 0.55
    col_box("SG_VilHouse", (sxb, syb, hb + 0.4), G.p(cxb, cyb, hb / 2 - 0.2), G.r())


# especificacao das 11 casas (indice = sg_layout.HOUSE_LOTS): 1 ou 2 pavimentos, empena de frente ou de lado,
# balanco, aguas-furtadas, chamine (x relativo a meia-largura, y relativo a meia-profundidade), um torreao, lojas
SPECS = [
    # P1 oeste
    dict(stories=[("stone", 6.4), ("timber", 5.6)], jetty=0.8, rise=8.4, shop=True, dormers=[("+y", 3.6)],
         chimney=(-0.62, -0.35), chim_kind="twin", planter=True, attic_all=True),
    dict(stories=[("timber", 6.8)], rise=9.8, dormers=[("+y", -2.6), ("+y", 2.6)], chimney=(0.6, -0.3), nwin=2,
         chim_kind="hood", planter=True, attic_all=True),
    dict(stories=[("stone", 6.0), ("timber", 5.4)], jetty=0.8, rise=9.8, gable_front=True, chimney=(-0.55, 0.5),
         chim_kind="stack", chim_h=3.4),
    # P1 leste
    dict(stories=[("stone", 6.6), ("timber", 6.0)], jetty=0.8, rise=8.6, turret=(-1, 1), dormers=[("+y", 3.2)],
         chimney=(0.66, -0.4), chim_kind="twin", planter=True, attic_all=True),
    dict(stories=[("timber", 7.0)], rise=10.2, gable_front=True, chimney=(0.5, -0.5), attic_all=True,
         chim_kind="hood", planter=True),
    dict(stories=[("stone", 6.2), ("timber", 5.4)], jetty=0.8, rise=8.0, shop=True, dormers=[("+y", -2.8)],
         chimney=(0.6, -0.3), chim_kind="stack", chimney2=(-0.55, -0.4), chim2_kind="hood", attic_all=True),
    # P2 oeste
    dict(stories=[("stone", 6.4), ("timber", 5.8)], jetty=0.8, rise=8.8, shop=True, dormers=[("+y", -3.6), ("+y", 3.6)],
         chimney=(0.62, -0.35), chim_kind="hood", planter=True, attic_all=True),
    dict(stories=[("timber", 6.8)], rise=11.0, gable_front=True, chimney=(-0.5, 0.45), chim_kind="twin", chim_h=2.0),
    dict(stories=[("stone", 6.0), ("timber", 5.6)], jetty=0.8, rise=9.6, gable_front=True, chimney=(0.5, -0.5),
         chim_kind="stack", planter=True),
    # P2 leste
    dict(stories=[("timber", 6.8)], rise=9.0, dormers=[("+y", -2.6), ("+y", 2.6)], chimney=(-0.6, -0.3), nwin=2,
         chim_kind="hood", chimney2=(0.62, -0.3), chim2_kind="stack", planter=True, attic_all=True),
    dict(stories=[("stone", 6.2), ("timber", 5.6)], jetty=0.8, rise=8.4, shop=True, dormers=[("+y", 2.8)],
         chimney=(-0.62, -0.35), chim_kind="twin", attic_all=True),
]
GROUPS = [("P1W", (0, 1, 2)), ("P1E", (3, 4, 5)), ("P2W", (6, 7, 8)), ("P2E", (9, 10))]


# ------------------------------------------------------------------ praca + fonte
def fountain_statue(mb, x, y, zb, yaw, s=0.7):
    """estatua encapuzada de manto longo (a mesma familia das estatuas do patio, sg_court.statue, em escala s) sobre
    a taca da fonte: plinto octogonal, manto de obsidiana, capuz pontudo, lamina de prata fincada A FRENTE com a
    ponta para baixo. Local +Y = frente (yaw). Nada de colisao (fica sobre a bacia)."""
    F = Frame(x, y, zb, yaw - math.pi / 2)
    rot = F.r()
    mb.cyl(1.5 * s, 0.5 * s, F.p(0, 0, 0.25 * s), F.r(0, 0, math.pi / 8), OBS, n=8, bevel=0.0)
    z0 = 0.5 * s
    # manto: barra alargada + corpo conico + ombros + capuz pontudo (inclinado para tras)
    mb.cyl(1.38 * s, 0.55 * s, F.p(0, 0, z0 + 0.275 * s), rot, OBS, n=10, r2=1.26 * s, bevel=0.0)
    mb.cyl(1.26 * s, 4.9 * s, F.p(0, 0, z0 + 3.0 * s), rot, OBS, n=10, r2=0.84 * s, bevel=0.0)
    mb.cyl(0.98 * s, 0.75 * s, F.p(0, 0, z0 + 5.82 * s), rot, OBS, n=10, r2=0.62 * s, bevel=0.0)
    mb.cyl(0.74 * s, 1.9 * s, F.p(0, -0.12 * s, z0 + 6.75 * s), F.r(0.2), OBS, n=8, r2=0.1 * s, bevel=0.0)
    # bracos (mangas) descendo para o cabo; maos
    for sg in (-1, 1):
        mb.beam(F.p(sg * 0.95 * s, 0.05 * s, z0 + 5.2 * s), F.p(sg * 0.28 * s, 1.35 * s, z0 + 3.85 * s),
                0.5 * s, 0.55 * s, OBS, 0.0)
        mb.box((0.34 * s, 0.4 * s, 0.36 * s), F.p(sg * 0.17 * s, 1.42 * s, z0 + 3.72 * s), F.r(), OBS, 0.0)
    # lamina fincada a frente (ponta para baixo), guarda e cabo de obsidiana, pomo de prata
    mb.box((0.5 * s, 0.14 * s, 3.1 * s), F.p(0, 1.5 * s, z0 + 1.6 * s), F.r(), "Metal_SG_Silver", 0.0)
    mb.box((1.6 * s, 0.3 * s, 0.26 * s), F.p(0, 1.5 * s, z0 + 3.28 * s), F.r(), OBS, 0.0)
    mb.box((0.24 * s, 0.24 * s, 0.75 * s), F.p(0, 1.5 * s, z0 + 3.78 * s), F.r(), OBS, 0.0)
    mb.ico(0.2 * s, tuple(F.p(0, 1.5 * s, z0 + 4.26 * s)), "Metal_SG_Silver", 1)


def plaza():
    rng = random.Random(4101)
    mb = MB("SG_Vil_Plaza", COLL, rng, detail="near")
    c = L.PLAZA_C
    R = L.PLAZA_R
    z = P1
    mb.prism(SL.ccw(ngon(c, R, 64)), z - 0.25, z + 0.07, "Stone_Paving_SG")
    ring_prism(mb, c, R - 1.4, R, 64, z - 0.1, z + 0.13, TRIM)                 # borda de cantaria
    ring_prism(mb, c, 7.4, 9.2, 24, z - 0.1, z + 0.1, M_COB)                    # colar escuro da fonte
    for r0, r1 in ((9.2, 9.8), (16.4, 17.0)):
        ring_prism(mb, c, r0, r1, 48, z - 0.1, z + 0.11, TRIM)
    # rosacea do chao: 16 setores alternados (escuro/claro) entre os aneis + 16 raios de cantaria
    n = 16
    for k in range(n):
        a0 = 360.0 / n * k
        a1 = a0 + 360.0 / n
        if k % 2 == 0:
            outer = SL.arc_pts(16.4, a0, a1, 5.0, c[0], c[1])
            inner = SL.arc_pts(9.8, a1, a0, 5.0, c[0], c[1])
            mb.prism(SL.ccw(outer + inner), z - 0.1, z + 0.095, M_COB)
        a = math.radians(a0)
        if k in (4, 12):
            continue            # os raios do eixo viram o fio da ordem (abaixo)
        for r0, r1 in ((9.8, 16.4), (17.0, R - 1.4)):
            if r0 > 16 and k % 2 == 1:
                continue
            rm = (r0 + r1) / 2
            mb.box((r1 - r0, 0.55, 0.22), (c[0] + rm * math.cos(a), c[1] + rm * math.sin(a), z + 0.0),
                   (0, 0, a), STONE_H, 0.0)
    # o FIO da ordem atravessa a praca no eixo: da borda (vindo da entrada / indo para a escada) ate o colar da fonte;
    # barra de obsidiana com o fio violeta rente (mesmo desenho do eixo nobre do sg_court)
    for s in (-1, 1):
        ya, yb = sorted((c[1] + s * 9.25, c[1] + s * (R + 0.02)))
        mb.box2((c[0] - 0.55, ya, z - 0.1), (c[0] + 0.55, yb, z + 0.14), OBS, 0.0)
        mb.box2((c[0] - 0.14, ya, z - 0.1), (c[0] + 0.14, yb, z + 0.15), "SG_VioletDeep_Glow", 0.0)
    mb.finish()

    # fonte: bacia dodecagonal (casa com a colisao do sg_col: 12 lados, R 7, topo P1+2,6), taca em 2 niveis, lua de prata
    mf = MB("SG_Vil_Fountain", COLL, rng, detail="near")
    rot = 0.0
    mf.prism(SL.ccw(ngon(c, 7.55, 12, rot)), z - 0.1, z + 0.32, TRIM)                 # degrau
    ring_prism(mf, c, 6.05, 7.0, 12, z + 0.32, z + 2.3, "Stone_SG_Castle", rot)       # parede da bacia
    ring_prism(mf, c, 5.85, 7.25, 12, z + 2.3, z + 2.6, TRIM, rot)                    # capeamento
    for k in range(12):
        a = math.radians(rot + 30.0 * k)
        mf.box((0.75, 0.75, 1.98), (c[0] + 7.02 * math.cos(a), c[1] + 7.02 * math.sin(a), z + 1.31), (0, 0, a), TRIM,
               0.0)
    mf.prism(SL.ccw(ngon(c, 6.1, 12, rot)), z + 0.32, z + 1.95, "Stone_SG_Castle")     # fundo da bacia
    mf.prism(SL.ccw(ngon(c, 6.08, 12, rot)), z + 1.95, z + 2.05, "Water_SG")           # lamina d'agua
    cx, cy = c
    mf.cyl(1.45, 0.6, (cx, cy, z + 2.3), (0, 0, math.pi / 8), TRIM, n=8, bevel=0.0)
    mf.cyl(1.05, 2.4, (cx, cy, z + 3.8), (0, 0, math.pi / 8), TRIM, n=8, r2=0.8, bevel=0.0)
    mf.cyl(0.8, 1.1, (cx, cy, z + 5.55), (0, 0, 0), "Stone_SG_Castle", n=12, r2=3.0, bevel=0.0)   # taca de baixo
    ring_prism(mf, c, 2.7, 3.15, 12, z + 6.0, z + 6.35, TRIM)
    mf.cyl(2.72, 0.12, (cx, cy, z + 6.18), (0, 0, 0), "Water_SG", n=12, bevel=0.0)
    mf.cyl(0.55, 2.0, (cx, cy, z + 7.3), (0, 0, math.pi / 8), TRIM, n=8, r2=0.45, bevel=0.0)
    mf.cyl(0.5, 0.8, (cx, cy, z + 8.6), (0, 0, 0), "Stone_SG_Castle", n=12, r2=1.7, bevel=0.0)    # taca de cima
    ring_prism(mf, c, 1.45, 1.8, 12, z + 8.95, z + 9.2, TRIM)
    mf.cyl(1.47, 0.1, (cx, cy, z + 9.05), (0, 0, 0), "Water_SG", n=12, bevel=0.0)
    # o MARCO da praca (referencia v2, ref2_plaza): estatua encapuzada da ordem sobre a taca de cima - manto longo de
    # pedra escura, lamina de prata apontada para baixo a frente, encarando o sul (quem chega da entrada). ~6 de
    # altura; NENHUMA colisao nova (so a bacia do sg_col). Nao repete o emblema (o monumental da fachada esta no
    # mesmo eixo): a figura e a mesma familia das estatuas do patio (sg_court), em escala de coroamento.
    fountain_statue(mf, cx, cy, z + 9.05, -math.pi / 2, 0.78)   # plinto dentro do anel da taca (agua em 9,1); ~6,1 alto
    # 4 lanternas douradas da ordem (SO Neon) sobre o capeamento da bacia externa, nas diagonais (entre os paineis
    # do emblema): o ritmo de luz quente da referencia em volta do marco (escala 0,6: nao briga com a taca)
    for a in (45.0, 135.0, 225.0, 315.0):
        ra = math.radians(a)
        EM.lantern_pedestal(mf, mf, mf, (cx + 6.7 * math.cos(ra), cy + 6.7 * math.sin(ra), z + 2.6), ra, 0.6)
    # o medalhao da ordem BAIXO, num painel de obsidiana na quina do eixo da bacia, encarando o sul (entrada) e o norte
    # (escada): topo < piso + 2
    for sgn in (-1, 1):
        mf.box((2.2, 1.05, 1.75), (cx, cy + sgn * 7.125, z + 1.3), (0, 0, 0), OBS, 0.06)
        mf.box((2.45, 1.2, 0.2), (cx, cy + sgn * 7.15, z + 2.25), (0, 0, 0), TRIM, 0.0)
        EM.plaque(mf, mf, mf, mf, (cx, cy + sgn * (7.65 + 0.3), z + 1.3), sgn * math.pi / 2, 0.58)
        col_box("SG_VilFountainPanel", (2.2, 1.05, 2.4), (cx, cy + sgn * 7.125, z + 1.2))
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


def streets():
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
            # os caminhos do patio leste param na borda da praca de aproximacao da dungeon (y 33; a praca e do
            # sg_dungeon: semicirculo r 23 em (100, 56) e faixa x 77..123, y 33..59)
            base = SL.ccw(SL.clip(base, 0.0, 1.0, DUN_PLAZA_Y))
        for poly in (cut_axis(base) if crosses else [base]):
            mb.prism(poly, z - 0.25, z + 0.05, M_COB)
        if z == P3:
            continue            # patio leste / dungeon: so o calcamento (o detalhe e das zonas do P3)
        # paralelepipedo escuro: margens de calcamento escuro + faixa central ainda mais escura (le como rua sobre
        # grama OU lajes, abaixo do eixo nobre na hierarquia)
        core = L.STREETS[i][0]
        cpoly = SL.ccw(SL.ribbon_poly(core, w / 2 - 1.5))
        for poly in (cut_axis(cpoly) if crosses else [cpoly]):
            mb.prism(poly, z - 0.1, z + 0.075, "Stone_SG_Floor")
        # meio-fio dos dois lados (interrompido em cruzamentos, praca, escadas, porta do craft e fora do piso)
        for side in (-1, 1):
            line = _resample(_offset_line(pts, side * (w / 2 - 0.3)), 1.0)
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
            for run in runs:
                k = 0
                while k < len(run) - 1:
                    j = min(len(run) - 1, k + 6)
                    a, b = run[k], run[j]
                    ln = math.hypot(b[0] - a[0], b[1] - a[1])
                    if ln > 0.3:
                        mb.box((ln + 0.1, 0.6, 0.34), ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z + 0.05),
                               (0, 0, math.atan2(b[1] - a[1], b[0] - a[0])), STONE, 0.0)
                    k = j
    for o in objs.values():
        o.finish()
    # escada P1 -> P2 (so visual; a colisao e do sg_col) + muretas baixas onde a rua do P2 tem queda
    ms = MB("SG_Vil_StairP1P2", COLL, rng, detail="near")
    SL.plan_stair(ms, "P1P2", m="Stone_Paving_SG", side_m=STONE)
    for s in (-1, 1):
        SL.vis_parapet(ms, [(s * 9.9, -83.45, P2), (s * 26.0, -83.45, P2)], h=1.5, w=1.0, m=STONE)
    SL.vis_parapet(ms, [(-118.0, -55.0, P2), (-119.2, -40.4, P2), (-117.6, -35.0, P2)], h=1.5, w=1.0, m=STONE)
    ms.finish()


# ------------------------------------------------------------------ postes de ferro (eixo principal + rua da praca)
LAMPS = [
    # (x, y, z, com_luz)  topo da escada P1P2 / cruzamento do eixo com a rua do P2 / rua da praca (O e L).
    # O pe da escada fica com as lanternas da praca (vestir): par proprio aqui virava cacho de postes.
    (-10.6, -80.6, P2, True), (10.6, -80.6, P2, True),
    (7.8, -51.6, P2, True),
    (-46.0, -125.3, P1, True), (48.0, -112.9, P1, True),
]


def lamps():
    rng = random.Random(4103)
    mb = MB("SG_Vil_Lamps", COLL, rng, detail="near")
    # topo da escada P1P2: o par de postes vira o ARCO de ferro negro (transicao praca -> vila alta), lanternas quentes
    # penduradas para dentro; as 2 luzes continuam as mesmas (agora na lanterna do arco)
    import sg_court as CT
    (xa, ya, za, _), (xb, yb, zb, _) = LAMPS[0], LAMPS[1]
    lan = CT.iron_arch(mb, (xa + xb) / 2, ya, za, abs(xb - xa) / 2, "Lantern_Glow", area="SG_VilLamp")
    for i, (x, y, zc) in enumerate(lan):
        light("L_SGVil_Lamp_%02d" % i, "POINT", (x, y, zc), 260.0, (1.0, 0.7, 0.4), 0.4)
    # postes soltos: viram o lantern_post DOURADO da ordem (referencia v2); a lanterna fica na MESMA cota (z + 8,3),
    # entao as 3 luzes reais continuam onde estavam (realocadas para dentro da lanterna nova, nenhuma luz a mais)
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
# estandartes pequenos da ordem SO nas esquinas principais: as 2 casas do P2 que ladeiam o eixo na rua transversal e
# (v3) as 2 casas do P1 que fecham as ruas da praca pelo norte (fachadas para a rua, quina voltada para o eixo, mesma
# altura): ritmo em pares simetricos, nao enfeite. (indice da casa, altura do suporte acima do piso)
HOUSE_BANNERS = [(8, 10.4), (10, 10.4), (2, 10.2), (5, 10.2)]
BANNER_W, BANNER_H = 1.8, 4.0


def _house_axes(idx):
    x, y, w, d, deg, z = L.HOUSE_LOTS[idx]
    a = math.radians(deg)
    fwd = (math.cos(a), math.sin(a))                  # para onde a fachada olha
    lat = (-fwd[1], fwd[0])
    return x, y, w, d, z, fwd, lat


def house_identity(mb):
    for idx, hz in HOUSE_BANNERS:
        x, y, w, d, z, fwd, lat = _house_axes(idx)
        jet = SPECS[idx].get("jetty", 0.0)
        # quina da fachada mais perto do eixo (x = 0)
        s = 1.0 if -x * lat[0] > 0 else -1.0
        wall = (x + fwd[0] * (d / 2 + jet) + lat[0] * s * (w / 2 - 1.1),
                y + fwd[1] * (d / 2 + jet) + lat[1] * s * (w / 2 - 1.1))
        reach = BANNER_W / 2 + 0.55
        top = (wall[0] + fwd[0] * reach, wall[1] + fwd[1] * reach, z + hz)
        yaw = math.atan2(lat[1] * s, lat[0] * s)       # o pano encara a rua na direcao do eixo
        EM.banner(mb, mb, mb, mb, top, yaw, BANNER_W, BANNER_H, trim=EM.GOLD)
        # mao-francesa de ferro negro (da parede a ponta da verga)
        mb.beam((wall[0], wall[1], z + hz - 1.5), (wall[0] + fwd[0] * (reach * 2 - 0.2), wall[1] + fwd[1] * (reach * 2 - 0.2),
                                                   z + hz - 0.05), 0.14, 0.16, BIRON, 0.0)
        mb.box((0.5, 0.5, 0.6), (wall[0] + fwd[0] * 0.1, wall[1] + fwd[1] * 0.1, z + hz - 1.5), (0, 0, yaw), BIRON, 0.0)
    # floreiras baixas de obsidiana ao pe da fachada (as duas quinas da frente; a do torreao fica sem)
    for idx, lot in enumerate(L.HOUSE_LOTS):
        x, y, w, d, z, fwd, lat = _house_axes(idx)
        spec = SPECS[idx]
        tur = spec.get("turret")
        ya = math.radians(lot[4]) - math.pi / 2
        for s in (-1, 1):
            if tur and not spec.get("gable_front") and \
                    lat[0] * s * tur[0] * math.cos(ya) + lat[1] * s * tur[0] * math.sin(ya) > 0.5:
                continue
            off = d / 2 + 0.35 + 0.42
            px, py = x + fwd[0] * off + lat[0] * s * (w / 2 - 1.55), y + fwd[1] * off + lat[1] * s * (w / 2 - 1.55)
            yaw = math.atan2(fwd[1], fwd[0])
            mb.box((0.84, 1.9, 0.72), (px, py, z + 0.3), (0, 0, yaw), OBS, 0.08)
            mb.box((0.62, 1.66, 0.3), (px, py, z + 0.72), (0, 0, yaw), "Leaf_SG_Pine", 0.08)
            for k in (-1, 0, 1):
                mb.ico(0.34, (px + lat[0] * k * 0.52, py + lat[1] * k * 0.52, z + 0.98), M_BLOOM, 1,
                       scale=(1.0, 1.0, 0.7))
            col_box("SG_VilPlanter", (0.9, 1.95, 1.0), (px, py, z + 0.4), (0, 0, yaw))
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
