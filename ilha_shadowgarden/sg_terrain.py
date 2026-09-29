# sg_terrain - ZONA TERRAIN da Ilha 3 (Shadow Garden): a massa da ilha flutuante, a moldura de tudo.
# build() substitui sg_blockout.terrain. Prefixo SG_Ter_, colecao 02_TERRAIN. Sem luzes.
#   1. topo de cada patamar EXATAMENTE na cota (P1/P3/entrada/summon em calcamento frio, P2 em grama fria);
#   2. arrimos entre patamares (P1->P2 em y -83, P2->P3 em y -9 sob a muralha): alvenaria escura em fiadas,
#      contrafortes, arremate claro, parapeito sobre cachorros; as bordas que dao para o terreno bravo ganham face
#      (P1: meio-fio de alvenaria; P2/P3: base de basalto em colunas + faixa de alvenaria = terraco fortificado);
#   3. terreno bravo (ombro) em 34,2 (mesma cota do blockout: o vestir apoia os pinheiros nela) e, na entrada, uma
#      espinha de rocha MAIS BAIXA que a calcada (26,2 -> 34,2 acompanhando a escadaria): a entrada corre por cima;
#      os 6 montes viram formacoes de basalto em colunas com topo de grama (colisao octo_col mantida);
#   4. penhasco: coroa de blocos de colunas hexagonais na borda (topos de grama em alturas diferentes, fendas
#      recuadas, pilares destacados na frente, estrato claro/escuro), massa de baixo em aneis de colunas pendentes
#      afinando ate ~-110 (nada de cone liso), CLIFF_SPIRES como aglomerados de colunas altas, ilhota do summon;
#   5. nada de arvore, cachoeira ou ponte (so as bordas/entalhes onde a agua e as pontes encostam);
#   6. refinamento v2 (borda viva): aglomerados de cristais SG_Crystal_Glow encravados na face externa (abaixo do
#      topo, fora do alcance), veios SG_VioletDeep_Glow e pontas de cristal nas colunas pendentes (rim_crystals).
# REGRA DA DUNGEON: nenhuma face entra em sg_layout.DUN_KEEP_OUT (x -70..74, y 50..110, z 2..32): tudo que fica
# dentro dessa projecao XY esta acima de 32,5 (topos/corpos) ou abaixo de -14 (massa de baixo); as faces laterais da
# massa ficam na borda da ilha, fora da caixa.
import math, random
import bpy
from mathutils import Vector
import sg_lib as SL
from sg_lib import MB, col_box, octo_col, ccw
import sg_layout as L
import sg_col

P1, P2, P3, SUM, DECK = L.P1, L.P2, L.P3, L.SUM, L.DECK
SH = P1 - 2.0                       # 34,2 ombro (terreno bravo)
NECK_LOW = DECK - 2.0               # 26,2 espinha de rocha ao lado do patio baixo
CUT_Y = L.ENTRY_HIGH[1]             # -188: sul disso e o pescoco da entrada
STAIR_Y0 = L.ENTRY_STAIR[1]         # -206: pe da escadaria da entrada
NECK_STAIR_X = 10.4                 # canal da escadaria da entrada (muretas do sg_entry ate |x| 10,4)
BODY_BOT = SH - 1.2                 # base (enterrada) dos corpos dos patamares
CORE_BOT = -16.0
KX0, KY0, KZ0, KX1, KY1, KZ1 = L.DUN_KEEP_OUT

ROCK, DARK, TOP, GRASS = "Cliff_Rock_SG", "Cliff_Rock_SG_Dark", "Cliff_Rock_SG_Top", "Grass_SG"
BLOCK, TRIM, PAVE = "Stone_SG_Block", "Stone_SG_Trim", "Stone_Paving_SG"

# ------------------------------------------------------------------ cameras de revisao da zona (360 graus)
CAMS = {
    "CAM_SGTer_Under": ((-270.0, -250.0, -96.0), (10.0, -20.0, -24.0), 24),
    "CAM_SGTer_CliffEast": ((310.0, -170.0, 46.0), (140.0, -80.0, 8.0), 24),
    "CAM_SGTer_Neck": ((95.0, -300.0, 62.0), (0.0, -200.0, 22.0), 22),
    "CAM_SGTer_NorthEast": ((300.0, 340.0, 150.0), (40.0, 100.0, 30.0), 24),
    "CAM_SGTer_NorthWest": ((-300.0, 320.0, 120.0), (-40.0, 100.0, 30.0), 24),
    "CAM_SGTer_Summon": ((-240.0, -40.0, 72.0), (-142.0, -118.0, 18.0), 24),
    "CAM_SGTer_WaterWest": ((-215.0, -10.0, 62.0), (-124.0, -52.0, 36.0), 24),
    "CAM_SGTer_WaterNorth": ((-110.0, 275.0, 88.0), (-52.0, 190.0, 44.0), 24),
    "CAM_SGTer_ExitBridge": ((215.0, -95.0, 58.0), (160.0, -38.0, 36.0), 24),
    # altura do jogador (olho 5,2 acima do piso)
    "CAM_SGTer_PlayerHeight_P1Wall": ((-44.0, -114.0, P1 + 5.2), (-12.0, -83.0, P2 + 1.0), 22),
    "CAM_SGTer_PlayerHeight_P3Wall": ((-20.0, -36.0, P2 + 5.2), (-42.0, -9.0, P3 + 2.0), 22),
    "CAM_SGTer_PlayerHeight_P3West": ((-50.0, 166.0, P3 + 5.2), (-112.0, 140.0, SH + 8.0), 22),
    "CAM_SGTer_PlayerHeight_P1Edge": ((70.0, -150.0, P1 + 5.2), (130.0, -190.0, SH - 6.0), 22),
}

# rotas extras: o pe dos arrimos continua andavel com os contrafortes (colisao propria)
EXTRA_ROUTES = {
    "P1_pe_do_arrimo_O": ([(-100.0, -87.0), (-14.0, -87.0)], P1),
    "P1_pe_do_arrimo_L": ([(14.0, -87.0), (130.0, -87.0)], P1),
    "P2_pe_da_muralha_O": ([(-100.0, -14.0), (-12.0, -14.0)], P2),
    "P2_pe_da_muralha_L": ([(12.0, -14.0), (100.0, -14.0)], P2),
}
EXTRA_PROBES = []


# ------------------------------------------------------------------ cotas do terreno bravo (para o vestir)
def neck_z(y):
    if y <= STAIR_Y0:
        return NECK_LOW
    if y >= CUT_Y:
        return SH
    return NECK_LOW + (SH - NECK_LOW) * (y - STAIR_Y0) / (CUT_Y - STAIR_Y0)


def wild_z(x, y):
    """cota do chao do terreno bravo (fora dos patamares): 34,2; no pescoco da entrada, a espinha baixa"""
    return neck_z(y) if y < CUT_Y else SH


def ground_z(x, y):
    """cota do chao visual em (x, y): patamar (planta) ou terreno bravo (sem contar montes/colunas)"""
    z = L.zone_of(x, y)
    return z if z is not None else wild_z(x, y)


# ------------------------------------------------------------------ geometria
def clean(poly, eps=0.03):
    out = []
    for p in poly:
        if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
            out.append((float(p[0]), float(p[1])))
    while len(out) > 2 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
        out.pop()
    return out


def prism2(mb, poly, z0, z1, m_side, m_top=None, m_bot=None):
    """prisma fechado; tampo e fundo com material proprio (sem tampo extra por cima)"""
    poly = clean(ccw(poly))
    if len(poly) < 3 or abs(SL.area(poly)) < 0.5:
        return
    bm = mb.bm
    vb = [bm.verts.new((x, y, z0)) for x, y in poly]
    vt = [bm.verts.new((x, y, z1)) for x, y in poly]
    fb = bm.faces.new(list(reversed(vb)))
    ft = bm.faces.new(vt)
    n = len(poly)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m_side, None, 0, 1)
    if m_top:
        ft.material_index = mb._mi_for(m_top)
    if m_bot:
        fb.material_index = mb._mi_for(m_bot)


def column(mb, cx, cy, r, zt, zb, rot=0.0, m=ROCK, cap=TOP, band=None, strata=None, low=None, tip=0.0,
           taper=1.0, n=6):
    """prisma de basalto (hexagonal): topo em zt (material cap), faixa de topo band=(esp, mat) (luar na quina),
    estrato strata=(z, fator_raio, (dx, dy)): abaixo de z a coluna recua/desloca (degrau) e usa 'low';
    tip > 0: ponta pendente abaixo de zb (estalactite). Malha fechada."""
    bm = mb.bm

    def ring(rr, z, ox=0.0, oy=0.0):
        return [bm.verts.new((cx + ox + rr * math.cos(rot + 2 * math.pi * k / n),
                              cy + oy + rr * math.sin(rot + 2 * math.pi * k / n), z)) for k in range(n)]
    seq = [ring(r, zt)]
    mats = []
    zcur = zt
    if band and zt - band[0] > zb + 0.8:
        zcur = zt - band[0]
        seq.append(ring(r, zcur))
        mats.append(band[1])
    if strata and zb + 0.8 < strata[0] < zcur - 0.8:
        zs, fs, (dx, dy) = strata
        seq.append(ring(r, zs))
        mats.append(m)
        seq.append(ring(r * fs, zs, dx, dy))
        mats.append(low or m)
        seq.append(ring(r * fs * taper, zb, dx, dy))
        mats.append(low or m)
    else:
        seq.append(ring(r * taper, zb))
        mats.append(m)
    allv = [v for rg in seq for v in rg]
    top = bm.faces.new(seq[0])
    groups = {}
    for (a, b), mm in zip(zip(seq, seq[1:]), mats):
        for k in range(n):
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last = seq[-1]
    lm = mats[-1]
    if tip > 0:
        lx = sum(v.co.x for v in last) / n
        ly = sum(v.co.y for v in last) / n
        apex = bm.verts.new((lx, ly, zb - tip))
        allv.append(apex)
        for k in range(n):
            groups.setdefault(lm, []).append(bm.faces.new((last[(k + 1) % n], last[k], apex)))
    else:
        groups.setdefault(lm, []).append(bm.faces.new(list(reversed(last))))
    mb._post(allv, m, None, 0, 1)
    top.material_index = mb._mi_for(cap)
    for mm, fs_ in groups.items():
        if mm != m:
            mi = mb._mi_for(mm)
            for f in fs_:
                f.material_index = mi


def ebox(mb, a, u, nrm, t0, t1, d0, d1, z0, z1, m):
    """caixa no referencial da aresta: ao longo de u de t0 a t1, para fora (nrm) de d0 a d1, z0..z1"""
    tm, dm = (t0 + t1) / 2, (d0 + d1) / 2
    cx = a[0] + u[0] * tm + nrm[0] * dm
    cy = a[1] + u[1] * tm + nrm[1] * dm
    mb.box((abs(t1 - t0), abs(d1 - d0), abs(z1 - z0)), (cx, cy, (z0 + z1) / 2), (0, 0, math.atan2(u[1], u[0])), m, 0)


def resample_closed(pts, step):
    """pontos igualmente espacados num contorno fechado: (x, y, nx, ny) com a normal para FORA (anti-horario)"""
    pts = ccw(pts)
    n = len(pts)
    segs = []
    tot = 0.0
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        segs.append((a, b, ln, tot))
        tot += ln
    m = max(3, int(round(tot / step)))
    out = []
    si = 0
    for k in range(m):
        t = tot * k / m
        while si < n - 1 and segs[si][3] + segs[si][2] < t:
            si += 1
        a, b, ln, t0 = segs[si]
        f = (t - t0) / ln if ln > 1e-9 else 0.0
        x, y = a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f
        # tangente suavizada (segmento anterior + atual + seguinte)
        pa, pb = pts[(si - 1) % n], pts[(si + 2) % n]
        tx, ty = pb[0] - pa[0], pb[1] - pa[1]
        tl = math.hypot(tx, ty) or 1.0
        out.append((x, y, ty / tl, -tx / tl))
    return out


def scaled(poly, f, c):
    return [(c[0] + (x - c[0]) * f, c[1] + (y - c[1]) * f) for x, y in poly]


# ------------------------------------------------------------------ restricoes (pontes, escadas, agua, pisos, dungeon)
BRIDGES = sg_col.bridge_list()
FALLS = []
for _wx, _wy, _wz, _deg in L.WATERFALLS:
    FALLS.append((_wx, _wy, _wz, math.cos(math.radians(_deg)), math.sin(math.radians(_deg))))


def hex_pts(cx, cy, r, n=6, rot=0.0):
    return [(cx + r * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)] + [(cx, cy)]


def water_fix(cx, cy, r, zt):
    """a cortina da cachoeira cai 2,5 alem do labio (larga 7): coluna na frente dela recua e baixa sob o labio"""
    for wx, wy, wz, ux, uy in FALLS:
        lat = abs(-(cx - wx) * uy + (cy - wy) * ux)
        along = (cx - wx) * ux + (cy - wy) * uy
        if lat < r + 4.6 and along > -r - 3.0:
            if along + r > 0.6:
                sh = along + r - 0.6
                cx -= ux * sh
                cy -= uy * sh
            zt = min(zt, wz - 0.4)
    return cx, cy, zt


def cap_top(cx, cy, r, zt, near=1.2):
    """nao furar piso: vertice dentro de patamar -> topo abaixo da cota (fica dentro do corpo do patamar);
    pontes/escadas por cima -> topo abaixo do tabuleiro"""
    for px, py in hex_pts(cx, cy, r * 1.02):
        z = L.zone_of(px, py)
        if z is not None:
            zt = min(zt, z - 0.08)
    for nm, a, b, z, w in BRIDGES:
        if sg_col._in_rect_along(cx, cy, a, b, w / 2 + r + 1.0, pad=r + 2.5):
            zt = min(zt, z - 2.6)
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        fp = sg_col.stair_footprint(nm, pad=1.5)
        if any(L.point_in_poly(px, py, fp) for px, py in hex_pts(cx, cy, r + 1.4)):
            zt = min(zt, foot[2] - 0.1)
    return zt


def in_keepout_xy(cx, cy, r):
    return cx + r > KX0 and cx - r < KX1 and cy + r > KY0 and cy - r < KY1


def dun_ok(cx, cy, r, z0, z1):
    """a peca (disco de raio r, z0..z1) fica fora da caixa das salas da dungeon?"""
    if not in_keepout_xy(cx, cy, r):
        return True
    return z1 <= KZ0 - 0.3 or z0 >= KZ1 + 0.3


# trechos de borda onde a VILA ja poe parapeito proprio (sg_village: muretas do topo da escada P1P2 e do mirante oeste
# do P2): aqui o terreno nao duplica o parapeito (so a alvenaria, o arremate e os cachorros)
VILLAGE_PARAPETS = [((-26.0, -83.45), (-9.9, -83.45)), ((9.9, -83.45), (26.0, -83.45)),
                    ((-118.0, -55.0), (-119.2, -40.4)), ((-119.2, -40.4), (-117.6, -35.0))]


def village_parapet(x, y):
    for a, b in VILLAGE_PARAPETS:
        d, t = L.seg_dist(x, y, a[0], a[1], b[0], b[1])
        if d < 1.6:
            return True
    return False


# volumes do CASTELO que nascem na borda do P3 / terreno bravo (sg_castle): cortina oeste pela borda do P3, torres da
# muralha/cortina/alas e o soco da ala oeste. Ali o terreno nao poe alvenaria/parapeito/rocha (ficariam dentro deles).
def _castle_shapes():
    circles, rects = [], []
    curtain = [(L.WALL_X[0], L.WALL_Y0), (-78.0, 40.0), (-60.0, 60.0)]
    try:
        import sg_castle as CS
        gr = getattr(CS, "GATE_R", 7.0)
        circles += [(x, y, gr + 1.0) for x, y, r in L.GATEHOUSE_TOWERS]
        circles += [(x, y, r + 1.0) for x, y, r in CS.WALL_TOWERS]
        circles.append((CS.SW_TOWER[0], CS.SW_TOWER[1], CS.SW_TOWER[2] + 1.5))
        circles.append((CS.CURTAIN_TOWER[0], CS.CURTAIN_TOWER[1], CS.CURTAIN_TOWER[2] + 1.5))
        circles += [(x, y, CS.EG_R + 1.0) for x, y in CS.EG_TURRETS]
        circles += [(t[0], t[1], t[2] + 1.5) for t in CS.WING_TOWERS]
        x0, y0, x1, y1 = CS.WW
        rects.append((x0 - 3.7, y0 - 3.7, x1 + 3.7, y1 + 3.7))
    except Exception as ex:                       # sem o modulo do castelo: valores da planta aprovada
        print("TER AVISO sg_castle indisponivel (%s): volumes do castelo pelos valores padrao" % ex)
        circles += [(x, y, r + 1.0) for x, y, r in L.GATEHOUSE_TOWERS]
        circles += [(-46.0, -6.0, 5.6), (62.0, -6.0, 5.6), (-80.5, -6.2, 8.0), (-82.0, 16.0, 7.0),
                    (-95.0, 65.0, 8.0), (-95.0, 133.0, 7.5), (-66.0, 138.0, 8.0), (55.0, 140.0, 8.0)]
        rects.append((-97.7, 61.3, -58.3, 136.7))
    return circles, rects, curtain


CAS_CIRCLES, CAS_RECTS, CAS_CURTAIN = _castle_shapes()


def castle_hit(x, y, r=0.0, curtain=True, rects=True):
    for cx, cy, cr in CAS_CIRCLES:
        if math.hypot(x - cx, y - cy) < cr + r:
            return True
    if rects:
        for x0, y0, x1, y1 in CAS_RECTS:
            if x0 - r < x < x1 + r and y0 - r < y < y1 + r:
                return True
    if curtain:
        for a, b in zip(CAS_CURTAIN, CAS_CURTAIN[1:]):
            d, t = L.seg_dist(x, y, a[0], a[1], b[0], b[1])
            if d < 4.0 + r:
                return True
    return False


def water_gap(x, y):
    """trecho de borda por onde a agua de uma cachoeira sai (parapeito aberto)"""
    for wx, wy, wz, ux, uy in FALLS:
        lat = abs(-(x - wx) * uy + (y - wy) * ux)
        back = (wx - x) * ux + (wy - y) * uy
        if lat < 3.6 and -1.0 < back < 18.0:
            return True
    return False


# ------------------------------------------------------------------ setores (massa grande dividida em objetos)
RIM = clean(ccw(L.ISLAND_RIM))
C = (sum(p[0] for p in RIM) / len(RIM), sum(p[1] for p in RIM) / len(RIM))
SECT = ["S", "E", "NE", "N", "NW", "W"]


def sector_of(x, y):
    a = math.degrees(math.atan2(y - C[1], x - C[0]))
    return SECT[int(((a + 120.0) % 360.0) // 60.0)]


def check_star():
    """as fatias por setor exigem contorno estrelado em relacao a C (angulo monotono)"""
    angs = [math.atan2(y - C[1], x - C[0]) for x, y in RIM]
    bad = 0
    for a0, a1 in zip(angs, angs[1:] + angs[:1]):
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        if d <= 0:
            bad += 1
    if bad:
        print("TER AVISO contorno nao estrelado em relacao ao centro: %d passos" % bad)


def sector_wedges(poly):
    """divide um contorno estrelado (em relacao a C) em 6 fatias de 60 graus"""
    rel = [(x - C[0], y - C[1]) for x, y in poly]
    out = {}
    for k, nm in enumerate(SECT):
        a0 = -120.0 + 60.0 * k
        w = SL.IL.wedge_clip(rel, a0, a0 + 60.0)
        w = clean([(x + C[0], y + C[1]) for x, y in w])
        if len(w) >= 3 and abs(SL.area(w)) > 1.0:
            out[nm] = w
    return out


_MB = {}


def smb(name, detail="far"):
    if name not in _MB:
        _MB[name] = MB(name, "02_TERRAIN", random.Random(zlib_seed(name)), detail=detail, floor=-999)
    return _MB[name]


def zlib_seed(s):
    import zlib
    return zlib.crc32(s.encode("utf-8")) & 0xffff


def cliff_mb(x, y):
    return smb("SG_Ter_Cliff_" + sector_of(x, y))


# ------------------------------------------------------------------ patamares: corpo + topo na cota
def terraces():
    polys = {nm: poly for nm, poly, z, pr in L.floors()}
    specs = [("P1", P1, PAVE), ("P2", P2, GRASS), ("P3", P3, PAVE)]
    for nm, z, top in specs:
        mb = smb("SG_Ter_Terrace_" + nm)
        if nm != "P3":
            prism2(mb, polys[nm], BODY_BOT, z, DARK, m_top=top)
            continue
        # P3: o piso visual do Mining Hall (sg_hall, topo 52,2) ocupa o retangulo do salao -> sem tampo meu ali
        hx0, hy0, hx1, hy1 = L.HALL_X0, L.HALL_Y0, L.HALL_X1, L.HALL_Y1
        poly = ccw(polys[nm])
        south = SL.clip(poly, 0.0, 1.0, hy0)
        north = SL.clip(poly, 0.0, -1.0, -hy1)
        midb = SL.clip(SL.clip(poly, 0.0, -1.0, -hy0), 0.0, 1.0, hy1)
        west = SL.clip(midb, 1.0, 0.0, hx0)
        east = SL.clip(midb, -1.0, 0.0, -hx1)
        for piece in (south, north, west, east):
            prism2(mb, piece, BODY_BOT, z, DARK, m_top=top)
    me = smb("SG_Ter_Terrace_Entry")
    x0, y0, x1, y1 = L.ENTRY_HIGH
    prism2(me, SL.IL.ccw([(x0, y0), (x1, y0), (x1, -164.0), (x0, -164.0)]), 26.0, P1, DARK, m_top=PAVE)
    x0, y0, x1, y1 = L.ENTRY_LOW
    prism2(me, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 20.0, DECK, DARK, m_top=PAVE)
    # leito da escadaria da entrada (a escada da planta assenta em 28,2; tapa a fresta sob os banzos)
    prism2(me, [(-NECK_STAIR_X, STAIR_Y0), (NECK_STAIR_X, STAIR_Y0), (NECK_STAIR_X, CUT_Y), (-NECK_STAIR_X, CUT_Y)],
           24.0, DECK - 0.2, DARK)


# ------------------------------------------------------------------ bordas dos patamares
def edge_runs(nm, poly, z, step=1.0):
    """trechos de borda do patamar com a mesma leitura do sg_col.edge_guards:
    (a, u, n, t0, t1, cls, zo, aberto, muralha). cls: 'terrace' (patamar mais baixo do lado de fora) ou 'wild'"""
    pts = clean(ccw(poly))
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.3:
            continue
        ux, uy = dx / ln, dy / ln
        nx, ny = uy, -ux
        ns = max(1, int(round(ln / step)))
        keys = []
        for k in range(ns):
            t = (k + 0.5) * ln / ns
            x, y = a[0] + ux * t, a[1] + uy * t
            key = None
            if L.floor_name(x - nx * 0.6, y - ny * 0.6) == nm:
                ox, oy = x + nx * 1.6, y + ny * 1.6
                zo = L.zone_of(ox, oy)
                cls = None
                if zo is None:
                    cls, zo = "wild", wild_z(ox, oy)
                elif zo < z - 2.3:
                    cls = "terrace"
                if cls:
                    opn = bool(sg_col.opening(ox, oy) or water_gap(x, y) or village_parapet(x + nx * 0.5, y + ny * 0.5))
                    mur = (nm == "P3" and abs(y - L.WALL_Y0) < 0.6 and L.WALL_X[0] - 0.5 <= x <= L.WALL_X[1] + 0.5)
                    cas = castle_hit(x + nx * 1.2, y + ny * 1.2, rects=False)
                    key = (cls, round(zo, 2), opn, mur, cas)
            keys.append(key)
        k = 0
        while k < ns:
            key = keys[k]
            j = k
            while j + 1 < ns and keys[j + 1] == key:
                j += 1
            if key is not None:
                out.append(dict(i=i, a=a, u=(ux, uy), n=(nx, ny), t0=k * ln / ns, t1=(j + 1) * ln / ns, ln=ln,
                                cls=key[0], zo=key[1], open=key[2], mur=key[3], cas=key[4]))
            k = j + 1
    return out


def stair_hit(x, y, pad=1.0):
    for nm, foot, deg, w, n, tread, g in L.STAIRS:
        if L.point_in_poly(x, y, sg_col.stair_footprint(nm, pad=pad)):
            return True
    return False


def masonry(mb, R, z0, z1, rng, depth=0.45, course=1.9, m=BLOCK, t0=None, t1=None):
    """alvenaria em fiadas sobre a face da aresta (blocos com junta, desencontrados), de z0 a z1"""
    a, u, nrm = R["a"], R["u"], R["n"]
    t0 = R["t0"] if t0 is None else t0
    t1 = R["t1"] if t1 is None else t1
    H = z1 - z0
    if H < 0.5 or t1 - t0 < 0.8:
        return
    nc = max(1, int(round(H / course)))
    hc = H / nc
    for c in range(nc):
        zc = z0 + c * hc
        pos = t0 - (rng.uniform(0.8, 2.6) if c % 2 else 0.0)
        while pos < t1 - 0.3:
            bl = rng.uniform(3.0, 5.4)
            p0, p1 = max(pos, t0), min(pos + bl, t1)
            pos += bl
            if p1 - p0 < 0.7:
                continue
            tm = (p0 + p1) / 2
            x = a[0] + u[0] * tm + nrm[0] * 0.3
            y = a[1] + u[1] * tm + nrm[1] * 0.3
            if stair_hit(x, y, pad=0.6):
                continue
            d = depth + rng.uniform(-0.1, 0.1)
            ebox(mb, a, u, nrm, p0 + 0.09, p1 - 0.09, -0.06, d, zc + 0.08, zc + hc - 0.08, m)


def coping(mb, R, z, w=1.3, h=0.7):
    """arremate claro na crista (topo 0,05 abaixo da cota: nao briga com o piso)"""
    ebox(mb, R["a"], R["u"], R["n"], R["t0"] - 0.1, R["t1"] + 0.1, 0.0, w, z - h, z - 0.05, TRIM)


def parapet(mb, R, z, rng, pier_step=11.0):
    """guarda-corpo visual sobre a guarda invisivel do sg_col (faixa 0..1 para fora da borda): corpo, capa clara,
    pilaretes nas pontas e a cada ~11"""
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    if t1 - t0 < 1.0:
        return
    ebox(mb, a, u, nrm, t0, t1, 0.05, 0.95, z - 0.05, z + 1.85, BLOCK)
    ebox(mb, a, u, nrm, t0 - 0.05, t1 + 0.05, -0.1, 1.15, z + 1.85, z + 2.15, TRIM)
    L_ = t1 - t0
    npier = max(1, int(round(L_ / pier_step)))
    for k in range(npier + 1):
        t = t0 + L_ * k / npier
        t = min(max(t, t0 + 0.95), t1 - 0.95)
        ebox(mb, a, u, nrm, t - 0.75, t + 0.75, -0.15, 1.3, z - 0.05, z + 2.5, BLOCK)
        ebox(mb, a, u, nrm, t - 0.9, t + 0.9, -0.3, 1.45, z + 2.5, z + 2.8, TRIM)


def buttresses(mb, R, z0, z1, rng, spacing=17.0):
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    L_ = t1 - t0
    nb = int(L_ / spacing)
    if nb < 1:
        return
    sp = L_ / nb
    for k in range(nb):
        t = t0 + sp * (k + 0.5)
        ok = True
        for dt in (-3.0, 0.0, 3.0):
            for dd in (0.5, 2.6, 4.0):
                x = a[0] + u[0] * (t + dt) + nrm[0] * dd
                y = a[1] + u[1] * (t + dt) + nrm[1] * dd
                if stair_hit(x, y, pad=2.5) or water_gap(x, y) or castle_hit(x, y, rects=False):
                    ok = False
        if not ok:
            continue
        h1 = (z1 - z0) - 1.9
        ebox(mb, a, u, nrm, t - 1.6, t + 1.6, -0.05, 2.5, z0, z0 + h1, BLOCK)
        ebox(mb, a, u, nrm, t - 1.8, t + 1.8, -0.05, 2.75, z0 + h1, z0 + h1 + 0.35, TRIM)
        ebox(mb, a, u, nrm, t - 1.25, t + 1.25, -0.05, 1.45, z0 + h1 + 0.35, z1, BLOCK)
        ebox(mb, a, u, nrm, t - 1.8, t + 1.8, -0.05, 0.6, z0 - 0.02, z0 + 0.5, TRIM)     # soco (base clara)
        cx = a[0] + u[0] * t + nrm[0] * 1.25
        cy = a[1] + u[1] * t + nrm[1] * 1.25
        col_box("SG_TerButtress", (3.2, 2.5, z1 - z0 + 0.05), (cx, cy, (z0 + z1) / 2),
                (0, 0, math.atan2(u[1], u[0])))


def corbels(mb, R, z, step=2.6):
    """cachorros sob a capa do arremate (o parapeito avanca sobre a face do arrimo)"""
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    nc = int((t1 - t0) / step)
    for k in range(nc):
        t = t0 + step * (k + 0.5)
        x = a[0] + u[0] * t + nrm[0] * 0.5
        y = a[1] + u[1] * t + nrm[1] * 0.5
        if stair_hit(x, y, pad=0.4):
            continue
        ebox(mb, a, u, nrm, t - 0.4, t + 0.4, 0.2, 1.15, z - 1.5, z - 0.7, TRIM)


def rock_base(mb, R, zb, ztop, rng):
    """base de basalto em colunas diante da face alta que da para o terreno bravo"""
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    L_ = t1 - t0
    nc = max(1, int(L_ / 4.3))
    for k in range(nc):
        t = t0 + L_ * (k + 0.5 + rng.uniform(-0.2, 0.2)) / nc
        r = rng.uniform(2.3, 3.4)
        d = r * rng.uniform(0.55, 1.0)
        cx = a[0] + u[0] * t + nrm[0] * d
        cy = a[1] + u[1] * t + nrm[1] * d
        zt = ztop + rng.uniform(-1.8, 1.8)
        cx, cy, zt = water_fix(cx, cy, r, zt)
        zt = cap_top(cx, cy, r, zt)
        if zt < zb + 1.0 or not dun_ok(cx, cy, r, zb - 1.4, zt) or castle_hit(cx, cy, r):
            continue
        grass = rng.random() < 0.45
        column(mb, cx, cy, r, zt, zb - 1.4, rng.uniform(0, 1.05), m=ROCK, cap=GRASS if grass else TOP,
               band=(0.8, TOP))


def quoins(mb, nm, poly, runs, z, rng):
    """cunhais claros nas quinas CONVEXAS de alvenaria"""
    pts = clean(ccw(poly))
    n = len(pts)
    ends = {}
    for R in runs:
        if R["t0"] < 0.6:
            ends.setdefault(R["i"], []).append(("start", R))
        if R["t1"] > R["ln"] - 0.6:
            ends.setdefault((R["i"] + 1) % n, []).append(("end", R))
    for vi, lst in ends.items():
        starts = [R for k, R in lst if k == "start"]
        endsr = [R for k, R in lst if k == "end"]
        if not starts or not endsr:
            continue
        Rs, Re = starts[0], endsr[0]
        cross = Re["u"][0] * Rs["u"][1] - Re["u"][1] * Rs["u"][0]
        if cross <= 0.05:
            continue
        v = pts[vi]
        nx, ny = Re["n"][0] + Rs["n"][0], Re["n"][1] + Rs["n"][1]
        ln = math.hypot(nx, ny) or 1.0
        cx, cy = v[0] + nx / ln * 0.75, v[1] + ny / ln * 0.75
        z0 = min(Rs["zo"], Re["zo"]) - (0.3 if min(Rs["zo"], Re["zo"]) >= SH - 0.1 else 0.0)
        ang = math.atan2(Rs["u"][1], Rs["u"][0])
        mb.box((1.9, 1.9, z - 0.75 - z0), (cx, cy, (z0 + z - 0.75) / 2), (0, 0, ang), TRIM, 0)


def terrace_edges():
    rng = random.Random(3101)
    for nm, poly, z, pr in L.floors():
        if nm not in ("P1", "P2", "P3"):
            continue
        mb = smb("SG_Ter_Wall_" + nm)
        mr = smb("SG_Ter_Terrace_" + nm)
        runs = edge_runs(nm, poly, z)
        runs = [R for R in runs if not R["cas"]]        # o castelo cobre esses trechos (cortina, torres)
        for R in runs:
            zo = R["zo"]
            if R["cls"] == "terrace":
                top = z - (0.6 if R["mur"] else 0.7)
                masonry(mb, R, zo, top, rng)
                if R["mur"]:
                    # cordao claro entre o arrimo e a muralha do castelo (face externa em y -9)
                    ebox(mb, R["a"], R["u"], R["n"], R["t0"], R["t1"], -0.02, 0.55, z - 0.6, z - 0.05, TRIM)
                else:
                    coping(mb, R, z)
                    corbels(mb, R, z)
                    if not R["open"]:
                        parapet(mb, R, z, rng)
                buttresses(mb, R, zo, top, rng)
                ebox(mb, R["a"], R["u"], R["n"], R["t0"], R["t1"], -0.02, 0.75, zo - 0.02, zo + 0.55, TRIM)   # soco
            else:
                drop = z - zo
                if drop <= 3.0:                      # P1: meio-fio sobre o ombro
                    masonry(mb, R, zo - 0.4, z - 0.7, rng, course=2.4)
                else:                                # P2/P3: base de rocha + faixa de alvenaria
                    band = 7.6 if drop > 12.0 else 4.4
                    masonry(mb, R, z - band, z - 0.7, rng)
                    rock_base(mr, R, zo, z - band + rng.uniform(0.6, 2.4), rng)
                coping(mb, R, z)
                if not R["open"]:
                    parapet(mb, R, z, rng)
        quoins(mb, nm, poly, runs, z, rng)


# ------------------------------------------------------------------ entrada: espinha baixa + meio-fios
def neck():
    """terreno bravo do pescoco da entrada: duas faixas de grama/rocha MAIS BAIXAS que a calcada (26,2 ao lado do
    patio baixo, subindo com a escadaria ate 34,2), o corpo do pescoco e os meio-fios do patio e da calcada"""
    me = smb("SG_Ter_Terrace_Entry")
    rng = random.Random(3203)
    ys = [p[1] for p in RIM]
    ymin = min(ys)
    rows = []
    y = ymin + 0.4
    while y < CUT_Y - 0.01:
        rows.append(y)
        y += 2.0
    rows += [STAIR_Y0 - 0.05, STAIR_Y0 + 0.05, CUT_Y]
    rows = sorted(set(round(v, 3) for v in rows if ymin + 0.3 <= v <= CUT_Y))
    for s in (-1, 1):
        ring_rows = []
        for y in rows:
            iv = SL.x_intervals(RIM, y)
            if not iv:
                continue
            xs = [x for pr in iv for x in pr]
            xo = min(xs) if s < 0 else max(xs)
            xi = s * (13.0 if y <= STAIR_Y0 else NECK_STAIR_X)
            if abs(xo) - abs(xi) < 0.6:
                continue
            ring_rows.append((y, xi, xo, neck_z(y)))
        bm = me.bm
        rings = []
        for y, xi, xo, zt in ring_rows:
            rings.append([bm.verts.new((xi, y, zt)), bm.verts.new((xo, y, zt)), bm.verts.new((xo, y, 23.0)),
                          bm.verts.new((xi, y, 23.0))])
        if len(rings) < 2:
            continue
        tops = []
        for r0, r1 in zip(rings, rings[1:]):
            for k in range(4):
                k2 = (k + 1) % 4
                f = bm.faces.new((r0[k], r0[k2], r1[k2], r1[k]))
                if k == 0:
                    tops.append(f)
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
        me._post([v for rg in rings for v in rg], DARK, None, 0, 1)
        mi = me._mi_for(GRASS)
        for f in tops:
            f.material_index = mi
    # corpo do pescoco (sob o patio baixo, a escadaria e as faixas) - base da massa de baixo
    neck_poly = SL.clip(RIM, 0.0, 1.0, CUT_Y)          # y <= -188
    prism2(smb("SG_Ter_Cliff_S"), neck_poly, CORE_BOT, 26.0, DARK)
    # meio-fios: patio baixo (lados), calcada alta (lados) - a entrada poe os parapeitos em cima
    x0, y0, x1, y1 = L.ENTRY_LOW
    for s in (-1, 1):
        xe = x1 if s > 0 else x0
        a = (xe, y0) if s > 0 else (xe, y1)
        u = (0.0, 1.0) if s > 0 else (0.0, -1.0)
        R = dict(a=a, u=u, n=(u[1], -u[0]), t0=0.0, t1=y1 - y0)
        masonry(me, R, NECK_LOW - 0.4, DECK - 0.35, rng, course=2.4)     # o parapeito da entrada assenta em cima
    # face sul do patio baixo (encontro com a ponte de chegada)
    R = dict(a=(x0, y0), u=(1.0, 0.0), n=(0.0, -1.0), t0=0.0, t1=x1 - x0)
    masonry(me, R, 25.6, DECK - 0.05, rng)
    hx0, hy0, hx1, hy1 = L.ENTRY_HIGH
    for s in (-1, 1):
        xe = hx1 if s > 0 else hx0
        a = (xe, hy0) if s > 0 else (xe, -164.0)
        u = (0.0, 1.0) if s > 0 else (0.0, -1.0)
        R = dict(a=a, u=u, n=(u[1], -u[0]), t0=0.0, t1=-164.0 - hy0)
        masonry(me, R, SH - 0.4, P1 - 0.35, rng, course=2.4)


# ------------------------------------------------------------------ ombro + massa (setores)
def core():
    """ombro de grama (34,2) sobre o nucleo escuro, e a massa de baixo afinando LOGO abaixo da face (1,5): bandas
    recuadas escondidas entre as colunas pendentes. Fatiado em 6 setores."""
    top = SL.clip(RIM, 0.0, -1.0, -CUT_Y)              # y >= -188
    # camadas: ombro (32,5..34,2) fatiado por setor; o MEIO (1,5..32,5) so e cortado por linhas que nao passam pela
    # caixa da dungeon (y 40 e x -78 / 82): nenhuma face interna atravessa as salas
    zlo, zhi = KZ0 - 0.5, KZ1 + 0.5
    for nm, w in sector_wedges(top).items():
        prism2(smb("SG_Ter_Cliff_" + nm), w, zhi, SH, DARK, m_top=GRASS)
    south = SL.clip(top, 0.0, 1.0, KY0 - 10.0)          # y <= 40
    for nm, w in sector_wedges(south).items():
        prism2(smb("SG_Ter_Cliff_" + nm), w, zlo, zhi, DARK)
    north = SL.clip(top, 0.0, -1.0, -(KY0 - 10.0))      # y >= 40
    xw, xe = KX0 - 8.0, KX1 + 8.0
    parts = [("NW", SL.clip(north, 1.0, 0.0, xw)), ("N", SL.clip(SL.clip(north, -1.0, 0.0, -xw), 1.0, 0.0, xe)),
             ("NE", SL.clip(north, -1.0, 0.0, -xe))]
    for nm, w in parts:
        prism2(smb("SG_Ter_Cliff_" + nm), w, zlo, zhi, DARK)
    for f, z0, z1 in BANDS:
        poly = scaled(RIM, f, C)
        for nm, w in sector_wedges(poly).items():
            prism2(smb("SG_Ter_Cliff_" + nm), w, z0, z1, DARK)


# bandas do nucleo de baixo (fator de escala do contorno, z0, z1) e aneis de colunas pendentes
BANDS = [(0.93, -12.0, KZ0 - 0.5), (0.82, -30.0, -12.0), (0.68, -50.0, -30.0), (0.52, -70.0, -50.0),
         (0.36, -88.0, -70.0), (0.20, -100.0, -88.0)]
RINGS = [(0.88, -10.0, (-44.0, -30.0), (4.4, 6.0), 1.3), (0.74, -28.0, (-62.0, -48.0), (5.0, 6.6), 1.3),
         (0.60, -48.0, (-80.0, -68.0), (5.4, 7.0), 1.3), (0.44, -68.0, (-96.0, -86.0), (5.8, 7.0), 1.2),
         (0.28, -86.0, (-102.0, -97.0), (6.0, 6.8), 1.1)]


def block_mesh(mb, outer, inner, T, zs, z0, apex, cap, rng):
    """bloco de basalto: contorno (face externa canelada + costas retas) extrudado de T ate z0, estrato (degrau) em
    zs, e o fundo fechando numa ponta facetada (apex = (x, y, z)). Faces: topo=cap, faixa de 1,0 = TOP (luar),
    face = ROCK ate o estrato, abaixo = DARK."""
    poly = clean(ccw(outer + inner[::-1]))
    n = len(poly)
    if n < 3:
        return
    bm = mb.bm
    gx = sum(p[0] for p in poly) / n
    gy = sum(p[1] for p in poly) / n
    ox, oy = apex[0] - gx, apex[1] - gy
    ol = math.hypot(ox, oy) or 1.0

    def ring(pts, z):
        return [bm.verts.new((x, y, z)) for x, y in pts]
    lower = [(gx + (x - gx) * 0.9 + ox / ol * 0.5, gy + (y - gy) * 0.9 + oy / ol * 0.5) for x, y in poly]
    seq = [(ring(poly, T), None), (ring(poly, T - 1.0), TOP)]
    if z0 + 1.0 < zs < T - 2.5:
        seq.append((ring(poly, zs), ROCK))
        seq.append((ring(lower, zs), DARK))
        seq.append((ring(lower, z0), DARK))
    else:
        seq.append((ring(poly, z0), ROCK))
    top = bm.faces.new(seq[0][0])
    groups = {}
    for (a, _), (b, mm) in zip(seq, seq[1:]):
        for k in range(n):
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last = seq[-1][0]
    av = bm.verts.new(apex)
    for k in range(n):
        groups.setdefault(DARK, []).append(bm.faces.new((last[(k + 1) % n], last[k], av)))
    allv = [v for rg, _ in seq for v in rg] + [av]
    mb._post(allv, ROCK, None, 0, 1)
    top.material_index = mb._mi_for(cap)
    for mm, fs in groups.items():
        if mm != ROCK:
            mi = mb._mi_for(mm)
            for f in fs:
                f.material_index = mi


def rim_tags(smp):
    """marca as amostras da borda que caem sob uma ponte (topo limitado) ou na frente de uma cachoeira (bloco
    recuado atras da cortina, topo sob o labio): o bloco nunca atravessa uma troca de marca"""
    tags = []
    for x, y, nx, ny in smp:
        tag = None
        for nm, a, b, z, w in BRIDGES:
            if sg_col._in_rect_along(x, y, a, b, w / 2 + 3.5, pad=6.0):
                tag = ("B", round(z - 2.6, 2))
        for wi, (wx, wy, wz, ux, uy) in enumerate(FALLS):
            lat = abs(-(x - wx) * uy + (y - wy) * ux)
            along = (x - wx) * ux + (y - wy) * uy
            if lat < 6.5 and -9.0 < along < 9.0:
                tag = ("W", wi)
        tags.append(tag)
    return tags


def rim_cliff():
    """coroa do penhasco em BLOCOS (a leitura da concept): cada bloco e uma massa de basalto com a face canelada
    (colunas), topo de grama num nivel proprio (alguns blocos descem um degrau), recuado/avancado em relacao ao
    vizinho, fenda escura entre blocos, estrato claro/escuro e fundo fechando em ponta pendente; poucos pilares
    destacados na frente"""
    rng = random.Random(3301)
    smp = resample_closed(RIM, 1.0)
    N = len(smp)
    tags = rim_tags(smp)
    i = 0
    nblk = 0
    prev_t = None
    while i < N - 3:
        W = int(rng.uniform(13.0, 24.0))
        tag = tags[i]
        j = i
        while j < min(N - 1, i + W) and tags[j + 1] == tag:
            j += 1
        W = j - i
        if W < 3:
            i = j + 1
            continue
        mid = smp[i + W // 2]
        base = wild_z(mid[0], mid[1])
        T = base - rng.uniform(3.5, 8.0) if rng.random() < 0.33 else base + rng.uniform(-0.8, 3.6)
        if prev_t is not None and abs(T - prev_t) < 1.4:
            T += 1.8 if T < prev_t else -1.4
        dout = rng.uniform(-1.2, 2.2)
        if tag and tag[0] == "B":
            T = min(T, tag[1])
        if tag and tag[0] == "W":
            wx, wy, wz, ux, uy = FALLS[tag[1]]
            T = min(T, wz - 0.5)
            dout = -2.0
        depth = rng.uniform(5.5, 7.5)
        per = rng.uniform(3.6, 5.4)
        outer, inner = [], []
        t = 0.0
        k = 0
        while t <= W + 0.01:
            x, y, nx, ny = smp[min(N - 1, i + int(round(t)))]
            d = dout + ((0.45 + rng.uniform(-0.2, 0.2)) if k % 2 == 0 else -0.75)
            outer.append((x + nx * d, y + ny * d))
            t += per / 2
            k += 1
        for q in range(0, W + 1, max(1, W // 4)):
            x, y, nx, ny = smp[i + q]
            inner.append((x - nx * (depth - dout), y - ny * (depth - dout)))
        if inner[-1] != (smp[i + W][0] - smp[i + W][2] * (depth - dout), smp[i + W][1] - smp[i + W][3] * (depth - dout)):
            x, y, nx, ny = smp[i + W]
            inner.append((x - nx * (depth - dout), y - ny * (depth - dout)))
        # nao furar piso andavel: topo abaixo da cota do patamar que o bloco invade
        for px, py in outer + inner:
            z = L.zone_of(px, py)
            if z is not None:
                T = min(T, z - 0.3)
        prev_t = T
        zs = T - rng.uniform(16.0, 26.0)
        z0 = min(zs - 4.0, rng.uniform(-8.0, 4.0))
        x, y, nx, ny = mid
        zap = rng.uniform(-50.0, -30.0)
        apex = (x + nx * (dout + 1.5), y + ny * (dout + 1.5), zap)
        grass = T >= base - 0.9
        gx = sum(p[0] for p in outer) / len(outer)
        gy = sum(p[1] for p in outer) / len(outer)
        if not dun_ok(gx, gy, W, zap, T):
            print("TER AVISO bloco da borda na caixa da dungeon", round(gx, 1), round(gy, 1))
        else:
            block_mesh(cliff_mb(gx, gy), outer, inner, T, zs, z0, apex, GRASS if grass else TOP, rng)
            nblk += 1
        # pilar destacado diante do bloco (poucos: profundidade, nao cerca)
        if not tag and rng.random() < 0.3:
            x, y, nx, ny = smp[i + int(W * rng.uniform(0.3, 0.7))]
            r2 = rng.uniform(2.6, 3.4)
            d2 = dout + 1.0 + r2 * 1.1
            px, py = x + nx * d2, y + ny * d2
            zt2 = T - rng.uniform(6.0, 14.0)
            zb2 = zt2 - rng.uniform(28.0, 46.0)
            px, py, zt2 = water_fix(px, py, r2, zt2)
            zt2 = cap_top(px, py, r2, zt2)
            if zt2 - zb2 > 8.0 and dun_ok(px, py, r2, zb2 - r2 * 1.5, zt2):
                column(cliff_mb(px, py), px, py, r2, zt2, zb2, rng.uniform(0, 1.05), m=ROCK,
                       cap=GRASS if rng.random() < 0.5 else TOP, band=(0.9, TOP),
                       strata=(zt2 - rng.uniform(7.0, 12.0), 0.86, (nx * 0.3, ny * 0.3)), low=DARK, tip=r2 * 1.5)
        gap = int(rng.uniform(3.0, 6.0)) if (j + 1 < N and tags[min(N - 1, j + 1)] == tag) else 1
        i += W + gap
    return nblk


def under():
    """massa de baixo: aneis de colunas pendentes (cada anel pendurado na banda de cima) afinando ate ~-108"""
    rng = random.Random(3401)
    for f, ztop, (zb0, zb1), (r0, r1), tk in RINGS:
        ravg = (r0 + r1) / 2
        for x, y, nx, ny in resample_closed(scaled(RIM, f, C), ravg * 1.45):
            r = rng.uniform(r0, r1)
            cx, cy = x + nx * rng.uniform(-0.8, 1.2), y + ny * rng.uniform(-0.8, 1.2)
            zt = ztop + rng.uniform(0.0, 2.0)
            zb = rng.uniform(zb0, zb1)
            zs = (zt + zb) / 2 + rng.uniform(-3.0, 3.0)
            column(cliff_mb(cx, cy), cx, cy, r, zt, zb, rng.uniform(0, 1.05), m=ROCK, cap=DARK,
                   strata=(zs, 0.8, (nx * 0.6, ny * 0.6)), low=DARK, tip=r * tk)
    for k in range(4):
        a = k * 2 * math.pi / 3 + 0.4
        d = 0.0 if k == 3 else 6.0
        cx, cy = C[0] + d * math.cos(a), C[1] + d * math.sin(a)
        column(cliff_mb(cx + 0.01, cy), cx, cy, 5.0, -98.0, -102.0 - (1.5 if k == 3 else 0.0),
               rng.uniform(0, 1.05), m=DARK, cap=DARK, tip=4.5)


def spires():
    """CLIFF_SPIRES: aglomerados de colunas altas e grossas na borda (silhueta vertical, topo de grama)"""
    rng = random.Random(3501)
    for x, y, r, top_z, kind in L.CLIFF_SPIRES:
        mb = cliff_mb(x, y)
        cols = [(0.0, 0.0, 0.5, 0.0)]
        for k in range(2):
            a = rng.uniform(0, 2 * math.pi)
            cols.append((a, r * 0.5, 0.42, rng.uniform(3.0, 9.0)))
        for k in range(4):
            a = 2 * math.pi * k / 4 + rng.uniform(-0.5, 0.5)
            cols.append((a, r * rng.uniform(0.55, 0.75), rng.uniform(0.3, 0.36), rng.uniform(14.0, 26.0)))
        for a, d, fr, dz in cols:
            rc = r * fr
            px, py = x + d * math.cos(a), y + d * math.sin(a)
            zt = top_z - dz
            zb = rng.uniform(-44.0, -24.0)
            px, py, zt = water_fix(px, py, rc, zt)
            zt = cap_top(px, py, rc, zt)
            if not dun_ok(px, py, rc, zb - rc * 1.5, zt):
                continue
            zs = zt - rng.uniform(12.0, 20.0)
            column(mb, px, py, rc, zt, zb, rng.uniform(0, 1.05), m=ROCK, cap=GRASS if dz < 10.0 else TOP,
                   band=(1.2, TOP), strata=(zs, 0.86, (0.0, 0.0)), low=DARK, tip=rc * 1.6)
        if L.point_in_poly(x, y, L.ISLAND_RIM):
            octo_col("SG_TerSpire", x, y, r * 0.8, 32.5, 32.5 + 20.0)


# pedido do castelo: sem os montes (-86,60) e (-88,100) (a ala oeste x -94..-62, y 65..133 e a massa ali);
# (-74,150,r16) -> (-84,162,r12); (-96,14) -> (-102,14) (libera a torre da cortina em (-82,16) r5,5)
MOUNDS = [(-84.0, 162.0, 12.0, 76.0), (86.0, 128.0, 16.0, 72.0), (100.0, 160.0, 12.0, 66.0),
          (-102.0, 14.0, 10.0, 58.0)]


def mounds():
    """os 6 montes do blockout viram MESAS de basalto em colunas: miolo de colunas no mesmo topo de grama (h),
    aneis de fora em degraus mais baixos (escalonado), face de sulcos verticais. Colisao octo_col mantida."""
    rng = random.Random(3601)
    mb = smb("SG_Ter_Mounds")
    for idx, (x, y, r, h) in enumerate(MOUNDS):
        s = 5.8
        pts = []
        row = 0
        yy = -r
        while yy <= r:
            xx = -r + (s / 2 if row % 2 else 0.0)
            while xx <= r:
                px, py = xx + rng.uniform(-0.5, 0.5), yy + rng.uniform(-0.5, 0.5)
                if math.hypot(px, py) <= r * 0.96:
                    pts.append((px, py))
                xx += s
            yy += s * 0.866
            row += 1
        step1 = rng.uniform(5.0, 9.0)
        step2 = step1 + rng.uniform(7.0, 12.0)
        for px, py in pts:
            d = math.hypot(px, py) / r
            rc = rng.uniform(3.0, 3.6)
            cx, cy = x + px, y + py
            if d < 0.45:
                zt = h - rng.uniform(0.0, 0.4)
            elif d < 0.75:
                zt = h - step1 - rng.uniform(0.0, 0.6)
            else:
                zt = h - step2 - rng.uniform(0.0, 3.0)
            zt = max(zt, SH + 3.0)
            # nunca por cima de piso andavel
            if any(L.zone_of(qx, qy) is not None for qx, qy in hex_pts(cx, cy, rc + 0.6)):
                continue
            # junto de um patamar a mesa desce em degrau (o jogador ve a formacao, nao um paredao colado no parapeito)
            zn = [L.zone_of(qx, qy) for qx, qy in hex_pts(cx, cy, rc + 6.0, 12)]
            zn = [z for z in zn if z is not None]
            if zn:
                zt = min(zt, max(zn) + rng.uniform(1.5, 4.5))
            cx, cy, zt = water_fix(cx, cy, rc, zt)
            if not dun_ok(cx, cy, rc, SH - 1.6, zt):
                continue
            column(mb, cx, cy, rc, zt, SH - 1.6, rng.uniform(0, 1.05), m=ROCK, cap=GRASS, band=(1.0, TOP))
        octo_col("SG_TerMound", x, y, r * 0.9, 32.5, h)


def water_lips():
    """labios de pedra das 3 cachoeiras que saem de um patamar (a agua e da zona water): bancada na cota do labio
    ligada a borda do patamar, com margens de colunas. A 4a (sul, 30,2) sai de uma fenda no penhasco (water_fix)."""
    rng = random.Random(3701)
    for wx, wy, wz, ux, uy in FALLS:
        # patamar de origem: recua pelo eixo ate achar piso
        src = None
        for k in range(1, 40):
            bx, by = wx - ux * k * 0.5, wy - uy * k * 0.5
            z = L.zone_of(bx, by)
            if z is not None:
                src = (bx, by, z, k * 0.5)
                break
        if src is None or src[2] - wz > 1.6:
            continue
        mb = cliff_mb(wx, wy)
        L_ = src[3] + 0.8
        vx, vy = -uy, ux
        a = (wx - ux * (L_ - 0.8) - 0.0, wy - uy * (L_ - 0.8))
        poly = [(a[0] - vx * 4.6, a[1] - vy * 4.6), (wx + ux * 0.8 - vx * 4.6, wy + uy * 0.8 - vy * 4.6),
                (wx + ux * 0.8 + vx * 4.6, wy + uy * 0.8 + vy * 4.6), (a[0] + vx * 4.6, a[1] + vy * 4.6)]
        prism2(mb, poly, SH - 1.0, wz - 0.1, ROCK, m_top=TOP)
        for s in (-1, 1):
            nk = max(2, int(L_ / 4.0) + 1)
            for k in range(nk):
                t = (L_ - 0.8) * (1.0 - k / max(1, nk - 1)) + 0.4
                rc = rng.uniform(1.9, 2.5)
                cx = wx - ux * (t - 0.8) + vx * s * (4.6 + rc * 0.9)
                cy = wy - uy * (t - 0.8) + vy * s * (4.6 + rc * 0.9)
                zt = wz + rng.uniform(0.7, 1.6)
                zt = cap_top(cx, cy, rc, zt)
                column(mb, cx, cy, rc, zt, SH - 1.2, rng.uniform(0, 1.05), m=ROCK, cap=GRASS if rng.random() < 0.5 else TOP,
                       band=(0.7, TOP))


# ------------------------------------------------------------------ cristais da borda (refinamento v2: borda viva)
def crystal(mb, base, ax, ln, r, m="SG_Crystal_Glow"):
    """prisma hexagonal apontado (corpo + ponta) com o eixo ax a partir de base (encravado na rocha)"""
    ax = Vector(ax).normalized()
    yaw = math.atan2(ax.y, ax.x)
    pitch = math.acos(max(-1.0, min(1.0, ax.z)))
    rot = (0.0, pitch, yaw)
    b = Vector(base)
    mb.cyl(r, ln * 0.7, b + ax * (ln * 0.35), rot, m=m, n=6, r2=r * 0.8, bevel=0.0)
    mb.cyl(r * 0.8, ln * 0.3, b + ax * (ln * 0.85), rot, m=m, n=6, r2=0.03, bevel=0.0)


def cave_hit(x, y, pad=2.0):
    """caixa DUNGEON_CAVE_MASS (a boca de caverna e do agente da dungeon): nada meu ali"""
    cx0, cy0, cx1, cy1 = L.DUNGEON_CAVE_MASS
    return cx0 - pad < x < cx1 + pad and cy0 - pad < y < cy1 + pad


def crystal_ok(x, y, r, z0, z1):
    """fora da dungeon (keepout + caverna), fora das pontes e fora da frente das cortinas d'agua"""
    if cave_hit(x, y) or not dun_ok(x, y, r, z0, z1):
        return False
    for nm, a, b, z, w in BRIDGES:
        if sg_col._in_rect_along(x, y, a, b, w / 2 + 3.0, pad=4.0):
            return False
    for wx, wy, wz, ux, uy in FALLS:
        lat = abs(-(x - wx) * uy + (y - wy) * ux)
        along = (x - wx) * ux + (y - wy) * uy
        if lat < 5.5 and along > -6.0:
            return False
    return True


def rim_crystals():
    """a borda viva da referencia v2: aglomerados de SG_Crystal_Glow (2-4 prismas inclinados para fora) encravados
    na face EXTERNA dos penhascos, abaixo do topo (fora do alcance do jogador); mais densos perto das quedas e da
    ponta da dungeon. Veios finos SG_VioletDeep_Glow rente a rocha e pontas esparsas nas colunas pendentes de baixo.
    Sem colisao nenhuma."""
    rng = random.Random(4101)
    mb = smb("SG_Ter_Crystals")
    smp = resample_closed(RIM, 1.0)
    N = len(smp)
    # pontos quentes: os 4 labios de cachoeira + a ponta leste da dungeon (fora da caixa da caverna)
    hot = [(wx, wy) for wx, wy, wz, ux, uy in FALLS] + [(136.0, 96.0)]

    def heat(x, y):
        d = min(math.hypot(x - hx, y - hy) for hx, hy in hot)
        return 0.95 if d < 36.0 else 0.5

    groups = 0
    i = 0
    while i < N and groups < 28:
        x, y, nx, ny = smp[i]
        i += int(rng.uniform(16.0, 30.0))
        if rng.random() > heat(x, y):
            continue
        zc = ground_z(x, y)
        zt = zc - rng.uniform(4.5, 11.0)
        gx, gy = x + nx * 0.4, y + ny * 0.4
        if not crystal_ok(gx, gy, 2.5, zt - 8.0, zt + 6.0):
            continue
        sx, sy = -ny, nx
        # 1 cristal-heroi + 1-3 menores encostados: quase verticais com leve inclinacao para FORA (como na
        # referencia, espigoes que crescem das prateleiras da rocha; de lado leem como agulha, nunca como bolha)
        hero_ln = rng.uniform(4.5, 7.5)
        nk = rng.randint(1, 3)
        for k in range(nk + 1):
            f = 1.0 if k == 0 else rng.uniform(0.45, 0.68)
            ln = hero_ln * f
            rr = (0.32 + hero_ln * 0.10) * f
            lat = 0.0 if k == 0 else rng.choice((-1, 1)) * rng.uniform(0.8, 1.5)
            lean = rng.uniform(-0.12, 0.12) if k == 0 else (0.3 * (1 if lat > 0 else -1) + rng.uniform(-0.15, 0.15))
            out = rng.uniform(0.3, 0.7)
            ax = (nx * out + sx * lean, ny * out + sy * lean, 1.0)
            base = (gx + sx * lat + nx * rng.uniform(-1.4, -0.6), gy + sy * lat + ny * rng.uniform(-1.4, -0.6),
                    zt - ln * 0.4 - (0.0 if k == 0 else 0.6))
            crystal(mb, base, ax, ln, rr, m="SG_Crystal_Glow" if k == 0 else "SG_VioletDeep_Glow")
        groups += 1
    # veios finos de energia rente a face da rocha (~10 pontos)
    veins = 0
    tries = 0
    while veins < 10 and tries < 60:
        tries += 1
        x, y, nx, ny = smp[rng.randrange(N)]
        zc = ground_z(x, y)
        zt = zc - rng.uniform(6.0, 15.0)
        if not crystal_ok(x, y, 1.5, zt - 6.0, zt + 1.0):
            continue
        yaw_t = math.atan2(nx, -ny)                    # tangente da borda
        for j in range(rng.randint(2, 3)):
            ln = rng.uniform(2.0, 4.0)
            mb.box((ln, 0.4, 0.34), (x + nx * rng.uniform(-0.6, -0.1) - ny * rng.uniform(-1.2, 1.2),
                                     y + ny * rng.uniform(-0.6, -0.1) + nx * rng.uniform(-1.2, 1.2),
                                     zt - j * rng.uniform(1.4, 2.4)),
                   (0, rng.uniform(-0.4, 0.4), yaw_t), "SG_VioletDeep_Glow", 0.0)
        veins += 1
    # pontas esparsas nas colunas pendentes de baixo (como as ilhotas da referencia)
    tips = 0
    for f, zlo, zhi in ((0.88, -24.0, -6.0), (0.74, -42.0, -22.0), (0.60, -60.0, -42.0)):
        for x, y, nx, ny in resample_closed(scaled(RIM, f, C), 46.0):
            if rng.random() > 0.5:
                continue
            z = rng.uniform(zlo, zhi)
            if not crystal_ok(x + nx * 1.2, y + ny * 1.2, 1.5, z - 6.0, z):
                continue
            crystal(mb, (x - nx * 0.6, y - ny * 0.6, z), (nx * 0.55, ny * 0.55, -1.0),
                    rng.uniform(2.6, 5.0), rng.uniform(0.45, 0.7))
            tips += 1
    # 3 pontas na massa pendente da ilhota do summon
    ssx, ssy = L.SUMMON_C
    for k in range(3):
        a = rng.uniform(0, 2 * math.pi)
        crystal(mb, (ssx + (L.SUMMON_R - 5.0) * math.cos(a), ssy + (L.SUMMON_R - 5.0) * math.sin(a),
                     rng.uniform(-18.0, -4.0)),
                (math.cos(a) * 0.6, math.sin(a) * 0.6, -1.0), rng.uniform(2.0, 3.6), rng.uniform(0.35, 0.5))
    print("TER CRISTAIS grupos=%d veios=%d pontas=%d" % (groups, veins, tips))


# ------------------------------------------------------------------ ilhota do summon
def summon_isle():
    """plataforma redonda propria (topo 40,2 na cota, 24-gono igual a colisao do sg_col) sobre tambor de alvenaria e
    rocha em colunas pendentes; lingua de rocha sob a escada curta (a escada assenta nela)"""
    rng = random.Random(3801)
    mb = smb("SG_Ter_SummonIsle")
    sx, sy = L.SUMMON_C
    R = L.SUMMON_R
    top = [(sx + R * math.cos(math.radians(15.0 * k)), sy + R * math.sin(math.radians(15.0 * k))) for k in range(24)]
    prism2(mb, top, SUM - 1.6, SUM, TRIM, m_top=PAVE)
    drum = [(sx + (R - 0.5) * math.cos(math.radians(15.0 * k)), sy + (R - 0.5) * math.sin(math.radians(15.0 * k)))
            for k in range(24)]
    prism2(mb, drum, 29.0, SUM - 1.6, DARK)
    zc0, zc1 = 33.0, SUM - 1.6
    nc = 3
    hc = (zc1 - zc0) / nc
    for c in range(nc):
        for k in range(24):
            a0 = math.radians(15.0 * k + (7.5 if c % 2 else 0.0))
            a1 = a0 + math.radians(15.0)
            p0 = (sx + (R - 0.5) * math.cos(a0), sy + (R - 0.5) * math.sin(a0))
            p1 = (sx + (R - 0.5) * math.cos(a1), sy + (R - 0.5) * math.sin(a1))
            ux, uy = p1[0] - p0[0], p1[1] - p0[1]
            ln = math.hypot(ux, uy)
            ux, uy = ux / ln, uy / ln
            # a face da lingua (leste) fica sem blocos (a escada encosta la)
            am = math.degrees((a0 + a1) / 2) % 360.0
            if am < 22.0 or am > 338.0:
                continue
            ebox(mb, p0, (ux, uy), (uy, -ux), 0.1, ln - 0.1, -0.05, 0.5 + rng.uniform(-0.08, 0.08),
                 zc0 + c * hc + 0.08, zc0 + (c + 1) * hc - 0.08, BLOCK)
    # nucleo em discos afinando
    for rr, z0, z1 in ((R - 3.0, 4.0, 29.5), (13.0, -18.0, 4.0), (7.0, -36.0, -18.0)):
        prism2(mb, [(sx + rr * math.cos(math.radians(22.5 * k)), sy + rr * math.sin(math.radians(22.5 * k)))
                    for k in range(16)], z0, z1, DARK)
    # rocha: 5 blocos canelados em arco (mesma familia da borda da ilha), cada um com topo e ponta proprios
    a0 = rng.uniform(0.0, 20.0)
    for k in range(5):
        aa = math.radians(a0 + 72.0 * k + 6.0)
        ab = math.radians(a0 + 72.0 * (k + 1) - 6.0)
        dout = rng.uniform(-0.6, 1.2)
        outer, inner = [], []
        m = 12
        for q in range(m + 1):
            t = aa + (ab - aa) * q / m
            rr = R - 0.3 + dout + ((0.45 + rng.uniform(-0.2, 0.2)) if q % 2 == 0 else -0.75)
            outer.append((sx + rr * math.cos(t), sy + rr * math.sin(t)))
        for q in range(5):
            t = aa + (ab - aa) * q / 4
            inner.append((sx + (R - 8.0) * math.cos(t), sy + (R - 8.0) * math.sin(t)))
        T = rng.uniform(30.5, 33.4)
        am = (aa + ab) / 2
        apex = (sx + (R - 3.0) * math.cos(am), sy + (R - 3.0) * math.sin(am), rng.uniform(-36.0, -14.0))
        block_mesh(mb, outer, inner, T, T - rng.uniform(10.0, 17.0), rng.uniform(-2.0, 6.0), apex, TOP, rng)
    # colunas pendentes do miolo (o fundo afina ate a ponta)
    for n, rad, rr0, rr1, zt0, zt1, zb0, zb1 in ((9, 11.0, 4.0, 4.8, 2.0, 3.5, -44.0, -26.0),
                                                  (3, 3.5, 4.0, 4.6, -17.0, -16.0, -58.0, -48.0)):
        for k in range(n):
            a = 2 * math.pi * (k + rng.uniform(-0.15, 0.15)) / n + 0.2
            cx, cy = sx + rad * math.cos(a), sy + rad * math.sin(a)
            r = rng.uniform(rr0, rr1)
            zt = rng.uniform(zt0, zt1)
            zb = rng.uniform(zb0, zb1)
            zs = (zt + zb) / 2 + rng.uniform(-3.0, 3.0)
            column(mb, cx, cy, r, zt, zb, rng.uniform(0, 1.05), m=ROCK, cap=TOP, band=(0.8, TOP),
                   strata=(zs, 0.84, (math.cos(a) * 0.4, math.sin(a) * 0.4)), low=DARK, tip=r * 1.4)
    # lingua sob a escada do summon (do fim da ponte ate a borda da plataforma)
    foot, deg, w, n, tread, g = L.stair_frame("Summon")
    xa, xb = foot[0] + 0.4, sx + R - 1.0
    ya, yb = foot[1] - w / 2 - 1.3, foot[1] + w / 2 + 1.3
    prism2(mb, [(xb, ya), (xa, ya), (xa, yb), (xb, yb)], 30.0, P1, DARK)
    for k, (dx, dy) in enumerate(((-2.5, -4.5), (-2.8, 4.4), (-6.2, 0.2))):
        cx, cy = foot[0] + dx, foot[1] + dy
        column(mb, cx, cy, rng.uniform(2.4, 3.0), 30.4, rng.uniform(8.0, 18.0), rng.uniform(0, 1.05), m=ROCK,
               cap=DARK, low=DARK, tip=3.6)


# ------------------------------------------------------------------ build
def build():
    _MB.clear()
    check_star()
    terraces()
    core()
    neck()
    terrace_edges()
    rim_cliff()
    under()
    spires()
    mounds()
    water_lips()
    summon_isle()
    rim_crystals()
    for nm in sorted(_MB):
        _MB[nm].finish()
    _MB.clear()
