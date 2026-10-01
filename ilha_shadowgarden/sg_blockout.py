# sg_blockout - BLOCKOUT da Ilha 3 (Shadow Garden), zona por zona, com a paleta final em formas simples.
# Cada zona cria: massas visuais (detail="far"), a colisao dos PROPRIOS volumes (predios, torres, muralha, salas) e as
# luzes basicas. O chao, as escadas, as pontes, as guardas, o SUBSOLO andavel e TODOS os marcadores sao do
# sg_core/sg_col (sempre). O modulo de detalhe de uma zona SUBSTITUI a funcao dela aqui (build(skip={...})).
# v4 (ONDA 0, plano mestre aprovado 2026-09-30): blockout nas medidas novas - ilha 2,4x, castelo 2x com a porta 28 x 34
# e o timpano, salao 184 x 196 x 84 com arcada, presbiterio com o TRONO MOVEL (SG_Hall_ThroneMov) e o arco secreto,
# escada caracol, SALAO SOMBRIO (zona nova 'cave', prefixo SG_Cave_), salas 3x da masmorra com os nichos do portal da
# proxima sala, 7 casas VISITAVEIS (vao de porta 8 x 11, piso, escada, andar de cima), patio-jardim simples e
# jardim-mirante. A praca/fonte e a entrada/invocacao/alquimia/saida da v3 entram pelo sg_relocate (so mudam de lugar).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, yaw_to, prism, Frame, light, ngon_col, octo_col, box_walls_col
import fm_lib
import sg_layout as L
import sg_col

ZONES = ["terrain", "entry", "village", "castle", "hall", "cave", "summon", "craft", "dungeon", "water", "exit",
         "dressing"]
WIN = "Window_Warm"
fm_lib.MATS.setdefault("Stone_SGCaveRock", (fm_lib.S(34, 30, 48), 0.9, 0.0, 0, None, 0.08))    # rocha do salao sombrio
fm_lib.MATS.setdefault("Crystal_SGCave", (fm_lib.S(62, 42, 108), 0.3, 0.0, 0, None, 0.04))
fm_lib.MATS.setdefault("SG_CaveVoid_Glow", (fm_lib.S(46, 26, 104), 0.3, 0.0, 1.0, fm_lib.S(56, 30, 124), 0.0))


# ------------------------------------------------------------------ utilidades 2D
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


def keyhole(poly, hole, eps=0.06):
    """poligono (anti-horario) com um furo RETANGULAR (x0, y0, x1, y1) por fenda (keyhole): um ngon simples"""
    poly = SL.ccw(poly)
    x0, y0, x1, y1 = hole
    hc = [(x0, y0), (x0, y1), (x1, y1), (x1, y0)]          # horario
    best = None
    for i, p in enumerate(poly):
        for k, h in enumerate(hc):
            d = math.hypot(p[0] - h[0], p[1] - h[1])
            if best is None or d < best[0]:
                best = (d, i, k)
    _, i, k = best
    p, h = poly[i], hc[k]
    dx, dy = h[0] - p[0], h[1] - p[1]
    ln = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / ln * eps, dx / ln * eps
    ring = [hc[(k + j) % 4] for j in range(5)]
    ring[-1] = (ring[-1][0] + nx, ring[-1][1] + ny)
    return poly[:i + 1] + ring + [(p[0] + nx, p[1] + ny)] + poly[i + 1:]


def scale_poly(poly, f, c):
    return [(c[0] + (x - c[0]) * f, c[1] + (y - c[1]) * f) for x, y in poly]


def cave_hole(pad=2.5):
    x0, y0, x1, y1 = L.CAVE
    cx, cy = L.SPIRAL_C
    return (x0 - pad, y0 - pad, x1 + pad, max(y1, cy + L.SPIRAL_R_OUT) + pad)


def shaft_hole(pad=0.5):
    cx, cy = L.SPIRAL_C
    r = L.SPIRAL_R_OUT + pad
    return (cx - r, cy - r, cx + r, cy + r)


def gable_roof(mb, F, w, d, zeave, rise, over=1.2, m="Roof_SG_Slate", wall_m="Plaster_SG"):
    """telhado de 2 aguas (cumeeira ao longo do X local) + empenas"""
    tilt = math.atan2(rise, d / 2)
    span = math.hypot(d / 2 + over, rise * (d / 2 + over) / (d / 2))
    for s in (-1, 1):
        mb.box((w + 2 * over, span, 0.7), F.p(0, s * (d / 4 + over / 2) * 0.98, zeave + rise / 2 - 0.1),
               (-s * tilt, 0, F.a), m, 0.05)
    for s in (-1, 1):
        mb.tri(F.p(s * w / 2, -d / 2, zeave), F.p(s * w / 2, d / 2, zeave), F.p(s * w / 2, 0, zeave + rise), wall_m)


def tower(mb, x, y, r, z0, z1, m, roof_m, spire_h, n=8, cap_m="Stone_SG_Trim"):
    mb.cyl(r, z1 - z0, (x, y, (z0 + z1) / 2), m=m, n=n, bevel=0.0)
    mb.cyl(r + 0.8, 1.4, (x, y, z1 + 0.7), m=cap_m, n=n, bevel=0.0)
    SL.spire(mb, (x, y), r + 1.2, z1 + 1.4, spire_h, roof_m, n=n)


def ring_boxes(mb, c, r0, r1, z0, z1, m, n=24, skip=None, col=None):
    """anel (parede cilindrica) em n caixas; skip(ang_deg) -> [(z0, z1)] trechos a manter nesse setor"""
    for k in range(n):
        a = 360.0 * (k + 0.5) / n
        spans = skip(a) if skip else [(z0, z1)]
        m_ = math.radians(a)
        rm = (r0 + r1) / 2
        chord = 2 * r1 * math.sin(math.pi / n) + 0.1
        for za, zb in spans:
            if zb - za < 0.05:
                continue
            loc = (c[0] + rm * math.cos(m_), c[1] + rm * math.sin(m_), (za + zb) / 2)
            mb.box((r1 - r0, chord, zb - za), loc, (0, 0, m_), m, 0.0)
            if col:
                col_box(col, (r1 - r0, chord, zb - za), loc, (0, 0, m_))


# ------------------------------------------------------------------ terreno: patamares, ombro, massa inferior, colunas
def terrain():
    rng = random.Random(11)
    mt = MB("SG_Ter_Blockout_Terraces", "02_TERRAIN", rng, detail="far", floor=-999)
    top = {"P1": "Stone_Paving_SG", "P2": "Grass_SG", "P3": "Stone_Paving_SG", "EntryHigh": "Stone_Paving_SG",
           "EntryLow": "Stone_Paving_SG", "Summon": "Stone_Paving_SG"}
    for nm, poly, z, pr in L.floors():
        side = "Cliff_Rock_SG" if nm in ("Summon", "EntryLow", "EntryHigh") else "Stone_SG_Block"
        if nm == "P3":
            # laje do P3 com o POCO da escada caracol vazado + saia ate 32,5 com o SALAO SOMBRIO vazado
            prism(mt, keyhole(poly, shaft_hole()), z - 10.0, z, side, top_m=top[nm])
            mt.prism(keyhole(poly, cave_hole()), 32.5, z - 10.0, side)
            continue
        z0 = {"P2": 32.5, "Summon": z - 16.0}.get(nm, z - 10.0)
        prism(mt, SL.ccw(poly), z0, z, side, top_m=top[nm])
    mt.finish()
    rim = SL.rim()
    cx = sum(p[0] for p in rim) / len(rim)
    cy = sum(p[1] for p in rim) / len(rim)
    # ombro (terreno bravo entre os patamares e a borda): rocha baixa com topo de grama (salao sombrio vazado)
    ms = MB("SG_Ter_Blockout_Shoulder", "02_TERRAIN", rng, detail="far", floor=-999)
    prism(ms, keyhole(rim, cave_hole()), 32.5, L.P1 - 2.0, "Cliff_Rock_SG", top_m="Grass_SG")
    # montes de rocha no terreno bravo do topo (cantos do terraco norte): moldura, com colisao
    for x, y, r, h in [(138.0, 300.0, 12.0, 70.0), (-146.0, 262.0, 8.0, 64.0), (150.0, 200.0, 8.0, 62.0)]:
        poly = SL.blob_poly(x, y, r, 10, rng, 0.2)
        ms.prism(SL.ccw(poly), 50.0, h - 6.0, "Cliff_Rock_SG")
        ms.prism(SL.ccw(SL.blob_poly(x, y, r * 0.8, 9, rng, 0.2)), h - 6.0, h, "Cliff_Rock_SG_Top")
        ms.prism(SL.ccw(SL.blob_poly(x, y, r * 0.6, 8, rng, 0.2)), h, h + 0.6, "Grass_SG")
        octo_col("SG_TerMound", x, y, r * 0.9, L.P3 - 1.0, h)
    ms.finish()
    # massa inferior: 3 bandas. A de cima (-20 .. 32,5) tem o SALAO SOMBRIO vazado; a do meio (-80 .. -20) ENVOLVE as
    # salas da masmorra (-76 .. -26) sem tampa cruzando; a ponta vai ate -108 (acima do mar em -110)
    mu = MB("SG_Ter_Blockout_Under", "02_TERRAIN", rng, detail="far", floor=-999)
    band1 = [(x * 1.0, y) for x, y in scale_poly(rim[::2], 0.99, (cx, cy))]
    mu.prism(keyhole(band1, cave_hole(3.0)), -20.0, 32.5, "Cliff_Rock_SG")
    mu.prism(SL.ccw(scale_poly(rim[::2], 0.84, (cx, cy))), -80.0, -20.0, "Cliff_Rock_SG_Dark")
    mu.prism(SL.ccw(scale_poly(rim[::3], 0.45, (cx, cy))), -108.0, -80.0, "Cliff_Rock_SG")
    sx, sy = L.SUMMON_C
    for k, (f, z0, z1) in enumerate(((1.0, L.SUM - 30.0, L.SUM - 16.0), (0.7, L.SUM - 52.0, L.SUM - 30.0),
                                     (0.35, L.SUM - 70.0, L.SUM - 52.0))):
        mu.prism(SL.ccw(SL.blob_poly(sx, sy, L.SUMMON_R * f, 12, rng, 0.08)), z0, z1,
                 "Cliff_Rock_SG" if k % 2 == 0 else "Cliff_Rock_SG_Dark")
    mu.finish()
    # colunas de basalto na borda (silhueta vertical)
    mc = MB("SG_Ter_Blockout_Spires", "02_TERRAIN", rng, detail="far", floor=-999)
    for x, y, r, top_z, kind in L.CLIFF_SPIRES:
        z0 = -30.0
        for k in range(5):
            a = rng.uniform(0, 6.28)
            rr = r * rng.uniform(0.25, 0.55)
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            hh = top_z - rng.uniform(0, 18.0)
            mc.cyl(r * rng.uniform(0.35, 0.5), hh - z0, (px, py, (z0 + hh) / 2), m="Cliff_Rock_SG", n=6, bevel=0.0)
            mc.cyl(r * 0.4, 0.8, (px, py, hh + 0.4), m="Cliff_Rock_SG_Top", n=6, bevel=0.0)
        if L.point_in_poly(x, y, L.ISLAND_RIM):
            octo_col("SG_TerSpire", x, y, r * 0.8, 32.5, 32.5 + 20.0)
    mc.finish()


# ------------------------------------------------------------------ entrada: ponte CURVA, escadaria, 2 porticos
def portico(mb, y, z, hw=11.0, h=17.0):
    for s in (-1, 1):
        x = s * hw
        mb.box((4.0, 4.0, 1.2), (x, y, z + 0.6), (0, 0, 0), "Stone_SG_Trim", 0.1)
        mb.box((3.2, 3.2, h), (x, y, z + 1.2 + h / 2), (0, 0, 0), "Stone_SG_Castle", 0.1)
        SL.spire(mb, (x, y), 2.4, z + 1.2 + h, 5.0, "Roof_SG_Navy", n=4)
        col_box("SG_EntPortico", (3.4, 3.4, h + 1.2), (x, y, z + (h + 1.2) / 2))
    mb.box((2 * hw + 3.2, 2.4, 2.0), (0, y, z + h + 0.2), (0, 0, 0), "Stone_SG_Castle", 0.1)


def entry_bridge(y_end=None):
    """ponte de chegada (polilinha da planta) da ancora da Ilha 2 ate y_end (o resto e do sg_entry); pilar no fim do
    arco (marco do meio do caminho)"""
    rng = random.Random(33)
    mb = MB("SG_Ent_BridgeCurve", "18_ENTRY", rng, detail="far", floor=-999)
    pts = list(L.BRIDGE_PATH)
    if y_end is not None:
        cut = [p for p in pts if p[1] <= y_end]
        if cut[-1][1] < y_end:
            cut.append((0.0, y_end))
        pts = cut
    hw = L.DECK_W / 2
    for a, b in zip(pts, pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        ang = math.atan2(dy, dx)
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        mb.box((ln + 0.6, L.DECK_W + 2.4, 2.4), (c[0], c[1], L.DECK - 1.2), (0, 0, ang), "Stone_SG_Block", 0.05)
        for s in (-1, 1):
            q = (c[0] - dy / ln * s * (hw + 0.6), c[1] + dx / ln * s * (hw + 0.6))
            mb.box((ln + 0.6, 1.0, 1.6), (q[0], q[1], L.DECK + 0.8), (0, 0, ang), "Stone_SG_Block", 0.05)
            mb.box((ln + 0.8, 1.3, 0.3), (q[0], q[1], L.DECK + 1.75), (0, 0, ang), "Stone_SG_Trim", 0.0)
    # pilares a cada ~45
    acc = 0.0
    nxt = 30.0
    for a, b in zip(pts, pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        while acc + ln >= nxt:
            t = (nxt - acc) / ln
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            mb.cyl(5.0, 70.0, (p[0], p[1], L.DECK - 37.0), m="Cliff_Rock_SG_Dark", n=8, r2=2.4, bevel=0.0)
            nxt += 45.0
        acc += ln
    # marco no fim do arco (onde a ponte endireita): 2 pilaretes com lanterna
    k = len(L.BRIDGE_PATH) - 2                                # fim do arco
    p, q = L.BRIDGE_PATH[k], L.BRIDGE_PATH[k + 1]
    ang = math.atan2(q[1] - p[1], q[0] - p[0])
    for s in (-1, 1):
        x, y = p[0] - math.sin(ang) * s * (hw + 1.6), p[1] + math.cos(ang) * s * (hw + 1.6)
        mb.box((2.2, 2.2, 9.0), (x, y, L.DECK + 4.5), (0, 0, ang), "Stone_SG_Castle", 0.1)
        mb.box((1.2, 1.2, 1.4), (x, y, L.DECK + 9.7), (0, 0, ang), "Lantern_Glow", 0.0)
    mb.finish()


def entry():
    """blockout completo da entrada (so se o sg_entry nao rodar)"""
    entry_bridge()
    rng = random.Random(31)
    mb = MB("SG_Ent_Blockout", "18_ENTRY", rng, detail="far", floor=-999)
    SL.plan_stair(mb, "Entry")
    portico(mb, L.PORTICO_A_Y, L.DECK)
    portico(mb, L.PORTICO_B_Y, L.P1)
    for rect_, z in ((L.ENTRY_HIGH, L.P1), (L.ENTRY_LOW, L.DECK)):
        x0, y0, x1, y1 = rect_
        for s in (-1, 1):
            SL.vis_parapet(mb, [(s * (x1 + 0.6), y0, z), (s * (x1 + 0.6), y1, z)], h=1.6, w=1.0)
    mb.finish()


# ------------------------------------------------------------------ vila: praca (v3 realocada), ruas, 7 casas VISITAVEIS
def house(mb, mi, spec, idx):
    """casa VISITAVEL (blockout): paredes de 1 com o vao da porta 8 x 11 no meio da frente, piso de madeira, lareira,
    mesa (e balcao na taverna), escada reta ao longo do fundo ate o andar de cima (A/B), laje do andar com guarda no vao
    da escada, forro/telhado. Colisao: paredes (vao), laje, escada (rampa), guarda, lareira/mesa/balcao, forro."""
    nm, tp, x, y, w, d, deg, z = spec
    T = L.HOUSE_TYPES[tp]
    F = Frame(x, y, z, math.radians(deg) - math.pi / 2)            # local +Y = frente
    t = L.HOUSE_WALL
    dw, dh = L.HOUSE_DOOR
    h0 = T["h0"]
    eave = h0 + (1.0 + T["h1"] if T["floors"] == 2 else 0.0)
    area = "SG_VilHouse%s" % nm
    iw, idp = w - 2 * t, d - 2 * t                                  # interior
    # soco + paredes (4 lados; frente com o vao)
    mb.box((w + 0.4, d + 0.4, 1.2), F.p(0, 0, 0.4), F.r(), "Stone_SG_Block", 0.05)
    for sx, sy, lx, ly in ((0, -d / 2 + t / 2, w, t), (-w / 2 + t / 2, 0, t, d), (w / 2 - t / 2, 0, t, d)):
        mb.box((lx, ly, eave), F.p(sx, sy, eave / 2), F.r(), "Plaster_SG", 0.02)
        col_box(area, (lx, ly, eave + 0.5), F.p(sx, sy, eave / 2 - 0.25), F.r())
    for s in (-1, 1):
        seg = (w - dw) / 2
        cxs = s * (dw / 2 + seg / 2)
        mb.box((seg, t, eave), F.p(cxs, d / 2 - t / 2, eave / 2), F.r(), "Plaster_SG", 0.02)
        col_box(area, (seg, t, eave + 0.5), F.p(cxs, d / 2 - t / 2, eave / 2 - 0.25), F.r())
    mb.box((dw, t, eave - dh), F.p(0, d / 2 - t / 2, dh + (eave - dh) / 2), F.r(), "Plaster_SG", 0.02)
    col_box(area, (dw, t, eave - dh), F.p(0, d / 2 - t / 2, dh + (eave - dh) / 2), F.r())
    # enxaimel da frente: moldura da porta, frechal e cunhais
    for s in (-1, 1):
        mb.box((0.6, 0.5, dh + 0.6), F.p(s * (dw / 2 + 0.3), d / 2 + 0.05, (dh + 0.6) / 2), F.r(), "Wood_SG_Dark", 0.0)
        mb.box((0.6, d + 0.3, eave), F.p(s * (w / 2 - 0.1), 0, eave / 2), F.r(), "Wood_SG_Dark", 0.0)
    mb.box((dw + 1.8, 0.5, 0.8), F.p(0, d / 2 + 0.05, dh + 0.4), F.r(), "Wood_SG_Dark", 0.0)
    mb.box((w + 0.3, d + 0.3, 0.6), F.p(0, 0, eave - 0.3), F.r(), "Wood_SG_Dark", 0.0)
    # folha da porta ABERTA (presa na parede de dentro, lado esquerdo)
    mb.box((0.35, dw * 0.55, dh - 0.4), F.p(-dw / 2 - 0.4, d / 2 - t - dw * 0.3, (dh - 0.4) / 2 + 0.1), F.r(),
           "Wood_SG_Dark", 0.0)
    # janelas quentes (frente e laterais, 1 por andar)
    for zz in [4.5] + ([h0 + 5.5] if T["floors"] == 2 else []):
        for s in (-1, 1):
            mb.box((2.6, 0.3, 3.2), F.p(s * (w / 2 - 5.0), d / 2 + 0.02, zz), F.r(), WIN, 0.0)
            mb.box((0.3, 2.6, 3.2), F.p(s * (w / 2 + 0.02), -d / 4, zz), F.r(), WIN, 0.0)
    # piso de madeira do terreo (visual; a colisao e a do patamar)
    mb.box((iw, idp, 0.12), F.p(0, 0, 0.06), F.r(), "Wood_SG_Dark", 0.0)
    # lareira na parede lateral esquerda (x-) + chamine ate o telhado
    fx = -w / 2 + t + 1.2
    mb.box((2.4, 6.0, 7.0), F.p(fx, 1.0, 3.5), F.r(), "Stone_SG_Block", 0.05)
    mb.box((0.4, 3.2, 2.4), F.p(fx + 1.25, 1.0, 1.4), F.r(), "SG_LampCore_Glow", 0.0)
    col_box(area, (2.4, 6.0, 7.0), F.p(fx, 1.0, 3.5), F.r())
    mb.box((2.0, 2.4, 10.0), F.p(fx - 0.2, 1.0, eave + 3.0), F.r(), "Stone_SG_Block", 0.05)
    # mesa (+ balcao na taverna)
    mb.box((6.0, 3.0, 2.6), F.p(2.0, 2.5 if T["stair"] else 0.0, 1.3), F.r(), "Wood_SG_Dark", 0.05)
    col_box(area, (6.0, 3.0, 2.6), F.p(2.0, 2.5 if T["stair"] else 0.0, 1.3), F.r())
    if tp == "B":
        mb.box((12.0, 2.2, 3.6), F.p(8.0, 6.5, 1.8), F.r(), "Wood_SG_Dark", 0.05)
        col_box(area, (12.0, 2.2, 3.6), F.p(8.0, 6.5, 1.8), F.r())
    if T["floors"] == 2:
        # escada reta ao longo da parede do fundo (sobe para +X), largura 6; laje do andar com o vao da escada
        rise = h0 + 1.0
        n = int(math.ceil(rise / 0.83))
        tread = 1.6
        run = n * tread
        sw = 6.0
        xs = -iw / 2 + 2.0
        yb = -idp / 2 + sw / 2
        SL.vis_stairs(mb, F.p(xs, yb, 0.0), F.a, sw, n, rise / n, tread, m="Wood_SG_Dark", side_m="Wood_SG_Dark",
                      stringers=False)
        sg_col.stair_col(area + "Stair", F.p(xs, yb, 0.0), F.a, sw, n, rise / n, tread, guards=False)
        xe = xs + run                                            # topo da escada
        zf = h0 + 1.0
        # laje: tudo menos a faixa da escada (x < xe) no fundo
        slabs = [((-iw / 2, -idp / 2 + sw), (iw / 2, idp / 2)), ((xe, -idp / 2), (iw / 2, -idp / 2 + sw))]
        for (ax, ay), (bx, by) in slabs:
            if bx - ax > 0.3 and by - ay > 0.3:
                c = F.p((ax + bx) / 2, (ay + by) / 2, zf - 0.5)
                mb.box((bx - ax, by - ay, 1.0), c, F.r(), "Wood_SG_Dark", 0.0)
                col_box(area + "Floor", (bx - ax, by - ay, 1.0), c, F.r())
        # guarda no vao da escada (andar de cima) e corrimao
        gy = -idp / 2 + sw + 0.3
        gx0, gx1 = -iw / 2, xe - 1.0
        c = F.p((gx0 + gx1) / 2, gy, zf + 1.6)
        mb.box((gx1 - gx0, 0.3, 0.3), F.p((gx0 + gx1) / 2, gy, zf + 3.0), F.r(), "Wood_SG_Dark", 0.0)
        col_box(area + "Guard", (gx1 - gx0, 0.6, 3.6), F.p((gx0 + gx1) / 2, gy, zf + 1.8), F.r())
        # cama e bau no andar de cima
        mb.box((4.0, 7.0, 1.6), F.p(iw / 2 - 3.0, idp / 2 - 4.5, zf + 0.8), F.r(), "Cloth_SG_Navy", 0.05)
        col_box(area, (4.0, 7.0, 1.6), F.p(iw / 2 - 3.0, idp / 2 - 4.5, zf + 0.8), F.r())
    else:
        mb.box((4.0, 7.0, 1.6), F.p(iw / 2 - 3.0, -idp / 2 + 4.5, 0.8), F.r(), "Cloth_SG_Navy", 0.05)
        col_box(area, (4.0, 7.0, 1.6), F.p(iw / 2 - 3.0, -idp / 2 + 4.5, 0.8), F.r())
    # forro (segura a camera) + telhado
    col_box(area + "Roof", (w, d, 1.0), F.p(0, 0, eave + 0.5), F.r())
    mb.box((iw, idp, 0.4), F.p(0, 0, eave - 0.2), F.r(), "Wood_SG_Dark", 0.0)
    gable_roof(mb, F, w, d, eave, rise=min(14.0, d * 0.55))


def village():
    rng = random.Random(41)
    try:
        import sg_relocate
        sg_relocate.run("sg_village", ("plaza",))           # praca + fonte da v3, mesma medida, transladada
    except Exception:
        import traceback
        traceback.print_exc()
        print("AVISO blockout: praca antiga nao rodou; praca simples")
        mp = MB("SG_Vil_Plaza", "05_VILLAGE", rng, detail="far", floor=-999)
        cx, cy = L.PLAZA_C
        mp.prism(SL.ccw(L.plaza_poly()), L.P1 - 0.2, L.P1 + 0.06, "Stone_SG_Trim")
        mp.cyl(L.FOUNTAIN_R, 2.6, (cx, cy, L.P1 + 1.3), m="Stone_SG_Castle", n=12, bevel=0.0)
        mp.finish()
    ms = MB("SG_Vil_Streets", "05_VILLAGE", rng, detail="far", floor=-999)
    for pts, w, z in L.STREETS:
        ms.prism(SL.ribbon_poly(pts, w / 2), z - 0.2, z + 0.05, "Stone_Paving_SG")
    ms.finish()
    for i, spec in enumerate(L.HOUSES):
        mb = MB("SG_Vil_House%s" % spec[0], "05_VILLAGE", random.Random(4200 + i), detail="far", floor=-999)
        house(mb, i, spec, i)
        mb.finish()
        nm, tp, x, y, w, d, deg, z = spec
        if nm in ("H1", "H2", "H5", "H7"):
            light("L_SGVil_House_%s" % nm, "POINT", (x, y, z + 5.0), 260.0, (1.0, 0.68, 0.40), 0.5)


# ------------------------------------------------------------------ castelo 2x: muralha + portao, nave, torres, coroa
def castle():
    rng = random.Random(51)
    mb = MB("SG_Cas_Blockout", "04_CASTLE", rng, detail="far", floor=-999)
    z = L.P3
    CM, TR, OB = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Obsidian"
    # --- muralha (10 de espessura, topo P3+24) + portao 24 x 32 entre 2 torres R 12 + passagem leste
    wy0, wy1 = L.WALL_Y0, L.WALL_Y1
    gx, gw = L.EAST_WALL_GAP
    gh = L.GATEHOUSE_W / 2
    cuts = [(-gh, gh), (gx - gw / 2, gx + gw / 2)]
    xs = [L.WALL_X[0]] + [c for ab in cuts for c in ab] + [L.WALL_X[1]]
    for a, b in zip(xs[0::2], xs[1::2]):
        mb.box2((a, wy0, z - 8.2), (b, wy1, L.WALL_TOP), "Stone_SG_Block", 0.1)
        n = int((b - a) / 4.0)
        for k in range(n):
            if k % 2 == 0:
                x = a + (k + 0.5) * (b - a) / n
                mb.box((2.0, wy1 - wy0, 2.4), (x, (wy0 + wy1) / 2, L.WALL_TOP + 1.2), (0, 0, 0), "Stone_SG_Block", 0.0)
        col_box2("SG_CasWall", (a, wy0, z - 8.5), (b, wy1, L.WALL_TOP))
    mb.box2((-gh - 1.0, wy0 - 1.0, z + L.GATEHOUSE_H), (gh + 1.0, wy1 + 1.0, L.WALL_TOP + 8.0), CM, 0.1)
    col_box2("SG_CasWall", (-gh - 1.0, wy0 - 1.0, z + L.GATEHOUSE_H), (gh + 1.0, wy1 + 1.0, L.WALL_TOP + 8.0))
    for k in range(7):                                              # dentes da grade levadica recolhida
        x = -gh + 1.5 + k * (2 * gh - 3.0) / 6
        mb.box((0.6, 0.6, 3.0), (x, (wy0 + wy1) / 2, z + L.GATEHOUSE_H - 1.5), (0, 0, 0), "Metal_SG_BlackIron", 0.0)
    for s in (-1, 1):                                               # folhas abertas 12 x 26 contra o intradorso
        mb.box((0.8, 12.0, 26.0), (s * (gh - 0.5), wy1 + 6.0, z + 13.0), (0, 0, 0), "Wood_SG_Dark", 0.0)
    for x, y, r in L.GATEHOUSE_TOWERS:
        tower(mb, x, y, r, z - 8.0, L.GATEHOUSE_TOWER_TOP, CM, "Roof_SG_Navy", 22.0)
        octo_col("SG_CasTower", x, y, r, z - 8.0, L.GATEHOUSE_TOWER_TOP)
    for x in (gx - gw / 2 - 4.6, gx + gw / 2 + 4.6):
        tower(mb, x, -18.0, 4.2, z - 8.0, z + 30.0, CM, "Roof_SG_Navy", 10.0)
        octo_col("SG_CasTower", x, -18.0, 4.2, z - 8.0, z + 30.0)
    # --- nave: face interna = retangulo do salao, parede 5, cornija 152,2; porta 28 x 34 (verga reta)
    hx0, hy0, hx1, hy1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
    t = L.HALL_WALL
    top = L.NAVE_WALL_TOP
    dw, dh = L.HALL_DOOR_W, L.HALL_DOOR_H
    tw, th = L.TRI_ARCH_W, L.TRI_ARCH_H
    mb.box2((hx0 - t, hy0, z - 0.2), (hx0, hy1, top), CM, 0.1)
    mb.box2((hx1, hy0, z - 0.2), (hx1 + t, hy1, top), CM, 0.1)
    mb.box2((hx0 - t, hy0 - t, z - 0.2), (-dw / 2, hy0, top), CM, 0.1)
    mb.box2((dw / 2, hy0 - t, z - 0.2), (hx1 + t, hy0, top), CM, 0.1)
    mb.box2((-dw / 2, hy0 - t, z + dh), (dw / 2, hy0, top), CM, 0.1)
    mb.box2((hx0 - t, hy1, z - 0.2), (-tw / 2, hy1 + t, top), CM, 0.1)          # parede norte com o ARCO TRIUNFAL
    mb.box2((tw / 2, hy1, z - 0.2), (hx1 + t, hy1 + t, top), CM, 0.1)
    mb.box2((-tw / 2, hy1, z + th), (tw / 2, hy1 + t, top), CM, 0.1)
    box_walls_col("SG_CasHall", (hx0, hy0, hx1, hy1), z - 0.5, top, t, doors=[("S", 0.0, dw, dh), ("N", 0.0, tw, th)])
    col_box2("SG_CasHallCeil", (hx0 - t, hy0 - t, L.HALL_CEIL), (hx1 + t, hy1 + t, L.HALL_CEIL + 2.0))
    # PORTAL: timpano ogival (obsidiana) ate 46 sobre a verga + 4 arquivoltas escalonadas (moldura externa 48 x 58)
    yf = hy0 - t
    mb.box((dw, 0.6, 7.0), (0.0, yf - 0.1, z + dh + 3.5), (0, 0, 0), OB, 0.0)
    mb.tri((-dw / 2, yf - 0.45, z + dh + 7.0), (dw / 2, yf - 0.45, z + dh + 7.0), (0.0, yf - 0.45, z + L.HALL_TYMPANUM_H), OB)
    for k in range(4):
        e = 2.5 * (k + 1)
        zt = z + L.HALL_TYMPANUM_H + 3.0 * k
        yy = yf - 0.4 - 0.5 * k
        for s in (-1, 1):
            mb.box((2.5, 1.0, dh + 3.0 * k), (s * (dw / 2 + e - 1.25), yy, z + (dh + 3.0 * k) / 2), (0, 0, 0), TR, 0.05)
            a = (s * (dw / 2 + e - 1.25), yy, z + dh + 3.0 * k)
            b = (0.0, yy, zt)
            mb.beam(a, b, 2.5, 1.0, TR, 0.0)
    # folhas da porta ABERTAS (14 x 34 cada, 100 graus para dentro)
    for s in (-1, 1):
        hxp = s * dw / 2
        ux, uy = s * math.cos(math.radians(80.0)), math.sin(math.radians(80.0))
        mb.box((14.0, 0.8, dh), (hxp + ux * 7.0, hy0 + uy * 7.0, z + dh / 2), (0, 0, math.atan2(uy, ux)), "Wood_SG_Dark", 0.0)
    # empena da fachada + rosacea da lua (vitral) e janelas da nave
    mb.tri((hx0 - t, yf - 0.1, top), (hx1 + t, yf - 0.1, top), (0.0, yf - 0.1, L.NAVE_RIDGE), CM)
    mb.cyl(12.0, 0.6, (0.0, yf - 0.4, z + 118.0), (math.pi / 2, 0, 0), m="Glass_SG_Rose", n=20, bevel=0.0)
    mb.cyl(13.4, 0.5, (0.0, yf - 0.3, z + 118.0), (math.pi / 2, 0, 0), m=TR, n=20, bevel=0.0)
    mb.box((12.0, 0.6, 24.0), (0.0, yf - 0.4, z + 66.0), (0, 0, 0), "Glass_SG_Rose", 0.0)   # janelao sobre o portal
    # contrafortes + janelas altas (8 por lado)
    for y in L.ARCADE_Y:
        for s in (-1, 1):
            x = s * (hx1 + t + 3.5)
            mb.box((7.0, 5.0, top - z - 12.0), (x, y, z + (top - z - 12.0) / 2), (0, 0, 0), CM, 0.1)
            SL.spire(mb, (x, y), 3.0, top - 12.0, 16.0, TR, n=4)
            col_box("SG_CasButtress", (7.0, 5.0, 12.0), (x, y, z + 6.0))
        for s in (-1, 1):
            if y + 11.25 < hy1:
                mb.box((0.6, 10.0, 34.0), (s * (hx1 + t + 0.2), y + 11.25, z + 47.0), (0, 0, 0), "Glass_SG_Rose", 0.0)
    # telhado navy (cumeeira N-S em 228)
    half = hx1 + t + 7.0
    rise = L.NAVE_RIDGE - top
    tilt = math.atan2(rise, half)
    span = math.hypot(half, rise) + 1.0
    for s in (-1, 1):
        mb.box((span, hy1 - hy0 + 2 * t + 2.0, 1.4), (s * half / 2, (hy0 + hy1) / 2, top + rise / 2),
               (0, s * tilt, 0), "Roof_SG_Navy", 0.05)
    mb.box2((hx0, hy0, L.HALL_CEIL), (hx1, hy1, L.HALL_CEIL + 1.0), CM, 0.0)       # teto interno (visual)
    # torres da fachada (R 20, topo 214, agulha 279)
    for x, y, r, tz in L.FRONT_TOWERS:
        tower(mb, x, y, r, z - 10.0, tz, CM, "Roof_SG_Navy", L.FRONT_SPIRE_TOP - tz - 1.4, n=8)
        octo_col("SG_CasTower", x, y, r, z - 1.0, tz)
    # --- base da torre-coroa: presbiterio (40 de largura) + bolso do trono + muro do retabulo com o ARCO SECRETO +
    #     camara do poco da escada caracol (anel do poco e do sg_cave)
    bx0, by0, bx1, by1 = L.CROWN_BASE
    cx0, cy0, cx1, cy1 = L.CHANCEL
    zc = L.CHANCEL_Z
    btop = z + 100.0
    wt = 5.0
    mb.box2((bx0, by1 - wt, z - 0.2), (bx1, by1, btop), CM, 0.1)                   # fundo
    mb.box2((bx0, hy1 + t, z - 0.2), (bx0 + wt, by1 - wt, btop), CM, 0.1)          # lados externos
    mb.box2((bx1 - wt, hy1 + t, z - 0.2), (bx1, by1 - wt, btop), CM, 0.1)
    col_box2("SG_CasCrown", (bx0, by1 - wt, z - 0.5), (bx1, by1, btop))
    col_box2("SG_CasCrown", (bx0, hy1 + t, z - 0.5), (bx0 + wt, by1 - wt, btop))
    col_box2("SG_CasCrown", (bx1 - wt, hy1 + t, z - 0.5), (bx1, by1 - wt, btop))
    ry0, ry1 = L.RETABLE_Y
    # paredes do presbiterio: oeste macica; leste com o BOLSO do trono (x 20 .. 35,5, y 288 .. 300, z 54,6 .. 76,6)
    px0, py0, px1, py1, pz0, pz1 = L.THRONE_POCKET
    mb.box2((bx0 + wt, hy1 + t, z - 0.2), (cx0, ry1, btop), CM, 0.1)
    col_box2("SG_CasChancel", (bx0 + wt, hy1 + t, z - 0.5), (cx0, ry1, btop))
    for p0, p1 in (((cx1, hy1 + t, z - 0.2), (bx1 - wt, py0, btop)), ((cx1, py1, z - 0.2), (bx1 - wt, ry1, btop)),
                   ((cx1, py0, z - 0.2), (bx1 - wt, py1, pz0)), ((cx1, py0, pz1), (bx1 - wt, py1, btop)),
                   ((px1, py0, pz0), (bx1 - wt, py1, pz1))):
        mb.box2(p0, p1, CM, 0.05)
        col_box2("SG_CasChancel", (p0[0], p0[1], max(p0[2], z - 0.5)), p1)
    mb.box2((px0 + 0.02, py0 + 0.02, pz0), (px1, py1 - 0.02, pz0 + 0.1), "Stone_SG_Obsidian", 0.0)    # fundo escuro do bolso
    # muro do retabulo (y 300 .. 308) com o arco secreto 12 x 18 no eixo
    aw, ah = L.SECRET_ARCH
    for p0, p1 in (((cx0, ry0, z - 0.2), (-aw / 2, ry1, btop)), ((aw / 2, ry0, z - 0.2), (cx1, ry1, btop)),
                   ((-aw / 2, ry0, zc + ah), (aw / 2, ry1, btop))):
        mb.box2(p0, p1, CM, 0.05)
        col_box2("SG_CasRetable", (p0[0], p0[1], max(p0[2], z - 0.5)), p1)
    mb.box2((-aw / 2 - 1.2, ry0 - 0.5, zc), (-aw / 2, ry0 + 0.2, zc + ah + 1.2), TR, 0.0)
    mb.box2((aw / 2, ry0 - 0.5, zc), (aw / 2 + 1.2, ry0 + 0.2, zc + ah + 1.2), TR, 0.0)
    mb.box2((-aw / 2 - 1.2, ry0 - 0.5, zc + ah), (aw / 2 + 1.2, ry0 + 0.2, zc + ah + 1.2), TR, 0.0)
    # teto do presbiterio e da camara do poco
    mb.box2((cx0, hy1 + t, z + L.TRI_ARCH_H), (cx1, ry0, z + L.TRI_ARCH_H + 1.5), CM, 0.0)
    mb.box2((bx0 + wt, ry1, z + 36.0), (bx1 - wt, by1 - wt, z + 37.5), CM, 0.0)
    col_box2("SG_CasHallCeil", (cx0, hy1 + t, z + L.TRI_ARCH_H), (cx1, ry0, z + L.TRI_ARCH_H + 1.5))
    col_box2("SG_CasHallCeil", (bx0 + wt, ry1, z + 36.0), (bx1 - wt, by1 - wt, z + 37.5))
    # piso da camara do poco em volta do anel (acima do P3; o patamar de topo e do sg_col)
    for p0, p1 in (((bx0 + wt, ry1, z), (-L.SPIRAL_R_OUT, by1 - wt, zc)), ((L.SPIRAL_R_OUT, ry1, z), (bx1 - wt, by1 - wt, zc))):
        mb.box2(p0, p1, "Stone_SG_Floor", 0.0)
    # fuste octogonal da coroa sobre a base (R 30, topo 311) + agulha 376 + pinaculos
    x, y, r, ctop = L.CROWN_TOWER
    mb.cyl(r, ctop - btop, (x, y, (btop + ctop) / 2), m=CM, n=8, bevel=0.0)
    mb.box2((bx0, hy1 + t, btop), (bx1, by1, btop + 3.0), TR, 0.0)
    mb.cyl(r + 1.6, 3.0, (x, y, ctop + 1.5), m=TR, n=8, bevel=0.0)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        SL.spire(mb, (x + (r - 1.5) * math.cos(a), y + (r - 1.5) * math.sin(a)), 3.0, ctop + 3.0, 24.0, "Roof_SG_Navy", n=4)
    SL.spire(mb, (x, y), r * 0.75, ctop + 3.0, L.CROWN_SPIRE_TOP - ctop - 3.0, "Roof_SG_Navy", n=8)
    mb.cyl(5.0, 0.8, (x, y - r * 0.95, ctop - 30.0), (math.pi / 2, 0, 0), m="SG_VioletSoft_Glow", n=12, bevel=0.0)
    mb.finish()
    light("L_SGCas_Door", "POINT", (0.0, yf - 4.0, z + 10.0), 900.0, (1.0, 0.72, 0.45), 0.6)
    light("L_SGCas_Rose", "POINT", (0.0, yf - 6.0, z + 118.0), 700.0, (0.62, 0.45, 1.0), 0.6)
    light("L_SGCas_Gate", "POINT", (0.0, wy0 - 4.0, z + 12.0), 500.0, (1.0, 0.72, 0.45), 0.5)


# ------------------------------------------------------------------ Mining Hall 2x: piso, arcada, lustres, presbiterio, TRONO
def hall():
    rng = random.Random(61)
    mb = MB("SG_Hall_Blockout", "03_MINING_HALL", rng, detail="far", floor=-999)
    z = L.HALL
    hx0, hy0, hx1, hy1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
    mb.box2((hx0, hy0, z - 0.2), (hx1, hy1, z + 0.04), "Stone_SG_Floor", 0.0)
    x0, y0, x1, y1 = L.MINE_RECT
    for a, b in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        mb.beam((a[0], a[1], z + 0.08), (b[0], b[1], z + 0.08), 0.8, 0.08, "Stone_SG_Trim", 0.0)
    # ARCADA: 8 pilares por lado (4 x 6) entre a nave central (128) e as naves laterais (24); arcos + parede alta
    pw, pd = L.ARCADE_PIER
    for s in (-1, 1):
        x = s * L.ARCADE_X
        for y in L.ARCADE_Y:
            mb.box((pw, pd, 48.0), (x, y, z + 24.0), (0, 0, 0), "Stone_SG_Castle", 0.1)
            mb.box((pw + 1.6, pd + 1.6, 1.4), (x, y, z + 0.7), (0, 0, 0), "Stone_SG_Trim", 0.05)
            col_box("SG_HallPier", (pw, pd, 14.0), (x, y, z + 7.0))
        mb.box2((x - pw / 2, L.ARCADE_Y[0] - pd / 2, z + 48.0), (x + pw / 2, L.ARCADE_Y[-1] + pd / 2, L.HALL_CEIL),
                "Stone_SG_Castle", 0.0)
        for ya, yb in zip(L.ARCADE_Y, L.ARCADE_Y[1:]):
            mb.beam((x, ya + pd / 2, z + 38.0), (x, (ya + yb) / 2, z + 47.0), pw, 2.0, "Stone_SG_Trim", 0.0)
            mb.beam((x, (ya + yb) / 2, z + 47.0), (x, yb - pd / 2, z + 38.0), pw, 2.0, "Stone_SG_Trim", 0.0)
        # capelas/nichos nas naves laterais (fundo escuro recuado)
        for y in L.ARCADE_Y[:-1]:
            mb.box((0.4, 10.0, 14.0), (s * (hx1 - 0.2), y + 11.25, z + 9.0), (0, 0, 0), "Stone_SG_Obsidian", 0.0)
    # lustres altos (sem colisao) + luz
    for i, (lx, ly) in enumerate(((-28.0, 110.0), (28.0, 110.0), (-28.0, 186.0), (28.0, 186.0))):
        mb.cyl(4.0, 0.8, (lx, ly, z + 40.0), m="Metal_SG_Iron", n=10, bevel=0.0)
        mb.cyl(3.2, 0.6, (lx, ly, z + 40.8), m="Lantern_Glow", n=10, bevel=0.0)
        mb.rod((lx, ly, z + 40.8), (lx, ly, L.HALL_CEIL), 0.2, "Metal_SG_Iron", 4)
        light("L_SGHall_Chandelier_%d" % i, "POINT", (lx, ly, z + 36.0), 5200.0, (1.0, 0.76, 0.5), 1.5)
    light("L_SGHall_Moon", "POINT", (0.0, hy1 - 8.0, z + 70.0), 3000.0, (0.6, 0.7, 1.0), 2.0)
    # rosacea da lua sobre o arco triunfal (face da nave)
    mb.cyl(14.0, 0.6, (0.0, hy1 - 0.3, z + 76.0), (math.pi / 2, 0, 0), m="Glass_SG_Rose", n=20, bevel=0.0)
    # presbiterio: degraus (visual), piso de marmore negro, dorsal atras do trono
    (fx, fy), w, n, tread = L.CHANCEL_STEPS
    SL.vis_stairs(mb, (fx, fy, z), math.pi / 2, w, n, (L.CHANCEL_Z - z) / n, tread, m="Stone_SG_MarbleBlack",
                  side_m="Stone_SG_Obsidian", stringers=False)
    cx0, cy0, cx1, cy1 = L.CHANCEL
    mb.box2((cx0, fy + n * tread, L.CHANCEL_Z - 0.2), (cx1, cy1, L.CHANCEL_Z + 0.04), "Stone_SG_MarbleBlack", 0.0)
    mb.box2((-L.SECRET_ARCH[0] / 2, cy1, L.CHANCEL_Z - 0.2), (L.SECRET_ARCH[0] / 2, L.RETABLE_Y[1], L.CHANCEL_Z + 0.04),
            "Stone_SG_MarbleBlack", 0.0)
    for k in range(2):                                               # tocheiros
        s = -1 if k == 0 else 1
        mb.cyl(0.6, 7.0, (s * 12.0, L.THRONE_REST[1] - 6.0, L.CHANCEL_Z + 3.5), m="Metal_SG_BlackIron", n=6, bevel=0.0)
        mb.cyl(1.0, 0.8, (s * 12.0, L.THRONE_REST[1] - 6.0, L.CHANCEL_Z + 7.2), m="Lantern_Glow", n=8, bevel=0.0)
    mb.finish()
    light("L_SGHall_Throne", "POINT", (0.0, L.THRONE_REST[1] - 14.0, L.CHANCEL_Z + 10.0), 2400.0, (0.62, 0.40, 1.0), 2.5)
    throne()


def throne():
    """TRONO MOVEL (objeto proprio SG_Hall_ThroneMov + colisao COL_SGHallThroneMov): o TronoService desliza as duas
    juntas de THRONE_Rest para THRONE_Park (27,5 para leste, 3 s). Aqui: pose de REPOUSO, tapando o arco secreto."""
    tx, ty = L.THRONE_REST
    z = L.CHANCEL_Z
    w, d, h = L.THRONE_SIZE
    mb = MB("SG_Hall_ThroneMov", "03_MINING_HALL", random.Random(62), detail="far", floor=-999)
    mb.box((w, d, 2.4), (tx, ty, z + 1.2), (0, 0, 0), "Stone_SG_Obsidian", 0.1)            # soco
    mb.box((w - 3.0, d - 2.0, 3.6), (tx, ty - 0.5, z + 4.2), (0, 0, 0), "Stone_SG_MarbleBlack", 0.1)  # assento
    mb.box((w - 3.0, d - 3.0, 0.8), (tx, ty - 1.0, z + 6.4), (0, 0, 0), "Cloth_SG_Purple", 0.05)   # almofada
    for s in (-1, 1):                                                                        # bracos
        mb.box((1.6, d - 2.0, 5.0), (tx + s * (w / 2 - 0.8), ty - 0.5, z + 7.4), (0, 0, 0), "Stone_SG_Obsidian", 0.1)
    mb.box((w - 1.0, 2.4, h - 2.4), (tx, ty + d / 2 - 1.2, z + 2.4 + (h - 2.4) / 2), (0, 0, 0), "Stone_SG_Obsidian", 0.1)
    mb.box((w - 4.0, 0.6, h - 8.0), (tx, ty + d / 2 - 2.6, z + 8.0 + (h - 8.0) / 2 - 1.0), (0, 0, 0), "Cloth_SG_Navy", 0.0)
    mb.box((w * 0.35, 0.8, 3.0), (tx, ty + d / 2 - 1.2, z + h + 1.2), (0, 0, 0), "Metal_SG_Silver", 0.05)  # crescente
    ob = mb.finish()
    col_box("SGHallThroneMov", (w, d, h), (tx, ty, z + h / 2))
    return ob


# ------------------------------------------------------------------ SALAO SOMBRIO (zona nova 'cave'): a bat-caverna
def cave():
    rng = random.Random(71)
    C = "17_DUNGEON"
    RK, RKD = "Stone_SGCaveRock", "Cliff_Rock_SG_Dark"
    x0, y0, x1, y1 = L.CAVE
    zf, zt = L.CAVE_FLOOR, L.CAVE_TOP
    mb = MB("SG_Cave_Shell", C, rng, detail="far", floor=-999)
    # casca: paredes (face interna = retangulo do salao) e abobada com o POCO vazado; piso em 2 pedacos + fundo do rio
    wt = 2.0
    mb.box2((x0 - wt, y0 - wt, zf - 4.0), (x0, y1 + wt, zt + 1.0), RK, 0.0)
    mb.box2((x1, y0 - wt, zf - 4.0), (x1 + wt, y1 + wt, zt + 1.0), RK, 0.0)
    mb.box2((x0, y0 - wt, zf - 4.0), (x1, y0, zt + 1.0), RK, 0.0)
    mb.box2((x0, y1, zf - 4.0), (x1, y1 + wt, zt + 1.0), RK, 0.0)
    mb.prism(keyhole(SL.ccw([(x0 - wt, y0 - wt), (x1 + wt, y0 - wt), (x1 + wt, y1 + wt), (x0 - wt, y1 + wt)]),
                     shaft_hole(-L.SPIRAL_R_OUT + L.SPIRAL_R_IN + 0.3)), zt, zt + 1.0, RK)
    box_walls_col("SG_CaveWall", (x0, y0, x1, y1), zf - 1.0, zt, wt)
    sh = shaft_hole(-L.SPIRAL_R_OUT + L.SPIRAL_R_IN)
    for p0, p1 in (((x0, y0, zt), (x1, sh[1], zt + 1.0)), ((x0, sh[3], zt), (x1, y1, zt + 1.0)),
                   ((x0, sh[1], zt), (sh[0], sh[3], zt + 1.0)), ((sh[2], sh[1], zt), (x1, sh[3], zt + 1.0))):
        col_box2("SG_CaveCeil", p0, p1)
    px0, py0, px1, py1, plev, pbot = L.CAVE_POOL
    mb.box2((x0, y0, zf - 4.0), (x1, py0, zf), RKD, 0.0)
    mb.box2((x0, py1, zf - 4.0), (x1, y1, zf), RKD, 0.0)
    mb.box2((px0, py0, pbot - 1.0), (px1, py1, pbot), "Stone_SG_Obsidian", 0.0)
    for a, b in ((x0, px0), (px1, x1)):
        mb.box2((a, py0, zf - 4.0), (b, py1, zf), RKD, 0.0)
    bw = L.CAVE_POOL_BRIDGE_W / 2
    mb.box2((-bw, py0 - 1.0, zf - 2.0), (bw, py1 + 1.0, zf), "Stone_SG_Block", 0.05)
    for s in (-1, 1):
        SL.vis_parapet(mb, [(s * (bw + 0.5), py0 - 1.0, zf), (s * (bw + 0.5), py1 + 1.0, zf)], h=1.4, w=1.0)
    # pedra bruta: colunas de basalto nas paredes, estalagmites junto das paredes e estalactites no teto
    for k in range(26):
        side = k % 4
        t = (k // 4 + 0.5) / 7.0
        if side < 2:
            px = x0 + 3.0 if side == 0 else x1 - 3.0
            py = y0 + 8.0 + t * (y1 - y0 - 16.0)
        else:
            py = y0 + 3.0 if side == 2 else y1 - 3.0
            px = x0 + 14.0 + t * (x1 - x0 - 28.0)
            if side == 2 and abs(px) < 30.0:
                continue
        hh = rng.uniform(16.0, 34.0)
        mb.cyl(rng.uniform(2.2, 3.6), hh, (px, py, zf + hh / 2), m=RK, n=6, bevel=0.0)
    for k in range(44):
        px = x0 + 8.0 + (k % 11) * (x1 - x0 - 16.0) / 10.0 + rng.uniform(-3.0, 3.0)
        py = y0 + 10.0 + (k // 11) * (y1 - y0 - 60.0) / 3.0 + rng.uniform(-4.0, 4.0)
        if math.hypot(px - L.SPIRAL_C[0], py - L.SPIRAL_C[1]) < L.SPIRAL_R_OUT + 6.0:
            continue
        ln = rng.uniform(6.0, 14.0)
        mb.cyl(rng.uniform(1.4, 2.6), ln, (px, py, zt - ln / 2), m=RK, n=6, r2=0.2, bevel=0.0)
    mb.finish()
    # POCO da escada caracol (anel R 14..16 de -12 ate 74,6, aberto no sul: saida da galeria e arco secreto),
    # nucleo e os 60 degraus em cunha (a colisao e do sg_col)
    ms = MB("SG_Cave_Spiral", C, random.Random(72), detail="far", floor=-999)
    cx, cy = L.SPIRAL_C
    aw = math.degrees(math.asin((L.SECRET_ARCH[0] / 2 + 0.2) / L.SPIRAL_R_IN))
    zb, ztp = L.SPIRAL_BOT_Z, L.SPIRAL_TOP_Z

    def keep(a):
        if abs((a - 270.0 + 180.0) % 360.0 - 180.0) < aw:
            return [(zf, zb), (zb + L.SECRET_ARCH[1], ztp), (ztp + L.SECRET_ARCH[1], ztp + 20.0)]
        return [(zf, ztp + 20.0)]
    ring_boxes(ms, (cx, cy), L.SPIRAL_R_IN, L.SPIRAL_R_IN + 2.0, zf, ztp + 20.0, "Stone_SG_Castle", 24, keep)
    ms.cyl(L.SPIRAL_R_NEWEL, ztp + 20.0 - zf, (cx, cy, (zf + ztp + 20.0) / 2), m="Stone_SG_Trim", n=12, bevel=0.0)
    r0, r1 = L.SPIRAL_R_NEWEL, L.SPIRAL_R_STEP
    for i in range(L.SPIRAL_N):
        a0, a1 = math.radians(L.stair_angle(i)), math.radians(L.stair_angle(i + 1))
        ztop = ztp - L.SPIRAL_RISE * i
        pts = [(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0)), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0)),
               (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1)), (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1))]
        ms.prism(SL.ccw(pts), ztop - 1.2, ztop, "Stone_SG_Block")
    for a0d, a1d, zz in ((L.SPIRAL_LANDING[0], L.SPIRAL_LANDING[1], ztp), (L.SPIRAL_A1, L.SPIRAL_A1 + 45.0, zb)):
        k = 6
        for j in range(k):
            a0 = math.radians(a0d + (a1d - a0d) * j / k)
            a1 = math.radians(a0d + (a1d - a0d) * (j + 1) / k)
            pts = [(cx + r0 * math.cos(a0), cy + r0 * math.sin(a0)), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0)),
                   (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1)), (cx + r0 * math.cos(a1), cy + r0 * math.sin(a1))]
            ms.prism(SL.ccw(pts), zz - 1.0, zz, "Stone_SG_Floor")
    ms.box2((-6.0, cy - L.SPIRAL_R_OUT - 4.0, zb - 1.5), (6.0, cy - L.SPIRAL_R_IN + 4.0, zb), "Stone_SG_Floor", 0.0)
    ms.finish()
    # galeria, escadaria, passarelas e ponte suspensa (visual; colisao e do sg_col)
    mg = MB("SG_Cave_Gallery", C, random.Random(73), detail="far", floor=-999)
    zg = L.CAVE_GALLERY_Z
    gx0, gy0, gx1, gy1 = L.CAVE_GALLERY
    gy1 = cy - L.SPIRAL_R_OUT
    mg.box2((gx0, gy0, zg - 1.5), (gx1, gy1, zg), "Stone_SG_Block", 0.0)
    sw = L.CAVE_STAIR_W / 2 + 0.6
    cw = list(L.CAVE_CATWALKS)
    SL.vis_fence(mg, [(cw[0][2], gy0, zg), (-sw, gy0, zg)], h=3.0)
    SL.vis_fence(mg, [(sw, gy0, zg), (cw[1][0], gy0, zg)], h=3.0)
    for nm, foot, n, rise, tread in L.CAVE_STAIRS:
        SL.vis_stairs(mg, foot, math.pi / 2, L.CAVE_STAIR_W, n, rise, tread, m="Stone_SG_Block",
                      side_m="Stone_SG_Castle")
    lx0, ly0, lx1, ly1, lz = L.CAVE_LANDING
    mg.box2((lx0, ly0, lz - 1.5), (lx1, ly1, lz), "Stone_SG_Block", 0.0)
    hx0, hy0, hx1, hy1 = L.CAVE_HANGING_BRIDGE
    for cx0_, cy0_, cx1_, cy1_ in cw:
        mg.box2((cx0_, cy0_, zg - 1.0), (cx1_, gy0, zg), "Metal_SG_BlackIron", 0.0)
        inner = cx1_ if cx0_ < 0 else cx0_
        SL.vis_fence(mg, [(inner, cy0_, zg), (inner, hy0, zg)], h=3.0)
        SL.vis_fence(mg, [(inner, hy1, zg), (inner, gy0, zg)], h=3.0)
    mg.box2((hx0, hy0, zg - 1.0), (hx1, hy1, zg), "Wood_SG_Dark", 0.0)
    for yy in (hy0, hy1):
        SL.vis_fence(mg, [(hx0, yy, zg), (hx1, yy, zg)], h=3.0)
    for xx in (-40.0, -60.0, 40.0, 60.0):                           # estandartes rasgados pendurados na ponte
        mg.box((5.0, 0.3, 11.0), (xx, (hy0 + hy1) / 2, zg - 6.5), (0, 0, 0), "Cloth_SG_Purple", 0.0)
        mg.tri((xx - 2.5, (hy0 + hy1) / 2, zg - 12.0), (xx + 2.5, (hy0 + hy1) / 2, zg - 12.0),
               (xx + 0.8, (hy0 + hy1) / 2, zg - 14.5), "Cloth_SG_Purple")
    mg.finish()
    # portal da masmorra no fundo sul: estrado, anel de basalto, vortice e a placa da UI
    mp = MB("SG_Cave_Portal", C, random.Random(74), detail="far", floor=-999)
    dx0, dy0, dx1, dy1, dz = L.CAVE_DAIS
    mp.box2((dx0, dy0, zf - 0.5), (dx1, dy1, dz), "Stone_SG_Obsidian", 0.05)
    SL.vis_stairs(mp, (0.0, dy1 + 3.6, zf), -math.pi / 2, dx1 - dx0, 2, (dz - zf) / 2, 1.8, m="Stone_SG_Obsidian",
                  side_m="Stone_SG_Obsidian", stringers=False)
    px, py = L.CAVE_PORTAL
    R = L.CAVE_PORTAL_R
    zc = dz + R
    for k in range(20):
        a = 2 * math.pi * (k + 0.5) / 20
        mp.box((2.6, 3.0, 2 * (R + 1.3) * math.sin(math.pi / 20) + 0.2),
               (px + (R + 1.3) * math.cos(a), py, zc + (R + 1.3) * math.sin(a)), (0, -a, 0), "Cliff_Rock_SG_Dark", 0.0)
    mp.cyl(R - 0.4, 0.4, (px, py, zc), (math.pi / 2, 0, 0), m="SG_CaveVoid_Glow", n=24, bevel=0.0)
    mp.cyl(R * 0.55, 0.3, (px, py - 0.3, zc), (math.pi / 2, 0, 0), m="SG_Violet_Glow", n=16, bevel=0.0)
    mp.box((22.0, 0.8, 6.0), (px, py - 1.0, dz + 2 * R + 6.0), (0, 0, 0), "Stone_SG_Obsidian", 0.05)
    col_box("SG_CavePortal", (2 * R + 6.0, 3.0, 2 * R + 4.0), (px, py, dz + R + 2.0))
    for k, (cxr, czr) in enumerate(((-24.0, 10.0), (-30.0, 22.0), (24.0, 12.0), (32.0, 24.0), (-14.0, 30.0), (16.0, 32.0))):
        base = (cxr, y0 + 0.6, czr)
        mp.cyl(1.2, 5.0, base, (math.radians(70.0), 0, math.radians(20.0 * (1 if k % 2 else -1))), m="Crystal_SGCave",
               n=6, r2=0.9, bevel=0.0)
        mp.cyl(0.9, 2.4, (base[0], base[1] + 2.6, base[2] + 1.0), (math.radians(70.0), 0, 0), m="SG_Crystal_Glow",
               n=6, r2=0.1, bevel=0.0)
    mp.finish()
    # forja/oficina secreta (oeste) e sala do mapa (leste)
    mf = MB("SG_Cave_Workshops", C, random.Random(75), detail="far", floor=-999)
    fx0, fy0, fx1, fy1 = L.CAVE_FORGE
    mf.box2((fx0, fy0 + 20.0, zf), (fx0 + 10.0, fy0 + 40.0, zf + 9.0), "Stone_SG_Block", 0.05)      # fornalha
    mf.box2((fx0 + 10.0, fy0 + 26.0, zf + 1.5), (fx0 + 10.3, fy0 + 34.0, zf + 5.0), "SG_LampCore_Glow", 0.0)
    mf.box2((fx0 + 2.0, fy0 + 25.0, zf + 9.0), (fx0 + 8.0, fy0 + 35.0, zt), "Stone_SG_Block", 0.0)   # chamine
    col_box2("SG_CaveForge", (fx0, fy0 + 20.0, zf - 0.5), (fx0 + 10.0, fy0 + 40.0, zf + 9.0))
    mf.box((3.0, 1.6, 3.2), (fx0 + 20.0, fy0 + 30.0, zf + 1.6), (0, 0, 0), "Metal_SG_BlackIron", 0.05)   # bigorna
    col_box("SG_CaveForge", (3.0, 1.6, 3.2), (fx0 + 20.0, fy0 + 30.0, zf + 1.6))
    for k in range(3):                                             # cabides de armas
        mf.box((0.6, 8.0, 7.0), (fx0 + 1.0, fy0 + 4.0 + k * 9.0 if k < 2 else fy0 + 50.0, zf + 3.5), (0, 0, 0),
               "Wood_SG_Dark", 0.0)
    mx0, my0, mx1, my1 = L.CAVE_MAPROOM
    mf.box2((mx0 + 10.0, my0 + 20.0, zf), (mx0 + 26.0, my0 + 32.0, zf + 3.2), "Wood_SG_Dark", 0.05)   # mesa do mapa
    mf.box2((mx0 + 12.0, my0 + 22.0, zf + 3.2), (mx0 + 24.0, my0 + 30.0, zf + 4.0), "Grass_SG", 0.0)   # maquete
    col_box2("SG_CaveMap", (mx0 + 10.0, my0 + 20.0, zf - 0.5), (mx0 + 26.0, my0 + 32.0, zf + 3.2))
    for k in range(3):                                             # armarios de reliquias
        mf.box2((mx1 - 2.0, my0 + 6.0 + k * 18.0, zf), (mx1, my0 + 16.0 + k * 18.0, zf + 10.0), "Wood_SG_Dark", 0.05)
    mf.box((4.0, 0.6, 3.0), (72.0, L.CAVE_POOL[3] + 1.5, zt - 6.0), (0, 0, 0), "Stone_SG_Block", 0.05)   # fenda da queda
    mf.finish()
    light("L_SGCave_Portal", "POINT", (px, py + 8.0, zc), 4200.0, (0.62, 0.40, 1.0), 3.0)
    light("L_SGCave_Forge", "POINT", (fx0 + 14.0, fy0 + 30.0, zf + 6.0), 2600.0, (1.0, 0.55, 0.25), 2.0)
    light("L_SGCave_Map", "POINT", (mx0 + 18.0, my0 + 26.0, zf + 10.0), 1500.0, (1.0, 0.72, 0.45), 1.5)
    light("L_SGCave_CrystalW", "POINT", (-28.0, y0 + 6.0, zf + 20.0), 1400.0, (0.55, 0.62, 1.0), 2.0)
    light("L_SGCave_CrystalE", "POINT", (28.0, y0 + 6.0, zf + 20.0), 1400.0, (0.55, 0.62, 1.0), 2.0)
    light("L_SGCave_Gallery", "POINT", (0.0, 290.0, zg + 8.0), 1800.0, (1.0, 0.72, 0.45), 1.5)


# ------------------------------------------------------------------ invocacao / alquimia (fallback: a v3 entra realocada)
def summon():
    rng = random.Random(71)
    mb = MB("SG_Sum_Blockout", "06_SUMMON", rng, detail="far", floor=-999)
    a0, a1, w = L.SUMMON_BRIDGE
    mb.box2((a1[0], a0[1] - w / 2, L.P1 - 2.0), (a0[0], a0[1] + w / 2, L.P1), "Stone_SG_Block", 0.05)
    SL.plan_stair(mb, "Summon")
    tx, ty = L.SUMMON_TOWER
    z = L.SUM
    mb.box((12.0, 14.0, 2.0), (tx, ty, z + 1.0), (0, 0, 0), "Stone_SG_Trim", 0.1)
    for s in (-1, 1):
        mb.box((3.4, 3.4, 20.0), (tx, ty + s * 6.0, z + 12.0), (0, 0, 0), "Stone_SG_Castle", 0.1)
    mb.box((3.4, 15.4, 3.0), (tx, ty, z + 21.0), (0, 0, 0), "Stone_SG_Castle", 0.1)
    mb.cyl(3.6, 0.6, (tx + 0.4, ty, z + 12.0), (0, math.pi / 2, 0), m="SG_Violet_Glow", n=16, bevel=0.0)
    col_box("SG_SumTower", (4.0, 16.0, 22.0), (tx - 1.0, ty, z + 11.0))
    mb.finish()
    light("L_SGSum_Star", "POINT", (tx + 3.0, ty, z + 12.0), 900.0, (0.66, 0.46, 1.0), 1.0)


def craft():
    rng = random.Random(81)
    mb = MB("SG_Craft_Blockout", "16_CRAFT", rng, detail="far", floor=-999)
    cx, cy = L.CRAFT_C
    z = L.P2
    R, ri, h = L.CRAFT_R, L.CRAFT_R - 2.5, 14.0
    da = math.radians(L.CRAFT_DOOR_DEG)
    half = math.asin((L.CRAFT_DOOR_W / 2) / ri)
    n = 20
    for k in range(n):
        a0 = 2 * math.pi * k / n
        am = a0 + math.pi / n
        diff = abs((am - da + math.pi) % (2 * math.pi) - math.pi)
        rm = (R + ri) / 2
        seg_w = 2 * R * math.sin(math.pi / n) + 0.3
        x, y = cx + rm * math.cos(am), cy + rm * math.sin(am)
        z0 = z + L.CRAFT_DOOR_H if diff < half + math.pi / n * 0.5 else z
        mb.box((R - ri, seg_w, z + h - z0), (x, y, (z0 + z + h) / 2), (0, 0, am), "Stone_SG_Castle", 0.0)
        col_box("SG_CraftWall", (R - ri, seg_w, z + h - z0), (x, y, (z0 + z + h) / 2), (0, 0, am))
    SL.dome(mb, (cx, cy), R + 0.4, z + h, "Roof_SG_Navy", n=20, rings=6, squash=0.8)
    col_box2("SG_CraftRoof", (cx - R, cy - R, z + h), (cx + R, cy + R, z + h + 1.2))
    mb.cyl(2.2, 2.6, (cx, cy, z + 1.3), m="Metal_SG_Iron", n=14, r2=2.6, bevel=0.0)
    ngon_col("SG_CraftCauldron", cx, cy, 12, 2.6, z, z + 2.8)
    mb.finish()


# ------------------------------------------------------------------ masmorra: salas 3x sob o salao sombrio (fila em +Y)
def dungeon():
    rng = random.Random(91)
    mb = MB("SG_Dun_Blockout", "17_DUNGEON", rng, detail="far", floor=-999)
    zf, zc = L.DUN_Z, L.DUN_CEIL
    lw, lh = L.DUN_LINK_W, L.DUN_LINK_H
    rooms = L.DUN_ROOMS
    for i, (nm, (x0, y0, x1, y1)) in enumerate(rooms):
        mb.box2((x0, y0, zf - 2.0), (x1, y1, zf), "Stone_SG_Floor", 0.0)
        mb.box2((x0 - 1.0, y0 - 1.0, zc), (x1 + 1.0, y1 + 1.0, zc + 1.5), "Stone_SGCaveRock", 0.0)
        doors = []
        if i > 0:
            doors.append(("S", L.DUN_LX, lw, lh))
        if i < len(rooms) - 1 or nm == "R3":
            doors.append(("N", L.DUN_LX, lw, lh))
        # paredes visuais (espessura 1, face interna no retangulo) com os vaos
        for sd in ("S", "N", "W", "E"):
            ds = [dd for dd in doors if dd[0] == sd]
            if sd in ("W", "E"):
                xx = x0 - 0.5 if sd == "W" else x1 + 0.5
                mb.box2((xx - 0.5, y0 - 1.0, zf), (xx + 0.5, y1 + 1.0, zc), "Stone_SG_Block", 0.0)
                continue
            yy = y0 - 0.5 if sd == "S" else y1 + 0.5
            if ds:
                _, c, ww, hh = ds[0]
                mb.box2((x0, yy - 0.5, zf), (c - ww / 2, yy + 0.5, zc), "Stone_SG_Block", 0.0)
                mb.box2((c + ww / 2, yy - 0.5, zf), (x1, yy + 0.5, zc), "Stone_SG_Block", 0.0)
                mb.box2((c - ww / 2, yy - 0.5, zf + hh), (c + ww / 2, yy + 0.5, zc), "Stone_SG_Block", 0.0)
                # moldura do vao (le como PORTAL: o selo/portal da proxima sala fica DENTRO deste plano)
                for s in (-1, 1):
                    mb.box((1.6, 1.4, hh + 1.6), (c + s * (ww / 2 + 0.8), yy, zf + (hh + 1.6) / 2), (0, 0, 0),
                           "Stone_SG_Trim", 0.0)
                mb.box((ww + 3.2, 1.4, 1.6), (c, yy, zf + hh + 0.8), (0, 0, 0), "Stone_SG_Trim", 0.0)
            else:
                mb.box2((x0, yy - 0.5, zf), (x1, yy + 0.5, zc), "Stone_SG_Block", 0.0)
        box_walls_col("SG_DunRoom", (x0, y0, x1, y1), zf, zc, 1.0, doors=doors)
        col_box2("SG_DunRoom", (x0 - 1.0, y0 - 1.0, zf - 2.0), (x1 + 1.0, y1 + 1.0, zf))
        col_box2("SG_DunRoom", (x0 - 1.0, y0 - 1.0, zc), (x1 + 1.0, y1 + 1.0, zc + 1.5))
        # pilastras nas paredes laterais (ritmo) + tochas
        for k in range(5):
            y = y0 + (y1 - y0) * (k + 0.5) / 5
            for s in (-1, 1):
                x = x0 + 1.0 if s < 0 else x1 - 1.0
                mb.box((2.0, 3.0, zc - zf), (x, y, (zf + zc) / 2), (0, 0, 0), "Stone_SG_Castle", 0.0)
        cxr, cyr = (x0 + x1) / 2, (y0 + y1) / 2
        light("L_SGDun_%s" % nm, "POINT", (cxr, cyr, zf + 24.0), 6000.0 if nm != "R1" else 3500.0, (0.72, 0.5, 1.0), 2.0)
    # nicho do muro norte da R3 (portal da proxima sala DENTRO do nicho): fundo atras do plano do portal
    x0, y0, x1, y1 = dict(rooms)["R3"]
    nx, ny = L.dun_next("R3")
    mb.box2((nx - lw / 2 - 1.0, ny + L.DUN_NEXT_T / 2 + 0.6, zf), (nx + lw / 2 + 1.0, ny + L.DUN_NEXT_T / 2 + 2.6, zf + lh + 1.0),
            "Stone_SG_Obsidian", 0.0)
    col_box2("SG_DunRoom", (nx - lw / 2 - 1.0, ny + L.DUN_NEXT_T / 2 + 0.6, zf), (nx + lw / 2 + 1.0, ny + L.DUN_NEXT_T / 2 + 2.6, zf + lh + 1.0))
    # portal de chegada da R1 (visual) no muro sul
    x0, y0, x1, y1 = dict(rooms)["R1"]
    mb.cyl(8.0, 0.6, (L.DUN_LX, y0 + 0.4, zf + 9.0), (math.pi / 2, 0, 0), m="SG_CaveVoid_Glow", n=20, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ agua: SO a pedra das bicas (a agua e feita no Roblox)
def water():
    rng = random.Random(101)
    mb = MB("SG_Water_Lips", "07_WATER", rng, detail="far", floor=-999)
    for i, (x, y, z, deg) in enumerate(L.WATERFALLS):
        a = math.radians(deg)
        ux, uy = math.cos(a), math.sin(a)
        mb.box((6.0, 7.4, 1.0), (x - ux * 1.5, y - uy * 1.5, z - 0.72), (0, 0, a), "Stone_SG_Block", 0.05)
        for s in (-1, 1):
            mb.box((6.0, 0.8, 1.2), (x - ux * 1.5 - uy * s * 3.3, y - uy * 1.5 + ux * s * 3.3, z + 0.2), (0, 0, a),
                   "Stone_SG_Block", 0.05)
    mb.finish()


# ------------------------------------------------------------------ saida (fallback: o sg_exit da v3 entra realocado)
def exit_():
    rng = random.Random(111)
    mb = MB("SG_Exit_Blockout", "08_NEXT_ISLAND", rng, detail="far", floor=-999)
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    Ln = L.EXIT_BRIDGE_LEN
    c = L.exit_point(Ln / 2)
    mb.box((Ln, L.EXIT_W, 2.0), (c[0], c[1], L.EXIT_Z - 1.0), (0, 0, a), "Stone_SG_Block", 0.1)
    ic = L.islet_center()
    mb.cyl(L.GATE_ISLET_R, 3.0, (ic[0], ic[1], L.EXIT_Z - 1.5), m="Stone_Paving_SG", n=24, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ vestir: pinheiros, lanternas, patio-jardim, mirante
def pine(mb, x, y, z, h, rng):
    mb.cyl(0.45, h * 0.3, (x, y, z + h * 0.15), m="Wood_SG_Dark", n=6, bevel=0.0)
    for k, (fr, fz) in enumerate(((1.0, 0.28), (0.74, 0.52), (0.48, 0.74))):
        mb.cyl(h * 0.18 * fr, h * 0.34, (x, y, z + h * fz), m="Leaf_SG_Pine", n=7, r2=0.15, bevel=0.0)


def dressing():
    rng = random.Random(121)
    mb = MB("SG_Veg_Blockout", "10_VEGETATION", rng, detail="far", floor=-999)
    for x, y, r, n in L.PINE_GROVES:
        for k in range(n):
            a = rng.uniform(0, 6.28)
            rr = rng.uniform(0, r)
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            z = L.zone_of(px, py)
            z = z if z is not None else L.P1 - 2.0
            pine(mb, px, py, z, rng.uniform(13.0, 20.0), rng)
            if L.zone_of(px, py) is not None:
                col_box("SG_VegPine", (1.2, 1.2, 8.0), (px, py, z + 4.0))
    # PATIO-JARDIM (plano mestre: eixo de 20, 2 gramados, 2 espelhos d'agua, 2 ARVORES-MARCO de 30-36)
    z = L.P3
    for s in (-1, 1):
        mb.box2((min(s * 24.0, s * 90.0), -6.0, z - 0.1), (max(s * 24.0, s * 90.0), 54.0, z + 0.08), "Grass_SG", 0.0)
        tx = s * 76.0
        mb.cyl(1.4, 14.0, (tx, 12.0, z + 7.0), m="Wood_SG_Dark", n=8, bevel=0.0)
        mb.cyl(7.5, 26.0, (tx, 12.0, z + 22.0), m="Leaf_SG_Pine", n=8, r2=1.0, bevel=0.0)
        col_box("SG_VegTree", (2.4, 2.4, 12.0), (tx, 12.0, z + 6.0))
    mb.finish()
    mp = MB("SG_Prop_Blockout", "09_PROPS", rng, detail="far", floor=-999)
    cx, cy = L.PLAZA_C
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        x, y = cx + (L.PLAZA_R - 2.5) * math.cos(a), cy + (L.PLAZA_R - 2.5) * math.sin(a)
        mp.cyl(0.35, 7.0, (x, y, L.P1 + 3.5), m="Metal_SG_Iron", n=6, bevel=0.0)
        mp.box((1.0, 1.0, 1.4), (x, y, L.P1 + 7.4), (0, 0, 0), "Lantern_Glow", 0.0)
        col_box("SG_PropLamp", (0.8, 0.8, 7.0), (x, y, L.P1 + 3.5))
    light("L_SGProp_Plaza", "POINT", (cx, cy - 14.0, L.P1 + 8.0), 600.0, (1.0, 0.72, 0.42), 0.5)
    # espelhos d'agua do patio (borda de pedra; a agua e do Roblox, WATER_Court_L/R)
    for s in (-1, 1):
        x0, x1 = s * 52.0 - 10.0, s * 52.0 + 10.0
        y0, y1 = 8.0, 40.0
        for p0, p1 in (((x0 - 0.8, y0 - 0.8), (x1 + 0.8, y0)), ((x0 - 0.8, y1), (x1 + 0.8, y1 + 0.8)),
                       ((x0 - 0.8, y0), (x0, y1)), ((x1, y0), (x1 + 0.8, y1))):
            mp.box2((p0[0], p0[1], z), (p1[0], p1[1], z + 0.8), "Stone_SG_Trim", 0.05)
        mp.box2((x0, y0, z), (x1, y1, z + 0.1), "Stone_SG_Obsidian", 0.0)
    # 2 estatuas da ordem no pe da porta
    for s in (-1, 1):
        mp.box((3.0, 3.0, 2.0), (s * 22.0, 48.0, z + 1.0), (0, 0, 0), "Stone_SG_Trim", 0.05)
        mp.cyl(1.2, 8.0, (s * 22.0, 48.0, z + 6.0), m="Stone_SG_Castle", n=8, r2=0.7, bevel=0.0)
        col_box("SG_PropStatue", (3.0, 3.0, 10.0), (s * 22.0, 48.0, z + 5.0))
    # jardim-mirante (P3 leste, no lugar da antiga portaria): terraco com parapeito, banco e arvore
    mx, my, mr = L.MIRANTE_E
    mp.cyl(mr, 0.3, (mx, my, z + 0.15), m="Stone_Paving_SG", n=16, bevel=0.0)
    arc = [(mx + mr * math.cos(math.radians(a)), my + mr * math.sin(math.radians(a)), z) for a in range(-80, 81, 20)]
    SL.vis_parapet(mp, arc, h=1.4, w=1.0)
    mp.box((8.0, 1.6, 1.2), (mx - 6.0, my, z + 0.6), (0, 0, math.pi / 2), "Stone_SG_Block", 0.05)
    mp.finish()


def build(skip=()):
    fns = {"terrain": terrain, "entry": entry, "village": village, "castle": castle, "hall": hall, "cave": cave,
           "summon": summon, "craft": craft, "dungeon": dungeon, "water": water, "exit": exit_, "dressing": dressing}
    for z in ZONES:
        if z not in skip:
            fns[z]()
