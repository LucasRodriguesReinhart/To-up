# il_gate_op - portao de compra ONE PIECE (area 5): "PORTAO DO TIMAO". Dono: zona gates.
# O arco E um TIMAO de navio: aro interno e aro externo de madeira envernizada com o vao aberto entre eles, 7 raios
# torneados que atravessam o vao e saem como PUNHOS alem do aro externo (o sol de punhos e a silhueta do portao), cravos
# de latao nos cruzamentos. Os aros pousam em duas ESTACAS de amarracao (tora redonda, chapeu largo, cintas de ferro,
# corda em helice, argolas). No alto, a BUSSOLA: tambor de latao com rosa-dos-ventos azul/vermelha e agulha acesa que
# gira (VFX), e um CHAPEU DE PALHA de fita vermelha pousado no punho de cima. Dos punhos laterais pendem lanternas de
# navio com energia azul-agua.
# Ornamentos laterais (fora de +-12): ANCORA em pe com corrente ate o poste (esquerda), barris com rolos de corda
# (direita) e dois cabecos de amarracao na frente com cabo ate os postes. Barreira azul (P_OP_Glow) em arco.
#
# PLANO (referencial do portao; z relativo ao tabuleiro):
#   vao 16 x 18 (arco: nascenca z 10, semicirculo r 8)     estacas r 1.8 em x = +-10.3 (face interna 8.5), z 0..10.4
#   chapeu r 2.25 (x 8.05..12.55), z 10.4..11.2 | timao: centro (0, 10), aro interno r 8.05..9.05, externo 11.3..12.3
#   raios a 10, 36.7, 63.3, 90, ... graus, de r 8.4 ate o punho em r 15.55 (topo z 25.6, laterais x +-15.3)
#   bussola r 2.3 em z 21.4 | chapeu de palha no punho de cima (aba r 2.7, topo ~27) | lanternas x +-14.8, z ~8.3..11.6
#   ancora x -14.7, y -2.4 (pa ate -17.3) | barris x 12.9..16.4 | cabecos (+-13.3, -5.6)
# RODADA 2 (critica: "papelao; sem soleira/pedestais/emblemas; nao e familia do DB"):
#   - PROFUNDIDADE: atras de cada estaca, um DUQUE D'ALBA (estaca de apoio r 1,25 em y 6) ligado por 2 travessas e uma
#     escora inclinada ate o chapeu da estaca, com amarras de corda -> moldura de y -2,3 a 7,3;
#   - kit de familia: soleira 22 x 10, plintos, 2 pedestais 4x4x4 com CABECO DE AMARRACAO duplo + BARRIL (o guardiao),
#     2 lanternas de pedra (camara azul-agua) e 4 CHAPEUS DE PALHA flutuantes (VFX_GATE_OnePiece_Hat_*);
#     os barris e cabecos soltos no chao sairam; a ancora foi para tras, encostada no duque d'alba esquerdo;
#   - folgas >= 0,1: cintas de ferro r + 0,12, fita do chapeu 0,12 fora da copa, latao do aro fora dos aneis de energia.
import math, random
from mathutils import Vector
import fm_lib
from fm_lib import S
import il_gate_std as GS
import il_gates_kit as GK
from il_gates_kit import G, GMB, star
import fm_portal_kit as K

KEY = "OnePiece"
# ------------------------------------------------------------------ material novo (1 dos 12 da zona)
fm_lib.MATS.setdefault("Wood_GateOP_Helm", (S(188, 110, 52), 0.55, 0.0, 0, None, 0.10))   # madeira envernizada
fm_lib.MATS.setdefault("Cloth_GateOP_Straw", (S(236, 200, 112), 0.85, 0.0, 0, None, 0.06))  # palha do chapeu
HELM, WD, WP, STRAW = "Wood_GateOP_Helm", "Wood_Dark", "Wood_Plank", "Cloth_GateOP_Straw"
ROPE, BRASS, IRON = "Rope", "Metal_Brass", "Metal_Dark"
CREAM, BLUE, RED = "Emblem_Cream", "P_OP_Blue", "Cloth_Red"
GLOW = "P_OP_Glow"                 # barreira
AQUA = "Crystal_Blue_Core"         # energia azul-agua das lanternas e da agulha (Neon)

CAMS = GK.cams_for(KEY)

ZC = 10.0                          # centro do timao = centro do semicirculo da barreira
RI0, RI1 = 8.05, 9.05              # aro interno
RO0, RO1 = 11.3, 12.3              # aro externo
SPOKES = [10.0 + (160.0 / 6) * k for k in range(7)]
PX, PR = 10.3, 1.8                 # estacas (face interna 8.5, chapeu ate 8.05)
COMP_Z, COMP_R = 21.4, 2.3         # bussola
A = "Gate" + KEY


def _posts(g, mb):
    """estacas de amarracao: tora redonda, chapeu largo (recebe os dois aros), cinta de ferro em baixo e sob o
    chapeu, corda em helice no meio com amarras nas pontas, argola de amarracao na frente e atras"""
    for s in (-1, 1):
        x = s * PX
        g.cyl(mb, PR, 10.4, (x, 0.0, 5.2), WD, 14, bev=0.12)
        g.cyl(mb, PR + 0.45, 0.62, (x, 0.0, 10.71), WD, 14, bev=0.16)
        g.cyl(mb, PR + 0.3, 0.26, (x, 0.0, 11.1), WD, 14, r2=PR - 0.2, bev=0.0)
        for z, h in ((0.48, 0.46), (10.1, 0.36)):
            g.cyl(mb, PR + 0.12, h, (x, 0.0, z), IRON, 14, bev=0.0)
        for z in (4.75, 7.65):
            g.cyl(mb, PR + 0.14, 0.34, (x, 0.0, z), ROPE, 14, bev=0.0)
        pts = []
        for i in range(41):
            t = i / 40.0
            a = math.tau * 2.5 * t
            pts.append((x + math.cos(a) * (PR + 0.12), math.sin(a) * (PR + 0.12), 4.95 + 2.5 * t))
        g.tube(mb, pts, [0.2] * len(pts), ROPE, 6)
        for yy in (-1, 1):
            g.box(mb, x - 0.3, x + 0.3, yy * (PR - 0.05), yy * (PR + 0.25), 2.9, 3.5, IRON, 0.0)
            g.ring(mb, x, 2.6, 0.55, 0.22, 0.22, yy * (PR + 0.25), IRON, n=12)


def _helm(g, mb):
    g.ring(mb, 0.0, ZC, (RI0 + RI1) / 2, RI1 - RI0, 1.3, 0.0, HELM, 0.0, 180.0, 40)
    g.ring(mb, 0.0, ZC, (RO0 + RO1) / 2, RO1 - RO0, 1.1, 0.0, HELM, 0.0, 180.0, 48)
    # faixa de latao nas faces do aro interno (frente e costas)
    for y in (-0.7, 0.7):
        g.ring(mb, 0.0, ZC, (RI0 + RI1) / 2, 0.3, 0.16, y, BRASS, 0.0, 180.0, 40)
    prof = [(8.4, 0.40), (9.2, 0.40), (9.65, 0.56), (10.2, 0.36), (10.75, 0.52), (11.35, 0.40), (12.3, 0.40),
            (12.8, 0.52), (13.35, 0.33), (14.25, 0.46), (14.85, 0.56), (15.3, 0.47), (15.55, 0.2)]
    for a in SPOKES:
        c, s_ = math.cos(math.radians(a)), math.sin(math.radians(a))
        g.tube(mb, [(c * r, 0.0, ZC + s_ * r) for r, _ in prof], [w for _, w in prof], HELM, 8)
        for rr, yy in (((RI0 + RI1) / 2, 0.72), ((RO0 + RO1) / 2, 0.62)):
            for sg in (-1, 1):
                g.cyl(mb, 0.34, 0.2, (c * rr, sg * yy, ZC + s_ * rr), BRASS, 8, bev=0.0, axis="y")
        # anel de latao no pescoco do punho
        g.cyl(mb, 0.5, 0.22, (c * 12.55, 0.0, ZC + s_ * 12.55), BRASS, 8, bev=0.0)
    return


def _compass(g, mb):
    """tambor de latao atravessando o aro, rosa-dos-ventos nas duas faces (a agulha acesa da frente e VFX)"""
    g.cyl(mb, COMP_R, 2.5, (0.0, 0.0, COMP_Z), BRASS, 28, bev=0.12, axis="y")
    for sg in (-1, 1):
        y = sg * 1.3
        g.cyl(mb, COMP_R - 0.32, 0.24, (0.0, y, COMP_Z), CREAM, 28, bev=0.0, axis="y")
        rose = []
        for k in range(16):
            rr = (1.8 if k % 4 == 0 else (1.15 if k % 2 == 0 else 0.42))
            rose.append(rr)
        g.plate(mb, star(0.0, COMP_Z, rose, 90.0), sg * 1.47, 0.2, BLUE)
        g.plate(mb, star(0.0, COMP_Z, [1.05, 0.3] * 4, 45.0), sg * 1.6, 0.2, RED)
        g.cyl(mb, 0.3, 0.4, (0.0, sg * 1.65, COMP_Z), BRASS, 10, bev=0.0, axis="y")
        # 4 marcas de latao no aro (N, L, S, O)
        for k in range(4):
            a = math.radians(90 * k)
            g.cyl(mb, 0.2, 0.5, (math.cos(a) * (COMP_R - 0.2), sg * 1.3, COMP_Z + math.sin(a) * (COMP_R - 0.2)),
                  BRASS, 6, bev=0.0, axis="y")


def _straw_hat(g, mb):
    """chapeu de palha com fita vermelha pousado no punho de cima do timao (levemente inclinado)"""
    t = math.radians(-9.0)
    z0 = ZC + 15.2

    def at(dz):
        return g.P(math.sin(t) * dz, 0.0, z0 + math.cos(t) * dz)
    rot = g.R(0.0, t, 0.0)
    mb.cyl(2.7, 0.34, at(0.1), rot, STRAW, 20, r2=1.6, bevel=0.0)                  # aba
    mb.cyl(1.32, 1.15, at(0.82), rot, STRAW, 16, r2=1.16, bevel=0.0)               # copa
    mb.cyl(1.42, 0.42, at(0.5), rot, RED, 16, bevel=0.0)                            # fita vermelha
    mb.ico(1.16, at(1.39), STRAW, 2, (1.0, 1.0, 0.42), rot)


def _needle_vfx(g):
    mb = GMB("VFX_GATE_OnePiece_Needle", None, detail="near")
    mb.coll = fm_lib.coll("12_VFX_HELPERS")
    pts = [(0.0, COMP_Z + 1.55), (0.3, COMP_Z), (0.0, COMP_Z - 1.2), (-0.3, COMP_Z)]
    g.plate(mb, pts, -1.95, 0.2, AQUA)
    ob = mb.finish()
    p = g.P(0.0, -1.95, COMP_Z)
    ob["pivot"] = (p.x, p.y, p.z)
    ax = -g.uy
    ob["axis"] = (ax.x, ax.y, ax.z)
    ob["rpm"] = 3.0
    ob["gate"] = KEY
    return ob


def _ship_lantern(g, mb, x, z_top):
    """lanterna de navio pendurada: gancho, chapeu, vidro aceso azul-agua, 4 montantes de latao, base"""
    g.rod(mb, (x, 0.0, z_top), (x, 0.0, z_top - 1.0), 0.1, IRON, 4)
    c = z_top - 2.9
    g.cone(mb, (x, 0.0, c + 1.3), (x, 0.0, c + 1.95), 0.95, 0.14, BRASS, 8)
    g.cyl(mb, 0.18, 0.3, (x, 0.0, c + 2.05), BRASS, 6, bev=0.0)
    g.cyl(mb, 0.78, 1.6, (x, 0.0, c + 0.45), AQUA, 8, bev=0.0)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        g.box(mb, x + math.cos(a) * 0.76 - 0.12, x + math.cos(a) * 0.76 + 0.12, math.sin(a) * 0.76 - 0.12,
              math.sin(a) * 0.76 + 0.12, c - 0.35, c + 1.3, BRASS, 0.0)
    g.cyl(mb, 0.92, 0.34, (x, 0.0, c - 0.48), BRASS, 8, bev=0.0)
    g.cone(mb, (x, 0.0, c - 0.65), (x, 0.0, c - 1.05), 0.5, 0.1, BRASS, 8)


AX, AY = -14.9, 5.2                # ancora (rodada 2: atras, encostada no duque d'alba esquerdo)
RPY, RPR = 6.0, 1.25               # duques d'alba (estacas de apoio atras das estacas principais)


def _anchor(g, mb):
    ax, ay = AX, AY
    g.box(mb, ax - 2.3, ax + 2.3, ay - 0.95, ay + 0.95, GK.BASE_Z, 0.3, WD, 0.0)               # berco de madeira
    g.box(mb, ax - 0.42, ax + 0.42, ay - 0.42, ay + 0.42, 0.45, 9.3, IRON, 0.12)                # haste
    g.box(mb, ax - 1.75, ax + 1.75, ay - 0.36, ay + 0.36, 8.05, 8.75, IRON, 0.1)               # cepo
    for s in (-1, 1):
        g.ico(mb, 0.42, (ax + s * 1.8, ay, 8.4), IRON, 1)
    g.ring(mb, ax, 10.05, 0.72, 0.3, 0.32, ay, IRON, n=14)
    R, zc = 1.95, 2.45
    pts = [(ax + math.cos(math.radians(a)) * R, ay, zc + math.sin(math.radians(a)) * R) for a in range(200, 341, 10)]
    g.tube(mb, pts, [0.44] * len(pts), IRON, 8)
    g.cone(mb, (ax, ay, 0.9), (ax, ay, 0.0), 0.62, 0.18, IRON, 6)
    for s in (-1, 1):
        a = math.radians(200 if s < 0 else 340)
        tip = (ax + math.cos(a) * R, zc + math.sin(a) * R)
        # pa (fluke) triangular voltada para cima e para fora
        pts2 = [(tip[0] - s * 0.1, tip[1] - 0.25), (tip[0] + s * 0.75, tip[1] + 0.45), (tip[0] + s * 0.05, tip[1] + 1.35)]
        g.plate(mb, pts2, ay, 0.4, IRON)
    # corrente da argola ate o duque d'alba esquerdo
    g.chain(mb, (ax + 0.5, ay + 0.2, 10.0), (-PX - RPR * 0.9, RPY - RPR * 0.4, 7.4), sag=0.9, link=0.62, m=IRON,
            t=0.2, w=0.42)


def _dolphins(g, mb):
    """duque d'alba atras de cada estaca principal: estaca de apoio, 2 travessas, escora ate o chapeu da estaca e
    amarras de corda (a moldura ganha profundidade: vista de lado le como um pier)"""
    for s in (-1, 1):
        x = s * PX
        g.cyl(mb, RPR, 9.0 - GK.BASE_Z, (x, RPY, (9.0 + GK.BASE_Z) / 2), WD, 12, bev=0.0)
        g.cyl(mb, RPR + 0.2, 0.5, (x, RPY, 9.25), WD, 12, r2=0.45, bev=0.0)
        for z in (0.7, 8.3):
            g.cyl(mb, RPR + 0.12, 0.36, (x, RPY, z), IRON, 12, bev=0.0)
        for z in (3.9, 4.5, 5.1):
            g.cyl(mb, RPR + 0.16, 0.34, (x, RPY, z), ROPE, 12, bev=0.0)
        for z in (3.1, 6.6):
            g.box(mb, x - 0.45, x + 0.45, PR - 0.3, RPY - RPR + 0.3, z, z + 1.0, WD, 0.0)
            g.box(mb, x - 0.6, x + 0.6, 3.35, 3.85, z - 0.12, z + 1.12, ROPE, 0.0)          # amarra no meio
        g.beam(mb, (x, RPY - 0.7, 8.4), (x, PR - 0.1, 10.25), 0.8, 0.8, WD, 0.0)            # escora


def _barrel(g, mb, x, y, z0, r=1.0, h=2.8):
    """barril (2 troncos de cone) com 3 cintas de ferro a 0,12 da madeira (sem z-fighting)"""
    g.cyl(mb, r, h / 2, (x, y, z0 + h / 4), WP, 10, r2=r * 1.12, bev=0.0)
    g.cyl(mb, r * 1.12, h / 2, (x, y, z0 + 3 * h / 4), WP, 10, r2=r, bev=0.0)
    for zz in (0.3, h / 2, h - 0.3):
        rr = r * (1.0 + 0.12 * (1.0 - abs(zz - h / 2) / (h / 2)))
        g.cyl(mb, rr + 0.12, 0.26, (x, y, z0 + zz), IRON, 10, bev=0.0)
    g.cyl(mb, r - 0.1, 0.2, (x, y, z0 + h + 0.05), WP, 10, bev=0.0)                     # tampo (0,1 acima)


def _guardian(g, mb, s):
    """guardiao do pedestal: CABECO DE AMARRACAO duplo de ferro com a corda em oito + BARRIL com rolo de corda"""
    cx, cy = s * GK.PED_C[0], GK.PED_C[1]
    z0 = GK.PED_TOP
    bx, by = cx + s * 0.35, cy + 0.85
    g.box(mb, bx - 1.75, bx + 1.75, by - 0.75, by + 0.75, z0, z0 + 0.35, IRON, 0.0)
    for dx in (-0.95, 0.95):
        g.cyl(mb, 0.58, 3.0, (bx + dx, by, z0 + 0.35 + 1.5), IRON, 10, bev=0.0)
        g.cyl(mb, 0.8, 0.34, (bx + dx, by, z0 + 3.35 + 0.17), IRON, 10, bev=0.0)
    g.beam(mb, (bx - 0.95, by, z0 + 2.5), (bx + 0.95, by, z0 + 2.5), 0.4, 0.4, IRON, 0.0)
    # corda em oito em volta dos dois postes (2 voltas em alturas diferentes)
    for zz in (1.2, 1.75):
        rr = 0.86
        pts = [(bx + 0.95 + math.cos(math.radians(a)) * rr, by + math.sin(math.radians(a)) * rr, z0 + zz)
               for a in range(-90, 91, 30)]
        pts += [(bx - 0.95 + math.cos(math.radians(a)) * rr, by + math.sin(math.radians(a)) * rr, z0 + zz + 0.15)
                for a in range(90, 271, 30)]
        pts.append(pts[0])
        g.tube(mb, pts, [0.2] * len(pts), ROPE, 6)
    _barrel(g, mb, cx - s * 0.75, cy - 0.95, z0, 0.95, 2.7)
    K.ring(mb, g.P(cx - s * 0.75, cy - 0.95, z0 + 2.7 + 0.15 + 0.2), 0.52, tuple(g.ux), tuple(g.uy), 0.36, 0.36,
           ROPE, n=12)


def _hat(g):
    def build(mb, p):
        from mathutils import Vector as V
        up = V((0.0, 0.0, 1.0))
        mb.cyl(1.45, 0.2, p + up * -0.3, (0, 0, 0), STRAW, 16, r2=0.95, bevel=0.0)
        mb.cyl(0.72, 0.65, p + up * 0.1, (0, 0, 0), STRAW, 12, r2=0.64, bevel=0.0)
        mb.cyl(0.84, 0.24, p + up * -0.05, (0, 0, 0), RED, 12, bevel=0.0)
        mb.ico(0.64, p + up * 0.42, STRAW, 1, (1.0, 1.0, 0.42))
    return build


def _collision(g):
    for s in (-1, 1):
        g.col(A, s * 8.05, s * 12.55, -2.25, 2.25, 0.0, 11.2)
        g.col(A, s * (PX - RPR - 0.2), s * (PX + RPR + 0.2), RPY - RPR - 0.2, RPY + RPR + 0.2, GK.BASE_Z, 9.5)
    g.col(A, AX - 2.3, AX + 2.3, AY - 0.95, AY + 0.95, GK.BASE_Z, 10.8)
    GK.family_collision(g, A, ped_h=3.6)


def build_gate(gx, gy, gz, yaw):
    rng = random.Random(5505)
    F = GS.gate_frame(gx, gy, gz, yaw)
    g = G(F)
    mb = GMB("GATE_%s_Frame" % KEY, rng, detail="hero", vcap=1)
    _posts(g, mb)
    _helm(g, mb)
    _compass(g, mb)
    _straw_hat(g, mb)
    for s in (-1, 1):
        a = math.radians(SPOKES[0] if s > 0 else SPOKES[-1])
        x = math.cos(a) * 15.0
        _ship_lantern(g, mb, x, ZC + math.sin(a) * 15.0 - 0.35)
    _anchor(g, mb)
    _dolphins(g, mb)
    GK.family_base(g, mb, A, accent=BLUE, glow=AQUA, roof=HELM, finial=BRASS)
    for s in (-1, 1):
        _guardian(g, mb, s)
        GK.inlay(g, mb, s, GK.star(0.0, 0.0, [0.85, 0.28] * 4, 90.0), BRASS)
    GK.tag(mb.finish(), KEY, "frame")
    _needle_vfx(g)
    GK.emblems(KEY, g, "Hat", _hat(g))
    _collision(g)
    GS.barrier(KEY, F, GLOW, shape="arch", rng=rng)
    GS.markers(KEY, F, yaw)
    GK.scale_dummy(KEY, g)
    GK.make_cams(CAMS)


def build():
    gx, gy, gz, yaw = GS.gallery_slot(KEY)
    build_gate(gx, gy, gz, yaw)
