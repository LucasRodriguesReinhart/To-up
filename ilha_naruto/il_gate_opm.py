# il_gate_opm - portao de compra ONE PUNCH MAN (area 6): "PORTAO DO HEROI". Dono: zona gates.
# Um pedaco de CIDADE: duas torres de concreto claro estilizado (arranha-ceus em miniatura) com fachada de vidro escuro,
# caixilhos pretos, algumas janelas acesas em dourado, aletas VERMELHAS nas quinas, cornija de ouro, cobertura recuada
# e antena com luz de aviso vermelha. Entre elas, uma VERGA de concreto com faixa vermelha e frisos de ouro; no meio,
# a ESTRELA DE IMPACTO de ouro (quadrinho) e um PUNHO VERMELHO de luva com punho de ouro saindo dela na direcao de quem
# chega (linguagem heroica, sem texto). A barreira dourada (P_Gold_Glow) corre num trilho tecnologico aceso em ouro.
# Ornamentos laterais (fora de +-12): dois predios baixos (skyline) com janelas, caixa d'agua e maquinas no telhado,
# cavaletes de obra com listras de perigo e dois cones. Faixa zebrada amarela/preta nos embasamentos.
#
# PLANO (referencial do portao; z relativo ao tabuleiro):
#   vao 16 x 18 (retangulo)         torres x 8.0..11.9 (embasamento ate 12.3), y +-2.4, corpo ate 21.8
#   verga x +-11.6, z 18.35..21.8 (trilho z 18.0..18.35) | cornija de ouro 21.8..22.35 (x +-12.3)
#   cobertura recuada x 8.7..11.2 ate 26.3, antena ate 30.6 | estrela R 2.95..4.75 em (0, 21.2), punho ate y -7.3
#   predios: esquerdo x -16.4..-12.4 (h 14.4 + caixa d'agua), direito x 12.4..16.4 (h 10.8) | cavaletes y -4.6
import math, random
import fm_lib
from fm_lib import S
import il_lib as IL
import il_gate_std as GS
import il_gates_kit as GK
from il_gates_kit import G, GMB
import fm_portal_kit as K

KEY = "OnePunchMan"
# ------------------------------------------------------------------ materiais novos (3 dos 12 da zona)
_M = fm_lib.MATS.setdefault
_M("Stone_GateOPM_Concrete", (S(200, 194, 184), 0.85, 0.0, 0, None, 0.10))   # concreto claro estilizado
_M("Metal_GateOPM_Red", (S(208, 36, 30), 0.35, 0.25, 0, None, 0.04))         # vermelho heroico (aletas, punho)
_M("Metal_GateOPM_Yellow", (S(250, 200, 32), 0.5, 0.1, 0, None, 0.03))       # amarelo de perigo
CON, RED, YEL = "Stone_GateOPM_Concrete", "Metal_GateOPM_Red", "Metal_GateOPM_Yellow"
GOLD, DARK, GLASS, STN = "Metal_Gold", "Metal_Dark", "P_OPM_DarkGlass", "Stone_Dark"
GGLOW, RGLOW = "P_Gold_Glow", "P_Red_Glow"

CAMS = GK.cams_for(KEY)

TX = 9.95                          # eixo das torres
STAR_C = 21.2
A = "Gate" + KEY


def _hazard(put, u0, u1, z0, z1, w=0.42, period=0.95):
    """faixa de perigo: base amarela + listras pretas diagonais recortadas no retangulo. put(pts, camada, material)"""
    put([(u0, z0), (u1, z0), (u1, z1), (u0, z1)], 0, YEL)
    h = z1 - z0
    x0 = u0 - h + 0.1
    while x0 < u1:
        poly = [(x0, z0), (x0 + w, z0), (x0 + w + h, z1), (x0 + h, z1)]
        poly = IL.clip(poly, 1.0, 0.0, u1)
        poly = IL.clip(poly, -1.0, 0.0, -u0)
        if len(poly) >= 3 and abs(IL.area(poly)) > 0.03:
            put(poly, 1, DARK)
        x0 += period


def _front_put(g, mb, y_face, sy, mirror=1):
    def put(pts, layer, m):
        pts = [(mirror * u, z) for u, z in pts]
        if mirror < 0:
            pts = list(reversed(pts))
        g.plate(mb, pts, y_face + sy * (0.1 + 0.14 * layer), 0.2, m)
    return put


def _side_put(g, mb, x_face, sx):
    def put(pts, layer, m):
        o = g.P(x_face + sx * (0.1 + 0.14 * layer), 0.0, 0.0)
        K.plate(mb, pts, o, tuple(g.uy), (0, 0, 1), 0.2, m)
    return put


def _facade(g, mb, rng, face, pos, sgn, u0, u1, z0, z1, lit=2, rows=1.8, cols=2):
    """vidro escuro + caixilhos pretos + algumas janelas acesas; face 'y' -> plano em y = pos, 'x' -> plano em x = pos
    (sgn = lado para onde a face olha)"""
    def put(pts, off, m):
        d = pos + sgn * off
        if face == "y":
            g.plate(mb, pts, d, 0.2, m)
        else:
            K.plate(mb, pts, g.P(d, 0.0, 0.0), tuple(g.uy), (0, 0, 1), 0.2, m)
    put([(u0, z0), (u1, z0), (u1, z1), (u0, z1)], 0.1, GLASS)
    nrow = max(1, int(round((z1 - z0) / rows)))
    dz = (z1 - z0) / nrow
    du = (u1 - u0) / cols
    for k in range(1, nrow):
        z = z0 + dz * k
        put([(u0 - 0.1, z - 0.13), (u1 + 0.1, z - 0.13), (u1 + 0.1, z + 0.13), (u0 - 0.1, z + 0.13)], 0.24, DARK)
    for c in range(1, cols):
        u = u0 + du * c
        put([(u - 0.12, z0), (u + 0.12, z0), (u + 0.12, z1), (u - 0.12, z1)], 0.24, DARK)
    for (ua, ub) in ((u0 - 0.2, u0), (u1, u1 + 0.2)):
        put([(ua, z0 - 0.2), (ub, z0 - 0.2), (ub, z1 + 0.2), (ua, z1 + 0.2)], 0.24, DARK)
    for (za, zb_) in ((z0 - 0.2, z0), (z1, z1 + 0.2)):
        put([(u0 - 0.2, za), (u1 + 0.2, za), (u1 + 0.2, zb_), (u0 - 0.2, zb_)], 0.24, DARK)
    cells = [(r, c) for r in range(nrow) for c in range(cols)]
    rng.shuffle(cells)
    for r, c in cells[:lit]:
        ua, ub = u0 + du * c + 0.2, u0 + du * (c + 1) - 0.2
        za, zb_ = z0 + dz * r + 0.22, z0 + dz * (r + 1) - 0.22
        put([(ua, za), (ub, za), (ub, zb_), (ua, zb_)], 0.2, GGLOW)


def _punched(g, mb, rng, face, pos, sgn, cols_u, rows_z, ww, wh, lit=2):
    """janelas recortadas no concreto: vidro escuro + peitoril preto; algumas acesas em dourado"""
    def put(pts, off, m):
        d = pos + sgn * off
        if face == "y":
            g.plate(mb, pts, d, 0.2, m)
        else:
            K.plate(mb, pts, g.P(d, 0.0, 0.0), tuple(g.uy), (0, 0, 1), 0.2, m)
    cells = [(u, z) for z in rows_z for u in cols_u]
    order = list(range(len(cells)))
    rng.shuffle(order)
    lit_set = set(order[:lit])
    for i, (u, z) in enumerate(cells):
        m = GGLOW if i in lit_set else GLASS
        put([(u - ww / 2, z - wh / 2), (u + ww / 2, z - wh / 2), (u + ww / 2, z + wh / 2), (u - ww / 2, z + wh / 2)],
            0.06, m)
        put([(u - ww / 2 - 0.18, z - wh / 2 - 0.3), (u + ww / 2 + 0.18, z - wh / 2 - 0.3),
             (u + ww / 2 + 0.18, z - wh / 2 - 0.06), (u - ww / 2 - 0.18, z - wh / 2 - 0.06)], 0.16, DARK)


def _towers(g, mb, rng):
    for s in (-1, 1):
        # embasamento de pedra escura com faixa de perigo (frente, costas e lado de fora)
        g.jamb_box(mb, s, 8.0, 12.3, -2.7, 2.7, 0.0, 1.7, STN, 0.12)
        for sy in (-1, 1):
            _hazard(_front_put(g, mb, sy * 2.7, sy, mirror=s), 8.3, 12.05, 0.45, 1.3)
        _hazard(_side_put(g, mb, s * 12.3, s), -2.45, 2.45, 0.45, 1.3)
        # corpo da torre com o trilho da barreira (labios de metal escuro, fundo aceso em ouro)
        g.jamb_box(mb, s, 8.0, 11.9, -2.4, 2.4, 1.7, 21.8, CON, 0.25, lip_m=DARK, slot_m=GGLOW)
        # janelas recortadas no concreto (frente e costas) e fita de vidro no lado de fora
        rows = [4.3 + 2.35 * k for k in range(6)]
        for sy in (-1, 1):
            _punched(g, mb, rng, "y", sy * 2.4, sy, [s * 9.25, s * 10.55], rows, 0.85, 1.3, lit=2)
        _facade(g, mb, rng, "x", s * 11.9, s, -1.0, 1.0, 3.4, 17.4, lit=1, rows=2.35, cols=1)
        # aletas vermelhas nas quinas de fora (frente e costas), subindo acima da cornija
        for sy in (-1, 1):
            xa, xb = sorted((s * 11.25, s * 12.2))
            ya, yb = sorted((sy * 1.5, sy * 2.95))
            g.box(mb, xa, xb, ya, yb, 1.7, 23.9, RED, 0.2)
        # cobertura recuada, faixa de vidro, tampa, antena com luz de aviso
        tx = s * TX
        g.box(mb, tx - 1.25, tx + 1.25, -1.9, 1.9, 22.35, 26.3, CON, 0.2)
        for sy in (-1, 1):
            g.plate(mb, [(tx - 1.0, 23.1), (tx + 1.0, 23.1), (tx + 1.0, 25.5), (tx - 1.0, 25.5)], sy * 2.0, 0.2, GLASS)
            g.box(mb, tx - 1.05, tx + 1.05, sy * 1.95 - 0.12, sy * 1.95 + 0.12, 24.2, 24.45, GOLD, 0.0)
        g.box(mb, tx - 1.45, tx + 1.45, -2.1, 2.1, 26.3, 26.7, DARK, 0.06)
        g.rod(mb, (tx, 0.0, 26.7), (tx, 0.0, 30.0), 0.2, DARK, 6)
        g.box(mb, tx - 0.7, tx + 0.7, -0.1, 0.1, 28.3, 28.5, DARK, 0.0)
        g.ico(mb, 0.4, (tx, 0.0, 30.2), RGLOW, 1)


def _lintel(g, mb):
    g.box(mb, -11.6, 11.6, -2.1, 2.1, 18.35, 21.8, CON, 0.25)
    # trilho de cima: labios escuros e fundo aceso (a barreira termina em 18.0)
    for y0, y1 in ((-2.1, -0.4), (0.4, 2.1)):
        g.box(mb, -8.3, 8.3, y0, y1, 18.0, 18.4, DARK, 0.04)
    g.box(mb, -8.0, 8.0, -0.3, 0.3, 18.15, 18.4, GGLOW, 0.0)
    for sy in (-1, 1):
        ya, yb = sorted((sy * 2.05, sy * 2.3))
        g.box(mb, -8.6, 8.6, ya, yb, 18.95, 21.15, RED, 0.06)
        ya, yb = sorted((sy * 2.0, sy * 2.38))
        for z0, z1 in ((18.55, 18.8), (21.3, 21.55)):
            g.box(mb, -11.9, 11.9, ya, yb, z0, z1, GOLD, 0.0)
    for s in (-1, 1):                                                                 # cornija de ouro
        xa, xb = sorted((s * 2.1, s * 12.3))
        g.box(mb, xa, xb, -2.75, 2.75, 21.8, 22.35, GOLD, 0.06)


def _emblem(g, mb):
    """estrela de impacto (ouro, atravessa a verga) + punho de luva vermelha saindo dela para quem chega"""
    spikes = [(20, 4.6), (55, 3.9), (90, 4.75), (125, 4.0), (158, 4.5), (195, 3.2), (232, 3.15), (270, 2.95),
              (308, 3.15), (342, 3.5)]
    pts = []
    for i, (a, r) in enumerate(spikes):
        a2 = spikes[(i + 1) % len(spikes)][0]
        if a2 < a:
            a2 += 360
        pts.append((math.cos(math.radians(a)) * r, STAR_C + math.sin(math.radians(a)) * r))
        am = math.radians((a + a2) / 2)
        pts.append((math.cos(am) * 2.3, STAR_C + math.sin(am) * 2.3))
    g.plate(mb, pts, 0.0, 4.9, GOLD, 0.12)
    # punho (escala FK, saindo da face da estrela para quem chega): punho de ouro, costas da mao, 4 dedos dobrados,
    # nos dos dedos, polegar cruzando na frente. Coordenadas do punho: x, d = distancia a face da estrela, z relativo
    FK, Y0, ZC = 1.25, -2.45, STAR_C - 0.05

    def fb(x0, x1, d0, d1, z0, z1, m, bev):
        g.box(mb, x0 * FK, x1 * FK, Y0 - d1 * FK, Y0 - d0 * FK, ZC + z0 * FK, ZC + z1 * FK, m, bev * FK)
    g.cyl(mb, 1.45 * FK, 0.9 * FK, (0.0, Y0 - 0.45 * FK, ZC), GOLD, 16, bev=0.08, axis="y")
    fb(-1.6, 1.6, 0.65, 2.6, -1.35, 1.4, RED, 0.5)
    for i, x in enumerate((-1.17, -0.39, 0.39, 1.17)):
        dz = (0.0, 0.06, 0.0, -0.12)[i]
        fb(x - 0.37, x + 0.37, 2.25, 3.5, -1.0 + dz, 1.1 + dz, RED, 0.3)
        fb(x - 0.36, x + 0.36, 2.0, 3.25, 0.75 + dz, 1.45 + dz, RED, 0.25)
    fb(-1.75, -0.95, 1.85, 3.15, -1.3, -0.15, RED, 0.3)
    fb(-1.55, 0.55, 3.05, 3.85, -1.2, -0.4, RED, 0.3)


def _building(g, mb, rng, s, h, roof):
    x0, x1 = sorted((s * 12.4, s * 16.4))
    y0, y1 = -1.6, 2.4
    g.box(mb, x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, 0.0, 1.0, STN, 0.08)
    g.box(mb, x0, x1, y0, y1, 1.0, h, CON, 0.2)
    g.box(mb, x0 - 0.1, x1 + 0.1, y0 - 0.1, y1 + 0.1, h - 0.45, h, GOLD, 0.0)
    g.box(mb, x0 - 0.15, x1 + 0.15, y0 - 0.15, y1 + 0.15, h, h + 0.4, DARK, 0.06)
    u0, u1 = sorted((s * 12.9, s * 15.9))
    _facade(g, mb, rng, "y", y0, -1, u0, u1, 2.0, h - 1.3, lit=2, rows=1.7, cols=2)
    _facade(g, mb, rng, "y", y1, 1, u0, u1, 2.0, h - 1.3, lit=1, rows=1.7, cols=2)
    _facade(g, mb, rng, "x", s * 16.4, s, -1.1, 1.9, 2.0, h - 1.3, lit=1, rows=1.7, cols=2)
    cx = s * 14.4
    if roof == "tank":
        tx, ty = s * 15.0, 1.0
        for dx in (-0.7, 0.7):
            for dy in (-0.7, 0.7):
                g.rod(mb, (tx + dx, ty + dy, h + 0.4), (tx + dx, ty + dy, h + 1.7), 0.14, DARK, 4)
        g.cyl(mb, 1.05, 1.9, (tx, ty, h + 2.65), DARK, 12, bev=0.0)
        g.cyl(mb, 1.12, 0.14 + 0.2, (tx, ty, h + 2.0), GOLD, 12, bev=0.0)
        g.cone(mb, (tx, ty, h + 3.6), (tx, ty, h + 4.3), 1.18, 0.1, DARK, 12)
    else:
        for dx, dy in ((-0.9, -0.3), (0.9, 0.9)):
            g.box(mb, cx + dx - 0.75, cx + dx + 0.75, dy - 0.65, dy + 0.65, h + 0.4, h + 1.35, DARK, 0.08)
            g.cyl(mb, 0.5, 0.2, (cx + dx, dy, h + 1.42), CON, 10, bev=0.0)
        g.rod(mb, (cx - s * 1.5, 1.8, h + 0.4), (cx - s * 1.5, 1.8, h + 2.6), 0.1, DARK, 4)
        g.ico(mb, 0.28, (cx - s * 1.5, 1.8, h + 2.75), RGLOW, 1)


def _barricade(g, mb, s):
    cx, cy = s * 14.4, -4.6
    for dx in (-1.5, 1.5):
        for dy in (-0.55, 0.55):
            g.beam(mb, (cx + dx, cy + dy, 0.0), (cx + dx, cy, 2.35), 0.2, 0.2, DARK, 0.0)
    for z0, z1 in ((1.45, 2.25), (0.55, 1.05)):
        u0, u1 = cx - 1.9, cx + 1.9
        _hazard(_front_put(g, mb, cy - 0.05, -1), u0, u1, z0, z1, w=0.4, period=0.9)
        g.box(mb, u0, u1, cy - 0.05, cy + 0.15, z0, z1, DARK, 0.0)


def _cones(g, mb):
    for x, y in ((12.9, -6.6), (16.0, -6.2)):
        g.box(mb, x - 0.6, x + 0.6, y - 0.6, y + 0.6, 0.0, 0.16, DARK, 0.0)
        g.cone(mb, (x, y, 0.16), (x, y, 1.6), 0.5, 0.1, RED, 8)
        g.cyl(mb, 0.36, 0.24, (x, y, 0.95), CON, 8, r2=0.3, bev=0.0)


def _collision(g):
    for s in (-1, 1):
        g.col(A, s * 8.0, s * 12.3, -2.95, 2.95, 0.0, 26.7)
        g.col(A, s * 12.3, s * 16.5, -1.8, 2.55, 0.0, (14.4 if s < 0 else 10.8) + 0.4)
        g.col(A, s * 12.45, s * 16.35, -5.25, -3.95, 0.0, 2.4)
    g.col(A, 12.3, 16.6, -7.2, -5.6, 0.0, 1.6)


def build_gate(gx, gy, gz, yaw):
    rng = random.Random(6606)
    F = GS.gate_frame(gx, gy, gz, yaw)
    g = G(F)
    mb = GMB("GATE_%s_Frame" % KEY, rng, detail="hero", vcap=1)
    _towers(g, mb, rng)
    _lintel(g, mb)
    _emblem(g, mb)
    _building(g, mb, rng, -1, 14.4, "tank")
    _building(g, mb, rng, 1, 10.8, "ac")
    for s in (-1, 1):
        _barricade(g, mb, s)
    _cones(g, mb)
    GK.tag(mb.finish(), KEY, "frame")
    _collision(g)
    GS.barrier(KEY, F, GGLOW, shape="rect", rng=rng)
    GS.markers(KEY, F, yaw)
    GK.scale_dummy(KEY, g)
    GK.make_cams(CAMS)


def build():
    gx, gy, gz, yaw = GS.gallery_slot(KEY)
    build_gate(gx, gy, gz, yaw)
