# op_terrain - ZONA TERRAIN da Ilha 5 (ONE PIECE / WANO), V2-3 (PLANO_V2 secoes 2, 3.3, 8, 9 e 11). build() substitui
# op_blockout.terrain. Prefixo OP_Ter_, colecao 02_TERRAIN. Sem luz, sem marcador, SEM COLISAO: a colisao e toda do
# op_col (planta). O visual daqui CASA com ela (gate 'visual' do op_qa):
#   REGRA 1 - todo piso visual andavel (normal >= 0,7) fica NA COTA da colisao (pele exata dos poligonos da planta) ou
#             DENTRO de um solido de colisao (rocha, piso, guarda); fora disso so superficie INGREME (normal < 0,7).
#   REGRA 2 - vao entre 2 placas (fresta de 0,4..3: T1 x praca, praca x canal, pisos x rochas) e fechado por FACE
#             INGREME: o muro de arrimo (ishigaki em talude) nasce na borda da placa de baixo e chega na borda da de
#             cima; nada de faixa plana sem colisao.
#   REGRA 3 - o labio de fora e a BORDA EXATA da uniao das placas (CDT do mathutils: contorno exato, sem grade); a
#             falesia desce dali, ingreme ate 25 abaixo do labio, e so depois se abre em massas, estratos e pe no mar.
#   REGRA 4 - rocha 'walk' (planta: L.ROCK_COL) tem topo PLANO na cota; rocha 'tall' pode subir alem da cota (ninguem
#             chega), mas a face que da para um piso fica dentro do poligono acima do pe (sem prateleira fora dele).
# Geradores:
#   1. PELE (OP_Ter_Ground): poligonos exatos de cada piso em celulas de 2,5 (recorte exato), material por campo
#      (grama 2 tons, terra batida, lajes) com a fronteira grama/terra ORGANICA (vertices puxados para a isolinha do
#      campo) e dissolvida por material. LEITO (piso - 0,35) onde outro modulo pavimenta (praca, ruas, avenida, patio
#      do castelo, patio do torii, caminho do promontorio). Lajeado do cais e do adro.
#   2. ARRIMOS E FACES (OP_Ter_Walls): toda borda de placa com placa mais baixa ao lado -> ishigaki em talude (pedras
#      em fiadas desencontradas, capa, soco) ou face de rocha (quedas altas, rochas), do pe na borda de baixo ao topo.
#   3. FALESIA (OP_Ter_Cliff): cortina continua no contorno da uniao: rolo verde no labio com linguas que escorrem,
#      massas de 18..60 com bojo, fendas escuras, estrato com almofadas verdes (so abaixo de 25 do labio), pe com blocos
#      caidos e espuma (pedra clara) na linha do mar, quilha em cone. Cais = muralha de pedra aparelhada.
#   4. ROCHAS DA PLANTA (OP_Ter_Rocks): topo das rochas 'walk' plano e verde; 'tall' esculpidas (domos, socalcos NE de
#      ishigaki com patamares verdes, contrafortes do castelo), agulhas e picos de Wano (pinaculo oeste SEM pagode,
#      topo 130), contrafortes do fundo, esporao da espada e assento da caveira.
#   5. ROCHEDO DO CASTELO (OP_Ter_CastleRock): proa em colunas facetadas, CANAL CENTRAL da cachoeira e os 2 PAINEIS dos
#      estandartes que o op_castle usa (hh('cf', i, 'dr'), x -19,5..-12,8 / 13,4..19,5, face 351,75).
# CONTRATOS mantidos: hh(), crag(), assign() (op_landmarks/op_castle), CASTLE_ROCK_ANCHORS/castle_rock_z() (op_tree),
#   EXIT_NOTCH (op_exit), TRECHO.
import math, zlib
import numpy as np
import bmesh
import bpy
from mathutils import Vector, noise
from mathutils import geometry as mgeo
import op_lib as DL
from op_lib import MB, ccw, camera
import op_layout as L

C = "02_TERRAIN"
T0, T1, P, CF, CC, W3Z, CL = L.T0, L.T1, L.P, L.CF, L.CC, L.W3, L.CL
SEA, BASE = L.SEA, L.BASE
H = 2.5                         # celula da pele
BBOX = (-262.0, -24.0, 372.0, 530.0)
ROCK, ROCKC, DARK, MOSS, VOID = "Cliff_OP_Face", "Cliff_OP_Shade", "Cliff_OP_Dark", "Cliff_OP_Moss", "Cliff_OP_Void"
CREV, LITE = "Cliff_OP_Crevice", "Cliff_OP"
GDEEP, GRASS, GRASSB = "Grass_OP_Deep", "Grass_OP", "Grass_OP_B"
DIRT, DIRTD, PATH, STONE = "Dirt_OP", "Dirt_OP_Dark", "Stone_OP_Path", "Stone_OP"
WALL, JOINT, WOOD, WOODD = "Stone_OP_Wall", "Stone_OP_Dark", "Wood_OP_Mid", "Wood_OP_Dark"
TRECHO = (-120.0, 109.0, 120.0, 170.0)
BED_D = 0.35                    # leito sob o piso de outro modulo (as lajes do kit2/praca vao de -0,3 a 0)
STEEP = 0.62                    # normal z maxima das faces 'ingremes' (gate: andavel >= 0,7)
REACH_DROP = 25.0               # o gate so olha 25 abaixo do alcancado: abaixo disso a falesia pode ter prateleira


# ------------------------------------------------------------------ variacao DIRIGIDA (hash com finalizador murmur)
def _fmix(h):
    h ^= h >> 16
    h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


def hh(*a):
    s = "|".join(("%.2f" % v) if isinstance(v, float) else str(v) for v in a)
    return _fmix(zlib.crc32(s.encode("utf-8")) ^ 0x9E3779B9) / 4294967296.0


def sdf_poly(X, Y, Pl):
    Pl = np.asarray(Pl, float)
    n = len(Pl)
    inside = np.zeros(X.shape, bool)
    d2 = np.full(X.shape, 1e18)
    for i in range(n):
        ax, ay = Pl[i]
        bx, by = Pl[(i + 1) % n]
        if ay != by:
            cond = (ay > Y) != (by > Y)
            xint = (bx - ax) * (Y - ay) / (by - ay) + ax
            inside ^= cond & (X < xint)
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0)
        d2 = np.minimum(d2, (X - ax - dx * t) ** 2 + (Y - ay - dy * t) ** 2)
    d = np.sqrt(d2)
    return np.where(inside, d, -d)


def sdf_line(X, Y, pts, hw):
    d2 = np.full(np.shape(X), 1e18)
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        l2 = dx * dx + dy * dy or 1e-9
        t = np.clip(((X - ax) * dx + (Y - ay) * dy) / l2, 0.0, 1.0)
        d2 = np.minimum(d2, (X - ax - dx * t) ** 2 + (Y - ay - dy * t) ** 2)
    return hw - np.sqrt(d2)


def waves(X, Y, seed, scale=1.0):
    out = np.zeros(np.shape(X))
    for k, (fx, fy, ph) in enumerate(((0.031, 0.018, 0.0), (-0.017, 0.043, 1.3), (0.052, -0.029, 2.1),
                                      (0.011, 0.067, 4.0))):
        out = out + math.cos(k * 0.7 + seed) * 0.42 * np.sin((np.asarray(X) * fx + np.asarray(Y) * fy) * scale * 6.0
                                                             + ph + seed * (k + 1))
    return out


def _area(pl):
    return 0.5 * sum(pl[i][0] * pl[(i + 1) % len(pl)][1] - pl[(i + 1) % len(pl)][0] * pl[i][1] for i in range(len(pl)))


def loop_area(pl):
    return _area(pl)


def _bb(pl):
    xs = [p[0] for p in pl]
    ys = [p[1] for p in pl]
    return (min(xs), min(ys), max(xs), max(ys))


def assign(mb, faces, m):
    """material EXPLICITO (sem sorteio de variante)"""
    mi = mb._mi(m)
    fl = [f for f in faces if f.is_valid]
    for f in fl:
        f.material_index = mi
        f[mb.tint] = 0.0
        f.smooth = False
    mb._uv(fl, m)
    return fl




# ================================================================== FACES com orientacao explicita
class FB:
    """faces soltas com a normal virada para 'want' e material explicito; o MB fecha com recalc=False"""

    def __init__(self, name, coll=C):
        self.mb = MB(name, coll, None, detail="far", floor=-999)
        self.by = {}

    def face(self, pts, m, want=None):
        bm = self.mb.bm
        if len(pts) < 3:
            return None
        try:
            f = bm.faces.new([bm.verts.new(p) for p in pts])
        except ValueError:
            return None
        if want is not None:
            f.normal_update()
            if Vector(want).dot(f.normal) < 0.0:
                f.normal_flip()
        self.by.setdefault(m, []).append(f)
        return f

    def add(self, faces, m):
        self.by.setdefault(m, []).extend(faces)

    def finish(self):
        for m in sorted(self.by):
            fl = [f for f in self.by[m] if f.is_valid]
            for f in fl:
                f.normal_update()
            assign(self.mb, fl, m)
        return self.mb.finish(recalc=False)


def tris_of(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob else 0


# ================================================================== 0. PLANTA: placas, frestas, contorno exato
class Plate:
    __slots__ = ("name", "kind", "poly", "z0", "zf", "bb", "walk")

    def __init__(self, name, kind, poly, z0, zf=None, walk=True):
        self.name, self.kind, self.poly, self.z0 = name, kind, ccw(poly), z0
        self.zf = zf or (lambda x, y, z=z0: z)
        self.bb = _bb(self.poly)
        self.walk = walk

    def has(self, x, y, pad=1e-6):
        b = self.bb
        return b[0] - pad <= x <= b[2] + pad and b[1] - pad <= y <= b[3] + pad and L.point_in_poly(x, y, self.poly)


def _stair_z(nm):
    foot, deg, w, n, tread, g = L.stair_frame(nm)
    rise = L.stair_rise(nm)
    a = math.radians(deg)
    ux, uy = math.cos(a), math.sin(a)

    def z(x, y):
        t = ((x - foot[0]) * ux + (y - foot[1]) * uy + tread / 2) / tread
        return foot[2] + max(0.0, min(float(n), t)) * rise
    return z


class PL:
    plates = []
    fillers = []        # (poligono, z, placa, placa vizinha)
    loops = []          # contornos de fora (anti-horario)
    holes = []


def _water_polys():
    import op_col
    return op_col.water_polys()


def plan_plates():
    out = []
    for nm, poly, z, pr in L.floors():
        if nm == "ShipDeck":
            continue
        for pc in L.floor_pieces(nm):
            pc = ccw(pc)
            if nm == "Harbor":
                pc = DL.clip_half(pc, -1.0, 0.0, 222.4)           # pier e palafita (x > 222,4) sao do op_harbor
            if len(pc) >= 3 and abs(_area(pc)) > 0.5:
                out.append(Plate(nm, "floor", pc, L._zval(z, 0, 0)))
    for nm, up, rect, zf, zt in L.stair_notches():
        out.append(Plate("Stair_" + nm, "stair", L.rect_poly(rect), zf, _stair_z(nm)))
    for nm, pts, z in L.ROCKS:
        out.append(Plate("Rock_" + nm, "rock", pts, z, walk=L.ROCK_COL.get(nm) == "walk"))
    for nm, pts, z in _water_polys():
        out.append(Plate("Water_" + nm, "water", pts, z))
    return out


def top_at(x, y, pad=1e-6):
    """(z, placa) do topo fisico em (x, y): o MAIOR z entre as placas que contem o ponto (as caixas de colisao sao
    solidos que se somam); None fora de tudo"""
    best = None
    for p in PL.plates:
        if p.has(x, y, pad):
            z = p.zf(x, y)
            if best is None or z > best[0] + 1e-6:
                best = (z, p)
    return best


MAXG = 8.0


def neighbor(p, x, y, nx, ny, maxg=MAXG):
    """primeira placa (outra) na normal de fora de (x, y): (d, z, placa) ou None"""
    d = 0.04
    while d <= maxg + 1e-6:
        q = top_at(x + nx * d, y + ny * d)
        if q is not None and q[1] is not p:
            return (d, q[0], q[1])
        d += 0.1 if d < 2.0 else 0.25
    return None


def _fillers(step=1.0):
    """frestas de 0,04..MAXG entre uma placa e a vizinha: quadrilateros que fecham o contorno (a uniao fica sem
    fendas); quem cobre a fresta e a face/arrimo da placa de cima"""
    out = []
    for p in PL.plates:
        pl = p.poly
        n = len(pl)
        for i in range(n):
            a, b = pl[i], pl[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 0.2:
                continue
            nx, ny = dy / ln, -dx / ln
            m = max(1, int(math.ceil(ln / step)))
            prev = None
            for s in range(m + 1):
                t = s / m
                x, y = a[0] + dx * t, a[1] + dy * t
                hit = neighbor(p, x, y, nx, ny)
                if prev is not None and prev[2] and hit and max(prev[2][0], hit[0]) > 0.1:
                    d0, d1 = prev[2][0] + 0.1, hit[0] + 0.1
                    quad = [(prev[0], prev[1]), (x, y), (x + nx * d1, y + ny * d1), (prev[0] + nx * d0, prev[1] + ny * d0)]
                    out.append((ccw(quad), min(p.zf(x, y), hit[1]), p, hit[2]))
                prev = (x, y, hit)
    return out


def _cdt_union(polys):
    """uniao EXATA (CDT): contornos = arestas de 1 triangulo so (orientadas: dentro a esquerda)"""
    vco, faces = [], []
    for pl in polys:
        b = len(vco)
        vco += [Vector(p) for p in pl]
        faces.append(list(range(b, b + len(pl))))
    res = mgeo.delaunay_2d_cdt(vco, [], faces, 1, 1e-4, True)
    V, F0, OF = res[0], res[2], res[5]
    F = [f for f, o in zip(F0, OF) if o]
    cnt = {}
    for f in F:
        k = len(f)
        for i in range(k):
            a, b = f[i], f[(i + 1) % k]
            key = (a, b) if a < b else (b, a)
            cnt[key] = cnt.get(key, 0) + 1
    nxt = {}
    for f in F:
        k = len(f)
        pa, pb, pc = V[f[0]], V[f[1]], V[f[2 % k]]
        cw = (pb.x - pa.x) * (pc.y - pa.y) - (pb.y - pa.y) * (pc.x - pa.x) < 0
        ff = list(reversed(f)) if cw else list(f)
        for i in range(k):
            a, b = ff[i], ff[(i + 1) % k]
            key = (a, b) if a < b else (b, a)
            if cnt[key] == 1:
                nxt[a] = b
    loops = []
    seen = set()
    for s in sorted(nxt):
        if s in seen:
            continue
        lp = []
        v = s
        while v not in seen and v in nxt:
            seen.add(v)
            lp.append((V[v].x, V[v].y))
            v = nxt[v]
        if len(lp) >= 3:
            loops.append(lp)
    return loops


def _simplify(lp, tol=0.02):
    """tira vertices colineares e pontas quase repetidas (a CDT quebra as arestas nos cruzamentos)"""
    out = list(lp)
    changed = True
    while changed and len(out) > 3:
        changed = False
        n = len(out)
        for i in range(n):
            a, b, c = out[i - 1], out[i], out[(i + 1) % n]
            if math.hypot(b[0] - a[0], b[1] - a[1]) < 0.05:
                out.pop(i)
                changed = True
                break
            d, t = L.seg_dist(b[0], b[1], a[0], a[1], c[0], c[1])
            if d < tol and 0.0 < t < 1.0:
                out.pop(i)
                changed = True
                break
    return out


def plan_prepare():
    PL.plates = plan_plates()
    PL.fillers = _fillers()
    polys = [p.poly for p in PL.plates] + [f[0] for f in PL.fillers]
    loops = [_simplify(lp) for lp in _cdt_union(polys)]
    loops.sort(key=lambda lp: -abs(_area(lp)))
    PL.loops = [lp for lp in loops if _area(lp) > 0]
    PL.holes = [lp for lp in loops if _area(lp) < -1.0]


# ================================================================== 1. PELE DO CHAO (exata na cota da colisao)
# LEITO (piso - 0,35) onde OUTRO modulo pavimenta: as lajes do kit2/op_plaza/op_castle vao de -0,3 a 0 (topo rente a
# colisao) e as juntas mostram o berco escuro deles -> a pele daqui fica embaixo (sem coplanar).
SUMMON_TERRACE = (116.0, 150.0, 206.0, 264.0)
SLABBED = {"Forecourt": (PATH, STONE), "HarborMid": (STONE, PATH), "Harbor": (STONE, PATH)}
LV = {"top": 0.0, "bed": -BED_D, "slab": -0.15}


def _in_summon(X, Y):
    r = SUMMON_TERRACE
    return (X >= r[0]) & (X <= r[2]) & (Y >= r[1]) & (Y <= r[3])


class Fields:
    """campos com sinal (> 0 = dentro) avaliados em pontos quaisquer (numpy): leito, terra, grama B, borda de rocha"""

    def __init__(self, plate):
        self.p = plate
        z = plate.z0
        b = plate.bb
        pad = 20.0
        near = lambda bb2: not (bb2[2] < b[0] - pad or bb2[0] > b[2] + pad or bb2[3] < b[1] - pad or bb2[1] > b[3] + pad)
        self.streets = [(pts, w) for pts, w, zz in L.STREETS_V2 if abs(zz - z) < 0.05 and near(_bb(pts))]
        self.lots = [L.lot_poly(lt, 0.6) for lt in L.block_lots() if abs(lt["z"] - z) < 0.05 and near(_bb(L.lot_poly(lt)))]
        self.nm = plate.name

    def bed(self, X, Y):
        f = np.full(np.shape(X), -1e9)
        nm = self.nm
        if self.p.kind == "stair":
            return np.full(np.shape(X), 1e3)
        if nm == "Plaza":
            f = np.maximum(f, sdf_poly(X, Y, ccw(L.PLAZA)) - 0.5)
        if nm == "Entry":
            f = np.maximum(f, sdf_poly(X, Y, ccw(L.ENTRY_COURT)) - 0.4)
        if nm == "Court":
            f = np.maximum(f, sdf_poly(X, Y, ccw(L.COURT)) - 0.4)
        if nm == "ExitLand":
            Ln = L.EXIT_BRIDGE_LEN
            f = np.maximum(f, sdf_line(X, Y, [L.exit_point(Ln - 2.0), L.exit_point(Ln + L.ANCHOR_OPM_OFF)], 6.0 - 0.4))
        ins = _in_summon(np.asarray(X), np.asarray(Y))
        for pts, w in self.streets:
            f = np.maximum(f, np.where(ins, -1e9, sdf_line(X, Y, pts, w / 2 - 0.4)))
        return f

    def dirt(self, X, Y, fb=None):
        fb = self.bed(X, Y) if fb is None else fb
        band = np.maximum(0.6, 1.1 + 0.5 * waves(X, Y, 1.7))
        f = fb + band
        for lp in self.lots:
            f = np.maximum(f, sdf_poly(X, Y, ccw(lp)))
        ins = _in_summon(np.asarray(X), np.asarray(Y))
        for pts, w in self.streets:
            f = np.maximum(f, np.where(ins, sdf_line(X, Y, pts, w / 2 - 0.4), -1e9))
        return f

    def gb(self, X, Y):
        return (waves(X, Y, 5.3, 0.7) - 0.25) * 6.0

    def moss(self, X, Y):
        e = -sdf_poly(X, Y, self.p.poly)                   # < 0 dentro: -distancia ate a borda
        return e + 3.6 + 1.6 * (0.5 + 0.5 * waves(X, Y, 3.1, 1.6))


def _classify(fl, X, Y):
    """classe por ponto: 'BED', 'SLAB', 'PATH', 'MOSS', 'GDEEP', 'DIRT', 'GRASSB', 'GRASS'"""
    p = fl.p
    fb = fl.bed(X, Y)
    out = np.empty(np.shape(X), dtype=object)
    if p.kind == "rock":
        fm = fl.moss(X, Y)
        out[:] = np.where(fm > 0, "MOSS", "GDEEP")
        return out
    if p.name in SLABBED:
        out[:] = np.where(fb > 0, "BED", "SLAB")
        return out
    if p.name == "CastleLanding":
        out[:] = np.where(fb > 0, "BED", "PATH")
        return out
    fd = fl.dirt(X, Y, fb)
    fg = fl.gb(X, Y)
    out[:] = np.where(fb > 0, "BED", np.where(fd > 0, "DIRT", np.where(fg > 0, "GRASSB", "GRASS")))
    return out


CLS_LV = {"BED": "bed", "SLAB": "slab"}
CLS_MAT = {"BED": DIRTD, "SLAB": JOINT, "PATH": PATH, "MOSS": MOSS, "GDEEP": GDEEP, "DIRT": DIRT, "GRASSB": GRASSB,
           "GRASS": GRASS}


def _snap_field(fl, classes):
    if "BED" in classes:
        return fl.bed
    if "MOSS" in classes:
        return fl.moss
    if "DIRT" in classes:
        return fl.dirt
    return fl.gb


def skin_plate(fb, p, higher):
    """pele da placa p: celulas de H com recorte EXATO do poligono, classe por campo no centro, fronteira entre classes
    puxada para a isolinha do campo (organica), dissolvida por material; saia vertical entre niveis"""
    fl = Fields(p)
    x0, y0, x1, y1 = p.bb
    i0, i1 = int(math.floor((x0 - BBOX[0]) / H)), int(math.ceil((x1 - BBOX[0]) / H))
    j0, j1 = int(math.floor((y0 - BBOX[1]) / H)), int(math.ceil((y1 - BBOX[1]) / H))
    cells = []
    for j in range(j0, j1):
        for i in range(i0, i1):
            rx0, ry0 = BBOX[0] + i * H, BBOX[1] + j * H
            pc = L.clip_rect(p.poly, (rx0, ry0, rx0 + H, ry0 + H))
            if len(pc) < 3 or abs(_area(pc)) < 1e-3:
                continue
            cx = sum(q[0] for q in pc) / len(pc)
            cy = sum(q[1] for q in pc) / len(pc)
            if higher:
                pts = [(cx, cy)] + list(pc)
                if all(any(h.has(qx, qy, -0.02) for h in higher) for qx, qy in pts):
                    continue                                  # inteira sob uma placa mais alta (mirante sobre a praca)
            cells.append([pc, cx, cy])
    if not cells:
        return 0
    CX = np.array([c[1] for c in cells])
    CY = np.array([c[2] for c in cells])
    cls = _classify(fl, CX, CY)
    K = lambda q: (int(round(q[0] * 1000.0)), int(round(q[1] * 1000.0)))
    pos, ecount, kcls = {}, {}, {}
    for ci, c in enumerate(cells):
        pc = c[0]
        ks = [K(q) for q in pc]
        # tira repetidos consecutivos (recorte pode gerar)
        kk, qq = [], []
        for k, q in zip(ks, pc):
            if not kk or kk[-1] != k:
                kk.append(k)
                qq.append(q)
        if len(kk) > 1 and kk[0] == kk[-1]:
            kk.pop()
            qq.pop()
        c.append(kk)
        for k, q in zip(kk, qq):
            pos.setdefault(k, [q[0], q[1]])
            kcls.setdefault(k, set()).add(cls[ci])
        for a, b in zip(kk, kk[1:] + kk[:1]):
            e = (a, b) if a < b else (b, a)
            ecount.setdefault(e, []).append(ci)
    bnd = set()
    for e, cs in ecount.items():
        if len(cs) == 1:
            bnd.add(e[0])
            bnd.add(e[1])
    # fronteira organica: vertice interno com classes diferentes -> isolinha do campo (passo de Newton limitado)
    mv = [k for k, s in kcls.items() if len(s) > 1 and k not in bnd]
    if mv:
        groups = {}
        for k in mv:
            groups.setdefault(_snap_field(fl, kcls[k]), []).append(k)
        for fn, ks in groups.items():
            X = np.array([pos[k][0] for k in ks])
            Y = np.array([pos[k][1] for k in ks])
            e = 0.15
            f0 = fn(X, Y)
            gx = (fn(X + e, Y) - fn(X - e, Y)) / (2 * e)
            gy = (fn(X, Y + e) - fn(X, Y - e)) / (2 * e)
            g2 = gx * gx + gy * gy + 1e-9
            dx, dy = -f0 * gx / g2, -f0 * gy / g2
            ln = np.sqrt(dx * dx + dy * dy)
            s = np.minimum(1.0, 0.42 * H / np.maximum(ln, 1e-9))
            for k, ddx, ddy in zip(ks, dx * s, dy * s):
                pos[k] = [pos[k][0] + float(ddx), pos[k][1] + float(ddy)]
    bm = fb.mb.bm
    verts = {}

    def V(k, lv):
        v = verts.get((k, lv))
        if v is None:
            v = bm.verts.new((pos[k][0], pos[k][1], p.z0 + LV[lv]))
            verts[(k, lv)] = v
        return v
    faces_by = {}
    lvl_of = []
    for ci, c in enumerate(cells):
        kk = c[3]
        lv = CLS_LV.get(cls[ci], "top")
        lvl_of.append(lv)
        if len(kk) < 3:
            continue
        try:
            f = bm.faces.new([V(k, lv) for k in kk])
        except ValueError:
            continue
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
        faces_by.setdefault((lv, cls[ci]), []).append(f)
    # saias entre niveis (topo -> leito/lajeado)
    skirts = []
    for e, cs in sorted(ecount.items()):
        if len(cs) != 2:
            continue
        la, lb = lvl_of[cs[0]], lvl_of[cs[1]]
        if la == lb:
            continue
        hi, lo = (cs[0], cs[1]) if LV[la] > LV[lb] else (cs[1], cs[0])
        lh, ll = lvl_of[hi], lvl_of[lo]
        a, b = e
        want = (cells[lo][1] - (pos[a][0] + pos[b][0]) / 2, cells[lo][2] - (pos[a][1] + pos[b][1]) / 2, 0.0)
        f = fb.face([(pos[a][0], pos[a][1], p.z0 + LV[lh]), (pos[b][0], pos[b][1], p.z0 + LV[lh]),
                     (pos[b][0], pos[b][1], p.z0 + LV[ll]), (pos[a][0], pos[a][1], p.z0 + LV[ll])], DIRTD, want)
        if f:
            skirts.append(f)
    # dissolve por TILE de 8 x 8 celulas, nivel e material, em ordem fixa (determinismo); depois TRIANGULA aqui
    # (ngon gigante concavo triangulava errado: buracos na pele)
    tiles = {}
    for (lv, c_), fs in faces_by.items():
        for f in fs:
            if not f.is_valid:
                continue
            cc = f.calc_center_median()
            tk = (int(math.floor((cc.x - BBOX[0]) / (H * 8))), int(math.floor((cc.y - BBOX[1]) / (H * 8))))
            tiles.setdefault((lv, c_, tk), []).append(f)
    n_f = 0
    for (lv, c_, tk) in sorted(tiles):
        fs = [f for f in tiles[(lv, c_, tk)] if f.is_valid]
        if not fs:
            continue
        bm.verts.index_update()
        bm.edges.index_update()
        es = sorted({e for f in fs for e in f.edges}, key=lambda e: e.index)
        vs = sorted({v for f in fs for v in f.verts}, key=lambda v: v.index)
        res = bmesh.ops.dissolve_limit(bm, angle_limit=0.01, use_dissolve_boundaries=False, verts=vs, edges=es,
                                       delimit={"MATERIAL"})
        allf = list({f for f in list(res.get("region", [])) + fs if f.is_valid})
        allf.sort(key=lambda f: min(v.index for v in f.verts))
        tr = bmesh.ops.triangulate(bm, faces=allf, quad_method="BEAUTY", ngon_method="BEAUTY")
        allf = [f for f in tr["faces"] if f.is_valid]
        for f in allf:
            f.normal_update()
            if f.normal.z < 0:
                f.normal_flip()
        fb.add(allf, CLS_MAT[c_])
        n_f += len(allf)
    return n_f


def slab_field(fb, p, mats):
    """lajeado (cais, rua alta do porto, adro): lajes em fiadas desencontradas, topo +0,12 (a colisao fica rente), fundo
    escondido no lajeado (-0,15); junta = o vao de 0,1 entre lajes. Faixa da borda d'agua (x 222,4) em pedra clara."""
    m0, m1 = mats
    x0, y0, x1, y1 = p.bb
    zt = p.z0 + 0.12
    along_x = (x1 - x0) > (y1 - y0) * 1.6 or p.name == "Forecourt"
    W, Lo, Lh = 3.0, 3.6, 2.4
    n = 0
    if along_x:
        rows = int(math.ceil((y1 - y0) / W))
        for r in range(rows):
            ya, yb = y0 + r * W, min(y1, y0 + (r + 1) * W)
            x = x0 - Lo * hh(p.name, r, "o")
            k = 0
            while x < x1:
                xa, xb = x, x + Lo + Lh * hh(p.name, r, k)
                x, k = xb, k + 1
                n += _slab(fb, p, (xa + 0.05, ya + 0.05, xb - 0.05, yb - 0.05), zt, m0 if hh(p.name, r, k, "m") > 0.3 else m1)
    else:
        cols = int(math.ceil((x1 - x0) / W))
        for c_ in range(cols):
            xa, xb = x1 - (c_ + 1) * W, x1 - c_ * W
            edge = p.name == "Harbor" and c_ == 0
            y = y0 - Lo * hh(p.name, c_, "o")
            k = 0
            while y < y1:
                ya, yb = y, y + Lo + Lh * hh(p.name, c_, k)
                y, k = yb, k + 1
                mm = m1 if edge else (m0 if hh(p.name, c_, k, "m") > 0.3 else m1)
                n += _slab(fb, p, (max(x0, xa) + 0.05, ya + 0.05, xb - 0.05, yb - 0.05), zt, mm)
    return n


def _slab(fb, p, rect, zt, m):
    pc = L.clip_rect(p.poly, rect)
    if len(pc) < 3 or abs(_area(pc)) < 0.4:
        return 0
    # so a parte que e DESTA placa (centro dentro e sem placa mais alta por cima)
    cx = sum(q[0] for q in pc) / len(pc)
    cy = sum(q[1] for q in pc) / len(pc)
    t = top_at(cx, cy)
    if t is None or t[1].name != p.name:
        return 0
    if Fields(p).bed(np.array([cx]), np.array([cy]))[0] > 0:
        return 0
    f = fb.face([(x, y, zt) for x, y in pc], m, (0, 0, 1))      # so o tampo: a junta e o vao (lajeado escuro embaixo)
    return 1 if f else 0


def build_ground():
    fb = FB("OP_Ter_Ground")
    n = 0
    for p in PL.plates:
        if p.kind == "water":
            continue
        higher = [q for q in PL.plates if q is not p and q.kind in ("floor", "rock") and q.z0 > p.z0 + 0.05 and
                  not (q.bb[2] < p.bb[0] or q.bb[0] > p.bb[2] or q.bb[3] < p.bb[1] or q.bb[1] > p.bb[3])]
        n += skin_plate(fb, p, higher)
    ns = 0
    fs = FB("OP_Ter_Slabs")
    for p in PL.plates:
        if p.name in SLABBED and p.kind == "floor":
            ns += slab_field(fs, p, SLABBED[p.name])
    # soleira do cais ate as tabuas do pier/palafita (op_harbor comeca em x 223): fecha a fresta 222,4..223
    for y0, y1 in ((40.0, 76.0), (110.0, 200.0)):
        y = y0
        k = 0
        while y < y1 - 0.1:
            yb = min(y1, y + 3.0 + 1.5 * hh("sol", y0, k))
            fs.face([(222.35, y + 0.05, L.HARBOR + 0.12), (223.1, y + 0.05, L.HARBOR + 0.12), (223.1, yb - 0.05, L.HARBOR + 0.12),
                     (222.35, yb - 0.05, L.HARBOR + 0.12)], PATH, (0, 0, 1))
            y, k = yb, k + 1
    ob = fb.finish()
    os_ = fs.finish()
    print("op_terrain: pele %d faces, %d tris | lajes %d, %d tris" % (n, tris_of(ob), ns, tris_of(os_)))
    return ob


# ================================================================== 2. ARRIMOS, FACES DE ROCHA E ESPINHAS (bordas internas)
PROA = (-25.6, 357.5, 25.6)          # frente do rochedo do castelo (patio, y < 357,5, |x| < 25,6): build_castle_rock
SOCALCO = ("Rock_CastleFootE", "Rock_NESocalco", "Rock_BackE")
CASTLE_STAIR_WALL = ("Court", "CastleLanding", "Rock_ButtressL", "Rock_CastleFootW", "Rock_BackW")


GUARDS = []
OTHERS = []


def guards_load():
    """caixas COL_OP_Guard_* (op_core ja criou): fresta com guarda dentro = o fundo da guarda vira 'piso' no gate"""
    GUARDS.clear()
    OTHERS.clear()
    for o in bpy.data.objects:
        if o.name.startswith("COL_") and not o.name.startswith("COL_OP_Guard_") and o.type == "MESH":
            ws = [o.matrix_world @ v.co for v in o.data.vertices]
            if abs(o.matrix_world.determinant()) < 1e-9:
                continue
            OTHERS.append((o.matrix_world.inverted(), min(v.z for v in ws), max(v.z for v in ws),
                           (min(v.x for v in ws), min(v.y for v in ws), max(v.x for v in ws), max(v.y for v in ws))))
        if o.name.startswith("COL_OP_Guard_") and o.type == "MESH":
            ws = [o.matrix_world @ v.co for v in o.data.vertices]
            GUARDS.append((o.matrix_world.inverted(), min(v.z for v in ws), (min(v.x for v in ws), min(v.y for v in ws),
                                                                              max(v.x for v in ws), max(v.y for v in ws))))


def guard_at(x, y):
    for mi, zb, bb in GUARDS:
        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]:
            q = mi @ Vector((x, y, zb + 0.5))
            if abs(q.x) <= 0.5 and abs(q.y) <= 0.5:
                return zb
    return None


def _proa(p, x, y):
    return p.name == "Court" and y < PROA[1] and abs(x) < PROA[2]


def _kind(p, q, zt, zn, d, x, y):
    drop = zt - zn
    if drop < 1.4 * d + 0.4:
        return "spine"
    if q.name.startswith("Stair_Castelo") and p.name in CASTLE_STAIR_WALL:
        return "big"
    if p.name in ("Harbor", "HarborMid") or q.name in ("Harbor", "HarborMid"):
        return "big"
    if p.name == "Court":
        return "rock"                      # o perimetro do patio tem os muros/guardas do op_castle: aqui so a rocha
    if p.name in SOCALCO and x > 95.0:
        return "ishi"
    if p.kind == "floor" and drop <= 12.5:
        return "ishi"
    return "rock"


def edge_runs(step=1.0):
    """bordas de placa com placa MAIS BAIXA ao lado (ate MAXG): corridas retas (por aresta) de amostras
    (x, y, nx, ny, z de cima, z de baixo, d ate a vizinha, vizinha anda?) agrupadas por tipo e vizinha"""
    runs = []
    for p in PL.plates:
        if p.kind in ("water", "stair"):
            continue
        pl = p.poly
        n = len(pl)
        for i in range(n):
            a, b = pl[i], pl[(i + 1) % n]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 0.3:
                continue
            nx, ny = dy / ln, -dx / ln
            m = max(1, int(math.ceil(ln / step)))
            cur, key_c = [], None
            for s in range(m + 1):
                t = s / m
                x, y = a[0] + dx * t, a[1] + dy * t
                key = None
                nb = neighbor(p, x, y, nx, ny)
                if nb is not None and not _proa(p, x, y):
                    d, zn, q = nb
                    zt = p.zf(x, y)
                    ok = q.name != p.name
                    if q.kind == "water" and p.kind == "floor" and q.name.startswith("Water_Canal") and zt - zn < 4.5:
                        ok = False                                # margem de canal: capa e cantaria do op_water
                    if ok and zt - zn < 0.3:
                        ok = abs(zt - zn) < 0.3 and d > 0.3 and p.name < q.name
                    if ok:
                        kd = _kind(p, q, zt, zn, d, x, y)
                        if q.kind == "stair" and kd in ("ishi", "big"):
                            d = 0.0                               # ao lado da escada: muro reto na borda (banzo/guarda)
                        g = guard_at(x + nx * d * 0.5, y + ny * d * 0.5) if (d > 0.6 and kd in ("ishi", "big")) else None
                        mode = "" if g is None else ("L" if g > zn + 1.0 else "G")
                        key = (kd, q.name, mode)
                        smp = (x, y, nx, ny, zt, zn, d, q.kind in ("floor", "stair"), g)
                if key != key_c and cur:
                    runs.append((key_c[0], p.name, key_c[1], cur))
                    cur = []
                key_c = key
                if key:
                    cur.append(smp)
            if cur and key_c:
                runs.append((key_c[0], p.name, key_c[1], cur))
    out = []
    for kind, pn, qn, smp in runs:
        if len(smp) < 2 or math.hypot(smp[-1][0] - smp[0][0], smp[-1][1] - smp[0][1]) < 1.5:
            continue
        # erosao do d (fresta): a amostra da quina mede a vizinha la longe (6+) e o talude passaria por cima do piso
        ds = [s_[6] for s_ in smp]
        er = [min(ds[max(0, i - 2):i + 3]) for i in range(len(ds))]
        smp = [s_[:6] + (e,) + s_[7:] for s_, e in zip(smp, er)]
        mode = kind[2] if isinstance(kind, tuple) else ""
        out.append((kind, pn, qn, smp))
    res = []
    for kind, pn, qn, smp in out:
        gs = [s_[8] for s_ in smp if s_[8] is not None]
        if gs and kind in ("ishi", "big"):
            g = min(gs)
            if g > max(s_[5] for s_ in smp) + 1.0:
                # fresta com a GUARDA da placa de cima (fundo = piso de cima - 0,5): TAMPA de pedra na fresta logo abaixo
                # do fundo da guarda e o muro desce na borda da placa de BAIXO
                smp = [(x + nx * d, y + ny * d, nx, ny, g - 0.7, zn, 0.0, w, ("L", x, y, d, zt, g))
                       for x, y, nx, ny, zt, zn, d, w, _ in smp]
            else:
                # fresta com a guarda da placa de baixo: muro recuado na borda de cima + canaleta sob o fundo da guarda
                smp = [(x, y, nx, ny, zt, zn, 0.0, w, ("G", d, g)) for x, y, nx, ny, zt, zn, d, w, _ in smp]
        else:
            smp = [s_[:8] + (None,) for s_ in smp]
        res.append((kind, pn, qn, smp))
    return res
    return out


def _lerp_smp(smp, s, ln, k):
    t = max(0.0, min(1.0, s / ln)) * (len(smp) - 1)
    i = min(int(t), len(smp) - 2)
    f = t - i
    return smp[i][k] * (1 - f) + smp[i + 1][k] * f


def wall_run(fb, smp, big=False, key="w", cap=True):
    """ISHIGAKI EM TALUDE: o pe nasce na borda da placa de baixo (d - 0,35), o topo na borda desta placa; pedras
    aparelhadas em fiadas desencontradas (30% das pedras grandes ocupam 2 fiadas), topo de cada pedra CHANFRADO (normal <
    0,7: nao e piso sem colisao), junta escura no plano do talude, capa clara DENTRO do piso (+0,12)"""
    a, b = smp[0], smp[-1]
    nx, ny = a[2], a[3]
    ux, uy = b[0] - a[0], b[1] - a[1]
    ln = math.hypot(ux, uy)
    if ln < 0.6:
        return 0
    ux, uy = ux / ln, uy / ln
    zt = max(s_[4] for s_ in smp)
    cap_h = 0.5
    ztop = zt - cap_h

    def foot(s):
        return _lerp_smp(smp, s, ln, 5) - 0.45

    def fo(s):
        return max(0.0, _lerp_smp(smp, s, ln, 6) - 0.38)

    def base(s):
        return min(0.0, _lerp_smp(smp, s, ln, 6) - 0.38)       # sem fresta: plano recuado (a pedra nao passa da borda)

    def op(s, z):
        zb = foot(s)
        h = max(0.1, ztop - zb)
        return fo(s) * max(0.0, min(1.0, (ztop - z) / h)) + base(s)

    def Pt(s, o, z):
        return (a[0] + ux * s + nx * o, a[1] + uy * s + ny * o, z)
    NV, UV = (nx, ny, 0.0), (ux, uy, 0.0)
    seg = max(1, int(math.ceil(ln / 6.0)))
    ch_seq = (1.5, 2.4, 1.9, 1.6, 2.2) if big else (1.1, 1.5, 1.0, 1.3, 1.6)
    bl_lo, bl_hi = (3.6, 6.2) if big else (2.0, 3.8)
    nst = 0
    for g in range(seg):
        s0, s1 = ln * g / seg, ln * (g + 1) / seg
        zb = min(foot(s0), foot(s1))
        # junta: plano do talude (escuro) do pe ate a capa
        fb.face([Pt(s0, op(s0, zb), zb), Pt(s1, op(s1, zb), zb), Pt(s1, 0.0, ztop + 0.05), Pt(s0, 0.0, ztop + 0.05)],
                JOINT, NV)
        z = zb + 0.3
        row = 0
        courses = []
        while z < ztop - 0.3:
            chh = ch_seq[int(hh(key, g, row, "c") * len(ch_seq)) % len(ch_seq)] * (0.85 + 0.3 * hh(key, g, row, "c2"))
            z1 = min(z + chh, ztop)
            if ztop - z1 < 0.45:
                z1 = ztop
            courses.append((z, z1))
            z = z1
            row += 1
        busy = {}
        for row, (z, z1) in enumerate(courses):
            s = s0 + (0.0 if row % 2 == 0 else -0.6 * hh(key, g, row))
            q = 0
            while s < s1 - 0.05:
                w = bl_lo + (bl_hi - bl_lo) * hh(key, g, row, q, "w")
                e = min(s + w, s1)
                if s1 - e < bl_lo * 0.5:
                    e = s1
                pieces = [(max(s, s0) + 0.07, e - 0.07)]
                for oa, ob_ in busy.get(row, ()):
                    nxt = []
                    for pa, pb in pieces:
                        if ob_ <= pa or oa >= pb:
                            nxt.append((pa, pb))
                            continue
                        if oa > pa:
                            nxt.append((pa, oa - 0.14))
                        if ob_ < pb:
                            nxt.append((ob_ + 0.14, pb))
                    pieces = nxt
                dbl = big and row + 1 < len(courses) and len(pieces) == 1 and hh(key, g, row, q, "dbl") > 0.7
                for sa, sb in pieces:
                    if sb - sa <= 0.3:
                        continue
                    za, zz = z + 0.06, z1 - 0.06
                    if dbl:
                        zz = courses[row + 1][1] - 0.06
                        busy.setdefault(row + 1, []).append((sa, sb))
                    pr = (0.2 + 0.12 * hh(key, g, row, q, "o")) if big else (0.14 + 0.1 * hh(key, g, row, q, "o"))
                    hw_ = max(0.1, ztop - foot(sa))
                    kk_ = 1.25 / max(0.3, 1.0 - 1.3 * max(fo(sa), fo(sb)) / hw_)
                    c = min(pr * kk_, (zz - za) * 0.6)             # chanfro ingreme (o talude deita a pedra)
                    pr = c / kk_

                    zf = zz - c
                    # frente, chanfro de cima, laterais (o plano da junta e o fundo)
                    fA, fB = Pt(sa, op(sa, za) + pr, za), Pt(sb, op(sb, za) + pr, za)
                    fC, fD = Pt(sb, op(sb, zf) + pr, zf), Pt(sa, op(sa, zf) + pr, zf)
                    bA, bB = Pt(sa, op(sa, za), za), Pt(sb, op(sb, za), za)
                    bC, bD = Pt(sb, op(sb, zz), zz), Pt(sa, op(sa, zz), zz)
                    fb.face([fA, fB, fC, fD], WALL, NV)
                    fb.face([fD, fC, bC, bD], WALL, (nx, ny, 1.0))
                    fb.face([fB, bB, bC, fC], WALL, UV)
                    fb.face([bA, fA, fD, bD], WALL, (-ux, -uy, 0.0))
                    if za < zb + 6.0:                                     # fundo so ate a cabeca (visto de baixo)
                        fb.face([bA, bB, fB, fA], WALL, (0.0, 0.0, -1.0))
                    nst += 1
                s = e
                q += 1
    # capa clara (dentro do piso: topo +0,12, frente no labio, sem balanco); sem capa onde o lajeado cobre (so a testa)
    e0, e1 = -0.05, ln + 0.05
    z0, z1 = ztop, zt + 0.12
    fb.face([Pt(e0, 0.0, z0), Pt(e1, 0.0, z0), Pt(e1, 0.0, z1), Pt(e0, 0.0, z1)], PATH, NV)
    gutter(fb, smp, a, ux, uy, nx, ny, ln)
    b0, b1 = base(0.0), base(ln)
    if not cap:
        return nst
    fb.face([Pt(e0, 0.0, z1), Pt(e1, 0.0, z1), Pt(e1, -0.9, z1), Pt(e0, -0.9, z1)], PATH, (0, 0, 1))
    for s_, sg in ((e0, -1), (e1, 1)):
        fb.face([Pt(s_, 0.0, z0), Pt(s_, 0.0, z1), Pt(s_, -0.9, z1), Pt(s_, -0.9, z0)], PATH, (ux * sg, uy * sg, 0))
    return nst


def gutter(fb, smp, a, ux, uy, nx, ny, ln):
    """fresta com guarda: 'G' = canaleta sob o fundo da guarda (testa ate o piso de baixo); 'L' = tampa de pedra sob o
    fundo da guarda de cima + testa na borda de cima"""
    if not (len(smp[0]) > 8 and smp[0][8] is not None):
        return
    for k in range(len(smp) - 1):
        A, B = smp[k], smp[k + 1]
        if A[8][0] == "G":
            P0, P1 = (A[0], A[1]), (B[0], B[1])
            za, zb = A[8][2] - 0.7, B[8][2] - 0.7
            q0 = (A[0] + nx * (A[8][1] + 0.08), A[1] + ny * (A[8][1] + 0.08))
            q1 = (B[0] + nx * (B[8][1] + 0.08), B[1] + ny * (B[8][1] + 0.08))
            fb.face([(q0[0], q0[1], za), (q1[0], q1[1], zb), (q1[0], q1[1], B[5] - 0.02), (q0[0], q0[1], A[5] - 0.02)], WALL,
                    (-nx, -ny, 0))
        else:
            _, x0a, y0a, da, zta, ga = A[8]
            _, x0b, y0b, db, ztb, gb = B[8]
            za, zb = ga - 0.7, gb - 0.7
            if k == 0 or k == len(smp) - 2:                    # tampa passa 1,2 das pontas (fecha a cunha da quina)
                ex, ey = (x0b - x0a), (y0b - y0a)
                el = math.hypot(ex, ey) or 1.0
                ex, ey = ex / el * 1.2, ey / el * 1.2
                if k == 0:
                    x0a, y0a = x0a - ex, y0a - ey
                    A = (A[0] - ex, A[1] - ey) + A[2:]
                if k == len(smp) - 2:
                    x0b, y0b = x0b + ex, y0b + ey
                    B = (B[0] + ex, B[1] + ey) + B[2:]
            fb.face([(x0a, y0a, za), (x0b, y0b, zb), (x0b, y0b, ztb - 0.02), (x0a, y0a, zta - 0.02)], WALL, (nx, ny, 0))


def _steep(rows, lim=0.85):
    """garante que nenhuma faixa entre 2 linhas olhe para cima com normal >= 0,7: o avanco para fora ao descer e no
    maximo 'lim' x a queda (corrige de cima para baixo)"""
    for k in range(1, len(rows)):
        o0, z0 = rows[k - 1]
        o1, z1 = rows[k]
        dz = max(z0 - z1, 0.02)
        if o1 - o0 > lim * dz:
            rows[k] = (o0 + lim * dz, z1)
    return rows


def rock_run(fb, smp, key, tall_rock=False):
    """FACE DE ROCHA facetada: rolo verde no labio, linguas verdes que caem, facetas de 5..11, estrato com labio de
    musgo (curto e ingreme), pe enterrado na borda da placa de baixo; nada avanca sobre o piso de baixo ate a cabeca"""
    pts = [(s_[0], s_[1]) for s_ in smp]
    acc = [0.0]
    for i in range(1, len(pts)):
        acc.append(acc[-1] + math.dist(pts[i - 1], pts[i]))
    tot = acc[-1]
    if tot < 1.0:
        return 0
    ds = [0.0]
    q = 0
    while ds[-1] < tot - 0.01:
        ds.append(min(tot, ds[-1] + 3.0 + 4.0 * hh(key, q, "fs")))
        q += 1
    if len(ds) > 2 and tot - ds[-2] < 2.0:
        ds.pop(-2)
    nodes = []
    for qi, d_ in enumerate(ds):
        j = 0
        while j < len(acc) - 2 and acc[j + 1] < d_:
            j += 1
        sp = (acc[j + 1] - acc[j]) or 1.0
        t = max(0.0, min(1.0, (d_ - acc[j]) / sp))
        s0, s1 = smp[j], smp[j + 1]
        lr = lambda k: s0[k] + (s1[k] - s0[k]) * t
        nodes.append((lr(0), lr(1), s0[2], s0[3], lr(4), lr(5), lr(6), s0[7] or s1[7], qi))
    gutter(fb, smp, smp[0], (smp[-1][0] - smp[0][0]) / max(tot, 1e-6), (smp[-1][1] - smp[0][1]) / max(tot, 1e-6),
           smp[0][2], smp[0][3], tot)
    n = len(nodes)
    cool = hh(key, "cool") > 0.6
    low = ROCKC if cool else ROCK
    R = None
    rows_all, mats_all = [], []
    for i, (x, y, nx, ny, zt, zn, d, walk, qi) in enumerate(nodes):
        h = max(zt - zn, 0.8)
        endf = 0.0 if i in (0, n - 1) else 1.0
        o_up = (0.4 + 2.6 * hh(key, qi, "o")) * endf * (1.0 + min(1.6, h / 16.0))
        if endf and qi % 2 == 1 and hh(key, qi, "fis") > 0.4:
            o_up = -0.6 - 0.6 * hh(key, qi, "fd")              # fissura: o no recua (V escura)
        lim_lo = max(0.0, d - 0.06)
        o_lo = min(o_up, lim_lo) if walk else min(o_up * 1.1, lim_lo + 0.6)
        dr = min(h * 0.38, 0.8 + 3.0 * hh(key, qi, "dr") ** 1.8)
        if h > 8.0 and endf and hh(key, qi, "dr") > 0.62:
            dr = h * (0.26 + 0.18 * hh(key, qi, "dl"))           # lingua verde longa da crista
        zhead = zn + min(6.5, h * 0.55)
        if h > 12.0:
            zl = zn + h * (0.45 + 0.2 * hh(key, "zl")) + (hh(key, qi, "zj") - 0.5) * 2.5
            zl = max(zhead + 1.5, min(zl, zt - dr - 2.0))
            wl = min(0.55, 0.2 + 0.5 * hh(key, qi, "wl")) * endf
            rows = [(0.0, zt - 0.02), (0.2, zt - 0.5), (o_up * 0.8, zt - dr), (o_up, zl + 0.8), (o_up + wl, zl),
                    (o_up + wl * 0.6, zl - 0.7), (max(o_lo, min(o_up, lim_lo + 1.2)), zhead), (o_lo, zn + 0.25),
                    (lim_lo, zn - 0.6)]
            mm = [GDEEP, MOSS, ROCK if hh(key, qi, "t") > 0.3 else ROCKC, ROCK, MOSS if wl > 0.35 else low, low, low,
                  DIRTD if walk else ROCKC]
            if o_up < 0:
                mm = mm[:2] + [CREV] * 4 + mm[6:]
        else:
            rows = [(0.0, zt - 0.02), (0.2, zt - 0.5), (o_up * 0.8, zt - max(0.7, min(dr, h * 0.45))),
                    (max(o_lo, min(o_up, lim_lo + 1.2)), max(zhead, zn + h * 0.5) if zhead < zt - 1.2 else zn + h * 0.5),
                    (o_lo, zn + 0.25), (lim_lo, zn - 0.6)]
            mm = [GDEEP, MOSS, ROCK, low, DIRTD if walk else ROCKC]
        for k in range(1, len(rows)):
            if rows[k][1] > rows[k - 1][1] - 0.05:
                rows[k] = (rows[k][0], rows[k - 1][1] - 0.05)
        # nada sobre o piso de baixo abaixo da cabeca: avanco <= d - 0,06 abaixo de zhead
        rows = [(min(o, lim_lo) if z < zhead + 0.5 else min(o, lim_lo + 1.2), z) for o, z in rows]
        if key.startswith(("Court_Rock_Buttress", "Court_Stair")):
            rows = [(min(o, 0.0), z) for o, z in rows]      # o muro/guarda do castelo assenta na rocha: face rente
        rows = _steep(rows)
        if R is None:
            R = len(rows)
        rows = (rows + [rows[-1]] * R)[:R]
        mm = (mm + [mm[-1]] * R)[:R - 1]
        rows_all.append([(x + nx * o, y + ny * o, z) for o, z in rows])
        mats_all.append(mm)
    nf = 0
    for i in range(n - 1):
        A, B = rows_all[i], rows_all[i + 1]
        nx, ny = nodes[i][2], nodes[i][3]
        for r in range(R - 1):
            pts = [A[r], B[r], B[r + 1], A[r + 1]]
            if math.dist(pts[0], pts[3]) < 1e-3 and math.dist(pts[1], pts[2]) < 1e-3:
                continue
            m = mats_all[i][r] if hh(key, i, r, "mm") > 0.5 else mats_all[i + 1][r]
            fb.face(pts, m, (nx, ny, 0.25))
            nf += 1
    return nf


def spine_run(fb, smp, key):
    """fresta LARGA demais para a queda (cantos entre placas, buraco da planta): espinha de rocha com as 2 encostas
    ingremes (crista acima do pulo so onde precisa), musgo na crista"""
    n = len(smp)
    rows_all = []
    for i, (x, y, nx, ny, zt, zn, d, walk, g) in enumerate(smp):
        hi = max(zt, zn)
        crest = hi + 1.15 * (d / 2.0) + 0.45 + 0.6 * hh(key, i, "c")
        oc = d * (0.45 + 0.1 * hh(key, i, "x"))
        rows = [(0.0, zt - 0.02), (oc, crest), (d + 0.02, zn - 0.5)]
        rows_all.append([(x + nx * o, y + ny * o, z) for o, z in rows])
    for i in range(n - 1):
        A, B = rows_all[i], rows_all[i + 1]
        nx, ny = smp[i][2], smp[i][3]
        for r in range(2):
            m = ROCK if hh(key, i, r) > 0.35 else MOSS
            fb.face([A[r], B[r], B[r + 1], A[r + 1]], m, (0.0, 0.0, 1.0) if r < 2 else (0, 0, 1))
    return n


def guards_at(x, y):
    out = []
    for mi, zb, bb in GUARDS:
        if bb[0] <= x <= bb[2] and bb[1] <= y <= bb[3]:
            q = mi @ Vector((x, y, zb + 0.5))
            if abs(q.x) <= 0.5 and abs(q.y) <= 0.5:
                out.append(zb)
    return out


def slit_lids(fb):
    """TAMPA de toda fresta com guarda (pelos quadrilateros das frestas: cobre ate as cunhas das quinas), logo abaixo do
    fundo da guarda (o gate ve o fundo da guarda como 'piso'; a tampa fica coberta por ela); onde a mesma guarda nao
    cobre a fresta inteira: FUNIL de pedra ingreme e raso (nem piso sem colisao nem fresta funda)"""
    n = 0
    for poly, zl, p, q in PL.fillers:
        if q is None or p.kind == "water" or q.kind == "water" or "Court" in (p.name, q.name):
            continue
        cx = sum(t[0] for t in poly) / len(poly)
        cy = sum(t[1] for t in poly) / len(poly)
        zu, zd = max(p.zf(cx, cy), q.zf(cx, cy)), min(p.zf(cx, cy), q.zf(cx, cy))
        if zu < zd + 0.3:
            continue
        gs = [g_ for g_ in guards_at(cx, cy) if g_ <= zu]
        if not gs:
            continue
        hi = q if q.zf(cx, cy) < p.zf(cx, cy) else p
        lo = p if hi is q else q
        pts = []
        for x, y in poly:
            if lo.has(x, y, 0.02):
                x, y = x + (cx - x) * 0.35, y + (cy - y) * 0.35
            pts.append((x, y))
        common = [g_ for g_ in gs if all(any(abs(g_ - h_) < 0.05 for h_ in guards_at(x + (cx - x) * 0.04, y + (cy - y) * 0.04))
                                         for x, y in pts)]
        if common:
            g = max(common)
            busy = False
            for mi, z0_, z1_, bb in OTHERS:                       # outra colisao (torreao, muro) na fresta: sem tampa
                if bb[0] <= cx <= bb[2] and bb[1] <= cy <= bb[3] and zd + 0.3 < z1_ < g - 0.4:
                    q_ = mi @ Vector((cx, cy, (z0_ + z1_) / 2))
                    if abs(q_.x) <= 0.5 and abs(q_.y) <= 0.5:
                        busy = True
            if busy:
                continue
            fb.face([(x, y, g - 0.7) for x, y in pts], PATH if g > zd + 1.0 else JOINT, (0, 0, 1))
        else:
            continue
        n += 1
    return n


def build_walls():
    guards_load()
    fw = FB("OP_Ter_Walls")
    print("op_terrain: tampas de fresta com guarda %d" % slit_lids(fw))
    cnt = {}
    tri = {}
    for i, (kind, pn, qn, smp) in enumerate(edge_runs()):
        f0 = len(fw.mb.bm.faces)
        key = "%s_%s_%d" % (pn, qn, i)
        cap = pn not in SLABBED
        if kind == "ishi":
            wall_run(fw, smp, False, key, cap)
        elif kind == "big":
            wall_run(fw, smp, True, key, cap)
        elif kind == "rock":
            rock_run(fw, smp, key)
        elif kind == "spine":
            spine_run(fw, smp, key)
        cnt[kind] = cnt.get(kind, 0) + 1
        tri[kind] = tri.get(kind, 0) + 2 * (len(fw.mb.bm.faces) - f0)
    ob = fw.finish()
    print("op_terrain: bordas internas %s tris~%s | %d tris" % (cnt, tri, tris_of(ob)))
    return ob


# ================================================================== 3. FALESIA (cortina continua no contorno exato)
QUAY = ("Harbor", "HarborMid")
FOAM = "Plaster_OP"                 # espuma no pe da falesia (fita clara rente ao mar local)


def massas(tot, key, lo=18.0, hi=60.0):
    """quebra o comprimento em massas de tamanho DIRIGIDO (sem periodo)"""
    out = []
    t, k = 0.0, 0
    while t < tot - lo * 0.6:
        ln = lo + (hi - lo) * hh(key, k, "len") ** 1.3
        out.append((t, min(t + ln, tot)))
        t += ln
        k += 1
    if out:
        out[-1] = (out[-1][0], tot)
    return out


def _edge_info(lp):
    """por aresta do contorno: (z do labio, placa) medido 0,3 para dentro do meio da aresta"""
    n = len(lp)
    out = []
    for i in range(n):
        a, b = lp[i], lp[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = dy / ln, -dx / ln
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        t = None
        for dd in (0.3, 0.8, 1.5):
            t = top_at(mx - nx * dd, my - ny * dd)
            if t:
                break
        if t is None:
            fl = [f for f in PL.fillers if L.point_in_poly(mx - nx * 0.05, my - ny * 0.05, f[0])]
            t = (fl[0][1], fl[0][2]) if fl else (P, None)
        out.append((t[0], t[1], nx, ny, ln))
    return out


def loop_nodes(lp, key):
    """nos da cortina: TODOS os vertices exatos + nos no meio das arestas longas (facetas de 4..9) + FENDAS entre
    massas (2 nos colados, o de dentro recua); vertice com degrau de cota vira 2 nos (mesmo x, y)"""
    ei = _edge_info(lp)
    n = len(lp)
    # comprimento acumulado
    acc = [0.0]
    for i in range(n):
        acc.append(acc[-1] + ei[i][4])
    tot = acc[-1]
    ms = massas(tot, key)
    bounds = [a for a, b in ms[1:]]
    nodes = []
    for i in range(n):
        a, b = lp[i], lp[(i + 1) % n]
        zt, pl, nx, ny, ln = ei[i]
        zp, plp, pnx, pny, pln = ei[i - 1]
        mxn, myn = nx + pnx, ny + pny
        ml = math.hypot(mxn, myn) or 1.0
        mxn, myn = mxn / ml, myn / ml
        k = max(0.5, mxn * nx + myn * ny)
        mxn, myn = mxn / k, myn / k
        mlen = math.hypot(mxn, myn)
        if mlen > 2.0:
            mxn, myn = mxn * 2.0 / mlen, myn * 2.0 / mlen
        if abs(zp - zt) > 0.05:
            nodes.append(dict(x=a[0], y=a[1], nx=mxn, ny=myn, z=zp, pl=plp, d=acc[i], crev=0, step=True))
        nodes.append(dict(x=a[0], y=a[1], nx=mxn, ny=myn, z=zt, pl=pl, d=acc[i], crev=0, step=abs(zp - zt) > 0.05))
        # nos internos da aresta (facetas) + fendas nas fronteiras de massa
        s = 0.0
        q = 0
        marks = []
        while True:
            s += 4.0 + 5.0 * hh(key, i, q, "fs")
            q += 1
            if s > ln - 2.5:
                break
            marks.append((s, 0))
        for bd in bounds:
            if acc[i] + 1.5 < bd < acc[i + 1] - 1.5:
                marks = [m for m in marks if abs(m[0] - (bd - acc[i])) > 1.6]
                marks.append((bd - acc[i] - 0.45, 1))
                marks.append((bd - acc[i] + 0.45, 2))
        # fissuras (V rasa) dentro das massas, a cada ~12..20 (quebra o plano das colunas)
        fz = 6.0 + 8.0 * hh(key, i, "f0")
        while fz < ln - 3.0:
            if all(abs(fz - m_[0]) > 1.4 for m_ in marks if m_[1] in (1, 2)):
                marks = [m_ for m_ in marks if not (m_[1] == 0 and abs(m_[0] - fz) < 1.2)]
                marks.append((fz, 3))
            fz += 12.0 + 8.0 * hh(key, i, fz, "f1")
        for s_, cv in sorted(marks):
            t = s_ / ln
            nodes.append(dict(x=a[0] + (b[0] - a[0]) * t, y=a[1] + (b[1] - a[1]) * t, nx=nx, ny=ny, z=zt, pl=pl,
                              d=acc[i] + s_, crev=cv, step=False))
    # massa / u de cada no
    for nd in nodes:
        k = 0
        for j, (a_, b_) in enumerate(ms):
            if a_ - 1e-6 <= nd["d"] <= b_ + 1e-6:
                k = j
                break
        a_, b_ = ms[k]
        nd["m"] = k
        nd["u"] = (nd["d"] - a_) / max(b_ - a_, 1e-6)
    return nodes, ms


def node_profile(nd, key, keelc):
    """linhas (offset para fora, z) e materiais de cima para baixo"""
    zt, k, u = nd["z"], nd["m"], nd["u"]
    pl = nd["pl"]
    pname = pl.name if pl else ""
    kind = pl.kind if pl else "floor"
    di = round(nd["d"], 1)
    cx, cy = keelc
    NR = 17

    def even(o_top, z_top, o_bot, z_bot, tail, mats):
        """perfil liso com o MESMO numero de linhas do natural (transicao sem quads torcidos)"""
        k = NR - len(tail)
        rows = [(o_top + (o_bot - o_top) * i / (k - 1), z_top + (z_bot - z_top) * i / (k - 1)) for i in range(k)] + tail
        return rows, (mats + [mats[-1]] * NR)[:NR - 1]
    if kind == "water":                                   # boca das quedas da borda: rocha molhada lisa
        return even(0.0, zt, 0.6, SEA + 2.0, [(1.0, SEA - 2.0), (-6.0, 22.0), (-10.0, 14.0)], [DARK])
    if pname in QUAY or zt < 60.0:                        # cais: muralha de pedra (as pedras vem do wall_run)
        return even(-0.12, zt - 0.5, -0.12, SEA + 0.4, [(0.2, SEA - 1.5), (-4.0, 26.0), (-12.0, 14.0)], [JOINT] * 9 + [DARK])
    A = 1.5 + 7.5 * hh(key, k, "A")
    if hh(key, k, "but") > 0.8:
        A *= 1.5
    sharp = 0.45 + 0.6 * hh(key, k, "sh")
    bump = math.sin(math.pi * max(0.0, min(1.0, u))) ** sharp
    jit = (hh(key, k, di, "j") - 0.5) * 2.4 * bump
    tp = nd.get("taper", 1.0)
    if tp < 0.3:                                          # vizinho do cais/queda: face lisa ingreme (transicao sem torcer)
        return even(0.0, zt, 0.3, SEA + 0.4, [(0.6, SEA - 1.5), (-4.0, 26.0), (-12.0, 14.0)],
                    [GDEEP, MOSS] + [ROCKC] * 8 + [DARK])
    bulge = (0.5 + A * bump + jit) * tp
    zr = min(zt, nd.get("zreach", zt)) - REACH_DROP
    # lingua verde da crista: 1 no em ~3 desce longe (6..16), os outros 1..3,5
    hv = hh(key, k, di, "dr")
    dr = (6.0 + 12.0 * hh(key, k, di, "dl")) if (hv > 0.55 and not nd["crev"]) else (2.0 + 2.8 * hv)
    dr = min(dr, max(1.2, zt - zr - 4.0))
    # estrato (prateleira) so abaixo da faixa do pulo; altura e largura proprias por massa; verde em ALMOFADAS
    zl = zr - 0.6 - 7.0 * hh(key, k, "zl")
    wl = (0.6 + 3.2 * hh(key, k, "wl")) * (bump ** 0.6) * tp
    if hh(key, k, "noledge") < 0.3 or zl < SEA + 8.0:
        wl, zl = 0.05, max(SEA + 6.0, min(zl, zr - 0.6))
    green = wl > 1.0 and hh(key, k, di, "lg") > 0.3
    drip = green and hh(key, k, di, "drip") > 0.4
    foot = (1.0 + 3.0 * hh(key, k, "ft")) * max(0.3, tp)
    cool = hh(key, k, "cool") > 0.5
    tone = ROCKC if (cool or hh(key, k, di, "tn") > 0.8) else ROCK
    if not cool and bump > 0.75 and hh(key, k, di, "lt") > 0.55:
        tone = LITE                                       # coluna saliente ao sol
    low = ROCKC if cool else ROCK
    o3 = 0.35 + bulge * 0.35
    o4 = bulge
    zA = zt - dr - 1.4
    zB = max(zr - 0.3, SEA + 9.0)
    om = bulge * (0.72 + 0.36 * hh(key, k, di, "om"))
    rows = [(0.0, zt), (0.3, zt - 0.8), (0.5 + 0.3 * bump, zt - dr), (o3, zA), (om, (zA + zB) / 2), (o4, zB)]
    rows = _steep(rows, 0.5)
    o4 = rows[-1][0]
    zl1 = zl - 1.4 - 2.0 * hh(key, k, di, "l2")
    ol = o4 * (0.85 + 0.3 * hh(key, k, di, "ol")) + 0.6
    # 2o estrato nas falesias altas (fundo do castelo): almofada verde no meio da face
    zl2 = SEA + (zl1 - SEA) * (0.45 + 0.15 * hh(key, k, "z2"))
    wl2 = (0.8 + 2.4 * hh(key, k, "w2")) * (bump ** 0.6) * tp if (zl1 - SEA > 40.0 and hh(key, k, "l2b") > 0.35) else 0.0
    g2 = wl2 > 1.0 and hh(key, k, di, "g2") > 0.3
    rows += [(o4 + wl, zl), (o4 + wl * 0.8 + 0.2, zl1), (ol, zl2 + 1.2), (ol + wl2, zl2), (ol + wl2 * 0.6, zl2 - 2.5),
             (ol * 0.95 + 0.4, zl2 - (zl2 - SEA) * 0.45),
             (o4 + foot * 0.4 + 0.5, SEA + 7.0), (o4 + foot * 0.6 + 0.6, SEA + 3.0), (o4 + foot + 0.8, SEA - 0.6),
             (o4 + foot * 0.4, 26.0), (-6.0 - 8.0 * hh(key, k, "k1"), 14.0)]
    if zr < SEA + 10.0:                                   # piso baixo perto (cais): tudo ingreme ate o mar
        rows = _steep(rows[:14], 0.6) + rows[14:]
    mm = [GDEEP, MOSS, tone, tone, tone, MOSS if green else tone, MOSS if drip else low, low, MOSS if g2 else low,
          MOSS if (g2 and drip) else low, low, ROCKC, DARK, DARK, DARK, DARK]
    nd["foot"] = o4 + foot + 0.8
    nd["ledge"] = (o4 + wl * 0.5, zl, wl, zr) if green else None
    if nd["crev"] in (1, 2):
        # fenda entre massas: recua (para DENTRO da placa) do rolo verde para baixo
        dep = -(1.4 + 1.6 * hh(key, k, di, "cv")) if nd["crev"] == 1 else -(0.9 + 0.8 * hh(key, k, di, "cv"))
        rows = rows[:2] + [(dep, z) for o, z in rows[2:13]] + rows[13:]
        mm = mm[:2] + [CREV] * 11 + mm[13:]
        nd["ledge"] = None
    elif nd["crev"] == 3:
        # fissura: V rasa (metade da saliencia), escura
        rows = rows[:2] + [(min(o * 0.45, -0.3), z) for o, z in rows[2:13]] + rows[13:]
        mm = mm[:2] + [CREV] * 2 + mm[4:]
        nd["ledge"] = None
    if pname.startswith("Rock_") and pname[5:] in ("BackN", "BackE", "NERocksE"):
        mm = [MOSS if m == GDEEP else m for m in mm]
    for kk in range(1, len(rows)):
        if rows[kk][1] > rows[kk - 1][1] - 0.05:
            rows[kk] = (rows[kk][0], rows[kk - 1][1] - 0.05)
    return rows, mm


def build_cliff():
    fb = FB("OP_Ter_Cliff")
    quay_runs = []
    nb_total = 0
    keel_all = []
    for li, lp in enumerate(PL.loops):
        key = "rim%d" % li
        nodes, ms = loop_nodes(lp, key)
        keelc = DL.centroid(lp)
        R = None
        cols = []
        zrs = []
        for nd in nodes:
            zr_ = reach_near(nd["x"] - nd["nx"] * 0.5, nd["y"] - nd["ny"] * 0.5, 7.0, low=True)
            zrs.append(zr_ if zr_ is not None else nd["z"])
        nn_ = len(nodes)
        smooth = lambda i: (nodes[i]["pl"] is None or nodes[i]["pl"].kind == "water" or nodes[i]["pl"].name in QUAY
                            or nodes[i]["z"] < 60.0)
        hard = [d_["d"] for i, d_ in enumerate(nodes) if smooth(i)]
        tot_ = sum(math.hypot(lp[(i + 1) % len(lp)][0] - lp[i][0], lp[(i + 1) % len(lp)][1] - lp[i][1]) for i in range(len(lp)))
        for i, nd in enumerate(nodes):
            nd["zreach"] = min(zrs[(i + k_) % nn_] for k_ in range(-3, 4)) - 1.0
            if hard:
                dd = min(min(abs(nd["d"] - h_), tot_ - abs(nd["d"] - h_)) for h_ in hard)
                nd["taper"] = max(0.0, min(1.0, (dd - 2.0) / 14.0))
        for nd in nodes:
            rows, mm = node_profile(nd, key, keelc)
            tx_, ty_ = -nd["ny"], nd["nx"]
            gs_ = [guard_at(nd["x"] + nd["nx"] * o_ + tx_ * t_, nd["y"] + nd["ny"] * o_ + ty_ * t_)
                   for o_ in (0.4, 1.2, 2.0, 3.0) for t_ in (-3.0, 0.0, 3.0)]
            gs_ = [g_ for g_ in gs_ if g_ is not None and g_ < nd["z"] - 1.0]
            g = min(gs_) if gs_ else None
            if g is not None:
                # labio dentro da guarda de um piso MAIS BAIXO (patio do torii): a face nao avanca ate 6 abaixo
                rows = [(min(o, 0.0) if z > g - 6.0 else o, z) for o, z in rows]
            cols.append((nd, rows, mm))
        R = max(len(r) for _, r, _ in cols)
        P3 = []
        for nd, rows, mm in cols:
            rows = (rows + [rows[-1]] * R)[:R]
            mm = (mm + [mm[-1]] * R)[:R - 1]
            P3.append(([(nd["x"] + nd["nx"] * o, nd["y"] + nd["ny"] * o, z) for o, z in rows], mm))
        n = len(cols)
        for i in range(n):
            j = (i + 1) % n
            A, ma = P3[i]
            B, mb_ = P3[j]
            nd, nd2 = cols[i][0], cols[j][0]
            if abs(nd["x"] - nd2["x"]) < 1e-6 and abs(nd["y"] - nd2["y"]) < 1e-6:
                continue                                  # degrau de cota: a face interna (rock_run) fecha
            ox, oy = (nd["nx"] + nd2["nx"]) / 2, (nd["ny"] + nd2["ny"]) / 2
            for r in range(R - 1):
                pts = [A[r], B[r], B[r + 1], A[r + 1]]
                if math.dist(pts[0], pts[3]) < 1e-4 and math.dist(pts[1], pts[2]) < 1e-4:
                    continue
                m = ma[r] if hh(key, i, r, "mm") > 0.45 else mb_[r]
                if nd["crev"] == 1 and nd2["crev"] == 2 and r >= 2:
                    m = CREV
                fb.face(pts, m, (ox, oy, 0.15))
        # ESPUMA no pe (fita clara rente ao mar, largura irregular) + BLOCOS CAIDOS + ALMOFADAS de musgo nos estratos
        for i in range(n):
            j = (i + 1) % n
            nd, nd2 = cols[i][0], cols[j][0]
            if "foot" not in nd or "foot" not in nd2 or math.hypot(nd["x"] - nd2["x"], nd["y"] - nd2["y"]) < 1e-3:
                continue
            w1, w2 = 0.9 + 1.8 * hh(key, i, "fw"), 0.9 + 1.8 * hh(key, j, "fw")
            za = SEA + 0.2
            pa = [(nd["x"] + nd["nx"] * (nd["foot"] - 0.4), nd["y"] + nd["ny"] * (nd["foot"] - 0.4), za),
                  (nd2["x"] + nd2["nx"] * (nd2["foot"] - 0.4), nd2["y"] + nd2["ny"] * (nd2["foot"] - 0.4), za),
                  (nd2["x"] + nd2["nx"] * (nd2["foot"] + w2), nd2["y"] + nd2["ny"] * (nd2["foot"] + w2), za),
                  (nd["x"] + nd["nx"] * (nd["foot"] + w1), nd["y"] + nd["ny"] * (nd["foot"] + w1), za)]
            fb.face(pa, FOAM, (0, 0, 1))
        for i, (nd, rows, mm) in enumerate(cols):
            if "foot" in nd and not nd["crev"] and hh(key, i, "bl") > 0.8 and nd.get("zreach", 0) > 70.0:
                o = nd["foot"] + 1.5 + 3.5 * hh(key, i, "bo")
                r_ = 1.6 + 3.2 * hh(key, i, "br")
                crag(fb.mb, nd["x"] + nd["nx"] * o, nd["y"] + nd["ny"] * o, r_, SEA - 3.0,
                     SEA + 0.8 + 3.8 * hh(key, i, "bh"), "blk%s%d" % (key, i), steps=1, cap=LITE, m=ROCKC, mlow=DARK,
                     top_tilt=0.2, drape=0.6)
            lg = nd.get("ledge")
            if lg and hh(key, i, "cu") > 0.45 and lg[2] > 1.5:
                o, zl, wl, zr = lg
                r_ = min(2.6, wl * (0.55 + 0.35 * hh(key, i, "cr")))
                top = min(zl + 0.6 + 1.2 * hh(key, i, "ch"), zr - 1.0 - (1.2 + 0.25 * r_))
                if top > zl - 0.2:
                    crag(fb.mb, nd["x"] + nd["nx"] * o, nd["y"] + nd["ny"] * o, r_, zl - 1.0, top, "cush%s%d" % (key, i),
                         steps=1, n=6, cap=GDEEP, m=MOSS, mlow=MOSS, top_tilt=0.1, drape=1.4, sx=1.5,
                         ang=math.atan2(nd["ny"], nd["nx"]) + math.pi / 2)
        # fundo da quilha: leque ate o apice (Tier C, sob o mar local)
        bm = fb.mb.bm
        last = [P3[i][0][-1] for i in range(n)]
        ap = (keelc[0], keelc[1], L.KEEL - 10.0)
        for i in range(n):
            a, b = last[i], last[(i + 1) % n]
            if math.dist(a, b) < 1e-4:
                continue
            fb.face([b, a, ap], DARK, (0, 0, -1))
        # muralha do cais: corridas do contorno com placa de cais (pedras do wall_run por cima do plano escuro)
        cur = []
        for nd in nodes + nodes[:1]:
            pl = nd["pl"]
            isq = pl is not None and pl.kind != "water" and (pl.name in QUAY or nd["z"] < 60.0)
            if isq:
                cur.append(nd)
            elif cur:
                quay_runs.append(cur)
                cur = []
        if cur:
            quay_runs.append(cur)
        keel_all.append(keelc)
        nb_total += len(nodes)
    # pedras aparelhadas do cais (pecas retas entre nos)
    fq = fb
    nst = 0
    for run in quay_runs:
        for a, b in zip(run, run[1:]):
            if math.hypot(b["x"] - a["x"], b["y"] - a["y"]) < 0.6:
                continue
            dx, dy = b["x"] - a["x"], b["y"] - a["y"]
            ln = math.hypot(dx, dy)
            nx, ny = dy / ln, -dx / ln
            smp = [(a["x"], a["y"], nx, ny, a["z"], SEA - 0.3, 0.0, False),
                   (b["x"], b["y"], nx, ny, b["z"], SEA - 0.3, 0.0, False)]
            nst += wall_run(fq, smp, True, "quay%.0f_%.0f" % (a["x"], a["y"]), cap=False)
    ob = fb.finish()
    print("op_terrain: falesia %d nos, %d pedras de cais, %d tris" % (nb_total, nst, tris_of(ob)))
    return ob


# ================================================================== 4. MASSAS: crag (contrato do op_landmarks), picos, agulhas
def crag(mb, cx, cy, r, z0, z1, key, n=None, steps=2, lean=(0.0, 0.0), cap=GDEEP, m=ROCK, mlow=ROCKC, sx=1.0,
         ang=0.0, top_tilt=0.0, drape=1.0, taper=None, cone=False, crev=None):
    """MASSA de rocha facetada (5..8 faces de raio dirigido), em 'steps' estratos que recuam para cima, topo inclinado
    com capa verde que escorre pela face; inclinacao 'lean' (dx, dy por stud). V2-3: o recuo entre estratos e INGREME
    (sobe >= 1,2 x o recuo: nao vira prateleira andavel sem colisao); cone=True afina dentro do estrato; crev=k pinta a
    coluna de faces k de fenda"""
    bm = mb.bm
    if n is None:
        n = (5, 6, 7, 6, 8)[int(hh(key, "n") * 5) % 5]
    rr = [0.78 + 0.4 * hh(key, k, "r") for k in range(n)]
    rot = ang + hh(key, "rot") * 6.28
    base = [(r * sx * rr[k] * math.cos(rot + 2 * math.pi * k / n), r * rr[k] * math.sin(rot + 2 * math.pi * k / n))
            for k in range(n)]
    H_ = z1 - z0
    tdx, tdy = math.cos(rot * 1.7), math.sin(rot * 1.7)
    levels = [z0 + H_ * s / steps for s in range(steps + 1)]
    rings, mats = [], []

    def ring(scale, z, tilt=0.0, dz=None):
        out = []
        for k, (u, v) in enumerate(base):
            zz = z + (tilt * (u * tdx + v * tdy) if tilt else 0.0) + (dz[k] if dz else 0.0)
            out.append(Vector((cx + u * scale + lean[0] * (zz - z0), cy + v * scale + lean[1] * (zz - z0), zz)))
        return out
    sc = 1.0
    rings.append(ring(1.05, z0 - 2.0))
    mats.append(mlow)
    for s in range(steps):
        za, zb_ = levels[s], levels[s + 1]
        rings.append(ring(sc, za + 0.01))
        mats.append(mlow if s == 0 and steps > 1 else m)
        sc2 = sc * ((0.8 + 0.1 * hh(key, s, "st")) if taper is None else taper * (0.94 + 0.12 * hh(key, s, "st")))
        if s < steps - 1:
            rec = r * max(0.0, (sc * (1.06 if cone else 1.0)) - sc2)
            hup = max(0.5, rec * 1.25)
            rings.append(ring(sc2 * 1.06 if cone else sc, zb_ - hup))
            mats.append(MOSS if hh(key, s, "ledge") > 0.5 else m)
            rings.append(ring(sc2, zb_))
            mats.append(m)
        elif cone:
            rings.append(ring(sc2 * 1.03, zb_ - 1.0 - 2.6 * drape))
            mats.append(m)
        sc = sc2
    dz = [-(0.6 + 2.6 * drape * hh(key, k, "d") ** 1.5) for k in range(n)]
    rings.append(ring(sc, z1, top_tilt, dz))
    mats.append(cap)
    rings.append(ring(sc * 0.86, z1 + 0.6, top_tilt))
    mats.append(cap)
    rings.append(ring(sc * 0.55, z1 + 1.0, top_tilt))
    vs = [[bm.verts.new(p) for p in rg] for rg in rings]
    fs_by = {}
    for r_ in range(len(vs) - 1):
        for k in range(n):
            j = (k + 1) % n
            try:
                f = bm.faces.new((vs[r_][k], vs[r_][j], vs[r_ + 1][j], vs[r_ + 1][k]))
            except ValueError:
                continue
            mr = mats[r_]
            if crev is not None and k == crev % n and mr in (m, mlow) and r_ > 0:
                mr = CREV
            fs_by.setdefault(mr, []).append(f)
    try:
        top = bm.faces.new(vs[-1])
        fs_by.setdefault(cap, []).append(top)
    except ValueError:
        pass
    for mm, fl in sorted(fs_by.items()):
        for f in fl:
            f.normal_update()
            c = f.calc_center_median()
            ax, ay = cx + lean[0] * (c.z - z0), cy + lean[1] * (c.z - z0)
            ref = Vector((c.x - ax, c.y - ay, 0.0))
            if abs(f.normal.z) > 0.5:
                ref = Vector((0.0, 0.0, 1.0))
            if f.normal.dot(ref) < -1e-4:
                f.normal_flip()
        assign(mb, fl, mm)


def reach_near(x, y, rad, low=False):
    """maior (low=True: menor) cota de piso/rocha 'walk' a ate 'rad' de (x, y) (amostras em aneis); None se nada"""
    best = None
    for rr in (0.0, rad * 0.35, rad * 0.7, rad):
        k = 1 if rr == 0 else max(8, int(rr * 0.8))
        for i in range(k):
            a = 2 * math.pi * i / k
            t = top_at(x + rr * math.cos(a), y + rr * math.sin(a))
            if t and t[1].kind in ("floor", "stair") or (t and t[1].kind == "rock" and t[1].walk):
                best = t[0] if best is None else (min(best, t[0]) if low else max(best, t[0]))
    return best


def safe_top(x, y, r, zt, extra=None):
    """topo de uma massa decorativa perto de piso alcancavel: ou >= piso + 8,5 (fora do pulo) ou com o PONTO MAIS ALTO
    (topo + capa + inclinacao: 'extra') <= piso - 26 (abaixo da faixa que o gate olha)"""
    extra = (1.2 + 0.25 * r) if extra is None else extra
    zr = reach_near(x, y, r + 6.5)
    if zr is None or zt >= zr + 8.5:
        return zt
    return min(zt, zr - 26.0 - extra)


def peak(mb, cx, cy, r, z0, z1, key, lean=(0.0, 0.0), n=11, neck=0.82, crown=0.98, green=0.16):
    """PICO DE WANO: coluna facetada quase vertical (faces de raio dirigido, 2 fendas escuras), afina ate o 'pescoco' e
    abre numa COROA arredondada coberta de verde que escorre em linguas pela face (ref_02/ref_03); pe largo no mar"""
    bm = mb.bm
    rr = [0.82 + 0.32 * hh(key, k, "r") for k in range(n)]
    rot = hh(key, "rot") * 6.28
    cv = {int(hh(key, "c1") * n) % n, int(hh(key, "c2") * n + n // 2) % n}
    H_ = z1 - z0
    zc = z1 - H_ * green                                # comeco da coroa verde (media)
    crown = min(crown, 1.0)
    prof = [(1.25, z0 - 3.0), (1.12, z0 + H_ * 0.06), (1.0, z0 + H_ * 0.3), (neck * 1.06, z0 + H_ * 0.55),
            (neck, zc - H_ * 0.06), (crown, zc + H_ * 0.03), (crown * 0.97, zc + H_ * 0.09), (crown * 0.82, z1 - H_ * 0.025),
            (crown * 0.5, z1 - H_ * 0.004 - 0.3), (0.0, z1)]
    rings = []
    for j, (sc, z) in enumerate(prof[:-1]):
        row = []
        for k in range(n):
            a = rot + 2 * math.pi * k / n
            rk = r * rr[k] * sc * (0.9 + 0.2 * hh(key, j, k))
            # linguas: a coroa verde desce mais em alguns lados
            zz = z
            tg = hh(key, k, "tongue")
            tdep = H_ * 0.14 * ((tg - 0.55) / 0.45) if tg > 0.55 else 0.0
            if j == 5:
                zz = z - tdep
            if j == 4:
                zz = min(z, prof[5][1] - tdep - 1.5)
            row.append(Vector((cx + rk * math.cos(a) + lean[0] * (zz - z0), cy + rk * math.sin(a) + lean[1] * (zz - z0), zz)))
        rings.append(row)
    topv = Vector((cx + lean[0] * H_, cy + lean[1] * H_, z1))
    vs = [[bm.verts.new(p) for p in rg] for rg in rings]
    tv = bm.verts.new(topv)
    by = {}
    mats = [ROCKC, ROCKC, ROCK, ROCK, ROCK, MOSS, GDEEP, GDEEP]
    for j in range(len(vs) - 1):
        for k in range(n):
            kk = (k + 1) % n
            try:
                f = bm.faces.new((vs[j][k], vs[j][kk], vs[j + 1][kk], vs[j + 1][k]))
            except ValueError:
                continue
            m = mats[j]
            if k in cv and j < 4:
                m = CREV
            if j == 4 and hh(key, k, "tongue") > 0.55:
                m = MOSS                                   # lingua verde que escorre da coroa
            if j == 5 and hh(key, k, "rk") > 0.7:
                m = ROCK                                   # rocha aparece na borda da coroa
            by.setdefault(m, []).append(f)
    for k in range(n):
        try:
            by.setdefault(GDEEP, []).append(bm.faces.new((vs[-1][k], vs[-1][(k + 1) % n], tv)))
        except ValueError:
            pass
    for m, fl in sorted(by.items()):
        for f in fl:
            f.normal_update()
            c = f.calc_center_median()
            ref = Vector((c.x - cx - lean[0] * (c.z - z0), c.y - cy - lean[1] * (c.z - z0), 0.0))
            if abs(f.normal.z) > 0.6:
                ref = Vector((0.0, 0.0, 1.0)) if c.z > zc else ref
            if f.normal.dot(ref) < 0:
                f.normal_flip()
        assign(mb, fl, m)


def _rock_inner_points(nm, r, k, key):
    """k pontos dentro da rocha 'nm' a >= r + 2 da borda (deterministico)"""
    pts = [p for p in L.ROCKS if p[0] == nm][0][1]
    b = _bb(pts)
    out = []
    i = 0
    while len(out) < k and i < 400:
        x = b[0] + (b[2] - b[0]) * hh(key, i, "x")
        y = b[1] + (b[3] - b[1]) * hh(key, i, "y")
        i += 1
        if L.point_in_poly(x, y, pts) and L.poly_edge_dist(x, y, pts) > r + 2.0 and \
                all(math.hypot(x - q[0], y - q[1]) > r * 1.6 for q in out):
            out.append((x, y))
    return out


def build_masses():
    fb = FB("OP_Ter_Rocks")
    mb = fb.mb
    # AGULHAS atras do castelo (moldura da concept, abaixo da torre): picos de Wano (pescoco e coroa verde)
    for i, (x, y, r, zt, lean) in enumerate(((-144.0, 478.0, 12.0, 160.0, (-0.03, 0.03)), (-66.0, 492.0, 18.0, 178.0, (-0.01, 0.02)),
                                            (118.0, 488.0, 16.0, 170.0, (-0.03, 0.02)), (182.0, 454.0, 13.0, 150.0, (0.04, 0.0)),
                                            (240.0, 376.0, 9.5, 134.0, (0.03, -0.01)))):
        peak(mb, x, y, r, 60.0, safe_top(x, y, r * 1.25, zt), "needle%d" % i, lean=lean, n=8 + i % 3,
             neck=0.72 + 0.1 * hh("needle", i), crown=1.0 + 0.18 * hh("needle", i, "c"))
    # PINACULO OESTE (U13: sem pagode), topo 130: pico de Wano de pe no mar a oeste do terraco alto
    px, py, pr, ptop = L.WEST_SPIRE
    peak(mb, px, py, pr * 0.55, 26.0, safe_top(px, py, pr, ptop), "spireW", lean=(-0.03, 0.01), n=12, neck=0.74, crown=0.95,
         green=0.12)
    peak(mb, px - 12.0, py - 20.0, 6.5, 26.0, safe_top(px - 12.0, py - 20.0, 6.5, 96.0), "spireW2", lean=(-0.04, -0.02),
         n=9, neck=0.78, crown=0.95, green=0.12)
    # topo das rochas ALTAS: domos/rochedos para dentro da borda (ninguem chega; a face que da para o piso fica lisa)
    for nm, k, rr_, hz in (("BackN", 3, 11.0, (14.0, 28.0)), ("BackE", 4, 12.0, (12.0, 30.0)), ("NERocksE", 2, 7.0, (6.0, 12.0)),
                           ):
        z0 = [p for p in L.ROCKS if p[0] == nm][0][2]
        for j, (x, y) in enumerate(_rock_inner_points(nm, rr_, k, "top" + nm)):
            h_ = hz[0] + (hz[1] - hz[0]) * hh(nm, j, "h")
            if False:
                pass
            else:
                crag(mb, x, y, rr_, z0 - 0.8, z0 + h_, "top%s%d" % (nm, j), steps=2 if h_ > 8 else 1, top_tilt=0.12,
                     drape=1.6, taper=0.82)
    # CONTRAFORTES do fundo (do mar contra o paredao): grupos de 2, alturas e larguras dirigidas, tops fora do pulo
    for i, (x, y, r, zt) in enumerate(((142.0, 506.0, 22.0, 106.0), (56.0, 514.0, 26.0, 124.0), (-14.0, 512.0, 19.0, 104.0),
                                        (-92.0, 497.0, 24.0, 118.0), (-170.0, 460.0, 20.0, 90.0), (-236.0, 410.0, 17.0, 86.0),
                                        (-246.0, 300.0, 14.0, 70.0), (-232.0, 140.0, 15.0, 64.0))):
        kk = "backbut%d" % i
        r2 = r * (0.6 + 1.0 * hh(kk, "rf"))
        zt2 = 26.0 + (zt - 26.0) * (0.65 + 0.7 * hh(kk, "zf"))
        zt2 = safe_top(x, y, r2 * 1.2, zt2)
        ln_ = (0.0, -0.02 if y > 300 else 0.0)
        if i % 3 == 1:
            ln_ = (0.1 * (1 if hh(kk, "ls") > 0.5 else -1), ln_[1] - 0.04)
        peak(mb, x, y, r2 * 0.8, 26.0, zt2, kk, lean=ln_, n=9 + i % 3, neck=0.78 + 0.12 * hh(kk, "nk"),
             crown=0.9 + 0.1 * hh(kk, "cr"), green=0.14 + 0.06 * hh(kk, "gr"))
        if i % 2 == 0:
            a_ = math.atan2(y - 260.0, x - 0.0) + (math.pi / 2) * (1 if hh(kk, "ss") > 0.5 else -1)
            x2, y2 = x + math.cos(a_) * r2 * 0.85, y + math.sin(a_) * r2 * 0.85
            peak(mb, x2, y2, r2 * 0.5, 26.0, safe_top(x2, y2, r2 * 0.66, 26.0 + (zt2 - 26.0) * (0.62 + 0.25 * hh(kk, "z2"))),
                 kk + "b", n=8, neck=0.85, crown=0.95, green=0.15)
    # ASSENTO DA CAVEIRA (nuca e queixo) e ESPORAO DA ESPADA (crista ate o pinaculo z 100)
    sx_, sy_ = L.SKULL_C
    a = math.radians(L.SKULL_FACE_DEG)
    fx, fy = math.cos(a), math.sin(a)
    crag(mb, sx_ - fx * 14.0, sy_ - fy * 14.0, 17.0, 84.0, 104.0, "skullnape", steps=2, cap=MOSS, m=DARK, mlow=DARK,
         top_tilt=0.15)
    crag(mb, sx_ + fx * 8.0, sy_ + fy * 8.0, 13.0, 82.0, 88.5, "skullchin", steps=1, cap=MOSS, m=DARK, mlow=DARK)
    wx, wy = L.SWORD_POS
    for i, (t, r, z1, st) in enumerate(((0.02, 22.0, 104.0, 2), (0.11, 17.0, 88.0, 2), (0.19, 19.0, 78.0, 2),
                                         (0.28, 15.0, 64.0, 1), (0.36, 18.0, 70.0, 2), (0.45, 16.0, 74.0, 2),
                                         (0.53, 14.0, 60.0, 1), (0.61, 17.0, 64.0, 2), (0.70, 16.0, 76.0, 2),
                                         (0.79, 15.0, 70.0, 1), (0.87, 18.0, 86.0, 2))):
        x_, y_ = 190.0 + (wx - 190.0) * t, 478.0 + (wy - 478.0) * t
        side = (hh("spurside", i) - 0.5) * 8.0
        ax_, ay_ = (wy - 478.0), -(wx - 190.0)
        al = math.hypot(ax_, ay_)
        crag(mb, x_ + ax_ / al * side, y_ + ay_ / al * side, r, 26.0, z1, "spur%d" % i, steps=st, top_tilt=0.14,
             drape=1.5, sx=1.25, ang=math.atan2(wy - 478.0, wx - 190.0), taper=0.78)
    crag(mb, wx, wy, 15.0, 26.0, L.SWORD_ROCK_Z - 18.0, "spurpin0", steps=2, top_tilt=0.0)
    crag(mb, wx, wy, 10.0, L.SWORD_ROCK_Z - 19.0, L.SWORD_ROCK_Z, "spurpin1", steps=1, top_tilt=0.0, n=7, drape=0.6)
    # buraco que sobra da planta (canto T1 x praca, alem das frestas): rochedo de topo fora do pulo
    for h_ in PL.holes:
        cx, cy = DL.centroid(h_)
        rad = max(math.hypot(q[0] - cx, q[1] - cy) for q in h_)
        zr = reach_near(cx, cy, rad + 2.0) or P
        crag(mb, cx, cy, rad * 0.95, zr - 30.0, zr + 9.0, "hole%.0f" % cx, steps=2, top_tilt=0.1, taper=0.85, drape=1.2)
    ob = fb.finish()
    print("op_terrain: massas %d tris" % tris_of(ob))
    return ob


# ================================================================== 5. ROCHEDO DO CASTELO (proa + canal da cachoeira)
# CONTRATO com a arvore (op_tree): ancoras na superficie da rocha onde as raizes agarram
CASTLE_ROCK_TOP = CC
CASTLE_ROCK_ANCHORS = [(73.5, 432.0, CC - 1.0, 1.0, -0.05), (74.2, 440.0, CC - 6.0, 0.98, 0.15),
                       (70.0, 455.0, CC - 3.0, 0.88, 0.47), (66.0, 463.0, CC - 8.0, 0.8, 0.6),
                       (78.0, 446.0, 120.0, 0.0, 0.0), (84.0, 458.0, 120.0, 0.0, 0.0), (60.0, 470.0, CC + 2.0, 0.2, -1.0)]
LIP_FRONT, LIP_BACK, LIP_TOP, LIP_SPOUT = 350.6, 357.6, 132.05, 130.3   # bica: topo plano DENTRO do patio (y >= 352),
                                                                        # ponta em rampa ingreme ate 130,3 (y 350,6)
EXIT_NOTCH = (77.0, 88.4, 10.5, T1 + 0.06 - 0.3 - 0.9 - 0.8 - 0.1)    # (compat. op_exit V1)


def castle_rock_z(x, y):
    """cota do topo da rocha/piso no rochedo do castelo (patio, BackE, BackN) - pura planta"""
    if not PL.plates:
        PL.plates = plan_plates()
    t = top_at(x, y)
    return t[0] if t else None


def build_castle_rock():
    """proa do patio (y 350..358, |x| <= 25): COLUNAS facetadas com recuo proprio, estrato com musgo, linguas verdes da
    crista, FENDAS escuras entre colunas, os 2 PAINEIS dos estandartes (op_castle: hh('cf', i, 'dr'), face 351,75) e o
    CANAL CENTRAL da cachoeira (fundo molhado, boca escura da nascente, bica de pedra). Tudo atras de y 350,3 (o pe nao
    entra na bacia nem sobe na rocha CastleFootW)"""
    fb = FB("OP_Ter_CastleRock")
    mb = fb.mb
    zt = CC
    zb = L.BASIN_Z - 2.6
    YF = 352.0
    YB = YF + 1.0
    ZL = 117.0

    def poly(pts, m, want):
        return fb.face(pts, m, want)

    def box(x0, x1, y0, y1, z0, z1, m, top=None):
        p = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        poly([(x, y, z1) for x, y in p], top or m, (0, 0, 1))
        cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
        for k in range(4):
            a, b = p[k], p[(k + 1) % 4]
            poly([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m,
                 ((a[0] + b[0]) / 2 - cx_, (a[1] + b[1]) / 2 - cy_, 0))
    # paineis dos estandartes (mesma conta do op_castle.banners)
    panels = {1: (-19.5, -12.8), 6: (13.4, 19.5)}
    for i, (xa, xb) in panels.items():
        ya_up, ya_lo = YF - 0.25, YF - 0.6 - 0.3
        dr = 1.4 + 4.2 * hh("cf", i, "dr") ** 1.5
        poly([(xa, YF + 1.2, zt - 0.3), (xb, YF + 1.2, zt - 0.3), (xb, ya_up - 0.15, zt - 0.15), (xa, ya_up - 0.15, zt - 0.15)],
             GDEEP, (0, 0, 1))
        poly([(xa, ya_up - 0.15, zt - 0.15), (xb, ya_up - 0.15, zt - 0.15), (xb, ya_up, zt - dr), (xa, ya_up, zt - dr)], MOSS,
             (0, -1, 0.3))
        poly([(xa, ya_up, zt - dr), (xb, ya_up, zt - dr), (xb, ya_up, ZL + 0.6), (xa, ya_up, ZL + 0.6)], ROCKC, (0, -1, 0))
        poly([(xa, ya_up, ZL + 0.6), (xb, ya_up, ZL + 0.6), (xb, ya_lo, ZL), (xa, ya_lo, ZL)], MOSS, (0, -1, -0.2))
        poly([(xa, ya_lo, ZL), (xb, ya_lo, ZL), (xb, ya_lo, zb), (xa, ya_lo, zb)], ROCKC, (0, -1, 0))
        for x_, sg in ((xa, -1), (xb, 1)):
            poly([(x_, ya_up, zt - dr), (x_, YB, zt - dr), (x_, YB, zb), (x_, ya_lo, zb)], CREV, (sg, 0, 0))
            poly([(x_, ya_up - 0.15, zt - 0.15), (x_, YB, zt - 0.3), (x_, YB, zt - dr), (x_, ya_up, zt - dr)], MOSS, (sg, 0, 0))
    # colunas: (x0, x1, recuo do topo, tom, lado do canal)
    cols = [(-25.4, -20.4, 1.9, ROCK, None), (-12.0, -5.6, 1.1, ROCK, "R"), (5.6, 12.6, 1.4, ROCKC, "L"),
            (20.3, 25.4, 2.1, ROCK, None)]
    for ci, (xa, xb, oa, tone, canal) in enumerate(cols):
        key = "proa%d" % ci
        w = xb - xa
        c = min(1.1, w * 0.2)
        xm = (xa + xb) / 2 + (hh(key, "xm") - 0.5) * w * 0.25
        yf = YF - oa
        zl = ZL + (hh(key, "zl") - 0.5) * 6.0
        ledge = hh(key, "ledge") > 0.35
        yb_l = YF if canal == "L" else YB
        yb_r = YF if canal == "R" else YB
        fx = [xa, xa, xa + c, xm, xb - c, xb, xb]
        base = [yb_l, yf + c, yf, yf - 0.7 - 0.5 * hh(key, "ar"), yf, yf + c, yb_r]
        dr_mid = (zt - zb) * (0.25 + 0.15 * hh(key, "dm"))
        drs = [1.4 + 1.6 * hh(key, j, "d") for j in range(7)]
        drs[3] = dr_mid
        drs[2] = drs[4] = max(drs[2], dr_mid * (0.35 + 0.3 * hh(key, "d2")))
        drs[0], drs[6] = drs[1], drs[5]
        rows_z = [[zt - 0.15] * 7, [zt - 0.9] * 7, [zt - min(d, zt - zl - 2.0) for d in drs], [zl + 0.7] * 7, [zl] * 7,
                  [zl - 1.0] * 7, [zb + 4.0] * 7, [zb - 0.6] * 7]
        rows_dy = [0.7, 0.0, 0.0, 0.3, -0.6 if ledge else -0.2, -0.6 if ledge else -0.2, -1.2, -1.4]
        mats_r = [MOSS, MOSS, tone, MOSS if ledge else tone, tone, ROCKC, DARK]
        V = []
        for zr, dy in zip(rows_z, rows_dy):
            row = []
            for k in range(7):
                y = base[k] + (dy if 0 < k < 6 else 0.0)
                y = max(y, 350.3)                         # o pe nao entra na bacia nem na rocha CastleFootW (y 350)
                row.append((fx[k], y, zr[k]))
            V.append(row)
        for r in range(len(V) - 1):
            for k in range(6):
                q = [V[r][k], V[r][k + 1], V[r + 1][k + 1], V[r + 1][k]]
                side = k == 0 or k == 5
                m = mats_r[r]
                if side and r >= 1:
                    m = DARK if ((k == 0 and canal == "L") or (k == 5 and canal == "R")) else CREV
                cxm = sum(p[0] for p in q) / 4
                cym = sum(p[1] for p in q) / 4
                fb.face(q, m, (cxm - xm, cym - (YB + 0.5), 0.0))
        fb.face([(fx[k], V[0][k][1], zt - 0.15) for k in range(7)] + [(xb, YF + 1.2, zt - 0.3), (xa, YF + 1.2, zt - 0.3)],
                GDEEP, (0, 0, 1))
    for xa, xb in ((-20.4, -19.5), (-12.8, -12.0), (12.6, 13.4), (19.5, 20.3)):
        poly([(xa, YB, zb), (xb, YB, zb), (xb, YB, zt - 0.3), (xa, YB, zt - 0.3)], CREV, (0, -1, 0))
        poly([(xa, YB, zt - 0.3), (xb, YB, zt - 0.3), (xb, YF + 1.2, zt - 0.3), (xa, YF + 1.2, zt - 0.3)], GDEEP, (0, 0, 1))
    # bloco caido no pe (sobre a rocha alta CastleFootE: dentro da colisao)
    crag(mb, 22.8, 349.4, 2.1, 103.6, 106.9, "proafall1", steps=1, top_tilt=0.25, cap=MOSS, m=ROCKC, mlow=DARK, drape=0.6)
    # CANAL CENTRAL: fundo molhado escuro recuado (y 355), boca escura da nascente, bica de pedra
    poly([(-5.6, 355.0, zb), (5.6, 355.0, zb), (5.6, 355.0, 128.4), (-5.6, 355.0, 128.4)], DARK, (0, -1, 0))
    for x_ in (-5.6, 5.6):
        poly([(x_, 352.0, zb), (x_, 355.0, zb), (x_, 355.0, zt - 0.3), (x_, 352.0, zt - 0.3)], DARK, (-x_, 0, 0))
    poly([(-3.4, 357.6, 128.4), (3.4, 357.6, 128.4), (3.4, 357.6, 134.0), (-3.4, 357.6, 134.0)], VOID, (0, -1, 0))
    for x_ in (-3.4, 3.4):
        poly([(x_, 355.0, 128.4), (x_, 357.6, 128.4), (x_, 357.6, 134.0), (x_, 355.0, 134.0)], DARK, (-x_, 0, 0))
    poly([(-3.4, 355.0, 134.0), (3.4, 355.0, 134.0), (3.4, 357.6, 134.0), (-3.4, 357.6, 134.0)], DARK, (0, 0, -1))
    poly([(-5.6, 355.0, 128.4), (-3.4, 355.0, 128.4), (-3.4, 355.0, 134.0), (-5.6, 355.0, 134.0)], DARK, (0, -1, 0))
    poly([(3.4, 355.0, 128.4), (5.6, 355.0, 128.4), (5.6, 355.0, 134.0), (3.4, 355.0, 134.0)], DARK, (0, -1, 0))
    poly([(-5.6, 355.0, 134.0), (5.6, 355.0, 134.0), (5.6, 355.0, zt - 0.3), (-5.6, 355.0, zt - 0.3)], DARK, (0, -1, 0))
    poly([(-5.6, 352.0, zt - 0.3), (5.6, 352.0, zt - 0.3), (5.6, 355.0, zt - 0.3), (-5.6, 355.0, zt - 0.3)], MOSS, (0, 0, 1))
    # bica: corpo dentro do patio (topo plano 132,05, y >= 352) e PONTA EM RAMPA ingreme ate a frente (y 350,6)
    x0, x1 = -4.2, 4.2
    poly([(x0, 352.0, LIP_TOP), (x1, 352.0, LIP_TOP), (x1, LIP_BACK, LIP_TOP), (x0, LIP_BACK, LIP_TOP)], DARK, (0, 0, 1))
    poly([(x0, LIP_FRONT, LIP_SPOUT), (x1, LIP_FRONT, LIP_SPOUT), (x1, 352.0, LIP_TOP), (x0, 352.0, LIP_TOP)], DARK,
         (0, -1, 1))
    poly([(x0, LIP_FRONT, 131.0 - 0.6), (x1, LIP_FRONT, 131.0 - 0.6), (x1, LIP_FRONT, LIP_SPOUT), (x0, LIP_FRONT, LIP_SPOUT)],
         STONE, (0, -1, 0))
    for x_ in (x0, x1):
        poly([(x_, LIP_FRONT, 130.4), (x_, LIP_BACK, 130.4), (x_, LIP_BACK, LIP_TOP), (x_, 352.0, LIP_TOP),
              (x_, LIP_FRONT, LIP_SPOUT)], STONE, (x_, 0, 0))
    poly([(x0, LIP_FRONT, 130.4), (x1, LIP_FRONT, 130.4), (x1, LIP_BACK, 130.4), (x0, LIP_BACK, 130.4)], STONE, (0, 0, -1))
    ob = fb.finish()
    print("op_terrain: rochedo do castelo %d tris" % tris_of(ob))
    return ob


# ================================================================== limpeza do blockout (marcos ainda em blockout)
def strip_blockout():
    """o pinaculo oeste e a crista do esporao sao do TERRENO (V2-3): tira do OP_Lmk_Blockout as rochas (e o pinheiro do
    pinaculo) que ficariam dentro dos picos daqui; a caveira, o pedestal dela e a ESPADA ficam"""
    ob = bpy.data.objects.get("OP_Lmk_Blockout")
    if not ob:
        return 0
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    px, py = L.WEST_SPIRE[0], L.WEST_SPIRE[1]
    wx, wy = L.SWORD_POS
    kill = []
    for f in bm.faces:
        mt = me.materials[f.material_index].name if f.material_index < len(me.materials) else ""
        if not mt.startswith(("Cliff_OP", "Leaf", "Bark")):
            continue
        c = ob.matrix_world @ f.calc_center_median()
        if math.hypot(c.x - L.SKULL_C[0], c.y - L.SKULL_C[1]) < 48.0:
            continue
        near_spire = math.hypot(c.x - px, c.y - py) < 30.0
        near_spur = L.seg_dist(c.x, c.y, 190.0, 478.0, wx, wy)[0] < 26.0 and c.z <= L.SWORD_ROCK_Z + 0.5
        if near_spire or near_spur:
            kill.append(f)
    bmesh.ops.delete(bm, geom=kill, context="FACES")
    bm.to_mesh(me)
    bm.free()
    return len(kill)


# ------------------------------------------------------------------ cameras de revisao da zona
CAMS = {
    "CAM_OPTer_CastleRock": ((-14.0, 262.0, 118.0), (0.0, 352.0, 117.0), 30),
    "CAM_OPTer_PH_Forecourt": ((-10.0, 330.0, CF + 5.5), (0.0, 352.0, 124.0), 20),
    "CAM_OPTer_PH_CastleStair": ((-71.0, 344.0, CF + 7.0), (-64.0, 400.0, 126.0), 22),
    "CAM_OPTer_PH_WallW3": ((-80.0, 262.0, P + 5.5), (-118.0, 306.0, P + 3.0), 22),
    "CAM_OPTer_PH_T1P": ((-40.0, 104.0, T1 + 5.5), (-10.0, 118.0, T1 + 2.0), 22),
    "CAM_OPTer_PH_Harbor": ((176.0, 66.0, L.HARBOR + 5.5), (160.0, 104.0, L.HMID), 22),
    "CAM_OPTer_PH_EdgeS": ((-120.0, 44.0, T1 + 5.5), (-60.0, 30.0, T1 - 4.0), 24),
    "CAM_OPTer_PH_EdgeW": ((-217.0, 146.0, P + 5.5), (-228.0, 230.0, P - 5.0), 24),
    "CAM_OPTer_PH_W3Spire": ((-170.0, 360.0, W3Z + 5.5), (-246.0, 380.0, 112.0), 24),
    "CAM_OPTer_PH_NE": ((150.0, 300.0, P + 5.5), (215.0, 345.0, 108.0), 24),
    "CAM_OPTer_NE": ((120.0, 250.0, 140.0), (210.0, 335.0, 105.0), 26),
    "CAM_OPTer_CanalW": ((-140.0, 205.0, 112.0), (-176.0, 200.0, 90.0), 24),
    "CAM_OPTer_PH_CanalBridge": ((-160.0, 166.0, P + 5.5), (-176.0, 186.0, P + 0.5), 22),
    "CAM_OPTer_CliffSW": ((-330.0, -40.0, 60.0), (-160.0, 70.0, 64.0), 24),
    "CAM_OPTer_CliffFront": ((-80.0, -110.0, 52.0), (-20.0, 20.0, 70.0), 24),
    "CAM_OPTer_CliffBack": ((-40.0, 720.0, 110.0), (-20.0, 470.0, 100.0), 24),
    "CAM_OPTer_CliffW": ((-420.0, 260.0, 90.0), (-220.0, 260.0, 80.0), 26),
    "CAM_OPTer_Spur": ((380.0, 470.0, 110.0), (240.0, 540.0, 70.0), 26),
    "CAM_OPTer_Enseada": ((300.0, 40.0, 70.0), (250.0, 240.0, 70.0), 24),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        camera(n, loc, tgt, lens)


# ------------------------------------------------------------------ build
def build():
    noise.seed_set(5521)
    guards_load()
    plan_prepare()
    print("op_terrain: placas %d, frestas %d, contornos %d, buracos %d" % (len(PL.plates), len(PL.fillers), len(PL.loops),
                                                                        len(PL.holes)))
    build_ground()
    build_walls()
    build_cliff()
    build_castle_rock()
    build_masses()
    print("op_terrain: blockout dos marcos sem pinaculo/esporao: %d faces" % strip_blockout())
    cams()
