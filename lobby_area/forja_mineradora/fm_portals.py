# fm_portals - seis portais no terraco (facil -> dificil, esquerda -> direita). Mesma familia (pad no terraco,
# espiral r7.5 voltada para -Y num PRATO CONCAVO com aro de energia e tampa traseira escura, degraus de acesso),
# mas cada um e uma PECA ARQUITETONICA independente, inteira no seu lote (px +-14, folga >= 4 entre vizinhos):
#   Naruto  = torii vermelho alto e fino + moon gate (anel de pedra clara num muro de vila) -> passagem p/ Konoha
#   DB      = dais-capsula + aro dourado + Shenlong que passa POR TRAS do aro (so cabeca e garras na frente)
#   Shadow  = porta de catedral gotica escura: parede com o disco, rosacea, capiteis, agulha, arcobotante
#   DS      = portao-santuario largo e baixo: karahafu de telha preta, cortina de glicinias, ichimatsu, hanafuda
#   OP      = cais sobre estacas + timao de raios torneados (aro interno e externo finos), caveira, ancora, mastro
#   OPM     = praca escura e contida: torres de vidro marinho com janelas finas, pilones de metal, punho r5
# O dressing das escadas, o do centro do terraco e as placas de dificuldade ficam em fm_portal_terrace.
import math, random
from mathutils import Vector
from fm_lib import MB, D, col_box, col_box2, marker, light, SWIRL_R, bezier
from fm_parts import crystal_cluster, frustum, barrel
import fm_portal_kit as K
from fm_portal_kit import V, GLOW, LIGHT_COL
import fm_portal_terrace as PT
import fm_layout as L

C = "06_PORTALS"
T = L.TERR
PY = L.PORTAL_Y     # plano do aro da espiral
SZ = T + 2.0 + 9.2  # centro da espiral
Y0 = L.FLIGHT2_Y1   # topo do lance 2 (inicio do pad)
A = "Portal"
DISH_D = 1.8        # recuo do centro do prato da espiral (+Y)


def swirl(key, px, mat_name, mb, back_m, rim_y=-0.6, z=None, r=SWIRL_R, cup_r=None):
    """espiral = PRATO CONCAVO raso (centro recuado DISH_D em +Y), 1 material e <= 200 faces (o export_vfx
    continua tratando o disco como 'simples'); no objeto do portal: aro de energia (toro r=SWIRL_R, secao 0.5,
    P_<key>_Glow) encaixado na moldura e tampa traseira escura (o verso le como costas do portal)"""
    zc = SZ if z is None else z
    sw = MB("PORTAL_%s_Swirl" % key, C)
    bm = sw.bm
    n = 32
    c = bm.verts.new((0.0, DISH_D, 0.0))
    rings = []
    for f in (0.3, 0.62, 0.86, 1.0):
        rr = r * f
        y = DISH_D * (1.0 - f * f)
        rings.append([bm.verts.new((math.cos(math.tau * i / n) * rr, y, math.sin(math.tau * i / n) * rr))
                      for i in range(n)])
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((c, rings[0][i], rings[0][j]))
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((r0[i], r1[i], r1[j], r0[j]))
    sw._post(list(bm.verts), mat_name, 0.0, 0, 1)
    ob = sw.finish(recalc=False)
    ob.location = (px, PY, zc)
    K.ring(mb, V(px, PY + rim_y, zc), r, (1, 0, 0), (0, 0, 1), 0.5, 0.5, GLOW[key], n=32)
    K.cup(mb, V(px, PY, zc), cup_r or (r + 0.06), -0.05, DISH_D + 0.45, back_m)
    marker("PORTAL_" + key, (px, PY - 0.6, zc), (0, 0, 0), 4, "CIRCLE",
           props={"destino": key, "raio": r, "touch": True})
    col = LIGHT_COL[key]
    light("L_Portal_" + key, "POINT", (px, PY - 3.0, zc), 1600, col, 3.0)
    # luz do pad: pinta o terraco na cor do portal (sem sombra; alcance pedido para o Roblox ~24)
    pl = light("L_P_%s_Pad" % key, "POINT", (px, PY - 7.0, T + 4.5), 650, col, 2.0)
    pl.data.use_shadow = False
    pl["rbx_range"] = 24.0
    pl["rbx_shadows"] = False
    return ob


def col_disc(cx, cy, r, z0, z1):
    """colisao de um disco/octogono: quadrado inscrito + cruz"""
    h = z1 - z0
    zc = (z0 + z1) / 2
    col_box(A, (r * 1.414, r * 1.414, h), (cx, cy, zc))
    col_box(A, (r * 1.84, r * 0.76, h), (cx, cy, zc))
    col_box(A, (r * 0.76, r * 1.84, h), (cx, cy, zc))


def spiral_pts(c, y, s, turns=21, step=0.5, k=0.12):
    """espiral de Konoha (plano XZ, na profundidade y)"""
    return [V(c.x + math.cos(t) * k * s * t, y, c.z + math.sin(t) * k * s * t) for t in [i * step for i in range(turns)]]


# ================================================================== 1 NARUTO / KONOHA
def naruto(rng):
    px = L.PORTAL_X[0]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_Naruto_Torii", C, rng, vcap=2)
    red, blk, wal, tl, gl = "P_Naruto_Red", "Wood_Dark", "P_Naruto_Wall", "P_Naruto_Tile", "P_Naruto_Glow"
    pc = PY - 1.0   # plataforma avancada 1 stud
    # sando (lajes claras no eixo) + canteiros de cascalho rastelado com meio-fio
    K.flag_floor(mb, [(X(-5.6), Y0 + 0.2), (X(5.6), Y0 + 0.2), (X(5.6), pc - 5.0), (X(-5.6), pc - 5.0)], T - 0.3, rng,
                 "Stone_Light", None, tile=3.4, h=0.4, bevel=0.0, base_m="Stone_Dark")
    for s in (-1, 1):
        xa, xb = X(s * 5.9), X(s * 12.6)
        mb.box2((xa, Y0 + 0.3, T - 0.3), (xb, pc - 5.4, T + 0.12), "P_Gravel", 0.04)
        for k in range(4):
            xx = X(s * (7.2 + k * 1.35))
            mb.box((0.16, pc - 5.9 - Y0, 0.07), (xx, (Y0 + pc - 5.4) / 2 + 0.1, T + 0.14), (0, 0, 0), "Stone_Dark", 0.0)
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

    # torii alto e fino: pilares de 25, nuki acima do moon gate, kasagi curvo (pontas dentro do lote)
    zb = T + 1.8
    ztop = T + 26.8
    for s in (-1, 1):
        x = X(s * 9.6)
        mb.cyl(1.95, 1.2, (x, PY, zb + 0.6), (0, 0, 0), "Stone_Dark", 10, bevel=0.15)
        mb.cyl(1.25, ztop - zb, (x, PY, (zb + ztop) / 2), (0, 0, 0), red, 12, r2=1.08, bevel=0.1)
        mb.cyl(1.45, 1.1, (x, PY, zb + 1.75), (0, 0, 0), blk, 12, bevel=0.08)
        mb.cyl(1.36, 0.8, (x, PY, ztop - 0.3), (0, 0, 0), blk, 12, bevel=0.05)
    zn = T + 22.3
    mb.box((24.6, 1.4, 1.5), (px, PY, zn), (0, 0, 0), red, 0.15)
    for s in (-1, 1):
        mb.box((0.5, 1.9, 1.9), (X(s * 11.4), PY, zn), (0, 0, 0), blk, 0.05)   # cunhas (kusabi) por fora
    zk = T + 27.4
    pts = [V(px + x, PY, zk + 0.018 * x * x) for x in [-13.2 + 26.4 * i / 14 for i in range(15)]]
    mb.sweep(pts, [(-1.4, -1.2), (1.4, -1.2), (1.6, 1.0), (-1.6, 1.0)], blk, True, up=(0, 0, 1))
    pts2 = [p + V(0, 0, -2.0) for p in pts[1:-1]]
    mb.sweep(pts2, [(-1.1, -0.9), (1.1, -0.9), (1.1, 0.9), (-1.1, 0.9)], red, True, up=(0, 0, 1))
    # gakuzuka (placa) com a espiral
    zg = T + 23.9
    mb.box((3.2, 1.8, 3.6), (px, PY - 0.2, zg), (0, 0, 0), blk, 0.15)
    mb.box((2.6, 0.4, 2.9), (px, PY - 1.1, zg), (0, 0, 0), wal, 0.05)
    mb.tube(spiral_pts(V(px, 0, zg), PY - 1.4, 1.0), 0.14, red, 6)
    # shimenawa presa na face do nuki (acima do moon gate, nunca na frente do disco) com shide
    def rz(x):
        return zn - 0.6 * (1 - (x / 8.3) ** 2)
    rope = [V(X(x), PY - 1.3, rz(x)) for x in [-8.3 + 16.6 * i / 12 for i in range(13)]]
    K.rope_twist(mb, rope, 0.6, "Rope", n=4, strands=2, pitch=2.2, seg=0.7)
    for x in (-5.4, -1.8, 1.8, 5.4):
        K.shide(mb, V(X(x), PY - 1.75, rz(x) - 0.45), 0.95, m=wal)
    # lanternas de papel laranja penduradas nas pontas do kasagi
    for s in (-1, 1):
        x = X(s * 12.3)
        c = K.chochin(mb, (x, PY, zk + 0.018 * 12.3 ** 2 - 1.2), r=1.05, h=2.1, paper=gl, cap=blk, band=red, hang=1.5,
                      rod_m=blk)
        light("L_P_Naruto_Chochin_%d" % (s + 1), "POINT", tuple(c + V(0, -1.2, 0)), 160, (1.0, 0.6, 0.3), 0.4)

    # MOON GATE: painel de muro de vila (reboco, soco de pedra, frechal e telhadinho) entre os pilares, com a
    # abertura circular emoldurada por anel de pedra clara em aduelas; o disco fica preso no anel
    hr = 8.3
    K.round_hole_panel(mb, px, PY, T + 1.8, T + 20.4, 9.6, SZ, hr, 1.0, wal, n=16)
    mb.box((19.2, 1.3, 0.8), (px, PY, T + 2.2), (0, 0, 0), "Stone_Dark", 0.1)
    mb.box((19.2, 1.2, 0.35), (px, PY, T + 20.25), (0, 0, 0), blk, 0.0)
    K.tile_coping(mb, (X(-9.6), PY), (X(9.6), PY), T + 20.45, 1.0, tl, tl, over=0.6, rise=0.6, t=0.3)
    for k in range(8):
        a0 = 45.0 * k + 0.4
        seg = [V(px + math.cos(D(a0 + 44.2 * i / 4)) * 7.85, PY, SZ + math.sin(D(a0 + 44.2 * i / 4)) * 7.85)
               for i in range(5)]
        mb.sweep(seg, [(-0.45, -0.9), (0.45, -0.9), (0.45, 0.9), (-0.45, 0.9)], "Stone_Light", True, up=(0, 1, 0))
    # fecho (aduela-chave) com a espiral de Konoha gravada em vermelho
    kz = SZ + 7.85
    mb.box((2.0, 2.2, 2.4), (px, PY, kz + 0.2), (0, 0, 0), "Stone_Light", 0.12)
    sp = spiral_pts(V(px, 0, kz + 0.25), PY - 1.16, 0.85, turns=19, step=0.45)
    mb.tube(sp, 0.11, red, 5)
    K.cone(mb, sp[-1], sp[-1] + V(0.3, 0, -0.55), 0.13, 0.0, red, 4)
    # soleira em 2 degraus (passa-se por cima do anel, como num moon gate de verdade): degraus de 1.0
    mb.box((6.0, 5.2, 1.0), (px, PY, T + 2.3), (0, 0, 0), "Stone_Light", 0.12)
    mb.box((4.4, 2.6, 1.0), (px, PY, T + 3.3), (0, 0, 0), "Stone_Light", 0.12)
    col_box2(A, (X(-3.0), PY - 2.6, T + 0.9), (X(3.0), PY + 2.6, T + 2.8))
    col_box2(A, (X(-2.2), PY - 1.3, T + 2.8), (X(2.2), PY + 1.3, T + 3.8))
    for s in (-1, 1):
        col_box2(A, (X(s * 7.7), PY - 0.6, T + 1.8), (X(s * 9.6), PY + 0.6, T + 20.4))

    # muro de vila continua dos lados: a oeste ate o penhasco, a leste volta para o fundo e fecha o patio
    for s, x1 in ((-1, 12.8), (1, 12.5)):
        a, b = (X(s * 10.9), PY), (X(s * x1), PY)
        K.village_wall(mb, a, b, T, 7.2, rng)
    col_box2(A, (X(-17.0), PY - 0.8, T), (X(-10.9), PY + 0.8, T + 8.6))
    col_box2(A, (X(10.9), PY - 0.8, T), (X(13.4), PY + 0.8, T + 8.6))
    K.village_wall(mb, (X(12.5), PY), (X(12.5), PY + 10.0), T, 7.2, rng)
    col_box2(A, (X(11.7), PY, T), (X(13.6), PY + 10.6, T + 8.6))
    for ex in (-12.05,):
        ec = V(X(ex), PY - 0.72, T + 4.4)
        mb.cyl(1.0, 0.25, ec, (D(90), 0, 0), wal, 16, bevel=0.0)
        K.ring(mb, ec, 1.1, (1, 0, 0), (0, 0, 1), 0.28, 0.35, red, n=18)
        mb.tube(spiral_pts(ec, ec.y - 0.18, 0.7, turns=18, step=0.55), 0.12, red, 5)

    # toro de pedra sobre o cascalho (luz propria) e pedras escuras
    for s in (-1, 1):
        x, y = X(s * 9.0), Y0 + 3.0
        K.toro(mb, (x, y, T + 0.1), 1.0, "Stone_Light", "Stone_Dark", glow=gl, name="L_P_Naruto_Toro_%d" % (s + 1))
        col_box(A, (2.6, 2.6, 6.6), (x, y, T + 3.3))
    for s in (-1, 1):
        K.mossy_rock(mb, (X(s * 11.4), Y0 + 1.5, T), (2.2, 1.9, 1.5), rng, "Stone_Dark", moss=None)
    K.mossy_rock(mb, (X(-12.2), PY - 6.8, T + 0.9), (2.0, 1.7, 1.3), rng, "Stone_Dark", moss=None)
    # nobori laranja/marinho diante do muro
    for s in (-1, 1):
        x, y = X(s * 12.7), PY - 3.6
        mb.box((0.5, 0.5, 13.0), (x, y, T + 6.5), (0, 0, 0), blk, 0.05)
        mb.box((3.0, 0.35, 0.35), (x - s * 1.3, y, T + 12.4), (0, 0, 0), blk, 0.0)
        mb.box((2.3, 0.22, 8.2), (x - s * 1.35, y, T + 8.1), (0, 0, 0), "P_Naruto_Orange", 0.02)
        mb.box((0.35, 0.26, 8.2), (x - s * 2.35, y, T + 8.1), (0, 0, 0), tl, 0.0)
        mb.cyl(0.62, 0.3, (x - s * 1.35, y - 0.15, T + 9.6), (D(90), 0, 0), tl, 10, bevel=0.0)
        col_box(A, (0.7, 0.7, 13.0), (x, y, T + 6.5))
    for s in (-1, 1):
        col_box(A, (2.6, 2.6, 25.0), (X(s * 9.6), PY, T + 13.3))
    PT.stairs_naruto(mb, px, rng)
    swirl("Naruto", px, "P_Naruto_Swirl", mb, "Stone_Dark", rim_y=-1.0)
    mb.finish()


# ================================================================== 2 DRAGON BALL
def flame(w, h):
    return [(-w / 2, 0.0), (-w * 0.28, h * 0.42), (-w * 0.46, h * 0.72), (-w * 0.08, h * 0.58), (0.0, h),
            (w * 0.16, h * 0.55), (w * 0.44, h * 0.8), (w * 0.3, h * 0.36), (w / 2, 0.0)]


def dragonball(rng):
    px = L.PORTAL_X[1]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_DragonBall_Ring", C, rng, vcap=2)
    W, O, G, E = "P_DB_White", "P_DB_Orange", "P_DB_Gold", "P_DB_Energy_Glow"
    # dais-capsula em 3 niveis (branco + faixas laranja/azul) com aneis de energia no topo
    ca = (px, Y0 + 0.2 + 11.4)
    cb = (px, PY + 0.4)
    mb.cyl(11.4, 1.1, (ca[0], ca[1], T + 0.05), (0, 0, 0), W, 28, bevel=0.1)
    mb.cyl(11.58, 0.34, (ca[0], ca[1], T + 0.1), (0, 0, 0), O, 32, bevel=0.0)
    mb.cyl(8.3, 0.8, (cb[0], cb[1], T + 1.0), (0, 0, 0), W, 24, bevel=0.08)
    mb.cyl(8.46, 0.24, (cb[0], cb[1], T + 0.95), (0, 0, 0), "P_DB_Blue", 28, bevel=0.0)
    mb.cyl(6.3, 0.8, (cb[0], cb[1], T + 1.8), (0, 0, 0), W, 20, bevel=0.08)
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
    for a in (0, 90):
        mb.ico(1.05, (px + math.cos(D(a)) * 11.25, PY, SZ + math.sin(D(a)) * 11.25), G, 2)
    # capsulas-pilone nos lados
    for s in (-1, 1):
        x = X(s * 10.9)
        mb.cyl(2.1, 5.2, (x, PY, T + 0.6 + 2.6), (0, 0, 0), W, 14, bevel=0.1)
        mb.ico(2.1, (x, PY, T + 5.8), W, 2, (1, 1, 0.8))
        mb.cyl(2.2, 0.7, (x, PY, T + 2.4), (0, 0, 0), O, 16, bevel=0.0)
        mb.cyl(2.2, 0.35, (x, PY, T + 4.3), (0, 0, 0), "P_DB_Blue", 16, bevel=0.0)
        col_box(A, (4.2, 4.2, 7.5), (x, PY, T + 3.75))
    # barbatana curva (crescente) so do lado direito: o esquerdo e do dragao (silhueta assimetrica)
    n = 10
    outer = bezier((10.2, 6.0), (13.0, 8.6), (13.4, 17.5), (11.4, 23.0), n)
    inner = bezier((10.7, 8.4), (12.0, 11.5), (12.2, 17.2), (11.4, 23.0), n)
    pts = [(p.x, p.y) for p in outer] + [(p.x, p.y) for p in reversed(inner[:-1])]
    K.plate(mb, pts, V(px, PY + 1.75, T), (1, 0, 0), (0, 0, 1), 1.1, W)
    st = [(outer[i].x * 0.7 + inner[i].x * 0.3, outer[i].y * 0.7 + inner[i].y * 0.3) for i in range(1, n)]
    st += [(outer[i].x * 0.35 + inner[i].x * 0.65, outer[i].y * 0.35 + inner[i].y * 0.65) for i in range(n - 1, 0, -1)]
    K.plate(mb, st, V(px, PY + 1.05, T), (1, 0, 0), (0, 0, 1), 0.4, O)
    # aura de ki em VOLUME (loft afunilado de 1.3 na base) subindo pela frente da base do aro
    for a in (200, 216, 232, 248, 292, 308, 324, 340):
        rad = V(math.cos(D(a)), 0, math.sin(D(a)))
        base = V(px, PY - 1.55, SZ) + rad * (R + 0.2)
        up = (rad + V(0, 0, 1.6)).normalized()
        side = V(up.z, 0, -up.x) * (1 if math.cos(D(a)) > 0 else -1)
        K.ki_flame(mb, base, up, side, rng.uniform(3.0, 4.6), 1.7, 1.3, E, bend=0.2)

    # dragao verde (Shenlong): o CORPO inteiro enrola POR TRAS do aro e do halo (y >= PY+2.25+raio: nao tapa a
    # moldura para quem chega, so aparece por fora do halo); so as garras e a cabeca vem para a frente, a cabeca
    # no alto, acima do aro, de frente para quem chega
    DG = "P_DB_Dragon"
    nb = 57
    ntot = nb + 3
    rad_of = [0.32 + 1.2 * min(1.0, (i / (ntot - 1)) / 0.45) ** 0.8 for i in range(ntot)]
    body = []
    for i in range(nb):
        t = i / (nb - 1)
        a = D(262 - 166 * t)
        rr = 11.6 + 0.35 * math.sin(t * math.pi * 3)
        x = math.cos(a) * rr
        body.append(V(px + x, PY + 2.25 + rad_of[i], SZ + math.sin(a) * rr))
    last = body[-1]
    path = body + [last + V(0.6, -2.4, 2.0), last + V(1.0, -4.6, 3.2), last + V(1.1, -6.0, 3.6)]
    K.taper_tube(mb, path, rad_of, DG, 7, up=(0, 1, 0))
    for i in range(5, len(path) - 4, 4):
        p = path[i]
        out = (p - V(px, p.y, SZ)).normalized()
        dv = (out * 0.35 + V(0, 0.8, 0.45)).normalized()     # cristas para tras/cima: nao alargam o lote
        K.cone(mb, p + dv * rad_of[i] * 0.6, p + dv * (rad_of[i] + 1.1), rad_of[i] * 0.42, 0.0, O, 4)
    # garras: saem do corpo (por tras), contornam o halo por fora e agarram a face da frente do aro dourado
    for i in (14, 38):
        p = path[i]
        rv = (p - V(px, p.y, SZ))
        rv.y = 0.0
        rv.normalize()
        q0 = V(px, PY + 1.35, SZ) + rv * 12.9       # contorna o halo por fora (r 11.9) sem encostar
        q1 = V(px, PY - 1.35, SZ) + rv * 12.9
        q2 = V(px, PY - 1.7, SZ) + rv * 11.3
        q3 = V(px, PY - 1.9, SZ) + rv * 10.4 + V(0, 0, -0.3)
        K.taper_tube(mb, [p, q0, q1, q2, q3], [0.55, 0.48, 0.42, 0.3, 0.1], DG, 6)
        for d in (-0.5, 0.5):
            tang = V(-rv.z, 0, rv.x)
            K.cone(mb, q3 + tang * d, q3 + tang * d - rv * 0.7 + V(0, -0.2, 0), 0.14, 0.0, "P_DB_White", 3)
    H = path[-1]
    hs = 1.3
    fwd = V(0, -1, -0.28).normalized() * hs
    up = (V(0, 0, 1) - V(0, -1, -0.28).normalized() * V(0, -1, -0.28).normalized().z).normalized() * hs
    side = fwd.normalized().cross(up.normalized()) * hs
    mb.beam(H - fwd * 0.6, H + fwd * 2.2, 2.6 * hs, 2.3 * hs, DG, 0.3)                          # cranio
    mb.beam(H + fwd * 1.9 + up * 0.15, H + fwd * 4.9 - up * 0.1, 1.9 * hs, 1.3 * hs, DG, 0.25)  # focinho
    mb.beam(H + fwd * 1.5 - up * 1.2, H + fwd * 4.3 - up * 2.2, 1.6 * hs, 0.5 * hs, DG, 0.1)    # mandibula aberta
    mb.beam(H + fwd * 2.0 - up * 0.55, H + fwd * 4.2 - up * 0.9, 1.3 * hs, 0.4 * hs, "P_DB_Star", 0.0)   # boca
    for s in (-1, 1):
        mb.ico(0.38 * hs, H + fwd * 2.05 + up * 0.8 + side * s * 1.05, "P_DB_Star", 1)
        mb.beam(H + fwd * 1.4 + up * 1.2 + side * s * 0.6, H + fwd * 2.6 + up * 1.0 + side * s * 1.2, 0.5 * hs,
                0.35 * hs, DG, 0.0)
        K.cone(mb, H + fwd * 4.5 - up * 0.55 + side * s * 0.5, H + fwd * 4.6 - up * 1.4 + side * s * 0.5, 0.2 * hs, 0.0,
               W, 4)
        hb = H + up * 1.0 + side * s * 0.75
        k1 = hb - fwd * 1.3 + up * 1.3 + side * s * 0.4
        K.taper_tube(mb, [hb, k1, hb - fwd * 3.0 + up * 2.3 + side * s * 1.0], [0.38 * hs, 0.26 * hs, 0.05], W, 6)
        K.taper_tube(mb, [k1, k1 + up * 1.2 + side * s * 0.5 + fwd * 0.2], [0.18 * hs, 0.04], W, 5)
        wb = H + fwd * 4.4 + side * s * 0.85
        K.taper_tube(mb, [wb, wb + side * s * 1.4 - fwd * 0.4 + up * 0.5, wb + side * s * 2.6 - fwd * 2.4 - up * 0.4,
                          wb + side * s * 3.2 - fwd * 4.4 - up * 1.9], [0.2, 0.16, 0.12, 0.05], W, 5)
    for k in range(5):
        p = H - fwd * (0.5 + k * 0.85) + up * 1.05
        K.cone(mb, p, p + up * (1.2 - k * 0.12) - fwd * 0.7, 0.34 * hs, 0.0, O, 4)

    # halo orbital inclinado acima do aro (as 7 esferas sobem pela escada, em pedestais - fm_portal_terrace)
    tl = D(12)
    cc, Ro = V(px, PY + 1.0, T + 32.0), 8.2
    uu, vv = V(1, 0, 0), V(0, math.cos(tl), math.sin(tl))
    K.ring(mb, cc, Ro, uu, vv, 0.5, 0.5, "P_DB_Blue", 0, 360, n=36)
    for a in (40, 160, 280):
        mb.ico(0.7, cc + (uu * math.cos(D(a)) + vv * math.sin(D(a))) * Ro, "P_DB_Ball", 1)
    # capsula gigante (brinquedo) meio enterrada no canto do pad
    PT.capsule(mb, (X(10.2), Y0 + 4.0, T + 0.7), D(55), 1.0)
    col_box(A, (4.4, 3.0, 2.4), (X(10.2), Y0 + 4.0, T + 1.2), (0, 0, D(55)))
    for s in (-1, 1):
        col_box(A, (2.6, 3.0, 17.0), (X(s * 9.6), PY, T + 10.5))
    PT.stairs_db(mb, px, rng)
    swirl("DragonBall", px, "P_DB_Swirl", mb, G, rim_y=-1.35)
    mb.finish()


# ================================================================== 3 SHADOW GARDEN (porta de catedral gotica)
def gothic_half(hw, z0, cz, r, arc_left, n=14):
    """metade esquerda (u<0) da parede da porta: retangulo ate a nascenca + ogiva (arc_left: pontos (u,z) da
    nascenca ate o apice), menos o furo circular do disco"""
    circ = [(math.cos(D(270 - 180 * i / n)) * r, cz + math.sin(D(270 - 180 * i / n)) * r) for i in range(n + 1)]
    return [(-hw, z0), (0.0, z0)] + circ + list(reversed(arc_left))


def shadow(rng):
    px = L.PORTAL_X[2]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_ShadowGarden_Gothic", C, rng, vcap=2)
    st, tr, gl, ir = "P_Shadow_Stone", "P_Shadow_Trim", "P_Shadow_Glow", "Metal_Dark"
    pc = PY + 1.5   # dais recuado 1.5
    K.flag_floor(mb, [(X(-11.6), Y0 + 0.2), (X(11.6), Y0 + 0.2), (X(11.6), pc - 9.0), (X(-11.6), pc - 9.0)], T - 0.3,
                 rng, st, tr, tile=3.5, h=0.4, bevel=0.0, base_m=tr, mix=0.4)
    # dais octogonal em 3 niveis com filetes de luz
    mb.cyl(11.8, 1.3, (px, pc, T - 0.05), (0, 0, D(22.5)), tr, 8, bevel=0.2)
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
    ts = 1    # lado da agulha alta (virado para o centro do terraco)
    tops = {}
    for s, ptop in ((ts, 19.0), (-ts, 16.2)):
        x = X(s * (hw + 1.2))
        mb.box((4.4, 4.8, 1.4), (x, PY, T + 1.3), (0, 0, 0), tr, 0.15)
        mb.box((3.4, 3.8, ptop - 2.0), (x, PY, T + 2.0 + (ptop - 2.0) / 2), (0, 0, 0), st, 0.2)
        if s != ts:     # o pilar da corrente helicoidal fica liso (a corrente abraca o fuste)
            for zz in (T + 5.0, T + 13.4):
                mb.box((3.8, 4.2, 0.6), (x, PY, zz), (0, 0, 0), tr, 0.08)
        # capitel escalonado + misula interna com espinho: a ogiva nasce apoiada nele (z ~ T+9.5..10.5)
        mb.box((4.0, 4.4, 0.5), (x, PY, T + 9.55), (0, 0, 0), tr, 0.08)
        mb.box((4.6, 5.0, 0.6), (x, PY, T + 10.1), (0, 0, 0), tr, 0.1)
        xi = x - s * 1.7
        mb.box((1.5, 3.4, 0.9), (xi - s * 0.6, PY, T + 9.95), (0, 0, 0), st, 0.1)
        K.cone(mb, V(xi - s * 0.7, PY - 1.1, T + 9.5), V(xi - s * 0.95, PY - 1.3, T + 7.7), 0.42, 0.0, st, 4)
        mb.box((4.2, 4.6, 1.0), (x, PY, T + ptop + 0.3), (0, 0, 0), tr, 0.12)
        tops[s] = T + ptop + 0.8
        for sx in (-1, 1):
            for sy in (-1, 1):
                K.cone(mb, V(x + sx * 1.8, PY + sy * 2.0, T + ptop + 0.8), V(x + sx * 2.2, PY + sy * 2.4, T + ptop + 3.0),
                       0.35, 0.0, ir, 4)
    xl = X(ts * (hw + 1.2))
    SP = 22.0
    mb.box((3.6, 4.0, 3.2), (xl, PY, tops[ts] + 1.6), (0, 0, 0), st, 0.15)
    K.plate(mb, [(-1.3, 0), (1.3, 0), (1.3, 1.6), (0, 2.8), (-1.3, 1.6)], V(xl, PY - 2.0, tops[ts] + 0.4),
            (1, 0, 0), (0, 0, 1), 0.3, gl)
    frustum(mb, (xl, PY, tops[ts] + 3.2), 3.4, 3.8, 0.25, 0.25, SP, st)
    for sx in (-1, 1):
        frustum(mb, (xl + sx * 2.2, PY, tops[ts] + 3.2), 1.2, 1.2, 0.1, 0.1, 8.0, st)
        frustum(mb, (xl, PY + sx * 2.3, tops[ts] + 3.2), 1.0, 1.0, 0.1, 0.1, 5.6, st)
    for k in range(6):
        z = tops[ts] + 5.5 + k * 3.2
        f = (z - tops[ts] - 3.2) / SP
        hwz = 1.7 * (1 - f) + 0.12
        for sx in (-1, 1):
            p = V(xl + sx * hwz, PY - 1.0 * (1 - f), z)
            K.cone(mb, p, p + V(sx * 0.9, 0, 0.7), 0.28, 0.0, st, 4)
    xr = X(-ts * (hw + 1.2))
    frustum(mb, (xr, PY, tops[-ts]), 3.2, 3.6, 0.3, 0.3, 11.0, st)
    # arcobotante PARA TRAS (profundidade de catedral sem sair do lote): contraforte atras do pilar da agulha
    bx, by = xl, PY + 9.8
    mb.box((2.4, 2.8, 9.0), (bx, by, T + 4.5), (0, 0, 0), st, 0.15)
    mb.box((3.0, 3.4, 1.0), (bx, by, T + 0.5), (0, 0, 0), tr, 0.1)
    frustum(mb, (bx, by, T + 9.0), 2.2, 2.6, 0.15, 0.15, 5.0, st)
    fb = bezier(V(xl, PY + 1.9, T + 17.2), V(xl, PY + 4.2, T + 17.4), V(xl, by - 1.9, T + 13.5), V(bx, by - 1.4, T + 9.2), 10)
    mb.sweep(fb, [(-0.7, -0.8), (0.7, -0.8), (0.7, 0.8), (-0.7, 0.8)], st, True, up=(1, 0, 0))
    for p in fb[2:-1:2]:
        K.cone(mb, p + V(0, 0, 0.6), p + V(0, 0.3, 2.0), 0.3, 0.0, st, 4)
    col_box(A, (2.6, 3.0, 9.0), (bx, by, T + 4.5))

    # arco ogival com crochets e tracado de luz por dentro; nasce sobre os capiteis
    rr = hw * 1.55
    a_top = math.acos((rr - hw) / rr)
    tip_z = SZ - 1.0 + rr * math.sin(a_top)
    arc_left = None
    for side in (-1, 1):
        cx = px - side * (rr - hw)
        a0 = 0.0 if side > 0 else math.pi
        arcp, inner = [], []
        for i in range(13):
            t = i / 12
            ang = (a0 + a_top * t) if side > 0 else (a0 - a_top * t)
            arcp.append(V(cx + math.cos(ang) * rr, PY, SZ - 1.0 + math.sin(ang) * rr))
            inner.append(V(cx + math.cos(ang) * (rr - 2.1), PY - 1.3, SZ - 1.0 + math.sin(ang) * (rr - 2.1)))
        if side < 0:
            arc_left = [(p.x - px, p.z) for p in arcp]
        mb.sweep(arcp, [(-1.5, -1.3), (1.5, -1.3), (1.5, 1.3), (-1.5, 1.3)], st, True, up=(0, 1, 0))
        mb.sweep(inner[1:-1], [(-0.22, -0.22), (0.22, -0.22), (0.22, 0.22), (-0.22, 0.22)], gl, True, up=(0, 1, 0))
        for i in range(2, 12, 2):
            p = arcp[i]
            out = V(p.x - cx, 0, p.z - (SZ - 1.0)).normalized()
            K.cone(mb, p + out * 1.3, p + out * 2.8 + V(0, 0, 0.9), 0.42, 0.0, st, 4)
    # PAREDE DA PORTA atras do disco (timpano + jambas): a ogiva deixa de ser moldura vazia e le como portal de
    # catedral; o disco fica num furo com moldura (anel apoiado na parede, que apoia no dais e nos pilares)
    left = gothic_half(hw, T + 1.4, SZ, 8.1, arc_left)
    right = [(-u, z) for (u, z) in reversed(left)]
    for poly in (left, right):
        K.plate(mb, poly, V(px, PY + 1.0, 0.0), (1, 0, 0), (0, 0, 1), 1.0, tr)
    K.ring(mb, V(px, PY + 0.6, SZ), 7.9, (1, 0, 0), (0, 0, 1), 0.8, 1.6, st, n=32)
    # rosacea pequena no timpano + cravos de ferro na moldura
    rc = V(px, PY + 0.35, T + 21.5)
    mb.cyl(1.15, 0.3, rc, (D(90), 0, 0), gl, 12, bevel=0.0)
    K.ring(mb, rc + V(0, -0.1, 0), 1.3, (1, 0, 0), (0, 0, 1), 0.3, 0.5, st, n=16)
    for k in range(3):
        mb.box((2.3, 0.3, 0.16), rc + V(0, -0.22, 0), (0, D(60 * k), 0), st, 0.0)
    for k in range(12):
        a = D(k * 30 + 15)
        mb.box((0.4, 0.3, 0.4), (px + math.cos(a) * 7.9, PY - 0.3, SZ + math.sin(a) * 7.9), (0, -a, 0), ir, 0.0)
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

    # correntes: agulha -> medalhao, pilar esquerdo -> argola no chao, helice colada ao fuste do pilar da agulha
    K.chain(mb, (xl - ts * 1.2, PY - 2.2, T + 21.5), mc + V(ts * 2.6, -0.8, -0.6), sag=2.2, link=0.85, m=ir, t=0.22,
            w=0.55)
    anc = V(X(-ts * 12.2), Y0 + 6.5, T)
    mb.cyl(0.9, 1.5, anc + V(0, 0, 0.75), (0, 0, 0), tr, 8, bevel=0.1)
    K.ring(mb, anc + V(0, 0, 1.9), 0.55, (1, 0, 0), (0, 0, 1), 0.2, 0.2, ir, n=10)
    K.chain(mb, (xr - ts * 1.4, PY - 2.0, T + 15.5), anc + V(0, 0, 2.3), sag=1.2, link=0.85, m=ir, t=0.22, w=0.55)
    col_box(A, (1.8, 1.8, 2.2), (anc.x, anc.y, T + 1.1))
    K.helix_chain(mb, V(xl, PY, 0), 1.7, 1.9, T + 2.4, T + 8.8, 3.2, ir, link=0.8, t=0.2, w=0.5, off=0.25)
    # estandarte rasgado pendurado na frente do pilar esquerdo (fora do capitel)
    bnr = V(xr, PY - 2.75, T + 15.0)
    mb.box((3.6, 0.3, 0.3), bnr + V(0, 0, 0.3), (0, 0, 0), ir, 0.0)
    for sx in (-1, 1):
        mb.box((0.25, 0.9, 0.25), bnr + V(sx * 1.5, 0.45, 0.3), (0, 0, 0), ir, 0.0)
    K.plate(mb, [(-1.5, 0), (1.5, 0), (1.5, -7.2), (1.0, -6.3), (0.4, -7.6), (-0.1, -6.5), (-0.7, -7.8), (-1.1, -6.6),
                 (-1.5, -7.2)], bnr, (1, 0, 0), (0, 0, 1), 0.2, "P_Shadow_Cloth")
    mc2 = bnr + V(0, -0.2, -3.0)
    mini = [(math.cos(D(a)) * 0.9, math.sin(D(a)) * 0.9) for a in range(60, 301, 30)]
    mini += [(0.35 + math.cos(D(a)) * 0.7, math.sin(D(a)) * 0.7) for a in range(250, 105, -30)]
    K.plate(mb, mini, mc2, (1, 0, 0), (0, 0, 1), 0.12, gl)
    # candelabros assimetricos, cristais roxos e grade de ferro com pontas de lanca
    for (dx, y, h) in ((ts * 11.6, Y0 + 4.8, 7.6), (-ts * 11.8, Y0 + 2.4, 5.6)):
        x = X(dx)
        mb.cyl(1.0, 0.5, (x, y, T + 0.25), (0, 0, 0), ir, 8, bevel=0.0)
        mb.cyl(0.28, h, (x, y, T + h / 2), (0, 0, 0), ir, 6, bevel=0.0)
        mb.box((3.0, 0.3, 0.3), (x, y, T + h - 0.8), (0, 0, 0), ir, 0.0)
        for ox, oz in ((-1.4, -0.4), (0.0, 0.2), (1.4, -0.4)):
            mb.cyl(0.45, 0.35, (x + ox, y, T + h - 0.3 + oz), (0, 0, 0), ir, 8, bevel=0.0)
            mb.ico(0.42, (x + ox, y, T + h + 0.3 + oz), gl, 1, (1, 1, 1.8))
        col_box(A, (1.4, 1.4, h), (x, y, T + h / 2))
    crystal_cluster(mb, (X(ts * 11.4), PY + 4.8, T + 0.4), 1.3, gl, rng, 4)
    crystal_cluster(mb, (X(ts * 9.4), PY + 8.4, T + 0.4), 1.0, gl, rng, 3)
    crystal_cluster(mb, (X(-ts * 11.6), PY + 6.0, T + 0.4), 1.0, gl, rng, 3)
    for s in (-1, 1):
        for k in range(7):
            x = X(s * (6.3 + k * 0.85))
            mb.box((0.22, 0.22, 3.2), (x, Y0 + 1.0, T + 1.6), (0, 0, 0), ir, 0.0)
            K.cone(mb, V(x, Y0 + 1.0, T + 3.2), V(x, Y0 + 1.0, T + 4.1), 0.24, 0.0, ir, 4)
        for z in (T + 0.8, T + 2.7):
            mb.box((5.6, 0.2, 0.28), (X(s * 8.85), Y0 + 1.0, z), (0, 0, 0), ir, 0.0)
        col_box(A, (5.6, 0.6, 4.0), (X(s * 8.85), Y0 + 1.0, T + 2.0))
    col_box(A, (3.6, 4.0, 45.0), (xl, PY, T + 22.5))
    col_box(A, (3.6, 4.0, 28.0), (xr, PY, T + 14.0))
    PT.stairs_shadow(mb, px, rng)
    swirl("ShadowGarden", px, "P_Shadow_Swirl", mb, st, rim_y=-0.6)
    mb.finish()


# ================================================================== 4 DEMON SLAYER (portao-santuario largo e baixo)
def _kara_front(x):
    """cota da beira frontal do karahafu: sino no centro (arco que sobe) + ponta levemente erguida nas quinas"""
    u = abs(x) / 7.2
    z = 21.6
    if u < 1.0:
        z += 3.6 * (1.0 - u * u) ** 1.5
    if abs(x) > 10.0:
        z += 0.9 * ((abs(x) - 10.0) / 4.0) ** 2
    return T + z


def _kara_ridge(x):
    u = abs(x) / 7.2
    z = 26.3 + 0.5 * (abs(x) / 14.0) ** 2
    if u < 1.0:
        z += 0.8 * (1.0 - u * u)
    return T + z


def _kara_back(x):
    z = 21.8
    if abs(x) > 10.0:
        z += 0.9 * ((abs(x) - 10.0) / 4.0) ** 2
    return T + z


def demonslayer(rng):
    px = L.PORTAL_X[3]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_DemonSlayer_Gate", C, rng, vcap=2)
    ch, bl, gl, tile, chk, wis = "P_DS_Char", "P_DS_Blood", "P_DS_Glow", "P_DS_Tile", "P_DS_Checker", "P_DS_Wisteria"
    pc = PY - 2.0   # plataforma avancada 2
    K.flag_floor(mb, [(X(-11.6), Y0 + 0.2), (X(11.6), Y0 + 0.2), (X(11.6), pc - 6.0), (X(-11.6), pc - 6.0)], T - 0.3,
                 rng, "Stone_Dark", ch, tile=3.4, h=0.4, bevel=0.0, base_m=bl, mix=0.3)

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

    # 4 esteios de madeira carbonizada: os da frente sao largos e levam o painel ichimatsu (verde/preto)
    zf = T + 1.6
    zt = T + 20.0
    yb = PY + 4.4
    for s in (-1, 1):
        x = X(s * 11.2)
        mb.box((2.8, 1.8, zt - zf), (x, PY, (zf + zt) / 2), (0, 0, 0), ch, 0.1)
        mb.box((3.4, 2.4, 1.0), (x, PY, zf + 0.5), (0, 0, 0), "Stone_Dark", 0.12)
        for zz in (T + 2.7, T + 13.5):
            mb.box((2.9, 1.9, 0.35), (x, PY, zz), (0, 0, 0), bl, 0.0)
        for i in range(2):
            for j in range(8):
                if (i + j) % 2 == 0:
                    mb.box((1.18, 0.2, 1.18), (x - 0.6 + i * 1.2, PY - 0.95, T + 3.5 + j * 1.2), (0, 0, 0), chk, 0.0)
        mb.box((1.6, 1.6, zt - zf), (x, yb, (zf + zt) / 2), (0, 0, 0), ch, 0.08)
        mb.box((2.2, 2.2, 1.0), (x, yb, zf + 0.5), (0, 0, 0), "Stone_Dark", 0.1)
        mb.box((1.2, yb - PY, 0.9), (x, (PY + yb) / 2, T + 8.0), (0, 0, 0), ch, 0.05)        # nuki lateral
        mb.box((1.3, yb - PY + 1.6, 1.0), (x, (PY + yb) / 2, zt + 0.5), (0, 0, 0), ch, 0.06)  # viga lateral
        # misulas (tokyo) que levam o beiral para a frente
        mb.beam(V(x, PY - 0.9, zt - 1.2), V(x, PY - 3.0, zt + 0.9), 0.9, 0.8, ch, 0.05)
        col_box(A, (2.8, 1.8, zt - zf), (x, PY, (zf + zt) / 2))
        col_box(A, (1.6, 1.6, zt - zf), (x, yb, (zf + zt) / 2))
    # vigas de cabeca (kashiragi) ACIMA do aro: nada cruza o disco
    for y in (PY, yb):
        mb.box((25.4, 1.2, 1.0), (px, y, zt + 0.5), (0, 0, 0), ch, 0.08)
    mb.box((25.6, 0.3, 0.3), (px, PY - 0.62, zt + 0.1), (0, 0, 0), bl, 0.0)

    # telhado KARAHAFU de telha preta: beira frontal ondulada (sobe em arco no centro), largo e baixo
    yr = PY + 2.2
    xs = [-14.0 + i for i in range(29)]
    rpts, profs = [], []
    for x in xs:
        zf_, zr_, zb_ = _kara_front(x), _kara_ridge(x), _kara_back(x)
        bf, bb = yr - (PY - 3.2), yr - (PY + 8.2)
        rpts.append(V(X(x), yr, 0.0))
        profs.append([(zf_, bf), (zr_, 0.0), (zb_, bb), (zb_ - 0.8, bb + 0.3), (zr_ - 0.95, 0.0), (zf_ - 0.8, bf - 0.3)])
    K.loft(mb, rpts, profs, tile, True, up=(0, 0, 1))
    # frisos de telha (canais) no pano da frente
    for x in xs[1:-1:2]:
        zf_, zr_ = _kara_front(x), _kara_ridge(x)
        a, b = V(X(x), PY - 3.0, zf_ + 0.12), V(X(x), yr - 0.4, zr_ + 0.02)
        mb.beam(a, b, 0.32, 0.22, tile, 0.0)
    # cumeeira + onigawara nas pontas
    mb.sweep([V(X(x), yr, _kara_ridge(x) + 0.2) for x in xs[1:-1]],
             [(-0.5, -0.45), (0.5, -0.45), (0.5, 0.45), (-0.5, 0.45)], ch, True, up=(0, 0, 1))
    for s in (-1, 1):
        mb.box((1.0, 1.8, 1.6), (X(s * 13.4), yr, _kara_ridge(13.4) + 0.7), (0, 0, 0), ch, 0.1)
    # hafu (tabua do frontao) seguindo a beira ondulada, com filete vermelho-sangue por baixo
    hf = [V(X(x), PY - 3.25, _kara_front(x) - 0.35) for x in [-13.8 + 27.6 * i / 34 for i in range(35)]]
    mb.sweep(hf, [(-0.55, -0.25), (0.55, -0.25), (0.55, 0.25), (-0.55, 0.25)], ch, True, up=(0, 1, 0))
    mb.sweep([p + V(0, 0.05, -0.62) for p in hf], [(-0.12, -0.2), (0.12, -0.2), (0.12, 0.2), (-0.12, 0.2)], bl, True,
             up=(0, 1, 0))
    # frontao sob o arco (painel vermelho-sangue) com a mascara oni pequena
    fr = [(x, _kara_front(x) - 0.75) for x in [-5.6 + 11.2 * i / 12 for i in range(13)]]
    K.plate(mb, [(5.6, T + 21.3)] + list(reversed(fr)) + [(-5.6, T + 21.3)], V(px, PY - 3.0, 0.0), (1, 0, 0), (0, 0, 1),
            0.3, bl)
    mb.box((22.4, 0.5, 0.45), (px, PY - 3.05, T + 21.1), (0, 0, 0), ch, 0.0)   # viga do karahafu sobre as misulas
    O = V(px, PY - 3.4, T + 23.0)
    K.plate(mb, [(-1.3, 1.1), (1.3, 1.1), (1.5, 0.2), (1.0, -1.1), (0.4, -1.6), (-0.4, -1.6), (-1.0, -1.1), (-1.5, 0.2)],
            O, (1, 0, 0), (0, 0, 1), 0.9, bl, bevel=0.05)
    K.plate(mb, [(-1.65, 0.55), (-0.15, 0.05), (0.15, 0.05), (1.65, 0.55), (1.55, 1.25), (-1.55, 1.25)], O + V(0, -0.4, 0),
            (1, 0, 0), (0, 0, 1), 0.35, ch)
    for s in (-1, 1):
        eye = [(s * 1.15, 0.2), (s * 0.28, -0.12), (s * 0.35, 0.18), (s * 1.05, 0.45)]
        if s < 0:
            eye = list(reversed(eye))
        K.plate(mb, eye, O + V(0, -0.5, 0), (1, 0, 0), (0, 0, 1), 0.15, gl)
        K.cone(mb, O + V(s * 0.5, -0.5, -0.8), O + V(s * 0.45, -0.55, -1.5), 0.16, 0.0, "Emblem_Cream", 4)
        hb = O + V(s * 1.1, 0.1, 0.95)
        K.taper_tube(mb, [hb, hb + V(s * 1.0, 0.1, 1.1), hb + V(s * 1.2, 0.2, 2.2)], [0.36, 0.22, 0.04], "Emblem_Cream", 6)
    light("L_DS_Oni", "POINT", tuple(O + V(0, -2.0, 0)), 160, (1.0, 0.25, 0.05), 0.5)

    # aro negro do disco, apoiado num berco e amarrado aos esteios (nao flutua)
    K.ring(mb, V(px, PY, SZ), 8.1, (1, 0, 0), (0, 0, 1), 1.0, 1.1, ch, n=32)
    mb.box((4.4, 1.6, 1.3), (px, PY, T + 2.25), (0, 0, 0), ch, 0.1)
    for s in (-1, 1):
        mb.box((1.6, 0.9, 1.0), (X(s * 9.2), PY, SZ), (0, 0, 0), ch, 0.05)
        mb.box((1.7, 0.95, 0.3), (X(s * 9.2), PY, SZ + 0.4), (0, 0, 0), bl, 0.0)
    # brinco hanafuda como medalhao no topo do aro, pendurado por uma argola apoiada na viga de cabeca (carta
    # clara com moldura negra, sol vermelho e raios pretos em leque subindo da base; abaixo da viga do karahafu)
    hc = V(px, PY - 1.0, SZ + 8.25)
    mb.box((2.4, 0.3, 3.0), hc, (0, 0, 0), "Emblem_Cream", 0.06)
    mb.box((2.7, 0.22, 3.3), hc + V(0, 0.14, 0), (0, 0, 0), ch, 0.0)
    mb.cyl(0.74, 0.2, hc + V(0, -0.2, 0.55), (D(90), 0, 0), gl, 14, bevel=0.0)
    rb = hc + V(0, -0.21, -1.4)
    for a in (-44, -22, 0, 22, 44):
        d = V(math.sin(D(a)), 0, math.cos(D(a)))
        mb.box((0.16, 0.12, 1.1), rb + d * 0.62, (0, D(a), 0), ch, 0.0)
    K.ring(mb, hc + V(0, 0, 1.85), 0.38, (1, 0, 0), (0, 0, 1), 0.14, 0.16, ch, n=10)

    # CORTINA DE GLICINIAS caindo do beiral: faixa de folhagem verde colada sob a beira (a planta) e cachos lilas em
    # 2 fileiras desencontradas, curtos no meio (acima do aro) e longos nos lados (na frente dos esteios)
    for i in range(19):
        x = -12.3 + 24.6 * i / 18        # meia-largura da folha 1.3: fica dentro do lote (px +-14)
        if abs(x) < 2.4:
            continue        # frontao com a mascara oni
        mb.ico(0.9, (X(x), PY - 3.05, _kara_front(x) - 1.0), "Leaf_Pine_Light", 1, (1.45, 0.85, 0.62),
               rot=(0, 0, rng.uniform(-0.3, 0.3)))
    for i in range(33):
        x = -13.4 + 26.8 * i / 32 + rng.uniform(-0.1, 0.1)
        if abs(abs(x) - 11.2) < 1.0 or abs(x) < 1.6:
            continue        # a misula do esteio passa ali (meia-largura 0.45 + raio do cacho); o centro fica livre
            #               para a carta hanafuda
        row = i % 2
        ztop_r = _kara_front(x) - 1.1
        ring_top = (SZ + math.sqrt(max(0.0, 9.0 ** 2 - x * x)) + 0.4) if abs(x) < 9.0 else T + 14.5
        ln = min(rng.uniform(1.8, 3.2) if row else rng.uniform(2.8, 4.6), ztop_r - ring_top)
        if ln < 0.9:
            continue
        K.raceme(mb, V(X(x), PY - 3.35 + 0.55 * row, ztop_r), ln, wis, rng.uniform(0.38, 0.46), rng)
    for s in (-1, 1):
        for x0 in (10.2, 12.2, 13.1):
            x = s * x0
            K.raceme(mb, V(X(x), PY - 2.6, _kara_front(x) - 0.9), rng.uniform(3.4, 5.2), wis, 0.4, rng)
    # lanternas de papel vermelhas sob o beiral, por fora dos esteios (fora do aro)
    for s in (-1, 1):
        x = s * 13.3
        c = K.chochin(mb, (X(x), PY - 1.3, _kara_front(x) - 0.8), r=0.8, h=1.5, paper=gl, cap=ch, hang=1.0, n=8,
                      rod_m=ch)
        light("L_DS_Eave_%d" % (s + 2 if s > 0 else 1), "POINT", tuple(c + V(0, -1.0, 0)), 120, (1.0, 0.3, 0.15), 0.3)
    # toro baixinhos de pedra escura e katanas cravadas no chao na entrada
    for s in (-1, 1):
        K.toro(mb, (X(s * 9.4), Y0 + 2.6, T + 0.1), 0.62, "Stone_Dark", ch, glow=gl, lit=False)
        col_box(A, (1.8, 1.8, 4.2), (X(s * 9.4), Y0 + 2.6, T + 2.1))
        g = V(X(s * 8.2), Y0 + 5.6, T + 6.4)
        K.katana(mb, g, (s * 0.1, 0.06, -1.0), (0, -1, 0), length=8.2, width=0.62, grip_m=ch, guard_m=bl)
        col_box(A, (0.9, 0.9, 6.4), (g.x, g.y, T + 3.2))
    PT.stairs_demonslayer(mb, px, rng)
    swirl("DemonSlayer", px, "P_DS_Swirl", mb, ch, rim_y=-0.62)
    mb.finish()


# ================================================================== 5 ONE PIECE (cais sobre estacas + timao)
def onepiece(rng):
    px = L.PORTAL_X[4]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_OnePiece_Pier", C, rng, vcap=2)
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
            mb.cyl(0.7, 0.4, (x, y, h - 0.7), (0, 0, 0), "Rope", 6, bevel=0.0)
            tops.append(V(x, y, h - 0.7))
            if k in (1, 5):
                K.ring(mb, V(x + s * 0.95, y, T + 1.1), 0.75, (0, 1, 0), (0, 0, 1), 0.42, 0.5, "Metal_Dark", n=8)
                mb.rod((x + s * 0.7, y, T + 1.9), (x + s * 0.95, y, T + 1.8), 0.08, "Rope", 4)
            elif k == 3:
                mb.cyl(0.55, 1.7, (x + s * 1.0, y, T + 1.2), (0, 0, 0), "Rope", 8, bevel=0.0)
                mb.rod((x + s * 1.0, y, T + 2.0), (x + s * 0.4, y, h - 0.8), 0.08, "Rope", 4)
        for a_, b_ in zip(tops, tops[1:]):
            mb.tube([a_ + (b_ - a_) * t - V(0, 0, 0.9 * 4 * t * (1 - t)) for t in (0, 0.25, 0.5, 0.75, 1.0)], 0.13,
                    "Rope", 4)
        col_box2(A, (X(s * 11.9) - 0.7, y0, T), (X(s * 11.9) + 0.7, y1, zd + 2.2))
    # plataforma de cabrestante em 2 niveis
    mb.cyl(8.6, 1.0, (px, PY, zd + 0.5), (0, 0, 0), "Wood_Dark", 20, bevel=0.15)
    mb.cyl(6.6, 0.8, (px, PY, zd + 1.4), (0, 0, 0), "Wood_Plank", 20, bevel=0.12)
    for k in range(10):
        a = D(k * 36)
        mb.box((0.35, 0.35, 1.05), (px + math.cos(a) * 8.62, PY + math.sin(a) * 8.62, zd + 0.5), (0, 0, a), "Metal_Dark", 0.0)
    col_disc(px, PY, 8.6, zd - 1.5, zd + 1.0)
    col_disc(px, PY, 6.6, zd - 1.5, zd + 1.8)

    # TIMAO: aro interno fino (r8.2) e aro externo fino (r12.5, secao 0.9) com VAO ABERTO entre eles; raios
    # torneados cruzam o vao e saem como punhos alem do aro externo; cravos de latao nos cruzamentos.
    # O aro externo mergulha no cabrestante embaixo (roda montada no conves)
    Ri, Ro = 8.2, 12.5
    ringi = [V(px + math.cos(D(a)) * Ri, PY, SZ + math.sin(D(a)) * Ri) for a in range(0, 361, 9)]
    mb.sweep(ringi, [(-0.45, -0.55), (0.45, -0.55), (0.45, 0.55), (-0.45, 0.55)], "Wood_Light", True, up=(0, 1, 0))
    a_cut = math.degrees(math.asin((T + 1.2 - SZ) / Ro))       # abaixo disso o aro fica enterrado no cabrestante
    arc0, arc1 = a_cut, 180.0 - a_cut                             # a_cut < 0: de -53 ate 233 graus
    nseg = 40
    ringo = [V(px + math.cos(D(arc0 + (arc1 - arc0) * i / nseg)) * Ro, PY,
               SZ + math.sin(D(arc0 + (arc1 - arc0) * i / nseg)) * Ro) for i in range(nseg + 1)]
    mb.sweep(ringo, [(-0.45, -0.45), (0.45, -0.45), (0.45, 0.45), (-0.45, 0.45)], "Wood_Light", True, up=(0, 1, 0))
    for k in range(8):
        a = D(k * 45 + 22.5)
        if math.sin(a) < -0.6:
            continue
        rv = V(math.cos(a), 0, math.sin(a))
        c0 = V(px, PY, SZ)
        prof = [(7.6, 0.34), (8.6, 0.46), (9.6, 0.36), (10.4, 0.52), (11.4, 0.36), (12.9, 0.34), (13.3, 0.5), (13.8, 0.46),
                (14.1, 0.2)]
        K.taper_tube(mb, [c0 + rv * r for r, _ in prof], [w for _, w in prof], "Wood_Light", 7, up=(0, 1, 0))
        for rr in (Ri, Ro):
            mb.cyl(0.36, 0.3, c0 + rv * rr + V(0, -0.62, 0), (D(90), 0, 0), "Metal_Brass", 6, bevel=0.0)
    # caveira com ossos cruzados pousada no alto do aro externo
    S = V(px, PY - 1.0, T + 25.6)
    for s in (-1, 1):
        mb.beam(S + V(-s * 2.8, 0.4, -2.4), S + V(s * 2.8, 0.4, 1.6), 0.7, 0.7, "Emblem_Cream", 0.1)
        for e in (S + V(-s * 2.8, 0.4, -2.4), S + V(s * 2.8, 0.4, 1.6)):
            for o in (-0.4, 0.4):
                mb.ico(0.5, e + V(o, 0, o * s), "Emblem_Cream", 1)
    mb.ico(2.0, S, "Emblem_Cream", 2, (1.0, 0.85, 0.95))
    mb.box((2.2, 1.4, 1.1), S + V(0, -0.2, -1.7), (0, 0, 0), "Emblem_Cream", 0.3)
    for s in (-1, 1):
        mb.ico(0.52, S + V(s * 0.74, -1.55, 0.15), "Metal_Dark", 1, (1, 0.5, 1.15))
    K.cone(mb, S + V(0, -1.66, -0.65), S + V(0, -1.8, -0.2), 0.28, 0.0, "Metal_Dark", 3)
    for k in range(3):
        mb.box((0.34, 0.2, 0.56), S + V(-0.48 + k * 0.48, -0.94, -2.0), (0, 0, 0), "Metal_Dark", 0.0)
    # ancora grande em pe no canto da frente (dentro do lote), corrente ate a estaca
    ax, ay = X(-9.2), Y0 + 4.4
    im = "Metal_Dark"
    sa = 0.85
    mb.box((1.0 * sa, 1.0 * sa, 10.2 * sa), (ax, ay, zd + 5.5 * sa), (0, 0, 0), im, 0.12)
    mb.box((5.4 * sa, 0.9 * sa, 0.9 * sa), (ax, ay, zd + 9.6 * sa), (0, 0, 0), im, 0.1)
    for s in (-1, 1):
        mb.ico(0.5, (ax + s * 2.7 * sa, ay, zd + 9.6 * sa), im, 1)
    K.ring(mb, V(ax, ay, zd + 11.2 * sa), 0.9, (1, 0, 0), (0, 0, 1), 0.34, 0.34, im, n=14)
    arcp = [V(ax + math.cos(D(a)) * 3.0 * sa, ay, zd + 3.6 * sa + math.sin(D(a)) * 2.7 * sa) for a in range(195, 346, 15)]
    mb.tube(arcp, 0.5 * sa, im, 8)
    for s, p in ((-1, arcp[0]), (1, arcp[-1])):
        K.plate(mb, [(0, 0), (1.7 * sa, 0.55 * sa), (0.2, 2.3 * sa)], p + V(0, 0, -0.3), (s, 0, 0), (0, 0, 1), 0.45, im)
    K.cone(mb, V(ax, ay, zd + 0.9), V(ax, ay, zd - 0.2), 0.7, 0.1, im, 4)
    K.chain(mb, (ax - 0.8, ay, zd + 10.8 * sa), (X(-11.9), y0 + 0.6 + 1 * 3.5, T + 2.8), sag=1.4, link=0.8, m=im)
    col_box(A, (5.0, 1.4, 10.5), (ax, ay, zd + 5.2))
    # mastro com verga, vela e bandeira pirata ATRAS do timao (a vela espia por tras do aro)
    mx, my = X(10.6), PY + 5.6
    mb.cyl(0.55, 23.0, (mx, my, T + 11.5), (0, 0, 0), "Wood_Dark", 8, r2=0.38, bevel=0.0)
    mb.cyl(1.2, 1.2, (mx, my, T + 17.4), (0, 0, 0), "Wood_Dark", 10, bevel=0.0)
    mb.box((5.0, 0.45, 0.45), (mx, my - 0.6, T + 20.6), (0, 0, 0), "Wood_Dark", 0.05)
    spts, sprof = [], []
    for i in range(7):
        f = i / 6
        spts.append(V(mx, my - 0.8, T + 20.3 - 6.0 * f))
        w = 2.3 - 0.4 * f
        bul = 0.3 + 1.0 * math.sin(math.pi * (0.15 + 0.7 * f))
        front = [(x, bul * (1 - (x / w) ** 2)) for x in [-w + 2 * w * k / 6 for k in range(7)]]
        sprof.append(front + [(x, b - 0.24) for x, b in reversed(front)])
    K.loft(mb, spts, sprof, "P_OP_Sail", True)
    mb.box((3.0, 0.2, 2.0), (mx - 1.6, my, T + 22.2), (0, 0, 0), "Metal_Dark", 0.0)
    mb.ico(0.5, (mx - 1.6, my - 0.2, T + 22.3), "Emblem_Cream", 1, (1, 0.5, 1))
    K.ring(mb, V(mx, my - 0.7, T + 7.0), 1.1, (1, 0, 0), (0, 0, 1), 0.5, 0.5, "P_OP_Red", n=16)
    for k in range(4):
        a = D(k * 90 + 45)
        mb.box((0.5, 0.58, 0.56), (mx + math.cos(a) * 1.1, my - 0.7, T + 7.0 + math.sin(a) * 1.1), (0, -a, 0),
               "Emblem_Cream", 0.0)
    mb.rod((mx, my, T + 22.4), (X(11.9), y0 + 0.6 + 5 * 3.5, T + 1.2), 0.1, "Rope", 4)
    col_box(A, (1.4, 1.4, 23.0), (mx, my, T + 11.5))
    # bau do tesouro aberto, barris, caixotes, rolos de corda
    cx_, cy_ = X(8.8), Y0 + 3.4
    mb.box((3.2, 2.2, 1.8), (cx_, cy_, zd + 0.9), (0, 0, -0.15), "Wood_Plank", 0.12)
    mb.box((3.3, 0.35, 2.0), (cx_ + 0.15, cy_ + 1.2, zd + 2.6), (D(-20), 0, -0.15), "Wood_Plank", 0.1)
    for k in range(6):
        mb.ico(0.42, (cx_ + rng.uniform(-1.1, 1.1), cy_ + rng.uniform(-0.6, 0.6), zd + 1.85), "Metal_Brass", 1)
    mb.box((3.4, 0.3, 0.3), (cx_, cy_ - 1.1, zd + 1.2), (0, 0, -0.15), "Metal_Brass", 0.0)
    col_box(A, (3.6, 2.8, 3.0), (cx_, cy_, zd + 1.5))
    for p in ((X(-6.4), PY + 7.4), (X(9.2), Y0 + 7.8)):
        K.barrel_small(mb, (p[0], p[1], zd), 1.05, 2.5)
        col_box(A, (2.4, 2.4, 2.6), (p[0], p[1], zd + 1.3))
    for (x, y) in ((X(9.4), PY + 2.6), (X(-9.0), PY + 3.0)):
        for k in range(2):
            K.ring(mb, V(x, y, zd + 0.25 + k * 0.42), 1.15 - k * 0.2, (1, 0, 0), (0, 1, 0), 0.5, 0.42, "Rope", n=10)
    K.palm_small(mb, (X(-9.8), PY + 7.4, T), 11.0, rng, frond=4.0, lean=(0.8, 0.4), a0=0.3)
    col_box(A, (1.6, 1.6, 8.0), (X(-9.8), PY + 7.4, T + 4.0))
    PT.stairs_onepiece(mb, px, rng)
    swirl("OnePiece", px, "P_OP_Swirl", mb, "Wood_Dark", rim_y=-0.8)
    mb.finish()


# ================================================================== 6 ONE PUNCH MAN (escuro e contido)
def _tower(mb, x, y, z0, h, w, d, rng, dg, con, win, gl):
    """torre de vidro marinho com quinas de concreto, 1 recuo e tiras finas de janela acesas (andares sorteados)"""
    z = z0
    ww, dd = w, d
    for i, hh in enumerate((h * 0.64, h * 0.36)):
        mb.box((ww, dd, hh), (x, y, z + hh / 2), (0, 0, 0), dg, 0.1)
        for sx in (-1, 1):
            mb.box((0.45, dd + 0.12, hh), (x + sx * ww / 2, y, z + hh / 2), (0, 0, 0), con, 0.0)
        nfl = int((hh - 1.2) / 2.3)
        for k in range(nfl):
            if rng.random() < 0.5:
                zz = z + 1.5 + k * 2.3
                ln = ww * rng.uniform(0.3, 0.62)
                off = rng.uniform(-(ww - ln) / 2 + 0.5, (ww - ln) / 2 - 0.5)
                mb.box((ln, 0.12, 0.26), (x + off, y - dd / 2 - 0.04, zz), (0, 0, 0), win, 0.0)
        mb.box((ww + 0.3, dd + 0.3, 0.4), (x, y, z + hh), (0, 0, 0), con, 0.0)
        z += hh
        ww, dd = ww * 0.74, dd * 0.74
    mb.cyl(0.15, 3.0, (x, y, z + 1.5), (0, 0, 0), "Metal_Dark", 6, bevel=0.0)
    mb.ico(0.3, (x, y, z + 3.1), gl, 1)
    return z


def opm(rng):
    px = L.PORTAL_X[5]

    def X(dx):
        return px + dx
    mb = K.LeanMB("PORTAL_OnePunchMan_City", C, rng, vcap=2)
    con, dg, win, gl, yel, red, dk = ("P_OPM_Concrete", "P_OPM_DarkGlass", "P_OPM_Glass", "P_OPM_Glow", "P_OPM_Yellow",
                                      "P_OPM_Red", "Metal_Dark")
    zp = T + 0.5
    # praca de concreto: placas com juntas, faixa zebrada na borda, frisos neon finos
    mb.box2((X(-11.8), Y0 + 0.2, T - 0.5), (X(11.8), PY + 8.8, zp), con, 0.1)
    for k in range(1, 7):
        mb.box((23.4, 0.16, 0.06), (px, Y0 + 0.2 + k * 3.0, zp + 0.02), (0, 0, 0), dk, 0.0)
    for k in (-2, -1, 1, 2):
        mb.box((0.16, PY + 8.6 - Y0, 0.06), (X(k * 4.7), (Y0 + PY + 8.8) / 2, zp + 0.02), (0, 0, 0), dk, 0.0)
    n = 16
    for i in range(n):
        mb.box((23.2 / n, 0.9, 0.1), (X(-11.6 + 23.2 * (i + 0.5) / n), Y0 + 0.75, zp + 0.03), (0, 0, 0),
               yel if i % 2 else dk, 0.0)
    for s in (-1, 1):
        mb.box((0.25, 11.0, 0.08), (X(s * 10.4), Y0 + 7.0, zp + 0.04), (0, 0, 0), gl, 0.0)
    col_box2(A, (X(-11.8), Y0 + 0.2, T - 1), (X(11.8), PY + 8.8, zp))
    # palco em 2 niveis com friso fino
    sy = PY + 1.0
    mb.box((22.0, 10.0, 0.9), (px, sy, zp + 0.45), (0, 0, 0), con, 0.15)
    mb.box((18.0, 8.0, 0.9), (px, sy, zp + 1.35), (0, 0, 0), con, 0.15)
    mb.box((18.1, 0.2, 0.12), (px, sy - 4.05, zp + 1.6), (0, 0, 0), gl, 0.0)
    mb.box((22.1, 0.2, 0.16), (px, sy - 5.05, zp + 0.7), (0, 0, 0), yel, 0.0)
    col_box(A, (22.0, 10.0, 1.9), (px, sy, zp - 0.05))
    col_box(A, (18.0, 8.0, 2.8), (px, sy, zp + 0.4))
    hw = SWIRL_R + 1.4
    # pilones de metal escuro (base e frisos de concreto) com um so filete neon interno de 0.3
    for s, htop, w in ((-1, 25.0, 4.0), (1, 22.0, 3.6)):
        x = X(s * (hw + 2.0))
        mb.box((w + 1.0, w + 1.6, 1.4), (x, PY, zp + 0.7), (0, 0, 0), con, 0.12)
        mb.box((w, w + 0.6, htop), (x, PY, zp + htop / 2), (0, 0, 0), dk, 0.15)
        for zz in (zp + htop * 0.34, zp + htop * 0.68):
            mb.box((w + 0.16, w + 0.76, 0.5), (x, PY, zz), (0, 0, 0), con, 0.0)
        mb.box((w + 0.3, w + 0.9, 0.6), (x, PY, zp + htop), (0, 0, 0), con, 0.05)
        mb.box((0.3, 0.3, htop - 4.0), (x - s * (w / 2 + 0.06), PY - 0.9, zp + 1.6 + (htop - 4.0) / 2), (0, 0, 0), gl, 0.0)
        col_box(A, (w, w + 0.6, htop), (x, PY, zp + htop / 2))
    # lintel de concreto escuro com filete neon por baixo
    mb.box((2 * hw + 6.0, 3.2, 2.8), (px, PY, T + 23.4), (0, 0, 0), con, 0.3)
    mb.box((2 * hw + 1.6, 0.3, 0.3), (px, PY - 1.45, T + 21.85), (0, 0, 0), gl, 0.0)
    # anel de metal que prende o disco (tirantes ate os pilones e ate o lintel)
    K.ring(mb, V(px, PY + 0.1, SZ), 7.95, (1, 0, 0), (0, 0, 1), 0.9, 1.2, dk, n=36)
    for s in (-1, 1):
        mb.box((1.2, 0.8, 0.8), (X(s * 8.9), PY, SZ), (0, 0, 0), dk, 0.0)
    mb.box((0.8, 0.8, 2.6), (px, PY, SZ + 9.6), (0, 0, 0), dk, 0.0)
    # medalhao amarelo r5 com contorno escuro grosso e punho de luva vermelha
    ez = T + 27.6
    mc = V(px, PY - 2.1, ez)
    mb.cyl(5.0, 0.9, mc, (D(90), 0, 0), yel, 28, bevel=0.1)
    K.ring(mb, mc + V(0, -0.1, 0), 5.35, (1, 0, 0), (0, 0, 1), 0.9, 1.3, dk, n=28)
    f = 1.45
    fc = mc + V(0, -0.9, 0)
    mb.box((3.0 * f, 1.0 * f, 2.0 * f), fc + V(0, -0.2, -0.2 * f), (0, 0, 0), red, 0.3)
    for k in range(4):
        mb.box((0.72 * f, 0.9 * f, 1.0 * f), fc + V((-1.1 + k * 0.73) * f, -0.6, 1.1 * f), (0, 0, 0), red, 0.18)
    mb.box((0.8 * f, 0.8 * f, 1.8 * f), fc + V(1.7 * f, -0.7, -0.1 * f), (0, 0, D(-25)), red, 0.18)
    mb.box((2.2 * f, 1.1 * f, 1.0 * f), fc + V(0, -0.1, -1.6 * f), (0, 0, 0), red, 0.2)
    # skyline contida atras (altura maxima 34 acima do terraco = 1.3x os vizinhos), dentro do lote
    towers = [(-9.2, 8.8, 29.0, 5.0, 4.8), (-3.4, 11.2, 24.0, 4.6, 4.6), (3.3, 9.2, 32.0, 5.8, 5.4),
              (9.7, 7.6, 27.0, 4.6, 4.6)]
    for (dx, dy, h, w, d) in towers:
        x, y = X(dx), PY + dy
        _tower(mb, x, y, T, h, w, d, rng, dg, con, win, gl)
        col_box(A, (w, d, h), (x, y, T + h / 2))
    # totens de holograma e postes urbanos
    for s in (-1, 1):
        x = X(s * 12.6)
        mb.box((1.6, 1.6, 5.0), (x, PY - 5.0, zp + 2.5), (0, 0, 0), con, 0.2)
        mb.box((1.7, 1.7, 0.4), (x, PY - 5.0, zp + 4.2), (0, 0, 0), gl, 0.0)
        mb.box((1.72, 1.72, 0.5), (x, PY - 5.0, zp + 1.0), (0, 0, 0), yel, 0.0)
        col_box(A, (1.6, 1.6, 5.0), (x, PY - 5.0, zp + 2.5))
        # poste urbano com o braco para FORA do lote central (nada cruza a frente do disco)
        lx, ly = X(s * 10.9), Y0 + 2.2
        mb.cyl(0.28, 8.0, (lx, ly, zp + 4.0), (0, 0, 0), dk, 6, bevel=0.0)
        mb.box((2.6, 0.5, 0.35), (lx + s * 1.1, ly, zp + 8.0), (0, 0, 0), dk, 0.0)
        mb.box((1.4, 0.9, 0.4), (lx + s * 2.2, ly, zp + 7.8), (0, 0, 0), dk, 0.0)
        mb.box((1.2, 0.7, 0.12), (lx + s * 2.2, ly, zp + 7.56), (0, 0, 0), gl, 0.0)
        col_box(A, (0.8, 0.8, 8.0), (lx, ly, zp + 4.0))
    PT.stairs_opm(mb, px, rng)
    swirl("OnePunchMan", px, "P_OPM_Swirl", mb, dk, rim_y=-0.6)
    mb.finish()


def build():
    rng = random.Random(707)
    naruto(rng)
    dragonball(rng)
    shadow(rng)
    demonslayer(rng)
    onepiece(rng)
    opm(rng)
    PT.build(rng)
    # placa de dificuldade (1..6) + caixote de cristais na cor do portal, no pe de cada escada: um objeto por
    # portal (PORTAL_<key>_Difficulty) para culling e para o vfx pulsar a placa
    for i, (key, px) in enumerate(zip(L.PORTAL_KEYS, L.PORTAL_X)):
        PT.difficulty(key, px, i, rng)
