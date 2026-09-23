# fm_water - geografia da agua: NASCENTES (cachoeiras NO, NE e central) -> CANAL do ledge -> VERTEDOURO ->
#            TANQUE -> RIO (roda d'agua aciona o eixo da forja) -> queda no penhasco sul
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, resample, bezier
from fm_parts import (Frame, stone_parapet, fence, masonry_wall, timber_wall, window_glow, cliff_band, rock_scatter,
                      hanging_lantern, lantern, crate, barrel, stairs, P3, arch)
import fm_layout as L

C = "05_WATER_SYSTEM"
F0 = L.FLOOR
WZ_RIVER = 2.8
WZ_CANAL = 13.2
WZ_TERR = L.TERR - 0.7


def waterfall(mb, top, bottom_z, width, rng, out=(0, -1), lip=1.5, foam=True, tiers=1, name=None):
    """cachoeira estilizada: fita curva (sai do bocal e cai) + faixas mais claras + espuma na base"""
    tx, ty, tz = top
    ox, oy = out
    side = Vector((-oy, ox, 0))
    pts = []
    H = tz - bottom_z
    for i in range(9):
        t = i / 8
        f = min(1.0, t * 3.0)
        # parabola: avanca 'lip' e cai
        pts.append(Vector((tx + ox * lip * (1 - (1 - f) ** 2), ty + oy * lip * (1 - (1 - f) ** 2), tz - H * t ** 1.15)))
    for k, (w, m, off) in enumerate(((width, "Water", 0.0), (width * 0.7, "Water_Fall", -0.25),
                                     (width * 0.35, "Foam", -0.4))):
        prof = [(-w / 2, 0.0), (w / 2, 0.0), (w / 2 * 0.95, 0.35), (-w / 2 * 0.95, 0.35)]
        shifted = [p + Vector((ox, oy, 0)) * off for p in pts]
        mb.sweep(shifted, prof, m, True, up=(ox, oy, 0))
    if foam:
        b = pts[-1] + Vector((ox, oy, 0)) * 1.0
        for i in range(9):
            mb.ico(rng.uniform(0.9, 1.8) * width / 6, (b.x + side.x * rng.uniform(-width / 2, width / 2) + ox * rng.uniform(-1, 1.5),
                                                      b.y + side.y * rng.uniform(-width / 2, width / 2) + oy * rng.uniform(-1, 1.5),
                                                      bottom_z + rng.uniform(-0.2, 0.6)), "Foam", 1, (1, 1, 0.55), jitter=0.2)


def build():
    rng = random.Random(606)
    canal()
    pool_and_river(rng)
    wheel(rng)
    wheel_house(rng)
    bridges(rng)
    sources(rng)


def canal():
    rng = random.Random(611)
    mb = MB("WATER_Canal_Ledge", C, rng)
    y0, y1 = L.CANAL_Y
    mb.box2((L.WEST_X + 1, y0 + 1.6, 11.5), (L.EAST_X - 1, y1 - 0.6, WZ_CANAL), "Water", 0.0)
    # vertedouro atravessa o passeio e despeja no tanque
    sx = L.SPILL_X
    mb.box2((sx - 3.5, L.MID_FRONT_Y, 11.5), (sx + 3.5, y0 + 1.6, WZ_CANAL - 0.3), "Water", 0.0)
    # soleira de pedra do vertedouro
    mb.box2((sx - 4.6, L.MID_FRONT_Y - 1.2, 11.0), (sx + 4.6, L.MID_FRONT_Y + 0.4, 12.4), "Stone_Light", 0.2)
    waterfall(mb, (sx, L.MID_FRONT_Y - 0.6, WZ_CANAL - 0.4), WZ_RIVER, 7.0, rng, out=(0, -1), lip=2.5)
    # linhas de corrente (espuma) no canal apontando para o vertedouro
    for i in range(26):
        x = rng.uniform(L.WEST_X + 4, L.EAST_X - 4)
        y = rng.uniform(y0 + 2.5, y1 - 1.5)
        mb.box((rng.uniform(2, 5), 0.25, 0.08), (x, y, WZ_CANAL + 0.03), (0, 0, 0), "Foam", 0.0)
    mb.finish()


def pool_and_river(rng):
    mb = MB("WATER_Pool_River", C, rng)
    px0, py0, px1, py1 = L.POOL
    rx0, rx1 = L.RIVER_X
    # tanque: fundo, agua, borda de pedra (parapeito) exceto por onde o rio sai
    mb.box2((px0, py0, 0.0), (px1, py1, 1.0), "Stone_Dark", 0.0)
    mb.box2((px0 + 1.2, py0 + 1.2, 1.0), (px1 - 1.2, py1 - 0.2, WZ_RIVER), "Water", 0.0)
    for (a, b) in (((px0 + 0.6, py0 + 0.6), (px0 + 0.6, py1)), ((px1 - 0.6, py0 + 0.6), (px1 - 0.6, py1)),
                   ((px0 + 0.6, py0 + 0.6), (rx0 - 0.6, py0 + 0.6)), ((rx1 + 0.6, py0 + 0.6), (px1 - 0.6, py0 + 0.6))):
        masonry_wall(mb, a, b, 0.0, F0, 1.2, rng, course=1.4)
        stone_parapet(mb, "Water", [(a[0], a[1], F0), (b[0], b[1], F0)], h=1.6, w=1.4, rng=rng)
    # rio: paredes de arrimo, leito, agua, corrimao de madeira nas margens
    ys, ye = py0 + 0.6, -62.0
    mb.box2((rx0, ye - 1, 0.0), (rx1, ys, 1.5), "Stone_Dark", 0.0)
    mb.box2((rx0 + 0.6, ye - 1, 1.5), (rx1 - 0.6, ys + 0.6, WZ_RIVER), "Water", 0.0)
    for x in (rx0, rx1):
        masonry_wall(mb, (x, ye), (x, ys), 0.0, F0, 1.2, rng, course=1.4)
    # pedras no leito e espuma (corrente)
    for i in range(22):
        y = rng.uniform(ye + 2, ys - 2)
        if abs(y - L.WHEEL_C[1]) < 11:
            continue
        mb.rock((rng.uniform(rx0 + 1.5, rx1 - 1.5), y, 2.2), (rng.uniform(1.0, 2.0), rng.uniform(1.0, 2.0), 1.2),
                "Cliff_Rock", 1)
        mb.box((0.25, rng.uniform(1.5, 4), 0.08), (rng.uniform(rx0 + 1, rx1 - 1), y + 1.5, WZ_RIVER + 0.03), (0, 0, 0),
               "Foam", 0.0)
    # queda do rio no penhasco sul
    waterfall(mb, ((rx0 + rx1) / 2, ye - 0.5, WZ_RIVER - 0.1), -44.0, rx1 - rx0 - 1.0, rng, out=(0, -1), lip=3.0,
              foam=False)
    for i in range(10):
        mb.ico(rng.uniform(2.0, 4.0), ((rx0 + rx1) / 2 + rng.uniform(-6, 6), ye - 6 + rng.uniform(-3, 3),
                                      -44 + rng.uniform(0, 6)), "Foam", 1, (1, 1, 0.6), jitter=0.2)
    mb.finish()
    fn = MB("WATER_River_Fences", C, rng)
    # guarda-corpo das margens (abre nas pontes e na roda)
    wy = L.WHEEL_C[1]
    for x in (rx0 - 0.9, rx1 + 0.9):
        spans = [(ye + 1.5, L.BRIDGE_MAIN_Y - 6.0), (L.BRIDGE_MAIN_Y + 6.0, wy - 11.5),
                 (wy + 11.5, L.BRIDGE_BACK_Y - 3.5)]
        if x > rx1:
            spans = [(ye + 1.5, L.BRIDGE_MAIN_Y - 6.0), (L.BRIDGE_MAIN_Y + 6.0, wy - 3.0),
                     (wy + 3.0, L.BRIDGE_BACK_Y - 3.5)]
        for a, b in spans:
            fence(fn, "Water", [(x, a, F0), (x, b, F0)], h=3.0, post_step=4.0, rng=rng)
    fn.finish()
    # colisao: leito do tanque e rio (caiu, nao prende: leito so 1.3 abaixo da margem? nao - cercado)
    A = "Water"
    col_box2(A, (px0, py0, -2), (px1, py1, 1.0))
    col_box2(A, (rx0, ye - 1, -2), (rx1, ys, 1.5))
    for x in (rx0, rx1):
        col_box2(A, (x - 0.6, ye, 0), (x + 0.6, ys, F0))
    col_box2(A, (px0, py0, 0), (px0 + 1.2, py1, F0 + 1.6))
    col_box2(A, (px1 - 1.2, py0, 0), (px1, py1, F0 + 1.6))
    col_box2(A, (px0, py0, 0), (rx0, py0 + 1.2, F0 + 1.6))
    col_box2(A, (rx1, py0, 0), (px1, py0 + 1.2, F0 + 1.6))


def wheel(rng):
    """roda d'agua (undershot) no rio, eixo em X a z11 entra na casa da roda e segue ate a ala dos foles"""
    wx, wy = L.WHEEL_C
    R = L.WHEEL_R
    az = 11.0
    mb = MB("WATER_Waterwheel", C, rng)
    Wd = 3.4
    for s in (-1, 1):
        x = wx + s * Wd / 2
        pts = [Vector((x, wy + math.cos(D(a)) * R, az + math.sin(D(a)) * R)) for a in range(0, 361, 15)]
        mb.sweep(pts, [(-0.35, -0.45), (0.35, -0.45), (0.35, 0.45), (-0.35, 0.45)], "Wood_Dark", True, up=(1, 0, 0))
        pts2 = [Vector((x, wy + math.cos(D(a)) * (R - 2.2), az + math.sin(D(a)) * (R - 2.2))) for a in range(0, 361, 20)]
        mb.sweep(pts2, [(-0.25, -0.3), (0.25, -0.3), (0.25, 0.3), (-0.25, 0.3)], "Wood_Dark", True, up=(1, 0, 0))
        for k in range(8):
            a = D(k * 45 + 10)
            mb.beam((x, wy, az), (x, wy + math.cos(a) * (R - 0.3), az + math.sin(a) * (R - 0.3)), 0.55, 0.55, "Wood_Light", 0.05)
        # aro de ferro
        pts3 = [Vector((x + s * 0.4, wy + math.cos(D(a)) * (R + 0.1), az + math.sin(D(a)) * (R + 0.1))) for a in range(0, 361, 15)]
        mb.sweep(pts3, [(-0.1, -0.2), (0.1, -0.2), (0.1, 0.2), (-0.1, 0.2)], "Metal_Iron", True, up=(1, 0, 0))
    # pas entre os aros
    for k in range(16):
        a = D(k * 22.5)
        p = Vector((wx, wy + math.cos(a) * (R - 1.1), az + math.sin(a) * (R - 1.1)))
        mb.box((Wd + 0.4, 0.35, 2.2), p, (a, 0, 0), "Wood_Plank", 0.05)
    # cubo e eixo (roda -> mancal leste; roda -> casa da roda -> ala dos foles)
    mb.cyl(1.4, Wd + 1.2, (wx, wy, az), (0, D(90), 0), "Metal_Dark", 12, bevel=0.1)
    mb.rod((wx + 6.5, wy, az), (L.MILL[0] + 1.6, wy, az), 0.6, "Wood_Dark", 10)
    # eixo alto (z 15.5): sai da casa da roda, cruza o vao por cima da passagem e entra na ala dos foles
    mb.rod((L.MILL[0] + 2.2, wy, 15.5), (L.FORGE_WING_R[2] - 0.8, wy, 15.5), 0.5, "Wood_Dark", 10)
    for x in (L.MILL[0] - 0.3, L.FORGE_WING_R[2] + 0.3):
        mb.box((0.8, 1.6, 1.6), (x, wy, 15.5), (0, 0, 0), "Metal_Iron", 0.08)
    for x in (wx - 3.0, wx + 3.0):
        mb.cyl(0.9, 0.6, (x, wy, az), (0, D(90), 0), "Metal_Iron", 10, bevel=0.0)
    # mancais: pilar de pedra na margem leste e na parede da casa
    for x in (L.RIVER_X[1] + 1.8,):
        mb.box((2.6, 3.2, az - 0.8), (x, wy, (az - 0.8) / 2 + 0.4), (0, 0, 0), "Stone_Light", 0.2)
        mb.box((2.8, 3.4, 1.4), (x, wy, az - 0.4), (0, 0, 0), "Metal_Iron", 0.1)
    mb.box((2.4, 3.2, az - 1.0 - F0), (L.RIVER_X[0] - 1.8, wy, (az - 1.0 + F0) / 2), (0, 0, 0), "Stone_Light", 0.2)
    mb.box((2.6, 3.4, 1.4), (L.RIVER_X[0] - 1.8, wy, az - 0.4), (0, 0, 0), "Metal_Iron", 0.1)
    # calha de agua (rego) canalizando o rio para as pas
    for s in (-1, 1):
        mb.box2((wx + s * (Wd / 2 + 0.9) - 0.4, wy - R - 3, 1.2), (wx + s * (Wd / 2 + 0.9) + 0.4, wy + R + 3, 3.6),
                "Wood_Plank", 0.06)
    mb.finish()
    col_box2("Water", (wx - Wd / 2 - 1.3, wy - R - 1, 0), (wx + Wd / 2 + 1.3, wy + R + 1, az + R + 1))
    col_box2("Water", (L.RIVER_X[1] + 0.5, wy - 1.6, F0), (L.RIVER_X[1] + 3.1, wy + 1.6, az))
    marker("VFX_Waterwheel_Rotate", (wx, wy, az), (0, D(90), 0), 4, "SINGLE_ARROW",
           props={"axis": "X", "rpm": 6, "note": "girar Waterwheel em torno do eixo X"})
    marker("VFX_Wheel_Splash", (wx, wy - R + 0.5, WZ_RIVER), (0, 0, 0), 2)


def wheel_house(rng):
    """casa da roda: eixo baixo (roda) -> roda de coroa -> pinhao no eixo alto (foles da forja); cames do eixo baixo
    acionam o martinete da oficina de refino. Porta para o patio sul.
    Casca pelo kit de arquitetura: oitao sul projetado com guincho coberto (lucam), lucarna na agua oeste, meia-agua
    leste protegendo a entrada do eixo da roda, telhado de ardosia com cumeeira arqueada e caibros aparentes."""
    from fm_arch_house import house
    import fm_arch_kit as K
    x0, y0, x1, y1 = L.MILL
    wy = L.WHEEL_C[1]
    az = 11.0
    uz = 15.5
    t = 1.4
    ze = F0 + 14.0
    ds0, ds1 = 6.5, 11.5
    FW = Frame((x0 + x1) / 2, (y0 + y1) / 2, 0.0, 0.0)
    V = dict(
        t=t, zs=4.0, ze=14.0, rise=6.2, door=(ds0, ds1, 8.0, 2.5), gjet=(1.0, 0.0), course=2.0, post=3.4,
        wins={0: [(1.5, 4.5, 8.5, 11.5)], 1: [(2.0, 5.0, 8.0, 11.0)], 2: [(4.0, 8.0, 7.0, 10.5)]},
        holes_t={1: [(wy - y0 - 1.2, wy - y0 + 1.2, az - 1.2 - F0, az + 1.2 - F0)],
                 3: [(y1 - wy - 1.0, y1 - wy + 1.0, uz - 1.0 - F0, uz + 1.0 - F0)]},
        roof=dict(m="Roof", m2="Roof_Slate_Blue", sag=0.35, over=(1.2, 1.2), ends=(1.3, 1.1), rafters=2.4),
        gables={0: dict(style="king", window=(2.0, 1.4, 1.45)), 1: dict(style="cross")},
        dormers=[dict(side=-1, y=2.6, wd=3.6, inset=1.4, h=2.8)],
        lean=[dict(edge=1, s0=3.0, s1=13.0, depth=3.4, z_hi=12.4, z_lo=10.6, content=None)],
        shutters=[(0, 1.5, 4.5, 8.5, 11.5)], flowers=[(0, 1.5, 4.5, 8.5)], paint="Wood_Painted_Red",
        floor_top=0.35,
    )
    mb = K.AMB("BLD_WheelHouse", "07_BUILDINGS", rng)
    A = "WheelHouse"
    house(mb, FW, x1 - x0, y1 - y0, F0, rng, V, area=A, name="WheelHouse")
    # guincho no oitao sul: viga saliente + roldana + corda + caixote, com telhadinho proprio (lucam)
    cxm = (x0 + x1) / 2
    ygab = y0 - 1.0
    hz = ze + 3.0
    mb.beam((cxm, ygab + 2.2, hz), (cxm, ygab - 3.5, hz), 0.8, 0.9, "Wood_Dark", 0.08)
    FH = Frame(cxm, ygab, 0.0, 0.0)
    K.gable_roof(mb, FH, 0.0, -3.4, 0.0, hz + 1.6, rng, sides=((1.2, hz + 0.55, 0.35), (1.2, hz + 0.55, 0.35)),
                 ends=((0.3, 0.0), (0.0, 0.0)), m="Roof", m2="Roof_Slate_Blue", sag=0.0, tile=(1.2, 1.8), course=1.1,
                 th=0.34, lip=0.24, horn_len=0.6, ridge_w=0.7, horns=(True, False))
    for sx in (-1, 1):
        K.lbox(mb, FH, (0.35, 0.35, 0.8), sx * 1.15, -3.1, hz + 0.3, "Wood_Dark", 0.03)
    mb.cyl(0.55, 0.35, (cxm, ygab - 3.0, hz - 0.8), (0, D(90), 0), "Metal_Dark", 10, bevel=0.0)
    mb.rod((cxm, ygab - 3.0, hz - 1.3), (cxm, ygab - 3.0, 17.4), 0.09, "Rope", 4)
    mb.box((0.5, 0.5, 0.35), (cxm, ygab - 3.0, 17.3), (0, 0, 0), "Metal_Dark", 0.03)
    crate(mb, (cxm, ygab - 3.0, 15.5), 1.6, 0.35, rng)
    from fm_parts import pave_poly
    pave_poly(mb, [(x0 + t, y0 + t), (x1 - t, y0 + t), (x1 - t, y1 - t), (x0 + t, y1 - t)], F0 + 0.05, rng, tile=2.4,
              h=0.3, grout=False)
    # eixo baixo (roda) ate a roda de coroa
    mb.rod((x1, wy, az), (x0 + 1.6, wy, az), 0.6, "Wood_Dark", 10)
    gx = x0 + 2.4
    def gear(cx, r, z, teeth, m="Wood_Light"):
        mb.cyl(r, 0.8, (cx, wy, z), (0, D(90), 0), m, 20, bevel=0.1)
        mb.cyl(r * 0.35, 1.2, (cx, wy, z), (0, D(90), 0), "Metal_Dark", 10, bevel=0.05)
        for k in range(teeth):
            a = k / teeth * math.tau
            mb.box((1.0, 0.55, 0.7), (cx, wy + math.cos(a) * (r + 0.25), z + math.sin(a) * (r + 0.25)), (a, 0, 0),
                   "Wood_Dark", 0.03)
        for k in range(4):
            a = k / 4 * math.pi
            mb.beam((cx, wy - math.cos(a) * r * 0.9, z - math.sin(a) * r * 0.9),
                    (cx, wy + math.cos(a) * r * 0.9, z + math.sin(a) * r * 0.9), 0.9, 0.4, "Wood_Dark", 0.03)
    gear(gx, 2.9, az, 18)
    gear(gx, 1.3, uz, 9)
    mb.rod((gx - 0.4, wy, uz), (x0 - 0.5, wy, uz), 0.5, "Wood_Dark", 10)
    for s in (-1, 1):
        mb.box((0.8, 0.8, uz + 1.2 - F0), (gx + 1.4, wy + s * 1.6, (F0 + uz + 1.2) / 2), (0, 0, 0), "Wood_Dark", 0.08)
    mb.box((1.0, 4.0, 0.8), (gx + 1.4, wy, uz - 0.9), (0, 0, 0), "Wood_Dark", 0.08)
    # cames no eixo baixo + martinete (pivo ao norte, cabeca ao sul)
    hx = x0 + 5.5
    for k in range(3):
        a = k * math.tau / 3
        mb.beam((hx, wy, az), (hx, wy + math.cos(a) * 2.0, az + math.sin(a) * 2.0), 0.5, 0.8, "Metal_Iron", 0.05)
    piv = Vector((hx, wy + 5.0, 9.0))
    head = Vector((hx, wy - 4.0, 8.0))
    for s in (-1, 1):
        mb.box((0.8, 0.8, 9.0 - F0), (hx + s * 1.2, piv.y, (F0 + 9.0) / 2), (0, 0, 0), "Wood_Dark", 0.1)
    mb.beam(piv + Vector((0, 1.0, 0)), head, 0.9, 0.9, "Wood_Dark", 0.08)
    mb.box((1.8, 1.8, 2.0), head + Vector((0, 0, -0.8)), (0, 0, 0), "Metal_Dark", 0.12)
    mb.box((2.4, 2.4, 2.6), (hx, head.y, F0 + 1.3), (0, 0, 0), "Metal_Iron", 0.12)
    mb.box((1.2, 0.7, 0.3), (hx, head.y, F0 + 2.75), (0, 0, 0), "Metal_Heated", 0.05)
    # bancada de refino (canto NE) + lingotes
    mb.box2((x1 - 5.0, y1 - 7.0, F0), (x1 - 1.8, y1 - 2.0, F0 + 3.0), "Wood_Plank", 0.1)
    for k in range(6):
        mb.box((1.1, 0.6, 0.45), (x1 - 3.4 + (k % 2) * 1.2 - 0.6, y1 - 6.0 + (k // 2) * 1.2, F0 + 3.25), (0, 0, 0),
               "Metal_Brass", 0.05)
    hanging_lantern(mb, ((x0 + x1) / 2 + 1.5, (y0 + y1) / 2, ze - 0.3), name="L_WheelHouse", chain=4.0)
    lantern(mb, (x0 + ds1 + 2.6, y0 - 1.9, F0), D(180), name="L_WheelHouse_Door", h=6.0)
    mb.finish()
    # casca (paredes com vao da porta, telhado, piso) criada por house(); aqui so o maquinario
    col_box2(A, (x0 + ds1 + 1.9, y0 - 2.6, F0), (x0 + ds1 + 3.3, y0 - 1.2, F0 + 7.5))
    col_box2(A, (x0 - 0.5, y0 - 0.5, ze), (x1 + 0.5, y1 + 0.5, ze + 6))
    col_box2(A, (hx - 1.6, wy - 5.5, F0), (hx + 1.6, wy + 6.5, F0 + 3.0))
    col_box2(A, (gx - 1.0, wy - 3.5, F0), (gx + 2.0, wy + 3.5, uz + 1.5))
    col_box2(A, (x1 - 5.0, y1 - 7.0, F0), (x1 - 1.8, y1 - 2.0, F0 + 3.0))
    marker("DOOR_WheelHouse", (x0 + (ds0 + ds1) / 2, y0, F0), (0, 0, 0), 1.5)
    marker("VFX_TripHammer", tuple(head), (0, 0, 0), 1.5, props={"anim": "martinete sobe/desce 1x por volta de came"})

def bridges(rng):
    """ponte principal (y -18) em arco de madeira e ponte dos fundos (y 38) sobre o rio"""
    rx0, rx1 = L.RIVER_X
    mb = MB("BLD_Bridges", "07_BUILDINGS", rng)
    for by, w in ((L.BRIDGE_MAIN_Y, 10.0), (L.BRIDGE_BACK_Y, 6.0)):
        xa, xb = rx0 - 3.5, rx1 + 3.5
        L_ = xb - xa
        n = int(L_ / 0.9)
        rise = 1.4
        # tabuleiro em arco (tabuas) sobre vigas curvas
        for i in range(n):
            x = xa + (i + 0.5) * L_ / n
            f = (x - xa) / L_
            z = F0 + rise * math.sin(math.pi * f)
            slope = rise * math.pi / L_ * math.cos(math.pi * f)
            mb.box((L_ / n - 0.08, w, 0.4), (x, by + rng.uniform(-0.1, 0.1), z - 0.2), (0, -math.atan(slope), 0),
                   "Wood_Plank", 0.05)
        for s in (-1, 1):
            pts = [Vector((xa + L_ * k / 12, by + s * (w / 2 - 0.4), F0 - 0.9 + rise * math.sin(math.pi * k / 12)))
                   for k in range(13)]
            mb.sweep(pts, [(-0.4, -0.5), (0.4, -0.5), (0.4, 0.5), (-0.4, 0.5)], "Wood_Dark", True)
            # corrimao
            posts = [Vector((xa + L_ * k / 5, by + s * (w / 2 + 0.2), F0 + rise * math.sin(math.pi * k / 5))) for k in range(6)]
            for p in posts:
                mb.box((0.8, 0.8, 3.6), (p.x, p.y, p.z + 1.6), (0, 0, 0), "Wood_Dark", 0.1)
            top = [p + Vector((0, 0, 3.2)) for p in posts]
            mb.sweep(top, [(-0.3, -0.25), (0.3, -0.25), (0.3, 0.25), (-0.3, 0.25)], "Wood_Light", True)
            mid = [p + Vector((0, 0, 1.7)) for p in posts]
            mb.sweep(mid, [(-0.2, -0.2), (0.2, -0.2), (0.2, 0.2), (-0.2, 0.2)], "Wood_Light", True)
        # cabeceiras de pedra
        for x in (xa - 0.5, xb + 0.5):
            mb.box((2.2, w + 1.6, 1.4), (x, by, F0 - 0.5), (0, 0, 0), "Stone_Light", 0.2)
        # colisao: 3 rampas suaves (arco) + corrimao
        A = "Bridge"
        k = 6
        for i in range(k):
            f0, f1 = i / k, (i + 1) / k
            za = F0 + rise * math.sin(math.pi * f0)
            zb = F0 + rise * math.sin(math.pi * f1)
            from fm_lib import col_ramp
            col_ramp(A, (xa + L_ * f0, by, za), (xa + L_ * f1, by, zb), w, 1.0)
        for s in (-1, 1):
            col_box(A, (L_, 0.8, 5.0), ((xa + xb) / 2, by + s * (w / 2 + 0.2), F0 + 2.5))
        lantern(mb, (xa - 1.0, by - w / 2 - 1.2, F0), D(90), name="L_Bridge_%d_W" % int(by), h=6.5)
        lantern(mb, (xb + 1.0, by + w / 2 + 1.2, F0), D(-90), name="L_Bridge_%d_E" % int(by), h=6.5)
    mb.finish()


def sources(rng):
    """nascentes: cachoeira NO e NE caem no canal; cachoeira central desce da montanha, cruza o terraco e cai no canal"""
    mb = MB("WATER_Waterfalls", C, rng)
    y0, y1 = L.CANAL_Y
    cy = (y0 + y1) / 2 + 1.0
    # NO: da montanha (z 55) no extremo oeste do canal
    waterfall(mb, (L.WEST_X + 4, y1 + 2.0, 58.0), WZ_CANAL, 7.0, rng, out=(0, -1), lip=2.0)
    # NE: cachoeira grande (dois degraus)
    waterfall(mb, (L.EAST_X - 5, y1 + 3.0, 72.0), 40.0, 9.0, rng, out=(0, -1), lip=2.5)
    mb.box2((L.EAST_X - 12, y1 - 3.0, 38.0), (L.EAST_X + 2, y1 + 3.5, 40.2), "Cliff_Rock", 0.4)
    mb.box2((L.EAST_X - 11, y1 - 2.5, 40.0), (L.EAST_X + 1, y1 + 3.0, 40.4), "Water", 0.0)
    waterfall(mb, (L.EAST_X - 5, y1 - 2.6, 40.3), WZ_CANAL, 8.0, rng, out=(0, -1), lip=1.8)
    # central: canal de pedra no terraco (atras da torre) + queda na parede superior
    sx = 0.0
    mb.box2((sx - 3.6, L.UPPER_FRONT_Y - 0.2, L.TERR - 2.2), (sx + 3.6, L.TERR_BACK_Y + 2, L.TERR - 1.0), "Stone_Dark", 0.0)
    for s in (-1, 1):
        mb.box2((sx + s * 3.6 - 0.7, L.UPPER_FRONT_Y + 1.0, L.TERR - 2.2), (sx + s * 3.6 + 0.7, L.TERR_BACK_Y + 2, L.TERR + 0.8),
                "Stone_Light", 0.2)
    mb.box2((sx - 2.9, L.UPPER_FRONT_Y - 0.2, L.TERR - 1.0), (sx + 2.9, L.TERR_BACK_Y + 2, WZ_TERR), "Water", 0.0)
    waterfall(mb, (sx, L.TERR_BACK_Y + 4, 50.0), WZ_TERR, 6.0, rng, out=(0, -1), lip=1.5)
    mb.box2((sx - 3.6, L.UPPER_FRONT_Y - 1.4, 11.5), (sx + 3.6, L.UPPER_FRONT_Y + 0.2, WZ_TERR - 0.6), "Stone_Dark", 0.2)
    waterfall(mb, (sx, L.UPPER_FRONT_Y - 0.4, WZ_TERR - 0.2), WZ_CANAL, 5.8, rng, out=(0, -1), lip=1.6)
    # passarela de pedra sobre o canal central (continuidade do terraco)
    for yy in (L.FLIGHT2_Y1 + 6.0,):
        mb.box2((sx - 5.0, yy - 3.0, L.TERR - 0.8), (sx + 5.0, yy + 3.0, L.TERR + 0.3), "Stone_Light", 0.25)
        col_box2("Terrace", (sx - 5.0, yy - 3.0, L.TERR - 1.0), (sx + 5.0, yy + 3.0, L.TERR + 0.3))
    mb.finish()
    for s in (-1, 1):
        col_box2("Terrace", (sx + s * 3.6 - 0.7, L.UPPER_FRONT_Y, L.TERR - 2.2), (sx + s * 3.6 + 0.7, L.FLIGHT2_Y1 + 3.0, L.TERR + 0.8))
        col_box2("Terrace", (sx + s * 3.6 - 0.7, L.FLIGHT2_Y1 + 9.0, L.TERR - 2.2), (sx + s * 3.6 + 0.7, L.TERR_BACK_Y + 2, L.TERR + 0.8))
    marker("VFX_Waterfall_NW", (L.WEST_X + 4, y1, 35), (0, 0, 0), 3)
    marker("VFX_Waterfall_NE", (L.EAST_X - 5, y1, 45), (0, 0, 0), 3)
    marker("VFX_Waterfall_Center", (0, L.UPPER_FRONT_Y, 20), (0, 0, 0), 3)
    marker("VFX_Waterfall_Spill", (L.SPILL_X, L.MID_FRONT_Y, 8), (0, 0, 0), 3)
    marker("VFX_Waterfall_South", ((L.RIVER_X[0] + L.RIVER_X[1]) / 2, -64, -20), (0, 0, 0), 3)
