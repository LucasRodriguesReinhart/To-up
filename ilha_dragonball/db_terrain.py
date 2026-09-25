# db_terrain - TERRENO da Ilha 2 (Dragon Ball): chao do plato (areia/terra, canteiros verdes, trilhas radiais
# calcadas), terraco da vila (calcada, areia e canteiros em volta dos lotes; muros de arrimo em blocos de arenito com
# coroamento Capsule branco/azul, guarda-corpos nas linhas das guardas do db_col e as 3 escadas da vila), penhascos da
# ilha flutuante (costelas de arenito penduradas com estratos escuros e tufos verdes), cristas baixas na borda, a massa
# de baixo que afunila ate as nuvens, as 12 mesas/pilares/agulhas e os 8 rochedos do plato.
# Dono: zona terrain (prefixo DB_Ter_, colecao 02_TERRAIN). A colisao andavel e do db_col (congelado): aqui so visual.
import math, random
import numpy as np
from mathutils import Vector, noise
import db_lib as DL
from db_lib import MB, FP, Frame
import db_layout as L
import db_col
import db_terrain_field as TF
import db_terrain_rock as TR

C = "02_TERRAIN"
G, HB = L.GROUND, L.HUB
SAND, SAND_B, DIRT, GRASS = "Sand_DB", "Sand_DB_B", "Dirt_DB", "Grass_DB"
PAVE, PAVE_B = "Stone_Paving_DB", "Stone_Paving_DB_B"
BLOCK, BLOCK_B = "Stone_DB_Block", "Stone_DB_Block_B"
WHITE, BLUE = "Plaster_DB_White", "Roof_DB_Blue"
ROCK = TR.ROCK
STEP = 3.3                      # passo base da grade do chao (studs)

# cameras de revisao da zona (loc, alvo, lente)
CAMS = {
    "CAM_DBTer_South": ((78.0, -262.0, 30.0), (0.0, -112.0, 2.0), 22),
    "CAM_DBTer_Under": ((-250.0, -270.0, -78.0), (-10.0, -10.0, -18.0), 22),
    "CAM_DBTer_West": ((-340.0, 30.0, 64.0), (-110.0, 80.0, 36.0), 24),
    "CAM_DBTer_Back": ((40.0, 430.0, 110.0), (0.0, 150.0, 50.0), 24),
    "CAM_DBTer_East": ((350.0, -40.0, 70.0), (120.0, 40.0, 30.0), 24),
    "CAM_DBTer_PlayerHeight_Rim": ((120.0, -84.0, G + 5.2), (40.0, -128.0, G + 1.0), 22),
    "CAM_DBTer_PlayerHeight_Hub": ((-24.0, 60.0, G + 5.2), (-52.0, 92.0, HB + 2.0), 22),
    "CAM_DBTer_PlayerHeight_Garden": ((-62.0, -64.0, G + 5.2), (-112.0, -96.0, G + 0.5), 22),
    "CAM_DBTer_PlayerHeight_Mesa": ((-104.0, 60.0, G + 5.2), (-150.0, 118.0, 66.0), 22),
    "CAM_DBTer_HubTop": ((-12.0, 84.0, HB + 5.2), (42.0, 118.0, HB + 2.0), 22),
    "CAM_DBTer_FrontPillar": ((-60.0, -170.0, 40.0), (-118.0, -104.0, 30.0), 24),
    "CAM_DBTer_PlayerHeight_HubRim": ((46.0, 196.0, HB + 5.2), (-40.0, 212.0, HB + 2.0), 22),
    "CAM_DBTer_PlayerHeight_SatSE": ((96.0, -44.0, G + 5.2), (140.0, -78.0, G + 1.0), 22),
    "CAM_DBTer_FallSE": ((126.0, -176.0, 12.0), (88.0, -104.0, 10.0), 22),
    "CAM_DBTer_PlayerHeight_HubWest": ((-104.0, 62.0, G + 5.2), (-112.0, 100.0, HB + 1.0), 22),
    "CAM_DBTer_PlayerHeight_Notch": ((6.0, -104.0, G + 5.2), (-4.0, -150.0, L.DECK + 1.0), 22),
    "CAM_DBTer_BackFar": ((0.0, 520.0, 60.0), (0.0, 120.0, 40.0), 28),
    "CAM_DBTer_PlayerHeight_NEMesa": ((104.0, 112.0, HB + 5.2), (126.0, 136.0, HB + 4.0), 22),
    "CAM_DBTer_PlayerHeight_NWMesa": ((-116.0, 118.0, HB + 5.2), (-142.0, 124.0, HB + 5.0), 22),
}
EXTRA_ROUTES = {}
EXTRA_PROBES = []

# ------------------------------------------------------------------ desenho do terraco da vila
LOT_PAD = 0.5                   # lote = quadrado de meio-lado r + 0,5 (livre para a vila)
LOT_TOP = L.HUB - 0.04          # laje do lote RENTE ao terraco: a casa redonda da vila assenta o piso dela por cima e
                                # os cantos do quadrado que sobram nao viram buraco (o jogador pisa na cota da colisao)
HUB_PAVE_RECTS = [(-15.0, 72.0, 15.0, 133.0)]
HUB_PAVE_DISCS = [(0.0, 112.0, 19.0)]
HUB_STREETS = [
    ([(-93.0, 85.5), (-78.0, 82.5), (-52.0, 81.5), (0.0, 81.2), (52.0, 81.5), (78.0, 82.5), (96.0, 87.0)], 4.3),
    ([(-86.0, 84.0), (-86.0, 115.5)], 3.2),
    ([(-58.0, 84.0), (-58.0, 89.5)], 2.8),
    ([(62.0, 84.0), (62.0, 88.5)], 2.8),
    ([(14.0, 112.0), (23.5, 112.0)], 3.0),
    ([(90.0, 86.0), (86.0, 104.0), (79.0, 113.0)], 2.8),
    ([(80.0, 121.0), (93.0, 134.0)], 2.8),
]


def lot_rects():
    out = []
    for x, y, r, kind in L.HUB_LOTS:
        h = r + LOT_PAD
        out.append((x - h, y - h, x + h, y + h))
    return out


def garden_blobs(level):
    rng = random.Random(505)
    out = []
    for x, y, r in L.GARDENS:
        blob = DL.ccw(DL.blob_poly(x, y, r, 14, rng, 0.2, rng.uniform(0, 6.28)))
        if abs(L.zone_of(x, y) - level) < 0.1:
            out.append(blob)
    return out


# ------------------------------------------------------------------ campos
_F = {}


def fields():
    if _F:
        return _F
    hp, ext = TR.hub_ext()
    notch = db_col.entry_notch()
    req_x = [-22.0, 22.0, notch[0][0], notch[1][0]] + [p[0] for p in L.HUB_POLY] + [p[0] for p in L.CAP_POLY]
    req_y = [L.ENTRY_PLAZA[1], L.ENTRY_PLAZA[3]] + [p[1] for p in L.HUB_POLY] + [p[1] for p in L.CAP_POLY]
    for x0, y0, x1, y1 in lot_rects():
        req_x += [x0, x1]
        req_y += [y0, y1]
    xs = TF.grid_lines(-182.0, 166.0, STEP, req_x)
    ys = TF.grid_lines(-142.0, 222.0, STEP, req_y)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    F = _F
    F["xs"], F["ys"], F["X"], F["Y"] = xs, ys, X, Y
    F.update(terms(X, Y))
    # ruidos por no (relevo e manchas)
    nz = np.zeros(X.shape)
    dn = np.zeros(X.shape)
    gn = np.zeros(X.shape)
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            nz[i, j] = noise.noise(Vector((x * 0.045, y * 0.045, 3.7))) + 0.45 * noise.noise(
                Vector((x * 0.13, y * 0.13, 9.1)))
            dn[i, j] = noise.noise(Vector((x * 0.022, y * 0.022, 21.3)))
            gn[i, j] = noise.noise(Vector((x * 0.05, y * 0.05, 41.9)))
    F["nz"], F["dn"], F["gn"] = nz, dn, gn
    return F


def terms(X, Y):
    """campos assinados (negativo = dentro) usados pelo chao, pela vila e pelo recorte das trilhas"""
    hp, ext = TR.hub_ext()
    out = {}
    out["rim"] = TF.sd_poly(X, Y, DL.rim())
    out["prom"] = TF.sd_polar(X, Y, L.prom_r, 0.5)
    x0, y0, x1, y1 = L.ENTRY_PLAZA
    out["plaza"] = TF.sd_rect(X, Y, x0, y0, x1, y1)
    out["notch"] = TF.sd_poly(X, Y, db_col.entry_notch())
    out["sum"] = TF.sd_disc(X, Y, L.SUMMON_C[0], L.SUMMON_C[1], L.SUMMON_R)
    hub = TF.sd_poly(X, Y, hp)
    out["hub"] = hub
    hubx = hub
    for q in ext:
        hubx = np.minimum(hubx, TF.sd_poly(X, Y, q))
    out["hubx"] = hubx
    out["cap"] = TF.sd_poly(X, Y, DL.cap_poly())
    out["exit"] = np.minimum(TF.sd_ribbon(X, Y, L.EXIT_PATH, L.EXIT_PATH_HW),
                             TF.sd_ribbon(X, Y, L.HUB_EXIT_LINK, L.HUB_EXIT_LINK_HW))
    wg, wh = None, None
    for k, p in db_col.water_polys():
        d = TF.sd_poly(X, Y, p)
        if k == "g":
            wg = d if wg is None else np.minimum(wg, d)
        else:
            wh = d if wh is None else np.minimum(wh, d)
    out["wg"], out["wh"] = wg, wh
    lots = None
    for r in lot_rects():
        d = TF.sd_rect(X, Y, *r)
        lots = d if lots is None else np.minimum(lots, d)
    out["lots"] = lots
    pth = None
    for pts, w in L.GROUND_PATHS:
        d = TF.sd_ribbon(X, Y, pts, w / 2.0)
        pth = d if pth is None else np.minimum(pth, d)
    out["paths"] = pth
    gg = None
    for b in garden_blobs(G):
        d = TF.sd_poly(X, Y, b)
        gg = d if gg is None else np.minimum(gg, d)
    out["gard_g"] = gg
    gh = None
    for b in garden_blobs(HB):
        d = TF.sd_poly(X, Y, b)
        gh = d if gh is None else np.minimum(gh, d)
    out["gard_h"] = gh
    pv = None
    for x0, y0, x1, y1 in HUB_PAVE_RECTS:
        d = TF.sd_rect(X, Y, x0, y0, x1, y1)
        pv = d if pv is None else np.minimum(pv, d)
    for cx, cy, r in HUB_PAVE_DISCS:
        pv = np.minimum(pv, TF.sd_disc(X, Y, cx, cy, r))
    for pts, hw in HUB_STREETS:
        pv = np.minimum(pv, TF.sd_ribbon(X, Y, pts, hw))
    out["pave_h"] = pv
    return out


def ground_region(F):
    """regiao do chao GROUND + (profundidade, material) da saia de cada termo que a recorta"""
    tl = [(F["rim"], 1.4, DIRT),                       # borda: as tampas das costelas cobrem
          (-F["prom"], 0.8, DIRT),                     # promenade (mineracao): sarjeta
          (-F["plaza"], 0.4, DIRT),                    # praca da entrada
          (-F["notch"], G - (L.DECK - 1.0), ROCK),     # recorte da escadaria da chegada (desce ate a ponte)
          (-(F["hubx"] + 1.2), 0.0, DIRT),             # terraco da vila
          (-F["wg"], 0.6, BLOCK)]                      # pocos e canais
    st = np.stack([t[0] for t in tl])
    return st.max(0), st.argmax(0), [t[1] for t in tl], [t[2] for t in tl]


def _skirt_fn(R, dom, depth, mats, extra=0.0, own=None):
    def f(pa, pb, m):
        if R[pa] > -1e-4 and R[pb] > -1e-4:
            da, db_ = depth[dom[pa]], depth[dom[pb]]
            d = max(da, db_)
            if d + extra <= 0.0:
                return None
            return d + extra, (own or mats[dom[pa] if da >= db_ else dom[pb]])
        if extra > 0.0:
            return extra, own or m
        return None
    return f


# ------------------------------------------------------------------ chao do plato
def ground(rng):
    F = fields()
    xs, ys = F["xs"], F["ys"]
    R, dom, depth, mats = ground_region(F)
    P = F["paths"]
    Gd = F["gard_g"]
    ring = TF.band(Gd, 0.0, 1.7)
    dpatch = 0.34 - F["dn"]
    fade = np.clip((-R - 1.0) / 6.0, 0.0, 1.0) * np.clip((P - 0.6) / 2.5, 0.0, 1.0)
    Z = G + 0.12 * F["nz"] * fade
    grass = np.maximum.reduce([R, Gd, -P])
    Fl = np.maximum(R, np.minimum(-Gd, P))
    dd = np.minimum(P, ring)
    dirt = np.maximum(Fl, dd)
    sand = np.maximum.reduce([Fl, -dd, -dpatch])
    sand_b = np.maximum.reduce([Fl, -dd, dpatch])
    mb = MB("DB_Ter_Ground", C, rng, detail="near", floor=-999)
    fl = TF.Surf(mb, xs, ys, Z)
    sk = _skirt_fn(R, dom, depth, mats)
    fl.build(sand, SAND, skirt=sk)
    fl.build(sand_b, SAND_B, skirt=sk)
    fl.build(dirt, DIRT, skirt=sk)
    gs = TF.Surf(mb, xs, ys, Z + 0.09)
    gs.build(grass, GRASS, skirt=_skirt_fn(R, dom, depth, mats, extra=0.26, own=GRASS))
    TF.flush(mb, fl)
    TF.flush(mb, gs)
    return mb.finish(recalc=False)


# ------------------------------------------------------------------ lajes (trilhas radiais do chao e calcada da vila)
def ribbon_cands(pts, w, curb, rng, cands, tile=(2.3, 3.2)):
    """lajes ao longo de uma polilinha: fileiras de 2-4 lajes atravessadas + meio-fio dos dois lados (curb > 0)"""
    P = [Vector((x, y, 0.0)) for x, y in pts]
    segs = list(zip(P, P[1:]))
    total = sum((b - a).length for a, b in segs)

    def at(s):
        for a, b in segs:
            ln = (b - a).length
            if s <= ln + 1e-9:
                return a + (b - a) * (s / ln), (b - a).normalized()
            s -= ln
        a, b = segs[-1]
        return b.copy(), (b - a).normalized()
    field = w - 2.0 * curb
    s = -rng.uniform(0.0, 1.0)
    while s < total + 1.8:
        Ls = rng.uniform(*tile)
        sm = s + Ls * 0.5
        cl = min(max(sm, 0.0), total)
        p, t = at(cl)
        p = p + t * (sm - cl)
        nrm = Vector((-t.y, t.x, 0.0))
        k = max(2, int(round(field / 2.5)))
        cuts = sorted([rng.uniform(0.3, 0.7)] if k == 2 else [(q + rng.uniform(-0.18, 0.18)) / k for q in range(1, k)])
        edges = [0.0] + cuts + [1.0]
        ang = math.atan2(t.y, t.x)
        for a0, a1 in zip(edges, edges[1:]):
            u0 = -field / 2 + field * a0
            u1 = -field / 2 + field * a1
            c = p + nrm * ((u0 + u1) / 2)
            cands.append(("stone", c, ang + rng.uniform(-0.03, 0.03), Ls - 0.2, (u1 - u0) - 0.18, t, nrm))
        if curb > 0.0:
            for sg in (-1, 1):
                c = p + nrm * (sg * (w / 2 - curb / 2))
                cands.append(("curb", c, ang, Ls - 0.08, curb - 0.1, t, nrm))
        s += Ls


def grid_cands(x0, y0, x1, y1, tile, rng, cands):
    """lajes quadradas em fiadas desencontradas (praca)"""
    t = Vector((1.0, 0.0, 0.0))
    nrm = Vector((0.0, 1.0, 0.0))
    row = 0
    y = y0
    while y < y1:
        h = tile * rng.uniform(0.85, 1.1)
        x = x0 - (tile * 0.5 if row % 2 else 0.0)
        while x < x1:
            wd = tile * rng.uniform(0.8, 1.25)
            c = Vector((x + wd / 2, y + h / 2, 0.0))
            cands.append(("stone", c, rng.uniform(-0.02, 0.02), wd - 0.22, h - 0.22, t, nrm))
            x += wd
        y += h
        row += 1


def cand_ok(cands, test):
    """True para as lajes cujo retangulo inteiro (centro + 4 cantos) passa no teste de regiao"""
    pts = []
    for kind, c, ang, ln, wd, t, nrm in cands:
        for du, dv in ((0, 0), (0.5, 0.5), (0.5, -0.5), (-0.5, 0.5), (-0.5, -0.5)):
            q = c + t * (ln * du) + nrm * (wd * dv)
            pts.append((q.x, q.y))
    A = np.array(pts)
    return test(A[:, 0], A[:, 1]).reshape(-1, 5).all(1)


def lay(mb, cands, ok, z_top, rng, curb_m=BLOCK, stone_m=PAVE, curb_up=0.12):
    """lajes com o topo em z_top; meio-fio curb_up acima delas (o pe do jogador nao afunda: tudo <= +0,25 do piso)"""
    n = 0
    for (kind, c, ang, ln, wd, t, nrm), good in zip(cands, ok):
        if not good or ln < 0.6 or wd < 0.4:
            continue
        if kind == "stone":
            hh = 0.3 + rng.uniform(-0.03, 0.03)
            mb.box((ln, wd, hh), (c.x, c.y, z_top - hh / 2), (0, 0, ang), stone_m, 0.0)
        else:
            mb.box((ln, wd, 0.62), (c.x, c.y, z_top + curb_up - 0.31), (0, 0, ang), curb_m, 0.0)
        n += 1
    return n


def paths(rng):
    mb = MB("DB_Ter_Paths", C, rng, detail="near", floor=-999)
    cands = []
    for pts, w in L.GROUND_PATHS:
        ribbon_cands(pts, w, 0.85, rng, cands)

    def test(X, Y):
        T = terms(X, Y)
        ok = ground_region(T)[0] < -0.15
        for x, y, r in L.PODS:
            ok &= np.hypot(X - x, Y - y) > r + 0.6
        for x, y, r, kind in L.GROUND_LOTS:
            ok &= np.hypot(X - x, Y - y) > r + 0.4
        return ok
    n = lay(mb, cands, cand_ok(cands, test), G + 0.11, rng)      # topo das lajes G+0,11, meio-fio G+0,23
    mb.finish()
    return n


def plaza_field(X, Y):
    d = None
    for x0, y0, x1, y1 in HUB_PAVE_RECTS:
        q = TF.sd_rect(X, Y, x0, y0, x1, y1)
        d = q if d is None else np.minimum(d, q)
    for cx, cy, r in HUB_PAVE_DISCS:
        d = np.minimum(d, TF.sd_disc(X, Y, cx, cy, r))
    return d


def hub_paving(rng):
    """calcada da vila: lajes grandes em fiadas na praca e ao longo das ruas, sobre o leito de rejunte do HubTop"""
    mb = MB("DB_Ter_HubPaving", C, rng, detail="near", floor=-999)
    grid = []
    x0, y0, x1, y1 = HUB_PAVE_RECTS[0]
    grid_cands(x0 - 20.0, y0, x1 + 20.0, y1 + 1.0, 3.3, rng, grid)

    def t_grid(X, Y):
        T = terms(X, Y)
        return (hub_region(T)[0] < -0.12) & (plaza_field(X, Y) < -0.12)
    n = lay(mb, grid, cand_ok(grid, t_grid), HB + 0.14, rng)
    street = []
    for pts, hw in HUB_STREETS:
        ribbon_cands(pts, hw * 2.0, 0.0, rng, street, tile=(2.6, 3.4))

    def t_street(X, Y):
        T = terms(X, Y)
        return (hub_region(T)[0] < -0.12) & (T["pave_h"] < -0.12) & (plaza_field(X, Y) > 0.12)
    n += lay(mb, street, cand_ok(street, t_street), HB + 0.14, rng)
    mb.finish()
    return n


# ------------------------------------------------------------------ terraco da vila (topo em HUB)
def hub_region(F):
    tl = [(F["rim"], 0.0, DIRT),                       # borda norte: as costelas cobrem
          (F["hubx"], 0.6, BLOCK),                     # contorno (muro de arrimo + coroamento cobrem)
          (-(F["cap"] + 1.0), 0.0, DIRT),              # terraco do Capsule (o topo entra 1,0 por baixo)
          (-F["exit"], 0.35, BLOCK),                   # ligacao com a prateleira da saida (mesmo nivel)
          (-F["wh"], 0.6, BLOCK),                      # poco NW
          (-F["lots"], 0.0, BLOCK)]                    # lotes da vila (laje propria rente, sem degrau)
    st = np.stack([t[0] for t in tl])
    return st.max(0), st.argmax(0), [t[1] for t in tl], [t[2] for t in tl]


def hub_top(rng):
    F = fields()
    xs, ys, X, Y = F["xs"], F["ys"], F["X"], F["Y"]
    R, dom, depth, mats = hub_region(F)
    P = F["pave_h"]
    lots = F["lots"]
    gr = np.minimum.reduce([TF.band(lots, 0.0, 3.0), F["gard_h"], TF.band(F["hub"], -2.8, 0.0),
                            TF.band(F["cap"], 0.0, 2.6), np.maximum(0.12 - F["gn"], 150.0 - Y)])
    fade = np.clip((-R - 1.0) / 5.0, 0.0, 1.0) * np.clip((P - 0.5) / 2.5, 0.0, 1.0)
    Z = HB + 0.08 * F["nz"] * fade
    pave = np.maximum(R, P)
    Fl = np.maximum(R, -P)
    grass = np.maximum(Fl, gr)
    sand = np.maximum(Fl, -gr)
    mb = MB("DB_Ter_HubTop", C, rng, detail="near", floor=-999)
    fl = TF.Surf(mb, xs, ys, Z)
    sk = _skirt_fn(R, dom, depth, mats)
    fl.build(pave, BLOCK_B, skirt=sk)
    fl.build(sand, SAND, skirt=sk)
    gs = TF.Surf(mb, xs, ys, Z + 0.09)
    gs.build(grass, GRASS, skirt=_skirt_fn(R, dom, depth, mats, extra=0.26, own=GRASS))
    TF.flush(mb, fl)
    TF.flush(mb, gs)
    # fundo liso sob o terraco do Capsule (fica dentro do volume dele; so tapa o vao se ele for vazado)
    cp = DL.cap_poly()
    mb.prism(cp, HB - 0.9, HB - 0.3, SAND, 0.0)
    # lajes dos lotes, rentes ao terraco (a vila assenta os predios por cima; canto descoberto = calcada, sem buraco)
    for x0, y0, x1, y1 in lot_rects():
        mb.box2((x0 + 0.02, y0 + 0.02, LOT_TOP - 0.5), (x1 - 0.02, y1 - 0.02, LOT_TOP), PAVE_B, 0.0)
    return mb.finish(recalc=False)


# ------------------------------------------------------------------ muros de arrimo, coroamento, guarda-corpos, escadas
def _simplify(pts, tol=0.05):
    """tira os pontos colineares de uma polilinha (Vector 2D/3D)"""
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        d1 = (b - a)
        d2 = (c - b)
        if d1.length < 1e-6:
            continue
        cr = abs(d1.x * d2.y - d1.y * d2.x) / max(1e-6, d1.length * d2.length)
        if cr > tol:
            out.append(b)
    out.append(pts[-1])
    return out


def hub_stairs():
    return [s for s in db_col.stair_list() if s[0].startswith("Hub")]


def near_hub_stair(x, y, pad):
    for nm, base, ang, w, n, rise, tread, g in hub_stairs():
        tx = base[0] + math.cos(ang) * tread * n
        ty = base[1] + math.sin(ang) * tread * n
        dx, dy = x - tx, y - ty
        along = abs(-dx * math.sin(ang) + dy * math.cos(ang))
        depth = abs(dx * math.cos(ang) + dy * math.sin(ang))
        if along < w / 2 + pad and depth < 3.0:
            return True
    return False


def wall_runs():
    """trechos do contorno da vila que dao para o chao GROUND (queda de 4): muro de arrimo"""
    hp, ext = TR.hub_ext()
    chords = {(tuple(q[0]), tuple(q[1])) for q in ext}
    n = len(hp)
    runs, run = [], []
    for i in range(n):
        a, b = Vector((hp[i][0], hp[i][1], 0.0)), Vector((hp[(i + 1) % n][0], hp[(i + 1) % n][1], 0.0))
        if (tuple(hp[i]), tuple(hp[(i + 1) % n])) in chords:
            if len(run) > 1:
                runs.append(run)
            run = []
            continue
        d = (b - a)
        ln = d.length
        u = d / ln
        nout = Vector((u.y, -u.x, 0.0))
        k = max(1, int(ln / 1.0))
        for s in range(k):
            p = a + d * (s / k)
            q = p + nout * 1.6
            ok = (L.point_in_poly(q.x, q.y, L.ISLAND_RIM) and L.zone_of(q.x, q.y) < HB - 2.3)
            if ok:
                run.append(p)
            else:
                if len(run) > 1:
                    runs.append(run)
                run = []
    if len(run) > 1:
        runs.append(run)
    # junta o ultimo com o primeiro se fecharem no vertice 0
    if len(runs) > 1 and (runs[0][0] - runs[-1][-1]).length < 1.5:
        runs[0] = runs[-1] + runs[0]
        runs.pop()
    return runs


def guard_runs():
    """as MESMAS linhas das guardas invisiveis da vila (db_col.terrace_guards, poligono Hub)"""
    stairs = db_col.stair_list()
    pts = DL.ccw(DL.hub_poly())
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)

    def near_stair_top(x, y, z_top):
        for nm, base, ang, w, n, rise, tread, g in stairs:
            if abs(base[2] + rise * n - z_top) > 0.3:
                continue
            tx = base[0] + math.cos(ang) * tread * n
            ty = base[1] + math.sin(ang) * tread * n
            dx, dy = x - tx, y - ty
            along = abs(-dx * math.sin(ang) + dy * math.cos(ang))
            depth = abs(dx * math.cos(ang) + dy * math.sin(ang))
            if along < w / 2 + 0.8 and depth < 3.0:
                return True
        return False

    def keep(x, y):
        d = Vector((x - cx, y - cy, 0))
        if d.length < 1e-3:
            return False
        d.normalize()
        ox, oy = x + d.x * 1.6, y + d.y * 1.6
        if not L.point_in_poly(ox, oy, L.ISLAND_RIM):
            return False
        zo = L.zone_of(ox, oy)
        if HB - zo <= 2.3:
            return False
        if db_col._opening(ox, oy):
            return False
        return not near_stair_top(x, y, HB)
    return db_col._runs(pts, keep, step=1.0)


def hub_walls(rng):
    mb = MB("DB_Ter_HubWalls", C, rng, detail="near", floor=-999)
    TH = 1.5
    off = 0.35 - TH / 2                  # face de fora 0,35 alem da borda (a guarda invisivel esta na borda)
    for run in wall_runs():
        pl = _simplify(run + [run[-1]] if len(run) < 2 else run)
        # muro de blocos por trecho reto (deslocado para fora), pontas estendidas para fechar as quinas
        for a, b in zip(pl, pl[1:]):
            d = (b - a)
            if d.length < 0.5:
                continue
            u = d.normalized()
            nout = Vector((u.y, -u.x, 0.0))
            a2 = a + nout * off - u * 0.8
            b2 = b + nout * off + u * 0.8
            FP.masonry_wall(mb, (a2.x, a2.y, G - 0.5), (b2.x, b2.y, G - 0.5), G - 0.5, HB - 0.78, TH, rng,
                            m=BLOCK, m2=BLOCK_B, course=1.24, mix=0.12, blk=(2.6, 4.6), core=True,
                            bevel=0.1, core_m=BLOCK_B)
        # coroamento Capsule: faixa azul saliente + capa branca (interrompido nas escadas)
        seg = []
        segs = []
        for p in run:
            if near_hub_stair(p.x, p.y, 1.3):
                if len(seg) > 1:
                    segs.append(seg)
                seg = []
            else:
                seg.append(p)
        if len(seg) > 1:
            segs.append(seg)
        for sp in segs:
            sp = _simplify(sp)
            path = [Vector((p.x, p.y, HB)) for p in sp]
            mb.sweep(path, [(-1.25, -0.5), (0.5, -0.5), (0.5, 0.16), (-1.25, 0.16)], WHITE, True)
            mb.sweep(path, [(0.18, -0.98), (0.62, -0.98), (0.62, -0.5), (0.18, -0.5)], BLUE, True)
    # guarda-corpo Capsule exatamente nas linhas das guardas invisiveis (Hub): mureta branca baixa, balaustres
    # brancos e corrimao azul (vazado: a vista da arena continua aberta), pilares maiores a cada ~9,6
    for run in guard_runs():
        pl = _simplify([Vector((p.x, p.y, HB)) for p in run])
        if len(pl) < 2:
            continue
        path = [Vector((p.x, p.y, HB)) for p in pl]
        mb.sweep(path, [(-0.42, 0.16), (0.42, 0.16), (0.42, 0.6), (-0.42, 0.6)], WHITE, True)
        mb.sweep(path, [(-0.42, 1.52), (0.42, 1.52), (0.42, 1.82), (-0.42, 1.82)], BLUE, True)
        total = sum((b - a).length for a, b in zip(pl, pl[1:]))
        k = max(1, int(round(total / 3.2)))
        marks = [total * i / k for i in range(k + 1)]
        acc = 0.0
        mi = 0
        for a, b in zip(pl, pl[1:]):
            ln = (b - a).length
            ang = math.atan2(b.y - a.y, b.x - a.x)
            while mi < len(marks) and marks[mi] <= acc + ln + 1e-6:
                t = (marks[mi] - acc) / ln if ln > 1e-6 else 0.0
                q = a + (b - a) * t
                if mi % 3 == 0 or mi == len(marks) - 1:
                    mb.box((0.95, 0.95, 1.95), (q.x, q.y, HB + 0.16 + 0.975), (0, 0, ang), WHITE, 0.08)
                    mb.box((1.15, 1.15, 0.3), (q.x, q.y, HB + 2.11 + 0.15), (0, 0, ang), BLUE, 0.08)
                else:
                    mb.box((0.5, 0.5, 0.95), (q.x, q.y, HB + 0.6 + 0.475), (0, 0, ang), WHITE, 0.0)
                mi += 1
            acc += ln
    # escadas da vila (visual, mesmas medidas da colisao) + pilaretes Capsule no topo
    for nm, base, ang, w, n, rise, tread, g in hub_stairs():
        DL.vis_stairs(mb, base, ang, w, n, rise, tread, PAVE, BLOCK)
        F = Frame(base[0], base[1], base[2], ang)
        for sg in (-1, 1):
            for xx, hz in ((tread * n - 0.6, rise * n), (0.6, rise)):
                p = F.p(xx, sg * (w / 2 + 0.6), hz + 1.2)
                mb.cyl(0.62, 1.7, (p.x, p.y, p.z + 0.85), m=WHITE, n=10, bevel=0.0)
                mb.cyl(0.78, 0.36, (p.x, p.y, p.z + 1.88), m=BLUE, n=10, bevel=0.0)
    return mb.finish()


# ------------------------------------------------------------------ build
def build():
    fields()
    ground(random.Random(11))
    paths(random.Random(12))
    hub_top(random.Random(13))
    hub_paving(random.Random(15))
    hub_walls(random.Random(14))
    TR.cliffs(random.Random(21))
    TR.crests(random.Random(22))
    TR.underside(random.Random(23))
    TR.mesas(random.Random(24))
    TR.plateau_rocks(random.Random(25))
