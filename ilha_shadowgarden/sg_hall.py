# sg_hall - INTERIOR do Mining Hall da Ilha 3 (Shadow Garden), PLANTA v4 (ONDA 1, agente 1b, 2026-09-30).
# Substitui sg_blockout.hall(). A CASCA (paredes da nave com a porta 28 x 34, janelas 10 x 34 das naves laterais, parede
# norte com o vao do arco triunfal 40 x 60, presbiterio/torre-coroa com o BOLSO do trono e o muro do retabulo com o vao
# do arco secreto, tetos colidiveis) e do sg_castle (1a). Aqui: tudo o que fica DENTRO do salao (x +-92, y 66..262,
# piso 52,2, pe-direito 84) e do presbiterio (x +-20, y 262..300, piso 54,6), e o TRONO MOVEL.
# Salao-igreja (HALLENKIRCHE): nave central de 128 + 2 naves laterais de 24, arcada de 8 pilares compostos por lado
# (x +-66, tramos de 22,5), arcos da arcada nascendo a +46 com o PANO DA ARCADA ate os formeiros; abobadas de nervuras
# na nave (fecho a +83,9) e nas naves laterais (fecho a +76), ambas com o formeiro ogival (+74 no tramo) em comum.
# Acabamento APROVADO (04/05, 04b, 04c) reaplicado com RITMO na escala nova (nada esticado: o detalhe fica na escala do
# avatar e REPETE por tramo):
#   - naves laterais: PILASTRAS COM COLUNELOS em cada tramo, paramento espesso com SILHAR ate o CORDAO, 1 NICHO por
#     tramo (A = misula + candeia de 3 velas, B = prateleira + vaso de ferro + arandela), GALERIA alta (+22) com
#     CORRIMAO de prata e grade de ferro, VITRAIS RECUADOS no vao da casca (vidro 1,05 para dentro, chumbo,
#     rendilhado com oculo violeta, moldura na face e peitoril);
#   - pilares da arcada: soco em talude, nucleo chanfrado, 4 colunelos com base de torno, capitel (anel violeta +
#     cavete + abaco); arcos de 2 ordens com CAPA de obsidiana;
#   - ABOBADAS: panos lisos azul-noite, linhas de fiada, nervuras em PERA, formeiros, CHAVES em florao (o emblema so na
#     chave do meio, sobre o medalhao do piso);
#   - LUSTRES grandes com velas de cera CREME (4, cada um com luz);
#   - parede norte: ARCO TRIUNFAL de 3 ordens nos 40 x 60 da casca, pilares compostos com pinaculos e a ROSACEA DA LUA
#     acima do arco (com 2 lancetas); parede sul: portal visto de dentro (ombreiras com colunelo violeta, verga e
#     arco de descarga);
#   - PISO LADRILHADO NA GEOMETRIA: lajes de marmore negro em fiadas desencontradas com junta chanfrada (le no Roblox
#     sem textura), faixas de obsidiana com filete de prata nas linhas dos pilares, medalhao com o emblema e a faixa
#     de TAPETE roxo no eixo da porta ate o trono (sobe os 3 degraus do presbiterio);
#   - PRESBITERIO: silhar, cordao, colunelos de canto, abobada ogival de nervuras (o perfil da ordem externa do arco),
#     estandartes, tocheiros, o BOLSO do trono emoldurado (leste) e o NICHO CEGO simetrico (oeste), o RETABULO com a
#     cornija e o VITRAL DE LUAR acima do trono (contraluz) e o ARCO SECRETO de 12 x 18 em CANTARIA (aduelas e
#     ombreiras em relevo raso <= 0,12: o trono passa rente) com o forro do vao e a soleira.
# TRONO MOVEL = objeto SEPARADO 'SG_Hall_ThroneMov' (catedra gotica aprovada no 04c, escala 1,22, assento fundo,
# crescente sem espada) + soco de 2 degraus + ESPALDAR-RETABULO de 13,8 x 19 que TAPA o arco secreto; colisao propria
# COL_SGHallThroneMov_*. Nada do trono encosta em peca fixa: ele desliza 27,5 em +X (THRONE_Rest -> THRONE_Park) por
# cima do piso do presbiterio ate o bolso (x 20..35,5; y 288..300; ate +22) e o volume varrido fica livre (QA).
# Z-FIGHT (regra da onda 1): tudo o que veste uma face da casca fica >= 0,15 na frente dela (o fundo coplanar e de
# sentido oposto: inerte); camadas de piso >= 0,08; nada de faixa/cordao no plano exato de outra peca (F10/F7).
# NAO modela minerio. Dentro da MINE_RECT nada colidivel; o corredor da porta fica livre.
# O kit de cantaria (ogiva, painel, perfil, bloco, pinaculo...) e uma COPIA do sg_castle: o 1a reescreve o sg_castle
# em paralelo e o salao nao pode depender das constantes dele.
import math, random
import bmesh
import sg_lib as SL
from sg_lib import MB, col_box, col_box2, light
import fm_lib
import sg_layout as L
import sg_emblem as EM

S = fm_lib.S
# ------------------------------------------------------------------ materiais novos da zona
NEW_MATS = {
    "Slate_SGHallVault": (S(26, 30, 60), 0.85, 0.0, 0, None, 0.0),        # panos da abobada: azul-noite liso
    "Slate_SGHallVaultJoint": (S(50, 56, 94), 0.85, 0.0, 0, None, 0.0),   # linhas de fiada da abobada
    "Slate_SGHallNiche": (S(58, 50, 76), 0.8, 0.0, 0, None, 0.0),         # fundo dos nichos / galeria: pedra lisa escura
    "Wax_SGHallCandle": (S(212, 170, 116), 0.7, 0.0, 0, None, 0.0),       # cera CREME QUENTE
    "Glass_SGHallMoon": (S(96, 124, 186), 0.4, 0.0, 0.4, S(110, 145, 220), 0.0),   # vitral de luar (= sg_castle)
    "Glass_SGHallViolet": (S(112, 56, 196), 0.3, 0.0, 0.9, S(130, 70, 230), 0.0),   # medalhoes / rosacea
}
for _k, _v in NEW_MATS.items():
    fm_lib.MATS.setdefault(_k, _v)
fm_lib.MATS.setdefault("Stone_SG_TrimLow", (S(132, 128, 134), 0.8, 0.0, 0, None, 0.06))

MARBLE, OBS, SILVER, IRON = "Stone_SG_MarbleBlack", "Stone_SG_Obsidian", "Metal_SG_Silver", "Metal_SG_BlackIron"
CLOTH, VIOST, RUNE, VGLOW = "Cloth_SG_Purple", "Stone_SG_Violet", "SG_Rune_Glow", "SG_VioletDeep_Glow"
VSOFT, NAVYC = "SG_VioletSoft_Glow", "Cloth_SG_Navy"
CS, TR, VA, NI = "Stone_SG_Castle", "Stone_SG_Trim", "Slate_SGHallVault", "Slate_SGHallNiche"
VJ = "Slate_SGHallVaultJoint"
CAPL = "Stone_SG_TrimLow"           # remate perto do jogador
ASH = "Stone_SG_Block_B"            # silhar
MOON, VGLASS = "Glass_SGHallMoon", "Glass_SGHallViolet"
IRONL = "Metal_SG_Iron"
WAX, FLAME = "Wax_SGHallCandle", "Lantern_Glow"
COURSES = (1.4, 1.05)               # fiadas do silhar do salao (as do castelo x 1,34: a parede e 2x)

# ------------------------------------------------------------------ planta (sg_layout v4)
Z = L.HALL
X0, X1, Y0, Y1 = L.HALL_X0, L.HALL_X1, L.HALL_Y0, L.HALL_Y1
MX0, MY0, MX1, MY1 = L.MINE_RECT
AX = L.ARCADE_X                                  # 66
AY = list(L.ARCADE_Y)                            # 78 .. 235,5
PHX, PHY = L.ARCADE_PIER[0] / 2.0, L.ARCADE_PIER[1] / 2.0    # nucleo 4 (x) x 6 (y)
NHW = AX - PHX                                   # 64: meia largura da nave central (face da arcada)
AIN = AX + PHX                                   # 68: face da arcada do lado da nave lateral
ACX = (AIN + X1) / 2.0                           # 80: eixo da nave lateral
CEIL_H = L.HALL_CEIL - Z                         # 84
ZC = CEIL_H - 0.25                               # fecho da abobada da nave (>= 0,12 do teto da casca: F7)
CAP = 46.0                                       # topo dos capiteis = nascenca de arcos e abobadas
F_RISE = 28.0                                    # flecha do formeiro num tramo de 22,5 (+74)
A_TOP = 30.0                                     # flecha transversal da nave lateral (fecho +76)
GAL_H = 22.0                                     # piso da galeria alta
PF = 0.8                                         # paramento espesso (face da casca em t = 0)
VAULT_Y = [Y0] + AY + [Y1]
CZ = L.CHANCEL_Z                                 # 54,6
CX0, CY0, CX1, CY1 = L.CHANCEL                   # -20, 262, 20, 300
CH_Y0 = Y1 + L.HALL_WALL                         # 267: face do presbiterio atras do arco
RY0, RY1 = L.RETABLE_Y                           # 300, 308
POCKET = L.THRONE_POCKET                         # (20, 288, 35,5, 300, 54,6, 76,6)
WIN_Y = [y + 11.25 for y in AY]                  # vaos da casca: 1 por tramo (= blockout do castelo)
WIN_A, WIN_SILL, WIN_SPRING, WIN_RISE = 5.0, 30.0, 56.0, 8.0    # 10 x 34 (apice +64)
DW, DH = L.HALL_DOOR_W / 2.0, L.HALL_DOOR_H
# arco triunfal: vao livre hw 16, 3 ordens de 4/3 (externa hw 20 = largura do vao da casca), apice externo +59,4
TRI_HW, TRI_SPRING, TRI_RISE, TRI_N = 16.0, 36.0, 19.3, 3
TRI_O = 4.0
ROSE_Z, ROSE_R = 72.2, 8.0
CORD = 9.2                                       # cordao com pingadeira (arranque dos arcos dos nichos)
ACORD = 9.0                                      # cordao do presbiterio (acima do piso dele)

# trono (catedra do 04c) na escala 1,22 + soco + espaldar-retabulo
TH_S = 1.22
TH_BACK = RY0 - 0.8                              # 299,2: costas do objeto movel (o retabulo fixo comeca em 299,48)
TH_FRONT = L.THRONE_REST[1] - L.THRONE_SIZE[1] / 2.0    # 288,5
TH_HW = L.THRONE_SIZE[0] / 2.0 - 0.1             # 6,9
TH_Y = 295.9                                     # linha das costas da cadeira (d = 0 do trono do 04c)
SOCO = (0.4, 0.35)                               # 2 degraus do soco movel
SOCO_H = SOCO[0] + SOCO[1]

CAMS = {
    "CAM_SGHall_DoorIn": ((5.0, 69.0, Z + 5.2), (0.0, 262.0, Z + 30.0), 18),
    "CAM_SGHall_NaveMid": ((12.0, 150.0, Z + 5.2), (-8.0, 262.0, Z + 30.0), 18),
    "CAM_SGHall_Ceiling": ((0.0, 112.0, Z + 5.2), (0.0, 178.0, Z + 84.0), 14),
    "CAM_SGHall_Aisle": ((80.0, 82.0, Z + 5.2), (77.0, 250.0, Z + 24.0), 18),
    "CAM_SGHall_AisleWall": ((72.0, 146.0, Z + 5.2), (92.0, 157.0, Z + 22.0), 20),
    "CAM_SGHall_Pier": ((50.0, 130.0, Z + 5.2), (66.0, 145.5, Z + 16.0), 20),
    "CAM_SGHall_Chancel": ((0.0, 226.0, Z + 5.2), (0.0, 285.0, Z + 38.0), 18),
    "CAM_SGHall_ThroneFront": ((0.0, 270.0, CZ + 5.2), (0.0, 300.0, CZ + 10.0), 20),
    "CAM_SGHall_Throne34": ((-12.0, 277.0, CZ + 5.2), (3.0, 297.0, CZ + 9.0), 20),
    "CAM_SGHall_Seat": ((2.2, 284.5, CZ + 5.2), (0.0, 294.0, CZ + 3.6), 26),
    "CAM_SGHall_FromThrone": ((0.0, 285.5, CZ + 5.2), (0.0, 66.0, Z + 22.0), 18),
    "CAM_SGHall_DoorOut": ((-8.0, 96.0, Z + 5.2), (4.0, Y0, Z + 26.0), 20),
}

EXTRA_ROUTES = {
    # volta pela margem da zona de minerio (prova que nada fecha a nave central)
    "SALAO_VOLTA": ([(0.0, Y0 + 3.0), (MX0 + 1.5, MY0 + 2.0), (MX0 + 1.5, MY1 - 2.0), (MX1 - 1.5, MY1 - 2.0),
                     (MX1 - 1.5, MY0 + 2.0), (0.0, Y0 + 3.0)], Z),
    # naves laterais andaveis de ponta a ponta (entra por um vao da arcada, sai por outro)
    "NAVE_LATERAL_O": ([(0.0, 89.0), (-56.0, 89.25), (-80.0, 89.25), (-80.0, 246.0), (-56.0, 247.0), (0.0, 247.0)], Z),
    "NAVE_LATERAL_L": ([(0.0, 89.0), (56.0, 89.25), (80.0, 89.25), (80.0, 246.0), (56.0, 247.0), (0.0, 247.0)], Z),
}
EXTRA_PROBES = []


# ================================================================== KIT de cantaria (copia do sg_castle)
def _P(W, u, t, z):
    (ox, oy), (ux, uy), (nx, ny) = W
    return (ox + ux * u + nx * t, oy + uy * u + ny * t, z)


def _dedupe(poly):
    out = []
    for p in poly:
        if not out or abs(p[0] - out[-1][0]) > 1e-4 or abs(p[1] - out[-1][1]) > 1e-4:
            out.append(p)
    if len(out) > 2 and abs(out[0][0] - out[-1][0]) < 1e-4 and abs(out[0][1] - out[-1][1]) < 1e-4:
        out.pop()
    return out


def _faces_ok(mb, fs):
    bmesh.ops.recalc_face_normals(mb.bm, faces=[f for f in fs if f is not None])


def panel(mb, W, poly, t0, t1, m):
    """prisma de um poligono (u, z) no plano da parede W, de t0 a t1"""
    poly = _dedupe(poly)
    bm = mb.bm
    a = [bm.verts.new(_P(W, u, t0, z)) for u, z in poly]
    b = [bm.verts.new(_P(W, u, t1, z)) for u, z in poly]
    n = len(poly)
    fs = [bm.faces.new(a), bm.faces.new(list(reversed(b)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((a[j], a[i], b[i], b[j])))
    _faces_ok(mb, fs)
    mb._post(a + b, m, None, 0, 1)


def rect(u0, u1, z0, z1):
    return [(u0, z0), (u1, z0), (u1, z1), (u0, z1)]


def ogive(uc, a, zr, rise, d=0.0, n=6):
    """arco ogival (2 arcos) de (uc-a-d, zr) pelo apice ate (uc+a+d, zr); d = afastamento (moldura)"""
    rise = max(rise, a)
    c = (rise * rise - a * a) / (2.0 * a)
    R = a + c + d
    th1 = math.acos(max(-1.0, min(1.0, -c / R)))
    left = [(uc + c + R * math.cos(th), zr + R * math.sin(th)) for th in
            [math.pi + (th1 - math.pi) * k / n for k in range(n + 1)]]
    left[-1] = (uc, left[-1][1])
    right = [(2 * uc - u, z) for (u, z) in reversed(left[:-1])]
    return left + right


def ogive_zk(a, rise, du, d=0.0):
    """altura (acima da nascenca) do arco ogival do kit (meio vao a, flecha rise, afastamento d) a |du| do eixo"""
    rise = max(rise, a)
    c = (rise * rise - a * a) / (2.0 * a)
    R = a + c + d
    q = abs(du) + c
    return math.sqrt(max(0.0, R * R - q * q)) if q <= R else 0.0


def wall_run(mb, W, u0, u1, zb, zt, t0, t1, opens, m):
    """parede de u0 a u1 com vaos ogivais: opens = [(uc, a, peitoril, nascenca, flecha)]"""
    cur = u0
    for uc, a, zs, zr, rise in sorted(opens):
        l, r = uc - a, uc + a
        if l - cur > 0.01:
            panel(mb, W, rect(cur, l, zb, zt), t0, t1, m)
        if zs - zb > 0.01:
            panel(mb, W, rect(l, r, zb, zs), t0, t1, m)
        panel(mb, W, [(r, zt), (l, zt)] + ogive(uc, a, zr, rise), t0, t1, m)
        cur = r
    if u1 - cur > 0.01:
        panel(mb, W, rect(cur, u1, zb, zt), t0, t1, m)


def ledge(mb, W, u0, u1, prof, m):
    """perfil [(t, z)] extrudado de u0 a u1 ao longo da parede W"""
    bm = mb.bm
    prof = _dedupe(prof)
    a = [bm.verts.new(_P(W, u0, t, z)) for t, z in prof]
    b = [bm.verts.new(_P(W, u1, t, z)) for t, z in prof]
    n = len(prof)
    fs = [bm.faces.new(a), bm.faces.new(list(reversed(b)))]
    for i in range(n):
        j = (i + 1) % n
        fs.append(bm.faces.new((a[i], a[j], b[j], b[i])))
    _faces_ok(mb, fs)
    mb._post(a + b, m, None, 0, 1)


def block(mb, W, u0, u1, z0, z1, t0, t1, ch, m, back=True):
    """bloco de cantaria: face de tras em t0, face da frente recuada 'ch' nas 4 arestas em t1 (back=False: sem a face
    de tras, que encosta no paramento e nunca aparece)"""
    bm = mb.bm
    ch = min(ch, (u1 - u0) * 0.3, (z1 - z0) * 0.3)
    bk = [bm.verts.new(_P(W, u, t0, z)) for u, z in ((u0, z0), (u1, z0), (u1, z1), (u0, z1))]
    fr = [bm.verts.new(_P(W, u, t1, z)) for u, z in ((u0 + ch, z0 + ch), (u1 - ch, z0 + ch), (u1 - ch, z1 - ch),
                                                     (u0 + ch, z1 - ch))]
    fs = [bm.faces.new(list(reversed(fr)))]
    if back:
        fs.append(bm.faces.new(bk))
    for i in range(4):
        j = (i + 1) % 4
        fs.append(bm.faces.new((bk[i], fr[i], fr[j], bk[j])))
    for f in fs:
        f.normal_update()
    nv = _P(W, 0.0, 1.0, 0.0)
    ov = _P(W, 0.0, 0.0, 0.0)
    if fs[0].normal.x * (nv[0] - ov[0]) + fs[0].normal.y * (nv[1] - ov[1]) < 0:
        for f in fs:
            f.normal_flip()
    mb._post(bk + fr, m, None, 0, 1)


def _cut(rects, e0, e1, ez0, ez1):
    out = []
    for a, b, ra, rb in rects:
        if e1 <= a or e0 >= b or ez1 <= ra or ez0 >= rb:
            out.append((a, b, ra, rb))
            continue
        if e0 - a > 0.35:
            out.append((a, e0 - 0.06, ra, rb))
        if b - e1 > 0.35:
            out.append((e1 + 0.06, b, ra, rb))
        m0, m1 = max(a, e0 - 0.06), min(b, e1 + 0.06)
        if ez0 - ra > 0.3:
            out.append((m0, m1, ra, ez0 - 0.05))
        if rb - ez1 > 0.3:
            out.append((m0, m1, ez1 + 0.05, rb))
    return out


def ashlar(mb, W, u0, u1, z0, z1, excl=(), m=ASH, PL=4.4, dep=0.12, ch=0.08, phase=0.0, gap=0.1, hs=COURSES):
    """SILHAR em fiadas de 2 alturas, juntas desencontradas, recorte nos vaos; blocos abertos atras"""
    if z1 - z0 < 0.5 or u1 - u0 < 0.5:
        return
    per = hs[0] + hs[1]
    npair = max(1, int(round((z1 - z0) / per)))
    sc = (z1 - z0) / (npair * per)
    zz, k = z0, 0
    while zz < z1 - 0.05:
        h = hs[k % 2] * sc
        rects = [(u0, u1, zz + gap / 2, zz + h - gap / 2)]
        for e in excl:
            rects = _cut(rects, *e)
        off = phase + (k % 2) * PL * 0.5
        for a, b, ra, rb in rects:
            cuts = [a] + [u0 + off + PL * j for j in range(-1, int((u1 - u0) / PL) + 3)
                          if a + 0.9 < u0 + off + PL * j < b - 0.9] + [b]
            for c0, c1 in zip(cuts, cuts[1:]):
                p0 = c0 + (gap / 2 if c0 > a else 0.0)
                p1 = c1 - (gap / 2 if c1 < b else 0.0)
                if p1 - p0 > 0.2 and rb - ra > 0.2:
                    block(mb, W, p0, p1, ra, rb, -0.03, dep, ch, m, back=False)
        zz += h
        k += 1


def drip(z, e=0.5, h=0.62, back=-0.1):
    """perfil de CORDAO com pingadeira (t, z)"""
    return [(back, z - h * 0.45), (e * 0.55, z - h * 0.45), (e, z - h * 0.18), (e, z + h * 0.12),
            (e * 0.45, z + h * 0.55), (back, z + h * 0.55)]


def plinth(zb, z1, e0=0.85, e1=0.4, back=-0.1):
    zt = z1 - (e0 - e1)
    return [(back, zb), (e0, zb), (e0, zt), (e1, z1), (back, z1)]


def ngon_pts(cx, cy, r, n, rot0=None):
    rot0 = 180.0 / n if rot0 is None else rot0
    return [(cx + r * math.cos(math.radians(rot0 + 360.0 * k / n)), cy + r * math.sin(math.radians(rot0 + 360.0 * k / n)))
            for k in range(n)]


def frustum(mb, cx, cy, r0, r1, n, z0, z1, m, rot0=None, top=True):
    bm = mb.bm
    a = [bm.verts.new((x, y, z0)) for x, y in ngon_pts(cx, cy, r0, n, rot0)]
    b = [bm.verts.new((x, y, z1)) for x, y in ngon_pts(cx, cy, r1, n, rot0)]
    bm.faces.new(list(reversed(a)))
    if top:
        bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def sq_ch(x, y, hw, c, rot=0.0):
    pts = [(-hw + c, -hw), (hw - c, -hw), (hw, -hw + c), (hw, hw - c), (hw - c, hw), (-hw + c, hw), (-hw, hw - c),
           (-hw, -hw + c)]
    ca, sa = math.cos(rot), math.sin(rot)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def finial(mb, x, y, z, s=1.0, m=SILVER):
    prof = [(0.17, 0.0), (0.24, 0.1), (0.14, 0.22), (0.3, 0.46), (0.22, 0.68), (0.09, 0.84), (0.13, 0.96),
            (0.0, 1.45)]
    if s < 1.2:
        prof = [(0.2, 0.0), (0.14, 0.2), (0.3, 0.46), (0.1, 0.82), (0.0, 1.45)]
    EM._lathe(mb, (x, y, z), [(r * s, h * s) for r, h in prof], m, 6, math.pi / 6)


def pinnacle(mb, x, y, z0, s=1.0, hb=3.0, hn=None, body_m=CS, spire_m="Roof_SG_Navy", gab=True, crock=True, rot=0.0,
             ring_m=SILVER, cap_m=OBS):
    """PINACULO do kit: corpo de quinas chanfradas com cornija e GABLETES, agulha octogonal com anel, crochés e
    florao. Devolve o topo."""
    hn = 5.6 * s if hn is None else hn
    hw = 1.0 * s
    zt = z0 + hb
    mb.prism(sq_ch(x, y, hw, 0.24 * s, rot), z0, zt, body_m)
    rr = hw * 1.08
    frustum(mb, x, y, rr + 0.1 * s, rr - 0.05 * s, 8, zt - 0.04, zt + 0.22 * s, cap_m, math.degrees(rot) + 22.5)
    if gab:
        bm = mb.bm
        for k in range(4):
            a = rot + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            tx, ty = -sa, ca

            def P(u, t, zz):
                return (x + ca * t + tx * u, y + sa * t + ty * u, zz)
            gw, gh, g0, g1 = 0.72 * s, 1.35 * s, hw * 0.55, hw + 0.14 * s
            pts = ((-gw, zt), (gw, zt), (0.0, zt + gh))
            A = [bm.verts.new(P(u, g0, zz)) for u, zz in pts]
            B = [bm.verts.new(P(u, g1, zz)) for u, zz in pts]
            fs = [bm.faces.new(A), bm.faces.new(list(reversed(B)))]
            for i in range(3):
                j = (i + 1) % 3
                fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
            _faces_ok(mb, fs)
            mb._post(A + B, body_m, None, 0, 1)
    rn = 0.8 * s
    SL.spire(mb, (x, y), rn, zt + 0.2 * s, hn, spire_m, n=8)
    zr = zt + 0.2 * s + hn * 0.42
    rad = rn * (1.0 - 0.42) + 0.1 * s
    if ring_m:
        frustum(mb, x, y, rad + 0.06 * s, rad - 0.04 * s, 8, zr - 0.14 * s, zr + 0.14 * s, ring_m)
    if crock:
        bm = mb.bm
        zc = zt + 0.2 * s + hn * 0.66
        rc = rn * (1.0 - 0.66)
        for k in range(4):
            a = math.pi / 8 + k * math.pi / 2
            ca, sa = math.cos(a), math.sin(a)
            tx, ty = -sa, ca
            base = [(x + ca * rc * 0.8 - tx * 0.14 * s, y + sa * rc * 0.8 - ty * 0.14 * s, zc - 0.3 * s),
                    (x + ca * rc * 0.8 + tx * 0.14 * s, y + sa * rc * 0.8 + ty * 0.14 * s, zc - 0.3 * s),
                    (x + ca * rc * 0.7, y + sa * rc * 0.7, zc + 0.25 * s)]
            tip = (x + ca * (rc + 0.42 * s), y + sa * (rc + 0.42 * s), zc + 0.18 * s)
            V = [bm.verts.new(p) for p in base] + [bm.verts.new(tip)]
            fs = [bm.faces.new((V[0], V[2], V[1])), bm.faces.new((V[0], V[1], V[3])),
                  bm.faces.new((V[1], V[2], V[3])), bm.faces.new((V[2], V[0], V[3]))]
            _faces_ok(mb, fs)
            mb._post(V, spire_m, None, 0, 1)
    top = zt + 0.2 * s + hn
    finial(mb, x, y, top - 0.45 * s, 0.9 * s)
    return top + 0.95 * s


def ring3(mb, C, U, V, N, r0, r1, t0, t1, m, n=24, a0=0.0):
    """anel no plano (U, V) com espessura ao longo de N"""
    bm = mb.bm

    def p(r, ang, t):
        return tuple(C[i] + U[i] * r * math.cos(ang) + V[i] * r * math.sin(ang) + N[i] * t for i in range(3))
    angs = [a0 + 2 * math.pi * k / n for k in range(n)]
    fi = [bm.verts.new(p(r0, a, t0)) for a in angs]
    fo = [bm.verts.new(p(r1, a, t0)) for a in angs]
    bi = [bm.verts.new(p(r0, a, t1)) for a in angs]
    bo = [bm.verts.new(p(r1, a, t1)) for a in angs]
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((fi[i], fo[i], fo[j], fi[j]))
        bm.faces.new((bi[j], bo[j], bo[i], bi[i]))
        bm.faces.new((fo[i], bo[i], bo[j], fo[j]))
        bm.faces.new((fi[j], bi[j], bi[i], fi[i]))
    mb._post(fi + fo + bi + bo, m, None, 0, 1)


def disc3(mb, C, U, V, N, r, t0, t1, m, n=24):
    bm = mb.bm

    def p(ang, t):
        return tuple(C[i] + U[i] * r * math.cos(ang) + V[i] * r * math.sin(ang) + N[i] * t for i in range(3))
    angs = [2 * math.pi * k / n for k in range(n)]
    f = [bm.verts.new(p(a, t0)) for a in angs]
    b = [bm.verts.new(p(a, t1)) for a in angs]
    bm.faces.new(f)
    bm.faces.new(list(reversed(b)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((f[j], f[i], b[i], b[j]))
    mb._post(f + b, m, None, 0, 1)


# ================================================================== referenciais de parede (t = para DENTRO)
W_W = ((X0, 0.0), (0.0, 1.0), (1.0, 0.0))
W_E = ((X1, 0.0), (0.0, 1.0), (-1.0, 0.0))
W_S = ((0.0, Y0), (1.0, 0.0), (0.0, 1.0))
W_N = ((0.0, Y1), (1.0, 0.0), (0.0, -1.0))
W_CW = ((CX0, 0.0), (0.0, 1.0), (1.0, 0.0))
W_CE = ((CX1, 0.0), (0.0, 1.0), (-1.0, 0.0))
W_R = ((0.0, RY0), (1.0, 0.0), (0.0, -1.0))


def WT(W, t):
    return (_P(W, 0.0, t, 0.0)[:2], W[1], W[2])


def N3(W):
    return (W[2][0], W[2][1], 0.0)


def U3(W):
    return (W[1][0], W[1][1], 0.0)


def rect_ut(u0, u1, t0, t1, ch=0.0):
    """retangulo (u, t) com as 2 quinas da FRENTE (t1) chanfradas"""
    if ch <= 0.0:
        return [(u0, t0), (u1, t0), (u1, t1), (u0, t1)]
    return [(u0, t0), (u1, t0), (u1, t1 - ch), (u1 - ch, t1), (u0 + ch, t1), (u0, t1 - ch)]


def wpoly(W, pts):
    P = [_P(W, u, t, 0.0)[:2] for u, t in pts]
    a = sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))
    return P if a > 0 else list(reversed(P))


def wprism(mb, W, pts, z0, z1, m, bevel=0.0):
    mb.prism(wpoly(W, pts), z0, z1, m, bevel)


def loft(mb, PA, PB, z0, z1, m):
    """solido entre o poligono PA (x, y) em z0 e PB em z1 (mesmo numero de pontos, anti-horario)"""
    bm = mb.bm
    a = [bm.verts.new((x, y, z0)) for x, y in PA]
    b = [bm.verts.new((x, y, z1)) for x, y in PB]
    n = len(a)
    bm.faces.new(list(reversed(a)))
    bm.faces.new(b)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((a[i], a[j], b[j], b[i]))
    mb._post(a + b, m, None, 0, 1)


def wloft(mb, W, A, B, z0, z1, m):
    PA, PB = wpoly(W, A), wpoly(W, B)
    loft(mb, PA, PB, z0, z1, m)


def wbox(mb, W, u0, u1, t0, t1, z0, z1, m, bevel=0.0):
    a, b = _P(W, u0, t0, z0), _P(W, u1, t1, z1)
    mb.box2(tuple(min(p, q) for p, q in zip(a, b)), tuple(max(p, q) for p, q in zip(a, b)), m, bevel)


def wcol(area, W, u0, u1, t0, t1, z0, z1):
    a, b = _P(W, u0, t0, z0), _P(W, u1, t1, z1)
    col_box2(area, tuple(min(p, q) for p, q in zip(a, b)), tuple(max(p, q) for p, q in zip(a, b)))


def band(mb, W, inner, outer, t0, t1, m, closed=False):
    """faixa solida entre 2 polilinhas (u, z) de mesmo tamanho (arquivolta, moldura, pano)"""
    bm = mb.bm
    n = len(inner)
    iF = [bm.verts.new(_P(W, u, t1, z)) for u, z in inner]
    iB = [bm.verts.new(_P(W, u, t0, z)) for u, z in inner]
    oF = [bm.verts.new(_P(W, u, t1, z)) for u, z in outer]
    oB = [bm.verts.new(_P(W, u, t0, z)) for u, z in outer]
    fs = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        fs.append(bm.faces.new((oF[i], oF[j], iF[j], iF[i])))
        fs.append(bm.faces.new((iB[i], iB[j], oB[j], oB[i])))
        fs.append(bm.faces.new((iF[i], iF[j], iB[j], iB[i])))
        fs.append(bm.faces.new((oB[i], oB[j], oF[j], oF[i])))
    if not closed:
        for k in (0, n - 1):
            fs.append(bm.faces.new((iF[k], oF[k], oB[k], iB[k])))
    _faces_ok(mb, fs)
    mb._post(iF + iB + oF + oB, m, None, 0, 1)


def moldW(mb, W, pts, t, prof, m):
    """MOLDURA varrida: perfil (a, b) ao longo da linha (u, z) no plano t; a > 0 aponta para o VAO"""
    path = [_P(W, u, t, z) for u, z in pts]
    up = N3(W)
    cu = sum(u for u, _ in pts) / len(pts)
    cz = sum(z for _, z in pts) / len(pts)
    c = _P(W, cu, t, cz)
    p0, p1 = path[0], path[1]
    tv = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    sv = (tv[1] * up[2] - tv[2] * up[1], tv[2] * up[0] - tv[0] * up[2], tv[0] * up[1] - tv[1] * up[0])
    if sum(a * (b - q) for a, b, q in zip(sv, c, p0)) < 0:
        path.reverse()
    mb.sweep(path, prof, m, True, None, up=up)


def arch_path(uc, hw, zs, zr, rise, d=0.0, n=6):
    return [(uc - hw - d, zs)] + ogive(uc, hw, zr, rise, d=d, n=n) + [(uc + hw + d, zs)]


def s_curve(t0, t1, z0, z1, k=6):
    out = []
    for i in range(k + 1):
        f = i / k
        g = f * f * (3.0 - 2.0 * f)
        out.append((t0 + (t1 - t0) * g, z0 + (z1 - z0) * f))
    return out


def rect_xy(cx, cy, hx, hy, ch):
    """retangulo (x, y) de quinas chanfradas, anti-horario"""
    ch = min(ch, hx * 0.9, hy * 0.9)
    return [(cx - hx + ch, cy - hy), (cx + hx - ch, cy - hy), (cx + hx, cy - hy + ch), (cx + hx, cy + hy - ch),
            (cx + hx - ch, cy + hy), (cx - hx + ch, cy + hy), (cx - hx, cy + hy - ch), (cx - hx, cy - hy + ch)]


# ------------------------------------------------------------------ arco ogival do 04 (nascenca de centro abatido)
def _ogive_center(hw, rise):
    xc = (hw * hw - rise * rise) / (2.0 * hw)
    c = min(xc, -0.25 * hw)
    zc = (rise * rise - hw * hw + 2.0 * hw * c) / (2.0 * rise)
    R = math.hypot(hw - c, zc)
    return c, zc, R


def ogive_right(hw, rise, n):
    c, zc, R = _ogive_center(hw, rise)
    t0 = math.atan2(-zc, hw - c)
    ta = math.atan2(rise - zc, -c)
    pts = [(c + R * math.cos(t0 + (ta - t0) * k / n), zc + R * math.sin(t0 + (ta - t0) * k / n)) for k in range(n + 1)]
    pts[0] = (hw, 0.0)
    pts[-1] = (0.0, rise)
    return pts


def ogive2(cs, hw, rise, spring, n=6):
    """(assinatura do 04) arco ogival completo no plano da parede"""
    r = ogive_right(hw, rise, n)
    left = [(cs - u, spring + v) for u, v in r]
    right = [(cs + u, spring + v) for u, v in reversed(r)][1:]
    return left + right


def ogive_z(hw, rise, u):
    c, zc, R = _ogive_center(hw, rise)
    return max(0.0, zc + math.sqrt(max(0.0, R * R - (abs(u) - c) ** 2)))


def finish(mb, recalc=True):
    """mb.finish() + remove faces de area nula"""
    ob = mb.finish(recalc=recalc)
    if ob is None:
        return ob
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    bad = [f for f in bm.faces if f.calc_area() < 1e-6]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES")
        bm.to_mesh(ob.data)
    bm.free()
    return ob


# ================================================================== geometria das abobadas
def bay_of(y):
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if ya - 1e-6 <= y <= yb + 1e-6:
            return ya, yb
    return (VAULT_Y[0], VAULT_Y[1]) if y < VAULT_Y[0] else (VAULT_Y[-2], VAULT_Y[-1])


def f_rise(ya, yb):
    return min(F_RISE, 1.25 * (yb - ya))


def F(y):
    """FORMEIRO (acima do piso): ogiva por tramo entre as linhas dos pilares; e o topo do pano da arcada, a borda da
    abobada da nave e das naves laterais e o arco da parede externa sobre o vitral"""
    ya, yb = bay_of(y)
    return CAP + ogive_z((yb - ya) / 2.0, f_rise(ya, yb), y - (ya + yb) / 2.0)


def zv(x, y):
    """intradorso da abobada da NAVE (acima do piso)"""
    d = min(abs(x), NHW) / NHW
    f = F(y)
    return f + (ZC - f) * math.sqrt(max(0.0, 1.0 - d * d))


def T_(ax):
    """perfil transversal da nave lateral (acima do piso) em |x| = ax"""
    return CAP + ogive_z(ACX - AIN, A_TOP, ax - ACX)


def za(x, y):
    """intradorso da abobada da NAVE LATERAL: formeiro nas 2 bordas, arco transversal nas linhas dos pilares"""
    ax = min(max(abs(x), AIN), X1)
    g = (T_(ax) - CAP) / A_TOP
    f = F(y)
    return f + (CAP + A_TOP - f) * g


def zceil(x, y):
    return zv(x, y) if abs(x) <= NHW else za(x, y)


# ================================================================== KIT DE VELA e remates de torno
def candle(mb, x, y, z, hc=0.6, s=1.0, dish=True, cup=False):
    """vela da ordem: prato de ferro ou copinho de prata, vela CREME nao emissiva, pavio e chama em GOTA (Neon)"""
    if dish:
        EM._lathe(mb, (x, y, z), [(0.12 * s, 0.0), (0.34 * s, 0.07 * s), (0.3 * s, 0.1 * s), (0.0, 0.07 * s)], IRONL, 6,
                  caps=(True, False))
        z += 0.07 * s
    if cup:
        EM._lathe(mb, (x, y, z), [(0.07 * s, 0.0), (0.24 * s, 0.12 * s), (0.0, 0.1 * s)], SILVER, 6, caps=(True, False))
        z += 0.1 * s
    r = 0.1 * s
    EM._lathe(mb, (x, y, z), [(r, 0.0), (r, hc - 0.04 * s), (0.0, hc - 0.01 * s)], WAX, 5, caps=(True, False))
    zt = z + hc - 0.02 * s
    mb.rod((x, y, zt - 0.02 * s), (x, y, zt + 0.12 * s), 0.018 * s + 0.01, IRON, 3, caps=False)
    zf = zt + 0.05 * s
    EM._lathe(mb, (x, y, zf), [(0.0, 0.0), (0.11 * s, 0.14 * s), (0.06 * s, 0.3 * s), (0.0, 0.44 * s)], FLAME, 5)
    return zf + 0.44 * s


def ball_finial(mb, x, y, z, r=0.2, m=SILVER, n=6):
    EM._lathe(mb, (x, y, z), [(r * 0.7, 0.0), (r * 0.42, r * 0.38), (r * 0.95, r * 0.95), (0.0, r * 1.9)], m, n,
              caps=(False, True))


# ================================================================== PISO ladrilhado (geometria)
RUN_HW, RUN_EDGE, RUN_OUT = 3.0, 3.3, 3.9        # tapete (miolo roxo) / filete de prata / margem de obsidiana
EMB_C = (0.0, (AY[2] + AY[3]) / 2.0)             # medalhao no tramo do meio da zona de minerio (156,75)
EMB_R = 8.6
MED = 11.0                                       # meia-aresta do quadrado do medalhao
BAND = 0.6                                       # meia largura das faixas transversais (linha dos pilares)
STEP_Y0 = L.CHANCEL_STEPS[0][1]                  # 256,6
STEP_N, STEP_T = L.CHANCEL_STEPS[2], L.CHANCEL_STEPS[3]
STEP_R = (CZ - Z) / STEP_N


def slab_frustum(mb, x0, y0, x1, y1, zt, m, ch=0.12, dz=0.08):
    """LAJE: face de cima em zt recuada 'ch' e 4 chanfros descendo ate a junta (zt - dz): le a junta no Roblox sem
    textura com 10 triangulos (sem laterais nem fundo, que ficam no leito)"""
    bm = mb.bm
    b = [bm.verts.new(p) for p in ((x0, y0, zt - dz), (x1, y0, zt - dz), (x1, y1, zt - dz), (x0, y1, zt - dz))]
    t = [bm.verts.new(p) for p in ((x0 + ch, y0 + ch, zt), (x1 - ch, y0 + ch, zt), (x1 - ch, y1 - ch, zt),
                                   (x0 + ch, y1 - ch, zt))]
    bm.faces.new(t)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((b[i], b[j], t[j], t[i]))
    mb._post(b + t, m, None, 0, 1)


def _sub(rects, hole):
    hx0, hy0, hx1, hy1 = hole
    out = []
    for x0, y0, x1, y1 in rects:
        if hx0 >= x1 or hx1 <= x0 or hy0 >= y1 or hy1 <= y0:
            out.append((x0, y0, x1, y1))
            continue
        if hy0 > y0:
            out.append((x0, y0, x1, hy0))
        if hy1 < y1:
            out.append((x0, hy1, x1, y1))
        ya, yb = max(y0, hy0), min(y1, hy1)
        if hx0 > x0:
            out.append((x0, ya, hx0, yb))
        if hx1 < x1:
            out.append((hx1, ya, x1, yb))
    return out


def lay_field(mb, x0, y0, x1, y1, zt, rows, width, phase, m, holes=()):
    """campo de lajes em FIADAS desencontradas (fiada ao longo de x, meia laje de deslocamento)"""
    g = 0.04
    ny = max(1, int(round((y1 - y0) / rows)))
    rh = (y1 - y0) / ny
    for j in range(ny):
        ya, yb = y0 + j * rh, y0 + (j + 1) * rh
        off = phase + (j % 2) * width * 0.5
        xs = [x0] + [x0 + off + width * k for k in range(-1, int((x1 - x0) / width) + 3)
                     if x0 + 0.8 < x0 + off + width * k < x1 - 0.8] + [x1]
        for a, b in zip(xs, xs[1:]):
            r = [(a + g, ya + g, b - g, yb - g)]
            for h in holes:
                r = _sub(r, h)
            for p0, q0, p1, q1 in r:
                if p1 - p0 > 0.5 and q1 - q0 > 0.5:
                    slab_frustum(mb, p0, q0, p1, q1, zt, m)


def floor():
    mb = MB("SG_Hall_Floor", "03_MINING_HALL", random.Random(301), detail="near")
    zt = Z
    # LEITO escuro (as juntas) 0,08 abaixo das lajes: salao inteiro (nave + naves laterais)
    mb.box2((X0, Y0, zt - 0.5), (X1, Y1, zt - 0.08), OBS, 0.0)
    ecx, ecy = EMB_C
    run_holes = [(-RUN_OUT, Y0, RUN_OUT, STEP_Y0), (ecx - MED, ecy - MED, ecx + MED, ecy + MED)]
    # faixas transversais nas linhas dos pilares (obsidiana | prata | obsidiana), rentes ao topo das lajes
    lines = [Y0] + AY + [STEP_Y0]
    for y in AY:
        for xa, xb in ((X0, -RUN_OUT), (RUN_OUT, X1)):
            for p, q in ((xa, xb),):
                mb.box2((p, y - BAND, zt - 0.3), (q, y - 0.1, zt), OBS, 0.0)
                mb.box2((p, y - 0.1, zt - 0.3), (q, y + 0.1, zt), SILVER, 0.0)
                mb.box2((p, y + 0.1, zt - 0.3), (q, y + BAND, zt), OBS, 0.0)
    # estilobato: faixa de obsidiana sob as arcadas (x 62..70) e rodape junto das paredes
    for s in (-1, 1):
        a, b = sorted((s * (AX - 4.0), s * (AX + 4.0)))
        for ya, yb in zip(lines, lines[1:]):
            y0_ = ya + (BAND if ya in AY else 0.0)
            y1_ = yb - (BAND if yb in AY else 0.0)
            mb.box2((a, y0_, zt - 0.3), (b, y1_, zt), OBS, 0.0)
    # campos de lajes (nave: 6 de largura, 3 fiadas por tramo; naves laterais: 4,5 x 3 fiadas)
    y_lines = [Y0] + AY + [Y1]
    for k, (ya, yb) in enumerate(zip(y_lines, y_lines[1:])):
        f0 = ya + (BAND if ya in AY else 0.0)
        f1 = yb - (BAND if yb in AY else 0.0)
        holes = list(run_holes)
        # nave central (o miolo dos degraus do presbiterio fica para os degraus)
        top_nave = f1
        if yb == Y1:
            holes.append((-20.0, STEP_Y0, 20.0, Y1))
        for xa, xb in ((-(AX - 4.0), -RUN_OUT), (RUN_OUT, AX - 4.0)):
            lay_field(mb, xa, f0, xb, top_nave, zt, 10.4, 9.5, 2.3 * (k % 3), MARBLE, holes)
        for s in (-1, 1):
            a, b = sorted((s * (AX + 4.0), s * X1))
            lay_field(mb, a, f0, b, f1, zt, 10.4, 7.0, 1.6 * (k % 2), MARBLE)
    # medalhao: quadrado de obsidiana -> aro de prata -> campo com o EMBLEMA (rente)
    n = 32
    ang = [2 * math.pi * k / n for k in range(n)]
    R0, R1 = EMB_R + 0.5, EMB_R + 0.1
    sq = [(ecx + MED * math.cos(a) / max(abs(math.cos(a)), abs(math.sin(a))),
           ecy + MED * math.sin(a) / max(abs(math.cos(a)), abs(math.sin(a)))) for a in ang]
    circ = lambda r: [(ecx + r * math.cos(a), ecy + r * math.sin(a)) for a in ang]
    bm = mb.bm
    zb = zt - 0.3
    for outer_p, inner_p, m in ((sq, circ(R0), OBS), (circ(R0), circ(R1), SILVER)):
        oT = [bm.verts.new((x, y, zt)) for x, y in outer_p]
        iT = [bm.verts.new((x, y, zt)) for x, y in inner_p]
        oB = [bm.verts.new((x, y, zb)) for x, y in outer_p]
        iB = [bm.verts.new((x, y, zb)) for x, y in inner_p]
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((oT[i], oT[j], iT[j], iT[i]))
            bm.faces.new((oB[i], oB[j], oT[j], oT[i]))
            bm.faces.new((iT[i], iT[j], iB[j], iB[i]))
        mb._post(oT + iT + oB + iB, m, None, 0, 1)
    mb.prism(circ(R1), zb, zt - 0.12, OBS)
    EM.emblem_flat(mb, mb, mb, (ecx, ecy, zt), math.pi / 2, EMB_R * 0.97, monumental=True, up=1, glow=VSOFT,
                   field=False, seg=None)
    # TAPETE: miolo roxo +0,08 (acima de tudo), filete de prata +0,05, margem de obsidiana rente
    for ya, yb in ((Y0, ecy - MED), (ecy + MED, STEP_Y0)):
        for s in (-1, 1):
            mb.box2((s * RUN_EDGE, ya, zt - 0.3), (s * RUN_OUT, yb, zt), OBS, 0.0)
            mb.box2((s * RUN_HW, ya, zt - 0.3), (s * RUN_EDGE, yb, zt + 0.05), SILVER, 0.0)
        mb.box2((-RUN_HW, ya, zt - 0.3), (RUN_HW, yb, zt + 0.08), CLOTH, 0.0)
    # DEGRAUS do presbiterio (3 x 0,8, piso 1,8, 40 de largura): espelho recuado, focinho boleado, filete de prata
    prev = zt
    for i in range(STEP_N):
        yf = STEP_Y0 + i * STEP_T
        top = Z + STEP_R * (i + 1)
        mb.box2((-20.0, yf + 0.14, prev - (0.3 if i == 0 else 0.0)), (20.0, Y1 + 0.2, top - 0.16), OBS, 0.0)
        mb.box2((-20.0, yf - 0.06, top - 0.16), (20.0, Y1 + 0.2, top), MARBLE, 0.05)
        mb.box2((-19.96, yf + 0.08, top - 0.36), (19.96, yf + 0.2, top - 0.3), SILVER, 0.0)
        nxt = STEP_Y0 + (i + 1) * STEP_T if i + 1 < STEP_N else Y1 + 0.2
        mb.box2((-RUN_HW, yf - 0.02, top), (RUN_HW, nxt - 0.04, top + 0.08), CLOTH, 0.0)
        mb.box2((-RUN_EDGE, yf - 0.02, top), (-RUN_HW, nxt - 0.04, top + 0.05), SILVER, 0.0)
        mb.box2((RUN_HW, yf - 0.02, top), (RUN_EDGE, nxt - 0.04, top + 0.05), SILVER, 0.0)
        prev = top
    # PRESBITERIO: leito, lajes com borda de obsidiana, tapete ate o soco do trono e a SOLEIRA do arco secreto
    mb.box2((CX0, Y1 + 0.2, CZ - 0.6), (CX1, RY0, CZ - 0.08), OBS, 0.0)
    for s in (-1, 1):
        a, b = sorted((s * 20.0, s * 18.8))
        mb.box2((a, Y1 + 0.2, CZ - 0.3), (b, RY0, CZ), OBS, 0.0)
    mb.box2((-18.8, RY0 - 1.2, CZ - 0.3), (18.8, RY0, CZ), OBS, 0.0)
    ch_holes = [(-RUN_OUT, Y1 + 0.2, RUN_OUT, TH_FRONT - 0.3)]
    lay_field(mb, -18.8, Y1 + 0.2, 18.8, RY0 - 1.2, CZ, 4.5, 5.0, 0.9, MARBLE, ch_holes)
    for s in (-1, 1):
        mb.box2((s * RUN_EDGE, Y1 + 0.2, CZ - 0.3), (s * RUN_OUT, TH_FRONT - 0.3, CZ), OBS, 0.0)
        mb.box2((s * RUN_HW, Y1 + 0.2, CZ - 0.3), (s * RUN_EDGE, TH_FRONT - 0.3, CZ + 0.05), SILVER, 0.0)
    mb.box2((-RUN_HW, Y1 + 0.16, CZ - 0.3), (RUN_HW, TH_FRONT - 0.3, CZ + 0.08), CLOTH, 0.0)
    aw = SA_HW
    mb.box2((-aw, RY0, CZ - 0.25), (aw, RY1, CZ), MARBLE, 0.0)
    finish(mb)


# ================================================================== pilares, pilastras e ARCADA
def shaft_base(mb, c, r, m=CAPL, n=6):
    EM._lathe(mb, c, [(r + 0.18, 0.0), (r + 0.07, 0.27), (r + 0.12, 0.4), (r, 0.56)], m, n,
              math.pi / n, caps=(False, True))


def respond(mb, W, s, core_hw, core_d, plinth_hw, plinth_d, top, shafts, collar_z=None, zb=None):
    """PILASTRA COMPOSTA engastada na parede W (u = s): soco de obsidiana em TALUDE, faixa de remate, nucleo de quinas
    CHANFRADAS, colunelos com base de torno, colar opcional (galeria), CAPITEL = anel violeta + cavete + abaco.
    shafts = [(du, t, r)]. top = cota absoluta do abaco."""
    zb = Z if zb is None else zb
    hb = 1.2
    wprism(mb, W, rect_ut(s - plinth_hw, s + plinth_hw, -0.4, plinth_d, 0.3), zb, zb + hb, OBS, 0.06)
    wloft(mb, W, rect_ut(s - plinth_hw, s + plinth_hw, -0.4, plinth_d, 0.3),
          rect_ut(s - plinth_hw + 0.25, s + plinth_hw - 0.25, -0.4, plinth_d - 0.25, 0.3), zb + hb, zb + hb + 0.3, OBS)
    wprism(mb, W, rect_ut(s - plinth_hw + 0.2, s + plinth_hw - 0.2, -0.4, plinth_d - 0.2, 0.25), zb + hb + 0.3,
           zb + hb + 0.55, CAPL, 0.05)
    z0 = zb + hb + 0.55
    zc = top - 1.5
    wprism(mb, W, rect_ut(s - core_hw, s + core_hw, -0.4, core_d, 0.3), z0, zc, CS)
    env_s = max(abs(ds) + r for ds, t, r in shafts) + 0.08
    env_d = max(t + r for ds, t, r in shafts) + 0.08
    for ds, t, r in shafts:
        c = _P(W, s + ds, t, z0)
        nn = 6
        shaft_base(mb, c, r, CAPL, nn)
        mb.cyl(r, zc - z0 - 0.56, _P(W, s + ds, t, (z0 + 0.56 + zc) / 2.0), m=MARBLE, n=nn, bevel=0.0, caps=False,
               rot=(0, 0, math.pi / nn))
    if collar_z is not None:
        wprism(mb, W, rect_ut(s - env_s - 0.05, s + env_s + 0.05, -0.4, env_d + 0.1, 0.35), collar_z - 0.6,
               collar_z + 0.4, OBS, 0.06)
    A0 = rect_ut(s - env_s, s + env_s, -0.4, env_d, 0.35)
    wprism(mb, W, rect_ut(s - env_s - 0.06, s + env_s + 0.06, -0.4, env_d + 0.06, 0.38), zc, zc + 0.28, VIOST)
    wloft(mb, W, A0, rect_ut(s - env_s - 0.45, s + env_s + 0.45, -0.4, env_d + 0.45, 0.45), zc + 0.28, zc + 1.0, TR)
    wprism(mb, W, rect_ut(s - env_s - 0.55, s + env_s + 0.55, -0.4, env_d + 0.55, 0.3), zc + 1.0, top, TR, 0.06)
    return env_s + 0.55, env_d + 0.55


WALL_SHAFTS = [(0.0, 1.45, 0.75)]
WR_HW, WR_D, WR_PHW, WR_PD = 1.8, 1.4, 2.9, 2.35     # pilastra das paredes externas (nucleo / soco)
END_SHAFTS = [(0.0, 3.3, 0.7), (-2.4, 0.9, 0.85), (2.4, 0.9, 0.85)]   # meia-pilastra da arcada nas paredes S e N


def arcade_pier(mb, s, y):
    """PILAR COMPOSTO livre da arcada (nucleo 4 x 6 chanfrado + 4 colunelos: nave, nave lateral e os 2 arcos)"""
    x = s * AX
    hx, hy = PHX + 1.7, PHY + 1.3
    mb.prism(rect_xy(x, y, hx, hy, 0.7), Z, Z + 1.2, OBS, 0.06)
    loft(mb, rect_xy(x, y, hx, hy, 0.7), rect_xy(x, y, hx - 0.25, hy - 0.25, 0.6), Z + 1.2, Z + 1.5, OBS)
    mb.prism(rect_xy(x, y, hx - 0.2, hy - 0.2, 0.55), Z + 1.5, Z + 1.8, CAPL, 0.05)
    z0, zc = Z + 1.8, Z + CAP - 1.5
    mb.prism(rect_xy(x, y, PHX, PHY, 0.45), z0, zc, CS)
    shafts = [(x - s * (PHX + 0.4), y, 0.95), (x + s * (PHX + 0.4), y, 0.95), (x, y - PHY - 0.25, 0.7),
              (x, y + PHY + 0.25, 0.7)]
    ex, ey = PHX + 0.4 + 0.95 + 0.08, PHY + 0.25 + 0.7 + 0.08
    # base comum dos colunelos: plinto de remate + toro chanfrado que abraca o feixe
    mb.prism(rect_xy(x, y, ex + 0.18, ey + 0.18, 0.7), z0, z0 + 0.3, CAPL)
    loft(mb, rect_xy(x, y, ex + 0.12, ey + 0.12, 0.7), rect_xy(x, y, ex - 0.1, ey - 0.1, 0.6), z0 + 0.3, z0 + 0.62,
         CAPL)
    for cx, cy, r in shafts:
        nn = 6
        mb.cyl(r, zc - z0 - 0.62, (cx, cy, (z0 + 0.62 + zc) / 2.0), m=MARBLE, n=nn, bevel=0.0, caps=False,
               rot=(0, 0, math.pi / nn))
    mb.prism(rect_xy(x, y, ex + 0.06, ey + 0.06, 0.5), zc, zc + 0.28, VIOST)
    loft(mb, rect_xy(x, y, ex, ey, 0.45), rect_xy(x, y, ex + 0.45, ey + 0.45, 0.6), zc + 0.28, zc + 1.0, TR)
    mb.prism(rect_xy(x, y, ex + 0.55, ey + 0.55, 0.55), zc + 1.0, Z + CAP, TR, 0.06)
    col_box2("SG_HallPier", (x - hx, y - hy, Z - 0.5), (x + hx, y + hy, Z + CAP))


def arcade_bay(mb, s, ya, yb, foot_a, foot_b):
    """ARCO da arcada (2 ordens: intradorso de remate claro + ordem de pedra) com a CAPA de obsidiana na face da nave
    e o PANO DA ARCADA (do extradorso ate o formeiro F, que e onde as 2 abobadas nascem)"""
    W = ((s * AX, 0.0), (0.0, 1.0), (-s, 0.0))           # u = y, t para a nave
    uc, hw = (foot_a + foot_b) / 2.0, (foot_b - foot_a) / 2.0
    rise = max(hw * 1.05, f_rise(ya, yb) - 10.0)
    zs = Z + CAP
    i0 = ogive(uc, hw, zs, rise, 0.0, 4)
    i1 = ogive(uc, hw, zs, rise, 1.3, 4)
    o2 = ogive(uc, hw, zs, rise, 2.4, 4)
    h1 = ogive(uc, hw, zs, rise, 2.9, 4)
    band(mb, W, i0, i1, -1.25, 1.25, TR)
    band(mb, W, i1, o2, -PHX, PHX, CS)
    band(mb, W, o2, h1, PHX - 0.15, PHX + 0.4, OBS)
    # pano: do extradorso (ou do abaco) ate o formeiro
    n = 10
    lo, hi = [], []
    for k in range(n + 1):
        u = ya + (yb - ya) * k / n
        du = u - uc
        e = ogive_zk(hw, rise, du, 2.4) if abs(du) < hw + 2.4 else 0.0
        lo.append((u, zs + e))
        hi.append((u, max(Z + F(u) - 0.02, zs + e + 0.02)))
    band(mb, W, lo, hi, -PHX + 0.15, PHX - 0.15, CS)


def arcade(mb):
    for s in (-1, 1):
        for y in AY:
            arcade_pier(mb, s, y)
        feet = [Y0 + 3.2] + [v for y in AY for v in (y - PHY - 0.2, y + PHY + 0.2)] + [Y1 - 3.2]
        for k, (ya, yb) in enumerate(zip(VAULT_Y, VAULT_Y[1:])):
            arcade_bay(mb, s, ya, yb, feet[2 * k], feet[2 * k + 1])
    # meia-pilastras da arcada nas paredes sul e norte (x +-66)
    for W in (W_S, W_N):
        for s in (-1, 1):
            respond(mb, W, s * AX, PHX, 3.0, PHX + 1.7, 4.3, Z + CAP, END_SHAFTS)
            wcol("SG_HallPier", W, s * AX - PHX - 1.7, s * AX + PHX + 1.7, 0.0, 4.3, Z - 0.5, Z + CAP)


def corner_pier(mb, W, s, corner):
    """pilar de canto (ocupa o canto das duas paredes): corner = sinal da parede transversal"""
    a = s + corner * 2.4
    s0, s1 = min(s, a), max(s, a)
    wprism(mb, W, rect_ut(s0, s1, -0.4, 2.0, 0.25), Z, Z + 1.2, OBS, 0.06)
    wloft(mb, W, rect_ut(s0, s1, -0.4, 2.0, 0.25), rect_ut(s0, s1, -0.4, 1.8, 0.25), Z + 1.2, Z + 1.5, OBS)
    wprism(mb, W, rect_ut(s0, s1, -0.4, 1.5, 0.25), Z + 1.5, Z + CAP - 1.5, CS)
    wprism(mb, W, rect_ut(s0, s1, -0.4, 1.6, 0.3), Z + CAP - 1.5, Z + CAP - 1.22, VIOST)
    wloft(mb, W, rect_ut(s0, s1, -0.4, 1.55, 0.3), rect_ut(s0, s1, -0.4, 1.95, 0.35), Z + CAP - 1.22, Z + CAP - 0.5,
          TR)
    wprism(mb, W, rect_ut(s0, s1, -0.4, 2.05, 0.3), Z + CAP - 0.5, Z + CAP, TR, 0.06)
    wcol("SG_HallPier", W, s0, s1, 0.0, 2.0, Z - 0.5, Z + CAP)


# ================================================================== paredes: paramento, nichos, galeria
NICHE_HW, NICHE_ZS, NICHE_ZR, NICHE_RISE = 4.0, 1.8, CORD, 5.2
M1_W, M2_W = 0.56, 0.4
PROF_M1 = [(0.06, -0.02), (0.06, 0.24), (-0.1, 0.46), (-0.34, 0.3), (-0.5, 0.34), (-0.56, -0.02)]
PROF_M2 = [(0.0, -0.02), (0.0, 0.16), (-0.1, 0.26), (-0.4, 0.26), (-0.4, -0.02)]


def niche_ext(double):
    return NICHE_HW + M1_W + (M2_W if double else 0.0)


def niche(mb, W, cs, kind, double, iw):
    """NICHO: recuo real no paramento (fundo liso escuro 0,15 na frente da casca), peitoril, moldura varrida (dupla sob
    os vitrais) e fecho de obsidiana. 'A' = misula + candeia de 3 velas; 'B' = prateleira + vaso de ferro + arandela"""
    hw, zs, zr, rise = NICHE_HW, Z + NICHE_ZS, Z + NICHE_ZR, NICHE_RISE
    arc = ogive(cs, hw + 0.03, zr, rise)
    panel(mb, W, [(cs - hw - 0.03, zs - 0.02), (cs + hw + 0.03, zs - 0.02)] + list(reversed(arc)), 0.02, 0.17, NI)
    ledge(mb, W, cs - hw - 0.35, cs + hw + 0.35, [(0.02, zs - 0.42), (PF + 0.22, zs - 0.42), (PF + 0.45, zs - 0.2),
                                                  (PF + 0.45, zs), (0.02, zs)], CAPL)
    moldW(mb, W, arch_path(cs, hw, zs, zr, rise, n=3), PF, PROF_M1, CAPL)
    apex = zr + rise
    if double:
        moldW(mb, W, arch_path(cs, hw, zs, zr, rise, d=M1_W, n=4), PF, PROF_M2, VIOST)
    ka = 0.4 if not double else 0.46
    block(mb, W, cs - ka, cs + ka, apex - 0.2, apex + M1_W + (M2_W if double else 0.0) + 0.4, PF - 0.1, PF + 0.62,
          0.08, OBS)
    if kind == "A":
        zt = Z + 4.4
        prof = [(0.1, zt - 1.1)] + s_curve(0.36, 1.1, zt - 1.1, zt - 0.02, 4) + [(1.1, zt), (0.1, zt)]
        ledge(mb, W, cs - 0.55, cs + 0.55, prof, CAPL)
        ledge(mb, W, cs - 0.7, cs + 0.7, [(0.1, zt), (1.22, zt), (1.22, zt + 0.17), (0.1, zt + 0.17)], CAPL)
        c = _P(W, cs, 0.68, zt + 0.17)
        EM._lathe(iw, c, [(0.15, 0.0), (0.52, 0.06), (0.53, 0.13), (0.45, 0.13), (0.0, 0.09)], IRONL, 6,
                  caps=(True, False))
        for du, hc in ((-0.3, 0.55), (0.0, 0.86), (0.3, 0.55)):
            p = _P(W, cs + du, 0.68, zt + 0.26)
            candle(iw, p[0], p[1], p[2], hc, 1.25, dish=False)
    else:
        zt = Z + 3.6
        ledge(mb, W, cs - hw - 0.02, cs + hw + 0.02, [(0.1, zt - 0.26), (0.98, zt - 0.26), (1.1, zt - 0.15),
                                                      (1.1, zt), (0.1, zt)], CAPL)
        c = _P(W, cs, 0.6, zt)
        vs = 1.45
        EM._lathe(iw, c, [(r * vs, h * vs) for r, h in ((0.26, 0.0), (0.16, 0.2), (0.36, 0.5), (0.41, 0.8),
                                                         (0.18, 1.25), (0.29, 1.44), (0.0, 1.4))], IRONL, 6,
                  caps=(True, False))
        EM._lathe(iw, c, [(r * vs, h * vs) for r, h in ((0.37, 0.5), (0.42, 0.6), (0.37, 0.7))], SILVER, 6, closed=True)
        za_ = zt + 3.3
        iw.rod(_P(W, cs, 0.18, za_ - 0.2), _P(W, cs, 0.28, za_ - 0.2), 0.36, IRONL, 6)
        iw.rod(_P(W, cs, 0.2, za_ - 0.2), _P(W, cs, 0.42, za_ - 0.2), 0.22, SILVER, 6)
        iw.tube([_P(W, cs, 0.3, za_ - 0.35), _P(W, cs, 0.6, za_ - 0.52), _P(W, cs, 0.84, za_ - 0.3),
                 _P(W, cs, 0.88, za_ - 0.02)], 0.065, IRONL, 4)
        c = _P(W, cs, 0.88, za_)
        candle(iw, c[0], c[1], c[2], 0.6, 1.25, dish=False, cup=True)


def bay_wall(mb, W, sa, sb, niches, top, iw, cord_cut=(), PL=4.4):
    """paramento ESPESSO de sa a sb (t 0..PF) com os recuos dos nichos, silhar ate o cordao, cordao com pingadeira,
    rodape em talude. niches = [(cs, kind, double)]; top = cota absoluta do topo do paramento"""
    opens = [(cs, NICHE_HW, Z + NICHE_ZS - 0.42, Z + NICHE_ZR, NICHE_RISE) for cs, _, _ in niches]
    wall_run(mb, W, sa, sb, Z + 0.9, top, 0.0, PF, opens, CS)
    excl = [(cs - niche_ext(dbl) - 0.02, cs + niche_ext(dbl) + 0.02, Z, Z + 40.0) for cs, _, dbl in niches]
    excl += [(a, b, Z, Z + 40.0) for a, b in cord_cut]
    ashlar(mb, WT(W, PF), sa, sb, Z + 1.0, Z + CORD - 0.34, excl, PL=PL, phase=(abs(sa) * 0.37) % 1.5)
    cuts = [sa] + [v for cs, _, dbl in sorted(niches) for v in (cs - niche_ext(dbl), cs + niche_ext(dbl))] + [sb]
    segs = [(a, b) for a, b in zip(cuts[0::2], cuts[1::2])]
    for a0, b0 in cord_cut:
        segs = [q for a, b in segs for q in ((a, min(b, a0)), (max(a, b0), b)) if q[1] - q[0] > 0.3]
    for a, b in segs:
        if b - a > 0.3:
            ledge(mb, WT(W, PF), a, b, drip(Z + CORD, 0.36, 0.5), OBS)
    ledge(mb, W, sa, sb, plinth(Z - 0.05, Z + 0.95, PF + 0.3, PF + 0.12), OBS)
    for cs, kind, dbl in niches:
        niche(mb, W, cs, kind, dbl, iw)


def gallery(mb, W, sa, sb, corbels, iw, rail="iron"):
    """GALERIA ALTA: laje de obsidiana com focinho boleado, cornija em cavete, misulas em S, fundo liso escuro (0,2 na
    frente da casca). rail='iron': grade de barras, rosetas a cada 3, CORRIMAO de prata, montantes com bola;
    'stone': parapeito de pedra com paineis cegos (paredes de fundo)"""
    g = Z + GAL_H
    ledge(mb, W, sa, sb, [(-0.3, g), (2.3, g), (2.52, g + 0.12), (2.6, g + 0.38), (2.52, g + 0.64),
                          (2.35, g + 0.8), (-0.3, g + 0.8)], OBS)
    ledge(mb, W, sa, sb, [(PF - 0.1, g - 0.62), (PF + 0.12, g - 0.62)] + s_curve(PF + 0.12, 1.6, g - 0.62, g, 4)[1:] +
          [(PF - 0.1, g)], OBS)
    wbox(mb, W, sa, sb, 0.0, 0.2, g + 0.8, g + 3.0, NI, 0.0)
    for c in corbels:
        prof = [(PF - 0.1, g - 2.5)] + s_curve(PF + 0.1, 2.2, g - 2.5, g - 0.3, 4) + [(2.2, g - 0.02),
                                                                                      (PF - 0.1, g - 0.02)]
        ledge(mb, W, c - 0.45, c + 0.45, prof, OBS)
    if rail == "stone":
        ledge(mb, W, sa, sb, [(2.05, g + 0.78), (2.45, g + 0.78), (2.45, g + 1.9), (2.05, g + 1.9)], CS)
        ledge(mb, W, sa - 0.02, sb + 0.02, [(1.95, g + 1.88), (2.52, g + 1.88), (2.62, g + 1.98), (2.58, g + 2.12),
                                           (1.95, g + 2.12)], TR)
        npn = max(2, int(round((sb - sa) / 3.6)))
        pw = (sb - sa) / npn
        for i in range(npn):
            block(mb, W, sa + i * pw + 0.4, sa + (i + 1) * pw - 0.4, g + 1.0, g + 1.7, 2.43, 2.55, 0.05, CS)
        return
    ledge(iw, W, sa, sb, [(2.22, g + 0.8), (2.48, g + 0.8), (2.48, g + 1.02), (2.22, g + 1.02)], IRON)
    hr = g + 2.7
    ledge(iw, W, sa - 0.08, sb + 0.08, [(2.12, hr - 0.02), (2.58, hr - 0.02), (2.63, hr + 0.1), (2.52, hr + 0.24),
                                        (2.35, hr + 0.28), (2.18, hr + 0.24), (2.07, hr + 0.1)], SILVER)
    L_ = sb - sa - 0.9
    nb = max(4, int(round(L_ / 2.3)))
    posts = {0, nb}
    for q in range(nb + 1):
        s = sa + 0.45 + q * L_ / nb
        if q in posts:
            wprism(iw, W, rect_ut(s - 0.17, s + 0.17, 2.18, 2.52), g + 0.8, g + 2.7, IRON)
            c = _P(W, s, 2.35, g + 2.98)
            ball_finial(iw, c[0], c[1], c[2], 0.2, SILVER)
            continue
        iw.rod(_P(W, s, 2.35, g + 1.0), _P(W, s, 2.35, g + 2.7), 0.085, IRON, 4, caps=False)


def aisle_walls(mb, iw):
    """paredes externas das naves laterais: pilastra com colunelos em cada linha de pilar, pilares de canto, 1 nicho
    por tramo sob o vitral (ritmo A B B A ...), galeria de ferro, e as paredes de fundo das naves laterais"""
    kinds = ["A", "B", "B", "A", "A", "B", "B", "A"]
    for W, sx in ((W_W, -1), (W_E, 1)):
        for y in AY:
            respond(mb, W, y, WR_HW, WR_D, WR_PHW, WR_PD, Z + CAP, WALL_SHAFTS)
            wcol("SG_HallPier", W, y - WR_PHW, y + WR_PHW, 0.0, WR_PD, Z - 0.5, Z + 14.0)
        corner_pier(mb, W, Y0, 1)
        corner_pier(mb, W, Y1, -1)
        ends = [Y0 + 2.4] + [v for y in AY for v in (y - WR_PHW, y + WR_PHW)] + [Y1 - 2.4]
        for bi, (sa, sb) in enumerate(zip(ends[0::2], ends[1::2])):
            if sb - sa < 10.0:
                bay_wall(mb, W, sa, sb, [], Z + GAL_H, iw)
                gallery(mb, W, sa - 0.4, sb + 0.4, [], iw, rail="stone")
                continue
            wy = WIN_Y[bi - 1]
            bay_wall(mb, W, sa, sb, [(wy, kinds[(bi - 1) % 8], False)], Z + GAL_H, iw, PL=5.0)
            gallery(mb, W, sa - 0.4, sb + 0.4, (wy - 6.5, wy + 6.5), iw)
        wcol("SG_HallWall", W, Y0, Y1, 0.0, PF, Z - 0.5, Z + 10.0)


def end_walls(mb, iw):
    """paredes de fundo: SUL (dos 2 lados da porta) e NORTE (fora do arco triunfal), na nave e nas naves laterais"""
    for W in (W_S, W_N):
        north = W is W_N
        for s in (-1, 1):
            # nave central: da porta (ou do pilar do arco triunfal) ate a meia-pilastra da arcada
            a0 = (TPS + 2.6) if north else (DW + 2.4)
            a, b = sorted((s * a0, s * (AX - PHX - 1.7)))
            L_ = b - a
            cn = (a + b) / 2.0
            bay_wall(mb, W, a, b, [] if north else [(cn, "A", False)], Z + GAL_H, iw, PL=5.0)
            ga, gb = (a + (1.2 if (s > 0 and not north) else 0.0), b - (1.2 if (s < 0 and not north) else 0.0))
            gallery(mb, W, ga - 0.15, gb + 0.15, [a + L_ / 6.0, a + L_ / 2.0, a + 5.0 * L_ / 6.0], iw, rail="stone")
            # nave lateral: da meia-pilastra ate o pilar de canto
            a, b = sorted((s * (AX + PHX + 1.7), s * (X1 - 2.0)))
            cs = (a + b) / 2.0
            bay_wall(mb, W, a, b, [], Z + GAL_H, iw, PL=5.0)
            gallery(mb, W, a - 0.15, b + 0.15, [cs - 6.0, cs + 6.0], iw, rail="stone")
            wcol("SG_HallWall", W, a, b, 0.0, PF, Z - 0.5, Z + 10.0)
            aa, bb = sorted((s * a0, s * (AX - PHX - 1.7)))
            wcol("SG_HallWall", W, aa, bb, 0.0, PF, Z - 0.5, Z + 10.0)


# ================================================================== portal (lado de dentro da porta principal)
PROF_DOOR = [(0.12, -0.02), (0.12, 0.42), (0.0, 0.68), (-0.25, 0.8), (-0.52, 0.68), (-0.64, 0.5), (-0.88, 0.56),
             (-0.95, -0.02)]


def portal(mb):
    """a porta vista de DENTRO: ombreiras com soco em talude e COLUNELO violeta de torno, verga moldurada, ARCO DE
    DESCARGA ogival varrido (o timpano de fora fica do sg_castle) e faixa violeta"""
    W = W_S
    base_prof = [(0.62, 0.0), (0.62, 0.1), (0.54, 0.2), (0.58, 0.3), (0.46, 0.42), (0.42, 0.5), (0.46, 0.56),
                 (0.5, 0.62), (0.4, 0.74)]
    cap_prof = [(0.4, 0.0), (0.47, 0.07), (0.4, 0.15), (0.44, 0.35), (0.56, 0.6), (0.66, 0.74)]
    jw = 2.4
    for k in (-1, 1):
        a, b = sorted((k * DW, k * (DW + jw)))
        wbox(mb, W, a, b, -0.1, 1.6, Z, Z + 1.3, OBS, 0.08)
        wloft(mb, W, rect_ut(a, b, -0.1, 1.6), rect_ut(a, b, -0.1, 1.4), Z + 1.3, Z + 1.6, OBS)
        wbox(mb, W, a, b, 0.0, 1.4, Z + 1.6, Z + DH, CAPL, 0.08)
        wcol("SG_HallDoor", W, a, b, 0.0, 1.6, Z - 0.5, Z + DH)
        cx = k * (DW + 0.45)
        c0 = _P(W, cx, 1.4, Z + 1.6)
        sc = 0.9
        EM._lathe(mb, c0, [(r * sc, h * sc) for r, h in base_prof], CAPL, 8, 0.0)
        z1 = Z + DH - 1.5
        mb.cyl(0.4 * sc, z1 - (Z + 1.6 + 0.74 * sc), _P(W, cx, 1.4, (Z + 1.6 + 0.74 * sc + z1) / 2.0), m=VIOST, n=8,
               bevel=0.0, caps=False)
        EM._lathe(mb, _P(W, cx, 1.4, z1), [(r * sc, h * sc) for r, h in cap_prof], CAPL, 8, 0.0)
        wbox(mb, W, cx - 0.62, cx + 0.62, 0.8, 2.0, z1 + 0.66, z1 + 0.88, CAPL, 0.04)
    zt = Z + DH
    ledge(mb, W, -DW - jw - 0.15, DW + jw + 0.15, [(0.02, zt), (1.65, zt), (1.65, zt + 0.28), (1.4, zt + 0.46),
                                                   (1.4, zt + 1.2), (1.72, zt + 1.45), (1.72, zt + 1.8),
                                                   (0.02, zt + 1.8)], OBS)
    pts = [(-(DW + 1.2), zt + 1.8)] + ogive2(0.0, DW + 1.2, 8.6, zt + 1.8, 8) + [(DW + 1.2, zt + 1.8)]
    moldW(mb, W, pts, 0.15, PROF_DOOR, CAPL)
    inner = ogive2(0.0, DW + 2.2, 8.6, zt + 1.8, 8)
    outer = ogive2(0.0, DW + 2.8, 9.2, zt + 1.8, 8)
    band(mb, W, inner, outer, 0.0, 0.6, VIOST)


# ================================================================== VITRAIS (lado de dentro dos vaos da casca)
G_T = -1.05


def lancet(mb, W, uc, a=WIN_A, zs=Z + WIN_SILL, zr=Z + WIN_SPRING, rise=WIN_RISE):
    """VITRAL RECUADO (lado de dentro do vao ogival de verdade da casca): vidro de luar 1,05 DENTRO do vao, chumbo,
    mainel + 2 subarcos + oculo com medalhao violeta NA MESMA PRUMADA do rendilhado de fora (sg_castle.nave_window:
    le como um rendilhado so, fundo), moldura ogival na face e peitoril em talude"""
    arc = ogive(uc, a - 0.15, zr, rise)
    panel(mb, W, [(uc - a + 0.15, zs + 0.14), (uc + a - 0.15, zs + 0.14)] + list(reversed(arc)), G_T - 0.12, G_T, MOON)
    tf = G_T + 0.03
    nz = int((zr - zs) / 5.0)
    for k in range(1, nz + 1):
        h = zs + (zr - zs) * k / (nz + 1)
        panel(mb, W, rect(uc - a, uc + a, h - 0.07, h + 0.07), tf, tf + 0.09, IRON)
    panel(mb, W, rect(uc - 0.4, uc + 0.4, zs, zr + 2.0), tf, tf + 0.5, TR)
    sub = (a - 0.4) / 2.0
    for k in (-1, 1):
        u_ = uc + k * (0.4 + sub)
        i0 = ogive(u_, sub, zr - 0.4, sub * 1.6, n=3)
        i1 = ogive(u_, sub, zr - 0.4, sub * 1.6, d=0.3, n=3)
        panel(mb, W, i0 + list(reversed(i1)), tf, tf + 0.46, TR)
    C = _P(W, uc, tf, zr + rise * 0.6)
    disc3(mb, C, U3(W), (0.0, 0.0, 1.0), N3(W), 1.56, 0.1, 0.2, VGLASS, 8)
    ring3(mb, C, U3(W), (0.0, 0.0, 1.0), N3(W), 1.55, 1.95, 0.0, 0.46, TR, 8)
    inner = [(uc - a, zs)] + ogive(uc, a, zr, rise, n=3) + [(uc + a, zs)]
    outer = [(uc - a - 0.7, zs)] + ogive(uc, a, zr, rise, d=0.7, n=3) + [(uc + a + 0.7, zs)]
    band(mb, W, inner, outer, 0.0, 0.55, TR)
    ledge(mb, W, uc - a + 0.02, uc + a - 0.02, [(G_T - 0.2, zs - 0.3), (0.0, zs - 0.3), (0.0, zs + 0.14),
                                                (G_T - 0.2, zs + 0.14)], TR)
    ledge(mb, W, uc - a - 0.95, uc + a + 0.95, [(0.02, zs - 0.45), (1.0, zs - 0.45), (1.0, zs - 0.2), (0.45, zs + 0.02),
                                                (0.02, zs + 0.02)], TR)


def blind_lancet(mb, W, uc, hw, sill, spring, rise, glass, med=False, mull=False):
    """vitral numa parede CEGA (rosacea/presbiterio): vidro 0,16 na frente da face, chumbo, mainel, oculo opcional,
    moldura funda (o recuo), capa e peitoril"""
    zs, zr = sill, spring
    arc = ogive(uc, hw, zr, rise, n=6)
    panel(mb, W, [(uc - hw, zs), (uc + hw, zs)] + list(reversed(arc)), 0.02, 0.16, glass)
    h = sill + 2.4
    while h < spring - 0.5:
        panel(mb, W, rect(uc - hw, uc + hw, h - 0.06, h + 0.06), 0.16, 0.24, IRON)
        h += 2.4
    if mull:
        panel(mb, W, rect(uc - 0.22, uc + 0.22, zs, zr + rise * 0.3), 0.14, 0.55, TR)
        sub = (hw - 0.22) / 2.0
        for k in (-1, 1):
            u_ = uc + k * (0.22 + sub)
            i0 = ogive(u_, sub - 0.22, zr - 0.2, 1.8, n=4)
            i1 = ogive(u_, sub - 0.22, zr - 0.2, 1.8, d=0.22, n=4)
            panel(mb, W, i0 + list(reversed(i1)), 0.14, 0.5, TR)
    else:
        panel(mb, W, rect(uc - 0.08, uc + 0.08, zs, zr + rise * 0.55), 0.16, 0.26, IRON)
    if med:
        C = _P(W, uc, 0.2, zr + rise * 0.42)
        disc3(mb, C, U3(W), (0.0, 0.0, 1.0), N3(W), 0.46, 0.0, 0.08, VGLASS, 12)
        ring3(mb, C, U3(W), (0.0, 0.0, 1.0), N3(W), 0.46, 0.66, 0.0, 0.3, TR, 12)
    fw = 0.55
    outer = ogive(uc, hw, zr, rise, d=fw, n=6)
    frame = [(uc - hw, zs), (uc - hw, zr)] + arc[1:-1] + [(uc + hw, zr), (uc + hw, zs), (uc + hw + fw, zs),
                                                          (uc + hw + fw, zr)] + list(reversed(outer))[1:-1] + \
        [(uc - hw - fw, zr), (uc - hw - fw, zs)]
    panel(mb, W, frame, 0.0, 0.9, TR)
    h0 = ogive(uc, hw, zr, rise, d=fw)
    h1 = ogive(uc, hw, zr, rise, d=fw + 0.36)
    panel(mb, W, h0 + list(reversed(h1)), 0.5, 1.0, OBS)
    ledge(mb, W, uc - hw - fw - 0.3, uc + hw + fw + 0.3, [(-0.1, zs - 0.42), (1.0, zs - 0.42), (1.12, zs - 0.28),
                                                          (1.12, zs), (-0.1, zs)], TR)


def windows(mb):
    for W in (W_W, W_E):
        for y in WIN_Y:
            lancet(mb, W, y)


# ================================================================== ABOBADAS: panos, nervuras, chaves
def pear(w, dep, top=0.12):
    h = w / 2.0
    return [(-h, top), (h, top), (h, -dep * 0.3), (h * 0.5, -dep * 0.8), (-h * 0.5, -dep * 0.8), (-h, -dep * 0.3)]


PROF_S = [(-0.28, 0.12), (0.28, 0.12), (0.28, -0.2), (0.0, -0.55), (-0.28, -0.2)]
PROF_F = [(-0.4, 0.12), (0.4, 0.12), (0.4, -0.75), (-0.4, -0.75)]


def rosette(mb, cx, cy, zt, R, dep, m, petals=8, n=24, flat=0.0):
    """FLORAO pendente (chave)"""
    bm = mb.bm
    k = petals / 2.0
    if flat > 0:
        rows = [(1.0, 0.0, True), (1.0, 0.14, True), (0.9, 0.45, True), (flat / R, 0.82, False), (flat / R, 1.0, False)]
    else:
        rows = [(1.0, 0.0, True), (1.0, 0.12, True), (0.8, 0.45, True), (0.55, 0.78, True)]
    rings = []
    for f, h, mod in rows:
        ring_ = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rr = R * f * ((0.72 + 0.28 * abs(math.cos(k * a))) if mod else 1.0)
            ring_.append(bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), zt - dep * h)))
        rings.append(ring_)
    fs = [bm.faces.new(rings[0])]
    for A, B in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            fs.append(bm.faces.new((A[i], A[j], B[j], B[i])))
    if flat > 0:
        fs.append(bm.faces.new(list(reversed(rings[-1]))))
        allv = [v for r_ in rings for v in r_]
    else:
        pole = bm.verts.new((cx, cy, zt - dep))
        for i in range(n):
            fs.append(bm.faces.new((rings[-1][i], rings[-1][(i + 1) % n], pole)))
        allv = [v for r_ in rings for v in r_] + [pole]
    bmesh.ops.recalc_face_normals(bm, faces=fs)
    mb._post(allv, m, None, 0, 1)


def _grid_surface(pv, xs, ys, fz, m):
    bm = pv.bm
    G = [[bm.verts.new((x, y, Z + fz(x, y))) for x in xs] for y in ys]
    fs = []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            fs.append(bm.faces.new((G[j][i], G[j + 1][i], G[j + 1][i + 1], G[j][i + 1])))
    pv._post([v for r in G for v in r], m, None, 0, 1)
    return G


def _vault_ys(per=3.0):
    ys = []
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        ny = max(4, 2 * int(round((yb - ya) / (2.0 * per))))
        ys += [ya + (yb - ya) * k / ny for k in range(ny)]
    ys.append(VAULT_Y[-1])
    return ys


def vault():
    """panos das abobadas (superficie UNICA do intradorso, normais para baixo) + linhas de fiada na nave"""
    pv = MB("SG_Hall_Vault", "03_MINING_HALL", random.Random(331), detail="near")
    bm = pv.bm
    ys = _vault_ys(4.2)
    K = 9
    half = [NHW * math.sin(0.5 * math.pi * k / K) for k in range(K + 1)]
    xs = sorted(set([-v for v in half] + half))
    _grid_surface(pv, xs, ys, zv, VA)
    for s in (-1, 1):
        axs = sorted(s * (AIN + 4.0 * k) for k in range(7))
        _grid_surface(pv, axs, ys, za, VA)
    # linhas de fiada da nave (faixas ao longo de y nas linhas pares da grade, 0,03 abaixo do pano)
    jv = []
    for i, x in enumerate(xs):
        if i % 3 or abs(x) < 1.0 or abs(x) > NHW - 3.0:
            continue
        xa, xb = x - 0.08, x + 0.08
        A = [bm.verts.new((xa, y, Z + zv(xa, y) - 0.14)) for y in ys]
        B = [bm.verts.new((xb, y, Z + zv(xb, y) - 0.14)) for y in ys]
        for j in range(len(ys) - 1):
            bm.faces.new((A[j], A[j + 1], B[j + 1], B[j]))
        jv += A + B
    pv._post(jv, VJ, None, 0, 1)
    # presbiterio: canhao ogival com o perfil da ordem externa do arco triunfal
    cxs = [20.0 * (-1.0 + 2.0 * k / 16) for k in range(17)]
    cys = [CH_Y0 + (RY0 - CH_Y0) * k / 6.0 for k in range(7)]
    _grid_surface(pv, cxs, cys, lambda x, y: chancel_z(x) - (Z - Z), VA)
    for f in bm.faces:
        f.normal_update()
        if f.normal.z > 0:
            f.normal_flip()
    finish(pv, recalc=False)


def chancel_z(x):
    """intradorso da abobada do presbiterio (acima do piso da NAVE) = ordem externa do arco triunfal"""
    return TRI_SPRING + ogive_zk(TRI_HW, TRI_RISE, min(abs(x), TRI_HW + TRI_O), TRI_O)


def ribs():
    mb = MB("SG_Hall_Ribs", "03_MINING_HALL", random.Random(333), detail="near")
    prof = pear(1.1, 1.0)
    prof_w = pear(0.8, 0.8)

    def rib(pts2, pr, m, fz):
        mb.sweep([(x, y, Z + fz(x, y) - 0.02) for x, y in pts2], pr, m)
    # NAVE: arcos transversais nas linhas dos pilares, diagonais por tramo, cumeeira, formeiros na arcada
    x_end = NHW - 0.3
    tx = sorted(set([x_end * math.sin(0.5 * math.pi * k / 5) for k in range(6)] +
                    [-x_end * math.sin(0.5 * math.pi * k / 5) for k in range(6)]))
    for y in VAULT_Y:
        yy = min(max(y, Y0 + 0.55), Y1 - 0.55)
        rib([(x, yy) for x in tx], prof if Y0 < y < Y1 else prof_w, OBS, zv)
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if yb - ya < 15.0:
            continue
        ya2, yb2 = max(ya, Y0 + 0.55), min(yb, Y1 - 0.55)
        for s in (1, -1):
            pts = [((-x_end + 2 * x_end * k / 6.0) * s, ya2 + (yb2 - ya2) * k / 6.0) for k in range(7)]
            rib(pts, PROF_S, SILVER, zv)
    rib([(0.0, Y0 + 0.55 + (Y1 - Y0 - 1.1) * k / 18.0) for k in range(19)], PROF_S, SILVER, zv)
    ys = _vault_ys(5.0)
    for s in (-1, 1):
        rib([(s * (NHW - 0.42), y) for y in ys], PROF_F, OBS, zv)
    # NAVES LATERAIS: transversais, diagonais e formeiro da parede externa
    for s in (-1, 1):
        axs = [s * (AIN + 0.4 + (X1 - AIN - 0.8) * k / 6.0) for k in range(7)]
        for y in VAULT_Y:
            yy = min(max(y, Y0 + 0.55), Y1 - 0.55)
            rib([(x, yy) for x in axs], PROF_S, OBS, za)
        for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
            if yb - ya < 15.0:
                continue
            ya2, yb2 = max(ya, Y0 + 0.55), min(yb, Y1 - 0.55)
            for q in (0, 1):
                pts = []
                for k in range(5):
                    t = k / 4.0
                    xx = AIN + 0.5 + (X1 - AIN - 1.0) * (t if q == 0 else 1.0 - t)
                    pts.append((s * xx, ya2 + (yb2 - ya2) * t))
                rib(pts, PROF_S, SILVER, za)
    # CHAVES: florao nas linhas dos pilares (o EMBLEMA so na chave do meio, sobre o medalhao), florao pequeno nos
    # meios de tramo; nas naves laterais, florao pequeno no meio de cada tramo
    for y in AY:
        zt = Z + zv(0.0, y) + 0.05
        rosette(mb, 0.0, y, zt, 2.6, 1.5, OBS, n=16)
        EM._lathe(mb, (0.0, y, zt - 1.85), [(0.0, 0.0), (0.24, 0.1), (0.29, 0.26), (0.17, 0.42)], SILVER, 8,
                  caps=(False, True))
    for ya, yb in zip(VAULT_Y, VAULT_Y[1:]):
        if yb - ya < 15.0:
            continue
        y = (ya + yb) / 2.0
        zt = Z + zv(0.0, y) + 0.05
        if abs(y - EMB_C[1]) < 0.1:
            rosette(mb, 0.0, y, zt, 3.2, 1.6, OBS, n=16, flat=2.0)
            EM.emblem_flat(mb, mb, mb, (0.0, y, zt - 1.72), math.pi / 2, 1.75, monumental=False, up=-1, glow=VSOFT,
                           field=False, seg=16)
            continue
        for s in (-1, 1):
            zt2 = Z + za(s * ACX, y) + 0.05
            rosette(mb, s * ACX, y, zt2, 1.3, 0.9, OBS, n=8, petals=4)
    # PRESBITERIO: transversais, diagonais, cumeeira de prata e florao no fecho
    ce = 19.4
    cxs = [ce * (-1.0 + 2.0 * k / 14) for k in range(15)]
    for yy in (CH_Y0 + 0.5, (CH_Y0 + RY0) / 2.0, RY0 - 0.6):
        rib([(x, yy) for x in cxs], pear(0.9, 0.8), OBS, lambda x, y: chancel_z(x))
    for s in (-1, 1):
        pts = [(s * (-ce + 2 * ce * k / 12.0), CH_Y0 + 0.5 + (RY0 - 0.6 - CH_Y0 - 0.5) * k / 12.0) for k in range(13)]
        rib(pts, PROF_S, SILVER, lambda x, y: chancel_z(x))
    rib([(0.0, CH_Y0 + 0.5 + (RY0 - CH_Y0 - 1.1) * k / 6.0) for k in range(7)], PROF_S, SILVER,
        lambda x, y: chancel_z(x))
    zt = Z + chancel_z(0.0) + 0.05
    rosette(mb, 0.0, (CH_Y0 + RY0) / 2.0, zt, 2.2, 1.3, OBS, n=16)
    EM._lathe(mb, (0.0, (CH_Y0 + RY0) / 2.0, zt - 1.62), [(0.0, 0.0), (0.2, 0.08), (0.24, 0.22), (0.14, 0.36)],
              SILVER, 8, caps=(False, True))
    finish(mb)


# ================================================================== ARCO TRIUNFAL + rosacea (parede norte)
TRI_OUT_PIER = TRI_HW + TRI_O                    # 20: face da ordem externa
TPS = TRI_OUT_PIER + 2.6                         # eixo dos pilares compostos do arco (plinto 20,1 .. 25,1)


def tri_pts(off, legs=True, n=8):
    arc = ogive(0.0, TRI_HW, Z + TRI_SPRING, TRI_RISE, d=off, n=n)
    if not legs:
        return arc
    return [(arc[0][0], CZ)] + arc + [(arc[-1][0], CZ)]


def triumph(mb):
    """ARCO TRIUNFAL de 3 ORDENS escalonadas na espessura da parede (remate / pedra violeta / obsidiana, toro na aresta
    de cada ordem), pilares compostos com PINACULO, capa de obsidiana na face da nave"""
    W = W_N
    tw = L.HALL_WALL
    mats = (CAPL, VIOST, OBS)
    roll = [(0.22 * math.cos(2 * math.pi * i / 6), 0.22 * math.sin(2 * math.pi * i / 6)) for i in range(6)]
    step = TRI_O / TRI_N
    for k in range(TRI_N):
        off = k * step
        t0 = -tw + k * tw / TRI_N
        t1 = -tw + (k + 1) * tw / TRI_N + (0.35 if k == TRI_N - 1 else 0.0)
        band(mb, W, tri_pts(off), tri_pts(TRI_O - 0.01), t0, t1, mats[k])
        path = [_P(W, u, t1 + 0.02, z) for u, z in tri_pts(off - 0.12, legs=False)]
        mb.sweep(path, roll, CAPL, True, None, up=N3(W))
        for sg in (-1, 1):
            wcol("SG_HallAltar", W, sg * (TRI_HW + off), sg * (TRI_OUT_PIER + 0.02), t0, t1, CZ - 0.5, Z + TRI_SPRING)
    band(mb, W, tri_pts(TRI_O, legs=False), tri_pts(TRI_O + 0.75, legs=False), 0.0, 0.6, OBS)
    for k in (-1, 1):
        s = k * TPS
        respond(mb, W, s, 1.7, 1.5, 2.5, 2.3, Z + TRI_SPRING, [(0.0, 1.6, 0.8), (-1.85, 0.75, 0.5), (1.85, 0.75, 0.5)])
        wcol("SG_HallAltar", W, s - 2.5, s + 2.5, 0.0, 2.3, Z - 0.5, Z + TRI_SPRING)
        c = _P(W, s + k * 0.4, 1.3, Z + TRI_SPRING)
        pinnacle(mb, c[0], c[1], c[2], s=1.15, hb=3.6, hn=6.4, body_m=CS, spire_m=CS, cap_m=OBS)


def rose(mb, mw):
    """ROSACEA DA LUA acima do arco triunfal (vidro violeta, 12 raios, anel interno, moldura de 2 aneis) com o EMBLEMA
    da ordem na frente, e 2 lancetas de luar ao lado"""
    W = W_N
    C = _P(W, 0.0, 0.0, Z + ROSE_Z)
    U, V, N_ = U3(W), (0.0, 0.0, 1.0), N3(W)
    disc3(mw, C, U, V, N_, ROSE_R, 0.02, 0.18, VGLASS, 24)
    ring3(mw, C, U, V, N_, ROSE_R - 0.05, ROSE_R + 0.9, 0.0, 0.95, TR, 24)
    ring3(mw, C, U, V, N_, ROSE_R + 0.9, ROSE_R + 1.6, 0.0, 0.65, OBS, 24)
    ring3(mw, C, U, V, N_, 5.1, 5.5, 0.18, 0.55, TR, 12)
    for k in range(12):
        a = 2 * math.pi * k / 12 + math.pi / 12
        p0 = _P(W, 5.3 * math.cos(a), 0.36, Z + ROSE_Z + 5.3 * math.sin(a))
        p1 = _P(W, (ROSE_R - 0.02) * math.cos(a), 0.36, Z + ROSE_Z + (ROSE_R - 0.02) * math.sin(a))
        mw.beam(p0, p1, 0.3, 0.34, TR, 0.0)
    EM.emblem(mw, mw, mw, _P(W, 0.0, 0.62, Z + ROSE_Z), -math.pi / 2, 4.7, depth=0.8, monumental=True, glow=VGLOW)
    for k in (-1, 1):
        blind_lancet(mw, W, k * 17.5, 2.4, Z + 64.0, Z + 74.0, 5.0, MOON, med=True)


# ================================================================== PRESBITERIO (paredes, retabulo, arco secreto)
SA_HW = L.SECRET_ARCH[0] / 2.0 - 0.15            # 5,85: vao do arco secreto (0,15 dentro do vao da casca)
SA_SPRING = 10.0
SA_RISE = L.SECRET_ARCH[1] - SA_SPRING - 0.15    # apice +17,85
RET_T = 0.4                                      # espessura do revestimento do retabulo (face em 299,6)
RET_TOP = 21.0                                   # cornija do retabulo (acima do trono: 20)
P_J = 1.4                                        # ombreira do bolso


def chancel(mb, iw):
    """paredes do presbiterio: silhar ate o cordao, BOLSO do trono emoldurado (leste) e NICHO CEGO simetrico (oeste),
    colunelos de canto (os do fundo nascem em misula acima do trono), lancetas cegas, estandartes, RETABULO com o ARCO
    SECRETO em cantaria, forro do vao e o VITRAL DE LUAR acima do trono"""
    py0, py1 = POCKET[1], POCKET[3]
    ph = POCKET[5] - CZ                          # 22
    for W, sx in ((W_CW, -1), (W_CE, 1)):
        sa, sb = CH_Y0 + 0.3, py0 - P_J
        wall_run(mb, W, sa, sb, CZ + 0.9, CZ + ACORD + 1.2, 0.0, PF, [], CS)
        ashlar(mb, WT(W, PF), sa, sb, CZ + 1.0, CZ + ACORD - 0.34, (), PL=3.4, phase=0.6)
        ledge(mb, WT(W, PF), sa, sb, drip(CZ + ACORD, 0.36, 0.5), OBS)
        ledge(mb, W, sa, sb, plinth(CZ - 0.05, CZ + 0.95, PF + 0.3, PF + 0.12), OBS)
        ledge(mb, W, sa, sb, [(-0.1, CZ + ACORD + 1.2), (PF + 0.1, CZ + ACORD + 1.2), (PF + 0.1, CZ + ACORD + 1.45),
                              (-0.1, CZ + ACORD + 1.45)], CAPL)
        wcol("SG_HallChancel", W, sa, sb, 0.0, PF, CZ - 0.5, CZ + 10.0)
        # moldura do BOLSO (leste) / do NICHO CEGO (oeste): ombreira sul, verga e arco de descarga
        wbox(mb, W, py0 - P_J, py0, 0.0, PF + 0.4, CZ, CZ + ph, CAPL, 0.06)
        wcol("SG_HallChancel", W, py0 - P_J, py0, 0.0, PF + 0.4, CZ - 0.5, CZ + ph)
        ledge(mb, W, py0 - P_J - 0.2, RY0 - RET_T - 0.02, [(0.02, CZ + ph), (PF + 0.55, CZ + ph),
                                                           (PF + 0.55, CZ + ph + 0.3), (PF + 0.3, CZ + ph + 0.5),
                                                           (PF + 0.3, CZ + ph + 1.3), (PF + 0.6, CZ + ph + 1.55),
                                                           (PF + 0.6, CZ + ph + 1.85), (0.02, CZ + ph + 1.85)], OBS)
        uc = (py0 - P_J + RY0 - RET_T) / 2.0
        hw_ = (RY0 - RET_T - py0 + P_J) / 2.0 - 0.3
        zr = CZ + ph + 1.85
        band(mb, W, ogive(uc, hw_ - 0.6, zr, 5.6, n=6), ogive(uc, hw_ - 0.6, zr, 5.6, d=0.7, n=6), 0.0, 0.55, VIOST)
        panel(mb, W, [(uc - hw_ + 0.6, zr), (uc + hw_ - 0.6, zr)] + list(reversed(ogive(uc, hw_ - 0.6, zr, 5.6, n=6))),
              0.02, 0.2, NI)
        if sx < 0:
            # oeste: nicho cego (fundo escuro), espelho do bolso
            panel(mb, W, rect(py0, RY0 - RET_T, CZ + 0.02, CZ + ph), 0.02, 0.18, NI)
        # lanceta cega + estandarte no pano entre o arco triunfal e a moldura do bolso
        yc = (sa + sb) / 2.0
        if True:
            yaw = 0.0 if sx < 0 else math.pi
            EM.banner(mb, mb, mb, mb, (sx * (20.0 - 1.6), yc, CZ + 17.0), yaw, 3.2, 12.0)
            for dy in (-1.8, 1.8):
                mb.rod((sx * 20.0, yc + dy, CZ + 16.8), (sx * 18.4, yc + dy, CZ + 16.8), 0.1, IRON, 6)
    # colunelos de canto: os do sul do chao ate a nascenca; os do fundo nascem numa MISULA acima do trono
    for sx in (-1, 1):
        for cy_, z0 in ((CH_Y0 + 0.75, CZ), (RY0 - RET_T - 0.75, Z + TRI_SPRING - 1.1)):
            cx = sx * (20.0 - 0.75)
            if z0 > CZ:
                W = W_CW if sx < 0 else W_CE
                ledge(mb, W, cy_ - 0.75, cy_ + 0.75, [(-0.1, z0 - 1.6)] + s_curve(0.1, 1.35, z0 - 1.6, z0 - 0.05, 4) +
                      [(1.35, z0), (-0.1, z0)], CAPL)
            else:
                EM._lathe(mb, (cx, cy_, z0), [(0.72, 0.0), (0.72, 0.2), (0.6, 0.32), (0.66, 0.46), (0.52, 0.6),
                                              (0.47, 0.66)], CAPL, 8, math.pi / 8, caps=(False, True))
            zt = Z + TRI_SPRING - 1.1
            if zt - z0 > 1.0:
                mb.cyl(0.47, zt - z0 - 0.66, (cx, cy_, (z0 + 0.66 + zt) / 2.0), m=MARBLE, n=8, bevel=0.0, caps=False,
                       rot=(0, 0, math.pi / 8))
            EM._lathe(mb, (cx, cy_, zt), [(0.47, 0.0), (0.58, 0.08), (0.5, 0.18), (0.56, 0.42), (0.8, 0.8),
                                          (0.88, 0.95), (0.88, 1.1), (0.0, 1.1)], CAPL, 8, math.pi / 8,
                      caps=(False, False))
    retable(mb)
    for k in (-1, 1):
        torchere(iw, k * 10.6, TH_FRONT - 3.4, CZ)
        col_box2("SG_HallChancel", (k * 10.6 - 0.6, TH_FRONT - 4.0, CZ - 0.5), (k * 10.6 + 0.6, TH_FRONT - 2.8, CZ + 6.0))


def retable(mb):
    """RETABULO: revestimento de 0,4 no muro (face em 299,6) com silhar raso, ARCO SECRETO de cantaria (ombreiras em
    fiadas alternadas e aduelas, relevo <= 0,12: o trono passa 0,28 na frente), forro do vao ate o poco, cornija acima
    do trono e o VITRAL DE LUAR (contraluz do trono)"""
    W = W_R
    zs, zr = CZ, CZ + SA_SPRING
    wall_run(mb, W, CX0 + PF, CX1 - PF, CZ + 0.02, CZ + RET_TOP, 0.0, RET_T, [(0.0, SA_HW, zs, zr, SA_RISE)], CS)
    fr = 1.45                                    # largura da moldura de cantaria
    excl = [(-SA_HW - fr - 0.05, SA_HW + fr + 0.05, CZ, CZ + 30.0)]
    ashlar(mb, WT(W, RET_T), CX0 + PF, CX1 - PF, CZ + 0.3, CZ + ACORD - 0.34, excl, PL=3.4, dep=0.1, phase=0.4)
    WF = WT(W, RET_T)
    # ombreiras: pedras alternadas longa/curta (le a cantaria sem textura)
    zz, k = zs + 0.05, 0
    hs = (1.5, 1.1)
    while zz < zr - 0.3:
        h = min(hs[k % 2], zr - zz)
        w = fr if k % 2 == 0 else fr * 0.62
        for sg in (-1, 1):
            a, b = sorted((sg * SA_HW, sg * (SA_HW + w)))
            block(mb, WF, a + 0.03, b - 0.03, zz + 0.04, zz + h - 0.04, -0.03, 0.11, 0.06, TR, back=False)
        zz += h
        k += 1
    # aduelas (radiais) + fecho
    inner = ogive(0.0, SA_HW, zr, SA_RISE, n=10)
    outer = ogive(0.0, SA_HW, zr, SA_RISE, d=fr, n=10)
    for i in range(len(inner) - 1):
        q = [inner[i], inner[i + 1], outer[i + 1], outer[i]]
        mid_u = sum(p[0] for p in q) / 4.0
        mid_z = sum(p[1] for p in q) / 4.0
        sh = [(mid_u + (u - mid_u) * 0.94, mid_z + (z - mid_z) * 0.94) for u, z in q]
        panel(mb, WF, sh, -0.03, 0.11, TR if i != len(inner) // 2 - 1 and i != len(inner) // 2 else OBS)
    # forro do vao (ombreiras e intradorso) ate a face do poco
    depth = RY1 - RY0
    for sg in (-1, 1):
        a, b = sorted((sg * SA_HW, sg * (SA_HW + 0.13)))
        panel(mb, W, rect(a, b, CZ + 0.02, zr), -depth + 0.02, 0.0, CS)
    band(mb, W, ogive(0.0, SA_HW, zr, SA_RISE, n=10), ogive(0.0, SA_HW, zr, SA_RISE, d=0.13, n=10), -depth + 0.02, 0.0,
         CS)
    # cordao do retabulo (morre na moldura) e a CORNIJA acima do trono
    for a, b in ((CX0 + PF, -SA_HW - fr - 0.05), (SA_HW + fr + 0.05, CX1 - PF)):
        ledge(mb, WF, a, b, drip(CZ + ACORD, 0.1, 0.4, back=-0.05), OBS)
    zt = CZ + RET_TOP
    ledge(mb, W, CX0 + PF, CX1 - PF, [(-0.1, zt - 0.02), (RET_T + 0.3, zt - 0.02), (RET_T + 0.3, zt + 0.25),
                                      (RET_T + 0.1, zt + 0.42), (RET_T + 0.1, zt + 0.95), (RET_T + 0.5, zt + 1.2),
                                      (RET_T + 0.5, zt + 1.55), (-0.1, zt + 1.55)], OBS)
    ledge(mb, W, CX0 + PF, CX1 - PF, [(RET_T + 0.1, zt + 0.5), (RET_T + 0.18, zt + 0.5), (RET_T + 0.18, zt + 0.86),
                                      (RET_T + 0.1, zt + 0.86)], SILVER)
    blind_lancet(mb, W, 0.0, 4.4, CZ + 24.5, CZ + 41.0, 7.0, MOON, mull=True)


def torchere(mb, x, y, z, s=1.3):
    """TOCHEIRO de ferro (tripe, fuste de torno, prato e 3 velas)"""
    for k in range(3):
        a = 2 * math.pi * k / 3 + math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        mb.tube([(x + ca * 0.9 * s, y + sa * 0.9 * s, z + 0.05 * s), (x + ca * 0.75 * s, y + sa * 0.75 * s, z + 0.35 * s),
                 (x + ca * 0.3 * s, y + sa * 0.3 * s, z + 0.7 * s), (x, y, z + 0.95 * s)], 0.08 * s, IRONL, 5)
        EM._lathe(mb, (x + ca * 0.9 * s, y + sa * 0.9 * s, z), [(0.16 * s, 0.0), (0.2 * s, 0.06 * s), (0.0, 0.12 * s)],
                  IRONL, 6, caps=(True, False))
    EM._lathe(mb, (x, y, z + 0.8 * s), [(r * s, h * s) for r, h in ((0.0, 0.0), (0.22, 0.1), (0.16, 0.3), (0.1, 0.4),
                                                                    (0.1, 3.6), (0.2, 3.72), (0.12, 3.84), (0.1, 4.6),
                                                                    (0.24, 4.72), (0.1, 4.86), (0.1, 5.0))], IRON, 6,
              caps=(False, True))
    zt = z + 5.8 * s
    EM._lathe(mb, (x, y, zt - 0.1 * s), [(r * s, h * s) for r, h in ((0.1, 0.0), (0.62, 0.12), (0.66, 0.2), (0.58, 0.2),
                                                                     (0.0, 0.16))], IRONL, 8, caps=(True, False))
    for dx, hc in ((-0.3, 0.7), (0.3, 0.7), (0.0, 1.0)):
        candle(mb, x + dx * s, y, zt + 0.06 * s, hc * s, 1.15 * s, dish=False)


# ================================================================== TRONO MOVEL (objeto separado)
def throne():
    """TRONO DE SHADOW (catedra gotica aprovada no 04c, crescente sem espada) na escala 1,22, sobre um SOCO de 2 degraus
    e com o ESPALDAR-RETABULO (13,8 x 19) que TAPA o arco secreto. Tudo num objeto so, 'SG_Hall_ThroneMov' (o export
    faz um Model proprio; o TronoService desliza o Model + COL_SGHallThroneMov_* 27,5 em +X ate o bolso)."""
    mb = MB("SG_Hall_ThroneMov", "03_MINING_HALL", random.Random(341), detail="hero")
    chair(mb)
    # a cadeira foi feita no referencial do 04c (costas em d = 0, frente para -y, base z = 0): escala e leva ao lugar
    zb = CZ + SOCO_H
    for v in mb.bm.verts:
        v.co.x, v.co.y, v.co.z = v.co.x * TH_S, TH_Y + v.co.y * TH_S, zb + v.co.z * TH_S
    # SOCO de 2 degraus (marmore negro com focinho de obsidiana e filete de prata)
    x0, x1 = -L.THRONE_SIZE[0] / 2.0, L.THRONE_SIZE[0] / 2.0
    y0, y1 = TH_FRONT, TH_BACK
    z0 = CZ
    for i, (h, ins, dy) in enumerate(((SOCO[0], 0.0, 0.0), (SOCO[1], 1.2, 1.1))):
        a, b, c = x0 + ins, x1 - ins, y0 + dy
        mb.box2((a, c + 0.14, z0), (b, y1, z0 + h - 0.14), MARBLE, 0.02)
        mb.box2((a - 0.05, c - 0.05, z0 + h - 0.14), (b + 0.05, y1, z0 + h), OBS, 0.05)
        mb.box2((a + 0.05, c + 0.08, z0 + h - 0.22), (b - 0.05, c + 0.2, z0 + h - 0.16), SILVER, 0.0)
        z0 += h
    # ESPALDAR-RETABULO: bloco de marmore negro com paineis nas laterais, pano azul-noite com debrum de prata na
    # frente (atras da cadeira), cornija de obsidiana e crista ogival de prata no eixo
    bx = TH_HW
    by0, by1 = TH_Y + 0.3, TH_BACK
    zt = CZ + SOCO_H + 18.3
    mb.box2((-bx, by0, zb), (bx, by1, zt), MARBLE, 0.05)
    Wf = ((0.0, by0), (1.0, 0.0), (0.0, -1.0))
    panel(mb, Wf, rect(-bx + 1.15, bx - 1.15, zb + 0.4, zt - 1.3), 0.0, 0.1, NAVYC)
    for r_ in (rect(-bx + 1.0, bx - 1.0, zb + 0.25, zb + 0.4), rect(-bx + 1.0, bx - 1.0, zt - 1.3, zt - 1.15),
               rect(-bx + 1.0, -bx + 1.15, zb + 0.25, zt - 1.15), rect(bx - 1.15, bx - 1.0, zb + 0.25, zt - 1.15)):
        panel(mb, Wf, r_, 0.0, 0.16, SILVER)
    for sg in (-1, 1):
        Ws = ((sg * bx, 0.0), (0.0, 1.0), (sg * 1.0, 0.0))
        for z_a, z_b in ((zb + 1.0, zb + 8.0), (zb + 9.0, zt - 1.6)):
            panel(mb, Ws, rect(by0 + 0.5, by1 - 0.5, z_a, z_b), -0.02, 0.1, OBS)
    ledge(mb, Wf, -bx - 0.1, bx + 0.1, [(0.0, zt), (0.0, zt + 0.1), (0.35, zt + 0.1), (0.35, zt + 0.3), (0.15, zt + 0.45),
                                        (0.15, zt + 0.7), (0.0, zt + 0.7)], OBS)
    mb.box2((-bx - 0.1, by0 - 0.05, zt + 0.7), (bx + 0.1, by1, zt + 0.82), SILVER, 0.0)
    ob = finish(mb)
    # colisao propria (move junto): soco, cadeira ate o apoio dos bracos, espaldar ate o topo
    w2 = L.THRONE_SIZE[0] / 2.0
    col_box2("SGHallThroneMov", (-w2, TH_FRONT, CZ), (w2, TH_BACK, CZ + SOCO_H))
    col_box2("SGHallThroneMov", (-3.9 * TH_S, TH_Y - 4.55 * TH_S, CZ + SOCO_H), (3.9 * TH_S, TH_Y, CZ + SOCO_H + 4.1 * TH_S))
    col_box2("SGHallThroneMov", (-bx, TH_Y - 1.2 * TH_S, CZ + SOCO_H), (bx, TH_BACK, CZ + SOCO_H + 18.3))
    return ob


def chair(mb):
    """a CATEDRA do 04c, no referencial local (costas em y = 0, frente para -y, base em z = 0; escala 1)"""
    W = ((0.0, 0.0), (1.0, 0.0), (0.0, -1.0))                  # u = x, t = d (para a nave)
    b = 0.0

    def P(u, d, h):
        return _P(W, u, d, b + h)

    SH, CU = 2.8, 0.55
    BT = SH - CU
    SW = 2.3
    DC = 0.92
    DF = 4.5
    DS, DR = 4.35, 4.17
    AW0, AW1 = 2.35, 3.15
    MU0, MU1 = 3.05, 3.8
    LG = 2.75
    LD = 4.15
    PT = 10.2
    AH = SH + 1.3
    SPB, RB = 8.6, 2.3
    WS = {1: ((0.0, 0.0), (0.0, -1.0), (1.0, 0.0)), -1: ((0.0, 0.0), (0.0, -1.0), (-1.0, 0.0))}

    def uloft(secs, m):
        bm = mb.bm
        rows = [[bm.verts.new(P(u, d, h)) for d, h in prof] for u, prof in secs]
        n = len(secs[0][1])
        for A, B in zip(rows, rows[1:]):
            for i in range(n):
                j = (i + 1) % n
                bm.faces.new((A[i], A[j], B[j], B[i]))
        bm.faces.new(rows[0])
        bm.faces.new(list(reversed(rows[-1])))
        mb._post([v for r in rows for v in r], m, None, 0, 1)

    def uribbon(u0, u1, inner, outer, m):
        bm = mb.bm
        n = len(inner)
        iA = [bm.verts.new(P(u0, d, h)) for d, h in inner]
        oA = [bm.verts.new(P(u0, d, h)) for d, h in outer]
        iB = [bm.verts.new(P(u1, d, h)) for d, h in inner]
        oB = [bm.verts.new(P(u1, d, h)) for d, h in outer]
        for i in range(n - 1):
            j = i + 1
            bm.faces.new((oA[i], oA[j], iA[j], iA[i]))
            bm.faces.new((iB[i], iB[j], oB[j], oB[i]))
            bm.faces.new((oA[i], oB[i], oB[j], oA[j]))
            bm.faces.new((iA[i], iA[j], iB[j], iB[i]))
        for k in (0, n - 1):
            bm.faces.new((iA[k], oA[k], oB[k], iB[k]))
        mb._post(iA + oA + iB + oB, m, None, 0, 1)

    def tufted(u0, u1, h0, h1, nx, ny, dlo, dhi, dbk, m):
        bm = mb.bm
        G, UH = {}, {}
        for i in range(nx + 1):
            for j in range(ny + 1):
                u, h = u0 + (u1 - u0) * i / nx, h0 + (h1 - h0) * j / ny
                UH[i, j] = (u, h)
                G[i, j] = bm.verts.new(P(u, dhi if (i + j) % 2 else dlo, h))
        for i in range(nx):
            for j in range(ny):
                a, c1, c2, e = G[i, j], G[i + 1, j], G[i + 1, j + 1], G[i, j + 1]
                if (i + j) % 2 == 0:
                    bm.faces.new((a, c1, c2))
                    bm.faces.new((a, c2, e))
                else:
                    bm.faces.new((a, c1, e))
                    bm.faces.new((c1, c2, e))
        C = [bm.verts.new(P(UH[k][0], dbk, UH[k][1])) for k in ((0, 0), (nx, 0), (nx, ny), (0, ny))]
        edges = [[G[i, 0] for i in range(nx + 1)], [G[nx, j] for j in range(ny + 1)],
                 [G[i, ny] for i in range(nx, -1, -1)], [G[0, j] for j in range(ny, -1, -1)]]
        for q, e_ in enumerate(edges):
            bm.faces.new(e_ + [C[(q + 1) % 4], C[q]])
        bm.faces.new(list(reversed(C)))
        mb._post(list(G.values()) + C, m, None, 0, 1)

    # ---------------- BASE: caixa macica de marmore negro
    mb.box2(P(-MU0, 0.3, 0.45), P(MU0, DR, BT - 0.02), MARBLE, 0.0)
    rod = [(0.3, 0.0), (4.5, 0.0), (4.5, 0.1), (4.44, 0.15), (4.47, 0.24), (4.41, 0.33), (4.36, 0.4), (4.36, 0.5),
           (0.3, 0.5)]
    ledge(mb, W, -(LG - 0.3), LG - 0.3, [(d, h) for d, h in rod], MARBLE)
    rods = [(2.8, 0.0), (3.2, 0.0), (3.2, 0.1), (3.14, 0.15), (3.17, 0.24), (3.11, 0.33), (3.07, 0.4), (3.07, 0.5),
            (2.8, 0.5)]
    for k in (-1, 1):
        ledge(mb, WS[k], 1.1, LD - 0.3, [(t, h) for t, h in rods], MARBLE)
        panel(mb, WS[k], rect(1.45, 3.45, 0.8, 1.9), MU0 - 0.01, MU0 + 0.1, OBS)
        for r_ in (rect(1.39, 3.51, 0.74, 0.8), rect(1.39, 3.51, 1.9, 1.96), rect(1.39, 1.45, 0.8, 1.9),
                   rect(3.45, 3.51, 0.8, 1.9)):
            panel(mb, WS[k], r_, MU0 - 0.01, MU0 + 0.2, SILVER)
        panel(mb, WS[k], rect(1.0, LD - 0.3, BT - 0.1, BT - 0.02), MU0 - 0.02, MU0 + 0.1, SILVER)
    AC, AO, ASP, ARS = (-1.5, 0.0, 1.5), 0.45, 1.1, 0.52
    TOPA = BT - 0.35
    for u0, u1 in ((-(LG - 0.3), -1.95), (-1.05, -AO), (AO, 1.05), (1.95, LG - 0.3)):
        mb.box2(P(u0, DR - 0.02, 0.45), P(u1, DS, TOPA), MARBLE, 0.0)
    mb.box2(P(-(LG - 0.3), DR - 0.02, TOPA), P(LG - 0.3, DS, BT - 0.02), MARBLE, 0.0)
    for uc in AC:
        inner = ogive2(uc, AO, ARS, ASP, 3)
        band(mb, W, [(s, b + h) for s, h in inner], [(s, b + TOPA) for s, _ in inner], DR - 0.02, DS, MARBLE)
        mb.box2(P(uc - AO, DR - 0.03, 0.45), P(uc + AO, DR + 0.11, TOPA - 0.05), OBS, 0.0)
        bead = [(uc - AO - 0.035, 0.5)] + ogive2(uc, AO + 0.035, ARS + 0.035, ASP, 3) + [(uc + AO + 0.035, 0.5)]
        mb.tube([P(s, DS + 0.015, h) for s, h in bead], 0.035, SILVER, 4)
    for k in (-1, 1):
        c = P(k * 0.75, DS + 0.07, 0.45)
        EM._lathe(mb, c, [(0.16, 0.0), (0.1, 0.12), (0.09, 0.56), (0.17, 0.68), (0.0, 0.68)], OBS, 6)

    # ---------------- ALMOFADA e QUEDA DE PANO
    def cp(e):
        return [(0.62, BT + e), (4.3 - e, BT + e), (4.42 - e, BT + 0.07 + e * 0.6), (DF - e, BT + 0.2),
                (DF - e, BT + 0.34), (4.44 - e, BT + 0.46 - e * 0.3), (4.3 - e, SH - 0.01 - e), (2.6, SH + 0.03 - e),
                (DC + 0.03, SH - e), (0.7, SH - 0.12 - e)]
    uloft([(-SW, cp(0.1)), (-SW + 0.14, cp(0.0)), (SW - 0.14, cp(0.0)), (SW, cp(0.1))], CLOTH)
    us = [-2.3, -1.95, -1.5, -1.05, -0.45, 0.0, 0.45, 1.05, 1.5, 1.95, 2.3]
    hh = [TOPA + 0.01 - (0.15 if abs(abs(u) - 1.5) < 1e-6 or abs(u) < 1e-6 else 0.0) for u in us]
    panel(mb, W, [(-SW, b + BT + 0.12), (SW, b + BT + 0.12)] + [(u, b + h) for u, h in zip(us[::-1], hh[::-1])],
          4.43, 4.52, CLOTH)
    mb.tube([P(u, 4.535, h) for u, h in zip(us, hh)], 0.04, SILVER, 4)
    # ---------------- PERNAS da frente: garra, perna, balaustre
    for k in (-1, 1):
        a0, a1 = sorted((k * (LG - 0.3), k * (LG + 0.3)))
        wprism(mb, W, rect_ut(a0, a1, LD - 0.3, LD + 0.3, 0.08), b + 0.55, b + BT, MARBLE)
        wprism(mb, W, rect_ut(a0 - 0.05, a1 + 0.05, LD - 0.35, LD + 0.35, 0.1), b + BT - 0.14, b + BT, OBS)
        x, y, _ = P(k * LG, LD, 0.0)
        EM._lathe(mb, (x, y, b), [(0.0, 0.0), (0.24, 0.06), (0.31, 0.27), (0.22, 0.5), (0.0, 0.56)], OBS, 6)
        for a in (-30.0, 25.0, 80.0):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            dx, dy = k * sa, -ca
            mb.tube([(x + dx * r, y + dy * r, b + h) for r, h in ((0.2, 0.58), (0.36, 0.32), (0.42, 0.03))], 0.07,
                    SILVER, 4)
        EM._lathe(mb, P(k * LG, LD, BT), [(0.27, 0.0), (0.27, 0.08), (0.13, 0.2), (0.24, 0.44), (0.11, 0.7),
                                          (0.16, 0.78), (0.26, 0.86), (0.2, 0.97), (0.0, 0.97)], OBS, 6, math.pi / 6)
    # ---------------- BRACOS com VOLUTA
    dC, hC, R0, Re = 4.05, AH - 0.5, 0.55, 0.18
    th0, th1, NS = 125.0, -340.0, 17
    sp_o, sp_i, sp_b = [], [], []
    for i in range(NS + 1):
        f = i / NS
        th = math.radians(th0 + (th1 - th0) * f)
        ro = R0 - (R0 - Re) * f
        ri = ro - (0.26 - 0.15 * f)
        sp_o.append((dC + ro * math.cos(th), hC + ro * math.sin(th)))
        sp_i.append((dC + ri * math.cos(th), hC + ri * math.sin(th)))
        sp_b.append((dC + (ro - 0.06) * math.cos(th), hC + (ro - 0.06) * math.sin(th)))
    for k in (-1, 1):
        a0, a1 = sorted((k * AW0, k * AW1))
        ledge(mb, W, a0, a1, [(0.6, b + AH - 0.68), (3.75, b + AH - 0.68), (3.9, b + AH - 0.55),
                              (3.9, b + AH - 0.24), (0.6, b + AH - 0.24)], OBS)
        mb.box2(P(a0 + 0.03, 0.95, AH - 0.24), P(a1 - 0.03, 3.9, AH - 0.2), SILVER, 0.0)
        pad = [(AW0 + 0.07, AH - 0.2), (AW1 - 0.07, AH - 0.2), (AW1 - 0.07, AH - 0.1), (AW1 - 0.14, AH - 0.01),
               ((AW0 + AW1) / 2.0, AH + 0.02), (AW0 + 0.14, AH - 0.01), (AW0 + 0.07, AH - 0.1)]
        ledge(mb, WS[k], 0.97, 3.88, [(t, b + h) for t, h in pad], CLOTH)
        uribbon(a0, a1, sp_i, sp_o, OBS)
        mb.cyl(0.36, AW1 - AW0 - 0.36, P(k * (AW0 + AW1) / 2.0, dC, hC), (0, math.pi / 2, 0), m=OBS, n=10,
               bevel=0.0)
        mb.tube([P(k * (AW1 + 0.02), d, h) for d, h in sp_b[:15]], 0.04, SILVER, 4)
    # ---------------- MONTANTES com colunelo, capitel de prata e PINACULO
    for k in (-1, 1):
        a0, a1 = sorted((k * MU0, k * MU1))
        um = k * (MU0 + MU1) / 2.0
        wprism(mb, W, rect_ut(a0 - 0.1, a1 + 0.1, -0.05, 1.12, 0.12), b, b + 0.5, MARBLE)
        wloft(mb, W, rect_ut(a0 - 0.1, a1 + 0.1, -0.05, 1.12, 0.12), rect_ut(a0, a1, 0.0, 1.0, 0.14), b + 0.5, b + 0.64,
              MARBLE)
        wprism(mb, W, rect_ut(a0, a1, 0.0, 1.0, 0.14), b + 0.64, b + PT, MARBLE, 0.04)
        EM._lathe(mb, P(um, 1.02, 0.64), [(0.17, 0.0), (0.17, 0.08), (0.12, 0.16), (0.12, PT - 0.64),
                                          (0.0, PT - 0.64)], OBS, 6)
        wloft(mb, W, rect_ut(a0, a1, 0.0, 1.0, 0.14), rect_ut(a0 - 0.14, a1 + 0.14, 0.0, 1.14, 0.14), b + PT,
              b + PT + 0.32, SILVER)
        wprism(mb, W, rect_ut(a0 - 0.14, a1 + 0.14, 0.0, 1.14, 0.14), b + PT + 0.32, b + PT + 0.48, SILVER)
        c = P(um, 0.5, PT + 0.48)
        pinnacle(mb, c[0], c[1], c[2], s=0.42, hb=1.4, hn=3.2, body_m=OBS, spire_m=OBS, cap_m=SILVER, crock=False)
    # ---------------- ESPALDAR ogival, CAPITONE, timpano e moldura
    bw = MU0
    back = [(-bw, b + BT), (bw, b + BT), (bw, b + SPB)] + \
        [(s, b + h) for s, h in ogive2(0.0, bw, RB, SPB, 6)[::-1][1:-1]] + [(-bw, b + SPB)]
    panel(mb, W, back, 0.0, 0.62, OBS)
    mb.tube([P(s, 0.64, h) for s, h in ogive2(0.0, bw, RB, SPB, 6)], 0.05, SILVER, 4)

    def ogv(w_, h0_, h1, h2):
        return [(-w_, b + h0_), (w_, b + h0_), (w_, b + h1)] + \
            [(s, b + h) for s, h in ogive2(0.0, w_, h2 - h1, h1, 5)[::-1][1:-1]] + [(-w_, b + h1)]
    CW, CT = 2.15, 8.2
    band(mb, W, ogv(CW, SH + 0.05, SPB, SPB + 1.6), ogv(CW + 0.27, SH - 0.1, SPB, SPB + 1.95), 0.55, 0.98,
         SILVER, closed=True)
    tufted(-CW, CW, SH + 0.05, CT, 8, 8, 0.74, DC, 0.6, CLOTH)
    panel(mb, W, ogv(CW, CT, SPB, SPB + 1.6), 0.6, 0.8, CLOTH)
    mb.box2(P(-CW, 0.6, CT - 0.06), P(CW, 0.97, CT + 0.06), SILVER, 0.0)
    # ---------------- CRESCENTE de prata (sem espada)
    h0, RO, RI, DH_ = b + 10.3, 3.5, 3.2, 0.8
    yt = (RO * RO - RI * RI + DH_ * DH_) / (2.0 * DH_)
    xt = math.sqrt(RO * RO - yt * yt)
    a_tip = math.degrees(math.atan2(yt, xt))
    a_in0 = math.degrees(math.atan2(yt - DH_, xt))
    arc = lambda cy, r, a0, a1, n: [(r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
                                     cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
    lo = arc(h0, RO, a_tip, -180.0 - a_tip, 20)
    hi = arc(h0 + DH_, RI, a_in0, -180.0 - a_in0, 20)
    band(mb, W, hi, lo, 0.98, 1.22, SILVER)
    lo2 = arc(h0, RO - 0.09, a_tip - 2.0, -178.0 - a_tip, 20)
    hi2 = arc(h0 + DH_, RI + 0.09, a_in0 - 3.0, -177.0 - a_in0, 20)
    band(mb, W, hi2, lo2, 1.22, 1.3, SILVER)
    mb.tube([_P(W, u, 1.26, h) for u, h in lo], 0.045, SILVER, 4)


# ================================================================== ferro: LUSTRES
CHAND = [(-32.0, WIN_Y[1]), (32.0, WIN_Y[1]), (-32.0, WIN_Y[5]), (32.0, WIN_Y[5])]
CHAND_H = 36.0
CH_S = 2.1


def chandelier(mb, x, y, s=CH_S):
    """LUSTRE: aro em tubo, 8 BRACOS em S, cubo em balaustre de torno, pingente, velas de cera creme e haste presa sob a
    abobada por uma ROSETA de ferro"""
    h = Z + CHAND_H
    R = 3.1 * s
    n = 12
    mb.tube([(x + R * math.cos(2 * math.pi * k / n), y + R * math.sin(2 * math.pi * k / n), h) for k in range(n + 1)],
            0.13 * s, IRONL, 5)

    def arm(t):
        u = 1 - t
        rr = (u ** 3 * 0.4 + 3 * u * u * t * 1.5 + 3 * u * t * t * 2.4) * s + t ** 3 * R
        zz = u ** 3 * (h - 0.05 * s) + 3 * u * u * t * (h - 0.75 * s) + 3 * u * t * t * (h + 0.85 * s) + t ** 3 * (h + 0.16 * s)
        return rr, zz
    EM._lathe(mb, (x, y, h - 1.0 * s), [(r * s, q * s) for r, q in ((0.0, 0.0), (0.42, 0.55), (0.48, 0.95), (0.2, 1.55),
                                                                    (0.32, 1.86), (0.12, 2.1), (0.12, 2.5))], IRON, 6,
              caps=(False, True))
    EM._lathe(mb, (x, y, h - 2.1 * s), [(r * s, q * s) for r, q in ((0.0, 0.0), (0.2, 0.55), (0.16, 0.9), (0.24, 1.02),
                                                                    (0.0, 1.12))], SILVER, 6)
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        ca, sa = math.cos(a), math.sin(a)
        P = lambda rr, zz: (x + rr * ca, y + rr * sa, zz)
        mb.tube([P(*arm(i / 4.0)) for i in range(5)], 0.075 * s, IRON, 4)
        cx, cy, _ = P(R, h)
        candle(mb, cx, cy, h + 0.08 * s, 0.9 * s, 1.35 * s, dish=False, cup=True)
    top = Z + zv(x, y) - 0.9
    mb.rod((x, y, h + 1.45 * s), (x, y, top - 0.3), 0.12, IRON, 6)
    EM._lathe(mb, (x, y, top - 0.62), [(0.14, 0.0), (0.72, 0.4), (0.76, 0.56), (0.0, 0.66)], IRON, 8,
              caps=(True, False))


# ================================================================== luzes (6)
def lights():
    for (x, y), nm in zip(CHAND, ["SW", "SE", "NW", "NE"]):
        light("L_SGHall_Chandelier_%s" % nm, "POINT", (x, y, Z + CHAND_H - 0.4), 9000.0, (1.0, 0.68, 0.40), 1.2)
    light("L_SGHall_Rose", "POINT", (0.0, Y1 - 14.0, Z + ROSE_Z - 4.0), 3200.0, (0.66, 0.55, 1.0), 3.0)
    light("L_SGHall_Throne", "POINT", (0.0, TH_FRONT - 12.0, CZ + 9.0), 2600.0, (0.62, 0.40, 1.0), 2.5)


# ================================================================== build
def build():
    iw = MB("SG_Hall_Ironwork", "03_MINING_HALL", random.Random(351), detail="near")
    floor()
    wl = MB("SG_Hall_Walls", "03_MINING_HALL", random.Random(313), detail="near")
    arcade(wl)
    aisle_walls(wl, iw)
    end_walls(wl, iw)
    portal(wl)
    finish(wl)
    mw = MB("SG_Hall_Windows", "03_MINING_HALL", random.Random(321), detail="near")
    windows(mw)
    rose(mw, mw)
    finish(mw)
    vault()
    ribs()
    al = MB("SG_Hall_Altar", "03_MINING_HALL", random.Random(341), detail="hero")
    triumph(al)
    chancel(al, iw)
    finish(al)
    for x, y in CHAND:
        chandelier(iw, x, y)
    finish(iw)
    throne()
    lights()
