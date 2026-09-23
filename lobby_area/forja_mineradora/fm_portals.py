# fm_portals - seis portais no terraco (facil -> dificil, esquerda -> direita). Mesma familia (pad no terraco,
# espiral r7.5 voltada para -Y, degraus de acesso), arquitetura propria para cada destino.
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, col_ramp, marker, light, SWIRL_R, bezier
from fm_parts import (Frame, stairs, lantern, hanging_lantern, banner, crate, barrel, crystal_cluster, sakura, palm,
                      pave_poly, stone_parapet, fence, frustum, P3, arch)
import fm_layout as L

C = "06_PORTALS"
T = L.TERR
PY = L.PORTAL_Y     # plano da espiral
SZ = T + 2.0 + 9.2  # centro da espiral (sobre plataforma de 2 degraus)


def swirl(key, px, mat_name, z=None, r=SWIRL_R):
    mb = MB("PORTAL_%s_Swirl" % key, C)
    mb.cyl(r, 0.3, (0, 0, 0), (D(90), 0, 0), mat_name, 40, bevel=0.0)
    ob = mb.finish()
    ob.location = (px, PY, SZ if z is None else z)
    marker("PORTAL_" + key, (px, PY - 0.6, SZ if z is None else z), (0, 0, 0), 4, "CIRCLE",
           props={"destino": key, "raio": r, "touch": True})
    col = {"Naruto": (1.0, 0.35, 0.55), "DragonBall": (1.0, 0.8, 0.3), "ShadowGarden": (0.62, 0.25, 1.0),
           "DemonSlayer": (1.0, 0.25, 0.25), "OnePiece": (0.2, 0.5, 1.0), "OnePunchMan": (0.35, 0.8, 1.0)}[key]
    light("L_Portal_" + key, "POINT", (px, PY - 3.0, SZ if z is None else z), 1600, col, 3.0)
    return ob


def plinth(mb, px, shape, m_top, m_side, rng, w=22.0, d=10.0):
    """plataforma de 2 degraus (z T -> T+2) diante/sob a espiral"""
    cy = PY
    if shape == "rect":
        for k in range(2):
            ww, dd = w - k * 3.0, d - k * 2.6
            mb.box((ww, dd, 1.0), (px, cy, T + 0.5 + k), (0, 0, 0), m_side if k == 0 else m_top, 0.18)
    elif shape == "round":
        for k in range(2):
            mb.cyl(w / 2 - k * 1.6, 1.0, (px, cy, T + 0.5 + k), (0, 0, 0), m_side if k == 0 else m_top, 28, bevel=0.3)
    elif shape == "oct":
        for k in range(2):
            mb.cyl(w / 2 - k * 1.6, 1.0, (px, cy, T + 0.5 + k), (0, 0, D(22.5)), m_side if k == 0 else m_top, 8, bevel=0.2)
    A = "Portal"
    col_box(A, (w, d, 1.0), (px, cy, T + 0.5))
    col_box(A, (w - 3.0, d - 2.6, 2.0), (px, cy, T + 1.0))


def pad(mb, px, rng, m="Stone_Paving"):
    """calcada do pad (do topo da escada ate a espiral)"""
    pave_poly(mb, [(px - 12, L.FLIGHT2_Y1 + 0.2), (px + 12, L.FLIGHT2_Y1 + 0.2), (px + 12, PY + 8),
                   (px - 12, PY + 8)], T - 0.3, rng, tile=2.6, h=0.35, grout=True)


def banners_pair(mb, px, cloth, trim, emblem="pickaxe", dx=13.5, h=7.0):
    for s in (-1, 1):
        x = px + s * dx
        mb.box((0.9, 0.9, h + 5.0), (x, PY - 3.0, T + (h + 5.0) / 2), (0, 0, 0), "Wood_Dark", 0.1)
        mb.box((0.6, 3.6, 0.5), (x, PY - 4.6, T + h + 4.4), (0, 0, 0), "Wood_Dark", 0.05)
        banner(mb, (x, PY - 5.2, T + h + 3.9), 0.0, w=3.0, h=h - 1.2, cloth=cloth, trim=trim, emblem=emblem)
        col_box("Portal", (1.0, 1.0, h + 5.0), (x, PY - 3.0, T + (h + 5.0) / 2))


# ------------------------------------------------------------------ 1 NARUTO / KONOHA (torii + lanternas de pedra)
def naruto(rng):
    px = L.PORTAL_X[0]
    mb = MB("PORTAL_Naruto_Torii", C, rng)
    pad(mb, px, rng)
    plinth(mb, px, "rect", "Stone_Light", "Stone_Dark", rng, w=24.0, d=12.0)
    # a plataforma continua atras (passagem para o canion de Konoha)
    red, blk = "P_Naruto_Red", "Wood_Dark"
    for s in (-1, 1):
        x = px + s * 9.6
        mb.cyl(1.9, 1.4, (x, PY, T + 2.7), (0, 0, 0), "Stone_Dark", 10, bevel=0.2)
        mb.cyl(1.25, 22.0, (x, PY, T + 13.4), (0, 0, 0), red, 12, r2=1.1, bevel=0.1)
        mb.cyl(1.45, 1.2, (x, PY, T + 3.9), (0, 0, 0), blk, 12, bevel=0.1)
    # nuki (viga de baixo) e kasagi curvo com pontas levantadas
    mb.box((24.0, 1.4, 1.5), (px, PY, T + 19.5), (0, 0, 0), red, 0.15)
    pts = [Vector((px + x, PY, T + 24.2 + 0.018 * x * x)) for x in range(-15, 16, 2)]
    mb.sweep(pts, [(-1.4, -1.2), (1.4, -1.2), (1.6, 1.0), (-1.6, 1.0)], blk, True, up=(0, 0, 1))
    pts2 = [p + Vector((0, 0, -2.0)) for p in pts[1:-1]]
    mb.sweep(pts2, [(-1.1, -0.9), (1.1, -0.9), (1.1, 0.9), (-1.1, 0.9)], red, True, up=(0, 0, 1))
    # gakuzuka (placa central) com espiral-folha
    mb.box((3.2, 1.8, 3.6), (px, PY - 0.2, T + 21.6), (0, 0, 0), blk, 0.15)
    mb.box((2.6, 0.4, 2.9), (px, PY - 1.1, T + 21.6), (0, 0, 0), "Metal_Brass", 0.05)
    spiral = [Vector((px + math.cos(t) * 0.12 * t, PY - 1.4, T + 21.6 + math.sin(t) * 0.12 * t)) for t in
              [i * 0.5 for i in range(0, 22)]]
    mb.tube(spiral, 0.14, "P_Naruto_Red", 6)
    # lanternas de papel penduradas no nuki
    for s in (-1, 1):
        x = px + s * 5.0
        mb.rod((x, PY, T + 18.8), (x, PY, T + 17.4), 0.08, "Metal_Dark", 4)
        mb.cyl(0.9, 1.9, (x, PY, T + 16.3), (0, 0, 0), "Lantern_Glow", 10, bevel=0.0)
        mb.cyl(0.95, 0.3, (x, PY, T + 17.3), (0, 0, 0), red, 10, bevel=0.0)
        mb.cyl(0.95, 0.3, (x, PY, T + 15.3), (0, 0, 0), red, 10, bevel=0.0)
    # lanternas de pedra (toro) no pad
    for s in (-1, 1):
        x = px + s * 11.0
        y = L.FLIGHT2_Y1 + 3.5
        mb.box((2.4, 2.4, 0.8), (x, y, T + 0.4), (0, 0, 0), "Stone_Light", 0.15)
        mb.cyl(0.5, 3.0, (x, y, T + 2.3), (0, 0, 0), "Stone_Light", 6, bevel=0.05)
        mb.box((2.0, 2.0, 1.8), (x, y, T + 4.6), (0, 0, 0), "Stone_Light", 0.12)
        mb.box((1.4, 2.1, 1.1), (x, y, T + 4.6), (0, 0, 0), "Lantern_Glow", 0.0)
        mb.cyl(2.2, 1.2, (x, y, T + 6.1), (0, 0, D(45)), "Stone_Dark", 4, r2=0.3, bevel=0.1)
        col_box("Portal", (2.4, 2.4, 6.5), (x, y, T + 3.25))
        light("L_Naruto_Toro_%d" % (s + 1), "POINT", (x, y - 1.2, T + 4.6), 150, (1.0, 0.6, 0.3), 0.3)
    # nobori (bandeiras verticais) e sakura moderada
    for s in (-1, 1):
        x = px + s * 16.0
        mb.box((0.5, 0.5, 13.0), (x, PY - 1.0, T + 6.5), (0, 0, 0), "Wood_Dark", 0.05)
        mb.box((0.3, 2.2, 8.0), (x + s * 0.4, PY - 2.1, T + 8.2), (0, 0, 0), "Cloth_Navy" if s < 0 else red, 0.02)
        col_box("Portal", (0.6, 0.6, 13.0), (x, PY - 1.0, T + 6.5))
    sakura(mb, (px - 19.0, PY + 4.0, T), 13.0, rng)
    sakura(mb, (px + 20.0, PY + 7.0, T), 11.0, rng)
    mb.finish()
    for s in (-1, 1):
        col_box("Portal", (2.6, 2.6, 24.0), (px + s * 9.6, PY, T + 12.0))
    swirl("Naruto", px, "P_Naruto_Swirl")


# ------------------------------------------------------------------ 2 DRAGON BALL (anel dourado + dragao + esferas)
def dragonball(rng):
    px = L.PORTAL_X[1]
    mb = MB("PORTAL_DragonBall_Ring", C, rng)
    pad(mb, px, rng, "Stone_Paving")
    plinth(mb, px, "round", "P_DB_White", "P_DB_Orange", rng, w=22.0)
    # anel dourado (moldura redonda) e base em capsula branca
    R = SWIRL_R + 1.4
    ring = [Vector((px + math.cos(D(a)) * R, PY, SZ + math.sin(D(a)) * R)) for a in range(0, 361, 10)]
    mb.sweep(ring, [(-1.6, -1.1), (1.6, -1.1), (1.6, 1.1), (-1.6, 1.1)], "P_DB_Gold", True, up=(0, 1, 0))
    ring2 = [Vector((px + math.cos(D(a)) * (R + 1.5), PY, SZ + math.sin(D(a)) * (R + 1.5))) for a in range(0, 361, 10)]
    mb.sweep(ring2, [(-0.8, -0.5), (0.8, -0.5), (0.8, 0.5), (-0.8, 0.5)], "P_DB_White", True, up=(0, 1, 0))
    for s in (-1, 1):
        mb.box((5.0, 5.0, 4.5), (px + s * (R + 1.0), PY, T + 4.2), (0, 0, 0), "P_DB_White", 1.2, 2)
        mb.cyl(1.6, 5.2, (px + s * (R + 1.0), PY - 2.6, T + 4.2), (D(90), 0, 0), "P_DB_Orange", 16, bevel=0.3)
    # dragao dourado enrolado no anel (helice toroidal) com cabeca no topo
    path = []
    for i in range(0, 121):
        t = i / 120
        a = D(-80 + 330 * t)
        rr = R + 2.8 + 1.2 * math.sin(t * math.tau * 3)
        yy = PY + 2.6 * math.cos(t * math.tau * 3)
        path.append(Vector((px + math.cos(a) * rr, yy, SZ + math.sin(a) * rr)))
    n = len(path)
    for i in range(n - 1):
        r = 1.35 * (0.35 + 0.65 * min(1.0, i / 20.0))
        mb.rod(path[i], path[i + 1], r, "P_DB_Gold", 8)
        if i % 6 == 0:
            mb.ico(r * 0.7, path[i] + Vector((0, 0, r * 0.7)), "P_DB_Orange", 1, (1, 1, 0.6))
    head = path[-1]
    hd = (path[-1] - path[-4]).normalized()
    mb.box((3.6, 2.6, 2.4), head + hd * 1.8, (0, 0, math.atan2(hd.y, hd.x)), "P_DB_Gold", 0.5, 2)
    for s in (-1, 1):
        mb.cyl(0.35, 3.0, head + Vector((0, s * 0.9, 2.2)), (s * 0.4, -0.5, 0), "P_DB_White", 6, r2=0.05, bevel=0.0)
        mb.ico(0.35, head + hd * 2.4 + Vector((0, s * 0.9, 0.8)), "P_Gold_Glow", 1)
    # sete esferas em pedestais em volta da plataforma
    for k, deg in enumerate((196, 213, 230, 247, 293, 310, 327)):   # frente (270) livre para entrar
        a = D(deg)
        x = px + math.cos(a) * 13.0
        y = PY + 1.0 + math.sin(a) * 8.0
        mb.cyl(0.9, 2.6, (x, y, T + 1.3), (0, 0, 0), "P_DB_White", 10, bevel=0.15)
        mb.ico(1.0, (x, y, T + 3.6), "P_DB_Orange", 2)
        col_box("Portal", (1.8, 1.8, 3.6), (x, y, T + 1.8))
    mb.finish()
    for s in (-1, 1):
        col_box("Portal", (5.0, 5.0, 25.0), (px + s * (R + 1.0), PY, T + 12.5))
    col_box("Portal", (2 * R + 6, 4, 3), (px, PY, SZ + R + 1.5))
    swirl("DragonBall", px, "P_DB_Swirl")


# ------------------------------------------------------------------ 3 SHADOW GARDEN (arco gotico + lua + correntes)
def shadow(rng):
    px = L.PORTAL_X[2]
    mb = MB("PORTAL_ShadowGarden_Gothic", C, rng)
    pad(mb, px, rng, "Stone_Dark")
    plinth(mb, px, "oct", "P_Shadow_Stone", "Stone_Dark", rng, w=24.0)
    st = "P_Shadow_Stone"
    # arco ogival: pilares + dois arcos de circulo que se encontram em ponta
    hw = SWIRL_R + 1.8
    for s in (-1, 1):
        x = px + s * (hw + 1.2)
        mb.box((3.2, 3.6, 14.0), (x, PY, T + 9.0), (0, 0, 0), st, 0.25)
        for k in range(4):
            mb.box((3.8, 4.2, 0.7), (x, PY, T + 3.0 + k * 4.0), (0, 0, 0), "Stone_Dark", 0.1)
        # pinaculo
        mb.box((3.6, 4.0, 1.2), (x, PY, T + 16.4), (0, 0, 0), "Stone_Dark", 0.1)
        frustum(mb, (x, PY, T + 17.0), 3.2, 3.6, 0.3, 0.3, 11.0, st)
        for k in (-1, 1):
            frustum(mb, (x + k * 2.4, PY, T + 13.0), 1.2, 1.2, 0.1, 0.1, 5.0, st)
    rr = hw * 1.55
    for side in (-1, 1):
        cx = px - side * (rr - hw)
        a0 = 0.0 if side > 0 else math.pi
        a_top = math.acos((rr - hw) / rr)
        arcp = []
        for i in range(13):
            t = i / 12
            ang = (a0 + a_top * t) if side > 0 else (a0 - a_top * t)
            arcp.append(Vector((cx + math.cos(ang) * rr, PY, SZ - 1.0 + math.sin(ang) * rr)))
        mb.sweep(arcp, [(-1.5, -1.2), (1.5, -1.2), (1.5, 1.2), (-1.5, 1.2)], st, True, up=(0, 1, 0))
    tip_z = SZ - 1.0 + rr * math.sin(math.acos((rr - hw) / rr))
    # lua crescente no topo (roxo emissivo) + espinho central
    moon = []
    for i in range(15):
        a = D(40 + i * 20)
        moon.append(Vector((px + math.cos(a) * 2.4, PY - 1.4, tip_z + 3.8 + math.sin(a) * 2.4)))
    mb.sweep(moon, [(-0.5, -0.4), (0.5, -0.4), (0.5, 0.4), (-0.5, 0.4)], "P_Shadow_Glow", True, up=(0, 1, 0))
    frustum(mb, (px, PY, tip_z - 0.5), 1.6, 1.6, 0.1, 0.1, 9.0, st)
    # correntes pendentes dos pinaculos ate o arco
    from fm_forge import chain
    for s in (-1, 1):
        chain(mb, (px + s * (hw + 1.2), PY - 2.0, T + 15.5), (px + s * 3.0, PY - 1.6, tip_z - 3.0), sag=2.5)
        chain(mb, (px + s * (hw + 1.2), PY - 2.0, T + 9.0), (px + s * 13.5, PY - 5.0, T + 5.0), sag=1.5)
    # cristais roxos e grade de ferro com pontas
    for s in (-1, 1):
        crystal_cluster(mb, (px + s * 12.5, PY - 1.0, T), 1.2, "Crystal_Purple", rng, 6)
        for k in range(7):
            x = px + s * (6.0 + k * 0.9)
            mb.box((0.25, 0.25, 3.4), (x, L.FLIGHT2_Y1 + 1.0, T + 1.7), (0, 0, 0), "Metal_Dark", 0.0)
            frustum(mb, (x, L.FLIGHT2_Y1 + 1.0, T + 3.4), 0.4, 0.4, 0.05, 0.05, 0.9, "Metal_Dark")
        mb.box((5.8, 0.25, 0.3), (px + s * 8.7, L.FLIGHT2_Y1 + 1.0, T + 2.8), (0, 0, 0), "Metal_Dark", 0.0)
        col_box("Portal", (5.8, 0.6, 4.0), (px + s * 8.7, L.FLIGHT2_Y1 + 1.0, T + 2.0))
    # candelabros roxos
    for s in (-1, 1):
        x = px + s * 13.5
        mb.cyl(0.4, 6.0, (x, PY - 5.0, T + 3.0), (0, 0, 0), "Metal_Dark", 6, bevel=0.0)
        mb.cyl(1.2, 0.5, (x, PY - 5.0, T + 6.2), (0, 0, 0), "Metal_Dark", 8, bevel=0.0)
        mb.ico(0.7, (x, PY - 5.0, T + 7.0), "P_Shadow_Glow", 1, (1, 1, 1.6))
        col_box("Portal", (1.0, 1.0, 7.0), (x, PY - 5.0, T + 3.5))
    mb.finish()
    for s in (-1, 1):
        col_box("Portal", (3.4, 3.8, 28.0), (px + s * (hw + 1.2), PY, T + 14.0))
    swirl("ShadowGarden", px, "P_Shadow_Swirl")


# ------------------------------------------------------------------ 4 DEMON SLAYER (portico-santuario + mascara oni + laminas)
def demonslayer(rng):
    px = L.PORTAL_X[3]
    mb = MB("PORTAL_DemonSlayer_Shrine", C, rng)
    pad(mb, px, rng, "Stone_Paving")
    plinth(mb, px, "rect", "Stone_Dark", "P_DS_Black", rng, w=24.0, d=11.0)
    blk, red = "P_DS_Black", "P_DS_Red"
    hw = SWIRL_R + 1.6
    for s in (-1, 1):
        x = px + s * (hw + 0.9)
        mb.box((2.4, 2.4, 20.0), (x, PY, T + 12.0), (0, 0, 0), blk, 0.15)
        for zz in (T + 4.0, T + 17.0):
            mb.box((2.8, 2.8, 1.0), (x, PY, zz), (0, 0, 0), red, 0.1)
        mb.box((3.4, 3.4, 1.4), (x, PY, T + 2.7), (0, 0, 0), "Stone_Dark", 0.15)
    # verga dupla + telhado de telhas curvo
    mb.box((2 * hw + 6.0, 2.0, 1.6), (px, PY, T + 21.8), (0, 0, 0), blk, 0.15)
    mb.box((2 * hw + 3.0, 1.5, 1.1), (px, PY, T + 19.2), (0, 0, 0), red, 0.12)
    roof_pts = [Vector((px + x, PY, T + 23.4 + 0.02 * x * x)) for x in range(-14, 15, 2)]
    mb.sweep(roof_pts, [(-3.4, 0.0), (3.4, 0.0), (1.2, 2.6), (-1.2, 2.6)], "Roof", True, up=(0, 0, 1))
    mb.sweep([p + Vector((0, 0, 2.6)) for p in roof_pts[2:-2]], [(-1.3, 0), (1.3, 0), (1.3, 0.9), (-1.3, 0.9)], blk, True)
    # mascara oni no centro do telhado (chifres, olhos brilhando)
    mz = T + 27.2
    mb.box((5.2, 1.8, 4.6), (px, PY - 2.4, mz), (0, 0, 0), red, 0.8, 2)
    mb.box((5.6, 1.2, 1.2), (px, PY - 3.0, mz + 1.2), (0, 0, 0), blk, 0.3)
    for s in (-1, 1):
        mb.box((1.1, 0.5, 0.6), (px + s * 1.3, PY - 3.4, mz + 0.4), (0, 0, s * 0.2), "Forge_Emissive", 0.1)
        horn = [Vector((px + s * 2.0, PY - 2.4, mz + 2.0)), Vector((px + s * 3.4, PY - 2.4, mz + 4.2)),
                Vector((px + s * 3.2, PY - 2.0, mz + 6.2))]
        for a_, b_, r in zip(horn, horn[1:], (0.8, 0.5)):
            mb.rod(a_, b_, r, "Emblem_Cream", 6)
    for k in range(5):
        mb.box((0.5, 0.4, 0.9), (px - 1.6 + k * 0.8, PY - 3.4, mz - 1.6), (0, 0, 0), "Emblem_Cream", 0.05)
    # katanas cruzadas diante do telhado (elementos de lamina)
    for s in (-1, 1):
        a = Vector((px - s * 7.5, PY - 3.6, T + 17.0))
        b = Vector((px + s * 7.0, PY - 3.6, T + 27.0))
        d = (b - a).normalized()
        mb.beam(a, a + d * 3.2, 0.6, 0.6, blk, 0.05)
        mb.beam(a + d * 3.2, a + d * 3.6, 1.6, 0.9, "Metal_Brass", 0.05)
        mb.beam(a + d * 3.6, b, 0.25, 0.9, "Metal_Iron", 0.0)
    # corda sagrada (shimenawa) com shide e braseiros vermelhos
    rope = [Vector((px + x, PY - 1.4, T + 17.8 - 1.2 * math.cos(x / hw * math.pi / 2))) for x in
            [(-hw + 2 * hw * i / 10) for i in range(11)]]
    mb.tube(rope, 0.55, "Rope", 8)
    for p in rope[1:-1:2]:
        mb.box((0.7, 0.1, 1.8), p + Vector((0, -0.3, -1.3)), (0, 0, 0), "Emblem_Cream", 0.0)
    for s in (-1, 1):
        x = px + s * 13.5
        mb.cyl(1.2, 3.4, (x, PY - 4.0, T + 1.7), (0, 0, 0), "Stone_Dark", 8, r2=0.8, bevel=0.1)
        mb.cyl(1.6, 0.9, (x, PY - 4.0, T + 3.8), (0, 0, 0), "Metal_Dark", 8, r2=1.9, bevel=0.0)
        for k in range(4):
            mb.cyl(0.5, 2.2, (x + rng.uniform(-0.6, 0.6), PY - 4.0 + rng.uniform(-0.6, 0.6), T + 5.2), (0, 0, 0),
                   "P_Red_Glow", 5, r2=0.05, bevel=0.0)
        col_box("Portal", (2.6, 2.6, 4.4), (x, PY - 4.0, T + 2.2))
        light("L_DS_Brazier_%d" % (s + 1), "POINT", (x, PY - 4.0, T + 6.0), 300, (1.0, 0.3, 0.2), 0.6)
    # glicinias (wisteria) roxas pendendo da verga
    for k in range(9):
        x = px - hw + 1.0 + k * (2 * hw - 2.0) / 8
        for j in range(3):
            mb.ico(0.55 - j * 0.12, (x + rng.uniform(-0.3, 0.3), PY + 1.4, T + 19.8 - j * 0.9), "Leaf_Sakura", 1,
                   (1, 1, 1.4))
    mb.finish()
    for s in (-1, 1):
        col_box("Portal", (2.6, 2.6, 22.0), (px + s * (hw + 0.9), PY, T + 11.0))
    swirl("DemonSlayer", px, "P_DS_Swirl")


# ------------------------------------------------------------------ 5 ONE PIECE (timao, cais, ancora, tesouro)
def onepiece(rng):
    px = L.PORTAL_X[4]
    mb = MB("PORTAL_OnePiece_Helm", C, rng)
    # deque de madeira (cais) em vez de pedra
    for i in range(12):
        y = L.FLIGHT2_Y1 + 0.6 + i * 1.9
        mb.box((24.0, 1.8, 0.4), (px + rng.uniform(-0.2, 0.2), y, T + 0.05), (0, 0, rng.uniform(-0.01, 0.01)),
               "Wood_Plank", 0.06)
    plinth(mb, px, "round", "Wood_Plank", "Wood_Dark", rng, w=21.0)
    # timao gigante: aro duplo, raios, puxadores (a espiral fica no miolo)
    R = SWIRL_R + 1.2
    for rr, w in ((R, 1.3), (R + 2.2, 0.8)):
        ring = [Vector((px + math.cos(D(a)) * rr, PY, SZ + math.sin(D(a)) * rr)) for a in range(0, 361, 10)]
        mb.sweep(ring, [(-w, -0.9), (w, -0.9), (w, 0.9), (-w, 0.9)], "Wood_Light" if w > 1 else "Wood_Dark", True,
                 up=(0, 1, 0))
    ringg = [Vector((px + math.cos(D(a)) * (R + 1.1), PY - 0.95, SZ + math.sin(D(a)) * (R + 1.1))) for a in range(0, 361, 10)]
    mb.sweep(ringg, [(-0.35, -0.1), (0.35, -0.1), (0.35, 0.1), (-0.35, 0.1)], "P_DB_Gold", True, up=(0, 1, 0))
    for k in range(8):
        a = D(k * 45 + 22.5)
        p0 = Vector((px + math.cos(a) * (R + 1.0), PY, SZ + math.sin(a) * (R + 1.0)))
        p1 = Vector((px + math.cos(a) * (R + 6.2), PY, SZ + math.sin(a) * (R + 6.2)))
        if p1.z < T + 3.0:
            continue
        mb.rod(p0, p1, 0.55, "Wood_Light", 8)
        mb.ico(0.95, p1, "Wood_Light", 1, (1, 1, 1.3))
    # base: dois cascos/pilares de madeira com cordas
    for s in (-1, 1):
        x = px + s * (R + 1.2)
        mb.box((3.0, 3.6, 6.5), (x, PY, T + 5.0), (0, 0, 0), "Wood_Dark", 0.3)
        for zz in (T + 3.0, T + 6.5):
            mb.cyl(1.9, 0.6, (x, PY, zz), (0, 0, 0), "Rope", 10, bevel=0.0)
    # ancora encostada, bau de tesouro, barris, bandeira pirata (caveira generica)
    ax = px + 13.0
    mb.box((0.9, 0.9, 9.0), (ax, PY - 4.0, T + 4.6), (0, D(12), 0), "Metal_Dark", 0.1)
    mb.box((4.4, 0.9, 0.9), (ax - 0.8, PY - 4.0, T + 7.8), (0, D(12), 0), "Metal_Dark", 0.1)
    arcp = [Vector((ax + 1.0 + math.cos(D(a)) * 3.0, PY - 4.0, T + 3.4 + math.sin(D(a)) * 3.0 * 0.8)) for a in range(190, 351, 16)]
    mb.tube(arcp, 0.55, "Metal_Dark", 8)
    col_box("Portal", (4.0, 2.0, 9.0), (ax, PY - 4.0, T + 4.5))
    cx_ = px - 12.5
    mb.box((3.6, 2.4, 2.0), (cx_, PY - 5.0, T + 1.0), (0, 0, 0.2), "Wood_Plank", 0.15)
    mb.cyl(1.2, 3.6, (cx_, PY - 5.0, T + 2.0), (0, D(90), 0.2), "Wood_Plank", 10, bevel=0.05)
    for k in range(5):
        mb.cyl(0.35, 0.18, (cx_ + rng.uniform(-1.5, 1.5), PY - 6.8 + rng.uniform(-0.6, 0.6), T + 0.1), (0, 0, 0),
               "P_DB_Gold", 8, bevel=0.0)
    col_box("Portal", (3.8, 2.6, 3.4), (cx_, PY - 5.0, T + 1.7))
    for p in ((px - 14.5, PY - 1.0), (px - 15.2, PY + 1.6), (px + 15.0, PY + 1.0)):
        barrel(mb, (p[0], p[1], T), 1.1, 2.6)
    # mastro com bandeira (azul) e vela
    mx = px + 15.5
    mb.cyl(0.55, 18.0, (mx, PY + 3.0, T + 9.0), (0, 0, 0), "Wood_Dark", 8, bevel=0.0)
    mb.box((0.2, 5.0, 3.4), (mx + 0.3, PY + 3.0 - 2.6, T + 16.0), (0, 0, 0), "Cloth_Navy", 0.02)
    mb.ico(0.6, (mx + 0.45, PY + 0.4, T + 16.3), "Emblem_Cream", 1, (0.4, 1, 1))
    mb.box((0.2, 7.0, 6.0), (mx + 0.2, PY + 3.0, T + 9.0), (0, 0, 0), "Cloth_Canvas", 0.02)
    col_box("Portal", (1.2, 1.2, 18.0), (mx, PY + 3.0, T + 9.0))
    palm(mb, (px - 18.0, PY + 5.0, T), 13.0, rng)
    palm(mb, (px + 19.0, PY + 7.0, T), 11.0, rng)
    # cordas amarradas entre postes do cais
    for s in (-1, 1):
        x = px + s * 11.5
        for y in (L.FLIGHT2_Y1 + 1.0, L.FLIGHT2_Y1 + 7.0):
            mb.cyl(0.55, 2.6, (x, y, T + 1.3), (0, 0, 0), "Wood_Dark", 8, bevel=0.1)
            col_box("Portal", (1.2, 1.2, 2.6), (x, y, T + 1.3))
        mb.tube([Vector((x, L.FLIGHT2_Y1 + 1.0, T + 2.2)), Vector((x, L.FLIGHT2_Y1 + 4.0, T + 1.6)),
                 Vector((x, L.FLIGHT2_Y1 + 7.0, T + 2.2))], 0.2, "Rope", 6)
    mb.finish()
    for s in (-1, 1):
        col_box("Portal", (3.0, 3.6, 7.0), (px + s * (R + 1.2), PY, T + 5.0))
    col_box("Portal", (2 * R + 16, 2.5, 4.0), (px, PY, SZ + R + 3.5))
    swirl("OnePiece", px, "P_OP_Swirl")


# ------------------------------------------------------------------ 6 ONE PUNCH MAN (torres hero-tech + neon)
def opm(rng):
    px = L.PORTAL_X[5]
    mb = MB("PORTAL_OnePunchMan_City", C, rng)
    pad(mb, px, rng, "P_OPM_Concrete")
    plinth(mb, px, "rect", "P_OPM_Concrete", "Stone_Dark", rng, w=24.0, d=11.0)
    con, gl, neon = "P_OPM_Concrete", "P_OPM_Glass", "P_OPM_Neon"
    hw = SWIRL_R + 1.4
    # moldura: portal retangular chanfrado com filete neon
    for s in (-1, 1):
        x = px + s * (hw + 1.4)
        mb.box((2.8, 3.0, 20.0), (x, PY, T + 12.0), (0, 0, 0), con, 0.3)
        mb.box((0.4, 3.2, 18.0), (x - s * 1.4, PY, T + 12.0), (0, 0, 0), neon, 0.0)
    mb.box((2 * hw + 5.6, 3.0, 2.8), (px, PY, T + 23.4), (0, 0, 0), con, 0.3)
    mb.box((2 * hw + 2.0, 3.2, 0.4), (px, PY, T + 21.8), (0, 0, 0), neon, 0.0)
    ring = [Vector((px + math.cos(D(a)) * (SWIRL_R + 0.5), PY - 0.3, SZ + math.sin(D(a)) * (SWIRL_R + 0.5))) for a in range(0, 361, 10)]
    mb.sweep(ring, [(-0.35, -0.3), (0.35, -0.3), (0.35, 0.3), (-0.35, 0.3)], neon, True, up=(0, 1, 0))
    # emblema no topo: punho estilizado em caixa
    ez = T + 27.2
    mb.box((5.0, 1.6, 4.4), (px, PY - 0.4, ez), (0, 0, 0), con, 0.4)
    mb.box((3.2, 0.5, 2.2), (px, PY - 1.4, ez + 0.2), (0, 0, 0), "Emblem_Cream", 0.3)
    for k in range(4):
        mb.box((0.7, 0.6, 0.9), (px - 1.1 + k * 0.73, PY - 1.7, ez + 1.2), (0, 0, 0), "Emblem_Cream", 0.15)
    mb.box((0.9, 0.6, 1.4), (px + 1.8, PY - 1.7, ez - 0.3), (0, 0, D(-20)), "Emblem_Cream", 0.15)
    mb.box((4.4, 0.3, 0.3), (px, PY - 1.3, ez - 1.9), (0, 0, 0), neon, 0.0)
    # torres (arranha-ceus) atras e aos lados, com faixas de janelas
    towers = [(-14.0, 8.0, 34.0, 6.0), (-19.0, 3.0, 24.0, 5.0), (15.0, 7.0, 38.0, 6.5), (20.0, 2.0, 22.0, 5.0),
              (-8.0, 12.0, 28.0, 5.0), (9.0, 13.0, 30.0, 5.0)]
    for (dx, dy, h, w) in towers:
        x, y = px + dx, PY + dy
        mb.box((w, w, h), (x, y, T + h / 2), (0, 0, 0), con, 0.3)
        for k in range(int(h / 3.2) - 1):
            z = T + 3.0 + k * 3.2
            mb.box((w + 0.2, w + 0.2, 1.0), (x, y, z), (0, 0, 0), gl, 0.0)
        mb.box((w * 0.6, w * 0.6, 3.0), (x, y, T + h + 1.5), (0, 0, 0), con, 0.2)
        mb.cyl(0.18, 5.0, (x, y, T + h + 5.0), (0, 0, 0), "Metal_Iron", 6, bevel=0.0)
        mb.ico(0.4, (x, y, T + h + 7.6), neon, 1)
        col_box("Portal", (w, w, h), (x, y, T + h / 2))
    # luzes de piso e totens com holograma
    for s in (-1, 1):
        x = px + s * 13.0
        mb.box((1.6, 1.6, 5.0), (x, PY - 5.0, T + 2.5), (0, 0, 0), con, 0.2)
        mb.box((1.7, 1.7, 0.4), (x, PY - 5.0, T + 4.2), (0, 0, 0), neon, 0.0)
        col_box("Portal", (1.6, 1.6, 5.0), (x, PY - 5.0, T + 2.5))
    for k in range(6):
        y = L.FLIGHT2_Y1 + 1.5 + k * 2.4
        for s in (-1, 1):
            mb.box((0.6, 1.2, 0.12), (px + s * 10.5, y, T + 0.08), (0, 0, 0), neon, 0.0)
    mb.finish()
    for s in (-1, 1):
        col_box("Portal", (3.0, 3.2, 24.0), (px + s * (hw + 1.4), PY, T + 12.0))
    swirl("OnePunchMan", px, "P_OPM_Swirl")


def build():
    rng = random.Random(707)
    naruto(rng)
    dragonball(rng)
    shadow(rng)
    demonslayer(rng)
    onepiece(rng)
    opm(rng)
    # placas de dificuldade (1..6) no pe de cada escada (sem texto: pips luminosos)
    mb = MB("PORTAL_Difficulty_Markers", C, rng)
    for i, px in enumerate(L.PORTAL_X):
        x, y = px + 7.8, L.FLIGHT1_Y0 - 1.5
        mb.box((1.0, 1.0, 6.0), (x, y, L.FLOOR + 3.0), (0, 0, 0), "Wood_Dark", 0.1)
        mb.box((3.6, 0.6, 2.2), (x, y - 0.3, L.FLOOR + 5.4), (0, 0, 0), "Wood_Plank", 0.1)
        for k in range(i + 1):
            mb.ico(0.28, (x - 1.25 + k * 0.5, y - 0.7, L.FLOOR + 5.4), "Forge_Emissive", 1)
        col_box("Portal", (1.2, 1.2, 6.0), (x, y, L.FLOOR + 3.0))
    mb.finish()
