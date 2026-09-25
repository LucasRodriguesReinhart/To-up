# db_col - COMPARTILHADO E CONGELADO (dono: integracao). Colisao de TUDO que e andavel na Ilha 2, independente do
# visual: chao de cada nivel (poligonos da planta), escadas e rampas (col_ramp), pontes (chegada, saida, satelites),
# ilhota do portao Shadow Garden, pocos, colunas das mesas/rochas e as guardas invisiveis (borda da ilha, borda da
# arena, bordas de terraco com queda > 2,3). Os modulos de detalhe desenham SO o visual destas pecas (escadas com
# db_lib.vis_stairs, guardas com vis_fence/vis_parapet) e criam a colisao SO dos proprios predios/props.
import math
from mathutils import Vector
import db_lib as DL
from db_lib import col_box, col_box2, col_ramp, col_poly, ccw, ribbon_poly
import db_layout as L

A = "DB_Terrain"
GUARD_H = 3.2          # guarda invisivel de terraco (acima do piso de cima)
RIM_H = 9.0            # parede invisivel da borda da ilha


# ------------------------------------------------------------------ escadas / rampas (so colisao)
def stair_col(area, base, ang, width, n, rise, tread, guards=True, guard_h=4.0):
    """a colisao de fm_parts.stairs (rampa pelo meio dos pisos + meia pisada final + banzos) sem a geometria"""
    F = DL.Frame(base[0], base[1], base[2], ang)
    bot = F.p(-tread / 2, 0, 0)
    top = F.p(tread * n - tread / 2, 0, rise * n)
    col_ramp(area, bot, top, width)
    q = F.p(tread * n - tread / 4 + 0.15, 0, rise * n - 0.5)
    col_box(area, (tread / 2 + 0.3, width, 1.0), (q.x, q.y, q.z), F.r())
    if guards:
        k = rise / tread
        H = guard_h
        T = H + 1.5
        off = k * (tread * k / 2 + H) / (1 + k * k)
        for s in (-1, 1):
            y = s * (width / 2 + 0.6)
            xa, xb = -off, tread * n - off
            a = F.p(xa, y, (xa + tread / 2) * k + H)
            b = F.p(xb, y, (xb + tread / 2) * k + H)
            col_ramp(area, a, b, 1.2, thick=T)
    return F.p(tread * n, 0, rise * n)


def stair_list():
    """todas as escadas da planta: (nome, pe (x, y, z), rumo_rad, largura, n, espelho, piso, guardas)"""
    out = []
    # escadaria da chegada: ponte (DECK) -> praca (GROUND)
    out.append(("Entry", (0.0, L.BRIDGE_Y1, L.DECK), math.pi / 2, L.ENTRY_STAIR_W,
                L.ENTRY_STAIR_N, (L.GROUND - L.DECK) / L.ENTRY_STAIR_N, L.ENTRY_STAIR_TREAD, True))
    # acessos da arena (escadas; a rampa leste e separada)
    for ang, w, kind in L.ARENA_ACCESS:
        if kind != "stair":
            continue
        foot, top, d = L.access_frame(ang)
        a_up = math.atan2(-d[1], -d[0])            # sobe para fora (da arena para o promenade)
        out.append(("Arena%03d" % int(ang), (foot[0], foot[1], L.ARENA), a_up, w, 5,
                    (L.GROUND - L.ARENA) / 5, L.TREAD, False))
    # vila: escada central + laterais (promenade GROUND -> HUB), sobem para o norte ate a frente do terraco
    for i, (x, y, w) in enumerate([L.HUB_STAIR] + list(L.HUB_SIDE_STAIRS)):
        ye = hub_front_y(x)
        n = 5
        out.append(("Hub%d" % i, (x, ye - n * L.TREAD, L.GROUND), math.pi / 2, w, n,
                    (L.HUB - L.GROUND) / n, L.TREAD, True))
    # Capsule: HUB -> CAP (8 x 0,75)
    x, y, w = L.CAP_STAIR
    n = L.CAP_STAIR_N
    out.append(("Cap", (x, y - n * L.TREAD, L.HUB), math.pi / 2, w, n, (L.CAP - L.HUB) / n, L.TREAD,
                True))
    # summon: GROUND -> SUM (8 x 0,75) subindo para oeste
    x, y, w = L.SUMMON_STAIR
    n = L.SUMMON_STAIR_N
    out.append(("Summon", (x, y, L.GROUND), math.pi, w, n, (L.SUM - L.GROUND) / n, L.TREAD, True))
    # saida: GROUND -> EXIT_Z (5 x 0,8)
    fx, fy, fdeg, fw = L.EXIT_STAIR
    a = math.radians(fdeg)
    out.append(("Exit", (fx, fy, L.GROUND), a, fw, 5,
                (L.EXIT_Z - L.GROUND) / 5, L.TREAD, True))
    return out


def hub_front_y(x):
    """y da frente do terraco da vila (menor y do contorno HUB_POLY na vertical x)"""
    best = None
    P = L.HUB_POLY
    n = len(P)
    for i in range(n):
        (x0, y0), (x1, y1) = P[i], P[(i + 1) % n]
        if (x0 - x) * (x1 - x) <= 0 and x0 != x1:
            y = y0 + (x - x0) * (y1 - y0) / (x1 - x0)
            best = y if best is None else min(best, y)
    return best


def ramp_east():
    """rampa natural leste da arena: 4 de subida em 18 (acesso suave)"""
    for ang, w, kind in L.ARENA_ACCESS:
        if kind == "ramp":
            foot, top, d = L.access_frame(ang)
            col_ramp(A, (foot[0], foot[1], L.ARENA), (top[0] - d[0] * 0.8, top[1] - d[1] * 0.8, L.GROUND), w)
            q = Vector((top[0] - d[0] * 0.2, top[1] - d[1] * 0.2, L.GROUND - 0.5))
            col_box(A, (1.6, w, 1.0), q, (0, 0, math.atan2(d[1], d[0])))


# ------------------------------------------------------------------ recortes do chao (pocos, canais, escadaria)
def entry_notch():
    """recorte do chao GROUND onde fica a escadaria da chegada (ela desce ate a ponte) - o plato ladeia a escada"""
    hw = L.ENTRY_STAIR_W / 2 + 1.4
    # vai 7 alem do topo: as faixas de 6 que cruzam a linha do topo nao cobrem a escada (a praca tem caixa propria)
    return [(-hw, L.BRIDGE_Y1 - 14.0), (hw, L.BRIDGE_Y1 - 14.0), (hw, L.ENTRY_STAIR_Y1 + 7.0),
            (-hw, L.ENTRY_STAIR_Y1 + 7.0)]


def water_polys():
    """pocos e canais (colisao no leito, 1,6 abaixo do piso): SW e SE no chao, NW na vila"""
    out = []
    for (px, py, pr), fall in ((L.POOL_SW, L.FALL_SW), (L.POOL_SE, L.FALL_SE)):
        out.append(("g", [(px + pr * math.cos(t * math.pi / 10), py + pr * math.sin(t * math.pi / 10)) for t in range(20)]))
        out.append(("g", ribbon_poly([(px, py), fall], 2.4)))
    px, py, pr = L.POOL_NW
    out.append(("h", [(px + pr * math.cos(t * math.pi / 10), py + pr * math.sin(t * math.pi / 10)) for t in range(20)]))
    return out


# ------------------------------------------------------------------ guardas
def _opening(x, y):
    """pontos da borda da ilha onde a parede invisivel fica aberta: pontes (chegada, saida, satelites)"""
    if y < L.BRIDGE_Y1 + 2.0 and abs(x) < L.ENTRY_STAIR_W / 2 + 1.0:
        return True
    ux, uy = L.exit_dir()
    sx, sy = L.EXIT_START
    t = (x - sx) * ux + (y - sy) * uy
    d = abs(-(x - sx) * uy + (y - sy) * ux)
    if -12.0 <= t <= L.EXIT_BRIDGE_LEN and d < L.EXIT_W / 2 + 0.6:
        return True
    for k, (a0, a1) in L.SAT_BRIDGES.items():
        dd, tt = L.seg_dist(x, y, a0[0], a0[1], a1[0], a1[1])
        if dd < L.SAT_BRIDGE_W / 2 + 0.6:
            return True
    return False


def _runs(pts, keep, step=1.0, closed=True):
    """divide a polilinha em trechos continuos onde keep(p) e verdadeiro"""
    runs, run = [], []
    n = len(pts)
    for i in range(n if closed else n - 1):
        a = Vector((*pts[i], 0))
        b = Vector((*pts[(i + 1) % n], 0))
        d = b - a
        ns = max(1, int(d.length / step))
        for k in range(ns):
            p = a + d * (k / ns)
            if keep(p.x, p.y):
                run.append(p)
            else:
                if len(run) > 1:
                    runs.append(run)
                run = []
    if len(run) > 1:
        runs.append(run)
    return runs


def _wall(area, run, z0, h, th=1.2, chord=10, inward=None, off=0.0):
    """caixas ao longo de um trecho (cordas de ate ~chord studs). inward=(cx, cy): desloca a caixa 'off' para o lado
    desse ponto (parede com a face de fora na linha do trecho)"""
    i = 0
    while i < len(run) - 1:
        j = min(len(run) - 1, i + chord)
        p0, p1 = run[i], run[j]
        mid = (p0 + p1) / 2
        d = p1 - p0
        if d.length > 0.3:
            c = Vector(mid)
            if inward is not None and off:
                nrm = Vector((-d.y, d.x, 0)).normalized()
                if (Vector((inward[0], inward[1], 0)) - mid).dot(nrm) < 0:
                    nrm = -nrm
                c = mid + nrm * off
            col_box(area, (d.length + 0.8, th, h), (c.x, c.y, z0 + h / 2), (0, 0, math.atan2(d.y, d.x)))
        i = j


def rim_guard():
    pts = DL.rim()

    def keep(x, y):
        return not _opening(x, y)
    for run in _runs(pts, keep):
        mid = run[len(run) // 2]
        inward = Vector((-mid.x, -mid.y + 20.0, 0)).normalized() * 6.0
        z = L.zone_of(mid.x + inward.x, mid.y + inward.y)
        _wall("DB_Rim", run, z - 1.0, RIM_H + 1.0, th=4.6, chord=12, inward=(0.0, 20.0), off=2.3)


def arena_guard():
    """guarda da borda da arena (no lado do promenade), aberta nos 6 acessos"""
    def keep(x, y):
        ang = math.degrees(math.atan2(y, x))
        for aa, w, kind in L.ARENA_ACCESS:
            r = L.arena_r(aa)
            half = math.degrees((w / 2 + 0.5) / r)
            if abs((ang - aa + 180.0) % 360.0 - 180.0) <= half:
                return False
        return True
    pts = [(p[0] * 1.0, p[1] * 1.0) for p in L.polar_poly(lambda a: L.arena_r(a) + 0.7, 2.0)]
    for run in _runs(pts, keep):
        _wall("DB_ArenaGuard", run, L.GROUND - 0.5, GUARD_H + 0.5, th=1.0, chord=8)


def terrace_guards():
    """bordas de terraco com queda > 2,3 para o nivel de fora (exceto escadas e onde encosta outro piso igual)"""
    polys = [("Hub", DL.hub_poly(), L.HUB), ("Cap", DL.cap_poly(), L.CAP), ("Sum", DL.summon_poly(), L.SUM)]
    for i, rp in enumerate(DL.exit_shelf_polys()):
        polys.append(("Exit%d" % i, rp, L.EXIT_Z))
    stairs = stair_list()

    def near_stair_top(x, y, z_top):
        for nm, base, ang, w, n, rise, tread, g in stairs:
            if abs(base[2] + rise * n - z_top) > 0.3:
                continue
            tx = base[0] + math.cos(ang) * tread * n
            ty = base[1] + math.sin(ang) * tread * n
            # ao longo da borda: dentro da largura da escada (+folga)
            dx, dy = x - tx, y - ty
            along = abs(-dx * math.sin(ang) + dy * math.cos(ang))
            depth = abs(dx * math.cos(ang) + dy * math.sin(ang))
            if along < w / 2 + 0.8 and depth < 3.0:
                return True
        return False

    for nm, poly, z in polys:
        pts = ccw(poly)

        def keep(x, y, pts=pts, z=z):
            # normal para fora aproximada: do centroide para o ponto
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            d = Vector((x - cx, y - cy, 0))
            if d.length < 1e-3:
                return False
            d.normalize()
            ox, oy = x + d.x * 1.6, y + d.y * 1.6
            if not L.point_in_poly(ox, oy, L.ISLAND_RIM):
                return False                       # a borda da ilha ja tem a parede do contorno
            zo = L.zone_of(ox, oy)
            if z - zo <= 2.3:
                return False                       # encosta em piso igual ou mais alto
            if _opening(ox, oy):
                return False
            return not near_stair_top(x, y, z)
        for run in _runs(pts, keep, step=1.0):
            _wall("DB_TerraceGuard", run, z - 0.5, GUARD_H + 0.5, th=1.0, chord=10)


# ------------------------------------------------------------------ pontes, ilhota, satelites
def bridges():
    hw = L.DECK_W / 2
    # chegada: tabuleiro + guardas laterais (a ponte encosta na cabeceira da Ilha 1 em y = PREV_Y)
    col_box2("DB_Bridge", (-hw, L.BRIDGE_Y0, L.DECK - 2.0), (hw, L.BRIDGE_Y1 + 0.6, L.DECK))
    for s in (-1, 1):
        xa, xb = sorted((s * hw, s * (hw + 1.2)))
        col_box2("DB_Bridge", (xa, L.BRIDGE_Y0, L.DECK - 0.5), (xb, L.BRIDGE_Y1, L.DECK + GUARD_H + 0.8))
    # saida: ponte (EXIT_Z) + ilhota + guardas; o portao SG tem colisao propria (il_gate_sg)
    ux, uy = L.exit_dir()
    a = math.atan2(uy, ux)
    Ln = L.EXIT_BRIDGE_LEN
    c = L.exit_point(Ln / 2)
    col_box("DB_ExitBridge", (Ln + 4.0, L.EXIT_W, 2.0), (c[0], c[1], L.EXIT_Z - 1.0), (0, 0, a))
    for s in (-1, 1):
        q = (c[0] - uy * s * (L.EXIT_W / 2 + 0.6), c[1] + ux * s * (L.EXIT_W / 2 + 0.6))
        col_box("DB_ExitBridge", (Ln - 2.0, 1.2, GUARD_H + 1.3), (q[0], q[1], L.EXIT_Z + (GUARD_H + 1.3) / 2 - 0.5),
                (0, 0, a))
    ic = L.islet_center()
    isl = [(ic[0] + L.GATE_ISLET_R * math.cos(t * math.pi / 12), ic[1] + L.GATE_ISLET_R * math.sin(t * math.pi / 12))
           for t in range(24)]
    col_poly("DB_Islet", isl, L.EXIT_Z - 3.0, L.EXIT_Z, 3.0, mode="union")
    # plataforma da ancora (retangulo DECK_W x 10 antes da ancora) - encosta no fim da ilhota
    ap = L.anchor_pos()
    pc = (ap[0] - ux * 5.0, ap[1] - uy * 5.0)
    col_box("DB_Islet", (10.0, L.DECK_W, 2.0), (pc[0], pc[1], L.EXIT_Z - 1.0), (0, 0, a))
    # guarda da ilhota (aberta na ponte e no corredor da ancora)
    bs = L.exit_point(L.EXIT_BRIDGE_LEN)

    def keep(x, y):
        t = (x - bs[0]) * ux + (y - bs[1]) * uy
        d = abs(-(x - bs[0]) * uy + (y - bs[1]) * ux)
        if d < L.EXIT_W / 2 + 0.6 and (t < 3.0 or t > L.ANCHOR_OFF - 14.0):
            return False
        return True
    for run in _runs(ccw(isl), keep):
        _wall("DB_Islet", run, L.EXIT_Z - 0.5, GUARD_H + 0.5)
    # laterais da plataforma da ancora
    for s in (-1, 1):
        q = (pc[0] - uy * s * (L.DECK_W / 2 + 0.6), pc[1] + ux * s * (L.DECK_W / 2 + 0.6))
        col_box("DB_Islet", (10.0, 1.2, GUARD_H + 1.0), (q[0], q[1], L.EXIT_Z + (GUARD_H + 1.0) / 2 - 0.5), (0, 0, a))
    # guarda PROVISORIA da ancora (sai quando a Ilha 3 encosta): parede invisivel na ponta
    g = col_box("DBAnchorGuard", (1.2, L.DECK_W + 2.0, 9.0), (ap[0] + ux * 0.6, ap[1] + uy * 0.6, L.EXIT_Z + 4.0),
                (0, 0, a))
    g["next_island_guard"] = True
    # satelites andaveis: ponte curta + plataforma redonda + guardas
    for x, y, r, kind, walk in L.TOWER_SITES:
        if not walk:
            continue
        a0, a1 = L.SAT_BRIDGES[kind]
        d = Vector((a1[0] - a0[0], a1[1] - a0[1], 0))
        ang = math.atan2(d.y, d.x)
        mid = ((a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2)
        col_box("DB_Sat", (d.length + 3.0, L.SAT_BRIDGE_W, 2.0), (mid[0], mid[1], L.GROUND - 1.0), (0, 0, ang))
        for s in (-1, 1):
            q = (mid[0] - math.sin(ang) * s * (L.SAT_BRIDGE_W / 2 + 0.6), mid[1] + math.cos(ang) * s * (L.SAT_BRIDGE_W / 2 + 0.6))
            col_box("DB_Sat", (d.length, 1.2, GUARD_H + 1.0), (q[0], q[1], L.GROUND + (GUARD_H + 1.0) / 2 - 0.5),
                    (0, 0, ang))
        pad = [(x + r * math.cos(t * math.pi / 8), y + r * math.sin(t * math.pi / 8)) for t in range(16)]
        col_poly("DB_Sat", pad, L.GROUND - 3.0, L.GROUND, 3.0, mode="union")

        def keep_pad(px, py, a1=a1, x=x, y=y):
            return math.hypot(px - a1[0], py - a1[1]) > L.SAT_BRIDGE_W / 2 + 1.2
        for run in _runs(ccw(pad), keep_pad):
            _wall("DB_Sat", run, L.GROUND - 0.5, GUARD_H + 0.5)


# ------------------------------------------------------------------ rochedos: colunas octogonais
def octo(area, x, y, r, z0, z1):
    s = r * 1.66                      # lado do quadrado ~ circulo inscrito
    for a in (0.0, math.pi / 4):
        col_box(area, (s, s, z1 - z0), (x, y, (z0 + z1) / 2), (0, 0, a))


def rocks():
    for x, y, r, top, kind in L.MESAS:
        # so a parte que pode encostar em quem anda (do nivel mais baixo ao redor ate 14 acima): o resto e visual
        if not L.point_in_poly(x, y, L.ISLAND_RIM) and min(
                math.hypot(x - px, y - py) for px, py in L.ISLAND_RIM) > r + 1.0:
            continue
        z0 = min(L.zone_of(x + r * math.cos(t), y + r * math.sin(t)) for t in (0, 1.57, 3.14, 4.71)) - 2.0
        octo("DB_Mesa", x, y, r * 0.92, z0, max(z0 + 16.0, min(top, z0 + 40.0)))
    for x, y, r, h in L.ARENA_ROCKS:
        octo("DB_ArenaRock", x, y, r * 0.9, L.ARENA - 1.0, L.ARENA + h)
    for x, y, r, h in L.PLATEAU_ROCKS:
        z = L.zone_of(x, y)
        octo("DB_PlateauRock", x, y, r * 0.9, z - 1.0, z + h)
    x, y, r = L.CORE_POD
    octo("DB_ArenaRock", x, y, r * 0.95, L.ARENA - 1.0, L.ARENA + 5.0)


# ------------------------------------------------------------------ chao
def strips(area, poly, z0, z1, step, mode="inter", minus=(), cut="inter"):
    """colisao de poligono em faixas ao longo de y (como il_lib.col_poly), mas o RECORTE (minus) usa a intersecao
    das amostras: quando a borda recortada e inclinada, o chao sobra um pouco POR CIMA do recorte (mesma altura ou
    embaixo de outra colisao) em vez de abrir buraco."""
    ys = [p[1] for p in poly]
    y = min(ys)
    n = 0
    while y < max(ys) - 1e-6:
        ya, yb = y, min(y + step, max(ys))
        samples = [ya + 0.05, (ya + yb) / 2, yb - 0.05]
        ivs = None
        for sm in samples:
            iv = DL.x_intervals(poly, sm)
            ivs = iv if ivs is None else (DL.IL._union(ivs, iv) if mode == "union" else DL.IL._inter(ivs, iv))
        if minus and ivs:
            cuts = None
            for sm in samples:
                c = []
                for mp in minus:
                    c += DL.x_intervals(mp, sm)
                c = DL.IL._union([], c)
                cuts = c if cuts is None else (DL.IL._union(cuts, c) if cut == "union" else DL.IL._inter(cuts, c))
            ivs = DL.IL._minus(ivs, cuts or [])
        for x0, x1 in ivs or []:
            if x1 - x0 > 0.3:
                col_box2(area, (x0, ya, z0), (x1, yb, z1))
                n += 1
        y = yb
    return n


def edge_fill(area, poly, z0, z1, w=3.2):
    """caixas finas por dentro de cada aresta: as faixas 'inter' aparam a borda inclinada ate 1 faixa; isto devolve o
    piso ate a aresta exata (topo das escadas que chegam na borda, encontro com outro piso)"""
    pts = ccw(poly)
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.5:
            continue
        nx, ny = -dy / ln, dx / ln                      # para dentro (poligono anti-horario)
        mid = ((a[0] + b[0]) / 2 + nx * w / 2, (a[1] + b[1]) / 2 + ny * w / 2)
        col_box(area, (ln + 0.4, w, z1 - z0), (mid[0], mid[1], (z0 + z1) / 2), (0, 0, math.atan2(dy, dx)))


def ribbon_col(area, pts, hw, z0, z1, ext0=1.5, ext1=1.5):
    """fita (trilha diagonal) exata: uma caixa orientada por trecho + juntas octogonais"""
    n = len(pts)
    for i in range(n - 1):
        a, b = Vector((pts[i][0], pts[i][1], 0)), Vector((pts[i + 1][0], pts[i + 1][1], 0))
        d = b - a
        ln = d.length
        u = d / ln
        a2 = a - u * (ext0 if i == 0 else 0.0)
        b2 = b + u * (ext1 if i == n - 2 else 0.0)
        c = (a2 + b2) / 2
        col_box(area, ((b2 - a2).length, 2 * hw, z1 - z0), (c.x, c.y, (z0 + z1) / 2), (0, 0, math.atan2(u.y, u.x)))
    for p in pts[1:-1]:
        DL.octo_col(area, p[0], p[1], hw * 0.98, z0, z1)


def arena_band(area, z0, z1, extra=4.0, step=5.0):
    """anel de caixas RADIAIS da borda da arena ate alem do promenade: a borda curva da bacia fica exata (o topo das
    escadas/rampa da arena encosta sem fresta)"""
    k = int(round(360.0 / step))
    for i in range(k):
        a0 = i * step
        a1 = a0 + step
        am = (a0 + a1) / 2
        rin = max(L.arena_r(a0), L.arena_r(a1), L.arena_r(am))
        rout = L.prom_r(am) + extra
        rm = (rin + rout) / 2
        w = 2 * rout * math.tan(math.radians(step / 2)) + 0.4
        col_box(area, (rout - rin, w, z1 - z0), (rm * math.cos(math.radians(am)), rm * math.sin(math.radians(am)),
                                                  (z0 + z1) / 2), (0, 0, math.radians(am)))


def ngon_col(area, cx, cy, n, R, z0, z1, rot0=0.0):
    """poligono regular CHEIO (vertices em rot0 + k*360/n, raio R): n/2 faixas pelo centro, cada uma com o
    comprimento do diametro interno (2*apotema) e a largura de um lado, giradas pela normal de cada par de faces.
    A uniao e exatamente o n-gono (sem fresta nas pontas como as faixas 'inter', sem sobra como as 'union')."""
    a = R * math.cos(math.pi / n)
    w = 2.0 * a * math.tan(math.pi / n) + 0.05
    for k in range(n // 2):
        ang = math.radians(rot0) + math.pi / n + k * 2.0 * math.pi / n
        col_box(area, (2.0 * a, w, z1 - z0), (cx, cy, (z0 + z1) / 2), (0, 0, ang))


def summon_col_poly():
    cx, cy = L.SUMMON_C
    return [(cx + L.SUMMON_R * math.cos(math.radians(a)), cy + L.SUMMON_R * math.sin(math.radians(a)))
            for a in range(0, 360, 15)]


def floors():
    wp = water_polys()
    g_cut = [p for k, p in wp if k == "g"]
    h_cut = [p for k, p in wp if k == "h"]
    band_out = L.polar_poly(lambda a: L.prom_r(a) + 3.4, 3.0)
    # chao GROUND: faixa radial em volta da arena + o resto do contorno (menos o disco da faixa, a escadaria e a agua)
    arena_band(A, L.GROUND - 8.0, L.GROUND)
    # praca da entrada: caixa exata (o recorte da escadaria passa 7 do topo; a praca devolve o piso ate o topo)
    hw = L.ENTRY_STAIR_W / 2 + 1.6
    col_box2(A, (-hw, L.ENTRY_STAIR_Y1, L.GROUND - 8.0), (hw, L.ENTRY_STAIR_Y1 + 8.0, L.GROUND))
    strips(A, DL.rim(), L.GROUND - 8.0, L.GROUND, 6.0, mode="inter", minus=[band_out, entry_notch()] + g_cut)
    for p in g_cut:
        strips("DB_WaterBed", p, L.GROUND - 6.0, L.GROUND - 1.6, 4.0, mode="union")
    # arena (bacia rasa)
    strips(A, DL.arena(), L.ARENA - 6.0, L.ARENA, 5.0, mode="union")
    # terracos (assentados no GROUND): faixas + preenchimento das arestas
    strips(A, DL.hub_poly(), L.GROUND - 1.0, L.HUB, 4.0, mode="inter", minus=h_cut)
    edge_fill(A, DL.hub_poly(), L.GROUND - 1.0, L.HUB)
    for p in h_cut:
        strips("DB_WaterBed", p, L.GROUND, L.HUB - 1.6, 4.0, mode="union")
    strips(A, DL.cap_poly(), L.HUB - 1.0, L.CAP, 4.0, mode="inter")
    edge_fill(A, DL.cap_poly(), L.HUB - 1.0, L.CAP)
    # plato do summon: 24-gono cheio (as faixas 'inter' + edge_fill deixavam frestas de 0,2-0,5 perto dos polos)
    ngon_col(A, L.SUMMON_C[0], L.SUMMON_C[1], 24, L.SUMMON_R, L.GROUND - 1.0, L.SUM)
    # prateleira da saida e ligacao com a vila: fitas exatas
    ribbon_col(A, L.EXIT_PATH, L.EXIT_PATH_HW, L.GROUND - 1.0, L.EXIT_Z, ext0=0.4, ext1=2.5)
    ribbon_col(A, L.HUB_EXIT_LINK, L.HUB_EXIT_LINK_HW, L.GROUND - 1.0, L.EXIT_Z, ext0=4.0, ext1=4.0)


def terrain_col():
    floors()
    for nm, base, ang, w, n, rise, tread, g in stair_list():
        stair_col("DB_Stair" + nm, base, ang, w, n, rise, tread, guards=g)
    ramp_east()
    bridges()
    rocks()
    rim_guard()
    arena_guard()
    terrace_guards()
