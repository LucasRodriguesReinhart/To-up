# sg_craft - CRAFT da Ilha 3 (Shadow Garden), 5o na hierarquia: o SALAO NOBRE DE ALQUIMIA (refinamento v2, referencia
# refs/v2/ref2_alchemy_interior.png e ref2_alchemy_ext.jpg). Substitui sg_blockout.craft. Tudo sai da planta: CRAFT_C
# (90, -60) no P2, CRAFT_R 16 (raio externo; interior ~13), porta a OESTE (CRAFT_DOOR_DEG 180) com vao 8 x 11 na mesma
# posicao. Os marcadores CRAFT_Station (centro), PLAYER_INTERACT_Craft (5 a oeste, em cima do ESTRADO) e NPC_Craft sao
# do sg_core: aqui so o lugar em volta deles.
#   EXTERIOR (v3): pavilhao redondo (24 faces) de pedra ESCURA (Stone_SGCraftDark) sobre SOCO ALTO de obsidiana com
#     remate de pedra violeta e FRISO DE ENERGIA violeta; 7 contrafortes (pinaculos navy com remate de prata); 6 janelas
#     ogivais ALTAS acesas alternadas (quente / violeta) com moldura violeta; portico ogival com moldura violeta + fio de
#     energia, OCULO violeta, empena com o frasco de prata, 2 ESTANDARTES da ordem (debrum dourado) e 2 POSTES de
#     lanterna dourada (sg_emblem.lantern_post) na porta; 4 CANTEIROS DE CRISTAL (SG_Crystal_Glow) no pe dos
#     contrafortes diagonais; domo navy com nervuras de prata, lanternim de obsidiana e o FRASCO GIGANTE no topo com 2
#     ANEIS DE ENERGIA inclinados (VFX_SGCRAFT_Ring_1/2, girando em torno do eixo vertical).
#   INTERIOR (pe-direito 18 ate a cornija, abobada de marmore negro com nervuras claras):
#     - CALDEIRAO DE FERRO com ARO e CINTAS DOURADAS, alcas douradas, 2 MEDALHOES DA ORDEM (sg_emblem.plaque), pocao
#       violeta acesa e braseiro VIOLETA por baixo, sobre ESTRADO de obsidiana com tampo de marmore negro e fio de ouro
#       (2 degraus de 0,7; colisao em 10-gonos por degrau - o jogador sobe); CIRCULO MAGICO em linhas Neon violeta;
#     - LUSTRE BAIXO de ferro negro (aro a +12,6: velas, pingentes de cristal) com o GRANDE CRISTAL pendendo sobre o
#       caldeirao e um FIO DE ENERGIA fino ate a pocao (substitui a antiga coluna de vapor solida);
#     - ESTANTES ALTAS com a 3a prateleira de frascos ACESOS em todas (ritmo), frontoes goticos nas estantes sem janela;
#       2 MESAS DE ESTUDO com lanterna dourada, sobre tapetes navy com debrum DOURADO; bancada do alquimista a leste;
#       atril e bau perto da porta; 2 POSTES DE LANTERNA ancorando o circulo magico;
#     - 2 ESTANDARTES da ordem (debrum dourado); GALERIA estreita nas costas (leste), so leitura de profundidade.
# Colisao propria: anel da parede (20 caixas) + portico com o vao, contrafortes, cobertura, ESTRADO (2 x 10-gono),
# caldeirao (8-gono), bancada, estantes, mesas, atril, bau e 4 postes de lanterna. Luzes (4): caldeirao (violeta), lustre,
# lanternas da porta (quente), bancada (quente).
import math, random
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light, Frame, ngon_col
import fm_lib
import sg_layout as L
import sg_emblem as EM

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona (5)
NEW_MATS = {
    "Glass_SGCraftAmber": (S(150, 116, 80), 0.15, 0.0, 0.22, S(168, 118, 70), 0.0),    # ambar apagado (frascos)
    "Glass_SGCraftSage": (S(104, 128, 118), 0.15, 0.0, 0.14, S(110, 140, 126), 0.0),   # verde-salvia apagado
    "Glass_SGCraftPale": (S(92, 104, 132), 0.12, 0.0, 0.12, S(96, 116, 164), 0.0),     # vidro frio (vidracas ao luar)
    "Cloth_SGCraftBook": (S(96, 58, 56), 0.85, 0.0, 0, None, 0.06),                    # encadernacao vinho apagado
    "Stone_SGCraftDark": (S(54, 52, 74), 0.8, 0.0, 0, None, 0.08),                     # alvenaria ESCURA do pavilhao (v3)
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)

CX, CY = L.CRAFT_C
Z = L.P2
DOOR = L.CRAFT_DOOR_DEG
R_IN = 13.4                    # face interna (vertices do 24-gono; interior ~13 de apotema)
R_OUT = 15.6                   # face externa (CRAFT_R 16 e o raio nominal; embasamento chega a 16,3)
H = 18.0                       # topo da parede / cornija (pe-direito interno)
STEP = 15.0                    # 24 faces
GAP = 30.0                     # meio vao angular do portico (4 faces abertas no anel)
A0, A1 = DOOR + GAP, DOOR + 360.0 - GAP
DW = L.CRAFT_DOOR_W / 2.0      # 4
DH = L.CRAFT_DOOR_H            # 11 (fecho do arco)
SPRING, RISE = 7.0, DH - 7.0   # arranque 7, flecha 4
PORT_HW = 8.1                  # meia largura do portico (cobre o vao angular de 30 no raio novo)
PORT_Y0, PORT_Y1 = 11.8, 16.6  # portico: face interna / face externa (distancia ao centro, no eixo da porta)
DOME_Z, DOME_R, DOME_RISE = 19.0, 15.8, 10.5
LAN_R, LAN_Z0, LAN_Z1 = 3.1, 28.6, 32.2
FLASK_R = 5.4                  # FRASCO maior (era 4)
FLASK_ZC = LAN_Z1 + 0.6 + 4.6  # centro do bojo (37,4)
IN_DOME_RISE = 8.6
WIN_A = [22.5, 67.5, 112.5, 247.5, 292.5, 337.5]
# janelas alternadas: quente / violeta (v2)
WIN_M = {a: ("Window_Warm" if i % 2 == 0 else "SG_VioletDeep_Glow") for i, a in enumerate(WIN_A)}
BUTT_A = [0.0, 45.0, 90.0, 135.0, 225.0, 270.0, 315.0]
SHELF_A = [67.5, 82.5, 97.5, 112.5, 247.5, 262.5, 277.5, 292.5]
BANNER_A = [52.5, 307.5]                     # faces livres (sem estante e sem janela)
TABLE_A = [37.5, 322.5]                      # mesas de estudo
RIB_A = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
GAL_A0, GAL_A1 = 315.0, 405.0                # galeria nas costas (leste) do salao
GAL_Z0, GAL_Z1 = 8.35, 8.95                  # piso da galeria (+8..9)
DAIS_R1, DAIS_R2 = 6.2, 4.8                  # estrado: degrau de baixo / de cima
DAIS_H1, DAIS_H2 = 0.7, 1.4                  # topos dos degraus (espelhos 0,7 <= 0,8)
WARM = (1.0, 0.68, 0.40)

IRON, SILVER, BRASS = "Metal_SG_Iron", "Metal_SG_Silver", "Metal_Brass"
CASTLE, TRIM, BLOCK, NAVY = "Stone_SG_Castle", "Stone_SG_Trim", "Stone_SG_Block", "Roof_SG_Navy"
WALL = "Stone_SGCraftDark"     # corpo das paredes (v3: pedra escura fria; contrafortes em Stone_SG_Castle, luar raspando)
WOOD, GLOW, VIOLET = "Wood_SG_Dark", "Lantern_Glow", "SG_Violet_Glow"
OBS, MARB, BIRON = "Stone_SG_Obsidian", "Stone_SG_MarbleBlack", "Metal_SG_BlackIron"
RUNE, CRYS, VDEEP, GOLD = "SG_Rune_Glow", "SG_Crystal_Glow", "SG_VioletDeep_Glow", "Metal_Gold"
VSTONE = "Stone_SG_Violet"
SOCLE = 2.6                    # soco alto de obsidiana (v3)
WIN_FOOT, WIN_SPRING, WIN_RISE, WIN_HW = 9.3, 14.4, 2.5, 1.35   # janelas ALTAS (v3: 9,3 -> 16,9)
OCU_Z, OCU_R = 14.8, 1.7       # oculo violeta sobre a porta (portico)
POST_A = [150.0, 210.0]        # lanternas do circulo magico (ancoras dos raios)
CRYS_A = [45.0, 135.0, 225.0, 315.0]   # canteiros de cristal no pe dos contrafortes diagonais
CHAND_Z, CHAND_R, CHAND_TIP = 12.6, 5.0, 8.2   # lustre BAIXO (lido da camera da porta): aro, raio, ponta do cristal
AMBER, SAGE, PALE, ROSE = "Glass_SGCraftAmber", "Glass_SGCraftSage", "Glass_SGCraftPale", "Glass_SG_Rose"
BOOKS = ["Cloth_SGCraftBook", "Leather", "Cloth_SG_Navy"]

P2 = Z
CAMS = {
    # 360 de fora (frente = oeste, a porta; tras = leste; lados norte e sul)
    "CAM_SGCraft_W": ((46.0, -52.0, P2 + 9.0), (90.0, -60.0, P2 + 24.0), 22),
    "CAM_SGCraft_N": ((102.0, -12.0, P2 + 18.0), (90.0, -60.0, P2 + 18.0), 22),
    "CAM_SGCraft_E": ((148.0, -46.0, P2 + 13.0), (90.0, -60.0, P2 + 22.0), 22),
    "CAM_SGCraft_S": ((108.0, -120.0, P2 + 9.0), (90.0, -60.0, P2 + 22.0), 22),
    "CAM_SGCraft_Far": ((0.0, -164.0, P2 + 50.0), (90.0, -60.0, P2 + 22.0), 30),
    # altura do jogador chegando pela rua do P2 (a porta e o frasco lidos juntos)
    "CAM_SGCraft_PH_Door": ((62.0, -58.0, P2 + 5.2), (90.0, -60.0, P2 + 11.0), 22),
    # dentro: da porta para o estrado/caldeirao; estantes; galeria; circulo; de volta; teto e lustre
    "CAM_SGCraft_In_Cauldron": ((78.2, -62.8, P2 + 6.2), (97.0, -59.0, P2 + 5.0), 18),
    "CAM_SGCraft_In_ShelvesN": ((81.5, -66.5, P2 + 6.0), (93.0, -46.5, P2 + 6.0), 18),
    "CAM_SGCraft_In_ShelvesS": ((81.5, -53.5, P2 + 6.0), (93.0, -73.5, P2 + 6.0), 18),
    "CAM_SGCraft_In_Gallery": ((80.0, -65.5, P2 + 5.2), (102.5, -57.0, P2 + 10.5), 17),
    "CAM_SGCraft_In_Circle": ((83.0, -67.5, P2 + 8.0), (92.5, -57.5, P2 + 1.4), 18),
    "CAM_SGCraft_In_Door": ((99.0, -61.0, P2 + 5.6), (76.0, -60.0, P2 + 7.0), 16),
    "CAM_SGCraft_In_Up": ((80.6, -60.0, P2 + 3.2), (93.0, -60.0, P2 + 18.0), 14),
}

# rota extra: da rua, pela porta, uma volta inteira em torno do caldeirao (raio 5,2 - SOBE no estrado, degraus 0,7) e
# saida - prova que estrado, mesas, atril, bau e estantes deixam a circulacao livre
_VOLTA = [(CX + 5.2 * math.cos(math.radians(180.0 - 30.0 * k)), CY + 5.2 * math.sin(math.radians(180.0 - 30.0 * k)))
          for k in range(13)]
EXTRA_ROUTES = {
    "CRAFT_VOLTA_CALDEIRAO": ([(CX - 20.0, CY), (CX - 13.0, CY), (CX - 8.0, CY)] + _VOLTA + [(CX - 8.0, CY), (CX - 20.0, CY)],
                              P2),
}
EXTRA_PROBES = [("CRAFT_estante_N", CX + 1.3, CY + 9.5, P2, 0.0, 1.0), ("CRAFT_bancada_L", CX + 7.6, CY, P2, 1.0, 0.0)]


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


YB_IN = apo(R_IN)              # face interna plana (~13,28): as estantes encostam aqui
SH_F = YB_IN - 1.24            # frente da caixa das estantes
YC0, YC1, YCM = YB_IN - 1.06, YB_IN - 0.28, YB_IN - 0.65   # faixa dos objetos nas prateleiras


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
    # SOCO ALTO de obsidiana (base da ordem) + remate de pedra violeta + FRISO DE ENERGIA violeta (a linha da magia)
    ring_band(mb, 15.15, 16.3, -0.4, SOCLE, OBS, A0, A1)
    ring_band(mb, 15.35, 16.05, SOCLE, SOCLE + 0.4, VSTONE, A0, A1)
    ring_band(mb, 15.3, 16.12, SOCLE + 0.4, SOCLE + 0.56, VDEEP, A0, A1)
    ring_band(mb, R_IN, R_OUT, -0.3, H, WALL, A0, A1)                    # parede (24-gono sem as 4 faces da porta)
    ring_band(mb, 15.45, 15.95, 8.7, 9.2, VSTONE, A0, A1)                # friso violeta sob as janelas
    ring_band(mb, 15.45, 16.4, H - 0.6, H, OBS, A0, A1)                  # cornija de obsidiana
    ring_band(mb, 15.0, 16.15, H, H + 1.0, VSTONE, 0.0, 360.0)           # anel de apoio do domo (volta inteira)
    ring_band(mb, 15.9, 16.22, H + 0.1, H + 0.3, SILVER, 0.0, 360.0)     # fio de prata do anel
    # contrafortes (ritmo gotico; alinhados as nervuras do domo): pe de obsidiana alto, pingadeira violeta, remate prata
    for a in BUTT_A:
        F = fr(a)
        pside(mb, F, [(15.3, 0.0), (17.5, 0.0), (17.5, 7.6), (16.7, 9.9), (15.3, 9.9)], -0.95, 0.95, CASTLE)
        pside(mb, F, [(15.3, 9.9), (16.7, 9.9), (16.7, 15.0), (15.3, 17.3)], -0.78, 0.78, CASTLE)
        fbox(mb, F, -1.1, 1.1, 15.3, 17.75, -0.1, SOCLE, OBS, 0.08)      # pe do contraforte (acompanha o soco)
        fbox(mb, F, -1.05, 1.05, 16.6, 17.62, 7.2, 7.5, VSTONE, 0.05)    # pingadeira
        fbox(mb, F, -0.84, 0.84, 16.5, 16.8, 14.85, 15.15, VSTONE, 0.04) # pingadeira de cima
        # PINACULO sobre o contraforte (coroa de agulhas em volta do domo, silhueta gotica da referencia)
        fbox(mb, F, -0.62, 0.62, 16.0, 17.24, H - 0.6, H + 1.4, VSTONE, 0.05)
        c = F.p(0.0, 16.62, H + 1.4)
        SL.spire(mb, (c[0], c[1]), 0.62, c[2], 2.9, NAVY, n=4)
        mb.ico(0.2, (c[0], c[1], c[2] + 3.0), SILVER, 1)
    # janelas ogivais ALTAS (por fora): vidraca acesa alternada quente/violeta, moldura violeta, mainel e travessa de
    # ferro negro, peitoril violeta
    for a in WIN_A:
        F = fr(a)
        y = apo(R_OUT)
        arch_panel(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, WIN_FOOT, y - 0.05, y + 0.06, WIN_M[a])
        arch_band(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, WIN_FOOT, 0.38, y - 0.05, y + 0.34, VSTONE)
        fbox(mb, F, -0.1, 0.1, y, y + 0.22, WIN_FOOT, WIN_SPRING + WIN_RISE - 0.3, BIRON)
        fbox(mb, F, -WIN_HW, WIN_HW, y, y + 0.22, 12.6, 12.8, BIRON)
        fbox(mb, F, -1.95, 1.95, y - 0.05, y + 0.6, 9.0, 9.3, VSTONE, 0.05)
    portal(mb)
    crystal_beds(mb)
    mb.finish()
    # colisao: anel refeito para o raio novo (20 caixas, mesmo padrao), contrafortes
    rm = (R_IN + R_OUT) / 2.0
    chord = 2.0 * R_OUT * math.sin(math.radians(STEP / 2.0)) + 0.1
    n = int(round((A1 - A0) / STEP))
    for k in range(n):
        am = math.radians(A0 + STEP * (k + 0.5))
        col_box("SG_CraftWall", (R_OUT - R_IN, chord, H + 0.5), (CX + rm * math.cos(am), CY + rm * math.sin(am), Z + (H - 0.5) / 2.0),
                (0, 0, am))
    for a in BUTT_A:
        fcol("SG_CraftButtress", fr(a), -0.95, 0.95, R_OUT - 0.2, 17.35, -0.5, 10.2)


def crystal_beds(mb):
    """CANTEIROS DE CRISTAL no pe dos 4 contrafortes diagonais (referencia v2: a casa da magia brota cristal): caixa baixa
    de obsidiana encostada no contraforte, 5 prismas SG_Crystal_Glow inclinados para fora, o maior no meio. Pisaveis
    (0,7 de altura), sem colisao; fora de qualquer rota."""
    rng = random.Random(8121)
    for a in CRYS_A:
        F = fr(a)
        fbox(mb, F, -1.9, 1.9, 17.7, 19.9, -0.3, 0.55, OBS, 0.08)
        fbox(mb, F, -1.7, 1.7, 17.8, 19.7, 0.55, 0.7, "Dirt_SG")
        for k, (u, y, h, r, lean) in enumerate(((0.0, 18.8, 3.6, 0.55, 0.0), (-1.05, 18.6, 2.2, 0.38, -0.35),
                                                (1.05, 18.7, 2.5, 0.4, 0.3), (-0.5, 19.35, 1.5, 0.3, -0.2),
                                                (0.65, 19.35, 1.3, 0.28, 0.25))):
            b = F.p(u, y, 0.55)
            t = F.p(u + lean * h * 0.35, y + 0.35 * h * 0.3, 0.55 + h)
            _prism(mb, b, t, r, CRYS, rot=rng.uniform(0.0, 1.0))


def _prism(mb, b, t, r, m, n=6, rot=0.0):
    """cristal: prisma hexagonal de b ate 78% do comprimento + ponta piramidal ate t"""
    bm = mb.bm
    ax = [t[i] - b[i] for i in range(3)]
    ln = math.sqrt(sum(c * c for c in ax))
    w = [c / ln for c in ax]
    ref = (1.0, 0.0, 0.0) if abs(w[0]) < 0.9 else (0.0, 1.0, 0.0)
    e1 = [w[1] * ref[2] - w[2] * ref[1], w[2] * ref[0] - w[0] * ref[2], w[0] * ref[1] - w[1] * ref[0]]
    l1 = math.sqrt(sum(c * c for c in e1))
    e1 = [c / l1 for c in e1]
    e2 = [w[1] * e1[2] - w[2] * e1[1], w[2] * e1[0] - w[0] * e1[2], w[0] * e1[1] - w[1] * e1[0]]

    def ringv(d, rr):
        out = []
        for i in range(n):
            a = rot + 2 * math.pi * i / n
            out.append(bm.verts.new(tuple(b[j] + w[j] * d + rr * (math.cos(a) * e1[j] + math.sin(a) * e2[j]) for j in range(3))))
        return out
    r0 = ringv(-0.3, r * 0.92)
    r1 = ringv(ln * 0.78, r)
    tip = bm.verts.new(tuple(t))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        bm.faces.new((r1[i], r1[j], tip))
    bm.faces.new(list(reversed(r0)))
    mb._post(r0 + r1 + [tip], m, None, 0, 1)


def portal(mb):
    """portico saliente da porta (oeste): vao ogival 8 x 11 aberto de ponta a ponta (mesma posicao), moldura de pedra
    violeta com FIO DE ENERGIA violeta, pilastras de obsidiana com pinaculos, OCULO violeta sobre a porta, empena com o
    emblema de prata do frasco, 2 ESTANDARTES da ordem (debrum dourado) ladeando a porta e 2 POSTES de lanterna dourada
    na frente"""
    F = FD
    y0, y1 = PORT_Y0, PORT_Y1
    for s in (-1, 1):
        fbox(mb, F, s * DW, s * PORT_HW, y0, y1, -0.3, H, WALL)                        # ombreiras (macico)
        fbox(mb, F, s * (DW + 0.05), s * (PORT_HW + 0.45), y0 - 0.2, y1 + 0.5, -0.4, SOCLE, OBS, 0.08)   # soco
        fbox(mb, F, s * (DW + 0.8), s * (PORT_HW + 0.45), y1 + 0.02, y1 + 0.55, SOCLE, SOCLE + 0.4, VSTONE, 0.04)
        fbox(mb, F, s * 7.3, s * 8.35, y1, y1 + 0.5, SOCLE, H, OBS, 0.06)             # pilastra de canto
        fbox(mb, F, s * 7.2, s * 8.45, y1 - 0.6, y1 + 0.6, H, H + 1.5, VSTONE, 0.06)   # base do pinaculo
        c = F.p(s * 7.82, y1 - 0.05, H + 1.5)
        SL.spire(mb, (c[0], c[1]), 0.8, c[2], 3.2, NAVY, n=4)
        mb.ico(0.26, (c[0], c[1], c[2] + 3.3), SILVER, 1)
    spandrels(mb, F, DW, RISE, SPRING, H, y0, y1, WALL)
    # moldura do vao (frente e dentro) + fio de energia + pingadeira ogival acima
    arch_band(mb, F, DW, RISE, SPRING, 0.9, 0.8, y1, y1 + 0.5, VSTONE)
    arch_band(mb, F, DW + 0.8, RISE + 0.8, SPRING, SOCLE + 0.4, 0.16, y1 + 0.05, y1 + 0.58, VDEEP)
    arch_band(mb, F, DW + 0.96, RISE + 0.96, SPRING, 6.3, 0.42, y1, y1 + 0.34, OBS)
    arch_band(mb, F, DW, RISE, SPRING, 0.8, 0.7, y0 - 0.4, y0, VSTONE)
    # OCULO violeta sobre a porta (atravessa o portico: vidraca acesa nas duas faces), moldura violeta, cruz de ferro
    ring = [(OCU_R * math.cos(2 * math.pi * k / 16), OCU_Z + OCU_R * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    ringo = [((OCU_R + 0.45) * math.cos(2 * math.pi * k / 16), OCU_Z + (OCU_R + 0.45) * math.sin(2 * math.pi * k / 16))
             for k in range(16)]
    pslab(mb, F, ring, y1 - 0.06, y1 + 0.05, VDEEP)
    pslab(mb, F, ring, y0 - 0.05, y0 + 0.06, VDEEP)
    band(mb, F, ring + ring[:1], ringo + ringo[:1], y1 - 0.05, y1 + 0.4, VSTONE)
    fbox(mb, F, -0.09, 0.09, y1, y1 + 0.2, OCU_Z - OCU_R, OCU_Z + OCU_R, BIRON)
    fbox(mb, F, -OCU_R, OCU_R, y1, y1 + 0.2, OCU_Z - 0.09, OCU_Z + 0.09, BIRON)
    # cornija do portico e empena
    fbox(mb, F, -PORT_HW - 0.4, PORT_HW + 0.4, y0 + 0.4, y1 + 0.6, H - 0.6, H, OBS, 0.05)
    GH = 7.4                                                      # empena gotica (ingreme)
    pslab(mb, F, [(-7.0, H), (7.0, H), (0.0, H + GH)], y1 - 1.4, y1, WALL)
    for s in (-1, 1):
        a = F.p(s * 7.4, y1 - 0.55, H - 0.1)
        b = F.p(0.0, y1 - 0.55, H + GH + 0.5)
        mb.beam(a, b, 1.4, 0.55, VSTONE, 0.05)
    c = F.p(0.0, y1 - 0.55, H + GH + 0.4)
    SL.spire(mb, (c[0], c[1]), 0.55, c[2], 2.0, SILVER, n=4)
    # emblema de prata: o frasco (bojo + gargalo + boca) na empena - o que o craft faz, lido da rua
    yb0, yb1 = y1, y1 + 0.18
    ce = H + 2.3
    pslab(mb, F, [(1.15 * math.cos(2 * math.pi * k / 12 - math.pi / 2), ce + 1.15 * math.sin(2 * math.pi * k / 12 - math.pi / 2))
                  for k in range(12)], yb0, yb1, SILVER)
    pslab(mb, F, [(-0.34, ce + 0.8), (0.34, ce + 0.8), (0.34, ce + 2.25), (-0.34, ce + 2.25)], yb0, yb1, SILVER)
    pslab(mb, F, [(-0.62, ce + 2.25), (0.62, ce + 2.25), (0.62, ce + 2.6), (-0.62, ce + 2.6)], yb0, yb1, SILVER)
    # soleira de obsidiana (topo 0,05 acima do piso, como o calcamento das ruas)
    fbox(mb, F, -DW, DW, y0 - 0.2, y1 + 0.5, -0.3, 0.05, OBS)
    # ESTANDARTES da ordem (debrum dourado) na face do portico, entre a moldura e as pilastras
    for s in (-1, 1):
        EM.banner(mb, mb, mb, mb, F.p(s * 6.3, y1 + 0.5, 17.0), math.radians(DOOR), 1.7, 8.2, tails=True, trim=GOLD)
    # POSTES DE LANTERNA DOURADA na frente da porta (o ritmo de lanternas da referencia chega ate a porta)
    for s in (-1, 1):
        p = F.p(s * 6.4, y1 + 2.2, 0.0)
        EM.lantern_post(mb, mb, (p[0], p[1], p[2]), math.radians(DOOR), h=6.6, s=1.0)
        col_box("SG_CraftLanternPost", (1.2, 1.2, 7.2), (p[0], p[1], p[2] + 3.4), (0, 0, math.radians(DOOR)))
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
            if rr < LAN_R + 0.25:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + DOME_Z + (DOME_RISE + 0.08) * math.sin(phi)))
        up = (-math.sin(ar), math.cos(ar), 0.0)
        mb.sweep(pts, [(-0.24, -0.34), (0.34, -0.34), (0.34, 0.34), (-0.24, 0.34)], SILVER, up=up)
    # lanternim: tambor octogonal com fendas quentes + anel de prata (assento do frasco)
    mb.cyl(LAN_R, LAN_Z1 - LAN_Z0, (CX, CY, Z + (LAN_Z0 + LAN_Z1) / 2.0), (0, 0, math.pi / 8), OBS, n=8, bevel=0.0)
    for k in range(8):
        F = fr(45.0 * k)
        y = LAN_R * math.cos(math.pi / 8)
        arch_panel(mb, F, 0.5, 0.62, 31.0, 29.4, y - 0.05, y + 0.06, VDEEP if k % 2 else "Window_Warm", n=3)
        fbox(mb, fr(45.0 * k + 22.5), -0.3, 0.3, LAN_R - 0.3, LAN_R + 0.25, 28.9, LAN_Z1, VSTONE)
    mb.cyl(LAN_R + 0.5, 0.65, (CX, CY, Z + LAN_Z1 + 0.32), (0, 0, math.pi / 8), SILVER, n=8, bevel=0.0)
    mb.cyl(LAN_R + 0.12, 0.55, (CX, CY, Z + LAN_Z0 + 0.28), (0, 0, math.pi / 8), VSTONE, n=8, bevel=0.0)
    flask(mb)
    mb.finish()
    # cobertura (colisao): octogono no topo da parede
    ngon_col("SG_CraftRoof", CX, CY, 8, R_OUT + 0.8, Z + H, Z + DOME_Z + 1.0)


def flask(mb):
    """o FRASCO GIGANTE (maior, v2): bojo de vidro com o liquido violeta um pouco acima do equador, gargalo, boca e
    rolha de prata, preso ao lanternim por 4 garras de prata (v3: no mesmo objeto do domo - menos MeshParts)"""
    zc = FLASK_ZC
    R = FLASK_R
    fill = 0.0                                     # nivel do liquido no equador: metade magia, metade vidro (v2)
    th_f = math.acos(-fill / R)                    # angulo (a partir do polo de baixo) do nivel
    rn = 1.7
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
    gl += [(rn, gtop + 1.1), (rn, gtop + 4.0), (rn + 0.4, gtop + 4.35), (rn + 0.4, gtop + 4.8), (rn - 0.12, gtop + 4.8)]
    lathe(mb, CX, CY, Z, gl, ROSE, n=18)
    # rolha de prata + anel do gargalo
    lathe(mb, CX, CY, Z, [(0.0, gtop + 4.4), (rn - 0.15, gtop + 4.4), (rn + 0.06, gtop + 5.6), (rn + 0.4, gtop + 5.85),
                          (rn + 0.25, gtop + 6.3), (0.5, gtop + 6.6), (0.5, gtop + 7.1), (0.0, gtop + 7.35)], SILVER, n=12)
    lathe(mb, CX, CY, Z, [(rn + 0.02, gtop + 1.5), (rn + 0.26, gtop + 1.5), (rn + 0.26, gtop + 2.0), (rn + 0.02, gtop + 2.0)],
          SILVER, n=12)
    # garras (do anel do lanternim ao bojo)
    for k in range(4):
        a = math.radians(45.0 + 90.0 * k)
        ca, sa = math.cos(a), math.sin(a)
        p0 = (CX + (LAN_R + 0.35) * ca, CY + (LAN_R + 0.35) * sa, Z + LAN_Z1 + 0.55)
        zz = zc - 1.6
        rr = math.sqrt(R * R - 1.6 * 1.6) + 0.14
        p1 = (CX + rr * ca, CY + rr * sa, Z + zz)
        mb.beam(p0, p1, 0.5, 0.42, SILVER, 0.0)
        mb.ico(0.4, p1, SILVER, 1)


def energy_rings():
    """2 ANEIS DE ENERGIA inclinados em volta do frasco (referencia ref2_alchemy_ext): pecas moveis como as do summon,
    girando em torno do eixo VERTICAL do frasco (a inclinacao faz o bamboleio ler de longe)"""
    for idx, (tilt, azim, R, rpm) in enumerate(((18.0, 0.0, 7.9, 4.2), (-34.0, 90.0, 9.9, -3.4)), 1):
        vf = MB("VFX_SGCRAFT_Ring_%d" % idx, "12_VFX_HELPERS", random.Random(8110 + idx), detail="near")
        t, p = math.radians(tilt), math.radians(azim)
        ct, st, cp, sp = math.cos(t), math.sin(t), math.cos(p), math.sin(p)
        pts = []
        for k in range(33):
            th = 2 * math.pi * k / 32.0
            lx, ly, lz = R * math.cos(th), R * math.sin(th) * ct, R * math.sin(th) * st
            pts.append((CX + lx * cp - ly * sp, CY + lx * sp + ly * cp, Z + FLASK_ZC + lz))
        vf.tube(pts, 0.32, VDEEP, 8)
        ob = vf.finish()
        ob["pivot"] = [round(CX, 3), round(CY, 3), round(Z + FLASK_ZC, 3)]
        ob["axis"] = [0.0, 0.0, 1.0]
        ob["rpm"] = rpm
        ob["vfx"] = "anel de energia %d do frasco do craft: inclinado, gira em torno do eixo vertical" % idx


# ------------------------------------------------------------------ interior: piso, estrado, circulo magico, abobada
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


def magic_circle(mb):
    """CIRCULO MAGICO no piso em volta do estrado: 2 aneis de energia rente (+0,055..0,09), 12 glifos e 4 raios; as 2
    lanternas da porta (POST_A) sao as ancoras do circulo (sem glifo embaixo delas)"""
    ring_band(mb, 8.75, 9.05, 0.055, 0.09, VDEEP, 0.0, 360.0, 7.5)     # v3: 1 anel so (o estrado ja traz ouro + energia)
    ring_band(mb, 7.1, 7.25, 0.055, 0.085, GOLD, 0.0, 360.0, 7.5)
    for k in range(12):
        a = 15.0 + 30.0 * k
        if min(abs(a - p) for p in POST_A) < 20.0:
            continue
        ar = math.radians(a)
        c = pol(8.05, a, 0.072)
        if k % 3 == 0:                                    # duas barras tangentes
            for d in (-0.2, 0.2):
                mb.box((0.24, 0.62, 0.036), (c[0] + d * math.cos(ar), c[1] + d * math.sin(ar), c[2]), (0, 0, ar), RUNE, 0.0)
        elif k % 3 == 1:                                  # barra + tico radial
            mb.box((0.24, 0.66, 0.036), c, (0, 0, ar), RUNE, 0.0)
            t = pol(8.55, a, 0.072)
            mb.box((0.3, 0.22, 0.036), t, (0, 0, ar), RUNE, 0.0)
        else:                                             # losango
            mb.box((0.46, 0.46, 0.036), c, (0, 0, ar + math.pi / 4), RUNE, 0.0)
    for a in (60.0, 240.0, 330.0, 0.0):
        mb.box((1.4, 0.2, 0.036), pol(8.05, a, 0.072), (0, 0, math.radians(a)), VDEEP, 0.0)


def dais_step(mb, r, z0, z1, n=30):
    """degrau do estrado: corpo de obsidiana, tampo de marmore negro embutido e fio de ouro na borda do tampo"""
    lathe(mb, CX, CY, Z, [(0.0, z0), (r, z0), (r, z1 - 0.06), (r - 0.06, z1), (0.0, z1)], OBS, n=n)
    lathe(mb, CX, CY, Z, [(0.0, z1 - 0.02), (r - 0.55, z1 - 0.02), (r - 0.55, z1 + 0.02), (0.0, z1 + 0.02)], MARB, n=n)
    ring_band(mb, r - 0.55, r - 0.3, z1 - 0.02, z1 + 0.03, GOLD, 0.0, 360.0, 360.0 / n)


def interior(mb):
    """piso, estrado, circulo e abobada (v3: no mesmo objeto da mobilia - os materiais sao os mesmos, menos MeshParts)"""
    # ESTRADO circular de 2 degraus (obsidiana + tampo de marmore negro + fio de ouro): o caldeirao sobe no palco
    dais_step(mb, DAIS_R1, -0.3, DAIS_H1)
    dais_step(mb, DAIS_R2, DAIS_H1, DAIS_H2)
    # circulo de energia no tampo de cima (em volta da lareira do caldeirao) + 8 ticos de runa
    ring_band(mb, 4.05, 4.3, DAIS_H2 + 0.02, DAIS_H2 + 0.06, VDEEP, 0.0, 360.0, 12.0)
    for k in range(8):
        a = 22.5 + 45.0 * k
        mb.box((0.46, 0.2, 0.04), pol(4.55, a, DAIS_H2 + 0.04), (0, 0, math.radians(a)), RUNE, 0.0)
    # piso nobre radial (topo 0,05 acima do piso; a colisao e a do P2): marmore negro com incrustacao de prata
    for r0, r1, m in ((DAIS_R1 + 0.05, 6.45, SILVER), (6.45, 9.85, MARB), (9.85, 10.1, SILVER), (10.1, R_IN + 0.1, MARB)):
        ring_band(mb, r0, r1, -0.3, 0.05, m, 0.0, 360.0, 7.5)
    magic_circle(mb)
    # frisos internos: rodape de obsidiana, friso violeta sobre as estantes, cornija violeta
    ring_band(mb, R_IN - 0.3, R_IN + 0.05, 0.0, 0.8, OBS, A0, A1)
    ring_band(mb, R_IN - 0.4, R_IN + 0.05, 9.16, 9.4, VSTONE, A0, A1)
    ring_band(mb, R_IN - 0.6, R_IN + 0.05, 17.4, 18.0, VSTONE, 0.0, 360.0)
    # abobada de marmore negro + nervuras claras apoiadas em misulas de obsidiana + chave central
    dome_shell(mb, R_IN, IN_DOME_RISE, R_IN + 0.4, IN_DOME_RISE + 0.4, H, MARB)
    for a in RIB_A:
        ar = math.radians(a)
        pts = []
        for k in range(13):
            phi = (math.pi / 2) * 0.9 * k / 12.0
            rr = (R_IN - 0.06) * math.cos(phi)
            if rr < 1.0:
                break
            pts.append((CX + rr * math.cos(ar), CY + rr * math.sin(ar), Z + H + (IN_DOME_RISE - 0.06) * math.sin(phi)))
        mb.sweep(pts, [(-0.3, -0.3), (0.3, -0.3), (0.3, 0.3), (-0.3, 0.3)], TRIM, up=(-math.sin(ar), math.cos(ar), 0.0))
        F = fr(a)
        if a != DOOR:
            fbox(mb, F, -0.5, 0.5, R_IN - 0.8, R_IN + 0.02, 16.0, 17.4, OBS, 0.05)
    mb.cyl(1.3, 0.75, (CX, CY, Z + H + IN_DOME_RISE - 0.38), (0, 0, 0), VSTONE, n=12, bevel=0.0)
    # colisao do estrado: um 10-gono por degrau (o jogador sobe: espelhos 0,7), apotema ~ raio do desenho
    ngon_col("SG_CraftDais", CX, CY, 10, DAIS_R1 + 0.25, Z - 0.3, Z + DAIS_H1)
    ngon_col("SG_CraftDais", CX, CY, 10, DAIS_R2 + 0.25, Z + DAIS_H1, Z + DAIS_H2)


# ------------------------------------------------------------------ o caldeirao (a estacao) - MAIOR, no estrado
CAUL_S = 1.3
CAUL_PROF = [(0.0, 0.95), (1.05, 0.95), (1.75, 1.18), (2.28, 1.7), (2.48, 2.35), (2.4, 2.95), (2.12, 3.28), (2.02, 3.38),
             (2.34, 3.46), (2.4, 3.66), (2.05, 3.66), (1.96, 3.32), (0.0, 3.32)]


def caul_r(h):
    """raio externo do bojo do caldeirao na altura h (desenho sem escala, subindo ate a aba)"""
    pr = CAUL_PROF[:9]
    for (ra, ha), (rb, hb) in zip(pr, pr[1:]):
        if ha <= h <= hb and hb > ha:
            return ra + (rb - ra) * (h - ha) / (hb - ha)
    return pr[-1][0]


def cauldron():
    mb = MB("SG_Craft_Cauldron", "16_CRAFT", random.Random(8105), detail="hero")
    x, y = CX, CY
    zb = DAIS_H2                     # base no topo do estrado (1,4)
    k = CAUL_S
    # lareira de obsidiana com FIO DE ENERGIA e o braseiro VIOLETA (o brilho por baixo do caldeirao)
    lathe(mb, x, y, Z, [(0.0, zb - 0.1), (3.8, zb - 0.1), (3.8, zb + 0.42), (3.55, zb + 0.6), (0.0, zb + 0.6)], OBS, n=16)
    ring_band(mb, 3.52, 3.84, zb + 0.28, zb + 0.4, VDEEP, 0.0, 360.0, 22.5)
    lathe(mb, x, y, Z, [(0.0, zb + 0.6), (1.9, zb + 0.6), (1.9, zb + 0.92), (1.57, zb + 0.95), (0.0, zb + 0.95)], IRON, n=12)
    mb.cyl(1.5, 0.16, (x, y, Z + zb + 1.0), (0, 0, 0), VIOLET, n=12, bevel=0.0)
    for j in range(5):
        a = 2 * math.pi * j / 5 + 0.3
        mb.ico(0.42, (x + 0.85 * math.cos(a), y + 0.85 * math.sin(a), Z + zb + 1.1), RUNE, 1, scale=(1, 1, 0.6))
    # 3 pes com sapata dourada
    for j in range(3):
        a = math.radians(90.0 + 120.0 * j)
        p0 = (x + 2.54 * math.cos(a), y + 2.54 * math.sin(a), Z + zb + 0.59)
        mb.beam(p0, (x + 1.89 * math.cos(a), y + 1.89 * math.sin(a), Z + zb + 1.76), 0.55, 0.55, IRON, 0.0)
        mb.box((0.85, 0.85, 0.2), (p0[0], p0[1], p0[2] + 0.1), (0, 0, a), GOLD, 0.0)
    # panela (bojo largo, pescoco, aba) - escala 1,3
    prof = [(r * k, zb + h * k) for r, h in CAUL_PROF]
    lathe(mb, x, y, Z, prof, IRON, n=24)
    # ARO DOURADO na aba + 2 CINTAS douradas no bojo
    lathe(mb, x, y, Z, [(2.28 * k, zb + 3.42 * k), (2.5 * k, zb + 3.42 * k), (2.5 * k, zb + 3.72 * k), (2.0 * k, zb + 3.72 * k)],
          GOLD, n=24, cap0=False, cap1=False)
    for h in (1.62, 2.95):
        r0 = caul_r(h) * k
        lathe(mb, x, y, Z, [(r0 - 0.1, zb + h * k - 0.2), (r0 + 0.1, zb + h * k - 0.2), (r0 + 0.1, zb + h * k + 0.2),
                            (r0 - 0.1, zb + h * k + 0.2)], GOLD, n=24, cap0=False, cap1=False)
    # alcas (argolas douradas) norte e sul
    for s in (-1, 1):
        ring = [(x + 0.55 * math.cos(2 * math.pi * j / 10), y + s * 3.28, Z + zb + 3.32 + 0.55 * math.sin(2 * math.pi * j / 10))
                for j in range(11)]
        mb.sweep(ring, [(0.13 * math.cos(2 * math.pi * i / 6), 0.13 * math.sin(2 * math.pi * i / 6)) for i in range(6)],
                 GOLD, up=(0.0, 1.0, 0.0))
    # MEDALHAO DA ORDEM no bojo: um para a porta (quem entra) e um para o alquimista (leste)
    ze = zb + 2.3 * k
    re_ = caul_r(2.3) * k
    for ang in (math.pi, 0.0):
        EM.plaque(mb, mb, mb, mb, (x + (re_ + 0.08) * math.cos(ang), y + (re_ + 0.08) * math.sin(ang), Z + ze), ang, 0.8)
    # POCAO violeta acesa (superficie de runa, mais clara) + bolhas + concha de mexer (do lado do alquimista)
    mb.cyl(2.62, 0.16, (x, y, Z + zb + 4.4), (0, 0, 0), RUNE, n=24, bevel=0.0)
    ring_band(mb, 1.9, 2.62, 4.42 + zb + 0.0, zb + 4.5, VIOLET, 0.0, 360.0, 15.0)
    mb.ico(0.47, (x - 0.78, y + 0.65, Z + zb + 4.52), VIOLET, 1, scale=(1, 1, 0.7))
    mb.ico(0.31, (x + 0.26, y - 1.04, Z + zb + 4.52), VIOLET, 1, scale=(1, 1, 0.7))
    mb.ico(0.22, (x + 1.1, y + 0.2, Z + zb + 4.52), VIOLET, 1, scale=(1, 1, 0.7))
    mb.rod((x + 1.17, y + 1.04, Z + zb + 3.9), (x + 2.47, y + 2.47, Z + zb + 6.5), 0.15, WOOD, 6)
    # FIO DE ENERGIA: feixe fino do cristal do lustre ate a pocao (substitui a coluna de vapor solida)
    mb.rod((x, y, Z + zb + 4.5), (x, y, Z + CHAND_TIP + 0.05), 0.09, RUNE, 6)
    mb.finish()
    ngon_col("SG_CraftCauldron", x, y, 8, 3.5, Z + zb - 0.1, Z + zb + 4.9, rot0=22.5)


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
    """uma prateleira (de u -1,68 a 1,68, fundo na parede nova) cheia de uma coisa so: livros, frascos, potes ou rolos"""
    if kind == "books":
        u = -1.68
        i = rng.randint(0, 2)
        while u < 1.55:
            w = rng.uniform(0.22, 0.34)
            h = rng.uniform(1.0, 1.42)
            if u + w > 1.68:
                break
            m = BOOKS[i % 3]
            i += 1 + (rng.random() < 0.3)
            if rng.random() < 0.12 and u < 1.0:
                t = 0.28
                fbox_rot(mb, F, u + w / 2 + h * math.sin(t) / 2, YCM, v0 + h * math.cos(t) / 2, w, 0.78, h, t, m)
                u += w + h * math.sin(t) + 0.05
                continue
            fbox(mb, F, u, u + w, YC0, YC1, v0, v0 + h, m)
            u += w + 0.02
    elif kind == "bottles":
        mats = col if isinstance(col, list) else [col]
        us = [-1.32, -0.66, 0.0, 0.66, 1.32]
        kinds = ["tall", "round", "tall", "flat", "round"]
        rng.shuffle(kinds)
        for k, u in enumerate(us):
            if rng.random() < 0.15:
                continue
            kd = kinds[k]
            h = rng.uniform(0.9, 1.3) if kd != "round" else rng.uniform(0.8, 1.0)
            r = rng.uniform(0.22, 0.3) if kd != "round" else rng.uniform(0.3, 0.36)
            bottle(mb, F, u + rng.uniform(-0.06, 0.06), YCM + rng.uniform(-0.1, 0.1), v0, h, r, mats[k % len(mats)], kd)
    elif kind == "jars":
        for u in (-1.05, -0.35, 0.35, 1.05):
            p = F.p(u, YCM, v0)
            h = rng.uniform(0.75, 0.95)
            lathe(mb, p[0], p[1], p[2], [(0.0, 0.0), (0.34, 0.0), (0.36, h * 0.8), (0.28, h), (0.0, h)], col, n=8)
            mb.cyl(0.32, 0.14, (p[0], p[1], p[2] + h + 0.05), (0, 0, 0), IRON, n=8, bevel=0.0)
    elif kind == "scrolls":
        for k, (u, dv) in enumerate(((-0.95, 0.22), (-0.5, 0.22), (-0.05, 0.22), (-0.73, 0.62), (-0.27, 0.62))):
            a = F.p(u, YC0, v0 + dv)
            b = F.p(u + 0.05, YC1, v0 + dv)
            mb.rod(a, b, 0.21, "Cloth_Canvas", 7)
        fbox(mb, F, 0.55, 0.85, YC0, YC1, v0, v0 + 1.1, BOOKS[0])
        fbox(mb, F, 0.95, 1.25, YC0, YC1, v0, v0 + 0.95, BOOKS[2])


def fbox_rot(mb, F, u, y, v, sx, sy, sz, tilt, m):
    """caixa inclinada (em torno do eixo radial local) - livro encostado"""
    mb.box((sx, sy, sz), F.p(u, y, v), F.r(0.0, -tilt, 0.0), m, 0.0)


# 5 prateleiras por estante (estantes ALTAS, v2); acentos acesos SG_Crystal_Glow em poucos frascos
# 5 prateleiras por estante (estantes ALTAS). v3: a 3a prateleira (altura dos olhos) de TODAS as estantes e a fileira
# de frascos ACESOS (violeta / ambar quente alternados) - o ritmo de luz da referencia, igual em cada vao
LIT_A = [CRYS, AMBER, "Lantern_Glow", PALE, CRYS]
LIT_B = [SAGE, CRYS, AMBER, CRYS, "Lantern_Glow"]
SHELF_ROWS = {
    67.5: ["books", ("jars", SAGE), ("bottles", LIT_A), ("bottles", PALE), "books"],
    82.5: [("jars", PALE), "books", ("bottles", LIT_B), "books", ("bottles", AMBER)],
    97.5: ["scrolls", ("bottles", AMBER), ("bottles", LIT_A), "books", ("jars", AMBER)],
    112.5: ["books", ("bottles", PALE), ("bottles", LIT_B), "scrolls", "books"],
    247.5: [("jars", AMBER), "books", ("bottles", LIT_A), ("bottles", SAGE), "scrolls"],
    262.5: ["books", "scrolls", ("bottles", LIT_B), "books", ("jars", SAGE)],
    277.5: [("bottles", SAGE), "books", ("bottles", LIT_A), ("jars", PALE), "books"],
    292.5: ["scrolls", "books", ("bottles", LIT_B), ("jars", SAGE), "books"],
}
SHELF_V = [0.5, 2.16, 3.82, 5.48, 7.14]
SHELF_TOP = 8.8


def shelves(mb, rng):
    hw = R_IN * math.sin(math.radians(STEP / 2.0)) - 0.02        # meia largura da face plana (~1,73)
    yb = YB_IN
    for a in SHELF_A:
        F = fr(a)
        fbox(mb, F, -hw, hw, yb - 0.2, yb + 0.02, 0.0, SHELF_TOP, WOOD)                 # fundo
        for s in (-1, 1):
            fbox(mb, F, s * (hw - 0.18), s * hw, SH_F, yb, 0.0, SHELF_TOP, WOOD)        # laterais
        fbox(mb, F, -hw, hw, SH_F, yb, 0.0, 0.5, WOOD)                                  # rodape
        for v in SHELF_V[1:] + [8.62]:
            fbox(mb, F, -hw + 0.18, hw - 0.18, SH_F + 0.02, yb, v - 0.14, v, WOOD)
        fbox(mb, F, -hw - 0.04, hw + 0.04, SH_F - 0.18, yb, SHELF_TOP, SHELF_TOP + 0.34, WOOD, 0.05)   # coroamento
        if a not in WIN_M:
            # frontao gotico (so nas estantes sem janela acima): empena de madeira escura com losango de pedra violeta
            pslab(mb, F, [(-hw, SHELF_TOP + 0.34), (hw, SHELF_TOP + 0.34), (0.0, SHELF_TOP + 2.2)], SH_F + 0.1, yb, WOOD)
            pslab(mb, F, [(0.0, SHELF_TOP + 0.62), (0.42, SHELF_TOP + 1.04), (0.0, SHELF_TOP + 1.46), (-0.42, SHELF_TOP + 1.04)],
                  SH_F, SH_F + 0.12, GOLD)
            c = F.p(0.0, (SH_F + yb) / 2.0 + 0.05, SHELF_TOP + 2.3)
            mb.ico(0.2, c, GOLD, 1)
        for kind, v0 in zip(SHELF_ROWS[a], SHELF_V):
            if isinstance(kind, tuple):
                shelf_row(mb, F, kind[0], v0, rng, kind[1])
            else:
                shelf_row(mb, F, kind, v0, rng)
        fcol("SG_CraftShelf", F, -hw, hw, SH_F - 0.05, yb + 0.05, -0.5, SHELF_TOP + 0.34)


def bench(mb, rng):
    """bancada do alquimista (leste, atras do NPC): gaveteiro, tampo, alambique, frascos na bandeja, almofariz;
    prateleira de parede com potes acima"""
    F = fr(0.0)
    y0, y1 = 10.2, 12.35
    fbox(mb, F, -3.6, 3.6, 10.5, 12.2, 0.0, 2.7, WOOD, 0.06)
    fbox(mb, F, -3.85, 3.85, y0, y1, 2.7, 3.0, WOOD, 0.08)
    for u in (-2.4, 0.0, 2.4):
        fbox(mb, F, u - 1.05, u + 1.05, 10.33, 10.5, 1.95, 2.55, WOOD, 0.04)
        fbox(mb, F, u - 0.14, u + 0.14, 10.23, 10.35, 2.12, 2.38, SILVER)
    for u in (-1.75, 1.75):
        fbox(mb, F, u - 1.6, u + 1.6, 10.33, 10.5, 0.35, 1.75, WOOD, 0.04)
    top = 3.0
    # alambique: fogareiro de ferro, caldeira de latao, pescoco de cisne ate o frasco coletor
    p = F.p(-2.5, 11.3, top)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.0), (0.62, 0.0), (0.62, 0.55), (0.5, 0.62), (0.0, 0.62)], IRON, n=8)
    mb.cyl(0.36, 0.12, (p[0], p[1], p[2] + 0.64), (0, 0, 0), GLOW, n=8, bevel=0.0)
    lathe(mb, p[0], p[1], p[2], [(0.0, 0.66), (0.5, 0.66), (0.78, 0.95), (0.8, 1.35), (0.55, 1.72), (0.24, 1.92),
                                 (0.24, 2.35), (0.42, 2.6), (0.3, 2.95), (0.0, 3.05)], BRASS, n=12)
    tube = []
    for k in range(9):
        t = k / 8.0
        tube.append(F.p(-2.5 + 1.7 * t, 11.3 - 0.2 * t, top + 2.7 + 0.35 * math.sin(math.pi * t * 0.7) - 1.3 * t * t))
    mb.tube(tube, 0.12, BRASS, 6)
    q = F.p(-0.75, 11.1, top)
    lathe(mb, q[0], q[1], q[2], [(0.0, 0.0), (0.3, 0.0), (0.55, 0.3), (0.55, 0.62), (0.3, 0.9), (0.18, 1.0), (0.18, 1.55),
                                 (0.0, 1.55)], PALE, n=10)
    # bandeja com dois frascos redondos (um e o acento violeta)
    fbox(mb, F, 0.15, 1.95, 10.65, 11.8, top, top + 0.14, WOOD)
    bottle(mb, F, 0.6, 11.2, top + 0.14, 1.25, 0.45, SAGE, "round")
    bottle(mb, F, 1.45, 11.25, top + 0.14, 1.1, 0.4, ROSE, "round")
    # almofariz e pilao
    m0 = F.p(2.85, 11.65, top)
    lathe(mb, m0[0], m0[1], m0[2], [(0.0, 0.0), (0.4, 0.0), (0.52, 0.42), (0.36, 0.44), (0.0, 0.3)], TRIM, n=10)
    mb.rod(F.p(2.8, 11.6, top + 0.3), F.p(3.1, 12.0, top + 1.0), 0.11, TRIM, 6)
    # livro aberto (anotacoes) na frente
    fbox_rot(mb, F, 2.2, 10.7, top + 0.04, 1.1, 0.8, 0.08, 0.0, BOOKS[1])
    fbox(mb, F, 1.7, 2.18, 10.35, 11.05, top + 0.08, top + 0.2, "Cloth_Canvas")
    fbox(mb, F, 2.22, 2.7, 10.35, 11.05, top + 0.08, top + 0.2, "Cloth_Canvas")
    # prateleira de parede acima da bancada
    yb = YB_IN
    fbox(mb, F, -3.2, 3.2, 12.45, yb + 0.1, 6.5, 6.72, WOOD, 0.04)
    for u in (-2.6, 2.6):
        pside(mb, F, [(yb + 0.1, 6.5), (12.6, 6.5), (yb + 0.1, 5.6)], u - 0.12, u + 0.12, IRON)
    for u, m in ((-2.1, AMBER), (-1.2, PALE), (-0.3, SAGE)):
        pp = F.p(u, 12.9, 6.72)
        lathe(mb, pp[0], pp[1], pp[2], [(0.0, 0.0), (0.34, 0.0), (0.36, 0.72), (0.26, 0.86), (0.0, 0.86)], m, n=8)
        mb.cyl(0.3, 0.14, (pp[0], pp[1], pp[2] + 0.92), (0, 0, 0), IRON, n=8, bevel=0.0)
    for k in range(4):
        fbox(mb, F, 0.5 + k * 0.3, 0.76 + k * 0.3, 12.52, 13.2, 6.72, 6.72 + 1.0 + 0.1 * (k % 2), BOOKS[k % 3])
    fcol("SG_CraftBench", F, -3.85, 3.85, y0, 12.8, -0.5, 3.0)


def study_tables(mb, rng):
    """2 MESAS DE ESTUDO (referencia v2): livro aberto, balanca, alambique pequeno / vela, banco; cada uma sobre
    tapete navy com debrum dourado rente"""
    for i, a in enumerate(TABLE_A):
        F = fr(a)
        rc = 10.6
        # tapete navy + debrum dourado (rente: 0,05..0,12)
        fbox(mb, F, -2.4, 2.4, rc - 1.9, rc + 1.9, 0.05, 0.1, "Cloth_SG_Navy")
        for u0, u1, w0, w1 in ((-2.4, -2.08, rc - 1.9, rc + 1.9), (2.08, 2.4, rc - 1.9, rc + 1.9),
                               (-2.08, 2.08, rc - 1.9, rc - 1.62), (-2.08, 2.08, rc + 1.62, rc + 1.9)):
            fbox(mb, F, u0, u1, w0, w1, 0.05, 0.12, GOLD)
        # mesa
        for su in (-1, 1):
            for sy in (-1, 1):
                fbox(mb, F, su * 1.5 - 0.13, su * 1.5 + 0.13, rc + sy * 0.75 - 0.13, rc + sy * 0.75 + 0.13, 0.0, 2.5, WOOD)
        fbox(mb, F, -1.85, 1.85, rc - 1.05, rc + 1.05, 2.5, 2.78, WOOD, 0.06)
        # banco
        st = F.p(-2.55 if i == 0 else 2.55, rc - 0.4, 0.0)
        mb.cyl(0.42, 1.5, (st[0], st[1], st[2] + 0.75), (0, 0, 0), WOOD, n=8, bevel=0.0)
        mb.cyl(0.56, 0.16, (st[0], st[1], st[2] + 1.58), (0, 0, 0), WOOD, n=8, bevel=0.0)
        # livro aberto
        fbox_rot(mb, F, -0.9, rc - 0.35, 2.8, 1.15, 0.85, 0.08, 0.0, BOOKS[i % 3])
        fbox(mb, F, -1.42, -0.92, rc - 0.72, rc + 0.02, 2.84, 2.96, "Cloth_Canvas")
        fbox(mb, F, -0.88, -0.38, rc - 0.72, rc + 0.02, 2.84, 2.96, "Cloth_Canvas")
        # balanca de dois pratos
        bp = F.p(0.6, rc + 0.35, 2.78)
        mb.rod(bp, (bp[0], bp[1], bp[2] + 1.5), 0.07, IRON, 6)
        mb.box((1.7, 0.1, 0.1), F.p(0.6, rc + 0.35, 4.22), F.r(), IRON, 0.0)
        for s in (-1, 1):
            pa = F.p(0.6 + s * 0.78, rc + 0.35, 4.2)
            mb.rod(pa, (pa[0], pa[1], pa[2] - 0.62), 0.03, IRON, 4)
            mb.cyl(0.3, 0.07, (pa[0], pa[1], pa[2] - 0.68), (0, 0, 0), SILVER, n=8, bevel=0.0)
        if i == 0:
            # alambique pequeno
            ap = F.p(1.35, rc - 0.5, 2.78)
            lathe(mb, ap[0], ap[1], ap[2], [(0.0, 0.0), (0.34, 0.0), (0.44, 0.35), (0.3, 0.7), (0.12, 0.8), (0.12, 1.15),
                                            (0.2, 1.3), (0.0, 1.35)], BRASS, n=8)
            bottle(mb, F, 1.0, rc + 0.6, 2.78, 0.8, 0.26, AMBER)
        else:
            # vela acesa + tinteiro
            vp = F.p(1.35, rc - 0.5, 2.78)
            mb.cyl(0.13, 0.6, (vp[0], vp[1], vp[2] + 0.3), (0, 0, 0), "Plaster_SG", n=6, bevel=0.0)
            mb.ico(0.1, (vp[0], vp[1], vp[2] + 0.72), GLOW, 1, scale=(1, 1, 1.6))
            tp = F.p(0.95, rc + 0.6, 2.78)
            lathe(mb, tp[0], tp[1], tp[2], [(0.0, 0.0), (0.2, 0.0), (0.22, 0.22), (0.1, 0.3), (0.0, 0.3)], IRON, n=6)
        # lanterna dourada pequena no canto de tras da mesa (luz de estudo; so Neon)
        EM.lantern_head(mb, mb, F.p(-1.45 if i == 0 else 1.45, rc + 0.62, 2.78 + 0.62), math.radians(a), 0.46)
        fcol("SG_CraftTable", F, -2.0, 2.0, rc - 1.15, rc + 1.15, -0.5, 2.78)


def gallery(mb, rng):
    """GALERIA anular estreita a +8,35..8,95 nas costas (leste) do salao: nao entravel (sem escada), so leitura de
    profundidade - piso de madeira sobre misulas, balaustrada de ferro negro e livros; sem colisao (inalcancavel)"""
    ring_band(mb, 10.8, R_IN + 0.05, GAL_Z0, GAL_Z1, WOOD, GAL_A0, GAL_A1)
    ring_band(mb, 10.72, 10.98, GAL_Z0 - 0.15, GAL_Z1 + 0.05, VSTONE, GAL_A0, GAL_A1)    # testeira
    for k in range(7):
        a = GAL_A0 + 15.0 * k
        pside(mb, fr(a), [(R_IN + 0.02, GAL_Z0), (11.0, GAL_Z0), (R_IN + 0.02, GAL_Z0 - 1.8)], -0.4, 0.4, OBS)
    # balaustrada de ferro negro
    for k in range(13):
        a = GAL_A0 + 7.5 * k
        mb.box((0.16, 0.16, 2.35), pol(11.05, a, GAL_Z1 + 1.175), (0, 0, math.radians(a)), BIRON, 0.0)
    ring_band(mb, 10.9, 11.2, GAL_Z1 + 2.3, GAL_Z1 + 2.55, BIRON, GAL_A0, GAL_A1)        # corrimao
    ring_band(mb, 10.98, 11.12, GAL_Z1 + 1.1, GAL_Z1 + 1.25, BIRON, GAL_A0, GAL_A1)      # travessa
    # livros na galeria (pilhas deitadas + uma fila em pe contra a parede)
    for j, a in enumerate((332.0, 356.0, 22.0)):
        F = fr(a)
        for k in range(3):
            fbox(mb, F, -0.55 + 0.06 * k, 0.45 - 0.06 * k, 12.1, 12.9, GAL_Z1 + 0.2 * k, GAL_Z1 + 0.2 * (k + 1),
                 BOOKS[(j + k) % 3])
    F = fr(8.0)
    u = -0.9
    while u < 0.9:
        w = rng.uniform(0.22, 0.3)
        fbox(mb, F, u, u + w, 12.35, YB_IN - 0.05, GAL_Z1, GAL_Z1 + rng.uniform(0.95, 1.25), BOOKS[rng.randint(0, 2)])
        u += w + 0.03


def banners(mb):
    """2 ESTANDARTES da ordem (emblema unico, debrum DOURADO - referencia v2) nas faces livres (v3: o medalhao de cima
    da porta deu lugar ao oculo violeta; a marca da ordem agora esta no caldeirao)"""
    for a in BANNER_A:
        EM.banner(mb, mb, mb, mb, pol(13.15, a, 14.0), math.radians(a + 180.0), 2.8, 7.6, tails=True, trim=GOLD)


def circle_lanterns(mb):
    """2 POSTES DE LANTERNA dourada ancorando o circulo magico dos dois lados da passadeira (referencia: lanternas em
    volta do estrado) - colisao fina propria, fora da volta do caldeirao (raio 5,2) e da passadeira"""
    for a in POST_A:
        b = pol(8.05, a, 0.05)
        EM.lantern_post(mb, mb, b, math.radians(a), h=4.4, s=0.8)
        col_box("SG_CraftLanternPost", (1.0, 1.0, 5.6), (b[0], b[1], b[2] + 2.6), (0, 0, math.radians(a)))


def lectern(mb):
    """atril com o livro de receitas (perto da porta, lado sul): o 'menu' do craft"""
    F = fr(217.5)
    r = 11.0
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
    r = 11.4
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
    """passadeira da porta ao estrado (a linha que leva o jogador a estacao): navy com debrum DOURADO rente"""
    x0, x1 = CX - 13.3, CX - 6.45
    mb.box2((x0, CY - 2.2, Z + 0.05), (x1, CY + 2.2, Z + 0.1), "Cloth_SG_Navy", 0.0)
    for s in (-1, 1):
        mb.box2((x0, CY + s * 2.2, Z + 0.05), (x1, CY + s * 1.78, Z + 0.12), GOLD, 0.0)
    for xx in (x0, x1 - 0.42):
        mb.box2((xx, CY - 1.78, Z + 0.05), (xx + 0.42, CY + 1.78, Z + 0.12), GOLD, 0.0)


def windows_in(mb):
    """o lado de dentro das janelas: vidraca acesa (fria nas quentes de fora? nao - mesma leitura: quente/violeta
    alternadas; as quentes leem PALE frio ao luar por dentro, as violeta ficam violeta), moldura clara, ferragens"""
    for a in WIN_A:
        F = fr(a)
        y = YB_IN
        m_in = "Window_Warm" if WIN_M[a] == "Window_Warm" else VDEEP    # a mesma leitura acesa por dentro (salao vivo)
        arch_panel(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, 9.4, y - 0.06, y + 0.05, m_in)
        arch_band(mb, F, WIN_HW, WIN_RISE, WIN_SPRING, 9.4, 0.3, y - 0.3, y + 0.05, VSTONE)
        fbox(mb, F, -0.1, 0.1, y - 0.16, y - 0.04, 9.4, WIN_SPRING + WIN_RISE - 0.3, BIRON)
        fbox(mb, F, -WIN_HW, WIN_HW, y - 0.16, y - 0.04, 12.6, 12.8, BIRON)


def chandelier(mb):
    """LUSTRE de ferro negro BAIXO (aro a +12,6, lido da camera da porta) com 8 velas acesas, 8 pingentes de cristal e o
    GRANDE CRISTAL SG_Crystal_Glow pendendo sobre o caldeirao (ponta a +8,2, 2,3 acima da pocao; o fio de energia sai
    dela); correntes ate a abobada. Sem colisao (fora do alcance de quem esta no estrado)."""
    x, y = CX, CY
    zr = Z + CHAND_Z
    R = CHAND_R
    ring = [(x + R * math.cos(2 * math.pi * k / 16), y + R * math.sin(2 * math.pi * k / 16), zr) for k in range(17)]
    mb.tube(ring, 0.22, BIRON, 6)
    ring2 = [(x + (R - 0.9) * math.cos(2 * math.pi * k / 16), y + (R - 0.9) * math.sin(2 * math.pi * k / 16), zr - 0.45)
             for k in range(17)]
    mb.tube(ring2, 0.12, GOLD, 5)
    for k in range(8):
        a = 2 * math.pi * k / 8 + math.pi / 8
        ca, sa = math.cos(a), math.sin(a)
        px, py = x + R * ca, y + R * sa
        # vela no aro (copinho dourado + vela + chama)
        mb.cyl(0.3, 0.16, (px, py, zr + 0.3), (0, 0, 0), GOLD, n=6, bevel=0.0)
        mb.cyl(0.14, 0.6, (px, py, zr + 0.68), (0, 0, 0), "Plaster_SG", n=6, bevel=0.0)
        mb.ico(0.13, (px, py, zr + 1.1), GLOW, 1, scale=(1, 1, 1.7))
        # pingente de cristal entre as velas
        b = 2 * math.pi * k / 8
        qx, qy = x + (R - 0.9) * math.cos(b), y + (R - 0.9) * math.sin(b)
        lathe(mb, qx, qy, Z, [(0.0, CHAND_Z - 1.75), (0.24, CHAND_Z - 1.25), (0.3, CHAND_Z - 0.85), (0.0, CHAND_Z - 0.5)],
              CRYS, n=5)
        # raio do aro ate o cubo
        mb.rod((px, py, zr), (x + 0.5 * ca, y + 0.5 * sa, zr + 1.3), 0.08, BIRON, 4)
    mb.cyl(0.55, 1.1, (x, y, zr + 1.4), (0, 0, 0), BIRON, n=8, r2=0.3, bevel=0.0)
    mb.cyl(0.7, 0.2, (x, y, zr + 0.85), (0, 0, 0), GOLD, n=8, bevel=0.0)
    # o GRANDE CRISTAL central (bipiramide alongada) pendendo do cubo
    t0 = CHAND_TIP
    lathe(mb, x, y, Z, [(0.0, t0), (0.6, t0 + 1.0), (1.02, t0 + 2.1), (0.78, t0 + 3.1), (0.36, t0 + 3.7), (0.0, t0 + 4.0)],
          CRYS, n=6, rot=math.pi / 6)
    mb.cyl(0.48, 0.3, (x, y, Z + t0 + 3.8), (0, 0, 0), GOLD, n=6, bevel=0.0)
    mb.rod((x, y, Z + t0 + 3.9), (x, y, zr + 0.85), 0.09, BIRON, 4)
    # correntes ate a abobada (4 tirantes + o fio central)
    for k in range(4):
        a = 2 * math.pi * k / 4 + math.pi / 4
        mb.rod((x + R * math.cos(a), y + R * math.sin(a), zr), (x + 1.1 * math.cos(a), y + 1.1 * math.sin(a), Z + H + IN_DOME_RISE - 0.9),
               0.07, BIRON, 4)
    mb.rod((x, y, zr + 1.9), (x, y, Z + H + IN_DOME_RISE - 0.6), 0.1, BIRON, 4)


def furnishings():
    rng = random.Random(8106)
    mb = MB("SG_Craft_Furnishings", "16_CRAFT", rng, detail="near")
    interior(mb)
    shelves(mb, rng)
    bench(mb, rng)
    study_tables(mb, rng)
    gallery(mb, rng)
    banners(mb)
    lectern(mb)
    chest(mb)
    rug(mb)
    circle_lanterns(mb)
    windows_in(mb)
    chandelier(mb)
    mb.finish()


def lights():
    light("L_SGCraft_Cauldron", "POINT", (CX, CY, Z + 7.4), 320.0, (0.72, 0.5, 1.0), 0.7)
    light("L_SGCraft_Chandelier", "POINT", (CX, CY, Z + 15.6), 650.0, (0.9, 0.74, 1.0), 1.0)
    p = FD.p(0.0, PORT_Y1 + 2.2, 8.0)
    light("L_SGCraft_DoorLantern", "POINT", tuple(p), 340.0, WARM, 0.5)
    q = fr(0.0).p(0.0, 9.2, 7.6)
    light("L_SGCraft_Bench", "POINT", tuple(q), 900.0, WARM, 0.8)


def build():
    shell()
    dome()
    energy_rings()
    cauldron()
    furnishings()
    lights()
