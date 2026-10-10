# op_water - ZONA WATER da Ilha 5 (ONE PIECE / WANO), V2-3 (PLANO_V2 secoes 2, 8 e 9). build() substitui
# op_blockout.water. Prefixo OP_Water_, colecao 07_WATER; peca movel VFX_OP_Wheel (12_VFX_HELPERS; pivot/axis/rpm ->
# tag IlhaMovel). Sem luz. A AGUA e do Roblox (laminas/espelho feitos dos marcadores FX_*/WATER_* que este modulo
# regrava: water_markers(), aplicado pelo op_core._water_measured quando a zona 'water' esta detalhada).
# PLANTA V2 (op_layout): canais REBAIXADOS - agua 89,6 (praca/NE) e 85,6 (bairro), leito colidivel 1,0 abaixo
# (op_col.water_beds: o visual do leito fica NA COTA da colisao), capa (mureta) de 0,9 so onde a margem e piso e FORA
# das pontes em arco (op_col.coping_runs: o visual da capa e EXATAMENTE a caixa de colisao dela); bacia do adro 97,6
# (leito 96,6); lago do santuario NE.
# REGRAS do gate 'visual' seguidas aqui: nada andavel sem colisao - o leito e a capa casam com a colisao; o degrau
# entre niveis de agua e uma CALHA ingreme (nao escada de patamares soltos); a fresta entre a capa e a borda do piso e
# um TALUDE de pedra ingreme (sobe do piso ate a quina de fora da capa).
#   1. CANAIS: leito de seixos escuros, muro de cantaria em fiadas da agua ate a capa (face 0,12 dentro do vao), capa
#      de pedra clara em pecas de 1,8..3,2 (juntas rebaixadas), talude ate o piso, calhas dos degraus (FX_Weir_*).
#   2. PONTES EM ARCO do kit2 (op_kit2.bridge2) nas 2 travessias do canal oeste, no envelope do op_col.arch_bridge
#      (vao de 17,2 entre os pes, encontros fora do canal, topo P + 1,4).
#   3. BACIA do adro: leito, cantaria nas bordas (sob a mureta do op_castle), pedras molhadas ao pe da cachoeira.
#   4. QUEDAS da borda (oeste y 54 / leste y 301): soleira de pedra (bica) com bochechas, pedras de base no mar.
#   5. RODA D'AGUA (VFX_OP_Wheel, eixo T1 + 1,9, pas mergulham ~2 na agua 85,6) com cavaletes nas capas e envelope
#      de colisao (peca movel: ninguem sobe nela); poco no leito sob a roda.
#   6. LAGO do santuario NE: borda de pedra rente e leito.
import math, zlib
import bmesh
import bpy
from mathutils import Vector
import op_lib as DL
from op_lib import MB, ccw, camera, yaw_to, Frame, col_box
import op_layout as L
import op_col

C = "07_WATER"
T1, P, CF, CC, SEA = L.T1, L.P, L.CF, L.CC, L.SEA
WALL, CAP, WET, PEB = "Stone_OP_Wall", "Stone_OP_Path", "Stone_OP_Dark", "Dirt_OP_Dark"
RDARK, RCOOL, MOSS = "Cliff_OP_Dark", "Cliff_OP_Shade", "Cliff_OP_Moss"
WOODD, WOOD, IRON = "Wood_OP_Dark", "Wood_OP_Mid", "Metal_OP_Iron"
DROP, BED = L.CANAL_DROP, L.CANAL_BED
LV_CF, LV_P, LV_T1 = CF - 0.6, P - DROP, T1 - DROP          # 97,6 / 89,6 / 85,6
COPE_H, COPE_W = L.CANAL_COPE_H, L.CANAL_COPE_W
WX, WY, WD, WW = L.WHEEL
WR = WD / 2.0
AXZ = L.WHEEL_AXLE_Z
RPM = 4.0
LIP_W_Y, LIP_E_Y = L.FALL_W[1] - 0.8, L.FALL_E[1] - 0.8      # ponta das bicas (0,8 alem do fim do leito)
SPRING = (L.SPRING_W[0], 298.6, L.SPRING_W[2])


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


class FB:
    def __init__(self, name, coll=C, detail="far"):
        self.mb = MB(name, coll, None, detail=detail, floor=-999)
        self.by = {}

    def face(self, pts, m, want=None):
        bm = self.mb.bm
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

    def box(self, x0, x1, y0, y1, z0, z1, m, top=None, bottom=False, ang=0.0, c=(0.0, 0.0)):
        ca, sa = math.cos(ang), math.sin(ang)
        T = lambda x, y: (c[0] + x * ca - y * sa, c[1] + x * sa + y * ca)
        p = [T(x0, y0), T(x1, y0), T(x1, y1), T(x0, y1)]
        self.face([(x, y, z1) for x, y in p], top or m, (0, 0, 1))
        if bottom:
            self.face([(x, y, z0) for x, y in p], m, (0, 0, -1))
        cx, cy = sum(q[0] for q in p) / 4, sum(q[1] for q in p) / 4
        for k in range(4):
            a, b = p[k], p[(k + 1) % 4]
            self.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m,
                      ((a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy, 0))

    def prism(self, poly, z0, z1, m, top=None):
        pl = ccw(poly)
        self.face([(x, y, z1) for x, y in pl], top or m, (0, 0, 1))
        n = len(pl)
        for i in range(n):
            a, b = pl[i], pl[(i + 1) % n]
            self.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], m,
                      (b[1] - a[1], a[0] - b[0], 0))

    def finish(self):
        for m in sorted(self.by):
            fl = [f for f in self.by[m] if f.is_valid]
            mi = self.mb._mi(m)
            for f in fl:
                f.normal_update()
                f.material_index = mi
                f[self.mb.tint] = 0.0
                f.smooth = False
            self.mb._uv(fl, m)
        return self.mb.finish(recalc=False)


def tris_of(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons) if ob else 0


# ------------------------------------------------------------------ 1. canais
def beds(fb):
    """leito NA COTA da colisao (op_col.water_beds): seixos escuros com 'pedras' claras soltas (faces da mesma placa)"""
    n = 0
    for nm, pts, zb in op_col.water_polys():
        fb.prism(ccw(pts), zb - 1.2, zb, RDARK, top=PEB)
        n += 1
    return n


def copings(fb):
    """capa = a caixa de colisao do op_col.copings (mesmo eixo, mesma largura, topo na margem + 0,9), em pecas de
    1,8..3,2 com junta rebaixada; muro de cantaria do leito ate a capa (face 0,12 dentro do vao, fiadas desencontradas);
    TALUDE ingreme de pedra da borda do piso ate a quina de fora da capa (fecha a fresta sem chao sem colisao)"""
    n = 0
    gaps = []
    for k, (a, b, zb, nrm) in enumerate(op_col.coping_runs()):
        if zb is None:
            continue
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        if ln < 0.3:
            continue
        ux, uy = dx / ln, dy / ln
        nx, ny = nrm                                       # para o canal
        P_ = lambda s, o, z: (a[0] + ux * s + nx * o, a[1] + uy * s + ny * o, z)
        hw = COPE_W / 2
        ztop = zb + COPE_H
        # pecas da capa
        s = 0.0
        q = 0
        while s < ln - 0.05:
            e = min(ln, s + 2.6 + 1.6 * hh("cp", k, q))
            if ln - e < 0.9:
                e = ln
            sa, sb = s + (0.04 if s > 0 else 0.0), e - (0.04 if e < ln else 0.0)
            fb.face([P_(sa, -hw, ztop), P_(sb, -hw, ztop), P_(sb, hw, ztop), P_(sa, hw, ztop)], CAP, (0, 0, 1))
            fb.face([P_(sa, hw, ztop), P_(sb, hw, ztop), P_(sb, hw, ztop - 0.45), P_(sa, hw, ztop - 0.45)], CAP, (nx, ny, 0))
            for s_, sg in ((sa, -1), (sb, 1)):
                fb.face([P_(s_, -hw, ztop - 0.45), P_(s_, hw, ztop - 0.45), P_(s_, hw, ztop), P_(s_, -hw, ztop)], CAP,
                        (ux * sg, uy * sg, 0))
            s, q = e, q + 1
        # junta entre pecas (fundo escuro rebaixado)
        fb.face([P_(0, -hw + 0.05, ztop - 0.12), P_(ln, -hw + 0.05, ztop - 0.12), P_(ln, hw - 0.05, ztop - 0.12),
                 P_(0, hw - 0.05, ztop - 0.12)], WET, (0, 0, 1))
        # muro do canal: do leito ate a capa, 0,12 para dentro do vao (cantaria em fiadas)
        zbed = zb - DROP - BED
        ow = hw + 0.12
        zt_w = ztop - 0.45
        fb.face([P_(0, ow - 0.25, zbed - 0.5), P_(ln, ow - 0.25, zbed - 0.5), P_(ln, ow - 0.25, zt_w), P_(0, ow - 0.25, zt_w)],
                WET, (nx, ny, 0))
        z = zbed - 0.3
        r = 0
        while z < zt_w - 0.2:
            z1 = min(zt_w, z + 1.1 + 0.6 * hh("cr", k, r))
            if zt_w - z1 < 0.4:
                z1 = zt_w
            s = -0.7 * hh("co", k, r) if r % 2 else 0.0
            j = 0
            while s < ln - 0.05:
                e = min(ln, s + 2.4 + 1.8 * hh("cw", k, r, j))
                sa, sb = max(0.0, s) + 0.06, e - 0.06
                if sb - sa > 0.3:
                    zf = z1 - 0.42                             # topo da pedra CHANFRADO (ingreme: nao e piso)
                    fb.face([P_(sa, ow, z + 0.05), P_(sb, ow, z + 0.05), P_(sb, ow, zf), P_(sa, ow, zf)], WALL, (nx, ny, 0))
                    fb.face([P_(sa, ow, zf), P_(sb, ow, zf), P_(sb, ow - 0.25, z1 - 0.05), P_(sa, ow - 0.25, z1 - 0.05)],
                            WALL, (nx, ny, 0.6))
                    for s_, sg in ((sa, -1), (sb, 1)):
                        fb.face([P_(s_, ow - 0.25, z + 0.05), P_(s_, ow, z + 0.05), P_(s_, ow, zf),
                                 P_(s_, ow - 0.25, z1 - 0.05)], WALL, (ux * sg, uy * sg, 0))
                s, j = e, j + 1
            z, r = z1, r + 1
        # fresta capa -> piso (lado de fora): mede a borda do piso ao longo da capa
        for t0 in [i * 1.0 for i in range(int(ln) + 1)]:
            t1 = min(ln, t0 + 1.0)
            if t1 - t0 < 0.2:
                continue
            ds = []
            for t in (t0, t1):
                d = 0.0
                while d < 3.0:
                    x, y, _ = P_(t, -hw - d - 0.05, 0)
                    if L.zone_of(x, y) is not None:
                        break
                    d += 0.1
                ds.append(d)
            if max(ds) < 0.12 or max(ds) >= 3.0:
                continue
            gaps.append(max(ds))
            za0 = L.zone_of(*P_(t0, -hw - ds[0] - 0.15, 0)[:2]) or zb
            za1 = L.zone_of(*P_(t1, -hw - ds[1] - 0.15, 0)[:2]) or zb
            fb.face([P_(t0, -hw - ds[0], za0 - 0.02), P_(t1, -hw - ds[1], za1 - 0.02), P_(t1, -hw, ztop - 0.02),
                     P_(t0, -hw, ztop - 0.02)], WALL, (-nx, -ny, 1.0))
        n += 1
    if gaps:
        print("op_water: taludes capa->piso %d (fresta max %.2f)" % (len(gaps), max(gaps)))
    return n


def chutes(fb):
    """degraus entre niveis: PAREDE de soleira na quina da colisao dos leitos (x 95 leste, y 116 oeste); a agua cai
    por cima (FX_Weir_*). Sem rampa: a rampa ficava sobre o leito de baixo (corpo dentro do modelo no gate)"""
    w = L.CANAL_E_W / 2 + 0.2
    y = 342.0
    z0, z1 = LV_CF - BED, LV_P - BED - 0.3
    fb.face([(95.0, y - w, z0), (95.0, y + w, z0), (95.0, y + w, z1), (95.0, y - w, z1)], WET, (1, 0, 0))
    w = (L.CANAL_W_X[1] - L.CANAL_W_X[0]) / 2 + 0.2
    x = -174.0
    z0, z1 = LV_P - BED, LV_T1 - BED - 0.3
    fb.face([(x - w, 116.0, z0), (x + w, 116.0, z0), (x + w, 116.0, z1), (x - w, 116.0, z1)], WET, (0, -1, 0))


def lips(fb):
    """bicas das quedas da borda: soleira de pedra molhada em balanco 0,8 alem do fim do leito + 2 bochechas"""
    for (x, y, zt, zb), hw in ((L.FALL_W, 4.0), (L.FALL_E, 3.0)):
        zbed = zt - BED
        fb.box(x - hw, x + hw, y - 0.8, y + 1.5, zbed - 1.2, zbed + 0.05, WET, bottom=True)


def basin(fb):
    """bacia do adro: leito (beds), cantaria nas bordas de frente e lados (sob a mureta do op_castle), pedras molhadas
    no pe da cachoeira (topo ingreme, abaixo da agua)"""
    B = ccw(L.BASIN)
    n = len(B)
    zbed = L.BASIN_Z - BED
    for k in range(n):
        a, b = B[k], B[(k + 1) % n]
        if min(a[1], b[1]) > 349.0:
            continue
        if max(a[0], b[0]) > 15.0 and min(a[1], b[1]) < 345.6 and max(a[1], b[1]) > 338.6:
            continue                                     # boca do canal leste
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy)
        nx, ny = dy / ln, -dx / ln                       # para fora
        P_ = lambda s, o, z: (a[0] + dx / ln * s + nx * o, a[1] + dy / ln * s + ny * o, z)
        z = zbed - 0.3
        r = 0
        while z < CF - 0.45:
            z1 = min(CF - 0.35, z + 0.8 + 0.3 * hh("bs", k, r))
            fb.face([P_(0, -0.12, z), P_(ln, -0.12, z), P_(ln, -0.12, z1), P_(0, -0.12, z1)], WALL if r % 2 else WET,
                    (-nx, -ny, 0))
            z, r = z1, r + 1
    for i, (x, y, rx, ry, h) in enumerate(((-9.6, 348.4, 2.0, 1.4, 1.0), (9.8, 348.6, 1.8, 1.3, 0.8), (-4.6, 347.8, 1.2, 0.9, 0.6),
                                           (5.0, 348.2, 1.3, 0.9, 0.5))):
        rock(fb, x, y, rx, ry, zbed - 0.4, LV_CF - 0.25 + 0.0 * h, RDARK, "bas%d" % i)


def rock(fb, x, y, rx, ry, z0, z1, m, key, k=7):
    """pedra facetada de topo arredondado (ingreme: nada de patamar)"""
    bm = fb.mb.bm
    rot = 2 * math.pi * hh(key, "r")
    h = z1 - z0
    rings = [(1.0, z0), (0.95, z0 + h * 0.55), (0.55, z1 - h * 0.1)]
    vs = []
    for j, (sc, z) in enumerate(rings):
        row = []
        for i in range(k):
            a = rot + 2 * math.pi * i / k
            f = sc * (0.85 + 0.25 * hh(key, j, i))
            row.append(bm.verts.new((x + math.cos(a) * rx * f, y + math.sin(a) * ry * f, z)))
        vs.append(row)
    top = bm.verts.new((x, y, z1))
    fl = []
    for j in range(len(vs) - 1):
        for i in range(k):
            try:
                fl.append(bm.faces.new((vs[j][i], vs[j][(i + 1) % k], vs[j + 1][(i + 1) % k], vs[j + 1][i])))
            except ValueError:
                pass
    for i in range(k):
        try:
            fl.append(bm.faces.new((vs[-1][i], vs[-1][(i + 1) % k], top)))
        except ValueError:
            pass
    for f in fl:
        f.normal_update()
        c = f.calc_center_median()
        if (Vector((c.x - x, c.y - y, (c.z - z0) * 0.3))).dot(f.normal) < 0:
            f.normal_flip()
    fb.by.setdefault(m, []).extend(fl)


def sea_rocks(fb):
    for i, (x, y, rx, ry) in enumerate(((-181.0, 47.0, 4.2, 3.4), (-167.0, 46.0, 3.8, 3.0), (-174.0, 43.0, 2.4, 1.9),
                                        (241.6, 295.0, 3.4, 2.8), (255.6, 294.6, 3.6, 2.9), (248.5, 292.0, 2.2, 1.7))):
        rock(fb, x, y, rx, ry, SEA - 4.0, SEA + 2.5 + 2.5 * hh("sr", i), RDARK if i % 2 else RCOOL, "sr%d" % i)


def pond(fb):
    (x0, y0, x1, y1), pz = L.NE_POND
    lk = L.NE_POND_LINK
    for (bx0, by0, bx1, by1) in ((x0 - 1.0, y0 - 1.0, x1 + 1.0, y0), (x0 - 1.0, y1, lk[0], y1 + 1.0),
                                 (lk[2], y1, x1 + 1.0, y1 + 1.0), (x0 - 1.0, y0, x0, y1), (x1, y0, x1 + 1.0, y1),
                                 (lk[0] - 1.0, y1, lk[0], lk[3] - 0.6), (lk[2], y1, lk[2] + 1.0, lk[3] - 0.6)):
        fb.prism(ccw(L.rect_poly((bx0, by0, bx1, by1))), P - 1.6, P + 0.3, WALL, top=CAP)


# ------------------------------------------------------------------ 2. pontes em arco (kit2)
def bridges(mb):
    import op_kit2 as K2
    n = 0
    for nm, a, b, w in L.bridge_list():
        if nm not in L.BRIDGE_ARCH:
            continue
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        F = Frame(cx, cy, a[2], ang)
        span = ln - 2 * 2.2
        width = w + 0.7                                  # guarda-corpo do kit em cima da guarda do op_col (y +-5,3)
        rise = L.BRIDGE_ARCH[nm]
        K2.bridge2(mb, F, span=span, width=width, rise=rise, bank_z=0.0, water_z=-DROP, bed_z=-DROP - BED)
        # colisao do guarda-corpo do kit (2,6 sobre o tabuleiro curvo): caixa ALTA (8,9: o topo dela nao vira degrau)
        Lh = span / 2 + 2.2
        zd = lambda x: rise * max(0.0, 1.0 - (x / Lh) ** 2) ** 0.85 + 0.05
        for sy in (-1, 1):
            for k in range(6):
                xa, xb = -Lh + 2 * Lh * k / 6, -Lh + 2 * Lh * (k + 1) / 6
                zt = max(zd(xa), zd(xb), zd((xa + xb) / 2)) + L.GUARD_V2 + 0.4   # alta: ninguem sobe nela
                c = F.p((xa + xb) / 2, sy * (width / 2 - 0.05), (zt - 0.4) / 2)
                col_box("OP_WaterBridgeRail", (xb - xa + 0.1, 0.62, zt + 0.4), (c.x, c.y, a[2] + (zt - 0.4) / 2), (0, 0, ang))
        n += 1
    return n


# ------------------------------------------------------------------ 3. roda d'agua
def wheel_static(fb):
    """cavaletes de madeira sobre as capas (x -178,9 / -169,1), mancais; poco no leito sob a roda"""
    for sx in (L.CANAL_W_X[0] - 0.8, L.CANAL_W_X[1] + 0.8):
        zc = T1 + COPE_H
        fb.box(sx - 0.7, sx + 0.7, WY - 1.8, WY + 1.8, zc - 0.05, zc + 0.4, CAP, bottom=True)
        for s in (-1, 1):
            p0 = Vector((sx, WY + s * 1.5, zc + 0.4))
            p1 = Vector((sx, WY + s * 0.4, AXZ - 0.9))
            beam(fb, p0, p1, 0.42, WOODD)
        fb.box(sx - 0.5, sx + 0.5, WY - 0.75, WY + 0.75, AXZ - 1.0, AXZ - 0.3, WOOD, bottom=True)
        fb.box(sx - 0.32, sx + 0.32, WY - 0.62, WY + 0.62, AXZ + 0.48, AXZ + 0.62, IRON, bottom=True)
    # poco no leito (a pa passa 0,5 acima do fundo)
    hw = (L.CANAL_W_X[1] - L.CANAL_W_X[0]) / 2 - 0.05
    zb = LV_T1 - BED
    zp = AXZ - WR - 0.5
    fb.box(-174.0 - hw, -174.0 + hw, WY - 7.2, WY + 7.2, zp - 0.3, zp, PEB)
    for s in (-1, 1):
        fb.face([(-174.0 - hw, WY + s * 7.2, zp), (-174.0 + hw, WY + s * 7.2, zp), (-174.0 + hw, WY + s * 7.2, zb + 0.01),
                 (-174.0 - hw, WY + s * 7.2, zb + 0.01)], WET, (0, -s, 0))


def beam(fb, p0, p1, w, m):
    d = p1 - p0
    u = d / d.length
    a = Vector((1.0, 0.0, 0.0)) if abs(u.x) < 0.9 else Vector((0.0, 1.0, 0.0))
    s1 = u.cross(a).normalized() * (w / 2)
    s2 = u.cross(s1).normalized() * (w / 2)
    cs = [s1 + s2, -s1 + s2, -s1 - s2, s1 - s2]
    for k in range(4):
        c0, c1 = cs[k], cs[(k + 1) % 4]
        fb.face([p0 + c0, p1 + c0, p1 + c1, p0 + c1], m, (c0 + c1))
    fb.face([p1 + c for c in cs], m, u)
    fb.face([p0 + c for c in cs], m, -u)


def wheel():
    mw = MB("VFX_OP_Wheel", "12_VFX_HELPERS", None, detail="near", floor=-999)
    xr = (WX - WW / 2 + 0.25, WX + WW / 2 - 0.25)
    n = 16
    r_rim = WR - 1.75
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        ch = 2 * r_rim * math.sin(math.pi / n) + 0.12
        for x in xr:
            mw.box((0.42, ch, 0.62), (x, WY + r_rim * math.cos(a), AXZ + r_rim * math.sin(a)), (a + math.pi / 2, 0, 0),
                   WOODD, 0.0)
    for k in range(n):
        a = 2 * math.pi * k / n
        rp = (r_rim - 0.35 + WR) / 2
        mw.box((WW + 0.3, 0.24, WR - r_rim + 0.35), (WX, WY + rp * math.cos(a), AXZ + rp * math.sin(a)),
               (a + math.pi / 2, 0, 0), WOOD, 0.0)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 16
        rc = (0.95 + r_rim) / 2
        for x in xr:
            mw.box((0.34, 0.42, r_rim - 0.95 + 0.2), (x, WY + rc * math.cos(a), AXZ + rc * math.sin(a)),
                   (a + math.pi / 2, 0, 0), WOODD, 0.0)
    mw.cyl(1.0, WW - 0.1, (WX, WY, AXZ), (0, math.pi / 2, 0), m=WOODD, n=8, bevel=0.0)
    mw.cyl(0.45, L.CANAL_W_X[1] - L.CANAL_W_X[0] + 3.6, (WX, WY, AXZ), (0, math.pi / 2, 0), m=IRON, n=8, bevel=0.0)
    ob = mw.finish()
    ob["pivot"] = (WX, WY, AXZ)
    ob["axis"] = (-1.0, 0.0, 0.0)                      # correnteza para -Y: as pas de baixo seguem a agua
    ob["rpm"] = RPM
    ob["vfx_zone"] = "canal"
    ob["Dist"] = 220.0
    col_box("OP_WheelEnvelope", (WW + 0.4, WD + 1.2, WD + 1.2), (WX, WY, AXZ))
    return ob


def spring(fb):
    """bica no arrimo do terraco alto (cabeceira do canal oeste): nicho escuro na face + calha de madeira"""
    x, y, z = SPRING
    yf = 299.88
    fb.face([(x - 1.1, yf, z - 0.5), (x + 1.1, yf, z - 0.5), (x + 1.1, yf, z + 1.2), (x - 1.1, yf, z + 1.2)], RDARK, (0, -1, 0))
    beam(fb, Vector((x, yf + 0.3, z - 0.1)), Vector((x, y, z - 0.25)), 0.32, WOODD)


# ------------------------------------------------------------------ marcadores (op_core._water_measured)
def _wp(pts):
    return ";".join("%.2f,%.2f,%.2f" % p for p in pts)


def _castle():
    import op_terrain as TR
    x = 0.0
    lip = [(x, TR.LIP_BACK - 0.2, TR.LIP_TOP + 0.14), (x, 352.0, TR.LIP_TOP + 0.14), (x, TR.LIP_FRONT, TR.LIP_SPOUT + 0.14)]
    pts = [(x, TR.LIP_FRONT - 0.15, TR.LIP_SPOUT + 0.1), (x, 350.0, 125.0), (x, 349.7, 112.0), (x, 349.5, LV_CF + 1.0),
           (x, 349.2, LV_CF)]
    return lip, pts, [6.0, 6.6, 7.2, 8.0, 9.0]


def _sea(nm):
    x, y, zt, zs = L.FALL_W if nm == "W" else L.FALL_E
    lv = zt
    yl = (LIP_W_Y if nm == "W" else LIP_E_Y)
    pts = [(x, yl - 0.05, lv + 0.1), (x, yl - 0.3, lv - 2.5), (x, yl - 0.8, 75.0), (x, yl - 1.4, 60.0), (x, yl - 1.9, 45.0),
           (x, yl - 2.2, SEA)]
    ws = ([7.4, 7.8, 8.4, 9.0, 9.6, 10.4] if nm == "W" else [5.4, 5.8, 6.4, 7.0, 7.6, 8.2])
    return pts, ws, yl, lv


def _canal_e():
    pts = [(18.4, 342.0, LV_CF), (95.0, 342.0, LV_CF), (95.2, 342.0, LV_P), (188.0, 342.5, LV_P), (248.5, 342.5, LV_P),
           (248.5, 304.0, LV_P), (248.5, L.FALL_E[1], LV_P), (248.5, LIP_E_Y, LV_P - 0.15)]
    return pts, [5.3] * (len(pts) - 1) + [5.4]


def _canal_w():
    pts = [(-174.0, 299.6, LV_P), (-174.0, 250.0, LV_P), (-174.0, 182.0, LV_P), (-174.0, 116.0, LV_P),
           (-174.0, 115.8, LV_T1), (-174.0, 92.0, LV_T1), (-174.0, 58.0, LV_T1), (-174.0, L.FALL_W[1], LV_T1),
           (-174.0, LIP_W_Y, LV_T1 - 0.15)]
    return pts, [7.3] * (len(pts) - 1) + [7.4]


def water_markers():
    """nome -> (posicao, rumo, props) dos FX_*/WATER_*: as MESMAS constantes que desenham a pedra (planta V2)"""
    south = yaw_to(0, -1)
    east = yaw_to(1, 0)
    lip, cpts, cws = _castle()
    wpts, wws, wy, wlv = _sea("W")
    epts, ews, ey, elv = _sea("E")
    ce, cew = _canal_e()
    cw, cww = _canal_w()
    bp = ccw(DL.offset_poly(L.BASIN, -0.12))
    xs = [p[0] for p in bp]
    ys = [p[1] for p in bp]
    bed_b = L.BASIN_Z - BED
    sx, sy, sz = SPRING
    return {
        "FX_Fall_Castle_Lip": ((0.0, lip[-1][1], lip[-1][2] - 0.14), south, {
            "fx": "nevoa_borda", "kind": "cachoeira", "width": 6.0, "drop": round(lip[-1][2] - LV_CF, 2),
            "water_level_up": round(lip[-1][2], 2), "waypoints": _wp(cpts), "widths": ",".join("%.1f" % w for w in cws),
            "spout_waypoints": _wp(lip), "spout_width": 5.0, "source_pos": (0.0, 357.6, 131.2),
            "note": "V2-3: ponta da bica de pedra do rochedo (op_terrain: topo 132,05 dentro do patio, ponta em rampa "
                    "ate 130,3 em y 350,6); a lamina sai da boca escura (y 357,6) e cai na bacia (97,6) rente a proa"}),
        "FX_Fall_Castle_Step": ((0.0, 349.4, LV_CF + 0.2), south, {
            "fx": "espuma_degrau", "width": 8.0, "jump": 0.2, "step2_pos": (0.0, 348.2, LV_CF),
            "note": "V2-3: a cortina bate na bacia rente a proa (sem degraus soltos: pedras molhadas nos flancos)"}),
        "FX_Fall_Castle_Base": ((0.0, 348.6, LV_CF), south, {
            "fx": "nevoa_base", "width": 10.0, "level": LV_CF,
            "note": "pe da cachoeira na bacia, entre as pedras molhadas"}),
        "FX_Mist_CastleFall": ((0.0, 347.6, LV_CF + 1.2), 0.0, {
            "fx": "nevoa_baixa", "radius": 11.0, "note": "nevoa do pe da cachoeira"}),
        "WATER_Basin": ((round(sum(xs) / len(xs), 2), round(sum(ys) / len(ys), 2), LV_CF), yaw_to(0, 1), {
            "shape": "poligono", "level": LV_CF, "floor": bed_b, "depth": round(LV_CF - bed_b, 2), "rim_min": CF,
            "sx": round(max(xs) - min(xs), 2), "sy": round(max(ys) - min(ys), 2),
            "waypoints": _wp([(x, y, LV_CF) for x, y in bp]),
            "mouth_a_pos": (19.0, 339.4, LV_CF), "mouth_b_pos": (18.6, 344.6, LV_CF),
            "note": "V2-3: contorno da bacia (planta, 0,12 para dentro da cantaria); leito colidivel 96,6 (op_col)"}),
        "WATER_CanalE": ((ce[0][0], ce[0][1], LV_CF), east, {
            "level": LV_CF, "level_low": LV_P, "floor": LV_CF - BED, "floor_low": LV_P - BED, "rim": CF + 0.0,
            "rim_low": P + COPE_H, "waypoints": _wp(ce), "widths": ",".join("%.1f" % w for w in cew),
            "note": "V2-3 canal REBAIXADO: boca da bacia (97,6) -> soleira x 95 (FX_Weir_E) -> 89,6 ao longo do pe "
                    "dos socalcos NE -> curva -> bica da queda leste; pares com cota diferente = quedas curtas"}),
        "WATER_CanalW": ((cw[0][0], cw[0][1], LV_P), south, {
            "level": LV_P, "level_low": LV_T1, "floor": LV_P - BED, "floor_low": LV_T1 - BED, "rim": P + COPE_H,
            "rim_low": T1 + COPE_H, "waypoints": _wp(cw), "widths": ",".join("%.1f" % w for w in cww),
            "wheel_pos": (WX, WY, LV_T1),
            "note": "V2-3 canal REBAIXADO (89,6): bica do terraco alto -> sob as 2 pontes em arco (y 182/252) -> calha "
                    "soleira y 116 (FX_Weir_W) -> 85,6 -> roda d'agua -> bica da queda oeste"}),
        "FX_Weir_E": ((95.0, 342.0, LV_CF), east, {
            "fx": "degrau_agua", "drop": round(LV_CF - LV_P, 2), "steps": 1, "width": 5.3, "tops": "%.2f" % (LV_CF - BED),
            "note": "V2-3: borda da soleira (x 95) do canal leste: queda de 8 sobre a parede; correnteza +X"}),
        "FX_Weir_W": ((-174.0, 116.0, LV_P), south, {
            "fx": "degrau_agua", "drop": round(LV_P - LV_T1, 2), "steps": 1, "width": 7.3, "tops": "%.2f" % (LV_P - BED),
            "note": "V2-3: borda da soleira (y 116) do canal oeste: queda de 4; correnteza -Y"}),
        "FX_Spring_W": ((sx, sy, sz), south, {
            "fx": "bica", "kind": "bica", "width": 1.0, "drop": round(sz - LV_P, 2),
            "waypoints": _wp([(sx, sy - 0.02, sz - 0.1), (sx, sy - 0.3, sz - 1.6), (sx, sy - 0.45, LV_P + 1.0), (sx, sy - 0.5, LV_P)]),
            "widths": "1.0,1.1,1.3,1.5", "note": "calha de madeira saindo do nicho no arrimo do terraco alto"}),
        "FX_Fall_W_Lip": ((-174.0, wy, wlv), south, {
            "fx": "nevoa_borda", "kind": "bica", "width": 7.4, "drop": round(wlv - SEA, 2), "water_level_up": wlv,
            "waypoints": _wp(wpts), "widths": ",".join("%.1f" % w for w in wws), "face_y_local": L.FALL_W[1],
            "note": "V2-3: ponta da soleira (85,6) alem do fim do leito do canal oeste; cortina ate o mar (36)"}),
        "FX_Fall_W_Base": ((wpts[-1][0], wpts[-1][1], SEA), south, {
            "fx": "espuma_mar", "width": 10.0, "level": SEA, "note": "pe da queda oeste no mar, entre as pedras"}),
        "FX_Fall_E_Lip": ((248.5, ey, elv), south, {
            "fx": "nevoa_borda", "kind": "bica", "width": 5.4, "drop": round(elv - SEA, 2), "water_level_up": elv,
            "waypoints": _wp(epts), "widths": ",".join("%.1f" % w for w in ews), "face_y_local": L.FALL_E[1],
            "note": "V2-3: ponta da soleira (89,6) na garganta NE; cai na enseada do porto"}),
        "FX_Fall_E_Base": ((epts[-1][0], epts[-1][1], SEA), south, {
            "fx": "espuma_mar", "width": 8.2, "level": SEA, "note": "pe da queda leste na enseada"}),
        "WATER_Sea": ((L.SEA_C[0], L.SEA_C[1], SEA), 0.0, {
            "shape": "quadrado", "level": SEA, "size": L.SEA_SIZE, "client_only": True, "area": 5, "color": "48,176,196",
            "falls": "FX_Fall_W_Base;FX_Fall_E_Base",
            "note": "mar LOCAL turquesa de Wano: so no cliente e so na area 5; espuma clara no pe das falesias (op_terrain)"}),
    }


# ------------------------------------------------------------------ previa da agua (00_REFERENCE: fora do export)
def preview():
    pw = FB("PREVIEW_Water_OP", "00_REFERENCE")
    M = water_markers()

    def parse(s):
        return [tuple(float(v) for v in p.split(",")) for p in s.split(";")]

    def ribbon(pts, ws):
        for (a, b), w0, w1 in zip(zip(pts, pts[1:]), ws, ws[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy)
            if ln < 0.05:
                continue
            nx, ny = -dy / ln, dx / ln
            pw.face([(a[0] + nx * w0 / 2, a[1] + ny * w0 / 2, a[2] - 0.04), (a[0] - nx * w0 / 2, a[1] - ny * w0 / 2, a[2] - 0.04),
                     (b[0] - nx * w1 / 2, b[1] - ny * w1 / 2, b[2] - 0.04), (b[0] + nx * w1 / 2, b[1] + ny * w1 / 2, b[2] - 0.04)],
                    "PREVIEW_Sea", (0, 0, 1))

    def curtain(pts, ws):
        for (a, b), w0, w1 in zip(zip(pts, pts[1:]), ws, ws[1:]):
            pw.face([(a[0] + w0 / 2, a[1], a[2]), (a[0] - w0 / 2, a[1], a[2]), (b[0] - w1 / 2, b[1], b[2]), (b[0] + w1 / 2, b[1], b[2])],
                    "PREVIEW_Falls", (0, -1, 0.3))
    for nm in ("WATER_CanalE", "WATER_CanalW"):
        p = M[nm][2]
        ribbon(parse(p["waypoints"]), [float(w) for w in p["widths"].split(",")])
    bp = parse(M["WATER_Basin"][2]["waypoints"])
    pw.face([(x, y, z - 0.04) for x, y, z in bp], "PREVIEW_Sea", (0, 0, 1))
    (x0, y0, x1, y1), pz = L.NE_POND
    pw.face([(x0, y0, pz), (x1, y0, pz), (x1, y1, pz), (x0, y1, pz)], "PREVIEW_Sea", (0, 0, 1))
    for nm in ("FX_Fall_Castle_Lip", "FX_Fall_W_Lip", "FX_Fall_E_Lip", "FX_Spring_W"):
        p = M[nm][2]
        curtain(parse(p["waypoints"]), [float(w) for w in p["widths"].split(",")])
    return pw.finish()


CAMS = {
    "CAM_OPWat_FallPlaza": ((-6.0, 262.0, P + 5.5), (0.0, 350.0, 116.0), 24),
    "CAM_OPWat_Basin": ((13.0, 323.0, CF + 5.5), (0.0, 347.5, 100.5), 22),
    "CAM_OPWat_Wheel": ((-190.0, 74.0, 97.0), (-174.0, 90.0, 89.0), 24),
    "CAM_OPWat_CanalW": ((-150.0, 240.0, 124.0), (-174.0, 160.0, 89.0), 26),
    "CAM_OPWat_PH_Bridge": ((-160.0, 170.0, P + 5.5), (-176.0, 186.0, P + 1.0), 22),
    "CAM_OPWat_Bridge": ((-165.0, 202.0, 104.0), (-174.0, 182.0, 91.0), 26),
    "CAM_OPWat_WeirW": ((-160.0, 104.0, T1 + 5.5), (-174.0, 118.0, 87.0), 24),
    "CAM_OPWat_Spring": ((-166.0, 284.0, P + 5.5), (-174.0, 299.5, 94.0), 26),
    "CAM_OPWat_CanalE": ((58.0, 326.0, 106.0), (130.0, 343.0, 91.0), 24),
    "CAM_OPWat_PH_CanalE": ((150.0, 334.0, P + 5.5), (200.0, 343.0, 91.0), 24),
    "CAM_OPWat_WeirE": ((110.0, 333.0, P + 5.5), (95.0, 342.0, 94.0), 24),
    "CAM_OPWat_CornerE": ((272.0, 296.0, 138.0), (247.0, 334.0, 92.0), 26),
    "CAM_OPWat_SeaW": ((-200.0, -16.0, 40.0), (-174.0, 46.0, 58.0), 24),
    "CAM_OPWat_SeaE": ((262.0, 205.0, 96.0), (248.5, 297.0, 64.0), 32),
}


def cams():
    for n, (loc, tgt, lens) in CAMS.items():
        camera(n, loc, tgt, lens)


def build():
    for o in [o for o in bpy.data.objects if o.name.startswith(("PREVIEW_Water", "OP_Water_", "VFX_OP_Wheel"))]:
        bpy.data.objects.remove(o, do_unlink=True)
    fb = FB("OP_Water_Stone")
    nb = beds(fb)
    nc = copings(fb)
    chutes(fb)
    lips(fb)
    basin(fb)
    sea_rocks(fb)
    pond(fb)
    wheel_static(fb)
    spring(fb)
    ob = fb.finish()
    mbb = MB("OP_Water_Bridges", C, None, detail="near", floor=-999)
    nbr = bridges(mbb)
    obb = mbb.finish()
    wob = wheel()
    preview()
    cams()
    print("op_water V2-3: leitos %d, capas %d, pontes %d | tris pedra %d + pontes %d, roda %d" % (
        nb, nc, nbr, tris_of(ob), tris_of(obb), tris_of(wob)))
