# wb_kit.py - KIT de construcao do lobby WOLFBERG (texturizado: a textura carrega o detalhe, a geometria da a forma).
# Todas as pecas desenham num wb_lib.Build (1 objeto por material ao finalizar) num Frame local Fr:
#   Fr.o = origem (Blender), Fr.f = para onde a peca OLHA (frente, +y local), Fr.t = direita de quem esta DENTRO olhando
#   a frente (+x local), z = altura. Fr.rbx(x, z, y, fx, fz) monta a partir de coordenadas ROBLOX.
# Escala: avatar 5,2 studs. Porta 4,4 x 6,2 + arco; terreo 8; andar 6,5; balanco 0,9; degrau 0,4.
# Z-fight: nada coplanar entre materiais diferentes (>= 0,12 de folga); pecas do mesmo material se interpenetram.
import math
import random
import zlib

import bmesh
import bpy
from mathutils import Matrix, Vector

import fm_lib
import wb_lib as W
import wb_layout as L
from wb_lib import RB, V

RAD = math.radians
UP = V((0, 0, 1))

ST, STD = "WB_Stone", "WB_Stone_Dark"
TB, PK, PKL = "WB_Timber", "WB_Plank", "WB_Plank_Light"
RF, RFD = "WB_Roof", "WB_Roof_Dark"
PL, PLO = "WB_Plaster", "WB_Plaster_Ochre"
GL, IR = "WB_Glass", "WB_Iron"
GH, FH, JET = 8.0, 6.5, 0.9
DOOR_W, DOOR_H = 4.4, 6.2
TXT = "WB_SignText"


def h01(*k):
    return (zlib.crc32(repr(k).encode()) & 0xffffffff) / 4294967296.0


def rng(*k):
    return random.Random(zlib.crc32(repr(k).encode()))


# ------------------------------------------------------------------ frame
class Fr:
    def __init__(self, o, f):
        self.o = V(o)
        fx, fy = f[0], f[1]
        n = math.hypot(fx, fy) or 1.0
        self.f = V((fx / n, fy / n, 0.0))
        self.t = V((self.f.y, -self.f.x, 0.0))

    @staticmethod
    def rbx(x, z, y, fx, fz):
        return Fr(RB(x, z, y), (fx, -fz))

    def p(self, x, y, z=0.0):
        return self.o + self.t * x + self.f * y + UP * z

    def R(self):
        return Matrix(((self.t.x, self.f.x, 0.0), (self.t.y, self.f.y, 0.0), (0.0, 0.0, 1.0)))

    def sub(self, x=0.0, y=0.0, z=0.0, turn=0.0):
        c, s = math.cos(RAD(turn)), math.sin(RAD(turn))
        f = (self.f.x * c - self.f.y * s, self.f.x * s + self.f.y * c)
        return Fr(self.p(x, y, z), f)

    def face(self, side, w, d):
        """frame de uma FACE de um bloco w (ao longo de t) x d (ao longo de f) centrado na origem: origem no meio da
        face, na base, olhando para fora; +x local = direita de quem esta dentro olhando para fora"""
        if side == "F":
            return self.sub(0, d / 2, 0, 0)
        if side == "B":
            return self.sub(0, -d / 2, 0, 180)
        if side == "R":
            return self.sub(w / 2, 0, 0, -90)
        return self.sub(-w / 2, 0, 0, 90)

    def yaw(self):
        return math.atan2(self.t.y, self.t.x)


def bx(b, F, x, y, z, sx, sy, sz, m, bevel=0.0, rx=0.0):
    """caixa no frame: centro (x, y, z) local, tamanho (sx ao longo de t, sy ao longo de f, sz altura); rx = giro em
    graus em torno do eixo t (inclinacao: telhados, toldos)"""
    R = F.R()
    if rx:
        R = R @ Matrix.Rotation(RAD(rx), 3, "X")
    b.box(F.p(x, y, z), (sx, sy, sz), m, rot=R, bevel=bevel)


def bb(b, F, x0, x1, y0, y1, z0, z1, m, bevel=0.0):
    bx(b, F, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, abs(x1 - x0), abs(y1 - y0), abs(z1 - z0), m, bevel)


def beam(b, F, a, c, w, h, m=TB):
    b.beam(F.p(*a), F.p(*c), w, h, m)


def cyl(b, F, a, c, r, m, seg=12, r1=None, caps=True):
    b.cyl(F.p(*a), F.p(*c), r, m, r1=r1, seg=seg, caps=caps)


def poly_wall(b, F, pts, x0, x1, m):
    """poligono no plano (y, z) local extrudado de x0 a x1 ao longo de t (oitoes, perfis)"""
    bm = bmesh.new()
    a = [bm.verts.new(F.p(x0, y, z)) for (y, z) in pts]
    c = [bm.verts.new(F.p(x1, y, z)) for (y, z) in pts]
    n = len(pts)
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], c[(i + 1) % n], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def poly_prism(b, F, pts, z0, z1, m):
    """poligono no plano (x, y) local extrudado de z0 a z1"""
    bm = bmesh.new()
    a = [bm.verts.new(F.p(x, y, z0)) for (x, y) in pts]
    c = [bm.verts.new(F.p(x, y, z1)) for (x, y) in pts]
    n = len(pts)
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(n):
        bm.faces.new((a[i], a[(i + 1) % n], c[(i + 1) % n], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


def lathe(b, F, x, y, prof, m, n=12, z0=0.0):
    """solido de revolucao em torno do eixo vertical que passa por (x, y): prof = [(r, z)] de baixo para cima"""
    bm = bmesh.new()
    rings = []
    for (r, z) in prof:
        ring = []
        for k in range(n):
            a = 2 * math.pi * k / n
            ring.append(bm.verts.new(F.p(x + max(r, 0.001) * math.cos(a), y + max(r, 0.001) * math.sin(a), z0 + z)))
        rings.append(ring)
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new((r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]))
    bm.faces.new(list(reversed(rings[0])))
    bm.faces.new(rings[-1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.002)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)


_TXT_N = [0]


def text(b, F, s, size, m, x=0.0, y=0.0, z=0.0, thick=0.3, align="CENTER", bold=False):
    """letras 3D (fonte padrao do Blender) na face: lidas por quem olha a peca de frente (de +y para -y).
    Tamanho = altura aproximada da caixa-alta."""
    cu = bpy.data.curves.new("TMP_txt%d" % _TXT_N[0], "FONT")
    _TXT_N[0] += 1
    cu.body = s
    cu.resolution_u = 3            # letras leves (o padrao 12 custa ~4x mais triangulos)
    cu.size = size * 1.4
    cu.extrude = thick / 2
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.offset = 0.04 * size if bold else 0.0
    ob = bpy.data.objects.new(cu.name, cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bm = bmesh.new()
    bm.from_mesh(me)
    R = Matrix(((-F.t.x, 0.0, F.f.x), (-F.t.y, 0.0, F.f.y), (0.0, 1.0, 0.0)))
    o = F.p(x, y, z)
    for v in bm.verts:
        v.co = o + R @ v.co
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, m)
    bpy.data.objects.remove(ob, do_unlink=True)
    bpy.data.meshes.remove(me)
    bpy.data.curves.remove(cu)


# ------------------------------------------------------------------ paredes e aberturas
def timber_face(b, Ff, x0, x1, z0, z1, bays=None, braces=True, mid=True, depth=0.32, w=0.5, m=TB, skip=()):
    """enxaimel sobre uma face de reboco (Ff: origem no meio da face na base, +y para fora, plano da face em y=0):
    soleira e verga, montantes, cantos, diagonais nos vaos de canto e travessa no meio dos vaos sem janela"""
    y = depth / 2
    bb(b, Ff, x0 - 0.1, x1 + 0.1, 0.0, depth, z0, z0 + w, m)              # soleira
    bb(b, Ff, x0 - 0.1, x1 + 0.1, 0.0, depth, z1 - w, z1, m)              # verga
    if bays is None:
        n = max(2, int(round((x1 - x0) / 3.4)))
        bays = [x0 + (x1 - x0) * k / n for k in range(n + 1)]
    for k, xk in enumerate(bays):
        ww = w * 1.3 if k in (0, len(bays) - 1) else w
        bb(b, Ff, xk - ww / 2, xk + ww / 2, 0.0, depth, z0, z1, m)
    for k in range(len(bays) - 1):
        a, c = bays[k], bays[k + 1]
        if k in skip:
            continue
        if braces and (k == 0 or k == len(bays) - 2):
            s = 1 if k == 0 else -1
            beam(b, Ff, (a + (0.4 if s > 0 else c - a - 0.4), y, z0 + w), (c - (0.4 if s > 0 else c - a - 0.4), y, z1 - w),
                 w * 0.9, depth * 0.9, m)
        elif mid:
            bb(b, Ff, a, c, 0.0, depth * 0.9, (z0 + z1) / 2 - w * 0.4, (z0 + z1) / 2 + w * 0.4, m)


def window(b, Ff, cx, zc, ww=2.2, wh=2.6, shutters=True, flowers="WB_FlowerRed", mull=True, frame=TB, box=True,
           seed=0):
    """janela na face Ff (y=0 = plano da face): vidro recuado, caixilho saliente, venezianas abertas, floreira"""
    g = 0.12
    bb(b, Ff, cx - ww / 2, cx + ww / 2, -0.35, -0.05, zc - wh / 2, zc + wh / 2, GL)
    fw = 0.32
    for (a, c, z0, z1) in ((cx - ww / 2 - fw, cx - ww / 2, zc - wh / 2 - fw, zc + wh / 2 + fw),
                           (cx + ww / 2, cx + ww / 2 + fw, zc - wh / 2 - fw, zc + wh / 2 + fw),
                           (cx - ww / 2, cx + ww / 2, zc + wh / 2, zc + wh / 2 + fw),
                           (cx - ww / 2, cx + ww / 2, zc - wh / 2 - fw, zc - wh / 2)):
        bb(b, Ff, a, c, 0.0, 0.3, z0, z1, frame)
    if mull:
        bb(b, Ff, cx - 0.1, cx + 0.1, -0.2, 0.05, zc - wh / 2, zc + wh / 2, frame)
        bb(b, Ff, cx - ww / 2, cx + ww / 2, -0.2, 0.05, zc - 0.1, zc + 0.1, frame)
    if shutters:
        sw = ww * 0.46
        for s in (-1, 1):
            x0 = cx + s * (ww / 2 + fw + 0.08)
            bb(b, Ff, min(x0, x0 + s * sw), max(x0, x0 + s * sw), 0.08, 0.3, zc - wh / 2 - 0.1, zc + wh / 2 + 0.1, PK)
            bb(b, Ff, min(x0, x0 + s * sw) + 0.1, max(x0, x0 + s * sw) - 0.1, 0.3, 0.42, zc - wh / 2 + 0.6, zc - wh / 2 + 0.9, TB)
            bb(b, Ff, min(x0, x0 + s * sw) + 0.1, max(x0, x0 + s * sw) - 0.1, 0.3, 0.42, zc + wh / 2 - 0.9, zc + wh / 2 - 0.6, TB)
    if box and flowers:
        zb = zc - wh / 2 - fw
        bb(b, Ff, cx - ww / 2 - 0.2, cx + ww / 2 + 0.2, 0.0, 0.8, zb - 0.75, zb - 0.1, PK)
        r = rng("fl", seed, cx, zc)
        n = max(3, int(ww / 0.55))
        for k in range(n):
            x = cx - ww / 2 + (k + 0.5) * ww / n
            b.sphere(Ff.p(x + r.uniform(-0.1, 0.1), 0.4 + r.uniform(-0.15, 0.15), zb - 0.05 + r.uniform(0.05, 0.3)),
                     r.uniform(0.26, 0.36), "WB_Leaf", seg=6)
            b.sphere(Ff.p(x + r.uniform(-0.15, 0.15), 0.42 + r.uniform(-0.1, 0.1), zb + 0.25 + r.uniform(0.0, 0.25)),
                     r.uniform(0.18, 0.26), flowers if r.random() < 0.75 else "WB_FlowerYellow", seg=6)


def door(b, Ff, cx=0.0, dw=DOOR_W, dh=DOOR_H, arch=True, m=PK, step=True, lamp=False):
    """porta de tabuas em arco de cantaria (recuada 0,4 na parede), ferragens, soleira"""
    bb(b, Ff, cx - dw / 2, cx + dw / 2, -0.45, -0.15, 0.2, dh, m)
    for z in (dh * 0.25, dh * 0.72):
        bb(b, Ff, cx - dw / 2 + 0.2, cx + dw / 2 - 0.2, -0.15, -0.02, z - 0.22, z + 0.22, TB)
        bb(b, Ff, cx - dw / 2 + 0.35, cx - dw / 2 + 1.6, -0.02, 0.06, z - 0.12, z + 0.12, IR)
    b.sphere(Ff.p(cx + dw / 2 - 0.7, 0.05, dh * 0.5), 0.2, IR, seg=6)
    jw = 0.9
    for s in (-1, 1):
        bb(b, Ff, cx + s * (dw / 2 + jw / 2) - jw / 2, cx + s * (dw / 2 + jw / 2) + jw / 2, -0.3, 0.35, 0.0, dh - 0.4, STD)
    if arch:
        bm = bmesh.new()
        n = 9
        ro, ri = dw / 2 + jw, dw / 2
        outer = [(cx + ro * math.cos(math.pi * k / n), dh - 0.4 + ro * math.sin(math.pi * k / n)) for k in range(n + 1)]
        inner = [(cx + ri * math.cos(math.pi * k / n), dh - 0.4 + ri * math.sin(math.pi * k / n)) for k in range(n + 1)]
        for k in range(n):
            quad = [outer[k], outer[k + 1], inner[k + 1], inner[k]]
            vs0 = [bm.verts.new(Ff.p(x, -0.3, z)) for (x, z) in quad]
            vs1 = [bm.verts.new(Ff.p(x, 0.35, z)) for (x, z) in quad]
            bm.faces.new(list(reversed(vs0)))
            bm.faces.new(vs1)
            for i in range(4):
                bm.faces.new((vs0[i], vs0[(i + 1) % 4], vs1[(i + 1) % 4], vs1[i]))
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.001)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, STD)
        bb(b, Ff, cx - dw / 2, cx + dw / 2, -0.45, -0.15, dh - 0.4, dh + dw / 2 - 0.2, "WB_Dark")   # fundo escuro do arco
    else:
        bb(b, Ff, cx - dw / 2 - jw, cx + dw / 2 + jw, -0.3, 0.35, dh - 0.4, dh + 0.5, STD)
    if step:
        bb(b, Ff, cx - dw / 2 - 1.0, cx + dw / 2 + 1.0, 0.0, 1.4, -0.3, 0.3, STD, bevel=0.08)
    if lamp:
        lantern_wall(b, Ff, cx + dw / 2 + jw + 1.2, dh + 1.0)


def lantern_wall(b, Ff, x, z, name=None):
    """lanterna de parede: braco de ferro + caixa de vidro quente (luz NightOnly se name)"""
    bb(b, Ff, x - 0.15, x + 0.15, 0.0, 1.6, z + 0.9, z + 1.2, IR)
    bb(b, Ff, x - 0.15, x + 0.15, 1.3, 1.6, z - 0.2, z + 1.2, IR)
    lantern(b, Ff, x, 1.45, z - 0.2, name)


def lantern(b, F, x, y, z_top, name=None, s=1.0):
    """lanterna pendurada pelo topo em (x, y, z_top): capa de ferro, vidro quente, base"""
    h = 1.5 * s
    bb(b, F, x - 0.42 * s, x + 0.42 * s, y - 0.42 * s, y + 0.42 * s, z_top - 0.1 * s, z_top, IR)
    bb(b, F, x - 0.3 * s, x + 0.3 * s, y - 0.3 * s, y + 0.3 * s, z_top - h, z_top - 0.1 * s, "WB_LampGlow")
    for sx in (-1, 1):
        for sy in (-1, 1):
            bb(b, F, x + sx * 0.3 * s - 0.05, x + sx * 0.3 * s + 0.05, y + sy * 0.3 * s - 0.05, y + sy * 0.3 * s + 0.05,
               z_top - h, z_top, IR)
    bb(b, F, x - 0.38 * s, x + 0.38 * s, y - 0.38 * s, y + 0.38 * s, z_top - h - 0.12 * s, z_top - h, IR)
    if name:
        fm_lib.light(name, "POINT", F.p(x, y, z_top - h / 2), 60.0, (1.0, 0.75, 0.42), 0.4)


def chimney(b, F, x, y, z0, z1, w=2.2, m=ST):
    bb(b, F, x - w / 2, x + w / 2, y - w / 2, y + w / 2, z0, z1, m)
    bb(b, F, x - w / 2 - 0.3, x + w / 2 + 0.3, y - w / 2 - 0.3, y + w / 2 + 0.3, z1, z1 + 0.5, STD)
    bb(b, F, x - w / 2 + 0.4, x + w / 2 - 0.4, y - w / 2 + 0.4, y + w / 2 - 0.4, z1 + 0.5, z1 + 0.9, "WB_Dark")


# ------------------------------------------------------------------ telhado de duas aguas
def roof(b, F, Lx, Dy, z_eave, pitch=50.0, over=1.4, thick=0.7, m=RF, mr=RFD, gable=True, pl=PL, gable_timber=True,
         fascia=True, dormers=0, seed=0, flowers="WB_FlowerRed"):
    """duas aguas com cumeeira ao longo de t (x local), cobrindo um bloco Lx x Dy cujo topo da parede esta em z_eave.
    Beiral 'over' em todos os lados; o oitao (em x = +-Lx/2) e reboco com vigas. Devolve z da cumeeira."""
    half = Dy / 2 + over
    rise = half * math.tan(RAD(pitch))
    slen = math.hypot(half, rise)
    ang = math.degrees(math.atan2(rise, half))
    for s in (-1, 1):
        # laje inclinada: centro no meio da agua, deslocada meia espessura para fora (normal)
        nrm = V((0, -s * math.sin(RAD(ang)), math.cos(RAD(ang))))
        c = F.p(0, s * half / 2, z_eave + rise / 2) + (F.R() @ nrm) * (thick / 2)
        R = F.R() @ Matrix.Rotation(RAD(-s * ang), 3, "X")
        b.box(c, (Lx + 2 * over, slen + 0.3, thick), m, rot=R)
        if fascia:
            bb(b, F, -Lx / 2 - over, Lx / 2 + over, s * half - 0.25, s * half + 0.25, z_eave - 0.6, z_eave + 0.25, TB)
    zr = z_eave + rise
    bb(b, F, -Lx / 2 - over - 0.1, Lx / 2 + over + 0.1, -0.7, 0.7, zr + thick * 0.4, zr + thick * 0.4 + 0.6, mr)
    if gable:
        hw = Dy / 2
        rise_w = hw * math.tan(RAD(pitch))
        for s in (-1, 1):
            Fg = F.face("R" if s > 0 else "L", Lx, Dy)
            # oitao: triangulo de reboco (plano da face em y=0 do Fg), 0,6 para dentro
            poly_wall(b, Fg, [(-0.6, z_eave - 0.05), (-0.6, z_eave + rise_w - 0.3), (0.0, z_eave + rise_w - 0.3),
                              (0.0, z_eave - 0.05)], -hw + 0.1, hw - 0.1, pl) if False else None
            poly_prism_gable(b, Fg, hw, z_eave, rise_w, pl)
            if gable_timber:
                bb(b, Fg, -0.3, 0.3, 0.0, 0.3, z_eave, z_eave + rise_w * 0.86, TB)
                bb(b, Fg, -hw + 0.3, hw - 0.3, 0.0, 0.3, z_eave + 0.05, z_eave + 0.5, TB)
                for sx in (-1, 1):
                    beam(b, Fg, (sx * (hw - 0.6), 0.15, z_eave + 0.5), (0.0, 0.15, z_eave + rise_w * 0.84), 0.42, 0.3, TB)
                bb(b, Fg, -hw * 0.5, hw * 0.5, 0.0, 0.3, z_eave + rise_w * 0.42, z_eave + rise_w * 0.42 + 0.36, TB)
                window(b, Fg, 0.0, z_eave + rise_w * 0.22 + 0.9, 1.6, 1.8, shutters=False, box=False, seed=seed)
    # aguas-furtadas na frente (+y)
    for k in range(dormers):
        xd = (k - (dormers - 1) / 2) * (Lx / (dormers + 0.4))
        dormer(b, F, xd, half, z_eave, pitch, m, mr, pl, flowers=flowers, seed="%s%d" % (seed, k))
    return zr


def poly_prism_gable(b, Fg, hw, z0, rise, pl):
    """triangulo do oitao na face Fg (origem no meio da face, +x ao longo da face): espessura 0,6 para dentro"""
    bm = bmesh.new()
    pts = [(-hw + 0.05, z0 - 0.05), (hw - 0.05, z0 - 0.05), (0.0, z0 + rise - 0.1)]
    a = [bm.verts.new(Fg.p(x, -0.7, z)) for (x, z) in pts]
    c = [bm.verts.new(Fg.p(x, -0.05, z)) for (x, z) in pts]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(3):
        bm.faces.new((a[i], a[(i + 1) % 3], c[(i + 1) % 3], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, pl)


def dormer(b, F, xd, half, z_eave, pitch, m, mr, pl, w=3.8, h=3.4, flowers="WB_FlowerRed", seed=0):
    """agua-furtada na agua da frente (+y): caixa de reboco enterrada no telhado + telhadinho de 2 aguas + janela"""
    t = math.tan(RAD(pitch))
    yf = half - 1.4                       # face da frente da agua-furtada
    zb = z_eave + 0.9
    depth = 3.4
    Fd = F.sub(xd, yf, 0, 0)              # origem na face da frente, olhando +y
    bb(b, Fd, -w / 2, w / 2, -depth, 0.0, zb, zb + h, pl)
    timber_face(b, Fd, -w / 2, w / 2, zb, zb + h, bays=[-w / 2, w / 2], braces=False, mid=False)
    window(b, Fd, 0.0, zb + h * 0.55, 2.0, 2.0, shutters=True, flowers=flowers, seed=seed)
    # telhadinho: cumeeira ao longo de y (perpendicular a cumeeira principal)
    Fr_ = F.sub(xd, yf - depth / 2, 0, 90)
    roof(b, Fr_, depth + 0.6, w, zb + h, 48.0, over=0.45, thick=0.45, m=m, mr=mr, gable=False, fascia=False)


# ------------------------------------------------------------------ CASA ENXAIMEL
def house(spec, coll="03_TOWN", seed=None):
    """casa fechada (360 graus) a partir do spec do wb_layout. Devolve (Build, z_ridge Blender)"""
    sid = spec["id"]
    r = rng("house", sid)
    b = W.Build("WB_House_" + sid, coll)
    y0 = spec.get("y", L.Y_PAVE)
    F = Fr.rbx(spec["x"], spec["z"], y0, spec["fx"], spec["fz"])
    w, d = float(spec["w"]), float(spec["d"])
    nf = spec["floors"]
    pl, rf = spec.get("plaster", PL), spec.get("roof", RF)
    rfd = RFD
    jet = JET if spec.get("jetty", True) else 0.0
    # soco + terreo: estilo A = pedra inteira; estilo B = base de pedra ate 3,2 e enxaimel por cima (variedade por casa)
    style = spec.get("style", "B" if h01("style", sid) < 0.45 else "A")
    bb(b, F, -w / 2 - 0.4, w / 2 + 0.4, -d / 2 - 0.4, d / 2 + 0.4, -0.5, 0.9, STD)
    Ff = F.face("F", w, d)
    door_x = spec.get("door_x", -w / 4 if w > 16 else 0.0)
    if style == "A":
        bb(b, F, -w / 2, w / 2, -d / 2, d / 2, 0.8, GH, ST)
    else:
        bb(b, F, -w / 2, w / 2, -d / 2, d / 2, 0.8, 3.2, ST)
        bb(b, F, -w / 2, w / 2, -d / 2, d / 2, 3.1, GH, pl)
        for side in ("F", "B", "R", "L"):
            Fs = F.face(side, w, d)
            ln = w if side in ("F", "B") else d
            n = max(2, int(round(ln / 3.6)))
            bays = [-ln / 2 + ln * k / n for k in range(n + 1)]
            skip = set()
            if side == "F":
                # no Ff, +x local = -x de F: a porta fica em -door_x
                skip = {k for k in range(n) if bays[k] - 0.4 <= -door_x + DOOR_W / 2 and bays[k + 1] + 0.4 >= -door_x - DOOR_W / 2}
            timber_face(b, Fs, -ln / 2, ln / 2, 3.2, GH, bays=bays, skip=skip, braces=True, mid=False)
    door(b, Ff, door_x, lamp=True)
    gw = [x for x in (-w / 2 + w * 0.25, w / 2 - w * 0.25, 0.0) if abs(x - door_x) > 4.2]
    for x in gw[:2]:
        window(b, Ff, x, 5.0, 2.4, 2.8, shutters=True, flowers=(None if style == "A" else "WB_FlowerRed"), box=(style == "B"), seed=sid)
        if style == "A":
            bb(b, Ff, x - 1.6, x + 1.6, 0.0, 0.5, 3.3, 3.65, STD)       # peitoril de pedra
    for side in ("R", "L"):
        Fs = F.face(side, w, d)
        for x in (-d / 4, d / 4):
            window(b, Fs, x, 5.0, 2.0, 2.6, shutters=True, flowers=None, box=False, seed=sid)
            if style == "A":
                bb(b, Fs, x - 1.4, x + 1.4, 0.0, 0.5, 3.4, 3.75, STD)
    # andares em balanco com vigas
    zb = GH
    Wj, Dj = w, d
    for i in range(nf - 1):
        j = jet if i == 0 else jet * 0.6
        Wj, Dj = Wj + 2 * j, Dj + 2 * j
        if j > 0:
            # cachorros (pontas das vigas) sob o balanco, nas 4 faces
            for side in ("F", "B", "R", "L"):
                Fs = F.face(side, Wj, Dj)
                ln = Wj if side in ("F", "B") else Dj
                n = max(3, int(ln / 2.2))
                for k in range(n):
                    x = -ln / 2 + (k + 0.5) * ln / n
                    bb(b, Fs, x - 0.3, x + 0.3, -j - 0.6, 0.1, zb - 0.5, zb + 0.1, TB)
        bb(b, F, -Wj / 2, Wj / 2, -Dj / 2, Dj / 2, zb, zb + FH, pl)
        flowers = ["WB_FlowerRed", "WB_FlowerPink", "WB_FlowerYellow"][int(h01("fl", sid, i) * 3)]
        for side in ("F", "B", "R", "L"):
            Fs = F.face(side, Wj, Dj)
            ln = Wj if side in ("F", "B") else Dj
            n = max(2, int(round(ln / 3.6)))
            bays = [-ln / 2 + ln * k / n for k in range(n + 1)]
            wins = [k for k in range(n) if (k % 2 == (1 if n > 3 else 0)) or n <= 2]
            if side == "B":
                wins = wins[::2]
            timber_face(b, Fs, -ln / 2, ln / 2, zb, zb + FH, bays=bays, skip=set(wins))
            for k in wins:
                cx = (bays[k] + bays[k + 1]) / 2
                window(b, Fs, cx, zb + FH * 0.52, 2.2, 2.6, shutters=True,
                       flowers=flowers if side in ("F", "R", "L") else None, seed=sid)
        if spec.get("balcony") and i == 0:
            balcony(b, F.face("F", Wj, Dj), -Wj * 0.22, Wj * 0.22, zb)
        zb += FH
    # telhado
    ridge = spec.get("ridge", "x")
    nd = 2 if spec.get("dormer") and ridge == "x" and Wj > 16 else (1 if spec.get("dormer") and ridge == "x" else 0)
    pitch = spec.get("pitch", 46.0 + 10.0 * h01("pitch", sid))
    if ridge == "x":
        zr = roof(b, F, Wj, Dj, zb, pitch, over=1.4, m=rf, mr=rfd, pl=pl, dormers=nd, seed=sid)
        cx = spec.get("chimney", 1) * (Wj / 2 - 2.6)
        cy = -Dj / 4
    else:
        zr = roof(b, F.sub(0, 0, 0, 90), Dj, Wj, zb, pitch, over=1.4, m=rf, mr=rfd, pl=pl, seed=sid)
        cx = spec.get("chimney", 1) * 1.8
        cy = -Dj / 2 + 2.6
    if spec.get("chimney", 1):
        chimney(b, F, cx, cy, zb - 1.0, zr + 2.6)
        fm_lib.marker("VFX_Smoke_House_" + sid, F.p(cx, cy, zr + 3.6), (0, 0, 0), 1.0, "PLAIN_AXES",
                      "15_GAMEPLAY_MARKERS", {"particle": "smoke_thin", "rate": 2})
    # placa pendurada
    if spec.get("sign"):
        hanging_sign(b, F.face("F", w, d), w / 2 - 2.5 if door_x <= 0 else -w / 2 + 2.5, GH + 1.6, spec["sign"])
    objs = b.finish()
    # colisao: volume inteiro (fachada fechada) + degrau
    c = F.p(0, 0, 0)
    fm_lib.col_box("House", (Wj + 0.3, Dj + 0.3, zb + 2.0), (c.x, c.y, y0 + (zb + 2.0) / 2 - 1.0), (0, 0, F.yaw()))
    return b, y0 + zr


def balcony(b, Ff, x0, x1, z, depth=2.0, rail=2.6):
    bb(b, Ff, x0, x1, 0.0, depth, z - 0.35, z + 0.05, PK)
    for x in (x0 + 0.2, x1 - 0.2):
        bb(b, Ff, x - 0.2, x + 0.2, depth - 0.4, depth, z, z + rail, TB)
        beam(b, Ff, (x, 0.1, z - 2.2), (x, depth - 0.2, z - 0.4), 0.35, 0.35, TB)
    bb(b, Ff, x0, x1, depth - 0.45, depth + 0.05, z + rail - 0.3, z + rail, TB)
    n = int((x1 - x0) / 0.8)
    for k in range(1, n):
        x = x0 + (x1 - x0) * k / n
        bb(b, Ff, x - 0.1, x + 0.1, depth - 0.3, depth - 0.1, z + 0.05, z + rail - 0.3, PK)
    for s in (0, 1):
        bb(b, Ff, x0 if s == 0 else x1 - 0.45, x0 + 0.45 if s == 0 else x1, 0.0, depth, z + rail - 0.3, z + rail, TB)


def hanging_sign(b, Ff, x, z, label, icon=None, w=3.6, h=2.2):
    """braco de ferro saindo da fachada + tabua pendurada com letras"""
    bb(b, Ff, x - 0.12, x + 0.12, 0.0, 2.4, z + h + 0.5, z + h + 0.74, IR)
    beam(b, Ff, (x, 0.1, z + h - 0.6), (x, 2.1, z + h + 0.5), 0.2, 0.2, IR)
    for yy in (1.2 - w / 2 + 0.3, 1.2 + w / 2 - 0.3):
        bb(b, Ff, x - 0.06, x + 0.06, yy - 0.06, yy + 0.06, z + h, z + h + 0.55, IR)
    # tabua perpendicular a fachada (le dos dois lados)
    Fs = Ff.sub(x, 1.2, 0, 90)
    bb(b, Fs, -w / 2, w / 2, -0.15, 0.15, z, z + h, PK, bevel=0.08)
    bb(b, Fs, -w / 2 - 0.15, w / 2 + 0.15, -0.2, 0.2, z - 0.1, z + 0.22, TB)
    bb(b, Fs, -w / 2 - 0.15, w / 2 + 0.15, -0.2, 0.2, z + h - 0.22, z + h + 0.1, TB)
    size = min(0.9, (w - 0.6) / max(1, len(label)) * 1.45)
    text(b, Fs, label, size, TXT, 0.0, 0.17, z + h * 0.55, 0.12)
    text(b, Fs.sub(0, 0, 0, 180), label, size, TXT, 0.0, 0.17, z + h * 0.55, 0.12)


# ------------------------------------------------------------------ PECAS DE RUA
def lantern_post(b, F, x, y, name=None, h=9.0):
    """poste de ferro com braco e lanterna (base de pedra)"""
    bb(b, F, x - 0.7, x + 0.7, y - 0.7, y + 0.7, -0.2, 0.6, STD, bevel=0.1)
    cyl(b, F, (x, y, 0.5), (x, y, h), 0.22, IR, seg=8, r1=0.16)
    cyl(b, F, (x, y, 0.5), (x, y, 1.6), 0.34, IR, seg=8, r1=0.22)
    bb(b, F, x - 0.12, x + 0.12, y - 0.12, y + 1.3, h - 0.26, h, IR)
    beam(b, F, (x, y + 0.1, h - 1.6), (x, y + 1.1, h - 0.3), 0.12, 0.12, IR)
    lantern(b, F, x, y + 1.3, h - 0.1, name)


def fence(b, F, x0, x1, y=0.0, h=3.2, post_every=4.0, rails=2):
    """cerca de madeira ao longo de x local (de x0 a x1) em y local"""
    n = max(1, int(round((x1 - x0) / post_every)))
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k / n
        bb(b, F, x - 0.35, x + 0.35, y - 0.35, y + 0.35, -0.3, h, TB, bevel=0.06)
        bb(b, F, x - 0.42, x + 0.42, y - 0.42, y + 0.42, h, h + 0.3, TB)
    for i in range(rails):
        z = h * (0.38 + 0.42 * i / max(1, rails - 1))
        bb(b, F, x0 - 0.2, x1 + 0.2, y - 0.2, y + 0.2, z - 0.3, z + 0.3, PK)


def welcome_sign(b, F, lines, w=14.0, h=7.0, z0=2.6):
    """placa grande de boas-vindas de 2 faces: 2 postes grossos + tabua com moldura + letras dos dois lados"""
    for s in (-1, 1):
        bb(b, F, s * (w / 2 + 0.6) - 0.55, s * (w / 2 + 0.6) + 0.55, -0.55, 0.55, -0.5, z0 + h + 1.4, TB, bevel=0.08)
        bb(b, F, s * (w / 2 + 0.6) - 0.7, s * (w / 2 + 0.6) + 0.7, -0.7, 0.7, z0 + h + 1.4, z0 + h + 1.9, TB)
        bb(b, F, s * (w / 2 + 0.6) - 1.0, s * (w / 2 + 0.6) + 1.0, -1.0, 1.0, -0.6, 0.8, STD, bevel=0.1)
    bb(b, F, -w / 2, w / 2, -0.3, 0.3, z0, z0 + h, PK, bevel=0.1)
    for (z0_, z1_) in ((z0 - 0.3, z0 + 0.45), (z0 + h - 0.45, z0 + h + 0.3)):
        bb(b, F, -w / 2 - 0.3, w / 2 + 0.3, -0.42, 0.42, z0_, z1_, TB, bevel=0.06)
    for s in (-1, 1):
        bb(b, F, s * w / 2 - 0.3, s * w / 2 + 0.3, -0.42, 0.42, z0 - 0.3, z0 + h + 0.3, TB)
    # pontas decorativas no topo
    bb(b, F, -w / 2 - 0.3, w / 2 + 0.3, -0.42, 0.42, z0 + h + 0.3, z0 + h + 0.7, TB)
    bb(b, F, -2.2, 2.2, -0.5, 0.5, z0 + h + 0.7, z0 + h + 1.6, TB, bevel=0.1)
    for face in (F, F.sub(0, 0, 0, 180)):
        n = len(lines)
        for i, (s, size) in enumerate(lines):
            zc = z0 + h * (1 - (i + 0.5) / n) - 0.1
            text(b, face, s, size, TXT, 0.0, 0.32, zc, 0.18, bold=True)


def signpost(b, F, arms, h=9.0):
    """poste de direcoes: arms = [(texto, angulo graus a partir de +y local)]"""
    bb(b, F, -0.8, 0.8, -0.8, 0.8, -0.3, 0.6, STD, bevel=0.1)
    bb(b, F, -0.35, 0.35, -0.35, 0.35, 0.5, h, TB)
    bb(b, F, -0.5, 0.5, -0.5, 0.5, h, h + 0.5, TB)
    for i, (label, ang) in enumerate(arms):
        Fa = F.sub(0, 0, 0, ang)
        z = h - 1.4 - i * 1.25
        bm = bmesh.new()
        pts = [(0.2, z - 0.45), (4.6, z - 0.45), (5.4, z), (4.6, z + 0.45), (0.2, z + 0.45)]
        a = [bm.verts.new(Fa.p(-0.12, y, zz)) for (y, zz) in pts]
        c = [bm.verts.new(Fa.p(0.12, y, zz)) for (y, zz) in pts]
        bm.faces.new(list(reversed(a)))
        bm.faces.new(c)
        for k in range(5):
            bm.faces.new((a[k], a[(k + 1) % 5], c[(k + 1) % 5], c[k]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, PK)
        Ft = Fa.sub(0.12, 2.7, 0, -90)
        text(b, Ft, label, 0.5, TXT, 0.0, 0.03, z, 0.08)
        text(b, Ft.sub(0, 0, 0, 180), label, 0.5, TXT, 0.0, 0.27, z, 0.08)


def barrel(b, F, x, y, r=1.1, h=2.6, seed=0, lying=False):
    prof = [(r * 0.86, 0.0), (r, h * 0.3), (r, h * 0.7), (r * 0.86, h)]
    if lying:
        Fb = F.sub(x, y, r, 0)
        bm_b = W.Build("_tmp")
        lathe(b, F, x, y, prof, PK, 12) if False else None
        # barril deitado: cilindro ao longo de y
        cyl(b, F, (x, y - h / 2, r), (x, y + h / 2, r), r * 0.9, PK, seg=12)
        for yy in (y - h * 0.3, y + h * 0.3):
            cyl(b, F, (x, yy - 0.12, r), (x, yy + 0.12, r), r * 0.96, IR, seg=12)
        return
    lathe(b, F, x, y, prof, PK, 12)
    for z in (h * 0.22, h * 0.78):
        cyl(b, F, (x, y, z - 0.12), (x, y, z + 0.12), r * 1.03, IR, seg=12)


def crate(b, F, x, y, s=2.2, z=0.0, turn=0.0, seed=0):
    Fc = F.sub(x, y, z, turn)
    bb(b, Fc, -s / 2, s / 2, -s / 2, s / 2, 0.0, s, PK, bevel=0.05)
    for sgn in (-1, 1):
        bb(b, Fc, -s / 2 - 0.08, s / 2 + 0.08, sgn * s / 2 - 0.1, sgn * s / 2 + 0.1, 0.0, 0.3, TB)
        bb(b, Fc, -s / 2 - 0.08, s / 2 + 0.08, sgn * s / 2 - 0.1, sgn * s / 2 + 0.1, s - 0.3, s, TB)
        bb(b, Fc, sgn * s / 2 - 0.1, sgn * s / 2 + 0.1, -s / 2 - 0.08, s / 2 + 0.08, 0.0, s, TB)


def sack(b, F, x, y, s=1.2, z=0.0):
    b.sphere(F.p(x, y, z + s * 0.55), s * 0.62, "WB_Cloth_Cream", seg=8, scale=(1.0, 1.0, 0.85))
    b.sphere(F.p(x, y, z + s * 1.05), s * 0.3, "WB_Cloth_Cream", seg=6)


def cart(b, F, x, y, turn=0.0, loaded=True):
    """carroca de madeira com 2 rodas grandes e varais no chao"""
    Fc = F.sub(x, y, 0, turn)
    bb(b, Fc, -2.4, 2.4, -3.6, 3.6, 2.3, 2.7, PK)
    for s in (-1, 1):
        bb(b, Fc, s * 2.4 - 0.15, s * 2.4 + 0.15, -3.6, 3.6, 2.7, 4.6, PK)
        bb(b, Fc, -2.55, 2.55, s * 3.6 - 0.15, s * 3.6 + 0.15, 2.7, 4.2, PK)
        bb(b, Fc, s * 2.4 - 0.25, s * 2.4 + 0.25, -3.8, 3.8, 2.0, 2.3, TB)
        # roda
        cyl(b, Fc, (s * 2.9, 0.4, 2.3), (s * 3.3, 0.4, 2.3), 2.2, TB, seg=14)
        cyl(b, Fc, (s * 2.85, 0.4, 2.3), (s * 3.35, 0.4, 2.3), 0.5, IR, seg=8)
        for k in range(6):
            a = math.pi * k / 6
            beam(b, Fc, (s * 3.1, 0.4 + 1.9 * math.cos(a), 2.3 + 1.9 * math.sin(a)),
                 (s * 3.1, 0.4 - 1.9 * math.cos(a), 2.3 - 1.9 * math.sin(a)), 0.22, 0.22, PK)
    cyl(b, Fc, (-3.4, 0.4, 2.3), (3.4, 0.4, 2.3), 0.22, IR, seg=8)
    for s in (-1, 1):
        beam(b, Fc, (s * 1.6, 3.6, 2.5), (s * 1.6, 8.2, 0.6), 0.3, 0.3, TB)
    if loaded:
        barrel(b, Fc, -1.2, -1.6, 1.0, 2.4, z=0) if False else None
        for (bx_, by_) in ((-1.2, -1.8), (1.2, -1.8), (0.0, 0.6)):
            lathe(b, Fc, bx_, by_, [(0.9, 0.0), (1.05, 0.7), (1.05, 1.7), (0.9, 2.4)], PK, 10, z0=2.7)
            cyl(b, Fc, (bx_, by_, 2.7 + 0.5), (bx_, by_, 2.7 + 0.74), 1.08, IR, seg=10)
            cyl(b, Fc, (bx_, by_, 2.7 + 1.85), (bx_, by_, 2.7 + 2.09), 1.08, IR, seg=10)
        sack(b, Fc, 1.3, 2.2, 1.3, z=2.7)
        sack(b, Fc, -1.2, 2.4, 1.1, z=2.7)


def stall(b, F, canvas="WB_CanvasRed", goods="bread", w=8.0, d=5.0, seed=0):
    """barraca de mercado: 4 postes, bancada, toldo listrado inclinado com aba, mercadorias e lanterna"""
    r = rng("stall", seed)
    for sx in (-1, 1):
        for sy in (-1, 1):
            zt = 7.6 if sy > 0 else 6.4
            bb(b, F, sx * w / 2 - 0.28, sx * w / 2 + 0.28, sy * d / 2 - 0.28, sy * d / 2 + 0.28, -0.3, zt, TB)
    # bancada
    bb(b, F, -w / 2 - 0.3, w / 2 + 0.3, 0.2, d / 2 + 0.6, 2.8, 3.2, PK, bevel=0.06)
    bb(b, F, -w / 2 + 0.2, w / 2 - 0.2, 0.3, d / 2 + 0.3, 0.0, 2.8, PK)
    bb(b, F, -w / 2 - 0.2, w / 2 + 0.2, d / 2 + 0.3, d / 2 + 0.55, 1.0, 2.8, canvas)       # saia da bancada
    # prateleira de fundo
    bb(b, F, -w / 2 + 0.2, w / 2 - 0.2, -d / 2 - 0.1, -d / 2 + 1.2, 4.6, 4.9, PK)
    bb(b, F, -w / 2 + 0.2, w / 2 - 0.2, -d / 2 - 0.25, -d / 2 + 0.05, 2.0, 6.0, PK)
    # toldo inclinado (sobe para tras) com aba pendente na frente
    half = d / 2 + 1.2
    ang = math.degrees(math.atan2(1.2, 2 * half))
    bx(b, F, 0.0, 0.0, 7.0, w + 1.6, 2 * half + 0.4, 0.3, canvas, rx=-ang)
    for k in range(int((w + 1.6) / 1.0)):
        x = -(w + 1.6) / 2 + 0.5 + k
        bx(b, F, x, half + 0.1, 6.4 - 0.45, 0.96, 0.3, 0.9, canvas)
    # mercadorias
    for k in range(5):
        x = -w / 2 + 1.0 + k * (w - 2.0) / 4
        y = r.uniform(0.6, d / 2 - 0.4)
        if goods == "bread":
            b.sphere(F.p(x, y, 3.65), 0.5, "WB_Bread", seg=8, scale=(1.4, 0.9, 0.8))
        elif goods == "fruit":
            b.sphere(F.p(x, y, 3.6), 0.4, "WB_Apple", seg=6)
            b.sphere(F.p(x + 0.5, y - 0.4, 3.6), 0.38, "WB_FlowerYellow", seg=6)
        else:
            lathe(b, F, x, y, [(0.35, 0.0), (0.45, 0.4), (0.3, 1.0), (0.2, 1.3)], "WB_Cloth_Blue", 8, z0=3.2)
    crate(b, F, -w / 2 + 1.4, 1.2, 1.8, z=3.2)
    for k in range(3):
        barrel(b, F, w / 2 + 1.6, -1.2 + k * 0.1, 0.9, 2.2) if k == 0 else None
    lantern(b, F, w / 2 - 0.6, d / 2 - 0.2, 6.2, None, 0.8)


def fountain(b, F, r_out=7.0, seed=0):
    """fonte octogonal de pedra: tanque, pedestal, taca, bico; agua"""
    n = 8
    poly = [(r_out * math.cos(math.pi / 8 + 2 * math.pi * k / n), r_out * math.sin(math.pi / 8 + 2 * math.pi * k / n))
            for k in range(n)]
    inner = [(p[0] * (r_out - 1.3) / r_out, p[1] * (r_out - 1.3) / r_out) for p in poly]
    poly_prism(b, F, poly, -0.3, 0.6, STD)
    # mureta: aneis de 8 blocos
    for k in range(n):
        a0, a1 = poly[k], poly[(k + 1) % n]
        i0, i1 = inner[k], inner[(k + 1) % n]
        bm = bmesh.new()
        q = [a0, a1, i1, i0]
        vs0 = [bm.verts.new(F.p(x, y, 0.6)) for (x, y) in q]
        vs1 = [bm.verts.new(F.p(x, y, 2.6)) for (x, y) in q]
        bm.faces.new(list(reversed(vs0)))
        bm.faces.new(vs1)
        for i in range(4):
            bm.faces.new((vs0[i], vs0[(i + 1) % 4], vs1[(i + 1) % 4], vs1[i]))
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        b.mesh(bm, ST)
    cap = [(p[0] * (r_out + 0.35) / r_out, p[1] * (r_out + 0.35) / r_out) for p in poly]
    poly_prism(b, F, cap, 2.0, 2.5, STD)
    cap_in = [(p[0] * (r_out - 1.6) / r_out, p[1] * (r_out - 1.6) / r_out) for p in poly]
    poly_prism(b, F, cap_in, 0.6, 1.7, "WB_Water")
    # pedestal + taca grande + coluna + taca pequena + remate
    lathe(b, F, 0, 0, [(2.2, 0.6), (2.0, 1.0), (1.1, 1.3), (0.8, 3.6), (1.3, 4.0), (3.6, 4.2), (3.8, 4.9), (3.4, 5.1),
                       (0.6, 5.3), (0.5, 7.0), (0.9, 7.2), (2.0, 7.4), (2.1, 7.9), (0.4, 8.0), (0.4, 8.8), (0.7, 9.0),
                       (0.0, 9.9)], ST, 14)
    lathe(b, F, 0, 0, [(3.3, 4.75), (0.0, 4.75)], "WB_Water", 14, z0=0.3)
    lathe(b, F, 0, 0, [(1.85, 7.55), (0.0, 7.55)], "WB_Water", 12, z0=0.3)
    # 4 bicos de bronze no pedestal
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        cyl(b, F, (1.0 * math.cos(a), 1.0 * math.sin(a), 2.6), (1.9 * math.cos(a), 1.9 * math.sin(a), 2.4), 0.16, "WB_Brass", seg=6)
    fm_lib.marker("VFX_Fountain_Splash", F.p(0, 0, 9.7), (0, 0, 0), 1.0, "PLAIN_AXES", "15_GAMEPLAY_MARKERS",
                  {"particle": "water", "rate": 20})
    fm_lib.col_box("Plaza", (2 * r_out + 0.7, 2 * r_out + 0.7, 2.6), F.p(0, 0, 1.0), (0, 0, F.yaw()))
    fm_lib.col_box("Plaza", (4.6, 4.6, 8.0), F.p(0, 0, 4.0), (0, 0, F.yaw()))


def well(b, F):
    lathe(b, F, 0, 0, [(3.0, -0.3), (3.0, 2.6), (2.2, 2.6), (2.2, 0.0)], ST, 12)
    lathe(b, F, 0, 0, [(3.3, 2.6), (3.3, 3.1), (2.0, 3.1), (2.0, 2.6)], STD, 12)
    cyl(b, F, (0, 0, 0.5), (0, 0, 1.0), 2.1, "WB_Dark", seg=12)
    for s in (-1, 1):
        bb(b, F, s * 2.4 - 0.3, s * 2.4 + 0.3, -0.3, 0.3, 2.6, 8.0, TB)
    cyl(b, F, (-2.6, 0, 6.2), (2.6, 0, 6.2), 0.5, TB, seg=10)
    Fr_ = F.sub(0, 0, 0, 90)
    roof(b, Fr_, 2.2, 6.4, 8.0, 42.0, over=0.9, thick=0.4, gable=False, fascia=False)
    bb(b, F, -0.6, 0.6, -0.5, 0.5, 2.5, 3.4, PK)       # balde
    fm_lib.col_box("Town", (6.8, 6.8, 3.4), F.p(0, 0, 1.4), (0, 0, F.yaw()))


def banner(b, F, x, y, z_top, color="WB_Cloth_Red", w=2.6, h=7.0, pole=False, emblem=True):
    """estandarte pendurado numa vara horizontal (ponta em V), com um emblema"""
    bb(b, F, x - w / 2 - 0.4, x + w / 2 + 0.4, y - 0.14, y + 0.14, z_top - 0.14, z_top + 0.14, TB)
    bm = bmesh.new()
    pts = [(x - w / 2, z_top - 0.2), (x + w / 2, z_top - 0.2), (x + w / 2, z_top - h + 1.0), (x, z_top - h),
           (x - w / 2, z_top - h + 1.0)]
    a = [bm.verts.new(F.p(px, y - 0.08, pz)) for (px, pz) in pts]
    c = [bm.verts.new(F.p(px, y + 0.08, pz)) for (px, pz) in pts]
    bm.faces.new(list(reversed(a)))
    bm.faces.new(c)
    for i in range(5):
        bm.faces.new((a[i], a[(i + 1) % 5], c[(i + 1) % 5], c[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    b.mesh(bm, color)
    if emblem:
        # disco no plano do pano (ao longo da normal do frame), nunca em eixos de mundo
        cyl(b, F, (x, y - 0.16, z_top - h * 0.45), (x, y + 0.16, z_top - h * 0.45), w * 0.26, "WB_Cloth_Gold", seg=10)
    if pole:
        bb(b, F, x - 0.25, x + 0.25, y - 0.25, y + 0.25, -0.3, z_top + 0.6, TB)


# ------------------------------------------------------------------ VEGETACAO
def oak(b, F, x, y, h=16.0, seed=0, leaf="WB_Leaf"):
    r = rng("oak", seed, x, y)
    cyl(b, F, (x, y, -0.5), (x + r.uniform(-0.6, 0.6), y + r.uniform(-0.6, 0.6), h * 0.55), 1.3, "WB_Bark", seg=8,
        r1=0.7)
    for k in range(3):
        a = 2 * math.pi * k / 3 + r.uniform(-0.4, 0.4)
        cyl(b, F, (x, y, h * 0.4), (x + 2.6 * math.cos(a), y + 2.6 * math.sin(a), h * 0.62), 0.55, "WB_Bark", seg=6,
            r1=0.3)
    cx, cy, cz = x, y, h * 0.75
    R = h * 0.42
    for k in range(7):
        a = 2 * math.pi * k / 6 + r.uniform(-0.3, 0.3)
        d = R * (0.0 if k == 6 else 0.55)
        rr = R * (0.9 if k == 6 else r.uniform(0.6, 0.75))
        b.sphere(F.p(cx + d * math.cos(a), cy + d * math.sin(a), cz + (R * 0.25 if k == 6 else r.uniform(-R * 0.2, R * 0.2))),
                 rr, leaf, seg=10, scale=(1.0, 1.0, 0.85))
    fm_lib.col_box("Veg", (2.6, 2.6, h * 0.55), F.p(x, y, h * 0.27), (0, 0, 0))
    fm_lib.marker("VFX_Leaves_%d_%d" % (int(x), int(y)), F.p(x, y, cz), (0, 0, 0), 1.0, "PLAIN_AXES",
                  "15_GAMEPLAY_MARKERS", {"particle": "leaves", "rate": 1, "radius": R})


def pine(b, F, x, y, h=22.0, seed=0):
    r = rng("pine", seed, x, y)
    cyl(b, F, (x, y, -0.5), (x, y, h * 0.35), 1.0, "WB_Bark", seg=7, r1=0.5)
    n = 4
    for k in range(n):
        z0 = h * (0.22 + 0.78 * k / n)
        z1 = h * (0.22 + 0.78 * (k + 1.25) / n)
        rr = h * 0.22 * (1.0 - 0.18 * k) * r.uniform(0.9, 1.1)
        cyl(b, F, (x, y, z0), (x, y, z1), rr, "WB_Pine", seg=9, r1=0.05)
    fm_lib.col_box("Veg", (2.0, 2.0, h * 0.4), F.p(x, y, h * 0.2), (0, 0, 0))


def bush(b, F, x, y, s=2.0, seed=0, leaf="WB_Leaf", flowers=None):
    r = rng("bush", seed, x, y)
    for k in range(4):
        b.sphere(F.p(x + r.uniform(-s * 0.4, s * 0.4), y + r.uniform(-s * 0.4, s * 0.4), s * 0.45 + r.uniform(0, s * 0.2)),
                 s * r.uniform(0.45, 0.6), leaf, seg=7, scale=(1, 1, 0.8))
    if flowers:
        for k in range(5):
            b.sphere(F.p(x + r.uniform(-s * 0.5, s * 0.5), y + r.uniform(-s * 0.5, s * 0.5), s * 0.9 + r.uniform(0, s * 0.2)),
                     s * 0.12, flowers, seg=5)


def grass_tufts(b, F, poly, n, seed=0, flowers=0.3):
    """tufos e flores espalhados num poligono local (x, y)"""
    r = rng("tufts", seed)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    k = 0
    tries = 0
    while k < n and tries < n * 20:
        tries += 1
        x, y = r.uniform(min(xs), max(xs)), r.uniform(min(ys), max(ys))
        if not fm_lib.point_in_poly(x, y, poly):
            continue
        k += 1
        for j in range(3):
            a = r.uniform(0, 2 * math.pi)
            b.cyl(F.p(x + 0.3 * math.cos(a), y + 0.3 * math.sin(a), 0.0),
                  F.p(x + 0.6 * math.cos(a), y + 0.6 * math.sin(a), r.uniform(0.9, 1.5)), 0.18, "WB_Leaf", r1=0.02, seg=4,
                  caps=False)
        if r.random() < flowers:
            b.sphere(F.p(x, y, r.uniform(0.8, 1.2)), 0.22,
                     r.choice(["WB_FlowerRed", "WB_FlowerYellow", "WB_FlowerWhite", "WB_FlowerPink"]), seg=5)
