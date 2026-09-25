# db_mining - zona "mining" da Ilha 2 (Dragon Ball) em arte final: prefixo DB_Mine_, colecao 03_MINING_ZONE.
# Substitui db_blockout.mining(). A arena e uma BACIA DE CANION rasa (ARENA 20,2; 4 abaixo do promenade GROUND 24,2)
# com a borda em SETORES DIFERENTES (nada de anel uniforme + cerca uniforme, que era o fosso da Ilha 1):
#   S (222..318): muro de arrimo de arenito cortado (quente) + guarda Capsule (postes brancos, corrimao azul, ciano)
#   E (318..45) : borda natural BAIXA de rocha em blocos, 2 prateleiras baixas andaveis, poucas lajes compridas com
#                 vaos, 3 rochas em pe e a rampa de pedra (ARENA_ACCESS 14 graus, 4 em 18)
#   N (45..135) : patamares naturais em UNIDADES alternadas (baixo+alto / so baixo com a face da borda atras / massa
#                 alta que atravessa os dois), blocos com altura, fundo e cor proprios, pontas arredondadas, entalhes,
#                 1 pedra grande sobre o patamar alto por lado + parapeito de blocos cortados de tamanhos variados
#   W (135..222): pilares de canion VERTICAIS em grupos (alto + medio + quebra baixa, 5..8 acima do promenade),
#                 camada clara horizontal continua (a mesma geologia em todos), vaos das escadas W e SW
# Piso: areia com relevo sutil (+-0,15 de 20,2: manchas escuras, ondulacoes, 2 placas de terra rachada RENTES longe
# dos ORE_*, trilhas batidas do pe de cada acesso ate o pod). NADA de minerio, cristal ou pedra solta.
# So as 7 ARENA_ROCKS (buttes de arenito em 2 camadas: base larga irregular com pe escuro de estrato inclinado,
# ressalto parcial, fraturas e patamar plano; torre estreita deslocada ate a altura da planta) e o CORE_POD (pod de
# sondagem Capsule, sem porta) ficam dentro.
# Colisao: o chao, as escadas, a rampa, a guarda da borda, as colunas das mesas e do pod sao do db_col (congelado).
# As mesas e o pod sao desenhados SOBRE a coluna pedida ao db_col (mesa_tiers / POD_COL, ngon_col 8): base = o
# octogono atual de 0,98 r cortado no patamar + torre; pod em 4 camadas. Aqui so a colisao dos volumes proprios:
# blocos dos patamares N, pilares W, prateleiras E, bochechas (guarda) das 5 escadas, meio-fio da rampa e pilones.
import math, random
from mathutils import Vector
import db_lib as DL
from db_lib import MB, col_box, col_ramp, light, ccw, ribbon_poly, dome, Frame
import db_layout as L
import db_col
import fm_lib

COLL = "03_MINING_ZONE"
A = L.ARENA
G = L.GROUND

# ------------------------------------------------------------------ materiais novos (3 de 4)
_M = fm_lib.MATS.setdefault
_M("Sand_DBMineDark", (fm_lib.S(216, 162, 104), 0.95, 0.0, 0, None, 0.10))     # manchas de areia umida/escura
_M("Sand_DBMineLight", (fm_lib.S(236, 196, 138), 0.95, 0.0, 0, None, 0.08))   # trilha batida / crista das ondulacoes
_M("Stone_DBMineSand", (fm_lib.S(222, 160, 104), 0.85, 0.0, 0, None, 0.12))   # arenito CORTADO quente (muro S, alas)

ROCK = "Cliff_Rock_DB"
DARK = "Cliff_Rock_DB_Dark"
TOP = "Cliff_Rock_DB_Top"
SANDSTONE = "Stone_DBMineSand"

MESA_COL_K = 0.98      # base das ARENA_ROCKS = a coluna atual do db_col (octo 0,98 r) cortada no patamar + torre
# coluna do CORE_POD pedida ao db_col (ngon_col 8): (raio do vertice, z0, z1) - tambor, base da cupula, cupula, topo
POD_COL = ((4.7, A - 1.0, A + 3.4), (4.45, A + 3.4, A + 4.8), (3.5, A + 4.8, A + 5.9), (2.0, A + 5.9, A + 6.9))

# ------------------------------------------------------------------ cameras de revisao (360 + altura do jogador)
CAMS = {
    "CAM_DBMine_South": ((0.0, -100.0, G + 30.0), (0.0, 6.0, A + 2.0), 22),
    "CAM_DBMine_North": ((8.0, 100.0, G + 30.0), (0.0, -4.0, A + 2.0), 22),
    "CAM_DBMine_East": ((104.0, -10.0, G + 28.0), (-2.0, 4.0, A + 2.0), 22),
    "CAM_DBMine_West": ((-100.0, 22.0, G + 30.0), (4.0, -4.0, A + 2.0), 22),
    "CAM_DBMine_Top": ((0.0, -1.0, A + 150.0), (0.0, 0.0, A), 18),
    # altura do jogador (olho 5,2 acima do piso)
    "CAM_DBMine_PlayerNW": ((14.0, -24.0, A + 5.2), (-40.0, 32.0, A + 5.0), 22),     # patamares N + pilares W
    "CAM_DBMine_PlayerS": ((-20.0, -10.0, A + 5.2), (12.0, -60.0, A + 3.5), 22),     # muro S + guarda Capsule
    "CAM_DBMine_PlayerRamp": ((66.0, 18.0, G + 5.2), (0.0, 0.0, A + 3.0), 22),       # topo da rampa E
    "CAM_DBMine_PlayerN": ((14.0, -2.0, A + 5.2), (-2.0, 56.0, A + 3.0), 22),         # patamares N de frente
    "CAM_DBMine_PlayerW": ((-84.0, -16.0, G + 5.2), (-52.0, 8.0, G + 2.0), 22),        # promenade W: costas dos pilares
    "CAM_DBMine_PlayerMesa": ((32.0, -14.0, A + 5.2), (52.0, -26.0, A + 4.5), 24),    # mesa de perto
    "CAM_DBMine_PlayerE": ((36.0, 4.0, A + 5.2), (60.0, 32.0, A + 3.0), 22),          # borda E + rampa
    "CAM_DBMine_PlayerOutcrop": ((-34.0, 4.0, A + 5.2), (-62.0, 8.0, A + 6.0), 22),   # pilares W de dentro
}

# ------------------------------------------------------------------ util
V = Vector


def P(a_deg, r, z=0.0):
    a = math.radians(a_deg)
    return V((r * math.cos(a), r * math.sin(a), z))


def P2(a_deg, r):
    a = math.radians(a_deg)
    return (r * math.cos(a), r * math.sin(a))


def ang_of(x, y):
    return math.degrees(math.atan2(y, x)) % 360.0


def adiff(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def R(a):
    return L.arena_r(a)


def deg_at(d, a):
    """angulo (graus) que um arco de d studs ocupa na borda da arena no angulo a"""
    return math.degrees(d / R(a))


def sector_poly(a0, a1, rin, rout, step=2.0):
    """setor de anel (graus; rin/rout = numero ou funcao do angulo), anti-horario"""
    n = max(1, int(math.ceil(abs(a1 - a0) / step)))
    fi = rin if callable(rin) else (lambda a, v=rin: v)
    fo = rout if callable(rout) else (lambda a, v=rout: v)
    outer = [P2(a0 + (a1 - a0) * i / n, fo(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]
    inner = [P2(a1 - (a1 - a0) * i / n, fi(a1 - (a1 - a0) * i / n)) for i in range(n + 1)]
    return outer + inner


def hexa(mb, bot, top, m, tint=None):
    """solido de 8 cantos: bot/top = 4 pontos (x, y, z), mesma ordem"""
    vb = [mb.bm.verts.new(V(p)) for p in bot]
    vt = [mb.bm.verts.new(V(p)) for p in top]
    mb.bm.faces.new(list(reversed(vb)))
    mb.bm.faces.new(vt)
    for i in range(4):
        j = (i + 1) % 4
        mb.bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    mb._post(vb + vt, m, tint, 0, 1)


def access(aa):
    """(ang, largura, tipo) do acesso no angulo aa"""
    for a, w, k in L.ARENA_ACCESS:
        if abs(adiff(a, aa)) < 1e-6:
            return a, w, k
    return None


def cut_half(aa, extra=0.6):
    """meio-angulo (graus) do recorte da borda num acesso: largura/2 + extra, na borda"""
    a, w, k = access(aa)
    return math.degrees(math.asin(min(0.99, (w / 2 + extra) / R(aa))))


def access_frame(aa):
    """Frame no pe do acesso, +X subindo para fora (arena -> promenade); run = comprimento"""
    foot, top, d = L.access_frame(aa)
    up = math.atan2(-d[1], -d[0])
    a, w, k = access(aa)
    run = L.RAMP_RUN if k == "ramp" else L.STAIR_RUN
    return Frame(foot[0], foot[1], 0.0, up), run, w, k


# setores (angulos) e recortes dos acessos
CUT = {aa: cut_half(aa) for aa, w, k in L.ARENA_ACCESS}
_FRAMES = {aa: access_frame(aa) for aa, w, k in L.ARENA_ACCESS}


def runs(a0, a1, extra=0.0):
    """sub-intervalos de [a0, a1] (graus, a1 > a0, pode passar de 360) fora dos recortes dos acessos"""
    cuts = []
    for aa, h in CUT.items():
        h = h + extra
        for base in (aa - 360.0, aa, aa + 360.0):
            if base + h > a0 and base - h < a1:
                cuts.append((base - h, base + h))
    cuts.sort()
    out = []
    cur = a0
    for c0, c1 in cuts:
        if c0 > cur:
            out.append((cur, min(c0, a1)))
        cur = max(cur, c1)
    if cur < a1:
        out.append((cur, a1))
    return [(x, y) for x, y in out if y - x > 0.5]


SECTORS = {"S": (222.0, 318.0), "E": (318.0, 405.0), "N": (45.0, 135.0), "W": (135.0, 222.0)}


def sector_of(a):
    a %= 360.0
    if 222.0 <= a < 318.0:
        return "S"
    if a >= 318.0 or a < 45.0:
        return "E"
    if a < 135.0:
        return "N"
    return "W"


def clear_access(x, y, margin=0.35):
    """empurra um ponto para fora da faixa de uma escada/rampa (lateral >= largura/2 + margem)"""
    for aa, w, k in L.ARENA_ACCESS:
        F, run, w_, kind = _FRAMES[aa]
        dx, dy = x - F.o.x, y - F.o.y
        t = dx * math.cos(F.a) + dy * math.sin(F.a)
        s = -dx * math.sin(F.a) + dy * math.cos(F.a)
        half = w / 2 + margin
        if -1.0 <= t <= run + 3.0 and abs(s) < half:
            s2 = half if s >= 0 else -half
            return (F.o.x + t * math.cos(F.a) - s2 * math.sin(F.a), F.o.y + t * math.sin(F.a) + s2 * math.cos(F.a))
    return (x, y)


def lateral(aa, x, y):
    """(t, |s|) de um ponto no referencial do acesso aa"""
    F, run, w, kind = _FRAMES[aa]
    dx, dy = x - F.o.x, y - F.o.y
    return (dx * math.cos(F.a) + dy * math.sin(F.a), abs(-dx * math.sin(F.a) + dy * math.cos(F.a)))


# ------------------------------------------------------------------ geometria: contornos e pilhas de aneis
def centroid(pts):
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


def to_world(pts, cx, cy, yaw):
    c, s = math.cos(yaw), math.sin(yaw)
    return [(cx + x * c - y * s, cy + x * s + y * c) for x, y in pts]


def offset_poly(pts, d):
    """desloca um contorno anti-horario 'd' para fora (d < 0 = para dentro): cada vertice anda pela bissetriz das
    normais das duas arestas vizinhas (esquina em meia-esquadria, limitada)"""
    n = len(pts)
    out = []
    for i in range(n):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        e1x, e1y = x1 - x0, y1 - y0
        e2x, e2y = x2 - x1, y2 - y1
        l1 = math.hypot(e1x, e1y) or 1e-9
        l2 = math.hypot(e2x, e2y) or 1e-9
        n1x, n1y = e1y / l1, -e1x / l1
        n2x, n2y = e2y / l2, -e2x / l2
        bx, by = n1x + n2x, n1y + n2y
        bl = math.hypot(bx, by)
        if bl < 1e-6:
            out.append((x1 + n1x * d, y1 + n1y * d))
            continue
        bx, by = bx / bl, by / bl
        k = d / max(0.4, bx * n1x + by * n1y)
        out.append((x1 + bx * k, y1 + by * k))
    return out


def rbox(a, b, cham, bulge=None):
    """contorno de bloco (retangulo 2a x 2b com cantos chanfrados 'cham' e barrigas 'bulge' no meio dos lados),
    local: x ao longo (a), y atravessado (b); cantos na ordem (a,-b) (a,b) (-a,b) (-a,-b); lado k = canto k -> k+1"""
    C = [(a, -b), (a, b), (-a, b), (-a, -b)]
    out = []
    for k in range(4):
        px, py = C[k - 1]
        cx, cy = C[k]
        nx, ny = C[(k + 1) % 4]
        c = max(0.1, min(cham[k], 0.8 * min(a, b)))
        li = math.hypot(cx - px, cy - py)
        lo = math.hypot(nx - cx, ny - cy)
        out.append((cx - (cx - px) / li * c, cy - (cy - py) / li * c))
        out.append((cx + (nx - cx) / lo * c, cy + (ny - cy) / lo * c))
        if bulge and abs(bulge[k]) > 0.01:
            ex, ey = (nx - cx) / lo, (ny - cy) / lo
            out.append(((cx + nx) / 2 + ey * bulge[k], (cy + ny) / 2 - ex * bulge[k]))
    return out


def jitter_out(pts, j, rng):
    """ruido radial PARA FORA (a partir do centroide) por vertice: facetas sem entrar na colisao"""
    cx, cy = centroid(pts)
    out = []
    for x, y in pts:
        dx, dy = x - cx, y - cy
        ln = math.hypot(dx, dy) or 1.0
        k = rng.uniform(0.0, j)
        out.append((x + dx / ln * k, y + dy / ln * k))
    return out


def stack(mb, rings, ch=0.3, top_m=TOP, flat=True):
    """pilha de aneis (mesmo numero de vertices, anti-horario): rings = [(pts, z | [z por vertice], material das faces
    ENTRE o anel anterior e este)]. Topo: chanfro 'ch' para dentro e tampo (top_m); flat = tampo horizontal na cota
    do ponto mais alto + ch (senao acompanha o anel: topo inclinado). Sem fundo (apoiado/enterrado)."""
    bm = mb.bm
    n = len(rings[0][0])
    vr = []
    for pts, z, m in rings:
        zs = list(z) if isinstance(z, (list, tuple)) else [z] * n
        vr.append([bm.verts.new((p[0], p[1], zz)) for p, zz in zip(pts, zs)])
    groups = {}
    for k in range(1, len(rings)):
        m = rings[k][2]
        r0, r1 = vr[k - 1], vr[k]
        for i in range(n):
            j = (i + 1) % n
            groups.setdefault(m, []).append(bm.faces.new((r0[i], r0[j], r1[j], r1[i])))
    top = vr[-1]
    if ch > 0.02:
        # chanfro por encolhimento RADIAL a partir do centroide (contornos estrelados com fratura: sem laco)
        tx_, ty_ = centroid([(v.co.x, v.co.y) for v in top])
        cp = []
        for v in top:
            dx, dy = v.co.x - tx_, v.co.y - ty_
            ln = math.hypot(dx, dy) or 1.0
            k = max(0.35, (ln - ch) / ln)
            cp.append((tx_ + dx * k, ty_ + dy * k))
        if flat:
            zt = max(v.co.z for v in top) + ch
            rc = [bm.verts.new((p[0], p[1], zt)) for p in cp]
        else:
            rc = [bm.verts.new((p[0], p[1], v.co.z + ch)) for p, v in zip(cp, top)]
        for i in range(n):
            j = (i + 1) % n
            groups.setdefault(top_m, []).append(bm.faces.new((top[i], top[j], rc[j], rc[i])))
        top = rc
    groups.setdefault(top_m, []).append(bm.faces.new(top))
    for m, fs in groups.items():
        mi = mb._mi_for(m)
        t = mb.rng.uniform(-1, 1)
        for f in fs:
            f.material_index = mi
            f[mb.tint] = t
            f.smooth = False
            f.normal_update()
        mb._uv(fs, m)


def banded(mb, foot, z0, z1, rng, bands=(), body=ROCK, base=None, taper=0.2, band=0.6, ch=0.3, jit=0.05,
           tilt=None, tamp=0.0, clip=None, top_m=TOP, top_tilt=None):
    """bloco de rocha em ESTRATOS com topo plano em z1: foot = contorno da base (mundo, anti-horario);
    base = (z, material, ressalto) = pe escuro (sobressai 'ressalto' e fecha num degrau claro);
    bands = [(z_a, z_b, material, recuo)] estratos em cotas ABSOLUTAS (a mesma geologia em todas as pecas do setor);
    band = faixa clara do topo; ch = chanfro; taper = recuo total da base ao topo (paredes a prumo: 0,1..0,35);
    tilt(x, y) = desnivel dos estratos (tamp = amplitude); clip(x, y) -> (x, y) em cada vertice;
    top_tilt(x, y) = topo inclinado (so pecas sem piso andavel em cima: faces da borda)."""
    zc = z1 - ch
    zb0 = zc - band
    lv = []
    last = z0
    if base is not None:
        bz, bmat, bo = base
        if z0 + 0.3 < bz - tamp and bz + tamp < zb0 - 0.35:
            lv.append((z0, -bo, None, False))
            lv.append((bz, -bo, bmat, True))
            if bo > 0.02:
                lv.append((bz + 0.05, 0.0, top_m, True))
            last = bz + 0.05
    if not lv:
        lv.append((z0, 0.0, None, False))
    for za, zb, m, ins in sorted(bands):
        if za - tamp > last + 0.35 and zb + tamp < zb0 - 0.35:
            lv.append((za, 0.0, body, True))
            if abs(ins) > 0.02:
                lv.append((za + 0.04, ins, body, True))
            lv.append((zb, ins, m, True))
            if abs(ins) > 0.02:
                lv.append((zb + 0.04, 0.0, m, True))
            last = zb + 0.04
    lv.append((zb0, 0.0, body, True))
    lv.append((zc, 0.0, top_m, False))
    span = max(0.1, z1 - z0)
    rings = []
    for k, (z, ins, m, tl) in enumerate(lv):
        d = taper * (z - z0) / span + ins
        pts = offset_poly(foot, -d) if abs(d) > 1e-4 else list(foot)
        if 0 < k < len(lv) - 1 and jit > 0:
            pts = jitter_out(pts, jit, rng)
        if clip:
            pts = [clip(px, py) for px, py in pts]
        if k == len(lv) - 1 and top_tilt:
            zs = [z + top_tilt(px, py) for px, py in pts]
        else:
            zs = [z + tilt(px, py) for px, py in pts] if (tl and tilt) else z
        rings.append((pts, zs, m))
    stack(mb, rings, ch=ch, top_m=top_m, flat=top_tilt is None)


def local_tilt(cx, cy, yaw, s):
    """estrato inclinado 's' (dz por stud) ao longo do eixo 'yaw' passando pelo centro (cx, cy)"""
    c, sn = math.cos(yaw), math.sin(yaw)
    return lambda x, y: s * ((x - cx) * c + (y - cy) * sn)


# ------------------------------------------------------------------ trilhas (pe de cada acesso -> pod)
def lanes():
    out = []
    for aa, w, k in L.ARENA_ACCESS:
        foot, top, d = L.access_frame(aa)
        fr = math.hypot(*foot)
        pts = []
        n = 6
        for i in range(n + 1):
            f = i / n
            r = fr + 0.8 - (fr + 0.8 - 7.8) * f
            wob = math.sin(f * math.pi * 1.6 + aa * 0.07) * 1.1 * math.sin(f * math.pi)
            pts.append(P2(aa + math.degrees(wob / max(r, 4.0)), r))
        out.append((aa, pts))
    return out


LANES = lanes()


def floor_free(x, y, rad):
    """ponto livre para relevo do piso (longe das trilhas, escadas, rochas, pod e da borda)"""
    r = math.hypot(x, y)
    a = ang_of(x, y)
    if r > R(a) - 4.0 - rad or r < 11.0 + rad:
        return False
    for aa, pts in LANES:
        if L.polyline_dist(x, y, pts) < 2.6 + rad + 0.8:
            return False
    for rx, ry, rr, h in L.ARENA_ROCKS:
        if math.hypot(x - rx, y - ry) < rr + rad + 1.2:
            return False
    return True


# ------------------------------------------------------------------ 1. piso da arena
def floor():
    rng = random.Random(2301)
    mb = MB("DB_Mine_Floor", COLL, rng, detail="far")
    # base (cobre ate debaixo do muro); topo 20,12
    mb.prism(ccw(L.polar_poly(lambda a: R(a) + 0.6, 3.0)), A - 6.0, A - 0.08, "Sand_DB")
    # trilhas batidas (areia clara compactada) do pe dos acessos ate o pod
    for aa, pts in LANES:
        mb.prism(ribbon_poly(pts, 2.0), A - 0.2, A + 0.05, "Sand_DBMineLight")
    # manchas de areia escura
    spots = []
    tries = 0
    while len(spots) < 7 and tries < 600:
        tries += 1
        a = rng.uniform(0, 360)
        rr = rng.uniform(4.0, 7.5)
        r = rng.uniform(14.0, R(a) - 6.0)
        x, y = P2(a, r)
        if not floor_free(x, y, rr * 0.8):
            continue
        if any(math.hypot(x - sx, y - sy) < rr + sr + 2.0 for sx, sy, sr, _ in spots):
            continue
        spots.append((x, y, rr, "patch"))
    for x, y, rr, kind in spots:
        th = math.radians(rng.uniform(25.0, 55.0))            # alongada pelo vento (SO -> NE), contorno organico
        pts = []
        for t in range(18):
            q = 2 * math.pi * t / 18
            rq = rr * (1.0 + 0.22 * math.sin(3 * q + x) + rng.uniform(-0.08, 0.08))
            lx, ly = math.cos(q) * rq * 1.35, math.sin(q) * rq * 0.62
            pts.append((x + lx * math.cos(th) - ly * math.sin(th), y + lx * math.sin(th) + ly * math.cos(th)))
        mb.prism(ccw(pts), A - 0.2, A - 0.01, "Sand_DBMineDark")
    # 2 placas de terra rachada RENTES ao piso (so linhas finas de racha, baixo contraste), longe dos ORE_* e trilhas
    ores = L.ore_points()
    tries = 0
    cracks = []
    while len(cracks) < 2 and tries < 1500:
        tries += 1
        a = rng.uniform(0, 360)
        rr = rng.uniform(3.2, 4.2)
        r = rng.uniform(14.0, R(a) - 7.0)
        x, y = P2(a, r)
        if not floor_free(x, y, rr):
            continue
        if any(math.hypot(x - ox, y - oy) < rr + orad + 1.5 for _, _, ox, oy, orad in ores):
            continue
        if any(math.hypot(x - sx, y - sy) < rr + sr + 3.0 for sx, sy, sr, _ in spots):
            continue
        spots.append((x, y, rr, "crack"))
        cracks.append((x, y, rr))
    for x, y, rr in cracks:
        th = rng.uniform(0, math.pi)
        edge = []
        for t in range(16):
            q = 2 * math.pi * t / 16
            rq = rr * (1.0 + 0.2 * math.sin(3 * q + x) + rng.uniform(-0.12, 0.12))
            lx, ly = math.cos(q) * rq * 1.25, math.sin(q) * rq * 0.8
            edge.append((x + lx * math.cos(th) - ly * math.sin(th), y + lx * math.sin(th) + ly * math.cos(th)))
        mb.prism(ccw(edge), A - 0.2, A + 0.0, "Sand_DBMineDark")
        inner = [(x + (px - x) * 0.82, y + (py - y) * 0.82) for px, py in edge]
        # rachas de lama seca: arestas de uma colmeia irregular (celulas ~1,25), linhas finas rentes (0,22)
        cs = rng.uniform(1.15, 1.35)
        rot = rng.uniform(0, math.pi)
        cr_, sr_ = math.cos(rot), math.sin(rot)
        jit = {}

        def hv(px, py):
            key = (round(px, 2), round(py, 2))
            if key not in jit:
                jit[key] = (px + rng.uniform(-0.3, 0.3), py + rng.uniform(-0.3, 0.3))
            return jit[key]
        edges = set()
        nq = int(rr / (1.5 * cs)) + 2
        for q in range(-nq, nq + 1):
            for rq in range(-nq - 2, nq + 3):
                hx, hy = cs * 1.5 * q, cs * math.sqrt(3.0) * (rq + q / 2.0)
                vs = [(round(hx + cs * math.cos(k * math.pi / 3), 2), round(hy + cs * math.sin(k * math.pi / 3), 2))
                      for k in range(6)]
                for k in range(6):
                    e = tuple(sorted((vs[k], vs[(k + 1) % 6])))
                    edges.add(e)
        for (ax, ay), (bx, by) in sorted(edges):
            pa, pb = hv(ax, ay), hv(bx, by)
            wa = (x + pa[0] * cr_ - pa[1] * sr_, y + pa[0] * sr_ + pa[1] * cr_)
            wb = (x + pb[0] * cr_ - pb[1] * sr_, y + pb[0] * sr_ + pb[1] * cr_)
            if not (L.point_in_poly(wa[0], wa[1], inner) and L.point_in_poly(wb[0], wb[1], inner)):
                continue
            mb.prism(ribbon_poly([wa, wb], 0.11), A - 0.05, A + 0.02, "Dirt_DB")
    # ondulacoes de vento (grupos de 3 cristas paralelas, baixas)
    prof = [(-0.55, 0.0), (0.0, 0.1), (0.55, 0.0)]
    groups = 0
    tries = 0
    while groups < 7 and tries < 600:
        tries += 1
        a = rng.uniform(0, 360)
        r = rng.uniform(15.0, R(a) - 9.0)
        x, y = P2(a, r)
        if not floor_free(x, y, 5.5):
            continue
        if any(math.hypot(x - sx, y - sy) < sr + 6.5 for sx, sy, sr, _ in spots):
            continue
        spots.append((x, y, 5.0, "ripple"))
        groups += 1
        th = math.radians(rng.uniform(20.0, 50.0))        # vento de SO: cristas ~perpendiculares
        tx, ty = math.cos(th), math.sin(th)
        nx, ny = -ty, tx
        nl = 3
        for li in range(nl):
            off = (li - (nl - 1) / 2) * 1.9
            ln = rng.uniform(7.0, 11.0) * (1.0 - abs(li - (nl - 1) / 2) * 0.12)
            pts = []
            for k in range(8):
                f = k / 7 - 0.5
                bend = math.sin((f + 0.5) * math.pi) * 0.45 + math.sin(f * 7.0 + li) * 0.3    # pouco arco: nada de seta
                pts.append((x + tx * f * ln + nx * (off + bend), y + ty * f * ln + ny * (off + bend), A - 0.08))
            mb.sweep(pts, prof, "Sand_DBMineLight", True)
    mb.finish()


# ------------------------------------------------------------------ 2. borda da bacia (setores) + guardas visuais
def rim_band(mb, a0, a1, top_m, face_m, rin_off=-0.1, z_top=G + 0.04):
    """faixa continua da borda (face vertical para a arena + tampo ate a guarda); fecha o que as pecas nao cobrem"""
    DL.ring_band(mb, lambda a: R(a) + rin_off, lambda a: R(a) + 1.25, A - 0.3, z_top, top_m, step=2.0,
                 wall_m=face_m, walls=(True, False), a0=a0, a1=a1)


def in_occ(a, occ):
    return any(o0 < a < o1 for o0, o1 in occ)


RIM_GEO = [(A + 2.45, A + 2.8, TOP, 0.1)]            # estrato claro fino da borda natural (E e W)


def on_rim(am, hl, off):
    """peca reta ao longo da borda: corda entre os pontos R(a) + off nos angulos am -+ hl (a corda acompanha a
    variacao do raio da bacia; nas pontas fica exatamente a 'off' da borda). -> (cx, cy, yaw, meio-comprimento);
    yaw = sentido anti-horario, +y local = para dentro da arena"""
    a0, a1 = am - deg_at(hl, am), am + deg_at(hl, am)
    pa, pb = P2(a0, R(a0) + off), P2(a1, R(a1) + off)
    return ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2, math.atan2(pb[1] - pa[1], pb[0] - pa[0]),
            math.hypot(pb[0] - pa[0], pb[1] - pa[1]) / 2)


def wall_blocks(mr, r0, r1, rng, occ=(), top=(-0.9, -0.2), crest=0.1, crest_h=(0.2, 0.5)):
    """face natural da borda: blocos de rocha lado a lado (face interna em R - 0,12..0,17: nunca mais de 0,2 para
    dentro da colisao da borda), topos em alturas variadas, juntas escuras entre eles"""
    ang = r0 + deg_at(0.15, r0)
    while ang < r1 - 0.3:
        a = rng.uniform(1.6, 3.4)
        am = ang + deg_at(a, ang)
        if am + deg_at(a, am) > r1 - deg_at(0.1, r1):
            a = math.radians(r1 - ang) * R(ang) / 2 - 0.1
            if a < 0.7:
                break
            am = ang + deg_at(a, ang)
        if not in_occ(am, occ):
            b = rng.uniform(0.55, 0.66)
            cx, cy, yaw, hl = on_rim(am, a, b + 0.02)
            zt = G + (rng.uniform(*crest_h) if rng.random() < crest else rng.uniform(*top))
            foot = to_world(rbox(hl, b, [rng.uniform(0.2, 0.45) for _ in range(4)],
                                 [0.0, rng.uniform(0.0, 0.06), 0.0, 0.0]), cx, cy, yaw)
            banded(mr, foot, A - 0.3, zt, rng, bands=RIM_GEO, base=(A + rng.uniform(1.3, 1.7), DARK, 0.0),
                   taper=0.05, band=0.35, ch=0.18, jit=0.05,
                   top_tilt=local_tilt(cx, cy, yaw, rng.choice((-1, 1)) * rng.uniform(0.03, 0.09)))
        ang = am + deg_at(a + rng.uniform(0.25, 0.5), am)


def slabs(mr, r0, r1, rng, occ=(), h=(0.45, 0.9), ln=(1.6, 3.4), gap=(1.2, 3.2)):
    """guarda visual natural na linha da guarda invisivel (R + 0,7): POUCAS lajes de rocha compridas e baixas, de
    tamanhos diferentes, com vaos (a colisao da borda segura o jogador); nunca colar de pedrinhas iguais"""
    ang = r0 + deg_at(rng.uniform(0.3, 1.5), r0)
    while ang < r1 - 0.5:
        a = rng.uniform(*ln)
        am = ang + deg_at(a, ang)
        if am + deg_at(a, am) > r1 - deg_at(0.2, r1):
            a = math.radians(r1 - ang) * R(ang) / 2 - 0.2
            if a < 1.0:
                break
            am = ang + deg_at(a, ang)
        lo, hi = am - deg_at(a, am), am + deg_at(a, am)
        if not any(o0 < hi and lo < o1 for o0, o1 in occ):
            b = rng.uniform(0.42, 0.5)
            cx, cy, yaw, hl = on_rim(am, a, 0.7)
            zt = G + rng.uniform(*h)
            foot = to_world(rbox(hl, b, [rng.uniform(0.25, 0.4) for _ in range(4)]), cx, cy,
                            yaw + rng.uniform(-0.04, 0.04))
            banded(mr, foot, G - 0.35, zt, rng, taper=0.06, band=0.25, ch=0.15, jit=0.04,
                   top_tilt=local_tilt(cx, cy, yaw, rng.uniform(-0.05, 0.05)))
        ang = am + deg_at(a + rng.uniform(*gap), am)


def standing(mr, am, a, dz, rng):
    """rocha em pe na linha da guarda (dentro da faixa R+0,0..R+1,24): marco natural baixo"""
    b = 0.6
    cx, cy, yaw, hl = on_rim(am, a, 0.66)
    foot = to_world(rbox(hl, b, [rng.uniform(0.25, 0.45) for _ in range(4)],
                         [0.0, rng.uniform(0.04, 0.1), 0.0, rng.uniform(0.05, 0.15)]), cx, cy, yaw)
    banded(mr, foot, A - 0.3, G + dz, rng, bands=RIM_GEO, base=(A + 1.5, DARK, 0.0), taper=0.18, band=0.45,
           ch=0.25, jit=0.05)


def south(ms, mt, rng):
    """S: muro de arrimo em arenito cortado (3 fiadas + capa) + guarda Capsule (postes brancos, corrimao azul,
    capuz ciano)"""
    a0, a1 = SECTORS["S"]
    for r0, r1 in runs(a0, a1):
        rim_band(ms, r0, r1, "Stone_Paving_DB", "Dirt_DB", rin_off=0.12, z_top=G - 0.3)
        # fiadas de blocos (juntas escuras = a face Dirt_DB atras)
        courses = [(A - 0.1, A + 1.3, (3.2, 4.6)), (A + 1.42, A + 2.62, (2.6, 3.8)), (A + 2.74, G - 0.36, (2.2, 3.4))]
        for ci, (z0, z1, (lmin, lmax)) in enumerate(courses):
            s = ci * 0.37
            rm = R((r0 + r1) / 2)
            ang = r0 + math.degrees(0.12 / rm)
            first = True
            while ang < r1 - 0.2:
                ln = rng.uniform(lmin, lmax) * (0.5 + s if first else 1.0)
                first = False
                da = math.degrees(ln / R(ang))
                b = min(ang + da, r1 - math.degrees(0.06 / R(ang)))
                if b - ang < math.degrees(0.8 / R(ang)):
                    break
                am = (ang + b) / 2
                rr = R(am)
                cx, cy, yaw, hl = on_rim(am, math.radians(b - ang) * rr / 2, 0.17)
                ms.box((2 * hl - 0.12, 0.5, z1 - z0), (cx, cy, (z0 + z1) / 2), (0, 0, yaw), SANDSTONE, 0.1)
                ang = b + math.degrees(0.12 / rr)
        # capa (coping) em lajes: sobressai 0,22 para dentro, cobre ate a guarda
        n = max(1, int(math.radians(r1 - r0) * R((r0 + r1) / 2) / 3.2))
        for i in range(n):
            ca = r0 + (r1 - r0) * i / n + (0.0 if i == 0 else math.degrees(0.07 / R(r0)))
            cb = r0 + (r1 - r0) * (i + 1) / n - (0.0 if i == n - 1 else math.degrees(0.07 / R(r0)))
            ms.prism(sector_poly(ca, cb, lambda a: R(a) - 0.22, lambda a: R(a) + 1.25, 1.0), G - 0.36, G + 0.14,
                     "Stone_Paving_DB", 0.0)
        # guarda Capsule na linha da guarda invisivel (R + 0,7): postes a cada ~4,4 + corrimao azul + barra de aco
        rg = lambda a: R(a) + 0.7
        arc = math.radians(r1 - r0) * R((r0 + r1) / 2)
        n = max(1, int(round(arc / 4.4)))
        for i in range(n + 1):
            a = r0 + (r1 - r0) * i / n
            a = min(max(a, r0 + math.degrees(0.5 / R(a))), r1 - math.degrees(0.5 / R(a)))
            p = P(a, rg(a))
            yaw = math.radians(a)
            mt.box((0.72, 0.72, 2.6), (p.x, p.y, G + 0.14 + 1.3), (0, 0, yaw), "Plaster_DB_White", 0.1)
            mt.box((0.9, 0.9, 0.32), (p.x, p.y, G + 0.14 + 0.16), (0, 0, yaw), "Plaster_DB_Navy", 0.06)
            mt.cyl(0.34, 0.34, (p.x, p.y, G + 0.14 + 2.6 + 0.17), m="DB_Cyan_Glow", n=8, bevel=0.0)
        k = max(2, int((r1 - r0) / 1.5) + 1)
        top = [P(r0 + (r1 - r0) * i / (k - 1), rg(r0 + (r1 - r0) * i / (k - 1)), G + 0.14 + 2.2) for i in range(k)]
        mt.sweep(top, [(-0.2, -0.17), (0.2, -0.17), (0.2, 0.17), (-0.2, 0.17)], "Roof_DB_Blue", True)
        mid = [V((p.x, p.y, G + 0.14 + 1.15)) for p in top]
        mt.sweep(mid, [(0.12 * math.cos(t * math.pi / 3), 0.12 * math.sin(t * math.pi / 3)) for t in range(6)],
                 "Metal_DB_Steel", True)


# E: rochas em pe (angulo, meio-comprimento, altura acima do promenade) e prateleiras baixas andaveis
# (angulo, meio-comprimento, quanto avanca na arena, topo acima do piso da arena)
E_STANDING = [(331.0, 1.5, 2.2), (357.0, 1.3, 1.7), (38.5, 1.7, 2.4)]
E_SHELVES = [(343.0, 3.0, 2.6, 1.5), (29.0, 2.6, 2.4, 1.75)]


def east(mr, rng):
    """E: borda natural BAIXA - blocos de rocha na face, 2 prateleiras baixas (andaveis, colisao propria), 3 rochas
    em pe e poucas lajes compridas com vaos"""
    a0, a1 = SECTORS["E"]
    occ = [(a - deg_at(hl + 0.8, a), a + deg_at(hl + 0.8, a)) for a, hl, dz in E_STANDING]
    occ += [(a + 360.0 - deg_at(hl + 0.8, a), a + 360.0 + deg_at(hl + 0.8, a)) for a, hl, dz in E_STANDING if a < 90]
    for r0, r1 in runs(a0, a1):
        rim_band(mr, r0, r1, TOP, DARK, rin_off=0.25)
        wall_blocks(mr, r0, r1, rng, top=(-0.95, -0.3), crest=0.08)
        slabs(mr, r0, r1, rng, occ, h=(0.45, 0.85), ln=(1.8, 3.6), gap=(1.4, 3.4))
    for a, hl, dz in E_STANDING:
        standing(mr, a, hl, dz, rng)
    for a, hl, pro, zt in E_SHELVES:
        b = (pro + 0.5) / 2
        cx0, cy0, yaw, hl = on_rim(a, hl, -pro + b)
        c = (cx0, cy0)
        foot = to_world(rbox(hl, b, [0.2, rng.uniform(0.7, 1.0), rng.uniform(0.7, 1.0), 0.2],
                             [0.0, rng.uniform(0.1, 0.2), 0.0, 0.0]), c[0], c[1], yaw)
        banded(mr, foot, A - 0.3, A + zt, rng, taper=0.1, band=0.35, ch=0.2, jit=0.06,
               tilt=local_tilt(c[0], c[1], yaw, 0.03), tamp=0.1)
        # colisao: 0,25 atras da frente visual (a quina chanfrada nao vira parede invisivel)
        ux, uy = math.cos(yaw), math.sin(yaw)
        vx, vy = -math.sin(yaw), math.cos(yaw)             # +y local = para dentro da arena
        cx, cy = c[0] - vx * 0.12, c[1] - vy * 0.12
        col_box("DB_MineShelf", (2 * hl - 0.4, 2 * b - 0.25, A + zt - (A - 0.5)), (cx, cy, (A + zt + A - 0.5) / 2),
                (0, 0, yaw))


def north(mr, ms, rng):
    """N: patamares naturais de arenito em UNIDADES que se alternam ao longo do arco (nada de arquibancada):
    'a' = patamar baixo L1 (~A+1,3) + alto L2 (~A+2,65) atras; 'c' = so o baixo, fundo ate a borda (baia: a face de
    rocha da borda aparece atras); 'b' = massa alta que atravessa os dois (fora das rotas do patamar). Cada bloco com
    altura (+-0,3), fundo e cor proprios, pontas arredondadas, entalhes, estrato inclinado; colisao por bloco.
    1 pedra grande sobre o patamar alto por lado. Parapeito de blocos cortados de tamanhos variados, com vaos."""
    a0, a1 = SECTORS["N"]
    clip = lambda x, y: clear_access(x, y, 1.3)
    for r0, r1 in runs(a0, a1):
        rim_band(mr, r0, r1, TOP, ROCK, rin_off=0.02)
        ang = r0
        prev = None
        n_b = 0
        boulder = False
        while ang < r1 - 0.2:
            ln = rng.uniform(6.0, 10.0)
            b_ang = min(r1, ang + math.degrees(ln / R(ang)))
            if r1 - b_ang < math.degrees(3.2 / R(b_ang)):
                b_ang = r1
            on_route = any(s0 - 3.0 < b_ang and ang < s1 + 3.0 for s0, s1 in LEDGE_ROUTE_SPANS)
            opts = ["a", "a", "c"] if on_route else ["a", "c", "b", "b"]
            opts = [o for o in opts if o != prev or o == "a"]
            if n_b >= 1:
                opts = [o for o in opts if o != "b"] or ["a"]
            kind = rng.choice(opts)
            if kind == "b":
                n_b += 1
                b_ang = min(b_ang, ang + deg_at(rng.uniform(3.6, 5.5), ang))
                ledge_block(mr, ang, b_ang, rng.uniform(3.9, 4.6), 0.3, A + rng.uniform(2.8, 3.2), rng, clip,
                            band=0.45, cross=True)
            elif kind == "c":
                ledge_block(mr, ang, b_ang, rng.uniform(3.9, 5.0), 0.3, A + 1.3 + rng.uniform(-0.3, 0.3), rng, clip,
                            band=rng.uniform(0.22, 0.4), body=rng.choice((ROCK, DARK)))
                wall_blocks(mr, ang, b_ang, rng, top=(-0.8, -0.1), crest=0.3, crest_h=(0.2, 0.6))
            else:
                ledge_block(mr, ang, b_ang, rng.uniform(3.9, 5.2), -0.6, A + 1.3 + rng.uniform(-0.3, 0.3), rng, clip,
                            band=rng.uniform(0.22, 0.4), body=rng.choice((ROCK, ROCK, DARK)))
                ledge_block(mr, ang, b_ang, rng.uniform(1.7, 2.2), 0.3, A + 2.65 + rng.uniform(-0.3, 0.3), rng, clip,
                            band=rng.uniform(0.25, 0.45))
                if not boulder and not on_route and b_ang - ang > deg_at(4.0, ang):
                    boulder = True
                    am = (ang + b_ang) / 2 + rng.uniform(-0.2, 0.2) * (b_ang - ang)
                    hl = rng.uniform(1.3, 1.7)
                    b = rng.uniform(0.85, 1.0)
                    cx, cy, yaw, hl = on_rim(am, hl, b - 1.9)
                    yaw += rng.uniform(-0.25, 0.25)
                    foot = to_world(rbox(hl, b, [rng.uniform(0.35, 0.6) for _ in range(4)],
                                         [rng.uniform(0.05, 0.2), rng.uniform(0.05, 0.2), 0.0, 0.0]), cx, cy, yaw)
                    zt = G + rng.uniform(0.8, 1.6)
                    banded(mr, foot, A + 2.0, zt, rng, base=(A + 3.2, DARK, 0.08), taper=0.25, band=0.45, ch=0.3,
                           jit=0.08)
                    col_box("DB_MineLedge", (2 * hl - 0.4, 2 * b - 0.4, zt - (A + 1.5)), (cx, cy, (zt + A + 1.5) / 2),
                            (0, 0, yaw))
            prev = kind
            ang = b_ang
        # parapeito: blocos de arenito cortado (2..4,2 de comprimento, 0,55..1,2 de altura), encostados ou com vaos
        ang = r0 + deg_at(0.4, r0)
        while ang < r1 - 0.3:
            ln = rng.uniform(2.0, 4.2)
            am = ang + deg_at(ln / 2, ang)
            end = am + deg_at(ln / 2, am)
            if end > r1:
                break
            pa, pb = P2(ang, R(ang) + 0.7), P2(end, R(end) + 0.7)
            near = any(lateral(aa, *q)[1] < w / 2 + 1.35 and -1.0 <= lateral(aa, *q)[0] <= 12.0
                       for aa, w, k in L.ARENA_ACCESS for q in (pa, pb))
            if not near:
                hh = rng.uniform(0.55, 1.2)
                dp = rng.uniform(0.9, 1.1)
                cx, cy, yaw, hl = on_rim(am, ln / 2, 0.7)
                yaw += rng.uniform(-0.04, 0.04)
                ms.box((2 * hl, dp, hh + 0.1), (cx, cy, G - 0.1 + (hh + 0.1) / 2), (0, 0, yaw), SANDSTONE, 0.12)
                if rng.random() < 0.18 and ln > 2.4:
                    s = rng.uniform(-0.25, 0.25) * ln
                    ms.box((ln * 0.45, dp * 0.8, 0.4), (cx + math.cos(yaw) * s, cy + math.sin(yaw) * s, G + hh + 0.2),
                           (0, 0, yaw + rng.uniform(-0.08, 0.08)), SANDSTONE, 0.1)
            r = rng.random()
            g = 0.0 if r < 0.25 else (rng.uniform(2.2, 3.4) if r > 0.8 else rng.uniform(0.8, 1.8))
            ang = end + deg_at(g + 0.06, end)


LEDGE_ROUTE_SPANS = [(60.0, 80.0), (118.0, 131.0)]     # trechos das EXTRA_ROUTES ao longo do patamar L1


def ledge_block(mr, a0, a1, d, back, zt, rng, clip, band=0.35, cross=False, body=ROCK):
    """bloco de patamar N entre os angulos a0..a1: radial de R(a) - d (frente) ate R(a) + back nas duas pontas (a
    corda acompanha a variacao do raio da bacia); pontas da frente arredondadas (entalhe entre blocos), estrato
    inclinado ao longo do bloco; colisao propria (frente 0,25 atras do visual)"""
    b = (d + back) / 2
    pa = P2(a0, R(a0) - d + b)
    pb = P2(a1, R(a1) - d + b)
    c = ((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2)
    yaw = math.atan2(pb[1] - pa[1], pb[0] - pa[0])      # x local = corda, +y local = para dentro (arena)
    hl = math.hypot(pb[0] - pa[0], pb[1] - pa[1]) / 2 + 0.25
    fc = rng.uniform(0.5, 0.9)
    foot = to_world(rbox(hl, b, [0.12, fc, rng.uniform(0.5, 0.9), 0.12],
                         [0.0, rng.uniform(0.0, 0.18), 0.0, 0.0]), c[0], c[1], yaw)
    tl = local_tilt(c[0], c[1], yaw, rng.choice((-1, 1)) * rng.uniform(0.02, 0.035))
    top_m = TOP if (cross or rng.random() < 0.4) else ROCK        # nem todo bloco com faixa clara (nada de listra)
    banded(mr, foot, A - 0.3, zt, rng, base=(A + 0.5, DARK, 0.1) if cross else None, taper=0.1 if cross else 0.06,
           band=band, ch=0.2, jit=0.07, tilt=tl, tamp=0.16, clip=clip, body=body, top_m=top_m)
    ux, uy = math.cos(yaw), math.sin(yaw)
    vx, vy = -math.sin(yaw), math.cos(yaw)
    ym = -0.125
    ta = hl - 0.15
    e0 = clear_access(c[0] - ux * ta + vx * ym, c[1] - uy * ta + vy * ym, 1.35)
    e1 = clear_access(c[0] + ux * ta + vx * ym, c[1] + uy * ta + vy * ym, 1.35)
    dx, dy = e1[0] - e0[0], e1[1] - e0[1]
    ln = math.hypot(dx, dy)
    if ln > 0.8:
        col_box("DB_MineLedge", (ln, 2 * b - 0.25, zt - (A - 0.5)), ((e0[0] + e1[0]) / 2, (e0[1] + e1[1]) / 2,
                                                                      (zt + A - 0.5) / 2), (0, 0, math.atan2(dy, dx)))


# W: grupos de pilares de canion (pilar alto T + medio M + quebra baixa B). Estratos W (cotas absolutas):
W_GEO = [(A + 3.9, A + 4.75, TOP, 0.0)]      # camada clara grossa (so cor, sem sulco: nada de aro de barril)
W_BASE = (A + 1.7, DARK, 0.14)
# (ang_T, hl_T, dp_T, altura_T acima do promenade, quanto T avanca na arena, lado de M (+1 anti-horario),
#  hl_M, dp_M, altura_M, hl_B, dp_B, topo_B acima do piso da arena)
W_GROUPS = [(151.0, 2.0, 1.9, 8.0, 1.7, -1, 1.55, 1.5, 5.0, 1.4, 1.0, 1.8),
            (166.0, 1.8, 1.7, 6.0, 1.4, 1, 1.4, 1.35, 3.6, 1.2, 0.9, 1.5),
            (193.5, 2.0, 1.9, 7.5, 1.6, 1, 1.5, 1.45, 4.5, 1.3, 1.0, 2.1),
            (209.5, 1.8, 1.7, 5.5, 1.4, -1, 1.4, 1.35, 3.4, 1.1, 0.9, 1.4)]
W_LONE = (139.5, 1.5, 1.4, 3.2, 1.0)


def pillar(mr, am, hl, dp, pin, ztop, rng, taper, name_col, radial_off=0.0, band=0.7):
    """pilar de canion: paredes quase a prumo (recuo total 'taper'), estratos horizontais W, topo plano chanfrado.
    Face interna em R - pin. Colisao: caixa orientada do tamanho do pilar a meia altura."""
    cx, cy, yaw, hl = on_rim(am, hl, -pin + dp + radial_off)
    c = (cx, cy)
    cham = [rng.uniform(0.3, 0.55) for _ in range(4)]
    # pontas com barriga; faces longas com barriga OU fratura vertical rasa (<= 0,28: dentro da folga da colisao)
    bul = [rng.uniform(0.05, 0.18), rng.choice((-1, 1)) * rng.uniform(0.12, 0.28), rng.uniform(0.05, 0.18),
           rng.choice((-1, 1)) * rng.uniform(0.12, 0.28)]
    foot = to_world(rbox(hl, dp, cham, bul), c[0], c[1], yaw)
    banded(mr, foot, A - 0.3, ztop, rng, bands=W_GEO, base=W_BASE, taper=taper, band=band, ch=0.35, jit=0.06)
    k = taper / 2 + 0.12
    col_box(name_col, (2 * (hl - k), 2 * (dp - k), ztop - (A - 1.0)), (c[0], c[1], (ztop + A - 1.0) / 2), (0, 0, yaw))
    return c


def west(mr, rng):
    """W: pilares de canion verticais em grupos (alto + medio + quebra baixa) com estratos horizontais continuos;
    entre eles, face de blocos e poucas lajes"""
    a0, a1 = SECTORS["W"]
    occ = []
    for g in W_GROUPS:
        aT, hlT, dpT, hT, pin, side, hlM, dpM, hM, hlB, dpB, hB = g
        aM = aT + side * deg_at((hlT + hlM) * 0.78, aT)
        lo = min(aT - deg_at(hlT, aT), aM - deg_at(hlM, aM))
        hi = max(aT + deg_at(hlT, aT), aM + deg_at(hlM, aM))
        occ.append((lo - deg_at(0.3, lo), hi + deg_at(0.3, hi)))
    aL, hlL, dpL, hL, pinL = W_LONE
    occ.append((aL - deg_at(hlL + 0.3, aL), aL + deg_at(hlL + 0.3, aL)))
    for r0, r1 in runs(a0, a1):
        rim_band(mr, r0, r1, TOP, DARK, rin_off=0.25)
        wall_blocks(mr, r0, r1, rng, occ, top=(-0.7, -0.1), crest=0.3, crest_h=(0.2, 0.7))
        slabs(mr, r0, r1, rng, occ, h=(0.6, 1.2), ln=(1.4, 2.8), gap=(1.0, 2.6))
    for g in W_GROUPS:
        aT, hlT, dpT, hT, pin, side, hlM, dpM, hM, hlB, dpB, hB = g
        pillar(mr, aT, hlT, dpT, pin, G + hT, rng, 0.3, "DB_MineOutcrop", band=0.75)
        aM = aT + side * deg_at((hlT + hlM) * 0.78, aT)
        pillar(mr, aM, hlM, dpM, pin * 0.55, G + hM, rng, 0.22, "DB_MineOutcrop", band=0.6)
        aB = aT + side * deg_at(hlT * 0.75, aT)
        # quebra baixa: na frente da juncao T/M, avanca ~1,2 alem da face de T
        cx, cy, yaw, hlB = on_rim(aB, hlB, -pin - 1.2 + dpB)
        c = (cx, cy)
        yaw += rng.uniform(-0.2, 0.2)
        foot = to_world(rbox(hlB, dpB, [rng.uniform(0.3, 0.5) for _ in range(4)],
                             [0.0, rng.uniform(0.05, 0.15), 0.0, 0.0]), c[0], c[1], yaw)
        banded(mr, foot, A - 0.3, A + hB, rng, taper=0.1, band=0.4, ch=0.25, jit=0.05)
        col_box("DB_MineOutcrop", (2 * (hlB - 0.17), 2 * (dpB - 0.17), A + hB - (A - 1.0)),
                (c[0], c[1], (A + hB + A - 1.0) / 2), (0, 0, yaw))
    pillar(mr, aL, hlL, dpL, pinL, G + hL, rng, 0.18, "DB_MineOutcrop", band=0.55)


# ------------------------------------------------------------------ 3. escadas, bochechas e rampa
STYLE = {270.0: "S", 90.0: "N", 180.0: "W", 222.0: "W", 318.0: "E"}


def stair_cheek_col(F, run, w, s):
    """guarda da lateral da escada (mesma formula do db_col.stair_col; invisivel 3,2 acima da linha dos pisos, o
    visual fica em ~1,3: o Humanoid passa por cima de guarda < 2). Comeca em t = 0,6 (pe livre para o minerio)"""
    rise, tread = (G - A) / 5, L.TREAD
    k = rise / tread
    Hh = 3.2
    off = k * (tread * k / 2 + Hh) / (1 + k * k)
    y = s * (w / 2 + 0.65)
    xa, xb = max(-off, 0.6), run + 1.2
    pa = F.p(xa, y, A + (xa + tread / 2) * k + Hh)
    pb = F.p(xb, y, A + (xb + tread / 2) * k + Hh)
    col_ramp("DB_MineCheek", pa, pb, 1.2, thick=Hh + 1.5)


def stairs(ms, mr, mt, rng):
    for nm, base, ang, w, n, rise, tread, g in db_col.stair_list():
        if not nm.startswith("Arena"):
            continue
        DL.vis_stairs(ms, base, ang, w, n, rise, tread, "Stone_Paving_DB", "Stone_DB_Block", stringers=False)
        aa = float(int(nm[5:]))
        F, run, w_, kind = access_frame(aa)
        style = STYLE.get(aa, "S")
        k = rise / tread
        # soleira na borda (liga o ultimo degrau ao promenade)
        c = F.p(run + 0.55, 0, 0)
        ms.box((1.45, w + 0.1, 0.42), (c.x, c.y, G - 0.09), F.r(), "Stone_Paving_DB", 0.06)
        for s in (-1, 1):
            y0, y1 = s * (w / 2 + 0.05), s * (w / 2 + 1.25)
            ym = (y0 + y1) / 2
            t0, t1, t2 = 0.4, run, run + 1.25
            ztop = lambda t: A + 0.8 + k * max(t, 0.0) + 0.55
            if style in ("S", "N"):
                # ala de alvenaria de arenito cortado com capa (sobe com a escada; na borda vira um pilarete)
                bm = SANDSTONE
                cap = "Stone_Paving_DB" if style == "S" else TOP
                bot = [F.p(t0, y0, A - 0.3), F.p(t1, y0, A - 0.3), F.p(t1, y1, A - 0.3), F.p(t0, y1, A - 0.3)]
                top = [F.p(t0, y0, ztop(t0) - 0.25), F.p(t1, y0, ztop(t1) - 0.25), F.p(t1, y1, ztop(t1) - 0.25),
                       F.p(t0, y1, ztop(t0) - 0.25)]
                hexa(ms, bot, top, bm)
                ms.box((t2 - t1, 1.2, ztop(t1) - 0.25 - (G - 0.4)), F.p((t1 + t2) / 2, ym, (ztop(t1) - 0.25 + G - 0.4) / 2),
                       F.r(), bm, 0.1)
                # capa inclinada + capa do pilarete
                cb = [F.p(t0 - 0.1, ym - 0.66, ztop(t0) - 0.3), F.p(t1, ym - 0.66, ztop(t1) - 0.3),
                      F.p(t1, ym + 0.66, ztop(t1) - 0.3), F.p(t0 - 0.1, ym + 0.66, ztop(t0) - 0.3)]
                ct = [V((p.x, p.y, p.z + 0.32)) for p in cb]
                hexa(ms, cb, ct, cap)
                q = F.p((t1 + t2) / 2, ym, 0)
                ms.box((t2 - t1 + 0.3, 1.45, 0.32), (q.x, q.y, ztop(t1) - 0.25 + 0.16), F.r(), cap, 0.08)
                if style == "S":
                    # poste-portal Capsule (branco, faixa azul, capuz ciano) na cabeca da escada
                    zb = ztop(t1) + 0.07
                    mt.box((0.95, 0.95, 2.4), (q.x, q.y, zb + 1.2), F.r(), "Plaster_DB_White", 0.12)
                    mt.box((1.05, 1.05, 0.4), (q.x, q.y, zb + 1.55), F.r(), "Roof_DB_Blue", 0.06)
                    mt.cyl(0.46, 0.42, (q.x, q.y, zb + 2.61), m="DB_Cyan_Glow", n=10, bevel=0.0)
            else:
                # bochecha natural: blocos de rocha que descem com a escada, DENTRO da faixa da guarda
                # (lateral w/2 + 0,05 .. w/2 + 1,25, a mesma da colisao DB_MineCheek)
                for t, dt in ((0.9, 0.0), (3.4, 0.2), (5.9, 0.35), (8.3, 0.5)):
                    zt = ztop(t) + rng.uniform(-0.15, 0.3) + dt
                    hl = rng.uniform(1.25, 1.55)
                    cc = F.p(t, s * (w / 2 + 0.65), 0)
                    foot = to_world(rbox(hl, 0.56, [rng.uniform(0.2, 0.4) for _ in range(4)]), cc.x, cc.y, F.a)
                    banded(mr, foot, A - 0.3, zt, rng, base=(A + rng.uniform(1.2, 1.6), DARK, 0.0), taper=0.06,
                           band=min(0.5, (zt - A) * 0.2), ch=0.2, jit=0.04)
            stair_cheek_col(F, run, w, s)


def ramp(ms, mr, rng):
    """rampa natural leste (casa com db_col.ramp_east: pe no ARENA, sobe ate R + 0,8 no GROUND) com lajes de
    arenito; o corpo abre para w/2 + 0,6 no topo (fecha a fresta com o recorte da borda); meio-fio = 2 lajes baixas
    compridas por lado, FORA da faixa, so no terco de cima (o minerio fica a 0,4 da lateral mais abaixo)"""
    for aa, w, kind in L.ARENA_ACCESS:
        if kind != "ramp":
            continue
        F, run, w_, k = access_frame(aa)
        te = run + 0.8                  # a rampa de colisao chega no GROUND 0,8 alem da borda
        tf = run + 1.25                 # fim da soleira (encosta na faixa do promenade)
        zf = lambda t: A + (G - A) * min(max(t, 0.0), te) / te
        hw0, hw1 = w / 2 + 0.1, w / 2 + 0.6
        loc = [(-0.3, -hw0), (te - 3.4, -hw0), (te - 1.8, -hw1), (te, -hw1), (te, hw1), (te - 1.8, hw1),
               (te - 3.4, hw0), (-0.3, hw0)]
        pts = [(F.p(t, s, 0).x, F.p(t, s, 0).y) for t, s in loc]
        zs = [zf(t) - 0.02 for t, s in loc]
        stack(mr, [(pts, A - 0.3, None), (pts, zs, DARK)], ch=0.0, top_m=DARK)
        c = F.p((te + tf) / 2, 0, 0)
        ms.box((tf - te + 0.1, w + 1.2, 0.45), (c.x, c.y, G - 0.1), F.r(), "Stone_DB_Block", 0.06)
        # lajes de arenito (8 fiadas, 2-3 pedras por fiada, juntas de 0,18)
        pitch = math.atan2(G - A, te)
        nrow = 8
        for i in range(nrow):
            ta, tb = te * i / nrow + 0.09, te * (i + 1) / nrow - 0.09
            tm = (ta + tb) / 2
            cuts = sorted([-w / 2 + 0.45] + [rng.uniform(-1.4, 1.4) + (j - 0.5) * 2.8 for j in range(rng.randint(1, 2))]
                          + [w / 2 - 0.45])
            for ya, yb in zip(cuts, cuts[1:]):
                if yb - ya < 1.0:
                    continue
                ym = (ya + yb) / 2
                p = F.p(tm, ym, zf(tm) - 0.08)
                ms.box(((tb - ta) / math.cos(pitch), yb - ya - 0.18, 0.3), p, (0, -pitch, F.a), SANDSTONE, 0.0)
        # meio-fio: 2 lajes baixas compridas por lado (topo 0,55 acima da rampa), lateral w/2+0,1 .. w/2+1,0
        for s in (-1, 1):
            t0c, t1c = 11.8, te + 0.3
            tm = rng.uniform(15.0, 15.8)
            for ta, tb in ((t0c, tm - 0.12), (tm + 0.12, t1c)):
                hl = (tb - ta) / 2
                tc = (ta + tb) / 2
                cc = F.p(tc, s * (w / 2 + 0.55), 0)
                foot = to_world(rbox(hl, 0.45, [0.35, 0.35, 0.35, 0.35]), cc.x, cc.y, F.a)
                tt = [(px - F.o.x) * math.cos(F.a) + (py - F.o.y) * math.sin(F.a) for px, py in foot]
                ztop = [zf(t) + 0.55 - 0.15 for t in tt]
                zmid = [z - 0.3 for z in ztop]
                zlow = [min(A + 1.5, z - 0.6) for z in ztop]
                stack(mr, [(foot, A - 0.3, None), (jitter_out(foot, 0.04, rng), zlow, DARK),
                           (foot, zmid, ROCK), (foot, ztop, TOP)], ch=0.15, top_m=TOP, flat=False)
            col_ramp("DB_MineRampCurb", F.p(t0c, s * (w / 2 + 0.55), zf(t0c) + 0.55),
                     F.p(t1c, s * (w / 2 + 0.55), zf(t1c) + 0.55), 0.9, thick=5.0)


# ------------------------------------------------------------------ 4. buttes da arena (ARENA_ROCKS)
def oct_spec(Rb, rng, vp=(0.04, 0.32), mp=(-0.12, 0.2), grooves=2, skip=2, e=0.0, phi=0.0, rot=0.0, prom=0,
             prom_p=(0.3, 0.5)):
    """contorno de rocha a partir do octogono de colisao (raio Rb = raio da coluna + 0,1; vertices em k*45 graus):
    vertices empurrados para FORA (vp), meios de aresta (mp; 'grooves' deles viram fratura vertical rasa, ate 0,25
    para dentro: a colisao fica no maximo ~0,2 alem da rocha), 'skip' meios omitidos (faces chatas); e = alongamento
    de um lado so (phi); rot = giro do octogono (o mesmo 'rot0' do ngon_col); prom = vertices salientes (quinas
    fortes: silhueta irregular, nada de tambor de 8 faces iguais). -> [(angulo, raio_base, empurrao)]"""
    mids = list(range(8))
    rng.shuffle(mids)
    gro = set(mids[:grooves])
    skp = set(mids[grooves:grooves + skip])
    pr = set(rng.sample(range(8), prom))
    spec = []
    for k in range(8):
        th = rot + k * math.pi / 4
        p = rng.uniform(*vp) + e * max(0.0, math.cos(th - phi)) ** 2 + (rng.uniform(*prom_p) if k in pr else 0.0)
        if (k - 1) % 8 in gro or k in gro:
            p += 0.12
        spec.append((th, Rb, p))
        if k in skp:
            continue
        tm = th + math.pi / 8
        pm = -0.25 if k in gro else rng.uniform(*mp) + e * max(0.0, math.cos(tm - phi)) ** 2
        spec.append((tm, Rb * math.cos(math.pi / 8), pm))
    return spec


def spec_ring(spec, cx, cy, pf, rmax=1e9):
    """anel do contorno (spec) com empurrao pf(angulo, p); rmax = raio maximo (plano: r + 12%)"""
    out = []
    for th, rb, p in spec:
        rr = min(rmax, rb + pf(th, p))
        out.append((cx + rr * math.cos(th), cy + rr * math.sin(th)))
    return out


# forma das buttes (FIXA: vira a coluna de colisao pedida ao db_col): (fracao da altura do patamar, angulo do
# deslocamento da torre, raio da torre / r, deslocamento da torre / r)
MESA_FORM = [(0.55, 200.0, 0.6, 0.25), (0.6, 35.0, 0.6, 0.25), (0.5, 250.0, 0.55, 0.28), (0.58, 110.0, 0.6, 0.25),
             (0.62, 300.0, 0.62, 0.22), (0.56, 160.0, 0.6, 0.25), (0.6, 75.0, 0.62, 0.22)]


def mesa_tiers(i):
    """coluna de colisao das ARENA_ROCKS em 2 camadas (pedido ao db_col, ngon_col 8, vertices em k*45 graus):
    [(cx, cy, raio, z0, z1, rot0) da base larga, (cx, cy, raio, z0, z1, rot0) da torre deslocada e girada]"""
    x, y, r, h = L.ARENA_ROCKS[i]
    zf, oa, r2f, of = MESA_FORM[i]
    zs = round(A + h * zf, 2)
    cx2 = round(x + of * r * math.cos(math.radians(oa)), 2)
    cy2 = round(y + of * r * math.sin(math.radians(oa)), 2)
    return [(x, y, round(MESA_COL_K * r, 3), A - 1.0, zs, 0.0), (cx2, cy2, round(r2f * r, 3), zs, A + h, 22.5)]


def mesa(mr, i, rng, shrub):
    """butte de arenito em 2 camadas: BASE larga (contem o octogono de colisao de raio 0,98 r) com pe escuro de
    estrato INCLINADO e ressalto parcial, faixa clara inclinada e patamar plano chanfrado; TORRE mais estreita
    DESLOCADA para um lado ate a altura da planta, com estrato escuro e topo plano chanfrado; fraturas verticais
    rasas e faces chatas; arbusto no patamar largo em 3 delas. Colisao = as 2 colunas (db_col, ver mesa_tiers)."""
    x, y, r, h = L.ARENA_ROCKS[i]
    (x1, y1, R1, _, zs, rot1), (x2, y2, R2, _, zt, rot2) = mesa_tiers(i)
    oa = math.radians(MESA_FORM[i][1])
    phi = oa + math.pi + rng.uniform(-0.5, 0.5)          # a base alonga para o lado do patamar largo
    spec = oct_spec(R1 + 0.1, rng, vp=(0.02, 0.14), mp=(-0.1, 0.1), grooves=2, skip=3, e=0.05 * r, phi=phi,
                    rot=math.radians(rot1), prom=3, prom_p=(0.22, 0.38))
    psi = oa + rng.choice((1, -1)) * rng.uniform(1.3, 2.0)       # lado do ressalto do pe escuro
    tamp = min(0.6, (zs - A - 1.6) * 0.22) * rng.uniform(0.8, 1.0)
    sm = tamp / (1.2 * r)
    beta = rng.uniform(0, math.tau)
    tilt = lambda px, py: sm * ((px - x) * math.cos(beta) + (py - y) * math.sin(beta))
    ch = 0.3
    band = max(0.5, tamp + 0.3)
    zd = A + min(h * rng.uniform(0.18, 0.24), (zs - A) * 0.42)
    zb = zs - ch - band
    ledge = lambda th: 0.03 + 0.42 * max(0.0, math.cos(th - psi)) ** 3
    rmax = 1.12 * r
    r0 = spec_ring(spec, x, y, lambda th, p: p + ledge(th), rmax)
    r1 = spec_ring(spec, x, y, lambda th, p: p + ledge(th) + rng.uniform(0.0, 0.04), rmax)
    r2 = spec_ring(spec, x, y, lambda th, p: p, rmax - 0.08)
    rings = [(r0, A - 0.3, None), (r1, [zd + tilt(*q) for q in r1], DARK), (r2, [zd + 0.07 + tilt(*q) for q in r2], TOP)]
    if zb - zd > 2 * tamp + 1.0:
        z3 = (zd + zb) / 2
        r3 = spec_ring(spec, x, y, lambda th, p: p + rng.uniform(0.0, 0.1), rmax - 0.08)
        rings.append((r3, [z3 + rng.uniform(-0.08, 0.08) for q in r3], ROCK))
    r4 = spec_ring(spec, x, y, lambda th, p: max(-0.25, p * 0.85), rmax - 0.12)
    rings += [(r4, [zb + tilt(*q) for q in r4], ROCK), (r4, zs - ch, TOP)]
    stack(mr, rings, ch=ch, top_m=TOP)
    # torre deslocada e girada 22,5 graus (nasce 0,5 dentro da base, pe alargado como talude sobre o patamar)
    spec2 = oct_spec(R2 + 0.1, rng, vp=(0.02, 0.12), mp=(-0.1, 0.1), grooves=1, skip=3, rot=math.radians(rot2),
                     prom=2, prom_p=(0.25, 0.4))
    ch2 = 0.3
    band2 = max(0.55, tamp + 0.3)
    t0 = spec_ring(spec2, x2, y2, lambda th, p: p + 0.45)
    tf = spec_ring(spec2, x2, y2, lambda th, p: p + rng.uniform(0.3, 0.45))
    t0b = spec_ring(spec2, x2, y2, lambda th, p: p + rng.uniform(0.0, 0.06))
    rings2 = [(t0, zs - 0.5, None), (tf, zs + 0.05, TOP), (t0b, zs + 0.55, ROCK)]
    zq = zs + (zt - zs) * rng.uniform(0.4, 0.52)
    if zq - tamp > zs + 0.95 and zt - ch2 - band2 - tamp - zq > 0.6:
        t1 = spec_ring(spec2, x2, y2, lambda th, p: p + rng.uniform(0.0, 0.08))
        rings2.append((t1, [zq + rng.uniform(-0.1, 0.1) for q in t1], ROCK))
    t3 = spec_ring(spec2, x2, y2, lambda th, p: max(-0.2, p * 0.8))
    z3 = max(zs + 0.85 + tamp, zt - ch2 - band2)
    rings2 += [(t3, [z3 + tilt(*q) for q in t3], ROCK), (t3, zt - ch2, TOP)]
    stack(mr, rings2, ch=ch2, top_m=TOP)
    if shrub:
        cx = x - math.cos(oa) * r * 0.62
        cy = y - math.sin(oa) * r * 0.62
        for k in range(2):
            a = rng.uniform(0, math.tau)
            d = rng.uniform(0.2, 0.6)
            mr.ico(rng.uniform(0.5, 0.75), (cx + math.cos(a) * d, cy + math.sin(a) * d, zs + 0.25),
                   "Leaf_Palm" if k else "Grass_DB", 1, (1, 1, 0.7), jitter=0.2)


def mesas(mr, rng):
    shrub = {0, 2, 3, 5}
    for i in range(len(L.ARENA_ROCKS)):
        mesa(mr, i, rng, i in shrub)


# ------------------------------------------------------------------ 5. pod de sondagem Capsule (centro)
def pod():
    rng = random.Random(2305)
    x, y, r = L.CORE_POD
    mb = MB("DB_Mine_Pod", COLL, rng, detail="hero")
    # patio: laje clara + aro azul-marinho + 6 setas azuis apontando para os acessos (ponto de encontro)
    mb.cyl(8.1, 0.28, (x, y, A - 0.04), m="Plaster_DB_Navy", n=32, bevel=0.0)
    mb.cyl(7.5, 0.3, (x, y, A + 0.01), m="Stone_Paving_DB", n=32, bevel=0.0)
    for aa, w, k in L.ARENA_ACCESS:
        ux, uy = math.cos(math.radians(aa)), math.sin(math.radians(aa))
        nx, ny = -uy, ux
        pts = [(x + ux * 8.2 + nx * 1.5, y + uy * 8.2 + ny * 1.5), (x + ux * 11.2, y + uy * 11.2),
               (x + ux * 8.2 - nx * 1.5, y + uy * 8.2 - ny * 1.5), (x + ux * 9.0, y + uy * 9.0)]
        mb.prism(ccw(pts), A - 0.1, A + 0.12, "Roof_DB_Blue", 0.0)
    # base escura + pernas de pouso curtas (sonda)
    mb.cyl(4.95, 0.7, (x, y, A + 0.51), m="Metal_DB_Dark", n=28, bevel=0.1)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        ca, sa = math.cos(a), math.sin(a)
        mb.beam((x + ca * 4.35, y + sa * 4.35, A + 1.9), (x + ca * 5.45, y + sa * 5.45, A + 0.35), 0.42, 0.42,
                "Metal_DB_Steel", 0.06)
        mb.cyl(0.55, 0.22, (x + ca * 5.5, y + sa * 5.5, A + 0.27), m="Metal_DB_Dark", n=10, bevel=0.04)
    # tambor branco, anel de luz ciano, janelas redondas (sem porta), faixa azul
    mb.cyl(4.5, 2.5, (x, y, A + 0.86 + 1.25), m="Plaster_DB_White", n=28, bevel=0.1)
    mb.cyl(4.58, 0.26, (x, y, A + 1.28), m="DB_Cyan_Glow", n=28, bevel=0.0)
    for i in range(8):
        a = math.radians(22.5 + 45 * i)
        ca, sa = math.cos(a), math.sin(a)
        rot = (math.pi / 2, 0, a + math.pi / 2)
        mb.cyl(0.66, 0.24, (x + ca * 4.5, y + sa * 4.5, A + 2.3), rot, "Plaster_DB_Navy", 12, bevel=0.0)
        mb.cyl(0.48, 0.3, (x + ca * 4.52, y + sa * 4.52, A + 2.3), rot, "Glass_DB_Blue", 12, bevel=0.0)
    mb.cyl(4.64, 0.42, (x, y, A + 3.2), m="Roof_DB_Blue", n=28, bevel=0.06)
    dome(mb, (x, y), 4.5, A + 3.36, "Plaster_DB_White", n=28, rings=7, squash=0.78)
    ztop = A + 3.36 + 4.5 * 0.78
    # escotilha azul, mastro, farol ciano
    mb.cyl(1.6, 0.5, (x, y, ztop - 0.12), m="Roof_DB_Blue", n=20, bevel=0.08)
    mb.cyl(0.9, 0.3, (x, y, ztop + 0.25), m="Metal_DB_Dark", n=16, bevel=0.05)
    mb.rod((x, y, ztop + 0.3), (x, y, ztop + 3.4), 0.16, "Metal_DB_Steel", 8)
    mb.ico(0.34, (x, y, ztop + 3.55), "DB_Cyan_Glow", 1)
    # sensor lateral fixo (braco curto com lente ciano)
    mb.beam((x + 2.2, y - 1.6, ztop - 0.9), (x + 3.4, y - 2.5, ztop + 0.2), 0.3, 0.3, "Metal_DB_Steel", 0.04)
    mb.cyl(0.35, 0.3, (x + 3.45, y - 2.55, ztop + 0.3), m="DB_Cyan_Glow", n=10, bevel=0.0)
    mb.finish()
    # prato do radar (peca movel, 1 material)
    zd = ztop + 2.3
    vf = MB("VFX_DBMINE_Dish", "12_VFX_HELPERS", rng, detail="near")
    vf.cyl(0.14, 0.9, (x + 0.5, y, zd), (0, math.pi / 2, 0), "Metal_DB_Steel", 6, bevel=0.0)
    vf.cyl(1.25, 0.45, (x + 1.1, y, zd + 0.1), (0, math.pi / 2 - 0.35, 0), "Metal_DB_Steel", 16, r2=0.3, bevel=0.0)
    ob = vf.finish()
    ob["pivot"] = (x, y, zd)
    ob["axis"] = (0.0, 0.0, 1.0)
    ob["rpm"] = 5.0
    ob["note"] = "prato do radar do pod de sondagem: gira em volta do mastro"
    # colisao: so a do db_col (coluna do pod; ver POD_COL e 'requests')
    light("L_DBMine_PodBeacon", "POINT", (x, y, ztop + 4.4), 260, (0.45, 0.85, 1.0), 0.6)


# ------------------------------------------------------------------ 6. promenade (lajes, faixas, medalhoes, pilones)
def promenade(rng):
    mb = MB("DB_Mine_Promenade", COLL, rng, detail="far")
    rin = lambda a: R(a) + 1.25
    rb1 = lambda a: R(a) + 2.45
    rb2 = lambda a: L.prom_r(a) - 1.2
    rmid = lambda a: (rb1(a) + rb2(a)) / 2
    rout = lambda a: L.prom_r(a)
    # base (cor das juntas)
    DL.ring_band(mb, rin, rout, G - 0.3, G + 0.03, "Stone_DB_Block", step=3.0, walls=(False, True))  # +0,03: nao coplanar com o chao
    # faixas de borda (interna e externa) em segmentos de ~15 graus
    for k in range(24):
        a0, a1 = k * 15.0, (k + 1) * 15.0
        g = math.degrees(0.1 / 60.0)
        mb.prism(sector_poly(a0 + g, a1 - g, rin, rb1, 3.0), G - 0.2, G + 0.1, "Stone_DB_Block", 0.0)
        mb.prism(sector_poly(a0 + g, a1 - g, rb2, lambda a: rout(a) - 0.02, 3.0), G - 0.2, G + 0.1, "Stone_DB_Block",
                 0.0)
    # lajes (2 fiadas desencontradas, ~4,2 de comprimento, juntas de 0,22)
    for row, (fa, fb, sh) in enumerate(((rb1, rmid, 0.0), (rmid, rb2, 0.5))):
        rm = 70.0
        n = int(round(2 * math.pi * rm / 4.2))
        for i in range(n):
            a0 = 360.0 * (i + sh) / n
            a1 = 360.0 * (i + 1 + sh) / n
            g = math.degrees(0.11 / rm)
            ra = lambda a, fa=fa: fa(a) + 0.11
            rbb = lambda a, fb=fb: fb(a) - 0.11
            mb.prism(sector_poly(a0 + g, a1 - g, ra, rbb, 6.0), G - 0.2, G + 0.08, "Stone_Paving_DB", 0.0)
    # medalhoes de bussola na cabeca de cada acesso
    for aa, w, k in L.ARENA_ACCESS:
        rr = R(aa) + 4.6
        c = P(aa, rr)
        mb.cyl(2.55, 0.34, (c.x, c.y, G - 0.05), m="Plaster_DB_Navy", n=24, bevel=0.0)
        mb.cyl(2.1, 0.34, (c.x, c.y, G - 0.01), m="Stone_Paving_DB", n=24, bevel=0.0)
        star = []
        for j in range(8):
            t = math.radians(aa) + j * math.pi / 4
            q = 1.85 if j % 2 == 0 else 0.55
            star.append((c.x + q * math.cos(t), c.y + q * math.sin(t)))
        mb.prism(ccw(star), G - 0.05, G + 0.21, "Roof_DB_Blue", 0.0)
        mb.cyl(0.36, 0.3, (c.x, c.y, G + 0.1), m="Plaster_DB_White", n=10, bevel=0.0)
    mb.finish()


PYLONS = [256.0, 284.0, 36.0]


def pylons(mt):
    """pilones-scanner Capsule no lado do promenade (nunca na area de minerio): lente ciano virada para a arena"""
    for a in PYLONS:
        r = R(a) + 2.9
        p = P(a, r)
        yaw = math.radians(a)
        z = G + 0.1
        mt.cyl(1.25, 0.5, (p.x, p.y, z + 0.25), m="Metal_DB_Dark", n=12, bevel=0.06)
        mt.cyl(0.62, 5.2, (p.x, p.y, z + 0.5 + 2.6), m="Plaster_DB_White", n=12, r2=0.5, bevel=0.0)
        mt.cyl(0.7, 0.4, (p.x, p.y, z + 3.3), m="Roof_DB_Blue", n=12, bevel=0.0)
        # cabeca do scanner (disco branco) + aro ciano + lente ciano para a arena + antena
        mt.cyl(1.35, 0.9, (p.x, p.y, z + 6.1), m="Plaster_DB_White", n=16, bevel=0.1)
        mt.cyl(1.42, 0.22, (p.x, p.y, z + 6.1), m="DB_Cyan_Glow", n=16, bevel=0.0)
        mt.cyl(1.1, 0.35, (p.x, p.y, z + 6.72), m="Roof_DB_Blue", n=16, bevel=0.05)
        lx, ly = p.x - math.cos(yaw) * 1.3, p.y - math.sin(yaw) * 1.3
        mt.cyl(0.46, 0.4, (lx, ly, z + 6.1), (math.pi / 2, 0, yaw + math.pi / 2), "DB_Cyan_Glow", 12, bevel=0.0)
        mt.rod((p.x, p.y, z + 6.9), (p.x, p.y, z + 8.4), 0.08, "Metal_DB_Steel", 6)
        mt.ico(0.2, (p.x, p.y, z + 8.5), "DB_Cyan_Glow", 1)
        col_box("DB_MinePylon", (2.1, 2.1, 7.2), (p.x, p.y, z + 3.5), (0, 0, yaw + math.pi / 4))


# ------------------------------------------------------------------ build
def build():
    floor()
    ms = MB("DB_Mine_Stone", COLL, random.Random(2310), detail="near")      # arenito cortado, escadas, lajes
    mr = MB("DB_Mine_Rock", COLL, random.Random(2320), detail="near")       # rocha natural: bordas, mesas
    mt = MB("DB_Mine_Tech", COLL, random.Random(2330), detail="near")       # guarda Capsule, postes, pilones
    south(ms, mt, random.Random(2311))
    east(mr, random.Random(2321))
    north(mr, ms, random.Random(2322))
    west(mr, random.Random(2323))
    stairs(ms, mr, mt, random.Random(2312))
    ramp(ms, mr, random.Random(2313))
    mesas(mr, random.Random(2324))
    pylons(mt)
    ms.finish()
    mr.finish()
    mt.finish()
    promenade(random.Random(2340))
    pod()
    # luz da cabeca da escada S (portal Capsule da arena)
    F, run, w, k = access_frame(270.0)
    q = F.p(run + 0.7, 0, 0)
    light("L_DBMine_TechGate", "POINT", (q.x, q.y, G + 4.2), 140, (0.45, 0.85, 1.0), 0.5)


# ------------------------------------------------------------------ rotas / sondas extras (db_qa)
def _ledge_route(a0, a1, off, z):
    """caminha AO LONGO do patamar N de baixo (prova que os blocos formam piso continuo, degraus <= 2,3)"""
    n = max(2, int(abs(a1 - a0) / 3.0))
    return ([P2(a0 + (a1 - a0) * i / n, R(a0 + (a1 - a0) * i / n) - off) for i in range(n + 1)], z)


def _cheek_probes():
    out = []
    for aa in (270.0, 90.0, 180.0, 222.0, 318.0):
        F, run, w, k = access_frame(aa)
        for s, tag in ((1, "L"), (-1, "R")):
            p = F.p(4.25, 0, 0)
            dx, dy = -math.sin(F.a) * s, math.cos(F.a) * s
            out.append(("MINE_ESCADA%03d_lado_%s" % (int(aa), tag), p.x, p.y, A + 2.4, dx, dy, w / 2 + 1.5))
    return out


EXTRA_ROUTES = {"TERRACO_N_L1_leste": _ledge_route(LEDGE_ROUTE_SPANS[0][0], LEDGE_ROUTE_SPANS[0][1], 3.3, A + 1.3),
                "TERRACO_N_L1_oeste": _ledge_route(LEDGE_ROUTE_SPANS[1][0], LEDGE_ROUTE_SPANS[1][1], 3.3, A + 1.3)}
EXTRA_PROBES = _cheek_probes()
