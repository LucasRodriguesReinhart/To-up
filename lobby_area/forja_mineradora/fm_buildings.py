# fm_buildings - praca + caminhos pavimentados, loja (interior completo), cabanas de mineiros (entraveis),
# estacao de carga sobre o trilho, galpao aberto de cristais na margem leste.
# Passe de acabamento: a casca das construcoes vem de fm_arch_house/fm_arch_kit (telhado em fiadas com cumeeira
# arqueada, oitoes com enxaimel, balancos, lucarnas, empenas cruzadas, chamines, meias-aguas, fundacao irregular)
# e cada cabana e uma variante propria (nao a mesma saida do gerador).
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, resample, bezier, point_in_poly
from fm_parts import (Frame, masonry_wall, timber_wall, window_glow, arch, lantern, hanging_lantern, crate, barrel,
                      crystal_cluster, pave_poly, pave_ring, banner, emblem_pickaxe, fence, mine_cart, P3, frustum,
                      stone_parapet, plank_floor)
import fm_arch_kit as K
from fm_arch_house import house
import fm_layout as L

F0 = L.FLOOR


def ribbon(pts, w):
    """poligono de uma faixa de largura w ao longo da polilinha"""
    pts = [Vector((p[0], p[1], 0)) for p in pts]
    left, right = [], []
    for i, p in enumerate(pts):
        j = min(i + 1, len(pts) - 1)
        k = max(i - 1, 0)
        t = (pts[j] - pts[k]).normalized()
        s = Vector((-t.y, t.x, 0))
        left.append(p + s * w / 2)
        right.append(p - s * w / 2)
    return [(p.x, p.y) for p in left + list(reversed(right))]


# ------------------------------------------------------------------ praca e caminhos
PATHS = {
    # nome: (pontos, largura)
    "Avenue": ([(0, -62.2), (0, -52)], 20.0),
    "West_Road": ([(-24, -36), (-38, -24), (-44, -8), (-44, 34)], 10.0),
    "Mine_Road": ([(-22, -44), (-40, -46), (-54, -40), (-60, -38)], 10.0),
    "Back_Court": ([(-116, 41), (50, 41)], 10.0),
    "East_Lane": ([(38, -8), (38, 36)], 7.0),
    "East_Road": ([(24, -20), (40, -18), (54, -18)], 10.0),
    "East_Bank": ([(70, -18), (96, -18), (96, 36), (70, 41)], 9.0),
    "East_Back": ([(70, 41), (116, 41)], 9.0),
    "Shop_Apron": ([(18, -40), (26, -39)], 8.0),
    "Mill_Apron": ([(38, 4), (L.MILL[0] + 9.0, 6), (L.MILL[0] + 9.0, 11)], 6.0),
}


def plaza_and_paths(rng):
    mb = MB("TER_Plaza_Paving", "02_TERRAIN", rng)
    cx, cy = 0.0, -30.0
    R = 25.0
    # praca circular: aneis de pedra + anel escuro de borda + mosaico central
    mb.cyl(R + 1.2, 0.8, (cx, cy, F0 - 0.2), (0, 0, 0), "Stone_Grout", 48, bevel=0.0)
    pave_ring(mb, cx, cy, 5.0, R - 1.4, F0 + 0.02, rng, 0, 360, ring_w=2.6, h=0.33, m="Stone_Paving")
    pave_ring(mb, cx, cy, R - 1.4, R + 0.8, F0 + 0.02, rng, 0, 360, ring_w=2.2, h=0.38, m="Stone_Dark")
    # centro: medalhao com picareta e martelo em pedra clara
    mb.cyl(5.0, 0.4, (cx, cy, F0 + 0.2), (0, 0, 0), "Stone_Dark", 32, bevel=0.1)
    mb.cyl(4.2, 0.45, (cx, cy, F0 + 0.25), (0, 0, 0), "Stone_Light", 32, bevel=0.1)
    for a in range(0, 360, 45):
        p = Vector((cx + math.cos(D(a)) * 3.2, cy + math.sin(D(a)) * 3.2, F0 + 0.5))
        mb.box((1.6, 0.5, 0.12), p, (0, 0, D(a)), "Metal_Brass", 0.02)
    mb.finish()
    pv = MB("TER_Path_Paving", "02_TERRAIN", rng)
    for name, (pts, w) in PATHS.items():
        pts2 = []
        for a, b in zip(pts, pts[1:]):
            pts2 += resample([Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))], 3.0)[:-1]
        pts2.append(Vector((pts[-1][0], pts[-1][1], 0)))
        poly = ribbon(pts2, w)
        pave_poly(pv, poly, F0 + 0.02, rng, tile=2.6, h=0.33, grout=True, bevel=0.0)
        # meio-fio de pedras nas bordas
        for i, p in enumerate(pts2[:-1]):
            q = pts2[i + 1]
            t = (q - p).normalized()
            s = Vector((-t.y, t.x, 0))
            for k in (-1, 1):
                c = (p + q) / 2 + s * k * (w / 2 + 0.35)
                if rng.random() < 0.85:
                    pv.box(((q - p).length - 0.2, 0.7, 0.55), (c.x, c.y, F0 + 0.2), (0, 0, math.atan2(t.y, t.x)),
                           "Stone_Light", 0.12)
    # patios diante dos pes das escadas dos portais
    for px in L.PORTAL_X:
        pave_poly(pv, [(px - 8, 38), (px + 8, 38), (px + 8, L.FLIGHT1_Y0), (px - 8, L.FLIGHT1_Y0)], F0 + 0.02, rng,
                  tile=2.6, h=0.33, grout=True)
    pv.finish()


# ------------------------------------------------------------------ loja
SHOP_V = dict(
    t=1.6, zs=6.8, ze=13.0, rise=7.0, door=(3.5, 8.5, 8.0, 2.5), course=1.9, post=3.4,
    # balanco nos dois lados compridos (sul 0.9, norte 0.7) a 6.8 do piso: passa por cima da cabeca
    jet=(0.0, 0.9, 0.0, 0.7), gjet=(1.0, 0.0),
    wins={0: [(11.0, 16.0, 1.9, 6.3), (11.4, 15.6, 8.4, 11.6)],
          1: [(4.0, 6.6, 2.2, 5.2), (5.2, 7.6, 8.2, 11.4), (8.8, 11.2, 8.2, 11.4), (13.2, 15.6, 8.2, 11.2)],
          2: [(6.0, 10.0, 8.0, 11.4)],
          3: [(10.4, 13.4, 8.2, 11.4)]},
    roof=dict(m="Roof_Red", m2="Roof_Red_Deep", sag=0.45, over=(1.3, 1.4), ends=(1.2, 1.0), rafters=2.2),
    gables={0: dict(style="cross", window=(2.6, 2.0, 2.7)), 1: dict(style="king", window=(2.0, 1.6, 2.4))},
    dormers=[dict(side=1, y=-1.0, wd=7.0, inset=0.0, h=0.0, jet=0.6, style="king", over=0.8),
             dict(side=-1, y=-4.0, wd=3.4, inset=1.6, h=2.8)],
    chimneys=[dict(kind="side", side=-1, y=3.5, name="Shop")],
    shutters=[(1, 13.2, 15.6, 8.2, 11.2), (0, 11.4, 15.6, 8.4, 11.6)],
    flowers=[(1, 5.2, 7.6, 8.2), (1, 8.8, 11.2, 8.2), (1, 4.0, 6.6, 2.2)],
    paint="Wood_Teal", floor_top=0.55,
)


def shop(rng):
    x0, y0, x1, y1 = L.SHOP
    t = SHOP_V["t"]
    zs, ze = F0 + SHOP_V["zs"], F0 + SHOP_V["ze"]
    cxs, cys = (x0 + x1) / 2, (y0 + y1) / 2
    # referencial: local -y = oeste (fachada para a praca), local +x = sul
    FS = Frame(cxs, cys, 0.0, D(-90))
    mb = K.AMB("BLD_Shop", "07_BUILDINGS", rng)
    A = "Shop"
    info = house(mb, FS, x1 - x0, y1 - y0, F0, rng, SHOP_V, area=A, name="Shop")
    # toldo listrado so sobre a vitrine, com sanefa recortada e maos-francesas
    for i in range(4):
        yy = y1 - 11.3 - i * 1.3
        mm = "Cloth_Red" if i % 2 else "Cloth_Canvas"
        mb.box((3.4, 1.3, 0.28), (x0 - 1.6, yy, 11.2), (0, D(-17), 0), mm, 0.03)
        mb.box((0.22, 1.3, 0.75), (x0 - 3.25, yy, 10.35), (0, 0, 0), "Cloth_Canvas" if i % 2 else "Cloth_Red", 0.02)
    for yy in (y1 - 10.9, y1 - 16.1):
        mb.beam((x0 - 0.1, yy, 9.9), (x0 - 3.1, yy, 10.7), 0.3, 0.3, "Wood_Dark", 0.03)
    mb.beam((x0 - 3.2, y1 - 10.8, 10.75), (x0 - 3.2, y1 - 16.2, 10.75), 0.3, 0.3, "Wood_Dark", 0.03)
    # lintel de pedra sobre a vitrine
    mb.box((t + 0.4, 5.6, 0.7), (x0 + t / 2, y1 - 13.5, F0 + 6.75), (0, 0, 0), "Stone_Dark", 0.12)
    # cobertura da porta (mini-telhado de duas aguas sobre maos-francesas)
    Fd = Frame(x0, y1 - 6.0, 0.0, D(-90))
    K.gable_roof(mb, Fd, 0.0, -2.5, 0.1, 15.2, rng, sides=((3.0, 13.7, 0.35), (3.0, 13.7, 0.35)),
                 ends=((0.25, 0.0), (0.0, 0.0)), m="Roof_Red", m2="Roof_Red_Deep", sag=0.0, tile=(1.4, 2.0),
                 course=1.2, th=0.36, lip=0.25, horn_len=0.7, ridge_w=0.8)
    for sx in (-1, 1):
        K.lbeam(mb, Fd, (sx * 2.6, 0.0, 11.4), (sx * 2.6, -2.3, 13.4), 0.4, 0.45, "Wood_Dark", 0.05)
        K.lbox(mb, Fd, (0.5, 2.6, 0.5), sx * 2.6, -1.2, 13.5, "Wood_Dark", 0.05)
    # placa pendurada (picareta + gema)
    mb.beam((x0 - 0.2, y1 - 1.0, 15.0), (x0 - 4.5, y1 - 1.0, 15.0), 0.4, 0.4, "Wood_Dark", 0.03)
    mb.beam((x0 - 0.2, y1 - 1.0, 12.4), (x0 - 2.6, y1 - 1.0, 14.9), 0.3, 0.3, "Wood_Dark", 0.03)
    mb.box((0.4, 3.6, 2.8), (x0 - 3.6, y1 - 1.0, 13.2), (0, 0, D(3)), "Wood_Plank", 0.1)
    mb.box((0.5, 3.9, 0.35), (x0 - 3.6, y1 - 1.0, 14.55), (0, 0, D(3)), "Wood_Dark", 0.04)
    emblem_pickaxe(mb, Vector((x0 - 3.85, y1 - 1.0, 13.2)), D(-90), s=0.32, normal_off=0.0)
    crystal_cluster(mb, (x0 - 3.6, y1 - 1.0, 14.8), 0.35, "Crystal_Blue", rng, 3)
    # interior: piso de tabuas, balcao em L, prateleiras, vitrines
    plank_floor(mb, Frame((x0 + x1) / 2, (y0 + y1) / 2, 0, 0.0), x1 - x0 - 2 * t, y1 - y0 - 2 * t, F0 + 0.3, rng)
    cx = x0 + 10.5
    mb.box2((cx - 0.8, y0 + 3.0, F0), (cx + 0.8, y1 - 5.5, F0 + 3.2), "Wood_Plank", 0.1)
    mb.box2((cx - 1.1, y0 + 2.8, F0 + 3.2), (cx + 1.1, y1 - 5.3, F0 + 3.6), "Wood_Light", 0.1)
    for yy in (y0 + 4.0, (y0 + y1) / 2 - 1.0, y1 - 7.0):
        mb.box((1.9, 0.35, 2.6), (cx, yy, F0 + 1.6), (0, 0, 0), "Wood_Dark", 0.05)
    for zz in (F0 + 2.0, F0 + 4.4, F0 + 6.8):
        mb.box2((x1 - 2.6, y0 + 2.0, zz), (x1 - 1.6, y1 - 2.0, zz + 0.3), "Wood_Light", 0.05)
        for k in range(8):
            yy = y0 + 3.0 + k * 1.7
            if k % 3 == 0:
                mb.beam((x1 - 2.1, yy, zz + 0.3), (x1 - 2.1, yy + 0.4, zz + 2.1), 0.25, 0.25, "Wood_Light", 0.0)
                mb.box((0.4, 1.4, 0.4), (x1 - 2.1, yy + 0.5, zz + 2.0), (0, 0, 0), "Metal_Iron", 0.03)
            else:
                crystal_cluster(mb, (x1 - 2.1, yy, zz + 0.3), 0.34, "Crystal_Blue" if k % 2 else "Crystal_Purple", rng, 2)
    for yy in (y0 + 3.5, y1 - 3.5):
        mb.box2((x0 + 3.0, yy - 1.2, F0), (x0 + 6.0, yy + 1.2, F0 + 2.8), "Wood_Dark", 0.1)
        crystal_cluster(mb, (x0 + 4.5, yy, F0 + 2.8), 0.45, "Crystal_Blue", rng, 4)
    hanging_lantern(mb, ((x0 + x1) / 2, (y0 + y1) / 2, ze - 0.2), name="L_Shop_In", chain=5.5)
    light("L_Shop_Fill", "POINT", ((x0 + x1) / 2, (y0 + y1) / 2, 12.0), 700, (1.0, 0.72, 0.45), 3.0)
    lantern(mb, (x0 - 2.0, y0 + 2.0, F0), D(180), name="L_Shop_Door", h=6.5)
    mb.finish()
    # colisao do mobiliario (a casca ja foi criada por house())
    col_box2(A, (cx - 1.1, y0 + 2.8, F0), (cx + 1.1, y1 - 5.3, F0 + 3.6))
    col_box2(A, (x1 - 2.6, y0 + 2.0, F0), (x1 - 1.6, y1 - 2.0, F0 + 9.0))
    for yy in (y0 + 3.5, y1 - 3.5):
        col_box2(A, (x0 + 3.0, yy - 1.2, F0), (x0 + 6.0, yy + 1.2, F0 + 2.8))
    marker("NPC_Shop", (cx + 2.5, (y0 + y1) / 2, F0 + 0.3), (0, 0, D(90)), 2, "ARROWS", props={"npc": "Lojista"})
    marker("INTERACT_Shop", (cx, (y0 + y1) / 2, F0 + 3.6), (0, 0, 0), 1.5, "SPHERE")
    marker("PLAYER_INTERACT_Shop", (cx - 4.0, (y0 + y1) / 2, F0 + 0.3), (0, 0, 0), 2, "CIRCLE")
    marker("DOOR_Shop", (x0, y1 - 6.0, F0), (0, 0, 0), 1.5)


# ------------------------------------------------------------------ cabanas de mineiros (entraveis)
# Cinco variantes com silhueta propria. Coordenadas locais: porta na face -Y; x em [-w/2, w/2].
CABINS = {
    # oeste, porta para o penhasco (oeste): oitao dos fundos (leste, visto da praca) projetado com janela,
    # chamine de pedra na lateral sul, lucarna, telheiro de lenha na lateral norte. Ardosia + reboco creme.
    "West_A": dict(
        pos=(-84.0, -4.0, -90), w=14.0, d=12.0,
        V=dict(zs=3.5, ze=10.5, rise=5.8, door=(4.8, 9.2, 7.5, 0.0), gjet=(0.0, 1.0), plaster="Plaster",
               wins={0: [(1.6, 3.8, 3.8, 6.4)], 1: [(3.0, 5.8, 4.0, 6.6)], 2: [(3.0, 6.6, 3.9, 6.6)],
                     3: [(8.6, 10.4, 4.6, 6.4)]},
               roof=dict(m="Roof", m2="Roof_Slate_Blue", sag=0.35, over=(1.3, 1.1), ends=(0.9, 1.3), cx=0.6),
               gables={0: dict(style="king", window=(1.8, 1.5, 2.2)), 1: dict(style="cross", window=(2.2, 1.7, 2.1))},
               chimneys=[dict(kind="side", side=1, y=2.6, name="Cabin_West_A")],
               dormers=[dict(side=1, y=-2.4, wd=3.4, inset=1.4, h=2.6)],
               lean=[dict(edge=3, s0=1.2, s1=7.8, depth=3.2, z_hi=8.4, z_lo=6.9, content="logs")],
               shutters=[(2, 3.0, 6.6, 3.9, 6.6)], flowers=[(2, 3.0, 6.6, 3.9)], paint="Wood_Teal"),
        inner=[("bed", -3.6, 1.8, 0), ("table", 1.6, -0.6, ((-2.4, 0.0), (2.4, 0.0))), ("shelf", -5.0, -2.8, 1),
               ("crate", 4.4, -3.2), ("rug", 0.8, 1.2)]),
    # oeste: sobrado estreito - terreo alto de pedra com porta em arco, andar de cima em balanco (sul e leste),
    # telhado vermelho ingreme, lucarna, chamine na lateral norte, jirau interno. Reboco ocre.
    "West_B": dict(
        pos=(-94.0, 20.0, -90), w=12.0, d=11.0,
        V=dict(zs=8.2, ze=13.8, rise=7.2, door=(3.8, 8.2, 6.8, 1.7), jet=(0.0, 0.9, 0.85, 0.0), gjet=(0.0, 0.0),
               plaster="Plaster_Ochre", course=1.7,
               wins={0: [(9.0, 10.8, 3.2, 5.6)], 1: [(3.2, 5.0, 3.0, 5.6), (4.0, 7.2, 9.4, 12.4)],
                     2: [(2.2, 4.0, 3.0, 5.6), (3.0, 6.0, 9.4, 12.4)], 3: [(6.5, 8.3, 9.6, 12.2)]},
               roof=dict(m="Roof_Red", m2="Roof_Red_Deep", sag=0.4, over=(1.0, 1.2), ends=(1.2, 1.0), course=1.6, cx=-0.5),
               gables={0: dict(style="collar", window=(1.6, 1.4, 2.6)),
                       1: dict(style="collar", window=(2.0, 1.8, 2.4))},
               chimneys=[dict(kind="side", side=-1, y=-1.0, name="Cabin_West_B")],
               dormers=[dict(side=1, y=-0.8, wd=3.2, inset=1.6, h=2.6)],
               shutters=[(2, 3.0, 6.0, 9.4, 12.4)], flowers=[(1, 4.0, 7.2, 9.4)], paint="Wood_Teal"),
        inner=[("bed", 2.6, 1.3, 0), ("table", -2.0, 2.4, ((0.0, -1.9),)), ("crate", 3.4, -2.9),
               ("barrel", -3.4, -3.0), ("rug", 0.0, -0.6), ("loft", 0.6, 4.1)]),
    # oeste, porta para o sul: telhado de meia-tesoura (jerkinhead) em ripas de madeira com musgo, alpendre com
    # banco na frente, chamine na lateral leste, floreira. Reboco creme.
    "West_C": dict(
        pos=(-64.0, 26.0, 0), w=12.0, d=10.0,
        V=dict(zs=3.5, ze=9.6, rise=5.6, door=(3.8, 8.2, 7.2, 0.0), plaster="Plaster",
               wins={0: [(1.4, 3.4, 3.8, 6.2), (9.4, 10.8, 4.2, 6.2)], 1: [(1.2, 3.8, 3.9, 6.5)],
                     2: [(4.0, 7.0, 4.0, 6.5)], 3: [(1.0, 2.8, 4.0, 6.3)]},
               roof=dict(m="Roof_Shingle_Wood", m2="Roof_Shingle_Moss", alt=0.16, sag=0.25, over=(1.5, 1.5),
                         ends=(1.2, 1.2), hips=(1.9, 1.9), tile=(1.8, 2.8), course=1.55),
               gables={0: dict(style="king", window=(1.5, 1.2, 1.4)), 1: dict(style="cross")},
               chimneys=[dict(kind="side", side=1, y=1.4, name="Cabin_West_C")],
               porch=dict(s0=0.8, s1=11.2, depth=3.2, z_hi=8.1, z_lo=6.8, bench=(0.9, 3.3)),
               shutters=[(0, 9.4, 10.8, 4.2, 6.2), (1, 1.2, 3.8, 3.9, 6.5)], flowers=[(0, 1.4, 3.4, 3.8)],
               paint="Wood_Painted_Red", lantern="hang"),
        inner=[("bed", -2.8, 0.9, 0), ("table", 1.0, -1.4, ((2.2, 0.0), (0.0, 1.9))), ("crate", -3.6, -2.7),
               ("shelf", 2.4, 3.1, 0), ("rug", 0.4, 1.0)]),
    # leste, porta para o penhasco (leste): saltbox - a agua norte desce ate um anexo baixo de tabuas, janela
    # saliente (bay) na lateral sul, chamine central saindo pela cumeeira, oitao dos fundos (caminho) projetado.
    # Ardosia + reboco ocre.
    "East_A": dict(
        pos=(114.0, -6.0, 90), w=14.0, d=12.0,
        V=dict(zs=3.5, ze=10.5, rise=5.6, door=(4.8, 9.2, 7.5, 0.0), gjet=(0.0, 0.9), plaster="Plaster_Ochre",
               wins={0: [(10.4, 12.4, 3.8, 6.4)], 2: [(2.6, 5.4, 3.9, 6.6), (8.6, 11.0, 3.9, 6.6)]},
               bays=[dict(edge=3, s=6.0, wd=4.2, z0=4.2, z1=8.2, out=1.1)],
               roof=dict(m="Roof", m2="Roof_Slate_Blue", sag=0.3, over=(1.2, 0.9), ends=(1.0, 1.3)),
               outshot=dict(depth=2.8, y0=-4.8, y1=4.6, window=0.0),
               gables={0: dict(style="plain", window=(1.5, 1.3, 2.0)), 1: dict(style="king", window=(2.2, 1.7, 2.2))},
               chimneys=[dict(kind="ridge", y=3.2, name="Cabin_East_A")],
               shutters=[(2, 2.6, 5.4, 3.9, 6.6)], flowers=[(2, 8.6, 11.0, 3.9)], paint="Wood_Painted_Red"),
        inner=[("bed", -3.8, 1.6, 0), ("table", 2.6, -0.8, ((-2.4, 0.0), (2.2, 0.0))), ("crate", -4.4, -3.4),
               ("shelf", 5.0, 2.6, 1), ("rug", 0.0, -1.0)]),
    # leste: empena cruzada projetada na lateral sul (com janela no oitao), chamine na lateral norte, telheiro de
    # lenha nos fundos (voltado para o caminho), telhado vermelho, postigos verde-azulados. Reboco creme.
    "East_B": dict(
        pos=(116.0, 18.0, 90), w=12.0, d=11.0,
        V=dict(zs=3.5, ze=10.3, rise=5.4, door=(3.8, 8.2, 7.4, 0.0), plaster="Plaster",
               wins={0: [(0.9, 2.7, 4.0, 6.4)], 1: [(6.6, 9.0, 4.0, 6.5)], 2: [(6.6, 9.4, 3.9, 6.6)],
                     3: [(4.0, 7.0, 3.9, 6.8)]},
               roof=dict(m="Roof_Red", m2="Roof_Red_Deep", sag=0.3, over=(1.1, 1.1), ends=(0.9, 1.2), cx=0.5),
               dormers=[dict(side=-1, y=0.0, wd=5.8, inset=0.0, h=0.0, jet=0.7, style="collar", over=0.7)],
               gables={0: dict(style="plain"), 1: dict(style="collar", window=(2.0, 1.6, 2.2))},
               chimneys=[dict(kind="side", side=1, y=-2.6, name="Cabin_East_B")],
               lean=[dict(edge=2, s0=0.6, s1=5.4, depth=3.0, z_hi=8.2, z_lo=6.8, content="logs")],
               shutters=[(3, 4.0, 7.0, 3.9, 6.8), (2, 6.6, 9.4, 3.9, 6.6)], flowers=[(3, 4.0, 7.0, 3.9)],
               paint="Wood_Teal"),
        inner=[("bed", -2.8, 1.4, 0), ("table", 1.4, 1.6, ((0.0, -1.9), (2.2, 0.0))), ("crate", -3.6, -3.1),
               ("shelf", 3.9, -0.4, 1), ("rug", 0.2, -1.4)]),
}



def cabin_interior(mb, F, w, d, rng, items, A, name):
    zf = F0 + 0.55
    for it in items:
        kind = it[0]
        if kind == "bed":
            _, x, y, rot = it
            sx, sy = (3.6, 5.4) if not rot else (5.4, 3.6)
            p = F.p(x, y)
            mb.box((sx, sy, 1.2), (p.x, p.y, zf + 0.6), F.r(), "Wood_Dark", 0.1)
            mb.box((sx - 0.4, sy - 0.4, 0.6), (p.x, p.y, zf + 1.45), F.r(), "Cloth_Canvas", 0.15)
            head = F.p(x, y + sy / 2 - 1.0) if not rot else F.p(x + sx / 2 - 1.0, y)
            mb.box((sx - 0.8, 1.3, 0.6) if not rot else (1.3, sy - 0.8, 0.6), (head.x, head.y, zf + 1.95), F.r(),
                   "Emblem_Cream", 0.2)
            blk = F.p(x, y - sy * 0.18) if not rot else F.p(x - sx * 0.18, y)
            mb.box((sx - 0.2, sy * 0.58, 0.35) if not rot else (sx * 0.58, sy - 0.2, 0.35), (blk.x, blk.y, zf + 1.8),
                   F.r(), "Cloth_Red" if rng.random() < 0.5 else "Cloth_Navy", 0.1)
            hb = F.p(x, y + sy / 2 + 0.1) if not rot else F.p(x + sx / 2 + 0.1, y)
            mb.box((sx + 0.2, 0.45, 3.0) if not rot else (0.45, sy + 0.2, 3.0), (hb.x, hb.y, zf + 1.5), F.r(),
                   "Wood_Dark", 0.08)
            col_box(A, (sx, sy, 2.4), (p.x, p.y, F0 + 1.2), F.r())
        elif kind == "table":
            _, x, y, stools = it
            p = F.p(x, y)
            mb.box((3.4, 2.4, 0.3), (p.x, p.y, zf + 2.5), F.r(0, 0, rng.uniform(-0.04, 0.04)), "Wood_Light", 0.05)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    q = F.p(x + sx * 1.3, y + sy * 0.9)
                    mb.box((0.35, 0.35, 2.4), (q.x, q.y, zf + 1.2), F.r(), "Wood_Dark", 0.0)
            xs, ys = [x - 1.7, x + 1.7], [y - 1.2, y + 1.2]
            for (dx, dy) in stools:
                q = F.p(x + dx, y + dy)
                mb.cyl(0.6, 1.6, (q.x, q.y, zf + 0.8), F.r(), "Wood_Plank", 8, bevel=0.05)
                xs += [x + dx - 0.6, x + dx + 0.6]
                ys += [y + dy - 0.6, y + dy + 0.6]
            mb.box((1.0, 0.8, 0.9), F.p(x - 0.5, y + 0.2, zf + 3.1), F.r(), "Lantern_Glow", 0.05)
            mb.cyl(0.35, 0.6, F.p(x + 0.8, y - 0.3, zf + 2.95), F.r(), "Metal_Brass", 8, bevel=0.0)
            c = F.p((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
            col_box(A, (max(xs) - min(xs), max(ys) - min(ys), 3.2), (c.x, c.y, F0 + 1.6), F.r())
        elif kind == "shelf":
            _, x, y, rot = it
            L_ = 3.4
            for zz in (zf + 1.8, zf + 3.6):
                mb.box((0.9, L_, 0.25) if rot else (L_, 0.9, 0.25), F.p(x, y, zz), F.r(), "Wood_Light", 0.03)
                for k in range(3):
                    off = -L_ / 2 + 0.6 + k * 1.1
                    q = F.p(x, y + off) if rot else F.p(x + off, y)
                    if rng.random() < 0.5:
                        mb.cyl(0.3, 0.8, (q.x, q.y, zz + 0.52), F.r(), "Metal_Brass" if k % 2 else "Stone_Light", 8,
                               bevel=0.0)
                    else:
                        crystal_cluster(mb, (q.x, q.y, zz + 0.12), 0.22, "Crystal_Blue", rng, 2)
            for k in (-1, 1):
                q = F.p(x, y + k * (L_ / 2 - 0.1)) if rot else F.p(x + k * (L_ / 2 - 0.1), y)
                mb.box((0.25, 0.25, 4.2), (q.x, q.y, zf + 2.1), F.r(), "Wood_Dark", 0.0)
        elif kind == "crate":
            # bau de mineiro com cintas de ferro (mais barato que o caixote modular e le melhor dentro de casa)
            _, x, y = it
            a = rng.uniform(-0.25, 0.25)
            q = F.p(x, y)
            mb.box((2.2, 1.4, 1.2), (q.x, q.y, zf + 0.6), F.r(0, 0, a), "Wood_Plank", 0.08)
            mb.box((2.35, 1.55, 0.4), (q.x, q.y, zf + 1.35), F.r(0, 0, a), "Wood_Dark", 0.08)
            Fc = Frame(q.x, q.y, 0.0, F.a + a)
            for sx in (-0.65, 0.65):
                mb.box((0.22, 1.62, 1.6), Fc.p(sx, 0, zf + 0.82), Fc.r(), "Metal_Dark", 0.0)
            mb.box((0.4, 0.2, 0.45), Fc.p(0, -0.8, zf + 1.05), Fc.r(), "Metal_Brass", 0.0)
            col_box(A, (2.4, 1.6, 2.0), (q.x, q.y, F0 + 1.0), F.r(0, 0, a))
        elif kind == "barrel":
            _, x, y = it
            barrel(mb, tuple(F.p(x, y, zf)), r=0.9, h=2.2)
            q = F.p(x, y)
            col_box(A, (2.0, 2.0, 2.4), (q.x, q.y, F0 + 1.2), F.r())
        elif kind == "rug":
            _, x, y = it
            mb.box((4.2, 3.0, 0.08), F.p(x, y, zf + 0.04), F.r(0, 0, rng.uniform(-0.08, 0.08)), "Cloth_Red", 0.0)
            mb.box((3.4, 2.2, 0.1), F.p(x, y, zf + 0.06), F.r(0, 0, rng.uniform(-0.08, 0.08)), "Cloth_Canvas", 0.0)
        elif kind == "loft":
            # jirau de tabuas no fundo do sobrado + escada de mao
            _, x, y_back = it
            zl = F0 + 8.2
            Fl = Frame(F.p(0, y_back - 1.8).x, F.p(0, y_back - 1.8).y, 0.0, F.a)
            plank_floor(mb, Fl, w - 2.8, 3.6, zl, rng)
            mb.box((w - 2.8, 0.5, 0.7), F.p(0, y_back - 3.7, zl - 0.35), F.r(), "Wood_Dark", 0.06)
            yl = y_back - 4.1
            zm = (zl + F0) / 2 + 0.2
            for sx in (-1, 1):
                mb.box((0.25, 0.25, zl - F0 - 0.5), F.p(x + sx * 0.8, yl, zm), F.r(-0.12, 0, 0), "Wood_Light", 0.0)
            for k in range(6):
                zz = F0 + 1.3 + k * 1.2
                mb.box((1.6, 0.2, 0.2), F.p(x, yl + (zz - zm) * 0.12, zz), F.r(), "Wood_Light", 0.0)
            for k, sx in enumerate((-2.8, -1.7)):
                mb.ico(0.85, F.p(sx, y_back - 1.5 + k * 0.4, zl + 0.95), "Cloth_Canvas", 1, (1.0, 0.8, 1.0),
                       jitter=0.15)
            barrel(mb, tuple(F.p(-0.4, y_back - 1.4, zl + 0.3)), r=0.7, h=1.8)


def cabin(name, rng):
    spec = CABINS[name]
    cx, cy, ang = spec["pos"]
    w, d = spec["w"], spec["d"]
    V = dict(spec["V"])
    V.setdefault("apron", True)     # pedras de passo + area livre de vegetacao diante da porta
    F = Frame(cx, cy, 0.0, D(ang))
    A = "Cabin"
    mb = K.AMB("BLD_Cabin_" + name, "07_BUILDINGS", rng)
    info = house(mb, F, w, d, F0, rng, V, area=A, name=name)
    t = V.get("t", 1.4)
    # piso e mobilia
    plank_floor(mb, F, w - 2 * t, d - 2 * t, F0 + 0.3, rng)
    cabin_interior(mb, F, w, d, rng, spec["inner"], A, name)
    # emblema da picareta sobre a porta
    ds0, ds1, dh, darch = V["door"]
    Fe0 = info["EF"][0][0]
    emblem_pickaxe(mb, Fe0.p((ds0 + ds1) / 2, -0.3, F0 + dh + (1.5 if not darch else 1.3)), F.a, s=0.42)
    if V.get("lantern") == "hang":
        P = V["porch"]
        hanging_lantern(mb, tuple(Fe0.p(P["s1"] - 1.6, -P["depth"] + 0.9, F0 + P["z_lo"] - 0.2)), name="L_Cabin_" + name,
                        chain=0.6)
    else:
        lantern(mb, tuple(F.p(w / 2 - 1.0, -d / 2 - 2.2, F0)), F.a - math.pi / 2, name="L_Cabin_" + name, h=5.5)
        q = F.p(w / 2 - 1.0, -d / 2 - 2.2)
        col_box(A, (1.4, 1.4, 7.0), (q.x, q.y, F0 + 3.5), F.r())
    light("L_Cabin_In_" + name, "POINT", tuple(F.p(0, 1.0, F0 + 6.5)), 90, (1.0, 0.6, 0.3), 0.5)
    mb.finish()
    marker("DOOR_Cabin_" + name, tuple(F.p(0, -d / 2, F0)), F.r(0, 0, -math.pi / 2), 1.5)


# ------------------------------------------------------------------ estacao de carga sobre o trilho + galpao leste
def open_truss(mb, F, y, hw, z0, z_r, rng, m="Wood_Dark"):
    """tesoura aberta (linha + pendural + escoras) no plano local y - oitao de telheiro sem parede"""
    K.lbox(mb, F, (0.6, 0.6, z_r - z0 - 0.4), 0, y, (z0 + z_r - 0.4) / 2, m, 0.06)
    for sx in (-1, 1):
        K.lbeam(mb, F, (sx * hw * 0.62, y, z0 + 0.3), (sx * 0.3, y, z0 + (z_r - z0) * 0.55), 0.45, 0.45, m, 0.05)


def weigh_station(rng):
    """telheiro aberto sobre o trilho (balanca de vagonetes, caixas, lanterna) - nao cria expectativa de porta"""
    import fm_mine
    pts = fm_mine.rail_path(fm_mine.tunnel_frame())
    fine = resample(pts, 1.0)
    # ponto do trilho na praca oeste
    idx = min(range(len(fine)), key=lambda k: (fine[k] - Vector((-54, -8, F0))).length)
    p = fine[idx]
    tdir = (fine[idx + 1] - fine[idx - 1]).normalized()
    a = math.atan2(tdir.y, tdir.x)
    F = Frame(p.x, p.y, 0, a)
    mb = K.AMB("BLD_Rail_Weigh_Station", "07_BUILDINGS", rng)
    for sx in (-5.0, 5.0):
        for sy in (-5.5, 5.5):
            q = F.p(sx, sy)
            lean = rng.uniform(-0.025, 0.025)
            mb.box((1.0, 1.0, 9.6), (q.x, q.y, F0 + 5.4), F.r(lean, rng.uniform(-0.02, 0.02), 0), "Wood_Dark", 0.12)
            mb.box((1.9, 1.9, 1.0), (q.x, q.y, F0 + 0.45), F.r(rng.uniform(-0.04, 0.04), 0, rng.uniform(-0.3, 0.3)),
                   "Stone_Dark", 0.18)
            mb.box((1.3, 1.3, 0.5), (q.x, q.y, F0 + 1.1), F.r(0, 0, rng.uniform(-0.2, 0.2)), "Stone_Light", 0.12)
            col_box("Station", (1.2, 1.2, 10.0), (q.x, q.y, F0 + 5.0), F.r())
            # maos-francesas nos dois sentidos
            K.lbeam(mb, F, (sx, sy, F0 + 7.6), (sx * 0.62, sy, F0 + 9.8), 0.45, 0.5, "Wood_Dark", 0.05)
            K.lbeam(mb, F, (sx, sy, F0 + 7.8), (sx, sy * 0.66, F0 + 9.8), 0.45, 0.5, "Wood_Dark", 0.05)
    for sy in (-5.5, 5.5):
        mb.beam(F.p(-6.2, sy, F0 + 10.2), F.p(6.2, sy, F0 + 10.2 + rng.uniform(-0.08, 0.08)), 0.95, 1.05, "Wood_Dark",
                0.08)
    for sx in (-5.0, 5.0):
        mb.beam(F.p(sx, -6.4, F0 + 10.2), F.p(sx, 6.4, F0 + 10.2), 0.9, 1.0, "Wood_Dark", 0.08)
    # telhado de 2 aguas (cumeeira ao longo do trilho) em ripas de madeira, com tesouras abertas nas pontas
    Fr = K.sub(F, 0, 0, D(-90))
    z_r = F0 + 14.0
    K.gable_roof(mb, Fr, 0.0, -5.6, 5.6, z_r, rng, sides=((6.0, F0 + 10.8, 1.3), (6.0, F0 + 10.8, 1.3)),
                 ends=((1.1, 0.0), (1.4, 0.0)), m="Roof_Shingle_Wood", m2="Roof_Shingle_Moss", alt=0.14, sag=0.3,
                 tile=(1.6, 2.6), course=1.45, rafters=2.0)
    for yy in (-5.0, 5.0):
        open_truss(mb, Fr, yy, 6.0, F0 + 10.7, z_r, rng)
    # balanca (plataforma de ferro sob o trilho) e mostrador
    q = F.p(0, 0)
    mb.box((6.0, 4.6, 0.25), (q.x, q.y, F0 + 0.02), F.r(), "Metal_Iron", 0.03)
    for sx in (-1, 1):
        mb.box((6.2, 0.35, 0.3), F.p(0, sx * 2.35, F0 + 0.15), F.r(), "Metal_Dark", 0.02)
    q2 = F.p(0, 4.4)
    mb.box((1.2, 1.2, 4.6), (q2.x, q2.y, F0 + 2.3), F.r(), "Wood_Dark", 0.1)
    mb.cyl(1.2, 0.4, (q2.x, q2.y, F0 + 5.2), F.r(D(90), 0, 0), "Metal_Brass", 16, bevel=0.05)
    mb.cyl(0.9, 0.45, F.p(0, 4.2, F0 + 5.2), F.r(D(90), 0, 0), "Emblem_Cream", 16, bevel=0.0)
    mb.beam(F.p(0, 4.0, F0 + 5.2), F.p(0.55, 4.0, F0 + 5.8), 0.12, 0.12, "Metal_Dark", 0.0)
    col_box("Station", (1.4, 1.4, 5.0), (q2.x, q2.y, F0 + 2.5), F.r())
    for i, (sx, sy) in enumerate(((3.5, -4.2), (-3.5, -4.4), (-3.0, 4.6))):
        crate(mb, tuple(F.p(sx, sy, F0)), 2.2, a + rng.uniform(-0.3, 0.3), rng)
        q3 = F.p(sx, sy)
        col_box("Station", (2.4, 2.4, 2.4), (q3.x, q3.y, F0 + 1.2), F.r())
    crystal_cluster(mb, tuple(F.p(3.5, -4.2, F0 + 2.2)), 0.45, "Crystal_Blue", rng, 4)
    hanging_lantern(mb, tuple(F.p(0, 0, F0 + 10.0)), name="L_Station", chain=1.5)
    mb.finish()
    marker("RAIL_Weigh_Station", (p.x, p.y, F0), F.r(), 2)


def crystal_shed(rng):
    """galpao aberto (tres lados) na margem leste: estoque de cristais refinados aguardando a forja"""
    F = Frame(112.0, -34.0, 0, D(180))
    mb = K.AMB("BLD_Crystal_Shed", "07_BUILDINGS", rng)
    w, d = 16.0, 10.0
    t = 1.2
    walls = ((F.p(-w / 2, d / 2), F.p(w / 2, d / 2)), (F.p(w / 2, -d / 2), F.p(w / 2, d / 2)),
             (F.p(-w / 2, -d / 2), F.p(-w / 2, d / 2)))
    for (a, b) in walls:
        timber_wall(mb, a, b, F0 + 1.0, F0 + 8.0, t, rng, post=3.4, m_p="Wood_Plank", wobble=0.05, brace_bevel=0.0)
        masonry_wall(mb, a, b, F0 - 0.2, F0 + 1.0, t + 0.3, rng, course=1.2, mix=0.35)
        dv = b - a
        cc = (a + b) / 2
        col_box("Shed", (dv.length, t, 8.0), (cc.x, cc.y, F0 + 4.0), (0, 0, math.atan2(dv.y, dv.x)))
    zf_, zb_ = F0 + 11.0, F0 + 8.4
    for sx in (-w / 2, w / 2):
        q = F.p(sx, -d / 2)
        mb.box((1.1, 1.1, 10.4), (q.x, q.y, F0 + 5.2), F.r(), "Wood_Dark", 0.1)
        mb.box((1.8, 1.8, 0.9), (q.x, q.y, F0 + 0.4), F.r(0, 0, rng.uniform(-0.3, 0.3)), "Stone_Dark", 0.16)
        # mao-francesa para a viga da frente (vao de 16)
        K.lbeam(mb, F, (sx, -d / 2, F0 + 6.8), (sx * 0.7, -d / 2, F0 + 9.8), 0.5, 0.55, "Wood_Dark", 0.05)
        # empena lateral de tabuas fechando o vao entre a parede (z 8) e a agua inclinada
        K.vprism(mb, F, [(d / 2, F0 + 7.9), (-d / 2, F0 + 7.9), (-d / 2, zf_ - 0.45), (d / 2, zb_ - 0.35)],
                 sx - 0.3, sx + 0.3, "Wood_Plank", "x")
    mb.beam(F.p(-w / 2 - 0.6, -d / 2, F0 + 10.0), F.p(w / 2 + 0.6, -d / 2, F0 + 10.15), 0.95, 1.05, "Wood_Dark", 0.08)
    # agua unica: alta na frente aberta, baixa no fundo - telhas de ardosia + testeiras e guarda-ventos
    g = (zf_ - zb_) / d
    E0, E1 = F.p(w / 2 + 0.9, d / 2 + 1.0, zb_ - g * 1.0), F.p(-w / 2 - 0.9, d / 2 + 1.0, zb_ - g * 1.0)
    R0, R1 = F.p(w / 2 + 0.9, -d / 2 - 1.2, zf_ + g * 1.2), F.p(-w / 2 - 0.9, -d / 2 - 1.2, zf_ + g * 1.2)
    P, N, Lr = K.roof_plane(mb, E0, E1, R0, R1, rng, "Roof", "Roof_Slate_Blue", 0.2, 0.42, 0.3, 1.5, (1.8, 2.8),
                            0.13, 0.3)
    for u in (0.0, 1.0):
        pts = [P(Lr * f / 3, u) for f in range(4)]
        for pa, pb in zip(pts, pts[1:]):
            dd = (pb - pa).normalized()
            mb.beam(pa - dd * 0.1 - N * 0.1 + N * (0.5 if u else 0.0), pb + dd * 0.1 - N * 0.1 + N * (0.5 if u else 0.0),
                    0.45, 0.8, "Wood_Dark", 0.06)
    for s in (0.0, Lr):
        mb.beam(P(s, 0.0) + N * 0.25, P(s, 1.0) + N * 0.25, 0.5, 1.1, "Wood_Dark", 0.08)
    # vigas do telhado (visiveis de dentro)
    for k in range(4):
        x = -w / 2 + 2.0 + k * 4.0
        K.lbeam(mb, F, (x, d / 2, zb_ - 0.4), (x, -d / 2, zf_ - 0.5), 0.5, 0.6, "Wood_Dark", 0.05)
    # estoque de cristais
    for k in range(4):
        q = F.p(-w / 2 + 2.5 + k * 3.7, d / 2 - 2.2, 0)
        mb.box((3.0, 2.8, 2.2), (q.x, q.y, F0 + 1.1), F.r(0, 0, rng.uniform(-0.06, 0.06)), "Wood_Plank", 0.1)
        mb.box((3.2, 0.35, 0.4), (q.x, q.y, F0 + 1.9), F.r(0, 0, 0), "Wood_Dark", 0.03)
        crystal_cluster(mb, (q.x, q.y, F0 + 2.2), 0.6, "Crystal_Blue" if k % 2 else "Crystal_Purple", rng, 5)
        col_box("Shed", (3.0, 2.8, 3.4), (q.x, q.y, F0 + 1.7), F.r())
    mine_cart(mb, tuple(F.p(-3.0, -1.0, F0)), F.a, "Crystal_Blue", rng)
    q = F.p(-3.0, -1.0)
    col_box("Shed", (3.6, 2.6, 3.4), (q.x, q.y, F0 + 1.7), F.r())
    # placa com cristal pendurada na viga da frente (acento frio)
    for sx in (-1.1, 1.1):
        mb.rod(F.p(sx, -d / 2, F0 + 8.0), F.p(sx, -d / 2, F0 + 6.9), 0.07, "Metal_Dark", 4)
    mb.box((3.2, 0.35, 1.5), F.p(0, -d / 2, F0 + 6.2), F.r(), "Wood_Plank", 0.08)
    crystal_cluster(mb, tuple(F.p(0, -d / 2 - 0.25, F0 + 5.7)), 0.3, "Crystal_Blue", rng, 3)
    hanging_lantern(mb, tuple(F.p(0, 0, F0 + 9.3)), name="L_Shed", chain=1.5)
    mb.finish()


def build():
    rng = random.Random(909)
    plaza_and_paths(rng)
    shop(rng)
    # cabanas: oeste (entre trilho e penhasco) e leste (margem) - cada uma com variante propria
    for name in ("West_A", "West_B", "West_C", "East_A", "East_B"):
        cabin(name, rng)
    weigh_station(rng)
    crystal_shed(rng)
