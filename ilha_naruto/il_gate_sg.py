# il_gate_sg - portao de compra SHADOW GARDEN (area 4): "PORTAL DA LUA NEGRA". Dono: zona gates.
# Gotico fino em pedra negra-violeta polida: arco QUEBRADO (ogiva) em duas ordens (a de fora escura com capa de prata,
# a de dentro em ardosia violeta com filete aceso), jambas com trilho da barreira, capiteis de prata, dois pinaculos
# com agulhas octogonais, wimperg (empena gotica) com crochets de prata e a LUA CRESCENTE acesa no remate (o ponto
# mais alto, 31,6). Timpano e enjuntas fechados em preto fosco com uma rosacea de prata e uma joia que flutua (VFX).
# Ornamentos laterais (fora de +-12): contrafortes com arcobotante e agulha; na frente de cada um, um pedestal com um
# CRISTAL roxo ACORRENTADO (o poder selado da Shadow Garden). Barreira roxa (P_Shadow_Glow) em arco.
#
# PLANO (referencial do portao; z relativo ao tabuleiro):
#   vao 16 x 18 (arco: nascenca z 10, semicirculo r 8)      jambas x 8.0..11.6 (plinto ate 12.2), y +-2.0
#   ogiva: centros (+-4, 10); ordem B r 12.0..13.1 (y +-1.2) ; ordem A r 13.0..14.5 (y +-1.9) + capa de prata ..14.8
#   apice: intradorso 21.3 | extradorso A 23.9 | empena (wimperg) ate 26.6 | lua z 27.3..31.6
#   pinaculos x 10.4..12.0 ate 24.4, agulha ate 30.8 | contrafortes x 12.6..15.8 ate 14.6, agulha 18.9
#   largura total +-15.8 (moldura) | altura 31.6
# RODADA 2 (critica: "papelao, sem soleira/pedestais/emblemas, nao e familia do DB"):
#   - kit de familia (il_gates_kit): soleira de cantaria 22 x 10, plintos em degrau, 2 pedestais 4x4x4 com o CRISTAL
#     ACORRENTADO em cima (correntes para o pedestal e para o contraforte), 2 lanternas de pedra (camara roxa) e 4 LUAS
#     CRESCENTES flutuantes (VFX_GATE_ShadowGarden_Moon_*, bob);
#   - profundidade: CONTRAFORTE gotico atras de cada jamba (y 2..7,2, 3 recuos com glacis de ardosia) -> moldura
#     de y -2,5 a 7,2 (9,7);
#   - regras novas (chanfro pela regra do GMB, folga >= 0,1 entre materiais diferentes).
import math, random
import fm_lib
from fm_lib import S
import il_gate_std as GS
import il_gates_kit as GK
from il_gates_kit import G, GMB, arc, ogive, radial_fill, crescent
from fm_parts import frustum
import fm_portal_kit as K

KEY = "ShadowGarden"
# ------------------------------------------------------------------ materiais novos (3 dos 12 da zona)
_M = fm_lib.MATS.setdefault
_M("Stone_GateSG_Obsidian", (S(52, 44, 68), 0.32, 0.0, 0, None, 0.08))     # pedra negra-violeta polida
_M("Stone_GateSG_Slate", (S(108, 98, 136), 0.65, 0.0, 0, None, 0.08))      # ardosia violeta (ordens, plintos)
_M("Metal_GateSG_Silver", (S(196, 200, 214), 0.3, 0.55, 0, None, 0.03))   # prata fria
OBS, SLA, SIL = "Stone_GateSG_Obsidian", "Stone_GateSG_Slate", "Metal_GateSG_Silver"
DEEP = "P_Shadow_Stone"          # preto-violeta fosco (timpano, enjuntas)
IRON = "Metal_Dark"              # correntes
GLOW = "P_Shadow_Glow"           # barreira e filetes (Neon)
CRY, CORE = "Crystal_Purple", "Crystal_Purple_Core"

CAMS = GK.cams_for(KEY, {
    # a familia inteira (4 portoes da galeria) em silhueta contra o ceu
    "CAM_Gates_Family": ((GS.GALLERY_X0 + GS.GALLERY_STEP * 1.5, -265.0, GS.GALLERY_Z + 14.0),
                         (GS.GALLERY_X0 + GS.GALLERY_STEP * 1.5, 0.0, GS.GALLERY_Z + 16.0), 20),
    # a fila em 3/4 (os 4 portoes em perspectiva: a familia de frente para quem chega)
    "CAM_Gates_Row": ((GS.GALLERY_X0 - 170.0, -140.0, GS.GALLERY_Z + 26.0),
                      (GS.GALLERY_X0 + 195.0, 0.0, GS.GALLERY_Z - 2.0), 24)})

ZS = 10.0                        # nascenca = centro do semicirculo da barreira
OFF = 4.0                        # centros da ogiva em x = +-OFF
PX0, PX1, PY = 8.0, 11.6, 2.0    # jamba
TX0, TX1 = 10.4, 12.0            # pinaculo (fuste acima do capitel)
GA_Z, GA_S = 26.6, 0.8           # apice e inclinacao (dz/dx) do wimperg
BX, BY = 14.2, 0.4               # contraforte lateral
CX, CY = 14.2, -3.6              # pedestal do cristal
A = "Gate" + KEY


def _gable_top(x):
    return GA_Z - abs(x) * GA_S


def _piers(g, mb):
    for s in (-1, 1):
        # plinto em 2 degraus, fuste, anel de prata na base, capitel (prata + ardosia); tudo com o trilho da barreira
        g.jamb_box(mb, s, PX0, 12.2, -2.5, 2.5, 0.0, 1.2, SLA, 0.15)
        g.jamb_box(mb, s, PX0, 11.9, -2.25, 2.25, 1.2, 1.9, OBS, 0.12)
        g.jamb_box(mb, s, PX0, 11.75, -2.15, 2.15, 1.9, 2.25, SIL, 0.06)
        g.jamb_box(mb, s, PX0, PX1, -PY, PY, 2.25, 9.0, OBS, 0.2)
        g.jamb_box(mb, s, PX0, 11.8, -2.2, 2.2, 9.0, 9.4, SIL, 0.06)
        g.jamb_box(mb, s, PX0, 12.1, -2.4, 2.4, 9.4, 10.6, SLA, 0.15)
        # lanceta cega (moldura de ardosia) nas faces da frente e de tras da jamba
        cx = s * 9.8
        outer = [(cx - 1.0, 2.25), (cx - 1.0, 7.0), (cx, 8.5), (cx + 1.0, 7.0), (cx + 1.0, 2.25)]
        inner = [(cx - 0.6, 2.25), (cx - 0.6, 6.85), (cx, 7.85), (cx + 0.6, 6.85), (cx + 0.6, 2.25)]
        for y0, y1 in ((-PY - 0.22, -PY + 0.05), (PY - 0.05, PY + 0.22)):
            g.band(mb, outer, inner, y0, y1, SLA, 0.0)
        # pinaculo: fuste, cornija de prata, agulha octogonal, 4 agulhinhas nos cantos, remate
        xa, xb = sorted((s * TX0, s * TX1))
        g.box(mb, xa, xb, -1.9, 1.9, 10.6, 24.4, OBS, 0.18)
        xa, xb = sorted((s * 10.1, s * 12.3))
        g.box(mb, xa, xb, -2.2, 2.2, 24.4, 24.9, SIL, 0.06)
        tx = s * (TX0 + TX1) / 2
        g.cyl(mb, 1.05, 5.9, (tx, 0.0, 24.9 + 2.95), OBS, 8, r2=0.06, bev=0.0)
        for cx2 in (s * 10.3, s * 12.1):
            for cy2 in (-2.0, 2.0):
                g.cone(mb, (cx2, cy2, 24.85), (cx2, cy2, 26.5), 0.3, 0.02, SLA, 4)
        g.ico(mb, 0.32, (tx, 0.0, 30.95), SIL, 1)
        # face da frente do pinaculo: filete de prata vertical
        for yy in (-1.95, 1.95):
            g.box(mb, tx - 0.18, tx + 0.18, yy - 0.12, yy + 0.12, 11.4, 23.6, SIL, 0.0)


def _arch(g, mb, gl):
    n = 12
    # ordem A (de fora, escura) atravessa a espessura toda; ordem B (de dentro, ardosia) recuada nas duas faces
    g.band(mb, ogive(OFF, ZS, 14.5, n), ogive(OFF, ZS, 13.0, n), -1.9, 1.9, OBS, 0.16)
    g.band(mb, ogive(OFF, ZS, 14.85, n), ogive(OFF, ZS, 14.45, n), -1.7, 1.7, SIL, 0.08)       # capa de prata
    g.band(mb, ogive(OFF, ZS, 13.1, n), ogive(OFF, ZS, 12.04, n), -1.2, 1.2, SLA, 0.12)
    # filete aceso no intradorso (frente e costas)
    for y0, y1 in ((-1.42, -1.2), (1.2, 1.42)):
        g.band(gl, ogive(OFF, ZS, 12.42, n), ogive(OFF, ZS, 12.1, n), y0, y1, GLOW, 0.0)
    # timpano + enjuntas: painel fosco entre o semicirculo da barreira (r 8, atras dela) e a empena/pinaculos
    poly = [(-TX0 - 0.1, ZS), (-TX0 - 0.1, _gable_top(TX0) - 0.2), (0.0, GA_Z - 1.2), (TX0 + 0.1, _gable_top(TX0) - 0.2),
            (TX0 + 0.1, ZS)]
    outer, inner = radial_fill(0.0, ZS, 8.02, poly, 0.0, 180.0, 36)
    g.band(mb, outer, inner, 0.35, 1.05, DEEP, 0.0)
    # rosacea de prata no timpano (a joia no meio e VFX)
    g.ring(mb, 0.0, 19.7, 1.08, 0.3, 0.45, 0.12, SIL, n=20)
    for k in range(4):
        a = math.radians(45 + 90 * k)
        g.beam(mb, (math.cos(a) * 0.35, 0.12, 19.7 + math.sin(a) * 0.35),
               (math.cos(a) * 0.95, 0.12, 19.7 + math.sin(a) * 0.95), 0.3, 0.2, SIL, 0.0)


def _crown(g, mb, gl):
    # wimperg: empena gotica atravessando os pinaculos, capa de prata, crochets e remate com a lua
    xe = 11.0
    th = 1.2 / math.cos(math.atan(GA_S))          # espessura vertical da viga inclinada
    top = [(-xe, _gable_top(xe)), (0.0, GA_Z), (xe, _gable_top(xe))]
    bot = [(-xe, _gable_top(xe) - th), (0.0, GA_Z - th), (xe, _gable_top(xe) - th)]
    g.band(mb, top, bot, -1.5, 1.5, OBS, 0.14)
    g.band(mb, [(x, z + 0.32) for x, z in top], [(x, z - 0.04) for x, z in top], -1.65, 1.65, SIL, 0.06)
    for s in (-1, 1):
        for x in (2.6, 5.2, 7.8):
            z = _gable_top(x) + 0.28
            g.cone(mb, (s * x, 0.0, z), (s * (x + 0.45), 0.0, z + 0.95), 0.34, 0.03, SIL, 4)
    # remate: haste, no e a lua crescente (placa de prata de contorno + corpo aceso lavanda)
    g.cyl(mb, 0.3, 1.5, (0.0, 0.0, GA_Z + 0.5), SIL, 8, bev=0.0)
    g.ico(mb, 0.5, (0.0, 0.0, GA_Z + 0.35), SIL, 1)
    mz = 29.3
    R = 2.4
    g.plate(mb, crescent(R + 0.2, 0.86 * R - 0.2, 0.42 * R, math.radians(50), 44, 0.0, mz), 0.0, 0.34, SIL)
    g.plate(gl, crescent(R, 0.86 * R, 0.42 * R, math.radians(50), 44, 0.0, mz), 0.0, 0.62, CORE)


def _buttresses(g, mb, gl, rng):
    for s in (-1, 1):
        bx = s * BX
        # contraforte: plinto, corpo, talude, corpo alto, cornija de prata, agulha, remate
        g.box(mb, bx - 1.6, bx + 1.6, BY - 1.6, BY + 1.6, 0.0, 1.2, SLA, 0.15)
        g.box(mb, bx - 1.3, bx + 1.3, BY - 1.3, BY + 1.3, 1.2, 8.6, OBS, 0.18)
        frustum(mb, g.P(bx, BY, 8.6), 2.6, 2.6, 1.8, 1.8, 1.0, OBS, ang=g.F.a)
        g.box(mb, bx - 0.9, bx + 0.9, BY - 0.9, BY + 0.9, 9.6, 14.2, OBS, 0.15)
        g.box(mb, bx - 1.1, bx + 1.1, BY - 1.1, BY + 1.1, 14.2, 14.6, SIL, 0.05)
        g.cyl(mb, 0.85, 4.2, (bx, BY, 14.6 + 2.1), SLA, 8, r2=0.05, bev=0.0)
        g.ico(mb, 0.28, (bx, BY, 18.9), SIL, 1)
        # lanceta cega de ardosia na frente do contraforte
        outer = [(bx - 0.75, 2.4), (bx - 0.75, 6.2), (bx, 7.3), (bx + 0.75, 6.2), (bx + 0.75, 2.4)]
        inner = [(bx - 0.42, 2.4), (bx - 0.42, 6.05), (bx, 6.75), (bx + 0.42, 6.05), (bx + 0.42, 2.4)]
        g.band(mb, outer, inner, BY - 1.52, BY - 1.28, SLA, 0.0)
        # arcobotante: do contraforte ao pinaculo
        a0, a1 = (s * (BX - 0.8), 12.6), (s * (TX1 - 0.2), 16.6)
        g.beam(mb, (a0[0], BY, a0[1]), (a1[0], BY, a1[1]), 1.1, 0.8, OBS, 0.1)
        # capa de prata POR CIMA do arcobotante (deslocada na normal da viga: 0,4 + 0,15 - 0,05 de encaixe)
        dx, dz = a1[0] - a0[0], a1[1] - a0[1]
        ln = math.hypot(dx, dz)
        nx, nz = -dz / ln, dx / ln
        if nz < 0:
            nx, nz = -nx, -nz
        o = 0.5
        e = 0.3 / ln                                    # a capa acaba 0,3 antes (ponta nao coplanar)
        g.beam(mb, (a0[0] + nx * o, BY, a0[1] + nz * o), (a1[0] - dx * e + nx * o, BY, a1[1] - dz * e + nz * o),
               0.8, 0.3, SIL, 0.0)
        # argolas de prata na frente do contraforte: as correntes descem ate o cristal do pedestal
        cx, cy = s * GK.PED_C[0], GK.PED_C[1]
        for dx in (-0.75, 0.75):
            g.box(mb, bx + dx - 0.3, bx + dx + 0.3, BY - 1.7, BY - 1.2, 8.1, 9.1, SIL, 0.0)
            g.chain(mb, (bx + dx, BY - 1.75, 8.6), (cx + dx * 0.7, cy + 0.75, GK.PED_TOP + 2.6), sag=0.45,
                    link=0.72, m=SIL, t=0.22, w=0.52)


def _rear_buttress(g, mb):
    """contraforte gotico ATRAS de cada jamba (profundidade da moldura): 3 lances com recuo, glacis de ardosia em cada
    recuo, o ultimo morre no pinaculo. Escondido de frente (fica dentro da largura da jamba)."""
    for s in (-1, 1):
        xa, xb = sorted((s * 8.6, s * 11.15))              # face de fora 0,15 alem da ponta da soleira (x 11)
        ca, cb = sorted((s * 8.45, s * 11.75))             # glacis 0,15 alem da jamba (11,6) e do filete
        g.side_prism(mb, [(1.8, GK.BASE_Z), (7.2, GK.BASE_Z), (7.2, 4.6), (1.8, 4.6)], xa, xb, OBS, 0.1)
        g.side_prism(mb, [(1.8, 4.6), (7.35, 4.6), (7.35, 4.9), (6.2, 6.0), (1.8, 6.0)], ca, cb, SLA, 0.0)
        g.side_prism(mb, [(1.8, 6.0), (6.2, 6.0), (6.2, 10.4), (1.8, 10.4)], xa, xb, OBS, 0.1)
        g.side_prism(mb, [(1.8, 10.4), (6.35, 10.4), (6.35, 10.7), (5.0, 11.8), (1.8, 11.8)], ca, cb, SLA, 0.0)
        g.side_prism(mb, [(1.8, 11.8), (5.0, 11.8), (5.0, 15.4), (1.8, 15.4)], xa, xb, OBS, 0.1)
        g.side_prism(mb, [(1.8, 15.4), (5.15, 15.4), (5.15, 15.7), (1.9, 19.6), (1.8, 19.6)], ca, cb, SLA, 0.0)
        # lanceta cega de ardosia na face de fora de cada lance (le como contraforte de catedral)
        xo = s * 11.15
        for y0, y1, z0, z1 in ((3.2, 5.8, 1.2, 3.8), (3.0, 5.0, 7.0, 9.4)):
            xa2, xb2 = sorted((xo - s * 0.1, xo + s * 0.12))
            yc = (y0 + y1) / 2
            g.box(mb, xa2, xb2, y0, y1, z0, z1 - 0.9, SLA, 0.0)
            g.side_prism(mb, [(y0, z1 - 0.9), (y1, z1 - 0.9), (yc, z1)], xa2, xb2, SLA, 0.0)


def _guardian(g, mb, gl, rng, s):
    """guardiao do pedestal: soquete de obsidiana, CRISTAL roxo e correntes de prata presas nas quinas da capa"""
    cx, cy = s * GK.PED_C[0], GK.PED_C[1]
    z = GK.PED_TOP
    g.cyl(mb, 1.45, 0.3, (cx, cy, z + 0.15), SIL, 8, bev=0.0, spin=math.radians(22.5))
    g.cyl(mb, 1.2, 0.6, (cx, cy, z + 0.6), OBS, 8, r2=0.95, bev=0.0, spin=math.radians(22.5))
    _crystal_cluster(g, gl, cx, cy, z + 0.9, rng, s)
    # aro de prata em volta do cristal grande e 2 correntes da capa ate ele
    K.ring(mb, g.P(cx, cy, z + 2.9), 1.12, tuple(g.ux), tuple(g.uy), 0.34, 0.5, SIL, n=10)
    for sx in (-1, 1):
        a = (cx + sx * 1.55, cy - 1.55, z + 0.25)
        g.box(mb, a[0] - 0.3, a[0] + 0.3, a[1] - 0.3, a[1] + 0.3, z, z + 0.45, SIL, 0.0)
        g.chain(mb, (a[0], a[1], z + 0.45), (cx + sx * 0.9, cy - 0.55, z + 2.9), sag=0.25, link=0.66, m=SIL,
                t=0.2, w=0.46)


def _moon(g):
    def build(mb, p):
        K.plate(mb, crescent(1.55, 0.92, 0.58, math.radians(50), 28), p, tuple(g.ux), (0, 0, 1), 0.36, SIL)
        K.plate(mb, crescent(1.32, 1.12, 0.58, math.radians(50), 28), p, tuple(g.ux), (0, 0, 1), 0.6, CORE)
    return build


def _crystal(g, gl, base, h, r, ax):
    """cristal de 5 lados: casca roxa + ponta acesa (a ponta vira Neon no Roblox)"""
    from mathutils import Vector
    import fm_props_kit as PK
    e = PK.axis_euler(ax, 0.3)
    b = Vector(base)
    gl.cyl(r, h * 0.66, b + ax * h * 0.33, e, CRY, 5, r2=r * 0.92, bevel=0.0)
    gl.cyl(r * 0.92, h * 0.34, b + ax * h * 0.83, e, CORE, 5, r2=0.04, bevel=0.0)


def _crystal_cluster(g, gl, cx, cy, z, rng, s):
    from mathutils import Vector
    spec = [(0.0, 0.0, 5.4, 0.78, 0.06), (0.7, 0.25, 3.5, 0.56, 0.42), (-0.65, 0.4, 3.0, 0.52, 0.5),
            (0.15, -0.7, 2.6, 0.48, 0.55), (-0.4, -0.5, 1.9, 0.4, 0.72), (0.75, -0.45, 1.6, 0.36, 0.8)]
    for dx, dy, h, r, tilt in spec:
        dx *= s
        base = g.P(cx + dx, cy + dy, z - 0.2)
        d = g.D(dx, dy, 0.0)
        d = d.normalized() if d.length > 1e-6 else Vector((0, 0, 0))
        ax = (Vector((0, 0, 1)) + d * math.tan(tilt)).normalized()
        _crystal(g, gl, base, h, r, ax)


def _gem_vfx(g):
    """joia que flutua na rosacea (peca movel: gira devagar e sobe/desce)"""
    mb = GMB("VFX_GATE_ShadowGarden_Gem", None, detail="near")
    mb.coll = fm_lib.coll("12_VFX_HELPERS")
    K.octa(mb, g.P(0.0, 0.12, 19.7), 0.5, 0.62, CORE, rot=g.F.a + math.radians(45))
    ob = mb.finish()
    p = g.P(0.0, 0.12, 19.7)
    ob["pivot"] = (p.x, p.y, p.z)
    ob["axis"] = (0.0, 0.0, 1.0)
    ob["rpm"] = 6.0
    ob["bob"] = 0.18
    ob["gate"] = KEY
    return ob


def _collision(g):
    for s in (-1, 1):
        g.col(A, s * PX0, s * 12.2, -2.5, 2.5, 0.0, 24.9)
        g.col(A, s * (BX - 1.6), s * (BX + 1.6), BY - 1.6, BY + 1.6, 0.0, 14.6)
        g.col(A, s * 8.45, s * 11.3, 2.5, 7.35, GK.BASE_Z, 10.4)          # contraforte de tras (lance baixo)
    GK.family_collision(g, A, ped_h=5.6)


def build_gate(gx, gy, gz, yaw):
    rng = random.Random(4404)
    F = GS.gate_frame(gx, gy, gz, yaw)
    g = G(F)
    mb = GMB("GATE_%s_Frame" % KEY, rng, detail="hero", vcap=1)
    gl = GMB("GATE_%s_Glow" % KEY, rng, detail="near", vcap=1)
    _piers(g, mb)
    _arch(g, mb, gl)
    _crown(g, mb, gl)
    _buttresses(g, mb, gl, rng)
    _rear_buttress(g, mb)
    GK.family_base(g, mb, A, accent=DEEP, glow=CORE, roof=OBS, finial=SIL, ped=(SLA, OBS))
    for s in (-1, 1):
        _guardian(g, mb, gl, rng, s)
        GK.inlay(g, mb, s, crescent(0.8, 0.62, 0.36, math.radians(50), 20), SIL)
    GK.tag(mb.finish(), KEY, "frame")
    GK.tag(gl.finish(), KEY, "glow")
    _gem_vfx(g)
    GK.emblems(KEY, g, "Moon", _moon(g))
    _collision(g)
    GS.barrier(KEY, F, GLOW, shape="arch", rng=rng)
    GS.markers(KEY, F, yaw)
    GK.scale_dummy(KEY, g)
    GK.make_cams(CAMS)


def build():
    gx, gy, gz, yaw = GS.gallery_slot(KEY)
    build_gate(gx, gy, gz, yaw)
