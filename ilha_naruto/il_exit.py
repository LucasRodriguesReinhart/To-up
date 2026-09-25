# il_exit - PASS 3 (detalhe) da SAIDA NE da Ilha 1: ponte de pedra em arcos sobre o vale leste (ref_16), ilhota de
# rocha do portao DB e a CABECEIRA (interface com a proxima ilha, ISLAND_NEXT_ANCHOR). Substitui
# il_blockout.exit_and_gate(). O portao Dragon Ball em si e do il_gate_db (nicho livre de +-20 em d = D_GATE).
#
# Ponte (d = 0..96, largura 18, piso em EXIT_Z):
#   - encontro no T1 (d < ~8), ARCO SEGMENTAR largo sobre o vale (o riacho cruza em diagonal por baixo; nenhum pilar
#     cai no riacho), pilar P1 na borda da ilha, 3 arcos plenos sobre o vazio com pilares P2/P3 e o encontro na ilhota;
#   - cada pilar fora da ilha assenta numa raiz de rocha que afina para baixo (mesma linguagem da ilhota flutuante);
#   - guarda-corpo: meio-fio de pedra + cerca de madeira + postes de pedra com lanterna (ref_16/ref_18).
# Ilhota: pilar de rocha facetado (tambor + cone + colunas laterais), topo gramado; plataforma calcada de 30 com o
#   nicho do portao, muretas de pedra, e a cabeceira: bastiao de pedra com face limpa, soleira e 2 pilones com
#   lanterna emoldurando o vao de 18.
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box, mk, light
import il_layout as L
import fm_parts as FP
import il_exit_plan as P

C = "07_NEXT_ISLAND"
Z = P.Z
HW = P.HW
F = P.frame()
YAW = P.yaw()
Z_TOP = Z - 0.3                     # topo do corpo da ponte (sob o calcamento)
CROWN = Z - 2.5                     # intradorso no fecho de todos os arcos
PIER_W = 4.0
UX = F.p(1, 0, 0) - F.p(0, 0, 0)    # lateral (mundo)
UY = F.p(0, 1, 0) - F.p(0, 0, 0)    # avanco (mundo)


def _plan():
    """pontos da ponte tirados da planta: pe do muro do T1 (lado SE), borda da ilha (lado NO), pilares"""
    # arco do vale nasce 2 antes de o bordo SE sair do T1 (x = 108) e morre no pilar P1, que fica na borda da ilha
    a0 = None
    d = 0.0
    while d < 40.0:
        if F.p(HW, d).x >= 108.0:
            a0 = d
            break
        d += 0.05
    a0 = (a0 or 8.0) - 2.0
    rim_l = P.edge_crossing(F, -HW, L.ISLAND_RIM) or 43.7
    p1 = (round(rim_l - 0.7, 1), round(rim_l - 0.7, 1) + 5.0)
    abut = P.D_ISL - 4.0
    span = (abut - p1[1] - 2 * PIER_W) / 3.0
    piers = [p1]
    x = p1[1]
    for k in range(2):
        x += span
        piers.append((x, x + PIER_W))
        x += PIER_W
    return a0, piers, abut, span


A0, PIERS, D_ABUT, SPAN = _plan()
A1 = PIERS[0][0]
R_VOID = SPAN / 2.0
Z_SPRING = CROWN - R_VOID           # nascenca dos arcos plenos
D_GATEWAY = 8.0                     # pilones da entrada: onde o tabuleiro sai do T1 (bordo SE)
LANTERN_D = [18.0, 30.0] + [(a + b) / 2 for a, b in PIERS] + [P.D_ISL - 0.6]
PIER_BASE = [-12.0, -6.0, -6.0]     # sapata de cada pilar (P1 desce pela borda da ilha)

CAMS = {
    "CAM_Exit_BridgeSide": (tuple(F.p(62, 26, 34)), tuple(F.p(0, 52, 4)), 22),
    "CAM_Exit_BridgeNW": (tuple(F.p(-58, 88, 44)), tuple(F.p(0, 46, 6)), 22),
    "CAM_Exit_Valley": ((122.0, 70.0, L.G + 6.0), (118.0, 118.0, 11.0), 18),
    "CAM_Exit_Islet": (tuple(F.p(96, 150, 10)), tuple(F.p(0, 108, -18)), 22),
    "CAM_Exit_Anchor": (tuple(F.p(-8, P.D_END + 34, Z + 14)), tuple(F.p(0, P.D_END - 8, Z + 3)), 22),
    "CAM_Exit_Back": (tuple(F.p(30, P.D_END + 16, Z + 34)), tuple(F.p(0, 40, Z - 2)), 22),
    "CAM_Exit_Player": (tuple(F.p(2.5, 8, Z + 5.5)), tuple(F.p(0, 100, Z + 7)), 18),
}


# ------------------------------------------------------------------ utilidades
def body_loft(mb, ds, zb, hw, z_top, m):
    """corpo macico da ponte entre secoes d (fundo zb[i], topo z_top, largura 2*hw): fundo = intradorso do arco"""
    bm = mb.bm
    rings = []
    for d, z in zip(ds, zb):
        rings.append([bm.verts.new(F.p(-hw, d, z_top)), bm.verts.new(F.p(hw, d, z_top)),
                      bm.verts.new(F.p(hw, d, z)), bm.verts.new(F.p(-hw, d, z))])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(4):
            j2 = (j + 1) % 4
            bm.faces.new((r0[j], r0[j2], r1[j2], r1[j]))
    bm.faces.new(rings[0])
    bm.faces.new(list(reversed(rings[-1])))
    mb._post([v for r in rings for v in r], m, None, 0, 1)


def arch_seg(d0, d1, zs, rise, n):
    """intradorso de arco segmentar: [(d, z)], centro, raio"""
    c = (d1 - d0) / 2.0
    R = (c * c + rise * rise) / (2.0 * rise)
    dc = (d0 + d1) / 2.0
    zc = zs + rise - R
    pts = []
    for i in range(n + 1):
        d = d0 + (d1 - d0) * i / n
        pts.append((d, zc + math.sqrt(max(0.0, R * R - (d - dc) ** 2))))
    return pts, (dc, zc), R


def arch_full(d0, d1, zs, n):
    r = (d1 - d0) / 2.0
    dc = (d0 + d1) / 2.0
    pts = []
    for i in range(n + 1):
        a = math.pi * (1 - i / n)
        pts.append((dc + r * math.cos(a), zs + r * math.sin(a)))
    return pts, (dc, zs), r


def voussoirs(mb, ctr, R, a0, a1, n, rng, m="Stone_Paving_Warm", key_m="Stone_Paving_Warm"):
    """aduelas nas DUAS faces: blocos radiais alternando comprimento (extradorso em degraus); chave saliente"""
    dc, zc = ctr
    for s in (-1, 1):
        for i in range(n):
            t0 = a0 + (a1 - a0) * i / n
            t1 = a0 + (a1 - a0) * (i + 1) / n
            tm = (t0 + t1) / 2
            key = i == n // 2
            rad = (1.9 if key else (1.45 if i % 2 else 1.15))
            dep = 1.25 if key else 0.95
            rm = R + rad / 2 - 0.08
            d = dc + rm * math.cos(tm)
            z = zc + rm * math.sin(tm)
            ln = R * abs(t1 - t0) * (1.0 if key else 0.94)
            tilt = tm - math.pi / 2          # tangente no plano (d, z)
            x = s * (HW - dep / 2 + (0.32 if key else 0.16))
            mb.box((dep, ln, rad), F.p(x, d, z), F.r(tilt, 0, 0), key_m if key else m, 0.0)


def pier(mb, d0, d1, z_base, z_top, rng):
    """pilar de alvenaria com talude, faixa de impostas e sapata escura (assenta na raiz de rocha)"""
    ln = d1 - d0
    dc = (d0 + d1) / 2
    h = (z_top - 0.6) - (z_base + 0.8)
    FP.frustum(mb, F.p(0, dc, z_base + 0.8), 2 * (HW + 1.1), ln + 1.2, 2 * (HW + 0.5), ln + 0.3, h,
               "Stone_Wall_Light", ang=YAW)
    mb.box((2 * HW + 1.6, ln + 0.9, 0.6), F.p(0, dc, z_top - 0.3), F.r(), "Stone_Wall_Dark", 0.08)
    mb.box((2 * HW + 2.8, ln + 2.2, 1.0), F.p(0, dc, z_base + 0.5), F.r(), "Stone_Wall_Dark", 0.1)
    # pilastras (sobem do pilar ate a cornija, nas duas faces)
    zp0, zp1 = z_top, Z - 1.3
    for s in (-1, 1):
        mb.box((0.5, ln - 0.9, zp1 - zp0), F.p(s * (HW + 0.2), dc, (zp0 + zp1) / 2), F.r(), "Stone_Wall_Light", 0.1)
    # cunhais nos cantos da face do pilar (pedra escura alternada), so no trecho visivel
    k = 0
    z = z_base + 1.3
    while z < z_top - 1.4:
        t = (z + 0.5 - (z_base + 0.8)) / h
        face = HW + 0.5 + 0.6 * (1.0 - t)
        half_d = (ln + 0.3 + 0.9 * (1.0 - t)) / 2
        for s in (-1, 1):
            for e in (-1, 1):
                w = 1.5 if (k + (e > 0)) % 2 == 0 else 0.9
                mb.box((0.35, w, 1.0), F.p(s * (face + 0.06), dc + e * (half_d - w / 2 + 0.06), z + 0.5), F.r(),
                       "Stone_Paving_Warm", 0.0)
        z += 1.7
        k += 1


def pylon(mb, x, d, h, s=1.0, name=None):
    """pilone de pedra com lanterna no topo (cabeceira e entrada da ponte); retorna o centro da lanterna"""
    b = 2.8 * s
    mb.box((b + 0.7, b + 0.7, 0.8), F.p(x, d, Z + 0.4), F.r(), "Stone_Wall_Dark", 0.15)
    mb.box((b, b, h - 0.8), F.p(x, d, Z + 0.8 + (h - 0.8) / 2), F.r(), "Stone_Wall_Light", 0.18)
    mb.box((b + 0.25, b + 0.25, 0.5), F.p(x, d, Z + h * 0.52), F.r(), "Stone_Wall_Dark", 0.08)
    mb.box((b + 0.6, b + 0.6, 0.5), F.p(x, d, Z + h + 0.25), F.r(), "Stone_Wall_Dark", 0.12)
    lz = Z + h + 0.5
    g = 1.9 * s
    mb.box((g, g, 2.0 * s), F.p(x, d, lz + 1.0 * s), F.r(), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.42 * s, 0.42 * s, 2.1 * s), F.p(x + sx * g / 2, d + sy * g / 2, lz + 1.05 * s), F.r(),
                   "Stone_Wall_Light", 0.0)
    mb.box((g + 0.8, g + 0.8, 0.35), F.p(x, d, lz + 2.1 * s + 0.17), F.r(), "Stone_Wall_Dark", 0.08)
    mb.cyl((g + 1.6) * 0.72, 1.3 * s, F.p(x, d, lz + 2.1 * s + 0.35 + 0.65 * s), (0, 0, YAW + math.pi / 4),
           "Stone_Wall_Dark", 4, r2=0.3 * s, bevel=0.0)
    mb.cyl(0.3 * s, 0.6 * s, F.p(x, d, lz + 2.1 * s + 0.35 + 1.6 * s), (0, 0, 0), "Stone_Wall_Dark", 6, bevel=0.0)
    return F.p(x, d, lz + 1.0 * s)


def rail_lantern(mb, x, d):
    """poste de pedra do guarda-corpo com lanterna (ritmo dos pilares)"""
    mb.box((1.3, 1.3, 3.1), F.p(x, d, Z + 0.5 + 1.55), F.r(), "Stone_Wall_Light", 0.12)
    mb.box((1.7, 1.7, 0.35), F.p(x, d, Z + 3.6 + 0.17), F.r(), "Stone_Wall_Dark", 0.06)
    mb.box((1.0, 1.0, 1.2), F.p(x, d, Z + 3.95 + 0.6), F.r(), "Lantern_Glow", 0.0)
    mb.box((1.5, 1.5, 0.25), F.p(x, d, Z + 5.15 + 0.12), F.r(), "Stone_Wall_Dark", 0.0)
    mb.cyl(1.05, 0.75, F.p(x, d, Z + 5.4 + 0.37), (0, 0, YAW + math.pi / 4), "Stone_Wall_Dark", 4, r2=0.2, bevel=0.0)


def mureta(mb, pts, area, post_step=6.5):
    """mureta de pedra (corpo claro + capa escura + pilaretes) sobre a borda da plataforma, com colisao"""
    zb = Z + 0.15
    for (ax, ad), (bx, bd) in zip(pts, pts[1:]):
        a, b = Vector((ax, ad)), Vector((bx, bd))
        ln = (b - a).length
        if ln < 0.3:
            continue
        ang = math.atan2(b.y - a.y, b.x - a.x) - math.pi / 2     # rotacao local (+y local ao longo do trecho)
        c = (a + b) / 2
        mb.box((1.2, ln, 2.0), F.p(c.x, c.y, zb + 1.0), F.r(0, 0, ang), "Stone_Wall_Light", 0.12)
        mb.box((1.6, ln + 0.3, 0.35), F.p(c.x, c.y, zb + 2.0 + 0.17), F.r(0, 0, ang), "Stone_Wall_Dark", 0.08)
        n = max(1, int(round(ln / post_step)))
        for k in range(n + 1):
            q = a + (b - a) * (k / n)
            mb.box((1.7, 1.7, 2.75), F.p(q.x, q.y, zb + 1.37), F.r(0, 0, ang), "Stone_Wall_Light", 0.14)
            mb.box((2.0, 2.0, 0.3), F.p(q.x, q.y, zb + 2.75 + 0.15), F.r(0, 0, ang), "Stone_Wall_Dark", 0.06)
        col_box(area, (1.6, ln + 0.4, 4.0), F.p(c.x, c.y, Z + 2.0), F.r(0, 0, ang))


def spandrel_ashlar(mb, rng):
    """blocos salientes nos timpanos das duas faces, em fiadas, so onde ha parede acima das aduelas"""
    spans = [arch_seg(A0, A1, L.G, CROWN - L.G, 60)[0]]
    for i, (p0, p1) in enumerate(PIERS):
        nxt = PIERS[i + 1][0] if i + 1 < len(PIERS) else D_ABUT
        spans.append(arch_full(p1, nxt, Z_SPRING, 40)[0])
    z_hi = Z - 1.55

    def intr(pts, d):
        for (da, za), (db, zb) in zip(pts, pts[1:]):
            if da <= d <= db:
                return za + (zb - za) * (d - da) / max(db - da, 1e-6)
        return 99.0
    for s in (-1, 1):
        for pts in spans:
            d_a, d_b = pts[0][0], pts[-1][0]
            z = z_hi - 0.55
            while z > L.G + 0.6:
                d = d_a + rng.uniform(0.0, 1.2)
                while d < d_b - 0.8:
                    ln = rng.uniform(1.6, 3.2)
                    ok = all(intr(pts, dd) + 2.0 < z - 0.55 for dd in (d, d + ln / 2, d + ln)) and d + ln < d_b
                    if ok and rng.random() < 0.55 and not (s < 0 and d < 27.0):
                        mb.box((0.28, ln - 0.15, 1.05), F.p(s * (HW + 0.02), d + ln / 2, z), F.r(),
                               "Stone_Paving_Warm" if rng.random() < 0.35 else "Stone_Wall_Light", 0.0)
                    d += ln + rng.uniform(0.2, 1.6)
                z -= 1.25


# ------------------------------------------------------------------ ponte
def bridge():
    rng = random.Random(8101)
    mb = MB("EXIT_Bridge", C, rng, detail="near")
    # --- corpo: arco do vale, topos de pilar, arcos plenos
    vp, vctr, vR = arch_seg(A0, A1, L.G, CROWN - L.G, 26)
    body_loft(mb, [p[0] for p in vp], [p[1] for p in vp], HW, Z_TOP, "Stone_Wall_Light")
    ta = math.atan2(L.G - vctr[1], A1 - vctr[0])
    voussoirs(mb, vctr, vR, math.pi - ta, ta, 21, rng)
    z_pt = Z_SPRING
    for i, (p0, p1) in enumerate(PIERS):
        body_loft(mb, [p0, p1], [z_pt, z_pt], HW, Z_TOP, "Stone_Wall_Light")
        z_base = PIER_BASE[i]
        pier(mb, p0, p1, z_base, z_pt, rng)
        nxt = PIERS[i + 1][0] if i + 1 < len(PIERS) else D_ABUT
        ap, actr, aR = arch_full(p1, nxt, Z_SPRING, 14)
        body_loft(mb, [p[0] for p in ap], [p[1] for p in ap], HW, Z_TOP, "Stone_Wall_Light")
        voussoirs(mb, actr, aR, math.pi, 0.0, 11, rng)
    # encontro na ilhota (desce para dentro da rocha)
    mb.box((2 * HW + 1.0, P.D_ISL + 1.0 - D_ABUT, Z_TOP + 8.0), F.p(0, (D_ABUT + P.D_ISL + 1.0) / 2, (Z_TOP - 8.0) / 2),
           F.r(), "Stone_Wall_Light", 0.12)
    mb.box((2 * HW + 1.6, 0.9, 0.6), F.p(0, D_ABUT + 0.2, Z_SPRING - 0.3), F.r(), "Stone_Wall_Dark", 0.08)
    # cornija continua (as duas faces) e pilastras do encontro
    for s in (-1, 1):
        mb.box((0.95, P.D_ISL - A0 + 0.6, 1.0), F.p(s * (HW + 0.03), (A0 + P.D_ISL) / 2, Z - 0.8), F.r(),
               "Stone_Wall_Dark", 0.1)
    # --- calcamento do tabuleiro: fiadas transversais (juntas desencontradas) sobre leito escuro
    d0, d1 = -0.1, P.D_ISL - 0.1        # a rua do T1 (il_terrain) termina em d = -0,16
    mb.box((2 * 8.2, d1 - D_GATEWAY + 1.0, 0.3), F.p(0, (D_GATEWAY - 1.0 + d1) / 2, Z - 0.2), F.r(),
           "Stone_Wall_Dark", 0.0)
    d = d0
    row = 0
    while d < d1 - 0.5:
        dep = min(rng.choice((1.7, 1.9, 2.1)), d1 - d)
        cuts = [-8.1] + ([-4.0, 0.0, 4.0] if row % 2 == 0 else [-2.7, 2.7]) + [8.1]
        cuts = [cuts[0]] + [c + rng.uniform(-0.45, 0.45) for c in cuts[1:-1]] + [cuts[-1]]
        for xa, xb in zip(cuts, cuts[1:]):
            if xb - xa < 1.0:
                continue
            hh = 0.4 + rng.uniform(-0.035, 0.035)
            mb.box((xb - xa - 0.2, dep - 0.2, hh), F.p((xa + xb) / 2, d + dep / 2, Z - 0.3 + hh / 2),
                   F.r(0, 0, rng.uniform(-0.006, 0.006)), "Stone_Paving_Warm", 0.0)
        d += dep
        row += 1
    # aparelho de pedra nos timpanos (blocos salientes em fiadas, mais densos junto aos pilares)
    spandrel_ashlar(mb, rng)
    mb.finish()
    # --- colisao: tabuleiro, patamar e o vale (pilar P1 e os arranques do arco, onde o intradorso fica baixo)
    col_box("ExitBridge", (2 * HW, P.D_ISL - D_GATEWAY + 4.0, 3.0), F.p(0, (P.D_ISL + D_GATEWAY - 3.0) / 2, Z - 1.5),
            F.r())
    p0, p1 = PIERS[0]
    col_box("ExitValley", (2 * HW + 1.6, p1 - p0 + 1.0, Z - 0.5 - (L.G - 8.0)), F.p(0, (p0 + p1) / 2,
                                                                                    (Z - 0.5 + L.G - 8.0) / 2), F.r())
    for dd in (A0 + 5.0, A1 - 5.0):
        col_box("ExitValley", (2 * HW, 10.0, Z - 0.5 - (L.G - 2.0)), F.p(0, dd, (Z - 0.5 + L.G - 2.0) / 2), F.r())


def bridge_rails():
    rng = random.Random(8102)
    mb = MB("EXIT_Rails", C, rng, detail="near")
    x = P.RAIL_X
    da, db = D_GATEWAY, P.D_ISL - 0.6
    stations = [da] + LANTERN_D
    for s in (-1, 1):
        # meio-fio continuo
        mb.box((1.2, db - da, 0.8), F.p(s * x, (da + db) / 2, Z_TOP + 0.4), F.r(), "Stone_Wall_Light", 0.1)
        for d in LANTERN_D:
            rail_lantern(mb, s * x, d)
        # cerca de madeira entre os postes: montantes a cada ~3,2 e 2 travessas
        for a, b in zip(stations, stations[1:]):
            a_ = a + (0.7 if a != da else 1.4)
            b_ = b - 0.7
            n = max(1, int(round((b_ - a_) / 3.2)))
            for k in range(1, n):
                d = a_ + (b_ - a_) * k / n
                mb.box((0.55, 0.55, 2.6), F.p(s * x, d, Z + 0.5 + 1.3), F.r(), "Wood_Dark", 0.08)
            for zz, th in ((Z + 1.55, 0.34), (Z + 2.95, 0.42)):
                mb.box((0.36, b_ - a_ + 0.3, th), F.p(s * x, (a_ + b_) / 2, zz), F.r(), "Wood_Plank", 0.06)
        # colisao do guarda-corpo (parede baixa continua)
        col_box("ExitBridge", (1.2, db - da + 1.0, 4.2), F.p(s * x, (da + db) / 2, Z + 2.1), F.r())
    # entrada da ponte: 2 pilones com lanterna (fazem par com os da cabeceira)
    for s in (-1, 1):
        pylon(mb, s * (x + 1.4), D_GATEWAY, 5.2, 0.82)
        col_box("ExitBridge", (3.2, 3.2, 8.0), F.p(s * (x + 1.4), D_GATEWAY, Z + 4.0), F.r())
    mb.finish()


# ------------------------------------------------------------------ ilhota: plataforma, cabeceira, rocha
def islet():
    rng = random.Random(8103)
    out = P.outline()
    wout = IL.ccw(P.to_world(F, out))
    mb = MB("EXIT_Islet", C, rng, detail="near")
    # laje da plataforma (lados aparecem ~1 acima da grama) com leito escuro em cima
    IL.prism(mb, wout, Z - 4.0, Z - 0.1, "Stone_Wall_Light", top_m="Stone_Wall_Dark")
    # lajes de pedra em grade (juntas desencontradas), longe da borda (a borda leva a capa escura)
    tile = 3.0
    d = P.D_ISL + 0.2
    row = 0
    while d < P.D_END - 1.2:
        off = (tile / 2) if row % 2 else 0.0
        x = -P.BAY_HW - 1.0 + off
        while x < P.BAY_HW + 1.0:
            cs = [(x - 1.35, d + 0.15), (x + 1.35, d + 0.15), (x + 1.35, d + 2.85), (x - 1.35, d + 2.85)]
            if all(P.point_in(out, cx, cy) and P.dist_to_edges(out, cx, cy) > 0.95 for cx, cy in cs):
                hh = 0.4 + rng.uniform(-0.04, 0.04)
                mb.box((2.8, 2.7, hh), F.p(x, d + 1.5, Z - 0.3 + hh / 2), F.r(0, 0, rng.uniform(-0.01, 0.01)),
                       "Stone_Paving_Warm", 0.0)
            x += tile
        d += tile
        row += 1
    # capa escura da borda (menos na chegada da ponte e no vao da cabeceira)
    n = len(out)
    for i in range(n):
        a, b = Vector(out[i]), Vector(out[(i + 1) % n])
        if abs(a.y - P.D_END) < 0.01 and abs(b.y - P.D_END) < 0.01:
            segs = [(a, Vector((P.ANCHOR_PYLON_X + 1.9, P.D_END))), (Vector((-P.ANCHOR_PYLON_X - 1.9, P.D_END)), b)]
        elif abs(a.y - P.D_ISL) < 0.01 and abs(b.y - P.D_ISL) < 0.01:
            segs = [(a, Vector((-HW - 0.4, P.D_ISL))), (Vector((HW + 0.4, P.D_ISL)), b)]
        else:
            segs = [(a, b)]
        for p, q in segs:
            ln = (q - p).length
            if ln < 0.2:
                continue
            e = (q - p).normalized()
            nrm = Vector((e.y, -e.x))                      # para fora (contorno anti-horario)
            c = (p + q) / 2 - nrm * 0.5
            ang = math.atan2(e.y, e.x) - math.pi / 2
            mb.box((1.05, ln + 1.0, 0.5), F.p(c.x, c.y, Z - 0.1), F.r(0, 0, ang), "Stone_Wall_Dark", 0.08)
    # --- cabeceira: bastiao de pedra (face limpa em D_END), faixa de apoio da proxima ponte, soleira
    de = P.D_END
    bw = P.PLAT_HW + 0.4
    mb.box((2 * bw, 7.0, 5.0), F.p(0, de - 3.5, Z - 0.3 - 2.5), F.r(), "Stone_Wall_Light", 0.15)
    mb.box((2 * bw + 0.8, 7.8, 0.7), F.p(0, de - 3.5 + 0.4, Z - 5.3 - 0.35), F.r(), "Stone_Wall_Dark", 0.1)
    FP.frustum(mb, F.p(0, de - 3.7 + 0.2, Z - 15.0), 2 * bw + 2.6, 8.4, 2 * bw + 0.4, 7.2, 9.0, "Stone_Wall_Light",
               ang=YAW)
    mb.box((2 * P.ANCHOR_PYLON_X - 3.0, 1.5, 0.48), F.p(0, de - 0.75, Z - 0.12), F.r(), "Stone_Wall_Dark", 0.06)
    # aparelho do bastiao: fiadas de blocos salientes nos lados e na face (o miolo de 19,6 da face fica liso:
    # e onde encosta o tabuleiro da proxima ilha)
    for k, z in enumerate((Z - 1.0, Z - 2.25, Z - 3.5, Z - 4.75)):
        x = -bw + 0.2 + (0.0 if k % 2 == 0 else 1.3)
        while x < bw - 0.6:
            ln = min(rng.uniform(2.2, 3.8), bw - 0.2 - x)
            if (x + ln < -HW - 0.8 or x > HW + 0.8 or z < Z - 3.2) and ln > 0.9:
                mb.box((ln - 0.16, 0.3, 1.05), F.p(x + ln / 2, de + 0.02, z), F.r(),
                       "Stone_Paving_Warm" if rng.random() < 0.4 else "Stone_Wall_Light", 0.0)
            x += ln
        for sx in (-1, 1):
            d = de - 6.9 + (0.0 if k % 2 == 0 else 1.2)
            while d < de - 0.3:
                ln = min(rng.uniform(2.2, 3.6), de - 0.1 - d)
                if ln > 0.9:
                    mb.box((0.3, ln - 0.16, 1.05), F.p(sx * (bw + 0.02), d + ln / 2, z), F.r(),
                           "Stone_Paving_Warm" if rng.random() < 0.4 else "Stone_Wall_Light", 0.0)
                d += ln
    mb.finish()
    # colisao da plataforma (retangulo principal + nicho do portao)
    col_box("ExitIslet", (2 * P.PLAT_HW, P.D_END - P.D_ISL, 3.0), F.p(0, (P.D_ISL + P.D_END) / 2, Z - 1.5), F.r())
    b0, b1 = P.D_GATE + P.BAY[0][1] + 1.0, P.D_GATE + P.BAY[-1][1] - 1.0
    col_box("ExitIslet", (2 * P.BAY_HW, b1 - b0, 3.0), F.p(0, (b0 + b1) / 2, Z - 1.5), F.r())

    # --- muretas, pilones e lanternas da cabeceira
    mr = MB("EXIT_Islet_Walls", C, rng, detail="near")
    ph = P.PLAT_HW - 0.6
    by0 = P.D_GATE + P.BAY[0][1]
    by1 = P.D_GATE + P.BAY[-1][1]
    for s in (-1, 1):
        mureta(mr, [(s * (HW + 0.2), P.D_ISL + 0.6), (s * ph, P.D_ISL + 0.6)], "ExitIslet")
        mureta(mr, [(s * ph, by1 + 1.2), (s * ph, de - 0.6), (s * (P.ANCHOR_PYLON_X + 1.9), de - 0.6)], "ExitIslet")
        lc = pylon(mr, s * P.ANCHOR_PYLON_X, de - 1.85, 7.6, 1.0)
        col_box("ExitAnchor", (3.6, 3.6, 12.0), F.p(s * P.ANCHOR_PYLON_X, de - 1.85, Z + 6.0), F.r())
        light("L_Exit_Anchor_%s" % ("R" if s > 0 else "L"), "POINT", lc, 160, (1.0, 0.64, 0.3), 0.4)
    mr.finish()


def rock():
    """ilhota (tambor + cone + colunas laterais) e raizes de rocha dos pilares fora da ilha"""
    rng = random.Random(8104)
    mb = MB("EXIT_Rock", C, rng, detail="near")
    out = P.outline()
    top = P.rounded_offset(out, 3.0)
    top = [(x, min(d, P.D_END - 3.2)) for x, d in top]      # frente reta atras da face do bastiao
    cxl = sum(p[0] for p in top) / len(top)
    cdl = sum(p[1] for p in top) / len(top)
    cc = F.p(cxl, cdl, 0.0)
    # contorno com ~28 pontos (reamostrado por angulo) em deslocamentos de mundo
    rel = []
    for k in range(28):
        a = math.tau * k / 28
        best = None
        for i in range(len(top)):
            (x0, y0), (x1, y1) = top[i], top[(i + 1) % len(top)]
            # raio do centro na direcao a cruzando a aresta
            dx, dy = math.cos(a), math.sin(a)
            ex, ey = x1 - x0, y1 - y0
            den = dx * ey - dy * ex
            if abs(den) < 1e-9:
                continue
            t = ((x0 - cxl) * ey - (y0 - cdl) * ex) / den
            u = ((x0 - cxl) * dy - (y0 - cdl) * dx) / den
            if t > 0 and -1e-6 <= u <= 1 + 1e-6:
                best = t if best is None else min(best, t)
        r = (best or 20.0) * (1.0 + 0.06 * max(0.0, math.sin(3 * a + 0.7)) + 0.04 * max(0.0, math.sin(5 * a + 2.1))) + 0.6
        lx, ld = math.cos(a) * r, math.sin(a) * r
        if cdl + ld > P.D_END - 3.2:
            ld = P.D_END - 3.2 - cdl
        rel.append(tuple((UX * lx + UY * ld).xy))
    drum_z0 = Z - 30.0
    FP.rock_column(mb, cc, [(x * 0.9, y * 0.9) for x, y in rel], drum_z0, Z - 0.8, rng, "Cliff_Rock_Tan",
                   taper=1 / 0.9, rings=3, jitter=0.035, tilt=0.0, top_m="Grass_Konoha", lip=0.9, rim=True,
                   tongues=(12, "Grass_Konoha", (1.2, 3.6), (1.0, 0.2)), bottom=False)
    FP.rock_column(mb, cc, [(x * 0.15, y * 0.15) for x, y in rel], -80.0, drum_z0 + 2.5, rng, "Cliff_Rock_Tan",
                   taper=0.86 / 0.15, rings=4, jitter=0.12, tilt=0.04)
    # colunas laterais (quebram a silhueta em prismas verticais, como na ref_13); nada na frente dos arcos
    back = math.atan2(-1.0, 0.0)
    for k in range(15):
        a = math.tau * (k + 0.5) / 15 + rng.uniform(-0.12, 0.12)
        da = abs((a - back + math.pi) % math.tau - math.pi)
        if da < math.radians(34):
            continue
        i = int(round(a / math.tau * 28)) % 28
        v = Vector(rel[i]) * rng.uniform(0.88, 0.95)
        c = cc + Vector((v.x, v.y, 0.0))
        tang = Vector((-v.y, v.x, 0.0)).normalized()
        nrm = Vector((v.x, v.y, 0.0)).normalized()
        poly = FP._to_world(FP._rock_poly(rng.uniform(3.6, 5.6), rng.uniform(2.6, 3.6), rng.choice((5, 6, 7)), rng,
                                          ex=2.4, jit=0.1), tang, nrm)
        zt = Z - rng.uniform(1.3, 7.0)
        zb = Z - rng.uniform(16.0, 50.0)
        FP.rock_column(mb, c, [(x * 0.5, y * 0.5) for x, y in poly], zb, zt, rng,
                       "Cliff_Rock_Tan_Dark" if k % 3 == 1 else "Cliff_Rock_Tan", taper=2.0, rings=2, jitter=0.1,
                       tilt=0.06, top_m=("Grass_Konoha" if zt > Z - 3.0 else None), lip=0.6, rim=False)
    # o bastiao da cabeceira assenta em 3 blocos de rocha (nada de alvenaria pendurada no vazio)
    for k, lx in enumerate((-10.5, 0.0, 10.5)):
        c = F.p(lx, P.D_END - 3.4, 0.0)
        poly = FP._to_world(FP._rock_poly(6.2, 4.6, 7, rng, ex=2.4, jit=0.1), UX, UY)
        FP.rock_column(mb, c, [(x * 0.35, y * 0.35) for x, y in poly], Z - rng.uniform(34.0, 44.0), Z - 13.6, rng,
                       "Cliff_Rock_Tan_Dark" if k == 1 else "Cliff_Rock_Tan", taper=1 / 0.35, rings=2, jitter=0.1,
                       tilt=0.0)
    # raizes de rocha dos pilares
    for i, (p0, p1) in enumerate(PIERS):
        dc = (p0 + p1) / 2
        z_base = PIER_BASE[i]
        poly = FP._to_world(FP._rock_poly(HW + 2.0, (p1 - p0) / 2 + 1.9, 8, rng, ex=2.6, jit=0.08, a0=0.2),
                            UX, UY)
        FP.rock_column(mb, F.p(0, dc, 0.0), [(x * 0.24, y * 0.24) for x, y in poly],
                       (-52.0 if i == 0 else rng.uniform(-36.0, -30.0)), z_base + 1.2, rng,
                       "Cliff_Rock_Tan", taper=1 / 0.24, rings=3, jitter=0.12, tilt=0.0)
    mb.finish()


def markers():
    s0 = F.p(0, 0, Z)
    mk("ISLAND_EXIT_Naruto", (s0.x, s0.y, Z), (0, 0, YAW), 3.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": Z, "heading_deg": L.EXIT_DEG})
    ax, ay = L.anchor_pos()
    mk("ISLAND_NEXT_ANCHOR", (ax, ay, Z), (0, 0, YAW), 5.0, "ARROWS",
       props={"width": L.EXIT_W, "deck_z": Z, "clear_h": L.PG_OPEN_H + 4.0, "heading_deg": L.EXIT_DEG,
              "next_area": 2})


def build():
    bridge()
    bridge_rails()
    islet()
    rock()
    markers()
