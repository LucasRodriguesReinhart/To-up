# fm_terrain_ground - chao do vale e do terraco com desgaste e variacao (chega ao Roblox: cada mancha e malha/cor
# propria, nao ruido de shader).
#   TER_Floor_Base  : laje de terra (Dirt) em z4.0 sob tudo (aparece nos cortes do gramado: trilho, bordas)
#   TER_Floor_Grass : gramado elevado a z4.3 (a colisao do piso esta em 4.35: os pes nao flutuam mais), recortado
#                     sob o calcamento, a praca, os patios e o trilho; manchas de 20-40 studs (Voronoi + ruido)
#                     alternando Grass / Grass_B / Grass_Dry; terra gasta (Dirt, z4.22) nos aventais das portas,
#                     na estacao de carga, na boca da mina, ao lado do trilho, nas curvas internas dos caminhos e
#                     na trilha do galpao; ondulacoes 0.3-1.2 e afloramentos baixos so fora das rotas (colisao
#                     continua plana); grama invadindo a borda do calcamento.
#   Terraco dos portais: o mesmo gramado em manchas (z29.95) sobre o enchimento de pedra (sem faces coplanares).
import math, random
from mathutils import Vector, noise
from mathutils.geometry import delaunay_2d_cdt
import fm_lib
from fm_lib import MB, point_in_poly, resample
import fm_layout as L

fm_lib.MATS.setdefault("Grass_Dry", (fm_lib.S(134, 146, 70), 0.9, 0.0, 0, None, 0.16))

Z_LAWN = L.FLOOR + 0.3
Z_DIRT = L.FLOOR + 0.22
Z_BASE = L.FLOOR


# ------------------------------------------------------------------ geometria 2D
def _area(poly):
    return 0.5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                     for i in range(len(poly)))


def ccw(poly):
    return list(poly) if _area(poly) > 0 else list(reversed(poly))


def clip_half(poly, px, py, nx, ny):
    """mantem os pontos com (p - (px,py)).(nx,ny) <= 0 (Sutherland-Hodgman, 1 semiplano)"""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        da = (a[0] - px) * nx + (a[1] - py) * ny
        db = (b[0] - px) * nx + (b[1] - py) * ny
        if da <= 0:
            out.append(a)
        if (da <= 0) != (db <= 0):
            t = da / (da - db)
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def voronoi(x0, y0, x1, y1, spacing, rng):
    """celulas de Voronoi de uma grade tremida (convexas, cobrem o retangulo)"""
    seeds = []
    nx, ny = int((x1 - x0) / spacing) + 2, int((y1 - y0) / spacing) + 2
    for i in range(-1, nx + 1):
        for j in range(-1, ny + 1):
            seeds.append((x0 + (i + 0.5 + rng.uniform(-0.42, 0.42)) * spacing,
                          y0 + (j + 0.5 + rng.uniform(-0.42, 0.42)) * spacing))
    cells = []
    R = spacing * 2.2
    for s in seeds:
        poly = [(s[0] - R, s[1] - R), (s[0] + R, s[1] - R), (s[0] + R, s[1] + R), (s[0] - R, s[1] + R)]
        for q in seeds:
            if q is s:
                continue
            dx, dy = q[0] - s[0], q[1] - s[1]
            if dx * dx + dy * dy > (2.4 * spacing) ** 2:
                continue
            poly = clip_half(poly, (s[0] + q[0]) / 2, (s[1] + q[1]) / 2, dx, dy)
            if len(poly) < 3:
                break
        for (px, py, nx_, ny_) in ((x0, 0, -1, 0), (x1, 0, 1, 0), (0, y0, 0, -1), (0, y1, 0, 1)):
            if len(poly) >= 3:
                poly = clip_half(poly, px, py, nx_, ny_)
        if len(poly) >= 3 and abs(_area(poly)) > 1.0:
            cells.append((s, ccw(poly)))
    return cells


def blob(cx, cy, rx, ry, ang, rng, n=11, jag=0.22):
    """mancha irregular (elipse com raio ruidoso)"""
    ca, sa = math.cos(ang), math.sin(ang)
    ph = rng.uniform(0, 10)
    out = []
    for i in range(n):
        t = math.tau * i / n
        k = 1.0 + jag * (0.6 * math.sin(3 * t + ph) + 0.4 * rng.uniform(-1, 1))
        x, y = math.cos(t) * rx * k, math.sin(t) * ry * k
        out.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return ccw(out)


def ribbon(pts, w):
    """faixa de largura w ao longo da polilinha (mesma regra do fm_buildings)"""
    pts = [Vector((p[0], p[1], 0)) for p in pts]
    left, right = [], []
    for i, p in enumerate(pts):
        j = min(i + 1, len(pts) - 1)
        k = max(i - 1, 0)
        t = (pts[j] - pts[k]).normalized()
        s = Vector((-t.y, t.x, 0))
        left.append(p + s * w / 2)
        right.append(p - s * w / 2)
    return ccw([(p.x, p.y) for p in left + list(reversed(right))])


def seg_dist(px, py, a, b):
    ax, ay = a[0], a[1]
    dx, dy = b[0] - ax, b[1] - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy + 1e-9)))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))


def poly_dist(px, py, pts):
    return min(seg_dist(px, py, a, b) for a, b in zip(pts, pts[1:])) if len(pts) > 1 else 1e9


def patches(bbox, n_b, n_dry, rng):
    """manchas organicas de 20-40 studs sobre o gramado base: Grass (fundo) + Grass_B (mais escura) + Grass_Dry
    (mais clara/seca) por cima; devolve (celulas, materiais) no formato do _lawn"""
    x0, y0, x1, y1 = bbox
    cells = [((x0, y0), [(x0 - 5, y0 - 5), (x1 + 5, y0 - 5), (x1 + 5, y1 + 5), (x0 - 5, y1 + 5)])]
    mats = ["Grass"]
    for m, n, (r0, r1) in (("Grass_B", n_b, (10.0, 20.0)), ("Grass_Dry", n_dry, (8.0, 15.0))):
        for i in range(n):
            cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
            rx = rng.uniform(r0, r1)
            cells.append(((cx, cy), blob(cx, cy, rx, rx * rng.uniform(0.55, 0.9), rng.uniform(0, math.pi), rng,
                                         n=14, jag=0.28)))
            mats.append(m)
    return cells, mats


# ------------------------------------------------------------------ o que ha no vale (planta travada + modulos)
def _paths():
    import fm_buildings
    out = []
    for name, (pts, w) in fm_buildings.PATHS.items():
        pts2 = []
        for a, b in zip(pts, pts[1:]):
            pts2 += [(p.x, p.y) for p in resample([Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))], 3.0)[:-1]]
        pts2.append((pts[-1][0], pts[-1][1]))
        out.append((name, pts2, w))
    return out


def _rail_valley():
    """trecho do trilho no vale (fora do tunel)"""
    import fm_mine
    pts = fm_mine.rail_path(fm_mine.tunnel_frame())
    fine = resample(pts, 2.0)
    mx, my = L.MINE_MOUTH
    dx, dy = math.cos(L.MINE_DIR), math.sin(L.MINE_DIR)
    return [(p.x, p.y) for p in fine if (p.x - mx) * dx + (p.y - my) * dy < 2.0]


def _cabins():
    """(porta, direcao para fora, frame) de cada cabana"""
    import fm_buildings
    from fm_parts import Frame
    out = []
    for name, spec in fm_buildings.CABINS.items():
        cx, cy, ang = spec["pos"]
        F = Frame(cx, cy, 0.0, math.radians(ang))
        door = F.p(0, -spec["d"] / 2)
        out_d = F.p(0, -1) - F.p(0, 0)
        out.append((name, (cx, cy), (door.x, door.y), (out_d.x, out_d.y), F.a, max(spec["w"], spec["d"])))
    return out


BUILD_RECTS = [(-36, 2, 36, 42), (-16, -18, 16, 4), (L.SHOP[0] - 2, L.SHOP[1] - 2, L.SHOP[2] + 2, L.SHOP[3] + 2),
               (L.MILL[0] - 3, L.MILL[1] - 3, L.MILL[2] + 3, L.MILL[3] + 3), (50, 44, 70, 64),
               (102, -42, 122, -24), (L.WHEEL_C[0] - 12, L.WHEEL_C[1] - 12, L.WHEEL_C[0] + 12, L.WHEEL_C[1] + 12)]


class Valley:
    """consultas de 'area livre' para ondulacoes, afloramentos e talude (fora de rotas, construcoes e trilho)"""

    def __init__(self):
        self.paths = _paths()
        self.rail = _rail_valley()
        self.cabins = _cabins()

    def free(self, x, y, margin=3.0):
        if not (point_in_poly(x, y, L.FLOOR_W) or point_in_poly(x, y, L.FLOOR_E)):
            return False
        if math.hypot(x - L.PLAZA_C[0], y - (-30.0)) < 27 + margin:
            return False
        for name, pts, w in self.paths:
            if poly_dist(x, y, pts) < w / 2 + margin:
                return False
        if self.rail and poly_dist(x, y, self.rail) < 4.5 + margin:
            return False
        for (x0, y0, x1, y1) in BUILD_RECTS:
            if x0 - margin < x < x1 + margin and y0 - margin < y < y1 + margin:
                return False
        for (_, c, door, od, a, sz) in self.cabins:
            if math.hypot(x - c[0], y - c[1]) < sz * 0.75 + margin:
                return False
            if math.hypot(x - door[0] - od[0] * 3, y - door[1] - od[1] * 3) < 5 + margin:
                return False
        for px in L.PORTAL_X:
            if abs(x - px) < 11 + margin and 30 < y < 64:
                return False
        if abs(x) < 13 + margin and y < -50:
            return False     # avenida / escadaria
        # boca da mina e estacao de carga
        if math.hypot(x - L.MINE_MOUTH[0], y - L.MINE_MOUTH[1]) < 12 + margin:
            return False
        if math.hypot(x + 54, y + 8) < 11 + margin:
            return False
        if x > L.RIVER_X[0] - 6 - margin and x < L.RIVER_X[1] + 6 + margin:
            return False     # rio e margens (cercas)
        return True


# ------------------------------------------------------------------ montagem do gramado (CDT)
def _lawn(name, C, region_polys, cells, dirt_polys, holes, z_lawn, z_dirt, z_skirt, rng, mats_of_cell):
    """gramado em manchas: arranjo 2D (CDT) de regioes x celulas x terra x furos; cada face vira grama (material da
    celula) em z_lawn, terra em z_dirt, ou nada (furo). Saia vertical nas bordas ate z_skirt."""
    verts, faces = [], []
    kinds = []

    def add(poly, kind):
        base = len(verts)
        for p in poly:
            verts.append(Vector((p[0], p[1])))
        faces.append(list(range(base, base + len(poly))))
        kinds.append(kind)
    for p in region_polys:
        add(ccw(p), ("R", None))
    for k, (s, p) in enumerate(cells):
        add(p, ("C", k))
    for p in dirt_polys:
        add(ccw(p), ("D", None))
    for p in holes:
        add(ccw(p), ("H", None))
    vs, es, fs, ov, oe, of = delaunay_2d_cdt(verts, [], faces, 4, 1e-4, True)
    mb = MB(name, C, rng)
    level_v = {}

    def V(i, z):
        key = (i, round(z, 3))
        v = level_v.get(key)
        if v is None:
            v = mb.bm.verts.new((vs[i].x, vs[i].y, z))
            level_v[key] = v
        return v
    groups = {}       # material -> [ (face_vert_ids, z) ]
    for f, o in zip(fs, of):
        ks = [kinds[i] for i in o]
        if not any(k[0] == "R" for k in ks) or any(k[0] == "H" for k in ks):
            continue
        cell = max((k[1] for k in ks if k[0] == "C"), default=None)     # manchas posteriores por cima
        if any(k[0] == "D" for k in ks):
            m, z = "Dirt", z_dirt
        else:
            m, z = (mats_of_cell[cell] if cell is not None else "Grass"), z_lawn
        groups.setdefault((m, z), []).append(f)
    # arestas por nivel (para decidir onde vai saia)
    edge_level = {}
    for (m, z), fl in groups.items():
        for f in fl:
            for a, b in zip(f, f[1:] + f[:1]):
                e = (min(a, b), max(a, b))
                edge_level.setdefault(e, []).append(z)
    for (m, z), fl in groups.items():
        made = []
        for f in fl:
            try:
                made.append(mb.bm.faces.new([V(i, z) for i in f]))
            except ValueError:
                pass
        # saia nas arestas de borda deste grupo (nao ha face vizinha no mesmo nivel ou acima)
        for f in fl:
            for a, b in zip(f, f[1:] + f[:1]):
                e = (min(a, b), max(a, b))
                zl = edge_level.get(e, [])
                if zl.count(z) > 1 or any(z2 > z + 1e-3 for z2 in zl):
                    continue
                try:
                    made.append(mb.bm.faces.new((V(b, z), V(a, z), V(a, z_skirt), V(b, z_skirt))))
                except ValueError:
                    pass
        if made:
            # material face a face: os grupos vizinhos compartilham vertices (superficie continua), entao o
            # MB._post (que pinta toda face ligada aos vertices) repintaria as manchas vizinhas
            mi = mb._mi_for(m)
            t = mb.rng.uniform(-1, 1)
            for fc in made:
                fc.material_index = mi
                fc[mb.tint] = t
                fc.smooth = False
                fc.normal_update()
            mb._uv(made, m)
    return mb


def valley_ground(C, rng):
    """laje de terra + gramado elevado em manchas do vale principal"""
    base = MB("TER_Floor_Base", C, rng)
    base.slab_poly(L.FLOOR_W, Z_BASE, 8.0, "Dirt")
    base.slab_poly(L.FLOOR_E, Z_BASE, 8.0, "Dirt")
    # chao do recuo do penhasco leste (atras da colisao: visto nas reentrancias da face) - terra de pe de penhasco,
    # no mesmo material da laje (um material a mais seria mais uma MeshPart)
    base.slab_poly([(L.EAST_X - 0.5, -64), (L.EAST_X + 18, -64), (L.EAST_X + 18, 64), (L.EAST_X - 0.5, 64)],
                   Z_BASE - 0.05, 8.0, "Dirt")
    base.finish()
    VL = Valley()
    cells, mats = patches((L.WEST_X - 2, -64, L.EAST_X + 2, 64), 17, 10, rng)
    # furos: calcamento (com meio-fio), praca, patios, miolo do trilho, faixas das margens do rio
    holes = []
    for name, pts, w in VL.paths:
        holes.append(ribbon(pts, w + 0.9))
    holes.append([(L.PLAZA_C[0] + math.cos(t) * 25.6, -30.0 + math.sin(t) * 25.6)
                  for t in [math.tau * i / 48 for i in range(48)]])
    for px in L.PORTAL_X:
        holes.append([(px - 8.3, 37.7), (px + 8.3, 37.7), (px + 8.3, L.FLIGHT1_Y0 + 0.4), (px - 8.3, L.FLIGHT1_Y0 + 0.4)])
    if len(VL.rail) > 2:
        holes.append(ribbon(VL.rail, 4.8))
    rx0, rx1 = L.RIVER_X
    holes.append([(rx0 - 0.7, -62.5), (rx0 + 0.2, -62.5), (rx0 + 0.2, 46.2), (rx0 - 0.7, 46.2)])
    holes.append([(rx1 - 0.2, -62.5), (rx1 + 0.7, -62.5), (rx1 + 0.7, 46.2), (rx1 - 0.2, 46.2)])
    # terra gasta
    dirt = []
    for (name, c, door, od, a, sz) in VL.cabins:
        dirt.append(blob(door[0] + od[0] * 3.4, door[1] + od[1] * 3.4, 3.2, 4.4, a, rng))
    if VL.rail:
        dirt.append(ribbon(VL.rail, 9.5))
        # estacao de carga (telheiro sobre o trilho)
        k = min(range(len(VL.rail)), key=lambda i: (VL.rail[i][0] + 54) ** 2 + (VL.rail[i][1] + 8) ** 2)
        q = VL.rail[k]
        dirt.append(blob(q[0], q[1], 10.0, 8.0, rng.uniform(0, 3), rng, n=12))
    mx, my = L.MINE_MOUTH
    ox, oy = -math.cos(L.MINE_DIR), -math.sin(L.MINE_DIR)
    dirt.append(blob(mx + ox * 6.5, my + oy * 6.5, 7.5, 10.5, math.atan2(oy, ox), rng, n=12))
    # curvas internas dos caminhos (atalho do jogador)
    for name, pts, w in VL.paths:
        raw = [p for p in pts]
        for i in range(1, len(raw) - 1):
            a, b, c = Vector(raw[i - 1]), Vector(raw[i]), Vector(raw[i + 1])
            d1, d2 = (b - a), (c - b)
            if d1.length < 1e-3 or d2.length < 1e-3:
                continue
            d1.normalize(); d2.normalize()
            turn = d1.x * d2.y - d1.y * d2.x
            if abs(turn) < 0.25:
                continue
            inner = (d2 - d1)
            if inner.length < 1e-3:
                continue
            inner.normalize()
            p = b + inner * (w / 2 + 2.2)
            dirt.append(blob(p.x, p.y, 3.0 + abs(turn) * 2.0, 2.2, math.atan2(inner.y, inner.x) + math.pi / 2, rng, n=9))
    # trilha gasta do galpao de cristais ate o caminho da margem leste (a caminho da ponte dos fundos)
    dirt.append(ribbon([(112, -28.5), (108, -24.5), (103, -21.5), (98.5, -20.0)], 3.6))
    region = [list(L.FLOOR_W), list(L.FLOOR_E)]
    lawn = _lawn("TER_Floor_Grass", C, region, cells, dirt, holes, Z_LAWN, Z_DIRT, Z_BASE - 0.05, rng, mats)
    # grama invadindo a borda do calcamento (tufos sobre o meio-fio)
    for name, pts, w in VL.paths:
        for a, b in zip(pts, pts[1:]):
            if rng.random() > 0.3:
                continue
            A, B = Vector(a), Vector(b)
            t = (B - A)
            if t.length < 0.5:
                continue
            t.normalize()
            s = Vector((-t.y, t.x))
            side = rng.choice((-1, 1))
            c = A.lerp(B, rng.uniform(0.2, 0.8)) + s * side * (w / 2 + rng.uniform(0.1, 0.6))
            if math.hypot(c.x - L.PLAZA_C[0], c.y + 30) < 27:
                continue
            p = blob(c.x, c.y, rng.uniform(0.9, 2.0), rng.uniform(0.6, 1.1), math.atan2(t.y, t.x), rng, n=7, jag=0.3)
            lawn.prism(p, Z_LAWN - 0.1, Z_LAWN + rng.uniform(0.28, 0.4), rng.choice(("Grass", "Grass_B")))
    # ondulacoes baixas e afloramentos de rocha nos gramados grandes (colisao continua plana)
    from fm_parts import rock_column, _rock_poly
    placed = []

    def far_from(x, y, d):
        return all(math.hypot(x - px, y - py) > d for px, py in placed)
    tries = 0
    nm = 0
    while nm < 14 and tries < 600:
        tries += 1
        x, y = rng.uniform(L.WEST_X + 6, L.EAST_X - 6), rng.uniform(-58, 58)
        R = rng.uniform(5.0, 9.5)
        if not VL.free(x, y, R * 0.6 + 2.0) or not far_from(x, y, 18):
            continue
        h = rng.uniform(0.3, 0.8) if rng.random() < 0.75 else rng.uniform(0.8, 1.2)
        cell = max([0] + [i for i in range(1, len(cells)) if point_in_poly(x, y, cells[i][1])])
        poly = _rock_poly(R, R * rng.uniform(0.6, 0.9), 8, rng, ex=2.0, jit=0.12)
        ang = rng.uniform(0, math.tau)
        ca, sa = math.cos(ang), math.sin(ang)
        poly = [(px * ca - py * sa, px * sa + py * ca) for px, py in poly]
        rock_column(lawn, Vector((x, y, 0)), poly, Z_LAWN - 0.1, Z_LAWN + h, rng, mats[cell], taper=0.42, rings=2,
                    jitter=0.1, tilt=0.02, chamfer=0.0, rim=False, bottom=False)
        placed.append((x, y))
        nm += 1
    no = 0
    tries = 0
    while no < 8 and tries < 600:
        tries += 1
        x, y = rng.uniform(L.WEST_X + 8, L.EAST_X - 8), rng.uniform(-56, 56)
        if not VL.free(x, y, 5.0) or not far_from(x, y, 14):
            continue
        for k in range(rng.randint(2, 4)):
            sz = rng.uniform(1.4, 3.2) * (1.4 if k == 0 else 1.0)
            qx, qy = x + rng.uniform(-3, 3), y + rng.uniform(-3, 3)
            ang = rng.uniform(0, math.tau)
            ca, sa = math.cos(ang), math.sin(ang)
            pl = [(px * ca - py * sa, px * sa + py * ca)
                  for px, py in _rock_poly(sz, sz * rng.uniform(0.55, 0.85), rng.choice((5, 6)), rng, ex=2.0, jit=0.18)]
            # (um material so: cada material a mais no gramado vira mais uma MeshPart no Roblox)
            rock_column(lawn, Vector((qx, qy, 0)), pl, Z_LAWN - 0.3, Z_LAWN + rng.uniform(0.4, 1.2), rng,
                        "Cliff_Rock_Top", taper=rng.uniform(0.5, 0.75), rings=1, jitter=0.15, tilt=0.18,
                        chamfer=0.3, rim=False, bottom=False)
        placed.append((x, y))
        no += 1
    edge_tongues(lawn, rng)
    lawn.finish()
    return VL


def edge_tongues(mb, rng, y=-62.0):
    """borda sul do vale: grama caindo em linguas (e musgo escorrendo) pela face da laje de terra, no lugar de uma
    faixa reta; fora da escadaria frontal e da saida do rio"""
    U = rng.uniform
    for (x0, x1) in ((L.FLOOR_W[0][0] + 1.0, -12.5), (12.5, L.RIVER_X[0] - 1.5), (L.RIVER_X[1] + 1.5, L.EAST_X - 1.0)):
        x = x0 + U(0.0, 1.5)
        while x < x1 - 1.0:
            w = min(U(1.4, 4.2), x1 - x)
            ln = U(0.9, 3.4) if rng.random() < 0.75 else U(3.4, 5.5)
            m = "Grass"
            tip = x + w * U(0.3, 0.7)
            pts = [(x, Z_LAWN + 0.05), (x + w, Z_LAWN + 0.05), (x + w - w * U(0.1, 0.3), Z_LAWN - ln * U(0.4, 0.7)),
                   (tip, Z_LAWN - ln), (x + w * U(0.1, 0.3), Z_LAWN - ln * U(0.5, 0.8))]
            yo = y - U(0.05, 0.25)
            # (aresta de cima chanfrada para fora: le como labio de grama e nao vira 'chao' para o fm_veg)
            f = [mb.bm.verts.new((px, yo - 0.3, pz - (0.32 if pz > Z_LAWN else 0.0))) for px, pz in pts]
            b = [mb.bm.verts.new((px, yo + 0.12, pz)) for px, pz in pts]
            n = len(pts)
            try:
                mb.bm.faces.new(f)
                mb.bm.faces.new(list(reversed(b)))
                for i in range(n):
                    j = (i + 1) % n
                    mb.bm.faces.new((f[j], f[i], b[i], b[j]))
            except ValueError:
                pass
            else:
                mb._post(f + b, m, None, 0, 1)
            x += w + (U(0.2, 2.5) if rng.random() < 0.8 else U(3.0, 7.0))


def terrace_ground(C, rng):
    """gramado em manchas no terraco dos portais (z29.95), com os pocos das escadas e o canal central abertos"""
    zt = L.TERR - 0.05
    x0, x1 = L.WEST_X - 30, L.EAST_X + 30
    y0, y1 = L.UPPER_FRONT_Y + 0.6, L.TERR_BACK_Y + 30
    region = [[(x0, y0), (x1, y0), (x1, y1), (x0, y1)]]
    holes = [[(px - 7.4, y0 - 1), (px + 7.4, y0 - 1), (px + 7.4, L.FLIGHT2_Y1 + 0.6), (px - 7.4, L.FLIGHT2_Y1 + 0.6)]
             for px in L.PORTAL_X]
    holes.append([(-4.3, y0 - 1), (4.3, y0 - 1), (4.3, y1 + 1), (-4.3, y1 + 1)])
    cells, mats = patches((x0, y0, x1, y1), 12, 6, rng)
    lawn = _lawn("TER_Terrace_Grass", C, region, cells, [], holes, zt, zt, L.TERR - 0.8, rng, mats)
    lawn.finish()
