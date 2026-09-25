# il_gate_db - PECA-HEROI No 4: portao de compra DRAGON BALL na ilhota da saida (ref_13). Substitui
# il_blockout.db_gate(). Segue o padrao il_gate_std (vao 16 x 18, barreira circular de energia, cadeado, colisao de
# bloqueio e marcadores) sem mudar nada dele; aqui so a MOLDURA e o entorno.
# RODADA 2 (critica):
#   - MOON GATE: painel de pedra (espessura 1,2) preenche o retangulo do vao 16 x 18 com um FURO circular r 8,2 onde
#     fica a barreira circular do padrao; moldura de pedra em volta do furo e 4 GREGAS de ouro nos cantos (2 faces).
#     Os cantos que tem colisao agora sao pedra de verdade (antes eram "cantos vazados" com parede invisivel). Soleira
#     de 0,8 no pe do circulo; colisao do painel em degraus (continua passavel com o portao aberto).
#   - PROPORCAO da ref_13: a ancora de preco foi para dentro do vao (z 14) -> telhado, vigas e medalhao desceram
#     (cumeeira 29,4, pinaculo ate ~36,7; antes ~41). MEDALHAO = tambor de ouro (esfera de 4 estrelas nas 2 faces)
#     apoiado na viga mestra e invadindo o beiral, como na ref.
#   - TELHADO: fiadas em UM tom (UV constante: a textura de telha nao pinta mosaico de 3 tons); tom escuro so na
#     cumeeira, nas empenas e na testeira; ouro nos chifres dos cantos e no pinaculo.
#   - LEOES: il_lion.lion() (leao compartilhado com a entrada) em lion(); lion_own() ficou como alternativa local.
#   - ESFERAS flutuantes r 1,55 com estrelas de 0,84 de diametro; nada movel < 0,35.
#   - regras novas: bevel pela regra (il_exit_plan.XMB), secao >= 0,3 em frisos/gregas, folga >= 0,1 entre faces de
#     materiais diferentes, nada com todas as dimensoes < 0,35.
# Esferas: as 7 estao no portao (1, 2, 5, 6 flutuando; 3 e 7 com os leoes; 4 no medalhao).
import math, random
import bmesh
from mathutils import Vector, Matrix
import fm_lib
from fm_lib import S
import il_lib as IL
from il_lib import col_box, mk, light
import il_layout as L
import il_gate_std as GS
import il_exit_plan as P
from il_exit_plan import XMB as MB
import fm_portal_kit as K

_M = fm_lib.MATS.setdefault
_M("Roof_DBGate_Tile", (S(66, 80, 110), 0.6, 0.0, 0, None, 0.08))         # telha azul-ardosia (UM tom)
_M("Roof_DBGate_Ridge", (S(36, 40, 56), 0.6, 0.0, 0, None, 0.06))        # cumeeira / empena / testeira (escuro)
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
Z_UB0, Z_UB1 = 25.2, 26.4         # viga de cima (sob o beiral)
Z_PLATE = 27.3                    # topo do frechal
MED_Z, MED_R, MED_D = 23.9, 4.0, 2.45   # medalhao: centro, raio do tambor, meia profundidade (face 0,15 a frente da viga)
# (topo do tambor 27,9 = abaixo da superficie das telhas em y +-2,85: de cima nao aparece "lua" de ouro no telhado)
RX, Y0, YE = 19.6, 0.45, 7.7      # telhado: meia largura, inicio da agua, beiral
ZR, RH = 29.4, 3.15               # cumeeira (topo) e queda ate o beiral
LIFT, RLIFT = 2.3, 0.55           # subida das pontas do beiral e da cumeeira
# moon gate
HOLE_ZC, HOLE_R = OH / 2.0, 8.2   # furo do painel (a barreira do padrao tem r 8 no mesmo centro)
PANEL_T = 1.2                     # espessura do painel (y +-0,6)
PANEL_X, PANEL_Z = JX0 + 0.3, Z_LINTEL + 0.3    # o painel entra 0,3 nas ombreiras e na verga
RING_W, RING_H = 0.9, 0.3         # moldura do furo: largura radial e saliencia sobre a face do painel
LIONS_XY = [(-16.4, -4.0, 3), (16.4, -4.0, 7)]          # (x, y, estrelas) - a sapata nao encosta na do pilar
ORB_R = 1.55
ORBS = [(-14.6, -3.0, 15.6, 1), (-13.4, -5.4, 11.6, 2), (13.6, -5.2, 12.0, 5), (14.8, -2.9, 16.0, 6)]
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
        "CAM_GateDB_Front": (tuple(F.p(0, -60, 15)), tuple(F.p(0, 0, 17.5)), 24),
        "CAM_GateDB_Front34": (tuple(F.p(34, -40, 26)), tuple(F.p(0, 0, 16)), 22),
        "CAM_GateDB_Back": (tuple(F.p(16, 46, 20)), tuple(F.p(0, 0, 17)), 22),
        "CAM_GateDB_Side": (tuple(F.p(62, -12, 22)), tuple(F.p(0, -1, 17)), 22),
        "CAM_GateDB_SideL": (tuple(F.p(-62, 8, 22)), tuple(F.p(0, -1, 17)), 22),
        "CAM_GateDB_Player": (tuple(F.p(2.5, -22, 5.5)), tuple(F.p(0, 0, 12.0)), 18),
        "CAM_GateDB_Lion": (tuple(F.p(9.0, -16.0, 7.5)), tuple(F.p(16.0, -4.0, 6.5)), 30),
    }


CAMS = _cams()


# ------------------------------------------------------------------ utilidades
def sphere(mb, c, r, m, F=None, us=18, vs=11, sy=1.0):
    """esfera lisa (sombreamento suave); F: gira junto do portao; sy: achata no eixo y local (lente)"""
    ang = F.a if F is not None else 0.0
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(ang, 4, "Z") @ Matrix.Diagonal((1.0, sy, 1.0, 1.0))
    res = bmesh.ops.create_uvsphere(mb.bm, u_segments=us, v_segments=vs, radius=r, matrix=M)
    faces = mb._post(res["verts"], m, None, 0, 1)
    for f in faces:
        if f.is_valid:
            f.smooth = True


def star2d(ro, ri=None, spin=0.0):
    ri = ro * 0.46 if ri is None else ri
    return [((ro if i % 2 == 0 else ri) * math.cos(math.radians(90 + spin + 36 * i)),
             (ro if i % 2 == 0 else ri) * math.sin(math.radians(90 + spin + 36 * i))) for i in range(10)]


def star_decal(mb, c, r, n, pts2d, m, M=None, off=0.06, depth=0.12, up=(0, 0, 1)):
    """estrela colada numa esfera de raio r em volta da direcao n (M = matriz 3x3 opcional que deforma junto).
    Face de cima a r + off (>= 0,06 da casca: sem z-fight), parede ate r - depth."""
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


def star_size(k):
    """raio externo da estrela (diametro >= 0,8 em todas)"""
    return 0.62 if k <= 2 else (0.52 if k <= 4 else 0.42)


def ball_stars(mb, c, r, k, facing, M=None, size=None, up=(0, 0, 1)):
    """k estrelas no hemisferio voltado para 'facing'; espacamento >= 2,25 x raio da estrela (nao se tocam)"""
    f = Vector(facing).normalized()
    size = size or star_size(k)
    lay = STAR_LAYOUT[k]
    dmin = min((math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(lay) for b in lay[i + 1:]),
               default=1.0)
    sp = max(r * (0.5 if k <= 4 else 0.66), 2.25 * size / dmin)
    u = Vector(up) - f * Vector(up).dot(f)
    if u.length < 1e-4:
        u = Vector((1, 0, 0))
    u.normalize()
    side = u.cross(f).normalized()
    for a, b in lay:
        t = side * (a * sp) + u * (b * sp)
        d = (t + f * math.sqrt(max(0.0, r * r - t.length_squared))).normalized()
        star_decal(mb, c, r, d, star2d(size), "Crystal_DBGate_Star", M=M, off=0.06, depth=min(0.12, r * 0.08),
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


# ------------------------------------------------------------------ moon gate (painel com furo circular)
def _rect_hit(dx, dz, hx, z0, z1, zc):
    """ponto em que o raio (dx, dz) a partir de (0, zc) sai do retangulo [-hx, hx] x [z0, z1]"""
    ts = []
    if dx > 1e-9:
        ts.append(hx / dx)
    if dx < -1e-9:
        ts.append(-hx / dx)
    if dz > 1e-9:
        ts.append((z1 - zc) / dz)
    if dz < -1e-9:
        ts.append((z0 - zc) / dz)
    t = min(ts)
    return dx * t, zc + dz * t


def panel(mb, F, n=64):
    """painel de pedra (y +-PANEL_T/2) no retangulo [-PANEL_X, PANEL_X] x [0, PANEL_Z] com furo circular r HOLE_R:
    leque de quadrilateros convexos entre o circulo e o retangulo (+ as quinas), superficie interna do furo e
    bordas externas. Uma malha fechada, sem n-gono concavo."""
    bm = mb.bm
    hy = PANEL_T / 2
    corners = [(PANEL_X, 0.0), (PANEL_X, PANEL_Z), (-PANEL_X, PANEL_Z), (-PANEL_X, 0.0)]
    ca = [math.atan2(z - HOLE_ZC, x) % math.tau for x, z in corners]
    # anel de pontos: para cada angulo k, (circulo, retangulo); as quinas entram como pontos extras do retangulo
    circ, rect = [], []
    for k in range(n):
        a = math.tau * k / n
        dx, dz = math.cos(a), math.sin(a)
        circ.append((HOLE_R * dx, HOLE_ZC + HOLE_R * dz))
        rect.append(_rect_hit(dx, dz, PANEL_X, 0.0, PANEL_Z, HOLE_ZC))

    def vpair(x, z):
        return bm.verts.new(F.p(x, -hy, z)), bm.verts.new(F.p(x, hy, z))
    cv = [vpair(*p) for p in circ]
    rv = [vpair(*p) for p in rect]
    allv = [v for p in cv + rv for v in p]
    outer = []                  # contorno externo (retangulo) em ordem, com as quinas
    for k in range(n):
        a0 = math.tau * k / n
        a1 = math.tau * (k + 1) / n
        k1 = (k + 1) % n
        mids = [i for i, a in enumerate(ca) if a0 < a <= a1 + 1e-9 or (k == n - 1 and a < 1e-9)]
        cvs = [vpair(*corners[i]) for i in mids]
        allv += [v for p in cvs for v in p]
        # frente (y-): circulo k -> retangulo k -> quinas -> retangulo k1 -> circulo k1 (horario visto de frente)
        ring = [cv[k], rv[k]] + cvs + [rv[k1], cv[k1]]
        bm.faces.new([p[0] for p in ring])
        bm.faces.new([p[1] for p in reversed(ring)])
        outer += [rv[k]] + cvs
        # parede do furo
        bm.faces.new((cv[k][0], cv[k1][0], cv[k1][1], cv[k][1]))
    for i in range(len(outer)):
        a, b = outer[i], outer[(i + 1) % len(outer)]
        bm.faces.new((a[0], a[1], b[1], b[0]))
    mb._post(allv, "Stone_Wall_Light", None, 0, 1)


def greek_key(mb, F, x, z, sx, sz, y, t=0.32, s=1.8):
    """greca (espiral quadrada) de ouro com secao t (>= 0,3) num quadrado de lado s: canto externo em (x, z),
    crescendo para (-sx, -sz); saliencia t sobre a face (centro em y). Caminho: 3 lados do quadrado + volta interna."""
    h = t / 2
    st = t + (s - 3 * t) / 2                     # passo da volta interna (barra + vao)
    path = [(h, h), (s - h, h), (s - h, s - h), (h, s - h), (h, h + st), (s - h - st, h + st)]
    for (u0, v0), (u1, v1) in zip(path, path[1:]):
        umin, umax = min(u0, u1) - h, max(u0, u1) + h
        vmin, vmax = min(v0, v1) - h, max(v0, v1) + h
        cu, cv = (umin + umax) / 2, (vmin + vmax) / 2
        mb.box((umax - umin, t, vmax - vmin), F.p(x - sx * cu, y, z - sz * cv), F.r(), "Metal_Gold", 0.0)


def moon_gate(mb, F):
    panel(mb, F)
    hy = PANEL_T / 2
    ux = F.p(1, 0, 0) - F.p(0, 0, 0)
    uz = Vector((0, 0, 1))
    for sy in (-1, 1):
        # moldura do furo (pedra quente, 0,3 de saliencia) - entra nas ombreiras dos lados
        K.ring(mb, F.p(0, sy * (hy + RING_H / 2), HOLE_ZC), HOLE_R + RING_W / 2, ux, uz, RING_W, RING_H,
               "Stone_Paving_Warm", n=56)
        # 4 gregas de ouro nos cantos do painel (a 0,25 da ombreira e da verga/piso)
        y = sy * (hy + 0.17)
        for sx in (-1, 1):
            for sz, zc in ((1, Z_LINTEL - 0.25), (-1, 0.25)):
                greek_key(mb, F, sx * (JX0 - 0.25), zc, sx, sz, y)


def moon_gate_col(F):
    """colisao do painel (fica com o portao aberto): soleira no centro + degraus sob a curva do furo nos 2 lados.
    Os cantos de cima ficam sem colisao (acima do alcance do pulo, z > 12)."""
    col_box("GateDB", (5.2, PANEL_T, 0.8), F.p(0, 0, 0.4), F.r())
    for s in (-1, 1):
        for x0, x1 in ((2.6, 4.6), (4.6, 6.6), (6.6, JX0 + 0.2)):
            top = HOLE_ZC - math.sqrt(max(0.0, HOLE_R ** 2 - x0 ** 2))
            col_box("GateDB", (x1 - x0, PANEL_T, top), F.p(s * (x0 + x1) / 2, 0, top / 2), F.r())


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
        h = Z_UB0 - 4.3
        mb.cyl(PR, h, F.p(x, 0, 4.3 + h / 2), F.r(), "Wood_Lacquer_Red", 20, bevel=0.0)
        for zc, hh in ((15.6, 0.5), (16.3, 0.3)):
            mb.cyl(PR + 0.22, hh, F.p(x, 0, zc), F.r(), "Metal_Gold", 20, bevel=0.0)
        mb.cyl(PR + 0.35, 0.8, F.p(x, 0, Z_BEAM0 - 0.4), F.r(), "Metal_Gold", 20, bevel=0.0)
        mb.cyl(PR + 0.25, 0.7, F.p(x, 0, Z_UB0 - 0.45), F.r(), "Metal_Gold", 20, bevel=0.0)
        # ombreira de pedra lisa com um filete de ouro (secao 0,34) em cada face
        jx = s * (JX0 + JX1) / 2
        mb.box((JX1 - JX0, 2.2, Z_LINTEL), F.p(jx, 0, Z_LINTEL / 2), F.r(), "Stone_Wall_Light", 0.12)
        for sy in (-1, 1):
            mb.box((0.34, 0.34, Z_LINTEL - 2.6), F.p(jx, sy * 1.25, 1.3 + (Z_LINTEL - 2.6) / 2), F.r(), "Metal_Gold",
                   0.0)
    # verga de pedra com 2 filetes de ouro (secao 0,34)
    mb.box((2 * JX1, 2.2, Z_BEAM0 - Z_LINTEL), F.p(0, 0, (Z_LINTEL + Z_BEAM0) / 2), F.r(), "Stone_Wall_Light", 0.12)
    for sy in (-1, 1):
        for zz in (Z_LINTEL + 0.3, Z_BEAM0 - 0.3):
            mb.box((2 * JX1 - 1.0, 0.34, 0.34), F.p(0, sy * 1.25, zz), F.r(), "Metal_Gold", 0.0)


def beams_and_frieze(mb, F):
    # viga mestra (passa pelos pilares) com testeiras e filete de ouro
    mb.box((32.4, 3.0, Z_BEAM1 - Z_BEAM0), F.p(0, 0, (Z_BEAM0 + Z_BEAM1) / 2), F.r(), "Wood_Lacquer_Red", 0.15)
    for s in (-1, 1):
        mb.box((0.4, 3.3, 2.0), F.p(s * 16.3, 0, (Z_BEAM0 + Z_BEAM1) / 2), F.r(), "Metal_Gold", 0.0)
        mb.box((31.6, 0.34, 0.34), F.p(0, s * 1.62, Z_BEAM1 - 0.4), F.r(), "Metal_Gold", 0.0)
    # friso (tabua de laca entre os pilares) com moldura de ouro nas duas faces
    zf0, zf1 = Z_BEAM1, Z_UB0
    mb.box((2 * (PX - PR) + 0.2, 0.7, zf1 - zf0), F.p(0, 0, (zf0 + zf1) / 2), F.r(), "Wood_Lacquer_Red", 0.0)
    for sy in (-1, 1):
        y = sy * 0.5
        for zz in (zf0 + 0.4, zf1 - 0.4):
            mb.box((2 * (PX - PR) - 0.6, 0.34, 0.34), F.p(0, y, zz), F.r(), "Metal_Gold", 0.0)
        for xx in (-(PX - PR) + 0.5, (PX - PR) - 0.5):
            mb.box((0.34, 0.34, zf1 - zf0 - 0.46), F.p(xx, y, (zf0 + zf1) / 2), F.r(), "Metal_Gold", 0.0)
    # misulas (blocos empilhados) sobre a viga, dos dois lados do medalhao, e escoras nas pontas
    for s in (-1, 1):
        x = s * 6.3
        mb.box((1.9, 2.8, 0.9), F.p(x, 0, Z_BEAM1 + 0.45), F.r(), "Wood_Lacquer_Red", 0.0)
        mb.box((2.2, 3.1, 0.34), F.p(x, 0, Z_BEAM1 + 1.07), F.r(), "Metal_Gold", 0.0)
        mb.box((1.3, 2.3, 0.8), F.p(x, 0, Z_BEAM1 + 1.64), F.r(), "Wood_Lacquer_Red", 0.0)
        mb.box((1.0, 1.0, Z_UB0 - Z_BEAM1), F.p(s * 14.9, 0, (Z_UB0 + Z_BEAM1) / 2), F.r(), "Wood_Lacquer_Red", 0.0)
        mb.box((1.9, 2.4, 0.6), F.p(s * 14.9, 0, Z_UB0 - 0.3), F.r(), "Wood_Lacquer_Red", 0.0)
        mb.box((1.4, 1.4, 0.34), F.p(s * 14.9, 0, Z_BEAM1 + 0.17), F.r(), "Metal_Gold", 0.0)
    # misulas em degraus (dougong) no alto de cada pilar, para a frente e para tras
    for s in (-1, 1):
        x = s * PX
        for sy in (-1, 1):
            for (dz, reach, w) in ((-2.3, 3.2, 1.3), (-1.45, 4.4, 1.45), (-0.6, 5.7, 1.6)):
                ln = reach - PR * 0.6
                z0 = Z_UB0 + dz
                mb.box((w, ln, 0.85), F.p(x, sy * (PR * 0.6 + ln / 2), z0 + 0.42), F.r(), "Wood_Lacquer_Red", 0.0)
                mb.box((w + 0.5, 0.9, 0.34), F.p(x, sy * (reach - 0.45), z0 + 0.85 + 0.17), F.r(), "Metal_Gold", 0.0)
            mb.box((1.8, 1.3, 0.7), F.p(x, sy * 5.25, Z_UB0 + 0.6), F.r(), "Wood_Lacquer_Red", 0.0)
    # viga de cima + frechal, cortados pelo tambor do medalhao (as pontas entram no tambor)
    for s in (-1, 1):
        xa, xb = 3.0, 17.6
        mb.box((xb - xa, 4.6, Z_UB1 - Z_UB0), F.p(s * (xa + xb) / 2, 0, (Z_UB0 + Z_UB1) / 2), F.r(),
               "Wood_Lacquer_Red", 0.06)
        for sy in (-1, 1):
            mb.box((xb - xa - 0.4, 0.34, 0.34), F.p(s * (xa + xb - 0.4) / 2, sy * 2.4, Z_UB0 + 0.32), F.r(),
                   "Metal_Gold", 0.0)
        mb.box((0.4, 4.9, 1.2), F.p(s * 17.8, 0, (Z_UB0 + Z_UB1) / 2), F.r(), "Metal_Gold", 0.0)
        xa2, xb2 = 2.0, 16.8
        mb.box((xb2 - xa2, 3.2, Z_PLATE - Z_UB1), F.p(s * (xa2 + xb2) / 2, 0, (Z_UB1 + Z_PLATE) / 2), F.r(),
               "Wood_Lacquer_Red", 0.0)


def medallion(mb, F):
    """medalhao da esfera de 4 estrelas: TAMBOR de ouro (r 4, 4,9 de fundo) encaixado na viga mestra, aro saliente e
    lente laranja com 4 estrelas nas duas faces (a frente invade o beiral, como na ref_13)"""
    c = F.p(0, 0, MED_Z)
    ux = F.p(1, 0, 0) - F.p(0, 0, 0)
    uy = F.p(0, 1, 0) - F.p(0, 0, 0)
    mb.cyl(MED_R, 2 * MED_D, c, F.r(math.pi / 2, 0, 0), "Metal_Gold", 36, bevel=0.0)
    for sy in (-1, 1):
        fc = c + uy * (sy * MED_D)
        K.ring(mb, fc + uy * (sy * 0.2), MED_R - 0.45, ux, Vector((0, 0, 1)), 0.9, 0.4, "Metal_Gold", n=36)
        dragon_ball(mb, fc, MED_R - 0.95, 4, uy * sy, F=F, sy=0.36)


def roof(mb, F):
    """telhado curvo de telhas em canal (duas aguas, cada uma um bloco fechado) com beiral subindo nas pontas.
    Fiadas em UM tom (UV constante); testeira/empena/cumeeira escuras; chifres e pinaculo de ouro."""
    per = 2 * RX / 22.0
    nx = 88
    ns = 4
    th = 0.55

    def zt(x, s):
        ax = abs(x) / RX
        return ZR - RH * (1.0 - (1.0 - s) ** 1.5) + LIFT * ax ** 3 * s ** 1.4 + RLIFT * ax ** 4

    def corr(x):                           # canal arredondado (perfil suave, sem cuspide)
        return 0.3 * math.sin(math.pi * x / per) ** 2

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
        faces = mb._post(allv, "Roof_DBGate_Tile", None, 0, 1)
        tops = {f for r0, r1 in zip(top, top[1:]) for v in r0 for f in v.link_faces if f.normal.z > 0.2}
        for f in faces:                       # UM tom: todas as faces leem o mesmo texel da textura de telha
            for lp in f.loops:
                lp[mb.uvl].uv = (0.5, 0.5)
            if f in tops:                     # fiadas lisas (o canal le como telha, sem listra dura de sombra)
                f.smooth = True
        # testeira escura no beiral e nas empenas (UV constante: um tom, sem o mosaico da textura de telha)
        with _Faces(mb, uv=(0.5, 0.5)):
            eave = [F.p(-RX + 2 * RX * i / 32, side * (YE + 0.12), zt(-RX + 2 * RX * i / 32, 1.0))
                    for i in range(33)]      # testeira cobre as pontas das telhas (zt - 0,55 .. zt + 0,3)
            mb.sweep(eave, [(-0.3, -0.72), (0.3, -0.72), (0.3, 0.48), (-0.3, 0.48)], "Roof_DBGate_Ridge", True)
            for sx in (-1, 1):
                verge = [F.p(sx * (RX + 0.1), side * (Y0 + (YE - Y0) * j / 6), zt(RX, j / 6) - 0.1) for j in range(7)]
                mb.sweep(verge, [(-0.25, -0.36), (0.25, -0.36), (0.25, 0.4), (-0.25, 0.4)], "Roof_DBGate_Ridge",
                         True)
        for sx in (-1, 1):
            # chifre de ouro no canto do beiral (sobe e abre para fora)
            c0 = F.p(sx * (RX + 0.15), side * (YE + 0.15), zt(RX, 1.0) - 0.1)
            out = (F.p(sx, side * 0.7, 0) - F.p(0, 0, 0)).normalized()
            pts = [c0, c0 + out * 0.7 + Vector((0, 0, 0.35)), c0 + out * 1.25 + Vector((0, 0, 1.05)),
                   c0 + out * 1.45 + Vector((0, 0, 1.9))]
            K.taper_tube(mb, pts, [0.46, 0.4, 0.3, 0.18], "Metal_Gold", n=7)
    # cumeeira escura com as pontas viradas para cima + chifres de ouro nas pontas
    pts = []
    for i in range(25):
        x = -RX - 0.3 + (2 * RX + 0.6) * i / 24
        pts.append(F.p(x, 0, ZR + RLIFT * (min(abs(x), RX) / RX) ** 4 + 0.3))
    with _Faces(mb, uv=(0.5, 0.5)):
        mb.sweep(pts, [(-0.8, -0.6), (0.8, -0.6), (0.8, 0.5), (-0.8, 0.5)], "Roof_DBGate_Ridge", True)
    for sx in (-1, 1):
        a = F.p(sx * (RX + 0.2), 0, ZR + RLIFT + 0.3)
        pts = [a, a + (F.p(sx * 0.8, 0, 0) - F.p(0, 0, 0)) + Vector((0, 0, 0.45)),
               a + (F.p(sx * 1.35, 0, 0) - F.p(0, 0, 0)) + Vector((0, 0, 1.4)),
               a + (F.p(sx * 1.5, 0, 0) - F.p(0, 0, 0)) + Vector((0, 0, 2.5))]
        K.taper_tube(mb, pts, [0.66, 0.58, 0.4, 0.2], "Metal_Gold", n=8)
    # pinaculo no centro da cumeeira: tambor vermelho, domo de ouro, esfera e agulha (tip ~ ZR + 7,3)
    z = ZR + 0.75
    mb.cyl(1.6, 1.1, F.p(0, 0, z + 0.55), F.r(), "Wood_Lacquer_Red", 16, bevel=0.0)
    mb.cyl(1.8, 0.34, F.p(0, 0, z + 1.27), F.r(), "Metal_Gold", 16, bevel=0.0)
    sphere(mb, F.p(0, 0, z + 1.44), 1.55, "Metal_Gold", F, us=16, vs=10, sy=1.0)
    mb.cyl(0.4, 0.8, F.p(0, 0, z + 3.3), F.r(), "Metal_Gold", 10, bevel=0.0)
    sphere(mb, F.p(0, 0, z + 4.0), 0.55, "Metal_Gold", F, us=12, vs=8)
    K.cone(mb, F.p(0, 0, z + 4.4), F.p(0, 0, z + 6.6), 0.4, 0.04, "Metal_Gold", n=8)


def frame(F, rng):
    mb = MB("GATE_DB_Frame", C, rng, detail="hero")
    pillars_and_jambs(mb, F)
    moon_gate(mb, F)
    beams_and_frieze(mb, F)
    medallion(mb, F)
    roof(mb, F)
    ob = mb.finish()
    # colisao: pilares com base (altura toda), ombreiras e o painel do moon gate
    for s in (-1, 1):
        col_box("GateDB", (4.8, 4.8, Z_UB1), F.p(s * PX, 0, Z_UB1 / 2), F.r())
        col_box("GateDB", (JX1 - JX0, 2.2, Z_LINTEL), F.p(s * (JX0 + JX1) / 2, 0, Z_LINTEL / 2), F.r())
    moon_gate_col(F)
    return ob


def open_glow(F):
    """contorno dourado do FURO (so acende ao desbloquear): anel na frente da moldura, nas 2 faces"""
    mb = MB("GATE_DB_OpenGlow", C, None, detail="hero")
    ux = F.p(1, 0, 0) - F.p(0, 0, 0)
    for sy in (-1, 1):
        y = sy * (PANEL_T / 2 + RING_H + 0.2)
        K.ring(mb, F.p(0, y, HOLE_ZC), HOLE_R + 0.2, ux, Vector((0, 0, 1)), 0.4, 0.34, "Metal_DBGate_Glow", n=48)
    ob = mb.finish()
    ob["gate"] = KEY
    ob["gate_part"] = "open_glow"
    ob["gate_state"] = "unlocked"
    return ob


# ------------------------------------------------------------------ leoes, esferas, guarda-corpo, lanternas
def pedestal(mb, F, x, y):
    mb.box((5.0, 5.0, 0.55), F.p(x, y, 0.27), F.r(), "Stone_Wall_Dark", 0.12)
    mb.box((4.4, 4.4, 3.0), F.p(x, y, 0.55 + 1.5), F.r(), "Stone_Wall_Light", 0.2)
    mb.box((4.9, 4.9, 0.5), F.p(x, y, 3.55 + 0.25), F.r(), "Stone_Wall_Dark", 0.12)
    for sy in (-1, 1):            # almofada rebaixada na frente e atras (saliente 0,15: sem z-fight)
        mb.box((2.8, 0.3, 1.5), F.p(x, y + sy * 2.2, 2.05), F.r(), "Stone_Wall_Dark", 0.0)


class _Faces:
    """faces criadas dentro do bloco (por identidade: o bmesh reaproveita posicoes de faces apagadas) recebem UV
    constante (um so tom da textura de detalhe: telhas escuras, massas do leao) e, com smooth=True, sombreado liso"""

    def __init__(self, mb, smooth=False, uv=(0.37, 0.61)):
        self.mb, self.smooth, self.uv = mb, smooth, uv

    def __enter__(self):
        self.before = set(self.mb.bm.faces)
        return self

    def __exit__(self, *a):
        uvl = self.mb.uvl
        for f in self.mb.bm.faces:
            if f not in self.before:
                if self.smooth:
                    f.smooth = True
                for lp in f.loops:
                    lp[uvl].uv = self.uv


def _Smooth(mb):
    return _Faces(mb, smooth=True)


def lion_own(mb, F, x, y, stars, s_in, k=1.15):
    """leao de pedra (shishi) sentado, estilizado: cabeca GRANDE, juba em LOBOS arredondados em volta da cabeca,
    peito e ancas lisos, a pata de fora POUSADA sobre a esfera do dragao (no canto do pedestal)"""
    base = F.p(x, y, 4.05)
    ang = F.a + math.pi + s_in * math.radians(14)
    FL = type(F)(base.x, base.y, base.z, ang)

    def Q(a, b, c):
        return FL.p(a * k, b * k, c * k)
    m = "Stone_Wall_Light"
    d = "Stone_Wall_Dark"
    mb.box((3.6 * k, 4.2 * k, 0.4), FL.p(0, 0.0, 0.2), FL.r(), d, 0.0)
    # ancas e patas de tras (sentado)
    with _Smooth(mb):
        for sx in (-1, 1):
            mb.ico(1.0 * k, Q(sx * 0.95, -0.9, 1.15), m, 1, (0.9, 1.25, 1.0), rot=FL.r())
            mb.ico(0.62 * k, Q(sx * 1.05, 0.05, 0.62), m, 1, (1.0, 1.35, 0.7), rot=FL.r())
        # peito (massa inclinada) e barriga
        mb.ico(1.0 * k, Q(0, -0.2, 2.3), m, 1, (1.2, 1.1, 1.65), rot=FL.r(-0.22))
    # esfera do dragao no canto da frente, do lado de fora; pata de fora POUSADA em cima dela
    br = 1.25
    bc = Q(s_in * 0.95, 1.05, (0.36 + br) / k)
    fwd = (FL.p(0, 1, 0) - FL.p(0, 0, 0)).normalized()
    dragon_ball(mb, bc, br, stars, fwd + Vector((0, 0, 0.35)), F=None)
    with _Smooth(mb):
        for sx in (-1, 1):
            if sx == s_in:
                # braco desce do ombro ate o alto da esfera; pata larga pousada
                top_b = bc + Vector((0, 0, br - 0.05))
                mb.rod(Q(sx * 0.8, 0.55, 2.5), top_b + Vector((0, 0, 0.25)) - fwd * 0.3, 0.46 * k, m, 8)
                mb.ico(0.62 * k, top_b + Vector((0, 0, 0.18)) + fwd * 0.05, m, 1, (1.2, 1.25, 0.6), rot=FL.r())
            else:
                mb.rod(Q(sx * 0.75, 0.75, 2.5), Q(sx * 0.8, 1.15, 0.5), 0.46 * k, m, 8)
                mb.ico(0.55 * k, Q(sx * 0.8, 1.45, 0.62), m, 1, (1.1, 1.3, 0.65), rot=FL.r())
        # cabeca GRANDE (acima e a frente do peito) + juba em 9 lobos arredondados em volta
        hc = (0.0, 0.75, 4.35)
        mb.ico(1.3 * k, Q(*hc), m, 2, (1.18, 1.0, 1.05), rot=FL.r())
        for i in range(9):
            a = math.radians(-100 + 25 * i)       # arco de lobos por cima e pelos lados (abre embaixo: queixo)
            rx, rz = 1.55 * math.cos(math.radians(90) + a), 1.45 * math.sin(math.radians(90) + a)
            mb.ico(0.62 * k, Q(hc[0] + rx, hc[1] - 0.35, hc[2] + rz), m, 1, (1.0, 0.8, 1.0), rot=FL.r())
        # rabo em cacho (2 lobos)
        mb.ico(0.8 * k, Q(0, -1.95, 2.9), m, 1, (0.9, 0.75, 1.15), rot=FL.r())
        mb.ico(0.55 * k, Q(0, -2.1, 3.8), m, 1, (1.0, 0.8, 1.0), rot=FL.r())
    # focinho arredondado, nariz, boca aberta (escura), sobrancelhas bravas em lobos, orelhas
    with _Smooth(mb):
        mb.ico(0.72 * k, Q(0, 1.9, 4.0), m, 2, (1.3, 0.85, 0.78), rot=FL.r())
        for sx in (-1, 1):
            mb.ico(0.42 * k, Q(sx * 0.5, 1.85, 4.72), m, 1, (1.25, 0.85, 0.75), rot=FL.r(0, sx * 0.35, 0))
            mb.ico(0.36 * k, Q(sx * 1.05, 0.45, 5.45), m, 1, (0.8, 0.6, 1.1), rot=FL.r())
        mb.ico(0.3 * k, Q(0, 2.45, 4.25), d, 1, (1.5, 0.9, 0.9), rot=FL.r())
        mb.ico(0.42 * k, Q(0, 2.15, 3.42), d, 1, (1.55, 0.9, 0.62), rot=FL.r())


def lion(mb, F, x, y, stars, s_in):
    """pedestal + leao COMPARTILHADO (il_lion.lion, dono: zona entrance) com os materiais que o portao ja usa (corpo
    Stone_Wall_Dark, juba Stone_Wall_Light, olhos/nariz Roof_DBGate_Ridge, boca Wood_Lacquer_Red) e a esfera do dragao
    sob a pata de fora. Escala 0,82: topo em ~10,6 (a colisao do court). lion_own() ficou como referencia."""
    import il_lion
    pedestal(mb, F, x, y)
    base = F.p(x, y, 4.05)
    yaw = F.a + math.pi + s_in * math.radians(14)

    def ball(mb_, c, r, fwd):
        dragon_ball(mb_, c, r, stars, fwd + Vector((0, 0, 0.35)), F=None)
    il_lion.lion(mb, base.x, base.y, base.z, yaw, s=0.82, side=s_in, body_m="Stone_Wall_Dark",
                 mane_m="Stone_Wall_Light", dark_m="Roof_DBGate_Ridge", mouth_m="Wood_Lacquer_Red", ball=ball,
                 ball_r=1.52)


def stone_lantern(mb, F, x, y, name=None):
    """lanterna de pedra quadrada (ref_13): sapata, fuste, prato, camara acesa com montantes, chapeu de telha"""
    zb = 0.15
    mb.box((2.0, 2.0, 0.6), F.p(x, y, zb + 0.3), F.r(), "Stone_Wall_Dark", 0.0)
    mb.box((1.2, 1.2, 2.4), F.p(x, y, zb + 0.6 + 1.2), F.r(), "Stone_Wall_Light", 0.06)
    mb.box((2.0, 2.0, 0.35), F.p(x, y, zb + 3.0 + 0.17), F.r(), "Stone_Wall_Dark", 0.0)
    mb.box((1.3, 1.3, 1.55), F.p(x, y, zb + 3.35 + 0.7), F.r(), "Lantern_Glow", 0.0)      # pontas entram 0,1
    for sx in (-1, 1):
        for sy in (-1, 1):
            mb.box((0.36, 0.36, 1.55), F.p(x + sx * 0.66, y + sy * 0.66, zb + 3.35 + 0.7), F.r(), "Stone_Wall_Light",
                   0.0)
    mb.box((1.9, 1.9, 0.3), F.p(x, y, zb + 4.75 + 0.15), F.r(), "Stone_Wall_Dark", 0.0)
    with _Faces(mb, uv=(0.5, 0.5)):
        mb.cyl(1.75, 0.95, F.p(x, y, zb + 5.05 + 0.47), F.r(0, 0, math.pi / 4), "Roof_DBGate_Ridge", 4, r2=0.3,
               bevel=0.0)
    sphere(mb, F.p(x, y, zb + 6.2), 0.3, "Metal_Gold", F, us=8, vs=6)
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
            mb.box((0.42, ln, th), F.p(c.x, c.y, 0.15 + zz), F.r(0, 0, ang), "Wood_Lacquer_Red", 0.0)
        col_box("GateDB", (1.0, ln + 0.4, 4.0), F.p(c.x, c.y, 2.0), F.r(0, 0, ang))
    for i, q in enumerate(posts):
        if i == 0 or i == len(posts) - 1:
            continue          # as pontas ficam dentro das lanternas de pedra
        mb.box((0.72, 0.72, 3.0), F.p(q.x, q.y, 0.15 + 1.5), F.r(), "Wood_Lacquer_Red", 0.0)
        # pinaculo de ouro barato (~50 tris): colar octogonal + bulbo em bipiramide de 6 lados + agulha
        mb.cyl(0.46, 0.3, F.p(q.x, q.y, 3.3), F.r(), "Metal_Gold", 8, bevel=0.0)
        with _Faces(mb, smooth=True, uv=(0.5, 0.5)):
            K.octa(mb, F.p(q.x, q.y, 3.88), 0.44, 0.44, "Metal_Gold", rot=F.a, n=6)
        K.cone(mb, F.p(q.x, q.y, 4.2), F.p(q.x, q.y, 4.85), 0.18, 0.03, "Metal_Gold", n=6)


def court(F, rng):
    mb = MB("GATE_DB_Court", C, rng, detail="near", vcap=1)
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
        dragon_ball(mb, c, ORB_R, k, fwd, F=None)
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
