# il_props - props de ambientacao da Ilha 1 (dono: integracao). Poucos e com funcao; nada de barril aleatorio.
#   - lanternas de rua da vila (poste de madeira + lanterna de papel vermelha): guiam do topo da escadaria ao salao,
#     a loja de armas, o ramen e o inicio da ponte de saida (a luz de cada uma e noturna: il_lights)
#   - campo de treino ninja no gramado sudoeste (postes de treino, alvo, suporte de kunais, banco): o "treinamento"
#   - poco comunitario no T1 oeste, bancos na praca do T2, caixas/barris SO junto as casas e ao moinho
# Cada peca e testada contra a geometria real dos outros modulos e contra as 14 rotas (como a vegetacao).
import math, random
from mathutils import Vector
import il_lib as IL
from il_lib import MB, col_box
import il_layout as L
import fm_portal_kit as PK
import fm_props_kit as PR
import il_veg as V

C = "09_PROPS"
# lanternas de rua (x, y) - o z vem do chao
STREET_LAMPS = [(-9.0, 112.0), (9.0, 112.0), (-14.0, 134.0), (14.0, 134.0), (-30.0, 140.0), (30.0, 140.0),
                (-44.0, 118.0), (44.0, 118.0), (-72.0, 100.0), (72.0, 100.0), (86.0, 90.0), (-100.0, 12.0),
                (-40.0, 146.0), (-74.0, 144.0)]
STREET_LAMPS[11] = (-98.0, 30.0)     # fora da faixa de chegada da escada do summon (y 8..22)
LAMP_SPOTS = []            # preenchido no build: (nome, x, y, z_da_lanterna) -> il_lights


def street_lamp(mb, x, y, z, yaw, rng):
    """poste de madeira com braco e lanterna de papel vermelha (chochin), estilo Konoha"""
    mb.box((1.0, 1.0, 0.6), (x, y, z + 0.3), (0, 0, yaw), "Wood_Dark", 0.0)   # (pedra pequena sumia no fold)
    mb.box((0.55, 0.55, 8.4), (x, y, z + 4.5), (0, 0, yaw), "Wood_Dark", 0.05)
    ax, ay = math.cos(yaw) * 1.5, math.sin(yaw) * 1.5
    mb.beam((x, y, z + 8.3), (x + ax, y + ay, z + 8.3), 0.35, 0.35, "Wood_Dark", 0.03)
    mb.box((1.3, 1.3, 0.25), (x, y, z + 8.85), (0, 0, yaw + math.pi / 4), "Roof_Terracotta", 0.0)
    c = PK.chochin(mb, (x + ax, y + ay, z + 8.1), r=0.75, h=1.5, paper="Lantern_Glow", cap="Wood_Dark",
                   band="Cloth_Red", hang=0.5)
    return c


def training_yard(mb, cx, cy, z, rng):
    """campo de treino ninja (o icone do Naruto): piso de terra batida 14 x 10 com cerca baixa, 3 postes de treino de
    tronco com amarras e um suporte de kunais. Sem alvos redondos (liam como enfeite solto)."""
    mb.box((15.0, 11.0, 0.3), (cx, cy + 1.0, z + 0.12), (0, 0, 0), "Dirt_Pit", 0.0)
    for (ax, ay), (bx, by) in (((-7.5, -4.5), (7.5, -4.5)), ((-7.5, 6.5), (7.5, 6.5)), ((-7.5, -4.5), (-7.5, 0.0)),
                               ((7.5, -4.5), (7.5, 0.0)), ((-7.5, 3.0), (-7.5, 6.5)), ((7.5, 3.0), (7.5, 6.5))):
        mb.beam((cx + ax, cy + ay, z + 1.0), (cx + bx, cy + by, z + 1.0), 0.3, 0.3, "Wood_Plank", 0.0)
        for (px, py) in ((ax, ay), (bx, by)):
            mb.box((0.45, 0.45, 1.3), (cx + px, cy + py, z + 0.65), (0, 0, 0), "Wood_Dark", 0.0)
    for k, (dx, dy) in enumerate(((-6.0, 3.0), (0.0, 5.0), (6.0, 3.0))):
        x, y = cx + dx, cy + dy
        mb.cyl(0.75, 5.4, (x, y, z + 2.7), (0, 0, 0), "Wood_Plank", 8, bevel=0.0)
        for hz in (1.6, 3.3):
            mb.cyl(0.82, 0.45, (x, y, z + hz), (0, 0, 0), "Rope", 8, bevel=0.0)
        mb.box((2.6, 0.35, 0.35), (x, y, z + 4.2), (0, 0, rng.uniform(-0.2, 0.2)), "Wood_Dark", 0.03)
        col_box("PropTraining", (1.6, 1.6, 5.4), (x, y, z + 2.7))
    # suporte de kunais e banco
    rx, ry = cx + 9.5, cy - 2.0
    mb.box((0.4, 3.2, 3.0), (rx, ry, z + 1.5), (0, 0, 0), "Wood_Dark", 0.03)
    for k in range(4):
        yy = ry - 1.1 + k * 0.75
        mb.beam((rx - 0.5, yy, z + 2.4), (rx + 0.5, yy, z + 1.4), 0.12, 0.3, "Metal_Iron", 0.0)
    col_box("PropTraining", (1.2, 3.4, 3.0), (rx, ry, z + 1.5))
    col_box("PropTraining", (15.0, 0.6, 1.8), (cx, cy - 4.5, z + 0.9))
    col_box("PropTraining", (15.0, 0.6, 1.8), (cx, cy + 6.5, z + 0.9))


def build():
    rng = random.Random(4401)
    gb = V._ground()
    ob = V._obstacles()
    LAMP_SPOTS.clear()
    lm = MB("PROP_Street_Lamps", C, rng, detail="near")
    n_l = 0
    for i, (x, y) in enumerate(STREET_LAMPS):
        z = V._ground_z(gb, x, y)
        if z is None or V._near_route(x, y, 2.6):
            continue
        if ob is not None and ob.find_nearest(Vector((x, y, z + 4.0)), 1.4)[0] is not None:
            continue
        yaw = math.atan2(-y, -x) if math.hypot(x, y) > 1 else 0.0
        c = street_lamp(lm, x, y, z, yaw, rng)
        col_box("PropLamp", (1.0, 1.0, 8.6), (x, y, z + 4.3))
        LAMP_SPOTS.append(("L_Lantern_Rua_%02d" % i, c.x, c.y, c.z))
        n_l += 1
    lm.finish()
    # campo de treino (gramado sudoeste)
    ty = MB("PROP_Training_Yard", C, rng, detail="near")
    cx, cy = -58.0, -70.0
    z = V._ground_z(gb, cx, cy) or L.G
    training_yard(ty, cx, cy, z, rng)
    ty.finish()
    # poco comunitario (T1 oeste) e bancos da praca do T2
    mi = MB("PROP_Village_Misc", C, rng, detail="near")
    wx, wy = -92.0, 118.0
    zw = V._ground_z(gb, wx, wy)
    if zw is not None and not V._near_route(wx, wy, 4.0) and (ob is None or ob.find_nearest(Vector((wx, wy, zw + 2.0)), 3.2)[0] is None):
        PR.well(mi, (wx, wy, zw), 0.3, rng)
        col_box("PropWell", (5.0, 5.0, 5.0), (wx, wy, zw + 2.5))
    for sx in (-1, 1):
        bx, by = sx * 20.0, 131.0
        zb = V._ground_z(gb, bx, by)
        if zb is None or V._near_route(bx, by, 2.5):
            continue
        PR.bench_log(mi, Vector((bx, by, zb)), 0.0, 3.6)
        col_box("PropBench", (3.8, 1.2, 1.4), (bx, by, zb + 0.7))
    # caixas e barris SO junto a casas e ao moinho (poucos)
    spots = [(L.MILL[0] - 4.0, L.MILL[1] + L.MILL[3] / 2 + 3.0), (L.MILL[0] + 4.0, L.MILL[1] - L.MILL[3] / 2 - 3.0),
             (L.RAMEN[0] + L.RAMEN[2] / 2 + 2.5, L.RAMEN[1] + 2.0)]
    for hx, hy, w, d, yaw, roof in L.HOUSES_T1 + L.HOUSES_T2:
        spots.append((hx + w / 2 + 2.2, hy - d / 4))
    for k, (x, y) in enumerate(spots):
        z = V._ground_z(gb, x, y)
        if z is None or V._near_route(x, y, 3.0):
            continue
        if ob is not None and ob.find_nearest(Vector((x, y, z + 1.2)), 1.2)[0] is not None:
            continue
        if k % 2:
            PR.crate(mi, (x, y, z), 1.8, rng.uniform(0, 1), rng=rng)
        else:
            PR.keg(mi, (x, y, z), 0.9, 2.1)
        col_box("PropCrate", (2.0, 2.0, 2.2), (x, y, z + 1.1))
    mi.finish()
    print("PROPS lanternas=%d treino=1 poco/bancos/caixas ok" % n_l)
