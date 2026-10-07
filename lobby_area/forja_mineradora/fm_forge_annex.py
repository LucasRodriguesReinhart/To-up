# fm_forge_annex - anexos industriais da Forja do Ignis (passe fabrica): elevador de canecas em corrente e descarga
# com carrinho da mina tombado (patio oeste), guindaste de minerio no canto externo da ala esquerda (lanca para a
# praca), telheiro de carvao, casa de foles externa (patio leste), fole GIGANTE de couro na fachada leste da ala
# direita tocado por manivela no eixo da roda (tampo+couro em FORGE_Bellows_Top para o vfx animar), ventilador de
# chapa rebitada com para-fagulhas, respiros com rufo, engrenagens na parede e cocho de tempera + suporte de tenazes
# junto a bigorna. A tubulacao grossa da torre e o fumeiro ficam em fm_forge_tower. Nada aqui bloqueia rotas.
import math
from mathutils import Vector, Matrix, Euler
from fm_lib import D, col_box, col_box2, light, marker
from fm_parts import crystal_cluster, crate, barrel, frustum, hanging_lantern, mine_cart
from fm_forge_kit import (FB, big_pipe, pipe_clamp, gate_valve, handwheel, flange, rivet, iron_bracket, chain_links,
                          gear, tube_pt, xz_prism, forge_roof, boss, rufo, Z, wing_roof_z, WING_RISE_L, WING_RISE_R)
import fm_layout as L

C = "03_FORGE"
F0 = L.FLOOR
FL = L.FL
A = "ForgeX"
SFD = "Stone_Forge_Dark"
CX, CY = L.CHIMNEY


def _chain_run(mb, a, b, link=0.9, m="Metal_Dark"):
    """corrente reta de elos alternados (barata e legivel de longe)"""
    a, b = Vector(a), Vector(b)
    n = max(2, int((b - a).length / link))
    for i in range(n):
        p0 = a + (b - a) * (i / n)
        p1 = a + (b - a) * ((i + 1) / n)
        mb.beam(p0, p1, 0.16 if i % 2 else 0.42, 0.42 if i % 2 else 0.16, m, 0.0)


# ------------------------------------------------------------------ elevador de canecas (patio oeste)
def ore_lift(rng):
    mb = FB("FORGE_Ore_Lift", C, rng, detail="near")
    x0, x1, y0, y1 = -39.4, -35.8, 24.0, 27.6
    xc, yc = (x0 + x1) / 2, (y0 + y1) / 2
    ztop = 30.0
    for x in (x0 + 0.35, x1 - 0.35):
        for y in (y0 + 0.35, y1 - 0.35):
            mb.box((0.7, 0.7, ztop - F0 + 0.2), (x + rng.uniform(-0.05, 0.05), y, (F0 + ztop) / 2), (0, 0, 0),
                   "Wood_Dark", 0.08)
    levels = [F0 + 0.4, 9.5, 15.0, 20.5, 25.5, ztop - 0.4]
    for z in levels:
        mb.beam((x0, y0 + 0.35, z), (x1, y0 + 0.35, z), 0.45, 0.55, "Wood_Dark", 0.05)
        mb.beam((x0, y1 - 0.35, z), (x1, y1 - 0.35, z), 0.45, 0.55, "Wood_Dark", 0.05)
        mb.beam((x0 + 0.35, y0, z), (x0 + 0.35, y1, z), 0.45, 0.55, "Wood_Dark", 0.05)
        mb.beam((x1 - 0.35, y0, z), (x1 - 0.35, y1, z), 0.45, 0.55, "Wood_Dark", 0.05)
    for za, zb in zip(levels, levels[1:]):
        for s in (1, -1):
            mb.beam((x0 + 0.1, y0 + 0.35 + (0 if s > 0 else y1 - y0 - 0.7), za),
                    (x0 + 0.1, y1 - 0.35 - (0 if s > 0 else y1 - y0 - 0.7), zb), 0.3, 0.4, "Wood_Plank", 0.0)
    mb.box2((x0 + 0.2, y0 + 0.2, F0), (x1 - 0.2, y1 - 0.2, F0 + 2.4), "Wood_Plank", 0.1)
    for z in (F0 + 0.3, F0 + 2.1):
        mb.box2((x0 + 0.1, y0 + 0.1, z - 0.15), (x1 - 0.1, y1 - 0.1, z + 0.15), "Metal_Dark", 0.0)
    mb.box2((x0 - 0.3, y0 - 0.3, ztop - 0.35), (x1 + 0.1, y1 + 0.3, ztop), "Metal_Iron", 0.05)
    for (pa, pb) in (((x0 - 0.2, y0 - 0.2), (x0 - 0.2, y1 + 0.2)), ((x0 - 0.2, y1 + 0.2), (x1, y1 + 0.2))):
        mb.beam((pa[0], pa[1], ztop + 1.3), (pb[0], pb[1], ztop + 1.3), 0.22, 0.22, "Metal_Dark", 0.0)
        mb.box((0.26, 0.26, 1.35), (pb[0], pb[1], ztop + 0.65), (0, 0, 0), "Metal_Dark", 0.0)
    # corrente visivel subindo (sul) e descendo (norte) sobre a roda de cabeca exposta
    ys, yn = y0 + 0.75, y1 - 0.75
    zc_, rw = ztop + 2.0, (yn - ys) / 2
    for y in (ys, yn):
        _chain_run(mb, (xc, y, F0 + 1.8), (xc, y, zc_), link=0.95)
    gear(mb, (xc, yc, zc_), (1, 0, 0), rw + 0.3, 0.7, 12, "Metal_Dark", "Metal_Iron", spokes=4)
    for s in (-1, 1):
        mb.box((0.5, 0.9, 2.6), (xc + s * 1.1, yc, ztop + 1.0), (0, 0, 0), "Wood_Dark", 0.05)
    mb.rod((xc - 1.5, yc, zc_), (xc + 1.5, yc, zc_), 0.22, "Metal_Iron", 8)
    forge_roof(mb, xc - 0.3, yc, x1 - x0 + 0.4, y1 - y0 + 0.2, ztop + 3.7, 1.6, rng, thick=0.5, over=0.5, sag=0.0,
               row_h=1.0, seg=5.0, patches=0)
    for x in (x0, x1 - 0.1):
        for y in (y0 - 0.05, y1 + 0.05):
            mb.box((0.3, 0.3, 3.7), (x, y, ztop + 1.85), (0, 0, 0), "Wood_Dark", 0.0)
    # canecas de ~1.2 presas na corrente: ferro escuro com borda clara; cheias subindo, viradas descendo
    z = F0 + 4.6
    k = 0
    while z < ztop - 1.2:
        by = ys - 0.75
        frustum(mb, (xc, by, z - 0.45), 1.2, 0.9, 1.45, 1.1, 0.95, "Metal_Dark")
        mb.box((1.55, 1.2, 0.14), (xc, by, z + 0.52), (0, 0, 0), "Metal_Iron", 0.0)
        mb.box((0.5, 0.35, 0.3), (xc, ys - 0.2, z + 0.1), (0, 0, 0), "Metal_Dark", 0.0)
        if k % 2 == 0:
            crystal_cluster(mb, (xc, by, z + 0.35), 0.28, "Crystal_Blue" if k % 4 == 0 else "Crystal_Purple", rng, 3)
        bn = yn + 0.75
        frustum(mb, (xc, bn, z + 1.0), 1.2, 0.9, 1.45, 1.1, -0.95, "Metal_Dark")
        mb.box((1.55, 1.2, 0.14), (xc, bn, z - 0.02), (0, 0, 0), "Metal_Iron", 0.0)
        z += 2.9
        k += 1
    # bica de descarga: do topo ate a agua-furtada no telhado de meia-agua da ala esquerda
    wx0, wx1 = L.FORGE_WING_L[0], L.FORGE_WING_L[2]

    def zshed(x):
        return wing_roof_z(x, "L")
    ya = y1 + 0.55
    hx, hy = -29.9, ya
    zr = zshed(hx)
    pa = Vector((x1 + 0.1, ya, ztop - 0.8))
    pb = Vector((hx - 1.35, ya, zr + 0.75))
    mb.beam(pa, pb, 1.3, 0.3, "Wood_Plank", 0.03)
    for s in (-1, 1):
        mb.beam(pa + Vector((0, s * 0.62, 0.4)), pb + Vector((0, s * 0.62, 0.4)), 0.22, 0.8, "Wood_Dark", 0.0)
    for f in (0.3, 0.7):
        q = pa + (pb - pa) * f
        mb.box((0.3, 1.5, 0.3), q + Vector((0, 0, 0.85)), (0, 0, 0), "Metal_Dark", 0.0)
    crystal_cluster(mb, pa + (pb - pa) * 0.5 + Vector((0, 0, 0.2)), 0.22, "Crystal_Blue", rng, 3)
    mb.box2((hx - 1.3, hy - 1.3, zr - 1.2), (hx + 1.3, hy + 1.3, zr + 1.9), "Wood_Plank", 0.08)
    mb.box2((hx - 1.4, hy - 0.8, zr + 0.3), (hx - 1.1, hy + 0.8, zr + 1.5), "Metal_Dark", 0.0)
    forge_roof(mb, hx, hy, 2.8, 2.6, zr + 1.9, 1.2, rng, thick=0.4, over=0.35, sag=0.0, row_h=0.9, seg=4.0, patches=0)
    mb.finish()
    col_box2(A, (x0 - 0.3, y0 - 0.3, F0), (x1 + 0.2, y1 + 0.3, ztop + 3.0))

    # ---- descarga: carrinho da mina (mesmo modelo) tombado ~35 graus para oeste, minerio escorrendo
    dm = FB("FORGE_Ore_Unload", C, rng, detail="near")
    cx_, cy_ = -37.4, 21.6
    n0 = len(dm.bm.verts)
    mine_cart(dm, (cx_, cy_, F0), 0.0, load=None, rng=rng)
    dm.bm.verts.ensure_lookup_table()
    R = Matrix.Rotation(D(-35.0), 3, "Y")
    piv = Vector((cx_ - 1.1, cy_, F0 + 0.7))
    for v in dm.bm.verts[n0:]:
        v.co = piv + R @ (v.co - piv)
    for i in range(7):
        f = i / 6
        x = cx_ - 2.6 - f * 2.0 + rng.uniform(-0.4, 0.4)
        y = cy_ + rng.uniform(-1.0, 1.0)
        s = rng.uniform(0.55, 1.0) * (1.2 - f * 0.4)
        dm.rock((x, y, F0 + 0.25 + (1.0 - f) * 0.9), (s * 1.3, s, s * 0.7), "Cliff_Rock_Dark", 0,
                (0, 0, rng.uniform(0, 6)))
    for k in range(3):
        crystal_cluster(dm, (cx_ - 3.0 - k * 0.9, cy_ - 0.6 + k * 0.6, F0 + 0.3), 0.4,
                        ("Crystal_Blue", "Crystal_Purple", "Crystal_Blue")[k], rng, 4)
    crate(dm, (-38.0, 12.4, F0), 1.8, 0.3, rng)
    dm.beam((cx_ + 1.9, cy_ - 1.3, F0 + 0.2), (cx_ + 1.4, cy_ - 0.7, F0 + 3.6), 0.16, 0.16, "Wood_Plank", 0.0)
    dm.box((0.8, 0.12, 0.9), (cx_ + 1.95, cy_ - 1.4, F0 + 0.55), (0, D(-15), D(45)), "Metal_Iron", 0.0)
    dm.finish()
    col_box2(A, (cx_ - 4.0, cy_ - 1.6, F0), (cx_ + 2.0, cy_ + 1.6, F0 + 3.0))
    col_box2(A, (-39.0, 11.4, F0), (-37.0, 13.4, F0 + 1.9))


# ------------------------------------------------------------------ guindaste de minerio (canto externo da ala esq.)
def ore_crane(rng):
    mb = FB("FORGE_Ore_Crane", C, rng, detail="near")
    x0, y0 = L.FORGE_WING_L[0], L.FORGE_WING_L[1]
    mx, my = -34.9, -0.4
    ztop = 17.2
    mb.box((2.3, 2.3, 0.9), (mx, my, F0 + 0.45), (0, 0, 0), SFD, 0.12)
    mb.box((1.2, 1.2, ztop - F0 - 0.9), (mx, my, (F0 + 0.9 + ztop) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    for zz in (F0 + 2.6, 9.4, 13.4, ztop - 0.5):
        mb.box((1.38, 1.38, 0.34), (mx, my, zz), (0, 0, 0), "Metal_Dark", 0.0)
    mb.box((1.6, 1.6, 0.5), (mx, my, ztop + 0.2), (0, 0, 0), "Metal_Iron", 0.04)
    # escoras ate o canto da ala (por baixo do deque e por cima do guarda-corpo da varanda)
    for (za, zb) in ((10.6, 11.0), (16.9, 17.5)):
        mb.beam((mx + 0.5, my + 0.5, za), (x0 + 0.7, y0 + 0.3, zb), 0.5, 0.5, "Wood_Dark", 0.0)
    # lanca apontando para a praca (ponta em z<=16), cintas de ferro e tirante ate o topo do mastro
    pivot = Vector((mx + 0.5, my - 0.5, 8.4))
    tip = Vector((-30.2, -7.0, 15.8))
    mb.beam(pivot, tip, 0.8, 0.9, "Wood_Dark", 0.06)
    d = (tip - pivot).normalized()
    for f in (0.3, 0.65, 0.93):
        q = pivot + (tip - pivot) * f
        mb.rod(q - d * 0.2, q + d * 0.2, 0.62, "Metal_Dark", 8)
    mb.rod((mx, my, ztop + 0.3), tip + Vector((0, 0, 0.4)), 0.11, "Metal_Dark", 6)
    mb.cyl(0.62, 0.36, tip + Vector((0, 0, -0.5)), (D(90), 0, math.atan2(d.y, d.x)), "Metal_Iron", 10, bevel=0.0)
    for s in (-1, 1):
        side = Vector((-d.y, d.x, 0)).normalized() * 0.3 * s
        mb.box((1.0, 0.12, 1.4), tip + side + Vector((0, 0, -0.35)), (0, 0, math.atan2(d.y, d.x)), "Metal_Dark", 0.0)
    # cabo, cacamba pendurada com minerio, sarilho no pe do mastro
    bz = 7.4
    mb.rod(tip + Vector((0, 0, -1.1)), Vector((tip.x, tip.y, bz + 1.95)), 0.09, "Metal_Dark", 5)
    bc = Vector((tip.x, tip.y, bz))
    mb.cyl(0.95, 1.4, bc, (0, 0, 0), "Metal_Iron", 10, r2=1.2, bevel=0.05)
    mb.cyl(1.22, 0.2, bc + Z * 0.62, (0, 0, 0), "Metal_Dark", 10, bevel=0.0)
    hb = [bc + Vector((0, -1.15, 0.5)), bc + Vector((0, -0.9, 1.5)), bc + Vector((0, 0, 1.95)),
          bc + Vector((0, 0.9, 1.5)), bc + Vector((0, 1.15, 0.5))]
    tube_pt(mb, hb, 0.09, "Metal_Dark", 5)
    crystal_cluster(mb, bc + Z * 0.6, 0.35, "Crystal_Blue", rng, 4)
    wz = 6.6
    wxp = mx + 1.0
    for s in (-1, 1):
        mb.box((0.3, 1.2, 2.2), (wxp, my + s * 0.95, wz - 0.3), (0, 0, 0), "Metal_Dark", 0.0)
    mb.cyl(0.55, 1.6, (wxp + 0.1, my, wz), (D(90), 0, 0), "Wood_Plank", 10, bevel=0.0)
    for dy in (-0.5, 0.05, 0.55):
        mb.cyl(0.6, 0.14, (wxp + 0.1, my + dy, wz), (D(90), 0, 0), "Metal_Dark", 10, bevel=0.0)
    mb.rod((wxp + 0.1, my - 1.3, wz), (wxp + 0.1, my + 1.3, wz), 0.12, "Metal_Iron", 6)
    mb.beam((wxp + 0.1, my + 1.3, wz), (wxp + 0.1, my + 1.3, wz + 1.0), 0.14, 0.14, "Metal_Dark", 0.0)
    mb.rod((wxp + 0.1, my + 1.3, wz + 1.0), (wxp + 0.6, my + 1.3, wz + 1.0), 0.14, "Wood_Plank", 6)
    mb.rod((wxp + 0.1, my, wz + 0.55), (mx + 0.55, my - 0.3, ztop - 0.2), 0.08, "Metal_Dark", 5)
    mb.finish()
    col_box2(A, (mx - 1.15, my - 1.15, F0), (mx + 1.6, my + 1.15, ztop + 0.5))
    col_box2(A, (bc.x - 1.25, bc.y - 1.25, bz - 0.8), (bc.x + 1.25, bc.y + 1.25, bz + 0.9))


# ------------------------------------------------------------------ telheiro de carvao (fundos da ala esquerda)
def coal_shed(rng):
    mb = FB("FORGE_Coal_Shed", C, rng, detail="near")
    xa, xb = -29.6, -20.6
    yw, yp = L.FORGE_WING_L[3], 35.3
    for x in (xa + 0.4, (xa + xb) / 2 + rng.uniform(-0.3, 0.3), xb - 0.4):
        mb.box((0.75, 0.75, 6.0), (x, yp, F0 + 3.0), (0, 0, rng.uniform(-0.04, 0.04)), "Wood_Dark", 0.08)
        mb.beam((x, yp, F0 + 4.6), (x, yp - 1.6, F0 + 6.1), 0.4, 0.45, "Wood_Dark", 0.0)
    mb.beam((xa, yp, F0 + 6.0), (xb, yp, F0 + 6.05), 0.7, 0.8, "Wood_Dark", 0.06)
    z_w, z_p = F0 + 8.6, F0 + 6.4
    ang = math.atan2(z_w - z_p, yp - yw + 0.8)
    for i in range(5):
        x = xa + 0.3 + i * (xb - xa - 0.6) / 4
        mb.beam((x, yw, z_w - 0.3), (x, yp + 0.8, z_p - 0.1), 0.35, 0.45, "Wood_Dark", 0.0)
    nsh = 6
    for i in range(nsh):
        x0_ = xa - 0.4 + i * (xb - xa + 0.8) / nsh
        x1_ = x0_ + (xb - xa + 0.8) / nsh + 0.12
        mid = Vector(((x0_ + x1_) / 2, (yw + yp + 0.9) / 2, (z_w + z_p) / 2 + 0.25))
        m = "Metal_Rust" if i in (1, 4) else "Roof_Forge"
        mb.box((x1_ - x0_, math.hypot(yp + 0.9 - yw, z_w - z_p) + 0.3, 0.22), mid,
               (-ang + rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), 0), m, 0.03)
        for k in range(3):
            xx = x0_ + (k + 0.5) * (x1_ - x0_) / 3
            mb.box((0.14, math.hypot(yp + 0.9 - yw, z_w - z_p) + 0.3, 0.12), (xx, mid.y, mid.z + 0.16), (-ang, 0, 0), m,
                   0.0)
    bx = [xa + 0.2, xa + 3.1, xb - 3.1, xb - 0.2]
    for x in bx:
        mb.box((0.3, 3.4, 2.0), (x, yw + 1.7, F0 + 1.0), (0, 0, 0), "Wood_Plank", 0.05)
    mb.box2((xa + 0.2, yw + 3.3, F0), (xb - 0.2, yw + 3.6, F0 + 1.3), "Wood_Plank", 0.05)
    for i in range(3):
        c0 = (bx[i] + bx[i + 1]) / 2
        for k in range(9):
            x = c0 + rng.uniform(-1.1, 1.1)
            y = yw + rng.uniform(0.5, 3.0)
            h = 1.2 * (1 - abs(x - c0) / 1.8) * (1 - (y - yw) / 5.0)
            s = rng.uniform(0.9, 1.4)
            mb.rock((x, y, F0 + 0.4 + h * rng.uniform(0.6, 1.0)), (s, s, s * 0.7), "Stone_Coal", 0,
                    (0, 0, rng.uniform(0, 6)))
    for k, (x, y) in enumerate(((xb + 0.9, yw + 1.0), (xb + 0.8, yw + 2.4), (xb + 1.0, yw + 1.7))):
        zz = F0 + 0.75 + (1.2 if k == 2 else 0.0)
        mb.ico(0.75, (x, y, zz), "Rope", 1, (0.85, 0.72, 1.0), jitter=0.12)
        mb.cyl(0.28, 0.45, (x, y, zz + 0.85), (0, 0, 0), "Rope", 6, r2=0.4, bevel=0.0)
    mb.beam((xa + 1.6, yp - 0.6, F0 + 0.2), (xa + 1.3, yp - 1.1, F0 + 3.8), 0.16, 0.16, "Wood_Plank", 0.0)
    mb.box((0.8, 0.14, 0.9), (xa + 1.62, yp - 0.55, F0 + 0.5), (D(10), 0, 0), "Metal_Iron", 0.0)
    wx, wy = -15.8, 34.0
    mb.cyl(1.1, 1.0, (wx, wy, F0 + 1.4), (0, 0, math.pi / 4), "Metal_Iron", 4, r2=1.5, bevel=0.04)
    for k in range(5):
        mb.rock((wx + rng.uniform(-0.6, 0.6), wy + rng.uniform(-0.6, 0.6), F0 + 1.95), (0.8, 0.8, 0.5), "Stone_Coal", 0)
    mb.cyl(0.45, 0.25, (wx + 1.6, wy, F0 + 0.5), (D(90), 0, 0), "Metal_Dark", 10, bevel=0.0)
    for s in (-1, 1):
        mb.beam((wx + 1.6, wy + s * 0.45, F0 + 0.5), (wx - 2.2, wy + s * 0.7, F0 + 1.9), 0.18, 0.18, "Wood_Plank", 0.0)
        mb.beam((wx - 0.6, wy + s * 0.55, F0 + 0.9), (wx - 0.7, wy + s * 0.55, F0), 0.16, 0.16, "Wood_Dark", 0.0)
    mb.finish()
    col_box2(A, (xa, yw, F0), (xb, yw + 3.6, F0 + 2.1))
    for x in (xa + 0.4, xb - 0.4):
        col_box2(A, (x - 0.45, yp - 0.45, F0), (x + 0.45, yp + 0.45, F0 + 6.4))
    col_box2(A, (xb + 0.2, yw + 0.2, F0), (xb + 1.8, yw + 3.0, F0 + 2.0))
    col_box2(A, (wx - 2.3, wy - 0.9, F0), (wx + 2.1, wy + 0.9, F0 + 2.2))


# ------------------------------------------------------------------ casa de foles externa (fundos da ala direita)
def bellows_house(rng):
    mb = FB("FORGE_Bellows_House", C, rng, detail="near")
    xa, xb = 20.8, 31.4
    yw, yp = L.FORGE_WING_R[3], 35.3
    yc = 33.9
    mb.box2((21.6, yw + 0.4, F0), (30.4, yp - 0.1, F0 + 1.2), SFD, 0.15)
    bl, br = 22.4, 29.4
    zb = F0 + 1.6
    h0, h1 = 0.5, 2.7
    mb.box2((bl, yc - 1.45, F0 + 1.2), (br, yc + 1.45, zb), "Wood_Plank", 0.08)
    xz_prism(mb, [(bl, zb), (br, zb), (br, zb + h1), (bl, zb + h0)], yc - 1.25, yc + 1.25, "Leather_Bellows", 0.0,
             (0.0, 0.0))
    for k in range(1, 4):
        f = k / 4
        for s in (-1, 1):
            mb.beam((bl + 0.3, yc + s * 1.35, zb + h0 * f), (br + 0.05, yc + s * 1.35, zb + h1 * f), 0.4, 0.3,
                    "Leather_Bellows", 0.0)
        mb.beam((br + 0.1, yc - 1.35, zb + h1 * f), (br + 0.1, yc + 1.35, zb + h1 * f), 0.4, 0.3, "Leather_Bellows", 0.0)
    lift = math.atan2(h1 - h0, br - bl)
    mb.beam((bl - 0.2, yc, zb + h0 + 0.2), (br + 0.2, yc, zb + h1 + 0.2), 3.1, 0.4, "Wood_Plank", 0.08)
    for x in (bl + 1.5, bl + 3.8, br - 0.8):
        zz = zb + h0 + (x - bl) * math.tan(lift) + 0.45
        mb.box((0.35, 3.2, 0.2), (x, yc, zz), (0, -lift, 0), "Metal_Dark", 0.0)
    mb.cyl(0.75, 1.0, (bl - 0.4, yc, zb + 0.3), (0, D(90), 0), "Metal_Brass", 10, r2=0.45, bevel=0.0)
    px = 30.3
    for s in (-1, 1):
        mb.beam((px + 0.8, yc + s * 1.3, F0), (px, yc + s * 0.45, 10.8), 0.5, 0.5, "Wood_Dark", 0.05)
    pv = Vector((px, yc, 10.6))
    ra = Vector((26.4, yc, 9.7))
    rb = Vector((31.2, yc, 10.9))
    mb.beam(ra, rb, 0.6, 0.7, "Wood_Dark", 0.05)
    mb.rod(pv - Vector((0, 0.8, 0)), pv + Vector((0, 0.8, 0)), 0.2, "Metal_Iron", 8)
    tz = zb + h0 + (26.4 - bl) * math.tan(lift) + 0.4
    mb.beam(ra, (26.4, yc, tz), 0.22, 0.22, "Metal_Dark", 0.0)
    shaft = Vector((29.0, yw, 11.4))
    mb.rod(shaft, shaft + Vector((0, 1.5, 0)), 0.3, "Metal_Iron", 8)
    gear(mb, shaft + Vector((0, 1.1, 0)), (0, 1, 0), 1.15, 0.4, 10, "Metal_Dark", "Metal_Iron", spokes=4)
    mb.beam(shaft + Vector((0.8, 1.4, 0.4)), rb + Vector((0, -0.4, 0)), 0.2, 0.2, "Metal_Dark", 0.0)
    mb.box((1.6, 0.4, 1.6), shaft + Vector((0, 0.15, 0)), (0, 0, 0), "Metal_Iron", 0.05)
    z_w, z_p = 13.8, 11.4
    for x in (xa + 0.4, (xa + xb) / 2, xb - 0.4):
        mb.box((0.75, 0.75, z_p - F0), (x, yp, (F0 + z_p) / 2), (0, 0, rng.uniform(-0.04, 0.04)), "Wood_Dark", 0.08)
    mb.beam((xa, yp, z_p - 0.2), (xb, yp, z_p - 0.15), 0.7, 0.8, "Wood_Dark", 0.06)
    ang = math.atan2(z_w - z_p, yp - yw + 0.8)
    nsh = 6
    for i in range(nsh):
        x0_ = xa - 0.4 + i * (xb - xa + 0.8) / nsh
        x1_ = x0_ + (xb - xa + 0.8) / nsh + 0.12
        mid = Vector(((x0_ + x1_) / 2, (yw + yp + 0.9) / 2, (z_w + z_p) / 2 + 0.25))
        mb.box((x1_ - x0_, math.hypot(yp + 0.9 - yw, z_w - z_p) + 0.3, 0.3), mid,
               (-ang + rng.uniform(-0.02, 0.02), rng.uniform(-0.02, 0.02), 0), "Roof_Forge", 0.06, tint=rng.uniform(-1, 1))
    for i in range(4):
        x = xa + 0.4 + i * (xb - xa - 0.8) / 3
        mb.beam((x, yw, z_w - 0.35), (x, yp + 0.8, z_p - 0.1), 0.35, 0.45, "Wood_Dark", 0.0)
    hanging_lantern(mb, (25.0, yp - 0.6, z_p - 0.4), name="L_BellowsHouse", chain=0.8)
    for k, (x, y) in enumerate(((xb + 0.2, yw + 1.3), (xb + 0.1, yw + 2.7))):
        mb.ico(0.72, (x - 0.9, y, F0 + 0.75), "Rope", 1, (0.85, 0.72, 1.0), jitter=0.12)
        mb.cyl(0.26, 0.45, (x - 0.9, y, F0 + 1.6), (0, 0, 0), "Rope", 6, r2=0.38, bevel=0.0)
    mb.finish()
    col_box2(A, (21.2, yw, F0), (30.8, yp - 0.2, F0 + 4.6))
    for x in (xa + 0.4, xb - 0.4):
        col_box2(A, (x - 0.45, yp - 0.45, F0), (x + 0.45, yp + 0.45, z_p))
    col_box2(A, (px - 0.6, yc - 1.8, F0), (px + 1.3, yc + 1.8, 12.0))

    # tubo de ar do fole ate a casa da fornalha (sobe acima da cabeca e entra na parede leste com colar)
    import fm_forge_tower as T
    pm = FB("FORGE_Pipes_Air", C, rng, detail="near")
    p0 = Vector((bl - 0.9, yc, zb + 0.3))
    p1 = Vector((18.2, yc, zb + 0.3))
    p2 = Vector((18.2, yc, 12.6))
    p3 = Vector((T.HX + 0.25, 33.2, 12.6))
    big_pipe(pm, [p0, p1, p2, p3], 1.2, "Metal_Dark", "Metal_Copper", bend=2.2, step=6.0, n=12, bolts=5)
    gate_valve(pm, Vector((18.2, yc, 8.6)), Z, 1.1, up=(-1, 0, 0))
    boss(pm, (T.HX + 0.2, 33.2, 12.6), (1, 0, 0), 3.0)
    q = p2 + (p3 - p2) * 0.45
    pipe_clamp(pm, q, (p3 - p2).normalized(), 1.2, Vector((q.x, q.y, 8.0)))
    pm.box((1.3, 1.3, 3.4), (q.x, q.y, F0 + 2.0), (0, 0, 0), SFD, 0.1)
    pm.finish()
    col_box2(A, (16.8, yc - 1.5, F0), (21.6, yc + 1.5, F0 + 3.7))
    col_box2(A, (q.x - 0.8, q.y - 0.8, F0), (q.x + 0.8, q.y + 0.8, F0 + 3.8))


# ------------------------------------------------------------------ ventilador de chapa rebitada (ala direita)
def vent_tower(rng):
    mb = FB("FORGE_Vent_Tower", C, rng, detail="near")
    x0, y0, x1, y1 = L.FORGE_WING_R
    cx = (x0 + x1) / 2
    vx, vy = 30.9, 11.2
    zr = wing_roof_z(vx, "R")
    hw = 1.45
    zb, zl, zt = zr - 0.6, zr + 4.0, zr + 6.4
    # corpo de chapas rebitadas com cantoneiras e duas cintas
    mb.box2((vx - hw, vy - hw, zb), (vx + hw, vy + hw, zl), "Metal_Burnt", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.36, 0.36, zt - zb + 0.2), (vx + sx * hw, vy + sy * hw, (zb + zt) / 2), (0, 0, 0), "Metal_Dark",
                   0.0)
    for z in (zr + 1.3, zl):
        mb.box2((vx - hw - 0.08, vy - hw - 0.08, z - 0.2), (vx + hw + 0.08, vy + hw + 0.08, z + 0.2), "Metal_Dark", 0.0)
    for (nx, ny) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for k in (-1, 1):
            p = Vector((vx + nx * (hw + 0.1) + ny * k * 0.8, vy + ny * (hw + 0.1) + nx * k * 0.8, zr + 2.7))
            rivet(mb, p, (nx, ny, 0), 0.22, "Metal_Iron", 0.12)
    # venezianas de ferro com o brilho da forja atras
    mb.box2((vx - hw + 0.3, vy - hw + 0.3, zl), (vx + hw - 0.3, vy + hw - 0.3, zt), "Forge_Glow_Soft", 0.0)
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = D(ang)
        d = Vector((math.cos(a), math.sin(a), 0))
        for k in range(3):
            z = zl + 0.45 + k * 0.75
            c = Vector((vx, vy, z)) + d * (hw - 0.1)
            mb.box((0.7, 2 * hw - 0.3, 0.12), c, _louver_rot(a), "Metal_Dark", 0.0)
    # chapeu conico com gaiola para-fagulhas e pinaculo
    mb.box2((vx - hw - 0.1, vy - hw - 0.1, zt), (vx + hw + 0.1, vy + hw + 0.1, zt + 0.25), "Metal_Dark", 0.0)
    for k in range(6):
        a = math.tau * k / 6
        mb.beam((vx + math.cos(a) * 1.0, vy + math.sin(a) * 1.0, zt + 0.25),
                (vx + math.cos(a) * 1.0, vy + math.sin(a) * 1.0, zt + 1.55), 0.12, 0.12, "Metal_Dark", 0.0)
    mb.cyl(1.05, 0.14, (vx, vy, zt + 0.9), (0, 0, 0), "Metal_Dark", 10, bevel=0.0, caps=False)
    mb.cyl(2.15, 0.9, (vx, vy, zt + 2.0), (0, 0, 0), "Metal_Burnt", 12, r2=0.35, bevel=0.0)
    mb.cyl(0.14, 1.2, (vx, vy, zt + 2.9), (0, 0, 0), "Metal_Dark", 6, bevel=0.0)
    mb.cyl(0.3, 0.3, (vx, vy, zt + 2.6), (0, 0, 0), "Metal_Brass", 8, bevel=0.0)
    rufo(mb, (vx, vy, zr), hw * 0.9, (0.0, math.atan2(WING_RISE_R, 7.0)))
    mb.finish()

    # respiros (chamines de chapa) nos telhados das alas, com rufo baixo
    # (ala esq.: respiro baixo no lado alto da meia-agua -> topo ~z30.5, como antes; fora das visadas)
    for (name, x, y, h, glow) in (("FORGE_Roof_Vents_L", -31.0, 10.8, 3.6, True),
                                  ("FORGE_Roof_Vents_R", 22.9, 27.6, 5.0, False)):
        rm = FB(name, C, rng, detail="near")
        if x < 0:
            wx0, wx1 = L.FORGE_WING_L[0], L.FORGE_WING_L[2]
            z0 = wing_roof_z(x, "L")
            slope = (0.0, math.atan(WING_RISE_L / (wx1 - wx0)))
        else:
            z0 = wing_roof_z(x, "R")
            slope = (0.0, -math.atan2(WING_RISE_R, 7.0))
        rm.rod((x, y, z0 - 1.0), (x, y, z0 + h), 0.75, "Metal_Dark", 10)
        for zz in (z0 + 1.6, z0 + h - 1.4):
            rm.rod((x, y, zz - 0.2), (x, y, zz + 0.2), 0.92, "Metal_Iron", 10)
        if glow:
            rm.rod((x, y, z0 + h - 0.9), (x, y, z0 + h - 0.3), 0.8, "Forge_Glow_Soft", 10)
        rm.cyl(1.5, 0.8, (x, y, z0 + h + 0.7), (0, 0, 0), "Metal_Dark", 10, r2=0.3, bevel=0.0)
        for k in range(3):
            a = math.tau * k / 3
            rm.beam((x + math.cos(a) * 0.7, y + math.sin(a) * 0.7, z0 + h - 0.1),
                    (x + math.cos(a) * 1.1, y + math.sin(a) * 1.1, z0 + h + 0.4), 0.14, 0.14, "Metal_Dark", 0.0)
        rufo(rm, (x, y, z0 - 0.05), 0.75, slope)
        rm.finish()


def _louver_rot(a):
    return (Matrix.Rotation(a, 3, "Z") @ Matrix.Rotation(D(38), 3, "Y")).to_euler()


# ------------------------------------------------------------------ parede leste da ala direita: engrenagens + fole gigante
def wall_gears(rng):
    mb = FB("FORGE_Wall_Gears", C, rng, detail="near")
    ex = L.FORGE_WING_R[2]
    ay = L.WHEEL_C[1]
    az = 15.5
    gx = ex + 1.9
    gear(mb, (gx, ay, az), (1, 0, 0), 3.0, 0.8, 18, "Metal_Dark", "Metal_Iron", spokes=6)
    py = ay + 4.15
    gear(mb, (gx, py, az), (1, 0, 0), 1.45, 0.8, 9, "Metal_Iron", "Metal_Dark", spokes=4, rot0=D(10))
    mb.rod((ex - 0.3, py, az), (gx + 0.7, py, az), 0.3, "Metal_Iron", 8)
    h = 2.2
    mb.box((0.4, h, h), (ex + 0.25, py, az), (0, 0, 0), "Metal_Iron", 0.06)
    for k in range(4):
        a = math.tau * k / 4 + math.pi / 4
        rivet(mb, (ex + 0.45, py + math.cos(a) * h * 0.36, az + math.sin(a) * h * 0.36), (1, 0, 0), 0.22, "Metal_Dark")
    arc_pts = [Vector((gx, ay + math.cos(D(a)) * 3.5, az + math.sin(D(a)) * 3.5)) for a in range(25, 156, 26)]
    for p0, p1 in zip(arc_pts, arc_pts[1:]):
        mb.beam(p0, p1, 1.0, 0.18, "Metal_Rust", 0.0)
    # manivela no eixo da roda (entre a parede e a engrenagem) -> biela -> tampo do fole
    mb.cyl(1.05, 0.4, (ex + 0.85, ay, az), (0, D(90), 0), "Metal_Iron", 12, bevel=0.0)
    pin = Vector((ex + 1.1, ay, az - 0.8))
    mb.rod((ex + 0.6, ay, az - 0.8), (ex + 1.25, ay, az - 0.8), 0.18, "Metal_Dark", 6)

    # fole GIGANTE de couro a mostra na fachada leste (<= z16): cunha ao longo da parede, articulada no bocal (sul)
    tm = FB("FORGE_Bellows_Top", C, rng, detail="near")
    xc, w = ex + 1.35, 2.4
    y_h, y_f = 10.4, 20.2
    zb = F0 + 1.9
    h0, h1 = 0.5, 4.2
    mb.box2((ex + 0.05, y_h - 1.3, F0), (ex + 2.7, y_f + 0.3, zb - 0.5), SFD, 0.12)
    mb.box2((xc - w / 2 - 0.1, y_h - 0.2, zb - 0.5), (xc + w / 2 + 0.1, y_f + 0.2, zb), "Wood_Plank", 0.06)
    xz_prism(tm, [(y_h, zb), (y_f, zb), (y_f, zb + h1), (y_h, zb + h0)], -(w / 2 - 0.2), w / 2 - 0.2,
             "Leather_Bellows", D(90), (xc, 0.0))
    for k in range(1, 5):
        f = k / 5
        for s in (-1, 1):
            tm.beam((xc + s * (w / 2 - 0.08), y_h + 0.3, zb + h0 * f), (xc + s * (w / 2 - 0.08), y_f + 0.05, zb + h1 * f),
                    0.28, 0.34, "Leather_Bellows", 0.0)
        tm.beam((xc - w / 2 + 0.1, y_f + 0.08, zb + h1 * f), (xc + w / 2 - 0.1, y_f + 0.08, zb + h1 * f), 0.28, 0.34,
                "Leather_Bellows", 0.0)
    tm.beam((xc, y_h - 0.1, zb + h0 + 0.2), (xc, y_f + 0.25, zb + h1 + 0.2), w + 0.15, 0.4, "Wood_Plank", 0.06)
    lift = math.atan2(h1 - h0, y_f - y_h)
    for f in (0.25, 0.6, 0.92):
        y = y_h + (y_f - y_h) * f
        zz = zb + h0 + (h1 - h0) * f + 0.43
        tm.box((w + 0.3, 0.35, 0.18), (xc, y, zz), (lift, 0, 0), "Metal_Dark", 0.0)
    tm.finish()
    hinge = Vector((xc, y_h, zb + h0 + 0.2))
    marker("VFX_Bellows_Hinge", tuple(hinge), (0, 0, 0), 1.5,
           props={"pivot": [round(hinge.x, 3), round(hinge.y, 3), round(hinge.z, 3)], "axis": [1.0, 0.0, 0.0],
                  "object": "FORGE_Bellows_Top", "angle_deg": 12.0,
                  "note": "tampo+couro giram em torno do eixo X (Blender) no bocal; 1 ciclo por volta da manivela"})
    # bocal de ferro -> cotovelo -> parede (colar rebitado); biela da manivela ate a ponta do tampo
    mb.cyl(0.62, 1.0, (xc, y_h - 0.6, zb + 0.35), (D(90), 0, 0), "Metal_Iron", 10, r2=0.38, bevel=0.0)
    tube_pt(mb, [Vector((xc, y_h - 1.0, zb + 0.35)), Vector((xc, y_h - 1.7, zb + 0.35)),
                 Vector((ex + 0.3, y_h - 1.7, zb + 0.35))], 0.42, "Metal_Dark", 10)
    boss(mb, (ex + 0.25, y_h - 1.7, zb + 0.35), (1, 0, 0), 1.5)
    mb.beam(pin, (xc, y_f - 0.2, zb + h1 + 0.45), 0.3, 0.3, "Metal_Dark", 0.0)
    mb.finish()
    col_box2(A, (ex, y_h - 2.2, F0), (ex + 2.8, y_f + 0.6, zb + h1 + 0.9))


# ------------------------------------------------------------------ fachada: carvao, barras, cocho de tempera, tenazes
def facade_props(rng):
    mb = FB("FORGE_Facade_Props", C, rng, detail="near")
    y0 = L.FORGE_HALL[1]
    x0, x1, ya, yb = -11.4, -8.9, y0 - 2.7, y0 - 0.25
    mb.box2((x0, ya, FL), (x1, yb, FL + 0.3), "Wood_Dark", 0.03)
    for (p, q) in (((x0, ya), (x1, ya + 0.3)), ((x0, yb - 0.3), (x1, yb)), ((x0, ya), (x0 + 0.3, yb)),
                   ((x1 - 0.3, ya), (x1, yb))):
        mb.box2((p[0], p[1], FL), (q[0], q[1], FL + 1.9), "Wood_Plank", 0.05)
    for (x, y) in ((x0, ya), (x1, ya), (x0, yb), (x1, yb)):
        mb.box((0.4, 0.4, 2.0), (x, y, FL + 1.0), (0, 0, 0), "Metal_Dark", 0.0)
    for k in range(8):
        s = rng.uniform(0.6, 0.95)
        mb.rock((rng.uniform(x0 + 0.6, x1 - 0.6), rng.uniform(ya + 0.6, yb - 0.6), FL + 1.7 + rng.uniform(0, 0.35)),
                (s, s, s * 0.7), "Stone_Coal", 0, (0, 0, rng.uniform(0, 6)))
    mb.beam((x1 - 0.3, ya + 0.4, FL + 1.6), (x1 + 0.3, ya - 0.6, FL + 3.9), 0.16, 0.16, "Wood_Plank", 0.0)
    mb.box((0.14, 0.8, 0.9), (x1 - 0.35, ya + 0.55, FL + 1.35), (D(-20), 0, 0), "Metal_Iron", 0.0)
    xr0, xr1 = 8.9, 11.4
    for x in (xr0 + 0.2, xr1 - 0.2):
        mb.box((0.35, 2.2, 0.35), (x, y0 - 1.5, FL + 0.9), (0, 0, 0), "Wood_Dark", 0.0)
        mb.box((0.35, 0.35, 1.9), (x, y0 - 2.5, FL + 0.95), (0, 0, 0), "Wood_Dark", 0.0)
        mb.box((0.35, 0.35, 3.2), (x, y0 - 0.5, FL + 1.6), (0, 0, 0), "Wood_Dark", 0.0)
    for k in range(6):
        x = xr0 + 0.25 + k * 0.4
        m = "Metal_Heated" if k == 2 else ("Metal_Iron" if k % 2 else "Metal_Dark")
        mb.beam((x, y0 - 2.4, FL + 1.9), (x + 0.05, y0 - 0.45, FL + 3.4), 0.25, 0.25, m, 0.0)
    barrel(mb, (10.1, y0 - 4.3, FL), 0.75, 1.5)
    mb.cyl(0.78, 0.1, (10.1, y0 - 4.3, FL + 1.35), (0, 0, 0), "Water", 10, bevel=0.0)
    # cocho de tempera (pedra + cintas de ferro) ao lado da bigorna, com tenaz atravessada
    ax, ay = L.ANVIL
    tx0, tx1, ty0, ty1 = ax - 6.6, ax - 3.4, ay - 0.8, ay + 0.8
    mb.box2((tx0, ty0, FL), (tx1, ty1, FL + 1.3), "Stone_Dark", 0.12)
    mb.box2((tx0 + 0.3, ty0 + 0.3, FL + 1.02), (tx1 - 0.3, ty1 - 0.3, FL + 1.18), "Water", 0.0)
    for x in (tx0 + 0.55, tx1 - 0.55):
        mb.box((0.3, ty1 - ty0 + 0.14, 1.34), (x, (ty0 + ty1) / 2, FL + 0.66), (0, 0, 0), "Metal_Dark", 0.0)
    for s in (-1, 1):
        mb.beam((tx0 + 0.6, (ty0 + ty1) / 2 + s * 0.12, FL + 1.35), (tx1 - 0.2, (ty0 + ty1) / 2 + s * 0.3, FL + 1.4),
                0.14, 0.14, "Metal_Dark", 0.0)
    marker("VFX_Quench_Steam", ((tx0 + tx1) / 2, (ty0 + ty1) / 2, FL + 1.2), (0, 0, 0), 1.5,
           props={"particle": "steam", "note": "vapor do cocho de tempera (lamina mergulhada)"})
    # suporte de tenazes (cavalete) do outro lado da bigorna
    rx0, rx1, ry = ax + 5.2, ax + 7.0, ay + 0.4
    for x in (rx0, rx1):
        mb.box((0.35, 0.35, 3.2), (x, ry, FL + 1.6), (0, 0, 0), "Wood_Dark", 0.0)
        mb.box((0.35, 1.2, 0.3), (x, ry, FL + 0.15), (0, 0, 0), "Wood_Dark", 0.0)
    mb.beam((rx0 - 0.3, ry, FL + 3.0), (rx1 + 0.3, ry, FL + 3.0), 0.3, 0.3, "Wood_Dark", 0.0)
    for k in range(3):
        x = rx0 + 0.45 + k * 0.45
        for s in (-1, 1):
            mb.beam((x, ry, FL + 3.1), (x + s * 0.18, ry - 0.1, FL + 1.1), 0.12, 0.12, "Metal_Dark", 0.0)
    mb.beam((rx1 + 0.6, ry - 0.3, FL), (rx1 + 0.3, ry - 0.1, FL + 2.6), 0.2, 0.2, "Wood_Plank", 0.0)
    mb.box((0.7, 0.45, 0.45), (rx1 + 0.3, ry - 0.1, FL + 2.75), (0, 0, 0.3), "Metal_Dark", 0.0)
    mb.finish()
    col_box2(A, (x0 - 0.2, ya - 0.2, FL), (x1 + 0.2, yb, FL + 2.0))
    col_box2(A, (xr0, y0 - 2.8, FL), (xr1, y0 - 0.2, FL + 3.4))
    col_box2(A, (9.2, y0 - 5.2, FL), (11.0, y0 - 3.4, FL + 1.6))
    col_box2(A, (tx0 - 0.1, ty0 - 0.1, FL), (tx1 + 0.1, ty1 + 0.1, FL + 1.4))
    col_box2(A, (rx0 - 0.3, ry - 0.7, FL), (rx1 + 0.9, ry + 0.7, FL + 3.3))


def build(rng):
    ore_lift(rng)
    ore_crane(rng)
    coal_shed(rng)
    bellows_house(rng)
    vent_tower(rng)
    wall_gears(rng)
    facade_props(rng)
