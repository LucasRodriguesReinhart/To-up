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
#   7. OVERHAUL 13 (2026-09-29): kit de cantaria nos arrimos/parapeitos, promontorios + estratos na coroa, cone
#      escalonado + quilhas embaixo, cristais em 3 aglomerados (ver o bloco OVERHAUL 13 abaixo).
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

# OVERHAUL 13 "tolerancia zero" (2026-09-29) - terreno e fundo:
#   Tier B onde o jogador encosta (arrimos P1->P2 e P2->P3, parapeitos das bordas) com o KIT DE CANTARIA do castelo
#   (sg_castle.block/ledge/strip) e o pilarete da entrada (sg_entry._post): fiadas de 2 alturas (2,2 / 1,4) com blocos
#   chanfrados de comprimento DIRIGIDO (ciclo fixo, juntas desencontradas), mesa de misulas com arquinhos por vao entre
#   contrafortes (o ritmo quebra a cada contraforte), contrafortes com talude e capa, soco e arremate em perfil,
#   parapeito com plinto, lajes em relevo na face interna, capa em pecas com junta, pedra de canto nas emendas e
#   pilarete SO nas pontas livres (nos). Remate perto do jogador em Stone_SG_TrimLow (14.01), nao o Trim quase branco.
#   Tier C no fundo (so silhueta e massa): coroa do penhasco com 5 PROMONTORIOS (avancam, sobem e pendem em quilha) e
#   2 ESTRATOS horizontais continuos (degrau com a face de cima ao luar) em cotas fixas da ilha inteira; a massa de
#   baixo vira um cone canelado unico + 5 quilhas com as colunas pendentes SO nelas (antes: ~480 colunas iguais em
#   aneis); base de basalto em macicos de 3-5 colunas com vao; faixas de alvenaria do terreno bravo (so vistas de fora)
#   num perfil so com as juntas de fiada em sulco; cristais em 3 aglomerados (dungeon, summon, castelo), sem veios.
import sg_castle as CK
import sg_entry as EN
CAPL = CK.CAPL                      # Stone_SG_TrimLow: remate perto do jogador (14.01)
PAR_M, REL_M = EN.PAR_M, EN.REL_M   # corpo do parapeito / relevo (a mesma dupla da entrada)
COURSES13 = (2.2, 1.4)              # fiadas alternadas do arrimo (13.05)
LEN_TALL = (4.4, 3.6, 5.0, 3.9)     # comprimentos DIRIGIDOS dos blocos (fiada alta / baixa), ciclo fixo
LEN_LOW = (2.9, 3.4, 2.5, 3.1)
ZS_A, ZS_B = 20.0, 6.0              # os 2 estratos continuos da coroa do penhasco (cota fixa na ilha inteira)
# promontorios da coroa (x, y, meia-largura): NW sob a ala oeste do castelo, N, NE, SE (saida) e SW (summon)
PROMS = [(-118.0, 120.0, 22.0), (60.0, 196.0, 22.0), (122.0, 118.0, 18.0), (156.0, -140.0, 17.0),
         (-112.0, -150.0, 17.0)]

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
    # overhaul 13: ilhotas do ceu (borda oeste da ilha em primeiro plano) e penhasco sul-leste visto da ponte de chegada
    "CAM_SGTer_Islets": ((-150.0, -190.0, 70.0), (-300.0, 120.0, 40.0), 24),
    "CAM_SGTer_FromIsle2": ((150.0, -520.0, 60.0), (20.0, -60.0, 20.0), 22),
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


def _W(R):
    """referencial da aresta para o kit do castelo: u ao longo (a partir de a), t para FORA (n), z"""
    return (R["a"], R["u"], R["n"])


def _xy(R, t, d):
    a, u, n = R["a"], R["u"], R["n"]
    return a[0] + u[0] * t + n[0] * d, a[1] + u[1] * t + n[1] * d


def course_heights(H, hs=COURSES13):
    """fiadas alternadas (alta, baixa, alta...) escaladas para fechar H; abaixo de ~2,6 uma fiada so"""
    if H < hs[0] + 0.4:
        return [H]
    n = max(1, int(round(H / (hs[0] + hs[1]) * 2.0)))
    seq = [hs[k % 2] for k in range(n)]
    sc = H / sum(seq)
    return [h * sc for h in seq]


def free_spans(R, t0, t1, d=0.3, pad=0.6, step=0.5):
    """trechos de t0..t1 sem escada (a alvenaria nao entra no volume de uma escada da planta)"""
    out, cur = [], None
    t = t0
    while t <= t1 + 1e-6:
        x, y = _xy(R, t, d)
        ok = not stair_hit(x, y, pad=pad)
        if ok and cur is None:
            cur = t
        if not ok and cur is not None:
            if t - step - cur > 0.8:
                out.append((cur, t - step))
            cur = None
        t += step
    if cur is not None and t1 - cur > 0.8:
        out.append((cur, t1))
    return out


def masonry(mb, R, z0, z1, rng=None, depth=0.45, course=None, m=BLOCK, t0=None, t1=None):
    """alvenaria de arrimo (Tier B, 13.05): fiadas de 2 alturas (2,2 / 1,4) alternadas, blocos do kit do castelo
    (face chanfrada 0,09 = le cantaria sem textura) com comprimento de um CICLO FIXO por fiada (juntas desencontradas
    de fiada para fiada), fiada baixa 0,07 mais recuada (a sombra marca as fiadas). Junta de 0,1 mostra o nucleo escuro."""
    W = _W(R)
    t0 = R["t0"] if t0 is None else t0
    t1 = R["t1"] if t1 is None else t1
    H = z1 - z0
    if H < 0.5 or t1 - t0 < 0.8:
        return
    zc = z0
    for c, hc in enumerate(course_heights(H)):
        tall = c % 2 == 0
        lens = LEN_TALL if tall else LEN_LOW
        dep = depth if tall else depth - 0.07
        for s0, s1 in free_spans(R, t0, t1):
            k = (c * 3 + int(s0)) % 4
            pos = s0 - (0.0 if tall else lens[k] * 0.45)
            while pos < s1 - 0.05:
                bl = lens[k % 4]
                k += 1
                if s1 - (pos + bl) < 0.9:              # sobra curta: o bloco vai ate a ponta
                    bl = s1 - pos
                p0, p1 = max(pos, s0), min(pos + bl, s1)
                pos += bl
                if p1 - p0 < 0.5:
                    continue
                CK.block(mb, W, p0 + 0.05, p1 - 0.05, zc + 0.05, zc + hc - 0.05, -0.06, dep, 0.09, m)
        zc += hc


def band_face(mb, R, z0, z1, depth=0.45, m=BLOCK):
    """faixa de alvenaria de FUNDO (Tier C: face externa do terreno bravo, so vista de fora): um perfil so, com as
    juntas das 2 alturas de fiada em sulco (a leitura de fiada fica, o custo e de uma peca por trecho)"""
    if z1 - z0 < 0.5:
        return
    hs = course_heights(z1 - z0)
    prof = [(-0.06, z0), (depth, z0)]
    zc = z0
    for h in hs[:-1]:
        zc += h
        prof += [(depth, zc - 0.1), (depth - 0.17, zc), (depth, zc + 0.1)]
    prof += [(depth, z1), (-0.06, z1)]
    for s0, s1 in free_spans(R, R["t0"], R["t1"]):
        CK.ledge(mb, _W(R), s0, s1, prof, m)


def coping(mb, R, z, w=1.3, h=0.7, ext=(0.1, 0.1)):
    """arremate da crista em perfil (TrimLow): aresta de fora chanfrada e pingadeira; topo 0,05 abaixo da cota"""
    prof = [(0.0, z - h), (w - 0.14, z - h), (w - 0.14, z - h + 0.12), (w, z - h + 0.2), (w, z - 0.22),
            (w - 0.17, z - 0.05), (0.0, z - 0.05)]
    CK.ledge(mb, _W(R), R["t0"] - ext[0], R["t1"] + ext[1], prof, CAPL)


PAR_TOP = 1.72                      # topo do corpo do parapeito (acima da cota); capa ate +2,04
CAP_LEN = (3.8, 3.2)                # pecas da capa (ritmo A-B)
SLAB_LEN = (3.8, 4.4)               # lajes da face interna


def parapet(mb, R, z, rng=None, ext=(0.0, 0.0)):
    """parapeito das bordas (Tier B, 13.06 = receita 01.03/13.05) sobre a guarda invisivel do sg_col (faixa 0..1
    para fora): corpo com PLINTO na face interna (um perfil), LAJES em relevo raso chanfradas na face que o jogador ve,
    capa em PECAS com junta e aresta interna chanfrada. ext = prolongamento do corpo nas emendas (cobre a cunha de fora
    do canto; a pedra de canto cobre a emenda da capa)."""
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    if t1 - t0 < 1.0:
        return
    W = _W(R)
    body = [(-0.1, z - 0.05), (0.95, z - 0.05), (0.95, z + PAR_TOP), (0.05, z + PAR_TOP), (0.05, z + 0.6),
            (-0.1, z + 0.44)]
    CK.ledge(mb, W, t0 - ext[0], t1 + ext[1], body, PAR_M)
    # lajes (ortostatos) em relevo 0,07 na face interna, entre o plinto e a capa
    k = int(abs(a[0] * 7.0 + a[1] * 3.0)) % 2
    pos = t0 + 0.12
    while pos < t1 - 0.4:
        bl = SLAB_LEN[k % 2]
        k += 1
        if t1 - 0.12 - (pos + bl) < 1.2:
            bl = t1 - 0.12 - pos
        CK.block(mb, W, pos + 0.04, pos + bl - 0.04, z + 0.66, z + PAR_TOP - 0.1, 0.06, -0.02, 0.07, REL_M)
        pos += bl
    # capa em pecas: aresta interna chanfrada (a que o jogador ve), sobra 0,2 para cada lado
    zc = z + PAR_TOP
    cap = [(-0.22, zc), (1.17, zc), (1.17, zc + 0.3), (-0.07, zc + 0.3)]      # face interna em talude (chanfro)
    k = int(abs(a[0] * 3.0 + a[1] * 7.0)) % 2
    pos = t0
    while pos < t1 - 0.05:
        bl = CAP_LEN[k % 2]
        k += 1
        if t1 - (pos + bl) < 1.2:
            bl = t1 - pos
        CK.ledge(mb, W, pos + (0.03 if pos > t0 else 0.0), pos + bl - (0.03 if pos + bl < t1 - 1e-6 else 0.0), cap,
                 CAPL)
        pos += bl


def corner_stone(mb, x, y, ang, z):
    """pedra de canto sobre a emenda de dois trechos de parapeito (0,04 acima das capas: nada coplanar)"""
    mb.box((1.62, 1.62, 0.36), (x, y, z + PAR_TOP + 0.17), (0, 0, ang), CAPL, 0.06)


def buttress_ts(R, spacing=17.0):
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    L_ = t1 - t0
    nb = int(L_ / spacing)
    out = []
    if nb < 1:
        return out
    sp = L_ / nb
    for k in range(nb):
        t = t0 + sp * (k + 0.5)
        ok = True
        for dt in (-3.0, 0.0, 3.0):
            for dd in (0.5, 2.6, 4.0):
                x, y = _xy(R, t + dt, dd)
                if stair_hit(x, y, pad=2.5) or water_gap(x, y) or castle_hit(x, y, rects=False):
                    ok = False
        if ok:
            out.append(t)
    return out


def buttresses(mb, R, z0, z1, rng=None, ts=None):
    """contrafortes com TALUDE (13.05): soco em perfil (TrimLow), corpo em perfil com o degrau inclinado e capa de
    pedra no talude; colisao propria (o pe do arrimo continua andavel em volta)"""
    ts = buttress_ts(R) if ts is None else ts
    W = _W(R)
    for t in ts:
        h1 = (z1 - z0) - 1.9
        zA = z0 + h1 - 1.2
        body = [(-0.05, z0 + 0.5), (2.45, z0 + 0.5), (2.45, zA), (1.45, zA + 1.25), (1.45, z1), (-0.05, z1)]
        CK.ledge(mb, W, t - 1.55, t + 1.55, body, BLOCK)
        cap = [(1.45, zA + 1.18), (2.62, zA - 0.2), (2.62, zA + 0.06), (1.45, zA + 1.5)]
        CK.ledge(mb, W, t - 1.66, t + 1.66, cap, CAPL)
        soc = [(-0.05, z0 - 0.02), (2.8, z0 - 0.02), (2.8, z0 + 0.3), (2.55, z0 + 0.55), (-0.05, z0 + 0.55)]
        CK.ledge(mb, W, t - 1.75, t + 1.75, soc, CAPL)
        cx, cy = _xy(R, t, 1.25)
        col_box("SG_TerButtress", (3.2, 2.5, z1 - z0 + 0.05), (cx, cy, (z0 + z1) / 2),
                (0, 0, math.atan2(R["u"][1], R["u"][0])))


def corbels(mb, R, z, ts=(), half=1.75):
    """mesa de MISULAS com ARQUINHOS sob o arremate (13.05), por vao entre contrafortes: cada vao reparte as
    misulas por igual (~3,1), entao o ritmo quebra a cada contraforte (16.04)"""
    W = _W(R)
    zc = z - 0.7
    zb = zc - 1.3
    prof = [(0.0, zb), (0.4, zb), (0.4, zb + 0.28), (1.12, zb + 0.82), (1.12, zc), (0.0, zc)]
    edges = [R["t0"] + 0.4] + [e for t in sorted(ts) for e in (t - half - 0.3, t + half + 0.3)] + [R["t1"] - 0.4]
    for b0, b1 in zip(edges[0::2], edges[1::2]):
        L_ = b1 - b0
        if L_ < 1.2:
            continue
        n = max(1, int(round(L_ / 3.8)))
        tsc = [b0 + L_ * k / n for k in range(n + 1)]
        tsc = [t for t in tsc if not stair_hit(*_xy(R, t, 0.5), pad=0.4)]
        for t in tsc:
            CK.ledge(mb, W, t - 0.34, t + 0.34, prof, CAPL)
        for ta, tb in zip(tsc, tsc[1:]):
            u0, u1 = ta + 0.34, tb - 0.34
            if u1 - u0 < 0.8 or tb - ta > 5.0:
                continue
            zs = zc - 0.95
            rise = min(0.62, (u1 - u0) * 0.4)
            lo = [(u0 + (u1 - u0) * i / 4.0, zs + rise * math.sin(math.pi * i / 4.0)) for i in range(5)]
            hi = [(uu, zc) for uu, _ in lo]
            CK.strip(mb, W, lo, hi, 0.84, 1.1, CAPL)


def rock_base(mb, R, zb, ztop, rng=None):
    """base de basalto (13.07) em MACICOS de 3-5 colunas com vao entre eles: o do meio mais alto e mais grosso, os
    de fora descem em degrau; o topo (grama ou rocha) alterna POR MACICO, nao por coluna"""
    a, u, nrm, t0, t1 = R["a"], R["u"], R["n"], R["t0"], R["t1"]
    NS = (3, 4, 3, 4)
    GAPS = (10.0, 12.0, 8.5)
    g = int(abs(a[0] * 5.0 + a[1] * 11.0)) % 4
    t = t0 + 2.4
    while t < t1 - 2.0:
        n = NS[g % 4]
        span = 3.3 * (n - 1)
        if t + span > t1 - 1.2:
            n = max(1, int((t1 - 1.2 - t) / 3.3) + 1)
            span = 3.3 * (n - 1)
        grass = g % 2 == 0
        for j in range(n):
            c = (j - (n - 1) / 2.0) / max(1.0, (n - 1) / 2.0)      # -1..1 no macico
            r = 3.0 - 0.6 * abs(c)
            d = r * (0.9 - 0.25 * abs(c)) + (0.5 if j % 2 else 0.0)
            tt = t + 3.3 * j
            cx, cy = _xy(R, tt, d)
            zt = ztop + 1.4 - 2.6 * abs(c) - (0.5 if j % 2 else 0.0)
            cx, cy, zt = water_fix(cx, cy, r, zt)
            zt = cap_top(cx, cy, r, zt)
            if zt < zb + 1.0 or not dun_ok(cx, cy, r, zb - 1.4, zt) or castle_hit(cx, cy, r):
                continue
            column(mb, cx, cy, r, zt, zb - 1.4, 0.35 * j + 0.2 * g, m=ROCK, cap=GRASS if grass else TOP,
                   band=None)
        t += span + GAPS[g % 3] + 3.0
        g += 1


def quoins(mb, nm, poly, runs, z, rng=None):
    """cunhais nas quinas CONVEXAS: nos arrimos entre patamares (Tier B) pedras alternadas longa/curta nas fiadas da
    alvenaria; no terreno bravo (fundo) um pilar de canto so. TrimLow."""
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
        if Rs["cls"] == "terrace" and Re["cls"] == "terrace":
            zc = z0
            for c, hc in enumerate(course_heights(z - 0.75 - z0)):
                sx, sy = (2.3, 1.5) if c % 2 == 0 else (1.5, 2.3)
                mb.box((sx, sy, hc - 0.1), (cx, cy, zc + hc / 2), (0, 0, ang), CAPL, 0.07)
                zc += hc
        else:
            mb.box((1.9, 1.9, z - 0.75 - z0), (cx, cy, (z0 + z - 0.75) / 2), (0, 0, ang), CAPL, 0)


def terrace_edges():
    rng = random.Random(3101)
    npost = nstone = 0
    for nm, poly, z, pr in L.floors():
        if nm not in ("P1", "P2", "P3"):
            continue
        mb = smb("SG_Ter_Wall_" + nm, detail="near")
        mr = smb("SG_Ter_Terrace_" + nm)
        runs = edge_runs(nm, poly, z)
        runs = [R for R in runs if not R["cas"]]        # o castelo cobre esses trechos (cortina, torres)
        pars = []
        for R in runs:
            zo = R["zo"]
            if R["cls"] == "terrace":
                top = z - (0.6 if R["mur"] else 0.7)
                masonry(mb, R, zo + 0.55, top)
                ts = buttress_ts(R)
                if R["mur"]:
                    # cordao entre o arrimo e a muralha do castelo (face externa em y -9): perfil com chanfro
                    prof = [(-0.02, z - 0.6), (0.5, z - 0.6), (0.55, z - 0.3), (0.4, z - 0.05), (-0.02, z - 0.05)]
                    CK.ledge(mb, _W(R), R["t0"], R["t1"], prof, CAPL)
                else:
                    coping(mb, R, z)
                    corbels(mb, R, z, ts)
                    if not R["open"]:
                        pars.append(R)
                buttresses(mb, R, zo, top, ts=ts)
                soc = [(-0.02, zo - 0.02), (0.75, zo - 0.02), (0.75, zo + 0.3), (0.55, zo + 0.55), (-0.02, zo + 0.55)]
                CK.ledge(mb, _W(R), R["t0"], R["t1"], soc, CAPL)
            else:
                drop = z - zo
                if drop <= 3.0:                      # P1: meio-fio sobre o ombro
                    band_face(mb, R, zo - 0.4, z - 0.7)
                else:                                # P2/P3: base de rocha + faixa de alvenaria
                    band = 7.6 if drop > 12.0 else 4.4
                    band_face(mb, R, z - band, z - 0.7)
                    rock_base(mr, R, zo, z - band + 1.2)
                coping(mb, R, z)
                if not R["open"]:
                    pars.append(R)
        # parapeitos: emendas nos vertices do contorno (corpo prolongado + pedra de canto) e pilarete SO nas pontas
        # livres (onde o parapeito para: agua, escada, castelo, abertura) = enfase nos nos (16.04)
        P = []
        for R in pars:
            P.append((R, _xy(R, R["t0"], 0.0), _xy(R, R["t1"], 0.0)))

        def joined(p, me):
            for R2, s, e in P:
                if R2 is me:
                    continue
                for q in (s, e):
                    if math.hypot(p[0] - q[0], p[1] - q[1]) < 0.35:
                        return R2
            return None
        for R, s, e in P:
            js, je = joined(s, R), joined(e, R)
            parapet(mb, R, z, ext=(0.7 if js else 0.0, 0.7 if je else 0.0))
            for p, other, t_end, sgn in ((s, js, R["t0"], 1.0), (e, je, R["t1"], -1.0)):
                if other is not None:
                    if sgn < 0:                       # a pedra de canto sai uma vez por emenda
                        bis = math.atan2(R["u"][1] + other["u"][1], R["u"][0] + other["u"][0])
                        cx, cy = _xy(R, t_end, 0.47)
                        ox, oy = _xy(other, other["t0"], 0.47)
                        corner_stone(mb, (cx + ox) / 2, (cy + oy) / 2, bis, z)
                        nstone += 1
                elif R["t1"] - R["t0"] > 2.4:
                    ex, ey = _xy(R, t_end - sgn * 1.5, 0.5)
                    if castle_hit(ex, ey, r=1.5, rects=True):
                        continue
                    px, py = _xy(R, t_end + sgn * 0.98, 0.47)
                    EN._post(mb, px, py, z - 0.05, 1.5, h=2.3, lamp=False)
                    npost += 1
        quoins(mb, nm, poly, runs, z)
    print("TER BORDAS pilaretes=%d pedras_de_canto=%d" % (npost, nstone))


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
    # (overhaul 13: as bandas escalonadas de baixo viraram o cone canelado de under())


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


def prom_w(x, y):
    """peso de promontorio (0..1) de um ponto da borda: 1 no miolo do promontorio, 0 fora dele"""
    w = 0.0
    for px, py, hw in PROMS:
        w = max(w, 1.0 - math.hypot(x - px, y - py) / hw)
    return min(1.0, max(0.0, w) * 1.6)


RIM_FACE = {}       # indice da amostra da borda (passo 1,0) -> avanco da face do bloco (os cristais encravam nela)


def block_strata(mb, outer, onrm, inner, inrm, T, z0, apex, cap):
    """bloco da coroa (13.01): face externa canelada (as colunas sao o DETALHE); 2 ESTRATOS em cota fixa da ilha
    (ZS_A, ZS_B): a face recua 0,9 em cada um e o degrau sai em Cliff_Rock_SG_Top (linha de luar continua na ilha
    inteira); abaixo de ZS_B a rocha escurece; o fundo fecha numa ponta (apex). Anel = contorno recuado 'ins'."""
    pts0 = outer + inner[::-1]
    nrm = onrm + inrm[::-1]
    n = len(pts0)
    if n < 3:
        return
    order = list(range(n)) if SL.area(pts0) > 0 else list(range(n))[::-1]
    bm = mb.bm

    def ring(ins, z):
        return [bm.verts.new((pts0[k][0] - nrm[k][0] * ins, pts0[k][1] - nrm[k][1] * ins, z)) for k in order]
    # faixa de luar na crista so sob o topo de GRAMA (no topo de rocha o proprio topo ja e Cliff_Rock_SG_Top)
    seq = [(ring(0.0, T), None)] + ([(ring(0.0, T - 1.0), TOP)] if cap != TOP else [])
    ins = 0.0
    if z0 + 1.0 < ZS_A < T - 2.5:
        seq += [(ring(0.0, ZS_A), ROCK), (ring(0.9, ZS_A), TOP)]
        ins = 0.9
    if z0 + 1.0 < ZS_B < min(T - 2.5, ZS_A - 1.0):
        seq += [(ring(ins, ZS_B), ROCK), (ring(ins + 0.9, ZS_B), TOP)]
        ins += 0.9
        seq.append((ring(ins, z0), DARK))
    else:
        seq.append((ring(ins, z0), ROCK))
    top = bm.faces.new(seq[0][0])
    groups = {}
    no = len(outer)
    # as costas do bloco (entre os pontos de dentro) ficam dentro do nucleo da ilha: sem face (so a coroa e as pontas)
    hidden = {k for k in range(n) if order[k] >= no and order[(k + 1) % n] >= no}
    for (a, _), (b, mm) in zip(seq, seq[1:]):
        for k in range(n):
            if k in hidden:
                continue
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((a[k2], a[k], b[k], b[k2])))
    last = seq[-1][0]
    av = bm.verts.new(apex)
    for k in range(n):
        if k in hidden:
            continue
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


# ritmo DIRIGIDO da coroa entre os promontorios (topo relativo ao ombro, avanco da face, largura do bloco):
# alto-baixo-alto com um entalhe fundo a cada 5 blocos (a coroa em degraus da concept, sem sorteio)
PAT_T = (0.8, -1.4, 1.6, -0.6, -5.0)
PAT_D = (0.4, -0.5, 0.9, -0.2, -0.9)
PAT_W = (24, 18, 26, 20, 16)


def rim_cliff():
    """coroa do penhasco (13.01, Tier C): 5 PROMONTORIOS (blocos largos que avancam ate 3,6, sobem ate 5 acima do
    ombro e pendem em quilha funda) e, entre eles, blocos calmos no ritmo PAT_*; 2 estratos continuos (block_strata);
    um pilar destacado so no miolo de cada promontorio"""
    RIM_FACE.clear()
    smp = resample_closed(RIM, 1.0)
    N = len(smp)
    tags = rim_tags(smp)
    i = 0
    nblk = npil = 0
    prev_t = None
    while i < N - 3:
        pw0 = prom_w(smp[i][0], smp[i][1])
        W = 26 if pw0 > 0.3 else PAT_W[nblk % 5]
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
        pw = prom_w(mid[0], mid[1])
        pat = nblk % 5
        if pw > 0.25:
            T = base + 1.5 + 3.5 * pw
            dout = 1.0 + 2.6 * pw
        else:
            T = base + PAT_T[pat]
            dout = PAT_D[pat]
        if prev_t is not None and abs(T - prev_t) < 1.0:
            T += 1.2 if T >= prev_t else -1.2
        if tag and tag[0] == "B":
            T = min(T, tag[1])
        if tag and tag[0] == "W":
            wx, wy, wz, ux, uy = FALLS[tag[1]]
            T = min(T, wz - 0.5)
            dout = -2.0
        depth = 6.5 + 1.0 * pw
        outer, onrm = [], []
        t = 0.0
        k = 0
        while t <= W + 0.01:
            q = min(N - 1, i + int(round(t)))
            x, y, nx, ny = smp[q]
            d = dout + (0.5 if k % 2 == 0 else -0.7)
            outer.append((x + nx * d, y + ny * d))
            onrm.append((nx, ny))
            t += 3.0
            k += 1
        inner, inrm = [], []
        for q in (0, W // 2, W):
            x, y, nx, ny = smp[i + q]
            inner.append((x - nx * (depth - dout), y - ny * (depth - dout)))
            inrm.append((nx, ny))
        for px, py in outer + inner:
            z = L.zone_of(px, py)
            if z is not None:
                T = min(T, z - 0.3)
        prev_t = T
        z0 = ZS_B - 5.0 - 9.0 * pw
        x, y, nx, ny = mid
        zap = -26.0 - 4.0 * (nblk % 3) - 44.0 * pw
        apex = (x - nx * (depth * 0.3 - dout), y - ny * (depth * 0.3 - dout), zap)
        grass = T >= base - 0.9
        gx = sum(p[0] for p in outer) / len(outer)
        gy = sum(p[1] for p in outer) / len(outer)
        bxs = [p[0] for p in outer + inner]
        bys = [p[1] for p in outer + inner]
        inbox = max(bxs) > KX0 and min(bxs) < KX1 and max(bys) > KY0 and min(bys) < KY1
        if inbox and not (T <= KZ0 - 0.3 or zap >= KZ1 + 0.3):
            print("TER AVISO bloco da borda na caixa da dungeon", round(gx, 1), round(gy, 1))
        else:
            block_strata(cliff_mb(gx, gy), outer, onrm, inner, inrm, T, z0, apex, GRASS if grass else TOP)
            for q in range(i, i + W + 1):
                RIM_FACE[q] = (dout, T)
            nblk += 1
        # pilar destacado: so no miolo do promontorio (profundidade, nao cerca)
        if not tag and pw > 0.7:
            x, y, nx, ny = smp[i + W // 2]
            r2 = 3.2
            d2 = dout + 1.0 + r2 * 1.1
            px, py = x + nx * d2, y + ny * d2
            zt2 = T - 9.0
            zb2 = zt2 - 40.0
            px, py, zt2 = water_fix(px, py, r2, zt2)
            zt2 = cap_top(px, py, r2, zt2)
            if zt2 - zb2 > 8.0 and dun_ok(px, py, r2, zb2 - r2 * 1.5, zt2):
                column(cliff_mb(px, py), px, py, r2, zt2, zb2, 0.3, m=ROCK, cap=TOP, band=(0.9, TOP),
                       strata=(ZS_A if ZS_A < zt2 - 2.0 else zt2 - 8.0, 0.86, (nx * 0.3, ny * 0.3)), low=DARK,
                       tip=r2 * 1.5)
                npil += 1
        gap = (1 if pw > 0.25 else 2) if (j + 1 < N and tags[min(N - 1, j + 1)] == tag) else 1
        i += W + gap
    print("TER COROA blocos=%d pilares=%d" % (nblk, npil))
    return nblk


# massa de baixo (13.01): UM cone ESCALONADO e canelado (cada estrato: faixa vertical de colunas + degrau por baixo)
# + 5 QUILHAS sob os promontorios com as colunas pendentes so nelas. (fator, cota, amplitude da flauta)
LOFT = [(0.97, KZ0 - 0.5, 0.0), (0.86, -14.0, 1.3), (0.72, -32.0, 1.5), (0.56, -50.0, 1.4), (0.39, -68.0, 1.1),
        (0.23, -84.0, 0.8), (0.11, -96.0, 0.4)]


def under():
    mb = smb("SG_Ter_Cliff_Under")
    NU = 84
    per = sum(math.hypot(RIM[(k + 1) % len(RIM)][0] - RIM[k][0], RIM[(k + 1) % len(RIM)][1] - RIM[k][1])
              for k in range(len(RIM)))
    pts = resample_closed(RIM, per / NU)
    n = len(pts)
    bm = mb.bm
    # flauta: grupos de 3 colunas (fora, fora, dentro) = feixes de basalto, nao serrilha regular
    FL = (1.0, 0.55, -1.0)
    rings, mats = [], []

    def ring(f, z, amp):
        rg = []
        for k, (x, y, nx, ny) in enumerate(pts):
            fl = amp * FL[k % 3]
            rg.append(bm.verts.new((C[0] + (x - C[0]) * f + nx * fl, C[1] + (y - C[1]) * f + ny * fl, z)))
        return rg
    for i, (f, z, amp) in enumerate(LOFT):
        rings.append(ring(f, z, amp))
        if i + 1 < len(LOFT):
            f1, z1, a1 = LOFT[i + 1]
            rings.append(ring(f * 0.965, z1 + 0.01 * 0, amp))      # faixa vertical (quase a prumo) ate o degrau
            mats.append(ROCK if i < 3 else DARK)
            mats.append(DARK)                                        # degrau (face de baixo)
    apex = bm.verts.new((C[0], C[1], -108.0))
    groups = {}
    for (r0, r1), mm in zip(zip(rings, rings[1:]), mats):
        for k in range(n):
            k2 = (k + 1) % n
            groups.setdefault(mm, []).append(bm.faces.new((r0[k2], r0[k], r1[k], r1[k2])))
    for k in range(n):
        groups.setdefault(DARK, []).append(bm.faces.new((rings[-1][(k + 1) % n], rings[-1][k], apex)))
    mb._post([v for rg in rings for v in rg] + [apex], DARK, None, 0, 1)
    mi = mb._mi_for(ROCK)
    for f in groups.get(ROCK, []):
        f.material_index = mi
    smp = resample_closed(RIM, 1.0)
    for idx, (px, py, hw) in enumerate(PROMS):
        x, y, nx, ny = min(smp, key=lambda s: math.hypot(s[0] - px, s[1] - py))
        tx, ty = -ny, nx
        cx, cy = x - nx * 7.0, y - ny * 7.0
        A, B = hw * 0.78, 9.5
        kmb = cliff_mb(x, y)
        m = 14
        bm = kmb.bm
        krings = []
        for sc, z in ((1.0, ZS_B - 2.0), (0.8, -26.0), (0.5, -52.0)):
            rg = []
            for k in range(m):
                a = 2 * math.pi * k / m
                rr = sc * (1.0 + (0.12 if k % 2 == 0 else -0.1))
                rg.append(bm.verts.new((cx + tx * A * rr * math.cos(a) + nx * B * rr * math.sin(a),
                                        cy + ty * A * rr * math.cos(a) + ny * B * rr * math.sin(a), z)))
            krings.append(rg)
        # contorno anti-horario? (tangente x normal): garante as normais para fora
        if tx * ny - ty * nx < 0:
            krings = [rg[::-1] for rg in krings]
        zk = -88.0 - 8.0 * (idx % 2)
        kap = bm.verts.new((cx + nx * 1.5, cy + ny * 1.5, zk))
        kf = [bm.faces.new(krings[0])]
        for r0, r1 in zip(krings, krings[1:]):
            for k in range(m):
                k2 = (k + 1) % m
                kf.append(bm.faces.new((r0[k2], r0[k], r1[k], r1[k2])))
        for k in range(m):
            kf.append(bm.faces.new((krings[-1][(k + 1) % m], krings[-1][k], kap)))
        import bmesh
        bmesh.ops.recalc_face_normals(bm, faces=kf)
        kmb._post([v for rg in krings for v in rg] + [kap], DARK, None, 0, 1)
        mi = kmb._mi_for(ROCK)
        for f in kf[1:1 + m]:
            f.material_index = mi
        # colunas pendentes (detalhe) SO na quilha, em leque do lado de fora: a do meio maior e mais funda
        for j in range(4):
            c = (j - 1.5) / 1.5
            a = math.pi * (0.5 + 0.34 * c)
            qx = cx + tx * A * 0.8 * math.cos(a) + nx * B * 0.85 * math.sin(a)
            qy = cy + ty * A * 0.8 * math.cos(a) + ny * B * 0.85 * math.sin(a)
            r = 4.2 - 0.9 * abs(c)
            zb = -48.0 - 20.0 * (1.0 - abs(c)) - 4.0 * (idx % 2)
            if not dun_ok(qx, qy, r, zb - r * 1.3, 0.0):
                continue
            column(kmb, qx, qy, r, 0.0, zb, 0.4 * j, m=ROCK, cap=DARK, strata=((0.0 + zb) / 2, 0.82,
                   (nx * 0.5, ny * 0.5)), low=DARK, tip=r * 1.3)


def spires():
    """CLIFF_SPIRES: aglomerados de 4 colunas altas (silhueta vertical, topo de grama): a do meio mais alta, 2 medias
    dos lados (ao longo da borda) e 1 baixa para fora; alturas e angulos dirigidos pelo lado de fora da ilha"""
    for x, y, r, top_z, kind in L.CLIFF_SPIRES:
        mb = cliff_mb(x, y)
        a0 = math.atan2(y - C[1], x - C[0])
        cols = [(0.0, 0.0, 0.5, 0.0), (a0 + math.pi / 2, r * 0.5, 0.42, 5.0), (a0 - math.pi / 2, r * 0.5, 0.40, 8.0),
                (a0 + 0.5, r * 0.66, 0.32, 16.0)]
        for q, (a, d, fr, dz) in enumerate(cols):
            rc = r * fr
            px, py = x + d * math.cos(a), y + d * math.sin(a)
            zt = top_z - dz
            zb = -30.0 - 3.0 * q
            px, py, zt = water_fix(px, py, rc, zt)
            zt = cap_top(px, py, rc, zt)
            if not dun_ok(px, py, rc, zb - rc * 1.5, zt):
                continue
            zs = zt - 14.0 - 1.5 * q
            column(mb, px, py, rc, zt, zb, 0.25 * q, m=ROCK, cap=GRASS if dz < 10.0 else TOP,
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
        s = 7.2
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
            rc = rng.uniform(3.7, 4.3)
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


def fall_steps():
    """degrau de basalto sob cada cachoeira na cota do estrato de cima (13.02): 2 fileiras de colunas saindo da face
    (a de tras encosta no penhasco, a da frente avanca sob a cortina). A agua (sg_water, raios nas malhas SG_Ter_*)
    BATE nele, quebra em espuma e abre - em vez da fita reta do labio ao pe."""
    for wx, wy, wz, ux, uy in FALLS:
        if wz - ZS_A < 8.0:
            continue
        mb = cliff_mb(wx, wy)
        vx, vy = -uy, ux
        for along, lats, dz, r in ((-0.6, (-3.4, 0.0, 3.4), (-1.6, -1.1, -1.9), 2.7),
                                   (3.0, (-3.0, 0.2, 3.3), (-0.6, 0.0, -0.9), 2.5)):
            for q, (lat, d) in enumerate(zip(lats, dz)):
                cx, cy = wx + ux * along + vx * lat, wy + uy * along + vy * lat
                zt = ZS_A + d
                if not dun_ok(cx, cy, r, zt - 14.0, zt):
                    continue
                column(mb, cx, cy, r, zt, zt - 3.5 - 0.8 * q, 0.3 + 0.4 * q, m=ROCK, cap=TOP, band=(0.6, TOP),
                       low=DARK, tip=r * 1.3)


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
    """cristais da borda (13.09): SO 3 aglomerados com funcao de leitura - a ponta leste da dungeon, sob a ala oeste do
    castelo e na massa pendente da ilhota do summon (virada para a praca). Cada um: 1 cristal-heroi + 3 menores em
    leque (inclinacao dirigida, sem sorteio), encravados na face REAL do bloco (RIM_FACE) abaixo do topo, + 2 pontas
    pendentes logo abaixo. O resto da borda fica sem cristal (antes: 28 grupos, 10 veios e ~20 pontas espalhados)."""
    mb = smb("SG_Ter_Crystals")
    smp = resample_closed(RIM, 1.0)
    N = len(smp)
    fan = [(0.0, 1.0, 0.0), (-1.4, 0.62, -0.32), (1.3, 0.55, 0.3), (0.55, 0.4, 0.12)]
    ncl = 0
    for name, (hx, hy), hero in (("Dungeon", (138.0, 92.0), 6.8), ("Castelo", (-124.0, 98.0), 6.0)):
        order = sorted(range(N), key=lambda q: math.hypot(smp[q][0] - hx, smp[q][1] - hy))
        got = None
        for q in order[:60]:
            if q not in RIM_FACE:
                continue
            x, y, nx, ny = smp[q]
            dout, T = RIM_FACE[q]
            zt = T - 6.5
            fx, fy = x + nx * (dout - 0.8), y + ny * (dout - 0.8)
            if crystal_ok(fx, fy, 3.5, zt - 10.0, zt + 7.0) and zt > ZS_A + 1.0:
                got = (fx, fy, nx, ny, zt)
                break
        if got is None:
            print("TER AVISO aglomerado de cristal sem lugar:", name)
            continue
        fx, fy, nx, ny, zt = got
        sx, sy = -ny, nx
        for lat, f, lean in fan:
            ln = hero * f
            rr = (0.32 + hero * 0.10) * f
            ax = (nx * 0.45 + sx * lean, ny * 0.45 + sy * lean, 1.0)
            crystal(mb, (fx + sx * lat, fy + sy * lat, zt - ln * 0.4 - (0.0 if f == 1.0 else 0.6)), ax, ln, rr,
                    m="SG_Crystal_Glow")   # 15: ambiente = o violeta mais baixo da ilha (o VioletDeep das pontas subia a hierarquia)
        # 2 pontas pendentes no estrato de baixo (a mesma veia, mais funda)
        for lat, dz, ln, rr in ((-1.8, 18.0, 4.4, 0.62), (2.2, 24.0, 3.2, 0.5)):
            if crystal_ok(fx, fy, 2.0, zt - dz - ln, zt - dz):
                crystal(mb, (fx - nx * 1.5 + sx * lat, fy - ny * 1.5 + sy * lat, ZS_B - 1.5 - (dz - 18.0)),
                        (nx * 0.5, ny * 0.5, -1.0), ln, rr)
        ncl += 1
    # ilhota do summon: 4 pontas pendentes em leque no lado sudeste (visto da praca e da ponte de chegada)
    ssx, ssy = L.SUMMON_C
    # (base a 12,2 do centro: dentro do disco do nucleo de raio 13 entre -18 e 4 - a ponta sai pela lateral)
    for k, (deg, z, ln, rr) in enumerate(((-58.0, -9.0, 3.2, 0.42), (-44.0, -14.0, 4.4, 0.55),
                                          (-30.0, -11.0, 3.0, 0.4), (-40.0, -16.5, 2.6, 0.36))):
        a = math.radians(deg)
        crystal(mb, (ssx + 12.2 * math.cos(a), ssy + 12.2 * math.sin(a), z),
                (math.cos(a) * 0.6, math.sin(a) * 0.6, -1.0), ln, rr)
    ncl += 1
    print("TER CRISTAIS aglomerados=%d" % ncl)


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
    # overhaul 13: 6 + 2 colunas pendentes (antes 9 + 3): o fundo da ilhota le massa, nao franja
    for n, rad, rr0, rr1, zt0, zt1, zb0, zb1 in ((6, 11.0, 4.4, 5.2, 2.0, 3.5, -44.0, -26.0),
                                                  (2, 3.5, 4.2, 4.8, -17.0, -16.0, -58.0, -48.0)):
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
    fall_steps()
    summon_isle()
    rim_crystals()
    for nm in sorted(_MB):
        _MB[nm].finish()
    _MB.clear()
