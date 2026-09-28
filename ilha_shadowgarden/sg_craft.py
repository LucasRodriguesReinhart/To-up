# sg_craft - CRAFT da Ilha 3 (Shadow Garden), 5o na hierarquia: o laboratorio do alquimista, onde o jogador transforma
# os ingredientes da dungeon em pocoes. Substitui sg_blockout.craft. Tudo sai da planta: CRAFT_C (90, -60) no P2,
# CRAFT_R 13 (raio externo), porta a OESTE (CRAFT_DOOR_DEG 180) com vao 8 x 11. Os marcadores CRAFT_Station (centro,
# caldeirao), PLAYER_INTERACT_Craft (5 a oeste) e NPC_Craft (6 a leste) sao do sg_core: aqui so o lugar em volta deles.
#   EXTERIOR: pavilhao redondo (24 faces) de pedra escura com embasamento, 7 contrafortes, frisos claros, 6 janelas
#     ogivais quentes, portico saliente com arco ogival (vao aberto de verdade), empena com o emblema de prata do frasco
#     e 2 lanternas; domo navy com 8 nervuras de prata, lanternim e o FRASCO GIGANTE no topo (vidro Glass_SG_Rose com o
#     liquido SG_Violet_Glow ate acima do bojo, gargalo, rolha de prata) - a marca que se le de longe.
#   INTERIOR (pe-direito 15,6 ate a cornija, abobada navy com nervuras ate 23): piso radial, passadeira da porta ao
#     caldeirao, caldeirao de ferro com pocao violeta sobre brasas (a estacao), bancada do alquimista a leste com
#     alambique, frascos e almofariz, 8 estantes (livros, frascos e potes em cores DESSATURADAS, 3 acentos violeta),
#     atril com o livro de receitas, bau de ingredientes, lustre quente.
# Colisao propria: anel da parede (20 caixas) + portico com o vao, contrafortes, cobertura, caldeirao (ngon ~2,6),
# bancada, estantes, atril e bau. Luzes (3): caldeirao (violeta fraca), lustre (quente), lanterna da porta (quente).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, Frame, ngon_col
import fm_lib
import sg_layout as L

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (4)
NEW_MATS = {
    "Glass_SGCraftAmber": (S(150, 116, 80), 0.15, 0.0, 0.22, S(168, 118, 70), 0.0),    # ambar apagado (frascos)
    "Glass_SGCraftSage": (S(104, 128, 118), 0.15, 0.0, 0.14, S(110, 140, 126), 0.0),   # verde-salvia apagado
    "Glass_SGCraftPale": (S(92, 104, 132), 0.12, 0.0, 0.12, S(96, 116, 164), 0.0),     # vidro frio (vidracas ao luar)
    "Cloth_SGCraftBook": (S(96, 58, 56), 0.85, 0.0, 0, None, 0.06),                    # encadernacao vinho apagado
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

CX, CY = L.CRAFT_C
Z = L.P2
DOOR = L.CRAFT_DOOR_DEG
R_IN = 10.5                    # face interna (vertices do 24-gono)
R_OUT = 12.6                   # face externa
H = 15.6                       # topo da parede / cornija (pe-direito interno)
STEP = 15.0                    # 24 faces
GAP = 30.0                     # meio vao angular do portico (4 faces abertas no anel)
A0, A1 = DOOR + GAP, DOOR + 360.0 - GAP
DW = L.CRAFT_DOOR_W / 2.0      # 4
DH = L.CRAFT_DOOR_H            # 11 (fecho do arco)
SPRING, RISE = 7.0, DH - 7.0   # arranque 7, flecha 4
PORT_HW = 6.8                  # meia largura do portico
PORT_Y0, PORT_Y1 = 9.0, 13.6   # portico: face interna / face externa (distancia ao centro, no eixo da porta)
DOME_Z, DOME_R, DOME_RISE = 16.6, 12.8, 9.0
LAN_R, LAN_Z0, LAN_Z1 = 2.7, 24.6, 27.8
FLASK_R = 4.0
FLASK_ZC = LAN_Z1 + 0.6 + 3.4  # centro do bojo
IN_DOME_RISE = 7.5
WIN_A = [22.5, 67.5, 112.5, 247.5, 292.5, 337.5]
BUTT_A = [0.0, 45.0, 90.0, 135.0, 225.0, 270.0, 315.0]
SHELF_A = [67.5, 82.5, 97.5, 112.5, 247.5, 262.5, 277.5, 292.5]
RIB_A = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
WARM = (1.0, 0.68, 0.40)

IRON, SILVER, BRASS = "Metal_SG_Iron", "Metal_SG_Silver", "Metal_Brass"
CASTLE, TRIM, BLOCK, NAVY = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Block", "Roof_SG_Navy"
WOOD, GLOW, VIOLET = "Wood_SG_Dark", "Lantern_Glow", "SG_Violet_Glow"
AMBER, SAGE, PALE, ROSE = "Glass_SGCraftAmber", "Glass_SGCraftSage", "Glass_SGCraftPale", "Glass_SG_Rose"
BOOKS = ["Cloth_SGCraftBook", "Leather", "Cloth_SG_Navy"]

P2 = Z
CAMS = {
    # 360 de fora (frente = oeste, a porta; tras = leste; lados norte e sul)
    "CAM_SGCraft_W": ((54.0, -54.0, P2 + 8.0), (90.0, -60.0, P2 + 19.0), 22),
    "CAM_SGCraft_N": ((80.0, -12.0, P2 + 12.0), (90.0, -60.0, P2 + 18.0), 22),
    "CAM_SGCraft_E": ((138.0, -50.0, P2 + 11.0), (90.0, -60.0, P2 + 18.0), 22),
    "CAM_SGCraft_S": ((104.0, -110.0, P2 + 8.0), (90.0, -60.0, P2 + 18.0), 22),
    "CAM_SGCraft_Far": ((10.0, -150.0, P2 + 44.0), (90.0, -60.0, P2 + 16.0), 32),
    # altura do jogador chegando pela rua do P2 (a porta e o frasco lidos juntos)
    "CAM_SGCraft_PH_Door": ((66.0, -58.0, P2 + 5.2), (90.0, -60.0, P2 + 9.0), 22),
    # dentro: da porta para o caldeirao e a bancada; estantes norte e sul; de volta para a porta; teto e lustre
    "CAM_SGCraft_In_Cauldron": ((81.6, -61.5, P2 + 6.0), (96.0, -59.5, P2 + 3.2), 18),
    "CAM_SGCraft_In_ShelvesN": ((88.5, -66.5, P2 + 5.2), (90.5, -50.0, P2 + 5.0), 16),
    "CAM_SGCraft_In_ShelvesS": ((91.5, -53.5, P2 + 5.2), (89.5, -70.0, P2 + 5.0), 16),
    "CAM_SGCraft_In_Door": ((96.0, -61.0, P2 + 5.6), (80.0, -60.0, P2 + 6.0), 16),
    "CAM_SGCraft_In_Up": ((83.5, -60.0, P2 + 3.0), (92.0, -60.0, P2 + 17.0), 14),
}

# rota extra: da rua, pela porta, uma volta inteira em torno do caldeirao (raio 5,2) e saida - prova que a bancada, o
# atril, o bau e as estantes deixam a circulacao livre
_VOLTA = [(CX + 5.2 * math.cos(math.radians(180.0 - 30.0 * k)), CY + 5.2 * math.sin(math.radians(180.0 - 30.0 * k)))
          for k in range(13)]
EXTRA_ROUTES = {
    "CRAFT_VOLTA_CALDEIRAO": ([(CX - 20.0, CY), (CX - 13.0, CY), (CX - 8.0, CY)] + _VOLTA + [(CX - 8.0, CY), (CX - 20.0, CY)],
                              P2),
}
EXTRA_PROBES = [("CRAFT_estante_N", CX + 1.3, CY + 6.0, P2, 0.0, 1.0), ("CRAFT_bancada_L", CX + 5.0, CY, P2, 1.0, 0.0)]


# ------------------------------------------------------------------ referenciais
def fr(a_deg):
    """referencial no centro do pavilhao: local +y = radial para fora no rumo a_deg, local x = tangente, z = altura"""
    return Frame(CX, CY, Z, math.radians(a_deg) - math.pi / 2)


FD = fr(DOOR)


def pol(r, a_deg, z):
    a = math.radians(a_deg)
    return (CX + r * math.cos(a), CY + r * math.sin(a), Z + z)


def apo(r):
    """apotema do 24-gono de raio (vertice) r: onde fica a face plana no meio de cada lado"""
    return r * math.cos(math.radians(STEP / 2.0))


# ------------------------------------------------------------------ primitivas
def ring_band(mb, r0, r1, z0, z1, m, a0=0.0, a1=360.0, step=STEP):
    """anel (setor) solido entre os raios r0 e r1 (vertices do poligono), de z0 a z1 (acima do piso)"""
    bm = mb.bm
    full = abs(a1 - a0 - 360.0) < 1e-6
    n = int(round((a1 - a0) / step))
    angs = [math.radians(a0 + (a1 - a0) * k / n) for k in range(n + (0 if full else 1))]

    def v(r, a, z):
        return bm.verts.new((CX + r * math.cos(a), CY + r * math.sin(a), Z + z))
    ib = [v(r0, a, z0) for a in angs]
    ob = [v(r1, a, z0) for a in angs]
    it = [v(r0, a, z1) for a in angs]
    ot = [v(r1, a, z1) for a in angs]
    K = len(angs)
    for i in (range(K) if full else range(K - 1)):
        j = (i + 1) % K
        bm.faces.new((ob[i], ob[j], ot[j], ot[i]))
        bm.faces.new((ib[j], ib[i], it[i], it[j]))
        bm.faces.new((it[i], ot[i], ot[j], it[j]))
        bm.faces.new((ib[i], ib[j], ob[j], ob[i]))
    if not full:
        bm.faces.new((ib[0], ob[0], ot[0], it[0]))
        bm.faces.new((ib[-1], it[-1], ot[-1], ob[-1]))
    mb._post(ib + ob + it + ot, m, None, 0, 1)


def pslab(mb, F, pts, y0, y1, m):
    """poligono (u, v) no plano tangente do referencial F, extrudado no radial de y0 a y1"""
    bm = mb.bm
    A = [bm.verts.new(F.p(u, y1, v)) for u, v in pts]
    B = [bm.verts.new(F.p(u, y0, v)) for u, v in pts]
    n = len(pts)
    bm.faces.new(A)
    bm.faces.new(list(reversed(B)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((A[j], A[i], B[i], B[j]))
    mb._post(A + B, m, None, 0, 1)


def pside(mb, F, pts, u0, u1, m):
    """poligono (y, v) no plano radial do referencial F, extrudado na tangente de u0 a u1"""
    bm = mb.bm
    A = [bm.verts.new(F.p(u1, y, v)) for y, v in pts]
    B = [bm.verts.new(F.p(u0, y, v)) for y, v in pts]
    n = len(pts)
    bm.faces.new(A)
    bm.faces.new(list(reversed(B)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((A[j], A[i], B[i], B[j]))
    mb._post(A + B, m, None, 0, 1)


def fbox(mb, F, u0, u1, y0, y1, v0, v1, m, bevel=0.0):
    c = F.p((u0 + u1) / 2.0, (y0 + y1) / 2.0, (v0 + v1) / 2.0)
    mb.box((abs(u1 - u0), abs(y1 - y0), abs(v1 - v0)), c, F.r(), m, bevel)


def fcol(area, F, u0, u1, y0, y1, v0, v1):
    c = F.p((u0 + u1) / 2.0, (y0 + y1) / 2.0, (v0 + v1) / 2.0)
    col_box(area, (abs(u1 - u0), abs(y1 - y0), abs(v1 - v0)), c, F.r())


def lathe(mb, x, y, z, prof, m, n=12, rot=0.0, cap0=True, cap1=True):
    """solido de revolucao: prof = [(raio, altura)] de baixo para cima; raio 0 = polo"""
    bm = mb.bm
    rows = []
    for r, h in prof:
        if r < 1e-4:
            rows.append([bm.verts.new((x, y, z + h))])
        else:
            rows.append([bm.verts.new((x + r * math.cos(rot + 2 * math.pi * i / n),
                                       y + r * math.sin(rot + 2 * math.pi * i / n), z + h)) for i in range(n)])
    for A, B in zip(rows, rows[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(n):
            j = (i + 1) % n
            if len(A) == 1:
                bm.faces.new((A[0], B[i], B[j]))
            elif len(B) == 1:
                bm.faces.new((A[i], A[j], B[0]))
            else:
                bm.faces.new((A[i], A[j], B[j], B[i]))
    if cap0 and len(rows[0]) > 1:
        bm.faces.new(list(reversed(rows[0])))
    if cap1 and len(rows[-1]) > 1:
        bm.faces.new(rows[-1])
    mb._post([v for r in rows for v in r], m, None, 0, 1)


def sph_uv(mb, faces, m, zb, R):
    """UV esferica (azimute x elevacao, em studs/TILE) para cupulas: a projecao planar do MB (uma primitiva so) esticava
    a textura em faixas"""
    key = fm_lib.tex_key(m)
    if key is None:
        return
    inv = 1.0 / fm_lib.tex_tile(key)
    uvl = mb.uvl
    for f in faces:
        c = f.calc_center_median()
        a0 = math.atan2(c.y - CY, c.x - CX)
        for lp in f.loops:
            co = lp.vert.co
            rr = math.hypot(co.x - CX, co.y - CY)
            az = a0 if rr < 1e-3 else math.atan2(co.y - CY, co.x - CX)
            while az - a0 > math.pi:
                az -= 2 * math.pi
            while az - a0 < -math.pi:
                az += 2 * math.pi
            el = math.atan2(co.z - zb, max(rr, 1e-3))
            lp[uvl].uv = (az * R * inv, el * R * inv)


# ------------------------------------------------------------------ arco ogival (mesmo desenho do Mining Hall)
def _ogive_center(hw, rise):
    xc = (hw * hw - rise * rise) / (2.0 * hw)
    c = min(xc, -0.25 * hw)
    zc = (rise * rise - hw * hw + 2.0 * hw * c) / (2.0 * rise)
    return c, zc, math.hypot(hw - c, zc)


def ogive_right(hw, rise, n):
    c, zc, R = _ogive_center(hw, rise)
    t0 = math.atan2(-zc, hw - c)
    ta = math.atan2(rise - zc, -c)
    pts = [(c + R * math.cos(t0 + (ta - t0) * k / n), zc + R * math.sin(t0 + (ta - t0) * k / n)) for k in range(n + 1)]
    pts[0] = (hw, 0.0)
    pts[-1] = (0.0, rise)
    return pts


def ogive(cs, hw, rise, spring, n=6):
    r = ogive_right(hw, rise, n)
    return [(cs - u, spring + v) for u, v in r] + [(cs + u, spring + v) for u, v in reversed(r)][1:]


def ogive_z(hw, rise, u):
    c, zc, R = _ogive_center(hw, rise)
    return max(0.0, zc + math.sqrt(max(0.0, R * R - (abs(u) - c) ** 2)))


def band(mb, F, inner, outer, y0, y1, m):
    """faixa solida no plano tangente entre duas polilinhas (u, v) de mesmo tamanho"""
    bm = mb.bm
    n = len(inner)
    iF = [bm.verts.new(F.p(u, y1, v)) for u, v in inner]
    iB = [bm.verts.new(F.p(u, y0, v)) for u, v in inner]
    oF = [bm.verts.new(F.p(u, y1, v)) for u, v in outer]
    oB = [bm.verts.new(F.p(u, y0, v)) for u, v in outer]
    for i in range(n - 1):
        j = i + 1
        bm.faces.new((oF[i], oF[j], iF[j], iF[i]))
        bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
        bm.faces.new((iF[i], iF[j], iB[j], iB[i]))
        bm.faces.new((oB[i], oB[j], oF[j], oF[i]))
    for k in (0, n - 1):
        bm.faces.new((iF[k], oF[k], oB[k], iB[k]))
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def arch_band(mb, F, hw, rise, spring, foot, t, y0, y1, m, n=6):
    inner = [(-hw, foot)] + ogive(0.0, hw, rise, spring, n) + [(hw, foot)]
    outer = [(-hw - t, foot)] + ogive(0.0, hw + t, rise + t, spring, n) + [(hw + t, foot)]
    band(mb, F, inner, outer, y0, y1, m)


def arch_panel(mb, F, hw, rise, spring, foot, y0, y1, m, n=6):
    pslab(mb, F, [(-hw, foot)] + ogive(0.0, hw, rise, spring, n) + [(hw, foot)], y0, y1, m)


def spandrels(mb, F, hw, rise, spring, top, y0, y1, m, n=6):
    """parede cheia acima do arco (de |u| <= hw ate top), em faixas verticais convexas: o intradorso segue a ogiva"""
    r = ogive_right(hw, rise, n)
    for s in (-1, 1):
        for (ua, va), (ub, vb) in zip(r, r[1:]):
            pslab(mb, F, [(s * ua, spring + va), (s * ub, spring + vb), (s * ub, top), (s * ua, top)], y0, y1, m)


# ------------------------------------------------------------------ casca: embasamento, parede, frisos, contrafortes
def shell():
    mb = MB("SG_Craft_Shell", "16_CRAFT", random.Random(8101), detail="near")
    ring_band(mb, 12.2, 13.25, -0.4, 0.6, BLOCK, A0, A1)                 # embasamento
    ring_band(mb, 12.4, 13.0, 0.6, 0.85, TRIM, A0, A1)                   # remate do embasamento
    ring_band(mb, R_IN, R_OUT, -0.3, H, CASTLE, A0, A1)                  # parede (24-gono sem as 4 faces da porta)
    ring_band(mb, 12.45, 12.95, 8.2, 8.7, TRIM, A0, A1)                  # friso sob as janelas
    ring_band(mb, 12.45, 13.35, 15.0, 15.6, TRIM, A0, A1)                # cornija
    ring_band(mb, 12.0, 13.1, 15.6, 16.6, TRIM, 0.0, 360.0)              # anel de apoio do domo (volta inteira)
    # contrafortes (ritmo gotico; alinhados as nervuras do domo)
    for a in BUTT_A:
        F = fr(a)
        pside(mb, F, [(12.3, 0.0), (14.5, 0.0), (14.5, 6.6), (13.7, 8.6), (12.3, 8.6)], -0.85, 0.85, CASTLE)
        pside(mb, F, [(12.3, 8.6), (13.7, 8.6), (13.7, 13.2), (12.3, 15.0)], -0.7, 0.7, CASTLE)
        fbox(mb, F, -1.0, 1.0, 12.3, 14.75, 0.0, 0.6, BLOCK, 0.08)      # pe do contraforte (acompanha o embasamento)
        fbox(mb, F, -0.95, 0.95, 13.6, 14.62, 6.2, 6.5, TRIM, 0.05)      # pingadeira
    # janelas ogivais quentes (por fora): vidraca Window_Warm, moldura clara, mainel, peitoril
    for a in WIN_A:
        F = fr(a)
        y = apo(R_OUT)
        arch_panel(mb, F, 1.0, 1.6, 12.2, 8.8, y - 0.05, y + 0.06, "Window_Warm")
        arch_band(mb, F, 1.0, 1.6, 12.2, 8.8, 0.34, y - 0.05, y + 0.32, TRIM)
        fbox(mb, F, -0.1, 0.1, y, y + 0.2, 8.8, 12.6, TRIM)
        fbox(mb, F, -1.55, 1.55, y - 0.05, y + 0.55, 8.55, 8.85, TRIM, 0.05)
    portal(mb)
    mb.finish()
    # colisao: anel (20 caixas), contrafortes
    rm = (R_IN + R_OUT) / 2.0
    chord = 2.0 * R_OUT * math.sin(math.radians(STEP / 2.0)) + 0.1
    n = int(round((A1 - A0) / STEP))
    for k in range(n):
        am = math.radians(A0 + STEP * (k + 0.5))
        col_box("SG_CraftWall", (R_OUT - R_IN, chord, H + 0.5), (CX + rm * math.cos(am), CY + rm * math.sin(am), Z + (H - 0.5) / 2.0),
                (0, 0, am))
    for a in BUTT_A:
        fcol("SG_CraftButtress", fr(a), -0.85, 0.85, R_OUT - 0.2, 14.5, -0.5, 9.0)


def portal(mb):
    """portico saliente da porta (oeste): vao ogival 8 x 11 aberto de ponta a ponta, moldura clara, empena com o emblema
    de prata do frasco, pilastras com pinaculos"""
    F = FD
    y0, y1 = PORT_Y0, PORT_Y1
    for s in (-1, 1):
        fbox(mb, F, s * DW, s * PORT_HW, y0, y1, -0.3, H, CASTLE)                      # ombreiras (macico)
        fbox(mb, F, s * (DW + 0.05), s * (PORT_HW + 0.45), y0 - 0.2, y1 + 0.5, -0.4, 0.9, BLOCK, 0.08)   # embasamento
        fbox(mb, F, s * 6.15, s * 7.2, y1, y1 + 0.5, 0.9, H, TRIM, 0.06)               # pilastra de canto
        fbox(mb, F, s * 6.05, s * 7.3, y1 - 0.6, y1 + 0.6, H, H + 1.4, TRIM, 0.06)     # base do pinaculo
        c = F.p(s * 6.68, y1 - 0.05, H + 1.4)
        SL.spire(mb, (c[0], c[1]), 0.72, c[2], 2.8, NAVY, n=4)
    spandrels(mb, F, DW, RISE, SPRING, H, y0, y1, CASTLE)
    # moldura do vao (frente e dentro) + pingadeira ogival acima
    arch_band(mb, F, DW, RISE, SPRING, 0.9, 0.8, y1, y1 + 0.5, TRIM)
    arch_band(mb, F, DW + 0.8, RISE + 0.8, SPRING, 6.3, 0.42, y1, y1 + 0.3, TRIM)
    arch_band(mb, F, DW, RISE, SPRING, 0.8, 0.7, y0 - 0.4, y0, TRIM)
    # cornija do portico e empena
    fbox(mb, F, -PORT_HW - 0.4, PORT_HW + 0.4, y0 + 0.4, y1 + 0.6, H - 0.6, H, TRIM, 0.05)
    GH = 6.6                                                      # empena gotica (ingreme)
    pslab(mb, F, [(-5.6, H), (5.6, H), (0.0, H + GH)], y1 - 1.4, y1, CASTLE)
    for s in (-1, 1):
        a = F.p(s * 6.0, y1 - 0.55, H - 0.1)
        b = F.p(0.0, y1 - 0.55, H + GH + 0.45)
        mb.beam(a, b, 1.3, 0.5, TRIM, 0.05)
    c = F.p(0.0, y1 - 0.55, H + GH + 0.35)
    SL.spire(mb, (c[0], c[1]), 0.5, c[2], 1.8, SILVER, n=4)
    # emblema de prata: o frasco (bojo + gargalo + boca) na empena - o que o craft faz, lido da rua
    yb0, yb1 = y1, y1 + 0.18
    ce = H + 1.8
    pslab(mb, F, [(0.9 * math.cos(2 * math.pi * k / 12 - math.pi / 2), ce + 0.9 * math.sin(2 * math.pi * k / 12 - math.pi / 2))
                  for k in range(12)], yb0, yb1, SILVER)
    pslab(mb, F, [(-0.28, ce + 0.6), (0.28, ce + 0.6), (0.28, ce + 1.75), (-0.28, ce + 1.75)], yb0, yb1, SILVER)
    pslab(mb, F, [(-0.5, ce + 1.75), (0.5, ce + 1.75), (0.5, ce + 2.05), (-0.5, ce + 2.05)], yb0, yb1, SILVER)
    # soleira (topo 0,05 acima do piso, como o calcamento das ruas)
    fbox(mb, F, -DW, DW, y0 - 0.2, y1 + 0.5, -0.3, 0.05, TRIM)
    # colisao do portico: ombreiras + verga em degraus que acompanha a ogiva (o vao fica 8 x 7 reto + arco ate 11)
    for s in (-1, 1):
        fcol("SG_CraftPortal", F, s * DW, s * (PORT_HW + 0.45), y0, y1 + 0.5, -0.5, H)
        fcol("SG_CraftPortal", F, s * 2.0, s * 3.2, y0, y1 + 0.5, SPRING + ogive_z(DW, RISE, 2.0), DH)
        fcol("SG_CraftPortal", F, s * 3.2, s * DW, y0, y1 + 0.5, SPRING + ogive_z(DW, RISE, 3.2), DH)
    fcol("SG_CraftPortal", F, -DW, DW, y0, y1 + 0.5, DH, H)


# ------------------------------------------------------------------ domo, nervuras de prata, lanternim
def dome():
    mb = MB("SG_Craft_Dome", "16_CRAFT", random.Random(8102), detail="near")
    # casca fechada (sem disco de fundo: a abobada de dentro fica visivel de baixo)
    dome_shell(mb, DOME_R - 0.4, DOME_RISE - 0.4, DOME_R, DOME_RISE, DOME_Z, NAVY, n=24, rings=8)
    # nervuras de prata sobre os contrafortes / o portico
    for a in RIB_A:
        ar = math.radians(a)
        pts = []
        for k in range(15):
            phi = (math.pi / 2) * 0.86 * k / 14.0
            rr = (DOME_R + 0.08) * math.cos(phi)
            if rr < LAN_R + 0.2:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + DOME_Z + (DOME_RISE + 0.08) * math.sin(phi)))
        up = (-math.sin(ar), math.cos(ar), 0.0)
        mb.sweep(pts, [(-0.22, -0.3), (0.3, -0.3), (0.3, 0.3), (-0.22, 0.3)], SILVER, up=up)
    # lanternim: tambor octogonal com fendas quentes + anel de prata (assento do frasco)
    mb.cyl(LAN_R, LAN_Z1 - LAN_Z0, (CX, CY, Z + (LAN_Z0 + LAN_Z1) / 2.0), (0, 0, math.pi / 8), CASTLE, n=8, bevel=0.0)
    for k in range(8):
        F = fr(45.0 * k)
        y = LAN_R * math.cos(math.pi / 8)
        arch_panel(mb, F, 0.42, 0.55, 26.6, 25.5, y - 0.05, y + 0.06, "Window_Warm", n=3)
        fbox(mb, fr(45.0 * k + 22.5), -0.28, 0.28, LAN_R - 0.3, LAN_R + 0.25, 25.0, LAN_Z1, TRIM)
    mb.cyl(LAN_R + 0.45, 0.6, (CX, CY, Z + LAN_Z1 + 0.3), (0, 0, math.pi / 8), SILVER, n=8, bevel=0.0)
    mb.cyl(LAN_R + 0.1, 0.5, (CX, CY, Z + LAN_Z0 + 0.25), (0, 0, math.pi / 8), TRIM, n=8, bevel=0.0)
    mb.finish()
    # cobertura (colisao): octogono no topo da parede
    ngon_col("SG_CraftRoof", CX, CY, 8, R_OUT + 0.8, Z + H, Z + DOME_Z + 1.0)


def flask():
    """o FRASCO GIGANTE: bojo de vidro com o liquido violeta ate acima do equador, gargalo, boca e rolha de prata,
    preso ao lanternim por 4 garras de prata"""
    mb = MB("SG_Craft_Flask", "16_CRAFT", random.Random(8103), detail="near")
    zc = FLASK_ZC
    R = FLASK_R
    fill = -0.3                                    # nivel do liquido (logo abaixo do equador: mais vidro, menos brilho)
    th_f = math.acos(-fill / R)                    # angulo (a partir do polo de baixo) do nivel
    rn = 1.3
    th_n = math.pi - math.asin(rn / R)
    liq = [(0.0, zc - R)]
    for k in range(1, 9):
        t = th_f * k / 8.0
        liq.append((R * math.sin(t), zc - R * math.cos(t)))
    lathe(mb, CX, CY, Z, liq, VIOLET, n=18, cap1=True)
    gl = []
    for k in range(0, 6):
        t = th_f + (th_n - th_f) * k / 5.0
        gl.append((R * math.sin(t) + 0.02, zc - R * math.cos(t)))
    gl[0] = (gl[0][0], gl[0][1] + 0.06)
    gtop = zc - R * math.cos(th_n)
    gl += [(rn, gtop + 0.9), (rn, gtop + 3.2), (rn + 0.35, gtop + 3.5), (rn + 0.35, gtop + 3.9), (rn - 0.1, gtop + 3.9)]
    lathe(mb, CX, CY, Z, gl, ROSE, n=18)
    # rolha de prata + anel do gargalo
    lathe(mb, CX, CY, Z, [(0.0, gtop + 3.6), (rn - 0.12, gtop + 3.6), (rn + 0.05, gtop + 4.6), (rn + 0.35, gtop + 4.8),
                          (rn + 0.2, gtop + 5.2), (0.45, gtop + 5.45), (0.45, gtop + 5.9), (0.0, gtop + 6.1)], SILVER, n=12)
    lathe(mb, CX, CY, Z, [(rn + 0.02, gtop + 1.2), (rn + 0.22, gtop + 1.2), (rn + 0.22, gtop + 1.6), (rn + 0.02, gtop + 1.6)],
          SILVER, n=12)
    # garras (do anel do lanternim ao bojo)
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        p0 = (CX + (LAN_R + 0.3) * ca, CY + (LAN_R + 0.3) * sa, Z + LAN_Z1 + 0.5)
        zz = zc - 1.2
        rr = math.sqrt(R * R - 1.2 * 1.2) + 0.12
        p1 = (CX + rr * ca, CY + rr * sa, Z + zz)
        mb.beam(p0, p1, 0.4, 0.35, SILVER, 0.0)
        mb.ico(0.34, p1, SILVER, 1)
    mb.finish()


# ------------------------------------------------------------------ interior: piso, frisos, abobada, nervuras
def dome_shell(mb, r_lo, rise_lo, r_hi, rise_hi, z0, m, n=24, rings=6):
    """abobada fechada (intradorso + extradorso + anel da base) - a de dentro e vista de baixo"""
    bm = mb.bm

    def surf(r, rise):
        rows = []
        for k in range(rings):
            phi = (math.pi / 2) * k / rings
            rr, zz = r * math.cos(phi), Z + z0 + rise * math.sin(phi)
            rows.append([bm.verts.new((CX + rr * math.cos(2 * math.pi * i / n), CY + rr * math.sin(2 * math.pi * i / n), zz))
                         for i in range(n)])
        top = bm.verts.new((CX, CY, Z + z0 + rise))
        return rows, top
    lo, tlo = surf(r_lo, rise_lo)
    hi, thi = surf(r_hi, rise_hi)
    for rows, top in ((lo, tlo), (hi, thi)):
        for r0, r1 in zip(rows, rows[1:]):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        for i in range(n):
            bm.faces.new((rows[-1][i], rows[-1][(i + 1) % n], top))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((lo[0][j], lo[0][i], hi[0][i], hi[0][j]))
    faces = mb._post([v for r in lo + hi for v in r] + [tlo, thi], m, None, 0, 1)
    sph_uv(mb, faces, m, Z + z0, r_lo)


def interior():
    mb = MB("SG_Craft_Interior", "16_CRAFT", random.Random(8104), detail="near")
    FL = "Stone_SG_Floor"
    # piso radial (topo 0,05 acima do piso, como o calcamento; a colisao e a do P2)
    for r0, r1, m in ((2.9, 3.5, TRIM), (3.5, 6.4, FL), (6.4, 6.8, TRIM), (6.8, R_IN + 0.1, FL)):
        ring_band(mb, r0, r1, -0.3, 0.05, m, 0.0, 360.0, 7.5)
    # frisos internos: rodape, friso das estantes/janelas, cornija
    ring_band(mb, R_IN - 0.3, R_IN + 0.05, 0.0, 0.8, TRIM, A0, A1)
    ring_band(mb, R_IN - 0.4, R_IN + 0.05, 8.5, 8.9, TRIM, A0, A1)
    ring_band(mb, R_IN - 0.6, R_IN + 0.05, 15.0, 15.6, TRIM, 0.0, 360.0)
    # abobada navy + nervuras claras apoiadas em misulas + chave central
    dome_shell(mb, R_IN, IN_DOME_RISE, R_IN + 0.4, IN_DOME_RISE + 0.4, H, "Stone_SG_Floor")
    for a in RIB_A:
        ar = math.radians(a)
        pts = []
        for k in range(13):
            phi = (math.pi / 2) * 0.9 * k / 12.0
            rr = (R_IN - 0.06) * math.cos(phi)
            if rr < 1.0:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + H + (IN_DOME_RISE - 0.06) * math.sin(phi)))
        mb.sweep(pts, [(-0.3, -0.28), (0.3, -0.28), (0.3, 0.28), (-0.3, 0.28)], TRIM, up=(-math.sin(ar), math.cos(ar), 0.0))
        F = fr(a)
        if a != DOOR:
            fbox(mb, F, -0.45, 0.45, R_IN - 0.75, R_IN + 0.02, 13.6, 15.0, TRIM, 0.05)
    mb.cyl(1.15, 0.7, (CX, CY, Z + H + IN_DOME_RISE - 0.35), (0, 0, 0), TRIM, n=12, bevel=0.0)
    mb.finish()


# ------------------------------------------------------------------ o caldeirao (a estacao)
def cauldron():
    mb = MB("SG_Craft_Cauldron", "16_CRAFT", random.Random(8105), detail="hero")
    x, y = CX, CY
    # base de pedra (lareira) e braseiro
    lathe(mb, x, y, Z, [(0.0, -0.1), (2.9, -0.1), (2.9, 0.3), (2.7, 0.45), (0.0, 0.45)], TRIM, n=16)
    lathe(mb, x, y, Z, [(0.0, 0.45), (1.45, 0.45), (1.45, 0.7), (1.2, 0.72), (0.0, 0.72)], IRON, n=12)
    mb.cyl(1.1, 0.12, (x, y, Z + 0.76), (0, 0, 0), GLOW, n=10, bevel=0.0)
    # 3 pes
    for k in range(3):
        a = math.radians(90.0 + 120.0 * k)
        mb.beam((x + 1.95 * math.cos(a), y + 1.95 * math.sin(a), Z + 0.45),
                (x + 1.45 * math.cos(a), y + 1.45 * math.sin(a), Z + 1.35), 0.42, 0.42, IRON, 0.0)
    # panela (bojo largo, pescoco, aba)
    prof = [(0.0, 0.95), (1.05, 0.95), (1.75, 1.18), (2.28, 1.7), (2.48, 2.35), (2.4, 2.95), (2.12, 3.28), (2.02, 3.38),
            (2.34, 3.46), (2.4, 3.66), (2.05, 3.66), (1.96, 3.32), (0.0, 3.32)]
    lathe(mb, x, y, Z, prof, IRON, n=20)
    # alcas (argolas) norte e sul
    for s in (-1, 1):
        ring = [(x + 0.42 * math.cos(2 * math.pi * k / 10), y + s * 2.52, Z + 2.55 + 0.42 * math.sin(2 * math.pi * k / 10))
                for k in range(11)]
        mb.sweep(ring, [(0.1 * math.cos(2 * math.pi * i / 6), 0.1 * math.sin(2 * math.pi * i / 6)) for i in range(6)],
                 IRON, up=(0.0, 1.0, 0.0))
    # pocao violeta + 2 bolhas + concha de mexer (do lado do alquimista)
    mb.cyl(2.0, 0.14, (x, y, Z + 3.38), (0, 0, 0), VIOLET, n=20, bevel=0.0)
    mb.ico(0.36, (x - 0.6, y + 0.5, Z + 3.44), VIOLET, 1, scale=(1, 1, 0.7))
    mb.ico(0.24, (x + 0.2, y - 0.8, Z + 3.44), VIOLET, 1, scale=(1, 1, 0.7))
    mb.rod((x + 0.9, y + 0.8, Z + 3.0), (x + 1.9, y + 1.9, Z + 5.0), 0.12, WOOD, 6)
    mb.finish()
    ngon_col("SG_CraftCauldron", x, y, 12, 2.7, Z - 0.1, Z + 3.7)


# ------------------------------------------------------------------ moveis e objetos de laboratorio
def bottle(mb, F, u, y, v, h, r, m, kind="tall", cork=True):
    """frasco pequeno em pe no referencial F (posicao local u, y, v = base)"""
    p = F.p(u, y, v)
    if kind == "round":
        prof = [(0.0, 0.0), (r * 0.6, 0.0), (r, h * 0.28), (r * 0.85, h * 0.55), (r * 0.3, h * 0.66), (r * 0.3, h * 0.94),
                (r * 0.42, h), (0.0, h)]
    elif kind == "flat":
        prof = [(0.0, 0.0), (r, 0.0), (r, h * 0.62), (r * 0.55, h * 0.74), (r * 0.4, h * 0.88), (r * 0.5, h), (0.0, h)]
    else:
        prof = [(0.0, 0.0), (r, 0.0), (r, h * 0.6), (r * 0.42, h * 0.74), (r * 0.36, h * 0.93), (r * 0.46, h), (0.0, h)]
    lathe(mb, p[0], p[1], p[2], prof, m, n=7)
    if cork:
        mb.cyl(r * 0.36 + 0.02, 0.24, (p[0], p[1], p[2] + h + 0.1), (0, 0, 0), WOOD, n=6, bevel=0.0)


def shelf_row(mb, F, kind, v0, rng, col=None):
    """uma prateleira (de u -1.1 a 1.1, fundo em y 9,5..10,2) cheia de uma coisa so: livros, frascos, potes ou rolos"""
    if kind == "books":
        u = -1.12
        i = rng.randint(0, 2)
        while u < 1.0:
            w = rng.uniform(0.22, 0.32)
            h = rng.uniform(1.0, 1.42)
            if u + w > 1.12:
                break
            m = BOOKS[i % 3]
            i += 1 + (rng.random() < 0.3)
            if rng.random() < 0.12 and u < 0.6:
                t = 0.28
                fbox_rot(mb, F, u + w / 2 + h * math.sin(t) / 2, 9.85, v0 + h * math.cos(t) / 2, w, 0.78, h, t, m)
                u += w + h * math.sin(t) + 0.05
                continue
            fbox(mb, F, u, u + w, 9.45, 10.23, v0, v0 + h, m)
            u += w + 0.02
    elif kind == "bottles":
        mats = col if isinstance(col, list) else [col]
        us = [-0.85, -0.3, 0.25, 0.8]
        kinds = ["tall", "round", "tall", "flat"]
        rng.shuffle(kinds)
        for k, u in enumerate(us):
            if rng.random() < 0.15:
                continue
            kd = kinds[k]
            h = rng.uniform(0.9, 1.3) if kd != "round" else rng.uniform(0.8, 1.0)
            r = rng.uniform(0.22, 0.3) if kd != "round" else rng.uniform(0.3, 0.36)
            bottle(mb, F, u + rng.uniform(-0.06, 0.06), 9.85 + rng.uniform(-0.1, 0.1), v0, h, r, mats[k % len(mats)], kd)
    elif kind == "jars":
        for u in (-0.72, 0.0, 0.72):
            p = F.p(u, 9.85, v0)
            h = rng.uniform(0.75, 0.95)
            lathe(mb, p[0], p[1], p[2], [(0.0, 0.0), (0.34, 0.0), (0.36, h * 0.8), (0.28, h), (0.0, h)], col, n=8)
            mb.cyl(0.32, 0.14, (p[0], p[1], p[2] + h + 0.05), (0, 0, 0), IRON, n=8, bevel=0.0)
    elif kind == "scrolls":
        for k, (u, dv) in enumerate(((-0.6, 0.22), (-0.15, 0.22), (0.3, 0.22), (-0.38, 0.62), (0.08, 0.62))):
            a = F.p(u, 9.45, v0 + dv)
            b = F.p(u + 0.05, 10.2, v0 + dv)
            mb.rod(a, b, 0.21, "Cloth_Canvas", 7)
        fbox(mb, F, 0.62, 0.92, 9.45, 10.23, v0, v0 + 1.1, BOOKS[0])


def fbox_rot(mb, F, u, y, v, sx, sy, sz, tilt, m):
    """caixa inclinada (em torno do eixo radial local) - livro encostado"""
    mb.box((sx, sy, sz), F.p(u, y, v), F.r(0.0, -tilt, 0.0), m, 0.0)


SHELF_ROWS = {
    67.5: ["books", ("jars", SAGE), ("bottles", AMBER), ("bottles", PALE)],
    82.5: [("jars", PALE), "books", ("bottles", SAGE), "books"],
    97.5: ["scrolls", ("bottles", AMBER), "books", ("bottles", [PALE, ROSE, PALE, SAGE])],
    112.5: ["books", ("bottles", PALE), ("jars", AMBER), "scrolls"],
    247.5: [("jars", AMBER), ("bottles", SAGE), "books", ("bottles", AMBER)],
    262.5: ["books", "scrolls", ("bottles", [PALE, AMBER, ROSE, PALE]), "books"],
    277.5: [("bottles", SAGE), "books", ("jars", PALE), ("bottles", AMBER)],
    292.5: ["scrolls", "books", ("bottles", SAGE), ("jars", SAGE)],
}
SHELF_V = [0.5, 2.36, 4.22, 6.08]
SHELF_TOP = 8.2


def shelves(mb, rng):
    hw = R_IN * math.sin(math.radians(STEP / 2.0)) - 0.02        # meia largura da face plana
    yb = apo(R_IN)
    for a in SHELF_A:
        F = fr(a)
        fbox(mb, F, -hw, hw, yb - 0.2, yb + 0.02, 0.0, SHELF_TOP, WOOD)                 # fundo
        for s in (-1, 1):
            fbox(mb, F, s * (hw - 0.18), s * hw, 9.28, yb, 0.0, SHELF_TOP, WOOD)       # laterais
        fbox(mb, F, -hw, hw, 9.28, yb, 0.0, 0.5, WOOD)                                  # rodape
        for v in SHELF_V[1:] + [7.94]:
            fbox(mb, F, -hw + 0.18, hw - 0.18, 9.3, yb, v - 0.14, v, WOOD)
        fbox(mb, F, -hw - 0.04, hw + 0.04, 9.1, yb, SHELF_TOP, SHELF_TOP + 0.34, WOOD, 0.05)   # coroamento
        for kind, v0 in zip(SHELF_ROWS[a], SHELF_V):
            if isinstance(kind, tuple):
                shelf_row(mb, F, kind[0], v0, rng, kind[1])
            else:
                shelf_row(mb, F, kind, v0, rng)
        fcol("SG_CraftShelf", F, -hw, hw, 9.25, yb + 0.05, -0.5, SHELF_TOP + 0.34)


def bench(mb, rng):
    """bancada do alquimista (leste, atras do NPC): gaveteiro, tampo, alambique, frascos na bandeja, almofariz;
    prateleira de parede com potes acima"""
    F = fr(0.0)
    y0, y1 = 7.3, 9.45
    fbox(mb, F, -3.6, 3.6, 7.6, 9.3, 0.0, 2.7, WOOD, 0.06)
    fbox(mb, F, -3.85, 3.85, y0, y1, 2.7, 3.0, WOOD, 0.08)
    for u in (-2.4, 0.0, 2.4):
        fbox(mb, F, u - 1.05, u + 1.05, 7.45, 7.62, 1.95, 2.55, WOOD, 0.04)
        fbox(mb, F, u - 0.14, u + 0.14, 7.35, 7.47, 2.12, 2.38, SILVER)
    for u in (-1.75, 1.75):
        fbox(mb, F, u - 1.6, u + 1.6, 7.45, 7.62, 0.35, 1.75, WOOD, 0.04)
    top = 3.0
    # alambique: fogareiro de ferro, caldeira de latao, pescoco de cisne ate o frasco coletor
    p = F.p(-2.5, 8.4, top)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.0), (0.62, 0.0), (0.62, 0.55), (0.5, 0.62), (0.0, 0.62)], IRON, n=8)
    mb.cyl(0.36, 0.12, (p[0], p[1], p[2] + 0.64), (0, 0, 0), GLOW, n=8, bevel=0.0)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.66), (0.5, 0.66), (0.78, 0.95), (0.8, 1.35), (0.55, 1.72), (0.24, 1.92),
                                 (0.24, 2.35), (0.42, 2.6), (0.3, 2.95), (0.0, 3.05)], BRASS, n=12)
    tube = []
    for k in range(9):
        t = k / 8.0
        tube.append(F.p(-2.5 + 1.7 * t, 8.4 - 0.2 * t, top + 2.7 + 0.35 * math.sin(math.pi * t * 0.7) - 1.3 * t * t))
    mb.tube(tube, 0.12, BRASS, 6)
    q = F.p(-0.75, 8.2, top)
    lathe(mb, q[0], q[1], q[2], [(0.0, 0.0), (0.3, 0.0), (0.55, 0.3), (0.55, 0.62), (0.3, 0.9), (0.18, 1.0), (0.18, 1.55),
                                 (0.0, 1.55)], PALE, n=10)
    # bandeja com dois frascos redondos (um e o acento violeta)
    fbox(mb, F, 0.15, 1.95, 7.75, 8.9, top, top + 0.14, WOOD)
    bottle(mb, F, 0.6, 8.3, top + 0.14, 1.25, 0.45, SAGE, "round")
    bottle(mb, F, 1.45, 8.35, top + 0.14, 1.1, 0.4, ROSE, "round")
    # almofariz e pilao
    m0 = F.p(2.85, 8.75, top)
    lathe(mb, m0[0], m0[1], m0[2], [(0.0, 0.0), (0.4, 0.0), (0.52, 0.42), (0.36, 0.44), (0.0, 0.3)], TRIM, n=10)
    mb.rod(F.p(2.8, 8.7, top + 0.3), F.p(3.1, 9.1, top + 1.0), 0.11, TRIM, 6)
    # livro aberto (anotacoes) na frente
    fbox_rot(mb, F, 2.2, 7.8, top + 0.04, 1.1, 0.8, 0.08, 0.0, BOOKS[1])
    fbox(mb, F, 1.7, 2.18, 7.45, 8.15, top + 0.08, top + 0.2, "Cloth_Canvas")
    fbox(mb, F, 2.22, 2.7, 7.45, 8.15, top + 0.08, top + 0.2, "Cloth_Canvas")
    # prateleira de parede acima da bancada (entre as duas janelas)
    yb = apo(R_IN)
    fbox(mb, F, -3.2, 3.2, 9.55, yb + 0.1, 6.5, 6.72, WOOD, 0.04)
    for u in (-2.6, 2.6):
        pside(mb, F, [(yb + 0.1, 6.5), (9.7, 6.5), (yb + 0.1, 5.6)], u - 0.12, u + 0.12, IRON)
    for u, m in ((-2.1, AMBER), (-1.2, PALE), (-0.3, SAGE)):
        pp = F.p(u, 10.0, 6.72)
        lathe(mb, pp[0], pp[1], pp[2], [(0.0, 0.0), (0.34, 0.0), (0.36, 0.72), (0.26, 0.86), (0.0, 0.86)], m, n=8)
        mb.cyl(0.3, 0.14, (pp[0], pp[1], pp[2] + 0.92), (0, 0, 0), IRON, n=8, bevel=0.0)
    for k in range(4):
        fbox(mb, F, 0.5 + k * 0.3, 0.76 + k * 0.3, 9.62, 10.3, 6.72, 6.72 + 1.0 + 0.1 * (k % 2), BOOKS[k % 3])
    fcol("SG_CraftBench", F, -3.85, 3.85, y0, 9.9, -0.5, 3.0)


def lectern(mb):
    """atril com o livro de receitas (perto da porta, lado sul): o 'menu' do craft"""
    F = fr(217.5)
    r = 8.2
    mb.cyl(0.65, 0.3, F.p(0.0, r, 0.15), (0, 0, 0), IRON, n=8, bevel=0.0)
    fbox(mb, F, -0.22, 0.22, r - 0.22, r + 0.22, 0.3, 3.05, WOOD)
    fbox(mb, F, -0.6, 0.6, r - 0.5, r + 0.5, 2.7, 3.0, WOOD)
    t = math.radians(24.0)
    nY, nZ = -math.sin(t), math.cos(t)

    def at(u, d):
        return F.p(u, r + nY * d, 3.35 + nZ * d)
    mb.box((1.7, 1.25, 0.14), at(0.0, 0.0), F.r(t, 0.0, 0.0), WOOD, 0.04)
    mb.box((1.6, 1.12, 0.07), at(0.0, 0.1), F.r(t, 0.0, 0.0), BOOKS[0], 0.0)
    for s in (-1, 1):
        mb.box((0.72, 1.0, 0.12), at(s * 0.38, 0.2), F.r(t, s * 0.06, 0.0), "Cloth_Canvas", 0.0)
    fcol("SG_CraftLectern", F, -0.85, 0.85, r - 0.75, r + 0.75, -0.5, 3.6)


def chest(mb):
    """bau de ingredientes da dungeon (perto da porta, lado norte) + saco de lona"""
    F = fr(142.5)
    r = 8.5
    fbox(mb, F, -1.0, 1.0, r - 0.6, r + 0.6, 0.0, 1.05, WOOD, 0.06)
    fbox(mb, F, -1.05, 1.05, r - 0.65, r + 0.65, 1.05, 1.45, WOOD, 0.08)
    for u in (-0.6, 0.6):
        fbox(mb, F, u - 0.12, u + 0.12, r - 0.68, r + 0.68, -0.02, 1.5, IRON)
    fbox(mb, F, -0.16, 0.16, r - 0.72, r - 0.64, 0.8, 1.2, SILVER)
    s = F.p(1.55, r - 0.2, 0.0)
    mb.ico(0.55, (s[0], s[1], s[2] + 0.5), "Cloth_Canvas", 1, scale=(1.0, 1.0, 0.95))
    mb.cyl(0.24, 0.3, (s[0], s[1], s[2] + 1.12), (0, 0, 0), "Cloth_Canvas", n=6, r2=0.34, bevel=0.0)
    fcol("SG_CraftChest", F, -1.1, 2.15, r - 0.75, r + 0.75, -0.5, 1.5)


def rug(mb):
    """passadeira da porta ao caldeirao (a linha que leva o jogador a estacao)"""
    x0, x1 = CX - 9.2, CX - 3.35
    mb.box2((x0, CY - 2.0, Z + 0.05), (x1, CY + 2.0, Z + 0.1), "Cloth_SG_Navy", 0.0)
    for s in (-1, 1):
        mb.box2((x0, CY + s * 2.0, Z + 0.05), (x1, CY + s * 1.6, Z + 0.12), BOOKS[0], 0.0)
    for xx in (x0, x1 - 0.4):
        mb.box2((xx, CY - 1.6, Z + 0.05), (xx + 0.4, CY + 1.6, Z + 0.12), BOOKS[0], 0.0)


def windows_in(mb):
    """o lado de dentro das janelas: vidraca clara fria (luar), moldura clara, mainel e travessa de ferro"""
    for a in WIN_A:
        F = fr(a)
        y = apo(R_IN)
        arch_panel(mb, F, 1.0, 1.6, 12.2, 8.9, y - 0.06, y + 0.05, PALE)
        arch_band(mb, F, 1.0, 1.6, 12.2, 8.9, 0.3, y - 0.3, y + 0.05, TRIM)
        fbox(mb, F, -0.1, 0.1, y - 0.16, y - 0.04, 8.9, 13.5, IRON)
        fbox(mb, F, -1.0, 1.0, y - 0.16, y - 0.04, 11.0, 11.2, IRON)


def chandelier(mb):
    x, y = CX, CY
    zr = Z + 12.0
    ring = [(x + 1.9 * math.cos(2 * math.pi * k / 12), y + 1.9 * math.sin(2 * math.pi * k / 12), zr) for k in range(13)]
    mb.tube(ring, 0.16, IRON, 6)
    mb.cyl(0.36, 0.7, (x, y, zr + 1.9), (0, 0, 0), IRON, n=8, r2=0.2, bevel=0.0)
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        if k % 2 == 0:
            mb.rod((x + 1.9 * ca, y + 1.9 * sa, zr), (x + 0.25 * ca, y + 0.25 * sa, zr + 1.7), 0.1, IRON, 4)
        px, py = x + 1.9 * ca, y + 1.9 * sa
        mb.cyl(0.3, 0.2, (px, py, zr + 0.2), (0, 0, 0), IRON, n=6, bevel=0.0)
        mb.cyl(0.18, 0.6, (px, py, zr + 0.6), (0, 0, 0), GLOW, n=6, bevel=0.0)
    mb.rod((x, y, zr + 2.2), (x, y, Z + H + IN_DOME_RISE - 0.6), 0.12, IRON, 6)


def door_lanterns(mb):
    F = FD
    for s in (-1, 1):
        u = s * 5.7
        yb = PORT_Y1 + 0.5
        mb.beam(F.p(u, yb, 9.9), F.p(u, yb + 1.1, 9.9), 0.2, 0.2, IRON, 0.0)
        pside(mb, F, [(yb, 9.9), (yb, 8.9), (yb + 0.7, 9.9)], u - 0.1, u + 0.1, IRON)
        c = F.p(u, yb + 1.1, 8.6)
        mb.box((0.72, 0.72, 0.12), (c[0], c[1], c[2] - 0.55), F.r(), IRON, 0.0)
        mb.box((0.5, 0.5, 0.95), (c[0], c[1], c[2]), F.r(), GLOW, 0.0)
        for du in (-1, 1):
            for dy in (-1, 1):
                q = F.p(u + du * 0.3, yb + 1.1 + dy * 0.3, 8.6)
                mb.box((0.14 + 0.06, 0.2, 1.05), q, F.r(), IRON, 0.0)
        SL.spire(mb, (c[0], c[1]), 0.52, c[2] + 0.5, 0.75, IRON, n=4)


def furnishings():
    rng = random.Random(8106)
    mb = MB("SG_Craft_Furnishings", "16_CRAFT", rng, detail="near")
    shelves(mb, rng)
    bench(mb, rng)
    lectern(mb)
    chest(mb)
    rug(mb)
    windows_in(mb)
    chandelier(mb)
    door_lanterns(mb)
    mb.finish()


def lights():
    light("L_SGCraft_Cauldron", "POINT", (CX, CY, Z + 5.2), 130.0, (0.72, 0.5, 1.0), 0.6)
    light("L_SGCraft_Chandelier", "POINT", (CX, CY, Z + 11.4), 4500.0, (1.0, 0.64, 0.36), 1.0)
    p = FD.p(0.0, PORT_Y1 + 2.2, 9.2)
    light("L_SGCraft_DoorLantern", "POINT", tuple(p), 320.0, WARM, 0.5)


def build():
    shell()
    dome()
    flask()
    interior()
    cauldron()
    furnishings()
    lights()
