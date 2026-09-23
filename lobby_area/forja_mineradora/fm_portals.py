# fm_portals - seis portais no terraco (facil -> dificil, esquerda -> direita). Mesma familia (pad no terraco,
# espiral r7.5 voltada para -Y, degraus de acesso), mas cada um e uma PECA ARQUITETONICA propria:
#   Naruto  = torii + muro de vila com telhadinho + shimenawa + toro de pedra (continua atras, para Konoha)
#   DB      = dais-capsula com energia + aro heroico + barbatanas curvas + aneis orbitais com as 7 esferas + dragao
#   Shadow  = gotico ASSIMETRICO: agulha alta, arcobotante, crochets, correntes, medalhao da lua, dais octogonal
#   DS      = portico carbonizado inclinado, telhado de beirais cortantes, leque de laminas, oni, xadrez verde
#   OP      = cais de madeira sobre estacas (cordas, defensas), timao, caveira, ancora, mastro com vela
#   OPM     = torres altas escalonadas (skyline), praca de concreto zebrada, punho no medalhao amarelo
# O terraco deixa de ser galeria reta: cada plataforma avanca/recua e tem altura e forma proprias, e os vaos
# entre portais recebem rochas, muretas e vegetacao tematica (fm_portal_terrace).
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, SWIRL_R, bezier
from fm_parts import crystal_cluster, sakura, palm, frustum, barrel, crate
import fm_portal_kit as K
from fm_portal_kit import V
import fm_layout as L

C = "06_PORTALS"
T = L.TERR
PY = L.PORTAL_Y     # plano da espiral
SZ = T + 2.0 + 9.2  # centro da espiral
Y0 = L.FLIGHT2_Y1   # topo do lance 2 (inicio do pad)
A = "Portal"


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


def col_disc(cx, cy, r, z0, z1):
    """colisao de um disco/octogono: quadrado inscrito + cruz"""
    h = z1 - z0
    zc = (z0 + z1) / 2
    col_box(A, (r * 1.414, r * 1.414, h), (cx, cy, zc))
    col_box(A, (r * 1.84, r * 0.76, h), (cx, cy, zc))
    col_box(A, (r * 0.76, r * 1.84, h), (cx, cy, zc))


def blade_roof(mb, cx, cy, z0, half, depth, rise, tip_rise, thick, m, n=16, finial=None):
    """telhado de beirais cortantes: secao em V invertido, pontas que sobem e afinam como laminas"""
    pts, profs = [], []
    for i in range(n + 1):
        x = -half + 2 * half * i / n
        f = abs(x) / half
        pts.append(V(cx + x, cy, z0 + tip_rise * f ** 3))
        w = depth * (1 - 0.72 * f ** 4)
        r_ = rise * (1 - 0.55 * f ** 2)
        profs.append([(0.0, w / 2), (r_, 0.0), (0.0, -w / 2), (-thick, -w / 2 + 0.35), (r_ - thick, 0.0),
                      (-thick, w / 2 - 0.35)])
    K.loft(mb, pts, profs, m, True, up=(0, 0, 1))
    if finial:
        for s in (-1, 1):
            tip = V(cx + s * half, cy, z0 + tip_rise)
            K.cone(mb, tip - V(s * 0.6, 0, 0.3), tip + V(s * 2.0, 0, 1.7), 0.55, 0.0, finial, 4)


def flame(w, h):
    return [(-w / 2, 0.0), (-w * 0.28, h * 0.42), (-w * 0.46, h * 0.72), (-w * 0.08, h * 0.58), (0.0, h),
            (w * 0.16, h * 0.55), (w * 0.44, h * 0.8), (w * 0.3, h * 0.36), (w / 2, 0.0)]


# ================================================================== 1 NARUTO / KONOHA
def naruto(rng):
    px = L.PORTAL_X[0]

    def X(dx):
        return px + dx
    mb = MB("PORTAL_Naruto_Torii", C, rng)
    red, blk = "P_Naruto_Red", "Wood_Dark"
    pc = PY - 1.0   # plataforma avancada 1 stud
    # sando (lajes claras no eixo) + canteiros de cascalho rastelado com meio-fio
    K.flag_floor(mb, [(X(-5.6), Y0 + 0.2), (X(5.6), Y0 + 0.2), (X(5.6), pc - 5.0), (X(-5.6), pc - 5.0)], T - 0.3, rng,
                 "Stone_Light", "Stone_Paving", tile=3.0, h=0.4, bevel=0.1)
    for s in (-1, 1):
        xa, xb = X(s * 5.9), X(s * 12.6)
        mb.box2((xa, Y0 + 0.3, T - 0.3), (xb, pc - 5.4, T + 0.12), "P_Gravel", 0.04)
        for k in range(4):
            xx = X(s * (7.2 + k * 1.35))
            mb.box((0.16, pc - 5.9 - Y0, 0.07), (xx, (Y0 + pc - 5.4) / 2 + 0.1, T + 0.14), (0, 0, 0), "Stone_Light", 0.0)
        mb.box2((xa - s * 0.25, Y0 + 0.3, T - 0.2), (xa + s * 0.25, pc - 5.4, T + 0.42), "Stone_Dark", 0.06)
        mb.box2((xa, Y0 + 0.1, T - 0.2), (xb, Y0 + 0.6, T + 0.42), "Stone_Dark", 0.06)

    # plataforma chanfrada em 2 niveis
    def chamf(hx, y0, y1, c):
        return [(X(-hx + c), y0), (X(hx - c), y0), (X(hx), y0 + c), (X(hx), y1 - c), (X(hx - c), y1),
                (X(-hx + c), y1), (X(-hx), y1 - c), (X(-hx), y0 + c)]
    mb.prism(chamf(12.2, pc - 5.9, pc + 6.4, 1.3), T - 0.6, T + 0.9, "Stone_Dark", 0.15)
    mb.prism(chamf(10.8, pc - 4.6, pc + 5.1, 1.0), T + 0.9, T + 1.8, "Stone_Light", 0.15)
    col_box2(A, (X(-12.2), pc - 5.9, T - 1), (X(12.2), pc + 6.4, T + 0.9))
    col_box2(A, (X(-10.8), pc - 4.6, T - 1), (X(10.8), pc + 5.1, T + 1.8))

    # torii
    zb = T + 1.8
    for s in (-1, 1):
        x = X(s * 9.6)
        mb.cyl(1.95, 1.2, (x, PY, zb + 0.6), (0, 0, 0), "Stone_Dark", 10, bevel=0.15)
        mb.cyl(1.25, 22.0, (x, PY, zb + 11.0), (0, 0, 0), red, 12, r2=1.1, bevel=0.1)
        mb.cyl(1.45, 1.1, (x, PY, zb + 1.75), (0, 0, 0), blk, 12, bevel=0.08)
        mb.cyl(1.5, 0.8, (x, PY, T + 22.7), (0, 0, 0), blk, 12, bevel=0.05)
        # amarras da corda no pilar
        mb.cyl(1.36, 0.6, (x, PY, T + 18.2), (0, 0, 0), "Rope", 12, bevel=0.0)
    mb.box((24.6, 1.4, 1.5), (px, PY, T + 19.5), (0, 0, 0), red, 0.15)
    for s in (-1, 1):
        mb.box((0.5, 1.9, 1.9), (X(s * 7.9), PY, T + 19.5), (0, 0, 0), blk, 0.05)   # cunhas (kusabi)
    pts = [V(px + x, PY, T + 24.2 + 0.018 * x * x) for x in range(-15, 16, 2)]
    mb.sweep(pts, [(-1.4, -1.2), (1.4, -1.2), (1.6, 1.0), (-1.6, 1.0)], blk, True, up=(0, 0, 1))
    pts2 = [p + V(0, 0, -2.0) for p in pts[1:-1]]
    mb.sweep(pts2, [(-1.1, -0.9), (1.1, -0.9), (1.1, 0.9), (-1.1, 0.9)], red, True, up=(0, 0, 1))
    # gakuzuka (placa) com espiral
    mb.box((3.2, 1.8, 3.6), (px, PY - 0.2, T + 21.6), (0, 0, 0), blk, 0.15)
    mb.box((2.6, 0.4, 2.9), (px, PY - 1.1, T + 21.6), (0, 0, 0), "Metal_Brass", 0.05)
    spiral = [V(px + math.cos(t) * 0.12 * t, PY - 1.4, T + 21.6 + math.sin(t) * 0.12 * t) for t in
              [i * 0.5 for i in range(0, 22)]]
    mb.tube(spiral, 0.14, red, 6)
    # shimenawa (corda torcida grossa) com shide
    def rz(x):
        return T + 18.3 - 1.5 * (1 - (x / 8.3) ** 2)
    rope = [V(X(x), PY - 1.35, rz(x)) for x in [-8.3 + 16.6 * i / 12 for i in range(13)]]
    K.rope_twist(mb, rope, 0.85, "Rope", n=6, strands=2, pitch=2.4)
    for x in (-5.4, -1.8, 1.8, 5.4):
        K.shide(mb, V(X(x), PY - 1.75, rz(x) - 0.55), 1.0)
    # lanternas de papel penduradas nas pontas do kasagi (fora dos pilares)
    for s in (-1, 1):
        x = X(s * 12.9)
        c = K.chochin(mb, (x, PY, T + 26.0), r=1.1, h=2.2, paper="Lantern_Glow", cap=blk, band=red, hang=2.1)
        light("L_P_Naruto_Chochin_%d" % (s + 1), "POINT", tuple(c + V(0, -1.2, 0)), 160, (1.0, 0.6, 0.3), 0.4)

    # muro de vila com telhadinho: a oeste encosta no penhasco; a leste sai do pilar e volta para o fundo,
    # fechando o patio de Konoha (a passagem atras do torii fica livre)
    for s, ln, ret in ((-1, 15.0, False), (1, 17.2, True)):
        a, b, c2 = (X(s * 11.8), PY + 1.0), (X(s * ln), PY + 1.0), (X(s * ln), PY + 10.0)
        K.village_wall(mb, a, b, T, 7.2, rng)
        col_box2(A, (a[0], PY + 0.2, T), (b[0], PY + 1.8, T + 8.6))
        if ret:
            K.village_wall(mb, b, c2, T, 7.2, rng)
            col_box2(A, (b[0] - 0.8, PY + 1.0, T), (b[0] + 0.8, PY + 10.0, T + 8.6))
        # brasao do cla (espiral vermelha sobre disco claro) na face do muro
        ec = V(X(s * (13.5 if s < 0 else 14.6)), PY + 0.2, T + 4.4)
        mb.cyl(1.55, 0.3, ec, (D(90), 0, 0), "Emblem_Cream", 16, bevel=0.0)
        K.ring(mb, ec, 1.72, (1, 0, 0), (0, 0, 1), 0.36, 0.42, red, n=20)
        sp = [ec + V(math.cos(t) * 0.12 * t, -0.2, math.sin(t) * 0.12 * t) for t in [i * 0.55 for i in range(20)]]
        mb.tube(sp, 0.15, red, 5)
    # torre de vigia (yagura) encostada no penhasco oeste, atras do muro
    K.yagura(mb, (X(-13.3), PY + 4.4, T), rng, w=3.6, h=11.0, name="L_P_Naruto_Yagura")
    col_box(A, (4.6, 4.6, 14.0), (X(-13.3), PY + 4.4, T + 7.0))

    # toro de pedra sobre o cascalho
    for s in (-1, 1):
        x, y = X(s * 9.0), Y0 + 3.0
        K.toro(mb, (x, y, T + 0.1), 1.0, "Stone_Light", "Stone_Dark", name="L_P_Naruto_Toro_%d" % (s + 1))
        col_box(A, (2.6, 2.6, 6.6), (x, y, T + 3.3))
    # pedras laterais (musgo): grande junto a plataforma (leste; a oeste o penhasco faz esse papel) e menores
    K.mossy_rock(mb, (X(13.8), PY - 3.8, T), (3.8, 3.2, 3.0), rng)
    col_box(A, (3.6, 3.0, 2.8), (X(13.8), PY - 3.8, T + 1.4))
    K.mossy_rock(mb, (X(-12.4), PY - 6.6, T), (2.6, 2.2, 2.0), rng)
    for s in (-1, 1):
        K.mossy_rock(mb, (X(s * 11.4), Y0 + 1.5, T), (2.2, 1.9, 1.5), rng)
    K.mossy_rock(mb, (X(15.4), PY - 7.0, T), (1.8, 1.6, 1.2), rng, moss=None)
    # nobori (laranja/marinho) diante do muro
    for s in (-1, 1):
        x, y = X(s * (12.9 if s < 0 else 16.6)), PY - (3.4 if s < 0 else 2.4)
        mb.box((0.5, 0.5, 13.0), (x, y, T + 6.5), (0, 0, 0), blk, 0.05)
        mb.box((3.0, 0.35, 0.35), (x - s * 1.3, y, T + 12.4), (0, 0, 0), blk, 0.0)
        mb.box((2.3, 0.22, 8.2), (x - s * 1.35, y, T + 8.1), (0, 0, 0), "P_Naruto_Orange", 0.02)
        mb.box((0.35, 0.26, 8.2), (x - s * 2.35, y, T + 8.1), (0, 0, 0), "Cloth_Navy", 0.0)
        mb.cyl(0.62, 0.3, (x - s * 1.35, y - 0.15, T + 9.6), (D(90), 0, 0), "Cloth_Navy", 10, bevel=0.0)
        col_box(A, (0.7, 0.7, 13.0), (x, y, T + 6.5))
    sakura(mb, (X(19.6), PY + 5.2, T), 12.5, rng)
    col_box(A, (1.6, 1.6, 6.0), (X(19.6), PY + 5.2, T + 3.0))
    mb.finish()
    for s in (-1, 1):
        col_box(A, (2.6, 2.6, 24.0), (X(s * 9.6), PY, T + 12.0))
    swirl("Naruto", px, "P_Naruto_Swirl")


# ================================================================== 2 DRAGON BALL
def dragonball(rng):
    px = L.PORTAL_X[1]

    def X(dx):
        return px + dx
    mb = MB("PORTAL_DragonBall_Ring", C, rng)
    W, O, G, E = "P_DB_White", "P_DB_Orange", "P_DB_Gold", "P_DB_Energy_Glow"
    # dais-capsula em 3 niveis (branco + faixas laranja/azul) com aneis de energia no topo
    ca = (px, Y0 + 0.2 + 11.4)
    cb = (px, PY + 0.4)
    mb.cyl(11.4, 1.1, (ca[0], ca[1], T + 0.05), (0, 0, 0), W, 32, bevel=0.2)
    mb.cyl(11.58, 0.34, (ca[0], ca[1], T + 0.1), (0, 0, 0), O, 32, bevel=0.0)
    mb.cyl(8.3, 0.8, (cb[0], cb[1], T + 1.0), (0, 0, 0), W, 28, bevel=0.15)
    mb.cyl(8.46, 0.24, (cb[0], cb[1], T + 0.95), (0, 0, 0), "P_DB_Blue", 28, bevel=0.0)
    mb.cyl(6.3, 0.8, (cb[0], cb[1], T + 1.8), (0, 0, 0), W, 24, bevel=0.15)
    K.ring(mb, V(cb[0], cb[1], T + 2.24), 4.8, (1, 0, 0), (0, 1, 0), 0.8, 0.1, E, n=28)
    K.ring(mb, V(cb[0], cb[1], T + 2.24), 2.6, (1, 0, 0), (0, 1, 0), 0.5, 0.1, E, n=20)
    K.ring(mb, V(ca[0], ca[1], T + 0.62), 9.9, (1, 0, 0), (0, 1, 0), 0.5, 0.08, O, n=36)
    for k in range(10):
        a = D(k * 36 + 18)
        mb.box((0.5, 0.2, 0.5), (cb[0] + math.cos(a) * 6.32, cb[1] + math.sin(a) * 6.32, T + 1.8), (0, 0, a + D(90)),
               E, 0.0)
    col_disc(ca[0], ca[1], 11.4, T - 1, T + 0.6)
    col_disc(cb[0], cb[1], 8.3, T - 1, T + 1.4)
    col_disc(cb[0], cb[1], 6.3, T - 1, T + 2.2)

    # aro heroico: anel dourado chanfrado + filete laranja + halo branco segmentado com cravos
    R = SWIRL_R + 1.4
    octp = [(-1.6, -0.6), (-1.0, -1.25), (1.0, -1.25), (1.6, -0.6), (1.6, 0.6), (1.0, 1.25), (-1.0, 1.25), (-1.6, 0.6)]
    ringp = [V(px + math.cos(D(a)) * R, PY, SZ + math.sin(D(a)) * R) for a in range(0, 361, 10)]
    mb.sweep(ringp, octp, G, True, up=(0, 1, 0))
    K.ring(mb, V(px, PY, SZ), 10.15, (1, 0, 0), (0, 0, 1), 0.45, 1.9, O, n=40)
    for a0 in (10, 100, 190, 280):
        K.ring(mb, V(px, PY, SZ), 11.25, (1, 0, 0), (0, 0, 1), 1.3, 1.6, W, a0, a0 + 70, n=10)
    for a in (0, 90, 180):
        mb.ico(1.05, (px + math.cos(D(a)) * 11.25, PY, SZ + math.sin(D(a)) * 11.25), G, 2)
    # capsulas-pilone nos lados
    for s in (-1, 1):
        x = X(s * 10.9)
        mb.cyl(2.1, 5.2, (x, PY, T + 0.6 + 2.6), (0, 0, 0), W, 16, bevel=0.2)
        mb.ico(2.1, (x, PY, T + 5.8), W, 2, (1, 1, 0.8))
        mb.cyl(2.2, 0.7, (x, PY, T + 2.4), (0, 0, 0), O, 16, bevel=0.0)
        mb.cyl(2.2, 0.35, (x, PY, T + 4.3), (0, 0, 0), "P_DB_Blue", 16, bevel=0.0)
        col_box(A, (4.2, 4.2, 7.5), (x, PY, T + 3.75))
    # barbatanas curvas (crescentes) saindo das capsulas: silhueta heroica
    for s in (-1, 1):
        n = 10
        outer = bezier((10.0, 6.0), (16.2, 8.6), (16.8, 17.5), (12.4, 23.0), n)
        inner = bezier((10.6, 8.4), (13.2, 11.5), (13.8, 17.2), (12.4, 23.0), n)
        pts = [(p.x, p.y) for p in outer] + [(p.x, p.y) for p in reversed(inner[:-1])]
        K.plate(mb, pts, V(px, PY + 0.4, T), (s, 0, 0), (0, 0, 1), 1.1, W)
        st = [(outer[i].x * 0.7 + inner[i].x * 0.3, outer[i].y * 0.7 + inner[i].y * 0.3) for i in range(1, n)]
        st += [(outer[i].x * 0.35 + inner[i].x * 0.65, outer[i].y * 0.35 + inner[i].y * 0.65) for i in range(n - 1, 0, -1)]
        K.plate(mb, st, V(px, PY - 0.3, T), (s, 0, 0), (0, 0, 1), 0.4, O)
    # aura de energia (chamas) subindo pela base do aro
    for a in (200, 214, 228, 243, 297, 312, 326, 340):
        rad = V(math.cos(D(a)), 0, math.sin(D(a)))
        base = V(px, PY - 1.3, SZ) + rad * (R + 0.6)
        vv = (rad + V(0, 0, 1.6)).normalized()
        uu = V(vv.z, 0, -vv.x)
        h = rng.uniform(2.6, 4.2)
        K.plate(mb, flame(1.9, h), base, uu, vv, 0.3, E)

    # dragao verde (Shenlong) enrolado no halo: sobe pela esquerda, passa pelo alto e ergue a cabeca no topo,
    # de frente para quem chega (boca aberta, chifres de galhada, bigodes longos)
    DG = "P_DB_Dragon"
    body = []
    for i in range(0, 73):
        t = i / 72
        a = D(262 - 166 * t)
        rr = 12.3 + 0.55 * math.sin(t * math.pi * 3)
        yy = PY + 2.4 * math.sin(t * math.pi * 3 + 0.5)
        body.append(V(px + math.cos(a) * rr, yy, SZ + math.sin(a) * rr))
    last = body[-1]
    path = body + [last + V(0.7, -0.6, 1.5), last + V(1.2, -1.4, 2.6), last + V(1.3, -2.2, 3.1)]
    n = len(path)
    radii = [0.32 + 1.2 * min(1.0, (i / (n - 1)) / 0.45) ** 0.8 for i in range(n)]
    K.taper_tube(mb, path, radii, DG, 8, up=(0, 1, 0))
    for i in range(5, n - 4, 4):
        p = path[i]
        out = (p - V(px, p.y, SZ)).normalized()
        K.cone(mb, p + out * radii[i] * 0.6, p + out * (radii[i] + 1.1) + V(0, 0, 0.2), radii[i] * 0.42, 0.0, O, 4)
    # garras: duas patas agarrando o aro
    for i in (18, 48):
        p = path[i]
        inn = (V(px, p.y, SZ) - p).normalized()
        K.taper_tube(mb, [p, p + inn * 1.6 + V(0, -0.6, 0), p + inn * 2.4 + V(0, -1.0, -0.4)], [0.45, 0.32, 0.12], DG, 6)
    H = path[-1]
    hs = 1.4   # escala da cabeca (le de longe)
    fwd = V(0, -1, -0.28).normalized() * hs
    up = (V(0, 0, 1) - V(0, -1, -0.28).normalized() * V(0, -1, -0.28).normalized().z).normalized() * hs
    side = fwd.normalized().cross(up.normalized()) * hs
    mb.beam(H - fwd * 0.6, H + fwd * 2.2, 2.6 * hs, 2.3 * hs, DG, 0.3)                          # cranio
    mb.beam(H + fwd * 1.9 + up * 0.15, H + fwd * 4.9 - up * 0.1, 1.9 * hs, 1.3 * hs, DG, 0.25)  # focinho
    mb.beam(H + fwd * 1.5 - up * 1.2, H + fwd * 4.3 - up * 2.2, 1.6 * hs, 0.5 * hs, DG, 0.1)    # mandibula aberta
    mb.beam(H + fwd * 2.0 - up * 0.55, H + fwd * 4.2 - up * 0.9, 1.3 * hs, 0.4 * hs, "P_OP_Red", 0.0)   # boca
    for s in (-1, 1):
        mb.ico(0.38 * hs, H + fwd * 2.05 + up * 0.8 + side * s * 1.05, "P_Red_Glow", 1)
        mb.beam(H + fwd * 1.4 + up * 1.2 + side * s * 0.6, H + fwd * 2.6 + up * 1.0 + side * s * 1.2, 0.5 * hs,
                0.35 * hs, DG, 0.0)
        K.cone(mb, H + fwd * 4.5 - up * 0.55 + side * s * 0.5, H + fwd * 4.6 - up * 1.4 + side * s * 0.5, 0.2 * hs, 0.0,
               "Emblem_Cream", 4)
        hb = H + up * 1.0 + side * s * 0.75
        k1 = hb - fwd * 1.3 + up * 1.3 + side * s * 0.4
        K.taper_tube(mb, [hb, k1, hb - fwd * 3.0 + up * 2.3 + side * s * 1.0], [0.38 * hs, 0.26 * hs, 0.05],
                     "Emblem_Cream", 6)
        K.taper_tube(mb, [k1, k1 + up * 1.2 + side * s * 0.5 + fwd * 0.2], [0.18 * hs, 0.04], "Emblem_Cream", 5)
        wb = H + fwd * 4.4 + side * s * 0.85
        K.taper_tube(mb, [wb, wb + side * s * 1.4 - fwd * 0.4 + up * 0.5, wb + side * s * 2.6 - fwd * 2.4 - up * 0.4,
                          wb + side * s * 3.4 - fwd * 4.8 - up * 1.9], [0.2, 0.16, 0.12, 0.05], "Emblem_Cream", 5)
    for k in range(5):
        p = H - fwd * (0.5 + k * 0.85) + up * 1.05
        K.cone(mb, p, p + up * (1.2 - k * 0.12) - fwd * 0.7, 0.34 * hs, 0.0, O, 4)

    # orbitas: halo inclinado acima do aro + grande orbita inclinada 25 graus em volta do aro (nunca cruza a
    # espiral de frente); as 7 esferas flutuam nelas
    orbs = []
    tl = D(12)
    orbs.append((V(px, PY + 0.5, T + 30.6), 8.6, V(1, 0, 0), V(0, math.cos(tl), math.sin(tl)), 0, 360))
    tb = D(25)
    orbs.append((V(px, PY, SZ), 14.6, V(1, 0, 0), V(0, math.sin(tb), math.cos(tb)), -24, 204))
    for (cc, Ro, uu, vv, a0, a1) in orbs:
        K.ring(mb, cc, Ro, uu, vv, 0.5, 0.5, "P_DB_Blue", a0, a1, n=56 if a1 - a0 > 300 else 44)
        if a1 - a0 < 360:
            for a in (a0, a1):
                mb.ico(0.75, cc + (uu * math.cos(D(a)) + vv * math.sin(D(a))) * Ro, G, 2)
    balls = [(0, 212), (0, 328), (0, 90), (1, 22), (1, 62), (1, 128), (1, 170)]
    for k, (oi, a) in enumerate(balls):
        cc, Ro, uu, vv, a0, a1 = orbs[oi]
        p = cc + (uu * math.cos(D(a)) + vv * math.sin(D(a))) * Ro
        mb.ico(1.2, p, "P_DB_Ball", 2)
        for j in range(k % 4 + 1):
            ang = D(90 * j + 45 * (k % 2))
            mb.ico(0.2, p + V(math.cos(ang) * 0.42 * (j > 0), -1.12, math.sin(ang) * 0.42 * (j > 0)), "P_DB_Star", 1)
    mb.finish()
    for s in (-1, 1):
        col_box(A, (2.6, 3.0, 17.0), (X(s * 9.6), PY, T + 10.5))
    swirl("DragonBall", px, "P_DB_Swirl")


# ================================================================== 3 SHADOW GARDEN (gotico assimetrico)
def shadow(rng):
    px = L.PORTAL_X[2]

    def X(dx):
        return px + dx
    mb = MB("PORTAL_ShadowGarden_Gothic", C, rng)
    st, tr, dk, gl, ir = "P_Shadow_Stone", "P_Shadow_Trim", "Stone_Dark", "P_Shadow_Glow", "Metal_Dark"
    pc = PY + 1.5   # dais recuado 1.5
    K.flag_floor(mb, [(X(-11.6), Y0 + 0.2), (X(11.6), Y0 + 0.2), (X(11.6), pc - 9.0), (X(-11.6), pc - 9.0)], T - 0.3,
                 rng, st, dk, tile=3.1, h=0.4, bevel=0.1, base_m="Stone_Grout", mix=0.4)
    # dais octogonal elegante em 3 niveis com filetes de luz
    mb.cyl(11.8, 1.3, (px, pc, T - 0.05), (0, 0, D(22.5)), dk, 8, bevel=0.2)
    mb.cyl(10.0, 0.8, (px, pc, T + 1.0), (0, 0, D(22.5)), st, 8, bevel=0.15)
    mb.cyl(8.3, 0.7, (px, pc, T + 1.75), (0, 0, D(22.5)), tr, 8, bevel=0.12)
    mb.cyl(10.18, 0.14, (px, pc, T + 0.64), (0, 0, D(22.5)), gl, 8, bevel=0.0)
    mb.cyl(8.48, 0.14, (px, pc, T + 1.44), (0, 0, D(22.5)), gl, 8, bevel=0.0)
    for k in range(8):
        a = D(k * 45)
        mb.box((0.7, 0.7, 0.1), (px + math.cos(a) * 9.15, pc + math.sin(a) * 9.15, T + 1.42), (0, 0, D(45)), gl, 0.0)
    col_disc(px, pc, 11.8 * 0.97, T - 1, T + 0.6)
    col_disc(px, pc, 10.0 * 0.97, T - 1, T + 1.4)
    col_disc(px, pc, 8.3 * 0.97, T - 1, T + 2.1)

    hw = SWIRL_R + 1.8
    ts = 1    # lado da agulha alta + arcobotante (virado para o centro do terraco, que e aberto)
    # pilares assimetricos: um sobe numa agulha alta, o outro e mais baixo com estandarte
    tops = {}
    for s, ptop in ((ts, 19.0), (-ts, 16.2)):
        x = X(s * (hw + 1.2))
        mb.box((4.4, 4.8, 1.4), (x, PY, T + 1.3), (0, 0, 0), dk, 0.15)
        mb.box((3.4, 3.8, ptop - 2.0), (x, PY, T + 2.0 + (ptop - 2.0) / 2), (0, 0, 0), st, 0.2)
        for k in range(3):
            mb.box((3.8, 4.2, 0.6), (x, PY, T + 5.0 + k * 4.2), (0, 0, 0), tr, 0.08)
        mb.box((4.2, 4.6, 1.0), (x, PY, T + ptop + 0.3), (0, 0, 0), tr, 0.12)
        tops[s] = T + ptop + 0.8
        for sx in (-1, 1):
            for sy in (-1, 1):
                K.cone(mb, V(x + sx * 1.8, PY + sy * 2.0, T + ptop + 0.8), V(x + sx * 2.2, PY + sy * 2.4, T + ptop + 3.0),
                       0.35, 0.0, ir, 4)
    xl = X(ts * (hw + 1.2))
    SP = 27.0
    mb.box((3.6, 4.0, 3.2), (xl, PY, tops[ts] + 1.6), (0, 0, 0), st, 0.15)
    K.plate(mb, [(-1.3, 0), (1.3, 0), (1.3, 1.6), (0, 2.8), (-1.3, 1.6)], V(xl, PY - 2.0, tops[ts] + 0.4),
            (1, 0, 0), (0, 0, 1), 0.3, gl)
    frustum(mb, (xl, PY, tops[ts] + 3.2), 3.4, 3.8, 0.25, 0.25, SP, st)
    for sx in (-1, 1):
        frustum(mb, (xl + sx * 2.2, PY, tops[ts] + 3.2), 1.2, 1.2, 0.1, 0.1, 8.5, st)
        frustum(mb, (xl, PY + sx * 2.3, tops[ts] + 3.2), 1.0, 1.0, 0.1, 0.1, 6.0, st)
    for k in range(7):
        z = tops[ts] + 5.5 + k * 3.3
        f = (z - tops[ts] - 3.2) / SP
        hwz = 1.7 * (1 - f) + 0.12
        for sx in (-1, 1):
            p = V(xl + sx * hwz, PY - 1.0 * (1 - f), z)
            K.cone(mb, p, p + V(sx * 0.9, 0, 0.7), 0.28, 0.0, st, 4)
    xr = X(-ts * (hw + 1.2))
    frustum(mb, (xr, PY, tops[-ts]), 3.2, 3.6, 0.3, 0.3, 11.0, st)
    # arcobotante do lado alto (arco que desce ate um contraforte com pinaculo)
    bx = X(ts * 17.4)
    mb.box((2.4, 2.8, 9.0), (bx, PY + 1.5, T + 4.5), (0, 0, 0), st, 0.15)
    mb.box((3.0, 3.4, 1.0), (bx, PY + 1.5, T + 0.5), (0, 0, 0), dk, 0.1)
    frustum(mb, (bx, PY + 1.5, T + 9.0), 2.2, 2.6, 0.15, 0.15, 5.0, st)
    fb = bezier(V(xl + ts * 1.6, PY + 0.8, T + 17.5), V(xl + ts * 3.8, PY + 1.0, T + 17.6),
                V(bx - ts * 0.4, PY + 1.4, T + 13.5), V(bx, PY + 1.5, T + 9.2), 10)
    mb.sweep(fb, [(-0.7, -0.8), (0.7, -0.8), (0.7, 0.8), (-0.7, 0.8)], st, True, up=(0, 1, 0))
    for p in fb[2:-1:2]:
        K.cone(mb, p + V(0, 0, 0.6), p + V(ts * 0.3, 0, 2.0), 0.3, 0.0, st, 4)
    col_box(A, (2.6, 3.0, 9.0), (bx, PY + 1.5, T + 4.5))

    # arco ogival com crochets (espinhos) no extradorso e tracado de luz por dentro
    rr = hw * 1.55
    a_top = math.acos((rr - hw) / rr)
    tip_z = SZ - 1.0 + rr * math.sin(a_top)
    for side in (-1, 1):
        cx = px - side * (rr - hw)
        a0 = 0.0 if side > 0 else math.pi
        arcp, inner = [], []
        for i in range(13):
            t = i / 12
            ang = (a0 + a_top * t) if side > 0 else (a0 - a_top * t)
            arcp.append(V(cx + math.cos(ang) * rr, PY, SZ - 1.0 + math.sin(ang) * rr))
            inner.append(V(cx + math.cos(ang) * (rr - 2.1), PY - 1.3, SZ - 1.0 + math.sin(ang) * (rr - 2.1)))
        mb.sweep(arcp, [(-1.5, -1.3), (1.5, -1.3), (1.5, 1.3), (-1.5, 1.3)], st, True, up=(0, 1, 0))
        mb.sweep(inner[1:-1], [(-0.22, -0.22), (0.22, -0.22), (0.22, 0.22), (-0.22, 0.22)], gl, True, up=(0, 1, 0))
        for i in range(2, 12, 2):
            p = arcp[i]
            out = V(p.x - cx, 0, p.z - (SZ - 1.0)).normalized()
            K.cone(mb, p + out * 1.3, p + out * 2.8 + V(0, 0, 0.9), 0.42, 0.0, st, 4)
    # medalhao (rosacea) com a lua crescente no apice + espinho
    mc = V(px, PY - 0.2, tip_z + 2.6)
    K.ring(mb, mc, 2.9, (1, 0, 0), (0, 0, 1), 0.8, 1.2, tr, n=24)
    mb.cyl(2.5, 0.5, mc + V(0, 0.2, 0), (D(90), 0, 0), st, 20, bevel=0.0)
    moon = [(math.cos(D(a)) * 1.95, math.sin(D(a)) * 1.95) for a in range(60, 301, 20)]
    moon += [(0.75 + math.cos(D(a)) * 1.5, 0.1 + math.sin(D(a)) * 1.5) for a in range(250, 105, -20)]
    K.plate(mb, moon, mc + V(0, -0.35, 0), (1, 0, 0), (0, 0, 1), 0.35, gl)
    frustum(mb, (px, PY - 0.2, tip_z + 5.3), 1.2, 1.2, 0.1, 0.1, 5.5, st)
    for s in (-1, 1):
        K.cone(mb, mc + V(s * 2.9, 0, 0), mc + V(s * 4.6, 0, 0.6), 0.4, 0.0, st, 4)

    # correntes: agulha -> medalhao, pilar direito -> ancoragem no chao, espiral em volta do pilar esquerdo
    K.chain(mb, (xl - ts * 1.2, PY - 2.2, T + 21.5), mc + V(ts * 2.6, -0.8, -0.6), sag=2.2, link=0.85, m=ir, t=0.22,
            w=0.55)
    anc = V(X(-ts * 15.2), Y0 + 7.0, T)
    mb.cyl(0.9, 1.5, anc + V(0, 0, 0.75), (0, 0, 0), dk, 8, bevel=0.1)
    K.ring(mb, anc + V(0, 0, 1.9), 0.55, (1, 0, 0), (0, 0, 1), 0.2, 0.2, ir, n=10)
    K.chain(mb, (xr - ts * 1.4, PY - 2.0, T + 15.5), anc + V(0, 0, 2.3), sag=1.2, link=0.85, m=ir, t=0.22, w=0.55)
    col_box(A, (1.8, 1.8, 2.2), (anc.x, anc.y, T + 1.1))
    hel = [V(xl + math.cos(t) * 2.35, PY + math.sin(t) * 2.55, T + 4.0 + t * 0.95) for t in
           [i * 0.3 for i in range(0, 43)]]
    K.chain_path(mb, hel, link=0.8, m=ir, t=0.2, w=0.5)
    # estandarte rasgado no pilar direito
    bnr = V(xr - ts * 2.6, PY - 1.4, T + 15.2)
    mb.box((3.6, 0.3, 0.3), bnr + V(ts * 0.4, 0, 0.3), (0, 0, 0), ir, 0.0)
    K.plate(mb, [(-1.5, 0), (1.5, 0), (1.5, -7.2), (1.0, -6.3), (0.4, -7.6), (-0.1, -6.5), (-0.7, -7.8), (-1.1, -6.6),
                 (-1.5, -7.2)], bnr + V(-ts * 0.2, 0, 0), (1, 0, 0), (0, 0, 1), 0.2, "P_Shadow_Cloth")
    mc2 = bnr + V(-ts * 0.2, -0.2, -3.0)
    mini = [(math.cos(D(a)) * 0.9, math.sin(D(a)) * 0.9) for a in range(60, 301, 30)]
    mini += [(0.35 + math.cos(D(a)) * 0.7, math.sin(D(a)) * 0.7) for a in range(250, 105, -30)]
    K.plate(mb, mini, mc2, (1, 0, 0), (0, 0, 1), 0.12, gl)
    # candelabros assimetricos, cristais roxos e grade de ferro com pontas de lanca
    for (dx, y, h) in ((ts * 13.6, Y0 + 4.8, 7.6), (-ts * 13.0, Y0 + 2.4, 5.6)):
        x = X(dx)
        mb.cyl(1.0, 0.5, (x, y, T + 0.25), (0, 0, 0), ir, 8, bevel=0.0)
        mb.cyl(0.28, h, (x, y, T + h / 2), (0, 0, 0), ir, 6, bevel=0.0)
        mb.box((3.0, 0.3, 0.3), (x, y, T + h - 0.8), (0, 0, 0), ir, 0.0)
        for ox, oz in ((-1.4, -0.4), (0.0, 0.2), (1.4, -0.4)):
            mb.cyl(0.45, 0.35, (x + ox, y, T + h - 0.3 + oz), (0, 0, 0), ir, 8, bevel=0.0)
            mb.ico(0.42, (x + ox, y, T + h + 0.3 + oz), gl, 1, (1, 1, 1.8))
        col_box(A, (1.4, 1.4, h), (x, y, T + h / 2))
    crystal_cluster(mb, (X(ts * 12.6), PY + 4.8, T + 0.4), 1.5, "Crystal_Purple", rng, 6)
    crystal_cluster(mb, (X(ts * 9.4), PY + 8.4, T + 0.4), 1.0, "Crystal_Purple", rng, 4)
    crystal_cluster(mb, (X(-ts * 12.8), PY + 6.0, T + 0.4), 1.1, "Crystal_Purple", rng, 5)
    for s in (-1, 1):
        for k in range(7):
            x = X(s * (6.3 + k * 0.85))
            mb.box((0.22, 0.22, 3.2), (x, Y0 + 1.0, T + 1.6), (0, 0, 0), ir, 0.0)
            K.cone(mb, V(x, Y0 + 1.0, T + 3.2), V(x, Y0 + 1.0, T + 4.1), 0.24, 0.0, ir, 4)
        for z in (T + 0.8, T + 2.7):
            mb.box((5.6, 0.2, 0.28), (X(s * 8.85), Y0 + 1.0, z), (0, 0, 0), ir, 0.0)
        col_box(A, (5.6, 0.6, 4.0), (X(s * 8.85), Y0 + 1.0, T + 2.0))
    mb.finish()
    col_box(A, (3.6, 4.0, 50.0), (xl, PY, T + 25.0))
    col_box(A, (3.6, 4.0, 28.0), (xr, PY, T + 14.0))
    swirl("ShadowGarden", px, "P_Shadow_Swirl")


# ================================================================== 4 DEMON SLAYER (carbonizado, cortante)
def demonslayer(rng):
    px = L.PORTAL_X[3]

    def X(dx):
        return px + dx
    mb = MB("PORTAL_DemonSlayer_Gate", C, rng)
    ch, bl, em, stl = "P_DS_Char", "P_DS_Blood", "P_DS_Ember_Glow", "Metal_Blade"
    pc = PY - 2.0   # plataforma avancada 2
    K.flag_floor(mb, [(X(-11.6), Y0 + 0.2), (X(11.6), Y0 + 0.2), (X(11.6), pc - 6.0), (X(-11.6), pc - 6.0)], T - 0.3,
                 rng, "Stone_Dark", ch, tile=2.8, h=0.4, bevel=0.08, base_m=bl, mix=0.3)

    # plataforma em proa (chevron) - pedra negra com faixa vermelho-sangue
    def chev(sc, dy0):
        pts = [(-12, -4.2), (-6.5, -7.2), (6.5, -7.2), (12, -4.2), (12, 6.2), (-12, 6.2)]
        return [(X(x * sc), pc + y * sc + dy0) for x, y in pts]
    mb.prism(chev(1.0, 0), T - 0.6, T + 0.8, "Stone_Dark", 0.12)
    mb.prism(chev(1.025, 0), T + 0.2, T + 0.45, bl, 0.0)
    mb.prism(chev(0.8, 0.6), T + 0.8, T + 1.6, ch, 0.12)
    col_box2(A, (X(-12), pc - 4.2, T - 1), (X(12), pc + 6.2, T + 0.8))
    col_box2(A, (X(-6.5), pc - 7.2, T - 1), (X(6.5), pc - 4.2, T + 0.8))
    col_box2(A, (X(-9.6), pc + 0.6 - 3.36, T - 1), (X(9.6), pc + 0.6 + 4.96, T + 1.6))
    col_box2(A, (X(-5.2), pc + 0.6 - 5.76, T - 1), (X(5.2), pc + 0.6 - 3.36, T + 1.6))

    # pilares carbonizados inclinados para dentro, com rachaduras em brasa e cintas vermelho-sangue
    for s in (-1, 1):
        a, b = V(X(s * 11.0), PY, T + 1.6), V(X(s * 9.2), PY, T + 21.6)
        d = (b - a).normalized()
        mb.beam(a, b, 2.6, 2.6, ch, 0.12)
        frustum(mb, (X(s * 11.0), PY, T + 1.4), 4.0, 4.0, 3.0, 3.0, 1.8, "Stone_Dark")
        for f in (0.1, 0.74):
            p = a + (b - a) * f
            mb.beam(p - d * 0.4, p + d * 0.4, 3.0, 3.0, bl, 0.05)
        for f0 in (0.2, 0.42, 0.6):
            p = a + (b - a) * (f0 + rng.uniform(-0.04, 0.04)) + V(rng.uniform(-0.5, 0.5), -1.33, 0)
            zz = [p]
            for j in range(3):
                zz.append(zz[-1] + V(rng.uniform(0.35, 0.7) * (1 if j % 2 else -1), 0, rng.uniform(0.8, 1.3)))
            for q0, q1 in zip(zz, zz[1:]):
                mb.beam(q0, q1, 0.14, 0.2, em, 0.0)
        # espora lateral (lamina de madeira apontando para fora)
        K.plate(mb, [(0, 0), (3.4, 1.6), (0, 2.2)], a + (b - a) * 0.55 + V(s * 1.2, 0, 0), (s, 0, 0), (0, 0, 1), 0.8, ch)
    # travessas com pontas cortadas: nuki vermelho-sangue e verga negra
    K.plate(mb, [(-13.6, 0.85), (13.6, 0.85), (12.2, -0.85), (-12.2, -0.85)], V(px, PY - 0.2, T + 17.2),
            (1, 0, 0), (0, 0, 1), 1.6, bl)
    K.plate(mb, [(-15.0, 1.0), (15.0, 1.0), (13.2, -1.0), (-13.2, -1.0)], V(px, PY, T + 21.2), (1, 0, 0), (0, 0, 1),
            2.4, ch)
    # telhado duplo de beirais cortantes (pontas sobem e afinam) + forro vermelho-sangue
    blade_roof(mb, px, PY, T + 22.1, 16.8, 7.6, 2.6, 4.8, 0.7, ch, finial=ch)
    blade_roof(mb, px, PY, T + 21.75, 16.2, 7.9, 2.3, 4.4, 0.22, bl)
    blade_roof(mb, px, PY + 0.4, T + 25.3, 10.4, 5.2, 2.0, 3.2, 0.6, ch, n=12, finial=ch)

    # aro negro com filete de brasa emoldurando a espiral + 8 pontas curtas para fora
    K.ring(mb, V(px, PY - 0.1, SZ), 8.1, (1, 0, 0), (0, 0, 1), 1.0, 1.1, ch, n=32)
    K.ring(mb, V(px, PY - 0.7, SZ), 7.55, (1, 0, 0), (0, 0, 1), 0.22, 0.2, em, n=32)
    for k in range(8):
        a = D(22.5 + k * 45)
        if math.sin(a) < -0.5:
            continue
        r0 = V(math.cos(a), 0, math.sin(a))
        K.cone(mb, V(px, PY - 0.1, SZ) + r0 * 8.4, V(px, PY - 0.1, SZ) + r0 * 10.4, 0.45, 0.0, ch, 4)
    # leque de laminas radiando por tras do telhado (silhueta agressiva, unica)
    fc = V(px, PY + 1.6, T + 19.5)
    for k in range(9):
        a = D(28 + k * 15.5)
        dirv = V(math.cos(a), 0, math.sin(a))
        ln = 9.5 + 4.0 * math.sin(D(k * 22.5))
        K.blade(mb, fc + dirv * 7.8, dirv, (0, -1, 0), ln, 1.35, stl if k % 2 == 0 else ch, thick=0.3, curve=0.05)
        K.blade(mb, fc + dirv * 7.8 + V(0, -0.2, 0), dirv, (0, -1, 0), ln * 0.55, 0.5, bl, thick=0.34, curve=0.02)

    # mascara oni no telhado: face angulosa, sobrancelha, olhos em brasa, presas e chifres de osso
    O = V(px, PY - 4.7, T + 25.0)
    K.plate(mb, [(-2.6, 2.2), (2.6, 2.2), (3.0, 0.4), (2.0, -2.2), (0.8, -3.2), (-0.8, -3.2), (-2.0, -2.2), (-3.0, 0.4)],
            O, (1, 0, 0), (0, 0, 1), 1.8, bl, bevel=0.1)
    K.plate(mb, [(-3.3, 1.1), (-0.3, 0.1), (0.3, 0.1), (3.3, 1.1), (3.1, 2.5), (-3.1, 2.5)], O + V(0, -0.8, 0),
            (1, 0, 0), (0, 0, 1), 0.7, ch)
    for s in (-1, 1):
        eye = [(s * 2.3, 0.4), (s * 0.55, -0.25), (s * 0.7, 0.35), (s * 2.1, 0.9)]
        if s < 0:
            eye = list(reversed(eye))
        K.plate(mb, eye, O + V(0, -1.0, 0), (1, 0, 0), (0, 0, 1), 0.3, em)
        K.cone(mb, O + V(s * 1.0, -1.0, -1.6), O + V(s * 0.9, -1.1, -3.0), 0.32, 0.0, "Emblem_Cream", 4)
        hb = O + V(s * 2.2, 0.2, 1.9)
        K.taper_tube(mb, [hb, hb + V(s * 2.0, 0.3, 2.3), hb + V(s * 2.5, 0.6, 5.0), hb + V(s * 1.5, 0.8, 7.2)],
                     [0.8, 0.58, 0.32, 0.05], "Emblem_Cream", 6)
    mb.box((3.2, 0.4, 0.7), O + V(0, -0.95, -1.7), (0, 0, 0), ch, 0.0)
    light("L_DS_Oni", "POINT", tuple(O + V(0, -2.5, 0)), 220, (1.0, 0.25, 0.05), 0.5)

    # alas com painel xadrez verde/negro e mini-telhado cortante
    for s in (-1, 1):
        xa, xb = sorted((X(s * 12.2), X(s * 17.6)))
        mb.box2((xa, PY - 0.1, T), (xb, PY + 1.4, T + 7.4), ch, 0.1)
        nx, nz = 4, 3
        cw = (xb - xa - 1.0) / nx
        chh = 5.4 / nz
        for i in range(nx):
            for j in range(nz):
                if (i + j) % 2 == 0:
                    mb.box((cw - 0.06, 0.2, chh - 0.06), (xa + 0.5 + cw * (i + 0.5), PY - 0.18, T + 1.1 + chh * (j + 0.5)),
                           (0, 0, 0), "P_DS_Checker", 0.0)
        mb.box((xb - xa + 0.2, 0.3, 0.5), ((xa + xb) / 2, PY - 0.2, T + 6.7), (0, 0, 0), bl, 0.0)
        blade_roof(mb, (xa + xb) / 2, PY + 0.6, T + 7.4, 3.9, 3.6, 1.1, 1.6, 0.4, ch, n=8)
        col_box2(A, (xa, PY - 0.1, T), (xb, PY + 1.4, T + 8.2))
        # glicinias pendendo do beiral das alas (cachos conicos lilas)
        for k in range(6):
            x = xa + 0.5 + k * (xb - xa - 1.0) / 5
            K.raceme(mb, V(x + rng.uniform(-0.2, 0.2), PY - 1.25, T + 6.9), rng.uniform(1.8, 3.2), "P_DS_Wisteria",
                     0.42, rng)
    # lanternas pequenas vermelhas sob o beiral principal
    for x in (-14.2, -7.0, 7.0, 14.2):
        f = abs(x) / 16.8
        c = K.chochin(mb, (X(x), PY - 3.2, T + 22.0 + 4.8 * f ** 3), r=0.6, h=1.15, paper="P_Red_Glow", cap=ch, hang=0.8, n=6)
    light("L_DS_Eave_1", "POINT", (X(-7.0), PY - 4.5, T + 19.5), 120, (1.0, 0.3, 0.15), 0.3)
    light("L_DS_Eave_2", "POINT", (X(7.0), PY - 4.5, T + 19.5), 120, (1.0, 0.3, 0.15), 0.3)
    # toro baixinhos de pedra escura e katanas cravadas no chao na entrada
    for s in (-1, 1):
        K.toro(mb, (X(s * 9.4), Y0 + 2.6, T + 0.1), 0.62, "Stone_Dark", ch, glow="P_Red_Glow", lit=False)
        col_box(A, (1.8, 1.8, 4.2), (X(s * 9.4), Y0 + 2.6, T + 2.1))
        g = V(X(s * 8.2), Y0 + 5.6, T + 6.4)
        K.katana(mb, g, (s * 0.1, 0.06, -1.0), (0, -1, 0), length=8.2, width=0.62)
        col_box(A, (0.9, 0.9, 6.4), (g.x, g.y, T + 3.2))
    # paliçada de estacas afiadas inclinadas para fora nas laterais do pad
    for s in (-1, 1):
        ys = [Y0 + 0.8 + k * 1.15 for k in range(5)]
        for y in ys:
            K.cone(mb, V(X(s * 11.3), y, T - 0.2), V(X(s * 12.6), y + rng.uniform(-0.2, 0.2), T + rng.uniform(3.4, 4.6)),
                   0.36, 0.0, ch, 4)
        mb.beam(V(X(s * 11.6), ys[0] - 0.4, T + 1.6), V(X(s * 11.6), ys[-1] + 0.4, T + 1.6), 0.3, 0.35, bl, 0.0)
        col_box2(A, (X(s * 11.0), ys[0] - 0.5, T), (X(s * 12.4), ys[-1] + 0.5, T + 4.0))
    mb.finish()
    for s in (-1, 1):
        col_box(A, (3.2, 3.2, 22.0), (X(s * 10.1), PY, T + 11.0))
    swirl("DemonSlayer", px, "P_DS_Swirl")


# ================================================================== 5 ONE PIECE (cais sobre estacas)
def onepiece(rng):
    px = L.PORTAL_X[4]

    def X(dx):
        return px + dx
    mb = MB("PORTAL_OnePiece_Pier", C, rng)
    zd = T + 0.6
    y0, y1 = Y0 + 0.2, PY + 8.6
    # cais: longarinas, testeira e tabuas desencontradas
    for s in (-1, 1):
        mb.box2((X(s * 11.0) - 0.45, y0, T - 0.4), (X(s * 11.0) + 0.45, y1, zd - 0.3), "Wood_Dark", 0.08)
    mb.box2((X(-11.2), y0, T - 0.4), (X(11.2), y0 + 0.8, zd - 0.3), "Wood_Dark", 0.08)
    K.deck(mb, X(-11.4), X(11.4), y0, y1, zd, rng, "Wood_Plank", pw=1.4)
    col_box2(A, (X(-11.4), y0, T - 1), (X(11.4), y1, zd))
    # estacas (pilings) com amarras e corda em catenaria; defensas (pneus e boias de corda)
    for s in (-1, 1):
        tops = []
        for k in range(7):
            y = y0 + 0.6 + k * 3.5
            x = X(s * 11.9)
            h = zd + rng.uniform(1.3, 2.9)
            mb.cyl(0.64, h - (T - 1.0), (x, y, (h + T - 1.0) / 2), (0, 0, rng.uniform(0, 1)), "Wood_Dark", 8, bevel=0.0)
            mb.cyl(0.7, 0.4, (x, y, h - 0.7), (0, 0, 0), "Rope", 8, bevel=0.0)
            tops.append(V(x, y, h - 0.7))
            if k in (1, 5):
                K.ring(mb, V(x + s * 0.95, y, T + 1.1), 0.75, (0, 1, 0), (0, 0, 1), 0.42, 0.5, "Metal_Dark", n=12)
                mb.rod((x + s * 0.7, y, T + 1.9), (x + s * 0.95, y, T + 1.8), 0.08, "Rope", 4)
            elif k == 3:
                mb.cyl(0.55, 1.7, (x + s * 1.0, y, T + 1.2), (0, 0, 0), "Rope", 8, bevel=0.0)
                mb.rod((x + s * 1.0, y, T + 2.0), (x + s * 0.4, y, h - 0.8), 0.08, "Rope", 4)
        for a_, b_ in zip(tops, tops[1:]):
            mb.tube([a_ + (b_ - a_) * t - V(0, 0, 0.9 * 4 * t * (1 - t)) for t in (0, 0.25, 0.5, 0.75, 1.0)], 0.13,
                    "Rope", 5)
        col_box2(A, (X(s * 11.9) - 0.7, y0, T), (X(s * 11.9) + 0.7, y1, zd + 2.2))
    # plataforma de cabrestante em 2 niveis
    mb.cyl(8.6, 1.0, (px, PY, zd + 0.5), (0, 0, 0), "Wood_Dark", 20, bevel=0.15)
    mb.cyl(6.6, 0.8, (px, PY, zd + 1.4), (0, 0, 0), "Wood_Plank", 20, bevel=0.12)
    for k in range(10):
        a = D(k * 36)
        mb.box((0.35, 0.35, 1.05), (px + math.cos(a) * 8.62, PY + math.sin(a) * 8.62, zd + 0.5), (0, 0, a), "Metal_Dark", 0.0)
    col_disc(px, PY, 8.6, zd - 1.5, zd + 1.0)
    col_disc(px, PY, 6.6, zd - 1.5, zd + 1.8)
    # timao gigante: aro duplo, filete dourado, raios com punhos, cravos
    R = SWIRL_R + 1.2
    for rr, w in ((R, 1.3), (R + 2.2, 0.8)):
        ring = [V(px + math.cos(D(a)) * rr, PY, SZ + math.sin(D(a)) * rr) for a in range(0, 361, 10)]
        mb.sweep(ring, [(-w, -0.9), (w, -0.9), (w, 0.9), (-w, 0.9)], "Wood_Light" if w > 1 else "Wood_Dark", True,
                 up=(0, 1, 0))
    K.ring(mb, V(px, PY - 0.95, SZ), R + 1.1, (1, 0, 0), (0, 0, 1), 0.7, 0.2, "P_DB_Gold", n=36)
    for k in range(8):
        a = D(k * 45 + 22.5)
        p0 = V(px + math.cos(a) * (R + 1.0), PY, SZ + math.sin(a) * (R + 1.0))
        p1 = V(px + math.cos(a) * (R + 6.2), PY, SZ + math.sin(a) * (R + 6.2))
        if p1.z < T + 4.0:
            continue
        mb.rod(p0, p1, 0.55, "Wood_Light", 8)
        mb.ico(0.95, p1, "Wood_Light", 1, (1, 1, 1.3))
        mb.cyl(0.7, 0.35, p0 + (p1 - p0) * 0.62, (0, math.pi / 2 - a, 0), "Metal_Brass", 8, bevel=0.0)
    for k in range(12):
        a = D(k * 30 + 15)
        mb.box((0.5, 0.3, 0.5), (px + math.cos(a) * R, PY - 1.0, SZ + math.sin(a) * R), (0, -a, 0), "Metal_Brass", 0.0)
    # caveira com ossos cruzados no topo do timao
    S = V(px, PY - 1.4, T + 25.4)
    for s in (-1, 1):
        mb.beam(S + V(-s * 3.0, 0.4, -2.6), S + V(s * 3.0, 0.4, 1.8), 0.7, 0.7, "Emblem_Cream", 0.1)
        for e in (S + V(-s * 3.0, 0.4, -2.6), S + V(s * 3.0, 0.4, 1.8)):
            for o in (-0.4, 0.4):
                mb.ico(0.5, e + V(o, 0, o * s), "Emblem_Cream", 1)
    mb.ico(2.1, S, "Emblem_Cream", 2, (1.0, 0.85, 0.95))
    mb.box((2.3, 1.5, 1.2), S + V(0, -0.2, -1.8), (0, 0, 0), "Emblem_Cream", 0.3)
    for s in (-1, 1):
        mb.ico(0.55, S + V(s * 0.78, -1.62, 0.15), "Metal_Dark", 1, (1, 0.5, 1.15))
    K.cone(mb, S + V(0, -1.75, -0.7), S + V(0, -1.9, -0.2), 0.3, 0.0, "Metal_Dark", 3)
    for k in range(3):
        mb.box((0.36, 0.2, 0.6), S + V(-0.5 + k * 0.5, -0.98, -2.1), (0, 0, 0), "Metal_Dark", 0.0)
    # cabecos laterais (bitts) com cordas enroladas e tampa de ferro
    for s in (-1, 1):
        x = X(s * 10.1)
        mb.cyl(1.7, 6.4, (x, PY, zd + 3.2), (0, 0, D(22.5)), "Wood_Dark", 8, bevel=0.15)
        mb.cyl(1.95, 0.5, (x, PY, zd + 6.5), (0, 0, D(22.5)), "Metal_Dark", 8, bevel=0.05)
        for zz in (zd + 1.8, zd + 2.4, zd + 4.6):
            mb.cyl(1.85, 0.5, (x, PY, zz), (0, 0, 0), "Rope", 10, bevel=0.0)
        col_box(A, (3.4, 3.4, 7.0), (x, PY, zd + 3.5))
    # ancora grande em pe a esquerda, corrente ate a estaca
    ax, ay = X(-14.6), PY - 3.2
    im = "Metal_Iron"
    mb.box((1.0, 1.0, 10.2), (ax, ay, T + 6.1), (0, 0, 0), im, 0.12)
    mb.box((5.8, 0.9, 0.9), (ax, ay, T + 10.2), (0, 0, 0), im, 0.1)
    for s in (-1, 1):
        mb.ico(0.55, (ax + s * 2.9, ay, T + 10.2), im, 1)
    K.ring(mb, V(ax, ay, T + 11.9), 1.0, (1, 0, 0), (0, 0, 1), 0.36, 0.36, im, n=14)
    arcp = [V(ax + math.cos(D(a)) * 3.4, ay, T + 4.4 + math.sin(D(a)) * 3.0) for a in range(195, 346, 15)]
    mb.tube(arcp, 0.55, im, 8)
    for s, p in ((-1, arcp[0]), (1, arcp[-1])):
        K.plate(mb, [(0, 0), (1.9, 0.6), (0.2, 2.6)], p + V(0, 0, -0.3), (s, 0, 0), (0, 0, 1), 0.5, im)
    K.cone(mb, V(ax, ay, T + 1.0), V(ax, ay, T - 0.3), 0.8, 0.1, im, 4)
    K.chain(mb, (ax + 0.8, ay, T + 11.6), (X(-11.9), y0 + 0.6 + 2 * 3.5, T + 2.8), sag=1.6, link=0.8, m="Metal_Dark")
    col_box(A, (6.0, 1.6, 12.0), (ax, ay, T + 6.0))
    # mastro com verga, vela, bandeira pirata, cesto de gavea, ovens e boia salva-vidas
    mx, my = X(14.6), PY - 1.6
    mb.cyl(0.62, 24.5, (mx, my, T + 12.25), (0, 0, 0), "Wood_Dark", 8, r2=0.42, bevel=0.0)
    mb.cyl(1.35, 1.3, (mx, my, T + 17.6), (0, 0, 0), "Wood_Dark", 10, bevel=0.0)
    mb.box((7.4, 0.5, 0.5), (mx, my - 0.7, T + 21.0), (0, 0, 0), "Wood_Dark", 0.05)
    spts, sprof = [], []
    for i in range(7):
        f = i / 6
        spts.append(V(mx, my - 0.9, T + 20.7 - 6.6 * f))
        w = 3.4 - 0.6 * f
        bul = 0.3 + 1.1 * math.sin(math.pi * (0.15 + 0.7 * f))
        front = [(x, bul * (1 - (x / w) ** 2)) for x in [-w + 2 * w * k / 6 for k in range(7)]]
        sprof.append(front + [(x, b - 0.24) for x, b in reversed(front)])
    K.loft(mb, spts, sprof, "P_OP_Sail", True)
    for s in (-1, 1):
        mb.rod((mx + s * 2.8, my - 1.4, T + 14.2), (mx + s * 2.6, my - 3.4, T + 1.0), 0.08, "Rope", 4)
    mb.box((3.6, 0.2, 2.4), (mx - 1.9, my, T + 23.2), (0, 0, 0), "Cloth_Navy", 0.0)
    mb.ico(0.55, (mx - 1.9, my - 0.2, T + 23.3), "Emblem_Cream", 1, (1, 0.5, 1))
    for (ex, ey) in ((X(11.9), y0 + 0.6 + 2 * 3.5), (X(16.9), PY - 6.5)):
        mb.rod((mx, my, T + 23.5), (ex, ey, T + 1.2), 0.1, "Rope", 4)
    K.ring(mb, V(mx, my - 0.75, T + 7.0), 1.15, (1, 0, 0), (0, 0, 1), 0.55, 0.5, "P_OP_Red", n=16)
    for k in range(4):
        a = D(k * 90 + 45)
        mb.box((0.55, 0.62, 0.6), (mx + math.cos(a) * 1.15, my - 0.75, T + 7.0 + math.sin(a) * 1.15), (0, -a, 0),
               "Emblem_Cream", 0.0)
    col_box(A, (1.4, 1.4, 24.0), (mx, my, T + 12.0))
    # bau do tesouro aberto, barris, caixotes, rolos de corda
    cx_, cy_ = X(-8.9), Y0 + 3.2
    mb.box((3.2, 2.2, 1.8), (cx_, cy_, zd + 0.9), (0, 0, 0.15), "Wood_Plank", 0.12)
    mb.box((3.3, 0.35, 2.0), (cx_ - 0.15, cy_ + 1.2, zd + 2.6), (D(-20), 0, 0.15), "Wood_Plank", 0.1)
    for k in range(6):
        mb.ico(0.42, (cx_ + rng.uniform(-1.1, 1.1), cy_ + rng.uniform(-0.6, 0.6), zd + 1.85), "P_DB_Gold", 1)
    mb.box((3.4, 0.3, 0.3), (cx_, cy_ - 1.1, zd + 1.2), (0, 0, 0.15), "Metal_Brass", 0.0)
    col_box(A, (3.6, 2.8, 3.0), (cx_, cy_, zd + 1.5))
    for p in ((X(-9.6), PY - 5.8), (X(-8.6), PY + 6.0), (X(9.0), Y0 + 2.2)):
        barrel(mb, (p[0], p[1], zd), 1.05, 2.5)
        col_box(A, (2.4, 2.4, 2.6), (p[0], p[1], zd + 1.3))
    crate(mb, (X(8.4), PY + 5.4, zd), 2.2, 0.3, rng)
    crate(mb, (X(8.6), PY + 5.2, zd + 2.2), 1.6, -0.2, rng)
    col_box(A, (2.8, 2.8, 4.0), (X(8.4), PY + 5.4, zd + 2.0))
    for (x, y) in ((X(9.2), Y0 + 6.2), (X(-9.4), PY + 3.2)):
        for k in range(3):
            K.ring(mb, V(x, y, zd + 0.25 + k * 0.42), 1.15 - k * 0.2, (1, 0, 0), (0, 1, 0), 0.5, 0.42, "Rope", n=14)
    palm(mb, (X(-18.2), PY + 6.5, T), 13.0, rng)
    palm(mb, (X(17.8), Y0 + 3.2, T), 10.5, rng)
    col_box(A, (1.6, 1.6, 8.0), (X(-18.2), PY + 6.5, T + 4.0))
    col_box(A, (1.6, 1.6, 8.0), (X(17.8), Y0 + 3.2, T + 4.0))
    mb.finish()
    swirl("OnePiece", px, "P_OP_Swirl")


# ================================================================== 6 ONE PUNCH MAN (skyline vertical)
def _tower(mb, x, y, z0, h, w, d, con, gl, neon, rng, setbacks=2, spire=True, top_neon=False, body=None):
    """arranha-ceu escalonado com faixas de janelas; devolve topo"""
    z = z0
    hs = [h * 0.58, h * 0.27, h * 0.15][:setbacks + 1]
    tot = sum(hs)
    hs = [v * h / tot for v in hs]
    ww, dd = w, d
    for i, hh in enumerate(hs):
        mb.box((ww, dd, hh), (x, y, z + hh / 2), (0, 0, 0), body or con, 0.25 if i == 0 else 0.18)
        kk = int((hh - 1.5) / 3.0)
        for k in range(kk):
            zz = z + 1.8 + k * 3.0
            mb.box((ww + 0.14, dd + 0.14, 0.7 if body else 1.0), (x, y, zz), (0, 0, 0), gl, 0.0)
        if body:
            for sx in (-1, 1):
                mb.box((0.5, dd + 0.3, hh), (x + sx * (ww / 2), y, z + hh / 2), (0, 0, 0), con, 0.0)
        mb.box((ww + 0.3, dd + 0.3, 0.4), (x, y, z + hh), (0, 0, 0), neon if (top_neon and i == len(hs) - 1) else con,
               0.0)
        z += hh
        ww, dd = ww * 0.72, dd * 0.72
    if spire:
        mb.cyl(0.2, 6.5, (x, y, z + 3.25), (0, 0, 0), "Metal_Iron", 6, bevel=0.0)
        mb.ico(0.45, (x, y, z + 6.7), neon, 1)
    return z


def opm(rng):
    px = L.PORTAL_X[5]

    def X(dx):
        return px + dx
    mb = MB("PORTAL_OnePunchMan_City", C, rng)
    con, gl, neon, yel, red = "P_OPM_Concrete", "P_OPM_Glass", "P_OPM_Neon", "P_OPM_Yellow", "P_OPM_Red"
    zp = T + 0.5
    # praca de concreto elevada: placas com juntas, faixa zebrada na borda, frisos neon
    mb.box2((X(-11.8), Y0 + 0.2, T - 0.5), (X(11.8), PY + 8.8, zp), con, 0.1)
    for k in range(1, 7):
        mb.box((23.4, 0.16, 0.06), (px, Y0 + 0.2 + k * 3.0, zp + 0.02), (0, 0, 0), "Stone_Dark", 0.0)
    for k in (-2, -1, 1, 2):
        mb.box((0.16, PY + 8.6 - Y0, 0.06), (X(k * 4.7), (Y0 + PY + 8.8) / 2, zp + 0.02), (0, 0, 0), "Stone_Dark", 0.0)
    n = 16
    for i in range(n):
        mb.box((23.2 / n, 0.9, 0.1), (X(-11.6 + 23.2 * (i + 0.5) / n), Y0 + 0.75, zp + 0.03), (0, 0, 0),
               yel if i % 2 else "Metal_Dark", 0.0)
    for k in range(6):
        y = Y0 + 2.0 + k * 1.9
        for s in (-1, 1):
            mb.box((0.6, 1.2, 0.12), (X(s * 10.4), y, zp + 0.05), (0, 0, 0), neon, 0.0)
    col_box2(A, (X(-11.8), Y0 + 0.2, T - 1), (X(11.8), PY + 8.8, zp))
    # palco em 2 niveis com friso neon (recuado 1 stud)
    sy = PY + 1.0
    mb.box((22.0, 10.0, 0.9), (px, sy, zp + 0.45), (0, 0, 0), con, 0.15)
    mb.box((18.0, 8.0, 0.9), (px, sy, zp + 1.35), (0, 0, 0), con, 0.15)
    mb.box((18.1, 0.2, 0.16), (px, sy - 4.05, zp + 1.6), (0, 0, 0), neon, 0.0)
    mb.box((22.1, 0.2, 0.16), (px, sy - 5.05, zp + 0.7), (0, 0, 0), yel, 0.0)
    col_box(A, (22.0, 10.0, 1.9), (px, sy, zp - 0.05))
    col_box(A, (18.0, 8.0, 2.8), (px, sy, zp + 0.4))
    hw = SWIRL_R + 1.4
    # pilones-torre (verticalidade): esquerdo 48, direito 40, escalonados, com filete neon na face interna
    for s, htop, w in ((-1, 48.0, 4.8), (1, 40.0, 4.4)):
        x = X(s * (hw + 2.0))
        top = _tower(mb, x, PY, zp, htop, w, w + 0.6, con, gl, neon, rng, setbacks=2, top_neon=True)
        mb.box((0.4, w + 0.8, 20.0), (x - s * (w / 2 + 0.05), PY, zp + 11.0), (0, 0, 0), neon, 0.0)
        mb.box((w + 1.0, w + 1.6, 1.4), (x, PY, zp + 0.7), (0, 0, 0), "Stone_Dark", 0.12)
        col_box(A, (w, w + 0.6, htop), (x, PY, zp + htop / 2))
    mb.box((2 * hw + 6.0, 3.2, 2.8), (px, PY, T + 23.4), (0, 0, 0), con, 0.3)
    mb.box((2 * hw + 1.6, 3.4, 0.4), (px, PY, T + 21.8), (0, 0, 0), neon, 0.0)
    ring = [V(px + math.cos(D(a)) * (SWIRL_R + 0.5), PY - 0.3, SZ + math.sin(D(a)) * (SWIRL_R + 0.5)) for a in
            range(0, 361, 10)]
    mb.sweep(ring, [(-0.35, -0.3), (0.35, -0.3), (0.35, 0.3), (-0.35, 0.3)], neon, True, up=(0, 1, 0))
    # medalhao amarelo com punho de luva vermelha
    ez = T + 28.4
    mb.cyl(3.5, 0.9, (px, PY - 0.6, ez), (D(90), 0, 0), yel, 24, bevel=0.1)
    K.ring(mb, V(px, PY - 1.0, ez), 3.5, (1, 0, 0), (0, 0, 1), 0.4, 0.5, con, n=24)
    mb.box((3.0, 1.0, 2.0), (px, PY - 1.5, ez - 0.2), (0, 0, 0), red, 0.3)
    for k in range(4):
        mb.box((0.72, 0.9, 1.0), (px - 1.1 + k * 0.73, PY - 1.9, ez + 1.1), (0, 0, 0), red, 0.18)
    mb.box((0.8, 0.8, 1.8), (px + 1.7, PY - 2.0, ez - 0.1), (0, 0, D(-25)), red, 0.18)
    mb.box((2.2, 1.1, 1.0), (px, PY - 1.4, ez - 1.6), (0, 0, 0), red, 0.2)
    # skyline atras e nos lados (alturas 28-62; a torre-sede no centro-direita)
    # (as de tras nascem do penhasco; as laterais direitas ficam na frente dele)
    towers = [(-7.0, 9.0, 54.0, 5.0, 4.8, False, True), (0.5, 10.5, 42.0, 4.6, 4.6, True, False),
              (7.5, 8.8, 68.0, 6.2, 6.0, False, True), (14.2, 7.0, 48.0, 5.0, 5.0, True, False),
              (17.4, 1.2, 50.0, 4.8, 4.8, False, True), (22.2, 2.2, 32.0, 4.0, 4.0, True, False)]
    for (dx, dy, h, w, d, tn, dark) in towers:
        x, y = X(dx), PY + dy
        _tower(mb, x, y, T, h, w, d, con, gl, neon, rng, setbacks=2 if h > 35 else 1, top_neon=tn,
               body="P_OPM_DarkGlass" if dark else None)
        col_box(A, (w, d, h), (x, y, T + h / 2))
    # torre-sede: coroa de neon
    hx, hy = X(7.5), PY + 8.8
    for zz in (T + 42.0, T + 56.0):
        mb.box((6.8, 6.6, 0.35), (hx, hy, zz), (0, 0, 0), neon, 0.0)
    # totens de holograma e postes urbanos
    for s in (-1, 1):
        x = X(s * 13.4)
        mb.box((1.6, 1.6, 5.0), (x, PY - 5.0, zp + 2.5), (0, 0, 0), con, 0.2)
        mb.box((1.7, 1.7, 0.4), (x, PY - 5.0, zp + 4.2), (0, 0, 0), neon, 0.0)
        mb.box((1.72, 1.72, 0.5), (x, PY - 5.0, zp + 1.0), (0, 0, 0), yel, 0.0)
        col_box(A, (1.6, 1.6, 5.0), (x, PY - 5.0, zp + 2.5))
        lx, ly = X(s * 11.2), Y0 + 2.2
        mb.cyl(0.28, 8.0, (lx, ly, zp + 4.0), (0, 0, 0), "Metal_Iron", 6, bevel=0.0)
        mb.box((2.6, 0.5, 0.35), (lx - s * 1.1, ly, zp + 8.0), (0, 0, 0), "Metal_Iron", 0.0)
        mb.box((1.4, 0.9, 0.4), (lx - s * 2.2, ly, zp + 7.8), (0, 0, 0), "Metal_Dark", 0.0)
        mb.box((1.2, 0.7, 0.12), (lx - s * 2.2, ly, zp + 7.56), (0, 0, 0), neon, 0.0)
        col_box(A, (0.8, 0.8, 8.0), (lx, ly, zp + 4.0))
    mb.finish()
    swirl("OnePunchMan", px, "P_OPM_Swirl")


def build():
    rng = random.Random(707)
    naruto(rng)
    dragonball(rng)
    shadow(rng)
    demonslayer(rng)
    onepiece(rng)
    opm(rng)
    import fm_portal_terrace
    fm_portal_terrace.build(rng)
    # placas de dificuldade (1..6) no pe de cada escada (sem texto: pips luminosos)
    mb = MB("PORTAL_Difficulty_Markers", C, rng)
    for i, px in enumerate(L.PORTAL_X):
        x, y = px + 7.8, L.FLIGHT1_Y0 - 1.5
        mb.box((1.0, 1.0, 6.0), (x, y, L.FLOOR + 3.0), (0, 0, 0), "Wood_Dark", 0.1)
        mb.box((3.6, 0.6, 2.2), (x, y - 0.3, L.FLOOR + 5.4), (0, 0, 0), "Wood_Plank", 0.1)
        for k in range(i + 1):
            mb.ico(0.28, (x - 1.25 + k * 0.5, y - 0.7, L.FLOOR + 5.4), "Forge_Emissive", 1)
        col_box(A, (1.2, 1.2, 6.0), (x, y, L.FLOOR + 3.0))
    mb.finish()
