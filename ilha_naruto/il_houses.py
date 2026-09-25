# il_houses - zona "houses" da Ilha 1 (Naruto / Vila da Folha). Substitui il_blockout.houses().
#   * casas NAO entraveis estilo Konoha: T1 (4), T2 (3), vale leste (2) e 5 casinhas no plato de cima (far)
#   * MOINHO DE MINERIO / Posto do Minerador (ENTRAVEL) em L.MILL, porta a oeste (escada do anel em x ~90),
#     eixo da roda d'agua (L.WHEEL, agente de agua) entrando pela parede leste -> engrenagens -> pilao de 3 socos
# Linguagem (ref_14..17): reboco creme, base de pedra, cunhais e faixa de madeira escura sob o beiral, telhado de
# 4 aguas com canais de telha em relevo, espigoes/cumeeira escuros com pontas levantadas, janelas com caixilho
# (algumas redondas, algumas de ripas), varandas altas sem acesso e caixas d'agua sobre o telhado.
# Casa NAO entravel: SEM PORTA nenhuma. Colisao em caixas simples (corpo + aguas do telhado).
# Objetos: VIL_Houses_Near (9 casas), VIL_Houses_Upper (5, far), VIL_Mill (casca + interior + props),
#          VFX_VIL_MillGear / VFX_VIL_MillCamshaft / VFX_VIL_MillStamps (pecas moveis, 12_VFX_HELPERS).
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, S, col_box, col_box2, mk, light
import il_layout as L
import fm_lib
import fm_parts as FP

# ------------------------------------------------------------------ materiais novos da zona (<= 5)
_M = fm_lib.MATS
_M.setdefault("Roof_HouRidge", (S(82, 78, 80), 0.75, 0.0, 0, None, 0.08))        # cumeeira / espigoes (telha cinza)
_M.setdefault("Plaster_HouPeach", (S(240, 206, 164), 0.9, 0.0, 0, None, 0.08))   # 2o tom de reboco
_M.setdefault("Window_Dark", ((0.035, 0.045, 0.06), 0.18, 0.0, 0.0, None, 0.0))  # vidro apagado (dia)

G = L.G
GLASS = "Window_Dark"
LIT = "Window_Warm"
RIDGE = "Roof_HouRidge"

# ------------------------------------------------------------------ cameras de revisao (360 graus + altura do jogador)
_MX, _MY = L.MILL[0], L.MILL[1]
CAMS = {
    "CAM_Houses_T1": ((44.0, 70.0, L.RING + 10.0), (62.0, 108.0, L.T1 + 7.0), 20),
    "CAM_Houses_T1W": ((-62.0, 58.0, L.RING + 11.0), (-98.0, 98.0, L.T1 + 7.0), 20),
    "CAM_Houses_T2": ((-82.0, 131.0, L.T2 + 9.0), (-116.0, 152.0, L.T2 + 7.0), 20),
    "CAM_Houses_T2E": ((66.0, 128.0, L.T2 + 8.0), (98.0, 150.0, L.T2 + 6.0), 20),
    "CAM_Houses_East": ((92.0, -62.0, G + 24.0), (132.0, 4.0, G + 6.0), 22),
    "CAM_Houses_Upper": ((4.0, 138.0, 106.0), (0.0, 197.0, L.CLIFF_TOP + 4.0), 18),
    "CAM_Houses_Mill34": ((74.0, -12.0, G + 16.0), (100.0, 12.0, G + 9.0), 20),
    "CAM_Houses_MillInterior": ((93.9, 13.6, G + 7.2), (104.0, 10.2, G + 6.2), 13),
    "CAM_Houses_MillMachine": ((97.0, 8.0, G + 5.6), (100.0, 18.0, G + 7.5), 16),
    "CAM_Houses_MillBack": ((124.0, 38.0, G + 15.0), (104.0, 13.0, G + 9.0), 20),
    "CAM_Houses_MillNorth": ((84.0, 38.0, G + 14.0), (100.0, 17.0, G + 8.0), 20),
    "CAM_Houses_PlayerMill": ((80.5, 12.0, L.RING + 5.3), (96.0, 12.0, G + 10.5), 20),
    "CAM_Houses_PlayerT1": ((22.0, 94.0, L.T1 + 5.3), (40.0, 108.0, L.T1 + 7.0), 20),
    "CAM_Houses_Back": ((20.0, 300.0, 150.0), (10.0, 118.0, 20.0), 24),
    "CAM_Houses_SideE": ((236.0, 30.0, 70.0), (112.0, 30.0, 12.0), 24),
    "CAM_Houses_SideW": ((-246.0, 100.0, 80.0), (-100.0, 110.0, 22.0), 24),
}


# ------------------------------------------------------------------ construtor
class HMB(MB):
    """MB das casas: telhado, reboco e vidro com a cor pedida (sem sorteio de variante) e no maximo 'vmax' variantes
    por familia (pedra/madeira) -> poucas MeshParts por objeto no Roblox"""

    def __init__(self, name, coll, rng=None, detail="near", floor=None, vmax=1):
        MB.__init__(self, name, coll, rng, detail, floor)
        self.vmax = vmax

    def _family(self, m):
        if m.startswith(("Roof_", "Plaster_", "Window_")):
            return None
        fam = MB._family(self, m)
        if fam is None:
            return None
        return (min(fam[0], self.vmax), fam[1])

    def _uv(self, faces, m):
        """telha modelada (canais em relevo): cada peca amostra um ponto calmo da textura de telha (a mesma regra do
        fm_arch_kit.AMB) -> um tom por peca, sem xadrez claro/escuro nos telhados"""
        if fm_lib.tex_key(m) == "roof" and faces:
            import fm_arch_kit
            return fm_arch_kit.AMB._uv(self, faces, m)
        return MB._uv(self, faces, m)


def V(x, y, z=0.0):
    return Vector((x, y, z))


def solid(mb, pts, faces, m, bevel=0.0):
    vs = [mb.bm.verts.new(Vector(p)) for p in pts]
    for f in faces:
        try:
            mb.bm.faces.new([vs[i] for i in f])
        except ValueError:
            pass
    mb._post(vs, m, None, bevel, 1)


def hexa(mb, bot, top, m):
    solid(mb, list(bot) + list(top),
          [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], m)


def slab4(mb, top, thick, m):
    top = [Vector(p) for p in top]
    hexa(mb, [p - Vector((0, 0, thick)) for p in top], top, m)


class Face:
    """fachada de um bloco alinhado aos eixos, vista de fora: s = distancia ao longo dela (da esquerda para a
    direita de quem olha), out = distancia para fora da parede"""

    def __init__(self, x0, y0, x1, y1, side):
        if side == "S":
            self.o, self.t, self.n, self.L = (x0, y0), (1.0, 0.0), (0.0, -1.0), x1 - x0
        elif side == "N":
            self.o, self.t, self.n, self.L = (x1, y1), (-1.0, 0.0), (0.0, 1.0), x1 - x0
        elif side == "E":
            self.o, self.t, self.n, self.L = (x1, y0), (0.0, 1.0), (1.0, 0.0), y1 - y0
        else:
            self.o, self.t, self.n, self.L = (x0, y1), (0.0, -1.0), (-1.0, 0.0), y1 - y0
        self.yaw = math.atan2(self.t[1], self.t[0])

    def p(self, s, z, out=0.0):
        return V(self.o[0] + self.t[0] * s + self.n[0] * out, self.o[1] + self.t[1] * s + self.n[1] * out, z)

    def box(self, mb, s, z, sx, sy, sz, out, m, bevel=0.0):
        """caixa: sx ao longo da fachada, sy na normal (centro a 'out' da face), sz vertical"""
        mb.box((sx, sy, sz), self.p(s, z, out), (0, 0, self.yaw), m, bevel)

    def col(self, area, s, z, sx, sy, sz, out):
        col_box(area, (sx, sy, sz), self.p(s, z, out), (0, 0, self.yaw))


def faces4(x0, y0, x1, y1):
    return {k: Face(x0, y0, x1, y1, k) for k in "SENW"}


# ------------------------------------------------------------------ pecas das casas
def window(mb, f, s, zc, w, h, style="cross", glass=GLASS, frame="Wood_Dark", sill=True, awning=None):
    """janela de caixilho saliente: vidro recuado, moldura, montantes/ripas, peitoril e telhadinho opcional"""
    fw = 0.42
    f.box(mb, s, zc, w + 2 * fw, 0.3, h + 2 * fw, 0.1, frame)
    f.box(mb, s, zc, w, 0.3, h, 0.17, glass)
    if style == "cross":
        f.box(mb, s, zc, 0.26, 0.3, h, 0.25, frame)
        f.box(mb, s, zc, w, 0.3, 0.26, 0.25, frame)
    elif style == "two":
        f.box(mb, s, zc, 0.26, 0.3, h, 0.25, frame)
    elif style == "grid":
        f.box(mb, s, zc, 0.24, 0.3, h, 0.25, frame)
        f.box(mb, s, zc + h / 6, w, 0.3, 0.22, 0.25, frame)
        f.box(mb, s, zc - h / 6, w, 0.3, 0.22, 0.25, frame)
    elif style == "slats":
        k = max(3, int(round(w / 0.9)))
        for i in range(k):
            f.box(mb, s - w / 2 + w * (i + 0.5) / k, zc, 0.28, 0.3, h, 0.27, frame)
    if sill:
        f.box(mb, s, zc - h / 2 - fw - 0.1, w + 2 * fw + 0.5, 0.75, 0.26, 0.3, frame)
    if awning:
        za = zc + h / 2 + fw + 0.7
        a0, a1 = s - w / 2 - fw - 0.55, s + w / 2 + fw + 0.55
        slab4(mb, [f.p(a0, za - 0.62, 1.4), f.p(a1, za - 0.62, 1.4), f.p(a1, za, -0.1), f.p(a0, za, -0.1)], 0.3,
              awning)
        for sg in (-1, 1):
            mb.beam(f.p(s + sg * (w / 2 + fw), za - 1.25, 0.05), f.p(s + sg * (w / 2 + fw), za - 0.62, 1.1),
                    0.26, 0.26, frame, 0.0)


def round_window(mb, f, s, zc, r, glass=GLASS, frame="Wood_Dark"):
    """janela redonda: aro de madeira (varrido), vidro recuado e cruzeta"""
    n = 10
    pts = [f.p(s + math.cos(math.tau * k / n) * (r + 0.2), zc + math.sin(math.tau * k / n) * (r + 0.2), 0.17)
           for k in range(n + 1)]
    mb.sweep(pts, [(-0.24, -0.2), (0.24, -0.2), (0.24, 0.2), (-0.24, 0.2)], frame, True, up=(f.n[0], f.n[1], 0.0),
             caps=False)
    mb.cyl(r + 0.05, 0.2, f.p(s, zc, 0.04), (math.pi / 2, 0.0, math.atan2(f.n[0], -f.n[1])), glass, n, bevel=0.0)
    f.box(mb, s, zc, 0.22, 0.28, 2 * r, 0.12, frame)
    f.box(mb, s, zc, 2 * r, 0.28, 0.22, 0.12, frame)


def win_row(mb, f, zs, n, w=2.8, h=3.4, style="cross", glass=GLASS, margin=1.4, awning=None, rounds=(), skip=(),
            lit=(), styles=None, s0=0.0, s1=None):
    """n janelas iguais distribuidas na fachada entre s0 e s1; zs = cota do peitoril"""
    s1 = f.L if s1 is None else s1
    for i in range(n):
        if i in skip:
            continue
        s = s0 + margin + (s1 - s0 - 2 * margin) * (i + 0.5) / n
        g = LIT if i in lit else glass
        if i in rounds:
            round_window(mb, f, s, zs + h / 2, min(w, h) / 2 + 0.1, g)
        else:
            window(mb, f, s, zs + h / 2, w, h, (styles[i] if styles else style), g, awning=awning)


def stone_base(mb, x0, y0, x1, y1, z0, h, rng, out=0.45, blocks=True):
    """base de pedra: soco escuro + fiada de pedras claras salientes (juntas escuras)"""
    mb.box2((x0 - out, y0 - out, z0 - 0.8), (x1 + out, y1 + out, z0 + h), "Stone_Wall_Dark", 0.1)
    if not blocks:
        return
    for f in faces4(x0 - out, y0 - out, x1 + out, y1 + out).values():
        s = 0.0
        k = 0
        while s < f.L - 0.3:
            ln = min(rng.uniform(1.7, 2.9), f.L - s)
            if f.L - s - ln < 0.9:
                ln = f.L - s
            hh = h * (0.82 if k % 2 else 0.62) + rng.uniform(-0.08, 0.08)
            f.box(mb, s + ln / 2, z0 + hh / 2 - 0.12, ln - 0.16, 0.32, hh + 0.24, 0.04, "Stone_Wall_Light")
            s += ln
            k += 1


def walls(mb, x0, y0, x1, y1, z0, z1, wall_m="Plaster_Cream", band=0.8, posts=True, post=0.9):
    """corpo macico de reboco + cunhais de madeira + faixa escura sob o beiral"""
    mb.box2((x0, y0, z0), (x1, y1, z1), wall_m, 0.0)
    if posts:
        for px, py in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            mb.box((post, post, z1 - z0), (px, py, (z0 + z1) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    if band:
        mb.box2((x0 - 0.24, y0 - 0.24, z1 - band), (x1 + 0.24, y1 + 0.24, z1), "Wood_Dark", 0.0)


def floor_band(mb, x0, y0, x1, y1, z, h=0.7):
    mb.box2((x0 - 0.26, y0 - 0.26, z - h / 2), (x1 + 0.26, y1 + 0.26, z + h / 2), "Wood_Dark", 0.0)


# ------------------------------------------------------------------ telhados
def hip_roof(mb, x0, y0, x1, y1, z_w, m, g=0.55, over=2.2, thick=0.9, rib=1.85, ridge_m=RIDGE, tips=True,
             finial=True, rafters=0.0):
    """4 aguas com testeira grossa: forro rente ao topo da parede, canais de telha em relevo (rib = passo, 0 = sem),
    espigoes e cumeeira escuros com pontas levantadas. Devolve info (cotas, funcao de altura zf(x, y))."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    W, Dd = (x1 - x0) / 2 + over, (y1 - y0) / 2 + over
    zb = z_w - 0.05
    ze = zb + thick
    run = min(W, Dd)
    zr = ze + g * run
    X0, X1, Y0, Y1 = cx - W, cx + W, cy - Dd, cy + Dd
    E = [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]
    if abs(W - Dd) < 0.05:
        R = [(cx, cy)]
        tops = [(4, 5, 8), (5, 6, 8), (6, 7, 8), (7, 4, 8)]
        ends = [0, 0, 0, 0]
    elif W > Dd:
        R = [(cx - (W - Dd), cy), (cx + (W - Dd), cy)]
        tops = [(4, 5, 9, 8), (5, 6, 9), (6, 7, 8, 9), (7, 4, 8)]
        ends = [0, 1, 1, 0]
    else:
        R = [(cx, cy - (Dd - W)), (cx, cy + (Dd - W))]
        tops = [(4, 5, 8), (5, 6, 9, 8), (6, 7, 9), (7, 4, 8, 9)]
        ends = [0, 0, 1, 1]
    pts = [V(px, py, zb) for px, py in E] + [V(px, py, ze) for px, py in E] + [V(px, py, zr) for px, py in R]
    solid(mb, pts, [(3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)] + tops, m)
    if rib:
        for k in range(4):
            ax, ay = E[k]
            bx, by = E[(k + 1) % 4]
            Lk = math.hypot(bx - ax, by - ay)
            tx, ty = (bx - ax) / Lk, (by - ay) / Lk
            nx, ny = -ty, tx
            nrm = Vector((-nx * g, -ny * g, 1.0)).normalized()
            n = max(2, int(Lk / rib))
            for i in range(n):
                s = (i + 0.5) * Lk / n
                ln = min(s, Lk - s, run) - 0.45
                if ln < 0.9:
                    continue
                p = V(ax + tx * s - nx * 0.15, ay + ty * s - ny * 0.15, ze - g * 0.15)
                q = V(ax + tx * s + nx * ln, ay + ty * s + ny * ln, ze + g * ln)
                mb.beam(p + nrm * 0.15, q + nrm * 0.15, 0.46, 0.34, m, 0.0)
    up = Vector((0, 0, 1))
    Rv = [V(px, py, zr) for px, py in R]
    for k in range(4):
        c = V(E[k][0], E[k][1], ze)
        r_ = Rv[ends[k]]
        mb.beam(c + up * 0.2, r_ + up * 0.32, 0.74, 0.52, ridge_m, 0.0)
        if tips:
            dp = Vector((c.x - r_.x, c.y - r_.y, 0)).normalized()
            mb.beam(c + up * 0.05 - dp * 0.7, c + dp * 0.6 + up * 0.62, 0.84, 0.56, ridge_m, 0.0)
    if len(Rv) == 2:
        d = (Rv[1] - Rv[0]).normalized()
        mb.beam(Rv[0] - d * 0.45 + up * 0.45, Rv[1] + d * 0.45 + up * 0.45, 0.98, 0.78, ridge_m, 0.0)
        if finial:
            for q, sg in ((Rv[0], -1), (Rv[1], 1)):
                mb.box((0.9, 1.4, 1.5), q + d * sg * 0.35 + up * 1.2, (0, 0, math.atan2(d.y, d.x)), ridge_m, 0.0)
                mb.box((0.6, 1.0, 0.5), q + d * sg * 0.35 + up * 2.15, (0, 0, math.atan2(d.y, d.x)), ridge_m, 0.0)
    else:
        mb.cyl(0.8, 1.0, Rv[0] + up * 0.7, (0, 0, math.pi / 4), ridge_m, 4, r2=0.3, bevel=0.0)
        if finial:
            mb.cyl(0.32, 1.6, Rv[0] + up * 1.9, (0, 0, 0), ridge_m, 6, r2=0.08, bevel=0.0)

    if rafters:
        # pontas de caibro sob o beiral nas aguas compridas (vistas da altura do jogador)
        zc = zb - 0.22
        if W >= Dd:
            n = max(2, int((x1 - x0 - 1.2) / rafters))
            for i in range(n + 1):
                x = x0 + 0.6 + (x1 - x0 - 1.2) * i / n
                for ya, yb in ((y0 + 0.1, Y0 + 0.35), (y1 - 0.1, Y1 - 0.35)):
                    mb.beam(V(x, ya, zc), V(x, yb, zc), 0.42, 0.44, "Wood_Dark", 0.0)
        else:
            n = max(2, int((y1 - y0 - 1.2) / rafters))
            for i in range(n + 1):
                y = y0 + 0.6 + (y1 - y0 - 1.2) * i / n
                for xa, xb in ((x0 + 0.1, X0 + 0.35), (x1 - 0.1, X1 - 0.35)):
                    mb.beam(V(xa, y, zc), V(xb, y, zc), 0.42, 0.44, "Wood_Dark", 0.0)

    def zf(px, py):
        return min(zr, ze + g * max(0.0, min(px - X0, X1 - px, py - Y0, Y1 - py)))
    return dict(cx=cx, cy=cy, W=W, D=Dd, g=g, zb=zb, ze=ze, zr=zr, zf=zf)


def skirt_roof(mb, x0, y0, x1, y1, z_in, m, g=0.5, over=1.8, thick=0.55, rib=1.85, ridge_m=RIDGE, tips=True):
    """saia de telhado (aba entre pavimentos) em volta do bloco [x0,x1]x[y0,y1], nascendo na cota z_in"""
    ins = 0.3
    I = [(x0 + ins, y0 + ins), (x1 - ins, y0 + ins), (x1 - ins, y1 - ins), (x0 + ins, y1 - ins)]
    O = [(x0 - over, y0 - over), (x1 + over, y0 - over), (x1 + over, y1 + over), (x0 - over, y1 + over)]
    o = over + ins
    zo = z_in - g * o
    up = Vector((0, 0, 1))
    for k in range(4):
        j = (k + 1) % 4
        slab4(mb, [V(*O[k], zo), V(*O[j], zo), V(*I[j], z_in), V(*I[k], z_in)], thick, m)
        if rib:
            ax, ay = O[k]
            bx, by = O[j]
            Lk = math.hypot(bx - ax, by - ay)
            tx, ty = (bx - ax) / Lk, (by - ay) / Lk
            nx, ny = -ty, tx
            nrm = Vector((-nx * g, -ny * g, 1.0)).normalized()
            n = max(2, int(Lk / rib))
            for i in range(n):
                s = (i + 0.5) * Lk / n
                ln = min(s, Lk - s, o) - 0.4
                if ln < 0.7:
                    continue
                p = V(ax + tx * s - nx * 0.12, ay + ty * s - ny * 0.12, zo - g * 0.12)
                q = V(ax + tx * s + nx * ln, ay + ty * s + ny * ln, zo + g * ln)
                mb.beam(p + nrm * 0.14, q + nrm * 0.14, 0.44, 0.3, m, 0.0)
        c = V(*O[k], zo)
        ci = V(*I[k], z_in)
        mb.beam(c + up * 0.15, ci + up * 0.2, 0.62, 0.44, ridge_m, 0.0)
        if tips:
            dp = Vector((c.x - ci.x, c.y - ci.y, 0)).normalized()
            mb.beam(c + up * 0.02 - dp * 0.55, c + dp * 0.5 + up * 0.5, 0.72, 0.48, ridge_m, 0.0)


def col_roof(area, info):
    """colisao do telhado: 2 lajes inclinadas nas aguas compridas (quem cair no telhado nao entra na casa)"""
    a = math.atan(info["g"])
    cx, cy, W, Dd, ze, zr = info["cx"], info["cy"], info["W"], info["D"], info["ze"], info["zr"]
    run = min(W, Dd)
    hyp = run / math.cos(a)
    zc = (ze + zr) / 2 - 0.35
    if W >= Dd:
        for s in (-1, 1):
            col_box(area, (2 * W - run, hyp, 0.7), (cx, cy + s * run / 2, zc), (-s * a, 0, 0))
    else:
        for s in (-1, 1):
            col_box(area, (hyp, 2 * Dd - run, 0.7), (cx + s * run / 2, cy, zc), (0, s * a, 0))


def water_tank(mb, x, y, zf, z_plat, r=2.0, h=3.3, cap_m=RIDGE):
    """caixa d'agua de madeira sobre pes (a marca dos telhados de Konoha): pes descem ate a agua do telhado"""
    legs = []
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        px, py = x + sx * (r - 0.3), y + sy * (r - 0.3)
        zb = zf(px, py) - 0.3
        legs.append((px, py, zb))
        mb.box((0.5, 0.5, z_plat - zb), (px, py, (zb + z_plat) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    for i in range(4):
        a, b = legs[i], legs[(i + 1) % 4]
        za = max(a[2], b[2]) + 0.3
        if z_plat - za > 1.2:
            mb.beam(V(a[0], a[1], za), V(b[0], b[1], z_plat - 0.2), 0.26, 0.26, "Wood_Dark", 0.0)
    mb.box((2 * r + 0.6, 2 * r + 0.6, 0.45), (x, y, z_plat + 0.22), (0, 0, 0), "Wood_Plank", 0.0)
    zt = z_plat + 0.45
    mb.cyl(r, h, (x, y, zt + h / 2), (0, 0, 0), "Wood_Plank", 12, bevel=0.0)
    for zz in (zt + 0.55, zt + h - 0.55):
        mb.cyl(r + 0.1, 0.32, (x, y, zz), (0, 0, 0), "Wood_Dark", 12, bevel=0.0)
    mb.cyl(r + 0.35, 1.25, (x, y, zt + h + 0.62), (0, 0, 0), cap_m, 12, r2=0.4, bevel=0.0)
    px, py = x + r * 0.72, y - r * 0.72
    mb.rod((px, py, zt + 0.6), (px, py, zf(px, py) - 0.2), 0.17, "Wood_Dark", 6)


def balcony(mb, f, s0, s1, z, depth, rail=3.0, area=None):
    """varanda alta SEM acesso (nao ha porta): piso de tabuas, maos-francesas, guarda-corpo com balaustres"""
    sc, Lb = (s0 + s1) / 2, s1 - s0
    f.box(mb, sc, z - 0.25, Lb, depth + 0.3, 0.5, depth / 2 - 0.15, "Wood_Plank")
    f.box(mb, sc, z - 0.62, Lb + 0.2, 0.45, 0.42, depth - 0.2, "Wood_Dark")
    nb = max(2, int(Lb / 3.4) + 1)
    for i in range(nb):
        s = s0 + 0.45 + (Lb - 0.9) * i / (nb - 1)
        mb.beam(f.p(s, z - 2.7, 0.1), f.p(s, z - 0.6, depth - 0.55), 0.4, 0.4, "Wood_Dark", 0.0)
    np_ = max(2, int(Lb / 2.3) + 1)
    for i in range(np_):
        s = s0 + 0.22 + (Lb - 0.44) * i / (np_ - 1)
        f.box(mb, s, z + rail / 2, 0.44, 0.44, rail, depth - 0.22, "Wood_Dark")
    f.box(mb, sc, z + rail - 0.16, Lb, 0.5, 0.32, depth - 0.22, "Wood_Dark")
    f.box(mb, sc, z + 0.42, Lb, 0.36, 0.26, depth - 0.22, "Wood_Dark")
    nbal = int(Lb / 1.0)
    for i in range(nbal):
        s = s0 + (i + 0.5) * Lb / nbal
        f.box(mb, s, z + rail / 2 + 0.1, 0.24, 0.24, rail - 0.75, depth - 0.22, "Wood_Plank")
    for s in (s0 + 0.22, s1 - 0.22):
        f.box(mb, s, z + rail - 0.16, 0.5, depth, 0.32, depth / 2, "Wood_Dark")
        f.box(mb, s, z + 0.42, 0.36, depth, 0.26, depth / 2, "Wood_Dark")
        for k in range(1, int(depth / 1.0)):
            f.box(mb, s, z + rail / 2 + 0.1, 0.24, 0.24, rail - 0.75, k * 1.0, "Wood_Plank")
    if area:
        f.col(area, sc, z + (rail - 0.5) / 2, Lb, depth, rail + 0.5, depth / 2)


def shoji_wall(mb, f, s0, s1, zs, h):
    """fileira de janelas de grade atras das varandas: peitoril na altura do joelho (janela, nunca porta)"""
    n = max(2, int((s1 - s0) / 3.2))
    w = (s1 - s0) / n
    for i in range(n):
        window(mb, f, s0 + w * (i + 0.5), zs + h / 2, w - 1.0, h, "grid", LIT if i % 2 else GLASS)


# ------------------------------------------------------------------ casas do T1 / T2 / leste (detalhe "near")
def _box(h):
    x, y, w, d = h[0], h[1], h[2], h[3]
    return x - w / 2, y - d / 2, x + w / 2, y + d / 2


def house_T1_0(mb, rng):
    """(38,107) verde: terrea comprida + anexo baixo a leste + caixa d'agua sobre a cumeeira"""
    A = "HousesT1"
    h = L.HOUSES_T1[0]
    roof = h[5]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    xm = x0 + 11.0
    ay0, ay1 = y0 + 1.6, y1 - 1.6
    zt, za = z0 + 10.0, z0 + 7.0
    stone_base(mb, x0, y0, xm, y1, z0, 1.25, rng)
    stone_base(mb, xm, ay0, x1, ay1, z0, 1.0, rng)
    walls(mb, x0, y0, xm, y1, z0, zt)
    walls(mb, xm - 0.4, ay0, x1, ay1, z0, za, band=0.7)
    F = faces4(x0, y0, xm, y1)
    Fa = faces4(xm, ay0, x1, ay1)
    win_row(mb, F["S"], z0 + 3.0, 2, 3.0, 3.6, "slats", awning=roof, lit=(1,))
    win_row(mb, F["N"], z0 + 3.2, 2, 2.6, 3.2, "cross")
    round_window(mb, F["W"], 6.0, z0 + 7.3, 1.4, LIT)
    win_row(mb, F["W"], z0 + 2.4, 2, 2.2, 2.4, "two", margin=0.6)
    win_row(mb, Fa["S"], z0 + 2.8, 1, 2.2, 2.6, "two", margin=1.0)
    win_row(mb, Fa["E"], z0 + 2.8, 2, 2.4, 2.6, "cross", margin=0.8)
    win_row(mb, Fa["N"], z0 + 2.8, 1, 2.2, 2.6, "two", margin=1.0)
    info = hip_roof(mb, x0, y0, xm, y1, zt, roof, rafters=1.8)
    ia = hip_roof(mb, xm - 0.6, ay0, x1, ay1, za, roof, g=0.5, over=1.6, thick=0.7)
    water_tank(mb, info["cx"], info["cy"], info["zf"], info["zr"] + 1.3)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (xm + 0.45, y1 + 0.45, zt))
    col_box2(A, (xm, ay0 - 0.45, z0 - 0.5), (x1 + 0.45, ay1 + 0.45, za))
    col_roof(A, info)
    col_roof(A, ia)


def house_T1_1(mb, rng):
    """(-84,110) terracota: sobrado recuado - saia de telhado entre os pavimentos, 2o andar menor"""
    A = "HousesT1"
    h = L.HOUSES_T1[1]
    roof = h[5]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    z1, z2 = z0 + 9.0, z0 + 16.0
    ux0, uy0, ux1, uy1 = x0 + 2.5, y0 + 2.5, x1 - 2.5, y1 - 2.5
    stone_base(mb, x0, y0, x1, y1, z0, 1.2, rng)
    walls(mb, x0, y0, x1, y1, z0, z1, "Plaster_HouPeach", band=0.6)
    walls(mb, ux0, uy0, ux1, uy1, z1 - 1.0, z2, "Plaster_HouPeach")
    skirt_roof(mb, ux0, uy0, ux1, uy1, z1 + 0.5 + 0.5 * 2.5, roof, over=2.5 + 1.9)
    F = faces4(x0, y0, x1, y1)
    Fu = faces4(ux0, uy0, ux1, uy1)
    win_row(mb, F["S"], z0 + 2.8, 3, 2.8, 3.4, styles=("cross", "slats", "cross"), lit=(1,))
    win_row(mb, F["N"], z0 + 2.8, 3, 2.6, 3.2, "cross")
    win_row(mb, F["E"], z0 + 2.8, 2, 2.6, 3.2, "two")
    win_row(mb, F["W"], z0 + 2.8, 2, 2.6, 3.2, "slats")
    win_row(mb, Fu["S"], z1 + 2.5, 3, 2.3, 2.8, "cross", rounds=(1,), margin=1.0, lit=(1,))
    win_row(mb, Fu["N"], z1 + 2.5, 2, 2.3, 2.8, "cross", margin=1.2)
    win_row(mb, Fu["E"], z1 + 2.5, 1, 2.2, 2.8, "two", margin=1.0)
    win_row(mb, Fu["W"], z1 + 2.5, 1, 2.2, 2.8, "two", margin=1.0)
    info = hip_roof(mb, ux0, uy0, ux1, uy1, z2, roof, over=2.0, rafters=1.8)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, z1))
    col_box2(A, (ux0, uy0, z1), (ux1, uy1, z2))
    col_roof(A, info)


def house_T1_2(mb, rng):
    """(84,108) terracota: sobrado com varanda a oeste (para a vila) e caixa d'agua; canto SE recortado e anexo
    baixo e estreito (a ponte de saida comeca em (96,96): o bloco principal para em x 88, o anexo vai de y 106 ate o
    fundo e para em x 91 com o beiral abaixo de T1+7, livre dos pilones de lanterna da entrada da ponte em (94.6,108.7))"""
    A = "HousesT1"
    h = L.HOUSES_T1[2]
    roof = h[5]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    xm = x0 + 12.0
    x1 = x0 + 15.0
    ay0 = y0 + 4.5
    z1, z2, za = z0 + 9.0, z0 + 17.0, z0 + 6.0
    stone_base(mb, x0, y0, xm, y1, z0, 1.2, rng)
    stone_base(mb, xm, ay0, x1, y1, z0, 1.0, rng)
    walls(mb, x0, y0, xm, y1, z0, z2)
    floor_band(mb, x0, y0, xm, y1, z1)
    walls(mb, xm - 0.4, ay0, x1, y1, z0, za, band=0.6)
    F = faces4(x0, y0, xm, y1)
    Fa = faces4(xm, ay0, x1, y1)
    win_row(mb, F["S"], z0 + 2.8, 2, 2.8, 3.4, "slats")
    win_row(mb, F["S"], z1 + 2.0, 2, 2.4, 3.0, "cross", rounds=(0,), lit=(1,))
    win_row(mb, F["W"], z0 + 2.8, 2, 2.8, 3.2, "cross", margin=2.0)
    balcony(mb, F["W"], 2.2, F["W"].L - 2.2, z1 + 0.25, 2.2, area=A)
    shoji_wall(mb, F["W"], 2.8, F["W"].L - 2.8, z1 + 1.7, 3.4)
    win_row(mb, F["N"], z0 + 2.8, 2, 2.6, 3.2, "two")
    win_row(mb, F["N"], z1 + 2.0, 2, 2.4, 3.0, "cross")
    win_row(mb, F["E"], z1 + 3.0, 2, 2.2, 2.6, "two", margin=1.6)
    win_row(mb, F["E"], z0 + 2.8, 1, 2.2, 2.6, "two", s0=0.0, s1=ay0 - y0 + 0.4, margin=0.6)
    win_row(mb, Fa["E"], z0 + 2.4, 2, 2.2, 2.4, "cross", margin=0.9)
    win_row(mb, Fa["S"], z0 + 2.4, 1, 1.4, 2.2, "two", margin=0.3)
    info = hip_roof(mb, x0, y0, xm, y1, z2, roof, rafters=1.8)
    ia = hip_roof(mb, xm - 0.7, ay0, x1, y1, za, roof, g=0.5, over=0.9, thick=0.6)
    water_tank(mb, info["cx"], info["cy"] + 0.4, info["zf"], info["zr"] + 1.3, r=2.2)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (xm + 0.45, y1 + 0.45, z2))
    col_box2(A, (xm, ay0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, za))
    col_roof(A, info)


def house_T1_3(mb, rng):
    """(-112,84) azul: casa terrea com torre-mirante quadrada no canto NO (telhado piramidal proprio)"""
    A = "HousesT1"
    h = L.HOUSES_T1[3]
    roof = h[5]
    z0 = L.zone_of(h[0], h[1])
    x0, y0, x1, y1 = _box(h)
    tx0, ty0, tx1, ty1 = x0, y1 - 6.0, x0 + 6.0, y1
    z1, zt = z0 + 9.0, z0 + 19.5
    stone_base(mb, x0, y0, x1, y1, z0, 1.2, rng)
    walls(mb, x0, y0, x1, y1, z0, z1)
    walls(mb, tx0, ty0, tx1, ty1, z0, zt, band=0.7)
    floor_band(mb, tx0, ty0, tx1, ty1, z1 + 0.4, 0.6)
    F = faces4(x0, y0, x1, y1)
    Ft = faces4(tx0, ty0, tx1, ty1)
    win_row(mb, F["S"], z0 + 2.8, 3, 2.7, 3.4, styles=("cross", "slats", "cross"), awning=roof, lit=(1,))
    win_row(mb, F["E"], z0 + 2.8, 2, 2.6, 3.2, "cross")
    win_row(mb, F["N"], z0 + 2.8, 2, 2.4, 3.0, "two", s0=0.0, s1=x1 - tx1, margin=0.8)
    win_row(mb, F["W"], z0 + 2.8, 1, 2.6, 3.2, "slats", s0=ty1 - ty0, s1=F["W"].L, margin=1.2)
    for k, side in enumerate("SENW"):
        if side == "S":
            round_window(mb, Ft[side], 3.0, zt - 3.0, 1.25, LIT)
        else:
            window(mb, Ft[side], 3.0, zt - 3.0, 2.2, 2.6, "cross" if k % 2 else "slats", GLASS)
    info = hip_roof(mb, x0, y0, x1, y1, z1, roof, rafters=1.8)
    it = hip_roof(mb, tx0, ty0, tx1, ty1, zt, roof, g=0.8, over=1.6, thick=0.8, rib=1.5)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, z1))
    col_box2(A, (tx0, ty0, z1), (tx1, ty1, zt))
    col_roof(A, info)


def house_T2_0(mb, rng):
    """(-98,160) terracota: sobrado largo com varanda corrida ao sul e janelas redondas nas empenas"""
    A = "HousesT2"
    h = L.HOUSES_T2[0]
    roof = h[5]
    z0 = L.T2
    x0, y0, x1, y1 = _box(h)
    z1, z2 = z0 + 9.0, z0 + 16.5
    stone_base(mb, x0, y0, x1, y1, z0, 1.3, rng)
    walls(mb, x0, y0, x1, y1, z0, z2)
    floor_band(mb, x0, y0, x1, y1, z1)
    F = faces4(x0, y0, x1, y1)
    win_row(mb, F["S"], z0 + 2.8, 3, 2.8, 3.4, styles=("slats", "cross", "slats"), lit=(0,))
    balcony(mb, F["S"], 1.2, F["S"].L - 1.2, z1 + 0.25, 2.1, area=A)
    shoji_wall(mb, F["S"], 2.0, F["S"].L - 2.0, z1 + 1.7, 3.4)
    for side in "EW":
        win_row(mb, F[side], z0 + 2.8, 2, 2.6, 3.2, "cross")
        round_window(mb, F[side], F[side].L / 2, z1 + 3.6, 1.45, LIT if side == "W" else GLASS)
    win_row(mb, F["N"], z0 + 2.8, 3, 2.4, 3.0, "two")
    win_row(mb, F["N"], z1 + 2.0, 3, 2.2, 2.8, "cross")
    info = hip_roof(mb, x0, y0, x1, y1, z2, roof, rafters=1.8)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, z2))
    col_roof(A, info)


def house_T2_1(mb, rng):
    """(98,150) verde: terrea com caixa d'agua; pegada 13,5 x 12 com o centro 1,5 a oeste (o riacho leste passa em
    x ~104-113 na cota do T2 e cortava o canto NE da pegada da planta)"""
    A = "HousesT2"
    h = L.HOUSES_T2[1]
    roof = h[5]
    z0 = L.T2
    cx, cy, w, d = h[0] - 1.5, h[1] - 0.5, h[2] * 0.9, 12.0
    x0, y0, x1, y1 = cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2
    zt = z0 + 9.5
    stone_base(mb, x0, y0, x1, y1, z0, 1.2, rng)
    walls(mb, x0, y0, x1, y1, z0, zt, "Plaster_HouPeach")
    F = faces4(x0, y0, x1, y1)
    win_row(mb, F["S"], z0 + 2.8, 3, 2.6, 3.4, "cross", rounds=(1,), awning=roof, lit=(1,))
    win_row(mb, F["W"], z0 + 2.8, 2, 2.6, 3.2, "slats")
    win_row(mb, F["N"], z0 + 2.8, 2, 2.6, 3.2, "cross")
    win_row(mb, F["E"], z0 + 2.8, 2, 2.4, 3.0, "two")
    info = hip_roof(mb, x0, y0, x1, y1, zt, roof, rafters=1.8)
    water_tank(mb, info["cx"] + 1.0, info["cy"], info["zf"], info["zr"] + 1.4, r=2.3, h=3.6)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, zt))
    col_roof(A, info)


def house_T2_2(mb, rng):
    """(-126,136) verde: sobrado recuado de 2o andar quadrado com telhado piramidal (saia em volta do terreo)"""
    A = "HousesT2"
    h = L.HOUSES_T2[2]
    roof = h[5]
    z0 = L.T2
    x0, y0, x1, y1 = _box(h)
    z1, z2 = z0 + 8.5, z0 + 16.0
    ux0, uy0 = h[0] - 3.6, h[1] - 3.6
    ux1, uy1 = h[0] + 3.6, h[1] + 3.6
    stone_base(mb, x0, y0, x1, y1, z0, 1.2, rng)
    walls(mb, x0, y0, x1, y1, z0, z1, band=0.6)
    walls(mb, ux0, uy0, ux1, uy1, z1 - 1.0, z2)
    skirt_roof(mb, ux0, uy0, ux1, uy1, z1 + 0.5 + 0.5 * (ux0 - x0), roof, over=(ux0 - x0) + 1.7)
    F = faces4(x0, y0, x1, y1)
    Fu = faces4(ux0, uy0, ux1, uy1)
    win_row(mb, F["S"], z0 + 2.7, 3, 2.4, 3.2, styles=("cross", "slats", "cross"))
    win_row(mb, F["N"], z0 + 2.7, 2, 2.6, 3.2, "slats")
    win_row(mb, F["E"], z0 + 2.7, 2, 2.6, 3.2, "cross", lit=(0,))
    win_row(mb, F["W"], z0 + 2.7, 2, 2.4, 3.0, "two")
    for side in "SENW":
        round_window(mb, Fu[side], Fu[side].L / 2, z1 + 4.2, 1.3, LIT if side in "SE" else GLASS)
    info = hip_roof(mb, ux0, uy0, ux1, uy1, z2, roof, g=0.75, over=2.0, rib=1.6, rafters=1.8)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, z1))
    col_box2(A, (ux0, uy0, z1), (ux1, uy1, z2))


def house_E_0(mb, rng):
    """(134,-26) terracota: sobrado na beira do penhasco leste sobre um embasamento de pedra que desce a encosta
    (a pegada da planta passa ~6 studs do topo do penhasco no canto SE); varanda alta virada para o mar"""
    A = "HousesEast"
    h = L.EAST_HOUSES[0]
    roof = h[5]
    z0 = L.G
    x0, y0, x1, y1 = _box(h)
    zp = z0 + 1.6
    z1, z2 = zp + 8.6, zp + 15.6
    # embasamento: bloco de pedra ate a prateleira do penhasco, com fiadas nas faces L e S
    mb.box2((x0 - 0.9, y0 - 0.9, L.SHELF_Z - 2.0), (x1 + 0.9, y1 + 0.9, zp), "Stone_Wall_Dark", 0.12)
    for side in "SE":
        f = Face(x0 - 0.9, y0 - 0.9, x1 + 0.9, y1 + 0.9, side)
        z = zp - 0.1
        row = 0
        while z > L.SHELF_Z - 1.0:
            hh = 1.5
            s = -rng.uniform(0.0, 1.2) if row % 2 else 0.0
            while s < f.L - 0.2:
                ln = rng.uniform(2.2, 3.6)
                a, b = max(s, 0.0), min(s + ln, f.L)
                if b - a > 0.4:
                    f.box(mb, (a + b) / 2, z - hh / 2, b - a - 0.18, 0.4, hh - 0.18, 0.05,
                          "Stone_Wall_Light" if rng.random() > 0.15 else "Stone_Wall_Dark")
                s += ln
            z -= hh
            row += 1
    mb.box2((x0 - 1.1, y0 - 1.1, zp - 0.1), (x1 + 1.1, y1 + 1.1, zp + 0.35), "Stone_Wall_Light", 0.1)
    walls(mb, x0, y0, x1, y1, zp, z2)
    floor_band(mb, x0, y0, x1, y1, z1)
    F = faces4(x0, y0, x1, y1)
    win_row(mb, F["W"], zp + 2.6, 2, 2.8, 3.4, "slats", lit=(0,))
    win_row(mb, F["W"], z1 + 1.9, 2, 2.4, 3.0, "cross")
    win_row(mb, F["S"], zp + 2.6, 2, 2.6, 3.2, "cross")
    win_row(mb, F["S"], z1 + 1.9, 2, 2.4, 3.0, "cross", rounds=(1,))
    win_row(mb, F["N"], zp + 2.6, 2, 2.6, 3.2, "two")
    win_row(mb, F["N"], z1 + 1.9, 2, 2.4, 3.0, "two")
    win_row(mb, F["E"], zp + 2.6, 2, 2.2, 2.8, "cross")
    balcony(mb, F["E"], 1.4, F["E"].L - 1.4, z1 + 0.25, 2.2, area=A)
    shoji_wall(mb, F["E"], 2.2, F["E"].L - 2.2, z1 + 1.7, 3.4)
    info = hip_roof(mb, x0, y0, x1, y1, z2, roof, rafters=1.8)
    col_box2(A, (x0 - 0.9, y0 - 0.9, z0 - 1.0), (x1 + 0.9, y1 + 0.9, zp))
    col_box2(A, (x0 - 0.3, y0 - 0.3, zp), (x1 + 0.3, y1 + 0.3, z2))
    col_roof(A, info)


def house_E_1(mb, rng):
    """(136,36) verde: sobrado 'kura' - 2o andar do mesmo tamanho com saia de telhado entre os pavimentos"""
    A = "HousesEast"
    h = L.EAST_HOUSES[1]
    roof = h[5]
    z0 = L.G
    x0, y0, x1, y1 = _box(h)
    z1, z2 = z0 + 8.6, z0 + 15.8
    stone_base(mb, x0, y0, x1, y1, z0, 1.3, rng)
    walls(mb, x0, y0, x1, y1, z0, z2, "Plaster_HouPeach")
    skirt_roof(mb, x0, y0, x1, y1, z1 + 0.3, roof, over=1.6, g=0.55)
    F = faces4(x0, y0, x1, y1)
    win_row(mb, F["W"], z0 + 2.7, 3, 2.4, 3.2, styles=("cross", "slats", "cross"), lit=(1,))
    win_row(mb, F["W"], z1 + 2.2, 2, 2.4, 2.8, "cross", rounds=(1,))
    win_row(mb, F["S"], z0 + 2.7, 2, 2.6, 3.2, "slats")
    win_row(mb, F["S"], z1 + 2.2, 2, 2.2, 2.8, "two")
    win_row(mb, F["N"], z0 + 2.7, 2, 2.6, 3.2, "cross")
    win_row(mb, F["N"], z1 + 2.2, 1, 2.2, 2.8, "cross")
    win_row(mb, F["E"], z0 + 2.7, 2, 2.4, 3.0, "two")
    round_window(mb, F["E"], F["E"].L / 2, z1 + 3.6, 1.35, GLASS)
    info = hip_roof(mb, x0, y0, x1, y1, z2, roof, rafters=1.8)
    col_box2(A, (x0 - 0.45, y0 - 0.45, z0 - 0.5), (x1 + 0.45, y1 + 0.45, z2))
    col_roof(A, info)


def houses_near():
    mb = HMB("VIL_Houses_Near", "04_VILLAGE", random.Random(4401), detail="near", vmax=1)
    for i, fn in enumerate((house_T1_0, house_T1_1, house_T1_2, house_T1_3, house_T2_0, house_T2_1, house_T2_2,
                            house_E_0, house_E_1)):
        fn(mb, random.Random(4410 + i))
    mb.finish()


# ------------------------------------------------------------------ plato de cima (simples, "far")
UPPER = [  # x, y, w, d, altura, telhado, tipo
    (-66.0, 196.0, 12.0, 9.0, 8.0, "Roof_Terracotta", "plain"),
    (-33.0, 197.0, 10.0, 10.0, 7.5, "Roof_Green", "tower"),
    (2.0, 198.0, 13.0, 10.0, 8.5, "Roof_Blue", "tank"),
    (32.0, 197.0, 10.0, 9.0, 7.5, "Roof_Terracotta", "skirt"),
    (62.0, 195.5, 12.0, 9.0, 8.0, "Roof_Green", "annex"),
]


def far_window(mb, f, s, zc, w, h, glass=GLASS):
    f.box(mb, s, zc, w + 0.7, 0.3, h + 0.7, 0.1, "Wood_Dark")
    f.box(mb, s, zc, w, 0.3, h, 0.2, glass)


def houses_upper():
    """5 casinhas no topo do paredao (cota L.CLIFF_TOP): silhueta e cor, sem chanfro e sem fundo apoiado"""
    A = "HousesUpper"
    mb = HMB("VIL_Houses_Upper", "04_VILLAGE", random.Random(4402), detail="far", floor=L.CLIFF_TOP, vmax=1)
    z0 = L.CLIFF_TOP
    for i, (x, y, w, d, hh, roof, kind) in enumerate(UPPER):
        x0, y0, x1, y1 = x - w / 2, y - d / 2, x + w / 2, y + d / 2
        mb.box2((x0 - 0.4, y0 - 0.4, z0 - 0.6), (x1 + 0.4, y1 + 0.4, z0 + 1.0), "Stone_Wall_Dark", 0.0)
        walls(mb, x0, y0, x1, y1, z0, z0 + hh, "Plaster_Cream" if i % 2 == 0 else "Plaster_HouPeach", band=0.7,
              post=0.8)
        F = faces4(x0, y0, x1, y1)
        ns = max(2, int(w / 4.2))
        for k in range(ns):
            far_window(mb, F["S"], 1.2 + (w - 2.4) * (k + 0.5) / ns, z0 + 4.2, 2.2, 2.6, LIT if (i + k) % 3 == 0 else GLASS)
        for side in "EW":
            far_window(mb, F[side], d / 2, z0 + 4.2, 2.0, 2.4)
        far_window(mb, F["N"], w / 2, z0 + 4.2, 2.2, 2.4)
        top = z0 + hh
        if kind == "tower":
            ux0, uy0, ux1, uy1 = x0 + 1.8, y0 + 1.8, x1 - 1.8, y1 - 1.8
            skirt_roof(mb, ux0, uy0, ux1, uy1, top + 0.5 + 0.9, roof, over=1.8 + 1.5, rib=0, tips=False)
            walls(mb, ux0, uy0, ux1, uy1, top - 1.0, top + 6.0, band=0.6, post=0.7)
            far_window(mb, Face(ux0, uy0, ux1, uy1, "S"), (ux1 - ux0) / 2, top + 3.0, 1.8, 2.2, LIT)
            hip_roof(mb, ux0, uy0, ux1, uy1, top + 6.0, roof, g=0.8, over=1.6, thick=0.7, rib=0, tips=False)
            ztop = top + 6.0
        elif kind == "skirt":
            ux0, uy0, ux1, uy1 = x0 + 2.0, y0 + 2.0, x1 - 2.0, y1 - 2.0
            skirt_roof(mb, ux0, uy0, ux1, uy1, top + 0.5 + 1.0, roof, over=2.0 + 1.5, rib=0, tips=False)
            walls(mb, ux0, uy0, ux1, uy1, top - 1.0, top + 5.0, band=0.6, post=0.7)
            far_window(mb, Face(ux0, uy0, ux1, uy1, "S"), (ux1 - ux0) / 2, top + 3.0, 2.0, 1.8)
            hip_roof(mb, ux0, uy0, ux1, uy1, top + 5.0, roof, over=1.7, thick=0.7, rib=0, tips=False)
            ztop = top + 5.0
        else:
            info = hip_roof(mb, x0, y0, x1, y1, top, roof, over=1.9, thick=0.8, rib=0, tips=kind != "plain")
            ztop = top
            if kind == "tank":
                water_tank(mb, info["cx"] - 1.5, info["cy"], info["zf"], info["zr"] + 1.2, r=1.9, h=3.0)
            if kind == "annex":
                mb.box2((x1 - 0.3, y0 + 1.5, z0), (x1 + 4.0, y1 - 1.5, z0 + 5.5), "Plaster_Cream", 0.0)
                hip_roof(mb, x1 - 0.8, y0 + 1.5, x1 + 4.0, y1 - 1.5, z0 + 5.5, roof, g=0.5, over=1.2, thick=0.6,
                         rib=0, tips=False, finial=False)
        col_box2(A, (x0 - 0.4, y0 - 0.4, z0 - 0.5), (x1 + 0.4, y1 + 0.4, ztop))
    mb.finish()


# ------------------------------------------------------------------ MOINHO DE MINERIO / Posto do Minerador
MX, MY, MW, MD = L.MILL
MX0, MX1 = MX - MW / 2, MX + MW / 2          # 93, 107
MY0, MY1 = MY - MD / 2, MY + MD / 2          # 3, 21
TW = 1.2                                     # espessura das paredes
IX0, IX1, IY0, IY1 = MX0 + TW, MX1 - TW, MY0 + TW, MY1 - TW
FL = G + 0.3                                 # piso de tabuas
ZS = G + 5.0                                 # topo da alvenaria (pedra) -> tabuado em cima
ZW = G + 16.0                                # topo das paredes (frechal)
CEIL = ZW - 0.8                              # forro (face de baixo do frechal/laje) -> pe-direito 14,9
AX_Z = G + 8.0                               # eixo da roda (L.WHEEL: raio 11, eixo L-O na cota G+8)
DY0, DY1 = MY - 4.0, MY + 4.0                # vao da porta oeste (8 de largura)
DZ1 = FL + 10.8                              # topo do vao (10,8 livres)
WX = L.WHEEL[0]
GEAR_X = IX1 - 1.6                           # engrenagens (roda de coroa no eixo da roda + pinhao da arvore de cames)
GA_R, GB_R = 2.5, 1.2                        # raios (aro) das engrenagens
CAM_Y = MY + GA_R + GB_R + 1.2               # arvore de cames (paralela ao eixo da roda, ao norte): ponta x raiz
STAMP_Y = CAM_Y + 1.6                        # socos do pilao (encostados no muro norte)
STAMPS_X = (96.8, 99.0, 101.2)
BED_Z = FL + 2.4                             # leito de minerio dentro do pilao
WHEEL_RPM = -4.0                             # rpm do VFX_WATER_Wheel (agente de agua): a roda de coroa acompanha


def _wall_lines():
    """linhas de centro das paredes (a -> b) e a coordenada de mundo que mede o 's' de cada uma"""
    return {"S": (V(MX0, MY0 + TW / 2), V(MX1, MY0 + TW / 2), "x", MX0),
            "N": (V(MX0, MY1 - TW / 2), V(MX1, MY1 - TW / 2), "x", MX0),
            "W": (V(MX0 + TW / 2, IY0), V(MX0 + TW / 2, IY1), "y", IY0),
            "E": (V(MX1 - TW / 2, IY0), V(MX1 - TW / 2, IY1), "y", IY0)}


# aberturas do moinho: parede -> [(u0, u1, z0, z1, janela?)] com u = x (S/N) ou y (L/O) do mundo
MILL_OPEN = {
    "W": [(DY0, DY1, G - 0.7, DZ1, "door"), (4.8, 6.9, ZS + 0.9, ZS + 3.7, "win"),
          (17.1, 19.2, ZS + 0.9, ZS + 3.7, "win")],
    "E": [(5.4, 8.4, ZS + 4.4, ZS + 8.0, "win"), (15.6, 18.6, ZS + 4.4, ZS + 8.0, "win"),
          (MY - 0.75, MY + 0.75, AX_Z - 0.75, AX_Z + 0.75, "hole")],
    "N": [(95.0, 97.6, ZS + 4.0, ZS + 7.6, "win"), (102.4, 105.0, ZS + 4.0, ZS + 7.6, "win"),
          (98.4, 100.4, ZS + 0.7, ZS + 2.9, "hole")],
    "S": [(95.2, 97.8, ZS + 4.6, ZS + 8.2, "win"), (102.2, 104.8, ZS + 4.6, ZS + 8.2, "win")],
}


def mill_shell(mb, rng):
    A = "HousesMill"
    lines = _wall_lines()
    Fo = faces4(MX0, MY0, MX1, MY1)
    for side, (a, b, ax, u0) in lines.items():
        Lw = (b - a).length
        d = (b - a).normalized()
        ang = math.atan2(d.y, d.x)
        ops = [(o[0] - u0, o[1] - u0, o[2], o[3]) for o in MILL_OPEN[side]]
        # alvenaria de pedra ate ZS (blocos atravessam a parede: aparecem por dentro e por fora)
        FP.masonry_wall(mb, a, b, G - 0.6, ZS, TW, rng, m="Stone_Wall_Light", m2="Stone_Wall_Dark", course=1.45,
                        mix=0.1, openings=[o for o in ops if o[2] < ZS], blk=(2.2, 3.6),
                        quoins=(side in "SN", side in "SN"), core_m="Stone_Wall_Dark", bevel=0.0)
        # tabuado ate o frechal (laje de tabuas recortada nas aberturas)
        FP._masonry_core(mb, a, d, ang, Lw, ZS, ZW - 0.8, TW - 0.2, [o for o in ops if o[3] > ZS], "Wood_Plank")
        # mata-juntas por fora + montantes que atravessam a parede
        f = Fo[side]
        up = [o for o in MILL_OPEN[side]]
        for k in range(int(f.L / 1.45) + 1):
            s = 0.7 + k * 1.45
            if s > f.L - 0.6:
                break
            u = _face_u(side, s)
            spans = _vspans(u, ZS + 0.35, ZW - 0.8, up)
            for za, zb in spans:
                if zb - za > 0.5:
                    f.box(mb, s, (za + zb) / 2, 0.34, 0.3, zb - za, 0.1, "Wood_Dark")
        n = 3 if f.L > 15 else 2
        for k in range(1, n + 1):
            s = f.L * k / (n + 1)
            u = _face_u(side, s)
            if any(o[0] - 0.9 < u < o[1] + 0.9 and o[3] > ZS for o in up):
                continue
            f.box(mb, s, (ZS + ZW) / 2, 0.8, TW + 0.5, ZW - ZS, TW / 2, "Wood_Dark")
        # travessa de apoio do tabuado sobre a pedra (interrompida na porta)
        segs = [(0.0, f.L)]
        for o in up:
            if o[2] < ZS + 0.3 < o[3]:
                s0, s1 = sorted((_face_s(side, o[0]), _face_s(side, o[1])))
                segs = [(p, min(q, s0)) for p, q in segs if min(q, s0) - p > 0.3] + \
                       [(max(p, s1), q) for p, q in segs if q - max(p, s1) > 0.3]
        for s0, s1 in segs:
            f.box(mb, (s0 + s1) / 2, ZS + 0.3, s1 - s0, TW + 0.5, 0.6, TW / 2, "Wood_Dark")
        # janelas (vidro aceso: o moinho trabalha)
        for (ua, ub, za, zb, kind) in up:
            if kind != "win":
                continue
            sa, sb = sorted((_face_s(side, ua), _face_s(side, ub)))
            window(mb, f, (sa + sb) / 2, (za + zb) / 2, sb - sa, zb - za, "grid", LIT)
    # cunhais de madeira (acima da pedra) e frechal/forro (laje: e o teto visto de dentro)
    for px, py in ((MX0, MY0), (MX1, MY0), (MX1, MY1), (MX0, MY1)):
        mb.box((1.1, 1.1, ZW - ZS + 0.3), (px, py, (ZS + ZW) / 2 - 0.15), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box2((MX0 - 0.3, MY0 - 0.3, ZW - 0.8), (MX1 + 0.3, MY1 + 0.3, ZW), "Wood_Dark", 0.0)
    # vigotas do forro (de dentro)
    for k in range(5):
        y = IY0 + 1.6 + k * (IY1 - IY0 - 3.2) / 4
        mb.box2((IX0, y - 0.35, CEIL - 0.7), (IX1, y + 0.35, CEIL), "Wood_Plank", 0.0)
    # porta: ombreiras, verga, soleira de pedra (vao aberto, sem folha)
    xw = MX0 + TW / 2
    for y in (DY0 - 0.45, DY1 + 0.45):
        mb.box((TW + 0.5, 0.9, DZ1 + 1.0 - G), (xw, y, (G + DZ1 + 1.0) / 2), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((TW + 0.6, DY1 - DY0 + 2.4, 1.0), (xw, MY, DZ1 + 0.5), (0, 0, 0), "Wood_Dark", 0.0)
    mb.box((TW + 1.6, DY1 - DY0 + 0.6, 0.3), (xw - 0.2, MY, FL - 0.15), (0, 0, 0), "Stone_Wall_Light", 0.0)
    # alpendre (hisashi) sobre a porta com maos-francesas
    zc = DZ1 + 2.3
    slab4(mb, [V(MX0 - 3.3, DY0 - 2.4, zc - 1.25), V(MX0 - 3.3, DY1 + 2.4, zc - 1.25), V(MX0 + 0.1, DY1 + 2.4, zc),
               V(MX0 + 0.1, DY0 - 2.4, zc)], 0.45, "Roof_Terracotta")
    g = 1.25 / 3.4
    nrm = Vector((-g, 0.0, 1.0)).normalized()
    for k in range(9):
        y = DY0 - 2.0 + k * (DY1 - DY0 + 4.0) / 8
        mb.beam(V(MX0 - 3.45, y, zc - 1.3) + nrm * 0.14, V(MX0 - 0.1, y, zc - 0.05) + nrm * 0.14, 0.44, 0.32,
                "Roof_Terracotta", 0.0)
    mb.beam(V(MX0 - 3.4, DY0 - 2.55, zc - 1.1), V(MX0 - 3.4, DY1 + 2.55, zc - 1.1), 0.5, 0.5, RIDGE, 0.0)
    for y in (DY0 - 1.7, DY1 + 1.7):
        mb.beam(V(MX0 - 0.1, y, DZ1 - 1.6), V(MX0 - 2.9, y, zc - 1.5), 0.45, 0.45, "Wood_Dark", 0.0)
        mb.beam(V(MX0 - 0.1, y, zc - 0.5), V(MX0 - 2.9, y, zc - 1.5), 0.4, 0.4, "Wood_Dark", 0.0)
    # placa redonda com a picareta (o jogador entende a funcao sem texto)
    pz = zc + 0.95
    mb.cyl(1.12, 0.35, (MX0 - 0.55, MY, pz), (0, math.pi / 2, 0), "Wood_Dark", 16, bevel=0.0)
    mb.cyl(0.92, 0.2, (MX0 - 0.7, MY, pz), (0, math.pi / 2, 0), "Wood_Plank", 16, bevel=0.0)
    # picareta de verdade presa na placa (cabo de madeira + cabeca de ferro): materiais que o moinho ja tem em
    # quantidade (um emblema creme minusculo seria dobrado no vizinho pelo export e sumiria no Roblox)
    xa = MX0 - 0.93
    pa, pb = V(xa, MY - 0.5, pz - 0.62), V(xa, MY + 0.42, pz + 0.44)
    mb.beam(pa, pb, 0.24, 0.26, "Wood_Dark", 0.0)
    ax = (pb - pa).normalized()
    hd = Vector((0.0, -ax.z, ax.y)).normalized()
    for sg in (-1, 1):
        mb.beam(pb - ax * 0.05, pb + hd * sg * 0.7 - ax * 0.22, 0.26, 0.3, "Metal_Dark", 0.0)
    # telhado de 4 aguas + lanternim de ventilacao na cumeeira
    info = hip_roof(mb, MX0, MY0, MX1, MY1, ZW, "Roof_Terracotta", g=0.58, over=2.2, thick=1.0)
    zr = info["zr"]
    mb.box2((MX - 1.3, MY - 2.2, zr - 0.8), (MX + 1.3, MY + 2.2, zr + 1.6), "Wood_Dark", 0.0)
    for k in range(3):
        for sx in (-1, 1):
            mb.box((0.3, 4.0, 0.36), (MX + sx * 1.38, MY, zr - 0.1 + k * 0.55), (0, sx * 0.55, 0), "Wood_Plank", 0.0)
    hip_roof(mb, MX - 1.3, MY - 2.2, MX + 1.3, MY + 2.2, zr + 1.6, "Roof_Terracotta", g=0.6, over=0.8, thick=0.5,
             rib=0, finial=False, tips=False)
    col_roof(A, info)
    # piso de tabuas
    FP.plank_floor(mb, FP.Frame(MX, MY, 0.0, 0.0), IX1 - IX0, IY1 - IY0, G + 0.02, rng, m="Wood_Plank", pw=1.25,
                   m_alt=("Wood_Plank", "Wood_Dark"))
    # colisao da casca: paredes com vao da porta, piso, forro
    col_box2(A, (MX0, MY0, G - 0.6), (MX1, MY0 + TW, ZW))
    col_box2(A, (MX0, MY1 - TW, G - 0.6), (MX1, MY1, ZW))
    col_box2(A, (MX1 - TW, MY0 + TW, G - 0.6), (MX1, MY1 - TW, ZW))
    col_box2(A, (MX0, MY0 + TW, G - 0.6), (MX0 + TW, DY0, ZW))
    col_box2(A, (MX0, DY1, G - 0.6), (MX0 + TW, MY1 - TW, ZW))
    col_box2(A, (MX0, DY0, DZ1), (MX0 + TW, DY1, ZW))
    col_box2(A, (MX0 - 0.6, DY0, G - 0.4), (IX0, DY1, FL))
    col_box2(A, (IX0, IY0, G - 0.4), (IX1, IY1, FL))
    col_box2(A, (IX0, IY0, CEIL), (IX1, IY1, ZW))
    return info


def _face_s(side, u):
    """coordenada de mundo (x ou y) -> s da fachada externa (Face)"""
    if side == "S":
        return u - MX0
    if side == "N":
        return MX1 - u
    if side == "E":
        return u - MY0
    return MY1 - u


def _face_u(side, s):
    if side == "S":
        return MX0 + s
    if side == "N":
        return MX1 - s
    if side == "E":
        return MY0 + s
    return MY1 - s


def _vspans(u, za, zb, ops):
    """trechos verticais [za, zb] na coordenada u que nao caem em nenhuma abertura"""
    spans = [(za, zb)]
    for o in ops:
        if o[0] - 0.3 < u < o[1] + 0.3:
            new = []
            for p, q in spans:
                if q <= o[2] - 0.2 or p >= o[3] + 0.2:
                    new.append((p, q))
                    continue
                if o[2] - 0.2 > p:
                    new.append((p, o[2] - 0.2))
                if o[3] + 0.2 < q:
                    new.append((o[3] + 0.2, q))
            spans = new
    return spans


def mill_exterior(mb, rng):
    """lado da roda (chapa de mancal; os pilares de apoio sao do WATER_Wheel_Frame), telheiro sul com caixotes,
    tremonha + calha de minerio ao norte, arandela"""
    A = "HousesMill"
    # chapa de mancal onde o eixo atravessa a parede leste + pilar de alvenaria com mancal na margem do riacho
    mb.box((0.35, 3.2, 3.2), (MX1 + 0.18, MY, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    for dy in (-1.15, 1.15):
        for dz in (-1.15, 1.15):
            mb.box((0.3, 0.42, 0.42), (MX1 + 0.4, MY + dy, AX_Z + dz), (0, 0, 0), "Metal_Iron", 0.0)
    # telheiro sul (meia-agua em 3 pilares) com caixotes de cristal, barril e ferramentas
    ys = MY0 - 5.2
    for x in (MX0 + 1.2, MX, MX1 - 1.2):
        mb.box((0.75, 0.75, 6.3), (x, ys + 0.4, G + 3.15), (0, 0, 0), "Wood_Dark", 0.0)
        mb.box((1.3, 1.3, 0.5), (x, ys + 0.4, G + 0.25), (0, 0, 0), "Stone_Wall_Dark", 0.0)
        col_box2(A, (x - 0.45, ys - 0.05, G - 0.3), (x + 0.45, ys + 0.85, G + 6.3))
    mb.beam(V(MX0 + 0.4, ys + 0.4, G + 6.1), V(MX1 - 0.4, ys + 0.4, G + 6.1), 0.7, 0.7, "Wood_Dark", 0.0)
    zh, zl = G + 8.6, G + 6.3
    slab4(mb, [V(MX0 - 0.6, ys - 0.9, zl), V(MX1 + 0.6, ys - 0.9, zl), V(MX1 + 0.6, MY0 + 0.1, zh),
               V(MX0 - 0.6, MY0 + 0.1, zh)], 0.42, "Roof_Terracotta")
    gg = (zh - zl) / (MY0 + 0.1 - ys + 0.9)
    nrm = Vector((0.0, -gg, 1.0)).normalized()
    for k in range(9):
        x = MX0 + (k + 0.5) * (MW + 1.2) / 9 - 0.6
        mb.beam(V(x, ys - 1.05, zl - 0.06) + nrm * 0.14, V(x, MY0 - 0.1, zh - 0.08) + nrm * 0.14, 0.44, 0.3,
                "Roof_Terracotta", 0.0)
    mb.beam(V(MX0 - 0.7, ys - 1.0, zl - 0.15), V(MX1 + 0.7, ys - 1.0, zl - 0.15), 0.5, 0.5, RIDGE, 0.0)
    for i, (x, y, s) in enumerate(((MX0 + 2.6, MY0 - 2.2, 2.2), (MX0 + 5.0, MY0 - 2.0, 2.0), (MX0 + 2.7, MY0 - 2.2, 1.6))):
        z = G + (2.2 if i == 2 else 0.0)
        FP.crate(mb, (x, y, z), s, rng.uniform(-0.2, 0.2), rng)
    _open_crate(mb, (MX + 2.4, MY0 - 2.3, G), 2.2, 0.15, rng)
    FP.barrel(mb, (MX1 - 2.0, MY0 - 2.4, G), 1.0, 2.5)
    col_box2(A, (MX0 + 1.3, MY0 - 3.5, G - 0.3), (MX0 + 6.2, MY0 - 0.9, G + 3.9))
    col_box2(A, (MX + 1.2, MY0 - 3.5, G - 0.3), (MX1 - 0.8, MY0 - 1.2, G + 2.5))
    _pickaxes(mb, MX + 5.0, MY0 - 0.05, -1)
    # tremonha de minerio + calha que entra pelo muro norte e despeja no pilao
    hx, hy = 99.4, MY1 + 3.9
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.6, 0.6, 7.6), (hx + sx * 1.5, hy + sy * 1.5, G + 3.8), (0, 0, 0), "Wood_Dark", 0.0)
        mb.beam(V(hx + sx * 1.5, hy - 1.5, G + 1.2), V(hx + sx * 1.5, hy + 1.5, G + 6.4), 0.3, 0.3, "Wood_Dark", 0.0)
    FP.frustum(mb, (hx, hy, G + 7.4), 1.7, 1.7, 4.6, 4.6, 3.2, "Wood_Plank")
    for sx, sy, lx, ly in ((0, -1, 5.0, 0.5), (0, 1, 5.0, 0.5), (-1, 0, 0.5, 4.0), (1, 0, 0.5, 4.0)):
        mb.box((lx, ly, 0.55), (hx + sx * 2.3, hy + sy * 2.3, G + 10.75), (0, 0, 0), "Wood_Dark", 0.0)
    for k in range(5):
        a = k * math.tau / 5 + 0.4
        mb.rock((hx + math.cos(a) * 1.3, hy + math.sin(a) * 1.3, G + 10.7), (1.3, 1.1, 0.8), "Stone_Wall_Dark", 1)
    for k in range(2):
        a = k * math.pi + 1.1
        FP.crystal_cluster(mb, (hx + math.cos(a) * 0.8, hy + math.sin(a) * 0.8, G + 10.5), 0.55, "Crystal_Blue", rng, 3)
    _chute(mb, V(hx, hy - 0.5, G + 7.7), V(hx, STAMP_Y + 0.45, AX_Z - 2.4))
    col_box2(A, (hx - 2.5, hy - 2.5, G - 0.3), (hx + 2.5, hy + 2.5, G + 10.9))
    FP.mine_cart(mb, (hx + 4.6, hy + 0.6, G), math.pi / 2, "Crystal_Blue", rng)
    col_box2(A, (hx + 3.3, hy - 1.3, G - 0.3), (hx + 5.9, hy + 2.5, G + 3.4))
    # arandela na porta
    lz = G + 11.0
    ly = DY1 + 1.3
    mb.box((0.3, 0.9, 1.8), (MX0 - 0.15, ly, lz + 0.2), (0, 0, 0), "Wood_Dark", 0.0)
    mb.beam(V(MX0 - 0.2, ly, lz + 0.8), V(MX0 - 1.5, ly, lz + 0.8), 0.25, 0.25, "Metal_Dark", 0.0)
    FP.hanging_lantern(mb, (MX0 - 1.35, ly, lz + 0.8), lights=False, chain=0.4)
    light("L_Houses_MillDoor", "POINT", (MX0 - 1.35, ly, lz - 0.8), 140, (1.0, 0.62, 0.28), 0.4)


def _open_crate(mb, loc, s, yaw, rng, m="Crystal_Blue"):
    x, y, z = loc
    F = FP.Frame(x, y, z, yaw)
    th = 0.25
    mb.box((s, s, th), F.p(0, 0, th / 2), F.r(), "Wood_Plank", 0.0)
    for sx in (-1, 1):
        mb.box((th, s, s), F.p(sx * (s - th) / 2, 0, s / 2), F.r(), "Wood_Plank", 0.0)
        mb.box((s - 2 * th, th, s), F.p(0, sx * (s - th) / 2, s / 2), F.r(), "Wood_Plank", 0.0)
    for dz in (0.3, s - 0.3):
        mb.box((s + 0.1, s + 0.1, 0.26), F.p(0, 0, dz), F.r(), "Wood_Dark", 0.0)
    mb.box((s - 0.4, s - 0.4, 0.3), F.p(0, 0, s * 0.72), F.r(), "Stone_Wall_Dark", 0.0)
    FP.crystal_cluster(mb, tuple(F.p(0, 0, s * 0.8)), s * 0.42, m, rng, 4)


def _pickaxes(mb, x, y_face, out):
    """duas picaretas encostadas na parede (y_face), inclinadas"""
    for i, dx in enumerate((0.0, 1.0)):
        a = V(x + dx, y_face + out * 1.1, G + 0.1)
        b = V(x + dx + 0.3, y_face + out * 0.35, G + 3.6)
        mb.beam(a, b, 0.22, 0.22, "Wood_Plank", 0.0)
        ax = (b - a).normalized()
        hd = V(1.0, 0.0, 0.0)
        hd = (hd - ax * hd.dot(ax)).normalized()
        for sg in (-1, 1):
            mb.beam(b, b + hd * sg * 1.05 - ax * 0.3, 0.24, 0.28, "Metal_Dark", 0.0)


def _chute(mb, a, b, w=1.4):
    """calha de tabuas (fundo + 2 bordas) de a ate b"""
    d = (b - a).normalized()
    side = d.cross(Vector((0, 0, 1))).normalized()
    upn = side.cross(d).normalized()
    if upn.z < 0:
        upn = -upn
    mb.beam(a, b, w, 0.25, "Wood_Plank", 0.0)
    for s in (-1, 1):
        mb.beam(a + side * s * (w / 2 + 0.1) + upn * 0.35, b + side * s * (w / 2 + 0.1) + upn * 0.35, 0.25, 0.8,
                "Wood_Dark", 0.0)


def gear_wheel(mb, cx, cy, cz, r, teeth, rim_w=0.62, depth=0.7, m="Wood_Dark", hub="Metal_Dark"):
    """engrenagem de madeira no plano YZ (eixo X): aro varrido, dentes radiais, raios cruzados e cubo de ferro"""
    n = 20 if r > 1.5 else 12
    pts = [V(cx, cy + math.cos(math.tau * k / n) * r, cz + math.sin(math.tau * k / n) * r) for k in range(n + 1)]
    mb.sweep(pts, [(-rim_w / 2, -depth / 2), (rim_w / 2, -depth / 2), (rim_w / 2, depth / 2), (-rim_w / 2, depth / 2)],
             m, True, up=(1, 0, 0), caps=False)
    for k in range(teeth):
        a = math.tau * k / teeth
        mb.box((depth * 0.9, 0.7, 0.5), (cx, cy + math.cos(a) * (r + rim_w / 2 + 0.3),
                                         cz + math.sin(a) * (r + rim_w / 2 + 0.3)), (a, 0, 0), m, 0.0)
    for a in (0.3, 0.3 + math.pi / 2):
        mb.beam(V(cx, cy - math.cos(a) * r, cz - math.sin(a) * r), V(cx, cy + math.cos(a) * r, cz + math.sin(a) * r),
                0.45, 0.5, m, 0.0)
    mb.cyl(0.62 if r > 1.5 else 0.5, depth + 0.5, (cx, cy, cz), (0, math.pi / 2, 0), hub, 10, bevel=0.0)


def mill_machine(rng):
    """eixo da roda -> roda de coroa (VFX, gira com a roda) -> pinhao na arvore de cames (VFX) -> cames levantam 3
    socos (VFX, sobe-e-desce) que batem o minerio no pilao; calha de saida para a caixa de cristais moidos"""
    # eixo da roda + roda de coroa
    ga = HMB("VFX_VIL_MillGear", "12_VFX_HELPERS", random.Random(4431), detail="near", vmax=1)
    # trecho INTERNO do eixo (o VFX_WATER_Wheel ja traz o eixo da face leste do moinho, x = MX1, ate a roda)
    x_end = MX1 + 0.05
    ga.cyl(0.62, x_end - (GEAR_X - 0.9), ((x_end + GEAR_X - 0.9) / 2, MY, AX_Z), (0, math.pi / 2, 0), "Wood_Dark", 10,
           bevel=0.0)
    ga.cyl(0.72, 0.4, (IX1 - 0.9, MY, AX_Z), (0, math.pi / 2, 0), "Metal_Dark", 10, bevel=0.0)
    gear_wheel(ga, GEAR_X, MY, AX_Z, GA_R, 20)
    oa = ga.finish()
    oa["pivot"] = (float(L.WHEEL[0]), MY, AX_Z)
    oa["axis"] = (1.0, 0.0, 0.0)
    oa["rpm"] = WHEEL_RPM
    oa["note"] = "mesmo eixo e mesmo rpm do VFX_WATER_Wheel (roda de baixo, -4 rpm em torno de +X)"
    # arvore de cames + pinhao
    gb = HMB("VFX_VIL_MillCamshaft", "12_VFX_HELPERS", random.Random(4432), detail="near", vmax=1)
    gb.cyl(0.46, IX1 - 0.3 - (IX0 + 0.6), ((IX1 - 0.3 + IX0 + 0.6) / 2, CAM_Y, AX_Z), (0, math.pi / 2, 0),
           "Wood_Dark", 10, bevel=0.0)
    gear_wheel(gb, GEAR_X, CAM_Y, AX_Z, GB_R, 10, rim_w=0.5, depth=0.7)
    for i, x in enumerate(STAMPS_X):
        a0 = i * math.tau / 3
        for k in range(2):
            a = a0 + k * math.pi
            tip = V(x, CAM_Y + math.cos(a) * 1.45, AX_Z + math.sin(a) * 1.45)
            gb.beam(V(x, CAM_Y, AX_Z), tip, 0.55, 0.7, "Metal_Dark", 0.0)
        gb.cyl(0.62, 0.9, (x, CAM_Y, AX_Z), (0, math.pi / 2, 0), "Metal_Dark", 8, bevel=0.0)
    ob = gb.finish()
    ob["pivot"] = (GEAR_X, CAM_Y, AX_Z)
    ob["axis"] = (1.0, 0.0, 0.0)
    ob["rpm"] = -WHEEL_RPM * GA_R / GB_R
    ob["note"] = "pinhao engrenado na roda de coroa (razao %.2f, sentido contrario ao da roda)" % (GA_R / GB_R)
    # socos do pilao (sobe e desce)
    st = HMB("VFX_VIL_MillStamps", "12_VFX_HELPERS", random.Random(4433), detail="near", vmax=1)
    for x in STAMPS_X:
        st.box((0.7, 0.7, AX_Z + 4.5 - BED_Z - 1.5), (x, STAMP_Y, (AX_Z + 4.5 + BED_Z + 1.5) / 2), (0, 0, 0),
               "Wood_Dark", 0.0)
        st.box((1.3, 1.3, 1.5), (x, STAMP_Y, BED_Z + 0.75), (0, 0, 0), "Metal_Dark", 0.0)
        st.box((1.0, 1.3, 0.55), (x, STAMP_Y - 0.55, AX_Z + 0.9), (0, 0, 0), "Metal_Dark", 0.0)
        st.box((0.95, 0.95, 0.4), (x, STAMP_Y, AX_Z + 4.5), (0, 0, 0), "Metal_Dark", 0.0)
    os_ = st.finish()
    os_["pivot"] = (STAMPS_X[1], STAMP_Y, BED_Z)
    os_["axis"] = (0.0, 0.0, 1.0)
    os_["bob"] = 1.2
    os_["rate"] = 2.0 * abs(WHEEL_RPM * GA_R / GB_R) / 60.0
    os_["note"] = "socos sobem 1,2 e caem (1 batida por came: 2 por volta da arvore de cames), defasados de 1/3"


def mill_interior(mb, rng):
    A = "HousesMill"
    # balcao de venda de frente para a porta (face oeste), NPC atras, jogador na frente
    cx0, cx1, cy0, cy1 = 100.4, 102.4, 5.2, 11.0
    mb.box2((cx0 + 0.15, cy0 + 0.1, FL), (cx1 - 0.1, cy1 - 0.1, FL + 3.1), "Wood_Plank", 0.0)
    mb.box2((cx0 - 0.3, cy0 - 0.2, FL + 3.1), (cx1 + 0.2, cy1 + 0.2, FL + 3.5), "Wood_Dark", 0.0)
    mb.box2((cx0 - 0.05, cy0, FL), (cx0 + 0.3, cy1, FL + 0.5), "Wood_Dark", 0.0)
    k = 0
    y = cy0 + 0.5
    while y < cy1 - 0.3:
        mb.box((0.3, 0.32, 2.5), (cx0 + 0.08, y, FL + 1.8), (0, 0, 0), "Wood_Dark", 0.0)
        y += 0.95
        k += 1
    # balanca + caixinha de cristais no balcao
    bz = FL + 3.5
    mb.box((0.9, 0.9, 0.2), (cx0 + 1.0, cy1 - 1.2, bz + 0.1), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((0.22, 0.22, 1.6), (cx0 + 1.0, cy1 - 1.2, bz + 1.0), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((0.22, 2.4, 0.22), (cx0 + 1.0, cy1 - 1.2, bz + 1.75), (0, 0, 0), "Metal_Dark", 0.0)
    for sy in (-1, 1):
        mb.cyl(0.55, 0.2, (cx0 + 1.0, cy1 - 1.2 + sy * 1.05, bz + 0.95), (0, 0, 0), "Metal_Iron", 8, r2=0.4, bevel=0.0)
        mb.box((0.22, 0.22, 0.75), (cx0 + 1.0, cy1 - 1.2 + sy * 1.05, bz + 1.35), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((1.3, 1.6, 0.6), (cx0 + 0.9, cy0 + 1.4, bz + 0.3), (0, 0, 0), "Wood_Dark", 0.0)
    FP.crystal_cluster(mb, (cx0 + 0.9, cy0 + 1.4, bz + 0.45), 0.35, "Crystal_Purple", rng, 3)
    col_box2(A, (cx0 - 0.3, cy0 - 0.2, FL), (cx1 + 0.2, cy1 + 0.2, FL + 3.5))
    # estante atras do NPC (parede leste) com cristais e potes
    sx0, sx1, sy0, sy1 = IX1 - 1.2, IX1, IY0 + 0.3, 9.9
    for y in (sy0 + 0.2, sy1 - 0.2):
        mb.box((1.2, 0.4, 7.2), ((sx0 + sx1) / 2, y, FL + 3.6), (0, 0, 0), "Wood_Dark", 0.0)
    for i, z in enumerate((FL + 0.4, FL + 2.4, FL + 4.4, FL + 6.4)):
        mb.box2((sx0, sy0, z - 0.15), (sx1, sy1, z + 0.15), "Wood_Plank", 0.0)
        if i == 0:
            continue
        for j in range(3):
            y = sy0 + 0.9 + j * (sy1 - sy0 - 1.8) / 2
            if (i + j) % 2 and i < 3:
                FP.crystal_cluster(mb, ((sx0 + sx1) / 2, y, z + 0.15), 0.3,
                                   "Crystal_Blue" if j != 1 else "Crystal_Purple", rng, 2)
            else:
                mb.cyl(0.4, 0.9, ((sx0 + sx1) / 2, y, z + 0.6), (0, 0, 0), "Wood_Plank", 8, bevel=0.0)
    col_box2(A, (sx0, sy0, FL), (sx1, sy1, FL + 7.2))
    # caixotes de cristais no canto SO (lado do jogador, longe da porta)
    FP.crate(mb, (IX0 + 1.1, IY0 + 1.1, FL), 2.0, 0.05, rng)
    FP.crate(mb, (IX0 + 1.2, IY0 + 1.0, FL + 2.0), 1.6, -0.2, rng)
    _open_crate(mb, (IX0 + 3.4, IY0 + 1.1, FL), 2.0, 0.1, rng, "Crystal_Purple")
    col_box2(A, (IX0, IY0, FL), (IX0 + 4.6, IY0 + 2.2, FL + 3.6))
    # pilao (almofariz) ao longo do muro norte: base de pedra, caixa de tabuas cintada, leito de minerio
    px0, px1 = STAMPS_X[0] - 1.6, STAMPS_X[-1] + 1.6
    py0, py1 = STAMP_Y - 1.3, IY1
    mb.box2((px0 - 0.2, py0 - 0.2, FL - 0.1), (px1 + 0.2, py1, FL + 1.1), "Stone_Wall_Dark", 0.0)
    mb.box2((px0, py0, FL + 1.1), (px1, py1, BED_Z), "Wood_Plank", 0.0)
    for (a, b) in (((px0, py0), (px1, py0 + 0.35)), ((px0, py1 - 0.35), (px1, py1)), ((px0, py0), (px0 + 0.35, py1)),
                   ((px1 - 0.35, py0), (px1, py1))):
        mb.box2((a[0], a[1], BED_Z - 0.1), (b[0], b[1], BED_Z + 0.55), "Wood_Dark", 0.0)
    for x in (px0 + 0.8, (px0 + px1) / 2, px1 - 0.8):
        mb.box2((x - 0.2, py0 - 0.08, FL + 1.1), (x + 0.2, py1, BED_Z + 0.3), "Metal_Dark", 0.0)
    for x in (97.9, 100.1):
        FP.crystal_cluster(mb, (x, STAMP_Y - 0.1, BED_Z - 0.05), 0.3, "Crystal_Blue", rng, 3)
    # estrutura-guia dos socos + mancais da arvore de cames
    gx0, gx1 = px0 - 0.5, px1 + 0.5
    for x in (gx0, gx1):
        mb.box((0.8, 0.8, CEIL - FL - 1.1), (x, STAMP_Y, (FL + 1.1 + CEIL) / 2), (0, 0, 0), "Wood_Dark", 0.0)
        mb.beam(V(x, STAMP_Y - 0.3, AX_Z), V(x, CAM_Y, AX_Z), 0.6, 0.8, "Wood_Dark", 0.0)
        mb.box((0.9, 1.1, 1.2), (x, CAM_Y, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    for z in (BED_Z + 3.4, AX_Z + 3.8):
        for dy in (-0.62, 0.62):
            mb.box2((gx0, STAMP_Y + dy - 0.2, z - 0.3), (gx1, STAMP_Y + dy + 0.2, z + 0.3), "Wood_Dark", 0.0)
    mb.box((1.0, 1.2, 1.2), (IX1 - 0.3, CAM_Y, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((1.0, 1.4, 1.4), (IX1 - 0.3, MY, AX_Z), (0, 0, 0), "Metal_Dark", 0.0)
    col_box2(A, (gx0 - 0.4, py0 - 0.3, FL), (gx1 + 0.4, IY1, CEIL))
    # bica de saida -> caixa de cristal moido (canto NE, sob as engrenagens)
    _chute(mb, V(px1 - 0.2, STAMP_Y - 1.0, BED_Z + 0.1), V(px1 + 1.9, STAMP_Y - 1.0, FL + 1.9), 0.9)
    _open_crate(mb, (IX1 - 1.3, STAMP_Y - 0.6, FL), 1.8, 0.0, rng)
    col_box2(A, (IX1 - 2.3, STAMP_Y - 0.8, FL), (IX1, IY1, FL + 2.0))
    # guarda-corpo de seguranca diante do pilao e das engrenagens (o jogador olha, nao entra)
    rail = [(IX0 + 0.3, STAMP_Y - 1.9), (cx1 + 0.1, STAMP_Y - 1.9), (cx1 + 0.1, cy1 + 0.3)]
    for (a, b) in zip(rail, rail[1:]):
        a3, b3 = V(a[0], a[1], FL), V(b[0], b[1], FL)
        ln = (b3 - a3).length
        n = max(1, int(ln / 2.0))
        for i in range(n + 1):
            p = a3 + (b3 - a3) * (i / n)
            mb.box((0.42, 0.42, 3.4), (p.x, p.y, FL + 1.7), (0, 0, 0), "Wood_Dark", 0.0)
        for zz in (FL + 3.25, FL + 1.8):
            mb.beam(a3 + V(0, 0, zz - FL), b3 + V(0, 0, zz - FL), 0.3, 0.34, "Wood_Plank", 0.0)
        c = (a3 + b3) / 2
        col_box(A, (ln + 0.4, 0.6, 4.0), (c.x, c.y, FL + 2.0), (0, 0, math.atan2(b3.y - a3.y, b3.x - a3.x)))
    # lanterna pendurada no forro + luz interna
    FP.hanging_lantern(mb, (98.0, 10.8, CEIL), lights=False, chain=2.6)
    light("L_Houses_MillInterior", "POINT", (98.0, 10.8, CEIL - 4.4), 520, (1.0, 0.66, 0.32), 0.8)
    FP.hanging_lantern(mb, ((cx0 + cx1) / 2 + 0.6, (cy0 + cy1) / 2, CEIL), lights=False, chain=4.2)
    light("L_Houses_MillCounter", "POINT", ((cx0 + cx1) / 2 + 0.6, (cy0 + cy1) / 2, CEIL - 6.0), 260,
          (1.0, 0.66, 0.32), 0.6)
    # marcadores de jogo: NPC atras do balcao olhando a porta, jogador na frente do balcao
    ny = (cy0 + cy1) / 2
    mk("NPC_Mill", (cx1 + 1.3, ny, FL), (0, 0, math.pi / 2), 2.0, "ARROWS",
       props={"note": "vendedor do posto do minerador (atras do balcao, olha para a porta oeste)"})
    mk("PLAYER_INTERACT_Mill", (cx0 - 1.9, ny, FL), (0, 0, -math.pi / 2), 2.0, "SPHERE",
       props={"note": "frente do balcao, dentro do moinho"})


def mill():
    rng = random.Random(4403)
    mb = HMB("VIL_Mill", "04_VILLAGE", rng, detail="near", vmax=2)
    mill_shell(mb, rng)
    mill_exterior(mb, rng)
    mill_interior(mb, rng)
    mb.finish()
    mill_machine(rng)


def build():
    houses_near()
    houses_upper()
    mill()
