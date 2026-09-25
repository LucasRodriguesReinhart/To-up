# il_gate_db - PECA-HEROI No 4: portao de compra DRAGON BALL na ilhota da saida (ref_13). Substitui
# il_blockout.db_gate(). Segue o padrao il_gate_std (vao 16 x 18, barreira circular de energia, cadeado, colisao de
# bloqueio e marcadores) sem mudar nada dele; aqui so a MOLDURA e o entorno:
#   - 2 pilares redondos de laca vermelha com aneis de ouro sobre bases de pedra; ombreiras e verga de pedra com
#     gregas de ouro emoldurando o vao (nada entra no vao);
#   - viga mestra vermelha, friso com o MEDALHAO dourado (esfera laranja de 4 estrelas, frente e costas) logo atras
#     da ancora do painel de preco (o BillboardGui fica NA FRENTE do medalhao, nunca dentro da geometria);
#   - telhado curvo de telhas escuras em canal, beiral que sobe nas pontas, cumeeira e chifres dourados, pinaculo;
#   - 2 leoes de pedra segurando esferas do dragao em pedestais FORA da passagem (+-16, 4 antes do plano);
#   - 4 esferas flutuantes VFX_GATE_DB_Orb_1..4 (bob + giro lento);
#   - guarda-corpo vermelho com pinaculos de ouro no nicho da plataforma e 4 lanternas de pedra;
#   - GATE_DB_OpenGlow: contorno dourado do vao que so acende ao desbloquear (gate_part = "open_glow").
# Esferas: as 7 estao no portao (1, 2, 5, 6 flutuando; 3 e 7 com os leoes; 4 no medalhao).
import math, random
import bmesh
from mathutils import Vector, Matrix, Euler
import fm_lib
from fm_lib import S
import il_lib as IL
from il_lib import MB, col_box, mk, light
import il_layout as L
import il_gate_std as GS
import il_exit_plan as P
import fm_portal_kit as K

_M = fm_lib.MATS.setdefault
_M("Roof_DBGate_Tile", (S(58, 66, 88), 0.6, 0.0, 0, None, 0.08))          # telha escura azul-ardosia
_M("Crystal_DBGate_Orb", (S(255, 140, 20), 0.18, 0.0, 0, None, 0.0))      # esfera do dragao (laranja)
_M("Crystal_DBGate_Star", (S(206, 24, 16), 0.45, 0.0, 0, None, 0.0))     # estrelas vermelhas
_M("Metal_DBGate_Glow", (S(255, 214, 112), 0.35, 0.0, 3.0, S(255, 196, 84), 0.0))   # contorno aceso (Neon)

C = "08_PURCHASE_GATES"
KEY = "DB"
OW = GS.OPEN_W / 2.0          # 8
OH = GS.OPEN_H                # 18
PX = 11.3                     # eixo dos pilares
PR = 2.2                      # raio do pilar
JX0, JX1 = OW + 0.05, 9.35    # ombreira de pedra (face interna 8,05: vao livre intacto)
Z_LINTEL = OH + 0.05          # 18,05
Z_BEAM0, Z_BEAM1 = 19.4, 21.0     # viga mestra
Z_UB0, Z_UB1 = 28.3, 29.5         # viga de cima (sob o beiral)
MED_Z = (21.0 + 28.3) / 2      # centro do medalhao entre as vigas (a ancora de preco fica em 26, 2 a frente)
RX, Y0, YE = 19.6, 0.45, 7.7      # telhado: meia largura, inicio da agua, beiral
ZR, RH = 32.1, 3.15               # cumeeira (topo) e queda ate o beiral
LIFT, RLIFT = 2.3, 0.55           # subida das pontas do beiral e da cumeeira
LIONS_XY = [(-16.0, -4.0, 3), (16.0, -4.0, 7)]          # (x, y, estrelas)
ORBS = [(-14.6, -3.0, 15.3, 1), (-13.2, -5.3, 11.7, 2), (13.4, -5.1, 12.1, 5), (14.8, -2.9, 15.9, 6)]
STAR_LAYOUT = {
    1: [(0.0, 0.0)],
    2: [(-0.5, 0.0), (0.5, 0.0)],
    3: [(0.0, 0.52), (-0.48, -0.32), (0.48, -0.32)],
    4: [(0.0, 0.62), (-0.62, 0.0), (0.62, 0.0), (0.0, -0.62)],
    5: [(0.0, 0.0), (-0.58, 0.42), (0.58, 0.42), (-0.4, -0.6), (0.4, -0.6)],
    6: [(-0.56, 0.4), (0.0, 0.56), (0.56, 0.4), (-0.56, -0.4), (0.0, -0.56), (0.56, -0.4)],
    7: [(0.0, 0.0)] + [(0.62 * math.cos(math.radians(90 + 60 * k)), 0.62 * math.sin(math.radians(90 + 60 * k)))
                       for k in range(6)],
}


def _cams():
    gx, gy = L.gate_db_pos()
    F = GS.gate_frame(gx, gy, L.EXIT_Z, P.yaw())
    return {
        "CAM_GateDB_Front": (tuple(F.p(0, -60, 15)), tuple(F.p(0, 0, 19.5)), 24),
        "CAM_GateDB_Front34": (tuple(F.p(-34, -40, 26)), tuple(F.p(0, 0, 17)), 22),
        "CAM_GateDB_Back": (tuple(F.p(16, 46, 20)), tuple(F.p(0, 0, 18)), 22),
        "CAM_GateDB_Side": (tuple(F.p(62, -12, 22)), tuple(F.p(0, -1, 18)), 22),
        "CAM_GateDB_SideL": (tuple(F.p(-62, 8, 22)), tuple(F.p(0, -1, 18)), 22),
        "CAM_GateDB_Player": (tuple(F.p(2.5, -22, 5.5)), tuple(F.p(0, 0, 13.0)), 18),
    }


CAMS = _cams()


# ------------------------------------------------------------------ utilidades
def smooth(mb, faces):
    for f in faces:
        if f.is_valid:
            f.smooth = True


def sphere(mb, c, r, m, F=None, us=18, vs=11, sy=1.0):
    """esfera lisa (sombreamento suave); F: gira junto do portao; sy: achata no eixo y local (lente)"""
    ang = F.a if F is not None else 0.0
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((1.0, sy, 1.0, 1.0))
    res = bmesh.ops.create_uvsphere(mb.bm, u_segments=us, v_segments=vs, radius=r, matrix=M)
    faces = mb._post(res["verts"], m, None, 0, 1)
    smooth(mb, faces)


def star2d(ro, ri=None, spin=0.0):
    ri = ro * 0.45 if ri is None else ri
    return [((ro if i % 2 == 0 else ri) * math.cos(math.radians(90 + spin + 36 * i)),
             (ro if i % 2 == 0 else ri) * math.sin(math.radians(90 + spin + 36 * i))) for i in range(10)]


def star_decal(mb, c, r, n, pts2d, m, M=None, off=0.05, depth=0.12, up=(0, 0, 1)):
    """estrela colada numa esfera de raio r em volta da direcao n (esfera unitaria no centro c, depois M = matriz
    3x3 opcional que deforma junto: lente achatada). Face de cima a r + off, parede ate r - depth."""
    c = Vector(c)
    n = Vector(n).normalized()
    u = Vector(up) - n * Vector(up).dot(n)
    if u.length < 1e-4:
        u = Vector((1, 0, 0)) - n * n.x
    u.normalize()
    side = u.cross(n).normalized()

    def on(a, b, h):
        t = side * a + u * b
        dep = math.sqrt(max(0.0, r * r - t.length_squared))
        v = (t + n * dep).normalized() * (r + h)
        return c + (M @ v if M is not None else v)
    bm = mb.bm
    top = [bm.verts.new(on(a, b, off)) for a, b in pts2d]
    bot = [bm.verts.new(on(a, b, -depth)) for a, b in pts2d]
    ct = bm.verts.new(on(0.0, 0.0, off))
    k = len(pts2d)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((ct, top[i], top[j]))
        bm.faces.new((top[j], top[i], bot[i], bot[j]))
    mb._post(top + bot + [ct], m, None, 0, 1)


def ball_stars(mb, c, r, k, facing, M=None, size=None, spread=None, up=(0, 0, 1)):
    """k estrelas no hemisferio voltado para 'facing' (esfera c, r; M deforma junto)"""
    f = Vector(facing).normalized()
    sp = spread if spread is not None else r * (0.5 if k <= 4 else 0.66)
    size = size if size is not None else r * (0.3 if k <= 2 else (0.23 if k <= 4 else 0.16))
    u = Vector(up) - f * Vector(up).dot(f)
    if u.length < 1e-4:
        u = Vector((1, 0, 0))
    u.normalize()
    side = u.cross(f).normalized()
    for a, b in STAR_LAYOUT[k]:
        t = side * (a * sp) + u * (b * sp)
        d = (t + f * math.sqrt(max(0.0, r * r - t.length_squared))).normalized()
        star_decal(mb, c, r, d, star2d(size), "Crystal_DBGate_Star", M=M, off=0.04, depth=min(0.12, r * 0.08),
                   up=up)


def dragon_ball(mb, c, r, k, facing, F=None, sy=1.0, back=False):
    """esfera do dragao: bola laranja lisa + k estrelas vermelhas viradas para 'facing' (e para tras, se back)"""
    sphere(mb, c, r, "Crystal_DBGate_Orb", F, us=20 if r > 2 else 16, vs=12 if r > 2 else 10, sy=sy)
    M = None
    if sy != 1.0 and F is not None:
        R = Matrix.Rotation(F.a, 3, "Z")
        M = R @ Matrix.Diagonal((1.0, sy, 1.0)) @ R.transposed()
    ball_stars(mb, c, r, k, facing, M=M)
    if back:
        ball_stars(mb, c, r, k, -Vector(facing), M=M)


# ------------------------------------------------------------------ moldura
def pillars_and_jambs(mb, F):
    for s in (-1, 1):
        x = s * PX
        # base de pedra (sapata escura + bloco claro + moldura), aneis de ouro, fuste de laca, capitel de ouro
        mb.box((5.0, 5.0, 0.55), F.p(x, 0, 0.27), F.r(), "Stone_Wall_Dark", 0.12)
        mb.box((4.6, 4.6, 2.5), F.p(x, 0, 0.55 + 1.25), F.r(), "Stone_Wall_Light", 0.2)
        mb.box((4.9, 4.9, 0.45), F.p(x, 0, 3.05 + 0.22), F.r(), "Stone_Wall_Dark", 0.1)
        mb.cyl(PR + 0.4, 0.55, F.p(x, 0, 3.5 + 0.27), F.r(), "Metal_Gold", 20, bevel=0.0)
        mb.cyl(PR + 0.2, 0.3, F.p(x, 0, 4.05 + 0.15), F.r(), "Metal_Gold", 20, bevel=0.0)
        h = Z_UB0 - 4.35
        mb.cyl(PR, h, F.p(x, 0, 4.35 + h / 2), F.r(), "Wood_Lacquer_Red", 20, bevel=0.0)
        for zc, hh in ((15.6, 0.5), (16.3, 0.25)):
            mb.cyl(PR + 0.22, hh, F.p(x, 0, zc), F.r(), "Metal_Gold", 20, bevel=0.0)
        mb.cyl(PR + 0.35, 0.8, F.p(x, 0, Z_BEAM0 - 0.4), F.r(), "Metal_Gold", 20, bevel=0.0)
        mb.cyl(PR + 0.25, 0.7, F.p(x, 0, Z_UB0 - 0.35), F.r(), "Metal_Gold", 20, bevel=0.0)
        # ombreira de pedra com greca de ouro (frente e costas)
        jx = s * (JX0 + JX1) / 2
        mb.box((JX1 - JX0, 2.2, Z_LINTEL), F.p(jx, 0, Z_LINTEL / 2), F.r(), "Stone_Wall_Light", 0.12)
        for sy in (-1, 1):
            y = sy * 1.18
            mb.box((0.24, 0.2, 12.2), F.p(jx, y, 9.0), F.r(), "Metal_Gold", 0.0)
            for zz in (2.2, 15.9):
                greek_key(mb, F, jx, y, zz, sy, s)
    # verga de pedra com friso de ouro
    mb.box((2 * JX1, 2.2, Z_BEAM0 - Z_LINTEL), F.p(0, 0, (Z_LINTEL + Z_BEAM0) / 2), F.r(), "Stone_Wall_Light", 0.12)
    for sy in (-1, 1):
        y = sy * 1.18
        mb.box((2 * JX1 - 1.2, 0.2, 0.22), F.p(0, y, Z_LINTEL + 0.3), F.r(), "Metal_Gold", 0.0)
        mb.box((2 * JX1 - 1.2, 0.2, 0.22), F.p(0, y, Z_BEAM0 - 0.28), F.r(), "Metal_Gold", 0.0)
        for k in range(7):
            x = -6.6 + k * 2.2
            mb.box((0.62, 0.2, 0.5), F.p(x, y, (Z_LINTEL + Z_BEAM0) / 2), F.r(0, 0, 0), "Metal_Gold", 0.0)


def greek_key(mb, F, x, y, z, sy, sx):
    """greca (espiral quadrada) de ouro em relevo raso na face da ombreira"""
    t = 0.22
    for (a, b, w, h) in ((0.0, 0.0, 0.94, t), (0.37, 0.37, t, 0.94), (0.0, 0.74, 0.94, t), (-0.37, 0.55, t, 0.52),
                         (-0.1, 0.37, 0.52, t)):
        mb.box((w, 0.2, h), F.p(x + sx * a * 0.9, y, z + b - 0.37), F.r(), "Metal_Gold", 0.0)


def beams_and_frieze(mb, F):
    # viga mestra (passa pelos pilares) com testeiras de ouro
    mb.box((32.4, 3.0, Z_BEAM1 - Z_BEAM0), F.p(0, 0, (Z_BEAM0 + Z_BEAM1) / 2), F.r(), "Wood_Lacquer_Red", 0.15)
    for s in (-1, 1):
        mb.box((0.35, 3.2, 2.2), F.p(s * 16.3, 0, (Z_BEAM0 + Z_BEAM1) / 2), F.r(), "Metal_Gold", 0.06)
        mb.box((32.4, 0.2, 0.3), F.p(0, s * 1.56, Z_BEAM1 - 0.35), F.r(), "Metal_Gold", 0.0)
    # friso (tabua de laca entre os pilares) com moldura de ouro nas duas faces
    zf0, zf1 = Z_BEAM1, Z_UB0
    mb.box((2 * (PX - PR) + 0.2, 0.7, zf1 - zf0), F.p(0, 0, (zf0 + zf1) / 2), F.r(), "Wood_Lacquer_Red", 0.0)
    for sy in (-1, 1):
        y = sy * 0.43
        for zz in (zf0 + 0.35, zf1 - 0.35):
            mb.box((2 * (PX - PR) - 0.6, 0.2, 0.28), F.p(0, y, zz), F.r(), "Metal_Gold", 0.0)
        for xx in (-(PX - PR) + 0.5, (PX - PR) - 0.5):
            mb.box((0.28, 0.2, zf1 - zf0 - 0.7), F.p(xx, y, (zf0 + zf1) / 2), F.r(), "Metal_Gold", 0.0)
    # misulas (blocos empilhados) sobre a viga, dos dois lados do medalhao, e escoras nas pontas
    for s in (-1, 1):
        for x in (s * 6.1,):
            mb.box((1.9, 2.8, 0.9), F.p(x, 0, Z_BEAM1 + 0.45), F.r(), "Wood_Lacquer_Red", 0.1)
            mb.box((2.2, 3.1, 0.25), F.p(x, 0, Z_BEAM1 + 1.02), F.r(), "Metal_Gold", 0.04)
            mb.box((1.3, 2.3, 0.8), F.p(x, 0, Z_BEAM1 + 1.55), F.r(), "Wood_Lacquer_Red", 0.08)
        mb.box((0.9, 0.9, Z_UB0 - Z_BEAM1), F.p(s * 14.9, 0, (Z_UB0 + Z_BEAM1) / 2), F.r(), "Wood_Lacquer_Red", 0.08)
        mb.box((1.9, 2.4, 0.6), F.p(s * 14.9, 0, Z_UB0 - 0.3), F.r(), "Wood_Lacquer_Red", 0.08)
        mb.box((1.3, 1.3, 0.3), F.p(s * 14.9, 0, Z_BEAM1 + 0.15), F.r(), "Metal_Gold", 0.04)
    # misulas em degraus (dougong) no alto de cada pilar, para a frente e para tras: ligam o pilar ao beiral e dao
    # profundidade ao portao visto de lado
    for s in (-1, 1):
        x = s * PX
        for sy in (-1, 1):
            for (z0, reach, w) in ((25.9, 3.2, 1.3), (26.75, 4.4, 1.45), (27.6, 5.7, 1.6)):
                ln = reach - PR * 0.6
                mb.box((w, ln, 0.85), F.p(x, sy * (PR * 0.6 + ln / 2), z0 + 0.42), F.r(), "Wood_Lacquer_Red", 0.1)
                mb.box((w + 0.3, 0.9, 0.22), F.p(x, sy * (reach - 0.45), z0 + 0.85 + 0.11), F.r(), "Metal_Gold", 0.03)
            mb.box((1.9, 1.3, 0.7), F.p(x, sy * 5.25, 28.9), F.r(), "Wood_Lacquer_Red", 0.1)
    # viga de cima + frechal (sustenta o telhado)
    mb.box((35.2, 4.6, Z_UB1 - Z_UB0), F.p(0, 0, (Z_UB0 + Z_UB1) / 2), F.r(), "Wood_Lacquer_Red", 0.15)
    for s in (-1, 1):
        mb.box((35.2, 0.2, 0.3), F.p(0, s * 2.36, Z_UB0 + 0.3), F.r(), "Metal_Gold", 0.0)
        mb.box((0.3, 4.8, 1.3), F.p(s * 17.65, 0, (Z_UB0 + Z_UB1) / 2), F.r(), "Metal_Gold", 0.04)
    mb.box((33.6, 3.2, 1.0), F.p(0, 0, Z_UB1 + 0.5), F.r(), "Wood_Lacquer_Red", 0.1)


def medallion(mb, F):
    """medalhao da esfera de 4 estrelas no friso (frente e costas): aro de ouro, lente laranja, estrelas, cravos"""
    c = F.p(0, 0, MED_Z)
    ux = F.p(1, 0, 0) - F.p(0, 0, 0)
    uy = F.p(0, 1, 0) - F.p(0, 0, 0)
    K.ring(mb, c, 2.9, ux, Vector((0, 0, 1)), 0.9, 1.3, "Metal_Gold", n=40)
    K.ring(mb, c, 3.48, ux, Vector((0, 0, 1)), 0.32, 0.8, "Metal_Gold", n=40)
    dragon_ball(mb, c, 2.5, 4, -uy, F=F, sy=0.56, back=True)
    # cravos de ouro no friso, dos dois lados do medalhao
    for sx in (-1, 1):
        for zz in (-1.6, 0.0, 1.6):
            for sy in (-1, 1):
                K.octa(mb, c + ux * (sx * (4.3 + 0.35 * (zz == 0.0))) + Vector((0, 0, zz)) + uy * (sy * 0.38),
                       0.3, 0.3, "Metal_Gold", rot=F.a)


def roof(mb, F):
    """telhado curvo de telhas em canal (duas aguas, cada uma um bloco fechado) com beiral subindo nas pontas"""
    per = 2 * RX / 22.0
    nx = 88
    ns = 4
    th = 0.55

    def zt(x, s):
        ax = abs(x) / RX
        return ZR - RH * (1.0 - (1.0 - s) ** 1.5) + LIFT * ax ** 3 * s ** 1.4 + RLIFT * ax ** 4

    def corr(x):
        return 0.34 * abs(math.sin(math.pi * x / per)) ** 0.6

    for side in (-1, 1):
        bm = mb.bm
        top, bot = [], []
        for i in range(nx + 1):
            x = -RX + 2 * RX * i / nx
            rt, rb = [], []
            for j in range(ns + 1):
                s = j / ns
                y = side * (Y0 + (YE - Y0) * s)
                z = zt(x, s)
                rt.append(bm.verts.new(F.p(x, y, z + corr(x) * (0.35 + 0.65 * s))))
                rb.append(bm.verts.new(F.p(x, y, z - th)))
            top.append(rt)
            bot.append(rb)
        for i in range(nx):
            for j in range(ns):
                bm.faces.new((top[i][j], top[i + 1][j], top[i + 1][j + 1], top[i][j + 1]))
                bm.faces.new((bot[i][j + 1], bot[i + 1][j + 1], bot[i + 1][j], bot[i][j]))
        for i in range(nx):
            for j in (0, ns):
                bm.faces.new((top[i][j], bot[i][j], bot[i + 1][j], top[i + 1][j]))
        for i in (0, nx):
            for j in range(ns):
                bm.faces.new((top[i][j], top[i][j + 1], bot[i][j + 1], bot[i][j]))
        allv = [v for r in top for v in r] + [v for r in bot for v in r]
        mb._post(allv, "Roof_DBGate_Tile", None, 0, 1)
        # testeira de ouro no beiral e nas empenas
        eave = [F.p(-RX + 2 * RX * i / 32, side * (YE + 0.05), zt(-RX + 2 * RX * i / 32, 1.0) - 0.25)
                for i in range(33)]
        mb.sweep(eave, [(-0.2, -0.36), (0.2, -0.36), (0.2, 0.36), (-0.2, 0.36)], "Metal_Gold", True)
        for sx in (-1, 1):
            verge = [F.p(sx * (RX + 0.05), side * (Y0 + (YE - Y0) * j / 6), zt(RX, j / 6) - 0.1) for j in range(7)]
            mb.sweep(verge, [(-0.2, -0.33), (0.2, -0.33), (0.2, 0.33), (-0.2, 0.33)], "Metal_Gold", True)
            # chifre de ouro no canto do beiral (sobe e abre para fora)
            c0 = F.p(sx * (RX + 0.1), side * (YE + 0.1), zt(RX, 1.0) - 0.1)
            out = (F.p(sx, side * 0.7, 0) - F.p(0, 0, 0)).normalized()
            pts = [c0, c0 + out * 0.7 + Vector((0, 0, 0.35)), c0 + out * 1.25 + Vector((0, 0, 1.05)),
                   c0 + out * 1.45 + Vector((0, 0, 1.9))]
            K.taper_tube(mb, pts, [0.42, 0.36, 0.26, 0.1], "Metal_Gold", n=7)
    # cumeeira de ouro com as pontas viradas para cima
    pts = []
    for i in range(25):
        x = -RX - 0.3 + (2 * RX + 0.6) * i / 24
        pts.append(F.p(x, 0, ZR + RLIFT * (min(abs(x), RX) / RX) ** 4 + 0.3))
    mb.sweep(pts, [(-0.75, -0.55), (0.75, -0.55), (0.75, 0.5), (-0.75, 0.5)], "Metal_Gold", True)
    for sx in (-1, 1):
        a = F.p(sx * (RX + 0.2), 0, ZR + RLIFT + 0.3)
        pts = [a, a + (F.p(sx * 0.8, 0, 0) - F.p(0, 0, 0)) + Vector((0, 0, 0.45)),
               a + (F.p(sx * 1.35, 0, 0) - F.p(0, 0, 0)) + Vector((0, 0, 1.4)),
               a + (F.p(sx * 1.5, 0, 0) - F.p(0, 0, 0)) + Vector((0, 0, 2.6))]
        K.taper_tube(mb, pts, [0.62, 0.55, 0.38, 0.12], "Metal_Gold", n=8)
    # pinaculo no centro da cumeeira: tambor vermelho, domo de ouro, esfera e agulha
    z = ZR + 0.7
    mb.cyl(1.75, 1.2, F.p(0, 0, z + 0.6), F.r(), "Wood_Lacquer_Red", 16, bevel=0.0)
    mb.cyl(1.95, 0.32, F.p(0, 0, z + 1.36), F.r(), "Metal_Gold", 16, bevel=0.0)
    sphere(mb, F.p(0, 0, z + 1.52), 1.85, "Metal_Gold", F, us=16, vs=10, sy=1.0)
    mb.cyl(0.42, 0.9, F.p(0, 0, z + 3.35), F.r(), "Metal_Gold", 10, bevel=0.0)
    sphere(mb, F.p(0, 0, z + 4.2), 0.62, "Metal_Gold", F, us=12, vs=8)
    K.cone(mb, F.p(0, 0, z + 4.6), F.p(0, 0, z + 8.4), 0.42, 0.03, "Metal_Gold", n=8)


def frame(F, rng):
    mb = MB("GATE_DB_Frame", C, rng, detail="hero")
    pillars_and_jambs(mb, F)
    beams_and_frieze(mb, F)
    medallion(mb, F)
    roof(mb, F)
    ob = mb.finish()
    # colisao: pilares com base (altura toda) e ombreiras
    for s in (-1, 1):
        col_box("GateDB", (4.8, 4.8, Z_UB1), F.p(s * PX, 0, Z_UB1 / 2), F.r())
        col_box("GateDB", (JX1 - JX0, 2.2, Z_LINTEL), F.p(s * (JX0 + JX1) / 2, 0, Z_LINTEL / 2), F.r())
    return ob


def open_glow(F):
    """contorno dourado do vao (so acende ao desbloquear): frente e costas das ombreiras e da verga, fora do vao"""
    mb = MB("GATE_DB_OpenGlow", C, None, detail="hero")
    for sy in (-1, 1):
        y = sy * 1.08
        for s in (-1, 1):
            mb.box((0.3, 0.3, Z_LINTEL - 0.3), F.p(s * (OW + 0.15), y, 0.3 + (Z_LINTEL - 0.3) / 2), F.r(),
                   "Metal_DBGate_Glow", 0.0)
        mb.box((2 * OW + 0.6, 0.3, 0.3), F.p(0, y, Z_LINTEL + 0.15), F.r(), "Metal_DBGate_Glow", 0.0)
    ob = mb.finish()
    ob["gate"] = KEY
    ob["gate_part"] = "open_glow"
    ob["gate_state"] = "unlocked"
    return ob


# ------------------------------------------------------------------ leoes, esferas, guarda-corpo, lanternas
def lion(mb, F, x, y, stars, s_in, k=1.18):
    """leao de pedra (shishi) sentado no pedestal, virado para quem chega e um pouco para dentro; juba em cachos e
    uma esfera do dragao sob a pata de fora"""
    mb.box((5.0, 5.0, 0.55), F.p(x, y, 0.27), F.r(), "Stone_Wall_Dark", 0.12)
    mb.box((4.4, 4.4, 3.0), F.p(x, y, 0.55 + 1.5), F.r(), "Stone_Wall_Light", 0.22)
    mb.box((4.9, 4.9, 0.5), F.p(x, y, 3.55 + 0.25), F.r(), "Stone_Wall_Dark", 0.12)
    for sy in (-1, 1):
        mb.box((2.6, 0.1, 1.4), F.p(x, y + sy * 2.21, 2.05), F.r(), "Stone_Wall_Dark", 0.0)
    base = F.p(x, y, 4.05)
    ang = F.a + math.pi + s_in * math.radians(15)
    FL = type(F)(base.x, base.y, base.z, ang)

    def Q(a, b, c):
        return FL.p(a * k, b * k, c * k)
    m = "Stone_Wall_Light"
    mb.box((3.5 * k, 4.1 * k, 0.35), FL.p(0, -0.1 * k, 0.17), FL.r(), "Stone_Wall_Dark", 0.1)
    for sx in (-1, 1):
        mb.ico(k, Q(sx * 0.95, -0.85, 1.25), m, 1, (0.95, 1.35, 1.05), rot=FL.r(), jitter=0.04)
        mb.box((0.95 * k, 1.25 * k, 0.5 * k), Q(sx * 1.05, -0.05, 0.6), FL.r(), m, 0.2)
    mb.ico(k, Q(0, -0.35, 2.35), m, 1, (1.25, 1.15, 1.75), rot=FL.r(-0.2), jitter=0.03)
    mb.ico(k, Q(0, 0.45, 2.5), m, 1, (1.1, 0.95, 1.2), rot=FL.r(), jitter=0.03)
    s_out = s_in           # lado de fora do pedestal, no referencial do leao
    bc = Q(0.2 * s_out, 1.95, 1.3)
    fwd = (FL.p(0, 1, 0) - FL.p(0, 0, 0)).normalized()
    dragon_ball(mb, bc, 0.95 * k, stars, fwd + Vector((0, 0, 0.25)), F=None)
    for sx in (-1, 1):
        if sx == s_out:
            mb.rod(Q(sx * 0.75, 0.75, 2.4), Q(sx * 0.6, 1.75, 2.05), 0.42 * k, m, 8)
            mb.box((0.9 * k, 1.0 * k, 0.45 * k), Q(sx * 0.5, 2.05, 2.2), FL.r(-0.25), m, 0.18)
        else:
            mb.rod(Q(sx * 0.75, 0.85, 2.4), Q(sx * 0.8, 1.1, 0.5), 0.42 * k, m, 8)
            mb.box((0.9 * k, 1.15 * k, 0.5 * k), Q(sx * 0.8, 1.35, 0.6), FL.r(), m, 0.2)
    # juba: massa + cachos nas bochechas e no alto; cabeca, focinho, boca aberta, sobrancelhas, orelhas
    mb.ico(k, Q(0, 0.25, 3.95), m, 1, (1.55, 1.2, 1.5), rot=FL.r(), jitter=0.12)
    for (a, b, c, r) in ((-1.15, 0.75, 3.6, 0.55), (1.15, 0.75, 3.6, 0.55), (-0.95, 0.55, 4.55, 0.5),
                         (0.95, 0.55, 4.55, 0.5), (0.0, 0.45, 5.05, 0.55), (-0.9, 0.2, 2.95, 0.5),
                         (0.9, 0.2, 2.95, 0.5)):
        mb.ico(r * k, Q(a, b, c), m, 1, (1.0, 0.85, 1.0), rot=FL.r(), jitter=0.1)
    mb.ico(k, Q(0, 1.05, 4.1), m, 1, (1.1, 1.05, 1.0), rot=FL.r(), jitter=0.05)
    mb.box((1.2 * k, 0.95 * k, 0.78 * k), Q(0, 2.0, 3.8), FL.r(), m, 0.28)
    mb.box((0.55 * k, 0.32 * k, 0.32 * k), Q(0, 2.46, 4.08), FL.r(), "Stone_Wall_Dark", 0.08)
    mb.box((1.05 * k, 0.55 * k, 0.22 * k), Q(0, 2.18, 3.36), FL.r(), "Stone_Wall_Dark", 0.05)
    mb.box((1.7 * k, 0.55 * k, 0.42 * k), Q(0, 1.82, 4.56), FL.r(), m, 0.16)
    for sx in (-1, 1):
        mb.box((0.5 * k, 0.4 * k, 0.65 * k), Q(sx * 0.95, 0.85, 4.85), FL.r(0, sx * 0.3, 0), m, 0.12)
    # rabo em cacho
    mb.ico(0.8 * k, Q(0, -1.95, 2.95), m, 1, (0.9, 0.7, 1.2), rot=FL.r(), jitter=0.12)
    mb.ico(0.5 * k, Q(0, -2.1, 3.85), m, 1, (1.0, 0.8, 1.0), rot=FL.r(), jitter=0.1)


def stone_lantern(mb, F, x, y, name=None):
    """lanterna de pedra quadrada (ref_13): sapata, fuste, prato, camara acesa com montantes, chapeu de telha"""
    zb = 0.15
    mb.box((2.0, 2.0, 0.6), F.p(x, y, zb + 0.3), F.r(), "Stone_Wall_Dark", 0.12)
    mb.box((1.2, 1.2, 2.4), F.p(x, y, zb + 0.6 + 1.2), F.r(), "Stone_Wall_Light", 0.12)
    mb.box((2.0, 2.0, 0.35), F.p(x, y, zb + 3.0 + 0.17), F.r(), "Stone_Wall_Dark", 0.08)
    mb.box((1.3, 1.3, 1.35), F.p(x, y, zb + 3.35 + 0.67), F.r(), "Lantern_Glow", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.3, 0.3, 1.4), F.p(x + sx * 0.66, y + sy * 0.66, zb + 3.35 + 0.7), F.r(), "Stone_Wall_Light", 0.0)
    mb.box((1.9, 1.9, 0.25), F.p(x, y, zb + 4.75 + 0.12), F.r(), "Stone_Wall_Dark", 0.0)
    mb.cyl(1.75, 0.95, F.p(x, y, zb + 5.0 + 0.47), F.r(0, 0, math.pi / 4), "Roof_DBGate_Tile", 4, r2=0.3, bevel=0.0)
    sphere(mb, F.p(x, y, zb + 6.15), 0.3, "Metal_Gold", F, us=8, vs=6)
    c = F.p(x, y, zb + 4.0)
    if name:
        light(name, "POINT", c, 120, (1.0, 0.62, 0.3), 0.3)
    col_box("GateDB", (2.0, 2.0, 6.4), F.p(x, y, 3.2), F.r())
    return c


def red_rail(mb, F, pts, rng):
    """guarda-corpo de laca vermelha com pinaculos de ouro (postes nas quinas e a cada ~3,6; 2 travessas)"""
    posts = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        a, b = Vector((ax, ay)), Vector((bx, by))
        ln = (b - a).length
        n = max(1, int(math.ceil(ln / 3.6)))
        for k in range(n + 1):
            q = a + (b - a) * (k / n)
            if not posts or (q - posts[-1]).length > 0.5:
                posts.append(q)
        ang = math.atan2(b.y - a.y, b.x - a.x) - math.pi / 2
        c = (a + b) / 2
        for zz, th in ((1.35, 0.42), (2.75, 0.5)):
            mb.box((0.42, ln, th), F.p(c.x, c.y, 0.15 + zz), F.r(0, 0, ang), "Wood_Lacquer_Red", 0.06)
        col_box("GateDB", (1.0, ln + 0.4, 4.0), F.p(c.x, c.y, 2.0), F.r(0, 0, ang))
    for i, q in enumerate(posts):
        if i == 0 or i == len(posts) - 1:
            continue          # as pontas ficam dentro das lanternas de pedra
        mb.box((0.72, 0.72, 3.0), F.p(q.x, q.y, 0.15 + 1.5), F.r(), "Wood_Lacquer_Red", 0.08)
        mb.cyl(0.46, 0.28, F.p(q.x, q.y, 3.29), F.r(), "Metal_Gold", 10, bevel=0.0)
        sphere(mb, F.p(q.x, q.y, 3.85), 0.42, "Metal_Gold", F, us=10, vs=7, sy=1.0)
        K.cone(mb, F.p(q.x, q.y, 4.15), F.p(q.x, q.y, 4.85), 0.16, 0.02, "Metal_Gold", n=6)


def court(F, rng):
    mb = MB("GATE_DB_Court", C, rng, detail="hero")
    for (x, y, k), s_in in zip(LIONS_XY, (1, -1)):
        lion(mb, F, x, y, k, s_in)
        col_box("GateDB", (5.0, 5.0, 10.6), F.p(x, y, 5.3), F.r())
    # guarda-corpo vermelho no nicho (recuado 0,55 da borda) + lanternas de pedra nas quinas
    for s in (-1, 1):
        pts = []
        bay = P.BAY
        for i, (x, y) in enumerate(bay):
            a = Vector(bay[max(0, i - 1)])
            b = Vector(bay[min(len(bay) - 1, i + 1)])
            e = (b - a).normalized()
            inward = Vector((-e.y, e.x))
            pts.append((s * (x + inward.x * 0.55), y + inward.y * 0.55))
        red_rail(mb, F, pts, rng)
        for (x, y), nm in ((bay[0], "L_GateDB_Lantern_%s" % ("R" if s > 0 else "L")), (bay[-1], None)):
            stone_lantern(mb, F, s * x, y, nm)
    ob = mb.finish()
    return ob


def orbs(F):
    for i, (x, y, z, k) in enumerate(ORBS):
        mb = MB("VFX_GATE_DB_Orb_%d" % (i + 1), "12_VFX_HELPERS", None, detail="hero")
        c = F.p(x, y, z)
        fwd = (F.p(0, -1, 0) - F.p(0, 0, 0)).normalized()
        dragon_ball(mb, c, 1.15, k, fwd, F=None)
        ob = mb.finish()
        ob["pivot"] = (c.x, c.y, c.z)
        ob["axis"] = (0.0, 0.0, 1.0)
        ob["bob"] = 0.6
        ob["rpm"] = 4.0 + i


# ------------------------------------------------------------------ contrato
def build_gate(gx, gy, gz, yaw):
    """portao Dragon Ball no ponto (gx, gy, gz) com +Y local = direcao de quem atravessa"""
    rng = random.Random(8201)
    F = GS.gate_frame(gx, gy, gz, yaw)
    frame(F, rng)
    open_glow(F)
    court(F, rng)
    orbs(F)
    GS.barrier(KEY, F, "DB_Energy_Glow", shape="circle", rng=rng)
    GS.markers(KEY, F, yaw)
    light("L_GateDB_Barrier", "POINT", F.p(0, -3.0, OH * 0.5), 260, (1.0, 0.55, 0.18), 1.0)


def build():
    gx, gy = L.gate_db_pos()
    build_gate(gx, gy, L.EXIT_Z, P.yaw())
